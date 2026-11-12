<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/disco_rl · extra page Policy Networks · fetched 2026-10-26 -->

# Policy Networks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [disco_rl/agent.py](disco_rl/agent.py)
- [disco_rl/networks/nets.py](disco_rl/networks/nets.py)

</details>



Policy networks are the neural network architectures that agents use to compute action distributions from observations. They implement the policy function π(a|s), producing outputs (logits, values, etc.) according to specifications defined by update rules. For meta-network architectures used by the Disco update rule, see [Meta-Networks](#3.4.2). For action-conditional models that extend policy networks, see [Action Models](#3.4.3).

**Sources**: [disco_rl/networks/nets.py:1-159](), [disco_rl/agent.py:90-99]()

---

## Architecture Overview

Policy networks in DiscoRL follow a modular design with three key components:

1. **Factory Function**: `get_network()` constructs networks based on string names
2. **Base Class**: `MLPHeadNet` defines the embedding + head architecture pattern
3. **Concrete Implementations**: Currently `MLP` for feedforward networks with optional recurrent action models

The system uses Haiku's `transform_with_state` to create pure functional interfaces that separate parameter initialization from execution.

```mermaid
graph TB
    subgraph "Factory Layer"
        GET_NET["get_network(name, ...)"]
    end
    
    subgraph "PolicyNetwork Interface"
        POLICY_NET["PolicyNetwork NamedTuple"]
        INIT["init(rng, obs, should_reset)"]
        ONE_STEP["one_step(params, state, obs, should_reset)"]
        UNROLL["unroll(params, state, obs, should_reset)"]
    end
    
    subgraph "Implementation Layer"
        BASE["MLPHeadNet<br/>Abstract Base"]
        MLP["MLP<br/>Concrete Implementation"]
        EMBEDDING["_embedding_pass()"]
        HEAD["_head_pass()"]
    end
    
    subgraph "Optional Extensions"
        ACTION_MODEL["ActionModel<br/>(LSTM/Transformer)"]
        MODEL_OUT["model_out"]
    end
    
    subgraph "Output Structure"
        OUT_SPEC["out_spec<br/>from UpdateRule"]
        MODEL_SPEC["model_out_spec<br/>from UpdateRule"]
        AGENT_OUTS["AgentOuts<br/>{logits, value, ...}"]
    end
    
    GET_NET -->|"returns"| POLICY_NET
    POLICY_NET --> INIT
    POLICY_NET --> ONE_STEP
    POLICY_NET --> UNROLL
    
    INIT -.->|"wraps"| MLP
    ONE_STEP -.->|"wraps"| MLP
    UNROLL -.->|"wraps"| MLP
    
    MLP -->|"inherits"| BASE
    BASE --> EMBEDDING
    BASE --> HEAD
    
    BASE -.->|"optional"| ACTION_MODEL
    ACTION_MODEL --> MODEL_OUT
    
    OUT_SPEC -->|"defines"| HEAD
    MODEL_SPEC -->|"defines"| ACTION_MODEL
    
    HEAD --> AGENT_OUTS
    MODEL_OUT --> AGENT_OUTS
```

**Sources**: [disco_rl/networks/nets.py:32-56](), [disco_rl/networks/nets.py:59-125]()

---

## PolicyNetwork Interface

The `PolicyNetwork` named tuple defines the functional interface for all policy networks, consisting of three pure functions:

| Function | Signature | Purpose |
|----------|-----------|---------|
| `init` | `(rng, obs, should_reset) -> (params, state)` | Initialize network parameters and initial RNN state |
| `one_step` | `(params, state, obs, should_reset) -> (outs, state)` | Single-step inference for actor rollout |
| `unroll` | `(params, state, obs, should_reset) -> (outs, state)` | Batched time-series processing for learning |

These functions are created by Haiku's `transform_with_state` and `without_apply_rng`, making them compatible with JAX transformations like `jit`, `vmap`, and `grad`.

```mermaid
graph LR
    subgraph "Haiku Transform"
        MODULE["Network Module<br/>(MLP class)"]
        TRANSFORM["hk.transform_with_state"]
        WITHOUT_RNG["hk.without_apply_rng"]
    end
    
    subgraph "Wrapped Functions"
        AGENT_STEP["_agent_step()"]
        UNROLL_FN["_unroll()"]
    end
    
    subgraph "Pure Functions"
        INIT_FN["init_fn"]
        ONE_STEP_FN["one_step_fn"]
        UNROLL_PURE["unroll_fn"]
    end
    
    subgraph "PolicyNetwork"
        PN_INIT["init"]
        PN_STEP["one_step"]
        PN_UNROLL["unroll"]
    end
    
    MODULE --> AGENT_STEP
    MODULE --> UNROLL_FN
    
    AGENT_STEP --> TRANSFORM
    UNROLL_FN --> TRANSFORM
    
    TRANSFORM --> WITHOUT_RNG
    WITHOUT_RNG --> INIT_FN
    WITHOUT_RNG --> ONE_STEP_FN
    WITHOUT_RNG --> UNROLL_PURE
    
    INIT_FN --> PN_INIT
    ONE_STEP_FN --> PN_STEP
    UNROLL_PURE --> PN_UNROLL
```

**Sources**: [disco_rl/networks/nets.py:32-56](), [disco_rl/types.py]()

---

## Network Implementations

### MLPHeadNet Base Class

`MLPHeadNet` is an abstract base class that implements the common **embedding + head** architecture pattern used across all policy networks. It separates the network into two stages:

1. **Embedding Pass**: Converts observations into a fixed-size embedding vector
2. **Head Pass**: Produces multiple outputs from the embedding according to `out_spec`

```mermaid
graph TB
    subgraph "Input Processing"
        OBS["observations<br/>(dict of arrays)"]
        SHOULD_RESET["should_reset<br/>(bool array)"]
    end
    
    subgraph "MLPHeadNet Pipeline"
        EMBED_PASS["_embedding_pass()<br/>Abstract method"]
        EMBEDDING["embedding<br/>(fixed-size vector)"]
        HEAD_PASS["_head_pass()<br/>Linear heads"]
        OUT_SPEC["out_spec<br/>(from update rule)"]
    end
    
    subgraph "Optional Action Model"
        ROOT_EMBED["_model.root_embedding()"]
        MODEL_STEP["_model.model_step()"]
        MODEL_OUT_SPEC["model_out_spec"]
    end
    
    subgraph "Output"
        BASE_OUTS["{'logits': [...], 'value': [...], ...}"]
        MODEL_OUTS["{'model_logits': [...], ...}"]
        FINAL_OUTS["AgentOuts<br/>(merged dict)"]
    end
    
    OBS --> EMBED_PASS
    SHOULD_RESET --> EMBED_PASS
    EMBED_PASS --> EMBEDDING
    
    EMBEDDING --> HEAD_PASS
    OUT_SPEC -.->|"defines structure"| HEAD_PASS
    HEAD_PASS --> BASE_OUTS
    
    EMBEDDING --> ROOT_EMBED
    ROOT_EMBED --> MODEL_STEP
    MODEL_OUT_SPEC -.->|"defines structure"| MODEL_STEP
    MODEL_STEP --> MODEL_OUTS
    
    BASE_OUTS --> FINAL_OUTS
    MODEL_OUTS --> FINAL_OUTS
```

The `_head_pass` method creates a separate linear layer for each output in `out_spec`, all reading from the same embedding:

```python
# Conceptual structure from _head_pass
for name, spec in out_spec.items():
    output[name] = hk.nets.MLP([spec.shape])(embedding)
```

**Sources**: [disco_rl/networks/nets.py:59-125]()

### MLP Implementation

The `MLP` class is a concrete implementation of `MLPHeadNet` that uses a simple feedforward network for the embedding pass. It flattens and concatenates all observation components, then passes them through a multi-layer perceptron.

| Component | Implementation | Configuration |
|-----------|----------------|---------------|
| Observation Processing | `hk.Flatten()` + `jnp.concatenate()` | Automatic |
| Embedding Network | `hk.nets.MLP(dense)` | `dense=(512, 512)` |
| Head Network | Linear layers per `out_spec` | `head_w_init_std=1e-2` |
| Action Model | Optional LSTM/Transformer | `model_arch_name='lstm'` |

```mermaid
graph TB
    subgraph "Input Layer"
        OBS_DICT["observations<br/>{grid: [B,H,W], ...}"]
        FLATTEN["hk.Flatten()"]
        CONCAT["jnp.concatenate()"]
    end
    
    subgraph "Embedding MLP"
        FLAT_INPUT["flat_input<br/>[B, D]"]
        DENSE1["Dense(512)<br/>+ ReLU"]
        DENSE2["Dense(512)<br/>+ ReLU"]
        EMBEDDING["embedding<br/>[B, 512]"]
    end
    
    subgraph "Output Heads"
        LOGITS_HEAD["Linear(num_actions)<br/>logits"]
        VALUE_HEAD["Linear(num_bins)<br/>value"]
        OTHER_HEADS["... other outputs"]
    end
    
    OBS_DICT --> FLATTEN
    FLATTEN --> CONCAT
    CONCAT --> FLAT_INPUT
    
    FLAT_INPUT --> DENSE1
    DENSE1 --> DENSE2
    DENSE2 --> EMBEDDING
    
    EMBEDDING --> LOGITS_HEAD
    EMBEDDING --> VALUE_HEAD
    EMBEDDING --> OTHER_HEADS
```

The `unroll` method applies the network to time-series data using `hk.BatchApply`:

```python
def unroll(self, inputs, should_reset):
    return hk.BatchApply(self.__call__)(inputs, should_reset)
```

This efficiently processes sequences by vectorizing over the time dimension.

**Sources**: [disco_rl/networks/nets.py:127-159]()

---

## Integration with Update Rules

Policy networks are tightly coupled with update rules, which define the network's output structure through two specifications:

### Output Specifications

```mermaid
graph LR
    subgraph "Update Rule"
        UR["UpdateRule instance"]
        FLAT_SPEC["flat_output_spec()"]
        MODEL_SPEC["model_output_spec()"]
    end
    
    subgraph "Network Factory"
        GET_NET["get_network()"]
        OUT_SPEC["out_spec parameter"]
        MODEL_OUT_SPEC["model_out_spec parameter"]
    end
    
    subgraph "Network Outputs"
        REQUIRED["Required Outputs<br/>logits, value"]
        OPTIONAL["Optional Outputs<br/>model_logits, aux_*"]
    end
    
    UR --> FLAT_SPEC
    UR --> MODEL_SPEC
    
    FLAT_SPEC --> OUT_SPEC
    MODEL_SPEC --> MODEL_OUT_SPEC
    
    OUT_SPEC --> GET_NET
    MODEL_OUT_SPEC --> GET_NET
    
    GET_NET --> REQUIRED
    GET_NET --> OPTIONAL
```

Example from Disco update rule configuration:
- `out_spec`: Contains 'logits' for action selection and 'value' for value prediction
- `model_out_spec`: Contains 'model_logits' and other auxiliary outputs from the action model

**Sources**: [disco_rl/agent.py:91-99](), [disco_rl/update_rules/base.py]()

---

## Agent Integration

The Agent class uses policy networks in three contexts:

### 1. Initialization

```mermaid
graph TB
    AGENT_INIT["Agent.__init__()"]
    UR_SPECS["update_rule.flat_output_spec()<br/>update_rule.model_output_spec()"]
    GET_NET["nets.get_network()"]
    NETWORK["self._network<br/>(PolicyNetwork)"]
    
    AGENT_INIT --> UR_SPECS
    UR_SPECS --> GET_NET
    GET_NET --> NETWORK
```

The agent creates the network during initialization, passing specifications from the update rule and configuration from `agent_settings.net_settings`.

**Sources**: [disco_rl/agent.py:90-99]()

### 2. Actor Step (Inference)

During environment interaction, the agent uses `one_step` for single-timestep inference:

```mermaid
graph LR
    subgraph "Actor Step"
        TIMESTEP["EnvironmentTimestep<br/>(obs, reward, ...)"]
        ACTOR_STATE["actor_state<br/>(RNN hidden state)"]
        PARAMS["actor_params"]
    end
    
    subgraph "Network Inference"
        ONE_STEP["network.one_step()"]
        AGENT_OUTS["agent_outs<br/>{logits, value, ...}"]
        NEXT_STATE["next_actor_state"]
    end
    
    subgraph "Action Selection"
        SAMPLE["distrax.Softmax.sample()"]
        ACTIONS["actions"]
    end
    
    TIMESTEP --> ONE_STEP
    ACTOR_STATE --> ONE_STEP
    PARAMS --> ONE_STEP
    
    ONE_STEP --> AGENT_OUTS
    ONE_STEP --> NEXT_STATE
    
    AGENT_OUTS --> SAMPLE
    SAMPLE --> ACTIONS
```

**Sources**: [disco_rl/agent.py:147-173]()

### 3. Learner Step (Training)

During training, the agent uses `unroll` to process entire trajectories efficiently:

```mermaid
graph TB
    subgraph "Input"
        ROLLOUT["ActorRollout<br/>(T timesteps)"]
        PARAMS["learner_state.params"]
        NET_STATE["agent_net_state"]
    end
    
    subgraph "Network Unroll"
        MASKS["masks = discounts[:-1] > 0"]
        SHOULD_RESET["should_reset<br/>(shifted masks)"]
        UNROLL["network.unroll()"]
    end
    
    subgraph "Output"
        AGENT_OUT["agent_out<br/>(T timesteps)"]
        NEW_STATE["new_agent_net_state"]
    end
    
    subgraph "Loss Computation"
        UR_INPUTS["UpdateRuleInputs"]
        LOSS["update_rule.agent_loss()"]
        GRADS["gradients"]
    end
    
    ROLLOUT --> MASKS
    MASKS --> SHOULD_RESET
    
    ROLLOUT --> UNROLL
    PARAMS --> UNROLL
    NET_STATE --> UNROLL
    SHOULD_RESET --> UNROLL
    
    UNROLL --> AGENT_OUT
    UNROLL --> NEW_STATE
    
    AGENT_OUT --> UR_INPUTS
    UR_INPUTS --> LOSS
    LOSS --> GRADS
```

The `unroll_net` method prepares reset signals and calls the network's `unroll` function, which uses `hk.BatchApply` to efficiently process the time dimension.

**Sources**: [disco_rl/agent.py:175-198](), [disco_rl/agent.py:248-316]()

---

## Configuration

Policy networks are configured through the `net_settings` section of agent configuration. Here are the typical configurations for different scenarios:

### Disco103 Configuration

```python
net_settings = dict(
    name='mlp',
    net_args=dict(
        dense=(512, 512),              # MLP embedding layers
        model_arch_name='lstm',        # Optional action model
        head_w_init_std=1e-2,          # Head initialization
        model_kwargs=dict(
            head_mlp_hiddens=(128,),   # Action model MLP
            lstm_size=128,             # Action model LSTM size
        ),
    ),
)
```

### Actor-Critic Configuration

```python
net_settings = dict(
    name='mlp',
    net_args=dict(
        dense=(64, 32, 32),            # Smaller MLP
        model_arch_name='lstm',
        head_w_init_std=1e-2,
        model_kwargs=dict(
            head_mlp_hiddens=(64,),
            lstm_size=64,
        ),
    ),
)
```

### Configuration Parameters

| Parameter | Type | Purpose |
|-----------|------|---------|
| `name` | str | Network architecture ('mlp') |
| `dense` | tuple[int] | Hidden layer sizes for embedding MLP |
| `model_arch_name` | str | Optional action model type ('lstm', 'transformer') |
| `head_w_init_std` | float | Standard deviation for head weight initialization |
| `model_kwargs` | dict | Configuration for optional action model |

**Sources**: [disco_rl/agent.py:319-420]()

---

## Network State Management

Policy networks maintain state for recurrent components (LSTM hidden states). The state lifecycle:

```mermaid
graph TB
    subgraph "Initialization"
        INIT_STATE["initial_actor_state(rng)"]
        DUMMY_OBS["dummy observations"]
        NETWORK_INIT["network.init()"]
        EMPTY_STATE["empty RNN state"]
    end
    
    subgraph "Actor Loop"
        ACTOR_STEP["actor_step()"]
        CURR_STATE["current actor_state"]
        ONE_STEP["network.one_step()"]
        NEXT_STATE["next_actor_state"]
        SHOULD_RESET["should_reset<br/>(on episode end)"]
    end
    
    subgraph "Learner Loop"
        UNROLL_NET["unroll_net()"]
        INITIAL_STATE["initial agent_net_state"]
        NET_UNROLL["network.unroll()"]
        FINAL_STATE["final agent_net_state"]
    end
    
    INIT_STATE --> DUMMY_OBS
    DUMMY_OBS --> NETWORK_INIT
    NETWORK_INIT --> EMPTY_STATE
    
    EMPTY_STATE --> CURR_STATE
    CURR_STATE --> ONE_STEP
    ONE_STEP --> NEXT_STATE
    SHOULD_RESET -.->|"resets if true"| ONE_STEP
    NEXT_STATE --> CURR_STATE
    
    EMPTY_STATE --> INITIAL_STATE
    INITIAL_STATE --> NET_UNROLL
    NET_UNROLL --> FINAL_STATE
```

The `should_reset` parameter signals when episodes end, allowing LSTM states to be reset appropriately. This is computed from the environment's `step_type` in the actor and from `discounts` in the learner.

**Sources**: [disco_rl/agent.py:123-132](), [disco_rl/agent.py:147-173](), [disco_rl/agent.py:175-198]()

---

