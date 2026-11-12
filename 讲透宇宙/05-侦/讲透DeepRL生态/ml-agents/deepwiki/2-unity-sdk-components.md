> 来源: [https://deepwiki.com/Unity-Technologies/ml-agents/2-unity-sdk-components](https://deepwiki.com/Unity-Technologies/ml-agents/2-unity-sdk-components)
> DeepWiki Unity-Technologies/ml-agents | Last indexed: 22 May 2026 (d52b00

# Unity SDK Components

  Relevant source files 
 - [Project/Assets/ML-Agents/Examples/SharedAssets/Scripts/ModelOverrider.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/Project/Assets/ML-Agents/Examples/SharedAssets/Scripts/ModelOverrider.cs)
 - [com.unity.ml-agents/CHANGELOG.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/CHANGELOG.md?plain=1)
 - [com.unity.ml-agents/Editor/BehaviorParametersEditor.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Editor/BehaviorParametersEditor.cs)
 - [com.unity.ml-agents/Runtime/Academy.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs)
 - [com.unity.ml-agents/Runtime/Actuators/IActionReceiver.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Actuators/IActionReceiver.cs)
 - [com.unity.ml-agents/Runtime/Actuators/IDiscreteActionMask.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Actuators/IDiscreteActionMask.cs)
 - [com.unity.ml-agents/Runtime/Agent.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs)
 - [com.unity.ml-agents/Runtime/Communicator/CommunicatorFactory.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Communicator/CommunicatorFactory.cs)
 - [com.unity.ml-agents/Runtime/Demonstrations/DemonstrationRecorder.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Demonstrations/DemonstrationRecorder.cs)
 - [com.unity.ml-agents/Runtime/Integrations/Match3/Match3Sensor.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Integrations/Match3/Match3Sensor.cs)
 - [com.unity.ml-agents/Runtime/Policies/BehaviorParameters.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Policies/BehaviorParameters.cs)
 - [com.unity.ml-agents/Runtime/Policies/BrainParameters.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Policies/BrainParameters.cs)
 - [com.unity.ml-agents/Runtime/Sensors/Reflection/ObservableAttribute.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Sensors/Reflection/ObservableAttribute.cs)
 - [com.unity.ml-agents/Runtime/SideChannels/SideChannelManager.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/SideChannels/SideChannelManager.cs)
 - [com.unity.ml-agents/Runtime/Timer.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Timer.cs)
 - [com.unity.ml-agents/package.json](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json)
 - [docs/Installation-Anaconda-Windows.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation-Anaconda-Windows.md?plain=1)
 - [docs/Installation.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1)
 - [docs/Migrating.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Migrating.md?plain=1)
 - [docs/Training-on-Amazon-Web-Service.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Amazon-Web-Service.md?plain=1)
 - [docs/Training-on-Microsoft-Azure.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Microsoft-Azure.md?plain=1)
 - [ml-agents-envs/README.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/README.md?plain=1)
 - [ml-agents-envs/mlagents_envs/__init__.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/__init__.py)
 - [ml-agents/README.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/README.md?plain=1)
 - [ml-agents/mlagents/trainers/__init__.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/__init__.py)
 - [utils/validate_versions.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/utils/validate_versions.py)
 
  The Unity ML-Agents SDK provides the core C# components for creating reinforcement learning environments within Unity. These components handle agent behavior, observation collection, action execution, and integration with external training systems. This page provides an overview of the main components and their relationships.

 
## Unity SDK Architecture

 The ML-Agents Unity SDK is structured around several key components that work together to create a complete learning environment:

 
```

```

 Sources:

 
 - [com.unity.ml-agents/Runtime/Academy.cs49-67](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L49-L67)
 - [com.unity.ml-agents/Runtime/Agent.cs110-162](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L110-L162)
 - [com.unity.ml-agents/package.json1-16](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L1-L16)
 
 
## Component Categories

 The Unity SDK components are organized into four main categories, each covered in detail in the following sections:

 
### Academy and Training Environment

 The `Academy` singleton orchestrates the entire ML-Agents environment, managing the simulation loop, episode lifecycle, and coordination between agents and external training processes. It provides the foundation for all ML-Agents functionality.

 **Key Components:**

 
 - `Academy` - Central coordinator and singleton [com.unity.ml-agents/Runtime/Academy.cs66-67](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L66-L67)
 - `AcademyFixedUpdateStepper` - Helper class to step the Academy during `FixedUpdate` phase [com.unity.ml-agents/Runtime/Academy.cs31-46](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L31-L46)
 - `ICommunicator` - Interface for managing communication between Unity and Python [com.unity.ml-agents/Runtime/Academy.cs162](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L162-L162)
 
 For detailed information, see [Academy and Training Environment](https://deepwiki.com/Unity-Technologies/ml-agents/2.1-academy-and-training-environment).

 
### Agent and Behavior Parameters

 The `Agent` class is the core component that transforms Unity GameObjects into intelligent agents. The `BehaviorParameters` component configures how agents make decisions and interact with their environment.

 **Key Components:**

 
 - `Agent` - Main component for implementing agent logic [com.unity.ml-agents/Runtime/Agent.cs110-113](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L110-L113)
 - `BehaviorParameters` - Configuration for agent behavior and decision-making [com.unity.ml-agents/Runtime/Agent.cs134-135](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L134-L135)
 - `AgentInfo` - Struct containing agent state like rewards, done flags, and actions [com.unity.ml-agents/Runtime/Agent.cs19-20](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L19-L20)
 
 For detailed information, see [Agent and Behavior Parameters](https://deepwiki.com/Unity-Technologies/ml-agents/2.2-agent-and-behavior-parameters).

 
### Sensors and Observations

 The sensor system provides agents with information about their environment through various observation types. All sensors implement the `ISensor` interface and can be combined to create rich observation spaces.

 **Key Components:**

 
 - `VectorSensor` - Numerical observations [com.unity.ml-agents/Runtime/Agent.cs124-125](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L124-L125)
 - `CameraSensor` - Visual observations from cameras [com.unity.ml-agents/Runtime/Agent.cs123](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L123-L123)
 - `RayPerceptionSensor` - Raycast-based observations [com.unity.ml-agents/Runtime/Agent.cs124](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L124-L124)
 
 For detailed information, see [Sensors and Observations](https://deepwiki.com/Unity-Technologies/ml-agents/2.3-sensors-and-observations).

 
### Inference and Model Running

 The inference system handles loading and running trained neural network models within Unity using the **Sentis** inference engine.

 **Key Components:**

 
 - `ModelRunner` - Manages the execution of neural network models [com.unity.ml-agents/Runtime/Academy.cs165](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L165-L165)
 - `ModelOverrider` - Utility class to allow the `ModelAsset` file for an agent to be overridden during inference [Project/Assets/ML-Agents/Examples/SharedAssets/Scripts/ModelOverrider.cs24-25](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/Project/Assets/ML-Agents/Examples/SharedAssets/Scripts/ModelOverrider.cs#L24-L25)
 
 For detailed information, see [Inference and Model Running](https://deepwiki.com/Unity-Technologies/ml-agents/2.4-inference-and-model-running).

 Sources:

 
 - [com.unity.ml-agents/Runtime/Academy.cs49-166](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L49-L166)
 - [com.unity.ml-agents/Runtime/Agent.cs110-162](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L110-L162)
 - [com.unity.ml-agents/CHANGELOG.md14](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/CHANGELOG.md?plain=1#L14-L14)
 
 
## Unity SDK Integration

 The Unity SDK components integrate with Unity's GameObject system through MonoBehaviour components and interfaces. The following diagram shows how these components work together in the Unity editor:

 
```

```

 Sources:

 
 - [com.unity.ml-agents/Runtime/Agent.cs110-157](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L110-L157)
 - [com.unity.ml-agents/Runtime/Academy.cs31-46](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L31-L46)
 - [com.unity.ml-agents/Runtime/Academy.cs43](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Academy.cs#L43-L43)
 
 
## Core Interfaces and Data Structures

 The Unity SDK is built around several key interfaces that provide a consistent API for ML-Agents functionality:

 
```

```

 These interfaces define the contracts for:

 
 - **`ISensor`** - How observations are collected and provided to agents [docs/Migrating.md79-118](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Migrating.md?plain=1#L79-L118)
 - **`IActuator`** - How actions are processed and executed by agents [docs/Migrating.md74-76](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Migrating.md?plain=1#L74-L76)
 - **`IActionReceiver`** - Interface for components that receive actions [com.unity.ml-agents/Runtime/Agent.cs96](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L96-L96)
 - **`ActionBuffers`** - Container for continuous and discrete action data [com.unity.ml-agents/Runtime/Agent.cs24](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L24-L24)
 
 Sources:

 
 - [com.unity.ml-agents/Runtime/Agent.cs19-88](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L19-L88)
 - [docs/Migrating.md34-122](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Migrating.md?plain=1#L34-L122)
 
 
## Package Structure and Dependencies

 The Unity ML-Agents SDK is distributed as a Unity package (`com.unity.ml-agents`) with the following key dependencies:

 
 - **Sentis** (`com.unity.ai.inference`): The neural network inference engine [com.unity.ml-agents/package.json8](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L8-L8)
 - **Unity Modules**: Includes `imageconversion`, `jsonserialize`, and `physics` [com.unity.ml-agents/package.json9-11](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L9-L11)
 
 As of version 4.0.0, the extension package `com.unity.ml-agents.extensions` was merged into the main package [com.unity.ml-agents/CHANGELOG.md39](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/CHANGELOG.md?plain=1#L39-L39)

 Sources:

 
 - [com.unity.ml-agents/package.json1-16](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/package.json#L1-L16)
 - [com.unity.ml-agents/CHANGELOG.md34-40](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/CHANGELOG.md?plain=1#L34-L40)
 
 
## Getting Started

 To begin using the Unity ML-Agents SDK components:

 
 - **Install Unity**: Version 6000.0 or later is required [docs/Installation.md34](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L34-L34)
 - **Install the Package**: Add `com.unity.ml-agents` via the Package Manager [docs/Installation.md92-98](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L92-L98)
 - **Implement an Agent**: Subclass the `Agent` class and implement `CollectObservations` and `OnActionReceived` [com.unity.ml-agents/Runtime/Agent.cs115-132](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L115-L132)
 
 **Basic Agent Setup Example:**

 
```

```

 For detailed information on each component category, refer to the specific sections:

 
 - [Academy and Training Environment](https://deepwiki.com/Unity-Technologies/ml-agents/2.1-academy-and-training-environment)
 - [Agent and Behavior Parameters](https://deepwiki.com/Unity-Technologies/ml-agents/2.2-agent-and-behavior-parameters)
 - [Sensors and Observations](https://deepwiki.com/Unity-Technologies/ml-agents/2.3-sensors-and-observations)
 - [Inference and Model Running](https://deepwiki.com/Unity-Technologies/ml-agents/2.4-inference-and-model-running)
 
 Sources:

 
 - [docs/Installation.md21-32](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L21-L32)
 - [com.unity.ml-agents/Runtime/Agent.cs115-157](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L115-L157)
