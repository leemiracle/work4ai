---
sidebar_position: 3
title: Environment Variables
---

# Environment Variables

Reference for commonly used environment variables in DB-GPT.

:::tip
Most configuration is done through TOML config files. Environment variables are useful for secrets, Docker deployments, and overriding defaults.
:::

## Model configuration

| Variable | Description | Example |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_API_BASE` | OpenAI-compatible API base URL | `https://api.openai.com/v1` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | `sk-...` |
| `SILICONFLOW_API_KEY` | SiliconFlow API key | `sk-...` |
| `DASHSCOPE_API_KEY` | Alibaba Cloud DashScope API key | `sk-...` |
| `AIMLAPI_API_KEY` | AI/ML API key | — |
| `LLM_MODEL` | Default LLM model name (cluster mode) | `glm-4-9b-chat` |
| `MODEL_SERVER` | Model controller address (cluster mode) | `http://127.0.0.1:8000` |

## Server configuration

| Variable | Description | Default |
|---|---|---|
| `DBGPT_LOG_LEVEL` | Logging level | `INFO` |
| `LOCAL_DB_TYPE` | Metadata database type | `sqlite` |
| `LOCAL_DB_PATH` | SQLite database path | `data/default_sqlite.db` |
| `MYSQL_HOST` | MySQL host | `127.0.0.1` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | — |
| `MYSQL_DATABASE` | MySQL database name | `dbgpt` |

## GPU and hardware

| Variable | Description | Example |
|---|---|---|
| `CUDA_VISIBLE_DEVICES` | Restrict which GPUs are visible | `0,1` |
| `DEVICE` | Force device type | `cuda`, `cpu`, `mps` |

## Network and proxy

| Variable | Description | Example |
|---|---|---|
| `UV_INDEX_URL` | PyPI mirror for uv | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| `HTTP_PROXY` | HTTP proxy for outbound requests | `http://proxy:8080` |
| `HTTPS_PROXY` | HTTPS proxy for outbound requests | `http://proxy:8080` |
| `NO_PROXY` | Hosts to bypass proxy | `localhost,127.0.0.1` |

## Using environment variables in TOML configs

DB-GPT supports environment variable substitution in TOML config files:

```toml
[[models.llms]]
api_key = "${env:OPENAI_API_KEY}"

[[models.embeddings]]
api_key = "${env:OPENAI_API_KEY:-default-key}"
```

**Syntax:**

| Pattern | Behavior |
|---|---|
| `${env:VAR_NAME}` | Read from environment variable (error if missing) |
| `${env:VAR_NAME:-default}` | Read from environment, use `default` if not set |

## Docker environment variables

When running with Docker, pass environment variables with `-e`:

```bash
docker run -it --rm \
  -e SILICONFLOW_API_KEY=your-key \
  -e DBGPT_LOG_LEVEL=DEBUG \
  -p 5670:5670 \
  eosphorosai/dbgpt-openai
```

Or with Docker Compose in `docker-compose.yml`:

```yaml
services:
  webserver:
    environment:
      - SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY}
      - DBGPT_LOG_LEVEL=INFO
```

## Next steps

| Topic | Link |
|---|---|
| Full config reference | [Config Reference](/docs/config/config-reference) |
| Model providers | [Providers](/docs/getting-started/providers/) |
| Troubleshooting index | [Troubleshooting](/docs/getting-started/troubleshooting/) |
