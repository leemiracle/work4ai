---
sidebar_position: 0
title: Troubleshooting
summary: "First checks and common fixes for install, model, and environment issues"
read_when:
  - Something broke and you want the fastest fix path
  - DB-GPT starts inconsistently, the UI is blank, or models fail to load
---

# Troubleshooting

Common issues and solutions when working with DB-GPT.

## First 60 seconds

Run these first:

```bash
curl http://localhost:5670/api/health
dbgpt model list
docker logs dbgpt -f
```

If you are not using Docker, check the same terminal where you started the webserver.

## Common quick fixes

- **Server will not start**
  - Re-run `uv sync` with the right extras
  - See [Installation Issues](/docs/getting-started/troubleshooting/installation)
- **Web UI is blank**
  - Wait for startup to finish
  - Confirm the server is reachable on `http://localhost:5670`
- **Model not found / auth error**
  - Re-check the TOML config and provider name
  - See [Model Issues](/docs/getting-started/troubleshooting/llm)
- **Port 5670 is already in use**
  - Find the conflicting process with `lsof -i :5670`
- **Out of memory**
  - Use a smaller local model or switch to an API proxy model

## More specific guides

- [Installation Issues](/docs/getting-started/troubleshooting/installation)
- [Model Issues](/docs/getting-started/troubleshooting/llm)
- [Environment Variables](/docs/getting-started/troubleshooting/environment)

## Logs

```bash
# Source code deployment
# Logs are printed to stdout by default

# Docker deployment
docker logs dbgpt -f

# Docker Compose deployment
docker logs db-gpt-webserver-1 -f
```

## Getting help

If the troubleshooting guides don't resolve your issue:

1. **Search existing issues**: [GitHub Issues](https://github.com/eosphoros-ai/DB-GPT/issues)
2. **Ask the community**: [GitHub Discussions](https://github.com/orgs/eosphoros-ai/discussions)
3. **Join Slack**: [DB-GPT Slack](https://join.slack.com/t/slack-inu2564/shared_invite/zt-29rcnyw2b-N~ubOD9kFc7b7MDOAM1otA)
4. **Check FAQ**: [Installation FAQ](/docs/faq/install) · [LLM FAQ](/docs/faq/llm) · [KBQA FAQ](/docs/faq/kbqa)
