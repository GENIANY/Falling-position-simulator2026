"""Validate the existing flight/1 input; no environment or solver dependency."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import math
import sys

EARTH_RADIUS_M = 6_371_000.0
GRAVITY_M_S2 = 9.80665
DRY_AIR_GAS_CONSTANT = 287.05
VAPOUR_GAS_CONSTANT = 461.5

class FlightError(ValueError):
    """A reproducible model, input or support failure with a machine code."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _number(value, name, *, minimum=None, positive=False):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise FlightError("INVALID_CONFIG", f"{name} must be a finite number")
    try:
        value = float(value)
    except (ValueError, OverflowError):
        raise FlightError("INVALID_CONFIG", f"{name} is not representable") from None
    if not math.isfinite(value) or (positive and value <= 0) or (
            minimum is not None and value < minimum):
        raise FlightError("INVALID_CONFIG", f"{name} is outside its valid range")
    return value


def _utc(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise FlightError("INVALID_CONFIG", "launch.time_utc is not ISO8601") from None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise FlightError("INVALID_CONFIG", "launch.time_utc must explicitly be UTC")
    return value.astimezone(timezone.utc)


def _known_fields(value, allowed, section):
    unknown = set(value) - set(allowed)
    if unknown:
        raise FlightError("UNSUPPORTED_CONFIG_FIELD", f"{section}: unknown fields {sorted(map(str, unknown))}")


def validate_config(config):
    """Return a detached, default-expanded JSON-compatible configuration.

    Coordinates and all launch/burst heights are geometric ASL.  An initial
    above-ground check requires the selected environment and occurs in simulate.
    Extra top-level metadata is retained; unimplemented model modes are errors.
    """
    if not isinstance(config, dict):
        raise FlightError("INVALID_CONFIG", "configuration must be an object")
    c = deepcopy(config)
    if c.get("schema", "balloon.flight.config/1") != "balloon.flight.config/1":
        raise FlightError("INVALID_CONFIG", "unsupported config schema")
    c["schema"] = "balloon.flight.config/1"
    for name in ("launch", "ascent", "burst", "descent"):
        if not isinstance(c.get(name), dict):
            raise FlightError("INVALID_CONFIG", f"{name} must be an object")
    launch = c["launch"]
    _known_fields(launch, ("time_utc", "latitude_deg", "longitude_deg", "altitude_m"), "launch")
    launch["time_utc"] = _utc(launch.get("time_utc")).isoformat()
    for name in ("latitude_deg", "longitude_deg", "altitude_m"):
        launch[name] = _number(launch.get(name), "launch." + name)
    if not -90 < launch["latitude_deg"] < 90:
        raise FlightError("INVALID_CONFIG", "launch latitude must lie strictly between poles")
    if not -180 <= launch["longitude_deg"] <= 180:
        raise FlightError("INVALID_CONFIG", "launch longitude must be in [-180,180]")
    if launch["altitude_m"] <= -EARTH_RADIUS_M:
        raise FlightError("INVALID_CONFIG", "launch radius must be positive")
    ascent = c["ascent"]
    if ascent.get("mode") == "constant_speed":
        _known_fields(ascent, ("mode", "speed_m_s"), "ascent")
        ascent["speed_m_s"] = _number(ascent.get("speed_m_s"), "ascent.speed_m_s", positive=True)
    elif ascent.get("mode") == "isothermal_buoyancy":
        _known_fields(ascent, ("mode", "gas_mass_kg", "envelope_mass_kg", "payload_mass_kg",
                              "drag_coefficient", "gas_constant_j_kg_k"), "ascent")
        for name in ("gas_mass_kg", "drag_coefficient"):
            ascent[name] = _number(ascent.get(name), "ascent." + name, positive=True)
        for name in ("envelope_mass_kg", "payload_mass_kg"):
            ascent[name] = _number(ascent.get(name), "ascent." + name, minimum=0)
        ascent["gas_constant_j_kg_k"] = _number(ascent.get("gas_constant_j_kg_k", 2077.1),
                                               "ascent.gas_constant_j_kg_k", positive=True)
    else:
        raise FlightError("UNSUPPORTED_MODEL", "unknown ascent.mode")
    burst = c["burst"]
    if burst.get("mode") == "altitude":
        _known_fields(burst, ("mode", "altitude_m"), "burst")
        burst["altitude_m"] = _number(burst.get("altitude_m"), "burst.altitude_m")
        if burst["altitude_m"] <= launch["altitude_m"]:
            raise FlightError("INVALID_CONFIG", "burst altitude must exceed launch altitude")
    elif burst.get("mode") == "diameter":
        _known_fields(burst, ("mode", "diameter_m"), "burst")
        if ascent["mode"] != "isothermal_buoyancy":
            raise FlightError("UNSUPPORTED_MODEL", "diameter burst requires gas-volume ascent")
        burst["diameter_m"] = _number(burst.get("diameter_m"), "burst.diameter_m", positive=True)
    else:
        raise FlightError("UNSUPPORTED_MODEL", "unknown burst.mode")
    descent = c["descent"]
    if descent.get("mode") == "constant_cda":
        _known_fields(descent, ("mode", "mass_kg", "drag_area_m2"), "descent")
        for name in ("mass_kg", "drag_area_m2"):
            descent[name] = _number(descent.get(name), "descent." + name, positive=True)
    elif descent.get("mode") == "rated_speed":
        descent["reference_speed_m_s"] = _number(descent.get("reference_speed_m_s"),
                                                 "descent.reference_speed_m_s", positive=True)
        descent.setdefault("density_model", "weather")
        if descent["density_model"] == "weather":
            _known_fields(descent, ("mode", "reference_speed_m_s", "density_model",
                                   "reference_density_kg_m3"), "descent")
            descent["reference_density_kg_m3"] = _number(descent.get("reference_density_kg_m3", 1.225),
                                                        "descent.reference_density_kg_m3", positive=True)
        elif descent["density_model"] == "exponential":
            _known_fields(descent, ("mode", "reference_speed_m_s", "density_model", "scale_height_m"), "descent")
            descent["scale_height_m"] = _number(descent.get("scale_height_m", 8400.0),
                                               "descent.scale_height_m", positive=True)
        else:
            raise FlightError("UNSUPPORTED_MODEL", "unknown descent.density_model")
    else:
        raise FlightError("UNSUPPORTED_MODEL", "unknown descent.mode")
    c.setdefault("integration", {})
    if not isinstance(c["integration"], dict):
        raise FlightError("INVALID_CONFIG", "integration must be an object")
    integration = c["integration"]
    _known_fields(integration, ("max_step_s", "max_duration_s", "event_tolerance_s", "max_steps",
                               "relative_tolerance", "absolute_tolerance"), "integration")
    for name, default in (("max_step_s", 10.0), ("max_duration_s", 14400.0),
                          ("event_tolerance_s", 0.001)):
        integration[name] = _number(integration.get(name, default), "integration." + name, positive=True)
    if integration["event_tolerance_s"] < 1e-6 or integration["max_step_s"] < 1e-6:
        raise FlightError("INVALID_CONFIG", "steps and event tolerance must resolve microsecond UTC")
    count = integration.get("max_steps", 200000)
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 1000000:
        raise FlightError("INVALID_CONFIG", "integration.max_steps must be an integer in [1,1000000]")
    integration["max_steps"] = count
    integration["relative_tolerance"] = _number(integration.get("relative_tolerance", 1e-9),
                                                "integration.relative_tolerance", positive=True)
    if integration["relative_tolerance"] < 100 * sys.float_info.epsilon:
        raise FlightError("INVALID_CONFIG", "relative_tolerance is below SciPy's double-precision floor")
    absolute = integration.setdefault("absolute_tolerance", {})
    if not isinstance(absolute, dict):
        raise FlightError("INVALID_CONFIG", "integration.absolute_tolerance must be an object")
    _known_fields(absolute, ("latitude_deg", "longitude_deg", "altitude_m"), "integration.absolute_tolerance")
    for name, default in (("latitude_deg",1e-9),("longitude_deg",1e-9),("altitude_m",1e-3)):
        absolute[name] = _number(absolute.get(name,default), "integration.absolute_tolerance."+name, positive=True)
    try:
        _utc(launch["time_utc"]) + timedelta(seconds=integration["max_duration_s"])
    except (ValueError, OverflowError):
        raise FlightError("INVALID_CONFIG", "simulation end time is not representable") from None
    return c
