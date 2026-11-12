<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/original_performance_takehome · page 8 Developer Reference · fetched 2026-10-26 -->

# Developer Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perf_takehome.py](perf_takehome.py)
- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page provides reference documentation for developers working with or extending the codebase. It covers repository structure, key API components, and development environment setup.

For detailed information about the optimization challenge, see [The Optimization Challenge](#2). For detailed machine architecture documentation, see [Machine Architecture](#4). For testing infrastructure, see [Testing Framework](#6).

## Repository Structure

The repository is organized with core implementation files at the root and tests in a subdirectory:

```mermaid
graph TB
    Root["/"]
    Root --> PerfTakehome["perf_takehome.py<br/>KernelBuilder & Tests"]
    Root --> Problem["problem.py<br/>Machine & Reference Kernels"]
    Root --> FrozenProblem["frozen_problem.py<br/>Frozen Simulator for Testing"]
    Root --> WatchTracePy["watch_trace.py<br/>Trace Server"]
    Root --> WatchTraceHTML["watch_trace.html<br/>Web Interface"]
    Root --> Readme["Readme.md<br/>Documentation"]
    Root --> GitIgnore[".gitignore<br/>Git Configuration"]
    Root --> TestsDir["tests/"]
    TestsDir --> SubmissionTests["submission_tests.py<br/>Official Test Suite"]
    
    style PerfTakehome fill:#f9f9f9
    style Problem fill:#f9f9f9
    style SubmissionTests fill:#f9f9f9
```

**Sources:** [perf_takehome.py:1-273](), [problem.py:1-569](), [.gitignore:1-5]()

### Core Files

| File | Purpose | Key Components |
|------|---------|----------------|
| `perf_takehome.py` | Optimization target and development tests | `KernelBuilder`, `do_kernel_test()`, `BASELINE` |
| `problem.py` | Machine simulator and problem definition | `Machine`, `Tree`, `Input`, `reference_kernel()`, `reference_kernel2()` |
| `frozen_problem.py` | Frozen simulator copy for fair testing | Identical to `problem.py` but used by official tests |
| `watch_trace.py` | Local HTTP server for trace visualization | HTTP server on port 8000, proxies Perfetto UI |
| `watch_trace.html` | Web interface for trace viewing | Auto-reload functionality, Perfetto integration |
| `tests/submission_tests.py` | Official correctness and performance tests | `CorrectnessTests`, `SpeedTests` classes |

**Sources:** [perf_takehome.py:1-17](), [problem.py:1-6](), [tests/frozen_problem.py:1-6]()

### File Relationships

```mermaid
graph LR
    SubmissionTests["tests/submission_tests.py"]
    PerfTakehome["perf_takehome.py"]
    FrozenProblem["tests/frozen_problem.py"]
    Problem["problem.py"]
    WatchTrace["watch_trace.py + .html"]
    
    SubmissionTests -->|"imports from"| FrozenProblem
    SubmissionTests -->|"imports KernelBuilder from"| PerfTakehome
    PerfTakehome -->|"imports from"| Problem
    FrozenProblem -->|"frozen copy of"| Problem
    Problem -->|"generates trace.json"| WatchTrace
    WatchTrace -->|"serves"| TraceJSON["trace.json"]
    
    style PerfTakehome fill:#f9f9f9
    style FrozenProblem fill:#f9f9f9
```

**Sources:** [perf_takehome.py:23-37](), [tests/frozen_problem.py:4-6]()

## API Reference

### Core Classes

#### Machine

The VLIW SIMD simulator that executes generated instruction sequences.

```mermaid
graph TB
    Machine["Machine"]
    Machine --> Init["__init__(<br/>mem_dump,<br/>program,<br/>debug_info,<br/>n_cores=1,<br/>trace=False)"]
    Machine --> Run["run()"]
    Machine --> Step["step(instr, core)"]
    Machine --> Engines["Engine Methods"]
    
    Engines --> ALU["alu(core, op, dest, a1, a2)"]
    Engines --> VALU["valu(core, *slot)"]
    Engines --> Load["load(core, *slot)"]
    Engines --> Store["store(core, *slot)"]
    Engines --> Flow["flow(core, *slot)"]
    
    Machine --> State["State"]
    State --> Cores["cores: list[Core]"]
    State --> Mem["mem: list[int]"]
    State --> Cycle["cycle: int"]
    State --> Program["program: list[Instruction]"]
```

**Location:** [problem.py:64-403]()

**Key Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `cores` | `list[Core]` | List of `Core` objects tracking per-core state |
| `mem` | `list[int]` | Main memory (flat array of 32-bit words) |
| `program` | `list[Instruction]` | List of VLIW instruction bundles |
| `cycle` | `int` | Current execution cycle count |
| `debug_info` | `DebugInfo` | Mapping data for trace naming |

**Key Methods:**
| Method | Parameters | Description |
|--------|------------|-------------|
| `run()` | None | Execute until all cores reach `STOPPED` or `PAUSED` |
| `step(instr, core)` | `Instruction`, `Core` | Execute one VLIW bundle on a specific core |
| `alu(...)` | Core, Op, Dest, A1, A2 | Execute scalar arithmetic/logic |
| `valu(...)` | Core, *slot | Execute vector SIMD operations |
| `load(...)` | Core, *slot | Execute memory-to-scratch transfers |
| `store(...)` | Core, *slot | Execute scratch-to-memory transfers |

**Sources:** [problem.py:64-118](), [problem.py:197-254]()

#### KernelBuilder

Generates instruction sequences for the machine. This is the primary optimization target.

```mermaid
graph TB
    KernelBuilder["KernelBuilder"]
    KernelBuilder --> Init["__init__()"]
    KernelBuilder --> BuildKernel["build_kernel(<br/>forest_height,<br/>n_nodes,<br/>batch_size,<br/>rounds)"]
    KernelBuilder --> Helpers["Helper Methods"]
    
    Helpers --> AllocScratch["alloc_scratch(name, length)"]
    Helpers --> ScratchConst["scratch_const(val, name)"]
    Helpers --> BuildHash["build_hash(val_hash_addr, tmp1, tmp2, round, i)"]
    Helpers --> Build["build(slots, vliw)"]
    Helpers --> Add["add(engine, slot)"]
    
    KernelBuilder --> State["State"]
    State --> Instrs["instrs: list[Instruction]"]
    State --> Scratch["scratch: dict[str, int]"]
    State --> ScratchPtr["scratch_ptr: int"]
    State --> ConstMap["const_map: dict[int, int]"]
```

**Location:** [perf_takehome.py:40-175]()

**Key Methods:**
| Method | Parameters | Description |
|--------|------------|-------------|
| `build_kernel(...)` | height, nodes, batch, rounds | The core optimization target |
| `alloc_scratch(name, length)` | str, int | Reserves scratch space and returns the base address |
| `scratch_const(val, name)` | int, str | Allocates or retrieves a scratch location for a constant |
| `build_hash(...)` | addr, tmp1, tmp2, r, i | Generates the `HASH_STAGES` instruction slots |
| `add(engine, slot)` | Engine, tuple | Appends a single-engine instruction bundle |

**Sources:** [perf_takehome.py:40-175]()

#### Core

Represents the state of a single core in the machine.

**Location:** [problem.py:25-31]()

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Core identifier |
| `scratch` | `list[int]` | Fast per-core memory (size: `SCRATCH_SIZE`) |
| `pc` | `int` | Program counter |
| `state` | `CoreState` | `RUNNING`, `PAUSED`, or `STOPPED` |

**Sources:** [problem.py:18-31]()

### Key Constants

```mermaid
graph LR
    Constants["Constants"]
    
    Constants --> SlotLimits["SLOT_LIMITS<br/>alu: 12<br/>valu: 6<br/>load: 2<br/>store: 2<br/>flow: 1<br/>debug: 64"]
    Constants --> VLEN["VLEN = 8<br/>Vector Length"]
    Constants --> NCores["N_CORES = 1<br/>Number of Cores"]
    Constants --> ScratchSize["SCRATCH_SIZE = 1536<br/>Per-Core Scratch Words"]
    Constants --> Baseline["BASELINE = 147734<br/>Unoptimized Cycle Count"]
    Constants --> HashStages["HASH_STAGES<br/>6 stages of hash function"]
```

**Sources:** [problem.py:48-62](), [perf_takehome.py:176]()

#### Engine Slot Limits

Defined in `SLOT_LIMITS` dictionary at [problem.py:48-55]():

| Engine | Slots Per Cycle | Description |
|--------|-----------------|-------------|
| `alu` | 12 | Scalar ALU operations |
| `valu` | 6 | Vector SIMD operations |
| `load` | 2 | Concurrent load operations |
| `store` | 2 | Concurrent store operations |
| `flow` | 1 | Branching/Flow control |

**Sources:** [problem.py:48-55]()

### Key Functions

#### reference_kernel2()

Reference implementation operating on flat memory, used for correctness validation.

**Location:** [problem.py:535-568]()

**Signature:**
```python
def reference_kernel2(mem: list[int], trace: dict[Any, int] = {}) -> Generator[list[int], None, None]
```

Yields memory state at each `pause` point. Populates `trace` dict with intermediate values for debugging.

**Sources:** [problem.py:535-568]()

#### build_mem_image()

Serializes `Tree` and `Input` into flat memory layout.

**Location:** [problem.py:487-513]()

**Signature:**
```python
def build_mem_image(t: Tree, inp: Input) -> list[int]
```

**Memory Layout Header:**
| Offset | Content |
|--------|---------|
| 0 | `rounds` |
| 1 | `n_nodes` |
| 2 | `batch_size` |
| 3 | `forest_height` |
| 4 | `forest_values_p` (Pointer) |
| 5 | `inp_indices_p` (Pointer) |
| 6 | `inp_values_p` (Pointer) |

**Sources:** [problem.py:487-513]()

## Configuration and Development Setup

### Git Configuration

The `.gitignore` file excludes development artifacts and bytecode:

**Location:** [.gitignore:1-5]()

```
trace.json
**/*.pyc
.hypothesis
.DS_Store
```

### Development Workflow

```mermaid
graph TB
    Start["Development Start"]
    Start --> Modify["Modify KernelBuilder.build_kernel()"]
    Modify --> RunLocal["Run Local Tests<br/>python perf_takehome.py"]
    RunLocal --> CheckTrace{"Need Trace?"}
    
    CheckTrace -->|Yes| GenTrace["Run test_kernel_trace<br/>python perf_takehome.py Tests.test_kernel_trace"]
    GenTrace --> WatchServer["Start watch_trace.py<br/>python watch_trace.py"]
    WatchServer --> ViewTrace["Open Browser<br/>Click 'Open Perfetto'"]
    ViewTrace --> Analyze["Analyze Performance<br/>in Perfetto UI"]
    Analyze --> Modify
    
    CheckTrace -->|No| CheckCorrect{"Correct?"}
    CheckCorrect -->|No| Debug["Debug Failures"]
    Debug --> Modify
    
    CheckCorrect -->|Yes| RunSubmission["Run Submission Tests<br/>python tests/submission_tests.py"]
```

**Sources:** [perf_takehome.py:1-17](), [problem.py:151-160]()

### Module Import Structure

```mermaid
graph TB
    SubmissionTests["tests/submission_tests.py"]
    PerfTakehome["perf_takehome.py"]
    Problem["problem.py"]
    FrozenProblem["tests/frozen_problem.py"]
    
    PerfTakehome -->|imports| Problem
    SubmissionTests -->|imports| FrozenProblem
    SubmissionTests -->|imports| PerfTakehome
    
    style PerfTakehome fill:#f9f9f9
    style FrozenProblem fill:#f9f9f9
```

**Import Pattern:**
- `perf_takehome.py` imports from `problem.py` for development. [perf_takehome.py:23-37]()
- `tests/submission_tests.py` imports from `frozen_problem.py` for final validation.

For details, see [Repository Structure](#8.1), [API Reference](#8.2), and [Configuration and Development Setup](#8.3).

---

