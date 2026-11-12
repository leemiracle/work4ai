<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/aloha_sim · extra page Sensors and Hardware · fetched 2026-10-26 -->

# Sensors and Hardware

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [aloha_sim/assets/aloha/assets/aloha_mapped_mesh/d405_solid.obj](aloha_sim/assets/aloha/assets/aloha_mapped_mesh/d405_solid.obj)
- [aloha_sim/assets/aloha/assets/aloha_mapped_mesh/overhead_mount.obj](aloha_sim/assets/aloha/assets/aloha_mapped_mesh/overhead_mount.obj)
- [aloha_sim/assets/aloha/assets/aloha_mapped_mesh/wormseye_mount.obj](aloha_sim/assets/aloha/assets/aloha_mapped_mesh/wormseye_mount.obj)

</details>



This document covers the 3D mesh assets for sensors and mounting hardware used in the ALOHA robot simulation. These components provide the visual representation of cameras and mounting systems that enable perception and structural support in the simulated environment.

For information about robot arm components and gripper hardware, see [Robot Components](#4.1.1). For environment objects and scene elements, see [Environment Objects](#4.1.3).

## Camera Sensors

The simulation includes detailed 3D models of camera sensors that provide visual perception capabilities for the ALOHA robot system.

### Intel RealSense D405 Camera

The primary camera sensor model is the Intel RealSense D405, represented by the `d405_solid.obj` mesh file. This compact depth camera is designed for close-range applications and is commonly mounted on robot wrists for manipulation tasks.

```mermaid
graph TD
    subgraph "Camera Sensor Assets"
        D405["d405_solid.obj<br/>Intel RealSense D405"]
        MESH_DATA["3D Mesh Geometry<br/>1000+ vertices<br/>Complex surface topology"]
        
        D405 --> MESH_DATA
    end
    
    subgraph "Robot Integration"
        WRIST_CAM["wrist_cam_left<br/>wrist_cam_right"]
        GRIPPER_SITES["gripper sites"]
        
        MESH_DATA --> WRIST_CAM
        WRIST_CAM --> GRIPPER_SITES
    end
    
    subgraph "Simulation Framework"
        MUJOCO["MuJoCo Physics Engine"]
        VISUAL_GEOM["Visual Geometry"]
        
        GRIPPER_SITES --> MUJOCO
        MESH_DATA --> VISUAL_GEOM
        VISUAL_GEOM --> MUJOCO
    end
```

The D405 model contains detailed geometric data with precise vertex coordinates and face definitions that accurately represent the physical camera's form factor. The mesh includes mounting points and connector details that ensure proper visual integration with the robot arm assembly.

**Sources:** [aloha_sim/assets/aloha/assets/aloha_mapped_mesh/d405_solid.obj:1-4000]()

## Mounting Hardware

Mounting hardware provides the structural interface between sensors and the robot framework, ensuring stable positioning and optimal viewing angles.

### Overhead Mount System

The `overhead_mount.obj` represents mounting hardware designed for overhead camera positioning and structural support.

```mermaid
graph LR
    subgraph "Mount Components"
        OVERHEAD["overhead_mount.obj<br/>Structural Support"]
        MOUNT_GEOM["Complex Geometry<br/>1000+ vertices<br/>Mounting interfaces"]
        
        OVERHEAD --> MOUNT_GEOM
    end
    
    subgraph "Mounting Points"
        CAMERA_ATTACH["Camera Attachment Points"]
        FRAME_CONNECT["Frame Connection Points"]
        ADJUST_MECH["Adjustment Mechanisms"]
        
        MOUNT_GEOM --> CAMERA_ATTACH
        MOUNT_GEOM --> FRAME_CONNECT
        MOUNT_GEOM --> ADJUST_MECH
    end
    
    subgraph "System Integration"
        ROBOT_FRAME["Robot Base Frame"]
        WORKSPACE["Workspace Coverage"]
        
        FRAME_CONNECT --> ROBOT_FRAME
        CAMERA_ATTACH --> WORKSPACE
    end
```

The overhead mount geometry includes precision-machined surfaces and mounting holes that accommodate standard camera threading and electrical connections. The design provides multiple degrees of adjustment for optimal sensor positioning.

**Sources:** [aloha_sim/assets/aloha/assets/aloha_mapped_mesh/overhead_mount.obj:1-4000]()

## Asset Organization and Integration

The sensor and hardware meshes are organized within the broader asset management system and integrated with the robot model definition.

```mermaid
graph TB
    subgraph "Asset Directory Structure"
        ASSETS_ROOT["aloha_sim/assets/"]
        ALOHA_DIR["aloha/assets/"]
        MAPPED_MESH["aloha_mapped_mesh/"]
        
        ASSETS_ROOT --> ALOHA_DIR
        ALOHA_DIR --> MAPPED_MESH
    end
    
    subgraph "Sensor Assets"
        D405_FILE["d405_solid.obj"]
        OVERHEAD_FILE["overhead_mount.obj"]
        
        MAPPED_MESH --> D405_FILE
        MAPPED_MESH --> OVERHEAD_FILE
    end
    
    subgraph "Robot Model Integration"
        ROBOT_XML["aloha_pbr.xml"]
        VISUAL_ELEMENTS["Visual Elements"]
        GEOM_REFS["Geometry References"]
        
        D405_FILE --> GEOM_REFS
        OVERHEAD_FILE --> GEOM_REFS
        GEOM_REFS --> VISUAL_ELEMENTS
        VISUAL_ELEMENTS --> ROBOT_XML
    end
    
    subgraph "Simulation Runtime"
        MUJOCO_ENGINE["MuJoCo Physics Engine"]
        RENDERED_SCENE["Rendered Scene"]
        
        ROBOT_XML --> MUJOCO_ENGINE
        MUJOCO_ENGINE --> RENDERED_SCENE
    end
```

### File Format and Structure

Both sensor and hardware meshes use the Wavefront OBJ format, which provides:

| Element | Description | Usage |
|---------|-------------|--------|
| Vertices (`v`) | 3D coordinate points | Define mesh geometry |
| Faces (`f`) | Polygon definitions | Create surface topology |
| Normals (`vn`) | Surface orientations | Enable proper lighting |
| Texture coordinates (`vt`) | UV mapping data | Support material application |

The mesh files are optimized for real-time rendering while maintaining sufficient detail for accurate visual representation during simulation tasks.

**Sources:** [aloha_sim/assets/aloha/assets/aloha_mapped_mesh/d405_solid.obj:1-10](), [aloha_sim/assets/aloha/assets/aloha_mapped_mesh/overhead_mount.obj:1-10]()

## Sensor-Robot Integration

The integration between sensor assets and the robot system follows a hierarchical attachment model that ensures proper kinematic relationships.

```mermaid
graph TD
    subgraph "Robot Kinematic Chain"
        BASE["Robot Base"]
        ARM_LINKS["Arm Link Hierarchy"]
        WRIST["Wrist Joint"]
        GRIPPER["Gripper Assembly"]
        
        BASE --> ARM_LINKS
        ARM_LINKS --> WRIST
        WRIST --> GRIPPER
    end
    
    subgraph "Sensor Mounting"
        MOUNT_POINTS["Mounting Points"]
        D405_INSTANCE["D405 Camera Instance"]
        OVERHEAD_INSTANCE["Overhead Mount Instance"]
        
        GRIPPER --> MOUNT_POINTS
        MOUNT_POINTS --> D405_INSTANCE
        BASE --> OVERHEAD_INSTANCE
    end
    
    subgraph "Simulation Features"
        WRIST_CAM_LEFT["wrist_cam_left"]
        WRIST_CAM_RIGHT["wrist_cam_right"]
        VISUAL_FEEDBACK["Visual Feedback"]
        
        D405_INSTANCE --> WRIST_CAM_LEFT
        D405_INSTANCE --> WRIST_CAM_RIGHT
        WRIST_CAM_LEFT --> VISUAL_FEEDBACK
        WRIST_CAM_RIGHT --> VISUAL_FEEDBACK
    end
```

The sensor models are referenced in the robot XML definition through geometry elements that specify mesh file paths and transformation matrices. This enables the MuJoCo physics engine to properly render and position the sensors within the simulated environment.

**Sources:** [aloha_sim/assets/aloha/assets/aloha_mapped_mesh/d405_solid.obj:1-4000](), [aloha_sim/assets/aloha/assets/aloha_mapped_mesh/overhead_mount.obj:1-4000]()

---

