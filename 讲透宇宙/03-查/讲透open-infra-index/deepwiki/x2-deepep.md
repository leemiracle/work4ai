<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/open-infra-index · extra page DeepEP · fetched 2026-10-30 -->

# DeepEP

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

DeepEP is the expert parallel (EP) communication library designed specifically for efficient MoE (Mixture of Experts) model training and inference across multiple nodes. This component handles the complex all-to-all communication patterns required when distributing expert computations across GPU clusters, optimizing both high-throughput training scenarios and low-latency inference workloads.

DeepEP focuses exclusively on expert-level parallelization communication. For pipeline parallelism strategies, see [DualPipe](#2.2.2). For expert workload distribution and balancing, see [EPLB](#2.2.3).

## System Architecture

DeepEP serves as the communication backbone for MoE model architectures, particularly those with large numbers of experts like DeepSeek-V3's 256-expert configuration where only 8 experts are active per layer.

### High-Level Integration

```mermaid
graph TB
    subgraph "MoE Model Layer"
        TOKENS["Input Tokens"]
        ROUTER["Expert Router<br/>Select 8 of 256"]
        EXPERTS["Distributed Experts<br/>E1, E2, ..., E256"]
        OUTPUT["Expert Outputs"]
    end
    
    subgraph "DeepEP Communication"
        DEEPEP_CORE["DeepEP Core Library"]
        ALLTOALL["All-to-All Patterns"]
        DISPATCH["FP8 Dispatch"]
        OVERLAP["Computation-Communication<br/>Overlapping"]
    end
    
    subgraph "Network Infrastructure"
        NVLINK["NVLink<br/>Intranode"]
        RDMA["RDMA Networks<br/>Internode"]
    end
    
    subgraph "Load Balancing"
        EPLB["EPLB Load Balancer"]
    end
    
    TOKENS --> ROUTER
    ROUTER --> DEEPEP_CORE
    DEEPEP_CORE --> ALLTOALL
    DEEPEP_CORE --> DISPATCH
    DEEPEP_CORE --> OVERLAP
    
    ALLTOALL --> EXPERTS
    EXPERTS --> OUTPUT
    
    DEEPEP_CORE --> NVLINK
    DEEPEP_CORE --> RDMA
    
    DEEPEP_CORE --> EPLB
```

Sources: [README.md:42-52]()

### Communication Pattern Architecture

```mermaid
graph TB
    subgraph "Training Phase"
        TRAIN_INPUT["Training Batch"]
        TRAIN_ALLTOALL["High-Throughput<br/>All-to-All"]
        TRAIN_EXPERTS["Expert Processing<br/>Batch Optimization"]
        TRAIN_OUTPUT["Training Gradients"]
    end
    
    subgraph "Inference Prefilling Phase"
        PREFILL_INPUT["Prefill Tokens"]
        PREFILL_ALLTOALL["High-Throughput<br/>All-to-All"]
        PREFILL_EXPERTS["Expert Processing<br/>EP32/DP32"]
        PREFILL_KV["KV Cache Generation"]
    end
    
    subgraph "Inference Decoding Phase"
        DECODE_INPUT["Single Token"]
        DECODE_ALLTOALL["Low-Latency<br/>All-to-All"]
        DECODE_EXPERTS["Expert Processing<br/>EP144/DP144"]
        DECODE_OUTPUT["Generated Token"]
    end
    
    subgraph "DeepEP Kernel Selection"
        KERNEL_SELECTOR["DeepEP Kernel Selector"]
        HIGH_THROUGHPUT["High-Throughput Kernels"]
        LOW_LATENCY["Low-Latency Kernels"]
        FP8_DISPATCH["Native FP8 Dispatch"]
    end
    
    TRAIN_INPUT --> TRAIN_ALLTOALL
    TRAIN_ALLTOALL --> TRAIN_EXPERTS
    TRAIN_EXPERTS --> TRAIN_OUTPUT
    
    PREFILL_INPUT --> PREFILL_ALLTOALL
    PREFILL_ALLTOALL --> PREFILL_EXPERTS
    PREFILL_EXPERTS --> PREFILL_KV
    
    DECODE_INPUT --> DECODE_ALLTOALL
    DECODE_ALLTOALL --> DECODE_EXPERTS
    DECODE_EXPERTS --> DECODE_OUTPUT
    
    TRAIN_ALLTOALL --> KERNEL_SELECTOR
    PREFILL_ALLTOALL --> KERNEL_SELECTOR
    DECODE_ALLTOALL --> KERNEL_SELECTOR
    
    KERNEL_SELECTOR --> HIGH_THROUGHPUT
    KERNEL_SELECTOR --> LOW_LATENCY
    KERNEL_SELECTOR --> FP8_DISPATCH
```

Sources: [README.md:47-52]()

## Communication Patterns

### All-to-All Communication

DeepEP implements optimized all-to-all communication patterns that are fundamental to expert parallel processing in MoE architectures. When tokens are routed to different experts across multiple nodes, the system must efficiently redistribute data according to expert assignments.

| Communication Type | Optimization Target | Use Case | Parallelism Strategy |
|-------------------|-------------------|----------|---------------------|
| High-Throughput | Maximize data transfer rate | Training, Prefilling | EP32/DP32 (4 nodes) |
| Low-Latency | Minimize communication delay | Decoding | EP144/DP144 (18 nodes) |

### Network Layer Support

DeepEP provides native support for both intranode and internode communication:

- **NVLink**: High-bandwidth GPU-to-GPU communication within nodes
- **RDMA**: Low-latency inter-node communication across the cluster

The library automatically selects the appropriate communication path based on the source and destination GPU locations.

Sources: [README.md:48]()

## Performance Characteristics

### Kernel Optimization Strategies

DeepEP employs different kernel optimizations depending on the workload phase:

```mermaid
graph LR
    subgraph "Training Workload"
        TRAIN_BATCH["Large Batch Size"]
        TRAIN_KERNEL["High-Throughput Kernel"]
        TRAIN_PERF["Optimize for<br/>Aggregate Bandwidth"]
    end
    
    subgraph "Inference Prefilling"
        PREFILL_BATCH["Medium Batch Size"]
        PREFILL_KERNEL["High-Throughput Kernel"]
        PREFILL_PERF["Optimize for<br/>Token Throughput"]
    end
    
    subgraph "Inference Decoding"
        DECODE_BATCH["Small Batch Size<br/>Single Tokens"]
        DECODE_KERNEL["Low-Latency Kernel"]
        DECODE_PERF["Optimize for<br/>Response Time"]
    end
    
    TRAIN_BATCH --> TRAIN_KERNEL
    TRAIN_KERNEL --> TRAIN_PERF
    
    PREFILL_BATCH --> PREFILL_KERNEL
    PREFILL_KERNEL --> PREFILL_PERF
    
    DECODE_BATCH --> DECODE_KERNEL
    DECODE_KERNEL --> DECODE_PERF
```

Sources: [README.md:49-50]()

### FP8 Support

DeepEP provides native FP8 dispatch support, enabling efficient mixed-precision communication patterns that align with the FP8 computations performed by expert layers. This reduces memory bandwidth requirements and improves overall system throughput.

Sources: [README.md:51]()

## Integration with System Components

### Expert Parallel Load Balancer Integration

DeepEP works closely with EPLB to ensure efficient expert utilization:

```mermaid
graph TB
    subgraph "Token Routing Flow"
        INPUT_TOKENS["Input Tokens"]
        EXPERT_ROUTER["Expert Router<br/>Token Assignment"]
        DEEPEP_COMM["DeepEP Communication<br/>All-to-All Redistribution"]
        EXPERT_COMPUTE["Expert Computation<br/>Distributed Processing"]
        EPLB_BALANCE["EPLB Load Balancing<br/>Dynamic Adjustment"]
        OUTPUT_GATHER["Output Gathering<br/>All-to-All Collection"]
    end
    
    INPUT_TOKENS --> EXPERT_ROUTER
    EXPERT_ROUTER --> DEEPEP_COMM
    DEEPEP_COMM --> EXPERT_COMPUTE
    EXPERT_COMPUTE --> EPLB_BALANCE
    EPLB_BALANCE --> OUTPUT_GATHER
    OUTPUT_GATHER --> DEEPEP_COMM
```

Sources: [README.md:42-52]()

### Computation-Communication Overlapping

DeepEP provides flexible GPU resource control that enables computation-communication overlapping strategies. This allows the system to hide communication latency by performing expert computations while data transfers are in progress.

The library supports dual-batch overlapping during prefilling phases and multi-stage pipeline overlapping during decoding phases, working in coordination with other system components like DualPipe.

Sources: [README.md:52]()

## Deployment Architecture

DeepEP operates across the distributed GPU infrastructure supporting DeepSeek-V3/R1 models:

### Node Configuration

| Phase | Expert Parallelism | Data Parallelism | Nodes per Unit |
|-------|------------------|-----------------|----------------|
| Prefilling | EP32 | DP32 | 4 |
| Decoding | EP144 | DP144 | 18 |

### Resource Management

DeepEP manages communication resources across the cluster, coordinating with the underlying RDMA network infrastructure and NVLink topology to optimize data movement patterns for the 256-expert MoE architecture where only 8 experts are active per layer.

Sources: [README.md:42-52]()

---

