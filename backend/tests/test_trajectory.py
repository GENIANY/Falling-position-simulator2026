from datetime import datetime, timezone

import pytest

from bfps.core.trajectory import FlightParams, simulate
from bfps.core.wind import ConstantWind, met_to_uv

BASE = FlightParams(
    launch_lat=33.1,
    launch_lon=132.5,
    launch_alt_m=0.0,
    launch_time=datetime(2026, 8, 5, 0, 0, tzinfo=timezone.utc),
    ascent_rate_ms=5.0,
    burst_altitude_m=30000.0,
    descent_rate_ms=5.0,
)


def test_no_wind_lands_at_launch_point():
    traj = simulate(BASE, ConstantWind(0, 0), dt=10)
    lat, lon = traj.landing
    assert lat == pytest.approx(BASE.launch_lat, abs=1e-9)
    assert lon == pytest.approx(BASE.launch_lon, abs=1e-9)
    assert traj.burst_index > 0
    assert traj.alts.max() == pytest.approx(30000.0, abs=60)


def test_eastward_wind_drifts_east_by_closed_form():
    u = 10.0
    traj = simulate(BASE, ConstantWind(u, 0), dt=10)
    lat, lon = traj.landing
    # 東西ドリフト: u * 総飛行時間 / (R cos(lat))
    import math

    expected_dlon = math.degrees(
        u * traj.flight_time_s / (6371000.0 * math.cos(math.radians(BASE.launch_lat)))
    )
    assert lon - BASE.launch_lon == pytest.approx(expected_dlon, rel=0.01)
    assert lat == pytest.approx(BASE.launch_lat, abs=1e-6)


def test_ascent_time_matches_kinematics():
    traj = simulate(BASE, ConstantWind(0, 0), dt=10)
    # 上昇時間 = 30000/5 = 6000s
    burst_time = traj.times_s[traj.burst_index]
    assert burst_time == pytest.approx(6000, abs=30)


def test_descent_faster_at_altitude():
    """降下は高高度ほど速い (密度スケーリング) → 総降下時間 < 等速仮定."""
    traj = simulate(BASE, ConstantWind(0, 0), dt=10)
    descent_time = traj.flight_time_s - traj.times_s[traj.burst_index]
    uniform_descent_time = 30000.0 / 5.0
    assert descent_time < uniform_descent_time * 0.8


def test_met_to_uv_conventions():
    # 北風 (dir=0, 北から吹く) → v は南向き (負)
    u, v = met_to_uv(10.0, 0.0)
    assert u == pytest.approx(0.0, abs=1e-9)
    assert v == pytest.approx(-10.0)
    # 西風 (dir=270, 西から吹く) → u は東向き (正)
    u, v = met_to_uv(10.0, 270.0)
    assert u == pytest.approx(10.0)
    assert v == pytest.approx(0.0, abs=1e-9)
