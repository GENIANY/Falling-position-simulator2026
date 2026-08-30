"""モンテカルロ: 風プロファイル1回取得→N回のインメモリ摂動シミュレーション.

旧フロントエンドの「1サンプル=1 HTTPリクエスト」方式を根本解消する。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .trajectory import FlightParams, simulate
from .wind import WindProfile

CHI2_95_2DOF = 5.991464547107979  # scipy.stats.chi2.ppf(0.95, 2)


@dataclass(frozen=True)
class Distributions:
    ascent_rate_std: float = 0.5  # m/s
    burst_altitude_std: float = 1500.0  # m
    descent_rate_std: float = 0.5  # m/s
    wind_error_std: float = 1.0  # m/s (プロファイル各層への等方摂動)


@dataclass(frozen=True)
class ConfidenceEllipse:
    center_lat: float
    center_lon: float
    semi_major_m: float
    semi_minor_m: float
    bearing_deg: float  # 東基準・反時計回り


@dataclass
class MonteCarloResult:
    landings: np.ndarray  # (N, 2) [lat, lon]
    mean_lat: float
    mean_lon: float
    covariance_enu: np.ndarray  # 2x2 [m^2]
    ellipse_95: ConfidenceEllipse
    percentile_radii_m: dict[int, float]
    flight_time_stats: dict[str, float]
    warnings: list[str] = field(default_factory=list)


M_PER_DEG_LAT = 110574.0
M_PER_DEG_LON_EQ = 111320.0


def run_montecarlo(
    params: FlightParams,
    dists: Distributions,
    profile: WindProfile,
    n: int,
    seed: int | None = None,
    dt: float = 10.0,
) -> MonteCarloResult:
    rng = np.random.default_rng(seed)

    landings = np.empty((n, 2))
    flight_times = np.empty(n)
    warnings: list[str] = list(profile.warnings)

    for i in range(n):
        p = FlightParams(
            launch_lat=params.launch_lat,
            launch_lon=params.launch_lon,
            launch_alt_m=params.launch_alt_m,
            launch_time=params.launch_time,
            ascent_rate_ms=max(
                0.1, params.ascent_rate_ms + rng.normal(0, dists.ascent_rate_std)
            ),
            burst_altitude_m=max(
                1000.0,
                params.burst_altitude_m + rng.normal(0, dists.burst_altitude_std),
            ),
            descent_rate_ms=max(
                0.5, params.descent_rate_ms + rng.normal(0, dists.descent_rate_std)
            ),
            ground_alt_m=params.ground_alt_m,
        )
        wind = (
            profile.perturbed(rng, dists.wind_error_std)
            if dists.wind_error_std > 0
            else profile
        )
        traj = simulate(p, wind, dt=dt)
        landings[i] = traj.landing
        flight_times[i] = traj.flight_time_s

    mean_lat = float(landings[:, 0].mean())
    mean_lon = float(landings[:, 1].mean())

    cos_lat = math.cos(math.radians(mean_lat))
    x = (landings[:, 1] - mean_lon) * M_PER_DEG_LON_EQ * cos_lat
    y = (landings[:, 0] - mean_lat) * M_PER_DEG_LAT
    cov = np.cov(np.vstack([x, y])) if n > 1 else np.zeros((2, 2))

    eigvals, eigvecs = np.linalg.eigh(cov)
    # eigh は昇順: [minor, major]
    major_val, minor_val = float(eigvals[1]), float(eigvals[0])
    major_vec = eigvecs[:, 1]
    bearing = math.degrees(math.atan2(major_vec[1], major_vec[0]))

    k = math.sqrt(CHI2_95_2DOF)
    ellipse = ConfidenceEllipse(
        center_lat=mean_lat,
        center_lon=mean_lon,
        semi_major_m=k * math.sqrt(max(major_val, 0.0)),
        semi_minor_m=k * math.sqrt(max(minor_val, 0.0)),
        bearing_deg=bearing,
    )

    radii = np.sqrt(x**2 + y**2)
    percentile_radii = {
        50: float(np.percentile(radii, 50)),
        90: float(np.percentile(radii, 90)),
        95: float(np.percentile(radii, 95)),
    }

    return MonteCarloResult(
        landings=landings,
        mean_lat=mean_lat,
        mean_lon=mean_lon,
        covariance_enu=cov,
        ellipse_95=ellipse,
        percentile_radii_m=percentile_radii,
        flight_time_stats={
            "mean_s": float(flight_times.mean()),
            "std_s": float(flight_times.std()),
            "min_s": float(flight_times.min()),
            "max_s": float(flight_times.max()),
        },
        warnings=warnings,
    )
