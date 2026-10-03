"""Independent analytical, physics, boundary and convergence tests for flight."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import math
import unittest
from unittest.mock import patch

from balloon_sim.dynamics import (FlightError, moist_air_density, simulate,
                                  validate_config, vertical_state)
from balloon_sim.flight.numerics import IntegrationStep


START = datetime(2026, 9, 23, 0, 0, tzinfo=timezone.utc)
RADIUS = 6_371_000.0


class SupportError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


class AnalyticWeather:
    def __init__(self, u=0., v=0., ground=0., end_s=100000., lon_max=180.,
                 temperature=288.15, pressure=None, q=0., variable=False):
        self.u, self.v, self.surface = u, v, ground
        self.end_s, self.lon_max = end_s, lon_max
        self.temperature, self.pressure, self.q = temperature, pressure, q
        self.variable = variable
        self.queries = []

    def _check(self, time, lon):
        if time < START or time > START + timedelta(seconds=self.end_s):
            raise SupportError("TIME_OUT_OF_RANGE")
        if lon > self.lon_max:
            raise SupportError("LONGITUDE_OUT_OF_RANGE")

    def ground_altitude(self, time, lat, lon):
        self._check(time, lon)
        return self.surface(time, lat, lon) if callable(self.surface) else self.surface

    def sample(self, time, lat, lon, altitude_m, fields=None):
        self._check(time, lon)
        terrain = self.ground_altitude(time, lat, lon)
        if altitude_m < terrain:
            raise SupportError("BELOW_GROUND")
        self.queries.append((time, lat, lon, altitude_m, tuple(fields or ())))
        pressure = self.pressure if self.pressure is not None else 1.225*287.05*self.temperature
        if self.variable:
            pressure *= math.exp(-altitude_m/8400.)
        all_fields = {"eastward_wind_m_s": self.u, "northward_wind_m_s": self.v,
                      "pressure_pa": pressure, "temperature_k": self.temperature,
                      "specific_humidity_kg_kg": self.q, "ground_altitude_m": terrain,
                      "quality": ["analytic_fixture"]}
        return {key: value for key, value in all_fields.items()
                if fields is None or key in fields or key in ("quality", "ground_altitude_m")}


def configuration(**integration):
    return {"schema": "balloon.flight.config/1",
            "launch": {"time_utc": START.isoformat(), "latitude_deg": 0.,
                       "longitude_deg": 0., "altitude_m": 10.},
            "ascent": {"mode": "constant_speed", "speed_m_s": 5.},
            "burst": {"mode": "altitude", "altitude_m": 1000.},
            "descent": {"mode": "rated_speed", "reference_speed_m_s": 5.,
                        "density_model": "weather", "reference_density_kg_m3": 1.225},
            "integration": {"max_step_s": 13., "max_duration_s": 10000.,
                            "event_tolerance_s": 0.00001, **integration}}


def physical_configuration(**integration):
    config = configuration(**integration)
    config["ascent"] = {"mode": "isothermal_buoyancy", "gas_mass_kg": .6,
                        "envelope_mass_kg": 1.2, "payload_mass_kg": 2.,
                        "drag_coefficient": .47, "gas_constant_j_kg_k": 2077.1}
    return config


class FullFlightTests(unittest.TestCase):
    def test_constant_density_flight_matches_analytic_spherical_integral(self):
        config = configuration()
        result = simulate(config, AnalyticWeather(u=20))
        self.assertTrue(result["complete"], result["stop_reason"])
        self.assertEqual([event["type"] for event in result["events"]], ["burst", "landing"])
        ascent_time = (1000-10)/5
        descent_time = 1000/5
        self.assertAlmostEqual(result["events"][0]["elapsed_s"], ascent_time, delta=1e-5)
        self.assertAlmostEqual(result["summary"]["duration_s"], ascent_time+descent_time, delta=2e-5)
        expected_radians = 20/5 * (math.log((RADIUS+1000)/(RADIUS+10))
                                   + math.log((RADIUS+1000)/RADIUS))
        self.assertAlmostEqual(result["records"][-1]["longitude_deg"],
                               math.degrees(expected_radians), delta=4e-9)
        self.assertEqual(result["records"][-1]["latitude_deg"], 0.)
        self.assertEqual(result["records"][-1]["height_agl_m"], 0.)
        self.assertEqual(result["summary"]["maximum_altitude_m"], 1000.)

    def test_exponential_descent_matches_integral_at_30km(self):
        config = configuration(max_step_s=7, max_duration_s=20000)
        config["burst"]["altitude_m"] = 30000
        config["descent"] = {"mode": "rated_speed", "reference_speed_m_s": 6,
                             "density_model": "exponential", "scale_height_m": 8400}
        result = simulate(config, AnalyticWeather())
        expected = (30000-10)/5 + 16800/6*(1-math.exp(-30000/16800))
        self.assertTrue(result["complete"], result["stop_reason"])
        self.assertAlmostEqual(result["summary"]["duration_s"], expected, delta=0.0001)
        self.assertGreater(result["summary"]["ground_clamped_stage_queries"], 0)
        self.assertTrue(all(row["height_agl_m"] >= 0 for row in result["records"]))

    def test_nonbinary_constant_speed_still_reaches_exact_altitude_event(self):
        config = configuration(max_step_s=2.3)
        config["ascent"]["speed_m_s"] = 3.14159
        config["burst"]["altitude_m"] = 1234.567
        result = simulate(config, AnalyticWeather())
        self.assertTrue(result["complete"], result["stop_reason"])
        self.assertEqual(result["events"][0]["altitude_m"], 1234.567)
        self.assertAlmostEqual(result["events"][0]["elapsed_s"], (1234.567-10)/3.14159, delta=1e-5)

    def test_simple_exponential_requires_only_wind_not_pressure_or_humidity(self):
        config = configuration()
        config["descent"] = {"mode": "rated_speed", "reference_speed_m_s": 5,
                             "density_model": "exponential"}
        weather = AnalyticWeather()
        result = simulate(config, weather)
        self.assertTrue(result["complete"])
        self.assertTrue(all(query[4] == ("eastward_wind_m_s", "northward_wind_m_s")
                            for query in weather.queries))

    def test_sloping_terrain_landing_uses_moving_position(self):
        # Eastward travel raises terrain by 1000m per degree, considerably
        # shifting landing from the flat-terrain analytical result.
        weather = AnalyticWeather(u=100, ground=lambda t, lat, lon: 1000*lon)
        config = configuration(max_step_s=3)
        result = simulate(config, weather)
        self.assertTrue(result["complete"], result["stop_reason"])
        landing = result["records"][-1]
        self.assertGreater(landing["ground_altitude_m"], 200)
        self.assertAlmostEqual(landing["altitude_m"], 1000*landing["longitude_deg"], places=10)
        self.assertLess(result["summary"]["duration_s"], 398)
        self.assertTrue(all(query[3] >= weather.ground_altitude(query[0], query[1], query[2])
                            for query in weather.queries))

    def test_ascent_terrain_collision_is_not_success(self):
        result = simulate(configuration(max_step_s=1), AnalyticWeather(
            u=100, ground=lambda t, lat, lon: 10000*lon))
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop_reason"]["code"], "TERRAIN_COLLISION")
        self.assertEqual(result["events"][-1]["type"], "terrain_collision")

    def test_detected_midstep_ridge_is_subdivided_not_skipped(self):
        def ridge(time, lat, lon):
            elapsed = (time-START).total_seconds()
            return max(0, 100*(1-abs(elapsed-5)))
        result = simulate(configuration(max_step_s=10), AnalyticWeather(ground=ridge))
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop_reason"]["code"], "TERRAIN_COLLISION")
        self.assertAlmostEqual(result["events"][-1]["elapsed_s"], 410/95, delta=1e-5)

    def test_launch_at_ground_is_allowed_and_moves_up(self):
        config = configuration()
        config["launch"]["altitude_m"] = 0
        result = simulate(config, AnalyticWeather())
        self.assertTrue(result["complete"])
        self.assertGreater(result["records"][1]["height_agl_m"], 0)

    def test_launch_at_ground_into_steeper_rising_terrain_is_collision(self):
        config = configuration()
        config["launch"]["altitude_m"] = 0
        result = simulate(config, AnalyticWeather(u=100, ground=lambda t, lat, lon: 10000*lon))
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop_reason"]["code"], "TERRAIN_COLLISION")
        self.assertLessEqual(result["events"][-1]["elapsed_s"], 1e-5)

    def test_initial_departure_then_hillside_collision_is_not_launch_time(self):
        config=configuration(max_step_s=10)
        config['launch']['altitude_m']=0
        # Constant east wind and ascent give an independent spherical longitude:
        # lon(t)=degrees((u/w)*ln(1+w*t/R)). Flat ground until the 2 s position,
        # followed by a slope passing exactly through balloon altitude at 4 s.
        lon2=math.degrees(100/5*math.log1p(5*2/RADIUS))
        lon4=math.degrees(100/5*math.log1p(5*4/RADIUS))
        slope=20/(lon4-lon2)
        weather=AnalyticWeather(u=100,ground=lambda t,lat,lon:slope*max(0,lon-lon2))
        result=simulate(config,weather)
        self.assertFalse(result['complete'])
        self.assertEqual(result['stop_reason']['code'],'TERRAIN_COLLISION')
        self.assertAlmostEqual(result['events'][-1]['elapsed_s'],4,delta=2e-5)
        self.assertAlmostEqual(result['events'][-1]['altitude_m'],20,delta=1e-4)

    def test_submicrosecond_adaptive_step_preserves_last_accepted_record(self):
        trial=IntegrationStep(0,1e-7,(0.,0.,10.),lambda time:(0.,0.,10.))
        with patch('balloon_sim.flight.trajectory.AdaptiveRK45.trial',return_value=trial):
            result=simulate(configuration(),AnalyticWeather())
        self.assertFalse(result['complete'])
        self.assertEqual(result['stop_reason']['code'],'NUMERIC_UNSUPPORTED')
        self.assertEqual(len(result['records']),1)
        self.assertEqual(result['records'][0]['elapsed_s'],0)

    def test_launch_below_ground_is_rejected_without_fake_trajectory(self):
        result = simulate(configuration(), AnalyticWeather(ground=11))
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop_reason"]["code"], "LAUNCH_BELOW_GROUND")
        self.assertEqual(result["records"], [])

    def test_time_boundary_preserves_partial_ascent(self):
        result = simulate(configuration(), AnalyticWeather(end_s=100))
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop_reason"]["code"], "TIME_OUT_OF_RANGE")
        self.assertGreater(result["records"][-1]["elapsed_s"], 99.99)
        self.assertLessEqual(result["records"][-1]["elapsed_s"], 100.000001)
        self.assertEqual(result["events"], [])

    def test_space_boundary_preserves_partial_flight(self):
        result = simulate(configuration(), AnalyticWeather(u=100, lon_max=.05))
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop_reason"]["code"], "LONGITUDE_OUT_OF_RANGE")
        self.assertTrue(result["records"])
        self.assertLessEqual(result["records"][-1]["longitude_deg"], .05)
        self.assertFalse(result["summary"]["landing"])

    def test_duration_limit_and_step_limit_are_not_landings(self):
        for limits, expected in (({"max_duration_s": 50}, "MAX_DURATION"),
                                 ({"max_steps": 1}, "MAX_STEPS")):
            with self.subTest(expected=expected):
                result = simulate(configuration(**limits), AnalyticWeather())
                self.assertFalse(result["complete"])
                self.assertEqual(result["stop_reason"]["code"], expected)

    def test_current_latitude_not_launch_latitude_in_longitude_derivative(self):
        # Eastward and northward wind ratio yields d(lambda)/d(phi)=u/v sec(phi),
        # independent of radius and vertical speed: lambda=(u/v)ln(sec(phi)+tan(phi)).
        config = configuration(max_step_s=10, max_duration_s=50000)
        config["launch"]["latitude_deg"] = 30
        config["burst"]["altitude_m"] = 30000
        result = simulate(config, AnalyticWeather(u=60, v=100))
        self.assertTrue(result["complete"])
        point = result["records"][-1]
        primitive = lambda phi: math.log(1/math.cos(phi) + math.tan(phi))
        expected = math.degrees(.6*(primitive(math.radians(point["latitude_deg"]))
                                    - primitive(math.radians(30))))
        self.assertAlmostEqual(point["longitude_deg"], expected, delta=1e-9)
        initial_latitude_approx = .6*(point["latitude_deg"]-30)/math.cos(math.radians(30))
        self.assertGreater(abs(point["longitude_deg"]-initial_latitude_approx), .2)

    def test_time_varying_wind_is_sampled_at_solver_stages(self):
        class LinearWind(AnalyticWeather):
            def sample(self, time, *args, **kwargs):
                sample = super().sample(time, *args, **kwargs)
                sample["eastward_wind_m_s"] = (time-START).total_seconds()/10
                return sample
        weather = LinearWind()
        result = simulate(configuration(max_step_s=10), weather)
        self.assertTrue(result["complete"])
        times = {(query[0]-START).total_seconds() for query in weather.queries}
        self.assertTrue(any(0 < time < 10 for time in times))
        self.assertGreater(result["records"][-1]["longitude_deg"], .05)

    def test_adaptive_records_are_finite_ordered_and_bounded_with_backend_receipt(self):
        config=physical_configuration(max_step_s=80,max_duration_s=20000)
        config['burst']['altitude_m']=25000
        result=simulate(config,AnalyticWeather(u=30,v=10,variable=True))
        self.assertTrue(result['complete'],result['stop_reason'])
        rows=result['records']
        self.assertTrue(all(0 <= b['elapsed_s']-a['elapsed_s'] <= 80+1e-9
                            for a,b in zip(rows,rows[1:])))
        duplicates=[(a,b) for a,b in zip(rows,rows[1:]) if a['elapsed_s']==b['elapsed_s']]
        self.assertEqual(len(duplicates),1)
        self.assertEqual([row['phase'] for row in duplicates[0]],['ascent','descent'])
        self.assertTrue(all(row['event']=='burst' for row in duplicates[0]))
        self.assertTrue(all(math.isfinite(row[key]) for row in rows
                            for key in ('elapsed_s','latitude_deg','longitude_deg','altitude_m')))
        self.assertEqual(result['numerics']['backend'],'scipy.integrate.RK45')
        self.assertEqual(result['numerics']['event_solver'],'scipy.optimize.brentq')
        self.assertEqual(result['numerics']['absolute_tolerance'],
                         result['config']['integration']['absolute_tolerance'])

    def test_record_rejection_keeps_last_committed_time_and_step_count(self):
        class InvalidQuality(AnalyticWeather):
            def sample(self,time,*args,**kwargs):
                sample=super().sample(time,*args,**kwargs)
                if time > START+timedelta(seconds=10):
                    sample['quality']='invalid quality'
                return sample
        result=simulate(configuration(max_step_s=13),InvalidQuality())
        self.assertFalse(result['complete'])
        self.assertEqual(result['stop_reason']['code'],'INVALID_WEATHER')
        self.assertEqual(result['stop_reason']['elapsed_s'],0)
        self.assertEqual(result['summary']['accepted_steps'],0)
        self.assertEqual(result['summary']['duration_s'],0)
        self.assertEqual(len(result['records']),1)

    def test_burst_reached_is_retained_when_descent_inputs_are_missing(self):
        class WindOnly(AnalyticWeather):
            def sample(self,*args,**kwargs):
                sample=super().sample(*args,**kwargs)
                sample.pop('specific_humidity_kg_kg',None)
                return sample
        result=simulate(configuration(max_step_s=13),WindOnly())
        self.assertFalse(result['complete'])
        self.assertEqual(result['stop_reason']['code'],'MISSING_WEATHER_FIELD')
        self.assertEqual(result['summary']['maximum_altitude_m'],1000)
        self.assertEqual(result['events'][-1]['type'],'burst')
        point=result['records'][-1]
        self.assertEqual(point['phase'],'ascent')
        self.assertEqual(point['event'],'burst')
        self.assertAlmostEqual(point['elapsed_s'],198,delta=1e-5)
        self.assertEqual(result['stop_reason']['elapsed_s'],point['elapsed_s'])

    def test_nonlinear_burst_at_exact_support_ceiling_stops_conservatively(self):
        class Ceiling(AnalyticWeather):
            def sample(self,time,lat,lon,altitude_m,fields=None):
                if altitude_m > 1000:
                    raise SupportError('ALTITUDE_OUT_OF_RANGE')
                return super().sample(time,lat,lon,altitude_m,fields)
        result=simulate(physical_configuration(),Ceiling(variable=True))
        self.assertFalse(result['complete'])
        self.assertEqual(result['stop_reason']['code'],'ALTITUDE_OUT_OF_RANGE')
        self.assertEqual(result['events'],[])
        self.assertLess(result['records'][-1]['altitude_m'],1000)
        self.assertGreater(result['records'][-1]['altitude_m'],999.99)

    def test_input_config_unchanged_and_result_quality_detached(self):
        config = configuration()
        original = deepcopy(config)
        result = simulate(config, AnalyticWeather())
        self.assertEqual(config, original)
        result["config"]["launch"]["altitude_m"] = 123
        self.assertEqual(config, original)
        self.assertEqual(result["records"][0]["weather_quality"], ["analytic_fixture"])


class PhysicalModelTests(unittest.TestCase):
    def test_isothermal_flight_converges_to_independent_closed_form_time(self):
        # p=p0 exp(-z/H), constant T/q: rho*V is constant and projected area
        # scales as exp(2z/(3H)), so ascent w=v0 exp(z/(6H)). The weather-density
        # descent law gives w_down=5 exp(z/(2H)). Both flight times integrate exactly.
        height_scale=8400.
        temperature=288.15
        pressure0=1.225*287.05*temperature
        volume0=.6*2077.1*temperature/pressure0
        area0=math.pi*(3*volume0/(4*math.pi))**(2/3)
        speed0=math.sqrt(2*9.80665*(1.225*volume0-3.8)/(1.225*.47*area0))
        ascent_time=6*height_scale/speed0*(math.exp(-10/(6*height_scale))
                                         -math.exp(-1000/(6*height_scale)))
        descent_time=2*height_scale/5*(1-math.exp(-1000/(2*height_scale)))
        errors=[]
        for step in (73,17,3):
            result=simulate(physical_configuration(max_step_s=step),AnalyticWeather(variable=True))
            self.assertTrue(result['complete'],result['stop_reason'])
            self.assertAlmostEqual(result['events'][0]['elapsed_s'],ascent_time,delta=1e-5)
            errors.append(abs(result['summary']['duration_s']-(ascent_time+descent_time)))
        self.assertLess(errors[1],errors[0])
        self.assertLess(errors[2],errors[1])
        self.assertLess(errors[2],2e-5)

    def test_moist_density_independent_partial_pressure_identity(self):
        p, temperature, q = 80000., 270., .012
        epsilon = 287.05/461.5
        vapour_pressure = q*p/(epsilon+(1-epsilon)*q)
        expected = (p-vapour_pressure)/(287.05*temperature) + vapour_pressure/(461.5*temperature)
        self.assertAlmostEqual(moist_air_density(p, temperature, q), expected, places=14)
        self.assertLess(moist_air_density(p, temperature, q), moist_air_density(p, temperature, 0))

    def test_equal_temperature_buoyancy_and_drag_independent_balance(self):
        config = validate_config(physical_configuration())
        weather = {"pressure_pa": 90000., "temperature_k": 280., "specific_humidity_kg_kg": .01}
        result = vertical_state(config, "ascent", 1000, weather)
        volume = .6*2077.1*280/90000
        radius = (3*volume/(4*math.pi))**(1/3)
        density = 90000/(280*(287.05*.99 + 461.5*.01))
        up = 9.80665*(density*volume-(.6+1.2+2.))
        drag = .5*density*.47*math.pi*radius**2*result["vertical_speed_m_s"]**2
        self.assertAlmostEqual(result["gas_volume_m3"], volume, places=14)
        self.assertAlmostEqual(up, drag, places=12)
        self.assertAlmostEqual(result["total_ascent_mass_kg"], 3.8)

    def test_insufficient_lift_stops_not_constant_speed_fallback(self):
        config = physical_configuration()
        config["ascent"]["payload_mass_kg"] = 100
        result = simulate(config, AnalyticWeather())
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop_reason"]["code"], "INSUFFICIENT_LIFT")

    def test_physical_flight_has_altitude_burst_and_postburst_cda(self):
        config = physical_configuration()
        config["descent"] = {"mode": "constant_cda", "mass_kg": 2.3, "drag_area_m2": .8}
        result = simulate(config, AnalyticWeather(variable=True))
        self.assertTrue(result["complete"], result["stop_reason"])
        self.assertEqual(result["events"][0]["altitude_m"], 1000)
        self.assertIn("gas_volume_m3", result["records"][0])
        last = result["records"][-1]
        self.assertAlmostEqual(.5*last["air_density_kg_m3"]*.8*last["vertical_speed_m_s"]**2,
                               2.3*9.80665, places=12)

    def test_diameter_burst_height_matches_exponential_pressure_identity(self):
        config = physical_configuration(max_step_s=2)
        config["burst"] = {"mode": "diameter", "diameter_m": 2.}
        weather = AnalyticWeather(variable=True)
        surface_pressure = 1.225*287.05*weather.temperature
        burst_volume = math.pi*2**3/6
        initial_volume = .6*2077.1*weather.temperature/surface_pressure
        expected_height = 8400*math.log(burst_volume/initial_volume)
        self.assertGreater(expected_height, 10)
        result = simulate(config, weather)
        self.assertTrue(result["complete"], result["stop_reason"])
        self.assertAlmostEqual(result["events"][0]["altitude_m"], expected_height, delta=.0001)
        self.assertGreaterEqual(result["events"][0]["gas_diameter_m"], 2.)
        self.assertAlmostEqual(result["events"][0]["gas_diameter_m"], 2., delta=1e-8)

    def test_step_refinement_converges_nonconstant_vertical_model(self):
        outputs = []
        for step in (80, 40, 20, 2):
            config = physical_configuration(max_step_s=step, event_tolerance_s=.000001)
            config["burst"]["altitude_m"] = 25000
            config["descent"] = {"mode": "rated_speed", "reference_speed_m_s": 6,
                                 "density_model": "exponential"}
            result = simulate(config, AnalyticWeather(u=30, v=10, variable=True))
            self.assertTrue(result["complete"], result["stop_reason"])
            outputs.append(result["summary"]["duration_s"])
        errors = [abs(value-outputs[-1]) for value in outputs[:-1]]
        self.assertLess(errors[1], errors[0]/4)
        self.assertLess(errors[2], errors[1]/4)
        self.assertLess(errors[2], .01)

    def test_missing_humidity_fails_explicitly(self):
        class MissingHumidity(AnalyticWeather):
            def sample(self, *args, **kwargs):
                sample = super().sample(*args, **kwargs)
                sample.pop("specific_humidity_kg_kg", None)
                return sample
        result = simulate(physical_configuration(), MissingHumidity())
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop_reason"]["code"], "MISSING_WEATHER_FIELD")


class ValidationTests(unittest.TestCase):
    def test_solver_tolerances_have_named_units_and_reject_invalid_control(self):
        config=validate_config(configuration())
        self.assertEqual(set(config['integration']['absolute_tolerance']),
                         {'latitude_deg','longitude_deg','altitude_m'})
        for controls in ({'relative_tolerance':0},
                         {'relative_tolerance':1e-30},
                         {'absolute_tolerance':{'altitude_m':-1}},
                         {'absolute_tolerance':{'unknown_axis':1}},
                         {'absolute_tolerance':[1,2,3]}):
            with self.subTest(controls=controls),self.assertRaises(FlightError):
                validate_config(configuration(**controls))

    def test_invalid_modes_never_fall_back(self):
        for section in ("ascent", "burst", "descent"):
            config = configuration()
            config[section]["mode"] = "future_inertial_model"
            with self.subTest(section=section), self.assertRaisesRegex(FlightError, "unknown"):
                validate_config(config)

    def test_unimplemented_nested_physics_cannot_be_silently_ignored(self):
        config = configuration()
        config["ascent"]["inertia"] = True
        with self.assertRaises(FlightError) as context:
            validate_config(config)
        self.assertEqual(context.exception.code, "UNSUPPORTED_CONFIG_FIELD")

    def test_diameter_burst_requires_gas_model(self):
        config = configuration()
        config["burst"] = {"mode": "diameter", "diameter_m": 8}
        with self.assertRaises(FlightError):
            validate_config(config)

    def test_nonfinite_bool_and_ambiguous_time_rejected(self):
        for value in (True, float("nan"), float("inf"), 10**1000):
            config = configuration()
            config["ascent"]["speed_m_s"] = value
            with self.subTest(value=type(value)), self.assertRaises(FlightError):
                validate_config(config)
        for value in ("2026-09-23T00:00:00", "2026-09-23T00:00:00+09:00", "bad"):
            config = configuration()
            config["launch"]["time_utc"] = value
            with self.subTest(value=value), self.assertRaises(FlightError):
                validate_config(config)

    def test_invalid_limits_and_humidity_rejected(self):
        for key, value in (("max_steps", True), ("max_steps", 0), ("max_step_s", 0),
                           ("event_tolerance_s", 1e-9)):
            with self.subTest(key=key), self.assertRaises(FlightError):
                validate_config(configuration(**{key: value}))
        for q in (-.1, 1., float("nan")):
            with self.subTest(q=q), self.assertRaises(FlightError):
                moist_air_density(100000, 280, q)


if __name__ == "__main__":
    unittest.main()
