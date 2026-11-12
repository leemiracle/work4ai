<!-- source: DeepWiki mcp.deepwiki.com · repo anomalyco/opencode · page 1 Overview · fetched 2026-10-27 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [bun.lock](bun.lock)
- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/console/app/package.json](packages/console/app/package.json)
- [packages/console/app/src/app.tsx](packages/console/app/src/app.tsx)
- [packages/console/app/src/style/token/font.css](packages/console/app/src/style/token/font.css)
- [packages/core/src/plugin/skill/opencode.md](packages/core/src/plugin/skill/opencode.md)
- [packages/desktop/package.json](packages/desktop/package.json)
- [packages/function/package.json](packages/function/package.json)
- [packages/plugin/package.json](packages/plugin/package.json)
- [packages/schema/script/config-schema.ts](packages/schema/script/config-schema.ts)
- [packages/schema/script/config-v1.json](packages/schema/script/config-v1.json)
- [packages/ui/package.json](packages/ui/package.json)
- [packages/web/astro.config.mjs](packages/web/astro.config.mjs)
- [packages/web/package.json](packages/web/package.json)
- [packages/web/src/assets/web/web-homepage-active-session.png](packages/web/src/assets/web/web-homepage-active-session.png)
- [packages/web/src/assets/web/web-homepage-new-session.png](packages/web/src/assets/web/web-homepage-new-session.png)
- [packages/web/src/assets/web/web-homepage-see-servers.png](packages/web/src/assets/web/web-homepage-see-servers.png)
- [packages/web/src/components/Footer.astro](packages/web/src/components/Footer.astro)
- [packages/web/src/components/Lander.astro](packages/web/src/components/Lander.astro)
- [packages/web/src/components/LanguageSelect.astro](packages/web/src/components/LanguageSelect.astro)
- [packages/web/src/content/docs/index.mdx](packages/web/src/content/docs/index.mdx)
- [packages/web/src/content/docs/troubleshooting.mdx](packages/web/src/content/docs/troubleshooting.mdx)
- [packages/web/src/content/docs/web.mdx](packages/web/src/content/docs/web.mdx)
- [packages/web/src/content/docs/windows-wsl.mdx](packages/web/src/content/docs/windows-wsl.mdx)
- [sdks/vscode/package.json](sdks/vscode/package.json)

</details>



## Purpose and Scope

This document provides a high-level overview of the OpenCode codebase, describing its mission as an open-source AI coding agent, the Bun workspace monorepo structure, the v2 Effect-based architecture (`cli`/`tui`/`core`/`server`/`protocol`/`client`/`schema`/`ai`), and the surrounding SaaS and documentation services. 

As a parent page, this document summarizes major subsystems and links to detailed child pages:
- For package layout and directory organization, see [Repository Structure & Packages](#1.1).
- For client/server architecture, Effect runtime, and specs, see [Architecture Overview](#1.2).
- For contributor workflows, AGENTS conventions, and automation, see [Contributor Guide & Repo Automation](#1.3).

Sources: [package.json:38-44](), [bun.lock:1-185]()

---

## What is OpenCode

OpenCode is an open-source AI coding agent designed to provide a modular, extensible, provider-agnostic alternative to proprietary AI code assistants. It integrates with over 20 large language model providers via `packages/ai` and supports multiple user interfaces including a Terminal UI (`packages/tui`), a SolidJS web/desktop app (`packages/app`, `packages/desktop`), and IDE integrations.

Key architectural characteristics include:
- **Effect-Based Core Runtime**: Leverages the `effect` library across `packages/core`, `packages/server`, and `packages/ai` for robust error handling, concurrency, and dependency injection.
- **Strict Protocol Contracts**: Uses `packages/protocol` and `packages/schema` to define type-safe API boundaries and generate clients via `packages/client`.
- **Extensible Plugin Model**: Supports custom tools, agents, skills, and model providers through `packages/plugin`.

Sources: [package.json:38-44](), [packages/plugin/package.json:1-38]()

---

## Monorepo Structure & V2 Architecture Overview

OpenCode is organized as a Bun workspace monorepo containing numerous specialized packages under `packages/`, infrastructure definitions under `infra/`, services under `services/`, and build automation under `script/`.

### Diagram 1: Monorepo Package Dependencies (Natural Language to Code Entities)

```mermaid
graph TB
    subgraph "Interfaces & CLI"
        cli[""@opencode/cli (packages/cli)""]
        tui[""@opencode/tui (packages/tui)""]
        app[""@opencode/app (packages/app)""]
    end

    subgraph "Server & Protocol"
        server[""@opencode/server (packages/server)""]
        protocol[""@opencode/protocol (packages/protocol)""]
        client[""@opencode/client (packages/client)""]
        schema[""@opencode/schema (packages/schema)""]
    end

    subgraph "Core Runtime & AI"
        core[""@opencode/core (packages/core)""]
        ai[""@opencode/ai (packages/ai)""]
        plugin[""@opencode/plugin (packages/plugin)""]
    end

    cli --> server
    cli --> tui
    app --> client
    client --> protocol
    protocol --> schema
    server --> core
    core --> ai
    core --> plugin
```
Sources: [package.json:38-44](), [packages/plugin/package.json:1-38]()

For a comprehensive breakdown of all packages (`ai`, `app`, `cli`, `client`, `codemode`, `console`, `core`, `desktop`, `gui-extensions`, `http-recorder`, `httpapi-codegen`, `identity`, `latex`, `merman`, `plugin`, `plugin-browser`, `posts`, `protocol`, `schema`, `sdk`, `server`, `session-ui`, `simulation`, `stats`, `storybook`, `theme`, `tui`, `ui`, `util`, `web`), services (`www`, `update`, `files`), and infra directories, see [Repository Structure & Packages](#1.1).

Sources: [package.json:38-44]()

---

## Architecture & Communication Flow

OpenCode v2 adopts a clean separation between the core domain logic, transport protocols, and presentation clients. The CLI daemon or standalone server runs the Effect-based backend (`packages/server`), exposing an Effect HttpApi protocol (`packages/protocol`) consumed by TypeScript clients (`packages/client`) and user interfaces.

### Diagram 2: V2 Client-Server & Core Runtime Architecture

```mermaid
graph LR
    subgraph "Client Space"
        TUI[""@opencode/tui (packages/tui)""]
        App[""@opencode/app (packages/app)""]
    end

    subgraph "Protocol & Transport"
        ClientLib[""@opencode/client (packages/client)""]
        ServerProc[""@opencode/server (packages/server)""]
    end

    subgraph "Core & AI Runtime"
        CoreSvc[""@opencode/core (packages/core)""]
        AIClient[""@opencode/ai (packages/ai)""]
    end

    TUI --> ClientLib
    App --> ClientLib
    ClientLib -->|"HTTP/SSE"| ServerProc
    ServerProc --> CoreSvc
    CoreSvc --> AIClient
```
Sources: [package.json:38-44](), [packages/plugin/package.json:1-38]()

For detailed specifications on the CLI daemon/server process, Effect runtime layers, session state machines, and `specs/v2` guidelines, see [Architecture Overview](#1.2).

Sources: [package.json:38-44]()

---

## Contributor Workflow & Automation

Development on OpenCode is governed by strict code quality standards, automated linting via `oxlint` and `ast-grep` rules located in `script/ast-grep`, and conventions defined in `AGENTS.md` and `CONTRIBUTING.md`.

For details on setting up the workspace, running test pipelines, and GitHub automation workflows (such as PR standards and issue triage), see [Contributor Guide & Repo Automation](#1.3).

Sources: [package.json:21-36](), [package.json:118-136]()

---

