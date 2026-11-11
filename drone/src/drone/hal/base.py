"""Hardware interfaces. Real and simulated implementations both satisfy these."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from ..types import ControlMode, Perception, Vec3


@dataclass(frozen=True)
class FCState:
    heartbeat_age: float
    imu_age: float
    gyro: Vec3          # rad/s
    accel: Vec3         # m/s^2
    attitude: Vec3      # roll, pitch, yaw (rad)
    battery_v: float


class FlightController(ABC):
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def poll(self) -> FCState: ...

    @abstractmethod
    def set_control_mode(self, mode: ControlMode) -> None: ...

    @abstractmethod
    def send_setpoint(self, roll: float, pitch: float, yaw_rate: float, thrust: float) -> None: ...

    def close(self) -> None:
        pass


class DepthSensor(ABC):
    @abstractmethod
    def read(self) -> tuple[Optional[float], float]:
        """Return (depth_m or None if invalid, age of the reading in seconds)."""


class BallastActuator(ABC):
    @abstractmethod
    def command(self, fore: float, aft: float) -> None:
        """Target fill fractions, 0 = purged (buoyant), 1 = full."""

    @abstractmethod
    def position(self) -> tuple[float, float]: ...

    @abstractmethod
    def stalled(self) -> bool: ...

    def close(self) -> None:
        pass


class Camera(ABC):
    @abstractmethod
    def read(self) -> tuple[Optional[Any], float]:
        """Return (latest frame or None, age in seconds)."""

    def close(self) -> None:
        pass


class Perceiver(ABC):
    @abstractmethod
    def process(self, frame: Any) -> Perception: ...