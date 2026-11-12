# Electronics

Electronics documentation for the biped platform.

Core artifacts:
- full wiring diagram image (`hardware/electronics/wiring_diagram.png`)
- connector and pin mapping (`hardware/electronics/connectors.md`)
- connector photo catalog (`hardware/electronics/connectors_photos/`)
- leg sub-cable diagrams with embedded images (`hardware/electronics/cabling/README.md`)
- power distribution notes
- controller and actuator bus topology

Leg sub-cable set (same cabling for left and right leg):
- legend, shin, thigh, and hip pass-through diagrams are embedded in `hardware/electronics/cabling/README.md`.

Motor pre-assembly commissioning:
- detailed workflow: `docs/electronics/motor_commissioning.md`
- tool: `hardware/config/commission_motor.py`
- recommended entrypoint: `wizard` command
- covers protocol detection, MIT switch, model-based ID assignment, and motion check

Implementation note:
- this script embeds only the CAN functions it uses; it does not import `robstride_toolkit`.

Bring-up runbooks:
- `docs/electronics/check_wiring.md`
- `docs/electronics/first_power_on.md`
