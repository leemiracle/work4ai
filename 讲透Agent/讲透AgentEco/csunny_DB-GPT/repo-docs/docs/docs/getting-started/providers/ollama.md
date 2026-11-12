---
sidebar_position: 5
title: Ollama
---

# Ollama

Configure DB-GPT to use [Ollama](https://ollama.ai) for running models locally. Ollama provides the easiest way to run open-source models on your own machine.

## Prerequisites

- [Ollama](https://ollama.ai) installed and running
- DB-GPT installed with `proxy_ollama` extra

## Install Ollama

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="mac" label="macOS" default>

```bash
# Download from https://ollama.ai or use Homebrew:
brew install ollama
```

  </TabItem>
  <TabItem value="linux" label="Linux">

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

  </TabItem>
  <TabItem value="windows" label="Windows">

Download the installer from [ollama.ai](https://ollama.ai).

  </TabItem>
</Tabs>

### Pull models

```bash
# Pull a chat model
ollama pull deepseek-r1:1.5b

# Pull an embedding model
ollama pull bge-m3:latest
```

:::tip
Use `ollama list` to see all downloaded models.
:::

## Install DB-GPT dependencies

```bash
uv sync --all-packages \
  --extra "base" \
  --extra "proxy_ollama" \
  --extra "rag" \
  --extra "storage_chromadb" \
  --extra "dbgpts"
```

## Configuration

Edit `configs/dbgpt-proxy-ollama.toml`:

```toml
[models]
[[models.llms]]
name = "deepseek-r1:1.5b"
provider = "proxy/ollama"
api_base = "http://localhost:11434"
api_key = ""

[[models.embeddings]]
name = "bge-m3:latest"
provider = "proxy/ollama"
api_url = "http://localhost:11434"
api_key = ""
```

:::info
The `api_key` can be left empty for local Ollama. If running Ollama on a different machine, update `api_base` to point to that host.
:::

## Popular model choices

### Chat models

| Model | Pull command | Size | Notes |
|---|---|---|---|
| DeepSeek-R1 1.5B | `ollama pull deepseek-r1:1.5b` | ~1 GB | Small, fast, reasoning |
| Qwen2.5 7B | `ollama pull qwen2.5:7b` | ~4.7 GB | Good balance |
| Llama 3.1 8B | `ollama pull llama3.1:8b` | ~4.7 GB | Meta's latest |
| Mistral 7B | `ollama pull mistral:7b` | ~4.1 GB | Fast general use |

### Embedding models

| Model | Pull command | Notes |
|---|---|---|
| bge-m3 | `ollama pull bge-m3:latest` | Multilingual |
| nomic-embed-text | `ollama pull nomic-embed-text` | English-focused |

## Start the server

Make sure Ollama is running first:

```bash
# Start Ollama (if not running as a service)
ollama serve
```

Then start DB-GPT:

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-ollama.toml
```

## Troubleshooting

| Issue | Solution |
|---|---|
| Connection refused | Ensure Ollama is running: `ollama serve` |
| Model not found | Pull the model first: `ollama pull model-name` |
| Slow responses | Try a smaller model or ensure GPU is being used |
| Out of memory | Use a smaller quantized model (e.g., `qwen2.5:7b-q4_0`) |

## What's next

- [Getting Started](/docs/getting-started/quick-start) — Full setup walkthrough
- [Ollama Advanced](/docs/installation/advanced_usage/ollama) — Advanced Ollama configuration
- [Model Providers](/docs/getting-started/providers/) — Try other providers
