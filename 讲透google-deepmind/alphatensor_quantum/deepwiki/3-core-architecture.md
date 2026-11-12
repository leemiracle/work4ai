<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphatensor_quantum · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/demo/agent.py](src/demo/agent.py)
- [src/environment.py](src/environment.py)
- [src/networks.py](src/networks.py)

</details>



This document explains the main architectural components of the AlphaTensor-Quantum reinforcement learning system and how they work together in the training pipeline. The core architecture consists of three primary subsystems: the Agent system for RL orchestration, the Environment system for quantum circuit decomposition games, and the Neural Network system for policy and value prediction.

For detailed information about individual components, see [Agent System](#3.1), [Environment System](#3.2), and [Neural Networks](#3.3). For mathematical foundations underlying these components, see [Mathematical Foundations](#4).

## System Overview

The AlphaTensor-Quantum system implements a reinforcement learning approach to quantum circuit optimization using Monte Carlo Tree Search (MCTS) and neural networks. The architecture follows the AlphaZero paradigm, adapted for the specific domain of tensor decomposition games.

### Main Component Architecture

```mermaid
graph TB
    subgraph "Core RL Pipeline"
        Agent["Agent<br/>(agent.py)"]
        Environment["Environment<br/>(environment.py)"]
        TorsoNetwork["TorsoNetwork<br/>(networks.py)"]
    end
    
    subgraph "Key Data Structures"
        RunState["RunState<br/>- params<br/>- env_states<br/>- demonstrations<br/>- opt_state<br/>- game_stats"]
        EnvState["EnvState<br/>- tensor<br/>- past_factors<br/>- num_moves<br/>- is_terminal<br/>- last_reward"]
        Observation["Observation<br/>- tensor<br/>- past_factors_as_planes<br/>- sqrt_played_fraction"]
    end
    
    subgraph "External Dependencies"
        MCTX["mctx.muzero_policy<br/>(MCTS Implementation)"]
        Optax["optax<br/>(Optimizer)"]
        JAX["JAX/Haiku<br/>(ML Framework)"]
    end
    
    Agent --> RunState
    Agent --> Environment
    Agent --> TorsoNetwork
    Agent --> MCTX
    Agent --> Optax
    
    Environment --> EnvState
    Environment --> Observation
    
    TorsoNetwork --> JAX
    RunState --> EnvState
    EnvState --> Observation
    
    MCTX --> Agent
    Environment --> Agent
    TorsoNetwork --> Agent
```

**Sources:** [src/demo/agent.py:54-73](), [src/environment.py:33-62](), [src/environment.py:65-76](), [src/networks.py:256-272]()

## Training Pipeline Data Flow

The training pipeline orchestrates the interaction between acting (gameplay), learning (neural network updates), and synthetic demonstrations. The `Agent` class manages this entire pipeline through its `run_agent_env_interaction` method.

### RL Training Loop Architecture

```mermaid
flowchart TD
    InitRunState["init_run_state()<br/>Initialize RunState"]
    
    subgraph "Training Iteration Loop"
        GetObs["env.get_observation()<br/>Extract Observations"]
        NetworkForward["network.apply()<br/>Policy + Value Prediction"]
        MCTS["mctx.muzero_policy()<br/>Tree Search"]
        SelectAction["jax.random.choice()<br/>Action Selection"]
        EnvStep["env.step()<br/>Apply Action"]
        UpdateStats["_update_game_stats()<br/>Track Performance"]
        
        subgraph "Loss Computation"
            ActingLoss["Acting Loss<br/>Policy + Value"]
            DemoLoss["Demonstration Loss<br/>Synthetic Data"]
            CombinedLoss["Combined Loss<br/>Weighted Sum"]
        end
        
        OptUpdate["opt.update()<br/>Parameter Update"]
        
        subgraph "State Management"
            ResetEnv["Reset if Terminal<br/>New Episodes"]
            UpdateDemo["Update Demonstrations<br/>Synthetic Data Refresh"]
        end
    end
    
    InitRunState --> GetObs
    GetObs --> NetworkForward
    NetworkForward --> MCTS
    MCTS --> SelectAction
    SelectAction --> EnvStep
    EnvStep --> UpdateStats
    
    UpdateStats --> ActingLoss
    UpdateStats --> DemoLoss
    ActingLoss --> CombinedLoss
    DemoLoss --> CombinedLoss
    CombinedLoss --> OptUpdate
    
    OptUpdate --> ResetEnv
    ResetEnv --> UpdateDemo
    UpdateDemo --> GetObs
```

**Sources:** [src/demo/agent.py:425-548](), [src/demo/agent.py:259-332](), [src/demo/agent.py:166-221]()

## Component Integration and State Management

The system maintains several interconnected state objects that flow through the training pipeline. The `RunState` serves as the central container for all training state, while `EnvState` tracks individual game episodes.

### State and Component Interaction

```mermaid
graph TB
    subgraph "RunState Management"
        RunStateData["RunState<br/>- params: chex.ArrayTree<br/>- env_states: EnvState<br/>- demonstrations: Demonstration<br/>- demonstrations_states: EnvState<br/>- opt_state: optax.OptState<br/>- game_stats: GameStats<br/>- rng: chex.PRNGKey"]
    end
    
    subgraph "Environment State Flow"
        EnvStateData["EnvState<br/>- tensor: residual tensor<br/>- past_factors: played factors<br/>- num_moves: move counter<br/>- last_reward: immediate reward<br/>- sum_rewards: cumulative reward<br/>- is_terminal: episode end flag<br/>- init_tensor_index: target type<br/>- change_of_basis: transform matrix<br/>- factors_in_gadgets: gadget tracking"]
    end
    
    subgraph "Neural Network Pipeline"
        ObservationData["Observation<br/>- tensor: float tensor<br/>- past_factors_as_planes: outer products<br/>- sqrt_played_fraction: progress indicator"]
        NetworkOutput["Network Output<br/>- policy_logits: action probabilities<br/>- values: state values"]
    end
    
    subgraph "MCTS Integration"
        MCTSOutput["mctx.PolicyOutput<br/>- action_weights: search policy<br/>- search_tree: tree statistics"]
        RecurrentOutput["mctx.RecurrentFnOutput<br/>- prior_logits: network policy<br/>- value: network value<br/>- reward: environment reward<br/>- discount: terminal discount"]
    end
    
    RunStateData --> EnvStateData
    EnvStateData --> ObservationData
    ObservationData --> NetworkOutput
    NetworkOutput --> MCTSOutput
    NetworkOutput --> RecurrentOutput
    MCTSOutput --> RunStateData
    RecurrentOutput --> MCTSOutput
```

**Sources:** [src/demo/agent.py:54-73](), [src/environment.py:33-62](), [src/environment.py:65-76](), [src/demo/agent.py:223-257]()

## Key Architectural Patterns

### Neural Network Architecture

The neural network system uses a specialized `TorsoNetwork` with symmetrized axial attention, designed for the geometric structure of tensor decomposition problems.

| Component | Class | Purpose |
|-----------|-------|---------|
| Main Network | `NeuralNetwork` | Simple policy/value head wrapper |
| Feature Extraction | `TorsoNetwork` | Core network architecture |
| Attention Mechanism | `_SymmetrizedAxialAttention` | Geometric-aware attention |
| Transformer Blocks | `_TransformerDecoderBlock` | Self-attention + feedforward |
| Symmetry Handling | `Symmetrization` | Learnable symmetry operations |

**Sources:** [src/demo/agent.py:76-114](), [src/networks.py:256-309](), [src/networks.py:185-253]()

### Environment Game Mechanics

The environment implements a tensor decomposition game where actions correspond to rank-one tensor updates. The game terminates when the tensor becomes zero or maximum moves are reached.

| Mechanism | Implementation | Key Functions |
|-----------|---------------|---------------|
| Action Space | Factor indices | `factors.action_index_to_factor` |
| State Transitions | Rank-one updates | `factors.rank_one_update_to_tensor` |
| Reward System | Move penalties + gadget bonuses | Built into `step()` method |
| Termination | Zero tensor or max moves | `jnp.all(new_tensor == 0)` |
| Gadget Detection | Toffoli and CS patterns | `factors.factors_form_*_gadget` |

**Sources:** [src/environment.py:109-196](), [src/environment.py:316-340]()

### Training Loop Integration

The `Agent` orchestrates the entire training process through the `_run_iteration_agent_env_interaction` method, which handles:

1. **Acting Phase**: MCTS policy search using current network
2. **Learning Phase**: Loss computation and parameter updates  
3. **State Management**: Environment resets and demonstration updates
4. **Statistics Tracking**: Game performance monitoring

The system uses a combined loss function that balances acting experience with synthetic demonstrations, with the demonstration weight decreasing over training steps.

**Sources:** [src/demo/agent.py:425-548](), [src/demo/agent.py:334-381](), [src/demo/agent.py:383-423]()

---

