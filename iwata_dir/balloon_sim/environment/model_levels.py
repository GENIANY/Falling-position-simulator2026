"""Strict model-column reconstruction, without product calendars or I/O.

Each positive-weight column must support the queried height. Pressure is linear
in geopotential height, matching the reviewed JRA prototype; the pressure-level
field retains its separate logarithmic-pressure and surface-bridge policies.
"""
from copy import deepcopy
import math
from .fields import (FIELD_NAMES, WeatherError, _array, _axis, _bracket, _number,
                     _utc, geometric_to_geopotential, geopotential_to_geometric)


class ModelLevelField:
    """Column-first interpolation with the flight kernel's geometric-ASL API."""

    def __init__(self, *, times, latitudes, longitudes, levels, heights, pressures,
                 fields, surface_pressure, surface_height, metadata):
        self.times = tuple(_utc(t) for t in times)
        if not self.times or any(b <= a for a, b in zip(self.times, self.times[1:])):
            raise WeatherError("INVALID_AXIS", "time must ascend")
        self.latitudes = _axis(latitudes, "latitude")
        self.longitudes = _axis(longitudes, "longitude")
        if not (-90 <= self.latitudes[0] <= self.latitudes[-1] <= 90
                and -180 <= self.longitudes[0] <= self.longitudes[-1] <= 360
                and self.longitudes[-1] - self.longitudes[0] < 360):
            raise WeatherError("INVALID_AXIS", "unsupported geographic coordinates")
        if (not isinstance(levels, (list, tuple)) or not levels
                or any(type(k) is not int for k in levels)
                or tuple(levels) != tuple(range(1, len(levels) + 1))):
            raise WeatherError("INVALID_AXIS", "model levels must be contiguous surface-up 1..N")
        self.levels = tuple(levels)
        shape = (len(self.times), len(self.levels), len(self.latitudes), len(self.longitudes))
        self.heights = _array(heights, shape, "geopotential height")
        self.pressures = _array(pressures, shape, "full pressure")
        if not isinstance(fields, dict) or set(fields) - (set(FIELD_NAMES) - {"pressure_pa"}):
            raise WeatherError("INVALID_BUNDLE", "unknown model field")
        self.fields = {name: _array(value, shape, name) for name, value in fields.items()}
        self.fields["pressure_pa"] = self.pressures
        self.surface_pressure = _array(surface_pressure, (shape[0], shape[2], shape[3]), "surface pressure")
        self.surface_height = _array(surface_height, (shape[0], shape[2], shape[3]), "surface height")
        if not isinstance(metadata, dict):
            raise WeatherError("INVALID_BUNDLE", "metadata must be an object")
        self.metadata = deepcopy(metadata)
        for t in range(shape[0]):
            for j in range(shape[2]):
                for i in range(shape[3]):
                    sp = self.surface_pressure[t][j][i]
                    if sp is not None and sp <= 0:
                        raise WeatherError("INVALID_PRESSURE", "surface pressure")
                    for array, ascending in ((self.heights, True), (self.pressures, False)):
                        known = [array[t][k][j][i] for k in range(shape[1]) if array[t][k][j][i] is not None]
                        if any(b <= a if ascending else b >= a for a, b in zip(known, known[1:])):
                            raise WeatherError("INVALID_COLUMN", "height/pressure must be monotonic")
                    for k in range(shape[1]):
                        for name, array in self.fields.items():
                            value = array[t][k][j][i]
                            if value is not None:
                                self._check_value(name, value)

    @staticmethod
    def _check_value(name, value):
        if (not math.isfinite(value) or (name in ("pressure_pa", "temperature_k") and value <= 0)
                or (name == "specific_humidity_kg_kg" and not 0 <= value < 1)):
            raise WeatherError("INVALID_FIELD_VALUE", name)
        return value

    def _support(self, time_utc, latitude_deg, longitude_deg):
        longitude = _number(longitude_deg, "longitude")
        # Equivalent coordinate notation is allowed; no seam interpolation or
        # periodic duplication of a regional field is implied.
        longitude = next((x for x in (longitude, longitude + 360, longitude - 360)
                          if self.longitudes[0] <= x <= self.longitudes[-1]), longitude)
        axes = (_bracket(self.times, _utc(time_utc), "TIME_OUT_OF_RANGE"),
                _bracket(self.latitudes, _number(latitude_deg, "latitude"), "LATITUDE_OUT_OF_RANGE"),
                _bracket(self.longitudes, longitude, "LONGITUDE_OUT_OF_RANGE"))
        return tuple((t, j, i, wt * wy * wx) for t, wt in axes[0]
                     for j, wy in axes[1] for i, wx in axes[2])

    def _ground(self, support):
        height = 0.0
        for t, j, i, weight in support:
            value = self.surface_height[t][j][i]
            if value is None:
                raise WeatherError("MISSING_SURFACE_SUPPORT", f"column {t},{j},{i}")
            height += weight * value
        return height

    def ground_altitude(self, time_utc, latitude_deg, longitude_deg):
        return geopotential_to_geometric(self._ground(self._support(time_utc, latitude_deg, longitude_deg)))

    def sample(self, time_utc, latitude_deg, longitude_deg, altitude_m, fields=None):
        requested = FIELD_NAMES if fields is None else fields
        if (not isinstance(requested, (list, tuple)) or not requested
                or any(not isinstance(name, str) for name in requested)
                or len(set(requested)) != len(requested)):
            raise WeatherError("INVALID_REQUIRED_FIELDS", "nonempty distinct field names required")
        absent = set(requested) - self.fields.keys()
        if absent:
            raise WeatherError("MISSING_CAPABILITY", ",".join(sorted(absent)))
        support = self._support(time_utc, latitude_deg, longitude_deg)
        height = geometric_to_geopotential(altitude_m)
        ground = self._ground(support)
        values = {name: 0.0 for name in requested}
        for t, j, i, weight in support:
            sp, local_ground = self.surface_pressure[t][j][i], self.surface_height[t][j][i]
            if sp is None or local_ground is None:
                raise WeatherError("MISSING_SURFACE_SUPPORT", f"column {t},{j},{i}")
            if height < local_ground:
                raise WeatherError("BELOW_MODEL_SURFACE", f"column {t},{j},{i}")
            heights = tuple(plane[j][i] for plane in self.heights[t])
            if any(h is None for h in heights):
                raise WeatherError("MISSING_HEIGHT_SUPPORT", f"column {t},{j},{i}")
            for k, wz in _bracket(heights, height, "HEIGHT_OUT_OF_RANGE"):
                pressure = self.pressures[t][k][j][i]
                if pressure is None:
                    raise WeatherError("MISSING_DATA", "full pressure coordinate missing")
                if pressure > sp or heights[k] < local_ground:
                    raise WeatherError("BELOW_MODEL_SURFACE", f"cell {t},{k},{j},{i}")
                combined = weight * wz
                if not math.isfinite(combined) or combined <= 0:
                    raise WeatherError("NUMERIC_UNSUPPORTED", "combined weight not representable")
                for name in requested:
                    value = self.fields[name][t][k][j][i]
                    if value is None:
                        raise WeatherError("MISSING_DATA", f"{name} at {t},{k},{j},{i}")
                    values[name] += combined * value
        for name, value in values.items():
            self._check_value(name, value)
        return {**values, "ground_altitude_m": geopotential_to_geometric(ground),
                "quality": ["spherical_geopotential_height_approximation",
                            "strict_model_column_support", "height_linear_pressure",
                            "model_orography_not_fine_dem"]}
