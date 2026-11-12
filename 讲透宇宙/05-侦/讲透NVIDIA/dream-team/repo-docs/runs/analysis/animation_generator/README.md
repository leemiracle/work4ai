# Animation generator

This renderer turns a completed ARC-AGI-3 solver run into a GIF or APNG. It can
show the real and simulated grids, action events, sub-goal progress, hypotheses,
role suggestions, reasoning, clickable cells, and world-model objects.

The renderer reads a completed run directory supplied at invocation. Create a
local YAML file such as:

```yaml
name: my_animation
run_path: results/arc_agi_3/my_run
team: my_team
anchor_step: 10
action_source:
  mode: sequence
  depth: 3
  sequence: [UP, RIGHT, USE]
wm:
  state_source: predicted
output:
  format: gif
  dir: animations
  loop: 0
```

Render it from the repository root:

```bash
python -m runs.analysis.animation_generator.generate --config my_animation.yaml
```

`--format gif|apng` and `--out-dir PATH` override the corresponding output
settings. Generated media and `.meta.json` sidecars are local artifacts and
should be reviewed before publication because they reflect the selected run.
The renderer executes world-model or harness Python from that run; use only a
trusted run directory.

The three GIFs under `assets/` are curated paper examples; they are inputs to
the root README, not fixtures required by the renderer.
