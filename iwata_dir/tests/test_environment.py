"""S14-3 environment contract tests, introduced in 0.14.0; no network.

Synthetic analytic fields exercise numerical support and rejection. Fixed GFS
tests separately check normalization against a direct ecCodes message decode.
These tests do not implement or accept a trajectory solver or real atmosphere.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("environment_candidate", ROOT / "tools/normalize_gfs_fixture.py")
env = importlib.util.module_from_spec(spec)
spec.loader.exec_module(env)
START = datetime(2026, 9, 21, 18, tzinfo=timezone.utc)


def synthetic_inputs(wind="linear"):
    fields = {name: [] for name in env.FIELD_UNITS}
    for t in range(2):
        for name in fields:
            fields[name].append([])
        for k in range(3):
            planes = {name: [] for name in fields}
            for j in range(2):
                rows = {name: [] for name in fields}
                for i in range(2):
                    h = 100 + 1000*k + 20*t + 50*j + 100*i
                    values = {"geopotential_height_gpm": h,
                              "temperature_k": 270 + 2*t + 3*j + 4*i + .005*h,
                              "eastward_wind_m_s": 5 + t + j + i + .001*h,
                              "northward_wind_m_s": -3 + 2*t - j + i - .002*h}
                    if wind != "linear":
                        values["eastward_wind_m_s"], values["northward_wind_m_s"] = wind
                    for name in fields:
                        rows[name].append(values[name])
                for name in fields:
                    planes[name].append(rows[name])
            for name in fields:
                fields[name][-1].append(planes[name])
    return {"times_utc": [START, START + timedelta(hours=1)],
            "latitude_degrees": [34, 36], "longitude_degrees": [136, 138],
            "pressure_pa": [100000, 80000, 60000], "fields": fields,
            "surface_pressure_pa": [[[100000]*2 for _ in range(2)] for _ in range(2)],
            "provenance": {"fixture_id": "synthetic-analytic-not-flight"}}


def sample(environment, **overrides):
    query = {"time_utc": START + timedelta(minutes=30), "latitude_degrees": 35,
             "longitude_degrees": 137, "geopotential_height_gpm": 1000}
    query.update(overrides)
    return environment.sample(**query)


class SyntheticEnvironmentTests(unittest.TestCase):
    def assert_rejected(self, environment, reason, **query):
        with self.assertRaises(env.EnvironmentQueryError) as caught:
            sample(environment, **query)
        self.assertEqual(caught.exception.code, reason)

    def test_affine_fields_across_distinct_column_heights(self):
        result = sample(env.Environment(**synthetic_inputs()))
        # Analytic fields at t=j=i=0.5, h=1000, independent of the interpolator.
        expected = {"temperature_k": 279.5, "eastward_wind_m_s": 7.5,
                    "northward_wind_m_s": -4, "geopotential_height_gpm": 1000,
                    "pressure_pa": 100000 - 20*(1000 - 100 - 10 - 25 - 50)}
        for name, value in expected.items():
            self.assertAlmostEqual(result["values"][name], value, places=10)
        self.assertAlmostEqual(sum(c["weight"] for c in result["support_cells"]), 1)
        self.assertEqual(len(result["support_cells"]), 16)

    def test_constant_wind_all_interior_and_boundary_queries(self):
        environment = env.Environment(**synthetic_inputs(wind=(7, -2)))
        for t in (START, START + timedelta(minutes=21), START + timedelta(hours=1)):
            for lat, lon in ((34,136), (35,137), (36,138)):
                result = sample(environment, time_utc=t, latitude_degrees=lat, longitude_degrees=lon)
                self.assertAlmostEqual(result["values"]["eastward_wind_m_s"], 7)
                self.assertAlmostEqual(result["values"]["northward_wind_m_s"], -2)

    def test_zero_wind_on_200_second_synthetic_ascent_queries(self):
        environment = env.Environment(**synthetic_inputs(wind=(0, 0)))
        # Prescribed 1000 m/5 m s-1 = 200 s is a synthetic query schedule,
        # not this module's vertical model; local displacement is u*dt, v*dt.
        for seconds in (0, 100, 200):
            values = sample(environment, time_utc=START + timedelta(seconds=seconds),
                            geopotential_height_gpm=500 + 5*seconds)["values"]
            self.assertEqual((values["eastward_wind_m_s"]*seconds,
                              values["northward_wind_m_s"]*seconds), (0, 0))

    def test_exact_maximum_corner_needs_only_one_cell(self):
        result = sample(env.Environment(**synthetic_inputs()), time_utc=START+timedelta(hours=1),
                        latitude_degrees=36, longitude_degrees=138, geopotential_height_gpm=2270)
        self.assertEqual(result["support_cells"], [{"index_t_level_lat_lon": [1,2,1,1], "weight": 1.0}])
        self.assertEqual(result["values"]["pressure_pa"], 60000)

    def test_exact_minimum_corner_and_surface_pressure_equality(self):
        result = sample(env.Environment(**synthetic_inputs()), time_utc=START,
                        latitude_degrees=34, longitude_degrees=136, geopotential_height_gpm=100)
        self.assertEqual(result["values"]["pressure_pa"], 100000)
        self.assertEqual(len(result["support_cells"]), 1)

    def test_no_time_extrapolation(self):
        environment = env.Environment(**synthetic_inputs())
        for time in (START-timedelta(microseconds=1), START+timedelta(hours=1, microseconds=1)):
            self.assert_rejected(environment, "TIME_OUT_OF_RANGE", time_utc=time)

    def test_no_space_extrapolation_or_wrapping(self):
        environment = env.Environment(**synthetic_inputs())
        for lat in (33.99999, 36.00001):
            self.assert_rejected(environment, "LATITUDE_OUT_OF_RANGE", latitude_degrees=lat)
        for lon in (135.99999, 138.00001, -223):
            self.assert_rejected(environment, "LONGITUDE_OUT_OF_RANGE", longitude_degrees=lon)

    def test_all_positive_weight_columns_must_support_height(self):
        environment = env.Environment(**synthetic_inputs())
        for height in (99.999, 2200.001):
            self.assert_rejected(environment, "HEIGHT_OUT_OF_RANGE", geopotential_height_gpm=height)

    def test_utc_is_required_and_offsets_are_not_silently_converted(self):
        environment = env.Environment(**synthetic_inputs())
        for time in (START.replace(tzinfo=None), START.astimezone(timezone(timedelta(hours=9))), "2026-09-21T18:00Z"):
            self.assert_rejected(environment, "NON_UTC_TIME", time_utc=time)

    def test_nonfinite_and_boolean_query_rejected(self):
        environment = env.Environment(**synthetic_inputs())
        for value in (float("nan"), float("inf"), True):
            self.assert_rejected(environment, "INVALID_QUERY", geopotential_height_gpm=value)

    def test_unrepresentable_integer_query_has_explicit_reason(self):
        environment = env.Environment(**synthetic_inputs())
        for key in ("geopotential_height_gpm", "latitude_degrees", "longitude_degrees"):
            self.assert_rejected(environment, "INVALID_QUERY", **{key: 10**1000})

    def test_finite_height_endpoints_with_overflowing_span_are_refused(self):
        inputs = synthetic_inputs()
        for t in range(2):
            for k, height in enumerate((-1e308, 1e308, 1.5e308)):
                inputs["fields"]["geopotential_height_gpm"][t][k] = [[height]*2 for _ in range(2)]
        self.assert_rejected(env.Environment(**inputs), "NUMERIC_UNSUPPORTED", geopotential_height_gpm=0)

    def test_tiny_interior_weight_does_not_silently_collapse_to_endpoint(self):
        inputs = synthetic_inputs()
        for t in range(2):
            for k, height in enumerate((0, 1e308, 1.5e308)):
                inputs["fields"]["geopotential_height_gpm"][t][k] = [[height]*2 for _ in range(2)]
        self.assert_rejected(env.Environment(**inputs), "NUMERIC_UNSUPPORTED", geopotential_height_gpm=1e-300)

    def test_below_ground_endpoint_and_crossing_stencil_rejected(self):
        inputs = synthetic_inputs()
        inputs["surface_pressure_pa"][0][0][0] = 90000
        environment = env.Environment(**inputs)
        self.assertEqual(environment.quality[0][0][0][0], ("below_ground",))
        for height in (100, 500):
            self.assert_rejected(environment, "BELOW_GROUND", time_utc=START,
                                 latitude_degrees=34, longitude_degrees=136, geopotential_height_gpm=height)
        # Exactly the next above-ground node does not depend on the masked node.
        result = sample(environment, time_utc=START, latitude_degrees=34,
                        longitude_degrees=136, geopotential_height_gpm=1100)
        self.assertEqual(result["values"]["pressure_pa"], 80000)

    def test_one_invalid_horizontal_corner_rejects_no_renormalization(self):
        inputs = synthetic_inputs()
        inputs["surface_pressure_pa"][1][1][1] = 70000
        self.assert_rejected(env.Environment(**inputs), "BELOW_GROUND")

    def test_missing_variable_at_required_endpoint_rejected(self):
        for missing in (None, float("nan"), float("inf")):
            inputs = synthetic_inputs()
            inputs["fields"]["temperature_k"][0][1][0][0] = missing
            self.assert_rejected(env.Environment(**inputs), "MISSING_DATA")

    def test_missing_height_rejects_column_without_guessing_bracket(self):
        inputs = synthetic_inputs()
        inputs["fields"]["geopotential_height_gpm"][0][2][0][0] = None
        self.assert_rejected(env.Environment(**inputs), "MISSING_HEIGHT_SUPPORT")

    def test_missing_surface_pressure_rejects_above_ground_guess(self):
        inputs = synthetic_inputs()
        inputs["surface_pressure_pa"][0][0][0] = None
        self.assert_rejected(env.Environment(**inputs), "MISSING_DATA")

    def test_missing_zero_weight_time_or_space_corner_is_irrelevant(self):
        inputs = synthetic_inputs()
        inputs["fields"]["temperature_k"][1][0][1][1] = None
        result = sample(env.Environment(**inputs), time_utc=START, latitude_degrees=34,
                        longitude_degrees=136, geopotential_height_gpm=100)
        self.assertEqual(result["values"]["temperature_k"], 270.5)

    def test_missing_level_is_not_bridged(self):
        inputs = synthetic_inputs()
        inputs["fields"]["temperature_k"][0][1][0][0] = None
        self.assert_rejected(env.Environment(**inputs), "MISSING_DATA", time_utc=START,
                             latitude_degrees=34, longitude_degrees=136, geopotential_height_gpm=1500)

    def test_input_mutation_does_not_change_environment(self):
        inputs = synthetic_inputs()
        environment = env.Environment(**inputs)
        before = sample(environment)
        inputs["fields"]["temperature_k"][0][1][0][0] = None
        inputs["provenance"]["fixture_id"] = "changed"
        self.assertEqual(sample(environment), before)

    def test_exported_fields_dictionary_cannot_mutate_live_environment(self):
        environment = env.Environment(**synthetic_inputs())
        before = sample(environment)
        exported = environment.to_dict()
        exported["fields"]["temperature_k"] = exported["fields"]["northward_wind_m_s"]
        exported["provenance"]["fixture_id"] = "changed"
        self.assertEqual(sample(environment), before)
        self.assertEqual(environment.to_dict()["fields"]["temperature_k"], environment.fields["temperature_k"])

    def test_invalid_axes_shapes_fields_or_nonmonotonic_heights_rejected(self):
        mutations = [lambda x: x.update(pressure_pa=[100000,60000,80000]),
                     lambda x: x.update(latitude_degrees=[36,34]),
                     lambda x: x.update(times_utc=[START,START]),
                     lambda x: x["fields"].pop("temperature_k"),
                     lambda x: x["fields"]["temperature_k"].pop(),
                     lambda x: x["fields"]["geopotential_height_gpm"][0][1][0].__setitem__(0,99),
                     lambda x: x["fields"]["temperature_k"][0][1][0].__setitem__(0,0)]
        for mutation in mutations:
            inputs = synthetic_inputs()
            mutation(inputs)
            with self.assertRaises(ValueError):
                env.Environment(**inputs)

    def test_explicit_height_keyword_prevents_geometric_height_confusion(self):
        with self.assertRaises(TypeError):
            env.Environment(**synthetic_inputs()).sample(time_utc=START, latitude_degrees=34,
                                                        longitude_degrees=136, height_m=1000)

    def test_output_preserves_null_mask_and_rejects_overwrite(self):
        inputs = synthetic_inputs()
        inputs["fields"]["temperature_k"][0][1][0][0] = float("nan")
        environment = env.Environment(**inputs)
        with tempfile.TemporaryDirectory() as parent:
            output = Path(parent)/"new"
            env.write_evidence(environment, output, ROOT)
            result = json.loads((output/"environment.json").read_text(encoding="utf-8"))
            self.assertIsNone(result["fields"]["temperature_k"][0][1][0][0])
            self.assertIn("missing_data", result["quality_flags"][0][1][0][0])
            with self.assertRaises(FileExistsError):
                env.write_evidence(environment, output, ROOT)

    def test_output_inside_input_or_tool_repository_is_refused(self):
        environment = env.Environment(**synthetic_inputs())
        for root, output in ((ROOT, ROOT/"forbidden-environment-output"),
                             (ROOT.parent, ROOT.parent/"forbidden-environment-output")):
            with self.assertRaises(ValueError):
                env.write_evidence(environment, output, root)
            self.assertFalse(output.exists())


class FixedGfsEnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import eccodes
            import numpy
        except ImportError as exc:
            raise unittest.SkipTest(f"fixed GRIB tests require existing ecCodes and NumPy: {exc}")
        cls.eccodes = eccodes
        cls.environment = env.load_fixture(ROOT)

    def test_real_fixture_units_provenance_masks_and_surface_separation(self):
        result = self.environment.to_dict()
        self.assertEqual(result["axes"]["pressure_pa"][0], 100000)
        self.assertEqual(result["axes"]["pressure_pa"][-1], 100)
        self.assertEqual(result["axes"]["time_utc"], [(START+timedelta(hours=i)).isoformat() for i in range(3)])
        counts = [sum("below_ground" in flags for plane in time for row in plane for flags in row)
                  for time in self.environment.quality]
        self.assertEqual(counts, [144,142,142])
        self.assertEqual(result["height_kind"], "geopotential_height")
        raw_orog = result["surface_fields_unconverted"]["orog:surface:0"]
        self.assertEqual(raw_orog["source_definition"]["units"], "m")
        self.assertEqual(len(raw_orog["values"]), 3)
        source = result["provenance"]["source_manifest"]
        self.assertEqual(len(source["files"]), 3)
        self.assertIn("source_url", source["files"][0])
        self.assertTrue(source["request_interval_deviation"]["occurred"])

    def test_exact_real_grid_cell_against_independent_raw_message_decode(self):
        raw = {}
        with (ROOT/"references/gfs_p1_fixture/f001.grib2").open("rb") as stream:
            while (handle := self.eccodes.codes_grib_new_from_file(stream)) is not None:
                try:
                    if (self.eccodes.codes_get(handle, "typeOfLevel") == "isobaricInhPa"
                            and self.eccodes.codes_get(handle, "level") == 500):
                        raw[self.eccodes.codes_get(handle, "shortName")] = float(self.eccodes.codes_get_values(handle)[40])
                finally:
                    self.eccodes.codes_release(handle)
        self.assertEqual(set(raw), {"gh","t","u","v"})
        result = self.environment.sample(time_utc=START+timedelta(hours=1), latitude_degrees=35,
                                         longitude_degrees=137, geopotential_height_gpm=raw["gh"])
        for source, target in env.SOURCE_NAMES.items():
            self.assertEqual(result["values"][target], raw[source])
        self.assertEqual(result["values"]["pressure_pa"], 50000)
        self.assertEqual(len(result["support_cells"]), 1)

    def test_real_interior_query_and_time_window_rejection(self):
        result = self.environment.sample(time_utc=START+timedelta(minutes=30), latitude_degrees=35.125,
                                         longitude_degrees=137.125, geopotential_height_gpm=30000)
        self.assertAlmostEqual(result["values"]["geopotential_height_gpm"], 30000)
        self.assertTrue(500 < result["values"]["pressure_pa"] < 5000)
        self.assertEqual(len(result["support_cells"]), 16)
        with self.assertRaises(env.EnvironmentQueryError) as caught:
            self.environment.sample(time_utc=START+timedelta(hours=3), latitude_degrees=35,
                                    longitude_degrees=137, geopotential_height_gpm=30000)
        self.assertEqual(caught.exception.code, "TIME_OUT_OF_RANGE")

    def test_actual_below_ground_cell_is_unusable(self):
        for k, plane in enumerate(self.environment.quality[0]):
            for j, row in enumerate(plane):
                for i, flags in enumerate(row):
                    if "below_ground" in flags:
                        with self.assertRaises(env.EnvironmentQueryError) as caught:
                            self.environment.sample(time_utc=START, latitude_degrees=self.environment.latitudes[j],
                                                    longitude_degrees=self.environment.longitudes[i],
                                                    geopotential_height_gpm=self.environment.fields["geopotential_height_gpm"][0][k][j][i])
                        self.assertEqual(caught.exception.code, "BELOW_GROUND")
                        return
        self.fail("expected an observed below-ground cell")


if __name__ == "__main__":
    unittest.main()
