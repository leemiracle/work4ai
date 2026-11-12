<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/skala · extra page Shell-to-Task Kernels · fetched 2026-10-26 -->

# Shell-to-Task Kernels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1_hessian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1_hessian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1_lapgrad.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1_lapgrad.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l2_lapgrad.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l2_lapgrad.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l2_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l2_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l3_hessian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l3_hessian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l3_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l3_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l4_gradient.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l4_gradient.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l0_hessian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l0_hessian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l0_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l0_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_gradient.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_gradient.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_hessian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_hessian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_lapgrad.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_lapgrad.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_hessian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_hessian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_lapgrad.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_lapgrad.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l3_hessian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l3_hessian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l3_lapgrad.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l3_lapgrad.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_hessian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_hessian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_laplacian.hpp)

</details>



## Purpose and Scope

Shell-to-Task kernels are GPU kernels that evaluate basis functions and their derivatives at quadrature points for DFT exchange-correlation integration. These kernels implement the "shell-to-task" parallelization strategy where multiple computational tasks can be associated with a single atomic shell, and each task is assigned to a GPU warp for parallel execution.

This page documents the kernel architecture, thread organization, memory management, and evaluation algorithms. For the broader collocation kernel ecosystem, see [Collocation Kernels](#7.2). For masked collocation variants, see [Masked Collocation Kernels](#7.2.1). For the complete kernel specialization landscape, see [Kernel Specialization Matrix](#7.2.3).

Sources: 
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:1-660]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l4_gradient.hpp:1-378]()

## Shell-to-Task Parallelization Architecture

### Conceptual Overview

```mermaid
graph TB
    subgraph "Shell Level"
        S0["Shell 0<br/>(L=2, nprim=5)"]
        S1["Shell 1<br/>(L=1, nprim=3)"]
        S2["Shell 2<br/>(L=3, nprim=4)"]
    end
    
    subgraph "Task Level"
        T0["Task 0<br/>(npts=256)"]
        T1["Task 1<br/>(npts=128)"]
        T2["Task 2<br/>(npts=192)"]
        T3["Task 3<br/>(npts=64)"]
        T4["Task 4<br/>(npts=256)"]
    end
    
    subgraph "Warp Assignment"
        W0["Warp 0"]
        W1["Warp 1"]
        W2["Warp 2"]
        W3["Warp 3"]
        W4["Warp 4"]
    end
    
    subgraph "Thread Level"
        PT0["32 threads<br/>process 256 points"]
        PT1["32 threads<br/>process 128 points"]
        PT2["32 threads<br/>process 192 points"]
    end
    
    S0 --> T0
    S0 --> T1
    S1 --> T2
    S1 --> T3
    S2 --> T4
    
    T0 --> W0
    T1 --> W1
    T2 --> W2
    T3 --> W3
    T4 --> W4
    
    W0 --> PT0
    W1 --> PT1
    W2 --> PT2
```

**Diagram: Shell-to-Task-to-Warp Mapping**

The shell-to-task pattern enables fine-grained load balancing by allowing a single shell to be associated with multiple tasks. Each task processes a batch of quadrature points and is assigned to an independent warp (32 threads on NVIDIA GPUs).

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:30-56]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_hessian.hpp:30-56]()

### Data Structure Mapping

```mermaid
graph LR
    subgraph "ShellToTaskDevice[ish]"
        STT_NTASK["ntask"]
        STT_SHELL["shell_device*"]
        STT_IDX["task_idx_device*"]
        STT_OFFS["task_shell_offs_device*"]
    end
    
    subgraph "Shell Device"
        SHELL_NPRIM["nprim()"]
        SHELL_O["O_data()"]
        SHELL_ALPHA["alpha_data()"]
        SHELL_COEFF["coeff_data()"]
    end
    
    subgraph "XCDeviceTask[itask]"
        TASK_PTS["points_x/y/z"]
        TASK_NPTS["npts"]
        TASK_BF["bf"]
        TASK_DBF["dbfx/dbfy/dbfz"]
        TASK_D2BF["d2bfxx/xy/xz/yy/yz/zz"]
        TASK_LAPL["d2bflapl"]
        TASK_LAPGRAD["d3bflapl_x/y/z"]
    end
    
    STT_SHELL --> SHELL_NPRIM
    STT_SHELL --> SHELL_O
    STT_SHELL --> SHELL_ALPHA
    STT_SHELL --> SHELL_COEFF
    
    STT_IDX --> TASK_PTS
    STT_OFFS --> TASK_BF
```

**Diagram: Data Structure Relationships in Shell-to-Task Kernels**

`ShellToTaskDevice` arrays store the mapping between shells and tasks. For each shell index `ish`, the structure contains the number of associated tasks, a pointer to shell parameters, and arrays indexing into the task list.

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:31-34]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:58-78]()

## Kernel Structure and Organization

### Launch Configuration

All shell-to-task kernels use the `__launch_bounds__` directive to guide occupancy:

- **Standard kernels** (L1-L4): `__launch_bounds__(128, 2)` - 128 threads per block, minimum 2 blocks per SM
- **L0 kernels**: `__launch_bounds__(256, 2)` - 256 threads per block for S-orbital efficiency

The kernel signature is consistent across all variants:

```cpp
__global__ __launch_bounds__(128,2) 
void collocation_device_shell_to_task_kernel_<coord>_<deriv>_<L>(
  uint32_t nshell,
  ShellToTaskDevice* __restrict__ shell_to_task,
  XCDeviceTask* __restrict__ device_tasks
)
```

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:18-22]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l0_hessian.hpp:18-22]()

### Execution Flow

```mermaid
graph TD
    START["Kernel Entry"]
    
    START --> ALLOC["Allocate shared memory<br/>alpha[4][33], coeff[4][33]"]
    
    ALLOC --> SHELL_LOOP["for ish in blockIdx.z : gridDim.z"]
    
    SHELL_LOOP --> LOAD_META["Load shell metadata<br/>ntasks, shell_device, task indices"]
    
    LOAD_META --> LOAD_SHELL["Load shell data to registers<br/>nprim, O (center)"]
    
    LOAD_SHELL --> CALC_WARP["Calculate warp IDs<br/>global_warp_id, nwarp_global"]
    
    CALC_WARP --> LOAD_COEFFS["Load coeffs/alphas to SM<br/>First warp only, warp_size elements"]
    
    LOAD_COEFFS --> TASK_LOOP["for itask in global_warp_id : nwarp_global"]
    
    TASK_LOOP --> GET_TASK["Retrieve task from device_tasks<br/>using task_idx[itask]"]
    
    GET_TASK --> CALC_OFFSET["Calculate output offset<br/>shoff = task_shell_offs[itask] * npts"]
    
    CALC_OFFSET --> POINT_LOOP["for ipt in warp_rank : cuda::warp_size : npts"]
    
    POINT_LOOP --> LOAD_POINT["Load point coordinates<br/>points_x/y/z[ipt]"]
    
    LOAD_POINT --> RADIAL["Evaluate radial part<br/>Loop over nprim primitives"]
    
    RADIAL --> ANGULAR["Evaluate angular part<br/>Compute basis + derivatives"]
    
    ANGULAR --> WRITE["Write results<br/>basis_eval[ipt + k*npts]"]
    
    WRITE --> POINT_LOOP
    
    POINT_LOOP --> TASK_LOOP
    TASK_LOOP --> SHELL_LOOP
    SHELL_LOOP --> END["Kernel Exit"]
```

**Diagram: Shell-to-Task Kernel Execution Flow**

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:25-660]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp:25-274]()

## Memory Hierarchy and Optimization

### Shared Memory Usage

Each kernel allocates shared memory for Gaussian primitive parameters:

```cpp
__shared__ double alpha[4][detail::shell_nprim_max + 1]; 
__shared__ double coeff[4][detail::shell_nprim_max + 1];
double* my_alpha = alpha[threadIdx.x/32];
double* my_coeff = coeff[threadIdx.x/32];
```

The arrays are dimensioned to support 4 warps per block, with `detail::shell_nprim_max = 32` (matching warp size). Each warp maintains its own cache of coefficients and exponents in shared memory.

**Loading Pattern:**
- Only the first warp loads data (cooperative loading)
- Static assertion ensures `shell_nprim_max == cuda::warp_size`
- Each thread loads one element: `my_alpha[warp_rank] = alpha_gm[warp_rank]`

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:25-52]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_hessian.hpp:25-52]()

### Register Optimization

Shell center coordinates are loaded into registers once per shell:

```cpp
const uint32_t nprim = shell->nprim();
const double3 O = *reinterpret_cast<const double3*>(shell->O_data());
```

During point evaluation, relative coordinates are computed and stored in registers:

```cpp
const auto x = point.x - O.x;
const auto y = point.y - O.y;
const auto z = point.z - O.z;
const auto rsq = x*x + y*y + z*z;
```

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:38-94]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l4_gradient.hpp:38-94]()

### Memory Access Patterns

```mermaid
graph TB
    subgraph "Global Memory Reads"
        GM_SHELL["shell_to_task[ish]<br/>Coalesced by block"]
        GM_ALPHA["alpha_gm[warp_rank]<br/>Broadcast within warp"]
        GM_COEFF["coeff_gm[warp_rank]<br/>Broadcast within warp"]
        GM_POINTS["points_x/y/z[ipt]<br/>Strided by warp_size"]
    end
    
    subgraph "Shared Memory"
        SM_ALPHA["alpha[warp_id][warp_rank]"]
        SM_COEFF["coeff[warp_id][warp_rank]"]
    end
    
    subgraph "Registers"
        REG_O["O (x, y, z)"]
        REG_NPRIM["nprim"]
        REG_POINT["point (x, y, z)"]
        REG_RADIAL["radial_eval*"]
    end
    
    subgraph "Global Memory Writes"
        GM_BF["basis_eval[ipt + k*npts]<br/>Strided by npts"]
        GM_DBF["dbfx/y/z[ipt + k*npts]"]
        GM_D2BF["d2bfxx/xy/...[ipt + k*npts]"]
    end
    
    GM_ALPHA --> SM_ALPHA
    GM_COEFF --> SM_COEFF
    GM_SHELL --> REG_O
    GM_SHELL --> REG_NPRIM
    GM_POINTS --> REG_POINT
    
    SM_ALPHA --> REG_RADIAL
    SM_COEFF --> REG_RADIAL
    REG_O --> REG_RADIAL
    REG_POINT --> REG_RADIAL
    
    REG_RADIAL --> GM_BF
    REG_RADIAL --> GM_DBF
    REG_RADIAL --> GM_D2BF
```

**Diagram: Memory Access Pattern in Shell-to-Task Kernels**

Output arrays use a strided layout where `npts` separates consecutive basis functions for the same point. This enables coalesced writes when threads process different points within a warp.

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:65-78]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp:65-69]()

## Thread Organization and Parallelism

### Three-Dimensional Grid Organization

The kernel uses a 3D grid configuration:
- **blockIdx.z**: Shell index (outer loop over shells)
- **blockIdx.x**: Warp group index (distributes tasks across blocks)
- **threadIdx.x**: Thread within block (maps to warps and warp lanes)

```mermaid
graph TB
    subgraph "Grid Dimension Z"
        GZ0["blockIdx.z = 0<br/>Shell 0"]
        GZ1["blockIdx.z = 1<br/>Shell 1"]
        GZ2["blockIdx.z = 2<br/>Shell 2"]
    end
    
    subgraph "Grid Dimension X (per shell)"
        GX0["blockIdx.x = 0"]
        GX1["blockIdx.x = 1"]
        GX2["blockIdx.x = 2"]
    end
    
    subgraph "Block Structure (128 threads)"
        W0["Warp 0 (threads 0-31)"]
        W1["Warp 1 (threads 32-63)"]
        W2["Warp 2 (threads 64-95)"]
        W3["Warp 3 (threads 96-127)"]
    end
    
    subgraph "Task Assignment"
        T0["Task assignment:<br/>global_warp_id = (threadIdx.x + blockIdx.x * 128) / 32"]
        T1["Stride by nwarp_global<br/>= max((128 * gridDim.x) / 32, 1)"]
    end
    
    GZ0 --> GX0
    GZ0 --> GX1
    GX0 --> W0
    GX0 --> W1
    W0 --> T0
    T0 --> T1
```

**Diagram: Three-Dimensional Grid and Warp Assignment**

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:30-42]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:54-56]()

### Warp-Level Point Processing

Within each warp processing a task:

```cpp
const int global_warp_id = (threadIdx.x + blockIdx.x*blockDim.x) / cuda::warp_size;
const int nwarp_global = max((blockDim.x*gridDim.x) / cuda::warp_size, 1);

for(int itask = global_warp_id; itask < ntasks; itask += nwarp_global) {
  // ...
  #pragma unroll 1
  for(int ipt = threadIdx.x % cuda::warp_size; ipt < npts; ipt += cuda::warp_size) {
    // Each thread processes every 32nd point
  }
}
```

The `#pragma unroll 1` directive prevents loop unrolling, which is critical for register pressure management in kernels with complex derivative calculations.

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:41-83]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp:73-74]()

## Radial Evaluation Algorithm

### Gaussian Primitive Accumulation

The radial part evaluation computes weighted sums over Gaussian primitives:

```mermaid
graph LR
    subgraph "Input"
        IN_RSQ["rsq = x² + y² + z²"]
        IN_ALPHA["alpha[i]"]
        IN_COEFF["coeff[i]"]
    end
    
    subgraph "Per-Primitive Loop"
        COMPUTE_E["e = coeff[i] * exp(-alpha[i] * rsq)"]
    end
    
    subgraph "Accumulation"
        ACC_R["radial_eval += e"]
        ACC_RA["radial_eval_alpha += alpha[i] * e"]
        ACC_RA2["radial_eval_alpha_squared += alpha[i]² * e"]
        ACC_RA3["radial_eval_alpha_cubed += alpha[i]³ * e"]
    end
    
    subgraph "Scaling"
        SCALE_RA["radial_eval_alpha *= -2"]
        SCALE_RA2["radial_eval_alpha_squared *= 4"]
        SCALE_RA3["radial_eval_alpha_cubed *= -8"]
    end
    
    IN_RSQ --> COMPUTE_E
    IN_ALPHA --> COMPUTE_E
    IN_COEFF --> COMPUTE_E
    
    COMPUTE_E --> ACC_R
    COMPUTE_E --> ACC_RA
    COMPUTE_E --> ACC_RA2
    COMPUTE_E --> ACC_RA3
    
    ACC_RA --> SCALE_RA
    ACC_RA2 --> SCALE_RA2
    ACC_RA3 --> SCALE_RA3
```

**Diagram: Radial Evaluation and Derivative Chain**

The number of `radial_eval_alpha*` terms computed depends on the maximum derivative order required:
- **Value only**: `radial_eval`
- **Gradient**: `radial_eval`, `radial_eval_alpha`
- **Hessian**: Add `radial_eval_alpha_squared`
- **Laplacian gradient**: Add `radial_eval_alpha_cubed`

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:96-116]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_hessian.hpp:93-109]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l4_gradient.hpp:87-100]()

### Derivative Scaling Factors

The scaling factors applied to `radial_eval_alpha*` terms arise from the chain rule when differentiating the Gaussian exponential `exp(-α*r²)`:

| Term | Scaling | Purpose |
|------|---------|---------|
| `radial_eval_alpha` | `-2` | First derivative: ∂/∂x exp(-α*r²) ∝ -2*α*x |
| `radial_eval_alpha_squared` | `4` | Second derivative: ∂²/∂x² exp(-α*r²) ∝ 4*α² |
| `radial_eval_alpha_cubed` | `-8` | Third derivative: ∂³/∂x³ exp(-α*r²) ∝ -8*α³ |

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:113-115]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_hessian.hpp:107-108]()

## Angular Evaluation and Common Subexpressions

### Common Subexpression Elimination

All kernels employ extensive common subexpression elimination (CSE) to reduce arithmetic operations. For example, in the L4 spherical lapgrad kernel:

```cpp
// Common Subexpressions
const auto x0 = 0.5*sqrt_35; 
const auto x1 = x0*y; 
const auto x2 = x*x1; 
const auto x3 = x*x; 
const auto x4 = x3; 
// ... hundreds more ...
const auto x279 = 8.0*x155; 
```

The CSE phase creates intermediate variables (`x0`, `x1`, ..., `x279`) that are reused in the final basis function evaluation. This optimization is critical for high-derivative kernels where the angular part can involve hundreds of terms.

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:117-398]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_hessian.hpp:110-287]()

### Basis Function Evaluation Structure

After CSE, basis functions are computed from the intermediate expressions:

```cpp
// Evaluate basis function
basis_eval[ipt + 0*npts] = radial_eval*x2*x8;
basis_eval[ipt + 1*npts] = radial_eval*x11*x13;
basis_eval[ipt + 2*npts] = radial_eval*x16*x21;
// ... one entry per basis function in the shell
```

For a shell with angular momentum L, there are `2*L+1` basis functions in spherical coordinates or `(L+1)*(L+2)/2` in Cartesian coordinates.

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:400-409]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l4_gradient.hpp:149-165]()

### Derivative Evaluation

Derivatives follow the same pattern with different angular functions:

```cpp
// Evaluate first derivative of bfn wrt x
basis_x_eval[ipt + 0*npts] = x1*(radial_eval_alpha*x45 + x44);
basis_x_eval[ipt + 1*npts] = x46*x49;
// ...

// Evaluate second derivative of bfn wrt xx
basis_xx_eval[ipt + 0*npts] = x2*(x115 + x47);
basis_xx_eval[ipt + 1*npts] = x11*(x116 + x119);
// ...

// Evaluate Laplacian of bfn 
basis_lapl_eval[ipt + 0*npts] = x2*(x115 + x165 + x184);
// ...
```

The derivative outputs are written to separate arrays (`dbfx`, `dbfy`, `dbfz` for gradients; `d2bfxx`, `d2bfxy`, etc. for Hessians).

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:413-522]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_hessian.hpp:302-400]()

## Kernel Specialization Matrix

### Specialization Dimensions

Shell-to-task kernels are specialized along three dimensions:

```mermaid
graph TB
    subgraph "Angular Momentum"
        L0["L = 0 (S)"]
        L1["L = 1 (P)"]
        L2["L = 2 (D)"]
        L3["L = 3 (F)"]
        L4["L = 4 (G)"]
    end
    
    subgraph "Coordinate System"
        SPHER["Spherical"]
        CART["Cartesian"]
    end
    
    subgraph "Derivative Order"
        VAL["Value only"]
        GRAD["Gradient"]
        HESS["Hessian"]
        LAPL["Laplacian"]
        LAPGRAD["Laplacian + Gradient"]
    end
    
    L0 --> SPHER
    L1 --> SPHER
    L2 --> SPHER
    L3 --> SPHER
    L4 --> SPHER
    
    L1 --> CART
    L2 --> CART
    L3 --> CART
    L4 --> CART
    
    SPHER --> VAL
    SPHER --> GRAD
    SPHER --> HESS
    SPHER --> LAPL
    SPHER --> LAPGRAD
    
    CART --> VAL
    CART --> GRAD
    CART --> HESS
    CART --> LAPL
    CART --> LAPGRAD
```

**Diagram: Kernel Specialization Dimensions**

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:1-8]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l4_gradient.hpp:1-8]()

### Kernel Naming Convention

Kernel functions follow a consistent naming pattern:

```
collocation_device_shell_to_task_kernel_<coord>_<deriv>_<L>
```

Examples:
- `collocation_device_shell_to_task_kernel_spherical_lapgrad_4` - Spherical, Laplacian+gradient, L=4
- `collocation_device_shell_to_task_kernel_cartesian_hessian_3` - Cartesian, Hessian, L=3
- `collocation_device_shell_to_task_kernel_spherical_gradient_1` - Spherical, gradient, L=1

The corresponding header files follow the pattern:
```
collocation_shell_to_task_kernels_<coord>_l<L>_<deriv>.hpp
```

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:18]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l3_hessian.hpp:18]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_gradient.hpp:18]()

### Full Specialization Table

| Angular Momentum | Spherical Variants | Cartesian Variants |
|------------------|-------------------|-------------------|
| L=0 | Value, Gradient, Hessian, Laplacian, Lapgrad | N/A (S-orbitals always spherical) |
| L=1 | Value, Gradient, Hessian, Laplacian, Lapgrad | Value, Gradient, Hessian, Laplacian, Lapgrad |
| L=2 | Value, Gradient, Hessian, Laplacian, Lapgrad | Value, Gradient, Hessian, Laplacian, Lapgrad |
| L=3 | Value, Gradient, Hessian, Laplacian, Lapgrad | Value, Gradient, Hessian, Laplacian, Lapgrad |
| L=4 | Value, Gradient, Hessian, Laplacian, Lapgrad | Value, Gradient, Hessian, Laplacian, Lapgrad |

Each cell represents a unique kernel implementation. For derivative orders:
- **Value**: Computes only `bf`
- **Gradient**: Computes `bf`, `dbfx`, `dbfy`, `dbfz`
- **Hessian**: Computes gradient + `d2bfxx`, `d2bfxy`, `d2bfxz`, `d2bfyy`, `d2bfyz`, `d2bfzz`
- **Laplacian**: Computes value + derivatives + `d2bflapl` (trace of Hessian)
- **Lapgrad**: Computes Laplacian + `d3bflapl_x`, `d3bflapl_y`, `d3bflapl_z`

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l0_hessian.hpp]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1.hpp]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_lapgrad.hpp]()

## Performance Characteristics

### Thread Occupancy Strategy

The `__launch_bounds__(128, 2)` configuration targets:
- **128 threads per block**: Exactly 4 warps, minimizing warp scheduling overhead
- **Minimum 2 blocks per SM**: Ensures sufficient occupancy to hide memory latency

For L0 kernels, `__launch_bounds__(256, 2)` is used because:
- S-orbitals have simpler angular functions (constants)
- Lower register pressure allows doubling threads per block
- Better utilization for small shells with many tasks

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:18]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l0_hessian.hpp:18]()

### Register Pressure Management

High-derivative kernels (Hessian, Laplacian gradient) generate hundreds of common subexpressions that consume registers. Key techniques to manage register pressure:

1. **Loop unroll prevention**: `#pragma unroll 1` on the point loop
2. **Shared memory for primitives**: Alpha/coeff in SM instead of registers
3. **Incremental evaluation**: Basis functions computed and written immediately

Without these optimizations, register spilling would significantly degrade performance.

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:82]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_lapgrad.hpp:82]()

### Work Distribution

The shell-to-task architecture provides fine-grained load balancing:

- **Intra-shell parallelism**: Multiple tasks per shell handled by different warps
- **Inter-shell parallelism**: Multiple shells processed by different blocks (z-dimension)
- **Intra-task parallelism**: 32 threads within a warp process different points

This three-level hierarchy adapts to varying shell sizes and task batching strategies.

Sources:
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_lapgrad.hpp:30-56]()
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp:30-56]()

---

