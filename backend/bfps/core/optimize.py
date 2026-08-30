"""最適化: グリッドサーチ + scipy.optimize リファインフック.

目的関数はプラガブル: MonteCarloResult -> float (小さいほど良い)。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Callable

from .montecarlo import Distributions, MonteCarloResult, run_montecarlo
from .trajectory import FlightParams
from .wind import WindProfile

Objective = Callable[[MonteCarloResult], float]


def distance_to_point(target_lat: float, target_lon: float) -> Objective:
    """平均着地点から目標地点までの距離 [m] を最小化."""

    def _obj(result: MonteCarloResult) -> float:
        dlat = (result.mean_lat - target_lat) * 110574.0
        dlon = (
            (result.mean_lon - target_lon)
            * 111320.0
            * math.cos(math.radians(target_lat))
        )
        return math.hypot(dlat, dlon)

    return _obj


def spread_penalty(weight: float = 1.0) -> Objective:
    """着地分布の広がり (95%楕円長半径) をペナルティ化."""

    def _obj(result: MonteCarloResult) -> float:
        return weight * result.ellipse_95.semi_major_m

    return _obj


def combined(*objectives: Objective) -> Objective:
    def _obj(result: MonteCarloResult) -> float:
        return sum(o(result) for o in objectives)

    return _obj


@dataclass(frozen=True)
class OptimizeCell:
    launch_time: datetime
    ascent_rate_ms: float
    score: float
    mean_lat: float
    mean_lon: float


@dataclass
class OptimizeResult:
    best: OptimizeCell
    grid: list[OptimizeCell]


def grid_search(
    base: FlightParams,
    dists: Distributions,
    profile: WindProfile,
    launch_times: list[datetime],
    ascent_rates: list[float],
    objective: Objective,
    n_per_cell: int = 50,
    seed: int | None = 42,
    dt: float = 20.0,
) -> OptimizeResult:
    """発射時刻 × 上昇率 (≒ガス量) のグリッドサーチ.

    注意 (骨組みの制約): 風プロファイルは発射点で1回取得したものを
    全セルで共有する。発射時刻を大きくずらす場合は本来時刻ごとの
    プロファイル取得が必要 (TODO: profile_fetcherコールバック化)。
    """
    grid: list[OptimizeCell] = []
    for launch_time in launch_times:
        for ascent_rate in ascent_rates:
            params = replace(
                base, launch_time=launch_time, ascent_rate_ms=ascent_rate
            )
            result = run_montecarlo(
                params, dists, profile, n=n_per_cell, seed=seed, dt=dt
            )
            grid.append(
                OptimizeCell(
                    launch_time=launch_time,
                    ascent_rate_ms=ascent_rate,
                    score=objective(result),
                    mean_lat=result.mean_lat,
                    mean_lon=result.mean_lon,
                )
            )

    grid.sort(key=lambda c: c.score)
    return OptimizeResult(best=grid[0], grid=grid)


def refine_scipy(
    base: FlightParams,
    dists: Distributions,
    profile: WindProfile,
    objective: Objective,
    initial_ascent_rate: float,
    n_per_eval: int = 50,
    seed: int | None = 42,
):
    """グリッド最良セルの近傍をNelder-Meadで微調整するフック (骨組み).

    連続変数は上昇率のみ。発射時刻はグリッドで離散探索する前提。
    """
    from scipy.optimize import minimize

    def _f(x):
        params = replace(base, ascent_rate_ms=max(0.5, float(x[0])))
        result = run_montecarlo(params, dists, profile, n=n_per_eval, seed=seed, dt=20.0)
        return objective(result)

    return minimize(
        _f,
        x0=[initial_ascent_rate],
        method="Nelder-Mead",
        options={"maxiter": 30, "xatol": 0.05, "fatol": 100.0},
    )
