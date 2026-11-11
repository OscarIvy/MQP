from __future__ import annotations

from ..types import UNDERWATER_STATES, Fault, State

_LINE_STATES = frozenset({State.SUBMERGED_FOLLOW, State.LINE_LOST_SEARCH})


def is_critical(fault: Fault, state: State) -> bool:
    """Does this fault force FAILSAFE in this state? Edit this table deliberately."""
    if fault is Fault.CAMERA_LOST:
        return state in _LINE_STATES           # only matters when we need the line
    if fault is Fault.LOOP_OVERRUN:
        return state in UNDERWATER_STATES      # TODO: require N consecutive overruns
    return True