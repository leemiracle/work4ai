> 来源: [https://deepwiki.com/deepseek-ai/profile-data/2-training-process](https://deepwiki.com/deepseek-ai/profile-data/2-training-process)
> DeepWiki deepseek-ai/profile-data

# Training Process

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1)
 - [assets/train.jpg](https://github.com/deepseek-ai/profile-data/blob/44960242/assets/train.jpg)
 - [train.json](https://github.com/deepseek-ai/profile-data/blob/44960242/train.json)
 
  This page documents the training process in the DeepSeek framework, focusing on the profiling data that demonstrates efficient training strategies. It details the parallel configuration, chunking methodology, and communication-computation overlap techniques employed during model training. For more detailed information about the DualPipe architecture, see [DualPipe Architecture](https://deepwiki.com/deepseek-ai/profile-data/2.1-dualpipe-architecture), and for specifics on MoE layers, see [MoE Layers](https://deepwiki.com/deepseek-ai/profile-data/2.2-moe-layers).

 
## Training Configuration Overview

 The DeepSeek training profiling data showcases a high-performance parallel configuration designed for large language model training. The configuration parameters reflect those used in DeepSeek-V3 pretraining:

 
 - **Expert Parallelism (EP)**: EP64 - distributes experts across 64 devices
 - **Tensor Parallelism (TP)**: TP1 - no tensor parallelism employed
 - **Sequence Length**: 4K tokens
 - **Pipeline Parallelism (PP)**: Not included in profiling for simplicity
 
 
```

```

 Sources: [README.md11-12](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L11-L12)

 
## DualPipe Chunk Organization

 The training process utilizes DualPipe for efficient execution of forward and backward passes. This architecture divides the model's MoE layers into chunks that can be processed with optimal computation-communication overlap.

 Key characteristics of the chunking strategy:

 
 - The model is divided into two chunks
 - Each chunk contains 4 MoE (Mixture of Experts) layers
 - Forward and backward passes of different chunks can be overlapped
 
 
```

```

 Sources: [README.md11](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L11-L11)

 
## Computation-Communication Overlap Strategy

 The profiling data demonstrates how forward and backward passes are executed with overlapping communication and computation. This strategy is key to the efficiency of the training process.

 
```

```

 The timeline shows how the execution of chunks is orchestrated to maximize device utilization:

 
 - The forward pass of Chunk 1 is executed first
 - While communication for Chunk 1 is in progress, the forward pass of Chunk 2 begins
 - The backward pass of Chunk 1 and Chunk 2 are similarly overlapped
 - All-to-all communication operations for expert parallelism are integrated into this schedule
 
 Sources: [README.md11](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L11-L11)

 
## Expert Parallelism Implementation

 The training process employs a balanced MoE routing strategy for profiling purposes. This ensures that expert computation is distributed evenly across devices.

 
```

```

 The diagram illustrates how tokens are routed to experts distributed across 64 devices (EP64 configuration). For profiling purposes, the system uses a balanced routing strategy to ensure consistent performance measurement.

 Sources: [README.md3](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L3-L3) [README.md11-12](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L11-L12)

 
## Profiling Data Visualization

 The training profiling data captures the execution timeline of the various components of the training process. When visualized in Chrome/Edge tracing tools, it provides insights into:

 
 - Execution of forward and backward passes for each chunk
 - Communication operations (particularly all-to-all for expert parallelism)
 - Overlapping execution patterns
 - Overall resource utilization
 
 
```

```

 The profiling data can be visualized by loading the `train.json` file in Chrome or Edge browser's tracing tool, accessible at chrome://tracing or edge://tracing.

 Sources: [README.md3](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L3-L3) [README.md7-9](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L7-L9)

 
## Relationship to Inference Process

 While this page focuses on the training process, it's worth noting the key differences between training and inference in the DeepSeek framework:

 
| Aspect | Training | Prefilling (Inference) | Decoding (Inference) |
|---|---|---|---|
| Parallel Configuration | EP64, TP1 | EP32, TP1 | EP128, TP1 |
| Sequence Length | 4K | 4K | 4K |
| Batch Size | - | 16K tokens/GPU | 128 requests/GPU |
| Chunking Strategy | 2 chunks, 4 MoE layers each | 2 micro-batches | 2 micro-batches |
| Communication Approach | All-to-all | All-to-all | RDMA + All-to-all |

 For more details on the inference process, see [Inference Process](https://deepwiki.com/deepseek-ai/profile-data/3-inference-process).

 Sources: [README.md11-12](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L11-L12) [README.md22-30](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L22-L30)
