"""Finite GFS temporal planning tests; all inventories below are artificial.

Expected leads are chosen from flight windows, not from a network listing.
No success here proves provider availability, decoded fields, altitude
coverage, forecast accuracy, or a working flight solver.
"""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import io
import json
import unittest
from unittest.mock import patch

from tools.compose_model import compose_model, tawhiri_like_spec
from tools.plan_gfs_forecast import (
    ForecastPlanError, INVENTORY_SCHEMA, PRODUCT, REQUEST_SCHEMA,
    _json_object, _bad_constant, main, plan_gfs_forecast,
)


INIT = datetime(2026, 9, 22, tzinfo=timezone.utc)


def stamp(hours=0, seconds=0):
    return (INIT + timedelta(hours=hours, seconds=seconds)).isoformat()


def run(init=INIT, leads=(4, 5, 6)):
    return {"initialization_time_utc": init.isoformat(), "entries": [
        {"lead_hours": h, "valid_time_utc": (init + timedelta(hours=h)).isoformat(), "availability": "available"}
        for h in leads]}


def inventory(*runs, observed=2):
    return {"schema": INVENTORY_SCHEMA, "product": PRODUCT,
            "observed_at_utc": stamp(observed), "source_id": "synthetic:test-input",
            "runs": list(runs) if runs else [run()]}


def request(launch=4, duration=3600, as_of=2, **extra):
    return {"schema": REQUEST_SCHEMA, "as_of_utc": stamp(as_of),
            "launch_time_utc": stamp(launch), "flight_duration_s": duration, **extra}


class ForecastPlanTests(unittest.TestCase):
    def reject(self, code, req=None, inv=None, fields=None):
        with self.assertRaises(ForecastPlanError) as caught:
            plan_gfs_forecast(request() if req is None else req,
                              inventory() if inv is None else inv, fields)
        self.assertEqual(caught.exception.code, code)
        self.assertTrue(caught.exception.path)

    def leads(self, result):
        self.assertEqual(result["status"], "temporal_plan_ready")
        return [e["lead_hours"] for e in result["selection"]["run"]["required_entries"]]

    def test_arbitrary_launch_brackets_whole_flight_and_end_margin(self):
        req = request(4, 5400, end_margin_s=600)
        req["launch_time_utc"] = stamp(4, 17 * 60 + 13)
        result = plan_gfs_forecast(req, inventory(run(leads=(4, 5, 6))))
        self.assertEqual(self.leads(result), [4, 5, 6])
        self.assertEqual(result["window"]["end_utc"], stamp(5, 57 * 60 + 13))
        self.assertEqual(result["selection"]["run"]["run_age_at_as_of_s"], 7200)
        self.assertEqual(result["inventory_context"]["observed_at_utc"], stamp(2))

    def test_exact_endpoints_do_not_require_zero_weight_neighbors(self):
        result = plan_gfs_forecast(request(), inventory(run(leads=(4, 5))))
        self.assertEqual(self.leads(result), [4, 5])

    def test_run_start_endpoint_is_supported(self):
        result = plan_gfs_forecast(request(0, 1), inventory(run(leads=(0, 1))))
        self.assertEqual(self.leads(result), [0, 1])

    def test_positive_microsecond_is_not_rounded_to_endpoint(self):
        req = request(4, 3600)
        req["launch_time_utc"] = "2026-09-22T04:00:00.000001+00:00"
        self.assertEqual(self.leads(plan_gfs_forecast(req, inventory())), [4, 5, 6])

    def test_hourly_to_three_hourly_transition(self):
        req = request(119, 3 * 3600)
        req["launch_time_utc"] = stamp(119, 30 * 60)
        result = plan_gfs_forecast(req, inventory(run(leads=(119, 120, 123))))
        self.assertEqual(self.leads(result), [119, 120, 123])

    def test_window_inside_120_123_interval_uses_real_neighbors(self):
        result = plan_gfs_forecast(request(121.5, 60), inventory(run(leads=(120, 123))))
        self.assertEqual(self.leads(result), [120, 123])

    def test_exact_120_123_interval_needs_no_126(self):
        result = plan_gfs_forecast(request(120, 10800), inventory(run(leads=(120, 123))))
        self.assertEqual(self.leads(result), [120, 123])

    def test_final_three_hour_interval(self):
        result = plan_gfs_forecast(request(381.5, 9000), inventory(run(leads=(381, 384))))
        self.assertEqual(self.leads(result), [381, 384])
        self.assertEqual(result["window"]["end_utc"], stamp(384))

    def test_384_hour_launch_does_not_support_later_flight(self):
        result = plan_gfs_forecast(request(384, 1), inventory(run(leads=(384,))))
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["candidates"][0]["issues"][0]["code"], "WINDOW_OUTSIDE_RUN")

    def test_margin_can_push_flight_outside_horizon(self):
        result = plan_gfs_forecast(request(383, 3600, end_margin_s=1), inventory(run(leads=(381, 384))))
        self.assertEqual(result["status"], "unavailable")

    def test_launch_before_run_is_not_extrapolated(self):
        result = plan_gfs_forecast(request(-.5, 3600), inventory(run(leads=(0, 1))))
        self.assertEqual(result["candidates"][0]["issues"][0]["code"], "WINDOW_OUTSIDE_RUN")

    def test_missing_middle_valid_is_not_bridged(self):
        result = plan_gfs_forecast(request(4, 7200), inventory(run(leads=(4, 6))))
        self.assertEqual(result["status"], "unavailable")
        candidate = result["candidates"][0]
        self.assertEqual([e["lead_hours"] for e in candidate["required_entries"]], [4, 5, 6])
        self.assertEqual(candidate["issues"], [{"code": "MISSING_VALID_IN_INVENTORY", "lead_hours": 5,
                                               "valid_time_utc": stamp(5)}])

    def test_absent_and_explicitly_not_published_are_distinct(self):
        r = run(leads=(4, 6))
        r["entries"][1]["availability"] = "not_yet_published"
        result = plan_gfs_forecast(request(4, 7200), inventory(r))
        self.assertEqual([x["code"] for x in result["candidates"][0]["issues"]],
                         ["MISSING_VALID_IN_INVENTORY", "REPORTED_NOT_YET_PUBLISHED"])

    def test_missing_unneeded_times_do_not_block_window(self):
        result = plan_gfs_forecast(request(), inventory(run(leads=(4, 5))))
        self.assertEqual(self.leads(result), [4, 5])
        self.assertEqual(result["model_field_requirements"]["status"], "not_provided")
        self.assertIn("field_level_units_statistics_and_missing_values", result["unresolved_contracts"])

    def test_latest_observed_run_selected_regardless_of_input_order(self):
        older, newer = run(leads=(8, 9)), run(INIT + timedelta(hours=6), (2, 3))
        for runs in ((older, newer), (newer, older)):
            result = plan_gfs_forecast(request(8, 3600, as_of=8), inventory(*runs, observed=7))
            self.assertEqual(self.leads(result), [2, 3])
            self.assertEqual(result["selection"]["reason"], "LATEST_OBSERVED_INVENTORY_RUN")
            self.assertEqual(result["selection"]["run"]["initialization_time_utc"], stamp(6))

    def test_incomplete_latest_does_not_silently_fallback(self):
        inv = inventory(run(leads=(8, 9)), run(INIT + timedelta(hours=6), (2,)), observed=7)
        result = plan_gfs_forecast(request(8, 3600, as_of=8), inv)
        self.assertIsNone(result["selection"]["run"])
        self.assertEqual(result["selection"]["reason"], "LATEST_OBSERVED_RUN_UNSUPPORTED_FALLBACK_DISABLED")
        self.assertEqual(result["candidates"][1]["status"], "temporal_inventory_supported")

    def test_opt_in_fallback_uses_single_complete_older_run(self):
        inv = inventory(run(leads=(8, 9)), run(INIT + timedelta(hours=6), (2,)), observed=7)
        req = request(8, 3600, as_of=8, allow_older_run=True)
        result = plan_gfs_forecast(req, inv)
        self.assertEqual(self.leads(result), [8, 9])
        self.assertEqual(result["selection"]["reason"], "EXPLICIT_OLDER_RUN_FALLBACK")
        self.assertEqual(result["selection"]["run"]["run_age_at_as_of_s"], 8 * 3600)

    def test_separately_incomplete_runs_are_not_joined(self):
        inv = inventory(run(leads=(9,)), run(INIT + timedelta(hours=6), (2,)), observed=7)
        result = plan_gfs_forecast(request(8, 3600, as_of=8, allow_older_run=True), inv)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["selection"]["reason"], "NO_SINGLE_RUN_SUPPORTS_WINDOW")

    def test_future_run_is_rejected_not_selected_as_latest(self):
        inv = inventory(run(leads=(8, 9)), run(INIT + timedelta(hours=6), (2, 3)))
        result = plan_gfs_forecast(request(8), inv)
        self.assertEqual(self.leads(result), [8, 9])
        self.assertEqual(result["candidates"][0]["issues"][0]["code"], "FUTURE_RUN")

    def test_run_not_yet_initialized_at_snapshot_cannot_claim_availability(self):
        inv = inventory(run(INIT + timedelta(hours=6), (2, 3)), observed=2)
        result = plan_gfs_forecast(request(8, as_of=8), inv)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["candidates"][0]["issues"][0]["code"], "RUN_AFTER_INVENTORY_OBSERVATION")

    def test_later_inventory_cannot_establish_past_availability(self):
        self.reject("INVENTORY_AFTER_AS_OF", inv=inventory(observed=3))

    def test_empty_inventory_and_empty_run_are_diagnosed(self):
        inv = inventory()
        inv["runs"] = []
        result = plan_gfs_forecast(request(), inv)
        self.assertEqual(result["selection"]["reason"], "NO_OBSERVED_RUNS")
        inv["runs"] = [run(leads=())]
        result = plan_gfs_forecast(request(), inv)
        self.assertEqual(len(result["candidates"][0]["issues"]), 2)

    def test_old_snapshot_is_explicit_and_not_global_latest(self):
        result = plan_gfs_forecast(request(8, as_of=8), inventory(run(leads=(8, 9)), observed=1))
        self.assertEqual(result["inventory_context"]["snapshot_age_at_as_of_s"], 7 * 3600)
        self.assertIn("provider_completeness_and_freshness_not_verified", result["inventory_context"]["scope"])
        self.assertEqual(result["selection"]["run"]["run_age_at_as_of_s"], 8 * 3600)

    def test_aware_datetime_input_and_calendar_rollover(self):
        init = datetime(2028, 2, 29, 18, tzinfo=timezone.utc)
        inv = inventory(run(init, (6, 7)))
        inv["observed_at_utc"] = init
        req = request()
        req.update(as_of_utc=init, launch_time_utc=datetime(2028, 3, 1, 0, tzinfo=timezone.utc))
        self.assertEqual(self.leads(plan_gfs_forecast(req, inv)), [6, 7])

    def test_timezone_missing_non_utc_and_ambiguous_text_rejected(self):
        for value in (datetime(2026, 9, 22), "2026-09-22", "2026-09-22T02:00:00",
                      "2026-09-22T11:00:00+09:00", "2026-09-22T02:00:00-00:00",
                      "2026-09-22 02:00:00+00:00", "2026-09-22T02:00:00.0000001+00:00", True, 0):
            with self.subTest(value=value):
                req = request()
                req["as_of_utc"] = value
                self.reject("NON_UTC_TIME", req=req)

    def test_invalid_calendar_and_overflow_have_reasoned_errors(self):
        req = request()
        req["launch_time_utc"] = "2026-02-30T00:00:00+00:00"
        self.reject("INVALID_TIME", req=req)
        req["launch_time_utc"] = "9999-12-31T23:59:59+00:00"
        self.reject("TIME_RANGE_UNSUPPORTED", req=req)

    def test_duration_and_margin_reject_bool_nonfinite_fraction_and_wrong_unit(self):
        for name, bad in (("flight_duration_s", [True, 0, -1, 1.0, .5, float("nan"), float("inf"), "3600", 10**1000]),
                          ("end_margin_s", [False, -1, .1, float("nan"), None])):
            for value in bad:
                with self.subTest(name=name, value_type=type(value).__name__):
                    req = request()
                    req[name] = value
                    self.reject("INVALID_DURATION", req=req)
        self.reject("UNKNOWN_KEY", req={**request(), "duration_hours": 1})
        self.reject("INVALID_FALLBACK_POLICY", req={**request(), "allow_older_run": 1})

    def test_bad_cycle_duplicate_run_duplicate_lead_rejected(self):
        inv = inventory(run(INIT + timedelta(hours=1), (4, 5)))
        self.reject("INVALID_GFS_CYCLE", inv=inv)
        self.reject("DUPLICATE_RUN", inv=inventory(run(), run()))
        self.reject("DUPLICATE_LEAD", inv=inventory(run(leads=(4, 4))))

    def test_unscheduled_leads_and_valid_mismatch_rejected(self):
        for lead in (True, 4.0, -1, 121, 122, 385, 10**1000):
            inv = inventory()
            inv["runs"][0]["entries"][0]["lead_hours"] = lead
            self.reject("UNEXPECTED_LEAD", inv=inv)
        inv = inventory()
        inv["runs"][0]["entries"][0]["valid_time_utc"] = stamp(5)
        self.reject("VALID_LEAD_MISMATCH", inv=inv)

    def test_product_schema_unknown_key_and_availability_rejected(self):
        self.reject("UNKNOWN_REQUEST_SCHEMA", req={**request(), "schema": "future/9"})
        self.reject("UNSUPPORTED_INVENTORY", inv={**inventory(), "product": "gfs.native.atm"})
        self.reject("UNKNOWN_KEY", inv={**inventory(), "latest_is_complete": True})
        inv = inventory()
        inv["runs"][0]["entries"][0]["availability"] = "downloaded_and_verified"
        self.reject("UNKNOWN_AVAILABILITY", inv=inv)

    def test_composition_connection_preserves_requirements_without_capability_claim(self):
        required = compose_model(tawhiri_like_spec(5, 5, 30000))["required_fields"]
        result = plan_gfs_forecast(request(), inventory(), required)
        self.assertEqual(result["model_field_requirements"]["fields"], required)
        self.assertEqual(set(required), {"eastward_wind_m_s", "northward_wind_m_s"})
        self.assertEqual(result["model_field_requirements"]["status"], "declared_only_not_checked_against_data")
        self.assertNotIn("capabilities", result)
        self.assertIn("spatial_vertical_and_surface_support", result["unresolved_contracts"])

    def test_requirement_errors_and_wrong_wind_units_rejected(self):
        self.reject("UNKNOWN_FIELD", fields={"omega": {"unit": "Pa s-1", "consumers": ["a"]}})
        self.reject("FIELD_UNIT_MISMATCH", fields={"geometric_vertical_wind_m_s": {"unit": "Pa s-1", "consumers": ["a"]}})
        for consumers in ([], [True], ["a", "a"], [{}]):
            self.reject("INVALID_REQUIREMENTS", fields={"temperature_k": {"unit": "K", "consumers": consumers}})

    def test_deterministic_detached_output_and_socket_disabled_execution(self):
        req, inv = request(), inventory()
        fields = compose_model(tawhiri_like_spec(5, 5, 30000))["required_fields"]
        before = deepcopy((req, inv, fields))
        with patch("socket.socket", side_effect=AssertionError("network forbidden")), patch("socket.create_connection", side_effect=AssertionError("network forbidden")):
            first = plan_gfs_forecast(req, inv, fields)
            second = plan_gfs_forecast(req, inv, fields)
        self.assertEqual(first, second)
        json.dumps(first, allow_nan=False)
        first["selection"]["run"]["required_entries"][0]["lead_hours"] = 999
        self.assertEqual(first["candidates"][0]["required_entries"][0]["lead_hours"], 4)
        first["model_field_requirements"]["fields"]["eastward_wind_m_s"]["consumers"].append("new")
        self.assertEqual((req, inv, fields), before)

    def test_cli_ready_unavailable_and_invalid_exit_codes(self):
        for req, expected in ((request(), 0), (request(384, 1), 2), ({**request(), "flight_duration_s": True}, 1)):
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch("tools.plan_gfs_forecast._read_json", side_effect=[req, inventory()]), redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(["request.json", "inventory.json"])
            self.assertEqual(code, expected)
            parsed = json.loads(stderr.getvalue() if code == 1 else stdout.getvalue())
            self.assertEqual(parsed["status"], {0: "temporal_plan_ready", 1: "invalid_input", 2: "unavailable"}[expected])

    def test_cli_rejects_duplicate_json_keys_and_nonfinite_constants(self):
        with self.assertRaises(ForecastPlanError) as caught:
            json.loads('{"as_of_utc":1,"as_of_utc":2}', object_pairs_hook=_json_object)
        self.assertEqual(caught.exception.code, "DUPLICATE_JSON_KEY")
        with self.assertRaises(ForecastPlanError) as caught:
            json.loads('{"duration":NaN}', parse_constant=_bad_constant)
        self.assertEqual(caught.exception.code, "NONFINITE_JSON_NUMBER")


if __name__ == "__main__":
    unittest.main()
