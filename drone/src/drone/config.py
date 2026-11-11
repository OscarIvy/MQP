"""All tunables in one place. Every number here is a PLACEHOLDER until tuned."""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Optional


@dataclass
class Config:
    # loop / hardware
    loop_hz: float = 20.0
    fc_device: str = "/dev/serial0"
    fc_baud: int = 921600
    camera_index: int = 0
    camera_width: int = 640
    camera_height: int = 480
    camera_fps: int = 30
    record_dir: str = "recordings"
    # fault thresholds
    fc_timeout_s: float = 1.0
    imu_timeout_s: float = 0.25
    depth_timeout_s: float = 0.5
    camera_timeout_s: float = 0.5
    max_depth_m: float = 3.0
    low_battery_v: float = 14.0
    max_cpu_temp_c: float = 80.0
    max_loop_dt_s: float = 0.2
    # mission geometry
    submerge_depth_m: float = 0.08
    surface_depth_m: float = 0.05
    target_depth_m: float = 1.0
    depth_tol_m: float = 0.1
    # ballast fill fractions (0 = purged/buoyant, 1 = full)
    ballast_purged: float = 0.0
    ballast_neutral: float = 0.4
    ballast_dive: float = 0.8
    # timers
    transition_timeout_s: float = 20.0
    ascent_timeout_s: float = 30.0
    line_lost_s: float = 2.0
    search_timeout_s: float = 15.0
    surface_lost_s: float = 1.0
    # line following / search
    min_line_confidence: float = 0.3
    search_yaw_rate: float = 0.3
    kp_lateral: float = 0.8
    kp_heading: float = 0.6
    cruise_speed: float = 0.5
    # setpoint mapping (placeholder until the Simulink-derived controller lands)
    max_pitch_rad: float = 0.35
    hover_thrust: float = 0.5
    kp_depth: float = 0.4


def load(path: Optional[str] = None) -> Config:
    if path is None:
        return Config()
    import yaml

    with open(path) as f:
        data = yaml.safe_load(f) or {}
    unknown = set(data) - {f.name for f in fields(Config)}
    if unknown:
        raise ValueError(f"Unknown config keys: {sorted(unknown)}")
    return Config(**data)