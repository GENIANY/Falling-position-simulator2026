"""Small input contract independent of HTTP, SQL and application storage."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

ADAPTER_VERSION = "jra3q-halfmonth-summary/3"
STATISTICS_VERSION = "gaussian-pooled-wind/3"


class ClimateError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ClimateError("CLIMATE_INPUT", f"{name} must be finite.")
    return float(value)


@dataclass(frozen=True)
class Bounds:
    west: float
    east: float
    south: float
    north: float

    def __post_init__(self):
        for key in ("west", "east", "south", "north"):
            object.__setattr__(self, key, finite_number(getattr(self, key), key))
        if not (-180 <= self.west <= self.east <= 180 and -90 <= self.south <= self.north <= 90):
            raise ClimateError("CLIMATE_BOUNDS", "Use ordered, non-wrapping native-grid bounds.")

    def as_dict(self):
        return {k: getattr(self, k) for k in ("west", "east", "south", "north")}


@dataclass(frozen=True)
class ClimateQuery:
    source_id: str
    level_id: int
    bounds: Bounds | None = None
    grain: str = "half"
    hours_utc: tuple[int, ...] | None = None
    rose_cell_id: int | None = None

    def __post_init__(self):
        if not isinstance(self.source_id, str) or not self.source_id:
            raise ClimateError("CLIMATE_INPUT", "A registered source_id is required.")
        if isinstance(self.level_id, bool) or not isinstance(self.level_id, int):
            raise ClimateError("CLIMATE_INPUT", "level_id must be an integer native level ID.")
        if self.bounds is not None and not isinstance(self.bounds, Bounds):
            raise ClimateError("CLIMATE_INPUT", "bounds must be Bounds or null.")
        if self.grain != "half":
            raise ClimateError("CLIMATE_UNSUPPORTED", "This source supports UTC half-month summaries only.")
        if self.rose_cell_id is not None and (type(self.rose_cell_id) is not int or self.rose_cell_id < 0):
            raise ClimateError("CLIMATE_INPUT", "rose_cell_id must be a nonnegative integer native cell ID.")
        if self.hours_utc is not None:
            h = self.hours_utc
            if (not isinstance(h, (list, tuple)) or not h or
                    any(type(v) is not int or v not in (0, 6, 12, 18) for v in h) or len(h) != len(set(h))):
                raise ClimateError("CLIMATE_INPUT", "hours_utc must select unique native hours from 0/6/12/18.")
            object.__setattr__(self, "hours_utc", tuple(sorted(h)) if len(h) < 4 else None)

    @classmethod
    def from_mapping(cls, value: Mapping):
        if not isinstance(value, Mapping):
            raise ClimateError("CLIMATE_INPUT", "Expected a query object.")
        unknown = set(value) - {"source_id", "level_id", "bounds", "grain", "hours_utc", "rose_cell_id"}
        if unknown:
            raise ClimateError("CLIMATE_UNSUPPORTED", "Unsupported query fields: " + ", ".join(sorted(unknown)))
        if "source_id" not in value or "level_id" not in value:
            raise ClimateError("CLIMATE_INPUT", "source_id and level_id are required.")
        bounds = value.get("bounds")
        if bounds is not None:
            if not isinstance(bounds, Mapping) or set(bounds) != {"west", "east", "south", "north"}:
                raise ClimateError("CLIMATE_INPUT", "bounds needs exactly west/east/south/north.")
            bounds = Bounds(**bounds)
        return cls(value["source_id"], value["level_id"], bounds, value.get("grain", "half"),
                   value.get("hours_utc"), value.get("rose_cell_id"))

    def as_dict(self):
        result = {"source_id": self.source_id, "level_id": self.level_id,
                "bounds": self.bounds.as_dict() if self.bounds else None, "grain": self.grain}
        if self.hours_utc is not None:
            result["hours_utc"] = list(self.hours_utc)
        if self.rose_cell_id is not None:
            result["rose_cell_id"] = self.rose_cell_id
        return result
