<!-- source: DeepWiki mcp.deepwiki.com · repo chainer/chainerrl · page 5 Examples and Usage · fetched 2026-10-30 -->

# Examples and Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/atari/reproduction/a3c/README.md](examples/atari/reproduction/a3c/README.md)
- [examples/atari/reproduction/dqn/README.md](examples/atari/reproduction/dqn/README.md)
- [examples/atari/reproduction/iqn/README.md](examples/atari/reproduction/iqn/README.md)
- [examples/atari/reproduction/rainbow/README.md](examples/atari/reproduction/rainbow/README.md)
- [examples/gym/train_a3c_gym.py](examples/gym/train_a3c_gym.py)
- [examples/gym/train_acer_gym.py](examples/gym/train_acer_gym.py)
- [examples/gym/train_categorical_dqn_gym.py](examples/gym/train_categorical_dqn_gym.py)
- [examples/gym/train_dqn_gym.py](examples/gym/train_dqn_gym.py)
- [examples/gym/train_pcl_gym.py](examples/gym/train_pcl_gym.py)
- [examples/gym/train_reinforce_gym.py](examples/gym/train_reinforce_gym.py)
- [examples/mujoco/reproduction/ddpg/README.md](examples/mujoco/reproduction/ddpg/README.md)
- [examples/mujoco/reproduction/ppo/README.md](examples/mujoco/reproduction/ppo/README.md)
- [examples/mujoco/reproduction/soft_actor_critic/README.md](examples/mujoco/reproduction/soft_actor_critic/README.md)
- [examples/mujoco/reproduction/td3/README.md](examples/mujoco/reproduction/td3/README.md)
- [examples/mujoco/reproduction/trpo/README.md](examples/mujoco/reproduction/trpo/README.md)

</details>



This page provides practical guidance for using ChainerRL through its comprehensive collection of examples and reproduction scripts. The examples demonstrate how to train reinforcement learning agents on standard benchmarks and reproduce results from published research papers.

For information about the underlying training infrastructure, see [Training and Evaluation Infrastructure](#4). For details about specific RL algorithms, see [Reinforcement Learning Agents](#2).

## Overview of Examples Structure

ChainerRL provides examples organized into three main categories: basic training examples for getting started, algorithm reproduction scripts that match paper results, and a pretrained models system for immediate evaluation.

### Example Categories and Code Structure

```mermaid
graph TB
    subgraph "examples/"
        subgraph "gym/"
            GYM_BASIC["Basic Gym Examples<br/>train_dqn_gym.py<br/>train_a3c_gym.py<br/>train_ppo_gym.py<br/>etc."]
        end
        
        subgraph "atari/reproduction/"
            ATARI_DQN["dqn/<br/>train_dqn.py"]
            ATARI_A3C["a3c/<br/>train_a3c.py"]
            ATARI_RAINBOW["rainbow/<br/>train_rainbow.py"]
            ATARI_IQN["iqn/<br/>train_iqn.py"]
        end
        
        subgraph "mujoco/reproduction/"
            MUJOCO_PPO["ppo/<br/>train_ppo.py"]
            MUJOCO_TRPO["trpo/<br/>train_trpo.py"]
            MUJOCO_DDPG["ddpg/<br/>train_ddpg.py"]
            MUJOCO_TD3["td3/<br/>train_td3.py"]
            MUJOCO_SAC["soft_actor_critic/<br/>train_soft_actor_critic.py"]
        end
    end
    
    subgraph "Core Training Functions"
        TRAIN_EVAL["experiments.train_agent_with_evaluation"]
        TRAIN_ASYNC["experiments.train_agent_async"]
        EVAL_PERF["experiments.eval_performance"]
    end
    
    GYM_BASIC --> TRAIN_EVAL
    ATARI_DQN --> TRAIN_EVAL
    ATARI_A3C --> TRAIN_ASYNC
    MUJOCO_PPO --> TRAIN_EVAL
    MUJOCO_DDPG --> TRAIN_EVAL
```

Sources: [examples/gym/train_dqn_gym.py:1-187](), [examples/gym/train_a3c_gym.py:1-203](), [examples/atari/reproduction/a3c/README.md:1-139](), [examples/mujoco/reproduction/ppo/README.md:1-90]()

### Common Command Line Interface

All examples follow a consistent command line interface pattern with standard options for training, evaluation, and model management.

| Option | Purpose | Example |
|--------|---------|---------|
| `--env` | Environment name | `--env CartPole-v0` |
| `--gpu` | GPU device ID (-1 for CPU) | `--gpu 0` |
| `--seed` | Random seed | `--seed 42` |
| `--outdir` | Output directory | `--outdir results` |
| `--demo` | Evaluation mode | `--demo` |
| `--load` | Load saved model | `--load model.pkl` |
| `--load-pretrained` | Load pretrained model | `--load-pretrained` |
| `--steps` | Training steps | `--steps 1000000` |
| `--eval-interval` | Evaluation frequency | `--eval-interval 10000` |

Sources: [examples/gym/train_dqn_gym.py:37-69](), [examples/gym/train_a3c_gym.py:91-116]()

## Basic Training Examples

The basic examples in `examples/gym/` demonstrate how to train popular RL algorithms on OpenAI Gym environments. These examples are designed for learning and experimentation with straightforward configurations.

### Environment Setup Pattern

All basic examples follow a consistent environment setup pattern using ChainerRL wrappers:

```mermaid
graph LR
    ENV_CREATE["gym.make(args.env)"] --> SEED["env.seed()"]
    SEED --> CAST_OBS["CastObservationToFloat32"]
    CAST_OBS --> MONITOR["Monitor (optional)"]
    MONITOR --> SCALE_REWARD["ScaleReward (training only)"]
    SCALE_REWARD --> RENDER["Render (optional)"]
    
    subgraph "Wrapper Classes"
        CAST_CLASS["chainerrl.wrappers.CastObservationToFloat32"]
        MONITOR_CLASS["chainerrl.wrappers.Monitor"]
        SCALE_CLASS["chainerrl.wrappers.ScaleReward"]
        RENDER_CLASS["chainerrl.wrappers.Render"]
    end
```

Sources: [examples/gym/train_dqn_gym.py:81-99](), [examples/gym/train_a3c_gym.py:133-149]()

### Agent Configuration Patterns

The examples demonstrate different agent configuration patterns based on action space types:

**Discrete Action Spaces (DQN Example):**
- Uses `FCStateQFunctionWithDiscreteAction` for Q-functions
- Employs `LinearDecayEpsilonGreedy` exploration
- Configures `ReplayBuffer` or `PrioritizedReplayBuffer`

**Continuous Action Spaces (DQN with NAF):**
- Uses `FCQuadraticStateQFunction` for continuous control
- Employs `AdditiveOU` exploration noise
- Handles action clipping with `make_action_filtered`

Sources: [examples/gym/train_dqn_gym.py:107-128](), [examples/gym/train_dqn_gym.py:153-160]()

### Training Loop Integration

Basic examples use the high-level training functions from the `experiments` module:

```mermaid
graph TD
    START["Script Start"] --> PARSE_ARGS["Parse Arguments"]
    PARSE_ARGS --> SETUP_ENV["Setup Environment"]
    SETUP_ENV --> CREATE_AGENT["Create Agent"]
    CREATE_AGENT --> DEMO_CHECK{"--demo flag?"}
    
    DEMO_CHECK -->|Yes| EVAL_PERF["experiments.eval_performance"]
    DEMO_CHECK -->|No| TRAIN_CHECK{"Async training?"}
    
    TRAIN_CHECK -->|Yes| TRAIN_ASYNC["experiments.train_agent_async"]
    TRAIN_CHECK -->|No| TRAIN_EVAL["experiments.train_agent_with_evaluation"]
    
    EVAL_PERF --> END["Print Results"]
    TRAIN_ASYNC --> END
    TRAIN_EVAL --> END
```

Sources: [examples/gym/train_dqn_gym.py:167-183](), [examples/gym/train_a3c_gym.py:176-198]()

## Algorithm Reproductions

The reproduction scripts in `examples/atari/reproduction/` and `examples/mujoco/reproduction/` are designed to match published paper results with carefully tuned hyperparameters and evaluation protocols.

### Atari Reproduction Structure

```mermaid
graph TB
    subgraph "Atari Algorithms"
        DQN_ATARI["DQN<br/>Human-level control through<br/>Deep Reinforcement Learning"]
        A3C_ATARI["A3C<br/>Asynchronous Methods for<br/>Deep Reinforcement Learning"]
        RAINBOW_ATARI["Rainbow<br/>Combining Improvements in<br/>Deep Reinforcement Learning"]
        IQN_ATARI["IQN<br/>Implicit Quantile Networks for<br/>Distributional Reinforcement Learning"]
    end
    
    subgraph "Common Features"
        ATARI_WRAPPERS["Atari Environment Wrappers<br/>Frame processing, stacking"]
        EVAL_PROTOCOL["Standardized Evaluation Protocol<br/>1M frame intervals, 500K evaluation frames"]
        PRETRAINED["Pretrained Model Support<br/>--load-pretrained flag"]
        BENCHMARKS["Performance Benchmarks<br/>Comparison with paper results"]
    end
    
    DQN_ATARI --> EVAL_PROTOCOL
    A3C_ATARI --> EVAL_PROTOCOL
    RAINBOW_ATARI --> EVAL_PROTOCOL
    IQN_ATARI --> EVAL_PROTOCOL
```

Sources: [examples/atari/reproduction/a3c/README.md:32-43](), [examples/atari/reproduction/dqn/README.md:34-49](), [examples/atari/reproduction/rainbow/README.md:35-46]()

### MuJoCo Reproduction Structure

```mermaid
graph TB
    subgraph "MuJoCo Algorithms"
        PPO_MUJOCO["PPO<br/>Proximal Policy Optimization"]
        TRPO_MUJOCO["TRPO<br/>Trust Region Policy Optimization"]
        DDPG_MUJOCO["DDPG<br/>Continuous Control with<br/>Deep Reinforcement Learning"]
        TD3_MUJOCO["TD3<br/>Addressing Function Approximation<br/>Error in Actor-Critic Methods"]
        SAC_MUJOCO["SAC<br/>Soft Actor-Critic Algorithms<br/>and Applications"]
    end
    
    subgraph "Evaluation Standards"
        BENCHMARKS_MUJOCO["Standardized Benchmarks<br/>HalfCheetah, Hopper, Walker2d, etc."]
        EVAL_EPISODES["100 evaluation episodes<br/>after 2M training steps"]
        MULTIPLE_SEEDS["Multiple random seeds<br/>10-20 trials per algorithm"]
        TIMING_DATA["Training time measurements<br/>Hours per environment"]
    end
    
    PPO_MUJOCO --> BENCHMARKS_MUJOCO
    TRPO_MUJOCO --> BENCHMARKS_MUJOCO
    DDPG_MUJOCO --> BENCHMARKS_MUJOCO
    TD3_MUJOCO --> BENCHMARKS_MUJOCO
    SAC_MUJOCO --> BENCHMARKS_MUJOCO
```

Sources: [examples/mujoco/reproduction/ppo/README.md:42-59](), [examples/mujoco/reproduction/trpo/README.md:42-55](), [examples/mujoco/reproduction/ddpg/README.md:39-82]()

### Evaluation Protocols

Reproduction scripts implement rigorous evaluation protocols that match the original papers:

**Atari Evaluation Protocol:**
- Evaluation frequency: Every 1 million frames (250K timesteps)
- Evaluation duration: 500K frames (125K timesteps) per evaluation
- Episode constraints: Random no-ops (up to 30), time limits vary by algorithm
- Reporting: Best intermediate score across 200 evaluations

**MuJoCo Evaluation Protocol:**
- Training duration: 2M timesteps for most algorithms
- Evaluation frequency: Every 5K-50K timesteps depending on algorithm
- Episode evaluation: 100 episodes without exploration noise
- Reporting: Average return ± standard error across multiple seeds

Sources: [examples/atari/reproduction/a3c/README.md:110-125](), [examples/mujoco/reproduction/ppo/README.md:42-52]()

## Pretrained Models System

ChainerRL provides a pretrained models system that allows immediate evaluation of trained agents without running lengthy training procedures.

### Loading Pretrained Models

The pretrained model system uses the `--load-pretrained` flag with optional `--pretrained-type` specification:

```bash
# Load best intermediate model
python train_dqn.py --demo --load-pretrained --env BreakoutNoFrameskip-v4 --pretrained-type best

# Load final model after training
python train_rainbow.py --demo --load-pretrained --env BreakoutNoFrameskip-v4 --pretrained-type final
```

### Pretrained Model Types

| Type | Description | Use Case |
|------|-------------|----------|
| `best` | Best intermediate network during training | Highest performance evaluation |
| `final` | Final network after training completion | End-of-training state |

Sources: [examples/atari/reproduction/dqn/README.md:16-30](), [examples/atari/reproduction/rainbow/README.md:16-30]()

### Model Availability

Pretrained models are available for:
- **Atari domains**: DQN, A3C, Rainbow, IQN across 50+ games
- **MuJoCo domains**: PPO, TRPO, DDPG, TD3, SAC across standard continuous control tasks

Each reproduction script includes pretrained models that represent the performance reported in the corresponding README files.

Sources: [examples/atari/reproduction/a3c/README.md:16-19](), [examples/mujoco/reproduction/ppo/README.md:19-23]()

## Practical Usage Patterns

### Quick Start for New Environments

1. **Choose an appropriate base example** based on action space:
   - Discrete actions: Use `train_dqn_gym.py` as starting point
   - Continuous actions: Use DQN with NAF or actor-critic methods

2. **Modify environment creation**:
   ```python
   def make_env(test):
       env = gym.make(args.env)
       env = chainerrl.wrappers.CastObservationToFloat32(env)
       # Add environment-specific wrappers
       return env
   ```

3. **Adjust hyperparameters** in the argument parser section

4. **Run training**:
   ```bash
   python your_script.py --env YourEnv-v0 --steps 100000
   ```

### Reproducing Paper Results

1. **Use the appropriate reproduction script** from the paper you want to reproduce
2. **Check requirements** in the README (e.g., MuJoCo Pro, atari_py)
3. **Run with paper-matching hyperparameters**:
   ```bash
   python train_algorithm.py --env PaperEnv-v0 --seed 0
   ```
4. **Compare results** with the benchmarks provided in the README

### Custom Algorithm Development

1. **Start with the closest existing example** to your algorithm type
2. **Replace the agent creation section** with your custom agent
3. **Maintain the environment setup and training loop patterns**
4. **Use the same evaluation infrastructure** for consistent comparisons

Sources: [examples/gym/train_dqn_gym.py:33-187](), [examples/gym/train_a3c_gym.py:88-202]()

---

