from drone.config import Config
from drone.fsm.machine import Machine
from drone.safety.supervisor import evaluate
from drone.types import ControlMode, Fault, LineObservation, Snapshot, State

CFG = Config()
GOOD_LINE = LineObservation(0.1, 0.0, 0.9)


def snap(t=0.0, **kw):
    base = dict(
        t=t, fc_heartbeat_age=0.05, imu_age=0.01, gyro=(0, 0, 0), accel=(0, 0, 9.8),
        attitude=(0, 0, 0), depth_m=0.0, depth_age=0.01, camera_age=0.03,
    )
    base.update(kw)
    return Snapshot(**base)


def step(m, **kw):
    s = snap(**kw)
    return m.step(s, evaluate(s, CFG))


def machine_in(state, t=0.0):
    m = Machine(CFG)
    m._enter(state, t)
    return m


def test_preflight_waits_for_arm_request():
    m = Machine(CFG)
    step(m, t=0.0)
    assert m.state is State.PREFLIGHT
    step(m, t=0.1, arm_request=True)
    assert m.state is State.FLIGHT


def test_preflight_blocked_by_fault():
    m = Machine(CFG)
    step(m, t=0.0, arm_request=True, battery_v=5.0)
    assert m.state is State.PREFLIGHT


def test_water_entry_floods_ballast_then_follows():
    m = machine_in(State.FLIGHT)
    cmd = step(m, t=1.0, depth_m=0.2)
    assert m.state is State.TRANSITION_DOWN
    assert cmd.ballast == (CFG.ballast_dive, CFG.ballast_dive)
    step(m, t=5.0, depth_m=CFG.target_depth_m)
    assert m.state is State.SUBMERGED_FOLLOW


def test_line_lost_then_search_then_ascend():
    m = machine_in(State.SUBMERGED_FOLLOW, t=0.0)
    step(m, t=0.5, depth_m=1.0, line=GOOD_LINE)
    step(m, t=0.5 + CFG.line_lost_s + 0.1, depth_m=1.0)
    assert m.state is State.LINE_LOST_SEARCH
    step(m, t=10.0, depth_m=1.0, line=GOOD_LINE)
    assert m.state is State.SUBMERGED_FOLLOW
    step(m, t=11.0 + CFG.line_lost_s, depth_m=1.0)
    t_search = m.entered_t
    step(m, t=t_search + CFG.search_timeout_s + 0.1, depth_m=1.0)
    assert m.state is State.TRANSITION_UP


def test_pool_edge_triggers_ascent_and_recovery():
    m = machine_in(State.SUBMERGED_FOLLOW)
    cmd = step(m, t=1.0, depth_m=1.0, line=GOOD_LINE, edge_detected=True)
    assert m.state is State.TRANSITION_UP
    assert cmd.ballast == (CFG.ballast_purged, CFG.ballast_purged)
    step(m, t=2.0, depth_m=0.01)
    assert m.state is State.RECOVERY


def test_link_loss_underwater_purges_and_stops_motors():
    m = machine_in(State.SUBMERGED_FOLLOW)
    cmd = step(m, t=1.0, depth_m=1.0, fc_heartbeat_age=5.0)
    assert m.state is State.FAILSAFE
    assert cmd.mode is ControlMode.MOTORS_OFF
    assert cmd.ballast == (CFG.ballast_purged, CFG.ballast_purged)


def test_link_loss_in_air_hands_to_fc_land():
    m = machine_in(State.FLIGHT)
    cmd = step(m, t=1.0, fc_heartbeat_age=5.0)
    assert m.state is State.FAILSAFE
    assert cmd.mode is ControlMode.FC_LAND


def test_camera_loss_only_critical_when_following_line():
    m = machine_in(State.FLIGHT)
    step(m, t=1.0, camera_age=5.0)
    assert m.state is State.FLIGHT
    m = machine_in(State.SUBMERGED_FOLLOW)
    step(m, t=1.0, depth_m=1.0, camera_age=5.0)
    assert m.state is State.FAILSAFE


def test_failsafe_latches_until_reset_with_no_faults():
    m = machine_in(State.SUBMERGED_FOLLOW)
    step(m, t=1.0, depth_m=1.0, fc_heartbeat_age=5.0)
    step(m, t=2.0, depth_m=1.0)  # fault cleared, no reset
    assert m.state is State.FAILSAFE
    step(m, t=3.0, reset_request=True)
    assert m.state is State.PREFLIGHT


def test_ascent_timeout_trips_failsafe():
    m = machine_in(State.TRANSITION_UP, t=0.0)
    step(m, t=CFG.ascent_timeout_s + 1, depth_m=1.0)
    assert m.state is State.FAILSAFE
    assert Fault.ASCENT_TIMEOUT in m.faults


def test_full_sim_mission_reaches_recovery():
    from drone.clock import VirtualClock
    from drone.hal.sim import SimVehicle
    from drone.main import run

    m = run(SimVehicle(CFG), CFG, VirtualClock(), duration=60.0)
    assert m.state is State.RECOVERY