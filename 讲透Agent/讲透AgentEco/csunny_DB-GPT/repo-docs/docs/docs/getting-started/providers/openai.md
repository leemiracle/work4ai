---
sidebar_position: 1
title: OpenAI
---

# OpenAI

Configure DB-GPT to use OpenAI's GPT models and embedding models.

## Prerequisites

- An [OpenAI API key](https://platform.openai.com/api-keys)
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

Edit `configs/dbgpt-proxy-openai.toml`:

```toml
[models]
[[models.llms]]
name = "gpt-4o"
provider = "proxy/openai"
api_base = "https://api.openai.com/v1"
api_key = "sk-your-openai-api-key"

[[models.embeddings]]
name = "text-embedding-3-small"
provider = "proxy/openai"
api_url = "https://api.openai.com/v1/embeddings"
api_key = "sk-your-openai-api-key"
```

:::tip Use environment variables
Instead of hardcoding your API key, use environment variables:

```toml
api_key = "${env:OPENAI_API_KEY}"
```

```bash
export OPENAI_API_KEY="sk-your-openai-api-key"
```
:::

## Available models

### LLMs

| Model | Config name | Notes |
|---|---|---|
| GPT-4o | `gpt-4o` | Recommended — best quality |
| GPT-4o mini | `gpt-4o-mini` | Faster and cheaper |
| GPT-4 Turbo | `gpt-4-turbo` | Previous generation |
| GPT-3.5 Turbo | `gpt-3.5-turbo` | Budget option |

### Embeddings

| Model | Config name | Dimensions |
|---|---|---|
| text-embedding-3-small | `text-embedding-3-small` | 1536 |
| text-embedding-3-large | `text-embedding-3-large` | 3072 |
| text-embedding-ada-002 | `text-embedding-ada-002` | 1536 |

## Start the server

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
```

## Azure OpenAI

To use Azure OpenAI, change the `api_base` to your Azure endpoint:

```toml
[[models.llms]]
name = "gpt-4o"
provider = "proxy/openai"
api_base = "https://your-resource.openai.azure.com/openai/deployments/your-deployment"
api_key = "your-azure-api-key"
```

## Troubleshooting

| Issue | Solution |
|---|---|
| `AuthenticationError` | Check that your API key is valid and has billing enabled |
| `RateLimitError` | Reduce request frequency or upgrade your OpenAI plan |
| Connection timeout | Check network connectivity; configure proxy if needed |
| Model not found | Verify the model name matches OpenAI's current offerings |

## What's next

- [Getting Started](/docs/getting-started/quick-start) — Full setup walkthrough
- [Config Reference](/docs/config/config-reference) — All configuration options
- [More Proxy LLMs](/docs/installation/advanced_usage/More_proxyllms) — Additional API providers
