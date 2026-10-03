"""Freeze explicit original-date weather windows against common vehicle cases.

This makes no climatological sampling claim. Missing/unsupported windows stay in
the complete trial ledger with no physical result; they are never redrawn.
"""
import copy
from datetime import timedelta

from balloon_sim.environment.fields import WeatherError, _utc
from balloon_sim.flight.config import FlightError, validate_config
from backend.errors import ServiceError
from backend.storage import digest, utc_now
from .planning import MAX_TRIALS, capabilities


def build_historical_plan(identity, request, sources, source_snapshot):
    windows = request["windows"]
    if len(windows) * len(request["cases"]) > MAX_TRIALS:
        raise ServiceError(422, "ENSEMBLE_LIMIT", "Total cases times windows must not exceed 256.")
    if len({w["window_id"] for w in windows}) != len(windows):
        raise ServiceError(422, "DUPLICATE_WINDOW", "Original weather window IDs must be unique.")
    if not request["reason"].strip() or any(not w["reason"].strip() for w in windows):
        raise ServiceError(422, "WINDOW_REASON", "Record why these original dates were selected.")
    if len({c["case_id"] for c in request["cases"]}) != len(request["cases"]) or len({c["candidate_id"] for c in request["cases"]}) != len(request["cases"]):
        raise ServiceError(422, "DUPLICATE_CASE", "Case and candidate IDs must be unique.")
    # Delays belong to the forecast family path. Historical times are owned by
    # the window ledger; disallow a second, ambiguous owner in this first mode.
    if any(c["parent_case_id"] is not None or c["delay_minutes"] is not None for c in request["cases"]):
        raise ServiceError(422, "HISTORICAL_DELAY_UNSUPPORTED", "Use independent common-vehicle cases; each historical window owns its launch UTC.")
    try:
        cases = [{**c, "submitted_config": copy.deepcopy(c["config"]),
                  "resolved_base_config": validate_config(c["config"]),
                  "parameter_activity": "fixed_vehicle"} for c in request["cases"]]
        for case in cases:
            vehicle = copy.deepcopy(case["resolved_base_config"])
            vehicle["launch"].pop("time_utc")
            case["base_config_hash"] = digest(case["resolved_base_config"])
            case["common_vehicle_hash"] = digest(vehicle)
        original_times = [_utc(w["launch_time_utc"]) for w in windows]
    except (FlightError, WeatherError) as exc:
        raise ServiceError(422, exc.code, str(exc)) from exc
    # Different labels/source IDs must not silently double one realization's
    # weight. A distinct release of the same analysis is still the same date.
    if len(set(original_times)) != len(original_times):
        raise ServiceError(422, "DUPLICATE_ORIGINAL_TIME", "Select each original launch UTC once.")
    ledger, trials, starts, ends = [], [], [], []
    for ordinal, (window, start) in enumerate(zip(windows, original_times), 1):
        source = sources.get(window["weather_source_id"])
        snapshot = copy.deepcopy(source["snapshot"]) if source else None
        error = None
        if source is None:
            error = {"code": "HISTORICAL_WINDOW_UNAVAILABLE", "message": "The requested original-date field is not registered; this window remains in the target ledger."}
        elif snapshot.get("time_kind") != "analysis_valid_utc":
            raise ServiceError(422, "NOT_HISTORICAL_ANALYSIS", "Historical windows require a source with original analysis UTC, not a forecast or aggregate.")
        row = {**window, "launch_time_utc": start.isoformat(), "ordinal": ordinal,
               "weather_snapshot": snapshot, "availability": "unavailable" if error else "registered"}
        ledger.append(row)
        for case in cases:
            config = copy.deepcopy(case["resolved_base_config"])
            config["launch"]["time_utc"] = start.isoformat()
            end = start + timedelta(seconds=config["integration"]["max_duration_s"])
            starts.append(start); ends.append(end)
            preflight = copy.deepcopy(error)
            if snapshot:
                times, bounds = snapshot["valid_times_utc"], snapshot["bounds"]
                launch = config["launch"]
                if start < _utc(times[0]) or end > _utc(times[-1]):
                    preflight = {"code": "WEATHER_WINDOW_UNSUPPORTED", "message": "Original field does not cover launch plus the full declared flight duration."}
                elif not (bounds["lat"][0] <= launch["latitude_deg"] <= bounds["lat"][1] and bounds["lon"][0] <= launch["longitude_deg"] <= bounds["lon"][1]):
                    preflight = {"code": "WEATHER_ORIGIN_UNSUPPORTED", "message": "Launch point is outside this original field; its climatic region does not supply flight support."}
            trials.append({"case_id": case["case_id"], "draw_id": window["window_id"], "ordinal": ordinal,
                           "weight": 1, "value": None, "unit": None,
                           "weather_window": row, "weather_snapshot": snapshot,
                           "config": config if preflight is None else None,
                           "config_hash": digest(config) if preflight is None else None,
                           "preflight_error": preflight})
    drawset = {"mode": "historical_windows", "windows": ledger, "weighting": "equal_explicit_windows",
               "reason": request["reason"], "selection_context": request["selection_context"]}
    hashed = digest(drawset)
    missing = sum(t["config"] is None for t in trials)
    sampling = {"mode": "historical_windows", "variable": "original_weather_window", "n": len(windows),
                "reason": request["reason"], "interpretation": "explicit_historical_windows",
                "pairing": "same_original_weather_window", "weighting": "equal_explicit_windows"}
    collection = {"id": "historical-" + hashed, "label": "明示した原日時の気象窓", "kind": "historical_window_set",
                  "schema": "balloon.weather-window-selection/1", "sha256": hashed,
                  "valid_times_utc": [], "members": [w["weather_snapshot"] for w in ledger if w["weather_snapshot"]]}
    plan = {"schema": "balloon.ensemble.plan/1", "mode": "historical_windows", "plan_id": identity,
            "created_at": utc_now(), "label": request["label"], "submitted_input": request,
            "status": "ready" if missing < len(trials) else "unavailable",
            "drawset_id": hashed, "drawset_hash": hashed, "drawset": drawset, "sampling": sampling,
            "draws": [{"draw_id": w["window_id"], "ordinal": w["ordinal"], "weather_window": w} for w in ledger],
            "draw_count": len(windows), "case_count": len(cases), "trial_count": len(trials),
            "invalid_trial_count": missing, "runnable_trial_count": len(trials) - missing,
            "weather_realization_id": hashed, "weather_snapshot": collection,
            "weather_windows": ledger, "source_snapshot": source_snapshot,
            "resolver_version": "original-utc-common-vehicle-v1", "cases": cases, "trials": trials,
            "blockers": [] if missing < len(trials) else [{"code": "NO_RUNNABLE_WINDOWS", "message": "No original window supports the requested flight inputs."}],
            "required_window": {"start": min(starts).isoformat(), "end": max(ends).isoformat()},
            "warnings": [{"code": "EXPLICIT_WINDOWS_ONLY", "message": "Equal-weight explicit dates, not a representative seasonal sample or a calibrated future landing probability."}],
            "selection_context": request["selection_context"], "limits": capabilities(),
            "cost": {"planned_physical_trials": len(trials) - missing, "time_seconds": None,
                     "storage_bytes": None, "basis": "Not measured for this plan."}}
    plan["plan_hash"] = digest(plan)
    return plan
