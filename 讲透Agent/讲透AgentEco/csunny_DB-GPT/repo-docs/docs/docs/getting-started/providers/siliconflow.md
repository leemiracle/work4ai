---
sidebar_position: 4
title: SiliconFlow
---

# SiliconFlow

Configure DB-GPT to use SiliconFlow's hosted model API. SiliconFlow provides access to multiple open-source models through a unified API, hosted in China.

## Prerequisites

- A [SiliconFlow API key](https://siliconflow.cn/)
- DB-GPT installed with `proxy_openai` extra

## Install dependencies

```bash
uv sync --all-packages \
  --extra "base" \
  --extra "proxy_openai" \
  --extra "rag" \
  --extra "storage_chromadb" \
  --extra "dbgpts"
```

## Configuration

Edit `configs/dbgpt-proxy-siliconflow.toml`:

```toml
[models]
[[models.llms]]
name = "Qwen/Qwen2.5-Coder-32B-Instruct"
provider = "proxy/siliconflow"
api_key = "${env:SILICONFLOW_API_KEY}"

[[models.embeddings]]
name = "BAAI/bge-large-zh-v1.5"
provider = "proxy/openai"
api_url = "https://api.siliconflow.cn/v1/embeddings"
api_key = "${env:SILICONFLOW_API_KEY}"

[[models.rerankers]]
name = "BAAI/bge-reranker-v2-m3"
provider = "proxy/siliconflow"
api_key = "${env:SILICONFLOW_API_KEY}"
```

:::tip
Set the environment variable:

```bash
export SILICONFLOW_API_KEY="your-siliconflow-api-key"
```
:::

## Available models

SiliconFlow hosts a wide range of open-source models. Some popular choices:

| Model | Config name | Notes |
|---|---|---|
| Qwen2.5-Coder-32B | `Qwen/Qwen2.5-Coder-32B-Instruct` | Code-focused |
| Qwen2.5-72B | `Qwen/Qwen2.5-72B-Instruct` | General purpose |
| DeepSeek-V3 | `deepseek-ai/DeepSeek-V3` | Strong reasoning |
| GLM-4-9B | `THUDM/glm-4-9b-chat` | Chinese & English |

:::info
Check [SiliconFlow's model list](https://siliconflow.cn/) for the latest available models and pricing.
:::

## Features

SiliconFlow configuration also supports **rerankers** for enhanced RAG retrieval:

```toml
[[models.rerankers]]
name = "BAAI/bge-reranker-v2-m3"
provider = "proxy/siliconflow"
api_key = "${env:SILICONFLOW_API_KEY}"
```

## Start the server

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-siliconflow.toml
```

## Troubleshooting

| Issue | Solution |
|---|---|
| Authentication failed | Verify your SiliconFlow API key |
| Model not available | Check SiliconFlow's current model offerings |
| Slow responses | Some larger models may have higher latency |

## What's next

- [Getting Started](/docs/getting-started/quick-start) — Full setup walkthrough
- [Model Providers](/docs/getting-started/providers/) — Try other providers
