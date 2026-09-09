> 来源: [https://deepwiki.com/deepseek-ai/profile-data/3-inference-process](https://deepwiki.com/deepseek-ai/profile-data/3-inference-process)
> DeepWiki deepseek-ai/profile-data

# Inference Process

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1)
 - [assets/decode.jpg](https://github.com/deepseek-ai/profile-data/blob/44960242/assets/decode.jpg)
 - [assets/prefill.jpg](https://github.com/deepseek-ai/profile-data/blob/44960242/assets/prefill.jpg)
 - [prefill.json](https://github.com/deepseek-ai/profile-data/blob/44960242/prefill.json)
 
  This document details the inference process used in the DeepSeek framework, focusing on the profiling data that demonstrates computation-communication overlap strategies. The inference process consists of two distinct stages: prefilling and decoding, each with different parallelism configurations and optimization techniques. For information about the training process, see [Training Process](https://deepwiki.com/deepseek-ai/profile-data/2-training-process).

 
## Overview of Inference Pipeline

 The DeepSeek inference pipeline is designed for high-performance text generation, with specialized configurations for handling both the initial processing of prompts (prefilling) and the subsequent token generation (decoding). Both stages employ expert parallelism (EP) with tensor parallelism (TP) configurations, and utilize micro-batching strategies to optimize performance.

 
```

```

 Sources: [README.md16-30](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L16-L30)

 
## Prefilling Stage

 The prefilling stage processes the initial prompt input before generating new tokens. It uses a configuration optimized for handling large batches of input tokens efficiently.

 
### Configuration and Workload

 
 - **Parallel Configuration**: EP32 (Expert Parallelism with 32 experts), TP1 (Tensor Parallelism degree 1)
 - **Workload**: 4K prompt length with 16K tokens per GPU
 - **Deployment**: Matches DeepSeek V3/R1's actual online deployment configuration
 
 
### Micro-batch Strategy

 The prefilling stage employs two micro-batches to effectively overlap computation and all-to-all communication, with the following characteristics:

 
 - The same prompt may be split between the two micro-batches
 - Attention computation load is balanced across the micro-batches
 - All-to-all communication occurs while computation is being performed
 
 
```

```

 Sources: [README.md16-22](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L16-L22)

 
## Decoding Stage

 The decoding stage generates new tokens sequentially after the prefilling stage completes. It uses a different configuration optimized for handling multiple simultaneous requests.

 
### Configuration and Workload

 
 - **Parallel Configuration**: EP128 (Expert Parallelism with 128 experts), TP1 (Tensor Parallelism degree 1)
 - **Workload**: 4K prompt length with 128 requests per GPU
 - **Deployment**: Closely matches DeepSeek's actual online deployment configuration
 
 
### RDMA-based Micro-batch Strategy

 Like prefilling, the decoding stage also uses two micro-batches for computation-communication overlap, but with a key difference:

 
 - After computation, RDMA (Remote Direct Memory Access) messages are issued
 - GPU SMs (Streaming Multiprocessors) are freed immediately after RDMA message issuance
 - The system waits for all-to-all communication to complete after computation is finished
 - This approach prevents all-to-all communication from occupying GPU SMs during decoding
 
 
```

```

 Sources: [README.md24-30](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L24-L30)

 
## Communication-Computation Overlap Mechanism

 The DeepSeek inference pipeline achieves high performance through careful overlap of computation and communication operations. This section details how the overlap mechanisms differ between prefilling and decoding.

 
### Prefilling Overlap Pattern

 In the prefilling stage, the overlap pattern follows these steps:

 
 - First micro-batch begins computation
 - When computation completes, all-to-all communication is initiated
 - While communication is in progress, the second micro-batch performs computation
 - This creates an effective overlap between computation and communication phases
 
 
```

```

 
### Decoding Overlap Pattern

 The decoding stage uses a more advanced overlap pattern:

 
 - First micro-batch performs computation
 - RDMA messages are issued, immediately freeing GPU resources
 - Second micro-batch begins computation while all-to-all communication happens in the background
 - System waits for all-to-all communication to complete after all computation is finished
 - This approach ensures GPU SMs are efficiently utilized for computation
 
 
```

```

 The key innovation in the decoding stage is the use of RDMA to initiate communication without occupying GPU computing resources, allowing for maximum utilization of GPU SMs for computation tasks.

 Sources: [README.md16-30](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L16-L30)

 
## Performance Considerations

 When using the DeepSeek inference pipeline, several factors affect performance:

 
### Parallel Configuration Selection

 The choice of parallel configurations significantly impacts performance:

 
 - **Prefilling**: EP32 is used as it balances expert model capacity with communication overhead for processing large prompts
 - **Decoding**: EP128 provides more specialized experts for handling diverse generation requests
 
 
### Micro-batch Size Optimization

 
 - Two micro-batches are used in both stages as this provides optimal overlap between computation and communication
 - Increasing micro-batches beyond two may increase overhead without proportional performance gains
 
 
### RDMA Implementation

 
 - The DeepEP implementation handles the low-level RDMA operations for efficient all-to-all communication
 - This specialized implementation prevents all-to-all communication from occupying GPU SMs during decoding
 
 
```

```

 Sources: [README.md16-30](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L16-L30)

 
## Relationship to Other System Components

 The inference process is closely connected to several other components in the DeepSeek framework:

 
```

```

 For more detailed information about specific components:

 
 - For information about the prefilling stage, see [Prefilling Stage](https://deepwiki.com/deepseek-ai/profile-data/3.1-prefilling-stage)
 - For information about the decoding stage, see [Decoding Stage](https://deepwiki.com/deepseek-ai/profile-data/3.2-decoding-stage)
 - For detailed explanation of the micro-batch strategy, see [Micro-batch Strategy](https://deepwiki.com/deepseek-ai/profile-data/3.3-micro-batch-strategy)
 - For information about expert parallelism configurations, see [Expert Parallelism](https://deepwiki.com/deepseek-ai/profile-data/4.1-expert-parallelism-(ep))
 
 Sources: [README.md1-30](https://github.com/deepseek-ai/profile-data/blob/44960242/README.md?plain=1#L1-L30)
