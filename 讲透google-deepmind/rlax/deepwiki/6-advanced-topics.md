<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/rlax · page 6 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rlax/_src/nonlinear_bellman.py](rlax/_src/nonlinear_bellman.py)
- [rlax/_src/transforms.py](rlax/_src/transforms.py)

</details>



## Purpose and Scope

This page covers advanced reinforcement learning techniques implemented in RLax that go beyond standard value learning and policy gradient methods. The primary focus is on **nonlinear Bellman equations** and **value transformations**, which enable learning in transformed value spaces for improved stability and representational capacity.

For basic value learning methods (TD, Q-learning, SARSA), see [Value-Based Learning](#2). For policy optimization methods, see [Policy Optimization Methods](#5). For multistep return calculations that these transformations wrap, see [Multistep Returns and Credit Assignment](#3).

The advanced topics covered here include:

- **Value function transformations** using the `TxPair` abstraction
- **Nonlinear Bellman equations** that operate in transformed value spaces
- **Specialized transformation functions** (signed hyperbolic, 2-hot encoding)
- **MuZero-style transformations** combining squashing and discretization
- **Transformed variants** of core RL algorithms (Q-learning, Retrace, etc.)

These techniques are particularly useful when dealing with unbounded or highly variable value ranges, as seen in algorithms like MuZero and R2D2.

---

## Overview of Value Transformations

Traditional value-based RL assumes that value functions are the fixed points of linear Bellman equations. However, learning can be improved by working in a **transformed value space**, where the Bellman equation becomes nonlinear. The key insight is that we can:

1. Transform values before computing bootstrapped returns
2. Compute targets in the transformed space
3. Learn to predict transformed values
4. Invert the transformation when needed for action selection

```mermaid
graph LR
    subgraph "Standard Value Learning"
        V1["V(s)"] --> B1["Bellman Operator<br/>R + γV(s')"] --> T1["Target"]
        P1["Predictions V(s)"] --> L1["Loss:<br/>||V - Target||²"]
    end
    
    subgraph "Transformed Value Learning"
        V2["V(s)"] --> TX1["h(V)"] --> B2["Nonlinear Bellman<br/>h(R + γh⁻¹(h(V')))"] --> T2["Transformed Target"]
        P2["Predictions h(V)"] --> L2["Loss:<br/>||h(V) - h(Target)||²"]
        TX1 -.inverse.-> INV["h⁻¹"]
        INV --> ACT["Action Selection"]
    end
    
    style TX1 fill:#f9f9f9
    style B2 fill:#f9f9f9
    style INV fill:#f9f9f9
```

**Diagram: Standard vs Transformed Value Learning**

The transformation `h(·)` and its inverse `h⁻¹(·)` form what RLax calls a `TxPair`.

**Sources:** [rlax/_src/nonlinear_bellman.py:15-24]()

---

## The TxPair Abstraction

The core abstraction for value transformations is the `TxPair` named tuple, defined in [rlax/_src/nonlinear_bellman.py:37]():

```python
TxPair = collections.namedtuple('TxPair', ['apply', 'apply_inv'])
```

A `TxPair` consists of:
- **`apply`**: The forward transformation function `h(x)`
- **`apply_inv`**: The inverse transformation function `h⁻¹(x)`

These are typically monotonically increasing functions to preserve value orderings.

```mermaid
graph TB
    subgraph "TxPair Structure"
        TP["TxPair<br/>(namedtuple)"]
        TP --> APPLY["apply: Callable<br/>x → h(x)"]
        TP --> AINV["apply_inv: Callable<br/>x → h⁻¹(x)"]
    end
    
    subgraph "Transformation Properties"
        PROP1["Monotonic:<br/>x₁ < x₂ ⟹ h(x₁) < h(x₂)"]
        PROP2["Invertible:<br/>h⁻¹(h(x)) = x"]
        PROP3["Squashing or<br/>Reparametrization"]
    end
    
    subgraph "Example Pairs from nonlinear_bellman.py"
        ID["IDENTITY_PAIR<br/>h(x) = x"]
        LOG["SIGNED_LOGP1_PAIR<br/>h(x) = sign(x)log(1+|x|)"]
        HYP["SIGNED_HYPERBOLIC_PAIR<br/>h(x) = sign(x)(√(|x|+1)-1) + εx"]
        SIN["HYPERBOLIC_SIN_PAIR<br/>h(x) = arcsinh(x)"]
        DISC["DISCOUNT_TRANSFORM_PAIR<br/>h(x) = -log(1-x)"]
    end
    
    TP --> ID
    TP --> LOG
    TP --> HYP
    TP --> SIN
    TP --> DISC
    
    APPLY -.satisfies.-> PROP1
    APPLY -.satisfies.-> PROP2
```

**Diagram: TxPair Abstraction and Built-in Pairs**

**Sources:** [rlax/_src/nonlinear_bellman.py:37-53]()

### Pre-defined Transformation Pairs

RLax provides several pre-built transformation pairs:

| Constant | Forward Transform `apply` | Inverse Transform `apply_inv` | Use Case |
|----------|--------------------------|-------------------------------|----------|
| `IDENTITY_PAIR` | `identity(x)` | `identity(x)` | No transformation (baseline) |
| `SIGNED_LOGP1_PAIR` | `signed_logp1(x)` | `signed_expm1(x)` | Logarithmic squashing |
| `SIGNED_HYPERBOLIC_PAIR` | `signed_hyperbolic(x)` | `signed_parabolic(x)` | MuZero-style squashing |
| `HYPERBOLIC_SIN_PAIR` | `hyperbolic_arcsin(x)` | `hyperbolic_sin(x)` | Smooth squashing |
| `DISCOUNT_TRANSFORM_PAIR` | `-log(1-x)` | `1-exp(-x)` | Discount factor transforms |

**Sources:** [rlax/_src/nonlinear_bellman.py:43-53]()

---

## Transformation Functions

The actual transformation functions are implemented in `rlax/_src/transforms.py`. These are element-wise operations that can be applied to arrays of values.

### Squashing Transformations

**Signed Logarithmic Transform** [rlax/_src/transforms.py:48-57]():
```
h(x) = sign(x) · log(1 + |x|)
h⁻¹(x) = sign(x) · (exp(|x|) - 1)
```

This transformation compresses large values logarithmically while preserving sign and being smooth at zero.

**Signed Hyperbolic Transform** [rlax/_src/transforms.py:60-82]():
```
h(x) = sign(x) · (√(|x| + 1) - 1) + εx
h⁻¹(x) = sign(x) · (z² - 1), where z = √(1 + 4ε(ε + 1 + |x|)) / 2ε - 1 / 2ε
```

This is the transformation used in MuZero, providing mild squashing for small values and stronger squashing for large values. The `ε` parameter (default 0.001) ensures the derivative doesn't vanish at zero.

```mermaid
graph LR
    subgraph "Common Transformations in transforms.py"
        TRANS["Transformation<br/>Functions"]
        
        TRANS --> SQU["Squashing<br/>Functions"]
        TRANS --> DISC["Discretization<br/>Functions"]
        
        SQU --> SLOG["signed_logp1<br/>signed_expm1"]
        SQU --> SHYP["signed_hyperbolic<br/>signed_parabolic"]
        SQU --> HSIN["hyperbolic_arcsin<br/>hyperbolic_sin"]
        SQU --> POW["power"]
        
        DISC --> T2H["transform_to_2hot<br/>transform_from_2hot"]
        DISC --> T2HN["transform_to_2hot_nonlinear<br/>transform_from_2hot_nonlinear"]
    end
    
    subgraph "Properties"
        SLOG --> P1["Logarithmic<br/>compression"]
        SHYP --> P2["MuZero-style<br/>gradual squashing"]
        T2H --> P3["Discretize to<br/>uniform bins"]
        T2HN --> P4["Discretize to<br/>non-uniform bins"]
    end
```

**Diagram: Transformation Functions in transforms.py**

**Sources:** [rlax/_src/transforms.py:48-89](), [rlax/_src/transforms.py:92-144]()

### 2-Hot Encoding

A **2-hot representation** discretizes a scalar value over a fixed support by distributing probability mass across two adjacent bins. This is particularly useful for representing value distributions.

**Forward Transformation** [rlax/_src/transforms.py:92-109]():
1. Clip scalar to `[min_value, max_value]`
2. Map to bin index in `[0, num_bins-1]`
3. Compute floor and ceiling bins
4. Distribute probability inversely proportional to distance

**Inverse Transformation** [rlax/_src/transforms.py:112-121]():
1. Compute weighted average over support space
2. Returns expected value under the categorical distribution

```mermaid
graph TD
    subgraph "2-Hot Encoding Process"
        SCALAR["Scalar Value<br/>v = 3.7"]
        
        SCALAR --> CLIP["Clip to [min, max]<br/>v ∈ [0, 10]"]
        CLIP --> MAP["Map to bin index<br/>idx = 3.7"]
        MAP --> SPLIT["Split to adjacent bins"]
        
        SPLIT --> LOWER["Lower bin: 3<br/>weight: 0.3"]
        SPLIT --> UPPER["Upper bin: 4<br/>weight: 0.7"]
        
        LOWER --> VEC["2-Hot Vector<br/>[0, 0, 0, 0.3, 0.7, 0, ...]"]
        UPPER --> VEC
    end
    
    subgraph "Inverse: From Distribution"
        VEC2["2-Hot Vector<br/>p ∈ ℝⁿ"]
        VEC2 --> SUPP["Support Space<br/>s = linspace(min, max, n)"]
        SUPP --> DOT["Weighted Sum<br/>v = Σ pᵢ·sᵢ"]
        DOT --> RES["Scalar Value"]
    end
```

**Diagram: 2-Hot Encoding and Decoding**

**Sources:** [rlax/_src/transforms.py:92-121]()

---

## Composing Transformations

Transformation pairs can be composed using the `compose_tx` function [rlax/_src/nonlinear_bellman.py:74-99]().

```mermaid
graph LR
    subgraph "compose_tx Example"
        X["Input x"]
        
        X --> F["f.apply(x)"]
        F --> G["g.apply(f(x))"]
        G --> Y["Output y"]
        
        Y -.inverse.-> GINV["g.apply_inv(y)"]
        GINV -.inverse.-> FINV["f.apply_inv(g⁻¹(y))"]
        FINV -.inverse.-> X2["Recovered x"]
    end
    
    subgraph "Forward: [f, g]"
        FWD["Transformations<br/>applied in order"]
        FWD --> FWD1["Step 1: f"]
        FWD --> FWD2["Step 2: g"]
    end
    
    subgraph "Inverse: [f, g]"
        INV["Inverses applied<br/>in reverse order"]
        INV --> INV1["Step 1: g⁻¹"]
        INV --> INV2["Step 2: f⁻¹"]
    end
```

**Diagram: Transformation Composition**

The `compose_tx(*tx_list)` function creates a new `TxPair` where:
- **Forward**: Applies transformations in order `g(f(x))`
- **Inverse**: Applies inverses in reverse order `f⁻¹(g⁻¹(x))`

**Sources:** [rlax/_src/nonlinear_bellman.py:74-99]()

---

## MuZero Transformation Pair

The **MuZero transformation pair** [rlax/_src/nonlinear_bellman.py:102-124]() combines squashing with discretization, as introduced in the MuZero paper (Schrittwieser et al., 2019).

```python
def muzero_pair(min_value, max_value, num_bins, tx) -> TxPair:
    """Combines a monotonic squashing function with 2-hot encoding."""
    return compose_tx(tx, twohot_pair(min_value, max_value, num_bins))
```

This composition:
1. First applies a nonlinear squashing function (typically `SIGNED_HYPERBOLIC_PAIR`)
2. Then applies 2-hot encoding to discretize over a fixed support

```mermaid
graph LR
    subgraph "MuZero Transformation Pipeline"
        V["Raw Value<br/>v ∈ ℝ"]
        
        V --> SQ["Squashing Transform<br/>h(v) = sign(v)(√(|v|+1)-1) + εv"]
        SQ --> DISC["2-Hot Encoding<br/>Over [h(min), h(max)]"]
        DISC --> OUT["Distribution<br/>p ∈ ℝⁿ"]
        
        OUT -.inverse.-> INV1["From 2-Hot<br/>Weighted average"]
        INV1 -.inverse.-> INV2["Unsquash<br/>h⁻¹(v)"]
        INV2 -.inverse.-> V2["Recovered Value"]
    end
    
    subgraph "Parameters"
        PARAMS["muzero_pair params"]
        PARAMS --> PMIN["min_value:<br/>minimum support"]
        PARAMS --> PMAX["max_value:<br/>maximum support"]
        PARAMS --> PBINS["num_bins:<br/>discretization bins"]
        PARAMS --> PTX["tx:<br/>squashing TxPair"]
    end
```

**Diagram: MuZero Transformation Pipeline**

**Example usage:**
```python
# Create a MuZero pair with signed hyperbolic squashing
muzero_tx = muzero_pair(
    min_value=-300.0,
    max_value=300.0,
    num_bins=601,
    tx=SIGNED_HYPERBOLIC_PAIR
)
```

**Sources:** [rlax/_src/nonlinear_bellman.py:102-124]()

---

## Unbiased Transformation Pair

The **unbiased transformation pair** [rlax/_src/nonlinear_bellman.py:127-155]() is an alternative to `muzero_pair` where the nonlinearity is applied to the bin locations rather than the scalar value.

```mermaid
graph TB
    subgraph "muzero_pair: Transform Value then Discretize"
        MZ_V["Value v"]
        MZ_V --> MZ_TX["Apply h(v)"]
        MZ_TX --> MZ_DISC["Discretize over<br/>uniform bins"]
    end
    
    subgraph "unbiased_transform_pair: Discretize over Transformed Bins"
        UB_V["Value v"]
        UB_BINS["Compute bins<br/>b = h⁻¹(linspace(min, max, n))"]
        UB_V --> UB_DISC["Discretize over<br/>non-uniform bins b"]
        UB_BINS --> UB_DISC
    end
    
    MZ_DISC --> MZ_RES["Can introduce bias<br/>in expectation"]
    UB_DISC --> UB_RES["Unbiased<br/>in expectation"]
```

**Diagram: MuZero Pair vs Unbiased Transform Pair**

The key difference:
- **`muzero_pair`**: Transforms the value, then discretizes uniformly
- **`unbiased_transform_pair`**: Discretizes over non-uniform bins defined by the inverse transformation

The unbiased version uses `transform_to_2hot_nonlinear` [rlax/_src/transforms.py:124-136]() and `transform_from_2hot_nonlinear` [rlax/_src/transforms.py:139-144](), which work with arbitrary bin locations.

**Sources:** [rlax/_src/nonlinear_bellman.py:127-155](), [rlax/_src/transforms.py:124-144]()

---

## Transformed Value Learning Algorithms

The `transform_values` decorator [rlax/_src/nonlinear_bellman.py:158-169]() wraps existing return calculation functions to operate in transformed space.

```mermaid
graph TB
    subgraph "transform_values Decorator Pattern"
        ORIG["Original Function<br/>build_targets(r, γ, V', ...)"]
        DEC["@transform_values<br/>decorator"]
        
        DEC --> WRAP["wrapped_build_targets<br/>(tx_pair, r, γ, V', ...)"]
        
        WRAP --> STEP1["1. Apply tx_pair.apply_inv<br/>to value arguments"]
        STEP1 --> STEP2["2. Call original function<br/>in untransformed space"]
        STEP2 --> STEP3["3. Apply tx_pair.apply<br/>to targets"]
        STEP3 --> RES["Transformed Targets"]
    end
    
    subgraph "Applied to Core Functions"
        WRAP --> TLR["transformed_lambda_returns"]
        WRAP --> TGOP["transformed_general_off_policy_returns"]
        WRAP --> TNS["transformed_n_step_returns"]
    end
```

**Diagram: transform_values Decorator Mechanics**

**Sources:** [rlax/_src/nonlinear_bellman.py:158-169]()

### Transformed Lambda Returns

[rlax/_src/nonlinear_bellman.py:172]() wraps `multistep.lambda_returns`:

```python
transformed_lambda_returns = transform_values(multistep.lambda_returns, 2)
```

The `2` indicates that the value argument (position 2) should be inverse-transformed before computing returns.

### Transformed Q(λ)

The `transformed_q_lambda` function [rlax/_src/nonlinear_bellman.py:179-218]() computes Q(λ) TD errors with value transformations:

```mermaid
graph LR
    subgraph "transformed_q_lambda Flow"
        Q_TM1["Q(s,a)<br/>at t-1"]
        A_TM1["Action a<br/>at t-1"]
        R_T["Rewards r<br/>at t"]
        Q_T["Q(s',a')<br/>at t"]
        
        Q_T --> MAX["max_a Q(s',a)"]
        MAX --> INV["tx_pair.apply_inv<br/>h⁻¹(V')"]
        
        INV --> TLR["transformed_lambda_returns<br/>(tx_pair, r, γ, h⁻¹(V'), λ)"]
        R_T --> TLR
        
        TLR --> TARGET["Transformed Target<br/>h(Target)"]
        
        Q_TM1 --> INDEX["batched_index<br/>Q(s,a)"]
        A_TM1 --> INDEX
        
        TARGET --> ERR["TD Error<br/>h(Target) - Q(s,a)"]
        INDEX --> ERR
    end
```

**Diagram: Transformed Q(λ) Calculation**

**Sources:** [rlax/_src/nonlinear_bellman.py:179-218]()

### Transformed Retrace

The `transformed_retrace` function [rlax/_src/nonlinear_bellman.py:221-268]() implements Retrace with value transformations for off-policy learning:

**Key features:**
- Supports importance sampling with policy ratio `π_t / μ_t`
- Computes trace cutting coefficients `c_t = min(1, π_a / μ) · λ`
- Uses `transformed_general_off_policy_returns_from_action_values`
- Suitable for experience replay and distributed training (as in R2D2)

```mermaid
graph TB
    subgraph "transformed_retrace Components"
        PI["Target Policy π"]
        MU["Behavior Policy μ"]
        
        PI --> IS["Importance Ratio<br/>ρ = π(a|s) / μ(a|s)"]
        MU --> IS
        
        IS --> CLIP["Trace Cutting<br/>c = min(1, ρ) · λ"]
        CLIP --> GOPS["transformed_general_off_policy_returns<br/>(tx_pair, Q, a, r, γ, c, π)"]
        
        GOPS --> TARGET["Transformed Target"]
        
        Q_TM1["Q(s,a) at t-1"]
        TARGET --> ERR["TD Error<br/>Target - Q(s,a)"]
        Q_TM1 --> ERR
    end
```

**Diagram: Transformed Retrace Algorithm**

**Sources:** [rlax/_src/nonlinear_bellman.py:221-268]()

### Transformed N-Step Q-Learning

The `transformed_n_step_q_learning` function [rlax/_src/nonlinear_bellman.py:271-314]() implements n-step TD with transformations:

```mermaid
graph LR
    subgraph "transformed_n_step_q_learning"
        Q_TM1["Q-values<br/>at t-1"]
        TARGET_Q["Target Q-values<br/>at t"]
        A_T["Actions a<br/>for bootstrapping"]
        
        TARGET_Q --> SELECT["batched_index<br/>V = Q(s', a')"]
        A_T --> SELECT
        
        SELECT --> INV["tx_pair.apply_inv<br/>h⁻¹(V)"]
        
        INV --> TNS["transformed_n_step_returns<br/>(tx_pair, r, γ, h⁻¹(V), n)"]
        R["Rewards r"] --> TNS
        
        TNS --> TARG["Transformed Target"]
        
        Q_TM1 --> IDX["batched_index<br/>Q(s,a)"]
        A_TM1["Actions a<br/>at t-1"] --> IDX
        
        TARG --> ERR["N-Step TD Error"]
        IDX --> ERR
    end
```

**Diagram: Transformed N-Step Q-Learning**

**Parameters:**
- `n`: Number of steps for reward accumulation
- Supports double Q-learning when `a_t` comes from online network
- Compatible with target network updates

**Sources:** [rlax/_src/nonlinear_bellman.py:271-314]()

---

## Usage Patterns

### Basic Transformation Example

```python
import rlax

# Define a transformation pair
tx_pair = rlax.SIGNED_HYPERBOLIC_PAIR

# Transform a value
raw_value = 100.0
transformed = tx_pair.apply(raw_value)  # Squashed value
recovered = tx_pair.apply_inv(transformed)  # Should equal raw_value

# Use in learning
q_values = network(state)
target_q = target_network(next_state)

td_error = rlax.transformed_q_lambda(
    q_tm1=q_values,
    a_tm1=actions,
    r_t=rewards,
    discount_t=discounts,
    q_t=target_q,
    lambda_=0.9,
    tx_pair=tx_pair
)
```

### MuZero-Style Transformation

```python
# Create MuZero transformation
muzero_tx = rlax.muzero_pair(
    min_value=-300.0,
    max_value=300.0,
    num_bins=601,
    tx=rlax.SIGNED_HYPERBOLIC_PAIR
)

# Value predictions are now distributions over bins
value_logits = network(state)  # Shape: [..., 601]
value_probs = jax.nn.softmax(value_logits)

# To get scalar value for action selection
scalar_value = muzero_tx.apply_inv(value_probs)

# Compute targets
targets = rlax.transformed_n_step_returns(
    muzero_tx,
    rewards,
    discounts,
    bootstrap_values,
    n=5
)

# Loss is cross-entropy between predicted and target distributions
loss = jax.nn.softmax_cross_entropy_with_logits(value_logits, targets)
```

---

## Relationship to Other RLax Components

```mermaid
graph TB
    subgraph "nonlinear_bellman Dependencies"
        NB["nonlinear_bellman.py"]
        
        NB --> TRANS["transforms.py<br/>Transformation functions"]
        NB --> MS["multistep.py<br/>Return calculations"]
        NB --> BASE["base.py<br/>batched_index, one_hot"]
    end
    
    subgraph "Transformation Usage Flow"
        USER["User Code"]
        
        USER --> CREATE["Create TxPair<br/>(muzero_pair, etc.)"]
        CREATE --> ALGO["Use transformed algorithm<br/>(transformed_q_lambda, etc.)"]
        
        ALGO --> WRAP["Wraps multistep function<br/>via transform_values"]
        WRAP --> CORE["Core return calculation<br/>(lambda_returns, etc.)"]
        
        ALGO --> TX_OPS["Uses transform operations<br/>(apply, apply_inv)"]
        TX_OPS --> TRANS
    end
    
    subgraph "Used By"
        ALGO --> VL["value_learning algorithms"]
        ALGO --> AGENTS["Advanced agents<br/>(MuZero, R2D2)"]
    end
```

**Diagram: Nonlinear Bellman in RLax Architecture**

The nonlinear Bellman module:
- **Depends on**: `transforms.py` for transformation functions, `multistep.py` for base return calculations, `base.py` for array utilities
- **Used by**: Advanced value learning algorithms, agents that require value transformations
- **Provides**: TxPair abstraction, pre-built transformation pairs, transformed versions of core algorithms

**Sources:** [rlax/_src/nonlinear_bellman.py:1-315]()

---

## When to Use Value Transformations

| Scenario | Recommended Transformation | Rationale |
|----------|---------------------------|-----------|
| Unbounded value ranges | `SIGNED_HYPERBOLIC_PAIR` | Provides bounded gradients while preserving ordering |
| Large value magnitudes | `SIGNED_LOGP1_PAIR` | Logarithmic compression prevents overflow |
| Discrete value predictions | `muzero_pair` | Combines squashing with categorical representation |
| Unbiased discrete values | `unbiased_transform_pair` | Removes bias from discretization |
| Stable baseline | `IDENTITY_PAIR` | No transformation (useful for comparison) |
| Custom needs | Compose via `compose_tx` | Chain multiple transformations |

**Guidelines:**
1. Start with `IDENTITY_PAIR` as a baseline
2. If training is unstable due to large values, try `SIGNED_HYPERBOLIC_PAIR`
3. For distributional RL with fixed support, use `muzero_pair`
4. For off-policy learning with replay, combine transformations with `transformed_retrace`
5. Always verify that `tx_pair.apply_inv(tx_pair.apply(x))` recovers `x` accurately

---

## Summary

Value transformations in RLax enable learning in transformed spaces through:

1. **TxPair abstraction**: Clean interface for transformation/inverse pairs
2. **Pre-built transformations**: Ready-to-use squashing and discretization functions
3. **Transformed algorithms**: Drop-in replacements for core RL algorithms
4. **Composition utilities**: Combine transformations for complex behaviors
5. **MuZero support**: Complete implementation of MuZero-style value representations

The key advantage is improved stability and representational capacity when dealing with unbounded or highly variable value estimates, as demonstrated in state-of-the-art algorithms like MuZero and R2D2.

For the actual transformation mathematics, see [Value Transformations](#6.1). For specialized utilities beyond value transformations, see [Specialized Utilities](#6.2).

**Sources:** [rlax/_src/nonlinear_bellman.py:1-315](), [rlax/_src/transforms.py:1-145]()

---

