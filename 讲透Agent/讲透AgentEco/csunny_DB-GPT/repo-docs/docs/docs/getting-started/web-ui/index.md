---
sidebar_position: 0
title: Web UI Overview
summary: "What is available in the DB-GPT Web UI and where each main feature lives"
read_when:
  - You already started DB-GPT and want to know what to click first
  - You want a quick map of chat, knowledge, dashboard, and app screens
---

# Web UI Overview

DB-GPT ships with a web interface at **[http://localhost:5670](http://localhost:5670)**.

## Main areas

- [Chat](/docs/getting-started/web-ui/chat) — normal chat, data chat, Excel chat, knowledge chat
- [Knowledge Base](/docs/getting-started/web-ui/knowledge-base) — upload files and build RAG datasets
- [Dashboard](/docs/getting-started/web-ui/dashboard) — generate charts and reports from natural language
- [App Management](/docs/getting-started/web-ui/app-management) — create and manage DB-GPT applications

## Feature map

| Feature | Description | Section |
|---|---|---|
| **Chat** | Multi-turn conversation with LLMs | [Chat](/docs/getting-started/web-ui/chat) |
| **Chat Data** | Natural language queries on connected databases (Text2SQL) | [Chat](/docs/getting-started/web-ui/chat) |
| **Chat Excel** | Upload and query Excel files with natural language | [Chat](/docs/getting-started/web-ui/chat) |
| **Chat Knowledge** | RAG conversations over your uploaded documents | [Knowledge Base](/docs/getting-started/web-ui/knowledge-base) |
| **Dashboard** | Auto-generated charts and reports from data | [Dashboard](/docs/getting-started/web-ui/dashboard) |
| **App Store** | Browse and install community applications | [App Management](/docs/getting-started/web-ui/app-management) |
| **AWEL Flow** | Visual workflow editor for building AI pipelines | [AWEL Flow](/docs/getting-started/tools/awel-flow) |
| **Agent Workspace** | Configure and run multi-agent tasks | [App Management](/docs/getting-started/web-ui/app-management) |

## Accessing the Web UI

After starting the DB-GPT server, the Web UI is available at:

```
http://localhost:5670
```

:::tip Running the front-end separately
For front-end development, you can run the Next.js app independently:

```bash
cd web && npm install
cp .env.template .env
# Set API_BASE_URL=http://localhost:5670
npm run dev
```

Then visit [http://localhost:3000](http://localhost:3000).
:::

## What to try first

1. Open **Chat** and confirm the configured model responds
2. Open **Knowledge Base** if you want RAG over documents
3. Open **Dashboard** if you want Text2SQL and charts
4. Open **Apps** if you want reusable app configurations

## Next steps

| Topic | Link |
|---|---|
| Start chatting | [Chat](/docs/getting-started/web-ui/chat) |
| Set up knowledge base | [Knowledge Base](/docs/getting-started/web-ui/knowledge-base) |
| Build workflows | [AWEL Flow](/docs/getting-started/tools/awel-flow) |
