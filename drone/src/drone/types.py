"""Shared data types. No I/O and no third-party imports here."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

Vec3 = tuple[float, float, float]


class State(Enum):
    PREFLIGHT = auto()
    FLIGHT = auto()            # in air: pilot/ArduPilot flies, Pi records video
    SURFACE_APPROACH = auto()  # camera sees water surface
    TRANSITION_DOWN = auto()   # flood ballast, descend to working depth
    SUBMERGED_FOLLOW = auto()  # autonomous line following
    LINE_LOST_SEARCH = auto()
    TRANSITION_UP = auto()     # purge ballast, climb to surface
    RECOVERY = auto()
    FAILSAFE = auto()          # latched until operator reset


UNDERWATER_STATES = frozenset(
    {State.TRANSITION_DOWN, State.SUBMERGED_FOLLOW, State.LINE_LOST_SEARCH, State.TRANSITION_UP}
)


class Fault(Enum):
    FC_LINK_LOST = auto()
    IMU_STALE = auto()
    DEPTH_INVALID = auto()
    DEPTH_LIMIT = auto()
    BALLAST_STALL = auto()
    CAMERA_LOST = auto()
    LOW_BATTERY = auto()
    OVERTEMP = auto()
    LOOP_OVERRUN = auto()
    ASCENT_TIMEOUT = auto()


class ControlMode(Enum):
    PILOT = auto()       # Pi observes only; ArduPilot/pilot in control
    DEPTH_LINE = auto()  # Pi sends attitude/thrust setpoints
    MOTORS_OFF = auto()
    FC_LAND = auto()     # hand over to ArduPilot LAND


@dataclass(frozen=True)
class LineObservation:
    lateral_offset: float  # normalized [-1, 1], + = line right of image center
    heading_error: float   # rad, + = line tilts clockwise (to the right going forward)
    confidence: float      # [0, 1]


@dataclass(frozen=True)
class Perception:
    line: Optional[LineObservation] = None
    surface_detected: bool = False
    edge_detected: bool = False  # pool edge -> go to surface


@dataclass(frozen=True)
class Snapshot:
    """Everything the state machine is allowed to know at one instant."""
    t: float
    fc_heartbeat_age: float
    imu_age: float
    gyro: Vec3
    accel: Vec3
    attitude: Vec3                 # roll, pitch, yaw (rad)
    depth_m: Optional[float]
    depth_age: float
    camera_age: float
    line: Optional[LineObservation] = None
    surface_detected: bool = False
    edge_detected: bool = False
    ballast_pos: tuple[float, float] = (0.0, 0.0)  # fore, aft: 0 = purged, 1 = full
    ballast_stalled: bool = False
    battery_v: float = 16.0
    cpu_temp_c: float = 50.0
    loop_dt: float = 0.0
    arm_request: bool = False
    takeoff_request: bool = False
    reset_request: bool = False


@dataclass(frozen=True)
class Command:
    mode: ControlMode
    ballast: tuple[float, float]       # fore, aft target fill fraction
    forward: float = 0.0               # [-1, 1]
    yaw_rate: float = 0.0              # rad/s
    depth_target: Optional[float] = None
    record_video: bool = True