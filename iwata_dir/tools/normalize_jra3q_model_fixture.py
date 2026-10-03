#!/usr/bin/env python3
"""Offline JRA-3Q model-level candidate, introduced in 0.18.0 (S20).

load_fixture(root) verifies the saved ASCII/DAS bundle and normalizes the fixed
2024-01-01 00/06 UTC, 100-level, 2x2 NCAR Gaussian subset. ModelLevelEnvironment
provides selected-field queries at explicit geopotential height (gpm), with
column-wise pressure and strict support. No network, new dependencies, geometric
height conversion, surface gap filling, or flight/accuracy acceptance.

Example: e = load_fixture(Path.cwd()); e.sample(time_utc=datetime(2024,1,1,3,
tzinfo=timezone.utc), latitude_degrees=34.8, longitude_degrees=137.0,
geopotential_height_gpm=30000, required_fields=("eastward_wind_m_s",))

Standard-library only. Reuses numerical validation helpers from the unchanged
GFS candidate; does not expand that candidate's four-field API. Retain the raw
fixture and counterexamples; reconsider this loader at general-adapter adoption.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys

if __package__:
    from .normalize_gfs_fixture import (EnvironmentQueryError, bracket,
        finite_number, immutable_array, utc_time, write_evidence)
else:
    # Also supports direct CLI execution and importlib loading used by tests.
    import importlib.util
    _spec = importlib.util.spec_from_file_location("_jra_gfs_helpers", Path(__file__).with_name("normalize_gfs_fixture.py"))
    _helpers = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_helpers)
    EnvironmentQueryError = _helpers.EnvironmentQueryError
    bracket, finite_number = _helpers.bracket, _helpers.finite_number
    immutable_array, utc_time = _helpers.immutable_array, _helpers.utc_time
    write_evidence = _helpers.write_evidence

SCHEMA = "balloon.environment.jra3q_model_fixture/1"
PINNED_SOURCE_BUNDLE_SHA256 = "81bf2a10759d8f92a9576f3285bc810bedbe30a6f3675df78416f3ccf8295811"
FIELD_UNITS = {"pressure_pa": "Pa", "temperature_k": "K",
    "eastward_wind_m_s": "m s-1", "northward_wind_m_s": "m s-1",
    "specific_humidity_kg_kg": "kg kg-1"}
DEFAULT_FIELDS = tuple(FIELD_UNITS)[:4]
G0 = 9.80665
NATIVE_STEP = timedelta(hours=6)


def _require(condition, detail):
    if not condition:
        raise ValueError(detail)


def full_pressure_pa(half_pressure_pa):
    """JMA Simmons-Burridge full pressure, surface-upward, top = half/2.

    Interior exp((L log L-U log U)/(L-U)-1) is evaluated with log1p to avoid
    subtracting nearly equal logarithmic products. Not ERA arithmetic averaging
    or NCAR's fitted full-level linear coefficients. Inputs/outputs are Pa.
    """
    half = tuple(finite_number(p, "half pressure") for p in half_pressure_pa)
    _require(len(half) >= 2 and half[-1] == 0 and half[-2] > 0
             and all(a > b for a, b in zip(half, half[1:])),
             "half pressure must strictly decrease from surface to zero top")
    result = []
    for lower, upper in zip(half[:-2], half[1:-1]):
        ratio = (lower-upper)/upper
        p = lower * math.exp(math.log1p(ratio)/ratio-1)
        _require(math.isfinite(p) and upper < p < lower, "full pressure unsupported")
        result.append(p)
    result.append(half[-2]/2)
    _require(result[-1] > 0, "top pressure underflow")
    return tuple(result)


class ModelLevelEnvironment:
    """Finite JRA-like columns, [time, level surface-upward, lat, lon].

    Constructor validates arrays/six-hour UTC schedule. Missing values remain
    None; only requested fields are required by sample. Coordinate/ground support
    is always required. A complete column height axis is needed to avoid silently
    skipping an unknown layer. Input arrays and returned metadata are detached.
    """
    def __init__(self, *, times_utc, expected_times_utc, latitude_degrees,
                 longitude_degrees, model_levels, geopotential_height_gpm,
                 pressure_pa, fields, surface_pressure_pa,
                 surface_geopotential_height_gpm, provenance):
        self.times = tuple(utc_time(t) for t in times_utc)
        expected = tuple(utc_time(t) for t in expected_times_utc)
        _require(bool(expected) and all(b-a == NATIVE_STEP for a,b in zip(expected, expected[1:])),
                 "EXPECTED_TIME_GAP: expected JRA schedule must be contiguous six-hour UTC")
        _require(all(t.hour % 6 == 0 and t.minute == t.second == t.microsecond == 0 for t in expected),
                 "expected JRA times must be 00/06/12/18 UTC")
        _require(self.times == expected, "EXPECTED_TIME_MISMATCH: missing, extra, or reordered valid time")
        self.latitudes = tuple(finite_number(v, "latitude") for v in latitude_degrees)
        self.longitudes = tuple(finite_number(v, "longitude") for v in longitude_degrees)
        self.levels = tuple(model_levels)
        _require(bool(self.levels) and all(type(k) is int for k in self.levels)
                 and self.levels == tuple(range(1, len(self.levels)+1)), "model levels must be contiguous 1..N")
        for name, axis in (("latitude",self.latitudes),("longitude",self.longitudes)):
            _require(bool(axis) and all(b>a for a,b in zip(axis,axis[1:])), name+" must ascend")
        _require(-90 <= self.latitudes[0] <= self.latitudes[-1] <= 90
                 and -180 <= self.longitudes[0] <= self.longitudes[-1] <= 360
                 and self.longitudes[-1]-self.longitudes[0] < 360, "unsupported coordinates; no wrap")
        shape = (len(self.times),len(self.levels),len(self.latitudes),len(self.longitudes))
        self.heights = immutable_array(geopotential_height_gpm,shape,"geopotential height")
        self.pressures = immutable_array(pressure_pa,shape,"full pressure")
        _require(set(fields).issubset(FIELD_UNITS.keys()-{"pressure_pa"}), "unknown model field")
        self.fields = {name:immutable_array(data,shape,name) for name,data in fields.items()}
        self.fields["pressure_pa"] = self.pressures
        ground_shape = (shape[0],shape[2],shape[3])
        self.surface_pressure = immutable_array(surface_pressure_pa,ground_shape,"surface pressure")
        self.surface_height = immutable_array(surface_geopotential_height_gpm,ground_shape,"surface height")
        self.provenance = deepcopy(provenance)
        for t in range(shape[0]):
            for j in range(shape[2]):
                for i in range(shape[3]):
                    sp = self.surface_pressure[t][j][i]
                    _require(sp is None or sp > 0,"nonpositive surface pressure")
                    for data,ascending in ((self.heights,True),(self.pressures,False)):
                        known = [data[t][k][j][i] for k in range(shape[1]) if data[t][k][j][i] is not None]
                        _require(all(b>a if ascending else b<a for a,b in zip(known,known[1:])),"nonmonotonic height/pressure")
                    for k in range(shape[1]):
                        p = self.pressures[t][k][j][i]
                        _require(p is None or p > 0,"nonpositive full pressure")
                        for name,data in self.fields.items():
                            v = data[t][k][j][i]
                            if name == "temperature_k":
                                _require(v is None or v > 0,"nonpositive temperature")
                            if name == "specific_humidity_kg_kg":
                                _require(v is None or 0 <= v < 1,"q must be kg/kg in [0,1)")

    @property
    def capabilities(self):
        """Declared variables/semantics, not a successful query or accuracy claim."""
        return {"fields":{name:FIELD_UNITS[name] for name in self.fields},
                "height_kind":"geopotential_height", "height_unit":"gpm",
                "time_kind":"analysis_valid_utc",
                "temporal_support":[t.isoformat() for t in self.times]}

    def sample(self, *, time_utc, latitude_degrees, longitude_degrees,
               geopotential_height_gpm, required_fields=DEFAULT_FIELDS):
        """Column-height first, then lat/lon/UTC; all positive weights required.

        No q -> dry substitution, missing-level bridge, surface extension, or
        weight renormalization. Return requested fields and exact support indices.
        """
        time = utc_time(time_utc)
        if (not isinstance(required_fields,(list,tuple)) or not required_fields
                or any(not isinstance(n,str) for n in required_fields)
                or len(set(required_fields)) != len(required_fields)):
            raise EnvironmentQueryError("INVALID_REQUIRED_FIELDS","nonempty distinct field names required")
        absent = set(required_fields)-self.fields.keys()
        if absent:
            raise EnvironmentQueryError("MISSING_CAPABILITY",",".join(sorted(absent)))
        try:
            lat = finite_number(latitude_degrees,"latitude")
            lon = finite_number(longitude_degrees,"longitude")
            height = finite_number(geopotential_height_gpm,"geopotential height")
        except ValueError as exc:
            raise EnvironmentQueryError("INVALID_QUERY",str(exc)) from exc
        supports = (bracket(self.times,time,"TIME_OUT_OF_RANGE"),
                    bracket(self.latitudes,lat,"LATITUDE_OUT_OF_RANGE"),
                    bracket(self.longitudes,lon,"LONGITUDE_OUT_OF_RANGE"))
        values = {name:0.0 for name in required_fields}
        cells = []
        for t,wt in supports[0]:
            for j,wy in supports[1]:
                for i,wx in supports[2]:
                    sp,ground = self.surface_pressure[t][j][i],self.surface_height[t][j][i]
                    if sp is None or ground is None:
                        raise EnvironmentQueryError("MISSING_SURFACE_SUPPORT",f"column [{t},{j},{i}]")
                    if height < ground:
                        raise EnvironmentQueryError("BELOW_MODEL_SURFACE",f"column [{t},{j},{i}]")
                    h = tuple(plane[j][i] for plane in self.heights[t])
                    if any(v is None for v in h):
                        raise EnvironmentQueryError("MISSING_HEIGHT_SUPPORT",f"column [{t},{j},{i}]")
                    for k,wz in bracket(h,height,"HEIGHT_OUT_OF_RANGE"):
                        p = self.pressures[t][k][j][i]
                        if p is None:
                            raise EnvironmentQueryError("MISSING_DATA","full pressure coordinate missing")
                        if p > sp or h[k] < ground:
                            raise EnvironmentQueryError("BELOW_MODEL_SURFACE",f"cell [{t},{k},{j},{i}]")
                        weight = wt*wy*wx*wz
                        if not math.isfinite(weight) or weight <= 0:
                            raise EnvironmentQueryError("NUMERIC_UNSUPPORTED","combined weight not representable")
                        for name in required_fields:
                            v = self.fields[name][t][k][j][i]
                            if v is None:
                                raise EnvironmentQueryError("MISSING_DATA",f"{name} at [{t},{k},{j},{i}]")
                            values[name] += weight*v
                        cells.append({"index_t_level_lat_lon":[t,k,j,i],"model_level":self.levels[k],"weight":weight})
        if (not all(math.isfinite(v) for v in values.values())
                or any(values.get(n,1) <= 0 for n in ("pressure_pa","temperature_k"))):
            raise EnvironmentQueryError("NUMERIC_UNSUPPORTED","result not finite/positive")
        return {"status":"ok", "height_kind":"geopotential_height",
                "query":{"time_utc":time.isoformat(),"latitude_degrees":lat,"longitude_degrees":lon,
                         "geopotential_height_gpm":height}, "values":values,
                "units":{n:FIELD_UNITS[n] for n in required_fields}, "quality_flags":[],
                "support_cells":cells, "fixture_id":self.provenance.get("fixture_id"),
                "source_bundle_sha256":self.provenance.get("source_bundle_sha256")}

    def to_dict(self):
        """Diagnostic normalized snapshot, not a general input interchange format."""
        return {"schema":SCHEMA,"introduced_in":"0.18.0","capabilities":self.capabilities,
                "axes":{"time_utc":[t.isoformat() for t in self.times],"model_level":self.levels,
                        "latitude_degrees":self.latitudes,"longitude_degrees":self.longitudes},
                "axis_order":["time_utc","model_level","latitude_degrees","longitude_degrees"],
                "geopotential_height_gpm":self.heights,"fields":deepcopy(self.fields),
                "surface_pressure_pa":self.surface_pressure,"surface_geopotential_height_gpm":self.surface_height,
                "provenance":deepcopy(self.provenance),
                "interpolation":"linear in each column gpm, then lat/lon/UTC; pressure also linear",
                "not_accepted":["surface gap closure","geometric/DEM height","general acquisition adapter",
                                "whole-flight support","scientific model accuracy"]}


def _attributes(text, name):
    match = re.search(r"\n    "+re.escape(name)+r" \{(.*?)\n    \}",text,re.S)
    _require(match is not None,"missing DAS variable "+name)
    result = dict(re.findall(r'String (\w+) "([^"]*)";',match[1]))
    result.update(re.findall(r"(?:Float32|Float64|Int32|UInt32) (\w+) ([^;]+);",match[1]))
    return result


def _parse_grid(text, das):
    """Read the pinned DAP2 ASCII Grid form; unsupported layouts fail closed."""
    m = re.search(r"Float32 ([^\[]+)((?:\[\w+ = \d+\])+);",text)
    _require(m is not None,"expected one Float32 grid")
    variable = m[1]
    dims = re.findall(r"\[(\w+) = (\d+)\]",m[2])
    shape = tuple(int(size) for _,size in dims)
    parts = text.split("---------------------------------------------\n")
    _require(len(parts)==2,"invalid ASCII body separator")
    body = parts[1]
    axes = {}
    for name,size in dims:
        match = re.search(r"^"+re.escape(variable+"."+name)+r"\["+size+r"\]\n([^\n]+)",body,re.M)
        _require(match is not None,"missing grid map "+name)
        axes[name] = [finite_number(float(v),name) for v in match[1].split(",")]
        _require(len(axes[name])==int(size),"axis length mismatch")
    attrs = _attributes(das,variable)
    fill = float(attrs["_FillValue"])
    values = {}
    for indices,numbers in re.findall(r"^((?:\[\d+\])+), ([^\n]+)",body,re.M):
        ix = tuple(map(int,re.findall(r"\d+",indices)))
        row = [float(v) for v in numbers.split(",")]
        _require(len(ix)==len(shape)-1 and len(row)==shape[-1],"row shape mismatch")
        for i,v in enumerate(row):
            key = ix+(i,)
            _require(all(0 <= k < n for k,n in zip(key,shape)) and key not in values,"duplicate/out-of-range index")
            values[key] = v if math.isfinite(v) and v != fill else None
    _require(len(values)==math.prod(shape),"missing rows")
    ta = _attributes(das,"time")
    _require(ta["units"]=="hours since 1900-01-01 00:00:00" and ta["calendar"]=="gregorian","unsupported time convention")
    return {"variable":variable,"dimensions":[n for n,_ in dims],"shape":shape,"axes":axes,
            "attributes":attrs,"time_utc":[datetime(1900,1,1,tzinfo=timezone.utc)+timedelta(hours=v) for v in axes["time"]],"values":values}


def load_fixture(root: Path) -> ModelLevelEnvironment:
    """Verify fixed source bytes/metadata then decode; never fetch missing inputs."""
    path = root/"references/jra3q_model_fixture/source_bundle.json"
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    _require(digest==PINNED_SOURCE_BUNDLE_SHA256,"source bundle SHA256 mismatch")
    bundle = json.loads(raw)
    _require(bundle["schema"]=="balloon.jra3q.saved_ascii_fixture/1","unsupported source schema")
    source = bundle["sources"]
    ids = {"jra-axes"}|{f"jra-{k}-{s}" for k in ("t","h","u","v","q","sp","gp") for s in ("cell","das")}
    _require(set(source)==ids,"source response set mismatch")
    for ident,item in source.items():
        body,receipt = item["body_utf8"].encode("utf-8"),item["response"]
        _require(receipt["status"]==200 and receipt["transport_complete"],"incomplete response "+ident)
        _require(len(body)==receipt["body_bytes"] and hashlib.sha256(body).hexdigest()==receipt["body_sha256"],"raw body mismatch "+ident)
        _require(item["request"]["url"]==receipt["url"],"request/response URL mismatch")
    parsed = {k:_parse_grid(source[f"jra-{k}-cell"]["body_utf8"],source[f"jra-{k}-das"]["body_utf8"])
              for k in ("t","h","u","v","q","sp","gp")}
    ref = parsed["t"]
    _require(ref["shape"]==(2,100,2,2) and ref["dimensions"]==["time","hybrid_level","lat","lon"],"wrong fixed model shape")
    expected = [datetime.fromisoformat(t) for t in bundle["expected_time_utc"]]
    _require(ref["time_utc"]==expected,"expected valid time missing")
    units = {"t":"K","h":"gpm","u":"m s-1","v":"m s-1","q":"kg kg-1","sp":"Pa","gp":"m2 s-2"}
    variables = {"t":"tmp-hyb-an-gauss","h":"hgt-hyb-an-gauss","u":"ugrd-hyb-an-gauss","v":"vgrd-hyb-an-gauss",
                 "q":"spfh-hyb-an-gauss","sp":"pres-sfc-an-gauss","gp":"gp-sfc-cn-gauss"}
    for name,field in parsed.items():
        _require(field["variable"]==variables[name] and field["attributes"]["units"]==units[name],"source variable/unit mismatch "+name)
        _require(field["attributes"]["data_type"]==("constant" if name=="gp" else "analysis"),"wrong temporal meaning")
        _require(field["attributes"]["time_step"]==("none" if name=="gp" else "6-hour"),"wrong native interval")
        _require(all(field["axes"][n]==ref["axes"][n] for n in ("lat","lon")),"horizontal axis mismatch")
        if name in ("t","h","u","v","q"):
            _require(field["axes"]==ref["axes"],"upper field axis mismatch")
        else:
            _require(field["shape"]==((1,2,2) if name=="gp" else (2,2,2)),"surface shape mismatch")
            _require(field["dimensions"]==["time","lat","lon"],"surface dimensions mismatch")
            _require(field["time_utc"]==([datetime(1947,9,1,tzinfo=timezone.utc)] if name=="gp" else expected),"surface/invariant time mismatch")
        _require(all(v is not None for v in field["values"].values()),"fixed observed field has missing values")
    _require(sum(len(f["values"]) for f in parsed.values())==4012,"fixed value count mismatch")
    coeftext = source["jra-axes"]["body_utf8"].split("---------------------------------------------\n")[1]
    coeffs = {}
    for name,count,values in re.findall(r"(?m)^([\w_]+)\[(\d+)\]\n([^\n]+)",coeftext):
        coeffs[name] = [finite_number(float(v),name) for v in values.split(",")]
        _require(len(coeffs[name])==int(count),"coefficient count mismatch")
    a,b = coeffs["a_hybrid_half_level"],coeffs["b_hybrid_half_level"]
    _require(len(a)==len(b)==101 and coeffs["hybrid_level"]==ref["axes"]["hybrid_level"],"hybrid coefficients mismatch")
    for name,unit in (("a_hybrid_half_level","Pa"),("b_hybrid_half_level","1")):
        meta = _attributes(source["jra-t-das"]["body_utf8"],name)
        _require(meta["units"]==unit and meta["vertical_orientation"]=="from surface upward","half coefficient meaning mismatch")
    lat_order = sorted(range(2),key=lambda j:ref["axes"]["lat"][j])
    lon_order = sorted(range(2),key=lambda i:ref["axes"]["lon"][i])
    def upper(name):
        return [[[[parsed[name]["values"][t,k,j,i] for i in lon_order] for j in lat_order] for k in range(100)] for t in range(2)]
    surface = [[[parsed["sp"]["values"][t,j,i] for i in lon_order] for j in lat_order] for t in range(2)]
    ground = [[[parsed["gp"]["values"][0,j,i]/G0 for i in lon_order] for j in lat_order] for _ in range(2)]
    columns = [[[full_pressure_pa([aa+bb*surface[t][j][i] for aa,bb in zip(a,b)]) for i in range(2)] for j in range(2)] for t in range(2)]
    pressure = [[[[columns[t][j][i][k] for i in range(2)] for j in range(2)] for k in range(100)] for t in range(2)]
    environment = ModelLevelEnvironment(times_utc=expected,expected_times_utc=expected,
        latitude_degrees=[ref["axes"]["lat"][j] for j in lat_order],longitude_degrees=[ref["axes"]["lon"][i] for i in lon_order],
        model_levels=list(range(1,101)),geopotential_height_gpm=upper("h"),pressure_pa=pressure,
        fields={target:upper(name) for name,target in (("t","temperature_k"),("u","eastward_wind_m_s"),("v","northward_wind_m_s"),("q","specific_humidity_kg_kg"))},
        surface_pressure_pa=surface,surface_geopotential_height_gpm=ground,
        provenance={"fixture_id":bundle["fixture_id"],"source_bundle_sha256":digest,
            "provider":bundle["provider"],"license_note":bundle["license_note"],"source_urls":bundle["source_urls"],
            "raw_receipts":{name:item["response"] for name,item in source.items()},
            "source_grid":"NCAR regular Gaussian 960x480 interpolated from JMA reduced N240; preserved DAS in bundle",
            "source_latitude_order":ref["axes"]["lat"],"source_longitude_order":ref["axes"]["lon"],
            "invariant_time_utc":parsed["gp"]["time_utc"][0].isoformat(),"gravity_m_s2":G0,
            "half_coefficients_pa":a,"half_coefficients_dimensionless":b,"pressure_method":bundle["pressure_method"]})
    _require(hashlib.sha256(path.read_bytes()).hexdigest()==digest,"source bundle changed during load")
    return environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir",type=Path,required=True)
    args = parser.parse_args()
    try:
        environment = load_fixture(args.root.resolve())
        write_evidence(environment,args.output_dir,args.root)
        print("PASS: fixed JRA model-level fixture normalized offline; ground gap remains unsupported.")
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}",file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
