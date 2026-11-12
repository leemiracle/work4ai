---
sidebar_position: 2
title: dbgpts Ecosystem
---

# dbgpts Ecosystem

**[dbgpts](https://github.com/eosphoros-ai/dbgpts)** is the official community repository of reusable components for DB-GPT — including apps, AWEL operators, workflow templates, and agents.

## What's in dbgpts?

| Component Type | Description | Example |
|---|---|---|
| **Apps** | Complete applications ready to install | Data analysis app, report generator |
| **Operators** | AWEL operators for use in workflows | Text splitter, HTTP request, LLM call |
| **Workflow Templates** | Pre-built AWEL workflow DAGs | RAG pipeline, multi-agent chat |
| **Agents** | Pre-configured agent definitions | SQL analyst, code reviewer |

## Installation

The `dbgpts` CLI is included when you install DB-GPT with the `dbgpts` extra:

```bash
uv sync --all-packages --extra "dbgpts" ...
```

## CLI commands

### Browse available packages

```bash
# List all remote packages
dbgpts list-remote

# List installed packages
dbgpts list
```

### Install a package

```bash
dbgpts install <package-name>
```

### Update a package

```bash
dbgpts update <package-name>
```

### Uninstall a package

```bash
dbgpts uninstall <package-name>
```

## Using in the Web UI

Once installed, dbgpts components are automatically available in the Web UI:

- **Apps** appear in the App Store
- **Operators** appear in the AWEL Flow editor's operator palette
- **Workflow templates** can be imported into the Flow editor
- **Agents** can be selected when creating multi-agent apps

## Repository structure

The dbgpts repository is organized by component type:

```
dbgpts/
├── apps/           # Complete applications
├── operators/      # AWEL operators
├── workflow/       # Workflow templates
└── agents/         # Agent definitions
```

## Creating your own dbgpts package

You can contribute your own components to the ecosystem:

1. Follow the package structure in the [dbgpts repository](https://github.com/eosphoros-ai/dbgpts)
2. Include a `manifest.json` with metadata
3. Submit a pull request

:::info
For detailed development instructions, see the [dbgpts Introduction](/docs/dbgpts/introduction).
:::

## Next steps

| Topic | Link |
|---|---|
| Build AWEL workflows | [AWEL Flow](/docs/getting-started/tools/awel-flow) |
| MCP tools integration | [MCP Protocol](/docs/getting-started/tools/mcp) |
| dbgpts development | [dbgpts Introduction](/docs/dbgpts/introduction) |
