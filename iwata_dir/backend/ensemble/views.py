"""Small complete trial tables; raw histories remain in immutable run artifacts."""
from collections import Counter
import copy

STATES = ("unstarted", "queued", "running", "landed", "stopped", "invalid_input", "failed", "cancelled", "interrupted")


def counts(rows):
    counter = Counter(r["state"] for r in rows)
    return {"planned": len(rows), **{key: counter[key] for key in STATES}}


def compact(row, fixed, variable, result=None):
    detail = {"trial_id": row["id"], "draw_id": row["draw_id"], "ordinal": row["ordinal"],
              "weight": fixed["weight"], "parameter": None if "weather_window" in fixed else {"id": variable, "value": fixed["value"], "unit": fixed["unit"]},
              "state": row["state"], "attempt": row["attempt"], "run_id": row["run_id"],
              "result_available": row["state"] in {"landed", "stopped"}, "geometry_loaded": result is not None,
              "config_hash": fixed["config_hash"],
              "landing": None, "burst": None, "last_valid_point": None, "stop": None,
              "error": copy.deepcopy(row.get("error")), "result_manifest_hash": row.get("result_manifest_hash")}
    if "weather_window" in fixed:
        detail["weather_window"] = copy.deepcopy(fixed["weather_window"])
    if result is not None:
        detail["landing"] = copy.deepcopy(result["summary"]["landing"]) if result["status"] == "landed" else None
        detail["burst"] = next((copy.deepcopy(e) for e in result["events"] if e["type"] == "burst"), None)
        records = result["records"]
        if records:
            detail["last_valid_point"] = {k: records[-1][k] for k in
                                          ("latitude_deg", "longitude_deg", "altitude_m", "elapsed_s", "phase") if k in records[-1]}
        detail["stop"] = copy.deepcopy(result["stop_reason"])
        detail["summary"] = copy.deepcopy(result["summary"])
    return detail
