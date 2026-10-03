"""HTTP envelopes; physical validation stays in balloon_sim.flight.config."""
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class RunRequest(StrictEnvelope):
    client_request_id: str = Field(min_length=1, max_length=128)
    candidate_id: str = Field(min_length=1, max_length=128)
    candidate_revision: int = Field(ge=0)
    label: str = Field(min_length=1, max_length=200)
    weather_source_id: str = Field(min_length=1, max_length=128)
    config: dict[str, Any]


class Candidate(StrictEnvelope):
    id: str = Field(min_length=1, max_length=128)
    label: str = Field(max_length=200)
    revision: int = Field(ge=0)
    weather_source_id: str
    config: dict[str, Any]
    parent_id: str | None = Field(default=None, min_length=1, max_length=128)
    delay_minutes: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    # Incomplete scientific drafts are saved; execution validates a separate type.
    sampling: dict[str, Any] | None = None
    analysis_mode: Literal["forecast", "historical_windows"] = "forecast"


class SingleResultRef(StrictEnvelope):
    kind: Literal["single_run"]
    run_id: str = Field(min_length=1, max_length=128)


class EnsembleResultRef(StrictEnvelope):
    kind: Literal["ensemble_case"]
    ensemble_id: str = Field(min_length=1, max_length=128)
    snapshot_id: str = Field(min_length=1, max_length=128)
    case_id: str = Field(min_length=1, max_length=128)
    analysis_id: str | None = None


class Project(StrictEnvelope):
    schema_id: Literal["balloon.project/1"] = Field(default="balloon.project/1", alias="schema")
    title: str = Field(max_length=200)
    candidates: list[Candidate]
    compare_run_ids: list[str]
    # None preserves the historical n=1 comparison list as the display authority.
    compare_results: list[SingleResultRef | EnsembleResultRef] | None = None
    # Display state belongs to the project, never to an immutable physical run.
    # The frontend owns its versioned screen-specific structure; finite JSON is
    # checked by ApplicationService alongside incomplete candidate drafts.
    ui_state: dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(StrictEnvelope):
    expected_revision: int = Field(ge=0)
    project: Project
