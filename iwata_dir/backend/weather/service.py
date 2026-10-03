"""Durable weather plans/jobs and immutable completed assets.

The acquisition worker is independent of the flight worker. Only explicit
inventory refresh and queued acquisitions can contact the provider. Polling,
planning, asset selection and result reopening perform no HTTP.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import threading
import uuid

from balloon_sim.environment.gfs import acquire_gfs, _url
from balloon_sim.environment.storage import read_json
from balloon_sim.environment.bundle import WeatherField
from balloon_sim.environment.fields import geopotential_to_geometric

from ..errors import ServiceError
from ..storage import canonical, digest, file_hash, utc_now, write_new_json
from ..worker import source_snapshot
from .catalog import observe_inventory
from .contracts import AcquisitionRequest, InventoryRefresh, WeatherPlanRequest
from .planning import decoder_identity, dependencies, make_plan, launch_support

ACTIVE = {"queued", "running", "cancelling"}
RETRYABLE = {"failed", "cancelled", "interrupted"}


class WeatherService:
    def __init__(self, data_dir, *, on_source=None, gateway=None, acquirer=None,
                 dependency_check=None, max_queued=4, source_guard=None):
        self.root = Path(data_dir) / "weather"
        self.on_source = on_source or (lambda source: None)
        self.gateway = gateway
        self.acquire = acquirer or acquire_gfs
        self._raw_reuse_enabled = acquirer is None  # Preserve injected acquirer signatures.
        self.dependencies = dependency_check or dependencies
        self.max_queued = max_queued
        self.source_guard = source_guard
        self._startup_source = None
        self._guard = threading.RLock()
        self._refresh_guard = threading.Lock()
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._cancels = {}
        self._thread = None
        self.db = None

    def start(self):
        if self.source_guard is None:
            self._startup_source = source_snapshot()
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "acquisitions").mkdir(exist_ok=True)
        (self.root / "inventories").mkdir(exist_ok=True)
        self.db = sqlite3.connect(self.root / "registry.sqlite3", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
              kind TEXT NOT NULL,id TEXT NOT NULL,created_at TEXT NOT NULL,body TEXT NOT NULL,
              PRIMARY KEY(kind,id));
            CREATE TABLE IF NOT EXISTS acquisitions (
              id TEXT PRIMARY KEY,client_request_id TEXT UNIQUE NOT NULL,
              request_hash TEXT NOT NULL,cache_key TEXT NOT NULL,body TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS requests (
              client_request_id TEXT PRIMARY KEY,request_hash TEXT NOT NULL,
              acquisition_id TEXT NOT NULL);
        """)
        for row in self.db.execute("SELECT body FROM acquisitions").fetchall():
            job = json.loads(row["body"])
            if job["state"] in ACTIVE:
                job.update(state="interrupted", finished_at=utc_now(),
                           error={"code": "RESTART_INTERRUPTED", "message": "Acquisition was interrupted; explicit retry is required."})
                self._save_job(job)
        self.db.commit()
        self._stop.clear()
        self._thread = threading.Thread(target=self._dispatch, name="balloon-weather-acquisition", daemon=True)
        self._thread.start()
        return self

    def close(self):
        self._stop.set()
        self._wake.set()
        with self._guard:
            for cancel in self._cancels.values():
                cancel.set()
        if self._thread:
            self._thread.join()
        with self._guard:
            if self.db:
                self.db.close()
                self.db = None

    def status(self):
        return {"dependencies": self.dependencies(), "workers": 1, "max_queued": self.max_queued}

    def _ensure_source_current(self):
        if self.source_guard is not None:
            self.source_guard()
            return
        try:
            current = source_snapshot()
        except Exception as exc:
            raise ServiceError(409, "SOURCE_CHANGED", "Application source or environment cannot be verified; restart before new work.") from exc
        if self._startup_source is None or current != self._startup_source:
            raise ServiceError(409, "SOURCE_CHANGED", "Application source or environment changed after startup; restart before new work.")

    def _insert(self, kind, identity, document):
        self.db.execute("INSERT INTO documents VALUES (?,?,?,?)",
                        (kind, identity, utc_now(), canonical(document)))

    def _get(self, kind, identity):
        row = self.db.execute("SELECT body FROM documents WHERE kind=? AND id=?", (kind, identity)).fetchone()
        if not row:
            raise ServiceError(404, kind.upper()+"_NOT_FOUND", "Saved weather "+kind+" does not exist.")
        return json.loads(row["body"])

    def _list(self, kind):
        return [json.loads(row["body"]) for row in self.db.execute(
            "SELECT body FROM documents WHERE kind=? ORDER BY created_at DESC,id DESC", (kind,))]

    def refresh_inventory(self, request):
        request = InventoryRefresh.model_validate(request).model_dump()
        self._ensure_source_current()
        # Reject a second simultaneous refresh rather than accumulating unbounded
        # gateway waiters. Acquisitions share the provider's process-safe gateway.
        if not self._refresh_guard.acquire(blocking=False):
            raise ServiceError(409, "INVENTORY_REFRESH_ACTIVE", "An inventory observation is already in progress.")
        identity = str(uuid.uuid4())
        folder = self.root / "inventories" / identity
        saved_observations = []
        try:
            folder.mkdir()
            if self.gateway is None:
                from balloon_sim.environment.nomads import NomadsGateway
                self.gateway = NomadsGateway()
            def record(url, data, metadata):
                sha = hashlib.sha256(data).hexdigest()
                if metadata.get("sha256") != sha or metadata.get("bytes") != len(data) or metadata.get("url") != url:
                    raise ValueError("inventory response differs from gateway metadata")
                name = f"{len(saved_observations):03d}.html"
                with (folder / name).open("xb") as stream:
                    stream.write(data)
                entry = {**metadata, "file": name}
                saved_observations.append(entry)
                write_new_json(folder / (name+".json"), entry)
                self._ensure_source_current()
                return entry
            result = observe_inventory(request, self.gateway, self._stop, recorder=record)
            self._ensure_source_current()
            result.update(inventory_id=identity, observed_at_utc=utc_now(),
                          raw_directory="weather/inventories/"+identity)
            write_new_json(folder / "inventory.json", result)
            result["manifest_sha256"] = file_hash(folder / "inventory.json")
            with self._guard, self.db:
                self._insert("inventory", result["inventory_id"], result)
            return result
        except Exception as exc:
            try:
                write_new_json(folder / "failure.json", {"inventory_id": identity, "request": request,
                    "failed_at_utc": utc_now(), "observations": saved_observations,
                    "error": {"code": getattr(exc, "code", "INVENTORY_FAILED"), "message": str(exc)}})
            except OSError:
                pass  # A full/unavailable disk must not leak the refresh lock.
            if isinstance(exc, ServiceError):
                raise
            raise ServiceError(502, getattr(exc, "code", "INVENTORY_FAILED"), str(exc)) from exc
        finally:
            self._refresh_guard.release()

    def list_inventories(self):
        with self._guard:
            return {"inventories": self._list("inventory")}

    def get_inventory(self, identity):
        with self._guard:
            inventory = self._get("inventory", identity)
            self._verify_inventory(inventory)
            return inventory

    def _verify_inventory(self, inventory):
        identity = inventory["inventory_id"]
        if str(uuid.UUID(identity)) != identity:
            raise ServiceError(409, "INVENTORY_INTEGRITY_ERROR", "Invalid saved inventory identity.")
        folder = self.root / "inventories" / identity
        try:
            if file_hash(folder / "inventory.json") != inventory["manifest_sha256"]:
                raise ValueError("saved inventory manifest changed")
            original = read_json(folder / "inventory.json")
            if original != {k: v for k, v in inventory.items() if k != "manifest_sha256"}:
                raise ValueError("saved inventory registry differs from its manifest")
            for item in inventory["observations"]:
                if Path(item["file"]).name != item["file"] or "/" in item["file"] or "\\" in item["file"]:
                    raise ValueError("invalid observation filename")
                path = folder / item["file"]
                if path.is_symlink() or path.stat().st_size != item["bytes"] or file_hash(path) != item["sha256"]:
                    raise ValueError("saved inventory response changed")
        except (ValueError, OSError, KeyError) as exc:
            raise ServiceError(409, "INVENTORY_INTEGRITY_ERROR", "Saved inventory failed raw-response verification.") from exc

    def plan(self, request):
        request = WeatherPlanRequest.model_validate(request).model_dump()
        self._ensure_source_current()
        with self._guard:
            inventory = self._get("inventory", request["inventory_id"])
            self._verify_inventory(inventory)
        try:
            result = make_plan(request, inventory, self.dependencies())
        except (ValueError, ImportError, OverflowError) as exc:
            raise ServiceError(422, getattr(exc, "code", "INVALID_WEATHER_PLAN"), str(exc)) from exc
        result.update(plan_id=str(uuid.uuid4()), created_at=utc_now())
        self._ensure_source_current()
        with self._guard, self.db:
            self._insert("plan", result["plan_id"], result)
        return result

    def get_plan(self, identity):
        with self._guard:
            return self._get("plan", identity)

    def _job(self, identity):
        row = self.db.execute("SELECT body FROM acquisitions WHERE id=?", (identity,)).fetchone()
        if not row:
            raise ServiceError(404, "ACQUISITION_NOT_FOUND", "Weather acquisition does not exist.")
        return json.loads(row["body"])

    @staticmethod
    def _public(job):
        return {**job, "cancellable": job["state"] in {"queued", "running"},
                "retryable": job["state"] in RETRYABLE}

    @staticmethod
    def _reuse_progress(asset, plan):
        count = len(plan["normalized_request"]["lead_hours"])
        raw = asset["snapshot"]["metadata"].get("provenance", [])
        return {"phase": "reused", "completed_files": count, "total_files": count,
                "bytes_downloaded": 0, "bytes_reused": sum(item.get("bytes", 0) for item in raw),
                "bundle_bytes_reused": asset["snapshot"]["bytes"]}

    def _save_job(self, job):
        self.db.execute("UPDATE acquisitions SET body=? WHERE id=?", (canonical(job), job["acquisition_id"]))

    def list_jobs(self):
        with self._guard:
            return {"acquisitions": [self._public(j) for j in self._jobs()]}

    def _jobs(self):
        jobs = [json.loads(r["body"]) for r in self.db.execute("SELECT body FROM acquisitions")]
        return sorted(jobs, key=lambda j: (j["created_at"], j["acquisition_id"]), reverse=True)

    def get_job(self, identity):
        with self._guard:
            return self._public(self._job(identity))

    def _check_plan(self, plan):
        self._ensure_source_current()
        if plan["status"] != "ready":
            raise ServiceError(409, "PLAN_NOT_READY", "This saved plan is not admissible for acquisition; inspect its issues.")
        try:
            request = WeatherPlanRequest.model_validate(plan["request"]).model_dump()
            support = launch_support(request, plan["normalized_request"]["bounds"])
            if support != plan.get("launch_support") or not all(p["inside"] for p in support):
                raise ValueError("Launch inclusion evidence is missing or differs.")
        except (ValueError, KeyError, TypeError) as exc:
            raise ServiceError(409, "PLAN_REPLAN_REQUIRED", "This saved plan lacks matching launch-location support. Make a new plan; the original plan, accepted request and saved assets remain readable.") from exc
        deps = self.dependencies()
        if not deps["available"]:
            raise ServiceError(409, "DEPENDENCIES_UNAVAILABLE", "Decoder dependencies are unavailable.")
        if decoder_identity(deps) != plan["decoder_identity"]:
            raise ServiceError(409, "DECODER_CHANGED", "Decoder source or environment changed; make a new plan.")

    def _verify_asset(self, asset):
        identity = asset["acquisition_id"]
        if str(uuid.UUID(identity)) != identity:
            raise ValueError("invalid acquisition identity")
        folder = self.root / "acquisitions" / identity
        marker = folder / "ASSET.json"
        if file_hash(marker) != asset["marker_sha256"]:
            raise ValueError("weather completion marker changed")
        saved = read_json(marker)
        if saved["snapshot"] != asset["snapshot"] or saved["cache_key"] != asset["cache_key"]:
            raise ValueError("weather identity changed")
        path = folder / "weather.json.gz"
        if path.is_symlink() or file_hash(path) != asset["snapshot"]["sha256"]:
            raise ValueError("weather bundle changed")
        return {"path": path, "snapshot": asset["snapshot"], "default_config": None}

    def _raw_donors(self, spec, leads):
        """Snapshot registered completed assets only; no cache/HTTP side effect."""
        with self._guard:
            assets=copy.deepcopy(self._list("asset"))
        for asset in sorted(assets,key=lambda item:item["acquisition_id"]):
            metadata=asset["snapshot"].get("metadata",{})
            saved_spec=metadata.get("request",{})
            if saved_spec.get("run_utc")!=spec["run_utc"] or saved_spec.get("bounds")!=spec["bounds"]:
                continue
            wanted=set(leads).intersection(saved_spec.get("lead_hours",[]))
            if not wanted: continue
            # Different selectors are a cache miss, not a license to substitute.
            provenance=metadata.get("provenance",[])
            selected=[(lead,item) for lead in sorted(wanted) for item in provenance
                      if item.get("file")==f"f{lead:03d}.grib2" and item.get("url")==_url(spec,lead)]
            if not selected: continue
            folder=self.root/"acquisitions"/asset["acquisition_id"]
            try:
                if (folder.is_symlink() or (self.root/"acquisitions").is_symlink()
                        or not folder.resolve().is_relative_to(self.root.resolve())
                        or (folder/"ASSET.json").is_symlink()):
                    raise ValueError("saved raw directory/marker is not local")
                self._verify_asset(asset)
            except (ValueError,OSError,KeyError) as exc:
                raise ServiceError(409,"ASSET_INTEGRITY_ERROR","Raw donor asset failed verification; no HTTP fallback.") from exc
            for lead,item in selected:
                yield {"lead_hours":lead,"path":folder/item["file"],"provenance":copy.deepcopy(item),
                       "donor":{"asset_id":asset["snapshot"]["id"],"acquisition_id":asset["acquisition_id"],
                                "bundle_sha256":asset["snapshot"]["sha256"],"marker_sha256":asset["marker_sha256"]}}

    def source_records(self):
        sources, errors = [], []
        with self._guard:
            for asset in self._list("asset"):
                try:
                    sources.append(self._verify_asset(asset))
                except (ValueError, OSError, KeyError) as exc:
                    errors.append({"id": asset.get("snapshot", {}).get("id"), "code": "SOURCE_UNAVAILABLE", "message": str(exc)})
        return sources, errors

    def submit(self, request):
        request = AcquisitionRequest.model_validate(request).model_dump()
        request_hash = digest(request)
        with self._guard:
            old = self.db.execute("SELECT request_hash,acquisition_id FROM requests WHERE client_request_id=?", (request["client_request_id"],)).fetchone()
            if old:
                if old["request_hash"] != request_hash:
                    raise ServiceError(409, "REQUEST_ID_CONFLICT", "This request ID refers to another acquisition plan.")
                return self._public(self._job(old["acquisition_id"]))
            plan = self._get("plan", request["plan_id"])
            self._check_plan(plan)
            for job in self._jobs():
                if job["cache_key"] == plan["cache_key"] and job["state"] in ACTIVE:
                    with self.db:
                        self.db.execute("INSERT INTO requests VALUES (?,?,?)", (request["client_request_id"], request_hash, job["acquisition_id"]))
                    return self._public(job)
            asset = next((a for a in self._list("asset") if a["cache_key"] == plan["cache_key"]), None)
            if asset:
                try:
                    self._verify_asset(asset)
                except (ValueError, OSError, KeyError) as exc:
                    raise ServiceError(409, "ASSET_INTEGRITY_ERROR", "Matching saved weather failed verification; it was not reused.") from exc
            if not asset and sum(j["state"] == "queued" for j in self._jobs()) >= self.max_queued:
                raise ServiceError(429, "WEATHER_QUEUE_FULL", "Weather waiting queue is full.")
            identity, now = str(uuid.uuid4()), utc_now()
            job = {"acquisition_id": identity, "plan_id": plan["plan_id"], "cache_key": plan["cache_key"],
                   "state": "completed" if asset else "queued", "attempt": 1, "created_at": now,
                   "started_at": None, "finished_at": now if asset else None,
                   "progress": {"phase": "reused" if asset else "queued", "completed_files": 0,
                                "total_files": len(plan["normalized_request"]["lead_hours"]),
                                "bytes_downloaded": 0, "bytes_reused": asset["snapshot"]["bytes"] if asset else 0},
                   "weather_source_id": asset["snapshot"]["id"] if asset else None,
                   "reused": bool(asset), "error": None}
            if asset:
                job["progress"] = self._reuse_progress(asset, plan)
            with self.db:
                self.db.execute("INSERT INTO acquisitions VALUES (?,?,?,?,?)",
                                (identity, request["client_request_id"], request_hash, plan["cache_key"], canonical(job)))
                self.db.execute("INSERT INTO requests VALUES (?,?,?)", (request["client_request_id"], request_hash, identity))
            self._wake.set()
            return self._public(job)

    def cancel(self, identity):
        with self._guard, self.db:
            job = self._job(identity)
            if job["state"] == "queued":
                job.update(state="cancelled", finished_at=utc_now())
            elif job["state"] in {"running", "cancelling"}:
                job["state"] = "cancelling"
                self._cancels[identity].set()
            else:
                raise ServiceError(409, "NOT_CANCELLABLE", "This acquisition is not waiting or running.")
            self._save_job(job)
            return self._public(job)

    def retry(self, identity):
        with self._guard, self.db:
            job = self._job(identity)
            if job["state"] not in RETRYABLE:
                raise ServiceError(409, "NOT_RETRYABLE", "Only failed, cancelled or interrupted acquisitions can be retried.")
            plan = self._get("plan", job["plan_id"])
            self._check_plan(plan)
            jobs = self._jobs()
            active = next((j for j in jobs if j["cache_key"] == job["cache_key"] and j["state"] in ACTIVE), None)
            if active:
                raise ServiceError(409, "MATCHING_ACQUISITION_ACTIVE", "The same request is already being acquired: "+active["acquisition_id"])
            asset = next((a for a in self._list("asset") if a["cache_key"] == job["cache_key"]), None)
            if asset:
                try:
                    self._verify_asset(asset)
                except (ValueError, OSError, KeyError) as exc:
                    raise ServiceError(409, "ASSET_INTEGRITY_ERROR", "Matching weather failed verification; retry did not overwrite it.") from exc
            if not asset and sum(j["state"] == "queued" for j in jobs) >= self.max_queued:
                raise ServiceError(429, "WEATHER_QUEUE_FULL", "Weather waiting queue is full.")
            # Retain each attempt's status/progress/error as durable history.
            history = job.setdefault("previous_attempts", [])
            history.append({k: copy.deepcopy(job[k]) for k in ("attempt", "state", "started_at", "finished_at", "progress", "error")})
            job.update(state="completed" if asset else "queued", attempt=job["attempt"]+1,
                       started_at=None, finished_at=utc_now() if asset else None, error=None, reused=bool(asset),
                       weather_source_id=asset["snapshot"]["id"] if asset else None)
            job["progress"] = self._reuse_progress(asset, plan) if asset else {**job["progress"], "phase": "queued"}
            self._save_job(job)
            self._wake.set()
            return self._public(job)

    def _publish(self, job, plan, target):
        target = Path(target)
        folder = self.root / "acquisitions" / job["acquisition_id"]
        if target.resolve() != (folder / "weather.json.gz").resolve() or target.is_symlink():
            raise ValueError("acquirer returned an unexpected path")
        receipt = read_json(folder / "receipt.json")
        sha = file_hash(target)
        if receipt["bundle"] != target.name or receipt["bundle_sha256"] != sha:
            raise ValueError("acquisition receipt does not match weather bundle")
        bundle = read_json(target)
        field = WeatherField(bundle)  # Only completely validated fields enter the catalog.
        spec = plan["normalized_request"]
        if bundle["metadata"].get("request") != spec:
            raise ValueError("acquired field differs from the fixed request")
        axes, metadata = bundle["axes"], bundle["metadata"]
        minimum_top = min(v for time in field.fields["geopotential_height_gpm"] for row in time[-1] for v in row)
        snapshot = {"id": "gfs-"+digest({"sha256": sha, "decoder": plan["decoder_identity"]}),
                    "kind": "acquired_gfs", "label": "GFS "+spec["run_utc"],
                    "sha256": sha, "bytes": target.stat().st_size, "run_utc": spec["run_utc"],
                    "valid_times_utc": axes["time_utc"],
                    "bounds": {"lat": [field.latitudes[0], field.latitudes[-1]],
                               "lon": [field.longitudes[0], field.longitudes[-1]],
                               "pressure_pa": [min(field.pressures), max(field.pressures)]},
                    "metadata": metadata, "plan_id": plan["plan_id"],
                    "support": {"minimum_top_geometric_m": geopotential_to_geometric(minimum_top),
                                "ground_model": "coarse_gfs_orography", "full_flight_guaranteed": False},
                    "acquisition_id": job["acquisition_id"], "registered_at_utc": utc_now()}
        marker = {"schema": "balloon.weather-asset/1", "snapshot": snapshot, "cache_key": plan["cache_key"]}
        marker_path = folder / "ASSET.json"
        if marker_path.exists():
            # Crash after marker but before DB: recover its original timestamp/identity.
            previous = read_json(marker_path)
            if (previous["snapshot"]["sha256"] != sha or previous["cache_key"] != plan["cache_key"]
                    or previous["snapshot"]["acquisition_id"] != job["acquisition_id"]):
                raise ValueError("existing completion marker differs")
            marker, snapshot = previous, previous["snapshot"]
        else:
            # A crash may leave an unregistered partial marker, never a truncated
            # final marker that makes verified raw/bundle recovery impossible.
            partial = folder / ("ASSET."+str(uuid.uuid4())+".partial")
            write_new_json(partial, marker)
            partial.rename(marker_path)
        asset = {"acquisition_id": job["acquisition_id"], "cache_key": plan["cache_key"],
                 "snapshot": snapshot, "marker_sha256": file_hash(marker_path)}
        return asset, self._verify_asset(asset)

    def _dispatch(self):
        while not self._stop.is_set():
            with self._guard, self.db:
                waiting = [j for j in reversed(self._jobs()) if j["state"] == "queued"]
                job = waiting[0] if waiting else None
                if job:
                    identity = job["acquisition_id"]
                    cancel = self._cancels[identity] = threading.Event()
                    job.update(state="running", started_at=utc_now())
                    self._save_job(job)
            if not job:
                self._wake.wait(0.25)
                self._wake.clear()
                continue
            try:
                with self._guard:
                    plan = self._get("plan", job["plan_id"])
                self._check_plan(plan)
                folder = self.root / "acquisitions" / identity
                def progress(update):
                    with self._guard, self.db:
                        current = self._job(identity)
                        current["progress"].update(update)
                        self._save_job(current)
                    self._ensure_source_current()
                request = {k: v for k, v in plan["normalized_request"].items() if k != "lead_hours"}
                reuse_options = {"raw_provider": self._raw_donors} if self._raw_reuse_enabled else {}
                target = self.acquire(request, folder, resume=folder.exists(), progress=progress, cancel=cancel,
                                      **reuse_options)
                self._check_plan(plan)
                with self._guard, self.db:
                    current = self._job(identity)
                    if cancel.is_set() or self._stop.is_set():
                        raise ServiceError(409, "ACQUISITION_CANCELLED", "Acquisition cancelled before publication.")
                    asset, source = self._publish(current, plan, target)
                    self._ensure_source_current()
                    self._insert("asset", asset["snapshot"]["id"], asset)
                    current.update(state="completed", finished_at=utc_now(), weather_source_id=asset["snapshot"]["id"])
                    current["progress"]["phase"] = "completed"
                    self._save_job(current)
                self.on_source(source)
            except Exception as exc:
                with self._guard, self.db:
                    current = self._job(identity)
                    if current["state"] != "completed":
                        code = getattr(exc, "code", "ACQUISITION_FAILED")
                        state = "interrupted" if self._stop.is_set() else ("cancelled" if cancel.is_set() or code == "ACQUISITION_CANCELLED" else "failed")
                        current.update(state=state, finished_at=utc_now(), error={"code": code, "message": str(exc)})
                        self._save_job(current)
            finally:
                with self._guard:
                    self._cancels.pop(identity, None)
