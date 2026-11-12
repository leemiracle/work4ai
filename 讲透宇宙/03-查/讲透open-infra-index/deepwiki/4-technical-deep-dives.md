<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/open-infra-index · page 4 Technical Deep Dives · fetched 2026-10-30 -->

# Technical Deep Dives

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md](202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md)

</details>



## Purpose and Scope

This section provides in-depth technical examinations of specific optimization techniques implemented in the DeepSeek infrastructure. These deep dives focus on core performance optimization strategies that enable the exceptional throughput and efficiency demonstrated in DeepSeek's V3/R1 models.

For a high-level overview of individual infrastructure components, see [Components](#2). For the complete architecture of the inference system, see [DeepSeek V3/R1 Inference System](#3).

## Communication-Computation Overlapping

Communication-computation overlapping enables concurrent execution of data transfer and computational operations in expert parallelism (EP) architectures. DeepSeek implements distinct strategies for prefilling and decoding phases to maximize GPU utilization.

### Dual-Batch Strategy for Prefilling Phase

During prefilling, DeepSeek employs a dual-batch overlap strategy where batches are split into two microbatches that execute alternately. The communication cost of one microbatch is hidden behind the computation of the other.

**Dual-Batch Prefilling Pipeline**
```mermaid
gantt
    title "Dual-Batch Communication-Computation Overlap (Prefilling)"
    dateFormat s
    axisFormat %S
    
    section "Microbatch A"
    "Comm A1" :microbatch_a_comm1, 0, 1s
    "Comp A1" :microbatch_a_comp1, after microbatch_a_comm1, 2s
    "Comm A2" :microbatch_a_comm2, after microbatch_a_comp1, 1s
    "Comp A2" :microbatch_a_comp2, after microbatch_a_comm2, 2s
    
    section "Microbatch B"
    "Comm B1" :microbatch_b_comm1, 1s, 1s
    "Comp B1" :microbatch_b_comp1, after microbatch_b_comm1, 2s
    "Comm B2" :microbatch_b_comm2, after microbatch_b_comp1, 1s
    "Comp B2" :microbatch_b_comp2, after microbatch_b_comm2, 2s
```

**Architecture: EP32/DP32 (4 nodes per deployment unit)**
- Each GPU handles 9 routed experts and 1 shared expert
- 32 redundant routed experts across the deployment unit
- Alternating microbatch execution hides `DeepEP` all-to-all communication latency

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:22-30]()

### 5-Stage Pipeline for Decoding Phase

During decoding, execution durations of different stages are unbalanced. DeepSeek subdivides the attention layer into two steps and uses a 5-stage pipeline to achieve seamless communication-computation overlapping.

**5-Stage Decoding Pipeline**
```mermaid
flowchart LR
    subgraph "5-Stage Pipeline Architecture"
        Stage1["Stage 1<br/>Pre-Attention<br/>Preparation"]
        Stage2["Stage 2<br/>FlashMLA<br/>Attention Part 1"]
        Stage3["Stage 3<br/>Expert Routing<br/>+ DeepEP Comm"]
        Stage4["Stage 4<br/>Expert Computation<br/>DeepGEMM FP8"]
        Stage5["Stage 5<br/>FlashMLA<br/>Attention Part 2"]
    end
    
    Stage1 --> Stage2
    Stage2 --> Stage3
    Stage3 --> Stage4
    Stage4 --> Stage5
    
    %% Overlapping indicators
    Stage2 -.-> |"Overlapped with"| Stage3
    Stage3 -.-> |"Overlapped with"| Stage4
    Stage4 -.-> |"Overlapped with"| Stage5
```

**Architecture: EP144/DP144 (18 nodes per deployment unit)**
- Each GPU manages 2 routed experts and 1 shared expert
- 256 total experts with 8 active per layer
- Pipeline stages overlap communication with computation phases

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:21-36]()

### Performance Impact

Measured performance with overlapping optimizations on H800 GPUs:

| Phase | Throughput | Architecture | Key Components |
|-------|------------|--------------|----------------|
| Prefilling | 73.7k input tokens/sec/H800 | EP32/DP32, 4 nodes | Dual-batch + DeepEP + DeepGEMM |
| Decoding | 14.8k output tokens/sec/H800 | EP144/DP144, 18 nodes | 5-stage pipeline + FlashMLA |

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:76-77]()

## Load Balancing Strategies

DeepSeek implements three specialized load balancing systems to address performance bottlenecks in large-scale expert parallelism across multiple GPU nodes.

### Prefill Load Balancer

**Problem**: Varying request counts and sequence lengths across DP instances cause imbalanced core-attention computation and dispatch send load.

**Optimization Objectives**:
- Balance core-attention computation across GPUs (computational load balancing)
- Equalize input token counts per GPU (dispatch send load balancing)

```mermaid
flowchart TB
    subgraph "Prefill Load Balancing System"
        Requests["Incoming Requests<br/>Variable Length Sequences"]
        PLB["Prefill Load Balancer"]
        
        subgraph "DP Instance 1 (4 nodes)"
            DP1GPU1["GPU 1<br/>9 routed + 1 shared expert"]
            DP1GPU2["GPU 2<br/>9 routed + 1 shared expert"]
            DP1GPU8["GPU 8<br/>9 routed + 1 shared expert"]
        end
        
        subgraph "DP Instance 2 (4 nodes)"
            DP2GPU1["GPU 1<br/>9 routed + 1 shared expert"]
            DP2GPU2["GPU 2<br/>9 routed + 1 shared expert"]
            DP2GPU8["GPU 8<br/>9 routed + 1 shared expert"]
        end
        
        AttentionBalance["Core-Attention<br/>Load Balancing"]
        TokenBalance["Input Token<br/>Count Balancing"]
    end
    
    Requests --> PLB
    PLB --> AttentionBalance
    PLB --> TokenBalance
    AttentionBalance --> DP1GPU1 & DP1GPU2 & DP1GPU8
    TokenBalance --> DP2GPU1 & DP2GPU2 & DP2GPU8
```

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:41-45]()

### Decode Load Balancer

**Problem**: Uneven request counts and sequence lengths across DP instances cause disparities in core-attention computation (linked to KVCache usage) and dispatch send load.

**Optimization Objectives**:
- Balance KVCache usage across GPUs (core-attention computational load balancing)
- Equalize request counts per GPU (dispatch send load balancing)

```mermaid
flowchart TB
    subgraph "Decode Load Balancing System"
        ActiveReqs["Active Generation Requests<br/>Variable KVCache Usage"]
        DLB["Decode Load Balancer"]
        
        subgraph "DP Instance 1 (18 nodes)"
            DP1GPU1_D["GPU 1<br/>2 routed + 1 shared expert"]
            DP1GPU2_D["GPU 2<br/>2 routed + 1 shared expert"]
            DP1GPU144_D["GPU 144<br/>2 routed + 1 shared expert"]
        end
        
        KVCacheBalance["KVCache Usage<br/>Load Balancing"]
        RequestBalance["Request Count<br/>Balancing"]
        
        subgraph "KVCache Management"
            KVCache["Paged KV Cache<br/>Block Size 64<br/>Average 4,989 tokens/request"]
        end
    end
    
    ActiveReqs --> DLB
    DLB --> KVCacheBalance
    DLB --> RequestBalance
    KVCacheBalance --> DP1GPU1_D & DP1GPU2_D & DP1GPU144_D
    RequestBalance --> DP1GPU1_D & DP1GPU2_D & DP1GPU144_D
    DP1GPU1_D & DP1GPU2_D & DP1GPU144_D --> KVCache
```

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:46-50](), [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:75]()

### Expert-Parallel Load Balancer (EPLB)

**Problem**: Inherently high-load experts result in imbalanced expert computational workloads across different GPUs.

**Optimization Objective**: Balance expert computation on each GPU by minimizing the maximum dispatch receive load across all GPUs.

```mermaid
flowchart TB
    subgraph "EPLB System Architecture"
        ExpertRouter["Expert Router<br/>Selects 8 of 256 experts"]
        EPLB_Core["EPLB Core<br/>Load Balancer"]
        
        subgraph "256 Expert Distribution"
            HighLoadExperts["High-Load Experts<br/>(e.g., Expert 1, 15, 42)"]
            MediumLoadExperts["Medium-Load Experts<br/>(e.g., Expert 88, 134, 201)"]
            LowLoadExperts["Low-Load Experts<br/>(e.g., Expert 99, 156, 233)"]
        end
        
        subgraph "GPU Load Balancing"
            LoadAnalysis["Load Analysis<br/>Monitor dispatch receive load"]
            RebalanceDecision["Rebalancing Decision<br/>Minimize max GPU load"]
            ExpertReassignment["Expert Reassignment<br/>Across GPU nodes"]
        end
        
        subgraph "Performance Monitoring"
            GPUUtilization["GPU Utilization<br/>Monitoring"]
            ThroughputTracking["Throughput Tracking<br/>Per Expert"]
        end
    end
    
    ExpertRouter --> HighLoadExperts & MediumLoadExperts & LowLoadExperts
    HighLoadExperts & MediumLoadExperts & LowLoadExperts --> EPLB_Core
    EPLB_Core --> LoadAnalysis
    LoadAnalysis --> RebalanceDecision
    RebalanceDecision --> ExpertReassignment
    ExpertReassignment --> GPUUtilization & ThroughputTracking
```

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:51-54]()

## Economic Analysis

DeepSeek's inference system demonstrates exceptional economic efficiency through technical optimizations, achieving a 545% profit margin based on theoretical R1 pricing.

### Production Metrics (24-hour period: UTC+8 02/27/2025 12:00 PM to 02/28/2025 12:00 PM)

**Infrastructure Scale**:
- Peak node occupancy: 278 H800 nodes (V3 + R1 combined)
- Average occupancy: 226.75 H800 nodes
- Dynamic scaling: Full deployment during peak daytime, reduced deployment at night
- Hardware cost: $2/hour per H800 GPU

**Traffic Statistics**:
- Total input tokens: 608B tokens/day
- Cache hit rate: 56.3% (342B tokens hit on-disk KV cache)
- Total output tokens: 168B tokens/day
- Average output speed: 20-22 tokens/second
- Average KV cache length: 4,989 tokens per output token

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:65-75]()

### Cost Structure and Revenue Analysis

```mermaid
graph TB
    subgraph "Daily Infrastructure Costs"
        HardwareCost["Hardware Cost<br/>$87,072/day<br/>226.75 avg nodes × 8 GPUs × $2/hr × 24hr"]
        DynamicScaling["Dynamic Scaling<br/>278 peak → variable nighttime"]
    end
    
    subgraph "Traffic Processing"
        InputTokens["608B Input Tokens<br/>73.7k tokens/sec/H800"]
        CacheHits["342B Cache Hits<br/>56.3% hit rate"]
        OutputTokens["168B Output Tokens<br/>14.8k tokens/sec/H800"]
    end
    
    subgraph "Revenue Calculation (R1 Pricing)"
        CacheHitRevenue["Cache Hit Revenue<br/>342B × $0.14/M = $47,880"]
        CacheMissRevenue["Cache Miss Revenue<br/>266B × $0.55/M = $146,300"]
        OutputRevenue["Output Revenue<br/>168B × $2.19/M = $367,920"]
        TotalTheoreticalRevenue["Total: $562,027/day"]
    end
    
    subgraph "Profit Analysis"
        ProfitMargin["545% Profit Margin<br/>($562,027 - $87,072) / $87,072"]
        ActualRevenue["Actual Revenue<br/>Substantially Lower:<br/>• V3 pricing < R1 pricing<br/>• Free web/app access<br/>• Nighttime discounts"]
    end
    
    HardwareCost --> ProfitMargin
    TotalTheoreticalRevenue --> ProfitMargin
    
    InputTokens --> CacheHits
    CacheHits --> CacheHitRevenue
    InputTokens --> CacheMissRevenue
    OutputTokens --> OutputRevenue
    
    CacheHitRevenue --> TotalTheoreticalRevenue
    CacheMissRevenue --> TotalTheoreticalRevenue
    OutputRevenue --> TotalTheoreticalRevenue
```

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:67-68](), [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:78-86]()

### Technical Optimization Impact on Economics

| Component | Technical Capability | Economic Impact |
|-----------|---------------------|-----------------|
| FlashMLA | 580 TFLOPS BF16, 3000 GB/s memory bandwidth | Maximizes token generation throughput per H800 |
| DeepGEMM | 1350+ FP8 TFLOPS | Accelerates expert computation, reduces hardware requirements |
| DeepEP | Cross-node expert parallelism | Enables 256-expert MoE scaling across 18 nodes |
| EPLB | Expert load balancing | Maximizes GPU utilization, prevents bottlenecks |
| 3FS | 6.6 TiB/s throughput, 40+ GiB/s per node | Eliminates storage bottlenecks for KV cache operations |

The 545% profit margin demonstrates how technical optimizations directly translate to economic efficiency in large-scale AI inference systems.

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:61-68](), [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:78-86]()

## Node Scaling with Expert Parallelism

DeepSeek's expert parallelism approach enables efficient scaling across multiple GPU nodes:

```mermaid
flowchart TB
    subgraph "Multi-Node Expert-Parallel Architecture"
        subgraph "Request Management"
            BatchSched["Batch Scheduler"]
            TokenRouting["Token Routing<br>Algorithm"]
        end
        
        subgraph "Node 1"
            N1E1["Expert 1"]
            N1E2["Expert 2"]
            N1GEMM["DeepGEMM"]
            N1MLA["FlashMLA"]
        end
        
        subgraph "Node 2"
            N2E3["Expert 3"]
            N2E4["Expert 4"]
            N2GEMM["DeepGEMM"]
            N2MLA["FlashMLA"]
        end
        
        subgraph "Node 3"
            N3E5["Expert 5"]
            N3E6["Expert 6"]
            N3GEMM["DeepGEMM"]
            N3MLA["FlashMLA"]
        end
        
        subgraph "Inter-node Communication"
            DeepEPLib["DeepEP Library"]
            EPLB["EPLB Load Balancer"]
            AllToAll["All-to-All<br>Communication"]
        end
        
        subgraph "Storage"
            FS["3FS File System"]
            KVCache["KV Cache Storage"]
        end
    end
    
    BatchSched --> TokenRouting
    TokenRouting --> DeepEPLib
    DeepEPLib --> EPLB
    EPLB --> AllToAll
    
    AllToAll <--> N1E1 & N1E2 & N2E3 & N2E4 & N3E5 & N3E6
    
    N1E1 & N1E2 --> N1GEMM
    N2E3 & N2E4 --> N2GEMM
    N3E5 & N3E6 --> N3GEMM
    
    N1GEMM --> N1MLA
    N2GEMM --> N2MLA
    N3GEMM --> N3MLA
    
    N1MLA & N2MLA & N3MLA <--> KVCache
    KVCache --> FS
```

Sources: README.md:41-49, 66-70, 74-83, 86-97

## Optimization Analysis: Prefilling vs. Decoding

The DeepSeek infrastructure employs different optimization strategies for prefilling and decoding phases:

| Phase | Communication Pattern | Computation Characteristic | Key Optimizations |
|-------|----------------------|----------------------------|-------------------|
| Prefilling | High-volume batch data | Compute-bound | DeepEP high-throughput kernels, DeepGEMM FP8, batch processing |
| Decoding | Low-latency token exchanges | Memory-bound | FlashMLA, low-latency DeepEP kernels, KV cache optimization |

```mermaid
graph TD
    subgraph "Prefilling Optimizations"
        BatchProc["Batch Processing"]
        HTKernel["High-Throughput Kernels"]
        EP["DeepEP Communication"]
        GEMM["DeepGEMM FP8 1350+ TFLOPS"]
    end
    
    subgraph "Decoding Optimizations"
        FMLA["FlashMLA 580 TFLOPS<br>3000 GB/s"]
        LLKernel["Low-Latency Kernels"]
        KVC["KV Cache Optimization"]
        FS["3FS 40+ GiB/s/node"]
    end
    
    subgraph "Common Infrastructure"
        LoadBal["EPLB Load Balancing"]
        OverlapTech["Comm-Comp Overlapping"]
        StreamMgmt["CUDA Stream Management"]
    end
    
    BatchProc & HTKernel --> PrefillPerf["73.7k Input Tokens/sec/H800"]
    EP & GEMM --> PrefillPerf
    
    FMLA & LLKernel --> DecodePerf["14.8k Output Tokens/sec/H800"]
    KVC & FS --> DecodePerf
    
    LoadBal & OverlapTech & StreamMgmt --> PrefillPerf
    LoadBal & OverlapTech & StreamMgmt --> DecodePerf
```

Sources: README.md:28-36, 41-49, 54-59, 66-70, 74-83, 87-97

## Future Optimization Directions

The DeepSeek infrastructure continues to evolve with several promising optimization paths:

1. **Further precision optimization**: Moving beyond FP8 to INT4/INT8 for specific operations
2. **Memory hierarchy optimization**: Better leveraging GPU/CPU/SSD memory tiers
3. **Dynamic expert allocation**: Runtime adjustment of expert placement based on workload
4. **Advanced batching techniques**: More sophisticated token clustering for varied length processing
5. **Hardware-specific optimizations**: Targeting next-generation GPU architectures

These optimizations aim to further improve both technical performance metrics and economic efficiency.

Sources: README.md:86-97

---

