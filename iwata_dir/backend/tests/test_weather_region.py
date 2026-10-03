"""Launch inclusion before acquisition; no network or worker startup."""
from copy import deepcopy

import pytest
from pydantic import ValidationError

from backend.weather.contracts import WeatherPlanRequest
from backend.weather.planning import make_plan


def request(**changes):
    value = {"inventory_id": "i", "run_utc": "2026-09-30T00:00:00Z",
             "region": {"kind": "bounds", "west": 139.5, "east": 146, "south": 41, "north": 46},
             "candidate_windows": [{"candidate_id": "A", "launch_time_utc": "2026-10-04T23:17:13Z",
                                    "latitude_deg": 43, "longitude_deg": 141.5, "max_duration_s": 14400}]}
    value.update(changes)
    return WeatherPlanRequest.model_validate(value).model_dump()


def plan(value):
    inventory = {"observed_at_utc": "2026-09-30T09:00:00Z", "runs": [
        {"run_utc": "2026-09-30T00:00:00+00:00", "available_leads": list(range(121))+list(range(123,385,3))}]}
    return make_plan(value, inventory, {"available": True, "missing": [], "versions": {"test": "offline"}})


def test_contains_launch_and_brackets_entire_120h_boundary():
    p = plan(request())
    assert p["status"] == "ready"
    assert p["normalized_request"]["lead_hours"] == [119,120,123,126]
    assert p["launch_support"] == [{"candidate_id": "A", "latitude_deg": 43.0, "longitude_deg": 141.5, "inside": True}]


def test_outside_delay_location_refuses_before_acquisition_without_changing_region():
    value = request(); child = {**value["candidate_windows"][0], "candidate_id": "delay", "longitude_deg": 147}
    value["candidate_windows"].append(child); original = deepcopy(value)
    p = plan(value)
    assert p["status"] == "unavailable" and value == original
    assert p["issues"][0]["code"] == "LAUNCH_OUTSIDE_REGION"
    assert p["issues"][0]["candidate_ids"] == ["delay"]
    assert [w["inside"] for w in p["launch_support"]] == [True,False]


def test_equivalent_longitude_and_rounded_edge_are_supported():
    value = request(region={"kind": "bounds", "west": -21, "east": -19, "south": 42.01, "north": 44})
    value["candidate_windows"][0].update(longitude_deg=-20, latitude_deg=42)
    p = plan(value)
    assert p["status"] == "ready" and p["normalized_request"]["bounds"]["south"] == 42
    assert p["launch_support"][0]["inside"] is True


def test_new_requests_require_location_not_guessed_from_region_center():
    value = request(); del value["candidate_windows"][0]["latitude_deg"]
    with pytest.raises(ValidationError):
        WeatherPlanRequest.model_validate(value)


def test_endpoint_window_and_overrun_are_distinct():
    value = request(); value["candidate_windows"][0]["launch_time_utc"] = "2026-10-15T19:17:13Z"
    assert plan(value)["normalized_request"]["lead_hours"] == [378,381,384]
    value["candidate_windows"][0]["launch_time_utc"] = "2026-10-15T20:00:01Z"
    with pytest.raises(ValueError, match="INVALID_WINDOW"):
        plan(value)


@pytest.mark.parametrize("damage", ["legacy", "evidence", "outside"])
def test_start_rechecks_fixed_launch_proof_and_keeps_accepted_request(tmp_path, damage):
    from backend.errors import ServiceError
    from backend.storage import canonical
    from backend.weather.service import WeatherService
    from backend.tests.test_weather import options, request as old_request, RUN
    service = WeatherService(tmp_path, **options())
    service._dispatch = lambda: service._stop.wait()
    service.start()
    try:
        inventory = service.refresh_inventory({"run_utc": RUN})
        p = service.plan(old_request(inventory["inventory_id"]))
        accepted = service.submit({"plan_id": p["plan_id"], "client_request_id": "accepted"})
        service.cancel(accepted["acquisition_id"])
        altered = deepcopy(p)
        if damage == "legacy":
            altered.pop("launch_support")
            for w in altered["request"]["candidate_windows"]:
                del w["latitude_deg"]; del w["longitude_deg"]
        elif damage == "evidence":
            altered["launch_support"][0]["latitude_deg"] += .1
        else:
            altered["request"]["candidate_windows"][0]["longitude_deg"] = 150
            altered["launch_support"][0].update(longitude_deg=150, inside=False)
        with service._guard, service.db:
            service.db.execute("UPDATE documents SET body=? WHERE kind='plan' AND id=?", (canonical(altered),p["plan_id"]))
        assert service.get_plan(p["plan_id"]) == altered
        assert service.submit({"plan_id": p["plan_id"], "client_request_id": "accepted"})["acquisition_id"] == accepted["acquisition_id"]
        for action in [lambda: service.submit({"plan_id": p["plan_id"], "client_request_id": "new"}), lambda: service.retry(accepted["acquisition_id"])]:
            with pytest.raises(ServiceError) as refused:
                action()
            assert refused.value.code == "PLAN_REPLAN_REQUIRED"
        assert len(service.list_jobs()["acquisitions"]) == 1
        assert service.get_job(accepted["acquisition_id"])["state"] == "cancelled"
    finally:
        service.close()
