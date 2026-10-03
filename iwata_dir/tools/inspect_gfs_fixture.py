#!/usr/bin/env python3
"""Inspect the fixed P1 GFS fixture offline; introduced in 0.13.0 (T-005).

Role: verify hashes, GRIB metadata and decoded values of three small input files.
Dependencies: the existing ecCodes Python/native library and NumPy; see BUILD.
This is an ingestion acceptance tool, not a weather adapter or trajectory model.
No download, dependency installation or input modification is performed.
Outputs require a directory outside the repository with no prior output files.
Lifecycle: retain through the T-005 normalization acceptance, then reassess its
role alongside the replacement ingestion tests (D-134 / CONTENT_MAP).
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys


PINNED_SHA256 = {
    "f000.grib2": "4baefb0af3ed2924e11c0610b26fdc5d6d2c21759dc7c63380818bb8c40e628c",
    "f001.grib2": "1f0a29b6855fcbad942a82440f6b8a3d8b1cde1b3db8c946172804212231332d",
    "f002.grib2": "547b2402efd47eb51c9ea03c516edd59696fbd1b20b687083da95395a43cb13e",
}
KEYS = (
    "shortName", "units", "typeOfLevel", "level", "discipline",
    "parameterCategory", "parameterNumber", "Ni", "Nj", "gridType",
    "dataDate", "dataTime", "step", "validityDate", "validityTime",
    "numberOfMissing", "numberOfPoints", "iDirectionIncrementInDegrees",
    "jDirectionIncrementInDegrees", "iScansNegatively", "jScansPositively",
    "jPointsAreConsecutive", "uvRelativeToGrid",
)


def require(condition: bool, message: str) -> None:
    """Raise a validation failure even when Python assertions are disabled."""
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs(root: Path) -> tuple[dict, dict]:
    """Validate the manifest and pin the immutable three-file input set."""
    directory = root / "references/gfs_p1_fixture"
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    require(manifest["schema_version"] == 1, "Unknown fixture manifest schema")
    require(manifest["document_version"] == "0.13.0", "Unsupported fixture document version")
    files = manifest["files"]
    require(len(files) == 3, "Expected exactly three fixture files")
    require({item["file"] for item in files} == set(PINNED_SHA256), "Unknown or missing fixture file")
    for item in files:
        path = directory / item["file"]
        expected_hash = PINNED_SHA256[item["file"]]
        require(item["sha256"] == expected_hash, f"Manifest hash changed: {path.name}")
        require(path.stat().st_size == item["bytes"], f"Size mismatch: {path.name}")
        require(digest(path) == expected_hash, f"SHA-256 mismatch: {path.name}")
    expected = {}
    for field in manifest["expected_fields"]:
        for level in field["levels"]:
            key = field["short_name"], field["type_of_level"], level
            require(key not in expected, f"Duplicate manifest field: {key}")
            expected[key] = field
    require(len(expected) == 139, "Expected 139 distinct manifest fields")
    levels = manifest["requested_pressure_levels_hpa"]
    require(len(levels) == 33 and levels == sorted(set(levels), reverse=True),
            "Expected 33 distinct descending requested pressure levels")
    for variable in ("gh", "t", "u", "v"):
        field_levels = {level for name, kind, level in expected
                        if name == variable and kind == "isobaricInhPa"}
        require(field_levels == set(levels),
                f"Requested and expected pressure levels differ: {variable}")
    return manifest, expected


def inspect_file(path: Path, item: dict, manifest: dict, expected: dict, eccodes, np):
    """Decode all messages; reject unknown, missing or inconsistent fields."""
    grid = manifest["grid"]
    init = datetime.fromisoformat(manifest["run_utc"].replace("Z", "+00:00"))
    require(init.utcoffset() == timedelta(0) and init.second == init.microsecond == 0,
            "Run timestamp must explicitly use UTC at a whole minute")
    valid = init + timedelta(hours=item["forecast_hour"])
    require(int(init.strftime("%Y%m%d")) == manifest["run_date"], "Manifest run date mismatch")
    require(int(init.strftime("%H%M")) == manifest["run_time"], "Manifest run time mismatch")
    checks = {
        "Ni": grid["ni"], "Nj": grid["nj"], "gridType": grid["type"],
        "dataDate": manifest["run_date"], "dataTime": manifest["run_time"],
        "validityDate": int(valid.strftime("%Y%m%d")),
        "validityTime": int(valid.strftime("%H%M")),
        "numberOfMissing": 0, "numberOfPoints": grid["ni"] * grid["nj"],
        "iDirectionIncrementInDegrees": grid["increment_degrees"],
        "jDirectionIncrementInDegrees": grid["increment_degrees"],
        "iScansNegatively": grid["i_scans_negatively"],
        "jScansPositively": grid["j_scans_positively"],
        "jPointsAreConsecutive": grid["j_points_are_consecutive"],
        "uvRelativeToGrid": grid["uv_relative_to_grid"],
    }
    expected_lats = np.repeat(np.linspace(grid["south"], grid["north"], grid["nj"]), grid["ni"])
    expected_lons = np.tile(np.linspace(grid["west"], grid["east"], grid["ni"]), grid["nj"])
    arrays, rows = {}, []
    with path.open("rb") as stream:
        while True:
            handle = eccodes.codes_grib_new_from_file(stream)
            if handle is None:
                break
            try:
                row = {key: eccodes.codes_get(handle, key) for key in KEYS}
                key = row["shortName"], row["typeOfLevel"], row["level"]
                require(key in expected, f"Unknown field in {path.name}: {key}")
                require(key not in arrays, f"Duplicate field in {path.name}: {key}")
                spec = expected[key]
                for code_key, spec_key in (("units", "units"), ("discipline", "discipline"),
                                           ("parameterCategory", "parameter_category"),
                                           ("parameterNumber", "parameter_number")):
                    require(row[code_key] == spec[spec_key], f"{path.name} {key}: {code_key} mismatch")
                for code_key, value in checks.items():
                    require(row[code_key] == value, f"{path.name} {key}: {code_key} mismatch")
                require(int(row["step"]) == item["forecast_hour"], f"Forecast hour mismatch: {path.name}")
                values = eccodes.codes_get_values(handle)
                require(len(values) == checks["numberOfPoints"], f"Value count mismatch: {path.name}")
                require(bool(np.isfinite(values).all()), f"Nonfinite values: {path.name} {key}")
                for coordinate, target in (("latitudes", expected_lats), ("longitudes", expected_lons)):
                    require(bool(np.array_equal(eccodes.codes_get_array(handle, coordinate), target)),
                            f"Coordinates or scanning order mismatch: {path.name} {coordinate}")
                arrays[key] = values
                row.update(minimum=float(values.min()), maximum=float(values.max()))
                rows.append(row)
            finally:
                eccodes.codes_release(handle)
    require(set(arrays) == set(expected), f"Missing decoded fields: {path.name}")
    require(len(rows) == item["expected_message_count"], f"Message count mismatch: {path.name}")
    require(sum(len(a) for a in arrays.values()) == item["expected_value_count"], f"Decoded value count mismatch: {path.name}")
    levels = manifest["requested_pressure_levels_hpa"]
    require(levels == sorted(set(levels), reverse=True), "Pressure levels must be distinct and descending")
    heights = np.stack([arrays["gh", "isobaricInhPa", level] for level in levels])
    require(bool(np.all(np.diff(heights, axis=0) > 0)), f"Nonmonotonic geopotential height: {path.name}")
    require(bool(np.all(heights[0] < 30000) and np.all(heights[-1] > 30000)), f"30000 gpm not bracketed: {path.name}")
    surface_pressure = arrays["sp", "surface", 0]
    below_ground = int((np.asarray(levels)[:, None] * 100 > surface_pressure[None, :]).sum())
    require(digest(path) == PINNED_SHA256[path.name], f"Input changed during inspection: {path.name}")
    result = {
        "file": path.name, "sha256": PINNED_SHA256[path.name],
        "messages_decoded": len(rows), "values_decoded": sum(len(a) for a in arrays.values()),
        "metadata_units_grid_time_missing_finite_checks": "pass",
        "monotonic_height_columns": grid["ni"] * grid["nj"],
        "brackets_30000_gpm_columns": grid["ni"] * grid["nj"],
        "below_ground_level_cells": below_ground,
        "warnings": [f"{below_ground} below-ground pressure-level cells need masking before interpolation.",
                     "Geopotential/geometric/terrain height conversion and scientific validity are not accepted."],
    }
    return result, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--root", type=Path, default=default_root, help="Input repository root (default: tool's parent repository)")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory outside the repository")
    args = parser.parse_args()
    try:
        root, output = args.root.resolve(), args.output_dir.resolve()
        require(not output.is_relative_to(root) and not output.is_relative_to(default_root),
                "Output directory must be outside the input and tool repositories")
        manifest, expected = load_inputs(root)
        import eccodes
        import numpy as np
        results, tables = [], {}
        for item in manifest["files"]:
            result, rows = inspect_file(root / "references/gfs_p1_fixture" / item["file"], item, manifest, expected, eccodes, np)
            results.append(result)
            tables[Path(item["file"]).stem + ".metadata.csv"] = rows
        targets = [output / "inspection.json"] + [output / name for name in tables]
        for target in targets:
            require(not target.exists(), f"Output already exists; choose a new directory: {target}")
            require(not target.resolve().is_relative_to(root) and not target.resolve().is_relative_to(default_root),
                    f"Output resolves inside a repository: {target}")
        output.mkdir(parents=True, exist_ok=True)
        for name, rows in tables.items():
            with (output / name).open("x", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        report = {"fixture_id": manifest["fixture_id"], "inspected_at_utc": datetime.now(timezone.utc).isoformat(),
                  "python_version": platform.python_version(), "eccodes_python_version": eccodes.__version__,
                  "eccodes_api_version": eccodes.codes_get_api_version(), "numpy_version": np.__version__,
                  "manifest_sha256": digest(root / "references/gfs_p1_fixture/manifest.json"),
                  "results": results, "not_accepted": manifest["not_accepted"]}
        with (output / "inspection.json").open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print("PASS: 3 fixed inputs, 417 GRIB2 messages, 33777 values inspected offline.")
        for result in results:
            for warning in result["warnings"]:
                print(f"WARNING {result['file']}: {warning}")
        print(f"Evidence: {output / 'inspection.json'}")
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
