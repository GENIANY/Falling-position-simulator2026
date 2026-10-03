"""Common elapsed-time, phase-separated summaries of immutable flight records."""
import math

import numpy as np

from ..flight.config import EARTH_RADIUS_M

UNITS = {"altitude_m": "m ASL", "east_km": "km", "north_km": "km",
         "distance_km": "km", "horizontal_speed_m_s": "m/s",
         "vertical_speed_m_s": "m/s", "latitude_deg": "degree",
         "longitude_deg": "degree"}


def _metric_records(result):
    records = result["records"]
    if not records:
        return {}
    t = np.array([r["elapsed_s"] for r in records], dtype=float)
    if not np.all(np.isfinite(t)) or np.any(np.diff(t) < 0):
        raise ValueError("records must have finite nondecreasing elapsed times")
    lat = np.radians([r["latitude_deg"] for r in records])
    lon = np.unwrap(np.radians([r["longitude_deg"] for r in records]))
    origin = result["config"]["launch"]
    lat0, lon0 = np.radians([origin["latitude_deg"], origin["longitude_deg"]])
    dl = (lon - lon0 + np.pi) % (2 * np.pi) - np.pi
    north = np.cos(lat0) * np.sin(lat) - np.sin(lat0) * np.cos(lat) * np.cos(dl)
    east = np.cos(lat) * np.sin(dl)
    distance_from_origin = EARTH_RADIUS_M * np.arctan2(np.hypot(east, north),
        np.sin(lat0) * np.sin(lat) + np.cos(lat0) * np.cos(lat) * np.cos(dl)) / 1000
    bearing = np.arctan2(east, north)
    h = np.sin(np.diff(lat) / 2)**2 + np.cos(lat[:-1])*np.cos(lat[1:])*np.sin(np.diff(lon) / 2)**2
    distance = np.r_[0.0, np.cumsum(2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(np.clip(h, 0, 1))) / 1000)]
    u = np.array([r.get("eastward_wind_m_s", np.nan) for r in records], dtype=float)
    v = np.array([r.get("northward_wind_m_s", np.nan) for r in records], dtype=float)
    metrics = {
        "altitude_m": np.array([r["altitude_m"] for r in records], dtype=float),
        "east_km": distance_from_origin * np.sin(bearing),
        "north_km": distance_from_origin * np.cos(bearing),
        "distance_km": distance, "horizontal_speed_m_s": np.hypot(u, v),
        "vertical_speed_m_s": np.array([r.get("vertical_speed_m_s", np.nan) for r in records], dtype=float),
        "latitude_deg": np.degrees(lat), "longitude_deg": np.degrees(lon),
    }
    phases = {}
    for phase in ("ascent", "descent"):
        indices = np.array([i for i, r in enumerate(records) if r["phase"] == phase], dtype=int)
        if not len(indices):
            continue
        # The kernel can emit launch and immediate-burst records at t=0 in
        # ascent. Identical physical values are one analysis endpoint; retain
        # the original records/events, and reject contradictory duplicates.
        unique = []
        for index in indices:
            if unique and t[index] == t[unique[-1]]:
                if any(not np.array_equal(np.array(a[index]), np.array(a[unique[-1]]), equal_nan=True)
                       for a in metrics.values()):
                    raise ValueError("conflicting values at the same time within a phase")
            else:
                unique.append(index)
        indices = np.array(unique, dtype=int)
        times = t[indices]
        phases[phase] = {"times": times, "metrics": {k: a[indices] for k, a in metrics.items()}}
    return {"end": float(t[-1]), "phases": phases}


def history_analysis(items):
    """Interpolate within a phase only; never extend a terminated trial.

    The curve represents available phase records at each elapsed time, including
    phase/flight endpoints. Its membership changes; it is not a simulated flight.
    Population quantiles are unweighted NumPy linear sample quantiles.
    """
    data = [_metric_records(i["result"]) for i in items if i["result"] and i["result"]["records"]]
    end = max((d["end"] for d in data), default=0)
    size = min(241, max(2, math.ceil(end / 60) + 1))
    grid = set(np.linspace(0, end, size).tolist()) if data else set()
    for d in data:
        for phase in d["phases"].values():
            grid.update([float(phase["times"][0]), float(phase["times"][-1])])
    times = sorted(grid)
    output = {"method": "elapsed-phase-linear/1", "band": [0.1, 0.9],
              "quantile_method": "numpy.linear", "grid_s": times, "units": UNITS,
              "history_count": len(data), "population": "selected_completed_phase_records",
              "phases": {"ascent": [], "descent": []},
              "limits": ["mean position is not a simulated trajectory; time-varying membership",
                         "phase endpoints included; ascent/descent endpoint counts must not be added",
                         "termination endpoint included; no values after it; wind distributions separately exclude landed trials",
                         "no interpolation across phases or beyond termination",
                         "horizontal displacement uses the flight kernel spherical radius",
                         "cumulative horizontal distance is the sum of accepted-record great-circle segments"]}
    for name in ("ascent", "descent"):
        for time in times:
            values = {k: [] for k in UNITS}
            count = 0
            for d in data:
                phase = d["phases"].get(name)
                if not phase or time > d["end"]:
                    continue
                t = phase["times"]
                if time < t[0] or time > t[-1]:
                    continue
                count += 1
                for metric, ys in phase["metrics"].items():
                    value = float(np.interp(time, t, ys))
                    if math.isfinite(value):
                        values[metric].append(value)
            stats = {}
            for metric, xs in values.items():
                low, high = np.quantile(xs, [0.1, 0.9], method="linear").tolist() if xs else (None, None)
                stats[metric] = {"mean": float(np.mean(xs)) if xs else None,
                                 "low": low, "high": high, "n": len(xs)}
            output["phases"][name].append({"elapsed_s": time, "n": count, "metrics": stats})
    return output
