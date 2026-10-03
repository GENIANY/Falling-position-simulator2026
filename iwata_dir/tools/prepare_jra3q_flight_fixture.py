"""Prepare one saved JRA example for the current flight CLI, fully offline.

This is a fixed research-source conversion, not a general JRA downloader. The
old decoder validates its pinned original responses; the simulator subsequently
loads only the resulting bundle through balloon_sim.environment.jra3q.
"""
from pathlib import Path
import argparse
import hashlib
import json
import time

from tools.normalize_jra3q_model_fixture import load_fixture
from balloon_sim.environment.jra3q import Jra3qModelField, SCHEMA, PRODUCT
from balloon_sim.environment.storage import write_bundle, load_weather, read_json


def prepare(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if root != Path(__file__).resolve().parents[1]:
        raise ValueError("root must match the executing source checkout")
    if output.exists():
        raise FileExistsError("existing output is preserved: " + str(output))
    start = time.perf_counter()
    environment = load_fixture(root)
    decoded = time.perf_counter()
    provenance = environment.provenance
    bundle = {
        "schema": SCHEMA, "product": PRODUCT,
        "axes": {"time_utc": [t.isoformat() for t in environment.times],
                 "model_level": list(environment.levels),
                 "latitude_deg": environment.latitudes, "longitude_deg": environment.longitudes},
        "fields": {"geopotential_height_gpm": environment.heights,
                   **{k: v for k, v in environment.fields.items() if k != "pressure_pa"}},
        "surface": {"pressure_pa": environment.surface_pressure,
                    "geopotential_height_gpm": environment.surface_height},
        "hybrid": {"a_half_pa": provenance["half_coefficients_pa"],
                   "b_half": provenance["half_coefficients_dimensionless"]},
        "metadata": {"source": provenance,
                     "scope": "Saved 2024-01-01 00/06 UTC, 100 levels, 2x2 grid; not a complete ground-flight field",
                     "surface_support": "No 2m thermodynamics or 10m winds; strict column support rejects ground gaps",
                     "preparation": {"command": "python -m tools.prepare_jra3q_flight_fixture",
                                     "source_files": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                         for name in ("tools/prepare_jra3q_flight_fixture.py",
                                                      "tools/normalize_jra3q_model_fixture.py",
                                                      "tools/normalize_gfs_fixture.py")}}},
    }
    field = Jra3qModelField(bundle)
    if field.pressures != environment.pressures:
        raise ValueError("new pressure binding differs from pinned fixture")
    validated = time.perf_counter()
    output.mkdir(parents=True, exist_ok=False)
    target = output / "weather.json.gz"
    write_bundle(target, bundle)
    if read_json(target) != json.loads(json.dumps(bundle, allow_nan=False)):
        raise ValueError("saved bundle payload differs, including axes and surface")
    restored = load_weather(target)
    if (restored.heights != field.heights or restored.fields != field.fields
            or restored.metadata != field.metadata):
        raise ValueError("saved weather readback differs")
    elapsed = time.perf_counter() - start
    receipt = {"schema": "balloon.jra3q.prepared_fixture/1", "source_bundle_sha256": provenance["source_bundle_sha256"],
               "bundle_sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "bundle_bytes": target.stat().st_size,
               "timing_seconds": {"decode_original": decoded - start, "validate_new": validated - decoded,
                                  "total_with_save_readback": elapsed}, "network_requests": 0,
               "scope": "Offline conversion/readback. No ground layer was added; no scientific-accuracy acceptance."}
    with (output / "receipt.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(prepare(args.root, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
