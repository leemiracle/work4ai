# Multi-Goal Non-Goal-Conditioned Brax Environments

This package provides multi-goal, non-goal-conditioned versions of four standard
[Brax](https://github.com/google/brax) environments. They are designed for
multi-goal RL research where the agent must learn to reach any of several fixed
goals without being told which goal to pursue.

## Core Design Principles

### 1. Fixed Goal Set

Each environment has a fixed set of goals defined as module-level constants. The
goals are **identical across all instantiations** — they do not depend on any
random seed. Only the agent's starting state varies across episodes (controlled
by the `rng` passed to `reset()`).

```python
env1 = Ant(rng=jax.random.PRNGKey(0))
env2 = Ant(rng=jax.random.PRNGKey(42))
# env1._goals == env2._goals  (always True)
```

### 2. Binary (Non-Dense) Reward

The reward is `1.0` if the agent is within a threshold distance of the **nearest
goal**, and `0.0` otherwise. There is no dense shaping.

```python
dists = jax.vmap(lambda g: safe_norm(agent_pos - g))(self._goals)
reward = jp.where(jp.min(dists) < self._threshold, 1.0, 0.0)
```

### 3. Goal-Free Observation

The observation vector contains **no information about goal locations**. This
includes direct goal coordinates, vector differences between the agent and a
goal, or any other goal-encoding signal. The agent must learn to navigate to
goals purely from its own proprioceptive state.

### 4. Action Rescaling

Environments with bounded actuator ranges (Pusher) rescale actions from `[−1,
1]` to the actuator's `ctrl_range` inside `step()`:

```python
action = (action + 1) * (action_max - action_min) * 0.5 + action_min
```

This lets all agents output actions in a uniform `[−1, 1]` range regardless of
the underlying actuator limits.

### 5. Goal-Sphere Rendering

The `render()` method returns an HTML string (via `brax.io.html.render`) using a
render-only system (`_render_sys`) that has **green semi-transparent spheres**
appended at each goal's 3D position. The spheres are added to the Brax system's
geom arrays by `utils.sys_with_goal_spheres` at construction time, so no
per-frame projection is needed.

---

## Environment Details

### Reacher

**Base:** `brax.envs.reacher.Reacher`
**Backend:** `generalized`
**Goal:** 2D (x, y) fingertip target position
**Number of goals:** 10
**Threshold:** 0.01 m

#### Original → Multi-Goal Transformation

| Aspect | Original Brax | This Implementation |
|---|---|---|
| Goal | Single random target per episode | 10 fixed targets |
| Reward | `−‖fingertip − target‖ − ‖action‖²` | `1` if `‖fingertip_xy − nearest_goal‖ < 0.01` |
| Obs (6-dim) | `[cos θ, sin θ, target_x, target_y, tip_vel, tip_to_target]` | `[cos θ₁, cos θ₂, sin θ₁, sin θ₂, tip_vel_x, tip_vel_y]` |
| Reset | Randomizes arm joints + target position | Randomizes arm joints only; target slot in `q` set to `[0, 0]` |

**Removed from obs:**

-   `q[2:]` — the target (x, y) position encoded directly in joint space
-   `tip_to_target` — the 3D vector from fingertip to target (encodes goal
    location)

The tip velocity retained in the observation is the 2D (x, y) component only.

---

### Ant

**Base:** `brax.envs.ant.Ant`
**Backend:** `spring`
**Goal:** 2D (x, y) torso position on the ground plane
**Number of goals:** 10
**Threshold:** 0.2 m

#### Original → Multi-Goal Transformation

| Aspect | Original Brax | This Implementation |
|---|---|---|
| Goal | Run in +x direction indefinitely | 10 fixed 2D positions |
| Reward | `forward_vel + healthy − ctrl_cost − contact_cost` | `1` if `‖torso_xy − nearest_goal‖ < 0.2` |
| Obs (27-dim) | Joint angles + velocities | Unchanged (27-dim; no goal info was present) |
| Reset | Standard noise around initial pose | Unchanged |

The original Ant observation contains no goal information, so the observation
vector is unchanged. Only the reward function is replaced. The health
termination condition (torso z-height out of range) is preserved.

---

### HalfCheetah

**Base:** `brax.envs.half_cheetah.Halfcheetah`
**Backend:** `generalized`
**Env name string:** `half_cheetah`
**Goal:** 1D x-position of the torso
**Number of goals:** 6
**Threshold:** 0.15 m

#### Original → Multi-Goal Transformation

| Aspect | Original Brax | This Implementation |
|---|---|---|
| Goal | Run in +x direction as fast as possible | 6 fixed x-positions: 1, 3, 5, 7, 9, 10 |
| Reward | `forward_vel − ctrl_cost` | `1` if `|torso_x − nearest_goal_x| < 0.15` |
| Obs (17-dim) | Joint positions (excl. x) + velocities | Unchanged (17-dim; no goal info was present) |
| Reset | Standard noise around initial pose | Unchanged |

HalfCheetah is a planar (2D) environment. Goals are defined as 1D x-positions
since the cheetah can only move along the x-axis meaningfully. The observation
already excludes the absolute x-position
(`exclude_current_positions_from_observation=True`), so no changes to the
observation are needed.

---

### Pusher

**Base:** `brax.envs.pusher.Pusher`
**Backend:** `generalized`
**Goal:** 2D (x, y) position for the pushed object
**Number of goals:** 5
**Threshold:** 0.03 m

#### Original → Multi-Goal Transformation

| Aspect | Original Brax | This Implementation |
|---|---|---|
| Goal | Push object to fixed position `(0.45, −0.05)` | 5 fixed goal positions near the reachable region |
| Reward | `−‖object − goal‖ − 0.1‖action‖² − 0.5‖fingertip − object‖` | `1` if `‖object_xy − nearest_goal‖ < 0.03` |
| Obs (20-dim) | `[q[:7], qd[:7], fingertip_pos, object_pos, goal_pos]` | `[q[:7], qd[:7], fingertip_pos, object_pos]` |
| Reset | Randomizes object position; goal fixed in model | Randomizes object position; goal slot unused for reward |

**Removed from obs:**

-   `x_i.pos[goal_idx]` — the 3D goal position (3 values), which directly
    encodes which goal the agent should target

Actions are rescaled from `[−1, 1]` to the actuator's `ctrl_range` inside
`step()`.

---

---

## Rendering

All environments override `render()` to return an HTML string produced by
`brax.io.html.render`. Rendering uses a dedicated `_render_sys` object
constructed at `__init__` time by `utils.sys_with_goal_spheres`. This function
augments the Brax system's geom arrays with additional sphere geoms (green,
semi-transparent, `rgba = [0, 1, 0, 0.8]`, `contype/conaffinity = 0`) placed at
each goal's 3D position, so they appear in the viewer without affecting physics.

```python
self._render_sys = utils.sys_with_goal_spheres(
    self.sys, 'envs/assets/ant.xml', goal_positions, radius=_THRESHOLD
)
```

The `goal_positions` array has shape `(n, 3)` — the first two columns are the 2D
goal coordinates and the third column is the z-height used for display (e.g.
`0.1` for ground-level goals).

---

## Usage

Environments are created via `env_utils.create_env`, which is the API used by
all agents:

```python
import jax
from jaxmgrl import utils as env_utils

rng = jax.random.PRNGKey(0)
env = env_utils.create_env('ant', rng)

state = env.reset(rng)
print(state.obs.shape)   # (27,) - no goal info
print(state.reward)      # 0.0 or 1.0

action = jax.random.uniform(rng, (env.action_size,), minval=-1, maxval=1)
state = env.step(state, action)

html_str = env.render([state])  # HTML string with green goal spheres
```

Valid `env_name` strings: `ant`, `reacher`, `pusher`, `half_cheetah`.
