---
sidebar_position: 6
title: vLLM
---

# vLLM

Configure DB-GPT to use [vLLM](https://docs.vllm.ai/) for high-throughput local model inference on NVIDIA GPUs.

## Prerequisites

- **NVIDIA GPU** with CUDA 12.1+
- Sufficient VRAM for your chosen model (8 GB+ for 7B models)
- DB-GPT installed with `vllm` extra

## Install dependencies

```bash
uv sync --all-packages \
  --extra "base" \
  --extra "hf" \
  --extra "cuda121" \
  --extra "vllm" \
  --extra "rag" \
  --extra "storage_chromadb" \
  --extra "quant_bnb" \
  --extra "dbgpts"
```

## Configuration

Edit `configs/dbgpt-local-vllm.toml`:

```toml
[models]
[[models.llms]]
name = "DeepSeek-R1-Distill-Qwen-1.5B"
provider = "vllm"
# Download from HuggingFace automatically, or specify local path:
# path = "models/DeepSeek-R1-Distill-Qwen-1.5B"

[[models.embeddings]]
name = "BAAI/bge-large-zh-v1.5"
provider = "hf"
# path = "models/bge-large-zh-v1.5"
```

:::info Model download
If you don't specify a `path`, the model will be downloaded from HuggingFace Hub automatically. For large models, pre-downloading is recommended:

```bash
# Using huggingface-cli
huggingface-cli download deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --local-dir models/DeepSeek-R1-Distill-Qwen-1.5B
```
:::

## Popular model choices

| Model | VRAM Required | Notes |
|---|---|---|
| DeepSeek-R1-Distill-Qwen-1.5B | ~4 GB | Small, good for testing |
| GLM-4-9B-Chat | ~20 GB | Strong Chinese & English |
| Qwen2.5-7B-Instruct | ~16 GB | Good balance |
| Qwen2.5-Coder-7B-Instruct | ~16 GB | Code-focused |

## Start the server

```bash
uv run dbgpt start webserver --config configs/dbgpt-local-vllm.toml
```

:::tip GPU selection
To use a specific GPU:

```bash
CUDA_VISIBLE_DEVICES=0 uv run dbgpt start webserver --config configs/dbgpt-local-vllm.toml
```
:::

## Troubleshooting

| Issue | Solution |
|---|---|
| CUDA not found | Install CUDA 12.1+ and verify with `nvidia-smi` |
| Out of GPU memory | Use a smaller model or enable quantization (`quant_bnb`) |
| Model download fails | Pre-download the model or configure a HuggingFace mirror |
| Slow first request | vLLM compiles kernels on first run — subsequent requests are fast |

## What's next

- [Getting Started](/docs/getting-started/quick-start) — Full setup walkthrough
- [vLLM Advanced](/docs/installation/advanced_usage/vLLM_inference) — Advanced vLLM configuration
- [Model Providers](/docs/getting-started/providers/) — Try other providers
