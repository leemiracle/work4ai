<!-- source: DeepWiki mcp.deepwiki.com · repo coderabbitai/skills · page 4 Plugin Packaging & Distribution · fetched 2026-10-27 -->

# Plugin Packaging & Distribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DISTRIBUTION_CHANNELS.md](DISTRIBUTION_CHANNELS.md)

</details>



## Purpose and Scope

This page provides a high-level overview of how the CodeRabbit multi-agent skills repository packages and distributes plugins across various host agent ecosystems. CodeRabbit supports diverse agent runtimes (such as Claude Code, Codex, Cursor, Gemini, and Antigravity) by maintaining agent-specific manifest files, shared core skill packages, and branding assets. 

Because this is a parent page, it covers the overarching architecture of plugin distribution and cross-agent packaging. For deep technical specifications, manifest schemas, validation procedures, and asset locations, please refer to the child pages:
- Claude Code & Codex Manifests: See [Claude Code & Codex Manifests](#4.1)
- Cursor, Gemini & Antigravity Manifests: See [Cursor, Gemini & Antigravity Manifests](#4.2)
- Branding Assets: See [Branding Assets](#4.3)
- Distribution Channel Inventory: See [Distribution Channel Inventory](#4.4)

Sources: [DISTRIBUTION_CHANNELS.md:1-30]()

---

## Host Agent Manifest Architecture

To integrate seamlessly into different agent runtimes, the repository houses dedicated configuration manifests and asset references for each supported ecosystem. Each host agent relies on its own configuration file format and loader behavior while consuming the same underlying core logic housed in `skills/` and `agents/`.

```mermaid
graph TD
    sub5["NaturalLanguageSpace"]
    sub6["CodeEntitySpace"]

    sub5 -->| "Multi-Agent Distribution" | sub6
    
    sub6 --> CC["Claude Code Runtime"]
    sub6 --> CX["Codex Agent Runtime"]
    sub6 --> CS["Cursor Editor Runtime"]
    sub6 --> GM["Gemini CLI Runtime"]
    sub6 --> AG["Antigravity CLI Runtime"]

    CC -->| "Loads Manifest" | MCP[".claude-plugin/plugin.json"]
    CX -->| "Loads Manifest" | MCX[".codex-plugin/plugin.json"]
    CS -->| "Loads Manifest" | MCS[".cursor-plugin/plugin.json"]
    GM -->| "Validates Extension" | MGM["gemini-extension.json"]
    AG -->| "Validates Plugin" | MAG["plugin.json"]

    MCP -.-> SK[( "skills/" )]
    MCX -.-> SK
    MCS -.-> SK
    MGM -.-> SK
    MAG -.-> SK
```
*Figure 1: Mapping natural language deployment intent to specific host agent manifest code entities.*

For details on Claude Code and Codex configurations, see [Claude Code & Codex Manifests](#4.1). For Cursor, Gemini, and Antigravity extensions, see [Cursor, Gemini & Antigravity Manifests](#4.2).

Sources: [DISTRIBUTION_CHANNELS.md:11-18]()

---

## Branding & Shared Assets

Visual branding elements—such as logomark SVGs and PNG badges—are centralized within the repository to ensure consistent representation across marketplace listings and IDE integrations. Manifests reference these assets directly during packaging.

```mermaid
graph TD
    sub1["NaturalLanguageSpace"]
    sub2["CodeEntitySpace"]

    sub2 --> AS["assets/ directory"]
    AS --> SVG["SVG Logomark"]
    AS --> PNG["PNG Logos"]
    
    SVG -->| "Referenced By" | MCP[".claude-plugin/plugin.json"]
    PNG -->| "Referenced By" | MCX[".codex-plugin/plugin.json"]
    SVG -->| "Referenced By" | MCS[".cursor-plugin/plugin.json"]
```
*Figure 2: Linking branding assets in Natural Language Space to code entities in the `assets/` directory and host manifests.*

For details on asset dimensions, paths, and manifest bindings, see [Branding Assets](#4.3).

Sources: [DISTRIBUTION_CHANNELS.md:18]()

---

## Distribution Channel Inventory

The repository maintains an operating ledger in `DISTRIBUTION_CHANNELS.md` that tracks active public channels, release statuses, sources of truth, and validation procedures. 

| Channel | Status | Source of Truth |
| :--- | :--- | :--- |
| Skills Package (`npx skills add coderabbitai/skills`) | Live | `README.md`, `skills/` [DISTRIBUTION_CHANNELS.md:11-11]() |
| Tagged GitHub Release Archive | Live (`v1.2.0` pending) | `.github/workflows/release.yml` [DISTRIBUTION_CHANNELS.md:12-12]() |
| Claude Code Plugin Marketplace | Live | `.claude-plugin/plugin.json` [DISTRIBUTION_CHANNELS.md:13-13]() |
| Gemini CLI Native Extension | Release pending | `gemini-extension.json` [DISTRIBUTION_CHANNELS.md:16-16]() |
| Antigravity CLI Native Plugin | GitHub-installable | `plugin.json` [DISTRIBUTION_CHANNELS.md:17-17]() |

For complete channel tracking, maintenance checklists, and validation commands (such as `gemini extensions validate .` and `agy plugin validate .`), see [Distribution Channel Inventory](#4.4).

Sources: [DISTRIBUTION_CHANNELS.md:1-30]()

---

