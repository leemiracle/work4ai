<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/blog · page 7 Deep Reinforcement Learning · fetched 2026-10-26 -->

# Deep Reinforcement Learning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [assets/63_deep_rl_intro/tasks.jpg](assets/63_deep_rl_intro/tasks.jpg)
- [assets/70_deep_rl_q_part1/bellman6.jpg](assets/70_deep_rl_q_part1/bellman6.jpg)
- [assets/78_ml_director_insights/witty-works.png](assets/78_ml_director_insights/witty-works.png)
- [assets/86_bloom/bloom-examples.jpg](assets/86_bloom/bloom-examples.jpg)
- [assets/controlnet/thumbnail.png](assets/controlnet/thumbnail.png)
- [assets/cosmopedia/thumbnail.png](assets/cosmopedia/thumbnail.png)
- [bloom.md](bloom.md)
- [classification-use-cases.md](classification-use-cases.md)
- [controlnet.md](controlnet.md)
- [cosmopedia.md](cosmopedia.md)
- [deep-rl-a2c.md](deep-rl-a2c.md)
- [deep-rl-dqn.md](deep-rl-dqn.md)
- [deep-rl-intro.md](deep-rl-intro.md)
- [deep-rl-pg.md](deep-rl-pg.md)
- [deep-rl-ppo.md](deep-rl-ppo.md)
- [deep-rl-q-part1.md](deep-rl-q-part1.md)
- [deep-rl-q-part2.md](deep-rl-q-part2.md)
- [ml-director-insights-2.md](ml-director-insights-2.md)

</details>



## Purpose and Scope

This section provides a comprehensive curriculum for Deep Reinforcement Learning, covering the progression from foundational concepts to advanced algorithms. The material spans value-based methods (Q-Learning, Deep Q-Networks) and policy-based methods (REINFORCE, Actor-Critic, PPO), teaching both theoretical foundations and practical implementations.

For specific Deep RL topics:
- Fundamental RL concepts and Q-Learning → see [Introduction to Deep RL](#7.1)
- Policy gradient and actor-critic methods → see [Policy Gradient Methods](#7.2)
- Practical applications of RL → see [RL Applications](#7.3)

For related ML topics:
- Training and fine-tuning LLMs → see [Training and Fine-tuning LLMs](#2.2)
- RLHF and reward models → see [Reinforcement Learning from Human Feedback](#4.3)

Sources: [deep-rl-intro.md](), [deep-rl-q-part1.md](), [deep-rl-dqn.md](), [deep-rl-pg.md](), [deep-rl-a2c.md](), [deep-rl-ppo.md]()

## Curriculum Architecture

The Deep RL curriculum follows a structured progression from basic concepts to advanced implementations, organized into distinct learning units.

```mermaid
graph TB
    subgraph "Unit 1: Foundations"
        U1["deep-rl-intro.md<br/>RL Framework & Basics"]
    end
    
    subgraph "Unit 2: Value-Based Methods"
        U2A["deep-rl-q-part1.md<br/>Q-Learning Theory"]
        U2B["deep-rl-q-part2.md<br/>Q-Learning Implementation"]
    end
    
    subgraph "Unit 3: Deep Q-Learning"
        U3["deep-rl-dqn.md<br/>DQN, Experience Replay<br/>Fixed Q-Target"]
    end
    
    subgraph "Unit 5: Policy Gradients"
        U5["deep-rl-pg.md<br/>REINFORCE Algorithm"]
    end
    
    subgraph "Unit 7: Actor-Critic"
        U7["deep-rl-a2c.md<br/>A2C Hybrid Methods"]
    end
    
    subgraph "Unit 8: Advanced Policy"
        U8["deep-rl-ppo.md<br/>PPO Clipped Objective"]
    end
    
    U1 --> U2A
    U2A --> U2B
    U2B --> U3
    U1 --> U5
    U5 --> U7
    U7 --> U8
    
    U3 -.alternative path.-> U5
```

**Curriculum Progression**

| Unit | Topic | Key Concepts | Implementation |
|------|-------|--------------|----------------|
| 1 | RL Basics | Markov Property, Reward Hypothesis, Exploration vs Exploitation | LunarLander environment |
| 2 | Q-Learning | Q-Table, Bellman Equation, TD Learning | FrozenLake, Taxi environments |
| 3 | Deep Q-Networks | Neural Network Q-Function, Experience Replay | Atari games (Space Invaders) |
| 5 | Policy Gradients | REINFORCE, Stochastic Policies | CartPole, PixelCopter, Pong |
| 7 | Actor-Critic | Advantage Function, Variance Reduction | PyBullet robotics environments |
| 8 | PPO | Clipped Surrogate Objective, Stable Updates | CartPole, LunarLander |

Sources: [deep-rl-intro.md:1-76](), [deep-rl-q-part1.md:1-52](), [deep-rl-dqn.md:1-54](), [deep-rl-pg.md:1-49](), [deep-rl-a2c.md:1-51](), [deep-rl-ppo.md:1-60]()

## Core RL Framework

### The Reinforcement Learning Loop

The fundamental RL process operates as a continuous interaction loop between an agent and its environment.

```mermaid
graph LR
    Agent["Agent<br/>(Policy π)"]
    Env["Environment"]
    
    Agent -->|"Action A_t"| Env
    Env -->|"State S_t"| Agent
    Env -->|"Reward R_t"| Agent
    
    Agent -.internal.-> QFunc["Q-Function or<br/>Policy Network"]
```

**Core Components:**

- **State (S_t)**: Complete or partial description of the environment at time t
- **Action (A_t)**: Decision made by the agent based on current state
- **Reward (R_t+1)**: Feedback signal indicating quality of action
- **Policy (π)**: Function mapping states to actions or action probability distributions
- **Value Function**: Estimates expected cumulative reward from a state

**Key Properties:**

The **Markov Property** states that the current state contains all necessary information for decision-making, without requiring the full history of past states and actions. This enables efficient learning algorithms that operate on state transitions.

The **Reward Hypothesis** posits that all goals can be formulated as maximization of expected cumulative reward, providing a universal optimization objective.

Sources: [deep-rl-intro.md:143-187](), [deep-rl-q-part1.md:64-76]()

### Action and Observation Spaces

RL environments are characterized by their action and observation spaces:

**Discrete Action Spaces**: Finite set of possible actions (e.g., {up, down, left, right, jump} in platformers)

**Continuous Action Spaces**: Infinite action possibilities (e.g., steering angle in self-driving cars can be any value between -180° and +180°)

**Fully Observable**: Agent receives complete state information (e.g., chess board)

**Partially Observable**: Agent receives limited observations (e.g., first-person view in video games)

Sources: [deep-rl-intro.md:188-253]()

## Value-Based Methods

Value-based methods learn to estimate the value of states or state-action pairs, then derive a policy by selecting actions with highest estimated values.

### Q-Learning Fundamentals

Q-Learning trains a **Q-Function** that outputs the expected cumulative reward for taking action `a` in state `s`. The Q-Function uses a **Q-Table** for tabular environments where each cell stores the value Q(s,a).

```mermaid
graph TB
    State["State s_t"] --> QTable["Q-Table<br/>(State-Action Values)"]
    Action["Action a_t"] --> QTable
    QTable --> QValue["Q(s_t, a_t)<br/>Expected Return"]
    
    QValue --> Policy["ε-Greedy Policy"]
    Policy --> Decision{"Random < ε?"}
    Decision -->|Yes| Explore["Random Action<br/>(Exploration)"]
    Decision -->|No| Exploit["argmax_a Q(s,a)<br/>(Exploitation)"]
```

**Bellman Equation for Q-Learning:**

The Q-value update uses the Bellman equation to incorporate immediate reward and discounted future value:

```
Q(S_t, A_t) ← Q(S_t, A_t) + α[R_t+1 + γ max_a Q(S_t+1, a) - Q(S_t, A_t)]
```

Where:
- `α` = learning rate
- `γ` = discount factor (typically 0.95-0.99)
- `R_t+1` = immediate reward
- `max_a Q(S_t+1, a)` = best Q-value in next state

**Key Characteristics:**

- **Off-policy**: Uses different policies for acting (ε-greedy) and updating (greedy)
- **Temporal Difference (TD)**: Updates after each step rather than waiting for episode completion
- **Bootstrap**: Estimates Q-values using other estimated Q-values

Sources: [deep-rl-q-part1.md:95-192](), [deep-rl-q-part2.md:50-220]()

### Deep Q-Networks (DQN)

For large or continuous state spaces, Q-Tables become infeasible. Deep Q-Learning replaces the Q-Table with a neural network that approximates Q-values.

**DQN Architecture:**

```mermaid
graph LR
    subgraph "Input Processing"
        Frame1["Frame t-3"]
        Frame2["Frame t-2"]
        Frame3["Frame t-1"]
        Frame4["Frame t"]
    end
    
    Stack["Stacked Frames<br/>84x84x4"]
    
    subgraph "Deep Q-Network"
        Conv1["Conv Layer 1"]
        Conv2["Conv Layer 2"]
        Conv3["Conv Layer 3"]
        FC1["Fully Connected 1"]
        FC2["Fully Connected 2"]
    end
    
    Output["Q-values for<br/>each action"]
    
    Frame1 --> Stack
    Frame2 --> Stack
    Frame3 --> Stack
    Frame4 --> Stack
    
    Stack --> Conv1
    Conv1 --> Conv2
    Conv2 --> Conv3
    Conv3 --> FC1
    FC1 --> FC2
    FC2 --> Output
```

**Critical DQN Improvements:**

1. **Experience Replay**: Stores transitions `(s, a, r, s')` in a replay buffer, then samples random mini-batches for training. This breaks correlations between consecutive samples and enables reuse of experiences.

2. **Fixed Q-Target**: Uses a separate target network with frozen parameters for computing TD targets, updated every C steps. This stabilizes training by preventing the target from moving during updates.

3. **Double DQN**: Decouples action selection (using main network) from Q-value estimation (using target network) to reduce overestimation bias.

**Preprocessing Steps:**
- Grayscale conversion (RGB → single channel)
- Resize to 84x84 pixels
- Stack 4 consecutive frames to capture temporal information
- Frame skipping to reduce computational cost

Sources: [deep-rl-dqn.md:55-229]()

## Policy-Based Methods

Policy-based methods directly optimize the policy function without learning value functions as intermediaries. They output probability distributions over actions.

### REINFORCE Algorithm

REINFORCE (Monte Carlo Policy Gradient) uses complete episode returns to update policy parameters θ through gradient ascent.

```mermaid
graph TB
    subgraph "Episode Collection"
        Start["Initial State s_0"]
        Action["Sample action a_t ~ π_θ(a|s_t)"]
        Env["Environment Step"]
        Next["New state s_t+1, reward r_t+1"]
        
        Start --> Action
        Action --> Env
        Env --> Next
        Next -.continue.-> Action
    end
    
    subgraph "Policy Update"
        Trajectory["Episode τ = (s_0,a_0,r_1,...,s_T)"]
        Return["Calculate Return R(τ)"]
        Gradient["∇_θ log π_θ(a_t|s_t) × R(τ)"]
        Update["θ ← θ + α∇_θ J(θ)"]
        
        Next --> Trajectory
        Trajectory --> Return
        Return --> Gradient
        Gradient --> Update
    end
```

**Policy Gradient Theorem:**

The gradient of the expected return is:

```
∇_θ J(θ) = E[∇_θ log π_θ(a_t|s_t) × R(τ)]
```

**Advantages over Value-Based:**
- Can learn stochastic policies
- Effective in high-dimensional or continuous action spaces
- No perceptual aliasing issues
- Simpler integration (no separate value function storage)

**Disadvantages:**
- High variance in gradient estimates
- Sample inefficiency (requires many episodes)
- Can converge to local optima
- Slower convergence than value-based methods

Sources: [deep-rl-pg.md:51-183]()

### Actor-Critic Methods (A2C)

Actor-Critic combines value-based and policy-based approaches to reduce variance while maintaining policy optimization.

```mermaid
graph TB
    State["State s_t"]
    
    subgraph "Actor (Policy)"
        Actor["π_θ(a|s)<br/>Policy Network"]
        ActorOut["Action a_t"]
    end
    
    subgraph "Critic (Value)"
        Critic["V_w(s) or Q_w(s,a)<br/>Value Network"]
        CriticOut["Value Estimate"]
    end
    
    State --> Actor
    State --> Critic
    Actor --> ActorOut
    Critic --> CriticOut
    
    ActorOut --> Env["Environment"]
    Env --> Reward["Reward r_t+1"]
    Env --> NextState["State s_t+1"]
    
    Reward --> Advantage["Advantage A(s,a)<br/>= R + γV(s') - V(s)"]
    CriticOut --> Advantage
    NextState --> Advantage
    
    Advantage --> ActorUpdate["Update Actor:<br/>∇_θ log π × A(s,a)"]
    Advantage --> CriticUpdate["Update Critic:<br/>Minimize TD Error"]
```

**Advantage Function:**

The advantage measures how much better an action is compared to the average:

```
A(s,a) = Q(s,a) - V(s) ≈ r + γV(s') - V(s)
```

This is estimated using the TD error, avoiding the need to learn both Q and V functions explicitly.

**Training Process:**
1. Actor selects action based on current policy
2. Critic evaluates the state value
3. Execute action, observe reward and next state
4. Calculate advantage using TD error
5. Update actor to increase probability of actions with positive advantage
6. Update critic to better estimate state values

Sources: [deep-rl-a2c.md:54-152]()

### Proximal Policy Optimization (PPO)

PPO improves upon basic policy gradient methods by constraining policy updates to prevent destructive large changes.

**Clipped Surrogate Objective:**

```mermaid
graph TB
    subgraph "Probability Ratio"
        OldPolicy["π_old(a|s)"]
        NewPolicy["π_θ(a|s)"]
        Ratio["r(θ) = π_θ(a|s) / π_old(a|s)"]
        
        NewPolicy --> Ratio
        OldPolicy --> Ratio
    end
    
    subgraph "Clipped Objective"
        Unclipped["r(θ) × A(s,a)"]
        Clipped["clip(r(θ), 1-ε, 1+ε) × A(s,a)"]
        Min["L^CLIP = min(unclipped, clipped)"]
        
        Ratio --> Unclipped
        Ratio --> Clipped
        Unclipped --> Min
        Clipped --> Min
    end
    
    Advantage["Advantage A(s,a)"] --> Unclipped
    Advantage --> Clipped
```

**Objective Function:**

```
L^CLIP(θ) = E[min(r_t(θ)A_t, clip(r_t(θ), 1-ε, 1+ε)A_t)]
```

Where `ε` is typically 0.2, creating a trust region `[0.8, 1.2]` for the probability ratio.

**Clipping Behavior:**

| Scenario | Advantage Sign | Ratio Range | Effect |
|----------|----------------|-------------|--------|
| Good action, increased probability | Positive | > 1+ε | Clipped - prevents excessive increase |
| Good action, moderate change | Positive | [1-ε, 1+ε] | Unclipped - allows increase |
| Bad action, decreased probability | Negative | < 1-ε | Clipped - prevents excessive decrease |
| Bad action, moderate change | Negative | [1-ε, 1+ε] | Unclipped - allows decrease |

The clipping ensures stable training by:
- Preventing catastrophically large policy updates
- Maintaining proximity between old and new policies
- Enabling multiple epochs of optimization on the same batch

Sources: [deep-rl-ppo.md:62-176]()

## Method Comparison and Selection

### Taxonomy of RL Algorithms

```mermaid
graph TB
    RL["Reinforcement Learning<br/>Methods"]
    
    subgraph "Value-Based"
        VB["Learn V(s) or Q(s,a)<br/>Derive policy implicitly"]
        QLearning["Q-Learning<br/>Tabular, Off-policy"]
        DQN["Deep Q-Network<br/>Neural Net approximation"]
        
        VB --> QLearning
        VB --> DQN
    end
    
    subgraph "Policy-Based"
        PB["Learn π(a|s) directly<br/>No value function"]
        REINFORCE["REINFORCE<br/>Monte Carlo gradients"]
        
        PB --> REINFORCE
    end
    
    subgraph "Actor-Critic (Hybrid)"
        AC["Learn both π(a|s) and V(s)<br/>Combine advantages"]
        A2C["A2C<br/>Advantage-based updates"]
        PPO["PPO<br/>Clipped updates"]
        
        AC --> A2C
        AC --> PPO
    end
    
    RL --> VB
    RL --> PB
    RL --> AC
```

### Algorithm Selection Guide

| Criterion | Q-Learning | DQN | REINFORCE | A2C | PPO |
|-----------|------------|-----|-----------|-----|-----|
| **State Space** | Small, discrete | Large, continuous | Any | Any | Any |
| **Action Space** | Small, discrete | Small, discrete | Any | Any | Any |
| **Sample Efficiency** | Moderate | High (replay) | Low | Moderate | Moderate |
| **Stability** | High | Moderate | Low (high variance) | Moderate | High |
| **Convergence Speed** | Fast (small spaces) | Moderate | Slow | Moderate | Moderate |
| **Implementation** | Simple | Complex | Moderate | Complex | Complex |
| **Memory Requirements** | Low (Q-table) | High (replay buffer) | Low | Moderate | Moderate |
| **Best For** | Grid worlds, simple games | Atari, visual inputs | Continuous control | Robotics | General purpose |

Sources: [deep-rl-intro.md:379-519](), [deep-rl-q-part2.md:185-220](), [deep-rl-pg.md:82-136](), [deep-rl-a2c.md:54-97](), [deep-rl-ppo.md:62-87]()

## Implementation Details

### Training Loop Components

Common elements across all Deep RL implementations:

```mermaid
graph TB
    subgraph "Environment Interaction"
        Env["gym.make(env_name)"]
        Reset["env.reset()"]
        Step["env.step(action)"]
        Obs["observation, reward, done"]
        
        Reset --> Step
        Step --> Obs
        Obs -.next step.-> Step
    end
    
    subgraph "Model Components"
        Model["Neural Network<br/>(Q-Network or Policy)"]
        Optim["Optimizer<br/>(Adam, RMSprop)"]
        Loss["Loss Function<br/>(MSE, Policy Gradient)"]
    end
    
    subgraph "Training Infrastructure"
        Buffer["Experience Buffer<br/>(for off-policy)"]
        Target["Target Network<br/>(for DQN)"]
        Scheduler["Learning Rate Scheduler"]
    end
    
    Obs --> Buffer
    Buffer --> Model
    Model --> Loss
    Loss --> Optim
    Optim -.updates.-> Model
```

**Common Hyperparameters:**

- **Learning Rate (α)**: Typically 0.0001 - 0.001 for deep networks
- **Discount Factor (γ)**: Usually 0.95 - 0.99
- **Batch Size**: 32 - 256 for DQN, 64 - 2048 for PPO
- **Epsilon Decay**: Start 1.0, decay to 0.01 - 0.1 for exploration
- **Network Architecture**: 2-3 hidden layers, 64-256 units each
- **Target Update Frequency**: Every 1000 - 10000 steps (DQN)
- **Clip Range (ε)**: 0.1 - 0.3 for PPO

### Exploration Strategies

**ε-Greedy (for Q-Learning, DQN):**
```
if random() < ε:
    action = random_action()  # Exploration
else:
    action = argmax(Q(s, a))  # Exploitation
```

**Stochastic Policies (for Policy Gradients):**
Actions sampled from learned probability distributions provide inherent exploration without manual ε scheduling.

Sources: [deep-rl-q-part2.md:116-181](), [deep-rl-dqn.md:87-229](), [deep-rl-pg.md:143-183]()

## Training Environments

The curriculum uses progressively challenging environments to demonstrate different algorithms:

| Environment | State Space | Action Space | Algorithm Units | Difficulty |
|-------------|-------------|--------------|-----------------|------------|
| FrozenLake-v1 | 16 discrete | 4 discrete | Q-Learning | Beginner |
| Taxi-v3 | 500 discrete | 6 discrete | Q-Learning | Beginner |
| CartPole-v1 | 4 continuous | 2 discrete | DQN, REINFORCE, PPO | Intermediate |
| LunarLander-v2 | 8 continuous | 4 discrete | DQN, PPO | Intermediate |
| Space Invaders (Atari) | 210×160×3 pixels | 6 discrete | DQN | Advanced |
| PixelCopter | Visual | 2 discrete | REINFORCE | Advanced |
| Pong (Atari) | 210×160×3 pixels | 6 discrete | REINFORCE | Advanced |
| PyBullet Robotics | High-dim continuous | Continuous | A2C | Advanced |

**Environment Characteristics:**

- **Discrete vs Continuous**: Affects algorithm selection (Q-Learning only for discrete)
- **Visual vs Low-dimensional**: Visual requires CNN preprocessing
- **Sparse vs Dense Rewards**: Affects learning difficulty and required techniques
- **Deterministic vs Stochastic**: Influences variance in learning

Sources: [deep-rl-q-part2.md:29-36](), [deep-rl-dqn.md:37-42](), [deep-rl-pg.md:38-41](), [deep-rl-a2c.md:37-42](), [deep-rl-ppo.md:36-45]()

## Monte Carlo vs Temporal Difference Learning

A fundamental distinction in RL is how value estimates are updated:

**Monte Carlo (MC) Learning:**
- Waits until episode completion
- Updates using actual observed return G_t
- Unbiased estimates but high variance
- Used in REINFORCE

**Temporal Difference (TD) Learning:**
- Updates after each step
- Uses bootstrapped estimate: r + γV(s')
- Biased but lower variance
- Used in Q-Learning, DQN, A2C, PPO

```mermaid
graph LR
    subgraph "Monte Carlo"
        MC_Start["Episode Start"]
        MC_Actions["Execute Actions"]
        MC_End["Episode End"]
        MC_Calc["G_t = Σ γ^k r_t+k"]
        MC_Update["Update V(s_0)"]
        
        MC_Start --> MC_Actions
        MC_Actions --> MC_End
        MC_End --> MC_Calc
        MC_Calc --> MC_Update
    end
    
    subgraph "Temporal Difference"
        TD_State["State s_t"]
        TD_Action["Take Action"]
        TD_Next["Observe r, s_t+1"]
        TD_Update["V(s_t) ← V(s_t) + α[r + γV(s_t+1) - V(s_t)]"]
        
        TD_State --> TD_Action
        TD_Action --> TD_Next
        TD_Next --> TD_Update
        TD_Update -.next step.-> TD_State
    end
```

**Variance-Bias Tradeoff:**
- MC: No bias (uses true returns) but high variance (single trajectory)
- TD: Biased (uses estimates) but lower variance (leverages learned values)

Sources: [deep-rl-q-part1.md:256-424]()

## Performance and Optimization

### Stability Techniques

Deep RL training can be unstable. Key stabilization techniques:

1. **Experience Replay** (DQN): Break temporal correlations
2. **Target Networks** (DQN): Stabilize bootstrapping targets
3. **Advantage Normalization** (A2C, PPO): Reduce gradient variance
4. **Clipped Updates** (PPO): Prevent catastrophic policy changes
5. **Gradient Clipping**: Prevent exploding gradients in recurrent policies
6. **Reward Scaling**: Normalize reward ranges for stable learning

### Computational Considerations

**Memory Requirements:**
- Q-Learning: O(|S| × |A|) for Q-table
- DQN: Replay buffer typically 100K - 1M transitions
- Policy Gradients: Episode storage, much smaller than DQN

**Training Time:**
- Simple environments: Minutes to hours
- Atari games: Hours to days on GPUs
- Robotics: Days to weeks with parallelization

**Parallelization:**
- A2C/A3C: Multiple environments in parallel
- PPO: Vectorized environments, batch processing
- DQN: Harder to parallelize due to replay buffer synchronization

Sources: [deep-rl-dqn.md:138-229](), [deep-rl-a2c.md:54-76](), [deep-rl-ppo.md:62-156]()

---

