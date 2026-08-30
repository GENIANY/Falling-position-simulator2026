from datetime import datetime, timezone

import numpy as np
import pytest

from bfps.core.montecarlo import Distributions, run_montecarlo
from bfps.core.optimize import distance_to_point, grid_search
from bfps.core.trajectory import FlightParams
from bfps.core.wind import WindProfile

BASE = FlightParams(
    launch_lat=33.1,
    launch_lon=132.5,
    launch_alt_m=0.0,
    launch_time=datetime(2026, 8, 5, 0, 0, tzinfo=timezone.utc),
    ascent_rate_ms=5.0,
    burst_altitude_m=30000.0,
    descent_rate_ms=5.0,
)


def uniform_profile(u=5.0, v=0.0) -> WindProfile:
    return WindProfile(
        alts_m=np.array([0.0, 50000.0]),
        u=np.array([u, u]),
        v=np.array([v, v]),
    )


def test_seed_reproducibility():
    prof = uniform_profile()
    dists = Distributions()
    a = run_montecarlo(BASE, dists, prof, n=30, seed=1, dt=30)
    b = run_montecarlo(BASE, dists, prof, n=30, seed=1, dt=30)
    assert np.allclose(a.landings, b.landings)


def test_zero_std_collapses_to_single_point():
    prof = uniform_profile()
    dists = Distributions(
        ascent_rate_std=0, burst_altitude_std=0, descent_rate_std=0, wind_error_std=0
    )
    r = run_montecarlo(BASE, dists, prof, n=10, seed=2, dt=30)
    assert np.allclose(r.landings, r.landings[0])
    assert r.ellipse_95.semi_major_m == pytest.approx(0.0, abs=1e-6)


def test_ellipse_shrinks_with_smaller_std():
    prof = uniform_profile()
    wide = run_montecarlo(
        BASE, Distributions(burst_altitude_std=3000), prof, n=60, seed=3, dt=30
    )
    narrow = run_montecarlo(
        BASE, Distributions(burst_altitude_std=300), prof, n=60, seed=3, dt=30
    )
    assert narrow.ellipse_95.semi_major_m < wide.ellipse_95.semi_major_m


def test_grid_search_finds_known_optimum():
    """東風5m/sで発射地点回帰を目的にすると、遅い上昇率ほど流される
    → 最速上昇率が最良になるはず (合成ケース)."""
    prof = uniform_profile(u=5.0)
    dists = Distributions(wind_error_std=0)
    result = grid_search(
        BASE,
        dists,
        prof,
        launch_times=[BASE.launch_time],
        ascent_rates=[2.0, 4.0, 7.0],
        objective=distance_to_point(BASE.launch_lat, BASE.launch_lon),
        n_per_cell=10,
        seed=4,
        dt=30,
    )
    assert result.best.ascent_rate_ms == 7.0
    # スコアは上昇率に対して単調減少
    scores = {c.ascent_rate_ms: c.score for c in result.grid}
    assert scores[7.0] < scores[4.0] < scores[2.0]
