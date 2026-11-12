> 来源: [https://deepwiki.com/deepseek-ai/open-infra-index/3-deepseek-v3r1-inference-system](https://deepwiki.com/deepseek-ai/open-infra-index/3-deepseek-v3r1-inference-system)
> DeepWiki deepseek-ai/open-infra-index

# DeepSeek V3/R1 Inference System

  Relevant source files 
 - [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1)
 - [README.md](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/README.md?plain=1)
 
  
## Purpose and Scope

 This document provides comprehensive technical documentation of the production DeepSeek V3/R1 Inference System, focusing on the large-scale Expert Parallelism (EP) architecture that serves DeepSeek's Mixture-of-Experts models. The system achieves higher throughput and lower latency through cross-node EP, computation-communication overlapping, and sophisticated load balancing strategies. This documentation covers the distributed inference architecture, prefill-decode disaggregation, performance optimizations, and production statistics from DeepSeek's online services. </old_str>

 <old_str>

 
## Key Performance Metrics

 Production statistics from 24-hour period (UTC+8 02/27/2025 12:00 PM to 02/28/2025 12:00 PM):

 
| Metric | Value | Details |
|---|---|---|
| Token Processing |  |  |
| Total input tokens | 608B | Daily processing volume |
| Total output tokens | 168B | Daily generation volume |
| Cache hit rate | 56.3% | 342B tokens from on-disk KV cache |
| Input tokens/sec per H800 | 73.7k | Including cache hits during prefill |
| Output tokens/sec per H800 | 14.8k | During decode phase |
| Average output speed | 20-22 tokens/sec | End-user experience |
| Average KV cache length | 4,989 tokens | Per output token |
| Infrastructure |  |  |
| Peak node count | 278 nodes | Combined V3/R1 services |
| Average node count | 226.75 nodes | 24-hour average |
| GPUs per node | 8 H800 | Total ~2,214 peak GPUs |
| Economics |  |  |
| Daily operational cost | $87,072 | At $2/hour per H800 GPU |
| Theoretical daily revenue | $562,027 | At R1 pricing rates |
| Cost profit margin | 545% | Theoretical calculation |

 Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md67-81](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L67-L81) [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md73-76](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L73-L76) </old_str> <new_str>

 
## System Overview

 The DeepSeek V3/R1 Inference System employs large-scale cross-node Expert Parallelism to serve MoE models where only 8 out of 256 experts per layer are activated. The system's high sparsity necessitates extremely large batch sizes to ensure sufficient per-expert batching for optimal throughput and latency. The architecture implements prefill-decode disaggregation with different parallelism degrees for each phase.

 **Core System Characteristics:**

 
 - **Model Architecture**: 256 experts per layer, 8 active experts per forward pass
 - **Prefill Configuration**: EP32/DP32 across 4 nodes per deployment unit
 - **Decode Configuration**: EP144/DP144 across 18 nodes per deployment unit
 - **Expert Distribution**: 32 redundant routed experts with dynamic load balancing
 
 
```

```

 Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md21-24](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L21-L24) [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md73-76](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L73-L76)

 
## System Overview

 The DeepSeek V3/R1 Inference System is a high-performance, distributed inference architecture designed specifically for serving large-scale mixture-of-experts (MoE) models. The system leverages multiple optimized components to achieve exceptional throughput, low latency, and cost-effective scaling across GPU nodes.

 
```

```

 Sources: [README.md85-101](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/README.md?plain=1#L85-L101)

 
## System Architecture

 The system implements a sophisticated multi-stage architecture with disaggregated prefill and decode processing, each optimized for different computational and communication patterns.

 **Architecture Overview Diagram**

 
```

```

 Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md21-24](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L21-L24) [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md38-55](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L38-L55) [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md57-58](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L57-L58)

 
## System Architecture

 The DeepSeek V3/R1 Inference System follows a distributed architecture that efficiently processes inference requests through specialized components optimized for both the prefilling and decoding phases of inference.

 
```

```

 Sources: [README.md85-101](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/README.md?plain=1#L85-L101)

 
### Inference Workflow

 The inference process in the DeepSeek V3/R1 system follows two main phases:

 
 - **Prefilling Phase**:

 
 - Processes all input tokens to generate the initial hidden states
 - Handles variable-length inputs efficiently through batching
 - Uses DeepEP for expert routing across GPUs
 - Stores intermediate states in the KV cache managed by 3FS
 - **Decoding Phase**:

 
 - Generates output tokens one at a time
 - Utilizes FlashMLA for optimized multi-head attention
 - Employs DeepGEMM for efficient FP8 computation
 - Balances expert loads using EPLB
 
 
## Component Integration

 The DeepSeek V3/R1 Inference System integrates several specialized components that work together to create a high-performance inference pipeline.

 
```

```

 Sources: [README.md28-83](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/README.md?plain=1#L28-L83)

 
### Key Component Roles

 
| Component | Role in Inference System |
|---|---|
| FlashMLA | Provides optimized multi-head attention for variable-length sequences during decoding; achieves 3000 GB/s memory-bound performance and BF16 580 TFLOPS compute-bound on H800 |
| DeepGEMM | Handles FP8 matrix multiplications for both dense and MoE operations; delivers up to 1350+ FP8 TFLOPS on Hopper GPUs |
| DeepEP | Manages all-to-all communication for expert parallelism; supports both intranode and internode communication with NVLink and RDMA |
| EPLB | Optimizes expert-parallel load balancing across GPUs to prevent bottlenecks |
| 3FS | Provides high-performance storage for KV cache with 40+ GiB/s peak throughput per client node |

 Sources: [README.md28-83](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/README.md?plain=1#L28-L83)

 
## Optimization Techniques

 The system employs three core optimization strategies to maximize resource utilization and minimize latency bottlenecks across the distributed inference infrastructure.

 
### Communication-Computation Overlapping

 The system implements phase-specific overlapping strategies to hide communication latency behind computation operations.

 **Prefill Phase: Dual-Batch Overlapping Strategy**

 
```

```

 **Decode Phase: 5-Stage Pipeline Strategy**

 
```

```

 Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md25-36](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L25-L36)

 
### Multi-Level Load Balancing

 The system implements three distinct load balancers to optimize resource utilization across different computational bottlenecks:

 **Load Balancing Architecture**

 
```

```

 Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md38-55](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L38-L55)

 
### Expert Parallelism Scaling

 Large-scale cross-node EP addresses the sparsity challenge of MoE models where only 8 of 256 experts are active per layer, requiring extremely large batch sizes for optimal expert utilization.

 **Expert Parallelism Configuration**

 
```

```

 Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md18-24](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L18-L24) [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md5-7](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L5-L7)

 
## Production Economics and Dynamic Resource Allocation

 The system implements dynamic resource allocation based on diurnal usage patterns, optimizing costs while maintaining service quality during peak and off-peak periods.

 **Dynamic Resource Management**

 
```

```

 **Performance and Economic Metrics:**

 
| Resource Allocation | Peak Period | Off-Peak Period |
|---|---|---|
| Node Configuration | 278 nodes active | Reduced allocation |
| Service Priority | Full inference capacity | Research/training priority |
| Cost Optimization | Maximum throughput | Resource reallocation |

 
| Economic Factor | Value | Impact |
|---|---|---|
| Theoretical Profit Margin | 545% | Based on R1 pricing |
| Daily Operational Cost | $87,072 | H800 GPU lease costs |
| Cache Hit Efficiency | 56.3% | Reduces computation costs |
| Average Token Processing Speed | 20-22 tokens/sec | End-user experience |

 Sources: [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md65-86](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L65-L86) [202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md82-86](https://github.com/deepseek-ai/open-infra-index/blob/56d86855/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md?plain=1#L82-L86)

 
## Related Documentation

 For more detailed information about specific components of the inference system:

 
 - For detailed information about the system architecture, see [Inference System Architecture](https://deepwiki.com/deepseek-ai/open-infra-index/3.1-inference-system-architecture)
 - For in-depth performance optimization details, see [Performance Optimization](https://deepwiki.com/deepseek-ai/open-infra-index/3.2-performance-optimization)
 - For the strategy behind open-sourcing components, see [Open-Sourcing Strategy](https://deepwiki.com/deepseek-ai/open-infra-index/3.3-open-sourcing-strategy)
 - For information about FlashMLA, see [FlashMLA](https://deepwiki.com/deepseek-ai/open-infra-index/2.1.1-flashmla)
 - For information about DeepEP, see [DeepEP](https://deepwiki.com/deepseek-ai/open-infra-index/2.2.1-deepep)
 - For information about DeepGEMM, see [DeepGEMM](https://deepwiki.com/deepseek-ai/open-infra-index/2.1.2-deepgemm)
 - For information about EPLB, see [EPLB](https://deepwiki.com/deepseek-ai/open-infra-index/2.2.3-eplb)
 - For information about 3FS, see [3FS](https://deepwiki.com/deepseek-ai/open-infra-index/2.3.1-3fs-(fire-flyer-file-system))
