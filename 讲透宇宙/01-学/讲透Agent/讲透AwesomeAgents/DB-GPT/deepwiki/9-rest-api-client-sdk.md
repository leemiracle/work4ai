<!-- source: DeepWiki mcp.deepwiki.com · repo eosphoros-ai/DB-GPT · page 9 REST API & Client SDK · fetched 2026-10-26 -->

# REST API & Client SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py](packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py)
- [packages/dbgpt-app/src/dbgpt_app/operators/llm.py](packages/dbgpt-app/src/dbgpt_app/operators/llm.py)
- [packages/dbgpt-core/src/dbgpt/core/awel/trigger/http_trigger.py](packages/dbgpt-core/src/dbgpt/core/awel/trigger/http_trigger.py)
- [packages/dbgpt-core/src/dbgpt/util/configure/manager.py](packages/dbgpt-core/src/dbgpt/util/configure/manager.py)
- [packages/dbgpt-core/src/dbgpt/util/configure/markdown.py](packages/dbgpt-core/src/dbgpt/util/configure/markdown.py)
- [packages/dbgpt-core/src/dbgpt/util/parameter_utils.py](packages/dbgpt-core/src/dbgpt/util/parameter_utils.py)
- [packages/dbgpt-ext/src/dbgpt_ext/storage/knowledge_graph/open_spg.py](packages/dbgpt-ext/src/dbgpt_ext/storage/knowledge_graph/open_spg.py)

</details>



This page provides a high-level overview of the communication interfaces available in DB-GPT. The system exposes a comprehensive REST API for universal language integration and a dedicated Python Client SDK (`dbgpt-client`) for streamlined interaction within Python environments.

For in-depth technical details, refer to the child pages:
- [OpenAPI Endpoints (v1 & v2)](#9.1)
- [Python Client SDK (dbgpt-client)](#9.2)

---

## Overview

DB-GPT follows a service-oriented architecture where backend functionality is exposed via FastAPI-based HTTP endpoints [packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py:12-56]() and routed to core service managers. 

The following diagram bridges natural language administration intents to exact REST API route implementations in the codebase:

```mermaid
graph TD
    subgraph "Natural_Language_Space"
        "NL_List_DB"[""Show me all connected databases""]
        "NL_Add_DB"[""Connect a new relational database""]
    end

    subgraph "Code_Entity_Space"
        "Route_DB_List"["router.get('/v1/chat/db/list') in packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py"]
        "Route_DB_Add"["router.post('/v1/chat/db/add') in packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py"]
    end

    "NL_List_DB" -- "invokes route" --> "Route_DB_List"
    "NL_Add_DB" -- "invokes route" --> "Route_DB_Add"
```

Sources:  
[packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py:12-56](),  
[packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py:174-198]()

---

## OpenAPI Endpoints (v1 & v2)

DB-GPT organizes its HTTP interface into two primary version tiers:
- **v1 API:** Focuses on legacy and internal utility routes such as custom datasource connection lists, user permission checks, and database configuration management [packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py:174-212]().
- **v2 API:** Provides OpenAI-compatible chat completion endpoints and modern resource management APIs (knowledge bases, AWEL flows, apps, and model clusters).

Authentication relies on Bearer token verification handled by FastAPI dependency injections [packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py:177]().

For a complete breakdown of routers, request/response models, and schemas, see [OpenAPI Endpoints (v1 & v2)](#9.1).

Sources:  
[packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py:174-212]()

---

## Python Client SDK (dbgpt-client)

The `dbgpt-client` package provides an asynchronous, type-safe client library to interact with DB-GPT server instances programmatically.

The following diagram maps high-level client tasks to specific SDK code entities:

```mermaid
graph LR
    subgraph "Natural_Language_Space"
        "NL_Chat_K"[""Chat with my Knowledge Space""]
        "NL_Delete_Flow"[""Delete my AWEL flow""]
    end

    subgraph "Code_Entity_Space"
        "Chat_Knowledge_Call"["DBGPTClient.chat_stream(..., chat_mode='chat_knowledge')"]
        "Flow_Delete_Call"["delete_flow(client=client, flow_id=flow_id) in packages/dbgpt-client/src/dbgpt_client/flow.py"]
    end

    "NL_Chat_K" -- "maps to" --> "Chat_Knowledge_Call"
    "NL_Delete_Flow" -- "maps to" --> "Flow_Delete_Flow"
```

For tutorials, reference implementation guides, and complete client models, see [Python Client SDK (dbgpt-client)](#9.2).

Sources:  
[packages/dbgpt-client/src/dbgpt_client/flow.py:13-128](),  
[packages/dbgpt-client/src/dbgpt_client/datasource.py:12-121]()

---

## Summary of Communication Modes

| Mode                      | Protocol     | Target Audience    | Primary Use Case                                    |
|---------------------------|--------------|--------------------|----------------------------------------------------|
| **OpenAI Compatible (v2)**| HTTP/SSE     | Ecosystem Developers| Integration with OpenAI client SDK and tools       |
| **Python Client SDK**      | Async Python | Developers         | Rapid Python app development & streaming           |
| **App Management**         | HTTP/JSON    | System Admins      | Programmatic CRUD of agent apps                    |
| **Flow Management**        | HTTP/JSON    | Workflow Developers| CRUD and execution of AWEL flows                   |
| **Datasource Management**  | HTTP/JSON    | Data Engineers     | Manage DB connectors and lifecycles                |

Sources:  
[packages/dbgpt-app/src/dbgpt_app/openapi/api_v1/api_v1.py:174-212](),  
[packages/dbgpt-client/src/dbgpt_client/flow.py:13-126]()

---

