> 来源: [https://deepwiki.com/huggingface/text-generation-inference](https://deepwiki.com/huggingface/text-generation-inference)
> 关联理由: HF 官方服务框架

# Overview

  Relevant source files 
 - [.github/workflows/autodocs.yaml](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/.github/workflows/autodocs.yaml)
 - [Cargo.lock](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/Cargo.lock)
 - [Cargo.toml](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/Cargo.toml)
 - [README.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1)
 - [docs/openapi.json](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/openapi.json)
 - [docs/source/_toctree.yml](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/_toctree.yml)
 - [docs/source/architecture.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/architecture.md?plain=1)
 - [docs/source/basic_tutorials/gated_model_access.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/basic_tutorials/gated_model_access.md?plain=1)
 - [docs/source/conceptual/quantization.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/conceptual/quantization.md?plain=1)
 - [docs/source/installation_amd.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/installation_amd.md?plain=1)
 - [docs/source/installation_inferentia.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/installation_inferentia.md?plain=1)
 - [docs/source/installation_intel.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/installation_intel.md?plain=1)
 - [docs/source/installation_nvidia.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/installation_nvidia.md?plain=1)
 - [docs/source/installation_tpu.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/installation_tpu.md?plain=1)
 - [docs/source/multi_backend_support.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/multi_backend_support.md?plain=1)
 - [docs/source/quicktour.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/quicktour.md?plain=1)
 - [docs/source/reference/api_reference.md](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/reference/api_reference.md?plain=1)
 - [integration-tests/neuron/test_implicit_env.py](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/integration-tests/neuron/test_implicit_env.py)
 - [update_doc.py](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/update_doc.py)
 
  This document provides a high-level introduction to Text Generation Inference (TGI), its architecture, and core capabilities. For detailed information about specific components, see the following pages:

 
 - System Architecture details: [System Architecture](https://deepwiki.com/huggingface/text-generation-inference/2-system-architecture)
 - Model implementation specifics: [Model Implementation](https://deepwiki.com/huggingface/text-generation-inference/3-model-implementation)
 - Advanced optimization features: [Advanced Features](https://deepwiki.com/huggingface/text-generation-inference/4-advanced-features)
 - Multi-backend hardware support: [Multi-Backend Support](https://deepwiki.com/huggingface/text-generation-inference/5-multi-backend-support)
 - Deployment guides: [Deployment](https://deepwiki.com/huggingface/text-generation-inference/6-deployment)
 
 
## What is Text Generation Inference

 Text Generation Inference (TGI) is a production-ready toolkit for deploying and serving Large Language Models (LLMs). Written primarily in Rust (router/launcher) and Python (model server), TGI is designed to maximize throughput and minimize latency for text generation workloads. It is used in production at Hugging Face to power Hugging Chat, the Inference API, and Inference Endpoints.

 **Sources:** [README.md16-17](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L16-L17) [README.md39-64](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L39-L64)

 
## Core Capabilities

 TGI implements several key features for high-performance LLM serving:

 
| Feature Category | Capabilities |
|---|---|
| Batching | Continuous batching of incoming requests for increased throughput |
| Streaming | Token streaming using Server-Sent Events (SSE) |
| Parallelism | Tensor Parallelism for inference across multiple GPUs |
| Memory Management | Paged Attention and prefix caching via RadixAllocator |
| Attention Optimization | Flash Attention and custom attention kernels |
| Quantization | bitsandbytes (4/8-bit), GPTQ, AWQ, EETQ, Marlin, FP8, EXL2 |
| Structured Generation | Grammar-constrained generation, JSON schema validation, tool calling |
| API Compatibility | OpenAI Messages API compatible endpoints |
| Observability | Distributed tracing (OpenTelemetry), Prometheus metrics |

 **Sources:** [README.md41-64](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L41-L64) [docs/openapi.json1-50](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/openapi.json#L1-L50) [docs/source/conceptual/quantization.md1-73](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/conceptual/quantization.md?plain=1#L1-L73)

 
## Three-Tier Architecture

 TGI follows a three-tier architecture where processes communicate via gRPC and HTTP:

 
```

```

 **Architecture Components:**

 
 - **text-generation-launcher**: Process orchestrator that spawns and configures both router and model server with compatible parameters. Located in [launcher/src/main.rs](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/launcher/src/main.rs)
 - **text-generation-router**: Rust-based HTTP server handling client requests, validation, batching, and gRPC communication with model server. Core implementation in [router/src/server.rs](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/server.rs)
 - **text-generation-server**: Python-based gRPC server performing model inference with hardware-optimized operations. Entry point at [server/text_generation_server/cli.py](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/server/text_generation_server/cli.py)
 
 This separation allows high-concurrency networking in Rust while leveraging Python's ML ecosystem for model execution.

 **Sources:** [docs/source/architecture.md1-14](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/architecture.md?plain=1#L1-L14) [README.md190-194](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L190-L194) [Cargo.toml1-21](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/Cargo.toml#L1-L21)

 
## Request Processing Flow

 The following diagram shows how a generation request flows through the system:

 
```

```

 Key stages in request processing:

 
 - **HTTP Endpoint**: Router receives requests at /generate, /generate_stream, or /v1/chat/completions
 - **Validation**: Request parameters validated against model constraints ([router/src/validation.rs](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/validation.rs))
 - **Chat Templates**: For chat endpoints, messages formatted using chat template ([router/src/infer/chat_template.rs](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/infer/chat_template.rs))
 - **Queuing**: Request added to queue managed by State ([router/src/queue.rs](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/queue.rs))
 - **Batching**: InferScheduler creates batches and allocates memory blocks ([router/src/scheduler_v3.rs](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/scheduler_v3.rs))
 - **Prefill**: Initial forward pass processes all input tokens via gRPC to server
 - **Decode Loop**: Iterative token generation with streaming results via Server-Sent Events
 
 **Sources:** [router/src/server.rs1-100](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/server.rs#L1-L100) [router/src/infer.rs1-50](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/infer.rs#L1-L50) [docs/source/architecture.md154-234](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/architecture.md?plain=1#L154-L234)

 
## Model Server Components

 The model server is organized around these key abstractions:

 
```

```

 The Model base class defines the interface for all model implementations:

 
 - warmup(): Initialize model and validate memory requirements
 - generate_token(): Core generation loop for a batch
 - decode_token(): Token decoding and sampling
 
 Each model type (e.g., FlashCausalLM, FlashVlmCausalLM) implements these methods with architecture-specific optimizations.

 **Sources:** [server/text_generation_server/models/__init__.py1-200](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/server/text_generation_server/models/__init__.py#L1-L200) [server/text_generation_server/models/model.py1-50](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/server/text_generation_server/models/model.py#L1-L50) [server/text_generation_server/models/flash_causal_lm.py1-100](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/server/text_generation_server/models/flash_causal_lm.py#L1-L100)

 
## Multi-Backend Hardware Support

 TGI supports multiple hardware backends with a unified API interface:

 
| Backend | Hardware | Container Tag | Key Features |
|---|---|---|---|
| CUDA | NVIDIA GPUs | ghcr.io/huggingface/text-generation-inference:3.3.5 | Flash Attention v2, Paged Attention, FP8, CUDA Graphs |
| ROCm | AMD GPUs | ghcr.io/huggingface/text-generation-inference:3.3.5-rocm | Custom Paged Attention, TunableOp, CK/Triton Flash Attention |
| Intel XPU | Intel GPUs | ghcr.io/huggingface/text-generation-inference:3.3.5-intel-xpu | IPEX optimizations |
| Intel CPU | Intel CPUs | ghcr.io/huggingface/text-generation-inference:3.3.5-intel-cpu | IPEX, OneDNN optimizations |
| Gaudi | Intel Gaudi | External repo | HPU Graphs, exponential bucketing |
| Neuron | AWS Inferentia | External backend | AWS Neuron SDK integration |
| TensorRT-LLM | NVIDIA GPUs | External backend | TensorRT optimizations |

 All backends share the same router layer and gRPC protocol, differing only in the model server implementation and optimizations.

 **Sources:** [README.md65-73](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L65-L73) [docs/source/installation_amd.md1-45](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/installation_amd.md?plain=1#L1-L45) [docs/source/installation_intel.md1-37](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/installation_intel.md?plain=1#L1-L37) [docs/source/multi_backend_support.md1-17](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/multi_backend_support.md?plain=1#L1-L17)

 
## API Interfaces

 TGI exposes two primary API surfaces:

 
### TGI Native API

 REST endpoints for text generation:

 
 - POST /generate: Single completion request
 - POST /generate_stream: Streaming completion with SSE
 - POST /tokenize: Tokenize input text
 - GET /info: Model and server information
 - GET /health: Health check endpoint
 - GET /metrics: Prometheus metrics
 
 **Sources:** [docs/openapi.json15-531](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/openapi.json#L15-L531) [router/src/server.rs200-400](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/server.rs#L200-L400)

 
### OpenAI Compatible API

 Compatible with OpenAI client libraries:

 
 - POST /v1/chat/completions: Chat completion (streaming/non-streaming)
 - POST /v1/completions: Text completion
 - GET /v1/models: List available models
 
 Example usage with OpenAI Python client:

 
```

```

 **Sources:** [docs/source/reference/api_reference.md1-100](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/reference/api_reference.md?plain=1#L1-L100) [docs/openapi.json532-747](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/openapi.json#L532-L747)

 
## Memory Optimization Systems

 TGI implements advanced memory management for efficient KV cache handling:

 
```

```

 **RadixAllocator**: Implements prefix caching using a radix tree structure. Common prompt prefixes are cached and reused across requests, avoiding redundant computation. Implementation in [router/src/block_allocator.rs](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/block_allocator.rs)

 **Paged Attention**: KV cache is divided into fixed-size blocks (pages), allowing non-contiguous memory allocation and efficient memory utilization. Pages are mapped via block tables.

 **Sources:** [router/src/block_allocator.rs1-100](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/block_allocator.rs#L1-L100) [README.md47](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L47-L47)

 
## Deployment Options

 TGI can be deployed in multiple ways:

 
### Docker (Recommended)

 
```

```

 
### Local Installation

 
```

```

 
### Nix

 Reproducible builds with pinned dependencies:

 
```

```

 **Sources:** [README.md75-120](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L75-L120) [README.md196-291](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L196-L291) [docs/source/quicktour.md1-103](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/quicktour.md?plain=1#L1-L103)

 
## Build System Overview

 TGI uses a multi-stage build process:

 
```

```

 Platform-specific Dockerfiles:

 
 - Dockerfile: NVIDIA CUDA support
 - Dockerfile_amd: AMD ROCm support
 - Dockerfile_intel: Intel XPU/CPU support
 - Dockerfile_gaudi: Intel Gaudi support
 
 CI/CD pipeline uses GitHub Actions with matrix builds for all platforms simultaneously.

 **Sources:** [Dockerfile1-100](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/Dockerfile#L1-L100) [Cargo.toml1-55](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/Cargo.toml#L1-L55) [.github/workflows/autodocs.yaml1-46](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/.github/workflows/autodocs.yaml#L1-L46)

 
## Key Configuration Parameters

 The launcher accepts numerous configuration parameters:

 
| Parameter | Purpose | Default |
|---|---|---|
| --model-id | Hugging Face model ID or local path | Required |
| --num-shard | Number of shards for tensor parallelism | 1 |
| --quantize | Quantization method (bitsandbytes, gptq, awq, etc) | None |
| --max-batch-total-tokens | Maximum tokens in a batch | Auto |
| --max-input-tokens | Maximum input sequence length | 1024 |
| --max-total-tokens | Maximum total sequence length (input + output) | 2048 |
| --dtype | Model precision (float16, bfloat16) | Auto |
| --trust-remote-code | Allow custom modeling code | False |

 Full list available via:

 
```

```

 **Sources:** [README.md126-129](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L126-L129) [launcher/src/main.rs1-100](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/launcher/src/main.rs#L1-L100) [update_doc.py32-83](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/update_doc.py#L32-L83)

 
## Continuous Batching Mechanism

 TGI's continuous batching allows new requests to be merged into active batches without waiting for previous requests to complete:

 
 - **Request arrives**: Added to queue via State::queue.append()
 - **Scheduler checks**: InferScheduler evaluates if batch can accommodate new request
 - **Dynamic merging**: If memory available, request added to existing CachedBatch
 - **Inference continues**: Model server processes merged batch
 - **Selective filtering**: Completed requests removed via filter_batch()
 
 This approach maximizes GPU utilization while maintaining low latency for individual requests.

 **Sources:** [router/src/scheduler_v3.rs1-100](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/router/src/scheduler_v3.rs#L1-L100) [README.md45](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L45-L45)

 
## Quantization Support

 TGI supports multiple quantization schemes:

 **Pre-quantized models** (require quantized weights):

 
 - **GPTQ**: 4-bit quantization with group-wise quantization
 - **AWQ**: Activation-aware weight quantization
 - **Marlin**: Optimized GPTQ kernels
 - **EXL2**: Variable bit-width quantization
 
 **On-the-fly quantization** (quantized at model load):

 
 - **bitsandbytes**: 8-bit and 4-bit (NF4/FP4) quantization
 - **EETQ**: INT8 quantization
 - **FP8**: 8-bit floating point (E4M3/E5M2)
 
 Usage:

 
```

```

 **Sources:** [docs/source/conceptual/quantization.md1-73](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/docs/source/conceptual/quantization.md?plain=1#L1-L73) [README.md48-54](https://github.com/huggingface/text-generation-inference/blob/24ee40d1/README.md?plain=1#L48-L54)

 
## Observability and Monitoring

 TGI provides comprehensive observability:

 **Prometheus Metrics**: Available at /metrics endpoint, including:

 
 - Request latency (prefill/decode)
 - Throughput metrics
 - Queue depth
 - Batch size statistic

...(截断，完整内容见源页面)
