"""軌道積分: 固定ステップRK4 (水平は風移流、鉛直は運動学的モデル).

Tawhiri同様の簡略モデル:
- 上昇: 一定速度 ascent_rate
- バースト後の降下: 海面等価降下率を密度スケーリング
    v_desc(z) = descent_rate * sqrt(rho_sl / rho_isa(z))
- 水平: 風速をそのまま移流 (慣性なし)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np

from .atmosphere import RHO0_ISA, density_isa
from .wind import WindProvider

R_EARTH = 6371000.0  # m


@dataclass(frozen=True)
class FlightParams:
    launch_lat: float
    launch_lon: float
    launch_alt_m: float
    launch_time: datetime  # UTC
    ascent_rate_ms: float
    burst_altitude_m: float
    descent_rate_ms: float  # 海面等価
    ground_alt_m: float | None = None  # Noneなら発射高度で着地判定


@dataclass
class Trajectory:
    times_s: np.ndarray
    lats: np.ndarray
    lons: np.ndarray
    alts: np.ndarray
    burst_index: int
    warnings: list[str] = field(default_factory=list)

    @property
    def landing(self) -> tuple[float, float]:
        return (float(self.lats[-1]), float(self.lons[-1]))

    @property
    def flight_time_s(self) -> float:
        return float(self.times_s[-1])


def _descent_rate(z: float, sea_level_rate: float) -> float:
    rho = max(density_isa(max(z, 0.0)), 1e-4)
    return sea_level_rate * math.sqrt(RHO0_ISA / rho)


def simulate(
    params: FlightParams,
    wind: WindProvider,
    dt: float = 10.0,
    max_time_s: float = 6 * 3600 * 4,
) -> Trajectory:
    """上昇→バースト→降下を積分。着地 (高度<=ground) で終了."""
    ground = params.ground_alt_m if params.ground_alt_m is not None else params.launch_alt_m

    t = 0.0
    lat = params.launch_lat
    lon = params.launch_lon
    alt = params.launch_alt_m
    burst = False
    burst_index = -1

    times = [t]
    lats = [lat]
    lons = [lon]
    alts = [alt]

    launch_time = params.launch_time.astimezone(timezone.utc)

    def vertical_rate(z: float, bursted: bool) -> float:
        if not bursted:
            return params.ascent_rate_ms
        return -_descent_rate(z, params.descent_rate_ms)

    def horizontal_derivative(la: float, lo: float, z: float, tt: float) -> tuple[float, float]:
        u, v = wind.wind_at(la, lo, z, launch_time)
        dlat = math.degrees(v / R_EARTH)
        dlon = math.degrees(u / (R_EARTH * math.cos(math.radians(la))))
        return (dlat, dlon)

    while t < max_time_s:
        # RK4 (水平)。鉛直は区分一定なのでオイラーで厳密
        w = vertical_rate(alt, burst)
        k1 = horizontal_derivative(lat, lon, alt, t)
        k2 = horizontal_derivative(
            lat + k1[0] * dt / 2, lon + k1[1] * dt / 2, alt + w * dt / 2, t + dt / 2
        )
        k3 = horizontal_derivative(
            lat + k2[0] * dt / 2, lon + k2[1] * dt / 2, alt + w * dt / 2, t + dt / 2
        )
        k4 = horizontal_derivative(lat + k3[0] * dt, lon + k3[1] * dt, alt + w * dt, t + dt)

        lat += (dt / 6) * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        lon += (dt / 6) * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        alt += w * dt
        t += dt

        if not burst and alt >= params.burst_altitude_m:
            alt = params.burst_altitude_m
            burst = True
            burst_index = len(times)

        times.append(t)
        lats.append(lat)
        lons.append(lon)
        alts.append(alt)

        if burst and alt <= ground:
            break

    warnings: list[str] = []
    if t >= max_time_s:
        warnings.append("max simulation time reached before landing")

    return Trajectory(
        times_s=np.asarray(times),
        lats=np.asarray(lats),
        lons=np.asarray(lons),
        alts=np.asarray(alts),
        burst_index=burst_index,
        warnings=warnings,
    )
