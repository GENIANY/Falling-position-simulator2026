"""Independent equations and boundary contracts for the SciPy numerical adapter."""
from copy import deepcopy
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from balloon_sim.flight.numerics import AdaptiveRK45, IntegrationError, IntegrationStep, locate_crossing
from balloon_sim.environment.fields import PressureLevelField
from balloon_sim.environment.bundle import WeatherField
from balloon_sim.environment.fields import WeatherError
from balloon_sim.flight.models import compile_models
from balloon_sim.flight.events import BurstEvent
from balloon_sim.flight.config import validate_config
from test_flight_weather import fixture, T0
from test_trajectory import configuration, physical_configuration


class NumericalKernelTests(unittest.TestCase):
    def test_tighter_error_control_improves_independent_exponential_solution(self):
        errors=[]
        for tolerance in (1e-5,1e-10):
            solver=AdaptiveRK45(lambda t,y:(y[0],),1,
                                relative_tolerance=tolerance,absolute_tolerance=(tolerance*.01,))
            time,state=0,(1.,)
            while time < 1:
                step=solver.trial(time,state,min(.5,1-time))
                time,state=step.end_time,step.state
            errors.append(abs(state[0]-math.e))
        self.assertLess(errors[1],errors[0]/1000)
        self.assertLess(errors[1],1e-9)

    def test_vector_state_uses_coupled_rhs_and_time(self):
        # x'=v, v'=6t with x(0)=0,v(0)=0 gives x=t^3,v=3t^2.
        solver=AdaptiveRK45(lambda t,y:(y[1],6*t),2,
                            relative_tolerance=1e-9,absolute_tolerance=(1e-10,1e-10))
        step=solver.trial(0,(0.,0.),2)
        self.assertAlmostEqual(step.state[0],8.,places=12)
        self.assertAlmostEqual(step.state[1],12.,places=12)
        self.assertAlmostEqual(step.state_at(1)[0],1.,places=12)

    def test_event_bracket_for_both_directions(self):
        for speed,target in ((3.,7.),(-3.,-7.)):
            solver=AdaptiveRK45(lambda t,y:(speed,),4,
                                relative_tolerance=1e-9,absolute_tolerance=(1e-10,))
            step=solver.trial(0,(0.,),4)
            time,state=locate_crossing(step,lambda t,y:y[0]-target,1e-8)
            self.assertAlmostEqual(time,7/3,delta=1e-8)
            self.assertAlmostEqual(state[0],target,delta=3e-8)

    def test_trial_failure_does_not_reinterpret_rhs_exception(self):
        original=FloatingPointError('source-specific arithmetic failure')
        def failed(t,y):
            raise original
        with self.assertRaises(FloatingPointError) as caught:
            AdaptiveRK45(failed,1,relative_tolerance=1e-9,
                         absolute_tolerance=(1e-10,)).trial(0,(1.,),1)
        self.assertIs(caught.exception,original)
        with self.assertRaises(IntegrationError):
            IntegrationStep(0,1,(1.,),lambda time:(math.inf,)).state_at(.5)

    def test_root_nonconvergence_is_a_numerical_failure_not_an_unhandled_runtime_error(self):
        step=IntegrationStep(0,1,(1.,),lambda time:(time,))
        with patch('balloon_sim.flight.numerics.brentq',
                   return_value=(.5,SimpleNamespace(converged=False))):
            with self.assertRaises(IntegrationError) as caught:
                locate_crossing(step,lambda time,state:state[0]-.5,1e-6)
        self.assertEqual(caught.exception.code,'NUMERIC_UNSUPPORTED')


class ProductBoundaryTests(unittest.TestCase):
    def test_product_schedule_is_bound_at_bundle_entry_not_reconstruction(self):
        bundle=fixture()
        # A non-GFS product can have a different valid-time schedule, but the
        # old public GFS bundle still rejects a run inconsistent with its grid.
        bundle['metadata']['run_utc']='2026-09-22T18:01:00+00:00'
        field=PressureLevelField(bundle)
        self.assertNotIn('coarse_gfs_orography',field.sample(T0,33,135,100)['quality'])
        with self.assertRaises(WeatherError) as caught:
            WeatherField(bundle)
        self.assertEqual(caught.exception.code,'INVALID_RUN')

    def test_source_quality_policy_is_detached_from_input(self):
        bundle=fixture(); original=deepcopy(bundle)
        flags=['external_coarse_terrain']
        field=PressureLevelField(bundle,quality_flags=flags)
        flags.append('later_mutation')
        sample=field.sample(T0,33,135,100)
        self.assertIn('external_coarse_terrain',sample['quality'])
        self.assertNotIn('later_mutation',sample['quality'])
        self.assertEqual(bundle,original)


class ModelBoundaryTests(unittest.TestCase):
    def test_compiled_gas_diagnostic_is_detached_from_legacy_phase_storage(self):
        config=validate_config(physical_configuration())
        selected=compile_models(config)
        config['ascent']['gas_mass_kg']=999
        sample={'pressure_pa':90000.,'temperature_k':280.,'specific_humidity_kg_kg':.01}
        diagnostic=selected.burst.diagnostics(sample)
        self.assertAlmostEqual(diagnostic['gas_volume_m3'],.6*2077.1*280/90000)
        self.assertEqual(selected.ascent.evaluate(1000,sample)['gas_volume_m3'],diagnostic['gas_volume_m3'])
        self.assertIn('specific_humidity_kg_kg',selected.ascent.required_fields)

    def test_event_consumes_gas_provider_without_any_ascent_config(self):
        event=BurstEvent('diameter',2.,lambda sample:(4.,3.,5.))
        self.assertEqual(event.value(1000,{}),1.)
        self.assertEqual(event.diagnostics({}),{'gas_volume_m3':4.,'gas_diameter_m':3.})
        self.assertIsNone(event.exact_step(1000))

    def test_simple_path_has_no_unused_gas_or_thermodynamic_requirements(self):
        config=configuration()
        config['descent']={'mode':'rated_speed','reference_speed_m_s':5.,'density_model':'exponential'}
        selected=compile_models(validate_config(config))
        wind=('eastward_wind_m_s','northward_wind_m_s')
        self.assertEqual(selected.ascent.required_fields,wind)
        self.assertEqual(selected.descent.required_fields,wind)
        self.assertEqual(selected.burst.diagnostics(),{})
        self.assertEqual(selected.burst.exact_step(10),198)


if __name__=='__main__':
    unittest.main()
