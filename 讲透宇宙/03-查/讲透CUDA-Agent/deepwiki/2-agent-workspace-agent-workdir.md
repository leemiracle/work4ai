<!-- source: DeepWiki mcp.deepwiki.com · repo BytedTsinghua-SIA/CUDA-Agent · page 2 Agent Workspace (agent_workdir) · fetched 2026-10-26 -->

# Agent Workspace (agent_workdir)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [agent_workdir/SKILL.md](agent_workdir/SKILL.md)

</details>



This page describes the structure and operation of the `agent_workdir` directory: what each file does, how the files relate to each other, and how the full implement → compile → verify → profile → iterate cycle is executed. It serves as the entry point for understanding the workspace as a whole.

For the workflow constraints that govern agent behavior (the rules encoded in `SKILL.md`), see [Workflow Constraints (SKILL.md)](#2.1). For the build system details, see [Build System](#2.3). For correctness verification and performance profiling specifics, see [Correctness Verification](#2.4) and [Performance Profiling](#2.5). For the CUDA binding registry architecture, see [CUDA Extension Architecture](#3).

---

## Purpose

`agent_workdir` is a self-contained, standardized workspace in which an LLM-based agent generates and iteratively refines custom CUDA kernels to accelerate a given PyTorch model. The workspace provides:

- A **fixed baseline** (`model.py`) that the agent must not change
- A **target file** (`model_new.py`) where the agent writes its optimized model
- A **kernels directory** (`kernels/`) where all CUDA and binding source files live
- **Immutable build/test infrastructure** (`utils/`, `binding.cpp`, `binding_registry.h`) that the agent must not modify
- **Workflow rules** (`SKILL.md`) that constrain and guide agent decisions

Sources: [README.md:30-54](), [agent_workdir/SKILL.md:18-28]()

---

## Directory Structure

```
agent_workdir/
├── SKILL.md                  # Workflow rules for the agent (read-only by convention)
├── model.py                  # Baseline PyTorch model (DO NOT MODIFY)
├── model_new.py              # Agent-generated optimized model
├── binding_registry.h        # Binding registry singleton + REGISTER_BINDING macro (DO NOT MODIFY)
├── binding.cpp               # PYBIND11_MODULE entry point (DO NOT MODIFY)
├── kernels/
│   ├── axpby.cu              # Example: CUDA __global__ kernel + extern C launcher
│   └── axpby_binding.cpp     # Example: PyTorch wrapper + REGISTER_BINDING call
└── utils/
    ├── compile.sh            # Shell wrapper that times the build
    ├── compile.py            # Discovers sources, calls torch.utils.cpp_extension.load
    ├── verification.py       # Correctness check: ModelNew vs Model
    └── profiling.py          # Timing: baseline / torch.compile / cuda_extension
```

| File / Directory | Modifiable by Agent | Purpose |
|---|---|---|
| `SKILL.md` | No | Encodes workflow rules and optimization strategy |
| `model.py` | No | Immutable PyTorch baseline; provides reference outputs and weights |
| `model_new.py` | **Yes** | Agent's optimized model; delegates to `cuda_extension` |
| `binding_registry.h` | No | `BindingRegistry` singleton and `REGISTER_BINDING` macro |
| `binding.cpp` | No | `PYBIND11_MODULE` that calls `applyBindings()` at import |
| `kernels/*.cu` | **Yes** | CUDA kernel implementations (agent-authored) |
| `kernels/*_binding.cpp` | **Yes** | PyTorch tensor wrappers and `REGISTER_BINDING` calls |
| `utils/` | No | Build, verification, and profiling tools |

Sources: [agent_workdir/SKILL.md:18-28](), [README.md:36-44]()

---

## The Iterative Agent Loop

The agent follows a fixed five-step cycle. Each step produces artifacts consumed by the next.

**Diagram: The Iterative Loop — Files and Commands**

```mermaid
flowchart LR
    subgraph "Inputs (read-only)"
        skill["SKILL.md"]
        model_py["model.py"]
    end

    subgraph "Step 1: Generate"
        kernels_cu["kernels/*.cu"]
        kernels_bind["kernels/*_binding.cpp"]
        model_new["model_new.py"]
    end

    subgraph "Step 2: Compile"
        compile_sh["bash utils/compile.sh"]
        compile_py["utils/compile.py"]
        so["cuda_extension.so"]
        compile_sh -->|"python3 -m"| compile_py
        compile_py -->|"torch.utils.cpp_extension.load"| so
    end

    subgraph "Step 3: Verify"
        ver["python3 -m utils.verification"]
        result_v["PASS / FAIL + diff"]
        ver --> result_v
    end

    subgraph "Step 4: Profile"
        prof["python3 -m utils.profiling"]
        result_p["µs timings: baseline / torch.compile / cuda_extension"]
        prof --> result_p
    end

    skill -->|"constrains generation"| kernels_cu
    model_py -->|"reference"| ver
    model_py -->|"timing baseline"| prof

    kernels_cu --> compile_sh
    kernels_bind --> compile_sh
    so -->|"imported by"| model_new

    model_new --> ver
    model_new --> prof

    result_v -->|"correctness feedback"| kernels_cu
    result_p -->|"speedup feedback"| kernels_cu
```

Sources: [README.md:47-53](), [agent_workdir/SKILL.md:166-174]()

---

## File Dependency Graph

This diagram maps every file in the workspace to the files it depends on at build time and runtime.

**Diagram: Static File Dependencies in `agent_workdir`**

```mermaid
graph TD
    subgraph "Infrastructure (DO NOT MODIFY)"
        brh["binding_registry.h\nBindingRegistry + REGISTER_BINDING"]
        bcp["binding.cpp\nPYBIND11_MODULE cuda_extension\napplyBindings()"]
        bcp -->|"#include"| brh
    end

    subgraph "kernels/"
        axcu["axpby.cu\naxpby_kernel + axpby_launcher"]
        axbind["axpby_binding.cpp\naxpby_forward()\nREGISTER_BINDING(axpby, ...)"]
        axbind -->|"#include"| brh
        axbind -->|"extern C links"| axcu
    end

    subgraph "utils/ (DO NOT MODIFY)"
        csh["compile.sh"]
        cpy["compile.py\nglob *.cu + *.cpp\ncpp_extension.load"]
        ver["verification.py\ncheck_equal + block_torch_functional"]
        pro["profiling.py\nbenchmark_model"]
        csh -->|"invokes"| cpy
    end

    subgraph "Models"
        mpy["model.py\nModel (baseline)"]
        mnew["model_new.py\nModelNew (optimized)"]
    end

    cpy -->|"compiles"| bcp
    cpy -->|"compiles"| axcu
    cpy -->|"compiles"| axbind
    bcp & axcu & axbind -->|"produces"| so["cuda_extension.so"]
    so -->|"import cuda_extension"| mnew

    mpy -->|"state_dict + reference output"| ver
    mnew -->|"forward pass"| ver
    mpy -->|"timing baseline"| pro
    mnew -->|"timed forward"| pro
```

Sources: [README.md:36-44](), [agent_workdir/SKILL.md:18-28]()

---

## Common Commands

All three commands are run from inside the `agent_workdir` directory.

| Command | Purpose |
|---|---|
| `bash utils/compile.sh` | Compile all `*.cu` and `*_binding.cpp` sources into `cuda_extension.so` |
| `python3 -m utils.verification` | Run correctness check comparing `ModelNew` against `Model` |
| `python3 -m utils.profiling` | Benchmark `Model`, `torch.compile(Model)`, and `ModelNew` |

An optional `TORCH_CUDA_ARCH_LIST` environment variable can be passed to target a specific GPU architecture:

```
TORCH_CUDA_ARCH_LIST=9.0 bash utils/compile.sh
```

Sources: [README.md:47-53](), [agent_workdir/SKILL.md:166-174]()

---

## Agent Modification Boundaries

The workspace enforces a strict separation between infrastructure (never touched) and agent work areas.

**Diagram: What the Agent May and May Not Modify**

```mermaid
flowchart TD
    subgraph "FORBIDDEN — Agent must not modify"
        binding_cpp["binding.cpp"]
        binding_registry_h["binding_registry.h"]
        utils_dir["utils/ (compile.sh, compile.py, verification.py, profiling.py)"]
        model_py2["model.py"]
    end

    subgraph "AGENT WORK AREA"
        kernels_cu2["kernels/*.cu\nCUDA __global__ kernels + extern C launchers"]
        kernels_bind2["kernels/*_binding.cpp\nPyTorch wrappers + REGISTER_BINDING"]
        model_new2["model_new.py\nModelNew class"]
    end

    kernels_cu2 -->|"registered via"| binding_registry_h
    kernels_bind2 -->|"registered via"| binding_registry_h
    binding_registry_h -->|"used by"| binding_cpp
    binding_cpp -->|"builds"| so2["cuda_extension.so"]
    so2 -->|"imported by"| model_new2
    model_py2 -->|"reference for"| utils_dir
    model_new2 -->|"evaluated by"| utils_dir
```

Sources: [agent_workdir/SKILL.md:5-16](), [agent_workdir/SKILL.md:362-372]()

---

## Key Invariants

The workspace enforces several invariants that the agent (and any contributor) must maintain:

1. **`model.py` is read-only.** It provides the reference forward pass and the weight initialization used to seed `ModelNew`.
2. **`ModelNew` constructor signature must match `Model`.** Both are instantiated via `get_init_inputs()` return values; the `state_dict` from `Model` is loaded directly into `ModelNew`.
3. **No `torch.*` operators in C++ files.** All CUDA bindings use raw pointers and call through `extern "C"` launchers. `torch::*` and `torch::nn::functional::*` are forbidden in `.cu` and `_binding.cpp` files.
4. **No `torch` operations in `model_new.py` forward pass.** Only tensor creation helpers and calls to `cuda_extension.*` functions are allowed.
5. **`utils/`, `binding.cpp`, `binding_registry.h` are never modified.** Kernel authors only add files to `kernels/`.
6. **The minimum performance target is 5% faster than `torch.compile` baseline.**

Sources: [agent_workdir/SKILL.md:5-16](), [agent_workdir/SKILL.md:349-363]()

---

