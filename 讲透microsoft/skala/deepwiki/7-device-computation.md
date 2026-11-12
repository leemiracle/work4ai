<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/skala · page 7 Device Computation · fetched 2026-10-26 -->

# Device Computation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [third_party/gauxc/attic/src/integrator/cuda/collocation_masked_combined_kernels.hpp](third_party/gauxc/attic/src/integrator/cuda/collocation_masked_combined_kernels.hpp)
- [third_party/gauxc/attic/src/integrator/cuda/collocation_masked_kernels.hpp](third_party/gauxc/attic/src/integrator/cuda/collocation_masked_kernels.hpp)
- [third_party/gauxc/attic/src/integrator/cuda/cuda_weights.cu](third_party/gauxc/attic/src/integrator/cuda/cuda_weights.cu)
- [third_party/gauxc/attic/src/new_integrator/device/cuda/collocation_masked_combined_kernels.hpp](third_party/gauxc/attic/src/new_integrator/device/cuda/collocation_masked_combined_kernels.hpp)
- [third_party/gauxc/attic/src/new_integrator/device/cuda/collocation_masked_kernels.hpp](third_party/gauxc/attic/src/new_integrator/device/cuda/collocation_masked_kernels.hpp)
- [third_party/gauxc/attic/src/new_integrator/device/cuda/cuda_weights.cu](third_party/gauxc/attic/src/new_integrator/device/cuda/cuda_weights.cu)
- [third_party/gauxc/attic/src/new_integrator/device/hip/collocation_masked_combined_kernels.hpp](third_party/gauxc/attic/src/new_integrator/device/hip/collocation_masked_combined_kernels.hpp)
- [third_party/gauxc/attic/src/new_integrator/device/hip/collocation_masked_kernels.hpp](third_party/gauxc/attic/src/new_integrator/device/hip/collocation_masked_kernels.hpp)
- [third_party/gauxc/attic/src/new_integrator/device/hip/hip_weights.hip](third_party/gauxc/attic/src/new_integrator/device/hip/hip_weights.hip)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_radial.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_radial.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l1_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l2_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_cartesian_l2_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l0_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l0_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_gradient.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_gradient.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l1_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l3_lapgrad.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l3_lapgrad.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_laplacian.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l4_laplacian.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation_masked_combined_kernels.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation_masked_combined_kernels.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation_masked_kernels.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation_masked_kernels.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/cuda_ssf_1d.cu](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/cuda_ssf_1d.cu)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/cuda_ssf_2d.hu](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/cuda_ssf_2d.hu)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/grid_to_center.cu](third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/grid_to_center.cu)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/collocation_masked_combined_kernels.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/collocation_masked_combined_kernels.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/collocation_masked_kernels.hpp](third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/collocation_masked_kernels.hpp)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/grid_to_center.hip](third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/grid_to_center.hip)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/hip_ssf_1d.hip](third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/hip_ssf_1d.hip)
- [third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/hip_ssh_2d.hip](third_party/gauxc/src/xc_integrator/local_work_driver/device/hip/kernels/hip_ssh_2d.hip)

</details>



## Purpose and Scope

This section documents GPU-based computation in GauXC, which executes exchange-correlation integration kernels on NVIDIA (CUDA) and AMD (HIP) GPUs. Device computation provides the performance-critical path for large-scale DFT calculations by parallelizing basis function evaluation, weight calculation, and matrix operations across thousands of GPU threads.

For CPU-based computation paths, see [Host Computation](#6). For the overall execution model that determines when device vs host paths are used, see [Execution Model: Host vs Device](#4.2). Platform-specific abstraction details are covered in [Platform Abstraction: CUDA and HIP](#9).

**Sources:** [third_party/gauxc/attic/src/integrator/cuda/cuda_weights.cu:1-642](), [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation_masked_kernels.hpp:1-159]()

## Kernel Ecosystem Overview

Device computation is organized into three major kernel families that execute sequentially in the integration pipeline:

| Kernel Family | Primary Functions | Purpose | Importance |
|---------------|------------------|---------|------------|
| **Weight Calculation** | `partition_weights_cuda_SoA`, `partition_weights_hip_SoA` | Compute integration weights using SSF partitioning | 94.32 |
| **Collocation** | `collocation_device_shell_to_task_kernel_*`, `collocation_device_masked_kernel` | Evaluate basis functions and derivatives | 82-86 |
| **Matrix Operations** | `sym_pack_submat`, `asym_pack_submat`, `sym_task_inc_potential`, `asym_task_inc_potential` | Pack density matrices and increment potential matrices | 79.49 |

These kernels operate on `XCDeviceTask` structures that encapsulate grid points, basis function screening data, and device memory pointers. Each kernel family is specialized for both CUDA and HIP platforms through compile-time selection.

**Sources:** [third_party/gauxc/attic/src/integrator/cuda/cuda_weights.cu:564-623](), [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation_masked_kernels.hpp:16-71]()

## Device Computation Architecture

```mermaid
graph TB
    subgraph "Entry Points"
        CUDA_ENTRY["partition_weights_cuda_SoA<br/>collocation_device_*_kernel<br/>sym_pack_submat"]
        HIP_ENTRY["partition_weights_hip_SoA<br/>collocation_device_*_kernel<br/>sym_pack_submat"]
    end
    
    subgraph "Weight Calculation Stage"
        DIST["compute_point_center_dist<br/>Kernel<br/>Lines: cuda_weights.cu:23-70"]
        SSF_1D["modify_weights_ssf_kernel_1d<br/>1D SIMT Kernel<br/>Lines: cuda_weights.cu:242-387"]
        SSF_2D["modify_weights_ssf_kernel_2d<br/>2D Warp-level Kernel<br/>Lines: cuda_weights.cu:411-553"]
    end
    
    subgraph "Collocation Stage"
        MASKED["collocation_device_masked_kernel<br/>Shell-based Evaluation<br/>Lines: collocation_masked_kernels.hpp:21-71"]
        SHELL_TO_TASK["collocation_device_shell_to_task_kernel_*<br/>Task-based Evaluation<br/>Spherical L0-L4, Cartesian L0-L4<br/>Value/Grad/Hess/Lapl/LapGrad"]
        RADIAL["collocation_device_radial_eval<br/>Gaussian Primitive Accumulation<br/>Lines: collocation_radial.hpp:16-45"]
        ANGULAR_SPH["collocation_spherical_unnorm_angular<br/>Spherical Harmonics"]
        ANGULAR_CART["collocation_cartesian_angular<br/>Cartesian Polynomials"]
    end
    
    subgraph "Matrix Operation Stage"
        PACK["sym_pack_submat<br/>asym_pack_submat<br/>Extract Submatrix"]
        INC["sym_task_inc_potential<br/>asym_task_inc_potential<br/>Accumulate Results"]
    end
    
    subgraph "Data Structures"
        TASK["XCDeviceTask<br/>npts, points_x/y/z<br/>bf, dbfx/y/z, d2bf*<br/>bfn_screening, cou_screening"]
        SHELL["Shell&lt;T&gt;<br/>nprim, l, pure<br/>O_data, alpha_data, coeff_data"]
        S2T["ShellToTaskDevice<br/>ntask, shell_device<br/>task_idx_device<br/>task_shell_offs_device"]
    end
    
    CUDA_ENTRY --> DIST
    HIP_ENTRY --> DIST
    DIST --> SSF_2D
    DIST -.->|fallback| SSF_1D
    
    SSF_2D --> MASKED
    SSF_2D --> SHELL_TO_TASK
    
    MASKED --> RADIAL
    SHELL_TO_TASK --> RADIAL
    
    RADIAL --> ANGULAR_SPH
    RADIAL --> ANGULAR_CART
    
    ANGULAR_SPH --> PACK
    ANGULAR_CART --> PACK
    
    PACK --> INC
    
    TASK -.->|provides| DIST
    TASK -.->|provides| MASKED
    TASK -.->|provides| SHELL_TO_TASK
    SHELL -.->|provides| RADIAL
    S2T -.->|provides| SHELL_TO_TASK
    
    style DIST fill:#f9f9f9
    style SSF_2D fill:#f9f9f9
    style SHELL_TO_TASK fill:#f9f9f9
    style RADIAL fill:#f9f9f9
```

**Diagram: Device Kernel Architecture and Data Flow**

This architecture shows how the three kernel families process data through the integration pipeline. Weight calculation kernels first compute point-to-center distances, then apply SSF partitioning to generate integration weights. Collocation kernels evaluate basis functions by separating radial (Gaussian primitive) evaluation from angular (spherical/Cartesian polynomial) evaluation. Matrix operations extract density submatrices and accumulate potential contributions.

**Sources:** [third_party/gauxc/attic/src/integrator/cuda/cuda_weights.cu:23-70](), [third_party/gauxc/attic/src/integrator/cuda/cuda_weights.cu:411-553](), [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_radial.hpp:16-45](), [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation_masked_kernels.hpp:21-71]()

## Kernel Specialization Strategy

Device kernels employ extensive compile-time specialization to optimize for different computational scenarios:

```mermaid
graph LR
    subgraph "Collocation Kernel Specialization Matrix"
        ROOT["collocation_device_shell_to_task_kernel"]
        
        ROOT --> COORD_SPH["Spherical<br/>pure = true"]
        ROOT --> COORD_CART["Cartesian<br/>pure = false"]
        
        COORD_SPH --> SPH_L0["L0: S-orbital"]
        COORD_SPH --> SPH_L1["L1: P-orbital"]
        COORD_SPH --> SPH_L2["L2: D-orbital"]
        COORD_SPH --> SPH_L3["L3: F-orbital"]
        COORD_SPH --> SPH_L4["L4: G-orbital"]
        
        SPH_L2 --> SPH_L2_VAL["_gradient<br/>bf, dbfx/y/z"]
        SPH_L2 --> SPH_L2_HESS["_hessian<br/>+ d2bfxx/xy/xz/yy/yz/zz"]
        SPH_L2 --> SPH_L2_LAPL["_laplacian<br/>+ d2bflapl"]
        SPH_L2 --> SPH_L2_LAPGRAD["_lapgrad<br/>+ d3bflapl_x/y/z"]
        
        COORD_CART --> CART_L0["L0: 1 function"]
        COORD_CART --> CART_L1["L1: 3 functions"]
        COORD_CART --> CART_L2["L2: 6 functions"]
        
        CART_L1 --> CART_L1_VAL["_gradient"]
        CART_L1 --> CART_L1_LAPL["_laplacian"]
    end
    
    subgraph "Launch Configuration"
        SPH_L2_LAPL -.->|"__launch_bounds__(128,2)"| CONFIG1["128 threads/block<br/>2 blocks/SM"]
        SPH_L3_LAPGRAD -.->|"__launch_bounds__(128,2)"| CONFIG2["128 threads/block<br/>2 blocks/SM"]
    end
    
    subgraph "Shared Memory Usage"
        SPH_L2_LAPL -.-> SM_ALPHA["alpha[4][32+1]<br/>Exponents"]
        SPH_L2_LAPL -.-> SM_COEFF["coeff[4][32+1]<br/>Coefficients"]
    end
```

**Diagram: Collocation Kernel Specialization Hierarchy**

Each combination of coordinate system (spherical/Cartesian), angular momentum (L0-L4), and derivative order (value/gradient/Hessian/Laplacian/Laplacian gradient) generates a separate kernel. This specialization eliminates runtime branching and enables aggressive compiler optimization. Shared memory arrays cache primitive exponents and coefficients for each warp, with indexing based on `threadIdx.x/32` to provide per-warp storage.

**Sources:** [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp:18-273](), [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l3_lapgrad.hpp:18-510]()

## Weight Calculation Kernels

Weight calculation uses a two-stage GPU pipeline to compute partition weights with SSF (Smooth Step Function) partitioning:

**Stage 1: Distance Computation** - The `compute_point_center_dist` kernel computes Euclidean distances between all integration points and atomic centers:

```mermaid
graph TB
    INPUT["Input Arrays<br/>points: npts × 3<br/>coords: natoms × 3"]
    
    LOAD_COORD["Load atomic coordinates<br/>into register<br/>coord_reg = coords_vec[iAtom]<br/>Lines: cuda_weights.cu:42-46"]
    
    LOAD_POINTS["Load point coordinates<br/>into shared memory<br/>point_buffer[threadIdx.x]<br/>Lines: cuda_weights.cu:48-51"]
    
    SYNC1["__syncthreads()<br/>Line: cuda_weights.cu:52"]
    
    COMPUTE["Compute distances<br/>rx = point.x - coord.x<br/>dist = sqrt(rx² + ry² + rz²)<br/>Lines: cuda_weights.cu:56-64"]
    
    SYNC2["__syncthreads()<br/>Line: cuda_weights.cu:67"]
    
    OUTPUT["Output: dist[natoms × npts]"]
    
    INPUT --> LOAD_COORD
    INPUT --> LOAD_POINTS
    LOAD_COORD --> COMPUTE
    LOAD_POINTS --> SYNC1
    SYNC1 --> COMPUTE
    COMPUTE --> SYNC2
    SYNC2 --> OUTPUT
```

**Diagram: Distance Computation Kernel Data Flow**

The kernel uses a blocked algorithm where atomic coordinates are cached in registers and point coordinates in shared memory. Threads synchronize after loading shared memory and after computation to ensure memory consistency across the warp.

**Sources:** [third_party/gauxc/attic/src/new_integrator/device/cuda/cuda_weights.cu:23-70]()

**Stage 2: SSF Weight Modification** - The `modify_weights_ssf_kernel_2d` kernel applies the Smooth Step Function partition scheme:

The kernel implements two key mathematical functions:

- `gFrisch(x)`: 7th-order polynomial `(35(s_x - s_x³) + 21s_x⁵ - 5s_x⁷) / 16` where `s_x = x / 0.64`
- `sFrisch(x)`: Smooth step function with cutoffs at `±0.64`

Each warp collaboratively processes one integration point, using atomic operations and warp-level synchronization for dynamic work distribution. The kernel employs vectorized loads (`double2`) to process 8 atomic centers per iteration for improved memory bandwidth.

**Sources:** [third_party/gauxc/attic/src/new_integrator/device/cuda/cuda_weights.cu:389-409](), [third_party/gauxc/attic/src/new_integrator/device/cuda/cuda_weights.cu:411-553]()

For detailed documentation of weight calculation algorithms and optimizations, see [Weight Calculation Kernels](#7.1).

## Collocation Kernels

Collocation kernels evaluate basis functions and their derivatives at integration points. Two kernel variants exist:

### Masked Kernels

The `collocation_device_masked_kernel` processes shells using a 2D thread grid where each thread evaluates one point-shell pair:

**Key characteristics:**
- Thread mapping: `tid_x` indexes points, `tid_y` indexes shells
- Radial evaluation: Accumulates Gaussian primitives `Σ coeff[i] * exp(-alpha[i] * rsq)`
- Angular evaluation: Dispatches to `collocation_spherical_unnorm_angular` or `collocation_cartesian_angular`
- Memory access: Direct indexing `eval_device[ibf*npts + ipt]`

The derivative variant `collocation_device_masked_kernel_deriv1` additionally computes first derivatives by accumulating `tmp_x -= 2*a*e*xc` terms during radial evaluation.

**Sources:** [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation_masked_kernels.hpp:21-71](), [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation_masked_kernels.hpp:82-155]()

### Shell-to-Task Kernels

The `collocation_device_shell_to_task_kernel_*` family provides extensive specialization for optimal performance:

```mermaid
graph TB
    subgraph "Kernel Launch Configuration"
        GRID["Grid: blocks.z = nshell<br/>Warp-based point processing"]
        SM["Shared Memory<br/>alpha[4][33]: exponents<br/>coeff[4][33]: coefficients<br/>Per-warp indexing"]
    end
    
    subgraph "Shell Loop"
        LOAD_SHELL["Load shell data<br/>nprim, O, alpha, coeff<br/>Lines: *:38-52"]
        TASK_LOOP["For each task in shell<br/>global_warp_id stride<br/>Lines: *:56-57"]
    end
    
    subgraph "Point Loop"
        POINT_ITER["For each point in warp<br/>threadIdx.x % warp_size<br/>Lines: *:74"]
        
        RADIAL["Radial Evaluation<br/>radial_eval = Σ coeff * exp(-alpha*rsq)<br/>radial_eval_alpha = Σ a*coeff*exp(-a*rsq)<br/>radial_eval_alpha_squared = Σ a²*coeff*exp(-a*rsq)<br/>Lines: *:88-103"]
        
        CSE["Common Subexpression Pre-computation<br/>x0, x1, ..., xN<br/>Symbolic algebra optimizations<br/>Lines: *:105-160"]
        
        ANGULAR["Angular Evaluation<br/>basis_eval[ipt + m*npts] = radial * angular<br/>Lines: *:164-168"]
        
        DERIV["Derivative Evaluation<br/>basis_x_eval, basis_y_eval, basis_z_eval<br/>d2bflapl, d3bflapl_x/y/z<br/>Lines: *:172-195"]
    end
    
    GRID --> LOAD_SHELL
    SM --> LOAD_SHELL
    LOAD_SHELL --> TASK_LOOP
    TASK_LOOP --> POINT_ITER
    POINT_ITER --> RADIAL
    RADIAL --> CSE
    CSE --> ANGULAR
    CSE --> DERIV
```

**Diagram: Shell-to-Task Kernel Execution Flow**

Shell-to-task kernels cache shell data in shared memory once per shell, then process multiple tasks. Each warp handles one task, with individual threads processing points. The radial evaluation computes multiple weighted sums simultaneously for derivatives. Common subexpressions are pre-computed to minimize register pressure and arithmetic operations.

**Sources:** [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_shell_to_task_kernels_spherical_l2_laplacian.hpp:18-273]()

### Radial and Angular Separation

The collocation process separates into radial and angular components:

**Radial Evaluation** (`collocation_device_radial_eval`):
- Computes Gaussian primitive accumulation for each point
- Produces `radial_eval`, `radial_eval_alpha`, `radial_eval_alpha_squared` (for derivatives)
- Scaling factors: `radial_eval_alpha *= -2`, `radial_eval_alpha_squared *= 4`

**Angular Evaluation**:
- Spherical harmonics: `collocation_spherical_unnorm_angular`
- Cartesian polynomials: `collocation_cartesian_angular`
- Selected via `shell.pure()` flag at runtime

This separation enables code reuse across angular momenta while maintaining computational efficiency.

**Sources:** [third_party/gauxc/src/xc_integrator/local_work_driver/device/cuda/kernels/collocation/collocation_radial.hpp:16-96]()

For comprehensive documentation of collocation algorithms, kernel variants, and specialization details, see [Collocation Kernels](#7.2).

## Matrix Operations

Matrix operation kernels transfer data between full matrices (size `LDA × LDA`) and sub-matrices (size `LDAS × LDAS`) that correspond to screened shell pairs. These operations minimize memory transfer and enable efficient GPU computation on relevant subspaces.

**Pack Operations** extract density matrix elements:
- `sym_pack_submat`: Symmetric matrices
- `asym_pack_submat`: Asymmetric matrices (UKS, GKS)

**Increment Operations** accumulate potential contributions:
- `sym_task_inc_potential`: Symmetric accumulation
- `asym_task_inc_potential`: Asymmetric accumulation

Both operation types utilize the `submat_cut` data structure for block-tiled execution and screening via `bfn_screening` and `cou_screening` systems.

**Sources:** Based on overall system architecture from high-level diagrams.

For detailed documentation of matrix operation kernels, screening systems, and performance optimizations, see [Matrix Operations](#7.3).

## Platform Abstraction

GauXC supports both CUDA and HIP platforms through dual implementation:

| Aspect | CUDA | HIP |
|--------|------|-----|
| **File Extension** | `.cu` | `.hip` |
| **Kernel Launch** | `kernel<<<blocks, threads, smem, stream>>>()` | `hipLaunchKernelGGL(kernel, blocks, threads, smem, stream, ...)` |
| **Stream Type** | `cudaStream_t` | `hipStream_t` |
| **Synchronization** | `__syncthreads()`, `__syncwarp()` | `__syncthreads()`, `__syncwarp()` (same) |
| **Warp Intrinsics** | `__shfl_sync()`, `__any_sync()` | `__shfl_sync()`, `__any_sync()` (same) |
| **Constants** | `cuda::warp_size`, `cuda::max_warps_per_thread_block` | `hip::warp_size`, `hip::max_warps_per_thread_block` |

The implementations are nearly identical, with differences primarily in:
- Kernel launch syntax
- Header file includes (`cuda_runtime.h` vs `hip/hip_runtime.h`)
- Namespace prefixes (`cuda::` vs `hip::`)
- Device property query functions

Build-time configuration via `GAUXC_ENABLE_CUDA` and `GAUXC_ENABLE_HIP` determines which implementations are compiled.

**Sources:** [third_party/gauxc/attic/src/integrator/cuda/cuda_weights.cu:1-10](), [third_party/gauxc/attic/src/new_integrator/device/hip/hip_weights.hip:1-10]()

For comprehensive platform abstraction details, see [Platform Abstraction: CUDA and HIP](#9).

## Execution Pipeline Integration

Device kernels integrate into the overall execution pipeline through the `DeviceLocalWorkDriver`:

1. **Task Generation**: `LoadBalancer` creates `XCDeviceTask` structures containing grid points and screening data
2. **Weight Calculation**: `partition_weights_*_SoA` computes integration weights
3. **Matrix Pack**: Density matrix elements transferred to device via pack operations
4. **Collocation**: Basis functions and derivatives evaluated at grid points
5. **XC Evaluation**: Functional evaluation (density, gradient, Hessian, etc.)
6. **Matrix Increment**: Potential contributions accumulated back to host via increment operations
7. **Reduction**: `ReductionDriver` performs MPI aggregation across ranks

All kernel launches are asynchronous and submitted to CUDA/HIP streams for overlapped execution with host operations.

**Sources:** Based on overall system architecture from high-level diagrams.

For execution model details, see [Execution Model: Host vs Device](#4.2). For task system documentation, see [Task System and Data Structures](#4.3).

---

