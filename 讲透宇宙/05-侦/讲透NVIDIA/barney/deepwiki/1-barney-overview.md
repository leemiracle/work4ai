<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/barney · page 1 Barney Overview · fetched 2026-10-26 -->

# Barney Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitmodules](.gitmodules)
- [CMakeLists.txt](CMakeLists.txt)
- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



Barney is a high-performance rendering engine that implements the **Khronos ANARI Cross-Platform Rendering API** [README.md:19-21](). While primarily optimized for NVIDIA OptiX and CUDA-capable GPUs, it features a modular backend architecture supporting AMD GPUs (via HIP/HIPRT) and CPUs (via Embree) [README.md:108-127]().

Barney is specifically designed for **Scientific Visualization (Sci-Vis)**, supporting large-scale data types such as structured volumes, Block-Structured AMR, and unstructured meshes [README.md:63-72](). It scales from single-laptop GPUs to multi-GPU nodes and massive MPI-parallel HPC clusters [README.md:23-28]().

### High-Level System Architecture

Barney functions as a library with a public C API that applications (like `hayStack` or ParaView) link against [README.md:88-92](). Internally, it translates ANARI state into a specialized ray tracing core (`rtcore`) that abstracts the underlying hardware.

#### Component Interaction Diagram
The following diagram illustrates how the primary subsystems relate, from the public API down to the hardware-specific backends.

**Barney Subsystem Relationship**
```mermaid
graph TD
    subgraph "Public Interface"
        [ANARI_API] --> ["BarneyDevice (ANARI Layer)"]
        ["Native C API"] --> ["BNContext (barney.h)"]
    end

    subgraph "Core Engine"
        ["BarneyDevice (ANARI Layer)"] --> ["Context (Internal)"]
        ["BNContext (barney.h)"] --> ["Context (Internal)"]
        ["Context (Internal)"] --> ["Model / Group / Geometry"]
        ["Context (Internal)"] --> ["GlobalTrace (MPI/Local)"]
    end

    subgraph "Ray Tracing Core (rtcore)"
        ["Model / Group / Geometry"] --> ["rtcore::Backend"]
        ["rtcore::Backend"] --> ["OptiXBackend"]
        ["rtcore::Backend"] --> ["CudaBackend"]
        ["rtcore::Backend"] --> ["HiprtBackend"]
        ["rtcore::Backend"] --> ["EmbreeBackend"]
    end

    subgraph "Hardware/Libraries"
        ["OptiXBackend"] --> ["NVIDIA OptiX"]
        ["CudaBackend"] --> ["CUDA Runtime"]
        ["HiprtBackend"] --> ["AMD HIPRT"]
        ["EmbreeBackend"] --> ["Intel Embree"]
    end
```
**Sources:** [README.md:17-85](), [CMakeLists.txt:43-108](), [CMakeLists.txt:158-185]()

### Primary Use Cases

1.  **Scientific Visualization:** Efficiently rendering geometric primitives (spheres, cylinders, curves) and complex scalar fields found in scientific datasets [README.md:63-72]().
2.  **Path Tracing:** Supporting global illumination effects including HDRI environment maps, glossy reflections, volumetric scattering, and depth-of-field [README.md:74-84]().
3.  **Distributed Rendering:**
    *   **Data Replicated:** Every GPU renders the same scene to different image tiles to increase frame rates [README.md:49-52]().
    *   **Data Parallel:** Large models are partitioned across GPUs/nodes, allowing the rendering of datasets that exceed the memory of a single device [README.md:52-59]().

### Hardware Backends

Barney abstracts hardware through its `rtcore` layer, enabling execution across diverse platforms:

| Backend | Hardware Target | Key Dependencies |
| :--- | :--- | :--- |
| **OptiX** | NVIDIA RTX GPUs | OptiX SDK, OWL [CMakeLists.txt:133-147]() |
| **CUDA** | NVIDIA GPUs | CUDA Toolkit [CMakeLists.txt:85-99]() |
| **HIPRT** | AMD RDNA2+ GPUs | ROCm, HIPRT SDK [CMakeLists.txt:75-84]() |
| **Embree** | x86/ARM CPUs | Intel Embree [CMakeLists.txt:189-192]() |

### Code Entity Mapping

The following diagram bridges the high-level concepts to the specific C++ classes and files that implement them.

**Code Entity Mapping**
```mermaid
graph LR
    subgraph "Management Entities"
        [Context] -- "implements" --> ["Context (barney/Context.h)"]
        [MPI_Support] -- "managed by" --> ["MPIContext (barney/MPIContext.h)"]
    end

    subgraph "Scene Entities"
        [Geometry] -- "defined in" --> ["Geometry (barney/geometry/Geometry.h)"]
        [Volume] -- "defined in" --> ["Volume (barney/volume/Volume.h)"]
        [Model] -- "defined in" --> ["Model (barney/Model.h)"]
    end

    subgraph "Rendering Entities"
        [Ray_Gen] -- "kernel" --> ["renderLaunch (renderRays.cu)"]
        [Shading] -- "kernel" --> ["shadeRays (shadeRays.cu)"]
        [Acceleration] -- "via" --> ["OWL (submodules/owl)"]
    end
```
**Sources:** [CMakeLists.txt:144-147](), [README.md:108-117](), [.gitmodules:4-12]()

---

### Detailed Documentation Sections

For specific details on building, configuring, or the internal mechanics of Barney, refer to the following child pages:

*   **[Getting Started: Building and Configuration](#1.1)**
    Provides instructions for CMake setup, enabling MPI (`BARNEY_MPI`), and selecting hardware backends like OptiX or HIPRT [README.md:135-165]().
*   **[CI/CD and Testing Infrastructure](#1.2)**
    Details the automated testing workflows for Ubuntu and Windows environments [README.md:6-9]().

**Sources:** [README.md:135-165](), [CMakeLists.txt:21-27]()

---

