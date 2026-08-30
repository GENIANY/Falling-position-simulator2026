"""Tawhiri APIプロキシ: 既存フロントエンドと同じリクエスト形式で転送する.

engine="tawhiri" 時の予測経路。native実装の検証基準としても使う。
"""

from __future__ import annotations

from datetime import datetime

import httpx

from ..config import settings


async def predict(
    launch_latitude: float,
    launch_longitude: float,
    launch_altitude: float,
    launch_datetime: datetime,
    ascent_rate: float,
    burst_altitude: float,
    descent_rate: float,
) -> dict:
    lon = launch_longitude if launch_longitude >= 0 else launch_longitude + 360.0
    params = {
        "profile": "standard_profile",
        "launch_latitude": launch_latitude,
        "launch_longitude": lon,
        "launch_altitude": launch_altitude,
        "launch_datetime": launch_datetime.isoformat(),
        "ascent_rate": ascent_rate,
        "burst_altitude": burst_altitude,
        "descent_rate": descent_rate,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.get(settings.tawhiri_url, params=params)
        res.raise_for_status()
        return res.json()
