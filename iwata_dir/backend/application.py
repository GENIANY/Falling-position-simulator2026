"""HTTP-independent application service: drafts, immutable runs and one worker."""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
import copy
import json
import multiprocessing
import os
from pathlib import Path
import threading
import uuid
import zlib

from balloon_sim.environment.storage import load_weather, read_json
from balloon_sim.environment.jra3q import SURFACE_SCHEMA as JRA_SURFACE_SCHEMA
from balloon_sim.flight.config import FlightError, validate_config
from balloon_sim.environment.fields import WeatherError, _utc
from datetime import timedelta

from .contracts import ProjectUpdate, RunRequest
from .errors import ServiceError
from .storage import canonical, digest, file_hash, open_registry, publish_result, read_result, recover_result, registry_instance_id, utc_now, write_new_json
from .worker import REPO_ROOT, execute_run, source_snapshot
from .weather.service import WeatherService
from .weather.contracts import GroundQuery
from .ensemble.service import EnsembleService
from .climate.service import ClimateService
from .historical_catalog import load_historical_sources


def default_data_dir():
    configured = os.environ.get("BALLOON_DATA_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share")))
    return base / "BalloonSimulator" / "state"


class ApplicationService:
    """Own one local state directory. Call start/close or use the context manager.

    At most one running flight and max_queued waiting flights. A separate server
    instance must use a different state directory; the process lock enforces it.
    """

    def __init__(self, data_dir=None, *, max_queued=4, weather_options=None, climate_options=None):
        self.data_dir = Path(data_dir or default_data_dir()).resolve()
        if not isinstance(max_queued, int) or max_queued < 1:
            raise ValueError("max_queued must be a positive integer")
        self.max_queued = max_queued
        self._guard = threading.RLock()
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._executor = None
        self._thread = None
        self._db = None
        self._lock_file = None
        self._sources = {}
        self._source_errors = []
        self._snapshot = None
        self._execution_error = None
        self.instance_id = None
        self.weather = WeatherService(self.data_dir, on_source=self._register_weather_source,
                                      source_guard=self._assert_source_current,
                                      **(weather_options or {}))
        self.ensemble = EnsembleService(self)
        self.climate = None
        self._climate_options = ({
            "source_path": os.environ.get("BALLOON_CLIMATE_DB") or None,
            "expected_sha256": os.environ.get("BALLOON_CLIMATE_SHA256") or None,
            "samples_path": os.environ.get("BALLOON_CLIMATE_SAMPLES") or None,
            "archive_paths": json.loads(os.environ.get("BALLOON_CLIMATE_ARCHIVES") or "[]"),
        } if climate_options is None else dict(climate_options))

    def _acquire_directory(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._lock_file = (self.data_dir / "service.lock").open("a+b")
        self._lock_file.seek(0)
        if os.name == "nt":
            import msvcrt
            if os.fstat(self._lock_file.fileno()).st_size == 0:
                self._lock_file.write(b"0")
                self._lock_file.flush()
            self._lock_file.seek(0)
            try:
                msvcrt.locking(self._lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                self._lock_file.close()
                self._lock_file = None
                raise RuntimeError("state directory is already in use") from None
        else:
            import fcntl
            try:
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                self._lock_file.close()
                self._lock_file = None
                raise RuntimeError("state directory is already in use") from None

    def start(self):
        with self._guard:
            if self._db is not None:
                return self
            self._acquire_directory()
            try:
                self._db = open_registry(self.data_dir)
                self.instance_id = registry_instance_id(self._db)
                # A complete renamed artifact may precede its registry update.
                # Inspect it against its original spec before interrupting work;
                # this never reloads today's weather or reruns the calculation.
                self._recover_registered_results()
                self._db.execute("UPDATE jobs SET state='interrupted',finished_at=?,error=? WHERE state IN ('queued','running')",
                                 (utc_now(), canonical({"code": "RESTART_INTERRUPTED", "message": "Previous execution did not finish; no automatic resubmission."})))
                self._db.commit()
                self._snapshot = source_snapshot()
                self.climate = ClimateService(self.data_dir,
                    source_guard=self._assert_source_current, **self._climate_options)
                self._load_sources()
                self.weather.start()
                sources, errors = self.weather.source_records()
                for source in sources:
                    self._register_weather_source(source)
                self._source_errors.extend(errors)
                self.ensemble.start()
                self._stop.clear()
                self._execution_error = None
                self._executor = ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context("spawn"))
                self._thread = threading.Thread(target=self._dispatch, name="balloon-job-dispatch", daemon=True)
                self._thread.start()
            except BaseException:
                self.weather.close()
                if self._db:
                    self._db.close()
                self._db = None
                self._lock_file.close()
                self._lock_file = None
                raise
        return self

    def close(self):
        self.weather.close()
        self._stop.set()
        self._wake.set()
        if self._thread:
            self._thread.join()  # Running work finishes; there is no false immediate cancellation.
        if self._executor:
            self._executor.shutdown(wait=True, cancel_futures=True)
        with self._guard:
            if self._db:
                self._db.close()
                self._db = None
            if self._lock_file:
                self._lock_file.close()
                self._lock_file = None

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.close()

    def _load_sources(self):
        definitions = [("wakayama", "wakayama-gfs-fixture", "和歌山・保存GFS例", "wakayama-isothermal.json", "fixture", "balloon.weather/1"),
                       ("hokkaido", "hokkaido-gfs-fixture", "北海道・保存GFS例", "hokkaido-simple.json", "fixture", "balloon.weather/1"),
                       ("jra3q", "jra3q-surface-fixture", "東海・保存JRA-3Q解析例（暫定地表接続）", "jra3q-ground-flight.json", "saved_jra3q", JRA_SURFACE_SCHEMA)]
        self._sources = {}
        self._source_errors = []
        for name, source_id, label, example, kind, schema in definitions:
            path = REPO_ROOT / "references" / "flight_fixture" / (name + "-weather.json.gz")
            try:
                # An unavailable or malformed source must not block result reopening.
                weather_hash = file_hash(path)
                bundle = read_json(path)
                if bundle["schema"] != schema:
                    raise ValueError("Saved source does not match its declared weather schema.")
                weather = load_weather(path)
                axes, metadata = bundle["axes"], copy.deepcopy(weather.metadata)
                bounds = {"lat": [min(axes["latitude_deg"]), max(axes["latitude_deg"])],
                          "lon": [min(axes["longitude_deg"]), max(axes["longitude_deg"])]}
                if kind == "saved_jra3q":
                    # Native level IDs are not a fixed pressure/height support axis.
                    bounds["model_level"] = [min(axes["model_level"]), max(axes["model_level"])]
                else:
                    bounds["pressure_pa"] = [min(axes["pressure_pa"]), max(axes["pressure_pa"])]
                snapshot = {
                    "id": source_id, "label": label, "sha256": weather_hash, "bytes": path.stat().st_size,
                    "kind": kind, "schema": schema, "product": metadata.get("product"),
                    "time_kind": "analysis_valid_utc" if kind == "saved_jra3q" else "forecast_valid_utc",
                    "run_utc": None if kind == "saved_jra3q" else metadata.get("run_utc"),
                    "valid_times_utc": axes["time_utc"], "bounds": bounds,
                    "metadata": metadata}
                if file_hash(path) != weather_hash:
                    raise ValueError("Saved weather changed during source registration.")
                default_config = validate_config(read_json(REPO_ROOT / "examples" / example))
                canonical(snapshot)
                self._sources[source_id] = {"path": path, "snapshot": snapshot, "default_config": default_config}
            except (OSError, ValueError, KeyError, TypeError, EOFError, zlib.error) as exc:
                self._source_errors.append({"id": source_id, "label": label, "code": "SOURCE_UNAVAILABLE", "message": str(exc)})
        sources, errors = load_historical_sources(os.environ.get("BALLOON_HISTORICAL_CATALOG"))
        self._sources.update(sources)
        self._source_errors.extend(errors)

    def _register_weather_source(self, source):
        with self._guard:
            self._sources[source["snapshot"]["id"]] = source

    def _assert_source_current(self):
        try:
            current = source_snapshot()
        except Exception as exc:
            raise ServiceError(409, "SOURCE_CHANGED", "Application source or environment cannot be verified; restart before new work.") from exc
        if self._snapshot is None or current != self._snapshot:
            raise ServiceError(409, "SOURCE_CHANGED", "Application source or environment changed after startup; restart before new work.")

    def execution_status(self):
        """API availability and flight-worker availability are different states."""
        with self._guard:
            error = self._execution_error
            if error is None and (self._db is None or self._stop.is_set()):
                error = {"code": "EXECUTION_UNAVAILABLE", "message": "Flight execution is not running."}
            elif error is None and self._thread is not None and not self._thread.is_alive():
                error = {"code": "DISPATCHER_UNAVAILABLE", "message": "Flight dispatch stopped; restart the service before new execution."}
            return {"available": error is None, "restart_required": error is not None,
                    "error": copy.deepcopy(error), "queued_policy": "preserved_without_automatic_resubmission"}

    def _assert_execution_available(self):
        status = self.execution_status()
        if not status["available"]:
            raise ServiceError(503, "EXECUTION_UNAVAILABLE", "Flight execution is unavailable. Saved results remain readable; restart the service and explicitly resume unfinished work.")

    def _recover_completed_run(self, run_id):
        """Restore only a complete artifact; retain the previous failure as history."""
        row = self._row(run_id)
        if row["state"] == "completed" and row["result_path"]:
            return False
        spec = json.loads(row["spec"])
        try:
            recovered = recover_result(self.data_dir, run_id, spec)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            error = {"code": "RESULT_RECOVERY_FAILED", "message": str(exc)}
            # Reopening an unchanged rejected artifact need not repeat the event.
            if row["error"] == canonical(error):
                return False
            event = {"outcome": "rejected", "checked_at": utc_now(), "previous_state": row["state"],
                     "previous_error": json.loads(row["error"]) if row["error"] else None, "error": error}
            with self._db:
                self._db.execute("INSERT INTO run_recoveries(run_id,document) VALUES (?,?)", (run_id, canonical(event)))
                self._db.execute("UPDATE jobs SET state='failed',finished_at=?,error=? WHERE run_id=?",
                                 (utc_now(), canonical(error), run_id))
            return False
        if recovered is None:
            return False
        path, hashed, _ = recovered
        event = {"outcome": "recovered", "checked_at": utc_now(), "previous_state": row["state"],
                 "previous_error": json.loads(row["error"]) if row["error"] else None,
                 "result_manifest_hash": hashed, "recomputed": False}
        with self._db:
            self._db.execute("INSERT INTO run_recoveries(run_id,document) VALUES (?,?)", (run_id, canonical(event)))
            self._db.execute("UPDATE runs SET result_path=?,manifest_hash=? WHERE id=?", (path, hashed, run_id))
            self._db.execute("UPDATE jobs SET state='completed',finished_at=?,error=NULL WHERE run_id=?", (utc_now(), run_id))
        return True

    def _recover_registered_results(self):
        rows = self._db.execute("SELECT r.id FROM runs r JOIN jobs j ON r.id=j.run_id WHERE j.state<>'completed' OR r.result_path IS NULL").fetchall()
        for row in rows:
            self._recover_completed_run(row["id"])

    def weather_sources(self):
        with self._guard:
            return {"sources": [copy.deepcopy({**s["snapshot"], "default_config": s["default_config"]}) for s in self._sources.values()],
                    "source_errors": copy.deepcopy(self._source_errors)}

    def weather_ground(self, source_id, query):
        """Read model terrain using exactly the field loader used by the worker.

        This does not change a draft or create a run. Do not hold the job lock
        while loading a field; identity is checked before and after the read.
        """
        query = GroundQuery.model_validate(query).model_dump()
        try:
            time = _utc(query["time_utc"])
        except WeatherError as exc:
            raise ServiceError(422, exc.code, str(exc)) from exc
        with self._guard:
            source = copy.deepcopy(self._sources.get(source_id))
        if source is None:
            raise ServiceError(422, "UNKNOWN_WEATHER_SOURCE", "Select an available saved weather source ID.")
        snapshot, path = source["snapshot"], source["path"]
        if query["expected_sha256"] != snapshot["sha256"]:
            raise ServiceError(409, "WEATHER_CHANGED", "The requested weather identity differs from the registered field; refresh and inspect the source.")
        self._assert_source_current()
        def verify_bytes():
            try:
                current = file_hash(path)
            except OSError as exc:
                raise ServiceError(409, "WEATHER_UNAVAILABLE", "Saved weather cannot be read; restore the source or inspect available sources.") from exc
            if current != snapshot["sha256"]:
                raise ServiceError(409, "WEATHER_CHANGED", "Saved weather changed; restart and inspect its identity.")
        verify_bytes()
        try:
            field = load_weather(path)
        except (OSError, ValueError, KeyError, TypeError, EOFError, zlib.error) as exc:
            raise ServiceError(409, "WEATHER_UNAVAILABLE", "Saved weather cannot be decoded as its declared field.") from exc
        try:
            ground = field.ground_altitude(time, query["latitude_deg"], query["longitude_deg"])
        except WeatherError as exc:
            raise ServiceError(422, exc.code, str(exc)) from exc
        verify_bytes()
        self._assert_source_current()
        return {"schema": "balloon.weather-ground/1", "weather_source_id": source_id,
                "weather_sha256": snapshot["sha256"],
                "query": {key: value for key, value in {**query, "time_utc": time.isoformat()}.items()
                          if key != "expected_sha256"},
                "ground_altitude_m": ground, "clearance_m": query["launch_altitude_m"] - ground,
                "below_model_ground": query["launch_altitude_m"] < ground,
                "ground_model": "jra3q_model_orography" if snapshot.get("kind") == "saved_jra3q" else "coarse_gfs_orography",
                "height_reference": "geometric_asl_m", "is_fine_dem": False,
                "scope": "point_ground_only_not_full_flight_validation"}

    def submit(self, request):
        request = RunRequest.model_validate(request).model_dump()
        try:
            request_hash = digest(request)
        except (ValueError, TypeError) as exc:
            raise ServiceError(422, "INVALID_JSON", "Input must contain finite JSON values.") from exc
        with self._guard:
            previous = self._db.execute("SELECT id,request_hash FROM runs WHERE client_request_id=?", (request["client_request_id"],)).fetchone()
            if previous:
                if previous["request_hash"] != request_hash:
                    raise ServiceError(409, "REQUEST_ID_CONFLICT", "This request ID already refers to different input.")
                return self._acceptance(previous["id"])
            self._assert_execution_available()
            source = self._sources.get(request["weather_source_id"])
            if source is None:
                raise ServiceError(422, "UNKNOWN_WEATHER_SOURCE", "Select an available saved weather source ID.")
            try:
                config = validate_config(request["config"])
            except FlightError as exc:
                raise ServiceError(422, exc.code, str(exc)) from exc
            # Legacy GFS fixtures intentionally retain their support-stop diagnostics.
            if source["snapshot"].get("kind") in {"acquired_gfs", "saved_jra3q"}:
                times = source["snapshot"]["valid_times_utc"]
                launch = _utc(config["launch"]["time_utc"])
                end = launch + timedelta(seconds=config["integration"]["max_duration_s"])
                if launch < _utc(times[0]) or end > _utc(times[-1]):
                    raise ServiceError(422, "WEATHER_WINDOW_UNSUPPORTED", "The selected field must support launch through the full integration duration; re-plan after time or delay edits.")
            self._assert_source_current()
            try:
                weather_hash = file_hash(source["path"])
            except OSError as exc:
                raise ServiceError(409, "WEATHER_UNAVAILABLE", "Saved weather cannot be read; restore the source or restart and inspect available sources.") from exc
            if weather_hash != source["snapshot"]["sha256"]:
                raise ServiceError(409, "WEATHER_CHANGED", "Saved weather changed; restart and inspect its identity.")
            queued = self._db.execute("SELECT count(*) FROM jobs WHERE state='queued'").fetchone()[0]
            if queued >= self.max_queued:
                raise ServiceError(429, "QUEUE_FULL", "The finite waiting queue is full; no run was created.")
            with self._db:
                run_id = self._register_fixed_run(request, config, source["snapshot"], self._snapshot)
            self._wake.set()
            return self._acceptance(run_id)

    def _register_fixed_run(self, request, config, weather_snapshot, source, ensemble=None):
        """Caller owns the lock and transaction; both paths use the same n=1 worker."""
        self._assert_execution_available()
        run_id, job_id = str(uuid.uuid4()), str(uuid.uuid4())
        spec = {"schema": "balloon.run/1", "run_id": run_id,
                "trial_id": ensemble["trial_id"] if ensemble else run_id + ":1", "n": 1, "weight": 1,
                "submitted_input": copy.deepcopy(request), "config": copy.deepcopy(config),
                "weather_snapshot": copy.deepcopy(weather_snapshot), "source_snapshot": copy.deepcopy(source)}
        if ensemble:
            spec["ensemble"] = copy.deepcopy(ensemble)
        spec["frozen_input_hash"] = digest({"config": config, "weather_snapshot": weather_snapshot, "source_snapshot": source})
        folder = self.data_dir / "specs" / run_id
        folder.mkdir()
        write_new_json(folder / "config.json", config)
        spec["config_file_sha256"] = file_hash(folder / "config.json")
        write_new_json(folder / "run.json", spec)
        self._db.execute("INSERT INTO runs VALUES (?,?,?,?,?,NULL,NULL)",
                         (run_id, request["client_request_id"], digest(request), canonical(spec), utc_now()))
        self._db.execute("INSERT INTO jobs VALUES (?,?,'queued',NULL,NULL,NULL)", (job_id, run_id))
        return run_id

    def _row(self, run_id):
        row = self._db.execute("SELECT r.*,j.id AS job_id,j.state,j.started_at,j.finished_at,j.error FROM runs r JOIN jobs j ON r.id=j.run_id WHERE r.id=?", (run_id,)).fetchone()
        if not row:
            raise ServiceError(404, "RUN_NOT_FOUND", "Run does not exist.")
        return row

    def _summary(self, row):
        spec = json.loads(row["spec"])
        request = spec["submitted_input"]
        return {"run_id": row["id"], "job_id": row["job_id"], "state": row["state"],
                "kind": "ensemble_trial" if "ensemble" in spec else "single_run", "ensemble": spec.get("ensemble"),
                "label": request["label"], "candidate_id": request["candidate_id"], "candidate_revision": request["candidate_revision"],
                "weather_source_id": request["weather_source_id"], "created_at": row["created_at"],
                "result_available": row["result_path"] is not None and row["state"] == "completed",
                "cancellable": row["state"] == "queued", "frozen_input_hash": spec["frozen_input_hash"],
                "error": json.loads(row["error"]) if row["error"] else None}

    def _acceptance(self, run_id):
        detail = self._summary(self._row(run_id))
        return {key: detail[key] for key in ("run_id", "job_id", "state", "frozen_input_hash")}

    def list_runs(self, include_ensemble=False):
        with self._guard:
            rows = self._db.execute("SELECT id FROM runs ORDER BY created_at DESC,id DESC").fetchall()
            results = [self._summary(self._row(row["id"])) for row in rows]
            return {"runs": [r for r in results if include_ensemble or r["kind"] == "single_run"]}

    def get_run(self, run_id):
        with self._guard:
            row = self._row(run_id)
            recovery = [json.loads(r["document"]) for r in self._db.execute("SELECT document FROM run_recoveries WHERE run_id=? ORDER BY id", (run_id,))]
            return {**self._summary(row), "spec": json.loads(row["spec"]), "started_at": row["started_at"], "finished_at": row["finished_at"],
                    "recovery": recovery}

    def get_run_request(self, client_request_id):
        """Read an accepted intent without source checks, computation or resubmission."""
        with self._guard:
            row = self._db.execute("SELECT id FROM runs WHERE client_request_id=?", (client_request_id,)).fetchone()
            if row is None:
                raise ServiceError(404, "RUN_REQUEST_NOT_FOUND", "This request ID has not been accepted at the time of this check.")
            return self.get_run(row["id"])

    def get_result(self, run_id):
        with self._guard:
            row = self._row(run_id)
            if not row["result_path"] or row["state"] != "completed":
                raise ServiceError(409, "RESULT_NOT_AVAILABLE", "This run has no committed result.")
            spec = json.loads(row["spec"])
            try:
                result = read_result(self.data_dir, row["result_path"], row["manifest_hash"], run_id)
            except (ValueError, OSError, KeyError) as exc:
                raise ServiceError(500, "RESULT_INTEGRITY_ERROR", "Saved result failed integrity verification.") from exc
            return {"run_id": run_id, "trial_id": spec["trial_id"], "n": 1, "weight": 1,
                    "kind": "ensemble_trial" if "ensemble" in spec else "single_run", "ensemble": spec.get("ensemble"),
                    "weather_snapshot": spec["weather_snapshot"], "source_snapshot": spec["source_snapshot"], "result": result}

    def cancel(self, run_id):
        with self._guard:
            row = self._row(run_id)
            if row["state"] != "queued":
                raise ServiceError(409, "NOT_CANCELLABLE", "Only waiting work can be cancelled; running computation cannot be stopped here.")
            with self._db:
                self._db.execute("UPDATE jobs SET state='cancelled',finished_at=? WHERE run_id=?", (utc_now(), run_id))
            return self.get_run(run_id)

    def get_project(self):
        with self._guard:
            row = self._db.execute("SELECT * FROM projects WHERE id='default'").fetchone()
            return {"revision": row["revision"], "project": json.loads(row["document"])}

    def save_project(self, update):
        update = ProjectUpdate.model_validate(update).model_dump(by_alias=True)
        project = update["project"]
        try:
            canonical(project)  # reject NaN/Infinity even in incomplete drafts
        except (ValueError, TypeError) as exc:
            raise ServiceError(422, "INVALID_JSON", "Draft must contain finite JSON values.") from exc
        with self._guard:
            current = self.get_project()
            if update["expected_revision"] != current["revision"]:
                raise ServiceError(409, "PROJECT_REVISION_CONFLICT", "Draft changed since it was read; reload before saving.")
            if len({c["id"] for c in project["candidates"]}) != len(project["candidates"]):
                raise ServiceError(422, "DUPLICATE_CANDIDATE", "Candidate IDs must be unique.")
            by_id = {c["id"]: c for c in project["candidates"]}
            for candidate in project["candidates"]:
                parent_id = candidate["parent_id"]
                if parent_id is None:
                    if candidate["delay_minutes"] is not None:
                        raise ServiceError(422, "INVALID_DELAY_PARENT", "A delay requires a parent candidate.")
                    continue
                if parent_id not in by_id or candidate["delay_minutes"] is None:
                    raise ServiceError(422, "INVALID_DELAY_PARENT", "A dependent candidate needs an existing parent and an explicit delay.")
                seen = {candidate["id"]}
                while parent_id is not None:
                    if parent_id in seen:
                        raise ServiceError(422, "CYCLIC_CANDIDATES", "Dependent candidates must not form a cycle.")
                    seen.add(parent_id)
                    parent = by_id.get(parent_id)
                    if parent is None:
                        raise ServiceError(422, "INVALID_DELAY_PARENT", "The parent chain contains a missing candidate.")
                    parent_id = parent["parent_id"]
            if len(set(project["compare_run_ids"])) != len(project["compare_run_ids"]):
                raise ServiceError(422, "DUPLICATE_COMPARISON", "A fixed result can only appear once in a comparison.")
            for run_id in project["compare_run_ids"]:
                row = self._row(run_id)
                if "ensemble" in json.loads(row["spec"]):
                    raise ServiceError(422, "ENSEMBLE_COMPARISON_REFERENCE", "Use a fixed ensemble case reference, not an internal trial attempt.")
                if row["state"] != "completed" or not row["result_path"]:
                    raise ServiceError(409, "COMPARISON_RESULT_NOT_READY", "Comparison selections require committed results; the previous selection was kept.")
            seen_refs = set()
            for ref in project["compare_results"] or []:
                if ref["kind"] == "single_run":
                    run = self.get_run(ref["run_id"])
                    if run["kind"] != "single_run" or not run["result_available"]:
                        raise ServiceError(409, "COMPARISON_RESULT_NOT_READY", "Select a committed independent run.")
                    key = ("single_run", ref["run_id"])
                else:
                    case = self.ensemble.case_result(ref["snapshot_id"], ref["case_id"])
                    if case["ensemble_id"] != ref["ensemble_id"]:
                        raise ServiceError(422, "ENSEMBLE_REFERENCE_MISMATCH", "Case and ensemble identities differ.")
                    if ref["analysis_id"]:
                        analysis = self.ensemble.analysis(ref["analysis_id"])
                        if (analysis["snapshot_id"], analysis["case_id"]) != (ref["snapshot_id"], ref["case_id"]):
                            raise ServiceError(422, "ANALYSIS_REFERENCE_MISMATCH", "Analysis belongs to another fixed case.")
                    key = ("ensemble_case", ref["snapshot_id"], ref["case_id"], ref["analysis_id"])
                if key in seen_refs:
                    raise ServiceError(422, "DUPLICATE_COMPARISON", "A fixed result can only appear once.")
                seen_refs.add(key)
            with self._db:
                self._db.execute("UPDATE projects SET revision=revision+1,document=? WHERE id='default'", (canonical(project),))
            return self.get_project()

    def _dispatch(self):
        while not self._stop.is_set():
            with self._guard:
                row = None
                if self._execution_error is None:
                    self.ensemble.tick()
                    row = self._db.execute("SELECT r.id,r.spec FROM runs r JOIN jobs j ON r.id=j.run_id WHERE j.state='queued' ORDER BY r.created_at,r.id LIMIT 1").fetchone()
                if row:
                    with self._db:
                        self._db.execute("UPDATE jobs SET state='running',started_at=? WHERE run_id=?", (utc_now(), row["id"]))
                        self.ensemble.mark_running(row["id"])
            if not row:
                self._wake.wait(0.25)
                self._wake.clear()
                continue
            run_id, spec = row["id"], json.loads(row["spec"])
            try:
                source = self._sources[spec["weather_snapshot"]["id"]]
                future = self._executor.submit(execute_run, spec, str(source["path"]),
                                               str(self.data_dir / "specs" / run_id / "config.json"),
                                               str(self.data_dir / "staging" / run_id))
                completion = future.result()
                if completion["run_id"] != run_id:
                    raise ValueError("worker returned a different run")
                path, marker_hash = publish_result(self.data_dir, run_id, spec)
                with self._guard, self._db:
                    self._db.execute("UPDATE runs SET result_path=?,manifest_hash=? WHERE id=?", (path, marker_hash, run_id))
                    self._db.execute("UPDATE jobs SET state='completed',finished_at=? WHERE run_id=?", (utc_now(), run_id))
            except Exception as exc:
                broken = isinstance(exc, BrokenProcessPool)
                error = {"code": "WORKER_PROCESS_BROKEN" if broken else "EXECUTION_FAILED", "message": str(exc)}
                with self._guard, self._db:
                    self._db.execute("UPDATE jobs SET state='failed',finished_at=?,error=? WHERE run_id=?", (utc_now(), canonical(error), run_id))
                    if broken:
                        self._execution_error = {"code": "WORKER_PROCESS_BROKEN", "message": "Flight worker exited unexpectedly. Pending work is preserved; restart the service before explicitly resuming."}
                with self._guard:
                    # A publication/registry failure can leave a fully committed
                    # output. Recover it rather than instructing a duplicate run.
                    self._recover_completed_run(run_id)
                    if broken and "ensemble" in spec:
                        self.ensemble._refresh(spec["ensemble"]["ensemble_id"])
