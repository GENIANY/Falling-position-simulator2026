"""Definitions applied to stored moments, with no invented raw observations."""
from __future__ import annotations

import calendar
import math
from .contracts import ClimateError, finite_number

ROUNDING_RELATIVE_TOLERANCE = 1e-6  # Source u/v/s are stored as FLOAT.


def vector_summary(mean_u, mean_v, mean_speed):
    u = finite_number(mean_u, "mean_u")
    v = finite_number(mean_v, "mean_v")
    speed = finite_number(mean_speed, "mean_speed")
    if speed < 0:
        raise ClimateError("CLIMATE_VALUES", "Mean scalar speed cannot be negative.")
    length = math.hypot(u, v)
    tolerance = ROUNDING_RELATIVE_TOLERANCE * max(1., speed)
    if length > speed + tolerance or (speed == 0 and length != 0):
        raise ClimateError("CLIMATE_VALUES", "Vector mean exceeds scalar mean beyond FLOAT roundoff.")
    return {"mean_u": u, "mean_v": v, "mean_speed": speed,
            "constancy": min(1., length / speed) if speed else None,
            "from_deg": (math.degrees(math.atan2(u, v)) + 180.) % 360. if length else None}


def combine_cells(cells):
    """Gaussian spatial average at one timebin/level, with equal time support.

    cells contain mean_u/mean_v/mean_speed, weight and time_count. This does
    not average cell constancies or treat space-time observations as independent.
    """
    cells = list(cells)
    if not cells:
        raise ClimateError("CLIMATE_EMPTY_REGION", "No native grid centers are selected.")
    counts = set()
    for row in cells:
        n = row["time_count"]
        if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
            raise ClimateError("CLIMATE_COUNTS", "Time counts must be positive integers.")
        counts.add(n)
        weight = finite_number(row["weight"], "weight")
        if weight <= 0:
            raise ClimateError("CLIMATE_WEIGHTS", "Gaussian weights must be positive.")
        vector_summary(row["mean_u"], row["mean_v"], row["mean_speed"])
    if len(counts) != 1:
        raise ClimateError("CLIMATE_COUNTS", "Unequal time support across cells is unsupported.")
    total = math.fsum(row["weight"] for row in cells)
    means = [math.fsum(row[key] * row["weight"] for row in cells) / total
             for key in ("mean_u", "mean_v", "mean_speed")]
    output = vector_summary(*means)
    output["pooled_constancy"] = output.pop("constancy")
    output.update(time_count=counts.pop(), cell_count=len(cells),
                  spatial_mean_speed_range=max(r["mean_speed"] for r in cells)-min(r["mean_speed"] for r in cells))
    return output


def utc_half_months(first_year=2016, last_year=2025):
    """Expected UTC day support, not conversion of a JST selection."""
    result = []
    for month in range(1, 13):
        last_days = [calendar.monthrange(year, month)[1] for year in range(first_year, last_year + 1)]
        for half in (1, 2):
            start = 1 if half == 1 else 16
            ends = [15 for _ in last_days] if half == 1 else last_days
            days = sum(end - start + 1 for end in ends)
            result.append({"timebin_id": (month-1)*2+half-1, "month": month, "bin": half,
                           "start_day": start, "end_day_min": min(ends), "end_day_max": max(ends),
                           "n_days_total": days, "n_analyses_expected": days*4})
    return result
