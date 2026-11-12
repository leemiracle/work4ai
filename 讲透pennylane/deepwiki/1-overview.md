<!-- source: DeepWiki mcp.deepwiki.com · repo PennyLaneAI/pennylane · page 1 Overview · fetched 2026-10-21 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)
- [.pylintrc](.pylintrc)
- [AI_Policy.md](AI_Policy.md)
- [README.md](README.md)
- [doc/code/qml.rst](doc/code/qml.rst)
- [doc/conf.py](doc/conf.py)
- [doc/development/guide/documentation.rst](doc/development/guide/documentation.rst)
- [doc/development/guide/installation.rst](doc/development/guide/installation.rst)
- [doc/index.rst](doc/index.rst)
- [doc/introduction/compiling_workflows.rst](doc/introduction/compiling_workflows.rst)
- [doc/requirements.txt](doc/requirements.txt)
- [pennylane/compiler/__init__.py](pennylane/compiler/__init__.py)
- [pennylane/compiler/compiler.py](pennylane/compiler/compiler.py)
- [pennylane/numpy/random.py](pennylane/numpy/random.py)
- [pyproject.toml](pyproject.toml)
- [setup.py](setup.py)
- [tests/.pylintrc](tests/.pylintrc)

</details>



## Purpose and Scope

This document provides a high-level introduction to PennyLane, its architecture, and core concepts. It is intended for developers who want to understand how PennyLane is structured and how its major systems interact.

For detailed information about specific subsystems:
- Core quantum abstractions (operators, circuits, measurements): see [Core Quantum Abstractions](#2)
- Circuit transformation and compilation: see [Transform and Compilation System](#3)
- Device backends and simulation: see [Devices and Simulation](#4)
- Quantum operations and gates: see [Quantum Operations](#5)
- Mathematical framework: see [Mathematical Framework](#6)
- Development tools and infrastructure: see [Development Infrastructure](#8)

**Sources:** [doc/index.rst:1-55](), [README.md:28-67]()

---

## What is PennyLane?

PennyLane is a cross-platform Python library for **quantum computing**, **quantum machine learning**, and **quantum chemistry**. Its central design principle is to enable users to "train a quantum computer the same way as a neural network" by providing automatic differentiation of quantum circuits and seamless integration with machine learning frameworks.

**Core capabilities:**

| Feature | Description |
|---------|-------------|
| **Quantum Circuit Programming** | Define quantum circuits using a wide range of gates, state preparations, and measurements |
| **Automatic Differentiation** | Built-in gradient computation for quantum circuits via multiple methods (parameter shift, adjoint, finite difference) |
| **Hybrid Workflows** | Combine quantum circuits with classical processing in a single computational graph |
| **Multi-Framework Support** | Interface with NumPy, JAX, PyTorch, TensorFlow, and Autograd |
| **Device Independence** | Run the same circuit on simulators or quantum hardware by changing one line of code |
| **JIT Compilation** | Compile hybrid quantum-classical workflows using Catalyst or CUDA Quantum |
| **Transform System** | Apply circuit optimizations and manipulations via composable transforms |

**Sources:** [doc/index.rst:28-92](), [README.md:47-67](), [pyproject.toml:6-8]()

---

## Installation and Requirements

**Minimum Requirements:**
- Python >= 3.11
- Core dependencies installed automatically: `numpy`, `scipy`, `networkx`, `rustworkx>=0.14.0`, `autograd`, `autoray==0.8.4`, `pennylane-lightning>=0.44`

**Installation:**
```bash
python -m pip install pennylane
```

**Optional Dependency Groups:**

| Group | Purpose | Install Command |
|-------|---------|-----------------|
| `dev` | Development tools (pytest, black, pylint, isort) | `pip install --group dev` |
| `docs` | Documentation building (sphinx, jax, torch) | `pip install --group docs` |
| `qchem` | Quantum chemistry support | `pip install pennylane[qchem]` |
| `qcut` | Circuit cutting functionality | `pip install pennylane[qcut]` |
| `external-libraries` | Third-party integrations (pyzx, stim, quimb) | `pip install --group external-libraries` |

**Sources:** [pyproject.toml:10-27](), [pyproject.toml:46-144](), [doc/development/guide/installation.rst:1-84]()

---

## Core Architecture

PennyLane follows a **layered architecture** that separates user-facing abstractions from device execution. This design enables the same quantum circuit to run on different backends with minimal code changes.

```mermaid
graph TB
    subgraph "Layer 1: User Interface"
        QNode["@qml.qnode<br/>QNode decorator"]
        Ops["Quantum Operators<br/>qml.RX, qml.CNOT, etc."]
        Templates["Circuit Templates<br/>qml.AngleEmbedding, etc."]
        Measure["Measurements<br/>qml.expval, qml.sample"]
    end
    
    subgraph "Layer 2: Compilation & Transforms"
        Pipeline["CompilePipeline<br/>pennylane/workflow/compilation.py"]
        Transforms["Transform Functions<br/>decompose, broadcast_expand"]
        Gradients["Gradient Methods<br/>parameter_shift, adjoint"]
    end
    
    subgraph "Layer 3: Circuit Representation"
        QuantumScript["QuantumScript<br/>pennylane/tape/qscript.py"]
        SymbolicOps["Symbolic Operators<br/>Controlled, Adjoint, Prod, Sum"]
    end
    
    subgraph "Layer 4: Mathematical Backend"
        MultiDispatch["multi_dispatch<br/>pennylane/math/multi_dispatch.py"]
        QuantumMath["quantum.py<br/>vn_entropy, partial_trace"]
    end
    
    subgraph "Layer 5: Device Ecosystem"
        DeviceAPI["Device<br/>pennylane/devices/device.py"]
        DefaultQubit["DefaultQubit<br/>pennylane/devices/default_qubit.py"]
        Plugins["Plugin Devices<br/>entry_points['pennylane.plugins']"]
    end
    
    subgraph "Layer 6: Execution Engine"
        Execute["qml.execute<br/>pennylane/workflow/execution.py"]
        ExecutionConfig["ExecutionConfig<br/>resolution.py"]
    end
    
    QNode --> Pipeline
    Ops --> QuantumScript
    Templates --> QuantumScript
    Measure --> QuantumScript
    
    Pipeline --> Transforms
    Pipeline --> Gradients
    Transforms --> QuantumScript
    
    QuantumScript --> SymbolicOps
    SymbolicOps --> MultiDispatch
    
    Pipeline --> Execute
    Execute --> ExecutionConfig
    ExecutionConfig --> DeviceAPI
    DeviceAPI --> DefaultQubit
    DeviceAPI --> Plugins
    
    style QNode fill:#f9f9f9,stroke:#333,stroke-width:2px
    style QuantumScript fill:#f9f9f9,stroke:#333,stroke-width:2px
    style DeviceAPI fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Architecture Layers:**

1. **User Interface Layer:** High-level abstractions for defining quantum circuits (`@qml.qnode`, operators, templates, measurements)
2. **Compilation & Transforms Layer:** Circuit optimization, decomposition, and gradient computation via `CompilePipeline`
3. **Circuit Representation Layer:** Internal representation as `QuantumScript` with symbolic operator algebra
4. **Mathematical Backend Layer:** Framework-agnostic math operations supporting NumPy, JAX, PyTorch, TensorFlow
5. **Device Ecosystem:** Abstract `Device` interface with built-in simulators and plugin system
6. **Execution Engine:** Batch execution, workflow configuration, and differentiation via `qml.execute`

**Sources:** High-level architecture diagram, [pennylane/workflow/qnode.py](), [pennylane/tape/qscript.py](), [pennylane/devices/device.py](), [pennylane/workflow/execution.py]()

---

## Key Concepts

### QNode: Quantum Functions

A **QNode** is a quantum function decorated with `@qml.qnode` that binds a Python function to a quantum device. When called, the QNode constructs a `QuantumScript`, applies transforms, and executes on the device.

```mermaid
graph LR
    UserCode["User Function<br/>def circuit(params):"]
    Decorator["@qml.qnode(device)"]
    QNode["QNode Object<br/>pennylane/workflow/qnode.py"]
    Tape["QuantumScript<br/>pennylane/tape/qscript.py"]
    Device["Device Execution<br/>DefaultQubit, etc."]
    
    UserCode --> Decorator
    Decorator --> QNode
    QNode --> Tape
    Tape --> Device
```

**Key QNode attributes:**
- `device`: The device to execute on
- `interface`: Auto-detected ML framework (`'jax'`, `'torch'`, `'tf'`, `'autograd'`, `'numpy'`)
- `diff_method`: Differentiation method (`'best'`, `'parameter-shift'`, `'adjoint'`, `'backprop'`, etc.)
- `expansion_strategy`: How to decompose operations

**Sources:** [pennylane/workflow/qnode.py](), QNode Execution Pipeline diagram

### Devices: Execution Backends

**Devices** implement the abstract `Device` interface and provide the execution backend for quantum circuits. Devices are registered via Python entry points in the `pennylane.plugins` group.

```mermaid
graph TD
    EntryPoints["pyproject.toml<br/>[project.entry-points.'pennylane.plugins']"]
    Discovery["Device Discovery<br/>at import time"]
    DeviceAPI["Device ABC<br/>pennylane/devices/device.py"]
    
    subgraph "Built-in Devices"
        DQ["default.qubit<br/>State vector simulator"]
        DM["default.mixed<br/>Density matrix simulator"]
        DG["default.gaussian<br/>CV simulator"]
        DC["default.clifford<br/>Stabilizer simulator"]
        DT["default.tensor<br/>Tensor network simulator"]
    end
    
    subgraph "Plugin Devices"
        Lightning["pennylane-lightning<br/>C++ simulator"]
        Qiskit["pennylane-qiskit<br/>IBM Quantum access"]
        ThirdParty["Other plugins<br/>cirq, braket, etc."]
    end
    
    EntryPoints --> Discovery
    Discovery --> DeviceAPI
    
    DeviceAPI --> DQ
    DeviceAPI --> DM
    DeviceAPI --> DG
    DeviceAPI --> DC
    DeviceAPI --> DT
    
    DeviceAPI --> Lightning
    DeviceAPI --> Qiskit
    DeviceAPI --> ThirdParty
```

**Entry point registration example:**
```python
[project.entry-points."pennylane.plugins"]
"default.qubit" = "pennylane.devices:DefaultQubit"
"default.gaussian" = "pennylane.devices:DefaultGaussian"
"default.mixed" = "pennylane.devices.default_mixed:DefaultMixed"
```

**Sources:** [pyproject.toml:161-170](), Device Plugin System diagram, [pennylane/devices/device.py]()

### Operators: Quantum Gates and Observables

All quantum operations inherit from the `Operator` base class defined in `pennylane/operation.py`. Operators support:
- **Matrix representation:** `compute_matrix()`, `sparse_matrix()`
- **Decomposition:** `compute_decomposition()` into primitive gates
- **Parameter broadcasting:** `batch_size`, `ndim_params` for batched execution
- **Symbolic composition:** `Controlled`, `Adjoint`, `Prod`, `Sum`, `SProd`, `Pow`

```mermaid
graph TD
    Operator["Operator<br/>pennylane/operation.py"]
    Operation["Operation<br/>Unitary gates"]
    Observable["Observable<br/>Measurement basis"]
    SymbolicOp["SymbolicOp<br/>Composite operators"]
    
    Operator --> Operation
    Operator --> Observable
    Operator --> SymbolicOp
    
    Operation --> Gates["Gates<br/>RX, CNOT, Hadamard"]
    Observable --> PauliObs["Pauli Observables<br/>PauliX, PauliZ"]
    SymbolicOp --> Controlled["Controlled<br/>ctrl function"]
    SymbolicOp --> Adjoint["Adjoint<br/>adjoint function"]
    SymbolicOp --> Arithmetic["Arithmetic<br/>Prod, Sum, SProd"]
```

**Sources:** [pennylane/operation.py](), Operator and Symbolic Mathematics System diagram

### Transforms: Circuit Manipulation

**Transforms** are functions decorated with `@transform` that modify quantum circuits. They can be applied to QNodes, tapes, or functions, and are composed into a `CompilePipeline`.

**Transform categories:**

| Category | Examples | Purpose |
|----------|----------|---------|
| **Circuit Optimization** | `cancel_inverses`, `merge_rotations`, `commute_controlled` | Reduce gate count |
| **Decomposition** | `decompose`, `unitary_to_rot` | Convert to device gate set |
| **Batching** | `broadcast_expand`, `batch_params` | Handle batched parameters |
| **Gradient** | `param_shift`, `adjoint_metric_tensor` | Enable differentiation |
| **Measurement** | `defer_measurements`, `dynamic_one_shot` | Mid-circuit measurements |
| **Advanced** | `qcut` (circuit cutting), `mitigate_with_zne` | Specialized techniques |

**Pipeline levels:**
- `top`: Complete pipeline
- `user`: User-applied transforms
- `gradient`: Gradient-related transforms
- `device`: Device-specific transforms

**Sources:** [pennylane/transforms/](), Transform and Compilation System diagram

---

## Execution Flow

The following diagram shows the complete execution path from user code to device results, including the key classes and functions involved:

```mermaid
sequenceDiagram
    participant User
    participant QNode as "QNode<br/>workflow/qnode.py"
    participant Pipeline as "CompilePipeline<br/>workflow/compilation.py"
    participant Config as "ExecutionConfig<br/>workflow/resolution.py"
    participant Execute as "qml.execute<br/>workflow/execution.py"
    participant Device as "Device<br/>devices/device.py"
    participant Gradient as "GradientTransform<br/>gradients/"
    
    User->>QNode: circuit(params)
    QNode->>QNode: Construct QuantumScript<br/>via queuing system
    QNode->>Pipeline: Apply transform chain
    
    Pipeline->>Pipeline: User transforms
    Pipeline->>Pipeline: Gradient transforms<br/>(based on diff_method)
    Pipeline->>Pipeline: Device transforms
    
    Pipeline->>Config: Resolve ExecutionConfig:<br/>- interface detection<br/>- diff_method selection<br/>- mcm_config
    
    Config->>Execute: execute(tapes, device, config)
    Execute->>Device: preprocess(execution_config)
    Device-->>Execute: transformed_tapes
    Execute->>Device: execute_and_compute_derivatives()
    Device-->>Execute: results
    
    alt Gradient Required
        Execute->>Gradient: compute_derivatives()
        Gradient->>Device: execute(gradient_tapes)
        Device-->>Gradient: gradient_results
        Gradient-->>Execute: processed_gradients
    end
    
    Execute-->>QNode: results
    QNode-->>User: output
```

**Key execution stages:**

1. **QNode Call:** User calls the quantum function with parameters
2. **Tape Construction:** QNode uses the queuing system to record operations into a `QuantumScript`
3. **Transform Pipeline:** `CompilePipeline` applies transforms at user/gradient/device levels
4. **Config Resolution:** `ExecutionConfig` determines interface, differentiation method, and device capabilities
5. **Device Preprocessing:** Device applies its own transforms and optimizations
6. **Execution:** `qml.execute` batches tapes and calls device execution methods
7. **Gradient Computation:** If gradients are needed, gradient transforms generate and execute additional tapes
8. **Result Processing:** Results are processed and returned to the user

**Sources:** QNode Execution Pipeline diagram, [pennylane/workflow/qnode.py](), [pennylane/workflow/execution.py](), [pennylane/workflow/resolution.py]()

---

## Multi-Framework Integration

PennyLane supports multiple machine learning frameworks through a **multi-dispatch system** that provides framework-agnostic mathematical operations:

```mermaid
graph TB
    subgraph "ML Frameworks"
        NumPy["NumPy<br/>numpy.ndarray"]
        Autograd["Autograd<br/>autograd.numpy.ArrayBox"]
        JAX["JAX<br/>jax.Array/Tracer"]
        PyTorch["PyTorch<br/>torch.Tensor"]
        TensorFlow["TensorFlow<br/>tf.Tensor"]
    end
    
    subgraph "Dispatch Layer"
        Autoray["autoray==0.8.4<br/>Backend abstraction"]
        SingleDispatch["single_dispatch.py<br/>Per-framework implementations"]
        MultiDispatch["multi_dispatch.py<br/>@multi_dispatch decorator"]
    end
    
    subgraph "Math Operations"
        BasicOps["Basic ops<br/>array, kron, concatenate"]
        LinAlg["Linear algebra<br/>inv, expm, eigvals"]
        QuantumOps["Quantum ops<br/>reduce_dm, vn_entropy"]
    end
    
    NumPy --> Autoray
    Autograd --> Autoray
    JAX --> Autoray
    PyTorch --> Autoray
    TensorFlow --> Autoray
    
    Autoray --> SingleDispatch
    SingleDispatch --> MultiDispatch
    
    MultiDispatch --> BasicOps
    MultiDispatch --> LinAlg
    MultiDispatch --> QuantumOps
```

**Interface detection:** PennyLane automatically detects the ML framework from tensor types:
- `numpy` → NumPy arrays
- `autograd` → Autograd ArrayBox
- `jax` → JAX Arrays/Tracers
- `torch` → PyTorch Tensors
- `tensorflow` → TensorFlow Tensors

**Gradient computation methods by interface:**

| Interface | Supported Gradient Methods |
|-----------|----------------------------|
| `autograd` | `parameter-shift`, `finite-diff`, `adjoint` |
| `jax` | `parameter-shift`, `finite-diff`, `adjoint`, `backprop` |
| `torch` | `parameter-shift`, `finite-diff`, `adjoint`, `backprop` |
| `tensorflow` | `parameter-shift`, `finite-diff`, `adjoint`, `backprop` |
| `numpy` | None (forward evaluation only) |

**Sources:** Math and Interface Abstraction Layer diagram, [pennylane/math/multi_dispatch.py](), [pennylane/math/single_dispatch.py](), [pyproject.toml:18]()

---

## Compiler Integration

PennyLane supports hybrid quantum-classical compilation through a **plugin system** for external compilers. Compilers are registered via the `pennylane.compilers` entry point group.

```mermaid
graph LR
    subgraph "Compiler Registration"
        EntryPoints["Entry Points<br/>group='pennylane.compilers'"]
        Interface["Required Exports:<br/>- context<br/>- ops<br/>- qjit"]
    end
    
    subgraph "Available Compilers"
        Catalyst["catalyst<br/>pennylane-catalyst<br/>MLIR-based JIT"]
        CUDAQuantum["cuda_quantum<br/>NVIDIA compiler<br/>GPU-accelerated"]
    end
    
    subgraph "Compiler API"
        Available["available_compilers()<br/>List installed compilers"]
        Active["active_compiler()<br/>Check compilation context"]
        QJIT["@qml.qjit<br/>JIT decorator"]
    end
    
    EntryPoints --> Interface
    Interface --> Catalyst
    Interface --> CUDAQuantum
    
    Catalyst --> Available
    CUDAQuantum --> Available
    Available --> Active
    Active --> QJIT
```

**Compiler entry point structure:**
- `compiler_name.context`: Compilation context manager with `is_tracing()` method
- `compiler_name.ops`: Compiler-specific operations (e.g., `cond`, `for_loop`)
- `compiler_name.qjit`: JIT decorator function with signature `qjit(fn, *args, **kwargs)`

**Usage example:**
```python
@qml.qjit  # Uses default compiler (Catalyst)
@qml.qnode(dev)
def circuit(x):
    qml.RX(x, wires=0)
    return qml.expval(qml.Z(0))

@qml.qjit(compiler="cuda_quantum")  # Specify compiler
@qml.qnode(dev)
def circuit_cuda(x):
    qml.RX(x, wires=0)
    return qml.expval(qml.Z(0))
```

**Sources:** [pennylane/compiler/compiler.py:1-248](), [pennylane/compiler/__init__.py:14-255](), [doc/introduction/compiling_workflows.rst:1-181]()

---

## Development Infrastructure

PennyLane uses modern Python development tools and CI/CD infrastructure:

```mermaid
graph TB
    subgraph "Package Management"
        Pyproject["pyproject.toml<br/>PEP 621 metadata"]
        Setup["setup.py<br/>Entry point wrapper"]
        Version["_version.py<br/>Version string"]
    end
    
    subgraph "Code Quality"
        Black["Black 25.9.0<br/>Code formatter"]
        Pylint["Pylint 4.0.0<br/>Linter"]
        Isort["isort 7.0.0<br/>Import sorter"]
        PreCommit["pre-commit 4.5.0<br/>Git hooks"]
    end
    
    subgraph "Testing"
        Pytest["pytest 8.4.1<br/>Test framework"]
        Coverage["pytest-cov<br/>Coverage tracking"]
        Xdist["pytest-xdist<br/>Parallel execution"]
        Split["pytest-split<br/>CI optimization"]
    end
    
    subgraph "Documentation"
        Sphinx["Sphinx 8.1<br/>Doc generator"]
        Automodapi["sphinx-automodapi<br/>API docs"]
        Theme["pennylane-sphinx-theme<br/>Custom styling"]
    end
    
    subgraph "CI/CD"
        GHA["GitHub Actions<br/>.github/workflows/"]
        InterfaceTests["interface-unit-tests.yml<br/>12 test job types"]
        Benchmarks["benchmarks.yml<br/>Performance tracking"]
    end
    
    Pyproject --> Setup
    Pyproject --> Version
    
    PreCommit --> Black
    PreCommit --> Pylint
    PreCommit --> Isort
    
    Pytest --> Coverage
    Pytest --> Xdist
    Pytest --> Split
    
    Sphinx --> Automodapi
    Sphinx --> Theme
    
    GHA --> InterfaceTests
    GHA --> Benchmarks
```

**Dependency groups:**

| Group | Purpose | Key Packages |
|-------|---------|--------------|
| Core dependencies | Required for basic functionality | `numpy>=2.0`, `scipy`, `autograd`, `autoray==0.8.4`, `pennylane-lightning>=0.44` |
| `dev` | Development and testing | `pytest>=8.4.1`, `black==25.9.0`, `pylint~=4.0.0`, `isort~=7.0.0` |
| `docs` | Documentation building | `sphinx==8.1`, `jax==0.7.1`, `torch~=2.9.0` |
| `qchem` | Quantum chemistry | `openfermionpyscf`, `basis-set-exchange`, `geometric` |
| `qcut` | Circuit cutting | `kahypar==1.3.5`, `opt_einsum` |
| `external-libraries` | Third-party integrations | `pyzx`, `stim`, `quimb`, `qualtran` |

**CI/CD workflows:**
- **interface-unit-tests.yml:** 12 test job types covering different ML frameworks (JAX, PyTorch, TensorFlow)
- **benchmarks.yml:** Performance regression tracking
- **upload.yml:** Automated PyPI releases

**Sources:** [pyproject.toml:1-210](), [setup.py:1-3](), [doc/conf.py:1-397](), [.pylintrc:1-48](), Development and Quality Infrastructure diagram

---

## Repository Structure

**Key directories:**

| Directory | Purpose |
|-----------|---------|
| `pennylane/` | Main package source code |
| `pennylane/devices/` | Built-in device implementations |
| `pennylane/ops/` | Quantum operations and gates |
| `pennylane/transforms/` | Circuit transforms |
| `pennylane/workflow/` | QNode and execution engine |
| `pennylane/math/` | Multi-dispatch math system |
| `pennylane/gradients/` | Differentiation methods |
| `pennylane/tape/` | QuantumScript and tape system |
| `pennylane/compiler/` | Compiler plugin infrastructure |
| `doc/` | Documentation source (reStructuredText) |
| `tests/` | Test suite |
| `.github/workflows/` | CI/CD configurations |

**Sources:** Repository structure inspection

---

## Next Steps

For detailed information about specific subsystems, refer to the following pages:

- **[Core Quantum Abstractions](#2):** `Operator`, `QuantumScript`, `QNode`, measurement processes
- **[Transform and Compilation System](#3):** Transform framework, `CompilePipeline`, decomposition, gradient methods
- **[Devices and Simulation](#4):** Device API, `DefaultQubit`, `DefaultMixed`, Gaussian simulators, Catalyst JIT
- **[Quantum Operations](#5):** Gate sets, controlled/adjoint operations, operator arithmetic, resource estimation
- **[Mathematical Framework](#6):** Multi-dispatch system, quantum information functions
- **[Templates and Advanced Features](#7):** Circuit templates, quantum chemistry, operator validation
- **[Development Infrastructure](#8):** Package structure, testing, CI/CD, documentation system

**External Resources:**
- GitHub Repository: https://github.com/PennyLaneAI/pennylane
- Documentation: https://docs.pennylane.ai
- Demos and Tutorials: https://pennylane.ai/qml/demonstrations
- Discussion Forum: https://discuss.pennylane.ai

**Sources:** [doc/index.rst:154-247](), [README.md:84-169](), [.github/CONTRIBUTING.md:1-106]()

---

