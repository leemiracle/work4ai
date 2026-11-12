<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/bux · page 2 Installation and Deployment · fetched 2026-10-30 -->

# Installation and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [install.md](install.md)
- [install.sh](install.sh)

</details>



This page provides a high-level overview of how to deploy **bux** to a persistent Linux environment. The deployment process transforms a fresh Ubuntu/Debian instance into a 24/7 autonomous agent capable of driving a cloud-hosted Chromium session via Claude Code.

## Quick Start: The One-Liner

For most users, installation is a single command executed as `root`. This script handles dependency resolution, user creation, and service registration.

```bash
curl -fsSL https://raw.githubusercontent.com/browser-use/bux/main/install.sh \
  | sudo BROWSER_USE_API_KEY=bu_xxx TG_BOT_TOKEN=123:abc bash
```
[install.md:5-11]()

## Deployment Prerequisites

Before running the installer, you need the following credentials and infrastructure:

| Requirement | Source | Purpose |
|:---|:---|:---|
| **Linux Box** | VPS (Hetzner, DO) or Home Lab | Runs the agent logic and systemd services. [install.md:19-33]() |
| **Browser Use API Key** | [Browser Use Cloud](https://cloud.browser-use.com) | Provides the remote Chromium instance via CDP. [install.md:37-38]() |
| **Telegram Bot Token** | [@BotFather](https://t.me/BotFather) | (Optional) Interface for remote commanding. [install.md:39-47]() |

For a detailed step-by-step walkthrough, see the [Installation Guide](#2.1).

## The `install.sh` Workflow

The `install.sh` script is designed to be **idempotent**, meaning it can be safely re-run to update the system or fix broken configurations without duplicating resources [install.sh:16-17]().

### Natural Language to Code Entity Space: Installation

The following diagram maps the installation steps to the specific code entities and filesystem locations they create.

```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Install Dependencies'"]
        B["'Create Service User'"]
        C["'Setup Services'"]
    end

    subgraph "Code Entity Space"
        A --> |"apt-get / npm"| D["/usr/local/bin/uv"]
        A --> |"npm -g"| E["claude-code"]
        B --> |"useradd"| F["bux user"]
        B --> |"mkdir"| G["/opt/bux/"]
        C --> |"cp"| H["bux-tg.service"]
        C --> |"cp"| I["bux-browser-keeper.service"]
    end

    D -.- [install.sh:118-119]
    E -.- [install.sh:143-143]
    F -.- [install.sh:147-147]
    H -.- [install.sh:220-220]
```
Sources: [install.sh:118-119](), [install.sh:143-143](), [install.sh:147-147](), [install.sh:220-220]()

For a deep dive into the environment variables and system hardening performed by this script, see the [install.sh Reference](#2.2).

## Provider Options

While bux is designed to be provider-agnostic, specific "recipes" exist to optimize deployment for different environments. The goal is to go from a "blank box to Claude" in under 5 minutes.

*   **VPS Providers:** Optimized for Hetzner CX11 or DigitalOcean $6 droplets [install.md:24-25]().
*   **Home Lab:** Support for Raspberry Pi and Mac mini (Asahi Linux) via Tailscale tunnels [install.md:29-30]().
*   **Managed:** Auto-provisioning via Browser Use Cloud AMI baking [install.md:27-27]().

For specific configuration files and provider-specific quirks, see [Provider Deploy Recipes](#2.3).

## Post-Installation Lifecycle

Once the script completes, the system enters a "First Run" state requiring human intervention for OAuth.

### Natural Language to Code Entity Space: Runtime Initialization

This diagram shows the relationship between the human-in-the-loop setup and the underlying system state.

```mermaid
graph LR
    subgraph "Human Actions"
        Step1["'Run /login in Claude'"]
        Step2["'Message the TG Bot'"]
    end

    subgraph "System State"
        State1["~/.claude/config.json"]
        State2["/etc/bux/tg-allowed.txt"]
    end

    Step1 --> |"OAuth Flow"| State1
    Step2 --> |"First Message Wins"| State2

    State1 -.- [install.md:72-77]
    State2 -.- [install.md:79-82]
```
Sources: [install.md:72-77](), [install.md:79-82]()

1.  **Claude OAuth:** The user must manually run `sudo -iu bux claude` and perform a one-time `/login` to authorize the Anthropic account [install.md:72-77]().
2.  **Telegram Binding:** The first person to message the bot becomes the "owner," and their `chat_id` is persisted to disk, locking out all other users [install.md:79-82]().

For troubleshooting common deployment failures (e.g., `browser.env` missing), refer to the troubleshooting section in the [Installation Guide](#2.1).

---

