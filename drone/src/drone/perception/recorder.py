from __future__ import annotations

import os
import time
from typing import Any

from ..config import Config


class Recorder:
    """Writes frames to a new timestamped file while recording is requested."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._writer: Any = None
        os.makedirs(cfg.record_dir, exist_ok=True)

    def update(self, want: bool, frame: Any) -> None:
        import cv2

        if want and frame is not None:
            if self._writer is None:
                path = os.path.join(self.cfg.record_dir, time.strftime("%Y%m%d-%H%M%S") + ".mp4")
                h, w = frame.shape[:2]
                self._writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), self.cfg.camera_fps, (w, h))
            self._writer.write(frame)
        elif not want and self._writer is not None:
            self.close()

    def close(self) -> None:
        if self._writer is not None:
            self._writer.release()
            self._writer = None