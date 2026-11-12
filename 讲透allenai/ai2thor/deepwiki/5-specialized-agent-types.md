<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/ai2thor · page 5 Specialized Agent Types · fetched 2026-10-30 -->

# Specialized Agent Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ai2thor/interact.py](ai2thor/interact.py)
- [ai2thor/offline_controller.py](ai2thor/offline_controller.py)
- [ai2thor/robot_controller.py](ai2thor/robot_controller.py)
- [ai2thor/tests/data/arm/object_drop.json](ai2thor/tests/data/arm/object_drop.json)
- [ai2thor/tests/data/arm/pickup_object.json](ai2thor/tests/data/arm/pickup_object.json)
- [ai2thor/tests/data/arm/pickup_plate_before_intersect.json](ai2thor/tests/data/arm/pickup_plate_before_intersect.json)
- [ai2thor/tests/data/arm/procthor_train_1.json](ai2thor/tests/data/arm/procthor_train_1.json)
- [ai2thor/tests/data/arm/procthor_train_1_laptop.json](ai2thor/tests/data/arm/procthor_train_1_laptop.json)
- [ai2thor/tests/test_arm.py](ai2thor/tests/test_arm.py)
- [ai2thor/util/scene_yaml_edit.py](ai2thor/util/scene_yaml_edit.py)
- [ai2thor/video_controller.py](ai2thor/video_controller.py)
- [arm_test/arm_counter_30fps_fixed_update.py](arm_test/arm_counter_30fps_fixed_update.py)
- [arm_test/arm_counter_30fps_fixed_update_random_sleep.py](arm_test/arm_counter_30fps_fixed_update_random_sleep.py)
- [arm_test/arm_counter_30fps_simulate.py](arm_test/arm_counter_30fps_simulate.py)
- [arm_test/arm_counter_30fps_simulate_pause_return_start.py](arm_test/arm_counter_30fps_simulate_pause_return_start.py)
- [arm_test/arm_stuck_test.py](arm_test/arm_stuck_test.py)
- [arm_test/arm_stuck_test_wait_frame.py](arm_test/arm_stuck_test_wait_frame.py)
- [arm_test/base.py](arm_test/base.py)
- [arm_test/check_determinism_different_machines.py](arm_test/check_determinism_different_machines.py)
- [arm_test/check_determinism_event_collision_different_machines.py](arm_test/check_determinism_event_collision_different_machines.py)
- [unity/Assets/Plugins/WebGL.jslib](unity/Assets/Plugins/WebGL.jslib)
- [unity/Assets/Scenes/Procedural/ProceduralAB.unity](unity/Assets/Scenes/Procedural/ProceduralAB.unity)
- [unity/Assets/Scripts/ArticulatedAgentController.cs](unity/Assets/Scripts/ArticulatedAgentController.cs)
- [unity/Assets/Scripts/ArticulatedAgentSolver.cs](unity/Assets/Scripts/ArticulatedAgentSolver.cs)
- [unity/Assets/Scripts/ArticulatedArmController.cs](unity/Assets/Scripts/ArticulatedArmController.cs)
- [unity/Assets/Scripts/ArticulatedArmExtender.cs](unity/Assets/Scripts/ArticulatedArmExtender.cs)
- [unity/Assets/Scripts/ArticulatedArmExtender.cs.meta](unity/Assets/Scripts/ArticulatedArmExtender.cs.meta)
- [unity/Assets/Scripts/ArticulatedArmJointSolver.cs](unity/Assets/Scripts/ArticulatedArmJointSolver.cs)
- [unity/Assets/Scripts/JavaScriptInterface.cs](unity/Assets/Scripts/JavaScriptInterface.cs)
- [unity/Assets/Scripts/NavMeshSetup.cs](unity/Assets/Scripts/NavMeshSetup.cs)
- [unity/Assets/Standard Assets/Characters/FirstPersonCharacter/Prefabs/ArticulatedFPSController.prefab](unity/Assets/Standard Assets/Characters/FirstPersonCharacter/Prefabs/ArticulatedFPSController.prefab)
- [unity/Assets/UnitTests/TestStretchArmMeta.cs](unity/Assets/UnitTests/TestStretchArmMeta.cs)
- [unity/Assets/WebGLTemplates/HideNSeek/TemplateData/script.js](unity/Assets/WebGLTemplates/HideNSeek/TemplateData/script.js)
- [unity/ProjectSettings/DynamicsManager.asset](unity/ProjectSettings/DynamicsManager.asset)
- [unity/ProjectSettings/TagManager.asset](unity/ProjectSettings/TagManager.asset)
- [unity/debug/test-arm-half-3.json](unity/debug/test-arm-half-3.json)
- [unity/debug/test-arm-half-limits-3.json](unity/debug/test-arm-half-limits-3.json)

</details>



This document covers the specialized agent implementations in AI2-THOR that extend beyond the basic `BaseFPSAgentController` functionality. These agents provide domain-specific capabilities such as robotic arm manipulation, articulated body physics, and specialized movement patterns. For core agent functionality and the base agent hierarchy, see [Core Agent System](#3).

## Agent Specialization Hierarchy

The specialized agents in AI2-THOR form an inheritance hierarchy that builds upon the base physics-enabled agent controller to provide specific capabilities for different use cases.

```mermaid
graph TD
    BASE["BaseFPSAgentController"] --> PHYSICS["PhysicsRemoteFPSAgentController"]
    BASE --> DEBUG["DebugFPSAgentController"]
    BASE --> DRONE["DroneFPSAgentController"]
    
    PHYSICS --> ARM["ArmAgentController"]
    PHYSICS --> FPIN["FpinAgentController"]
    
    ARM --> STRETCH["StretchAgentController"]
    ARM --> ARTIC["ArticulatedAgentController"]
    ARM --> LOCO["LocobotFPSAgentController"]
    
    ARTIC --> SOLVER["ArticulatedAgentSolver"]
    ARTIC --> ARMCTRL["ArticulatedArmController"]
    ARMCTRL --> JOINTS["ArticulatedArmJointSolver[]"]
```

**Sources:** [unity/Assets/Scripts/ArticulatedAgentController.cs:11-16](), [unity/Assets/Scripts/ArticulatedArmController.cs:8]()

## ArticulatedAgentController System

The `ArticulatedAgentController` represents the most sophisticated specialized agent implementation, designed for realistic robotic arm simulation using Unity's Articulation Body physics system.

### Core Components Architecture

```mermaid
graph TD
    AAC["ArticulatedAgentController"] --> AAC_INIT["InitializeBody()"]
    AAC --> AAC_TELEPORT["TeleportFull()"]
    AAC --> AAC_MOVE["MoveAgent()"]
    AAC --> AAC_ROTATE["RotateAgent()"]
    
    AAC --> ARM_IMPL["getArmImplementation()"]
    ARM_IMPL --> AACTL["ArticulatedArmController"]
    
    AACTL --> JOINTS_ARRAY["ArticulatedArmJointSolver[]"]
    JOINTS_ARRAY --> LIFT_JOINT["joints[0] - Lift"]
    JOINTS_ARRAY --> EXTEND_JOINT["joints[1] - Extend"]
    JOINTS_ARRAY --> WRIST_JOINT["joints[2] - Wrist"]
    
    AAC --> SOLVER_COMP["ArticulatedAgentSolver"]
    SOLVER_COMP --> BODY_MOVABLE["MovableContinuous"]
    SOLVER_COMP --> AB_PHYSICS["ArticulationBody"]
    
    AAC --> FLOOR_PHYSICS["Floor Friction Management"]
    FLOOR_PHYSICS --> HIGH_FRICTION["SetFloorColliderToHighFriction()"]
    FLOOR_PHYSICS --> LOW_FRICTION["SetFloorColliderToSlippery()"]
```

**Sources:** [unity/Assets/Scripts/ArticulatedAgentController.cs:11-17](), [unity/Assets/Scripts/ArticulatedArmController.cs:131-140](), [unity/Assets/Scripts/ArticulatedAgentSolver.cs:36]()

### Articulation Body Physics Integration

The articulated agent uses Unity's `ArticulationBody` system for realistic physics simulation, requiring specialized initialization and movement handling.

```mermaid
graph LR
    INIT["InitializeBody()"] --> AB_SETUP["ArticulationBody.TeleportRoot()"]
    AB_SETUP --> CAM_CONFIG["Camera Configuration"]
    CAM_CONFIG --> FRICTION_SETUP["Floor Collider Setup"]
    
    MOVE_CMD["Movement Command"] --> PREP_PARAMS["PrepToControlAgentFromAction()"]
    PREP_PARAMS --> CONT_UPDATE["ContinuousUpdate()"]
    CONT_UPDATE --> SHOULD_HALT["ShouldHalt()"]
    SHOULD_HALT --> FINISH_MOVE["FinishContinuousMove()"]
    
    TELEPORT["TeleportFull()"] --> COROUTINE["TeleportThenWait()"]
    COROUTINE --> AB_TELEPORT["ArticulationBody.TeleportRoot()"]
    AB_TELEPORT --> WAIT_FIXED["WaitForFixedUpdate"]
```

**Sources:** [unity/Assets/Scripts/ArticulatedAgentController.cs:45-129](), [unity/Assets/Scripts/ArticulatedAgentController.cs:297-307](), [unity/Assets/Scripts/ArticulatedAgentSolver.cs:73-115]()

## Articulated Arm Control System

The arm control system manages complex multi-joint robotic arm movements through a hierarchical joint solver architecture.

### Joint Control Architecture

```mermaid
graph TD
    ARM_MOVE["MoveArm() Command"] --> ARM_TARGET["moveArmTarget()"]
    ARM_BASE["MoveArmBase() Command"] --> ARM_BASE_IMPL["moveArmBase()"]
    WRIST_ROT["RotateWristRelative()"] --> WRIST_IMPL["rotateWrist()"]
    
    ARM_TARGET --> JOINT_PREP["prepAllTheThingsBeforeJointMoves()"]
    ARM_BASE_IMPL --> JOINT_PREP
    WRIST_IMPL --> JOINT_PREP
    
    JOINT_PREP --> JOINT_PARAMS["ArmMoveParams"]
    JOINT_PARAMS --> SOLVER_PREP["PrepToControlJointFromAction()"]
    
    SOLVER_PREP --> CONT_MOVE["ContinuousMovement.moveAB()"]
    CONT_MOVE --> JOINT_UPDATE["ControlJointFromAction()"]
    
    JOINT_UPDATE --> LIFT_DRIVE["yDrive - Lift Joint"]
    JOINT_UPDATE --> EXTEND_DRIVE["zDrive - Extend Joint"]
    JOINT_UPDATE --> ROTATE_DRIVE["xDrive - Rotate Joint"]
    
    JOINT_UPDATE --> HALT_CHECK["shouldHalt()"]
    HALT_CHECK --> LAST_STEP["lastStepCallback()"]
```

**Sources:** [unity/Assets/Scripts/ArticulatedArmController.cs:150-202](), [unity/Assets/Scripts/ArticulatedArmJointSolver.cs:72-131](), [unity/Assets/Scripts/ArticulatedArmJointSolver.cs:133-397]()

### Joint Movement State Management

The joint solver system manages individual joint states and coordinates movement across multiple degrees of freedom.

| Joint Type | Enum State | Drive Axis | Movement Range |
|------------|------------|------------|----------------|
| Lift | `ArmLiftState` | yDrive | -0.1832155f to 0.9177839f |
| Extend | `ArmExtendState` | zDrive | 0.0f to 0.516f |
| Rotate | `ArmRotateState` | xDrive | Unlimited rotation |

**Sources:** [unity/Assets/Scripts/ArticulatedArmJointSolver.cs:7-30](), [unity/Assets/Scripts/ArticulatedArmJointSolver.cs:63-67]()

## Agent Movement and Physics

### Continuous Movement System

The articulated agent implements sophisticated continuous movement with physics-based acceleration and deceleration.

```mermaid
graph TD
    MOVE_AGENT["MoveAgent()"] --> CALC_MASS["CalculateTotalMass()"]
    CALC_MASS --> MOVE_PARAMS["AgentMoveParams"]
    MOVE_PARAMS --> SOLVER_PREP["ArticulatedAgentSolver.PrepToControlAgentFromAction()"]
    
    SOLVER_PREP --> ACCEL_CALC["Acceleration Distance Calculation"]
    ACCEL_CALC --> CONT_UPDATE["ContinuousUpdate()"]
    
    CONT_UPDATE --> ACCEL_PHASE["Acceleration Phase"]
    CONT_UPDATE --> CRUISE_PHASE["Cruise Control Phase"]
    CONT_UPDATE --> DECEL_PHASE["Deceleration Phase"]
    
    ACCEL_PHASE --> FORCE_CALC["Force = forceScaler * distanceDelta * mass"]
    CRUISE_PHASE --> SPEED_CALC["Force = forceScaler * speedDelta * mass"]
    DECEL_PHASE --> BRAKE_CALC["Force = beginDecelerationSpeed * remainingDistance"]
    
    FORCE_CALC --> ADD_FORCE["ArticulationBody.AddRelativeForce()"]
    SPEED_CALC --> ADD_FORCE
    BRAKE_CALC --> ADD_FORCE
```

**Sources:** [unity/Assets/Scripts/ArticulatedAgentController.cs:559-610](), [unity/Assets/Scripts/ArticulatedAgentSolver.cs:117-367]()

### Physics State Management

The system manages physics state transitions and collision handling through friction control and halt detection.

```mermaid
graph LR
    START_MOVE["Start Movement"] --> SET_SLIPPERY["SetFloorColliderToSlippery()"]
    SET_SLIPPERY --> PHYSICS_MOVE["Physics Movement"]
    PHYSICS_MOVE --> HALT_CHECK["ApproximatelyNoChange()"]
    
    HALT_CHECK --> CONTINUE["Continue Movement"]
    HALT_CHECK --> HALT["Movement Complete"]
    
    HALT --> SET_FRICTION["SetFloorColliderToHighFriction()"]
    SET_FRICTION --> FINISH["ActionFinished"]
    
    CONTINUE --> PHYSICS_MOVE
```

**Sources:** [unity/Assets/Scripts/ArticulatedAgentController.cs:256-267](), [unity/Assets/Scripts/ArticulatedAgentController.cs:146-151](), [unity/Assets/Scripts/ArticulatedAgentSolver.cs:476-498]()

## Robot Controller Integration

The Python `robot_controller.py` provides a simplified interface for robotic agent interaction, particularly useful for testing and validation.

### Robot Controller Architecture

```mermaid
graph TD
    RC["robot_controller.Controller"] --> INIT_PARAMS["Initialization Parameters"]
    INIT_PARAMS --> HOST_PORT["host, port, agent_id"]
    INIT_PARAMS --> CAMERA_PARAMS["camera_near_plane, camera_far_plane"]
    INIT_PARAMS --> RENDER_PARAMS["width, height, depth_format"]
    
    RC --> STEP_METHOD["step()"]
    STEP_METHOD --> ACTION_PROC["Action Processing"]
    ACTION_PROC --> ROTATION_HANDLE["Rotation Handling"]
    ACTION_PROC --> POST_EVENT["_post_event()"]
    
    POST_EVENT --> EVENT_CREATION["Event Creation"]
    EVENT_CREATION --> IMAGE_MAPPING["Image Mapping"]
    IMAGE_MAPPING --> THIRD_PARTY_CAM["Third Party Camera"]
    IMAGE_MAPPING --> DEPTH_IMAGE["Depth Image Processing"]
    
    RC --> INTERACT_CTRL["InteractiveControllerPrompt"]
    INTERACT_CTRL --> DEFAULT_ACTIONS["DefaultActions Enum"]
```

**Sources:** [ai2thor/robot_controller.py:15-62](), [ai2thor/robot_controller.py:85-181](), [ai2thor/robot_controller.py:183-198]()

## Testing and Validation Systems

### Determinism Testing Framework

Specialized agents require extensive determinism testing to ensure reproducible behavior across different machines and configurations.

```mermaid
graph TD
    TEST_SETUP["Test Setup"] --> CONTROLLER_INIT["Controller Initialization"]
    CONTROLLER_INIT --> SCENE_LOAD["Scene Loading"]
    SCENE_LOAD --> ACTION_SEQ["Action Sequence Execution"]
    
    ACTION_SEQ --> ARM_ACTIONS["Arm Movement Commands"]
    ACTION_SEQ --> AGENT_ACTIONS["Agent Movement Commands"]
    ACTION_SEQ --> PICKUP_ACTIONS["Object Pickup Commands"]
    
    ARM_ACTIONS --> MOVE_ARM["w,z,s,a,3,4 commands"]
    ARM_ACTIONS --> ARM_BASE["u,j commands"]
    AGENT_ACTIONS --> CONTINUOUS["mm,rr,ll commands"]
    PICKUP_ACTIONS --> PICKUP["p command"]
    
    ACTION_SEQ --> EVENT_CAPTURE["Event Metadata Capture"]
    EVENT_CAPTURE --> COLLISION_CHECK["Event Collision Validation"]
    EVENT_CAPTURE --> STATE_COMPARISON["State Comparison"]
    
    STATE_COMPARISON --> DETERMINISM_RESULT["Determinism Validation"]
```

**Sources:** [arm_test/check_determinism_different_machines.py:95-142](), [arm_test/check_determinism_event_collision_different_machines.py:50-142]()

### Arm Manipulation Testing

The testing framework validates complex arm manipulation scenarios including object pickup, collision detection, and state consistency.

| Test Category | Test Functions | Validation Points |
|---------------|----------------|-------------------|
| Object Pickup | `test_arm_pickup_object()` | `heldObjects` metadata |
| Collision Detection | `test_arm_object_intersect()` | Action failure on collision |
| Body Intersection | `test_arm_body_object_intersect()` | State rollback validation |
| Metadata Consistency | `TestStretchArmMeta` | Gripper state tracking |

**Sources:** [ai2thor/tests/test_arm.py:61-82](), [ai2thor/tests/test_arm.py:125-162](), [unity/Assets/UnitTests/TestStretchArmMeta.cs:14-20]()

---

