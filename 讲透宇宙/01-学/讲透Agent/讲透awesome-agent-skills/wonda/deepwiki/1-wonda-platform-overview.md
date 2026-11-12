<!-- source: DeepWiki mcp.deepwiki.com · repo degausai/wonda · page 1 Wonda Platform Overview · fetched 2026-10-26 -->

# Wonda Platform Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [.codex-plugin/plugin.json](.codex-plugin/plugin.json)
- [README.md](README.md)
- [assets/terminal.gif](assets/terminal.gif)
- [assets/terminal.png](assets/terminal.png)
- [gemini-extension.json](gemini-extension.json)
- [mcp/README.md](mcp/README.md)

</details>



The Wonda platform is an AI-native content generation and social automation suite designed to be operated by both human users and AI agents (e.g., Claude Code, Cursor, Codex). It bridges high-level natural language intent with low-level execution of media generation, video editing, and social platform interactions.

## Core Value Proposition

Wonda provides a unified interface for the entire content lifecycle:
*   **AI Generation**: Integration with 20+ models for images, video, music, and speech.
*   **Programmatic Editing**: A "local-first" editing engine for automated video manipulation (captions, overlays, merges).
*   **Social Connectivity**: Unified drivers for LinkedIn, X (Twitter), Reddit, and Instagram.
*   **Agent-Native Design**: Built-in "Skills" and Model Context Protocol (MCP) support, allowing AI agents to discover and execute workflows without manual configuration.

## System Architecture

The platform consists of four primary layers that bridge the gap between user intent and platform execution.

### High-Level Component Interaction

```mermaid
graph TD
    subgraph "Natural Language Space"
        A["AI Agent (Claude, Cursor, etc.)"]
        B["User Terminal"]
    end

    subgraph "Wonda Platform Layer"
        C["MCP Server (@degausai/wonda-mcp)"]
        D["wonda CLI (Binary)"]
        E["Skills Registry (.md files)"]
    end

    subgraph "Execution Layer"
        F["WAB (Wonda Automation Browser)"]
        G["Cloud Twins (Remote Relay)"]
        H["AI Generation APIs"]
    end

    A -->|"Tool Calls"| C
    B -->|"Commands"| D
    C -->|"Executes"| D
    D -->|"Local Action"| F
    D -->|"Remote Action"| G
    D -->|"Inference"| H
    E -.->|"Context Injection"| A
```

**Sources:**
*   `mcp/src/index.ts` (MCP server entry point) [mcp/src/index.ts:1-10]()
*   `README.md` (CLI overview) [README.md:5-12]()
*   `.codex-plugin/plugin.json` (Agent integration) [.codex-plugin/plugin.json:1-32]()

---

## Key Components

### 1. wonda CLI
The core binary providing the command-line interface. It handles credential encryption, rate limiting, and the heavy lifting of media processing via `ffmpeg`.
*   **For details, see [wonda CLI Reference](#2)**.

### 2. MCP Server (`@degausai/wonda-mcp`)
A Model Context Protocol server that exposes Wonda's capabilities as structured tools to AI agents. It supports two modes: `local` (using the local CLI/browser) and `remote` (dispatching to Cloud Twins).
*   **For details, see [MCP Server Architecture](#3)**.

### 3. Wonda Automation Browser (WAB)
A hardened, anti-detect Chromium fork used to bypass bot detection on social platforms. It maintains real browser fingerprints and persistent sessions.
*   **For details, see [Wonda Automation Browser (WAB)](#5)**.

### 4. Cloud Twins
Provisioned remote environments that run WAB sessions 24/7. They allow agents to perform scheduled tasks or high-volume outreach without keeping a local machine active.
*   **For details, see [Cloud Twins & Digital Personas](#6)**.

---

## Bridging Natural Language to Code Entities

The following diagrams illustrate how abstract concepts like "Generation" or "Social Actions" map to specific code implementations within the `wonda-mcp` package.

### Generation & Media Pipeline Mapping

```mermaid
graph LR
    subgraph "Natural Language Intent"
        I1["'Generate a video'"]
        I2["'Add captions to video'"]
    end

    subgraph "MCP Tool Layer"
        T1["generate_video"]
        T2["edit_video"]
    end

    subgraph "Code Implementation"
        C1["registerGenerateTools()"]
        C2["GENERATION_ENDPOINTS"]
        C3["LocalActionSpec (animatedCaptions)"]
    end

    I1 --> T1
    I2 --> T2
    T1 --> C1
    C1 --> C2
    T2 --> C3
```
**Sources:**
*   `mcp/src/tools/generate.ts` (Generation tools) [mcp/src/tools/generate.ts:1-20]()
*   `mcp/src/local-action-registry.ts` (Editing actions) [mcp/src/local-action-registry.ts:1-50]()

### Social Action Dispatch Mapping

```mermaid
graph LR
    subgraph "Platform Action"
        P1["LinkedIn Post"]
        P2["X (Twitter) Like"]
    end

    subgraph "MCP Registry"
        R1["TWIN_ACTION_MANIFEST"]
        R2["LOCAL_ACTIONS"]
    end

    subgraph "Execution Logic"
        E1["remotePlatformExecutor()"]
        E2["runLocalVerb()"]
    end

    P1 --> R1
    P2 --> R2
    R1 --> E1
    R2 --> E2
```
**Sources:**
*   `mcp/src/tools/twin-action-manifest.ts` [mcp/src/tools/twin-action-manifest.ts:1-10]()
*   `mcp/src/local-action-registry.ts` [mcp/src/local-action-registry.ts:1-10]()
*   `mcp/src/local-exec.ts` [mcp/src/local-exec.ts:1-15]()

---

## Getting Started
To begin using the platform, users typically install the CLI and authenticate their accounts. AI agents are then granted access via the MCP server or by installing "Skill" files into the project directory.

*   **Installation**: `curl -fsSL https://wonda.sh/install.sh | bash`
*   **Authentication**: `wonda auth login`
*   **Agent Setup**: `wonda skill install -o .`

For a complete walkthrough, see **[Getting Started & Installation](#1.1)** and **[AI Agent Integration (Skills & Plugins)](#1.2)**.

---

