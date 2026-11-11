"""ArduPilot over MAVLink via pymavlink. UNTESTED ON HARDWARE: bench-test with props off.

Wiring: Pixhawk TELEM2 <-> Pi UART (/dev/serial0 or similar). Set on the Pixhawk
SERIAL2_PROTOCOL=2 (MAVLink2) and SERIAL2_BAUD=921 (or match cfg.fc_baud).
"""
from __future__ import annotations

import math
import time

from ..types import ControlMode
from .base import FCState, FlightController

_MODE_NAMES = {ControlMode.DEPTH_LINE: "GUIDED_NOGPS", ControlMode.FC_LAND: "LAND"}


def euler_to_quat(roll: float, pitch: float, yaw: float) -> list[float]:
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return [cr * cp * cy + sr * sp * sy, sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy, cr * cp * sy - sr * sp * cy]


class ArduPilotFC(FlightController):
    def __init__(self, device: str, baud: int) -> None:
        self.device, self.baud = device, baud
        self._m = None
        self._mav = None
        self._t_hb = self._t_imu = 0.0
        self._gyro = (0.0, 0.0, 0.0)
        self._accel = (0.0, 0.0, 0.0)
        self._att = (0.0, 0.0, 0.0)
        self._batt_v = 0.0

    def connect(self) -> None:
        from pymavlink import mavutil

        self._mav = mavutil
        self._m = mavutil.mavlink_connection(self.device, baud=self.baud)
        self._m.wait_heartbeat(timeout=10)
        ml = mavutil.mavlink
        for msg_id, hz in ((ml.MAVLINK_MSG_ID_ATTITUDE, 50), (ml.MAVLINK_MSG_ID_SCALED_IMU, 50),
                           (ml.MAVLINK_MSG_ID_SYS_STATUS, 2)):
            self._cmd(ml.MAV_CMD_SET_MESSAGE_INTERVAL, msg_id, 1e6 / hz)
        self._t_hb = time.monotonic()

    def _cmd(self, command: int, *params: float) -> None:
        p = list(params) + [0.0] * (7 - len(params))
        self._m.mav.command_long_send(self._m.target_system, self._m.target_component, command, 0, *p)

    def poll(self) -> FCState:
        now = time.monotonic()
        while True:
            msg = self._m.recv_match(blocking=False)
            if msg is None:
                break
            kind = msg.get_type()
            if kind == "HEARTBEAT":
                self._t_hb = now
            elif kind == "ATTITUDE":
                self._att = (msg.roll, msg.pitch, msg.yaw)
            elif kind == "SCALED_IMU":  # mG and mrad/s
                self._accel = tuple(v * 9.80665e-3 for v in (msg.xacc, msg.yacc, msg.zacc))
                self._gyro = tuple(v * 1e-3 for v in (msg.xgyro, msg.ygyro, msg.zgyro))
                self._t_imu = now
            elif kind == "SYS_STATUS":
                self._batt_v = msg.voltage_battery / 1000.0
        return FCState(now - self._t_hb, now - self._t_imu, self._gyro, self._accel, self._att, self._batt_v)

    def set_control_mode(self, mode: ControlMode) -> None:
        if mode is ControlMode.MOTORS_OFF:
            # force-disarm (magic param2 = 21196); TODO decide if this is what you want underwater
            self._cmd(self._mav.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 21196)
        elif mode in _MODE_NAMES:
            self._m.set_mode(self._m.mode_mapping()[_MODE_NAMES[mode]])
        # PILOT: do nothing; the pilot's RC mode switch is in charge

    def send_setpoint(self, roll: float, pitch: float, yaw_rate: float, thrust: float) -> None:
        # type_mask 3: ignore roll/pitch rates; use attitude quaternion + yaw rate + thrust.
        # Yaw angle is held at the current yaw while yaw_rate steers.
        q = euler_to_quat(roll, pitch, self._att[2])
        self._m.mav.set_attitude_target_send(0, self._m.target_system, self._m.target_component,
                                             3, q, 0.0, 0.0, yaw_rate, thrust)

    def close(self) -> None:
        if self._m is not None:
            self._m.close()