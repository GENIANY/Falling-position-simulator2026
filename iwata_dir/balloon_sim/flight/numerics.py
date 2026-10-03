"""SciPy numerical adapter, independent of weather products and flight models.

SciPy owns local error control, adaptive steps, dense interpolation and roots.
The caller may reject a trial for a domain/support reason and restart from its
last accepted state with a smaller bound. No physical fallback is supplied here.
"""
from dataclasses import dataclass
import math
import numpy as np
import scipy
from scipy.integrate import RK45
from scipy.optimize import brentq


class IntegrationError(ArithmeticError):
    """The numerical method failed, distinct from an RHS/provider exception."""
    code = "NUMERIC_UNSUPPORTED"


@dataclass(frozen=True)
class IntegrationStep:
    start_time: float
    end_time: float
    state: tuple
    interpolate: object

    def state_at(self, time):
        state = tuple(float(value) for value in self.interpolate(time))
        if not all(math.isfinite(value) for value in state):
            raise IntegrationError("SciPy dense output produced a non-finite state")
        return state


class AdaptiveRK45:
    """Advance from the caller's last accepted state using the public step API.

    A failed RHS is propagated unchanged. A rejected trial is recognized on the
    next call by a different start state/time or cap, so its solver is discarded.
    The retained accepted result belongs to the caller, not to this cache.
    """
    def __init__(self, rhs, end_time, *, relative_tolerance, absolute_tolerance):
        self.rhs, self.end_time = rhs, end_time
        self.rtol, self.atol = relative_tolerance, tuple(absolute_tolerance)
        self.reset()

    def reset(self):
        self._solver = None
        self._cap = None

    def trial(self, time, state, maximum_step):
        if (self._solver is None or self._solver.t != time
                or tuple(self._solver.y) != tuple(state) or self._cap != maximum_step):
            self._solver = None
            # An explicit first bound prevents initial-step estimation from
            # probing beyond a support/event boundary already known to the caller.
            self._solver = RK45(self.rhs, time, state, self.end_time,
                                max_step=maximum_step, first_step=min(maximum_step,self.end_time-time),
                                rtol=self.rtol, atol=self.atol)
            self._cap = maximum_step
        try:
            message = self._solver.step()
        except (ValueError, KeyError, OverflowError, ArithmeticError):
            self.reset()
            raise
        if self._solver.status == "failed":
            self.reset()
            raise IntegrationError(message or "SciPy RK45 step failed")
        end = float(self._solver.t)
        values = tuple(float(value) for value in self._solver.y)
        if end <= time or not all(math.isfinite(value) for value in values):
            self.reset()
            raise IntegrationError("SciPy produced a non-increasing time or non-finite state")
        return IntegrationStep(time,end,values,self._solver.dense_output())


def locate_crossing(step, function, tolerance, *, start_time=None):
    """Locate a caller-established crossing on the accepted dense interpolant."""
    left = step.start_time if start_time is None else start_time
    root, result = brentq(lambda time:function(time,step.state_at(time)),
                          left,step.end_time,xtol=tolerance,
                          full_output=True,disp=False)
    if not result.converged:
        raise IntegrationError("SciPy event root did not converge")
    return root-step.start_time,step.state_at(root)


def numerical_metadata(controls):
    return {"backend":"scipy.integrate.RK45", "event_solver":"scipy.optimize.brentq",
            "scipy_version":scipy.__version__, "numpy_version":np.__version__,
            "relative_tolerance":controls["relative_tolerance"],
            "absolute_tolerance":dict(controls["absolute_tolerance"]),
            "event_tolerance_s":controls["event_tolerance_s"],
            "max_step_s":controls["max_step_s"],
            "record_sampling":"accepted adaptive steps and events; nonuniform times"}
