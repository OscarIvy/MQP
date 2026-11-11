from __future__ import annotations

import math
from typing import Any, Optional

import cv2

from ..config import Config
from ..hal.base import Perceiver
from ..types import LineObservation, Perception


def detect_line(frame_bgr: Any, dark_line: bool = True, min_area_frac: float = 0.005) -> Optional[LineObservation]:
    gray = cv2.GaussianBlur(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    mode = cv2.THRESH_BINARY_INV if dark_line else cv2.THRESH_BINARY
    _, mask = cv2.threshold(gray, 0, 255, mode + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    c = max(contours, key=cv2.contourArea)
    h, w = mask.shape
    frac = cv2.contourArea(c) / (h * w)
    if frac < min_area_frac:
        return None
    vx, vy, x0, _ = cv2.fitLine(c, cv2.DIST_L2, 0, 0.01, 0.01).flatten()
    if vy > 0:  # orient the direction vector to point "up" in the image (forward)
        vx, vy = -vx, -vy
    return LineObservation(
        lateral_offset=float((x0 - w / 2) / (w / 2)),
        heading_error=float(math.atan2(vx, -vy)),
        confidence=float(min(1.0, frac / 0.05)),
    )


class LinePerception(Perceiver):
    """TODO: water-surface and pool-edge detection (return False until implemented)."""

    def __init__(self, cfg: Config, dark_line: bool = True) -> None:
        self.cfg, self.dark_line = cfg, dark_line

    def process(self, frame: Any) -> Perception:
        return Perception(line=detect_line(frame, self.dark_line))