<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/jaxpp · page 3 Performance Optimization · fetched 2026-10-26 -->

# Performance Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PERF_GUIDE.md](PERF_GUIDE.md)

</details>



This page provides an overview of performance optimization strategies for training Large Language Models (LLMs) using JaxPP. It focuses on how to efficiently scale model training across multiple devices while maximizing throughput and minimizing memory usage. For specific implementation details of parallelization techniques, see [Parallelization Strategies](#3.1). For memory-specific optimizations, see [Memory Management](#3.2).

## Optimization Philosophy

The primary goal of JaxPP's performance optimization is to maximize training throughput (tokens/second) while efficiently utilizing available hardware. The recommended approach follows a key principle:

> Make Tensor Parallelism (TP) and Pipeline Parallelism (PP) as small as possible—just enough to fit the model with activations in memory—then scale Data Parallelism (DP) for near-linear throughput improvements.

Sources: [PERF_GUIDE.md:10-15]()

## Training Step Decomposition

When using pipeline parallelism, a training step can be decomposed into three distinct phases, each with different performance characteristics and optimization strategies.

```mermaid
flowchart LR
    subgraph "Training Step Phases"
        direction TB
        A["Before GA Loop"] --> B["GA Loop"]
        B --> C["After GA Loop"]
        
        subgraph "A: Before Loop"
            direction TB
            A1["Cast fp32 → bf16"] --> A2["All-gather across DP"]
            A2 --> A3["Zero gradients"]
        end
        
        subgraph "B: GA Loop (90% compute)"
            direction TB
            B1["Forward pass"] --> B2["Backward pass"]
            B2 --> B3["Accumulate gradients"]
        end
        
        subgraph "C: After Loop"
            direction TB
            C1["Reduce-scatter gradients"] --> C2["Apply optimizer"]
            C2 --> C3["Update parameters"]
        end
    end
```

Sources: [PERF_GUIDE.md:18-71]()

### Before Gradient Accumulation Loop

In this phase:

1. "Master" (fp32) model parameters are cast to bf16
2. All-gather operation is performed across data-parallel ranks
3. Initial zero gradients are allocated for accumulation

```mermaid
sequenceDiagram
    participant DP1 as "DP Rank 1"
    participant DP2 as "DP Rank 2"
    participant DPN as "DP Rank N"
    
    Note over DP1,DPN: Each rank has its own θ_DP (fp32 parameters)
    DP1->>DP1: Cast θ_DP to bf16
    DP2->>DP2: Cast θ_DP to bf16
    DPN->>DPN: Cast θ_DP to bf16
    
    Note over DP1,DPN: All-gather communication
    DP1->>DP2: Share parameters
    DP1->>DPN: Share parameters
    DP2->>DP1: Share parameters
    DP2->>DPN: Share parameters
    DPN->>DP1: Share parameters
    DPN->>DP2: Share parameters
    
    Note over DP1,DPN: All ranks now have complete θ̂ (replicated bf16 parameters)
    DP1->>DP1: Allocate ∇θ̂ (zero gradients)
    DP2->>DP2: Allocate ∇θ̂ (zero gradients)
    DPN->>DPN: Allocate ∇θ̂ (zero gradients)
```

Sources: [PERF_GUIDE.md:29-42]()

### Gradient Accumulation Loop

This is the most computation-heavy phase (approximately 90% of total computation). Key characteristics:

- No DP communication occurs
- Memory is primarily needed for microbatch activations
- Each iteration processes a microbatch of size: batch_size / gradient_accumulation_steps

Optimization techniques in this phase include:
- Pipeline scheduling (e.g., Zero Bubble)
- Activation rematerialization (trading computation for memory)
- Activation offloading for older microbatches

```mermaid
flowchart TB
    subgraph "GA Loop Optimization Techniques"
        direction TB
        A["GA Loop Memory Usage"] --> B["Activation Management"]
        A --> C["Computation Efficiency"]
        
        B --> B1["Rematerialization"]
        B --> B2["Activation Offloading"]
        
        C --> C1["Minimize TP/PP Collectives"]
        C --> C2["Reduce GA Steps"]
        C --> C3["Optimize Sharding Rules"]
    end
```

Sources: [PERF_GUIDE.md:44-62]()

### After Gradient Accumulation Loop

In this final phase:

1. DP-ranks perform reduce-scatter of their gradients to synchronize them
2. Each rank updates its portion of the model parameters
3. Optimizer state is updated

```mermaid
sequenceDiagram
    participant DP1 as "DP Rank 1"
    participant DP2 as "DP Rank 2"
    participant DPN as "DP Rank N"
    
    Note over DP1,DPN: Each rank has accumulated gradients ∇θ̂
    
    Note over DP1,DPN: Reduce-scatter communication
    DP1->>DP1: Prepare gradient shard
    DP2->>DP2: Prepare gradient shard
    DPN->>DPN: Prepare gradient shard
    
    DP1->>DP2: Share gradient part
    DP1->>DPN: Share gradient part
    DP2->>DP1: Share gradient part
    DP2->>DPN: Share gradient part
    DPN->>DP1: Share gradient part
    DPN->>DP2: Share gradient part
    
    Note over DP1,DPN: Each rank now has ∇θ̂_DP (its portion of gradients)
    DP1->>DP1: Update parameters θ_DP
    DP2->>DP2: Update parameters θ_DP
    DPN->>DPN: Update parameters θ_DP
    
    DP1->>DP1: Update optimizer state μθ_DP, νθ_DP
    DP2->>DP2: Update optimizer state μθ_DP, νθ_DP
    DPN->>DPN: Update optimizer state μθ_DP, νθ_DP
```

Sources: [PERF_GUIDE.md:63-71]()

## Memory-Performance Tradeoffs

Training LLMs involves several memory-performance tradeoffs that can be adjusted based on your specific hardware and model requirements.

| Technique | Memory Impact | Performance Impact | When to Use |
|-----------|---------------|-------------------|-------------|
| Gradient Accumulation | ↓ Memory usage by processing smaller microbatches | ↑ Training step time due to more loop iterations | When batch size is too large to fit in memory |
| Rematerialization | ↓ Memory usage by discarding and recomputing activations | ↑ Computation cost | When activations are a memory bottleneck |
| Precision Reduction | ↓ Memory usage by using lower precision (e.g., bf16) | Minimal impact if hardware supports it | Almost always beneficial on modern hardware |
| Activation Offloading | ↓ Memory usage by offloading older microbatch activations | ↑ I/O overhead | When compute/memory ratio is high |
| Optimizer State Offloading | ↓ Memory usage | ↑ I/O overhead | When using small DP with large optimizer state |

Sources: [PERF_GUIDE.md:22-25](), [PERF_GUIDE.md:48-55]()

## Scaling Strategy Recommendations

```mermaid
flowchart TD
    A["Start with model"] --> B["Model fits in single device?"]
    B -->|"Yes"| C["Use single device"]
    B -->|"No"| D["Add minimal TP to fit layers"]
    D --> E["Model with TP fits in single device?"]
    E -->|"Yes"| F["Use TP only"]
    E -->|"No"| G["Add minimal PP to fit model"]
    G --> H["Scale with DP for throughput"]
    H --> I["Optimize GA steps, scheduling"]
    I --> J["Fine-tune with rematerialization/offloading"]
```

### Practical Guidelines

1. **Minimize PP depth**: Keep pipeline stages to a minimum to reduce pipeline bubbles
2. **Reduce GA steps**: Minimize gradient accumulation iterations to reduce overhead, potentially at the cost of a higher bubble which can be recovered with better schedules
3. **Optimize communication**: In the GA loop, optimize TP/EP/CP/SP sharding rules to minimize collective operations
4. **Balance rematerialization**: Trade memory for computation by rematerializing activations when needed
5. **Consider memory hierarchy**: For models with small DP, consider offloading optimizer state to free up memory

Sources: [PERF_GUIDE.md:9-16](), [PERF_GUIDE.md:54-62]()

## Performance Debugging

When encountering performance issues, consider the following diagnostic approach:

```mermaid
flowchart TD
    A["Performance Issue"] --> B["Identify bottleneck"]
    
    B --> C["Memory bottleneck?"]
    C -->|"Yes"| D["Memory Optimization"]
    D --> D1["Increase TP/PP"]
    D --> D2["Add rematerialization"]
    D --> D3["Offload activations/optimizer state"]
    
    B --> E["Computation bottleneck?"]
    E -->|"Yes"| F["Computation Optimization"]
    F --> F1["Optimize TP/PP communication"]
    F --> F2["Improve pipeline scheduling"]
    F --> F3["Consider XLA flags"]
    
    B --> G["Communication bottleneck?"]
    G -->|"Yes"| H["Communication Optimization"]
    H --> H1["Reduce collective operations"]
    H --> H2["Use optimal DP sharding"]
    H --> H3["Optimize network topology"]
```

## Additional Resources

For more detailed information on performance optimization:

- Jax's scaling book on parallelization strategies: [Link to JAX scaling book](https://jax-ml.github.io/scaling-book/training/)
- The Ultra-Scale Playbook for additional explanations and visualizations
- For B200 and other XLA flags, refer to [NVIDIA JAX-Toolbox documentation](https://github.com/NVIDIA/JAX-Toolbox/blob/main/rosetta/docs/GPU_performance.md#tips-for-good-llm-training-performance-on-blackwell-b200)

Sources: [PERF_GUIDE.md:3-7]()

---

