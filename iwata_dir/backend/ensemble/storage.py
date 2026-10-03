"""Ensemble registry and immutable JSON publication; no calculation or scheduling."""
import json
import uuid
from pathlib import Path
from backend.storage import file_hash, write_new_json


def create_tables(db):
    db.executescript("""
      CREATE TABLE IF NOT EXISTS ensemble_plans (
        id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, request_hash TEXT NOT NULL,
        document_hash TEXT NOT NULL, created_at TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS ensembles (
        id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, request_hash TEXT NOT NULL,
        plan_id TEXT NOT NULL, state TEXT NOT NULL, epoch INTEGER NOT NULL,
        revision INTEGER NOT NULL, created_at TEXT NOT NULL, last_dispatch TEXT,
        snapshot_id TEXT, error TEXT);
      CREATE TABLE IF NOT EXISTS ensemble_trials (
        id TEXT PRIMARY KEY, ensemble_id TEXT NOT NULL, ordinal INTEGER NOT NULL,
        case_id TEXT NOT NULL, draw_id TEXT NOT NULL, state TEXT NOT NULL,
        attempt INTEGER NOT NULL, run_id TEXT, error TEXT);
      CREATE TABLE IF NOT EXISTS ensemble_attempts (
        trial_id TEXT NOT NULL, attempt INTEGER NOT NULL, epoch INTEGER NOT NULL,
        run_id TEXT UNIQUE NOT NULL, state TEXT NOT NULL,
        PRIMARY KEY(trial_id,attempt));
      CREATE TABLE IF NOT EXISTS ensemble_snapshots (
        id TEXT PRIMARY KEY, ensemble_id TEXT NOT NULL, epoch INTEGER NOT NULL,
        document_hash TEXT NOT NULL, created_at TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS ensemble_commands (
        request_id TEXT PRIMARY KEY, request_hash TEXT NOT NULL, response TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS ensemble_analyses (
        id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, request_hash TEXT NOT NULL,
        snapshot_id TEXT NOT NULL, case_id TEXT NOT NULL,
        document_hash TEXT NOT NULL, created_at TEXT NOT NULL);
    """)
    db.commit()


def _folder(root, identity):
    if str(uuid.UUID(identity)) != identity:
        raise ValueError("invalid ensemble artifact identity")
    return Path(root) / "ensemble-artifacts" / identity


def publish(root, identity, document):
    """A partial JSON is never readable by its final identity."""
    final = _folder(root, identity)
    final.parent.mkdir(exist_ok=True)
    stage = final.parent / (identity + ".partial-" + str(uuid.uuid4()))
    stage.mkdir()
    write_new_json(stage / "document.json", document)
    expected = file_hash(stage / "document.json")
    write_new_json(stage / "COMMITTED.json", {"id": identity, "sha256": expected})
    if final.exists():
        raise FileExistsError("ensemble artifact already exists")
    stage.rename(final)
    return expected


def read(root, identity, expected):
    folder = _folder(root, identity)
    if folder.is_symlink() or folder.is_junction():
        raise ValueError("linked ensemble artifact")
    for name in ("document.json", "COMMITTED.json"):
        if (folder / name).is_symlink() or not (folder / name).is_file():
            raise ValueError("missing ensemble artifact")
    marker = json.loads((folder / "COMMITTED.json").read_text(encoding="utf-8"))
    if marker != {"id": identity, "sha256": expected} or file_hash(folder / "document.json") != expected:
        raise ValueError("ensemble artifact integrity failure")
    return json.loads((folder / "document.json").read_text(encoding="utf-8"))
