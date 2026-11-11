def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def compute(cmd: Command, snap: Snapshot, cfg: Config) -> tuple[float, float, float, float]:
    """Map a high-level Command to (roll, pitch, yaw_rate, thrust) for the FC.

    Placeholder: pitch from forward command, thrust from a P depth loop.
    Replace with the controller from the Simulink digital twin.
    """
    pitch = -cmd.forward * cfg.max_pitch_rad
    thrust = cfg.hover_thrust
    if cmd.depth_target is not None and snap.depth_m is not None:
        # more depth than target -> more upward thrust
        thrust = _clip(cfg.hover_thrust - cfg.kp_depth * (cmd.depth_target - snap.depth_m), 0.0, 1.0)
    return 0.0, pitch, cmd.yaw_rate, thrust