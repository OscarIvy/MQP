from __future__ import annotations

import argparse
import logging

from .clock import RealClock, VirtualClock
from .config import Config, load
from .fsm.machine import Machine
from .safety.supervisor import evaluate

log = logging.getLogger("drone")


def run(vehicle, cfg: Config, clock, duration: float | None = None) -> Machine:
    machine = Machine(cfg)
    period = 1.0 / cfg.loop_hz
    t0 = last = clock.now()
    prev = machine.state
    try:
        while duration is None or clock.now() - t0 < duration:
            t = clock.now()
            snap = vehicle.read(t, t - last)
            last = t
            cmd = machine.step(snap, evaluate(snap, cfg))
            vehicle.apply(cmd, snap)
            if machine.state is not prev:
                log.info("t=%6.2fs  %s -> %s", t - t0, prev.name, machine.state.name)
                prev = machine.state
            clock.sleep_until(t + period)
    finally:
        vehicle.close()
    return machine


def build_real(cfg: Config, auto_arm: bool):
    from .hal.ardupilot import ArduPilotFC
    from .hal.ballast import LinearActuatorBallast
    from .hal.camera import UsbCamera
    from .hal.depth import I2CPressureDepth
    from .hal.vehicle import Vehicle
    from .perception.line import LinePerception
    from .perception.recorder import Recorder

    fc = ArduPilotFC(cfg.fc_device, cfg.fc_baud)
    fc.connect()
    v = Vehicle(cfg, fc, I2CPressureDepth(), LinearActuatorBallast(), UsbCamera(cfg),
                LinePerception(cfg), Recorder(cfg))
    v.arm_request = auto_arm  # TODO: wire to a real operator input (RC switch / button)
    return v


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true", help="run against scripted simulated hardware")
    ap.add_argument("--config", default=None)
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--auto-arm", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = load(args.config)
    if args.sim:
        from .hal.sim import SimVehicle

        run(SimVehicle(cfg), cfg, VirtualClock(), args.duration or 45.0)
    else:
        run(build_real(cfg, args.auto_arm), cfg, RealClock(), args.duration)


if __name__ == "__main__":
    main()