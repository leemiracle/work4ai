# Safety

## Minimum safety requirements

- Keep a physical emergency power cutoff accessible.
- Use current-limited bench supply for first electronics checks.
- Verify motor direction and limits at low torque/current first.
- Keep clear of moving joints during bring-up.
- Never run unattended during first powered motion passes.

## Power bring-up rules

1. Validate wiring continuity before connecting battery/high-current source.
2. Bring up logic power before actuator power.
3. Confirm communication heartbeat and watchdog behavior.
4. Enable actuators only after limit/zero checks pass.

## Mechanical checks before motion

- Fastener torque check completed.
- Structural parts inspected for cracks/print defects.
- Joint free motion verified by hand (power off).
- Cable strain relief and routing confirmed.
