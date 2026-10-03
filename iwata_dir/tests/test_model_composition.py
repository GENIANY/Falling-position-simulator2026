"""0.18.0 dependency and contradiction tests; no force solver or network.

Expected sets come from the consumer scenario, not from catalogue iteration.
The same weather capability shape is shared with the JRA candidate adapter.
Numbers below are artificial configuration values, not adopted balloon inputs.
"""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tools.compose_model import CompositionError, SCHEMA, compose_model, tawhiri_like_spec


UV = {"eastward_wind_m_s", "northward_wind_m_s"}
PT = {"pressure_pa", "temperature_k"}
Q = "specific_humidity_kg_kg"
W = "geometric_vertical_wind_m_s"
JRA_CAPABILITIES = {
    "fields": {"pressure_pa": "Pa", "temperature_k": "K",
               "eastward_wind_m_s": "m s-1", "northward_wind_m_s": "m s-1",
               "specific_humidity_kg_kg": "kg kg-1"},
    "height_kind": "geopotential_height", "height_unit": "gpm",
    "time_kind": "analysis_valid_utc", "temporal_support": "2024-01-01T00:00:00+00:00/2024-01-01T06:00:00+00:00",
}


def force_stage(family="quasisteady", moist=False):
    parameters = {"dry_air_gas_constant_j_kg_k": 287.05, "mass_kg": 2.0,
                  "drag_coefficient": .5, "reference_area_m2": 1.0, "gravity_m_s2": 9.8}
    if moist:
        parameters["vapour_gas_constant_j_kg_k"] = 461.5
    result = {"id": "descent", "family": family, "horizontal": "wind_advection",
              "vertical_air": "ignore", "components": ["density.moist" if moist else "density.dry", "drag.constant_cd", "area.fixed"],
              "parameters": parameters, "events": ["landing.terrain"]}
    if family == "inertial":
        result["entry_velocity"] = {"mode": "explicit", "ground_velocity_m_s": 0.0}
    return result


def model(*stages):
    return {"schema": SCHEMA, "stages": list(stages)}


class ModelCompositionTests(unittest.TestCase):
    def reject(self, spec, code, capabilities=None):
        with self.assertRaises(CompositionError) as caught:
            compose_model(spec, capabilities)
        self.assertEqual(caught.exception.code, code)
        self.assertTrue(caught.exception.path)

    def test_simple_profile_needs_only_uv_and_separate_terrain(self):
        result = compose_model(tawhiri_like_spec(5, 5, 30000), JRA_CAPABILITIES)
        self.assertEqual(set(result["required_fields"]), UV)
        self.assertEqual(set(result["required_terrain_fields"]), {"terrain_geometric_height_m"})
        self.assertEqual(result["stages"][0]["events"][0]["outcome"], "transition")
        self.assertEqual(result["stages"][1]["events"][0]["outcome"], "complete")
        self.assertEqual(result["capability_check"], "declared_field_units_only")
        self.assertIn("geometric_state_to_weather_height_coordinate", result["unresolved_contracts"])

    def test_diameter_burst_adds_transitive_volume_requirements(self):
        spec = tawhiri_like_spec(5, 5, 30000)
        ascent = spec["stages"][0]
        ascent["events"] = ["burst.diameter"]
        del ascent["parameters"]["burst_geometric_height_m"]
        ascent["parameters"].update(burst_diameter_m=10, helium_mass_kg=.5, helium_gas_constant_j_kg_k=2077)
        self.reject(spec, "MISSING_CLOSURE")
        ascent["components"] += ["geometry.sphere", "volume.ideal_gas", "temperature.equal_air", "pressure.equal_air"]
        result = compose_model(spec)
        self.assertEqual(set(result["required_fields"]), UV | PT)
        self.assertNotIn(Q, result["required_fields"])
        order = result["stages"][0]["evaluation_order"]
        self.assertLess(order.index("volume.ideal_gas"), order.index("geometry.sphere"))
        self.assertIn("ascent:pressure.equal_air", result["required_fields"]["pressure_pa"]["consumers"])

    def test_dry_moist_axis_adds_only_humidity(self):
        dry = compose_model(model(force_stage()), JRA_CAPABILITIES)
        moist = compose_model(model(force_stage(moist=True)), JRA_CAPABILITIES)
        self.assertEqual(set(dry["required_fields"]), UV | PT)
        self.assertEqual(set(moist["required_fields"]) - set(dry["required_fields"]), {Q})
        self.assertNotIn("volume", " ".join(moist["stages"][0]["evaluation_order"]))

    def test_fixed_drag_diameter_cannot_bypass_volume_burst_dependency(self):
        spec = tawhiri_like_spec(5, 5, 30000)
        ascent = spec["stages"][0]
        ascent["events"] = ["burst.diameter"]
        ascent["components"].append("diameter.fixed")
        del ascent["parameters"]["burst_geometric_height_m"]
        ascent["parameters"].update(burst_diameter_m=10, reference_diameter_m=2)
        self.reject(spec, "INCOMPATIBLE_EVENT_GEOMETRY")

    def test_inertia_does_not_add_weather_fields_but_adds_state(self):
        quasi = compose_model(model(force_stage()))
        inertial = compose_model(model(force_stage("inertial")))
        self.assertEqual(quasi["required_fields"], inertial["required_fields"])
        self.assertEqual(set(inertial["stages"][0]["state_schema"]) - set(quasi["stages"][0]["state_schema"]), {"ground_vertical_velocity_m_s"})

    def test_motion_density_drag_axes_can_be_combined(self):
        for family in ("quasisteady", "inertial"):
            for moist in (False, True):
                for reynolds in (False, True):
                    with self.subTest(family=family, moist=moist, reynolds=reynolds):
                        stage = force_stage(family, moist)
                        if reynolds:
                            stage["components"][1] = "drag.reynolds"
                            stage["components"] += ["diameter.fixed", "viscosity.sutherland"]
                            del stage["parameters"]["drag_coefficient"]
                            stage["parameters"].update(drag_correlation_id="comparison-candidate", reference_diameter_m=1,
                                                       viscosity_reference_pa_s=1.7e-5, viscosity_reference_temperature_k=273,
                                                       sutherland_temperature_k=110)
                        result = compose_model(model(stage), JRA_CAPABILITIES)
                        self.assertEqual(set(result["required_fields"]), UV | PT | ({Q} if moist else set()))
                        self.assertEqual("ground_vertical_velocity_m_s" in result["stages"][0]["state_schema"], family == "inertial")

    def test_reynolds_transitively_requires_viscosity_and_diameter(self):
        stage = force_stage()
        stage["components"][0] = "density.legacy_altitude"
        del stage["parameters"]["dry_air_gas_constant_j_kg_k"]
        simple = compose_model(model(stage))
        stage["components"][1] = "drag.reynolds"
        del stage["parameters"]["drag_coefficient"]
        stage["parameters"]["drag_correlation_id"] = "candidate-not-scientifically-accepted"
        self.reject(model(stage), "MISSING_CLOSURE")
        stage["components"] += ["viscosity.sutherland", "diameter.fixed"]
        stage["parameters"].update(reference_diameter_m=1, viscosity_reference_pa_s=1.7e-5,
                                   viscosity_reference_temperature_k=273, sutherland_temperature_k=110)
        result = compose_model(model(stage))
        self.assertEqual(set(simple["required_fields"]), UV)
        self.assertEqual(set(result["required_fields"]), UV | {"temperature_k"})
        self.assertLess(result["stages"][0]["evaluation_order"].index("viscosity.sutherland"), result["stages"][0]["evaluation_order"].index("drag.reynolds"))

    def test_ground_rate_cannot_add_vertical_wind(self):
        spec = tawhiri_like_spec(5, 5, 30000)
        spec["stages"][0]["vertical_air"] = "geometric"
        self.reject(spec, "DOUBLE_VERTICAL_WIND")

    def test_air_rate_adds_geometric_wind_once_and_requires_it(self):
        spec = tawhiri_like_spec(5, 5, 30000)
        spec["stages"][0].update(rate_reference="air", vertical_air="geometric")
        result = compose_model(spec)
        self.assertEqual(set(result["required_fields"]), UV | {W})
        self.assertEqual(result["stages"][0]["vertical_wind_use"], "air_rate_plus_wind_once")
        self.reject(spec, "MISSING_CAPABILITY", JRA_CAPABILITIES)

    def test_pressure_velocity_is_not_a_geometric_wind_capability(self):
        stage = force_stage()
        stage["vertical_air"] = "geometric"
        caps = deepcopy(JRA_CAPABILITIES)
        caps["fields"][W] = "Pa s-1"
        self.reject(model(stage), "CAPABILITY_UNIT_MISMATCH", caps)
        stage["vertical_air"] = "omega"
        self.reject(model(stage), "UNSUPPORTED_VERTICAL_WIND")

    def test_duplicate_drag_or_pressure_provider_rejected(self):
        stage = force_stage()
        stage["components"].append("drag.cda_over_mass")
        self.reject(model(stage), "DUPLICATE_PROVIDER")
        spec = tawhiri_like_spec(5, 5, 30000)
        spec["stages"][0]["components"] += ["pressure.fixed", "pressure.overpressure"]
        self.reject(spec, "DUPLICATE_PROVIDER")

    def test_reference_rate_and_cda_mass_are_alternative_inputs(self):
        stage = force_stage()
        stage["components"] = ["density.legacy_altitude", "drag.reference_rate"]
        stage["parameters"] = {"descent_reference_speed_m_s": 5, "reference_density_kg_m3": 1.2, "gravity_m_s2": 9.8}
        self.assertEqual(set(compose_model(model(stage))["required_fields"]), UV)
        stage["parameters"]["cda_over_mass_m2_kg"] = .2
        self.reject(model(stage), "UNUSED_PARAMETER")
        stage["components"].append("drag.cda_over_mass")
        self.reject(model(stage), "DUPLICATE_PROVIDER")

    def test_unconsumed_cd_is_not_silently_ignored(self):
        spec = tawhiri_like_spec(5, 5, 30000)
        spec["stages"][0]["parameters"]["drag_coefficient"] = .5
        self.reject(spec, "UNUSED_PARAMETER")
        del spec["stages"][0]["parameters"]["drag_coefficient"]
        spec["stages"][0]["components"].append("density.legacy_altitude")
        self.reject(spec, "UNUSED_COMPONENT")
        spec["stages"][0]["diagnostics"] = ["density"]
        self.assertEqual(set(compose_model(spec)["required_fields"]), UV)

    def test_density_shared_by_drag_buoyancy_is_resolved_once(self):
        stage = force_stage(moist=True)
        stage["components"] += ["buoyancy.volume", "volume.ideal_gas", "temperature.equal_air", "pressure.equal_air"]
        stage["parameters"].update(helium_mass_kg=.5, helium_gas_constant_j_kg_k=2077)
        result = compose_model(model(stage))
        self.assertEqual(result["stages"][0]["evaluation_order"].count("density.moist"), 1)
        self.assertEqual(set(result["required_fields"]), UV | PT | {Q})

    def test_inertial_initialization_is_required(self):
        stage = force_stage("inertial")
        del stage["entry_velocity"]
        self.reject(model(stage), "MISSING_INITIAL_STATE")
        stage["entry_velocity"] = {"mode": "carry"}
        self.reject(model(stage), "INVALID_STATE_TRANSFER")

    def test_transition_from_air_rate_consumes_prior_ground_rate(self):
        ascent = tawhiri_like_spec(5, 5, 30000)["stages"][0]
        ascent.update(rate_reference="air", vertical_air="geometric")
        descent = force_stage("inertial")
        descent["entry_velocity"] = {"mode": "from_previous_rate"}
        result = compose_model(model(ascent, descent))
        entry = result["stages"][1]["entry_velocity"]
        self.assertEqual(entry["source"], "previous_resolved_ground_rate")
        self.assertEqual(entry["source_vertical_wind_use"], "air_rate_plus_wind_once")
        self.assertIn(W, result["required_fields"])
        descent["entry_velocity"] = {"mode": "carry"}
        self.reject(model(ascent, descent), "INVALID_STATE_TRANSFER")

    def test_inertial_carry_and_explicit_discard(self):
        ascent = force_stage("inertial")
        ascent["id"] = "ascent"
        ascent["events"] = ["burst.altitude"]
        ascent["parameters"]["burst_geometric_height_m"] = 30000
        descent = force_stage("inertial")
        descent["entry_velocity"] = {"mode": "carry"}
        self.assertEqual(compose_model(model(ascent, descent))["stages"][1]["entry_velocity"]["mode"], "carry")
        simple = tawhiri_like_spec(5, 5, 30000)["stages"][1]
        self.reject(model(ascent, simple), "MISSING_INITIAL_STATE")
        simple["entry_velocity"] = {"mode": "discard"}
        self.assertNotIn("ground_vertical_velocity_m_s", compose_model(model(ascent, simple))["stages"][1]["state_schema"])

    def test_two_dynamics_cannot_own_same_state(self):
        stage = force_stage()
        stage["family"] = ["quasisteady", "inertial"]
        self.reject(model(stage), "UNKNOWN_FAMILY")
        stage["family"] = "quasisteady"
        stage["additional_dz_dt"] = "rate.constant"
        self.reject(model(stage), "UNKNOWN_KEY")

    def test_time_limit_is_incomplete_not_landing(self):
        stage = force_stage()
        stage["events"] = ["time_limit"]
        stage["parameters"]["max_duration_s"] = 600
        result = compose_model(model(stage))
        self.assertEqual(result["stages"][0]["events"], [{"id": "time_limit", "outcome": "incomplete"}])
        self.assertEqual(result["required_terrain_fields"], {})

    def test_missing_transition_and_ambiguous_burst_are_rejected(self):
        spec = tawhiri_like_spec(5, 5, 30000)
        spec["stages"][0]["events"] = []
        self.reject(spec, "INVALID_PHASE_EVENT")
        spec["stages"][0]["events"] = ["burst.altitude", "burst.altitude"]
        self.reject(spec, "DUPLICATE_SELECTION")

    def test_numeric_and_unknown_inputs_reject_without_raw_exceptions(self):
        for value in (True, float("nan"), float("inf"), 10**1000):
            with self.subTest(value_type=type(value).__name__):
                stage = force_stage()
                stage["parameters"]["mass_kg"] = value
                self.reject(model(stage), "INVALID_PARAMETER")
        spec = tawhiri_like_spec(5, 5, 30000)
        spec["schema"] = "future/99"
        self.reject(spec, "UNKNOWN_SCHEMA")

    def test_results_do_not_share_mutable_input_or_prior_output(self):
        spec = tawhiri_like_spec(5, 5, 30000)
        before = deepcopy(spec)
        result = compose_model(spec, JRA_CAPABILITIES)
        json.dumps(result, allow_nan=False)
        result["stages"][0]["parameters"]["vertical_rate_m_s"] = 99
        result["capability_context"]["fields"]["temperature_k"] = "wrong"
        self.assertEqual(spec, before)
        self.assertEqual(JRA_CAPABILITIES["fields"]["temperature_k"], "K")
        self.assertEqual(compose_model(spec)["stages"][0]["parameters"]["vertical_rate_m_s"], 5)


class JraCompositionIntegrationTests(unittest.TestCase):
    """Real saved capability/query linkage; geometric flight height is not inferred."""

    def test_selected_requirements_query_saved_jra_without_network(self):
        from tools.normalize_jra3q_model_fixture import load_fixture
        with patch("socket.socket", side_effect=AssertionError("network forbidden")), patch("socket.create_connection", side_effect=AssertionError("network forbidden")):
            environment = load_fixture(Path(__file__).resolve().parents[1])
            for spec, expected in ((tawhiri_like_spec(5, 5, 30000), UV), (model(force_stage(moist=True)), UV | PT | {Q})):
                with self.subTest(expected=sorted(expected)):
                    plan = compose_model(spec, environment.capabilities)
                    query = environment.sample(time_utc=datetime(2024, 1, 1, 2, 17, 13, tzinfo=timezone.utc),
                                               latitude_degrees=34.8, longitude_degrees=137,
                                               geopotential_height_gpm=30000,
                                               required_fields=tuple(plan["required_fields"]))
                    self.assertEqual(set(query["values"]), expected)
                    self.assertEqual(query["status"], "ok")
                    self.assertEqual(len(query["support_cells"]), 16)
                    self.assertIn("geometric_state_to_weather_height_coordinate", plan["unresolved_contracts"])

    def test_real_jra_capability_refuses_geometric_wind_request(self):
        from tools.normalize_jra3q_model_fixture import load_fixture
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            environment = load_fixture(Path(__file__).resolve().parents[1])
            stage = force_stage()
            stage["vertical_air"] = "geometric"
            with self.assertRaises(CompositionError) as caught:
                compose_model(model(stage), environment.capabilities)
            self.assertEqual(caught.exception.code, "MISSING_CAPABILITY")


if __name__ == "__main__":
    unittest.main()
