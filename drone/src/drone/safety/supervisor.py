from __future__ import annotations

from ..config import Config
from ..types import Fault, Snapshot


def evaluate(s: Snapshot, cfg: Config) -> set[Fault]:
    """Pure check of a snapshot against thresholds. Whether a fault matters in the
    current state is decided by fsm.policy.is_critical."""
    f: set[Fault] = set()
    if s.fc_heartbeat_age > cfg.fc_timeout_s:
        f.add(Fault.FC_LINK_LOST)
    if s.imu_age > cfg.imu_timeout_s:
        f.add(Fault.IMU_STALE)
    if s.depth_m is None or s.depth_age > cfg.depth_timeout_s:
        f.add(Fault.DEPTH_INVALID)
    elif s.depth_m > cfg.max_depth_m:
        f.add(Fault.DEPTH_LIMIT)
    if s.ballast_stalled:
        f.add(Fault.BALLAST_STALL)
    if s.camera_age > cfg.camera_timeout_s:
        f.add(Fault.CAMERA_LOST)
    if s.battery_v < cfg.low_battery_v:
        f.add(Fault.LOW_BATTERY)
    if s.cpu_temp_c > cfg.max_cpu_temp_c:
        f.add(Fault.OVERTEMP)
    if s.loop_dt > cfg.max_loop_dt_s:
        f.add(Fault.LOOP_OVERRUN)
    return f