> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/6-inference-serving](https://deepwiki.com/kvcache-ai/ktransformers/6-inference-serving)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Inference Serving

  Relevant source files 
 - [README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1)
 - [doc/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/README.md?plain=1)
 - [doc/SUMMARY.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/SUMMARY.md?plain=1)
 - [doc/en/DeepseekR1_V3_tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1)
 - [doc/en/FAQ.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/FAQ.md?plain=1)
 - [doc/en/balance-serve.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1)
 - [doc/en/fp8_kernel.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1)
 - [doc/en/install.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1)
 - [doc/en/llama4.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1)
 - [doc/zh/DeepseekR1_V3_tutorial_zh.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1)
 
  This page documents the inference serving infrastructure in KTransformers. It covers server architecture, backend types, request processing pipelines, and deployment configurations for production serving of large language models using CPU-GPU heterogeneous computing.

 For detailed information on specific serving features, see:

 
 - Multi-concurrency implementation: [balance_serve Multi-Concurrency](https://deepwiki.com/kvcache-ai/ktransformers/6.1-balance_serve-multi-concurrency)
 - KV cache management: [Prefix Cache System](https://deepwiki.com/kvcache-ai/ktransformers/6.2-prefix-cache-system)
 - Distributed inference: [Multi-GPU Inference](https://deepwiki.com/kvcache-ai/ktransformers/6.3-multi-gpu-inference)
 - Optimization guidelines: [Performance Tuning](https://deepwiki.com/kvcache-ai/ktransformers/6.4-performance-tuning)
 - Long context support: [Long Context Inference](https://deepwiki.com/kvcache-ai/ktransformers/6.5-long-context-inference)
 
 For integration with the SGLang serving framework, see [SGLang Integration](https://deepwiki.com/kvcache-ai/ktransformers/4.3-sglang-integration).

 
## Architecture Overview

 
### Three-Layer Serving Architecture

 KTransformers implements a three-layer serving architecture designed to handle concurrent inference requests by offloading heavy Mixture-of-Experts (MoE) computations to the CPU while keeping attention and "hot" experts on the GPU.

 
```

```

 **Sources:** [doc/en/balance-serve.md20-26](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L20-L26) [doc/en/install.md173-186](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L173-L186)

 The architecture consists of:

 
 - **Server Layer** ([ktransformers/server/main.py1-150](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/ktransformers/server/main.py#L1-L150)): Handles user requests and serves the OpenAI-compatible API.
 - **Scheduler Layer**: Manages task scheduling and requests orchestration. Supports continuous batching by organizing queued requests into batches in a First-Come-First-Serve (FCFS) manner and sending them to the inference engine [doc/en/balance-serve.md25](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L25-L25)
 - **Inference Engine Layer**: Executes model inference using heterogeneous CPU-GPU computing via either `ktransformers` (single-concurrency) or `balance_serve` (multi-concurrency) backends.
 
 
## Server Entry Point

 
### Main Server Script

 The main server entry point is `ktransformers/server/main.py`. This script:

 
 - Parses command-line arguments.
 - Initializes the model with operator injection rules from YAML files [doc/en/balance-serve.md118](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L118-L118)
 - Loads quantized weights from GGUF format or Safetensors [doc/en/balance-serve.md116-117](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L116-L117)
 - Creates the inference engine (either `ktransformers` or `balance_serve` backend).
 - Exposes OpenAI-compatible API endpoints via FastAPI.
 
 
### Server Module Structure

 
```

```

 **Sources:** [doc/en/install.md176-186](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L176-L186) [doc/en/balance-serve.md113-140](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L113-L140)

 
### Command-Line Parameters

 
| Parameter | Description | Default | Required |
|---|---|---|---|
| --port | HTTP server port | 10002 | No |
| --model_path | Path to model config directory (must be local path) | - | Yes |
| --gguf_path | Path to directory containing GGUF quantized weight files | - | Yes |
| --optimize_config_path | YAML file defining operator injection rules and device placement | - | Yes |
| --backend_type | Backend engine: ktransformers (single) or balance_serve (multi-concurrent) | ktransformers | No |
| --cpu_infer | Number of CPU worker threads for expert computation | - | Yes |
| --max_new_tokens | Maximum tokens to generate per request | 1024 | No |
| --chunk_size | Maximum tokens processed per engine run (chunked prefill) | 256 | No |
| --cache_lens | Total KV cache length allocated by scheduler (tokens) | 32768 | No |
| --max_batch_size | Maximum concurrent requests (balance_serve only) | 1 | No |
| --force_think | Force DeepSeek-R1 to output reasoning tokens | False | No |

 **Important Constraints:**

 
 - Since v0.2.4, `--model_path` **MUST** be a local directory containing configuration files; Hugging Face online links are not supported for the server [doc/en/balance-serve.md136](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L136-L136)
 - `--max_batch_size` is only supported by the `balance_serve` backend [doc/en/balance-serve.md131](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L131-L131)
 
 **Sources:** [doc/en/install.md176-186](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L176-L186) [doc/en/balance-serve.md113-140](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L113-L140) [doc/en/balance-serve.md136-140](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L136-L140)

 
## Backend Types

 KTransformers supports two backend engines with different concurrency models:

 
### ktransformers Backend (Single-Concurrency)

 The original single-request-at-a-time backend suitable for:

 
 - Interactive single-user scenarios (e.g., `local_chat.py`).
 - Development and debugging.
 - Maximum per-request throughput with minimal latency for one user.
 
 **Invocation:** `--backend_type ktransformers` [doc/en/balance-serve.md134](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L134-L134)

 
### balance_serve Backend (Multi-Concurrency)

 Introduced in v0.2.4, this backend supports high-performance asynchronous concurrent scheduling implemented in C++ [doc/en/balance-serve.md6-7](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L6-L7)

 **Key Features:**

 
 - **Continuous Batching**: Organizes queued requests into batches in an FCFS manner [doc/en/balance-serve.md25](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L25-L25)
 - **Chunked Prefill**: Breaks large prompts into chunks for incremental processing [doc/en/balance-serve.md24](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L24-L24)
 - **Variable Batch Size CUDA Graph**: Implemented via `custom_flashinfer` to reduce memory and padding overhead [doc/en/balance-serve.md17](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L17-L17)
 - **Throughput Gains**: Improved overall throughput by approximately 130% under 4-way concurrency in benchmarks [doc/en/balance-serve.md18](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L18-L18)
 
 **Build Requirements:** To enable `balance_serve`, users must set `USE_BALANCE_SERVE=1` during installation [doc/en/install.md119](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L119-L119)

 **Sources:** [doc/en/balance-serve.md1-31](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L1-L31) [doc/en/balance-serve.md113-141](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L113-L141) [doc/en/install.md119-125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L119-L125)

 
## Request Processing Flow

 
### Sequence Diagram: balance_serve Multi-Concurrency

 
```

```

 **Sources:** [doc/en/balance-serve.md20-26](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L20-L26) [doc/en/balance-serve.md7-8](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L7-L8) [doc/en/balance-serve.md16-17](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L16-L17)

 
## Key Serving Concepts

 
### Continuous Batching

 The scheduler manages task scheduling and request orchestration by organizing queued requests into batches in a First-Come-First-Serve (FCFS) manner and sending them to the inference engine [doc/en/balance-serve.md25](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L25-L25)

 
### Chunked Prefill

 The inference engine supports chunked prefill, allowing large prompts to be processed in segments defined by `--chunk_size` [doc/en/balance-serve.md24](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L24-L24) [doc/en/balance-serve.md132](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L132-L132)

 
### 3-Layer Prefix Cache

 KTransformers supports prefix cache reuse using a 3-layer scheme (GPU-CPU-Disk) [README.md37](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L37-L37)

 
 - **GPU**: Highest performance, lowest capacity.
 - **CPU**: Medium performance, large capacity.
 - **Disk**: High capacity, used for long-term storage.
 
 For configuration details, see [Prefix Cache System](https://deepwiki.com/kvcache-ai/ktransformers/6.2-prefix-cache-system).

 
## Launching an Inference Server

 
### Multi-Concurrency Server (balance_serve Backend)

 For production deployments with concurrent request handling:

 
```

```

 **Sources:** [doc/en/balance-serve.md86-105](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L86-L105) [doc/en/balance-serve.md113-124](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L113-L124)

 
## Model-Specific Configurations

 
### DeepSeek-R1 / V3

 DeepSeek-R1 and V3 are supported on single (24GB VRAM) or multi-GPU setups.

 
 - **Rule**: Use `DeepSeek-V3-Chat-serve.yaml` or `DeepSeek-V3-Chat-fp8-linear-ggml-experts-serve.yaml` for hybrid quantization [doc/zh/DeepseekR1_V3_tutorial_zh.md139](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L139-L139)
 - **Force Think**: Use `--force_think` to ensure R1 outputs reasoning tags [doc/en/balance-serve.md137](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L137-L137)
 - **Long Context**: Supports up to 139K context for R1 in 24GB VRAM using FP8 kernels [README.md43](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L43-L43)
 
 
### LLaMA 4 (Experimental)

 LLaMA 4 models (Scout 17B-16E and Maverick 17B-128E) are experimentally supported via the `support-llama4` branch using the `balance_serve` backend [doc/en/llama4.md3-5](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1#L3-L5)

 
 - **Requirement**: `transformers >= 4.51.0` [doc/en/llama4.md125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1#L125-L125)
 - **Rule**: Use `Llama4-serve.yaml` [doc/en/llama4.md95](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1#L95-L95)
 
 
### MiniMax-M2.5

 MiniMax-M2.5 is supported with native FP8 precision and day-0 support [README.md22](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L22-L22)

 
## Related Documentation

 
 - **[balance_serve Multi-Concurrency](https://deepwiki.com/kvcache-ai/ktransformers/6.1-balance_serve-multi-concurrency)**: Detailed scheduler implementation and continuous batching.
 - **[Prefix Cache System](https://deepwiki.com/kvcache-ai/ktransformers/6.2-prefix-cache-system)**: 3-layer KV cache architecture.
 - **[Multi-GPU Inference](https://deepwiki.com/kvcache-ai/ktransformers/6.3-multi-gpu-inference)**: Layer distribution and transfer maps for distributed inference.
 - **[Performance Tuning](https://deepwiki.com/kvcache-ai/ktransformers/6.4-performance-tuning)**: Optimization guidelines and benchmarking methodologies.
 - **[Long Context Inference](https://deepwiki.com/kvcache-ai/ktransformers/6.5-long-context-inference)**: Support for 128K-1M tokens with sparse attention.
