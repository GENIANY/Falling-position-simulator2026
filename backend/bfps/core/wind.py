"""風プロバイダ: WindProvider protocol + ConstantWind / OpenMeteoWind.

制約 (正直に書く): Open-Meteoの気圧面データは30hPa (≈23.5-24km) まで。
高高度バルーンのバースト高度 (30-33km) より低いため、上端以遠は
最上層の風を保持して外挿する。該当時は警告を発する。
中期的にはNOAA NOMADSのGFS GRIB直取得か、Tawhiriプロキシで代替する。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

import numpy as np

from .atmosphere import altitude_from_pressure

# Open-Meteoが提供する気圧面 [hPa]
OPEN_METEO_LEVELS = [
    1000, 975, 950, 925, 900, 850, 800, 700, 600, 500,
    400, 300, 250, 200, 150, 100, 70, 50, 30,
]
OPEN_METEO_CEILING_M = 23800.0  # 30hPa相当のおよその高度


class WindProvider(Protocol):
    def wind_at(self, lat: float, lon: float, alt_m: float, t: datetime) -> tuple[float, float]:
        """(u_east_ms, v_north_ms) を返す."""
        ...


@dataclass(frozen=True)
class ConstantWind:
    """テスト・検証用の一様風."""

    u: float = 0.0
    v: float = 0.0

    def wind_at(self, lat: float, lon: float, alt_m: float, t: datetime) -> tuple[float, float]:
        return (self.u, self.v)


def met_to_uv(speed_ms: float, direction_deg: float) -> tuple[float, float]:
    """気象風向 (風が吹いてくる方向, 北=0, 時計回り) → (u東向き, v北向き)."""
    rad = math.radians(direction_deg)
    u = -speed_ms * math.sin(rad)
    v = -speed_ms * math.cos(rad)
    return (u, v)


@dataclass
class WindProfile:
    """高度でソートされた風プロファイル (発射点で1回取得し飛行中は固定)."""

    alts_m: np.ndarray
    u: np.ndarray
    v: np.ndarray
    warnings: list[str] = field(default_factory=list)

    def wind_at(self, lat: float, lon: float, alt_m: float, t: datetime) -> tuple[float, float]:
        # np.interp は範囲外を端値でクランプする (上端以遠は最上層の風を保持)
        return (
            float(np.interp(alt_m, self.alts_m, self.u)),
            float(np.interp(alt_m, self.alts_m, self.v)),
        )

    def perturbed(self, rng: np.random.Generator, std_ms: float) -> "WindProfile":
        """モンテカルロ用: 各層の風に等方ガウス摂動を加えたコピー."""
        return WindProfile(
            alts_m=self.alts_m,
            u=self.u + rng.normal(0.0, std_ms, self.u.shape),
            v=self.v + rng.normal(0.0, std_ms, self.v.shape),
            warnings=list(self.warnings),
        )


async def fetch_openmeteo_profile(
    lat: float, lon: float, t: datetime, *, client=None
) -> WindProfile:
    """Open-Meteoから気圧面風プロファイルを取得 (発射時刻に最も近い1時間分).

    ネットワークを叩くため、テストでは使用しないこと (@pytest.mark.network)。
    """
    import httpx

    hourly_vars: list[str] = []
    for p in OPEN_METEO_LEVELS:
        hourly_vars.append(f"wind_speed_{p}hPa")
        hourly_vars.append(f"wind_direction_{p}hPa")
        hourly_vars.append(f"geopotential_height_{p}hPa")

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(hourly_vars),
        "start_date": t.strftime("%Y-%m-%d"),
        "end_date": t.strftime("%Y-%m-%d"),
        "wind_speed_unit": "ms",
    }
    own_client = client is None
    if own_client:
        client = httpx.AsyncClient(timeout=30)
    try:
        res = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
        res.raise_for_status()
        data = res.json()
    finally:
        if own_client:
            await client.aclose()

    hours: list[str] = data["hourly"]["time"]
    target = t.strftime("%Y-%m-%dT%H:00")
    idx = hours.index(target) if target in hours else 0

    alts, us, vs = [], [], []
    warnings: list[str] = []
    for p in OPEN_METEO_LEVELS:
        speed = data["hourly"].get(f"wind_speed_{p}hPa", [None])[idx]
        direction = data["hourly"].get(f"wind_direction_{p}hPa", [None])[idx]
        height = data["hourly"].get(f"geopotential_height_{p}hPa", [None])[idx]
        if speed is None or direction is None:
            continue
        alt = float(height) if height is not None else altitude_from_pressure(p)
        u, v = met_to_uv(float(speed), float(direction))
        alts.append(alt)
        us.append(u)
        vs.append(v)

    if not alts:
        raise RuntimeError("Open-Meteo returned no usable wind levels")

    order = np.argsort(alts)
    profile = WindProfile(
        alts_m=np.asarray(alts)[order],
        u=np.asarray(us)[order],
        v=np.asarray(vs)[order],
        warnings=warnings,
    )
    profile.warnings.append(
        f"wind data ceiling {profile.alts_m[-1]:.0f} m (Open-Meteo 30hPa); "
        "winds above are held constant"
    )
    return profile
