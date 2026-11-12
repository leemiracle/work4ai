---
sidebar_position: 3
title: Qwen (Tongyi)
---

# Qwen (Tongyi)

Configure DB-GPT to use Alibaba Cloud's Qwen models via the DashScope API.

## Prerequisites

- A [DashScope API key](https://dashscope.console.aliyun.com/)
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

Edit `configs/dbgpt-proxy-tongyi.toml`:

```toml
[models]
[[models.llms]]
name = "qwen-plus"
provider = "proxy/tongyi"
api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = "${env:DASHSCOPE_API_KEY}"

[[models.embeddings]]
name = "text-embedding-v3"
provider = "proxy/tongyi"
api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
api_key = "${env:DASHSCOPE_API_KEY}"
```

:::tip
Set the environment variable to keep your key out of config:

```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```
:::

## Available models

### LLMs

| Model | Config name | Notes |
|---|---|---|
| Qwen-Max | `qwen-max` | Flagship model, best quality |
| Qwen-Plus | `qwen-plus` | Balanced performance and cost |
| Qwen-Turbo | `qwen-turbo` | Fastest and cheapest |
| Qwen-Long | `qwen-long` | Extended context window |

### Embeddings

| Model | Config name | Notes |
|---|---|---|
| text-embedding-v3 | `text-embedding-v3` | Recommended |
| text-embedding-v2 | `text-embedding-v2` | Previous generation |

## Start the server

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-tongyi.toml
```

## Troubleshooting

| Issue | Solution |
|---|---|
| `InvalidAPIKey` | Verify your DashScope API key and ensure it is activated |
| Model quota exceeded | Check your DashScope console for usage limits |
| Slow response | Try `qwen-turbo` for faster responses |

## What's next

- [Getting Started](/docs/getting-started/quick-start) — Full setup walkthrough
- [Model Providers](/docs/getting-started/providers/) — Try other providers
