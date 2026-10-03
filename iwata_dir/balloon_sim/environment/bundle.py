"""Accept the existing GFS pressure/surface weather bundle as an offline field."""
from .fields import PressureLevelField
from .gfs_contract import validate_gfs_times


class WeatherField(PressureLevelField):
    """Compatibility bundle contract, including GFS schedule and quality policy.

    The reconstruction is inherited from PressureLevelField; this binding makes
    the existing GFS-specific input policy explicit rather than silently imposing
    it on a future product adapter. Constructor and public query APIs are stable.
    """
    def __init__(self, bundle):
        super().__init__(bundle, quality_flags=("coarse_gfs_orography",),
                         validate_times=validate_gfs_times)
        self.metadata.setdefault("terrain", "GFS coarse geopotential orography; not a fine DEM")
