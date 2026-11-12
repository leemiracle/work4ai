---
sidebar_position: 4
title: App Management
---

# App Management

Create, configure, and manage AI applications in DB-GPT. Apps combine LLMs, tools, knowledge bases, and workflows into reusable configurations.

## App types

| Type | Description |
|---|---|
| **Native App** | Built-in applications included with DB-GPT |
| **Community App** | Apps from the dbgpts community repository |
| **Custom App** | Your own applications built with agents and AWEL |

## Browsing apps

### App Store

1. Click **Apps** in the sidebar
2. Browse available applications
3. Click an app to see its details, including description, required resources, and configuration

### Installed apps

The **My Apps** tab shows applications you have installed or created.

## Creating an app

### Step 1 — Define the app

1. Navigate to **Apps** → **Create**
2. Fill in:
   - **Name** — Display name for the app
   - **Description** — What the app does
   - **Language** — Natural language for prompts (e.g., English, Chinese)

### Step 2 — Configure resources

Add resources the app needs:

- **LLM** — Select the language model
- **Knowledge Base** — Attach one or more knowledge bases for RAG
- **Database** — Connect data sources for Text2SQL
- **Tools** — Add external tools (MCP tools, custom functions)

### Step 3 — Set up agents

For multi-agent applications:

1. Choose an agent team mode:
   - **Single Agent** — One agent handles all tasks
   - **Auto-Plan** — Agents collaborate with automatic task planning
   - **Sequential** — Agents execute in a fixed order

2. Configure each agent:
   - **Role** — Agent's persona and expertise
   - **Prompt** — System instructions
   - **Resources** — Which tools and data the agent can access

### Step 4 — Test and deploy

1. Click **Save** to save the configuration
2. Use **Test** to try the app in a sandbox
3. The app appears in your **My Apps** list for use

## Managing apps

| Action | How |
|---|---|
| **Edit** | Click the edit icon on any app card |
| **Delete** | Click the delete icon (only for custom apps) |
| **Share** | Export app configuration for sharing |
| **Duplicate** | Create a copy of an existing app as a starting point |

## AWEL Flow integration

Apps can use AWEL workflows as their execution engine:

1. Create a workflow in the **Flow** editor
2. When creating an app, select the AWEL flow as the app's backend
3. The app UI automatically maps to the flow's inputs and outputs

See [AWEL Flow](/docs/getting-started/tools/awel-flow) for details on building workflows.

## Community apps (dbgpts)

Install community-contributed apps using the `dbgpts` CLI:

```bash
# List available apps
dbgpts list-remote

# Install an app
dbgpts install <app-name>
```

:::info
Community apps are maintained in the [dbgpts repository](https://github.com/eosphoros-ai/dbgpts). See [dbgpts](/docs/getting-started/tools/dbgpts) for more details.
:::

## Next steps

| Topic | Link |
|---|---|
| Build workflows | [AWEL Flow](/docs/getting-started/tools/awel-flow) |
| Explore agents | [Agents Concept](/docs/getting-started/concepts/agents) |
| Community apps | [dbgpts](/docs/getting-started/tools/dbgpts) |
| App development guide | [App Development](/docs/cookbook/app/data_analysis_app_develop) |
