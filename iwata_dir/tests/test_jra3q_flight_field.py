"""Offline JRA flight binding: independent values, strict support and phase stops.

Only the test fixture builder imports the preserved 0.18 prototype. Runtime
field/storage/flight code must consume normalized bytes without that dependency.
Agreement with the prototype is supplemented by analytic/Decimal/raw-row oracles.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
import builtins
import importlib.util
import json
import math
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from balloon_sim.environment.bundle import WeatherField
from balloon_sim.environment.fields import WeatherError
from balloon_sim.environment.jra3q import Jra3qModelField, PRODUCT, SCHEMA, full_pressure_pa
from balloon_sim.environment.model_levels import ModelLevelField
from balloon_sim.environment.storage import load_weather, write_bundle
from balloon_sim.flight.trajectory import simulate

ROOT = Path(__file__).resolve().parents[1]
START = datetime(2024, 1, 1, tzinfo=timezone.utc)
RADIUS = 6_371_000.0
U, V = "eastward_wind_m_s", "northward_wind_m_s"
T, Q, P = "temperature_k", "specific_humidity_kg_kg", "pressure_pa"
ALL_FIELDS = (U, V, P, T, Q)


def geometric(h):
    # Independent spelling of the documented spherical inverse, not a call to
    # the production conversion whose input convention is being tested.
    return RADIUS * h / (RADIUS - h)


def observed_fixture():
    spec = importlib.util.spec_from_file_location(
        "jra_prototype_for_flight_tests", ROOT / "tools/normalize_jra3q_model_fixture.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    old = module.load_fixture(ROOT)
    # to_dict explicitly remains a diagnostic format. This test constructs the
    # new interchange schema rather than teaching runtime to load old tools.
    bundle = {
        "schema": SCHEMA, "product": PRODUCT,
        "axes": {"time_utc": [t.isoformat() for t in old.times],
                 "model_level": list(old.levels), "latitude_deg": list(old.latitudes),
                 "longitude_deg": list(old.longitudes)},
        "fields": {"geopotential_height_gpm": old.heights,
                   **{name: data for name, data in old.fields.items() if name != P}},
        "surface": {"pressure_pa": old.surface_pressure,
                    "geopotential_height_gpm": old.surface_height},
        "hybrid": {"a_half_pa": old.provenance["half_coefficients_pa"],
                   "b_half": old.provenance["half_coefficients_dimensionless"]},
        "metadata": deepcopy(old.provenance),
    }
    return old, json.loads(json.dumps(bundle, allow_nan=False))


def affine_columns():
    """Independent affine formulas with moving, column-specific height axes."""
    arrays = {name: [] for name in ("h", P, T, U, V, Q)}
    for t in range(2):
        for data in arrays.values():
            data.append([])
        for k in range(3):
            for data in arrays.values():
                data[t].append([])
            for j in range(2):
                for data in arrays.values():
                    data[t][k].append([])
                for i in range(2):
                    h = 100 + 1000*k + 20*t + 50*j + 100*i
                    values = {"h": h, P: 100000-20*h+4*t+6*j+8*i,
                              T: 270+2*t+3*j+4*i+.005*h,
                              U: 5+t+j+i+.001*h, V: -3+2*t-j+i-.002*h,
                              Q: .001+.0001*t+.0002*j+.0003*i+.000001*h}
                    for name, value in values.items():
                        arrays[name][t][k][j].append(value)
    return {"times": [START, START+timedelta(hours=6)], "latitudes": [34, 36],
            "longitudes": [136, 138], "levels": [1, 2, 3],
            "heights": arrays.pop("h"), "pressures": arrays.pop(P), "fields": arrays,
            "surface_pressure": [[[101000]*2 for _ in range(2)] for _ in range(2)],
            "surface_height": [[[0]*2 for _ in range(2)] for _ in range(2)],
            "metadata": {"fixture_id": "analytic-not-an-observation"}}


def query(field, *, time=START+timedelta(hours=3), lat=35, lon=137, h=1000, fields=ALL_FIELDS):
    return field.sample(time, lat, lon, geometric(h), fields=fields)


def short_config():
    return {"schema": "balloon.flight.config/1",
            "launch": {"time_utc": "2024-01-01T02:17:13+00:00",
                       "latitude_deg": 34.838688086410954, "longitude_deg": 137.0625,
                       "altitude_m": 311.6637155690019768},
            "ascent": {"mode": "constant_speed", "speed_m_s": 5},
            "burst": {"mode": "altitude", "altitude_m": 30000},
            "descent": {"mode": "rated_speed", "reference_speed_m_s": 5,
                        "density_model": "exponential", "scale_height_m": 8400},
            "integration": {"max_step_s": 10, "max_duration_s": 60,
                            "event_tolerance_s": .001}}


class OfflineCase(unittest.TestCase):
    def setUp(self):
        for name in ("socket.socket", "socket.create_connection"):
            block = patch(name, side_effect=AssertionError("network forbidden"))
            block.start()
            self.addCleanup(block.stop)

    def reject(self, code, call):
        with self.assertRaises(WeatherError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)


class ColumnContractTests(OfflineCase):
    def test_affine_fields_and_column_pressure_have_independent_values(self):
        field = ModelLevelField(**affine_columns())
        result = query(field)
        for name, expected in {P: 80009, T: 279.5, U: 7.5, V: -4, Q: .0023}.items():
            self.assertAlmostEqual(result[name], expected, places=10)
        node = query(field, time=START, lat=36, lon=138, h=250)
        self.assertAlmostEqual(node[P], 95014, places=9)
        self.assertEqual(result["ground_altitude_m"], 0)
        self.assertIn("height_linear_pressure", result["quality"])

    def test_strict_surface_gap_and_higher_terrain_column_do_not_extend(self):
        field = ModelLevelField(**affine_columns())
        for h, code in ((0, "HEIGHT_OUT_OF_RANGE"), (50, "HEIGHT_OUT_OF_RANGE"),
                        (-1, "BELOW_MODEL_SURFACE"), (150, "HEIGHT_OUT_OF_RANGE")):
            with self.subTest(h=h):
                self.reject(code, lambda: query(field, h=h))
        data = affine_columns()
        data["surface_height"][0][1][1] = 1200
        field = ModelLevelField(**data)
        # Mean terrain is only 150 gpm; being above it does not authorize a
        # contributing underground column or the GFS terrain-clamp policy.
        self.assertAlmostEqual(field.ground_altitude(START+timedelta(hours=3), 35, 137), geometric(150))
        self.reject("BELOW_MODEL_SURFACE", lambda: query(field))

    def test_missing_coordinate_or_surface_support_rejects_wind_only(self):
        cases = (("surface_pressure", (0, 0, 0), "MISSING_SURFACE_SUPPORT"),
                 ("surface_height", (0, 0, 0), "MISSING_SURFACE_SUPPORT"),
                 ("heights", (0, 1, 0, 0), "MISSING_HEIGHT_SUPPORT"),
                 ("pressures", (0, 0, 0, 0), "MISSING_DATA"))
        for name, indices, code in cases:
            with self.subTest(name=name):
                data = affine_columns()
                target = data[name]
                for index in indices[:-1]:
                    target = target[index]
                target[indices[-1]] = None
                self.reject(code, lambda: query(ModelLevelField(**data), fields=(U, V)))

    def test_missing_q_is_not_dry_air_and_zero_weight_support_is_unused(self):
        data = affine_columns()
        data["fields"][Q][1][0][1][1] = None
        field = ModelLevelField(**data)
        node = query(field, time=START, lat=34, lon=136, h=100)
        self.assertAlmostEqual(node[Q], .0011)
        self.assertAlmostEqual(query(field, fields=(U, V))[U], 7.5)
        self.reject("MISSING_DATA", lambda: query(field))
        del data["fields"][Q]
        absent = ModelLevelField(**data)
        query(absent, fields=(U, V))
        self.reject("MISSING_CAPABILITY", lambda: query(absent))

    def test_equivalent_longitude_does_not_make_region_periodic_or_extend_it(self):
        data = affine_columns()
        data["longitudes"] = [339, 341]
        field = ModelLevelField(**data)
        self.assertEqual(query(field, lon=-20), query(field, lon=340))
        self.assertEqual(field.ground_altitude(START, 35, -20), field.ground_altitude(START, 35, 340))
        for lon in (338, 342, -22, -18, 1060):
            with self.subTest(lon=lon):
                self.reject("LONGITUDE_OUT_OF_RANGE", lambda: query(field, lon=lon))

    def test_simmons_burridge_matches_decimal_not_half_pressure_average(self):
        for lower, upper in ((100000, 90000), (100000, 99999.999), (100, 20)):
            with self.subTest(lower=lower, upper=upper), localcontext() as context:
                context.prec = 60
                a, b = Decimal(str(lower)), Decimal(str(upper))
                expected = float(((a*a.ln()-b*b.ln())/(a-b)-1).exp())
                result = full_pressure_pa([lower, upper, 0])
                self.assertAlmostEqual(result[0], expected, places=8)
                self.assertEqual(result[1], upper/2)
        self.assertGreater(abs(full_pressure_pa([100000, 90000, 0])[0]-95000), 40)
        for bad in ([100, 100, 0], [100, 200, 0], [100, -1, 0], [100, 20, 1], [100, float("nan"), 0]):
            with self.subTest(bad=bad):
                with self.assertRaises(WeatherError):
                    full_pressure_pa(bad)

    def test_constant_wind_columns_match_analytic_spherical_flight(self):
        data = affine_columns()
        for t in range(2):
            for k in range(3):
                for j in range(2):
                    data["fields"][U][t][k][j] = [20, 20]
                    data["fields"][V][t][k][j] = [0, 0]
        config = short_config()
        config["launch"].update(time_utc="2024-01-01T03:00:00+00:00", latitude_deg=35,
                                longitude_deg=137, altitude_m=1000)
        result = simulate(config, ModelLevelField(**data))
        self.assertEqual(result["stop_reason"]["code"], "MAX_DURATION")
        last = result["records"][-1]
        delta = 20/(5*math.cos(math.radians(35))) * math.log((RADIUS+1300)/(RADIUS+1000))
        self.assertAlmostEqual(last["longitude_deg"], 137+math.degrees(delta), delta=4e-9)
        self.assertEqual(last["latitude_deg"], 35)
        self.assertAlmostEqual(last["altitude_m"], 1300, places=9)


class ObservedJraFlightTests(OfflineCase):
    @classmethod
    def setUpClass(cls):
        cls.old, cls.bundle = observed_fixture()

    def test_old_query_agreement_at_native_and_arbitrary_times_all_fields(self):
        field = Jra3qModelField(self.bundle)
        for time in (START, START+timedelta(hours=6), START+timedelta(hours=2, minutes=17, seconds=13)):
            for z in (311.663715569002, 30000):
                with self.subTest(time=time, geometric_m=z):
                    h = RADIUS*z/(RADIUS+z)
                    expected = self.old.sample(time_utc=time, latitude_degrees=34.8,
                                               longitude_degrees=137, geopotential_height_gpm=h,
                                               required_fields=ALL_FIELDS)["values"]
                    actual = field.sample(time, 34.8, 137, z, fields=ALL_FIELDS)
                    for name in ALL_FIELDS:
                        self.assertTrue(math.isclose(actual[name], expected[name], rel_tol=2e-13, abs_tol=2e-11),
                                        (name, actual[name], expected[name]))
        self.assertEqual(field.metadata["time_kind"], "analysis_valid_utc")
        self.assertIn("no extrapolation", field.metadata["surface_policy"])

    def test_direct_original_row_and_independent_30000gpm_values(self):
        raw = json.loads((ROOT/"references/jra3q_model_fixture/source_bundle.json").read_bytes())
        def original(short):
            text = raw["sources"][f"jra-{short}-cell"]["body_utf8"]
            return float(re.search(r"^\[0\]\[50\]\[1\], ([^\n]+)", text, re.M)[1].split(",")[0])
        field = Jra3qModelField(self.bundle)
        node = field.sample(START, 34.651383346207, 136.875, geometric(original("h")))
        for name, short in ((T, "t"), (U, "u"), (V, "v"), (Q, "q")):
            self.assertAlmostEqual(node[name], original(short), delta=2e-11)
        expected = {T: 234.19382622059165, U: -45.107594381376995,
                    V: -2.5550255797890772, Q: .000003986902242771835199}
        high = field.sample(START+timedelta(hours=3), 34.8, 137, geometric(30000))
        for name, value in expected.items():
            self.assertAlmostEqual(high[name], value, delta=2e-11)
        # 30 km geometric is not the 30,000 gpm oracle above.
        geometric30 = field.sample(START+timedelta(hours=3), 34.8, 137, 30000)
        self.assertGreater(abs(geometric30[T]-high[T]), .01)

    def test_jra_native_schedule_and_query_bounds_are_explicit(self):
        for times in ((START, START+timedelta(hours=12)),
                      (START+timedelta(hours=1), START+timedelta(hours=7))):
            data = deepcopy(self.bundle)
            data["axes"]["time_utc"] = [t.isoformat() for t in times]
            self.reject("EXPECTED_TIME_GAP", lambda: Jra3qModelField(data))
        field = Jra3qModelField(self.bundle)
        for time in (START-timedelta(microseconds=1), START+timedelta(hours=6, microseconds=1)):
            self.reject("TIME_OUT_OF_RANGE", lambda: field.sample(time, 34.8, 137, 1000))
        self.reject("NON_UTC_TIME", lambda: field.sample(datetime(2024, 1, 1, 3), 34.8, 137, 1000))
        self.reject("LATITUDE_OUT_OF_RANGE", lambda: field.sample(START, 34.6, 137, 1000))
        self.reject("LONGITUDE_OUT_OF_RANGE", lambda: field.sample(START, 34.8, 137.3, 1000))

    def test_jra_ground_gap_rejection_at_all_eight_original_columns(self):
        field = Jra3qModelField(self.bundle)
        for t in range(2):
            for j in range(2):
                for i in range(2):
                    with self.subTest(column=(t, j, i)):
                        time, lat, lon = self.old.times[t], self.old.latitudes[j], self.old.longitudes[i]
                        ground, low = self.old.surface_height[t][j][i], self.old.heights[t][0][j][i]
                        self.assertAlmostEqual(field.ground_altitude(time, lat, lon), geometric(ground))
                        self.reject("HEIGHT_OUT_OF_RANGE", lambda: field.sample(time, lat, lon, geometric((ground+low)/2)))
                        self.reject("BELOW_MODEL_SURFACE", lambda: field.sample(time, lat, lon, geometric(ground-1)))

    def test_malformed_bundle_and_nonfinite_json_are_not_accepted(self):
        mutations = (lambda b: b.update(schema="balloon.weather.jra3q_model/99"),
                     lambda b: b.update(product="another_product"),
                     lambda b: b["axes"].update(model_level=[1, 3, 4]),
                     lambda b: b["hybrid"]["b_half"].__setitem__(0, .9),
                     lambda b: b["fields"][U][0][0][0].__setitem__(0, float("nan")),
                     lambda b: b["fields"][Q][0][0][0].__setitem__(0, 1))
        for change in mutations:
            data = deepcopy(self.bundle)
            change(data)
            with self.subTest(change=change.__code__.co_firstlineno), self.assertRaises(WeatherError):
                Jra3qModelField(data)
        sigma = deepcopy(self.bundle)
        sigma["hybrid"] = {"a_half_pa": [0]*101, "b_half": [1-k/100 for k in range(101)]}
        # A generic descending 100-level sigma coordinate is not JRA's reviewed
        # hybrid coordinate, even if its surface/top endpoints are identical.
        self.reject("UNSUPPORTED_VERTICAL_COORDINATE", lambda: Jra3qModelField(sigma))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"bad.json"
            for text in ('{"schema":"a","schema":"b"}', '{"value":NaN}', '{"value":1e9999}'):
                path.write_text(text, encoding="utf-8")
                self.reject("INVALID_JSON", lambda: load_weather(path))

    def test_storage_plain_gzip_and_gfs_dispatch_without_fixture_runtime_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            plain, compressed = Path(tmp)/"jra.json", Path(tmp)/"jra.json.gz"
            plain.write_text(json.dumps(self.bundle, allow_nan=False), encoding="utf-8")
            write_bundle(compressed, self.bundle)
            original_import = builtins.__import__
            def runtime_import(name, *args, **kwargs):
                if name == "tools" or name.startswith("tools.") or "normalize_jra3q_model_fixture" in name:
                    raise AssertionError("runtime must not import the fixture tool")
                return original_import(name, *args, **kwargs)
            with patch("builtins.__import__", side_effect=runtime_import):
                a, b = load_weather(plain), load_weather(compressed)
                self.assertIsInstance(a, Jra3qModelField)
                self.assertEqual(a.sample(START, 34.8, 137, 1000), b.sample(START, 34.8, 137, 1000))
                self.assertIsInstance(load_weather(ROOT/"references/flight_fixture/wakayama-weather.json.gz"), WeatherField)
            before = compressed.read_bytes()
            with self.assertRaises(FileExistsError):
                write_bundle(compressed, self.bundle)
            self.assertEqual(compressed.read_bytes(), before)

    def test_observed_sixty_second_flight_preserves_records_and_duration_stop(self):
        config = short_config()
        result = simulate(config, Jra3qModelField(self.bundle))
        self.assertEqual(result["status"], "stopped")
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop_reason"]["code"], "MAX_DURATION")
        self.assertEqual(result["events"], [])
        last = result["records"][-1]
        self.assertEqual(last["time_utc"], "2024-01-01T02:18:13+00:00")
        self.assertEqual(last["elapsed_s"], 60)
        self.assertAlmostEqual(last["altitude_m"], config["launch"]["altitude_m"]+300, places=9)
        self.assertIsNone(result["summary"]["landing"])
        self.assertTrue(all(r["phase"] == "ascent" and r["height_agl_m"] > 0 for r in result["records"]))
        self.assertTrue(all("strict_model_column_support" in r["weather_quality"] for r in result["records"]))
        self.assertEqual(result, simulate(config, Jra3qModelField(self.bundle)))

    def test_isothermal_burst_descent_stops_at_model_support_not_false_landing(self):
        config = short_config()
        config["ascent"] = {"mode": "isothermal_buoyancy", "gas_mass_kg": .7,
                            "envelope_mass_kg": 1.2, "payload_mass_kg": 2,
                            "drag_coefficient": .47, "gas_constant_j_kg_k": 2077.1}
        config["burst"]["altitude_m"] = 600
        config["descent"] = {"mode": "rated_speed", "reference_speed_m_s": 5,
                             "density_model": "weather", "reference_density_kg_m3": 1.225}
        config["integration"]["max_duration_s"] = 600
        result = simulate(config, Jra3qModelField(self.bundle))
        self.assertEqual([e["type"] for e in result["events"]], ["burst"], result["stop_reason"])
        self.assertEqual(result["events"][0]["altitude_m"], 600)
        self.assertEqual({r["phase"] for r in result["records"]}, {"ascent", "descent"})
        self.assertEqual(result["stop_reason"]["code"], "HEIGHT_OUT_OF_RANGE")
        self.assertFalse(result["complete"])
        self.assertIsNone(result["summary"]["landing"])
        last = result["records"][-1]
        self.assertEqual(last["phase"], "descent")
        self.assertGreater(last["height_agl_m"], 0)
        self.assertLess(last["vertical_speed_m_s"], 0)
        # Independent ideal-mixture density check on the retained physical input.
        first = result["records"][0]
        density = first[P]/(first[T]*(287.05*(1-first[Q])+461.5*first[Q]))
        self.assertAlmostEqual(first["air_density_kg_m3"], density, places=12)
        self.assertGreater(first["free_lift_n"], 0)
        self.assertTrue(all(r["height_agl_m"] > 0 for r in result["records"]))


if __name__ == "__main__":
    unittest.main()
