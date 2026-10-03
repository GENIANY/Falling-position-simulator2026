"""Independent surface-reconstruction boundaries; no meteorological accuracy claim."""
from copy import deepcopy
from pathlib import Path
import builtins
import json
import tempfile
import unittest
from unittest.mock import patch

from balloon_sim.environment.fields import FIELD_NAMES, WeatherError
from balloon_sim.environment.model_levels import ModelLevelField
from balloon_sim.environment.model_surface import ModelSurfaceField, JOIN_LEVELS, POLICY
from balloon_sim.environment.jra3q import (Jra3qModelField, Jra3qSurfaceField,
    SCHEMA, PRODUCT, SURFACE_SCHEMA, SURFACE_PRODUCT)
from balloon_sim.environment.storage import load_weather, write_bundle

ROOT = Path(__file__).resolve().parents[1]
TIMES = ["2024-01-01T00:00:00+00:00", "2024-01-01T06:00:00+00:00"]
MID = "2024-01-01T03:00:00+00:00"
P, T, Q, U, V = "pressure_pa", "temperature_k", "specific_humidity_kg_kg", "eastward_wind_m_s", "northward_wind_m_s"
RADIUS = 6371000.0


def geometric(h):
    return RADIUS * h / (RADIUS - h)


def analytic_inputs():
    """Known affine values on two columns whose terrain differs by200gpm."""
    heights = [[[[ground + offset for ground in (0., 200.)]] for offset in (8., 28., 1000.)] for _ in TIMES]
    formulas = {P: lambda h, t: 100000. - 10*h, T: lambda h, t: 280. - .006*h,
                Q: lambda h, t: .004, U: lambda h, t: 2. + .01*h + t, V: lambda h, t: -1. + .005*h}
    arrays = {name: [[[[f(h, t) for h in row] for row in level] for level in heights[t]]
                     for t in range(2)] for name, f in formulas.items()}
    source = dict(times=TIMES, latitudes=[0.], longitudes=[0., 1.], levels=[1, 2, 3], heights=heights,
                  pressures=arrays.pop(P), fields=arrays,
                  surface_pressure=[[[100000., 98000.]], [[100000., 98000.]]],
                  surface_height=[[[0., 200.]], [[0., 200.]]], metadata={})
    surface = {"temperature_2m_k": [[[279.988, 278.788]], [[279.988, 278.788]]],
               "specific_humidity_2m_kg_kg": [[[.004, .004]], [[.004, .004]]],
               "eastward_wind_10m_m_s": [[[2.1, 4.1]], [[3.1, 5.1]]],
               "northward_wind_10m_m_s": [[[-.95, .05]], [[-.95, .05]]]}
    return source, surface


def query(field, h=100., time=TIMES[0], lon=.5, fields=None):
    return field.sample(time, 0., lon, geometric(h), fields=fields)


class OfflineCase(unittest.TestCase):
    def setUp(self):
        for name in ("socket.socket", "socket.create_connection"):
            blocker = patch(name, side_effect=AssertionError("network forbidden"))
            blocker.start(); self.addCleanup(blocker.stop)

    def reject(self, code, call):
        with self.assertRaises(WeatherError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)


class ReconstructionTests(OfflineCase):
    def setUp(self):
        super().setUp()
        self.data, self.surface = analytic_inputs()

    def build(self):
        return ModelSurfaceField(ModelLevelField(**self.data), self.surface, JOIN_LEVELS)

    def test_affine_upper_values_and_ground_are_independent_oracles(self):
        source = ModelLevelField(**self.data)
        field = ModelSurfaceField(source, self.surface, JOIN_LEVELS)
        for name, expected in {P: 95000., T: 277., Q: .004, U: 7.5, V: 1.5}.items():
            self.assertAlmostEqual(query(field, h=500., time=MID)[name], expected, places=9)
            self.assertAlmostEqual(query(source, h=500., time=MID)[name], expected, places=9)
        ground = query(field)
        self.assertAlmostEqual(ground[P], 99000.)
        self.assertAlmostEqual(ground[T], 279.388)
        self.assertAlmostEqual(ground[U], 3.1)
        self.assertAlmostEqual(ground["ground_altitude_m"], geometric(100.))
        self.assertEqual(ground["terrain_stencil_clamp_depth_m"], 0.)
        self.assertIn(POLICY, ground["quality"])
        self.assertIn("10m_analysis_held_below_anchor", ground["quality"])
        self.assertIn("native_wind_level1_not_used", ground["quality"])
        self.reject("BELOW_MODEL_SURFACE", lambda: query(source))

    def test_native_join_kept_and_replaced_wind_is_explicit(self):
        field = self.build()
        self.assertAlmostEqual(query(field, h=28., lon=0.)[U], 2.28)
        self.assertAlmostEqual(query(field, h=28., lon=0.)[P], 99720.)
        self.assertAlmostEqual(query(field, h=8., lon=0.)[U], 2.1)
        self.assertNotEqual(query(field, h=8., lon=0.)[U], self.data["fields"][U][0][0][0][0])
        for center in (10., geometric(28.)):
            values = [field.sample(TIMES[0], 0., 0., center + offset)[U] for offset in (-1e-6, 1e-6)]
            self.assertLess(abs(values[1] - values[0]), 3e-8)

    def test_original_utc_columns_are_queried_before_time_average(self):
        # Flat columns isolate time ordering: the level2 heights move, so
        # averaging their coordinates first would cross a different segment.
        heights = [[[[z, z]] for z in levels] for levels in ((8., 28., 100.), (8., 68., 100.))]
        self.data.update(heights=heights, surface_height=[[[0., 0.]], [[0., 0.]]],
                         surface_pressure=[[[100000., 100000.]], [[100000., 100000.]]],
                         pressures=[[[[100000.-10*z for z in row] for row in level] for level in when] for when in heights])
        self.data["fields"] = {T: [[[[280., 280.]]]*3 for _ in TIMES], Q: [[[[.004, .004]]]*3 for _ in TIMES],
            U: [[[[v, v]] for v in levels] for levels in ((999., 10., 20.), (999., 30., 40.))],
            V: [[[[0., 0.]]]*3 for _ in TIMES]}
        self.surface["eastward_wind_10m_m_s"] = [[[0., 0.]], [[0., 0.]]]
        field = self.build()
        h10 = RADIUS * 10. / (RADIUS + 10.)
        left = 10. + (50. - 28.) / (100. - 28.) * 10.
        right = (50. - h10) / (68. - h10) * 30.
        self.assertAlmostEqual(query(field, h=50., time=MID)[U], (left + right) / 2., places=10)
        wrongly_mixed_first = 20. + (50. - 48.) / (100. - 48.) * 10.
        self.assertGreater(abs(query(field, h=50., time=MID)[U] - wrongly_mixed_first), 1.)

    def test_original_bad_q_cannot_be_hidden_by_a_valid_mean(self):
        self.surface["specific_humidity_2m_kg_kg"][0][0] = [-.1, .108]
        field = self.build()
        self.reject("INVALID_FIELD_VALUE", lambda: query(field))
        self.assertAlmostEqual(query(field, fields=(U, V))[U], 3.1)
        self.assertAlmostEqual(query(field, h=500.)[Q], .004)  # diagnostic not consumed
        self.data["fields"][Q][0][0][0] = [-.1, .108]
        self.reject("INVALID_FIELD_VALUE", self.build)

    def test_missing_positive_support_is_not_renormalized_or_dried(self):
        self.surface["specific_humidity_2m_kg_kg"][0][0][1] = None
        field = self.build()
        self.reject("MISSING_DATA", lambda: query(field))
        query(field, h=0., lon=0.)  # exact node excludes the missing horizontal weight
        query(field, time=TIMES[1])  # exact UTC excludes the missing temporal weight
        query(field, fields=(U, V))
        query(field, h=500.)  # upper model q does not need surface q
        self.data["fields"][U][0][1][0][1] = None
        self.reject("MISSING_DATA", lambda: query(self.build()))

    def test_all_window_join_geometry_checked_without_switching_layer(self):
        self.data["heights"][1][1][0][1] = 209.
        self.reject("SURFACE_JOIN_UNSUPPORTED", self.build)  # laterUTC, other column
        self.data["heights"][1][1][0][1] = None
        self.reject("MISSING_HEIGHT_SUPPORT", self.build)
        self.data, self.surface = analytic_inputs()
        self.data["surface_height"][1][0][1] = None
        self.reject("MISSING_SURFACE_SUPPORT", self.build)
        self.data, self.surface = analytic_inputs()
        source = ModelLevelField(**self.data)
        for joins in ({**JOIN_LEVELS, U: 1}, {**JOIN_LEVELS, P: True}, {P: 1}):
            self.reject("INVALID_RECONSTRUCTION", lambda: ModelSurfaceField(source, self.surface, joins))

    def test_surface_and_virtual_top_limits_do_not_extend(self):
        field = self.build()
        self.reject("BELOW_MODEL_SURFACE", lambda: query(field, h=99.))
        self.reject("HEIGHT_OUT_OF_RANGE", lambda: query(field, h=1100.001))
        query(field, h=1100.)  # exact virtual top: horizontal mean of1000/1200
        self.reject("TIME_OUT_OF_RANGE", lambda: query(field, time="2024-01-01T06:00:01Z"))
        self.reject("LONGITUDE_OUT_OF_RANGE", lambda: query(field, lon=1.1))
        self.data["surface_pressure"][0][0][1] = None
        self.reject("MISSING_DATA", lambda: query(self.build(), fields=(U,)))

    def test_requested_fields_and_input_immutability(self):
        original_data, original_surface = deepcopy(self.data), deepcopy(self.surface)
        field = self.build(); expected = query(field)
        self.assertEqual(self.data, original_data); self.assertEqual(self.surface, original_surface)
        self.data["fields"][U][0][1][0][0] = 1e6
        self.surface["eastward_wind_10m_m_s"][0][0][0] = 1e6
        self.assertEqual(query(field), expected)
        for fields in ([], [U, U], [123]):
            self.reject("INVALID_REQUIRED_FIELDS", lambda: query(field, fields=fields))
        self.reject("MISSING_CAPABILITY", lambda: query(field, fields=("undefined",)))


class ProductBindingTests(OfflineCase):
    @classmethod
    def setUpClass(cls):
        # Only test preparation imports the preserved fixture decoder. The
        # production loader below is exercised with that import forbidden.
        from tools.normalize_jra3q_model_fixture import load_fixture
        old = load_fixture(ROOT)
        cls.strict = json.loads(json.dumps({
            "schema": SCHEMA, "product": PRODUCT,
            "axes": {"time_utc": [t.isoformat() for t in old.times], "model_level": list(old.levels),
                     "latitude_deg": list(old.latitudes), "longitude_deg": list(old.longitudes)},
            "fields": {"geopotential_height_gpm": old.heights,
                       **{name: data for name, data in old.fields.items() if name != P}},
            "surface": {"pressure_pa": old.surface_pressure, "geopotential_height_gpm": old.surface_height},
            "hybrid": {"a_half_pa": old.provenance["half_coefficients_pa"], "b_half": old.provenance["half_coefficients_dimensionless"]},
            "metadata": {"scope": "strict no bridge", "surface_policy": "strict support", "vertical_interpolation": "strict column"}}))

    def bundle(self):
        data = deepcopy(self.strict)
        data.update(schema=SURFACE_SCHEMA, product=SURFACE_PRODUCT,
                    reconstruction={"policy": POLICY, "join_model_levels": dict(JOIN_LEVELS)})
        for name, value in {"temperature_2m_k": 290., "specific_humidity_2m_kg_kg": .004,
                            "eastward_wind_10m_m_s": 2., "northward_wind_10m_m_s": -1.}.items():
            data["surface"][name] = [[[value]*2 for _ in range(2)] for _ in range(2)]
        return data

    def test_new_gzip_dispatch_and_metadata_are_explicit_old_strict_unchanged(self):
        strict = Jra3qModelField(self.strict)
        args = (TIMES[0], strict.latitudes[0], strict.longitudes[0])
        ground = strict.ground_altitude(*args)
        self.reject("HEIGHT_OUT_OF_RANGE", lambda: strict.sample(*args, ground))
        real_import = builtins.__import__
        def import_without_tools(name, *a, **kw):
            if name == "tools" or name.startswith("tools.") or name in ("surface_prototype", "normalize_window520"):
                raise AssertionError("runtime depends on an experiment/tool")
            return real_import(name, *a, **kw)
        data = self.bundle(); before = deepcopy(data)
        with tempfile.TemporaryDirectory() as temporary:
            new_path, old_path = Path(temporary) / "new.json.gz", Path(temporary) / "old.json.gz"
            write_bundle(new_path, data); write_bundle(old_path, self.strict)
            with patch("builtins.__import__", side_effect=import_without_tools):
                new, old = load_weather(new_path), load_weather(old_path)
                result = new.sample(*args, ground)
            self.assertIsInstance(new, Jra3qSurfaceField)
            self.assertIsInstance(old, Jra3qModelField)
            self.assertEqual(old.metadata, strict.metadata)
            self.assertEqual(old.sample(*args, geometric(30000.)), strict.sample(*args, geometric(30000.)))
            self.assertEqual(new.metadata["schema"], SURFACE_SCHEMA)
            self.assertEqual(new.metadata["product"], SURFACE_PRODUCT)
            self.assertEqual(new.metadata["reconstruction_policy"], POLICY)
            self.assertNotIn("strict", new.metadata["vertical_interpolation"])
            self.assertNotIn("strict", new.metadata["scope"])
            self.assertEqual(new.metadata["native_wind_not_used_model_levels"], [1])
            self.assertEqual(result[U], 2.); self.assertEqual(result[Q], .004)
        self.assertEqual(data, before)

    def test_schema_policy_shapes_coefficients_and_time_reject(self):
        cases = [(lambda d: d.update(product=PRODUCT), "INVALID_BUNDLE"),
                 (lambda d: d["reconstruction"].update(policy="column_surface_extension"), "INVALID_RECONSTRUCTION"),
                 (lambda d: d.pop("reconstruction"), "INVALID_BUNDLE"),
                 (lambda d: d["surface"].pop("temperature_2m_k"), "INVALID_BUNDLE"),
                 (lambda d: d["surface"].update(temperature_2m_k=[[[1.]]]), "INVALID_SHAPE"),
                 (lambda d: d["surface"]["temperature_2m_k"][0][0].__setitem__(0, float("nan")), "INVALID_NUMBER"),
                 (lambda d: d["hybrid"]["a_half_pa"].__setitem__(1, 1.), "UNSUPPORTED_VERTICAL_COORDINATE"),
                 (lambda d: d["axes"]["time_utc"].__setitem__(1, "2024-01-01T12:00:00Z"), "EXPECTED_TIME_GAP")]
        for change, code in cases:
            with self.subTest(code=code):
                data = self.bundle(); change(data)
                self.reject(code, lambda: Jra3qSurfaceField(data))


if __name__ == "__main__":
    unittest.main(verbosity=2)
