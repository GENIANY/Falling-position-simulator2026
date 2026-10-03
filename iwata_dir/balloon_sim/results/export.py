"""Result serialization and one-run provenance, preserving stopped trajectories."""
import csv
import hashlib
import json
from pathlib import Path
from .. import __version__
from .report import render_report

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _write_json(path, value):
    Path(path).write_text(_json(value), encoding="utf-8", newline="\n")


def _point(record):
    return [record["longitude_deg"], record["latitude_deg"], record["altitude_m"]]


def make_geojson(result):
    records = result["records"]
    features = []
    if len(records) >= 2:
        features.append({"type": "Feature", "geometry": {"type": "LineString",
                         "coordinates": [_point(r) for r in records]},
                         "properties": {"status": result["status"], "complete": result["complete"],
                                        "times_utc": [r["time_utc"] for r in records],
                                        "phases": [r["phase"] for r in records]}})
    for event in result["events"]:
        if all(k in event for k in ("longitude_deg", "latitude_deg", "altitude_m")):
            features.append({"type": "Feature", "geometry": {"type": "Point",
                             "coordinates": _point(event)}, "properties": dict(event)})
    return {"type": "FeatureCollection", "features": features,
            "height_note": "coordinates[2] is model geometric altitude m, not a surveyed landing elevation"}


def export_result(result, config_path, weather_path, output_dir, weather_metadata):
    """Create one new output directory. Never modify inputs or reuse old output."""
    out=Path(output_dir)
    if out.exists():
        raise FileExistsError("output already exists: "+str(out))
    config_path,weather_path=Path(config_path),Path(weather_path)
    package = Path(__file__).resolve().parents[1]
    provenance={"package_version":__version__,
                "numerics":result.get("numerics",{}),
                "config":{"path":str(config_path.resolve()),"sha256":sha256(config_path)},
                "weather_bundle":{"path":str(weather_path.resolve()),"sha256":sha256(weather_path),
                                  "metadata":weather_metadata},
                "source_sha256":{p.relative_to(package).as_posix():sha256(p)
                                  for p in sorted(package.rglob("*.py"))},
                "reproduction":"Run simulate with the same config, bundle, source, and numerical settings; do not replace saved input with a newer forecast."}
    out.mkdir(parents=True,exist_ok=False)
    (out/"input.json").write_bytes(config_path.read_bytes())
    _write_json(out/"result.json",result)
    _write_json(out/"provenance.json",provenance)
    _write_json(out/"trajectory.geojson",make_geojson(result))
    preferred=["time_utc","elapsed_s","latitude_deg","longitude_deg","altitude_m",
               "ground_altitude_m","height_agl_m","phase","vertical_speed_m_s",
               "eastward_wind_m_s","northward_wind_m_s","weather_quality"]
    extra=sorted({k for r in result["records"] for k in r}-set(preferred))
    with (out/"trajectory.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=preferred+extra);writer.writeheader()
        for row in result["records"]:
            writer.writerow({k:(json.dumps(v,ensure_ascii=False,allow_nan=False) if isinstance(v,(list,dict)) else v) for k,v in row.items()})
    (out/"report.html").write_text(render_report(result,provenance),encoding="utf-8",newline="\n")
    files={p.name:{"bytes":p.stat().st_size,"sha256":sha256(p)} for p in sorted(out.iterdir()) if p.is_file()}
    _write_json(out/"manifest.json",{"schema":"balloon.flight.output_manifest/1","files":files,
                                     "complete":result["complete"],"status":result["status"]})
    return out
