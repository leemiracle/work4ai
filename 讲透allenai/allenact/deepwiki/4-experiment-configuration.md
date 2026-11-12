<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/allenact · page 4 Experiment Configuration · fetched 2026-10-26 -->

# Experiment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [allenact/base_abstractions/experiment_config.py](allenact/base_abstractions/experiment_config.py)
- [allenact/utils/viz_utils.py](allenact/utils/viz_utils.py)
- [docs/tutorials/gym-tutorial.md](docs/tutorials/gym-tutorial.md)
- [docs/tutorials/index.md](docs/tutorials/index.md)
- [docs/tutorials/minigrid-tutorial.md](docs/tutorials/minigrid-tutorial.md)
- [docs/tutorials/offpolicy-tutorial.md](docs/tutorials/offpolicy-tutorial.md)
- [docs/tutorials/running-inference-on-a-pretrained-model.md](docs/tutorials/running-inference-on-a-pretrained-model.md)
- [projects/objectnav_baselines/experiments/ithor/objectnav_ithor_base.py](projects/objectnav_baselines/experiments/ithor/objectnav_ithor_base.py)
- [projects/objectnav_baselines/experiments/robothor/objectnav_robothor_base.py](projects/objectnav_baselines/experiments/robothor/objectnav_robothor_base.py)
- [projects/pointnav_baselines/experiments/habitat/pointnav_habitat_base.py](projects/pointnav_baselines/experiments/habitat/pointnav_habitat_base.py)
- [projects/pointnav_baselines/experiments/ithor/pointnav_ithor_base.py](projects/pointnav_baselines/experiments/ithor/pointnav_ithor_base.py)
- [projects/pointnav_baselines/experiments/robothor/pointnav_robothor_base.py](projects/pointnav_baselines/experiments/robothor/pointnav_robothor_base.py)
- [projects/tutorials/gym_tutorial.py](projects/tutorials/gym_tutorial.py)
- [projects/tutorials/minigrid_offpolicy_tutorial.py](projects/tutorials/minigrid_offpolicy_tutorial.py)
- [projects/tutorials/object_nav_ithor_dagger_then_ppo_one_object_viz.py](projects/tutorials/object_nav_ithor_dagger_then_ppo_one_object_viz.py)
- [projects/tutorials/pointnav_habitat_rgb_ddppo.py](projects/tutorials/pointnav_habitat_rgb_ddppo.py)
- [projects/tutorials/pointnav_ithor_rgb_ddppo.py](projects/tutorials/pointnav_ithor_rgb_ddppo.py)
- [projects/tutorials/running_inference_tutorial.py](projects/tutorials/running_inference_tutorial.py)
- [projects/tutorials/training_a_pointnav_model.py](projects/tutorials/training_a_pointnav_model.py)

</details>



This document covers AllenAct's experiment configuration system, which provides a declarative way to define complete embodied AI experiments through the `ExperimentConfig` abstraction. This system handles model creation, task sampling, training pipelines, hardware allocation, and evaluation parameters.

For information about the core training execution that uses these configurations, see [Core Training Architecture](#3). For details about specific simulation environments, see [Simulation Environments](#5).

## ExperimentConfig Abstract Base Class

The `ExperimentConfig` class serves as the foundation for all experiments in AllenAct. It defines a comprehensive interface that specifies every aspect of an experiment, from model architecture to hardware allocation.

```mermaid
graph TB
    subgraph "ExperimentConfig Abstract Interface"
        CONFIG["ExperimentConfig<br/>(Abstract Base)"]
        CONFIG --> TAG["tag()<br/>Experiment Identifier"]
        CONFIG --> MODEL["create_model()<br/>Neural Network Creation"]
        CONFIG --> SAMPLER["make_sampler_fn()<br/>TaskSampler Factory"]
        CONFIG --> PIPELINE["training_pipeline()<br/>TrainingPipeline Setup"]
        CONFIG --> MACHINE["machine_params()<br/>Hardware Configuration"]
        CONFIG --> TRAIN_ARGS["train_task_sampler_args()<br/>Training Parameters"]
        CONFIG --> VALID_ARGS["valid_task_sampler_args()<br/>Validation Parameters"]
        CONFIG --> TEST_ARGS["test_task_sampler_args()<br/>Test Parameters"]
    end
    
    subgraph "Key Components"
        TASKSAMPLER["TaskSampler<br/>Episode Generation"]
        TRAININGPIPELINE["TrainingPipeline<br/>Loss & Optimization"]
        MACHINEPARAMS["MachineParams<br/>GPU/CPU Allocation"]
    end
    
    SAMPLER --> TASKSAMPLER
    PIPELINE --> TRAININGPIPELINE
    MACHINE --> MACHINEPARAMS
```

**Core ExperimentConfig Methods**

The `ExperimentConfig` abstract base class requires implementation of eight essential methods:

| Method | Purpose | Returns |
|--------|---------|---------|
| `tag()` | Unique experiment identifier | `str` |
| `create_model()` | Instantiate the neural network | `nn.Module` |
| `make_sampler_fn()` | Create task sampler instance | `TaskSampler` |
| `training_pipeline()` | Define losses and optimization | `TrainingPipeline` |
| `machine_params()` | Configure hardware allocation | `MachineParams` |
| `train_task_sampler_args()` | Training task parameters | `Dict[str, Any]` |
| `valid_task_sampler_args()` | Validation task parameters | `Dict[str, Any]` |
| `test_task_sampler_args()` | Test task parameters | `Dict[str, Any]` |

Sources: [allenact/base_abstractions/experiment_config.py:188-314]()

## Configuration Components

### TaskSampler Configuration

TaskSamplers generate episodes for training, validation, and testing. The three `*_task_sampler_args` methods provide different parameters for different phases:

```mermaid
graph LR
    subgraph "Task Sampler Configuration Flow"
        CONFIG["ExperimentConfig"]
        CONFIG --> TRAIN_ARGS["train_task_sampler_args()<br/>process_ind, total_processes"]
        CONFIG --> VALID_ARGS["valid_task_sampler_args()<br/>process_ind, total_processes"]
        CONFIG --> TEST_ARGS["test_task_sampler_args()<br/>process_ind, total_processes"]
        
        TRAIN_ARGS --> TRAIN_SAMPLER["Training TaskSampler<br/>Infinite episodes"]
        VALID_ARGS --> VALID_SAMPLER["Validation TaskSampler<br/>Fixed episode count"]
        TEST_ARGS --> TEST_SAMPLER["Test TaskSampler<br/>Fixed episode count"]
        
        MAKE_SAMPLER["make_sampler_fn()"]
        MAKE_SAMPLER --> TRAIN_SAMPLER
        MAKE_SAMPLER --> VALID_SAMPLER
        MAKE_SAMPLER --> TEST_SAMPLER
    end
```

### TrainingPipeline Configuration

The `TrainingPipeline` defines the complete training process including losses, optimizers, learning rate schedules, and multi-stage training:

```mermaid
graph TB
    subgraph "TrainingPipeline Components"
        PIPELINE["TrainingPipeline"]
        PIPELINE --> LOSSES["named_losses<br/>Dict[str, Loss]"]
        PIPELINE --> STAGES["pipeline_stages<br/>List[PipelineStage]"]
        PIPELINE --> OPTIMIZER["optimizer_builder<br/>Builder[Optimizer]"]
        PIPELINE --> SCHEDULER["lr_scheduler_builder<br/>Builder[LRScheduler]"]
        
        STAGES --> STAGE1["PipelineStage<br/>loss_names, max_stage_steps"]
        STAGE1 --> PPO_LOSS["PPO Loss"]
        STAGE1 --> IMITATION_LOSS["Imitation Loss"]
        
        LOSSES --> PPO["PPO(clip_param=0.2)"]
        LOSSES --> BC["BehaviorCloning()"]
    end
```

### MachineParams Configuration

`MachineParams` handles hardware allocation, process distribution, and preprocessing graphs:

```mermaid
graph TB
    subgraph "MachineParams Structure"
        PARAMS["MachineParams"]
        PARAMS --> NPROC["nprocesses<br/>int | Sequence[int]"]
        PARAMS --> DEVICES["devices<br/>List[torch.device]"]
        PARAMS --> SAMPLER_DEV["sampler_devices<br/>List[torch.device]"]
        PARAMS --> PREPROC["sensor_preprocessor_graph<br/>SensorPreprocessorGraph"]
        PARAMS --> VIZ["visualizer<br/>VizSuite"]
        
        NPROC --> DIST["Process Distribution<br/>Across GPUs"]
        DEVICES --> GPU_ALLOC["GPU Allocation<br/>Per Process"]
        PREPROC --> SENSORS["Sensor Processing<br/>ResNet, etc."]
    end
```

Sources: [allenact/base_abstractions/experiment_config.py:27-161](), [allenact/utils/experiment_utils.py]()

## Configuration Hierarchy and Inheritance

AllenAct experiments typically use inheritance to share common configurations across related tasks and environments:

```mermaid
graph TB
    subgraph "Configuration Inheritance Patterns"
        BASE["ExperimentConfig<br/>(Abstract)"]
        
        subgraph "Task-Specific Bases"
            POINTNAV_BASE["PointNavBaseConfig<br/>Common PointNav Logic"]
            OBJECTNAV_BASE["ObjectNavBaseConfig<br/>Common ObjectNav Logic"]
        end
        
        subgraph "Environment-Specific Bases"
            ROBOTHOR_BASE["PointNavRoboThorBaseConfig<br/>RoboThor Settings"]
            ITHOR_BASE["PointNaviThorBaseConfig<br/>iThor Settings"]
            HABITAT_BASE["PointNavHabitatBaseConfig<br/>Habitat Settings"]
        end
        
        subgraph "Concrete Experiments"
            ROBOTHOR_RGB["PointNavRoboThorRGBPPO<br/>RGB + PPO"]
            ROBOTHOR_DEPTH["PointNavRoboThorDepthPPO<br/>Depth + PPO"]
            ITHOR_RGB["PointNaviThorRGBPPO<br/>RGB + PPO"]
        end
        
        BASE --> POINTNAV_BASE
        BASE --> OBJECTNAV_BASE
        
        POINTNAV_BASE --> ROBOTHOR_BASE
        POINTNAV_BASE --> ITHOR_BASE
        POINTNAV_BASE --> HABITAT_BASE
        
        ROBOTHOR_BASE --> ROBOTHOR_RGB
        ROBOTHOR_BASE --> ROBOTHOR_DEPTH
        ITHOR_BASE --> ITHOR_RGB
    end
```

This hierarchy allows sharing of:
- **Task logic** (reward functions, sensors, action spaces)
- **Environment settings** (dataset paths, simulation parameters)
- **Model architectures** (common network designs)
- **Training parameters** (hyperparameters, schedules)

Sources: [projects/pointnav_baselines/experiments/robothor/pointnav_robothor_base.py:1-16](), [projects/pointnav_baselines/experiments/ithor/pointnav_ithor_base.py:1-16](), [projects/objectnav_baselines/experiments/robothor/objectnav_robothor_base.py:1-60]()

## Environment-Specific Configurations

### RoboThor Configuration Example

RoboThor configurations typically define dataset paths, simulation parameters, and hardware allocation:

```mermaid
graph LR
    subgraph "RoboThor PointNav Configuration"
        CONFIG["PointNavRoboThorRGBPPOExperimentConfig"]
        
        CONFIG --> DATASETS["Dataset Paths<br/>TRAIN_DATASET_DIR<br/>VAL_DATASET_DIR"]
        CONFIG --> SENSORS["Sensors<br/>RGBSensorThor<br/>GPSCompassSensorRoboThor"]
        CONFIG --> ENV_ARGS["Environment Args<br/>rotateStepDegrees: 30<br/>gridSize: 0.25"]
        CONFIG --> MACHINE["Machine Config<br/>NUM_PROCESSES: 60<br/>TRAINING_GPUS: [0,1,2,3]"]
        
        DATASETS --> EPISODES["Episode Files<br/>*.json.gz"]
        SENSORS --> OBSERVATIONS["Observations<br/>rgb_lowres<br/>target_coordinates_ind"]
        ENV_ARGS --> SIMULATOR["AI2-THOR Simulator<br/>Physics Settings"]
        MACHINE --> DISTRIBUTED["Distributed Training<br/>Process per GPU"]
    end
```

### Habitat Configuration Example

Habitat configurations use a different approach with habitat-specific config objects:

```mermaid
graph LR
    subgraph "Habitat PointNav Configuration"
        CONFIG["PointNavHabitatBaseConfig"]
        
        CONFIG --> HABITAT_CONFIG["create_pointnav_config()<br/>habitat.Config object"]
        CONFIG --> SCENE_DATASETS["Scene Datasets<br/>Gibson environments"]
        CONFIG --> TASK_CONFIG["Task Configuration<br/>SUCCESS_DISTANCE<br/>MAX_EPISODE_STEPS"]
        
        HABITAT_CONFIG --> SIMULATOR_CONFIG["Simulator Config<br/>RGB_SENSOR settings<br/>DEPTH_SENSOR settings"]
        SCENE_DATASETS --> TRAIN_SCENES["Training Scenes<br/>gibson/v1/train"]
        TASK_CONFIG --> MEASUREMENTS["Measurements<br/>DISTANCE_TO_GOAL<br/>SUCCESS, SPL"]
    end
```

Sources: [projects/pointnav_baselines/experiments/habitat/pointnav_habitat_base.py:34-97](), [projects/tutorials/pointnav_habitat_rgb_ddppo.py:44-281]()

## Tutorial Examples

### MiniGrid Configuration

The MiniGrid tutorial demonstrates a minimal but complete configuration:

```mermaid
graph TB
    subgraph "MiniGrid Tutorial Configuration"
        TUTORIAL["MiniGridTutorialExperimentConfig"]
        
        TUTORIAL --> SIMPLE_MODEL["MiniGridSimpleConvRNN<br/>Lightweight RNN model"]
        TUTORIAL --> SIMPLE_SENSOR["EgocentricMiniGridSensor<br/>agent_view_size: 5"]
        TUTORIAL --> SIMPLE_SAMPLER["MiniGridTaskSampler<br/>EmptyRandomEnv5x5"]
        TUTORIAL --> SIMPLE_PIPELINE["PPO Training<br/>150k steps, CPU only"]
        
        SIMPLE_SAMPLER --> TRAIN_MODE["Train: infinite tasks<br/>random sampling"]
        SIMPLE_SAMPLER --> VALID_MODE["Valid: 20 tasks<br/>deterministic seeds"]
        SIMPLE_SAMPLER --> TEST_MODE["Test: 40 tasks<br/>deterministic seeds"]
    end
```

### Advanced Configuration Features

More complex configurations can include:

- **Multi-stage training** (DAgger → PPO)
- **Auxiliary losses** (inverse dynamics, CPCA)
- **Visualization setup** for testing
- **Distributed training** across multiple nodes

```mermaid
graph TB
    subgraph "Advanced Configuration Features"
        ADV_CONFIG["Advanced ExperimentConfig"]
        
        ADV_CONFIG --> MULTI_STAGE["Multi-stage Pipeline<br/>Stage 1: Imitation<br/>Stage 2: RL"]
        ADV_CONFIG --> AUX_LOSSES["Auxiliary Losses<br/>InverseDynamicsLoss<br/>CPCALoss"]
        ADV_CONFIG --> VISUALIZATION["Visualization Suite<br/>TrajectoryViz<br/>AgentViewViz"]
        ADV_CONFIG --> PREPROCESSING["Preprocessing Graph<br/>ResNetPreprocessor<br/>Custom transforms"]
        
        MULTI_STAGE --> STAGE_COMPONENTS["StageComponent<br/>Different storage/losses<br/>per stage"]
        AUX_LOSSES --> MULTI_LOSS["Multiple named_losses<br/>Combined optimization"]
        VISUALIZATION --> VIZ_SUITE["VizSuite<br/>Test-time visualization"]
    end
```

Sources: [docs/tutorials/minigrid-tutorial.md:32-279](), [projects/tutorials/training_a_pointnav_model.py:133-468](), [projects/tutorials/running_inference_tutorial.py:118-182]()

---

