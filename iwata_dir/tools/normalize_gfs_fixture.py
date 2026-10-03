#!/usr/bin/env python3
"""Offline P1 environment candidate, introduced in 0.14.0 (S14-3).

Fixed GFS fixture -> SI pressure/temperature/wind, UTC and explicit geopotential
height -> bounded, conservative interpolation. See docs/ENVIRONMENT_CONTRACT.md.
Core queries use the standard library; fixture decoding reuses the inspector and
requires the existing ecCodes/NumPy installation. No download or model/landing
calculation. Retain until the general adapter and height contract are accepted.
"""
from __future__ import annotations

import argparse
from bisect import bisect_left
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import math
from pathlib import Path
import platform
import sys

SCHEMA = "balloon.environment.fixture/1"
FIELD_UNITS = {"geopotential_height_gpm": "gpm", "temperature_k": "K",
               "eastward_wind_m_s": "m s-1", "northward_wind_m_s": "m s-1"}
SOURCE_NAMES = {"gh": "geopotential_height_gpm", "t": "temperature_k",
                "u": "eastward_wind_m_s", "v": "northward_wind_m_s"}


class EnvironmentQueryError(ValueError):
    """A rejected query with a stable machine-readable reason code."""
    def __init__(self, code: str, detail: str):
        self.code = code
        super().__init__(f"{code}: {detail}")


def utc_time(value: datetime) -> datetime:
    """Require an explicit zero UTC offset; never interpret local/naive time."""
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise EnvironmentQueryError("NON_UTC_TIME", "an aware UTC datetime is required")
    return value.astimezone(timezone.utc)


def finite_number(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds finite float range") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def bracket(axis, value, code: str):
    """Return positive-weight support only; exact endpoints need one node."""
    if value < axis[0] or value > axis[-1]:
        raise EnvironmentQueryError(code, f"{value!s} outside [{axis[0]!s}, {axis[-1]!s}]")
    right = bisect_left(axis, value)
    if right < len(axis) and value == axis[right]:
        return ((right, 1.0),)
    left = right - 1
    span = axis[right] - axis[left]
    if isinstance(span, (int, float)) and not math.isfinite(span):
        raise EnvironmentQueryError("NUMERIC_UNSUPPORTED", "support coordinate span exceeds finite float range")
    weight = (value - axis[left]) / span
    if not math.isfinite(weight) or not 0.0 < weight < 1.0:
        raise EnvironmentQueryError("NUMERIC_UNSUPPORTED", "interior support weight is not representable")
    return ((left, 1.0 - weight), (right, weight))


def immutable_array(value, shape, name):
    """Validate dimensions and encode nonfinite/missing input as explicit None."""
    if not shape:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name}: numeric values or None required")
        try:
            number = float(value)
        except OverflowError as exc:
            raise ValueError(f"{name}: value exceeds finite float range") from exc
        return number if math.isfinite(number) else None
    if not isinstance(value, (list, tuple)) or len(value) != shape[0]:
        raise ValueError(f"{name}: expected shape {shape}")
    return tuple(immutable_array(child, shape[1:], name) for child in value)


class Environment:
    """Validated finite-grid candidate; queries explicitly use geopotential gpm.

    Fields have axes [UTC time, descending pressure level, latitude, longitude].
    Surface pressure has [UTC time, latitude, longitude]. Values are immutable.
    This constructor also accepts synthetic inputs without GRIB dependencies.
    """
    def __init__(self, *, times_utc, latitude_degrees, longitude_degrees,
                 pressure_pa, fields, surface_pressure_pa, provenance,
                 surface_fields=None):
        self.times = tuple(utc_time(t) for t in times_utc)
        self.latitudes = tuple(finite_number(v, "latitude") for v in latitude_degrees)
        self.longitudes = tuple(finite_number(v, "longitude") for v in longitude_degrees)
        self.pressures = tuple(finite_number(v, "pressure") for v in pressure_pa)
        for name, axis in (("time", self.times), ("latitude", self.latitudes),
                           ("longitude", self.longitudes)):
            if not axis or any(b <= a for a, b in zip(axis, axis[1:])):
                raise ValueError(f"{name} axis must be nonempty, distinct and ascending")
        if (self.latitudes[0] < -90 or self.latitudes[-1] > 90
                or self.longitudes[0] < -180 or self.longitudes[-1] > 360
                or self.longitudes[-1] - self.longitudes[0] >= 360):
            raise ValueError("unsupported latitude/longitude range; no periodic seam handling")
        if not self.pressures or self.pressures[-1] <= 0 or any(
                b >= a for a, b in zip(self.pressures, self.pressures[1:])):
            raise ValueError("pressure levels must be positive, distinct and descending")
        if set(fields) != set(FIELD_UNITS):
            raise ValueError("exactly the four explicitly named environment fields are required")
        nt, nz, ny, nx = map(len, (self.times, self.pressures, self.latitudes, self.longitudes))
        self.fields = {name: immutable_array(value, (nt, nz, ny, nx), name)
                       for name, value in fields.items()}
        self.surface_pressure = immutable_array(surface_pressure_pa, (nt, ny, nx), "surface pressure")
        self.provenance = deepcopy(provenance)
        self.surface_fields = deepcopy(surface_fields or {})
        self.quality = []
        for t in range(nt):
            time_quality = []
            for k, pressure in enumerate(self.pressures):
                plane = []
                for j in range(ny):
                    row = []
                    for i in range(nx):
                        flags = []
                        sp = self.surface_pressure[t][j][i]
                        if sp is None:
                            flags.append("surface_pressure_missing")
                        elif sp <= 0:
                            raise ValueError("nonpositive surface pressure")
                        elif pressure > sp:
                            flags.append("below_ground")
                        if any(v[t][k][j][i] is None for v in self.fields.values()):
                            flags.append("missing_data")
                        temp = self.fields["temperature_k"][t][k][j][i]
                        if temp is not None and temp <= 0:
                            raise ValueError("nonpositive absolute temperature")
                        row.append(tuple(flags))
                    plane.append(tuple(row))
                time_quality.append(tuple(plane))
            self.quality.append(tuple(time_quality))
            for j in range(ny):
                for i in range(nx):
                    heights = [self.fields["geopotential_height_gpm"][t][k][j][i] for k in range(nz)]
                    known = [h for h in heights if h is not None]
                    if any(b <= a for a, b in zip(known, known[1:])):
                        raise ValueError("geopotential height must increase as pressure decreases")
        self.quality = tuple(self.quality)

    def sample(self, *, time_utc, latitude_degrees, longitude_degrees,
               geopotential_height_gpm):
        """Interpolate in each column's gpm, then latitude/longitude/UTC time.

        Every positive-weight source cell must be usable. No fallback, gap
        bridging, weight renormalization, longitude wrapping or extrapolation.
        """
        time = utc_time(time_utc)
        try:
            lat = finite_number(latitude_degrees, "latitude")
            lon = finite_number(longitude_degrees, "longitude")
            height = finite_number(geopotential_height_gpm, "geopotential height")
        except ValueError as exc:
            raise EnvironmentQueryError("INVALID_QUERY", str(exc)) from exc
        support = (bracket(self.times, time, "TIME_OUT_OF_RANGE"),
                   bracket(self.latitudes, lat, "LATITUDE_OUT_OF_RANGE"),
                   bracket(self.longitudes, lon, "LONGITUDE_OUT_OF_RANGE"))
        values = {name: 0.0 for name in FIELD_UNITS}
        values["pressure_pa"] = 0.0
        cells = []
        for t, wt in support[0]:
            for j, wy in support[1]:
                for i, wx in support[2]:
                    heights = tuple(plane[j][i] for plane in self.fields["geopotential_height_gpm"][t])
                    if any(h is None for h in heights):
                        raise EnvironmentQueryError("MISSING_HEIGHT_SUPPORT", f"column [{t},{j},{i}]")
                    for k, wz in bracket(heights, height, "HEIGHT_OUT_OF_RANGE"):
                        flags = self.quality[t][k][j][i]
                        if flags:
                            code = "BELOW_GROUND" if "below_ground" in flags else "MISSING_DATA"
                            raise EnvironmentQueryError(code, f"cell [{t},{k},{j},{i}]: {','.join(flags)}")
                        weight = wt * wy * wx * wz
                        if not math.isfinite(weight) or weight <= 0:
                            raise EnvironmentQueryError("NUMERIC_UNSUPPORTED", "combined support weight is not representable")
                        for name, field in self.fields.items():
                            values[name] += weight * field[t][k][j][i]
                        values["pressure_pa"] += weight * self.pressures[k]
                        cells.append({"index_t_level_lat_lon": [t, k, j, i], "weight": weight})
        if (not all(math.isfinite(value) for value in values.values())
                or values["pressure_pa"] <= 0 or values["temperature_k"] <= 0):
            raise EnvironmentQueryError("NUMERIC_UNSUPPORTED", "interpolated result is not finite or positive where required")
        return {"status": "ok", "height_kind": "geopotential_height",
                "query": {"time_utc": time.isoformat(), "latitude_degrees": lat,
                          "longitude_degrees": lon, "geopotential_height_gpm": height},
                "units": {**FIELD_UNITS, "pressure_pa": "Pa"}, "values": values,
                "quality_flags": [], "support_cells": cells,
                "fixture_id": self.provenance.get("fixture_id"),
                "source_manifest_sha256": self.provenance.get("source_manifest_sha256")}

    def to_dict(self):
        """Return JSON-compatible normalized values, masks and full provenance."""
        return {"schema": SCHEMA, "introduced_in": "0.14.0",
                "height_kind": "geopotential_height", "units": {**FIELD_UNITS, "pressure_pa": "Pa"},
                "axes": {"time_utc": [t.isoformat() for t in self.times],
                         "pressure_pa": self.pressures, "latitude_degrees": self.latitudes,
                         "longitude_degrees": self.longitudes},
                "axis_order": ["time_utc", "pressure_pa", "latitude_degrees", "longitude_degrees"],
                "fields": deepcopy(self.fields), "surface_pressure_pa": self.surface_pressure,
                "quality_flags": self.quality, "surface_fields_unconverted": deepcopy(self.surface_fields),
                "provenance": deepcopy(self.provenance),
                "interpolation": "piecewise linear gpm in each column, then latitude/longitude/time; pressure also linear",
                "not_accepted": ["geometric height conversion", "near-surface gap filling", "landing or coastline",
                                 "full-flight trajectory", "forecast accuracy", "general GFS adapter"]}


def load_fixture(root: Path) -> Environment:
    """Verify immutable fixture with the existing inspector, then decode offline."""
    spec = importlib.util.spec_from_file_location("fixture_inspector", Path(__file__).with_name("inspect_gfs_fixture.py"))
    inspector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inspector)
    import eccodes
    import numpy as np
    manifest_path = root / "references/gfs_p1_fixture/manifest.json"
    manifest_hash = inspector.digest(manifest_path)
    manifest, expected = inspector.load_inputs(root)
    grid = manifest["grid"]
    levels = manifest["requested_pressure_levels_hpa"]
    fields = {name: [] for name in FIELD_UNITS}
    surface_pressure, times, inspections = [], [], []
    surface_fields = {f"{name}:{kind}:{level}": {"source_definition": deepcopy(expected[name, kind, level]), "values": []}
                      for name, kind, level in expected if kind != "isobaricInhPa"}
    for item in manifest["files"]:
        path = manifest_path.parent / item["file"]
        report, _ = inspector.inspect_file(path, item, manifest, expected, eccodes, np)
        inspections.append(report)
        decoded = {}
        with path.open("rb") as stream:
            while (handle := eccodes.codes_grib_new_from_file(stream)) is not None:
                try:
                    key = tuple(eccodes.codes_get(handle, k) for k in ("shortName", "typeOfLevel", "level"))
                    decoded[key] = eccodes.codes_get_values(handle).reshape(grid["nj"], grid["ni"]).tolist()
                finally:
                    eccodes.codes_release(handle)
        inspector.require(inspector.digest(path) == inspector.PINNED_SHA256[path.name], "fixture changed during normalization")
        for source, target in SOURCE_NAMES.items():
            fields[target].append([decoded[source, "isobaricInhPa", level] for level in levels])
        surface_pressure.append(decoded["sp", "surface", 0])
        for (name, kind, level), array in decoded.items():
            if kind != "isobaricInhPa":
                surface_fields[f"{name}:{kind}:{level}"]["values"].append(array)
        times.append(datetime.fromisoformat(manifest["run_utc"].replace("Z", "+00:00")) + timedelta(hours=item["forecast_hour"]))
    inspector.require(inspector.digest(manifest_path) == manifest_hash, "manifest changed during normalization")
    return Environment(times_utc=times,
                       latitude_degrees=np.linspace(grid["south"], grid["north"], grid["nj"]).tolist(),
                       longitude_degrees=np.linspace(grid["west"], grid["east"], grid["ni"]).tolist(),
                       pressure_pa=[level * 100 for level in levels], fields=fields,
                       surface_pressure_pa=surface_pressure, surface_fields=surface_fields,
                       provenance={"fixture_id": manifest["fixture_id"], "source_manifest": manifest,
                                   "source_manifest_sha256": manifest_hash, "inspection": inspections,
                                   "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                                               "eccodes_python": eccodes.__version__, "eccodes_native": eccodes.codes_get_api_version()}})


def write_evidence(environment: Environment, output: Path, input_root: Path):
    """Write only to a new external directory; never replace fixture or outputs."""
    output = output.resolve()
    roots = (input_root.resolve(), Path(__file__).resolve().parents[1])
    if any(output.is_relative_to(root) for root in roots):
        raise ValueError("output directory must be outside the input and tool repositories")
    if output.exists():
        raise FileExistsError(f"choose a new output directory: {output}")
    payload = json.dumps(environment.to_dict(), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    output.mkdir(parents=True, exist_ok=False)
    (output / "environment.json").write_text(payload, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        environment = load_fixture(args.root.resolve())
        write_evidence(environment, args.output_dir, args.root)
        print("PASS: fixed GFS normalized; UTC/Pa/K/m s-1/gpm, source metadata and below-ground masks retained.")
        print(f"Evidence: {args.output_dir.resolve() / 'environment.json'}")
        print("NOT ACCEPTED: geometric height, landing, whole-flight support or scientific accuracy.")
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
