---
sidebar_position: 2
title: Docker Compose Deployment
---

# Docker Compose Deployment

Deploy DB-GPT with MySQL using Docker Compose — a production-ready setup with persistent storage.

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed
- An API key from a supported provider

## Quick start

The root `docker-compose.yml` deploys DB-GPT with a MySQL database and SiliconFlow as the default LLM provider.

### Step 1 — Set your API key

<Tabs>
  <TabItem value="siliconflow" label="SiliconFlow" default>

```bash
export SILICONFLOW_API_KEY="your-siliconflow-api-key"
```

Get your key at [SiliconFlow](https://cloud.siliconflow.cn/account/ak).

  </TabItem>
  <TabItem value="aiml" label="AI/ML API">

```bash
export AIMLAPI_API_KEY="your-aiml-api-key"
```

Get your key at [AI/ML API](https://aimlapi.com/).

  </TabItem>
</Tabs>

### Step 2 — Start the services

<Tabs>
  <TabItem value="siliconflow" label="SiliconFlow" default>

```bash
SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY} docker compose up -d
```

  </TabItem>
  <TabItem value="aiml" label="AI/ML API">

```bash
AIMLAPI_API_KEY=${AIMLAPI_API_KEY} docker compose up -d
```

  </TabItem>
</Tabs>

You should see output like:

```
[+] Running 3/3
 ✔ Network dbgptnet              Created   0.0s
 ✔ Container db-gpt-db-1         Started   0.2s
 ✔ Container db-gpt-webserver-1  Started   0.2s
```

### Step 3 — Open the Web UI

Visit **[http://localhost:5670](http://localhost:5670)** in your browser.

:::warning First start may take a moment
The webserver waits for MySQL to finish initializing. If it fails on first start, it will auto-restart. Check logs with `docker logs db-gpt-webserver-1 -f`.
:::

## What gets deployed

The default `docker-compose.yml` creates:

| Service | Image | Port | Purpose |
|---|---|---|---|
| `db` | `mysql/mysql-server` | 3306 | MySQL database for metadata |
| `webserver` | `eosphorosai/dbgpt-openai:latest` | 5670 | DB-GPT application server |

## Common operations

### View logs

```bash
# Webserver logs
docker logs db-gpt-webserver-1 -f

# Database logs
docker logs db-gpt-db-1 -f
```

### Stop services

```bash
docker compose down
```

### Restart services

```bash
docker compose restart
```

### Reset everything (including data)

```bash
docker compose down -v
```

:::warning
The `-v` flag removes all volumes, including the MySQL database. All data will be lost.
:::

## Customization

### Use a different config file

Mount your own TOML config and override the startup command:

```yaml
webserver:
  image: eosphorosai/dbgpt-openai:latest
  command: dbgpt start webserver --config /app/configs/your-config.toml
  volumes:
    - ./your-config.toml:/app/configs/your-config.toml
```

### Mount local models

For GPU deployments, mount a local models directory:

```yaml
webserver:
  volumes:
    - /data/models:/app/models
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            capabilities: [gpu]
```

## Other Compose examples

DB-GPT ships with additional Compose files for specific scenarios:

| File | Use case |
|---|---|
| `docker-compose.yml` | Default proxy deployment with MySQL |
| `docker/compose_examples/cluster-docker-compose.yml` | Multi-worker cluster with GPU |
| `docker/compose_examples/ha-cluster-docker-compose.yml` | High-availability cluster |
| `docker/compose_examples/dbgpt-oceanbase-docker-compose.yml` | OceanBase database backend |

Example:

```bash
docker compose -f docker/compose_examples/cluster-docker-compose.yml up -d
```

## Next steps

| Topic | Link |
|---|---|
| Cluster deployment | [Cluster](/docs/getting-started/deploy/cluster) |
| Docker (single container) | [Docker](/docs/getting-started/deploy/docker) |
| Source code deployment | [Source Code](/docs/getting-started/deploy/source-code) |
