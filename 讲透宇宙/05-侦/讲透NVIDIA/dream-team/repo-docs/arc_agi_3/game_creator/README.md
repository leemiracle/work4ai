# ARC-AGI-3 Game Creator

Generates standalone 64x64 arcade-game artifacts from seed words using LLM agents. Each game has 8 levels with evolving difficulty, governed by a DreamerV3-inspired state architecture (`h_t`, `z_t`, module constants).

> [!IMPORTANT]
> Generated `game_functions.py` bundles become standard offline environments
> via `build_generated_environments.py` + `arcengine_adapter.py`: the
> functional game is hosted inside the arcade engine and runs through the
> unchanged TeamSolver stack (ledgers, scoring, CLICK coordinates included).
> The repository ships 25 curated generated games under
> `environment_files_generated/`.

> [!WARNING]
> Generation, validation, and snapshot creation execute the generated
> `game_functions.py` as Python. Use generated or third-party artifacts only
> when you trust the code.

Games are controlled by sampled hyperparameters that ensure variety across two orthogonal axes: **genre** (how the player interacts) and **cognitive skill** (what mental challenge is tested).

## Quick Start

```bash
# Install dependencies
uv sync

# Generate 10 games with the default high-capacity model
uv run python -m runs.arc_agi_3.run_game_creator --llm gpt5.5 --num_games 10

# Generate with both LLMs in parallel
uv run python -m runs.arc_agi_3.run_game_creator --llm gpt5.5,flash --num_games 10

# Generate from 12 explicit seed words
uv run python -m runs.arc_agi_3.run_game_creator \
    --llm gpt5.5 \
    --words "crystal shadow river flame clock moss ember glass tide circuit echo frost"

# Compare a newly generated batch with an existing baseline
uv run python -m runs.arc_agi_3.run_game_creator --num_games 10 \
    --baseline_dir results/arc_agi_3/game_creator_baseline
```

`--words` must contain exactly 12 seed words.

---

## Hyperparameters

### Game Type (`game_type`)

The genre determines the structural pattern — how the player interacts with the world. Genres are grouped by action mode to ensure structural diversity.

#### Directional Games (player IS an entity on the grid)

| Genre | Nudge |
|-------|-------|
| `maze` | Navigate through connected spaces, finding routes and unlocking passages |
| `sokoban` | Reposition objects to satisfy spatial arrangements |
| `chase` | Move among other moving entities — pursuing, evading, or herding |
| `action` | React to a changing environment — growing trails, bouncing projectiles, or dodging hazards |
| `arena` | Place or trigger effects on the grid while navigating — explosions, traps, or area denial |

#### Click Games (player acts ON the grid from outside)

| Genre | Nudge |
|-------|-------|
| `logic` | Reveal, mark, or deduce hidden information through cell-by-cell interaction |
| `match` | Swap, group, or clear elements by creating alignments or connections |
| `territory` | Claim, flip, or flood regions through strategic placement |
| `sort` | Rearrange elements into a target ordering through pours, flips, or shifts |
| `tower` | Place or assign resources to influence autonomous processes |
| `path` | Connect, rotate, or extend segments to form complete routes |
| `pattern` | Observe, memorize, or reproduce sequences and configurations |
| `merge` | Combine identical or compatible elements to create higher-order ones |
| `cellular` | Set initial conditions or intervene in an evolving system governed by local rules |

#### Hybrid Games (directional + button or click)

| Genre | Nudge |
|-------|-------|
| `falling` | Elements drop or stack under gravity, the player controls placement or orientation |

### Cognitive Skill (`skill`)

The skill determines what mental challenge the game tests. This is **orthogonal to genre** — the same skill can appear in different genres, and the same genre can test different skills.

| Skill | Nudge |
|-------|-------|
| `pathfinding` | Find routes through connected spaces, considering obstacles and dead ends |
| `spatial_planning` | Think several moves ahead — actions have irreversible or cascading consequences |
| `constraint_satisfaction` | Fill in values or states that satisfy multiple simultaneous rules |
| `deduction` | Infer hidden information from indirect clues and partial observations |
| `pattern_matching` | Recognize, remember, or reproduce visual or sequential patterns |
| `sorting` | Rearrange elements into a target order through constrained operations |
| `resource_management` | Allocate limited resources across competing needs |
| `spatial_transformation` | Mentally rotate, reflect, or reshape configurations |
| `opponent_modeling` | Predict and counter the behavior of adversarial entities |
| `estimation` | Judge quantities, areas, distances, or probabilities without exact calculation |
| `timing` | Act at the right moment within cycles, patterns, or moving elements |
| `composition` | Combine or chain elements to produce emergent effects |

#### Skill x Genre Combinations

The skill nudges the LLM away from default genre behavior:

- `maze + deduction` — walls are invisible but clue numbers hint at nearby structure
- `territory + estimation` — choose which region to claim based on judging area sizes
- `chase + timing` — enemies follow patterns, player times movements between gaps
- `logic + constraint_satisfaction` — nonogram or lights-out style grid deduction
- `sort + spatial_planning` — wrong moves create dead ends in the sorting sequence
- `pattern + composition` — set up chain reactions by arranging matching elements
- `falling + spatial_transformation` — rotate falling pieces to fit target shapes
- `cellular + opponent_modeling` — compete against an evolving automaton

### Feature Tags (`feature_tags`)

Cross-cutting modifiers applied to any genre. Tags are introduced progressively across levels via `active_tags` in LEVELS.

**Observability**: `fog`, `hidden`, `memory`, `deduction`
**Time/Resource**: `timer`, `lives`, `undo`, `energy`
**Enemy/Agent**: `patrol`, `chase`, `random-enemy`, `spawn`
**Movement**: `ice`, `teleport`, `wrap`, `conveyor`, `gravity`, `one-way`, `push`
**Items**: `keys`, `powerup`, `collectible`, `switch`, `transform`, `destructible`
**Cascade**: `cascade`, `spread`, `explosion`

### Color Palette (`color_palette`)

15 named palettes with dark/neutral backgrounds and ranked entity colors. Palette size varies from 4 to 16 colors.

| Palette | BG | Colors | Size |
|---------|:--:|--------|:----:|
| minimal | white(0) | 3 entity colors | 4 |
| toxic | black(5) | 4 entity colors | 5 |
| arctic | white(0) | 4 entity colors | 5 |
| stone | dark-gray(3) | 5 entity colors | 6 |
| midnight | black(5) | 5 entity colors | 6 |
| ember | near-black(4) | 5 entity colors | 6 |
| ocean | near-black(4) | 6 entity colors | 7 |
| forest | dark-gray(3) | 6 entity colors | 7 |
| royal | near-black(4) | 6 entity colors | 7 |
| desert | dark-gray(3) | 7 entity colors | 8 |
| frost | light-gray(1) | 7 entity colors | 8 |
| candy | white(0) | 8 entity colors | 9 |
| sunset | near-black(4) | 9 entity colors | 10 |
| rainbow | black(5) | 11 entity colors | 12 |
| spectrum | white(0) | all 15 colors | 16 |

### Element Size (`element_size`)

| Size | Nudge |
|------|-------|
| `small` | Fine-grain elements (1-2px), dense grids, many elements |
| `medium` | Standard elements (3-4px), typical puzzle games |
| `large` | Chunky elements (5-8px), bold visuals, fewer objects |
| `varied` | Different sizes for different entity types |

### Evolution Tendencies

| Parameter | Options | Nudge |
|-----------|---------|-------|
| `scale` | growing / constant | Whether play areas tend to expand |
| `evolution` | progressive / all / scale_only | How new mechanics are introduced |
| `observability` | full / progressive / partial | Whether information hiding evolves |
| `stochastic` | none / progressive / always | Whether randomness is present |
| `pressure` | increasing / constant | Whether resource constraints tighten |

---

## State Architecture

### Module-Level Constants
Level layouts, entity definitions, color maps — defined once at file scope in `LEVELS` dict. Never reconstructed inside functions.

### `h_t` — Deterministic History State
Step-varying game state: entity positions, states, counters, inventory, undo stack. Updated by `transition(h_t, z_t, a_t)` (DreamerV3 sequence model). Small, flat, diffable.

### `z_t` — Stochastic/Derived State
Produced by `predict(h_t, seed)`. For deterministic games: `{}`. For stochastic games: sampled random elements using seed.

### Evolving Difficulty
Levels evolve along 5 dimensions via per-level parameters in LEVELS:
- Spatial scale (room/grid sizes)
- Mechanic count (via `active_tags`)
- Observability (via `fog_radius`)
- Stochasticity (via `stochastic` field)
- Resource pressure (via `budget`)

---

## File Structure

```
arc_agi_3/game_creator/
  config.yaml       # Agent config + game design hyperparameters
  skill.jinja       # Multi-phase skill template (Jinja2, rendered with config)
  hooks.py          # PhaseProgressMiddleware — tracks 5-phase progress
  stubs.py          # REPL stubs: print_grid, validate, test, run_game_sequence
  arcengine_adapter.py            # FunctionalArcGame — hosts a generated game in the arcade engine
  build_generated_environments.py # bundle -> SDK offline environment converter (--verify replays solutions)
  assets/           # generated-games showcase GIF
  words.py          # BIP39 seed word generation (2048-word mnemonic list)
  memory/           # Initial memory templates (copied per run)
  README.md         # This file
```

## Output Structure

```
results/arc_agi_3/game_creator/
  <timestamp>_<llm>_<word1>_<word2>_<hash>/
    memory/
      game_design.md       # Game design document
      game_functions.py    # Standalone generated game functions
      progress.md          # Phase completion tracking
    snapshots/
      level_0_start.png    # 3 snapshots per level
      level_0_mid.png
      level_0_end.png
      ...
    agent_logs/
      events.jsonl         # Agent activity log
    result.json            # Run metadata, hyperparams, stats
  summary.json             # Aggregate results
```

## Quality Metrics

Reported automatically by `run_game_creator.py` after generation:

- **Structure**: Module LEVELS, no _get_level_data(), all 7 required functions (including `solve_level`), runtime validation
- **Win conditions**: Relational (LEVELS-based) vs direct (coordinate-based)
- **Genre diversity**: Distribution across 15 genres
- **Skill diversity**: Distribution across 12 cognitive skills
- **Evolution**: active_tags, fog_radius, stochastic fields per level
- **Progression consistency**: later feature tags should deepen the main skill, not trivialize it into a one-trigger solve pattern
- **Visual variety**: Background colors, palette diversity, element sizes
- **Stochasticity balance**: Deterministic vs progressive vs always
- **Snapshots**: PNG coverage (3 per level x 8 levels = 24 per game)
