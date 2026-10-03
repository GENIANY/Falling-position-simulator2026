"""Persistent trial orchestration inside ApplicationService's one-worker lifecycle."""
import copy
import json
import uuid

from balloon_sim.flight.config import FlightError
from backend.errors import ServiceError
from backend.storage import canonical, digest, file_hash, recover_result, utc_now
from .contracts import AnalysisRequest, CancelRequest, HistoricalPlanRequest, PlanRequest, RetryRequest, SubmitRequest
from .planning import MAX_ACTIVE, MAX_HISTORY_BYTES, build_plan, capabilities
from . import storage
from .views import compact, counts

ACTIVE = {"queued", "running", "cancelling"}
RETRYABLE = {"unstarted", "cancelled", "interrupted", "failed"}
SUCCESS = {"landed", "stopped"}
CLASSIFIER_PATHS = ("frontend/src/screens/forecast/math.js", "frontend/src/screens/forecast/controller.js",
                    "frontend/src/screens/shared/scene-style.js")


def identity():
    return str(uuid.uuid4())


class EnsembleService:
    """Uses the parent's registry, lock and dispatch loop; starts no threads."""
    def __init__(self, application):
        self.app = application

    @property
    def db(self):
        return self.app._db

    @property
    def root(self):
        return self.app.data_dir

    def _artifact(self, table, key):
        if table not in {"ensemble_plans", "ensemble_snapshots", "ensemble_analyses"}:
            raise ValueError("invalid artifact table")
        row = self.db.execute(f"SELECT * FROM {table} WHERE id=?", (key,)).fetchone()
        if row is None:
            raise ServiceError(404, "ENSEMBLE_ARTIFACT_NOT_FOUND", "Saved ensemble artifact does not exist.")
        try:
            return storage.read(self.root, key, row["document_hash"])
        except (ValueError, OSError, KeyError) as exc:
            raise ServiceError(500, "ENSEMBLE_INTEGRITY_ERROR", "Saved ensemble artifact failed integrity verification.") from exc

    def start(self):
        storage.create_tables(self.db)
        # The parent already marked unfinished run jobs interrupted. Recover a
        # fully published result before interpreting an attempt as incomplete.
        for row in self.db.execute("SELECT id FROM ensembles WHERE state IN ('queued','running','cancelling')").fetchall():
            eid = row["id"]
            self._refresh(eid)
            with self.db:
                self.db.execute("UPDATE ensembles SET state='interrupted',revision=revision+1 WHERE id=?", (eid,))
            self._finalize(eid, interrupted=True)

    def get_plan(self, key):
        with self.app._guard:
            return self._artifact("ensemble_plans", key)

    def list_plans(self):
        with self.app._guard:
            plans = [self.get_plan(r["id"]) for r in self.db.execute("SELECT id FROM ensemble_plans ORDER BY created_at DESC,id")]
            return {"plans": [{k: p[k] for k in ("plan_id", "plan_hash", "created_at", "label", "status", "trial_count", "drawset_id")}
                              for p in plans]}

    def plan(self, body):
        historical = body.get("mode") == "historical_windows"
        body = (HistoricalPlanRequest if historical else PlanRequest).model_validate(body).model_dump()
        try:
            request_hash = digest(body)
        except (ValueError, TypeError) as exc:
            raise ServiceError(422, "INVALID_JSON", "Plan inputs must contain finite JSON values.") from exc
        with self.app._guard:
            old = self.db.execute("SELECT id,request_hash FROM ensemble_plans WHERE request_id=?", (body["client_request_id"],)).fetchone()
            if old:
                if old["request_hash"] != request_hash:
                    raise ServiceError(409, "REQUEST_ID_CONFLICT", "Plan request ID already refers to different input.")
                return self.get_plan(old["id"])
            self.app._assert_source_current()
            key = identity()
            if historical:
                from .historical_planning import build_historical_plan
                plan = build_historical_plan(key, body, self.app._sources, copy.deepcopy(self.app._snapshot))
            else:
                source = self.app._sources.get(body["weather_source_id"])
                if source is None:
                    raise ServiceError(422, "UNKNOWN_WEATHER_SOURCE", "Select an available fixed weather asset.")
                self._verify_weather(source, source["snapshot"])
                plan = build_plan(key, body, copy.deepcopy(source["snapshot"]), copy.deepcopy(self.app._snapshot))
            self.app._assert_source_current()
            self._ensure_plan_current(plan)
            hashed = storage.publish(self.root, key, plan)
            with self.db:
                self.db.execute("INSERT INTO ensemble_plans VALUES (?,?,?,?,?)",
                                (key, body["client_request_id"], request_hash, hashed, utc_now()))
            return plan

    def _ensure_plan_current(self, plan):
        self.app._assert_source_current()
        if plan["source_snapshot"] != self.app._snapshot:
            raise ServiceError(409, "ENSEMBLE_SOURCE_CHANGED", "This plan belongs to different code or numerical dependencies; create a new plan instead of resolving it again.")
        snapshots = ([w["weather_snapshot"] for w in plan["weather_windows"] if w["weather_snapshot"]]
                     if plan.get("mode") == "historical_windows" else [plan["weather_snapshot"]])
        for expected in snapshots:
            self._verify_weather(self.app._sources.get(expected["id"]), expected)

    @staticmethod
    def _verify_weather(source, expected):
        try:
            matches = source is not None and file_hash(source["path"]) == expected["sha256"]
        except OSError:
            matches = False
        if not matches:
            raise ServiceError(409, "ENSEMBLE_WEATHER_CHANGED", "The original fixed weather asset is unavailable or changed.")

    def _capacity(self):
        if self.db.execute("SELECT count(*) FROM ensembles WHERE state IN ('queued','running','cancelling')").fetchone()[0] >= MAX_ACTIVE:
            raise ServiceError(429, "ENSEMBLE_QUEUE_FULL", "Four ensembles are active; no partial trial set was accepted.")

    def submit(self, body):
        body = SubmitRequest.model_validate(body).model_dump()
        request_hash = digest(body)
        with self.app._guard:
            old = self.db.execute("SELECT id,request_hash FROM ensembles WHERE request_id=?", (body["client_request_id"],)).fetchone()
            if old:
                if old["request_hash"] != request_hash:
                    raise ServiceError(409, "REQUEST_ID_CONFLICT", "Execution request ID already refers to another plan.")
                return self.get(old["id"])
            self.app._assert_execution_available()
            plan = self.get_plan(body["plan_id"])
            if body["plan_hash"] != plan["plan_hash"]:
                raise ServiceError(409, "PLAN_HASH_MISMATCH", "Execution must name the exact previewed plan.")
            if plan["status"] != "ready":
                raise ServiceError(422, "PLAN_UNAVAILABLE", "Resolve the saved plan blockers before execution.")
            self._ensure_plan_current(plan)
            self._capacity()
            eid = identity()
            with self.db:
                self.db.execute("INSERT INTO ensembles VALUES (?,?,?,?,'queued',1,1,?,NULL,NULL,NULL)",
                                (eid, body["client_request_id"], request_hash, plan["plan_id"], utc_now()))
                for trial in plan["trials"]:
                    tid = identity()
                    self.db.execute("INSERT INTO ensemble_trials VALUES (?,?,?,?,?,?,0,NULL,?)",
                                    (tid, eid, trial["ordinal"], trial["case_id"], trial["draw_id"],
                                     "invalid_input" if trial["preflight_error"] else "unstarted",
                                     canonical(trial["preflight_error"]) if trial["preflight_error"] else None))
            self.app._wake.set()
            return self.get(eid)

    def _row(self, eid):
        row = self.db.execute("SELECT * FROM ensembles WHERE id=?", (eid,)).fetchone()
        if not row:
            raise ServiceError(404, "ENSEMBLE_NOT_FOUND", "Ensemble does not exist.")
        return row

    def _rows(self, eid):
        return [dict(row) for row in self.db.execute("SELECT * FROM ensemble_trials WHERE ensemble_id=? ORDER BY ordinal,case_id", (eid,))]

    def get(self, eid):
        with self.app._guard:
            row = self._row(eid)
            plan = self.get_plan(row["plan_id"])
            trials = self._rows(eid)
            return {"schema": "balloon.ensemble.job/1", "ensemble_id": eid, "plan_id": plan["plan_id"],
                    "mode": plan.get("mode", "equipment_sensitivity"),
                    "plan_hash": plan["plan_hash"], "label": plan["label"], "drawset_id": plan["drawset_id"],
                    "state": row["state"], "epoch": row["epoch"], "state_revision": row["revision"],
                    "created_at": row["created_at"], "planned_trials": len(trials), "counts": counts(trials),
                    "cases": [{"case_id": c["case_id"], "candidate_id": c["candidate_id"],
                               "candidate_revision": c["candidate_revision"], "label": c["label"],
                               "counts": counts([t for t in trials if t["case_id"] == c["case_id"]])} for c in plan["cases"]],
                    "latest_snapshot_id": row["snapshot_id"],
                    "snapshots": [dict(s) for s in self.db.execute("SELECT id AS snapshot_id,epoch,created_at FROM ensemble_snapshots WHERE ensemble_id=? ORDER BY epoch,created_at", (eid,))],
                    "cancellable": row["state"] in {"queued", "running"},
                    "retryable": row["state"] not in ACTIVE and (any(t["state"] in RETRYABLE for t in trials) or not self._has_snapshot(eid, row["epoch"])),
                    "error": json.loads(row["error"]) if row["error"] else None}

    def list(self):
        with self.app._guard:
            return {"ensembles": [self.get(r["id"]) for r in self.db.execute("SELECT id FROM ensembles ORDER BY created_at DESC,id")]}

    def trials(self, eid, case_id=None, offset=0, limit=256):
        with self.app._guard:
            row = self._row(eid)
            plan = self.get_plan(row["plan_id"])
            if case_id is not None and case_id not in {c["case_id"] for c in plan["cases"]}:
                raise ServiceError(404, "CASE_NOT_FOUND", "Case is not part of the fixed plan.")
            fixed = {(t["case_id"], t["draw_id"]): t for t in plan["trials"]}
            rows = [r for r in self._rows(eid) if case_id is None or r["case_id"] == case_id]
            for r in rows:
                r["error"] = json.loads(r["error"]) if r["error"] else None
            return {"ensemble_id": eid, "state_revision": row["revision"], "counts": counts(rows),
                    "total": len(rows), "offset": offset,
                    "trials": [compact(r, fixed[r["case_id"], r["draw_id"]], plan["sampling"]["variable"])
                               for r in rows[offset:offset+limit]]}

    def _has_snapshot(self, eid, epoch):
        return self.db.execute("SELECT id FROM ensemble_snapshots WHERE ensemble_id=? AND epoch=?", (eid, epoch)).fetchone() is not None

    def mark_running(self, run_id):
        row = self.db.execute("SELECT ensemble_id FROM ensemble_trials WHERE run_id=?", (run_id,)).fetchone()
        if row:
            self.db.execute("UPDATE ensemble_trials SET state='running' WHERE run_id=?", (run_id,))
            self.db.execute("UPDATE ensemble_attempts SET state='running' WHERE run_id=?", (run_id,))
            self.db.execute("UPDATE ensembles SET revision=revision+1 WHERE id=?", (row["ensemble_id"],))

    def _recover(self, run_id):
        run = self.app._row(run_id)
        if run["state"] == "completed" and run["result_path"]:
            return
        recovered = recover_result(self.root, run_id, json.loads(run["spec"]))
        if recovered:
            path, hashed, _ = recovered
            with self.db:
                self.db.execute("UPDATE runs SET result_path=?,manifest_hash=? WHERE id=?", (path, hashed, run_id))
                self.db.execute("UPDATE jobs SET state='completed',finished_at=?,error=NULL WHERE run_id=?", (utc_now(), run_id))

    def _refresh(self, eid):
        changed = False
        for trial in self._rows(eid):
            if not trial["run_id"] or trial["state"] in SUCCESS:
                continue
            try:
                self._recover(trial["run_id"])
                run = self.app._row(trial["run_id"])
                state, error = run["state"], run["error"]
                if state == "completed":
                    state = self.app.get_result(trial["run_id"])["result"]["status"]
            except (ValueError, OSError, ServiceError, KeyError) as exc:
                state, error = "failed", canonical({"code": "RESULT_RECOVERY_FAILED", "message": str(exc)})
            if state != trial["state"] or error != trial["error"]:
                with self.db:
                    self.db.execute("UPDATE ensemble_trials SET state=?,error=? WHERE id=?", (state, error, trial["id"]))
                    self.db.execute("UPDATE ensemble_attempts SET state=? WHERE trial_id=? AND attempt=?", (state, trial["id"], trial["attempt"]))
                changed = True
        if changed:
            with self.db:
                self.db.execute("UPDATE ensembles SET revision=revision+1 WHERE id=?", (eid,))

    def tick(self):
        """Called under the parent lock only, before its ordinary queue lookup."""
        rows = self.db.execute("SELECT id FROM ensembles WHERE state IN ('queued','running','cancelling') ORDER BY COALESCE(last_dispatch,''),created_at,id").fetchall()
        for row in rows:
            eid = row["id"]
            try:
                self._refresh(eid)
                trials = self._rows(eid)
                if not any(t["state"] in {"unstarted", "queued", "running"} for t in trials):
                    self._finalize(eid)
            except Exception as exc:
                # Corrupt ensemble metadata must not kill the independent n=1 dispatcher.
                with self.db:
                    self.db.execute("UPDATE ensembles SET state='failed',revision=revision+1,error=? WHERE id=?",
                                    (canonical({"code": "ENSEMBLE_STATE_ERROR", "message": str(exc)}), eid))
        queued = self.db.execute("SELECT count(*) FROM jobs WHERE state='queued'").fetchone()[0]
        ensemble_queued = self.db.execute("SELECT count(*) FROM ensemble_trials WHERE state='queued'").fetchone()[0]
        if queued >= self.app.max_queued or ensemble_queued:
            return
        for row in rows:
            eid = row["id"]
            ensemble = self._row(eid)
            if ensemble["state"] not in {"queued", "running"}:
                continue
            pending = next((t for t in self._rows(eid) if t["state"] == "unstarted"), None)
            if pending is None:
                continue
            try:
                plan = self.get_plan(ensemble["plan_id"])
                self._ensure_plan_current(plan)
                fixed = next(t for t in plan["trials"] if t["case_id"] == pending["case_id"] and t["draw_id"] == pending["draw_id"])
                case = next(c for c in plan["cases"] if c["case_id"] == pending["case_id"])
                attempt = pending["attempt"] + 1
                join = {"ensemble_id": eid, "plan_id": plan["plan_id"], "case_id": pending["case_id"],
                        "drawset_id": plan["drawset_id"], "draw_id": pending["draw_id"], "trial_id": pending["id"],
                        "attempt": attempt, "epoch": ensemble["epoch"]}
                weather_snapshot = fixed.get("weather_snapshot") or plan["weather_snapshot"]
                request = {"client_request_id": f"ensemble:{pending['id']}:{attempt}", "candidate_id": case["candidate_id"],
                           "candidate_revision": case["candidate_revision"], "label": case["label"],
                           "weather_source_id": weather_snapshot["id"], "config": fixed["config"]}
                # Register run+job and trial linkage in the same outer transaction.
                with self.db:
                    run_id = self.app._register_fixed_run(request, fixed["config"], weather_snapshot, plan["source_snapshot"], join)
                    self.db.execute("INSERT INTO ensemble_attempts VALUES (?,?,?,?,?)", (pending["id"], attempt, ensemble["epoch"], run_id, "queued"))
                    self.db.execute("UPDATE ensemble_trials SET state='queued',attempt=?,run_id=?,error=NULL WHERE id=?", (attempt, run_id, pending["id"]))
                    self.db.execute("UPDATE ensembles SET state='running',revision=revision+1,last_dispatch=? WHERE id=?", (utc_now(), eid))
                return
            except Exception as exc:
                with self.db:
                    self.db.execute("UPDATE ensembles SET state='interrupted',revision=revision+1,error=? WHERE id=?",
                                    (canonical({"code": getattr(exc, "code", "ENSEMBLE_DISPATCH_FAILED"), "message": str(exc)}), eid))
                self._finalize(eid, interrupted=True)

    def cancel(self, eid, body):
        body = CancelRequest.model_validate(body).model_dump()
        request_hash = digest({"action": "cancel", "ensemble_id": eid, **body})
        with self.app._guard:
            previous = self.db.execute("SELECT request_hash,response FROM ensemble_commands WHERE request_id=?", (body["client_request_id"],)).fetchone()
            if previous:
                if previous["request_hash"] != request_hash:
                    raise ServiceError(409, "REQUEST_ID_CONFLICT", "Cancel ID already names another command.")
                return json.loads(previous["response"])
            ensemble = self._row(eid)
            if ensemble["state"] not in ACTIVE:
                response = self.get(eid)
                with self.db:
                    self.db.execute("INSERT INTO ensemble_commands VALUES (?,?,?)", (body["client_request_id"], request_hash, canonical(response)))
                return response
            with self.db:
                self.db.execute("UPDATE ensembles SET state='cancelling',revision=revision+1 WHERE id=?", (eid,))
                for t in self._rows(eid):
                    if t["state"] == "unstarted":
                        self.db.execute("UPDATE ensemble_trials SET state='cancelled' WHERE id=?", (t["id"],))
                    elif t["state"] == "queued":
                        # Parent job state wins if it was already selected to run.
                        self.db.execute("UPDATE jobs SET state='cancelled',finished_at=? WHERE run_id=? AND state='queued'", (utc_now(), t["run_id"]))
                # The receipt and cancellation intent are one transaction. A
                # lost response cannot later cancel a newly retried epoch.
                response = self.get(eid)
                self.db.execute("INSERT INTO ensemble_commands VALUES (?,?,?)", (body["client_request_id"], request_hash, canonical(response)))
            self._refresh(eid)
            if not any(t["state"] == "running" for t in self._rows(eid)):
                self._finalize(eid)
            self.app._wake.set()
            return response

    def retry(self, eid, body):
        body = RetryRequest.model_validate(body).model_dump()
        request_hash = digest({"action": "retry", "ensemble_id": eid, **body})
        with self.app._guard:
            previous = self.db.execute("SELECT request_hash,response FROM ensemble_commands WHERE request_id=?", (body["client_request_id"],)).fetchone()
            if previous:
                if previous["request_hash"] != request_hash:
                    raise ServiceError(409, "REQUEST_ID_CONFLICT", "Retry ID already names another selection.")
                return json.loads(previous["response"])
            self.app._assert_execution_available()
            ensemble = self._row(eid)
            if ensemble["state"] in ACTIVE:
                raise ServiceError(409, "ENSEMBLE_ACTIVE", "Wait for the current epoch to settle before retry.")
            self._refresh(eid)  # Also recover a renamed final after a same-process DB failure.
            plan = self.get_plan(ensemble["plan_id"])
            self._ensure_plan_current(plan)
            rows = {t["id"]: t for t in self._rows(eid)}
            selected = body["trial_ids"]
            if len(selected) != len(set(selected)) or any(t not in rows for t in selected):
                raise ServiceError(422, "INVALID_TRIAL_SELECTION", "Retry must name distinct trials from this ensemble.")
            if any(rows[t]["error"] and json.loads(rows[t]["error"]).get("code") == "RESULT_RECOVERY_FAILED" for t in selected):
                raise ServiceError(409, "RESULT_RECOVERY_REQUIRED", "An existing final result failed recovery verification; inspect it before creating another attempt.")
            if any(rows[t]["state"] not in RETRYABLE for t in selected):
                raise ServiceError(409, "TRIAL_NOT_RETRYABLE", "Completed physical results and invalid input rows cannot be retried.")
            if not selected:
                if self._has_snapshot(eid, ensemble["epoch"]):
                    raise ServiceError(422, "EMPTY_RETRY", "Select unfinished trials to retry.")
                self._finalize(eid, interrupted=ensemble["state"] == "interrupted")
                response = self.get(eid)
                with self.db:
                    self.db.execute("INSERT INTO ensemble_commands VALUES (?,?,?)", (body["client_request_id"], request_hash, canonical(response)))
            else:
                self._capacity()
                with self.db:
                    for tid in selected:
                        self.db.execute("UPDATE ensemble_trials SET state='unstarted',run_id=NULL,error=NULL WHERE id=?", (tid,))
                    self.db.execute("UPDATE ensembles SET state='queued',epoch=epoch+1,revision=revision+1,error=NULL WHERE id=?", (eid,))
                    response = self.get(eid)
                    self.db.execute("INSERT INTO ensemble_commands VALUES (?,?,?)", (body["client_request_id"], request_hash, canonical(response)))
                self.app._wake.set()
            return response

    def _finalize(self, eid, interrupted=False):
        ensemble = self._row(eid)
        if self._has_snapshot(eid, ensemble["epoch"]):
            return
        plan = self.get_plan(ensemble["plan_id"])
        rows = self._rows(eid)
        if any(t["state"] in {"queued", "running"} for t in rows):
            return
        if not interrupted and any(t["state"] == "unstarted" for t in rows):
            return
        sid = identity()
        try:
            from balloon_sim.ensemble.statistics import analyze_results
            cases = []
            for case in plan["cases"]:
                fixed = {t["draw_id"]: t for t in plan["trials"] if t["case_id"] == case["case_id"]}
                small, items = [], []
                case_rows = [t for t in rows if t["case_id"] == case["case_id"]]
                history_bytes = sum((self.root / "results" / t["run_id"] / "result.json").stat().st_size
                                    for t in case_rows if t["state"] in SUCCESS)
                omit_history = history_bytes > MAX_HISTORY_BYTES
                omitted_count = 0
                for t in rows:
                    if t["case_id"] != case["case_id"]:
                        continue
                    result = None
                    if t["state"] in SUCCESS:
                        result = self.app.get_result(t["run_id"])["result"]
                        t["result_manifest_hash"] = self.app._row(t["run_id"])["manifest_hash"]
                    t["error"] = json.loads(t["error"]) if t["error"] else None
                    small.append(compact(t, fixed[t["draw_id"]], plan["sampling"]["variable"], result))
                    if omit_history and result is not None:
                        omitted_count += int(bool(result["records"]))
                        result = {**result, "records": []}  # analysis-only projection, never stored over the raw result
                    items.append({"trial_id": t["id"], "result": result})
                analysis = None
                warning = None
                if plan["source_snapshot"] == self.app._snapshot:
                    try:
                        self.app._assert_source_current()
                        analysis = analyze_results(items)
                        self._history_limit(analysis, history_bytes, omitted_count, omit_history)
                        self.app._assert_source_current()
                    except Exception as exc:
                        analysis = None
                        warning = {"code": "ANALYSIS_UNAVAILABLE", "message": str(exc)}
                else:
                    warning = {"code": "ANALYSIS_SOURCE_CHANGED", "message": "Recovered results remain readable; request a separately versioned analysis for this code."}
                ccounts = counts(small)
                cases.append({"schema": "balloon.ensemble.case-result/1", "ensemble_id": eid, "snapshot_id": sid,
                              "case_id": case["case_id"], "plan_id": plan["plan_id"], "drawset_id": plan["drawset_id"],
                              "epoch": ensemble["epoch"], "candidate": {"id": case["candidate_id"], "revision": case["candidate_revision"], "label": case["label"]},
                              "sampling": plan["sampling"], "submitted_config": case["submitted_config"],
                              "mode": plan.get("mode", "equipment_sensitivity"),
                              "weather_windows": plan.get("weather_windows"),
                              "selection_context": plan.get("selection_context"),
                              "resolved_base_config": case["resolved_base_config"], "weather_snapshot": plan["weather_snapshot"],
                              "source_snapshot": plan["source_snapshot"], "settled": True,
                              "all_requested_have_physical_result": ccounts["landed"]+ccounts["stopped"] == ccounts["planned"],
                              "counts": ccounts, "weights": {"planned": len(small), "landed": ccounts["landed"], "stopped": ccounts["stopped"]},
                              "trials": small, "overview_analysis": analysis, "overview_analysis_id": None,
                              "warnings": [warning] if warning else []})
            state = "interrupted" if interrupted else ("cancelled" if ensemble["state"] == "cancelling" else "completed")
            doc = {"schema": "balloon.ensemble.snapshot/1", "snapshot_id": sid, "ensemble_id": eid,
                   "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"], "drawset_id": plan["drawset_id"],
                   "epoch": ensemble["epoch"], "state": state, "created_at": utc_now(), "counts": counts(rows), "cases": cases}
            hashed = storage.publish(self.root, sid, doc)
            with self.db:
                self.db.execute("INSERT INTO ensemble_snapshots VALUES (?,?,?,?,?)", (sid, eid, ensemble["epoch"], hashed, utc_now()))
                self.db.execute("UPDATE ensembles SET state=?,snapshot_id=?,revision=revision+1 WHERE id=?", (state, sid, eid))
        except Exception as exc:
            with self.db:
                self.db.execute("UPDATE ensembles SET state='failed',revision=revision+1,error=? WHERE id=?",
                                (canonical({"code": "SNAPSHOT_FAILED", "message": str(exc)}), eid))

    def snapshot(self, sid):
        with self.app._guard:
            return self._artifact("ensemble_snapshots", sid)

    def case_result(self, sid, case_id):
        snapshot = self.snapshot(sid)
        case = next((c for c in snapshot["cases"] if c["case_id"] == case_id), None)
        if case is None:
            raise ServiceError(404, "CASE_NOT_FOUND", "Case is not part of this fixed snapshot.")
        return case

    def trial_result(self, sid, tid):
        with self.app._guard:
            snapshot = self.snapshot(sid)
            trial = next((t for c in snapshot["cases"] for t in c["trials"] if t["trial_id"] == tid), None)
            if trial is None:
                raise ServiceError(404, "TRIAL_NOT_FOUND", "Trial is not part of this fixed snapshot.")
            if not trial["result_available"]:
                raise ServiceError(409, "RESULT_NOT_AVAILABLE", "The selected snapshot has no physical result for this trial.")
            run = self.app._row(trial["run_id"])
            if run["manifest_hash"] != trial["result_manifest_hash"]:
                raise ServiceError(500, "ENSEMBLE_INTEGRITY_ERROR", "Fixed snapshot result reference changed.")
            return self.app.get_result(trial["run_id"])

    def analyze(self, body):
        body = AnalysisRequest.model_validate(body).model_dump()
        try:
            encoded = canonical(body)
        except (ValueError, TypeError) as exc:
            raise ServiceError(422, "INVALID_JSON", "Selection provenance must be finite JSON.") from exc
        if len(encoded.encode("utf-8")) > 1024*1024:
            raise ServiceError(422, "ANALYSIS_LIMIT", "Region and selection provenance exceeds the local 1 MiB limit.")
        request_hash = digest(body)
        with self.app._guard:
            old = self.db.execute("SELECT id,request_hash FROM ensemble_analyses WHERE request_id=?", (body["client_request_id"],)).fetchone()
            if old:
                if old["request_hash"] != request_hash:
                    raise ServiceError(409, "REQUEST_ID_CONFLICT", "Analysis request ID names different input.")
                return self.analysis(old["id"])
            self.app._assert_source_current()
            case = self.case_result(body["snapshot_id"], body["case_id"])
            ids = [t["trial_id"] for t in case["trials"]]
            selected_ids = ids if body["selected_trial_ids"] is None else body["selected_trial_ids"]
            if len(set(selected_ids)) != len(selected_ids) or not set(selected_ids) <= set(ids):
                raise ServiceError(422, "INVALID_TRIAL_SELECTION", "Selection must name distinct trials from this fixed case.")
            selected = set(selected_ids)
            history_bytes = sum((self.root / "results" / t["run_id"] / "result.json").stat().st_size
                                for t in case["trials"] if t["trial_id"] in selected and t["result_available"])
            omit_history, omitted_count, items = history_bytes > MAX_HISTORY_BYTES, 0, []
            for t in case["trials"]:
                result = self.trial_result(body["snapshot_id"], t["trial_id"])["result"] if t["trial_id"] in selected and t["result_available"] else None
                if omit_history and result is not None:
                    omitted_count += int(bool(result["records"]))
                    result = {**result, "records": []}
                items.append({"trial_id": t["trial_id"], "result": result})
            from balloon_sim.ensemble.statistics import analyze_results
            try:
                analysis = analyze_results(items, selected_trial_ids=body["selected_trial_ids"])
                self._history_limit(analysis, history_bytes, omitted_count, omit_history)
            except (ValueError, FlightError) as exc:
                raise ServiceError(422, getattr(exc, "code", "INVALID_TRIAL_SELECTION"), str(exc)) from exc
            classifier = None
            if body["selection_origin"] == "frontend-region-classifier":
                if body["region_set"] is None or not body["classifier_version"]:
                    raise ServiceError(422, "CLASSIFIER_PROVENANCE_REQUIRED", "Region selection needs fixed region data and a classifier version.")
                from backend.worker import REPO_ROOT
                classifier = {"declared_version": body["classifier_version"],
                              "files": {p: file_hash(REPO_ROOT / p) for p in CLASSIFIER_PATHS}}
                classifier["fingerprint"] = digest(classifier)
            self.app._assert_source_current()
            aid = identity()
            selected = analysis["selected_trial_ids"]
            selected_rows = [t for t in case["trials"] if t["trial_id"] in set(selected)]
            if classifier and any(t["state"] != "landed" for t in selected_rows):
                raise ServiceError(422, "REGION_SELECTION_NOT_LANDED", "Landing-region groups may only contain landed trials; incomplete trials remain in the case denominator.")
            doc = {"schema": "balloon.ensemble.analysis-artifact/1", "analysis_id": aid,
                   "snapshot_id": body["snapshot_id"], "ensemble_id": case["ensemble_id"], "case_id": body["case_id"],
                   "created_at": utc_now(), "selected_trial_ids": selected, "counts": counts(selected_rows),
                   "source_snapshot": copy.deepcopy(self.app._snapshot), "analysis": analysis,
                   "region_set": body["region_set"], "region_set_hash": digest(body["region_set"]),
                   "selection_origin": body["selection_origin"], "classifier_snapshot": classifier,
                   "classification_verified_by_server": False,
                   "groups": [{"group_id": "selected", "trial_ids": selected, "landed_denominator": case["counts"]["landed"],
                               "hit_count": len(selected_rows), "weight": len(selected_rows)}] if classifier else [],
                   "limits": ["Server verifies fixed trial identity and statistics, not equivalence between client region classification and selected IDs."]}
            hashed = storage.publish(self.root, aid, doc)
            with self.db:
                self.db.execute("INSERT INTO ensemble_analyses VALUES (?,?,?,?,?,?,?)",
                                (aid, body["client_request_id"], request_hash, body["snapshot_id"], body["case_id"], hashed, utc_now()))
            return doc

    def analysis(self, aid):
        with self.app._guard:
            return self._artifact("ensemble_analyses", aid)

    @staticmethod
    def _history_limit(analysis, result_bytes, omitted_count, omitted):
        analysis["history"].update({"unavailable_reason": "HISTORY_ANALYSIS_BYTE_LIMIT" if omitted else None,
                                    "omitted_count": omitted_count, "result_bytes": result_bytes,
                                    "byte_limit": MAX_HISTORY_BYTES,
                                    "available_history_count": analysis["history_count"] + omitted_count})
