"""Original UTC and missing-window semantics in the existing flight lifecycle."""
import copy
import json

import pytest

from backend.application import ServiceError
from backend.historical_catalog import load_historical_sources
from backend.storage import file_hash
from backend.tests.test_ensemble import paused, settle


def request(service):
    source = next(s for s in service.weather_sources()["sources"] if s["id"] == "jra3q-surface-fixture")
    config = copy.deepcopy(source["default_config"])
    # Short physical test still exercises real original fields and the worker.
    config["burst"] = {"mode": "altitude", "altitude_m": 500.0}
    config["integration"]["max_duration_s"] = 1200.0
    return {"mode": "historical_windows", "client_request_id": "historical-plan", "label": "Explicit times",
            "reason": "Two explicit original times for contract testing; not seasonal sampling.",
            "selection_context": {"interest": "original-date flight"},
            "windows": [{"window_id": "w1", "label": "Original one", "weather_source_id": source["id"],
                         "launch_time_utc": "2024-01-01T02:17:13Z", "reason": "Within saved field"},
                        {"window_id": "w2", "label": "Original two", "weather_source_id": source["id"],
                         "launch_time_utc": "2024-01-01T04:17:13Z", "reason": "Another explicit original time"},
                        {"window_id": "missing", "label": "Unavailable July", "weather_source_id": None,
                         "launch_time_utc": "2024-07-01T02:17:13Z", "reason": "Target retained even when unavailable"}],
            "cases": [{"case_id": "H", "candidate_id": "H", "candidate_revision": 1, "label": "Common vehicle", "config": config}]}


def test_original_windows_reuse_kernel_and_keep_missing_rows(tmp_path):
    with paused(tmp_path) as service:
        body = request(service)
        plan = service.ensemble.plan(body)
        assert plan["status"] == "ready" and plan["trial_count"] == 3
        assert plan["runnable_trial_count"] == 2 and plan["invalid_trial_count"] == 1
        assert plan["trials"][0]["config"]["launch"]["time_utc"] == "2024-01-01T02:17:13+00:00"
        assert plan["trials"][1]["config"]["launch"]["time_utc"] == "2024-01-01T04:17:13+00:00"
        assert "distribution" not in plan["sampling"]
        assert service.ensemble.plan(body) == plan
        job = service.ensemble.submit({"client_request_id": "historical-start", "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"]})
        done = settle(service, job["ensemble_id"])
        case = service.ensemble.case_result(done["latest_snapshot_id"], "H")
        assert case["mode"] == "historical_windows" and case["counts"]["planned"] == 3
        assert case["counts"]["landed"] == 2 and case["counts"]["invalid_input"] == 1
        assert case["overview_analysis"]["landing"]["n"] == 2
        assert all(t["parameter"] is None for t in case["trials"])
        first = case["trials"][0]
        result = service.ensemble.trial_result(case["snapshot_id"], first["trial_id"])
        assert result["result"]["config"]["launch"]["time_utc"] == plan["trials"][0]["config"]["launch"]["time_utc"]
        assert result["weather_snapshot"]["id"] == "jra3q-surface-fixture"
        # Saved result/snapshot reads do not depend on the current catalog.
        service._sources.pop("jra3q-surface-fixture")
        assert service.ensemble.case_result(case["snapshot_id"], "H") == case
        assert service.ensemble.trial_result(case["snapshot_id"], first["trial_id"])["result"] == result["result"]


@pytest.mark.parametrize("change,code", [("duplicate_time", "DUPLICATE_ORIGINAL_TIME"),
    ("forecast", "NOT_HISTORICAL_ANALYSIS"), ("delay", "HISTORICAL_DELAY_UNSUPPORTED")])
def test_refuse_ambiguous_historical_population(tmp_path, change, code):
    with paused(tmp_path) as service:
        body = request(service)
        if change == "duplicate_time": body["windows"][1]["launch_time_utc"] = body["windows"][0]["launch_time_utc"]
        if change == "forecast": body["windows"][0]["weather_source_id"] = "hokkaido-gfs-fixture"
        if change == "delay": body["cases"][0].update(parent_case_id="parent", delay_minutes=30.0)
        with pytest.raises(ServiceError) as caught: service.ensemble.plan(body)
        assert caught.value.code == code
        assert not service.list_runs()["runs"]


def test_unsupported_origins_and_times_remain_visible_not_extrapolated(tmp_path):
    with paused(tmp_path) as service:
        body = request(service)
        body["windows"][0]["launch_time_utc"] = "2030-01-01T00:00:00Z"
        body["cases"][0]["config"]["launch"]["latitude_deg"] = 43.0
        plan = service.ensemble.plan(body)
        assert plan["status"] == "unavailable"
        assert [t["preflight_error"]["code"] for t in plan["trials"]] == [
            "WEATHER_WINDOW_UNSUPPORTED", "WEATHER_ORIGIN_UNSUPPORTED", "HISTORICAL_WINDOW_UNAVAILABLE"]


def test_catalog_requires_fixed_hash_and_original_utc_field(tmp_path):
    from backend.worker import REPO_ROOT
    path = REPO_ROOT / "references/flight_fixture/jra3q-weather.json.gz"
    entry = {"id": "historical-example", "label": "Original dates", "path": str(path), "sha256": file_hash(path)}
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema": "balloon.historical-catalog/1", "sources": [entry]}), encoding="utf-8")
    sources, errors = load_historical_sources(catalog)
    assert not errors and sources[entry["id"]]["snapshot"]["time_kind"] == "analysis_valid_utc"
    entry["sha256"] = "0" * 64
    catalog.write_text(json.dumps({"schema": "balloon.historical-catalog/1", "sources": [entry]}), encoding="utf-8")
    sources, errors = load_historical_sources(catalog)
    assert not sources and errors[0]["code"] == "SOURCE_UNAVAILABLE"


@pytest.mark.parametrize("value", [None, [], {"schema": "other"}])
def test_malformed_catalog_does_not_block_saved_results(tmp_path, value):
    catalog = tmp_path / "bad.json"
    catalog.write_text(json.dumps(value), encoding="utf-8")
    sources, errors = load_historical_sources(catalog)
    assert not sources and errors[0]["id"] == "historical-catalog"
