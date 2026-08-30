from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, HTTPException

from ..core.montecarlo import Distributions, run_montecarlo
from ..core.trajectory import FlightParams, simulate
from ..core.wind import ConstantWind, WindProfile, fetch_openmeteo_profile
from ..models.schemas import (
    MonteCarloRequest,
    MonteCarloResponse,
    SimulateRequest,
    SimulateResponse,
    TrajectoryPointOut,
    EllipseOut,
)
from ..services import tawhiri

router = APIRouter()


def _params_from_profile(p) -> FlightParams:
    lon = p.launch_longitude
    if lon > 180:
        lon -= 360
    return FlightParams(
        launch_lat=p.launch_latitude,
        launch_lon=lon,
        launch_alt_m=p.launch_altitude,
        launch_time=p.launch_datetime,
        ascent_rate_ms=p.ascent_rate,
        burst_altitude_m=p.burst_altitude,
        descent_rate_ms=p.descent_rate,
    )


async def _wind_for_request(req) -> tuple[object, list[str]]:
    if req.wind_source == "constant":
        return ConstantWind(req.constant_wind_u, req.constant_wind_v), []
    profile = await fetch_openmeteo_profile(
        req.profile.launch_latitude,
        req.profile.launch_longitude,
        req.profile.launch_datetime,
    )
    return profile, list(profile.warnings)


@router.post("/api/simulate", response_model=SimulateResponse)
async def simulate_endpoint(req: SimulateRequest) -> SimulateResponse:
    if req.engine == "tawhiri":
        data = await tawhiri.predict(
            req.profile.launch_latitude,
            req.profile.launch_longitude,
            req.profile.launch_altitude,
            req.profile.launch_datetime,
            req.profile.ascent_rate,
            req.profile.burst_altitude,
            req.profile.descent_rate,
        )
        points: list[TrajectoryPointOut] = []
        t0 = None
        for stage in data["prediction"]:
            for pt in stage["trajectory"]:
                from datetime import datetime as _dt

                ts = _dt.fromisoformat(pt["datetime"].replace("Z", "+00:00"))
                if t0 is None:
                    t0 = ts
                lon = pt["longitude"]
                if lon > 180:
                    lon -= 360
                points.append(
                    TrajectoryPointOut(
                        latitude=pt["latitude"],
                        longitude=lon,
                        altitude=pt["altitude"],
                        time_s=(ts - t0).total_seconds(),
                    )
                )
        if not points:
            raise HTTPException(502, "empty Tawhiri response")
        ascent_len = len(data["prediction"][0]["trajectory"])
        return SimulateResponse(
            trajectory=points,
            landing_latitude=points[-1].latitude,
            landing_longitude=points[-1].longitude,
            burst_index=ascent_len - 1,
            flight_time_s=points[-1].time_s,
            warnings=[],
        )

    wind, warnings = await _wind_for_request(req)
    params = _params_from_profile(req.profile)
    traj = simulate(params, wind, dt=req.dt)
    step = max(1, len(traj.times_s) // 500)  # レスポンス点数を間引き
    points = [
        TrajectoryPointOut(
            latitude=float(traj.lats[i]),
            longitude=float(traj.lons[i]),
            altitude=float(traj.alts[i]),
            time_s=float(traj.times_s[i]),
        )
        for i in range(0, len(traj.times_s), step)
    ]
    return SimulateResponse(
        trajectory=points,
        landing_latitude=traj.landing[0],
        landing_longitude=traj.landing[1],
        burst_index=traj.burst_index // step,
        flight_time_s=traj.flight_time_s,
        warnings=warnings + traj.warnings,
    )


@router.post("/api/montecarlo", response_model=MonteCarloResponse)
async def montecarlo_endpoint(req: MonteCarloRequest) -> MonteCarloResponse:
    wind, warnings = await _wind_for_request(req)
    # ConstantWindの場合も摂動可能な形式に揃える
    if isinstance(wind, ConstantWind):
        import numpy as np

        wind = WindProfile(
            alts_m=np.array([0.0, 50000.0]),
            u=np.array([wind.u, wind.u]),
            v=np.array([wind.v, wind.v]),
        )
    params = _params_from_profile(req.profile)
    dists = Distributions(
        ascent_rate_std=req.distributions.ascent_rate_std,
        burst_altitude_std=req.distributions.burst_altitude_std,
        descent_rate_std=req.distributions.descent_rate_std,
        wind_error_std=req.distributions.wind_error_std,
    )
    result = run_montecarlo(params, dists, wind, n=req.n_samples, seed=req.seed)
    return MonteCarloResponse(
        landings=[(float(la), float(lo)) for la, lo in result.landings],
        mean_lat=result.mean_lat,
        mean_lon=result.mean_lon,
        ellipse_95=EllipseOut(
            center_lat=result.ellipse_95.center_lat,
            center_lon=result.ellipse_95.center_lon,
            semi_major_m=result.ellipse_95.semi_major_m,
            semi_minor_m=result.ellipse_95.semi_minor_m,
            bearing_deg=result.ellipse_95.bearing_deg,
        ),
        percentile_radii_m=result.percentile_radii_m,
        flight_time_stats=result.flight_time_stats,
        warnings=warnings + result.warnings,
    )
