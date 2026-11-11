"""Glue: reads all hardware into a Snapshot and applies a Command back to it."""
from __future__ import annotations

from typing import Any, Optional

from ..config import Config
from ..control import setpoints
from ..types import Command, ControlMode, Perception, Snapshot
from .base import BallastActuator, Camera, DepthSensor, FlightController, Perceiver


class Vehicle:
    def __init__(self, cfg: Config, fc: FlightController, depth: DepthSensor,
                 ballast: BallastActuator, camera: Camera, perceiver: Perceiver,
                 recorder: Any = None) -> None:
        self.cfg, self.fc, self.depth, self.ballast = cfg, fc, depth, ballast
        self.camera, self.perceiver, self.recorder = camera, perceiver, recorder
        self.arm_request = False
        self.takeoff_request = False
        self.reset_request = False
        self._mode: Optional[ControlMode] = None
        self._frame: Any = None

    def cpu_temp_c(self) -> float:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                return int(f.read()) / 1000.0
        except OSError:
            return 0.0

    def read(self, t: float, loop_dt: float) -> Snapshot:
        fc = self.fc.poll()
        depth_m, depth_age = self.depth.read()
        frame, cam_age = self.camera.read()
        self._frame = frame
        perc = self.perceiver.process(frame) if frame is not None else Perception()
        snap = Snapshot(
            t=t, fc_heartbeat_age=fc.heartbeat_age, imu_age=fc.imu_age,
            gyro=fc.gyro, accel=fc.accel, attitude=fc.attitude,
            depth_m=depth_m, depth_age=depth_age, camera_age=cam_age,
            line=perc.line, surface_detected=perc.surface_detected, edge_detected=perc.edge_detected,
            ballast_pos=self.ballast.position(), ballast_stalled=self.ballast.stalled(),
            battery_v=fc.battery_v, cpu_temp_c=self.cpu_temp_c(), loop_dt=loop_dt,
            arm_request=self.arm_request, takeoff_request=self.takeoff_request,
            reset_request=self.reset_request,
        )
        self.takeoff_request = self.reset_request = False  # one-shot requests
        return snap

    def apply(self, cmd: Command, snap: Snapshot) -> None:
        if cmd.mode is not self._mode:
            self.fc.set_control_mode(cmd.mode)
            self._mode = cmd.mode
        self.ballast.command(*cmd.ballast)
        if cmd.mode is ControlMode.DEPTH_LINE:
            self.fc.send_setpoint(*setpoints.compute(cmd, snap, self.cfg))
        if self.recorder is not None:
            self.recorder.update(cmd.record_video, self._frame)

    def close(self) -> None:
        for dev in (self.fc, self.ballast, self.camera, self.recorder):
            if dev is not None:
                dev.close()