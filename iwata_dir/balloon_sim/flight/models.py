"""Current physical closures and their field requirements, independent of integration.

These finite selections implement flight.config/1. The wider composition prototype
is not an executable model registry. Gas state and moist density are shared
physical evaluations, so future motion/drag choices need not copy their equations.
"""
from copy import deepcopy
from dataclasses import dataclass
import math
from typing import Callable
from .config import (FlightError, _number, GRAVITY_M_S2,
                     DRY_AIR_GAS_CONSTANT, VAPOUR_GAS_CONSTANT)
from .events import BurstEvent

def moist_air_density(pressure_pa, temperature_k, specific_humidity_kg_kg):
    """Ideal moist-air density, q is water-vapour mass / total moist-air mass."""
    p = _number(pressure_pa, "pressure_pa", positive=True)
    temperature = _number(temperature_k, "temperature_k", positive=True)
    q = _number(specific_humidity_kg_kg, "specific_humidity_kg_kg", minimum=0)
    if q >= 1:
        raise FlightError("INVALID_WEATHER", "specific humidity must be less than one")
    density = p / (temperature * (DRY_AIR_GAS_CONSTANT * (1 - q) + VAPOUR_GAS_CONSTANT * q))
    if not math.isfinite(density) or density <= 0:
        raise FlightError("NUMERIC_UNSUPPORTED", "air density is not positive and finite")
    return density


def _density(sample):
    try:
        return moist_air_density(sample["pressure_pa"], sample["temperature_k"],
                                 sample["specific_humidity_kg_kg"])
    except KeyError as exc:
        raise FlightError("MISSING_WEATHER_FIELD", str(exc)) from None
    except FlightError as exc:
        if exc.code == "INVALID_CONFIG":
            raise FlightError("INVALID_WEATHER", str(exc)) from None
        raise


def _gas_state(gas, sample):
    p = sample.get("pressure_pa")
    temperature = sample.get("temperature_k")
    try:
        p = _number(p, "pressure_pa", positive=True)
        temperature = _number(temperature, "temperature_k", positive=True)
    except FlightError as exc:
        raise FlightError("INVALID_WEATHER", str(exc)) from None
    volume = gas["gas_mass_kg"] * gas["gas_constant_j_kg_k"] * temperature / p
    if not math.isfinite(volume) or volume <= 0:
        raise FlightError("NUMERIC_UNSUPPORTED", "gas volume is not finite and positive")
    diameter = (6 * volume / math.pi) ** (1 / 3)
    area = math.pi * diameter * diameter / 4
    return volume, diameter, area


def vertical_state(config, phase, altitude_m, sample):
    """Evaluate the selected quasi-steady velocity and inspectable physics terms."""
    if phase not in ("ascent", "descent"):
        raise FlightError("UNSUPPORTED_MODEL", "unknown flight phase")
    if phase == "ascent":
        ascent = config["ascent"]
        if ascent["mode"] == "constant_speed":
            return {"vertical_speed_m_s": ascent["speed_m_s"]}
        rho = _density(sample)
        volume, diameter, area = _gas_state(ascent, sample)
        mass = ascent["gas_mass_kg"] + ascent["envelope_mass_kg"] + ascent["payload_mass_kg"]
        excess_mass = rho * volume - mass
        if excess_mass <= 0:
            raise FlightError("INSUFFICIENT_LIFT", "equal-temperature model has no positive free lift")
        speed = math.sqrt(2 * GRAVITY_M_S2 * excess_mass / (rho * ascent["drag_coefficient"] * area))
        result = {"vertical_speed_m_s": speed, "air_density_kg_m3": rho,
                  "gas_volume_m3": volume, "gas_diameter_m": diameter,
                  "projected_area_m2": area, "total_ascent_mass_kg": mass,
                  "free_lift_n": GRAVITY_M_S2 * excess_mass}
    else:
        descent = config["descent"]
        if descent["mode"] == "constant_cda":
            rho = _density(sample)
            speed = math.sqrt(2 * GRAVITY_M_S2 * descent["mass_kg"] / (rho * descent["drag_area_m2"]))
            result = {"vertical_speed_m_s": -speed, "air_density_kg_m3": rho}
        elif descent["density_model"] == "weather":
            rho = _density(sample)
            speed = descent["reference_speed_m_s"] * math.sqrt(descent["reference_density_kg_m3"] / rho)
            result = {"vertical_speed_m_s": -speed, "air_density_kg_m3": rho}
        else:
            speed = descent["reference_speed_m_s"] * math.exp(altitude_m / (2 * descent["scale_height_m"]))
            result = {"vertical_speed_m_s": -speed, "density_model": "exponential"}
    if not all(not isinstance(v, (float, int)) or math.isfinite(v) for v in result.values()):
        raise FlightError("NUMERIC_UNSUPPORTED", "non-finite vertical model result")
    return result


@dataclass(frozen=True)
class PhaseModel:
    """Chosen physical evaluator and the weather quantities it consumes."""
    evaluate: Callable
    required_fields: tuple[str, ...]


@dataclass(frozen=True)
class FlightModels:
    """Finite implemented composition consumed by the flight driver.

    This carries callable evaluations, not an assertion that the wider prototype
    catalogue is executable. Additional stateful physics will need an explicit
    state/transition contract; it is not silently accepted by these callbacks.
    """
    ascent: PhaseModel
    descent: PhaseModel
    burst: BurstEvent

    def phase(self, name):
        if name == "ascent":
            return self.ascent
        if name == "descent":
            return self.descent
        raise FlightError("UNSUPPORTED_MODEL", "unknown flight phase")

    def assumptions(self):
        """Current result/1 wording retained; selection does not endorse accuracy."""
        return [
            "no vertical atmospheric wind, horizontal inertia, thermal lag or ground rebound",
            "isothermal mode: fixed gas mass; gas pressure equals external pressure; spherical balloon; constant Cd",
            "descent mode specifies effective post-burst mass/CdA or density-scaled reference speed",
        ]


def compile_models(config):
    """Bind validated flight.config/1 choices once, outside the flight driver.

    The legacy input places gas parameters in ascent. Extract only gas parameters
    here and pass an independent gas-state callable to the event. Neither event
    code nor the driver knows that storage arrangement or the ascent mode name.
    """
    ascent, descent = deepcopy(config["ascent"]), deepcopy(config["descent"])
    wind = ("eastward_wind_m_s", "northward_wind_m_s")
    thermodynamics = ("pressure_pa", "temperature_k", "specific_humidity_kg_kg")
    gas_state = None
    constant_speed = None
    if ascent["mode"] == "constant_speed":
        ascent_fields = wind
        constant_speed = ascent["speed_m_s"]
    else:
        ascent_fields = wind + thermodynamics
        gas = {name: ascent[name] for name in ("gas_mass_kg", "gas_constant_j_kg_k")}
        gas_state = lambda sample: _gas_state(gas, sample)
    descent_fields = wind
    if descent["mode"] == "constant_cda" or descent.get("density_model") == "weather":
        descent_fields += thermodynamics
    # Each closure owns only its selected phase configuration. A gas diagnostic
    # has its own independent parameter closure rather than the entire phase.
    ascent_model = PhaseModel(lambda altitude, sample: vertical_state(
        {"ascent": ascent}, "ascent", altitude, sample), ascent_fields)
    descent_model = PhaseModel(lambda altitude, sample: vertical_state(
        {"descent": descent}, "descent", altitude, sample), descent_fields)
    burst = config["burst"]
    threshold = burst["altitude_m"] if burst["mode"] == "altitude" else burst["diameter_m"]
    event = BurstEvent(burst["mode"], threshold, gas_state, constant_speed)
    return FlightModels(ascent_model, descent_model, event)
