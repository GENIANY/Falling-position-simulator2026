"""Compatibility entry for flight.config/1 and existing public imports.

Definitions live under flight by responsibility. Keep this entry while existing
examples and callers use balloon_sim.dynamics; reconsider removal only at an
explicit API migration after all callers and unique evidence have been checked.
Internal implementation does not import this compatibility module.
"""
from .flight.config import (FlightError, validate_config, EARTH_RADIUS_M,
                            GRAVITY_M_S2, DRY_AIR_GAS_CONSTANT, VAPOUR_GAS_CONSTANT)
from .flight.models import moist_air_density, vertical_state
from .flight.trajectory import simulate

__all__ = ["FlightError", "validate_config", "moist_air_density", "vertical_state", "simulate"]
