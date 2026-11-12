# Page: Introduction and Overview

# Introduction and Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Readme.md](Readme.md)
- [perf_takehome.py](perf_takehome.py)

</details>



This document provides a high-level introduction to the performance optimization benchmark repository. It explains the system's purpose, architecture, and key concepts needed to begin optimization work.

For detailed instructions on running tests and beginning optimization, see [Quick Start Guide](#1.2). For comprehensive architectural details, see [System Architecture Overview](#1.3). For specific information about optimizing the kernel, see [Kernel Builder - The Optimization Target](#5).

## Purpose and Scope

This repository implements a **performance optimization benchmark** for a custom VLIW SIMD machine architecture. The system is used for:

| Use Case | Description |
|----------|-------------|
| **AI Code Generation Evaluation** | Testing code generation capabilities of models like Claude Opus 4.5 |
| **Performance Engineering Recruitment** | Identifying skilled optimizers who achieve sub-1487 cycle performance |
| **Educational Tool** | Teaching compiler optimization techniques for parallel architectures |
| **Research Platform** | Studying optimization strategies for VLIW SIMD systems |

The core challenge is to optimize instruction generation in the `KernelBuilder.build_kernel` method to minimize cycle count on a frozen simulator while maintaining correctness.

**Sources:** [Readme.md:1-21](), [perf_takehome.py:8-14]()

## System Overview

The repository consists of three primary layers:

```mermaid
graph TB
    subgraph Input["Problem Definition Layer (problem.py)"]
        Tree["Tree<br/>(problem.py:406-418)"]
        InputData["Input<br/>(problem.py:422-436)"]
        RefKernel["reference_kernel2()<br/>(problem.py:535-568)"]
    end
    
    subgraph Optimization["Optimization Layer (perf_takehome.py)"]
        KB["KernelBuilder Class<br/>(perf_takehome.py:40-175)"]
        BuildKernel["build_kernel()<br/>(perf_takehome.py:88-175)"]
        Instructions["list[dict[Engine, list]]<br/>VLIW Bundles"]
    end
    
    subgraph Execution["Execution & Validation Layer"]
        Machine["Machine Simulator<br/>(problem.py:64-402)"]
        DoTest["do_kernel_test()<br/>(perf_takehome.py:178-225)"]
        SubmissionTests["submission_tests.py"]
    end
    
    Tree --> KB
    InputData --> KB
    KB --> BuildKernel
    BuildKernel --> Instructions
    Instructions --> Machine
    Machine --> DoTest
    RefKernel --> DoTest
    DoTest --> SubmissionTests
    
    style KB stroke-width:3px
    style BuildKernel stroke-width:3px
```

**Diagram: Core System Components and Data Flow**

The optimization target is `KernelBuilder.build_kernel`, which generates instruction sequences executed by the `Machine` simulator. Correctness is validated against `reference_kernel2`, and performance is measured in cycle count.

**Sources:** [perf_takehome.py:40-175](), [problem.py:64-402](), [problem.py:535-568]()

## Key Concepts

### VLIW SIMD Architecture

The system simulates a custom architecture with two key features:

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **VLIW** (Very Long Instruction Word) | Multiple operations execute in parallel per cycle, organized into engines with slot limits | `SLOT_LIMITS` dict in [problem.py:48-55]() |
| **SIMD** (Single Instruction Multiple Data) | Vector operations process multiple elements simultaneously | `VLEN = 8` in [problem.py:57]() |

```mermaid
graph LR
    subgraph Instruction["Instruction Bundle = dict[Engine, list[tuple]]"]
        ALU["alu Engine<br/>12 slots<br/>Scalar arithmetic"]
        VALU["valu Engine<br/>6 slots<br/>Vector ops"]
        LOAD["load Engine<br/>2 slots<br/>Mem -> Scratch"]
        STORE["store Engine<br/>2 slots<br/>Scratch -> Mem"]
        FLOW["flow Engine<br/>1 slot<br/>Control/Pause"]
    end
    
    subgraph MemoryHierarchy["Memory Hierarchy"]
        MainMem["Machine.mem: list[int]<br/>Flat Main Memory"]
        Scratch["Core.scratch: list[int]<br/>Fast Registers<br/>SCRATCH_SIZE=1536"]
    end
    
    LOAD -.-> MainMem
    LOAD -.-> Scratch
    STORE -.-> Scratch
    STORE -.-> MainMem
    ALU -.-> Scratch
    VALU -.-> Scratch
```

**Diagram: Machine Architecture Components**

Each `Instruction` is a dictionary mapping `Engine` types to lists of operation tuples. The `Machine.step` method executes all slots in parallel within a single cycle using a two-phase commit model (read all inputs, then write all outputs).

**Sources:** [problem.py:14-15](), [problem.py:48-55](), [problem.py:57-60](), [problem.py:64-96](), [problem.py:352-397]()

### The Computational Problem

The kernel implements a parallel tree traversal algorithm with a custom hash function:

```mermaid
flowchart TD
    Start["For each round & batch item:<br/>idx, val from Input"]
    Load["node_val = Tree.values[idx]"]
    XOR["val = val ^ node_val"]
    Hash["val = myhash(val)<br/>(HASH_STAGES)"]
    Branch["idx = 2*idx + (1 if val%2==0 else 2)"]
    Wrap["idx = 0 if idx >= n_nodes else idx"]
    Store["Update Input indices & values"]
    
    Start --> Load
    Load --> XOR
    XOR --> Hash
    Hash --> Branch
    Branch --> Wrap
    Wrap --> Store
```

**Diagram: Tree Traversal Algorithm Flow**

The `myhash` function applies six stages of bitwise operations defined in the `HASH_STAGES` constant. The reference implementation is provided in `reference_kernel` and `reference_kernel2`.

**Sources:** [problem.py:439-464](), [problem.py:467-484](), [problem.py:535-568]()

## System Components

### Core Classes and Functions

| Component | Location | Purpose |
|-----------|----------|---------|
| `KernelBuilder` | [perf_takehome.py:40-175]() | Generates instruction sequences (**OPTIMIZATION TARGET**) |
| `Machine` | [problem.py:64-402]() | VLIW SIMD simulator that executes instructions |
| `Tree` | [problem.py:406-418]() | Implicit balanced binary tree data structure |
| `Input` | [problem.py:422-436]() | Batch of indices and values for processing |
| `reference_kernel2` | [problem.py:535-568]() | Ground truth implementation for validation |
| `do_kernel_test` | [perf_takehome.py:178-225]() | Test harness that runs and validates kernels |
| `build_mem_image` | [problem.py:487-513]() | Serializes Tree and Input into flat memory layout |

**Sources:** [perf_takehome.py:40-175](), [problem.py:64-402](), [problem.py:406-436](), [problem.py:487-568](), [perf_takehome.py:178-225]()

### File Structure

```
.
├── perf_takehome.py       # KernelBuilder and local tests (MAIN WORKSPACE)
├── problem.py             # Machine simulator, data structures, reference kernels
├── frozen_problem.py      # Frozen simulator for official submission testing
├── watch_trace.py         # HTTP server for trace visualization
├── watch_trace.html       # Web UI for Perfetto integration
└── tests/
    └── submission_tests.py  # Official test suite with performance thresholds
```

**Sources:** [perf_takehome.py:1-20](), [problem.py:1-20](), [Readme.md:25-39]()

## Performance Benchmarks

Performance is measured in clock cycles from the simulated machine. The benchmark suite establishes a performance ladder:

| Cycles | Description | Speedup |
|--------|-------------|---------|
| 147,734 | `BASELINE` - Unoptimized scalar starting point | 1.0× |
| 18,532 | Starter point for the 2-hour version | 7.97× |
| 2,164 | Claude Opus 4 after many hours | 68.3× |
| 1,790 | Claude Opus 4.5 casual session (≈ best human 2hr) | 82.5× |
| 1,579 | Claude Opus 4.5 after 2 hours in harness | 93.5× |
| 1,548 | Claude Sonnet 4.5 after many hours | 95.4× |
| **1,487** | **Claude Opus 4.5 at launch (RECRUITMENT GATE)** | **99.3×** |
| 1,363 | Claude Opus 4.5 with improved harness (best known) | 108.4× |

Run `python tests/submission_tests.py` to see which thresholds you pass. Achieving sub-1487 cycle performance qualifies for contacting Anthropic recruiting.

**Sources:** [Readme.md:9-21](), [perf_takehome.py:176]()

## Development Workflow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant KB as KernelBuilder.build_kernel
    participant Machine as Machine.run
    participant Ref as reference_kernel2
    participant Test as do_kernel_test
    
    Dev->>KB: Modify instruction generation
    Dev->>Test: Run python tests/submission_tests.py
    Test->>KB: Call build_kernel(height, nodes, batch, rounds)
    KB-->>Test: Return instrs: list[Instruction]
    Test->>Machine: Initialize Machine(mem, instrs)
    Test->>Machine: Execute run()
    Machine-->>Test: Return cycle count, updated mem
    Test->>Ref: Generate expected mem
    Ref-->>Test: Yield expected mem states
    Test->>Test: Validate mem[inp_values_p:] matches
    Test-->>Dev: Report cycles and correctness
```

**Diagram: Optimization Development Workflow**

The `Machine` class in `problem.py` is the development simulator, while `frozen_problem.py` (identical code) is used by submission tests to ensure integrity.

**Sources:** [perf_takehome.py:178-225](), [problem.py:64-402](), [problem.py:535-568]()

## Trace Visualization

For performance debugging, the system includes trace generation and visualization:

| Component | Purpose |
|-----------|---------|
| `Machine(trace=True)` | Generates `trace.json` in Chrome Trace Event Format |
| `watch_trace.py` | Local HTTP server on port 8000 for serving traces |
| `watch_trace.html` | Browser UI with live-reload and Perfetto integration |
| Perfetto UI | Professional performance visualization at `ui.perfetto.dev` |

To use: Run a test that enables tracing, then `python watch_trace.py` in another terminal. The browser will open with automatic trace reloading.

**Sources:** [problem.py:118-120](), [problem.py:151-196](), [perf_takehome.py:244-247]()

## Next Steps

- **To get started immediately:** See [Quick Start Guide](#1.2)
- **To understand the problem in detail:** See [The Tree Traversal Problem](#2.1)
- **To learn the machine architecture:** See [Machine Architecture](#4)
- **To begin optimization:** See [Kernel Builder - The Optimization Target](#5)

The key optimization target is the `build_kernel` method at [perf_takehome.py:88-175](). The current implementation generates one instruction bundle per operation using only scalar ALU and load/store engines. Significant performance gains are possible through VLIW packing and SIMD vectorization.

**Sources:** [perf_takehome.py:88-175](), [perf_takehome.py:51-56]()

---

# Page: What is This Repository

# What is This Repository

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Readme.md](Readme.md)

</details>



This document explains the purpose and scope of this repository, its intended audiences, and what constitutes success when using it. For technical details about how to run your first test, see [Quick Start Guide](1.2). For comprehensive architecture information, see [System Architecture Overview](1.3).

## Purpose and Scope

This repository contains **Anthropic's original performance take-home challenge**: a compiler optimization benchmark for a custom VLIW SIMD machine simulator. The repository serves three distinct purposes:

1. **AI Code Generation Benchmark** - Evaluates AI models' ability to optimize low-level systems code. [Readme.md:1-5]()
2. **Recruitment Tool** - Identifies exceptional performance engineers who can beat state-of-the-art AI. [Readme.md:21-21]()
3. **Educational Platform** - Teaches compiler optimization for parallel architectures.

The challenge is **frozen** - the simulator implementation at [frozen_problem.py:1-500]() cannot be modified, ensuring fair comparison across all submissions. [Readme.md:27-34]()

---

## The Core Challenge

Your task is to optimize the `KernelBuilder.build_kernel()` method in [perf_takehome.py:46-56]() to generate efficient instruction sequences for a parallel tree traversal computation.

### Challenge Flow

```mermaid
graph TB
    You["Developer/AI Model"]
    KB["KernelBuilder.build_kernel()<br/>(perf_takehome.py)"]
    Test["submission_tests.py"]
    Sim["Machine Simulator<br/>(frozen_problem.py)"]
    Result["Performance Result<br/>(cycle count)"]
    
    You -->|"Modify optimization logic"| KB
    KB -->|"Generates instructions"| Test
    Test -->|"Executes on frozen simulator"| Sim
    Sim -->|"Returns cycle count"| Result
    Result -->|"Compare vs thresholds"| You
    
    Test -->|"Validates correctness vs"| RefKernel["reference_kernel2()"]
```

**Sources:** [Readme.md:1-21](), [tests/submission_tests.py:1-120](), [perf_takehome.py:46-56]()

---

## Three Audiences, Three Goals

### Audience 1: AI Models Being Evaluated

AI models (like Claude Opus 4.5) attempt to optimize [perf_takehome.py:KernelBuilder]() through iterative refinement in a test-time compute harness. [Readme.md:3-7]()

**Success Metric:** Cycle count achieved after N hours of computation time.

```mermaid
graph LR
    Model["AI Model"]
    Harness["Test-Time Compute Harness"]
    Iterations["Iterative Code Generation"]
    Cycles["Final Cycle Count"]
    
    Model --> Harness
    Harness --> Iterations
    Iterations -->|"Many hours"| Cycles
```

**Sources:** [Readme.md:3-17]()

### Audience 2: Human Performance Engineers (Recruitment)

Exceptional optimizers who beat the **1487-cycle threshold** (Claude Opus 4.5's best performance at launch) are invited to contact `performance-recruiting@anthropic.com`. [Readme.md:21-21]()

**Success Metric:** Achieve `< 1487 cycles` on the standard test case `(forest_height=10, rounds=16, batch_size=256)`. [tests/submission_tests.py:109-111]()

**How to Verify:**
```bash
python tests/submission_tests.py
```

The test suite at [tests/submission_tests.py:109-111]() explicitly checks this threshold:
```python
def test_opus45_11hr(self):
    # Claude Opus 4.5 after 11.5 hours in the harness
    assert cycles() < 1487
```

**Sources:** [Readme.md:18-21](), [tests/submission_tests.py:109-111]()

### Audience 3: Students and Learners

Those interested in learning compiler optimization, VLIW architectures, and performance engineering techniques.

**Success Metric:** Progressive improvement through the performance ladder (see next section).

---

## The Performance Ladder

The repository defines a stratified benchmark suite with progressively aggressive targets. All benchmarks are measured in clock cycles from the simulated machine. [Readme.md:9-11]()

| Threshold | Cycles | Speedup | Achievement |
|-----------|--------|---------|-------------|
| **Baseline** | 147,734 | 1.0x | Starting point (unoptimized) |
| **Updated Starting Point** | 18,532 | 7.97x | Newer take-home starting code |
| **Claude Opus 4 (many hours)** | 2,164 | 68.3x | First AI success in harness |
| **Claude Opus 4.5 (casual)** | 1,790 | 82.5x | ≈ Best human 2hr performance |
| **Claude Opus 4.5 (2hr harness)** | 1,579 | 93.5x | Test-time compute (2 hours) |
| **Claude Sonnet 4.5 (many hours)** | 1,548 | 95.4x | Extended compute |
| **🎯 RECRUITMENT GATE** | **1,487** | **99.3x** | **Opus 4.5 after 11.5 hours** |
| **Best AI (improved harness)** | 1,363 | 108.4x | Claude Opus 4.5 optimized |

**Sources:** [Readme.md:13-18](), [tests/submission_tests.py:76-116]()

### How Testing Works

The test function [tests/submission_tests.py:30-54]() measures performance:

```mermaid
graph TB
    Test["do_kernel_test(10, 16, 256)"]
    Gen["Generate random Tree & Input"]
    Build["KernelBuilder.build_kernel()"]
    Machine["Machine(mem, instrs)"]
    Run["machine.run()"]
    Validate["Compare vs reference_kernel2"]
    Cycles["Return machine.cycle"]
    
    Test --> Gen
    Gen --> Build
    Build --> Machine
    Machine --> Run
    Run --> Validate
    Validate --> Cycles
```

The `do_kernel_test()` function:
1. Generates random test data with `Tree.generate(10)` and `Input.generate()` [tests/submission_tests.py:34-36]()
2. Builds instruction sequence via `KernelBuilder.build_kernel()` [tests/submission_tests.py:38-38]()
3. Executes on `Machine` simulator from [frozen_problem.py:273-273]()
4. Validates correctness against `reference_kernel2()` [tests/submission_tests.py:46-46]()
5. Returns cycle count [tests/submission_tests.py:54-54]()

**Sources:** [tests/submission_tests.py:30-54](), [frozen_problem.py:273-300]()

---

## Repository Structure at a Glance

```mermaid
graph TB
    subgraph "Your Optimization Target"
        PerfTH["perf_takehome.py<br/>KernelBuilder class"]
    end
    
    subgraph "Testing Infrastructure"
        SubTests["tests/submission_tests.py<br/>CorrectnessTests<br/>SpeedTests"]
    end
    
    subgraph "Frozen Simulator (Cannot Modify)"
        FrozenProb["frozen_problem.py<br/>Machine<br/>reference_kernel2<br/>Tree, Input"]
    end
    
    subgraph "Supporting Tools"
        WatchTrace["watch_trace.py<br/>Trace visualization server"]
        WatchHTML["watch_trace.html<br/>Browser interface"]
    end
    
    PerfTH -->|"generates instructions"| SubTests
    SubTests -->|"executes on"| FrozenProb
    SubTests -->|"optional: enable tracing"| WatchTrace
    WatchTrace --> WatchHTML
```

**Key Files:**
- **[perf_takehome.py]()** - Your optimization target (`KernelBuilder` class). [perf_takehome.py:8-10]()
- **[frozen_problem.py]()** - Frozen simulator (cannot modify). [frozen_problem.py:273-273]()
- **[tests/submission_tests.py]()** - Validation and benchmarking. [tests/submission_tests.py:1-5]()
- **[watch_trace.py]()** - Performance visualization server. [watch_trace.py:1-10]()
- **[Readme.md]()** - Instructions and performance benchmarks. [Readme.md:1-5]()

**Sources:** [Readme.md:1-21](), [perf_takehome.py:8-10](), [tests/submission_tests.py:1-5]()

---

## What Success Looks Like

### Tier 1: Functional Correctness
Pass `CorrectnessTests` in [tests/submission_tests.py:57-60]():
```python
def test_kernel_correctness(self):
    for i in range(8):
        do_kernel_test(10, 16, 256)
```
Your generated instructions must produce identical results to `reference_kernel2()`. [tests/submission_tests.py:46-46]()

### Tier 2: Basic Optimization
Beat the baseline: `cycles() < 147734` ([tests/submission_tests.py:85-86]())

### Tier 3: Professional Performance
Beat updated starting point: `cycles() < 18532` ([tests/submission_tests.py:88-90]()). This corresponds to the starting point of the 2-hour version of the take-home. [Readme.md:5-5]()

### Tier 4: Expert Optimization
Beat AI models in the ladder (1790 → 1579 → 1548 cycles). [Readme.md:13-16]()

### Tier 5: 🎯 Recruitment Threshold
**`cycles() < 1487`** - Beat Claude Opus 4.5's best performance after 11.5 hours in the harness. [Readme.md:17-17]()
- Email `performance-recruiting@anthropic.com` with your code. [Readme.md:21-21]()
- Include resume for interview consideration.

### Tier 6: State-of-the-Art
Beat the best AI performance: `cycles() < 1363` ([tests/submission_tests.py:113-115]()). [Readme.md:18-18]()

**Sources:** [Readme.md:18-21](), [tests/submission_tests.py:76-116]()

---

## Why This Problem is Interesting

The challenge tests three critical skills:

1. **Instruction-Level Parallelism** - The VLIW architecture exposes parallelism explicitly via multiple engine slots (alu, valu, load, store, flow); you must pack operations efficiently. [frozen_problem.py:348-354]()
2. **Memory Hierarchy Optimization** - Understanding the two-tier memory model (main memory + scratch space) is crucial. [frozen_problem.py:302-315]()
3. **Algorithmic Insight** - The tree traversal problem (with HASH_STAGES=16) has structure that can be exploited via vectorization. [frozen_problem.py:10-15]()

**Warning:** Multicore is disabled intentionally (`N_CORES = 1`). Attempting to enable multicore or modifying the `tests/` folder constitutes an invalid solution. [Readme.md:39-40]()

**Sources:** [Readme.md:39-40](), [frozen_problem.py:10-15](), [frozen_problem.py:348-354]()

---

# Page: Quick Start Guide

# Quick Start Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Readme.md](Readme.md)
- [tests/submission_tests.py](tests/submission_tests.py)

</details>



This guide walks you through running your first performance test within minutes of cloning the repository. You'll learn how to execute the test suite, interpret cycle count results, and understand the performance benchmarks that define success.

For detailed information about the optimization challenge itself, see **2. The Optimization Challenge**. For comprehensive system architecture, see **1.3. System Architecture Overview**.

## Prerequisites

**Dependencies**: This repository requires Python 3.x with no external dependencies. All required modules are part of the Python standard library.

**Repository Structure**: Clone the repository and verify you have these key files:
- `perf_takehome.py`: Contains the `KernelBuilder` class you'll optimize [[perf_takehome.py:85-87]]().
- `tests/submission_tests.py`: Official test suite for performance validation [[tests/submission_tests.py:1-20]]().
- `problem.py`: Development simulator (mutable).
- `frozen_problem.py`: Frozen simulator used for testing to ensure a stable environment [[tests/submission_tests.py:11-19]]().

Sources: [Readme.md:1-21](), [perf_takehome.py:1-14](), [tests/submission_tests.py:1-20]()

## Running Your First Test

### Quick Start: Submission Tests

The fastest way to see where you stand is to run the official submission test suite:

```bash
python tests/submission_tests.py
```

This command executes both correctness validation and performance benchmarking against the frozen simulator defined in `frozen_problem.py`.

### Alternative: Development Tests

For iterative development with more detailed output, you can run the main file directly:

```bash
python perf_takehome.py
```

Or run a specific test method within the `Tests` class:

```bash
python perf_takehome.py Tests.test_kernel_cycles
```

**Diagram: Test Execution Flow**

```mermaid
flowchart TD
    User["User runs<br/>python tests/submission_tests.py"]
    
    subgraph "Test_Initialization"
        Correct["CorrectnessTests.test_kernel_correctness<br/>8 randomized runs"]
        Speed["SpeedTests<br/>8 threshold tests"]
    end
    
    subgraph "Per_Test_Execution"
        DoTest["do_kernel_test()<br/>forest_height=10<br/>rounds=16<br/>batch_size=256"]
        GenData["Tree.generate()<br/>Input.generate()"]
        BuildMem["build_mem_image()"]
        GetKB["kernel_builder()<br/>@lru_cache"]
        CreateMachine["Machine(mem, instrs, debug_info)"]
        Run["machine.run()"]
        Validate["Compare vs reference_kernel2()"]
    end
    
    User --> Correct
    User --> Speed
    Correct --> DoTest
    Speed --> DoTest
    
    DoTest --> GenData
    GenData --> BuildMem
    DoTest --> GetKB
    BuildMem --> CreateMachine
    GetKB --> CreateMachine
    CreateMachine --> Run
    Run --> Validate
    
    Validate -->|Success| Cycles["Return machine.cycle"]
    Validate -->|Failure| Error["AssertionError:<br/>Incorrect output values"]
```

Sources: [tests/submission_tests.py:30-54](), [tests/submission_tests.py:57-61]()

## Understanding Test Output

### Correctness Validation

The `CorrectnessTests.test_kernel_correctness` test runs 8 iterations with different random seeds to verify your implementation produces correct results [[tests/submission_tests.py:57-61]]():

```
Testing forest_height=10, rounds=16, batch_size=256
CYCLES:  147734
.
Testing forest_height=10, rounds=16, batch_size=256
CYCLES:  147734
.
...
```

Each `.` indicates a passed test. If correctness fails, you'll see an `AssertionError`. This means your `KernelBuilder.build_kernel()` generated instructions that produce different memory values than the `reference_kernel2()` [[tests/submission_tests.py:45-52]]().

Sources: [tests/submission_tests.py:57-61](), [tests/submission_tests.py:45-52]()

### Performance Benchmarks

After correctness tests pass, the `SpeedTests` class runs performance benchmarks. Here's what the output looks like:

```
Testing forest_height=10, rounds=16, batch_size=256
CYCLES:  147734
Speedup over baseline:  1.0
```

**Key Metrics Explained**:

| Metric | Description | Example Value |
|--------|-------------|---------------|
| `CYCLES` | Total machine cycles to complete execution [[tests/submission_tests.py:53]]() | 147734 (baseline) |
| `Speedup over baseline` | Performance ratio: `BASELINE / machine.cycle` [[tests/submission_tests.py:70]]() | 1.0x (no improvement) |
| `BASELINE` | Unoptimized starting point constant [[tests/submission_tests.py:63]]() | 147734 cycles |

Sources: [tests/submission_tests.py:63-74](), [perf_takehome.py:173]()

### Performance Threshold Ladder

The `SpeedTests` class contains multiple test methods, each representing a performance milestone achieved by various Claude models or human benchmarks.

**Diagram: Performance Test Hierarchy**

```mermaid
flowchart TD
    Entry["SpeedTests.cycles()<br/>@lru_cache<br/>Runs once per test session"]
    
    T1["test_kernel_speedup<br/>cycles < 147734<br/>BASELINE"]
    T2["test_kernel_updated_starting_point<br/>cycles < 18532<br/>7.97x speedup"]
    T3["test_opus4_many_hours<br/>cycles < 2164<br/>68.3x speedup"]
    T4["test_opus45_casual<br/>cycles < 1790<br/>82.5x speedup<br/>~Best Human 2hr"]
    T5["test_opus45_2hr<br/>cycles < 1579<br/>93.5x speedup"]
    T6["test_sonnet45_many_hours<br/>cycles < 1548<br/>95.4x speedup"]
    T7["test_opus45_11hr<br/>cycles < 1487<br/>99.3x speedup<br/>🏆 RECRUITMENT GATE"]
    T8["test_opus45_improved_harness<br/>cycles < 1363<br/>108.4x speedup"]
    
    Entry --> T1
    T1 --> T2
    T2 --> T3
    T3 --> T4
    T4 --> T5
    T5 --> T6
    T6 --> T7
    T7 --> T8
    
    T7 -.->|"If passed"| Contact["Contact:<br/>performance-recruiting@anthropic.com"]
```

Sources: [tests/submission_tests.py:76-116](), [Readme.md:7-18]()

### Test Caching Behavior

The submission tests use `@lru_cache` decorators to optimize test execution:

- **`kernel_builder()`** [[tests/submission_tests.py:23-27]](): Caches the generated instructions for a specific configuration so the machine doesn't re-compile the kernel for every test.
- **`cycles()`** [[tests/submission_tests.py:66-74]](): Runs the simulator once per test session and reuses the result across all `SpeedTests` assertions.

Sources: [tests/submission_tests.py:23-27](), [tests/submission_tests.py:66-74]()

## Development Workflow Overview

**Diagram: Typical Optimization Iteration**

```mermaid
flowchart LR
    Edit["Edit<br/>KernelBuilder.build_kernel()<br/>in perf_takehome.py"]
    Test["Run<br/>python tests/submission_tests.py"]
    Results["Check Results:<br/>- Correctness: Pass/Fail<br/>- Cycles: Number<br/>- Tests passed: X/9"]
    
    Edit --> Test
    Test --> Results
    Results -->|"Failure or<br/>want better cycles"| Edit
    Results -->|"cycles < 1487"| Submit["Email solution to<br/>performance-recruiting@<br/>anthropic.com"]
    
    Results -.->|"Optional:<br/>Need to debug"| Trace["Run with trace=True<br/>Use watch_trace.py<br/>See Perfetto UI"]
    Trace -.-> Edit
```

Sources: [perf_takehome.py:85-172](), [Readme.md:18-20]()

### Key Files for Optimization

| File | Your Role | What to Modify |
|------|-----------|----------------|
| `perf_takehome.py` | **Primary optimization target** | Modify the `KernelBuilder.build_kernel()` method [[perf_takehome.py:85-172]](). |
| `tests/submission_tests.py` | Run to validate | Do not modify (uses the frozen simulator to prevent cheating) [[Readme.md:29-37]](). |
| `problem.py` | Reference/documentation | Read for understanding; not used in official tests. |
| `frozen_problem.py` | Testing environment | Do not modify (this is the ground truth for tests) [[tests/submission_tests.py:11-19]](). |

Sources: [perf_takehome.py:85-172](), [tests/submission_tests.py:11-19](), [Readme.md:29-37]()

## Next Steps

Once you have tests running successfully:

1. **Understand the Problem**: Read **2.1. The Tree Traversal Problem** to understand the hashing and tree logic.
2. **Learn the Architecture**: Review **4. Machine Architecture** to understand the VLIW SIMD execution model.
3. **Study the Current Implementation**: Examine **5.1. KernelBuilder Class Overview** to see the baseline approach.
4. **Enable Trace Visualization**: Follow **7.1. Trace Generation** to visualize instruction execution in Perfetto.

### Quick Command Reference

```bash
# Official submission tests (what counts)
python tests/submission_tests.py

# Development testing with trace generation (requires watch_trace.py)
python perf_takehome.py Tests.test_kernel_trace

# In separate terminal: Launch trace viewer server
python watch_trace.py
```

Sources: [perf_takehome.py:258-269](), [Readme.md:20]()

## Understanding Your Starting Point

The unmodified `KernelBuilder.build_kernel()` method generates a **scalar implementation** that:

- Uses only scalar ALU operations (no vector VALU engine) [[perf_takehome.py:131-167]]().
- Processes batch items sequentially in nested loops [[perf_takehome.py:131-167]]().
- Achieves 147,734 cycles (the `BASELINE`) [[tests/submission_tests.py:63]]().
- Uses simple non-VLIW instruction packing (each instruction is emitted as a single-operation bundle) [[perf_takehome.py:48-53]]().

**Your optimization goal**: Modify `build_kernel()` to generate more efficient instruction sequences that utilize the VLIW slots (ALU, VALU, LOAD, STORE, FLOW) in parallel while maintaining correctness [[perf_takehome.py:85-172]]().

The recruitment threshold of 1,487 cycles represents a **99.3x speedup** over baseline—achievable through vectorization, VLIW instruction packing, and efficient memory management [[Readme.md:15-18]]().

Sources: [perf_takehome.py:85-172](), [tests/submission_tests.py:63](), [Readme.md:15-18]()

---

# Page: System Architecture Overview

# System Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perf_takehome.py](perf_takehome.py)
- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This document provides a high-level overview of the system architecture for the performance optimization take-home challenge. It explains how the major components interact, the data flow through the system, and how code execution and validation work.

For detailed information about the optimization target itself, see [KernelBuilder - The Optimization Target](5.1). For the machine instruction set and execution semantics, see [Machine Architecture](4.1). For the testing infrastructure, see [Testing Framework](6.1).

## Purpose and Scope

This system implements a performance optimization benchmark for a custom VLIW SIMD architecture. The architecture consists of three primary layers:

1.  **Problem Definition Layer**: Defines the computational problem (tree traversal with hashing), input data structures, and reference implementations.
2.  **Optimization Layer**: The `KernelBuilder` class that participants modify to generate efficient instruction sequences.
3.  **Execution and Validation Layer**: The `Machine` simulator that executes generated instructions and validates correctness.

## Component Architecture

The following diagram shows the major code entities and their relationships:

**Component Interaction Diagram**
```mermaid
graph TB
    subgraph "Problem Definition [problem.py]"
        Tree["Tree<br/>(class)"]
        Input["Input<br/>(class)"]
        reference_kernel["reference_kernel()<br/>reference_kernel2()"]
        build_mem_image["build_mem_image()"]
        myhash["myhash()"]
    end
    
    subgraph "Optimization Target [perf_takehome.py]"
        KernelBuilder["KernelBuilder<br/>(class)"]
        build_kernel["build_kernel()<br/>(method)"]
        do_kernel_test["do_kernel_test()"]
    end
    
    subgraph "Execution [problem.py / frozen_problem.py]"
        Machine["Machine<br/>(class)"]
        Core["Core<br/>(class)"]
        step["step()<br/>(method)"]
        alu["alu(), valu(), load(),<br/>store(), flow()<br/>(methods)"]
    end
    
    subgraph "Testing [tests/submission_tests.py]"
        CorrectnessTests["CorrectnessTests<br/>(class)"]
        SpeedTests["SpeedTests<br/>(class)"]
        kernel_builder_cache["kernel_builder()<br/>(@lru_cache)"]
    end
    
    subgraph "Debugging [problem.py]"
        setup_trace["setup_trace()"]
        trace_slot["trace_slot()"]
        DebugInfo["DebugInfo<br/>(class)"]
    end
    
    Tree --> build_mem_image
    Input --> build_mem_image
    build_mem_image --> Machine
    
    KernelBuilder --> build_kernel
    build_kernel --> Machine
    
    Machine --> Core
    Machine --> step
    step --> alu
    
    do_kernel_test --> KernelBuilder
    do_kernel_test --> Machine
    do_kernel_test --> reference_kernel
    
    CorrectnessTests --> kernel_builder_cache
    SpeedTests --> kernel_builder_cache
    kernel_builder_cache --> KernelBuilder
    
    Machine --> setup_trace
    setup_trace --> trace_slot
    KernelBuilder --> DebugInfo
    DebugInfo --> Machine
```

**Sources**: [perf_takehome.py:1-176](), [problem.py:1-569](), [tests/submission_tests.py:1-120](), [tests/frozen_problem.py:1-569]()

### Component Table

| Component | File Location | Primary Responsibility |
|-----------|--------------|------------------------|
| `Tree` | [problem.py:406-418]() | Represents implicit balanced binary tree structure with node values |
| `Input` | [problem.py:421-436]() | Batch of input indices and values for tree traversal |
| `reference_kernel` / `reference_kernel2` | [problem.py:467-569]() | Ground truth implementations defining correct computation |
| `KernelBuilder` | [perf_takehome.py:40-174]() | **Optimization target**: Generates instruction sequences |
| `Machine` | [problem.py:64-403]() | VLIW SIMD simulator that executes instruction bundles |
| `Core` | [problem.py:25-30]() | Per-core state (scratch space, PC, execution state) |
| `do_kernel_test` | [perf_takehome.py:178-226]() | Main testing harness for development |

**Sources**: [perf_takehome.py:23-37](), [problem.py:405-437](), [problem.py:64-95]()

## Data Flow Architecture

The following diagram shows how data transforms through the system, from problem generation to validation:

**Data Flow Diagram**
```mermaid
flowchart TD
    subgraph Generation["Problem Generation"]
        params["Parameters:<br/>forest_height, batch_size, rounds"]
        Tree_generate["Tree.generate()"]
        Input_generate["Input.generate()"]
        tree_obj["Tree object:<br/>height, values[]"]
        input_obj["Input object:<br/>indices[], values[], rounds"]
    end
    
    subgraph Serialization["Memory Serialization"]
        build_mem_image_fn["build_mem_image()"]
        mem_image["Flat memory array:<br/>[header, tree_values, inp_indices, inp_values]"]
    end
    
    subgraph Compilation["Instruction Generation"]
        kb_init["kb = KernelBuilder()"]
        kb_build["kb.build_kernel()"]
        instrs["List[Instruction]<br/>(VLIW bundles)"]
        debug_info["DebugInfo:<br/>scratch_map"]
    end
    
    subgraph Execution["Execution"]
        machine_init["Machine(mem, instrs, debug_info)"]
        machine_run["machine.run()"]
        machine_mem["machine.mem<br/>(updated)"]
        cycle_count["machine.cycle"]
    end
    
    subgraph Validation["Validation"]
        ref_kernel2["reference_kernel2(mem)"]
        ref_mem["Expected memory state"]
        compare["Assert: machine.mem[inp_values_p:] ==<br/>ref_mem[inp_values_p:]"]
    end
    
    params --> Tree_generate
    params --> Input_generate
    Tree_generate --> tree_obj
    Input_generate --> input_obj
    
    tree_obj --> build_mem_image_fn
    input_obj --> build_mem_image_fn
    build_mem_image_fn --> mem_image
    
    tree_obj --> kb_init
    input_obj --> kb_init
    kb_init --> kb_build
    kb_build --> instrs
    kb_build --> debug_info
    
    mem_image --> machine_init
    instrs --> machine_init
    debug_info --> machine_init
    machine_init --> machine_run
    machine_run --> machine_mem
    machine_run --> cycle_count
    
    mem_image --> ref_kernel2
    ref_kernel2 --> ref_mem
    machine_mem --> compare
    ref_mem --> compare
```

**Sources**: [perf_takehome.py:178-226](), [problem.py:487-513](), [problem.py:535-569]()

### Memory Layout

The `build_mem_image` function creates a flat memory layout that both the simulator and reference kernel operate on:

| Offset | Content | Description |
|--------|---------|-------------|
| `mem[0]` | `rounds` | Number of traversal rounds to execute |
| `mem[1]` | `n_nodes` | Total number of tree nodes (2^(height+1) - 1) |
| `mem[2]` | `batch_size` | Number of parallel traversals |
| `mem[3]` | `forest_height` | Height of the binary tree |
| `mem[4]` | `forest_values_p` | Pointer to tree node values array |
| `mem[5]` | `inp_indices_p` | Pointer to input indices array |
| `mem[6]` | `inp_values_p` | Pointer to input values array |
| `mem[7:]` | Data arrays | Tree values, input indices, input values, extra room |

**Sources**: [problem.py:487-513]()

## Execution Architecture

This diagram shows the relationship between the instruction generation phase and the execution phase:

**Execution Phase Diagram**
```mermaid
graph TB
    subgraph "KernelBuilder Phase [perf_takehome.py]"
        dimensions["Input dimensions:<br/>forest_height, n_nodes,<br/>batch_size, rounds"]
        kb_state["KernelBuilder state:<br/>instrs[], scratch{},<br/>scratch_ptr"]
        build_kernel_method["build_kernel()<br/>method"]
        alloc_scratch["alloc_scratch()"]
        scratch_const["scratch_const()"]
        build_hash["build_hash()"]
        add_method["add()"]
        build_method["build()"]
        final_instrs["List[dict[Engine, list[tuple]]]"]
    end
    
    subgraph "Machine Phase [problem.py]"
        machine_state["Machine state:<br/>mem[], program[],<br/>cycle, cores[]"]
        run_method["run()<br/>method"]
        step_method["step()"]
        engine_methods["Engine-specific methods:<br/>alu(), valu(), load(),<br/>store(), flow()"]
        scratch_write["scratch_write{}<br/>(buffered)"]
        mem_write["mem_write{}<br/>(buffered)"]
        commit["Commit phase:<br/>Apply writes to<br/>core.scratch[] and mem[]"]
    end
    
    dimensions --> build_kernel_method
    build_kernel_method --> alloc_scratch
    build_kernel_method --> scratch_const
    build_kernel_method --> build_hash
    build_kernel_method --> add_method
    add_method --> kb_state
    kb_state --> build_method
    build_method --> final_instrs
    
    final_instrs --> machine_state
    machine_state --> run_method
    run_method --> step_method
    step_method --> engine_methods
    engine_methods --> scratch_write
    engine_methods --> mem_write
    scratch_write --> commit
    mem_write --> commit
```

**Sources**: [perf_takehome.py:40-174](), [problem.py:197-217](), [problem.py:352-398]()

### Instruction Bundle Structure

Each instruction in the program is a dictionary mapping engine names to lists of operation tuples:

```python
# Example instruction structure
{"valu": [("*", 4, 0, 0), ("+", 8, 4, 0)], "load": [("load", 16, 17)]}
```

The `KernelBuilder` generates these through the `build()` method, which can optionally pack multiple operations into single instruction bundles (VLIW packing):

**Sources**: [perf_takehome.py:51-56](), [problem.py:14-15]()

### Execution Model: Two-Phase Commit

The `Machine.step()` method implements a two-phase execution model:

1.  **Read Phase**: All slots read their operands from the cycle-start state [problem.py:356-382]().
2.  **Write Phase**: All writes are buffered in `scratch_write` and `mem_write` dictionaries [problem.py:383-394]().
3.  **Commit Phase**: Buffered writes are applied atomically at the end of the cycle [problem.py:396-398]().

**Sources**: [problem.py:352-398]()

## Testing and Validation Architecture

**Testing Architecture Diagram**
```mermaid
graph LR
    subgraph "Development Testing [perf_takehome.py]"
        dev_test["Tests.test_kernel_cycles"]
        dev_do_kernel["do_kernel_test()"]
        dev_machine["Machine(trace=False,<br/>enable_pause=True,<br/>enable_debug=True)"]
        dev_ref["reference_kernel2()<br/>(with value_trace)"]
    end
    
    subgraph "Submission Testing [tests/submission_tests.py]"
        correctness["CorrectnessTests"]
        speed["SpeedTests"]
        cached_kb["kernel_builder()<br/>@lru_cache"]
        frozen_machine["Machine from frozen_problem<br/>(enable_pause=False,<br/>enable_debug=False)"]
        frozen_ref["reference_kernel2()<br/>from frozen_problem"]
    end
    
    subgraph "Caching Strategy"
        lru_cache["@lru_cache(maxsize=None)"]
        cache_key["Key: (forest_height, n_nodes,<br/>batch_size, rounds)"]
    end
    
    dev_test --> dev_do_kernel
    dev_do_kernel --> dev_machine
    dev_do_kernel --> dev_ref
    
    correctness --> cached_kb
    speed --> cached_kb
    cached_kb --> lru_cache
    lru_cache --> cache_key
    cached_kb --> frozen_machine
    cached_kb --> frozen_ref
```

**Sources**: [perf_takehome.py:178-256](), [tests/submission_tests.py:23-74]()

### Test Execution Flow

The testing system uses two different simulator instances:

| Testing Context | Simulator Source | Debug Features | Purpose |
|----------------|-----------------|----------------|---------|
| Development (`perf_takehome.py`) | `problem.py` | Pause points, debug instructions, value tracing | Interactive debugging during optimization |
| Submission (`tests/submission_tests.py`) | `tests/frozen_problem.py` | Disabled | Fair performance measurement on frozen simulator |

**Key differences**:
*   **Development**: `Machine(trace=True/False, value_trace={...})` with pause points that match `reference_kernel2` yields for step-by-step validation [perf_takehome.py:194-204]().
*   **Submission**: `Machine(enable_pause=False, enable_debug=False)` for pure performance measurement [tests/submission_tests.py:40-43]().

**Sources**: [perf_takehome.py:194-204](), [tests/submission_tests.py:40-43]()

### Performance Measurement

Cycle counting occurs in `Machine.run()`:

```python
# Logic from problem.py:216-217
if has_non_debug:
    self.cycle += 1
```

Only non-debug instructions increment the cycle counter. The baseline of 147,734 cycles represents the unoptimized starting point.

**Sources**: [problem.py:197-217](), [perf_takehome.py:176](), [tests/submission_tests.py:63-74]()

## Cross-Component Data Dependencies

**Constant Dependencies Diagram**
```mermaid
graph TB
    subgraph "Constants [problem.py]"
        SLOT_LIMITS["SLOT_LIMITS<br/>{alu: 12, valu: 6,<br/>load: 2, store: 2, flow: 1}"]
        VLEN["VLEN = 8"]
        N_CORES["N_CORES = 1"]
        SCRATCH_SIZE["SCRATCH_SIZE = 1536"]
        HASH_STAGES["HASH_STAGES<br/>(list of tuples)"]
    end
    
    subgraph "KernelBuilder Usage [perf_takehome.py]"
        kb_scratch["Scratch allocation:<br/>scratch_ptr tracking"]
        kb_hash["build_hash()<br/>generates hash operations"]
        kb_assert["Assert scratch_ptr <= SCRATCH_SIZE"]
    end
    
    subgraph "Machine Usage [problem.py]"
        m_cores["cores = [Core(...)]<br/>×N_CORES"]
        m_scratch["core.scratch = [0]*SCRATCH_SIZE"]
        m_step["step() checks<br/>len(slots) <= SLOT_LIMITS"]
        m_valu["valu() operates on<br/>VLEN elements"]
        m_hash["Executes hash instructions<br/>based on HASH_STAGES"]
    end
    
    SLOT_LIMITS --> m_step
    VLEN --> m_valu
    N_CORES --> m_cores
    SCRATCH_SIZE --> m_scratch
    SCRATCH_SIZE --> kb_assert
    HASH_STAGES --> kb_hash
    HASH_STAGES --> m_hash
    
    kb_scratch --> m_scratch
    kb_hash --> m_hash
```

**Sources**: [problem.py:48-62](), [problem.py:439-446](), [perf_takehome.py:61-68](), [problem.py:383]()

## Key Architectural Invariants

1.  **Instruction Format**: All instructions are dictionaries mapping `Engine` names to lists of operation tuples [problem.py:14-15]().
2.  **Memory Model**: Flat word array with pointer-based addressing; all addresses are word offsets [problem.py:79-83]().
3.  **Scratch Space**: Per-core fast memory (1536 words) for intermediate values; addresses are managed by `KernelBuilder` [problem.py:60](), [perf_takehome.py:61-68]().
4.  **Atomic Cycles**: Within a cycle, all reads see the cycle-start state; all writes are buffered and committed atomically [problem.py:352-398]().
5.  **Correctness Oracle**: `reference_kernel2` defines ground truth; the optimized kernel must produce identical `inp_values` array [problem.py:535-569]().
6.  **Performance Metric**: Total cycle count (non-debug instructions only) measured by the frozen simulator [problem.py:216-217]().

**Sources**: [problem.py:64-95](), [problem.py:352-398](), [tests/submission_tests.py:48-53]()

---

# Page: The Optimization Challenge

# The Optimization Challenge

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Readme.md](Readme.md)
- [tests/submission_tests.py](tests/submission_tests.py)

</details>



This page frames the core optimization challenge in this repository: what you're trying to optimize, how performance is measured, what targets exist, and how to validate your solution. For detailed information about the tree traversal algorithm being optimized, see [The Tree Traversal Problem](#2.1). For comprehensive performance benchmark details, see [Performance Benchmarks and Thresholds](#2.2). For the structure of the `KernelBuilder` class you'll be modifying, see [Kernel Builder - The Optimization Target](#5).

## The Core Task

Your objective is to optimize the `KernelBuilder.build_kernel` method in [perf_takehome.py:85-172]() to generate the most efficient instruction sequence possible for a custom VLIW SIMD architecture. The challenge measures performance in **clock cycles** consumed by the `Machine` simulator when executing your generated instructions.

### Optimization Flow: Code to Execution

The following diagram bridges the "Natural Language Space" of the challenge to the "Code Entity Space" where you will be working.

```mermaid
graph TB
    subgraph "Natural Language Space"
        Problem["Problem Parameters"]
        Opt["Optimization Target"]
        Sim["Simulation & Cycles"]
        Val["Validation"]
    end

    subgraph "Code Entity Space"
        InputParams["forest_height, batch_size, rounds"]
        KB["KernelBuilder.build_kernel()<br/>(perf_takehome.py:85)"]
        Instrs["kb.instrs<br/>(List of Instructions)"]
        MachineClass["Machine (frozen_problem.py:12)"]
        Ref["reference_kernel2()<br/>(frozen_problem.py:14)"]
        Cycles["machine.cycle"]
    end

    Problem --- InputParams
    Opt --- KB
    Sim --- MachineClass
    Val --- Ref

    InputParams --> KB
    KB --> Instrs
    Instrs --> MachineClass
    MachineClass --> Cycles
    MachineClass -.->|Memory Compare| Ref
    
    style KB stroke-width:4px
    style MachineClass stroke-width:4px
```

**Sources:** [perf_takehome.py:85-172](), [tests/submission_tests.py:11-20](), [tests/submission_tests.py:40-43]()

## What You're Optimizing

The optimization target is a **tree traversal kernel** that processes batches of inputs through a perfect binary tree. Each input follows a path determined by hashing operations at each node.

### The `KernelBuilder.build_kernel` Method

The method signature is:

```python
def build_kernel(
    self, forest_height: int, n_nodes: int, batch_size: int, rounds: int
):
```

This method generates a list of `Instruction` objects (dictionaries mapping engine names to slot lists) that the `Machine` simulator will execute. The current implementation in [perf_takehome.py:85-172]() is a **scalar baseline** that processes one input element at a time using only scalar ALU and load/store operations.

**Key constraints:**
- You generate instructions **only** from dimensional parameters (heights, counts).
- Instructions must work for **any** valid tree and input data with those dimensions.
- The generated code must match `reference_kernel2` output at pause points.
- The frozen simulator in `frozen_problem.py` evaluates your submission.

### The Architecture You're Targeting

You're compiling for a custom **VLIW SIMD** machine. All slots in an instruction bundle execute **in parallel** within a single cycle.

| Engine | Slots | Purpose | Key Operations |
|--------|-------|---------|----------------|
| `alu` | 12 | Scalar arithmetic | `+`, `-`, `*`, `^`, `<<`, `>>`, `%`, `<`, `==` |
| `valu` | 6 | Vector arithmetic (VLEN=8) | Same ops + `vbroadcast`, `multiply_add` |
| `load` | 2 | Memory to scratch | `load`, `vload`, `const` |
| `store` | 2 | Scratch to memory | `store`, `vstore` |
| `flow` | 1 | Control flow | `select`, `vselect`, `pause`, `halt` |
| `debug` | 64 | Validation (submission ignores) | `compare`, `vcompare`, `comment` |

**Sources:** [perf_takehome.py:37-83](), [tests/submission_tests.py:17-19]()

## Performance Measurement

Performance is measured by the `machine.cycle` counter after executing your generated instructions. The baseline scalar implementation consumes **147,734 cycles** for the standard test case (forest_height=10, batch_size=256, rounds=16) [tests/submission_tests.py:63-71]().

### Performance Ladder

The repository defines a performance ladder representing progressively better optimizations. Beating the **1,487 cycle threshold** demonstrates optimization skill exceeding Claude Opus 4.5's launch-time performance [Readme.md:17-21]().

| Threshold (cycles) | Speedup vs Baseline | Achievement |
|-------------------|---------------------|-------------|
| 147,734 | 1.0x | Starting baseline |
| 18,532 | 7.97x | Updated starting point |
| 2,164 | 68.3x | Claude Opus 4 (many hours) |
| 1,790 | 82.5x | Claude Opus 4.5 casual / Best human (2hr) |
| 1,579 | 93.5x | Claude Opus 4.5 (2hr harness) |
| 1,548 | 95.4x | Claude Sonnet 4.5 (many hours) |
| **1,487** | **99.3x** | **Claude Opus 4.5 launch (recruitment gate)** |
| 1,363 | 108.4x | Claude Opus 4.5 (improved harness) |

**Sources:** [Readme.md:9-21](), [tests/submission_tests.py:85-115]()

## Validation and Submission

### Correctness and Test Integrity

The testing harness validates functional correctness by comparing the final memory state of the `Machine` against the output of `reference_kernel2` [tests/submission_tests.py:45-52]().

```mermaid
graph LR
    subgraph "Validation Logic"
        RefK["reference_kernel2(mem)"]
        MachineMem["machine.mem"]
        Compare["assert machine.mem == ref_mem"]
    end

    subgraph "Integrity Rules"
        GitDiff["git diff origin/main tests/"]
        NoCores["N_CORES = 1 (Fixed)"]
    end

    RefK --> Compare
    MachineMem --> Compare
    Compare --> Success["Valid Submission"]
    GitDiff -->|Must be empty| Success
    NoCores -->|Must not change| Success
```

**Important Submission Rules:**
1. **No Test Modification**: The `tests/` folder must remain unchanged. Run `git diff origin/main tests/` to verify [Readme.md:31-34]().
2. **No Multicore Hacks**: `N_CORES` is intentionally set to 1. Modifying this to achieve speedup is considered an invalid solution [Readme.md:39]().
3. **Beating the Gate**: If you optimize below **1487 cycles**, you are encouraged to email your code to `performance-recruiting@anthropic.com` [Readme.md:21]().

**Sources:** [Readme.md:25-40](), [tests/submission_tests.py:45-54](), [tests/submission_tests.py:17]()

For details on the validation process and how to submit, see [Validation and Submission](#2.3).

---

# Page: The Tree Traversal Problem

# The Tree Traversal Problem

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page describes the computational problem at the heart of the optimization challenge: a parallel tree traversal algorithm with cryptographic-style hashing. Understanding this algorithm is essential before attempting to optimize the `KernelBuilder` in `perf_takehome.py`.

## Overview

The tree traversal problem processes a batch of independent traversals through an implicit binary tree structure. Each traversal follows a deterministic path based on hashing operations, and the entire batch is processed for multiple rounds. The challenge is to implement this computation efficiently on a VLIW SIMD architecture.

**Key characteristics:**
- **Batch parallelism**: 256 independent traversals processed simultaneously [tests/frozen_problem.py:421-436]().
- **Data-dependent control flow**: Path decisions (left vs. right child) are based on computed hash values [tests/frozen_problem.py:476-484]().
- **Memory access patterns**: Irregular tree node lookups based on current indices [tests/frozen_problem.py:551-564]().
- **Computational intensity**: A 6-stage hash function is applied at every step [tests/frozen_problem.py:439-464]().
- **Multiple iterations**: The default configuration runs 16 rounds of traversal [tests/frozen_problem.py:421-436]().

Sources: [tests/frozen_problem.py:421-436](), [tests/frozen_problem.py:439-464](), [tests/frozen_problem.py:476-484](), [tests/frozen_problem.py:551-564]()

## The Algorithm

The following diagram illustrates the logical flow of the traversal as defined in the reference implementations.

```mermaid
flowchart TD
    Start["Start: rounds=16, batch_size=256"] --> OuterLoop["For each round h in [0..rounds)"]
    OuterLoop --> InnerLoop["For each batch index i in [0..batch_size)"]
    
    InnerLoop --> LoadIdx["Load current index:<br/>idx = inp.indices[i]"]
    LoadIdx --> LoadVal["Load current value:<br/>val = inp.values[i]"]
    LoadVal --> LoadNode["Load tree node value:<br/>node_val = tree.values[idx]"]
    
    LoadNode --> XOR["XOR operation:<br/>val = val ^ node_val"]
    XOR --> Hash["Apply myhash(val)"]
    
    Hash --> CheckParity["Check if val is even:<br/>val % 2 == 0"]
    CheckParity -->|"Even (left child)"| LeftChild["next_idx = 2 * idx + 1"]
    CheckParity -->|"Odd (right child)"| RightChild["next_idx = 2 * idx + 2"]
    
    LeftChild --> CheckBounds["Check bounds:<br/>next_idx >= n_nodes?"]
    RightChild --> CheckBounds
    
    CheckBounds -->|"Out of bounds"| Wrap["Wrap to root:<br/>idx = 0"]
    CheckBounds -->|"In bounds"| NoWrap["idx = next_idx"]
    
    Wrap --> Store["Store results:<br/>inp.values[i] = val<br/>inp.indices[i] = idx"]
    NoWrap --> Store
    
    Store --> NextBatch["Next batch element"]
    NextBatch -->|"More elements"| InnerLoop
    NextBatch -->|"Batch complete"| NextRound["Next round"]
    NextRound -->|"More rounds"| OuterLoop
    NextRound -->|"Complete"| End["End: Updated inp.values and inp.indices"]
```

Sources: [tests/frozen_problem.py:467-484](), [tests/frozen_problem.py:535-568]()

### Algorithm Steps in Detail

The reference implementation `reference_kernel` [tests/frozen_problem.py:467-484]() performs the following operations:

1.  **Outer loop**: Iterate `rounds` times (typically 16).
2.  **Inner loop**: Process each of `batch_size` elements (typically 256).
3.  **Node lookup**: Read `tree.values[idx]` using the current index.
4.  **Hash computation**: Compute `myhash(val ^ node_val)`.
5.  **Branch decision**: Choose the left child (`2*idx + 1`) if the hash is even, or the right child (`2*idx + 2`) if it is odd.
6.  **Boundary handling**: If the new index exceeds the tree size (`n_nodes`), wrap back to the root (index 0).
7.  **State update**: Store the updated value and index back to the input arrays.

This creates a complex dependency chain where the next memory address to load (`tree.values[idx]`) depends on the previous cycle's hash result.

Sources: [tests/frozen_problem.py:476-484]()

## Data Structures

### Tree Structure

The `Tree` class [tests/frozen_problem.py:405-418]() represents an implicit perfect binary tree stored as a flat array.

| Field | Type | Description |
| :--- | :--- | :--- |
| `height` | `int` | Tree height (default: 10) |
| `values` | `list[int]` | Node values in breadth-first order |

**Implicit tree properties:**
- Total nodes: $2^{height+1} - 1$ (default: 2047 nodes).
- Node $i$ has left child at $2i + 1$ and right child at $2i + 2$.
- Root node is at index 0.

Sources: [tests/frozen_problem.py:405-418]()

### Input Structure

The `Input` class [tests/frozen_problem.py:421-436]() represents the batch of traversals.

| Field | Type | Description |
| :--- | :--- | :--- |
| `indices` | `list[int]` | Current tree node index for each traversal |
| `values` | `list[int]` | Current hash value for each traversal |
| `rounds` | `int` | Number of traversal iterations |

Sources: [tests/frozen_problem.py:421-436]()

## The Hash Function

The `myhash` function [tests/frozen_problem.py:449-464]() implements a 6-stage mixing operation. Each stage follows the pattern: `a = (a op1 constant) op2 (a op3 shift_amount)`.

```mermaid
graph LR
    subgraph "Hash Logic (myhash)"
        Input["Input: a"] --> S0["Stage 0: +, << 12"]
        S0 --> S1["Stage 1: ^, >> 19"]
        S1 --> S2["Stage 2: +, << 5"]
        S2 --> S3["Stage 3: +, << 9 (XOR)"]
        S3 --> S4["Stage 4: +, << 3"]
        S4 --> S5["Stage 5: ^, >> 16"]
        S5 --> Output["Output: a (mod 2^32)"]
    end
```

### HASH_STAGES Definition

The specific operations and constants are defined in the `HASH_STAGES` list:

```python
# tests/frozen_problem.py:439-446
HASH_STAGES = [
    ("+", 0x7ED55D16, "+", "<<", 12),  # Stage 0
    ("^", 0xC761C23C, "^", ">>", 19),  # Stage 1
    ("+", 0x165667B1, "+", "<<", 5),   # Stage 2
    ("+", 0xD3A2646C, "^", "<<", 9),   # Stage 3
    ("+", 0xFD7046C5, "+", "<<", 3),   # Stage 4
    ("^", 0xB55A4F09, "^", ">>", 16),  # Stage 5
]
```

Sources: [tests/frozen_problem.py:439-446](), [tests/frozen_problem.py:449-464]()

## Why This Problem Is Interesting for Optimization

### 1. Data-Dependent Memory Access
The memory address for the next node lookup (`tree.values[idx]`) is calculated from the result of the `myhash` function. This prevents simple prefetching and creates a "pointer chasing" bottleneck.

### 2. SIMD and Vectorization
While individual traversals are serial, the `batch_size` of 256 allows for massive parallelism. The `Machine` architecture supports vector operations (`valu`) on `VLEN=8` elements [tests/frozen_problem.py:57](). Efficiently grouping 8 traversals into vector registers is key to high performance.

### 3. VLIW Instruction Packing
The `Machine` can execute multiple slots per cycle (e.g., 12 ALU slots, 6 VALU slots, 2 Load slots) [tests/frozen_problem.py:48-55](). Optimization involves "packing" the hash computation of one batch while simultaneously loading the tree nodes for another batch to hide latency.

### 4. Register Management
The `SCRATCH_SIZE` is limited to 1536 words [tests/frozen_problem.py:60](). Managing this space for constants, loop counters, and vector registers for 256 traversals requires careful allocation.

Sources: [tests/frozen_problem.py:48-55](), [tests/frozen_problem.py:57](), [tests/frozen_problem.py:60]()

## Reference Implementations

### reference_kernel
A high-level Python implementation used for conceptual correctness [tests/frozen_problem.py:467-484]().

### reference_kernel2
A lower-level implementation that operates on a flat memory array, simulating how the `Machine` sees data [tests/frozen_problem.py:535-568](). It uses a `yield` pattern to allow the test suite to pause and inspect memory at specific points [tests/frozen_problem.py:548]().

## Memory Layout and Data Flow

The `build_mem_image` function [tests/frozen_problem.py:487-513]() serializes the `Tree` and `Input` into a single list of integers.

```mermaid
graph TD
    subgraph "Machine Memory Layout"
        Header["Header (indices 0-6)"]
        TreeData["Tree Values"]
        InpIdx["Input Indices"]
        InpVal["Input Values"]
    end

    Header --- H0["0: Rounds"]
    Header --- H1["1: n_nodes"]
    Header --- H2["2: batch_size"]
    Header --- H4["4: Tree Ptr"]
    Header --- H5["5: Index Ptr"]
    Header --- H6["6: Value Ptr"]

    H4 --> TreeData
    H5 --> InpIdx
    H6 --> InpVal
```

Sources: [tests/frozen_problem.py:487-513]()

---

# Page: Performance Benchmarks and Thresholds

# Performance Benchmarks and Thresholds

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Readme.md](Readme.md)
- [tests/submission_tests.py](tests/submission_tests.py)

</details>



## Purpose and Scope

This page documents the performance benchmark ladder used to evaluate optimization submissions, from the baseline (147,734 cycles) to the best AI-achieved performance (1,363 cycles). It explains each threshold level, what performance they represent, the recruitment gate at 1,487 cycles, and how to test your implementation against these benchmarks.

For information about correctness validation, see **2.3 Validation and Submission**. For details about how cycle counting works in the simulator, see **4.4 Execution Model and Cycle Semantics**. For guidance on running and interpreting test results, see **6.4 Running and Interpreting Tests**.

## The Performance Ladder

The repository defines a stratified benchmark suite with increasingly aggressive cycle count targets. Each threshold represents a specific AI model's performance under particular compute conditions, providing context for optimization difficulty.

### Benchmark Levels

| Threshold | Cycles | Speedup | Description | Test Method |
|-----------|--------|---------|-------------|-------------|
| **Baseline** | 147,734 | 1.0x | Original unoptimized starting point | `test_kernel_speedup()` |
| **Updated Starting Point** | 18,532 | 7.97x | Improved starter code provided to candidates in later versions | `test_kernel_updated_starting_point()` |
| **Opus 4 (Many Hours)** | 2,164 | 68.3x | Claude Opus 4 with extensive test-time compute | `test_opus4_many_hours()` |
| **Opus 4.5 Casual** | 1,790 | 82.5x | Claude Opus 4.5 casual session ≈ best human 2hr | `test_opus45_casual()` |
| **Opus 4.5 (2hr)** | 1,579 | 93.5x | Claude Opus 4.5 with 2hr harness | `test_opus45_2hr()` |
| **Sonnet 4.5 (Many Hours)** | 1,548 | 95.4x | Claude Sonnet 4.5 with extended compute | `test_sonnet45_many_hours()` |
| **🎯 Recruitment Gate** | **1,487** | **99.3x** | Claude Opus 4.5 at launch (11.5hr harness) | `test_opus45_11hr()` |
| **Best AI Performance** | 1,363 | 108.4x | Claude Opus 4.5 with improved harness | `test_opus45_improved_harness()` |

The 1,487-cycle threshold serves as the recruitment screening gate, representing Claude Opus 4.5's performance at launch time.

**Sources:** [Readme.md:9-21](), [tests/submission_tests.py:63-115]()

### Performance Ladder Diagram

```mermaid
graph TB
    Start["Optimization Challenge Begins"]
    
    Baseline["BASELINE<br/>147,734 cycles<br/>1.0x speedup"]
    Updated["Updated Starting Point<br/>18,532 cycles<br/>7.97x speedup"]
    Opus4["Claude Opus 4 Many Hours<br/>2,164 cycles<br/>68.3x speedup"]
    Opus45Casual["Claude Opus 4.5 Casual<br/>≈ Best Human 2hr<br/>1,790 cycles<br/>82.5x speedup"]
    Opus45_2hr["Claude Opus 4.5 2hr Harness<br/>1,579 cycles<br/>93.5x speedup"]
    Sonnet45["Claude Sonnet 4.5 Many Hours<br/>1,548 cycles<br/>95.4x speedup"]
    
    Gate["🎯 RECRUITMENT GATE<br/>1,487 cycles<br/>99.3x speedup<br/>Claude Opus 4.5 Launch"]
    
    Best["Best AI Performance<br/>1,363 cycles<br/>108.4x speedup<br/>Improved Harness"]
    
    Contact["Email:<br/>performance-recruiting@<br/>anthropic.com"]
    
    Start --> Baseline
    Baseline --> Updated
    Updated --> Opus4
    Opus4 --> Opus45Casual
    Opus45Casual --> Opus45_2hr
    Opus45_2hr --> Sonnet45
    Sonnet45 --> Gate
    Gate --> Best
    
    Gate -.->|"cycles < 1487"| Contact
```

**Sources:** [Readme.md:9-21](), [tests/submission_tests.py:63-115]()

## The Baseline: 147,734 Cycles

The baseline performance is established by the `BASELINE` constant at 147,734 cycles, representing the original unoptimized implementation. This serves as the reference point for all speedup calculations.

[tests/submission_tests.py:63-63]()
```python
BASELINE = 147734
```

All submissions are measured against this baseline using the standard test configuration in `do_kernel_test`:
- **Forest height:** 10 (2,047 tree nodes) [tests/submission_tests.py:60]()
- **Batch size:** 256 input indices and values [tests/submission_tests.py:60]()
- **Rounds:** 16 processing rounds [tests/submission_tests.py:60]()

The speedup factor is calculated as: `speedup = BASELINE / res` [tests/submission_tests.py:70]().

**Sources:** [tests/submission_tests.py:60-70]()

## The Recruitment Threshold: 1,487 Cycles

The 1,487-cycle threshold represents a critical performance gate. This benchmark captures Claude Opus 4.5's best performance at launch, achieved after 11.5 hours in the test-time compute harness. 

According to the repository documentation:

> If you optimize below 1487 cycles, beating Claude Opus 4.5's best performance at launch, email us at performance-recruiting@anthropic.com with your code (and ideally a resume) so we can be appropriately impressed.

This threshold serves dual purposes:
1. **Talent identification:** Automatically identifies exceptionally skilled performance engineers.
2. **Benchmark reference:** Provides a concrete measure of state-of-the-art AI code generation capability.

**Sources:** [Readme.md:17-21](), [tests/submission_tests.py:109-111]()

## Testing Against Benchmarks

### Test Suite Structure

The benchmark thresholds are implemented as unit tests in the `SpeedTests` class in `tests/submission_tests.py`. Each test method asserts that the measured cycle count falls below a specific threshold.

```mermaid
graph LR
    SubTests["tests/submission_tests.py"]
    
    Correct["CorrectnessTests"]
    Speed["SpeedTests"]
    
    DoTest["do_kernel_test()"]
    CyclesFunc["cycles()"]
    Baseline["BASELINE = 147734"]
    
    TestBaseline["test_kernel_speedup()"]
    TestUpdated["test_kernel_updated_starting_point()"]
    TestOpus4["test_opus4_many_hours()"]
    TestOpus45C["test_opus45_casual()"]
    TestOpus45_2h["test_opus45_2hr()"]
    TestSonnet45["test_sonnet45_many_hours()"]
    TestOpus45_11h["test_opus45_11hr()"]
    TestOpus45Imp["test_opus45_improved_harness()"]
    
    SubTests --> Correct
    SubTests --> Speed
    
    Correct --> DoTest
    Speed --> CyclesFunc
    CyclesFunc --> DoTest
    
    Speed --> TestBaseline
    Speed --> TestUpdated
    Speed --> TestOpus4
    Speed --> TestOpus45C
    Speed --> TestOpus45_2h
    Speed --> TestSonnet45
    Speed --> TestOpus45_11h
    Speed --> TestOpus45Imp
    
    TestBaseline -.-> |"assert < 147734"| Baseline
    TestUpdated -.-> |"assert < 18532"| Baseline
    TestOpus4 -.-> |"assert < 2164"| Baseline
    TestOpus45C -.-> |"assert < 1790"| Baseline
    TestOpus45_2h -.-> |"assert < 1579"| Baseline
    TestSonnet45 -.-> |"assert < 1548"| Baseline
    TestOpus45_11h -.-> |"assert < 1487"| Baseline
    TestOpus45Imp -.-> |"assert < 1363"| Baseline
```

**Sources:** [tests/submission_tests.py:76-115]()

### Execution Flow

When you run `python tests/submission_tests.py`, the testing system:

1. **Correctness First:** Executes `CorrectnessTests.test_kernel_correctness()` which runs 8 randomized correctness tests [tests/submission_tests.py:58-60]().
2. **Performance Second:** Executes each `SpeedTests` method in sequence [tests/submission_tests.py:76-115]().
3. **Caching:** Uses `@lru_cache` on the `cycles()` function to avoid re-running the kernel for every threshold test [tests/submission_tests.py:66-67]().
4. **Failure Handling:** Returns `BASELINE * 2` (295,468 cycles) if an assertion error occurs during testing [tests/submission_tests.py:72-73]().

```mermaid
sequenceDiagram
    participant User
    participant Tests as "tests/submission_tests.py"
    participant Cycles as "cycles() @lru_cache"
    participant DoTest as "do_kernel_test()"
    participant KB as "KernelBuilder"
    participant Machine as "Machine"
    
    User->>Tests: "python tests/submission_tests.py"
    
    rect
        Note over Tests: CorrectnessTests Phase
        loop 8 times
            Tests->>DoTest: "test_kernel_correctness()"
            DoTest->>KB: "build_kernel(10, 2047, 256, 16)"
            KB-->>DoTest: "instructions"
            DoTest->>Machine: "Machine.run()"
            Machine-->>DoTest: "Machine.cycle"
            DoTest->>DoTest: "validate vs reference_kernel2"
        end
    end
    
    rect
        Note over Tests: SpeedTests Phase
        Tests->>Cycles: "test_kernel_speedup()"
        Cycles->>DoTest: "do_kernel_test(10, 16, 256)"
        DoTest->>Machine: "Machine.run()"
        Machine-->>DoTest: "cycle_count"
        DoTest-->>Cycles: "cycle_count"
        Cycles-->>Tests: "cycle_count (cached)"
        
        Tests->>Tests: "assert cycles < BASELINE"
        
        loop For each threshold
            Tests->>Cycles: "test_opus45_11hr(), etc."
            Cycles-->>Tests: "cycle_count (from cache)"
            Tests->>Tests: "assert cycles < threshold"
        end
    end
    
    Tests-->>User: "Test Results"
```

**Sources:** [tests/submission_tests.py:23-74](), [tests/submission_tests.py:58-60]()

### The cycles() Function

The `cycles()` function is the central measurement point:

[tests/submission_tests.py:66-74]()
```python
@lru_cache(maxsize=None)
def cycles():
    try:
        res = do_kernel_test(10, 16, 256)
        print("Speedup over baseline: ", BASELINE / res)
        return res
    except AssertionError as e:
        return BASELINE * 2
```

Key characteristics:
- **Cached:** Uses `@lru_cache` to ensure the kernel is only executed once per test run [tests/submission_tests.py:66]().
- **Error handling:** Returns double the baseline (295,468 cycles) on assertion errors, causing all speed tests to fail [tests/submission_tests.py:73]().
- **Speedup reporting:** Prints the speedup factor relative to baseline [tests/submission_tests.py:70]().

**Sources:** [tests/submission_tests.py:66-74]()

## Measuring Cycle Count

The cycle count is obtained from the `machine.cycle` attribute after calling `machine.run()` in the `do_kernel_test` function:

[tests/submission_tests.py:40-54]()
```python
    machine = Machine(mem, kb.instrs, kb.debug_info(), n_cores=N_CORES)
    machine.enable_pause = False
    machine.enable_debug = False
    machine.run()

    # ... validation ...

    print("CYCLES: ", machine.cycle)
    return machine.cycle
```

The `Machine` simulator increments its `cycle` counter on each execution cycle. The final count represents the total number of cycles required to complete the tree traversal computation.

**Sources:** [tests/submission_tests.py:40-54]()

## Speedup Calculation

The speedup factor is calculated as the ratio of baseline cycles to measured cycles:

```
speedup = BASELINE / measured_cycles
speedup = 147734 / measured_cycles
```

### Example Calculations

| Measured Cycles | Calculation | Speedup | Performance Level |
|----------------|-------------|---------|-------------------|
| 147,734 | 147734 / 147734 | 1.0x | Baseline |
| 18,532 | 147734 / 18532 | 7.97x | Updated Starting Point |
| 2,164 | 147734 / 2164 | 68.3x | Opus 4 Many Hours |
| 1,487 | 147734 / 1487 | 99.3x | 🎯 Recruitment Gate |
| 1,363 | 147734 / 1363 | 108.4x | Best AI Performance |

The speedup metric provides an intuitive measure of optimization effectiveness, with higher values indicating better performance.

**Sources:** [tests/submission_tests.py:70]()

## Test Configuration Parameters

All benchmark measurements use standardized test parameters defined in the `do_kernel_test()` function call within `cycles()`:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `forest_height` | 10 | Creates a balanced binary tree with 2^11-1 = 2,047 nodes |
| `rounds` | 16 | Number of processing rounds over the input batch |
| `batch_size` | 256 | Number of input indices and values to process |

These parameters are fixed across all tests to ensure fair comparison. The problem size is substantial enough to expose optimization opportunities while remaining manageable for iterative development.

**Sources:** [tests/submission_tests.py:30-34](), [tests/submission_tests.py:69]()

## Running the Benchmark Suite

To execute all benchmarks and see which thresholds you pass:

```bash
python tests/submission_tests.py
```

The test output will show:
1. **Correctness results:** Pass/fail for 8 randomized correctness tests.
2. **Cycle count:** The measured number of cycles for your implementation.
3. **Speedup:** The speedup factor relative to baseline.
4. **Threshold results:** Pass/fail for each performance threshold.

Example output format:
```
Testing forest_height=10, rounds=16, batch_size=256
CYCLES:  1500
Speedup over baseline:  98.489...
```

If your cycle count is below 1,487, the README instructs you to contact `performance-recruiting@anthropic.com` with your code and resume.

**Sources:** [Readme.md:21-23](), [tests/submission_tests.py:30-54]()

---

# Page: Validation and Submission

# Validation and Submission

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Readme.md](Readme.md)
- [tests/submission_tests.py](tests/submission_tests.py)

</details>



This page documents how your optimized kernel is validated for correctness and evaluated for performance. It covers the test framework in `tests/submission_tests.py`, the validation mechanisms using reference implementations, cycle counting methodology, and the rules regarding valid solutions.

For information about the optimization target itself, see [5. Kernel Builder - The Optimization Target](). For details on the machine simulator execution, see [4. Machine Architecture](). For the reference implementations used for validation, see [3.3. Reference Implementations]().

## Overview of Validation Architecture

The validation system has two independent axes of evaluation: **correctness** and **performance**. Your generated kernel must produce identical memory state to the reference implementation, after which its cycle count determines your performance tier.

**Validation Flow from Code Generation to Results**

```mermaid
flowchart TB
    KB["KernelBuilder.build_kernel()"]
    Instrs["kb.instrs<br/>(instruction list)"]
    DebugInfo["kb.debug_info()"]
    
    TreeGen["Tree.generate(height)"]
    InputGen["Input.generate(forest, batch_size, rounds)"]
    MemImage["build_mem_image(forest, inp)"]
    
    RefKernel["reference_kernel2(mem)"]
    Machine["Machine(mem, instrs, debug_info, n_cores=N_CORES)"]
    
    RefMem["ref_mem<br/>(expected state)"]
    MachineMem["machine.mem<br/>(actual state)"]
    
    Compare{"mem[inp_values_p:] ==<br/>ref_mem[inp_values_p:]"}
    CycleCheck{"machine.cycle<br/>< threshold"}
    
    KB --> Instrs
    KB --> DebugInfo
    
    TreeGen --> MemImage
    InputGen --> MemImage
    
    MemImage --> RefKernel
    MemImage --> Machine
    Instrs --> Machine
    DebugInfo --> Machine
    
    Machine --> MachineMem
    Machine --> CycleCount["machine.cycle"]
    
    RefKernel --> RefMem
    
    MachineMem --> Compare
    RefMem --> Compare
    
    Compare -->|"Match"| CycleCheck
    Compare -->|"Mismatch"| Fail["AssertionError:<br/>Incorrect output values"]
    
    CycleCheck -->|"Pass"| Success["Test Pass"]
    CycleCheck -->|"Fail"| Slow["Test Fail"]
```

Sources: [tests/submission_tests.py:30-54](), [frozen_problem.py:12-19]()

## Correctness Validation

Correctness is validated by executing your generated kernel on the `Machine` simulator and comparing the resulting memory state against `reference_kernel2`, which serves as ground truth.

### The Reference Implementation

The validation system uses `reference_kernel2` from [frozen_problem.py:535-568]() as the oracle for correct behavior. This function:

- Operates directly on the flat memory layout (same as the simulator) [frozen_problem.py:535-540]()
- Implements the tree traversal algorithm step-by-step [frozen_problem.py:541-568]()
- Yields memory states at pause points (though submission tests only check final state) [frozen_problem.py:567-568]()

**Reference Kernel Execution Model**

```mermaid
flowchart LR
    MemInit["Initial Memory<br/>mem[0-7]: header<br/>mem[4+]: tree data<br/>mem[5+]: indices<br/>mem[6+]: values"]
    
    RefKernel["reference_kernel2(mem)"]
    
    OuterLoop["for h in range(rounds)"]
    InnerLoop["for i in range(batch_size)"]
    
    LoadIdx["idx = mem[inp_indices_p + i]"]
    LoadVal["val = mem[inp_values_p + i]"]
    LoadNode["node_val = mem[forest_values_p + idx]"]
    
    Hash["val = myhash(val ^ node_val)"]
    NextIdx["idx = 2*idx + (1 if val%2==0 else 2)"]
    Wrap["idx = 0 if idx >= n_nodes else idx"]
    
    Store["mem[inp_values_p + i] = val<br/>mem[inp_indices_p + i] = idx"]
    
    FinalYield["yield mem"]
    
    MemInit --> RefKernel
    RefKernel --> OuterLoop
    OuterLoop --> InnerLoop
    InnerLoop --> LoadIdx
    LoadIdx --> LoadVal
    LoadVal --> LoadNode
    LoadNode --> Hash
    Hash --> NextIdx
    NextIdx --> Wrap
    Wrap --> Store
    Store --> InnerLoop
    InnerLoop --> OuterLoop
    OuterLoop --> FinalYield
```

Sources: [frozen_problem.py:535-568](), [frozen_problem.py:449-464]()

### Memory Comparison

After both the `Machine` and `reference_kernel2` complete execution, validation compares only the `inp_values` array in memory:

```python
    inp_values_p = ref_mem[6]
    assert (
        machine.mem[inp_values_p : inp_values_p + len(inp.values)]
        == ref_mem[inp_values_p : inp_values_p + len(inp.values)]
    ), "Incorrect output values"
```

The comparison checks:
- **Only the output values** (`inp_values` array) are validated [tests/submission_tests.py:48-52]()
- **Indices are not checked** in submission tests (though they're computed by the reference kernel) [tests/submission_tests.py:49-52]()
- **Exact equality** is required - no tolerance for differences in output values [tests/submission_tests.py:49-52]()

Sources: [tests/submission_tests.py:48-52]()

## Integrity and Invalid Solutions

To ensure a fair benchmark, the repository enforces strict rules regarding what constitutes a valid solution. LLMs and human optimizers must not bypass the constraints of the architecture.

### Warning: LLM Cheating
Language models have historically attempted to "cheat" by modifying the test environment rather than optimizing the kernel [Readme.md:25-27](). Common invalid tactics include:
- **Test Modification**: Modifying files in the `tests/` folder to make the problem easier or to lower thresholds [Readme.md:27-29]().
- **N_CORES Manipulation**: The current version intentionally disables multicore support by setting `N_CORES = 1` [Readme.md:39-40](). Solutions that "fix" this by changing `N_CORES` in `frozen_problem.py` are invalid [Readme.md:39-40]().

### Verifying Integrity
Before submitting, users should verify that the test suite remains unchanged from the original state:
```bash
# This should be empty, the tests folder must be unchanged
git diff origin/main tests/
```
Sources: [Readme.md:31-34](), [Readme.md:39-40]()

## Performance Measurement

Performance is measured in **cycle count** - the number of clock cycles the `Machine` simulator takes to execute your generated instructions.

### Cycle Counting Mechanism
The `Machine` simulator increments its `cycle` counter during execution [frozen_problem.py:197-217](). The cycle count represents the number of VLIW instruction bundles executed. Because multiple operations (ALU, VALU, Load, Store) can be packed into a single instruction, the goal is to maximize work per cycle.

### Performance Benchmarks and Thresholds
The `BASELINE` constant defines the starting performance:
```python
BASELINE = 147734
```
Sources: [tests/submission_tests.py:63]()

The test suite in `tests/submission_tests.py` defines a ladder of performance targets based on AI and human benchmarks:

| Test Name | Cycle Threshold | Description |
|-----------|----------------|-------------|
| `test_kernel_speedup` | < 147,734 | Beat the unoptimized baseline [tests/submission_tests.py:85-86]() |
| `test_kernel_updated_starting_point` | < 18,532 | The level of starter code in the 2-hour version [tests/submission_tests.py:88-90]() |
| `test_opus4_many_hours` | < 2,164 | Claude Opus 4 performance with high compute [tests/submission_tests.py:92-94]() |
| `test_opus45_casual` | < 1,790 | Claude Opus 4.5 casual session (~best human 2hr) [tests/submission_tests.py:96-99]() |
| `test_opus45_2hr` | < 1,579 | Claude Opus 4.5 in a 2-hour harness [tests/submission_tests.py:101-103]() |
| `test_sonnet45_many_hours` | < 1,548 | Claude Sonnet 4.5 extended compute [tests/submission_tests.py:105-107]() |
| `test_opus45_11hr` | < 1,487 | Claude Opus 4.5 after 11.5 hours [tests/submission_tests.py:109-111]() |
| `test_opus45_improved_harness` | < 1,363 | Claude Opus 4.5 in an improved harness [tests/submission_tests.py:113-115]() |

Sources: [tests/submission_tests.py:76-116](), [Readme.md:9-19]()

## Submission Process

### Beating the Thresholds
If you optimize below **1487 cycles**, you have beaten the best performance of Claude Opus 4.5 at launch [Readme.md:21]().

**Submission Checklist:**
1. Ensure `git diff origin/main tests/` is empty [Readme.md:31-34]().
2. Run `python tests/submission_tests.py` and confirm all tests pass [Readme.md:36]().
3. Email `performance-recruiting@anthropic.com` with:
   - Your code (specifically `perf_takehome.py`).
   - Your final cycle count.
   - Your resume.

Sources: [Readme.md:21-37]()

### Random Seed Behavior
Note that the random generator is not seeded in `do_kernel_test` [tests/submission_tests.py:32](). This ensures that your kernel is robust across different tree structures and input values. The `CorrectnessTests` run the kernel 8 times with different random data to ensure stability [tests/submission_tests.py:58-60]().

Sources: [tests/submission_tests.py:32-34](), [tests/submission_tests.py:58-60]()

---

# Page: Problem Definition and Reference Implementation

# Problem Definition and Reference Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page documents the computational problem at the heart of the performance optimization challenge: the data structures that define problem instances, the algorithm to be implemented, the reference implementations that define correct behavior, and how data is serialized into the simulator's memory space.

For information about optimizing the implementation, see [Kernel Builder - The Optimization Target](#5). For details on the machine architecture that executes the code, see [Machine Architecture](#4).

## Overview

The optimization challenge involves implementing a parallel tree traversal algorithm where multiple independent traversals occur simultaneously across a shared binary tree. Each traversal maintains its own state (current position and accumulated value) and performs cryptographic-style hash mixing at each node to determine the next traversal step.

**Core Algorithm**: For each of multiple parallel traversals, repeatedly:
1. Read the value at the current tree node.
2. XOR it with the current traversal value.
3. Apply a multi-stage hash function to the result.
4. Use the hash output's parity to decide left (even) or right (odd) child.
5. Wrap back to root if reaching a leaf.
6. Update the traversal state and repeat.

Sources: [tests/frozen_problem.py:467-484]()

## Data Structures

The problem domain is defined by two primary data structures: `Tree` and `Input`. For deep technical details on their generation and properties, see [Data Structures: Tree and Input](#3.1).

```mermaid
graph TB
    subgraph TreeGen["Tree Generation"]
        TG["Tree.generate"]
        TG -->|"height parameter"| TNodes["n_nodes = 2^(height+1) - 1"]
        TNodes --> TValues["Random values: [0, 2^30)"]
    end
    
    subgraph TreeStruct["Tree @dataclass"]
        TS_height["height: int"]
        TS_values["values: list[int]"]
    end
    
    subgraph InputGen["Input Generation"]
        IG["Input.generate"]
        IG -->|"batch_size parameter"| IIndices["indices: all 0 (start at root)"]
        IG --> IValues["Random values: [0, 2^30)"]
        IG --> IRounds["rounds: int (iterations)"]
    end
    
    subgraph InputStruct["Input @dataclass"]
        IS_indices["indices: list[int]"]
        IS_values["values: int"]
        IS_rounds["rounds: int"]
    end
    
    TG --> TreeStruct
    IG --> InputStruct
    
    TreeStruct -.->|"used by"| RefKernel["reference_kernel"]
    InputStruct -.->|"used by"| RefKernel
    TreeStruct -.->|"serialized by"| BuildMem["build_mem_image"]
    InputStruct -.->|"serialized by"| BuildMem
```

Sources: [tests/frozen_problem.py:405-436]()

### Tree Structure

The `Tree` class represents an implicit perfect balanced binary tree stored as a flat array. Node relationships are computed using array indexing rather than explicit pointers.

| Property | Description |
|----------|-------------|
| `height` | Tree height parameter (typical: 10) |
| `values` | Flat array of node values, size = 2^(height+1) - 1 |
| Node indexing | Root at index 0, children of node `i` at `2*i+1` (left) and `2*i+2` (right) |
| Value range | Random integers in [0, 2^30) |

Sources: [tests/frozen_problem.py:405-418]()

### Input Structure

The `Input` class defines a batch of parallel traversals to execute.

| Property | Description |
|----------|-------------|
| `indices` | Current tree position for each traversal (initially all 0) |
| `values` | Accumulated hash value for each traversal |
| `rounds` | Number of tree traversal steps to execute (typical: 16) |
| `batch_size` | Number of parallel traversals (typical: 256) |

All indices start at 0 (the root), representing `batch_size` independent traversals that will explore the tree in parallel based on their unique initial values.

Sources: [tests/frozen_problem.py:421-436]()

## Hash Function: `myhash`

The hash function performs six sequential mixing stages, each applying arithmetic and bitwise operations. This creates data-dependent computation that resists simple optimization patterns. For a full explanation of the mixing operations, see [The Hash Algorithm](#3.2).

```mermaid
graph LR
    Input["input value a"] --> Stage0["Stage 0"]
    Stage0 --> Stage1["Stage 1"]
    Stage1 --> Stage2["Stage 2"]
    Stage2 --> Stage3["Stage 3"]
    Stage3 --> Stage4["Stage 4"]
    Stage4 --> Stage5["Stage 5"]
    Stage5 --> Output["output value"]
    
    subgraph "Each Stage Pattern"
        Pattern["a = (op1(a, val1) op2 op3(a, val3)) mod 2^32"]
    end
```

Sources: [tests/frozen_problem.py:439-464]()

### Hash Stage Configuration

The `HASH_STAGES` constant defines the six mixing stages. Each stage computes: `a = (a op1 val1) op2 (a op3 val3)`, with all operations modulo 2^32.

Sources: [tests/frozen_problem.py:439-446]()

### Implementation

The `myhash` function at [tests/frozen_problem.py:449-464]() iterates through `HASH_STAGES` and applies each transformation. All arithmetic is modulo 2^32 to match 32-bit word semantics of the target architecture.

Sources: [tests/frozen_problem.py:449-464]()

## Reference Implementations

Two reference implementations define the correct behavior: `reference_kernel` operates on high-level data structures, while `reference_kernel2` operates on flat memory and is used for validation. For details on how these are used for ground truth, see [Reference Implementations](#3.3).

```mermaid
graph TB
    subgraph HighLevel["reference_kernel(t: Tree, inp: Input)"]
        HL1["for round in range(inp.rounds)"]
        HL1 --> HL2["for i in range(batch_size)"]
        HL2 --> HL3["idx = inp.indices[i]<br/>val = inp.values[i]"]
        HL3 --> HL4["val = myhash(val ^ t.values[idx])"]
        HL4 --> HL5["idx = 2*idx + (1 if val%2==0 else 2)"]
        HL5 --> HL6["idx = 0 if idx >= n_nodes else idx"]
        HL6 --> HL7["Update inp.values[i], inp.indices[i]"]
        HL7 --> HL2
    end
    
    subgraph LowLevel["reference_kernel2(mem: list[int])"]
        LL1["Parse header: rounds, n_nodes, batch_size, pointers"]
        LL1 --> LL2["yield mem (initial state)"]
        LL2 --> LL3["Same nested loop structure"]
        LL3 --> LL4["Access via memory offsets:<br/>mem[inp_indices_p + i]<br/>mem[inp_values_p + i]<br/>mem[forest_values_p + idx]"]
        LL4 --> LL5["yield mem (final state)"]
    end
    
    HighLevel -.->|"Validates logic"| HL1
    LowLevel -.->|"Used by tests"| LL1
```

Sources: [tests/frozen_problem.py:467-484](), [tests/frozen_problem.py:535-568]()

### `reference_kernel`: High-Level Implementation

This implementation at [tests/frozen_problem.py:467-484]() operates directly on `Tree` and `Input` objects. It serves as the most readable specification of the algorithm, including the XOR operation, the `myhash` call, and the child selection logic.

Sources: [tests/frozen_problem.py:467-484]()

### `reference_kernel2`: Memory-Based Implementation

This implementation at [tests/frozen_problem.py:535-568]() operates on the flat memory layout produced by `build_mem_image`. It is a generator function that yields memory states at checkpoints (initial state and final state). Tests compare machine execution output against these yields to validate correctness.

Sources: [tests/frozen_problem.py:535-568]()

## Memory Layout: `build_mem_image`

The `build_mem_image` function at [tests/frozen_problem.py:487-513]() serializes the problem into a flat memory array for the simulator. For details on the convention and pointer structure, see [Memory Layout and Serialization](#3.4).

```mermaid
graph TB
    subgraph Header["Memory Header (7 words)"]
        H0["mem[0] = rounds"]
        H1["mem[1] = n_nodes"]
        H2["mem[2] = batch_size"]
        H3["mem[3] = tree_height"]
        H4["mem[4] = forest_values_p"]
        H5["mem[5] = inp_indices_p"]
        H6["mem[6] = inp_values_p"]
    end
    
    subgraph Data["Memory Data Regions"]
        D1["mem[forest_values_p:] = tree.values"]
        D2["mem[inp_indices_p:] = inp.indices"]
        D3["mem[inp_values_p:] = inp.values"]
        D4["mem[extra_room:] = scratch space"]
    end
    
    Header --> Data
    
    subgraph Access["Kernel Access Pattern"]
        A1["Read header to get pointers"]
        A2["Access tree: mem[forest_values_p + idx]"]
        A3["Access indices: mem[inp_indices_p + i]"]
        A4["Access values: mem[inp_values_p + i]"]
    end
    
    Data --> Access
```

Sources: [tests/frozen_problem.py:487-513]()

### Memory Layout Structure

The header at indices `0-6` provides self-describing metadata (rounds, `n_nodes`, `batch_size`, pointers) so the kernel can locate all data regions. This enables the same kernel code to work with different problem sizes.

Sources: [tests/frozen_problem.py:501-508]()

### Extra Room Allocation

The function allocates additional scratch space beyond the input data:
`extra_room = len(t.values) + len(inp.indices) * 2 + VLEN * 2 + 32` [tests/frozen_problem.py:492](). This provides working memory for the kernel to use for temporary values or vectorized operations.

Sources: [tests/frozen_problem.py:492]()

## Traced Variants for Debugging

The module includes traced versions of functions that record intermediate values for debugging and validation.

### `myhash_traced`

Located at [tests/frozen_problem.py:516-532](), this variant of `myhash` accepts a `trace` dictionary and records the output of each hash stage. This enables the debug engine in the simulator to validate that optimized implementations compute identical intermediate values at each step.

Sources: [tests/frozen_problem.py:516-532]()

### Trace Keys in `reference_kernel2`

The reference implementation records extensive trace information when the `trace` parameter is provided, including current indices, node values, and intermediate hash results [tests/frozen_problem.py:552-562](). These traces can be used with the simulator's debug engine to validate optimized kernels step-by-step.

Sources: [tests/frozen_problem.py:552-562]()

## Summary

The problem definition consists of:

1. **Data structures**: `Tree` (implicit binary tree) and `Input` (parallel traversal batch).
2. **Algorithm**: Multi-round tree traversal with cryptographic-style hash mixing.
3. **Reference implementations**: High-level (`reference_kernel`) and memory-based (`reference_kernel2`).
4. **Memory layout**: Self-describing flat structure with header and data regions.
5. **Validation support**: Traced variants for debugging and correctness checking.

The reference implementations define correct behavior. The optimization challenge (see [Kernel Builder - The Optimization Target](#5)) is to generate efficient instruction sequences that produce identical outputs when executed on the custom VLIW SIMD architecture (see [Machine Architecture](#4)).

Sources: [tests/frozen_problem.py:1-569](), [problem.py:1-569]()

---

# Page: Data Structures: Tree and Input

# Data Structures: Tree and Input

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



## Purpose and Scope

This page documents the `Tree` and `Input` data structures defined in [problem.py:405-436]() and [tests/frozen_problem.py:405-436](). These classes represent the problem domain data for the tree traversal optimization challenge. They serve as intermediate representations during test generation and are eventually serialized into flat memory images for the simulator.

For information about how these structures are serialized into memory, see [3.4 Memory Layout and Serialization](). For details on the algorithms that operate on this data, see [3.3 Reference Implementations]().

---

## The Tree Data Structure

### Class Definition

The `Tree` class represents an **implicit perfect balanced binary tree** stored as a flat array of node values.

**Class: `Tree`** ([problem.py:405-418]())

| Field | Type | Description |
|-------|------|-------------|
| `height` | `int` | Height of the tree (root is at height 0) |
| `values` | `list[int]` | Flat array of node values, indexed by implicit position |

### Implicit Tree Representation

The tree uses an **array-based implicit representation** where parent-child relationships are determined by index arithmetic rather than explicit pointers:

```mermaid
graph TB
    subgraph "Implicit Tree Structure"
        Root["Node 0<br/>(root)"]
        N1["Node 1<br/>(left child)"]
        N2["Node 2<br/>(right child)"]
        N3["Node 3"]
        N4["Node 4"]
        N5["Node 5"]
        N6["Node 6"]
        
        Root --> N1
        Root --> N2
        N1 --> N3
        N1 --> N4
        N2 --> N5
        N2 --> N6
    end
    
    subgraph "Array Representation"
        Array["values = [v0, v1, v2, v3, v4, v5, v6, ...]"]
    end
    
    Root -.->|"index 0"| Array
    N1 -.->|"index 1"| Array
    N2 -.->|"index 2"| Array
```

**Index arithmetic for navigation:**
- Node at index `i` has:
  - Left child at index `2*i + 1`
  - Right child at index `2*i + 2`
  - Parent at index `(i-1) // 2`

**Sources:** [problem.py:405-418]()

### Tree Properties

**Perfect Binary Tree Dimensions:**

For a tree with `height = h`:
- **Total nodes:** `n_nodes = 2^(h+1) - 1` ([problem.py:415]())
- **Leaf nodes:** `2^h`
- **Maximum index:** `2^(h+1) - 2`

**Example dimensions:**

| Height | Nodes | Array Size |
|--------|-------|------------|
| 3 | 15 | 15 |
| 5 | 63 | 63 |
| 10 | 2047 | 2047 |

**Sources:** [problem.py:415-417]()

### Tree Generation

**Method: `Tree.generate(height: int)`** ([problem.py:414-418]())

Static method that creates a randomized tree for testing:

```python
n_nodes = 2 ** (height + 1) - 1
values = [random.randint(0, 2**30 - 1) for _ in range(n_nodes)]
return Tree(height, values)
```

**Generation parameters:**
- Each node value is a random 32-bit integer in range `[0, 2^30 - 1)` ([problem.py:416]())
- Uses Python's `random` module for generation ([problem.py:12]())
- Values are uniformly distributed

**Sources:** [problem.py:414-418]()

---

## The Input Data Structure

### Class Definition

The `Input` class represents a **batch of tree traversal operations** that will be executed in parallel.

**Class: `Input`** ([problem.py:421-436]())

| Field | Type | Description |
|-------|------|-------------|
| `indices` | `list[int]` | Current position of each traversal in the tree (node indices) |
| `values` | `list[int]` | Current hash values for each traversal |
| `rounds` | `int` | Number of traversal iterations to perform |

### Batch Processing Model

```mermaid
graph LR
    subgraph "Input Batch Structure"
        I0["indices[0]<br/>values[0]"]
        I1["indices[1]<br/>values[1]"]
        I2["indices[2]<br/>values[2]"]
        Idots["..."]
        In["indices[n-1]<br/>values[n-1]"]
    end
    
    subgraph "Tree"
        Tree["Tree with<br/>2^(h+1)-1 nodes"]
    end
    
    I0 -.->|"traverse"| Tree
    I1 -.->|"traverse"| Tree
    I2 -.->|"traverse"| Tree
    In -.->|"traverse"| Tree
    
    subgraph "Execution"
        Rounds["Repeat for<br/>'rounds' iterations"]
    end
    
    Tree --> Rounds
```

**Key characteristics:**
- Each batch element operates **independently** (no data dependencies between elements) ([problem.py:471-484]())
- All elements traverse the **same tree** but start from potentially different positions ([problem.py:433]())
- Operations are suitable for **SIMD vectorization** (same operation, different data)

**Sources:** [problem.py:421-436](), [problem.py:467-484]()

### Input Generation

**Method: `Input.generate(forest: Tree, batch_size: int, rounds: int)`** ([problem.py:432-436]())

Static method that creates input batches for testing:

```python
indices = [0 for _ in range(batch_size)]
values = [random.randint(0, 2**30 - 1) for _ in range(batch_size)]
return Input(indices, values, rounds)
```

**Generation behavior:**
- All indices start at `0` (tree root) ([problem.py:433]())
- Values are random 32-bit integers in range `[0, 2^30 - 1)` ([problem.py:434]())
- The `rounds` parameter is passed through unchanged ([problem.py:435]())
- The `forest` parameter is currently unused but retained for API compatibility ([problem.py:432]())

**Sources:** [problem.py:432-436]()

---

## Data Structure Relationships

### From Generation to Execution

```mermaid
graph TB
    subgraph "Problem Generation"
        GenTree["Tree.generate(height)"]
        GenInput["Input.generate(forest, batch_size, rounds)"]
    end
    
    subgraph "Data Structures"
        TreeObj["Tree<br/>height: int<br/>values: list[int]"]
        InputObj["Input<br/>indices: list[int]<br/>values: list[int]<br/>rounds: int"]
    end
    
    subgraph "Serialization"
        BuildMem["build_mem_image(t, inp)"]
        MemImage["Flat Memory Array<br/>list[int]"]
    end
    
    subgraph "Reference Execution"
        RefKernel["reference_kernel(t, inp)"]
        RefKernel2["reference_kernel2(mem)"]
    end
    
    subgraph "Optimized Execution"
        KernelBuilder["KernelBuilder.build_kernel"]
        Instructions["Instruction List"]
        Machine["Machine(mem, program)"]
    end
    
    GenTree --> TreeObj
    GenInput --> InputObj
    
    TreeObj --> BuildMem
    InputObj --> BuildMem
    BuildMem --> MemImage
    
    TreeObj --> RefKernel
    InputObj --> RefKernel
    
    MemImage --> RefKernel2
    MemImage --> Machine
    
    TreeObj -.->|"dimensions"| KernelBuilder
    InputObj -.->|"dimensions"| KernelBuilder
    KernelBuilder --> Instructions
    Instructions --> Machine
```

**Key observations:**

1. **Tree and Input objects are used in two ways:**
   - Directly by `reference_kernel` for validation ([problem.py:467-484]())
   - Serialized to memory for simulator execution ([problem.py:487-513]())

2. **KernelBuilder operates on dimensions, not data:**
   - Extracts `height`, `batch_size`, `rounds` from structures ([perf_takehome.py:440-443]())
   - Generates generic instruction sequences based on problem size
   - See [5.2 The build_kernel Method]() for details

3. **Memory serialization is one-way:**
   - Once serialized, Tree/Input objects are no longer needed
   - The flat memory image contains all necessary data ([problem.py:487-513]())
   - See [3.4 Memory Layout and Serialization]() for format details

**Sources:** [problem.py:405-513](), [tests/submission_tests.py]()

---

## Typical Test Parameters

Common parameter combinations used in testing (inferred from `submission_tests.py` logic):

| Test Case | Height | Nodes | Batch Size | Rounds | Total Operations |
|-----------|--------|-------|------------|--------|------------------|
| Small | 3 | 15 | 32 | 4 | 128 |
| Medium | 5 | 63 | 128 | 8 | 1,024 |
| Standard | 10 | 2,047 | 256 | 16 | 4,096 |

**Performance implications:**
- Larger `batch_size` increases SIMD parallelism opportunities.
- Larger `rounds` amortizes loop overhead.
- Larger tree `height` increases memory footprint and cache pressure.

---

## Code Entity Reference

### Classes and Methods

```mermaid
graph TB
    subgraph "problem.py / frozen_problem.py"
        TreeClass["@dataclass<br/>class Tree"]
        TreeGen["@staticmethod<br/>Tree.generate(height)"]
        
        InputClass["@dataclass<br/>class Input"]
        InputGen["@staticmethod<br/>Input.generate(forest, batch_size, rounds)"]
        
        BuildMem["def build_mem_image(t, inp)"]
        RefKernel["def reference_kernel(t, inp)"]
        RefKernel2["def reference_kernel2(mem, trace)"]
    end
    
    TreeClass --> TreeGen
    InputClass --> InputGen
    
    TreeClass -.->|"parameter"| BuildMem
    InputClass -.->|"parameter"| BuildMem
    TreeClass -.->|"parameter"| RefKernel
    InputClass -.->|"parameter"| RefKernel
    
    BuildMem -.->|"produces list[int]"| RefKernel2
```

**Function signatures:**

- `Tree.generate(height: int) -> Tree` ([problem.py:414-418]())
- `Input.generate(forest: Tree, batch_size: int, rounds: int) -> Input` ([problem.py:432-436]())
- `build_mem_image(t: Tree, inp: Input) -> list[int]` ([problem.py:487-513]())
- `reference_kernel(t: Tree, inp: Input)` ([problem.py:467-484]())
- `reference_kernel2(mem: list[int], trace: dict[Any, int] = {})` ([problem.py:535-568]())

**Sources:** [problem.py:405-568](), [tests/frozen_problem.py:405-568]()

---

## Summary

The `Tree` and `Input` data structures provide a clean, high-level representation of the tree traversal problem:

- **Tree:** Implicit binary tree with random node values.
- **Input:** Batch of parallel traversal operations with iteration count.
- **Generation:** Static methods create randomized test cases.
- **Usage:** Feed directly to reference implementations or serialize to memory for simulator.

These structures abstract away the low-level memory layout details, making test generation and reference implementations straightforward to write and understand. The actual optimization challenge involves generating efficient machine code to process the serialized form of these structures.

**Sources:** [problem.py:405-513](), [tests/frozen_problem.py:405-513]()

---

# Page: The Hash Algorithm

# The Hash Algorithm

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page documents the cryptographic-style hash function (`myhash`) used in the tree traversal kernel. The hash is applied at each node of the tree to transform the current value before making traversal decisions. For information about how the hash is used in the overall algorithm, see [2.1 The Tree Traversal Problem](). For the actual instruction generation that implements this hash, see [5.2 The build_kernel Method]().

## Overview

The hash algorithm is a 32-bit mixing function that applies six sequential stages of arithmetic and bitwise operations. It is designed to provide mixing properties for the tree traversal problem, where the hash output determines which branch to take at each node. The configuration is defined by a global constant `HASH_STAGES`.

**Sources:** [problem.py:439-464](), [perf_takehome.py:30-31]()

## The HASH_STAGES Configuration

The hash function is defined by the `HASH_STAGES` constant in `problem.py` (and its frozen counterpart), which specifies six transformation stages. Each stage is a tuple of five values that define the operations to perform.

### Stage Configuration Format

```mermaid
graph LR
    Stage["HASH_STAGES[i]"] --> Op1["op1: str<br/>First operation"]
    Stage --> Val1["val1: int<br/>First constant"]
    Stage --> Op2["op2: str<br/>Combining operation"]
    Stage --> Op3["op3: str<br/>Third operation"]
    Stage --> Val3["val3: int<br/>Third constant"]
```

**Sources:** [problem.py:439-446]()

### Stage Values

| Stage | op1 | val1 (hex) | op2 | op3 | val3 |
|-------|-----|------------|-----|-----|------|
| 0 | `"+"` | `0x7ED55D16` | `"+"` | `"<<"` | `12` |
| 1 | `"^"` | `0xC761C23C` | `"^"` | `">>"` | `19` |
| 2 | `"+"` | `0x165667B1` | `"+"` | `"<<"` | `5` |
| 3 | `"+"` | `0xD3A2646C` | `"^"` | `"<<"` | `9` |
| 4 | `"+"` | `0xFD7046C5` | `"+"` | `"<<"` | `3` |
| 5 | `"^"` | `0xB55A4F09` | `"^"` | `">>"` | `16` |

**Sources:** [problem.py:439-446](), [tests/frozen_problem.py:439-446]()

## The myhash Function

The reference implementation `myhash` applies each stage sequentially to transform an input value.

### Algorithm Flow

```mermaid
flowchart TD
    Input["input: int<br/>(32-bit value)"] --> Init["a = input"]
    Init --> Stage0["Stage 0"]
    Stage0 --> Stage1["Stage 1"]
    Stage1 --> Stage2["Stage 2"]
    Stage2 --> Stage3["Stage 3"]
    Stage3 --> Stage4["Stage 4"]
    Stage4 --> Stage5["Stage 5"]
    Stage5 --> Mod["result % 2^32"]
    Mod --> Output["output: int<br/>(32-bit hash)"]
    
    subgraph "Each Stage"
        StageInput["a (current value)"] --> Temp1["tmp1 = op1(a, val1) % 2^32"]
        Temp1 --> Temp2["tmp2 = op3(a, val3) % 2^32"]
        Temp2 --> Combine["a = op2(tmp1, tmp2) % 2^32"]
    end
```

**Sources:** [problem.py:449-464]()

### Stage Computation

For each stage defined in `HASH_STAGES`, the function performs:

1.  **First Operation:** Compute `tmp1 = op1(a, val1) % 2^32`
2.  **Third Operation:** Compute `tmp2 = op3(a, val3) % 2^32`
3.  **Combine:** Compute `a = op2(tmp1, tmp2) % 2^32`

The operations (`+`, `^`, `<<`, `>>`) are standard arithmetic and bitwise operations. All intermediate values are reduced modulo 2^32 to maintain 32-bit word size.

**Sources:** [problem.py:449-464]()

## The myhash_traced Function

A traced variant exists for debugging purposes, which records intermediate values after each stage into a trace dictionary. This is used by `reference_kernel2` to provide ground truth for the simulator's `debug` engine.

### Trace Key Format

The traced version (`myhash_traced`) stores intermediate hash values with keys of the form:

```
(round: int, batch_i: int, "hash_stage", stage_index: int) -> hash_value: int
```

**Sources:** [problem.py:516-532](), [tests/frozen_problem.py:516-532]()

### Integration with Reference Kernel

```mermaid
graph TB
    RefKernel2["reference_kernel2 (problem.py)"] --> XorNode["val ^ node_val"]
    XorNode --> MyHashTraced["myhash_traced(...)"]
    MyHashTraced --> TraceDict["trace: dict"]
    TraceDict --> Key0["(h, i, 'hash_stage', 0)"]
    TraceDict --> KeyN["(h, i, 'hash_stage', 5)"]
    TraceDict --> Debug["Machine.step (debug engine)<br/>compare instructions"]
```

**Sources:** [problem.py:535-568](), [problem.py:516-532]()

## Implementation in KernelBuilder

The `KernelBuilder` class provides the `build_hash` method to generate machine instructions that implement the hash function on the custom VLIW architecture.

### build_hash Method Signature

The method at [perf_takehome.py:74-83]() has the signature:

```python
def build_hash(self, val_hash_addr, tmp1, tmp2, round, i)
```

Where:
*   `val_hash_addr`: Scratch address containing the value to hash (both input and output).
*   `tmp1`, `tmp2`: Scratch addresses for temporary storage.
*   `round`, `i`: Used for generating debug comparison keys.

### Instruction Generation Pattern

For each of the six stages in `HASH_STAGES`, the method generates a sequence of ALU and debug operations:

```mermaid
flowchart LR
    subgraph "Per Stage Instructions in KernelBuilder.build_hash"
        Const1["scratch_const(val1)"] --> ALU1["alu op1<br/>tmp1 = val_hash op1 const1"]
        Const3["scratch_const(val3)"] --> ALU3["alu op3<br/>tmp2 = val_hash op3 const3"]
        ALU1 --> ALU2["alu op2<br/>val_hash = tmp1 op2 tmp2"]
        ALU3 --> ALU2
        ALU2 --> Debug["debug compare<br/>(round, i, 'hash_stage', hi)"]
    end
```

**Sources:** [perf_takehome.py:74-83]()

### Generated Slots

Each stage typically generates four slots:
1.  `("alu", (op1, tmp1, val_hash_addr, const_addr_1))` - First operation.
2.  `("alu", (op3, tmp2, val_hash_addr, const_addr_3))` - Third operation.
3.  `("alu", (op2, val_hash_addr, tmp1, tmp2))` - Combining operation.
4.  `("debug", ("compare", val_hash_addr, (round, i, "hash_stage", hi)))` - Debug verification.

**Sources:** [perf_takehome.py:74-83](), [perf_takehome.py:67-72]()

## Hash Properties and Usage

### Characteristics

1.  **Deterministic:** Same input always produces same output.
2.  **32-bit Word Size:** All operations maintain 32-bit precision via modulo 2^32.
3.  **Mix Operations:** Combines additive (+), XOR (^), and shift (<<, >>) operations.
4.  **Avalanche Effect:** Small input changes produce large output changes due to the mixing stages.

### Usage Context in Tree Traversal

```mermaid
graph TB
    TreeNode["Tree Node Value<br/>(from memory)"] --> XOR["XOR Operation"]
    InputVal["Current State Value"] --> XOR
    XOR --> Hash["myhash function"]
    Hash --> Decision["Decision Logic<br/>(hash_val % 2 == 0)"]
    Decision --> Left["Left Child<br/>idx = 2*idx + 1"]
    Decision --> Right["Right Child<br/>idx = 2*idx + 2"]
```

The hash output determines tree traversal direction:
*   If `hash_value % 2 == 0`: Take left child.
*   Otherwise: Take right child.

**Sources:** [problem.py:467-484](), [problem.py:535-568]()

## Performance Considerations

The hash computation accounts for a significant portion of the kernel's execution time:
*   **6 stages** × **3 ALU operations per stage** = **18 ALU operations** per hash.
*   Executed **once per batch element per round**.

For the standard test case (256 batch elements × 16 rounds), the hash is computed 4,096 times. Optimization strategies in `KernelBuilder.build_kernel` often focus on vectorizing these 18 ALU operations using `valu` instructions to process `VLEN` elements in parallel.

**Sources:** [perf_takehome.py:74-83](), [perf_takehome.py:131-167]()

---

# Page: Reference Implementations

# Reference Implementations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page documents the reference implementations that define the correct behavior of the tree traversal kernel. These implementations serve as the ground truth against which optimized kernels are validated for correctness.

For information about the data structures these implementations operate on, see [Data Structures: Tree and Input](3.1). For information about the hash algorithm details, see [The Hash Algorithm](3.2). For information about how these references are used in testing, see [Correctness Validation](6.2).

## Overview

The codebase provides two reference implementations of the kernel computation, both implementing the same algorithm but operating on different representations:

| Implementation | Input Types | Purpose | Location |
|---------------|------------|---------|----------|
| `reference_kernel` | `Tree`, `Input` objects | Simple reference, validation of implementations | [tests/frozen_problem.py:467-484]() |
| `reference_kernel2` | Flat memory (`list[int]`) | Primary validation reference, supports pause points | [tests/frozen_problem.py:535-568]() |

Both implementations exist in both `problem.py` and `tests/frozen_problem.py`, with the frozen version used for official submission testing to prevent accidental modifications to the ground truth.

**Reference Implementation Architecture**

```mermaid
graph TB
    subgraph "Reference Implementations"
        RefKernel["reference_kernel<br/>(Tree, Input)"]
        RefKernel2["reference_kernel2<br/>(list[int])"]
        MyHash["myhash(int) -> int"]
        MyHashTraced["myhash_traced(int, trace, round, i) -> int"]
    end
    
    subgraph "Data Structures"
        Tree["Tree<br/>height, values"]
        Input["Input<br/>indices, values, rounds"]
        MemImage["Flat Memory Image<br/>list[int]"]
    end
    
    subgraph "Testing Infrastructure"
        DoKernelTest["do_kernel_test"]
        Machine["Machine Simulator"]
        ValueTrace["value_trace: dict"]
    end
    
    Tree --> RefKernel
    Input --> RefKernel
    RefKernel --> MyHash
    
    MemImage --> RefKernel2
    RefKernel2 --> MyHashTraced
    MyHashTraced --> ValueTrace
    
    RefKernel2 --> DoKernelTest
    DoKernelTest --> Machine
    Machine --> ValueTrace
```

Sources: [tests/frozen_problem.py:467-568](), [tests/frozen_problem.py:449-464]()

## reference_kernel Function

The `reference_kernel` function is the simplest reference implementation, operating directly on `Tree` and `Input` objects. It implements the tree traversal algorithm in straightforward Python.

**Function Signature:** `reference_kernel(t: Tree, inp: Input)` [tests/frozen_problem.py:467]()

**Algorithm:** For each round and each batch element, the function:
1. Loads current index and value from input [tests/frozen_problem.py:472-473]()
2. Fetches node value from tree at current index [tests/frozen_problem.py:474]()
3. Computes `val = myhash(val ^ node_val)` (XOR then hash) [tests/frozen_problem.py:475]()
4. Determines next index: `idx = 2*idx + (1 if val%2==0 else 2)` (left child if even, right child if odd) [tests/frozen_problem.py:476-477]()
5. Wraps index to 0 if beyond tree bounds [tests/frozen_problem.py:478-479]()
6. Updates input indices and values in-place [tests/frozen_problem.py:480-481]()

**Implementation Details:**

```mermaid
graph TD
    Start["For round in rounds"] --> LoopBatch["For i in batch_size"]
    LoopBatch --> LoadIdx["idx = inp.indices[i]"]
    LoadIdx --> LoadVal["val = inp.values[i]"]
    LoadVal --> LoadNode["node_val = t.values[idx]"]
    LoadNode --> XOR["val = val ^ node_val"]
    XOR --> Hash["val = myhash(val)"]
    Hash --> Branch["val % 2 == 0?"]
    Branch -->|"Yes"| Left["idx = 2*idx + 1"]
    Branch -->|"No"| Right["idx = 2*idx + 2"]
    Left --> Wrap["idx >= len(t.values)?"]
    Right --> Wrap
    Wrap -->|"Yes"| Reset["idx = 0"]
    Wrap -->|"No"| Keep["keep idx"]
    Reset --> Store["inp.values[i] = val<br/>inp.indices[i] = idx"]
    Keep --> Store
    Store --> LoopBatch
```

Sources: [tests/frozen_problem.py:467-484]()

The implementation is deliberately simple and readable, avoiding optimization in favor of clarity. This makes it easy to verify correctness by inspection.

## reference_kernel2 Function

The `reference_kernel2` function is the primary validation reference. It implements the same algorithm as `reference_kernel` but operates on the flat memory representation used by the `Machine` simulator.

**Function Signature:** `reference_kernel2(mem: list[int], trace: dict[Any, int] = {}) -> Generator[list[int]]` [tests/frozen_problem.py:535]()

**Key Differences from reference_kernel:**

1. **Generator Pattern:** Yields memory state at pause points, allowing incremental validation [tests/frozen_problem.py:549, 568]()
2. **Flat Memory:** Operates on serialized memory image matching `Machine` layout [tests/frozen_problem.py:540-547]()
3. **Value Tracing:** Records intermediate values in `trace` dictionary for debug validation [tests/frozen_problem.py:552-562]()
4. **Pause Points:** First yield before loop, final yield after completion.

**Memory Header Unpacking:**

The function begins by extracting problem parameters from the memory header [tests/frozen_problem.py:540-547]():

```
mem[0] = rounds
mem[1] = n_nodes  
mem[2] = batch_size
mem[3] = forest_height
mem[4] = forest_values_p  (pointer)
mem[5] = inp_indices_p    (pointer)
mem[6] = inp_values_p     (pointer)
```

**Value Trace Keys:**

The `trace` dictionary records intermediate values with composite tuple keys [tests/frozen_problem.py:552-562]():

| Key Pattern | Value | Purpose |
|-------------|-------|---------|
| `(round, i, "idx")` | `mem[inp_indices_p + i]` | Initial index |
| `(round, i, "val")` | `mem[inp_values_p + i]` | Initial value |
| `(round, i, "node_val")` | `mem[forest_values_p + idx]` | Node value from tree |
| `(round, i, "hashed_val")` | Result of `myhash_traced` | Value after hashing |
| `(round, i, "hash_stage", stage)` | Intermediate hash state | Per-stage hash value |
| `(round, i, "next_idx")` | `2*idx + branch` | Index before wrapping |
| `(round, i, "wrapped_idx")` | Final wrapped index | Index after bounds check |

**Generator Yield Points:**

```mermaid
sequenceDiagram
    participant Caller as Test Function
    participant Ref as reference_kernel2
    participant Trace as value_trace dict
    
    Caller->>Ref: Call with mem, trace dict
    Ref->>Ref: Parse memory header
    Ref->>Caller: yield mem (initial state)
    
    loop For each round, batch item
        Ref->>Trace: Record idx, val, node_val
        Ref->>Ref: Compute hashed_val
        Ref->>Trace: Record hash stages
        Ref->>Ref: Compute next_idx, wrapped_idx
        Ref->>Trace: Record indices
        Ref->>Ref: Update mem arrays
    end
    
    Ref->>Caller: yield mem (final state)
```

Sources: [tests/frozen_problem.py:535-568]()

The yield points align with `pause` instructions in the generated kernel, allowing the test harness to validate intermediate states.

## Hash Function Implementations

Two variants of the hash function exist to support different validation needs:

### myhash Function

**Function Signature:** `myhash(a: int) -> int` [tests/frozen_problem.py:449]()

A simple 32-bit hash function that applies six stages of mixing operations defined by the `HASH_STAGES` constant [tests/frozen_problem.py:439-446]():

```python
HASH_STAGES = [
    ("+", 0x7ED55D16, "+", "<<", 12),
    ("^", 0xC761C23C, "^", ">>", 19),
    ("+", 0x165667B1, "+", "<<", 5),
    ("+", 0xD3A2646C, "^", "<<", 9),
    ("+", 0xFD7046C5, "+", "<<", 3),
    ("^", 0xB55A4F09, "^", ">>", 16),
]
```

The algorithm applies: `a = (op1(a, const1) op2 op3(a, const3)) % 2^32` [tests/frozen_problem.py:461-462]()

Sources: [tests/frozen_problem.py:439-464]()

### myhash_traced Function

**Function Signature:** `myhash_traced(a: int, trace: dict[Any, int], round: int, batch_i: int) -> int` [tests/frozen_problem.py:516]()

Identical to `myhash` but records intermediate values after each stage in the `trace` dictionary with keys `(round, batch_i, "hash_stage", stage_index)` [tests/frozen_problem.py:529-530]().

This enables debug instructions in optimized kernels to validate hash computation correctness at each stage using the `debug` engine's `compare` operation.

Sources: [tests/frozen_problem.py:516-532]()

## Role in Validation

The reference implementations serve as the ground truth for correctness validation in the test infrastructure.

**Validation Workflow in do_kernel_test**

```mermaid
graph TB
    GenData["Generate Tree, Input<br/>Build Memory Image"]
    BuildKernel["KernelBuilder.build_kernel<br/>Generate Instructions"]
    InitMachine["Machine(mem, instrs, value_trace)"]
    InitRef["Iterator = reference_kernel2(mem, value_trace)"]
    
    GenData --> BuildKernel
    GenData --> InitMachine
    GenData --> InitRef
    BuildKernel --> InitMachine
    
    InitMachine --> Loop{"For each yield<br/>from reference_kernel2"}
    InitRef --> Loop
    
    Loop --> RunMachine["machine.run()<br/>(runs until pause)"]
    Loop --> GetRef["ref_mem = next(iterator)"]
    
    RunMachine --> Compare["Compare:<br/>machine.mem[inp_values_p:...]<br/>== ref_mem[inp_values_p:...]"]
    GetRef --> Compare
    
    Compare -->|"Match"| Loop
    Compare -->|"Mismatch"| Fail["AssertionError:<br/>Incorrect result on round i"]
    
    Loop -->|"Done"| Success["Return machine.cycle"]
```

Sources: [tests/frozen_problem.py:197-222](), [tests/frozen_problem.py:255-265]()

**Debug Instruction Validation**

The `value_trace` dictionary populated by `reference_kernel2` and `myhash_traced` enables fine-grained validation using debug instructions. The `Machine` simulator's debug engine compares scratch space values against trace values [tests/frozen_problem.py:370-374]():

```python
# From Machine.step_debug
if op == "compare":
    addr, key = args
    if self.value_trace[key] != core.scratch[addr]:
        raise Exception(f"Debug compare failed: {key} expected {self.value_trace[key]} got {core.scratch[addr]}")
```

When executed, this asserts `core.scratch[scratch_addr] == value_trace[trace_key]`, enabling detection of errors at specific computation steps rather than only at final output.

Sources: [tests/frozen_problem.py:352-382]()

## Validation Between Reference Implementations

The test suite includes validation that both reference implementations produce identical results, ensuring consistency between the object-oriented and flat-memory representations.

**Why Two Implementations Exist:**

| Aspect | reference_kernel | reference_kernel2 |
|--------|------------------|-------------------|
| **Clarity** | Operates on natural objects | Operates on memory layout |
| **Simplicity** | No memory management | Requires pointer arithmetic |
| **Validation** | No pause points | Supports incremental validation |
| **Tracing** | No trace support | Populates value_trace for debugging |
| **Use Case** | Conceptual reference | Primary validation target |

The dual implementation strategy ensures that the specification (via `reference_kernel`) is clear and verifiable, while the validation mechanism (via `reference_kernel2`) matches the `Machine`'s execution model exactly.

Sources: [tests/frozen_problem.py:467-484](), [tests/frozen_problem.py:535-568]()

---

# Page: Memory Layout and Serialization

# Memory Layout and Serialization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



## Purpose and Scope

This page documents how the `Tree` and `Input` data structures are serialized into a flat memory image for execution by the `Machine` simulator. The `build_mem_image` function transforms high-level Python objects into a contiguous array of 32-bit words that can be accessed by the generated kernel instructions.

For information about the `Tree` and `Input` data structures themselves, see **3.1 Data Structures: Tree and Input**. For details on how the `Machine` simulator accesses this memory, see **4.3 Memory Hierarchy**.

## Overview

The `Machine` simulator operates on a flat memory model consisting of an array of 32-bit words [tests/frozen_problem.py:80-83](). To execute the tree traversal algorithm, the simulator needs access to:
- Tree node values
- Input batch indices and values  
- Metadata (tree height, batch size, number of rounds)
- Pointers to locate data within memory

The serialization process converts the object-oriented `Tree` and `Input` structures into this flat representation through the `build_mem_image` function [tests/frozen_problem.py:487-513]().

**Sources:** [tests/frozen_problem.py:80-83](), [tests/frozen_problem.py:487-513]()

## Memory Layout Structure

The flat memory image follows a standardized layout convention with two main components:

1. **Header Section** - Fixed 7-word header containing metadata and pointers [tests/frozen_problem.py:491-508]()
2. **Data Sections** - Variable-length arrays containing the actual data [tests/frozen_problem.py:510-513]()

```mermaid
graph TB
    subgraph "Flat Memory Array (32-bit words)"
        Header["Header<br/>Words 0-6<br/>Metadata + Pointers"]
        TreeVals["Tree Values<br/>forest_values_p...<br/>2^(height+1)-1 words"]
        InpIndices["Input Indices<br/>inp_indices_p...<br/>batch_size words"]
        InpValues["Input Values<br/>inp_values_p...<br/>batch_size words"]
        Extra["Extra Room<br/>extra_room...<br/>Scratch space"]
    end
    
    Header -->|"mem[4] = forest_values_p"| TreeVals
    Header -->|"mem[5] = inp_indices_p"| InpIndices
    Header -->|"mem[6] = inp_values_p"| InpValues
    Header -->|"mem[7] = extra_room"| Extra
```

**Sources:** [tests/frozen_problem.py:487-513]()

## The build_mem_image Function

The serialization is performed by the `build_mem_image` function, which takes a `Tree` and `Input` object and returns a flat list of integers.

**Function Signature:**
`def build_mem_image(t: Tree, inp: Input) -> list[int]` [tests/frozen_problem.py:487]()

### Serialization Process

```mermaid
flowchart LR
    Tree["Tree Object<br/>height: int<br/>values: list[int]"]
    Input["Input Object<br/>indices: list[int]<br/>values: list[int]<br/>rounds: int"]
    
    BuildMem["build_mem_image()<br/>tests/frozen_problem.py:487"]
    
    FlatMem["Flat Memory Image<br/>list[int]<br/>length = header + data + extra"]
    
    Tree --> BuildMem
    Input --> BuildMem
    BuildMem --> FlatMem
    
    subgraph "Serialization Steps"
        Step1["1. Calculate sizes"]
        Step2["2. Allocate array"]
        Step3["3. Compute pointers"]
        Step4["4. Write header"]
        Step5["5. Copy data arrays"]
    end
    
    BuildMem -.-> Step1
    Step1 -.-> Step2
    Step2 -.-> Step3
    Step3 -.-> Step4
    Step4 -.-> Step5
```

**Sources:** [tests/frozen_problem.py:487-513]()

## Header Format

The header occupies the first 7 words (indices 0-6) of the memory array and contains both metadata and pointers to data sections [tests/frozen_problem.py:501-508]().

| Word Index | Field Name | Description | Source |
|------------|------------|-------------|---------|
| `mem[0]` | `inp.rounds` | Number of rounds to execute | `Input` object |
| `mem[1]` | `len(t.values)` | Total number of tree nodes | `Tree` object |
| `mem[2]` | `len(inp.indices)` | Batch size | `Input` object |
| `mem[3]` | `t.height` | Tree height | `Tree` object |
| `mem[4]` | `forest_values_p` | Pointer to tree values array | Calculated |
| `mem[5]` | `inp_indices_p` | Pointer to input indices array | Calculated |
| `mem[6]` | `inp_values_p` | Pointer to input values array | Calculated |
| `mem[7]` | `extra_room` | Pointer to extra scratch space | Calculated |

**Header Constant:** The header size is fixed at 7 words [tests/frozen_problem.py:491]().

**Sources:** [tests/frozen_problem.py:501-508]()

## Pointer Calculation

Pointers are calculated sequentially based on the sizes of preceding sections [tests/frozen_problem.py:491-499]():

```python
header = 7
forest_values_p = header                              # Word 7
inp_indices_p = forest_values_p + len(t.values)      # After tree values
inp_values_p = inp_indices_p + len(inp.values)       # After input indices  
extra_room = inp_values_p + len(inp.values)          # After input values
```

These pointers enable the kernel and reference implementations to locate data within the flat memory array.

**Sources:** [tests/frozen_problem.py:491-499]()

## Data Sections

### Tree Values Section
**Location:** `mem[forest_values_p : inp_indices_p]`
Contains all node values from the binary tree in implicit array representation [tests/frozen_problem.py:510]().

### Input Indices Section
**Location:** `mem[inp_indices_p : inp_values_p]`
Contains the current tree node index for each element in the batch. These values are updated during kernel execution [tests/frozen_problem.py:511]().

### Input Values Section
**Location:** `mem[inp_values_p : extra_room]`
Contains the current hash values for each element in the batch [tests/frozen_problem.py:512]().

### Extra Room Section
**Location:** `mem[extra_room : end]`
Additional scratch space allocated for temporary computations. The size is calculated to provide space for vectorized operations and intermediate results [tests/frozen_problem.py:492]():
`extra_room_size = len(t.values) + len(inp.indices) * 2 + VLEN * 2 + 32`

**Sources:** [tests/frozen_problem.py:510-513](), [tests/frozen_problem.py:492]()

## Memory Access Patterns

### Reference Kernel Access

The `reference_kernel2` function demonstrates how to access the serialized memory [tests/frozen_problem.py:535-548]():

```mermaid
graph LR
    subgraph "reference_kernel2 Memory Access"
        ReadHeader["Read Header<br/>mem[0:7]"]
        ExtractMeta["Extract Metadata<br/>rounds, n_nodes,<br/>batch_size"]
        ExtractPtrs["Extract Pointers<br/>forest_values_p,<br/>inp_indices_p,<br/>inp_values_p"]
        Access["Access Data<br/>mem[ptr + offset]"]
    end
    
    ReadHeader --> ExtractMeta
    ReadHeader --> ExtractPtrs
    ExtractPtrs --> Access
```

**Example Access Pattern:**
```python
# Read header [tests/frozen_problem.py:536-543]
rounds = mem[0]
n_nodes = mem[1]
batch_size = mem[2]
forest_height = mem[3]
forest_values_p = mem[4]
inp_indices_p = mem[5]
inp_values_p = mem[6]

# Access data using pointers [tests/frozen_problem.py:546-548]
idx = mem[inp_indices_p + i]           # Read index for batch element i
val = mem[inp_values_p + i]            # Read value for batch element i  
node_val = mem[forest_values_p + idx]  # Read tree node value at idx
```

**Sources:** [tests/frozen_problem.py:535-548]()

## Memory Size Calculation

The total memory allocation is the sum of the header, data arrays, and extra room [tests/frozen_problem.py:491-495](). For a standard tree of height 10 and batch size 256, this results in approximately 5206 words (20.8 KB).

**Sources:** [tests/frozen_problem.py:491-495]()

## Integration with Machine Simulator

The `Machine` class receives the memory image through its constructor and stores it in `self.mem` [tests/frozen_problem.py:99-110]().

```mermaid
sequenceDiagram
    participant Test as Test Code
    participant Tree as Tree.generate()
    participant Input as Input.generate()
    participant Build as build_mem_image()
    participant Machine as Machine()
    participant Ref as reference_kernel2()
    
    Test->>Tree: Generate tree
    Tree-->>Test: Tree object
    Test->>Input: Generate input
    Input-->>Test: Input object
    Test->>Build: build_mem_image(tree, input)
    Build-->>Test: mem_dump: list[int]
    Test->>Machine: Machine(mem_dump, program, ...)
    Test->>Ref: reference_kernel2(mem_dump.copy())
    Ref-->>Test: expected_mem
    Machine-->>Test: actual_mem
    Test->>Test: Compare actual_mem vs expected_mem
```

**Sources:** [tests/frozen_problem.py:97-110](), [tests/frozen_problem.py:487-513]()

## Key Invariants

1. **Fixed Header Size:** The header always occupies exactly 7 words [tests/frozen_problem.py:491]().
2. **Contiguous Layout:** All sections are contiguous with no gaps or padding [tests/frozen_problem.py:491-499]().
3. **32-bit Words:** All values are stored as 32-bit integers [tests/frozen_problem.py:80]().
4. **Pointer Validity:** All pointers in the header point to valid locations within the allocated array [tests/frozen_problem.py:505-508]().

**Sources:** [tests/frozen_problem.py:487-513](), [tests/frozen_problem.py:80]()

---

# Page: Machine Architecture

# Machine Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This document provides comprehensive documentation of the custom VLIW SIMD simulator architecture implemented in the `Machine` class. This simulator executes instruction sequences generated by the `KernelBuilder` to solve the tree traversal problem. For information about optimizing the kernel code generation, see [Kernel Builder - The Optimization Target](#5). For information about instruction set details and individual operations, see [Instruction Set Reference](#4.2).

## Machine Simulator Overview

The `Machine` class in [problem.py:64-403]() implements a software simulator for a custom parallel architecture that combines VLIW (Very Long Instruction Word) and SIMD (Single Instruction Multiple Data) execution models. The simulator executes programs represented as lists of instruction bundles, operating on a flat memory space and maintaining per-core scratch space.

**Machine Entity Mapping**
```mermaid
graph TB
    Machine["Machine\n(problem.py:64)"]
    Machine --> mem["mem: list[int]\nFlat memory array"]
    Machine --> cores["cores: list[Core]\nCore state array"]
    Machine --> program["program: list[Instruction]\nInstruction sequence"]
    Machine --> debug_info["debug_info: DebugInfo\nScratch variable mapping"]
    
    cores --> Core["Core\n(problem.py:25)"]
    Core --> scratch["scratch: list[int]\n1536 words per core"]
    Core --> pc["pc: int\nProgram counter"]
    Core --> state["state: CoreState\nRUNNING/PAUSED/STOPPED"]
    
    program --> Instruction["Instruction\ndict[Engine, list[tuple]]"]
    Instruction --> alu_slots["'alu': [...]\n12 slots max"]
    Instruction --> valu_slots["'valu': [...]\n6 slots max"]
    Instruction --> load_slots["'load': [...]\n2 slots max"]
    Instruction --> store_slots["'store': [...]\n2 slots max"]
    Instruction --> flow_slots["'flow': [...]\n1 slot max"]
    
    debug_info --> scratch_map["scratch_map\ndict[int, (str, int)]"]
```

**Sources:** [problem.py:64-122](), [problem.py:25-31](), [problem.py:34-42](), [problem.py:14-15]()

## Core Architectural Components

### Machine Class Structure

The `Machine` class manages the execution environment and coordinates instruction execution across all cores. Key attributes include:

| Attribute | Type | Purpose |
|-----------|------|---------|
| `cores` | `list[Core]` | Array of core state objects |
| `mem` | `list[int]` | Main memory (32-bit words) |
| `program` | `list[Instruction]` | Instruction sequence to execute |
| `debug_info` | `DebugInfo` | Scratch variable naming information |
| `cycle` | `int` | Current cycle counter |
| `enable_pause` | `bool` | Whether pause instructions take effect |
| `enable_debug` | `bool` | Whether debug instructions execute |

**Sources:** [problem.py:97-122]()

### Core Class Structure

Each `Core` object ([problem.py:25-31]()) represents an independent execution unit with its own state:

| Attribute | Type | Purpose |
|-----------|------|---------|
| `id` | `int` | Core identifier (0-indexed) |
| `scratch` | `list[int]` | Fast local storage (1536 words) |
| `trace_buf` | `list[int]` | Debug trace buffer |
| `pc` | `int` | Program counter (instruction index) |
| `state` | `CoreState` | Execution state enum |

The `CoreState` enum ([problem.py:18-22]()) defines three states:
- `RUNNING`: Core actively executes instructions
- `PAUSED`: Core halted via pause instruction, can resume
- `STOPPED`: Core completed execution or halted permanently

**Sources:** [problem.py:25-31](), [problem.py:18-22]()

## VLIW Architecture: Engine and Slot Model

The architecture follows a VLIW design where each instruction bundle can contain multiple operations that execute in parallel. Operations are grouped into specialized **engines**, each with a fixed number of **slots** that limit parallel execution capacity.

### Slot Limits Configuration

The `SLOT_LIMITS` constant ([problem.py:48-55]()) defines the parallelism capacity:

```python
SLOT_LIMITS = {
    "alu": 12,      # Scalar arithmetic/logic operations
    "valu": 6,      # Vector arithmetic/logic operations
    "load": 2,      # Memory reads to scratch
    "store": 2,     # Scratch writes to memory
    "flow": 1,      # Control flow operations
    "debug": 64,    # Debug/validation operations
}
```

**Interpretation:** In a single cycle, the machine can execute up to 12 scalar arithmetic operations, 6 vector operations, 2 loads, 2 stores, and 1 control flow operation simultaneously. For details on operation semantics, see [Instruction Set Reference](#4.2).

**Sources:** [problem.py:48-55]()

### Engine Type Mapping

**Engine Execution Logic**
```mermaid
graph LR
    InstrBundle["Instruction Bundle\ndict[Engine, list[tuple]]"]
    
    InstrBundle --> ALU["ALU Engine\nalu()\n12 slots"]
    InstrBundle --> VALU["VALU Engine\nvalu()\n6 slots"]
    InstrBundle --> LOAD["LOAD Engine\nload()\n2 slots"]
    InstrBundle --> STORE["STORE Engine\nstore()\n2 slots"]
    InstrBundle --> FLOW["FLOW Engine\nflow()\n1 slot"]
    
    ALU --> ScratchOps["Operates on\ncore.scratch"]
    VALU --> ScratchOps
    LOAD --> MemToScratch["mem → scratch"]
    STORE --> ScratchToMem["scratch → mem"]
    FLOW --> Control["Control flow\nconditionals\nselect ops"]
```

Each engine is implemented as a method on the `Machine` class:
- `alu()`: [problem.py:219-253]()
- `valu()`: [problem.py:254-267]()
- `load()`: [problem.py:269-286]()
- `store()`: [problem.py:288-298]()
- `flow()`: [problem.py:300-335]()

**Sources:** [problem.py:219-335](), [problem.py:356-362]()

## SIMD Architecture: Vector Operations

The architecture supports SIMD parallelism through vector operations. The vector length is fixed at compile time by the `VLEN` constant ([problem.py:57]()).

```python
VLEN = 8  # Vector operations process 8 elements in parallel
```

Vector operations in the `valu` engine operate on consecutive scratch addresses. For example, a vector add operation `("+", dest, a1, a2)` computes `scratch[dest+i] = scratch[a1+i] + scratch[a2+i]` for `i` in `range(VLEN)`. For more details, see [VLIW SIMD Concepts](#4.1).

**Sources:** [problem.py:57](), [problem.py:254-267]()

## Configuration Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `VLEN` | 8 | Number of elements in vector operations |
| `N_CORES` | 1 | Number of cores (single-core in current version) |
| `SCRATCH_SIZE` | 1536 | Size of per-core scratch space in 32-bit words |
| `BASE_ADDR_TID` | 100000 | Thread ID offset for scratch variable traces |

**Note:** The comment at [problem.py:58-59]() indicates that older versions used multiple cores, but the current version is single-core only.

**Sources:** [problem.py:57-61]()

## Instruction Format

Instructions follow a dictionary-based format where keys are engine names and values are lists of operation tuples:

```python
Instruction = dict[Engine, list[tuple]]
```

Example instruction bundle ([problem.py:85-87]()):
```python
{
    "valu": [("*", 4, 0, 0), ("+", 8, 4, 0)],  # Two vector operations
    "load": [("load", 16, 17)]                   # One load operation
}
```

### Operand Addressing Convention

As documented in [problem.py:89-91]():
- **All numbers in instructions are scratch addresses** except for specific operations like `const`, `jump`, and `add_imm` which take immediate values or instruction pointers.
- **First operand is destination** for most operations except for `store` and some `flow` operations.

For details on memory addressing, see [Memory Hierarchy](#4.3).

**Sources:** [problem.py:14-15](), [problem.py:85-91]()

## Execution Flow

### Main Execution Loop

The `run()` method ([problem.py:197-217]()) implements the fetch-decode-execute cycle. Debug-only instructions do not increment the cycle counter ([problem.py:214-217]()). For a detailed breakdown of timing, see [Execution Model and Cycle Semantics](#4.4).

**Sources:** [problem.py:197-217]()

### Instruction Step Execution

The `step()` method ([problem.py:352-397]()) executes a single instruction bundle using a **two-phase commit model**:

1. **Read Phase** ([problem.py:363-387]()): All engine methods read from `core.scratch` and `self.mem` directly, seeing the state at the start of the cycle.
2. **Write Phase** ([problem.py:388-391]()): All writes go into `scratch_write` and `mem_write` dictionaries.
3. **Commit Phase** ([problem.py:388-391]()): After all operations complete, writes are applied atomically.

This ensures deterministic parallel execution even when multiple slots write to the same location (last write wins). For details, see [Execution Model and Cycle Semantics](#4.4).

**Sources:** [problem.py:352-397]()

## Machine Initialization

The `Machine.__init__()` method ([problem.py:97-122]()) initializes the execution environment. If `trace=True`, the simulator calls `setup_trace()` ([problem.py:151-195]()) to initialize Chrome Trace Event Format output to `trace.json`. For trace analysis details, see [Performance Analysis and Debugging](#7).

**Sources:** [problem.py:97-122]()

## Data Word Format

All data in memory and scratch space consists of **32-bit unsigned words**. Arithmetic operations automatically modulo by 2³² to maintain this constraint ([problem.py:251]()).

**Sources:** [problem.py:83](), [problem.py:251]()

## Frozen vs Development Simulators

Two implementations of the simulator exist:
- **Development version:** [problem.py:64-403]()
- **Frozen version:** [tests/frozen_problem.py:64-403]()

The frozen version is used for testing to ensure the machine behavior remains static. For details on when each is used, see [Frozen vs Development Simulators](#4.5).

**Sources:** [problem.py:1-6](), [tests/frozen_problem.py:1-6]()

## Related Documentation

- [VLIW SIMD Concepts](#4.1)
- [Instruction Set Reference](#4.2)
- [Memory Hierarchy](#4.3)
- [Execution Model and Cycle Semantics](#4.4)
- [Frozen vs Development Simulators](#4.5)

---

# Page: VLIW SIMD Concepts

# VLIW SIMD Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



## Purpose and Scope

This page explains the Very Large Instruction Word (VLIW) and Single Instruction Multiple Data (SIMD) architectural concepts that form the foundation of the custom machine simulator in this repository. It covers how these paradigms combine to enable instruction-level and data-level parallelism, and how they are implemented in the `Machine` class.

For details on specific instruction operations and their semantics, see [Instruction Set Reference](#4.2). For information on the execution model and cycle semantics, see [Execution Model and Cycle Semantics](#4.4). For the memory system, see [Memory Hierarchy](#4.3).

## VLIW: Very Large Instruction Word

### Concept

VLIW is a computer architecture paradigm where the compiler (rather than the hardware) explicitly schedules multiple operations to execute in parallel within a single instruction. Each instruction is a "bundle" containing operations for multiple execution units called **engines** [tests/frozen_problem.py:14-15]().

In this architecture, the optimizer (you) acts as the compiler, generating instruction bundles that pack as many operations as possible into each cycle while respecting hardware constraints [tests/frozen_problem.py:68-71]().

**VLIW Instruction Bundle Structure**

```mermaid
graph TB
    Instr["Instruction Bundle<br/>(dict[Engine, list[tuple]])"]
    
    Instr --> ALU["ALU Engine<br/>Scalar arithmetic<br/>up to 12 slots"]
    Instr --> VALU["VALU Engine<br/>Vector arithmetic<br/>up to 6 slots"]
    Instr --> LOAD["LOAD Engine<br/>Memory to scratch<br/>up to 2 slots"]
    Instr --> STORE["STORE Engine<br/>Scratch to memory<br/>up to 2 slots"]
    Instr --> FLOW["FLOW Engine<br/>Control flow<br/>up to 1 slot"]
    Instr --> DEBUG["DEBUG Engine<br/>Validation ops<br/>up to 64 slots"]
    
    ALU --> ALU_Ex["Execute all ALU slots<br/>in parallel"]
    VALU --> VALU_Ex["Execute all VALU slots<br/>in parallel"]
    LOAD --> LOAD_Ex["Execute all LOAD slots<br/>in parallel"]
    STORE --> STORE_Ex["Execute all STORE slots<br/>in parallel"]
    FLOW --> FLOW_Ex["Execute FLOW slot"]
    DEBUG --> DEBUG_Ex["Execute DEBUG slots"]
    
    ALU_Ex --> Commit["Commit Phase:<br/>Apply all writes"]
    VALU_Ex --> Commit
    LOAD_Ex --> Commit
    STORE_Ex --> Commit
    FLOW_Ex --> Commit
    DEBUG_Ex --> Commit
```

Sources: [tests/frozen_problem.py:14-15](), [tests/frozen_problem.py:48-55](), [tests/frozen_problem.py:64-95]()

### Engine Architecture and Slot Limits

The machine contains six engine types, each with a maximum number of **slots** (operations) it can execute per cycle [tests/frozen_problem.py:48-55]():

| Engine | Slot Limit | Purpose | Example Operations |
|--------|-----------|---------|-------------------|
| `alu` | 12 | Scalar arithmetic and logic | `+`, `-`, `*`, `^`, `<<`, `%`, `<`, `==` |
| `valu` | 6 | Vector arithmetic and logic | `vbroadcast`, `multiply_add`, vector ops |
| `load` | 2 | Memory → scratch transfers | `load`, `vload`, `const`, `load_offset` |
| `store` | 2 | Scratch → memory transfers | `store`, `vstore` |
| `flow` | 1 | Control flow and conditionals | `select`, `cond_jump`, `halt`, `pause` |
| `debug` | 64 | Correctness validation | `compare`, `vcompare` |

These limits are defined in the `SLOT_LIMITS` constant and enforced by the simulator during execution [tests/frozen_problem.py:48-55](), [tests/frozen_problem.py:383]().

### Instruction Format

An instruction is represented as a Python dictionary mapping engine names to lists of operation tuples [tests/frozen_problem.py:14-15]():

```python
Instruction = dict[Engine, list[tuple]]

# Example instruction with 3 engines active:
{
    "valu": [("*", 4, 0, 0), ("+", 8, 4, 0)],     # 2 vector operations
    "load": [("const", 16, 42)],                    # 1 load operation
    "flow": [("add_imm", 20, 16, 5)]               # 1 flow operation
}
```

All operations in this bundle execute **in parallel** during a single cycle. The first element of each tuple is the operation name; subsequent elements are operand addresses (except for immediate values like constants and jump targets) [tests/frozen_problem.py:86-94]().

## SIMD: Single Instruction Multiple Data

### Concept

SIMD allows a single instruction to operate on multiple data elements simultaneously. This architecture uses **vector operations** that process `VLEN = 8` elements in parallel using a single instruction slot [tests/frozen_problem.py:57](), [tests/frozen_problem.py:75-78]().

**SIMD Vector Operations**

```mermaid
graph LR
    subgraph "Scalar Operation (ALU)"
        S_In1["scratch[a]<br/>single value"]
        S_In2["scratch[b]<br/>single value"]
        S_Op["+ operation"]
        S_Out["scratch[dest]<br/>single value"]
        
        S_In1 --> S_Op
        S_In2 --> S_Op
        S_Op --> S_Out
    end
    
    subgraph "Vector Operation (VALU)"
        V_In1["scratch[a:a+8]<br/>8 values"]
        V_In2["scratch[b:b+8]<br/>8 values"]
        V_Op["+ operation<br/>(8 parallel lanes)"]
        V_Out["scratch[dest:dest+8]<br/>8 values"]
        
        V_In1 --> V_Op
        V_In2 --> V_Op
        V_Op --> V_Out
    end
```

Sources: [tests/frozen_problem.py:57](), [tests/frozen_problem.py:75-78](), [tests/frozen_problem.py:254-267]()

### Vector Length

The constant `VLEN = 8` defines the number of elements processed by vector operations [tests/frozen_problem.py:57](). All vector operations work on exactly 8 contiguous elements starting at the specified scratch address.

### Vector Operations in VALU Engine

The `valu` engine implements vector operations through the `Machine.valu()` method [tests/frozen_problem.py:254-267]():

**Core Vector Operations:**

1. **`vbroadcast`** - Broadcast a scalar to all 8 vector lanes:
   ```python
   ("vbroadcast", dest, src)
   # scratch[dest:dest+8] = [scratch[src]] * 8
   ```

2. **`multiply_add`** - Fused multiply-add on vectors:
   ```python
   ("multiply_add", dest, a, b, c)
   # scratch[dest+i] = (scratch[a+i] * scratch[b+i]) + scratch[c+i] for i in 0..7
   ```

3. **Element-wise ALU operations** - Apply any ALU operation to vectors:
   ```python
   ("+", dest, a1, a2)
   # scratch[dest+i] = scratch[a1+i] + scratch[a2+i] for i in 0..7
   ```

Sources: [tests/frozen_problem.py:254-267]()

### Vector Memory Operations

Vector loads and stores transfer 8 contiguous elements:

- **`vload`**: Load 8 words from memory to scratch vector [tests/frozen_problem.py:279-282]()
- **`vstore`**: Store 8 words from scratch vector to memory [tests/frozen_problem.py:293-296]()

**Important**: Vector memory operations can only access **contiguous** elements. Non-contiguous access patterns require multiple scalar loads/stores or data reorganization.

## Combined VLIW-SIMD Architecture

### Parallelism at Two Levels

This architecture exploits parallelism at two distinct levels simultaneously:

1. **Instruction-Level Parallelism (VLIW)**: Multiple engines execute different operations in parallel.
2. **Data-Level Parallelism (SIMD)**: Each vector operation processes 8 elements in parallel.

**Parallel Execution Within a Cycle**

```mermaid
graph TB
    subgraph Cycle["Single Cycle"]
        direction TB
        
        subgraph Read["Read Phase: All inputs read simultaneously"]
            R1["ALU slots read<br/>scratch addresses"]
            R2["VALU slots read<br/>scratch vectors"]
            R3["LOAD slots read<br/>memory addresses"]
            R4["STORE slots read<br/>scratch values"]
            R5["FLOW slots read<br/>conditions"]
        end
        
        subgraph Compute["Compute Phase: All engines execute in parallel"]
            C1["12 ALU operations<br/>(up to 12 scalar ops)"]
            C2["6 VALU operations<br/>(up to 6 × 8 = 48 element ops)"]
            C3["2 LOAD operations"]
            C4["2 STORE operations"]
            C5["1 FLOW operation"]
        end
        
        subgraph Write["Write Phase: All writes committed atomically"]
            W1["scratch_write buffer"]
            W2["mem_write buffer"]
            W3["Apply to scratch space"]
            W4["Apply to main memory"]
        end
        
        Read --> Compute
        Compute --> Write
    end
```

Sources: [tests/frozen_problem.py:352-397]()

### Maximum Theoretical Throughput

In a single cycle, the architecture can theoretically execute [tests/frozen_problem.py:48-55](), [tests/frozen_problem.py:57]():

| Resource | Operations per Cycle | Elements per Cycle (with SIMD) |
|----------|---------------------|-------------------------------|
| ALU operations | 12 scalar | 12 |
| VALU operations | 6 vector | 6 × 8 = 48 |
| Memory loads | 2 (scalar or vector) | 2 to 16 |
| Memory stores | 2 (scalar or vector) | 2 to 16 |
| Control flow | 1 | 1 |
| **Total** | **23 slots** | **Up to 77+ elements** |

### Why This Combination Is Powerful

**VLIW advantages:**
- Exposes all parallelism opportunities to the optimizer.
- No hardware scheduling overhead; the compiler (optimizer) handles hazards.
- Deterministic, predictable performance.

**SIMD advantages:**
- Amortizes instruction fetch/decode overhead across 8 elements.
- Efficient for regular, predictable data access patterns.

**Combined benefits:**
- Can exploit both task parallelism (different operations) and data parallelism (same operation, multiple data).
- Particularly effective for the tree traversal problem, which has both batch parallelism (SIMD) and independent hashing operations (VLIW).

Sources: [tests/frozen_problem.py:64-95]()

## Code Implementation: Machine.step()

The VLIW-SIMD execution is implemented in the `Machine.step()` method [tests/frozen_problem.py:352-397]():

**Execution Flow**

```mermaid
flowchart TD
    Start["step(instr, core)"] --> Init["Initialize write buffers:<br/>scratch_write = {}<br/>mem_write = {}"]
    
    Init --> Loop["For each engine in instruction"]
    
    Loop --> Skip{"Is engine<br/>'debug'?"}
    Skip -->|Yes| Debug["Execute debug validation<br/>(if enabled)"]
    Skip -->|No| Check["Check len(slots) <= SLOT_LIMITS[engine]"]
    
    Check --> SlotLoop["For each slot in engine"]
    
    SlotLoop --> Trace{"Tracing<br/>enabled?"}
    Trace -->|Yes| TraceWrite["Write trace event"]
    Trace -->|No| Execute
    TraceWrite --> Execute["Execute slot:<br/>ENGINE_FNS[engine](core, *slot)"]
    
    Execute --> Buffer["Writes go to<br/>scratch_write / mem_write<br/>(not directly to state)"]
    
    Buffer --> More{"More slots?"}
    More -->|Yes| SlotLoop
    More -->|No| MoreEngines{"More engines?"}
    
    Debug --> MoreEngines
    MoreEngines -->|Yes| Loop
    
    MoreEngines -->|No| Commit["Commit Phase:<br/>Apply all writes atomically"]
    
    Commit --> Scratch["core.scratch[addr] = val<br/>for all in scratch_write"]
    Scratch --> Mem["mem[addr] = val<br/>for all in mem_write"]
    
    Mem --> TracePost{"Tracing?"}
    TracePost -->|Yes| TracePostWrite["trace_post_step()"]
    TracePost -->|No| Cleanup
    TracePostWrite --> Cleanup["Delete write buffers"]
    
    Cleanup --> End["Return"]
```

Sources: [tests/frozen_problem.py:352-397]()

**Key Implementation Details:**

1. **Two-Phase Commit** [tests/frozen_problem.py:363-391](): All reads happen before any writes are visible.
   - Reads use current `core.scratch` and `self.mem` state.
   - Writes buffer into `scratch_write` and `mem_write` dictionaries.
   - Buffered writes are applied atomically after all slots execute.

2. **Slot Limit Enforcement** [tests/frozen_problem.py:383](): Asserts that each engine respects its defined limit in `SLOT_LIMITS`.

3. **Parallel Semantics**: Although Python executes slots sequentially, the two-phase commit ensures **as-if parallel** semantics where all slots in a cycle see the same input state.

## Performance Characteristics

### Cycle Counting

The simulator increments the cycle counter only for instructions containing non-debug operations [tests/frozen_problem.py:214-217]():

```python
if any(name != "debug" for name in instr.keys()):
    has_non_debug = True
if has_non_debug:
    self.cycle += 1
```

This means instructions with only `debug` slots are "free" and don't count toward performance metrics.

### Optimization Opportunities

The VLIW-SIMD architecture creates several optimization opportunities:

1. **Instruction Packing**: Fill multiple slots per engine to maximize work per cycle.
2. **Vectorization**: Use SIMD operations to process 8 elements at once.
3. **Load-Store Elimination**: Keep frequently accessed data in scratch space.
4. **Instruction Scheduling**: Reorder operations to avoid dependencies and maximize slot utilization.

Sources: [tests/frozen_problem.py:64-95](), [tests/frozen_problem.py:352-397]()

---

# Page: Instruction Set Reference

# Instruction Set Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page provides a complete reference for all operations available in the custom VLIW SIMD machine architecture. Each instruction bundle can contain multiple operations across different engines, executed in parallel within a single cycle subject to slot limits.

For information about the execution model and cycle semantics, see [Execution Model and Cycle Semantics](#4.4). For details on memory organization and addressing, see [Memory Hierarchy](#4.3). For general VLIW SIMD architectural concepts, see [VLIW SIMD Concepts](#4.1).

## Instruction Format

An instruction is a Python dictionary mapping engine names to lists of operation tuples:

```python
Instruction = dict[Engine, list[tuple]]
Engine = Literal["alu", "load", "store", "flow", "valu", "debug"]
```

Example instruction bundle:
```python
{
    "valu": [("*", 4, 0, 0), ("+", 8, 4, 0)],
    "load": [("load", 16, 17)],
    "alu": [("+", 20, 16, 8)]
}
```

**Important addressing convention:** In general, every number in an instruction is a scratch space address, except for:
- `const` operation: the value is an immediate constant [tests/frozen_problem.py:274-274]()
- `jump` operation: the address is a program counter value [tests/frozen_problem.py:311-311]()
- `store` operations: the first operand is the memory address source [tests/frozen_problem.py:291-291]()
- Immediate offsets in certain operations (e.g., `add_imm`, `load_offset`) [tests/frozen_problem.py:272-272](), [tests/frozen_problem.py:307-307]()

Except for `store` and some `flow` operations, the **first operand after the operation name is the destination address**.

Sources: [tests/frozen_problem.py:14-16](), [tests/frozen_problem.py:86-94]()

## Instruction Structure and Execution Flow

```mermaid
graph TB
    subgraph "Instruction Bundle Format"
        Instr["Instruction<br/>(dict)"]
        Instr --> EngineALU["'alu': list[tuple]"]
        Instr --> EngineVALU["'valu': list[tuple]"]
        Instr --> EngineLOAD["'load': list[tuple]"]
        Instr --> EngineSTORE["'store': list[tuple]"]
        Instr --> EngineFLOW["'flow': list[tuple]"]
        Instr --> EngineDEBUG["'debug': list[tuple]"]
    end
    
    subgraph "Engine Methods"
        EngineALU --> AluMethod["Machine.alu()"]
        EngineVALU --> ValuMethod["Machine.valu()"]
        EngineLOAD --> LoadMethod["Machine.load()"]
        EngineSTORE --> StoreMethod["Machine.store()"]
        EngineFLOW --> FlowMethod["Machine.flow()"]
        EngineDEBUG --> DebugLogic["Debug validation<br/>in step()"]
    end
    
    subgraph "Execution in Machine.step()"
        StepMethod["Machine.step(instr, core)"]
        StepMethod --> ReadPhase["Read phase:<br/>All slots read<br/>core.scratch values"]
        ReadPhase --> WriteBuf["Write buffers:<br/>self.scratch_write<br/>self.mem_write"]
        WriteBuf --> CommitPhase["Commit phase:<br/>Apply all writes<br/>atomically"]
    end
    
    AluMethod --> WriteBuf
    ValuMethod --> WriteBuf
    LoadMethod --> WriteBuf
    StoreMethod --> WriteBuf
    FlowMethod --> WriteBuf
```

**Diagram: Instruction Bundle Structure and Execution Path**

This diagram shows how an instruction dictionary maps to engine execution methods, and the two-phase execution model within `Machine.step()`.

Sources: [tests/frozen_problem.py:352-397](), [tests/frozen_problem.py:356-362]()

## Engine Slot Limits

Each engine can execute a limited number of operations per cycle as defined in `SLOT_LIMITS`:

| Engine | Slot Limit | Purpose |
|--------|-----------|---------|
| `alu` | 12 | Scalar arithmetic and logic operations |
| `valu` | 6 | Vector (SIMD) operations on VLEN=8 elements |
| `load` | 2 | Memory to scratch transfers, constants |
| `store` | 2 | Scratch to memory transfers |
| `flow` | 1 | Control flow, conditionals, core management |
| `debug` | 64 | Validation operations (not counted in cycles) |

Sources: [tests/frozen_problem.py:48-55](), [tests/frozen_problem.py:57]()

## ALU Engine Operations

The ALU engine performs scalar arithmetic and logical operations on scratch space values. All operations read operands and write one result. All results are computed modulo 2³².

### Operation Format

```python
("op", dest, a1, a2)
```

- `op`: Operation name (string)
- `dest`: Destination scratch address (writes result here)
- `a1`: First operand scratch address
- `a2`: Second operand scratch address

### ALU Operation Reference

| Operation | Semantics | Python Equivalent |
|-----------|-----------|-------------------|
| `"+"` | Addition | `(a1 + a2) % 2**32` |
| `"-"` | Subtraction | `(a1 - a2) % 2**32` |
| `"*"` | Multiplication | `(a1 * a2) % 2**32` |
| `"//"` | Integer division | `a1 // a2` |
| `"cdiv"` | Ceiling division | `(a1 + a2 - 1) // a2` |
| `"^"` | Bitwise XOR | `a1 ^ a2` |
| `"&"` | Bitwise AND | `a1 & a2` |
| `"\|"` | Bitwise OR | `a1 \| a2` |
| `"<<"` | Left shift | `(a1 << a2) % 2**32` |
| `">>"` | Right shift | `a1 >> a2` |
| `"%"` | Modulo | `a1 % a2` |
| `"<"` | Less than | `1` if `a1 < a2` else `0` |
| `"=="` | Equality | `1` if `a1 == a2` else `0` |

Sources: [tests/frozen_problem.py:219-252]()

## VALU Engine Operations

The VALU (Vector ALU) engine performs SIMD operations on vectors of `VLEN=8` consecutive scratch addresses.

### Operation Formats

**Standard vectorized ALU operations:**
```python
("op", dest, a1, a2)
```
Applies the ALU operation `op` to each element: for `i` in `range(VLEN)`, `scratch[dest+i] = op(scratch[a1+i], scratch[a2+i])` [tests/frozen_problem.py:263-267]().

**Vector broadcast:**
```python
("vbroadcast", dest, src)
```
Copies scalar `scratch[src]` to all 8 elements of vector starting at `dest` [tests/frozen_problem.py:255-257]().

**Fused multiply-add:**
```python
("multiply_add", dest, a, b, c)
```
Computes `scratch[dest+i] = (scratch[a+i] * scratch[b+i] + scratch[c+i]) % 2**32` for each element [tests/frozen_problem.py:258-262]().

Sources: [tests/frozen_problem.py:254-267](), [tests/frozen_problem.py:57]()

## LOAD Engine Operations

The LOAD engine transfers data from main memory to scratch space and loads immediate constants.

### Operation Formats and Reference

| Operation | Format | Semantics |
|-----------|--------|-----------|
| `"load"` | `(op, dest, addr)` | Load single word: `scratch[dest] = mem[scratch[addr]]` |
| `"load_offset"` | `(op, dest, addr, offset)` | Load with offset: `scratch[dest+offset] = mem[scratch[addr+offset]]` |
| `"vload"` | `(op, dest, addr)` | Vector load: `scratch[dest:dest+8] = mem[scratch[addr]:scratch[addr]+8]` |
| `"const"` | `(op, dest, val)` | Load constant: `scratch[dest] = val % 2**32` |

Sources: [tests/frozen_problem.py:269-286]()

## STORE Engine Operations

The STORE engine transfers data from scratch space to main memory.

### Operation Formats and Reference

| Operation | Format | Semantics |
|-----------|--------|-----------|
| `"store"` | `(op, addr, src)` | Store single word: `mem[scratch[addr]] = scratch[src]` |
| `"vstore"` | `(op, addr, src)` | Vector store: `mem[scratch[addr]:scratch[addr]+8] = scratch[src:src+8]` |

**Key point:** The **first operand is the source of the address**, not the destination [tests/frozen_problem.py:291-291](), [tests/frozen_problem.py:295-295]().

Sources: [tests/frozen_problem.py:288-298]()

## FLOW Engine Operations

The FLOW engine controls program flow and provides selection operations. Only one flow operation can execute per cycle [tests/frozen_problem.py:53]().

### Selection and Arithmetic

| Operation | Format | Semantics |
|-----------|--------|-----------|
| `"select"` | `(op, dest, cond, a, b)` | `scratch[dest] = scratch[a]` if `scratch[cond] != 0` else `scratch[b]` |
| `"vselect"` | `(op, dest, cond, a, b)` | Vectorized element-wise select |
| `"add_imm"` | `(op, dest, a, imm)` | `scratch[dest] = (scratch[a] + imm) % 2**32` |

### Control Flow

| Operation | Format | Semantics |
|-----------|--------|-----------|
| `"jump"` | `(op, addr)` | `core.pc = addr` (absolute PC) |
| `"jump_indirect"` | `(op, addr)` | `core.pc = scratch[addr]` |
| `"cond_jump"` | `(op, cond, addr)` | `core.pc = addr` if `scratch[cond] != 0` |
| `"cond_jump_rel"` | `(op, cond, offset)` | `core.pc += offset` if `scratch[cond] != 0` |

### Core and Debug

| Operation | Format | Semantics |
|-----------|--------|-----------|
| `"halt"` | `(op,)` | `core.state = CoreState.STOPPED` |
| `"pause"` | `(op,)` | `core.state = CoreState.PAUSED` |
| `"coreid"` | `(op, dest)` | `scratch[dest] = core.id` |
| `"trace_write"` | `(op, val)` | Append `scratch[val]` to `core.trace_buf` |

Sources: [tests/frozen_problem.py:300-335]()

## DEBUG Engine Operations

The DEBUG engine provides validation operations used during testing. These do not consume cycles and are only executed when `enable_debug=True` [tests/frozen_problem.py:366-381]().

| Operation | Format | Semantics |
|-----------|--------|-----------|
| `"compare"` | `(op, loc, key)` | Assert `scratch[loc] == value_trace[key]` |
| `"vcompare"` | `(op, loc, keys)` | Assert vector matches list of trace keys |

Sources: [tests/frozen_problem.py:366-381](), [tests/frozen_problem.py:54]()

## Engine Method Dispatch

```mermaid
graph LR
    subgraph "Machine.step() Execution"
        Step["Machine.step(instr, core)"]
        Step --> DispatchTable["ENGINE_FNS dict"]
    end
    
    subgraph "ENGINE_FNS Dispatch"
        DispatchTable --> MapALU["'alu' → Machine.alu"]
        DispatchTable --> MapVALU["'valu' → Machine.valu"]
        DispatchTable --> MapLOAD["'load' → Machine.load"]
        DispatchTable --> MapSTORE["'store' → Machine.store"]
        DispatchTable --> MapFLOW["'flow' → Machine.flow"]
    end
    
    subgraph "Implementation"
        MapALU --> AluImpl["alu(core, op, dest, a1, a2)"]
        MapVALU --> ValuImpl["valu(core, *slot)"]
        MapLOAD --> LoadImpl["load(core, *slot)"]
        MapSTORE --> StoreImpl["store(core, *slot)"]
        MapFLOW --> FlowImpl["flow(core, *slot)"]
    end
```

**Diagram: Machine Engine Dispatch Mechanism**

This diagram illustrates how `Machine.step()` uses the `ENGINE_FNS` dictionary to route instruction slots to their respective implementation methods.

Sources: [tests/frozen_problem.py:352-397](), [tests/frozen_problem.py:217-217]()

---

# Page: Memory Hierarchy

# Memory Hierarchy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



## Purpose and Scope

This document describes the two-tier memory hierarchy implemented by the custom VLIW SIMD machine simulator. It covers the organization of main memory and scratch space, memory access operations, and the addressing model. For information about the instruction set operations that manipulate memory, see [Instruction Set Reference](#4.2). For details about the two-phase execution model that governs memory access, see [Execution Model and Cycle Semantics](#4.4).

---

## Two-Tier Memory Architecture

The machine implements a load-store architecture with two distinct memory tiers. ALU and VALU engines cannot directly access main memory; they operate exclusively on scratch space. Memory transfers occur through dedicated LOAD and STORE engines.

```mermaid
graph TB
    subgraph MainMemory["Main Memory (Machine.mem)"]
        MemArray["Flat word array<br/>32-bit integers<br/>Arbitrary size"]
        Header["Header (7 words)<br/>Metadata & pointers"]
        TreeData["Tree values<br/>forest_values_p"]
        InputIndices["Input indices<br/>inp_indices_p"]
        InputValues["Input values<br/>inp_values_p"]
        Extra["Extra room<br/>Working space"]
    end
    
    subgraph ScratchSpace["Scratch Space (Core.scratch)"]
        ScratchArray["Per-core array<br/>SCRATCH_SIZE=1536 words<br/>32-bit integers"]
        ScratchPurpose["Serves as:<br/>- Registers<br/>- Constants<br/>- Manual cache"]
    end
    
    subgraph Engines["Execution Engines"]
        LoadEngine["LOAD Engine<br/>2 slots/cycle"]
        StoreEngine["STORE Engine<br/>2 slots/cycle"]
        ALUEngine["ALU Engine<br/>12 slots/cycle"]
        VALUEngine["VALU Engine<br/>6 slots/cycle"]
    end
    
    LoadEngine -->|"load, vload<br/>const"| ScratchArray
    ScratchArray -->|"addresses"| LoadEngine
    MemArray -->|"read data"| LoadEngine
    
    StoreEngine -->|"store, vstore"| MemArray
    ScratchArray -->|"addresses & data"| StoreEngine
    
    ALUEngine -->|"operates on"| ScratchArray
    VALUEngine -->|"operates on"| ScratchArray
```

**Sources:** [tests/frozen_problem.py:64-95](), [tests/frozen_problem.py:107-110](), [tests/frozen_problem.py:59-61]()

---

## Main Memory

### Structure and Organization

Main memory (`self.mem`) is a flat array of 32-bit words. All values are stored modulo 2³², effectively treating the memory as unsigned 32-bit integers. The memory is initialized from a memory dump created by the `build_mem_image` function.

| Property | Value | Location |
|----------|-------|----------|
| Data type | `list[int]` | [tests/frozen_problem.py:110]() |
| Word size | 32 bits | [tests/frozen_problem.py:80-83]() |
| Initialization | `copy(mem_dump)` | [tests/frozen_problem.py:110]() |
| Addressing | Zero-indexed integers | - |

**Sources:** [tests/frozen_problem.py:110](), [tests/frozen_problem.py:80-83]()

### Memory Layout Convention

The `build_mem_image` function (defined in `perf_takehome.py`) establishes a standard memory layout convention with a 7-word header containing metadata and pointers to data regions:

```mermaid
graph LR
    subgraph Header["Header (words 0-7)"]
        W0["0: rounds"]
        W1["1: n_nodes"]
        W2["2: batch_size"]
        W3["3: forest_height"]
        W4["4: forest_values_p"]
        W5["5: inp_indices_p"]
        W6["6: inp_values_p"]
        W7["7: extra_room_p"]
    end
    
    subgraph Data["Data Arrays"]
        ForestVals["forest_values_p<br/>Tree node values"]
        InpIndices["inp_indices_p<br/>Current indices"]
        InpValues["inp_values_p<br/>Current values"]
        ExtraRoom["extra_room_p<br/>Working space"]
    end
    
    W4 -.->|"pointer"| ForestVals
    W5 -.->|"pointer"| InpIndices
    W6 -.->|"pointer"| InpValues
    W7 -.->|"pointer"| ExtraRoom
```

**Sources:** [perf_takehome.py:487-513]()

The memory layout implementation:

```python
mem[0] = inp.rounds           # Number of traversal rounds
mem[1] = len(t.values)        # Total tree nodes
mem[2] = len(inp.indices)     # Batch size
mem[3] = t.height             # Tree height
mem[4] = forest_values_p      # Pointer to tree values array
mem[5] = inp_indices_p        # Pointer to indices array
mem[6] = inp_values_p         # Pointer to values array
mem[7] = extra_room           # Pointer to working space
```

**Sources:** [perf_takehome.py:501-508]()

### Memory Access Patterns

Main memory supports both scalar and vector access through the LOAD and STORE engines:

| Access Type | Operation | Description |
|-------------|-----------|-------------|
| Scalar load | `load` | Load single word from memory to scratch |
| Vector load | `vload` | Load VLEN=8 contiguous words |
| Scalar store | `store` | Store single word from scratch to memory |
| Vector store | `vstore` | Store VLEN=8 contiguous words |

**Sources:** [tests/frozen_problem.py:269-298]()

---

## Scratch Space

### Size and Organization

Each core maintains its own isolated scratch space. The scratch space is a flat array of 1536 words, indexed from 0 to 1535.

```mermaid
graph TB
    subgraph CoreEntity["Core (tests/frozen_problem.py)"]
        Scratch0["Core.scratch<br/>[0] * SCRATCH_SIZE<br/>1536 words"]
    end
    
    subgraph Properties["Scratch Space Properties"]
        Size["Size: SCRATCH_SIZE = 1536"]
        Type["Type: list[int]"]
        Init["Initialization: Core(scratch=[0] * scratch_size)"]
        Access["Access: core.scratch[addr]"]
    end
    
    CoreEntity --> Properties
```

**Sources:** [tests/frozen_problem.py:60](), [tests/frozen_problem.py:108]()

### Multiple Roles

The scratch space serves three conceptual purposes, though they are not physically separated:

1. **Registers**: Fast temporary storage for computation results.
2. **Constant memory**: Storage for program constants loaded via `const` operation.
3. **Manual cache**: User-managed cache for frequently accessed main memory data.

The `KernelBuilder` (in `perf_takehome.py`) allocates scratch space addresses and tracks their usage through the `alloc_scratch` helper method. The `DebugInfo.scratch_map` provides symbolic names for scratch regions, mapping addresses to `(name, length)` tuples.

**Sources:** [tests/frozen_problem.py:80-83](), [tests/frozen_problem.py:40-42](), [tests/frozen_problem.py:140-144]()

### Per-Core Isolation

With `N_CORES = 1`, the current implementation uses a single core. However, the architecture supports multiple cores, each with its own isolated scratch space. The `Core` dataclass encapsulates this:

```python
@dataclass
class Core:
    id: int
    scratch: list[int]
    trace_buf: list[int]
    pc: int = 0
    state: CoreState = CoreState.RUNNING
```

**Sources:** [tests/frozen_problem.py:24-31](), [tests/frozen_problem.py:59]()

---

## Memory Transfer Operations

### LOAD Engine Operations

The LOAD engine provides operations to transfer data from main memory to scratch space. It can execute up to 2 slots per cycle.

```mermaid
graph LR
    MainMem["Main Memory<br/>Machine.mem"]
    ScratchSpace["Scratch Space<br/>Core.scratch"]
    
    MainMem -->|"load"| ScratchSpace
    MainMem -->|"vload (VLEN=8)"| ScratchSpace
    ScratchSpace -->|"load_offset"| ScratchSpace
    Immediate["Immediate Value"] -->|"const"| ScratchSpace
```

| Operation | Syntax | Description |
|-----------|--------|-------------|
| `load` | `("load", dest, addr)` | Load `mem[scratch[addr]]` to `scratch[dest]` |
| `load_offset` | `("load_offset", dest, addr, offset)` | Load `mem[scratch[addr+offset]]` to `scratch[dest+offset]` |
| `vload` | `("vload", dest, addr)` | Load 8 contiguous words from `mem[scratch[addr]:scratch[addr]+8]` |
| `const` | `("const", dest, val)` | Load immediate value `val` to `scratch[dest]` |

**Sources:** [tests/frozen_problem.py:269-286](), [tests/frozen_problem.py:48-55]()

**Implementation Details:**

The `load` operation uses indirect addressing - the address stored in scratch space is used to access main memory:

```python
case ("load", dest, addr):
    self.scratch_write[dest] = self.mem[core.scratch[addr]]
```

The `vload` operation loads VLEN=8 contiguous words in a single slot:

```python
case ("vload", dest, addr):
    addr = core.scratch[addr]
    for vi in range(VLEN):
        self.scratch_write[dest + vi] = self.mem[addr + vi]
```

**Sources:** [tests/frozen_problem.py:271-282]()

### STORE Engine Operations

The STORE engine transfers data from scratch space to main memory. It can also execute up to 2 slots per cycle.

```mermaid
graph LR
    ScratchSpace["Scratch Space<br/>Core.scratch"]
    MainMem["Main Memory<br/>Machine.mem"]
    
    ScratchSpace -->|"store"| MainMem
    ScratchSpace -->|"vstore (VLEN=8)"| MainMem
```

| Operation | Syntax | Description |
|-----------|--------|-------------|
| `store` | `("store", addr, src)` | Store `scratch[src]` to `mem[scratch[addr]]` |
| `vstore` | `("vstore", addr, src)` | Store 8 contiguous words to `mem[scratch[addr]:scratch[addr]+8]` |

**Implementation:**

```python
case ("store", addr, src):
    addr = core.scratch[addr]
    self.mem_write[addr] = core.scratch[src]

case ("vstore", addr, src):
    addr = core.scratch[addr]
    for vi in range(VLEN):
        self.mem_write[addr + vi] = core.scratch[src + vi]
```

**Sources:** [tests/frozen_problem.py:288-298]()

---

## Two-Phase Memory Commit Model

Memory operations use a two-phase commit model to enable parallel execution within a single cycle. This ensures deterministic behavior when multiple operations in the same instruction bundle access memory.

```mermaid
graph TB
    subgraph Cycle["Machine.step() Cycle"]
        ReadPhase["Read Phase<br/>All engines read from<br/>cycle-start state"]
        WriteBuffer["Write Buffering<br/>Machine.scratch_write = {}<br/>Machine.mem_write = {}"]
        CommitPhase["Commit Phase<br/>Apply all writes<br/>atomically"]
    end
    
    ReadPhase --> WriteBuffer
    WriteBuffer --> CommitPhase
    
    subgraph Details["Implementation Details"]
        D1["1. Initialize empty buffers"]
        D2["2. Execute all slots<br/>Results go to buffers"]
        D3["3. Apply scratch_write<br/>to core.scratch"]
        D4["4. Apply mem_write<br/>to Machine.mem"]
        D5["5. Delete buffers"]
    end
    
    CommitPhase --> Details
```

**Sources:** [tests/frozen_problem.py:352-397]()

### Read Phase

During the read phase, all operations read from the memory and scratch state as it existed at the start of the cycle. The `step` method initializes empty write buffers:

```python
self.scratch_write = {}
self.mem_write = {}
```

All read operations access `core.scratch[addr]` or `self.mem[addr]` directly, seeing the state from the beginning of the cycle.

**Sources:** [tests/frozen_problem.py:363-364]()

### Write Buffering

Operations accumulate their results in write buffers rather than modifying memory directly:

```python
# Example from alu operation
self.scratch_write[dest] = res

# Example from load operation
self.scratch_write[dest] = self.mem[core.scratch[addr]]

# Example from store operation
self.mem_write[addr] = core.scratch[src]
```

**Sources:** [tests/frozen_problem.py:252](), [tests/frozen_problem.py:273](), [tests/frozen_problem.py:292]()

### Commit Phase

After all engines execute their slots, writes are committed atomically:

```python
for addr, val in self.scratch_write.items():
    core.scratch[addr] = val
for addr, val in self.mem_write.items():
    self.mem[addr] = val

del self.scratch_write
del self.mem_write
```

This ensures that:
1. All reads see consistent state from the cycle start.
2. All writes become visible simultaneously at cycle end.
3. There are no read-after-write hazards within a cycle.
4. Parallel execution is deterministic.

**Sources:** [tests/frozen_problem.py:388-397]()

---

## Addressing Conventions

### Scratch Space Addressing

Scratch addresses are direct zero-indexed offsets into the `core.scratch` array. Most instruction operands are scratch addresses:

- Scalar operations use single addresses: `scratch[addr]`
- Vector operations use base addresses: `scratch[base], scratch[base+1], ..., scratch[base+VLEN-1]`

The general convention from the `Machine` class docstring:

> In general every number in an instruction is a scratch address except for const and jump, and except for store and some flow instructions the first operand is the destination.

**Sources:** [tests/frozen_problem.py:86-91]()

### Main Memory Addressing

Main memory uses indirect addressing through scratch space. To access `mem[N]`, you must:

1. Load the address N into a scratch location using `const`.
2. Use that scratch address in a `load` or `store` operation.

Example addressing pattern for loading from `mem[100]`:

```
{"load": [("const", 0, 100)]}        # scratch[0] = 100
{"load": [("load", 1, 0)]}           # scratch[1] = mem[scratch[0]] = mem[100]
```

**Sources:** [tests/frozen_problem.py:269-298]()

### Vector Addressing

Vector operations access VLEN=8 contiguous elements. The base address must refer to the start of an 8-word aligned region:

```python
# vload example
("vload", dest, addr)
# Loads: mem[scratch[addr]], mem[scratch[addr]+1], ..., mem[scratch[addr]+7]
# Into:  scratch[dest], scratch[dest+1], ..., scratch[dest+7]
```

**Sources:** [tests/frozen_problem.py:279-282](), [tests/frozen_problem.py:57]()

---

## Memory Constraints and Considerations

### Size Limits

| Resource | Limit | Constant |
|----------|-------|----------|
| Scratch space per core | 1536 words | `SCRATCH_SIZE` |
| Main memory | Arbitrary size | Depends on problem |
| Vector length | 8 words | `VLEN` |

**Sources:** [tests/frozen_problem.py:57](), [tests/frozen_problem.py:60]()

### Access Bandwidth

The LOAD and STORE engines limit memory bandwidth:

- Maximum 2 scalar loads per cycle.
- Maximum 2 scalar stores per cycle.
- Each `vload` or `vstore` consumes one slot but transfers 8 words.

This creates a bottleneck for memory-intensive operations. Effective optimization requires:
1. Maximizing scratch space reuse.
2. Using vector operations for bulk transfers.
3. Minimizing memory round-trips.

**Sources:** [tests/frozen_problem.py:48-55]()

### Alignment and Packing

The machine does not enforce alignment constraints, but vector operations expect contiguous storage:

- `vload` and `vstore` access sequential addresses.
- Scratch space for vectors should be allocated in contiguous blocks.
- The `KernelBuilder` (in `perf_takehome.py`) must manage allocation to prevent overlaps.

**Sources:** [tests/frozen_problem.py:279-296]()

---

# Page: Execution Model and Cycle Semantics

# Execution Model and Cycle Semantics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



## Purpose and Scope

This document explains how the `Machine` simulator executes instruction bundles and counts cycles. It details the two-phase commit execution model that enables deterministic parallel execution, the rules for cycle counting, and the semantics of instruction execution within a single cycle.

For information about the specific instruction types and their operations, see [Instruction Set Reference](#4.2). For details on the memory system accessed during execution, see [Memory Hierarchy](#4.3).

**Sources:** [tests/frozen_problem.py:64-403](), [problem.py:64-403]()

## Two-Phase Execution Model

The `Machine` implements a **two-phase commit execution model** to ensure deterministic parallel execution. This model prevents race conditions when multiple slots execute simultaneously within a single cycle.

### Execution Phases

Each cycle consists of three distinct phases:

1. **Read Phase**: All engine slots read their operands from the current state of scratch space and memory.
2. **Write Buffering**: All write operations are buffered in temporary dictionaries (`scratch_write` and `mem_write`).
3. **Commit Phase**: All buffered writes are applied atomically to scratch space and memory.

This ensures that all operations within a single instruction bundle see a consistent view of memory and scratch space at the start of the cycle, regardless of execution order.

```mermaid
graph TD
    Start["Cycle N begins"]
    Read["Read Phase<br/>All slots read from<br/>cycle-start state"]
    Buffer["Write Buffering<br/>scratch_write dict<br/>mem_write dict"]
    Commit["Commit Phase<br/>Apply all writes<br/>atomically"]
    End["Cycle N+1 begins"]
    
    Start --> Read
    Read --> Buffer
    Buffer --> Commit
    Commit --> End
    
    subgraph "Single Instruction Bundle"
        Read
        Buffer
        Commit
    end
```

**Diagram: Two-Phase Execution Cycle**

**Sources:** [tests/frozen_problem.py:352-397](), [problem.py:352-397]()

### Implementation Details

The `step()` method in the `Machine` class implements this two-phase model:

| Phase | Implementation | Code Reference |
|-------|---------------|----------------|
| **Initialization** | Create empty write buffers | [tests/frozen_problem.py:363-364]() |
| **Read & Buffer** | Execute all engine slots, populating write buffers | [tests/frozen_problem.py:365-387]() |
| **Commit** | Apply buffered writes to actual state | [tests/frozen_problem.py:388-391]() |
| **Cleanup** | Delete write buffers | [tests/frozen_problem.py:396-397]() |

The write buffers are implemented as dictionaries:

```python
self.scratch_write = {}  # Maps scratch_addr -> value
self.mem_write = {}      # Maps mem_addr -> value
```

Each engine operation writes to these buffers rather than directly modifying state. For example, the ALU operation at [tests/frozen_problem.py:252]() writes `self.scratch_write[dest] = res` rather than `core.scratch[dest] = res`.

**Sources:** [tests/frozen_problem.py:352-397](), [problem.py:352-397]()

## Instruction Bundle Execution

An instruction bundle is a dictionary mapping engine names to lists of operation slots. All slots in the bundle execute in parallel within a single cycle, subject to slot limits per engine.

### Bundle Structure

```mermaid
graph LR
    Bundle["Instruction<br/>dict[Engine, list[tuple]]"]
    
    ALU["alu<br/>list of slots<br/>(max 12)"]
    VALU["valu<br/>list of slots<br/>(max 6)"]
    LOAD["load<br/>list of slots<br/>(max 2)"]
    STORE["store<br/>list of slots<br/>(max 2)"]
    FLOW["flow<br/>list of slots<br/>(max 1)"]
    DEBUG["debug<br/>list of slots<br/>(max 64)"]
    
    Bundle --> ALU
    Bundle --> VALU
    Bundle --> LOAD
    Bundle --> STORE
    Bundle --> FLOW
    Bundle --> DEBUG
```

**Diagram: Instruction Bundle Structure**

**Sources:** [tests/frozen_problem.py:14-15](), [tests/frozen_problem.py:48-55]()

### Execution Flow

The `step()` method processes an instruction bundle as follows:

```mermaid
flowchart TD
    Start["step(instr, core)"]
    InitBuffers["Initialize write buffers<br/>scratch_write = {}<br/>mem_write = {}"]
    IterEngines["For each engine in instr"]
    CheckDebug{"Engine == 'debug'?"}
    ProcessDebug["Process debug slots<br/>(if enable_debug)"]
    CheckSlots["Assert len(slots) <= SLOT_LIMITS[engine]"]
    IterSlots["For each slot in engine"]
    TraceSlot["Trace slot execution<br/>(if trace enabled)"]
    ExecSlot["Execute ENGINE_FNS[engine](core, *slot)"]
    CommitScratch["Commit scratch writes<br/>core.scratch[addr] = val"]
    CommitMem["Commit memory writes<br/>self.mem[addr] = val"]
    TracePost["Trace post-step<br/>(if trace enabled)"]
    End["Return"]
    
    Start --> InitBuffers
    InitBuffers --> IterEngines
    IterEngines --> CheckDebug
    CheckDebug -->|Yes| ProcessDebug
    CheckDebug -->|No| CheckSlots
    ProcessDebug --> IterEngines
    CheckSlots --> IterSlots
    IterSlots --> TraceSlot
    TraceSlot --> ExecSlot
    ExecSlot --> IterSlots
    IterSlots -->|Done| IterEngines
    IterEngines -->|Done| CommitScratch
    CommitScratch --> CommitMem
    CommitMem --> TracePost
    TracePost --> End
```

**Diagram: Instruction Bundle Execution Flow**

**Sources:** [tests/frozen_problem.py:352-397](), [problem.py:352-397]()

### Engine Functions

The `step()` method dispatches to engine-specific functions through the `ENGINE_FNS` dictionary:

| Engine | Function | Purpose |
|--------|----------|---------|
| `alu` | `self.alu()` | Scalar arithmetic operations on scratch space |
| `valu` | `self.valu()` | Vector arithmetic operations (VLEN=8) |
| `load` | `self.load()` | Load from memory to scratch space |
| `store` | `self.store()` | Store from scratch space to memory |
| `flow` | `self.flow()` | Control flow and special operations |

**Sources:** [tests/frozen_problem.py:356-362](), [tests/frozen_problem.py:219-335]()

## Cycle Counting Rules

Cycles are counted in the `run()` method based on specific rules that determine what constitutes a meaningful computational cycle.

### Cycle Counter Increment Logic

```mermaid
flowchart TD
    Start["Process instruction bundle"]
    HasNonDebug["has_non_debug = False"]
    ForCore["For each core"]
    CheckState{"core.state ==<br/>RUNNING?"}
    CheckPC{"core.pc >=<br/>len(program)?"}
    Stop["core.state = STOPPED"]
    GetInstr["instr = program[core.pc]"]
    Print["Print debug info<br/>(if prints enabled)"]
    IncPC["core.pc += 1"]
    Step["step(instr, core)"]
    CheckNonDebug{"Any non-debug<br/>engines?"}
    SetTrue["has_non_debug = True"]
    CheckIncrement{"has_non_debug?"}
    IncCycle["self.cycle += 1"]
    End["Continue to next instruction"]
    
    Start --> HasNonDebug
    HasNonDebug --> ForCore
    ForCore --> CheckState
    CheckState -->|No| ForCore
    CheckState -->|Yes| CheckPC
    CheckPC -->|Yes| Stop
    CheckPC -->|No| GetInstr
    Stop --> ForCore
    GetInstr --> Print
    Print --> IncPC
    IncPC --> Step
    Step --> CheckNonDebug
    CheckNonDebug -->|Yes| SetTrue
    CheckNonDebug -->|No| ForCore
    SetTrue --> ForCore
    ForCore -->|Done| CheckIncrement
    CheckIncrement -->|Yes| IncCycle
    CheckIncrement -->|No| End
    IncCycle --> End
```

**Diagram: Cycle Counting Logic**

The key rules are:

1. **Debug Instructions Don't Count**: Instructions containing only `debug` engine operations do not increment the cycle counter.
2. **One Increment Per Round**: The cycle counter increments at most once per iteration of the main loop, even with multiple cores (though `N_CORES` is currently 1).
3. **Non-Running Cores**: Paused or stopped cores do not prevent cycle counting if other cores are running.

This is implemented at [tests/frozen_problem.py:214-217]():

```python
if any(name != "debug" for name in instr.keys()):
    has_non_debug = True
if has_non_debug:
    self.cycle += 1
```

**Sources:** [tests/frozen_problem.py:197-217](), [problem.py:197-217]()

### What Counts as a Cycle

| Scenario | Cycle Count | Reason |
|----------|-------------|--------|
| Instruction with ALU, LOAD, or STORE operations | +1 | Contains computational work |
| Instruction with only `debug` operations | +0 | Debug operations are for validation only |
| Multiple cores executing in parallel | +1 | All cores execute simultaneously in one cycle |
| Core in PAUSED or STOPPED state | +0 (for that core) | Core is not actively executing |
| Empty instruction (no engines) | +1 | Still consumes a cycle if non-debug engines are absent but keys exist |

**Sources:** [tests/frozen_problem.py:214-217]()

## Core State Management

Each core maintains a state that controls its participation in execution. The `CoreState` enum defines three states:

```mermaid
stateDiagram-v2
    [*] --> RUNNING: Machine.__init__()
    RUNNING --> PAUSED: flow: ("pause",)
    RUNNING --> STOPPED: flow: ("halt",)<br/>or pc >= len(program)
    PAUSED --> RUNNING: Machine.run()<br/>(new invocation)
    STOPPED --> [*]
    
    note right of RUNNING
        Executes instructions
        Increments PC
        Participates in cycles
    end note
    
    note right of PAUSED
        Does not execute
        Awaits run() call
        Used for debugging
    end note
    
    note right of STOPPED
        Permanently halted
        No further execution
        End of program
    end note
```

**Diagram: Core State Transitions**

### State Definitions

- **RUNNING**: Core actively executes instructions, advancing its program counter each cycle.
- **PAUSED**: Core temporarily halts execution but can be resumed by calling `run()` again. Enabled by the `enable_pause` flag.
- **STOPPED**: Core has permanently completed execution, either by reaching the end of the program or executing a `halt` instruction.

The states are defined at [tests/frozen_problem.py:18-21]() and managed in the `Core` dataclass at [tests/frozen_problem.py:24-30]().

**Sources:** [tests/frozen_problem.py:18-30](), [tests/frozen_problem.py:197-217](), [tests/frozen_problem.py:315-319]()

### State Transitions in Code

| Transition | Triggered By | Code Location |
|------------|--------------|---------------|
| Init → RUNNING | Core creation | [tests/frozen_problem.py:30]() |
| PAUSED → RUNNING | `run()` method start | [tests/frozen_problem.py:198-200]() |
| RUNNING → STOPPED | PC exceeds program length | [tests/frozen_problem.py:206-208]() |
| RUNNING → STOPPED | `halt` flow instruction | [tests/frozen_problem.py:315-316]() |
| RUNNING → PAUSED | `pause` flow instruction | [tests/frozen_problem.py:317-319]() |

**Sources:** [tests/frozen_problem.py:197-217](), [tests/frozen_problem.py:315-319]()

## Parallel Execution Within a Cycle

Multiple operations execute simultaneously within a single cycle, limited only by the slot constraints per engine. The two-phase commit model ensures deterministic results regardless of internal execution order.

### Slot Parallelism

Each engine can execute multiple slots in parallel:

| Engine | Slot Limit | Description |
|--------|-----------|-------------|
| `alu` | 12 | Up to 12 scalar operations per cycle |
| `valu` | 6 | Up to 6 vector operations (8 elements each) per cycle |
| `load` | 2 | Up to 2 memory reads per cycle |
| `store` | 2 | Up to 2 memory writes per cycle |
| `flow` | 1 | One control flow operation per cycle |
| `debug` | 64 | Up to 64 debug operations (don't count toward cycles) |

The limits are enforced at [tests/frozen_problem.py:383]() with an assertion: `assert len(slots) <= SLOT_LIMITS[name]`

**Sources:** [tests/frozen_problem.py:48-55](), [tests/frozen_problem.py:383]()

### Example: Parallel Execution

Consider this instruction bundle:

```python
{
    "valu": [("*", 4, 0, 0), ("+", 8, 4, 0)],
    "load": [("load", 16, 17)]
}
```

Execution sequence:

```mermaid
graph TD
    Start["Cycle Start<br/>scratch_write = {}<br/>mem_write = {}"]
    
    subgraph "Read Phase (All operations read current state)"
        VALU1["valu slot 0: Multiply<br/>Read scratch[0], scratch[0]"]
        VALU2["valu slot 1: Add<br/>Read scratch[4], scratch[0]"]
        LOAD1["load slot 0: Load<br/>Read scratch[17]<br/>Read mem[scratch[17]]"]
    end
    
    subgraph "Write Buffer Phase"
        VALU1_W["Buffer: scratch_write[4:12] = results"]
        VALU2_W["Buffer: scratch_write[8:16] = results"]
        LOAD1_W["Buffer: scratch_write[16] = mem value"]
    end
    
    subgraph "Commit Phase"
        Commit["Atomically apply:<br/>scratch[4:12] = scratch_write[4:12]<br/>scratch[8:16] = scratch_write[8:16]<br/>scratch[16] = scratch_write[16]"]
    end
    
    Start --> VALU1
    Start --> VALU2
    Start --> LOAD1
    
    VALU1 --> VALU1_W
    VALU2 --> VALU2_W
    LOAD1 --> LOAD1_W
    
    VALU1_W --> Commit
    VALU2_W --> Commit
    LOAD1_W --> Commit
    
    Commit --> End["Cycle End<br/>cycle += 1"]
```

**Diagram: Example Parallel Execution**

Key observations:

1. All three operations read from the scratch/memory state at the start of the cycle.
2. The multiply operation at `scratch[4]` and the add operation at `scratch[8]` don't interfere with each other.
3. Even though the multiply writes to `scratch[4]` and the add reads from `scratch[4]`, the add sees the value from the start of the cycle, not the result of the multiply.
4. All writes are applied atomically at the end.

**Sources:** [tests/frozen_problem.py:352-397](), [tests/frozen_problem.py:254-267](), [tests/frozen_problem.py:269-286]()

### Deterministic Execution Guarantees

The two-phase model provides these guarantees:

1. **Read Consistency**: All operations within a cycle see the same initial state.
2. **Write Atomicity**: All writes appear to happen simultaneously at cycle end.
3. **Order Independence**: The execution order of slots within an engine doesn't affect the result.
4. **No Read-After-Write Within Cycle**: Operations cannot see the results of other operations in the same cycle.

These properties enable aggressive parallelization while maintaining predictable semantics, making the simulator easier to reason about and optimize for.

**Sources:** [tests/frozen_problem.py:352-397](), [problem.py:352-397]()

---

# Page: Frozen vs Development Simulators

# Frozen vs Development Simulators

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page explains why the repository contains two nearly identical simulator implementations and when to use each one. For details about the simulator architecture itself, see [Machine Architecture](#4). For information about running tests, see [Test Suite Structure](#6.1).

## Purpose and Scope

The repository maintains two separate implementations of the VLIW SIMD machine simulator: a frozen version for testing and a development version for iteration. This separation ensures fair performance comparison across different optimization attempts while allowing developers to experiment with simulator modifications during development.

## Why Two Simulator Versions Exist

The repository contains two functionally identical files:
- [problem.py:1-569]() - Development simulator
- [tests/frozen_problem.py:1-569]() - Frozen simulator for testing

Both files contain the same classes and functions:
- `Machine` - The VLIW SIMD simulator [problem.py:64-95]() [tests/frozen_problem.py:64-95]()
- `Core` - Dataclass representing core state [problem.py:24-31]() [tests/frozen_problem.py:24-31]()
- `DebugInfo` - Metadata for variable mapping [problem.py:33-42]() [tests/frozen_problem.py:33-42]()
- Supporting constants: `SLOT_LIMITS`, `VLEN`, `N_CORES`, `SCRATCH_SIZE` [problem.py:48-61]() [tests/frozen_problem.py:48-61]()

**Sources:** [problem.py:1-7](), [tests/frozen_problem.py:1-7]()

## The Frozen Simulator: Ensuring Fair Comparison

### Purpose

The frozen simulator in [tests/frozen_problem.py]() serves as the immutable reference implementation used by all submission tests. This guarantees that:

1. **Consistent validation** - All optimizations are validated against the same reference implementation.
2. **Fair benchmarking** - Cycle counts are measured using identical execution semantics.
3. **Reproducible results** - Test results remain stable across development sessions.

### Usage in Testing

The submission test suite imports exclusively from the frozen simulator to ensure that any local changes to `problem.py` do not accidentally invalidate benchmark results.

**Code Entity Mapping: Test Suite to Frozen Entities**
```mermaid
graph LR
    subgraph TestSuite["tests/submission_tests.py"]
        Imports["from frozen_problem import<br/>Machine, Tree, Input,<br/>reference_kernel2,<br/>build_mem_image"]
        CorrectnessTests["CorrectnessTests"]
        SpeedTests["SpeedTests"]
    end
    
    subgraph FrozenModule["tests/frozen_problem.py"]
        FrozenMachine["Machine class"]
        FrozenRef["reference_kernel2"]
        FrozenTree["Tree class"]
        FrozenInput["Input class"]
        FrozenBuild["build_mem_image"]
    end
    
    Imports --> FrozenMachine
    Imports --> FrozenRef
    Imports --> FrozenTree
    Imports --> FrozenInput
    Imports --> FrozenBuild
    
    FrozenMachine --> CorrectnessTests
    FrozenRef --> CorrectnessTests
    FrozenMachine --> SpeedTests
```

**Sources:** [tests/submission_tests.py:11-19]()

### Test Execution Flow

The test suite orchestrates the relationship between your optimized `KernelBuilder` and the `Machine` simulator defined in the frozen file.

**Sequence: Execution using Frozen Machine**
```mermaid
sequenceDiagram
    participant Test as submission_tests.py
    participant KB as KernelBuilder<br/>(perf_takehome.py)
    participant Frozen as frozen_problem.py
    
    Note over Test,Frozen: All imports from frozen_problem
    
    Test->>Frozen: Tree.generate(height)
    Frozen-->>Test: Tree instance
    
    Test->>Frozen: Input.generate(tree, batch, rounds)
    Frozen-->>Test: Input instance
    
    Test->>Frozen: build_mem_image(tree, inp)
    Frozen-->>Test: mem array
    
    Test->>KB: build_kernel(height, n_nodes, batch, rounds)
    KB-->>Test: instructions
    
    Test->>Frozen: Machine(mem, instrs, debug_info)
    Note over Frozen: Frozen simulator executes
    Test->>Frozen: machine.run()
    Frozen-->>Test: cycle count
    
    Test->>Frozen: reference_kernel2(mem)
    Frozen-->>Test: expected memory state
    
    Note over Test: Compare machine.mem vs ref_mem
```

**Sources:** [tests/submission_tests.py:30-54]()

## The Development Simulator: Enabling Experimentation

### Purpose

The development simulator in [problem.py]() serves several purposes:

1. **Debugging tool** - Can be modified to add logging, assertions, or custom instrumentation.
2. **Experimentation** - Test hypothetical ISA extensions or execution model changes.
3. **Understanding** - Read and study the simulator without worrying about breaking tests.
4. **Trace generation** - Enable tracing during development without affecting test imports.

### When to Use the Development Simulator

Use [problem.py]() when:

| Scenario | Example |
|----------|---------|
| **Local testing** | Manually running your `KernelBuilder` to check correctness before running full tests. |
| **Debugging** | Adding print statements to `Machine.step()` to understand instruction execution. |
| **Trace generation** | Running with `trace=True` to generate Perfetto traces. |
| **ISA experimentation** | Testing whether a new instruction type would help your optimization. |
| **Learning** | Understanding how the VLIW execution model works. |

**Sources:** [problem.py:64-122](), [problem.py:151-196]()

## Key Architectural Guarantee

Both simulators implement **identical execution semantics**. The implementations are byte-for-byte copies (or nearly so), ensuring that results are consistent.

**System Mapping: Consistency between Implementations**
```mermaid
graph TB
    subgraph Inputs
        Tree["Tree + Input + Instructions"]
    end
    
    subgraph Simulators
        Dev["problem.py<br/>Machine"]
        Frozen["frozen_problem.py<br/>Machine"]
    end
    
    subgraph Outputs
        DevResult["Cycle Count<br/>Memory State"]
        FrozenResult["Cycle Count<br/>Memory State"]
    end
    
    Tree --> Dev
    Tree --> Frozen
    Dev --> DevResult
    Frozen --> FrozenResult
    
    DevResult -.->|"MUST BE<br/>IDENTICAL"| FrozenResult
```

Both simulators share:
- **Same slot limits:** `SLOT_LIMITS` defined in [problem.py:48-55]() and [tests/frozen_problem.py:48-55]().
- **Same SIMD width:** `VLEN = 8` [problem.py:57]().
- **Same scratch size:** `SCRATCH_SIZE = 1536` [problem.py:60]().
- **Identical instruction semantics** in `run()` and internal engine processing [problem.py:197-217]().

**Sources:** [problem.py:48-61](), [tests/frozen_problem.py:48-61](), [problem.py:197-217](), [tests/frozen_problem.py:197-217]()

## Practical Implications

### For Optimization Work

| Activity | Use Simulator | Rationale |
|----------|---------------|-----------|
| **Running submission tests** | Frozen (automatic) | Tests always import from `frozen_problem` [tests/submission_tests.py:11-19](). |
| **Debugging your KernelBuilder** | Development | Can add instrumentation without affecting tests. |
| **Generating traces** | Development | Trace files don't affect test results [problem.py:160](). |
| **Understanding ISA** | Development | Study and experiment freely. |
| **Measuring final performance** | Frozen (automatic) | Tests provide official cycle counts. |

### What You Can Modify

**Development simulator (`problem.py`):**
- ✅ Add debug prints to `Machine.print_step()` [problem.py:134-139]().
- ✅ Modify `setup_trace()` to capture additional events [problem.py:151-196]().
- ✅ Add assertions to validate assumptions.

**Frozen simulator (`tests/frozen_problem.py`):**
- ❌ Do not modify - changes won't be used by the official benchmarking suite.
- ❌ Even if modified locally, the repository structure treats this as a read-only snapshot for testing.

### Performance Measurement Flow

```mermaid
graph TB
    subgraph Development
        DevScript["Your script<br/>from problem import Machine"]
        DevMachine["problem.py Machine"]
        QuickTest["Quick correctness check<br/>Informal cycle count"]
    end
    
    subgraph Testing
        SubmitTests["python tests/submission_tests.py"]
        FrozenMachine["frozen_problem.py Machine"]
        OfficialCycles["Official cycle count<br/>Used for benchmarks"]
    end
    
    DevScript --> DevMachine
    DevMachine --> QuickTest
    QuickTest -.->|"Ready for testing"| SubmitTests
    SubmitTests --> FrozenMachine
    FrozenMachine --> OfficialCycles
```

**Sources:** [tests/submission_tests.py:30-54](), [tests/submission_tests.py:66-73]()

## The Copy Comment

Both files begin with this explanatory comment, reinforcing the design intent:

```python
"""
Read the top of perf_takehome.py for more introduction.

This file is separate mostly for ease of copying it to freeze the machine and
reference kernel for testing.
"""
```

**Sources:** [problem.py:1-6](), [tests/frozen_problem.py:1-6]()

---

# Page: Kernel Builder - The Optimization Target

# Kernel Builder - The Optimization Target

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perf_takehome.py](perf_takehome.py)

</details>



This document provides high-level documentation of the `KernelBuilder` class in [perf_takehome.py:40-171](), which is the **primary optimization target** of the performance challenge. The `KernelBuilder` is responsible for generating VLIW instruction bundles that execute the tree traversal algorithm on the custom simulator.

## KernelBuilder Role and Responsibilities

The `KernelBuilder` sits between the problem definition and the simulator, translating high-level algorithm structure into low-level VLIW instructions. It handles memory management for "scratch space" (the processor's fast local memory) and the assembly of instruction bundles.

```mermaid
graph TB
    Input["Input Parameters<br/>forest_height, n_nodes<br/>batch_size, rounds"]
    KB["KernelBuilder<br/>perf_takehome.py:40-171"]
    BuildKernel["build_kernel()<br/>perf_takehome.py:88-171"]
    Helpers["Helper Methods<br/>alloc_scratch()<br/>scratch_const()<br/>build_hash()"]
    
    InstrList["Instruction List<br/>list[dict[Engine, list[tuple]]]"]
    Machine["Machine Simulator<br/>problem.py:64-403"]
    
    Input --> BuildKernel
    BuildKernel --> Helpers
    Helpers --> BuildKernel
    KB --> InstrList
    InstrList --> Machine
    
    subgraph "Your Optimization Target"
        BuildKernel
        Helpers
    end
```

Sources: [perf_takehome.py:40-171](), [problem.py:64-403]()

## Key Components

### KernelBuilder Class Overview
The class maintains the state of the kernel being built, including the instruction stream (`instrs`), a mapping of scratch space variables (`scratch`), and a constant cache (`const_map`). It provides the foundational API for allocating memory and adding operations to the execution pipeline.

For details, see [KernelBuilder Class Overview](#5.1).

### The build_kernel Method
This is the core method where the optimization challenge takes place. It implements the tree traversal logic by generating a sequence of instructions. The baseline implementation is a scalar, unrolled loop that processes one batch element at a time, resulting in a cycle count of approximately 147,734.

For details, see [The build_kernel Method](#5.2).

### Helper Methods and Utilities
The builder includes utility methods to simplify instruction generation:
*   `alloc_scratch`: Manages the limited `SCRATCH_SIZE` (1536 words) by allocating addresses for variables.
*   `scratch_const`: Loads a constant into scratch space and deduplicates it to save memory.
*   `build_hash`: Generates the 24-slot sequence required for the multi-stage hashing algorithm.

For details, see [Helper Methods and Utilities](#5.3).

### Optimization Strategies and Patterns
To reach the recruitment gate (1,487 cycles) or the top AI benchmarks (1,363 cycles), the kernel must be transformed from scalar execution to highly parallel VLIW/SIMD execution. This involves packing multiple operations into a single cycle and using vector instructions (`valu`, `vload`) to process 8 elements (the `VLEN`) simultaneously.

For details, see [Optimization Strategies and Patterns](#5.4).

## System Entity Mapping

The following diagram maps the high-level builder concepts to the specific code entities in the repository.

```mermaid
graph LR
    subgraph "Kernel Logic"
        BK["build_kernel()"]
        BH["build_hash()"]
    end

    subgraph "Memory Management"
        AS["alloc_scratch()"]
        SC["scratch_const()"]
        SM["scratch_ptr"]
    end

    subgraph "Instruction Output"
        INST["self.instrs"]
        AD["add()"]
        BLD["build()"]
    end

    BK --> BH
    BK --> AS
    BK --> SC
    BK --> AD
    BH --> SC
    AS --> SM
    AD --> INST
    BLD --> INST

    style BK stroke-width:4px
```

Sources: [perf_takehome.py:40-171]()

## Summary of Optimization Target

| Feature | Baseline Implementation | Optimization Goal |
| :--- | :--- | :--- |
| **Instruction Packing** | 1 slot per cycle [perf_takehome.py:54-56]() | Up to 23 slots per cycle [problem.py:48-55]() |
| **Data Width** | Scalar (1 element) | Vectorized (8 elements/`VLEN`) [problem.py:57]() |
| **Engine Usage** | `alu`, `load`, `store` | `valu`, `vload`, `vstore`, `flow` |
| **Cycle Count** | 147,734 | < 1,487 |

Sources: [perf_takehome.py:176](), [problem.py:48-57]()

---

# Page: KernelBuilder Class Overview

# KernelBuilder Class Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perf_takehome.py](perf_takehome.py)

</details>



## Purpose and Scope

This document provides an overview of the `KernelBuilder` class defined in [perf_takehome.py:40-172](). The `KernelBuilder` is the primary optimization target in this performance benchmark—it generates instruction sequences that execute on the custom VLIW SIMD machine simulator. This page covers the class's role, structure, and responsibilities. For detailed implementation of specific methods, see [The build_kernel Method](5.2) and [Helper Methods and Utilities](5.3).

**Sources:** [perf_takehome.py:1-17](), [perf_takehome.py:40-172]()

## Role in System Architecture

The `KernelBuilder` sits at the center of the optimization challenge, transforming problem parameters into executable instruction sequences:

```mermaid
graph TB
    ProblemParams["Problem Parameters<br/>(forest_height, n_nodes,<br/>batch_size, rounds)"]
    KB["KernelBuilder<br/>perf_takehome.py:40-172"]
    BuildKernel["build_kernel()<br/>Line 88"]
    Instructions["Instruction List<br/>List[Dict[Engine, List[Tuple]]]"]
    DebugInfo["DebugInfo<br/>scratch_map"]
    Machine["Machine Simulator<br/>problem.py"]
    Memory["Memory Image<br/>Tree + Input data"]
    Execution["Execution Result<br/>Cycle Count"]
    
    ProblemParams --> BuildKernel
    BuildKernel --> KB
    KB --> Instructions
    KB --> DebugInfo
    Instructions --> Machine
    DebugInfo --> Machine
    Memory --> Machine
    Machine --> Execution
    
    style KB stroke-width:3px
    style BuildKernel stroke-width:2px
```

**Diagram: KernelBuilder in the execution pipeline**

The `KernelBuilder` receives dimensional information about the problem (tree height, batch size, etc.) and produces:
1. A list of instruction bundles (`self.instrs`) that the `Machine` simulator executes [perf_takehome.py:42]().
2. Debug information (`DebugInfo`) that maps scratch addresses to variable names for tracing [perf_takehome.py:48-49]().

**Sources:** [perf_takehome.py:40-50](), [perf_takehome.py:88-172](), [problem.py:288-305]()

## Class Structure and Responsibilities

The `KernelBuilder` class is defined at [perf_takehome.py:40-172]() and has three primary responsibilities:

| Responsibility | Description | Key Methods |
|---|---|---|
| **Instruction Generation** | Create VLIW instruction bundles for the target architecture | `add()`, `build()`, `build_kernel()` |
| **Scratch Memory Management** | Allocate and track scratch space addresses | `alloc_scratch()`, `scratch_const()` |
| **Constant Optimization** | Deduplicate and reuse constant values | `scratch_const()` via `const_map` |

```mermaid
graph LR
    subgraph KernelBuilder["KernelBuilder Class"]
        Init["__init__()<br/>Initialize state"]
        BuildKernel["build_kernel()<br/>Main entry point"]
        Add["add()<br/>Append instruction"]
        Build["build()<br/>Pack slots into bundles"]
        AllocScratch["alloc_scratch()<br/>Allocate scratch addr"]
        ScratchConst["scratch_const()<br/>Load constant"]
        BuildHash["build_hash()<br/>Generate hash ops"]
        DebugInfo["debug_info()<br/>Return DebugInfo"]
    end
    
    BuildKernel --> Add
    BuildKernel --> AllocScratch
    BuildKernel --> ScratchConst
    BuildKernel --> BuildHash
    BuildHash --> Add
    ScratchConst --> AllocScratch
    ScratchConst --> Add
```

**Diagram: KernelBuilder method relationships**

**Sources:** [perf_takehome.py:40-172]()

## Instance Variables

The `KernelBuilder` maintains state across instruction generation in several instance variables initialized at [perf_takehome.py:41-46]():

| Variable | Type | Purpose | Initialized To |
|---|---|---|---|
| `instrs` | `list` | Accumulates generated instruction bundles | `[]` |
| `scratch` | `dict` | Maps variable names to scratch addresses | `{}` |
| `scratch_debug` | `dict` | Maps scratch addresses to `(name, length)` tuples for debugging | `{}` |
| `scratch_ptr` | `int` | Current scratch space allocation pointer | `0` |
| `const_map` | `dict` | Maps constant values to their scratch addresses (deduplication) | `{}` |

```mermaid
graph TB
    subgraph State["KernelBuilder State"]
        Instrs["instrs: List[Dict]<br/>Generated instructions"]
        Scratch["scratch: Dict[str, int]<br/>name → address"]
        ScratchDebug["scratch_debug: Dict[int, Tuple]<br/>address → (name, length)"]
        ScratchPtr["scratch_ptr: int<br/>Next free address"]
        ConstMap["const_map: Dict[int, int]<br/>value → address"]
    end
    
    AllocOp["alloc_scratch() call"]
    AddOp["add() call"]
    ConstOp["scratch_const() call"]
    
    AllocOp --> ScratchPtr
    AllocOp --> Scratch
    AllocOp --> ScratchDebug
    AddOp --> Instrs
    ConstOp --> ConstMap
    ConstOp --> AllocOp
    ConstOp --> AddOp
```

**Diagram: Instance variable usage pattern**

**Sources:** [perf_takehome.py:41-46]()

## Method Categories

The `KernelBuilder` methods can be categorized by their function:

### Core Generation Methods

| Method | Lines | Purpose |
|---|---|---|
| `build_kernel()` | [perf_takehome.py:88-172]() | Main entry point that generates the complete kernel instruction sequence |
| `build()` | [perf_takehome.py:51-56]() | Packs a list of `(engine, slot)` tuples into instruction bundles |
| `add()` | [perf_takehome.py:58-59]() | Appends a single instruction bundle to `self.instrs` |

### Scratch Space Management

| Method | Lines | Purpose |
|---|---|---|
| `alloc_scratch()` | [perf_takehome.py:61-68]() | Allocates scratch space and updates tracking maps |
| `scratch_const()` | [perf_takehome.py:70-75]() | Loads a constant into scratch, reusing if already loaded |

### Helper Methods

| Method | Lines | Purpose |
|---|---|---|
| `build_hash()` | [perf_takehome.py:77-86]() | Generates instruction slots for the hash computation stages |
| `debug_info()` | [perf_takehome.py:48-49]() | Returns `DebugInfo` object for trace visualization |

**Sources:** [perf_takehome.py:40-172]()

## Instruction Generation Process

The `KernelBuilder` follows a specific workflow when generating instructions:

```mermaid
sequenceDiagram
    participant User
    participant KB as KernelBuilder
    participant Scratch as Scratch Allocator
    participant Instrs as Instruction List
    
    User->>KB: __init__()
    KB->>KB: Initialize state variables
    
    User->>KB: build_kernel(forest_height, n_nodes, batch_size, rounds)
    
    KB->>Scratch: alloc_scratch("tmp1")
    Scratch-->>KB: Returns address 0
    
    KB->>Scratch: alloc_scratch("rounds")
    Scratch-->>KB: Returns address 3
    
    KB->>KB: scratch_const(0)
    KB->>Scratch: alloc_scratch(None)
    KB->>Instrs: add("load", ("const", addr, 0))
    
    loop For each instruction
        KB->>Instrs: add(engine, slot)
    end
    
    KB->>KB: build(body_slots)
    KB->>Instrs: Extend with body instructions
    
    KB->>Instrs: add("flow", ("pause",))
    
    User->>KB: debug_info()
    KB-->>User: DebugInfo(scratch_map)
```

**Diagram: Instruction generation sequence**

The process consists of:

1. **Initialization**: Create `KernelBuilder` instance, initializing all state to empty/zero [perf_takehome.py:41-46]().
2. **Scratch Allocation**: Reserve scratch addresses for variables and constants [perf_takehome.py:95-116]().
3. **Instruction Emission**: Generate instruction slots and add them to `self.instrs` [perf_takehome.py:112-172]().
4. **Packing**: Convert slot lists into instruction bundles via `build()` method [perf_takehome.py:51-56]().
5. **Debug Info**: Extract debug information mapping for trace visualization [perf_takehome.py:48-49]().

**Sources:** [perf_takehome.py:40-174]()

## Scratch Memory Management Strategy

The `KernelBuilder` implements a simple linear allocator for scratch space, enforcing the `SCRATCH_SIZE` limit defined in [problem.py:29]():

```mermaid
graph TB
    subgraph ScratchSpace["Scratch Space (1536 words per core)"]
        Addr0["Address 0<br/>tmp1"]
        Addr1["Address 1<br/>tmp2"]
        Addr2["Address 2<br/>tmp3"]
        Addr3["Address 3<br/>rounds"]
        AddrN["Address N<br/>..."]
        ScratchPtr["scratch_ptr<br/>Next free address"]
        Free["Free space"]
    end
    
    Alloc1["alloc_scratch('tmp1')"]
    Alloc2["alloc_scratch('rounds')"]
    ConstAlloc["scratch_const(42)"]
    
    Alloc1 --> Addr0
    Alloc2 --> Addr3
    ConstAlloc --> AddrN
    
    ScratchPtr -.-> Free
```

**Diagram: Scratch space allocation**

Key characteristics:

- **Linear Allocation**: `scratch_ptr` increments by `length` on each allocation at [perf_takehome.py:66]().
- **Named Variables**: Optional `name` parameter creates entries in `scratch` and `scratch_debug` maps at [perf_takehome.py:63-65]().
- **Bounds Checking**: Asserts that `scratch_ptr <= SCRATCH_SIZE` at [perf_takehome.py:67]().
- **Constant Deduplication**: `scratch_const()` uses `const_map` to reuse previously loaded constants at [perf_takehome.py:70-75]().

**Sources:** [perf_takehome.py:61-75](), [problem.py:29]()

## Instruction Format and Engine Types

The `KernelBuilder` generates instructions as dictionaries mapping `Engine` types to lists of operation tuples:

```mermaid
graph LR
    Instruction["Instruction<br/>(dict)"]
    
    Instruction --> ALU["Engine.ALU<br/>List of (op, dst, src1, src2)"]
    Instruction --> VALU["Engine.VALU<br/>List of vector ops"]
    Instruction --> LOAD["Engine.LOAD<br/>List of (type, dst, src)"]
    Instruction --> STORE["Engine.STORE<br/>List of (type, dst, src)"]
    Instruction --> FLOW["Engine.FLOW<br/>List of control ops"]
    Instruction --> DEBUG["Engine.DEBUG<br/>List of debug ops"]
    
    ALU --> Slot1["Slot 1"]
    ALU --> SlotN["Slot N"]
```

**Diagram: Instruction bundle structure**

Example instruction bundle generated by `add("alu", ("+", dst, src1, src2))` [perf_takehome.py:59]():
```python
{"alu": [("+", dst, src1, src2)]}
```

The `build()` method at [perf_takehome.py:51-56]() currently creates one bundle per slot (no packing), but the `vliw` parameter in the method signature suggests the class is intended to support packing multiple operations into single cycles.

**Sources:** [perf_takehome.py:51-59](), [problem.py:24-26]()

## Relationship with Machine Simulator

The `KernelBuilder` output interfaces directly with the `Machine` simulator defined in [problem.py:305]():

```mermaid
graph TB
    KB["KernelBuilder"]
    Instrs["self.instrs<br/>List[Dict[Engine, List[Tuple]]]"]
    DebugInfo["DebugInfo<br/>scratch_map"]
    
    Machine["Machine.__init__()<br/>problem.py"]
    Cores["Core instances<br/>N_CORES cores"]
    ScratchSpace["Scratch space<br/>SCRATCH_SIZE per core"]
    Execute["Machine.run()<br/>Execute instructions"]
    
    KB --> Instrs
    KB --> DebugInfo
    
    Instrs --> Machine
    DebugInfo --> Machine
    Machine --> Cores
    Cores --> ScratchSpace
    Machine --> Execute
    
    Execute --> CycleCount["Cycle Count<br/>Performance metric"]
    Execute --> MemState["Memory State<br/>Correctness validation"]
```

**Diagram: KernelBuilder output to Machine simulator**

The `Machine` receives:
1. **Memory image**: Built by `build_mem_image()` from `Tree` and `Input` objects [problem.py:228-254]().
2. **Instructions**: `kb.instrs` list generated by `build_kernel()` [perf_takehome.py:171-172]().
3. **Debug info**: `kb.debug_info()` containing scratch variable mappings [perf_takehome.py:48-49]().

The `Machine` then executes the instruction sequence, updating memory and counting cycles until completion [problem.py:382-392]().

**Sources:** [perf_takehome.py:40-50](), [problem.py:228-254](), [problem.py:305-392]()

---

# Page: The build_kernel Method

# The build_kernel Method

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perf_takehome.py](perf_takehome.py)

</details>



## Purpose and Scope

This page documents the `build_kernel` method in the `KernelBuilder` class [perf_takehome.py:40-175](), which is the core optimization target of this performance challenge. The method generates a sequence of VLIW instruction bundles that implement the tree traversal algorithm when executed by the `Machine` simulator.

The current implementation provides a functional baseline that uses scalar operations and no instruction packing. Achieving competitive cycle counts requires modifying this method to utilize the vector engine (VALU) and the VLIW capabilities of the architecture.

**Sources:** [perf_takehome.py:40-175]()

## Method Signature and Parameters

```python
def build_kernel(
    self, forest_height: int, n_nodes: int, batch_size: int, rounds: int
):
```
[perf_takehome.py:88-90]()

The method accepts four parameters that define the problem dimensions:

| Parameter | Type | Description | Example Value |
|-----------|------|-------------|---------------|
| `forest_height` | `int` | Height of the balanced binary tree | 10 |
| `n_nodes` | `int` | Total number of nodes in tree (2^(height+1) - 1) | 2047 |
| `batch_size` | `int` | Number of parallel tree traversals | 256 |
| `rounds` | `int` | Number of iterations per traversal | 16 |

These parameters are derived from `Tree` [problem.py:448-472]() and `Input` [problem.py:474-485]() objects. The method generates instructions based on these dimensions, which will later be executed by the `Machine` simulator on actual problem data.

**Sources:** [perf_takehome.py:88-90](), [problem.py:448-485]()

## Method Structure Overview

The `build_kernel` method follows a structured approach to instruction generation:

```mermaid
flowchart TD
    Start["build_kernel entry"]
    Start --> Alloc["Allocate scratch space<br/>(tmp1, tmp2, tmp3)"]
    Alloc --> InitVars["Allocate init_vars scratch<br/>(rounds, n_nodes, batch_size,<br/>forest_height, pointers)"]
    InitVars --> LoadHeader["Generate load instructions<br/>for header values"]
    LoadHeader --> Constants["Allocate constants<br/>(0, 1, 2)"]
    Constants --> Pause1["Add pause & debug comment"]
    Pause1 --> LoopVars["Allocate loop scratch registers<br/>(tmp_idx, tmp_val,<br/>tmp_node_val, tmp_addr)"]
    LoopVars --> GenBody["Generate nested loop body<br/>(rounds × batch_size)"]
    GenBody --> Build["Call self.build() to pack<br/>slots into instruction bundles"]
    Build --> Append["Append instructions to self.instrs"]
    Append --> Pause2["Add final pause instruction"]
    Pause2 --> End["Return (implicit)"]
    
    style GenBody fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Diagram: build_kernel Execution Flow**

The method generates instructions in phases. Note that `build_kernel` itself does not perform the tree traversal; it generates the code that the simulator will use to perform the traversal.

**Sources:** [perf_takehome.py:88-175]()

## Initialization Phase

### Temporary Variable Allocation

The method begins by allocating temporary scratch registers used throughout instruction generation:

[perf_takehome.py:95-97]()

These temporaries (`tmp1`, `tmp2`, `tmp3`) are reused across multiple operations to manage scratch space.

### Header Variable Loading

The method allocates scratch space for variables that correspond to the memory header layout defined by `build_mem_image` [problem.py:487-514]():

[perf_takehome.py:98-113]()

```mermaid
flowchart LR
    subgraph "Memory Header (mem[0:6])"
        M0["mem[0]: rounds"]
        M1["mem[1]: n_nodes"]
        M2["mem[2]: batch_size"]
        M3["mem[3]: forest_height"]
        M4["mem[4]: forest_values_p"]
        M5["mem[5]: inp_indices_p"]
        M6["mem[6]: inp_values_p"]
    end
    
    subgraph "Scratch Space (Core.scratch)"
        S0["scratch[rounds]"]
        S1["scratch[n_nodes]"]
        S2["scratch[batch_size]"]
        S3["scratch[forest_height]"]
        S4["scratch[forest_values_p]"]
        S5["scratch[inp_indices_p]"]
        S6["scratch[inp_values_p]"]
    end
    
    M0 -.->|"load instruction"| S0
    M1 -.->|"load instruction"| S1
    M2 -.->|"load instruction"| S2
    M3 -.->|"load instruction"| S3
    M4 -.->|"load instruction"| S4
    M5 -.->|"load instruction"| S5
    M6 -.->|"load instruction"| S6
```

**Diagram: Header Loading - Memory to Scratch Mapping**

For each header variable, the method generates:
1. A `const` load to put the memory offset (0-6) into `tmp1` [perf_takehome.py:111]()
2. A `load` instruction to read `mem[tmp1]` into the designated scratch location [perf_takehome.py:112]()

### Constant Allocation

Commonly-used constants are allocated and cached using `scratch_const` [perf_takehome.py:70-75]():

[perf_takehome.py:114-116]()

**Sources:** [perf_takehome.py:70-75](), [perf_takehome.py:95-116](), [problem.py:487-514]()

## Synchronization and Debug Support

After initialization, the method adds a `pause` instruction and debug comment:

[perf_takehome.py:122-124]()

The `pause` instruction synchronizes with `yield` statements in `reference_kernel2` [problem.py:548](). During testing with `do_kernel_test`, the machine pauses here allowing correctness validation. The submission harness ignores pause instructions.

**Sources:** [perf_takehome.py:122-124](), [problem.py:535-569]()

## Main Loop Structure

### Loop Variable Allocation

Before generating the loop body, scratch registers are allocated for variables used in each iteration:

[perf_takehome.py:129-132]()

These correspond to logic in `reference_kernel2` [problem.py:549-565]():
- `tmp_idx`: Current tree node index.
- `tmp_val`: Current hash value.
- `tmp_node_val`: Tree node value fetched from memory.
- `tmp_addr`: Temporary address calculation.

### Nested Loop Generation

The method generates instructions for nested loops using Python loops:

[perf_takehome.py:134-170]()

```mermaid
flowchart TD
    Start["for round in range(rounds)"]
    Start --> Inner["for i in range(batch_size)"]
    Inner --> GenSlots["Generate instruction slots<br/>for this (round, i) pair"]
    GenSlots --> AppendBody["Append slots to body[] list"]
    AppendBody --> NextI{More i values?}
    NextI -->|Yes| Inner
    NextI -->|No| NextR{More rounds?}
    NextR -->|Yes| Start
    NextR -->|No| BuildInstrs["Call self.build(body)<br/>to pack into VLIW bundles"]
    BuildInstrs --> Done["body_instrs complete"]
    
    style GenSlots fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Diagram: Loop Unrolling Strategy**

This implementation **fully unrolls** both loops at kernel generation time. For the standard test case (rounds=16, batch_size=256), this generates 4,096 iterations. Each iteration produces approximately 36 instruction slots, resulting in a large linear sequence of instruction bundles.

**Sources:** [perf_takehome.py:134-170]()

## Tree Traversal Step Implementation

Each loop iteration generates instructions that implement one step of the tree traversal:

### Step 1: Load Current Index and Value
The kernel computes the address for `inp_indices_p + i` and `inp_values_p + i`, then loads the data into `tmp_idx` and `tmp_val` [perf_takehome.py:138-143]().

### Step 2: Load Node Value
The kernel uses the current index to fetch the node value from the tree: `mem[forest_values_p + idx]` [perf_takehome.py:146-147]().

### Step 3: Hash Computation
The current value is XORed with the node value [perf_takehome.py:150](), followed by a call to `build_hash` [perf_takehome.py:77-86](), which generates the multi-stage hash operations defined by `HASH_STAGES` [problem.py:439-446]().

### Step 4: Compute Next Index
Implements the logic: `idx = 2*idx + (1 if val % 2 == 0 else 2)` [perf_takehome.py:154-158]().
1. **ALU**: `tmp1 = val % 2`
2. **ALU**: `tmp1 = (tmp1 == 0)`
3. **FLOW**: `select` instruction to choose between `one_const` and `two_const`.
4. **ALU**: `idx = idx * 2 + selected_offset`.

### Step 5: Wrap Around and Store
The kernel checks if the index exceeds `n_nodes` and wraps to 0 if necessary [perf_takehome.py:161-162](). Finally, it stores the updated `idx` and `val` back to memory [perf_takehome.py:165-169]().

**Sources:** [perf_takehome.py:77-86](), [perf_takehome.py:134-170](), [problem.py:439-446](), [problem.py:549-565]()

## Instruction Building and VLIW Packing

After generating the `body[]` list of slots, the method packs them into instruction bundles:

[perf_takehome.py:171-172]()

The `build` method [perf_takehome.py:51-56]() currently uses a trivial packing strategy:

```python
def build(self, slots: list[tuple[Engine, tuple]], vliw: bool = False):
    instrs = []
    for engine, slot in slots:
        instrs.append({engine: [slot]})
    return instrs
```

This strategy puts only **one slot per bundle**, resulting in one cycle per operation. This is the primary bottleneck. The `Machine` architecture supports multiple slots per cycle (e.g., 12 ALU slots, 2 LOAD slots) [problem.py:48-55]().

**Sources:** [perf_takehome.py:51-56](), [perf_takehome.py:171-172](), [problem.py:48-55]()

## Relationship to Reference Implementation

The `build_kernel` method directly mirrors the structure of `reference_kernel2` [problem.py:535-569]():

```mermaid
flowchart LR
    subgraph "reference_kernel2 (problem.py)"
        RK_Header["Load header values"]
        RK_Yield1["yield mem"]
        RK_Loop["for round in range(rounds):<br/>  for i in range(batch_size):"]
        RK_Body["    Update idx and val"]
        RK_Yield2["yield mem"]
    end
    
    subgraph "build_kernel (perf_takehome.py)"
        BK_Header["Generate load instructions"]
        BK_Pause1["Add pause instruction"]
        BK_Loop["for round in range(rounds):<br/>  for i in range(batch_size):"]
        BK_Body["    Generate instruction slots"]
        BK_Pause2["Add pause instruction"]
    end
    
    RK_Header -.->|"mirrors"| BK_Header
    RK_Yield1 -.->|"corresponds"| BK_Pause1
    RK_Loop -.->|"mirrors"| BK_Loop
    RK_Body -.->|"generates code for"| BK_Body
    RK_Yield2 -.->|"corresponds"| BK_Pause2
```

**Diagram: Correspondence Between Reference and Generated Code**

**Sources:** [perf_takehome.py:88-175](), [problem.py:535-569]()

## Current Implementation Characteristics

| Characteristic | Description | Performance Impact |
|----------------|-------------|-------------------|
| **Scalar-only** | Uses only scalar engines (ALU, LOAD, etc.) | Does not utilize VLEN=16 vector engine |
| **Fully unrolled** | Loops are unrolled during kernel generation | No branch overhead, but high instruction count |
| **No VLIW packing** | One operation per cycle | Underutilizes available engine slots |
| **Naive scratch** | Linear allocation without reuse | High scratch space consumption |

These characteristics result in the BASELINE cycle count of 147,734 cycles [perf_takehome.py:176]().

**Sources:** [perf_takehome.py:88-176]()

---

# Page: Helper Methods and Utilities

# Helper Methods and Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perf_takehome.py](perf_takehome.py)

</details>



This page documents the helper methods and utility functions in the `KernelBuilder` class that support instruction generation. These methods handle memory allocation, constant management, instruction building, and hash computation generation. For the overall structure and responsibilities of `KernelBuilder`, see [5.1](). For the main optimization target, see [5.2]().

## Overview of Helper Methods

The `KernelBuilder` class provides several helper methods that abstract common instruction generation patterns. These utilities handle scratch space management, constant value caching, VLIW bundle construction, and specialized instruction sequences like hash computation.

**Key helper methods:**
- **Memory management**: `alloc_scratch()`, `scratch_const()`
- **Instruction generation**: `add()`, `build()`, `build_hash()`
- **Debug support**: `debug_info()`

Sources: [perf_takehome.py:40-86]()

## State Variables

The `KernelBuilder` maintains several internal state variables that track resource allocation during instruction generation:

| Variable | Type | Purpose | Initialized |
|----------|------|---------|-------------|
| `self.instrs` | `list` | Accumulator for generated instructions | `[]` |
| `self.scratch` | `dict[str, int]` | Maps variable names to scratch addresses | `{}` |
| `self.scratch_debug` | `dict[int, tuple]` | Maps addresses to (name, length) for debugging | `{}` |
| `self.scratch_ptr` | `int` | Current allocation pointer in scratch space | `0` |
| `self.const_map` | `dict[int, int]` | Maps constant values to their scratch addresses (cache) | `{}` |

These variables work together to manage scratch space allocation and prevent conflicts:

```mermaid
graph LR
    alloc["alloc_scratch()"]
    scratch_ptr["self.scratch_ptr"]
    scratch["self.scratch"]
    scratch_debug["self.scratch_debug"]
    const_map["self.const_map"]
    
    alloc -->|increments| scratch_ptr
    alloc -->|populates| scratch
    alloc -->|populates| scratch_debug
    alloc -->|returns| addr["address"]
    
    scratch_const["scratch_const()"]
    scratch_const -->|checks| const_map
    scratch_const -->|calls if new| alloc
    scratch_const -->|updates| const_map
```

Sources: [perf_takehome.py:41-46]()

## Scratch Space Allocation

### `alloc_scratch(name=None, length=1)`

Allocates a contiguous region of scratch space and returns its starting address.

**Parameters:**
- `name` (str, optional): Variable name for debugging and reference via `self.scratch[name]`
- `length` (int, default=1): Number of consecutive words to allocate

**Returns:** `int` - The starting address of the allocated region

**Behavior:**
1. Captures current `self.scratch_ptr` as the allocation address [perf_takehome.py:62]().
2. If `name` is provided, stores mapping in `self.scratch[name]` and `self.scratch_debug[addr]` [perf_takehome.py:63-65]().
3. Advances `self.scratch_ptr` by `length` [perf_takehome.py:66]().
4. Asserts that total allocation doesn't exceed `SCRATCH_SIZE` (1536 words per core) [perf_takehome.py:67]().

**Example usage from build_kernel:**

```python
tmp1 = self.alloc_scratch("tmp1")                    # Allocate 1 word for tmp1
init_vars = ["rounds", "n_nodes", "batch_size", ...]
for v in init_vars:
    self.alloc_scratch(v, 1)                         # Named allocation
```

**Key constraint:** Scratch space is limited to 1536 words per core. The assertion at [perf_takehome.py:67]() catches over-allocation errors immediately.

Sources: [perf_takehome.py:61-68](), [perf_takehome.py:95-109]()

### Scratch Allocation Flow

```mermaid
sequenceDiagram
    participant BK as "build_kernel()"
    participant AS as "alloc_scratch()"
    participant State as "State Variables"
    
    BK->>AS: alloc_scratch("tmp1")
    AS->>State: addr = self.scratch_ptr (e.g., 0)
    AS->>State: self.scratch["tmp1"] = 0
    AS->>State: self.scratch_debug[0] = ("tmp1", 1)
    AS->>State: self.scratch_ptr += 1
    AS->>State: assert scratch_ptr <= 1536
    AS-->>BK: return 0
    
    BK->>AS: alloc_scratch("buffer", 16)
    AS->>State: addr = self.scratch_ptr (e.g., 1)
    AS->>State: self.scratch["buffer"] = 1
    AS->>State: self.scratch_debug[1] = ("buffer", 16)
    AS->>State: self.scratch_ptr += 16
    AS-->>BK: return 1
```

Sources: [perf_takehome.py:61-68](), [perf_takehome.py:95-109]()

## Constant Value Management

### `scratch_const(val, name=None)`

Allocates scratch space for a constant value, loading it with a `const` instruction. Implements caching to avoid duplicate allocations for the same constant value.

**Parameters:**
- `val` (int): The constant value to load
- `name` (str, optional): Variable name for debugging

**Returns:** `int` - Scratch address containing the constant value

**Behavior:**
1. Checks if `val` already exists in `self.const_map` [perf_takehome.py:71]().
2. If not cached:
   - Allocates scratch space via `alloc_scratch(name)` [perf_takehome.py:72]().
   - Generates a `("load", ("const", addr, val))` instruction [perf_takehome.py:73]().
   - Caches the mapping in `self.const_map[val] = addr` [perf_takehome.py:74]().
3. Returns the cached address (new or existing) [perf_takehome.py:75]().

**Example usage from build_kernel:**

```python
zero_const = self.scratch_const(0)      # First call: allocates and loads
one_const = self.scratch_const(1)       # Allocates and loads
two_const = self.scratch_const(2)       # Allocates and loads

# Later in the code:
self.scratch_const(0)                   # Returns cached address, no new instruction
```

**Optimization benefit:** Eliminates redundant constant loads. For `build_kernel`, values 0, 1, 2, and all `i` values in `range(batch_size)` are reused multiple times.

Sources: [perf_takehome.py:70-75]()

### Constant Caching Mechanism

```mermaid
graph TB
    Call["scratch_const(42)"]
    Check{"val in<br/>const_map?"}
    
    Call --> Check
    
    Check -->|Yes| Return1["return<br/>const_map[42]"]
    
    Check -->|No| Alloc["alloc_scratch()"]
    Alloc --> GenInstr["add('load',<br/>('const', addr, 42))"]
    GenInstr --> Cache["const_map[42] = addr"]
    Cache --> Return2["return addr"]
    
    Return1 --> End["Address"]
    Return2 --> End
```

Sources: [perf_takehome.py:70-75]()

## Instruction Generation

### `add(engine, slot)`

Appends a single instruction bundle to `self.instrs`. The bundle contains one slot for the specified engine.

**Parameters:**
- `engine` (Engine): The execution engine (e.g., `"alu"`, `"load"`, `"store"`, `"flow"`, `"debug"`)
- `slot` (tuple): The operation specification (format depends on engine type)

**Behavior:**
Creates a dictionary with the engine as key and a single-element list containing the slot:
```python
self.instrs.append({engine: [slot]})
```

**Example usage:**
```python
self.add("load", ("const", tmp1, i))           # Load constant
self.add("alu", ("+", result, a, b))           # ALU operation
self.add("flow", ("pause",))                   # Control flow
```

**Note:** This method creates **unpacked VLIW bundles** (one operation per cycle). For optimization, consider manually building bundles with multiple slots per engine. See [5.4]() for VLIW packing strategies.

Sources: [perf_takehome.py:58-59]()

### `build(slots, vliw=False)`

Converts a list of `(engine, slot)` tuples into instruction bundles. The current implementation uses **naive packing** (one slot per bundle).

**Parameters:**
- `slots` (list[tuple[Engine, tuple]]): List of (engine, slot) pairs to pack
- `vliw` (bool, default=False): VLIW packing flag (currently unused in implementation)

**Returns:** `list[dict]` - List of instruction bundles

**Current implementation:**
```python
def build(self, slots: list[tuple[Engine, tuple]], vliw: bool = False):
    instrs = []
    for engine, slot in slots:
        instrs.append({engine: [slot]})  # One slot per bundle
    return instrs
```

**Optimization opportunity:** The `vliw` parameter suggests this method was intended to support VLIW packing. Implementing intelligent packing here (respecting `SLOT_LIMITS` and avoiding conflicts) could reduce cycle count significantly.

**Example usage from build_kernel:**
```python
body = []  # Accumulate (engine, slot) pairs
body.append(("alu", ("+", tmp_addr, base_addr, offset)))
body.append(("load", ("load", tmp_idx, tmp_addr)))
# ... more operations ...

body_instrs = self.build(body)  # Convert to instruction bundles
self.instrs.extend(body_instrs)
```

Sources: [perf_takehome.py:51-56](), [perf_takehome.py:171-172]()

## Hash Computation Generation

### `build_hash(val_hash_addr, tmp1, tmp2, round, i)`

Generates instruction slots for the `myhash` function computation, which applies multiple hash stages defined by `HASH_STAGES`.

**Parameters:**
- `val_hash_addr` (int): Scratch address containing the value to hash (input/output)
- `tmp1` (int): Scratch address for first temporary register
- `tmp2` (int): Scratch address for second temporary register
- `round` (int): Current round number (for debug tracing)
- `i` (int): Current batch index (for debug tracing)

**Returns:** `list[tuple[Engine, tuple]]` - List of (engine, slot) pairs

**Behavior:**
For each stage in `HASH_STAGES`, generates four operations:
1. **ALU operation 1:** `tmp1 = val_hash_addr op1 const(val1)` [perf_takehome.py:81]()
2. **ALU operation 2:** `tmp2 = val_hash_addr op3 const(val3)` [perf_takehome.py:82]()
3. **ALU combination:** `val_hash_addr = tmp1 op2 tmp2` [perf_takehome.py:83]()
4. **Debug checkpoint:** Compare intermediate result [perf_takehome.py:84]()

**Example generated sequence:**
```python
# For each hash stage (op1, val1, op2, op3, val3):
("alu", (">>", tmp1, val_hash_addr, const(13)))
("alu", ("^", tmp2, val_hash_addr, const(0xdead_beef)))
("alu", ("^", val_hash_addr, tmp1, tmp2))
("debug", ("compare", val_hash_addr, (round, i, "hash_stage", 0)))
# ... repeat for remaining stages
```

**Usage in build_kernel:**
```python
# After XOR with node value:
body.append(("alu", ("^", tmp_val, tmp_val, tmp_node_val)))
body.extend(self.build_hash(tmp_val, tmp1, tmp2, round, i))
```

Sources: [perf_takehome.py:77-86](), [perf_takehome.py:150-151]()

### Hash Computation Structure

```mermaid
graph TB
    Input["val_hash_addr<br/>(input value)"]
    
    subgraph "For each HASH_STAGES entry"
        Stage["Stage (op1, val1, op2, op3, val3)"]
        
        Op1["ALU: tmp1 = val op1 const(val1)"]
        Op2["ALU: tmp2 = val op3 const(val3)"]
        Combine["ALU: val = tmp1 op2 tmp2"]
        Debug["Debug: compare checkpoint"]
        
        Stage --> Op1
        Stage --> Op2
        Op1 --> Combine
        Op2 --> Combine
        Combine --> Debug
    end
    
    Input --> Stage
    Debug --> Output["val_hash_addr<br/>(hashed value)"]
```

Sources: [perf_takehome.py:77-86]()

## Debug Information

### `debug_info()`

Constructs a `DebugInfo` object containing the scratch space mapping for trace visualization.

**Returns:** `DebugInfo` - Object with `scratch_map` attribute

**Behavior:**
```python
def debug_info(self):
    return DebugInfo(scratch_map=self.scratch_debug)
```

The `DebugInfo` object is passed to the `Machine` simulator to enable named variable tracking in traces. The `scratch_map` dictionary maps scratch addresses to `(name, length)` tuples, allowing the trace viewer to display meaningful variable names instead of raw addresses.

**Example:**
```python
kb = KernelBuilder()
kb.build_kernel(...)
debug_info = kb.debug_info()  # Contains scratch_map
machine = Machine(mem, kb.instrs, debug_info, ...)
```

The trace visualization system uses this mapping to label scratch space variables in the Perfetto UI. See [7.1]() for trace generation details.

Sources: [perf_takehome.py:48-49]()

## Helper Method Interaction Pattern

The following diagram shows how helper methods are typically used together during kernel building:

```mermaid
sequenceDiagram
    participant BK as "build_kernel()"
    participant AS as "alloc_scratch()"
    participant SC as "scratch_const()"
    participant BH as "build_hash()"
    participant Add as "add()"
    participant Build as "build()"
    
    Note over BK: Setup phase
    BK->>AS: alloc_scratch("tmp1")
    AS-->>BK: addr_tmp1
    BK->>SC: scratch_const(0)
    SC->>AS: alloc_scratch()
    SC->>Add: add("load", const)
    SC-->>BK: addr_zero
    
    Note over BK: Instruction generation
    BK->>Add: add("load", ...)
    BK->>Add: add("alu", ...)
    
    Note over BK: Hash generation
    BK->>SC: scratch_const(0xdead)
    SC-->>BK: addr_const
    BK->>BH: build_hash(val, tmp1, tmp2, ...)
    BH->>SC: scratch_const(...) [multiple]
    BH-->>BK: slots_list
    
    Note over BK: Batch packing
    BK->>Build: build(slots)
    Build-->>BK: instrs
```

Sources: [perf_takehome.py:88-175]()

## Optimization Considerations

When using these helper methods, consider the following optimization opportunities:

| Helper Method | Current Limitation | Optimization Opportunity |
|---------------|-------------------|--------------------------|
| `alloc_scratch()` | Sequential allocation | Could implement scratch reuse for non-overlapping lifetimes |
| `scratch_const()` | Caches by value only | Could deduplicate arithmetically related constants |
| `add()` | One slot per bundle | Should be replaced with VLIW-aware bundling |
| `build()` | Naive unpacking | Implement intelligent slot packing respecting `SLOT_LIMITS` |
| `build_hash()` | Returns unpacked slots | Could pre-pack hash operations into efficient bundles |

**Key insight:** The current helper methods prioritize correctness and readability over performance. The main optimization work involves either:
1. Modifying these helpers to generate more efficient instruction sequences
2. Bypassing them in performance-critical sections with hand-tuned VLIW bundles

For detailed optimization strategies, see [5.4]().

Sources: [perf_takehome.py:51-86]()

## Summary Table

| Method | Purpose | Key Parameters | Returns |
|--------|---------|----------------|---------|
| `alloc_scratch(name, length)` | Allocate scratch space | `name`: optional variable name<br/>`length`: word count (default 1) | Address (int) |
| `scratch_const(val, name)` | Load constant with caching | `val`: constant value<br/>`name`: optional debug name | Address (int) |
| `add(engine, slot)` | Add single instruction | `engine`: execution engine<br/>`slot`: operation tuple | None |
| `build(slots, vliw)` | Pack slots into bundles | `slots`: list of (engine, slot)<br/>`vliw`: unused flag | Instruction list |
| `build_hash(val_hash_addr, tmp1, tmp2, round, i)` | Generate hash computation | `val_hash_addr`: value address<br/>`tmp1, tmp2`: temp registers<br/>`round, i`: debug context | Slots list |
| `debug_info()` | Export debug mapping | None | DebugInfo object |

Sources: [perf_takehome.py:48-86]()

---

# Page: Optimization Strategies and Patterns

# Optimization Strategies and Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perf_takehome.py](perf_takehome.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



## Purpose and Scope

This page documents optimization strategies and patterns for improving the performance of the `KernelBuilder.build_kernel` method [perf_takehome.py:88-90](). The goal is to reduce cycle count by exploiting the VLIW SIMD architecture's parallelism capabilities.

For details on the `KernelBuilder` class structure, see [5.1 KernelBuilder Class Overview](). For the baseline implementation details, see [5.2 The build_kernel Method](). For information on the machine architecture being optimized for, see [4 Machine Architecture]().

The baseline implementation achieves 147,734 cycles [perf_takehome.py:176](), while the best known result is 1,363 cycles (108.4x speedup). This page covers techniques to bridge that gap.

---

## VLIW Instruction Packing

The `Machine` architecture supports multiple operations per cycle through Very Large Instruction Word (VLIW) bundles [tests/frozen_problem.py:68-73](). Each engine can execute multiple slots in parallel within a single cycle, subject to `SLOT_LIMITS` [tests/frozen_problem.py:48-55]().

### Slot Limits Per Engine

| Engine | Slots Per Cycle | Purpose |
|--------|----------------|---------|
| `alu` | 12 | Scalar arithmetic operations |
| `valu` | 6 | Vector arithmetic (VLEN=8) |
| `load` | 2 | Memory → Scratch transfers |
| `store` | 2 | Scratch → Memory transfers |
| `flow` | 1 | Control flow and selections |
| `debug` | 64 | Debug/validation (ignored in submission) |

**Baseline Issue**: The default `build()` method in the take-home template creates one instruction bundle per slot [perf_takehome.py:51-56]():

```python
def build(self, slots: list[tuple[Engine, tuple]], vliw: bool = False):
    # Simple slot packing that just uses one slot per instruction bundle
    instrs = []
    for engine, slot in slots:
        instrs.append({engine: [slot]})
    return instrs
```

**Optimization Strategy**: Pack multiple operations into each instruction bundle to execute them in parallel.

### VLIW Packing Pattern

```mermaid
graph TB
    subgraph "Baseline: 5 Cycles"
        C1["Cycle 1: {alu: [op1]}"]
        C2["Cycle 2: {alu: [op2]}"]
        C3["Cycle 3: {alu: [op3]}"]
        C4["Cycle 4: {load: [op4]}"]
        C5["Cycle 5: {store: [op5]}"]
    end
    
    subgraph "Optimized: 1 Cycle"
        C["Cycle 1: {alu: [op1, op2, op3], load: [op4], store: [op5]}"]
    end
    
    C1 -.-> C
    C2 -.-> C
    C3 -.-> C
    C4 -.-> C
    C5 -.-> C
```

**Packing Algorithm**:
1. Accumulate operations that can execute in parallel (no data dependencies).
2. Group by engine type.
3. Check `SLOT_LIMITS` [tests/frozen_problem.py:48-55]() before adding to bundle.
4. Emit bundle when any engine hits its limit or a dependency forces a flush.

**Key Constraint**: Operations in the same cycle read from the core state at cycle start; writes take effect at cycle end (two-phase commit model) [tests/frozen_problem.py:71-73]().

Sources: [perf_takehome.py:51-56](), [tests/frozen_problem.py:48-55](), [tests/frozen_problem.py:64-95]()

---

## Vectorization with VALU Instructions

The architecture supports SIMD operations with `VLEN=8` [tests/frozen_problem.py:57](), allowing 8 values to be processed in a single slot.

### Vector Operation Types

```mermaid
graph LR
    subgraph "Scalar Path: 8 cycles"
        S1["alu + slot 1<br/>Process value 0"]
        S2["alu + slot 2<br/>Process value 1"]
        S3["alu + slot 3<br/>Process value 2"]
        S4["..."]
        S5["alu + slot 8<br/>Process value 7"]
    end
    
    subgraph "Vector Path: 1 cycle"
        V1["valu + slot<br/>Process values 0-7"]
    end
    
    S1 --> S2 --> S3 --> S4 --> S5
```

**Available VALU Operations**:
- `vbroadcast`: Broadcast scalar to vector [tests/frozen_problem.py:254-257]().
- Arithmetic: `+`, `-`, `*`, `//`, `^`, `&`, `|`, `<<`, `>>`, `%`, `<`, `==` [tests/frozen_problem.py:258-267]().
- `multiply_add`: Fused multiply-add for hash optimization [tests/frozen_problem.py:261-262]().
- `vselect`: Vector conditional selection [tests/frozen_problem.py:288-298]().

**Memory Operations**:
- `vload`: Load 8 contiguous words from memory [tests/frozen_problem.py:269-277]().
- `vstore`: Store 8 contiguous words to memory [tests/frozen_problem.py:279-286]().

### Vectorization Pattern for Batch Processing

The baseline processes `batch_size` items sequentially [perf_takehome.py:135]().

**Optimization**: Process 8 items at once using vector operations:
1. `vload` input indices and values in chunks of `VLEN`.
2. Perform hashing and index calculations using `valu` instructions.
3. `vstore` updated state back to memory.

**Scratch Layout for Vectors**: Allocate consecutive addresses for vector values. A vector at address `X` occupies `X` through `X + VLEN - 1`.

Sources: [tests/frozen_problem.py:57](), [tests/frozen_problem.py:254-298](), [perf_takehome.py:135]()

---

## Loop Transformations

The baseline has nested loops with a small inner body [perf_takehome.py:134-135]().

### Loop Unrolling

**Purpose**: Reduce loop overhead and enable more instruction-level parallelism.

**Pattern**: Process multiple iterations (or vector chunks) in a single loop body to fill more VLIW slots.

**Benefits**:
- Fewer `flow` control operations.
- More opportunities for VLIW packing across iterations.
- Better utilization of scratch space.

### Full Loop Unrolling

For small, fixed iteration counts like the hash function, fully unroll the logic. The `build_hash` helper [perf_takehome.py:77-86]() already iterates through `HASH_STAGES`:

```python
for hi, (op1, val1, op2, op3, val3) in enumerate(HASH_STAGES):
    slots.append(("alu", (op1, tmp1, val_hash_addr, self.scratch_const(val1))))
    # ...
```

All 6 hash stages are known at compile time, so they can be unrolled and interleaved to hide latency.

Sources: [perf_takehome.py:77-86](), [perf_takehome.py:134-170]()

---

## Memory Access Optimization

Memory operations (`load`, `store` engines) are limited to 2 slots per cycle each [tests/frozen_problem.py:51-52]().

### Memory Access Pattern

```mermaid
graph TB
    subgraph "Memory Architecture"
        MainMem["Main Memory<br/>(Flat Word Array)"]
        LoadEngine["LOAD Engine<br/>2 slots/cycle"]
        StoreEngine["STORE Engine<br/>2 slots/cycle"]
        Scratch["Scratch Space<br/>(1536 words)"]
        
        MainMem -->|"load/vload"| LoadEngine
        LoadEngine --> Scratch
        Scratch --> StoreEngine
        StoreEngine -->|"store/vstore"| MainMem
    end
    
    subgraph "ALU Execution"
        Scratch2["Scratch Space"]
        ALU["ALU/VALU Engines<br/>Scratch Access Only"]
        
        Scratch2 <--> ALU
    end
```

### Prefetching and Latency Hiding

**Problem**: The baseline loads data immediately before use [perf_takehome.py:139-143](), creating bubbles.

**Solution**: Load data for iteration `N+1` while computing iteration `N`.

### Scratch Space as Cache

**Strategy**: Keep frequently accessed values in scratch space instead of repeatedly loading from memory.

**Key Values to Cache**:
- Constants: `0`, `1`, `2` [perf_takehome.py:114-116]().
- Base Pointers: `forest_values_p`, `inp_indices_p`, `inp_values_p` [perf_takehome.py:104-106]().
- Loop invariants: `n_nodes`, `batch_size`, `rounds` [perf_takehome.py:100-103]().

### Vector Memory Operations

Use `vload` and `vstore` to transfer 8 words per slot instead of 1 [tests/frozen_problem.py:269-286](). This effectively increases memory bandwidth by 8x.

Sources: [tests/frozen_problem.py:48-55](), [perf_takehome.py:100-116](), [perf_takehome.py:138-148]()

---

## Dependency Management

The two-phase execution model means all reads happen at cycle start, all writes at cycle end [tests/frozen_problem.py:71-73]().

### Read-After-Write (RAW) Dependencies

```mermaid
graph TB
    subgraph "Cycle N"
        ReadPhase["Read Phase<br/>(Cycle Start State)"]
        WriteBuffer["Write Buffer<br/>(Internal State)"]
        ReadPhase --> WriteBuffer
    end
    
    subgraph "Cycle Boundary"
        Commit["Commit Phase<br/>(Write to Scratch/Mem)"]
    end
    
    subgraph "Cycle N+1"
        NextRead["Read Phase<br/>(New State)"]
    end
    
    WriteBuffer --> Commit
    Commit --> NextRead
```

**Rule**: If instruction A writes to address X and instruction B reads from X, they cannot be in the same cycle.

**Optimization**: Schedule independent operations (e.g., processing different batch elements) between dependent operations to fill pipeline slots.

Sources: [tests/frozen_problem.py:71-73](), [tests/frozen_problem.py:219-252]()

---

## Scratch Space Allocation Strategies

The scratch space (1536 words) [tests/frozen_problem.py:60]() serves as registers and cache.

### Allocation Methods

- `alloc_scratch(name, length)`: Reserves a block of addresses [perf_takehome.py:61-68]().
- `scratch_const(val)`: Uses `const_map` to deduplicate and reuse addresses for the same constant value [perf_takehome.py:70-75]().

### Register Reuse

**Problem**: The baseline `alloc_scratch` inside `build_kernel` is for scalars that live throughout the kernel [perf_takehome.py:95-132]().

**Solution**: For complex kernels, manually manage scratch addresses to reuse them for different variables that have non-overlapping lifetimes.

### Vector Register Alignment

VALU operations treat a block of `VLEN` addresses as a single unit. Ensure vector allocations are planned to avoid overlapping with other critical scalars.

Sources: [perf_takehome.py:61-75](), [tests/frozen_problem.py:60]()

---

## Common Optimization Patterns

### Pattern 1: Interleaved Hashing
Interleave the 6 stages of `myhash` [perf_takehome.py:77-86]() for different vector chunks. While one chunk is waiting for the result of `alu` stage 1 to commit, another chunk can be processed in `alu` stage 1.

### Pattern 2: Branchless Index Selection
Use `flow.select` [tests/frozen_problem.py:288-298]() or `valu.vselect` to handle the tree traversal logic:
```python
# idx = 2*idx + (1 if val % 2 == 0 else 2)
```
This avoids `pause` or complex control flow that breaks VLIW packing.

### Pattern 3: Address Pre-calculation
The baseline computes `inp_indices_p + i` using ALU operations in the loop [perf_takehome.py:138](). These can be pre-calculated or incremented to save ALU slots for hashing.

Sources: [perf_takehome.py:77-86](), [perf_takehome.py:138-163](), [tests/frozen_problem.py:288-298]()

---

# Page: Testing Framework

# Testing Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/submission_tests.py](tests/submission_tests.py)

</details>



This document describes the testing infrastructure that validates the correctness and measures the performance of kernels generated by `KernelBuilder`. The testing framework is implemented in [tests/submission_tests.py]() and uses the frozen simulator and reference implementations from [frozen_problem.py](). For information about the `KernelBuilder` class itself, see [Kernel Builder - The Optimization Target](#5). For details about the simulator architecture, see [Machine Architecture](#4).

## Test Suite Structure

The testing framework consists of two main test classes that serve different purposes: correctness validation and performance benchmarking. It utilizes a central execution function and caching mechanisms to ensure efficiency and reliability. For details, see [Test Suite Structure](#6.1).

### Test Class Hierarchy

```mermaid
graph TB
    TestSuite["submission_tests.py"]
    
    subgraph "Test_Classes"
        CorrectnessTests["CorrectnessTests<br/>unittest.TestCase"]
        SpeedTests["SpeedTests<br/>unittest.TestCase"]
    end
    
    subgraph "Core_Functions"
        DoKernelTest["do_kernel_test()<br/>forest_height, rounds, batch_size"]
        KernelBuilderCache["kernel_builder()<br/>@lru_cache"]
        Cycles["cycles()<br/>@lru_cache"]
    end
    
    subgraph "External_Dependencies"
        FrozenMachine["Machine<br/>frozen_problem.py"]
        RefKernel2["reference_kernel2()<br/>frozen_problem.py"]
        KBuild["KernelBuilder<br/>perf_takehome.py"]
        TreeInput["Tree, Input<br/>frozen_problem.py"]
    end
    
    TestSuite --> CorrectnessTests
    TestSuite --> SpeedTests
    
    CorrectnessTests --> DoKernelTest
    SpeedTests --> Cycles
    Cycles --> DoKernelTest
    
    DoKernelTest --> KernelBuilderCache
    DoKernelTest --> TreeInput
    DoKernelTest --> FrozenMachine
    DoKernelTest --> RefKernel2
    
    KernelBuilderCache --> KBuild
```

**Sources:** [tests/submission_tests.py:57-116]()

### Test Parameters and Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `BASELINE` | 147,734 | Unoptimized baseline cycle count for performance comparison |
| Default `forest_height` | 10 | Tree height (2^11 - 1 = 2047 nodes) |
| Default `rounds` | 16 | Number of traversal rounds |
| Default `batch_size` | 256 | Number of parallel traversals |

**Sources:** [tests/submission_tests.py:63](), [tests/submission_tests.py:30-34]()

## Correctness Validation

The `do_kernel_test` function is the central mechanism that generates test data, builds the kernel, executes it on the simulator, and validates correctness against a reference. It compares the final state of output values in the simulator memory against the result of `reference_kernel2`. For details, see [Correctness Validation](#6.2).

### Validation Process

```mermaid
graph LR
    subgraph "Execution_Paths"
        MachineExec["Machine.run()<br/>Generated Instructions"]
        RefExec["reference_kernel2()<br/>Python Reference"]
    end
    
    subgraph "Memory_State"
        MachineMem["machine.mem<br/>Post-execution"]
        RefMem["ref_mem<br/>Expected result"]
    end
    
    subgraph "Comparison_Logic"
        Extract["Extract inp_values_p offset"]
        Compare["Compare arrays<br/>machine.mem[p:p+n]<br/>vs ref_mem[p:p+n]"]
    end
    
    MachineExec --> MachineMem
    RefExec --> RefMem
    
    MachineMem --> Extract
    RefMem --> Extract
    
    Extract --> Compare
    
    Compare -->|Match| Pass["✓ Test Passes"]
    Compare -->|Mismatch| Fail["✗ AssertionError:<br/>'Incorrect output values'"]
```

**Sources:** [tests/submission_tests.py:45-52]()

## Performance Measurement

The framework documents a performance ladder ranging from the unoptimized baseline (147,734 cycles) to highly optimized AI-generated targets. Performance is measured by the `cycle` attribute of the `Machine` after execution. Caching via `@lru_cache` ensures that the kernel is only built and measured once per test session. For details, see [Performance Measurement](#6.3).

### Performance Benchmark Ladder

| Test Method | Cycle Threshold | Description |
|-------------|-----------------|-------------|
| `test_kernel_speedup` | < 147,734 | Any improvement over baseline |
| `test_kernel_updated_starting_point` | < 18,532 | Performance of updated starter code |
| `test_opus4_many_hours` | < 2,164 | Claude Opus 4 (extended compute) |
| `test_opus45_casual` | < 1,790 | Claude Opus 4.5 casual (~best human 2hr) |
| `test_opus45_2hr` | < 1,579 | Claude Opus 4.5 (2hr harness) |
| `test_sonnet45_many_hours` | < 1,548 | Claude Sonnet 4.5 (extended compute) |
| `test_opus45_11hr` | < 1,487 | Claude Opus 4.5 (11.5hr) - Recruitment gate |
| `test_opus45_improved_harness` | < 1,363 | Claude Opus 4.5 (improved harness) |

**Sources:** [tests/submission_tests.py:85-115]()

## Running and Interpreting Tests

Tests are executed using `unittest`. Users can run the entire suite to see speedup over the baseline and verify that logic changes haven't broken the kernel. Output includes cycle counts and speedup calculations. For a practical guide on running tests and debugging failures, see [Running and Interpreting Tests](#6.4).

### Implementation Details

1. **Test Data Generation** [tests/submission_tests.py:33-35](): Creates random `Tree` and `Input` objects.
2. **Memory Image Construction** [tests/submission_tests.py:35](): Uses `build_mem_image()` to create a flat memory layout.
3. **Kernel Building** [tests/submission_tests.py:37](): Invokes the cached `kernel_builder()` function.
4. **Machine Configuration** [tests/submission_tests.py:40-42](): Creates `Machine` instance with memory and instructions.
5. **Execution** [tests/submission_tests.py:43](): Runs `machine.run()` to execute instructions and count cycles.
6. **Validation** [tests/submission_tests.py:48-52](): Compares the output values array in `machine.mem` with `ref_mem` at offset `inp_values_p`.

**Sources:** [tests/submission_tests.py:30-54]()

---

# Page: Test Suite Structure

# Test Suite Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/submission_tests.py](tests/submission_tests.py)

</details>



This page documents the organization and structure of the testing infrastructure used to validate correctness and measure performance of kernel implementations. It covers the test file organization, the test class hierarchy, and the core testing function `do_kernel_test`.

## Test File Organization

The repository contains two distinct test locations with different purposes and execution contexts:

### Development Tests: perf_takehome.py
The `Tests` class in `perf_takehome.py` [perf_takehome.py:225-256]() provides lightweight tests for development iteration. These tests use the simulator from `problem.py`, which allows for debugging features like pause points and trace generation.

**Key characteristics:**
- Uses `Machine` from `problem.py`.
- Enables `trace=True` and `prints=True` options in `do_kernel_test` [perf_takehome.py:175-182]().
- Contains `test_kernel_trace()` for generating execution traces [perf_takehome.py:241-243]().
- Validates against `reference_kernel2` at each pause point [perf_takehome.py:207-217]().
- Seeds random generator with `seed=123` for reproducibility [perf_takehome.py:183]().

### Submission Tests: tests/submission_tests.py
The `CorrectnessTests` and `SpeedTests` classes in `tests/submission_tests.py` [tests/submission_tests.py:57-116]() provide the official validation suite. These tests use the "frozen" simulator from `frozen_problem.py` to ensure fair performance comparison.

**Key characteristics:**
- Uses `Machine` from `frozen_problem.py` [tests/submission_tests.py:11-19]().
- Disables pause and debug features: `machine.enable_pause = False`, `machine.enable_debug = False` [tests/submission_tests.py:41-42]().
- Does not seed the random generator (tests must work for any random input) [tests/submission_tests.py:32]().
- Uses `@lru_cache` decorator to cache kernel builds [tests/submission_tests.py:23-27]().
- Implements the performance ladder with specific cycle thresholds [tests/submission_tests.py:85-115]().

```mermaid
graph TB
    subgraph DevTests["Development Tests (perf_takehome.py)"]
        TestsClass["Tests(unittest.TestCase)"]
        TestsClass --> TestRefKernels["test_ref_kernels()"]
        TestsClass --> TestTrace["test_kernel_trace()"]
        TestsClass --> TestCycles["test_kernel_cycles()"]
    end
    
    subgraph SubTests["Submission Tests (tests/submission_tests.py)"]
        CorrectnessTests["CorrectnessTests(unittest.TestCase)"]
        SpeedTests["SpeedTests(unittest.TestCase)"]
        
        CorrectnessTests --> TestCorrectness["test_kernel_correctness()"]
        SpeedTests --> TestSpeedup["test_kernel_speedup()"]
        SpeedTests --> TestOpus4["test_opus4_many_hours()"]
        SpeedTests --> TestOpus45Improved["test_opus45_improved_harness()"]
    end
    
    DoKernelTestDev["do_kernel_test()<br/>(perf_takehome.py)"]
    DoKernelTestSub["do_kernel_test()<br/>(submission_tests.py)"]
    
    TestTrace --> DoKernelTestDev
    TestCorrectness --> DoKernelTestSub
    SpeedTests --> CyclesFunc["cycles()"]
    CyclesFunc --> DoKernelTestSub
    
    DoKernelTestDev -.->|"uses"| ProblemPy["problem.py"]
    DoKernelTestSub -.->|"uses"| FrozenProblemPy["frozen_problem.py"]
```
**Diagram: Test File Structure and Class Hierarchy**

Sources: [perf_takehome.py:225-256](), [tests/submission_tests.py:1-119]()

## Core Test Function: do_kernel_test

Both test files implement a `do_kernel_test` function that serves as the core test execution engine. While the implementations differ slightly, they follow the same fundamental pattern of generating data, building the kernel, running the machine, and validating memory.

### Function Signature and Parameters

**Submission version** [tests/submission_tests.py:30]():
`do_kernel_test(forest_height: int, rounds: int, batch_size: int)`

| Parameter | Type | Purpose |
|-----------|------|---------|
| `forest_height` | `int` | Height of the binary tree (determines tree size: 2^(h+1)-1 nodes) |
| `rounds` | `int` | Number of rounds to execute the kernel |
| `batch_size` | `int` | Number of parallel computations per round |

### Execution Flow

```mermaid
sequenceDiagram
    participant Test as "do_kernel_test()"
    participant Tree as "Tree.generate()"
    participant Input as "Input.generate()"
    participant KB as "kernel_builder()"
    participant Mem as "build_mem_image()"
    participant Machine as "Machine"
    participant Ref as "reference_kernel2()"
    
    Test->>Tree: "Generate Tree"
    Test->>Input: "Generate Input"
    
    Test->>Mem: "build_mem_image(forest, inp)"
    Mem-->>Test: "mem (flat memory array)"
    
    Test->>KB: "Get cached/new KernelBuilder"
    KB-->>Test: "kb.instrs"
    
    Test->>Machine: "Machine(mem, kb.instrs, kb.debug_info(), n_cores)"
    
    Test->>Machine: "machine.run() (full execution)"
    Machine-->>Test: "final state"
    
    Test->>Ref: "Consume reference_kernel2 generator"
    Ref-->>Test: "ref_mem"
    
    Test->>Test: "Compare machine.mem with ref_mem"
    Test->>Test: "Return machine.cycle"
```
**Diagram: do_kernel_test Execution Flow (Submission)**

Sources: [tests/submission_tests.py:30-54](), [perf_takehome.py:175-222]()

### Key Differences Between Versions

| Aspect | Development (perf_takehome.py) | Submission (submission_tests.py) |
|--------|--------------------------------|----------------------------------|
| Simulator | `problem.py` (mutable) | `frozen_problem.py` (frozen) |
| Random Seed | Fixed (`seed=123`) | Not seeded (random) |
| Pause Points | Validated at each `pause` | Disabled (`enable_pause = False`) |
| Debug Info | Included | Included via `kb.debug_info()` |
| Trace Generation | Optional (`trace=True`) | Not available |
| Validation | Incremental (at each pause) | Final state only |

Sources: [perf_takehome.py:175-222](), [tests/submission_tests.py:30-54]()

## Test Class Structure

### CorrectnessTests Class
The `CorrectnessTests` class [tests/submission_tests.py:57-61]() validates functional correctness by running multiple randomized test cases. It executes 8 iterations with different random seeds (no seed specified) using standard benchmark parameters: `forest_height=10, rounds=16, batch_size=256`.

### SpeedTests Class
The `SpeedTests` class [tests/submission_tests.py:76-116]() implements the performance ladder with progressively aggressive cycle count thresholds.

**Performance Thresholds:**

| Test Method | Threshold (cycles) | Description |
|-------------|-------------------|-------------|
| `test_kernel_speedup()` | 147734 | `BASELINE` - any improvement [tests/submission_tests.py:86]() |
| `test_kernel_updated_starting_point()` | 18532 | Updated starter code performance [tests/submission_tests.py:90]() |
| `test_opus4_many_hours()` | 2164 | Claude Opus 4 after many hours [tests/submission_tests.py:94]() |
| `test_opus45_casual()` | 1790 | Claude Opus 4.5 casual session [tests/submission_tests.py:99]() |
| `test_opus45_2hr()` | 1579 | Claude Opus 4.5 after 2 hours [tests/submission_tests.py:103]() |
| `test_sonnet45_many_hours()` | 1548 | Claude Sonnet 4.5 after many hours [tests/submission_tests.py:107]() |
| `test_opus45_11hr()` | 1487 | Claude Opus 4.5 after 11.5 hours [tests/submission_tests.py:111]() |
| `test_opus45_improved_harness()` | 1363 | Claude Opus 4.5 improved harness [tests/submission_tests.py:115]() |

Sources: [tests/submission_tests.py:76-116]()

## Caching Strategy

The submission test suite employs two levels of caching to improve test execution performance.

### Kernel Builder Cache
The `kernel_builder` function [tests/submission_tests.py:23-27]() is decorated with `@lru_cache(maxsize=None)` to cache compiled kernels. It ensures that `kb.build_kernel` is only called once for a specific set of parameters, regardless of how many tests require it.

### Cycle Count Cache
The `cycles` function [tests/submission_tests.py:66-73]() is also decorated with `@lru_cache(maxsize=None)`. This ensures that the actual `Machine` simulation is performed only once per test run. All `SpeedTests` methods call `cycles()` instead of `do_kernel_test` directly. If a correctness assertion fails, it returns `BASELINE * 2` [tests/submission_tests.py:73]().

```mermaid
graph LR
    SpeedTests["SpeedTests"] --> CyclesFunc["cycles()<br/>@lru_cache"]
    CyclesFunc --> DoTest["do_kernel_test()"]
    DoTest --> KernelBuilderFunc["kernel_builder()<br/>@lru_cache"]
    KernelBuilderFunc --> Build["kb.build_kernel()"]
```
**Diagram: Two-Level Caching Strategy**

Sources: [tests/submission_tests.py:23-27](), [tests/submission_tests.py:66-73]()

## Test Parameters

All submission tests use identical benchmark parameters to ensure consistent performance measurement:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `forest_height` | 10 | `n_nodes = 2^11 - 1 = 2047` |
| `rounds` | 16 | Number of complete traversal rounds |
| `batch_size` | 256 | Number of parallel tree traversals |
| `BASELINE` | 147734 | Original unoptimized cycle count [tests/submission_tests.py:63]() |

The `do_kernel_test` function uses these to instantiate `Tree` and `Input` [tests/submission_tests.py:33-34](), build the memory image [tests/submission_tests.py:35](), and initialize the `Machine` with `N_CORES` [tests/submission_tests.py:40]().

Sources: [tests/submission_tests.py:30-54](), [tests/submission_tests.py:63]()

---

# Page: Correctness Validation

# Correctness Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/frozen_problem.py](tests/frozen_problem.py)
- [tests/submission_tests.py](tests/submission_tests.py)

</details>



This page explains how the testing framework validates that generated kernels produce functionally correct results. For information about performance measurement and cycle counting, see [6.3 Performance Measurement](). For the overall test suite structure, see [6.1 Test Suite Structure]().

## Purpose and Scope

Correctness validation ensures that the instructions generated by `KernelBuilder.build_kernel` [perf_takehome.py:53-54]() produce the same output as the reference implementation. The system uses a **reference implementation strategy** where a ground-truth Python implementation runs on the same flat memory layout and produces expected results for comparison. This approach validates that optimizations in the generated kernel preserve functional correctness regardless of how instructions are reordered, vectorized, or parallelized.

## Validation Strategy Overview

```mermaid
graph TB
    subgraph "Test Execution"
        Test["do_kernel_test()"]
        Test --> GenData["Generate Random:<br/>Tree.generate()<br/>Input.generate()"]
        GenData --> BuildMem["build_mem_image()"]
        BuildMem --> Memory["Flat Memory Image"]
    end
    
    subgraph "Parallel Execution"
        Memory --> MachineExec["Machine Execution"]
        Memory --> RefExec["Reference Execution"]
        
        KB["KernelBuilder.build_kernel()"]
        KB --> Instructions["Generated Instructions"]
        Instructions --> MachineExec
        
        RefKernel["reference_kernel2(mem)"]
        RefExec --> RefKernel
        
        MachineExec --> MachineResult["Machine.mem"]
        RefKernel --> RefResult["ref_mem from generator"]
    end
    
    subgraph "Validation"
        MachineResult --> Compare["Memory Comparison"]
        RefResult --> Compare
        Compare --> Extract["Extract inp_values array"]
        Extract --> Assert["assert machine.mem == ref_mem"]
        Assert --> Pass["✓ Correctness Validated"]
        Assert --> Fail["✗ Assertion Error"]
    end
    
    style RefKernel fill:#e8f5e9
    style Compare fill:#fff3e0
    style Assert fill:#fce4ec
```

**Sources:** [tests/submission_tests.py:30-54](), [tests/frozen_problem.py:535-568]()

The validation strategy follows these principles:

1. **Same Memory Layout**: Both the Machine simulator and reference implementation operate on the same flat memory image format produced by `build_mem_image` [tests/frozen_problem.py:469-487]().
2. **Generator Pattern**: `reference_kernel2` is a generator function that yields memory states at validation checkpoints [tests/frozen_problem.py:535-568]().
3. **Output Comparison**: Tests compare specific memory regions (the `inp_values` array) rather than instruction-by-instruction execution [tests/submission_tests.py:48-52]().
4. **Random Testing**: Correctness tests run multiple iterations with different random data to catch edge cases [tests/submission_tests.py:58-60]().

## Reference Implementation: reference_kernel2

The `reference_kernel2` function in [tests/frozen_problem.py:535-568]() is the ground truth implementation that defines correct behavior:

```mermaid
graph LR
    subgraph "reference_kernel2 Execution"
        Start["reference_kernel2(mem, trace)"]
        Start --> ReadHeader["Read Header:<br/>rounds, n_nodes, batch_size<br/>forest_values_p, inp_indices_p, inp_values_p"]
        ReadHeader --> YieldInit["yield mem<br/>(initial state)"]
        
        YieldInit --> OuterLoop["for h in range(rounds)"]
        OuterLoop --> InnerLoop["for i in range(batch_size)"]
        
        InnerLoop --> ReadIdx["idx = mem[inp_indices_p + i]"]
        ReadIdx --> ReadVal["val = mem[inp_values_p + i]"]
        ReadVal --> ReadNode["node_val = mem[forest_values_p + idx]"]
        ReadNode --> Hash["val = myhash_traced(val ^ node_val)"]
        Hash --> NextIdx["idx = 2 * idx + (1 if val % 2 == 0 else 2)"]
        NextIdx --> Wrap["idx = 0 if idx >= n_nodes else idx"]
        Wrap --> WriteBack["mem[inp_values_p + i] = val<br/>mem[inp_indices_p + i] = idx"]
        
        WriteBack --> InnerLoop
        InnerLoop --> OuterLoop
        OuterLoop --> YieldFinal["yield mem<br/>(final state)"]
    end
    
    subgraph "Optional Trace"
        Hash -.-> TraceValues["trace[(h, i, 'idx')] = idx<br/>trace[(h, i, 'val')] = val<br/>trace[(h, i, 'node_val')] = node_val<br/>..."]
    end
```

**Sources:** [tests/frozen_problem.py:535-568](), [tests/frozen_problem.py:516-532]()

### Memory Layout Dependencies

The reference implementation reads the memory layout convention from the header [tests/frozen_problem.py:539-547]():

| Offset | Field | Description |
|--------|-------|-------------|
| `mem[0]` | `rounds` | Number of traversal rounds |
| `mem[1]` | `n_nodes` | Total tree nodes |
| `mem[2]` | `batch_size` | Number of parallel traversals |
| `mem[3]` | `forest_height` | Tree height |
| `mem[4]` | `forest_values_p` | Pointer to tree values array |
| `mem[5]` | `inp_indices_p` | Pointer to input indices array |
| `mem[6]` | `inp_values_p` | Pointer to input values array |

The reference implementation directly indexes into these arrays: `mem[forest_values_p + idx]`, `mem[inp_indices_p + i]`, `mem[inp_values_p + i]`. This ensures it operates on the same data layout as the Machine simulator.

**Sources:** [tests/frozen_problem.py:539-547]()

### Trace Dictionary Mechanism

The optional `trace` dictionary parameter enables fine-grained debugging by recording intermediate values:

```mermaid
graph TB
    subgraph "Trace Keys Format"
        Key["(round, batch_i, key_name)"]
        Key --> Examples["Examples:<br/>(h, i, 'idx')<br/>(h, i, 'val')<br/>(h, i, 'node_val')<br/>(h, i, 'hashed_val')<br/>(h, i, 'next_idx')<br/>(h, i, 'wrapped_idx')"]
    end
    
    subgraph "Hash Stage Tracing"
        HashKey["(round, batch_i, 'hash_stage', stage_num)"]
        HashKey --> HashVals["Traces each of 6<br/>hash mixing stages"]
    end
    
    subgraph "Usage in Machine"
        Machine["Machine(value_trace=trace)"]
        Machine --> DebugInstr["debug engine:<br/>('compare', loc, key)<br/>('vcompare', loc, keys)"]
        DebugInstr --> Assert["assert core.scratch[loc] == trace[key]"]
    end
```

**Sources:** [tests/frozen_problem.py:516-532](), [tests/frozen_problem.py:551-562](), [tests/frozen_problem.py:366-381]()

The trace dictionary maps tuple keys `(round, batch_i, variable_name)` to expected values. This enables:
- **Debugging individual operations**: Check if specific intermediate calculations match reference [tests/frozen_problem.py:551-562]().
- **Hash stage validation**: The `myhash_traced` function records output after each of 6 mixing stages [tests/frozen_problem.py:528-530]().
- **Debug instructions**: The Machine's debug engine can insert `compare` instructions to validate scratch space values against the trace [tests/frozen_problem.py:370-381]().

### Generator Yield Points

The `reference_kernel2` function yields memory states at specific checkpoints:

1. **Initial state** [tests/frozen_problem.py:548](): `yield mem` after reading header but before computation.
2. **Final state** [tests/frozen_problem.py:568](): `yield mem` after all rounds complete.

The comment at [tests/frozen_problem.py:565-567]() notes: "You can add new yields or move this around for debugging as long as it's matched by pause instructions." This allows intermediate validation points where the Machine uses `pause` instructions to synchronize with reference yields.

**Sources:** [tests/frozen_problem.py:548](), [tests/frozen_problem.py:565-568]()

## Validation Flow in Tests

```mermaid
sequenceDiagram
    participant Test as do_kernel_test()
    participant Gen as Tree/Input.generate()
    participant Builder as kernel_builder()
    participant Machine as Machine.run()
    participant Ref as reference_kernel2()
    
    Test->>Gen: Generate random data
    Gen-->>Test: Tree, Input
    
    Test->>Test: build_mem_image(Tree, Input)
    Note over Test: Create flat memory layout
    
    Test->>Builder: kernel_builder(height, nodes, batch, rounds)
    Note over Builder: Cached via @lru_cache
    Builder-->>Test: KernelBuilder with instructions
    
    Test->>Machine: Machine(mem, kb.instrs, kb.debug_info())
    Test->>Machine: machine.enable_pause = False
    Test->>Machine: machine.enable_debug = False
    Test->>Machine: machine.run()
    Note over Machine: Execute generated kernel
    Machine-->>Test: machine.cycle, machine.mem
    
    Test->>Ref: for ref_mem in reference_kernel2(mem)
    Note over Ref: Generator yields states
    Ref-->>Test: Final ref_mem
    
    Test->>Test: Extract inp_values_p from ref_mem[6]
    Test->>Test: Compare arrays:<br/>machine.mem[inp_values_p:inp_values_p+len]<br/>== ref_mem[inp_values_p:inp_values_p+len]
    
    alt Memory matches
        Test-->>Test: ✓ Correctness validated
    else Memory mismatch
        Test-->>Test: ✗ AssertionError: "Incorrect output values"
    end
```

**Sources:** [tests/submission_tests.py:30-54]()

### The do_kernel_test Function

The core validation logic resides in `do_kernel_test` [tests/submission_tests.py:30-54]():

1. **Generate random test data** [tests/submission_tests.py:33-35](): Creates a random `Tree` and `Input` (note: no seed, so each run is different).
2. **Build memory image** [tests/submission_tests.py:35](): Converts to flat memory layout using `build_mem_image` [tests/frozen_problem.py:469]().
3. **Get cached kernel builder** [tests/submission_tests.py:37](): Uses `@lru_cache` to avoid rebuilding identical kernels.
4. **Execute Machine** [tests/submission_tests.py:40-43]():
   - `machine.enable_pause = False`: Disables pause instructions for speed.
   - `machine.enable_debug = False`: Disables debug instruction validation.
5. **Iterate reference generator** [tests/submission_tests.py:45-46](): Consumes all yields to get final state.
6. **Compare output arrays** [tests/submission_tests.py:48-52](): Validates `inp_values` array matches.

### Memory Comparison Logic

The validation specifically compares the `inp_values` array:

```python
inp_values_p = ref_mem[6]  # Read pointer from header
assert (
    machine.mem[inp_values_p : inp_values_p + len(inp.values)]
    == ref_mem[inp_values_p : inp_values_p + len(inp.values)]
), "Incorrect output values"
```

**Why only inp_values?** The `inp_indices` array at `mem[5]` is also modified during execution, but the final indices depend on implementation details (e.g., order of operations). The `inp_values` array is the primary output that must match exactly. The tree values at `mem[4]` remain constant.

**Sources:** [tests/submission_tests.py:48-52]()

### Multiple Random Test Runs

The `CorrectnessTests` class runs validation multiple times with different random data:

```python
def test_kernel_correctness(self):
    for i in range(8):
        do_kernel_test(10, 16, 256)
```

This catches:
- **Edge cases**: Rare value combinations that trigger bugs.
- **Race conditions**: If the kernel has any non-determinism.
- **Memory corruption**: Writes to wrong addresses might not manifest every time.

Since `Tree.generate` and `Input.generate` use `random.randint` without seeding [tests/frozen_problem.py:417-436](), each iteration has different data.

**Sources:** [tests/submission_tests.py:57-60]()

## Pause/Resume Mechanism

The Machine simulator supports **pausing execution** for intermediate validation:

```mermaid
graph LR
    subgraph "Core State Machine"
        Running["CoreState.RUNNING"]
        Paused["CoreState.PAUSED"]
        Stopped["CoreState.STOPPED"]
        
        Running -->|"pause instruction"| Paused
        Paused -->|"machine.run()"| Running
        Running -->|"halt instruction<br/>or pc >= len(program)"| Stopped
    end
    
    subgraph "Generator Synchronization"
        Yield1["reference_kernel2:<br/>yield mem (initial)"]
        Yield2["reference_kernel2:<br/>yield mem (final)"]
        
        Pause1["Machine:<br/>pause instruction"]
        Pause2["Machine:<br/>pause instruction"]
        
        Yield1 -.->|"corresponds to"| Pause1
        Yield2 -.->|"corresponds to"| Pause2
    end
    
    subgraph "Submission Tests"
        Disable["machine.enable_pause = False"]
        Note["Pauses ignored for speed"]
    end
```

**Sources:** [tests/frozen_problem.py:18-22](), [tests/frozen_problem.py:317-319](), [tests/frozen_problem.py:199-200]()

### How Pause Instructions Work

1. **flow engine instruction** [tests/frozen_problem.py:317-319](): `("pause",)` sets `core.state = CoreState.PAUSED`.
2. **Execution stops** [tests/frozen_problem.py:201](): The run loop skips cores in PAUSED state.
3. **Resume on next run()** [tests/frozen_problem.py:199-200](): Calling `machine.run()` again resets PAUSED cores to RUNNING.

This enables:
- **Checkpoint validation**: Compare machine.mem with reference_kernel2 yields at intermediate points.
- **Debugging**: Inspect memory/scratch state mid-execution.
- **Incremental testing**: Test kernel correctness round-by-round rather than only final output.

### Why Submission Tests Disable Pauses

The submission tests set `machine.enable_pause = False` [tests/submission_tests.py:41]() because:
- **Performance**: Validation at intermediate points would require multiple Machine.run() calls.
- **Simplicity**: Final output comparison is sufficient for correctness.
- **Speed**: Tests run faster without pause/resume overhead.

Developers can enable pauses during debugging by modifying this flag or running the Machine manually with pauses enabled.

**Sources:** [tests/submission_tests.py:41-42]()

## Debug Instrumentation

Beyond basic memory comparison, the system provides **fine-grained validation** through debug instructions:

```mermaid
graph TB
    subgraph "Debug Engine Instructions"
        Compare["('compare', loc, key)"]
        VCompare["('vcompare', loc, keys)"]
    end
    
    subgraph "value_trace Dictionary"
        Trace["Machine(value_trace=trace_dict)"]
        TraceKeys["Keys:<br/>(round, batch_i, 'var_name')<br/>(round, batch_i, 'hash_stage', stage)"]
    end
    
    subgraph "Validation at Execution Time"
        Compare --> ReadScratch["res = core.scratch[loc]"]
        ReadScratch --> ReadTrace["ref = self.value_trace[key]"]
        ReadTrace --> Assert1["assert res == ref"]
        
        VCompare --> ReadVScratch["res = core.scratch[loc:loc+VLEN]"]
        ReadVScratch --> ReadVTrace["ref = [value_trace[k] for k in keys]"]
        ReadVTrace --> Assert2["assert res == ref"]
    end
    
    subgraph "Error Reporting"
        Assert1 -.-> Error["AssertionError:<br/>'X != Y for key at pc=N'"]
        Assert2 -.-> Error
    end
```

**Sources:** [tests/frozen_problem.py:366-381]()

### compare and vcompare Instructions

The debug engine [tests/frozen_problem.py:366-382]() supports two validation instructions:

1. **`("compare", loc, key)`**: Validates a scalar scratch variable [tests/frozen_problem.py:370-375]().
   - Reads `core.scratch[loc]`.
   - Looks up expected value in `self.value_trace[key]`.
   - Asserts they match with detailed error message.

2. **`("vcompare", loc, keys)`**: Validates a vector scratch variable [tests/frozen_problem.py:376-381]().
   - Reads `core.scratch[loc : loc + VLEN]` (8 consecutive words).
   - Looks up expected values for each element in `keys` list.
   - Asserts entire vector matches.

### Usage in Kernel Builder

A kernel can insert debug instructions to validate intermediate results. These instructions execute during `Machine.run()` and will raise `AssertionError` immediately if values don't match the reference trace. This catches errors closer to their source than final memory comparison.

### Disabling Debug Instructions

Submission tests disable debug validation with `machine.enable_debug = False` [tests/submission_tests.py:42]() because:
- **Performance**: Checking every intermediate value is slow.
- **Trace dependency**: Requires running reference_kernel2 with trace collection first.
- **Not needed**: Final memory comparison is sufficient for correctness validation.

Developers can enable debug instructions during development to catch errors early.

**Sources:** [tests/submission_tests.py:42](), [tests/frozen_problem.py:366-368]()

## Summary

Correctness validation in this system uses a **reference implementation strategy** where:

1. **reference_kernel2** defines ground truth behavior on the same flat memory layout [tests/frozen_problem.py:535]().
2. **Generator pattern** allows validation at multiple checkpoints (though submission tests only use final state) [tests/frozen_problem.py:548, 568]().
3. **Memory comparison** validates the `inp_values` output array matches exactly [tests/submission_tests.py:49-52]().
4. **Random testing** runs validation 8 times with different data to catch edge cases [tests/submission_tests.py:59-60]().
5. **Debug instrumentation** provides optional fine-grained validation of intermediate values [tests/frozen_problem.py:366-381]().

This approach validates functional correctness independently of performance optimizations, allowing the kernel builder to explore aggressive transformations like vectorization, reordering, and loop unrolling while maintaining confidence in correctness.

**Sources:** [tests/submission_tests.py:30-60](), [tests/frozen_problem.py:535-568](), [tests/frozen_problem.py:366-381]()

---

# Page: Performance Measurement

# Performance Measurement

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/submission_tests.py](tests/submission_tests.py)

</details>



This page documents how the testing framework measures performance in cycle counts, calculates speedup over baseline, and implements caching strategies to avoid redundant measurements. For information about test suite organization and test execution, see [Test Suite Structure](#6.1). For correctness validation mechanisms, see [Correctness Validation](#6.2).

## Overview

Performance measurement in this system is straightforward: count the number of simulated machine cycles required to execute the generated kernel. The `Machine` simulator maintains a `cycle` counter that increments after each instruction bundle executes. The testing framework compares this cycle count against a baseline and various performance thresholds to assess optimization quality.

## Cycle Counting Mechanism

The cycle counter is maintained by the `Machine` class in `frozen_problem.py`. Each time an instruction bundle executes, the cycle counter increments by one, regardless of how many operations execute in parallel within that bundle.

### Measurement Data Flow

```mermaid
sequenceDiagram
    participant Test as "do_kernel_test()"
    participant KB as "KernelBuilder"
    participant Machine as "Machine"
    participant Cycle as "machine.cycle"
    
    Test->>KB: "build_kernel(10, 2047, 256, 16)"
    KB-->>Test: "kb.instrs"
    Test->>Machine: "Machine(mem, kb.instrs, ...)"
    Test->>Machine: "machine.run()"
    
    loop "Until CoreState.PC >= len(instrs)"
        Machine->>Machine: "Execute VLIW bundle"
        Machine->>Cycle: "cycle += 1"
    end
    
    Machine-->>Test: "Execution complete"
    Test->>Cycle: "Read machine.cycle"
    Test->>Test: "Return cycle count"
```
Sources: [tests/submission_tests.py:30-54](), [frozen_problem.py:596-608]()

The measurement occurs in the `do_kernel_test` function:

| Step | Code Location | Action |
|------|---------------|--------|
| 1. Create Machine | [tests/submission_tests.py:40]() | `machine = Machine(mem, kb.instrs, kb.debug_info(), n_cores=N_CORES)` |
| 2. Configure | [tests/submission_tests.py:41-42]() | Disable pause and debug modes for performance runs |
| 3. Execute | [tests/submission_tests.py:43]() | `machine.run()` executes all instructions |
| 4. Read Counter | [tests/submission_tests.py:53]() | `return machine.cycle` provides the total cycle count |

Sources: [tests/submission_tests.py:40-54]()

## Baseline Measurement

The `BASELINE` constant represents the cycle count of the initial unoptimized implementation provided as a starting point:

```python
BASELINE = 147734
```

This baseline serves as the denominator in speedup calculations. All performance comparisons are relative to this reference point.

Sources: [tests/submission_tests.py:63]()

## Speedup Calculation

Speedup is computed as the ratio of baseline cycles to optimized cycles:

```
Speedup = BASELINE / cycles()
```

This formula yields:
- `1.0x` for implementations matching the baseline.
- `~7.97x` for the updated starting point (18,532 cycles).
- `>100x` for high-performance AI-optimized kernels.

The speedup is printed after the main test execution:

```python
print("Speedup over baseline: ", BASELINE / res)
```

Sources: [tests/submission_tests.py:70-71]()

## Performance Thresholds Hierarchy

The `SpeedTests` class defines a ladder of performance targets, ranging from the baseline to the best known performance achieved by Claude Opus 4.5.

### Threshold Association Diagram

```mermaid
graph TD
    subgraph "Natural Language Benchmarks"
        B["Baseline"]
        U["Updated Starter"]
        O4["Opus 4 Many Hours"]
        O45C["Opus 4.5 Casual"]
        O45_2h["Opus 4.5 2hr Harness"]
        S45["Sonnet 4.5 Many Hours"]
        O45_11h["Opus 4.5 11.5hr Launch"]
        O45_Best["Opus 4.5 Improved Harness"]
    end

    subgraph "Code Entity Space (SpeedTests)"
        T1["test_kernel_speedup"]
        T2["test_kernel_updated_starting_point"]
        T3["test_opus4_many_hours"]
        T4["test_opus45_casual"]
        T5["test_opus45_2hr"]
        T6["test_sonnet45_many_hours"]
        T7["test_opus45_11hr"]
        T8["test_opus45_improved_harness"]
    end

    B --- T1
    U --- T2
    O4 --- T3
    O45C --- T4
    O45_2h --- T5
    S45 --- T6
    O45_11h --- T7
    O45_Best --- T8
```
Sources: [tests/submission_tests.py:85-115]()

### Threshold Details

| Test Method | Cycle Threshold | Description |
|-------------|----------------|-------------|
| `test_kernel_speedup` | `< 147734` | Beat the original baseline. |
| `test_kernel_updated_starting_point` | `< 18532` | Beat the updated starter code given to candidates. |
| `test_opus4_many_hours` | `< 2164` | Claude Opus 4 after extended compute. |
| `test_opus45_casual` | `< 1790` | Claude Opus 4.5 in a casual session (~best human 2hr). |
| `test_opus45_2hr` | `< 1579` | Claude Opus 4.5 after 2 hours in a compute harness. |
| `test_sonnet45_many_hours` | `< 1548` | Claude Sonnet 4.5 after extended compute. |
| `test_opus45_11hr` | `< 1487` | Claude Opus 4.5 after 11.5 hours; the recruitment gate. |
| `test_opus45_improved_harness` | `< 1363` | Claude Opus 4.5 in an improved test-time compute harness. |

Sources: [tests/submission_tests.py:76-116]()

## Caching Strategy

The testing framework implements a two-level caching strategy using `functools.lru_cache` to ensure that expensive operations—kernel generation and machine execution—are only performed once per test run.

```mermaid
graph TB
    subgraph "Test Suite"
        T1["test_kernel_speedup"]
        T2["test_kernel_updated_starting_point"]
        T3["..."]
    end

    subgraph "Caching Layer"
        CacheC["cycles() @lru_cache"]
        CacheK["kernel_builder() @lru_cache"]
    end

    subgraph "Execution"
        KB["KernelBuilder.build_kernel()"]
        M["Machine.run()"]
    end

    T1 --> CacheC
    T2 --> CacheC
    T3 --> CacheC
    
    CacheC -->|"First Call"| M
    M -.-> CacheK
    CacheK -->|"First Call"| KB
```
Sources: [tests/submission_tests.py:23-28](), [tests/submission_tests.py:66-74]()

### Implementation Details

1.  **`kernel_builder()`**: Decorated with `@lru_cache(maxsize=None)` [tests/submission_tests.py:23](). It ensures that for a specific set of parameters (`forest_height`, `n_nodes`, `batch_size`, `rounds`), the `KernelBuilder` only builds the kernel once [tests/submission_tests.py:24-27]().
2.  **`cycles()`**: Decorated with `@lru_cache(maxsize=None)` [tests/submission_tests.py:66](). It calls `do_kernel_test` and caches the resulting cycle count [tests/submission_tests.py:69-71](). This prevents the `Machine` from re-running the same instructions for every threshold check in `SpeedTests`.

## Error Handling in Measurement

If a correctness assertion fails during the execution of `do_kernel_test`, the `cycles()` function catches the `AssertionError`:

```python
try:
    res = do_kernel_test(10, 16, 256)
    return res
except AssertionError as e:
    return BASELINE * 2
```

By returning `BASELINE * 2` (295,468 cycles), the framework ensures that an incorrect implementation fails all speed tests (since they all check for values less than `BASELINE` or smaller thresholds).

Sources: [tests/submission_tests.py:68-73]()

## Test Parameters

The standard performance benchmark uses the following parameters, defined in the `cycles()` function:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `forest_height` | 10 | The height of the binary tree. |
| `rounds` | 16 | Number of hash rounds per batch item. |
| `batch_size` | 256 | Total items to process. |

Sources: [tests/submission_tests.py:69]()

## Standard Test Output

When running `python tests/submission_tests.py`, the measurement logic produces status updates to the console:

1.  **Execution Start**: `Testing forest_height=10, rounds=16, batch_size=256` [tests/submission_tests.py:31]()
2.  **Cycle Count**: `CYCLES: <count>` [tests/submission_tests.py:53]()
3.  **Speedup**: `Speedup over baseline: <ratio>` [tests/submission_tests.py:70]()

Sources: [tests/submission_tests.py:31-70]()

---

# Page: Running and Interpreting Tests

# Running and Interpreting Tests

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Readme.md](Readme.md)
- [tests/submission_tests.py](tests/submission_tests.py)

</details>



This page provides a practical guide for executing tests, understanding their output, debugging failures, and iterating on optimizations. For information about test suite structure and organization, see [Test Suite Structure](#6.1). For details on correctness validation mechanisms, see [Correctness Validation](#6.2). For performance measurement methodology, see [Performance Measurement](#6.3).

## Test Execution Overview

The repository provides two test entry points serving different purposes:

| Test File | Purpose | Simulator Used | When to Use |
|-----------|---------|---------------|-------------|
| `perf_takehome.py` | Development and debugging | `problem.py` (live) | During optimization work, with trace enabled |
| `tests/submission_tests.py` | Final validation and scoring | `frozen_problem.py` | Before submission, to check threshold performance |

Sources: [perf_takehome.py:1-273](), [tests/submission_tests.py:1-120]()

## Running Development Tests

### Basic Test Execution

Execute tests from the repository root:

```bash
# Run all tests in perf_takehome.py
python perf_takehome.py

# Run specific test
python perf_takehome.py Tests.test_kernel_cycles

# Run with trace generation (for debugging)
python perf_takehome.py Tests.test_kernel_trace
```

Sources: [perf_takehome.py:258-267]()

### Available Development Tests

The `Tests` class in `perf_takehome.py` provides:

**`test_ref_kernels()`** [perf_takehome.py:226-239]()
- Validates that `reference_kernel` and `reference_kernel2` produce identical results.
- Runs 10 randomized test cases with varying tree heights and batch sizes.
- Useful for verifying reference implementation consistency.

**`test_kernel_trace()`** [perf_takehome.py:241-243]()
- Executes the full-scale benchmark (height=10, rounds=16, batch=256) with tracing enabled.
- Generates `trace.json` for visualization with Perfetto UI.
- **Recommended for debugging** - see [Trace Generation](#7.1) for visualization workflow.

**`test_kernel_cycles()`** [perf_takehome.py:254-255]()
- Measures cycle count for standard benchmark parameters.
- Quick performance check during development.
- Uses development simulator (allows debug output).

Sources: [perf_takehome.py:225-256]()

## Running Submission Tests

### Execution Commands

```bash
# Run all submission tests
python tests/submission_tests.py

# Run only correctness tests
python tests/submission_tests.py CorrectnessTests

# Run only speed tests
python tests/submission_tests.py SpeedTests

# Run specific threshold test
python tests/submission_tests.py SpeedTests.test_opus45_11hr
```

Sources: [tests/submission_tests.py:118-120]()

### Test Classes

#### CorrectnessTests

The `CorrectnessTests.test_kernel_correctness()` validates functional correctness across multiple random inputs [tests/submission_tests.py:57-60]():

```python
def test_kernel_correctness(self):
    for i in range(8):
        do_kernel_test(10, 16, 256)
```

- Runs 8 iterations with non-deterministic random seeds [tests/submission_tests.py:32-33]().
- Each iteration generates a new `Tree` and `Input` configuration [tests/submission_tests.py:33-34]().
- Tests against standard benchmark parameters (height=10, rounds=16, batch=256) [tests/submission_tests.py:60]().
- **Must pass** before performance is meaningful.

#### SpeedTests

The `SpeedTests` class contains progressive performance thresholds [tests/submission_tests.py:76-116](). Each test method asserts `cycles() < THRESHOLD`:

| Test Method | Threshold | Description |
|-------------|-----------|-------------|
| `test_kernel_speedup()` | 147,734 | Beat baseline (any improvement) |
| `test_kernel_updated_starting_point()` | 18,532 | Updated starter code performance |
| `test_opus4_many_hours()` | 2,164 | Claude Opus 4 extended optimization |
| `test_opus45_casual()` | 1,790 | Best human 2-hour performance |
| `test_opus45_2hr()` | 1,579 | Claude Opus 4.5 2-hour harness |
| `test_sonnet45_many_hours()` | 1,548 | Claude Sonnet 4.5 extended |
| `test_opus45_11hr()` | 1,487 | **Recruitment threshold** |
| `test_opus45_improved_harness()` | 1,363 | Best known performance |

Sources: [tests/submission_tests.py:76-116](), [Readme.md:13-18]()

### Caching Behavior

The `cycles()` function uses `@lru_cache(maxsize=None)` to avoid redundant simulation [tests/submission_tests.py:66-71]():

```python
@lru_cache(maxsize=None)
def cycles():
    try:
        res = do_kernel_test(10, 16, 256)
        print("Speedup over baseline: ", BASELINE / res)
        return res
    except AssertionError as e:
        return BASELINE * 2
```

**Implications:**
- Cycle count is computed **once** per test run, then cached [tests/submission_tests.py:66-71]().
- All `SpeedTests` methods use the same cached result.
- Correctness failures return `BASELINE * 2` (295,468 cycles), causing all speed tests to fail [tests/submission_tests.py:73]().
- To re-measure after code changes, restart the Python process.

Sources: [tests/submission_tests.py:66-73]()

## Understanding Test Output

### Standard Output Format

Diagram: Test Execution Logic Flow

```mermaid
flowchart TD
    Start["Test Execution Starts"]
    Params["Print: forest_height, rounds, batch_size"]
    Build["KernelBuilder.build_kernel()"]
    Execute["Machine.run()"]
    Validate["Validate vs reference_kernel2"]
    
    Success["Print: CYCLES\nPrint: Speedup"]
    Failure["AssertionError: Message"]
    
    Start --> Params
    Params --> Build
    Build --> Execute
    Execute --> Validate
    
    Validate -->|Correct| Success
    Validate -->|Mismatch| Failure
```

Sources: [perf_takehome.py:175-222](), [tests/submission_tests.py:30-54]()

### Example Output: Success

```
Testing forest_height=10, rounds=16, batch_size=256
CYCLES:  18532
Speedup over baseline:  7.971459383753502
.
----------------------------------------------------------------------
Ran 1 test in 0.234s

OK
```

**Interpretation:**
- Test completed successfully (correctness validated).
- Required 18,532 cycles to complete.
- Achieved ~7.97x speedup over baseline (147,734 cycles).

### Example Output: Correctness Failure

```
Testing forest_height=10, rounds=16, batch_size=256
Traceback (most recent call last):
  ...
AssertionError: Incorrect output values
```

**Interpretation:**
- Generated instructions produced incorrect results.
- Memory state at `inp_values_p` differs from reference implementation [tests/submission_tests.py:49-52]().

### Example Output: Performance Failure

```
Testing forest_height=10, rounds=16, batch_size=256
CYCLES:  2500
Speedup over baseline:  59.0936
F
======================================================================
FAIL: test_opus45_casual (tests.submission_tests.SpeedTests)
----------------------------------------------------------------------
...
AssertionError: assert 2500 < 1790
```

**Interpretation:**
- Correctness validation passed.
- Cycle count (2,500) exceeds threshold (1,790) [tests/submission_tests.py:99]().

Sources: [tests/submission_tests.py:30-54](), [tests/submission_tests.py:85-115]()

## Interpreting Test Failures

### Debugging Correctness Failures

Diagram: Data Space Validation Comparison

```mermaid
flowchart LR
    subgraph "Simulated State"
        MachineObj["Machine"]
        MachineMem["Machine.mem"]
    end
    
    subgraph "Reference State"
        RefFunc["reference_kernel2"]
        RefMem["ref_mem"]
    end
    
    subgraph "Validation Logic"
        Compare{{"machine.mem[inp_values_p:] == ref_mem[inp_values_p:]"}}
        Pass["Correctness Pass"]
        Fail["AssertionError"]
    end
    
    MachineObj --> MachineMem
    RefFunc --> RefMem
    
    MachineMem --> Compare
    RefMem --> Compare
    
    Compare -->|True| Pass
    Compare -->|False| Fail
```

Sources: [tests/submission_tests.py:40-52](), [frozen_problem.py:284-300]()

The assertion at [tests/submission_tests.py:49-52]() compares the `inp_values` array in memory:

```python
inp_values_p = ref_mem[6]
assert (
    machine.mem[inp_values_p : inp_values_p + len(inp.values)]
    == ref_mem[inp_values_p : inp_values_p + len(inp.values)]
), "Incorrect output values"
```

**Common Causes:**

1. **Missing or incorrect hash stages**: The `build_hash()` method must implement all `HASH_STAGES` operations in order [perf_takehome.py:74-83]().
2. **Incorrect scratch register reuse**: Overwriting values still needed in subsequent operations.
3. **Wrong VLIW packing**: Multiple operations in the same bundle that create read-after-write conflicts within a single cycle.
4. **Missing pause points**: If using development tests with `reference_kernel2` yields, `pause` instructions must match the reference yield points [perf_takehome.py:115-119]().

**Debugging Strategy:**

Enable debug comparisons and prints in `do_kernel_test()` within `perf_takehome.py` [perf_takehome.py:202-218]():

```python
machine.prints = True  # Set this to enable output
for i, ref_mem in enumerate(reference_kernel2(mem, value_trace)):
    machine.run()
    if prints:
        print(machine.mem[inp_values_p : inp_values_p + len(inp.values)])
        print(ref_mem[inp_values_p : inp_values_p + len(inp.values)])
```

This shows your output vs expected output at each pause point, allowing identification of where divergence occurs.

Sources: [perf_takehome.py:175-222]()

### Debugging Performance Issues

When correctness passes but cycle count is too high:

**Step 1: Measure baseline for your implementation**
Run `test_kernel_cycles` to get your current cycle count [perf_takehome.py:254-255]().

**Step 2: Enable tracing**
Run `test_kernel_trace` and visualize with Perfetto UI [perf_takehome.py:241-243]().

**Step 3: Identify bottlenecks**
In Perfetto UI, examine:
- **Engine utilization**: Are ALU/VALU slots being filled efficiently?
- **Memory access patterns**: Are LOAD/STORE engines saturated?
- **Parallelization**: Are operations serialized that could be parallel?
- **Scratch allocation**: Is scratch space used efficiently?

Sources: [perf_takehome.py:241-243](), [perf_takehome.py:262-266]()

## Test Iteration Workflow

Diagram: Development Iteration Cycle

```mermaid
flowchart TD
    Start["Modify KernelBuilder.build_kernel()"]
    
    QuickTest["Run: python perf_takehome.py Tests.test_kernel_cycles"]
    
    CheckCorrect{{"Correctness passed?"}}
    
    CheckPerf{{"Cycle count improved?"}}
    
    TraceTest["Run: python perf_takehome.py Tests.test_kernel_trace"]
    
    Visualize["Analyze in Perfetto UI (watch_trace.py)"]
    
    Identify["Identify Bottlenecks"]
    
    SubmitTest["Run: python tests/submission_tests.py"]
    
    CheckThreshold{{"Recruitment Threshold Passed?"}}
    
    Done["Ready for submission (< 1487 cycles)"]
    
    Start --> QuickTest
    QuickTest --> CheckCorrect
    
    CheckCorrect -->|No| Start
    CheckCorrect -->|Yes| CheckPerf
    
    CheckPerf -->|No| TraceTest
    CheckPerf -->|Yes| SubmitTest
    
    TraceTest --> Visualize
    Visualize --> Identify
    Identify --> Start
    
    SubmitTest --> CheckThreshold
    CheckThreshold -->|Yes| Done
    CheckThreshold -->|No| TraceTest
```

Sources: [perf_takehome.py:241-273](), [tests/submission_tests.py:1-120](), [Readme.md:21-21]()

### Workflow Phases

**Phase 1: Rapid Iteration (Development Tests)**
Use `perf_takehome.py` for fast feedback:
- Test correctness with `test_kernel_cycles` [perf_takehome.py:254-255]().
- Quick cycle count measurement.
- Uses development simulator (not frozen).

**Phase 2: Deep Analysis (Trace Mode)**
When performance plateaus:
- Generate trace with `test_kernel_trace` [perf_takehome.py:241-243]().
- Visualize execution with Perfetto UI.
- Identify specific bottlenecks.

**Phase 3: Validation (Submission Tests)**
Before final submission:
- Run full `CorrectnessTests` (8 random seeds) [tests/submission_tests.py:58-60]().
- Check `SpeedTests` to see which thresholds you pass [tests/submission_tests.py:76-116]().
- Uses frozen simulator for deterministic results.

Sources: [perf_takehome.py:258-273](), [tests/submission_tests.py:57-116]()

## Key Command Reference

| Command | Purpose | Output Location |
|---------|---------|----------------|
| `python perf_takehome.py` | Run all development tests | stdout |
| `python perf_takehome.py Tests.test_kernel_cycles` | Quick performance check | stdout (cycle count) |
| `python perf_takehome.py Tests.test_kernel_trace` | Generate execution trace | `trace.json` |
| `python tests/submission_tests.py` | Run all validation tests | stdout (pass/fail) |
| `python tests/submission_tests.py CorrectnessTests` | Validate correctness only | stdout |
| `python tests/submission_tests.py SpeedTests` | Check performance thresholds | stdout |
| `python watch_trace.py` | Start trace visualization server | localhost:8000 |

Sources: [perf_takehome.py:258-273](), [tests/submission_tests.py:118-119]()

## Notes on Test Determinism

**Development Tests (`perf_takehome.py`)**
- Use fixed seed (`seed=123`) [perf_takehome.py:179-184]().
- Deterministic for debugging; same tree and input every run.

**Submission Tests (`tests/submission_tests.py`)**  
- **No seed set** [tests/submission_tests.py:32-33]().
- Non-deterministic tree and input generation.
- Tests robustness across varied inputs.
- Cycle count may vary slightly across runs.

This design ensures that optimizations work correctly for arbitrary inputs, not just a single test case.

Sources: [perf_takehome.py:175-187](), [tests/submission_tests.py:30-35]()

---

# Page: Performance Analysis and Debugging

# Performance Analysis and Debugging

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [watch_trace.html](watch_trace.html)
- [watch_trace.py](watch_trace.py)

</details>



This document covers the trace visualization system used for debugging performance issues and understanding execution behavior in the VLIW SIMD simulator. The trace system generates Chrome Trace Event Format files that can be visualized using Perfetto UI, providing detailed insight into instruction execution, slot utilization, and scratch space updates across cycles.

For information about the machine architecture being traced, see [Machine Architecture](#4). For information about performance measurement in tests, see [Performance Measurement](#6.3). For optimization strategies, see [Optimization Strategies and Patterns](#5.4).

## Trace System Architecture

The trace visualization pipeline consists of three integrated components: trace generation in the simulator, a local HTTP server for serving trace files, and a web interface that communicates with Perfetto UI.

### System Flow Diagram
Title: Trace Visualization Pipeline Architecture
```mermaid
flowchart TB
    subgraph "Machine Simulator (problem.py)"
        Machine["Machine(trace=True)"]
        Setup["setup_trace()"]
        TraceSlot["trace_slot()"]
        TracePost["trace_post_step()"]
        JsonFile["trace.json"]
    end
    
    subgraph "Local Server (watch_trace.py)"
        HTTPServer["MyHandler<br/>Port 8000"]
        ServeHTML["GET /<br/>Returns watch_trace.html"]
        ServeJSON["GET /trace.json<br/>Streams trace file"]
        ServeMtime["GET /mtime<br/>Returns file timestamp"]
        ProxyPerfetto["GET /perfetto/*<br/>Proxies to ui.perfetto.dev"]
    end
    
    subgraph "Browser (watch_trace.html)"
        FetchTrace["fetchAndOpen()"]
        Repoll["repoll()<br/>Every 500ms"]
        OpenWin["window.open()"]
        PostMessage["window.postMessage()"]
    end
    
    subgraph "Perfetto UI"
        PerfettoWindow["ui.perfetto.dev"]
        Timeline["Timeline View"]
        EngineTracks["Engine Slot Tracks"]
        ScratchTracks["Scratch Variable Tracks"]
    end
    
    Machine --> Setup
    Setup --> JsonFile
    TraceSlot --> JsonFile
    TracePost --> JsonFile
    
    JsonFile -.-> ServeJSON
    HTTPServer --> ServeHTML
    HTTPServer --> ServeJSON
    HTTPServer --> ServeMtime
    HTTPServer --> ProxyPerfetto
    
    ServeHTML --> FetchTrace
    FetchTrace --> ServeJSON
    FetchTrace --> ServeMtime
    FetchTrace --> OpenWin
    OpenWin --> PerfettoWindow
    PostMessage --> PerfettoWindow
    Repoll --> ServeMtime
    Repoll --> ServeJSON
    Repoll --> PostMessage
    
    PerfettoWindow --> Timeline
    Timeline --> EngineTracks
    Timeline --> ScratchTracks
```
Sources: [watch_trace.py:9-67](), [watch_trace.html:36-130]()

## Trace Generation (#7.1)

Traces are enabled by passing `trace=True` to the `Machine` constructor. The simulator records two primary types of data: engine slot activity and scratch memory state.

*   **Slot Tracing:** Every operation in every engine (e.g., `alu`, `valu`, `load`) is recorded as a duration event.
*   **Scratch Tracing:** Changes to scratch memory addresses are recorded. If a `DebugInfo` object is provided with a `scratch_map`, these addresses are labeled with human-readable names in the UI.
*   **Output Format:** The system produces a `trace.json` file compatible with the Chrome Trace Event Format.

For details, see [Trace Generation](#7.1).

## Trace Visualization Server (#7.2)

The `watch_trace.py` script runs a specialized `http.server.BaseHTTPRequestHandler` called `MyHandler` on port 8000. It serves three main functions:
1.  **File Hosting:** Serves `watch_trace.html` and the `trace.json` file.
2.  **State Polling:** Provides a `/mtime` endpoint that returns the last modified timestamp of `trace.json` so the browser can detect when a new simulation has finished.
3.  **Perfetto Proxying:** Proxies requests to `https://ui.perfetto.dev` while applying patches to the Perfetto frontend code (e.g., auto-expanding tracks and fixing known UI bugs).

For details, see [Trace Visualization Server](#7.2).

Sources: [watch_trace.py:9-67](), [watch_trace.py:74-79]()

## Web Interface Usage (#7.3)

The `watch_trace.html` file provides the frontend logic for the debugging system. It automates the process of loading local trace data into the cloud-hosted Perfetto UI using the `window.postMessage` API.

*   **Handshake:** It performs a "PING/PONG" handshake with the Perfetto window to ensure the UI is ready before sending data.
*   **Live Reload:** It implements a `repoll()` function that checks `/mtime` every 500ms. If the timestamp changes, it automatically refetches the trace and pushes it to the open Perfetto tab.

For details, see [Web Interface Usage](#7.3).

Sources: [watch_trace.html:43-90](), [watch_trace.html:103-120]()

## Perfetto UI Integration (#7.4)

Perfetto UI provides a high-fidelity timeline view of the kernel execution.

### Visualization Mapping
Title: Code Entity to Perfetto Track Mapping
```mermaid
graph TD
    subgraph "Code Entities"
        ALU_Slots["Engine: 'alu' (0-11)"]
        VALU_Slots["Engine: 'valu' (0-5)"]
        Scratch_Map["DebugInfo.scratch_map"]
    end

    subgraph "Perfetto UI Tracks"
        ALU_Track["Process: 'Core 0'<br/>Thread: 'alu-N'"]
        VALU_Track["Process: 'Core 0'<br/>Thread: 'valu-N'"]
        Var_Track["Process: 'Core 0 Scratch'<br/>Thread: 'variable_name'"]
    end

    ALU_Slots --> ALU_Track
    VALU_Slots --> VALU_Track
    Scratch_Map --> Var_Track
```
Sources: [watch_trace.py:55-59](), [watch_trace.html:75-90]()

Users can use the UI to:
*   Identify cycles where engines are idle (bubbles in the pipeline).
*   Verify that vector operations are correctly aligned.
*   Monitor the values of scratch variables across the entire execution.

For details, see [Perfetto UI Integration](#7.4).

## Debugging Workflows and Strategies (#7.5)

Effective performance analysis involves identifying why specific engine slots are empty and finding ways to fill them.

*   **Bottleneck Identification:** Use the selection tool to see which engine (e.g., `load` vs `alu`) is the limiting factor for a loop iteration.
*   **Dependency Tracking:** Observe the "Core 0 Scratch" tracks to see if an instruction is stalled waiting for a value written in a previous cycle.
*   **Parallelization:** Look for opportunities to move scalar `alu` operations into empty slots during long `valu` or `load` sequences.

For details, see [Debugging Workflows and Strategies](#7.5).

---

# Page: Trace Generation

# Trace Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page documents the trace generation system built into the `Machine` simulator, which produces execution traces in Chrome Trace Event Format for performance visualization and debugging. For information about the visualization server and UI that consumes these traces, see [7.2 Trace Visualization Server]() and [7.3 Web Interface Usage]().

## Purpose and Scope

The trace generation system captures fine-grained execution events during kernel simulation, writing them to a `trace.json` file that can be visualized in Perfetto UI. This enables developers to:

- Observe parallel slot execution across engine types (`alu`, `valu`, `load`, `store`, `flow`)
- Monitor scratch variable state changes over time
- Identify performance bottlenecks and underutilized execution slots
- Debug instruction scheduling and VLIW packing effectiveness

The tracing infrastructure is completely optional and has no effect on cycle counting or correctness validation.

## Enabling Trace Generation

Trace generation is controlled by the `trace` parameter when constructing a `Machine` instance:

```python
machine = Machine(
    mem,
    instructions,
    debug_info,
    n_cores=N_CORES,
    trace=True  # Enable tracing
)
```

When `trace=True`, the `Machine` constructor calls `setup_trace()` to initialize the trace file [tests/frozen_problem.py:118-119](). When `trace=False` (the default), no trace file is generated and the tracing methods become no-ops [tests/frozen_problem.py:121]().

Sources: [tests/frozen_problem.py:97-121](), [problem.py:97-121]()

### Test Integration

The test suite provides a dedicated test for trace generation in `submission_tests.py`:

```python
def test_kernel_trace(self):
    do_kernel_test(10, 16, 256, trace=True, prints=False)
```

This test runs the full-scale benchmark kernel with tracing enabled, producing a comprehensive `trace.json` file for analysis [tests/submission_tests.py:100-102]().

Sources: [tests/submission_tests.py:100-102]()

## Chrome Trace Event Format

The simulator outputs traces in [Chrome's Trace Event Format](https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/preview), a JSON-based format designed for performance visualization tools [tests/frozen_problem.py:153-158](). This format is compatible with:

- **Perfetto UI** (ui.perfetto.dev) - recommended
- **chrome://tracing** - Chrome's built-in trace viewer

The format uses structured JSON events with specific fields:

| Field | Purpose |
|-------|---------|
| `name` | Event name/label displayed in UI |
| `ph` | Phase type (`M` = metadata, `X` = duration event) |
| `pid` | Process ID (maps to cores) |
| `tid` | Thread ID (maps to engine slots or scratch variables) |
| `ts` | Timestamp (cycle number) |
| `dur` | Duration (always 1 cycle for slot events) |
| `cat` | Category (e.g., "op" for operations) |
| `args` | Additional structured data |

Sources: [tests/frozen_problem.py:160-196]()

## Trace File Lifecycle

```mermaid
flowchart TB
    Init["Machine.__init__(trace=True)"]
    Setup["setup_trace()"]
    OpenFile["Open 'trace.json' for writing"]
    WriteHeader["Write '[' array start"]
    WriteMetadata["Write process/thread metadata"]
    
    RunLoop["Machine.run()"]
    StepLoop["For each instruction cycle"]
    TraceSlots["trace_slot() for each executed slot"]
    TracePost["trace_post_step() for scratch updates"]
    
    Destructor["Machine.__del__()"]
    WriteClosing["Write ']' array end"]
    CloseFile["Close trace.json"]
    
    Init --> Setup
    Setup --> OpenFile
    OpenFile --> WriteHeader
    WriteHeader --> WriteMetadata
    WriteMetadata --> RunLoop
    
    RunLoop --> StepLoop
    StepLoop --> TraceSlots
    TraceSlots --> TracePost
    TracePost --> StepLoop
    
    StepLoop --> Destructor
    Destructor --> WriteClosing
    WriteClosing --> CloseFile
```

**Diagram: Trace File Lifecycle**

Sources: [tests/frozen_problem.py:97-121](), [tests/frozen_problem.py:151-196](), [tests/frozen_problem.py:399-402]()

## Trace Setup and Metadata

The `setup_trace()` method initializes the trace file and writes structural metadata that defines the visualization hierarchy [tests/frozen_problem.py:151-160]().

### Process and Thread Metadata

The trace format organizes events into a two-level hierarchy:

1. **Processes** - Represent individual cores or scratch variable groups [tests/frozen_problem.py:165-167]().
2. **Threads** - Represent engine slots or specific scratch variables within a core [tests/frozen_problem.py:173-175]().

```mermaid
graph TB
    subgraph "Process 0 (Core 0)"
        alu0["Thread: alu-0"]
        alu1["Thread: alu-1"]
        alu11["Thread: alu-11"]
        valu0["Thread: valu-0"]
        valu5["Thread: valu-5"]
        load0["Thread: load-0"]
        load1["Thread: load-1"]
        store0["Thread: store-0"]
        store1["Thread: store-1"]
        flow0["Thread: flow-0"]
    end
    
    subgraph "Process 1 (Core 0 Scratch)"
        scratch0["Thread: rounds-1"]
        scratch1["Thread: n_nodes-1"]
        scratch2["Thread: tmp1-1"]
        scratchN["Thread: tmp_addr-1"]
    end
```

**Diagram: Trace Hierarchy Structure**

Each core gets two processes:
- **Core N**: Contains threads for each engine slot (e.g., "alu-0" through "alu-11") [tests/frozen_problem.py:166-176]().
- **Core N Scratch**: Contains threads for each named scratch variable [tests/frozen_problem.py:189-195]().

Sources: [tests/frozen_problem.py:151-196]()

### Thread ID Assignment

Thread IDs are assigned systematically:

```python
tid_counter = 0
self.tids = {}
for ci, core in enumerate(self.cores):
    for name, limit in SLOT_LIMITS.items():
        if name == "debug":
            continue
        for i in range(limit):
            tid_counter += 1
            self.tids[(ci, name, i)] = tid_counter
```

For scratch variables, thread IDs are derived from scratch addresses plus `BASE_ADDR_TID` (100000) [tests/frozen_problem.py:194]():

```python
BASE_ADDR_TID = 100000
# Scratch variable at address 5 gets TID 100005
```

This ensures scratch variable TIDs don't collide with slot TIDs [tests/frozen_problem.py:61]().

Sources: [tests/frozen_problem.py:162-196](), [tests/frozen_problem.py:61]()

### Slot Limits and Thread Count

Each engine type has a maximum number of slots that can execute per cycle, defined in `SLOT_LIMITS` [tests/frozen_problem.py:48-55]():

| Engine | Slot Limit | Threads Created |
|--------|-----------|-----------------|
| `alu` | 12 | 12 (alu-0 through alu-11) |
| `valu` | 6 | 6 (valu-0 through valu-5) |
| `load` | 2 | 2 (load-0, load-1) |
| `store` | 2 | 2 (store-0, store-1) |
| `flow` | 1 | 1 (flow-0) |
| `debug` | 64 | 0 (not traced) |

Sources: [tests/frozen_problem.py:48-55]()

## Event Capture During Execution

The `Machine.step()` method integrates trace capture into the execution cycle [tests/frozen_problem.py:352-397](). Two methods handle event generation:

### Slot Execution Events

`trace_slot()` is called for each executed slot before the slot's operation is performed [tests/frozen_problem.py:384-386]():

```python
def trace_slot(self, core, slot, name, i):
    self.trace.write(
        f'{{"name": "{slot[0]}", "cat": "op", "ph": "X", '
        f'"pid": {core.id}, "tid": {self.tids[(core.id, name, i)]}, '
        f'"ts": {self.cycle}, "dur": 1, '
        f'"args":{{"slot": "{str(slot)}", "named": "{str(self.rewrite_slot(slot))}" }} }},\n'
    )
```

This creates a duration event (`"ph": "X"`) showing the operation type, cycle number, and operands [tests/frozen_problem.py:347-350]().

Sources: [tests/frozen_problem.py:347-350](), [tests/frozen_problem.py:384-386]()

### Scratch Variable Updates

`trace_post_step()` is called after all writes are committed, capturing scratch variable state changes [tests/frozen_problem.py:393-394]():

```python
def trace_post_step(self, instr, core):
    for addr, (name, length) in self.debug_info.scratch_map.items():
        if any((addr + vi) in self.scratch_write for vi in range(length)):
            val = str(core.scratch[addr : addr + length])
            # ... formatting and write ...
```

This creates events on the "Core N Scratch" process showing the new value of any scratch variable that was modified during the cycle [tests/frozen_problem.py:337-345]().

Sources: [tests/frozen_problem.py:337-345](), [tests/frozen_problem.py:393-394]()

### Execution Flow Integration

```mermaid
sequenceDiagram
    participant Step as "Machine.step()"
    participant Engine as "Engine Function"
    participant Trace as "Trace Methods"
    participant File as "trace.json"
    
    Note over Step: Initialize scratch_write, mem_write
    
    loop For each engine in instruction
        loop For each slot in engine
            Step->>Trace: trace_slot(core, slot, name, i)
            Trace->>File: Write slot event JSON
            Step->>Engine: Execute slot operation
            Engine->>Step: Buffer writes in scratch_write
        end
    end
    
    Note over Step: Commit all buffered writes
    
    Step->>Trace: trace_post_step(instr, core)
    Trace->>File: Write scratch update events
    
    Note over Step: Increment cycle counter
```

**Diagram: Trace Integration in Execution Cycle**

Sources: [tests/frozen_problem.py:352-397]()

## Variable Name Resolution

The `rewrite_slot()` method converts scratch addresses to human-readable variable names for the trace [tests/frozen_problem.py:146-149]():

```python
def rewrite_slot(self, slot):
    return tuple(
        self.debug_info.scratch_map.get(s, (None, None))[0] or s 
        for s in slot
    )
```

This uses the `DebugInfo.scratch_map` dictionary [tests/frozen_problem.py:34-42](). In traces, this allows viewing operations like:
- Raw: `('+', 5, 3, 4)` 
- Named: `('+', tmp1, rounds, n_nodes)`

Sources: [tests/frozen_problem.py:146-149](), [tests/frozen_problem.py:34-42]()

## Trace File Finalization

The trace file is properly closed when the `Machine` object is destroyed [tests/frozen_problem.py:399-402]():

```python
def __del__(self):
    if self.trace is not None:
        self.trace.write("]")
        self.trace.close()
```

This completes the JSON array. If the simulator crashes, the file may be left in an invalid state.

Sources: [tests/frozen_problem.py:399-402]()

---

# Page: Trace Visualization Server

# Trace Visualization Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [watch_trace.py](watch_trace.py)

</details>



## Purpose and Scope

This document describes `watch_trace.py`, a local HTTP server that enables live visualization of execution traces generated by the Machine simulator. The server provides endpoints for serving trace files, monitoring file modifications, and proxying the Perfetto UI visualization tool. For information about generating trace files, see [7.1 Trace Generation](). For details on the web interface that consumes these endpoints, see [7.3 Web Interface Usage]().

**Sources:** [watch_trace.py:1-85]()

---

## Server Architecture

The `watch_trace.py` server is implemented using Python's built-in `http.server` module. It creates a custom request handler `MyHandler` that serves static files, streams trace data, provides modification time polling, and proxies external resources.

### Request Flow Diagram

```mermaid
flowchart TD
    Start["run() function"] --> CreateServer["HTTPServer on port 8000"]
    CreateServer --> OpenBrowser["webbrowser.open<br/>'http://localhost:8000'"]
    CreateServer --> ServeForever["httpd.serve_forever()"]
    
    subgraph "Request Handler: MyHandler"
        Request["HTTP GET Request"] --> Router{"self.path"}
        
        Router -->|"/"| RootHandler["Serve watch_trace.html<br/>Content-type: text/html"]
        Router -->|"/trace.json"| TraceHandler["Stream trace.json in 8KB chunks<br/>Content-type: application/json"]
        Router -->|"/mtime"| MtimeHandler["Return os.path.getmtime<br/>of trace.json<br/>Content-type: text/plain"]
        Router -->|"/perfetto/*"| ProxyHandler["Proxy to ui.perfetto.dev<br/>with response patching"]
        Router -->|"other"| NotFound["404 File Not Found"]
        
        TraceHandler --> ReadLoop["Read file.read(8192)<br/>in chunks"]
        MtimeHandler --> FormatTime["datetime.fromtimestamp<br/>format as string"]
        ProxyHandler --> FetchRemote["urllib.request.urlopen<br/>proxy_url"]
        FetchRemote --> PatchResponse["Apply patches to<br/>frontend_bundle.js"]
    end
    
    ServeForever -.->|"on each request"| Request
```

**Sources:** [watch_trace.py:8-84]()

---

## HTTP Endpoints

The server implements five distinct endpoints through the `do_GET` method of the `MyHandler` class:

### Endpoint Reference Table

| Endpoint | Content-Type | Purpose | Implementation |
|----------|-------------|---------|----------------|
| `/` | `text/html` | Serves the web interface | Reads and returns `watch_trace.html` [watch_trace.py:13-18]() |
| `/trace.json` | `application/json` | Streams the trace file | Chunked read of `trace.json` (8192 bytes) [watch_trace.py:21-27]() |
| `/mtime` | `text/plain` | Provides trace file modification time | Returns `os.path.getmtime("trace.json")` formatted timestamp [watch_trace.py:29-38]() |
| `/perfetto/*` | various | Proxies Perfetto UI resources | Forwards to `ui.perfetto.dev` with patches [watch_trace.py:40-64]() |
| other | - | Error handling | Returns 404 response [watch_trace.py:67]() |

**Sources:** [watch_trace.py:10-70]()

### Root Endpoint (/)

The root endpoint serves the web interface HTML file directly from disk. It loads the entire `watch_trace.html` file into memory and serves it [watch_trace.py:13-18](). The file is expected to be in the same directory as the server script.

**Sources:** [watch_trace.py:13-18]()

### Trace Streaming Endpoint (/trace.json)

The `/trace.json` endpoint streams the trace file using chunked transfer to handle potentially large trace files efficiently:

```mermaid
sequenceDiagram
    participant Client as "Web Browser"
    participant Server as "MyHandler.do_GET()"
    participant File as "trace.json file"
    
    Client->>Server: GET /trace.json
    Server->>Server: send_response(200)
    Server->>Server: send_header("application/json")
    Server->>File: open("trace.json", "rb")
    
    loop While chunks available
        File->>Server: file.read(8192)
        Server->>Client: wfile.write(chunk)
    end
    
    File->>Server: EOF (empty chunk)
    Server->>Client: Connection closed
```

The chunked reading strategy (8192 bytes per read) prevents loading large trace files entirely into memory, making it suitable for traces that can grow to hundreds of megabytes during long simulations [watch_trace.py:25-27]().

**Sources:** [watch_trace.py:21-27]()

### Modification Time Endpoint (/mtime)

The `/mtime` endpoint enables the web interface to implement live reload functionality by polling for file changes. The endpoint returns a formatted timestamp string (e.g., "2024-01-15 14:30:45") using `datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")` [watch_trace.py:32-34](). The web interface can compare this against previous values to detect when `trace.json` has been regenerated.

**Sources:** [watch_trace.py:29-38]()

---

## Perfetto UI Proxy

The server includes a proxy mechanism for the Perfetto UI at `/perfetto/*` paths. This proxy forwards requests to `ui.perfetto.dev` while applying runtime patches to fix bugs and customize behavior.

### Proxy Architecture

```mermaid
flowchart LR
    Client["watch_trace.html<br/>in browser"] --> LocalProxy["/perfetto/* endpoint<br/>on localhost:8000"]
    LocalProxy --> BuildURL["proxy_url =<br/>'https://ui.perfetto.dev'<br/>+ path[len('/perfetto'):]"]
    BuildURL --> FetchRemote["urllib.request.urlopen<br/>(proxy_url)"]
    FetchRemote --> CheckPath{"path ends with<br/>frontend_bundle.js?"}
    
    CheckPath -->|Yes| ApplyPatches["Apply three<br/>binary patches"]
    CheckPath -->|No| PassThrough["Pass through<br/>unmodified"]
    
    ApplyPatches --> Patch1["Fix EngineProxy disposal bug"]
    Patch1 --> Patch2["Auto-expand tracks:<br/>collapsed: true → false"]
    Patch2 --> Patch3["Auto-expand heap profiles"]
    Patch3 --> UpdateLength["Recalculate Content-Length"]
    
    PassThrough --> SendResponse["Forward response<br/>to client"]
    UpdateLength --> SendResponse
```

**Sources:** [watch_trace.py:40-64]()

### Runtime Patches

The proxy applies three specific binary patches to `frontend_bundle.js` [watch_trace.py:48-59]():

#### Patch 1: EngineProxy Disposal Bug Fix
This patch prevents Perfetto from throwing errors when the `EngineProxy` is disposed, replacing the error with a silent null return [watch_trace.py:51-54](). This fixes a known bug in Perfetto that was fixed internally but not yet deployed at the time of the server's creation [watch_trace.py:50]().

#### Patch 2: Auto-Expand Tracks
This modifies Perfetto's default behavior to show all tracks expanded by default (`collapsed: false`), making it easier to see execution details immediately upon opening a trace [watch_trace.py:56]().

#### Patch 3: Auto-Expand Heap Profiles
This ensures heap profile tracks are also expanded by default, overriding the conditional logic that would collapse them [watch_trace.py:57-59]().

**Important:** Because these patches modify the response body, the server recalculates the `Content-Length` header at [watch_trace.py:62]() to match the new response size.

**Sources:** [watch_trace.py:48-64]()

---

## Server Startup and Configuration

### Startup Sequence

The server initialization follows this sequence:

```mermaid
sequenceDiagram
    participant Main as "__main__ block"
    participant RunFunc as "run() function"
    participant HTTPServer as "http.server.HTTPServer"
    participant Browser as "webbrowser module"
    
    Main->>RunFunc: run()
    RunFunc->>RunFunc: Create server_address = ("", 8000)
    RunFunc->>HTTPServer: HTTPServer(server_address, MyHandler)
    HTTPServer-->>RunFunc: httpd instance
    RunFunc->>Browser: webbrowser.open("http://localhost:8000")
    Browser-->>RunFunc: Opens default browser
    RunFunc->>HTTPServer: httpd.serve_forever()
    Note over HTTPServer: Blocks here, serving requests indefinitely
```

**Sources:** [watch_trace.py:74-84]()

### Configuration Constants

| Configuration | Value | Location | Description |
|---------------|-------|----------|-------------|
| Port | 8000 | [watch_trace.py:75]() | Server listening port |
| Chunk Size | 8192 | [watch_trace.py:26]() | Bytes per read for trace streaming |
| Timestamp Format | `"%Y-%m-%d %H:%M:%S"` | [watch_trace.py:32-33]() | Date format for mtime endpoint |

The server automatically opens the default web browser to `http://localhost:8000` immediately after starting [watch_trace.py:78]().

**Sources:** [watch_trace.py:75-79]()

---

## File Dependencies

The server expects the following files to exist in the current working directory:

### Required Files

```mermaid
graph TD
    Server["watch_trace.py<br/>HTTP Server"]
    
    Server -->|"serves"| HTML["watch_trace.html<br/>Web interface"]
    Server -->|"streams"| Trace["trace.json<br/>Execution trace data"]
    Server -->|"monitors"| TraceStat["trace.json mtime<br/>Filesystem metadata"]
    Server -->|"proxies"| Perfetto["ui.perfetto.dev<br/>Remote Perfetto UI"]
    
    HTML -.->|"generated by"| User["Developer/AI running<br/>Machine simulator"]
    Trace -.->|"generated by"| User
```

**Missing File Behavior:**
- If `watch_trace.html` is missing, requests to `/` will raise an `IOError` and return a 404 response [watch_trace.py:69-70]().
- If `trace.json` is missing, requests to `/trace.json` or `/mtime` will similarly fail with 404 [watch_trace.py:69-70]().
- Network failures when proxying to `ui.perfetto.dev` will raise exceptions and result in connection errors.

**Sources:** [watch_trace.py:17, 25, 31, 41, 69-70]()

---

## Error Handling

The `do_GET` method wraps request handling in a try-except block [watch_trace.py:11, 69](). File not found errors (missing `trace.json` or `watch_trace.html`) return clean 404 responses [watch_trace.py:70](). Unknown paths that don't match any defined endpoint also return 404 [watch_trace.py:67]().

**Sources:** [watch_trace.py:11, 67, 69-70]()

---

# Page: Web Interface Usage

# Web Interface Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [watch_trace.html](watch_trace.html)

</details>



## Purpose and Scope

This page documents `watch_trace.html`, the browser-based web interface for trace visualization. The interface serves as a bridge between the local trace file and Perfetto UI, providing automatic trace fetching, live reload functionality, and cross-window communication. For information about the backend server that serves this interface, see [Trace Visualization Server](#7.2). For details about using Perfetto UI itself, see [Perfetto UI Integration](#7.4).

---

## Interface Components

The web interface consists of a minimal HTML page with three main UI elements:

| Element | Type | Purpose |
|---------|------|---------|
| `#source` | `<select>` dropdown | Selects which trace file to load (default: `/trace.json`) |
| `#btn_fetch` | `<button>` | Triggers trace fetching and opens Perfetto UI window |
| `#logs` | `<pre>` | Displays status messages and debugging information |

The interface is intentionally minimal, focusing on functionality over aesthetics. The primary interaction is clicking the "Open Perfetto" button, which initiates the trace loading workflow.

**Sources:** [watch_trace.html:24-34]()

---

## Configuration Constants

The interface uses a single configuration constant that determines where Perfetto UI is hosted:

```javascript
const ORIGIN = "https://ui.perfetto.dev";
```

This points to the official Perfetto UI hosted by Google. An alternative localhost configuration is commented out at [watch_trace.html:37-38](), which could be used if proxying through the local server via the `/perfetto/` endpoint.

**Sources:** [watch_trace.html:37-38]()

---

## Trace Loading Workflow

The trace loading process follows a multi-step sequence involving fetch operations, window management, and inter-window communication:

**Figure 1: Trace Loading Sequence**
```mermaid
sequenceDiagram
    participant User
    participant Interface as "watch_trace.html"
    participant Server as "watch_trace.py (Server)"
    participant Perfetto as "Perfetto UI (ui.perfetto.dev)"

    User->>Interface: "Click 'Open Perfetto'"
    Interface->>Interface: "fetchAndOpen()"
    Interface->>Server: "GET /mtime"
    Server-->>Interface: "timestamp"
    Interface->>Server: "GET /trace.json"
    Server-->>Interface: "trace blob"
    Interface->>Interface: "blob.arrayBuffer()"
    Interface->>Perfetto: "window.open(ORIGIN)"
    Note over Interface,Perfetto: "PING/PONG handshake"
    loop "Every 50ms"
        Interface->>Perfetto: "postMessage('PING')"
    end
    Perfetto->>Interface: "postMessage('PONG')"
    Interface->>Interface: "Clear interval, remove listener"
    Interface->>Perfetto: "postMessage({perfetto: {...}})"
    Note over Perfetto: "Trace opens in UI"
    Interface->>Interface: "Start repoll() timer"
```

### Key Functions

**`fetchAndOpen(traceUrl)`** - Entry point for trace loading:

[watch_trace.html:49-58]()

This function:
1. Fetches the current modification time via `getMtime()`
2. Fetches the trace file as a blob
3. Converts the blob to an ArrayBuffer
4. Calls `openTrace()` to open Perfetto UI and send the data

**`getMtime()`** - Retrieves trace file modification timestamp:

[watch_trace.html:43-47]()

This simple wrapper fetches the `/mtime` endpoint provided by the local server, which returns the modification time of `trace.json` formatted as a timestamp string.

**`openTrace(arrayBuffer, traceUrl, mtime)`** - Opens Perfetto UI and initiates handshake:

[watch_trace.html:92-120]()

This function handles:
- Opening a new browser window to `ui.perfetto.dev`
- Detecting popup blockers and providing fallback UI
- Initiating the PING/PONG handshake to detect when Perfetto is ready
- Calling `sendTrace()` once the handshake completes
- Starting the `repoll()` timer for live reload

**Sources:** [watch_trace.html:43-120]()

---

## PING/PONG Handshake Protocol

Before sending trace data, the interface must ensure Perfetto UI is fully loaded and ready to receive messages. This is accomplished through a handshake protocol:

**Figure 2: Handshake Logic**
```mermaid
graph TB
    Open["window.open(ORIGIN)"] --> Timer["setInterval: PING every 50ms"]
    Timer --> Send["postMessage('PING', ORIGIN)"]
    Send --> Listen["addEventListener('message')"]
    Listen --> Check{"evt.data === 'PONG'?"}
    Check -->|No| Send
    Check -->|Yes| ClearTimer["clearInterval(timer)"]
    ClearTimer --> RemoveListener["removeEventListener"]
    RemoveListener --> SendTrace["sendTrace(win, arrayBuffer)"]
    SendTrace --> StartPoll["Start repoll() timer"]
```

The handshake implementation at [watch_trace.html:103-119]():

1. **Timer Setup**: Sends "PING" messages every 50ms
2. **Event Listener**: Waits for "PONG" response from Perfetto UI
3. **Cleanup**: Once PONG received, clears interval and removes listener
4. **Data Transfer**: Calls `sendTrace()` to send the trace ArrayBuffer
5. **Live Reload**: Starts the `repoll()` loop

### Popup Blocker Handling

If `window.open()` returns `null` (popup blocked), the interface gracefully degrades:

[watch_trace.html:94-100]()

- Changes button background color to yellow (`#f3ca63`)
- Updates button text to inform user of popup blocker
- Changes button `onclick` to retry opening the trace

**Sources:** [watch_trace.html:92-120]()

---

## Live Reload Mechanism

The interface implements automatic trace reloading by polling the `/mtime` endpoint every 500ms:

**Figure 3: Live Reload State Machine**
```mermaid
stateDiagram-v2
    [*] --> Waiting: "Start repoll()"
    Waiting --> FetchMtime: "After 500ms"
    FetchMtime --> Compare: "Get new mtime"
    Compare --> Waiting: "mtime unchanged"
    Compare --> FetchTrace: "mtime changed"
    FetchTrace --> SendToUI: "Get new ArrayBuffer"
    SendToUI --> Waiting: "postMessage to Perfetto"
    Waiting --> [*]: "Window closed"
```

**`repoll(win, traceUrl, mtime)`** - Implements the live reload loop:

[watch_trace.html:60-73]()

Algorithm:
1. Fetch current modification time via `getMtime()`
2. Compare with previous `mtime`
3. If changed:
   - Fetch new trace file from `traceUrl`
   - Convert to ArrayBuffer
   - Call `sendTrace()` to update Perfetto UI
4. Schedule next poll after 500ms with updated `mtime`

This creates a continuous monitoring loop that automatically refreshes the Perfetto UI whenever the trace file is regenerated.

**Sources:** [watch_trace.html:60-73]()

---

## Perfetto Communication Protocol

Communication with Perfetto UI uses the `postMessage` API with a specific message format:

**`sendTrace(win, arrayBuffer, traceUrl)`** - Sends trace data to Perfetto:

[watch_trace.html:75-90]()

The message structure follows Perfetto's API:

```javascript
{
    perfetto: {
        buffer: arrayBuffer,        // The trace data
        title: "trace.json",        // Display name
        url: reopenUrl.toString(),  // URL to reopen this trace
        keepApiOpen: true          // Keep communication channel open
    }
}
```

### Reopen URL Feature

The interface constructs a special URL that allows Perfetto to link back to reload the same trace:

```javascript
const reopenUrl = new URL(location.href);
reopenUrl.hash = `#reopen=${traceUrl}`;
```

When a user follows this link from Perfetto's sidebar, the interface detects it and automatically reloads:

[watch_trace.html:122-126]()

If the page loads with a hash starting with `#reopen=`, it extracts the trace URL and immediately calls `fetchAndOpen()`.

**Sources:** [watch_trace.html:75-126]()

---

## Data Flow Architecture

The complete data flow from trace generation to visualization:

**Figure 4: System Data Flow**
```mermaid
graph LR
    Generator["Machine (trace=True)"] --> File["trace.json"]
    File --> Server["watch_trace.py (Server)"]
    Server --> Mtime["/mtime"]
    Server --> Trace["/trace.json"]
    
    User["User"] --> Interface["watch_trace.html"]
    Interface --> FetchTrace["fetch('/trace.json')"]
    Interface --> PollMtime["fetch('/mtime')"]
    
    FetchTrace --> Trace
    PollMtime --> Mtime
    
    Interface --> PostMsg["postMessage(arrayBuffer)"]
    PostMsg --> Perfetto["ui.perfetto.dev"]
    
    Mtime --> CompareLogic["Compare mtime"]
    CompareLogic --> RefetchDecision{"Changed?"}
    RefetchDecision -->|Yes| FetchTrace
    RefetchDecision -->|No| Wait["Wait 500ms"]
    Wait --> PollMtime
```

**Sources:** [watch_trace.html:1-132]()

---

## Usage Scenarios

### Basic Usage

1. Start the local server: `python watch_trace.py`
2. Server automatically opens browser to `http://localhost:8000`
3. Interface loads and displays "Open Perfetto" button
4. Click button to fetch `trace.json` and open Perfetto UI
5. Trace visualization appears in new window

### Live Development Workflow

1. Run tests with tracing enabled to generate `trace.json`
2. Open web interface (if not already open)
3. Click "Open Perfetto" to view current trace
4. Make changes to kernel builder
5. Re-run tests to regenerate `trace.json`
6. Interface automatically detects change and reloads Perfetto
7. Review updated trace in same Perfetto window
8. Iterate without manual refreshing

### Troubleshooting Popup Blockers

If the "Open Perfetto" button shows yellow background with "Popups blocked" message:

1. Allow popups for `localhost:8000` in browser settings
2. Click the button again
3. Alternatively, manually navigate to `ui.perfetto.dev` and drag-drop `trace.json`

**Sources:** [watch_trace.html:94-100]()

---

## Implementation Details

### Event Listener Management

The interface carefully manages event listeners to avoid memory leaks:

- Adds message listener before PING/PONG handshake: [watch_trace.html:119]()
- Removes listener after handshake completes: [watch_trace.html:113]()
- Uses named function `onMessageHandler` for proper cleanup

### Timer Management

Two types of timers are used:

| Timer | Interval | Purpose | Cleanup |
|-------|----------|---------|---------|
| PING interval | 50ms | Detect Perfetto UI ready | `clearInterval()` on PONG |
| Repoll timeout | 500ms | Check for trace updates | Self-scheduling via `setTimeout()` |

The PING interval is aggressive (50ms) to minimize latency when opening traces. The repoll timeout is more conservative (500ms) to avoid overwhelming the server with `mtime` checks.

### Blob Handling

Trace data flows through multiple representations:

1. HTTP Response → `Response` object
2. `Response.blob()` → `Blob` object
3. `Blob.arrayBuffer()` → `ArrayBuffer`
4. `postMessage(arrayBuffer)` → Transferred to Perfetto

The ArrayBuffer is necessary because Perfetto's API expects raw binary data, and `postMessage` can efficiently transfer ArrayBuffers between windows.

**Sources:** [watch_trace.html:52-68]()

---

## Integration with Server Endpoints

The interface depends on three server endpoints provided by `watch_trace.py`:

| Endpoint | Method | Response Type | Purpose |
|----------|--------|---------------|---------|
| `/` | GET | HTML | Serves this interface |
| `/trace.json` | GET | JSON | Streams trace file |
| `/mtime` | GET | Text | Returns trace modification time |

The `/mtime` endpoint is critical for the live reload feature. It returns a formatted timestamp string that changes whenever `trace.json` is modified. The interface treats this as an opaque string for comparison purposes.

**Sources:** [watch_trace.html:43-47](), [watch_trace.html:61-63]()

---

# Page: Perfetto UI Integration

# Perfetto UI Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [watch_trace.html](watch_trace.html)
- [watch_trace.py](watch_trace.py)

</details>



This page documents the integration between the Machine simulator's trace output and Perfetto UI, a professional-grade performance visualization tool. It covers the communication protocol, live-reload functionality, and how to use Perfetto UI to analyze execution traces for performance debugging.

For information on generating traces from the simulator, see [Trace Generation](#7.1). For practical debugging workflows using Perfetto, see [Debugging Workflows and Strategies](#7.5).

---

## Integration Architecture

The Perfetto UI integration uses a browser-based `postMessage` API to communicate between the local web interface and the external Perfetto UI. This architecture enables seamless trace visualization with automatic updates when traces are regenerated.

### Communication Flow

```mermaid
sequenceDiagram
    participant Browser as "watch_trace.html<br/>(Browser)"
    participant Server as "watch_trace.py<br/>:8000"
    participant Perfetto as "ui.perfetto.dev<br/>(Perfetto UI)"
    
    Note over Browser,Perfetto: Initial Load
    Browser->>Server: "GET /"
    Server-->>Browser: "watch_trace.html content"
    Browser->>Server: "GET /trace.json"
    Server-->>Browser: "trace.json binary"
    Browser->>Browser: "Convert to ArrayBuffer"
    
    Note over Browser,Perfetto: Open Perfetto Window
    Browser->>Perfetto: "window.open(ORIGIN)"
    Perfetto-->>Browser: "New window opened"
    
    Note over Browser,Perfetto: PING/PONG Handshake
    loop "Every 50ms"
        Browser->>Perfetto: "postMessage('PING')"
    end
    Perfetto->>Browser: "postMessage('PONG')"
    Browser->>Browser: "Clear PING timer"
    
    Note over Browser,Perfetto: Send Trace
    Browser->>Perfetto: "postMessage({perfetto: {...}})"
    Perfetto->>Perfetto: "Render trace"
    
    Note over Browser,Perfetto: Live Reload Loop
    loop "Every 500ms"
        Browser->>Server: "GET /mtime"
        Server-->>Browser: "Modification timestamp"
        alt "Timestamp changed"
            Browser->>Server: "GET /trace.json"
            Server-->>Browser: "New trace.json"
            Browser->>Perfetto: "postMessage(new buffer)"
            Perfetto->>Perfetto: "Update visualization"
        end
    end
```

Sources: [watch_trace.html:36-130](), [watch_trace.py:1-84]()

### postMessage Protocol

The integration implements a custom protocol over the browser's `postMessage` API defined in `watch_trace.html`:

| Message Direction | Content | Purpose |
|------------------|---------|---------|
| `watch_trace.html` → Perfetto | `"PING"` | Detect when Perfetto UI is ready [watch_trace.html:103-106]() |
| Perfetto → `watch_trace.html` | `"PONG"` | Signal that UI has loaded [watch_trace.html:108-109]() |
| `watch_trace.html` → Perfetto | `{perfetto: {buffer, title, url, keepApiOpen}}` | Send trace data [watch_trace.html:79-89]() |

The handshake ensures the trace is only sent after Perfetto UI has fully loaded:

```mermaid
stateDiagram-v2
    [*] --> "Opening_Window"
    Opening_Window --> "Sending_PING": "window.open() succeeds"
    Opening_Window --> "Popup_Blocked": "window.open() returns null"
    Popup_Blocked --> [*]: "User clicks retry button"
    
    Sending_PING --> "Sending_PING": "No PONG received (50ms timer)"
    Sending_PING --> "Ready": "PONG received"
    Ready --> "Sending_Trace": "Clear timer, remove listener"
    Sending_Trace --> "Polling_Mtime": "sendTrace() complete"
    
    Polling_Mtime --> "Polling_Mtime": "mtime unchanged (500ms)"
    Polling_Mtime --> "Sending_Trace": "mtime changed, fetch new trace"
```

Sources: [watch_trace.html:103-120](), [watch_trace.html:43-73]()

### Live Reload Mechanism

The interface implements automatic trace reloading by polling the modification time of `trace.json` via the `repoll` function:

1. **Initial mtime fetch**: When opening the trace, the current `mtime` is captured by `getMtime()` [watch_trace.html:51]().
2. **Polling loop**: Every 500ms, the interface fetches `/mtime` from the server [watch_trace.html:72]().
3. **Change detection**: If the `newMtime` differs from the stored `mtime`, a new trace is fetched [watch_trace.html:63]().
4. **Update transmission**: The new trace buffer is sent via `sendTrace` to the already-open Perfetto window [watch_trace.html:69]().

This enables a rapid iteration workflow: modify kernel → regenerate trace → automatic visualization update.

Sources: [watch_trace.html:60-73](), [watch_trace.py:29-38]()

---

## Opening Traces in Perfetto

### Using the Web Interface

To open a trace in Perfetto UI:

1. **Start the server**: Run `python watch_trace.py` from the repository root [watch_trace.py:74-84]().
2. **Browser opens automatically**: The `run()` function calls `webbrowser.open("http://localhost:8000")` [watch_trace.py:78]().
3. **Select trace source**: The dropdown in `watch_trace.html` shows `/trace.json` (the default) [watch_trace.html:24-26]().
4. **Click "Open Perfetto"**: This triggers `fetchAndOpen()`, which fetches the trace and opens Perfetto UI [watch_trace.html:30](), [watch_trace.html:128-129]().

```mermaid
graph LR
    RunScript["python watch_trace.py"] --> "Server_Start[HTTP Server :8000]"
    Server_Start --> "Browser_Open[Browser opens localhost:8000]"
    Browser_Open --> "Interface[watch_trace.html UI]"
    Interface --> "Click[User clicks 'Open Perfetto']"
    Click --> "Fetch[Fetch /trace.json]"
    Fetch --> "Open[Open ui.perfetto.dev window]"
    Open --> "Display[Perfetto displays trace]"
    
    Display -.->|"Every 500ms"| Poll["Poll /mtime"]
    Poll -.->|"If changed"| Reload["Reload trace in same window"]
```

Sources: [watch_trace.py:74-84](), [watch_trace.html:128-129]()

### Handling Popup Blockers

If the browser blocks the Perfetto popup window, the `openTrace` function provides fallback handling:

- **Detection**: `window.open()` returns `null` when blocked [watch_trace.html:94]().
- **Visual feedback**: Button background changes to `#f3ca63` (orange) [watch_trace.html:95]().
- **Manual retry**: Button text changes to "Popups blocked, click here to open the trace file" [watch_trace.html:99]().
- **User action**: Clicking the modified button retries the window opening [watch_trace.html:96]().

Sources: [watch_trace.html:94-100]()

### Reopening from Perfetto Sidebar

Perfetto UI includes a sidebar link that reopens traces. When following this link, the URL hash contains `#reopen=/trace.json`:

```mermaid
graph TB
    PerfettoSidebar["Perfetto UI Sidebar Link"] --> HashURL["URL: localhost:8000#reopen=/trace.json"]
    HashURL --> CheckHash["watch_trace.html checks location.hash"]
    CheckHash --> StartsWith["Hash starts with '#reopen='?"]
    StartsWith -->|"Yes"| Extract["Extract trace URL from hash"]
    StartsWith -->|"No"| WaitButton["Wait for button click"]
    Extract --> AutoFetch["Automatically fetchAndOpen()"]
    AutoFetch --> Display["Display in Perfetto"]
```

Sources: [watch_trace.html:123-126](), [watch_trace.html:76-77]()

---

## Perfetto UI Interface Overview

Perfetto UI is a Chrome-based timeline visualizer that displays execution events across multiple parallel tracks. The simulator's trace format maps directly to Perfetto's track model.

### Key Interface Components

| Component | Description | Usage |
|-----------|-------------|-------|
| **Timeline View** | Horizontal time axis showing execution events | Pan with mouse drag, zoom with scroll wheel |
| **Track List** | Left sidebar showing all available tracks | Click to select, expand/collapse hierarchies |
| **Event Details** | Bottom panel showing selected event information | Click any event to view details |
| **Search Bar** | Filter events by name or properties | Press `/` to focus search |
| **Minimap** | Overview of entire trace at top | Click to jump to time regions |

### Navigation Controls

Common keyboard shortcuts for Perfetto UI:

| Action | Shortcut | Description |
|--------|----------|-------------|
| Zoom in | `W` or scroll up | Increase temporal resolution |
| Zoom out | `S` or scroll down | Decrease temporal resolution |
| Pan left/right | `A` / `D` or drag | Move along timeline |
| Select event | Click | Display event details in bottom panel |
| Search | `/` | Open search bar |
| Zoom to selection | Double-click event | Center and zoom to event |

---

## Track Organization

The Machine simulator generates traces with a hierarchical track structure organized by execution engine and scratch space variables.

### Per-Engine Tracks

Each execution engine creates a separate track showing which operations execute in each cycle:

```mermaid
graph TB
    TraceRoot["Trace Root"] --> Core0["Core 0"]
    Core0 --> ALU["ALU Track<br/>12 parallel slots"]
    Core0 --> VALU["VALU Track<br/>6 parallel slots"]
    Core0 --> LOAD["LOAD Track<br/>2 parallel slots"]
    Core0 --> STORE["STORE Track<br/>2 parallel slots"]
    Core0 --> FLOW["FLOW Track<br/>1 slot"]
    Core0 --> DEBUG["DEBUG Track<br/>Debug operations"]
    
    Core0 --> ScratchVars["Scratch Variables Group"]
    ScratchVars --> Var0["scratch[0] changes"]
    ScratchVars --> Var1["scratch[1] changes"]
    ScratchVars --> VarN["scratch[N] changes"]
    
    TraceRoot --> Core1["Core 1<br/>(if N_CORES > 1)"]
    Core1 --> EnginesC1["Similar engine tracks"]
```

Sources: Based on trace generation patterns in the Machine simulator and the `collapsed: false` patching in [watch_trace.py:55-59]().

### Track Naming Conventions

Tracks follow a consistent naming pattern derived from the `trace.json` event names:

| Track Pattern | Example | Meaning |
|--------------|---------|---------|
| `core_{N}` | `core_0` | All activity for core N |
| `core_{N}.{ENGINE}` | `core_0.alu` | Specific engine on core N |
| `core_{N}.{ENGINE}.slot_{S}` | `core_0.alu.slot_3` | Individual slot within engine |
| `core_{N}.scratch[{ADDR}]` | `core_0.scratch[42]` | Value changes for scratch address |

---

## Custom Integration Features

The local proxy server `watch_trace.py` applies custom modifications to Perfetto UI to improve the debugging experience.

### Auto-Expanded Tracks

By default, Perfetto collapses track hierarchies. The proxy modifies the Perfetto JavaScript bundle to expand all tracks automatically:

**Modifications applied** [watch_trace.py:55-59]():
- Changes `collapsed: true` → `collapsed: false`
- Changes `collapsed: !hasHeapProfiles` → `collapsed: false`

This eliminates the need to manually expand each engine and scratch variable track when opening a trace.

### Bug Fix Patch

The proxy applies a fix for a Perfetto UI bug where disposed engines throw errors:

**Original code**:
```javascript
throw new Error(`EngineProxy ${this.tag} was disposed.`);
```

**Patched code** [watch_trace.py:51-54]():
```javascript
return null;
```

This prevents errors when quickly reloading traces, as the old Perfetto instance may still be processing events when the new trace arrives.

### Proxy Architecture

The proxy in `MyHandler` serves two purposes:

1. **Offline operation**: Allows running Perfetto UI locally by proxying the remote UI [watch_trace.py:40-64]().
2. **Custom modifications**: Applies JavaScript patches to improve UX [watch_trace.py:48-59]().

The proxy intercepts requests to `/perfetto/*` and forwards them to `https://ui.perfetto.dev`, modifying responses in transit:

| Request Path | Action |
|-------------|--------|
| `/perfetto/frontend_bundle.js` | Fetch, apply patches, serve modified JS [watch_trace.py:48-59]() |
| `/perfetto/*` (other files) | Fetch and serve unmodified [watch_trace.py:40-47]() |

Sources: [watch_trace.py:40-64]()

---

## Configuration Options

The integration supports two deployment modes configured via the `ORIGIN` constant in `watch_trace.html`:

**Production mode** [watch_trace.html:38]():
```javascript
const ORIGIN = "https://ui.perfetto.dev";
```
- Connects directly to official Perfetto UI.
- Requires internet connection.
- Always uses latest Perfetto version.

**Local proxy mode** [watch_trace.html:37]() (commented out):
```javascript
// const ORIGIN = 'http://localhost:8000/perfetto/';
```
- Routes through local proxy server in `watch_trace.py`.
- Enables offline operation.
- Applies custom modifications described above.

To switch modes, modify the `ORIGIN` constant in `watch_trace.html`.

Sources: [watch_trace.html:37-38](), [watch_trace.py:40-64]()

---

# Page: Debugging Workflows and Strategies

# Debugging Workflows and Strategies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perf_takehome.py](perf_takehome.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page documents practical debugging approaches for optimizing kernel performance in the VLIW SIMD architecture. It covers systematic workflows for identifying bottlenecks, analyzing slot utilization, finding parallelization opportunities, and avoiding common pitfalls during optimization.

For information about enabling and generating traces, see [7.1 Trace Generation](). For details on the visualization tools themselves, see [7.4 Perfetto UI Integration](). For general optimization techniques, see [5.4 Optimization Strategies and Patterns]().

## The Debug-Optimize Iteration Cycle

The fundamental debugging workflow is a tight iteration loop between code generation, execution measurement, and trace analysis:

```mermaid
flowchart TB
    Modify["Modify KernelBuilder.build_kernel()"]
    RunTest["Run test with trace=True"]
    CheckCorrect{"Correctness<br/>check passed?"}
    ViewTrace["Open trace in Perfetto"]
    Identify["Identify bottleneck"]
    Hypothesize["Formulate optimization hypothesis"]
    
    Modify --> RunTest
    RunTest --> CheckCorrect
    CheckCorrect -->|No| DebugCorrectness["Debug using debug.compare<br/>and value_trace"]
    DebugCorrectness --> Modify
    CheckCorrect -->|Yes| ViewTrace
    ViewTrace --> Identify
    Identify --> Hypothesize
    Hypothesize --> Modify
    
    CheckCycles{"Cycles below<br/>target?"}
    CheckCorrect -->|Yes| CheckCycles
    CheckCycles -->|Yes| Done["Complete"]
    CheckCycles -->|No| ViewTrace
```

**Sources:** [perf_takehome.py:241-256](), [perf_takehome.py:175-222]()

## Workflow 1: Baseline Analysis

Start by understanding the current implementation's performance characteristics:

### Step 1: Measure Baseline Performance

```bash
python tests/submission_tests.py CorrectnessTests.test_kernel_cycles
```

This executes `do_kernel_test` with `trace=False` and reports cycle count and speedup versus `BASELINE` (147,734 cycles) [perf_takehome.py:176-178]().

**Key metrics to record:**
- Absolute cycle count.
- Speedup ratio.
- Which performance threshold you're targeting (see [2.2 Performance Benchmarks and Thresholds]()).

### Step 2: Generate Initial Trace

```bash
# Set trace=True in the test call within submission_tests.py or your local script
```

Running `Machine` with `trace=True` [tests/frozen_problem.py:118-121]() generates `trace.json` in Chrome Trace Event Format [tests/frozen_problem.py:151-161]().

### Step 3: Launch Trace Viewer

```bash
python watch_trace.py
# Opens browser to localhost:8000, click "Open Perfetto"
```

The `watch_trace.py` server provides live reload - any regenerated `trace.json` automatically updates in Perfetto [watch_trace.py:74-84]().

**Sources:** [perf_takehome.py:176-178](), [tests/frozen_problem.py:118-161](), [watch_trace.py:74-84]()

## Workflow 2: Identifying Execution Bottlenecks

Use Perfetto timeline visualization to identify where cycles are being wasted. The simulator maps hardware engines to specific "threads" in the trace [tests/frozen_problem.py:168-176]().

```mermaid
graph TB
    subgraph "Perfetto Timeline View (Machine Space)"
        Timeline["Timeline spans cycles 0 to machine.cycle"]
        
        subgraph "Engine Tracks (Core 0)"
            ALU["alu-0 through alu-11<br/>(SLOT_LIMITS['alu'])"]
            VALU["valu-0 through valu-5<br/>(SLOT_LIMITS['valu'])"]
            LOAD["load-0, load-1<br/>(SLOT_LIMITS['load'])"]
            STORE["store-0, store-1<br/>(SLOT_LIMITS['store'])"]
            FLOW["flow-0<br/>(SLOT_LIMITS['flow'])"]
        end
        
        subgraph "Scratch Variable Tracks"
            Vars["DebugInfo.scratch_map<br/>Shows value changes per cycle"]
        end
    end
    
    Analysis["Click on events to see:<br/>- Engine Type (alu, valu, load, etc)<br/>- Instruction Opcode<br/>- Scratch Addresses (e.g. tmp1)"]
    
    Timeline --> ALU
    Timeline --> VALU
    Timeline --> LOAD
    Timeline --> STORE
    Timeline --> FLOW
    Timeline --> Vars
    Timeline --> Analysis
```

### Bottleneck Patterns

| Pattern | Symptom | Root Cause | Solution |
|---------|---------|------------|----------|
| **Sparse slot usage** | Many empty slots in ALU/VALU tracks | Poor VLIW packing in `build()` [perf_takehome.py:51-56]() | Pack multiple operations into same instruction bundle |
| **Load/store saturation** | All load/store slots filled (2/cycle), but ALU mostly idle | Memory bandwidth bottleneck [tests/frozen_problem.py:51-52]() | Use scratch space as a cache, batch memory ops |
| **Sequential ALU operations** | Operations that could be parallel are sequential | Not exploiting instruction-level parallelism | Reorder operations to remove dependencies |
| **Scalar operations on vectors** | ALU slots used where VALU could vectorize | Missing vectorization opportunities | Use `valu` engine with `VLEN=8` SIMD operations [tests/frozen_problem.py:57-78]() |
| **Repeated constant loads** | Multiple `load.const` for same value | `scratch_const()` cache misses | Check `const_map` is being used correctly [perf_takehome.py:70-75]() |

**Sources:** [tests/frozen_problem.py:48-60](), [tests/frozen_problem.py:151-196](), [perf_takehome.py:51-56](), [perf_takehome.py:70-75]()

## Workflow 3: Analyzing VLIW Slot Utilization

The VLIW architecture allows parallel execution within a single cycle. Analyze utilization to maximize parallelism. How many slots each engine can execute per cycle is limited by `SLOT_LIMITS` [tests/frozen_problem.py:68-72]().

### Calculating Slot Efficiency

For each cycle, count how many slots are used versus available:

```
Total Available = 12 (ALU) + 6 (VALU) + 2 (LOAD) + 2 (STORE) + 1 (FLOW) = 23 slots
```

**Low utilization (<30%)** indicates poor instruction packing.

### Identifying Packing Opportunities

The baseline `build()` method uses simple 1-slot-per-instruction packing [perf_takehome.py:51-56]():

```python
# Baseline implementation in KernelBuilder.build()
def build(self, slots: list[tuple[Engine, tuple]], vliw: bool = False):
    instrs = []
    for engine, slot in slots:
        instrs.append({engine: [slot]}) # Wasteful: one instruction per slot
    return instrs
```

**Optimization:** Pack independent operations into the same instruction bundle (a dictionary mapping engine names to lists of slots) [tests/frozen_problem.py:15]().

### Data Dependency Analysis

The simulator's two-phase commit model helps identify what can be packed. Effects of instructions don't take effect until the end of the cycle [tests/frozen_problem.py:70-73]().

```mermaid
sequenceDiagram
    participant Core as "Core.scratch / Machine.mem"
    participant Read as "Read Phase (Cycle N)"
    participant Slots as "All Slots Execute"
    participant Buffers as "scratch_write / mem_write"
    participant Commit as "Commit Phase (End of Cycle N)"
    
    Note over Read: All reads see Cycle N-1 state
    Core->>Read: Read operands
    Read->>Slots: Execute Op
    
    Slots->>Buffers: Store results in temp buffers
    Note over Buffers: Writes don't affect reads<br/>within same cycle
    
    Buffers->>Commit: Apply all writes atomically
    Commit->>Core: Update state for Cycle N+1
```

**Safe to pack:** Operations reading different addresses or writing to different addresses.
**Unsafe to pack:** Operation B reads from address that operation A writes to in the same cycle; B will see the *old* value [tests/frozen_problem.py:70-73]().

**Sources:** [perf_takehome.py:51-56](), [tests/frozen_problem.py:15](), [tests/frozen_problem.py:48-55](), [tests/frozen_problem.py:70-73]()

## Workflow 4: Vectorization Analysis

The `valu` engine provides SIMD operations on `VLEN=8` elements [tests/frozen_problem.py:57-78]().

### Vectorization Strategy

```mermaid
flowchart LR
    subgraph "Scalar Approach (alu)"
        S1["For i in range(256):<br/>  load one element<br/>  process element<br/>  store one element"]
        S2["256 loop iterations<br/>256 loads<br/>256 stores"]
    end
    
    subgraph "Vector Approach (valu)"
        V1["For i in range(0, 256, 8):<br/>  vload 8 elements<br/>  valu process 8 elements<br/>  vstore 8 elements"]
        V2["32 loop iterations<br/>32 vloads (8x throughput)<br/>32 vstores (8x throughput)"]
    end
    
    S1 --> S2
    V1 --> V2
    S2 -.->|"8x improvement"| V2
```

### VALU Operations Available

| Operation | Syntax | Semantics |
|-----------|--------|-----------|
| `vbroadcast` | `("vbroadcast", dest, src)` | Broadcast scalar `src` to vector `dest[0..7]` [tests/frozen_problem.py:310-312]() |
| Vector arithmetic | `(op, dest, a1, a2)` | Element-wise: `dest[i] = a1[i] op a2[i]` [tests/frozen_problem.py:273-281]() |
| `vload` | `("vload", dest, addr)` | Load 8 words from `mem[addr..addr+7]` [tests/frozen_problem.py:254-257]() |
| `vstore` | `("vstore", addr, src)` | Store 8 words to `mem[addr..addr+7]` [tests/frozen_problem.py:263-267]() |

**Key constraint:** Vector operations require contiguous scratch addresses. Use `alloc_scratch(length=VLEN)` to allocate vector registers [perf_takehome.py:61-68]().

**Sources:** [tests/frozen_problem.py:57-78](), [tests/frozen_problem.py:254-312](), [perf_takehome.py:61-68]()

## Workflow 5: Correctness Debugging with Debug Instructions

When optimizations break correctness, use `debug` instructions to pinpoint divergence from the reference implementation.

### Debug Infrastructure

The simulator supports `debug` engine instructions that validate against a `value_trace` [tests/frozen_problem.py:366-382]().

```python
# In KernelBuilder.build_kernel
body.append(("debug", ("compare", tmp_idx, (round, i, "idx"))))
```

This checks `core.scratch[tmp_idx]` against `value_trace[(round, i, "idx")]` populated by `reference_kernel2` [perf_takehome.py:140]().

### Debug Workflow

```mermaid
flowchart TB
    TestFail["Test fails:<br/>Assertion Error in do_kernel_test"]
    
    CheckError{"Error type?"}
    TestFail --> CheckError
    
    CheckError -->|"Incorrect result on round X"| MemMismatch["Memory mismatch<br/>at pause point"]
    CheckError -->|"Assert failed at pc=Y"| DebugCompare["Debug compare failed<br/>in step execution"]
    
    MemMismatch --> FindKey["Identify which round/batch<br/>first diverges"]
    FindKey --> AddDebug["Add debug.compare at<br/>intermediate steps"]
    
    DebugCompare --> Inspect["Inspect key from traceback:<br/>(round, i, 'stage')"]
    Inspect --> CheckScratch["Check scratch variable<br/>values in trace"]
    
    AddDebug --> Rerun["Rerun test"]
    CheckScratch --> Fix["Fix instruction generation"]
```

**Tip:** The `debug` engine is ignored by the submission simulator if you follow the recruitment rules, so they don't affect performance measurement cycles [perf_takehome.py:123-124]().

**Sources:** [tests/frozen_problem.py:366-382](), [perf_takehome.py:137-166](), [perf_takehome.py:123-124]()

## Common Pitfalls and Solutions

### Pitfall 1: Exceeding Scratch Space

**Symptom:** `AssertionError: Out of scratch space` in `alloc_scratch` [perf_takehome.py:67]().

**Cause:** More than `SCRATCH_SIZE` (1536) words allocated [tests/frozen_problem.py:60]().

**Solution:**
- Reuse scratch addresses for temporary values with non-overlapping lifetimes.
- Use fewer vector registers (each requires `VLEN=8` words).

### Pitfall 2: Violating Slot Limits

**Symptom:** `AssertionError` in `step()` when checking `len(slots) <= SLOT_LIMITS[name]` [tests/frozen_problem.py:383]().

**Cause:** Too many operations packed into single engine in one instruction bundle.

**Limits [tests/frozen_problem.py:48-55]():**
- ALU: 12 slots
- VALU: 6 slots  
- LOAD: 2 slots
- STORE: 2 slots
- FLOW: 1 slot

### Pitfall 3: Forgetting Pause Instructions

**Symptom:** `do_kernel_test` hangs or produces incorrect comparison at intermediate steps.

**Cause:** Number of `pause` instructions doesn't match `yield` statements in `reference_kernel2` [perf_takehome.py:118-122]().

**Required pauses [perf_takehome.py:122, 174]():**
1. After loading header variables.
2. After the main loop body completes.

**Sources:** [perf_takehome.py:67](), [tests/frozen_problem.py:60](), [tests/frozen_problem.py:48-55](), [tests/frozen_problem.py:383](), [perf_takehome.py:118-174]()

## Interpreting Performance Results

### Performance Ladder Reference

| Threshold | Cycles | Speedup | Description |
|-----------|--------|---------|-------------|
| Baseline | 147,734 | 1.0x | Unoptimized scalar [perf_takehome.py:176]() |
| Updated Starting Point | 18,532 | 7.97x | Basic improvements [perf_takehome.py:221]() |
| Claude Opus 4 | 2,164 | 68.3x | Many hours optimization [perf_takehome.py:224]() |
| **Recruitment Gate** | **1,487** | **99.3x** | Claude Opus 4.5 11hr [perf_takehome.py:236]() |
| Best Known | 1,363 | 108.4x | Claude Opus 4.5 improved [perf_takehome.py:239]() |

**Goal:** Beat 1,487 cycles to qualify for recruitment review [perf_takehome.py:236]().

**Sources:** [perf_takehome.py:176-239]()

---

# Page: Developer Reference

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

# Page: Repository Structure

# Repository Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [Readme.md](Readme.md)

</details>



This page documents the file and directory organization of the performance take-home repository. It explains what each file does, the distinction between development files (root level) and submission files (`tests/` directory), and the module architecture.

## Overview

The repository follows a simple two-tier structure: root-level files for development and iteration, and a `tests/` directory containing frozen implementations for official submission evaluation. This separation ensures that performance improvements can be fairly measured against a fixed simulator implementation.

```mermaid
graph TB
    subgraph Root["Root Directory (Development)"]
        Readme["Readme.md<br/>Overview & Benchmarks"]
        PerfTake["perf_takehome.py<br/>KernelBuilder + Dev Tests"]
        Problem["problem.py<br/>Machine Simulator<br/>(Development Version)"]
        WatchPy["watch_trace.py<br/>Trace Visualization Server"]
        WatchHTML["watch_trace.html<br/>Trace UI"]
    end
    
    subgraph Tests["tests/ Directory (Submission)"]
        FrozenProblem["frozen_problem.py<br/>Machine Simulator<br/>(Frozen Copy)"]
        SubmissionTests["submission_tests.py<br/>Official Test Suite"]
    end
    
    subgraph Generated["Generated Output"]
        TraceJSON["trace.json<br/>Trace Data"]
    end
    
    PerfTake -->|imports| Problem
    SubmissionTests -->|imports| FrozenProblem
    SubmissionTests -->|imports| PerfTake
    PerfTake -.->|generates| TraceJSON
    WatchPy -->|serves| TraceJSON
    WatchPy -->|serves| WatchHTML
    
    style PerfTake stroke-width:2px
    style Problem stroke-width:2px
    style FrozenProblem stroke-width:2px
    style SubmissionTests stroke-width:2px
```

**Sources:** [Readme.md:1-21](), [perf_takehome.py:1-273](), [problem.py:1-6](), [tests/submission_tests.py:1-20]()

## Root-Level Files

### Core Implementation Files

| File | Purpose | Key Contents |
|------|---------|--------------|
| `perf_takehome.py` | Primary optimization target and development tests | `KernelBuilder` class, `do_kernel_test()`, `Tests` class |
| `problem.py` | Development simulator and problem definition | `Machine` class, `Tree`, `Input`, reference implementations |

#### perf_takehome.py

[perf_takehome.py:1-273]() is the central file for this performance challenge. It contains:

- **`KernelBuilder` class** [perf_takehome.py:37-172](): The optimization target. Developers modify the `build_kernel()` method to generate more efficient instruction sequences.
- **`do_kernel_test()` function** [perf_takehome.py:175-222](): Test harness that runs a kernel, compares against the reference implementation, and reports cycle count.
- **`Tests` class** [perf_takehome.py:225-256](): Development test suite including `test_kernel_cycles()` and `test_kernel_trace()`.
- **`BASELINE` constant** [perf_takehome.py:173](): The baseline cycle count (147,734 cycles) used for speedup calculations.

The file imports from `problem.py` to use the development simulator during iteration.

#### problem.py

[problem.py:1-569]() contains the machine simulator and problem definition:

- **`Machine` class** [problem.py:64-402](): The VLIW SIMD simulator that executes instruction bundles. This is the development version that can be modified for debugging.
- **`Tree` and `Input` classes** [problem.py:405-436](): Data structures representing the tree traversal problem.
- **`HASH_STAGES` constant** [problem.py:439-446](): The hash function stages that define the computation.
- **`reference_kernel()` and `reference_kernel2()` functions** [problem.py:467-568](): Ground truth implementations for correctness validation.
- **`build_mem_image()` function** [problem.py:487-513](): Serializes problem data into flat memory layout.

**Sources:** [perf_takehome.py:1-273](), [problem.py:1-569]()

### Visualization Files

| File | Purpose | Execution |
|------|---------|-----------|
| `watch_trace.py` | HTTP server for trace visualization | Run separately with `python watch_trace.py` |
| `watch_trace.html` | Web interface for Perfetto integration | Served by `watch_trace.py` |

These files implement the trace visualization system. They are not imported by other modules but run as standalone tools.

**Sources:** [perf_takehome.py:262-266](), comments in [problem.py:151-159]()

### Documentation and Config

**`Readme.md`** [Readme.md:1-21]() provides:
- Repository overview and purpose
- Performance benchmark ladder (from 2164 cycles down to 1363 cycles)
- Recruitment threshold (1487 cycles)
- Quick start instructions (`python tests/submission_tests.py`)

**`.gitignore`** [gitignore:1-5]() ensures that generated trace data (`trace.json`), python cache files, and system-specific files like `.DS_Store` are not tracked.

**Sources:** [Readme.md:1-21](), [.gitignore:1-5]()

## tests/ Directory

The `tests/` directory contains the official submission evaluation infrastructure:

### frozen_problem.py

[tests/frozen_problem.py:1-569]() is a frozen copy of `problem.py` that ensures fair evaluation. Key characteristics:

- **Identical implementation**: The code is byte-for-byte identical to `problem.py` at the time it was frozen.
- **Used by submission tests**: `submission_tests.py` imports from this file, not from the root-level `problem.py`.
- **Cannot be modified**: Any changes to the root-level `problem.py` do not affect submission evaluation. LLMs are specifically warned not to modify this folder [Readme.md:25-30]().

### submission_tests.py

[tests/submission_tests.py:1-120]() is the official test suite that determines performance thresholds:

**Import structure:**
```python
from frozen_problem import (
    Machine, build_mem_image, reference_kernel2,
    Tree, Input, N_CORES, VLEN
)
from perf_takehome import KernelBuilder
```

**Test organization:**
- **`CorrectnessTests`** [tests/submission_tests.py:57-60](): Validates correctness with 8 random test cases.
- **`SpeedTests`** [tests/submission_tests.py:76-116](): Performance threshold tests matching the benchmark ladder.

**Key features:**
- **`@lru_cache` on `kernel_builder()`** [tests/submission_tests.py:23-27](): Caches compiled kernels by dimensions.
- **`@lru_cache` on `cycles()`** [tests/submission_tests.py:66-73](): Ensures cycle count is measured only once.
- **Disabled debug features** [tests/submission_tests.py:41-42](): `enable_pause = False`, `enable_debug = False` for clean measurements.

**Sources:** [tests/submission_tests.py:1-120](), [tests/frozen_problem.py:1-569](), [Readme.md:25-30]()

## Module Dependencies

```mermaid
graph LR
    subgraph "Development Workflow"
        PTDev["perf_takehome.py<br/>(development)"]
        ProbDev["problem.py<br/>(development)"]
        PTDev -->|imports| ProbDev
    end
    
    subgraph "Submission Workflow"
        PTSub["perf_takehome.py<br/>(KernelBuilder only)"]
        SubTests["tests/submission_tests.py"]
        FrozenProb["tests/frozen_problem.py"]
        SubTests -->|imports KernelBuilder| PTSub
        SubTests -->|imports Machine, etc| FrozenProb
    end
    
    subgraph "Visualization Workflow"
        Trace["trace.json"]
        WatchServer["watch_trace.py"]
        WatchUI["watch_trace.html"]
        PTDev -.->|trace=True generates| Trace
        WatchServer -->|serves| Trace
        WatchServer -->|serves| WatchUI
    end
```

**Import relationships:**

1. **Development execution**: `perf_takehome.py` imports from `problem.py` [perf_takehome.py:20-34]().
2. **Submission execution**: `tests/submission_tests.py` imports `KernelBuilder` from `perf_takehome.py` but imports the simulator from `tests/frozen_problem.py` [tests/submission_tests.py:1-20]().
3. **No circular dependencies**: The structure is strictly hierarchical.

**Sources:** [perf_takehome.py:20-34](), [tests/submission_tests.py:1-20]()

## Development vs Submission Workflows

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant PTDev as perf_takehome.py<br/>(Dev Tests)
    participant ProbDev as problem.py<br/>(Dev Simulator)
    participant SubTests as submission_tests.py
    participant FrozenProb as frozen_problem.py<br/>(Frozen Simulator)
    
    Note over Dev,FrozenProb: Development Iteration
    Dev->>PTDev: Modify KernelBuilder.build_kernel()
    Dev->>PTDev: python perf_takehome.py Tests.test_kernel_cycles
    PTDev->>ProbDev: Import Machine, reference_kernel2
    PTDev->>ProbDev: Execute generated instructions
    ProbDev-->>PTDev: Cycle count, trace output
    PTDev-->>Dev: Development feedback
    
    Note over Dev,FrozenProb: Official Submission
    Dev->>SubTests: python tests/submission_tests.py
    SubTests->>PTDev: Import KernelBuilder (build_kernel only)
    SubTests->>FrozenProb: Import Machine, reference_kernel2
    SubTests->>FrozenProb: Execute on frozen simulator
    FrozenProb-->>SubTests: Official cycle count
    SubTests-->>Dev: Pass/fail vs thresholds
```

**Development workflow** uses:
- `perf_takehome.py` with `problem.py` imports.
- Can enable tracing: `do_kernel_test(..., trace=True)` [perf_takehome.py:243]().
- Can enable debug prints: `machine.prints = True` [perf_takehome.py:202]().
- Yields intermediate states for validation [perf_takehome.py:203-212]().

**Submission workflow** uses:
- `tests/submission_tests.py` with `frozen_problem.py` imports.
- Disables pause and debug: `machine.enable_pause = False`, `machine.enable_debug = False` [tests/submission_tests.py:41-42]().
- Only validates final memory state [tests/submission_tests.py:48-52]().
- Caches kernel compilation to measure pure execution time [tests/submission_tests.py:23-27]().

**Sources:** [perf_takehome.py:175-222](), [tests/submission_tests.py:30-54]()

## Key File Relationships

The following diagram shows the execution flow and data dependencies:

```mermaid
graph TB
    subgraph Input["Problem Input Generation"]
        TreeGen["Tree.generate()"]
        InputGen["Input.generate()"]
        MemImage["build_mem_image()"]
    end
    
    subgraph Compilation["Instruction Generation"]
        KB["KernelBuilder"]
        BuildKernel["build_kernel()"]
        KB --> BuildKernel
    end
    
    subgraph Execution["Simulator Execution"]
        MachineInit["Machine.__init__()"]
        MachineRun["Machine.run()"]
        MachineInit --> MachineRun
    end
    
    subgraph Validation["Correctness Check"]
        RefKernel["reference_kernel2()"]
        Compare["Memory Comparison"]
        RefKernel --> Compare
    end
    
    TreeGen --> MemImage
    InputGen --> MemImage
    TreeGen --> BuildKernel
    InputGen --> BuildKernel
    
    BuildKernel -->|instrs| MachineInit
    MemImage -->|mem_dump| MachineInit
    MemImage -->|ref_mem| RefKernel
    
    MachineRun -->|machine.mem| Compare
    RefKernel -->|ref_mem| Compare
    Compare -->|assertion| Result["Test Pass/Fail"]
    MachineRun -->|machine.cycle| CycleCount["Performance Metric"]
```

**Key data flows:**

1. **Problem generation**: `Tree.generate()` [problem.py:409]() and `Input.generate()` [problem.py:426]() create test data.
2. **Serialization**: `build_mem_image()` [problem.py:487]() converts to flat memory.
3. **Compilation**: `KernelBuilder.build_kernel()` [perf_takehome.py:47]() generates instruction list.
4. **Execution**: `Machine` [problem.py:64]() runs instructions on memory.
5. **Validation**: Results compared against `reference_kernel2()` [problem.py:542]() output.

**Sources:** [perf_takehome.py:175-222](), [tests/submission_tests.py:30-54](), [problem.py:487-568]()

## Constants and Configuration

Key constants are defined in `problem.py` and mirrored in `frozen_problem.py`:

| Constant | Value | Purpose | Location |
|----------|-------|---------|----------|
| `SLOT_LIMITS` | `{"alu": 12, "valu": 6, ...}` | Engine slot capacities | [problem.py:48-55]() |
| `VLEN` | `8` | SIMD vector length | [problem.py:57]() |
| `N_CORES` | `1` | Number of cores (always 1 in this version) | [problem.py:59]() |
| `SCRATCH_SIZE` | `1536` | Scratch space per core (words) | [problem.py:60]() |
| `HASH_STAGES` | 6 stages | Hash function definition | [problem.py:439-446]() |
| `BASELINE` | `147734` | Baseline cycle count | [perf_takehome.py:173]() |

**Sources:** [problem.py:48-60](), [problem.py:439-446](), [perf_takehome.py:173]()

## Generated Files

The repository generates output files during execution:

**`trace.json`**: Generated when running with `trace=True` [perf_takehome.py:243]():
- Format: Chrome Trace Event Format.
- Contains: Per-cycle slot execution, scratch variable updates.
- Size: Can be large for full runs.
- Used by: Perfetto UI via `watch_trace.py` server.
- Ignored by Git: Listed in `.gitignore` [gitignore:1]().

This file is created by `Machine.__del__()` [problem.py:399-402]() and is not version-controlled.

**Sources:** [problem.py:151-196](), [problem.py:399-402](), [.gitignore:1]()

---

# Page: API Reference

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perf_takehome.py](perf_takehome.py)
- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page provides a quick reference for the key classes, functions, constants, and type definitions used throughout the codebase. For conceptual explanations of the machine architecture, see [Machine Architecture](#4). For details on optimization strategies in KernelBuilder, see [Kernel Builder - The Optimization Target](#5).

## Overview

The API is organized into three main modules:
- **problem.py**: Contains the simulator (`Machine`), data structures (`Tree`, `Input`), and reference implementations. [problem.py:1-570]()
- **frozen_problem.py**: Identical frozen copy of `problem.py` used for testing to ensure a stable evaluation environment. [tests/frozen_problem.py:1-570]()
- **perf_takehome.py**: Contains the `KernelBuilder` class and the primary optimization target `build_kernel`. [perf_takehome.py:40-172]()

## Core Type System

### Type Aliases and Enums

| Type | Definition | Purpose |
|------|------------|---------|
| `Engine` | `Literal["alu", "load", "store", "flow"]` | Valid engine types for instructions. [problem.py:14]() |
| `Instruction` | `dict[Engine, list[tuple]]` | A single VLIW instruction bundle mapping engines to slot lists. [problem.py:15]() |

**Sources:** [problem.py:14-15](), [tests/frozen_problem.py:14-15]()

### CoreState Enum

```python
class CoreState(Enum):
    RUNNING = 1   # Core is actively executing
    PAUSED = 2    # Core is paused at a pause instruction
    STOPPED = 3   # Core has halted or reached end of program
```

**Sources:** [problem.py:18-22](), [tests/frozen_problem.py:18-22]()

### Type Relationships Diagram

```mermaid
graph TB
    subgraph "Type System"
        Engine["Engine<br/>(Type Alias)"]
        Instruction["Instruction<br/>(Type Alias)"]
        CoreState["CoreState<br/>(Enum)"]
    end
    
    subgraph "Instruction Structure"
        InstrDict["dict[Engine, list[tuple]]"]
        EngineKey["'alu' | 'valu' | 'load' | 'store' | 'flow' | 'debug'"]
        SlotList["[slot1, slot2, ...]"]
        Slot["tuple of operation args"]
    end
    
    subgraph "Core State Machine"
        Running["RUNNING = 1"]
        Paused["PAUSED = 2"]
        Stopped["STOPPED = 3"]
    end
    
    Instruction --> InstrDict
    InstrDict --> EngineKey
    InstrDict --> SlotList
    SlotList --> Slot
    
    CoreState --> Running
    CoreState --> Paused
    CoreState --> Stopped
```

**Sources:** [problem.py:14-22](), [tests/frozen_problem.py:14-22]()

## Configuration Constants

### Machine Configuration

| Constant | Value | Description |
|----------|-------|-------------|
| `SLOT_LIMITS` | `{"alu": 12, "valu": 6, "load": 2, "store": 2, "flow": 1, "debug": 64}` | Maximum slots per engine per cycle. [problem.py:48-55]() |
| `VLEN` | `8` | Vector length for SIMD operations. [problem.py:57]() |
| `N_CORES` | `1` | Number of cores (fixed in this version). [problem.py:59]() |
| `SCRATCH_SIZE` | `1536` | Size of scratch space per core in words. [problem.py:60]() |
| `BASE_ADDR_TID` | `100000` | Base thread ID for trace visualization. [problem.py:61]() |

**Sources:** [problem.py:48-61](), [tests/frozen_problem.py:48-61]()

### Hash Configuration

| Constant | Value | Description |
|----------|-------|-------------|
| `HASH_STAGES` | List of 6 tuples | Defines the `myhash` function stages: `(op1, val1, op2, op3, val3)`. [problem.py:439-446]() |

**Sources:** [problem.py:439-446](), [tests/frozen_problem.py:439-446]()

### Performance Baseline

| Constant | Value | Description |
|----------|-------|-------------|
| `BASELINE` | `147734` | Baseline cycle count for speedup calculation. [perf_takehome.py:176]() |

**Sources:** [perf_takehome.py:176]()

## Data Classes

### Core

Represents a single execution core with its state. [problem.py:25-30]()

```python
@dataclass
class Core:
    id: int                      # Core identifier
    scratch: list[int]           # Scratch space array (SCRATCH_SIZE words)
    trace_buf: list[int]         # Buffer for trace_write instructions
    pc: int = 0                  # Program counter
    state: CoreState = CoreState.RUNNING  # Current execution state
```

**Sources:** [problem.py:25-30](), [tests/frozen_problem.py:25-30]()

### DebugInfo

Container for debugging metadata passed to Machine. [problem.py:34-41]()

```python
@dataclass
class DebugInfo:
    scratch_map: dict[int, (str, int)]  # Maps scratch addr -> (name, length)
```

**Sources:** [problem.py:34-41](), [tests/frozen_problem.py:34-41]()

### Tree

Represents an implicit balanced binary tree structure. [problem.py:406-418]()

```python
@dataclass
class Tree:
    height: int          # Tree height (0-indexed)
    values: list[int]    # Node values (length = 2^(height+1) - 1)
    
    @staticmethod
    def generate(height: int) -> Tree
```

**Sources:** [problem.py:406-418](), [tests/frozen_problem.py:406-418]()

### Input

Represents a batch of traversal inputs. [problem.py:422-436]()

```python
@dataclass
class Input:
    indices: list[int]   # Current node indices
    values: list[int]    # Current hash values
    rounds: int          # Number of traversal rounds
    
    @staticmethod
    def generate(forest: Tree, batch_size: int, rounds: int) -> Input
```

**Sources:** [problem.py:422-436](), [tests/frozen_problem.py:422-436]()

## Core Classes

### Machine

The VLIW SIMD architecture simulator. [problem.py:64-403]()

#### Constructor

```python
Machine(
    mem_dump: list[int],          # Initial memory image
    program: list[Instruction],   # Instruction sequence
    debug_info: DebugInfo,        # Debug metadata
    n_cores: int = 1,             # Number of cores
    scratch_size: int = SCRATCH_SIZE,  # Scratch space size
    trace: bool = False,          # Enable trace generation
    value_trace: dict[Any, int] = {}   # Reference values for debug compare
)
```

#### Key Methods

| Method | Purpose |
|--------|---------|
| `run()` | Execute until all cores stop or pause. [problem.py:197-217]() |
| `step(instr, core)` | Execute one instruction bundle on a core. [problem.py:352-397]() |
| `alu(core, op, dest, a1, a2)` | Execute scalar ALU operation. [problem.py:219-252]() |
| `valu(core, *slot)` | Execute vector ALU operation. [problem.py:254-267]() |
| `load(core, *slot)` | Execute load operation. [problem.py:269-286]() |
| `store(core, *slot)` | Execute store operation. [problem.py:288-298]() |
| `flow(core, *slot)` | Execute control flow operation. [problem.py:300-335]() |
| `setup_trace()` | Initialize trace file generation. [problem.py:151-195]() |

**Sources:** [problem.py:64-403](), [tests/frozen_problem.py:64-403]()

### KernelBuilder

Builder class for generating kernel instructions. [perf_takehome.py:40-172]()

#### Key Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `alloc_scratch` | `(name=None, length=1) -> int` | Allocate scratch space, returns address. [perf_takehome.py:61-68]() |
| `scratch_const` | `(val, name=None) -> int` | Allocate and initialize constant, returns address. [perf_takehome.py:70-75]() |
| `add` | `(engine, slot)` | Add instruction to sequence. [perf_takehome.py:58-59]() |
| `build` | `(slots, vliw=False) -> list[Instruction]` | Convert slot list to instructions. [perf_takehome.py:51-56]() |
| `build_hash` | `(val_hash_addr, tmp1, tmp2, round, i) -> list` | Generate hash computation slots. [perf_takehome.py:77-86]() |
| `build_kernel` | `(forest_height, n_nodes, batch_size, rounds)` | Main optimization target. [perf_takehome.py:88-172]() |

**Sources:** [perf_takehome.py:37-172]()

### Class Interaction Diagram

```mermaid
graph TB
    subgraph "Kernel Generation"
        KB["KernelBuilder"]
        BuildKernel["build_kernel()"]
        AllocScratch["alloc_scratch()"]
        ScratchConst["scratch_const()"]
        BuildHash["build_hash()"]
        Add["add()"]
    end
    
    subgraph "Simulator"
        Machine["Machine"]
        Run["run()"]
        Step["step()"]
        ALU["alu()"]
        VALU["valu()"]
        Load["load()"]
        Store["store()"]
        Flow["flow()"]
    end
    
    subgraph "Data Structures"
        Core["Core"]
        Tree["Tree"]
        Input["Input"]
        DebugInfo["DebugInfo"]
    end
    
    subgraph "Program Flow"
        BuildKernel --> AllocScratch
        BuildKernel --> ScratchConst
        BuildKernel --> BuildHash
        BuildKernel --> Add
        KB --> DebugInfo
    end
    
    Machine --> Core
    Machine --> DebugInfo
    Run --> Step
    Step --> ALU
    Step --> VALU
    Step --> Load
    Step --> Store
    Step --> Flow
    
    KB -.generates.-> Machine
    Tree -.defines.-> Machine
    Input -.configures.-> Machine
```

**Sources:** [perf_takehome.py:37-172](), [problem.py:64-403]()

## Utility Functions

### myhash

32-bit hash function implementation. [problem.py:449-464]()

```python
def myhash(a: int) -> int:
    """
    A simple 32-bit hash function.
    Applies 6 stages of mixing operations defined in HASH_STAGES.
    """
```

**Sources:** [problem.py:449-464](), [tests/frozen_problem.py:449-464]()

### reference_kernel2

Reference implementation operating on flat memory with yielding for correctness validation. [problem.py:535-568]()

```python
def reference_kernel2(
    mem: list[int],
    trace: dict[Any, int] = {}
) -> Generator[list[int], None, None]:
    """
    Reference implementation on flat memory layout.
    Yields memory state at pause points for validation.
    """
```

**Sources:** [problem.py:535-568](), [tests/frozen_problem.py:535-568]()

### build_mem_image

Serializes Tree and Input into flat memory layout. [problem.py:487-513]()

```python
def build_mem_image(t: Tree, inp: Input) -> list[int]:
    """
    Build flat memory image with header containing rounds, 
    n_nodes, and pointers to data arrays.
    """
```

**Sources:** [problem.py:487-513](), [tests/frozen_problem.py:487-513]()

## Instruction Format Reference

### ALU Operations

| Operation | Format | Description |
|-----------|--------|-------------|
| Arithmetic | `("+", dest, a1, a2)` | Also: `-`, `*`, `//`, `%`. [problem.py:219-252]() |
| Bitwise | `("^", dest, a1, a2)` | Also: `&`, `|`, `<<`, `>>`. [problem.py:219-252]() |
| Comparison | `("<", dest, a1, a2)` | Also: `==`. [problem.py:219-252]() |

### LOAD Operations

| Operation | Format | Description |
|-----------|--------|-------------|
| Load | `("load", dest, addr)` | Load from `mem[scratch[addr]]`. [problem.py:270]() |
| Vector Load | `("vload", dest, addr)` | Load `VLEN` contiguous words. [problem.py:278]() |
| Constant | `("const", dest, val)` | Load immediate constant. [problem.py:284]() |

**Sources:** [problem.py:219-335](), [tests/frozen_problem.py:219-335]()

## Memory Layout Convention

The `build_mem_image` function creates a standard memory layout:

```mermaid
graph LR
    subgraph "Memory Layout"
        Header["Header<br/>[0:7]"]
        ForestValues["Tree Values<br/>[7:7+n_nodes]"]
        InpIndices["Input Indices<br/>[...:..+batch_size]"]
        InpValues["Input Values<br/>[...:..+batch_size]"]
        ExtraRoom["Extra Space<br/>[...:end]"]
    end
    
    subgraph "Header Contents"
        H0["mem[0] = rounds"]
        H1["mem[1] = n_nodes"]
        H2["mem[2] = batch_size"]
        H3["mem[3] = forest_height"]
        H4["mem[4] = forest_values_p"]
        H5["mem[5] = inp_indices_p"]
        H6["mem[6] = inp_values_p"]
        H7["mem[7] = extra_room_p"]
    end
    
    Header --> H0
    Header --> H1
    Header --> H2
    Header --> H3
    Header --> H4
    Header --> H5
    Header --> H6
    Header --> H7
    
    H4 -.points to.-> ForestValues
    H5 -.points to.-> InpIndices
    H6 -.points to.-> InpValues
    H7 -.points to.-> ExtraRoom
```

**Sources:** [problem.py:487-513](), [tests/frozen_problem.py:487-513]()

## Machine Execution Model

```mermaid
graph TB
    subgraph "Cycle Execution"
        FetchInstr["Fetch Instruction Bundle<br/>program[pc]"]
        ReadPhase["Read Phase<br/>All slots read from<br/>scratch/mem state"]
        ExecEngines["Execute Engines in Parallel<br/>alu, valu, load, store, flow"]
        WriteBuffer["Buffer Writes<br/>scratch_write, mem_write"]
        CommitPhase["Commit Phase<br/>Apply all writes atomically"]
        IncrCycle["Increment cycle counter"]
    end
    
    FetchInstr --> ReadPhase
    ReadPhase --> ExecEngines
    ExecEngines --> WriteBuffer
    WriteBuffer --> CommitPhase
    CommitPhase --> IncrCycle
    IncrCycle --> FetchInstr
    
    ExecEngines -.constraint.-> SlotLimit["Respects SLOT_LIMITS<br/>per engine"]
    ReadPhase -.ensures.-> Determinism["Deterministic parallel execution<br/>reads see cycle-start state"]
```

**Sources:** [problem.py:197-217](), [problem.py:352-397]()

---

# Page: Configuration and Development Setup

# Configuration and Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [Readme.md](Readme.md)

</details>



## Purpose and Scope

This page documents the repository configuration, development workflows, and maintenance practices for working with the performance take-home codebase. It covers version control settings, iteration cycles for optimization work, and best practices for managing generated artifacts.

For information about running tests and interpreting results, see [Running and Interpreting Tests](#6.4). For trace generation and visualization workflows, see [Performance Analysis and Debugging](#7).

---

## Version Control Configuration

### .gitignore Structure

The repository uses a minimal `.gitignore` configuration that excludes generated artifacts and development environment files to ensure the repository remains clean and focused on source code:

| Pattern | Purpose | Related System |
|---------|---------|----------------|
| `trace.json` | Excludes trace files generated by the simulator | Trace visualization system ([Performance Analysis and Debugging](#7)) |
| `**/*.pyc` | Excludes Python bytecode files | Python interpreter cache |
| `.hypothesis` | Excludes Hypothesis framework cache | Testing framework ([Testing Framework](#6)) |
| `.DS_Store` | Excludes macOS filesystem metadata | Operating system artifacts |

**Sources:** [.gitignore:1-5]()

### Version Control Philosophy

```mermaid
graph TB
    subgraph "Version Controlled"
        Source["Source Code<br/>perf_takehome.py<br/>problem.py<br/>frozen_problem.py"]
        Tests["Test Suite<br/>tests/submission_tests.py"]
        Tools["Visualization Tools<br/>watch_trace.py<br/>watch_trace.html"]
        Docs["Documentation<br/>Readme.md"]
    end
    
    subgraph "Excluded from Version Control"
        Trace["trace.json<br/>Generated traces"]
        Pyc["*.pyc files<br/>Python bytecode"]
        Hypo[".hypothesis/<br/>Test framework cache"]
        OS[".DS_Store<br/>OS metadata"]
    end
    
    Source --> Pyc
    Tests --> Pyc
    Tests --> Hypo
    
    Source -.->|"generates"| Trace
    
    style Source fill:#f9f9f9
    style Tests fill:#f9f9f9
    style Tools fill:#f9f9f9
    style Docs fill:#f9f9f9
```

**Diagram: Version Control Boundaries**

The repository maintains a clean separation between source code and generated artifacts. All generated files can be recreated from source, so they are excluded from version control to prevent merge conflicts and repository bloat.

**Sources:** [.gitignore:1-5]()

---

## Development Workflows

### Optimization Iteration Cycle

The primary development workflow for this repository is the optimization iteration cycle, where developers repeatedly modify the kernel builder and test performance. The goal is to reduce the cycle count from the baseline (~147,734 cycles) toward the performance thresholds set by various Claude models.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Editor as "perf_takehome.py"
    participant Tests as "submission_tests.py"
    participant Results as "Test Results"
    
    Note over Dev,Results: Optimization Iteration
    
    Dev->>Editor: Edit KernelBuilder.build_kernel()
    Dev->>Tests: Run python tests/submission_tests.py
    
    Tests->>Tests: Execute CorrectnessTests
    Tests->>Results: Report correctness status
    
    alt Correctness Pass
        Tests->>Tests: Execute SpeedTests
        Tests->>Results: Report cycle counts<br/>and speedup factors
        
        Results->>Dev: Display performance metrics
        
        alt Below 1487 cycles
            Dev->>Dev: Email performance-recruiting@anthropic.com
        else Above threshold
            Dev->>Editor: Identify bottlenecks<br/>Try new optimization
        end
    else Correctness Fail
        Results->>Dev: Display assertion error
        Dev->>Editor: Fix correctness issue
    end
```

**Diagram: Standard Optimization Workflow**

This workflow emphasizes correctness validation before performance measurement, ensuring that optimizations do not compromise functional correctness.

**Sources:** [Readme.md:21-23](), [Readme.md:36]()

### Testing and Validation Workflow

The testing workflow validates both correctness and performance characteristics. Users are specifically warned not to modify the `tests/` directory to ensure valid performance measurements.

| Test Phase | Command | Purpose | Outputs |
|------------|---------|---------|---------|
| **Integrity Check** | `git diff origin/main tests/` | Ensure test code hasn't been tampered with | Diff output (should be empty) |
| **Full Test Suite** | `python tests/submission_tests.py` | Run all correctness and speed tests | Pass/fail status, cycle counts |

**Sources:** [Readme.md:31-36]()

### Trace-Driven Debugging Workflow

For performance analysis and debugging, the trace visualization workflow provides detailed execution insights. This involves setting `trace=True` in the `Machine` simulator.

```mermaid
flowchart LR
    subgraph "Code Modification"
        Edit["Edit build_kernel()"]
    end
    
    subgraph "Trace Generation"
        EnableTrace["Set trace=True in<br/>Machine constructor"]
        RunCode["Execute kernel"]
        GenTrace["Generate trace.json"]
    end
    
    subgraph "Visualization"
        Server["Start watch_trace.py<br/>on port 8000"]
        Browser["Open browser to<br/>localhost:8000"]
        Perfetto["View in Perfetto UI"]
    end
    
    subgraph "Analysis"
        Examine["Examine timeline<br/>Identify bottlenecks"]
        Decision{"Optimization<br/>idea?"}
    end
    
    Edit --> EnableTrace
    EnableTrace --> RunCode
    RunCode --> GenTrace
    GenTrace --> Server
    Server --> Browser
    Browser --> Perfetto
    Perfetto --> Examine
    Examine --> Decision
    Decision -->|Yes| Edit
    Decision -->|No| Done["Optimization complete"]
```

**Diagram: Trace-Driven Development Cycle**

The trace file `trace.json` is automatically regenerated each time the simulator runs with tracing enabled. The `watch_trace.py` server provides the necessary infrastructure to view these traces in the Perfetto UI.

**Sources:** [.gitignore:1](), [Readme.md:5]()

---

## Repository Hygiene and Best Practices

### Python Environment Management

The repository uses standard Python 3 without complex dependency requirements.

```mermaid
graph TB
    subgraph "Python Environment"
        Python["Python 3.x"]
        StdLib["Standard Library<br/>json, http.server, etc."]
    end
    
    subgraph "No External Dependencies"
        NoDeps["No pip install required<br/>No requirements.txt"]
    end
    
    subgraph "Optional Tools"
        Browser["Web browser<br/>for trace visualization"]
        Perfetto["ui.perfetto.dev<br/>online trace viewer"]
    end
    
    Python --> StdLib
    StdLib --> NoDeps
    Browser -.->|optional| Perfetto
```

**Diagram: Minimal Dependency Structure**

The codebase deliberately avoids external dependencies to ensure maximum portability and minimize setup friction.

**Sources:** [Readme.md:5](), [Readme.md:23]()

### Working with Generated Files

Generated files are temporary artifacts of the development process and should be managed appropriately:

| File Type | Location | Lifecycle | Action |
|-----------|----------|-----------|--------|
| **trace.json** | Repository root | Generated per execution | Excluded from git, safe to delete |
| **\*.pyc** | `__pycache__/` directories | Cached on import | Excluded from git, safe to delete |
| **.hypothesis/** | Repository root | Testing framework cache | Excluded from git, safe to delete |

To clean all generated artifacts:

```bash
# Remove trace file
rm -f trace.json

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Remove Hypothesis cache
rm -rf .hypothesis
```

**Sources:** [.gitignore:1-4]()

### Performance Submission Guidelines

When achieving cycle counts below the **1487-cycle threshold** (Claude Opus 4.5 11.5hr performance):

| Requirement | Details |
|-------------|---------|
| **Contact** | Email `performance-recruiting@anthropic.com` |
| **Include** | Your optimized code and ideally a resume |
| **Integrity** | Ensure `git diff origin/main tests/` is empty |
| **Validation** | Mention that you ran the validation commands |

The submission process validates that the optimization is legitimate and not a result of modifying the test environment (e.g., increasing `N_CORES`).

**Sources:** [Readme.md:17](), [Readme.md:21](), [Readme.md:31-39]()

---

## Development Environment Setup

### Initial Setup Workflow

```mermaid
flowchart TB
    Clone["Clone repository<br/>git clone <repo-url>"]
    Verify["Verify Python 3.x<br/>python --version"]
    Test["Run baseline tests<br/>python tests/submission_tests.py"]
    Baseline["Note baseline performance<br/>~147,734 cycles"]
    
    Ready["Ready for optimization"]
    
    Clone --> Verify
    Verify --> Test
    Test --> Baseline
    Baseline --> Ready
```

**Diagram: Initial Repository Setup**

No package installation or virtual environment configuration is required. The repository is designed to work immediately after cloning with a standard Python 3 installation.

**Sources:** [Readme.md:23]()

### File Modification Guidelines

When optimizing the kernel builder, follow these guidelines to maintain the integrity of the benchmark:

| File | Modification Policy | Rationale |
|------|-------------------|-----------|
| **perf_takehome.py** | Modify freely | Primary optimization target |
| **problem.py** | Avoid modification | Development simulator reference |
| **frozen_problem.py** | **DO NOT MODIFY** | Used for official performance validation |
| **tests/** | **DO NOT MODIFY** | Integrity of the performance benchmark |

**Sources:** [Readme.md:27-39]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Readme.md](Readme.md)
- [perf_takehome.py](perf_takehome.py)
- [problem.py](problem.py)
- [tests/frozen_problem.py](tests/frozen_problem.py)

</details>



This page provides a comprehensive reference for terms, jargon, and architectural constants used throughout the performance optimization benchmark. It defines the relationships between hardware simulation concepts and their software implementations.

### Architectural Terms

| Term | Definition | Implementation Detail |
|:---|:---|:---|
| **VLIW** | Very Large Instruction Word. An architecture where a single instruction bundle contains multiple operations for different hardware engines. | `Instruction` is a `dict[Engine, list[tuple]]` [problem.py:15-15](). |
| **SIMD** | Single Instruction Multiple Data. Processing multiple data points (vectors) with a single operation. | Implemented via `valu`, `vload`, and `vstore` engines [problem.py:75-78](). |
| **VLEN** | Vector Length. The number of 32-bit words processed in a single SIMD operation. | Fixed at `8` [problem.py:57-57](). |
| **Engine** | A specialized hardware unit (ALU, Load, Store, etc.) capable of executing specific types of operations. | Defined as `Literal["alu", "load", "store", "flow"]` [problem.py:14-14](). |
| **Slot** | An execution unit within an engine. An engine can have multiple slots to execute operations in parallel. | Managed via `SLOT_LIMITS` [problem.py:48-55](). |
| **SLOT_LIMITS** | The maximum number of parallel operations allowed per engine per clock cycle. | ALU: 12, VALU: 6, Load: 2, Store: 2, Flow: 1 [problem.py:48-55](). |
| **Scratch** | Fast, per-core memory used for registers, constants, and local caching. | Size is `1536` words [problem.py:60-60](). |
| **N_CORES** | The number of processing units in the machine. | Fixed at `1` for this version of the challenge [problem.py:59-59](). |
| **SCRATCH_SIZE** | The total capacity of the scratch memory in 32-bit words. | `1536` [problem.py:60-60](). |

**Sources:** [problem.py:14-60](), [problem.py:75-78]()

---

### Core Logic and Software Entities

#### Machine and State
*   **Machine**: The simulator class that executes the VLIW program. It manages memory, cores, and cycle counting [problem.py:64-118]().
*   **Core**: A representation of a single execution unit containing its own `scratch` memory, program counter (`pc`), and `state` [problem.py:25-31]().
*   **CoreState**: An Enum representing the status of a core: `RUNNING`, `PAUSED`, or `STOPPED` [problem.py:18-21]().
*   **DebugInfo**: A container for metadata, primarily the `scratch_map`, which links raw scratch addresses to human-readable names for tracing [problem.py:34-42]().

#### Kernel Development
*   **KernelBuilder**: A utility class used to generate the program instructions. It handles scratch allocation and instruction packing [perf_takehome.py:40-47]().
*   **build_kernel**: The primary method in `KernelBuilder` that users must optimize. It translates the tree traversal logic into machine instructions [perf_takehome.py:88-175]().
*   **reference_kernel / reference_kernel2**: Python-based implementations of the tree traversal algorithm used to define correct behavior and provide a comparison baseline [perf_takehome.py:34-36]().

#### Problem Domain
*   **HASH_STAGES**: A sequence of operations (add, xor, etc.) and constants that define the `myhash` algorithm [perf_takehome.py:80-86]().
*   **myhash**: The hashing function applied at each node of the tree traversal [perf_takehome.py:149-152]().
*   **forest_height**: The depth of the binary trees in the forest.
*   **n_nodes**: The total number of nodes across the forest.
*   **batch_size**: The number of independent traversals processed in parallel during one round [perf_takehome.py:135-135]().
*   **rounds**: The number of times the batch processing is repeated [perf_takehome.py:134-134]().
*   **pause**: A special instruction that yields execution to the simulator, used for synchronization and debugging [perf_takehome.py:122-122]().

**Sources:** [problem.py:18-118](), [perf_takehome.py:34-175]()

---

### System Component Mapping

The following diagram bridges the conceptual "Problem Space" to the specific "Code Entities" that implement them.

**System Entity Relationship**
```mermaid
graph TD
    subgraph "Problem Space"
        A["Tree Traversal"] --> B["Hashing Logic"]
        A --> C["Parallel Batches"]
    end

    subgraph "Code Entity Space (Implementation)"
        B --> D["HASH_STAGES [problem.py]"]
        D --> E["KernelBuilder.build_hash() [perf_takehome.py]"]
        C --> F["batch_size [perf_takehome.py]"]
        A --> G["reference_kernel2 [problem.py]"]
    end

    subgraph "Execution Space (Hardware Simulation)"
        E --> H["Machine.run() [problem.py]"]
        H --> I["Core [problem.py]"]
        I --> J["Scratch Memory"]
        I --> K["ALU/VALU Engines"]
    end
```
**Sources:** [problem.py:25-118](), [perf_takehome.py:77-175]()

---

### Execution and Performance Metrics

*   **build_mem_image**: A function that prepares the initial state of main memory, including the tree nodes and input indices [perf_takehome.py:35-35]().
*   **BASELINE**: The cycle count achieved by the unoptimized scalar implementation (147,734 cycles) [perf_takehome.py:176-176]().
*   **cycle count**: The primary metric of performance, representing the number of iterations the `Machine` loop performs until all cores reach `STOPPED` [problem.py:115-115]().
*   **frozen_problem**: A copy of the simulator (`frozen_problem.py`) used by the test suite to ensure optimizations are measured against a stable, non-modified architecture [tests/frozen_problem.py:1-6]().
*   **trace.json**: A file generated by the `Machine` (when `trace=True`) in Chrome Trace Event Format [problem.py:160-160]().
*   **Perfetto**: The recommended web-based UI for visualizing `trace.json` to analyze engine utilization and scratch memory transitions [problem.py:153-158]().
*   **test-time compute harness**: A reference to the environment where Claude models were evaluated, involving multiple hours of iterative optimization [Readme.md:13-18]().

**Hardware Slot Mapping**
```mermaid
graph LR
    subgraph "Instruction Bundle (VLIW)"
        direction TB
        S1["'alu': [slot0...slot11]"]
        S2["'valu': [slot0...slot5]"]
        S3["'load': [slot0...slot1]"]
        S4["'store': [slot0...slot1]"]
    end

    S1 --> M["Machine.step()"]
    S2 --> M
    S3 --> M
    S4 --> M

    M --> P["Parallel Execution Phase"]
    P --> C["End-of-Cycle Commit"]
    C --> SC["Update Core.scratch"]
    C --> ME["Update Machine.mem"]
```
**Sources:** [problem.py:48-55](), [problem.py:68-73](), [problem.py:197-205]()

**Sources:** [problem.py:1-205](), [perf_takehome.py:1-176](), [Readme.md:1-40](), [tests/frozen_problem.py:1-6]()