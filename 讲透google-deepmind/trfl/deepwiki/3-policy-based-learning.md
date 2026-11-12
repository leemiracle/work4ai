<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/trfl · page 3 Policy-Based Learning · fetched 2026-10-26 -->

# Policy-Based Learning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/multistep_forward_view.md](docs/multistep_forward_view.md)
- [docs/trfl.md](docs/trfl.md)
- [trfl/discrete_policy_gradient_ops.py](trfl/discrete_policy_gradient_ops.py)
- [trfl/policy_gradient_ops.py](trfl/policy_gradient_ops.py)

</details>



## Purpose and Scope

This page provides an overview of policy-based reinforcement learning methods implemented in the TRFL library. Policy-based methods directly learn a policy function that maps states to actions (or action probabilities), in contrast to [Value-Based Learning](#2) which learns value functions and derives policies from them. This document covers the core policy gradient algorithms for both discrete and continuous action spaces, actor-critic methods, and deterministic policy gradient implementations.

For off-policy correction methods like V-trace that can be used with policy-based algorithms, see [Off-Policy Learning Methods](#4).

## Overview of Policy-Based Learning in TRFL

Policy-based learning in TRFL provides operations to optimize policies directly using gradient ascent on the expected return. The library supports:

1. **Stochastic Policy Gradients** - For both continuous and discrete action spaces
2. **Actor-Critic Methods** - Combining policy gradients with value function learning
3. **Deterministic Policy Gradient** - Direct optimization of deterministic policies

The implementations follow a modular approach where lower-level operations can be combined to create complete algorithms.

```mermaid
flowchart TD
    PBL["Policy-Based Learning"]
    DPG["Deterministic Policy Gradient"]
    SPG["Stochastic Policy Gradients"]
    AC["Actor-Critic Methods"]
    
    PBL --> SPG
    PBL --> AC
    PBL --> DPG
    
    SPG --> CAPG["Continuous Action\npolicy_gradient()"]
    SPG --> DAPG["Discrete Action\ndiscrete_policy_gradient()"]
    
    AC --> A2C["Advantage Actor-Critic\nsequence_a2c_loss()"]
    AC --> DAAC["Discrete A2C\nsequence_advantage_actor_critic_loss()"]
    
    CAPG -.-> EP["Entropy Penalties\npolicy_entropy_loss()"]
    DAPG -.-> DEP["Discrete Entropy Penalties\ndiscrete_policy_entropy_loss()"]
```

Sources: [trfl/policy_gradient_ops.py](), [trfl/discrete_policy_gradient_ops.py](), [docs/trfl.md:365-371]()

## Policy Gradient Methods

Policy gradient methods optimize a parameterized policy by directly adjusting the policy parameters in the direction of the gradient of expected return. TRFL implements policy gradients for both continuous and discrete action spaces.

### Continuous Action Spaces

For continuous action spaces, TRFL provides implementations that work with probability distributions over actions.

```mermaid
flowchart LR
    PG["policy_gradient()"]
    PGL["policy_gradient_loss()"]
    DIST["Distribution\nSupporting log_prob()"]
    
    PG --> PGL
    PGL --> ACT["Actions\nShape: [T,B,...]"]
    PGL --> POL["Policies (Distributions)\nShape: [T,B]"]
    PGL --> AV["Action Values\nShape: [T,B]"]
    
    POL --> DIST
    DIST --> LP["log_prob() method"]
```

Key operations:

- `policy_gradient`: Computes basic policy gradient losses for a batch of trajectories
- `policy_gradient_loss`: Handles nested action spaces and sums losses across time dimensions

These operations implement the policy gradient theorem, calculating gradients of the form:
- log_prob(action) * advantage_value

Sources: [trfl/policy_gradient_ops.py:39-74](), [trfl/policy_gradient_ops.py:77-105](), [docs/trfl.md:827-892]()

### Discrete Action Spaces

For discrete action spaces, TRFL provides implementations that work with categorical distributions represented by logits.

```mermaid
flowchart LR
    DPG["discrete_policy_gradient()"]
    DPGL["discrete_policy_gradient_loss()"]
    
    DPG --> DPGL
    DPGL --> ACT["Actions (Indices)\nShape: [T,B]"]
    DPGL --> POL["Policy Logits\nShape: [T,B,num_actions]"]
    DPGL --> AV["Action Values\nShape: [T,B]"]
```

Key operations:

- `discrete_policy_gradient`: Computes policy gradient losses for discrete action spaces
- `discrete_policy_gradient_loss`: Handles nested action spaces and sums losses across time dimensions

These implementations use `tf.nn.sparse_softmax_cross_entropy_with_logits` to efficiently compute the negative log probabilities of chosen actions.

Sources: [trfl/discrete_policy_gradient_ops.py:223-276](), [trfl/discrete_policy_gradient_ops.py:279-327](), [docs/trfl.md:212-329]()

## Entropy Regularization

Both continuous and discrete policy gradient implementations support entropy regularization, which encourages exploration by penalizing low-entropy policies.

For continuous action spaces:
- `policy_entropy_loss`: Calculates entropy 'loss' for policies represented by distributions
  
For discrete action spaces:
- `discrete_policy_entropy_loss`: Computes entropy 'loss' for a batch of policy logits

The entropy loss is scaled by a negative constant to make it a minimization objective when combined with the policy gradient loss. Both implementations support optional normalization to make the entropy loss invariant to the action space size.

Sources: [trfl/policy_gradient_ops.py:137-196](), [trfl/discrete_policy_gradient_ops.py:42-95](), [docs/trfl.md:212-248](), [docs/trfl.md:779-825]()

## Actor-Critic Methods

Actor-critic methods combine policy-based learning (the actor) with value function estimation (the critic) to reduce variance in policy updates. TRFL implements advantage actor-critic methods:

```mermaid
flowchart TD
    AC["Actor-Critic Methods"]
    
    AC --> CA2C["Continuous A2C\nsequence_a2c_loss()"]
    AC --> DA2C["Discrete A2C\nsequence_advantage_actor_critic_loss()"]
    
    CA2C --> PG["Policy Gradient\npolicy_gradient_loss()"]
    CA2C --> TD["TD Lambda\ntd_lambda()"]
    CA2C --> ENT["Entropy\npolicy_entropy_loss()"]
    
    DA2C --> DPG["Discrete Policy Gradient\ndiscrete_policy_gradient_loss()"]
    DA2C --> TD
    DA2C --> DENT["Discrete Entropy\ndiscrete_policy_entropy_loss()"]
    
    TD --> ADV["advantages\n= temporal_differences"]
    TD --> RET["discounted_returns"]
```

Key operations:

- `sequence_a2c_loss`: Implements advantage actor-critic for continuous action spaces
- `sequence_advantage_actor_critic_loss`: Implements advantage actor-critic for discrete action spaces

Both implementations:
1. Calculate advantages using TD(λ) error
2. Use these advantages for policy gradient updates
3. Train the value function toward n-step returns
4. Optionally add entropy regularization

The advantage actor-critic implementations support Generalized Advantage Estimation (GAE) through the lambda parameter.

Sources: [trfl/policy_gradient_ops.py:199-341](), [trfl/discrete_policy_gradient_ops.py:98-219](), [docs/trfl.md:199-211](), [docs/multistep_forward_view.md]()

## Deterministic Policy Gradient

While stochastic policy gradients learn a probability distribution over actions, the Deterministic Policy Gradient (DPG) algorithm directly learns a deterministic policy that outputs the optimal action.

```mermaid
flowchart LR
    DPG["dpg()"]
    
    DPG --> QMAX["q_max: Q-values\nShape: [B]"]
    DPG --> AMAX["a_max: Optimal actions\nShape: [B, action_dimension]"]
    DPG --> CLIP["dqda_clipping: Optional\ngradient clipping"]
    
    DPG --> LOSS["loss = -dq/da * a_max"]
```

The DPG implementation in TRFL:
1. Receives Q-values and optimal actions
2. Computes the gradients of Q-values with respect to actions (dq/da)
3. Optionally applies clipping to these gradients
4. Returns the loss which can be minimized to update the policy

This algorithm is the foundation for DDPG (Deep Deterministic Policy Gradient) and other actor-critic algorithms for continuous action spaces.

Sources: [docs/trfl.md:366-402]()

## Implementation Considerations

### Input/Output Tensor Shapes

Most policy-based learning operations in TRFL follow a consistent convention for tensor shapes:
- Time dimension first: `[T, ...]`
- Batch dimension second: `[T, B, ...]`
- Additional dimensions specific to the operation type

For example, policy logits for discrete action spaces typically have shape `[T, B, num_actions]`, while actions have shape `[T, B]`.

### Nested Structures Support

TRFL policy operations support nested structures of inputs to handle:
1. Multiple action dimensions
2. Multiple distribution types 
3. Independent multivariate distributions

This allows for complex policies that might produce actions across different spaces or dimensions.

### Integration with TensorFlow

All policy-based learning operations are implemented as differentiable TensorFlow operations, enabling them to be incorporated into larger computation graphs and trained using standard optimizers.

## Usage Pattern

A typical usage pattern for policy-based learning in TRFL follows these steps:

1. Define policy network(s) that output policy parameters (logits, means, etc.)
2. Define value network(s) that estimate state or action values
3. Use TRFL operations to compute losses from trajectories of experience
4. Update networks using TensorFlow optimizers

For example, to implement Advantage Actor-Critic with a discrete action space:

```
# Compute A2C loss
loss_output = trfl.sequence_advantage_actor_critic_loss(
    policy_logits=policy_logits,
    baseline_values=baseline_values,
    actions=actions,
    rewards=rewards,
    pcontinues=discounts,
    bootstrap_value=bootstrap_value,
    lambda_=lambda_param,
    entropy_cost=entropy_cost)

# Extract total loss
total_loss = loss_output.loss

# Use optimizer to update network parameters
optimizer.minimize(total_loss)
```

Sources: [trfl/policy_gradient_ops.py](), [trfl/discrete_policy_gradient_ops.py]()

---

