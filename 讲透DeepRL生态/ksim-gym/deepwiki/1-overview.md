> 来源: [https://deepwiki.com/kscalelabs/ksim-gym/1-overview](https://deepwiki.com/kscalelabs/ksim-gym/1-overview)
> DeepWiki kscalelabs/ksim-gym | Last indexed: 18 May 2025 (3e92db

# Overview

  Relevant source files 
 - [README.md](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1)
 
  K-Sim Gym is a framework for training and deploying humanoid robot controllers using reinforcement learning. With just around 700 lines of Python code, this system provides a complete pipeline to develop walking policies for humanoid robots through simulation and then deploy these policies to either simulation environments or physical robots.

 
## Purpose and Scope

 This document provides a high-level introduction to the K-Sim Gym system, its core components, and the end-to-end workflow from training to deployment. For detailed information about the training system, see [Training System](https://deepwiki.com/kscalelabs/ksim-gym/2-training-system), and for deployment procedures, refer to [Model Conversion and Deployment](https://deepwiki.com/kscalelabs/ksim-gym/3-model-conversion-and-deployment).

 Sources: [README.md1-17](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L1-L17)

 
## System Architecture

 K-Sim Gym consists of several interconnected components that work together to facilitate the training and deployment process of humanoid robot controllers.

 
```

```

 Sources: [README.md48-69](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L48-L69) [README.md71-81](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L71-L81)

 
## Training and Deployment Workflow

 The typical workflow in K-Sim Gym follows these steps:

 
```

```

 Sources: [README.md48-87](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L48-L87)

 
## Key Components

 
### HumanoidWalkingTask

 The central class that orchestrates the training process. It defines the task environment, reward structure, and coordinates the simulation with the learning algorithm.

 
### Actor-Critic Model Architecture

 The policy is implemented as an actor-critic architecture where:

 
```

```

 Sources: [README.md67-69](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L67-L69)

 
### Observation and Reward Systems

 The model receives a comprehensive set of observations and is trained with a multi-component reward function:

 
| System | Components |
|---|---|
| Observation Space | Joint positions, Joint velocities, Accelerometer, Gyroscope, Projected gravity, Center of mass info, Base position/orientation |
| Reward System | Forward progress rewards, Upright orientation rewards, Stay alive bonuses, Movement penalties, Posture penalties |

 For detailed explanations of these systems, see [Reward System](https://deepwiki.com/kscalelabs/ksim-gym/2.3-reward-system) and [Observation System](https://deepwiki.com/kscalelabs/ksim-gym/2.4-observation-system).

 
### Conversion System

 The conversion process transforms trained model checkpoints into deployable K-Infer format:

 
```

```

 Sources: [README.md71-75](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L71-L75)

 
### Deployment Options

 Trained and converted models can be deployed in two ways:

 
 - **K-Infer Simulator**: For visualization and testing in a simulated environment

 
```
kinfer-sim assets/model.kinfer kbot --start-height 1.2 --save-video video.mp4
```
 - **Real Robot Deployment**: Submit to the K-Scale Leaderboard for deployment on physical robots
 
 Sources: [README.md77-87](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L77-L87)

 
## Getting Started

 To get started with K-Sim Gym:

 
 - **Training a Policy**:

 
```
python -m train
```
 - **Monitoring Training**:

 
```
tensorboard --logdir humanoid_walking_task
```
 - **Viewing a Trained Policy**:

 
```
python -m train run_mode=view load_from_ckpt_path=humanoid_walking_task/run_<number>/checkpoints/ckpt.bin
```
 - **Converting to K-Infer Format**:

 
```
python -m convert /path/to/ckpt.bin /path/to/model.kinfer
```
 - **Visualizing with K-Infer Simulator**:

 
```
kinfer-sim assets/model.kinfer kbot --start-height 1.2 --save-video video.mp4
```
 
 For more detailed instructions, see [Training a Policy](https://deepwiki.com/kscalelabs/ksim-gym/4.1-training-a-policy), [Monitoring and Visualization](https://deepwiki.com/kscalelabs/ksim-gym/4.2-monitoring-and-visualization), and [Converting and Deploying Models](https://deepwiki.com/kscalelabs/ksim-gym/4.3-converting-and-deploying-models).

 Sources: [README.md48-87](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L48-L87)

 
## Learning Approach

 K-Sim Gym uses a curriculum learning approach to gradually increase the difficulty of the training task:

 
```

```

 For more about curriculum learning, see [Curriculum Learning](https://deepwiki.com/kscalelabs/ksim-gym/2.5-curriculum-learning).

 Sources: [README.md94-117](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L94-L117)

 
## System Requirements

 K-Sim Gym requires:

 
 - Python 3.11 or later
 - JAX with GPU support (recommended)
 - Supporting libraries (MuJoCo, etc.)
 
 On an RTX 4090 GPU, a basic walking policy can be trained in approximately 30 minutes (around 80 training steps).

 Sources: [README.md39-45](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L39-L45) [README.md48-50](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L48-L50)
