"""Finite operational faults: no provider traffic, live-state edits or model changes."""
import copy
from concurrent.futures import Future
from concurrent.futures.process import BrokenProcessPool
import json
import sqlite3
import time
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.application import ApplicationService, ServiceError
from backend.storage import canonical, file_hash, open_registry, publish_result, registry_instance_id
from backend.tests.test_application import paused_service, request_for, wait_finished
from backend.worker import execute_run


def small_request(service, key="unknown/受付 #1"):
    body = request_for(service.weather_sources()["sources"][0], key)
    body["config"]["integration"]["max_duration_s"] = 10.0
    return body


def output_without_registry(service, run_id, *, publish=True):
    spec = service.get_run(run_id)["spec"]
    source = service._sources[spec["weather_snapshot"]["id"]]
    execute_run(spec, str(source["path"]), str(service.data_dir / "specs" / run_id / "config.json"),
                str(service.data_dir / "staging" / run_id))
    if publish:
        publish_result(service.data_dir, run_id, spec)
    return spec


@pytest.mark.parametrize("previous_state", ["running", "failed"])
def test_single_completed_rename_recovers_without_current_source(tmp_path, monkeypatch, previous_state):
    with paused_service(tmp_path) as service:
        body = small_request(service)
        run_id = service.submit(body)["run_id"]
        spec = output_without_registry(service, run_id)
        marker = file_hash(tmp_path / "results" / run_id / "COMMITTED.json")
        with service._db:
            service._db.execute("UPDATE jobs SET state=?,error=? WHERE run_id=?",
                                (previous_state, canonical({"code": "INJECTED_LOST_REGISTRY"}), run_id))
        old_source = copy.deepcopy(service._snapshot)
    import backend.application as module
    changed = copy.deepcopy(old_source)
    changed["fingerprint"] = "different-current-code-for-read-only-recovery"
    monkeypatch.setattr(module, "source_snapshot", lambda: copy.deepcopy(changed))
    reopened = paused_service(tmp_path)
    reopened._load_sources = lambda: None
    with reopened:
        detail = reopened.get_run_request(body["client_request_id"])
        result = reopened.get_result(run_id)
        assert detail["state"] == "completed" and detail["spec"] == spec
        assert result["source_snapshot"] == old_source
        assert detail["recovery"][0]["previous_state"] == previous_state
        assert detail["recovery"][0]["previous_error"]["code"] == "INJECTED_LOST_REGISTRY"
        assert detail["recovery"][0]["recomputed"] is False
        assert reopened.submit(body)["run_id"] == run_id
        assert len(reopened.list_runs()["runs"]) == 1
        assert file_hash(tmp_path / "results" / run_id / "COMMITTED.json") == marker
    with paused_service(tmp_path) as again:
        assert again.get_run(run_id)["recovery"] == detail["recovery"]
        assert again.get_result(run_id) == result


@pytest.mark.parametrize("damage", ["output", "manifest", "identity", "marker_type", "kernel_type", "result_type"])
def test_recovery_refuses_damaged_or_different_complete_output(tmp_path, damage):
    with paused_service(tmp_path) as service:
        run_id = service.submit(small_request(service))["run_id"]
        output_without_registry(service, run_id)
        folder = tmp_path / "results" / run_id
        if damage == "marker_type":
            (folder / "COMMITTED.json").write_text("[]", encoding="utf-8")
        elif damage == "output":
            (folder / "report.html").write_text("damaged", encoding="utf-8")
        else:
            marker = json.loads((folder / "COMMITTED.json").read_text(encoding="utf-8"))
            if damage == "manifest":
                del marker["files"]["manifest.json"]
            elif damage == "identity":
                saved = json.loads((folder / "run.json").read_text(encoding="utf-8"))
                saved["submitted_input"]["label"] = "different-original-intent"
                (folder / "run.json").write_text(canonical(saved), encoding="utf-8")
                marker["files"]["run.json"] = {"bytes": (folder / "run.json").stat().st_size,
                                                "sha256": file_hash(folder / "run.json")}
            else:
                name = "manifest.json" if damage == "kernel_type" else "result.json"
                (folder / name).write_text("[]", encoding="utf-8")
                marker["files"][name] = {"bytes": (folder / name).stat().st_size,
                                           "sha256": file_hash(folder / name)}
                if damage == "result_type":
                    # Keep both manifests consistent, so result-type validation
                    # is exercised after successful whole-artifact hashing.
                    kernel = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
                    kernel["files"][name] = marker["files"][name]
                    (folder / "manifest.json").write_text(canonical(kernel), encoding="utf-8")
                    marker["files"]["manifest.json"] = {"bytes": (folder / "manifest.json").stat().st_size,
                                                         "sha256": file_hash(folder / "manifest.json")}
            (folder / "COMMITTED.json").write_text(canonical(marker), encoding="utf-8")
    with paused_service(tmp_path) as reopened:
        detail = reopened.get_run(run_id)
        assert detail["state"] == "failed" and detail["error"]["code"] == "RESULT_RECOVERY_FAILED"
        assert detail["recovery"][0]["outcome"] == "rejected"
        with pytest.raises(ServiceError) as missing:
            reopened.get_result(run_id)
        assert missing.value.code == "RESULT_NOT_AVAILABLE"
        assert len(reopened.list_runs()["runs"]) == 1


def test_startup_loads_explicit_historical_catalog_and_keeps_saved_results(tmp_path, monkeypatch):
    from backend.worker import REPO_ROOT
    state = tmp_path / "state"
    with paused_service(state) as service:
        run_id = service.submit(small_request(service))["run_id"]
        output_without_registry(service, run_id)
    source = REPO_ROOT / "references/flight_fixture/jra3q-weather.json.gz"
    catalog = tmp_path / "catalog.json"
    entry = {"id": "historical-recovery-test", "label": "Explicit original field", "path": str(source), "sha256": file_hash(source)}
    catalog.write_text(json.dumps({"schema": "balloon.historical-catalog/1", "sources": [entry]}), encoding="utf-8")
    monkeypatch.setenv("BALLOON_HISTORICAL_CATALOG", str(catalog))
    with paused_service(state) as service:
        assert entry["id"] in {s["id"] for s in service.weather_sources()["sources"]}
        result = service.get_result(run_id)
    catalog.write_text("[]", encoding="utf-8")
    with paused_service(state) as service:
        assert service.get_result(run_id) == result
        assert entry["id"] not in {s["id"] for s in service.weather_sources()["sources"]}
        assert any(e["id"] == "historical-catalog" for e in service.weather_sources()["source_errors"])


def test_second_historical_asset_change_stops_fixed_plan_without_redrawing(tmp_path):
    from backend.tests.test_historical_ensemble import request
    with paused_service(tmp_path) as service:
        body = request(service)
        source_id = body["windows"][1]["weather_source_id"]
        second = copy.deepcopy(service._sources[source_id])
        second["path"] = tmp_path / "second-weather.json.gz"
        second["path"].write_bytes(service._sources[source_id]["path"].read_bytes())
        second["snapshot"]["id"] = "historical-independent-second"
        service._sources[second["snapshot"]["id"]] = second
        body["windows"][1]["weather_source_id"] = second["snapshot"]["id"]
        plan = service.ensemble.plan(body)
        start = {"client_request_id": "fixed-history-start", "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"]}
        accepted = service.ensemble.submit(start)
        second["path"].write_bytes(b"changed-after-acceptance")
        service.ensemble.tick()
        observed = service.ensemble.get(accepted["ensemble_id"])
        assert observed["state"] == "interrupted" and not service.list_runs()["runs"]
        assert observed["error"]["code"] == "ENSEMBLE_WEATHER_CHANGED"
        # An old receipt remains observable; it is not a new source resolution.
        assert service.ensemble.plan(body) == plan
        assert service.ensemble.submit(start)["ensemble_id"] == accepted["ensemble_id"]
        with pytest.raises(ServiceError) as rejected:
            service.ensemble.submit({**start, "client_request_id": "new-history-start"})
        assert rejected.value.code == "ENSEMBLE_WEATHER_CHANGED"


def test_staging_is_not_recovered_as_completed(tmp_path):
    with paused_service(tmp_path) as service:
        body = small_request(service)
        run_id = service.submit(body)["run_id"]
        output_without_registry(service, run_id, publish=False)
    with paused_service(tmp_path) as reopened:
        detail = reopened.get_run_request(body["client_request_id"])
        assert detail["state"] == "interrupted" and not detail["result_available"]
        assert detail["recovery"] == []
        assert reopened.submit(body)["run_id"] == run_id
        assert len(reopened.list_runs()["runs"]) == 1


def test_same_process_publish_exception_recovers_completed_output(tmp_path, monkeypatch):
    import backend.application as module
    original = module.publish_result
    def after_rename(*args):
        original(*args)
        raise OSError("injected exception after completed rename")
    monkeypatch.setattr(module, "publish_result", after_rename)
    with ApplicationService(tmp_path) as service:
        run_id = service.submit(small_request(service))["run_id"]
        # The intermediate failed state is followed by verification, not a rerun.
        deadline = time.monotonic() + 30
        while service.get_run(run_id)["state"] != "completed" and time.monotonic() < deadline:
            time.sleep(.02)
        detail = service.get_run(run_id)
        assert detail["state"] == "completed"
        assert detail["recovery"][0]["previous_error"]["code"] == "EXECUTION_FAILED"
        assert detail["recovery"][0]["recomputed"] is False
        assert service.get_result(run_id)["result"]["status"] == "stopped"
        assert len(service.list_runs()["runs"]) == 1


class BrokenExecutor:
    def __init__(self):
        self.submissions = 0
    def submit(self, *args):
        self.submissions += 1
        f = Future()
        f.set_exception(BrokenProcessPool("injected worker exit"))
        return f
    def shutdown(self, **kwargs):
        pass


def test_broken_pool_preserves_next_run_and_read_requests(tmp_path):
    service = ApplicationService(tmp_path)
    original_dispatch = service._dispatch
    gate = __import__("threading").Event()
    service._dispatch = lambda: (gate.wait(10), original_dispatch())
    with service:
        first = small_request(service, "first")
        second = small_request(service, "second")
        one, two = service.submit(first), service.submit(second)
        service._executor.shutdown(wait=True)
        broken = service._executor = BrokenExecutor()
        gate.set()
        failed = wait_finished(service, one["run_id"])
        assert failed["state"] == "failed" and failed["error"]["code"] == "WORKER_PROCESS_BROKEN"
        # An explicit wake would normally dispatch another queued job.
        service._wake.set()
        time.sleep(.35)
        assert broken.submissions == 1
        assert service.get_run(two["run_id"])["state"] == "queued"
        status = service.execution_status()
        assert not status["available"] and status["restart_required"]
        assert service.get_run_request("first")["run_id"] == one["run_id"]
        assert service.submit(first)["run_id"] == one["run_id"]
        with pytest.raises(ServiceError) as rejected:
            service.submit(small_request(service, "new"))
        assert rejected.value.status == 503 and len(service.list_runs()["runs"]) == 2
        assert service.get_project()["revision"] == 0
    with paused_service(tmp_path) as reopened:
        assert reopened.execution_status()["available"]
        assert reopened.get_run(two["run_id"])["state"] == "interrupted"
        assert reopened.get_run(one["run_id"])["error"]["code"] == "WORKER_PROCESS_BROKEN"


def test_request_lookup_is_read_only_and_supports_non_path_ids(tmp_path, monkeypatch):
    app = create_app(tmp_path)
    app.state.service._dispatch = lambda: app.state.service._stop.wait()
    with TestClient(app) as client:
        service = app.state.service
        body = small_request(service)
        absent = client.get("/api/v1/run-requests", params={"client_request_id": body["client_request_id"]})
        assert absent.status_code == 404
        run = client.post("/api/v1/runs", json=body).json()
        def changed():
            raise AssertionError("read-only intent lookup touched current source")
        monkeypatch.setattr(service, "_assert_source_current", changed)
        observed = client.get("/api/v1/run-requests", params={"client_request_id": body["client_request_id"]})
        assert observed.status_code == 200
        assert observed.json()["run_id"] == run["run_id"]
        assert observed.json()["spec"]["submitted_input"] == body
        assert len(client.get("/api/v1/runs").json()["runs"]) == 1
        service._execution_error = {"code": "WORKER_PROCESS_BROKEN", "message": "injected"}
        health = client.get("/api/v1/health").json()
        assert health["status"] == "degraded" and not health["flight_execution"]["available"]
        assert client.post("/api/v1/runs", json=body).json()["run_id"] == run["run_id"]


def test_registry_identity_survives_restart_and_differs_between_state_dirs(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    db = open_registry(first)
    identity = registry_instance_id(db)
    assert str(uuid.UUID(identity)) == identity
    db.close()
    db = open_registry(first)
    assert registry_instance_id(db) == identity
    db.close()
    db = open_registry(second)
    assert registry_instance_id(db) != identity
    db.close()


def test_legacy_registry_migration_preserves_existing_project(tmp_path):
    db = open_registry(tmp_path)
    project = {"schema": "balloon.project/1", "title": "Existing project preserved", "candidates": [], "compare_run_ids": []}
    with db:
        db.execute("UPDATE projects SET revision=17,document=? WHERE id='default'", (canonical(project),))
        db.execute("DROP TABLE service_identity")  # A finite old-schema fixture.
    db.close()
    db = open_registry(tmp_path)
    identity = registry_instance_id(db)
    row = db.execute("SELECT revision,document FROM projects WHERE id='default'").fetchone()
    assert row["revision"] == 17 and json.loads(row["document"]) == project
    db.close()
    db = open_registry(tmp_path)
    assert registry_instance_id(db) == identity
    db.close()


@pytest.mark.parametrize("damage", ["missing", "malformed"])
def test_registry_identity_corruption_is_not_silently_rekeyed(tmp_path, damage):
    db = open_registry(tmp_path)
    with db:
        if damage == "missing": db.execute("DELETE FROM service_identity")
        else: db.execute("UPDATE service_identity SET instance_id='not-an-identity'")
    db.close()
    for _ in range(2):
        with pytest.raises(ValueError, match="identity"):
            open_registry(tmp_path)
    db = sqlite3.connect(tmp_path / "registry.sqlite3")
    rows = db.execute("SELECT instance_id FROM service_identity").fetchall()
    assert rows == ([] if damage == "missing" else [("not-an-identity",)])
    db.close()


def test_http_instance_guard_rejects_read_and_write_before_acceptance(tmp_path):
    app = create_app(tmp_path)
    app.state.service._dispatch = lambda: app.state.service._stop.wait()
    with TestClient(app) as client:
        identity = client.get("/api/v1/health").json()["instance_id"]
        good = {"X-Balloon-Instance-Id": identity}
        wrong = {"X-Balloon-Instance-Id": str(uuid.uuid4())}
        body = small_request(app.state.service)
        assert client.get("/api/v1/health", headers=wrong).json()["instance_id"] == identity
        for response in (client.get("/api/v1/project", headers=wrong),
                         client.get("/api/v1/run-requests", params={"client_request_id": body["client_request_id"]}, headers=wrong),
                         client.post("/api/v1/runs", json=body, headers=wrong),
                         client.put("/api/v1/project", json={"expected_revision": 0, "project": {}}, headers=wrong)):
            assert response.status_code == 409 and response.json()["error"]["code"] == "INSTANCE_MISMATCH"
        assert client.get("/api/v1/project", headers=good).json()["revision"] == 0
        assert not client.get("/api/v1/runs").json()["runs"]  # Header-free CLI read stays compatible.
        accepted = client.post("/api/v1/runs", json=body, headers=good)
        assert accepted.status_code == 202
        assert client.post("/api/v1/runs", json=body).json()["run_id"] == accepted.json()["run_id"]
    with TestClient(app) as reopened:
        assert reopened.get("/api/v1/health").json()["instance_id"] == identity
