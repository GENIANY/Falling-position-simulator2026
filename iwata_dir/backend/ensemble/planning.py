"""Freeze physical input rows once; numerical sampling remains in the core."""
import copy
from datetime import timedelta
from balloon_sim.flight.config import FlightError, validate_config
from balloon_sim.environment.fields import _utc
from balloon_sim.ensemble.sampling import VARIABLES
from backend.errors import ServiceError
from backend.storage import digest, utc_now

MAX_TRIALS = 256
MAX_ACTIVE = 4
MAX_HISTORY_BYTES = 64 * 1024 * 1024


def capabilities():
    return {"schema": "balloon.ensemble.capabilities/1", "max_trials_per_ensemble": MAX_TRIALS,
            "max_active_ensembles": MAX_ACTIVE, "max_ensemble_queued_runs": 1,
            "max_history_analysis_result_bytes": MAX_HISTORY_BYTES,
            "history_limit_note": "Sum of selected result.json bytes; not an RSS guarantee. Landing summaries remain available above this limit.",
            "variables": [{"variable": key, "unit": value[0], "section": value[1], "mode": value[2]}
                          for key, value in VARIABLES.items()],
            "interpretation": "assumed_sensitivity", "pairing": "same_physical_value",
            "limits_scope": "Initial local deployment resource limits, not scientific limits."}


def build_plan(identity, request, weather_snapshot, source_snapshot):
    from balloon_sim.ensemble.sampling import freeze_drawset, resolve_config
    sampling = request["sampling"]
    if sampling["n"] * len(request["cases"]) > MAX_TRIALS:
        raise ServiceError(422, "ENSEMBLE_LIMIT", "Total cases times draws must not exceed 256; no partial plan was accepted.")
    unit, section, mode, _ = VARIABLES[sampling["variable"]]
    if sampling["unit"] != unit:
        raise ServiceError(422, "ENSEMBLE_UNIT", "Use the declared physical unit for the selected variable.")
    if not sampling["reason"].strip():
        raise ServiceError(422, "ENSEMBLE_REASON", "The assumed sensitivity range needs a reason.")
    try:
        drawset = freeze_drawset(sampling)
        cases = []
        for case in request["cases"]:
            base = validate_config(case["config"])
            if base[section]["mode"] != mode:
                raise ServiceError(422, "ENSEMBLE_VARIABLE_UNSUPPORTED",
                                   f"Case {case['case_id']} does not use {sampling['variable']}; choose a shared active input.")
            cases.append({**case, "submitted_config": copy.deepcopy(case["config"]),
                          "resolved_base_config": base, "base_config_hash": digest(base),
                          "parameter_activity": "active"})
    except FlightError as exc:
        raise ServiceError(422, exc.code, str(exc)) from exc
    by_id = {c["case_id"]: c for c in cases}
    if len(by_id) != len(cases) or len({c["candidate_id"] for c in cases}) != len(cases):
        raise ServiceError(422, "DUPLICATE_CASE", "Case and candidate IDs must be unique.")
    for case in cases:
        parent_id = case["parent_case_id"]
        if (parent_id is None) != (case["delay_minutes"] is None):
            raise ServiceError(422, "INVALID_DELAY_PARENT", "A delay requires an explicit parent and minutes.")
        seen = {case["case_id"]}
        current = parent_id
        while current is not None:
            if current not in by_id or current in seen:
                raise ServiceError(422, "INVALID_DELAY_PARENT", "Missing or cyclic ensemble parent.")
            seen.add(current)
            current = by_id[current]["parent_case_id"]
        if parent_id is not None:
            parent = by_id[parent_id]["resolved_base_config"]
            child = case["resolved_base_config"]
            expected = _utc(parent["launch"]["time_utc"]) + timedelta(minutes=case["delay_minutes"])
            if _utc(child["launch"]["time_utc"]) != expected:
                raise ServiceError(422, "DELAY_TIME_MISMATCH", "A delay case must use its parent's exact launch plus the declared delay.")
            for part in ("launch", "ascent", "burst", "descent", "integration"):
                a, b = copy.deepcopy(parent[part]), copy.deepcopy(child[part])
                if part == "launch":
                    a.pop("time_utc"); b.pop("time_utc")
                if a != b:
                    raise ServiceError(422, "DELAY_INPUT_MISMATCH", "A dependent delay may only change launch time; use a separate comparison case for model changes.")
    blockers, starts, ends, trials = [], [], [], []
    valid_times = weather_snapshot["valid_times_utc"]
    for case in cases:
        start = _utc(case["resolved_base_config"]["launch"]["time_utc"])
        end = start + timedelta(seconds=case["resolved_base_config"]["integration"]["max_duration_s"])
        starts.append(start); ends.append(end)
        if start < _utc(valid_times[0]) or end > _utc(valid_times[-1]):
            blockers.append({"code": "WEATHER_WINDOW_UNSUPPORTED", "case_id": case["case_id"],
                             "message": "The fixed field must support the full declared flight duration."})
        for ordinal, draw in enumerate(drawset["draws"], 1):
            config, error = None, None
            try:
                config = resolve_config(case["resolved_base_config"], sampling["variable"], draw["value"])
            except FlightError as exc:
                error = {"code": exc.code, "message": str(exc)}
            trials.append({"case_id": case["case_id"], "draw_id": draw["draw_id"], "ordinal": ordinal,
                           "weight": draw["weight"], "value": draw["value"], "unit": sampling["unit"],
                           "config": config, "config_hash": digest(config) if config is not None else None,
                           "preflight_error": error})
    invalid = sum(t["config"] is None for t in trials)
    if invalid == len(trials):
        blockers.append({"code": "NO_RUNNABLE_TRIALS", "message": "Every realized input failed validation; no resampling was performed."})
    plan = {"schema": "balloon.ensemble.plan/1", "plan_id": identity, "created_at": utc_now(),
            "label": request["label"], "submitted_input": request, "status": "unavailable" if blockers else "ready",
            "drawset_id": drawset["drawset_id"], "drawset_hash": digest(drawset), "drawset": drawset,
            "sampling": {**sampling, "interpretation": "assumed_sensitivity", "pairing": "same_physical_value"},
            "draws": [{**d, "ordinal": i, "variable": sampling["variable"], "unit": sampling["unit"]}
                      for i, d in enumerate(drawset["draws"], 1)],
            "draw_count": sampling["n"], "case_count": len(cases), "trial_count": len(trials),
            "invalid_trial_count": invalid, "runnable_trial_count": len(trials)-invalid,
            "weather_realization_id": digest(weather_snapshot), "weather_snapshot": weather_snapshot,
            "source_snapshot": source_snapshot, "resolver_version": drawset["resolver_version"],
            "cases": cases, "trials": trials, "blockers": blockers,
            "required_window": {"start": min(starts).isoformat(), "end": max(ends).isoformat()},
            "warnings": [{"code": "ASSUMED_SENSITIVITY", "message": "An assumed equipment sensitivity range in one fixed weather field, not calibrated forecast uncertainty."}],
            "limits": capabilities(), "cost": {"planned_physical_trials": len(trials)-invalid,
                  "time_seconds": None, "storage_bytes": None, "basis": "Not yet measured for this plan."}}
    plan["plan_hash"] = digest(plan)
    return plan
