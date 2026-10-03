"""0.18.0 JRA candidate: independent analytic/Decimal expectations, no network.

The fixed 4,012-value fixture is compared with original ASCII rows and a separate
high-precision pressure expression. Synthetic fields isolate support failures
without pretending that meteorological continuity establishes physical accuracy.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("jra_candidate", ROOT/"tools/normalize_jra3q_model_fixture.py")
env = importlib.util.module_from_spec(spec)
spec.loader.exec_module(env)
START = datetime(2024,1,1,tzinfo=timezone.utc)
Q = "specific_humidity_kg_kg"
T = "temperature_k"
U = "eastward_wind_m_s"
V = "northward_wind_m_s"


def synthetic_inputs():
    names = ("height","pressure",T,U,V,Q)
    data = {n:[] for n in names}
    for t in range(2):
        for n in names:
            data[n].append([])
        for k in range(3):
            planes = {n:[] for n in names}
            for j in range(2):
                rows = {n:[] for n in names}
                for i in range(2):
                    h = 100+1000*k+20*t+50*j+100*i
                    vals = {"height":h,"pressure":100000-20*h+4*t+6*j+8*i,
                            T:270+2*t+3*j+4*i+.005*h,U:5+t+j+i+.001*h,
                            V:-3+2*t-j+i-.002*h,Q:.001+.0001*t+.0002*j+.0003*i+.000001*h}
                    for n in names:
                        rows[n].append(vals[n])
                for n in names:
                    planes[n].append(rows[n])
            for n in names:
                data[n][-1].append(planes[n])
    return {"times_utc":[START,START+timedelta(hours=6)],"expected_times_utc":[START,START+timedelta(hours=6)],
            "latitude_degrees":[34,36],"longitude_degrees":[136,138],"model_levels":[1,2,3],
            "geopotential_height_gpm":data.pop("height"),"pressure_pa":data.pop("pressure"),"fields":data,
            "surface_pressure_pa":[[[101000]*2 for _ in range(2)] for _ in range(2)],
            "surface_geopotential_height_gpm":[[[0]*2 for _ in range(2)] for _ in range(2)],
            "provenance":{"fixture_id":"synthetic-not-an-observation"}}


def sample(e, **kwargs):
    query = {"time_utc":START+timedelta(hours=3),"latitude_degrees":35,"longitude_degrees":137,
             "geopotential_height_gpm":1000,"required_fields":tuple(env.FIELD_UNITS)}
    query.update(kwargs)
    return e.sample(**query)


def decimal_full(lower, upper):
    # Independent high-precision form, not implementation's log1p rearrangement.
    with localcontext() as ctx:
        ctx.prec = 60
        lower,upper = Decimal(str(lower)),Decimal(str(upper))
        return float(((lower*lower.ln()-upper*upper.ln())/(lower-upper)-1).exp())


class OfflineTestCase(unittest.TestCase):
    def setUp(self):
        for name in ("socket.socket","socket.create_connection"):
            block = patch(name,side_effect=AssertionError("network forbidden in fixture tests"))
            block.start()
            self.addCleanup(block.stop)

    def assert_rejected(self,e,code,**query):
        with self.assertRaises(env.EnvironmentQueryError) as caught:
            sample(e,**query)
        self.assertEqual(caught.exception.code,code)


class NumericalContractTests(OfflineTestCase):
    def test_affine_fields_with_moving_column_heights(self):
        result = sample(env.ModelLevelEnvironment(**synthetic_inputs()))
        expected = {"pressure_pa":80009,T:279.5,U:7.5,V:-4,Q:.0023}
        for name,value in expected.items():
            self.assertAlmostEqual(result["values"][name],value,places=10)
        self.assertEqual(len(result["support_cells"]),16)
        self.assertAlmostEqual(sum(c["weight"] for c in result["support_cells"]),1)

    def test_column_pressure_is_not_shared_level_pressure(self):
        result = sample(env.ModelLevelEnvironment(**synthetic_inputs()),time_utc=START,
                        latitude_degrees=36,longitude_degrees=138,geopotential_height_gpm=250)
        self.assertEqual(result["values"]["pressure_pa"],95014)
        self.assertEqual(len(result["support_cells"]),1)

    def test_zero_weight_vertices_do_not_require_missing_q(self):
        args = synthetic_inputs()
        args["fields"][Q][1][0][0][0] = None
        e = env.ModelLevelEnvironment(**args)
        self.assertEqual(len(sample(e,time_utc=START,latitude_degrees=34,longitude_degrees=136,
                                    geopotential_height_gpm=100)["support_cells"]),1)
        self.assert_rejected(e,"MISSING_DATA")

    def test_missing_unused_q_does_not_block_simple_wind_path(self):
        args = synthetic_inputs()
        args["fields"][Q][0][0][0][0] = None
        e = env.ModelLevelEnvironment(**args)
        self.assertEqual(set(sample(e,required_fields=(U,V))["values"]),{U,V})
        self.assert_rejected(e,"MISSING_DATA")

    def test_absent_q_is_capability_failure_only_when_requested(self):
        args = synthetic_inputs()
        del args["fields"][Q]
        e = env.ModelLevelEnvironment(**args)
        sample(e,required_fields=(U,V))
        self.assert_rejected(e,"MISSING_CAPABILITY")

    def test_every_positive_vertex_needed_no_renormalization(self):
        args = synthetic_inputs()
        args["fields"][U][1][0][1][1] = None
        self.assert_rejected(env.ModelLevelEnvironment(**args),"MISSING_DATA",required_fields=(U,))

    def test_height_hole_does_not_bridge_to_other_levels(self):
        args = synthetic_inputs()
        args["geopotential_height_gpm"][0][1][0][0] = None
        self.assert_rejected(env.ModelLevelEnvironment(**args),"MISSING_HEIGHT_SUPPORT")

    def test_unused_height_column_does_not_block_exact_node(self):
        args = synthetic_inputs()
        args["geopotential_height_gpm"][1][1][1][1] = None
        sample(env.ModelLevelEnvironment(**args),time_utc=START,latitude_degrees=34,longitude_degrees=136)

    def test_ground_gap_and_below_ground_are_distinct(self):
        e = env.ModelLevelEnvironment(**synthetic_inputs())
        self.assert_rejected(e,"HEIGHT_OUT_OF_RANGE",geopotential_height_gpm=0)
        self.assert_rejected(e,"HEIGHT_OUT_OF_RANGE",geopotential_height_gpm=50)
        self.assert_rejected(e,"BELOW_MODEL_SURFACE",geopotential_height_gpm=-1)

    def test_one_column_lower_support_is_insufficient(self):
        # H=150 is above one bottom node, but below several positive-weight ones.
        self.assert_rejected(env.ModelLevelEnvironment(**synthetic_inputs()),"HEIGHT_OUT_OF_RANGE",geopotential_height_gpm=150)

    def test_missing_ground_or_pressure_coordinate_rejects(self):
        for field,indices,code in (("surface_pressure_pa",(0,0,0),"MISSING_SURFACE_SUPPORT"),
                                  ("surface_geopotential_height_gpm",(0,0,0),"MISSING_SURFACE_SUPPORT"),
                                  ("pressure_pa",(0,0,0,0),"MISSING_DATA")):
            args = synthetic_inputs()
            ref = args[field]
            for ix in indices[:-1]:
                ref = ref[ix]
            ref[indices[-1]] = None
            self.assert_rejected(env.ModelLevelEnvironment(**args),code)

    def test_utc_required_and_window_strict(self):
        e = env.ModelLevelEnvironment(**synthetic_inputs())
        for time in (datetime(2024,1,1),datetime(2024,1,1,tzinfo=timezone(timedelta(hours=9))),"2024-01-01Z"):
            self.assert_rejected(e,"NON_UTC_TIME",time_utc=time)
        for time in (START-timedelta(microseconds=1),START+timedelta(hours=6,microseconds=1)):
            self.assert_rejected(e,"TIME_OUT_OF_RANGE",time_utc=time)
        for time in (START,START+timedelta(hours=6)):
            sample(e,time_utc=time)

    def test_missing_scheduled_time_not_long_interpolation_edge(self):
        args = synthetic_inputs()
        args["times_utc"][1] = START+timedelta(hours=12)
        with self.assertRaisesRegex(ValueError,"EXPECTED_TIME_MISMATCH"):
            env.ModelLevelEnvironment(**args)
        args["expected_times_utc"] = args["times_utc"]
        with self.assertRaisesRegex(ValueError,"EXPECTED_TIME_GAP"):
            env.ModelLevelEnvironment(**args)

    def test_wrong_native_hour_or_missing_level_rejects(self):
        args = synthetic_inputs()
        args["times_utc"] = args["expected_times_utc"] = [START+timedelta(hours=1),START+timedelta(hours=7)]
        with self.assertRaisesRegex(ValueError,"00/06/12/18"):
            env.ModelLevelEnvironment(**args)
        args = synthetic_inputs()
        args["model_levels"] = [1,3,4]
        with self.assertRaisesRegex(ValueError,"contiguous"):
            env.ModelLevelEnvironment(**args)

    def test_invalid_query_and_required_fields(self):
        e = env.ModelLevelEnvironment(**synthetic_inputs())
        for value in (True,None,float("nan"),float("inf"),10**400):
            self.assert_rejected(e,"INVALID_QUERY",geopotential_height_gpm=value)
        for fields in ((),(U,U),U,(1,)):
            self.assert_rejected(e,"INVALID_REQUIRED_FIELDS",required_fields=fields)
        self.assert_rejected(e,"MISSING_CAPABILITY",required_fields=("geometric_vertical_wind_m_s",))
        self.assert_rejected(e,"LATITUDE_OUT_OF_RANGE",latitude_degrees=33.99)
        self.assert_rejected(e,"LONGITUDE_OUT_OF_RANGE",longitude_degrees=138.01)

    def test_physical_domain_validation(self):
        for name,value in ((T,0),(Q,-.01),(Q,1)):
            args = synthetic_inputs()
            args["fields"][name][0][0][0][0] = value
            with self.assertRaises(ValueError):
                env.ModelLevelEnvironment(**args)
        args = synthetic_inputs()
        args["geopotential_height_gpm"][0][1][0][0] = 0
        with self.assertRaisesRegex(ValueError,"nonmonotonic"):
            env.ModelLevelEnvironment(**args)

    def test_nonfinite_field_is_missing_not_zero(self):
        for value in (float("nan"),float("inf"),None):
            args = synthetic_inputs()
            args["fields"][U][0][0][0][0] = value
            e = env.ModelLevelEnvironment(**args)
            self.assertIsNone(e.to_dict()["fields"][U][0][0][0][0])
            self.assert_rejected(e,"MISSING_DATA",required_fields=(U,))

    def test_inputs_and_returned_metadata_detached(self):
        args = synthetic_inputs()
        e = env.ModelLevelEnvironment(**args)
        before = sample(e)
        args["fields"][T][0][0][0][0] = 1
        e.capabilities["fields"][T] = "wrong"
        e.to_dict()["provenance"]["fixture_id"] = "wrong"
        self.assertEqual(before,sample(e))
        self.assertEqual(e.capabilities["fields"][T],"K")

    def test_simmons_burridge_independent_decimal_and_top(self):
        for lower,upper in ((100000,90000),(100000,99999.999),(100,20)):
            actual = env.full_pressure_pa([lower,upper,0])
            self.assertAlmostEqual(actual[0],decimal_full(lower,upper),places=8)
            self.assertEqual(actual[1],upper/2)
        actual = env.full_pressure_pa([100000,90000,0])[0]
        self.assertGreater(abs(actual-95000),40)  # Detect ERA arithmetic-mean substitution.

    def test_bad_half_pressure_never_accepted(self):
        for half in ([100,200,0],[100,100,0],[100,-1,0],[100,20,1],[100,float("nan"),0]):
            with self.assertRaises(ValueError):
                env.full_pressure_pa(half)


class SavedFixtureTests(OfflineTestCase):
    def setUp(self):
        super().setUp()
        self.e = env.load_fixture(ROOT)
        self.bundle = json.loads((ROOT/"references/jra3q_model_fixture/source_bundle.json").read_bytes())

    def test_real_axes_metadata_and_4012_values_retained(self):
        self.assertEqual(self.e.times,(START,START+timedelta(hours=6)))
        self.assertEqual(self.e.latitudes,(34.651383346207,35.0259928266149))
        self.assertEqual(self.e.longitudes,(136.875,137.25))
        self.assertEqual(len(self.e.levels),100)
        self.assertEqual(self.e.provenance["invariant_time_utc"],"1947-09-01T00:00:00+00:00")
        self.assertEqual(len(self.e.provenance["raw_receipts"]),15)
        self.assertEqual(self.bundle["data_value_count"],4012)
        for item in self.bundle["sources"].values():
            self.assertEqual(hashlib.sha256(item["body_utf8"].encode()).hexdigest(),item["response"]["body_sha256"])

    def test_real_node_matches_direct_original_ascii(self):
        # Independent direct row read, bypassing loader's parser and normalization.
        names = {T:"t",U:"u",V:"v",Q:"q"}
        expected = {}
        for name,short in names.items():
            text = self.bundle["sources"][f"jra-{short}-cell"]["body_utf8"]
            row = re.search(r"^\[0\]\[50\]\[1\], ([^\n]+)",text,re.M)[1]
            expected[name] = float(row.split(",")[0])
        h = float(re.search(r"^\[0\]\[50\]\[1\], ([^\n]+)",self.bundle["sources"]["jra-h-cell"]["body_utf8"],re.M)[1].split(",")[0])
        result = sample(self.e,time_utc=START,latitude_degrees=self.e.latitudes[0],longitude_degrees=self.e.longitudes[0],
                        geopotential_height_gpm=h,required_fields=tuple(names))
        self.assertEqual(result["values"],expected)
        self.assertEqual(result["support_cells"][0]["index_t_level_lat_lon"],[0,50,0,0])

    def test_real_pressure_against_decimal_half_formula(self):
        a,b = self.e.provenance["half_coefficients_pa"],self.e.provenance["half_coefficients_dimensionless"]
        for t,j,i in ((0,0,0),(1,1,1)):
            sp = self.e.surface_pressure[t][j][i]
            for k in (0,50,80,98):
                expected = decimal_full(a[k]+b[k]*sp,a[k+1]+b[k+1]*sp)
                self.assertAlmostEqual(self.e.pressures[t][k][j][i],expected,places=8)
            self.assertEqual(self.e.pressures[t][99][j][i],(a[99]+b[99]*sp)/2)

    def test_30000gpm_at_arbitrary_utc_and_grid_midpoint(self):
        result = sample(self.e,time_utc=START+timedelta(hours=2,minutes=17,seconds=13),
                        latitude_degrees=sum(self.e.latitudes)/2,longitude_degrees=sum(self.e.longitudes)/2,
                        geopotential_height_gpm=30000)
        self.assertEqual(len(result["support_cells"]),16)
        self.assertAlmostEqual(sum(c["weight"] for c in result["support_cells"]),1)
        self.assertTrue(all(0<c["weight"]<1 for c in result["support_cells"]))
        self.assertGreater(result["values"][Q],0)
        self.assertTrue(1000 < result["values"]["pressure_pa"] < 1500)

    def test_real_30000gpm_independent_decimal_reference(self):
        # 60-digit Decimal calculation from original ASCII decimal row strings,
        # independent of the normalizer/parser; exact query 03UTC/34.8N/137E.
        expected = {T:234.19382622059165210256,U:-45.10759438137699534569,
                    V:-2.55502557978907724269,Q:.000003986902242771835199}
        result = sample(self.e,time_utc=START+timedelta(hours=3),latitude_degrees=34.8,
                        longitude_degrees=137,geopotential_height_gpm=30000)
        for name,value in expected.items():
            self.assertAlmostEqual(result["values"][name],value,places=12)

    def test_real_gap_strict_rejection_all_eight_columns(self):
        gaps = []
        for t in range(2):
            for j in range(2):
                for i in range(2):
                    ground,lowest = self.e.surface_height[t][j][i],self.e.heights[t][0][j][i]
                    gaps.append(lowest-ground)
                    query = dict(time_utc=self.e.times[t],latitude_degrees=self.e.latitudes[j],longitude_degrees=self.e.longitudes[i])
                    self.assert_rejected(self.e,"HEIGHT_OUT_OF_RANGE",geopotential_height_gpm=(ground+lowest)/2,**query)
                    self.assert_rejected(self.e,"BELOW_MODEL_SURFACE",geopotential_height_gpm=ground-1,**query)
                    sample(self.e,geopotential_height_gpm=lowest,**query)
        self.assertAlmostEqual(min(gaps),7.847620,places=5)
        self.assertAlmostEqual(max(gaps),8.042075,places=5)

    def test_raw_bundle_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"references/jra3q_model_fixture"
            p.mkdir(parents=True)
            raw = (ROOT/"references/jra3q_model_fixture/source_bundle.json").read_bytes()
            (p/"source_bundle.json").write_bytes(raw+b" ")
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                env.load_fixture(Path(tmp))

    def test_new_external_output_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/"evidence"
            env.write_evidence(self.e,output,ROOT)
            report = json.loads((output/"environment.json").read_text(encoding="utf-8"))
            self.assertEqual(report["schema"],env.SCHEMA)
            self.assertEqual(report["provenance"]["source_bundle_sha256"],env.PINNED_SOURCE_BUNDLE_SHA256)
            with self.assertRaises(FileExistsError):
                env.write_evidence(self.e,output,ROOT)
            with self.assertRaises(ValueError):
                env.write_evidence(self.e,ROOT/"forbidden-evidence",ROOT)


if __name__ == "__main__":
    unittest.main()
