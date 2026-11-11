from __future__ import annotations

from ..config import Config
from ..types import LineObservation


def follow(line: LineObservation, cfg: Config) -> tuple[float, float]:
    """Return (forward [-1..1], yaw_rate rad/s). Simple P law; placeholder."""
    yaw_rate = cfg.kp_lateral * line.lateral_offset + cfg.kp_heading * line.heading_error
    forward = cfg.cruise_speed * (1.0 - 0.5 * min(1.0, abs(line.lateral_offset)))
    return forward, yaw_rate