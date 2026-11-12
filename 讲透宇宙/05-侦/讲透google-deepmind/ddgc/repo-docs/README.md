# DDGC: Dense and Diverse Goal Coverage

Code for training and evaluating RL agents on multi-goal, non-goal-conditioned,
continuing environments built on [Brax](https://github.com/google/brax).

## Environments

Four environments with sparse binary rewards (+1 at goal, 0 otherwise) and no
goal information in observations:

| Environment | Obs Dim | Action Dim | Goals | Threshold |
|---|---|---|---|---|
| `ant` | 27 | 8 | 10 | 0.2 m |
| `reacher` | 6 | 2 | 10 | 0.01 m |
| `pusher` | 20 | 7 | 5 | 0.03 m |
| `half_cheetah` | 17 | 6 | 6 | 0.15 m |

## Agents

| Agent | Directory | Description |
|---|---|---|
| **SAC** | `agents/sac/` | Soft Actor-Critic with automatic entropy tuning |
| **SAC+PC** | `agents/sac_pc/` | SAC + SimHash pseudo-count intrinsic reward |
| **SMM** | `agents/smm/` | State Marginal Matching via fictitious play |
| **DDGC** | `agents/ddgc/` | RND exploration → iterative policy mixture via Fitted AC |
| **GFlowNet** | `agents/gflownet/` | Trajectory balance + critic Q-value maximization |

## Installation

```bash
pip install jax jaxlib brax flax optax orbax-checkpoint absl-py numpy
```

## Usage

Each agent has a `run.sh` script. Example:

```bash
# Train DDGC agent on Ant environment
bash agents/ddgc/run.sh --env_name=ant --total_env_steps=5000000 --seed=0

# Train SAC agent on Reacher environment
bash agents/sac/run.sh --env_name=reacher --total_env_steps=1000000 --seed=0
```

All agents accept these common flags:

| Flag | Default | Description |
|---|---|---|
| `--env_name` | `ant` | Environment: ant, reacher, pusher, half_cheetah |
| `--seed` | `0` | Random seed |
| `--total_env_steps` | `5000000` | Total environment steps |
| `--num_envs` | `64` | Parallel environment count |
| `--episode_length` | `500` | Episode length |
| `--checkpoint_dir` | `''` | Directory for checkpoints |

## Citing this work

```
@article{ddgc2026,
      title={DDGC: Dense and Diverse Goal Coverage},
      author={Sagalpreet Singh and Rishi Saket and Aravindan Raghuveer},
      year={2026},
}
```

## License and disclaimer

Copyright 2026 Google LLC

All software is licensed under the Apache License, Version 2.0 (Apache 2.0);
you may not use this file except in compliance with the Apache 2.0 license.
You may obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.
