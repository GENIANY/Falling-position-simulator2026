"""JRA-3Q analysis binding for saved regular-Gaussian model-level fields.

Native UTCs, hybrid half coefficients and surface pressure are retained. No HTTP
or fixture decoder enters the simulator. Full pressure follows JMA TL479 section
8.1, rather than ERA5's arithmetic average of half pressures.
"""
from copy import deepcopy
from datetime import timedelta
import hashlib
import json
import math
from .fields import WeatherError, _array, _required_object, _utc
from .model_levels import ModelLevelField
from .model_surface import ModelSurfaceField, POLICY, SURFACE_FIELDS

SCHEMA = "balloon.weather.jra3q_model/1"
PRODUCT = "jra3q.ncar.regular_gaussian.model_analysis"
SURFACE_SCHEMA = "balloon.weather.jra3q_surface/1"
SURFACE_PRODUCT = "jra3q.ncar.regular_gaussian.model_surface_analysis"
# Float-normalized [A_half_Pa, B_half], from the independently preserved d640000
# coordinate response. Another coefficient revision needs explicit review, not
# acceptance just because it happens to produce 100 monotonic pressures.
COEFFICIENT_SHA256 = "a02303033541811e03fe3e4baa76f2d678480ecd6c39a44f5a910d38a4c079ce"


def full_pressure_pa(half):
    """Simmons–Burridge pressure, surface-up; top full level = lower half / 2."""
    if not isinstance(half, (list, tuple)):
        raise WeatherError("INVALID_PRESSURE", "half pressure must be an array")
    half = _array(half, (len(half),), "half pressure")
    if (len(half) < 2 or any(p is None or p < 0 for p in half) or half[-1] != 0
            or any(a <= b for a, b in zip(half, half[1:]))):
        raise WeatherError("INVALID_PRESSURE", "half pressure must descend to zero")
    result = []
    for lower, upper in zip(half, half[1:]):
        if upper == 0:
            value = lower / 2
        else:
            ratio = (lower - upper) / upper
            value = lower * math.exp(math.log1p(ratio) / ratio - 1)
        if not upper < value < lower:
            raise WeatherError("NUMERIC_UNSUPPORTED", "full pressure not representable")
        result.append(value)
    return tuple(result)


class Jra3qModelField(ModelLevelField):
    """Validated saved JRA field, deliberately without a ground-layer bridge."""

    def __init__(self, bundle):
        _required_object(bundle, ("schema", "product", "axes", "fields", "surface", "hybrid", "metadata"), "bundle")
        if bundle["schema"] != SCHEMA or bundle["product"] != PRODUCT:
            raise WeatherError("INVALID_BUNDLE", "unsupported JRA schema/product")
        axes = _required_object(bundle["axes"], ("time_utc", "model_level", "latitude_deg", "longitude_deg"), "axes")
        if not isinstance(axes["time_utc"], (list, tuple)):
            raise WeatherError("INVALID_AXIS", "time must be an array")
        times = tuple(_utc(t) for t in axes["time_utc"])
        if (not times or any(t.hour % 6 or t.minute or t.second or t.microsecond for t in times)
                or any(b - a != timedelta(hours=6) for a, b in zip(times, times[1:]))):
            raise WeatherError("EXPECTED_TIME_GAP", "JRA analyses must be contiguous 00/06/12/18 UTC")
        if axes["model_level"] != list(range(1, 101)):
            raise WeatherError("INVALID_AXIS", "JRA requires all 100 surface-up levels")
        for name in ("latitude_deg", "longitude_deg"):
            if not isinstance(axes[name], (list, tuple)) or not axes[name]:
                raise WeatherError("INVALID_AXIS", name)
        shape = (len(times), len(axes["latitude_deg"]), len(axes["longitude_deg"]))
        surface = _required_object(bundle["surface"], ("pressure_pa", "geopotential_height_gpm"), "surface")
        sp = _array(surface["pressure_pa"], shape, "surface pressure")
        hybrid = _required_object(bundle["hybrid"], ("a_half_pa", "b_half"), "hybrid")
        a, b = (_array(hybrid[n], (101,), n) for n in ("a_half_pa", "b_half"))
        if (any(v is None for v in (*a, *b)) or a[0] != 0 or b[0] != 1 or a[-1] != 0 or b[-1] != 0):
            raise WeatherError("INVALID_PRESSURE", "JRA half coefficients must join surface and zero top")
        coordinate_hash = hashlib.sha256(json.dumps([a, b], separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        if coordinate_hash != COEFFICIENT_SHA256:
            raise WeatherError("UNSUPPORTED_VERTICAL_COORDINATE", "unreviewed JRA half coefficients")
        columns = [[[((None,) * 100 if sp[t][j][i] is None else
                     full_pressure_pa([aa + bb * sp[t][j][i] for aa, bb in zip(a, b)]))
                    for i in range(shape[2])] for j in range(shape[1])] for t in range(shape[0])]
        pressures = [[[[columns[t][j][i][k] for i in range(shape[2])]
                       for j in range(shape[1])] for k in range(100)] for t in range(shape[0])]
        fields = _required_object(bundle["fields"], ("geopotential_height_gpm",), "fields")
        if not isinstance(bundle["metadata"], dict):
            raise WeatherError("INVALID_BUNDLE", "metadata must be an object")
        metadata = deepcopy(bundle["metadata"])
        metadata.update(product=PRODUCT, time_kind="analysis_valid_utc",
                        hybrid_coordinate_sha256=coordinate_hash,
                        vertical_pressure_method="JMA Simmons-Burridge; top half/2",
                        vertical_interpolation="linear in column geopotential height, including pressure",
                        surface_policy="strict column support; no extrapolation or terrain clamp",
                        altitude_api="geometric ASL m; spherical radius 6371000 m")
        super().__init__(times=times, latitudes=axes["latitude_deg"], longitudes=axes["longitude_deg"],
                         levels=axes["model_level"], heights=fields["geopotential_height_gpm"],
                         pressures=pressures, fields={n: v for n, v in fields.items() if n != "geopotential_height_gpm"},
                         surface_pressure=sp, surface_height=surface["geopotential_height_gpm"], metadata=metadata)


class Jra3qSurfaceField(ModelSurfaceField):
    """Explicit surface-analysis option; schema1 strict callers stay unchanged."""

    def __init__(self, bundle):
        _required_object(bundle, ("schema", "product", "axes", "fields", "surface", "hybrid", "metadata", "reconstruction"), "bundle")
        if bundle["schema"] != SURFACE_SCHEMA or bundle["product"] != SURFACE_PRODUCT:
            raise WeatherError("INVALID_BUNDLE", "unsupported JRA surface schema/product")
        reconstruction = bundle["reconstruction"]
        if (not isinstance(reconstruction, dict) or set(reconstruction) != {"policy", "join_model_levels"}
                or reconstruction["policy"] != POLICY):
            raise WeatherError("INVALID_RECONSTRUCTION", "explicit native_horizontal_first_surface_v1 policy required")
        diagnostic_names = tuple(name for name, _ in SURFACE_FIELDS.values())
        surface = _required_object(bundle["surface"], ("pressure_pa", "geopotential_height_gpm", *diagnostic_names), "surface")
        strict = {name: bundle[name] for name in ("axes", "fields", "hybrid", "metadata")}
        strict.update(schema=SCHEMA, product=PRODUCT,
                      surface={name: surface[name] for name in ("pressure_pa", "geopotential_height_gpm")})
        source = Jra3qModelField(strict)
        super().__init__(source, {name: surface[name] for name in diagnostic_names}, reconstruction["join_model_levels"])
        self.metadata.update(schema=SURFACE_SCHEMA, product=SURFACE_PRODUCT)
