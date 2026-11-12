# Wiring Check Procedure

Run this before first power-on.

## 1. Visual and continuity checks

- Confirm every connector orientation.
- Match each physical connector against `hardware/electronics/connectors.md` and `hardware/electronics/connectors_photos/`.
- Confirm no exposed conductor can short to frame.
- Continuity-check power and ground path end-to-end.
- Verify there is no short between main power and ground.
- Apply the leg cabling legend and diagrams from `hardware/electronics/cabling/README.md` (red = power, green = CAN, blue = CAN + power).
- Use the same leg cabling pattern on both left and right legs.
- Shin sub-cable, thigh sub-cable, and hip pass-through sub-cable are all shown there.

## 2. Signal checks

- Confirm bus lines are not swapped.
- Confirm encoder and sensor pin polarity.
- Confirm shield/ground policy is consistent.

## 3. Pre-power checklist

- Bench supply current limit set to `2 A` for first logic-only bring-up.
- Emergency power cutoff reachable.
- Motor power path still disconnected for logic-only test.
