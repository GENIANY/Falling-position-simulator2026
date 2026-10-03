"""Finite pressure-column reconstruction, horizontal/time interpolation and support.

Product delivery schedules are supplied at construction, never inferred here.
The current normalized pressure/surface schema is not a model-level adapter.
No I/O, acquisition, solver or result-format dependency is allowed in this layer.
"""
from bisect import bisect_left
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import math

SCHEMA = "balloon.weather/1"
RADIUS_M = 6371000.0
FIELD_NAMES = ("eastward_wind_m_s", "northward_wind_m_s", "pressure_pa",
               "temperature_k", "specific_humidity_kg_kg")
UPPER_FIELD_NAMES = ("geopotential_height_gpm", "temperature_k",
                     "eastward_wind_m_s", "northward_wind_m_s",
                     "specific_humidity_kg_kg")

class WeatherError(ValueError):
    """A stable rejection code plus human-readable detail."""
    def __init__(self, code, detail):
        self.code, self.detail = code, str(detail)
        super().__init__(f"{code}: {detail}")


def _required_object(value,required,name):
    if not isinstance(value,dict):
        raise WeatherError("INVALID_BUNDLE",f"{name} must be an object")
    missing=set(required)-set(value)
    if missing:
        raise WeatherError("INVALID_BUNDLE",f"{name} missing {sorted(missing)}")
    return value


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WeatherError("INVALID_NUMBER", name)
    try:
        result = float(value)
    except OverflowError as exc:
        raise WeatherError("INVALID_NUMBER", name) from exc
    if not math.isfinite(result):
        raise WeatherError("INVALID_NUMBER", name)
    return result


def _utc(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise WeatherError("INVALID_TIME", value) from exc
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise WeatherError("NON_UTC_TIME", "explicit UTC timestamp required")
    return value.astimezone(timezone.utc)


def geometric_to_geopotential(z):
    z = _number(z, "geometric altitude")
    if z <= -RADIUS_M:
        raise WeatherError("INVALID_HEIGHT", z)
    return RADIUS_M * z / (RADIUS_M + z)


def geopotential_to_geometric(h):
    h = _number(h, "geopotential altitude")
    if h >= RADIUS_M:
        raise WeatherError("INVALID_HEIGHT", h)
    return RADIUS_M * h / (RADIUS_M - h)


def _bracket(axis, value, code):
    if value < axis[0] or value > axis[-1]:
        raise WeatherError(code, f"{value} outside [{axis[0]}, {axis[-1]}]")
    i = bisect_left(axis, value)
    if i < len(axis) and axis[i] == value:
        return ((i, 1.0),)
    w = (value-axis[i-1])/(axis[i]-axis[i-1])
    return ((i-1, 1-w), (i, w))


def _axis(values, name, descending=False):
    if not isinstance(values, (list, tuple)) or not values:
        raise WeatherError("INVALID_AXIS", name)
    axis = tuple(_number(x, name) for x in values)
    if any((b >= a if descending else b <= a) for a,b in zip(axis,axis[1:])):
        raise WeatherError("INVALID_AXIS", name)
    return axis


def _array(value, shape, name):
    if not shape:
        return None if value is None else _number(value, name)
    if not isinstance(value, (list, tuple)) or len(value) != shape[0]:
        raise WeatherError("INVALID_SHAPE", f"{name}: {shape}")
    return tuple(_array(x, shape[1:], name) for x in value)


class PressureLevelField:
    """Immutable finite field: per-column vertical, then horizontal/time.

    Every positive source support is required. Underground pressure levels
    are excluded independently in each column. Surface anchors bridge to
    its first above-ground pressure level. A contributing terrain column
    higher than the query holds its surface values only for interpolation,
    with explicit clamp depth; queries below interpolated terrain reject.
    """
    def __init__(self, bundle, *, quality_flags=(), validate_times=None):
        if not isinstance(bundle, dict) or bundle.get("schema") != SCHEMA:
            raise WeatherError("INVALID_SCHEMA", SCHEMA)
        _required_object(bundle,("axes","fields","surface"),"bundle")
        self.metadata = deepcopy(_required_object(bundle.get("metadata",{}),(),"metadata"))
        axes = _required_object(bundle["axes"],("time_utc","latitude_deg","longitude_deg","pressure_pa"),"axes")
        if not isinstance(axes["time_utc"],(list,tuple)) or not axes["time_utc"]:
            raise WeatherError("INVALID_AXIS","time_utc must be a nonempty array")
        self.times = tuple(_utc(t) for t in axes["time_utc"])
        if not self.times or any(b <= a for a,b in zip(self.times,self.times[1:])):
            raise WeatherError("INVALID_AXIS", "time")
        self.latitudes = _axis(axes["latitude_deg"], "latitude")
        self.longitudes = _axis(axes["longitude_deg"], "longitude")
        self.pressures = _axis(axes["pressure_pa"], "pressure", True)
        if not (-90 <= self.latitudes[0] <= self.latitudes[-1] <= 90):
            raise WeatherError("INVALID_AXIS", "latitude range")
        if not (-180 <= self.longitudes[0] < 360 and self.longitudes[-1] <= 360
                and self.longitudes[-1]-self.longitudes[0] < 360):
            raise WeatherError("INVALID_AXIS", "longitude range/seam")
        if self.pressures[-1] <= 0:
            raise WeatherError("INVALID_AXIS", "nonpositive pressure")
        self.quality_flags = tuple(quality_flags)
        if validate_times is not None:
            validate_times(self.metadata, self.times)
        n, k, y, x = map(len, (self.times,self.pressures,self.latitudes,self.longitudes))
        _required_object(bundle["fields"],UPPER_FIELD_NAMES,"fields")
        self.fields = {name:_array(bundle["fields"][name], (n,k,y,x), name)
                       for name in UPPER_FIELD_NAMES}
        names = ("geopotential_height_gpm", "pressure_pa", "temperature_2m_k",
                 "specific_humidity_2m_kg_kg", "eastward_wind_10m_m_s", "northward_wind_10m_m_s")
        _required_object(bundle["surface"],names,"surface")
        self.surface = {name:_array(bundle["surface"][name], (n,y,x), name) for name in names}
        for t in range(n):
            for j in range(y):
                for i in range(x):
                    hs = [a[j][i] for a in self.fields["geopotential_height_gpm"][t]]
                    if any(v is None for v in hs) or any(b <= a for a,b in zip(hs,hs[1:])):
                        raise WeatherError("INVALID_HEIGHT_PROFILE", f"{t},{j},{i}")
                    for name in names:
                        if self.surface[name][t][j][i] is None:
                            raise WeatherError("MISSING_SURFACE", name)
                    if self.surface["pressure_pa"][t][j][i] <= 0:
                        raise WeatherError("INVALID_PRESSURE", "surface")
        self.metadata.setdefault("height_method", "H=R*z/(R+z), R=6371000 m; spherical geoid approximation")

    def _support(self, time_utc, latitude_deg, longitude_deg):
        t = _utc(time_utc)
        lat, lon = _number(latitude_deg,"latitude"), _number(longitude_deg,"longitude")
        # A single equivalent representation is accepted; no seam interpolation.
        if not -180 <= lon <= 360:
            raise WeatherError("LONGITUDE_OUT_OF_RANGE",lon)
        if not self.longitudes[0] <= lon <= self.longitudes[-1]:
            for equivalent in (lon+360,lon-360):
                if self.longitudes[0] <= equivalent <= self.longitudes[-1]:
                    lon=equivalent
                    break
        return tuple((it,iy,ix,wt*wy*wx)
                     for it,wt in _bracket(self.times,t,"TIME_OUT_OF_RANGE")
                     for iy,wy in _bracket(self.latitudes,lat,"LATITUDE_OUT_OF_RANGE")
                     for ix,wx in _bracket(self.longitudes,lon,"LONGITUDE_OUT_OF_RANGE"))

    @staticmethod
    def _mix(array, support):
        result = 0.0
        for t,j,i,w in support:
            value = array[t][j][i]
            if value is None:
                raise WeatherError("MISSING_DATA", f"positive support {t},{j},{i}")
            result += w*value
        return result

    def ground_altitude(self, time_utc, latitude_deg, longitude_deg):
        support = self._support(time_utc,latitude_deg,longitude_deg)
        return geopotential_to_geometric(self._mix(self.surface["geopotential_height_gpm"],support))

    def sample(self, time_utc, latitude_deg, longitude_deg, altitude_m, fields=None):
        if fields is not None and (not isinstance(fields,(list,tuple))
                                   or any(not isinstance(name,str) for name in fields)):
            raise WeatherError("UNKNOWN_FIELD","fields must be a list of unique field names")
        requested = tuple(FIELD_NAMES if fields is None else fields)
        if not requested or len(set(requested))!=len(requested) or set(requested)-set(FIELD_NAMES):
            raise WeatherError("UNKNOWN_FIELD", requested)
        support = self._support(time_utc,latitude_deg,longitude_deg)
        h = geometric_to_geopotential(altitude_m)
        ground = self._mix(self.surface["geopotential_height_gpm"],support)
        if h < ground-1e-7:
            raise WeatherError("BELOW_GROUND", f"{h} < {ground} gpm")
        h = max(h, ground)
        quality = ["spherical_geopotential_height_approximation", *self.quality_flags]
        result = {name:0.0 for name in requested}
        max_gap, max_clamp = 0.0, 0.0
        surface_name = {"pressure_pa":"pressure_pa", "temperature_k":"temperature_2m_k",
                        "specific_humidity_kg_kg":"specific_humidity_2m_kg_kg",
                        "eastward_wind_m_s":"eastward_wind_10m_m_s",
                        "northward_wind_m_s":"northward_wind_10m_m_s"}
        def flag(value):
            if value not in quality:
                quality.append(value)
        def checked(value,name):
            if value is None:
                raise WeatherError("MISSING_DATA",name)
            if (not math.isfinite(value) or (name in ("pressure_pa","temperature_k") and value<=0)
                    or (name=="specific_humidity_kg_kg" and not 0<=value<1)):
                raise WeatherError("INVALID_FIELD_VALUE",name)
            return value
        for t,j,i,weight in support:
            local_ground=self.surface["geopotential_height_gpm"][t][j][i]
            local_h=max(h,local_ground)
            if h < local_ground:
                # Finite surface-only extension for a contributing terrain stencil.
                # This is not an underground atmospheric sample or solver state.
                flag("terrain_stencil_surface_clamp")
                max_clamp=max(max_clamp,geopotential_to_geometric(local_ground)-geopotential_to_geometric(h))
            keep=[k for k,p in enumerate(self.pressures)
                  if p<=self.surface["pressure_pa"][t][j][i]
                  and self.fields["geopotential_height_gpm"][t][k][j][i]>local_ground+10]
            if not keep:
                raise WeatherError("NO_VERTICAL_SUPPORT", f"column {t},{j},{i}")
            heights=tuple(self.fields["geopotential_height_gpm"][t][k][j][i] for k in keep)
            max_gap=max(max_gap,geopotential_to_geometric(heights[0])-geopotential_to_geometric(local_ground))
            if local_h < heights[0]:
                flag("surface_layer_bridge")
            def upper(name,k):
                value=self.fields[name][t][k][j][i]
                if value is None:
                    raise WeatherError("MISSING_DATA",f"{name}[{t},{k},{j},{i}]")
                return checked(value,name)
            for name in requested:
                if local_h < heights[0]:
                    offset=0 if name=="pressure_pa" else (10 if "wind" in name else 2)
                    anchor_h=geometric_to_geopotential(geopotential_to_geometric(local_ground)+offset)
                    fraction=max(0.0,(local_h-anchor_h)/(heights[0]-anchor_h))
                    low=checked(self.surface[surface_name[name]][t][j][i],name)
                    high=self.pressures[keep[0]] if name=="pressure_pa" else upper(name,keep[0])
                    if name=="pressure_pa":
                        if low<=0:
                            raise WeatherError("INVALID_PRESSURE","surface")
                        value=math.exp((1-fraction)*math.log(low)+fraction*math.log(high))
                    else:
                        value=(1-fraction)*low+fraction*high
                        if local_h<=anchor_h:
                            flag("10m_wind_held_below_anchor" if "wind" in name else "2m_thermodynamics_held_below_anchor")
                else:
                    vertical=_bracket(heights,local_h,"HEIGHT_OUT_OF_RANGE")
                    if name=="pressure_pa":
                        value=math.exp(sum(w*math.log(self.pressures[keep[k]]) for k,w in vertical))
                    else:
                        value=sum(w*upper(name,keep[k]) for k,w in vertical)
                if (not math.isfinite(value) or (name in ("pressure_pa","temperature_k") and value<=0)
                        or (name=="specific_humidity_kg_kg" and not 0<=value<1)):
                    raise WeatherError("INVALID_FIELD_VALUE", name)
                result[name]+=weight*value
        result.update(ground_altitude_m=geopotential_to_geometric(ground), quality=quality,
                      surface_bridge_height_m=max_gap, terrain_stencil_clamp_depth_m=max_clamp)
        return result
