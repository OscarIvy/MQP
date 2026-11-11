# Amphibious drone: onboard software

Raspberry Pi 5 + Pixhawk 2.4.8 (ArduPilot). In air the Pi records video; underwater it
runs the mission state machine (line following, depth/ballast, failsafes).

## Run

```bash
pip install -e ".[dev]"
pytest
python -m drone.main --sim          # whole stack against scripted simulated hardware
pip install -e ".[hw]"              # on the Pi
python -m drone.main --config config/default.yaml
```

## Layout

- `types.py`: Snapshot (all inputs), Command (all outputs), State, Fault
- `fsm/machine.py`: mission states and transitions (pure, no I/O); `fsm/policy.py`: which faults trip FAILSAFE where
- `safety/supervisor.py`: snapshot -> set of faults
- `hal/`: interfaces (`base.py`), ArduPilot MAVLink, camera, and stubs (`depth.py`, `ballast.py`) to implement; `sim.py` for laptop runs
- `perception/`: line detection (OpenCV) and video recorder
- `control/`: line-follow law and Command -> FC setpoint mapping (placeholders)
- `config.py` + `config/default.yaml`: every tunable (all placeholders)

## Not done yet

- I2C pressure sensor driver, ballast actuator driver (stubs raise NotImplementedError)
- Water-surface and pool-edge detection
- Real controller (replace `control/setpoints.py` with the Simulink-derived one)
- Telemetry logging, operator arm/reset input, ArduPilot parameter setup
- ArduPilot code is untested on hardware: bench-test with props off