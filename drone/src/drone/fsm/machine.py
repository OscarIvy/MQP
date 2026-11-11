"""Deterministic mission state machine. No I/O: feed it Snapshots, get Commands."""
from __future__ import annotations

import logging
from typing import Iterable, Optional

from ..config import Config
from ..control.line_follow import follow
from ..types import UNDERWATER_STATES, Command, ControlMode, Fault, Snapshot, State
from .policy import is_critical

log = logging.getLogger(__name__)
