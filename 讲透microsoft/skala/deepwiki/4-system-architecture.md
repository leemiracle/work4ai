<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/skala · page 4 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [third_party/gauxc/attic/include/gauxc/new_xc_integrator/impl.hpp](third_party/gauxc/attic/include/gauxc/new_xc_integrator/impl.hpp)
- [third_party/gauxc/attic/include/gauxc/new_xc_integrator/replicated/impl.hpp](third_party/gauxc/attic/include/gauxc/new_xc_integrator/replicated/impl.hpp)
- [third_party/gauxc/attic/include/gauxc/new_xc_integrator/replicated/replicated_xc_integrator_impl.hpp](third_party/gauxc/attic/include/gauxc/new_xc_integrator/replicated/replicated_xc_integrator_impl.hpp)
- [third_party/gauxc/attic/include/gauxc/new_xc_integrator/replicated_xc_integrator.hpp](third_party/gauxc/attic/include/gauxc/new_xc_integrator/replicated_xc_integrator.hpp)
- [third_party/gauxc/attic/include/gauxc/new_xc_integrator/xc_integrator_impl.hpp](third_party/gauxc/attic/include/gauxc/new_xc_integrator/xc_integrator_impl.hpp)
- [third_party/gauxc/attic/include/gauxc/xc_integrator/impl.hpp](third_party/gauxc/attic/include/gauxc/xc_integrator/impl.hpp)
- [third_party/gauxc/attic/include/gauxc/xc_integrator/xc_integrator_impl.hpp](third_party/gauxc/attic/include/gauxc/xc_integrator/xc_integrator_impl.hpp)
- [third_party/gauxc/attic/src/new_integrator/replicated_xc_integrator_impl.cxx](third_party/gauxc/attic/src/new_integrator/replicated_xc_integrator_impl.cxx)
- [third_party/gauxc/include/gauxc/xc_integrator.hpp](third_party/gauxc/include/gauxc/xc_integrator.hpp)
- [third_party/gauxc/include/gauxc/xc_integrator/impl.hpp](third_party/gauxc/include/gauxc/xc_integrator/impl.hpp)
- [third_party/gauxc/include/gauxc/xc_integrator/replicated/impl.hpp](third_party/gauxc/include/gauxc/xc_integrator/replicated/impl.hpp)
- [third_party/gauxc/include/gauxc/xc_integrator/replicated/replicated_xc_integrator_impl.hpp](third_party/gauxc/include/gauxc/xc_integrator/replicated/replicated_xc_integrator_impl.hpp)
- [third_party/gauxc/include/gauxc/xc_integrator/replicated_xc_integrator.hpp](third_party/gauxc/include/gauxc/xc_integrator/replicated_xc_integrator.hpp)
- [third_party/gauxc/src/xc_integrator/replicated/device/incore_replicated_xc_device_integrator_dd.hpp](third_party/gauxc/src/xc_integrator/replicated/device/incore_replicated_xc_device_integrator_dd.hpp)
- [third_party/gauxc/src/xc_integrator/replicated/host/reference_replicated_xc_host_integrator_dd_psi_potential.hpp](third_party/gauxc/src/xc_integrator/replicated/host/reference_replicated_xc_host_integrator_dd_psi_potential.hpp)
- [third_party/gauxc/src/xc_integrator/replicated/replicated_xc_integrator_impl.cxx](third_party/gauxc/src/xc_integrator/replicated/replicated_xc_integrator_impl.cxx)
- [third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_dd_psi.hpp](third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_dd_psi.hpp)
- [third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_dd_psi_potential.hpp](third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_dd_psi_potential.hpp)
- [third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc.hpp](third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc.hpp)
- [third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_grad.hpp](third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_grad.hpp)
- [third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_vxc.hpp](third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_vxc.hpp)
- [third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exx.hpp](third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exx.hpp)
- [third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_fxc_contraction.hpp](third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_fxc_contraction.hpp)
- [third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_integrate_den.hpp](third_party/gauxc/src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_integrate_den.hpp)

</details>



## Purpose and Scope

This page describes the overall architecture of GauXC, focusing on the organizational structure of components, design patterns, and data flow through the integration pipeline. It provides a conceptual framework for understanding how the major subsystems interact to perform XC integration.

For detailed information about specific components, see [Core Components](#4.1). For execution paths and runtime behavior, see [Execution Model: Host vs Device](#4.2). For task organization and data structures, see [Task System and Data Structures](#4.3). For the public API, see [XCIntegrator API](#3).

---

## Architectural Overview

GauXC employs a layered architecture with clear separation between interface, implementation, and execution:

```mermaid
graph TB
    subgraph "Public API Layer"
        XCI["XCIntegrator&lt;MatrixType&gt;<br/>Public template class"]
    end
    
    subgraph "Implementation Layer"
        XCII["XCIntegratorImpl&lt;MatrixType&gt;<br/>Abstract base"]
        RXCI["ReplicatedXCIntegrator&lt;MatrixType&gt;<br/>Replicated data implementation"]
    end
    
    subgraph "PIMPL Layer"
        RXCII["ReplicatedXCIntegratorImpl&lt;ValueType&gt;<br/>Type-erased implementation"]
        SBXCII["ShellBatchedReplicatedXCIntegratorImpl<br/>Shell batching strategy"]
        IRXCII["IncoreReplicatedXCIntegratorImpl<br/>Full in-core strategy"]
    end
    
    subgraph "Core Components"
        FUNC["functional_type<br/>XC Functional"]
        LB["LoadBalancer<br/>Task generation"]
        LWD["LocalWorkDriver<br/>Computation execution"]
        RD["ReductionDriver<br/>MPI aggregation"]
    end
    
    XCI -->|"owns via unique_ptr"| XCII
    XCII <|--|"inherits"| RXCI
    RXCI -->|"owns via unique_ptr"| RXCII
    RXCII <|--|"inherits"| SBXCII
    RXCII <|--|"inherits"| IRXCII
    
    RXCII -->|"shared_ptr"| FUNC
    RXCII -->|"shared_ptr"| LB
    RXCII -->|"unique_ptr"| LWD
    RXCII -->|"shared_ptr"| RD
    
    style XCI fill:#f9f9f9,stroke:#333,stroke-width:2px
    style RXCII fill:#f0f0f0,stroke:#333,stroke-width:2px
    style SBXCII fill:#e8e8e8,stroke:#333,stroke-width:1px
```

**Architecture Diagram: Class Hierarchy and Ownership Model**

The architecture uses three levels of indirection:
1. **Public API**: Template classes parameterized on `MatrixType`
2. **Implementation Bridge**: Type-preserving implementation classes
3. **PIMPL Core**: Type-erased (`ValueType` only) implementation holding execution components

Sources: [include/gauxc/xc_integrator.hpp:25-95](), [include/gauxc/xc_integrator/replicated_xc_integrator.hpp:24-76](), [include/gauxc/xc_integrator/replicated/replicated_xc_integrator_impl.hpp:20-204]()

---

## PIMPL Pattern

GauXC extensively uses the Pointer to Implementation (PIMPL) pattern to achieve binary stability and separate interface from implementation. This pattern appears at multiple levels:

### XCIntegrator PIMPL Structure

```mermaid
graph LR
    subgraph "Public Interface"
        XCI["XCIntegrator&lt;MatrixType&gt;"]
        XCI_PIMPL["unique_ptr&lt;XCIntegratorImpl&lt;MatrixType&gt;&gt;"]
    end
    
    subgraph "Implementation Polymorphism"
        XCII["XCIntegratorImpl&lt;MatrixType&gt;<br/>(abstract)"]
        RXCI["ReplicatedXCIntegrator&lt;MatrixType&gt;<br/>(concrete)"]
    end
    
    subgraph "Type Erasure Layer"
        RXCI_PIMPL["unique_ptr&lt;ReplicatedXCIntegratorImpl&lt;ValueType&gt;&gt;"]
        RXCII["ReplicatedXCIntegratorImpl&lt;ValueType&gt;<br/>(abstract)"]
    end
    
    subgraph "Concrete Implementations"
        SBXCII["ShellBatchedReplicatedXCIntegrator"]
        IRXCII["IncoreReplicatedXCIntegrator"]
    end
    
    XCI -->|"owns"| XCI_PIMPL
    XCI_PIMPL -.->|"polymorphic"| XCII
    XCII <|-- RXCI
    
    RXCI -->|"owns"| RXCI_PIMPL
    RXCI_PIMPL -.->|"polymorphic"| RXCII
    RXCII <|-- SBXCII
    RXCII <|-- IRXCII
    
    style XCI fill:#f9f9f9,stroke:#333,stroke-width:2px
    style RXCII fill:#f0f0f0,stroke:#333,stroke-width:2px
```

**PIMPL Layering Diagram**

The double-PIMPL structure serves two purposes:
- **First PIMPL** (`XCIntegrator` → `XCIntegratorImpl`): Enables polymorphism over data distribution strategies (replicated vs distributed)
- **Second PIMPL** (`ReplicatedXCIntegrator` → `ReplicatedXCIntegratorImpl`): Erases `MatrixType`, leaving only `ValueType`, and enables selection of execution strategy (shell-batched vs incore)

All public methods on `XCIntegrator` follow this delegation pattern:
```cpp
// Public method in XCIntegrator
value_type eval_exc(const MatrixType& P, const IntegratorSettingsXC& settings) {
    if( not pimpl_ ) GAUXC_PIMPL_NOT_INITIALIZED();
    return pimpl_->eval_exc(P, settings);
}
```

Sources: [include/gauxc/xc_integrator.hpp:44-48](), [include/gauxc/xc_integrator/replicated_xc_integrator.hpp:42-44](), [include/gauxc/xc_integrator/impl.hpp:16-154](), [include/gauxc/xc_integrator/replicated/impl.hpp:19-281]()

---

## Replicated Data Model

The `ReplicatedXCIntegrator` class implements a **replicated data model** where all input data (density matrices, molecular geometry, basis set) is replicated across all MPI ranks. This contrasts with distributed models where data is partitioned.

### Key Characteristics

| Aspect | Replicated Model Behavior |
|--------|---------------------------|
| **Input Data** | Full density matrix `P` present on every rank |
| **Task Distribution** | Each rank processes a subset of grid points/tasks |
| **Local Computation** | Each rank computes partial `EXC` and `VXC` contributions |
| **Result Aggregation** | MPI Allreduce sums contributions from all ranks |
| **Memory Overhead** | O(nbf²) per rank (duplicated) |
| **Communication** | Single allreduce at end; no intermediate communication |

The replicated model simplifies implementation because each rank has all information needed to evaluate any task. Work distribution is performed by the `LoadBalancer`, which assigns different grid point batches to different ranks.

### Data Flow in Replicated Model

```mermaid
flowchart TB
    subgraph "Input (Replicated on All Ranks)"
        P["Density Matrix P<br/>nbf × nbf"]
        MOL["Molecule Geometry"]
        BASIS["Basis Set"]
    end
    
    subgraph "Rank 0 Local Work"
        LB0["LoadBalancer<br/>Tasks 0-N/4"]
        LWD0["LocalWorkDriver"]
        PARTIAL0["Partial EXC₀, VXC₀"]
    end
    
    subgraph "Rank 1 Local Work"
        LB1["LoadBalancer<br/>Tasks N/4-N/2"]
        LWD1["LocalWorkDriver"]
        PARTIAL1["Partial EXC₁, VXC₁"]
    end
    
    subgraph "Rank 2 Local Work"
        LB2["LoadBalancer<br/>Tasks N/2-3N/4"]
        LWD2["LocalWorkDriver"]
        PARTIAL2["Partial EXC₂, VXC₂"]
    end
    
    subgraph "Rank 3 Local Work"
        LB3["LoadBalancer<br/>Tasks 3N/4-N"]
        LWD3["LocalWorkDriver"]
        PARTIAL3["Partial EXC₃, VXC₃"]
    end
    
    subgraph "Reduction"
        RD["ReductionDriver<br/>MPI_Allreduce"]
        FINAL["Final EXC, VXC<br/>(Identical on All Ranks)"]
    end
    
    P --> LB0
    P --> LB1
    P --> LB2
    P --> LB3
    MOL --> LB0
    MOL --> LB1
    MOL --> LB2
    MOL --> LB3
    BASIS --> LB0
    BASIS --> LB1
    BASIS --> LB2
    BASIS --> LB3
    
    LB0 --> LWD0 --> PARTIAL0
    LB1 --> LWD1 --> PARTIAL1
    LB2 --> LWD2 --> PARTIAL2
    LB3 --> LWD3 --> PARTIAL3
    
    PARTIAL0 --> RD
    PARTIAL1 --> RD
    PARTIAL2 --> RD
    PARTIAL3 --> RD
    RD --> FINAL
    
    style P fill:#f9f9f9,stroke:#333,stroke-width:2px
    style RD fill:#f0f0f0,stroke:#333,stroke-width:2px
    style FINAL fill:#e8e8e8,stroke:#333,stroke-width:2px
```

**Replicated Data Flow Across MPI Ranks**

Sources: [include/gauxc/xc_integrator/replicated_xc_integrator.hpp:19-23](), [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_vxc.hpp:104-115]()

---

## Core Components and Their Roles

The `ReplicatedXCIntegratorImpl` base class holds references to four core components that orchestrate the integration process:

```mermaid
graph TB
    subgraph "ReplicatedXCIntegratorImpl"
        FUNC["shared_ptr&lt;functional_type&gt; func_<br/>XC functional definition"]
        LB["shared_ptr&lt;LoadBalancer&gt; load_balancer_<br/>Task generation and distribution"]
        LWD["unique_ptr&lt;LocalWorkDriver&gt; local_work_driver_<br/>Execute computation on tasks"]
        RD["shared_ptr&lt;ReductionDriver&gt; reduction_driver_<br/>Aggregate results across ranks"]
    end
    
    subgraph "Component Responsibilities"
        FUNC_ROLE["• Define functional type LDA/GGA/MGGA<br/>• Provide ExchCXX interface<br/>• Compute εxc and vxc from ρ"]
        LB_ROLE["• Generate XCTask objects<br/>• Partition grid points to ranks<br/>• Maintain molecular data<br/>• Screen basis functions"]
        LWD_ROLE["• Evaluate basis functions<br/>• Compute density on grid<br/>• Integrate XC contributions<br/>• Host or Device execution"]
        RD_ROLE["• MPI_Allreduce operations<br/>• Sum partial integrals<br/>• Host or Device memory"]
    end
    
    FUNC -.->|"defines"| FUNC_ROLE
    LB -.->|"performs"| LB_ROLE
    LWD -.->|"executes"| LWD_ROLE
    RD -.->|"aggregates"| RD_ROLE
    
    style FUNC fill:#f9f9f9,stroke:#333,stroke-width:1px
    style LB fill:#f0f0f0,stroke:#333,stroke-width:1px
    style LWD fill:#e8e8e8,stroke:#333,stroke-width:1px
    style RD fill:#e0e0e0,stroke:#333,stroke-width:1px
```

**Core Component Responsibilities**

### Ownership and Lifetime

- **`func_`**: Shared pointer allows multiple integrators to share the same functional definition
- **`load_balancer_`**: Shared pointer enables sharing of expensive load balancing state
- **`local_work_driver_`**: Unique pointer indicates exclusive ownership; can be temporarily transferred to incore integrators
- **`reduction_driver_`**: Shared pointer allows sharing of MPI communicator state

The `LocalWorkDriver` is unique among these components because ownership can be temporarily released during execution via `release_local_work_driver()` and later restored. This pattern appears in shell-batched execution where the driver is passed to incore integrator instances for task batch execution.

Sources: [include/gauxc/xc_integrator/replicated/replicated_xc_integrator_impl.hpp:30-34](), [include/gauxc/xc_integrator/replicated/replicated_xc_integrator_impl.hpp:196-198]()

For detailed descriptions of each component's implementation, see [Core Components](#4.1).

---

## Integration Methods and Spin Treatments

`ReplicatedXCIntegratorImpl` defines a comprehensive set of virtual methods for different integration tasks and spin treatments:

### Integration Method Categories

| Method Family | Purpose | Variants |
|---------------|---------|----------|
| `integrate_den_` | Compute electron count | RKS only |
| `eval_exc_` | Compute XC energy only | RKS, UKS, GKS |
| `eval_exc_vxc_` | Compute XC energy and potential | RKS, UKS, GKS |
| `eval_exc_grad_` | Compute XC energy gradient | RKS, UKS |
| `eval_exx_` | Compute exact exchange | RKS only |
| `eval_fxc_contraction_` | Compute XC kernel contraction | RKS, UKS |
| `eval_dd_psi_` | Compute spherical harmonic projection | Generic |
| `eval_dd_psi_potential_` | Compute potential from projection | Generic |

### Spin Treatment Signatures

```mermaid
graph TB
    subgraph "Restricted Kohn-Sham (RKS)"
        RKS_IN["P<br/>Single density matrix"]
        RKS_OUT["VXC<br/>Single potential matrix"]
    end
    
    subgraph "Unrestricted Kohn-Sham (UKS)"
        UKS_IN["Ps, Pz<br/>Spin-summed and spin-difference"]
        UKS_OUT["VXCs, VXCz<br/>Spin-summed and spin-difference"]
    end
    
    subgraph "Generalized Kohn-Sham (GKS)"
        GKS_IN["Ps, Pz, Py, Px<br/>Four-component density"]
        GKS_OUT["VXCs, VXCz, VXCy, VXCx<br/>Four-component potential"]
    end
    
    RKS_IN --> EVAL["eval_exc_vxc_"]
    UKS_IN --> EVAL
    GKS_IN --> EVAL
    
    EVAL --> RKS_OUT
    EVAL --> UKS_OUT
    EVAL --> GKS_OUT
    
    style RKS_IN fill:#f9f9f9,stroke:#333,stroke-width:1px
    style UKS_IN fill:#f0f0f0,stroke:#333,stroke-width:1px
    style GKS_IN fill:#e8e8e8,stroke:#333,stroke-width:1px
```

**Spin Treatment Input/Output Structure**

Each `eval_exc_vxc_` overload has a corresponding non-virtual public wrapper that validates inputs and delegates to the virtual implementation. For example:

```cpp
// Public wrapper (non-virtual)
void eval_exc_vxc(int64_t m, int64_t n, const value_type* P,
                  int64_t ldp, value_type* VXC, int64_t ldvxc,
                  value_type* EXC, const IntegratorSettingsXC& ks_settings);

// Virtual implementation (pure virtual in base)
virtual void eval_exc_vxc_(int64_t m, int64_t n, const value_type* P,
                           int64_t ldp, value_type* VXC, int64_t ldvxc,
                           value_type* EXC, const IntegratorSettingsXC& ks_settings) = 0;
```

Sources: [include/gauxc/xc_integrator/replicated/replicated_xc_integrator_impl.hpp:39-106](), [src/xc_integrator/replicated/replicated_xc_integrator_impl.cxx:67-135]()

---

## Shell-Batched Execution Strategy

`ShellBatchedReplicatedXCIntegrator` implements a sophisticated batching strategy that groups tasks based on their union of shell lists to improve data locality and reduce memory overhead.

### Shell Batching Architecture

```mermaid
graph TB
    subgraph "Task Generation Phase"
        TASKS["XCTask Collection<br/>From LoadBalancer"]
        THRESHOLD["nbf_threshold = 8000"]
        GEN["generate_incore_task()<br/>Groups tasks into batches"]
    end
    
    subgraph "Task Batch Structure"
        BATCH["incore_task_data"]
        BATCH_BEGIN["task_begin iterator"]
        BATCH_END["task_end iterator"]
        UNION_LIST["union_shell_list<br/>Combined shell list"]
    end
    
    subgraph "Subbasis Extraction"
        FULL_BASIS["Full Basis Set<br/>nbf functions"]
        SUB_BASIS["Basis Subset<br/>nbe functions"]
        SUBMAT_MAP["submat_map<br/>Index translation"]
    end
    
    subgraph "Submatrix Operations"
        FULL_P["Full Density P<br/>nbf × nbf"]
        SUB_P["Subdensity Ps<br/>nbe × nbe"]
        SUB_VXC["Subpotential VXCs<br/>nbe × nbe"]
        FULL_VXC["Full Potential VXC<br/>nbf × nbf"]
    end
    
    subgraph "Execution"
        INCORE["IncoreIntegrator<br/>Process batch"]
        DEVICE_DATA["XCDeviceData<br/>(if GPU enabled)"]
    end
    
    TASKS --> GEN
    THRESHOLD --> GEN
    GEN --> BATCH
    
    BATCH --> BATCH_BEGIN
    BATCH --> BATCH_END
    BATCH --> UNION_LIST
    
    UNION_LIST --> SUB_BASIS
    FULL_BASIS --> SUB_BASIS
    SUB_BASIS --> SUBMAT_MAP
    
    FULL_P -->|"submat_set()"| SUB_P
    SUBMAT_MAP -->|"guides"| SUB_P
    
    SUB_P --> INCORE
    SUB_BASIS --> INCORE
    BATCH_BEGIN --> INCORE
    BATCH_END --> INCORE
    DEVICE_DATA -.->|"if GPU"| INCORE
    
    INCORE --> SUB_VXC
    SUB_VXC -->|"inc_by_submat()"| FULL_VXC
    SUBMAT_MAP -->|"guides"| FULL_VXC
    
    style BATCH fill:#f9f9f9,stroke:#333,stroke-width:2px
    style INCORE fill:#f0f0f0,stroke:#333,stroke-width:2px
    style SUBMAT_MAP fill:#e8e8e8,stroke:#333,stroke-width:2px
```

**Shell-Batched Execution Flow**

### Batching Algorithm

The `generate_incore_task()` function groups consecutive tasks until the union of their shell lists exceeds `nbf_threshold`:

1. Start with empty `union_shell_list`
2. For each task, compute union with current shell list
3. If union size ≤ threshold, add task to batch
4. If union size > threshold, finalize current batch and start new one

This strategy ensures that:
- Each batch operates on a manageable subbasis (nbe ≤ threshold)
- Memory allocations for subdensities and subpotentials remain bounded
- Multiple tasks can be processed with the same subbasis extraction

### Asynchronous Execution

Shell batches are executed asynchronously using a producer-consumer pattern:

```cpp
std::queue<incore_task_data> incore_task_data_queue;
std::future<void> task_future;

// Producer: Generate batches
while(task_it != task_end) {
    incore_task_data_queue.emplace(generate_incore_task(...));
    task_it = incore_task_data_queue.back().task_end;
    
    // Consumer: Execute batches asynchronously
    if(not task_future.valid()) {
        task_future = std::async(std::launch::async, execute_incore_task);
    } else if(task_future.wait_for(5ms) == std::future_status::ready) {
        task_future.get();
        task_future = std::async(std::launch::async, execute_incore_task);
    }
}
```

This overlaps batch generation with batch execution, improving GPU utilization.

Sources: [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_vxc.hpp:230-270](), [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_vxc.hpp:274-439]()

For details on task data structures, see [Task System and Data Structures](#4.3). For details on submatrix operations, see [Submatrix Operations](#5.2).

---

## Method Delegation Pattern

All integration methods follow a consistent delegation pattern from public API through the PIMPL layers to concrete implementations:

### Delegation Chain for `eval_exc_vxc`

```mermaid
flowchart LR
    subgraph "Layer 1: Public API"
        L1_PUB["XCIntegrator::eval_exc_vxc<br/>MatrixType& P"]
    end
    
    subgraph "Layer 2: Impl Bridge"
        L2_PRIV["XCIntegratorImpl::eval_exc_vxc_<br/>MatrixType& P"]
        L2_CONCRETE["ReplicatedXCIntegrator::eval_exc_vxc_<br/>MatrixType& P"]
    end
    
    subgraph "Layer 3: PIMPL Core"
        L3_PUB["ReplicatedXCIntegratorImpl::eval_exc_vxc<br/>value_type* P, ldp"]
        L3_PRIV["ReplicatedXCIntegratorImpl::eval_exc_vxc_<br/>value_type* P, ldp"]
    end
    
    subgraph "Layer 4: Concrete Strategy"
        L4_IMPL["ShellBatchedReplicatedXCIntegrator::eval_exc_vxc_<br/>value_type* P, ldp"]
        L4_WORK["ShellBatchedReplicatedXCIntegrator::exc_vxc_local_work_<br/>Executes task batches"]
    end
    
    L1_PUB -->|"pimpl_->eval_exc_vxc(P)"| L2_PRIV
    L2_PRIV -->|"virtual dispatch"| L2_CONCRETE
    L2_CONCRETE -->|"pimpl_->eval_exc_vxc(...)<br/>Extract P.data(), P.rows()"| L3_PUB
    L3_PUB -->|"eval_exc_vxc_(...)<br/>virtual dispatch"| L3_PRIV
    L3_PRIV -->|"virtual dispatch"| L4_IMPL
    L4_IMPL -->|"calls"| L4_WORK
    
    style L1_PUB fill:#f9f9f9,stroke:#333,stroke-width:2px
    style L2_CONCRETE fill:#f0f0f0,stroke:#333,stroke-width:2px
    style L4_IMPL fill:#e8e8e8,stroke:#333,stroke-width:2px
```

**Method Delegation Through PIMPL Layers**

Each layer performs specific transformations:

1. **Layer 1 (Public API)**: Template method on `MatrixType`, validates PIMPL initialization
2. **Layer 2 (Impl Bridge)**: Virtual method enabling polymorphism over data distribution models
3. **Layer 3 (PIMPL Core)**: Non-template method on raw pointers, wraps virtual `_` method
4. **Layer 4 (Concrete Strategy)**: Implements actual integration logic

This pattern appears for all 10+ integration method families.

Sources: [include/gauxc/xc_integrator/impl.hpp:55-60](), [include/gauxc/xc_integrator/replicated/impl.hpp:103-115](), [src/xc_integrator/replicated/replicated_xc_integrator_impl.cxx:66-74](), [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_vxc.hpp:30-121]()

---

## Integration Pipeline Data Flow

The complete integration pipeline for computing XC energy and potential follows this data flow:

```mermaid
flowchart TB
    subgraph "Inputs"
        P["Density Matrix P<br/>nbf × nbf"]
        FUNC["XC Functional<br/>functional_type"]
        MOL["Molecule<br/>Geometry"]
        BASIS["Basis Set<br/>BasisSet&lt;double&gt;"]
    end
    
    subgraph "Task Generation"
        LB["LoadBalancer<br/>load_balancer_->get_tasks()"]
        TASKS["Vector&lt;XCTask&gt;<br/>Grid points, weights, shell lists"]
    end
    
    subgraph "Shell Batching (Optional)"
        BATCH_GEN["generate_incore_task<br/>Group by union shell list"]
        SUBBASIS["Extract BasisSet subset"]
        EXTRACT_P["submat_set<br/>Extract subdensity"]
    end
    
    subgraph "Local Work Execution"
        LWD_EXEC["LocalWorkDriver Execution<br/>Host or Device"]
        COLLOC["Collocation<br/>Evaluate φ, ∇φ, ∇²φ"]
        DENS_EVAL["Density Evaluation<br/>ρ = Σ Pᵢⱼ φᵢ φⱼ"]
        XC_EVAL["XC Functional Evaluation<br/>εxc, vxc from ρ, ∇ρ"]
        INTEGRATE["Numerical Integration<br/>Exc = Σ wᵢ εxc, Vxc = Σ wᵢ vxc φᵢ φⱼ"]
    end
    
    subgraph "Result Aggregation"
        INCREMENT["inc_by_submat<br/>Add to full VXC (if batched)"]
        REDUCE["ReductionDriver<br/>MPI_Allreduce"]
        OUTPUT["EXC (scalar)<br/>VXC (nbf × nbf matrix)"]
    end
    
    P --> LB
    MOL --> LB
    BASIS --> LB
    LB --> TASKS
    
    TASKS --> BATCH_GEN
    TASKS --> LWD_EXEC
    
    BATCH_GEN --> SUBBASIS
    BASIS --> SUBBASIS
    SUBBASIS --> COLLOC
    
    BATCH_GEN --> EXTRACT_P
    P --> EXTRACT_P
    EXTRACT_P --> DENS_EVAL
    
    LWD_EXEC --> COLLOC
    COLLOC --> DENS_EVAL
    DENS_EVAL --> XC_EVAL
    FUNC --> XC_EVAL
    TASKS -->|"weights"| INTEGRATE
    XC_EVAL --> INTEGRATE
    COLLOC --> INTEGRATE
    
    INTEGRATE --> INCREMENT
    INCREMENT --> REDUCE
    INTEGRATE --> REDUCE
    REDUCE --> OUTPUT
    
    style LB fill:#f9f9f9,stroke:#333,stroke-width:2px
    style LWD_EXEC fill:#f0f0f0,stroke:#333,stroke-width:2px
    style REDUCE fill:#e8e8e8,stroke:#333,stroke-width:2px
```

**Complete Integration Pipeline Data Flow**

The pipeline executes in six stages:

1. **Task Generation**: `LoadBalancer` generates `XCTask` objects from molecular data
2. **Shell Batching**: Tasks optionally grouped and subbasis/subdensity extracted
3. **Collocation**: Basis functions evaluated on grid points
4. **Density Evaluation**: Density computed from basis functions and density matrix
5. **Integration**: XC functional evaluated and integrated with quadrature weights
6. **Reduction**: Partial results aggregated across MPI ranks

Sources: [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_vxc.hpp:30-121](), [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_vxc.hpp:154-270]()

For execution-specific details, see [Execution Model: Host vs Device](#4.2).

---

## Code Organization by Integration Strategy

The codebase is organized to separate different integration strategies:

### Directory Structure

```
src/xc_integrator/
├── replicated/                           # Replicated data implementations
│   ├── replicated_xc_integrator_impl.cxx # Base implementation
│   ├── host/                             # Host-only implementations
│   │   └── reference_replicated_xc_host_integrator*.hpp
│   ├── device/                           # Device implementations
│   │   └── incore_replicated_xc_device_integrator*.hpp
│   └── ...
├── shell_batched/                        # Shell batching strategy
│   ├── shell_batched_replicated_xc_integrator_exc_vxc.hpp
│   ├── shell_batched_replicated_xc_integrator_exc.hpp
│   ├── shell_batched_replicated_xc_integrator_exx.hpp
│   └── ...
└── ...
```

### Implementation File Naming Convention

Shell-batched implementations follow a systematic naming pattern:
- `shell_batched_replicated_xc_integrator_exc_vxc.hpp`: Energy + potential
- `shell_batched_replicated_xc_integrator_exc.hpp`: Energy only
- `shell_batched_replicated_xc_integrator_exc_grad.hpp`: Energy gradient
- `shell_batched_replicated_xc_integrator_exx.hpp`: Exact exchange
- `shell_batched_replicated_xc_integrator_integrate_den.hpp`: Density integration
- `shell_batched_replicated_xc_integrator_fxc_contraction.hpp`: XC kernel contraction
- `shell_batched_replicated_xc_integrator_dd_psi.hpp`: Spherical harmonic projection
- `shell_batched_replicated_xc_integrator_dd_psi_potential.hpp`: Projection potential

Each file contains the `eval_*_()` virtual method implementation for that specific integration task.

### Feature Availability Matrix

| Integration Method | ShellBatched | IncoreHost | IncoreDevice |
|--------------------|--------------|------------|--------------|
| `integrate_den` | ❌ NYI | ✓ | ❌ NYI |
| `eval_exc` | ✓ | ✓ | ✓ |
| `eval_exc_vxc` | ✓ | ✓ | ✓ |
| `eval_exc_grad` | ❌ NYI | ✓ | ❌ NYI |
| `eval_exx` | ❌ NYI | ✓ | ❌ NYI |
| `eval_fxc_contraction` | ❌ NYI | ✓ | ❌ NYI |
| `eval_dd_psi` | ❌ NYI | ✓ | ❌ NYI |
| `eval_dd_psi_potential` | ❌ NYI | ✓ | ❌ NYI |
| `eval_exc_vxc_onedft` | ❌ NYI | ✓ | ❌ NYI |

Not-Yet-Implemented (NYI) methods throw `GAUXC_GENERIC_EXCEPTION`.

Sources: [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc.hpp:1-134](), [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exx.hpp:16-23](), [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_exc_grad.hpp:16-32](), [src/xc_integrator/shell_batched/shell_batched_replicated_xc_integrator_integrate_den.hpp:16-24]()

---

## Summary

The GauXC system architecture employs several key design patterns:

1. **Layered PIMPL**: Double indirection enables polymorphism over data models and execution strategies while maintaining binary stability
2. **Replicated Data Model**: All ranks hold full input data; work distribution via task partitioning; single reduction at end
3. **Component Composition**: Four core components (Functional, LoadBalancer, LocalWorkDriver, ReductionDriver) orchestrate the integration
4. **Shell Batching**: Tasks grouped by union shell lists to improve data locality and reduce memory overhead
5. **Asynchronous Execution**: Producer-consumer pattern overlaps batch generation with execution
6. **Submatrix Operations**: Extract and operate on relevant subbasis/subdensity to minimize memory and computation
7. **Virtual Method Delegation**: Consistent pattern from public API through PIMPL layers to concrete implementations

For implementation details of specific subsystems, see:
- [Core Components](#4.1) for LoadBalancer, LocalWorkDriver, and ReductionDriver
- [Execution Model: Host vs Device](#4.2) for computational execution paths
- [Task System and Data Structures](#4.3) for XCTask and related structures

---

