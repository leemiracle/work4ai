<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/aloha_sim · page 3 Robot System · fetched 2026-10-26 -->

# Robot System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [aloha_sim/assets/aloha/README.md](aloha_sim/assets/aloha/README.md)
- [aloha_sim/assets/aloha/aloha_pbr.xml](aloha_sim/assets/aloha/aloha_pbr.xml)

</details>



This document provides comprehensive documentation of the ALOHA bimanual robot model used in aloha_sim. It covers the robot's physical structure, kinematic chains, control interfaces, and visual representation as defined in the MuJoCo XML model files.

For information about the 3D meshes and textures used by the robot system, see [Assets](#4). For details on how the robot integrates with simulation tasks, see [Available Tasks](#2.4).

## Overview

The ALOHA robot system is a bimanual (dual-arm) robotic platform based on the [ALOHA 2](https://aloha-2.github.io/) design. The simulation model is implemented as a MuJoCo XML description that defines the robot's physical properties, kinematics, sensors, and visual appearance.

The robot model is frozen at a specific version to maintain compatibility with existing teleoperation data and ensure reproducible simulation results. This approach prevents breaking changes from upstream model improvements that could invalidate collected datasets.

**Robot Model Architecture**

```mermaid
graph TB
    subgraph "Robot Definition"
        XML["aloha_pbr.xml<br/>Main Robot Model"]
        ACTUATORS["joint_position_actuators.xml<br/>Control Interface"]
        
        XML --> ACTUATORS
    end
    
    subgraph "Left Arm Chain"
        L_BASE["left/base_link"]
        L_SHOULDER["left/shoulder_link"]
        L_UPPER["left/upper_arm_link"]
        L_FOREARM_U["left/upper_forearm_link"]
        L_FOREARM_L["left/lower_forearm_link"]
        L_WRIST["left/wrist_link"]
        L_GRIPPER["left/gripper_link"]
        L_FINGERS["left finger joints"]
        
        L_BASE --> L_SHOULDER
        L_SHOULDER --> L_UPPER
        L_UPPER --> L_FOREARM_U
        L_FOREARM_U --> L_FOREARM_L
        L_FOREARM_L --> L_WRIST
        L_WRIST --> L_GRIPPER
        L_GRIPPER --> L_FINGERS
    end
    
    subgraph "Right Arm Chain"
        R_BASE["right/base_link"]
        R_SHOULDER["right/shoulder_link"]
        R_UPPER["right/upper_arm_link"]
        R_FOREARM_U["right/upper_forearm_link"]
        R_FOREARM_L["right/lower_forearm_link"]
        R_WRIST["right/wrist_link"]
        R_GRIPPER["right/gripper_link"]
        R_FINGERS["right finger joints"]
        
        R_BASE --> R_SHOULDER
        R_SHOULDER --> R_UPPER
        R_UPPER --> R_FOREARM_U
        R_FOREARM_U --> R_FOREARM_L
        R_FOREARM_L --> R_WRIST
        R_WRIST --> R_GRIPPER
        R_GRIPPER --> R_FINGERS
    end
    
    subgraph "Sensors"
        CAM_L["wrist_cam_left"]
        CAM_R["wrist_cam_right"]
        SITES["Reference Sites<br/>gripper sites"]
    end
    
    subgraph "Visual Assets"
        MESHES["3D Meshes<br/>vx300s_*.obj"]
        TEXTURES["PBR Materials<br/>BaseColor/Normal/ORM"]
        
        MESHES --> TEXTURES
    end
    
    XML --> L_BASE
    XML --> R_BASE
    L_GRIPPER --> CAM_L
    R_GRIPPER --> CAM_R
    L_GRIPPER --> SITES
    R_GRIPPER --> SITES
    
    MESHES --> L_BASE
    MESHES --> R_BASE
```

Sources: [aloha_sim/assets/aloha/aloha_pbr.xml:1-305](), [aloha_sim/assets/aloha/README.md:1-32]()

## Dual-Arm Configuration

The robot consists of two identical 7-degree-of-freedom manipulator arms positioned symmetrically on either side of the robot's workspace. Each arm is based on the VX300S design and includes a parallel gripper with coupled finger joints.

**Arm Positioning and Orientation**

| Arm | Position | Orientation | Base Frame |
|-----|----------|-------------|------------|
| Left | `(-0.469, -0.019, 0.02)` | Standard | `left/base_link` |
| Right | `(0.469, -0.019, 0.02)` | Standard | `right/base_link` |

The arms are positioned 0.938 meters apart (center-to-center distance) and slightly offset backward from the robot's coordinate origin.

Sources: [aloha_sim/assets/aloha/aloha_pbr.xml:125-126](), [aloha_sim/assets/aloha/aloha_pbr.xml:209-210]()

## Joint Structure and Degrees of Freedom

Each arm provides 7 degrees of freedom plus gripper control, for a total of 16 controllable joints across both arms.

**Joint Hierarchy per Arm**

```mermaid
graph TD
    subgraph "Joint Classes and Parameters"
        WAIST_CLASS["waist class<br/>Range: ±180°<br/>Axis: Z (0,0,1)<br/>Damping: 5.76<br/>Kp: 43"]
        SHOULDER_CLASS["shoulder class<br/>Range: -106° to 72°<br/>Axis: Y (0,1,0)<br/>Armature: 0.395<br/>Kp: 265"]
        ELBOW_CLASS["elbow class<br/>Range: -101° to 92°<br/>Axis: Y (0,1,0)<br/>Armature: 0.383<br/>Kp: 227"]
        FOREARM_CLASS["forearm_roll class<br/>Range: ±180°<br/>Axis: X (1,0,0)<br/>Armature: 0.14<br/>Kp: 78"]
        WRIST_ANGLE_CLASS["wrist_angle class<br/>Range: -107° to 128°<br/>Axis: Y (0,1,0)<br/>Armature: 0.008<br/>Kp: 37"]
        WRIST_ROTATE_CLASS["wrist_rotate class<br/>Range: ±180°<br/>Axis: X (1,0,0)<br/>Kp: 10.4"]
        FINGER_CLASS["finger class<br/>Type: slide<br/>Range: 0-4.1cm<br/>Control: 0.2-3.7cm<br/>Kp: 2000"]
    end
    
    subgraph "Left Arm Joints"
        L_WAIST["left/waist"]
        L_SHOULDER["left/shoulder"]
        L_ELBOW["left/elbow"]
        L_FOREARM["left/forearm_roll"]
        L_WRIST_A["left/wrist_angle"]
        L_WRIST_R["left/wrist_rotate"]
        L_FINGER_L["left/left_finger"]
        L_FINGER_R["left/right_finger"]
        
        L_WAIST --> L_SHOULDER
        L_SHOULDER --> L_ELBOW
        L_ELBOW --> L_FOREARM
        L_FOREARM --> L_WRIST_A
        L_WRIST_A --> L_WRIST_R
        L_WRIST_R --> L_FINGER_L
        L_WRIST_R --> L_FINGER_R
    end
    
    subgraph "Right Arm Joints"
        R_WAIST["right/waist"]
        R_SHOULDER["right/shoulder"]
        R_ELBOW["right/elbow"]
        R_FOREARM["right/forearm_roll"]
        R_WRIST_A["right/wrist_angle"]
        R_WRIST_R["right/wrist_rotate"]
        R_FINGER_L["right/left_finger"]
        R_FINGER_R["right/right_finger"]
        
        R_WAIST --> R_SHOULDER
        R_SHOULDER --> R_ELBOW
        R_ELBOW --> R_FOREARM
        R_FOREARM --> R_WRIST_A
        R_WRIST_A --> R_WRIST_R
        R_WRIST_R --> R_FINGER_L
        R_WRIST_R --> R_FINGER_R
    end
    
    WAIST_CLASS -.-> L_WAIST
    WAIST_CLASS -.-> R_WAIST
    SHOULDER_CLASS -.-> L_SHOULDER
    SHOULDER_CLASS -.-> R_SHOULDER
    ELBOW_CLASS -.-> L_ELBOW
    ELBOW_CLASS -.-> R_ELBOW
    FOREARM_CLASS -.-> L_FOREARM
    FOREARM_CLASS -.-> R_FOREARM
    WRIST_ANGLE_CLASS -.-> L_WRIST_A
    WRIST_ANGLE_CLASS -.-> R_WRIST_A
    WRIST_ROTATE_CLASS -.-> L_WRIST_R
    WRIST_ROTATE_CLASS -.-> R_WRIST_R
    FINGER_CLASS -.-> L_FINGER_L
    FINGER_CLASS -.-> L_FINGER_R
    FINGER_CLASS -.-> R_FINGER_L
    FINGER_CLASS -.-> R_FINGER_R
```

**Joint Control Parameters**

| Joint Type | Control Range | Physical Range | Axis | Proportional Gain (Kp) |
|------------|---------------|----------------|------|-------------------------|
| `waist` | ±180° | ±180° | Z (0,0,1) | 43 |
| `shoulder` | -106° to 72° | -106° to 72° | Y (0,1,0) | 265 |
| `elbow` | -101° to 92° | -101° to 92° | Y (0,1,0) | 227 |
| `forearm_roll` | ±180° | ±180° | X (1,0,0) | 78 |
| `wrist_angle` | -107° to 128° | -107° to 128° | Y (0,1,0) | 37 |
| `wrist_rotate` | ±180° | ±180° | X (1,0,0) | 10.4 |
| `finger` (slide) | 0.2-3.7cm | 0-4.1cm | Z (0,0,-1) | 2000 |

Sources: [aloha_sim/assets/aloha/aloha_pbr.xml:48-103](), [aloha_sim/assets/aloha/aloha_pbr.xml:133-302]()

## Gripper System

The parallel gripper system uses linear slide joints rather than rotational joints to model finger movement along rails. This design choice provides more intuitive control and measurement of gripper aperture.

**Gripper Mechanics**

The gripper fingers move along a 12cm rail system with the following constraints:
- **Physical Range**: 0 to 4.1cm (representing distance from rail center to finger inner edge)
- **Control Range**: 0.2 to 3.7cm (software-enforced limits from real robot measurements)
- **Finger Coupling**: Left and right fingers are constrained to move symmetrically via equality constraints

**Finger Coupling Constraints**

```mermaid
graph LR
    subgraph "Left Gripper"
        L_LEFT["left/left_finger"]
        L_RIGHT["left/right_finger"]
        L_CONSTRAINT["Equality Constraint<br/>polycoef: 0 1 0 0 0"]
        
        L_LEFT --> L_CONSTRAINT
        L_RIGHT --> L_CONSTRAINT
    end
    
    subgraph "Right Gripper"
        R_LEFT["right/left_finger"]
        R_RIGHT["right/right_finger"]
        R_CONSTRAINT["Equality Constraint<br/>polycoef: 0 1 0 0 0"]
        
        R_LEFT --> R_CONSTRAINT
        R_RIGHT --> R_CONSTRAINT
    end
```

The equality constraints ensure that `left_finger` and `right_finger` joints move with identical displacement, maintaining symmetric gripper operation.

Sources: [aloha_sim/assets/aloha/aloha_pbr.xml:72-103](), [aloha_sim/assets/aloha/aloha_pbr.xml:299-302]()

## Sensor Systems

The robot includes multiple sensor systems for perception and state monitoring.

**Wrist-Mounted Cameras**

Each gripper includes a RealSense D405 camera mounted on the gripper base:

| Camera | Name | Position | Orientation | Resolution | Focal Length |
|--------|------|----------|-------------|------------|--------------|
| Left | `wrist_cam_left` | `(-0.011, -0.0814748, -0.0095955)` | `euler="2.70525955359 0 0"` | 1280×720 | 1.93mm |
| Right | `wrist_cam_right` | `(-0.011, -0.0814748, -0.0095955)` | `euler="2.70525955359 0 0"` | 1280×720 | 1.93mm |

**Reference Sites**

The robot defines several reference sites for control and monitoring:
- `left/gripper` and `right/gripper`: End-effector reference points at gripper tips
- `left/left_finger`, `left/right_finger`: Finger contact reference points  
- `right/left_finger`, `right/right_finger`: Finger contact reference points

**External Cameras**

The robot model also defines two external viewpoint cameras:
- `teleoperator_pov`: Positioned for operator perspective at `(0, -1.354, 0.685)`
- `collaborator_pov`: Positioned for external observation at `(0, 1.5, 0.8)`

Sources: [aloha_sim/assets/aloha/aloha_pbr.xml:122-124](), [aloha_sim/assets/aloha/aloha_pbr.xml:172-173](), [aloha_sim/assets/aloha/aloha_pbr.xml:256-257](), [aloha_sim/assets/aloha/aloha_pbr.xml:164-198](), [aloha_sim/assets/aloha/aloha_pbr.xml:248-282]()

## Visual Representation

The robot uses a Physically Based Rendering (PBR) material system with high-quality 3D meshes and texture maps.

**Material System**

```mermaid
graph TB
    subgraph "PBR Material Pipeline"
        TEXTURES["Texture Assets"]
        ARM_RGB["arm_rgb<br/>Arm_material_BaseColor.png"]
        ARM_ORM["arm_orm<br/>Arm_material_ORM.png"]
        ARM_NORMAL["arm_normal<br/>Arm_material_Normal.png"]
        
        TEXTURES --> ARM_RGB
        TEXTURES --> ARM_ORM
        TEXTURES --> ARM_NORMAL
    end
    
    subgraph "Material Definition"
        ARM_MATERIAL["arm_material"]
        RGB_LAYER["RGB Layer"]
        ORM_LAYER["ORM Layer<br/>(Occlusion/Roughness/Metallic)"]
        NORMAL_LAYER["Normal Layer"]
        
        ARM_MATERIAL --> RGB_LAYER
        ARM_MATERIAL --> ORM_LAYER
        ARM_MATERIAL --> NORMAL_LAYER
    end
    
    subgraph "Geometry Classes"
        VISUAL_CLASS["visual class<br/>Group: 2<br/>No collision"]
        COLLISION_CLASS["collision class<br/>Group: 3<br/>Physics enabled"]
        
        VISUAL_CLASS --> ARM_MATERIAL
    end
    
    ARM_RGB --> RGB_LAYER
    ARM_ORM --> ORM_LAYER
    ARM_NORMAL --> NORMAL_LAYER
```

**3D Mesh Components**

The robot uses separate mesh files for each component:
- `vx300s_1_base.obj` - Base link geometry
- `vx300s_2_shoulder.obj` - Shoulder link geometry  
- `vx300s_3_upper_arm.obj` - Upper arm geometry
- `vx300s_4_upper_forearm.obj` - Upper forearm geometry
- `vx300s_5_lower_forearm.obj` - Lower forearm geometry
- `vx300s_6_wrist.obj` - Wrist link geometry
- `vx300s_7_gripper_prop_bar.obj` - Gripper base geometry
- `vx300s_8_custom_finger_left.obj` - Left finger geometry
- `vx300s_8_custom_finger_right.obj` - Right finger geometry
- `d405_solid.obj` - Camera housing geometry

Each body in the kinematic chain uses both visual and collision geometry instances of the same mesh, with different material properties and collision settings.

Sources: [aloha_sim/assets/aloha/aloha_pbr.xml:22-42](), [aloha_sim/assets/aloha/aloha_pbr.xml:104-116]()

## Physics and Constraints

The robot model includes several physics configurations and constraints to ensure realistic simulation behavior.

**Contact Exclusions**

Certain body pairs are excluded from collision detection to prevent self-collision issues:
```xml
<exclude body1="left/base_link" body2="left/shoulder_link"/>
<exclude body1="right/base_link" body2="right/shoulder_link"/>
```

**Collision Properties**

Different collision classes provide specialized contact behavior:
- `finger_collision`: Enhanced friction properties (`friction="1 0.005 0.0001"`) for grasping
- `sphere_collision`: Small sphere contacts at finger tips for precision manipulation
- Standard collision geometry for all other components

**Actuator Integration**

The robot model includes joint position actuators defined in a separate file (`joint_position_actuators.xml`) that provide the control interface between the simulation and external policies or control systems.

Sources: [aloha_sim/assets/aloha/aloha_pbr.xml:294-297](), [aloha_sim/assets/aloha/aloha_pbr.xml:109-114](), [aloha_sim/assets/aloha/aloha_pbr.xml:304]()

---

