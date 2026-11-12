---
sidebar_position: 0
title: Source Code Deployment
summary: "Run DB-GPT from source with uv, configure a provider, and verify the webserver"
read_when:
  - You want the repo-based install instead of Docker
  - You need the most flexible setup for development or customization
---

# Source Code Deployment

Deploy DB-GPT directly from source code. This is the most flexible option for development, debugging, and custom integrations.

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## Hardware requirements

| Mode | CPU × RAM | GPU | Notes |
|---|---|---|---|
| API proxy | 4C × 8 GB | None | Proxy mode does not use local GPU |
| Local model | 8C × 32 GB | ≥ 24 GB VRAM | NVIDIA GPU with CUDA support |

## Step 1 — Clone the repository

```bash
git clone https://github.com/eosphoros-ai/DB-GPT.git
cd DB-GPT
```

## Step 2 — Install uv

<Tabs>
  <TabItem value="sh" label="macOS / Linux" default>

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

  </TabItem>
  <TabItem value="pypi" label="PyPI (pipx)">

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade pipx
python -m pipx ensurepath
pipx install uv --global
```

  </TabItem>
</Tabs>

Verify:

```bash
uv --version
```

## Step 3 — Install dependencies

<Tabs>
  <TabItem value="openai" label="OpenAI (proxy)" default>

```bash
uv sync --all-packages \
  --extra "base" \
  --extra "proxy_openai" \
  --extra "rag" \
  --extra "storage_chromadb" \
  --extra "dbgpts"
```

  </TabItem>
  <TabItem value="deepseek" label="DeepSeek (proxy)">

```bash
uv sync --all-packages \
  --extra "base" \
  --extra "proxy_openai" \
  --extra "rag" \
  --extra "storage_chromadb" \
  --extra "dbgpts"
```

:::info
DeepSeek uses the OpenAI-compatible proxy, so the extras are the same as OpenAI.
:::

  </TabItem>
  <TabItem value="ollama" label="Ollama (local)">

```bash
uv sync --all-packages \
  --extra "base" \
  --extra "proxy_ollama" \
  --extra "rag" \
  --extra "storage_chromadb" \
  --extra "dbgpts"
```

  </TabItem>
  <TabItem value="gpu" label="Local GPU (HuggingFace)">

```bash
uv sync --all-packages \
  --extra "base" \
  --extra "cuda121" \
  --extra "hf" \
  --extra "rag" \
  --extra "storage_chromadb" \
  --extra "quant_bnb" \
  --extra "dbgpts"
```

  </TabItem>
</Tabs>

<details>
<summary><strong>Use the interactive install helper</strong></summary>

DB-GPT provides an interactive helper to generate the right `uv sync` command:

```bash
uv run install_help.py install-cmd --interactive
```

Or list all available extras:

```bash
uv run install_help.py list
```

</details>

## Step 4 — Configure your model

Edit the TOML config file for your chosen provider. See [Model Providers](/docs/getting-started/providers/) for details.

<Tabs>
  <TabItem value="openai" label="OpenAI" default>

Edit `configs/dbgpt-proxy-openai.toml`:

```toml
[models]
[[models.llms]]
name = "chatgpt_proxyllm"
provider = "proxy/openai"
api_key = "your-openai-api-key"    # <-- replace

[[models.embeddings]]
name = "text-embedding-3-small"
provider = "proxy/openai"
api_key = "your-openai-api-key"    # <-- replace
```

  </TabItem>
  <TabItem value="deepseek" label="DeepSeek">

Edit `configs/dbgpt-proxy-deepseek.toml`:

```toml
[models]
[[models.llms]]
name = "deepseek-reasoner"
provider = "proxy/deepseek"
api_key = "your-deepseek-api-key"  # <-- replace

[[models.embeddings]]
name = "BAAI/bge-large-zh-v1.5"
provider = "hf"
```

:::info
If using a HuggingFace embedding, also add `--extra "hf"` and `--extra "cpu"` to the install command.
:::

  </TabItem>
  <TabItem value="ollama" label="Ollama">

Make sure [Ollama](https://ollama.ai) is running, then edit `configs/dbgpt-proxy-ollama.toml`:

```toml
[models]
[[models.llms]]
name = "qwen2.5:latest"
provider = "proxy/ollama"
api_base = "http://localhost:11434"

[[models.embeddings]]
name = "nomic-embed-text:latest"
provider = "proxy/ollama"
api_base = "http://localhost:11434"
```

  </TabItem>
</Tabs>

:::tip Environment variables
Use `"${env:OPENAI_API_KEY}"` syntax in TOML to read from environment variables instead of hardcoding keys.
:::

## Step 5 — Start the server

<Tabs>
  <TabItem value="openai" label="OpenAI" default>

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
```

  </TabItem>
  <TabItem value="deepseek" label="DeepSeek">

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-deepseek.toml
```

  </TabItem>
  <TabItem value="ollama" label="Ollama">

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-ollama.toml
```

  </TabItem>
</Tabs>

## Step 6 — Open the Web UI

Open your browser and visit **[http://localhost:5670](http://localhost:5670)**.

:::tip Verify it works
If the Web UI loads and you can start a chat conversation, your DB-GPT is running.
:::

## Common first-run issues

- **`uv sync` fails**
  - Re-check Python and uv: [Prerequisites](/docs/getting-started/prerequisites)
  - If you are in China, use a mirror via `UV_INDEX_URL`
- **Provider auth fails**
  - Verify the selected TOML file under `configs/`
  - Check the matching provider guide: [Model Providers](/docs/getting-started/providers/)
- **Server starts but UI is blank**
  - Confirm the terminal shows the webserver started cleanly
  - Check whether another process is already using port `5670`

## Database configuration

<Tabs>
  <TabItem value="sqlite" label="SQLite (default)" default>

SQLite is the default — tables are created automatically. No extra setup needed.

```toml
[service.web.database]
type = "sqlite"
path = "pilot/meta_data/dbgpt.db"
```

  </TabItem>
  <TabItem value="mysql" label="MySQL">

1. Create the database:

```bash
mysql -h127.0.0.1 -uroot -p{your_password} < ./assets/schema/dbgpt.sql
```

2. Update your TOML config:

```toml
[service.web.database]
type = "mysql"
host = "127.0.0.1"
port = 3306
user = "root"
database = "dbgpt"
password = "your-password"
```

  </TabItem>
</Tabs>

## Load test data (optional)

```bash
# Linux / macOS
bash ./scripts/examples/load_examples.sh

# Windows
.\scripts\examples\load_examples.bat
```

## Run web front-end separately (optional)

For front-end development or custom UI work:

```bash
cd web && npm install
cp .env.template .env
# Edit .env — set API_BASE_URL=http://localhost:5670
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Next steps

| Topic | Link |
|---|---|
| Configure more model providers | [Model Providers](/docs/getting-started/providers/) |
| Deploy with Docker | [Docker](/docs/getting-started/deploy/docker) |
| Deploy as a cluster | [Cluster](/docs/getting-started/deploy/cluster) |
| Explore the Web UI | [Web UI Guide](/docs/getting-started/web-ui/) |
