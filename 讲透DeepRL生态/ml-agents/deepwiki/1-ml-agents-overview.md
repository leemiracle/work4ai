> 来源: [https://deepwiki.com/Unity-Technologies/ml-agents/1-ml-agents-overview](https://deepwiki.com/Unity-Technologies/ml-agents/1-ml-agents-overview)
> DeepWiki Unity-Technologies/ml-agents | Last indexed: 22 May 2026 (d52b00

# ML-Agents Overview

  Relevant source files 
 - [com.unity.ml-agents/CHANGELOG.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/CHANGELOG.md?plain=1)
 - [com.unity.ml-agents/Runtime/Academy.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs)
 - [com.unity.ml-agents/package.json](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json)
 - [docs/Background-Machine-Learning.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Background-Machine-Learning.md?plain=1)
 - [docs/Background-Unity.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Background-Unity.md?plain=1)
 - [docs/FAQ.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/FAQ.md?plain=1)
 - [docs/Getting-Started.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Getting-Started.md?plain=1)
 - [docs/Learning-Environment-Create-New.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Create-New.md?plain=1)
 - [docs/Learning-Environment-Design-Agents.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design-Agents.md?plain=1)
 - [docs/Learning-Environment-Design.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design.md?plain=1)
 - [docs/Learning-Environment-Examples.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Examples.md?plain=1)
 - [docs/Learning-Environment-Executable.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Executable.md?plain=1)
 - [docs/ML-Agents-Overview.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/ML-Agents-Overview.md?plain=1)
 - [docs/ML-Agents-Toolkit-Documentation.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/ML-Agents-Toolkit-Documentation.md?plain=1)
 - [docs/Readme.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Readme.md?plain=1)
 - [docs/Training-Configuration-File.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-Configuration-File.md?plain=1)
 - [docs/Training-ML-Agents.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-ML-Agents.md?plain=1)
 - [localized_docs/RU/README.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/localized_docs/RU/README.md?plain=1)
 - [localized_docs/TR/README.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/localized_docs/TR/README.md?plain=1)
 - [localized_docs/TR/docs/Getting-Started.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/localized_docs/TR/docs/Getting-Started.md?plain=1)
 - [ml-agents-envs/mlagents_envs/__init__.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/__init__.py)
 - [ml-agents/mlagents/trainers/__init__.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/__init__.py)
 - [utils/validate_versions.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/utils/validate_versions.py)
 
  The Unity ML-Agents Toolkit is a comprehensive framework that enables Unity environments to serve as training grounds for machine learning agents. This document provides an architectural overview of the toolkit, covering the core Unity SDK components, Python training system, and communication infrastructure that bridges game environments with machine learning algorithms.

 For specific implementation details of Unity components, see [Unity SDK Components](https://deepwiki.com/Unity-Technologies/ml-agents/2-unity-sdk-components). For Python training system internals, see [Python Training System](https://deepwiki.com/Unity-Technologies/ml-agents/3-python-training-system). For communication protocol details, see [Unity-Python Communication](https://deepwiki.com/Unity-Technologies/ml-agents/4-unity-python-communication).

 
## System Architecture

 ML-Agents implements a distributed architecture where Unity provides the simulation environment while Python handles the machine learning algorithms. The system operates through a client-server model connected via gRPC communication.

 
### Overall System Design

 
```

```

 Sources: [com.unity.ml-agents/Runtime/Academy.cs13-67](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L13-L67) [com.unity.ml-agents/Runtime/Agent.cs1-50](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L1-L50) [ml-agents/mlagents/trainers/learn.py1-40](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/learn.py#L1-L40) [docs/ML-Agents-Overview.md35-65](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/ML-Agents-Overview.md?plain=1#L35-L65)

 
### Core Component Relationships

 The ML-Agents architecture follows a hierarchical pattern where the `Academy` manages the global training environment, `Agent` instances implement individual behaviors, and various supporting components handle observations, actions, and communication.

 
```

```

 Sources: [docs/Learning-Environment-Design-Agents.md44-84](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design-Agents.md?plain=1#L44-L84) [com.unity.ml-agents/Runtime/Academy.cs165-180](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L165-L180) [com.unity.ml-agents/Runtime/Agent.cs200-533](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L200-L533)

 
## Key Components

 
### Academy

 The `Academy` class serves as the central coordinator for the ML-Agents system. It operates as a singleton that manages environment stepping, communicator connections, and global training state. As of version 4.0.0, it supports Unity 6000.0+ and integrates with the latest Sentis inference engine [com.unity.ml-agents/package.json1-12](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L1-L12)

 
| Component | Purpose | Key Methods |
|---|---|---|
| Academy | Global environment management | EnvironmentStep(), LazyInitialize() com.unity.ml-agents/Runtime/Academy.cs43-132 |
| AcademyFixedUpdateStepper | Internal helper to step Academy | FixedUpdate() com.unity.ml-agents/Runtime/Academy.cs31-46 |
| StatsRecorder | Metrics collection | Add(), statistics recording |

 Sources: [com.unity.ml-agents/Runtime/Academy.cs40-160](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L40-L160)

 
### Agent

 The `Agent` class represents individual learning entities. Each agent observes its environment via `CollectObservations`, receives actions through `OnActionReceived`, and provides rewards to guide the learning process [docs/Learning-Environment-Design-Agents.md66-84](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design-Agents.md?plain=1#L66-L84)

 
 - **OnEpisodeBegin()**: Called to reset the environment for a new training cycle [docs/Learning-Environment-Create-New.md136-150](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Create-New.md?plain=1#L136-L150)
 - **Heuristic()**: Allows manual control of the agent for debugging or player-controlled behavior [docs/Learning-Environment-Design-Agents.md78-83](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design-Agents.md?plain=1#L78-L83)
 - **RequestDecision()**: Triggers the observation-decision-action cycle [docs/Learning-Environment-Design-Agents.md105-120](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design-Agents.md?plain=1#L105-L120)
 
 Sources: [com.unity.ml-agents/Runtime/Agent.cs206-600](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L206-L600) [docs/Learning-Environment-Design-Agents.md1-100](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design-Agents.md?plain=1#L1-L100)

 
### Communication Infrastructure

 ML-Agents uses gRPC for communication between Unity and Python. The system follows semantic versioning on the communication protocol to ensure compatibility.

 
 - **API Version**: Current protocol version is `1.5.0` [com.unity.ml-agents/Runtime/Academy.cs104](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L104-L104)
 - **Port Configuration**: Default Editor training port is `5004`, or specified via `--mlagents-port` [com.unity.ml-agents/Runtime/Academy.cs112-114](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L112-L114)
 - **Side Channels**: Used for non-RL data exchange, such as environment parameters or engine configuration [com.unity.ml-agents/Runtime/Academy.cs10](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L10-L10)
 
 Sources: [com.unity.ml-agents/Runtime/Academy.cs68-115](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L68-L115)

 
## Training vs Inference Modes

 The toolkit supports two primary operational modes:

 
### Training Mode

 Driven by the Python `mlagents-learn` utility.

 
 - The `Academy` connects to the Python process via an `ICommunicator` [com.unity.ml-agents/Runtime/Academy.cs162](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L162-L162)
 - Training metrics are monitored via **TensorBoard** [docs/Training-ML-Agents.md91-95](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-ML-Agents.md?plain=1#L91-L95)
 - Supports algorithms like **PPO**, **SAC**, and **MA-POCA** for cooperative multi-agent scenarios [docs/Training-Configuration-File.md24-31](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-Configuration-File.md?plain=1#L24-L31)
 
 
### Inference Mode

 Uses trained models locally within Unity.

 
 - Employs the **Unity Inference Engine** (Sentis) for cross-platform model execution [com.unity.ml-agents/package.json8](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L8-L8)
 - Loads `.onnx` model files exported after training [docs/Training-ML-Agents.md96-99](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-ML-Agents.md?plain=1#L96-L99)
 - Managed by `ModelRunner` to handle tensor execution [com.unity.ml-agents/Runtime/Academy.cs165](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L165-L165)
 
 Sources: [docs/Training-ML-Agents.md39-105](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-ML-Agents.md?plain=1#L39-L105) [com.unity.ml-agents/CHANGELOG.md14-25](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/CHANGELOG.md?plain=1#L14-L25)

 
## Package Structure

 The ML-Agents Toolkit is modularized into several components:

 
| Package | Language | Purpose |
|---|---|---|
| com.unity.ml-agents | C# | Core Unity SDK for Agent/Academy logic com.unity.ml-agents/package.json2-6 |
| mlagents | Python | Training algorithms (PPO, SAC, etc.) and CLI ml-agents/mlagents/trainers/__init__.py1-6 |
| mlagents_envs | Python | API for interacting with Unity environments ml-agents-envs/mlagents_envs/__init__.py1-6 |

 **Current Versions (v4.0.3):**

 
 - Unity Package: `4.0.3` [com.unity.ml-agents/package.json4](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L4-L4)
 - Minimum Unity Version: `6000.0` [com.unity.ml-agents/package.json5](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L5-L5)
 - Sentis Dependency: `2.6.1` [com.unity.ml-agents/package.json8](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L8-L8)
 
 Sources: [com.unity.ml-agents/package.json1-16](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L1-L16) [com.unity.ml-agents/CHANGELOG.md8-15](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/CHANGELOG.md?plain=1#L8-L15)
