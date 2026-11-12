> 来源: [https://deepwiki.com/geek-ai/MAgent/5-built-in-scenarios](https://deepwiki.com/geek-ai/MAgent/5-built-in-scenarios)
> DeepWiki geek-ai/MAgent | Last indexed: 26 October 2025 (2144db

# Built-in Scenarios

  Relevant source files 
 - [README.md](https://github.com/geek-ai/MAgent/blob/2144dbd4/README.md?plain=1)
 - [doc/get_started.md](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1)
 - [examples/train_battle.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py)
 
  
## Purpose and Scope

 This page provides an overview of the pre-built training scenarios included with MAgent. These scenarios demonstrate different multi-agent reinforcement learning challenges and serve as starting points for research and experimentation. Each scenario includes complete environment configuration, agent type definitions, map generation logic, reward structures, and training scripts.

 For detailed information about specific scenarios, see:

 
 - [Battle Scenario](https://deepwiki.com/geek-ai/MAgent/5.1-battle-scenario) - competitive two-team combat
 - [Pursuit and Gather Scenarios](https://deepwiki.com/geek-ai/MAgent/5.2-pursuit-and-gather-scenarios) - predator-prey and resource collection
 - [Arrangement Task](https://deepwiki.com/geek-ai/MAgent/5.3-arrangement-task) - cooperative goal formation and navigation
 
 For information about creating custom scenarios, see [Creating Custom Environments](https://deepwiki.com/geek-ai/MAgent/8.1-creating-custom-environments).

 
## Overview of Available Scenarios

 MAgent includes several built-in scenarios that showcase different aspects of many-agent reinforcement learning. Each scenario is implemented as a complete training pipeline with corresponding visualization demos.

 
### Scenario Architecture

 
```

```

 **Sources:** [examples/train_battle.py1-235](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L1-L235) [doc/get_started.md1-126](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L1-L126)

 Each scenario follows a standard structure:

 
 - **Environment Initialization** - Create GridWorld with scenario name and map size
 - **Agent Type Registration** - Define agent properties via Config or built-in configs
 - **Map Generation** - Custom function to place agents and walls
 - **Training Loop** - Observation → Inference → Action → Step → Reward collection
 - **Visualization** - Interactive demos for watching trained agents
 
 
## Scenario Comparison

 
| Scenario | Agent Groups | Map Type | Primary Challenge | Training Time* |
|---|---|---|---|---|
| Battle | 2 (symmetric teams) | Open field | Competitive combat, team coordination | ~1 day |
| Pursuit | 2 (predators, prey) | Open field | Predator cooperation, prey evasion | ~1 day |
| Gather | 2 (agents, food) | Open with resources | Resource collection, competition | ~1 day |
| Arrangement | 1 (agents) | Maze with goals | Cooperative goal reaching, path finding | ~1 day |

 *Training time on GTX1080-Ti GPU

 **Sources:** [README.md57-83](https://github.com/geek-ai/MAgent/blob/2144dbd4/README.md?plain=1#L57-L83) [doc/get_started.md91-103](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L91-L103)

 
## Scenario Categories

 
### Competitive Scenarios

 **Battle** - The flagship scenario demonstrating two-team combat. Agents learn to coordinate attacks, maintain formation, and eliminate opponents.

 
 - **Script:** [examples/train_battle.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py)
 - **Demo:** [examples/show_battle_game.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/show_battle_game.py)
 - **Agent Types:** Two symmetric groups with identical capabilities
 - **Key Features:** User-playable demo where you act as general
 
 **Pursuit** - Classic predator-prey dynamics where predators must cooperate to catch faster prey.

 
 - **Script:** [examples/train_pursuit.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_pursuit.py)
 - **Demo:** [examples/api_demo.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/api_demo.py)
 - **Agent Types:** Predators (attackers) and prey (evaders)
 - **Key Features:** Demonstrates emergent cooperative hunting behavior
 
 
### Resource-Based Scenarios

 **Gather** - Agents compete to collect resources (food) scattered across the environment.

 
 - **Script:** [examples/train_gather.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_gather.py)
 - **Agent Types:** Foraging agents
 - **Key Features:** Resource competition, spatial exploration
 
 
### Cooperative Scenarios

 **Arrangement** - Agents must navigate to specific goal locations, often requiring formation and coordination.

 
 - **Script:** [examples/train_arrange.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_arrange.py)
 - **Demo:** [examples/show_arrange.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/show_arrange.py)
 - **Agent Types:** Homogeneous cooperative agents
 - **Key Features:** Goal formation, obstacle navigation
 
 **Sources:** [README.md62-89](https://github.com/geek-ai/MAgent/blob/2144dbd4/README.md?plain=1#L62-L89) [doc/get_started.md98-103](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L98-L103)

 
## Scenario Implementation Pattern

 All scenarios follow a consistent implementation pattern that makes them easy to understand and modify:

 
```

```

 **Sources:** [examples/train_battle.py133-235](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L133-L235)

 
### Common Code Structure

 
#### 1. Environment Initialization

 
```

```

 The scenario name (e.g., `"battle"`) selects a built-in configuration that pre-defines agent types and reward rules.

 **Sources:** [examples/train_battle.py152-156](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L152-L156)

 
#### 2. Map Generation Function

 Each scenario implements a custom `generate_map()` function that places agents:

 
```

```

 **Sources:** [examples/train_battle.py15-40](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L15-L40)

 
#### 3. Training Loop (play_a_round)

 The `play_a_round()` function implements the standard RL loop with MAgent-specific optimizations:

 **Key components:**

 
 - **Parallel inference** - Models infer actions with `block=False` [examples/train_battle.py67](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L67-L67)
 - **Non-blocking sampling** - Replay buffer updates asynchronously [examples/train_battle.py83](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L83-L83)
 - **Batch training** - All models train after episode completion [examples/train_battle.py121-124](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L121-L124)
 
 **Sources:** [examples/train_battle.py43-131](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L43-L131)

 
#### 4. Model Configuration

 Models are initialized with scenario-specific hyperparameters:

 
| Parameter | DQN Value | DRQN Value | Purpose |
|---|---|---|---|
| batch_size | 256 | 32 | Training batch size |
| memory_size | 2^20 | 5000 | Replay buffer capacity |
| learning_rate | 1e-4 | 1e-4 | Optimizer learning rate |
| target_update | 1200 | 1200 | Target network update frequency |
| train_freq | 5 | 5 | Steps between training |
| unroll_step | - | 8 | DRQN sequence length |

 **Sources:** [examples/train_battle.py168-187](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L168-L187)

 
## Running Scenarios

 
### Training Mode

 All scenarios support training mode with the `--train` flag:

 
```

```

 **Common command-line arguments:**

 
 - `--train` - Enable training mode
 - `--render` - Render every episode
 - `--render_every N` - Render every N episodes (default: 10)
 - `--save_every N` - Save model checkpoints every N episodes (default: 5)
 - `--map_size N` - Set map dimensions (default: 125)
 - `--alg {dqn,drqn,a2c}` - Select RL algorithm
 - `--load_from N` - Load checkpoint from episode N
 - `--greedy` - Disable epsilon-greedy exploration
 
 **Sources:** [examples/train_battle.py134-146](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L134-L146) [README.md62-82](https://github.com/geek-ai/MAgent/blob/2144dbd4/README.md?plain=1#L62-L82)

 
### Evaluation Mode

 Run trained models without training:

 
```

```

 The `--greedy` flag disables exploration for evaluation.

 
### Interactive Demos

 Some scenarios include interactive visualization demos:

 
```

```

 **Note:** PyGame-based demos may be slow on macOS due to PyGame compatibility issues.

 **Sources:** [README.md84-89](https://github.com/geek-ai/MAgent/blob/2144dbd4/README.md?plain=1#L84-L89) [doc/get_started.md111-123](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L111-L123)

 
## Scenario Configuration Files

 Built-in scenarios use pre-defined configurations located in `python/magent/builtin/config/`:

 
```

```

 **Sources:** [doc/get_started.md59](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L59-L59)

 
### Agent Type Configuration Example

 From the pursuit scenario configuration:

 
```

```

 **Key configuration parameters:**

 
 - **Physical attributes** - `width`, `length`, `hp`, `speed`
 - **Perception** - `view_range` (CircleRange or SectorRange)
 - **Actions** - `attack_range`, movement capabilities
 - **Rewards** - `attack_penalty`, `step_reward`, `kill_reward`, `dead_penalty`
 
 **Sources:** [doc/get_started.md11-18](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L11-L18)

 
### Reward Rule Configuration

 Scenarios can define complex event-based rewards:

 
```

```

 This reward structure encourages cooperative behavior. For more details, see [Reward System](https://deepwiki.com/geek-ai/MAgent/2.5-reward-system) and [Custom Reward Functions](https://deepwiki.com/geek-ai/MAgent/8.2-custom-reward-functions).

 **Sources:** [doc/get_started.md46-60](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L46-L60)

 
## Scenario Outputs

 
### Training Outputs

 During training, scenarios generate:

 
 - **Console logs** - Step-by-step statistics

 
 - Agent counts per group
 - Step rewards and cumulative rewards
 - Training loss and value estimates
 - **Model checkpoints** - Saved to `save_model/` directory

 
 - Format: `{name}-{round}.pkl`
 - Contains model weights and training state
 - **Render files** - Saved to `build/render/` (if rendering enabled)

 
 - `config.json` - Environment configuration
 - `video_{round}.txt` - Frame-by-frame state data
 
 **Sources:** [examples/train_battle.py153](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L153-L153) [examples/train_battle.py199-230](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L199-L230)

 
### Performance Metrics

 Typical training output shows:

 
```
===== sample =====
eps 0.20 number [100, 98]
step   0,  nums: [100, 98] reward: [2.4, -1.2],  total_reward: [2.4, -1.2]
step  50,  nums: [95, 93] reward: [5.8, 3.2],  total_reward: [124.5, 98.3]
steps: 108,  total time: 12.34,  step average 0.11

===== train =====
train_time 8.45
round 0  loss: [0.34, 0.29]  num: [92, 88]  reward: [156.2, 134.8]  value: [2.1, 1.9]
```

 **Metrics explained:**

 
 - `eps` - Epsilon-greedy exploration rate
 - `nums` - Agent count per group (alive agents)
 - `reward` - Immediate step reward per group
 - `total_reward` - Cumulative episode reward
 - `loss` - Training loss per model
 - `value` - Average Q-value or value estimate
 
 **Sources:** [examples/train_battle.py58-130](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L58-L130)

 
## Extending Scenarios

 
### Modifying Existing Scenarios

 To modify a scenario:

 
 - **Adjust map generation** - Edit `generate_map()` function
 - **Change hyperparameters** - Modify batch_size, learning_rate, etc.
 - **Switch algorithms** - Use `--alg` flag (dqn, drqn, a2c)
 - **Tune exploration** - Modify epsilon decay schedule
 
 Example epsilon schedule modification:

 
```

```

 **Sources:** [examples/train_battle.py217](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L217-L217)

 
### Creating New Scenarios

 For completely new scenarios, see [Creating Custom Environments](https://deepwiki.com/geek-ai/MAgent/8.1-creating-custom-environments). The process involves:

 
 - Define agent types via Config
 - Implement map generation logic
 - Set up reward rules
 - Create training script following the standard pattern
 - Optionally implement visualization demo
 
 
## Next Steps

 
 - For detailed battle scenario mechanics, see [Battle Scenario](https://deepwiki.com/geek-ai/MAgent/5.1-battle-scenario)
 - For predator-prey and resource gathering, see [Pursuit and Gather Scenarios](https://deepwiki.com/geek-ai/MAgent/5.2-pursuit-and-gather-scenarios)
 - For cooperative tasks, see [Arrangement Task](https://deepwiki.com/geek-ai/MAgent/5.3-arrangement-task)
 - To understand the training workflow, see [Training Workflow](https://deepwiki.com/geek-ai/MAgent/4.1-training-workflow)
 - To create your own scenarios, see [Creating Custom Environments](https://deepwiki.com/geek-ai/MAgent/8.1-creating-custom-environments)
 
 **Sources:** [README.md1-97](https://github.com/geek-ai/MAgent/blob/2144dbd4/README.md?plain=1#L1-L97) [doc/get_started.md1-126](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L1-L126) [examples/train_battle.py1-235](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L1-L235)
