> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/3-core-architecture](https://deepwiki.com/kvcache-ai/ktransformers/3-core-architecture)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Core Architecture

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
 
  
## Purpose and Scope

 This page provides an overview of KTransformers' fundamental architectural design, including its dual-module structure, core design principles, and how components integrate. For detailed information about specific aspects, see:

 
 - [System Design Overview](https://deepwiki.com/kvcache-ai/ktransformers/3.1-system-design-overview) — Overview of the dual-module architecture (kt-kernel + kt-sft), serving layers, and integration with external frameworks.
 - [CPU-GPU Heterogeneous Computing](https://deepwiki.com/kvcache-ai/ktransformers/3.2-cpu-gpu-heterogeneous-computing) — Details on the heterogeneous inference architecture, expert routing, and memory distribution strategy across GPU/CPU/disk.
 - [Build System and Compilation](https://deepwiki.com/kvcache-ai/ktransformers/3.3-build-system-and-compilation) — CMake build system, multi-variant compilation, CPU feature detection, and environment variables.
 
 
## Dual-Module Architecture

 KTransformers is structured as two independent but complementary modules:

 **kt-kernel**: High-performance inference engine focused on CPU-GPU heterogeneous execution, featuring AMX/AVX optimized kernels for quantized MoE inference. [README.md57-59](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L57-L59)

 **kt-sft**: Fine-tuning framework that integrates with LLaMA-Factory to enable LoRA-based training of ultra-large models using the same heterogeneous computing strategy. [README.md91-93](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L91-L93)

 Both modules share the same operator injection system and heterogeneous computing principles, but serve distinct use cases:

 
| Aspect | kt-kernel | kt-sft |
|---|---|---|
| Primary Use Case | Production inference serving | Model fine-tuning and training |
| Entry Point | ktransformers.server.main / SGLang integration | LLaMA-Factory with USE_KT=1 flag |
| Key Classes | KTMoEWrapper, CPUInfer, balance_serve | Custom trainer, LoRA injection |
| Backend Integration | SGLang, balance_serve scheduler | LLaMA-Factory training loop |
| Weight Format | Quantized (INT4/INT8/FP8/RAWINT4) | BF16/FP16 with heterogeneous acceleration |

 
### System Components Diagram

 This diagram bridges the natural language concepts of the framework to the specific code entities and directories.

 
```

```

 Sources: [README.md14-118](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L14-L118) [doc/en/balance-serve.md21-27](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L21-L27) [doc/en/install.md61-63](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L61-L63)

 
## Operator Injection System

 The core architectural pattern in KTransformers is **operator injection**: replacing standard PyTorch modules with optimized implementations at runtime based on YAML configuration files. This enables both inference and fine-tuning to use heterogeneous computing without modifying model source code. [doc/en/DeepseekR1_V3_tutorial.md118-125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L118-L125)

 
```

```

 Sources: [doc/en/DeepseekR1_V3_tutorial.md52-60](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L52-L60) [doc/en/balance-serve.md114-118](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L114-L118) [doc/en/fp8_kernel.md4-9](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1#L4-L9)

 
## Heterogeneous Computing Strategy

 The central architectural principle is **heterogeneous computing**: operators with high computational density (attention, shared experts) execute on GPU, while operators with high memory requirements (routed experts in large MoE models) execute on CPU. [README.md78-80](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L78-L80)

 
### Resource Allocation Examples

 
| Component | Device Placement | Optimization Method |
|---|---|---|
| MLA Attention | GPU | Triton MLA Kernel / FlashInfer doc/en/DeepseekR1_V3_tutorial.md97-98 |
| Shared Experts | GPU | FP8/BF16 Precision doc/en/fp8_kernel.md7 |
| Routed Experts | CPU | AMX/AVX INT4/INT8 Quantization README.md65-67 |

 
### Memory Hierarchy and Caching

 KTransformers implements a 3-layer prefix cache (GPU-CPU-Disk) to optimize memory usage during long-context inference. [README.md37](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L37-L37)

 Sources: [doc/en/DeepseekR1_V3_tutorial.md52-60](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L52-L60) [doc/en/fp8_kernel.md4-10](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1#L4-L10)

 
## Serving and Concurrency

 Starting from v0.2.4, KTransformers introduced the `balance_serve` backend, which provides a high-performance asynchronous concurrent scheduling system. [doc/en/balance-serve.md3-7](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L3-L7)

 
 - **Server**: Handles user requests and serves the OpenAI-compatible API. [doc/en/balance-serve.md23](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L23-L23)
 - **Inference Engine**: Executes model inference and supports chunked prefill. [doc/en/balance-serve.md24](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L24-L24)
 - **Scheduler**: Manages task orchestration and continuous batching in C++. [doc/en/balance-serve.md25](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L25-L25)
 
 Sources: [doc/en/balance-serve.md20-27](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L20-L27)

 
## Runtime CPU Optimization

 KTransformers builds multiple CPU-optimized variants, selecting the optimal backend at runtime based on hardware capabilities detected via `cpufeature`. [doc/en/install.md61-63](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L61-L63)

 
| Variant | CPU Support | Performance Characteristics |
|---|---|---|
| AMX | Intel Sapphire Rapids+ | Optimized INT8/INT4 MoE kernels doc/en/DeepseekR1_V3_tutorial.md54 |
| AVX512 | Modern Intel/AMD CPUs | High-performance fallback doc/en/balance-serve.md45-48 |
| AVX2 | Legacy CPUs | Minimum requirement for heterogeneous inference README.md21 |

 The build system supports environment variables like `USE_NUMA=1` to enable NUMA-aware memory management for multi-socket server configurations. [doc/en/install.md113-115](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L113-L115)

 Sources: [doc/en/DeepseekR1_V3_tutorial.md52-60](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L52-L60) [doc/en/install.md68-71](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L68-L71)
