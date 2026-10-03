"""Frozen sensitivity draws and read-only analysis of completed flight sets.

No job, storage, network or screen dependencies. The application owns trial
states; these functions never simulate, retry or fill missing flights.
"""
from .sampling import freeze_drawset, resolve_config, RESOLVER_VERSION
from .statistics import analyze_results

__all__ = ["freeze_drawset", "resolve_config", "RESOLVER_VERSION", "analyze_results"]
