"""Offline lifecycle counterexamples; physical examples use the actual saved field."""
import copy
import json
import time
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.application import ApplicationService, ServiceError
from backend.storage import canonical, publish_result, utc_now
from backend.worker import execute_run
from balloon_sim.environment.fields import _utc


def paused(path):
    service = ApplicationService(path)
    service._dispatch = lambda: service._stop.wait()
    return service


def request(service, key="plan", n=2, delays=False):
    source = service.weather_sources()["sources"][0]
    config = copy.deepcopy(source["default_config"])
    config["burst"]["altitude_m"] = 500.0
    config["integration"]["max_duration_s"] = 1200.0
    case = {"case_id": "A", "candidate_id": "A", "candidate_revision": 2, "label": "A",
            "config": config}
    cases = [case]
    if delays:
        child = copy.deepcopy(case)
        child.update(case_id="A30", candidate_id="A30", label="A +30 min", parent_case_id="A", delay_minutes=30.0)
        child["config"]["launch"]["time_utc"] = (_utc(config["launch"]["time_utc"])+timedelta(minutes=30)).isoformat()
        cases.append(child)
    return {"client_request_id": key, "label": "Explicit sensitivity", "weather_source_id": source["id"],
            "sampling": {"variable": "gas_mass_kg", "unit": "kg", "distribution": {"family": "uniform", "low": .45, "high": .55},
                         "reason": "Offline sensitivity assumption, not measured variability", "seed": 72, "n": n}, "cases": cases}


def submit(service, body):
    plan = service.ensemble.plan(body)
    assert plan["status"] == "ready", plan["blockers"]
    job = service.ensemble.submit({"client_request_id": body["client_request_id"]+"-execute", "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"]})
    return plan, job


def execute_one(service, *, lose_registry=False):
    """Exercise the real n=1 worker/output barrier with deterministic dispatch timing."""
    with service._guard:
        service.ensemble.tick()
        row = service._db.execute("SELECT r.id,r.spec FROM runs r JOIN jobs j ON r.id=j.run_id WHERE j.state='queued' LIMIT 1").fetchone()
        assert row
        run_id, spec = row["id"], json.loads(row["spec"])
        with service._db:
            service._db.execute("UPDATE jobs SET state='running' WHERE run_id=?", (run_id,))
            service.ensemble.mark_running(run_id)
    source = service._sources[spec["weather_snapshot"]["id"]]
    execute_run(spec, str(source["path"]), str(service.data_dir/"specs"/run_id/"config.json"), str(service.data_dir/"staging"/run_id))
    relative, hashed = publish_result(service.data_dir, run_id, spec)
    with service._guard, service._db:
        if lose_registry:
            service._db.execute("UPDATE jobs SET state='failed',error=? WHERE run_id=?", (canonical({"code": "INJECTED_DB_FAILURE"}), run_id))
        else:
            service._db.execute("UPDATE runs SET result_path=?,manifest_hash=? WHERE id=?", (relative, hashed, run_id))
            service._db.execute("UPDATE jobs SET state='completed' WHERE run_id=?", (run_id,))
    return run_id


def settle(service, eid):
    for _ in range(260):
        with service._guard:
            service.ensemble.tick()
        current = service.ensemble.get(eid)
        if current["state"] not in {"queued", "running", "cancelling"}:
            assert current["latest_snapshot_id"], current
            return current
        execute_one(service)
    pytest.fail("finite ensemble did not settle")


def test_plan_pairs_exact_values_preserves_input_and_rejects_inactive_quantity(tmp_path):
    with paused(tmp_path) as service:
        body = request(service, delays=True)
        original = copy.deepcopy(body)
        plan = service.ensemble.plan(body)
        assert body == original
        assert plan["trial_count"] == 4 and plan["resolver_version"] == "flight-primitive/1"
        assert [t["value"] for t in plan["trials"][:2]] == [t["value"] for t in plan["trials"][2:]]
        assert plan["drawset"]["draws"][0]["draw_id"] == plan["trials"][0]["draw_id"]
        assert not service.list_runs()["runs"]
        assert service.ensemble.plan(body) == plan
        body["client_request_id"] = "inactive"
        body["cases"][0]["config"]["ascent"] = {"mode": "constant_speed", "speed_m_s": 5.0}
        with pytest.raises(ServiceError) as caught:
            service.ensemble.plan(body)
        assert caught.value.code == "ENSEMBLE_VARIABLE_UNSUPPORTED"


@pytest.mark.parametrize("change,code", [("unit", "ENSEMBLE_UNIT"), ("cap", "ENSEMBLE_LIMIT"),
    ("delay", "DELAY_TIME_MISMATCH"), ("model", "DELAY_INPUT_MISMATCH")])
def test_plan_rejects_unsupported_pairings_without_partial_jobs(tmp_path, change, code):
    with paused(tmp_path) as service:
        body = request(service, delays=True)
        if change == "unit": body["sampling"]["unit"] = "m"
        if change == "cap": body["sampling"]["n"] = 256
        if change == "delay": body["cases"][1]["delay_minutes"] = 45.0
        if change == "model": body["cases"][1]["config"]["ascent"]["drag_coefficient"] = .6
        with pytest.raises(ServiceError) as caught: service.ensemble.plan(body)
        assert caught.value.code == code
        assert service.ensemble.list()["ensembles"] == [] and service.list_runs(True)["runs"] == []


def test_full_window_and_invalid_draws_stay_distinct(tmp_path):
    with paused(tmp_path) as service:
        body = request(service, n=6)
        body["sampling"]["distribution"].update(low=-.5, high=.5)
        plan, job = submit(service, body)
        assert 0 < plan["invalid_trial_count"] < 6
        assert job["counts"]["planned"] == 6
        assert job["counts"]["invalid_input"] == plan["invalid_trial_count"]
        body["client_request_id"] = "bad-window"
        body["cases"][0]["config"]["launch"]["time_utc"] = "2030-01-01T00:00:00+00:00"
        plan2 = service.ensemble.plan(body)
        assert plan2["status"] == "unavailable" and plan2["blockers"][0]["code"] == "WEATHER_WINDOW_UNSUPPORTED"
        with pytest.raises(ServiceError):
            service.ensemble.submit({"client_request_id": "bad-submit", "plan_id": plan2["plan_id"], "plan_hash": plan2["plan_hash"]})


def test_queue_feeder_uses_existing_pool_and_hides_attempts_from_n1_list(tmp_path):
    with paused(tmp_path) as service:
        _, job = submit(service, request(service, n=8))
        with service._guard:
            service.ensemble.tick(); service.ensemble.tick()
        assert len(service.list_runs(True)["runs"]) == 1
        assert service.list_runs()["runs"] == []
        run = service.list_runs(True)["runs"][0]
        assert run["kind"] == "ensemble_trial" and run["ensemble"]["ensemble_id"] == job["ensemble_id"]
        assert service.ensemble.get(job["ensemble_id"])["counts"]["unstarted"] == 7
        body = request(service)["cases"][0]
        direct = service.submit({"client_request_id": "direct", "candidate_id": "direct", "candidate_revision": 0,
                                 "label": "direct", "weather_source_id": "wakayama-gfs-fixture", "config": body["config"]})
        assert [r["run_id"] for r in service.list_runs()["runs"]] == [direct["run_id"]]


def test_physical_results_group_analysis_and_fixed_comparison_survive_reopen(tmp_path):
    with paused(tmp_path) as service:
        plan, job = submit(service, request(service, delays=True))
        ended = settle(service, job["ensemble_id"])
        sid = ended["latest_snapshot_id"]
        case = service.ensemble.case_result(sid, "A")
        assert case["counts"]["landed"] == case["counts"]["planned"] == 2
        assert [b["probability"] for b in case["overview_analysis"]["landing"]["bands"]] == [.5, .9, .95]
        raw = service.ensemble.trial_result(sid, case["trials"][0]["trial_id"])
        assert raw["kind"] == "ensemble_trial" and raw["result"]["records"]
        region = {"type": "FeatureCollection", "features": []}
        selection = {"client_request_id": "selection", "snapshot_id": sid, "case_id": "A",
                     "selected_trial_ids": [case["trials"][0]["trial_id"]], "region_set": region,
                     "selection_origin": "frontend-region-classifier", "classifier_version": "math.js/0.48"}
        analysis = service.ensemble.analyze(selection)
        assert analysis["classification_verified_by_server"] is False
        assert analysis["groups"][0]["hit_count"] == 1 and analysis["groups"][0]["landed_denominator"] == 2
        assert analysis["analysis"]["landing"]["extent"]["type"] == "Point"
        saved = service.save_project({"expected_revision": 0, "project": {"title": "paired", "candidates": [], "compare_run_ids": [],
                     "compare_results": [{"kind": "ensemble_case", "ensemble_id": job["ensemble_id"], "snapshot_id": sid,
                                          "case_id": "A", "analysis_id": analysis["analysis_id"]}]}})
    with paused(tmp_path) as service:
        assert service.get_project() == saved
        assert service.ensemble.case_result(sid, "A") == case
        assert service.ensemble.trial_result(sid, case["trials"][0]["trial_id"]) == raw
        assert service.ensemble.analysis(analysis["analysis_id"]) == analysis
        assert service.list_runs()["runs"] == []


def test_cancel_retry_keeps_old_snapshot_and_retry_idempotency_precedes_source_guard(tmp_path, monkeypatch):
    with paused(tmp_path) as service:
        _, job = submit(service, request(service))
        cancelled = service.ensemble.cancel(job["ensemble_id"], {"client_request_id": "cancel1"})
        old = service.ensemble.snapshot(service.ensemble.get(job["ensemble_id"])["latest_snapshot_id"])
        assert old["counts"]["cancelled"] == 2
        tid = old["cases"][0]["trials"][0]["trial_id"]
        body = {"client_request_id": "retry1", "trial_ids": [tid]}
        accepted = service.ensemble.retry(job["ensemble_id"], body)
        assert accepted["epoch"] == 2 and accepted["counts"]["cancelled"] == 1
        assert service.ensemble.cancel(job["ensemble_id"], {"client_request_id": "cancel1"}) == cancelled
        assert service.ensemble.get(job["ensemble_id"])["state"] == "queued"
        ended = settle(service, job["ensemble_id"])
        assert service.ensemble.snapshot(old["snapshot_id"]) == old
        assert ended["counts"]["landed"] == 1 and ended["counts"]["cancelled"] == 1
        def changed(): raise ServiceError(409, "SOURCE_CHANGED", "injected drift")
        monkeypatch.setattr(service, "_assert_source_current", changed)
        assert service.ensemble.retry(job["ensemble_id"], body) == accepted
        assert service.ensemble.snapshot(old["snapshot_id"]) == old
        with pytest.raises(ServiceError) as drift:
            service.ensemble.retry(job["ensemble_id"], {"client_request_id": "retry2", "trial_ids": [old["cases"][0]["trials"][1]["trial_id"]]})
        assert drift.value.code == "SOURCE_CHANGED"


def test_same_process_renamed_result_is_recovered_before_retry(tmp_path):
    with paused(tmp_path) as service:
        _, job = submit(service, request(service, n=1))
        run = execute_one(service, lose_registry=True)
        with service._db:
            service._db.execute("UPDATE ensembles SET state='failed' WHERE id=?", (job["ensemble_id"],))
            service._db.execute("UPDATE ensemble_trials SET state='failed' WHERE run_id=?", (run,))
        tid = service.ensemble.trials(job["ensemble_id"])["trials"][0]["trial_id"]
        with pytest.raises(ServiceError) as recovered:
            service.ensemble.retry(job["ensemble_id"], {"client_request_id": "retry", "trial_ids": [tid]})
        assert recovered.value.code == "TRIAL_NOT_RETRYABLE"
        assert service.get_run(run)["state"] == "completed"
        assert service._db.execute("SELECT count(*) FROM ensemble_attempts").fetchone()[0] == 1
        finished = service.ensemble.retry(job["ensemble_id"], {"client_request_id": "finalize", "trial_ids": []})
        assert finished["latest_snapshot_id"]


def test_restart_retains_unstarted_denominator_and_completed_old_source_is_readable(tmp_path):
    with paused(tmp_path) as service:
        _, job = submit(service, request(service))
        run = execute_one(service, lose_registry=True)
    with paused(tmp_path) as service:
        current = service.ensemble.get(job["ensemble_id"])
        assert current["state"] == "interrupted"
        case = service.ensemble.case_result(current["latest_snapshot_id"], "A")
        assert case["counts"]["landed"] == 1 and case["counts"]["unstarted"] == 1
        assert case["overview_analysis"]["selected_count"] == 2
        assert service.get_result(run)["result"]["status"] == "landed"


def test_corrupt_renamed_result_blocks_retry_instead_of_duplicate_execution(tmp_path):
    with paused(tmp_path) as service:
        _, job = submit(service, request(service, n=1))
        run = execute_one(service, lose_registry=True)
        (tmp_path / "results" / run / "result.json").write_text("{}", encoding="utf-8")
        with service._db:
            service._db.execute("UPDATE ensembles SET state='failed' WHERE id=?", (job["ensemble_id"],))
        tid = service.ensemble.trials(job["ensemble_id"])["trials"][0]["trial_id"]
        with pytest.raises(ServiceError) as corrupt:
            service.ensemble.retry(job["ensemble_id"], {"client_request_id": "retry", "trial_ids": [tid]})
        assert corrupt.value.code == "RESULT_RECOVERY_REQUIRED"
        assert service._db.execute("SELECT count(*) FROM ensemble_attempts").fetchone()[0] == 1


def test_inactive_epoch_snapshot_recovery_does_not_require_current_code(tmp_path, monkeypatch):
    with paused(tmp_path) as service:
        _, job = submit(service, request(service, n=1))
        run = execute_one(service, lose_registry=True)
        old_source = copy.deepcopy(service._snapshot)
    import backend.application as module
    new_source = copy.deepcopy(old_source)
    new_source["fingerprint"] = "changed-environment-for-offline-test"
    monkeypatch.setattr(module, "source_snapshot", lambda: copy.deepcopy(new_source))
    with paused(tmp_path) as service:
        current = service.ensemble.get(job["ensemble_id"])
        case = service.ensemble.case_result(current["latest_snapshot_id"], "A")
        assert case["counts"]["landed"] == 1 and case["source_snapshot"] == old_source
        assert case["overview_analysis"] is None and case["warnings"][0]["code"] == "ANALYSIS_SOURCE_CHANGED"
        assert service.get_result(run)["result"]["status"] == "landed"


def test_running_cancel_retains_physical_result_and_cancels_remaining_rows(tmp_path):
    with paused(tmp_path) as service:
        _, job = submit(service, request(service, n=2))
        with service._guard:
            service.ensemble.tick()
            run = service.list_runs(True)["runs"][0]["run_id"]
            with service._db:
                service._db.execute("UPDATE jobs SET state='running' WHERE run_id=?", (run,))
                service.ensemble.mark_running(run)
        accepted = service.ensemble.cancel(job["ensemble_id"], {"client_request_id": "cancel-running"})
        assert accepted["state"] == "cancelling" and accepted["counts"]["running"] == 1
        spec = service.get_run(run)["spec"]
        source = service._sources[spec["weather_snapshot"]["id"]]
        execute_run(spec, str(source["path"]), str(tmp_path/"specs"/run/"config.json"), str(tmp_path/"staging"/run))
        path, hashed = publish_result(tmp_path, run, spec)
        with service._db:
            service._db.execute("UPDATE runs SET result_path=?,manifest_hash=? WHERE id=?", (path, hashed, run))
            service._db.execute("UPDATE jobs SET state='completed' WHERE run_id=?", (run,))
        with service._guard: service.ensemble.tick()
        result = service.ensemble.get(job["ensemble_id"])
        assert result["state"] == "cancelled" and result["counts"]["landed"] == result["counts"]["cancelled"] == 1


def test_disappeared_weather_blocks_new_work_but_not_saved_result(tmp_path):
    with paused(tmp_path) as service:
        plan, job = submit(service, request(service))
        run = execute_one(service)
        service.ensemble.cancel(job["ensemble_id"], {"client_request_id": "cancel-rest"})
        current = service.ensemble.get(job["ensemble_id"])
        case = service.ensemble.case_result(current["latest_snapshot_id"], "A")
        pending = next(t["trial_id"] for t in case["trials"] if t["state"] == "cancelled")
        old_result = service.get_result(run)
        service._sources[plan["weather_snapshot"]["id"]]["path"] = tmp_path / "unavailable-weather.json.gz"
        for action in (lambda: service.ensemble.retry(job["ensemble_id"], {"client_request_id": "retry-missing", "trial_ids": [pending]}),
                       lambda: service.ensemble.plan(request(service, key="new-plan"))):
            with pytest.raises(ServiceError) as missing: action()
            assert missing.value.status == 409 and missing.value.code == "ENSEMBLE_WEATHER_CHANGED"
        assert service.get_result(run) == old_result
        assert service.ensemble.case_result(case["snapshot_id"], "A") == case
        assert service.ensemble.get_plan(plan["plan_id"]) == plan


def test_capacity_and_bad_selection_leave_current_ledger_unchanged(tmp_path):
    with paused(tmp_path) as service:
        jobs = [submit(service, request(service, key=f"p{i}", n=1))[1] for i in range(4)]
        plan = service.ensemble.plan(request(service, key="fifth", n=1))
        with pytest.raises(ServiceError) as capacity:
            service.ensemble.submit({"client_request_id": "fifth-execute", "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"]})
        assert capacity.value.code == "ENSEMBLE_QUEUE_FULL"
        service.ensemble.cancel(jobs[0]["ensemble_id"], {"client_request_id": "cancel-first"})
        case = service.ensemble.case_result(service.ensemble.get(jobs[0]["ensemble_id"])["latest_snapshot_id"], "A")
        selected = case["trials"][0]["trial_id"]
        for ids in ([selected, selected], ["unknown"]):
            with pytest.raises(ServiceError) as invalid:
                service.ensemble.analyze({"client_request_id": "bad-group", "snapshot_id": case["snapshot_id"], "case_id": "A", "selected_trial_ids": ids})
            assert invalid.value.code == "INVALID_TRIAL_SELECTION"
        with pytest.raises(ServiceError) as not_landed:
            service.ensemble.analyze({"client_request_id": "nonlanding-group", "snapshot_id": case["snapshot_id"], "case_id": "A", "selected_trial_ids": [selected],
                                      "selection_origin": "frontend-region-classifier", "classifier_version": "test", "region_set": {}})
        assert not_landed.value.code == "REGION_SELECTION_NOT_LANDED"
        assert service.ensemble.case_result(case["snapshot_id"], "A") == case


def test_physical_zero_record_stop_is_not_failure_or_retryable(tmp_path):
    with paused(tmp_path) as service:
        body = request(service, n=1)
        body["sampling"]["distribution"].update(low=.0001, high=.0002)
        _, job = submit(service, body)
        ended = settle(service, job["ensemble_id"])
        case = service.ensemble.case_result(ended["latest_snapshot_id"], "A")
        trial = case["trials"][0]
        assert trial["state"] == "stopped" and trial["last_valid_point"] is None and trial["landing"] is None
        assert case["overview_analysis"]["completed_count"] == 1 and case["overview_analysis"]["history_count"] == 0
        assert case["overview_analysis"]["history"]["unavailable_reason"] is None
        with pytest.raises(ServiceError) as blocked:
            service.ensemble.retry(job["ensemble_id"], {"client_request_id": "invalid-retry", "trial_ids": [trial["trial_id"]]})
        assert blocked.value.code == "TRIAL_NOT_RETRYABLE"


def test_history_byte_limit_preserves_landing_and_original_records(tmp_path, monkeypatch):
    import backend.ensemble.service as module
    with paused(tmp_path) as service:
        _, job = submit(service, request(service, n=2))
        monkeypatch.setattr(module, "MAX_HISTORY_BYTES", 1)
        ended = settle(service, job["ensemble_id"])
        case = service.ensemble.case_result(ended["latest_snapshot_id"], "A")
        stats = case["overview_analysis"]
        assert stats["landing"]["n"] == 2 and stats["landing"]["bands"]
        assert stats["history"]["unavailable_reason"] == "HISTORY_ANALYSIS_BYTE_LIMIT"
        assert stats["history"]["omitted_count"] == 2
        original = service.ensemble.trial_result(case["snapshot_id"], case["trials"][0]["trial_id"])
        assert original["result"]["records"]
        monkeypatch.setattr(module, "MAX_HISTORY_BYTES", 64*1024*1024)
        analysis = service.ensemble.analyze({"client_request_id": "subset", "snapshot_id": case["snapshot_id"], "case_id": "A",
                                             "selected_trial_ids": [case["trials"][0]["trial_id"]]})
        assert analysis["analysis"]["history"]["unavailable_reason"] is None
        assert analysis["analysis"]["history_count"] == 1


def test_api_incomplete_sampling_draft_and_empty_group_survive(tmp_path):
    app = create_app(tmp_path)
    app.state.service._dispatch = lambda: app.state.service._stop.wait()
    with TestClient(app) as client:
        assert client.get("/api/v1/ensemble-capabilities").json()["max_trials_per_ensemble"] == 256
        body = request(app.state.service, n=1)
        plan = client.post("/api/v1/ensemble-plans", json=body).json()
        job = client.post("/api/v1/ensembles", json={"client_request_id": "execute", "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"]}).json()
        ended = client.post(f"/api/v1/ensembles/{job['ensemble_id']}/cancel", json={"client_request_id": "cancel"}).json()
        ended = client.get(f"/api/v1/ensembles/{job['ensemble_id']}").json()
        aid = client.post("/api/v1/ensemble-analyses", json={"client_request_id": "empty", "snapshot_id": ended["latest_snapshot_id"], "case_id": "A", "selected_trial_ids": []}).json()
        assert aid["analysis"]["selected_count"] == 0 and aid["analysis"]["landing"]["n"] == 0
        assert client.get(f"/api/v1/ensembles/{job['ensemble_id']}/trials?offset=-1").status_code == 422
        draft = {"expected_revision": 0, "project": {"title": "draft", "compare_run_ids": [], "candidates": [
                 {"id": "A", "label": "A", "revision": 2, "weather_source_id": "draft", "config": {}, "sampling": {"distribution": {"low": ""}}}]}}
        assert client.put("/api/v1/project", json=draft).json()["project"]["candidates"][0]["sampling"] == {"distribution": {"low": ""}}


def test_real_process_dispatch_settles_ensemble_with_one_existing_worker(tmp_path):
    with ApplicationService(tmp_path) as service:
        _, job = submit(service, request(service, n=1))
        deadline = time.monotonic()+60
        while time.monotonic() < deadline:
            current = service.ensemble.get(job["ensemble_id"])
            if current["state"] not in {"queued", "running", "cancelling"}: break
            time.sleep(.05)
        assert current["state"] == "completed", current
        assert current["counts"]["landed"] == 1
        assert service.ensemble.case_result(current["latest_snapshot_id"], "A")["overview_analysis"]["history_count"] == 1
