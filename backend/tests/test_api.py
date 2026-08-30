from fastapi.testclient import TestClient

from bfps.main import app

client = TestClient(app)

PROFILE = {
    "launch_latitude": 33.1,
    "launch_longitude": 132.5,
    "launch_altitude": 0,
    "launch_datetime": "2026-08-05T00:00:00Z",
    "ascent_rate": 5.0,
    "burst_altitude": 30000,
    "descent_rate": 5.0,
}


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_simulate_constant_wind():
    res = client.post(
        "/api/simulate",
        json={
            "profile": PROFILE,
            "engine": "native",
            "wind_source": "constant",
            "constant_wind_u": 10.0,
            "constant_wind_v": 0.0,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["flight_time_s"] > 6000
    assert body["landing_longitude"] > 132.5  # 東風で東へ流される
    assert abs(body["landing_latitude"] - 33.1) < 0.01
    assert len(body["trajectory"]) > 10


def test_montecarlo_constant_wind():
    res = client.post(
        "/api/montecarlo",
        json={
            "profile": PROFILE,
            "wind_source": "constant",
            "constant_wind_u": 5.0,
            "n_samples": 30,
            "seed": 1,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert len(body["landings"]) == 30
    assert body["ellipse_95"]["semi_major_m"] > 0
    assert body["percentile_radii_m"]["95"] >= body["percentile_radii_m"]["50"]


def test_montecarlo_rejects_oversized():
    res = client.post(
        "/api/montecarlo",
        json={
            "profile": PROFILE,
            "wind_source": "constant",
            "n_samples": 10000,
        },
    )
    assert res.status_code == 422  # pydantic le=2000


def test_optimize_constant_wind():
    res = client.post(
        "/api/optimize",
        json={
            "profile": PROFILE,
            "wind_source": "constant",
            "constant_wind_u": 5.0,
            "launch_time_offsets_h": [0],
            "ascent_rates": [3.0, 6.0],
            "n_per_cell": 10,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["best"]["ascent_rate"] == 6.0  # 速いほど流されない
    assert len(body["grid"]) == 2
