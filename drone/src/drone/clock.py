import time


class RealClock:
    def now(self) -> float:
        return time.monotonic()

    def sleep_until(self, t: float) -> None:
        d = t - time.monotonic()
        if d > 0:
            time.sleep(d)


class VirtualClock:
    """Runs the loop faster than real time for simulation and tests."""

    def __init__(self) -> None:
        self._t = 0.0

    def now(self) -> float:
        return self._t

    def sleep_until(self, t: float) -> None:
        self._t = max(self._t, t)