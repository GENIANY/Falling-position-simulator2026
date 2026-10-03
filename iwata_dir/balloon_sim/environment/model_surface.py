"""Opt-in surface reconstruction of validated model levels; no product I/O.

At each original UTC, mix corresponding native levels horizontally, query that
virtual column at the same absolute geopotential height, then interpolate time.
This changes interior queries at all heights, not merely the bottom gap. It is
an engineering approximation, not a conservative or hydrostatic reconstruction.
"""
from copy import deepcopy
import math

from .fields import (FIELD_NAMES, WeatherError, _array, _bracket,
                     geometric_to_geopotential as to_h, geopotential_to_geometric as to_z)
from .model_levels import ModelLevelField

POLICY = "native_horizontal_first_surface_v1"
SURFACE_FIELDS = {
    "temperature_k": ("temperature_2m_k", 2),
    "specific_humidity_kg_kg": ("specific_humidity_2m_kg_kg", 2),
    "eastward_wind_m_s": ("eastward_wind_10m_m_s", 10),
    "northward_wind_m_s": ("northward_wind_10m_m_s", 10),
}
JOIN_LEVELS = {name: 2 if name in ("eastward_wind_m_s", "northward_wind_m_s") else 1
               for name in FIELD_NAMES}


class ModelSurfaceField:
    """B reconstruction only; fixed join geometry is checked across the window.

    Missing scalar values remain local to consumed positive-weight supports.
    Missing join/terrain geometry cannot be inferred from neighbouring columns.
    """

    def __init__(self, source, surface, join_model_levels):
        if not isinstance(source, ModelLevelField):
            raise WeatherError("INVALID_BUNDLE", "validated model-level field required")
        if (not isinstance(join_model_levels, dict) or set(join_model_levels) != set(JOIN_LEVELS)
                or any(type(value) is not int for value in join_model_levels.values())
                or join_model_levels != JOIN_LEVELS or len(source.levels) < 2):
            raise WeatherError("INVALID_RECONSTRUCTION", "v1 requires fixed p/T/q level1 and u/v level2 joins")
        names = {name for name, _ in SURFACE_FIELDS.values()}
        if not isinstance(surface, dict) or set(surface) != names:
            raise WeatherError("INVALID_BUNDLE", "four 2m/10m surface analysis arrays required")
        self.source = source
        self.join_model_levels = dict(join_model_levels)
        shape = (len(source.times), len(source.latitudes), len(source.longitudes))
        self.surface = {name: _array(surface[name], shape, name) for name in sorted(names)}
        self._validate_fixed_joins()
        self.metadata = deepcopy(source.metadata)
        self.metadata.update(
            reconstruction_policy=POLICY,
            surface_policy="fixed native joins; 2m T/q and 10m u/v held below anchors",
            join_model_levels=dict(self.join_model_levels),
            vertical_interpolation="horizontal native-level means at each original UTC, then linear in absolute H, then time",
            pressure_interpolation="original-column full pressure, horizontal mean, linear in geopotential height",
            time_order="independent reconstruction at each original UTC, then linear time",
            native_wind_not_used_model_levels=[1],
            native_wind_replacement="level1 wind is replaced by the 10m analysis and the bridge to level2; T/q/p level1 retained",
            reconstruction_scope="horizontal-before-height changes interior values at all heights, including above the bridge",
            fixed_join_validation="all original UTCs/columns; terrain and configured join geometry must be present",
            diagnostic_value_validation="each consumed positive-weight value before averaging; unused diagnostics not required",
            scope="explicit opt-in engineering reconstruction; scientific accuracy and conservation not established",
        )

    def __getattr__(self, name):
        return getattr(self.source, name)

    def _validate_fixed_joins(self):
        source = self.source
        for t in range(len(source.times)):
            for j in range(len(source.latitudes)):
                for i in range(len(source.longitudes)):
                    ground = source.surface_height[t][j][i]
                    if ground is None:
                        raise WeatherError("MISSING_SURFACE_SUPPORT", f"join geometry {t},{j},{i}")
                    for name, level in self.join_model_levels.items():
                        height = source.heights[t][level - 1][j][i]
                        if height is None:
                            raise WeatherError("MISSING_HEIGHT_SUPPORT", f"join geometry {t},{level},{j},{i}")
                        offset = 0 if name == "pressure_pa" else SURFACE_FIELDS[name][1]
                        if height <= to_h(to_z(ground) + offset):
                            raise WeatherError("SURFACE_JOIN_UNSUPPORTED", f"{name} level {level} column {t},{j},{i}")

    def ground_altitude(self, time_utc, latitude_deg, longitude_deg):
        return self.source.ground_altitude(time_utc, latitude_deg, longitude_deg)

    def _mix(self, array, members, name):
        values = [(array[t][j][i], weight) for t, j, i, weight in members]
        if any(value is None for value, _ in values):
            raise WeatherError("MISSING_DATA", name)
        physical_name = next((n for n, (diagnostic, _) in SURFACE_FIELDS.items() if diagnostic == name), name)
        if physical_name == "surface pressure":
            physical_name = "pressure_pa"
        if physical_name in FIELD_NAMES:
            for value, _ in values:
                self.source._check_value(physical_name, value)
        result = sum(value * weight for value, weight in values)
        if not math.isfinite(result):
            raise WeatherError("INVALID_FIELD_VALUE", name)
        return result

    def _column(self, members, height, requested):
        source = self.source
        ground = self._mix(source.surface_height, members, "surface H")
        sp = self._mix(source.surface_pressure, members, "surface pressure")
        if height < ground - 1e-7:
            raise WeatherError("BELOW_MODEL_SURFACE", "virtual column")
        height = max(height, ground)  # inverse-height roundoff only; no terrain extension
        heights = [self._mix([planes[k] for planes in source.heights], members, "native H")
                   for k in range(len(source.levels))]
        if any(b <= a for a, b in zip(heights, heights[1:])):
            raise WeatherError("INVALID_COLUMN", "mixed heights not ascending")

        def native(name, k):
            for t, j, i, _ in members:
                pressure = source.pressures[t][k][j][i]
                if pressure is None:
                    raise WeatherError("MISSING_DATA", "native pressure")
                source._check_value("pressure_pa", pressure)
                if (source.heights[t][k][j][i] < source.surface_height[t][j][i]
                        or pressure > source.surface_pressure[t][j][i]):
                    raise WeatherError("BELOW_MODEL_SURFACE", "selected native node")
            return source._check_value(name, self._mix([planes[k] for planes in source.fields[name]], members, name))

        result, quality, bridge_height = {}, set(), 0.0
        for name in requested:
            join = self.join_model_levels[name] - 1
            offset = 0 if name == "pressure_pa" else SURFACE_FIELDS[name][1]
            anchor = to_h(to_z(ground) + offset)
            if heights[join] <= anchor:
                raise WeatherError("SURFACE_JOIN_UNSUPPORTED", f"{name} level {join + 1}")
            if height < heights[join]:
                bridge_height = max(bridge_height, to_z(heights[join]) - to_z(ground))
                quality.add("surface_layer_bridge")
                low = sp if name == "pressure_pa" else self._mix(self.surface[SURFACE_FIELDS[name][0]], members, SURFACE_FIELDS[name][0])
                source._check_value(name, low)
                # Fixed bridge endpoints must exist even below the diagnostic
                # anchor, where the upper endpoint has interpolation weight0.
                high = native(name, join)
                fraction = max(0.0, (height - anchor) / (heights[join] - anchor))
                result[name] = low * (1 - fraction) + high * fraction
                if offset and height <= anchor:
                    quality.add(f"{offset}m_analysis_held_below_anchor")
                if name in ("eastward_wind_m_s", "northward_wind_m_s"):
                    quality.add("native_wind_level1_not_used")
            else:
                vertical = _bracket(heights[join:], height, "HEIGHT_OUT_OF_RANGE")
                result[name] = sum(weight * native(name, join + k) for k, weight in vertical)
            source._check_value(name, result[name])
        return result, quality, bridge_height

    def sample(self, time_utc, latitude_deg, longitude_deg, altitude_m, fields=None):
        requested = FIELD_NAMES if fields is None else fields
        if (not isinstance(requested, (list, tuple)) or not requested
                or any(not isinstance(name, str) for name in requested)
                or len(set(requested)) != len(requested)):
            raise WeatherError("INVALID_REQUIRED_FIELDS", "nonempty distinct field names required")
        absent = set(requested) - self.source.fields.keys()
        if absent:
            raise WeatherError("MISSING_CAPABILITY", ",".join(sorted(absent)))
        support = self.source._support(time_utc, latitude_deg, longitude_deg)
        height = to_h(altitude_m)
        ground = self.source._ground(support)
        if height < ground - 1e-7:
            raise WeatherError("BELOW_MODEL_SURFACE", "query below interpolated terrain")
        height = max(height, ground)
        groups = {}
        for t, j, i, weight in support:
            groups.setdefault(t, []).append((t, j, i, weight))
        values = {name: 0.0 for name in requested}
        quality = {POLICY, "spherical_geopotential_height_approximation", "height_linear_pressure",
                   "model_orography_not_fine_dem", "fixed_native_join_levels"}
        max_bridge = 0.0
        for members in groups.values():
            temporal_weight = sum(member[3] for member in members)
            horizontal = tuple((t, j, i, weight / temporal_weight) for t, j, i, weight in members)
            result, flags, bridge = self._column(horizontal, height, requested)
            for name in requested:
                values[name] += temporal_weight * result[name]
            quality.update(flags)
            max_bridge = max(max_bridge, bridge)
        for name, value in values.items():
            self.source._check_value(name, value)
        return {**values, "ground_altitude_m": to_z(ground), "quality": sorted(quality),
                "surface_bridge_height_m": max_bridge, "terrain_stencil_clamp_depth_m": 0.0}
