# Biped Platform STL

Store STL exports split by side and mechanical group.

Main structure:
- `left_leg/<group>/...`
- `right_leg/<group>/...`
- `torso/...`

Per-leg groups currently used:
- `ankle`
- `ankle_mechanism`
- `foot`
- `hipx`
- `hipz`
- `knee_mechanism`
- `shin`
- `thigh`

Filename rule:
- Use lowercase snake_case.
- Do not use parentheses in filenames.
- Keep explicit instance indices when the same part appears multiple times.

Example path:
`right_leg/ankle_mechanism/bearing_spacer14_5_7_3.stl`
