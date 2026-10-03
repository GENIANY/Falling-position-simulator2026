"""Scientific and identity boundaries of the initial sensitivity/analysis path."""
from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import unittest

from balloon_sim.ensemble import analyze_results, freeze_drawset, resolve_config
from balloon_sim.ensemble.geography import LocalPlane
from balloon_sim.flight.config import FlightError, validate_config


def config():
    return json.loads((Path(__file__).parents[1] / "examples/hokkaido-simple.json").read_text())


def result(points, *, status="landed", landing=(43.0, 141.5)):
    return {"status": status, "config": config(), "records": points,
            "summary": {"landing": {"latitude_deg": landing[0], "longitude_deg": landing[1]} if status == "landed" else None}}


def point(t, phase, height, vertical=1):
    return {"elapsed_s": t, "phase": phase, "latitude_deg": 43.0,
            "longitude_deg": 141.5 + t/100000, "altitude_m": height,
            "eastward_wind_m_s": 10.0, "northward_wind_m_s": 0.0,
            "vertical_speed_m_s": vertical}


def spec(**kw):
    return dict(variable="burst_altitude_m", unit="m", distribution={"family":"uniform", "low":29000, "high":31000},
                reason="Explicit sensitivity interval, not a product probability estimate.", seed=1701, n=16, **kw)


class EnsembleTests(unittest.TestCase):
    def test_realizations_fixed_and_primitive_resolution_keeps_other_inputs(self):
        a, b = freeze_drawset(spec()), freeze_drawset(spec())
        assert a == b and len({d["draw_id"] for d in a["draws"]}) == 16
        assert all(29000 <= d["value"] < 31000 and d["weight"] == 1 for d in a["draws"])
        c = config(); resolved = resolve_config(c, a["variable"], a["draws"][0]["value"])
        expected = validate_config(c); expected["burst"]["altitude_m"] = a["draws"][0]["value"]
        assert resolved == expected and c["burst"]["altitude_m"] == 30000
        with self.assertRaisesRegex(FlightError, "not used"):
            resolve_config(c, "gas_mass_kg", 0.5)


    def test_invalid_draw_is_not_clamped_or_redrawn_and_gas_is_not_postburst_mass(self):
        c = config(); c["ascent"] = {"mode":"isothermal_buoyancy", "gas_mass_kg":0.5, "envelope_mass_kg":1,
                                   "payload_mass_kg":1, "drag_coefficient":0.3}
        c["descent"] = {"mode":"constant_cda", "mass_kg":1.5, "drag_area_m2":1}
        assert resolve_config(c, "gas_mass_kg", 0.6)["descent"]["mass_kg"] == 1.5
        with self.assertRaises(FlightError):
            resolve_config(c, "gas_mass_kg", -0.1)
        s = spec(); s["unit"] = "km"
        with self.assertRaises(FlightError):
            freeze_drawset(s)
        s = spec(); s["reason"] = " "
        with self.assertRaises(FlightError):
            freeze_drawset(s)


    def test_missing_and_empty_history_remain_selected_not_landed(self):
        rows = [{"trial_id":"landed", "result":result([])},
                {"trial_id":"lift-failure", "result":result([], status="stopped")},
                {"trial_id":"cancelled", "result":None}]
        a = analyze_results(rows)
        assert (a["selected_count"], a["completed_count"], a["missing_result_count"], a["history_count"]) == (3, 2, 1, 0)
        assert a["landing"]["n"] == 1
        for b in a["landing"]["bands"]:
            assert b["geometry"]["type"] == "Point" and b["count"] == 1
        assert analyze_results(rows, selected_trial_ids=[])["landing"]["n"] == 0
        with self.assertRaises(ValueError):
            analyze_results(rows, selected_trial_ids=["another-snapshot-trial"])


    def test_line_ties_and_thin_but_real_area(self):
        # Equatorial points are exactly collinear in this local projection.
        rows = [{"trial_id":str(i), "result":result([], landing=(0.0, i * 0.01))} for i in (-2, -1, 1, 2)]
        a = analyze_results(rows)["landing"]
        assert a["rank"] == 1 and a["extent"]["type"] == "LineString"
        assert a["bands"][0]["count"] == 2
        assert a["bands"][1]["count"] == 4 and a["bands"][2]["count"] == 4
        assert a["bands"][1]["geometry"] == a["bands"][2]["geometry"]
        rows[0]["result"]["summary"]["landing"]["latitude_deg"] = 1e-6
        a = analyze_results(rows)["landing"]
        assert a["rank"] == 2 and a["bands"][2]["geometry"]["type"] == "Polygon"


    def test_curved_and_two_lobed_clouds_are_not_declared_lines_by_input_dimension(self):
        plane = LocalPlane(43, 141.5)
        xy = [(-1000, -100), (-900, 100), (-800, -80), (800, 80), (900, -100), (1000, 100)]
        rows = []
        for i, p in enumerate(xy):
            lon, lat = plane.lonlat(p)
            rows.append({"trial_id":str(i), "result":result([], landing=(lat, lon))})
        a = analyze_results(rows)["landing"]
        assert a["rank"] == 2 and a["extent"]["type"] == "Polygon"
        assert all(b["count"] >= b["rank_index"] for b in a["bands"])
        assert "empty space" in " ".join(a["limits"])


    def test_plot_domain_failure_does_not_drop_landed_denominator(self):
        rows = [{"trial_id":"a", "result":result([], landing=(40,179.9))},
                {"trial_id":"b", "result":result([], landing=(40,-179.9))}]
        a = analyze_results(rows)
        assert a["selected_count"] == a["landing"]["n"] == 2
        assert a["landing"]["unavailable_reason"] == "REGIONAL_PLOT_DOMAIN"


    def test_empty_object_is_not_a_completed_result_and_score_tolerance_does_not_expand_point(self):
        with self.assertRaises(ValueError):
            analyze_results([{"trial_id":"bad", "result":{}}])
        plane = LocalPlane(0, 0)
        xs = [-100000, 100000] + [0]*8 + [-0.001, 0.001]
        rows = []
        for i, x in enumerate(xs):
            lon, lat = plane.lonlat((x, 0))
            rows.append({"trial_id":str(i), "result":result([], landing=(lat,lon))})
        band = analyze_results(rows)["landing"]["bands"][0]
        assert band["count"] == 8
        assert band["geometry"]["type"] == "Point"


    def test_phase_boundary_and_termination_never_join_other_flight_or_clamp(self):
        one = [point(0,"ascent",0), point(60,"ascent",100), point(60,"descent",100,-2), point(120,"descent",0,-2)]
        two = [point(0,"ascent",0,3), point(90,"ascent",300,3), point(90,"descent",300,-4), point(180,"descent",0,-4)]
        rows = [{"trial_id":"one", "result":result(one)}, {"trial_id":"two", "result":result(two)}]
        original = deepcopy(rows)
        a = analyze_results(rows)
        assert rows == original
        up = {r["elapsed_s"]: r for r in a["history"]["phases"]["ascent"]}
        down = {r["elapsed_s"]: r for r in a["history"]["phases"]["descent"]}
        assert up[0]["n"] == 2 and up[0]["metrics"]["vertical_speed_m_s"]["mean"] == 2
        assert up[60]["n"] == 2 and down[60]["n"] == 1
        assert down[60]["metrics"]["vertical_speed_m_s"]["mean"] == -2
        assert down[120]["n"] == 2 and down[120]["metrics"]["altitude_m"]["mean"] == 100
        assert down[180]["n"] == 1 and down[180]["metrics"]["altitude_m"]["mean"] == 0
        assert all(r["n"] == 1 for r in a["history"]["phases"]["descent"] if 120 < r["elapsed_s"] <= 180)


    def test_sampling_order_does_not_change_mean_and_selection_uses_identity(self):
        rows = [{"trial_id":"a", "result":result([point(0,"ascent",0),point(120,"ascent",120)])},
                {"trial_id":"b", "result":result([point(0,"ascent",100),point(120,"ascent",220)])}]
        all_ = analyze_results(rows)["history"]
        reverse = analyze_results(list(reversed(rows)))["history"]
        assert all_ == reverse
        chosen = analyze_results(rows, selected_trial_ids=["b"])
        assert chosen["history"]["phases"]["ascent"][0]["metrics"]["altitude_m"]["mean"] == 100


    def test_immediate_burst_duplicate_physical_endpoint_is_accepted_but_conflict_is_not(self):
        launch = point(0,"ascent",100)
        burst = dict(launch, event="burst")
        rows = [{"trial_id":"immediate", "result":result([launch, burst, point(0,"descent",100,-5), point(20,"descent",0,-5)])}]
        before = deepcopy(rows)
        a = analyze_results(rows)
        assert rows == before and a["history"]["phases"]["ascent"][0]["n"] == 1
        rows[0]["result"]["records"][1]["altitude_m"] = 101
        with self.assertRaisesRegex(ValueError, "conflicting"):
            analyze_results(rows)
