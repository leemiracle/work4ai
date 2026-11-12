> 来源: [https://deepwiki.com/Unity-Technologies/ml-agents/3-python-training-system](https://deepwiki.com/Unity-Technologies/ml-agents/3-python-training-system)
> DeepWiki Unity-Technologies/ml-agents | Last indexed: 22 May 2026 (d52b00

# Python Training System

  Relevant source files 
 - [.pre-commit-config.yaml](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/.pre-commit-config.yaml)
 - [docs/Using-Virtual-Environment.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Using-Virtual-Environment.md?plain=1)
 - [ml-agents-envs/mlagents_envs/registry/binary_utils.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/registry/binary_utils.py)
 - [ml-agents-envs/setup.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/setup.py)
 - [ml-agents/mlagents/trainers/cli_utils.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/cli_utils.py)
 - [ml-agents/mlagents/trainers/learn.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py)
 - [ml-agents/mlagents/trainers/settings.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/settings.py)
 - [ml-agents/mlagents/trainers/tests/test_learn.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/tests/test_learn.py)
 - [ml-agents/mlagents/trainers/tests/test_settings.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/tests/test_settings.py)
 - [ml-agents/mlagents/trainers/tests/test_trainer_controller.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/tests/test_trainer_controller.py)
 - [ml-agents/mlagents/trainers/tests/test_trainer_util.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/tests/test_trainer_util.py)
 - [ml-agents/mlagents/trainers/trainer_controller.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/trainer_controller.py)
 - [ml-agents/setup.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/setup.py)
 - [utils/validate_release_links.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/utils/validate_release_links.py)
 
  The Python Training System is the core training infrastructure of the ML-Agents toolkit, responsible for orchestrating reinforcement learning training sessions. This system provides the command-line interface, configuration management, training loop coordination, and environment management for training ML agents in Unity environments.

 For information about the Unity SDK components that interact with this system, see [Unity SDK Components](https://deepwiki.com/Unity-Technologies/ml-agents/2-unity-sdk-components). For details about specific training algorithms and policies, see [Trainers and Algorithms](https://deepwiki.com/Unity-Technologies/ml-agents/3.2-trainers-and-algorithms) and [Policies and Optimization](https://deepwiki.com/Unity-Technologies/ml-agents/3.3-policies-and-optimization).

 
## System Architecture

 The Python Training System follows a layered architecture with clear separation of concerns, managed primarily by the `mlagents-learn` entry point which delegates to specialized managers.

 
```

```

 Sources: [ml-agents/mlagents/trainers/learn.py59-134](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L59-L134) [ml-agents/mlagents/trainers/cli_utils.py63-193](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/cli_utils.py#L63-L193) [ml-agents/mlagents/trainers/settings.py758-848](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/settings.py#L758-L848) [ml-agents/mlagents/trainers/trainer_controller.py34-70](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/trainer_controller.py#L34-L70)

 
## CLI Entry Point

 The `mlagents-learn` command serves as the primary entry point for training sessions. It is defined as a console script in `setup.py` and maps to `mlagents.trainers.learn:main`.

 
```

```

 The command-line interface supports extensive configuration options defined in `cli_utils.py`:

 
| Category | Key Options | Purpose |
|---|---|---|
| Environment | --env, --num-envs, --num-areas | Unity environment configuration ml-agents/mlagents/trainers/cli_utils.py71-180 |
| Training | --run-id, --resume, --initialize-from | Training session control ml-agents/mlagents/trainers/cli_utils.py88-130 |
| Inference | --inference, --deterministic | Model evaluation mode ml-agents/mlagents/trainers/cli_utils.py95-152 |
| Engine | --no-graphics, --env-args | Unity engine settings ml-agents/mlagents/trainers/cli_utils.py182-192 |

 Sources: [ml-agents/setup.py79-81](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/setup.py#L79-L81) [ml-agents/mlagents/trainers/learn.py51-56](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L51-L56) [ml-agents/mlagents/trainers/cli_utils.py63-193](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/cli_utils.py#L63-L193)

 
## Configuration System

 The configuration system is built around the `RunOptions` class, which aggregates all training parameters using the `attr` and `cattr` libraries for structured data management.

 
```

```

 Configuration can be loaded from YAML files or command-line arguments. The `settings.py` file contains logic for deep merging and validating these settings. For details on configuration structure, see [Training Configuration Files](https://deepwiki.com/Unity-Technologies/ml-agents/5.2-training-configuration-files).

 Sources: [ml-agents/mlagents/trainers/settings.py758-848](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/settings.py#L758-L848) [ml-agents/mlagents/trainers/settings.py38-68](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/settings.py#L38-L68) [ml-agents/mlagents/trainers/cli_utils.py25-61](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/cli_utils.py#L25-L61)

 
## Training Orchestration

 The `run_training()` function in `learn.py` coordinates the setup and execution of the training session. It instantiates the `TrainerController`, which manages the main training loop.

 
```

```

 For details on the execution phase and the inner loop, see [Training Pipeline](https://deepwiki.com/Unity-Technologies/ml-agents/3.1-training-pipeline).

 Sources: [ml-agents/mlagents/trainers/learn.py59-144](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L59-L144) [ml-agents/mlagents/trainers/trainer_controller.py168-192](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/trainer_controller.py#L168-L192)

 
## Environment Management

 The system supports running multiple Unity instances in parallel via `SubprocessEnvManager`. The `create_environment_factory` ensures each instance is properly configured with unique seeds and ports.

 
```

```

 For details on how Python interacts with the Unity executable, see [Environment Management](https://deepwiki.com/Unity-Technologies/ml-agents/3.5-environment-management).

 Sources: [ml-agents/mlagents/trainers/learn.py175-205](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L175-L205) [ml-agents/mlagents/trainers/learn.py111](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L111-L111)

 
## Parameter Management

 The `EnvironmentParameterManager` handles dynamic environment parameters and curriculum learning. It tracks training progress to determine when to advance to the next "lesson" in a curriculum.

 
```

```

 Supported randomization samplers include `UniformSettings`, `GaussianSettings`, and `MultiRangeUniformSettings` defined in `settings.py`.

 Sources: [ml-agents/mlagents/trainers/learn.py112-114](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L112-L114) [ml-agents/mlagents/trainers/settings.py516-595](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/settings.py#L516-L595) [ml-agents/mlagents/trainers/trainer_controller.py104-105](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/trainer_controller.py#L104-L105)

 
## Key Workflows

 
### Training Session Startup

 
 - **CLI Parsing**: `parse_command_line` processes arguments and loads YAML configs [ml-agents/mlagents/trainers/learn.py51-56](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L51-L56)
 - **Resource Validation**: `validate_existing_directories` checks for existing models to prevent accidental overwrites [ml-agents/mlagents/trainers/learn.py75-80](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L75-L80)
 - **Factory Initialization**: `TrainerFactory` and environment factories are prepared [ml-agents/mlagents/trainers/learn.py116-125](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L116-L125)
 - **Loop Execution**: `TrainerController.start_learning` enters the training loop [ml-agents/mlagents/trainers/trainer_controller.py168-172](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/trainer_controller.py#L168-L172)
 
 
### Output Management

 Upon completion or interruption, the system persists the final state:

 
 - **Models**: Saved via `Trainer.save_model()` called by `TrainerController` [ml-agents/mlagents/trainers/trainer_controller.py72-81](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/trainer_controller.py#L72-L81)
 - **Status**: `training_status.json` tracks global training state [ml-agents/mlagents/trainers/learn.py160-161](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L160-L161)
 - **Timers**: `timers.json` provides a hierarchical breakdown of performance [ml-agents/mlagents/trainers/learn.py164-173](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L164-L173)
 
 Sources: [ml-agents/mlagents/trainers/learn.py137-144](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L137-L144) [ml-agents/mlagents/trainers/trainer_controller.py72-82](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/trainer_controller.py#L72-L82) [ml-agents/mlagents/trainers/learn.py16-19](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L16-L19)
