"""Point terrain reads are bound to bytes and inputs, not flight acceptance."""
import copy

import pytest
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.application import ApplicationService, ServiceError
from backend.storage import file_hash
from backend.worker import source_snapshot
from balloon_sim.environment.storage import load_weather


@pytest.fixture(scope="module")
def registered_sources():
    # No service, DB, worker or HTTP is started by these read-only checks.
    service = ApplicationService()
    service._load_sources()
    assert not service._source_errors
    return service._sources


@pytest.fixture
def service(registered_sources):
    app = ApplicationService()
    app._sources = copy.deepcopy(registered_sources)
    app._snapshot = source_snapshot()
    return app


def query_for(source):
    return {"expected_sha256": source["snapshot"]["sha256"],
            **{key: value for key, value in source["default_config"]["launch"].items()
               if key != "altitude_m"},
            "launch_altitude_m": source["default_config"]["launch"]["altitude_m"]}


@pytest.mark.parametrize("source_id,ground_model", [
    ("hokkaido-gfs-fixture", "coarse_gfs_orography"),
    ("jra3q-surface-fixture", "jra3q_model_orography"),
])
def test_ground_matches_flight_field_without_changing_source(service, source_id, ground_model):
    source = service._sources[source_id]
    before = copy.deepcopy(source)
    query = query_for(source)
    expected = load_weather(source["path"]).ground_altitude(
        query["time_utc"], query["latitude_deg"], query["longitude_deg"])
    result = service.weather_ground(source_id, query)
    assert result["ground_altitude_m"] == expected
    assert result["clearance_m"] == query["launch_altitude_m"] - expected
    assert result["weather_sha256"] == query["expected_sha256"]
    assert result["weather_source_id"] == source_id
    assert result["ground_model"] == ground_model
    assert result["height_reference"] == "geometric_asl_m"
    assert result["is_fine_dem"] is False
    assert result["scope"] == "point_ground_only_not_full_flight_validation"
    assert source == before
    assert service._db is None and service._thread is None


def test_ground_reports_below_model_ground_without_rewriting_altitude(service):
    source_id = "hokkaido-gfs-fixture"
    query = query_for(service._sources[source_id])
    query.update(latitude_deg=43.5, longitude_deg=143.0)
    result = service.weather_ground(source_id, query)
    assert result["ground_altitude_m"] > 1100
    assert result["clearance_m"] < -1000 and result["below_model_ground"]
    assert result["query"]["launch_altitude_m"] == query["launch_altitude_m"]


@pytest.mark.parametrize("patch,code", [
    ({"time_utc": "2026-09-23T03:30:00+09:00"}, "NON_UTC_TIME"),
    ({"time_utc": "bad"}, "INVALID_TIME"),
    ({"time_utc": "2030-01-01T00:00:00Z"}, "TIME_OUT_OF_RANGE"),
    ({"latitude_deg": 0.0}, "LATITUDE_OUT_OF_RANGE"),
    ({"longitude_deg": 0.0}, "LONGITUDE_OUT_OF_RANGE"),
])
def test_ground_rejects_unsupported_point(service, patch, code):
    query = {**query_for(service._sources["hokkaido-gfs-fixture"]), **patch}
    with pytest.raises(ServiceError) as error:
        service.weather_ground("hokkaido-gfs-fixture", query)
    assert error.value.status == 422 and error.value.code == code


def test_ground_identity_missing_and_changed_bytes(service, tmp_path):
    source_id = "hokkaido-gfs-fixture"
    source = service._sources[source_id]
    query = query_for(source)
    with pytest.raises(ServiceError) as unknown:
        service.weather_ground("unregistered", query)
    assert unknown.value.code == "UNKNOWN_WEATHER_SOURCE"
    with pytest.raises(ServiceError) as changed:
        service.weather_ground(source_id, {**query, "expected_sha256": "0" * 64})
    assert changed.value.code == "WEATHER_CHANGED"
    source["path"] = tmp_path / "missing-weather.json.gz"
    with pytest.raises(ServiceError) as missing:
        service.weather_ground(source_id, query)
    assert missing.value.status == 409 and missing.value.code == "WEATHER_UNAVAILABLE"
    source["path"].write_bytes(b"changed")
    with pytest.raises(ServiceError) as changed:
        service.weather_ground(source_id, query)
    assert changed.value.code == "WEATHER_CHANGED"
    source["snapshot"]["sha256"] = file_hash(source["path"])
    with pytest.raises(ServiceError) as invalid:
        service.weather_ground(source_id, query_for(source))
    assert invalid.value.code == "WEATHER_UNAVAILABLE"


def test_ground_rechecks_bytes_after_loading(service, tmp_path, monkeypatch):
    import backend.application as application
    source = service._sources["hokkaido-gfs-fixture"]
    saved = tmp_path / "weather.json.gz"
    saved.write_bytes(source["path"].read_bytes())
    source["path"] = saved
    original = application.load_weather
    def changed_after_load(path):
        field = original(path)
        saved.write_bytes(b"replacement")
        return field
    monkeypatch.setattr(application, "load_weather", changed_after_load)
    with pytest.raises(ServiceError) as changed:
        service.weather_ground("hokkaido-gfs-fixture", query_for(source))
    assert changed.value.code == "WEATHER_CHANGED"


def test_ground_api_validates_input_and_returns_bound_read(service):
    app = create_app()
    app.state.service._sources = service._sources
    app.state.service._snapshot = service._snapshot
    client = TestClient(app)  # No lifespan: no worker/service/network starts.
    query = query_for(service._sources["hokkaido-gfs-fixture"])
    path = "/api/v1/weather-sources/hokkaido-gfs-fixture/ground"
    response = client.get(path, params=query)
    assert response.status_code == 200
    assert response.json()["query"]["time_utc"].endswith("+00:00")
    assert client.get(path).status_code == 422
    for patch in ({"latitude_deg": "NaN"}, {"longitude_deg": "Infinity"},
                  {"launch_altitude_m": "NaN"}, {"expected_sha256": "wrong"}):
        assert client.get(path, params={**query, **patch}).status_code == 422
    assert app.state.service._db is None
