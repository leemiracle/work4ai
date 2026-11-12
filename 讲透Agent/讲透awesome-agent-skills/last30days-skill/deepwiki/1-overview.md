<!-- source: DeepWiki mcp.deepwiki.com · repo mvanhorn/last30days-skill · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [CHANGELOG.md](CHANGELOG.md)
- [CONCEPTS.md](CONCEPTS.md)
- [CONFIGURATION.md](CONFIGURATION.md)
- [README.md](README.md)
- [docs/solutions/architecture-patterns/discovery-checkpoint-protocol-design-conventions.md](docs/solutions/architecture-patterns/discovery-checkpoint-protocol-design-conventions.md)
- [docs/solutions/architecture-patterns/discovery-topic-queue-design-conventions.md](docs/solutions/architecture-patterns/discovery-topic-queue-design-conventions.md)
- [docs/solutions/conventions/argparse-optional-value-flag-dispatch-truthiness.md](docs/solutions/conventions/argparse-optional-value-flag-dispatch-truthiness.md)
- [docs/solutions/design-patterns/ranked-output-confidence-floor-honest-empty-state.md](docs/solutions/design-patterns/ranked-output-confidence-floor-honest-empty-state.md)
- [docs/solutions/logic-errors/fusion-source-item-dedupe-by-stream-local-id-drops-enrichment.md](docs/solutions/logic-errors/fusion-source-item-dedupe-by-stream-local-id-drops-enrichment.md)
- [docs/solutions/logic-errors/non-daemon-executor-threads-defeat-wall-clock-budget.md](docs/solutions/logic-errors/non-daemon-executor-threads-defeat-wall-clock-budget.md)
- [gemini-extension.json](gemini-extension.json)
- [skills/last30days/SKILL.md](skills/last30days/SKILL.md)
- [skills/last30days/scripts/lib/env.py](skills/last30days/scripts/lib/env.py)

</details>



## Purpose and Scope

The `/last30days` skill is an agent-led multi-source social research engine designed to aggregate, normalize, score, and synthesize real-time community sentiment and data from the last 30 days [README.md:1-25](). Rather than relying on traditional SEO-prioritized web scraping, the engine queries platforms where real people vote with their attention, engagement, and money (Reddit, X/Twitter, YouTube, TikTok, Hacker News, Polymarket, GitHub, and more) [README.md:23-49]().

This page serves as a high-level overview of the engine's purpose, supported sources, and host integrations. For detailed technical specifications, refer to the child pages:
- For the instruction contract, the eleven output LAWs, preflight checks, and stale-clone self-checks, see [SKILL.md Contract and Output LAWs](#1.1).
- For domain concepts and user-facing query modes (general, comparison, discovery, drill, deep research, confidence floor), see [Key Concepts and Query Modes](#1.2).

Sources: [SKILL.md:1-6](), [README.md:1-49]()

---

## Supported Sources and Host Integrations

The engine bridges disparate walled gardens by utilizing specialized connectors and transport mechanisms, allowing multiple AI agent harnesses to invoke the research pipeline seamlessly.

### Supported Sources
| Source | Signal Type | Transport / Implementation |
| :--- | :--- | :--- |
| **Reddit** | Unfiltered community debates & upvotes | `reddit_public.py`, `reddit_keyless.py`, `reddit_arctic.py` [README.md:71]() |
| **X / Twitter** | Breaking reactions, expert threads | `bird_x.py`, `xai_x.py`, `xapi` backend chain [README.md:72](), [CHANGELOG.md:16-20]() |
| **YouTube** | Deep dives and transcript segments | `youtube.py` (`yt-dlp` integration) [README.md:73](), [CHANGELOG.md:57]() |
| **TikTok / Instagram** | Creator reach & visual culture | `tiktok.py`, `instagram.py` (via ScrapeCreators) [README.md:74-75]() |
| **Hacker News** | Technical developer consensus | `hackernews.py` (Algolia API) [README.md:76]() |
| **Polymarket** | Real-money prediction odds | `polymarket.py` (Gamma API) [README.md:77]() |
| **GitHub** | PR velocity, repo stats, issues | `github.py` search qualifier engine [README.md:78]() |
| **Web & Perplexity** | Editorial coverage & deep search | `grounding.py`, `perplexity.py`, `brave.py` [README.md:88-89]() |

### Host Integrations
The skill is packaged for multi-harness distribution, supporting automatic loading and execution across diverse environments:
*   **Claude Code**: Native plugin marketplace integration via `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` [.claude-plugin/plugin.json:1-30](), [.claude-plugin/marketplace.json:1-24]().
*   **Codex, Cursor, Copilot, and Agent Skills Ecosystem**: Global installation via `npx skills add mvanhorn/last30days-skill -g` [README.md:33-37]().
*   **Gemini CLI**: Configured via `gemini-extension.json` supporting environment variable injection [gemini-extension.json:1-67]().
*   **Grok / OpenClaw**: Supported via execution metadata and platform-specific hooks [SKILL.md:13-68]().
*   **Model Context Protocol (MCP)**: Bundled as a `.mcpb` package utilizing the Go MCP server located in `mcp/`.

Sources: [README.md:33-90](), [.claude-plugin/plugin.json:1-30](), [gemini-extension.json:1-67](), [SKILL.md:13-68]()

---

## Natural Language Space to Code Entity Space Mappings

To bridge high-level user intents with the underlying codebase, the following diagrams associate natural-language concepts and system workflows with exact Python modules, classes, and entry points.

### Diagram 1: Research Execution Pipeline Mapping

Title: "Natural Language to Code Entity Mapping: Research Workflow"
```mermaid
graph TB
    subgraph "Natural Language Space"
        NL_Query["User Research Prompt<br/>'/last30days nvidia earnings'"]
        NL_Plan["Intent & Entity Planning"]
        NL_Retrieve["Multi-Source Retrieval"]
        NL_Synthesize["Ranked Evidence & Markdown Brief"]
    end

    subgraph "Code Entity Space"
        CE_CLI["skills/last30days/scripts/last30days.py:main()"]
        CE_Plan["skills/last30days/scripts/lib/planner.py:ResearchPlanner"]
        CE_Pipe["skills/last30days/scripts/lib/pipeline.py:ResearchPipeline.run()"]
        CE_Fusion["skills/last30days/scripts/lib/fusion.py:weighted_rrf()"]
        CE_Render["skills/last30days/scripts/lib/render.py:render_full()"]
    end

    NL_Query --> CE_CLI
    NL_Plan --> CE_Plan
    CE_CLI --> CE_Plan
    CE_Plan --> CE_Pipe
    NL_Retrieve --> CE_Pipe
    CE_Pipe --> CE_Fusion
    CE_Fusion --> CE_Render
    NL_Synthesize --> CE_Render
```
Sources: [README.md:35-41](), [CONCEPTS.md:13-18]()

### Diagram 2: Connector and Source Architecture Mapping

Title: "Natural Language to Code Entity Mapping: Source Connectors"
```mermaid
graph TB
    subgraph "Natural Language Space"
        Src_Reddit["Reddit Community Threads"]
        Src_X["X / Twitter Posts & Handles"]
        Src_Poly["Polymarket Prediction Odds"]
        Src_Web["Web Search & Grounding"]
    end

    subgraph "Code Entity Space"
        Code_Reddit["skills/last30days/scripts/lib/reddit_public.py"]
        Code_X["skills/last30days/scripts/lib/bird_x.py"]
        Code_Poly["skills/last30days/scripts/lib/polymarket.py"]
        Code_Web["skills/last30days/scripts/lib/grounding.py"]
        Code_Norm["skills/last30days/scripts/lib/normalize.py:normalize_item()"]
    end

    Src_Reddit --> Code_Reddit
    Src_X --> Code_X
    Src_Poly --> Code_Poly
    Src_Web --> Code_Web
    Code_Reddit --> Code_Norm
    Code_X --> Code_Norm
    Code_Poly --> Code_Norm
    Code_Web --> Code_Norm
```
Sources: [README.md:67-90](), [CHANGELOG.md:16-20]()

---

