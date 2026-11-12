<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-protocol · page 1 Overview · fetched 2026-11-02 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_zh.md](README_zh.md)

</details>



The **Agent Protocol** monorepo is a comprehensive suite of software development kits (SDKs) designed to facilitate agent interoperability, tool integration, agent-to-agent communication, and verifiable authorization boundaries across diverse runtime environments [README.md:5-7](). 

This parent page provides a high-level summary of the monorepo's architecture, its four core subsystems, licensing notes, and links to detailed child pages. For directory layouts and build instructions, see [Repository Layout](#1.1) and [Getting Started](#1.2).

---

## Architecture and Component Relationships

The monorepo organizes its capabilities into four distinct subsystems tailored for C++ and Python environments [README.md:9-14](). These components work together to form a secure, interoperable agentic ecosystem where clients, servers, registries, and authorization protocols interact seamlessly.

```mermaid
graph TD
    subgraph "Natural Language Space: Client & Orchestration"
        A["Agent Client"] -->| "JSON-RPC via Stdio/HTTP" | B["MCP C++ SDK (MCP/)"]
        A2["Agent Service"] -->| "A2A Protocol & SSE" | C["A2A C++ SDK (A2A/)"]
    end

    subgraph "Natural Language Space: Discovery & Security"
        D["Agent Search & Navigation"] -->| "FastAPI & Vector/Tree" | E["A2X Agent Registry (AgentRegistry/)"]
        F["Mandate & Intent Audit"] -->| "Ed25519 / WebAuthn" | G["A4P Python SDK (A4P/)"]
    end

    B -.->| "Registers Tools/Prompts" | E
    C -.->| "Verifies Intent" | G

    style A fill:none,stroke:#000,stroke-width:2px
    style B fill:none,stroke:#000,stroke-width:2px
    style C fill:none,stroke:#000,stroke-width:2px
    style D fill:none,stroke:#000,stroke-width:2px
    style E fill:none,stroke:#000,stroke-width:2px
    style F fill:none,stroke:#000,stroke-width:2px
    style G fill:none,stroke:#000,stroke-width:2px
```
*Figure 1: High-level architectural mapping between natural language agent roles and repository code entities.*

Sources: `[README.md:5-15]()`

---

## Core Subsystems

The repository is structured around four primary components, each addressing a specialized layer of agent infrastructure:

1. **Model Context Protocol (MCP) C++ SDK (`MCP/`)**: Implements the Model Context Protocol in C++, providing server and client abstractions, JSON-RPC message framing, capabilities validation, and pluggable transports (Stdio and Streamable HTTP).
2. **Agent2Agent Protocol (A2A) C++ SDK (`A2A/`)**: Delivers C++ support for Agent-to-Agent communication, featuring server builders, task updaters, agent cards, and libcurl-based asynchronous connections with Server-Sent Events (SSE) streaming.
3. **A2X Agent Registry (`AgentRegistry/`)**: A Python-based service and agent registry featuring hierarchical capability catalog construction, LLM-based recursive navigation, FastAPI endpoints, and distributed peer synchronization.
4. **A4P Python SDK (`A4P/`)**: The Agentic Authentication, Authorization, and Audit Protocol SDK, providing two-phase operation/intent mandates (`prepare`/`complete`), scope matching, quota consumption, and cryptographic signature verification (Ed25519 and WebAuthn).

```mermaid
graph LR
    subgraph "Code Entity Space"
        H["McpServerImplement"] -->| "Routes Methods" | I["ToolManager"]
        J["HttpServerBuilder"] -->| "StreamServerEmitter" | K["AgentExecutor"]
        L["FastAPIApp"] -->| "Registry Store" | M["A2XClient"]
        N["UserAuthorizer"] -->| "Mandate Validation" | O["MandateSecurity"]
    end

    style H fill:none,stroke:#000,stroke-width:2px
    style I fill:none,stroke:#000,stroke-width:2px
    style J fill:none,stroke:#000,stroke-width:2px
    style K fill:none,stroke:#000,stroke-width:2px
    style L fill:none,stroke:#000,stroke-width:2px
    style M fill:none,stroke:#000,stroke-width:2px
    style N fill:none,stroke:#000,stroke-width:2px
    style O fill:none,stroke:#000,stroke-width:2px
```
*Figure 2: Core code entities governing runtime execution across the SDK modules.*

Sources: `[README.md:9-15]()`

---

## Licensing and Compliance

The Agent Protocol repository is licensed under the Apache-2.0 License [README.md:25-27](). 

> **Important Compliance Note:** This product serves solely as a workflow orchestration tool and does not embed any AI model capabilities. When users integrate AI models for specific business scenarios, they shall bear full responsibility for compliance obligations under the EU AI Act and other relevant regulatory frameworks [README.md:28-29]().

Sources: `[README.md:25-29]()`, `[README_zh.md:25-29]()`

---

## Child Pages

For more detailed technical descriptions, examine the following child pages:
- [Repository Layout](#1.1) — Top-level directory mappings to subsystems, languages, and build configurations.
- [Getting Started](#1.2) — Build instructions, CMake options, Python dependencies, and running examples.

---

