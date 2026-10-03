"""Burst conditions consume selected physical callbacks, never a phase config."""
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class BurstEvent:
    """Event geometry, optional gas diagnostics and exact prescribed-rate timing."""
    kind: str
    threshold: float
    gas_state: Callable | None = None
    constant_ascent_speed: float | None = None

    @property
    def requires_sample(self):
        return self.kind == "diameter"

    @property
    def has_diagnostics(self):
        return self.gas_state is not None

    def value(self, altitude_m, sample=None):
        if self.kind == "altitude":
            return altitude_m - self.threshold
        return self.gas_state(sample)[1] - self.threshold

    def diagnostics(self, sample=None):
        if self.gas_state is None:
            return {}
        volume, diameter, _ = self.gas_state(sample)
        return {"gas_volume_m3": volume, "gas_diameter_m": diameter}

    def exact_step(self, altitude_m):
        if self.kind == "altitude" and self.constant_ascent_speed is not None:
            return (self.threshold - altitude_m) / self.constant_ascent_speed
        return None

    def project_altitude(self, altitude_m):
        """Remove root-bracket roundoff only for an explicit altitude threshold."""
        return self.threshold if self.kind == "altitude" else altitude_m
