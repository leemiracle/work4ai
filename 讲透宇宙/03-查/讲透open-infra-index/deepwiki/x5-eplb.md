<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/open-infra-index · extra page EPLB · fetched 2026-10-30 -->

# EPLB

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

EPLB (Expert-Parallel Load Balancer) is a specialized load balancing system designed for Mixture of Experts (MoE) model architectures, specifically optimized for DeepSeek-V3 and R1 models. This document covers EPLB's role in managing workload distribution across expert-parallel configurations, its integration with the broader inference pipeline, and its optimization strategies for both prefill and decode phases.

For information about the underlying expert-parallel communication patterns, see [DeepEP](#2.2.1). For broader parallelism strategies, see [DualPipe](#2.2.2).

## Architecture Overview

EPLB operates within DeepSeek's MoE inference system, managing load distribution across 256 experts where only 8 are active per layer. The load balancer addresses the fundamental challenge of expert utilization imbalance that can occur during both training and inference phases.

### System Integration

```mermaid
graph TB
    subgraph "Request Flow"
        INPUT["Input Tokens"]
        PREFILL["Prefill Phase<br/>EP32/DP32"]
        DECODE["Decode Phase<br/>EP144/DP144"]
        OUTPUT["Output Tokens"]
    end
    
    subgraph "EPLB Core Components"
        ROUTER["Expert Router<br/>Selects 8 of 256"]
        LOAD_MONITOR["Load Monitor<br/>Track Expert Utilization"]
        BALANCER["Load Balancer<br/>Redistribute Workload"]
        SCHEDULER["Expert Scheduler<br/>Optimize Assignment"]
    end
    
    subgraph "Expert Layer"
        EXPERT_1["Expert 1"]
        EXPERT_8["Expert 8"]
        EXPERT_DOTS["..."]
        EXPERT_256["Expert 256"]
    end
    
    subgraph "Communication Layer"
        DEEPEP["DeepEP<br/>All-to-All Communication"]
        OVERLAP_ENGINE["Communication-Computation<br/>Overlap Engine"]
    end
    
    INPUT --> PREFILL
    PREFILL --> DECODE
    DECODE --> OUTPUT
    
    PREFILL --> ROUTER
    DECODE --> ROUTER
    ROUTER --> LOAD_MONITOR
    LOAD_MONITOR --> BALANCER
    BALANCER --> SCHEDULER
    
    SCHEDULER --> EXPERT_1
    SCHEDULER --> EXPERT_8
    SCHEDULER --> EXPERT_256
    
    EXPERT_1 --> DEEPEP
    EXPERT_8 --> DEEPEP
    EXPERT_256 --> DEEPEP
    DEEPEP --> OVERLAP_ENGINE
```

Sources: [README.md:70-71](), [README.md:89-105]()

## Load Balancing Strategies

EPLB implements distinct load balancing strategies optimized for different phases of MoE model inference, addressing the varying computational and communication patterns between prefill and decode operations.

### Prefill Phase Balancing

During the prefill phase, EPLB manages load distribution across EP32/DP32 configurations with 4 nodes per processing unit. The primary focus is on token-level load balancing to ensure efficient parallel processing of input sequences.

```mermaid
graph TB
    subgraph "Prefill Load Balancing"
        TOKEN_BATCH["Input Token Batch<br/>Variable Length Sequences"]
        TOKEN_ANALYZER["Token Distribution<br/>Analyzer"]
        EXPERT_PREDICTOR["Expert Selection<br/>Predictor"]
        LOAD_CALCULATOR["Load Calculator<br/>Per Expert"]
    end
    
    subgraph "Expert Assignment"
        ASSIGNMENT_ENGINE["Assignment Engine"]
        REBALANCE_LOGIC["Rebalancing Logic"]
        MIGRATION_HANDLER["Token Migration<br/>Handler"]
    end
    
    subgraph "Execution Units"
        NODE_1["Node 1<br/>EP32 Slice"]
        NODE_2["Node 2<br/>EP32 Slice"]
        NODE_3["Node 3<br/>EP32 Slice"]
        NODE_4["Node 4<br/>EP32 Slice"]
    end
    
    TOKEN_BATCH --> TOKEN_ANALYZER
    TOKEN_ANALYZER --> EXPERT_PREDICTOR
    EXPERT_PREDICTOR --> LOAD_CALCULATOR
    
    LOAD_CALCULATOR --> ASSIGNMENT_ENGINE
    ASSIGNMENT_ENGINE --> REBALANCE_LOGIC
    REBALANCE_LOGIC --> MIGRATION_HANDLER
    
    ASSIGNMENT_ENGINE --> NODE_1
    ASSIGNMENT_ENGINE --> NODE_2
    ASSIGNMENT_ENGINE --> NODE_3
    ASSIGNMENT_ENGINE --> NODE_4
```

Sources: [README.md:97](), [README.md:91-94]()

### Decode Phase Balancing

The decode phase operates under EP144/DP144 configurations with 18 nodes per processing unit, requiring different load balancing considerations due to the sequential nature of token generation and KV cache management.

```mermaid
graph TB
    subgraph "Decode Load Balancing"
        KV_CACHE["KV Cache<br/>Management"]
        SEQUENCE_TRACKER["Active Sequence<br/>Tracker"]
        EXPERT_UTILIZATION["Real-time Expert<br/>Utilization Monitor"]
    end
    
    subgraph "Dynamic Rebalancing"
        UTILIZATION_ANALYZER["Utilization<br/>Analyzer"]
        REBALANCE_TRIGGER["Rebalancing<br/>Trigger Logic"]
        MIGRATION_SCHEDULER["Migration<br/>Scheduler"]
    end
    
    subgraph "EP144 Node Groups"
        GROUP_1["Nodes 1-9<br/>Expert Subset"]
        GROUP_2["Nodes 10-18<br/>Expert Subset"]
        GROUP_DOTS["..."]
        GROUP_N["Nodes N-144<br/>Expert Subset"]
    end
    
    KV_CACHE --> SEQUENCE_TRACKER
    SEQUENCE_TRACKER --> EXPERT_UTILIZATION
    EXPERT_UTILIZATION --> UTILIZATION_ANALYZER
    
    UTILIZATION_ANALYZER --> REBALANCE_TRIGGER
    REBALANCE_TRIGGER --> MIGRATION_SCHEDULER
    
    MIGRATION_SCHEDULER --> GROUP_1
    MIGRATION_SCHEDULER --> GROUP_2
    MIGRATION_SCHEDULER --> GROUP_N
```

Sources: [README.md:97](), [README.md:91-94]()

## Performance Metrics and Optimization

EPLB contributes to the overall system performance by maintaining high expert utilization and minimizing load imbalance penalties. The system achieves significant throughput improvements in production deployments.

### Key Performance Indicators

| Metric | Value | Description |
|--------|-------|-------------|
| Input Tokens/sec/node | 73.7k | Per H800 node throughput |
| Output Tokens/sec/node | 14.8k | Per H800 node generation rate |
| Expert Utilization | Variable | Balanced across 256 experts |
| Cost Efficiency | 545% profit margin | Production cost optimization |

### Load Balancing Algorithms

EPLB employs sophisticated algorithms to manage expert assignment and workload distribution:

```mermaid
flowchart TB
    subgraph "Load Balancing Algorithm Flow"
        START["Request Arrival"]
        ANALYZE["Analyze Current<br/>Expert Load"]
        PREDICT["Predict Expert<br/>Requirements"]
        ASSIGN["Assign Experts<br/>to Request"]
        MONITOR["Monitor Execution<br/>Performance"]
        ADJUST["Adjust Future<br/>Assignments"]
    end
    
    subgraph "Optimization Criteria"
        THROUGHPUT["Maximize<br/>Throughput"]
        LATENCY["Minimize<br/>Latency"]
        UTILIZATION["Balance Expert<br/>Utilization"]
        COMMUNICATION["Minimize Communication<br/>Overhead"]
    end
    
    START --> ANALYZE
    ANALYZE --> PREDICT
    PREDICT --> ASSIGN
    ASSIGN --> MONITOR
    MONITOR --> ADJUST
    ADJUST --> ANALYZE
    
    ASSIGN --> THROUGHPUT
    ASSIGN --> LATENCY
    ASSIGN --> UTILIZATION
    ASSIGN --> COMMUNICATION
```

Sources: [README.md:96-99](), [README.md:91-94]()

## Integration with Communication Systems

EPLB works closely with DeepEP to optimize communication patterns during expert-parallel execution. The integration focuses on minimizing all-to-all communication overhead while maintaining load balance.

### Communication-Computation Overlap

The load balancer coordinates with communication overlap strategies to hide latency during expert execution:

```mermaid
graph TB
    subgraph "EPLB Communication Integration"
        LOAD_DECISION["Load Balancing<br/>Decision"]
        COMM_PATTERN["Communication<br/>Pattern Analysis"]
        OVERLAP_COORD["Overlap<br/>Coordination"]
    end
    
    subgraph "DeepEP Integration"
        ALL_TO_ALL["All-to-All<br/>Communication"]
        NVLINK_COMM["NVLink<br/>Communication"]
        RDMA_COMM["RDMA<br/>Communication"]
    end
    
    subgraph "Overlap Strategies"
        DUAL_BATCH["Dual-batch<br/>Overlapping"]
        PIPELINE_5["5-stage<br/>Pipeline"]
        ASYNC_COMM["Async Communication<br/>Scheduling"]
    end
    
    LOAD_DECISION --> COMM_PATTERN
    COMM_PATTERN --> OVERLAP_COORD
    
    OVERLAP_COORD --> ALL_TO_ALL
    OVERLAP_COORD --> NVLINK_COMM
    OVERLAP_COORD --> RDMA_COMM
    
    ALL_TO_ALL --> DUAL_BATCH
    NVLINK_COMM --> PIPELINE_5
    RDMA_COMM --> ASYNC_COMM
```

Sources: [README.md:47-52](), [README.md:73-74]()

## Production Deployment Considerations

EPLB is battle-tested in production environments serving DeepSeek V3 and R1 models. The system handles dynamic workload variations and maintains consistent performance under varying load conditions.

### Scalability and Resource Management

The load balancer adapts to different cluster configurations and resource availability:

- **Node-level scaling**: Automatically adjusts to available H800 nodes
- **Memory management**: Coordinates with KV cache systems for optimal memory utilization  
- **Network optimization**: Minimizes cross-node communication through intelligent expert placement
- **Fault tolerance**: Handles node failures and expert reassignment dynamically

### Monitoring and Observability

EPLB provides detailed metrics for system monitoring and performance analysis:

- Real-time expert utilization tracking
- Load imbalance detection and alerting
- Communication pattern analysis
- Performance degradation early warning systems

Sources: [README.md:96-99](), [README.md:89-105]()

---

