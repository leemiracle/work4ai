> 来源: [https://deepwiki.com/allenai/ai2thor/3-core-agent-system](https://deepwiki.com/allenai/ai2thor/3-core-agent-system)
> DeepWiki allenai/ai2thor | Last indexed: 16 September 2025 (24f798

# Core Agent System

  Relevant source files 
 - [ai2thor/hooks/metadata_hook.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/hooks/metadata_hook.py)
 - [ai2thor/util/metrics.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/util/metrics.py)
 - [ai2thor/util/trials.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/util/trials.py)
 - [fpin_tutorial.py](https://github.com/allenai/ai2thor/blob/24f79883/fpin_tutorial.py)
 - [unity/Assets/Scenes/FloorPlan_Train2_3/NavMesh.asset](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scenes/FloorPlan_Train2_3/NavMesh.asset)
 - [unity/Assets/Scripts/ActionDispatcher.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ActionDispatcher.cs)
 - [unity/Assets/Scripts/AgentManager.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/AgentManager.cs)
 - [unity/Assets/Scripts/ArmAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ArmAgentController.cs)
 - [unity/Assets/Scripts/ArmController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ArmController.cs)
 - [unity/Assets/Scripts/BaseAgentComponent.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseAgentComponent.cs)
 - [unity/Assets/Scripts/BaseFPSAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs)
 - [unity/Assets/Scripts/Contains.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/Contains.cs)
 - [unity/Assets/Scripts/ContinuousMovement.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ContinuousMovement.cs)
 - [unity/Assets/Scripts/DebugDiscreteAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/DebugDiscreteAgentController.cs)
 - [unity/Assets/Scripts/DebugInputField.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/DebugInputField.cs)
 - [unity/Assets/Scripts/DiscreteHidenSeekAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/DiscreteHidenSeekAgentController.cs)
 - [unity/Assets/Scripts/DiscretePointClickAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/DiscretePointClickAgentController.cs)
 - [unity/Assets/Scripts/DroneFPSAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/DroneFPSAgentController.cs)
 - [unity/Assets/Scripts/FpinAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/FpinAgentController.cs)
 - [unity/Assets/Scripts/IK_Robot_Arm_Controller.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/IK_Robot_Arm_Controller.cs)
 - [unity/Assets/Scripts/InstantiatePrefabTest.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/InstantiatePrefabTest.cs)
 - [unity/Assets/Scripts/LocobotFPSAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/LocobotFPSAgentController.cs)
 - [unity/Assets/Scripts/ObjectHighlightController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ObjectHighlightController.cs)
 - [unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs)
 - [unity/Assets/Scripts/PhysicsSceneManager.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/PhysicsSceneManager.cs)
 - [unity/Assets/Scripts/PlayerControllers.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/PlayerControllers.cs)
 - [unity/Assets/Scripts/RobotArmTest/Stretch_Arm_Solver.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/RobotArmTest/Stretch_Arm_Solver.cs)
 - [unity/Assets/Scripts/RobotArmTest/robot_arm_rig_gripper.prefab](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/RobotArmTest/robot_arm_rig_gripper.prefab)
 - [unity/Assets/Scripts/RobotArmTest/stretch_arm_rig_gripper.prefab](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/RobotArmTest/stretch_arm_rig_gripper.prefab)
 - [unity/Assets/Scripts/SimObjPhysics.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/SimObjPhysics.cs)
 - [unity/Assets/Scripts/SimObjType.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/SimObjType.cs)
 - [unity/Assets/Scripts/StretchAgentController.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/StretchAgentController.cs)
 - [unity/Assets/Scripts/Stretch_Robot_Arm_Controller.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/Stretch_Robot_Arm_Controller.cs)
 - [unity/Assets/Scripts/UtilityFunctions.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/UtilityFunctions.cs)
 - [unity/Assets/Standard Assets/Characters/FirstPersonCharacter/Models/stretch_robot_grp.fbx](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Standard Assets/Characters/FirstPersonCharacter/Models/stretch_robot_grp.fbx)
 - [unity/Assets/Standard Assets/Characters/FirstPersonCharacter/Prefabs/FPSController.prefab](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Standard Assets/Characters/FirstPersonCharacter/Prefabs/FPSController.prefab)
 - [unity/Assets/UnitTests/TestDispatcher.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/UnitTests/TestDispatcher.cs)
 - [unity/Assets/UnitTests/TestThirdPartyCameraAndMainCamera.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/UnitTests/TestThirdPartyCameraAndMainCamera.cs)
 - [unity/ProjectSettings/ProjectSettings.asset](https://github.com/allenai/ai2thor/blob/24f79883/unity/ProjectSettings/ProjectSettings.asset)
 
  
## Purpose and Scope

 The Core Agent System forms the foundation of AI2-THOR's embodied AI simulation framework, providing a hierarchical architecture for different types of virtual agents that can perceive and interact with 3D environments. This system manages agent initialization, movement, action execution, and physics simulation across multiple specialized agent types including standard first-person controllers, robotic arms, drones, and mobile robots.

 For information about scene management and object interaction, see [Object Interaction System](https://deepwiki.com/allenai/ai2thor/7-object-interaction-system). For details about communication protocols and Python API integration, see [Python API and Communication](https://deepwiki.com/allenai/ai2thor/4-python-api-and-communication).

 
## Agent Controller Hierarchy

 The agent system is built around an inheritance hierarchy with `BaseFPSAgentController` as the abstract foundation:

 
```

```

 **Sources:** [unity/Assets/Scripts/BaseFPSAgentController.cs28-29](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs#L28-L29) [unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs28](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs#L28-L28) [unity/Assets/Scripts/AgentManager.cs33](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/AgentManager.cs#L33-L33) [unity/Assets/Scripts/ArmAgentController.cs11](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ArmAgentController.cs#L11-L11)

 
## BaseFPSAgentController Foundation

 The `BaseFPSAgentController` class provides core functionality shared by all agent types:

 
### Core Components and Properties

 
| Component | Purpose | Key Properties |
|---|---|---|
| BaseAgentComponent | Unity MonoBehaviour wrapper | Camera, hand transforms, visibility capsules |
| CharacterController | Unity physics movement | Collision detection, ground constraints |
| AgentManager | Scene-level coordination | Multi-agent management, bounds tracking |
| PhysicsSceneManager | Physics simulation control | Object spawning, scene setup |

 
### Essential Agent State Management

 The agent system maintains several critical state variables:

 
```

```

 **Sources:** [unity/Assets/Scripts/BaseFPSAgentController.cs196](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs#L196-L196) [unity/Assets/Scripts/BaseFPSAgentController.cs294-312](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs#L294-L312) [unity/Assets/Scripts/BaseFPSAgentController.cs445-479](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs#L445-L479)

 
### Movement and Navigation System

 The base controller implements grid-based and continuous movement through several key methods:

 
 - `getReachablePositions()` - Computes valid agent positions using capsule casting
 - `CastBodyTrayectory()` - Physics-based collision detection for movement validation
 - `handObjectCanFitInPosition()` - Validates positions considering held objects
 
 **Sources:** [unity/Assets/Scripts/BaseFPSAgentController.cs526-711](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs#L526-L711) [unity/Assets/Scripts/BaseFPSAgentController.cs1459-1515](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs#L1459-L1515)

 
## PhysicsRemoteFPSAgentController Extensions

 The `PhysicsRemoteFPSAgentController` extends the base class with physics-based capabilities:

 
### Physics Integration Features

 
| Feature | Implementation | Purpose |
|---|---|---|
| Object Pickup/Drop | PickupObject(), DropHandObject() | Manipulate scene objects |
| Temperature System | SetTemperatureDecayTime() | Object state management |
| Mass Properties | SetMassProperties() | Dynamic physics tuning |
| Collision Handling | CheckIfAgentCanRotate() | Movement validation |

 
### Rotation and Look Controls

 The physics controller implements sophisticated rotation checking to prevent object collisions:

 
```

```

 **Sources:** [unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs687-734](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs#L687-L734) [unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs513-625](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs#L513-L625)

 
## Specialized Agent Types

 
### ArmAgentController for Robotic Manipulation

 The `ArmAgentController` provides a foundation for robotic arm simulation with several concrete implementations:

 
| Controller Type | Use Case | Key Features |
|---|---|---|
| StretchAgentController | Stretch Research Robot | Telescoping arm, dual cameras |
| KinovaArmAgentController | Kinova robotic arm | 6-DOF manipulation |
| ArticulatedAgentController | General articulated robots | Multi-joint coordination |

 **Sources:** [unity/Assets/Scripts/ArmAgentController.cs11-13](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ArmAgentController.cs#L11-L13) [unity/Assets/Scripts/StretchAgentController.cs12](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/StretchAgentController.cs#L12-L12)

 
### DroneFPSAgentController for Aerial Agents

 The drone controller implements 3D movement with physics constraints:

 
```

```

 **Sources:** [unity/Assets/Scripts/DroneFPSAgentController.cs12](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/DroneFPSAgentController.cs#L12-L12) [unity/Assets/Scripts/DroneFPSAgentController.cs16-22](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/DroneFPSAgentController.cs#L16-L22)

 
## Agent Lifecycle and Coordination

 
### Initialization Process

 Agent initialization follows a structured sequence managed by `AgentManager`:

 
 - **Controller Selection** - `SetUpPhysicsController()`, `SetUpArmController()`, etc.
 - **Body Initialization** - `InitializeBody()` sets physical parameters
 - **Camera Setup** - Field of view, clipping planes, render targets
 - **Physics Configuration** - Collision detection, mass properties
 - **Multi-agent Coordination** - Position validation for additional agents
 
 **Sources:** [unity/Assets/Scripts/AgentManager.cs219-372](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/AgentManager.cs#L219-L372) [unity/Assets/Scripts/BaseFPSAgentController.cs745-912](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs#L745-L912)

 
### Action Execution Framework

 The system uses `ActionDispatcher` to route commands to appropriate agent methods:

 
```

```

 **Sources:** [unity/Assets/Scripts/ActionDispatcher.cs73-92](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ActionDispatcher.cs#L73-L92) [unity/Assets/Scripts/BaseFPSAgentController.cs445-512](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs#L445-L512)

 
## Communication and Control Interface

 
### Multi-Modal Communication

 The agent system supports multiple communication protocols through `AgentManager`:

 
| Protocol | Implementation | Use Case |
|---|---|---|
| WSGI Server | WsgiServer | HTTP-based communication |
| FIFO Pipes | FifoServer.Client | Named pipe communication |
| WebGL Interface | JavaScriptInterface | Browser-based control |

 
### Debug and Development Tools

 The `DebugInputField` provides interactive development capabilities:

 
 - Text-based command input with auto-completion
 - Real-time agent state visualization
 - Multi-agent switching and control
 - Physics parameter tuning
 
 **Sources:** [unity/Assets/Scripts/AgentManager.cs72-77](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/AgentManager.cs#L72-L77) [unity/Assets/Scripts/AgentManager.cs143-158](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/AgentManager.cs#L143-L158) [unity/Assets/Scripts/DebugInputField.cs16-17](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/DebugInputField.cs#L16-L17)

 
### Metadata and State Reporting

 Each agent generates comprehensive metadata through `generateMetadataWrapper()`:

 
 - Agent position, rotation, and camera parameters
 - Visible object inventories with distance and visibility data
 - Physics state including velocity and collision status
 - Specialized data for arm positions, drone status, etc.
 
 **Sources:** [unity/Assets/Scripts/BaseFPSAgentController.cs3023-3122](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/BaseFPSAgentController.cs#L3023-L3122) [unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs203-207](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/PhysicsRemoteFPSAgentController.cs#L203-L207)
