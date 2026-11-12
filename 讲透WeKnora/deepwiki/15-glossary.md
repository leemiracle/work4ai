> 来源: [https://deepwiki.com/Tencent/WeKnora/15-glossary](https://deepwiki.com/Tencent/WeKnora/15-glossary)
> DeepWiki Tencent/WeKnora

# Glossary

  Relevant source files 
 - [CHANGELOG.md](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1)
 - [README.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1)
 - [README_CN.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_CN.md?plain=1)
 - [README_JA.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_JA.md?plain=1)
 - [README_KO.md](https://github.com/Tencent/WeKnora/blob/10973ed3/README_KO.md?plain=1)
 - [VERSION](https://github.com/Tencent/WeKnora/blob/10973ed3/VERSION)
 - [config/prompt_templates/agent_system_prompt.yaml](https://github.com/Tencent/WeKnora/blob/10973ed3/config/prompt_templates/agent_system_prompt.yaml)
 - [docs/QA.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/QA.md?plain=1)
 - [docs/images/architecture.png](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/images/architecture.png)
 - [frontend/package-lock.json](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package-lock.json)
 - [frontend/package.json](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/package.json)
 - [frontend/src/api/system/index.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/system/index.ts)
 - [frontend/src/components/menu.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/menu.vue)
 - [frontend/src/i18n/locales/en-US.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/en-US.ts)
 - [frontend/src/i18n/locales/ja-JP.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/ja-JP.ts)
 - [frontend/src/i18n/locales/ko-KR.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/ko-KR.ts)
 - [frontend/src/i18n/locales/ru-RU.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/ru-RU.ts)
 - [frontend/src/i18n/locales/zh-CN.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/zh-CN.ts)
 - [frontend/src/views/agent/AgentEditorModal.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/agent/AgentEditorModal.vue)
 - [frontend/src/views/knowledge/KnowledgeBase.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue)
 - [helm/Chart.yaml](https://github.com/Tencent/WeKnora/blob/10973ed3/helm/Chart.yaml)
 - [internal/agent/act.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/act.go)
 - [internal/agent/const.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/const.go)
 - [internal/agent/engine.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/engine.go)
 - [internal/agent/engine_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/engine_test.go)
 - [internal/agent/finalize.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/finalize.go)
 - [internal/agent/observe.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/observe.go)
 - [internal/agent/observe_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/observe_test.go)
 - [internal/agent/think.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/think.go)
 - [internal/application/service/agent_service.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_service.go)
 - [internal/application/service/agent_service_scope_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_service_scope_test.go)
 - [internal/application/service/agent_service_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_service_test.go)
 - [internal/application/service/session_agent_qa.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session_agent_qa.go)
 - [internal/application/service/session_agent_qa_scope_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session_agent_qa_scope_test.go)
 - [internal/handler/tenant.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/tenant.go)
 - [internal/router/router.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go)
 - [internal/types/agent.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/agent.go)
 - [internal/types/tenant.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/tenant.go)
 
  This page provides detailed definitions for WeKnora-specific terms, jargon, abbreviations, and domain concepts crucial for onboarding engineers. It connects high-level concepts to their technical implementations, workflows, and relevant code entities in the codebase.

 
---

 
## Core Domain Concepts

 
### Knowledge Base (KB)

 A **Knowledge Base** is a logical container that organizes documents, FAQs, and vector indices. It provides boundaries for data isolation, model binding, storage configuration, and retrieval scope.

 
 - **Purpose**: To hold related information artifacts such as uploaded files, extracted FAQs, or wiki pages.
 - **Types**: 
 - `document` — for PDF, Office files, manual Markdown, and various document formats.
 - `faq` — for structured question-answer pairs.
 - **Implementation**: 
 - Managed by the `interfaces.KnowledgeBaseService` interface injected via router parameters [internal/router/router.go34](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L34-L34)
 - Configurations include embedding and rerank models, indexing strategies, and retrieval engines.
 - **Frontend**: The KnowledgeBase UI supports tabs for documents, wiki pages, and graph visualization [frontend/src/views/knowledge/KnowledgeBase.vue90-95](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L90-L95)
 
 Sources: [internal/router/router.go34](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L34-L34) [frontend/src/views/knowledge/KnowledgeBase.vue90-95](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L90-L95)

 
### Knowledge Item & Parsing

 A **Knowledge Item** represents a single content unit in a KB: a file, web URL, or manual markdown entry.

 
 - **Status**: Tracks lifecycle states such as pending, processing, completed, and failed parsing.
 - **Implementation**: Handled through `interfaces.KnowledgeService` [internal/router/router.go35](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L35-L35) and document handlers.
 
 Sources: [internal/router/router.go35](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L35-L35)

 
### Chunk

 A **Chunk** is the minimal retrievable piece formed by splitting Knowledge Items for vector indexing.

 
 - **Role**: Enables fine-grained semantic search.
 - **Services**: Managed by `interfaces.ChunkService` [internal/router/router.go36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L36-L36) and `handler.ChunkHandler` [internal/router/router.go53](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L53-L53)
 
 Sources: [internal/router/router.go36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L36-L36) [internal/router/router.go53](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L53-L53)

 
### FAQ (Frequently Asked Questions)

 An FAQ knowledge base stores Q&A pairs optimized for retrieval.

 
 - **Implementation**: Managed by `handler.FAQHandler` [internal/router/router.go76](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L76-L76) providing batch processing and structured entry management.
 
 Sources: [internal/router/router.go76](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L76-L76)

 
### Wiki Mode

 Wiki Mode enables agents to autonomously generate, maintain, and visualize a structured markdown knowledge base with graph relationships.

 
 - **Implementation**: 
 - `interfaces.WikiPageService` and `handler.WikiPageHandler` handle wiki page entity management and routing [internal/router/router.go89](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L89-L89)
 
 Sources: [internal/router/router.go89](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L89-L89)

 
---

 
## Technical Infrastructure

 
### Retrieve Engine Registry

 An abstraction layer over supported vector and graph database backends.

 
 - **Backends Supported**: PostgreSQL (pgvector), Elasticsearch, Qdrant, Milvus, Weaviate, Apache Doris, Tencent VectorDB.
 - **Implementation**: Exposed via `handler.VectorStoreHandler` [internal/router/router.go72](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L72-L72)
 
 Sources: [internal/router/router.go72](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L72-L72)

 
### MCP (Model Context Protocol)

 A protocol that standardizes integration of external tools, APIs, and services into the Agent reasoning loop.

 
 - **Integration**: Managed by `handler.MCPServiceHandler`, `handler.MCPCredentialsHandler`, and `interfaces.ResourceCatalog` [internal/router/router.go66-75](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L66-L75)
 
 Sources: [internal/router/router.go66-75](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L66-L75)

 
### ReAct Agent Engine

 The engine implementing the ReAct pattern: combining reasoning steps (Thoughts) and actions (Tool invocations) iteratively.

 
 - **Implementation**: Implemented in `agentService` [internal/application/service/agent_service.go95-175](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_service.go#L95-L175) and initialized via `CreateAgentEngine` [internal/application/service/agent_service.go180-187](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_service.go#L180-L187)
 
 Sources: [internal/application/service/agent_service.go95-187](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_service.go#L95-L187)

 
---

 
## System Architecture Mapping

 The diagrams below illustrate key natural language concepts mapped to WeKnora codebase entities, bridging natural language space to code entity space.

 
### Diagram 1: From Document Upload to Vector Indexing

 
```

```

 Sources: [internal/router/router.go34-72](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L34-L72)

 
### Diagram 2: Chat with ReAct Agent and MCP Tool Integration

 
```

```

 Sources: [internal/router/router.go54-66](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L54-L66) [internal/application/service/agent_service.go95-180](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_service.go#L95-L180)

 
---

 
## Key Abbreviations & Jargon

 
| Term | Full Name / Meaning | Context and Code References |
|---|---|---|
| KB | Knowledge Base | Root domain entity for tenant-scoped knowledge aggregation internal/router/router.go34 |
| VLM | Vision Language Model | Model type used for image/attachment processing README.md62 |
| RRF | Reciprocal Rank Fusion | Algorithm for merging vector and keyword search results README_CN.md67 |
| Tenant | Account / Workspace | Highest isolation unit represented by X-Tenant-ID header internal/router/router.go118 |
| MCP | Model Context Protocol | Protocol and tool registration for agent external tool integration internal/router/router.go66 |
| RBAC | Role-Based Access Control | Permissions model with roles across workspaces CHANGELOG.md73 |

 Sources: [internal/router/router.go34-118](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L34-L118) [README.md62](https://github.com/Tencent/WeKnora/blob/10973ed3/README.md?plain=1#L62-L62) [README_CN.md67](https://github.com/Tencent/WeKnora/blob/10973ed3/README_CN.md?plain=1#L67-L67) [CHANGELOG.md73](https://github.com/Tencent/WeKnora/blob/10973ed3/CHANGELOG.md?plain=1#L73-L73)

 
---
