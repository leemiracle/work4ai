<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuopt · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [conda/environments/all_cuda-129_arch-aarch64.yaml](conda/environments/all_cuda-129_arch-aarch64.yaml)
- [conda/environments/all_cuda-129_arch-x86_64.yaml](conda/environments/all_cuda-129_arch-x86_64.yaml)
- [conda/environments/all_cuda-133_arch-aarch64.yaml](conda/environments/all_cuda-133_arch-aarch64.yaml)
- [conda/environments/all_cuda-133_arch-x86_64.yaml](conda/environments/all_cuda-133_arch-x86_64.yaml)
- [conda/recipes/cuopt-server/recipe.yaml](conda/recipes/cuopt-server/recipe.yaml)
- [conda/recipes/cuopt-sh-client/recipe.yaml](conda/recipes/cuopt-sh-client/recipe.yaml)
- [conda/recipes/cuopt/recipe.yaml](conda/recipes/cuopt/recipe.yaml)
- [conda/recipes/libcuopt/recipe.yaml](conda/recipes/libcuopt/recipe.yaml)
- [dependencies.yaml](dependencies.yaml)
- [docs/cuopt/source/convex-features.rst](docs/cuopt/source/convex-features.rst)
- [docs/cuopt/source/cuopt-c/mip/index.rst](docs/cuopt/source/cuopt-c/mip/index.rst)
- [docs/cuopt/source/cuopt-c/quick-start.rst](docs/cuopt/source/cuopt-c/quick-start.rst)
- [docs/cuopt/source/cuopt-cli/index.rst](docs/cuopt/source/cuopt-cli/index.rst)
- [docs/cuopt/source/cuopt-cli/quick-start.rst](docs/cuopt/source/cuopt-cli/quick-start.rst)
- [docs/cuopt/source/cuopt-python/index.rst](docs/cuopt/source/cuopt-python/index.rst)
- [docs/cuopt/source/cuopt-python/mip/index.rst](docs/cuopt/source/cuopt-python/mip/index.rst)
- [docs/cuopt/source/cuopt-python/quick-start.rst](docs/cuopt/source/cuopt-python/quick-start.rst)
- [docs/cuopt/source/cuopt-server/quick-start.rst](docs/cuopt/source/cuopt-server/quick-start.rst)
- [docs/cuopt/source/index.rst](docs/cuopt/source/index.rst)
- [docs/cuopt/source/introduction.rst](docs/cuopt/source/introduction.rst)
- [docs/cuopt/source/milp-features.rst](docs/cuopt/source/milp-features.rst)
- [docs/cuopt/source/mip-settings.rst](docs/cuopt/source/mip-settings.rst)
- [docs/cuopt/source/thirdparty_modeling_languages/index.rst](docs/cuopt/source/thirdparty_modeling_languages/index.rst)
- [python/cuopt/pyproject.toml](python/cuopt/pyproject.toml)
- [python/cuopt_self_hosted/pyproject.toml](python/cuopt_self_hosted/pyproject.toml)
- [python/cuopt_server/pyproject.toml](python/cuopt_server/pyproject.toml)
- [python/libcuopt/pyproject.toml](python/libcuopt/pyproject.toml)

</details>



This document introduces NVIDIA cuOpt, a GPU-accelerated optimization engine designed for high-performance combinatorial and continuous optimization. It covers the system's core capabilities (Linear Programming, Quadratic Programming, Mixed Integer Linear Programming, Second-Order Cone Programming, and Vehicle Routing Problems), design philosophy, package ecosystem, and positioning within the NVIDIA AI Enterprise ecosystem [README.md:15-17](). 

As a parent page, this document provides a high-level summary of cuOpt's architecture and deployment options. For deep technical details, refer to the child pages:
- Installation and system requirements: [Installation and Getting Started](#1.1)
- Component layering and library splitting: [Package Architecture](#1.2)
- Internal solver hierarchy, hybrid execution, and data flow: [System Architecture](#1.3)

---

## Capabilities and Design Philosophy

NVIDIA cuOpt leverages massively parallel GPU architectures to deliver near real-time solutions for large-scale mathematical optimization problems. The core engine is implemented in C++ and exposes multiple integration interfaces, including a low-level C API (`cuopt_c.h`), high-level Python bindings, REST/FastAPI microservices, and gRPC remote services [README.md:21-42]().

### Supported Problem Types
*   **Linear Programming (LP)** & **Quadratic Programming (QP)**: Solved concurrently via GPU first-order methods (PDLP), GPU interior-point barrier methods (using cuDSS), and CPU revised dual simplex [README.md:15-17]().
*   **Mixed Integer Programming (MILP)**: Hybrid GPU/CPU solver combining GPU primal heuristics (Feasibility Jump, RINS) with CPU branch-and-bound [README.md:15-17]().
*   **Second-Order Cone Programming (SOCP)** & **Quadratically Constrained QP (QCQP)**: Supported in beta via advanced barrier and conic solvers [README.md:15-17]().
*   **Vehicle Routing Problems (VRP)**: Supports Traveling Salesperson (TSP), Capacitated VRP (CVRP), and Pickup and Delivery with Time Windows (PDPTW) using population-based metaheuristics [README.md:36-36]().

```mermaid
graph TB
    subgraph ProblemSpace["Problem Formulations"]
        LP["Linear / Quadratic / Conic (LP/QP/SOCP)"]
        MILP["Mixed Integer Linear / Quadratic (MILP)"]
        VRP["Vehicle Routing (TSP/CVRP/PDPTW)"]
    end

    subgraph SolverEngines["cuOpt Core Engines (libcuopt)"]
        MathOpt["libcuopt-mathopt<br/>pdlp::PDLPSolver<br/>barrier::BarrierSolver<br/>dual_simplex::DualSimplexSolver"]
        MIPEngine["Hybrid MIP Engine<br/>mip_heuristics::*<br/>branch_and_bound::BranchAndBound"]
        RoutingEngine["libcuopt-routing<br/>Routing population metaheuristics"]
    end

    subgraph HardwareExecution["Hybrid GPU / CPU Execution"]
        GPU["NVIDIA GPU<br/>RMM, cuDSS, cuSPARSE, NCCL"]
        CPU["Multi-Core CPU<br/>Revised Simplex & Branch-and-Bound"]
    end

    LP --> MathOpt
    MILP --> MIPEngine
    VRP --> RoutingEngine

    MathOpt --> GPU
    MathOpt --> CPU
    MIPEngine --> GPU
    MIPEngine --> CPU
    RoutingEngine --> GPU

    Sources: [README.md:15-17](), [conda/recipes/libcuopt/recipe.yaml:106-115]()
```

Sources: [README.md:15-17](), [conda/recipes/libcuopt/recipe.yaml:106-115]()

---

## 1.1. Installation and Getting Started

cuOpt supports multiple installation channels including pip wheels (from the NVIDIA Python Package Index), conda packages (from the `rapidsai` channel), and pre-built Docker containers on Docker Hub and NVIDIA NGC [README.md:82-143](). 

System requirements include:
*   **GPU Architecture**: Volta architecture or later (Compute Capability ≥ 7.0) [README.md:66-66]().
*   **CUDA Toolkit**: CUDA 12.x or CUDA 13.x [README.md:64-64]().
*   **Operating System**: Linux (x86_64, aarch64) or Windows via WSL2 [README.md:74-76]().
*   **Python**: Python 3.11 through 3.14 [README.md:70-70]().

For step-by-step installation instructions, smoke tests, and interface quickstarts, see [Installation and Getting Started](#1.1).

Sources: [README.md:62-143]()

---

## 1.2. Package Architecture

The cuOpt repository is structured around a modular package ecosystem that separates client communication, mathematical optimization solvers, and routing engines. This modularity reduces dependency footprints for specialized deployments [dependencies.yaml:40-63]().

```mermaid
graph TB
    subgraph PythonLayer["Python SDK & Services"]
        PythonSDK["cuopt (Python SDK)<br/>Cython wrappers"]
        Server["cuopt_server<br/>FastAPI Microservice"]
        ShClient["cuopt_sh_client<br/>Self-hosted client"]
        MCP["cuopt_mcp<br/>Model Context Protocol"]
    end

    subgraph CppSplitLibs["Split C++ Shared Libraries (libcuopt metapackage)"]
        ClientLib["libcuopt-client<br/>RPC & client helpers"]
        MathOptLib["libcuopt-mathopt<br/>LP/QP/MILP solver engines<br/>(cuDSS, cuSparse, NCCL)"]
        RoutingLib["libcuopt-routing<br/>VRP solver engine"]
        GrpcServer["cuopt_grpc_server<br/>libcuopt._grpc_server_wrapper"]
    end

    PythonSDK --> ClientLib
    PythonSDK --> MathOptLib
    PythonSDK --> RoutingLib
    Server --> PythonSDK
    ShClient --> ClientLib
    MCP --> PythonSDK
    GrpcServer --> ClientLib

    Sources: [dependencies.yaml:40-63](), [python/libcuopt/pyproject.toml:33-36]()
```

For detailed component descriptions, see [Package Architecture](#1.2).

Sources: [dependencies.yaml:40-63](), [python/libcuopt/pyproject.toml:33-36]()

---

## 1.3. System Architecture

Internally, cuOpt manages optimization problems through a rigorous translation and execution pipeline. Problems are ingested via API layers (`cuopt_c.h` or Python wrappers), translated into internal representation structures (`optimization_problem_t`, `user_problem_t`), preprocessed (using PaPILO or internal presolvers), and dispatched to GPU-accelerated or hybrid CPU/GPU solver backends [README.md:21-21]().

```mermaid
graph TB
    subgraph APILayer["API Layers"]
        CAPI["C API (cuopt_c.h)"]
        PyAPI["Python SDK API"]
        ServerAPI["gRPC / HTTP Server API"]
    end

    subgraph TranslationPipeline["Problem Translation Pipeline"]
        Parser["MPS / LP Parser<br/>mps_parser"]
        Translator["Problem Translator<br/>user_problem_t -> lp_problem_t"]
        Presolve["Presolver<br/>PaPILO / PSLP"]
    end

    subgraph ExecutionCore["Execution Core"]
        RMM["RMM Memory Manager<br/>Device Memory Pools"]
        SolverDispatch["Solver Dispatcher<br/>Concurrent LP / MIP / VRP"]
    end

    CAPI --> Parser
    PyAPI --> Parser
    ServerAPI --> Parser

    Parser --> Translator
    Translator --> Presolve
    Presolve --> SolverDispatch
    
    RMM -.-> SolverDispatch

    Sources: [README.md:21-21](), [conda/recipes/libcuopt/recipe.yaml:80-94]()
```

For full architectural details on solver hierarchies, memory management via RMM, and remote gRPC execution, see [System Architecture](#1.3).

Sources: [README.md:21-21](), [conda/recipes/libcuopt/recipe.yaml:80-94]()

---

