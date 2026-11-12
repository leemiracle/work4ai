> 来源: [https://deepwiki.com/opendilab/DI-engine/4-policy-system](https://deepwiki.com/opendilab/DI-engine/4-policy-system)
> DeepWiki opendilab/DI-engine | Last indexed: 20 April 2025 (c290a6

# Policy System

  Relevant source files 
 - [ding/data/buffer/buffer.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/data/buffer/buffer.py)
 - [ding/data/buffer/deque_buffer_wrapper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/data/buffer/deque_buffer_wrapper.py)
 - [ding/framework/middleware/tests/test_advantage_estimator.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/middleware/tests/test_advantage_estimator.py)
 - [ding/model/template/collaq.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/collaq.py)
 - [ding/model/template/coma.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/coma.py)
 - [ding/model/template/ppg.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/ppg.py)
 - [ding/model/template/q_learning.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/q_learning.py)
 - [ding/model/template/qac.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/qac.py)
 - [ding/model/template/qac_dist.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/qac_dist.py)
 - [ding/model/template/qmix.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/qmix.py)
 - [ding/model/template/qtran.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/qtran.py)
 - [ding/model/template/tests/test_qac.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/tests/test_qac.py)
 - [ding/model/template/wqmix.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/wqmix.py)
 - [ding/policy/cql.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/cql.py)
 - [ding/policy/ngu.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ngu.py)
 - [ding/policy/ppo.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py)
 - [ding/policy/r2d2.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/r2d2.py)
 - [ding/policy/r2d2_collect_traj.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/r2d2_collect_traj.py)
 - [ding/policy/r2d3.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/r2d3.py)
 - [ding/policy/sac.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py)
 - [ding/rl_utils/a2c.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/a2c.py)
 - [ding/rl_utils/acer.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/acer.py)
 - [ding/rl_utils/adder.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/adder.py)
 - [ding/rl_utils/beta_function.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/beta_function.py)
 - [ding/rl_utils/coma.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/coma.py)
 - [ding/rl_utils/exploration.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/exploration.py)
 - [ding/rl_utils/gae.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/gae.py)
 - [ding/rl_utils/isw.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/isw.py)
 - [ding/rl_utils/ppg.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/ppg.py)
 - [ding/rl_utils/retrace.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/retrace.py)
 - [ding/rl_utils/td.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/td.py)
 - [ding/rl_utils/tests/test_retrace.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/tests/test_retrace.py)
 - [ding/rl_utils/upgo.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/upgo.py)
 - [ding/rl_utils/vtrace.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/vtrace.py)
 - [dizoo/classic_control/pendulum/entry/pendulum_cql_main.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/classic_control/pendulum/entry/pendulum_cql_main.py)
 - [dizoo/dmc2gym/config/dmc2gym_sac_pixel_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/config/dmc2gym_sac_pixel_config.py)
 - [dizoo/dmc2gym/config/dmc2gym_sac_state_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/config/dmc2gym_sac_state_config.py)
 - [dizoo/dmc2gym/entry/dmc2gym_sac_pixel_main.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/entry/dmc2gym_sac_pixel_main.py)
 - [dizoo/dmc2gym/entry/dmc2gym_sac_state_main.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/entry/dmc2gym_sac_state_main.py)
 
  The Policy System in DI-engine is the core component responsible for implementing reinforcement learning algorithms. It defines how agents decide on actions based on observations and manages the training process. This system includes implementations of various RL algorithms such as DQN, PPO, SAC, and QMIX, supporting both single-agent and multi-agent scenarios across discrete, continuous, and hybrid action spaces.

 For information about specific algorithm implementations, see the dedicated pages for [Policy Gradient Methods](https://deepwiki.com/opendilab/DI-engine/4.1-policy-gradient-methods), [Value-Based Methods](https://deepwiki.com/opendilab/DI-engine/4.2-value-based-methods), [Actor-Critic Methods](https://deepwiki.com/opendilab/DI-engine/4.3-actor-critic-methods), and [Multi-Agent Methods](https://deepwiki.com/opendilab/DI-engine/4.4-multi-agent-methods).

 
## Policy Architecture

 The Policy System is built around a base `Policy` class which defines the core interfaces and functionalities common to all RL algorithms. Specific algorithm implementations inherit from this base class and implement the required methods.

 
```

```

 Sources:

 
 - [ding/policy/ppo.py14-600](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L14-L600)
 - [ding/policy/sac.py19-346](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L19-L346)
 - [ding/policy/r2d2.py16-95](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/r2d2.py#L16-L95)
 
 Policies in DI-engine follow a common operational mode structure with three primary modes:

 
 - **Learn Mode**: For updating policy parameters based on collected data
 - **Collect Mode**: For collecting data by interacting with environments
 - **Eval Mode**: For evaluating policy performance without exploration
 
 Each algorithm implementation must define these three modes through corresponding methods:

 
 - `_init_*`: Initializes the necessary components for a specific mode
 - `_forward_*`: Defines the forward computation for that mode
 
 
## Policy Registry and Configuration

 Policies are registered in a central registry, allowing them to be instantiated by name. Each policy has a default configuration that can be customized for specific use cases.

 
```

```

 Sources:

 
 - [ding/policy/ppo.py18-92](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L18-L92)
 - [ding/policy/sac.py19-108](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L19-L108)
 
 
## Policy Workflow and Interaction

 The Policy System interacts with multiple other components of DI-engine, primarily the Model System, Environment System, and Pipeline System. The following diagram illustrates these interactions:

 
```

```

 Sources:

 
 - [ding/policy/ppo.py94-167](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L94-L167)
 - [ding/policy/sac.py124-193](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L124-L193)
 - [ding/policy/r2d2.py162-211](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/r2d2.py#L162-L211)
 
 
## Policy Learning and Data Flow

 The following diagram illustrates the data flow within policy learning:

 
```

```

 Sources:

 
 - [ding/policy/ppo.py203-362](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L203-L362)
 - [ding/policy/sac.py195-346](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L195-L346)
 
 
## Forward Methods and Mode Transitions

 
```

```

 Sources:

 
 - [ding/policy/ppo.py395-430](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L395-L430)
 - [ding/policy/ppo.py434-463](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L434-L463)
 - [ding/policy/ppo.py465-518](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L465-L518)
 - [ding/policy/ppo.py542-576](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L542-L576)
 
 
## Policy Types and Their Models

 The Policy System in DI-engine supports various types of reinforcement learning algorithms, each with its own model architecture. The table below summarizes the main policy types and their corresponding models:

 
| Policy Type | Description | Main Model | Action Space Support |
|---|---|---|---|
| PPO | Proximal Policy Optimization | VAC (Value-Actor-Critic) | Discrete, Continuous, Hybrid |
| SAC | Soft Actor-Critic | QAC (Q-Actor-Critic) | Continuous |
| Discrete SAC | Discrete version of SAC | Discrete QAC | Discrete |
| DQN | Deep Q-Network | DQN (Q-Network) | Discrete |
| QRDQN | Quantile Regression DQN | QRDQN (Distributional Q-Network) | Discrete |
| C51DQN | Categorical 51-atom DQN | C51DQN (Distributional Q-Network) | Discrete |
| R2D2 | Recurrent Replay DQN | DRQN (Recurrent Q-Network) | Discrete |
| QMIX | Q-Mixing for MARL | QMIX (Mixing Network) | Discrete |

 Sources:

 
 - [ding/policy/ppo.py95-115](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L95-L115)
 - [ding/policy/sac.py111-122](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L111-L122)
 - [ding/model/template/q_learning.py12-133](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/q_learning.py#L12-L133)
 - [ding/model/template/qmix.py101-279](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/qmix.py#L101-L279)
 
 
## Policy Component Integration

 
```

```

 Sources:

 
 - [ding/policy/ppo.py136-201](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L136-L201)
 - [ding/policy/sac.py124-193](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L124-L193)
 - [ding/policy/r2d2.py162-211](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/r2d2.py#L162-L211)
 - [ding/rl_utils/td.py26-72](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/td.py#L26-L72)
 - [ding/rl_utils/gae.py1-25](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/gae.py#L1-L25)
 
 
## Common Algorithm Components

 Many reinforcement learning algorithms share common components for data processing and loss computation. The following table outlines key utility functions used across different policies:

 
| Utility Function | Description | Used in |
|---|---|---|
| q_nstep_td_error | Computes TD error for n-step Q-learning | DQN, R2D2 |
| v_1step_td_error | Computes TD error for value function | PPO, SAC |
| gae | Generalized Advantage Estimation | PPO |
| get_train_sample | Processes transitions into training samples | All policies |
| get_nstep_return_data | Computes n-step returns | DQN, R2D2, SAC |

 Sources:

 
 - [ding/rl_utils/td.py26-152](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/td.py#L26-L152)
 - [ding/rl_utils/adder.py157-223](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/adder.py#L157-L223)
 - [ding/rl_utils/gae.py22-47](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/gae.py#L22-L47)
 
 
## Policy Modes in Detail

 
### Learn Mode

 The learn mode is responsible for updating policy parameters based on collected data. It typically involves:

 
 - Data preprocessing
 - Forward pass through the model
 - Loss computation
 - Parameter updates via optimizer
 - Target network updates (if applicable)
 
 Example implementation from PPO:

 
```

```

 Sources:

 
 - [ding/policy/ppo.py203-362](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L203-L362)
 - [ding/policy/sac.py195-346](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L195-L346)
 
 
### Collect Mode

 The collect mode is responsible for interacting with the environment to collect new data for training. It typically involves:

 
 - Processing observations from the environment
 - Selecting actions based on the current policy (with exploration)
 - Processing the transitions for storage in the replay buffer
 
 Example implementation from SAC:

 
```

```

 Sources:

 
 - [ding/policy/sac.py404-466](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L404-L466)
 - [ding/policy/ppo.py395-463](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L395-L463)
 
 
### Eval Mode

 The eval mode is responsible for evaluating the policy's performance. It's similar to collect mode but typically uses a deterministic action selection strategy without exploration:

 
```

```

 Sources:

 
 - [ding/policy/ppo.py542-576](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L542-L576)
 - [ding/policy/sac.py496-556](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L496-L556)
 
 
## Policy Models and Templates

 The Policy System in DI-engine uses a variety of model templates based on the requirements of different algorithms. These templates provide the neural network architecture for the policy.

 
```

```

 Sources:

 
 - [ding/model/template/q_learning.py12-133](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/q_learning.py#L12-L133)
 - [ding/model/template/qac.py12-193](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/qac.py#L12-L193)
 - [ding/model/template/qmix.py101-279](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/qmix.py#L101-L279)
 
 The policy can request a specific model via the `default_model` method, which returns the model name and import path:

 
```

```

 Sources:

 
 - [ding/policy/ppo.py95-115](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L95-L115)
 - [ding/policy/sac.py111-122](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L111-L122)
 - [ding/policy/r2d2.py148-161](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/r2d2.py#L148-L161)
 
 
## Policy Monitoring and Visualization

 Policies in DI-engine provide a method to monitor training statistics which are then used for logging and visualization. The `_monitor_vars_learn` method returns a list of variable names that should be logged during training:

 
```

```

 Sources:

 
 - [ding/policy/ppo.py578-599](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/ppo.py#L578-L599)
 
 
## Policy State Management

 Policies in DI-engine manage their internal state using `_state_dict_learn` and `_load_state_dict_learn` methods. These methods are responsible for saving and loading the policy's learning state, including model parameters and optimizer states:

 
```

```

 Sources:

 
 - [ding/policy/sac.py349-383](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/sac.py#L349-L383)
 
 
## Conclusion

 The Policy System in DI-engine provides a flexible and extensible framework for implementing a wide range of reinforcement learning algorithms. By separating the policy into different operational modes (learn, collect, eval) and defining clear interfaces for interaction with other components, DI-engine makes it easy to implement new algorithms and integrate them with the rest of the framework.

 The system supports various types of reinforcement learning algorithms, from value-based methods like DQN to policy gradient methods like PPO and actor-critic methods like SAC. It also supports both single-agent and multi-agent settings, making it a versatile tool for reinforcement learning research and applications.
