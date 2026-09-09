> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/12-api-and-usage-examples](https://deepwiki.com/kvcache-ai/ktransformers/12-api-and-usage-examples)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# API and Usage Examples

  Relevant source files 
 - [.github/workflows/release-pypi.yml](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/workflows/release-pypi.yml)
 - [doc/en/balance-serve.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1)
 - [doc/en/fp8_kernel.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1)
 - [doc/en/install.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1)
 - [doc/en/llama4.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1)
 - [doc/zh/DeepseekR1_V3_tutorial_zh.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1)
 - [kt-kernel/CMakeLists.txt](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/CMakeLists.txt)
 - [kt-kernel/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1)
 - [kt-kernel/README_zh.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README_zh.md?plain=1)
 - [kt-kernel/install.sh](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/install.sh)
 - [kt-kernel/setup.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/setup.py)
 
  This page provides practical examples demonstrating common use cases for KTransformers. It covers both basic testing scenarios and production deployment patterns, with concrete command-line examples and configuration guidance.

 For detailed step-by-step tutorials on specific deployment scenarios, see:

 
 - Running production inference servers: [Running Inference Server](https://deepwiki.com/kvcache-ai/ktransformers/12.1-running-inference-server)
 - Fine-Tuning Models: [Fine-Tuning Models](https://deepwiki.com/kvcache-ai/ktransformers/12.2-fine-tuning-models)
 - Python API usage: [Python API Usage](https://deepwiki.com/kvcache-ai/ktransformers/12.3-python-api-usage)
 - OpenAI API Integration: [OpenAI API Integration](https://deepwiki.com/kvcache-ai/ktransformers/12.4-openai-api-integration)
 
 For installation instructions, see [Installation](https://deepwiki.com/kvcache-ai/ktransformers/2.1-installation). For model-specific deployment guides, see [Model Deployment Guides](https://deepwiki.com/kvcache-ai/ktransformers/9-model-deployment-guides).

 
---

 
## Quick Start Examples

 
### Basic Local Chat

 The simplest way to test KTransformers is using the `local_chat.py` script for single-turn inference:

 
```

```

 **Key Parameters:**

 
 - `--model_path`: Hugging Face model name or local path (only config files needed, not `.safetensors`) [doc/en/install.md164-165](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L164-L165)
 - `--gguf_path`: Directory containing quantized GGUF weight files [doc/en/install.md168-170](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L168-L170)
 - `--cpu_infer`: Number of CPU workers for expert inference (typically total cores - 2) [doc/en/install.md172](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L172-L172)
 - `--max_new_tokens`: Maximum tokens to generate per request [doc/en/install.md171](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L171-L171)
 
 **Sources:** [doc/en/install.md134-172](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L134-L172)

 
---

 
### Production Server Deployment

 For production workloads with OpenAI-compatible API using the `balance_serve` backend:

 
```

```

 **Key Parameters:**

 
 - `--optimize_config_path`: YAML rules defining layer placement and operator injection [doc/en/balance-serve.md118](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L118-L118)
 - `--chunk_size`: Maximum tokens processed per engine iteration (for chunked prefill) [doc/en/balance-serve.md132](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L132-L132)
 - `--cache_lens`: Total KV cache pool size shared across all concurrent requests [doc/en/balance-serve.md130](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L130-L130)
 - `--max_batch_size`: Maximum concurrent requests processed simultaneously [doc/en/balance-serve.md131](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L131-L131)
 - `--backend_type`: Use `balance_serve` for multi-concurrency (v0.2.4+) or `ktransformers` for single-request [doc/en/balance-serve.md134](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L134-L134)
 - `--force_think`: Force responding with the reasoning tag for DeepSeek-R1 [doc/en/balance-serve.md137](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L137-L137)
 
 **Sources:** [doc/en/balance-serve.md113-138](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L113-L138) [doc/zh/DeepseekR1_V3_tutorial_zh.md133-152](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L133-L152)

 
---

 
### Code-Level Entry Point Diagram

 **Title: From Command Line to Kernel Execution**

 
```

```

 **Sources:** [doc/en/install.md134-294](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L134-L294) [doc/en/balance-serve.md113-157](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L113-L157) [kt-kernel/README.md35-37](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L35-L37)

 
---

 
## Model-Specific Examples

 
### DeepSeek-R1 / V3 (671B Parameters)

 **Single-Socket Configuration (382GB RAM, 14GB VRAM):** Requires `USE_BALANCE_SERVE=1` during installation [doc/en/install.md119](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L119-L119) Use `--cpu_infer 33` and `numactl -N 1 -m 1` to avoid cross-NUMA data transfer [doc/zh/DeepseekR1_V3_tutorial_zh.md151-165](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L151-L165)

 **Dual-Socket Configuration (1TB RAM, 14GB VRAM):** Requires `USE_NUMA=1` and `USE_BALANCE_SERVE=1` during installation [doc/en/install.md124](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L124-L124) Use `--cpu_infer 65` [doc/zh/DeepseekR1_V3_tutorial_zh.md181-185](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L181-L185)

 **Sources:** [doc/en/balance-serve.md107-138](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L107-L138) [doc/zh/DeepseekR1_V3_tutorial_zh.md156-183](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L156-L183)

 
---

 
### LLaMA 4 (Experimental - support-llama4 branch)

 LLaMA 4 support targets the Meta LLaMA 4 Scout (17B-16E) and Maverick (17B-128E) models [doc/en/llama4.md5-15](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1#L5-L15)

 
```

```

 **Resources:**

 
 - Scout (16 Experts): ~65GB RAM, 10GB VRAM [doc/en/llama4.md30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1#L30-L30)
 - Maverick (128 Experts): ~270GB RAM, 12GB VRAM [doc/en/llama4.md30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1#L30-L30)
 
 **Sources:** [doc/en/llama4.md34-118](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1#L34-L118)

 
---

 
## Deployment Workflow Diagram

 **Title: Complete Deployment Pipeline from Setup to Inference**

 
```

```

 **Sources:** [doc/en/install.md12-294](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L12-L294) [doc/en/balance-serve.md44-157](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L44-L157)

 
---

 
## Advanced Examples

 
### FP8 Hybrid Quantization (DeepSeek-V3/R1)

 Use FP8 precision for Attention/Shared-Experts and GGML for Experts to balance performance and memory (~19GB VRAM) [doc/en/fp8_kernel.md4-15](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1#L4-L15)

 
```

```

 **Sources:** [doc/en/fp8_kernel.md1-76](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1#L1-L76)

 
---

 
### SGLang Integration with kt-kernel

 KT-Kernel can be integrated into SGLang for high-performance production serving using specific `--kt-*` parameters [kt-kernel/README.md12-15](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L12-L15)

 
```

```

 **Key Integration Parameters:**

 
 - `--kt-method`: Backend type (`AMXINT4`, `AMXINT8`, or `LLAMAFILE`) [kt-kernel/README_zh.md172](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README_zh.md?plain=1#L172-L172)
 - `--kt-weight-path`: Path to converted CPU experts [kt-kernel/README_zh.md173](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README_zh.md?plain=1#L173-L173)
 - `--kt-cpuinfer`: Number of CPU inference threads [kt-kernel/README_zh.md174](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README_zh.md?plain=1#L174-L174)
 - `--kt-num-gpu-experts`: Number of experts kept on GPU [kt-kernel/README_zh.md176](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README_zh.md?plain=1#L176-L176)
 
 **Sources:** [kt-kernel/README.md12-18](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L12-L18) [kt-kernel/README_zh.md110-191](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README_zh.md?plain=1#L110-L191)

 
---

 
## Troubleshooting Common Issues

 
 - **DeepSeek-R1 No Thinking**: Use `--force_think` to prevent the model from skipping reasoning steps [doc/zh/DeepseekR1_V3_tutorial_zh.md152](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L152-L152)
 - **CUDA OOM on Long Context**: Adjust `--cache_lens` and `--chunk_size`. Chunked prefill helps manage memory overhead [doc/en/balance-serve.md120-133](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L120-L133)
 - **CPU Variant Selection**: Use `KT_KERNEL_CPU_VARIANT` to override automatic detection (e.g., `export KT_KERNEL_CPU_VARIANT=avx2`) [kt-kernel/README.md141-143](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L141-L143)
 - **Build Failures**: Ensure `libhwloc-dev` and `pkg-config` are installed [kt-kernel/README.md23](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L23-L23)
 
 **Sources:** [doc/en/balance-serve.md113-138](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L113-L138) [kt-kernel/README.md21-24](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L21-L24) [kt-kernel/README.md140-149](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L140-L149)
