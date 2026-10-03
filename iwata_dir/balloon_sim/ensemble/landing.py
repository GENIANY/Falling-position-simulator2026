"""Finite-sample landing coverage and all-point extent in a regional plane."""
import math

import numpy as np
from scipy.spatial import ConvexHull, QhullError

from .geography import LocalPlane, MAX_RADIUS_M, supported_ring

POSITION_TOLERANCE_M = 1e-6


def _geometry(points, plane, rank):
    coords = [plane.lonlat(p) for p in points]
    if not supported_ring(coords):
        return None
    if rank == 0:
        return {"type": "Point", "coordinates": coords[0]}
    if rank == 1:
        return {"type": "LineString", "coordinates": coords}
    return {"type": "Polygon", "coordinates": [coords + [coords[0]]]}


def landing_analysis(items):
    """Coverage means included empirical landings, not a calibrated probability.

    Radius ordering uses a pseudoinverse only in numerically supported axes.
    A discarded axis is required to have <=1 micrometre actual residual, so a
    visibly thin cloud is never made into a line merely by covariance conditioning.
    """
    rows = [(i["trial_id"], i["result"]["summary"]["landing"])
            for i in items if i["result"] and i["result"]["status"] == "landed"]
    n = len(rows)
    out = {"method": "regional-empirical-mahalanobis/1", "n": n,
           "population": "selected_landed", "mean": None, "rank": None,
           "bands": [], "extent": None, "unavailable_reason": None,
           "position_tolerance_m": POSITION_TOLERANCE_M,
           "max_plot_radius_m": MAX_RADIUS_M,
           "limits": ["empirical coverage, not a normal model or forecast probability",
                      "ellipses may cover empty space between curved or multiple modes",
                      "geographic rings are finite plotting approximations to projected geometry"]}
    if not rows:
        out["unavailable_reason"] = "NO_LANDED_TRIALS"
        return out
    lat = np.array([p["latitude_deg"] for _, p in rows], dtype=float)
    lon = np.array([p["longitude_deg"] for _, p in rows], dtype=float)
    if not np.all(np.isfinite(lat)) or not np.all(np.isfinite(lon)):
        raise ValueError("landing coordinates must be finite")
    if np.any(np.abs(lat) >= 85) or np.ptp(lon) > 180:
        out["unavailable_reason"] = "REGIONAL_PLOT_DOMAIN"
        return out
    plane = LocalPlane(float(lat.mean()), float(lon.mean()))
    xy = np.array([plane.xy(a, b) for a, b in zip(lat, lon)])
    if np.any(np.linalg.norm(xy, axis=1) > MAX_RADIUS_M):
        out["unavailable_reason"] = "REGIONAL_PLOT_RADIUS"
        return out
    center = xy.mean(axis=0)
    ll = plane.lonlat(center)
    out["mean"] = {"longitude_deg": ll[0], "latitude_deg": ll[1]}
    delta = xy - center
    covariance = delta.T @ delta / max(1, n - 1)
    eigen, axes = np.linalg.eigh(covariance)
    projected = delta @ axes
    residuals = np.max(np.abs(projected), axis=0)
    # A numerical eigensolver can round a tiny negative eigenvalue. If the
    # associated spatial residual is real, do not manufacture a rank/coverage.
    active = residuals > POSITION_TOLERANCE_M
    if np.any((eigen <= 0) & active):
        out["unavailable_reason"] = "COVARIANCE_NUMERIC_RESOLUTION"
        return out
    rank = int(active.sum())
    out.update(rank=rank, discarded_axis_max_residual_m=float(max(residuals[~active], default=0)),
               projection={"method": "WGS84-azimuthal-equidistant",
                           "latitude_deg": plane.latitude, "longitude_deg": plane.longitude})
    scores = np.sum(projected[:, active] ** 2 / eigen[active], axis=1) if rank else np.zeros(n)
    order = np.sort(scores)
    if rank == 0:
        extent = [center]
    elif rank == 1:
        axis = axes[:, active][:, 0]
        v = projected[:, active][:, 0]
        extent = [center + axis * v.min(), center + axis * v.max()]
    else:
        try:
            extent = xy[ConvexHull(xy).vertices]
        except QhullError:
            out["unavailable_reason"] = "HULL_NUMERIC_RESOLUTION"
            return out
    out["extent"] = _geometry(extent, plane, rank)
    for probability in (0.5, 0.9, 0.95):
        k = math.ceil(probability * n)
        threshold = float(order[k - 1])
        # A relative score epsilon can have a sizeable spatial radius when the
        # cloud is very large, and would count points outside a Point/line.
        # Ties here mean equality of the computed finite-precision scores.
        tolerance = 0.0
        included = scores <= threshold
        actual_rank = rank if threshold > 0 else 0
        if actual_rank == 0:
            points = [center]
        elif actual_rank == 1:
            axis = axes[:, active][:, 0]
            radius = math.sqrt(threshold * eigen[active][0])
            points = [center - radius * axis, center + radius * axis]
        else:
            # Include observed boundary directions to avoid cutting a selected
            # boundary point off an inscribed, discretized ellipse in the plane.
            normalized = projected / np.sqrt(eigen)
            boundary_angles = np.arctan2(normalized[included, 1], normalized[included, 0])
            angles = np.unique(np.concatenate((np.linspace(-math.pi, math.pi, 180, endpoint=False), boundary_angles)))
            unit = np.column_stack((np.cos(angles), np.sin(angles)))
            points = center + (unit * np.sqrt(eigen * threshold)) @ axes.T
        geometry = _geometry(points, plane, actual_rank)
        out["bands"].append({"probability": probability, "rank_index": k,
                             "count": int(included.sum()), "total": n,
                             "trial_ids": [row[0] for row, keep in zip(rows, included) if keep],
                             "threshold": threshold, "score_tolerance": tolerance,
                             "geometry": geometry, "geometry_rank": actual_rank,
                             "unavailable_reason": None if geometry else "REGIONAL_PLOT_DOMAIN"})
    return out
