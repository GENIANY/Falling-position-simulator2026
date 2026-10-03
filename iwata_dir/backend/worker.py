"""Picklable, HTTP-free process entry point. Uses saved fields only."""
from __future__ import annotations

import importlib.metadata
import platform
from pathlib import Path

from balloon_sim.environment.storage import load_weather
from balloon_sim.flight.trajectory import simulate
from balloon_sim.results.export import export_result

from .storage import digest, file_hash

REPO_ROOT = Path(__file__).resolve().parents[1]


def source_snapshot():
    files = {}
    for folder in ("balloon_sim", "backend"):
        paths = (REPO_ROOT / folder).rglob("*.py") if folder == "balloon_sim" else (REPO_ROOT / folder).glob("*.py")
        paths = list(paths)
        if folder == "backend":
            paths += list((REPO_ROOT / "backend" / "weather").rglob("*.py"))
            paths += list((REPO_ROOT / "backend" / "ensemble").rglob("*.py"))
            paths += list((REPO_ROOT / "backend" / "climate").rglob("*.py"))
        for path in sorted(paths):
            files[path.relative_to(REPO_ROOT).as_posix()] = file_hash(path)
    environment = {"python": platform.python_version(), "implementation": platform.python_implementation(),
                   "numpy": importlib.metadata.version("numpy"), "scipy": importlib.metadata.version("scipy"),
                   "geographiclib": importlib.metadata.version("geographiclib")}
    content = {"files": files, "environment": environment}
    return {**content, "fingerprint": digest(content)}


def execute_run(spec, weather_path, config_path, staging_path):
    """Calculate exactly one fixed input; numerical stops are valid results."""
    if source_snapshot() != spec["source_snapshot"]:
        raise ValueError("source or numerical environment changed after submission")
    if file_hash(weather_path) != spec["weather_snapshot"]["sha256"]:
        raise ValueError("saved weather changed after submission")
    if file_hash(config_path) != spec["config_file_sha256"]:
        raise ValueError("fixed config file changed after submission")
    weather = load_weather(weather_path)
    result = simulate(spec["config"], weather)
    export_result(result, config_path, weather_path, staging_path, weather.metadata)
    if (source_snapshot() != spec["source_snapshot"]
            or file_hash(weather_path) != spec["weather_snapshot"]["sha256"]
            or file_hash(config_path) != spec["config_file_sha256"]):
        raise ValueError("fixed inputs changed during execution; result was not committed")
    # No large arrays/results are transferred through the process queue.
    return {"run_id": spec["run_id"], "status": result["status"]}
