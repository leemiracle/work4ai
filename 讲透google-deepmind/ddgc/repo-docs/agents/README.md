# RL Agents for JaxMGRL Multi-Goal Environments

This directory contains five RL agents for multi-goal, non-goal-conditioned,
continuing environments built on [Brax](https://github.com/google/brax). All
agents use a shared `--total_env_steps` budget for fair comparison.

## Environments

| Environment | Obs Dim | Action Dim | Steps Budget |
|---|---|---|---|
| `ant` | 27 | 8 | 5M |
| `reacher` | 6 | 2 | 1M |
| `pusher` | 20 | 7 | 2M |
| `half_cheetah` | 17 | 6 | 5M |

Rewards are sparse: **+1** when the agent is within a goal sphere, **0**
otherwise. Goals are not provided in the observation.

## Agents

### SAC — `agents/sac/`

Standard Soft Actor-Critic with automatic entropy tuning. Gaussian policy,
double critic, target network soft updates.

### SAC+PC — `agents/sac_pc/`

SAC augmented with SimHash pseudo-count intrinsic reward: `r_aug = r_env + β /
sqrt(N(s'))`.

### SMM — `agents/smm/`

State Marginal Matching via fictitious play. Trains a VAE density model `q(s)`
and uses intrinsic reward `r = -log q(s)`. Repeats for `num_iterations` rounds;
final policy is a uniform mixture.

### DDGC — `agents/ddgc/`

1.  **Exploration** (`exploration_fraction` of budget): RND-driven random
    exploration to collect goal-reaching trajectories into a goal buffer.
2.  **Policy mixture** (remainder of budget): Iteratively builds a policy
    mixture using incremental state visitation estimates and Fitted Actor-Critic
    offline RL. Mixture weights decay as `2/(k+1)`.

### GFlowNets — `agents/gflownet/`

Trajectory balance objective `L_TB = (log Z + log P_F(τ) - log R(τ))²` combined
with critic Q-value maximization. Learned scalar `log Z` trained jointly with
the actor.

## Shared Infrastructure (`agents/common/`)

| Module | Contents |
|---|---|
| `networks.py` | MLP, Actor, DoubleCritic, VAE, RNDNetwork, GFlowNetActor |
| `replay_buffer.py` | Circular `ReplayBuffer` with `state_dict` / `load_state_dict` for checkpointing |
| `train_state.py` | `TrainState` with target params, `soft_update` |
| `rollout.py` | `collect_rollout`, `eval_policy` (via `jax.lax.scan`) |
| `checkpointing.py` | `save_full_checkpoint` / `load_full_checkpoint` using pickle (params + optimizer states + replay buffer + agent-specific state) |
| `logging_utils.py` | `MetricsLogger` for logging training metrics |
| `eval_metrics.py` | `compute_eval_metrics`, `run_final_eval`, `write_datatable_row` — final evaluation and leaderboard logging |

## Checkpointing

All agents save and load their **complete training state** (model parameters,
optimizer states, replay buffer, and agent-specific data) to
`{checkpoint_dir}/checkpoint.npz`. Training resumes seamlessly from the last
saved checkpoint when `--checkpoint_dir` is set.

## Evaluation Metrics

At the end of training, every agent runs a final evaluation
(`--final_eval_episodes`, default 1000) with both deterministic and stochastic
policies.

Three metrics are computed per policy variant (`_det` / `_stoch`):

| Metric | Description |
|---|---|
| `return_mean` | Mean discounted return across episodes |
| `return_std` | Std of discounted return across episodes |
| `partial_entropy_mean` | Entropy of the discounted goal-visitation distribution |
| `partial_gini_mean` | Negative sum of squared goal-visitation probabilities (Modified Partial Gini) |

## Launch Commands

### SAC

```bash
bash agents/sac/run.sh --env_name=ant --total_env_steps=5000000 --seed=0
```

### SAC + Pseudo Counts

```bash
bash agents/sac_pc/run.sh --env_name=ant --total_env_steps=5000000 --seed=0
```

### SMM

```bash
bash agents/smm/run.sh --env_name=ant --total_env_steps=5000000 --seed=0
```

### DDGC

```bash
bash agents/ddgc/run.sh --env_name=ant --total_env_steps=5000000 --seed=0
```

### GFlowNets

```bash
bash agents/gflownet/run.sh --env_name=ant --total_env_steps=5000000 --seed=0
```
