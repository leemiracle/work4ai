<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/deep-rl-class · page 2 Reinforcement Learning Fundamentals · fetched 2026-10-26 -->

# Reinforcement Learning Fundamentals

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [units/en/unit1/conclusion.mdx](units/en/unit1/conclusion.mdx)
- [units/en/unit1/deep-rl.mdx](units/en/unit1/deep-rl.mdx)
- [units/en/unit1/exp-exp-tradeoff.mdx](units/en/unit1/exp-exp-tradeoff.mdx)
- [units/en/unit1/quiz.mdx](units/en/unit1/quiz.mdx)
- [units/en/unit1/rl-framework.mdx](units/en/unit1/rl-framework.mdx)
- [units/en/unit1/summary.mdx](units/en/unit1/summary.mdx)
- [units/en/unit1/tasks.mdx](units/en/unit1/tasks.mdx)
- [units/en/unit1/two-methods.mdx](units/en/unit1/two-methods.mdx)
- [units/en/unit1/what-is-rl.mdx](units/en/unit1/what-is-rl.mdx)

</details>



This wiki page introduces the core concepts of reinforcement learning (RL) as covered in Unit 1 of the Deep Reinforcement Learning course. It provides a comprehensive explanation of the RL framework, components, and approaches that form the foundation for all subsequent units. For hands-on implementation with the LunarLander environment, see [LunarLander with Stable-Baselines3](#2.1).

## What is Reinforcement Learning?

Reinforcement Learning is a computational approach to learning from actions. An agent learns from the environment by interacting with it through trial and error and receiving rewards (positive or negative) as feedback for performing actions.

```mermaid
graph TD
    A["Agent"] -->|"Takes action"| E["Environment"]
    E -->|"Provides state"| A
    E -->|"Gives reward"| A
    A -->|"Updates knowledge"| A
```

Sources: [units/en/unit1/what-is-rl.mdx:5-40]()

The formal definition:

> Reinforcement learning is a framework for solving control tasks (also called decision problems) by building agents that learn from the environment by interacting with it through trial and error and receiving rewards (positive or negative) as unique feedback.

Unlike supervised learning where models learn from labeled data, RL agents learn optimal behavior through direct interaction with their environment, guided only by the rewards they receive.

## The Reinforcement Learning Framework

### The RL Process

The RL process is a loop that produces a sequence of state, action, reward, and next state:

```mermaid
flowchart LR
    S["State (St)"] --> A["Action (At)"]
    A --> R["Reward (Rt+1)"]
    R --> NS["Next State (St+1)"]
    NS --> A2["Action (At+1)"]
    
    style S fill:#f9f9f9,stroke:#333,stroke-width:1px
    style A fill:#f9f9f9,stroke:#333,stroke-width:1px
    style R fill:#f9f9f9,stroke:#333,stroke-width:1px
    style NS fill:#f9f9f9,stroke:#333,stroke-width:1px
    style A2 fill:#f9f9f9,stroke:#333,stroke-width:1px
```

Let's break down this process:

1. The agent receives a **state** (S₀) from the environment
2. Based on that state, the agent takes an **action** (A₀)
3. The environment transitions to a **new state** (S₁)
4. The environment provides a **reward** (R₁) to the agent

This loop continues, generating sequences of state, action, reward, and next state tuples.

Sources: [units/en/unit1/rl-framework.mdx:3-24]()

### The Reward Hypothesis

The central idea in RL is the reward hypothesis, which states that all goals can be described as the maximization of expected cumulative reward.

The agent's objective is to learn a behavior (policy) that will maximize the expected return (cumulative reward). This is why in reinforcement learning, agents aim to take actions that maximize the expected cumulative reward.

Sources: [units/en/unit1/rl-framework.mdx:26-32]()

### Markov Property

In reinforcement learning, the process is typically modeled as a Markov Decision Process (MDP). The Markov Property implies that the future depends only on the current state and not on the sequence of events that preceded it.

This means our agent needs **only the current state** to decide what action to take, not the history of all states and actions that came before.

Sources: [units/en/unit1/rl-framework.mdx:35-40]()

## Core Components of Reinforcement Learning

### States and Observations

States and observations represent the information the agent receives from the environment.

There's an important distinction between states and observations:

| States | Observations |
|--------|--------------|
| Complete description of the environment | Partial description of the environment |
| No hidden information | May contain hidden information |
| Example: Chess board (fully observable) | Example: Part of a Mario level (partially observable) |

In a fully observed environment (like chess), the agent receives a state. In a partially observed environment (like Super Mario Bros), the agent receives an observation since it only sees part of the level.

```mermaid
graph TD
    subgraph "Information from Environment"
        S["State/Observation"]
    end
    
    subgraph "Fully Observable"
        FS["State (Complete Information)"]
        FS --> CHESS["Example: Chess Board"]
    end
    
    subgraph "Partially Observable"
        PO["Observation (Partial Information)"]
        PO --> MARIO["Example: Mario's Visible Area"]
    end
    
    S --> FS
    S --> PO
```

Sources: [units/en/unit1/rl-framework.mdx:41-74]()

### Action Space

The action space represents all possible actions an agent can take in an environment. Actions can come from either:

1. **Discrete space**: Finite number of possible actions
   - Example: Left, right, up, down in Super Mario Bros

2. **Continuous space**: Infinite number of possible actions
   - Example: Precise steering angles in a self-driving car

Understanding the action space is crucial when selecting an appropriate RL algorithm.

```mermaid
graph TD
    AS["Action Space"] --> DS["Discrete Space (Finite)"]
    AS --> CS["Continuous Space (Infinite)"]
    
    DS --> MARIO["Example: Mario (Left, Right, Jump, Crouch)"]
    CS --> CAR["Example: Self-Driving Car (Infinite steering angles)"]
```

Sources: [units/en/unit1/rl-framework.mdx:76-103]()

### Rewards and Discounting

Rewards are the fundamental feedback mechanism in RL. The agent's goal is to maximize the cumulative reward over time.

Since future rewards are less certain than immediate ones, we use discounting:

- We define a discount factor γ (gamma), typically between 0.95 and 0.99
- Future rewards are multiplied by γᵗ, where t is the time step
- Smaller γ: Agent focuses more on immediate rewards
- Larger γ: Agent values future rewards more

The discounted expected cumulative reward is represented as:

```
R = r₁ + γr₂ + γ²r₃ + ...
```

Sources: [units/en/unit1/rl-framework.mdx:105-144]()

## Types of Tasks

In reinforcement learning, tasks are specific instances of RL problems. They can be categorized into two types:

### Episodic Tasks

Episodic tasks have a clear starting point and ending point (terminal state), creating an episode.

- Example: Super Mario Bros - starts at the beginning of a level, ends when Mario dies or reaches the flagpole
- Each episode provides a complete sequence of experience for learning

### Continuing Tasks

Continuing tasks have no terminal state and continue indefinitely.

- Example: Stock trading bot - operates continuously with no natural endpoint
- The agent must learn while continuously interacting with the environment

```mermaid
graph TD
    T["RL Tasks"] --> E["Episodic Tasks"]
    T --> C["Continuing Tasks"]
    
    E --> GAME["Examples:<br>- Video Games<br>- Board Games"]
    C --> ROBOT["Examples:<br>- Stock Trading<br>- HVAC Control<br>- Continuous Robotics Tasks"]
    
    E --> ES["Has terminal states"]
    C --> CS["No terminal states"]
```

Sources: [units/en/unit1/tasks.mdx:1-27]()

## The Exploration/Exploitation Trade-off

One of the fundamental challenges in reinforcement learning is balancing exploration and exploitation:

- **Exploration**: Trying new actions to discover more about the environment
- **Exploitation**: Using known information to maximize rewards

This trade-off can be understood with a simple example: Imagine a mouse in a maze looking for cheese. There might be small pieces of cheese (+1 reward) in easily accessible areas, but there could be a large pile of cheese (+1000 reward) hidden in a difficult-to-reach area.

If the agent only exploits (always goes for the known small cheese), it will never discover the large reward. But if it explores too much, it might waste time trying random actions when it could be consistently getting smaller rewards.

```mermaid
graph TD
    EE["Exploration/Exploitation<br>Trade-off"] --> EXP["Exploration"]
    EE --> EXL["Exploitation"]
    
    EXP --> ENEW["Trying new actions<br>to discover environment"]
    EXL --> EKNOWN["Using known information<br>to maximize rewards"]
    
    EXP --> ERISK["Risk: Wasted time/resources"]
    EXP --> EREWARD["Potential: Discovering<br>better rewards"]
    
    EXL --> EXRISK["Risk: Missing better<br>opportunities"]
    EXL --> EXREWARD["Potential: Consistent<br>known rewards"]
```

This concept is similar to choosing a restaurant: Do you go to a familiar one you know is good (exploitation) or try a new one that might be better or worse (exploration)?

Sources: [units/en/unit1/exp-exp-tradeoff.mdx:1-37]()

## Approaches to Solve RL Problems

There are two main approaches to solving reinforcement learning problems:

### Policy-Based Methods

Policy-based methods directly learn a policy function π that maps states to actions.

- The policy is the "brain" of the agent, telling it what action to take in each state
- Policies can be:
  - **Deterministic**: For a given state, always returns the same action
  - **Stochastic**: Outputs a probability distribution over actions

```mermaid
graph TD
    PBM["Policy-Based Methods"] --> P["Policy (π)"]
    P --> DP["Deterministic Policy<br>action = π(state)"]
    P --> SP["Stochastic Policy<br>π(actions|state) = probability distribution"]
    
    DP --> DPE["Example: Always move right<br>in state X"]
    SP --> SPE["Example: 70% chance move right,<br>30% chance move left in state X"]
```

Sources: [units/en/unit1/two-methods.mdx:9-65]()

### Value-Based Methods

Value-based methods learn a value function that maps states to the expected value (cumulative reward) of being in that state.

- The value function estimates how good it is to be in a particular state
- The policy is derived from the value function by selecting actions that lead to states with higher values

```mermaid
graph TD
    VBM["Value-Based Methods"] --> V["Value Function V(s)"]
    V --> VS["Value of States"]
    VS --> BEST["Policy: Choose action leading<br>to highest-valued state"]
    
    subgraph "Example Grid World"
        S1["State (-7)"] --> S2["State (-6)"]
        S2 --> S3["State (-5)"]
        S3 --> S4["State (-4)"]
        S4 --> GOAL["Goal (0)"]
    end
```

In this approach, the agent will navigate toward higher-valued states - following the path from -7 to -6 to -5 and so on until reaching the goal.

Sources: [units/en/unit1/two-methods.mdx:68-90]()

## Deep Reinforcement Learning

Deep Reinforcement Learning incorporates deep neural networks into reinforcement learning methods, enhancing their capabilities to handle complex environments with high-dimensional state spaces.

The "Deep" in Deep RL refers to using deep neural networks to:
- Approximate value functions (in value-based methods)
- Directly represent policies (in policy-based methods)

```mermaid
graph TD
    DRL["Deep Reinforcement Learning"] --> VB["Value-Based Methods"]
    DRL --> PB["Policy-Based Methods"]
    
    VB --> DQN["Deep Q-Network (DQN)"]
    DQN --> DQNNN["Neural Network approximates<br>Q-value function"]
    
    PB --> DPG["Deep Policy Gradient"]
    DPG --> DPGNN["Neural Network represents<br>policy directly"]
    
    subgraph "Traditional RL vs. Deep RL"
        TRL["Traditional: Tabular Methods<br>(State-Action tables)"]
        DEEPRL["Deep RL: Neural Networks<br>(Function approximation)"]
    end
```

The advantage of using deep neural networks is their ability to generalize across states and handle environments with large or continuous state spaces where tabular methods would be impractical.

Sources: [units/en/unit1/deep-rl.mdx:1-21]()

## Summary

Reinforcement learning is a computational approach to learning from actions, where agents learn by interacting with their environment through trial and error and receiving rewards as feedback.

Key concepts:
- The RL process is a loop of state, action, reward, and next state
- The goal is to maximize expected cumulative reward (based on the reward hypothesis)
- States represent complete information, observations represent partial information
- Action spaces can be discrete or continuous
- Tasks can be episodic or continuing
- There's a fundamental trade-off between exploration and exploitation
- Two main approaches: policy-based and value-based methods
- Deep RL incorporates neural networks to handle complex environments

The foundations covered in this page will be expanded upon in subsequent units, building from basic Q-Learning [Q-Learning](#3) to Deep Q-Learning [Deep Q-Learning](#4) and more advanced methods.

Sources: [units/en/unit1/summary.mdx:1-19]()

---

