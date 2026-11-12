<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/AMGX · page 3 Solvers · fetched 2026-10-26 -->

# Solvers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/aggregation/aggregation_amg_level.h](include/aggregation/aggregation_amg_level.h)
- [include/amg_level.h](include/amg_level.h)
- [include/solvers/solver.h](include/solvers/solver.h)
- [src/aggregation/aggregation_amg_level.cu](src/aggregation/aggregation_amg_level.cu)
- [src/amg.cu](src/amg.cu)
- [src/cycles/fixed_cycle.cu](src/cycles/fixed_cycle.cu)
- [src/solvers/block_jacobi_solver.cu](src/solvers/block_jacobi_solver.cu)
- [src/solvers/solver.cu](src/solvers/solver.cu)
- [src/tests/fgmres_zero_initial_residual.cu](src/tests/fgmres_zero_initial_residual.cu)

</details>



## Overview
The AMGX solver framework provides a collection of high-performance GPU-accelerated linear system solvers designed to efficiently solve large sparse linear systems. This page documents the solver framework architecture, the base `Solver<TConfig>` class, and the available solution methods.

All solvers in AMGX inherit from the `Solver<TConfig>` base class ([include/solvers/solver.h:21-268]()), which defines the common interface for setup, solve iterations, convergence checking, and residual computation. The framework uses a factory pattern for solver instantiation and supports flexible composition where solvers can serve as preconditioners for other solvers.

Sources:
- [include/solvers/solver.h:21-268]()
- [src/solvers/solver.cu:26-109]()

## Solver Framework Architecture

### Solver Base Class

The `Solver<TConfig>` class ([include/solvers/solver.h:21-268]()) provides the abstract interface that all concrete solvers implement. Key components include:

**Core Data Members:**
- `Operator<TConfig> *m_A` - The matrix operator
- `Vector<TConfig> *m_r` - Residual vector
- `Convergence<TConfig> *m_convergence` - Convergence checking object
- `Scaler<TConfig> *m_Scaler` - Optional matrix/vector scaler
- `AMG_Config *m_cfg` - Configuration object
- `PODVector_h m_nrm`, `m_nrm_ini` - Current and initial norm values
- `std::vector<PODVector_h> m_res_history` - Residual history storage

**Key Parameters:**
- `m_max_iters` - Maximum iterations allowed
- `m_norm_type` - Norm type (L1, L2, or Max)
- `m_monitor_residual` - Whether to compute residuals
- `m_monitor_convergence` - Whether to check convergence
- `m_store_res_history` - Whether to store residual history

Sources:
- [include/solvers/solver.h:191-267]()
- [src/solvers/solver.cu:26-109]()

### Solver Class Hierarchy

```mermaid
graph TD
    SolverBase["Solver&lt;TConfig&gt;<br/>Base class<br/>[solver.h:21-268]"]
    
    subgraph "Krylov Solvers"
        PCG["PCG_Solver<br/>Preconditioned<br/>Conjugate Gradient"]
        GMRES["GMRES_Solver<br/>Generalized Minimal<br/>Residual"]
        FGMRES["FGMRES_Solver<br/>Flexible GMRES"]
        BiCGStab["BiCGStab_Solver<br/>BiConjugate Gradient<br/>Stabilized"]
    end
    
    subgraph "Smoothers/Relaxation"
        BlockJacobi["BlockJacobi_Solver<br/>[block_jacobi_solver.cu]"]
        GaussSeidel["GaussSeidel_Solver<br/>Multicolor GS"]
        DILU["DILU_Solver<br/>Incomplete LU"]
    end
    
    subgraph "Direct Methods"
        DenseLU["DenseLUSolver<br/>[dense_lu_solver.cu]"]
    end
    
    subgraph "Multigrid"
        AMG["AMG<br/>Algebraic Multigrid<br/>[amg.cu]"]
    end
    
    SolverBase --> PCG
    SolverBase --> GMRES
    SolverBase --> FGMRES
    SolverBase --> BiCGStab
    SolverBase --> BlockJacobi
    SolverBase --> GaussSeidel
    SolverBase --> DILU
    SolverBase --> DenseLU
    SolverBase --> AMG
    
    subgraph "Supporting Components"
        ConvergenceObj["Convergence&lt;TConfig&gt;<br/>Criteria checking"]
        ScalerObj["Scaler&lt;TConfig&gt;<br/>Matrix/vector scaling"]
        ConfigObj["AMG_Config<br/>Parameter storage"]
    end
    
    SolverBase --> ConvergenceObj
    SolverBase --> ScalerObj
    SolverBase --> ConfigObj
```

Sources:
- [include/solvers/solver.h:21-268]()
- [src/solvers/block_jacobi_solver.cu:1-1295]()

### SolverFactory Pattern

Solvers are instantiated through the `SolverFactory<TConfig>` pattern ([include/solvers/solver.h:270-308]()), which maintains a registry of available solver types. The factory:

1. **Registration**: Each solver type registers itself with `SolverFactory::registerFactory()`
2. **Allocation**: `SolverFactory::allocate()` creates solver instances based on configuration strings
3. **Nested Solvers**: The factory prevents infinite recursion when solvers use themselves as preconditioners with the same scope

```mermaid
flowchart TD
    Config["AMG_Config<br/>JSON configuration"]
    Factory["SolverFactory::allocate()<br/>[solver.cu:1099-1132]"]
    Registry["Static factory registry<br/>map&lt;string, SolverFactory*&gt;"]
    
    Config -->|"solver name"| Factory
    Factory -->|"lookup"| Registry
    Registry -->|"factory instance"| Factory
    Factory -->|"create()"| ConcreteFactory["Concrete SolverFactory<br/>e.g., PCG_Factory"]
    ConcreteFactory -->|"new"| SolverInstance["Solver instance<br/>e.g., PCG_Solver"]
    
    SolverInstance -->|"preconditioner parameter"| Factory2["Recursive allocate()<br/>for preconditioner"]
    Factory2 -->|"create nested solver"| Preconditioner["Preconditioner Solver<br/>e.g., AMG"]
```

Sources:
- [include/solvers/solver.h:270-308]()
- [src/solvers/solver.cu:1037-1132]()

## Solver Lifecycle

### Setup Phase

The `Solver::setup()` method ([src/solvers/solver.cu:332-553]()) initializes the solver for a given matrix:

```mermaid
flowchart TD
    SetupStart["setup(Operator&lt;TConfig&gt; &A, bool reuse)"]
    
    CheckMatrix["Check matrix initialized<br/>[solver.cu:391-393]"]
    ColorMatrix["Color matrix if needed<br/>setupMatrix() or colorMatrix()<br/>[solver.cu:415-429]"]
    SetA["Set m_A = &A<br/>[solver.cu:433]"]
    
    ApplyScaling["If scaling != NONE:<br/>m_Scaler->setup()<br/>m_Scaler->scaleMatrix()<br/>[solver.cu:454-469]"]
    
    SolverSetup["Call solver_setup()<br/>Virtual method<br/>[solver.cu:472]"]
    
    UnscaleMatrix["Unscale matrix<br/>[solver.cu:474-477]"]
    
    AllocateR["Allocate residual vector m_r<br/>if monitor_residual<br/>[solver.cu:481-503]"]
    
    AllocateNorms["Resize norm vectors<br/>m_nrm, m_nrm_ini<br/>[solver.cu:506-511]"]
    
    SetupStart --> CheckMatrix
    CheckMatrix --> ColorMatrix
    ColorMatrix --> SetA
    SetA --> ApplyScaling
    ApplyScaling --> SolverSetup
    SolverSetup --> UnscaleMatrix
    UnscaleMatrix --> AllocateR
    AllocateR --> AllocateNorms
```

**Key Steps:**
1. **Matrix Validation**: Check that matrix is initialized ([solver.cu:391-393]())
2. **Matrix Coloring**: Apply coloring if solver requires it ([solver.cu:415-429]())
3. **Scaling**: Optionally scale the matrix for better conditioning ([solver.cu:454-469]())
4. **Solver-Specific Setup**: Call virtual `solver_setup()` method ([solver.cu:472]())
5. **Vector Allocation**: Allocate residual and norm vectors ([solver.cu:481-511]())

Sources:
- [src/solvers/solver.cu:332-553]()

### Solve Phase

The `Solver::solve()` method ([src/solvers/solver.cu:586-970]()) executes the solver iterations:

```mermaid
flowchart TD
    SolveStart["solve(VVector &b, VVector &x, bool xIsZero)"]
    
    Validate["Check solver is setup<br/>[solver.cu:592-596]"]
    
    Scaling["Apply scaling to b, x<br/>if m_Scaler != NULL<br/>[solver.cu:668-675]"]
    
    InitialResidual["Compute initial residual:<br/>if xIsZero: r = b<br/>else: r = b - Ax<br/>[solver.cu:681-691]"]
    
    InitialNorm["Compute initial norm<br/>m_nrm_ini = ||r||<br/>[solver.cu:694-722]"]
    
    InitSolver["Call solve_init(b, x, xIsZero)<br/>Virtual method<br/>[solver.cu:795]"]
    
    IterLoop["For m_curr_iter = 0 to m_max_iters"]
    
    SolveIter["solve_iteration(b, x, xIsZero)<br/>Returns AMGX_STATUS<br/>[solver.cu:806]"]
    
    CheckConv["Check convergence<br/>isDone(conv_stat)<br/>[solver.cu:810]"]
    
    StoreRes["Store residual in m_res_history<br/>if m_store_res_history<br/>[solver.cu:840-844]"]
    
    Finalize["Call solve_finalize(b, x)<br/>[solver.cu:851-854]"]
    
    Unscale["Unscale solution x<br/>if m_Scaler != NULL<br/>[solver.cu:856-863]"]
    
    SolveStart --> Validate
    Validate --> Scaling
    Scaling --> InitialResidual
    InitialResidual --> InitialNorm
    InitialNorm --> InitSolver
    InitSolver --> IterLoop
    IterLoop --> SolveIter
    SolveIter --> CheckConv
    CheckConv -->|"Not converged"| StoreRes
    StoreRes --> IterLoop
    CheckConv -->|"Converged"| Finalize
    Finalize --> Unscale
```

**Key Steps:**
1. **Validation**: Verify setup was called ([solver.cu:592-596]())
2. **Initial Residual**: Compute `r = b - Ax` or `r = b` if `xIsZero` ([solver.cu:681-691]())
3. **Initial Norm**: Compute and store `m_nrm_ini` ([solver.cu:711-714]())
4. **Initialization**: Call solver-specific `solve_init()` ([solver.cu:795]())
5. **Iteration Loop**: Repeatedly call `solve_iteration()` until convergence ([solver.cu:803-845]())
6. **Finalization**: Call `solve_finalize()` to clean up ([solver.cu:851-854]())

Sources:
- [src/solvers/solver.cu:586-970]()

## Solver Hierarchy and Composition

AMGX uses a sophisticated solver composition system allowing solvers to be nested as preconditioners for other solvers. This enables the creation of powerful solution strategies tailored to specific problem characteristics.

```mermaid
graph TD
    subgraph "Solver Composition Example"
        Main["Main Solver: PCG"]
        Prec["Preconditioner: AMG"]
        Smooth["Smoother: Block Jacobi"]
        CoarseSolve["Coarse Solver: LU"]
        
        Main --> Prec
        Prec --> Smooth
        Prec --> CoarseSolve
    end

    subgraph "Configuration Parameters"
        MainParams["Main Parameters:
        - max_iters
        - tolerance
        - convergence criteria
        - norm type"]
        
        PrecParams["Preconditioner Parameters:
        - cycle type (V/W/F)
        - pre/post sweeps
        - interpolator type
        - max_levels"]
        
        SmoothParams["Smoother Parameters:
        - damping factor
        - iterations"]
        
        Main --> MainParams
        Prec --> PrecParams
        Smooth --> SmoothParams
    end
```

Sources:
- [src/configs/PCG_V.json:3-34]()
- [src/solvers/gmres_solver.cu:25-48]()
- [src/solvers/fgmres_solver.cu:214-250]()

## Krylov Subspace Methods

AMGX implements several Krylov subspace methods, which are iterative techniques for solving large sparse linear systems. These methods are particularly effective when combined with appropriate preconditioners.

### PCG (Preconditioned Conjugate Gradient)

PCG is an efficient Krylov subspace method for symmetric positive definite matrices. In AMGX, it can be configured with various convergence criteria and preconditioners, typically AMG.

### GMRES (Generalized Minimal RESidual)

GMRES is designed for non-symmetric systems and is implemented with restart capabilities to manage memory usage. The implementation includes:

- Modified Gram-Schmidt orthogonalization
- Givens rotations for stability
- Configurable restart parameter
- Support for flexible preconditioning

```mermaid
flowchart TD
    Init["Initialize:
    - Compute initial residual r₀
    - Set v₁ = r₀/‖r₀‖"]
    
    Loop["For j = 1 to m:"]
    
    PreApply["Apply preconditioner: 
    Solve M z_j = v_j"]
    
    MatVec["Matrix-vector product:
    w = A·z_j"]
    
    Arnoldi["Arnoldi process:
    - Orthogonalize w against v₁,...,vⱼ
    - Get v_{j+1} and update H matrix"]
    
    UpdateSol["Update solution:
    - Apply plane rotations to H
    - Solve least squares problem
    - Compute solution update"]
    
    Check["Check convergence"]
    
    Restart["Restart if needed"]
    
    Init --> Loop
    Loop --> PreApply
    PreApply --> MatVec
    MatVec --> Arnoldi
    Arnoldi --> Check
    Check -->|Not converged| UpdateSol
    UpdateSol --> Restart
    Restart --> Loop
    Check -->|Converged| End[Return solution]
```

Sources:
- [src/solvers/gmres_solver.cu:151-210]()
- [src/solvers/gmres_solver.cu:270-392]()

### FGMRES (Flexible GMRES)

FGMRES extends GMRES to allow for varying preconditioners in each iteration. This is particularly useful when using adaptive or approximate preconditioning techniques.

Key features of the FGMRES implementation:

- Dynamic Krylov subspace management
- Memory-adaptive implementation
- Fallback to DQGMRES when memory is limited
- Support for different convergence criteria

Sources:
- [src/solvers/fgmres_solver.cu:17-180]()
- [src/solvers/fgmres_solver.cu:407-568]()

## Direct Solvers

### Dense LU Solver

AMGX includes a direct solver based on LU factorization for dense matrices, which is particularly useful for small to medium-sized problems or as a coarse grid solver in multigrid methods.

The Dense LU solver:
- Uses cuSOLVER for GPU-accelerated factorization
- Handles both single and multi-GPU configurations
- Supports block matrices with various block sizes
- Can be used for both exact and inexact solutions

```mermaid
flowchart TD
    Setup["Setup Phase:
    - Convert sparse matrix to dense format
    - Allocate memory for factorization
    - Perform LU decomposition"]
    
    Solve["Solve Phase:
    - For distributed matrices:
      - Gather RHS from all processors
      - Solve using factorized matrix
      - Distribute solution
    - For local matrices:
      - Adjust RHS for boundary conditions
      - Solve using factorized matrix"]
    
    Setup --> Solve
    
    subgraph "Dense LU Internal Process"
        CSR2Dense["Convert CSR to dense matrix"]
        Allocate["Allocate pivoting arrays"]
        Factor["Call cuSolverDn for LU factorization"]
        
        CSR2Dense --> Allocate
        Allocate --> Factor
    end
    
    Setup --> CSR2Dense
```

Sources:
- [src/solvers/dense_lu_solver.cu:453-889]()
- [src/solvers/dense_lu_solver.cu:485-508]()
- [src/solvers/dense_lu_solver.cu:513-568]()

## Residual Computation and Convergence

### Residual Computation

The `Solver` class provides methods for computing residuals ([src/solvers/solver.cu:184-206]()):

**Method**: `compute_residual(const VVector &b, VVector &x)`
- Computes `r = b - Ax` using the stored `m_r` vector
- Uses `m_A->apply(x, *m_r)` for matrix-vector product
- Performs AXPBY operation: `r = 1.0*b - 1.0*(Ax)`

**Method**: `compute_residual(const VVector &b, VVector &x, VVector &r)`
- Same as above but stores result in provided vector `r`

Sources:
- [src/solvers/solver.cu:184-206]()

### Norm Computation

The `Solver::compute_norm()` method ([src/solvers/solver.cu:209-214]()) computes the norm of the residual:

- Uses the `get_norm()` utility function
- Supports scalar norm (single value) or block norm (one value per block row)
- Applies norm factor for L1 normalization if configured
- Supports L1, L2, and Max norms via `m_norm_type`

Sources:
- [src/solvers/solver.cu:209-222]()

### Convergence Checking

The `Solver::converged()` methods ([src/solvers/solver.cu:264-296]()) check convergence using the `Convergence<TConfig>` object:

**Key Method**: `converged(const VVector &b, VVector &x)`
1. Computes residual if `m_monitor_residual` is true
2. Computes norm if `m_monitor_convergence` is true
3. Calls `m_convergence->convergence_update_and_check(m_nrm, m_nrm_ini)`
4. Returns `AMGX_STATUS` (CONVERGED, NOT_CONVERGED, or DIVERGED)

**Convergence Criteria Types:**

| Type | Description | Check |
|------|-------------|-------|
| `ABSOLUTE` | Absolute tolerance | `‖r‖ < tolerance` |
| `RELATIVE_INI` | Relative to initial | `‖r‖/‖r₀‖ < tolerance` |
| `RELATIVE_MAX_CORE` | Relative to max | `‖r‖/max(‖r₀‖, ‖b‖) < tolerance` |
| `COMBINED` | Combined criteria | Both relative and absolute |

Sources:
- [src/solvers/solver.cu:264-296]()
- [include/solvers/solver.h:236-239]()

## Solver Configuration

AMGX solvers are configured through JSON configuration files that specify the solver type, preconditioners, convergence criteria, and other parameters.

### Configuration Parameters

Common parameters read by the `Solver` constructor ([src/solvers/solver.cu:26-109]()):

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `max_iters` | int | Maximum iterations | Required |
| `tolerance` | double | Convergence tolerance | Via Convergence object |
| `norm` | NormType | Norm type (L1, L2, MAX) | Required |
| `use_scalar_norm` | int | Use single scalar vs block norm | Required |
| `convergence` | string | Convergence criterion type | Required |
| `monitor_residual` | int | Compute residuals each iteration | 0 |
| `store_res_history` | int | Store residual history | 0 |
| `obtain_timings` | int | Measure setup/solve times | 0 |
| `scaling` | string | Matrix scaling type | "NONE" |
| `print_solve_stats` | int | Print iteration statistics | 0 |
| `print_grid_stats` | int | Print grid hierarchy info | 0 |
| `solver_verbose` | int | Verbose parameter output | 0 |

Sources:
- [src/solvers/solver.cu:33-80]()
- [include/solvers/solver.h:221-255]()

### Example Configuration

PCG with AMG preconditioner from [src/configs/PCG_V.json:1-35]():

```json
{
    "config_version": 2, 
    "solver": {
        "solver": "PCG", 
        "preconditioner": {
            "solver": "AMG", 
            "smoother": "BLOCK_JACOBI",
            "presweeps": 1, 
            "postsweeps": 1,
            "max_iters": 1, 
            "cycle": "V"
        }, 
        "max_iters": 100, 
        "tolerance": 1e-06, 
        "convergence": "RELATIVE_INI", 
        "norm": "L2"
    }
}
```

Sources:
- [src/solvers/solver.cu:26-109]()

## Matrix Scaling

The `Solver` class supports optional matrix and vector scaling to improve conditioning ([src/solvers/solver.cu:454-477]()):

**Scaling Workflow:**
1. During `setup()`: Scale the matrix using `m_Scaler->scaleMatrix(A, SCALE)`
2. Perform solver setup on the scaled matrix
3. Unscale the matrix before returning from `setup()`
4. During `solve()`: Scale matrix and RHS, unscale initial guess
5. After solving: Scale solution, unscale RHS and matrix

**Note**: Current scaling implementation is conservative to ensure correct convergence checks. Custom kernels could optimize this by scaling/unscaling on-the-fly.

Sources:
- [src/solvers/solver.cu:435-477]()
- [src/solvers/solver.cu:668-675]()
- [src/solvers/solver.cu:856-863]()

## Solver Timing and Profiling

When `obtain_timings=1`, the `Solver` class records detailed timing information using CUDA events ([src/solvers/solver.cu:88-109]()):

**Timing Events:**
- `m_setup_start`, `m_setup_stop` - Setup phase timing
- `m_solve_start`, `m_solve_stop` - Overall solve timing
- `m_iter_start`, `m_iter_stop` - Per-iteration timing

**Timing Output** ([src/solvers/solver.cu:1023-1031]()):
- Total time (setup + solve)
- Setup time in seconds
- Solve time in seconds  
- Average time per iteration

Sources:
- [src/solvers/solver.cu:88-109]()
- [src/solvers/solver.cu:1023-1031]()

## Solver-Preconditioner Relationships

One of AMGX's key strengths is the flexible composition of solvers and preconditioners. The following diagram shows common solver-preconditioner combinations:

```mermaid
graph TD
    subgraph "Solver-Preconditioner Combinations"
        PCG_AMG["PCG + AMG"]
        GMRES_AMG["GMRES + AMG"]
        FGMRES_Multi["FGMRES + Multi-level"]
        PCG_Jacobi["PCG + Jacobi"]
        AMG_GS["AMG + Gauss-Seidel"]
        BiCGStab_AMG["BiCGStab + AMG"]
    end
    
    subgraph "Common Use Cases"
        SPD["Symmetric Positive Definite"] --> PCG_AMG
        NonSymmetric["Non-symmetric Systems"] --> GMRES_AMG
        NonSymmetric --> BiCGStab_AMG
        Complex["Complex Systems"] --> FGMRES_Multi
        Simple["Simple Problems"] --> PCG_Jacobi
        HighPerformance["High Performance"] --> AMG_GS
    end
```

Sources:
- [src/configs/PCG_V.json:3-34]()
- [src/solvers/gmres_solver.cu:25-48]()
- [src/solvers/fgmres_solver.cu:214-250]()

## Summary

The AMGX solver framework provides a comprehensive suite of iterative and direct solvers for large sparse linear systems, with a focus on GPU acceleration. The modular design allows for flexible composition of solvers and preconditioners to address a wide range of problem types and sizes.

Key features include:
- Krylov subspace methods (PCG, GMRES, FGMRES)
- Direct solvers (Dense LU)
- Multiple convergence criteria options
- Flexible preconditioner integration
- JSON-based configuration system

For specific solver implementations, see the subpages:
- [Algebraic Multigrid (AMG)](#3.1)
- [Krylov Solvers](#3.2)
- [Other Solvers](#3.3)

---

