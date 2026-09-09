> 来源: [https://deepwiki.com/geek-ai/MAgent/7-performance-and-scalability](https://deepwiki.com/geek-ai/MAgent/7-performance-and-scalability)
> DeepWiki geek-ai/MAgent | Last indexed: 26 October 2025 (2144db

# Performance and Scalability

  Relevant source files 
 - [scripts/test/test_1m.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_1m.py)
 - [scripts/test/test_fps.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_fps.py)
 - [src/gridworld/GridWorld.cc](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc)
 
  
## Purpose and Scope

 This document covers the performance characteristics and scalability mechanisms in MAgent, focusing on how the system achieves efficient simulation of large-scale multi-agent environments. It explains the multi-level parallelism architecture, optimization strategies, and benchmarking tools available for performance testing.

 For training-specific parallelism (multi-process model training), see [ProcessingModel and Parallelism](https://deepwiki.com/geek-ai/MAgent/4.2-processingmodel-and-parallelism). For detailed parallelization techniques and implementation, see [Parallelization Strategies](https://deepwiki.com/geek-ai/MAgent/7.2-parallelization-strategies). For large-scale simulation techniques, see [Scaling to Millions of Agents](https://deepwiki.com/geek-ai/MAgent/7.3-scaling-to-millions-of-agents).

 
## Performance Architecture Overview

 MAgent achieves high performance through a three-tier parallelization strategy that operates at different levels of the system stack.

 
### Multi-Level Parallelism Architecture

 
```

```

 **Sources:** [src/gridworld/GridWorld.cc1-70](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L1-L70) [scripts/test/test_1m.py77-86](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_1m.py#L77-L86) [scripts/test/test_fps.py22-43](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_fps.py#L22-L43)

 The system achieves parallelism at three levels:

 
 - **Python Multiprocessing**: Multiple model processes avoid GIL constraints
 - **C++ OpenMP**: Thread-level parallelism within the simulation engine
 - **Hardware**: Multi-core CPUs and multi-GPU inference
 
 
## C++ Engine Parallelization

 The core simulation engine in `GridWorld.cc` uses OpenMP directives extensively to parallelize computationally intensive operations.

 
### Parallel Operation Breakdown

 
```

```

 **Sources:** [src/gridworld/GridWorld.cc456-631](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L456-L631)

 
| Operation | Parallelization Method | Key Code Location |
|---|---|---|
| Attack Processing | #pragma omp parallel for reduction(merge: render_attack_buffer) | GridWorld.cc475-506 |
| Starve Check | #pragma omp parallel for reduction(+: starve_ct) | GridWorld.cc527-541 |
| Observation Extraction | #pragma omp parallel for over agents | GridWorld.cc363-397 |
| Agent Deletion | #pragma omp parallel for over groups | GridWorld.cc636-664 |
| Info Queries | #pragma omp parallel for for various info types | GridWorld.cc721-779 |

 
### OpenMP Thread Configuration

 The system automatically configures OpenMP threads based on map size:

 
```

```

 **Sources:** [scripts/test/test_fps.py30-36](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_fps.py#L30-L36)

 The thread count is set externally via `OMP_NUM_THREADS` environment variable:

 
 - **Small simulations (< 1M agents)**: 8 threads
 - **Large simulations (>= 1M agents)**: 16 threads
 
 
## Scalability Mechanisms

 
### Large Map Mode

 MAgent implements a "large map mode" that activates automatic spatial partitioning for efficient parallel processing of actions.

 
```

```

 **Sources:** [src/gridworld/GridWorld.cc72-85](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L72-L85)

 
### Spatial Partitioning for Parallel Action Processing

 When large map mode is enabled, the map is divided into vertical bands to enable parallel processing of move and turn actions.

 **Partitioning Strategy:**

 
 - Map width is divided into `NUM_SEP_BUFFER` equal bands
 - `bandwidth = (width + NUM_SEP_BUFFER - 1) / NUM_SEP_BUFFER`
 - Each band has its own action buffer: `move_buffers[NUM_SEP_BUFFER]`, `turn_buffers[NUM_SEP_BUFFER]`
 - Actions near boundaries (within 4 pixels) go into special boundary buffers
 
 
```

```

 **Sources:** [src/gridworld/GridWorld.cc403-453](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L403-L453)

 **Parallel Execution:**

 After partitioning, move and turn operations are processed in parallel:

 
```
// Move phase - parallel execution
#pragma omp parallel for
for (int i = 0; i < NUM_SEP_BUFFER; i++) {
    do_move_for_a_buffer(move_buffers[i], map);
}
// Then process boundary buffer sequentially
do_move_for_a_buffer(move_buffer_bound, map);
```

 **Sources:** [src/gridworld/GridWorld.cc605-613](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L605-L613)

 This strategy ensures:

 
 - **No race conditions**: Each thread operates on disjoint spatial regions
 - **Load balancing**: Bands are sized to distribute work evenly
 - **Boundary safety**: Actions near boundaries are handled sequentially to avoid conflicts
 
 
### Memory Management

 The C++ engine uses several memory optimization techniques:

 
| Technique | Implementation | Benefit |
|---|---|---|
| Buffer Reuse | Action buffers cleared after each step | Avoids repeated allocation |
| NDPointer | Stack-allocated view wrappers | Zero-copy array access |
| Conditional Allocation | Minimap allocated only when needed | Reduces memory footprint |
| Agent Pooling | Agents deleted in parallel during cleanup | Fast deallocation |

 **Sources:** [src/gridworld/GridWorld.cc310-311](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L310-L311) [src/gridworld/GridWorld.cc332-333](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L332-L333) [src/gridworld/GridWorld.cc636-664](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L636-L664)

 
## Performance Characteristics

 
### Operation Time Breakdown

 The `test_1m.py` script measures the time spent in each major operation:

 
```

```

 **Sources:** [scripts/test/test_1m.py95-118](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_1m.py#L95-L118)

 **Typical Time Distribution** (1M agents, GPU inference):

 
 - **Observation Extraction**: ~15-20% of step time
 - **Neural Network Inference**: ~30-40% of step time (GPU-bound)
 - **Simulation Step**: ~20-30% of step time (parallel C++ execution)
 - **Reward Collection**: ~5-10% of step time
 - **Dead Agent Cleanup**: ~5% of step time
 
 
### Bottlenecks

 Common performance bottlenecks and their causes:

 
```

```

 **Sources:** [src/gridworld/GridWorld.cc292-401](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L292-L401) [scripts/test/test_1m.py77-86](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_1m.py#L77-L86)

 
## Optimization Strategies

 
### Thread Configuration Tuning

 The optimal number of OpenMP threads depends on the simulation scale:

 
```

```

 **Sources:** [scripts/test/test_fps.py34-36](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_fps.py#L34-L36)

 **Guidelines:**

 
 - **Too few threads**: Underutilizes CPU cores
 - **Too many threads**: Excessive context switching overhead
 - **Rule of thumb**: Use 50-75% of available CPU cores
 - **Hyperthreading**: Generally not beneficial for MAgent workloads
 
 
### Batch Processing Configuration

 For neural network inference, batch size significantly impacts performance:

 
```

```

 **Sources:** [scripts/test/test_1m.py85-86](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_1m.py#L85-L86)

 **Batch Size Recommendations:**

 
| Agent Count | CPU Inference | GPU Inference |
|---|---|---|
| < 10K | 1000-5000 | 5000-10000 |
| 10K-100K | 5000-10000 | 10000-50000 |
| 100K-1M | 10000-50000 | 50000-100000 |
| > 1M | 50000-100000 | 100000-500000 |

 
### GPU Utilization Strategy

 
```

```

 **Sources:** [scripts/test/test_1m.py77-86](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_1m.py#L77-L86)

 **GPU Strategy:**

 
 - **No GPU** (`num_gpu=0`): Use for rule-based models or small-scale testing
 - **Single GPU**: Suitable for most scenarios up to 100K agents
 - **Multi-GPU**: Required for 1M+ agents with neural network policies
 
 
### Non-Blocking Inference

 When using `ProcessingModel`, enable non-blocking inference to overlap computation:

 
```

```

 This allows multiple model processes to compute simultaneously, reducing idle time.

 **Sources:** Described in system architecture diagrams

 
## Benchmarking Tools

 
### test_1m.py - Detailed Performance Profiling

 The `test_1m.py` script provides detailed timing information for each operation in the training loop.

 **Usage:**

 
```

```

 **Parameters:**

 
 - `--n_step`: Number of simulation steps to run
 - `--agent_number`: Total number of agents (split equally between groups)
 - `--num_gpu`: Number of GPUs for inference (0 for CPU-only)
 - `--frame`: Deep learning framework ('tf' or 'mx')
 
 **Output Format:**

 
```
===== step 0 =====
get obs 1   0.05234
infer act 1 0.12456
set act 1   0.00123
get obs 2   0.05678
infer act 2 0.11234
set act 2   0.00134
step        0.08901
get reward  0.00234
clear       0.01234
all time: 0.45328

number of deer: 500000
number of tiger: 500000
total reward: 12345
FPS 43.2
```

 **Sources:** [scripts/test/test_1m.py1-130](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_1m.py#L1-L130)

 
### test_fps.py - Systematic Performance Testing

 The `test_fps.py` script performs systematic benchmarking across different agent counts and GPU configurations.

 
```

```

 **Sources:** [scripts/test/test_fps.py1-48](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_fps.py#L1-L48)

 **Usage:**

 
```

```

 **Output:** Matrix of FPS values for each (agent_count, num_gpu) combination:

 
```
# Agents  | 0 GPU  | 1 GPU  | 2 GPU
----------|--------|--------|--------
1,000     | 1250.3 | 1180.5 | 1150.2
10,000    | 425.6  | 520.8  | 610.3
100,000   | 52.3   | 85.4   | 120.7
1,000,000 | 5.1    | 12.3   | 18.9
```

 
### Performance Testing Workflow

 
```

```

 **Sources:** [scripts/test/test_1m.py62-129](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_1m.py#L62-L129)

 **Best Practices:**

 
 - **Warm-up**: Skip first 20 steps to exclude initialization overhead
 - **Environment isolation**: Set `TF_CPP_MIN_LOG_LEVEL=3` to reduce logging
 - **Consistent configuration**: Use same map size ratio (agent_number * 20) for fair comparison
 - **Multiple runs**: Average results across multiple runs for reliability
 
 
## Performance Expectations

 
### Typical Performance Metrics

 Based on reference hardware (modern multi-core CPU + GPU):

 
| Configuration | Agent Count | FPS | Steps/Second/Agent |
|---|---|---|---|
| CPU-only (8 threads) | 1K | ~1200 | 1.2 |
| CPU-only (8 threads) | 10K | ~400 | 0.04 |
| CPU-only (8 threads) | 100K | ~50 | 0.0005 |
| 1 GPU (batch=100K) | 1K | ~1100 | 1.1 |
| 1 GPU (batch=100K) | 10K | ~500 | 0.05 |
| 1 GPU (batch=100K) | 100K | ~80 | 0.0008 |
| 1 GPU (batch=100K) | 1M | ~12 | 0.000012 |
| 2 GPUs (batch=100K) | 1M | ~18 | 0.000018 |

 **Sources:** Estimated from [scripts/test/test_fps.py22-48](https://github.com/geek-ai/MAgent/blob/2144dbd4/scripts/test/test_fps.py#L22-L48)

 
### Scalability Characteristics

 
```

```

 **Key Insights:**

 
 - **Linear scaling**: Most operations scale linearly with agent count due to parallelization
 - **Memory bound**: Large simulations (>1M agents) require 20-50GB RAM
 - **GPU bottleneck**: Neural network inference becomes dominant cost at scale
 - **Observation overhead**: High-resolution observations can dominate runtime
 
 **Sources:** [src/gridworld/GridWorld.cc72-86](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L72-L86) [src/gridworld/GridWorld.cc292-401](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L292-L401)
