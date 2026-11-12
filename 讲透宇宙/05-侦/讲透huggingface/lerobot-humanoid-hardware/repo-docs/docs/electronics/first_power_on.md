# First Power-On Procedure

## Phase 1: logic power only

1. Power controller logic rails only.
2. Set bench supply current limit to `2 A` for this first test phase (no motion capability expected).
3. Confirm expected idle current is around `1 A` maximum.
4. If current rises above `2 A`, stop immediately and re-check wiring before continuing.
5. Confirm communication with all controller nodes.
6. Verify watchdog/heartbeat behavior.

## Phase 2: actuator power with safety limits

1. Set low current/torque limits.
2. Enable one actuator at a time.
3. Verify sign/direction and encoder consistency.
4. Disable immediately if unexpected motion occurs.

## Phase 3: low-amplitude validation

1. Execute tiny motion commands around neutral position.
2. Confirm software limits are enforced.
3. Log observed offsets and runtime notes for later integration in `lerobot_humanoid_runtime`.

Stop criteria:
- unexpected heating, smell, noise, or oscillation
- communication instability under load
- any limit/safety mismatch
