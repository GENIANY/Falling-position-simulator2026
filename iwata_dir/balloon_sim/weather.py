"""Compatibility entry for existing weather/1 APIs and fixture tooling.

Definitions now live under environment. The old path remains active for current
callers; evaluate retirement only during an explicit API migration. Private
aliases are retained for existing regression/fixture tools, not promoted to APIs.
"""
from .environment.fields import (WeatherError, geometric_to_geopotential,
    geopotential_to_geometric, SCHEMA, RADIUS_M, FIELD_NAMES,
    _number, _utc, _bracket, _axis, _array, _required_object)
from .environment.bundle import WeatherField
from .environment.storage import load_weather, read_json as _read_json, write_bundle as _write_bundle
from .environment.gfs_contract import LEVELS_HPA, LEADS, FILTER_URL, UPPER_KEYS
from .environment.gfs import acquire_gfs, replay_gfs, decode_gfs, _request, _url, _download

__all__ = ["WeatherError", "WeatherField", "load_weather", "acquire_gfs", "replay_gfs",
           "decode_gfs", "geometric_to_geopotential", "geopotential_to_geometric"]
