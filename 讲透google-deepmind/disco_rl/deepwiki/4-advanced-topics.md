<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/disco_rl · page 4 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [colabs/eval.ipynb](colabs/eval.ipynb)
- [colabs/meta_train.ipynb](colabs/meta_train.ipynb)

</details>



This page covers advanced implementation details and optimization techniques in DiscoRL. It provides an overview of JAX parallelization strategies, meta-gradient computation, replay buffers, and performance optimizations that enable efficient training and meta-training of RL agents.

For detailed information on parallelization patterns, see [JAX Parallelization](#4.1). For documentation on input transformation systems used by meta-networks, see [Input Transformations](#4.2).

## JAX Parallelization Strategy

DiscoRL leverages JAX's parallelization primitives to achieve efficient distributed training across multiple devices (TPUs/GPUs). The system uses three key JAX transformations:

| Transformation | Purpose | Usage in DiscoRL |
|---------------|---------|------------------|
| `jax.pmap` | Data parallelism across devices | Distributes environment batches and synchronizes gradients |
| `jax.vmap` | Vectorization within device | Batches jittable environment operations |
| `jax.jit` | Just-in-time compilation | Compiles training loops for performance |

### Device Replication Pattern

```mermaid
graph TB
    subgraph "Host Python"
        PARAMS["update_rule_params<br/>(single copy)"]
        LEARNER["learner_state<br/>(single copy)"]
        ACTOR["actor_state<br/>(single copy)"]
    end
    
    subgraph "Device Operations"
        REPLICATE["jax.device_put_replicated()"]
        
        subgraph "Device 0"
            D0_PARAMS["Replicated Params"]
            D0_STATE["Replicated States"]
            D0_ENV["Sharded Envs<br/>(batch slice)"]
        end
        
        subgraph "Device 1"
            D1_PARAMS["Replicated Params"]
            D1_STATE["Replicated States"]
            D1_ENV["Sharded Envs<br/>(batch slice)"]
        end
        
        subgraph "Device N"
            DN_PARAMS["Replicated Params"]
            DN_STATE["Replicated States"]
            DN_ENV["Sharded Envs<br/>(batch slice)"]
        end
    end
    
    subgraph "Synchronization"
        PMEAN["jax.lax.pmean()<br/>axis_name='i'"]
        GATHER["utils.gather_from_devices()"]
    end
    
    PARAMS --> REPLICATE
    LEARNER --> REPLICATE
    ACTOR --> REPLICATE
    
    REPLICATE --> D0_PARAMS
    REPLICATE --> D0_STATE
    REPLICATE --> D1_PARAMS
    REPLICATE --> D1_STATE
    REPLICATE --> DN_PARAMS
    REPLICATE --> DN_STATE
    
    D0_STATE --> D0_ENV
    D1_STATE --> D1_ENV
    DN_STATE --> DN_ENV
    
    D0_ENV --> PMEAN
    D1_ENV --> PMEAN
    DN_ENV --> PMEAN
    
    PMEAN --> GATHER
```

**Sources:** [colabs/eval.ipynb:316-319](), [colabs/meta_train.ipynb:609-614]()

The parallelization strategy involves:

1. **Parameter Replication**: Model parameters, optimizer states, and update rule parameters are replicated to all devices using `jax.device_put_replicated()` [colabs/eval.ipynb:316-319]()
2. **Environment Sharding**: Environment states are distributed across devices with each device handling a subset of the total batch [colabs/eval.ipynb:285-287]()
3. **Gradient Synchronization**: Gradients are averaged across devices using `jax.lax.pmean()` with a shared `axis_name` [colabs/meta_train.ipynb:443-446]()
4. **Result Gathering**: Metrics and outputs are collected from all devices using `utils.gather_from_devices()` [colabs/eval.ipynb:391-395]()

### Parallelized Function Setup

```python
# Parallelizing actor and learner steps
actor_step_fn = jax.pmap(agent.actor_step, axis_name, devices=devices)
learner_step_fn = jax.pmap(
    agent.learner_step,
    axis_name=axis_name,
    devices=devices,
    static_broadcasted_argnums=(5,),  # is_meta_training flag
)

# Parallelizing environment unroll
jitted_unroll_actor = jax.pmap(
    unroll_jittable_actor,
    axis_name=axis_name,
    devices=devices,
    static_broadcasted_argnums=(5, 6, 7, 8),  # env, rollout_len, etc.
)
```

**Sources:** [colabs/eval.ipynb:296-309]()

Key considerations:
- The `axis_name` parameter (typically `'i'`) identifies the parallel axis for collective operations like `pmean`
- `static_broadcasted_argnums` specifies arguments that should not be sharded (e.g., configuration flags, static structures)
- All pmapped functions operate on the leading axis, which represents the device dimension

## Meta-Gradient Computation

Meta-training optimizes the update rule parameters by differentiating through the inner training loop. This involves a two-level optimization structure:

```mermaid
graph TB
    subgraph "Outer Loop: Update Rule Optimization"
        UR_PARAMS["update_rule_params<br/>(meta parameters)"]
        META_OPT["meta_opt<br/>(optax.adam)"]
        META_GRAD["Meta Gradients<br/>∂meta_loss/∂update_rule_params"]
    end
    
    subgraph "Inner Loop: Agent Training"
        AGENT_PARAMS["learner_state.params<br/>(agent parameters)"]
        
        TRAIN_ROLL["train_rollouts<br/>(N inner steps)"]
        INNER_STEP["agent.learner_step()<br/>(uses update_rule_params)"]
        
        TRAIN_ROLL --> INNER_STEP
        INNER_STEP --> AGENT_PARAMS
        AGENT_PARAMS -.->|"scan over N steps"| INNER_STEP
    end
    
    subgraph "Validation"
        VALID_ROLL["valid_rollout<br/>(2x longer)"]
        VALID_INFERENCE["agent.actor_step()<br/>(with trained params)"]
        VALUE_FN["agent.value_fn.get_value_outs()"]
        META_LOSS["meta_loss<br/>(PG + regularizers)"]
        
        VALID_ROLL --> VALID_INFERENCE
        VALID_INFERENCE --> VALUE_FN
        VALUE_FN --> META_LOSS
    end
    
    UR_PARAMS --> INNER_STEP
    AGENT_PARAMS --> VALID_INFERENCE
    
    META_LOSS --> META_GRAD
    META_GRAD --> META_OPT
    META_OPT --> UR_PARAMS
```

**Sources:** [colabs/meta_train.ipynb:292-448]()

### Inner Step: Agent Parameter Updates

The inner loop performs standard RL updates using the current update rule:

```python
def _inner_step(carry, inputs):
    update_rule_params, learner_state, actor_state, value_state = carry
    actor_rollout, learner_rng = inputs
    
    # Update agent parameters using current update rule
    new_learner_state, new_actor_state, metrics = agent.learner_step(
        rng=learner_rng,
        rollout=actor_rollout,
        learner_state=learner_state,
        agent_net_state=actor_state,
        update_rule_params=update_rule_params,
        is_meta_training=True,
    )
    
    # Update value function
    agent_out, _ = agent.unroll_net(learner_state.params, actor_state, actor_rollout)
    new_value_state, _, _ = agent.value_fn.update(
        value_state, actor_rollout, agent_out['logits']
    )
    
    return (update_rule_params, new_learner_state, new_actor_state, new_value_state), metrics
```

**Sources:** [colabs/meta_train.ipynb:308-336]()

The inner loop:
1. Receives trajectories from the current policy
2. Updates agent parameters using the learned update rule
3. Updates the value function for advantage estimation
4. Returns updated states that carry gradients back to the update rule

### Outer Loss: Meta-Objective

The outer loss evaluates how well the trained agent performs on validation rollouts:

| Component | Purpose | Weight |
|-----------|---------|--------|
| Policy Gradient Loss | Maximize expected returns on validation | 1.0 |
| Entropy Regularizer | Encourage exploration | -1e-2 |
| Y/Z Entropy Loss | Regularize meta-network auxiliary outputs | 1e-3 |
| KL Regularizer | Stabilize policy updates | 1e-3 |
| Mean Deviation Loss | Prevent extreme auxiliary outputs | 1e-3 |

```python
# Meta loss calculation
pg_loss_per_step = utils.differentiable_policy_gradient_loss(
    logits_on_valid, actions_on_valid, adv_t=adv_t, backprop=False
)

# Regularization terms
reg_loss = 0
reg_loss += -1e-2 * distrax.Softmax(logits_on_valid).entropy().mean()
reg_loss += 1e-3 * (y_entropy_loss + z_entropy_loss)
reg_loss += 1e-2 * jnp.mean(target_kl_loss)

meta_loss = pg_loss_per_step.mean() + reg_loss
```

**Sources:** [colabs/meta_train.ipynb:383-415]()

### Gradient Computation Through Training

Meta-gradients are computed using JAX's `jax.grad` with `has_aux=True`:

```python
meta_grads, outputs = jax.grad(_outer_loss, has_aux=True)(
    update_rule_params, agent_state, train_rollouts, valid_rollout, rng
)
```

**Sources:** [colabs/meta_train.ipynb:439-441]()

JAX automatically:
1. Traces through the entire inner training loop (via `jax.lax.scan`)
2. Computes gradients of the validation loss with respect to update rule parameters
3. Handles the composition of multiple gradient computations (agent updates, value function updates)

### Population-Based Training

Meta-training uses a population of agents to stabilize learning:

```mermaid
graph LR
    subgraph "Population"
        A0["Agent 0"]
        A1["Agent 1"]
        AN["Agent N"]
    end
    
    subgraph "Per-Agent Processing"
        R0["train_rollouts[0]<br/>valid_rollouts[0]"]
        R1["train_rollouts[1]<br/>valid_rollouts[1]"]
        RN["train_rollouts[N]<br/>valid_rollouts[N]"]
        
        G0["meta_grads[0]"]
        G1["meta_grads[1]"]
        GN["meta_grads[N]"]
    end
    
    subgraph "Aggregation"
        AVG["jax.tree.map<br/>mean across population"]
        META_OPT["meta_opt.update()"]
        NEW_UR["Updated<br/>update_rule_params"]
    end
    
    A0 --> R0
    A1 --> R1
    AN --> RN
    
    R0 --> G0
    R1 --> G1
    RN --> GN
    
    G0 --> AVG
    G1 --> AVG
    GN --> AVG
    
    AVG --> META_OPT
    META_OPT --> NEW_UR
    
    NEW_UR -.->|"shared across population"| A0
    NEW_UR -.->|"shared across population"| A1
    NEW_UR -.->|"shared across population"| AN
```

**Sources:** [colabs/meta_train.ipynb:460-538]()

The population strategy:
1. Maintains multiple independent agents with separate environment states [colabs/meta_train.ipynb:580-592]()
2. Generates training and validation rollouts for each agent [colabs/meta_train.ipynb:476-491]()
3. Computes meta-gradients independently per agent [colabs/meta_train.ipynb:493-508]()
4. Averages gradients across the population before applying the meta-optimizer [colabs/meta_train.ipynb:525-527]()
5. Broadcasts updated update rule parameters to all agents [colabs/meta_train.ipynb:531]()

## Replay Buffer System

DiscoRL provides a simple FIFO replay buffer for off-policy training:

```mermaid
graph TB
    subgraph "SimpleReplayBuffer"
        DEQUE["collections.deque<br/>(maxlen=capacity)"]
        NP_RNG["np.random.default_rng<br/>(seed)"]
    end
    
    subgraph "Storage"
        ACTOR_ROLL["ActorRollout<br/>(from actor)"]
        DEVICE_GET["jax.device_get()"]
        SPLIT["rlax.tree_split_leaves<br/>(axis=2, batch dim)"]
        
        ACTOR_ROLL --> DEVICE_GET
        DEVICE_GET --> SPLIT
        SPLIT --> DEQUE
    end
    
    subgraph "Sampling"
        SAMPLE_REQ["sample(batch_size)"]
        INDICES["np_rng.integers<br/>(buffer_size)"]
        STACK["utils.tree_stack<br/>(selected trajectories)"]
        SAMPLED["Batched Rollout"]
        
        SAMPLE_REQ --> INDICES
        INDICES --> DEQUE
        DEQUE --> STACK
        STACK --> SAMPLED
    end
```

**Sources:** [colabs/eval.ipynb:232-263]()

### Buffer Implementation

The `SimpleReplayBuffer` class provides basic replay functionality:

```python
class SimpleReplayBuffer:
    def __init__(self, capacity: int, seed: int):
        self.buffer = collections.deque(maxlen=capacity)
        self.capacity = capacity
        self.np_rng = np.random.default_rng(seed)
    
    def add(self, rollout: types.ActorRollout) -> None:
        rollout = jax.device_get(rollout)
        split_tree = rlax.tree_split_leaves(rollout, axis=2)
        self.buffer.extend(split_tree)
    
    def sample(self, batch_size: int) -> types.ActorRollout | None:
        buffer_size = len(self.buffer)
        indices = self.np_rng.integers(buffer_size, size=batch_size)
        batched_samples = utils.tree_stack(
            [self.buffer[i] for i in indices], axis=2
        )
        return batched_samples
```

**Sources:** [colabs/eval.ipynb:232-259]()

Key features:
- **FIFO Storage**: Uses `collections.deque` with fixed capacity for automatic eviction of old samples
- **Device Handling**: Transfers data from device to host using `jax.device_get()` [colabs/eval.ipynb:243]()
- **Trajectory Splitting**: Splits batched rollouts into individual trajectories along the batch dimension [colabs/eval.ipynb:245]()
- **Random Sampling**: Uses NumPy's RNG for efficient CPU-based sampling [colabs/eval.ipynb:255]()
- **Tree Operations**: Leverages JAX tree utilities for structured data handling [colabs/eval.ipynb:256-258]()

### Replay Ratio Pattern

```python
replay_ratio = 32
min_buffer_size = batch_size
num_envs = batch_size // replay_ratio

# Generate trajectories with num_envs parallel environments
actor_rollout, actor_state, ts, env_state = unroll_actor(...)
buffer.add(actor_rollout)

# Sample batch_size trajectories for learning (replay_ratio > 1)
if len(buffer) >= min_buffer_size:
    learner_rollout = buffer.sample(batch_size)
    learner_state, _, metrics = learner_step_fn(...)
```

**Sources:** [colabs/eval.ipynb:281-388]()

The replay ratio allows learning from more samples than are generated per step, improving sample efficiency. With `replay_ratio=32`, the system generates experiences from 2 environments but learns from 64 sampled trajectories per step.

## CPU vs Jittable Environment Handling

DiscoRL supports both CPU-based and JAX-jittable environments with different unroll strategies:

```mermaid
graph TB
    subgraph "Environment Type Detection"
        ENV["env instance"]
        CHECK["isinstance(...,<br/>BatchedJittableEnvironment)"]
        
        ENV --> CHECK
    end
    
    subgraph "CPU Path"
        CPU_UNROLL["unroll_cpu_actor"]
        CPU_LOOP["Python for loop<br/>(rollout_len iterations)"]
        CPU_STEP["env.step(env_state, actions)<br/>(Python call)"]
        CPU_SHARD["utils.shard_across_devices<br/>(for each step)"]
        CPU_GATHER["utils.gather_from_devices<br/>(actions from pmap)"]
        
        CPU_UNROLL --> CPU_LOOP
        CPU_LOOP --> CPU_SHARD
        CPU_SHARD --> CPU_STEP
        CPU_STEP --> CPU_GATHER
        CPU_GATHER --> CPU_LOOP
    end
    
    subgraph "Jittable Path"
        JIT_UNROLL["unroll_jittable_actor<br/>(jax.pmap wrapped)"]
        JIT_SCAN["jax.lax.scan<br/>(rollout_len steps)"]
        JIT_STEP["env.step(env_state, actions)<br/>(pure JAX function)"]
        JIT_COMPILE["JIT compiled<br/>(no Python overhead)"]
        
        JIT_UNROLL --> JIT_SCAN
        JIT_SCAN --> JIT_STEP
        JIT_STEP --> JIT_COMPILE
        JIT_COMPILE -.->|"fused operations"| JIT_SCAN
    end
    
    CHECK -->|"False"| CPU_UNROLL
    CHECK -->|"True"| JIT_UNROLL
```

**Sources:** [colabs/eval.ipynb:146-218](), [colabs/eval.ipynb:321-334]()

### CPU Actor Unroll

For CPU environments, the system uses a Python loop with explicit device communication:

```python
def unroll_cpu_actor(params, actor_state, ts, env_state, rng, 
                     env, rollout_len, actor_step_fn, devices):
    actor_timesteps = []
    for _ in range(rollout_len):
        rng, step_rng = jax.random.split(rng)
        step_rng = jax.random.split(step_rng, len(devices))
        ts = utils.shard_across_devices(ts, devices)
        
        actor_timestep, actor_state = actor_step_fn(
            params, step_rng, ts, actor_state
        )
        actions = utils.gather_from_devices(actor_timestep.actions)
        env_state, ts = env.step(env_state, actions)
        
        actor_timesteps.append(actor_timestep)
    
    actor_rollout = types.ActorRollout.from_timestep(
        utils.tree_stack(actor_timesteps, axis=1)
    )
    return actor_rollout, actor_state, ts, env_state
```

**Sources:** [colabs/eval.ipynb:146-175]()

### Jittable Actor Unroll

For jittable environments, the entire unroll is compiled as a single fused operation:

```python
def unroll_jittable_actor(params, actor_state, ts, env_state, rng, 
                          env, rollout_len, actor_step_fn, devices):
    def _single_step(carry, step_rng):
        env_state, ts, actor_state = carry
        actor_timestep, actor_state = agent.actor_step(
            params, step_rng, ts, actor_state
        )
        env_state, ts = env.step(env_state, actor_timestep.actions)
        return (env_state, ts, actor_state), actor_timestep
    
    (env_state, ts, actor_state), actor_rollout = jax.lax.scan(
        _single_step,
        (env_state, ts, actor_state),
        jax.random.split(rng, rollout_len),
    )
    
    actor_rollout = types.ActorRollout.from_timestep(actor_rollout)
    return actor_rollout, actor_state, ts, env_state
```

**Sources:** [colabs/eval.ipynb:178-207](), [colabs/meta_train.ipynb:154-180]()

Performance characteristics:

| Aspect | CPU Environment | Jittable Environment |
|--------|----------------|----------------------|
| Compilation | Actor steps compiled, loop in Python | Entire unroll compiled as one function |
| Device Communication | Per-step shard/gather overhead | All data stays on device |
| Flexibility | Easier to debug, arbitrary Python logic | Restricted to JAX-traceable operations |
| Performance | Lower (Python loop overhead) | Higher (fused operations, no host sync) |

## Static vs Dynamic Arguments

JAX compilation requires distinguishing between static (compile-time) and dynamic (runtime) arguments:

```python
jitted_unroll_actor = jax.pmap(
    unroll_jittable_actor,
    axis_name=axis_name,
    devices=devices,
    static_broadcasted_argnums=(5, 6, 7, 8),  # env, rollout_len, actor_step_fn, devices
)

learner_step_fn = jax.pmap(
    agent.learner_step,
    axis_name=axis_name,
    devices=devices,
    static_broadcasted_argnums=(5,),  # is_meta_training flag
)
```

**Sources:** [colabs/eval.ipynb:304-309](), [colabs/eval.ipynb:298-303]()

### Static Arguments

Arguments marked as static via `static_broadcasted_argnums`:
- Must be hashable and equal across all devices
- Trigger recompilation if their values change
- Examples: environment objects, rollout lengths, boolean flags, function references

### Dynamic Arguments

Arguments not marked as static:
- Are traced as abstract values (shapes and dtypes)
- Can change values between calls without recompilation
- Examples: parameters, states, observations, RNG keys

Proper static argument specification is critical for:
1. **Avoiding Recompilation**: Changing static arguments forces recompilation, which can be expensive
2. **Enabling Optimizations**: Static values allow XLA to perform compile-time optimizations (e.g., loop unrolling)
3. **Correctness**: Some values (like environment instances) cannot be traced and must be static

## Accumulating Episode Returns

DiscoRL provides utilities for tracking cumulative returns across episode boundaries:

```python
def accumulate_rewards(acc_rewards, x):
    rewards, discounts = x
    
    def _step_fn(acc_rewards, x):
        rewards, discounts = x
        acc_rewards += rewards
        return acc_rewards * discounts, acc_rewards
    
    return jax.lax.scan(_step_fn, acc_rewards, (rewards, discounts))
```

**Sources:** [colabs/eval.ipynb:210-218]()

The accumulator:
1. Adds immediate rewards to the running total
2. Outputs the current accumulated return
3. Resets to zero when an episode ends (discount = 0)
4. Continues accumulating for ongoing episodes (discount > 0)

This pattern correctly handles multiple parallel environments with episodes ending at different times, making it suitable for pmapped execution where each device tracks multiple episodes simultaneously.

**Sources:** [colabs/eval.ipynb:210-218](), [colabs/eval.ipynb:310-314](), [colabs/eval.ipynb:366-374]()

---

