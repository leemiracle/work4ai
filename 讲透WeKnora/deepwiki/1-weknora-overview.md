> 来源: [https://deepwiki.com/Tencent/WeKnora/1-weknora-overview](https://deepwiki.com/Tencent/WeKnora/1-weknora-overview)
> DeepWiki Tencent/WeKnora

# WeKnora Overview

  Relevant source files 
 - [.env.example](https://github.com/Tencent/WeKnora/blob/10973ed3/.env.example)
 - [CHANGELOG.md](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1)
 - [README.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1)
 - [README_CN.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_CN.md?plain=1)
 - [README_JA.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_JA.md?plain=1)
 - [README_KO.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_KO.md?plain=1)
 - [VERSION](https://github.com/Tencent/WeKnora/blob/10973ed3/VERSION)
 - [config/config.yaml](https://github.com/Tencent/WeKnora/blob/10973ed3/config/config.yaml)
 - [docker-compose.dev.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.dev.yml)
 - [docker-compose.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml)
 - [docs/QA.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/QA.md?plain=1)
 - [docs/images/architecture.png](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/images/architecture.png)
 - [frontend/package-lock.json](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package-lock.json)
 - [frontend/package.json](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package.json)
 - [frontend/src/api/skill/index.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/skill/index.ts)
 - [frontend/vite.config.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/vite.config.ts)
 - [go.mod](https://github.com/Tencent/WeKnora/blob/10973ed3/go.mod)
 - [go.sum](https://github.com/Tencent/WeKnora/blob/10973ed3/go.sum)
 - [helm/Chart.yaml](https://github.com/Tencent/WeKnora/blob/10973ed3/helm/Chart.yaml)
 - [internal/config/config.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go)
 - [internal/container/container.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go)
 - [internal/handler/skill_handler.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/skill_handler.go)
 - [internal/types/retriever.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/retriever.go)
 - [scripts/dev.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/dev.sh)
 
  
## Purpose and Scope

 This document provides a high-level introduction to WeKnora, explaining its core purpose as an LLM-powered RAG (Retrieval-Augmented Generation) framework, the problems it addresses, and its fundamental architecture. This overview is designed for developers, architects, and technical stakeholders who want to understand what WeKnora is and how its components work together before diving into specific subsystems.

 For detailed information about:

 
 - Specific features and capabilities, see [Key Features and Capabilities](https://deepwiki.com/Tencent/WeKnora/1.1-key-features-and-capabilities)
 - System components and their interactions, see [System Components Overview](https://deepwiki.com/Tencent/WeKnora/1.2-system-components-overview)
 - Architecture patterns and design decisions, see [System Architecture](https://deepwiki.com/Tencent/WeKnora/3-system-architecture)
 - Deployment and operations, see [Deployment and Operations](https://deepwiki.com/Tencent/WeKnora/9-deployment-and-operations)
 
 Sources: [README.md49-51](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L49-L51) [README_CN.md49-51](https://github.com/Tencent/WeKnora/blob/10973ed3/README_CN.md?plain=1#L49-L51)

 
---

 
## What is WeKnora?

 WeKnora (维娜拉) is an open-source, LLM-powered knowledge framework built for enterprise-grade document understanding, semantic retrieval, and autonomous reasoning [README.md51-53](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L51-L53) It transforms scattered organizational documents into a queryable, reasoning-capable, and continuously evolving knowledge asset [README.md53-54](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L53-L54)

 At its core, WeKnora integrates three primary interaction modes:

 
 - **RAG-based Quick Q&A**: Standard retrieval-augmented generation for everyday lookups, enabling fast and accurate question answering over knowledge bases created from diverse document sources [README.md52-53](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L52-L53)
 - **ReAct Agent**: An autonomous agent engine implementing the ReAct (Reasoning and Acting) pattern. It orchestrates knowledge retrieval, Model Context Protocol (MCP) tools, tenant skill catalogs, and web search to handle complex multi-step tasks [README.md53-54](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L53-L54) [CHANGELOG.md9-10](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L10)
 - **Wiki Mode**: A novel agent-driven mode where raw documents are distilled into a self-maintaining, interlinked Markdown wiki knowledge base, enhanced with an interactive knowledge graph visualization and revision history [README.md53-54](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L53-L54) [README.md61-62](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L61-L62)
 
 Sources: [README.md51-61](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L51-L61) [CHANGELOG.md5-25](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L5-L25)

 
---

 
## Problems WeKnora Solves

 WeKnora addresses several key challenges commonly encountered in enterprise knowledge management and AI-assisted document understanding:

 
### 1. The "Static Knowledge" Problem

 Conventional RAG solutions return individual chunks without synthesizing underlying knowledge effectively. WeKnora solves this via **Wiki Mode**, where autonomous agents synthesize raw input documents into an evolving, structured Markdown wiki supplemented by a dynamic knowledge graph [README.md53-54](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L53-L54)

 
### 2. Complex Multi-Step Reasoning

 Many enterprise queries require multi-step reasoning and integration of external tools or web search beyond static retrieval. WeKnora's **ReAct Agent** and **Skill Sandbox Runtime** address this by supporting session-persistent sandboxes (Docker, E2B, Cube), parallel tool invocation, and standardized tool protocols [CHANGELOG.md9-10](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L10)

 
### 3. Enterprise Governance and Multi-Tenancy

 WeKnora supports multi-tenant enterprise environments with robust security controls:

 
 - **Tenant RBAC**: Enforces role-based access control with a four-tier matrix (`Owner`, `Admin`, `Contributor`, `Viewer`) [README.md65-66](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L65-L66)
 - **Scoped API Keys**: Fine-grained capability-level grants and per-KB restrictions for programmatic integrations [README.md60-61](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L60-L61)
 - **Audit Logging**: Platform-level and KB-level activity tracking [README.md65-66](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L65-L66)
 
 Sources: [README.md58-90](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L58-L90) [CHANGELOG.md5-25](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L5-L25)

 
---

 
## 1.1. Key Features and Capabilities

 WeKnora provides an extensive feature set covering multimodal processing (PDF, Office, images, XMind), advanced hybrid retrieval, cross-session long-term memory, tenant skill catalogs, and flexible deployment options [README.md60-63](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L60-L63) [CHANGELOG.md5-25](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L5-L25)

 For detailed information about specific capabilities, including multimodal document parsers, agent execution modes, knowledge graph support, skill sandbox runtimes, and deployment configurations, see [Key Features and Capabilities](https://deepwiki.com/Tencent/WeKnora/1.1-key-features-and-capabilities).

 Sources: [README.md60-63](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L60-L63) [CHANGELOG.md5-25](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L5-L25)

 
---

 
## 1.2. System Components Overview

 The system architecture spans a modular frontend built with Vue.js 3 [frontend/package.json39](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package.json#L39-L39) a Go-based backend service layer using the Gin framework, a multi-database persistence tier (PostgreSQL, Redis, vector stores, graph databases, object storage), and external integrations including LLM providers, IM channels, and Langfuse observability [README.md62-63](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L62-L63) [internal/router/router.go28-87](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L28-L87)

 For a comprehensive breakdown of major system components, frontend architecture, backend services, storage layers, and external integrations, see [System Components Overview](https://deepwiki.com/Tencent/WeKnora/1.2-system-components-overview).

 Sources: [README.md62-63](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L62-L63) [internal/router/router.go28-87](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L28-L87)

 
---

 
## Core Architecture Diagrams

 
### System Layer Map

 
```

```

 Sources: [frontend/package.json1-41](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package.json#L1-L41) [internal/router/router.go28-87](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L28-L87) [README.md53-56](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L53-L56) [internal/tracing/langfuse/client.go1-10](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/tracing/langfuse/client.go#L1-L10) [internal/handler/system.go42](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/system.go#L42-L42)

 
### Retrieval and Storage Mapping

 
```

```

 Sources: [internal/router/router.go34-35](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L34-L35) [internal/router/router.go36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L36-L36) [internal/router/router.go70](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L70-L70) [README.md65-75](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L65-L75) [internal/handler/system.go42](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/system.go#L42-L42)

 
---

 This overview provides a foundation for understanding WeKnora’s purpose, architecture, and capabilities. For details on specific modules or deployment instructions, consult the child pages linked above.
