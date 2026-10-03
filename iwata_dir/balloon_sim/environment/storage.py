"""Strict JSON and deterministic saved weather bundles; never contact providers."""
import gzip
import io
import json
import math
from pathlib import Path
from .bundle import WeatherField
from .fields import WeatherError

def read_json(path):
    """Read plain/gzip UTF-8 JSON without ambiguous duplicate/nonfinite values."""
    path=Path(path)
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:
                raise WeatherError("INVALID_JSON",f"duplicate key: {key}")
            result[key]=value
        return result
    def nonfinite(value):
        raise WeatherError("INVALID_JSON",f"nonfinite number: {value}")
    def finite_float(value):
        result=float(value)
        if not math.isfinite(result):
            return nonfinite(value)
        return result
    opener=gzip.open if path.suffix==".gz" else open
    try:
        with opener(path,"rt",encoding="utf-8-sig") as stream:
            return json.load(stream,object_pairs_hook=unique,parse_constant=nonfinite,parse_float=finite_float)
    except (json.JSONDecodeError,UnicodeError) as exc:
        raise WeatherError("INVALID_JSON",str(exc)) from exc


def load_weather(bundle_path):
    """Load an offline normalized bundle; no network or GRIB dependency."""
    bundle = read_json(bundle_path)
    from .jra3q import (Jra3qModelField, SCHEMA as JRA_SCHEMA,
                       Jra3qSurfaceField, SURFACE_SCHEMA as JRA_SURFACE_SCHEMA)
    if isinstance(bundle, dict) and bundle.get("schema") == JRA_SURFACE_SCHEMA:
        return Jra3qSurfaceField(bundle)
    if isinstance(bundle, dict) and bundle.get("schema") == JRA_SCHEMA:
        return Jra3qModelField(bundle)
    return WeatherField(bundle)


def write_bundle(target, bundle):
    # Fixed gzip header makes replay bytes reproducible, not just the JSON values.
    with Path(target).open("xb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as compressed:
            with io.TextIOWrapper(compressed,encoding="utf-8",newline="\n") as stream:
                json.dump(bundle,stream,separators=(",",":"),allow_nan=False)
