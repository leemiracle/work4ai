> 来源: [https://deepwiki.com/Tencent/WeKnora/11-advanced-topics](https://deepwiki.com/Tencent/WeKnora/11-advanced-topics)
> DeepWiki Tencent/WeKnora

# Advanced Topics

  Relevant source files 
 - [CHANGELOG.md](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1)
 - [README.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1)
 - [README_CN.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_CN.md?plain=1)
 - [README_JA.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_JA.md?plain=1)
 - [README_KO.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_KO.md?plain=1)
 - [VERSION](https://github.com/Tencent/WeKnora/blob/10973ed3/VERSION)
 - [docs/QA.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/QA.md?plain=1)
 - [docs/images/architecture.png](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/images/architecture.png)
 - [frontend/package-lock.json](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package-lock.json)
 - [frontend/package.json](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package.json)
 - [helm/Chart.yaml](https://github.com/Tencent/WeKnora/blob/10973ed3/helm/Chart.yaml)
 
  This section covers the advanced capabilities of WeKnora intended for power users, integrators, and contributors who need a deep understanding of specific subsystems. The topics here go beyond basic setup and operation to explain the architectural mechanics of specialized features.

 Each subsystem listed below has its own dedicated child page. This page orients you to how they fit together within the overall system, incorporating recent updates such as session-persistent sandboxes, tenant skill catalogs, and cross-session long-term memory [CHANGELOG.md9-11](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L11)

 For foundational coverage of the RAG pipeline, see [RAG Pipeline Architecture](https://deepwiki.com/Tencent/WeKnora/3.2-rag-pipeline-architecture). For the agent system's overall structure, see [Agent System and ReAct Engine](https://deepwiki.com/Tencent/WeKnora/3.3-agent-system-and-react-engine). For storage backend selection and configuration, see [Storage and Database Layer](https://deepwiki.com/Tencent/WeKnora/3.4-storage-and-database-layer).

 
---

 
## Scope of Advanced Topics

 The following subsystems are documented in this section:

 
| Subsystem | Child Page | Core Technologies |
|---|---|---|
| Knowledge Graph / GraphRAG | Knowledge Graph and GraphRAG | Neo4j, WikiKnowledgeExtractPrompt |
| Async Task Processing | Async Task Processing with Asynq | Asynq, Redis, task_pending_ops, Worker Pools |
| Event-Driven Architecture & Streaming | Event-Driven Architecture and Streaming | EventBus, SSE, AgentEngine events |
| MCP Server Integration | MCP Server Integration | MCPManager, MCPApproval, Tool Protocol, OAuth |
| Multimodal Document Processing | Multimodal Document Processing | VLM, ImageMultimodal, image_multimodal queue |
| Hybrid Retrieval Strategies | Hybrid Retrieval Strategies | ToolRegistry, Reranking, SearchTargets |
| Wiki Mode & Auto-Wiki | Wiki Mode and Auto-Wiki Generation | wikiIngestService, WikiSummaryPrompt, WikiPageRepository |
| Desktop Application (Wails) | Desktop Application (Wails) | Wails, Lite Mode, liteLocks |
| Skills and Sandbox Execution | Skills and Sandbox Execution | CubeRemoteClient, E2BRemoteClient, TenantSandboxConfig |
| Long-Term Memory & Browser Skill | Long-Term Memory and Browser Skill | migration 000084_memory, search_memory, BrowserSkill |

 Sources: [CHANGELOG.md9-24](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L24)

 
---

 
## How the Advanced Subsystems Relate

 The diagrams below map natural language subsystem names to their corresponding code entities within the codebase.

 
### Advanced Subsystem Interaction Map

 
```

```

 Sources: [internal/application/service/wiki_ingest.go58-65](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest.go#L58-L65) [internal/application/service/wiki_ingest_batch.go54-59](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest_batch.go#L54-L59) [internal/application/service/knowledge_post_process.go21-29](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledge_post_process.go#L21-L29) [internal/router/task.go31-45](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/task.go#L31-L45)

 
### Sandbox and Memory Subsystem Code Mapping

 
```

```

 Sources: [CHANGELOG.md9-11](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L11) [internal/sandbox/cube_remote_client.go27-32](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/sandbox/cube_remote_client.go#L27-L32) [internal/sandbox/e2b_remote_client.go25-30](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/sandbox/e2b_remote_client.go#L25-L30)

 
---

 
## Knowledge Graph and GraphRAG

 WeKnora's Knowledge Graph and GraphRAG subsystem extracts entities and concepts during document ingestion to build a richly connected knowledge representation.

 
 - The core extraction uses the `WikiKnowledgeExtractPrompt`, which identifies notable entities like people and organizations, as well as domain concepts, from the document text [internal/agent/prompts_wiki.go90-116](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/prompts_wiki.go#L90-L116)
 - The extracted entities and their relations form the basis for a knowledge graph viewable with the WikiBrowser UI component [frontend/src/views/knowledge/wiki/WikiBrowser.vue4-15](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/wiki/WikiBrowser.vue#L4-L15)
 - Key data types include `GraphNode` and `GraphRelation` which are stored and queried in graph stores like Neo4j.
 - This integration enables graph-based retrieval augmenting traditional vector search in RAG pipelines.
 
 For a detailed explanation of architecture and integration techniques, see [Knowledge Graph and GraphRAG](https://deepwiki.com/Tencent/WeKnora/11.1-knowledge-graph-and-graphrag).

 Sources: [internal/agent/prompts_wiki.go90-116](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/prompts_wiki.go#L90-L116) [frontend/src/views/knowledge/wiki/WikiBrowser.vue4-15](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/wiki/WikiBrowser.vue#L4-L15)

 
---

 
## Async Task Processing with Asynq

 Heavy background processing in WeKnora such as document parsing, wiki page ingestion, indexing, and post-processing are managed via **Asynq**, a Redis-backed distributed task queue system.

 Key features:

 
 - **Worker Pools**: Tasks are routed to designated pools like `core`, `postprocess`, `enrichment`, `maintenance`, and `wiki` for load distribution.
 - **Concurrency Handling**: Safe concurrent execution is protected with row-level claiming and distributed locks, for example via `wikiSlugLockPrefix` to allow parallel ingestion batches for the same knowledge base [internal/application/service/wiki_ingest.go58-65](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest.go#L58-L65)
 - **Batch Processing**: The wiki ingestion service batches documents up to `wikiMaxDocsPerBatch` per task for efficiency [internal/application/service/wiki_ingest.go115-118](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest.go#L115-L118)
 - **Progress Tracking**: Complex ingestion tasks log detailed progress through the `SpanTracker`, capturing hierarchical attempt trees and timestamps that facilitate monitoring and debugging.
 
 Refer to [Async Task Processing with Asynq](https://deepwiki.com/Tencent/WeKnora/11.2-async-task-processing-with-asynq) for the full task registry, inspector, and lifecycle management.

 Sources: [internal/application/service/wiki_ingest.go58-118](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest.go#L58-L118) [internal/application/service/wiki_ingest_batch.go41-65](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest_batch.go#L41-L65)

 
---

 
## Event-Driven Architecture and Streaming

 WeKnora employs an event-driven architecture to provide real-time updates and interactions, particularly for streaming chat responses and agent communications.

 
 - The `EventBus` component allows asynchronous propagation of events like agent thoughts, tool invocations, and final answers [internal/event].
 - Server-Sent Events (SSE) are used to stream data efficiently to the frontend UI, enabling progressive rendering and interactive feedback.
 - Key event types include `EventAgentThought` and `EventAgentFinalAnswer`.
 - The chat pipeline and agent engine generate and listen to events, which are consumed by frontend plugins and UI components.
 
 For deep technical details on the event lifecycle, SSE streaming, and plugin architecture see [Event-Driven Architecture and Streaming](https://deepwiki.com/Tencent/WeKnora/11.3-event-driven-architecture-and-streaming).

 Sources: [internal/agent/engine.go210-270](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/engine.go#L210-L270) [internal/event/event_bus.go15-70](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/event/event_bus.go#L15-L70)

 
---

 
## MCP Server Integration

 WeKnora integrates an MCP (Model Context Protocol) server to coordinate interactions between agents and external tools.

 
 - The `MCPManager` handles the lifecycle of MCP tools and proxies.
 - Tool invocation and approval workflows are managed via the `MCPApproval` subsystem.
 - The MCP protocol supports multiple transports such as stdio, SSE, and HTTP, allowing flexible connectivity.
 - OAuth 2 authorization is integrated for secure tool access.
 - The system exposes MCP tools including document readers, search interfaces, and skill invokers [CHANGELOG.md44](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L44-L44)
 
 Refer to [MCP Server Integration](https://deepwiki.com/Tencent/WeKnora/11.4-mcp-server-integration) for the advanced MCP server setup, catalog management, and custom tool development details.

 Sources: [CHANGELOG.md44](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L44-L44)

 
---

 
## Multimodal Document Processing

 Multimodal features in WeKnora augment textual knowledge with images and vision-language models (VLMs), enabling richer document understanding and retrieval.

 
 - Images and embedded media are processed through the `ImageMultimodal` tool, initiated by tasks from the `image_multimodal` asynchronous queue [internal/router/task.go31-45](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/task.go#L31-L45)
 - OCR is supported using backend options such as PaddleOCR (`OCR_BACKEND=paddle`) or external VLM services (`OCR_BACKEND=vlm`) [docs/QA.md101-124](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/QA.md?plain=1#L101-L124)
 - Caption generation and image feature extraction enable improved indexing and question answering for documents with visual content.
 - The multimodal pipeline tightly integrates with DocReader parsers for seamless handling of complex Office and PDF documents.
 
 For a full exploration, see [Multimodal Document Processing](https://deepwiki.com/Tencent/WeKnora/11.5-multimodal-document-processing).

 Sources: [internal/router/task.go31-45](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/task.go#L31-L45) [docs/QA.md101-124](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/QA.md?plain=1#L101-L124)

 
---

 
## Hybrid Retrieval Strategies

 WeKnora supports flexible retrieval algorithms to improve knowledge access accuracy and robustness by combining vector search and lexical methods.

 
 - The `ToolRegistry` manages retrieval-related tool implementations including BM25 and RRF fusion methods.
 - Re-ranking with LLMs or dedicated rerank models refines result relevance.
 - The system employs normalization strategies for scores and final ranking.
 - Retrieval target selection and routing optimizes the comprehensive use of multiple vector stores and search backends.
 
 For implementation details and configuration options, see [Hybrid Retrieval Strategies](https://deepwiki.com/Tencent/WeKnora/11.6-hybrid-retrieval-strategies).

 Sources: [CHANGELOG.md31](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L31-L31)

 
---

 
## Wiki Mode and Auto-Wiki Generation

 Wiki Mode enables autonomous creation and maintenance of a structured, markdown-based knowledge base with rich linking and revision control.

 
 - The `wikiIngestService` manages automatic creation, updates, and linking of wiki pages [internal/application/service/wiki_ingest.go1-36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest.go#L1-L36)
 - Optimistic locking via versioned `wikiPageRepository` prevents update conflicts during concurrent editing [internal/application/repository/wiki_page.go52-63](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/wiki_page.go#L52-L63)
 - Bidirectional linking updates `OutLinks` and `InLinks` between pages automatically [internal/application/service/wiki_page.go91-106](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_page.go#L91-L106)
 - The system persists page revisions and supports rollback through `UpdateWithRevision` [internal/application/repository/wiki_page.go70-87](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/wiki_page.go#L70-L87)
 - The `WikiTaxonomyPlanPrompt` guides the hierarchical folder structure planning during content ingestion [internal/agent/prompts_wiki.go10-46](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/prompts_wiki.go#L10-L46)
 - This mode tightly couples with the knowledge graph and async task queues.
 
 For detailed architecture, ingestion pipelines, and editing tools, see [Wiki Mode and Auto-Wiki Generation](https://deepwiki.com/Tencent/WeKnora/11.7-wiki-mode-and-auto-wiki-generation).

 Sources: [internal/application/repository/wiki_page.go52-87](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/wiki_page.go#L52-L87) [internal/application/service/wiki_page.go91-106](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_page.go#L91-L106) [internal/agent/prompts_wiki.go10-46](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/prompts_wiki.go#L10-L46)

 
---

 
## Desktop Application (Wails)

 WeKnora includes a native desktop application built using the **Wails** framework, supporting macOS and other platforms.

 
 - The Desktop App packages the frontend and backend into a single executable, simplifying deployment.
 - It uses an in-process lock map `liteLocks` for concurrency in place of Redis [internal/application/service/wiki_ingest.go29-36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest.go#L29-L36)
 - SQLite support enables local persistent storage [internal/application/repository/wiki_page.go34-36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/wiki_page.go#L34-L36)
 - Lite mode omits external dependencies enabling lightweight usage scenarios.
 
 Refer to [Desktop Application (Wails)](https://deepwiki.com/Tencent/WeKnora/11.8-desktop-application-(wails)) for packaging steps, differences from full server mode, and platform-specific considerations.

 Sources: [internal/application/service/wiki_ingest.go29-36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest.go#L29-L36) [internal/application/repository/wiki_page.go34-36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/wiki_page.go#L34-L36)

 
---

 
## Skills and Sandbox Execution

 WeKnora's sandbox subsystem provides secure, isolated runtimes for agent skill execution and user code evaluation, supporting session-persistent Docker, E2B, and Cube backends [CHANGELOG.md9](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L9)

 
 - `RemoteSandboxClient` offers a decoupled API allowing integration of multiple sandbox backends.
 - Supported backends include **CubeSandbox** [internal/sandbox/cube_remote_client.go27-32](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/sandbox/cube_remote_client.go#L27-L32) **E2B** [internal/sandbox/e2b_remote_client.go25-30](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/sandbox/e2b_remote_client.go#L25-L30) and session-persistent **Docker** [CHANGELOG.md9](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L9)
 - Tenant sandbox credentials and network policies are managed with `TenantSandboxConfig` [internal/types/tenant.go86-129](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/tenant.go#L86-L129)
 - Skill snapshots enable reuse of configured environments for persistent user sessions [CHANGELOG.md9](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L9)
 - Tenant skill catalogs manage installation from ClawHub, SkillHub, git, or zip archives [CHANGELOG.md10](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L10-L10)
 - Sandbox tools include `shell_exec`, file manipulation, and database query capabilities with strict authorization scoping.
 
 See the following child pages for full details and guides:

 
 - [Sandbox Runtimes and Configuration](https://deepwiki.com/Tencent/WeKnora/11.9.1-sandbox-runtimes-and-configuration)
 - [Tenant Skill Catalog and Installation](https://deepwiki.com/Tencent/WeKnora/11.9.2-tenant-skill-catalog-and-installation)
 - [Sandbox Tools and Artifacts](https://deepwiki.com/Tencent/WeKnora/11.9.3-sandbox-tools-and-artifacts)
 
 Sources: [CHANGELOG.md9-10](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L10) [internal/sandbox/cube_remote_client.go27-32](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/sandbox/cube_remote_client.go#L27-L32) [internal/sandbox/e2b_remote_client.go25-30](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/sandbox/e2b_remote_client.go#L25-L30) [internal/types/tenant.go86-129](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/tenant.go#L86-L129)

 
---

 
## Long-Term Memory and Browser Skill

 WeKnora features a cross-session long-term memory subsystem and integration options for local browser automation via Chrome extensions.

 
 - The long-term memory subsystem (`migration 000084_memory`) tracks user profiles, preferences, facts, tasks, and interests across sessions [CHANGELOG.md11](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L11-L11)
 - Background extractors and explicit inputs update memory items, with inferred items remaining pending until confirmed by the user [CHANGELOG.md11](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L11-L11)
 - Tools like `search_memory` allow the agent to recall persistent user facts and context dynamically on demand [CHANGELOG.md11](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L11-L11)
 - Local browser automation integrates via the BrowserSkill Chrome extension interface.
 
 For a detailed walkthrough, see [Long-Term Memory and Browser Skill](https://deepwiki.com/Tencent/WeKnora/11.10-long-term-memory-and-browser-skill).

 Sources: [CHANGELOG.md11](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L11-L11)

 
---

 This overview introduces the advanced architectural patterns and features available in WeKnora. For detailed technical and implementation information, consult the dedicated child pages linked in each section.

 Sources:
 [CHANGELOG.md9-24](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L9-L24)
 [internal/application/service/wiki_ingest.go29-118](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest.go#L29-L118)
 [internal/application/service/wiki_ingest_batch.go41-65](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest_batch.go#L41-L65)
 [internal/application/service/knowledge_post_process.go21-29](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledge_post_process.go#L21-L29)
 [internal/event/event_bus.go10-70](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/event/event_bus.go#L10-L70)
 [internal/agent/engine.go200-280](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/engine.go#L200-L280)
 [internal/agent/prompts_wiki.go10-116](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/prompts_wiki.go#L10-L116)
 [internal/application/repository/wiki_page.go34-87](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/wiki_page.go#L34-L87)
 [internal/application/service/wiki_page.go85-106](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_page.go#L85-L106)
 [internal/sandbox/cube_remote_client.go27-32](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/sandbox/cube_remote_client.go#L27-L32)
 [internal/sandbox/e2b_remote_client.go25-30](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/sandbox/e2b_remote_client.go#L25-L30)
 [internal/types/tenant.go86-129](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/tenant.go#L86-L129)
 [internal/router/task.go31-45](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/task.go#L31-L45)
 [frontend/src/views/knowledge/wiki/WikiBrowser.vue4-15](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/wiki/WikiBrowser.vue#L4-L15)
