"""Strict execution requests, separate from incomplete candidate drafts."""
from typing import Any, Literal
from pydantic import Field
from backend.contracts import StrictEnvelope


class Uniform(StrictEnvelope):
    family: Literal["uniform"]
    low: float = Field(allow_inf_nan=False)
    high: float = Field(allow_inf_nan=False)


class Sampling(StrictEnvelope):
    variable: Literal["gas_mass_kg", "burst_altitude_m", "reference_descent_speed_m_s"]
    unit: Literal["kg", "m", "m/s"]
    distribution: Uniform
    reason: str = Field(min_length=1, max_length=2000)
    seed: int = Field(ge=0, le=2**32-1)
    n: int = Field(ge=1, le=256)


class Case(StrictEnvelope):
    case_id: str = Field(min_length=1, max_length=128)
    candidate_id: str = Field(min_length=1, max_length=128)
    candidate_revision: int = Field(ge=0)
    label: str = Field(min_length=1, max_length=200)
    parent_case_id: str | None = None
    delay_minutes: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    config: dict[str, Any]


class PlanRequest(StrictEnvelope):
    client_request_id: str = Field(min_length=1, max_length=128)
    label: str = Field(min_length=1, max_length=200)
    weather_source_id: str = Field(min_length=1, max_length=128)
    sampling: Sampling
    cases: list[Case] = Field(min_length=1, max_length=256)


class HistoricalWindow(StrictEnvelope):
    window_id: str = Field(min_length=1, max_length=128)
    label: str = Field(min_length=1, max_length=200)
    weather_source_id: str | None = Field(default=None, min_length=1, max_length=128)
    launch_time_utc: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=1, max_length=2000)


class HistoricalPlanRequest(StrictEnvelope):
    """Explicit original-date fields, not draws from half-month moments."""
    mode: Literal["historical_windows"]
    client_request_id: str = Field(min_length=1, max_length=128)
    label: str = Field(min_length=1, max_length=200)
    windows: list[HistoricalWindow] = Field(min_length=1, max_length=256)
    reason: str = Field(min_length=1, max_length=2000)
    selection_context: dict[str, Any] = Field(default_factory=dict)
    cases: list[Case] = Field(min_length=1, max_length=256)


class SubmitRequest(StrictEnvelope):
    client_request_id: str = Field(min_length=1, max_length=128)
    plan_id: str = Field(min_length=1, max_length=128)
    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class RetryRequest(StrictEnvelope):
    client_request_id: str = Field(min_length=1, max_length=128)
    trial_ids: list[str] = Field(max_length=256)


class CancelRequest(StrictEnvelope):
    client_request_id: str = Field(min_length=1, max_length=128)


class AnalysisRequest(StrictEnvelope):
    client_request_id: str = Field(min_length=1, max_length=128)
    snapshot_id: str = Field(min_length=1, max_length=128)
    case_id: str = Field(min_length=1, max_length=128)
    selected_trial_ids: list[str] | None = Field(default=None, max_length=256)
    # Finite provenance only; geographic membership is the frontend's predicate.
    region_set: dict[str, Any] | None = None
    selection_origin: Literal["manual", "frontend-region-classifier"] = "manual"
    classifier_version: str | None = Field(default=None, max_length=200)
