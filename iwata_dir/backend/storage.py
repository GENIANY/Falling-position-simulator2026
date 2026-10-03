"""Small persistent registry and an explicit completed-artifact barrier."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_new_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(canonical(value) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def registry_instance_id(db):
    """Read a stable opaque identity; malformed existing state is never rekeyed."""
    rows = db.execute("SELECT singleton,instance_id FROM service_identity").fetchall()
    if len(rows) != 1 or rows[0]["singleton"] != 1:
        raise ValueError("Registry instance identity is missing or ambiguous; preserve the state and inspect it.")
    value = rows[0]["instance_id"]
    try:
        parsed = uuid.UUID(value) if isinstance(value, str) else None
    except ValueError:
        parsed = None
    if parsed is None or parsed.version != 4 or str(parsed) != value:
        raise ValueError("Registry instance identity is invalid; preserve the state and inspect it.")
    return value


def open_registry(data_dir):
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in ("specs", "staging", "results"):
        (data_dir / name).mkdir(exist_ok=True)
    db = sqlite3.connect(data_dir / "registry.sqlite3", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY, revision INTEGER NOT NULL, document TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY, client_request_id TEXT NOT NULL UNIQUE,
            request_hash TEXT NOT NULL, spec TEXT NOT NULL, created_at TEXT NOT NULL,
            result_path TEXT, manifest_hash TEXT);
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, run_id TEXT NOT NULL UNIQUE REFERENCES runs(id),
            state TEXT NOT NULL, started_at TEXT, finished_at TEXT, error TEXT);
        CREATE TABLE IF NOT EXISTS run_recoveries (
            id INTEGER PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
            document TEXT NOT NULL);
    """)
    try:
        # An old schema has no identity table. Migrate once in one transaction;
        # an existing but empty/corrupt table is not a reason to invent a new ID.
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='service_identity'").fetchone():
            with db:
                db.execute("BEGIN IMMEDIATE")
                db.execute("CREATE TABLE service_identity (singleton INTEGER PRIMARY KEY CHECK(singleton=1), instance_id TEXT NOT NULL)")
                db.execute("INSERT INTO service_identity VALUES (1,?)", (str(uuid.uuid4()),))
        registry_instance_id(db)
    except BaseException:
        db.close()
        raise
    project = {"schema": "balloon.project/1", "title": "保存気象で条件を比較", "candidates": [], "compare_run_ids": []}
    db.execute("INSERT OR IGNORE INTO projects VALUES ('default',0,?)", (canonical(project),))
    db.commit()
    return db


def verify_files(folder, files):
    """Validate exact names, sizes and hashes; never follow a manifest path."""
    folder = Path(folder)
    for name, expected in files.items():
        if not name or Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("invalid artifact filename")
        path = folder / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("missing artifact: " + name)
        if path.stat().st_size != expected["bytes"] or file_hash(path) != expected["sha256"]:
            raise ValueError("artifact integrity failure: " + name)


def publish_result(data_dir, run_id, spec):
    """Verify worker output, add the run identity, then expose one complete folder."""
    stage = Path(data_dir) / "staging" / run_id
    original = json.loads((stage / "manifest.json").read_text(encoding="utf-8"))
    expected_names = {"input.json", "result.json", "provenance.json", "trajectory.geojson", "trajectory.csv", "report.html"}
    if original.get("schema") != "balloon.flight.output_manifest/1" or set(original["files"]) != expected_names:
        raise ValueError("unexpected kernel manifest")
    verify_files(stage, original["files"])
    if {p.name for p in stage.iterdir()} != expected_names | {"manifest.json"}:
        raise ValueError("unexpected staging files")
    result = json.loads((stage / "result.json").read_text(encoding="utf-8"))
    if result.get("schema") != "balloon.flight.result/1" or result["config"] != spec["config"]:
        raise ValueError("result does not match fixed input")
    if result["status"] not in ("landed", "stopped"):
        raise ValueError("unknown physical result status")
    write_new_json(stage / "run.json", spec)
    files = {p.name: {"bytes": p.stat().st_size, "sha256": file_hash(p)} for p in sorted(stage.iterdir())}
    marker = {"schema": "balloon.committed-result/1", "run_id": run_id, "files": files}
    write_new_json(stage / "COMMITTED.json", marker)
    verify_files(stage, files)
    final = Path(data_dir) / "results" / run_id
    if final.exists():
        raise FileExistsError("result already exists")
    stage.rename(final)
    return "results/" + run_id, file_hash(final / "COMMITTED.json")


def read_result(data_dir, relative_path, manifest_hash, run_id):
    if relative_path != "results/" + run_id:
        raise ValueError("invalid result reference")
    folder = Path(data_dir) / relative_path
    marker = folder / "COMMITTED.json"
    if file_hash(marker) != manifest_hash:
        raise ValueError("completion marker integrity failure")
    manifest = json.loads(marker.read_text(encoding="utf-8"))
    if manifest.get("schema") != "balloon.committed-result/1" or manifest.get("run_id") != run_id:
        raise ValueError("completion identity mismatch")
    verify_files(folder, manifest["files"])
    return json.loads((folder / "result.json").read_text(encoding="utf-8"))


def recover_result(data_dir, run_id, spec):
    """Recover only a fully renamed result after registry publication was interrupted.

    Source identity is compared to the original fixed spec, never today's code.
    New computation/retry has a separate current-source guard.
    """
    folder = Path(data_dir) / "results" / run_id
    if not folder.exists():
        return None
    if folder.is_symlink() or folder.is_junction():
        raise ValueError("linked committed result")
    marker_hash = file_hash(folder / "COMMITTED.json")
    marker = json.loads((folder / "COMMITTED.json").read_text(encoding="utf-8"))
    kernel_names = {"input.json", "result.json", "provenance.json", "trajectory.geojson", "trajectory.csv", "report.html"}
    if (not isinstance(marker, dict) or not isinstance(marker.get("files"), dict)
            or set(marker["files"]) != kernel_names | {"manifest.json", "run.json"}):
        raise ValueError("incomplete committed recovery manifest")
    result = read_result(data_dir, "results/" + run_id, marker_hash, run_id)
    original = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if (not isinstance(original, dict) or original.get("schema") != "balloon.flight.output_manifest/1"
            or not isinstance(original.get("files"), dict) or set(original["files"]) != kernel_names
            or any(original["files"][name] != marker["files"][name] for name in kernel_names)):
        raise ValueError("kernel and committed recovery manifests differ")
    if (json.loads((folder / "run.json").read_text(encoding="utf-8")) != spec
            or not isinstance(result, dict) or result.get("schema") != "balloon.flight.result/1"
            or result.get("status") not in {"landed", "stopped"}
            or result["config"] != spec["config"]
            or file_hash(folder / "input.json") != spec["config_file_sha256"]):
        raise ValueError("completed result differs from fixed run identity")
    return "results/" + run_id, marker_hash, result["status"]
