from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter
import numpy as np

from ..core.montecarlo import Distributions
from ..core.optimize import combined, distance_to_point, grid_search, spread_penalty
from ..core.trajectory import FlightParams
from ..core.wind import ConstantWind, WindProfile, fetch_openmeteo_profile
from ..models.schemas import OptimizeCellOut, OptimizeRequest, OptimizeResponse

router = APIRouter()

# 骨組みの簡略化: MC/最適化は同期実行 (n上限で応答時間を制御)。
# 実行時間が30秒を超える規模になったらジョブキュー+ポーリングへ移行する。


@router.post("/api/optimize", response_model=OptimizeResponse)
async def optimize_endpoint(req: OptimizeRequest) -> OptimizeResponse:
    warnings: list[str] = []
    if req.wind_source == "constant":
        profile = WindProfile(
            alts_m=np.array([0.0, 50000.0]),
            u=np.array([req.constant_wind_u, req.constant_wind_u]),
            v=np.array([req.constant_wind_v, req.constant_wind_v]),
        )
    else:
        profile = await fetch_openmeteo_profile(
            req.profile.launch_latitude,
            req.profile.launch_longitude,
            req.profile.launch_datetime,
        )
        warnings.extend(profile.warnings)
        warnings.append(
            "wind profile fetched once at base launch time and shared across "
            "all launch-time cells (skeleton limitation)"
        )

    lon = req.profile.launch_longitude
    if lon > 180:
        lon -= 360
    base = FlightParams(
        launch_lat=req.profile.launch_latitude,
        launch_lon=lon,
        launch_alt_m=req.profile.launch_altitude,
        launch_time=req.profile.launch_datetime,
        ascent_rate_ms=req.profile.ascent_rate,
        burst_altitude_m=req.profile.burst_altitude,
        descent_rate_ms=req.profile.descent_rate,
    )
    dists = Distributions(
        ascent_rate_std=req.distributions.ascent_rate_std,
        burst_altitude_std=req.distributions.burst_altitude_std,
        descent_rate_std=req.distributions.descent_rate_std,
        wind_error_std=req.distributions.wind_error_std,
    )

    if req.target_latitude is not None and req.target_longitude is not None:
        objective = combined(
            distance_to_point(req.target_latitude, req.target_longitude),
            spread_penalty(0.5),
        )
    else:
        objective = combined(
            distance_to_point(base.launch_lat, base.launch_lon),
            spread_penalty(0.5),
        )

    launch_times = [
        req.profile.launch_datetime + timedelta(hours=h)
        for h in req.launch_time_offsets_h
    ]
    result = grid_search(
        base,
        dists,
        profile,
        launch_times=launch_times,
        ascent_rates=req.ascent_rates,
        objective=objective,
        n_per_cell=req.n_per_cell,
        seed=req.seed,
    )

    def to_out(cell) -> OptimizeCellOut:
        return OptimizeCellOut(
            launch_datetime=cell.launch_time,
            ascent_rate=cell.ascent_rate_ms,
            score=cell.score,
            mean_lat=cell.mean_lat,
            mean_lon=cell.mean_lon,
        )

    return OptimizeResponse(
        best=to_out(result.best),
        grid=[to_out(c) for c in result.grid],
        warnings=warnings,
    )
