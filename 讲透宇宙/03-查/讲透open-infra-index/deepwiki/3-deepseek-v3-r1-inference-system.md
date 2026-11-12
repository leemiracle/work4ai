<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/open-infra-index · page 3 DeepSeek V3/R1 Inference System · fetched 2026-10-30 -->

# DeepSeek V3/R1 Inference System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md](202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md)
- [README.md](README.md)

</details>



## Purpose and Scope

This document provides comprehensive technical documentation of the production DeepSeek V3/R1 Inference System, focusing on the large-scale Expert Parallelism (EP) architecture that serves DeepSeek's Mixture-of-Experts models. The system achieves higher throughput and lower latency through cross-node EP, computation-communication overlapping, and sophisticated load balancing strategies. This documentation covers the distributed inference architecture, prefill-decode disaggregation, performance optimizations, and production statistics from DeepSeek's online services.
</old_str>

<old_str>
## Key Performance Metrics

Production statistics from 24-hour period (UTC+8 02/27/2025 12:00 PM to 02/28/2025 12:00 PM):

| Metric | Value | Details |
|--------|-------|---------|
| **Token Processing** | | |
| Total input tokens | 608B | Daily processing volume |
| Total output tokens | 168B | Daily generation volume |
| Cache hit rate | 56.3% | 342B tokens from on-disk KV cache |
| Input tokens/sec per H800 | 73.7k | Including cache hits during prefill |
| Output tokens/sec per H800 | 14.8k | During decode phase |
| Average output speed | 20-22 tokens/sec | End-user experience |
| Average KV cache length | 4,989 tokens | Per output token |
| **Infrastructure** | | |
| Peak node count | 278 nodes | Combined V3/R1 services |
| Average node count | 226.75 nodes | 24-hour average |
| GPUs per node | 8 H800 | Total ~2,214 peak GPUs |
| **Economics** | | |
| Daily operational cost | $87,072 | At $2/hour per H800 GPU |
| Theoretical daily revenue | $562,027 | At R1 pricing rates |
| Cost profit margin | 545% | Theoretical calculation |

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:67-81](), [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:73-76]()
</old_str>
<new_str>
## System Overview

The DeepSeek V3/R1 Inference System employs large-scale cross-node Expert Parallelism to serve MoE models where only 8 out of 256 experts per layer are activated. The system's high sparsity necessitates extremely large batch sizes to ensure sufficient per-expert batching for optimal throughput and latency. The architecture implements prefill-decode disaggregation with different parallelism degrees for each phase.

**Core System Characteristics:**
- **Model Architecture**: 256 experts per layer, 8 active experts per forward pass
- **Prefill Configuration**: EP32/DP32 across 4 nodes per deployment unit
- **Decode Configuration**: EP144/DP144 across 18 nodes per deployment unit  
- **Expert Distribution**: 32 redundant routed experts with dynamic load balancing

```mermaid
graph TD
    subgraph "Production Inference Pipeline"
        UserReq["User Requests<br/>(Web/APP/API)"] --> LoadBalancer["nginx Load Balancer"]
        LoadBalancer --> RequestRouter["Request Router"]
        
        subgraph "Prefill Phase - EP32/DP32"
            RequestRouter --> PrefillUnit1["Deployment Unit 1<br/>(4 nodes, 32 GPUs)"]
            RequestRouter --> PrefillUnit2["Deployment Unit 2<br/>(4 nodes, 32 GPUs)"]
            PrefillUnit1 --> PrefillEP["Expert Routing<br/>(9 routed + 1 shared per GPU)"]
            PrefillUnit2 --> PrefillEP
        end
        
        subgraph "Decode Phase - EP144/DP144"  
            PrefillEP --> DecodeUnit1["Deployment Unit 1<br/>(18 nodes, 144 GPUs)"]
            PrefillEP --> DecodeUnit2["Deployment Unit 2<br/>(18 nodes, 144 GPUs)"]
            DecodeUnit1 --> DecodeEP["Expert Routing<br/>(2 routed + 1 shared per GPU)"]
            DecodeUnit2 --> DecodeEP
        end
        
        subgraph "Storage & Cache"
            KVCache["KV Cache<br/>(3FS, 40+ GiB/s per node)"] <--> PrefillEP
            KVCache <--> DecodeEP
            DiskCache["On-disk Cache<br/>(56.3% hit rate)"] --> KVCache
        end
        
        DecodeEP --> OutputTokens["Output Tokens<br/>(168B tokens/day)"]
    end
```

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:21-24](), [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:73-76]()

## System Overview

The DeepSeek V3/R1 Inference System is a high-performance, distributed inference architecture designed specifically for serving large-scale mixture-of-experts (MoE) models. The system leverages multiple optimized components to achieve exceptional throughput, low latency, and cost-effective scaling across GPU nodes.

```mermaid
graph TD
    subgraph "DeepSeek V3/R1 Inference System"
        Request["User Request"] --> Preprocessor["Request Preprocessor"]
        Preprocessor --> BatchManager["Batch Manager"]
        BatchManager --> Router["Cross-Node Router"]
        
        Router --> Node1["Inference Node 1"]
        Router --> Node2["Inference Node 2"]
        Router --> NodeN["Inference Node N"]
        
        subgraph "Inference Node Components"
            Prefill["Prefilling Phase"] --> KVCache["KV Cache (Managed by 3FS)"]
            KVCache --> Decode["Decoding Phase (FlashMLA)"]
            DeepEP["DeepEP Communication"] <--> Prefill
            DeepEP["DeepEP Communication"] <--> Decode
            EPLB["EPLB Load Balancer"] --> DeepEP
            DeepGEMM["DeepGEMM Computation"] --> Prefill
            DeepGEMM --> Decode
        end
        
        Node1 & Node2 & NodeN --> ResponseMerger["Response Merger"]
        ResponseMerger --> Response["User Response"]
    end
```

Sources: [README.md:85-101]()

## System Architecture

The system implements a sophisticated multi-stage architecture with disaggregated prefill and decode processing, each optimized for different computational and communication patterns.

**Architecture Overview Diagram**
```mermaid
flowchart TB
    subgraph "Client Interface Layer"
        WebUI["Web Interface"]
        MobileApp["Mobile App"] 
        APIClients["API Clients"]
    end
    
    subgraph "Load Balancing & Routing"
        NginxLB["nginx Load Balancer"]
        PrefillLB["Prefill Load Balancer<br/>(Balance input tokens & attention computation)"]
        DecodeLB["Decode Load Balancer<br/>(Balance KV cache usage & request counts)"]
        EPLB["Expert-Parallel Load Balancer<br/>(Balance expert computation load)"]
    end
    
    subgraph "Prefill Infrastructure - EP32/DP32"
        PrefillCluster["4-Node Deployment Units"]
        PrefillExperts["32 Redundant Routed Experts<br/>(9 routed + 1 shared per GPU)"]
        PrefillComm["DeepEP All-to-All Communication"]
        DualBatch["Dual-batch Overlapping Strategy"]
    end
    
    subgraph "Decode Infrastructure - EP144/DP144"
        DecodeCluster["18-Node Deployment Units"] 
        DecodeExperts["32 Redundant Routed Experts<br/>(2 routed + 1 shared per GPU)"]
        DecodeComm["DeepEP All-to-All Communication"]
        FiveStage["5-Stage Pipeline Overlapping"]
    end
    
    subgraph "Compute Engines"
        FlashMLA["FlashMLA<br/>(BF16 MLA computation, paged KV cache)"]
        DeepGEMM["DeepGEMM<br/>(FP8 matrix ops & dispatch transmission)"]
    end
    
    subgraph "Storage Systems"
        ThreeFS["3FS File System<br/>(6.6 TiB/s aggregate throughput)"]
        KVCacheFS["KV Cache Storage<br/>(40+ GiB/s per node)"]
        OnDiskCache["On-disk Cache<br/>(342B token hits, 56.3% rate)"]
    end
    
    WebUI & MobileApp & APIClients --> NginxLB
    NginxLB --> PrefillLB
    PrefillLB --> PrefillCluster
    PrefillCluster --> PrefillExperts
    PrefillExperts --> PrefillComm
    PrefillComm --> DualBatch
    
    DualBatch --> DecodeLB
    DecodeLB --> DecodeCluster
    DecodeCluster --> DecodeExperts
    DecodeExperts --> DecodeComm
    DecodeComm --> FiveStage
    
    EPLB --> PrefillExperts
    EPLB --> DecodeExperts
    
    PrefillExperts --> DeepGEMM
    DecodeExperts --> FlashMLA
    DecodeExperts --> DeepGEMM
    
    PrefillComm <--> ThreeFS
    DecodeComm <--> KVCacheFS
    KVCacheFS --> OnDiskCache
```

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:21-24](), [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:38-55](), [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:57-58]()

## System Architecture

The DeepSeek V3/R1 Inference System follows a distributed architecture that efficiently processes inference requests through specialized components optimized for both the prefilling and decoding phases of inference.

```mermaid
flowchart TD
    subgraph "Request Processing"
        Input["Input Tokens"] --> TokenPreprocessor["Token Preprocessor"]
        TokenPreprocessor --> BatchScheduler["Batch Scheduler"]
        BatchScheduler --> Dispatcher["Node Dispatcher"]
    end
    
    subgraph "Inference Processing"
        Dispatcher --> PrefillPhase["Prefilling Phase"]
        PrefillPhase --> KVCacheStorage["KV Cache Storage (3FS)"]
        KVCacheStorage --> DecodePhase["Decoding Phase (FlashMLA)"]
        DecodePhase --> OutputGenerator["Output Generator"]
        OutputGenerator --> Output["Output Tokens"]
    end
    
    subgraph "Communication Layer"
        DeepEPComm["DeepEP Communication"] <--> PrefillPhase
        DeepEPComm <--> DecodePhase
        EPLBBalancer["EPLB Load Balancer"] --> DeepEPComm
    end
    
    subgraph "Computation Layer"
        DeepGEMMCompute["DeepGEMM FP8 Computation"] --> PrefillPhase
        DeepGEMMCompute --> DecodePhase
    end
    
    subgraph "Storage Layer"
        ThreeFSStorage["3FS Storage System"] --> KVCacheStorage
    end
```

Sources: [README.md:85-101]()

### Inference Workflow

The inference process in the DeepSeek V3/R1 system follows two main phases:

1. **Prefilling Phase**: 
   - Processes all input tokens to generate the initial hidden states
   - Handles variable-length inputs efficiently through batching
   - Uses DeepEP for expert routing across GPUs
   - Stores intermediate states in the KV cache managed by 3FS

2. **Decoding Phase**: 
   - Generates output tokens one at a time
   - Utilizes FlashMLA for optimized multi-head attention
   - Employs DeepGEMM for efficient FP8 computation
   - Balances expert loads using EPLB

## Component Integration

The DeepSeek V3/R1 Inference System integrates several specialized components that work together to create a high-performance inference pipeline.

```mermaid
graph TD
    subgraph "DeepSeek V3/R1 Inference System"
        direction LR
        subgraph "Compute Optimization"
            FlashMLA["FlashMLA<br>Optimized MLA Decoding"]
            DeepGEMM["DeepGEMM<br>FP8 Computation"]
        end
        
        subgraph "Communication"
            DeepEP["DeepEP<br>All-to-All Communication"]
            EPLB["EPLB<br>Expert Load Balancing"]
        end
        
        subgraph "Storage"
            ThreeFS["3FS<br>KV Cache Management"]
        end
        
        subgraph "Inference Logic"
            Prefilling["Prefilling Logic"]
            Decoding["Decoding Logic"]
            BatchManagement["Batch Management"]
        end
    end
    
    FlashMLA --> Decoding
    DeepGEMM --> Prefilling
    DeepGEMM --> Decoding
    
    DeepEP <--> Prefilling
    DeepEP <--> Decoding
    EPLB --> DeepEP
    
    ThreeFS --> Prefilling
    ThreeFS --> Decoding
    
    BatchManagement --> Prefilling
    Prefilling --> Decoding
```

Sources: [README.md:28-83]()

### Key Component Roles

| Component | Role in Inference System |
|-----------|--------------------------|
| FlashMLA | Provides optimized multi-head attention for variable-length sequences during decoding; achieves 3000 GB/s memory-bound performance and BF16 580 TFLOPS compute-bound on H800 |
| DeepGEMM | Handles FP8 matrix multiplications for both dense and MoE operations; delivers up to 1350+ FP8 TFLOPS on Hopper GPUs |
| DeepEP | Manages all-to-all communication for expert parallelism; supports both intranode and internode communication with NVLink and RDMA |
| EPLB | Optimizes expert-parallel load balancing across GPUs to prevent bottlenecks |
| 3FS | Provides high-performance storage for KV cache with 40+ GiB/s peak throughput per client node |

Sources: [README.md:28-83]()

## Optimization Techniques

The system employs three core optimization strategies to maximize resource utilization and minimize latency bottlenecks across the distributed inference infrastructure.

### Communication-Computation Overlapping

The system implements phase-specific overlapping strategies to hide communication latency behind computation operations.

**Prefill Phase: Dual-Batch Overlapping Strategy**
```mermaid
gantt
    title Dual-Batch Prefill Communication-Computation Overlap
    dateFormat s
    axisFormat %S
    
    section Microbatch A
    Communication A    :commA, 0, 2
    Computation A      :compA, 2, 6
    
    section Microbatch B  
    Communication B    :commB, 3, 5
    Computation B      :compB, 5, 9
    
    section Timeline
    Overlap Period     :milestone, overlap, 3, 0
```

**Decode Phase: 5-Stage Pipeline Strategy**
```mermaid
flowchart LR
    subgraph "5-Stage Decode Pipeline"
        Stage1["Stage 1<br/>Attention Layer Part 1"]
        Stage2["Stage 2<br/>Expert Communication"]
        Stage3["Stage 3<br/>Expert Computation"] 
        Stage4["Stage 4<br/>Expert Combine"]
        Stage5["Stage 5<br/>Attention Layer Part 2"]
        
        Stage1 --> Stage2
        Stage2 --> Stage3
        Stage3 --> Stage4
        Stage4 --> Stage5
        
        CommOverlap["Communication<br/>overlapped with<br/>computation stages"]
        CommOverlap -.-> Stage2
        CommOverlap -.-> Stage4
    end
```

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:25-36]()

### Multi-Level Load Balancing

The system implements three distinct load balancers to optimize resource utilization across different computational bottlenecks:

**Load Balancing Architecture**
```mermaid
flowchart TD
    subgraph "Load Balancing Hierarchy"
        RequestFlow["Incoming Requests"] --> PrefillLB["Prefill Load Balancer"]
        
        subgraph "Prefill Load Balancer"
            PrefillObjective1["Balance core-attention computation<br/>(varying sequence lengths)"]
            PrefillObjective2["Balance input token counts per GPU<br/>(dispatch send load balancing)"]
        end
        
        PrefillLB --> DecodeLB["Decode Load Balancer"]
        
        subgraph "Decode Load Balancer"
            DecodeObjective1["Balance KV cache usage across GPUs<br/>(core-attention computation)"]
            DecodeObjective2["Balance request counts per GPU<br/>(dispatch send load balancing)"]
        end
        
        subgraph "Expert-Parallel Load Balancer (EPLB)"
            EPLBObjective["Minimize maximum dispatch receive load<br/>(balance expert computation)"]
        end
        
        PrefillLB --> EPLB["Expert-Parallel Load Balancer"]
        DecodeLB --> EPLB
    end
    
    subgraph "Target Resources"
        PrefillNodes["Prefill Deployment Units<br/>(4 nodes, 32 GPUs each)"]
        DecodeNodes["Decode Deployment Units<br/>(18 nodes, 144 GPUs each)"]
        ExpertGPUs["Expert Distribution<br/>(256 experts → 8 active per layer)"]
    end
    
    PrefillLB --> PrefillNodes
    DecodeLB --> DecodeNodes  
    EPLB --> ExpertGPUs
```

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:38-55]()

### Expert Parallelism Scaling

Large-scale cross-node EP addresses the sparsity challenge of MoE models where only 8 of 256 experts are active per layer, requiring extremely large batch sizes for optimal expert utilization.

**Expert Parallelism Configuration**
```mermaid
flowchart TB
    subgraph "MoE Model Structure" 
        Layer["Model Layer"] --> ExpertSelection["Expert Selection<br/>(8 of 256 experts)"]
        ExpertSelection --> ActiveExperts["Active Experts<br/>(High sparsity)"]
    end
    
    subgraph "EP Scaling Strategy"
        LargeBatch["Large Batch Size<br/>(Required for expert efficiency)"] --> EPDistribution["EP Distribution"]
        
        subgraph "Prefill EP32 Configuration"
            PrefillUnit["4 nodes (32 GPUs)"]
            PrefillExperts["9 routed + 1 shared<br/>per GPU"]
        end
        
        subgraph "Decode EP144 Configuration" 
            DecodeUnit["18 nodes (144 GPUs)"]
            DecodeExperts["2 routed + 1 shared<br/>per GPU"]
        end
        
        EPDistribution --> PrefillUnit
        EPDistribution --> DecodeUnit
    end
    
    subgraph "Performance Benefits"
        HighThroughput["Enhanced GPU matrix<br/>computation efficiency"]
        LowLatency["Reduced memory access<br/>demands per GPU"]
    end
    
    ActiveExperts --> LargeBatch
    PrefillUnit --> HighThroughput
    DecodeUnit --> LowLatency
```

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:18-24](), [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:5-7]()

## Production Economics and Dynamic Resource Allocation

The system implements dynamic resource allocation based on diurnal usage patterns, optimizing costs while maintaining service quality during peak and off-peak periods.

**Dynamic Resource Management**
```mermaid
flowchart TB
    subgraph "24-Hour Resource Allocation Cycle"
        DaytimePeak["Daytime Peak Load<br/>(High service demand)"] --> FullDeployment["All 278 nodes active<br/>(Inference services)"]
        NighttimeLow["Nighttime Low Load<br/>(Reduced demand)"] --> PartialDeployment["Reduced inference nodes<br/>(Resources to R&D/Training)"]
        
        FullDeployment --> ResourceMetrics["Peak: 278 nodes<br/>Average: 226.75 nodes<br/>8 H800 GPUs per node"]
        PartialDeployment --> CostOptimization["Dynamic cost optimization<br/>Research resource reallocation"]
    end
    
    subgraph "Economic Analysis (24-Hour Period)"
        OperationalCosts["Daily Operational Cost: $87,072<br/>($2/hour per H800 GPU)"]
        
        subgraph "Revenue Components"
            InputRevenue["Input Token Processing<br/>608B tokens (342B cache hits)"]
            OutputRevenue["Output Token Generation<br/>168B tokens"]
            CacheRevenue["Cache Hit Pricing<br/>$0.14/M input tokens"]
            MissRevenue["Cache Miss Pricing<br/>$0.55/M input tokens"] 
            OutputPricing["Output Token Pricing<br/>$2.19/M output tokens"]
        end
        
        TheoreticalRevenue["Theoretical Revenue: $562,027<br/>(At R1 pricing rates)"]
        ProfitMargin["Cost Profit Margin: 545%"]
        
        InputRevenue & OutputRevenue --> TheoreticalRevenue
        CacheRevenue & MissRevenue & OutputPricing --> TheoreticalRevenue
        OperationalCosts & TheoreticalRevenue --> ProfitMargin
    end
    
    subgraph "Actual Revenue Considerations"
        PricingDiff["V3 pricing < R1 pricing"]
        FreeServices["Web & APP access free"]
        NightDiscounts["Automatic off-peak discounts"]
        ActualRevenue["Actual Revenue << Theoretical"]
        
        PricingDiff & FreeServices & NightDiscounts --> ActualRevenue
    end
```

**Performance and Economic Metrics:**

| Resource Allocation | Peak Period | Off-Peak Period |
|--------------------|-----------|----|
| **Node Configuration** | 278 nodes active | Reduced allocation |
| **Service Priority** | Full inference capacity | Research/training priority |
| **Cost Optimization** | Maximum throughput | Resource reallocation |

| Economic Factor | Value | Impact |
|----------------|-------|--------|
| **Theoretical Profit Margin** | 545% | Based on R1 pricing |
| **Daily Operational Cost** | $87,072 | H800 GPU lease costs |
| **Cache Hit Efficiency** | 56.3% | Reduces computation costs |
| **Average Token Processing Speed** | 20-22 tokens/sec | End-user experience |

Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:65-86](), [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md:82-86]()

## Related Documentation

For more detailed information about specific components of the inference system:

- For detailed information about the system architecture, see [Inference System Architecture](#3.1)
- For in-depth performance optimization details, see [Performance Optimization](#3.2)
- For the strategy behind open-sourcing components, see [Open-Sourcing Strategy](#3.3)
- For information about FlashMLA, see [FlashMLA](#2.1.1)
- For information about DeepEP, see [DeepEP](#2.2.1)
- For information about DeepGEMM, see [DeepGEMM](#2.1.2)
- For information about EPLB, see [EPLB](#2.2.3)
- For information about 3FS, see [3FS](#2.3.1)

---

