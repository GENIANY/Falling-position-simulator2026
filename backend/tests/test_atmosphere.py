import math

import pytest

from bfps.core.atmosphere import (
    altitude_from_pressure,
    density_exponential,
    density_isa,
    pressure_isa,
    temperature_isa,
)


def test_isa_anchors():
    assert density_isa(0) == pytest.approx(1.2250, abs=1e-3)
    assert temperature_isa(0) == pytest.approx(288.15)
    # 対流圏界面
    assert temperature_isa(11000) == pytest.approx(216.65, abs=0.01)
    assert density_isa(11000) == pytest.approx(0.3639, abs=5e-3)
    # 等温層
    assert temperature_isa(15000) == pytest.approx(216.65, abs=0.01)
    # 成層圏
    assert temperature_isa(25000) == pytest.approx(221.65, abs=0.1)


def test_pressure_monotonic_decreasing():
    prev = pressure_isa(0)
    for alt in range(1000, 40001, 1000):
        p = pressure_isa(alt)
        assert p < prev
        prev = p


def test_exponential_matches_formula():
    for z in [0, 5000, 15000, 30000]:
        assert density_exponential(z) == pytest.approx(
            1.2050 * math.exp(-z / 7238.3)
        )


def test_altitude_from_pressure_round_trip():
    for alt in [1000, 5000, 11000, 20000, 24000]:
        p_hpa = pressure_isa(alt) / 100.0
        assert altitude_from_pressure(p_hpa) == pytest.approx(alt, abs=1.0)


def test_open_meteo_ceiling_altitude():
    # 30hPa は およそ 23.5-24.5km
    alt = altitude_from_pressure(30.0)
    assert 23000 < alt < 25000
