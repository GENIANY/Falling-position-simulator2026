"""Pure forecast planning and dependency admission; no acquisition or model choice."""
from datetime import timedelta
import importlib
import importlib.metadata
from pathlib import Path

from balloon_sim.environment.fields import WeatherError, _utc
from balloon_sim.environment.gfs import _request, estimate_decode_bytes

from ..storage import digest, file_hash


def dependencies():
    versions, missing = {}, []
    for module, distribution in (("numpy", "numpy"), ("eccodes", "eccodes"),
                                 ("geographiclib", "geographiclib")):
        try:
            loaded = importlib.import_module(module)
            versions[distribution] = importlib.metadata.version(distribution)
            if module == "eccodes":
                versions["eccodes_api"] = loaded.codes_get_api_version()
        except (ImportError, OSError, RuntimeError, importlib.metadata.PackageNotFoundError) as exc:
            missing.append({"name": distribution, "message": str(exc)})
    return {"available": not missing, "versions": versions, "missing": missing}


def decoder_identity(dependency_state):
    root = Path(__file__).resolve().parents[2] / "balloon_sim" / "environment"
    files = {p.name: file_hash(p) for p in sorted(root.glob("*.py"))}
    if not {"gfs.py", "gfs_contract.py", "fields.py", "storage.py"} <= set(files):
        raise ValueError("decoder source inventory is incomplete")
    return {"files": files, "versions": dependency_state["versions"]}


def region_bounds(region):
    if region["kind"] == "bounds":
        return {key: region[key] for key in ("west", "east", "south", "north")}
    from geographiclib.geodesic import Geodesic
    lat, lon = region["latitude_deg"], region["longitude_deg"]
    points = {bearing: Geodesic.WGS84.Direct(lat, lon, bearing, distance * 1000)
              for bearing, distance in ((0, region["half_height_km"]),
                                        (180, region["half_height_km"]),
                                        (90, region["half_width_km"]),
                                        (270, region["half_width_km"]))}
    bounds = {"south": points[180]["lat2"], "north": points[0]["lat2"],
              "west": points[270]["lon2"], "east": points[90]["lon2"]}
    if not bounds["south"] <= lat <= bounds["north"] or not bounds["west"] < lon < bounds["east"]:
        raise WeatherError("UNSUPPORTED_SEAM", "Region crosses a pole or longitude seam; choose a smaller rectangle.")
    return bounds


def launch_support(request, bounds):
    """Bind each declared launch to the actual rounded acquisition rectangle."""
    return [{"candidate_id": w["candidate_id"],
             "latitude_deg": w["latitude_deg"], "longitude_deg": w["longitude_deg"],
             "inside": bounds["south"] <= w["latitude_deg"] <= bounds["north"] and any(
                 bounds["west"] <= lon <= bounds["east"] for lon in
                 (w["longitude_deg"]-360, w["longitude_deg"], w["longitude_deg"]+360))}
            for w in request["candidate_windows"]]


def make_plan(request, inventory, dependency_state):
    starts = [_utc(w["launch_time_utc"]) for w in request["candidate_windows"]]
    ends = [start + timedelta(seconds=w["max_duration_s"] + request["end_margin_s"])
            for start, w in zip(starts, request["candidate_windows"])]
    raw = {"run_utc": request["run_utc"], "start_utc": min(starts).isoformat(),
           "end_utc": max(ends).isoformat(), "bounds": region_bounds(request["region"]),
           "max_bytes": request["max_bytes"]}
    spec = _request(raw)
    b = spec["bounds"]
    grid = (round((b["east"]-b["west"])*4)+1) * (round((b["north"]-b["south"])*4)+1)
    values = grid * len(spec["lead_hours"]) * 171
    # Admission estimate includes Python scalars/containers, parsed JSON, immutable
    # arrays and GRIB coordinate temporaries. It is not a measured RSS guarantee.
    memory = estimate_decode_bytes(spec)
    selected = next((r for r in inventory["runs"] if r["run_utc"] == spec["run_utc"]), None)
    available = set(selected["available_leads"]) if selected else set()
    missing = [lead for lead in spec["lead_hours"] if lead not in available]
    issues = []
    support = launch_support(request, b)
    outside = [w["candidate_id"] for w in support if not w["inside"]]
    if outside:
        issues.append({"code": "LAUNCH_OUTSIDE_REGION", "candidate_ids": outside,
                       "message": "Launch points are outside the rounded acquisition region: " + ", ".join(outside)})
    if selected is None:
        issues.append({"code": "RUN_NOT_OBSERVED", "message": "The fixed run was not observed in this saved inventory."})
    elif missing:
        issues.append({"code": "REQUIRED_LEADS_NOT_LISTED", "message": "Required files were not listed in the observed run directory; no older run is substituted."})
    if not dependency_state["available"]:
        issues.append({"code": "DEPENDENCIES_UNAVAILABLE", "message": "Install the declared decoder dependencies before acquisition."})
    if memory > request["max_memory_bytes"]:
        issues.append({"code": "MEMORY_BUDGET_EXCEEDED", "message": "The conservative decoded-memory estimate exceeds the selected limit; reduce area or time window."})
    identity = decoder_identity(dependency_state)
    return {"status": "unavailable" if issues else "ready", "request": request,
            "normalized_request": spec,
            "required_window": {"start_utc": raw["start_utc"], "end_utc": raw["end_utc"]},
            "inventory_observed_at_utc": inventory["observed_at_utc"], "missing_leads": missing,
            "issues": issues,
            "launch_support": support,
            "estimate": {"grid_points": grid, "time_count": len(spec["lead_hours"]),
                         "scalar_values": values, "float64_bytes": values*8,
                         "estimated_working_memory_bytes": memory,
                         "max_memory_bytes": request["max_memory_bytes"],
                         "max_download_bytes": spec["max_bytes"], "download_bytes_exact": False},
            "dependencies": dependency_state, "decoder_identity": identity,
            "cache_key": digest({"request": spec, "decoder": identity})}
