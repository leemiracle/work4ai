# DreamTeam for ARC-AGI-3

DreamTeam is a multi-agent solver for interactive ARC-AGI-3 environments. It
coordinates six specialized agents around a shared, executable world model:
an observer encodes the scene, a simulator models dynamics, two explorers
propose experiments and policies, a critic checks the evidence, and a team
leader selects the action to execute.

This repository accompanies the paper
[Workspace Optimization: How to Train Your Agent](https://arxiv.org/abs/2605.09650).
It provides the TeamSolver algorithm, its runtime dependencies, visualization
tools, and reproducible configuration for offline and competition runs.

## Examples

The renderer under `runs/analysis/animation_generator` produced these curated
examples. Click an image to open the full GIF.

| LS20 — long solve, level 1 | WA30 — long solve, level 1 |
|---|---|
| [![LS20 level 1 long-horizon solve](runs/analysis/animation_generator/assets/ls20_L1_long_0244.gif)](runs/analysis/animation_generator/assets/ls20_L1_long_0244.gif) | [![WA30 level 1 long-horizon solve](runs/analysis/animation_generator/assets/wa30_L1_long_0138.gif)](runs/analysis/animation_generator/assets/wa30_L1_long_0138.gif) |
| CD82 — policy flow, level 3 | VC33 — policy flow, level 2 |
| [![CD82 level 3 policy execution](runs/analysis/animation_generator/assets/cd82_L3_policy_0356.gif)](runs/analysis/animation_generator/assets/cd82_L3_policy_0356.gif) | [![VC33 level 2 policy execution](runs/analysis/animation_generator/assets/vc33_L2_policy_0017.gif)](runs/analysis/animation_generator/assets/vc33_L2_policy_0017.gif) |

## Components

- `arc_agi_3/arc_league/team_solver.py`: the TeamSolver algorithm.
- `arc_agi_3/base_solver.py` and `arc_agi_3/arc_league/`: the execution loop,
  world-model evaluation, prompts, middleware, and file-based team memory.
- `runs/arc_agi_3/run_team_solver.py`: the single-game entry point.
- `runs/arc_agi_3/run_multi_team_solver.py`: the parallel offline/competition
  entry point, with its integrated terminal dashboard.
- `arc_agi_3/tui_multi_game_viewer.py`: a standalone viewer for an existing
  multi-game results directory.
- `arc_agi_3/arc_league/viewer/`: the local FastAPI/React run viewer,
  playground, and analysis APIs.
- `arc_agi_3/game_creator/`: the standalone game-generation component used in
  the paper.
- `runs/analysis/animation_generator/`: the GIF/APNG renderer used for the
  examples above.
- `beam/`: the complete agent framework used by TeamSolver.

Team agents coordinate through files in a shared workspace.

## Requirements and installation

- Python 3.12
- Node.js and npm only if you want to build the HTTP viewer frontend
- An OpenAI-compatible LLM gateway for the configured model profiles
- The ARC-AGI-3 SDK data for offline runs, or an ARC API key for competition
  mode

Using `uv`:

```bash
uv sync
source .venv/bin/activate
```

Using `venv` and pip:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Copy the environment template and supply your gateway values:

```bash
cp .env.example .env
export LLM_BASE_URL=https://your-gateway.example/v1
export LLM_API_KEY=your-api-key
# Alternatively: export LLM_API_KEY_POOL=key-one,key-two
```

Competition mode also requires:

```bash
export ARC_API_KEY=your-arc-api-key
```

Do not commit `.env` or credentials.

## LLM profiles

Static model profiles live in
[`arc_agi_3/llm_configs.yaml`](arc_agi_3/llm_configs.yaml). The file contains
model, reasoning, streaming, and context-window settings only; endpoint and
credential values come from the environment.

Role selection stays in
[`runs/arc_agi_3/configs/offline_focused.yaml`](runs/arc_agi_3/configs/offline_focused.yaml)
using the existing concrete fields such as `team_leader_model`,
`observer_model`, and `critic_model`. To add a model, add one named profile to
`llm_configs.yaml`, then select that name in the run YAML. Model profiles are
defined only in the standalone LLM configuration file.

The packaged profiles use the `beam-gateway` protocol. To test the same
profiles against any configured gateway without starting a game:

```bash
python -m pytest -q -m live_llm tests/release/test_llm_gateway_live.py
```

That command makes live model requests. The default test command does not.

## Run TeamSolver

### One offline game

```bash
python -m runs.arc_agi_3.run_team_solver \
  runs/arc_agi_3/configs/offline_focused.yaml \
  --game_id R11L \
  --operation_mode offline \
  --results_dir results/arc_agi_3/team_solver
```

The focused YAML selects the paper model ensemble. Solver behavior defaults
live in `arc_agi_3/config.py`; the YAML is the thin run-selection layer.

### Multiple games

Run one game with the terminal dashboard:

```bash
python -m runs.arc_agi_3.run_multi_team_solver \
  --config runs/arc_agi_3/configs/offline_focused.yaml \
  --games R11L \
  --parallel 1 \
  --operation_mode offline
```

For an unattended run, add `--no_tui`. Closing the integrated TUI stops the
runner and its workers. Running only `--config` uses the YAML's full 14-game,
4-worker selection; it is a real experiment, not a lightweight smoke test.

Competition mode uses the same runner and requires `ARC_API_KEY`:

```bash
python -m runs.arc_agi_3.run_multi_team_solver \
  --config runs/arc_agi_3/configs/offline_focused.yaml \
  --games R11L \
  --parallel 1 \
  --operation_mode competition
```

To reopen the terminal dashboard for an existing multi-run directory:

```bash
python -m arc_agi_3.tui_multi_game_viewer \
  results/arc_agi_3/multi_team_solver/<run-directory> \
  --watch team_leader
```

## HTTP run viewer

Build the frontend once from a source checkout:

```bash
cd arc_agi_3/arc_league/viewer/frontend
npm ci
npm run build
cd ../../../..
```

Then start the server from the repository root:

```bash
python -m arc_agi_3.arc_league.viewer \
  --results-dir results/arc_agi_3 \
  --host 127.0.0.1 \
  --port 8420
```

Open `http://127.0.0.1:8420`; API documentation is available at `/docs`.
The viewer supports run discovery, live event tailing, team/agent inspection,
comparisons, annotations, analysis, and the local playground.

The viewer has no authentication. Keep it bound to localhost. Its playground
and animation paths can execute `world_model` or harness Python from a selected
run, and analysis can send run content to the configured LLM. Use only trusted
run directories.

## Game Creator

Generate one standalone game artifact:

```bash
python -m runs.arc_agi_3.run_game_creator \
  --llm gpt5.5 \
  --num_games 1 \
  --workers 1 \
  --output_dir results/arc_agi_3/game_creator
```

You can also provide exactly 12 seed words with `--words`. See
[`arc_agi_3/game_creator/README.md`](arc_agi_3/game_creator/README.md) for the
generation schema and options.

During generation, Game Creator artifacts are validated and snapshotted by the component's built-in validation harness.

### Generated games

The repository ships 25 curated Game-Creator-generated games as standard offline environments under `environment_files_generated/`, converted by `arc_agi_3/game_creator/build_generated_environments.py` (each game's functional `game_functions.py` is hosted inside the arcade engine by `arc_agi_3/game_creator/arcengine_adapter.py`). They run through the unchanged TeamSolver stack — same ledgers, scoring, and CLICK semantics as the downloaded games — and every game's exported solution replays to a WIN through the SDK (`--verify`).

[![25 generated games](arc_agi_3/game_creator/assets/generated_games_5x5.gif)](arc_agi_3/game_creator/assets/generated_games_5x5.gif)

Run the TeamSolver fleet on them:

```bash
ENVIRONMENTS_DIR=environment_files_generated \
  python -m runs.arc_agi_3.run_multi_team_solver \
  --config runs/arc_agi_3/configs/offline_generated.yaml
```

To rebuild the environments from a directory of game bundles (each containing `game_functions.py` and `solution.json`):

```bash
python -m arc_agi_3.game_creator.build_generated_environments \
  --games_root /path/to/game-bundles --verify
```

Generated `game_functions.py` is executed during validation, snapshot generation, and gameplay. Treat generated or third-party game code as trusted code only.

## Animation generator

Create a local YAML file pointing at a trusted completed run:

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

Render it with:

```bash
python -m runs.analysis.animation_generator.generate \
  --config my_animation.yaml
```

The renderer supports GIF and APNG output. It executes world-model code from
the selected run, so do not use an untrusted run directory.

## Tests

The default suite is offline and includes import boundaries, config/profile
contracts, runner/viewer smoke tests, runtime manifests, curated GIF hashes,
and byte-level fingerprints for all six agents' system prompts, opening and
steady user/context prompts, and middleware feedback.

```bash
python -m pytest -q
python -m compileall -q arc_agi_3 beam runs tests/release
```

Viewer frontend checks:

```bash
cd arc_agi_3/arc_league/viewer/frontend
npm ci
npm run build
npm audit --audit-level=high
```

## Contributions

This project is currently not accepting contributions.

## License

NVIDIA-authored portions of DreamTeam are licensed under the
[Apache License 2.0](LICENSE). Third-party portions retain their respective
licenses; see [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) and [NOTICE](NOTICE).

## Security

Do not report security vulnerabilities through public GitHub issues. Follow
the private reporting instructions in [SECURITY.md](SECURITY.md).

## Citation

Citation metadata is provided in [CITATION.cff](CITATION.cff). The associated
paper is [Workspace Optimization: How to Train Your Agent](https://arxiv.org/abs/2605.09650).
