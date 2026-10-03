"""Bounded public weather requests; no caller-controlled URL or filesystem path."""
from typing import Literal

from pydantic import Field

from ..contracts import StrictEnvelope


class InventoryRefresh(StrictEnvelope):
    run_utc: str | None = None
    run_limit: int = Field(default=2, ge=1, le=4)


class CenterRegion(StrictEnvelope):
    kind: Literal["center"]
    latitude_deg: float = Field(ge=-85, le=85, allow_inf_nan=False)
    longitude_deg: float = Field(ge=-180, le=180, allow_inf_nan=False)
    half_width_km: float = Field(gt=0, le=2000, allow_inf_nan=False)
    half_height_km: float = Field(gt=0, le=2000, allow_inf_nan=False)


class BoundsRegion(StrictEnvelope):
    kind: Literal["bounds"]
    west: float = Field(ge=-180, le=360, allow_inf_nan=False)
    east: float = Field(ge=-180, le=360, allow_inf_nan=False)
    south: float = Field(ge=-90, le=90, allow_inf_nan=False)
    north: float = Field(ge=-90, le=90, allow_inf_nan=False)


class CandidateWindow(StrictEnvelope):
    candidate_id: str = Field(min_length=1, max_length=128)
    launch_time_utc: str
    latitude_deg: float = Field(gt=-90, lt=90, allow_inf_nan=False)
    longitude_deg: float = Field(ge=-180, le=180, allow_inf_nan=False)
    max_duration_s: float = Field(gt=0, le=1382400, allow_inf_nan=False)


class WeatherPlanRequest(StrictEnvelope):
    inventory_id: str = Field(min_length=1, max_length=128)
    run_utc: str
    region: CenterRegion | BoundsRegion = Field(discriminator="kind")
    candidate_windows: list[CandidateWindow] = Field(min_length=1, max_length=256)
    end_margin_s: float = Field(default=0, ge=0, le=86400, allow_inf_nan=False)
    max_bytes: int = Field(default=50_000_000, ge=1024, le=50_000_000)
    max_memory_bytes: int = Field(default=268_435_456, ge=16_777_216, le=536_870_912)


class AcquisitionRequest(StrictEnvelope):
    plan_id: str = Field(min_length=1, max_length=128)
    client_request_id: str = Field(min_length=1, max_length=128)


class GroundQuery(StrictEnvelope):
    """Read one saved field at a declared launch point; not a flight request."""
    expected_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    time_utc: str
    latitude_deg: float = Field(gt=-90, lt=90, allow_inf_nan=False)
    longitude_deg: float = Field(ge=-180, le=180, allow_inf_nan=False)
    launch_altitude_m: float = Field(gt=-6371000, allow_inf_nan=False)
