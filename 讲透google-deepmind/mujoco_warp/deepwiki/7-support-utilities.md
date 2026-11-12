<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mujoco_warp · page 7 Support Utilities · fetched 2026-10-26 -->

# Support Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mujoco_warp/_src/block_cholesky.py](mujoco_warp/_src/block_cholesky.py)
- [mujoco_warp/_src/math.py](mujoco_warp/_src/math.py)
- [mujoco_warp/_src/math_test.py](mujoco_warp/_src/math_test.py)
- [mujoco_warp/_src/support.py](mujoco_warp/_src/support.py)
- [mujoco_warp/_src/support_test.py](mujoco_warp/_src/support_test.py)

</details>



This page provides an overview of the helper functions and mathematical utilities that support the main physics pipeline in MuJoCo Warp. These utilities provide the computational foundation for matrix operations, spatial mathematics, state management, and derivative computations.

For details on the core simulation steps that use these utilities, see [Forward Dynamics and Integration](#3.1).

## System Overview

The utility systems are organized into categories that provide specialized logic for the GPU-accelerated pipeline:

```mermaid
graph TB
    subgraph "Main Pipeline"
        [step] --> [forward]
        [forward] --> [fwd_velocity]
        [fwd_velocity] --> [smooth_dynamics]
    end
    
    subgraph "Support Utilities [support.py]"
        [mul_m] --> [Matrix_Multiplication]
        [apply_ft] --> [Force_Transformations]
        [xfrc_accumulate] --> [Generalized_Forces]
    end
    
    subgraph "Derivative System [derivative.py]"
        [deriv_smooth_vel] --> [Implicit_Integration]
        [_qderiv_actuator_passive_vel] --> [Actuator_Derivatives]
    end
    
    subgraph "Math Foundations [math.py]"
        [motion_cross] --> [Spatial_Algebra]
        [mul_quat] --> [Rotations]
        [inert_vec] --> [Inertia_Ops]
    end

    [smooth_dynamics] -.-> [mul_m]
    [smooth_dynamics] -.-> [motion_cross]
    [Implicit_Integration] -.-> [deriv_smooth_vel]
```

Sources: [mujoco_warp/_src/support.py:1-35](), [mujoco_warp/_src/math.py:1-30]()

## Mathematical Utilities

The mathematical utilities provide fundamental operations for 3D geometry, quaternion algebra, and spatial vector arithmetic. These are implemented as `wp.func` routines to be called directly from Warp kernels.

### Spatial and Rigid Body Math
MuJoCo Warp utilizes spatial algebra (6D vectors) to represent velocities and forces.
*   **Spatial Algebra**: Functions like `motion_cross` [mujoco_warp/_src/math.py:134-145]() and `motion_cross_force` [mujoco_warp/_src/math.py:148-159]() handle the non-intuitive cross products required for spatial dynamics.
*   **Inertia Operations**: `inert_vec` [mujoco_warp/_src/math.py:121-132]() multiplies a 6D motion vector by a 6D inertia matrix.
*   **Quaternions**: Comprehensive support for quaternion multiplication (`mul_quat`), integration (`quat_integrate`), and conversion to matrices (`quat_to_mat`) [mujoco_warp/_src/math.py:24-84]().

For a full catalog of mathematical routines, see **[Mathematical Utilities](#7.1)**.

## Support Operations

The `support.py` module contains high-level orchestration for matrix and force operations that bridge the gap between low-level math and the physics pipeline.

### Matrix Multiplication (`mul_m`)
The `mul_m` function [mujoco_warp/_src/support.py:218-226]() is the primary interface for multiplying vectors by the joint-space inertia matrix $M$. It automatically handles the selection between sparse and dense implementations based on the system layout [mujoco_warp/_src/support.py:155-215]().

| Implementation | Function | Logic |
| :--- | :--- | :--- |
| **Sparse** | `_mul_m` | Gather-based multiplication using `M_mulm_rowadr` and `M_mulm_col` [mujoco_warp/_src/support.py:155-188](). |
| **Dense** | `_mul_m_dense` | Standard SIMT dense matmul for compact active-DOF inertia blocks [mujoco_warp/_src/support.py:191-215](). |

### Force and State Management
*   **`xfrc_accumulate`**: Maps applied body forces to joint-space generalized forces using system Jacobians.
*   **`apply_ft`**: A general-purpose kernel that applies spatial forces/torques across kinematic branches.
*   **`next_act`**: Predicts the next activation state based on the actuator's `dyntype` (e.g., `FILTEREXACT`) and `dynprm` [mujoco_warp/_src/support.py:38-65]().

Sources: [mujoco_warp/_src/support.py:38-226]()

## Derivative Computations

For implicit integration schemes, the system must compute the derivatives of smooth forces with respect to velocities.

```mermaid
graph LR
    subgraph "Derivative Workflow"
        [deriv_smooth_vel] --> [Actuator_Passive_Vel]
        [deriv_smooth_vel] --> [Actuator_Passive_Actuation]
        [Actuator_Passive_Actuation] --> [Sparse_or_Dense_Output]
    end

    [Implicit_Integrator] -- calls --> [deriv_smooth_vel]
    [deriv_smooth_vel] -- populates --> [qDeriv]
```

The derivative pipeline calculates smooth force gradients and effective metrics (such as through block Cholesky factorizations in `block_cholesky.py`) to support stable implicit and discrete integration.

For details on the analytical derivation and implementation, see **[Derivative Computations](#7.2)**.

## Sleeping and Sensor History

To optimize performance on GPU, inactive kinematic trees can utilize sleep policies (`sleep.py`) that bypass unnecessary updates during idle periods. Additionally, sensor delay and history buffers (`history.py`) manage temporal sensor data streams and integrate cleanly with collision and solver fast paths.

For details on sleep states and sensor buffers, see **[Sleeping and Sensor History](#7.3)**.

Sources: [mujoco_warp/_src/block_cholesky.py:21-41]()

---

