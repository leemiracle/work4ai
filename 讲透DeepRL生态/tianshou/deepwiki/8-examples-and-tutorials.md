> 来源: [https://deepwiki.com/thu-ml/tianshou/8-examples-and-tutorials](https://deepwiki.com/thu-ml/tianshou/8-examples-and-tutorials)
> DeepWiki thu-ml/tianshou | Last indexed: 19 April 2025 (90846f

# Examples and Tutorials

  Relevant source files 
 - [examples/atari/atari_c51.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_c51.py)
 - [examples/atari/atari_dqn.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_dqn.py)
 - [examples/atari/atari_fqf.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_fqf.py)
 - [examples/atari/atari_iqn.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_iqn.py)
 - [examples/atari/atari_ppo.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_ppo.py)
 - [examples/atari/atari_qrdqn.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_qrdqn.py)
 - [examples/atari/atari_rainbow.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_rainbow.py)
 - [examples/atari/atari_sac.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_sac.py)
 - [examples/mujoco/mujoco_a2c_hl.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_a2c_hl.py)
 - [examples/mujoco/mujoco_ddpg_hl.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_ddpg_hl.py)
 - [examples/mujoco/mujoco_npg_hl.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_npg_hl.py)
 - [examples/mujoco/mujoco_ppo_hl.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_ppo_hl.py)
 - [examples/mujoco/mujoco_redq_hl.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_redq_hl.py)
 - [examples/mujoco/mujoco_reinforce_hl.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_reinforce_hl.py)
 - [examples/mujoco/mujoco_sac_hl.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_sac_hl.py)
 - [examples/mujoco/mujoco_td3_hl.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_td3_hl.py)
 - [examples/mujoco/mujoco_trpo_hl.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_trpo_hl.py)
 - [examples/vizdoom/vizdoom_c51.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/vizdoom/vizdoom_c51.py)
 - [examples/vizdoom/vizdoom_ppo.py](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/vizdoom/vizdoom_ppo.py)
 
  This page provides an overview of the example implementations and tutorials available in the Tianshou reinforcement learning framework. These examples demonstrate how to use Tianshou's components to build and train reinforcement learning agents for various environments and algorithms. For information about the core API components, see [Core Concepts](https://deepwiki.com/thu-ml/tianshou/1.1-core-concepts) and for installation instructions, see [Installation and Dependencies](https://deepwiki.com/thu-ml/tianshou/1.2-installation-and-dependencies).

 
## Example Organization

 The examples in Tianshou are organized by environment type and API approach, covering a wide range of reinforcement learning algorithms.

 
```

```

 Sources: examples/mujoco/mujoco_ppo_hl.py, examples/atari/atari_dqn.py, examples/vizdoom/vizdoom_ppo.py

 
### Environment Types

 Tianshou provides examples for three main environments:

 
| Environment Type | Description | Example Files |
|---|---|---|
| Atari | Classic arcade games using the Gym Atari environment | atari_dqn.py, atari_ppo.py, etc. |
| MuJoCo | Continuous control tasks for physics-based simulation | mujoco_sac_hl.py, mujoco_ppo_hl.py, etc. |
| VizDoom | First-person shooter environment based on the Doom engine | vizdoom_ppo.py, vizdoom_c51.py |

 Sources: examples/atari/atari_dqn.py, examples/mujoco/mujoco_sac_hl.py, examples/vizdoom/vizdoom_ppo.py

 
### API Approaches

 Tianshou supports two distinct approaches for implementing reinforcement learning algorithms:

 
 - **High-Level API**: Uses builder patterns and factory methods to quickly configure and run experiments
 - **Procedural API**: Provides more fine-grained control over each component
 
 
## High-Level API Examples

 The high-level API simplifies experiment setup through builder classes and factory methods, making it easier to configure and run reinforcement learning experiments.

 
```

```

 Sources: examples/mujoco/mujoco_ppo_hl.py, examples/mujoco/mujoco_sac_hl.py, examples/mujoco/mujoco_a2c_hl.py

 
### MuJoCo High-Level API Examples

 The MuJoCo examples demonstrate continuous control tasks using the high-level API. Here's an overview of the key components used in these examples:

 
 - **Environment Factory**: Creates training and testing environments
 - **Sampling Configuration**: Defines sampling parameters (epochs, batch size, etc.)
 - **Experiment Configuration**: Sets experiment-wide parameters (seed, device, etc.)
 - **Builder Pattern**: Uses method chaining to configure the experiment
 
 Example of using the high-level API with PPO (from [examples/mujoco/mujoco_ppo_hl.py68-94](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/mujoco/mujoco_ppo_hl.py#L68-L94)):

 
```
experiment = (
    PPOExperimentBuilder(env_factory, experiment_config, sampling_config)
    .with_ppo_params(
        PPOParams(
            discount_factor=gamma,
            gae_lambda=gae_lambda,
            action_bound_method=bound_action_method,
            reward_normalization=rew_norm,
            ent_coef=ent_coef,
            vf_coef=vf_coef,
            max_grad_norm=max_grad_norm,
            eps_clip=eps_clip,
            dual_clip=dual_clip,
            value_clip=value_clip,
            advantage_normalization=norm_adv,
            recompute_advantage=recompute_adv,
            lr=lr,
            lr_scheduler_factory=LRSchedulerFactoryLinear(sampling_config)
            if lr_decay
            else None,
        ),
    )
    .with_actor_factory_default(hidden_sizes, torch.nn.Tanh, continuous_unbounded=True)
    .with_critic_factory_default(hidden_sizes, torch.nn.Tanh)
    .build()
)
experiment.run(run_name=log_name)
```

 Available MuJoCo Examples with High-Level API:

 
| Algorithm | File | Description |
|---|---|---|
| PPO | mujoco_ppo_hl.py | Proximal Policy Optimization |
| SAC | mujoco_sac_hl.py | Soft Actor-Critic |
| A2C | mujoco_a2c_hl.py | Advantage Actor-Critic |
| TRPO | mujoco_trpo_hl.py | Trust Region Policy Optimization |
| NPG | mujoco_npg_hl.py | Natural Policy Gradient |
| DDPG | mujoco_ddpg_hl.py | Deep Deterministic Policy Gradient |
| TD3 | mujoco_td3_hl.py | Twin Delayed DDPG |
| REINFORCE | mujoco_reinforce_hl.py | REINFORCE algorithm (vanilla policy gradient) |
| REDQ | mujoco_redq_hl.py | Randomized Ensemble Double Q-Learning |

 Sources: examples/mujoco/mujoco_ppo_hl.py, examples/mujoco/mujoco_sac_hl.py, examples/mujoco/mujoco_a2c_hl.py, examples/mujoco/mujoco_trpo_hl.py, examples/mujoco/mujoco_npg_hl.py, examples/mujoco/mujoco_ddpg_hl.py, examples/mujoco/mujoco_td3_hl.py, examples/mujoco/mujoco_reinforce_hl.py, examples/mujoco/mujoco_redq_hl.py

 
## Procedural API Examples

 The procedural API provides more fine-grained control over the components and training process, allowing for greater customization.

 
```

```

 Sources: examples/atari/atari_dqn.py, examples/atari/atari_ppo.py, examples/vizdoom/vizdoom_ppo.py

 
### Atari Examples

 The Atari examples demonstrate training agents to play classic arcade games using the procedural API:

 
 - **Environment Setup**: Using `make_atari_env()` to create vectorized environments
 - **Network Definition**: Creating neural networks for the specific algorithm
 - **Policy Configuration**: Instantiating and configuring the policy
 - **Buffer and Collector Setup**: Setting up the replay buffer and collectors
 - **Training**: Configuring and running the appropriate trainer
 
 Example of DQN configuration (from [examples/atari/atari_dqn.py107-116](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_dqn.py#L107-L116)):

 
```
policy = DQNPolicy(
    model=net,
    optim=optim,
    action_space=env.action_space,
    discount_factor=args.gamma,
    estimation_step=args.n_step,
    target_update_freq=args.target_update_freq,
)
```

 Available Atari Examples:

 
| Algorithm | File | Description |
|---|---|---|
| DQN | atari_dqn.py | Deep Q-Network |
| PPO | atari_ppo.py | Proximal Policy Optimization |
| C51 | atari_c51.py | Categorical 51-Atom DQN |
| QRDQN | atari_qrdqn.py | Quantile Regression DQN |
| IQN | atari_iqn.py | Implicit Quantile Network |
| FQF | atari_fqf.py | Fully Parameterized Quantile Function |
| Rainbow | atari_rainbow.py | Rainbow DQN (combines multiple improvements) |
| SAC | atari_sac.py | Soft Actor-Critic (discrete version) |

 Sources: examples/atari/atari_dqn.py, examples/atari/atari_ppo.py, examples/atari/atari_c51.py, examples/atari/atari_qrdqn.py, examples/atari/atari_iqn.py, examples/atari/atari_fqf.py, examples/atari/atari_rainbow.py, examples/atari/atari_sac.py

 
### VizDoom Examples

 The VizDoom examples show how to train agents in a first-person shooter environment:

 
 - **Environment Setup**: Using `make_vizdoom_env()` to create VizDoom environments
 - **Network Definition**: Creating CNN-based networks suitable for VizDoom
 - **Policy Configuration**: Setting up policies for the FPS environment
 - **Collector and Buffer Setup**: Similar to Atari but with VizDoom-specific settings
 
 Available VizDoom Examples:

 
| Algorithm | File | Description |
|---|---|---|
| PPO | vizdoom_ppo.py | Proximal Policy Optimization for VizDoom |
| C51 | vizdoom_c51.py | Categorical 51-Atom DQN for VizDoom |

 Sources: examples/vizdoom/vizdoom_ppo.py, examples/vizdoom/vizdoom_c51.py

 
## Example Workflow Comparison: High-Level vs. Procedural API

 The following diagram illustrates the difference between using the high-level API and the procedural API:

 
```

```

 Sources: examples/mujoco/mujoco_ppo_hl.py, examples/atari/atari_dqn.py

 
## Deep Dive: PPO Algorithm Implementation

 Let's examine how the PPO algorithm is implemented in both API styles:

 
### High-Level API PPO Implementation

 
```

```

 Sources: examples/mujoco/mujoco_ppo_hl.py

 
### Procedural API PPO Implementation

 
```

```

 Sources: examples/atari/atari_ppo.py

 
## Common Design Patterns

 Throughout the examples, several design patterns can be identified:

 
### Command-line Interface Pattern

 Most examples use argparse to define parameters that can be configured through command-line arguments, making it easy to experiment with different hyperparameters.

 Example from [examples/atari/atari_dqn.py21-83](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_dqn.py#L21-L83):

 
```
def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="PongNoFrameskip-v4")
    parser.add_argument("--seed", type=int, default=0)
    # many more arguments...
    return parser.parse_args()
```

 
### Training Loop Functions

 Most examples define several key functions for the training loop:

 
 - `train_fn`: Called before each training episode to update parameters like exploration epsilon
 - `test_fn`: Called before each test episode
 - `stop_fn`: Determines when to stop training (e.g., when reaching a threshold reward)
 - `save_best_fn`: Saves the best policy during training
 
 Example of training functions from [examples/atari/atari_dqn.py175-203](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_dqn.py#L175-L203):

 
```
def save_best_fn(policy: BasePolicy) -> None:
    torch.save(policy.state_dict(), os.path.join(log_path, "policy.pth"))

def stop_fn(mean_rewards: float) -> bool:
    if env.spec.reward_threshold:
        return mean_rewards >= env.spec.reward_threshold
    if "Pong" in args.task:
        return mean_rewards >= 20
    return False

def train_fn(epoch: int, env_step: int) -> None:
    # nature DQN setting, linear decay in the first 1M steps
    if env_step <= 1e6:
        eps = args.eps_train - env_step / 1e6 * (args.eps_train - args.eps_train_final)
    else:
        eps = args.eps_train_final
    policy.set_eps(eps)
    if env_step % 1000 == 0:
        logger.write("train/env_step", env_step, {"train/eps": eps})

def test_fn(epoch: int, env_step: int | None) -> None:
    policy.set_eps(args.eps_test)
```

 
### Watch Pattern

 Most examples include a "watch" function that allows users to visualize the trained agent:

 Example from [examples/atari/atari_dqn.py205-227](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/atari_dqn.py#L205-L227):

 
```
def watch() -> None:
    print("Setup test envs ...")
    policy.set_eps(args.eps_test)
    test_envs.seed(args.seed)
    # Testing or saving buffer
    # ...
    result.pprint_asdict()
```

 
## Getting Started with Examples

 To run an example, you can use the following steps:

 
 - **Choose an example** from the examples directory based on your environment and algorithm of interest
 - **Run the example** with default parameters: `python examples/atari/atari_dqn.py`
 - **Modify parameters** as needed: `python examples/atari/atari_dqn.py --task BreakoutNoFrameskip-v4 --seed 1 --epoch 200`
 
 For the high-level API examples, we use the SensAI logging utility which provides a CLI interface for configuring experiments:

 
```
python examples/mujoco/mujoco_ppo_hl.py --task Hopper-v4 --seed 1 --epoch 200
```

 
## Tips for Creating Your Own Examples

 When creating your own examples based on the provided templates:

 
 - **Choose the API style**:

 
 - High-Level API for quick experimentation with standard algorithms
 - Procedural API for more customization and control
 - **Adapt the environment**:

 
 - For custom environments, create your own environment factory or wrapper
 - **Select algorithms**:

 
 - Start with simpler algorithms (REINFORCE, DQN) before moving to more complex ones
 - Consider the problem domain when selecting an algorithm (discrete vs. continuous action space)
 - **Configure hyperparameters**:

 
 - Use the example hyperparameters as a starting point
 - Systematically tune parameters for your specific environment
