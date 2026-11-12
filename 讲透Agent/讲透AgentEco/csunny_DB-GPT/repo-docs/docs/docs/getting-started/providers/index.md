---
sidebar_position: 0
title: Model Providers
summary: "Which DB-GPT model provider to choose and where each provider guide lives"
read_when:
  - You need to pick a provider for your first setup
  - You want to know whether to use API models, Ollama, or vLLM
---

# Model Providers

DB-GPT supports API providers and local runtimes. For a first run, use an API provider unless you specifically want local inference.

:::info Quick pick
Not sure which provider to choose? Start with **OpenAI** or **DeepSeek** for the fastest setup (API proxy, no GPU needed). Use **Ollama** if you want to run models locally without complex setup.
:::

## Provider comparison

| Provider | Type | GPU Required | Best for |
|---|---|---|---|
| [**OpenAI**](./openai) | API proxy | No | Production quality, fastest setup |
| [**DeepSeek**](./deepseek) | API proxy | No | Cost-effective, strong reasoning |
| [**Qwen (Tongyi)**](./qwen) | API proxy | No | Chinese language, Alibaba Cloud users |
| [**SiliconFlow**](./siliconflow) | API proxy | No | China-hosted, multiple model choices |
| [**Ollama**](./ollama) | Local proxy | Optional | Easy local models, privacy-first |
| [**vLLM**](./vllm) | Local | Yes (NVIDIA) | High-throughput production inference |

## How model configuration works

All models are configured in TOML files under `configs/`. Each config file defines:

- **LLM(s)** — The language model(s) for chat and reasoning
- **Embedding(s)** — The embedding model(s) for RAG and knowledge search
- **Reranker(s)** — Optional re-ranking models for better retrieval

```toml
[models]

# Language model
[[models.llms]]
name = "model-name"
provider = "provider-type"
api_key = "your-api-key"

# Embedding model
[[models.embeddings]]
name = "embedding-model-name"
provider = "provider-type"
api_key = "your-api-key"
```

:::tip Environment variables
You can use environment variable syntax in TOML configs: `"${env:VARIABLE_NAME:-default_value}"`. This keeps secrets out of config files.
:::

## Provider guides

- [OpenAI](/docs/getting-started/providers/openai) — fastest default for a first setup
- [DeepSeek](/docs/getting-started/providers/deepseek) — strong reasoning, OpenAI-compatible proxy pattern
- [Qwen (Tongyi)](/docs/getting-started/providers/qwen) — Alibaba Cloud / DashScope
- [SiliconFlow](/docs/getting-started/providers/siliconflow) — China-hosted API options
- [Ollama](/docs/getting-started/providers/ollama) — simple local model runtime
- [vLLM](/docs/getting-started/providers/vllm) — GPU-backed local inference for heavier workloads

## More providers

DB-GPT also supports additional providers through its proxy system. See [Advanced LLM Configuration](/docs/installation/advanced_usage/More_proxyllms) for:

- Azure OpenAI
- Google Gemini
- Anthropic Claude
- Baichuan
- Spark (iFlyTek)
- And more
