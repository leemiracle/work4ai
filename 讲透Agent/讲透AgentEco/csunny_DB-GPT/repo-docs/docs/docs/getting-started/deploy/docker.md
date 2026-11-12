---
sidebar_position: 1
title: Docker Deployment
---

# Docker Deployment

Run DB-GPT in a single Docker container — no Python setup required.

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- For GPU mode: [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Deploy with API proxy (no GPU)

The fastest way to get started. Uses a cloud LLM provider — no GPU needed.

### Step 1 — Pull the image

```bash
docker pull eosphorosai/dbgpt-openai:latest
```

### Step 2 — Run the container

<Tabs>
  <TabItem value="siliconflow" label="SiliconFlow" default>

```bash
docker run -it --rm \
  -e SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY} \
  -p 5670:5670 \
  --name dbgpt \
  eosphorosai/dbgpt-openai
```

Replace `${SILICONFLOW_API_KEY}` with your actual key from [SiliconFlow](https://cloud.siliconflow.cn/account/ak).

  </TabItem>
  <TabItem value="openai" label="OpenAI">

```bash
docker run -it --rm \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  -v ./configs/dbgpt-proxy-openai.toml:/app/configs/dbgpt-proxy-openai.toml \
  -p 5670:5670 \
  --name dbgpt \
  eosphorosai/dbgpt-openai \
  dbgpt start webserver --config /app/configs/dbgpt-proxy-openai.toml
```

  </TabItem>
</Tabs>

### Step 3 — Open the Web UI

Visit **[http://localhost:5670](http://localhost:5670)** in your browser.

---

## Deploy with GPU (local model)

Run models locally on your NVIDIA GPU.

### Step 1 — Download models

<Tabs>
  <TabItem value="modelscope" label="ModelScope (China)" default>

```bash
mkdir -p ./models && cd ./models
git lfs install
git clone https://www.modelscope.cn/Qwen/Qwen2.5-Coder-0.5B-Instruct.git
git clone https://www.modelscope.cn/BAAI/bge-large-zh-v1.5.git
cd ..
```

  </TabItem>
  <TabItem value="huggingface" label="Hugging Face">

```bash
mkdir -p ./models && cd ./models
git lfs install
git clone https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct
git clone https://huggingface.co/BAAI/bge-large-zh-v1.5
cd ..
```

  </TabItem>
</Tabs>

### Step 2 — Create a config file

Create `dbgpt-local-gpu.toml`:

```toml
[models]
[[models.llms]]
name = "Qwen2.5-Coder-0.5B-Instruct"
provider = "hf"
path = "/app/models/Qwen2.5-Coder-0.5B-Instruct"

[[models.embeddings]]
name = "BAAI/bge-large-zh-v1.5"
provider = "hf"
path = "/app/models/bge-large-zh-v1.5"
```

### Step 3 — Run the container

```bash
docker run --ipc host --gpus all \
  -it --rm \
  -p 5670:5670 \
  -v ./dbgpt-local-gpu.toml:/app/configs/dbgpt-local-gpu.toml \
  -v ./models:/app/models \
  --name dbgpt \
  eosphorosai/dbgpt \
  dbgpt start webserver --config /app/configs/dbgpt-local-gpu.toml
```

| Flag | Purpose |
|---|---|
| `--ipc host` | Enables host IPC mode for better performance |
| `--gpus all` | Allows the container to use all available GPUs |
| `-v ./models:/app/models` | Mounts local models into the container |

### Step 4 — Open the Web UI

Visit **[http://localhost:5670](http://localhost:5670)** in your browser.

---

## Persist data (optional)

By default, data is lost when the container stops. To persist it:

```bash
mkdir -p ./pilot/data ./pilot/message ./pilot/alembic_versions
```

Add these volume mounts to your `docker run` command:

```bash
-v ./pilot/data:/app/pilot/data \
-v ./pilot/message:/app/pilot/message \
-v ./pilot/alembic_versions:/app/pilot/meta_data/alembic/versions
```

And configure the database path in your TOML file:

```toml
[service.web.database]
type = "sqlite"
path = "/app/pilot/message/dbgpt.db"
```

## Build your own image

To build a custom Docker image from source:

```bash
# Proxy image (no GPU required)
bash docker/base/build_proxy_image.sh

# Full image (with GPU support)
bash docker/base/build_image.sh
```

:::info
For detailed build options, see `bash docker/base/build_image.sh --help`.
:::

## Directory structure

After setup, your working directory looks like:

```
.
├── dbgpt-local-gpu.toml    # Your config file
├── models/
│   ├── Qwen2.5-Coder-0.5B-Instruct/
│   └── bge-large-zh-v1.5/
└── pilot/                  # (optional) persistent data
    ├── data/
    └── message/
```

## Next steps

| Topic | Link |
|---|---|
| Docker Compose (multi-service) | [Docker Compose](/docs/getting-started/deploy/docker-compose) |
| Cluster deployment | [Cluster](/docs/getting-started/deploy/cluster) |
| Model providers | [Providers](/docs/getting-started/providers/) |
