<!-- source: DeepWiki mcp.deepwiki.com · repo khoj-ai/khoj · page 3 Conversation and AI System · fetched 2026-10-29 -->

# Conversation and AI System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/khoj/processor/conversation/anthropic/anthropic_chat.py](src/khoj/processor/conversation/anthropic/anthropic_chat.py)
- [src/khoj/processor/conversation/anthropic/utils.py](src/khoj/processor/conversation/anthropic/utils.py)
- [src/khoj/processor/conversation/google/gemini_chat.py](src/khoj/processor/conversation/google/gemini_chat.py)
- [src/khoj/processor/conversation/google/utils.py](src/khoj/processor/conversation/google/utils.py)
- [src/khoj/processor/conversation/openai/gpt.py](src/khoj/processor/conversation/openai/gpt.py)
- [src/khoj/processor/conversation/openai/utils.py](src/khoj/processor/conversation/openai/utils.py)
- [src/khoj/processor/conversation/prompts.py](src/khoj/processor/conversation/prompts.py)
- [src/khoj/processor/conversation/utils.py](src/khoj/processor/conversation/utils.py)
- [src/khoj/processor/image/generate.py](src/khoj/processor/image/generate.py)
- [src/khoj/processor/tools/online_search.py](src/khoj/processor/tools/online_search.py)
- [src/khoj/processor/tools/run_code.py](src/khoj/processor/tools/run_code.py)
- [src/khoj/routers/api_chat.py](src/khoj/routers/api_chat.py)
- [src/khoj/routers/helpers.py](src/khoj/routers/helpers.py)
- [src/khoj/routers/research.py](src/khoj/routers/research.py)
- [src/khoj/utils/constants.py](src/khoj/utils/constants.py)
- [src/khoj/utils/helpers.py](src/khoj/utils/helpers.py)

</details>



## Purpose and Scope

The Conversation and AI System is the core subsystem powering Khoj's chat capabilities. It handles end-to-end processing of user queries, from receiving chat requests through FastAPI endpoints, selecting and executing appropriate tools, integrating with multiple LLM providers (OpenAI, Anthropic, Google Gemini), managing conversation context, and streaming responses back to clients.

This document covers the overall architecture and data flow through the conversation system. For detailed information on specific subsystems, see:
- Chat request processing and response generation: [Chat Processing Pipeline](#3.1)
- Multi-provider LLM integration: [LLM Provider Integration](#3.2)
- Agent configuration and persona management: [Agent System](#3.3)
- Built-in and extensible tool execution: [Tool Integration and Execution](#3.4)
- Autonomous multi-step research: [Research Mode](#3.5)
- Computer automation capabilities: [Computer Operator Agent](#3.6)

## System Architecture

The conversation system follows a layered architecture where FastAPI routers receive requests, delegate to processing helpers that orchestrate tool selection and execution, interact with LLM providers, and save conversation state to PostgreSQL.

### High-Level Component Diagram

```mermaid
graph TB
    Client["Client<br/>(Web/Desktop/Emacs/Obsidian)"]
    
    subgraph "API Layer"
        ChatAPI["api_chat.py<br/>/api/chat endpoints"]
        WebSocket["WebSocket Handler<br/>Streaming Support"]
    end
    
    subgraph "Processing Core"
        EventGen["event_generator()<br/>Request Orchestration"]
        Helpers["helpers.py<br/>agenerate_chat_response()"]
        ToolSelector["aget_data_sources_and_output_format()<br/>Tool Selection"]
        ContextAssembly["Context Assembly<br/>search_documents(), search_online()"]
    end
    
    subgraph "LLM Integration"
        Wrapper["send_message_to_model_wrapper()<br/>Provider Abstraction"]
        OpenAI["openai/gpt.py<br/>completion_with_backoff()"]
        Anthropic["anthropic/anthropic_chat.py<br/>anthropic_completion_with_backoff()"]
        Gemini["google/gemini_chat.py<br/>gemini_completion_with_backoff()"]
    end
    
    subgraph "Tool Execution"
        OnlineSearch["online_search.py<br/>search_online()"]
        RunCode["run_code.py<br/>run_code()"]
        ImageGen["generate.py<br/>text_to_image()"]
        Research["research.py<br/>research()"]
        MCP["mcp.py<br/>MCPClient"]
    end
    
    subgraph "Data Layer"
        ConvAdapters["ConversationAdapters<br/>save_conversation()"]
        AgentAdapters["AgentAdapters<br/>get_agent_chat_model()"]
        DB[("PostgreSQL<br/>Conversation, ChatMessageModel<br/>Agent, UserMemory")]
    end
    
    Client -->|HTTP/WSS| ChatAPI
    ChatAPI --> EventGen
    EventGen --> Helpers
    Helpers --> ToolSelector
    ToolSelector --> ContextAssembly
    ContextAssembly --> OnlineSearch
    ContextAssembly --> RunCode
    Helpers --> Wrapper
    Wrapper --> OpenAI
    Wrapper --> Anthropic
    Wrapper --> Gemini
    Helpers --> Research
    Research --> MCP
    Helpers --> ImageGen
    Helpers --> ConvAdapters
    Helpers --> AgentAdapters
    ConvAdapters --> DB
    AgentAdapters --> DB
    EventGen -->|Server-Sent Events| WebSocket
    WebSocket --> Client
```

**Sources:** [src/khoj/routers/api_chat.py:105-200](), [src/khoj/routers/helpers.py:1520-1550](), [src/khoj/processor/conversation/openai/gpt.py:27-133](), [src/khoj/processor/conversation/google/gemini_chat.py:18-82]()

### Component Responsibilities

| Component | Primary Responsibility | Key Classes/Functions |
|-----------|------------------------|----------------------|
| **API Routers** | HTTP/WebSocket endpoint handling, authentication, telemetry | `api_chat.py`: `chat()`, `event_generator()` |
| **Processing Helpers** | Request orchestration, tool selection, context assembly | `helpers.py`: `agenerate_chat_response()`, `aget_data_sources_and_output_format()` |
| **LLM Wrappers** | Provider-agnostic LLM interaction with retry logic | `send_message_to_model_wrapper()`, `completion_with_backoff()` |
| **Tool Executors** | Execute specific capabilities (search, code, image gen) | `search_online()`, `run_code()`, `text_to_image()` |
| **Research Orchestrator** | Multi-step autonomous tool execution | `research.py`: `research()`, `execute_tool()` |
| **Conversation Adapters** | Database persistence, conversation management | `ConversationAdapters`: `save_conversation()`, `aget_conversation_by_user()` |
| **Agent Adapters** | Agent configuration retrieval | `AgentAdapters`: `aget_user_chat_model()`, `aget_default_chat_model()` |

**Sources:** [src/khoj/routers/api_chat.py:105-180](), [src/khoj/routers/helpers.py:354-468](), [src/khoj/routers/helpers.py:2510-2750](), [src/khoj/database/adapters/__init__.py:1-1000]()

## Request Processing Flow

### Chat Request Lifecycle

The system receives chat requests through the `/api/chat` endpoint, which initializes an `event_generator` to stream typed `ChatEvent` updates back to the client.

```mermaid
sequenceDiagram
    participant Client
    participant api_chat as api_chat.py
    participant event_gen as event_generator()
    participant helpers as agenerate_chat_response()
    participant tool_select as aget_data_sources_and_output_format()
    participant tools as Tool Executors
    participant llm_wrapper as send_message_to_model_wrapper()
    participant provider as LLM Provider
    participant db as ConversationAdapters

    Client->>api_chat: POST /api/chat<br/>{q, conversation_id, images}
    api_chat->>event_gen: Create event stream
    event_gen->>helpers: Process query
    helpers->>tool_select: Determine tools & output mode
    tool_select->>llm_wrapper: Infer from query & history
    llm_wrapper->>provider: Pick relevant tools
    provider-->>llm_wrapper: {sources: [online, notes], output: text}
    llm_wrapper-->>tool_select: Tool selection result
    tool_select-->>helpers: ConversationCommand list
    
    loop For each selected tool
        helpers->>tools: Execute tool (search_online, search_documents)
        tools-->>helpers: Tool results
    end
    
    helpers->>helpers: Assemble context from tool results
    helpers->>llm_wrapper: Generate response with context
    llm_wrapper->>provider: Chat completion request
    
    loop Stream response chunks
        provider-->>llm_wrapper: Response chunk
        llm_wrapper-->>helpers: Chunk
        helpers-->>event_gen: ChatEvent.MESSAGE
        event_gen-->>api_chat: SSE event
        api_chat-->>Client: Stream chunk
    end
    
    helpers->>db: save_conversation()
    db-->>helpers: Conversation saved
    helpers-->>event_gen: ChatEvent.END_RESPONSE
    event_gen-->>api_chat: Complete
    api_chat-->>Client: Close stream
```

**Sources:** [src/khoj/routers/api_chat.py:665-900](), [src/khoj/routers/helpers.py:354-468](), [src/khoj/routers/helpers.py:1520-2200]()

### Event Stream Types

The system uses a typed event stream to communicate different stages of processing via the `ChatEvent` class.

| Event Type | Purpose | Data Format |
|------------|---------|-------------|
| `ChatEvent.STATUS` | Progress updates (e.g., "Searching the web") | String message |
| `ChatEvent.THOUGHT` | LLM reasoning process (for reasoning models) | String (thought text) |
| `ChatEvent.MESSAGE` | Response text chunks | String (response chunk) |
| `ChatEvent.REFERENCES` | Document citations | List of Context objects |
| `ChatEvent.GENERATED_ASSETS` | Images, diagrams | Dict with asset URLs |
| `ChatEvent.END_LLM_RESPONSE` | LLM streaming complete | Empty |
| `ChatEvent.END_RESPONSE` | Full response complete | Empty |

**Sources:** [src/khoj/processor/conversation/utils.py:482-495](), [src/khoj/routers/helpers.py:98-111]()

## Core Processing Components

### Message Processing Pipeline

The `agenerate_chat_response()` function implements the core conversation logic, including memory retrieval, tool selection, and context assembly.

```mermaid
graph TB
    Start["agenerate_chat_response()"]
    
    GetConv["Get/Create Conversation<br/>ConversationAdapters.aget_conversation_by_user()"]
    GetAgent["Get Agent Config<br/>AgentAdapters.aget_conversation_agent()"]
    GetMemories["Retrieve Relevant Memories<br/>UserMemoryAdapters.aget_relevant_memories()"]
    
    CheckCommand{"Check Query<br/>Command"}
    
    DirectMode["Direct Mode<br/>(image, diagram, automation)"]
    
    ToolSelection["Tool Selection<br/>aget_data_sources_and_output_format()"]
    
    ExecuteTools["Execute Tools<br/>(search_documents, search_online, etc)"]
    
    AssembleContext["Assemble Context<br/>compiled_references, online_results"]
    
    FormatMessages["Format Messages<br/>generate_chatml_messages_with_context()"]
    
    LLMCall["LLM Request<br/>send_message_to_model_wrapper()"]
    
    StreamResponse["Stream Response<br/>Yield ChatEvent.MESSAGE chunks"]
    
    SaveConv["Save to DB<br/>save_to_conversation_log()"]
    
    Start --> GetConv
    GetConv --> GetAgent
    GetAgent --> GetMemories
    GetMemories --> CheckCommand
    
    CheckCommand -->|/image, /diagram, etc| DirectMode
    CheckCommand -->|Regular query| ToolSelection
    
    DirectMode --> SaveConv
    
    ToolSelection --> ExecuteTools
    ExecuteTools --> AssembleContext
    AssembleContext --> FormatMessages
    FormatMessages --> LLMCall
    LLMCall --> StreamResponse
    StreamResponse --> SaveConv
```

**Sources:** [src/khoj/routers/helpers.py:1520-2200](), [src/khoj/processor/conversation/utils.py:106-109]()

### LLM Integration Layer

Khoj provides a unified integration layer for multiple providers. The `send_message_to_model_wrapper()` function abstracts provider-specific APIs (OpenAI, Anthropic, Gemini) and handles retryable errors via `RetryableModelError`.

#### Provider-Specific Implementations

| Provider | Completion Module | Primary Utility |
|----------|-------------------|-----------------|
| **OpenAI** | `openai/gpt.py` | `completion_with_backoff()` |
| **Anthropic** | `anthropic/anthropic_chat.py` | `anthropic_completion_with_backoff()` |
| **Google** | `google/gemini_chat.py` | `gemini_completion_with_backoff()` |

**Sources:** [src/khoj/processor/conversation/openai/utils.py:83-104](), [src/khoj/processor/conversation/google/utils.py:178-188](), [src/khoj/processor/conversation/utils.py:101-121]()

## Key Data Models

The following diagram maps conversation-related Django models to their Pydantic validation counterparts used in the AI pipeline.

```mermaid
graph LR
    subgraph "Django ORM Models (khoj.database.models)"
        Conversation["Conversation<br/>user: KhojUser<br/>conversation_log: JSON<br/>agent: Agent<br/>file_filters: List[str]"]
        
        KhojUser["KhojUser<br/>uuid: UUID<br/>username: str<br/>email: str"]
        
        Agent["Agent<br/>name: str<br/>personality: str<br/>input_tools: List[str]<br/>output_modes: List[str]"]
        
        ChatModel["ChatModel<br/>name: str<br/>model_type: ModelType"]
        
        UserMemory["UserMemory<br/>user: KhojUser<br/>memory: str"]
    end
    
    subgraph "Pydantic & Data Structures"
        ChatMessageModel["ChatMessageModel<br/>by: str<br/>message: str | list[dict]<br/>context: List[Context]"]
        
        ResponseWithThought["ResponseWithThought<br/>text: str<br/>thought: str<br/>raw_content: list"]
        
        ResearchIteration["ResearchIteration<br/>query: ToolCall<br/>summarizedResult: str"]
    end
    
    Conversation -->|contains| ChatMessageModel
    Conversation -->|belongs to| KhojUser
    Conversation -->|uses| Agent
    Agent -->|uses| ChatModel
    UserMemory -->|belongs to| KhojUser
    ChatMessageModel -->|maps to| ResponseWithThought
```

**Sources:** [src/khoj/database/models/__init__.py:1-1000](), [src/khoj/processor/conversation/utils.py:210-236](), [src/khoj/processor/conversation/openai/utils.py:38-42]()

## Tool Execution Framework

Khoj implements a flexible tool system where the LLM can trigger specific actions based on the user's intent.

| Tool | Command | Implementation |
|------|---------|----------------|
| **Document Search** | `SemanticSearchFiles` | `search_documents()` |
| **Web Search** | `SearchWeb` | `search_online()` |
| **Webpage Reader** | `ReadWebpage` | `read_webpages_content()` |
| **Code Execution** | `RunCode` | `run_code()` |
| **Image Generation** | `TextToImage` | `text_to_image()` |
| **Diagram Creation** | `GenerateDiagram` | `generate_mermaidjs_diagram()` |

**Sources:** [src/khoj/routers/api_chat.py:48-53](), [src/khoj/routers/research.py:101-184](), [src/khoj/processor/tools/online_search.py:56-72]()

## Research Mode Orchestration

Research mode allows the system to perform iterative, multi-step tasks. It uses `ResearchIteration` to track the state of an autonomous investigation, executing tools in parallel where possible.

```mermaid
graph TB
    Start["research()"]
    PickTool["Pick Next Tool<br/>(via LLM)"]
    
    CheckTool{"Tool Selected?"}
    
    ParallelExec["execute_tool()<br/>(Parallel asyncio.gather)"]
    
    Summarize["Summarize Iteration"]
    
    CheckComplete{"Complete?"}
    
    FinalResponse["Final Response"]
    
    Start --> PickTool
    PickTool --> CheckTool
    
    CheckTool -->|Yes| ParallelExec
    CheckTool -->|No| FinalResponse
    
    ParallelExec --> Summarize
    Summarize --> CheckComplete
    
    CheckComplete -->|No| PickTool
    CheckComplete -->|Yes| FinalResponse
```

**Sources:** [src/khoj/routers/research.py:64-274](), [src/khoj/processor/conversation/utils.py:210-236]()

---

