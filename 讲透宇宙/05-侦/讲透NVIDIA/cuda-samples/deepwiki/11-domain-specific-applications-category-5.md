<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuda-samples · page 11 Domain-Specific Applications (Category 5) · fetched 2026-10-26 -->

# Domain-Specific Applications (Category 5)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [Common/helper_math.h](Common/helper_math.h)

</details>



## Purpose and Scope

This page provides a high-level overview of specialized CUDA applications that demonstrate the technology in real-world scenarios. These samples, located in the `cpp/5_Domain_Specific` directory, showcase how GPU parallelism solves complex problems in financial modeling, physics simulation, fluid dynamics, and medical imaging.

For detailed technical deep-dives into specific domains, please refer to the following child pages:
*   [Physics Simulation and Particle Systems](#11.1) — Covers N-body simulations, particle dynamics, and smoke effects.
*   [Fluid Dynamics and Visualization](#11.2) — Covers Navier-Stokes solvers and FFT-based ocean simulation.
*   [Volume Rendering and Medical Imaging](#11.3) — Covers Isosurface extraction (Marching Cubes) and 3D ray casting.

## Overview of Domain-Specific Application Categories

The domain-specific samples bridge the gap between low-level CUDA primitives and complex, industry-specific algorithms. They often integrate multiple CUDA features, such as `cuFFT` for signal processing, `Thrust` for data management, and Graphics API interop for real-time visualization.

```mermaid
graph TD
    subgraph "Domain-Specific CUDA Applications (Category 5)"
        [Finance] --> [BlackScholes]
        [Finance] --> [MonteCarloMultiGPU]
        
        [Physics] --> [nbody]
        [Physics] --> [FDTD3d]
        
        [Fluids] --> [fluidsGL]
        [Fluids] --> [oceanFFT]
        
        [Imaging] --> [marchingCubes]
        [Imaging] --> [volumeRender]
        
        [Vision] --> [HSOpticalFlow]
        [Vision] --> [stereoDisparity]
    end

    subgraph "Code Entities"
        [BlackScholes] --- BlackScholes_kernel["BlackScholes_kernel.cu"]
        [nbody] --- BodySystem["BodySystemCUDA"]
        [fluidsGL] --- Advect["advectVelocity_k"]
        [marchingCubes] --- LaunchMC["launch_marchingCubes"]
    end
```

Sources: [CHANGELOG.md:47-49](), [Common/helper_math.h:28-37]()

## Financial Computing Applications

The financial computing samples demonstrate GPU acceleration for computationally intensive models used in quantitative finance. These applications typically involve high-dimensional integration or solving partial differential equations (PDEs).

### Options Pricing and Simulation
*   **Black-Scholes**: Implements the Black-Scholes PDE for European options. The sample includes both standard and NVRTC versions (e.g., `BlackScholes_nvrtc.cpp`).
*   **Monte Carlo Multi-GPU**: Demonstrates distributed simulation across multiple devices using quasi-random number generators (Sobol sequences) to price complex derivatives.
*   **Binomial Options**: Uses a tree-based approach for American options, showcasing dynamic programming patterns on the GPU.

Sources: [CHANGELOG.md:38-40](), [CHANGELOG.md:46]()

## Physics Simulation and Particle Systems

These samples focus on simulating physical phenomena where large numbers of independent entities interact, a workload perfectly suited for SIMT (Single Instruction, Multiple Threads) architectures.

*   **N-Body Simulation**: A classic gravitational simulation where every particle interacts with every other particle. It demonstrates O(N²) complexity optimized through shared memory tiles.
*   **FDTD3d**: Implements the Finite Difference Time Domain method for Maxwell's equations, showcasing 3D stencil operations.
*   **Smoke Particles**: Combines particle physics with volumetric rendering techniques.

For details, see [Physics Simulation and Particle Systems](#11.1).

## Fluid Dynamics and Visualization

Fluid dynamics samples solve the Navier-Stokes equations to simulate incompressible flow. These often require a combination of grid-based solvers and spectral methods.

*   **fluidsGL**: An interactive simulation where the user can disturb a fluid grid. It uses a stable fluids solver and maps CUDA buffers directly to OpenGL for zero-copy rendering.
*   **oceanFFT**: Simulates a realistic ocean surface using Fast Fourier Transforms (via `cuFFT`) to generate height maps from frequency-domain wave spectra.

For details, see [Fluid Dynamics and Visualization](#11.2).

## Volume Rendering and Medical Imaging

This sub-category focuses on the visualization and processing of 3D volumetric data, commonly found in CT or MRI scans.

*   **Marching Cubes**: Extracts a polygonal isosurface from a 3D scalar field. This sample demonstrates the use of prefix sums (scan) to manage variable output geometry per thread.
*   **Volume Render**: Uses 3D texture sampling and ray casting to render semi-transparent volumes.
*   **SimpleTexture3D**: A foundational sample showing how to bind and sample from `cudaArray` 3D textures.

For details, see [Volume Rendering and Medical Imaging](#11.3).

## Computer Vision and Signal Processing

Several samples demonstrate high-level vision algorithms that serve as building blocks for robotics and autonomous systems.

*   **HSOpticalFlow**: Implements the Horn-Schunck variational method for estimating motion vectors between frames.
*   **Stereo Disparity**: Computes depth maps from stereo image pairs using block-matching techniques.
*   **Recursive Gaussian**: Shows how to implement a Gaussian blur with O(1) complexity relative to the filter radius using recursive filtering.

Sources: [Common/helper_math.h:88-103]() (Vector types used in Vision)

## Domain-Specific Math Utilities

Many of these applications rely on `Common/helper_math.h`, which provides Cg-style operator overloading for CUDA vector types (e.g., `float3`, `float4`). This allows developers to write concise mathematical expressions like `a + b * c` for vectors within kernels.

```mermaid
graph LR
    subgraph "helper_math.h"
        [Vector Ops] --> [make_float2]
        [Vector Ops] --> [make_float3]
        [Vector Ops] --> [make_float4]
        [Math Functions] --> [fminf/fmaxf]
        [Math Functions] --> [rsqrtf]
    end
    [nbody] -.-> [Vector Ops]
    [fluidsGL] -.-> [Vector Ops]
```

Sources: [Common/helper_math.h:58-81](), [Common/helper_math.h:135-158]()

---

