> 来源: [https://deepwiki.com/Tencent/WeKnora/4-knowledge-base-management](https://deepwiki.com/Tencent/WeKnora/4-knowledge-base-management)
> DeepWiki Tencent/WeKnora

# Knowledge Base Management

  Relevant source files 
 - [docs/api/model.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/api/model.md?plain=1)
 - [frontend/src/api/model/modelUsage.test.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/model/modelUsage.test.ts)
 - [frontend/src/api/model/modelUsage.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/model/modelUsage.ts)
 - [frontend/src/components/ListSpaceSidebar.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/ListSpaceSidebar.vue)
 - [frontend/src/views/agent/AgentList.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/agent/AgentList.vue)
 - [frontend/src/views/knowledge/KnowledgeBaseList.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBaseList.vue)
 - [frontend/src/views/organization/OrganizationList.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/organization/OrganizationList.vue)
 - [internal/application/repository/knowledgebase.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/knowledgebase.go)
 - [internal/application/repository/model_usage.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/model_usage.go)
 - [internal/application/repository/model_usage_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/model_usage_test.go)
 - [internal/application/service/knowledgebase.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledgebase.go)
 - [internal/handler/knowledgebase.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/knowledgebase.go)
 - [internal/types/interfaces/knowledgebase.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/interfaces/knowledgebase.go)
 - [internal/types/knowledgebase.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/knowledgebase.go)
 
  This page provides an overview of knowledge base (KB) management in WeKnora: what a knowledge base is, the primary KB types, the core data model, and how the service, handler, and repository layers are organized. It is the entry point for the sub-pages that cover each specific area in depth.

 
 - For **creating and configuring** a knowledge base (chunking, VLM, storage provider, etc.), see [Knowledge Base Creation and Configuration](https://deepwiki.com/Tencent/WeKnora/4.1-knowledge-base-creation-and-configuration).
 - For **uploading and processing documents**, see [Document Upload and Processing](https://deepwiki.com/Tencent/WeKnora/4.2-document-upload-and-processing).
 - For **FAQ entry operations**, see [FAQ Management](https://deepwiki.com/Tencent/WeKnora/4.3-faq-management).
 - For **chunk storage and vector indexing**, see [Chunk Management and Vector Indexing](https://deepwiki.com/Tencent/WeKnora/4.4-chunk-management-and-vector-indexing).
 - For **tag/category management**, see [Tag Management and Organization](https://deepwiki.com/Tencent/WeKnora/4.5-tag-management-and-organization).
 
 
---

 
## What Is a Knowledge Base?

 A knowledge base is a tenant-scoped container that groups knowledge entries, controls how they are chunked and embedded, and determines which AI models and vector stores are used. Every RAG query and agent tool call targets one or more knowledge bases.

 The `KnowledgeBase` struct is defined in `internal/types/knowledgebase.go` and is the central data model. Key fields include:

 
| Field | Type | Purpose |
|---|---|---|
| ID | string (UUID) | Unique identifier internal/types/knowledgebase.go61 |
| Type | string | "document", "faq", or "wiki" internal/types/knowledgebase.go31-36 |
| TenantID | uint64 | Multi-tenant isolation internal/types/knowledgebase.go71 |
| EmbeddingModelID | string | Model used to generate vectors internal/types/knowledgebase.go83 |
| VectorStoreID | *string | Binding to a specific VectorStore entity internal/types/knowledgebase.go97-103 |
| ChunkingConfig | ChunkingConfig | Chunk size, overlap, and parser rules internal/types/knowledgebase.go79 |
| StorageBackendID | *string | Concrete storage instance binding internal/types/knowledgebase.go94 |

 Sources: [internal/types/knowledgebase.go59-114](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/knowledgebase.go#L59-L114) [internal/application/service/knowledgebase.go118-177](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledgebase.go#L118-L177)

 
---

 
## Knowledge Base Types

 
### Document KB (`type = "document"`)

 A document knowledge base holds **knowledge entries**. Each entry represents a single source: an uploaded file, a crawled URL, or manual text. Entries are processed into chunks and indexed in a vector store. The backend handles this via repository and service methods [internal/application/repository/knowledgebase.go26-39](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/knowledgebase.go#L26-L39)

 
### FAQ KB (`type = "faq"`)

 A FAQ knowledge base holds **FAQ entries** (Question-Answer pairs). The `FAQConfig` controls indexing strategies, such as `FAQIndexModeQuestionOnly` or `FAQIndexModeQuestionAnswer` [internal/types/knowledgebase.go38-46](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/knowledgebase.go#L38-L46)

 
### Wiki KB (`type = "wiki"`)

 A wiki-enabled knowledge base supports automatic wiki page generation. Configuration is handled via `WikiConfig` and `IndexingStrategy`, which determines if wiki generation and knowledge graph extraction are active [internal/types/knowledgebase.go110-116](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/knowledgebase.go#L110-L116)

 Sources: [internal/types/knowledgebase.go31-56](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/knowledgebase.go#L31-L56) [internal/application/repository/knowledgebase.go26-39](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/knowledgebase.go#L26-L39)

 
---

 
## Core Data Model & Code Mapping

 This diagram bridges natural language configuration concepts to concrete code entities in the `internal/types` package.

 Title: "Knowledge Base Configuration to Code Entities"

 
```

```

 Sources: [internal/types/knowledgebase.go59-116](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/knowledgebase.go#L59-L116)

 
---

 
## Service Layer Architecture & Component Mapping

 The knowledge base management logic is encapsulated in `service.knowledgeBaseService`, which coordinates persistence, cross-tenant validation, and vector store bindings.

 Title: "Service Layer Architecture to Code Entities"

 
```

```

 Sources: [internal/application/service/knowledgebase.go33-54](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledgebase.go#L33-L54) [internal/handler/knowledgebase.go31-47](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/knowledgebase.go#L31-L47) [internal/application/repository/knowledgebase.go16-23](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/knowledgebase.go#L16-L23)

 
---

 
## HTTP API and UI Interaction

 Knowledge base operations are exposed via `KnowledgeBaseHandler`. The frontend uses these endpoints to drive management views.

 Title: "Knowledge Base API Routing"

 
```

```

 Sources: [internal/handler/knowledgebase.go31-74](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/knowledgebase.go#L31-L74) [internal/application/service/knowledgebase.go118-177](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledgebase.go#L118-L177)

 
---

 
## Vector Store Binding and Multi-Tenancy

 A critical security feature is the binding of a Knowledge Base to a `VectorStoreID`.

 
 - **Validation:** The `knowledgeBaseService` validates that a `VectorStoreID` belongs to the requesting tenant before creation using `validateVectorStoreBinding` [internal/application/service/knowledgebase.go155-159](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledgebase.go#L155-L159)
 - **Normalization:** Empty string IDs are normalized to `nil` to indicate usage of tenant-wide default engines [internal/application/service/knowledgebase.go145-154](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledgebase.go#L145-L154)
 - **Metadata Hiding:** In shared knowledge base responses via `buildKBResponse`, the raw `vector_store_id` UUID is stripped to prevent cross-tenant infrastructure correlation [internal/handler/knowledgebase.go109-124](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/knowledgebase.go#L109-L124)
 - **Storage Backends:** KBs are bound to concrete storage instances via `StorageBackendID`. The system resolves these via `StorageBackendResolver` to ensure availability and proper provider selection [internal/application/service/knowledgebase.go179-183](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledgebase.go#L179-L183)
 
 Sources: [internal/application/service/knowledgebase.go118-183](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/knowledgebase.go#L118-L183) [internal/handler/knowledgebase.go109-141](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/knowledgebase.go#L109-L141) [internal/types/knowledgebase.go94-103](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/knowledgebase.go#L94-L103)

 
---

 
## Sub-Topics and Child Pages

 
 - For detailed configuration parameters, chunking rules, and model selections, see [Knowledge Base Creation and Configuration](https://deepwiki.com/Tencent/WeKnora/4.1-knowledge-base-creation-and-configuration).
 - For file upload mechanisms, validation, and async parsing, see [Document Upload and Processing](https://deepwiki.com/Tencent/WeKnora/4.2-document-upload-and-processing).
 - For FAQ entry management and batch import/export, see [FAQ Management](https://deepwiki.com/Tencent/WeKnora/4.3-faq-management).
 - For parent-child chunking strategies and vector indexing, see [Chunk Management and Vector Indexing](https://deepwiki.com/Tencent/WeKnora/4.4-chunk-management-and-vector-indexing).
 - For category trees and tag-based filtering, see [Tag Management and Organization](https://deepwiki.com/Tencent/WeKnora/4.5-tag-management-and-organization).
