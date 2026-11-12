<!-- source: DeepWiki mcp.deepwiki.com · repo ml-energy/zeus · page 11 Research Background · fetched 2026-10-21 -->

# Research Background

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/research_overview/index.md](docs/research_overview/index.md)
- [docs/research_overview/perseus.md](docs/research_overview/perseus.md)
- [docs/research_overview/zeus.md](docs/research_overview/zeus.md)

</details>



## Purpose and Scope

This document provides an overview of the academic research that forms the foundation of the Zeus framework. Zeus is built on multiple peer-reviewed publications that introduced novel techniques for optimizing energy consumption in deep learning training. Understanding these research contributions is essential for comprehending the design decisions and optimization strategies implemented in the codebase.

For detailed implementation guides on the optimization techniques, see [Energy Optimization](#5). For information on energy measurement capabilities, see [Energy Measurement](#4).

**Sources:** docs/research_overview/index.md, docs/research_overview/zeus.md, docs/research_overview/perseus.md

---

## Research Evolution and Timeline

Zeus emerged from a sequence of research papers that progressively addressed different aspects of energy efficiency in deep learning training. The framework implements techniques from multiple publications, each contributing distinct optimization strategies.

```mermaid
graph LR
    subgraph "Research Timeline"
        NSDI23["Zeus (NSDI '23)<br/>JIT Profiling<br/>Batch Size Optimization"]
        ICLR23["Chase (ICLRW '23)<br/>Carbon-Aware Training"]
        SOSP24["Perseus (SOSP '24)<br/>Energy Bloat Reduction<br/>Pipeline Optimization"]
    end
    
    subgraph "Core Problems Addressed"
        PROB1["Time-Energy Tradeoff<br/>Single GPU Training"]
        PROB2["Carbon Intensity<br/>Temporal Variation"]
        PROB3["Energy Bloat<br/>Pipeline Parallelism"]
    end
    
    subgraph "Key Contributions"
        CONTRIB1["Power Limit Selection<br/>Batch Size Selection<br/>Multi-Armed Bandit"]
        CONTRIB2["Carbon-Aware<br/>Scheduling"]
        CONTRIB3["Frequency Assignment<br/>Graph Cut Algorithm<br/>Pareto Frontiers"]
    end
    
    NSDI23 --> PROB1
    ICLR23 --> PROB2
    SOSP24 --> PROB3
    
    PROB1 --> CONTRIB1
    PROB2 --> CONTRIB2
    PROB3 --> CONTRIB3
```

**Sources:** docs/research_overview/index.md:1-9, docs/research_overview/zeus.md:1-12, docs/research_overview/perseus.md:1-12

---

## Zeus (NSDI '23): Foundational Concepts

The original Zeus paper established the fundamental observation that DNN training exhibits a **time-energy tradeoff** when varying two key knobs: GPU power limit and batch size. This research introduced the concept of navigating the Pareto frontier of (time, energy) configurations to find optimal training parameters.

### Key Research Findings

| Finding | Description | Implementation Impact |
|---------|-------------|----------------------|
| **Energy Inefficiency** | Default training configurations waste 30-50% energy | Motivates automatic optimization |
| **Time-Energy Tradeoff** | Reducing energy often increases training time | User-defined cost metric $\eta$ |
| **Recurring Jobs** | Production training jobs recur frequently | Enables online profiling across runs |
| **GPU Power Limit** | Capping power reduces energy with minimal time impact | JIT profiling of power limits |
| **Batch Size Impact** | Larger batches are more energy-efficient up to a point | Multi-armed bandit exploration |

### Cost Metric Definition

Zeus introduced a parameterized cost function to quantify the time-energy tradeoff:

$$
\text{Cost} = \eta \cdot \text{Energy} + (1 - \eta) \cdot \text{MaxPower} \cdot \text{Time}
$$

where $\eta \in [0, 1]$ represents user preference: $\eta = 0$ minimizes time, $\eta = 1$ minimizes energy, and intermediate values balance both objectives.

**Sources:** docs/research_overview/zeus.md:27-98

---

## Perseus (SOSP '24): Energy Bloat Taxonomy

Perseus extended Zeus to address energy inefficiency in large-scale pipeline-parallel training. The paper identified two independent sources of **energy bloat**—wasted energy that does not contribute to training throughput—and proposed techniques to eliminate both.

### Energy Bloat Categories

```mermaid
graph TB
    subgraph "Energy Bloat Types"
        INTRINSIC["Intrinsic Bloat<br/>Load imbalance within pipeline<br/>Some stages finish early"]
        EXTRINSIC["Extrinsic Bloat<br/>Stragglers across pipelines<br/>Fast pipelines wait for slow ones"]
    end
    
    subgraph "Root Causes"
        CAUSE1["Imperfect Stage Partitioning<br/>Different computation sizes"]
        CAUSE2["Heterogeneous Hardware<br/>Performance variation"]
        CAUSE3["System Stragglers<br/>Thermal throttling, faults"]
        CAUSE4["Data Pipeline Stalls<br/>I/O bottlenecks"]
    end
    
    subgraph "Perseus Solutions"
        SOL1["Per-Stage Frequency Tuning<br/>Slow down light stages"]
        SOL2["Pipeline-Wide Frequency Plans<br/>Slow down non-straggler pipelines"]
    end
    
    CAUSE1 --> INTRINSIC
    CAUSE2 --> INTRINSIC
    CAUSE3 --> EXTRINSIC
    CAUSE4 --> EXTRINSIC
    
    INTRINSIC --> SOL1
    EXTRINSIC --> SOL2
```

### Pareto Frontier Characterization

Perseus pre-computes the **iteration time-energy Pareto frontier** for pipeline training by solving a graph cut optimization problem. Each point on the frontier represents a GPU frequency plan (per-stage frequency assignments) that minimizes energy for a given iteration time constraint.

**Sources:** docs/research_overview/perseus.md:44-86

---

## Research Concepts Mapped to Code Entities

The following diagrams map research concepts to their concrete implementations in the Zeus codebase.

### Zeus (NSDI '23) Implementation Map

```mermaid
graph TB
    subgraph "Research Concepts"
        JIT["JIT Profiling<br/>Online power limit search"]
        MAB["Multi-Armed Bandit<br/>Batch size exploration"]
        COST["Cost Metric<br/>eta parameter"]
        PARETO["Pareto Frontier<br/>Efficient configurations"]
    end
    
    subgraph "Core Implementation"
        GPLO["GlobalPowerLimitOptimizer<br/>zeus/optimizer/power_limit.py"]
        BSO["BatchSizeOptimizer<br/>zeus/_legacy/policy/optimizer.py"]
        STATE["State Machine<br/>Ready→Warmup→Profiling→Done"]
        PROFILE["ProfileCache<br/>Disk persistence"]
    end
    
    subgraph "Optimization Strategies"
        ENERGY_MIN["minimize_energy()"]
        TIME_MIN["minimize_time()"]
        ZEUS_COST_MIN["minimize_cost(eta)"]
        SLOWDOWN["minimize_energy_with_max_slowdown()"]
    end
    
    subgraph "Measurement Integration"
        MONITOR["ZeusMonitor<br/>zeus/monitor/energy.py"]
        MEASUREMENT["begin_window/end_window"]
        SYNC["sync_execution_with"]
    end
    
    JIT --> GPLO
    MAB --> BSO
    COST --> ZEUS_COST_MIN
    PARETO --> ENERGY_MIN
    PARETO --> TIME_MIN
    PARETO --> SLOWDOWN
    
    GPLO --> STATE
    GPLO --> PROFILE
    GPLO --> ENERGY_MIN
    GPLO --> TIME_MIN
    GPLO --> ZEUS_COST_MIN
    GPLO --> SLOWDOWN
    
    GPLO --> MONITOR
    MONITOR --> MEASUREMENT
    MONITOR --> SYNC
```

**Key Files:**
- `zeus/optimizer/power_limit.py`: `GlobalPowerLimitOptimizer` implements JIT profiling algorithm from Zeus paper
- `zeus/_legacy/policy/optimizer.py`: `BatchSizeOptimizer` base class and Thompson Sampling implementation
- `zeus/monitor/energy.py`: `ZeusMonitor` provides energy measurement for optimization
- `zeus/optimizer/power_limit.py:100-150`: State machine transitions (Ready → Warmup → Profiling → Done)

**Sources:** docs/research_overview/zeus.md:100-122, zeus/optimizer/power_limit.py (implied from diagram context)

### Perseus (SOSP '24) Implementation Map

```mermaid
graph TB
    subgraph "Research Concepts"
        GRAPH_CUT["Graph Cut Algorithm<br/>NP-Hard frequency assignment"]
        INTRINSIC["Intrinsic Bloat Reduction<br/>Per-stage frequency tuning"]
        EXTRINSIC["Extrinsic Bloat Reduction<br/>Pipeline slowdown on stragglers"]
        FRONTIER["Pareto Frontier Discovery<br/>All iteration times"]
    end
    
    subgraph "Core Implementation"
        PFO["PipelineFrequencyOptimizer<br/>zeus/optimizer/pipeline_frequency/"]
        SERVER["PFOServer<br/>HTTP API for frequency control"]
        OPTIMIZER["Optimizer<br/>Graph cut solver"]
        EXECUTOR["PFOExecutor<br/>Frequency plan execution"]
    end
    
    subgraph "Frequency Control"
        FREQ_SET["setGpuLockedClocks()"]
        MEM_FREQ["setMemLockedClocks()"]
        RESET["resetGpuLockedClocks()"]
    end
    
    subgraph "Pre-Characterization"
        STAGE_PROF["Stage Profiling<br/>Cost matrix generation"]
        PARETO_COMP["Pareto Computation<br/>All time constraints"]
        HIST_PROF["Histogram Profiler<br/>Historical data"]
    end
    
    GRAPH_CUT --> OPTIMIZER
    INTRINSIC --> PFO
    EXTRINSIC --> SERVER
    FRONTIER --> PARETO_COMP
    
    PFO --> OPTIMIZER
    PFO --> EXECUTOR
    PFO --> SERVER
    
    OPTIMIZER --> STAGE_PROF
    OPTIMIZER --> PARETO_COMP
    
    EXECUTOR --> FREQ_SET
    EXECUTOR --> MEM_FREQ
    EXECUTOR --> RESET
    
    SERVER --> HIST_PROF
```

**Key Files:**
- `zeus/optimizer/pipeline_frequency/`: Root directory for Perseus implementation
- `zeus/optimizer/pipeline_frequency/server/`: PFO server for distributed frequency control
- `zeus/optimizer/pipeline_frequency/optimizer.py`: Graph cut algorithm implementation
- `zeus/optimizer/pipeline_frequency/common.py`: Frequency plan data structures
- `zeus/device/gpu/nvidia.py`: GPU frequency control methods (`setGpuLockedClocks`, `setMemLockedClocks`)

**Sources:** docs/research_overview/perseus.md:62-89

---

## Optimization Algorithm Summary

The table below summarizes the key algorithms from the research papers and their implementation status in Zeus.

| Algorithm | Paper | Purpose | Implementation | Complexity |
|-----------|-------|---------|----------------|------------|
| **JIT Profiling** | Zeus (NSDI '23) | Find optimal power limit via online measurement | `GlobalPowerLimitOptimizer` | O(k) iterations, k power limits |
| **Thompson Sampling** | Zeus (NSDI '23) | Multi-armed bandit for batch size exploration | `ZeusBatchSizeOptimizer` | O(log T) regret over T rounds |
| **Graph Cut** | Perseus (SOSP '24) | Assign frequencies to pipeline stages | `Optimizer.optimize()` | Approximate solution, NP-Hard |
| **Pareto Discovery** | Perseus (SOSP '24) | Enumerate all efficient time-energy pairs | `Optimizer.optimize_all()` | O(T × S × F²), T times, S stages, F frequencies |
| **Wraparound Tracking** | Implementation detail | Handle RAPL counter overflow | `RAPLCPUs` | Background polling process |

**Sources:** docs/research_overview/zeus.md:100-141, docs/research_overview/perseus.md:62-86

---

## Research Reproducibility

Both research papers provide mechanisms for reproducibility and extension within the Zeus codebase.

### Zeus Simulator

The Zeus paper includes a trace-driven simulator that allows researchers to evaluate custom optimization policies without access to physical GPUs. The simulator operates on pre-collected training traces from 6 DNNs across 4 GPU architectures.

**Abstract Interfaces:**
- `zeus._legacy.policy.BatchSizeOptimizer`: Base class for batch size optimization policies
- `zeus._legacy.policy.PowerLimitOptimizer`: Base class for power limit optimization policies
- `zeus._legacy.simulate.Simulator`: Trace-driven simulation engine

**Location:** `examples/research_reproducibility/zeus_nsdi23/`

### Perseus Integration

Perseus is implemented as the `PipelineFrequencyOptimizer` and is in active development. The implementation includes:

- Graph cut-based frequency optimizer
- HTTP server for distributed control
- Stage profiling and cost matrix generation
- Pareto frontier computation

**Location:** `zeus/optimizer/pipeline_frequency/`

**Sources:** docs/research_overview/zeus.md:126-141, docs/research_overview/perseus.md:87-91

---

## Integration with Zeus Architecture

The research contributions integrate with Zeus's broader architecture through well-defined interfaces:

```mermaid
graph TB
    subgraph "Research Algorithms"
        ALG1["JIT Profiling<br/>Power Limit Optimization"]
        ALG2["Thompson Sampling<br/>Batch Size Exploration"]
        ALG3["Graph Cut<br/>Frequency Assignment"]
    end
    
    subgraph "Zeus Core Components"
        MONITOR["ZeusMonitor<br/>Energy Measurement"]
        DEVICE["Device Abstraction<br/>GPU/CPU Control"]
        CALLBACK["Callback API<br/>Training Integration"]
    end
    
    subgraph "Hardware Layer"
        NVML["NVIDIA GPUs<br/>Power limit, frequency control"]
        AMDSMI["AMD GPUs<br/>Power limit control"]
        RAPL["CPU RAPL<br/>Energy counters"]
    end
    
    subgraph "Framework Integration"
        PYTORCH["PyTorch<br/>sync_execution_with"]
        HF["HuggingFace<br/>TrainerCallback"]
        CUSTOM["Custom Training<br/>Manual integration"]
    end
    
    ALG1 --> MONITOR
    ALG2 --> MONITOR
    ALG3 --> MONITOR
    
    ALG1 --> DEVICE
    ALG3 --> DEVICE
    
    ALG1 --> CALLBACK
    ALG3 --> CALLBACK
    
    DEVICE --> NVML
    DEVICE --> AMDSMI
    MONITOR --> RAPL
    
    CALLBACK --> PYTORCH
    CALLBACK --> HF
    CALLBACK --> CUSTOM
```

**Key Integration Points:**
- **Measurement:** All optimizers use `ZeusMonitor` for energy measurement with framework synchronization
- **Control:** Optimizers modify GPU state through the device abstraction layer
- **Training Loop:** Callback API provides hooks for `on_step_begin()` and `on_step_end()` events
- **State Persistence:** Profile caches persist measurements to disk for recurring jobs

**Sources:** Derived from overall system architecture

---

## Research Metrics and Evaluation

The research papers introduced specific metrics for evaluating energy optimization, which are reflected in Zeus's measurement and optimization APIs.

### Zeus Metrics

| Metric | Definition | Purpose |
|--------|------------|---------|
| **TTA** | Time To Accuracy | Training time to reach target validation metric |
| **ETA** | Energy To Accuracy | Energy consumed to reach target validation metric |
| **Cost** | $\eta \cdot \text{Energy} + (1-\eta) \cdot \text{MaxPower} \cdot \text{Time}$ | User-defined tradeoff metric |
| **Normalized Cost** | Cost relative to baseline configuration | Quantify improvement percentage |

### Perseus Metrics

| Metric | Definition | Purpose |
|--------|------------|---------|
| **Iteration Time** | End-to-end pipeline execution time | Performance constraint |
| **Iteration Energy** | Total energy for one pipeline iteration | Optimization objective |
| **Energy Bloat** | Wasted energy not contributing to throughput | Quantify inefficiency |
| **Slowdown** | Relative increase in iteration time | Constraint for optimization |

**Sources:** docs/research_overview/zeus.md:117, docs/research_overview/perseus.md:20-24

---

## Future Research Directions

The Zeus framework continues to evolve with ongoing research. Current areas of development include:

1. **Carbon-Aware Training**: Integrating temporal carbon intensity variation (Chase, ICLRW '23)
2. **Multi-Objective Optimization**: Joint optimization of energy, time, and carbon
3. **Distributed Training**: Extending Perseus to fully-sharded data parallelism
4. **Automated Pipeline Partitioning**: Optimal pipeline stage assignment to minimize intrinsic bloat
5. **Hardware Heterogeneity**: Optimizing across mixed GPU generations and vendors

These research directions will continue to expand Zeus's capabilities and improve its energy optimization effectiveness.

**Sources:** docs/research_overview/index.md:1-9

---

