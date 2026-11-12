<!-- source: DeepWiki mcp.deepwiki.com · repo infiniflow/ragflow · page 10 Memory System · fetched 2026-10-29 -->

# Memory System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/dao/memory.go](internal/dao/memory.go)
- [internal/handler/memory.go](internal/handler/memory.go)
- [internal/service/memory.go](internal/service/memory.go)
- [internal/service/memory_extractor.go](internal/service/memory_extractor.go)
- [internal/service/memory_extractor_test.go](internal/service/memory_extractor_test.go)
- [internal/service/memory_message_service.go](internal/service/memory_message_service.go)
- [internal/service/memory_message_service_test.go](internal/service/memory_message_service_test.go)
- [internal/service/memory_message_test.go](internal/service/memory_message_test.go)

</details>



The **Memory System** in RAGFlow provides a persistent, searchable storage layer for agentic workflows and chats. Unlike standard conversation history, which is ephemeral or bounded by context window limits, the Memory System treats dialogue turns and extracted insights as structured data. It enables agents to maintain long-term state, recall prior interactions across sessions, and classify information into cognitive categories (raw, semantic, episodic, and procedural).

### System Overview

The memory subsystem bridges the LLM's "Natural Language Space" to the "Code Entity Space" by mapping conversation turns into vector-searchable documents stored in specialized indices. The entire subsystem is implemented in Go within the backend engine (`internal/service/memory.go` [internal/service/memory.go:17-43](), `internal/service/memory_message_service.go` [internal/service/memory_message_service.go:104-124]()).

Title: "MemorySystemArchitecture"
```mermaid
graph TD
    subgraph "Natural Language Space"
        UserInteraction[("UserInteraction")] --> LLMExtraction[("LLMExtraction")]
        LLMExtraction -- "extract_by_llm" --> MemoryTypes[("MemoryTypes")]
        MemoryTypes --> RawSemanticEpisodicProcedural[("Raw,Semantic,Episodic,Procedural")]
    end

    subgraph "Code Entity Space"
        RawSemanticEpisodicProcedural --> GoMemoryMessageService["MemoryMessageService (internal/service/memory_message_service.go)"]
        GoMemoryMessageService --> GoDocEngine["engine.DocEngine"]
        GoDocEngine --> PerUserIndices["PerUserIndices: memory_{uid}"]
    end

    subgraph "Storage Layer"
        PerUserIndices --> ElasticsearchDB[("Elasticsearch/Infinity")]
    end
```
Sources: [internal/service/memory.go:17-43](), [internal/handler/memory.go:38-44](), [internal/service/memory_message_service.go:104-124]()

---

### Memory Types, Extraction and Storage

RAGFlow categorizes memory into four distinct types: raw, semantic, episodic, and procedural. These are represented as bit flags defined in `internal/dao/memory.go` [internal/dao/memory.go:31-37](). When a message is processed via `queueSaveToMemoryTask` in `internal/service/memory_message_service.go` [internal/service/memory_message_service.go:161-190](), the system persists raw dialogue and queues asynchronous extraction tasks.

The asynchronous extraction worker (`internal/service/memory_extractor.go`) claims durable memory tasks via `HandleSaveToMemoryTask` [internal/service/memory_extractor.go:133-163](), invokes the LLM using prompt templates assembled by `PromptAssembler` [internal/service/memory.go:108-187](), and stores the parsed structures back into the document store.

For deep technical details on the four memory types, queue-driven processing, message indices, and storage backends, see [Memory Types, Extraction and Storage](#10.1).

Sources: [internal/service/memory.go:108-187](), [internal/service/memory_message_service.go:161-190](), [internal/dao/memory.go:31-37](), [internal/service/memory_extractor.go:133-163]()

---

### Memory Management UI and API

The system exposes REST API endpoints via `MemoryHandler` (`internal/handler/memory.go`) [internal/handler/memory.go:38-56]() alongside a React-based frontend interface for managing agent states. Users can configure parameters such as memory size limits (`MemorySizeLimit = 5242880` bytes) [internal/service/memory.go:48-50](), forgetting policies (`ForgettingPolicyFIFO`) [internal/service/memory.go:83-88](), and tenant access permissions (`me`, `team`, `all`) [internal/service/memory.go:56-67]().

Title: "MemoryConfigurationAndStorageFlow"
```mermaid
sequenceDiagram
    participant UI as "FrontendUI (web/src/pages/memory)"
    participant GoHandler as "MemoryHandler (internal/handler/memory.go)"
    participant GoService as "MemoryService (internal/service/memory.go)"
    participant GoMemoryMessageService as "MemoryMessageService (internal/service/memory_message_service.go)"
    participant NATS as "NATSJetStream (internal/engine/nats)"
    participant Ingestor as "Ingestor (internal/ingestion/service)"
    participant DocStore as "DocEngine (internal/engine)"

    UI->>GoHandler: POST /api/v1/memories (CreateMemory)
    GoHandler->>GoService: CreateMemory(userID, req)
    GoService->>DocStore: CreateChunkStore(memory_tenantID_memoryID)
    GoService-->>GoHandler: MemoryEntity
    GoHandler-->>UI: SuccessResponse

    UI->>GoHandler: GET /api/v1/memories/:memory_id/messages
    GoHandler->>GoService: GetMemoryMessages(...)
    GoService->>DocStore: Search(...)
    DocStore-->>GoService: SearchResult
    GoService-->>GoHandler: FormattedMessages
    GoHandler-->>UI: SuccessResponse

    AgentComponent->>GoMemoryMessageService: queueSaveToMemoryTask(memoryIDs, message)
    GoMemoryMessageService->>DocStore: InsertChunks(raw_message)
    GoMemoryMessageService->>NATS: PublishTask(task_type=memory)
    NATS->>Ingestor: DeliverTaskMessage
    Ingestor->>GoMemoryMessageService: HandleSaveToMemoryTask(taskID, leaseOwner)
    GoMemoryMessageService->>GoService: LLMExtraction
    GoService->>DocStore: InsertChunks(extracted_memories)
```
Sources: [internal/handler/memory.go:38-56](), [internal/service/memory.go:45-88](), [internal/dao/memory.go:103-112](), [internal/service/memory_message_service.go:104-124](), [internal/service/memory_extractor.go:133-163]()

For complete documentation on REST API routes, frontend settings, message tables, and how chats and agents attach memories, see [Memory Management UI and API](#10.2).

Sources: [internal/handler/memory.go:38-56](), [internal/service/memory.go:45-88](), [internal/dao/memory.go:103-112](), [internal/service/memory_message_service.go:104-124]()

---

