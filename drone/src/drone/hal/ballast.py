from __future__ import annotations

from .base import BallastActuator


class LinearActuatorBallast(BallastActuator):
    """TODO: drive two linear actuators (fore/aft syringes).

    Needs, per actuator: a motor driver (PWM/DIR), position feedback (pot or limit
    switches), a position controller, and stall detection (commanded move with no
    position change for N ms -> stalled() True). Pi 5 GPIO: use gpiozero with the lgpio backend.
    """

    def __init__(self) -> None:
        raise NotImplementedError("Implement the ballast actuator driver")

    def command(self, fore: float, aft: float) -> None:
        raise NotImplementedError

    def position(self) -> tuple[float, float]:
        raise NotImplementedError

    def stalled(self) -> bool:
        raise NotImplementedError