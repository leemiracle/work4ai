> 来源: [https://deepwiki.com/Tencent/WeKnora/6-api-reference](https://deepwiki.com/Tencent/WeKnora/6-api-reference)
> DeepWiki Tencent/WeKnora

# API Reference

  Relevant source files 
 - [client/README.md](https://github.com/Tencent/WeKnora/blob/10973ed3/client/README.md?plain=1)
 - [client/README_EN.md](https://github.com/Tencent/WeKnora/blob/10973ed3/client/README_EN.md?plain=1)
 - [client/knowledgebase.go](https://github.com/Tencent/WeKnora/blob/10973ed3/client/knowledgebase.go)
 - [client/skill.go](https://github.com/Tencent/WeKnora/blob/10973ed3/client/skill.go)
 - [docs/api/README.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/README.md?plain=1)
 - [docs/api/agent.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/agent.md?plain=1)
 - [docs/api/chat.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/chat.md?plain=1)
 - [docs/api/chunk.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/chunk.md?plain=1)
 - [docs/api/evaluation.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/evaluation.md?plain=1)
 - [docs/api/faq.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/faq.md?plain=1)
 - [docs/api/knowledge-base.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/knowledge-base.md?plain=1)
 - [docs/api/knowledge-search.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/knowledge-search.md?plain=1)
 - [docs/api/knowledge.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/knowledge.md?plain=1)
 - [docs/api/message.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/message.md?plain=1)
 - [docs/api/organization.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/organization.md?plain=1)
 - [docs/api/session.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/session.md?plain=1)
 - [docs/api/skill.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/skill.md?plain=1)
 - [docs/api/system.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/system.md?plain=1)
 - [docs/api/tag.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/tag.md?plain=1)
 - [docs/api/web-search.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/web-search.md?plain=1)
 - [docs/docs.go](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/docs.go)
 - [docs/plans/2026-09-10-faq-enabled-filter-design.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/plans/2026-09-10-faq-enabled-filter-design.md?plain=1)
 - [docs/swagger.json](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/swagger.json)
 - [docs/swagger.yaml](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/swagger.yaml)
 - [docs/swagger_contract_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/swagger_contract_test.go)
 - [internal/application/repository/chunk_sqlite_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/chunk_sqlite_test.go)
 - [internal/handler/system.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/system.go)
 
  
## Purpose and Scope

 This document provides a high-level overview of WeKnora's REST API. It outlines the core architectural patterns, request/response formats, authentication mechanisms, and functional domains. The API enables programmatic access to knowledge base management, document processing, FAQ operations, conversational AI, and multi-tenant collaboration features.

 WeKnora exposes a structured API organized into functional domains, primarily serving the frontend application and external integrations via platform-level or tenant-level credentials. Detailed endpoint specifications, parameter schemas, and code examples are maintained in the child pages.

 For details on authentication and permissions, see [Authentication and Authorization](https://deepwiki.com/Tencent/WeKnora/6.1-authentication-and-authorization). For knowledge base operations, see [Knowledge Base Management APIs](https://deepwiki.com/Tencent/WeKnora/6.2-knowledge-base-management-apis). For file processing, see [Knowledge and Document APIs](https://deepwiki.com/Tencent/WeKnora/6.3-knowledge-and-document-apis). For conversational features, see [Chat and Query APIs](https://deepwiki.com/Tencent/WeKnora/6.4-chat-and-query-apis). For system settings, see [Model and Configuration APIs](https://deepwiki.com/Tencent/WeKnora/6.5-model-and-configuration-apis). For FAQ and chunk details, see [FAQ and Chunk APIs](https://deepwiki.com/Tencent/WeKnora/6.6-faq-and-chunk-apis).

 Sources: [docs/api/README.md1-50](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/README.md?plain=1#L1-L50) [internal/router/router.go93-180](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L93-L180)

 
---

 
## API Architecture Overview

 WeKnora exposes a RESTful API organized into functional groups, all prefixed with `/api/v1` [docs/swagger.yaml1](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/swagger.yaml#L1-L1) The system provides an interactive Swagger UI for exploring endpoints, available at `/swagger/index.html` when running in non-release modes [internal/router/router.go137-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L137-L144)

 
### Route Registration and Handler Mapping

 The system uses a structured routing approach in `internal/router/router.go`, categorizing endpoints into functional domains such as knowledge bases, chat, and system configuration.

 
```

```

 Sources: [internal/router/router.go93-180](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L93-L180) [docs/swagger.json32-50](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/swagger.json#L32-L50)

 
### Request Flow Architecture

 The following diagram bridges the natural language API concepts to the code entities found in the Go backend, specifically highlighting the interaction between the router, handlers, and application services.

 
```

```

 Sources: [internal/router/router.go113-120](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L113-L120) [docs/swagger.json15-23](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/swagger.json#L15-L23) [frontend/src/api/chat/index.ts11](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/chat/index.ts#L11-L11) [internal/handler/system.go164-170](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/system.go#L164-L170)

 
---

 
## 6.1 Authentication and Authorization

 All API requests require identity verification via specific headers. The primary mechanisms include `X-API-Key` headers and `Authorization: Bearer` tokens [docs/swagger.json17-23](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/swagger.json#L17-L23) WeKnora implements a fine-grained principal model where API keys carry explicit role and capability grants (e.g., `tenantsRead`, `settingsManage`) [frontend/src/i18n/locales/zh-CN.ts33-50](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/zh-CN.ts#L33-L50)

 Requests are scoped to specific workspaces via the `X-Tenant-ID` header [internal/router/router.go116](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L116-L116) Platform-level API keys allow control-plane automation across multiple tenants independently [frontend/src/i18n/locales/zh-CN.ts2-7](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/zh-CN.ts#L2-L7)

 For detailed documentation, parameter schemas, and permission models, see [Authentication and Authorization](https://deepwiki.com/Tencent/WeKnora/6.1-authentication-and-authorization).

 Sources: [internal/router/router.go113-120](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go#L113-L120) [frontend/src/i18n/locales/zh-CN.ts2-50](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/zh-CN.ts#L2-L50)

 
---

 
## 6.2 Knowledge Base Management APIs

 These endpoints manage the lifecycle of Knowledge Bases (KBs), including creation, deletion, configuration updates, cloning, and access control [frontend/src/views/knowledge/KnowledgeBase.vue27-43](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L27-L43) Administrators can configure indexing strategies (Vector, Keyword, Wiki, Graph) and associate embedding or LLM models [frontend/src/i18n/locales/en-US.ts151-166](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/en-US.ts#L151-L166)

 For detailed endpoint listings and request payloads, see [Knowledge Base Management APIs](https://deepwiki.com/Tencent/WeKnora/6.2-knowledge-base-management-apis).

 Sources: [frontend/src/views/knowledge/KnowledgeBase.vue27-43](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L27-L43) [frontend/src/i18n/locales/en-US.ts151-166](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/en-US.ts#L151-L166)

 
---

 
## 6.3 Knowledge and Document APIs

 This domain handles content ingestion from various sources, including file uploads, web URLs, and manual text entries [frontend/src/views/knowledge/KnowledgeBase.vue30-31](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L30-L31) It provides asynchronous status queries, parsing control (`reparseKnowledge`, `cancelKnowledgeParse`), and document deletion [frontend/src/views/knowledge/KnowledgeBase.vue32-35](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L32-L35)

 For detailed endpoint documentation and status polling flows, see [Knowledge and Document APIs](https://deepwiki.com/Tencent/WeKnora/6.3-knowledge-and-document-apis).

 Sources: [frontend/src/views/knowledge/KnowledgeBase.vue30-35](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L30-L35)

 
---

 
## 6.4 Chat and Query APIs

 The chat and query subsystem exposes endpoints for session management, knowledge QA, agent reasoning loops (`smart-reasoning`), and real-time streaming via Server-Sent Events (SSE) [docs/docs.go37](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/docs.go#L37-L37) [frontend/src/views/agent/AgentEditorModal.vue104-109](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/agent/AgentEditorModal.vue#L104-L109) It also manages tool approvals and MCP (Model Context Protocol) interactions during conversational flows [docs/docs.go89-204](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/docs.go#L89-L204)

 For complete reference on chat sessions, message handling, and SSE payloads, see [Chat and Query APIs](https://deepwiki.com/Tencent/WeKnora/6.4-chat-and-query-apis).

 Sources: [docs/docs.go37-204](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/docs.go#L37-L204) [frontend/src/views/agent/AgentEditorModal.vue104-109](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/agent/AgentEditorModal.vue#L104-L109)

 
---

 
## 6.5 Model and Configuration APIs

 These administrative endpoints govern model provider credentials, tenant-level configurations, storage backend resolvers, parser engines (`DocReader`, `MinerU`), and system health status [frontend/src/api/system/index.ts27-231](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/system/index.ts#L27-L231)

 For full configuration reference and system administration endpoints, see [Model and Configuration APIs](https://deepwiki.com/Tencent/WeKnora/6.5-model-and-configuration-apis).

 Sources: [frontend/src/api/system/index.ts27-231](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/system/index.ts#L27-L231)

 
---

 
## 6.6 FAQ and Chunk APIs

 This domain provides specialized operations for FAQ entry management, batch import/export, granular document chunk queries, span inspection, and tag-based organization [frontend/src/views/knowledge/KnowledgeBase.vue28-45](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L28-L45)

 For API specifications on batch operations and chunk filtering, see [FAQ and Chunk APIs](https://deepwiki.com/Tencent/WeKnora/6.6-faq-and-chunk-apis).

 Sources: [frontend/src/views/knowledge/KnowledgeBase.vue28-45](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L28-L45)

 
---

 
## Error Handling

 The API uses standard HTTP status codes and a uniform JSON error envelope defined by the `AppError` structure [docs/swagger.yaml86-93](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/swagger.yaml#L86-L93)

 
| HTTP Status | Error Code | Description |
|---|---|---|
| 400 | 1000 | Bad Request (Validation failure) docs/swagger.yaml121 |
| 401 | 1001 | Unauthorized (Invalid API Key/Token) docs/swagger.yaml122 |
| 403 | 1002 | Forbidden (RBAC violation) docs/swagger.yaml123 |
| 404 | 1003 | Not Found (Resource missing) docs/swagger.yaml124 |
| 409 | 1005 | Conflict (Duplicate resource) docs/swagger.yaml126 |
| 500 | 1007 | Internal Server Error docs/swagger.yaml128 |

 Sources: [docs/swagger.yaml86-144](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/swagger.yaml#L86-L144)
