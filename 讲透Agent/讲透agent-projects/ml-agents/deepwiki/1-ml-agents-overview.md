<!-- source: DeepWiki mcp.deepwiki.com · repo Unity-Technologies/ml-agents · page 1 ML-Agents Overview · fetched 2026-10-30 -->

# ML-Agents Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [com.unity.ml-agents/CHANGELOG.md](com.unity.ml-agents/CHANGELOG.md)
- [com.unity.ml-agents/Runtime/Academy.cs](com.unity.ml-agents/Runtime/Academy.cs)
- [com.unity.ml-agents/package.json](com.unity.ml-agents/package.json)
- [docs/Background-Machine-Learning.md](docs/Background-Machine-Learning.md)
- [docs/Background-Unity.md](docs/Background-Unity.md)
- [docs/FAQ.md](docs/FAQ.md)
- [docs/Getting-Started.md](docs/Getting-Started.md)
- [docs/Learning-Environment-Create-New.md](docs/Learning-Environment-Create-New.md)
- [docs/Learning-Environment-Design-Agents.md](docs/Learning-Environment-Design-Agents.md)
- [docs/Learning-Environment-Design.md](docs/Learning-Environment-Design.md)
- [docs/Learning-Environment-Examples.md](docs/Learning-Environment-Examples.md)
- [docs/Learning-Environment-Executable.md](docs/Learning-Environment-Executable.md)
- [docs/ML-Agents-Overview.md](docs/ML-Agents-Overview.md)
- [docs/ML-Agents-Toolkit-Documentation.md](docs/ML-Agents-Toolkit-Documentation.md)
- [docs/Readme.md](docs/Readme.md)
- [docs/Training-Configuration-File.md](docs/Training-Configuration-File.md)
- [docs/Training-ML-Agents.md](docs/Training-ML-Agents.md)
- [localized_docs/RU/README.md](localized_docs/RU/README.md)
- [localized_docs/TR/README.md](localized_docs/TR/README.md)
- [localized_docs/TR/docs/Getting-Started.md](localized_docs/TR/docs/Getting-Started.md)
- [ml-agents-envs/mlagents_envs/__init__.py](ml-agents-envs/mlagents_envs/__init__.py)
- [ml-agents/mlagents/trainers/__init__.py](ml-agents/mlagents/trainers/__init__.py)
- [utils/validate_versions.py](utils/validate_versions.py)

</details>



The Unity ML-Agents Toolkit is a comprehensive framework that enables Unity environments to serve as training grounds for machine learning agents. This document provides an architectural overview of the toolkit, covering the core Unity SDK components, Python training system, and communication infrastructure that bridges game environments with machine learning algorithms.

For specific implementation details of Unity components, see [Unity SDK Components](#2). For Python training system internals, see [Python Training System](#3). For communication protocol details, see [Unity-Python Communication](#4).

## System Architecture

ML-Agents implements a distributed architecture where Unity provides the simulation environment while Python handles the machine learning algorithms. The system operates through a client-server model connected via gRPC communication.

### Overall System Design

```mermaid
graph TB
    subgraph "Unity Environment (C#)"
        [Academy] --> [Agent]
        [Agent] --> [BehaviorParameters]
        [Agent] --> [ISensor]
        [Agent] --> [IActuator]
        [BehaviorParameters] --> [ModelRunner]
        [Academy] --> [RpcCommunicator]
    end
    
    subgraph "Python Training Environment"
        [mlagents-learn] --> [TrainerController]
        [TrainerController] --> [Trainers]
        [TrainerController] --> [SubprocessEnvManager]
        [SubprocessEnvManager] --> [UnityEnvironment]
    end
    
    [RpcCommunicator] <== "gRPC / Protobuf" ==> [UnityEnvironment]
    
    subgraph "Local Inference"
        [ModelRunner] -. "Sentis/ONNX" .-> [TrainedModel]
    end
```

Sources: [com.unity.ml-agents/Runtime/Academy.cs:13-67](), [com.unity.ml-agents/Runtime/Agent.cs:1-50](), [ml-agents/mlagents/trainers/learn.py:1-40](), [docs/ML-Agents-Overview.md:35-65]()

### Core Component Relationships

The ML-Agents architecture follows a hierarchical pattern where the `Academy` manages the global training environment, `Agent` instances implement individual behaviors, and various supporting components handle observations, actions, and communication.

```mermaid
graph TB
    subgraph "Agent Logic [Agent.cs]"
        [Agent] --> [CollectObservations]
        [Agent] --> [OnActionReceived]
        [Agent] --> [OnEpisodeBegin]
    end
    
    subgraph "Decision Flow [BehaviorParameters.cs]"
        [BehaviorParameters] --> [HeuristicPolicy]
        [BehaviorParameters] --> [SentisPolicy]
        [BehaviorParameters] --> [RemotePolicy]
    end
    
    subgraph "Sensor System [ISensor.cs]"
        [VectorSensor]
        [RayPerceptionSensor]
        [CameraSensor]
    end

    [Agent] -- "Uses" --> [BehaviorParameters]
    [Agent] -- "Populates" --> [VectorSensor]
```

Sources: [docs/Learning-Environment-Design-Agents.md:44-84](), [com.unity.ml-agents/Runtime/Academy.cs:165-180](), [com.unity.ml-agents/Runtime/Agent.cs:200-533]()

## Key Components

### Academy
The `Academy` class serves as the central coordinator for the ML-Agents system. It operates as a singleton that manages environment stepping, communicator connections, and global training state. As of version 4.0.0, it supports Unity 6000.0+ and integrates with the latest Sentis inference engine [com.unity.ml-agents/package.json:1-12]().

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `Academy` | Global environment management | `EnvironmentStep()`, `LazyInitialize()` [com.unity.ml-agents/Runtime/Academy.cs:43-132]() |
| `AcademyFixedUpdateStepper` | Internal helper to step Academy | `FixedUpdate()` [com.unity.ml-agents/Runtime/Academy.cs:31-46]() |
| `StatsRecorder` | Metrics collection | `Add()`, statistics recording |

Sources: [com.unity.ml-agents/Runtime/Academy.cs:40-160]()

### Agent
The `Agent` class represents individual learning entities. Each agent observes its environment via `CollectObservations`, receives actions through `OnActionReceived`, and provides rewards to guide the learning process [docs/Learning-Environment-Design-Agents.md:66-84]().

- **OnEpisodeBegin()**: Called to reset the environment for a new training cycle [docs/Learning-Environment-Create-New.md:136-150]().
- **Heuristic()**: Allows manual control of the agent for debugging or player-controlled behavior [docs/Learning-Environment-Design-Agents.md:78-83]().
- **RequestDecision()**: Triggers the observation-decision-action cycle [docs/Learning-Environment-Design-Agents.md:105-120]().

Sources: [com.unity.ml-agents/Runtime/Agent.cs:206-600](), [docs/Learning-Environment-Design-Agents.md:1-100]()

### Communication Infrastructure

ML-Agents uses gRPC for communication between Unity and Python. The system follows semantic versioning on the communication protocol to ensure compatibility.

- **API Version**: Current protocol version is `1.5.0` [com.unity.ml-agents/Runtime/Academy.cs:104-104]().
- **Port Configuration**: Default Editor training port is `5004`, or specified via `--mlagents-port` [com.unity.ml-agents/Runtime/Academy.cs:112-114]().
- **Side Channels**: Used for non-RL data exchange, such as environment parameters or engine configuration [com.unity.ml-agents/Runtime/Academy.cs:10-10]().

Sources: [com.unity.ml-agents/Runtime/Academy.cs:68-115]()

## Training vs Inference Modes

The toolkit supports two primary operational modes:

### Training Mode
Driven by the Python `mlagents-learn` utility.
1. The `Academy` connects to the Python process via an `ICommunicator` [com.unity.ml-agents/Runtime/Academy.cs:162-162]().
2. Training metrics are monitored via **TensorBoard** [docs/Training-ML-Agents.md:91-95]().
3. Supports algorithms like **PPO**, **SAC**, and **MA-POCA** for cooperative multi-agent scenarios [docs/Training-Configuration-File.md:24-31]().

### Inference Mode  
Uses trained models locally within Unity.
1. Employs the **Unity Inference Engine** (Sentis) for cross-platform model execution [com.unity.ml-agents/package.json:8-8]().
2. Loads `.onnx` model files exported after training [docs/Training-ML-Agents.md:96-99]().
3. Managed by `ModelRunner` to handle tensor execution [com.unity.ml-agents/Runtime/Academy.cs:165-165]().

Sources: [docs/Training-ML-Agents.md:39-105](), [com.unity.ml-agents/CHANGELOG.md:14-25]()

## Package Structure

The ML-Agents Toolkit is modularized into several components:

| Package | Language | Purpose |
|---------|----------|---------|
| `com.unity.ml-agents` | C# | Core Unity SDK for Agent/Academy logic [com.unity.ml-agents/package.json:2-6](). |
| `mlagents` | Python | Training algorithms (PPO, SAC, etc.) and CLI [ml-agents/mlagents/trainers/__init__.py:1-6](). |
| `mlagents_envs` | Python | API for interacting with Unity environments [ml-agents-envs/mlagents_envs/__init__.py:1-6](). |

**Current Versions (v4.0.3):**
- Unity Package: `4.0.3` [com.unity.ml-agents/package.json:4-4]()
- Minimum Unity Version: `6000.0` [com.unity.ml-agents/package.json:5-5]()
- Sentis Dependency: `2.6.1` [com.unity.ml-agents/package.json:8-8]()

Sources: [com.unity.ml-agents/package.json:1-16](), [com.unity.ml-agents/CHANGELOG.md:8-15]()

---

