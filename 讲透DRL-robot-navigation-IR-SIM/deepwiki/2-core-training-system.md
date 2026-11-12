<!-- source: DeepWiki mcp.deepwiki.com · repo reiniscimurs/DRL-robot-navigation-IR-SIM · page 2 Core Training System · fetched 2026-10-14 -->

# Core Training System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [poetry.lock](poetry.lock)
- [robot_nav/models/CNNTD3/CNNTD3.py](robot_nav/models/CNNTD3/CNNTD3.py)
- [robot_nav/models/DDPG/DDPG.py](robot_nav/models/DDPG/DDPG.py)
- [robot_nav/models/TD3/TD3.py](robot_nav/models/TD3/TD3.py)
- [robot_nav/rl_train.py](robot_nav/rl_train.py)

</details>



This document covers the central training orchestration system that coordinates reinforcement learning model training for robot navigation. The core training system is implemented primarily in `train.py` and serves as the main entry point for training RL agents in the IR-SIM simulation environment.

For detailed information about the simulation environment mechanics, see [Simulation Environment](#2.1). For replay buffer management and preprocessing utilities, see [Data Management and Utilities](#2.2). For specific RL algorithm implementations, see [Reinforcement Learning Models](#3).

## System Architecture

The core training system follows a modular architecture that separates concerns between model selection, environment management, and training orchestration.

```mermaid
graph TB
    main["main()"] --> model_init["Model Initialization"]
    main --> sim_init["SIM_ENV() Instantiation"]
    main --> buffer_init["get_buffer() Call"]
    
    model_init --> TD3["TD3()"]
    model_init --> SAC["SAC()"]
    model_init --> PPO["PPO()"]
    model_init --> DDPG["DDPG()"]
    model_init --> CNNTD3["CNNTD3()"]
    model_init --> HCM["HCM()"]
    
    sim_init --> sim_step["sim.step()"]
    sim_init --> sim_reset["sim.reset()"]
    
    buffer_init --> replay_buffer["replay_buffer"]
    buffer_init --> pretrain_check["Pretraining Logic"]
    
    main --> training_loop["Training Loop"]
    training_loop --> prepare_state["model.prepare_state()"]
    training_loop --> get_action["model.get_action()"]
    training_loop --> buffer_add["replay_buffer.add()"]
    training_loop --> model_train["model.train()"]
    training_loop --> evaluate_func["evaluate()"]
    
    evaluate_func --> tensorboard["model.writer.add_scalar()"]
```

**Training System Component Mapping**

| Component | Code Entity | File Location | Purpose |
|-----------|-------------|---------------|---------|
| Training Orchestrator | `main()` | [robot_nav/train.py:14-108]() | Main training loop coordinator |
| Environment Manager | `SIM_ENV` | [robot_nav/train.py:49]() | Simulation environment interface |
| Buffer Manager | `get_buffer()` | [robot_nav/train.py:50-58]() | Replay buffer initialization |
| Model Interface | Various model classes | [robot_nav/train.py:1-6]() | RL algorithm implementations |
| Evaluation System | `evaluate()` | [robot_nav/train.py:109-144]() | Performance assessment |

Sources: [robot_nav/train.py:1-149]()

## Training Pipeline Components

The training system consists of several key components that work together to train RL agents:

```mermaid
flowchart TD
    config["Configuration Parameters"] --> main_func["main()"]
    main_func --> model_select["Model Selection"]
    main_func --> env_setup["Environment Setup"]
    main_func --> buffer_setup["Buffer Setup"]
    
    model_select --> model_instance["Model Instance"]
    env_setup --> sim_instance["SIM_ENV Instance"]
    buffer_setup --> replay_buffer_instance["Replay Buffer"]
    
    model_instance --> training_loop["Training Loop"]
    sim_instance --> training_loop
    replay_buffer_instance --> training_loop
    
    training_loop --> state_prep["prepare_state()"]
    training_loop --> action_gen["get_action()"]
    training_loop --> env_step["sim.step()"]
    training_loop --> experience_store["replay_buffer.add()"]
    training_loop --> model_update["model.train()"]
    
    training_loop --> episode_check["Episode Complete?"]
    episode_check -->|"Yes"| epoch_check["Epoch Complete?"]
    episode_check -->|"No"| state_prep
    
    epoch_check -->|"Yes"| evaluation["evaluate()"]
    epoch_check -->|"No"| state_prep
    evaluation --> tensorboard_log["TensorBoard Logging"]
    tensorboard_log --> state_prep
```

### Core Configuration Parameters

The training system uses a comprehensive set of hyperparameters defined in the `main()` function:

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `action_dim` | 2 | Linear and angular velocity actions |
| `state_dim` | 25 | Laser scan + goal + action state vector |
| `max_epochs` | 60 | Total training epochs |
| `episodes_per_epoch` | 70 | Episodes before evaluation |
| `train_every_n` | 2 | Training frequency (every n episodes) |
| `training_iterations` | 80 | Batches per training cycle |
| `batch_size` | 64 | Experience batch size |
| `max_steps` | 300 | Maximum steps per episode |

Sources: [robot_nav/train.py:16-37]()

## Main Training Loop

The core training loop implements the standard RL training cycle with episode and epoch management:

### State-Action-Reward Cycle

```mermaid
graph LR
    reset["sim.reset()"] --> prepare["model.prepare_state()"]
    prepare --> action["model.get_action()"]
    action --> transform["Action Transformation"]
    transform --> step["sim.step()"]
    step --> next_state["Next State Preparation"]
    next_state --> store["replay_buffer.add()"]
    store --> terminal_check["Terminal Check"]
    terminal_check -->|"Terminal"| reset
    terminal_check -->|"Continue"| prepare
```

The training loop processes experiences in the following sequence:

1. **State Preparation**: Raw sensor data is processed via `model.prepare_state()` [robot_nav/train.py:65-67]()
2. **Action Generation**: Policy network produces actions via `model.get_action()` [robot_nav/train.py:69]()
3. **Action Transformation**: Actions are scaled to appropriate velocity ranges [robot_nav/train.py:70-73]()
4. **Environment Step**: Actions are executed in simulation via `sim.step()` [robot_nav/train.py:75-77]()
5. **Experience Storage**: Transitions are stored via `replay_buffer.add()` [robot_nav/train.py:81-83]()

### Episode and Epoch Management

The system manages training at two hierarchical levels:

- **Episodes**: Individual navigation attempts, terminated by collision, goal reach, or step limit
- **Epochs**: Collections of episodes (default 70) followed by evaluation

Training occurs every `train_every_n` episodes via `model.train()` [robot_nav/train.py:91-95](), while evaluation runs after each epoch completion [robot_nav/train.py:101-106]().

Sources: [robot_nav/train.py:64-107]()

## Model Training Integration

The training system supports multiple RL algorithms through a unified interface:

### Supported Models

| Model Class | Algorithm Type | Key Features |
|-------------|----------------|--------------|
| `TD3` | Off-policy Actor-Critic | Twin networks, delayed updates |
| `SAC` | Off-policy Actor-Critic | Entropy regularization |
| `PPO` | On-policy Actor-Critic | Clipped surrogate objective |
| `DDPG` | Off-policy Actor-Critic | Deterministic policy |
| `CNNTD3` | Enhanced TD3 | CNN laser processing |
| `HCM` | Rule-based | Hardcoded navigation baseline |

All models implement the same interface:
- `prepare_state()`: State preprocessing
- `get_action()`: Action generation
- `train()`: Network parameter updates

Sources: [robot_nav/train.py:1-6](), [robot_nav/train.py:39-47]()

## Evaluation System

The evaluation system provides comprehensive performance assessment through the `evaluate()` function:

### Evaluation Metrics

```mermaid
graph TB
    eval_start["evaluate()"] --> reset_loop["Evaluation Episodes Loop"]
    reset_loop --> sim_reset_eval["sim.reset()"]
    sim_reset_eval --> eval_step_loop["Episode Step Loop"]
    
    eval_step_loop --> eval_prepare["model.prepare_state()"]
    eval_prepare --> eval_action["model.get_action(noise=False)"]
    eval_action --> eval_step["sim.step()"]
    eval_step --> reward_acc["Reward Accumulation"]
    eval_step --> collision_check["Collision Detection"]
    eval_step --> goal_check["Goal Detection"]
    
    reward_acc --> metrics["Performance Metrics"]
    collision_check --> metrics
    goal_check --> metrics
    
    metrics --> tensorboard_write["TensorBoard Logging"]
    tensorboard_write --> console_output["Console Output"]
```

The evaluation system tracks three primary metrics:

1. **Average Reward**: Cumulative reward across evaluation episodes [robot_nav/train.py:128-135]()
2. **Collision Rate**: Percentage of episodes ending in collision [robot_nav/train.py:130-136]()
3. **Goal Rate**: Percentage of episodes reaching the target [robot_nav/train.py:132-137]()

Results are logged to TensorBoard via `model.writer.add_scalar()` [robot_nav/train.py:142-144]() and displayed in console output [robot_nav/train.py:138-141]().

### Evaluation Configuration

- **Episode Count**: Configurable via `nr_eval_episodes` (default 10)
- **Step Limit**: 501 steps maximum per evaluation episode
- **Noise**: Actions generated without exploration noise (`noise=False`)

Sources: [robot_nav/train.py:109-144]()

## Buffer and Pretraining Integration

The training system integrates with the buffer management system through `get_buffer()` which handles:

- Replay buffer instantiation
- Optional experience loading from saved data
- Pretraining capability for model initialization
- Buffer size and type configuration based on model requirements

The buffer setup supports both off-policy algorithms (with replay buffers) and on-policy algorithms (with rollout buffers), determined by the model type.

Sources: [robot_nav/train.py:50-58]()

---

