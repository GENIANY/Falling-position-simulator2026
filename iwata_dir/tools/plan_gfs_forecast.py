"""Plan one GFS pressure/surface forecast time window from supplied inventory.

Introduced in 0.19.0 for D-151 / ENVIRONMENT_CONTRACT. This is a finite,
offline planning candidate for gfs.pgrb2.0p25: 0..120 h hourly, then
123..384 h every three hours. It does not contact a provider, download,
decode, cache, interpolate, convert heights, or simulate a balloon.

``available`` means the caller reports a file present in an inventory
snapshot, not that its fields, levels, bytes or scientific applicability
have been accepted. Absence means unknown in that snapshot, not proven
nonpublication. The newest run means newest in the supplied snapshot;
the module neither enumerates all provider runs nor proves freshness.

API: plan_gfs_forecast(request, inventory, required_fields=None).
UTC datetimes or JSON timestamps with explicit +00:00 are accepted.
Durations are integer seconds; result timestamps use +00:00. Invalid
declarations raise ForecastPlanError(code, path); a valid but unsupported
request returns status=unavailable and candidate reasons. A supported time
window returns temporal_plan_ready, which is NOT simulation readiness.
The optional required_fields object accepts compose_model's output shape,
preserves consumers, and remains a declaration without a capability check.

CLI reads JSON files and writes JSON to stdout only. It never saves files.
Exit 0: temporal_plan_ready; 2: unavailable; 1: invalid input/read error.
Internal dependency: compose_model.FIELD_UNITS; otherwise standard library.
Tests: tests/test_gfs_forecast_plan.py. Revisit this candidate when actual
inventory discovery, per-field acquisition, or product schedules change.
"""
from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys

if __package__:
    from .compose_model import FIELD_UNITS
else:
    from compose_model import FIELD_UNITS


REQUEST_SCHEMA = "balloon.gfs.forecast_request/1"
INVENTORY_SCHEMA = "balloon.gfs.forecast_inventory/1"
PLAN_SCHEMA = "balloon.gfs.forecast_plan/1"
PRODUCT = "gfs.pgrb2.0p25"
EXPECTED_LEADS = tuple(range(121)) + tuple(range(123, 385, 3))
_UTC_TEXT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?\+00:00\Z")
_MAX_SECONDS = 384 * 3600


class ForecastPlanError(ValueError):
    """An invalid declaration; distinct from missing temporal coverage."""

    def __init__(self, code, path, message):
        self.code, self.path = code, path
        super().__init__(f"{code} at {path}: {message}")


def _object(value, path, required, optional=()):
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise ForecastPlanError("INVALID_OBJECT", path, "expected an object with string keys")
    if set(required) - set(value):
        raise ForecastPlanError("MISSING_KEY", path, str(sorted(set(required) - set(value))))
    if set(value) - set(required) - set(optional):
        raise ForecastPlanError("UNKNOWN_KEY", path, str(sorted(set(value) - set(required) - set(optional))))


def _utc(value, path):
    if isinstance(value, str):
        if not _UTC_TEXT.fullmatch(value):
            raise ForecastPlanError("NON_UTC_TIME", path, "use YYYY-MM-DDTHH:MM:SS[.ffffff]+00:00")
        try:
            value = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ForecastPlanError("INVALID_TIME", path, "invalid calendar date or time") from exc
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise ForecastPlanError("NON_UTC_TIME", path, "an aware UTC datetime is required")
    return value.astimezone(timezone.utc)


def _seconds(value, path, positive):
    # Integer seconds make the duration precision explicit and avoid rounding
    # a small positive float into an apparently exact schedule endpoint.
    if type(value) is not int or value < (1 if positive else 0) or value > _MAX_SECONDS:
        raise ForecastPlanError("INVALID_DURATION", path, "expected integer seconds within 0..1382400 (positive for flight)")
    return value


def _add(time, delta, path):
    try:
        return time + delta
    except OverflowError as exc:
        raise ForecastPlanError("TIME_RANGE_UNSUPPORTED", path, "result exceeds datetime's calendar range") from exc


def _requirements(value):
    if value is None:
        return {"status": "not_provided", "fields": None}
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise ForecastPlanError("INVALID_REQUIREMENTS", "required_fields", "expected compose_model required_fields object")
    for name, requirement in value.items():
        path = "required_fields." + name
        if name not in FIELD_UNITS:
            raise ForecastPlanError("UNKNOWN_FIELD", path, "not in the current composition field catalogue")
        _object(requirement, path, ("unit", "consumers"))
        if requirement["unit"] != FIELD_UNITS[name]:
            raise ForecastPlanError("FIELD_UNIT_MISMATCH", path + ".unit", FIELD_UNITS[name])
        consumers = requirement["consumers"]
        if (not isinstance(consumers, (list, tuple)) or not consumers
                or any(not isinstance(x, str) or not x.strip() for x in consumers)
                or len(set(consumers)) != len(consumers)):
            raise ForecastPlanError("INVALID_REQUIREMENTS", path + ".consumers", "nonempty unique consumer identifiers required")
    return {"status": "declared_only_not_checked_against_data",
            "fields": {name: {"unit": value[name]["unit"], "consumers": list(value[name]["consumers"])}
                       for name in sorted(value)}}


def _inventory(value, as_of):
    _object(value, "inventory", ("schema", "product", "observed_at_utc", "source_id", "runs"))
    if value["schema"] != INVENTORY_SCHEMA or value["product"] != PRODUCT:
        raise ForecastPlanError("UNSUPPORTED_INVENTORY", "inventory", "expected the current GFS 0.25 degree inventory schema/product")
    observed = _utc(value["observed_at_utc"], "inventory.observed_at_utc")
    if observed > as_of:
        raise ForecastPlanError("INVENTORY_AFTER_AS_OF", "inventory.observed_at_utc", "a later snapshot cannot prove availability at as_of")
    if not isinstance(value["source_id"], str) or not value["source_id"].strip():
        raise ForecastPlanError("INVALID_SOURCE", "inventory.source_id", "a nonempty snapshot identifier is required")
    if not isinstance(value["runs"], (list, tuple)):
        raise ForecastPlanError("INVALID_RUNS", "inventory.runs", "expected a list")
    runs, seen = [], set()
    for i, run in enumerate(value["runs"]):
        path = f"inventory.runs[{i}]"
        _object(run, path, ("initialization_time_utc", "entries"))
        init = _utc(run["initialization_time_utc"], path + ".initialization_time_utc")
        if init.hour not in (0, 6, 12, 18) or (init.minute, init.second, init.microsecond) != (0, 0, 0):
            raise ForecastPlanError("INVALID_GFS_CYCLE", path, "cycle must be exactly 00/06/12/18 UTC")
        if init in seen:
            raise ForecastPlanError("DUPLICATE_RUN", path, init.isoformat())
        seen.add(init)
        if not isinstance(run["entries"], (list, tuple)):
            raise ForecastPlanError("INVALID_ENTRIES", path + ".entries", "expected a list")
        entries = {}
        for j, entry in enumerate(run["entries"]):
            ep = f"{path}.entries[{j}]"
            _object(entry, ep, ("lead_hours", "valid_time_utc", "availability"))
            lead = entry["lead_hours"]
            if type(lead) is not int or lead not in EXPECTED_LEADS:
                raise ForecastPlanError("UNEXPECTED_LEAD", ep + ".lead_hours", "not on this product's forecast schedule")
            if lead in entries:
                raise ForecastPlanError("DUPLICATE_LEAD", ep, str(lead))
            valid = _utc(entry["valid_time_utc"], ep + ".valid_time_utc")
            if valid != _add(init, timedelta(hours=lead), ep):
                raise ForecastPlanError("VALID_LEAD_MISMATCH", ep, "valid must equal initialization plus lead")
            if entry["availability"] not in ("available", "not_yet_published"):
                raise ForecastPlanError("UNKNOWN_AVAILABILITY", ep, "use available or not_yet_published; absent leads remain unknown")
            entries[lead] = {"lead_hours": lead, "valid_time_utc": valid.isoformat(),
                             "availability": entry["availability"]}
        runs.append((init, entries))
    return observed, sorted(runs, key=lambda item: item[0], reverse=True)


def _candidate(init, entries, start, end, as_of, observed):
    result = {"initialization_time_utc": init.isoformat(), "run_age_at_as_of_s": (as_of - init).total_seconds(),
              "status": "unavailable", "required_entries": [], "issues": []}
    if init > as_of:
        result["issues"].append({"code": "FUTURE_RUN", "detail": "initialization is later than as_of"})
        return result
    if init > observed:
        result["issues"].append({"code": "RUN_AFTER_INVENTORY_OBSERVATION", "detail": "this snapshot predates initialization"})
        return result
    last = _add(init, timedelta(hours=384), "inventory.run forecast horizon")
    if start < init or end > last:
        result["issues"].append({"code": "WINDOW_OUTSIDE_RUN", "earliest_valid_utc": init.isoformat(),
                                 "latest_valid_utc": last.isoformat()})
        return result
    # Bisect on datetimes, not rounded float lead hours: a microsecond next
    # to a node still requires its real neighboring forecast time.
    axis = [_add(init, timedelta(hours=h), "inventory.run forecast axis") for h in EXPECTED_LEADS]
    left = bisect_right(axis, start) - 1
    right = bisect_left(axis, end)
    for lead in EXPECTED_LEADS[left:right + 1]:
        entry = entries.get(lead)
        item = {"lead_hours": lead, "valid_time_utc": axis[EXPECTED_LEADS.index(lead)].isoformat()}
        if entry is None:
            item["availability"] = "unknown_in_supplied_inventory"
            result["issues"].append({"code": "MISSING_VALID_IN_INVENTORY", "lead_hours": lead,
                                     "valid_time_utc": item["valid_time_utc"]})
        else:
            item["availability"] = entry["availability"]
            if entry["availability"] != "available":
                result["issues"].append({"code": "REPORTED_NOT_YET_PUBLISHED", "lead_hours": lead,
                                         "valid_time_utc": item["valid_time_utc"]})
        result["required_entries"].append(item)
    if not result["issues"]:
        result["status"] = "temporal_inventory_supported"
    return result


def plan_gfs_forecast(request, inventory, required_fields=None):
    """Return a deterministic time-only plan or an explained unavailable result.

    No run mixing or bridging of missing scheduled times is permitted.
    Default selection tries only the latest observed run in this supplied
    inventory, even if incomplete. allow_older_run=True explicitly permits
    newest-to-oldest fallback; every candidate and its reasons is retained.
    The end margin extends the requested duration; it is not landing evidence.
    """
    _object(request, "request", ("schema", "as_of_utc", "launch_time_utc", "flight_duration_s"),
            ("end_margin_s", "allow_older_run"))
    if request["schema"] != REQUEST_SCHEMA:
        raise ForecastPlanError("UNKNOWN_REQUEST_SCHEMA", "request.schema", REQUEST_SCHEMA)
    as_of = _utc(request["as_of_utc"], "request.as_of_utc")
    launch = _utc(request["launch_time_utc"], "request.launch_time_utc")
    duration = _seconds(request["flight_duration_s"], "request.flight_duration_s", True)
    margin = _seconds(request.get("end_margin_s", 0), "request.end_margin_s", False)
    fallback = request.get("allow_older_run", False)
    if type(fallback) is not bool:
        raise ForecastPlanError("INVALID_FALLBACK_POLICY", "request.allow_older_run", "expected a boolean")
    end = _add(launch, timedelta(seconds=duration + margin), "request window")
    fields = _requirements(required_fields)
    observed, runs = _inventory(inventory, as_of)
    candidates = [_candidate(init, entries, launch, end, as_of, observed) for init, entries in runs]
    eligible = [c for c, (init, _) in zip(candidates, runs) if init <= observed and init <= as_of]
    selected = next((c for c in (eligible if fallback else eligible[:1])
                     if c["status"] == "temporal_inventory_supported"), None)
    if selected is not None:
        code = "LATEST_OBSERVED_INVENTORY_RUN" if selected is eligible[0] else "EXPLICIT_OLDER_RUN_FALLBACK"
    elif not eligible:
        code = "NO_OBSERVED_RUNS"
    elif fallback:
        code = "NO_SINGLE_RUN_SUPPORTS_WINDOW"
    else:
        code = "LATEST_OBSERVED_RUN_UNSUPPORTED_FALLBACK_DISABLED"
    return {"schema": PLAN_SCHEMA, "product": PRODUCT,
            "status": "temporal_plan_ready" if selected is not None else "unavailable",
            "request": {"as_of_utc": as_of.isoformat(), "launch_time_utc": launch.isoformat(),
                        "flight_duration_s": duration, "end_margin_s": margin, "allow_older_run": fallback},
            "window": {"start_utc": launch.isoformat(), "end_utc": end.isoformat(), "end_inclusive": True},
            "inventory_context": {"source_id": inventory["source_id"], "observed_at_utc": observed.isoformat(),
                                  "snapshot_age_at_as_of_s": (as_of - observed).total_seconds(),
                                  "scope": "supplied_runs_only_provider_completeness_and_freshness_not_verified"},
            "selection": {"reason": code, "run": deepcopy(selected)}, "candidates": candidates,
            "schedule": {"lead_unit": "h", "expected_lead_hours": list(EXPECTED_LEADS)},
            "model_field_requirements": fields,
            "unresolved_contracts": ["provider_inventory_discovery_and_freshness",
                                     "actual_acquisition_integrity_and_grib_metadata",
                                     "field_level_units_statistics_and_missing_values",
                                     "spatial_vertical_and_surface_support",
                                     "height_conversion_and_terrain_reference",
                                     "weather_interpolation_and_flight_solver"]}


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ForecastPlanError("DUPLICATE_JSON_KEY", key, "JSON object repeats a key")
        result[key] = value
    return result


def _bad_constant(value):
    raise ForecastPlanError("NONFINITE_JSON_NUMBER", "JSON", value)


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_json_object,
                      parse_constant=_bad_constant)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request_json")
    parser.add_argument("inventory_json")
    parser.add_argument("--required-fields", help="JSON object from compose_model(...)[required_fields]")
    args = parser.parse_args(argv)
    try:
        result = plan_gfs_forecast(_read_json(args.request_json), _read_json(args.inventory_json),
                                   _read_json(args.required_fields) if args.required_fields else None)
    except (ForecastPlanError, OSError, ValueError) as exc:
        print(json.dumps({"status": "invalid_input", "code": getattr(exc, "code", "INPUT_READ_ERROR"),
                          "path": getattr(exc, "path", "JSON file"), "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["status"] == "temporal_plan_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
