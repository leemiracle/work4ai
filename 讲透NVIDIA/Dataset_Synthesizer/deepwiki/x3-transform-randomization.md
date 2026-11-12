<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Dataset_Synthesizer · extra page Transform Randomization · fetched 2026-10-26 -->

# Transform Randomization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Documentation/ClassDetails/_d_r_utils_8h_source.html](Documentation/ClassDetails/_d_r_utils_8h_source.html)

</details>



This page documents the transform randomization data structures used in the domain randomization system to randomize object positions, rotations, and scales in synthetic scenes. Transform randomization is a critical component of dataset generation, enabling the creation of diverse training data by varying object poses and sizes.

For information about appearance randomization (colors and materials), see [Appearance Randomization](#4.3.2). For managing large asset libraries, see [Asset Streaming](#4.3.3).

## Overview

The transform randomization system consists of three primary data structures defined in [DRUtils.h:19-167]():

- `FRandomRotationData` - Controls rotation randomization (cone-based or per-axis)
- `FRandomLocationData` - Controls position randomization (per-axis ranges)
- `FRandomScale3DData` - Controls scale randomization (uniform or per-axis)

These structs are used by `AGroupActorManager` (see [Actor Spawning](#4.2)) to randomize spawned actors' transforms, creating variation in object placement, orientation, and size across synthetic scenes.

**Sources:** [Documentation/ClassDetails/_d_r_utils_8h_source.html:19-167]()

## Transform Randomization Components

The following diagram shows the three transform randomization data structures and their key methods:

```mermaid
classDiagram
    class FRandomRotationData {
        +bool bRandomizeRotationInACone
        +float RandomConeHalfAngle
        +bool bRandomizePitch
        +FFloatInterval PitchRange
        +bool bRandomizeRoll
        +FFloatInterval RollRange
        +bool bRandomizeYaw
        +FFloatInterval YawRange
        +GetRandomRotation() FRotator
        +GetRandomRotationRelative(BaseRotation) FRotator
        +ShouldRandomized() bool
    }
    
    class FRandomLocationData {
        +bool bRandomizeXAxis
        +FFloatInterval XAxisRange
        +bool bRandomizeYAxis
        +FFloatInterval YAxisRange
        +bool bRandomizeZAxis
        +FFloatInterval ZAxisRange
        +GetRandomLocation() FVector
        +GetRandomLocationRelative(BaseLocation) FVector
        +GetRandomLocationInLocalSpace(ObjectTransform) FVector
        +ShouldRandomized() bool
    }
    
    class FRandomScale3DData {
        +bool bUniformScale
        +FFloatInterval UniformScaleRange
        +bool bRandomizeXAxis
        +FFloatInterval XAxisRange
        +bool bRandomizeYAxis
        +FFloatInterval YAxisRange
        +bool bRandomizeZAxis
        +FFloatInterval ZAxisRange
        +GetRandomScale3D() FVector
        +ShouldRandomized() bool
    }
    
    class AGroupActorManager {
        Uses for spawned actors
    }
    
    FRandomRotationData --> AGroupActorManager
    FRandomLocationData --> AGroupActorManager
    FRandomScale3DData --> AGroupActorManager
```

**Sources:** [Documentation/ClassDetails/_d_r_utils_8h_source.html:19-167]()

## Rotation Randomization

`FRandomRotationData` provides two distinct randomization strategies defined in [DRUtils.h:19-66]():

### Cone-Based Rotation

When `bRandomizeRotationInACone` is true, rotations are generated inside a cone with half-angle specified by `RandomConeHalfAngle`. This is useful for objects that should maintain approximate upright orientation while allowing some variation.

| Property | Type | Description |
|----------|------|-------------|
| `bRandomizeRotationInACone` | `bool` | Enables cone-based randomization |
| `RandomConeHalfAngle` | `float` | Half-angle of the cone in degrees |

### Per-Axis Rotation

Alternatively, each Euler angle (pitch, roll, yaw) can be independently randomized within specified ranges:

| Axis | Enable Flag | Range Property | Description |
|------|-------------|----------------|-------------|
| Pitch | `bRandomizePitch` | `PitchRange` | Rotation around Y-axis |
| Roll | `bRandomizeRoll` | `RollRange` | Rotation around X-axis |
| Yaw | `bRandomizeYaw` | `YawRange` | Rotation around Z-axis |

### Methods

```mermaid
flowchart LR
    Start["FRandomRotationData"] --> Check{"ShouldRandomized()"}
    Check -->|"Any flag enabled"| GetRand["GetRandomRotation()"]
    Check -->|"No flags enabled"| NoOp["No randomization"]
    
    GetRand --> Cone{"bRandomizeRotationInACone?"}
    Cone -->|"Yes"| ConeGen["Generate rotation<br/>in cone"]
    Cone -->|"No"| PerAxis["Generate per-axis<br/>rotation"]
    
    Relative["GetRandomRotationRelative()"] --> ApplyBase["Apply around<br/>base rotation"]
    
    ConeGen --> Result["FRotator"]
    PerAxis --> Result
    ApplyBase --> Result
```

**Key Methods:**

- `GetRandomRotation()` - Returns a random rotation based on configured constraints (line 27)
- `GetRandomRotationRelative(BaseRotation)` - Returns a random rotation applied around a base rotation (line 30)
- `ShouldRandomized()` - Returns true if any randomization flag is enabled (line 32-35)

**Sources:** [Documentation/ClassDetails/_d_r_utils_8h_source.html:19-66]()

## Location Randomization

`FRandomLocationData` provides per-axis position randomization in world space, defined in [DRUtils.h:69-113]().

### Configuration

Each axis can be independently enabled and configured with a range:

| Axis | Enable Flag | Range Property | Description |
|------|-------------|----------------|-------------|
| X | `bRandomizeXAxis` | `XAxisRange` | Position along world X-axis |
| Y | `bRandomizeYAxis` | `YAxisRange` | Position along world Y-axis |
| Z | `bRandomizeZAxis` | `ZAxisRange` | Position along world Z-axis |

### Methods

The struct provides three location generation methods:

```mermaid
flowchart TB
    FRandomLocationData["FRandomLocationData"]
    
    FRandomLocationData --> Method1["GetRandomLocation()"]
    FRandomLocationData --> Method2["GetRandomLocationRelative(BaseLocation)"]
    FRandomLocationData --> Method3["GetRandomLocationInLocalSpace(ObjectTransform)"]
    
    Method1 --> Desc1["Returns random position<br/>in world space"]
    Method2 --> Desc2["Returns random position<br/>offset from base location"]
    Method3 --> Desc3["Returns random position<br/>in object's local space"]
    
    Desc1 --> Check["Check enabled axes"]
    Desc2 --> Check
    Desc3 --> Check
    
    Check --> X{"bRandomizeXAxis?"}
    Check --> Y{"bRandomizeYAxis?"}
    Check --> Z{"bRandomizeZAxis?"}
    
    X -->|Yes| RandX["Random value<br/>in XAxisRange"]
    Y -->|Yes| RandY["Random value<br/>in YAxisRange"]
    Z -->|Yes| RandZ["Random value<br/>in ZAxisRange"]
    
    X -->|No| DefaultX["Use 0 or<br/>base value"]
    Y -->|No| DefaultY["Use 0 or<br/>base value"]
    Z -->|No| DefaultZ["Use 0 or<br/>base value"]
    
    RandX --> Result["FVector"]
    RandY --> Result
    RandZ --> Result
    DefaultX --> Result
    DefaultY --> Result
    DefaultZ --> Result
```

**Key Methods:**

- `GetRandomLocation()` - Returns a random location in world space (line 76)
- `GetRandomLocationRelative(BaseLocation)` - Returns a random location offset from a base position (line 79)
- `GetRandomLocationInLocalSpace(ObjectTransform)` - Returns a random location in an object's local coordinate system (line 82)
- `ShouldRandomized()` - Returns true if any axis randomization is enabled (line 84-87)

**Sources:** [Documentation/ClassDetails/_d_r_utils_8h_source.html:69-113]()

## Scale Randomization

`FRandomScale3DData` provides both uniform and per-axis scale randomization, defined in [DRUtils.h:116-167]().

### Uniform vs. Per-Axis Scaling

The struct supports two mutually exclusive modes:

```mermaid
flowchart LR
    FRandomScale3DData["FRandomScale3DData"]
    
    FRandomScale3DData --> Decision{"bUniformScale?"}
    
    Decision -->|"true"| Uniform["Uniform Scaling"]
    Decision -->|"false"| PerAxis["Per-Axis Scaling"]
    
    Uniform --> UniformRange["UniformScaleRange<br/>Same value for X, Y, Z"]
    
    PerAxis --> XScale["bRandomizeXAxis<br/>XAxisRange"]
    PerAxis --> YScale["bRandomizeYAxis<br/>YAxisRange"]
    PerAxis --> ZScale["bRandomizeZAxis<br/>ZAxisRange"]
    
    UniformRange --> Result["FVector with<br/>scale values"]
    XScale --> Result
    YScale --> Result
    ZScale --> Result
```

### Configuration

**Uniform Scaling:**

| Property | Type | Description |
|----------|------|-------------|
| `bUniformScale` | `bool` | When true, all axes use the same scale value |
| `UniformScaleRange` | `FFloatInterval` | Range for uniform scale value |

**Per-Axis Scaling:**

| Axis | Enable Flag | Range Property | Minimum Value |
|------|-------------|----------------|---------------|
| X | `bRandomizeXAxis` | `XAxisRange` | 0.001 (line 146-148) |
| Y | `bRandomizeYAxis` | `YAxisRange` | 0.001 (line 154-157) |
| Z | `bRandomizeZAxis` | `ZAxisRange` | 0.001 (line 163-166) |

**Note:** Minimum scale values are clamped at 0.001 to prevent degenerate geometry.

### Methods

**Key Methods:**

- `GetRandomScale3D()` - Returns a random 3D scale vector based on configuration (line 124)
- `ShouldRandomized()` - Returns true if uniform scale or any axis randomization is enabled (line 126-129)

**Sources:** [Documentation/ClassDetails/_d_r_utils_8h_source.html:116-167]()

## Integration with Domain Randomization Workflow

The following diagram shows how transform randomization structures are used within the broader domain randomization workflow:

```mermaid
flowchart TB
    ADRSceneManager["ADRSceneManager<br/>(Scene Orchestrator)"]
    
    ADRSceneManager --> AGroupActorManager["AGroupActorManager<br/>(Actor Spawning)"]
    
    AGroupActorManager --> SpawnActors["SpawnActors()"]
    
    SpawnActors --> Actor1["Spawn Actor Instance"]
    
    Actor1 --> ApplyTransform["Apply Randomized Transform"]
    
    ApplyTransform --> UseRotation["Use FRandomRotationData"]
    ApplyTransform --> UseLocation["Use FRandomLocationData"]
    ApplyTransform --> UseScale["Use FRandomScale3DData"]
    
    UseRotation --> CallMethod1["GetRandomRotation()<br/>or GetRandomRotationRelative()"]
    UseLocation --> CallMethod2["GetRandomLocation()<br/>or GetRandomLocationRelative()<br/>or GetRandomLocationInLocalSpace()"]
    UseScale --> CallMethod3["GetRandomScale3D()"]
    
    CallMethod1 --> SetActorTransform["SetActorTransform()<br/>or similar UE method"]
    CallMethod2 --> SetActorTransform
    CallMethod3 --> SetActorTransform
    
    SetActorTransform --> FinalActor["Actor with<br/>Randomized Transform"]
    
    FinalActor --> NextIteration{"More Actors<br/>to Spawn?"}
    NextIteration -->|Yes| Actor1
    NextIteration -->|No| Complete["Scene Ready for Capture"]
```

The transform randomization structs are typically configured in `AGroupActorManager` (see [Actor Spawning](#4.2)) and applied to each spawned actor. The randomization can be:

- **Absolute:** Using `GetRandomRotation()`, `GetRandomLocation()`, and `GetRandomScale3D()` to generate completely random transforms
- **Relative:** Using `GetRandomRotationRelative()` and `GetRandomLocationRelative()` to apply variations around a base transform
- **Local Space:** Using `GetRandomLocationInLocalSpace()` to randomize position in an object's local coordinate system

**Sources:** [Documentation/ClassDetails/_d_r_utils_8h_source.html:19-167]()

## Usage Example Pattern

While no implementation code is shown here, the typical usage pattern in actor spawning code follows this structure:

1. **Check if randomization is needed** using `ShouldRandomized()` methods
2. **Generate random values** using the appropriate `Get*` methods
3. **Apply to spawned actors** using Unreal Engine's transform methods

Each struct is designed as a `USTRUCT(BlueprintType)` (lines 18, 68, 115), making them:
- Serializable for saving/loading configurations
- Exposable to Blueprint visual scripting
- Editable in the Unreal Editor UI via `UPROPERTY(EditAnywhere)` macros

The `FFloatInterval` type used throughout represents a min/max range for random value generation.

**Sources:** [Documentation/ClassDetails/_d_r_utils_8h_source.html:18-167]()

---

