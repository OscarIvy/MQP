from __future__ import annotations

from typing import Optional

from .base import DepthSensor

G = 9.80665


def pressure_to_depth(p_pa: float, p_surface_pa: float, rho: float = 997.0) -> float:
    """Fresh water by default (pool). Use ~1025 for seawater."""
    return (p_pa - p_surface_pa) / (rho * G)


class I2CPressureDepth(DepthSensor):
    """TODO: pick the driver for your sensor (e.g. MS5837 via the `ms5837` package).

    Plan: read pressure in a background thread, zero p_surface_pa at startup in air,
    return (pressure_to_depth(...), age_seconds), or (None, age) on bad CRC/timeouts.
    """

    def __init__(self, bus: int = 1) -> None:
        raise NotImplementedError("Implement the I2C pressure sensor driver")

    def read(self) -> tuple[Optional[float], float]:
        raise NotImplementedError