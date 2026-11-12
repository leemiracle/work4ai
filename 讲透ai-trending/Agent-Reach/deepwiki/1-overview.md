<!-- source: DeepWiki mcp.deepwiki.com · repo Panniantong/Agent-Reach · page 1 Overview · fetched 2026-10-30 -->

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

