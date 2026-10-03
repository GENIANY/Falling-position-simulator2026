"""Regional plotting coordinates, separate from trajectory dynamics."""
import math

from geographiclib.geodesic import Geodesic

GEODESIC = Geodesic.WGS84
MAX_RADIUS_M = 1_000_000.0


class LocalPlane:
    """WGS84 azimuthal-equidistant coordinates about an explicit anchor.

    This is a finite regional display convention, not an Earth-wide probability
    geometry. The 1000 km plotting radius is reported by analysis, not applied
    to trial denominators or landing/forbidden-region classification.
    """
    def __init__(self, latitude, longitude):
        self.latitude, self.longitude = latitude, longitude

    def xy(self, latitude, longitude):
        g = GEODESIC.Inverse(self.latitude, self.longitude, latitude, longitude)
        azimuth = math.radians(g["azi1"])
        return g["s12"] * math.sin(azimuth), g["s12"] * math.cos(azimuth)

    def lonlat(self, xy):
        east, north = map(float, xy)
        g = GEODESIC.Direct(self.latitude, self.longitude,
                            math.degrees(math.atan2(east, north)), math.hypot(east, north))
        return [g["lon2"], g["lat2"]]


def supported_ring(coordinates):
    return all(abs(p[1]) < 85 for p in coordinates) and all(
        abs(a[0] - b[0]) <= 180 for a, b in zip(coordinates, coordinates[1:]))
