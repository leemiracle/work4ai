> 来源: [https://deepwiki.com/rail-berkeley/softlearning/3-experiment-framework](https://deepwiki.com/rail-berkeley/softlearning/3-experiment-framework)
> DeepWiki rail-berkeley/softlearning | Last indexed: 25 June 2025 (13cf18

# Experiment Framework

  Relevant source files 
 - [README.md](https://github.com/rail-berkeley/softlearning/blob/13cf187c/README.md?plain=1)
 - [environment.yml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/environment.yml)
 - [examples/development/main.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/main.py)
 - [examples/development/variants.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py)
 - [examples/instrument.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py)
 - [examples/utils.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/utils.py)
 - [requirements.txt](https://github.com/rail-berkeley/softlearning/blob/13cf187c/requirements.txt)
 - [setup.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/setup.py)
 - [softlearning/replay_pools/flexible_replay_pool_test.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/softlearning/replay_pools/flexible_replay_pool_test.py)
 
  The Experiment Framework is the core orchestration system that coordinates all components of the softlearning library to run deep reinforcement learning experiments. It provides a configuration-driven approach to experiment management, seamless integration with Ray Tune for distributed execution, and support for multiple execution modes from local debugging to large-scale cloud deployment.

 For information about specific algorithms and policies used within experiments, see [Core Components](https://deepwiki.com/rail-berkeley/softlearning/4-core-components). For details about distributed training setup, see [Distributed Training with Ray](https://deepwiki.com/rail-berkeley/softlearning/5.3-distributed-training-with-ray).

 
## Core Architecture

 The experiment framework consists of three main components: the configuration system (`variant_spec`), the orchestration engine (`ExperimentRunner`), and the execution infrastructure that integrates with Ray Tune.

 
### Experiment Orchestration Flow

 
```

```

 **Sources:** [examples/development/main.py25-93](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/main.py#L25-L93) [examples/development/variants.py567-577](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L567-L577) [examples/instrument.py220-244](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py#L220-L244)

 
### ExperimentRunner Architecture

 The `ExperimentRunner` class serves as the central coordinator that inherits from `tune.Trainable` and manages the complete experiment lifecycle.

 
```

```

 **Sources:** [examples/development/main.py25-258](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/main.py#L25-L258)

 
## Configuration System

 The variant specification (`variant_spec`) system provides hierarchical configuration management for experiments. It uses nested dictionaries to define all aspects of an experiment, from algorithm parameters to environment settings.

 
### Variant Specification Structure

 
| Component | Configuration Key | Purpose |
|---|---|---|
| Environment | environment_params | Training and evaluation environment settings |
| Policy | policy_params | Policy network architecture and parameters |
| Algorithm | algorithm_params | RL algorithm configuration (SAC, SQL) |
| Replay Pool | replay_pool_params | Experience replay buffer settings |
| Sampler | sampler_params | Data collection configuration |
| Q-Functions | Q_params | Value function network architecture |
| Runtime | run_params | Checkpointing, seeding, and execution settings |

 
### Configuration Generation Process

 
```

```

 **Sources:** [examples/development/variants.py427-577](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L427-L577) [examples/development/variants.py17-74](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L17-L74) [examples/development/variants.py77-86](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L77-L86)

 
### Hierarchical Parameter Defaults

 The configuration system uses hierarchical defaults with the `DEFAULT_KEY` pattern to provide fallback values:

 
```

```

 **Sources:** [examples/development/variants.py348-356](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L348-L356) [examples/development/variants.py233-245](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L233-L245)

 
## Execution Modes

 The framework supports multiple execution modes to accommodate different development and deployment scenarios.

 
### Execution Mode Selection

 
| Mode | Purpose | Ray Configuration | TensorFlow Mode |
|---|---|---|---|
| local | Production training with parallelization | local_mode=False | Graph mode |
| debug | Development debugging | local_mode=True | Eager mode |
| cluster | Distributed cluster execution | address=head_node:6379 | Graph mode |

 
### Mode-Specific Workflow

 
```

```

 **Sources:** [examples/instrument.py220-244](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py#L220-L244) [examples/instrument.py247-304](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py#L247-L304) [examples/instrument.py307-338](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py#L307-L338)

 
## Ray Tune Integration

 The framework leverages Ray Tune's capabilities for hyperparameter optimization, resource management, and experiment tracking.

 
### Tune Configuration Parameters

 
| Parameter Category | Key Parameters | Purpose |
|---|---|---|
| Resources | resources_per_trial, trial_cpus, trial_gpus | Resource allocation per trial |
| Sampling | num_samples | Number of trial repetitions |
| Checkpointing | checkpoint_freq, checkpoint_at_end | Model persistence |
| Recovery | max_failures, restore | Fault tolerance |
| Storage | local_dir, upload_dir | Result storage |

 
### Experiment Launch Flow

 
```

```

 **Sources:** [examples/instrument.py83-144](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py#L83-L144) [examples/utils.py55-153](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/utils.py#L55-L153)

 
## Checkpoint System

 The framework implements comprehensive checkpointing to enable experiment resumption and model deployment.

 
### Checkpoint Components

 
| Component | Save Method | Restore Method | File Format |
|---|---|---|---|
| Replay Pool | _save_replay_pool() | _restore_replay_pool() | .pkl (gzipped) |
| Sampler | _save_sampler() | _restore_sampler() | .pkl (pickle) |
| Policy | _save_policy() | _restore_policy() | TensorFlow SavedModel |
| Q-Functions | _save_value_functions() | _restore_value_functions() | TensorFlow weights |
| Algorithm | _save_algorithm() | _restore_algorithm() | JSON + TensorFlow checkpoint |

 
### Checkpoint Directory Structure

 
```

```

 **Sources:** [examples/development/main.py105-258](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/main.py#L105-L258)
