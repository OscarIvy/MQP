from __future__ import annotations

import threading
import time
from typing import Any, Optional

from ..config import Config
from .base import Camera


class UsbCamera(Camera):
    """UVC camera via OpenCV/V4L2, read in a thread so the control loop never blocks."""

    def __init__(self, cfg: Config) -> None:
        import cv2

        self._cap = cv2.VideoCapture(cfg.camera_index, cv2.CAP_V4L2)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.camera_width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.camera_height)
        self._cap.set(cv2.CAP_PROP_FPS, cfg.camera_fps)
        self._frame: Any = None
        self._t = 0.0
        self._lock = threading.Lock()
        self._run = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while self._run:
            ok, frame = self._cap.read()
            if ok:
                with self._lock:
                    self._frame, self._t = frame, time.monotonic()
            else:
                time.sleep(0.01)

    def read(self) -> tuple[Optional[Any], float]:
        with self._lock:
            if self._frame is None:
                return None, float("inf")
            return self._frame, time.monotonic() - self._t

    def close(self) -> None:
        self._run = False
        self._thread.join(timeout=1.0)
        self._cap.release()