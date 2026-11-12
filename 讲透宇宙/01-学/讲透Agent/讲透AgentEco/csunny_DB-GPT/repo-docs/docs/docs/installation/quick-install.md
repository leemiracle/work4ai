---
sidebar_position: 1
title: Quick Install
summary: "The fastest way to install DB-GPT with the installer script from the README"
read_when:
  - You want the shortest path to a working DB-GPT web UI
  - You prefer the installer script over a manual source setup
---

import CommandCopyCard from "@site/src/components/mdx/CommandCopyCard";

# Quick Install

The fastest way to get DB-GPT running. The installer script prepares a local DB-GPT workspace, generates a provider profile, and gives you a ready-to-run webserver command.

## Recommended: installer script

Use the installer script if you want the shortest path from zero to a working DB-GPT web UI.

<CommandCopyCard command={`curl -fsSL https://raw.githubusercontent.com/eosphoros-ai/DB-GPT/main/scripts/install/install.sh | bash`} />

## System requirements

This quick-install flow is designed for:

- **macOS** or **Linux**
- a shell environment that can run `bash`
- network access to download dependencies
- an API key if you plan to use a hosted model provider immediately

:::tip Best fit
Choose this path if you want to try DB-GPT quickly without managing the repository structure yourself.
:::

## Install with a provider profile

If you already know which provider you want, pass the profile and API key directly during installation.

### OpenAI-compatible profile

<CommandCopyCard command={`curl -fsSL https://raw.githubusercontent.com/eosphoros-ai/DB-GPT/main/scripts/install/install.sh \
  | OPENAI_API_KEY=sk-xxx bash -s -- --profile openai`} />

### Kimi 2.5 via Moonshot API

<CommandCopyCard command={`curl -fsSL https://raw.githubusercontent.com/eosphoros-ai/DB-GPT/main/scripts/install/install.sh \
  | MOONSHOT_API_KEY=sk-xxx bash -s -- --profile kimi`} />

### MiniMax via an OpenAI-compatible API

<CommandCopyCard command={`curl -fsSL https://raw.githubusercontent.com/eosphoros-ai/DB-GPT/main/scripts/install/install.sh \
  | MINIMAX_API_KEY=sk-xxx bash -s -- --profile minimax`} />

## Reuse an existing local checkout

Already have a local DB-GPT repository? Reuse it instead of cloning into `~/.dbgpt/DB-GPT`.

### Reuse local repo with OpenAI

<CommandCopyCard command={`OPENAI_API_KEY=sk-xxx \
  bash scripts/install/install.sh --profile openai --repo-dir "$(pwd)" --yes`} />

### Reuse local repo with Kimi

<CommandCopyCard command={`MOONSHOT_API_KEY=sk-xxx \
  bash scripts/install/install.sh --profile kimi --repo-dir "$(pwd)" --yes`} />

### Reuse local repo with MiniMax

<CommandCopyCard command={`MINIMAX_API_KEY=sk-xxx \
  bash scripts/install/install.sh --profile minimax --repo-dir "$(pwd)" --yes`} />

## What the installer prepares

The installer script sets up the common runtime layout for you:

- a DB-GPT checkout under `~/.dbgpt/DB-GPT` unless `--repo-dir` is used
- generated provider configs under `~/.dbgpt/configs/`
- the DB-GPT home directory under `~/.dbgpt/`
- a ready-to-run webserver command using the generated profile

## Start DB-GPT after installation

After installation completes, start the webserver with the generated profile config:

<CommandCopyCard command={`cd ~/.dbgpt/DB-GPT && uv run dbgpt start webserver --profile <profile>`} />

Then open [http://localhost:5670](http://localhost:5670).

## Verify the install

Your install is working if:

- the webserver starts without configuration errors
- the Web UI opens at `http://localhost:5670`
- you can start a chat in the browser

## Review the script first

If you prefer to inspect the installer before running it:

```bash
curl -fsSL https://raw.githubusercontent.com/eosphoros-ai/DB-GPT/main/scripts/install/install.sh -o install.sh
less install.sh
bash install.sh --profile openai
```

## Alternative install methods

If the installer script is not the right fit for your environment:

- use [CLI Install](/docs/getting-started/cli-quickstart) for a PyPI-based install with the `dbgpt` command
- use [Source Install](/docs/getting-started/deploy/source-code) for development, debugging, and customization

## Troubleshooting

### The installer script does not match my shell or platform

Use [CLI Install](/docs/getting-started/cli-quickstart) or [Source Install](/docs/getting-started/deploy/source-code) instead.

### I want more control over dependencies and configuration

Use [Source Install](/docs/getting-started/deploy/source-code). It exposes the full repository layout and `uv sync` workflow.

### The install completed, but DB-GPT does not start cleanly

Check the generated config under `~/.dbgpt/configs/`, then see [Installation Issues](/docs/getting-started/troubleshooting/installation).
