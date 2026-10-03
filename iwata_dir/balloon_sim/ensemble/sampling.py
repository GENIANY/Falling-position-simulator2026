"""Explicit one-parameter sensitivity assumptions, resolved to physical inputs."""
from copy import deepcopy
import hashlib
import json

import numpy as np

from ..flight.config import FlightError, _number, validate_config

RESOLVER_VERSION = "flight-primitive/1"
VARIABLES = {
    "gas_mass_kg": ("kg", "ascent", "isothermal_buoyancy", "gas_mass_kg"),
    "burst_altitude_m": ("m", "burst", "altitude", "altitude_m"),
    "reference_descent_speed_m_s": ("m/s", "descent", "rated_speed", "reference_speed_m_s"),
}


def _invalid(message):
    raise FlightError("INVALID_SAMPLING", message)


def freeze_drawset(spec):
    """Freeze realized values, not merely a seed or a mutable RNG state.

    Uniform bounds and their reason are supplied by the caller, not inferred
    from product data. A deployment may further bound the total case x draw cost.
    """
    fields = {"variable", "unit", "distribution", "reason", "seed", "n"}
    if not isinstance(spec, dict) or set(spec) != fields:
        _invalid("sampling needs exactly variable, unit, distribution, reason, seed, n")
    variable = spec["variable"]
    if not isinstance(variable, str) or variable not in VARIABLES:
        _invalid("unsupported primitive variable")
    if spec["unit"] != VARIABLES[variable][0]:
        _invalid("primitive unit does not match the selected variable")
    dist = spec["distribution"]
    if not isinstance(dist, dict) or set(dist) != {"family", "low", "high"} or dist["family"] != "uniform":
        _invalid("only an explicitly bounded uniform sensitivity assumption is implemented")
    low = _number(dist["low"], "sampling.low")
    high = _number(dist["high"], "sampling.high")
    if not low < high or not np.isfinite(high - low):
        _invalid("uniform bounds must be finite and low < high")
    if not isinstance(spec["reason"], str) or not spec["reason"].strip() or len(spec["reason"]) > 2000:
        _invalid("state the reason for this assumed interval (1..2000 characters)")
    n, seed = spec["n"], spec["seed"]
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 256:
        _invalid("this deployment accepts 1..256 draws per plan")
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32:
        _invalid("seed must be an integer in [0, 2^32)")
    rng = np.random.Generator(np.random.PCG64(seed))
    values = rng.uniform(low, high, n).tolist()
    output = {
        "schema": "balloon.sensitivity.drawset/1", "method": "numpy.PCG64.uniform/1",
        "numpy_version": np.__version__, "resolver_version": RESOLVER_VERSION,
        "variable": variable, "unit": spec["unit"],
        "distribution": {"family": "uniform", "low": low, "high": high},
        "reason": spec["reason"].strip(), "seed": seed, "n": n,
        "interpretation": "assumed_sensitivity", "pairing": "same_physical_value",
        "draws": [{"ordinal": i + 1, "value": value, "weight": 1} for i, value in enumerate(values)],
    }
    encoded = json.dumps(output, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    identity = "drawset-" + hashlib.sha256(encoded.encode()).hexdigest()
    output["drawset_id"] = identity
    for row in output["draws"]:
        row["draw_id"] = identity + ":" + str(row["ordinal"])
    return output


def resolve_config(config, variable, value):
    """Change only an implemented primitive; validate the full resolved input.

    Gas mass belongs to ascent's gas state. It is not added to the independently
    specified effective post-burst mass. Payload and free-lift conversions are
    deliberately absent until their coupled primitive resolver is implemented.
    """
    if variable not in VARIABLES:
        raise FlightError("UNSUPPORTED_SAMPLING_VARIABLE", str(variable))
    c = validate_config(config)
    _, section, mode, field = VARIABLES[variable]
    if c[section]["mode"] != mode:
        raise FlightError("INACTIVE_SAMPLING_VARIABLE", f"{variable} is not used by {section}.{c[section]['mode']}")
    c = deepcopy(c)
    c[section][field] = _number(value, variable)
    return validate_config(c)
