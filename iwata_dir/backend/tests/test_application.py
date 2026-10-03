"""Offline acceptance boundaries, including the real Windows spawn worker."""
import copy
import json
import shutil
import time
import zlib

import pytest
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.application import ApplicationService, ServiceError
from balloon_sim.environment.storage import load_weather
from balloon_sim.flight.trajectory import simulate
from backend.worker import REPO_ROOT


def request_for(source, key="request-a"):
    return {"client_request_id": key, "candidate_id": key, "candidate_revision": 0,
            "label": key, "weather_source_id": source["id"], "config": copy.deepcopy(source["default_config"])}


def wait_finished(service, run_id, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        detail = service.get_run(run_id)
        if detail["state"] not in {"queued", "running"}:
            return detail
        time.sleep(0.05)
    pytest.fail("worker did not finish within the finite deadline")


def paused_service(path, max_queued=4):
    service = ApplicationService(path, max_queued=max_queued)
    # Hold dispatch to examine queued work deterministically, not a simulated kernel.
    service._dispatch = lambda: service._stop.wait()
    return service


def test_project_preserves_candidate_family_and_screen_context(tmp_path):
    """A real plan, its delays and weather exploration survive one save/reopen."""
    with ApplicationService(tmp_path) as service:
        source = service.weather_sources()["sources"][0]
        parent = {"id": "A", "label": "予定", "revision": 1,
                  "weather_source_id": source["id"], "config": source["default_config"]}
        children = [{**copy.deepcopy(parent), "id": f"A-{delay}",
                     "parent_id": "A", "delay_minutes": delay} for delay in (30, 60, 90)]
        project = {"schema": "balloon.project/1", "title": "延期と季節を読む",
                   "candidates": [parent, *children], "compare_run_ids": [],
                   "ui_state": {"schema": "balloon.ui/1",
                                "forecast_real": {"active": "A-60", "visible": ["A", "A-60"],
                                                  "center": [43.05, 141.35], "zoom": 9},
                                "weather_fixture": {"view": "annual", "years": [2020, 2025]}}}
        saved = service.save_project({"expected_revision": 0, "project": project})
        assert len(saved["project"]["candidates"]) == 4
        assert saved["project"]["ui_state"] == project["ui_state"]
        assert service.list_runs()["runs"] == []  # saving a delay never starts computation
    with ApplicationService(tmp_path) as reopened:
        assert reopened.get_project() == saved
        assert reopened.list_runs()["runs"] == []


@pytest.mark.parametrize("kind,code", [
    ("missing", "INVALID_DELAY_PARENT"), ("cycle", "CYCLIC_CANDIDATES"),
    ("unbound", "INVALID_DELAY_PARENT"), ("nonfinite", "INVALID_JSON"),
])
def test_invalid_screen_project_keeps_previous_saved_state(tmp_path, kind, code):
    with ApplicationService(tmp_path) as service:
        initial = service.get_project()
        project = copy.deepcopy(initial["project"])
        base = {"id": "A", "label": "A", "revision": 0, "weather_source_id": "draft", "config": {}}
        project["candidates"] = [base]
        if kind == "missing":
            base.update(parent_id="unknown", delay_minutes=30)
        elif kind == "cycle":
            base.update(parent_id="B", delay_minutes=30)
            project["candidates"].append({**base, "id": "B", "parent_id": "A"})
        elif kind == "unbound":
            base["delay_minutes"] = 30
        else:
            project["ui_state"] = {"forecast_real": {"zoom": float("nan")}}
        with pytest.raises(ServiceError) as error:
            service.save_project({"expected_revision": 0, "project": project})
        assert error.value.code == code
        assert service.get_project() == initial


def test_serves_scene_renderer_assets_without_masking_unknown_api(tmp_path, monkeypatch):
    import backend.app as app_module
    dist = tmp_path / "source" / "frontend" / "dist"
    for name, body in {"index.html": "<h1>Planning</h1>",
                       "scene3d/index.html": "<h1>Inspection</h1>",
                       "cesium/Workers/test.js": "self.onmessage = () => {};"}.items():
        path = dist / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    monkeypatch.setattr(app_module, "REPO_ROOT", tmp_path / "source")
    with TestClient(app_module.create_app(tmp_path / "state")) as client:
        assert "Planning" in client.get("/").text
        assert "Inspection" in client.get("/scene3d/index.html").text
        assert client.get("/cesium/Workers/test.js").status_code == 200
        assert client.get("/api/v1/unknown").status_code == 404
        assert client.get("/scene3d/missing.js").status_code == 404


def test_two_real_flights_draft_edit_and_reopen(tmp_path):
    with ApplicationService(tmp_path) as service:
        source = service.weather_sources()["sources"][0]
        a = request_for(source)
        b = request_for(source, "request-b")
        b["config"]["ascent"]["payload_mass_kg"] += 0.5
        ar = service.submit(a)
        br = service.submit(b)
        assert ar["run_id"] != br["run_id"]
        assert service.submit(a)["run_id"] == ar["run_id"]
        changed = copy.deepcopy(a)
        changed["config"]["ascent"]["payload_mass_kg"] = 3
        with pytest.raises(ServiceError) as conflict:
            service.submit(changed)
        assert conflict.value.status == 409
        draft = {"schema": "balloon.project/1", "title": "A/B", "candidates": [
            {"id": "request-a", "label": "edited draft", "revision": 1,
             "weather_source_id": source["id"], "config": {"incomplete": True}}],
             "compare_run_ids": []}
        saved = service.save_project({"expected_revision": 0, "project": draft})
        assert saved["revision"] == 1
        with pytest.raises(ServiceError) as stale:
            service.save_project({"expected_revision": 0, "project": draft})
        assert stale.value.code == "PROJECT_REVISION_CONFLICT"
        assert wait_finished(service, ar["run_id"])["state"] == "completed"
        assert wait_finished(service, br["run_id"])["state"] == "completed"
        draft["compare_run_ids"] = [ar["run_id"], br["run_id"]]
        saved = service.save_project({"expected_revision": 1, "project": draft})
        ra, rb = service.get_result(ar["run_id"]), service.get_result(br["run_id"])
        assert ra["result"]["config"]["ascent"]["payload_mass_kg"] == 1
        assert rb["result"]["config"]["ascent"]["payload_mass_kg"] == 1.5
        assert ra["n"] == rb["n"] == 1
        assert ra["result"]["complete"] and rb["result"]["complete"]
        assert ra["result"]["summary"]["landing"] != rb["result"]["summary"]["landing"]
        assert service.get_run(ar["run_id"])["spec"]["submitted_input"] == a
        assert any(e["type"] == "burst" for e in ra["result"]["events"])
        committed_before = (tmp_path / "results" / ar["run_id"] / "COMMITTED.json").read_bytes()
    # New service, same disk state. No weather loader is needed to read results.
    reopened = ApplicationService(tmp_path)
    reopened._load_sources = lambda: None
    with reopened:
        assert reopened.weather_sources()["sources"] == []
        assert reopened.get_project() == saved
        assert reopened.get_result(ar["run_id"]) == ra
        assert reopened.get_result(br["run_id"]) == rb
        assert (tmp_path / "results" / ar["run_id"] / "COMMITTED.json").read_bytes() == committed_before
        assert len(reopened.list_runs()["runs"]) == 2


def test_real_support_stop_preserves_kernel_result(tmp_path):
    with ApplicationService(tmp_path) as service:
        source = service.weather_sources()["sources"][0]
        request = request_for(source)
        request["config"]["launch"]["longitude_deg"] = 136.24
        request["config"]["launch"]["altitude_m"] = 500.0  # valid start, later leaves support
        run = service.submit(request)
        assert wait_finished(service, run["run_id"])["state"] == "completed"
        result = service.get_result(run["run_id"])["result"]
        direct = simulate(request["config"], load_weather(REPO_ROOT / "references/flight_fixture/wakayama-weather.json.gz"))
        assert result == direct  # adapter preserves records, events, and the last valid point
        assert not result["complete"] and result["status"] == "stopped"
        assert result["summary"]["landing"] is None
        assert result["stop_reason"]["code"] == "LONGITUDE_OUT_OF_RANGE"
        assert result["records"] and result["records"][-1]["longitude_deg"] <= 136.25
        output = tmp_path / "results" / run["run_id"] / "result.json"
        output.write_text("{}", encoding="utf-8")
        with pytest.raises(ServiceError) as corrupt:
            service.get_result(run["run_id"])
        assert corrupt.value.code == "RESULT_INTEGRITY_ERROR"


def test_queue_cancel_restart_no_auto_resubmit_and_owner_lock(tmp_path):
    with paused_service(tmp_path, max_queued=1) as service:
        source = service.weather_sources()["sources"][0]
        one = service.submit(request_for(source))
        with pytest.raises(ServiceError) as full:
            service.submit(request_for(source, "other"))
        assert full.value.status == 429
        assert len(service.list_runs()["runs"]) == 1
        assert service.cancel(one["run_id"])["state"] == "cancelled"
        two = service.submit(request_for(source, "second"))
        project = service.get_project()
        project["project"]["compare_run_ids"] = [two["run_id"]]
        with pytest.raises(ServiceError) as incomplete_comparison:
            service.save_project({"expected_revision": 0, "project": project["project"]})
        assert incomplete_comparison.value.code == "COMPARISON_RESULT_NOT_READY"
        assert service.get_project()["project"]["compare_run_ids"] == []
        with pytest.raises(ServiceError) as pending:
            service.get_result(two["run_id"])
        assert pending.value.code == "RESULT_NOT_AVAILABLE"
        with pytest.raises(RuntimeError, match="already in use"):
            ApplicationService(tmp_path).start()
    with ApplicationService(tmp_path) as reopened:
        assert reopened.get_run(one["run_id"])["state"] == "cancelled"
        assert reopened.get_run(two["run_id"])["state"] == "interrupted"
        assert reopened.submit(request_for(source, "second"))["state"] == "interrupted"
        assert reopened.get_run(two["run_id"])["result_available"] is False


def test_running_recovery_and_truthful_cancel(tmp_path):
    with paused_service(tmp_path) as service:
        source = service.weather_sources()["sources"][0]
        run = service.submit(request_for(source))
        # Persist the same state left by abrupt termination, without killing pytest.
        with service._db:
            service._db.execute("UPDATE jobs SET state='running' WHERE run_id=?", (run["run_id"],))
        assert service.get_run(run["run_id"])["cancellable"] is False
        with pytest.raises(ServiceError) as running:
            service.cancel(run["run_id"])
        assert running.value.code == "NOT_CANCELLABLE"
        assert service.get_run(run["run_id"])["state"] == "running"
    with ApplicationService(tmp_path) as reopened:
        assert reopened.get_run(run["run_id"])["state"] == "interrupted"
        assert reopened.get_run(run["run_id"])["error"]["code"] == "RESTART_INTERRUPTED"


def test_publish_failure_keeps_previous_result(tmp_path, monkeypatch):
    import backend.application as application
    with ApplicationService(tmp_path) as service:
        source = service.weather_sources()["sources"][0]
        first = request_for(source)
        first["config"]["integration"]["max_duration_s"] = 10
        one = service.submit(first)
        assert wait_finished(service, one["run_id"])["state"] == "completed"
        original = service.get_result(one["run_id"])

        def fail_publish(*args):
            raise OSError("injected failure before commit marker")

        monkeypatch.setattr(application, "publish_result", fail_publish)
        second = copy.deepcopy(first)
        second["client_request_id"] = "second"
        two = service.submit(second)
        detail = wait_finished(service, two["run_id"])
        assert detail["state"] == "failed" and detail["result_available"] is False
        assert not (tmp_path / "results" / two["run_id"]).exists()
        assert (tmp_path / "staging" / two["run_id"] / "manifest.json").exists()
        assert service.get_result(one["run_id"]) == original


def test_api_validation_and_no_api_spa_fallback(tmp_path):
    app = create_app(tmp_path)
    app.state.service._dispatch = lambda: app.state.service._stop.wait()
    with TestClient(app) as client:
        assert client.get("/api/v1/typo").status_code == 404
        assert client.post("/api/v1/runs", content="{}").status_code == 415
        source = client.get("/api/v1/weather-sources").json()["sources"][0]
        request = request_for(source)
        wrong = copy.deepcopy(request)
        wrong["weather_source_id"] = "../../arbitrary-path"
        assert client.post("/api/v1/runs", json=wrong).status_code == 422
        wrong = copy.deepcopy(request)
        wrong["config"]["launch"]["time_utc"] = "2026-09-23T12:30:00+09:00"
        assert client.post("/api/v1/runs", json=wrong).status_code == 422
        wrong = copy.deepcopy(request)
        wrong["config"]["ascent"] = {"mode": "constant_speed", "speed_m_s": 5}
        wrong["config"]["burst"] = {"mode": "diameter", "diameter_m": 5}
        assert client.post("/api/v1/runs", json=wrong).status_code == 422
        accepted = client.post("/api/v1/runs", json=request)
        assert accepted.status_code == 202
        run_id = accepted.json()["run_id"]
        assert client.get("/api/v1/runs").json()["runs"][0]["run_id"] == run_id
        assert client.get(f"/api/v1/runs/{run_id}").json()["spec"]["submitted_input"] == request
        assert client.post(f"/api/v1/runs/{run_id}/cancel", json={}).json()["state"] == "cancelled"
        assert client.post(f"/api/v1/runs/{run_id}/cancel", json={}).status_code == 409


def test_corrupt_source_does_not_block_other_source_or_project(tmp_path, monkeypatch):
    import backend.application as application
    original = application.read_json

    def fail_one(path):
        if path.name == "wakayama-weather.json.gz":
            raise ValueError("test corrupted JSON")
        return original(path)

    monkeypatch.setattr(application, "read_json", fail_one)
    with ApplicationService(tmp_path) as service:
        sources = service.weather_sources()
        assert [s["id"] for s in sources["sources"]] == ["hokkaido-gfs-fixture", "jra3q-surface-fixture"]
        assert sources["source_errors"][0]["id"] == "wakayama-gfs-fixture"
        assert service.get_project()["revision"] == 0


def jra_source(service):
    return next(s for s in service.weather_sources()["sources"] if s["id"] == "jra3q-surface-fixture")


def private_jra_source(tmp_path, monkeypatch):
    """Only copied test fixtures may be removed/replaced; never edit repo inputs."""
    import backend.application as application
    root = tmp_path / "input-copy"
    for name in ("references/flight_fixture/jra3q-weather.json.gz", "examples/jra3q-ground-flight.json"):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / name, path)
    monkeypatch.setattr(application, "REPO_ROOT", root)
    return root / "references/flight_fixture/jra3q-weather.json.gz"


def test_saved_jra_native_support_and_effective_metadata(tmp_path):
    with paused_service(tmp_path) as service:
        source = jra_source(service)
        field = load_weather(REPO_ROOT / "references/flight_fixture/jra3q-weather.json.gz")
        assert source["kind"] == "saved_jra3q"
        assert source["schema"] == "balloon.weather.jra3q_surface/1"
        assert source["product"] == "jra3q.ncar.regular_gaussian.model_surface_analysis"
        assert source["time_kind"] == "analysis_valid_utc"
        assert source["run_utc"] is None and "lead_hours" not in source
        assert source["valid_times_utc"] == ["2024-01-01T00:00:00+00:00", "2024-01-01T06:00:00+00:00", "2024-01-01T12:00:00+00:00"]
        assert source["bounds"] == {"lat": [min(field.latitudes), max(field.latitudes)],
                                     "lon": [min(field.longitudes), max(field.longitudes)], "model_level": [1, 100]}
        assert source["metadata"] == field.metadata
        assert source["metadata"]["reconstruction_policy"] == "native_horizontal_first_surface_v1"
        assert source["metadata"]["native_wind_not_used_model_levels"] == [1]
        request = request_for(source)
        run = service.submit(request)
        spec = service.get_run(run["run_id"])["spec"]
        assert spec["config"]["launch"]["time_utc"] == "2024-01-01T02:17:13+00:00"
        assert spec["submitted_input"] == request
        assert spec["weather_snapshot"]["metadata"] == field.metadata
        assert spec["weather_snapshot"]["sha256"] == source["sha256"]


@pytest.mark.parametrize("launch,supported", [
    ("2023-12-31T23:59:59+00:00", False),
    ("2024-01-01T08:00:01+00:00", False),
    ("2024-01-01T08:00:00+00:00", True),
])
def test_saved_jra_requires_full_duration_window(tmp_path, launch, supported):
    with paused_service(tmp_path) as service:
        request = request_for(jra_source(service))
        request["config"]["launch"]["time_utc"] = launch
        if supported:
            assert service.submit(request)["state"] == "queued"
        else:
            with pytest.raises(ServiceError) as error:
                service.submit(request)
            assert (error.value.status, error.value.code) == (422, "WEATHER_WINDOW_UNSUPPORTED")
            assert service.list_runs()["runs"] == []
            assert list((tmp_path / "specs").iterdir()) == []


def test_jra_worker_matches_direct_result_and_effective_export(tmp_path):
    # One full C11 flight checks all records/events/summary, not only its last point.
    with ApplicationService(tmp_path) as service:
        source = jra_source(service)
        request = request_for(source)
        run = service.submit(request)
        assert wait_finished(service, run["run_id"])["state"] == "completed"
        envelope = service.get_result(run["run_id"])
        path = REPO_ROOT / "references/flight_fixture/jra3q-weather.json.gz"
        field = load_weather(path)
        direct = simulate(request["config"], field)
        assert envelope["result"] == direct
        assert direct["status"] == "landed" and direct["summary"]["landing"] is not None
        assert direct["records"][0]["time_utc"] == "2024-01-01T02:17:13+00:00"
        provenance = json.loads((tmp_path / "results" / run["run_id"] / "provenance.json").read_text(encoding="utf-8"))
        assert provenance["weather_bundle"]["metadata"] == field.metadata == source["metadata"]
        assert provenance["weather_bundle"]["sha256"] == source["sha256"]


@pytest.mark.parametrize("change,code", [("missing", "WEATHER_UNAVAILABLE"), ("replaced", "WEATHER_CHANGED")])
def test_jra_changed_source_refuses_new_work_but_reopens_result(tmp_path, monkeypatch, change, code):
    from balloon_sim.environment.storage import read_json, write_bundle
    weather_path = private_jra_source(tmp_path, monkeypatch)
    state = tmp_path / "state"
    with ApplicationService(state) as service:
        request = request_for(jra_source(service))
        request["config"]["integration"]["max_duration_s"] = 10
        run = service.submit(request)
        assert wait_finished(service, run["run_id"])["state"] == "completed"
        original = service.get_result(run["run_id"])
        marker = state / "results" / run["run_id"] / "COMMITTED.json"
        marker_before = marker.read_bytes()
        if change == "missing":
            weather_path.unlink()
        else:
            # A valid bundle at the same stable ID still needs a new identity.
            bundle = read_json(weather_path)
            bundle["metadata"]["test_replacement"] = "new bytes, unchanged physical arrays"
            weather_path.unlink()
            write_bundle(weather_path, bundle)
        # Re-reading the same accepted request stays idempotent even without input.
        assert service.submit(request)["run_id"] == run["run_id"]
        request["client_request_id"] = "new-work"
        with pytest.raises(ServiceError) as error:
            service.submit(request)
        assert (error.value.status, error.value.code) == (409, code)
        assert len(service.list_runs()["runs"]) == 1
        assert service.get_result(run["run_id"]) == original
    with ApplicationService(state) as reopened:
        errors = reopened.weather_sources()["source_errors"]
        if change == "missing":
            assert any(e["id"] == "jra3q-surface-fixture" and e["code"] == "SOURCE_UNAVAILABLE" for e in errors)
            with pytest.raises(ServiceError) as unavailable:
                reopened.submit(request)
            assert (unavailable.value.status, unavailable.value.code) == (422, "UNKNOWN_WEATHER_SOURCE")
        else:
            replacement = jra_source(reopened)
            assert replacement["id"] == original["weather_snapshot"]["id"]
            assert replacement["sha256"] != original["weather_snapshot"]["sha256"]
            assert replacement["metadata"] != original["weather_snapshot"]["metadata"]
        assert reopened.get_result(run["run_id"]) == original
        assert marker.read_bytes() == marker_before


@pytest.mark.parametrize("fault", ["truncated_gzip", "invalid_deflate", "invalid_join"])
def test_invalid_jra_source_is_not_published_and_project_reopens(tmp_path, monkeypatch, fault):
    from balloon_sim.environment.storage import read_json, write_bundle
    weather_path = private_jra_source(tmp_path, monkeypatch)
    if fault == "truncated_gzip":
        weather_path.write_bytes(weather_path.read_bytes()[:24])
    elif fault == "invalid_deflate":
        raw = weather_path.read_bytes()
        assert raw[:4] == b"\x1f\x8b\x08\x00"  # fixed 10-byte gzip header, no optional fields
        weather_path.write_bytes(raw[:10] + b"\x07" + raw[11:])  # reserved DEFLATE BTYPE=3
        with pytest.raises(zlib.error):
            read_json(weather_path)
    else:
        bundle = read_json(weather_path)
        bundle["reconstruction"]["join_model_levels"]["eastward_wind_m_s"] = 1
        weather_path.unlink()
        write_bundle(weather_path, bundle)
    state = tmp_path / "state"
    with paused_service(state) as service:
        assert all(s["id"] != "jra3q-surface-fixture" for s in service.weather_sources()["sources"])
        assert any(e["id"] == "jra3q-surface-fixture" for e in service.weather_sources()["source_errors"])
        project = service.get_project()
        saved = service.save_project({"expected_revision": 0, "project": project["project"]})
    with paused_service(state) as reopened:
        assert reopened.get_project() == saved
