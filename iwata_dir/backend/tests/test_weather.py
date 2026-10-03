"""Offline acquisition application tests; transport and raw GRIB are separate tests."""
import copy
from datetime import timedelta
import hashlib
import threading
import time

import pytest
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.application import ApplicationService, ServiceError
from backend.storage import file_hash, write_new_json
from backend.weather.catalog import BASE, observe_inventory
from backend.weather.service import WeatherService
from backend.worker import REPO_ROOT
from balloon_sim.environment.fields import WeatherError, _utc
from balloon_sim.environment.gfs import _request
from balloon_sim.environment.storage import read_json, write_bundle

RUN = "2026-09-22T18:00:00+00:00"


def deps():
    return {"available": True, "versions": {"test": "offline-injected-decoder"}, "missing": []}


class DirectoryGateway:
    def __init__(self, leads=range(9, 16)):
        self.calls, self.leads = [], list(leads)

    def fetch(self, url, max_bytes, cancel=None):
        self.calls.append(url)
        if url == BASE:
            names = ["gfs.20260922/", "https://evil.invalid/gfs.20260929/", "../gfs.20990101/"]
        elif url == BASE + "gfs.20260922/":
            names = ["18/", "12/", "13/"]
        else:
            cycle = url.split("/")[-3]
            names = [f"gfs.t{cycle}z.pgrb2.0p25.f{n:03d}" for n in self.leads]
            names += ["gfs.t18z.pgrb2.0p25.f099.idx", "../gfs.t18z.pgrb2.0p25.f100"]
        data = "".join(f'<a href="{name}">{name}</a>' for name in names).encode()
        return data, {"url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                      "started_at_utc": RUN, "completed_at_utc": RUN, "headers": {}}


def request(inventory_id, **changes):
    result = {"inventory_id": inventory_id, "run_utc": RUN,
              "region": {"kind": "bounds", "west": 135, "east": 136.25, "south": 33.5, "north": 34.75},
              "candidate_windows": [{"candidate_id": "C1", "launch_time_utc": "2026-09-23T03:30:00Z", "max_duration_s": 19800.0}]}
    result.update(changes)
    result["candidate_windows"] = [{"latitude_deg": 34.0, "longitude_deg": 135.5, **w}
                                   for w in result["candidate_windows"]]
    return result


def fixture_acquirer(request, folder, *, resume=False, progress=None, cancel=None):
    """Use a declared saved fixture instead of HTTP/ecCodes; exercise publication."""
    folder.mkdir(exist_ok=resume)
    spec = _request(request)
    bundle = read_json(REPO_ROOT / "references/flight_fixture/wakayama-weather.json.gz")
    times = [(_utc(spec["run_utc"])+timedelta(hours=h)).isoformat() for h in spec["lead_hours"]]
    indices = [bundle["axes"]["time_utc"].index(t) for t in times]
    bundle["axes"]["time_utc"] = times
    for category in ("fields", "surface"):
        bundle[category] = {name: [values[i] for i in indices] for name, values in bundle[category].items()}
    bundle["metadata"]["request"] = spec
    bundle["metadata"]["test_only"] = "Offline injected acquisition; not a new observed forecast."
    target = folder / "weather.json.gz"
    if not target.exists():
        write_bundle(target, bundle)
        write_new_json(folder / "receipt.json", {"bundle": target.name, "bundle_sha256": file_hash(target)})
    if progress:
        progress({"phase": "normalizing", "completed_files": len(times), "total_files": len(times),
                  "bytes_downloaded": target.stat().st_size, "bytes_reused": 0})
    return target


def options(**extra):
    return {"gateway": DirectoryGateway(), "dependency_check": deps, "acquirer": fixture_acquirer, **extra}


def prepared(service, **changes):
    inventory = service.weather.refresh_inventory({"run_utc": RUN})
    return service.weather.plan(request(inventory["inventory_id"], **changes))


def wait_job(weather, identity, seconds=15):
    deadline = time.monotonic()+seconds
    while time.monotonic() < deadline:
        job = weather.get_job(identity)
        if job["state"] not in {"queued", "running", "cancelling"}:
            return job
        time.sleep(.02)
    pytest.fail("acquisition did not finish within bounded test wait")


def test_directory_allowlist_and_no_get_network(tmp_path):
    gateway = DirectoryGateway()
    result = observe_inventory({"run_utc": None, "run_limit": 2}, gateway)
    assert len(result["runs"]) == 2
    assert result["runs"][0]["available_leads"] == list(range(9, 16))
    assert len(gateway.calls) == 4
    assert all(url.startswith(BASE) for url in gateway.calls)
    with ApplicationService(tmp_path, weather_options=options(gateway=gateway)) as app:
        inventory = app.weather.refresh_inventory({"run_utc": RUN})
        calls = list(gateway.calls)
        assert app.weather.get_inventory(inventory["inventory_id"]) == inventory
        assert app.weather.list_inventories()["inventories"] == [inventory]
        app.weather.list_jobs()
        app.weather.status()
        assert gateway.calls == calls


def test_partial_inventory_is_durable_and_does_not_substitute_failed_run(tmp_path):
    gateway = DirectoryGateway()
    original = gateway.fetch
    def fail_newest(url, *args, **kwargs):
        if url.endswith("/18/atmos/"):
            raise WeatherError("HTTP_STATUS", "injected 503")
        return original(url, *args, **kwargs)
    gateway.fetch = fail_newest
    with ApplicationService(tmp_path, weather_options=options(gateway=gateway)) as app:
        inventory = app.weather.refresh_inventory({})
        assert inventory["observation_status"] == "partial"
        assert inventory["observation_errors"][0]["run_utc"] == RUN
        assert [run["run_utc"] for run in inventory["runs"]] == ["2026-09-22T12:00:00+00:00"]
        plan = app.weather.plan(request(inventory["inventory_id"]))
        assert plan["status"] == "unavailable"
        assert plan["normalized_request"]["run_utc"] == RUN
        assert plan["issues"][0]["code"] == "RUN_NOT_OBSERVED"
        assert app.weather.get_inventory(inventory["inventory_id"]) == inventory
        before = list(gateway.calls)
    with ApplicationService(tmp_path, weather_options=options(gateway=gateway)) as reopened:
        assert reopened.weather.get_inventory(inventory["inventory_id"]) == inventory
        assert gateway.calls == before


def test_plan_full_delay_window_native_cadence_and_missing(tmp_path):
    with ApplicationService(tmp_path, weather_options=options(gateway=DirectoryGateway([120, 123]))) as app:
        inventory = app.weather.refresh_inventory({"run_utc": RUN})
        plan = app.weather.plan(request(inventory["inventory_id"], candidate_windows=[
            {"candidate_id": "C1", "launch_time_utc": "2026-09-27T17:30:00Z", "max_duration_s": 3600.0},
            {"candidate_id": "C2", "launch_time_utc": "2026-09-27T19:00:00Z", "max_duration_s": 14400.0}]))
        assert plan["status"] == "unavailable"
        assert plan["normalized_request"]["lead_hours"] == [119, 120, 123, 126]
        assert plan["missing_leads"] == [119, 126]
        assert plan["required_window"]["end_utc"] == "2026-09-27T23:00:00+00:00"
        assert plan["estimate"]["scalar_values"] > 0
        with pytest.raises(ServiceError, match="not admissible"):
            app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "missing"})


def test_plan_budget_dependencies_and_center_geometry(tmp_path):
    with ApplicationService(tmp_path, weather_options=options()) as app:
        plan = prepared(app, max_memory_bytes=16_777_216)
        assert "gfs.py" in plan["decoder_identity"]["files"]
        assert plan["issues"][0]["code"] == "MEMORY_BUDGET_EXCEEDED"
        center = prepared(app, region={"kind": "center", "latitude_deg": 34.0, "longitude_deg": 135.5,
                                       "half_width_km": 10.0, "half_height_km": 20.0})
        assert center["status"] == "ready"
        assert center["normalized_request"]["bounds"] == {"west": 135.25, "east": 135.75, "south": 33.75, "north": 34.25}
        app.weather.dependencies = lambda: {"available": False, "versions": {}, "missing": [{"name": "eccodes"}]}
        absent = prepared(app)
        assert absent["status"] == "unavailable"
        assert absent["issues"][0]["code"] == "DEPENDENCIES_UNAVAILABLE"


def test_inventory_raw_preserved_verified_and_failed_refresh_retained(tmp_path):
    gateway = DirectoryGateway()
    with ApplicationService(tmp_path, weather_options=options(gateway=gateway)) as app:
        inventory = app.weather.refresh_inventory({"run_utc": RUN})
        raw = tmp_path / inventory["raw_directory"] / inventory["observations"][0]["file"]
        assert file_hash(raw) == inventory["observations"][0]["sha256"]
        raw.write_bytes(b"modified raw listing")
        with pytest.raises(ServiceError) as changed:
            app.weather.plan(request(inventory["inventory_id"]))
        assert changed.value.code == "INVENTORY_INTEGRITY_ERROR"
        original = gateway.fetch
        def fail_after_root(url, *args, **kwargs):
            if url != BASE:
                raise OSError("injected after first listing")
            return original(url, *args, **kwargs)
        gateway.fetch = fail_after_root
        with pytest.raises(ServiceError):
            app.weather.refresh_inventory({})
        failures = list((tmp_path / "weather/inventories").glob("*/failure.json"))
        assert len(failures) == 1
        failed = read_json(failures[0])
        assert len(failed["observations"]) == 1
        assert (failures[0].parent / "000.html").is_file()
        assert len(app.weather.list_inventories()["inventories"]) == 1


def test_decoder_change_after_plan_refuses_submit(tmp_path):
    with ApplicationService(tmp_path, weather_options=options()) as app:
        plan = prepared(app)
        app.weather.dependencies = lambda: {"available": True, "versions": {"test": "changed"}, "missing": []}
        with pytest.raises(ServiceError) as changed:
            app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "changed"})
        assert changed.value.code == "DECODER_CHANGED"
        assert app.weather.list_jobs()["acquisitions"] == []


def test_startup_source_change_blocks_new_work_but_keeps_saved_reads_and_cancel(tmp_path, monkeypatch):
    import backend.application as module
    gateway = DirectoryGateway()
    app = ApplicationService(tmp_path, weather_options=options(gateway=gateway))
    app.weather._dispatch = lambda: app.weather._stop.wait()
    with app:
        plan = prepared(app)
        job = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "before-edit"})
        original_calls = list(gateway.calls)
        monkeypatch.setattr(module, "source_snapshot", lambda: {"fingerprint": "changed-disk-source"})
        for action in (
            lambda: app.weather.refresh_inventory({"run_utc": RUN}),
            lambda: app.weather.plan(request(plan["request"]["inventory_id"])),
            lambda: app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "after-edit"}),
        ):
            with pytest.raises(ServiceError) as changed:
                action()
            assert changed.value.code == "SOURCE_CHANGED"
        assert gateway.calls == original_calls
        assert app.weather.get_plan(plan["plan_id"]) == plan
        assert app.weather.get_inventory(plan["request"]["inventory_id"])["inventory_id"] == plan["request"]["inventory_id"]
        assert app.get_project()["revision"] == 0
        # Repeating the same accepted request only reads its saved job identity.
        assert app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "before-edit"})["acquisition_id"] == job["acquisition_id"]
        assert app.weather.cancel(job["acquisition_id"])["state"] == "cancelled"
        with pytest.raises(ServiceError) as changed:
            app.weather.retry(job["acquisition_id"])
        assert changed.value.code == "SOURCE_CHANGED"


def test_source_change_during_acquisition_retains_input_without_publishing(tmp_path, monkeypatch):
    import backend.application as module
    original = module.source_snapshot
    def changed_after_bytes(request, folder, **kwargs):
        target = fixture_acquirer(request, folder, **kwargs)
        monkeypatch.setattr(module, "source_snapshot", lambda: {"fingerprint": "changed-mid-transfer"})
        return target
    with ApplicationService(tmp_path, weather_options=options(acquirer=changed_after_bytes)) as app:
        sources_before = app.weather_sources()["sources"]
        plan = prepared(app)
        job = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "mid-edit"})
        failed = wait_job(app.weather, job["acquisition_id"])
        assert failed["state"] == "failed" and failed["error"]["code"] == "SOURCE_CHANGED"
        folder = tmp_path / "weather/acquisitions" / job["acquisition_id"]
        assert (folder / "weather.json.gz").is_file()
        assert not (folder / "ASSET.json").exists()
        assert app.weather_sources()["sources"] == sources_before
        assert app.weather.get_plan(plan["plan_id"]) == plan
    monkeypatch.setattr(module, "source_snapshot", original)
    with ApplicationService(tmp_path, weather_options=options()) as reopened:
        reopened.weather.retry(job["acquisition_id"])
        assert wait_job(reopened.weather, job["acquisition_id"])["state"] == "completed"


def test_source_change_during_inventory_keeps_raw_and_releases_refresh_lock(tmp_path, monkeypatch):
    import backend.application as module
    gateway = DirectoryGateway()
    original_source, original_fetch = module.source_snapshot, gateway.fetch
    def changing_fetch(*args, **kwargs):
        response = original_fetch(*args, **kwargs)
        monkeypatch.setattr(module, "source_snapshot", lambda: {"fingerprint": "changed-mid-listing"})
        return response
    with ApplicationService(tmp_path, weather_options=options(gateway=gateway)) as app:
        gateway.fetch = changing_fetch
        with pytest.raises(ServiceError) as changed:
            app.weather.refresh_inventory({"run_utc": RUN})
        assert changed.value.code == "SOURCE_CHANGED"
        assert app.weather.list_inventories()["inventories"] == []
        failures = list((tmp_path / "weather/inventories").glob("*/failure.json"))
        assert len(failures) == 1 and (failures[0].parent / "000.html").is_file()
        assert read_json(failures[0])["error"]["code"] == "SOURCE_CHANGED"
        monkeypatch.setattr(module, "source_snapshot", original_source)
        gateway.fetch = original_fetch
        assert app.weather.refresh_inventory({"run_utc": RUN})["runs"]


def test_source_change_during_asset_validation_does_not_register_marker(tmp_path, monkeypatch):
    import backend.application as module
    original_source = module.source_snapshot
    with ApplicationService(tmp_path, weather_options=options()) as app:
        sources_before = app.weather_sources()["sources"]
        original_publish = app.weather._publish
        def changed_after_validation(*args):
            result = original_publish(*args)
            monkeypatch.setattr(module, "source_snapshot", lambda: {"fingerprint": "changed-during-validation"})
            return result
        app.weather._publish = changed_after_validation
        plan = prepared(app)
        job = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "publication-edit"})
        failed = wait_job(app.weather, job["acquisition_id"])
        assert failed["state"] == "failed" and failed["error"]["code"] == "SOURCE_CHANGED"
        assert (tmp_path / "weather/acquisitions" / job["acquisition_id"] / "ASSET.json").is_file()
        assert app.weather_sources()["sources"] == sources_before
    monkeypatch.setattr(module, "source_snapshot", original_source)
    with ApplicationService(tmp_path, weather_options=options()) as reopened:
        reopened.weather.retry(job["acquisition_id"])
        assert wait_job(reopened.weather, job["acquisition_id"])["state"] == "completed"


def test_acquire_fixed_input_run_reopen_and_cache_without_network(tmp_path):
    opts = options()
    with ApplicationService(tmp_path, weather_options=opts) as app:
        plan = prepared(app)
        body = {"plan_id": plan["plan_id"], "client_request_id": "weather-1"}
        accepted = app.weather.submit(body)
        finished = wait_job(app.weather, accepted["acquisition_id"])
        assert finished["state"] == "completed", finished
        sources = app.weather_sources()["sources"]
        acquired = next(s for s in sources if s["id"] == finished["weather_source_id"])
        assert acquired["kind"] == "acquired_gfs" and acquired["default_config"] is None
        assert app.get_project()["project"]["candidates"] == []
        config = copy.deepcopy(sources[0]["default_config"])
        run = app.submit({"client_request_id": "flight", "candidate_id": "C1", "candidate_revision": 2,
                          "label": "fixed acquisition", "weather_source_id": acquired["id"], "config": config})
        deadline = time.monotonic()+60
        while app.get_run(run["run_id"])["state"] in {"queued", "running"} and time.monotonic() < deadline:
            time.sleep(.05)
        assert app.get_run(run["run_id"])["state"] == "completed"
        saved_result = app.get_result(run["run_id"])
        cache = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "weather-2"})
        assert cache["reused"] and cache["weather_source_id"] == acquired["id"]
        assert cache["progress"]["completed_files"] == cache["progress"]["total_files"] == 7
        assert cache["progress"]["bytes_downloaded"] == 0
        assert app.weather.submit(body)["acquisition_id"] == accepted["acquisition_id"]
        # A changed draft duration must be checked against the selected completed field.
        config["integration"]["max_duration_s"] = 86400
        with pytest.raises(ServiceError) as unsupported:
            app.submit({"client_request_id": "late", "candidate_id": "C1", "candidate_revision": 3,
                        "label": "late", "weather_source_id": acquired["id"], "config": config})
        assert unsupported.value.code == "WEATHER_WINDOW_UNSUPPORTED"
    gateway = DirectoryGateway()
    with ApplicationService(tmp_path, weather_options=options(gateway=gateway)) as reopened:
        assert reopened.get_result(run["run_id"]) == saved_result
        assert any(s["id"] == acquired["id"] for s in reopened.weather_sources()["sources"])
        assert reopened.weather.get_plan(plan["plan_id"]) == plan
        assert gateway.calls == []


def test_partial_failure_is_not_published_and_explicit_retry_keeps_attempt(tmp_path):
    calls = []
    def partial(request, folder, **kwargs):
        calls.append(kwargs["resume"])
        if len(calls) == 1:
            folder.mkdir()
            (folder / "preserved.partial").write_bytes(b"partial-test")
            kwargs["progress"]({"phase": "downloading", "completed_files": 0, "bytes_downloaded": 12})
            raise WeatherError("INJECTED_TRANSFER_FAILURE", "offline partial failure")
        assert (folder / "preserved.partial").read_bytes() == b"partial-test"
        return fixture_acquirer(request, folder, **kwargs)
    with ApplicationService(tmp_path, weather_options=options(acquirer=partial)) as app:
        sources_before = app.weather_sources()["sources"]
        plan = prepared(app)
        job = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "partial"})
        failed = wait_job(app.weather, job["acquisition_id"])
        assert failed["state"] == "failed"
        assert app.weather_sources()["sources"] == sources_before
        app.weather.retry(job["acquisition_id"])
        done = wait_job(app.weather, job["acquisition_id"])
        assert done["state"] == "completed" and done["attempt"] == 2
        assert done["previous_attempts"][0]["error"]["code"] == "INJECTED_TRANSFER_FAILURE"
        assert calls == [False, True]


def test_retry_reuses_later_completed_identical_asset(tmp_path):
    calls = []
    def first_fails(request, folder, **kwargs):
        calls.append(folder)
        if len(calls) == 1:
            raise WeatherError("INJECTED_FAILURE", "before acquiring")
        return fixture_acquirer(request, folder, **kwargs)
    with ApplicationService(tmp_path, weather_options=options(acquirer=first_fails)) as app:
        plan = prepared(app)
        a = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "failed-a"})
        assert wait_job(app.weather, a["acquisition_id"])["state"] == "failed"
        b = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "replacement-b"})
        done = wait_job(app.weather, b["acquisition_id"])
        assert done["state"] == "completed"
        retry = app.weather.retry(a["acquisition_id"])
        assert retry["state"] == "completed" and retry["reused"]
        assert retry["weather_source_id"] == done["weather_source_id"]
        assert retry["progress"]["completed_files"] == retry["progress"]["total_files"] == 7
        assert retry["progress"]["bytes_downloaded"] == 0
        assert len(calls) == 2


def test_partial_completion_marker_does_not_prevent_retry(tmp_path, monkeypatch):
    import backend.weather.service as module
    original = module.write_new_json
    failed = []
    def break_marker(path, value):
        if path.name.startswith("ASSET.") and path.suffix == ".partial" and not failed:
            failed.append(path)
            path.write_text('{"unfinished":', encoding="utf-8")
            raise OSError("injected interruption while writing completion marker")
        return original(path, value)
    monkeypatch.setattr(module, "write_new_json", break_marker)
    with ApplicationService(tmp_path, weather_options=options()) as app:
        plan = prepared(app)
        job = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "marker"})
        assert wait_job(app.weather, job["acquisition_id"])["state"] == "failed"
        assert failed[0].exists() and not (failed[0].parent / "ASSET.json").exists()
        app.weather.retry(job["acquisition_id"])
        assert wait_job(app.weather, job["acquisition_id"])["state"] == "completed"
        assert failed[0].exists()  # original failure evidence is retained


def test_cancel_running_does_not_publish_and_active_idempotency(tmp_path):
    entered = threading.Event()
    def blocked(request, folder, *, cancel, **kwargs):
        entered.set()
        assert cancel.wait(10)
        raise WeatherError("ACQUISITION_CANCELLED", "cancelled test")
    with ApplicationService(tmp_path, weather_options=options(acquirer=blocked)) as app:
        sources_before = app.weather_sources()["sources"]
        plan = prepared(app)
        a = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "a"})
        assert entered.wait(5)
        b_body = {"plan_id": plan["plan_id"], "client_request_id": "b"}
        assert app.weather.submit(b_body)["acquisition_id"] == a["acquisition_id"]
        assert app.weather.cancel(a["acquisition_id"])["state"] == "cancelling"
        assert wait_job(app.weather, a["acquisition_id"])["state"] == "cancelled"
        assert app.weather.submit(b_body)["acquisition_id"] == a["acquisition_id"]
        assert len(app.weather.list_jobs()["acquisitions"]) == 1
        assert app.weather_sources()["sources"] == sources_before


def test_restart_keeps_queue_interrupted_without_auto_http(tmp_path):
    app = ApplicationService(tmp_path, weather_options=options())
    app.weather._dispatch = lambda: app.weather._stop.wait()
    with app:
        plan = prepared(app)
        job = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "restart"})
        assert job["state"] == "queued"
    gateway = DirectoryGateway()
    with ApplicationService(tmp_path, weather_options=options(gateway=gateway)) as reopened:
        assert reopened.weather.get_job(job["acquisition_id"])["state"] == "interrupted"
        assert gateway.calls == []
        reopened.weather.retry(job["acquisition_id"])
        assert wait_job(reopened.weather, job["acquisition_id"])["state"] == "completed"
        assert gateway.calls == []  # injected acquirer uses saved bytes only


def test_corrupt_asset_refuses_reuse_but_saved_project_still_opens(tmp_path):
    with ApplicationService(tmp_path, weather_options=options()) as app:
        plan = prepared(app)
        job = app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "first"})
        assert wait_job(app.weather, job["acquisition_id"])["state"] == "completed"
        path = tmp_path / "weather/acquisitions" / job["acquisition_id"] / "weather.json.gz"
        path.write_bytes(b"changed")
        with pytest.raises(ServiceError) as corrupt:
            app.weather.submit({"plan_id": plan["plan_id"], "client_request_id": "second"})
        assert corrupt.value.code == "ASSET_INTEGRITY_ERROR"
    with ApplicationService(tmp_path, weather_options=options()) as reopened:
        assert reopened.get_project()["revision"] == 0
        assert len(reopened.weather_sources()["source_errors"]) == 1


def test_weather_api_and_custom_dist_are_offline(tmp_path, monkeypatch):
    dist = tmp_path / "selected-dist"
    dist.mkdir()
    (dist / "index.html").write_text("<h1>selected 470</h1>", encoding="utf-8")
    monkeypatch.setenv("BALLOON_FRONTEND_DIST", str(dist))
    gateway = DirectoryGateway()
    with TestClient(create_app(tmp_path / "state", weather_options=options(gateway=gateway))) as client:
        assert "selected 470" in client.get("/").text
        assert client.post("/api/v1/weather-inventories/refresh", json={"url": "https://example.com"}).status_code == 422
        assert gateway.calls == []
        inv = client.post("/api/v1/weather-inventories/refresh", json={"run_utc": RUN}).json()
        plan = client.post("/api/v1/weather-plans", json=request(inv["inventory_id"]))
        assert plan.status_code == 201 and plan.json()["status"] == "ready"
        calls = list(gateway.calls)
        assert client.get("/api/v1/weather-plans/"+plan.json()["plan_id"]).json() == plan.json()
        assert client.get("/api/v1/weather-acquisitions").json() == {"acquisitions": []}
        assert gateway.calls == calls
