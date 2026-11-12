# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [agent_reach/__init__.py](agent_reach/__init__.py)
- [docs/README_en.md](docs/README_en.md)
- [docs/wechat-group-qr.jpg](docs/wechat-group-qr.jpg)
- [pyproject.toml](pyproject.toml)

</details>



This page covers what Agent Reach is, the problem it solves, its core design philosophy, and the top-level structure of the codebase. For installation steps, see [Getting Started](#1.2). For the internal module architecture, see [Architecture](#1.1).

---

## What Is Agent Reach?

Agent Reach is a Python CLI package (`agent-reach`) that gives AI agents (Claude Code, Cursor, OpenClaw, Windsurf, etc.) structured access to internet content across a set of platforms. It exposes a single, consistent shell interface that agents can call without any per-platform API keys or paid subscriptions [pyproject.toml:1-17]().

The core problem it addresses: each platform on the internet has different access barriers — paid APIs, IP-based blocking, login walls, anti-scraping measures. Without Agent Reach, an agent operator must find the right tool for each platform, install it, configure it, and handle errors [README.md:58-75](). Agent Reach pre-selects, wires, and manages those tools so that a single command like `agent-reach read <url>` or `agent-reach search-twitter "query"` works regardless of the underlying platform [docs/README_en.md:60-81]().

The package is explicitly designed as a **glue layer**: it makes tool selection and configuration decisions on behalf of the operator, but every backend is swappable by changing a single channel file [CLAUDE.md:37-39]().

Sources: [README.md:58-75](), [docs/README_en.md:60-81](), [CLAUDE.md:3-6](), [CLAUDE.md:37-39](), [pyproject.toml:1-17]()

---

## Design Philosophy

| Principle | Implementation |
|-----------|---------------|
| **Zero mandatory API fees** | Every default backend is free: Jina Reader, `bird` CLI, `yt-dlp`, `feedparser`, `gh` CLI, `bili-cli`, Exa via `mcporter` [README.md:92-101]() |
| **Pluggable channels** | Each platform is an independent Python file in `agent_reach/channels/` inheriting from `BaseChannel` [CLAUDE.md:29-32]() |
| **Swappable backends** | The channel file is the only thing that changes if a better backend emerges (e.g., Bilibili switching from `yt-dlp` to `bili-cli`) [README.md:98-98]() |
| **AI agent first** | The primary consumer is an AI agent reading `SKILL.md` and issuing shell commands [README.md:147-153]() |
| **Credential locality** | Cookies and tokens are stored only in `~/.agent-reach/config.yaml` with restricted permissions [README.md:126-131]() |
| **Tiered setup** | Channels are classified by setup complexity (zero-config, needs credentials, needs setup) [README.md:104-123]() |

Sources: [README.md:92-101](), [CLAUDE.md:29-32](), [README.md:147-153](), [README.md:126-131](), [README.md:104-123]()

---

## Supported Platforms

Agent Reach supports a wide range of global and Chinese-specific platforms, categorized by their setup requirements.

| Platform | Backend | Tier | Read | Search |
|----------|---------|------|------|--------|
| Any web URL | Jina Reader (`r.jina.ai`) | 0 — zero config | ✅ | — |
| YouTube | `yt-dlp` | 0 — zero config | ✅ | ✅ |
| RSS / Atom | `feedparser` | 0 — zero config | ✅ | — |
| GitHub | `gh` CLI | 0 — zero config (public) | ✅ | ✅ |
| V2EX | Public JSON API | 0 — zero config | ✅ | ✅ |
| Xueqiu (雪球) | Public JSON API | 0 — zero config | ✅ | ✅ |
| Twitter / X | `bird` CLI | 0/1 — cookies unlock search | ✅ | ✅ |
| Bilibili | `bili-cli` | 0/1 — proxy for servers | ✅ | ✅ |
| Reddit | `rdt-cli` | 1 — login required | ✅ | ✅ |
| Facebook | `OpenCLI` | 1 — browser session | ✅ | ✅ |
| Instagram | `OpenCLI` | 1 — browser session | ✅ | ✅ |
| LinkedIn | `mcporter` → `mcp-server-linkedin` | 2 — MCP setup | ✅ | ✅ |
| XiaoHongShu | `mcporter` → `xiaohongshu-mcp` | 2 — MCP + cookies | ✅ | ✅ |
| Xiaoyuzhou | Groq Whisper | 2 — Free API Key | ✅ | — |

Sources: [README.md:104-123](), [docs/README_en.md:101-107](), [CLAUDE.md:3-6]()

---

## System Components

**Top-level flow from user to platform:**

```mermaid
flowchart TD
    User["User / Developer"]
    Agent["AI Agent\n(Claude Code, Cursor, etc.)"]
    SKILL["agent_reach/skill/SKILL.md"]
    CLI["agent_reach/cli.py\nmain()"]
    Core["agent_reach/core.py\nAgentReach"]
    Registry["agent_reach/channels/__init__.py\nALL_CHANNELS / SEARCH_CHANNELS"]
    Channel["agent_reach/channels/base.py\nBaseChannel (abstract)"]
    Backend["External Backend\n(bird, yt-dlp, gh, bili-cli, rdt-cli, mcporter, OpenCLI)"]
    Platform["External Platform\n(Twitter, YouTube, GitHub, Reddit, Bilibili, ...)"]

    User -->|"natural language"| Agent
    Agent -->|"reads skills"| SKILL
    SKILL -->|"shell command"| CLI
    CLI -->|"delegates"| Core
    Core -->|"URL routing"| Registry
    Registry -->|"selects"| Channel
    Channel -->|"subprocess / HTTP / Python lib"| Backend
    Backend -->|"API / scrape"| Platform
```

Sources: [README.md:147-153](), [CLAUDE.md:16-25](), [agent_reach/cli.py:53-53](), [agent_reach/core.py:7-7]()

---

**Core Python package modules and their responsibilities:**

```mermaid
graph LR
    subgraph entry["Entrypoints"]
        console["console_scripts:\nagent-reach"]
        pyapi["import agent_reach"]
    end

    subgraph cli["agent_reach/cli.py"]
        main["main()"]
        cmd_read["_cmd_read()"]
        cmd_search["_cmd_search()"]
        cmd_install["_cmd_install()"]
        cmd_configure["_cmd_configure()"]
        cmd_doctor["_cmd_doctor()"]
    end

    subgraph core["agent_reach/core.py"]
        AR["AgentReach\nread() / search_*() / doctor()"]
    end

    subgraph config["agent_reach/config.py"]
        CFG["Config\nget() / set() / is_configured()\n~/.agent-reach/config.yaml"]
    end

    subgraph doctor["agent_reach/doctor.py"]
        DOC["check_all()\nformat_report()"]
    end

    subgraph registry["agent_reach/channels/__init__.py"]
        ALL["ALL_CHANNELS list"]
        SEARCH["SEARCH_CHANNELS dict"]
    end

    subgraph base["agent_reach/channels/base.py"]
        BASE["BaseChannel (abstract)\ncan_handle() / check() / read() / search()"]
    end

    console --> main
    pyapi --> AR
    main --> cmd_read & cmd_search & cmd_install & cmd_configure & cmd_doctor
    cmd_read & cmd_search --> AR
    cmd_doctor --> DOC
    cmd_install & cmd_configure --> CFG
    AR --> CFG
    AR --> ALL & SEARCH
    DOC --> ALL
    ALL & SEARCH --> BASE
```

Sources: [pyproject.toml:52-53](), [agent_reach/__init__.py:7-9](), [CLAUDE.md:16-25](), [agent_reach/core.py:7-7]()

---

## Channel Tier Classification

Channels are classified into three tiers based on what is required before they function:

| Tier | Label | What's Required | Examples |
|------|-------|----------------|---------|
| 0 | Zero config | Nothing beyond `pip install agent-reach` | `web.py`, `youtube.py`, `rss.py`, `github.py` (public) |
| 1 | Needs credential or proxy | Browser cookies or a residential proxy | `twitter.py` (search), `bilibili.py` (server), `reddit.py` |
| 2 | Needs MCP service or full setup | Docker, `mcporter`, API keys | `xiaohongshu.py`, `linkedin.py`, `xiaoyuzhou.py` |

The `agent-reach doctor` command reports each channel's status (`ok` / `warn` / `off`) based on its tier and current configuration [README.md:100-101](). See [Diagnostics and Monitoring](#2.5) for details.

Sources: [README.md:104-123](), [docs/README_en.md:101-107](), [CLAUDE.md:5-5]()

---

## What's in the Repository

```
agent_reach/
├── cli.py              # CLI entrypoint, argument parsing, subcommand dispatch
├── core.py             # AgentReach class — primary programmatic API
├── config.py           # Config management (YAML, env vars)
├── doctor.py           # Diagnostics engine — channel health checks
├── channels/           # One file per platform
│   ├── __init__.py     # Channel registry and routing
│   ├── base.py         # BaseChannel abstract base class
│   ├── twitter.py      # TwitterChannel — bird CLI backend
│   ├── youtube.py      # YouTubeChannel — yt-dlp backend
│   ├── bilibili.py     # BilibiliChannel — bili-cli backend
│   ├── github.py       # GitHubChannel — gh CLI backend
│   ├── reddit.py       # RedditChannel — rdt-cli backend
│   ├── xhs.py          # XiaoHongShuChannel — mcporter backend
│   └── ...             # Other platform channels
├── integrations/
│   └── mcp_server.py   # MCP server implementation
├── skill/
│   └── SKILL.md        # AI agent skill definition file
└── guides/             # Usage and configuration guides
```

Sources: [CLAUDE.md:16-27](), [pyproject.toml:64-65]()

---

## Related Pages

| Topic | Page |
|-------|------|
| End-to-end architecture, channel routing, and tier levels | [Architecture](#1.1) |
| Installation, `agent-reach install`, and verification | [Getting Started](#1.2) |
| All CLI subcommands, search commands, and diagnostics | [CLI Reference](#2) |
| Channel abstract base class and platform-specific docs | [Channels](#3) |
| `Config` class, `config.yaml`, and proxy management | [Configuration](#4) |
| `SKILL.md` registration and AI agent integration | [AI Agent Integration](#5) |
| Development conventions, testing, and upstream sync | [Development](#6) |

---

# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [agent_reach/__init__.py](agent_reach/__init__.py)
- [agent_reach/channels/__init__.py](agent_reach/channels/__init__.py)
- [agent_reach/channels/base.py](agent_reach/channels/base.py)
- [agent_reach/channels/instagram.py](agent_reach/channels/instagram.py)
- [agent_reach/channels/rss.py](agent_reach/channels/rss.py)
- [agent_reach/probe.py](agent_reach/probe.py)
- [docs/wechat-group-qr.jpg](docs/wechat-group-qr.jpg)
- [pyproject.toml](pyproject.toml)
- [tests/test_channel_contracts.py](tests/test_channel_contracts.py)
- [tests/test_probe.py](tests/test_probe.py)

</details>



This page describes Agent Reach's internal architecture: how the `AgentReach` class, channel registry, URL dispatch, tier classification, and result types fit together as a system. For installation and first-use, see [Getting Started](#1.2). For per-channel details, see [Channels](#3).

---

## Overview

Agent Reach is a thin routing layer. Its job is to accept a URL or search query, dispatch it to the correct platform-specific channel, and return a normalized result. No channel knows about any other channel. The core has no platform logic of its own.

**Key design properties:**

- Each platform is one Python file (`agent_reach/channels/*.py`) implementing a shared abstract interface [agent_reach/channels/base.py:29-70]().
- URL dispatch is done by iterating an ordered list (`ALL_CHANNELS`) until a `can_handle()` match is found [agent_reach/channels/__init__.py:26-42]().
- The backend tool used by any channel can be changed or reordered via configuration without touching any other part of the system [agent_reach/channels/base.py:45-59]().

---

## Package Structure

**Diagram: Module Dependencies**

```mermaid
graph LR
    entrypoint["agent-reach\n(console_scripts)"] --> main["cli.py: main()"]
    pyapi["import agent_reach"] --> AgentReach["core.py: AgentReach"]

    main --> AgentReach
    AgentReach --> Config["config.py: Config"]
    AgentReach --> registry["channels/__init__.py\nget_channel()\nget_all_channels()"]
    AgentReach -.->|"lazy import"| doctor["doctor.py\ncheck_all()\nformat_report()"]

    registry --> ALL_CHANNELS["ALL_CHANNELS: List[Channel]"]
    ALL_CHANNELS --> base["channels/base.py: Channel (ABC)"]

    doctor --> registry
```

Sources: [agent_reach/core.py:7](), [agent_reach/channels/__init__.py:26-63](), [agent_reach/channels/base.py:29-70](), [pyproject.toml:52-53]()

---

## The `AgentReach` Class

`AgentReach` in [agent_reach/core.py:7]() is the primary health-check and configuration entry point. It holds a `Config` instance and provides methods to audit the system's readiness.

| Method | Delegates to | Notes |
|---|---|---|
| `__init__(config)` | `Config()` | Initializes configuration. |
| `doctor()` | `check_all(self.config)` | Returns `Dict[str, dict]` of channel statuses. |
| `doctor_report()` | `format_report(...)` | Human-readable string for the agent. |

For reading and searching, Agent Reach encourages agents to use the upstream tools directly as defined in the system's `SKILL.md`.

Sources: [agent_reach/core.py:7](), [CLAUDE.md:16-28]()

---

## Channel Registry and URL Routing

**Diagram: ALL_CHANNELS dispatch (class names to channel names)**

```mermaid
graph TD
    url["Input URL"] --> loop["Iterate ALL_CHANNELS\nin order"]
    loop --> can_handle["channel.can_handle(url)?"]
    can_handle -->|"No"| next["next channel"]
    next --> can_handle
    can_handle -->|"Yes"| dispatch["Dispatch to Channel Logic"]

    subgraph "ALL_CHANNELS (ordered)"
        ch1["GitHubChannel\nname='github'"]
        ch2["TwitterChannel\nname='twitter'"]
        ch3["YouTubeChannel\nname='youtube'"]
        ch4["RedditChannel\nname='reddit'"]
        ch5["FacebookChannel\nname='facebook'"]
        ch6["InstagramChannel\nname='instagram'"]
        ch7["BilibiliChannel\nname='bilibili'"]
        ch8["XiaoHongShuChannel\nname='xiaohongshu'"]
        ch9["LinkedInChannel\nname='linkedin'"]
        ch10["XiaoyuzhouChannel\nname='xiaoyuzhou'"]
        ch11["V2EXChannel\nname='v2ex'"]
        ch12["XueqiuChannel\nname='xueqiu'"]
        ch13["RSSChannel\nname='rss'"]
        ch14["ExaSearchChannel\nname='exa_search'"]
        ch15["WebChannel\nname='web'\n(fallback)"]
    end
```

The registry is defined in [agent_reach/channels/__init__.py:26-42](). The list is strictly ordered: **first match wins**. `WebChannel` is positioned last because it acts as the universal fallback.

### Registry Access Functions

| Function | Purpose |
|---|---|
| `get_channel(name)` | Looks up a channel by its `name` attribute [agent_reach/channels/__init__.py:45-50]() |
| `get_all_channels()` | Returns the full `ALL_CHANNELS` list [agent_reach/channels/__init__.py:53-55]() |

Sources: [agent_reach/channels/__init__.py:26-63](), [tests/test_channel_contracts.py:15-26]()

---

## The `Channel` Abstract Base Class

Every channel inherits from `Channel` in [agent_reach/channels/base.py:29-70](). The class defines the contract for platform detection and health auditing.

**Diagram: Channel ABC and its implementors**

```mermaid
classDiagram
    class Channel {
        <<abstract>>
        +str name
        +str description
        +List backends
        +int tier
        +str active_backend
        +can_handle(url) bool*
        +ordered_backends(config) List
        +check(config) Tuple
    }

    GitHubChannel --|> Channel
    TwitterChannel --|> Channel
    YouTubeChannel --|> Channel
    RedditChannel --|> Channel
    BilibiliChannel --|> Channel
    RSSChannel --|> Channel
    WebChannel --|> Channel
    InstagramChannel --|> OpenCLISiteChannel
    OpenCLISiteChannel --|> Channel
```

### Core Interface

- `can_handle(url) → bool` — Returns `True` if this channel owns this URL pattern. Must be implemented by subclasses [agent_reach/channels/base.py:40-43]().
- `check(config) → (status, message)` — Probes upstream tools and sets `self.active_backend`. Subclasses should use `probe_command` for accurate health reporting [agent_reach/channels/base.py:61-70]().
- `ordered_backends(config) → List[str]` — Returns candidate backends, moving user-configured overrides to the front [agent_reach/channels/base.py:45-59]().

### Attributes

| Attribute | Type | Purpose |
|---|---|---|
| `name` | `str` | Unique identifier (e.g., `"github"`) [agent_reach/channels/base.py:32]() |
| `description` | `str` | Human-readable platform description [agent_reach/channels/base.py:33]() |
| `backends` | `List[str]` | Names of external tools used (e.g., `["gh"]`) [agent_reach/channels/base.py:34]() |
| `tier` | `int` | Setup complexity (0=zero-config, 1=needs key, 2=needs setup) [agent_reach/channels/base.py:35]() |
| `active_backend`| `Optional[str]` | The specific tool currently serving the channel [agent_reach/channels/base.py:38]() |

Sources: [agent_reach/channels/base.py:29-70](), [tests/test_channel_contracts.py:39-46]()

---

## Tier Classification

The `tier` integer on each `Channel` subclass categorizes how much setup is required [agent_reach/channels/base.py:35]().

| Tier | Meaning | Example channels |
|---|---|---|
| `0` | Zero-config — works after `pip install` | `RSSChannel` [agent_reach/channels/rss.py:11](), `V2EXChannel` |
| `1` | Needs a free key or minor setup | `GitHubChannel`, `YouTubeChannel` |
| `2` | Needs accounts, cookies, or Docker | `TwitterChannel`, `XiaoHongShuChannel`, `InstagramChannel` |

Sources: [agent_reach/channels/base.py:35](), [agent_reach/channels/rss.py:11](), [tests/test_channel_contracts.py:21-25]()

---

## Health Reporting and Probing

Agent Reach uses `probe_command` to distinguish between different failure modes, ensuring `doctor` reports reflect actual usability rather than just file existence [agent_reach/probe.py:1-14]().

**`probe_command` Failure Modes** ([agent_reach/probe.py:28-31]()):
- `missing`: Command not on PATH.
- `broken`: Command exists (e.g., a stale venv shim) but cannot execute.
- `timeout`: Command runs but exceeds the time limit.
- `error`: Command returns a non-zero exit code.

**`check()` Statuses** ([agent_reach/channels/base.py:64]()):
- `ok`: Backend tool is installed and reachable.
- `warn`: Tool is installed but needs configuration (e.g., cookies/proxy).
- `off`: Tool is missing or dependencies are not met.
- `error`: Unexpected failure during check.

Sources: [agent_reach/probe.py:1-120](), [agent_reach/channels/base.py:61-70](), [agent_reach/channels/rss.py:16-27]()

---

## Configuration and Backend Overrides

`AgentReach` uses the `Config` class to manage settings. Channels can honor user overrides for backend selection. The config key `<channel>_backend` (or environment variable `<CHANNEL>_BACKEND`) promotes a specific tool to the front of the candidate list [agent_reach/channels/base.py:45-59]().

For example, if `TwitterChannel` supports both `bird` and `jina`, a user can force `bird` by setting `twitter_backend: bird` in `config.yaml` [tests/test_channel_contracts.py:86-93]().

Sources: [agent_reach/channels/base.py:45-59](), [tests/test_channel_contracts.py:72-98]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/README_en.md](docs/README_en.md)
- [docs/install.md](docs/install.md)

</details>



This page covers the three-step process to get Agent Reach installed and operational: installing the Python package, running the automated setup command, and verifying channel status with the built-in diagnostic tool.

For a conceptual overview of what Agent Reach is and why it exists, see [1. Overview](). For full CLI reference including all flags, see [2. CLI Reference](). For configuring individual credentials (cookies, proxies, tokens), see [4. Configuration]().

---

## Prerequisites

| Requirement | Minimum | Notes |
|---|---|---|
| Python | 3.10+ | Required by `pyproject.toml` |
| pip / pipx | Recent version | `pipx` is recommended for CLI isolation |
| Internet access | Required | Several backends make outbound HTTP calls |

Some channels install additional system dependencies automatically during `agent-reach install`. These include Node.js (for `bird`), the `gh` CLI, `mcporter`, and `instaloader`. If you prefer not to have these installed automatically, use the default check-only mode or `--safe`.

Sources: [pyproject.toml:21-21](), [docs/install.md:53-81]()

---

## Step 1: Install the Package

The recommended way to install Agent Reach is via `pipx` to ensure the CLI and its dependencies are isolated from your global Python environment.

```bash
# Recommended: pipx
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip

# Alternative: Standard pip (inside a venv)
python3 -m venv ~/.agent-reach-venv
source ~/.agent-reach-venv/bin/activate
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
```

This installs the `agent_reach` Python package and registers the `agent-reach` console script entrypoint, which maps to the `main()` function in `agent_reach/cli.py`.

Sources: [docs/install.md:52-66](), [pyproject.toml:35-36]()

---

## Step 2: Run Automated Setup

Once the package is installed, you must run the installation command to set up the necessary system-level dependencies and configuration files. By default, `agent-reach install` performs a read-only check. To actually modify the system, the `--system` flag is required.

```bash
# Read-only check (default)
agent-reach install --env=auto

# Perform system-level installation (after user approval)
agent-reach install --env=auto --system
```

**What `agent-reach install --env=auto --system` does:**

| Action | Details |
|---|---|
| **Detects environment** | Checks whether running locally or on a server to adjust proxy/dependency logic. |
| **Installs system deps** | Automatically installs Node.js, `gh` CLI, `bird` (via npm), and `mcporter`. |
| **Configures Exa search** | Sets up the `mcporter` connection to `mcp.exa.ai` for semantic search. |
| **Registers SKILL.md** | Copies `agent_reach/skill/SKILL.md` into the agent's skills directory (e.g., `~/.openclaw/skills/`). |
| **Channel Selection** | Allows specific activation via `--channels=all` or comma-separated names. |

**Installation mode variants:**

| Command | Behavior |
|---|---|
| `agent-reach install --env=auto` | **Safe Default**: Checks and reports missing dependencies but does not install system packages. |
| `agent-reach install --env=auto --system` | **System Install**: Explicitly allows external/system installs and configuration writes. |
| `agent-reach install --env=auto --dry-run` | **Dry Run**: Previews all actions (file writes, installs) without making changes. |

Sources: [docs/install.md:81-95](), [docs/install.md:120-126]()

---

## Step 3: Verify with Doctor

After installation, verify the status of all integrations using the `doctor` command.

```bash
agent-reach doctor
```

This command iterates over every channel in `ALL_CHANNELS` to determine operational status, reporting whether backends are missing, unconfigured, or ready.

**Example output:**

```text
👁️  Agent Reach Status
========================================

✅ Ready to use:
  ✅ GitHub repos and code — gh CLI
  ✅ YouTube video subtitles — yt-dlp
  ✅ RSS/Atom feeds — feedparser
  ✅ Web pages (any URL) — Jina Reader API

🔍 Search (configure to unlock):
  ⬜ Web semantic search — configure Exa MCP

🔧 Configurable:
  ⬜ Twitter/X — needs cookie
  ⬜ XiaoHongShu notes — needs mcporter/cookie
```

**Status indicators:**

| Symbol | Meaning |
|---|---|
| ✅ | **OK**: Channel is operational and all dependencies are found. |
| ⚠️ | **Warning**: Channel works partially or status is unverified (e.g., OpenCLI channels). |
| ⬜ / ❌ | **Off/Error**: Channel is unconfigured or a required dependency/cookie is missing. |

Sources: [docs/install.md:130-132](), [docs/README_en.md:97-97]()

---

## Setup Flow Diagram

**Diagram: Installation steps mapped to code entities**

```mermaid
flowchart TD
    subgraph "Natural Language Space"
        User["'Install Agent Reach'"]
        Agent["AI Agent (Claude/Cursor)"]
    end

    subgraph "Code Entity Space: Installation Phase"
        Pip["pip install agent-reach"] --> CLI_Main["agent_reach/cli.py: main()"]
        CLI_Main --> CmdInstall["agent_reach/cli.py: cmd_install()"]
    end

    subgraph "Code Entity Space: Setup Logic"
        CmdInstall --> DepCheck["Checks: Node.js, gh, bird, mcporter"]
        CmdInstall --> ConfigWrite["agent_reach/config.py: Config.set()\nWrites ~/.agent-reach/config.yaml"]
        CmdInstall --> SkillReg["agent_reach/skill/SKILL.md\nCopied to agent skills dir"]
    end

    subgraph "Code Entity Space: Verification Phase"
        CmdDoctor["agent_reach/cli.py: cmd_doctor()"] --> DoctorCheck["agent_reach/doctor.py: check_all()"]
        DoctorCheck --> Registry["agent_reach/channels/__init__.py: ALL_CHANNELS"]
    end

    User --> Agent
    Agent --> Pip
    CmdInstall -.-> CmdDoctor
```

Sources: [docs/install.md:49-96](), [docs/install.md:130-132]()

---

## Channel Availability After Install

After running `agent-reach install`, channels are categorized into three tiers based on their configuration requirements.

**Diagram: Channel tiers and their backend dependencies**

```mermaid
graph LR
    subgraph "Tier 0: Zero-Config (Works Immediately)"
        web["WebChannel\n(Jina Reader)"]
        youtube["YouTubeChannel\n(yt-dlp)"]
        github["GitHubChannel\n(gh CLI)"]
        rss["RSSChannel\n(feedparser)"]
        v2ex["V2EXChannel\n(Public API)"]
    end

    subgraph "Tier 1: Needs Configuration"
        exa["ExaSearchChannel\n(mcporter + Exa)"]
        twitter["TwitterChannel\n(bird + Cookies)"]
        xueqiu["XueqiuChannel\n(Cookie Jar)"]
    end

    subgraph "Tier 2: Requires Setup/Browser"
        xhs["XiaoHongShuChannel\n(mcporter + Docker/OpenCLI)"]
        meta["Facebook/Instagram\n(OpenCLI browser session)"]
        reddit["RedditChannel\n(rdt-cli + Proxy)"]
    end

    InstallCmd["agent-reach install --system"] --> web
    InstallCmd --> youtube
    InstallCmd --> github
    ConfigCmd["agent-reach configure"] --> exa
    ConfigCmd --> twitter
    ConfigCmd --> xhs
```

| Tier | Channels | What's needed |
|---|---|---|
| **0 — Zero-config** | `Web`, `YouTube`, `GitHub`, `RSS`, `V2EX` | Nothing — works immediately after `--system` installation. |
| **1 — Needs config** | `Exa`, `Twitter`, `Xueqiu`, `Bilibili` | `agent-reach configure` for cookies, proxies, or API keys. |
| **2 — External setup** | `XiaoHongShu`, `Reddit`, `Facebook`, `Instagram` | Requires `mcporter` for MCP servers or `OpenCLI` for browser sessions. |

Sources: [docs/README_en.md:101-115](), [docs/install.md:101-116]()

---

## Quick Reference: What to Run

```bash
# 1. Install the package
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip

# 2. Auto-setup (installs deps, registers skill, configures basic channels)
agent-reach install --env=auto --system

# 3. Check which channels are working
agent-reach doctor

# 4. (Optional) Test reading a URL
agent-reach read https://github.com/Panniantong/agent-reach

# 5. (Optional) Test search
agent-reach search "LLM framework comparison"
```

---

## Next Steps

After the initial setup, you can:

- **Unlock additional channels**: Follow the prompts from `agent-reach doctor` to configure cookies or proxies. See [4.1 Cookie Export Guide]() and [4.2 Proxy Configuration]().
- **Configure MCP services**: Needed for XiaoHongShu and Exa. See [4.3 mcporter Setup]().
- **Integrate with AI agents**: Ensure your agent has access to the registered `SKILL.md`. See [5. AI Agent Integration]().

Sources: [docs/install.md:97-151](), [docs/README_en.md:89-98]()

---

# Page: CLI Reference

# CLI Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/cli.py](agent_reach/cli.py)
- [docs/update.md](docs/update.md)
- [tests/test_cli.py](tests/test_cli.py)

</details>



This page documents the `agent-reach` command-line interface: the `main()` entrypoint in `agent_reach/cli.py`, how subcommands are parsed and dispatched, global flags, and the complete set of subcommands with their arguments.

For details on what each channel does when called by these commands, see [Channels](#3). For the configuration file and credential storage, see [Configuration](#4). For a guided first-run walkthrough, see [Getting Started](#1.2).

---

## Entrypoint

The package registers a single console script called `agent-reach`, which maps to `agent_reach.cli:main` as declared in `pyproject.toml`. The `main()` function [agent_reach/cli.py:59-163]() builds an `argparse.ArgumentParser` with one subparser per command, parses `sys.argv`, then dispatches to a `_cmd_*` handler function.

On Windows, `main()` also patches `sys.stdout` and `sys.stderr` to UTF-8 before anything else [agent_reach/cli.py:33-49](), so emoji and CJK characters do not crash on narrow system encodings.

Loguru logging is suppressed by default; passing `-v` / `--verbose` re-enables it at `INFO` level via `_configure_logging()` [agent_reach/cli.py:51-57]().

---

## Command Dispatch

**Diagram: `main()` → handler function dispatch**

```mermaid
flowchart LR
    entry["agent-reach\n(console_scripts)"]
    main["main()\nagent_reach/cli.py"]

    entry --> main

    main --> r["read\n→ _cmd_read(args)"]
    main --> s["search\n→ _cmd_search(args)"]
    main --> sr["search-reddit\n→ _cmd_search(args)"]
    main --> sg["search-github\n→ _cmd_search(args)"]
    main --> st["search-twitter\n→ _cmd_search(args)"]
    main --> sy["search-youtube\n→ _cmd_search(args)"]
    main --> sb["search-bilibili\n→ _cmd_search(args)"]
    main --> sx["search-xhs\n→ _cmd_search(args)"]
    main --> si["search-instagram\n→ _cmd_search(args)"]
    main --> sl["search-linkedin\n→ _cmd_search(args)"]
    main --> ins["install\n→ _cmd_install(args)"]
    main --> cfg["configure\n→ _cmd_configure(args)"]
    main --> doc["doctor\n→ _cmd_doctor()"]
    main --> cu["check-update\n→ _cmd_check_update()"]
    main --> w["watch\n→ _cmd_watch()"]
    main --> su["setup\n→ _cmd_setup()"]
    main --> sk["skill\n→ _cmd_skill(args)"]
    main --> fmt["format\n→ _cmd_format(args)"]
    main --> tr["transcribe\n→ _cmd_transcribe(args)"]

    r & s & sr & sg & st & sy & sb & sx & si & sl -->|"asyncio.run()"| AR["AgentReach\nagent_reach/core.py"]
    doc & w --> DOC["check_all()\nagent_reach/doctor.py"]
    ins & cfg --> CFG["Config\nagent_reach/config.py"]
    sk --> SKILL["_cmd_skill()\nagent_reach/cli.py"]
    tr --> TRANS["transcribe()\nagent_reach/transcribe.py"]
```

Sources: [agent_reach/cli.py:59-163](), [tests/test_cli.py:12-13]()

---

## Global Flags

These flags apply to the top-level `agent-reach` parser and must be placed before the subcommand name.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-v`, `--verbose` | bool flag | off | Enable loguru INFO logs on stderr |
| `--version` | action | — | Print `Agent Reach vX.Y.Z` and exit |

Sources: [agent_reach/cli.py:66-67](), [tests/test_cli.py:18-24]()

---

## Command Summary

| Command | Handler | Description |
|---------|---------|-------------|
| `read <url>` | `_cmd_read()` | Read content from any URL |
| `search <query>` | `_cmd_search()` | Web search via Exa |
| `search-twitter <query>` | `_cmd_search()` | Search Twitter/X |
| `search-reddit <query>` | `_cmd_search()` | Search Reddit |
| `search-github <query>` | `_cmd_search()` | Search GitHub |
| `search-youtube <query>` | `_cmd_search()` | Search YouTube |
| `search-bilibili <query>` | `_cmd_search()` | Search Bilibili |
| `search-xhs <query>` | `_cmd_search()` | Search XiaoHongShu |
| `search-instagram <query>` | `_cmd_search()` | Search Instagram |
| `search-linkedin <query>` | `_cmd_search()` | Search LinkedIn |
| `install` | `_cmd_install()` | One-shot installer with dependency detection |
| `configure` | `_cmd_configure()` | Set config values or auto-extract from browser |
| `setup` | `_cmd_setup()` | Interactive configuration wizard |
| `doctor` | `_cmd_doctor()` | Check platform availability and health |
| `skill` | `_cmd_skill()` | Install or uninstall SKILL.md for AI agents |
| `format` | `_cmd_format()` | Clean and format platform API output (e.g., XHS) |
| `watch` | `_cmd_watch()` | Quick health + update check for scheduled tasks |
| `check-update` | `_cmd_check_update()` | Check for new versions and changes |
| `transcribe` | `_cmd_transcribe()` | Transcribe audio/video via Whisper (Groq/OpenAI) |
| `uninstall` | `_cmd_uninstall()` | Remove config, tokens, and skill files |

Sources: [agent_reach/cli.py:68-163]()

---

## `read`

```
agent-reach read <url> [--json]
```

Dispatches to `_cmd_read(args)`, which calls `AgentReach.read(url)`. The correct channel is selected by `get_channel_for_url()` based on the URL. Output defaults to a human-readable multiline format; `--json` switches to a `json.dumps` of the raw result dict.

| Argument | Required | Description |
|----------|----------|-------------|
| `url` | yes | Any URL; channel selection is automatic |
| `--json` | no | Output as a JSON object instead of formatted text |

Sources: [agent_reach/cli.py:904-927] (approx)

---

## `install`

```
agent-reach install [--env {local,server,auto}] [--proxy URL] [--system] [--safe] [--dry-run]
```

**Diagram: `_cmd_install()` execution flow**

```mermaid
flowchart TD
    start["_cmd_install(args)"]
    detect["_detect_environment()\nauto-detects local vs server"]
    deps["_install_system_deps()\ngh CLI, Node.js, bird, mcporter"]
    deps_safe["_install_system_deps_safe()\ncheck-only mode"]
    deps_dry["_install_system_deps_dryrun()\nprint-only mode"]
    skill["_install_skill()\nwrite SKILL.md to agent dirs"]
    end_["print summary"]

    start --> detect
    detect --> D{mode?}
    D -->|"--system"| deps
    D -->|"--safe"| deps_safe
    D -->|"--dry-run"| deps_dry
    deps & deps_safe & deps_dry --> skill
    skill --> end_
```

| Flag | Default | Description |
|------|---------|-------------|
| `--env` | `auto` | `local`, `server`, or `auto` (auto-detects cloud/desktop) |
| `--proxy` | `""` | Network proxy saved for agents |
| `--system` | off | Explicitly allow system dependency installation |
| `--safe` | off | Safe check-only mode |
| `--dry-run` | off | Show changes without applying them |

Sources: [agent_reach/cli.py:73-97](), [docs/update.md:78-79]()

---

## `configure`

```
agent-reach configure <key> <value>
agent-reach configure --from-browser <BROWSER> --platform <PLATFORM>
```

Handled by `_cmd_configure(args)`. Supports manual entry or automatic extraction from browser profiles.

**Configurable keys:**

| Key | Config field(s) set | Notes |
|-----|---------------------|-------|
| `proxy` | `proxy` | Restricted network bypass |
| `twitter-cookies` | `twitter_auth_token`, `twitter_ct0` | Supports raw tokens or cookie headers |
| `github-token` | `github-token` | Personal access token |
| `groq-key` | `groq-key` | Groq API for Whisper |
| `xhs-cookies` | `xhs-cookies` | XiaoHongShu session |

Sources: [agent_reach/cli.py:99-128](), [tests/test_cli.py:148-186]()

---

## `transcribe`

```
agent-reach transcribe <source> [--provider {auto,groq,openai}] [--o output.txt]
```

Transcribes a local file or URL using Whisper.

| Flag | Default | Description |
|------|---------|-------------|
| `--provider` | `auto` | Choose backend (Groq preferred) |
| `--allow-provider-fallback` | off | Allow switching if primary fails |
| `-o`, `--output` | stdout | Save result to a file |

Sources: [agent_reach/cli.py:156-163](), [tests/test_cli.py:91-147]()

---

## `doctor` and `watch`

- **`doctor`**: Detailed health report of all channels, showing which backends are active (e.g., bird CLI vs Jina Reader) and their status (ok/warn/off) [agent_reach/cli.py:131-133](), [tests/test_cli.py:32-90]().
- **`watch`**: Optimized for automated monitoring; checks health and updates in one go [docs/update.md:90-93]().

---

## Update Workflow

Updates are managed via `check-update` and the instructions in `docs/update.md`.

1. Run `agent-reach check-update` to see if a new version exists [docs/update.md:31-35]().
2. Use `pip install --upgrade` or `pipx install --force` to pull the latest main branch [docs/update.md:39-46]().
3. Run `agent-reach doctor` to verify skill registration and channel health [docs/update.md:90-108]().

Sources: [docs/update.md:1-120]()

---

# Page: Installation Command

# Installation Command

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/cli.py](agent_reach/cli.py)
- [docs/install.md](docs/install.md)

</details>



This page documents the `agent-reach install` subcommand: its flags, what system dependencies it detects and installs, how it decides between operating modes, and how it registers `SKILL.md` into AI agent skill directories.

For the overall CLI structure and all available subcommands, see [CLI Reference](2). For configuring credentials after installation, see [Configure Command](2.4). For understanding channel health after installation, see [Diagnostics and Monitoring](2.5).

---

## Overview

The `install` command is a one-shot, deterministic installer that bootstraps all system-level dependencies required by Agent Reach's channel backends. It is defined in `agent_reach/cli.py` and invoked as:

```bash
agent-reach install [--env=local|server|auto] [--system] [--safe] [--dry-run] [--proxy URL] [--channels twitter,reddit,...]
```

The flags control the operating mode and environment context:

| Flag | Behavior |
|---|---|
| `--env=auto` (default) | Auto-detects whether the machine is a local computer or a server [agent_reach/cli.py:75-76]() |
| `--env=local` | Forces local-computer mode (attempts browser cookie import) [agent_reach/cli.py:75-76]() |
| `--env=server` | Forces server mode (skips cookie import, prints proxy advice) [agent_reach/cli.py:75-76]() |
| `--system` | Explicitly allows system dependency, global tool, and skill installation [agent_reach/py:82-85]() |
| `--safe` (default) | Checks what is installed; prints instructions for what is missing; makes no changes [agent_reach/cli.py:87-90]() |
| `--dry-run` | Prints what *would* be done; makes no changes whatsoever [agent_reach/cli.py:91-92]() |
| `--proxy URL` | Immediately writes a proxy value to `reddit_proxy` and `bilibili_proxy` in config [agent_reach/cli.py:77-79]() |
| `--channels` | Comma-separated list of optional channels to install (e.g., `twitter,bilibili,all`) [agent_reach/cli.py:93-96]() |

Sources: [agent_reach/cli.py:73-96](), [docs/install.md:88-95]()

---

## Operating Modes

The installation logic follows a clear decision tree based on the provided flags. By default, the command is "Safe" (read-only check). System changes only occur if `--system` is provided.

**Operating Mode Decision Logic**

```mermaid
flowchart TD
    A["agent-reach install"] --> B{"--dry-run?"}
    B -- "yes" --> C["_install_system_deps_dryrun()\nprint what would run\nno changes"]
    B -- "no" --> D{"--system?"}
    D -- "no" --> E["_install_system_deps_safe()\ncheck + print instructions\nno auto-install"]
    D -- "yes" --> F["_install_system_deps()\nauto-install all deps"]
    C --> G["print mcporter dry-run message"]
    E --> H["_install_mcporter_safe()\ncheck only"]
    F --> I["_install_mcporter()\nauto-install + configure"]
    I --> J{"env == local?"}
    J -- "yes" --> K["configure_from_browser(chrome)\nconfigure_from_browser(firefox)"]
    J -- "no" --> L["print server proxy advice"]
    K --> M["check_all(config)\nformat_report(results)"]
    L --> M
    M --> N["_install_skill()"]
```

Sources: [agent_reach/cli.py:179-299](), [docs/install.md:11-15]()

---

## Environment Auto-Detection

When `--env=auto` is passed (the default), `_detect_environment()` inspects several OS-level signals to differentiate between a local workstation and a remote server/container.

**`_detect_environment()` Scoring Logic**

```mermaid
flowchart LR
    subgraph "Indicators checked in _detect_environment()"
        SSH["SSH_CONNECTION or\nSSH_CLIENT env var\n(+2 points)"]
        Docker["/.dockerenv or\n/run/.containerenv\n(+2 points)"]
        Display["No DISPLAY and\nno WAYLAND_DISPLAY\n(+1 point)"]
        Cloud["Cloud vendor string\nin /sys/hypervisor/uuid\nor product_name\n(+2 points)"]
        Virt["systemd-detect-virt\nreturns non-none\n(+1 point)"]
    end
    Score["Total score"] --> Result{"score >= 2?"}
    Result -- "yes" --> Server["env = 'server'"]
    Result -- "no" --> Local["env = 'local'"]
```

Sources: [agent_reach/cli.py:643-681]()

---

## System Dependencies

`_install_system_deps()` checks and installs tools in sequence. Each tool is verified with `shutil.which()` before any installation is attempted.

**Dependency Installation Map**

| Tool | Binary check | Install method | Purpose |
|---|---|---|---|
| `gh` CLI | `shutil.which("gh")` | APT (Linux) / Homebrew (macOS) | GitHub channel backend [agent_reach/cli.py:394-420]() |
| Node.js | `shutil.which("node")` | NodeSource curl script + `apt-get install nodejs` | Required by mcporter and bird [agent_reach/cli.py:422-454]() |
| `bird` CLI | `shutil.which("bird")` | `npm install -g @steipete/bird` | Twitter channel backend [agent_reach/cli.py:456-470]() |
| `undici` | `npm list -g undici` | `npm install -g undici` | Proxy support for Node.js `fetch()` [agent_reach/cli.py:472-487]() |
| `instaloader` | `shutil.which("instaloader")` | `pip install instaloader` | Instagram channel backend [agent_reach/cli.py:489-502]() |
| `rdt-cli` | `shutil.which("rdt")` | `pip install git+https://github.com/public-clis/rdt-cli.git` | Reddit channel backend [agent_reach/cli.py:504-518]() |

Sources: [agent_reach/cli.py:391-532]()

### Safe Mode Implementation

`_install_system_deps_safe()` iterates the same dependency list but never runs any install command. It prints the manual install hint for each missing tool, such as `npm install -g @steipete/bird` for the bird CLI.

Sources: [agent_reach/cli.py:535-563]()

### Dry-Run Mode Implementation

`_install_system_deps_dryrun()` performs `shutil.which()` checks and prints either `✅ already installed, skip` or `📥 would install via: <method>` for each tool. No subprocess calls are made.

Sources: [agent_reach/cli.py:566-584]()

---

## mcporter Setup

After system dependencies, `_install_mcporter()` installs and configures `mcporter`, the MCP bridge used by Exa search, LinkedIn, and XiaoHongShu channels.

**`_install_mcporter()` Sequence**

```mermaid
sequenceDiagram
    participant "install" as "_cmd_install()"
    participant "mc" as "_install_mcporter()"
    participant "npm" as "npm subprocess"
    participant "mcporter" as "mcporter subprocess"
    participant "xhs" as "localhost:18060"

    "install" ->> "mc": call
    "mc" ->> "mc": shutil.which('mcporter')?
    alt "not installed"
        "mc" ->> "npm": npm install -g mcporter
    end
    "mc" ->> "mcporter": mcporter list
    alt "'exa' not in output"
        "mc" ->> "mcporter": mcporter config add exa https://mcp.exa.ai/mcp
    end
    "mc" ->> "mcporter": mcporter list
    alt "'xiaohongshu' not in output"
        "mc" ->> "xhs": GET http://localhost:18060/ (3s timeout)
        alt "server running"
            "mc" ->> "mcporter": mcporter config add xiaohongshu http://localhost:18060/mcp
        else "not running"
            "mc" ->> "install": print Docker setup instructions
        end
    end
```

Sources: [agent_reach/cli.py:587-624]()

The Exa MCP endpoint (`https://mcp.exa.ai/mcp`) is always configured if not already present [agent_reach/cli.py:619-622](). The XiaoHongShu MCP (`http://localhost:18060/mcp`) is only registered if a Docker container is detected responding at that address [agent_reach/cli.py:634-641]().

---

## Browser Cookie Auto-Import

On `env=local` (provided it is not safe or dry-run mode), the installer attempts to pull cookies from the local browser via `configure_from_browser()`.

```python
# Implementation detail in _cmd_install
if env == "local" and not safe_mode and not dry_run:
    from agent_reach.cookie_extract import configure_from_browser
    configure_from_browser("chrome", config)
    configure_from_browser("firefox", config)
```

Only successes are printed. If neither browser yields any cookies, a message is shown suggesting manual configuration via `agent-reach configure`.

Sources: [agent_reach/cli.py:237-268]()

---

## SKILL.md Registration

The final step of installation is `_install_skill()`, which writes the `SKILL.md` file into recognized AI agent skill directories.

**`_install_skill()` Directory Probe Order**

```mermaid
flowchart TD
    A["_install_skill()"] --> B["check ~/.openclaw/skills"]
    B -- "exists" --> W1["write SKILL.md to\n~/.openclaw/skills/agent-reach/"]
    B -- "missing" --> C["check ~/.claude/skills"]
    C -- "exists" --> W2["write SKILL.md to\n~/.claude/skills/agent-reach/"]
    C -- "missing" --> D["check ~/.agents/skills"]
    D -- "exists" --> W3["write SKILL.md to\n~/.agents/skills/agent-reach/"]
    D -- "missing" --> E["no known dir found\ncreate ~/.openclaw/skills/agent-reach/\nas default fallback"]
    W1 & W2 & W3 & E --> F["importlib.resources.files('agent_reach')\n.joinpath('skill', 'SKILL.md')\n.read_text()"]
```

The skill file content is read using `importlib.resources` from the package data [agent_reach/cli.py:353-355](). Multiple matching directories are all updated if they exist [agent_reach/cli.py:359-380]().

Sources: [agent_reach/cli.py:350-388]()

---

## Full Install Sequence Summary

| Step | `--dry-run` | `--safe` (Default) | `--system` |
|---|---|---|---|
| System deps | Prints `[dry-run] would install` | Prints install hints | Installs via subprocess |
| mcporter | Prints `[dry-run] would install` | Prints manual hint | Installs + configures |
| Cookies | Prints `[dry-run] would try` | Prints manual hint | Auto-extracts from Chrome/FF |
| Channel check | Skipped | Runs `check_all()` | Runs `check_all()` |
| `SKILL.md` | Skipped | Runs `_install_skill()` | Runs `_install_skill()` |

Sources: [agent_reach/cli.py:179-299](), [docs/install.md:88-95]()

---

# Page: Reading Content

# Reading Content

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/web.py](agent_reach/channels/web.py)
- [agent_reach/cli.py](agent_reach/cli.py)
- [agent_reach/utils/url.py](agent_reach/utils/url.py)
- [tests/test_web_channel.py](tests/test_web_channel.py)

</details>



This page documents the `agent-reach read <url>` command: its flags, output formats, URL normalization behavior, and the internal channel dispatch mechanism that determines which backend handles each URL. For documentation on search commands, see **2.3 Search Commands**. For details on individual channel backends, see **3. Channels**.

---

## Command Syntax

```bash
agent-reach read <url> [--json]
```

| Flag | Description |
|------|-------------|
| `url` | Any URL to read. Scheme (`https://`) is optional. |
| `--json` | Emit a JSON object instead of the default human-readable output. |
| `-v` / `--verbose` | Show internal log output from channel backends. |

Sources: [agent_reach/cli.py:62-68](), [agent_reach/cli.py:168-175]()

---

## Internal Execution Flow

When `agent-reach read` is invoked, the CLI parses the arguments and delegates the network operations to the `AgentReach` core class. The core class performs URL normalization and iterates through the `ALL_CHANNELS` registry to find a suitable handler.

**Dispatch diagram: `agent-reach read` internals**

```mermaid
flowchart TD
    A["agent-reach read <url>"] --> B["main() in agent_reach/cli.py"]
    B --> C["_cmd_read(args)"]
    C --> D["AgentReach().read(url) in agent_reach/core.py"]
    D --> E{"url starts with\nhttp:// or https://?"}
    E -- "No" --> F["prepend https://"]
    E -- "Yes" --> G["get_channel_for_url(url)\nin agent_reach/channels/__init__.py"]
    F --> G
    G --> H["iterate ALL_CHANNELS\nfirst channel.can_handle(url) wins"]
    H --> I["channel.read(url)"]
    I --> J["ReadResult.to_dict()"]
    J --> K{"--json flag?"}
    K -- "Yes" --> L["json.dumps(result)"]
    K -- "No" --> M["print title, url, author, content"]
```

Sources: [agent_reach/cli.py:168-185](), [agent_reach/core.py:42](), [agent_reach/channels/__init__.py:36-53]()

---

## URL Normalization and Security

Before channel dispatch, `AgentReach.read()` and the underlying `WebChannel` ensure the input is a valid absolute URL. The `normalize_public_http_url` utility provides a security boundary by rejecting non-public targets.

1.  **Scheme Completion**: If `://` is missing, `https://` is prepended [agent_reach/utils/url.py:59-60]().
2.  **Public Boundary Enforcement**: The system rejects URLs targeting local networks, private IP ranges (e.g., `127.0.0.1`, `192.168.x.x`), or internal hostnames (e.g., `.local`, `.internal`) [agent_reach/utils/url.py:71-82]().
3.  **Credential Stripping**: URLs containing embedded usernames or passwords are rejected for security [agent_reach/utils/url.py:74-75]().

Sources: [agent_reach/utils/url.py:47-84](), [agent_reach/channels/web.py:50-51]()

---

## Channel Dispatch

The `get_channel_for_url(url)` function iterates through the `ALL_CHANNELS` list in a specific priority order. The first channel whose `can_handle(url)` returns `True` is selected. `WebChannel` is positioned at the end of the list as a catch-all fallback using Jina Reader.

**Channel registry order (ALL_CHANNELS)**

```mermaid
flowchart LR
    URL["Input URL"] --> G["GitHubChannel"]
    G -- "no match" --> T["TwitterChannel"]
    T -- "no match" --> Y["YouTubeChannel"]
    Y -- "no match" --> R["RedditChannel"]
    R -- "no match" --> Bi["BilibiliChannel"]
    Bi -- "no match" --> X["XiaoHongShuChannel"]
    X -- "no match" --> Dy["DouyinChannel"]
    Dy -- "no match" --> Li["LinkedInChannel"]
    Li -- "no match" --> Wc["WeChatChannel"]
    Wc -- "no match" --> Wb["WeiboChannel"]
    Wb -- "no match" --> Xyz["XiaoyuzhouChannel"]
    Xyz -- "no match" --> V2["V2EXChannel"]
    V2 -- "no match" --> Xq["XueqiuChannel"]
    Xq -- "no match" --> Rss["RSSChannel"]
    Rss -- "no match" --> Exa["ExaSearchChannel"]
    Exa -- "no match" --> W["WebChannel (fallback)"]
```

Sources: [agent_reach/channels/__init__.py:36-53](), [agent_reach/core.py:42]()

---

## URL-to-Channel Mapping

The following table summarizes which channel handles specific URL patterns based on their `can_handle()` implementation.

| Channel class | Handled URL patterns | Primary backend |
|---|---|---|
| `GitHubChannel` | `github.com/*` | `gh` CLI |
| `TwitterChannel` | `twitter.com/*`, `x.com/*` | `bird` CLI |
| `YouTubeChannel` | `youtube.com/*`, `youtu.be/*` | `yt-dlp` |
| `RedditChannel` | `reddit.com/*` | `rdt-cli` |
| `BilibiliChannel` | `bilibili.com/*`, `b23.tv/*` | `bili-cli` |
| `XiaoHongShuChannel` | `xiaohongshu.com/*`, `xhslink.com/*` | `mcporter` + `xiaohongshu-mcp` |
| `V2EXChannel` | `v2ex.com/*` | V2EX Public API |
| `RSSChannel` | Feed URLs (detected by content/ext) | `feedparser` |
| `WebChannel` | any URL | Jina Reader (`r.jina.ai`) |

Sources: [agent_reach/channels/web.py:40-41](), [agent_reach/channels/__init__.py:36-53]()

---

## WebChannel Fallback (Jina Reader)

When no specific platform channel matches, the `WebChannel` acts as the universal fallback. It routes the request through `https://r.jina.ai/` to convert the target webpage into Markdown.

*   **Antibot Detection**: `WebChannel` includes `_is_antibot_page` to recognize Cloudflare or Jina captcha challenges, raising a `RuntimeError` to inform the user to try a browser-based method [agent_reach/channels/web.py:15-31]().
*   **Size Limits**: It enforces a 5MB response limit (`_MAX_RESPONSE_BYTES`) to prevent memory exhaustion when reading large assets [agent_reach/channels/web.py:11](), [agent_reach/channels/web.py:58-61]().

Sources: [agent_reach/channels/web.py:48-67](), [tests/test_web_channel.py:185-196]()

---

## Output Formats

### Default (human-readable)
The CLI prints a formatted view optimized for AI agent consumption or terminal reading:
```text
📖 <title>
🔗 <url>
👤 <author>       ← only printed when present

<content>
```
The `author` field is optional and only displayed if the channel populates it in the `ReadResult`.

### JSON (`--json`)
Emits a structured JSON object. This is preferred for programmatic integration or when the agent needs to parse specific metadata fields.
```json
{
  "title": "Example Title",
  "url": "https://example.com",
  "author": "Author Name",
  "content": "Full article content...",
  "platform": "web"
}
```

Sources: [agent_reach/cli.py:168-175]()

---

## Code Entity Map

This diagram associates natural language concepts with the specific code entities that implement the reading logic.

**Diagram: symbols used in the read pipeline**

```mermaid
flowchart TD
    subgraph "agent_reach/cli.py"
        main["main()"]
        cmd_read["_cmd_read(args)"]
    end
    subgraph "agent_reach/core.py"
        AR["AgentReach Class"]
        read["AgentReach.read(url)"]
    end
    subgraph "agent_reach/channels/__init__.py"
        gcfu["get_channel_for_url(url)"]
        ALL["ALL_CHANNELS: List[Channel]"]
    end
    subgraph "agent_reach/channels/base.py"
        Channel["Channel (Base Class)"]
        ReadResult["ReadResult (Data Class)"]
        can_handle["can_handle(url)"]
        ch_read["read(url)"]
        to_dict["ReadResult.to_dict()"]
    end

    main --> cmd_read
    cmd_read --> read
    read --> gcfu
    gcfu --> ALL
    ALL --> can_handle
    can_handle --> ch_read
    ch_read --> ReadResult
    ReadResult --> to_dict
```

Sources: [agent_reach/cli.py:168-185](), [agent_reach/core.py:42](), [agent_reach/channels/base.py:10-50]()

---

## Error Handling

The CLI implements specific error mapping to provide clear feedback when a read operation fails:

| Exception Pattern | CLI Output Message |
|---|---|
| `ValueError` (Public HTTP) | `❌ Invalid URL: <url>` |
| `ConnectionError` / `Timeout` | `❌ Could not connect to: <url>` |
| `RuntimeError` (Antibot) | `❌ Jina Reader 返回了反爬验证页...` |

Sources: [agent_reach/cli.py:180-210](), [agent_reach/channels/web.py:62-66]()

---

# Page: Search Commands

# Search Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/cli.py](agent_reach/cli.py)
- [agent_reach/skill/references/career.md](agent_reach/skill/references/career.md)
- [agent_reach/skill/references/search.md](agent_reach/skill/references/search.md)
- [agent_reach/skill/references/web.md](agent_reach/skill/references/web.md)
- [tests/test_skill_command.py](tests/test_skill_command.py)

</details>



This page documents all `search-*` subcommands exposed by the `agent-reach` CLI: their syntax, flags, default behaviors, and which backend channel each one invokes. For information about reading a specific URL (rather than issuing a search query), see [2.2](). For details on how individual channels work internally, see [3]().

---

## Overview

Every search command follows the same pattern:

```bash
agent-reach <search-subcommand> "<query>" [flags]
```

All commands accept a free-text query and a common `-n` flag to control result count. The CLI entrypoint `main()` in `agent_reach/cli.py` parses these arguments and dispatches them to the `_cmd_search` helper function.

The dispatching logic in `_cmd_search()` instantiates the core `AgentReach` class, calls the platform-specific search method (e.g., `search_twitter`), and iterates through the returned list of results to print them to the console.

**Output format per result (all commands):**

```text
1. <title>
   🔗 <url>
   <snippet, up to 200 chars>
   ⭐ <stars>  🍴 <forks>  📝 <language>   ← GitHub only
```

Sources: [agent_reach/cli.py:62-105](), [agent_reach/cli.py:930-995]()

---

## Command Reference

### Subcommand Summary

| Subcommand | Default `-n` | Platform-specific flags | Primary Backend |
|---|---|---|---|
| `search` | 5 | — | `ExaSearchChannel` (mcporter → exa-mcp) |
| `search-twitter` | 10 | — | `TwitterChannel` → `bird` CLI |
| `search-reddit` | 10 | `--sub <subreddit>` | `RedditChannel` → `rdt-cli` / `OpenCLI` |
| `search-github` | 5 | `--lang <language>` | `GitHubChannel` → `gh` CLI |
| `search-youtube` | 5 | — | `YouTubeChannel` → `yt-dlp` |
| `search-bilibili` | 5 | — | `BilibiliChannel` → `bili-cli` |
| `search-xhs` | 10 | — | `XiaoHongShuChannel` → `mcporter` / `OpenCLI` |
| `search-instagram` | 10 | — | `InstagramChannel` → `OpenCLI` |
| `search-linkedin` | 10 | — | `LinkedInChannel` → `mcporter` |
| `search-bosszhipin` | 10 | — | `BossZhipinChannel` → `mcporter` |

Sources: [agent_reach/cli.py:68-105](), [agent_reach/channels/__init__.py:31-50]()

---

### Common Flag: `-n / --num`

All search subcommands accept `-n` (or `--num`) to control the number of results returned. This is defined in the `argparse` setup for each search parser.

```bash
agent-reach search "rust async runtime" -n 10
agent-reach search-reddit "homelab" -n 20
```

The value is passed as the `limit` or `num_results` argument to the underlying `AgentReach` methods.

Sources: [agent_reach/cli.py:177-224]()

---

### `search` — General Web Search

```bash
agent-reach search "<query>" [-n N]
```

Routes to `AgentReach.search()`, which delegates to `ExaSearchChannel`. It uses `mcporter` to call the Exa MCP server. This is the recommended tool for technical documentation and code examples.

Sources: [agent_reach/cli.py:177-180](), [agent_reach/skill/references/search.md:5-13]()

---

### `search-twitter` — Twitter/X Search

```bash
agent-reach search-twitter "<query>" [-n N]
```

Routes to `AgentReach.search_twitter()`. The primary backend is the `bird` CLI. It requires `twitter-cookies` to be configured via `agent-reach configure`.

Sources: [agent_reach/cli.py:194-197](), [agent_reach/cli.py:948]()

---

### `search-reddit` — Reddit Search

```bash
agent-reach search-reddit "<query>" [--sub <subreddit>] [-n N]
```

Routes to `AgentReach.search_reddit()`. The optional `--sub` flag restricts search to a specific subreddit. Note that `RedditChannel` typically requires a proxy on server environments due to IP blocking.

Sources: [agent_reach/cli.py:182-186](), [agent_reach/cli.py:944]()

---

### `search-github` — GitHub Repository Search

```bash
agent-reach search-github "<query>" [--lang <language>] [-n N]
```

Routes to `AgentReach.search_github()`. The optional `--lang` flag filters results by programming language. It uses the `gh` CLI as the backend.

Sources: [agent_reach/cli.py:188-192](), [agent_reach/cli.py:946]()

---

### `search-linkedin` — LinkedIn Search

```bash
mcporter call linkedin.search_people keywords="AI engineer" location="Shanghai"
mcporter call linkedin.search_jobs keywords="software engineer" location="Remote"
```

LinkedIn search is primarily handled via the `mcporter` bridge to `mcp-server-linkedin`. It supports searching for people, companies, and jobs.

Sources: [agent_reach/skill/references/career.md:7-19](), [tests/test_skill_command.py:57-85]()

---

## Internal Dispatch Flow

**Diagram: Search Command Dispatch — from CLI to Code Entities**

```mermaid
flowchart TD
    input["agent-reach search-* query -n N"]
    main["main()\nagent_reach/cli.py"]
    dispatch["_cmd_search()\nagent_reach/cli.py:930"]
    ar["AgentReach class\nagent_reach/core.py"]

    subgraph methods["AgentReach Search Methods"]
        s["search()"]
        st["search_twitter()"]
        sr["search_reddit()"]
        sg["search_github()"]
        sy["search_youtube()"]
        sb["search_bilibili()"]
    end

    subgraph channels["Channel Classes"]
        exa["ExaSearchChannel"]
        tw["TwitterChannel"]
        rd["RedditChannel"]
        gh["GitHubChannel"]
        yt["YouTubeChannel"]
        bi["BilibiliChannel"]
    end

    input --> main
    main --> dispatch
    dispatch --> ar
    ar --> s --> exa
    ar --> st --> tw
    ar --> sr --> rd
    ar --> sg --> gh
    ar --> sy --> yt
    ar --> sb --> bi
```

Sources: [agent_reach/cli.py:60-224](), [agent_reach/cli.py:930-963]()

---

## Backend and Fallback Map

**Diagram: Natural Language Search to Backend Tools**

```mermaid
flowchart LR
    subgraph user["User Prompt"]
        p1["'Search Twitter for...'"]
        p2["'Find GitHub repos...'"]
        p3["'Search Bilibili...'"]
    end

    subgraph backends["Code Entity Backends"]
        bird["bird CLI\n(@steipete/bird)"]
        gh_cli["gh CLI\n(GitHub CLI)"]
        bili["bili-cli\n(Node.js)"]
        exa["Exa MCP\n(via mcporter)"]
    end

    user --> p1 --> bird
    bird -.->|"fallback"| exa
    user --> p2 --> gh_cli
    user --> p3 --> bili
    bili -.->|"fallback"| exa
```

Sources: [agent_reach/cli.py:930-963](), [agent_reach/skill/references/search.md:30-36]()

---

## Setup Requirements by Command

| Subcommand | Tier | Required Setup / Backend |
|---|---|---|
| `search` | 0 | `mcporter` + `exa-mcp` (Auto-installed) |
| `search-github` | 0 | `gh` CLI |
| `search-youtube` | 0 | `yt-dlp` |
| `search-reddit` | 1 | `rdt-cli` + Proxy (recommended) |
| `search-twitter` | 1 | `bird` CLI + `twitter-cookies` |
| `search-xhs` | 2 | `mcporter` + `xiaohongshu-mcp` (Docker) |
| `search-linkedin` | 2 | `mcporter` + `mcp-server-linkedin` |

For credential configuration, see [2.4](). For mcporter setup, see [4.3]().

Sources: [agent_reach/cli.py:98-128](), [tests/test_skill_command.py:88-111]()

---

# Page: Configure Command

# Configure Command

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/cli.py](agent_reach/cli.py)
- [agent_reach/config.py](agent_reach/config.py)
- [tests/test_config.py](tests/test_config.py)

</details>



The `configure` command stores credentials and settings that channels need to access specific platforms. It writes values to `~/.agent-reach/config.yaml` with restricted file permissions. This page documents all configurable keys, their accepted formats, and the automatic browser extraction option.

For details on the underlying storage mechanism, see [Configuration](#4). For a guide on exporting cookies from a browser, see [Cookie Export Guide](#4.1). For proxy-specific details (why it's needed and per-channel behavior), see [Proxy Configuration](#4.2).

---

## Command Syntax

```bash
agent-reach configure <key> <value>
agent-reach configure --from-browser <browser> --platform <platform>
```

The `key` argument is constrained to a fixed set of accepted names defined in the `argparse` configuration [agent_reach/cli.py:100-104](). The `value` argument accepts one or more space-separated tokens which are processed by the command handler [agent_reach/cli.py:105]().

**Key Mapping: CLI name → Internal config key(s)**

| CLI `key` | Internal config key(s) stored | Storage location |
|---|---|---|
| `proxy` | `proxy` | `config.yaml` |
| `github-token` | `github_token` | `config.yaml` |
| `groq-key` | `groq_api_key` | `config.yaml` |
| `openai-key` | `openai_api_key` | `config.yaml` |
| `twitter-cookies` | `twitter_auth_token`, `twitter_ct0` | `config.yaml` |
| `youtube-cookies` | `youtube_cookies_from` | `config.yaml` |
| `xhs-cookies` | `xhs_cookies` | `config.yaml` |

Sources: [agent_reach/cli.py:100-104](), [agent_reach/cli.py:23-30](), [agent_reach/config.py:106-112]()

---

## How Values Are Stored

Values are written via the `Config.set()` method [agent_reach/config.py:170-184](), which serializes to YAML and immediately sets the file to `0o600` (owner read/write only) via `_atomic_write_yaml` [agent_reach/config.py:46-96](). On subsequent reads, `Config.get()` checks the YAML data first, then falls back to an uppercase environment variable of the same name [agent_reach/config.py:159-168]().

**Configure command: code flow**

```mermaid
flowchart TD
    A["agent-reach configure"]
    B{"--from-browser\nset?"}
    C["_cmd_configure_from_browser(browser, platform, profile, config)\n(agent_reach/cli.py)"]
    D{"key argument"}
    E["proxy\n→ config.set('proxy')"]
    F["twitter-cookies\n→ parse auth_token + ct0\n→ config.set('twitter_auth_token')\n→ config.set('twitter_ct0')"]
    G["youtube-cookies\n→ config.set('youtube_cookies_from')"]
    H["github-token\n→ config.set('github_token')"]
    I["groq-key\n→ config.set('groq_api_key')"]
    K["Config.save()\n→ config.yaml chmod 0o600"]

    A --> B
    B -- "yes" --> C
    B -- "no" --> D
    D -- "proxy" --> E
    D -- "twitter-cookies" --> F
    D -- "youtube-cookies" --> G
    D -- "github-token" --> H
    D -- "groq-key" --> I
    E & F & G & H & I --> K
```

Sources: [agent_reach/cli.py:99-128](), [agent_reach/config.py:152-158](), [agent_reach/config.py:78-79](), [agent_reach/config.py:159-168]()

---

## Configurable Keys

### `proxy`

Sets a global proxy used by multiple channels (e.g., Reddit, Bilibili) to bypass server-side IP blocking or access restricted networks.

```bash
agent-reach configure proxy http://user:pass@ip:port
```

The value is stored as `proxy` in `config.yaml`. Note that `_SENSITIVE_CONFIG_KEYS` includes `proxy` to ensure it is redacted in diagnostic outputs [agent_reach/cli.py:23-30]().

Sources: [agent_reach/cli.py:24](), [agent_reach/cli.py:101]()

---

### `twitter-cookies`

Provides Twitter session credentials. The CLI accepts either a full cookie string or space-separated tokens. The internal logic parses these into `twitter_auth_token` and `twitter_ct0` [agent_reach/config.py:108]().

| Format | Example |
|---|---|
| Full cookie header string | `"auth_token=abc123; ct0=xyz789; ..."` |
| Two space-separated tokens | `AUTH_TOKEN_VALUE CT0_VALUE` |

Sources: [agent_reach/cli.py:102](), [agent_reach/config.py:108]()

---

### `youtube-cookies`

Configures a browser name for `yt-dlp`'s cookie extraction. This enables downloading age-restricted or member-only content.

```bash
agent-reach configure youtube-cookies chrome
```

The value is stored as `youtube_cookies_from` in `config.yaml`.

Sources: [agent_reach/cli.py:102]()

---

### `github-token`

Stores a GitHub personal access token as `github_token` [agent_reach/config.py:111](). This raises the GitHub API rate limit for the `GitHubChannel`.

```bash
agent-reach configure github-token ghp_xxxxxxxxxxxx
```

Sources: [agent_reach/cli.py:101](), [agent_reach/config.py:111]()

---

### `groq-key`

Stores a Groq API key as `groq_api_key` [agent_reach/config.py:109](). This key is used for Whisper transcription services.

```bash
agent-reach configure groq-key gsk_xxxxxxxxxxxx
```

Sources: [agent_reach/cli.py:101](), [agent_reach/config.py:109]()

---

## `--from-browser` Option

Automatically extracts cookies from a locally installed browser for a specific platform [agent_reach/cli.py:112-119]().

```bash
agent-reach configure --from-browser chrome --platform twitter
```

**Required Flags:**
*   `--from-browser`: Choices include `chrome`, `firefox`, `edge`, `brave`, `opera` [agent_reach/cli.py:113]().
*   `--platform`: Choices include `twitter`, `xiaohongshu`, `bilibili`, `xueqiu` [agent_reach/cli.py:117]().
*   `--profile` (Optional): Specifies an exact browser profile [agent_reach/cli.py:121]().

**`--from-browser` data flow**

```mermaid
flowchart LR
    Browser["Local Browser\n(logged-in session)"]
    CE["_cmd_configure_from_browser(browser, platform, profile, config)"]
    CFG["Config.set(...)\n→ config.yaml"]
    OUT["stdout:\n✅ Successfully imported cookies"]

    Browser -- "cookie store on disk" --> CE
    CE -- "extract platform cookies" --> CFG
    CFG --> OUT
```

Sources: [agent_reach/cli.py:112-123]()

---

## Internal Configuration Keys Reference

The `Config` class uses its own internal key names. This table maps CLI arguments to `config.yaml` keys.

```mermaid
graph LR
    subgraph CLIKeys["CLI key argument"]
        proxy["\"proxy\""]
        twcookies["\"twitter-cookies\""]
        ytcookies["\"youtube-cookies\""]
        ghtoken["\"github-token\""]
        groqkey["\"groq-key\""]
        xhscookies["\"xhs-cookies\""]
    end

    subgraph ConfigYAML["config.yaml keys (Config.data)"]
        gproxy["proxy"]
        twauth["twitter_auth_token"]
        twct0["twitter_ct0"]
        ytfrom["youtube_cookies_from"]
        ghtkn["github_token"]
        groqk["groq_api_key"]
        xhsc["xhs_cookies"]
    end

    subgraph FileSystem["Filesystem"]
        cfgfile["~/.agent-reach/config.yaml\n(chmod 0o600)"]
    end

    proxy --> gproxy
    twcookies --> twauth & twct0
    ytcookies --> ytfrom
    ghtoken --> ghtkn
    groqkey --> groqk
    xhscookies --> xhsc

    gproxy & twauth & twct0 & ytfrom & ghtkn & groqk & xhsc --> cfgfile
```

Sources: [agent_reach/cli.py:100-104](), [agent_reach/config.py:106-112]()

---

## Environment Variable Fallback

`Config.get()` checks the config file first, then falls back to an environment variable with the same name uppercased [agent_reach/config.py:159-168]().

| Internal key | Environment variable |
|---|---|
| `proxy` | `PROXY` |
| `twitter_auth_token` | `TWITTER_AUTH_TOKEN` |
| `twitter_ct0` | `TWITTER_CT0` |
| `github_token` | `GITHUB_TOKEN` |
| `groq_api_key` | `GROQ_API_KEY` |
| `openai_api_key` | `OPENAI_API_KEY` |

Sources: [agent_reach/config.py:165-167]()

---

## Post-Configure Verification

After running `configure`, use `agent-reach doctor` to confirm the channel status has changed. The `Config.is_configured()` method checks whether all required keys for a feature are present [agent_reach/config.py:199-202]().

| Feature name | Required keys |
|---|---|
| `exa_search` | `exa_api_key` |
| `twitter_xreach` | `twitter_auth_token`, `twitter_ct0` |
| `github_token` | `github_token` |
| `groq_whisper` | `groq_api_key` |

Sources: [agent_reach/config.py:106-112](), [agent_reach/config.py:199-202]()

---

# Page: Diagnostics and Monitoring

# Diagnostics and Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/doctor.py](agent_reach/doctor.py)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [docs/update.md](docs/update.md)
- [tests/test_cli.py](tests/test_cli.py)
- [tests/test_doctor.py](tests/test_doctor.py)

</details>



This page covers the three commands used to inspect and monitor the health of an Agent Reach installation: `agent-reach doctor`, `agent-reach watch`, and `agent-reach check-update`. These commands let you identify which channels are functional, detect configuration problems, and check for package updates.

For information on configuring credentials and proxies to resolve issues flagged by `doctor`, see [Configure Command](#2.4). For background on the channel tier system referenced in `doctor` output, see [Channel Architecture](#3.1).

---

## Overview

**Diagnostics flow diagram**

```mermaid
flowchart TD
    CLI["agent-reach CLI\ncli.main()"]
    
    CLI -->|"doctor"| cmd_doctor["_cmd_doctor()"]
    CLI -->|"watch"| cmd_watch["_cmd_watch()"]
    CLI -->|"check-update"| cmd_check_update["_cmd_check_update()"]

    cmd_doctor --> check_all["doctor.check_all(config)"]
    cmd_doctor --> format_report["doctor.format_report(results)"]
    cmd_watch --> check_all
    cmd_watch --> cmd_check_update

    check_all --> get_all_channels["channels.get_all_channels()"]
    get_all_channels --> ch_check["Channel.check(config)\n→ (status, message)"]

    ch_check --> results_dict["results: Dict[str, dict]\n{status, name, message, tier, backends, active_backend}"]
    results_dict --> format_report
    format_report --> stdout["stdout (text report)"]
```

Sources: [agent_reach/doctor.py:1-24](), [agent_reach/doctor.py:57-131](), [agent_reach/cli.py:12-25]()

---

## `agent-reach doctor`

### Purpose

`doctor` runs a health check across every registered channel and prints a tiered status report. It is the primary tool for diagnosing installation problems and verifying that channels are correctly configured.

### Implementation

The command handler is `_cmd_doctor()`. It:

1. Instantiates `Config()` to load `~/.agent-reach/config.yaml`.
2. Calls `check_all(config)` from `agent_reach/doctor.py` [agent_reach/doctor.py:16-45]().
3. Passes the result to `format_report(results)` and prints it [agent_reach/doctor.py:57-131]().

`check_all()` is the core diagnostic engine. It iterates over every channel returned by `get_all_channels()`, calls `ch.check(config)` on each, and assembles a results dict [agent_reach/doctor.py:23-25](). A critical design feature is the **isolation of channel failures**: if one channel raises an exception, it is caught and reported as an "error" status, preventing the entire diagnostic report from crashing [agent_reach/doctor.py:27-32]().

`doctor` also serves as a **security boundary**. Before rendering, it calls `scrub_url_credentials()` on all channel messages to ensure that any URLs containing passwords or tokens (leaked from backend error messages) are masked [agent_reach/doctor.py:33-36]().

### Status Indicators

| Status value | Display symbol | Meaning |
|---|---|---|
| `ok` | ✅ | Channel is fully functional [agent_reach/doctor.py:62]() |
| `warn` | [!] (Yellow) | Channel is partially available or requires config/login [agent_reach/doctor.py:62]() |
| `off` | [X] (Red) | Channel backend is not installed [agent_reach/doctor.py:62]() |
| `error` | [X] (Red) | Unexpected exception during health check [agent_reach/doctor.py:30]() |

### Multi-Backend Reporting

For platforms that support multiple backends (e.g., Twitter, Bilibili, Reddit), `doctor` identifies which specific backend is currently active [agent_reach/doctor.py:51-54](). This is retrieved via the `active_backend` attribute on the channel instance [agent_reach/doctor.py:26]().

### Security Check

`format_report()` performs a Unix-specific check on `config.yaml` permissions [agent_reach/doctor.py:114-129](). If the file is readable by group or others (violating the recommended `0o600`), a red alert is appended to the report with the specific fix: `chmod 600 ~/.agent-reach/config.yaml` [agent_reach/doctor.py:125-127]().

---

## `agent-reach watch`

### Purpose

`watch` is a combined health and update check designed for automation (e.g., cron jobs or AI agent status polling). It prints the standard `doctor` report followed by a version check [docs/update.md:90-108]().

### Automated Maintenance

AI agents are instructed to use `watch` to determine if maintenance is required [docs/update.md:19-27](). If `watch` reports a new version or a channel regression, the agent can initiate the update workflow.

---

## `agent-reach check-update`

### Purpose

`check-update` compares the local package version against the latest release on GitHub [docs/update.md:29-35](). It is used to trigger the `pip install --upgrade` workflow.

### Update Workflow

The standardized update process is documented in `docs/update.md`:
1. **Check**: `agent-reach check-update` [docs/update.md:31-33]().
2. **Upgrade**: `pip install --upgrade https://github.com/Panniantong/agent-reach/archive/main.zip` [docs/update.md:40]().
3. **Refresh Tools**: Update upstream CLIs like `twitter-cli`, `bilibili-cli`, and `mcporter` [docs/update.md:48-67]().
4. **Verify**: Run `agent-reach doctor` to confirm the environment is healthy [docs/update.md:92]().

---

## Troubleshooting Guide

The codebase includes a troubleshooting guide for common failures [docs/troubleshooting.md:1-67]():

### bird/twitter-cli Failures
**Symptom**: Twitter search returns errors or `doctor` shows `[!]`.
**Resolution**:
- **Authentication**: Ensure `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` are exported in the environment [docs/troubleshooting.md:32-34]().
- **Proxy**: If X.com is blocked, set `HTTP_PROXY` or use a global proxy tool like `proxychains` [docs/troubleshooting.md:35-48]().
- **Alternative**: Switch to the Exa-based Twitter search fallback via `mcporter` [docs/troubleshooting.md:50-57]().

### Xueqiu 400 Errors
**Symptom**: `doctor` reports `HTTP Error 400` for Xueqiu.
**Cause**: The API requires valid session cookies.
**Fix**: Use `agent-reach configure --from-browser chrome --platform xueqiu` to refresh the session [docs/troubleshooting.md:9-15]().

---

## Implementation Details

**Doctor Logic flow**

```mermaid
sequenceDiagram
    participant CLI as "cli._cmd_doctor"
    participant Doctor as "doctor.check_all"
    participant Channel as "Channel Instance"
    participant Utils as "utils.text.scrub_url_credentials"

    CLI->>Doctor: check_all(config)
    loop for each ch in ALL_CHANNELS
        Doctor->>Channel: ch.check(config)
        Channel-->>Doctor: (status, message)
        Doctor->>Channel: get active_backend
        Doctor->>Utils: scrub(message)
        Utils-->>Doctor: clean_message
    end
    Doctor-->>CLI: results_dict
```

Sources: [agent_reach/doctor.py:16-45](), [tests/test_doctor.py:18-31]()

### Tests

Diagnostic logic is verified in `tests/test_doctor.py`:
- **Isolation**: `test_stale_active_backend_does_not_leak_into_errored_result` ensures that if a channel check fails, it doesn't report the backend from a previous successful run [tests/test_doctor.py:117-135]().
- **Security**: `test_channel_exception_credentials_are_scrubbed` verifies that secrets in exception messages are redacted [tests/test_doctor.py:137-162]().
- **Formatting**: `test_format_report` checks the `rich` output structure [tests/test_doctor.py:80-115]().

Sources: [tests/test_doctor.py:1-212]()

---

# Page: Channels

# Channels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/__init__.py](agent_reach/channels/__init__.py)
- [agent_reach/channels/base.py](agent_reach/channels/base.py)
- [agent_reach/channels/instagram.py](agent_reach/channels/instagram.py)
- [agent_reach/channels/rss.py](agent_reach/channels/rss.py)
- [tests/test_channel_contracts.py](tests/test_channel_contracts.py)

</details>



This page describes what channels are, how they are registered and selected at runtime, and the full list of supported platforms with their tier requirements. For the abstract `Channel` base class interface and the `active_backend` logic, see [Channel Architecture](#3.1).

---

## What Is a Channel?

A **channel** is a Python module in `agent_reach/channels/` that wraps an external tool, CLI, or API to expose standardized operations. Every channel implements the `Channel` abstract base class.

- **`can_handle(url)`** — returns `True` if the channel can process the given URL based on domain or pattern matching.
- **`check(config)`** — performs a health check to see if dependencies (CLIs, APIs, cookies) are available and sets `active_backend`.
- **`ordered_backends(config)`** — returns the list of supported backends, prioritizing user overrides from `config.yaml`.

The design philosophy emphasizes **pluggable backends**: the platform (e.g., Twitter) is decoupled from the tool (e.g., `bird` CLI or Jina Reader).

Sources: [agent_reach/channels/base.py:1-23](), [agent_reach/channels/base.py:29-60]()

---

## Channel Registry

All channels are registered in `agent_reach/channels/__init__.py`. The order in the `ALL_CHANNELS` list determines the priority for URL routing. For instance, the `WebChannel` is placed last to act as a catch-all fallback.

**`ALL_CHANNELS`** — the ordered routing list:

```python
ALL_CHANNELS: List[Channel] = [
    GitHubChannel(),
    TwitterChannel(),
    YouTubeChannel(),
    RedditChannel(),
    FacebookChannel(),
    InstagramChannel(),
    BilibiliChannel(),
    XiaoHongShuChannel(),
    LinkedInChannel(),
    XiaoyuzhouChannel(),
    V2EXChannel(),
    XueqiuChannel(),
    RSSChannel(),
    ExaSearchChannel(),
    WebChannel(),
]
```

Sources: [agent_reach/channels/__init__.py:26-42](), [agent_reach/channels/base.py:13-16]()

---

## URL Routing and Lookup

When the system needs to process a URL, it iterates through the registry to find the appropriate handler.

**Figure 1: URL dispatch path from Natural Language Space to Code Entity Space**

```mermaid
flowchart TD
    subgraph "Natural Language Space"
        URL["'https://v2ex.com/t/123'"]
    end

    subgraph "Code Entity Space (agent_reach/channels/__init__.py)"
        INIT["ALL_CHANNELS"]
        V2EX["V2EXChannel.can_handle(url)"]
        RSS["RSSChannel.can_handle(url)"]
        WEB["WebChannel.can_handle(url)"]
    end

    URL --> INIT
    INIT -->|"iterates"| V2EX
    V2EX -->|"returns True"| MATCH["V2EXChannel Selected"]
    V2EX -.->|"if False"| RSS
    RSS -.->|"if False"| WEB
```

**Figure 2: Named channel lookup for platform-specific search**

```mermaid
flowchart LR
    subgraph "CLI/Agent Request"
        REQ["get_channel('instagram')"]
    end

    subgraph "agent_reach/channels/__init__.py"
        GC["get_channel(name)"]
        AC["ALL_CHANNELS"]
    end

    subgraph "agent_reach/channels/instagram.py"
        IC["InstagramChannel"]
    end

    REQ --> GC
    GC --> AC
    AC -->|"find name == 'instagram'"| IC
```

Sources: [agent_reach/channels/__init__.py:45-50](), [tests/test_channel_contracts.py:166-176]()

---

## Tier Classification

Channels are classified into tiers (`Channel.tier`) based on their configuration complexity.

| Tier | Label | Meaning | Examples |
|------|-------|---------|---------|
| 0 | Zero-config | Works immediately via public APIs or standard tools | `GitHubChannel`, `V2EXChannel`, `RSSChannel`, `WebChannel` |
| 1 | Needs Key/Setup | Requires an API key (Exa) or a specific CLI setup | `ExaSearchChannel`, `RedditChannel`, `XiaoyuzhouChannel` |
| 2 | Needs Account | Requires authenticated cookies or session tokens | `XiaoHongShuChannel`, `InstagramChannel`, `LinkedInChannel` |

Sources: [agent_reach/channels/base.py:35](), [agent_reach/channels/rss.py:11](), [agent_reach/channels/instagram.py:7-13](), [tests/test_channel_contracts.py:25]()

---

## Supported Platforms

| Platform | Channel Class | Channel Name | Tier | Primary Backend(s) |
|----------|--------------|--------------|------|-----------------|
| 📦 GitHub | `GitHubChannel` | `github` | 0 | `gh` CLI |
| 🐦 Twitter/X | `TwitterChannel` | `twitter` | 0 | `bird` CLI, Jina |
| 📺 YouTube | `YouTubeChannel` | `youtube` | 0 | `yt-dlp` |
| 📖 Reddit | `RedditChannel` | `reddit` | 1 | `rdt-cli`, OpenCLI |
| 👥 Facebook | `FacebookChannel` | `facebook` | 2 | OpenCLI |
| 📸 Instagram | `InstagramChannel` | `instagram` | 2 | OpenCLI |
| 📺 Bilibili | `BilibiliChannel` | `bilibili` | 1 | `bili-cli`, OpenCLI |
| 📕 XiaoHongShu | `XiaoHongShuChannel` | `xiaohongshu` | 2 | `mcporter` (XHS MCP) |
| 💼 LinkedIn | `LinkedInChannel` | `linkedin` | 2 | `mcporter` (LinkedIn MCP) |
| 🎙️ 小宇宙 | `XiaoyuzhouChannel` | `xiaoyuzhou` | 1 | Groq Whisper |
| 🟢 V2EX | `V2EXChannel` | `v2ex` | 0 | Public API |
| 📈 雪球 | `XueqiuChannel` | `xueqiu` | 0 | Public API |
| 📰 RSS | `RSSChannel` | `rss` | 0 | `feedparser` |
| 🔍 Exa Search | `ExaSearchChannel` | `exa_search` | 1 | `mcporter` (Exa MCP) |
| 🌐 Web | `WebChannel` | `web` | 0 | Jina Reader |

Sources: [agent_reach/channels/__init__.py:26-42](), [agent_reach/channels/instagram.py:7-13](), [agent_reach/channels/rss.py:7-11]()

---

## Detailed Channel Documentation

- [Channel Architecture](#3.1) — The `Channel` base class, `active_backend` logic, and `probe_command` utility.
- [Twitter Channel](#3.2) — Twitter-specific logic using the `bird` CLI and Jina fallbacks.
- [YouTube and Bilibili Channels](#3.3) — Video platforms using `yt-dlp` and `bili-cli`.
- [GitHub Channel](#3.4) — Repository and issue reading via `gh` CLI.
- [Reddit Channel](#3.5) — Community reading via `rdt-cli` and proxy handling.
- [Web and RSS Channels](#3.6) — Fallback web reading and feed parsing via `feedparser`.
- [XiaoHongShu Channel](#3.7) — MCP-based integration for notes and search.
- [Exa Search Channel](#3.8) — Semantic web search integration via MCP.
- [Facebook, Instagram, and LinkedIn Channels](#3.9) — Browser-bridge channels using `OpenCLISiteChannel`.
- [Xiaoyuzhou, V2EX, and Xueqiu Channels](#3.10) — Podcast transcription and public financial/community APIs.

---

# Page: Channel Architecture

# Channel Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/__init__.py](agent_reach/channels/__init__.py)
- [agent_reach/channels/base.py](agent_reach/channels/base.py)
- [agent_reach/channels/instagram.py](agent_reach/channels/instagram.py)
- [agent_reach/channels/rss.py](agent_reach/channels/rss.py)
- [agent_reach/probe.py](agent_reach/probe.py)
- [tests/test_channel_contracts.py](tests/test_channel_contracts.py)
- [tests/test_probe.py](tests/test_probe.py)

</details>



This page documents the internal architecture of the channels subsystem: the `Channel` abstract base class, the `OpenCLISiteChannel` helper, the routing logic in `ALL_CHANNELS`, and the `probe_command` utility for robust health diagnostics.

---

## Overview

Every platform integration in Agent Reach is a `Channel` — a class that implements a common interface and wraps specific external backend tools or APIs. The channel system has four primary responsibilities:

1.  **URL Routing**: Determining which channel handles a given URL via `can_handle()`.
2.  **Health Reporting**: Reporting whether the channel's dependencies (tools, APIs, or configs) are satisfied via `check()`.
3.  **Backend Prioritization**: Managing multiple candidate backends (e.g., CLI vs. HTTP API) via `ordered_backends()`.
4.  **Data Fetching**: Providing structured access to platform-specific data.

All channels live under `agent_reach/channels/`. The abstract contract is defined in `agent_reach/channels/base.py`, and the registry that connects everything is in `agent_reach/channels/__init__.py`.

Sources: [agent_reach/channels/base.py:1-23](), [agent_reach/channels/__init__.py:1-9]()

---

## The `Channel` Abstract Base Class

**File:** [agent_reach/channels/base.py:29-70]()

Every channel subclasses `Channel` and must implement the `can_handle` abstract method.

### Class-Level Attributes

| Attribute | Type | Purpose |
| :--- | :--- | :--- |
| `name` | `str` | Unique identifier (e.g. `"youtube"`, `"twitter"`) [agent_reach/channels/base.py:32]() |
| `description` | `str` | Human-readable summary of the platform [agent_reach/channels/base.py:33]() |
| `backends` | `List[str]` | **Ordered** list of candidate tools; `backends[0]` is the preferred primary. [agent_reach/channels/base.py:34]() |
| `tier` | `int` | Setup complexity: `0`=zero-config, `1`=needs key/CLI, `2`=needs browser/MCP [agent_reach/channels/base.py:35]() |
| `active_backend` | `Optional[str]` | The backend currently serving the channel; set during `check()`. [agent_reach/channels/base.py:38]() |

### Core Methods

**`can_handle(url: str) -> bool`**  
Abstract method to determine if a URL belongs to this platform. [agent_reach/channels/base.py:41-43]()

**`ordered_backends(config=None) -> List[str]`**  
Returns backends in probe order. It honors user overrides via config keys like `<channel>_backend` (e.g., `twitter_backend: "bird"`), which moves the requested backend to the front of the list. [agent_reach/channels/base.py:45-60]()

**`check(config=None) -> Tuple[str, str]`**  
Performs health diagnostics. Subclasses are expected to use `probe_command` to verify that backends are not just present on the `PATH`, but are actually executable. [agent_reach/channels/base.py:61-70]()

---

**Diagram: Channel Class Interface and Backend Selection**

```mermaid
classDiagram
    class Channel {
        <<abstract>>
        +name: str
        +description: str
        +backends: List~str~
        +active_backend: str
        +tier: int
        +can_handle(url: str) bool*
        +ordered_backends(config) List~str~
        +check(config) Tuple~str,str~
    }
    class OpenCLISiteChannel {
        +site: str
        +domains: Tuple~str~
        +check(config) Tuple~str,str~
    }
    class TwitterChannel {
        +can_handle(url) bool
    }
    
    Channel <|-- OpenCLISiteChannel
    OpenCLISiteChannel <|-- TwitterChannel
    
    note for Channel "Base logic in\nagent_reach/channels/base.py"
    note for OpenCLISiteChannel "Browser-session helper in\nagent_reach/channels/_opencli_site.py"
```

Sources: [agent_reach/channels/base.py:29-70](), [agent_reach/channels/twitter.py:1-20](), [tests/test_channel_contracts.py:86-98]()

---

## Health Probing with `probe_command`

Agent Reach distinguishes between a tool being "missing" and "broken" (e.g., a stale venv after a Python upgrade). The `probe_command` utility in `agent_reach/probe.py` is used by channels to verify backend health.

### Probe Failure Modes
*   **`missing`**: Command not found on `PATH`. [agent_reach/probe.py:68-69]()
*   **`broken`**: Command exists but `exec` fails (e.g., stale shebang) or returns exit code 126/127. [agent_reach/probe.py:106-115]()
*   **`timeout`**: Command runs but does not respond within the timeout (default 10s). [agent_reach/probe.py:111-112]()
*   **`error`**: Command runs but returns a non-zero exit code. [agent_reach/probe.py:118-119]()
*   **`ok`**: Command returns exit code 0. [agent_reach/probe.py:120]()

Sources: [agent_reach/probe.py:27-36](), [agent_reach/probe.py:47-66]()

---

## OpenCLISiteChannel Helper

For platforms that rely on a logged-in browser session (Facebook, Instagram, etc.), the `OpenCLISiteChannel` provides a shared implementation. It uses the `opencli` tool to bridge the browser session to the CLI.

*   **Shared Check**: It probes `opencli` and checks the specific site status. [agent_reach/channels/instagram.py:7-13]()
*   **Usage Guidance**: Provides specific `login_hint` and `usage` strings to help users configure the browser session. [agent_reach/channels/instagram.py:12-13]()

---

## Channel Registry and Routing

`ALL_CHANNELS` is an ordered list in `agent_reach/channels/__init__.py`. The system iterates this list; the first channel whose `can_handle(url)` returns `True` is selected.

**Registry Order (Routing Priority):**
1.  `GitHubChannel`
2.  `TwitterChannel`
3.  `YouTubeChannel`
4.  `RedditChannel`
5.  `FacebookChannel`
6.  `InstagramChannel`
7.  `BilibiliChannel`
8.  `XiaoHongShuChannel`
9.  `LinkedInChannel`
10. `XiaoyuzhouChannel`
11. `V2EXChannel`
12. `XueqiuChannel`
13. `RSSChannel`
14. `ExaSearchChannel`
15. `WebChannel` (Catch-all Fallback)

Sources: [agent_reach/channels/__init__.py:26-42]()

---

**Diagram: URL Routing to Code Entities**

```mermaid
flowchart TD
    A["Input URL: https://x.com/..."] --> B["ALL_CHANNELS Registry\n(agent_reach/channels/__init__.py)"]
    B --> C{"Dispatch Loop"}
    C --> D["GitHubChannel.can_handle()"]
    D -- "False" --> E["TwitterChannel.can_handle()"]
    E -- "True" --> F["TwitterChannel Instance"]
    
    F --> G["check(config)"]
    G --> H["probe_command('bird')"]
    H -- "Status: ok" --> I["Set active_backend = 'bird'"]
    
    subgraph "Natural Language Space"
    A
    end

    subgraph "Code Entity Space"
    B
    E
    F
    H
    end
```

Sources: [agent_reach/channels/__init__.py:26-50](), [agent_reach/probe.py:47-55](), [agent_reach/channels/base.py:61-70]()

---

## Tier Classification

The `tier` attribute defines the expected environment complexity for the channel.

| Tier | Classification | Requirements | Examples |
| :--- | :--- | :--- | :--- |
| **0** | **Zero-Config** | No external tools or keys needed. | `RSSChannel` [rss.py:11](), `V2EXChannel` [v2ex.py:19]() |
| **1** | **Needs Setup** | Requires standalone CLI tools or free keys. | `GitHubChannel`, `YouTubeChannel` |
| **2** | **Complex** | Requires browser sessions, MCP, or Docker. | `XiaoHongShuChannel`, `InstagramChannel` |

Sources: [agent_reach/channels/base.py:35](), [agent_reach/channels/rss.py:11](), [tests/test_channel_contracts.py:25]()

---

# Page: Twitter Channel

# Twitter Channel

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/twitter.py](agent_reach/channels/twitter.py)
- [agent_reach/core.py](agent_reach/core.py)
- [agent_reach/guides/setup-twitter.md](agent_reach/guides/setup-twitter.md)
- [agent_reach/integrations/mcp_server.py](agent_reach/integrations/mcp_server.py)
- [tests/test_twitter_channel.py](tests/test_twitter_channel.py)

</details>



This page documents `TwitterChannel`, the channel implementation for reading and searching Twitter/X content. It covers the transition to `twitter-cli` as the primary backend, legacy `bird` support, `OpenCLI` bridge integration, and the cookie authentication policy designed to avoid automated browser fallback.

---

## Overview

`TwitterChannel` is defined in [agent_reach/channels/twitter.py:34-142]() and handles all URLs on `x.com` and `twitter.com` [agent_reach/channels/twitter.py:40-41](). It is classified as **tier 1** [agent_reach/channels/twitter.py:38-38](). The channel supports multiple backends in an ordered preference list: `twitter-cli`, `OpenCLI`, and `bird CLI (legacy)` [agent_reach/channels/twitter.py:37-37]().

| Property | Value |
|---|---|
| `name` | `"twitter"` [agent_reach/channels/twitter.py:35-35]() |
| `tier` | `1` [agent_reach/channels/twitter.py:38-38]() |
| `backends` | `twitter-cli`, `OpenCLI`, `bird CLI` [agent_reach/channels/twitter.py:37-37]() |
| URL match | `x.com`, `twitter.com` [agent_reach/channels/twitter.py:41-41]() |

**Feature availability by configuration:**

| State | Read single tweet | Search | Timeline |
|---|---|---|---|
| No CLI, no cookies | ⚠️ (Jina fallback) | ⚠️ (Exa fallback) | ❌ |
| `twitter-cli` installed, no cookies | ⚠️ (Auth required) | ⚠️ (Auth required) | ❌ |
| `twitter-cli` + valid cookies | ✅ | ✅ | ✅ |

Sources: [agent_reach/channels/twitter.py:34-41](), [agent_reach/guides/setup-twitter.md:1-12]()

---

## Architecture

The `TwitterChannel` employs a two-stage backend selection process. It probes candidates in order; the first "fully-usable" (`ok`) backend wins. If no backend is fully verified, it selects the first `warn` candidate to provide feedback to the user [agent_reach/channels/twitter.py:43-71]().

**Diagram: TwitterChannel — Backends and Fallback Paths**

```mermaid
flowchart TD
    A["TwitterChannel.check()"] --> B{"Backend Loop\n(ordered_backends)"}
    B -- 1 --> C["twitter-cli"]
    B -- 2 --> D["OpenCLI"]
    B -- 3 --> E["bird CLI (legacy)"]
    
    C --> C1{"twitter in PATH?"}
    C1 -- "No" --> NEXT["Try Next"]
    C1 -- "Yes" --> C2{"Explicit Auth\nin Config/Env?"}
    C2 -- "Yes" --> C3["Status: warn\n(Manual verification req)"]
    
    D --> D1{"opencli_status()"}
    D1 -- "Ready" --> D2["Status: warn\n(Bridge connected)"]
    
    E --> E1{"bird in PATH?"}
    E1 -- "Yes" --> E2["Status: warn"]
    
    C3 --> WIN["Select Active Backend"]
    D2 --> WIN
    
    WIN --> F["Final Status: ok/warn/error"]
```

Sources: [agent_reach/channels/twitter.py:43-81](), [agent_reach/channels/twitter.py:83-142](), [tests/test_twitter_channel.py:138-154]()

---

**Diagram: Code Entities and Data Flow**

```mermaid
graph LR
    subgraph "agent_reach/channels/twitter.py"
        TC["TwitterChannel"]
        TCE["twitter_cli_child_env()"]
        TC_CHECK["_check_twitter_cli()"]
    end

    subgraph "External CLI Tools"
        TCLI["twitter-cli\n(upstream)"]
        BIRD["bird CLI\n(legacy)"]
    end

    subgraph "Configuration"
        CONF["Config.yaml"]
        ENV["os.environ"]
    end

    TC --> TC_CHECK
    TC_CHECK --> TCE
    TCE -- "reads" --> CONF
    TCE -- "reads" --> ENV
    TCE -- "provides" --> TCLI
    
    TC -- "fallback" --> JINA["Jina Reader"]
```

Sources: [agent_reach/channels/twitter.py:12-31](), [agent_reach/channels/twitter.py:83-109](), [agent_reach/guides/setup-twitter.md:62-65]()

---

## Authentication and Security Policy

`TwitterChannel` enforces a strict **Cookie-Editor-only policy**. To prevent unexpected browser automation or credential leakage, `agent-reach doctor` does not execute upstream `status` commands (like `twitter status`) because these tools often automatically fall back to reading local browser cookies if explicit credentials fail [agent_reach/channels/twitter.py:86-89](), [agent_reach/channels/twitter.py:133-136]().

### Credential Mapping
Credentials can be provided via environment variables or the `agent-reach configure` command [agent_reach/guides/setup-twitter.md:39-46]().

| Backend | Token 1 | Token 2 | Config Key |
|---|---|---|---|
| `twitter-cli` | `TWITTER_AUTH_TOKEN` | `TWITTER_CT0` | `twitter_auth_token` / `twitter_ct0` |
| `bird` (legacy) | `AUTH_TOKEN` | `CT0` | (via Env) |

The helper function `twitter_cli_child_env` ensures that shell environment variables remain authoritative over the configuration file [agent_reach/channels/twitter.py:12-31]().

Sources: [agent_reach/channels/twitter.py:12-31](), [agent_reach/channels/twitter.py:93-98](), [tests/test_twitter_channel.py:57-71]()

---

## Health Check and Diagnostics

The `check()` method implements specific logic for each backend to verify installation without triggering network requests:

1. **twitter-cli:** Checks `shutil.which("twitter")`. If found, it checks for `auth_token` and `ct0` in the environment or config. It returns `warn` rather than `ok` to indicate that while the tool is ready, the login state has not been live-verified [agent_reach/channels/twitter.py:83-109]().
2. **OpenCLI:** Utilizes `opencli_status()` to check if the bridge extension is connected. Even if connected, it returns `warn` because Twitter-specific commands are not verified in real-time [agent_reach/channels/twitter.py:111-125]().
3. **bird CLI:** Scans for `bird` or `birdx`. It similarly avoids running `check` to prevent browser cookie fallback [agent_reach/channels/twitter.py:127-142]().

Sources: [agent_reach/channels/twitter.py:43-81](), [tests/test_twitter_channel.py:18-29](), [tests/test_twitter_channel.py:122-136]()

---

## Proxy Support

`twitter-cli` supports standard proxy environment variables. Because it is a Node.js application, users may need to explicitly export these variables or use wrapper tools if the system-wide proxy is not inherited by the Node process [agent_reach/guides/setup-twitter.md:85-99]().

```bash
export HTTP_PROXY="http://user:pass@host:port"
export HTTPS_PROXY="http://user:pass@host:port"
twitter search "test" -n 1
```

Alternatively, `proxychains` can be used to wrap the execution [agent_reach/guides/setup-twitter.md:98-99]().

Sources: [agent_reach/guides/setup-twitter.md:85-99]()

---

## Integration via MCP

The Twitter channel's status is exposed to AI agents through the Model Context Protocol (MCP) server defined in `agent_reach/integrations/mcp_server.py`. The `get_status` tool allows agents to verify if the Twitter backend is correctly configured before attempting a search or read operation [agent_reach/integrations/mcp_server.py:43-55]().

```python
@server.list_tools()
async def list_tools():
    return [
        Tool(name="get_status",
             description="Get Agent Reach status: which channels are installed and active.",
             inputSchema={"type": "object", "properties": {}}),
    ]
```

Sources: [agent_reach/integrations/mcp_server.py:43-55](), [agent_reach/core.py:34-37]()

---

# Page: YouTube and Bilibili Channels

# YouTube and Bilibili Channels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/bilibili.py](agent_reach/channels/bilibili.py)
- [agent_reach/channels/reddit.py](agent_reach/channels/reddit.py)
- [agent_reach/channels/youtube.py](agent_reach/channels/youtube.py)
- [agent_reach/utils/text.py](agent_reach/utils/text.py)
- [tests/test_paths.py](tests/test_paths.py)
- [tests/test_youtube_channel.py](tests/test_youtube_channel.py)

</details>



This page documents `YouTubeChannel` and `BilibiliChannel`: the two primary video platform channels in Agent Reach. While `YouTubeChannel` leverages `yt-dlp` as its core backend, `BilibiliChannel` utilizes a multi-backend strategy involving `bili-cli`, `OpenCLI`, and raw API fallbacks to navigate aggressive platform risk controls.

---

## Overview

| Property | `YouTubeChannel` | `BilibiliChannel` |
|---|---|---|
| File | [agent_reach/channels/youtube.py:39-118]() | [agent_reach/channels/bilibili.py:35-119]() |
| Class | `YouTubeChannel` | `BilibiliChannel` |
| `name` | `"youtube"` | `"bilibili"` |
| `tier` | `0` (Zero-config) | `1` (Needs Setup) |
| Backends | `yt-dlp` | `bili-cli`, `OpenCLI`, `B站搜索 API` |
| `can_handle` domains | `youtube.com`, `youtu.be` | `bilibili.com`, `b23.tv` |
| Key Requirement | JS Runtime (Node/Deno) | `bili-cli` or browser bridge |

Sources: [agent_reach/channels/youtube.py:39-48](), [agent_reach/channels/bilibili.py:35-44]()

---

## Architecture

The following diagrams map the natural language requirements for video processing to the specific code entities and data flows that implement them.

**Diagram: Video Channel Code Entities**

```mermaid
classDiagram
    class Channel {
        <<abstract>>
        +can_handle(url) bool
        +check(config) tuple
        +ordered_backends(config) list
    }

    class YouTubeChannel {
        +name = "youtube"
        +tier = 0
        +backends = ["yt-dlp"]
        +transcribe(url, provider) str
    }

    class BilibiliChannel {
        +name = "bilibili"
        +tier = 1
        +backends = ["bili-cli", "OpenCLI", "B站搜索 API"]
    }

    Channel <|-- YouTubeChannel
    Channel <|-- BilibiliChannel

    class YouTubeProbe {
        +probe_command("yt-dlp")
        +shutil.which("node")
        +shutil.which("deno")
        +_has_js_runtime_config()
    }

    class BilibiliProbe {
        +probe_command("bili")
        +opencli_status()
        +_search_api_ok()
    }

    YouTubeChannel ..> YouTubeProbe : uses
    BilibiliChannel ..> BilibiliProbe : uses
```

Sources: [agent_reach/channels/youtube.py:39-52](), [agent_reach/channels/bilibili.py:35-84](), [agent_reach/channels/base.py:15-22]()

---

## YouTube Channel

The `YouTubeChannel` focuses on extracting video information and subtitles using `yt-dlp`. A critical requirement for YouTube is the presence of a JavaScript runtime, as `yt-dlp` requires it to solve signature challenges [agent_reach/channels/youtube.py:2-3]().

### Runtime Requirements
The `check()` method [agent_reach/channels/youtube.py:50-118]() performs a multi-step validation:
1. **Binary Check**: Uses `probe_command` to verify `yt-dlp` is executable [agent_reach/channels/youtube.py:52-65]().
2. **JS Runtime Check**: Looks for `deno` (works out of the box) or `node` [agent_reach/channels/youtube.py:69-77]().
3. **Configuration Check**: If using Node.js, it checks `yt-dlp`'s config file for the `--js-runtimes node` flag [agent_reach/channels/youtube.py:78-80]().
4. **Version Check**: Ensures `yt-dlp` is newer than version `2025.11.12` to support JS runtimes [agent_reach/channels/youtube.py:17-18](), [agent_reach/channels/youtube.py:88-92]().

### Transcription Pipeline
YouTube supports audio transcription via external providers (Groq/OpenAI). The `transcribe()` method [agent_reach/channels/youtube.py:120-141]() delegates to the core transcription utility. `doctor` reports readiness if `ffmpeg`/`ffprobe` are present and a provider is configured [agent_reach/channels/youtube.py:98-117]().

Sources: [agent_reach/channels/youtube.py:50-96](), [agent_reach/channels/youtube.py:120-141](), [tests/test_youtube_channel.py:4-11]()

---

## Bilibili Channel

The `BilibiliChannel` handles video content and search. Notably, `yt-dlp` was **removed** as a Bilibili backend because platform risk control (412 errors) consistently blocks its requests [agent_reach/channels/bilibili.py:4-9]().

### Multi-Backend Strategy
The channel probes backends in order of capability [agent_reach/channels/bilibili.py:51-60]():
1. **bili-cli**: Primary backend for search, hot topics, and video details without login [agent_reach/channels/bilibili.py:82-94]().
2. **OpenCLI**: Fallback for subtitles, leveraging a logged-in browser session [agent_reach/channels/bilibili.py:96-110]().
3. **B站搜索 API**: Final fallback for basic search using direct `urllib` requests [agent_reach/channels/bilibili.py:112-119]().

**Diagram: Bilibili Backend Resolution**

```mermaid
flowchart TD
    Start["BilibiliChannel.check()"] --> Loop["For backend in ordered_backends"]
    Loop --> BiliCLI{"bili-cli?"}
    BiliCLI -- "Yes" --> ProbeBili["probe_command('bili')"]
    BiliCLI -- "No" --> OpenCLI{"OpenCLI?"}
    
    OpenCLI -- "Yes" --> ProbeOCLI["opencli_status()"]
    OpenCLI -- "No" --> SearchAPI["_search_api_ok()"]
    
    ProbeBili --> Eval{Is usable?}
    ProbeOCLI --> Eval
    SearchAPI --> Eval
    
    Eval -- "Yes (ok/warn)" --> SetActive["active_backend = backend"]
    Eval -- "No" --> Loop
    
    SetActive --> Return["Return Status"]
```

### Connectivity Detection
- **_search_api_ok()**: Attempts a direct request to the Bilibili search API [agent_reach/channels/bilibili.py:24-32]().
- **OpenCLI Ready**: Checks if the OpenCLI bridge is connected, though it does not verify Bilibili login state during `doctor` to avoid side effects [agent_reach/channels/bilibili.py:105-109]().

Sources: [agent_reach/channels/bilibili.py:46-80](), [agent_reach/channels/bilibili.py:82-119]()

---

## Configuration and Remediation

### yt-dlp Fixes
If `yt-dlp` lacks a JS runtime on YouTube, the system provides a remediation command [agent_reach/channels/youtube.py:94](). The helper `render_ytdlp_fix_command()` generates a shell command to append `--js-runtimes node` to the user's config file [agent_reach/utils/paths.py:12-13](), [tests/test_paths.py:13-31]().

### Proxy and Secrets
For Bilibili, network issues may require proxies. The system also includes text helpers to scrub sensitive information (tokens, credentials) from URLs before logging or processing [agent_reach/utils/text.py:24-28]().

| Feature | YouTube Detail | Bilibili Detail |
|---|---|---|
| **Subtitles** | Handled by `yt-dlp` | Handled by `OpenCLI` |
| **Search** | via `yt-dlp` | via `bili-cli` or API |
| **Remediation** | `agent-reach install --system` | `pipx install bilibili-cli` |

Sources: [agent_reach/channels/youtube.py:73-74](), [agent_reach/channels/bilibili.py:78-79](), [agent_reach/utils/text.py:1-28]()

---

# Page: GitHub Channel

# GitHub Channel

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/github.py](agent_reach/channels/github.py)
- [agent_reach/guides/setup-exa.md](agent_reach/guides/setup-exa.md)
- [agent_reach/guides/setup-reddit.md](agent_reach/guides/setup-reddit.md)

</details>



This page documents the `GitHubChannel` class: its backend tool (`gh CLI`), URL routing logic, read and search behavior, authentication states, and the `WebChannel` fallback path. For general channel architecture concepts (base class, `ReadResult`, `SearchResult`, registration), see [Channel Architecture](3.1).

---

## Overview

`GitHubChannel` handles all URLs on `github.com` [agent_reach/channels/github.py:101-104](). It is a **tier-0** channel [agent_reach/channels/github.py:99](): public repository reading and search work immediately after `gh CLI` is installed. 

The backend is the official [`gh CLI`](https://cli.github.com) [agent_reach/channels/github.py:98](). To ensure privacy and prevent unwanted side effects during diagnostics, the channel uses a "read-only" environment configuration that disables telemetry and update notifiers [agent_reach/channels/github.py:20-27]().

---

## Implementation Location

| Item | Value |
|---|---|
| Source file | `agent_reach/channels/github.py` |
| Class | `GitHubChannel` |
| `name` | `"github"` |
| `tier` | `0` |
| `backends` | `["gh CLI"]` |
| Primary CLI | `gh` |

Sources: [agent_reach/channels/github.py:95-99]()

---

## URL Routing

The `can_handle` method matches any URL whose host contains `github.com`. It utilizes the `host_matches` utility to validate the domain [agent_reach/channels/github.py:101-104]().

**Natural Language to Code Entity Space: URL Dispatch**

```mermaid
flowchart TD
    url["'https://github.com/Panniantong/Agent-Reach'"]
    can_handle["GitHubChannel.can_handle(url)"]
    host_matches["host_matches(url, 'github.com')"]
    match{"Match?"}
    
    url --> can_handle
    can_handle --> host_matches
    host_matches --> match
    match -- "True" --> handle["Channel Selected"]
    match -- "False" --> next["Try Next Channel"]
```

Sources: [agent_reach/channels/github.py:101-104]()

---

## Authentication and Health Check

The `check()` method determines channel health by probing the `gh` binary and inspecting local configuration files without executing commands that write to the disk (like `gh auth status`, which creates a `device-id` file) [agent_reach/channels/github.py:106-145]().

**System State to Code Entity Space: Health Check**

```mermaid
flowchart TD
    check["GitHubChannel.check(config)"]
    probe["probe_command('gh', ['--version'])"]
    status{"probe.status?"}
    
    inspect["_explicit_github_credentials() OR _saved_github_host_configured()"]
    conf_res{"Configured?"}

    missing["'warn', 'gh CLI 未安装'"]
    broken["'error', '安装已损坏'"]
    warn_auth["'warn', '未检测到显式认证配置'"]
    warn_verify["'warn', '检测到配置但未实时验证'"]

    check --> probe
    probe --> status
    status -- "missing" --> missing
    status -- "broken" --> broken
    status -- "ok" --> inspect
    inspect --> conf_res
    conf_res -- "False" --> warn_auth
    conf_res -- "True" --> warn_verify
```

### Diagnostic Logic
1.  **CLI Availability**: Uses `probe_command` to check if `gh` is installed and functional [agent_reach/channels/github.py:108-114](). If missing, it suggests installation via the official site [agent_reach/channels/github.py:116]().
2.  **Configuration Inspection**:
    *   **Environment/Config**: `_explicit_github_credentials` checks for `GH_TOKEN` or `GITHUB_TOKEN` in environment variables or the Agent Reach `config.yaml` [agent_reach/channels/github.py:84-93]().
    *   **Filesystem**: `_saved_github_host_configured` reads the `hosts.yml` file used by `gh CLI` [agent_reach/channels/github.py:51-82](). It searches for the file in standard locations (XDG config, AppData, or `GH_CONFIG_DIR`) [agent_reach/channels/github.py:34-49]().
3.  **Auth Boundary**: To maintain a "read-only" diagnostic state, the channel does not run `gh auth status` because that command triggers telemetry and writes local state files [agent_reach/channels/github.py:133-145]().

Sources: [agent_reach/channels/github.py:34-145]()

---

## Read and Search Capabilities

The `GitHubChannel` leverages the `gh` CLI to provide structured data.

### Repository and Code Reading
The channel utilizes `gh repo view` to fetch repository metadata and README contents. It also supports deep links to issues and pull requests by wrapping `gh issue view` and `gh pr view`.

### Search Functionality
Search is implemented via `gh search repos`. It supports:
*   **Query**: Semantic or keyword search.
*   **Language Filter**: Restricting results to specific programming languages (e.g., `--lang python`).
*   **Result Limit**: Controlled via the `-n` flag in the CLI.

---

## WebChannel Fallback

If `gh CLI` is missing or the user is unauthenticated and attempting to access a public repository that `gh` fails to fetch, the system falls back to `WebChannel`. The `WebChannel` uses Jina Reader (`r.jina.ai`) to scrape the public GitHub web interface. This ensures that the agent can still "see" code and READMEs even without a local GitHub setup.

Sources: [agent_reach/channels/github.py:116](), [agent_reach/channels/github.py:142-145]() (Warning logic implying limited functionality without CLI).

---

## Comparison with Similar Channels

Unlike `RedditChannel` or `TwitterChannel`, which often require specific proxies or cookie exports to bypass anti-scraping, `GitHubChannel` relies on a standard developer tool (`gh`) that handles authentication via OAuth tokens.

| Feature | GitHub | Reddit | Twitter |
|---|---|---|---|
| **Primary Backend** | `gh CLI` | `rdt-cli` | `bird CLI` |
| **Auth Requirement** | OAuth Token / CLI Login | Browser Cookie | Browser Cookie |
| **Proxy Needed** | Rarely | Highly Recommended | Recommended |
| **Tier** | 0 | 1 | 1 |

Sources: [agent_reach/channels/github.py:98-99](), [agent_reach/guides/setup-reddit.md:7-11](), [agent_reach/guides/setup-exa.md:4-7]()

---

# Page: Reddit Channel

# Reddit Channel

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/bilibili.py](agent_reach/channels/bilibili.py)
- [agent_reach/channels/reddit.py](agent_reach/channels/reddit.py)
- [agent_reach/guides/setup-exa.md](agent_reach/guides/setup-exa.md)
- [agent_reach/guides/setup-reddit.md](agent_reach/guides/setup-reddit.md)
- [tests/test_reddit_channel.py](tests/test_reddit_channel.py)

</details>



This page documents `RedditChannel`: how it routes Reddit URLs, how it manages its multi-backend architecture (`OpenCLI` and `rdt-cli`), its mandatory login requirement, and how it handles recursive content extraction while navigating aggressive IP blocking.

---

## Overview

`RedditChannel` is a **Tier 1** channel providing access to Reddit posts and comments. Unlike other channels, it has **no zero-config path** [agent_reach/channels/reddit.py:4-10](). Reddit has blocked anonymous `.json` endpoints for data centers and restricted official API access; therefore, every backend used by this channel requires a logged-in session [agent_reach/channels/reddit.py:34]().

| Property | Value |
|---|---|
| Class | `RedditChannel` |
| File | `agent_reach/channels/reddit.py` |
| Tier | 1 (Login mandatory — no anonymous access) |
| Backends | `OpenCLI`, `rdt-cli` |
| URL patterns | `reddit.com`, `redd.it` |

Sources: [agent_reach/channels/reddit.py:30-34](), [agent_reach/guides/setup-reddit.md:5-11]()

---

## Architecture and Data Flow

The following diagram illustrates how `RedditChannel` bridges the Natural Language Space to the Code Entity Space, specifically focusing on the multi-backend selection logic.

**Diagram: Reddit Backend Selection and Validation**

```mermaid
flowchart TD
    subgraph "Natural Language Space"
        UserReq["'Read this Reddit thread'"]
        LoginNeed["'I need to authenticate'"]
    end

    subgraph "Code Entity Space: agent_reach/channels/reddit.py"
        RedditChannel["class RedditChannel"]
        can_handle["can_handle(url)"]
        check["check(config)"]
        check_rdt["_check_rdt()"]
        check_opencli["_check_opencli()"]
    end

    subgraph "Code Entity Space: External Backends"
        RDT["rdt-cli (via ~/.config/rdt-cli/credential.json)"]
        OpenCLI["OpenCLI (via browser bridge)"]
    end

    UserReq --> can_handle
    LoginNeed --> check
    check --> check_opencli
    check --> check_rdt
    check_rdt --> RDT
    check_opencli --> OpenCLI
```

Sources: [agent_reach/channels/reddit.py:30-53](), [agent_reach/channels/reddit.py:90-95]()

---

## URL Handling

### URL Matching
The `can_handle()` method identifies Reddit URLs by checking if the host matches `reddit.com` or `redd.it` using the `host_matches` utility [agent_reach/channels/reddit.py:36-39]().

### Backend Dispatch
The channel probes backends in order of preference. The first backend that returns an `ok` or `warn` status is selected as the `active_backend` [agent_reach/channels/reddit.py:43-60]().

Sources: [agent_reach/channels/reddit.py:36-60](), [tests/test_reddit_channel.py:11-20]()

---

## Backend Implementations

### 1. OpenCLI Backend
This is the recommended backend for desktop environments. It reuses the user's active Chrome/browser session. If the user is logged into Reddit in their browser, OpenCLI can bridge that session to the CLI [agent_reach/channels/reddit.py:66-68]().
- **Health Check**: `_check_opencli()` calls `opencli_status()` to verify the bridge is installed and connected [agent_reach/channels/reddit.py:74-88]().

### 2. rdt-cli Backend
Recommended for server environments. It is a specialized CLI for Reddit that imports session cookies [agent_reach/channels/reddit.py:69-70]().
- **Credential Safety**: The channel reads `~/.config/rdt-cli/credential.json` using `read_small_text_no_follow` to prevent symlink attacks [agent_reach/channels/reddit.py:95-101]().
- **Validation**: It checks for the existence of `reddit_session` in the cookie dictionary and verifies if the credentials are older than 7 days (`_CREDENTIAL_TTL_SECONDS`) [agent_reach/channels/reddit.py:121-128]().

Sources: [agent_reach/channels/reddit.py:74-136](), [tests/test_reddit_channel.py:66-87]()

---

## Health Check and Diagnostics

The `check()` method avoids executing live platform commands to prevent unwanted side effects, such as triggering automatic cookie refreshes that might invalidate sessions [agent_reach/channels/reddit.py:134-136]().

**Diagram: Health Check Decision Tree**

```mermaid
flowchart TD
    Start["RedditChannel.check()"]
    ProbeOpenCLI["_check_opencli()"]
    ProbeRDT["_check_rdt()"]
    
    ProbeOpenCLI -- "Ready" --> StatusWarnO["Status: 'warn'\nMsg: '桥接已连接，未实时验证'"]
    ProbeOpenCLI -- "Not Installed" --> ProbeRDT
    
    ProbeRDT -- "Cookie Found" --> StatusWarnR["Status: 'warn'\nMsg: '检测到 Cookie，未实时验证'"]
    ProbeRDT -- "No Cookie" --> LoginHint["Return 'off' + Login Hint"]
    
    StatusWarnO --> Active["active_backend = None (requires manual verify)"]
    StatusWarnR --> Active
```

Sources: [agent_reach/channels/reddit.py:41-72](), [tests/test_reddit_channel.py:156-176]()

---

## Proxy and Error Handling

Reddit aggressively blocks data center IP ranges with `403 Forbidden` and `429 Too Many Requests` errors. 

- **Proxy Configuration**: Users must configure `reddit_proxy` via `agent-reach configure` to bypass these blocks in server environments [agent_reach/channels/reddit.py:71]().
- **Recursive Extraction**: When reading a post, the backends are responsible for parsing the JSON response to extract the full post body and recursive comment threads [agent_reach/guides/setup-reddit.md:9]().
- **Fallback**: If both primary backends fail, the system suggests using **Exa Search** as a fallback for Reddit content discovery [agent_reach/guides/setup-reddit.md:47-55]().

Sources: [agent_reach/channels/reddit.py:5-9](), [agent_reach/guides/setup-reddit.md:5-9](), [agent_reach/guides/setup-reddit.md:47-55]()

---

# Page: Web and RSS Channels

# Web and RSS Channels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/base.py](agent_reach/channels/base.py)
- [agent_reach/channels/rss.py](agent_reach/channels/rss.py)
- [agent_reach/channels/web.py](agent_reach/channels/web.py)
- [agent_reach/utils/url.py](agent_reach/utils/url.py)
- [tests/test_web_channel.py](tests/test_web_channel.py)

</details>



This page documents two zero-configuration channels: `WebChannel` ([agent_reach/channels/web.py:34]()) and `RSSChannel` ([agent_reach/channels/rss.py:7]()). Both are classified as **Tier 0** (zero-config) [agent_reach/channels/web.py:38](), [agent_reach/channels/rss.py:11]() and work immediately after installation without API keys or complex environment setup.

`WebChannel` is the system's catch-all fallback — it handles any URL that no other channel claims. `RSSChannel` handles RSS and Atom feed URLs specifically using pattern detection and the `feedparser` backend.

---

## WebChannel

`WebChannel` uses the [Jina Reader](https://r.jina.ai) HTTP service as its backend [agent_reach/channels/web.py:37](). It acts as a proxy that transforms complex HTML into clean, LLM-friendly Markdown.

### Role as Catch-All Fallback
In the channel registry, `WebChannel` acts as the final safety net. Its `can_handle` method [agent_reach/channels/web.py:40-41]() returns `True` for any input, ensuring that if no specialized channel (like `TwitterChannel` or `GitHubChannel`) matches the URL, the system still attempts to read it via Jina Reader.

### Implementation Details
- **Backend**: `Jina Reader` [agent_reach/channels/web.py:37]().
- **URL Normalization**: Before sending to Jina, the URL is passed through `normalize_public_http_url` [agent_reach/utils/url.py:47](). This function rejects non-public targets (e.g., `localhost`, `127.0.0.1`, `internal` domains) to prevent SSRF (Server-Side Request Forgery) [agent_reach/utils/url.py:71-82]().
- **Anti-Bot Detection**: The channel includes a `_is_antibot_page` helper [agent_reach/channels/web.py:15]() that scans the first 4KB of the response for markers indicating Cloudflare challenges or Jina captcha requirements [agent_reach/channels/web.py:17-31](). If detected, it raises a `RuntimeError` suggesting the user switch to a browser-based tool [agent_reach/channels/web.py:62-66]().
- **Constraints**: It enforces a strict 5MB response limit (`_MAX_RESPONSE_BYTES`) to prevent memory exhaustion [agent_reach/channels/web.py:11](), [agent_reach/channels/web.py:58-61]().

### Diagnostics
The `check()` method [agent_reach/channels/web.py:43-46]() is designed to be zero-overhead. It does not perform network probes during a `doctor` check, ensuring that diagnostics remain fast and do not trigger rate limits on the Jina API unnecessarily.

**Diagram 1: WebChannel Request Pipeline**

```mermaid
graph TD
    "Input[URL]" --> "Normalize[normalize_public_http_url]"
    "Normalize[normalize_public_http_url]" -->|"SSRF/Private Check"| "Jina_Req[urllib.request.Request]"
    "Jina_Req[urllib.request.Request]" -->|"Prepend https://r.jina.ai/"| "HTTP_Fetch[urlopen]"
    "HTTP_Fetch[urlopen]" --> "Size_Check[Length > 5MB?]"
    "Size_Check[Length > 5MB?]" -->|"No"| "Bot_Check[_is_antibot_page]"
    "Bot_Check[_is_antibot_page]" -->|"Clean"| "Output[Markdown Body]"
    
    subgraph "Safety Filters (agent_reach/utils/url.py)"
    "Normalize[normalize_public_http_url]"
    end
    
    subgraph "Response Validation (agent_reach/channels/web.py)"
    "Size_Check[Length > 5MB?]"
    "Bot_Check[_is_antibot_page]"
    end
```
Sources: [agent_reach/channels/web.py:11-67](), [agent_reach/utils/url.py:47-84]()

---

## RSSChannel

`RSSChannel` provides structured access to syndicated content. It wraps the `feedparser` library to process XML-based feeds into a standardized format.

### URL Detection Logic
The `can_handle` method [agent_reach/channels/rss.py:13-14]() performs string-based pattern matching on the URL to identify potential feeds. It looks for case-insensitive matches of:
- Path segments: `/feed`, `/rss`, `atom`
- File extensions: `.xml`

### Backend Requirements and Health
The channel depends on the `feedparser` Python package [agent_reach/channels/rss.py:10](). The `check()` method [agent_reach/channels/rss.py:16-27]() verifies the installation state:
- **Status `ok`**: `feedparser` is successfully imported.
- **Status `off`**: `feedparser` is missing, providing a `pip install` command to the user [agent_reach/channels/rss.py:21]().
- **Status `error`**: `feedparser` is installed but fails during import (e.g., version conflict), providing a `--force-reinstall` remedy [agent_reach/channels/rss.py:25]().

**Diagram 2: RSSChannel Code Entity Interaction**

```mermaid
sequenceDiagram
    participant Core as "AgentReach Core"
    participant RSS as "RSSChannel [rss.py]"
    participant Lib as "feedparser library"
    
    Core->>RSS: "can_handle(url)"
    Note over RSS: "Search for /feed, /rss, .xml, atom"
    RSS-->>Core: "True/False"
    
    Core->>RSS: "check(config)"
    alt "Import Success"
        RSS->>Lib: "import feedparser"
        RSS-->>Core: "('ok', '可读取 RSS/Atom 源')"
    else "ImportError"
        RSS-->>Core: "('off', 'feedparser 未安装')"
    else "Other Exception"
        RSS-->>Core: "('error', '修复：pip install --force-reinstall...')"
    end
```
Sources: [agent_reach/channels/rss.py:7-27]()

---

## Comparison of Generic Channels

| Feature | WebChannel | RSSChannel |
| :--- | :--- | :--- |
| **Class Name** | `WebChannel` [agent_reach/channels/web.py:34]() | `RSSChannel` [agent_reach/channels/rss.py:7]() |
| **Tier** | 0 (Zero Config) [agent_reach/channels/web.py:38]() | 0 (Zero Config) [agent_reach/channels/rss.py:11]() |
| **Primary Backend** | Jina Reader (HTTP) [agent_reach/channels/web.py:37]() | `feedparser` (Python Lib) [agent_reach/channels/rss.py:10]() |
| **Trigger Pattern** | `True` (Catch-all) [agent_reach/channels/web.py:41]() | `.xml`, `/feed`, `/rss`, `atom` [agent_reach/channels/rss.py:14]() |
| **Security** | SSRF protection via `url.py` [agent_reach/channels/web.py:50]() | Standard library parsing |
| **Diagnostics** | Zero-overhead (no network) [agent_reach/channels/web.py:44]() | Import-based check [agent_reach/channels/rss.py:17]() |

Sources: [agent_reach/channels/web.py:1-67](), [agent_reach/channels/rss.py:1-27](), [agent_reach/utils/url.py:47-84]()

---

# Page: XiaoHongShu Channel

# XiaoHongShu Channel

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/exa_search.py](agent_reach/channels/exa_search.py)
- [agent_reach/channels/xiaohongshu.py](agent_reach/channels/xiaohongshu.py)
- [agent_reach/guides/setup-xiaohongshu.md](agent_reach/guides/setup-xiaohongshu.md)
- [docs/cookie-export.md](docs/cookie-export.md)

</details>



This page documents `XiaoHongShuChannel`: its multi-backend stack (OpenCLI, xiaohongshu-mcp, and xhs-cli), authentication boundaries, data cleaning logic, and Docker-based setup. For the general channel interface that all channels implement, see [Channel Architecture](). For mcporter configuration, see [mcporter Setup]().

---

## Overview

`XiaoHongShuChannel` supports reading and searching XiaoHongShu (小红书) notes. It implements a multi-backend strategy: **OpenCLI** is prioritized for desktop environments with active browser sessions, while **xiaohongshu-mcp** (running via Docker) serves as the primary backend for server environments requiring explicit cookie imports.

| Property | Value |
|---|---|
| Class | `XiaoHongShuChannel` [agent_reach/channels/xiaohongshu.py:160]() |
| `name` | `"xiaohongshu"` [agent_reach/channels/xiaohongshu.py:161]() |
| `description` | `"小红书笔记"` [agent_reach/channels/xiaohongshu.py:162]() |
| `backends` | `["OpenCLI", "xiaohongshu-mcp", "xhs-cli (xiaohongshu-cli)"]` [agent_reach/channels/xiaohongshu.py:163]() |
| `tier` | `1` [agent_reach/channels/xiaohongshu.py:164]() |
| Supported Domains | `xiaohongshu.com`, `xhslink.com` [agent_reach/channels/xiaohongshu.py:169]() |

Sources: [agent_reach/channels/xiaohongshu.py:160-170]()

---

## Backend Architecture

The channel probes backends in a specific order to automatically adapt to the environment. **OpenCLI** is checked first; if a desktop Chrome session is not detected, it falls back to **xiaohongshu-mcp** (a Model Context Protocol server). **xhs-cli** remains as a legacy fallback for existing installations [agent_reach/channels/xiaohongshu.py:2-10]().

**System Entity Mapping:**

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserPrompt["'Read this XHS note: xhslink.com/...'"]
    end

    subgraph "Code Entity Space"
        CLI["agent-reach read"]
        Channel["XiaoHongShuChannel\n(agent_reach/channels/xiaohongshu.py)"]
        OpenCLI["OpenCLI Backend\n(Chrome Session)"]
        MCP_Bridge["mcporter CLI\n(xiaohongshu-mcp)"]
        Legacy["xhs-cli\n(xiaohongshu-cli)"]
        
        CLI -->|"dispatches to"| Channel
        Channel -->|"Probes Order 1"| OpenCLI
        Channel -->|"Probes Order 2"| MCP_Bridge
        Channel -->|"Probes Order 3"| Legacy
    end
    
    UserPrompt -.-> CLI
```

Sources: [agent_reach/channels/xiaohongshu.py:2-10](), [agent_reach/channels/xiaohongshu.py:181-190](), [agent_reach/guides/setup-xiaohongshu.md:4-6]()

---

## Authentication and Cookies

Agent Reach maintains a strict **Authentication Boundary**: it does not perform login or read browser cookies directly [agent_reach/guides/setup-xiaohongshu.md:14-15]().

1.  **OpenCLI**: Uses existing, user-controlled Chrome sessions. No cookie injection occurs [agent_reach/guides/setup-xiaohongshu.md:16-17]().
2.  **xiaohongshu-mcp**: Requires manual cookie export via the **Cookie-Editor** extension (Header String format) [agent_reach/guides/setup-xiaohongshu.md:21-23]().
3.  **Configuration**: The command `agent-reach configure xhs-cookies` saves the provided string to an owner-only local file or imports it directly into the `xiaohongshu-mcp` container if running [agent_reach/guides/setup-xiaohongshu.md:27-35]().

Sources: [agent_reach/guides/setup-xiaohongshu.md:12-36](), [docs/cookie-export.md:34-38]()

---

## Data Flow and Formatting

The `format_xhs_result` function cleans raw API responses to reduce token usage by stripping structural redundancy [agent_reach/channels/xiaohongshu.py:51-56]().

**Data Transformation Flow:**

```mermaid
flowchart TD
    Raw["Raw XHS JSON\n(nested 'note_card', 'interact_info', 'image_list')"]
    CleanFunc["format_xhs_result()\n(agent_reach/channels/xiaohongshu.py:51)"]
    NoteCleaner["_clean_note()\n(agent_reach/channels/xiaohongshu.py:73)"]
    CommentCleaner["_clean_comment()\n(agent_reach/channels/xiaohongshu.py:144)"]
    Final["Cleaned Dict\n(id, xsec_token, title, images, tags, comments)"]

    Raw --> CleanFunc
    CleanFunc --> NoteCleaner
    NoteCleaner --> CommentCleaner
    CommentCleaner --> Final
```

### Key Formatting Rules
- **Fields Kept**: `id`, `note_id`, `xsec_token`, `title`, `desc`, `type`, `time` [agent_reach/channels/xiaohongshu.py:84-86]().
- **Author Info**: Extracts only `nickname` and `user_id` [agent_reach/channels/xiaohongshu.py:95-97]().
- **Image Handling**: Extracts raw URLs from `image_list` or `images_list` [agent_reach/channels/xiaohongshu.py:111-122]().
- **Engagement**: Flattens `interact_info` (likes, collections, comments, shares) into the top-level dictionary [agent_reach/channels/xiaohongshu.py:100-108]().

Sources: [agent_reach/channels/xiaohongshu.py:51-157]()

---

## Health Check and Diagnostics

The `check()` method probes candidates in order and returns the first fully usable backend or an actionable prescription for the best candidate [agent_reach/channels/xiaohongshu.py:171-177]().

**Diagnostic Logic:**

```mermaid
flowchart TD
    Start["check()"] --> ProbeOrder["Iterate: OpenCLI -> MCP -> xhs-cli"]
    
    ProbeOrder --> OpenCLI{"OpenCLI active?"}
    OpenCLI -- "Yes" --> OK["Status: 'ok'\n(Active: OpenCLI)"]
    
    OpenCLI -- "No" --> MCPCheck{"xiaohongshu-mcp\nservice reachable?"}
    MCPCheck -- "Yes" --> LoginCheck{"mcporter check_login?"}
    LoginCheck -- "Logged In" --> OK2["Status: 'ok'\n(Active: xiaohongshu-mcp)"]
    LoginCheck -- "No" --> Warn["Status: 'warn'\n(Login Required)"]
    
    MCPCheck -- "No" --> LegacyCheck{"xhs-cli installed?"}
    LegacyCheck -- "Yes" --> OK3["Status: 'ok'\n(Active: xhs-cli)"]
    LegacyCheck -- "No" --> Off["Status: 'off'\n(No backends found)"]
```

### MCP Service Detection
The helper `_mcp_service_reachable` verifies if the service is up on `localhost:18060` by explicitly bypassing proxies, as `localhost` must not be routed through `HTTP_PROXY` [agent_reach/channels/xiaohongshu.py:33-48]().

Sources: [agent_reach/channels/xiaohongshu.py:33-48](), [agent_reach/channels/xiaohongshu.py:171-191]()

---

## Server Setup: Docker MCP

For server-side usage, the Docker-based `xiaohongshu-mcp` is recommended.

1.  **Run Container**:
    ```bash
    docker run -d --name xiaohongshu-mcp -p 18060:18060 xpzouying/xiaohongshu-mcp
    ```
    [agent_reach/guides/setup-xiaohongshu.md:73-76]()
2.  **Register with mcporter**:
    ```bash
    mcporter config add xiaohongshu http://localhost:18060/mcp --scope home
    ```
    [agent_reach/guides/setup-xiaohongshu.md:78]()
3.  **Risk Mitigation**: If encountering "IP Risk" blocks, use a residential proxy by exporting `HTTP_PROXY` [agent_reach/guides/setup-xiaohongshu.md:62-63]().

Sources: [agent_reach/guides/setup-xiaohongshu.md:68-81]()

---

# Page: Exa Search Channel

# Exa Search Channel

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/exa_search.py](agent_reach/channels/exa_search.py)
- [agent_reach/channels/xiaohongshu.py](agent_reach/channels/xiaohongshu.py)
- [agent_reach/guides/setup-exa.md](agent_reach/guides/setup-exa.md)
- [agent_reach/guides/setup-reddit.md](agent_reach/guides/setup-reddit.md)

</details>



This page documents `ExaSearchChannel`, the semantic web search channel implemented in `agent_reach/channels/exa_search.py`. It covers the channel's role as both a first-class search channel and a cross-channel search fallback, its `mcporter` + Exa MCP backend, and its zero-configuration setup.

For the abstract channel interface that `ExaSearchChannel` conforms to, see **3.1 Channel Architecture**. For `mcporter` configuration details, see **4.3 mcporter Setup**.

---

## Overview

`ExaSearchChannel` provides semantic web search by bridging to the Exa MCP server (`mcp.exa.ai`) via the `mcporter` CLI. It is a **search-only** channel: `can_handle()` always returns `False` [agent_reach/channels/exa_search.py:16-17](), ensuring it never intercepts URL reads. It is classified as **Tier 0** (zero-config) because it requires no API keys or complex local setup beyond the `mcporter` bridge [agent_reach/channels/exa_search.py:14]().

| Property | Value |
|---|---|
| `name` | `exa_search` [agent_reach/channels/exa_search.py:11]() |
| `description` | 全网语义搜索 [agent_reach/channels/exa_search.py:12]() |
| `backends` | `["Exa via mcporter"]` [agent_reach/channels/exa_search.py:13]() |
| `tier` | `0` [agent_reach/channels/exa_search.py:14]() |
| `can_handle()` | Always `False` [agent_reach/channels/exa_search.py:17]() |
| API key required | No [agent_reach/guides/setup-exa.md:32]() |

Sources: [agent_reach/channels/exa_search.py:10-17](), [agent_reach/guides/setup-exa.md:4-32]()

---

## Role in the System

`ExaSearchChannel` serves two primary functions:

1.  **Primary Search Provider**: Invoked directly via `agent-reach search` for general web queries.
2.  **Cross-Channel Fallback**: Used by other channels (Twitter, Reddit, LinkedIn) when their native search mechanisms fail or are blocked [agent_reach/guides/setup-reddit.md:47-53]().

**Search Capabilities via Exa:**
-   **General Web**: AI-powered semantic search.
-   **Reddit**: Targeted via `site:reddit.com` [agent_reach/guides/setup-exa.md:6]().
-   **Twitter/X**: Targeted via `site:x.com` [agent_reach/guides/setup-exa.md:7]().

Sources: [agent_reach/guides/setup-exa.md:3-8](), [agent_reach/guides/setup-reddit.md:47-55]()

---

## Architecture and Data Flow

The channel communicates with Exa through the `mcporter` CLI process, which connects to the official Exa MCP endpoint at `https://mcp.exa.ai/mcp` [agent_reach/guides/setup-exa.md:21]().

### Search Execution Flow

```mermaid
flowchart LR
    subgraph "Natural Language Space"
        UserPrompt["'Search for latest AI news'"]
    end

    subgraph "Code Entity Space"
        SearchCmd["agent-reach search"]
        ExaChan["ExaSearchChannel"]
        MCP["mcporter (CLI)"]
        ExaServer["mcp.exa.ai (MCP Server)"]
    end

    UserPrompt --> SearchCmd
    SearchCmd --> ExaChan
    ExaChan -- "subprocess/shutil" --> MCP
    MCP -- "JSON-RPC" --> ExaServer
    ExaServer -- "Search Results" --> MCP
    MCP -- "stdout" --> ExaChan
```

Sources: [agent_reach/channels/exa_search.py:19-44](), [agent_reach/guides/setup-exa.md:14-22]()

### Class Structure and Interface

```mermaid
classDiagram
    class Channel {
        <<abstract>>
        +can_handle(url) bool
        +check(config) tuple
    }

    class ExaSearchChannel {
        +name: str = "exa_search"
        +tier: int = 0
        +can_handle(url) False
        +check(config) tuple
    }

    class McporterUtils {
        +inspect_mcporter_config()
    }

    Channel <|-- ExaSearchChannel
    ExaSearchChannel ..> McporterUtils : uses
```

Sources: [agent_reach/channels/exa_search.py:10-28]()

---

## Health Check and Diagnostics

The `check()` method is used by `agent-reach doctor` to verify the environment. Unlike simple CLI checks, it uses `inspect_mcporter_config()` to analyze the `mcporter` configuration file without necessarily spawning the full bridge process [agent_reach/channels/exa_search.py:28]().

| Condition | Status | Message / Action |
|---|---|---|
| `mcporter` missing | `"off"` | Prompts installation of `mcporter` [agent_reach/channels/exa_search.py:21-26]() |
| `exa` in config | `"warn"` | "Exa 已写入 mcporter 配置，但 Doctor 未启动远端服务做连通验证" [agent_reach/channels/exa_search.py:32-35]() |
| `exa` missing in config | `"off"` | Prompts `mcporter config add exa https://mcp.exa.ai/mcp` [agent_reach/channels/exa_search.py:41-44]() |
| Config read error | `"error"` | Reports `McporterConfigError` [agent_reach/channels/exa_search.py:29-30]() |

Sources: [agent_reach/channels/exa_search.py:19-44](), [agent_reach/channels/mcporter.py:1-25]()

---

## Setup and Configuration

Setup is typically handled automatically by `agent-reach install --env=auto --system` [agent_reach/guides/setup-exa.md:11-12]().

### Manual Configuration
If manual intervention is required, the following steps register the Exa MCP server:

1.  **Install Bridge**: `npm install -g mcporter` [agent_reach/guides/setup-exa.md:16]()
2.  **Register Server**: `mcporter config add exa https://mcp.exa.ai/mcp --scope home` [agent_reach/guides/setup-exa.md:21]()
3.  **Verify**: `agent-reach doctor` [agent_reach/guides/setup-exa.md:26]()

### Implementation Detail: `check()`
The implementation utilizes `shutil.which` to locate the binary and the `inspect_mcporter_config` utility to parse the local JSON configuration [agent_reach/channels/exa_search.py:21-28]().

```python
# [agent_reach/channels/exa_search.py:21-31]
if not shutil.which("mcporter"):
    return "off", (
        "需要 mcporter + Exa MCP。安装：\n"
        "  npm install -g mcporter\n"
        "  mcporter config add exa https://mcp.exa.ai/mcp --scope home"
    )
try:
    inspection = inspect_mcporter_config()
except McporterConfigError as exc:
    return "error", f"mcporter 配置检查失败：{exc}"
```

Sources: [agent_reach/channels/exa_search.py:19-31](), [agent_reach/guides/setup-exa.md:14-22]()

---

## Limitations and Behavior

-   **Search-Only**: `ExaSearchChannel` does not implement `read()`. It is designed to find content, which is then typically read by `WebChannel` or specific platform channels [agent_reach/channels/exa_search.py:17]().
-   **No API Key**: The official MCP endpoint provided by Exa (`mcp.exa.ai`) currently operates without requiring an API key for the bridge [agent_reach/guides/setup-exa.md:32]().
-   **Dependency**: Relies on Node.js being installed to run `mcporter` [agent_reach/guides/setup-exa.md:16]().
-   **Doctor Verification**: The `check()` method reports `warn` even if configured, as it avoids making a network request during a simple status check to prevent unnecessary credential/network usage [agent_reach/channels/exa_search.py:32-35]().

Sources: [agent_reach/channels/exa_search.py:16-44](), [agent_reach/guides/setup-exa.md:29-42]()

---

# Page: Facebook, Instagram, and LinkedIn Channels

# Facebook, Instagram, and LinkedIn Channels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/backends/opencli.py](agent_reach/backends/opencli.py)
- [agent_reach/channels/__init__.py](agent_reach/channels/__init__.py)
- [agent_reach/channels/instagram.py](agent_reach/channels/instagram.py)
- [agent_reach/channels/linkedin.py](agent_reach/channels/linkedin.py)
- [agent_reach/channels/mcporter.py](agent_reach/channels/mcporter.py)
- [tests/test_channel_contracts.py](tests/test_channel_contracts.py)
- [tests/test_opencli_backend.py](tests/test_opencli_backend.py)

</details>



This page documents the implementation of the Facebook, Instagram, and LinkedIn channels. These channels are categorized as **Tier 2** (needs setup) because they rely on external browser-bridge tools or specialized MCP servers to bypass modern web scrap-protection and session requirements.

## Overview

Facebook and Instagram share a common architecture based on the `OpenCLISiteChannel` base class, which utilizes a local browser-bridge to reuse the user's active Chrome/Edge session. LinkedIn utilizes the Model Context Protocol (MCP) via `mcporter`.

| Channel | Class | File | Primary Backend | Tier |
|:---|:---|:---|:---|:---|
| **Facebook** | `FacebookChannel` | [agent_reach/channels/facebook.py:7-13]() | OpenCLI | 2 |
| **Instagram** | `InstagramChannel` | [agent_reach/channels/instagram.py:7-13]() | OpenCLI | 2 |
| **LinkedIn** | `LinkedInChannel` | [agent_reach/channels/linkedin.py:23-28]() | `mcp-server-linkedin` | 2 |

Sources: [agent_reach/channels/__init__.py:26-42](), [agent_reach/channels/facebook.py:7-13](), [agent_reach/channels/instagram.py:7-13](), [agent_reach/channels/linkedin.py:23-28]()

---

## OpenCLISiteChannel Base Class

The `FacebookChannel` and `InstagramChannel` are subclasses of `OpenCLISiteChannel` [agent_reach/channels/_opencli_site.py:10-14](). This shared base class implements the logic for interacting with **OpenCLI**, a tool that drives the user's real browser via a bridge extension.

### Data Flow: Natural Language to Code Entity

**Diagram: OpenCLI Browser-Bridge Interaction**

```mermaid
flowchart TD
    subgraph "Natural Language Space"
        UserPrompt["'Read the latest post from facebook.com/zuck'"]
    end

    subgraph "Code Entity Space"
        Core["AgentReach.read(url)"]
        Registry["ALL_CHANNELS Registry"]
        FBChannel["FacebookChannel"]
        BaseClass["OpenCLISiteChannel"]
        OpenCLIProbe["opencli_status()"]
    end

    subgraph "External System Space"
        OpenCLICLI["opencli binary"]
        Daemon["OpenCLI Daemon (Port 19825)"]
        Browser["Chrome/Edge + Extension"]
    end

    UserPrompt --> Core
    Core --> Registry
    Registry -- "can_handle('facebook.com')" --> FBChannel
    FBChannel -- "Inherits read()" --> BaseClass
    BaseClass -- "Probes Health" --> OpenCLIProbe
    OpenCLIProbe -- "HTTP GET /status" --> Daemon
    BaseClass -- "Executes Command" --> OpenCLICLI
    OpenCLICLI <--> Daemon
    Daemon <--> Browser
```

Sources: [agent_reach/channels/_opencli_site.py:10-40](), [agent_reach/backends/opencli.py:128-157](), [agent_reach/channels/facebook.py:7-13]()

### Implementation Details
- **Zero Configuration:** No API keys or manual cookie exports are needed; it reuses the browser's `Cookie` header automatically.
- **Desktop Only:** Since it requires a GUI browser, it is not suitable for headless server environments.
- **Health Probing:** The `opencli_status()` function performs a side-effect-free probe by checking the CLI version and querying the local daemon's `/status` endpoint [agent_reach/backends/opencli.py:128-157]().
- **Warning State:** These channels report `warn` rather than `ok` in `agent-reach doctor` because while the bridge might be active, the code cannot verify if the user is actually logged into the specific site without performing a heavy page load [agent_reach/backends/opencli.py:158-179]().

---

## Instagram Channel

**File:** [agent_reach/channels/instagram.py]()

The `InstagramChannel` handles URLs for `instagram.com` and `instagr.am` [agent_reach/channels/instagram.py:11-11](). It provides specific OpenCLI commands for searching, profile extraction, and exploring posts [agent_reach/channels/instagram.py:12-12]().

### Key Commands
- **Search:** `agent-reach search-instagram <query>`
- **Read:** `agent-reach read https://www.instagram.com/openai/`

Sources: [agent_reach/channels/instagram.py:7-13]()

---

## Facebook Channel

**File:** [agent_reach/channels/facebook.py]()

The `FacebookChannel` handles `facebook.com` and `fb.com` [agent_reach/channels/facebook.py:11-11](). Like Instagram, it leverages the OpenCLI bridge to bypass Facebook's aggressive login walls.

### Key Commands
- **Search:** `agent-reach search-facebook <query>`
- **Read:** `agent-reach read https://www.facebook.com/zuck`

Sources: [agent_reach/channels/facebook.py:7-13]()

---

## LinkedIn Channel

**File:** [agent_reach/channels/linkedin.py]()

Unlike the OpenCLI-based channels, `LinkedInChannel` is built around the **Model Context Protocol (MCP)**. It primarily uses `mcp-server-linkedin` via the `mcporter` bridge [agent_reach/channels/linkedin.py:26-26]().

### Backend Strategy
1. **Primary:** `mcp-server-linkedin` (Full profile, company, and job data).
2. **Fallback:** `Jina Reader` (Basic public content extraction).

### Data Flow: MCP Routing

**Diagram: LinkedIn MCP Routing**

```mermaid
flowchart LR
    subgraph "Agent Reach Entities"
        LI["LinkedInChannel"]
        MCPHelper["inspect_mcporter_config()"]
    end

    subgraph "System Dependencies"
        MCPorter["mcporter CLI"]
        UVX["uvx (Astral)"]
        LinkedInMCP["mcp-server-linkedin"]
    end

    LI -- "1. Check availability" --> MCPHelper
    MCPHelper -- "Reads ~/.mcporter/mcporter.json" --> MCPorter
    LI -- "2. Execute" --> UVX
    UVX -- "Runs latest" --> LinkedInMCP
    LinkedInMCP -- "Scrapes via Session" --> LinkedIn((LinkedIn.com))
```

Sources: [agent_reach/channels/linkedin.py:34-69](), [agent_reach/channels/mcporter.py:32-47]()

### Status Checking (`check`)
The `check()` method performs a multi-stage validation:
- **Missing mcporter:** Returns `off` with installation instructions for `uv` and `mcporter` [agent_reach/channels/linkedin.py:36-43]().
- **Config Validation:** Uses `inspect_mcporter_config()` to see if any known LinkedIn server names (e.g., `linkedin-scraper`, `mcp-server-linkedin`) are registered in the `mcporter` configuration [agent_reach/channels/linkedin.py:45-48]().
- **Missing uvx:** If configured but `uvx` is missing from the system path, it issues a `warn` [agent_reach/channels/linkedin.py:49-54]().
- **Verification Warning:** Even if everything looks correct, it reports `warn` because `doctor` does not start the local service to verify live connectivity, to avoid side effects [agent_reach/channels/linkedin.py:55-58]().

Sources: [agent_reach/channels/linkedin.py:34-69](), [agent_reach/channels/mcporter.py:49-82]()

---

# Page: Xiaoyuzhou, V2EX, and Xueqiu Channels

# Xiaoyuzhou, V2EX, and Xueqiu Channels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/_opencli_site.py](agent_reach/channels/_opencli_site.py)
- [agent_reach/channels/v2ex.py](agent_reach/channels/v2ex.py)
- [agent_reach/channels/xiaoyuzhou.py](agent_reach/channels/xiaoyuzhou.py)
- [agent_reach/channels/xueqiu.py](agent_reach/channels/xueqiu.py)
- [agent_reach/scripts/transcribe_xiaoyuzhou.sh](agent_reach/scripts/transcribe_xiaoyuzhou.sh)
- [tests/test_channels.py](tests/test_channels.py)
- [tests/test_v2ex_channel.py](tests/test_v2ex_channel.py)
- [tests/test_xueqiu_channel.py](tests/test_xueqiu_channel.py)

</details>



This page documents the specialized platform channels for Xiaoyuzhou (podcast transcription), V2EX (developer community), and Xueqiu (financial data). These channels represent a mix of Tier 0 (zero-config public APIs) and Tier 1 (external dependencies and API keys) implementations within the Agent Reach ecosystem.

### XiaoyuzhouChannel

The `XiaoyuzhouChannel` provides a sophisticated transcription pipeline for the Xiaoyuzhou (小宇宙) podcast platform. Unlike standard text-based channels, it manages a multi-step workflow involving audio extraction, transcoding, and AI-driven speech-to-text.

*   **Implementation:** The channel class `XiaoyuzhouChannel` acts as a wrapper and health-checker for the underlying `transcribe.sh` bash script [agent_reach/channels/xiaoyuzhou.py:12-15]().
*   **Dependencies:**
    *   **ffmpeg:** Required for audio transcoding and segmenting [agent_reach/channels/xiaoyuzhou.py:28-38]().
    *   **Groq API Key:** Used to access the `whisper-large-v3` model for high-speed transcription [agent_reach/channels/xiaoyuzhou.py:49-62]().
*   **Transcription Pipeline (`transcribe_xiaoyuzhou.sh`):**
    1.  **Extraction:** Parses the show page to find direct media URLs (`.m4a` or `.mp3`) [agent_reach/scripts/transcribe_xiaoyuzhou.sh:110-123]().
    2.  **Transcoding:** Uses `ffmpeg` to convert audio to single-channel (mono) 64k MP3 to minimize upload size [agent_reach/scripts/transcribe_xiaoyuzhou.sh:177-182]().
    3.  **Chunking:** Splits the audio into 20MB segments to stay within Groq's 25MB file limit [agent_reach/scripts/transcribe_xiaoyuzhou.sh:184-204]().
    4.  **AI Transcription:** dispatches chunks to the Groq Whisper API [agent_reach/scripts/transcribe_xiaoyuzhou.sh:206-220]().
    5.  **Polishing (Optional):** If the `--polish` flag is used, it calls Llama 3.3 70B to correct Chinese punctuation and formatting [agent_reach/scripts/transcribe_xiaoyuzhou.sh:6-8]().

**Sources:** [agent_reach/channels/xiaoyuzhou.py:1-65](), [agent_reach/scripts/transcribe_xiaoyuzhou.sh:1-220]()

---

### V2EXChannel

`V2EXChannel` is a Tier 0 channel that interacts with the V2EX developer community. It is designed to be highly resilient to TLS issues common in specific network environments.

*   **Public API Integration:** Uses the standard V2EX JSON API for fetching hot topics and node-specific content [agent_reach/channels/v2ex.py:140-144]().
*   **TLS Fallback Mechanism:** If the standard Python `urllib` stack encounters an `UNEXPECTED_EOF_WHILE_READING` error (common with certain proxies or MTU settings), the channel automatically falls back to using the system's `curl` binary to complete the request [agent_reach/channels/v2ex.py:57-82](), [agent_reach/channels/v2ex.py:128-137]().
*   **Safety Constraints:**
    *   **Domain Validation:** Only permits requests to `v2ex.com` or `www.v2ex.com` over HTTPS [agent_reach/channels/v2ex.py:28-44]().
    *   **Size Limits:** Enforces a 1 MiB limit on API responses to prevent memory exhaustion [agent_reach/channels/v2ex.py:19](), [agent_reach/channels/v2ex.py:52-54]().
*   **Key Capabilities:**
    *   `get_hot_topics()`: Retrieves the top trending discussions [agent_reach/channels/v2ex.py:177-200]().
    *   `get_node_topics()`: Browses topics within a specific node (e.g., "python") [tests/test_v2ex_channel.py:182-188]().

**Sources:** [agent_reach/channels/v2ex.py:1-201](), [tests/test_v2ex_channel.py:1-202]()

---

### XueqiuChannel

`XueqiuChannel` provides financial data and community posts from the Xueqiu (雪球) platform. It requires careful session management to navigate the platform's anti-crawling measures.

*   **Cookie-Aware Session Management:**
    *   Uses `http.cookiejar.CookieJar` to persist session state [agent_reach/channels/xueqiu.py:24-27]().
    *   `_ensure_cookies()`: Prioritizes cookies from `config.yaml` (set via `agent-reach configure --from-browser`). If missing, it performs a fallback visit to the Xueqiu homepage to obtain basic session cookies (e.g., `acw_tc`) [agent_reach/channels/xueqiu.py:74-94]().
*   **Data Shaping:**
    *   **Stock Quotes:** Normalizes stock data for SH/SZ/HK/US markets into a standard dictionary [agent_reach/channels/xueqiu.py:161-195]().
    *   **Community Posts:** Extracts "Hot Posts" by unwrapping JSON-in-JSON payloads and stripping HTML tags [tests/test_xueqiu_channel.py:173-192]().
*   **Health Check:** The `check()` method attempts to fetch a quote for a stable stock (e.g., `SH601138`) to verify API connectivity [agent_reach/channels/xueqiu.py:133-144]().

**Sources:** [agent_reach/channels/xueqiu.py:1-195](), [tests/test_xueqiu_channel.py:1-200]()

---

### Natural Language to Code Entity Mapping

The following diagrams illustrate how user intents are mapped to specific backend implementations for these three platforms.

**Diagram 1: Xiaoyuzhou Transcription Pipeline**
This diagram shows how a natural language request to "transcribe a podcast" triggers a chain of specialized system tools.

```mermaid
graph TD
    User["'Transcribe this podcast'"] --> Channel["XiaoyuzhouChannel.check()"]
    Channel --> |"Validates"| FFMPEG["ffmpeg (System Tool)"]
    Channel --> |"Validates"| Key["groq_api_key (Config)"]
    
    Channel --> Script["transcribe.sh"]
    Script --> |"Download & Transcode"| FFMPEG
    Script --> |"STT Request"| Groq["Groq Whisper API"]
    Groq --> Markdown["Markdown Transcript"]
```
**Sources:** [agent_reach/channels/xiaoyuzhou.py:23-65](), [agent_reach/scripts/transcribe_xiaoyuzhou.sh:177-220]()

**Diagram 2: V2EX and Xueqiu API Dispatch**
This diagram maps URL-based intents to the specific public API handlers and their internal recovery/session logic.

```mermaid
graph LR
    subgraph "Natural Language Space"
        V2URL["'What is hot on V2EX?'"]
        XQURL["'Price of SH600519?'"]
    end

    subgraph "Code Entity Space"
        V2C["V2EXChannel"]
        XQC["XueqiuChannel"]
        Curl["curl (TLS Fallback)"]
        CJar["CookieJar (Session)"]
    end

    V2URL --> V2C
    XQURL --> XQC
    
    V2C --> |"on TLS Error"| Curl
    XQC --> |"Auth/Anti-Bot"| CJar
```
**Sources:** [agent_reach/channels/v2ex.py:128-137](), [agent_reach/channels/xueqiu.py:24-27](), [agent_reach/channels/xueqiu.py:74-94]()

### Platform Comparison Table

| Feature | Xiaoyuzhou | V2EX | Xueqiu |
| :--- | :--- | :--- | :--- |
| **Tier** | 1 (Needs Key/Tool) | 0 (Zero-Config) | 0 (Zero-Config) |
| **Primary Backend** | Groq Whisper | Public JSON API | Public JSON API |
| **Key Dependency** | `ffmpeg` | `curl` (optional fallback) | `http.cookiejar` |
| **Authentication** | API Key (`groq-key`) | None (Public) | Cookies (Optional/Auto) |
| **Routing Domain** | `xiaoyuzhoufm.com` | `v2ex.com` | `xueqiu.com` |
| **Primary Method** | `transcribe.sh` | `get_hot_topics` | `get_stock_quote` |

**Sources:** [agent_reach/channels/xiaoyuzhou.py:13-21](), [agent_reach/channels/v2ex.py:140-153](), [agent_reach/channels/xueqiu.py:114-128]()

---

# Page: Configuration

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/cli.py](agent_reach/cli.py)
- [agent_reach/config.py](agent_reach/config.py)
- [tests/test_config.py](tests/test_config.py)

</details>



This page documents Agent Reach's configuration system: where settings are stored, how the `Config` class manages them, and how values are resolved at runtime. For step-by-step instructions on specific configuration tasks, see the following sub-pages:

- [Cookie Export Guide](#4.1) — Instructions for Twitter, Instagram, XiaoHongShu, and Bilibili session management.
- [Proxy Configuration](#4.2) — Setting up network proxies for Reddit, Bilibili, and other restricted platforms.
- [mcporter Setup](#4.3) — Configuring the MCP bridge for XiaoHongShu, LinkedIn, and Exa semantic search.

---

## Storage Location

All configuration is stored in a single YAML file at:

```
~/.agent-reach/config.yaml
```

The directory and file are managed by the `Config` class. The private directory is created only on the first write via `_ensure_dir()` [agent_reach/config.py:126-130](). To protect sensitive credentials, the file is written with **mode `0o600`** (owner read/write only) using an atomic write process [agent_reach/config.py:46-80]().

**Sources:** [agent_reach/config.py:102-103](), [agent_reach/config.py:126-130]()

---

## The `Config` Class

The `Config` class in [agent_reach/config.py:99-233]() is the central authority for configuration. It handles loading, saving, and validating requirements for specific features.

**Diagram: Config class structure**

```mermaid
classDiagram
    class "Config" {
        +CONFIG_DIR: Path
        +CONFIG_FILE: Path
        +FEATURE_REQUIREMENTS: dict
        +config_path: Path
        +data: dict
        +load()
        +save()
        +get(key, default) Any
        +set(key, value)
        +delete(key)
        +is_configured(feature) bool
        +get_configured_features() dict
        -_ensure_dir()
    }
```

**Sources:** [agent_reach/config.py:99-233]()

### Core Methods

| Method | Description |
|---|---|
| `load()` | Reads `config.yaml` using `yaml.safe_load`. Rejects symlinks for security [agent_reach/config.py:132-150](). |
| `save()` | Atomically writes `self.data` to disk. On non-Windows systems, it enforces `0o600` permissions [agent_reach/config.py:152-157](). |
| `get(key, default)` | Retrieves a value from the data dict, falling back to the uppercase environment variable [agent_reach/config.py:159-168](). |
| `set(key, value)` | Updates a key and persists changes to disk immediately [agent_reach/config.py:170-184](). |
| `delete(key)` | Removes a key and persists changes to disk [agent_reach/config.py:186-197](). |
| `is_configured(feature)` | Validates if all keys required by a feature in `FEATURE_REQUIREMENTS` are present [agent_reach/config.py:199-202](). |

**Sources:** [agent_reach/config.py:132-202]()

---

## Value Resolution Order

When `get(key)` is called, the system checks the configuration file first, followed by environment variables.

**Diagram: Value resolution in `Config.get()`**

```mermaid
flowchart TD
    A["Config.get(key)"]
    B{"key in self.data?\n(config.yaml)"}
    C["Return value from config.yaml"]
    D{"os.environ.get(key.upper())\nexists?"}
    E["Return environment variable value"]
    F["Return default (None)"]

    A --> B
    B -->|"Yes"| C
    B -->|"No"| D
    D -->|"Yes"| E
    D -->|"No"| F
```

**Sources:** [agent_reach/config.py:159-168]()

---

## Feature Requirements Map

The `FEATURE_REQUIREMENTS` map [agent_reach/config.py:106-112]() defines the minimum necessary keys for Agent Reach features to function. This map is used by the `doctor` command to report channel health.

| Feature name | Required config keys |
|---|---|
| `exa_search` | `exa_api_key` |
| `twitter_xreach` | `twitter_auth_token`, `twitter_ct0` |
| `groq_whisper` | `groq_api_key` |
| `openai_whisper` | `openai_api_key` |
| `github_token` | `github_token` |

**Sources:** [agent_reach/config.py:106-112]()

---

## Security and Permissions

Agent Reach employs several layers of security for its configuration:

1.  **Symlink Rejection**: `_reject_symlink` [agent_reach/config.py:39-44]() prevents "file hijacking" by refusing to read or write through symbolic links.
2.  **Atomic Writes**: `_atomic_write_yaml` [agent_reach/config.py:46-96]() writes to a temporary file before replacing the target, ensuring the config isn't corrupted during a crash.
3.  **Restricted Permissions**: The system uses `os.fchmod` (where available) to set `stat.S_IRUSR | stat.S_IWUSR` (0o600) so only the current user can read the credentials [agent_reach/config.py:61-62]().
4.  **Credential Masking**: The `to_dict()` method (tested in [tests/test_config.py:75-137]()) ensures that sensitive keys like `twitter_auth_token` or `proxy` are redacted when converted to a dictionary for logging.

**Sources:** [agent_reach/config.py:46-96](), [tests/test_config.py:139-182]()

---

## Config Lifecycle Diagram

**Diagram: Config interaction across Code Entities**

```mermaid
flowchart LR
    subgraph "CLI Entity Space"
        CLI["agent_reach/cli.py"]
    end

    subgraph "Core Entity Space"
        ConfigClass["Config Class\n(agent_reach/config.py)"]
        Data["self.data"]
    end

    subgraph "External Space"
        Env["os.environ\n(UPPERCASE_KEYS)"]
        FS["~/.agent-reach/config.yaml\n(Perms: 0o600)"]
    end

    CLI -- "set(key, val)" --> ConfigClass
    CLI -- "get(key)" --> ConfigClass
    ConfigClass -- "load()" --> FS
    ConfigClass -- "save()" --> FS
    ConfigClass -- "fallback" --> Env
    ConfigClass -- "manages" --> Data
```

**Sources:** [agent_reach/config.py:99-233](), [agent_reach/cli.py:98-128]()

---

# Page: Cookie Export Guide

# Cookie Export Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/cookie_extract.py](agent_reach/cookie_extract.py)
- [agent_reach/guides/setup-xiaohongshu.md](agent_reach/guides/setup-xiaohongshu.md)
- [agent_reach/utils/paths.py](agent_reach/utils/paths.py)
- [docs/cookie-export.md](docs/cookie-export.md)
- [tests/test_cookie_extract_perms.py](tests/test_cookie_extract_perms.py)
- [tests/test_private_file_writes.py](tests/test_private_file_writes.py)

</details>



This page explains how to export browser session cookies from your local machine and supply them to Agent Reach. This is necessary when Agent Reach is running on a server without direct browser access, or when you want to automate authentication for specific channels using your existing browser session.

Agent Reach provides a built-in automated extraction tool (`--from-browser`) for local environments and manual methods for server environments.

---

## When Cookies Are Required

Not all channels need cookies. The following table maps platforms to their required config keys and the channels that consume them:

| Platform | Config Key | Channel Class | What it unlocks |
|---|---|---|---|
| Twitter / X | `twitter-cookies` | `TwitterChannel` | Search, timeline, authenticated reads |
| XiaoHongShu | `xhs-cookies` | `XiaoHongShuChannel` | Note fetching, search, comments |
| Instagram | `instagram-cookies` | `InstagramChannel` | Private content, profile reads |
| Bilibili | `bilibili` | `BilibiliChannel` | Age-restricted and member-only content |

Sources: [agent_reach/cookie_extract.py:32-57](), [agent_reach/guides/setup-xiaohongshu.md:14-29]()

---

## Method 1: Cookie-Editor Extension (Recommended — 30 seconds per site)

This method is the most reliable for both local and server environments, especially for platforms where automatic extraction is disabled due to project policy (e.g., Twitter and XiaoHongShu).

**Steps:**
1. Install **Cookie-Editor** for Chrome, Firefox, or Edge: [Chrome Web Store](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm).
2. Go to the website (e.g., `https://x.com`) and make sure you're logged in.
3. Click the Cookie-Editor icon in your toolbar.
4. Click **Export** → **Header String**.
5. Provide the result to Agent Reach:
   ```bash
   agent-reach configure twitter-cookies
   # Paste the exported string into the hidden prompt
   ```

Sources: [docs/cookie-export.md:6-27](), [agent_reach/guides/setup-xiaohongshu.md:21-29]()

---

## Method 2: Browser DevTools (Manual)

1. Open the site (e.g., `https://www.bilibili.com`) and log in.
2. Press **F12** (or right-click → Inspect) and click the **Network** tab.
3. Refresh the page (F5).
4. Click any request in the list.
5. In the right panel, scroll to **Request Headers**.
6. Find the line starting with `Cookie:`.
7. Copy the entire value after `Cookie: ` and provide it to `agent-reach configure`.

Sources: [docs/cookie-export.md:48-58]()

---

## Method 3: Auto-Extraction (Local Chromium Only)

For platforms like Bilibili and Xueqiu, Agent Reach can extract cookies directly from local Chromium-based browsers if you are running the CLI on the same machine.

**Command:**
```bash
agent-reach configure --from-browser chrome --platform bilibili
```
*Supported browsers: chrome, edge, brave.*

### Implementation Details
The extraction logic in `agent_reach/cookie_extract.py` targets specific browser profiles and cookie databases.

**Data Flow (Auto-Extraction):**
1. `list_browser_profiles(browser)` [agent_reach/cookie_extract.py:122-154]() locates the `Cookies` or `Network/Cookies` SQLite database in the user data directory [agent_reach/cookie_extract.py:136-139]().
2. `_platform_spec(platform)` [agent_reach/cookie_extract.py:181-196]() retrieves the target domains and required cookie names (e.g., `SESSDATA` for Bilibili).
3. `_require_browser_extractable(spec)` [agent_reach/cookie_extract.py:198-207]() enforces a project policy where high-risk platforms like Twitter and XHS *must* use manual export via Cookie-Editor [agent_reach/cookie_extract.py:65-68]().

Sources: [agent_reach/cookie_extract.py:70-86](), [agent_reach/cookie_extract.py:122-207]()

---

## Technical Mapping: Browser to Code Entities

The following diagrams illustrate how extracted browser data is mapped to internal configuration keys and eventually used by specific Channel classes.

**Diagram: Cookie Data Flow to Channel Entities**

```mermaid
flowchart TD
    subgraph Browser["Local Browser / Cookie-Editor"]
        X_Raw["x.com Header String"]
        XHS_Raw["xhs.com Header String"]
        Bili_DB["bilibili.com SQLite"]
    end

    subgraph CLILogic["agent_reach/cli.py"]
        config_twitter["_configure_twitter_cookies()"]
        config_xhs["_configure_xhs_cookies()"]
    end

    subgraph SyncLogic["agent_reach/cookie_extract.py"]
        sync_bird["_sync_bird_env()"]
        sync_xfetch["_sync_xfetch_session()"]
    end

    subgraph Filesystem["~/.config/ & ~/.agent-reach/"]
        BirdEnv[".config/bird/credentials.env"]
        XfetchJSON[".config/xfetch/session.json"]
        XHSJSON[".agent-reach/xhs-cookies.json"]
    end

    X_Raw --> config_twitter
    config_twitter --> sync_bird
    config_twitter --> sync_xfetch
    sync_bird --> BirdEnv
    sync_xfetch --> XfetchJSON

    XHS_Raw --> config_xhs
    config_xhs --> XHSJSON
    
    Bili_DB -->|extract_all| BiliConfig["config.yaml: bilibili"]
```

**Diagram: Credential Protection Mechanism**

```mermaid
flowchart LR
    subgraph Utils["agent_reach/utils/paths.py"]
        atomic_write["atomic_write_private_text()"]
        ensure_safe["ensure_no_symlink_path()"]
    end

    subgraph Security["OS Permissions"]
        P600["0o600 (Owner Only)"]
        P700["0o700 (Owner Only Dir)"]
    end

    atomic_write --> ensure_safe
    atomic_write --> P600
    ensure_safe -->|Prevents| SymlinkAttack["Symlink Race Condition"]
```

Sources: [agent_reach/cookie_extract.py:115-156](), [agent_reach/utils/paths.py:71-136](), [tests/test_cookie_extract_perms.py:44-92]()

---

## Platform-Specific Details

### Twitter / X
Twitter authentication requires `auth_token` and `ct0`. When configured, Agent Reach automatically syncs these to:
- `~/.config/bird/credentials.env`: Used by the `bird` Node.js CLI [agent_reach/cookie_extract.py:141-156]().
- `~/.config/xfetch/session.json`: Used by the `bird-x` / `xfetch` backend [agent_reach/cookie_extract.py:115-135]().

### XiaoHongShu (XHS)
XHS requires a complete cookie set. 
- `agent-reach configure xhs-cookies` parses the Header String into a JSON array of cookies [agent_reach/guides/setup-xiaohongshu.md:31-35]().
- If a `xiaohongshu-mcp` Docker container is running, the CLI attempts to import cookies into the container [agent_reach/guides/setup-xiaohongshu.md:34-36]().
- Otherwise, it writes to `~/.agent-reach/xhs-cookies.json` with `0o600` permissions [tests/test_private_file_writes.py:119-123]().

### Bilibili and Xueqiu
- **Bilibili:** Targets `SESSDATA` and `bili_jct` [agent_reach/cookie_extract.py:48-48]().
- **Xueqiu:** Targets `xq_a_token` [agent_reach/cookie_extract.py:54-54]().

---

## Security and Permissions
Agent Reach follows a strict security model for credentials:
- **Atomic Writes:** Uses `atomic_write_private_text` to prevent partial writes or corruption [agent_reach/utils/paths.py:71-136]().
- **Symlink Protection:** The `ensure_no_symlink_path` helper rejects paths that contain symlinks to prevent credential redirection attacks [agent_reach/utils/paths.py:34-47]().
- **POSIX Permissions:** Files like `credentials.env` and `session.json` are strictly set to `0o600` [tests/test_cookie_extract_perms.py:44-50]().
- **Shell Injection Guard:** When writing `bird/credentials.env`, values are shell-quoted to prevent arbitrary command execution during `source` operations [tests/test_cookie_extract_perms.py:94-133]().

Sources: [agent_reach/utils/paths.py:71-136](), [tests/test_private_file_writes.py:19-26](), [tests/test_cookie_extract_perms.py:94-133]()

---

# Page: Proxy Configuration

# Proxy Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/channels/twitter.py](agent_reach/channels/twitter.py)
- [agent_reach/config.py](agent_reach/config.py)
- [tests/test_config.py](tests/test_config.py)
- [tests/test_twitter_channel.py](tests/test_twitter_channel.py)

</details>



This page documents how Agent Reach applies proxy settings to specific channels that are commonly blocked when running on server IPs. It covers the general proxy configuration key, per-channel proxy behavior, and the `undici` `EnvHttpProxyAgent` bootstrap mechanism used to route the `bird` CLI's Node.js `fetch()` through the proxy.

For general configuration key management and credential storage, see [4. Configuration](). For cookie-based authentication (Twitter, Instagram, XiaoHongShu), see [4.1. Cookie Export Guide]().

---

## Why Proxies Are Needed

Several platforms actively block requests originating from datacenter or server IP ranges. Agent Reach identifies these as "Risk Control" platforms that require residential or ISP proxies for reliable access.

| Platform | Channel | Blocking Behavior |
|---|---|---|
| Reddit | `RedditChannel` | Returns 403 (Forbidden) or 429 (Too Many Requests) on server IPs. |
| Bilibili | `BilibiliChannel` | Server-side IP blocking on search and content APIs. |
| XiaoHongShu | `XiaoHongShuChannel` | IP risk control on Docker MCP server. |
| Twitter/X | `TwitterChannel` | Node.js `fetch()` silently fails or returns "fetch failed" without specific proxy injection. |

Sources: [agent_reach/channels/twitter.py:34-37](), [agent_reach/config.py:106-112]()

---

## Setting the Proxy

The proxy configuration is managed via the `Config` class and stored in `~/.agent-reach/config.yaml` [agent_reach/config.py:102-103]().

### Configuration Commands

Users can set the proxy using the CLI:

```bash
# General proxy for most channels
agent-reach configure proxy http://user:pass@host:port

# Specific proxy for Reddit (recommended ISP/Residential proxy)
agent-reach configure reddit_proxy http://user:pass@host:port
```

### Internal Resolution Logic

The `Config.get()` method [agent_reach/config.py:159-168]() resolves values using a specific priority:
1. **Config File:** Checks `~/.agent-reach/config.yaml` first.
2. **Environment Variables:** Falls back to the uppercase version of the key (e.g., `PROXY` or `GITHUB_TOKEN`).

The `Config.save()` method [agent_reach/config.py:152-157]() ensures that settings are written atomically with owner-only permissions (`0o600`) to protect proxy credentials [agent_reach/config.py:61-62]().

Sources: [agent_reach/config.py:102-103](), [agent_reach/config.py:152-168](), [agent_reach/config.py:61-62]()

---

## Per-Channel Proxy Application

The following diagram maps how configuration keys in the `Config` class are applied to different backend entities.

**Proxy Data Flow and Entity Mapping:**

```mermaid
flowchart TD
    subgraph ConfigSpace ["Config Entity Space (agent_reach/config.py)"]
        cfg_obj["Config Class Instance"]
        proxy_val["key: 'proxy'"]
        reddit_val["key: 'reddit_proxy'"]
    end

    subgraph ChannelSpace ["Channel Execution Space"]
        twitter_ch["TwitterChannel (twitter.py)"]
        reddit_ch["RedditChannel"]
        bili_ch["BilibiliChannel"]
    end

    subgraph BackendSpace ["Native Tool Space"]
        bird_cli["bird CLI (NODE_OPTIONS injection)"]
        req_lib["Python 'requests' (proxies=...)"]
        ytdlp["yt-dlp (--proxy flag)"]
    end

    cfg_obj -- "get('proxy')" --> twitter_ch
    cfg_obj -- "get('reddit_proxy')" --> reddit_ch
    cfg_obj -- "get('proxy')" --> bili_ch

    twitter_ch --> bird_cli
    reddit_ch --> req_lib
    bili_ch --> ytdlp
```

Sources: [agent_reach/config.py:159-168](), [agent_reach/channels/twitter.py:12-31]()

---

## Twitter/bird CLI: The undici Proxy Bootstrap

The `bird` CLI (a legacy backend for `TwitterChannel`) relies on Node.js native `fetch()`. Unlike many tools, native `fetch()` does not automatically respect `HTTP_PROXY` environment variables.

Agent Reach implements a "Bootstrap Injection" strategy to solve this. The `twitter_cli_child_env` function [agent_reach/channels/twitter.py:12-31]() prepares the environment for child processes, ensuring credentials like `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` are passed correctly from the `Config` store [agent_reach/channels/twitter.py:22-25]().

**Implementation Logic:**
1. Agent Reach detects if a proxy is configured in `Config`.
2. It identifies if the `bird` or `birdx` command is being used [agent_reach/channels/twitter.py:129-130]().
3. It passes credentials via environment variables to the child process [agent_reach/channels/twitter.py:30-31]().

**Sequence of Proxy Injection:**

```mermaid
sequenceDiagram
    participant AR as "AgentReach Core"
    participant TC as "TwitterChannel (twitter.py)"
    participant CFG as "Config (config.py)"
    participant Node as "Node.js Runtime (bird)"

    AR->>TC: "Invoke check()/read()"
    TC->>CFG: "twitter_cli_child_env(config)"
    CFG-->>TC: "Return {TWITTER_AUTH_TOKEN, ...}"
    TC->>TC: "Check for 'proxy' in Config"
    TC->>Node: "Spawn process with injected Env"
    Node->>Node: "Execute bird commands"
```

Sources: [agent_reach/channels/twitter.py:12-31](), [agent_reach/channels/twitter.py:127-142]()

---

## Reddit Proxy Requirements

Reddit is particularly aggressive against datacenter IPs. The `Config` system is designed to handle specific overrides like `reddit_proxy` to bypass these blocks.

**Security and Validation:**
- **Redaction:** When `Config.to_dict()` is called (e.g., for logging), sensitive keys including those containing `proxy` are redacted [tests/test_config.py:121]().
- **Permissions:** The configuration file containing these proxy URLs is strictly protected using `os.chmod` to `stat.S_IRUSR | stat.S_IWUSR` [agent_reach/config.py:61-62]().
- **Resolution:** If `reddit_proxy` is not found in the YAML file, the system checks for an environment variable named `REDDIT_PROXY` [agent_reach/config.py:165-167]().

Sources: [agent_reach/config.py:61-62](), [agent_reach/config.py:165-168](), [tests/test_config.py:121]()

---

## Troubleshooting

### Twitter CLI Verification
The `TwitterChannel.check()` method [agent_reach/channels/twitter.py:43-81]() is designed to be "Safe". It avoids executing live commands like `twitter status` if it might trigger an automatic browser cookie fallback that violates the `Cookie-Editor`-only policy [agent_reach/channels/twitter.py:86-89]().

- **Warning "已配置" (Configured):** Means credentials exist in `config.yaml` but `doctor` did not execute a live network test to avoid triggering upstream fallbacks [agent_reach/channels/twitter.py:99-103]().
- **Warning "未检测到显式" (Not Detected):** Means the CLI is installed but `TWITTER_AUTH_TOKEN` is missing from both environment and config [agent_reach/channels/twitter.py:104-109]().

### Configuration Integrity
If proxy settings are not taking effect, verify the config file permissions. Agent Reach will reject configuration files that are symlinks to prevent credential redirection attacks [agent_reach/config.py:39-43]().

Sources: [agent_reach/channels/twitter.py:83-109](), [agent_reach/config.py:39-43](), [tests/test_twitter_channel.py:31-55]()

---

# Page: mcporter Setup

# mcporter Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/core.py](agent_reach/core.py)
- [agent_reach/guides/setup-twitter.md](agent_reach/guides/setup-twitter.md)
- [agent_reach/integrations/mcp_server.py](agent_reach/integrations/mcp_server.py)
- [config/mcporter.json](config/mcporter.json)
- [tests/test_mcporter_config.py](tests/test_mcporter_config.py)

</details>



This page covers what `mcporter` is, how Agent Reach uses it as an MCP bridge, the `config/mcporter.json` configuration structure, and the setup steps for each dependent channel. It also documents the Agent Reach MCP server which exposes internal diagnostics.

For broader configuration of Agent Reach credentials and settings, see [Configuration](). For details on the individual channels that use mcporter (XiaoHongShu, Exa, LinkedIn), see [Channels]().

---

## What mcporter Is

`mcporter` is a command-line tool (`npm install -g mcporter`) that acts as a bridge between a shell process and one or more **MCP servers** (Model Context Protocol servers). Agent Reach's channel implementations invoke it as a subprocess to call tools exposed by remote or local MCP servers.

The two key operations Agent Reach performs via `mcporter`:

| Command | Purpose |
|---|---|
| `mcporter list` | Lists all configured MCP server names; used to check if a server is registered |
| `mcporter call <expr>` | Calls a tool on a configured MCP server, e.g. `exa.web_search_exa(query: "foo")` |
| `mcporter config add <name> <url>` | Registers an MCP server endpoint by name |

mcporter is installed via npm and must be on `PATH` for mcporter-dependent channels to function.

Sources: [agent_reach/integrations/mcp_server.py:7-9](), [config/mcporter.json:1-11]()

---

## Configuration and Inspection

### Configuration Structure (`config/mcporter.json`)
The repository ships a reference configuration at `config/mcporter.json` [config/mcporter.json:1-11](). This file uses the `mcpServers` key to declare named MCP server endpoints.

```json
{
  "mcpServers": {
    "exa": {
      "baseUrl": "https://mcp.exa.ai/mcp"
    },
    "xiaohongshu": {
      "baseUrl": "http://localhost:18060/mcp"
    }
  },
  "imports": []
}
```

| Field | Type | Description |
|---|---|---|
| `mcpServers` | object | Map of logical server name → endpoint config |
| `mcpServers.<name>.baseUrl` | string | HTTP(S) URL of the MCP server's endpoint |
| `imports` | array | Additional config files to merge |

Sources: [config/mcporter.json:1-11]()

### Configuration Inspection Helper
Agent Reach provides an `inspect_mcporter_config()` helper [tests/test_mcporter_config.py:12-12]() to read and validate the configuration without actually starting the `mcporter` process. This utility:
- Merges home-directory (`~/.mcporter/mcporter.json`) and project-level configurations [tests/test_mcporter_config.py:24-52]().
- Respects the `MCPORTER_CONFIG` environment variable for explicit overrides [tests/test_mcporter_config.py:54-76]().
- Enforces security by rejecting symlinks to prevent unauthorized configuration injection [tests/test_mcporter_config.py:86-120]().
- Returns a `McporterConfigInspection` object containing `server_names` and the configuration `source`.

Sources: [tests/test_mcporter_config.py:1-158]()

---

## Channels That Depend on mcporter

**Channel-to-MCP-server mapping:**

```mermaid
graph LR
    mcporter["mcporter\n(npm global binary)"]

    subgraph "Remote MCP Servers"
        exa_mcp["exa\nhttps://mcp.exa.ai/mcp"]
    end

    subgraph "Local MCP Servers"
        xhs_mcp["xiaohongshu\nhttp://localhost:18060/mcp"]
        li_mcp["linkedin\nmcp-server-linkedin"]
    end

    subgraph "agent_reach/channels/"
        ExaSearchChannel["ExaSearchChannel"]
        XiaoHongShuChannel["XiaoHongShuChannel"]
        LinkedInChannel["LinkedInChannel"]
    end

    ExaSearchChannel -->|"mcporter call exa.*"| mcporter
    XiaoHongShuChannel -->|"mcporter call xiaohongshu.*"| mcporter
    LinkedInChannel -->|"mcporter call linkedin.*"| mcporter

    mcporter --> exa_mcp
    mcporter --> xhs_mcp
    mcporter --> li_mcp
```

Sources: [config/mcporter.json:1-11](), [agent_reach/integrations/mcp_server.py:7-9]()

---

## Agent Reach's Own MCP Server

Agent Reach includes its own MCP server implementation at `agent_reach/integrations/mcp_server.py` [agent_reach/integrations/mcp_server.py:1-79](). This server allows external AI agents (like Claude Code or Cursor) to inspect the health and capabilities of Agent Reach via the MCP protocol.

### Implementation Details
- **Class/Function**: `create_server()` [agent_reach/integrations/mcp_server.py:29-69]() initializes an MCP `Server` instance.
- **Dependency**: Requires `mcp` Python package (`pip install agent-reach[mcp]`) [agent_reach/integrations/mcp_server.py:19-26]().
- **Transport**: Uses `stdio_server` for communication [agent_reach/integrations/mcp_server.py:74-75]().

### Exposed Tools
| Tool Name | Description | Implementation |
|---|---|---|
| `get_status` | Returns which channels are installed and active. | Calls `AgentReach.doctor_report()` [agent_reach/integrations/mcp_server.py:54-55]() |

### Data Flow for get_status
```mermaid
sequenceDiagram
    participant Agent as "AI Agent (e.g. Claude)"
    participant MCPS as "agent_reach/integrations/mcp_server.py"
    participant AR as "agent_reach/core.py:AgentReach"
    participant Doc as "agent_reach/doctor.py:check_all"

    Agent->>MCPS: "call_tool('get_status')"
    MCPS->>AR: "doctor_report()"
    AR->>Doc: "check_all(self.config)"
    Doc-->>AR: "Status Dict (ok/warn/off)"
    AR-->>MCPS: "Formatted Report String"
    MCPS-->>Agent: "TextContent(text=...)"
```

Sources: [agent_reach/integrations/mcp_server.py:29-79](), [agent_reach/core.py:23-42]()

---

## Setup by Channel

### Exa Search (Remote server)
Exa uses a publicly hosted MCP endpoint. 
```bash
npm install -g mcporter
mcporter config add exa https://mcp.exa.ai/mcp
```
The configuration is stored in `mcporter.json` under the `exa` key [config/mcporter.json:3-5]().

### XiaoHongShu (Local Docker server)
XiaoHongShu requires a locally running MCP server (`xiaohongshu-mcp`) exposed over HTTP.
```bash
npm install -g mcporter
# Start the MCP server (Docker required)
docker run -d --name xiaohongshu-mcp -p 18060:18060 xpzouying/xiaohongshu-mcp
# Register the local endpoint
mcporter config add xiaohongshu http://localhost:18060/mcp
```
The `XiaoHongShuChannel` requires an `xsec_token` for note fetching and uses the MCP server to verify login status.

Sources: [config/mcporter.json:6-8](), [agent_reach/integrations/mcp_server.py:7-9]()

---

## Diagnostics

The `AgentReach.doctor()` method [agent_reach/core.py:34-37]() evaluates channel health. For mcporter-dependent channels, the logic typically checks:
1. If the `mcporter` binary exists on the system.
2. If the required server (e.g., `exa`, `xiaohongshu`) is present in the `mcporter` configuration.
3. If the server is reachable and (for authenticated platforms) the session is valid.

Sources: [agent_reach/core.py:34-42](), [agent_reach/integrations/mcp_server.py:46-49]()

---

# Page: AI Agent Integration

# AI Agent Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent_reach/skill/SKILL.md](agent_reach/skill/SKILL.md)
- [agent_reach/skill/SKILL_en.md](agent_reach/skill/SKILL_en.md)
- [agent_reach/skill/references/career.md](agent_reach/skill/references/career.md)
- [agent_reach/skill/references/search.md](agent_reach/skill/references/search.md)
- [agent_reach/skill/references/web.md](agent_reach/skill/references/web.md)
- [tests/test_skill_command.py](tests/test_skill_command.py)

</details>



This page documents how AI agents (Claude Code, Cursor, OpenClaw, Windsurf, and others) discover and use agent-reach capabilities through the `SKILL.md` skill registration mechanism. It covers the skill file structure, installation into agent skill directories, natural language trigger mapping, and the expected agent interaction model.

---

## Overview

Agent Reach is a CLI tool, but it is primarily intended to be driven by an AI agent. The integration works through a single mechanism: a file called `SKILL.md` that is installed into the agent's skill directory. Once installed, the agent reads this file to learn what agent-reach can do, when to invoke it, and how to invoke it.

### Agent Interaction Flow
```mermaid
sequenceDiagram
    participant "User" as User
    participant "AI Agent" as Agent
    participant "SKILL.md" as Skill Definition
    participant "agent-reach CLI" as CLI / Backends

    User->>Agent: "Search Twitter for opinions on this product"
    Agent->>Skill Definition: Consult registered skill metadata
    Skill Definition-->>Agent: Trigger matched; Use "twitter search" or "agent-reach search-twitter"
    Agent->>CLI: twitter search "product opinions" -n 10
    CLI-->>Agent: Structured JSON/Text results
    Agent-->>User: Summarized response with citations
```

Sources: [agent_reach/skill/SKILL.md:1-18](), [agent_reach/skill/SKILL.md:91-92]()

---

## The SKILL.md File

`SKILL.md` is the contract between the agent-reach package and any agent that supports the skills protocol. It lives at `agent_reach/skill/SKILL.md` (and `SKILL_en.md` for English environments) and serves as the primary instruction set for the agent.

### Frontmatter: Registration Metadata
The file begins with YAML frontmatter that defines the skill's identity and activation triggers.

[agent_reach/skill/SKILL.md:1-24]()

| Field | Purpose |
|---|---|
| `name` | Unique identifier (`agent-reach`) |
| `description` | Tells the agent *when* to use this skill (e.g., "MUST USE when user wants to research/search/look up anything") |
| `metadata` | Integration-specific data (e.g., `homepage` link) |

### Skill Body: Command Reference
The body of the file provides the agent with specific shell commands to execute for different platforms. The agent is encouraged to use direct backends or `mcporter` for MCP-based channels.

**Key Command Examples for Agents:**
- **Web Search (Exa via mcporter):** `mcporter call exa.web_search_exa query="query" numResults=5` [agent_reach/skill/SKILL.md:59-61]()
- **Twitter (twitter-cli):** `twitter search "query" -n 10` [agent_reach/skill/SKILL.md:91-92]()
- **Reddit (OpenCLI):** `opencli reddit search "query" -f yaml` [agent_reach/skill/SKILL.md:94-95]()
- **GitHub Search:** `gh search repos "query" --sort stars --limit 10` [agent_reach/skill/SKILL.md:66-67]()

Sources: [agent_reach/skill/SKILL.md:57-106](), [agent_reach/skill/SKILL_en.md:61-112]()

---

## Skill Installation

Installation is handled by internal CLI helpers that detect common agent skill directories and copy the localized markdown files.

### Implementation: `_install_skill` and `_uninstall_skill`
The functions `_install_skill()` and `_uninstall_skill()` manage the lifecycle of the `SKILL.md` file within the agent's environment.

- **Detection:** It looks for directories like `~/.openclaw/skills/` or paths defined by environment variables. [tests/test_skill_command.py:126-151]()
- **Localization:** The package includes both `SKILL.md` (Default/Chinese) and `SKILL_en.md` (English). [tests/test_skill_command.py:19-28]()
- **Action:** It creates an `agent-reach` subdirectory and populates it with the instruction set. [tests/test_skill_command.py:152-162]()

### Installation Logic Flow
```mermaid
graph TD
    subgraph "Source (agent_reach/skill/)"
        src1["SKILL.md"]
        src2["SKILL_en.md"]
    end

    subgraph "CLI Execution"
        cmd["agent-reach install"]
        fn["_install_skill() in cli.py"]
    end

    subgraph "Target Skill Dirs"
        oc["~/.openclaw/skills/agent-reach/"]
        cursor["~/Library/Application Support/Cursor/skills/agent-reach/"]
    end

    src1 --> cmd
    src2 --> cmd
    cmd --> fn
    fn --> oc
    fn --> cursor
```

Sources: [tests/test_skill_command.py:19-162](), [agent_reach/cli.py:13-13]()

---

## Natural Language to Code Mapping

This section illustrates how the agent bridges the gap between a user's natural language request and the specific code entities or commands defined in `agent-reach`.

### Intent Mapping Table

| User Prompt (Natural Language) | Agent Action (Command) | Internal Logic / Backend |
|---|---|---|
| "Read this link" | `curl -s "https://r.jina.ai/URL"` | `WebChannel` via Jina Reader |
| "Search Twitter for AI news" | `twitter search "AI news"` | `TwitterChannel` via `bird` CLI |
| "Find LinkedIn jobs" | `mcporter call linkedin.search_jobs ...` | `LinkedInChannel` via MCP |
| "Transcribe this podcast" | `transcribe.sh <url>` | `XiaoyuzhouChannel` (Groq Whisper) |
| "Search Bilibili" | `bili search "query" --type video` | `BilibiliChannel` via `bili-cli` |

### Bridge: Natural Language to Code Entity Space
```mermaid
graph LR
    subgraph "Natural Language Space (Triggers)"
        t1["'research this topic' / '全网调研'"]
        t2["'look up jobs' / '搜招聘'"]
        t3["'search github' / '搜代码'"]
    end

    subgraph "Command / Entity Space (SKILL.md & References)"
        c1["mcporter call exa.web_search_exa"]
        c2["mcporter call linkedin.search_jobs"]
        c3["gh search repos"]
    end

    subgraph "Code Implementation"
        ch1["exa.py: ExaSearchChannel"]
        ch2["mcp_server.py: mcporter bridge"]
        ch3["github.py: GitHubChannel"]
    end

    t1 --> c1 --> ch1
    t2 --> c2 --> ch2
    t3 --> c3 --> ch3
```

Sources: [agent_reach/skill/SKILL.md:4-11](), [agent_reach/skill/SKILL.md:57-77](), [agent_reach/skill/references/career.md:17-18](), [agent_reach/skill/references/search.md:9-12]()

---

## Agent Interaction Model

### Diagnostic-Driven Interaction
Agents are instructed to perform a health check before acting on platforms requiring login or multi-backend routing.

1. **Trigger:** User asks to search a specific platform (e.g., Reddit).
2. **Action:** Agent runs `agent-reach doctor --json`. [agent_reach/skill/SKILL.md:32-35]()
3. **Analysis:** Agent checks the `active_backend` field. If `null`, it uses the fallback/retry chains defined in the `references/` directory. [agent_reach/skill/SKILL_en.md:30-34]()
4. **Execution:** Agent announces the backend being used (e.g., "Using agent-reach, platform Reddit via backend OpenCLI"). [agent_reach/skill/SKILL_en.md:35-36]()

### Workspace and Safety Rules
To ensure stability, the `SKILL.md` enforces strict operational boundaries:
- **No Workspace Files:** Agents must use `/tmp/` for temporary output and `~/.agent-reach/` for persistent data, never creating files in the project workspace. [agent_reach/skill/SKILL.md:123-124]()
- **Version Watching:** After completing a major task, agents run `agent-reach check-update` and suggest an update command if a new version is available. [agent_reach/skill/SKILL.md:39-43]()
- **Credential Safety:** For platforms like Twitter, agents must provide `TWITTER_AUTH_TOKEN` in the environment without logging or echoing the values. [agent_reach/skill/SKILL.md:81-84]()

### Troubleshooting Model
```mermaid
graph TD
    A["Agent Command Fails"] --> B["Consult 'references/' Retry Chain"]
    B --> C{"Is Backend Available?"}
    C -- "No" --> D["Run 'agent-reach doctor'"]
    C -- "Yes" --> E["Try Fallback (e.g., Jina Reader for LinkedIn)"]
    D --> F["Check active_backend in JSON"]
    F --> G["Report missing config/cookies to User"]
```

Sources: [agent_reach/skill/SKILL.md:32-43](), [agent_reach/skill/references/career.md:23-29](), [agent_reach/skill/SKILL_en.md:85-94]()

---

# Page: Development

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pytest.yml](.github/workflows/pytest.yml)
- [CLAUDE.md](CLAUDE.md)
- [agent_reach/__init__.py](agent_reach/__init__.py)
- [docs/wechat-group-qr.jpg](docs/wechat-group-qr.jpg)
- [pyproject.toml](pyproject.toml)
- [tests/test_opencode_skill.py](tests/test_opencode_skill.py)

</details>



This page is a contributor-oriented overview of how the `agent-reach` package is structured, built, tested, and kept up to date with upstream dependencies. It covers the build system configuration, the included data directories, the test suite, and the development conventions defined in `CLAUDE.md`.

For end-user installation steps, see the Getting Started page ([Getting Started](#1.2)). For detailed dependency and extras documentation, see [Package and Dependencies](#6.1). For the test suite specifics, see [Testing](#6.2). For upstream sync details, see [Upstream Sync](#6.3).

---

## Repository Layout

The repository contains the following top-level directories and files relevant to contributors:

| Path | Purpose |
|---|---|
| `agent_reach/` | Main Python package source [pyproject.toml:65]() |
| `agent_reach/channels/` | All platform implementations inheriting from `BaseChannel` [CLAUDE.md:21-22]() |
| `agent_reach/guides/` | Bundled documentation included in the wheel [pyproject.toml:82]() |
| `agent_reach/skill/` | `SKILL.md` bundled for AI agent skill registration [pyproject.toml:81]() |
| `agent_reach/integrations/` | External protocol bridges (e.g., `mcp_server.py`) [CLAUDE.md:23]() |
| `scripts/` | Maintenance scripts like `sync-upstream.sh` [pyproject.toml:82]() |
| `test.sh` | End-to-end integration test script [CLAUDE.md:12]() |
| `tests/` | Pytest suite (CLI, config, channels, doctor) [CLAUDE.md:26]() |
| `pyproject.toml` | Package metadata, dependencies, and build configuration [pyproject.toml:1-63]() |
| `CLAUDE.md` | Developer guide: commands, structure, and rules [CLAUDE.md:1-44]() |

Sources: [pyproject.toml:60-82](), [CLAUDE.md:16-28]()

---

## Package Build

**Build system diagram — `pyproject.toml` to wheel contents**

```mermaid
flowchart TD
    pyproject["pyproject.toml"]
    hatchling["hatchling\n(build-backend)"]
    pkg["agent_reach/\n(Python source)"]
    guides["agent_reach/guides/\n(data directory)"]
    skill["agent_reach/skill/\n(data directory)"]
    scripts["agent_reach/scripts/\n(data directory)"]
    wheel["agent-reach-*.whl"]
    entrypoint["console_scripts:\nagent-reach = agent_reach.cli:main"]

    pyproject --> hatchling
    hatchling --> pkg
    hatchling --> guides
    hatchling --> skill
    hatchling --> scripts
    hatchling --> wheel
    wheel --> entrypoint
```

Sources: [pyproject.toml:52-53](), [pyproject.toml:60-65](), [.github/workflows/pytest.yml:81-83]()

The build backend is `hatchling` [pyproject.toml:61-62](). The `packages` directive includes the core `agent_reach` directory [pyproject.toml:65](). The CI process verifies that `SKILL.md` and data directories (`guides/`, `scripts/`, `skill/references/`) are correctly bundled into the wheel [ .github/workflows/pytest.yml:81-83]().

The console script entrypoint maps the `agent-reach` command to the `main` function in `agent_reach.cli` [pyproject.toml:52-53]().

### Runtime Dependencies

| Dependency | Minimum Version | Role |
|---|---|---|
| `requests` | 2.28 | HTTP requests and API updates [pyproject.toml:31]() |
| `feedparser` | 6.0 | RSS channel backend [pyproject.toml:32]() |
| `python-dotenv` | 1.0 | Environment variable management [pyproject.toml:33]() |
| `loguru` | 0.7 | Structured logging [pyproject.toml:34]() |
| `pyyaml` | 6.0 | `config.yaml` parsing [pyproject.toml:35]() |
| `rich` | 13.0 | CLI formatting and diagnostics [pyproject.toml:36]() |
| `yt-dlp` | 2026.07.04 | YouTube video/transcript extraction [pyproject.toml:37]() |

Sources: [pyproject.toml:30-38]()

### Optional Extras

| Extra | Packages Added | Enables |
|---|---|---|
| `[browser]` | `playwright>=1.40` | Headless browser capabilities [pyproject.toml:41]() |
| `[cookies]` | `browser-cookie3>=0.19` | `agent-reach configure --from-browser` [pyproject.toml:42]() |
| `[all]` | `playwright`, `mcp[cli]`, `browser-cookie3` | Full feature set including MCP tools [pyproject.toml:43]() |
| `[dev]` | `pytest`, `ruff`, `mypy` | Linting, type checking, and testing [pyproject.toml:44-50]() |

Sources: [pyproject.toml:40-50]()

---

## Developer Conventions (`CLAUDE.md`)

The `CLAUDE.md` file defines the primary rules and conventions for the project:

- **Channel Contract**: Every platform must implement `can_handle(url)`, `read(url)`, `search(query)`, and `check()` [CLAUDE.md:32]().
- **Glue Layer Philosophy**: Agent Reach is a "glue layer" that routes and calls existing tools; it does not reimplement their internals [CLAUDE.md:39]().
- **Version Synchronization**: The version string must match exactly in `pyproject.toml`, `agent_reach/__init__.py`, and `tests/test_cli.py` [CLAUDE.md:40]().
- **Authentication**: For XHS and Twitter, only cookie-based exports are supported to avoid hanging on QR scans [CLAUDE.md:43-44]().

Sources: [CLAUDE.md:29-44](), [agent_reach/__init__.py:4]()

---

## Testing

The test suite consists of automated unit tests and a manual integration script.

| Component | File / Directory | Type | What it tests |
|---|---|---|---|
| Integration | `test.sh` | Shell script | Full CLI lifecycle (install, doctor, read, search) [CLAUDE.md:12]() |
| CLI Logic | `tests/test_cli.py` | Pytest | Arg parsing, version output, and cookie parsing [CLAUDE.md:11]() |
| Diagnostics | `tests/test_doctor.py` | Pytest | Health check logic and report formatting [CLAUDE.md:20]() |
| Skill Registry | `tests/test_opencode_skill.py` | Pytest | `SKILL.md` frontmatter and directory discovery [tests/test_opencode_skill.py:29-56]() |

### Integration Test Flow

**`test.sh` execution flow**

```mermaid
flowchart TD
    start["bash test.sh"]
    venv["Create temp venv\npython3 -m venv"]
    install["pip install -e ."]
    run_doctor["agent-reach doctor"]
    
    subgraph read_tests["Read Tests"]
        web_read["agent-reach read example.com"]
        gh_read["agent-reach read github.com/..."]
        yt_read["agent-reach read youtube.com/..."]
    end
    
    subgraph search_tests["Search Tests"]
        web_search["agent-reach search '...'"]
        gh_search["agent-reach search-github '...'"]
        tw_search["agent-reach search-twitter '...'"]
    end
    
    validate{"Output validation\n(Keyword based)"}
    pass["PASS ✅"]
    fail["FAIL ❌"]
    
    start --> venv --> install --> run_doctor
    run_doctor --> read_tests --> search_tests
    search_tests --> validate
    validate -->|success| pass
    validate -->|failure| fail
```

Sources: [CLAUDE.md:8-15](), [tests/test_opencode_skill.py:15-105]()

For full details on the test suite, see [Testing](#6.2).

---

## Upstream Sync

Channel implementations in `agent_reach/channels/` are tracked against the `runesleo/x-reader` repository. The script `scripts/sync-upstream.sh` automates the comparison and path rewriting.

**Upstream sync workflow**

```mermaid
flowchart TD
    upstream["github.com/runesleo/x-reader\nx_reader/fetchers/"]
    local["agent_reach/channels/"]
    
    diff["diff with path rewrite\nx_reader.fetchers\n→ agent_reach.channels"]
    
    result_changed["📝 CHANGED: diff output"]
    result_ok["✅ All up to date"]
    
    manual["Manual Review:\n1. Update files\n2. Run pytest"]

    upstream --> diff
    local --> diff
    diff -->|"files differ"| result_changed
    diff -->|"no diffs"| result_ok
    result_changed --> manual
```

Sources: [CLAUDE.md:21-22](), [CLAUDE.md:35-39]()

For details on the path rewriting logic and manual merge workflow, see [Upstream Sync](#6.3).

---

# Page: Package and Dependencies

# Package and Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [agent_reach/__init__.py](agent_reach/__init__.py)
- [constraints.txt](constraints.txt)
- [docs/dependency-locking.md](docs/dependency-locking.md)
- [docs/wechat-group-qr.jpg](docs/wechat-group-qr.jpg)
- [pyproject.toml](pyproject.toml)
- [tests/test_core.py](tests/test_core.py)

</details>



This page documents the `agent-reach` package's build configuration, runtime dependencies, optional extras, the `console_scripts` entrypoint, and the non-Python data directories bundled into the wheel. It is derived primarily from `pyproject.toml`.

For context on how the CLI entrypoint is used at runtime, see [CLI Reference](2). For the `agent_reach/skill/` and `agent_reach/guides/` directories bundled as package data, see [AI Agent Integration](5) and [Development](6).

---

## Build System

The package uses [hatchling](https://hatch.pypa.io/) as its PEP 517 build backend [pyproject.toml:60-62]().

| Field | Value |
|---|---|
| `build-backend` | `hatchling.build` |
| `requires` | `["hatchling"]` |

The wheel target is explicitly scoped to the `agent_reach` Python package [pyproject.toml:64-65]().

---

## Package Metadata

The package metadata defines the project identity and supported environments [pyproject.toml:1-28]().

| Field | Value |
|---|---|
| `name` | `agent-reach` |
| `version` | `1.5.0` |
| `requires-python` | `>=3.10` |
| `license` | MIT |
| Supported Python versions | 3.10, 3.11, 3.12 |

Note: The version is synchronized across `pyproject.toml`, `agent_reach/__init__.py`, and the test suite [CLAUDE.md:40-41]().

Sources: [pyproject.toml:1-28](), [agent_reach/__init__.py:4-5](), [CLAUDE.md:6-7]()

---

## Console Scripts Entrypoint

The package registers one command-line entrypoint [pyproject.toml:52-53]().

| Shell command | Python target |
|---|---|
| `agent-reach` | `agent_reach.cli:main` |

When `pip install agent-reach` completes, pip writes an `agent-reach` executable that calls `main()` in `agent_reach/cli.py` [pyproject.toml:53](). This is the sole supported CLI invocation path for end users, while developers can use `python -m agent_reach.cli` [CLAUDE.md:13-14]().

Sources: [pyproject.toml:52-53](), [CLAUDE.md:17-17]()

---

## Runtime Dependencies

These are installed unconditionally with every `pip install agent-reach` [pyproject.toml:30-38]().

| Package | Min Version | Role in agent-reach |
|---|---|---|
| `requests` | 2.28 | HTTP calls for APIs and update checks |
| `feedparser` | 6.0 | RSS feed parsing in `RSSChannel` |
| `python-dotenv` | 1.0 | Environment variable loading for configuration |
| `loguru` | 0.7 | Structured logging across all modules |
| `pyyaml` | 6.0 | Config file read/write (`~/.agent-reach/config.yaml`) |
| `rich` | 13.0 | Terminal output formatting and `doctor` reports |
| `yt-dlp[default]` | 2026.07.04 | Video info and subtitle extraction for YouTube/Bilibili |

**Dependency-to-Code Mapping:**

```mermaid
graph LR
    subgraph ["Core Runtime Dependencies (pyproject.toml)"]
        requests["requests>=2.28"]
        feedparser["feedparser>=6.0"]
        dotenv["python-dotenv>=1.0"]
        loguru["loguru>=0.7"]
        pyyaml["pyyaml>=6.0"]
        rich["rich>=13.0"]
        ytdlp["yt-dlp[default]>=2026.07.04"]
    end

    subgraph ["agent_reach Code Entities"]
        web_ch["WebChannel"]
        rss_ch["RSSChannel"]
        reddit_ch["RedditChannel"]
        youtube_ch["YouTubeChannel"]
        bilibili_ch["BilibiliChannel"]
        config_cls["Config Class"]
        doctor_mod["doctor_report()"]
        cli_mod["cli.py / main()"]
        core_cls["AgentReach Class"]
    end

    requests --> web_ch
    requests --> reddit_ch
    requests --> cli_mod
    feedparser --> rss_ch
    ytdlp --> youtube_ch
    ytdlp --> bilibili_ch
    pyyaml --> config_cls
    rich --> cli_mod
    rich --> doctor_mod
    loguru --> core_cls
    loguru --> cli_mod
    dotenv --> config_cls
```
Sources: [pyproject.toml:30-38](), [agent_reach/core.py:7-7](), [agent_reach/__init__.py:7-9](), [CLAUDE.md:30-33]()

---

## Optional Extras

Named extras gate optional heavy dependencies or specialized toolsets [pyproject.toml:40-50]().

| Extra | Install command | Packages added | Enables |
|---|---|---|---|
| `[browser]` | `pip install agent-reach[browser]` | `playwright>=1.40` | Headless browser automation via Playwright |
| `[cookies]` | `pip install agent-reach[cookies]` | `browser-cookie3>=0.19` | Auto-extraction in `agent-reach configure` |
| `[all]` | `pip install agent-reach[all]` | `playwright`, `mcp[cli]`, `browser-cookie3` | Full feature set including MCP client support |
| `[dev]` | `pip install agent-reach[dev]` | `pytest`, `ruff`, `mypy`, `types-*` | Development, linting, and testing tools |

**Extras-to-Feature Mapping:**

```mermaid
graph TD
    subgraph ["Optional Extras (pyproject.toml)"]
        browser["[browser]"]
        cookies["[cookies]"]
        all["[all]"]
        dev["[dev]"]
    end

    subgraph ["Optional Packages"]
        PW["playwright>=1.40"]
        BC["browser-cookie3>=0.19"]
        MCP["mcp[cli]>=1.0"]
        PT["pytest>=8.0"]
    end

    subgraph ["Code Features"]
        cookie_ext["configure --from-browser"]
        mcp_bridge["mcporter / MCP channels"]
        test_suite["tests/ directory"]
    end

    browser --> PW
    cookies --> BC
    all --> PW
    all --> BC
    all --> MCP
    dev --> PT

    BC --> cookie_ext
    MCP --> mcp_bridge
    PT --> test_suite
```
Sources: [pyproject.toml:40-50](), [CLAUDE.md:9-12]()

---

## Bundled Package Data

Hatchling is configured to include the `agent_reach` package directory in the build [pyproject.toml:64-65](). This includes non-Python assets required for integration:

| Directory | Contents | Consumer |
|---|---|---|
| `agent_reach/guides/` | Usage and troubleshooting guides | Developers and `agent-reach doctor` |
| `agent_reach/skill/` | `SKILL.md` descriptor | AI Agents (Claude, Cursor, etc.) |
| `agent_reach/integrations/` | `mcp_server.py` | MCP-compatible clients |

Sources: [pyproject.toml:64-65](), [CLAUDE.md:21-25]()

---

## Dependency Locking

For development and CI, Agent Reach uses `constraints.txt` to ensure a reproducible dependency baseline [docs/dependency-locking.md:1-4]().

**Stable Environment Setup:**
```bash
pip install -c constraints.txt -e '.[dev]'
```

This pins specific versions (e.g., `requests==2.32.5`, `yt-dlp==2026.07.04`) that have been validated against the current test suite [constraints.txt:5-11]().

Sources: [docs/dependency-locking.md:13-15](), [constraints.txt:1-18]()

---

# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pytest.yml](.github/workflows/pytest.yml)
- [agent_reach/doctor.py](agent_reach/doctor.py)
- [docs/update.md](docs/update.md)
- [test.sh](test.sh)
- [tests/conftest.py](tests/conftest.py)
- [tests/test_cli.py](tests/test_cli.py)
- [tests/test_doctor.py](tests/test_doctor.py)
- [tests/test_integration_script.py](tests/test_integration_script.py)
- [tests/test_opencode_skill.py](tests/test_opencode_skill.py)
- [tests/test_xiaoyuzhou_install.py](tests/test_xiaoyuzhou_install.py)

</details>



This page documents the test suite for Agent Reach, which includes a bash-based end-to-end integration script, a comprehensive set of pytest unit tests, and specialized format validators. The suite ensures functional correctness across CLI commands, channel contracts, and configuration handling.

---

## Test Components Overview

| Component | File | Type | Scope |
|---|---|---|---|
| **Integration** | `test.sh` | Bash E2E | Venv setup, `pip install`, `doctor`, and CLI smoke tests. |
| **CLI Logic** | `tests/test_cli.py` | pytest | Versioning, update checking, cookie parsing, and transcription flags. |
| **Doctor Unit** | `tests/test_doctor.py` | pytest | `check_all()` collection, credential scrubbing, and Rich output. |
| **Xiaoyuzhou** | `tests/test_xiaoyuzhou_install.py` | pytest | Bash syntax validation and secure temp file handling for transcription. |
| **Opencode/Skill** | `tests/test_opencode_skill.py` | pytest | Metadata schema compliance and skill directory discovery. |
| **Core/Config** | `tests/test_core.py`, `tests/test_config.py` | pytest | `AgentReach` core class and `config.yaml` permission enforcement. |
| **CI/CD** | `.github/workflows/pytest.yml` | YAML | Multi-platform (Linux/Windows) and Wheel packaging validation. |

Sources: [test.sh:1-70](), [tests/test_cli.py:1-186](), [tests/test_doctor.py:1-131](), [tests/test_xiaoyuzhou_install.py:1-215](), [tests/test_opencode_skill.py:1-105]()

---

## `test.sh` — End-to-End Integration Script

`test.sh` is a self-contained script that validates the entire installation lifecycle. It creates an isolated environment to ensure the package and its entrypoints are correctly configured.

**E2E Test Flow Diagram:**

```mermaid
flowchart TD
    subgraph Setup["1. Environment Setup"]
        start["bash test.sh"] --> mktemp["mktemp -d (Isolated Home)"]
        mktemp --> venv["python -m venv"]
        venv --> pip["pip install -e .[dev]"]
    end

    subgraph Config["2. CLI Verification"]
        pip --> version_cmd["agent-reach version"]
        version_cmd --> install_safe["agent-reach install --safe"]
        install_safe --> install_dry["agent-reach install --system --dry-run"]
    end

    subgraph Execution["3. Data Integrity"]
        install_dry --> doctor_json["agent-reach doctor --json"]
        doctor_json --> py_assert["python -c 'assert doctor_data'"]
    end

    subgraph Results["4. Repository Tests"]
        py_assert --> pytest_run["pytest tests/ -q"]
        pytest_run --> cleanup["trap cleanup (rm -rf)"]
    end
```

Sources: [test.sh:6-70](), [tests/test_integration_script.py:12-24]()

### Key Integration Checks
*   **Venv Isolation:** The script explicitly exports `HOME` and `XDG_CONFIG_HOME` to the temporary directory to prevent polluting the developer's actual configuration [test.sh:11-14]().
*   **CLI Contract:** It verifies that the `agent-reach` command is available in the path after an editable install and that `doctor --json` returns a valid dictionary [test.sh:58-65]().

---

## Unit Testing: `tests/test_doctor.py`

This module validates the diagnostic engine. It ensures that failures in a single channel do not crash the entire report and that sensitive data is never leaked.

**Doctor Implementation & Security:**

```mermaid
classDiagram
    class TestDoctor {
        +test_check_all_collects_channel_results()
        +test_stale_active_backend_no_leak()
        +test_channel_exception_credentials_scrubbed()
    }
    class doctor_py {
        <<agent_reach.doctor>>
        +check_all(config)
        +format_report(results)
        -_name_msg(r, escape)
    }
    class scrub_util {
        <<agent_reach.utils.text>>
        +scrub_url_credentials(text)
    }

    TestDoctor ..> doctor_py : invokes
    doctor_py ..> scrub_util : filters output through
    doctor_py ..> Rich : renders markup
```

Sources: [agent_reach/doctor.py:16-45](), [tests/test_doctor.py:117-184]()

### Key Security & Robustness Features
*   **Credential Scrubbing:** `test_channel_exception_credentials_are_scrubbed` verifies that if a channel backend throws an error containing a URL with a password (e.g., `https://user:pass@host`), the `doctor` output masks it to `https://***@host` [tests/test_doctor.py:137-161]().
*   **Isolation:** `test_stale_active_backend_does_not_leak_into_errored_result` ensures that a successful `active_backend` from a previous singleton check is cleared if the current check fails [tests/test_doctor.py:117-135]().
*   **Permission Check:** `format_report` includes a Unix-only check that warns the user if `config.yaml` is world-readable (not `0o600`) [agent_reach/doctor.py:118-127]().

---

## CLI and Integration Tests

### `tests/test_cli.py`
This suite covers the `main()` entrypoint and argument parsing logic.
*   **Cookie Parsing:** Tests `_parse_twitter_cookie_input` to ensure it can handle both raw token strings and full `Cookie:` headers [tests/test_cli.py:148-159]().
*   **Transcription Logic:** Validates that the `transcribe` command correctly handles provider fallbacks and output file writing [tests/test_cli.py:91-147]().
*   **Safe Configuration:** Verifies that `agent-reach configure` does not execute live backend checks (like `twitter status`) to remain side-effect free during setup [tests/test_cli.py:160-186]().

### `tests/test_xiaoyuzhou_install.py`
Focuses on the complex transcription pipeline for podcasts.
*   **Script Integrity:** Uses `bash -n` to verify the shell syntax of `transcribe_xiaoyuzhou.sh` [tests/test_xiaoyuzhou_install.py:67-72]().
*   **Security:** Ensures the script uses `mktemp` for secure temporary file creation and enforces `MAX_PAGE_BYTES` and `MAX_AUDIO_BYTES` limits to prevent resource exhaustion [tests/test_xiaoyuzhou_install.py:195-215]().

### `tests/test_opencode_skill.py`
Validates the AI Agent "Skill" registration.
*   **Schema Compliance:** Ensures `SKILL.md` frontmatter contains only fields supported by the OpenCode standard (`name`, `description`, `compatibility`, `metadata`) [tests/test_opencode_skill.py:29-55]().
*   **Directory Discovery:** Tests the automatic detection of `~/.config/opencode/skills/` for global skill installation [tests/test_opencode_skill.py:56-69]().

---

## CI/CD Pipeline

The project uses GitHub Actions (`.github/workflows/pytest.yml`) to ensure cross-platform stability.

| Job | Environment | Purpose |
|---|---|---|
| `test` | Ubuntu (3.10-3.13) | Core pytest suite execution. |
| `windows-test` | Windows Latest | Validates Git Bash paths and `.exe` suffix handling. |
| `wheel-gate` | Ubuntu | Builds a production wheel and verifies that data files like `SKILL.md` and `guides/` are included in the package [github/workflows/pytest.yml:57-93](). |

Sources: [.github/workflows/pytest.yml:8-92](), [docs/update.md:29-108]()

---

# Page: Upstream Sync

# Upstream Sync

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/sync-upstream.sh](scripts/sync-upstream.sh)

</details>



This page documents the `scripts/sync-upstream.sh` script, which is used to track and merge channel implementation updates from an upstream open-source repository. This is a developer/contributor workflow concern.

For information about what channels are and how they are structured, see [Channel Architecture](). For information about the overall development environment, see [Development]().

---

## Purpose

Agent Reach's channel implementations are partially derived from the [`runesleo/x-reader`](https://github.com/runesleo/x-reader) project. The script at `scripts/sync-upstream.sh` provides a semi-automated way to identify which channel files have diverged from their upstream counterparts, so a developer can manually review and merge relevant improvements.

The sync is intentionally **manual**: the script only reports differences, it does not apply them automatically. This preserves Agent Reach-specific modifications (import paths, added config integration, etc.) during the merge process.

---

## Repository Mapping

The key relationship is between two directories in two separate repositories:

| Upstream (`runesleo/x-reader`) | Local (`Panniantong/Agent-Reach`) |
|---|---|
| `x_reader/fetchers/` | `agent_reach/channels/` |
| Import prefix: `x_reader.fetchers` | Import prefix: `agent_reach.channels` |

The upstream branch tracked is `main`.

Sources: [scripts/sync-upstream.sh:12-16]()

---

## Script Internals

**Script: `scripts/sync-upstream.sh`**

The script workflow has four phases:

1. **Clone** — shallow-clone the upstream repo into a temporary directory [scripts/sync-upstream.sh:25-27]()
2. **Validate** — confirm that `x_reader/fetchers/` still exists in the upstream (guards against upstream restructuring) [scripts/sync-upstream.sh:29-33]()
3. **Compare** — for each `.py` file in the upstream fetchers directory, diff it against the local channel file of the same name, normalizing import paths before comparing [scripts/sync-upstream.sh:40-58]()
4. **Report** — print a diff summary and emit the exact `cp` + `sed` commands needed to apply each file [scripts/sync-upstream.sh:60-72]()

**Import path normalization in the diff:**

When comparing files, the script rewrites the upstream import prefix on-the-fly using `sed` before passing it to `diff`:

```bash
sed 's/x_reader\.fetchers/agent_reach.channels/g'
```

This means a file that differs only in import paths will appear **unchanged** in the comparison output. Only substantive logic differences are surfaced.

Sources: [scripts/sync-upstream.sh:51-53]()

---

## Workflow Diagram

**Upstream Sync Workflow**

```mermaid
flowchart TD
    A["Run scripts/sync-upstream.sh"]
    B["mktemp -d\n(create TMPDIR)"]
    C["git clone --depth 1\nrunesleo/x-reader → TMPDIR/upstream"]
    D{"TMPDIR/upstream/\nx_reader/fetchers/\nexists?"}
    E["Exit: upstream structure changed"]
    F["For each *.py in\nx_reader/fetchers/"]
    G{"Matching file in\nagent_reach/channels/?"}
    H["Report: NEW file"]
    I["sed rewrite:\nx_reader.fetchers →\nagent_reach.channels"]
    J{"diff -q\nupstream vs local"}
    K["Report: CHANGED\nprint head -20 of diff"]
    L["No action: files match"]
    M{"CHANGES > 0?"}
    N["Print: all channels up to date"]
    O["Print merge instructions:\ncp + sed commands"]
    P["Developer manually reviews\nand applies changes"]
    Q["Run tests, commit"]

    A --> B --> C --> D
    D -- No --> E
    D -- Yes --> F
    F --> G
    G -- No --> H --> M
    G -- Yes --> I --> J
    J -- differs --> K --> M
    J -- same --> L --> M
    M -- No --> N
    M -- Yes --> O --> P --> Q
```

Sources: [scripts/sync-upstream.sh:22-72]()

---

## Comparison Logic Detail

The comparison logic in the script processes each upstream file as follows:

**File Classification**

| Condition | Output Label | Meaning |
|---|---|---|
| File exists upstream but not in `agent_reach/channels/` | `🆕 NEW` | Upstream added a new fetcher; consider porting it |
| File exists in both, content differs (after import rewrite) | `📝 CHANGED` | Upstream has logic changes worth reviewing |
| File exists in both, content matches (after import rewrite) | *(silent)* | In sync; no action needed |

For changed files, the script prints the first 20 lines of the unified diff (`diff --color -u ... | head -20`) followed by an ellipsis, giving a quick overview without overwhelming the terminal.

Sources: [scripts/sync-upstream.sh:40-58]()

---

## Manual Merge Instructions

When changes are detected, the script emits the exact commands needed to apply a specific upstream file:

```sh
cp $TMPDIR/upstream/x_reader/fetchers/FILENAME.py agent_reach/channels/FILENAME.py
sed -i 's/x_reader\.fetchers/agent_reach.channels/g' agent_reach/channels/FILENAME.py
```

After applying:
1. Review the diff manually — the upstream may not have Agent Reach-specific config integration, proxy support, or fallback channels.
2. Run the test suite. See [Testing]() for the test runner.
3. Commit the updated channel file.

> **Important:** The upstream files use raw `x_reader.fetchers` import paths. The `sed` substitution in the merge command handles the rename. Forgetting this step will produce broken imports.

Sources: [scripts/sync-upstream.sh:63-72]()

---

## Structural Diagram: Code Entities

**Entities involved in the sync process**

```mermaid
graph LR
    subgraph upstream["runesleo/x-reader (GitHub)"]
        UF["x_reader/fetchers/*.py\n(upstream channel implementations)"]
        UB["branch: main"]
    end

    subgraph script["scripts/sync-upstream.sh"]
        VAR_UPSTREAM["UPSTREAM_REPO=\nrunesleo/x-reader"]
        VAR_BRANCH["UPSTREAM_BRANCH=main"]
        VAR_UDIR["UPSTREAM_DIR=\nx_reader/fetchers"]
        VAR_LDIR["LOCAL_DIR=\nagent_reach/channels"]
        SED["sed rewrite:\nx_reader.fetchers →\nagent_reach.channels"]
        DIFF["diff -q (compare)"]
    end

    subgraph local["Panniantong/Agent-Reach (local)"]
        LC["agent_reach/channels/*.py\n(local channel implementations)"]
    end

    UB --> UF
    UF -->|"shallow clone"| script
    VAR_UPSTREAM --> VAR_UDIR
    VAR_UDIR --> SED --> DIFF
    VAR_LDIR --> DIFF
    DIFF -->|"reports delta"| LC
```

Sources: [scripts/sync-upstream.sh:12-16]()

---

## Environment and Prerequisites

The script has minimal requirements:

| Requirement | Purpose |
|---|---|
| `bash` | Script interpreter (`set -e` is used) |
| `git` | Shallow-clones the upstream repository |
| `diff` | Compares file content |
| `sed` | Rewrites import paths in-memory before comparison |
| Network access | GitHub must be reachable for the clone step |

The temporary directory is created with `mktemp -d` and is automatically removed on exit via `trap "rm -rf $TMPDIR" EXIT`, so no cleanup is required even if the script is interrupted.

Sources: [scripts/sync-upstream.sh:10-23]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [agent_reach/__init__.py](agent_reach/__init__.py)
- [agent_reach/backends/__init__.py](agent_reach/backends/__init__.py)
- [agent_reach/channels/base.py](agent_reach/channels/base.py)
- [agent_reach/channels/rss.py](agent_reach/channels/rss.py)
- [agent_reach/probe.py](agent_reach/probe.py)
- [docs/wechat-group-qr.jpg](docs/wechat-group-qr.jpg)
- [pyproject.toml](pyproject.toml)
- [tests/test_probe.py](tests/test_probe.py)

</details>



This page provides definitions for codebase-specific terms, jargon, and abbreviations used throughout Agent Reach. It serves as a technical reference for onboarding engineers to understand the internal nomenclature and the specific tools integrated into the system.

## Core Concepts

### Channel
A **Channel** is a pluggable adapter providing a standardized interface for interacting with a specific internet platform (e.g., Twitter, GitHub, Reddit). Each channel is responsible for URL detection, health/dependency status reporting, and content retrieval [agent_reach/channels/base.py:1-23]().

### ALL_CHANNELS
The global registry of all supported platforms. It is an ordered list of instantiated `Channel` objects used for URL routing. The system iterates through this list and calls `can_handle(url)` on each; the first channel to return `True` is selected [agent_reach/channels/__init__.py:31-48]().

### Tier (0/1/2)
Channels are categorized into tiers based on their configuration requirements [agent_reach/channels/base.py:35-35]():
*   **Tier 0 (Zero Config):** Works out-of-the-box with no API keys or login (e.g., V2EX, RSS, Web) [agent_reach/channels/rss.py:11-11]().
*   **Tier 1 (Needs Key/Tool):** Requires a free API key or specific system tool installation (e.g., Twitter via `bird`, YouTube via `yt-dlp`).
*   **Tier 2 (Complex Setup):** Requires cookies, stealth browsers, or local Docker containers (e.g., XiaoHongShu, Instagram).

### can_handle & check()
*   **`can_handle(url)`**: A method implemented by every channel to determine if a given URL belongs to its platform using domain or path pattern matching [agent_reach/channels/rss.py:13-14]().
*   **`check(config)`**: A diagnostic method used by `agent-reach doctor`. It verifies if the required backends are functional and sets the `active_backend` [agent_reach/channels/base.py:61-70]().

### active_backend & ordered_backends
*   **`active_backend`**: The specific backend currently serving a channel (e.g., `bird` for Twitter). Set during `check()` [agent_reach/channels/base.py:38-38]().
*   **`ordered_backends()`**: Returns a candidate list of backends in probe order, prioritizing user overrides defined in `config.yaml` [agent_reach/channels/base.py:45-59]().

### System Entity Mapping

The following diagram illustrates how natural language platform requests map to specific code entities and backend CLI tools.

**Platform Routing and Backend Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        UserPrompt["'Search Twitter for AI news'"]
        UserURL["'Read https://x.com/status/123'"]
    end

    subgraph "Code Entity Space (AgentReach Class)"
        AR["AgentReach.get_channel()"]
        TC["TwitterChannel (Class)"]
        Registry["ALL_CHANNELS (List)"]
    end

    subgraph "Backend Tool Space"
        Bird["bird CLI (@steipete/bird)"]
        Jina["Jina Reader (r.jina.ai)"]
    end

    UserPrompt --> AR
    UserURL --> AR
    AR --> Registry
    Registry --> TC
    TC -- "check()" --> Bird
    TC -- "fallback" --> Jina
```
Sources: [agent_reach/channels/base.py:29-70](), [agent_reach/channels/__init__.py:31-48](), [agent_reach/core.py:7-25]()

---

## Technical Components & Backends

### bird / birdx
A Node.js-based CLI tool (`@steipete/bird`) used as the primary backend for the Twitter channel. It handles authenticated requests for reading tweets and searching [README.md:113-113]().

### mcporter
The **Model Context Protocol (MCP) bridge**. It is a CLI tool that allows Agent Reach to call tools from various MCP servers (like Exa or XiaoHongShu) via a unified interface [README.md:139-143]().

### MCP (Model Context Protocol)
An open standard that enables AI models to connect to external data sources. Agent Reach uses MCP servers for platforms like XiaoHongShu and LinkedIn [README.md:111-119]().

### SKILL.md
A specialized Markdown file containing a structured "Usage Guide" that AI agents (like Claude Code or Cursor) read to understand which commands to run for specific user requests [CLAUDE.md:24-24]().

### doctor
The diagnostic command (`agent-reach doctor`) that executes the `check()` method for all registered channels to report system health [CLAUDE.md:13-13]().

### Jina Reader
A fallback web reading service (`https://r.jina.ai/`) that converts any URL into clean Markdown. It is used as a fallback for several channels [README.md:98-98]().

### yt-dlp
A command-line media downloader used by the `YouTubeChannel` to extract video metadata and subtitles [pyproject.toml:37-37]().

### bili-cli
The primary backend for Bilibili, replacing `yt-dlp` due to risk control blocks. It allows searching and video detail extraction without login [README.md:98-98]().

### OpenCLISiteChannel & _opencli_site.py
A shared base class for platforms that reuse a Chrome browser session via the `opencli` tool (Facebook, Instagram). It handles common browser-bridge logic [agent_reach/backends/opencli.py:10-16]().

### probe_command & ProbeResult
A utility in `agent_reach/probe.py` that distinguishes between missing, broken (stale venv), and timeout failure modes by actually executing the CLI tool [agent_reach/probe.py:47-81]().

---

## Specialized Terms

### xsec_token
A mandatory security token required by the XiaoHongShu (XHS) API for fetching note details [README.md:118-118]().

### Node (V2EX)
In the context of the `V2EXChannel`, a **Node** refers to a specific sub-forum or category (e.g., `python`, `tech`) [README.md:120-120]().

### Cookie Auth
A method where the user exports cookies (via **Cookie-Editor**) and provides them to Agent Reach to bypass login screens [README.md:126-130]().

### Residential Proxy
A recommended configuration for server-side deployments to bypass Data Center IP blocks on platforms like Reddit or Bilibili [README.md:131-131]().

### Zero Config
Platforms that work immediately after `pip install` without any API keys or cookies (Tier 0) [README.md:108-110]().

### Scaffolding
The design philosophy where Agent Reach acts as a "glue layer" that sets up independent upstream tools for the AI agent to call directly [CLAUDE.md:37-39]().

### Groq Whisper
A transcription pipeline used by the `XiaoyuzhouChannel` to convert podcast audio into text using Groq's API [README.md:122-122]().

---

## Internal Logic Flow

The following diagram describes the data flow when the `agent-reach doctor` command is executed to verify system health.

**Doctor Diagnostic Data Flow**
```mermaid
graph LR
    CLI["CLI: agent-reach doctor"]
    Core["agent_reach/core.py"]
    Config["Config Class (~/.agent-reach/config.yaml)"]
    Registry["ALL_CHANNELS"]
    Probe["probe_command()"]
    
    CLI --> Core
    Core --> Config
    Core --> Registry
    
    subgraph "Per Channel Check"
        Registry -- "ch.check(config)" --> Probe
        Probe -- "subprocess.run()" --> SubResult["ProbeResult"]
    end
    
    SubResult --> Report["format_report()"]
    Report --> Terminal["Rich Console Output"]
```
Sources: [agent_reach/probe.py:47-81](), [agent_reach/channels/base.py:61-70](), [CLAUDE.md:17-21]()

### Key Classes
*   **AgentReach**: The central orchestrator for request routing [agent_reach/__init__.py:7-9]().
*   **Config**: Manages `config.yaml`, API keys, and proxy settings [CLAUDE.md:19-19]().
*   **ProbeResult**: Data class containing status ("ok", "broken", etc.) and output from a command probe [agent_reach/probe.py:28-36]().
*   **McporterConfigInspection**: A dataclass returned by `inspect_mcporter_config()` to check MCP tool availability without starting the bridge.

Sources: [README.md:1-154](), [agent_reach/channels/base.py:1-70](), [agent_reach/probe.py:1-120](), [CLAUDE.md:1-44](), [pyproject.toml:1-65]()