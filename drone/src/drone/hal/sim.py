"""Scripted simulated hardware so the whole stack runs on a laptop.

The world is a toy: depth responds to ballast fill; events are time-scripted.
Swap in the Simulink digital twin by implementing these same interfaces.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from ..config import Config
from ..types import ControlMode, LineObservation, Perception
from .base import BallastActuator, Camera, DepthSensor, FCState, FlightController, Perceiver
from .vehicle import Vehicle


@dataclass
class Script:
    arm_t: float = 1.0
    surface_seen_t: float = 2.0
    water_entry_t: float = 4.0
    line_gap: tuple[float, float] = (15.0, 18.0)
    edge_t: float = 30.0


class SimWorld:
    def __init__(self, script: Script) -> None:
        self.s = script
        self.t = 0.0
        self.depth = 0.0
        self.in_water = False
        self.fill = [0.0, 0.0]
        self.fill_cmd = [0.0, 0.0]
        self.fc_alive = True

    def step(self, t: float) -> None:
        dt, self.t = t - self.t, t
        for i in range(2):  # actuator slew 0.2 fill/s
            d = self.fill_cmd[i] - self.fill[i]
            self.fill[i] += max(-0.2 * dt, min(0.2 * dt, d))
        if not self.in_water and t >= self.s.water_entry_t:
            self.in_water, self.depth = True, 0.1
        if self.in_water:
            avg = sum(self.fill) / 2
            self.depth = max(0.0, self.depth + 0.4 * (avg - 0.4) * dt)

    @property
    def line_visible(self) -> bool:
        a, b = self.s.line_gap
        return self.in_water and not (a <= self.t < b)


class SimFC(FlightController):
    def __init__(self, world: SimWorld) -> None:
        self.w = world
        self.mode = None

    def connect(self) -> None: ...

    def poll(self) -> FCState:
        hb = 0.01 if self.w.fc_alive else 99.0
        return FCState(hb, 0.01, (0, 0, 0), (0, 0, 9.81), (0, 0, 0), 16.0)

    def set_control_mode(self, mode: ControlMode) -> None:
        self.mode = mode

    def send_setpoint(self, roll, pitch, yaw_rate, thrust) -> None: ...


class SimDepth(DepthSensor):
    def __init__(self, world: SimWorld) -> None:
        self.w = world

    def read(self) -> tuple[Optional[float], float]:
        return self.w.depth, 0.01


class SimBallast(BallastActuator):
    def __init__(self, world: SimWorld) -> None:
        self.w = world

    def command(self, fore: float, aft: float) -> None:
        self.w.fill_cmd = [fore, aft]

    def position(self) -> tuple[float, float]:
        return (self.w.fill[0], self.w.fill[1])

    def stalled(self) -> bool:
        return False


class SimCamera(Camera):
    def __init__(self, world: SimWorld) -> None:
        self.w = world

    def read(self) -> tuple[Optional[Any], float]:
        return self.w, 0.0  # the "frame" is the world itself; SimPerceiver reads it


class SimPerceiver(Perceiver):
    def process(self, frame: SimWorld) -> Perception:
        line = LineObservation(0.1, 0.05, 0.9) if frame.line_visible else None
        return Perception(
            line=line,
            surface_detected=frame.s.surface_seen_t <= frame.t < frame.s.water_entry_t,
            edge_detected=frame.t >= frame.s.edge_t,
        )


class SimVehicle(Vehicle):
    def __init__(self, cfg: Config, script: Script | None = None) -> None:
        self.world = SimWorld(script or Script())
        w = self.world
        super().__init__(cfg, SimFC(w), SimDepth(w), SimBallast(w), SimCamera(w), SimPerceiver())

    def cpu_temp_c(self) -> float:
        return 45.0

    def read(self, t: float, loop_dt: float):
        self.world.step(t)
        self.arm_request = t >= self.world.s.arm_t
        return super().read(t, loop_dt)