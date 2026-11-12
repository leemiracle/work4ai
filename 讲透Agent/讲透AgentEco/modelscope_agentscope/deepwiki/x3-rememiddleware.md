<!-- source: DeepWiki mcp.deepwiki.com · repo modelscope/agentscope · extra page ReMeMiddleware · fetched 2026-10-27 -->

# ReMeMiddleware

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/long_term_memory/mem0/README.md](examples/long_term_memory/mem0/README.md)
- [examples/long_term_memory/reme/README.md](examples/long_term_memory/reme/README.md)
- [examples/long_term_memory/reme/reme_demo.py](examples/long_term_memory/reme/reme_demo.py)
- [src/agentscope/middleware/_longterm_memory/_reme/_config.py](src/agentscope/middleware/_longterm_memory/_reme/_config.py)
- [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py](src/agentscope/middleware/_longterm_memory/_reme/_middleware.py)
- [tests/reme_middleware_test.py](tests/reme_middleware_test.py)

</details>



The `ReMeMiddleware` provides a file-based long-term memory system for AgentScope agents, powered by the [ReMe](https://github.com/agentscope-ai/ReMe) toolkit [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:4-7](). Unlike service-based memory systems, ReMe is embedded **in-process**, running within the same memory space as the agent without requiring a separate server or external database process [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:4-7]().

Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:4-7]()

## Purpose and Scope

`ReMeMiddleware` embeds the ReMe application in-process, configuring chat and embedding backends via AgentScope model abstractions [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:4-7](). It manages conversation memory lifecycles—including automatic write-backs, nightly consolidation, and search—while isolating session writes and providing flexible retrieval modes (`static_control`, `agent_control`, and `both`) [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:14-31]().

Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:4-32]()

## Overview and Core Architecture

`ReMeMiddleware` records memory by listening to conversations through the `on_reply` hook [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:14-16](). It performs an automatic write-back after every reply using an LLM-backed `auto_memory` job to extract and persist key facts from dialogue [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:14-16](). The middleware manages an internal `reme.ReMe` application instance and bridges AgentScope's `ChatModelBase` and `EmbeddingModelBase` into ReMe's internal components [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:89-92]().

### Key Features
- **In-Process Storage**: Memories are stored in a local workspace directory, making file versioning and inspection straightforward [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:92-93]().
- **Auto Write-Back**: Memory extraction happens automatically in the background after each exchange via the `auto_memory` job without requiring explicit agent tool calls [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:14-16](), [examples/long_term_memory/reme/README.md:10-14]().
- **Concurrent Retrieval**: Search tasks run in parallel with the agent's reply process using `asyncio.Task` to minimize latency overhead during the reasoning loop [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:22-23]().
- **Session Isolation and Scoping**: Writes are scoped by `session_id` (read dynamically from `agent.state.session_id` at hook time), while searches are workspace-wide, enabling cross-session recall across different session IDs [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:28-31](), [examples/long_term_memory/reme/README.md:131-143]().

Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:14-31](), [examples/long_term_memory/reme/README.md:10-14](), [examples/long_term_memory/reme/README.md:131-143]()

## Architecture and Data Flow

The following diagrams bridge the natural language concepts of memory lifecycle to the specific code entities (`Agent.reply_stream`, `ReMeMiddleware`, `_search`, and `_run_job`) within `src/agentscope/middleware/_longterm_memory/_reme/_middleware.py`.

Natural Language Space to Code Entity Space: ReMe Middleware Execution Flow
```mermaid
graph TD
    subgraph NaturalLanguageSpace["Natural Language Space"]
        A["Agent Reply Processing"] --> B["Pre-Reply Hook"]
        B --> C["Reasoning & Polling"]
        C --> D["Post-Reply Write-Back"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        A1["Agent_reply_stream[\"Agent.reply_stream()\"]"] --> B1["ReMeMiddleware_on_reply_pre[\"ReMeMiddleware.on_reply() (pre)\"]"]
        B1 --> C1["ReMeMiddleware_on_reasoning[\"ReMeMiddleware.on_reasoning()\"]"]
        C1 --> D1["ReMeMiddleware_on_reply_post[\"ReMeMiddleware.on_reply() (post)\"]"]
    end

    A --> A1
    B --> B1
    C --> C1
    D --> D1

    B1 -- "Spawns async task" --> E1["ReMeMiddleware__search[\"ReMeMiddleware._search()\"]"]
    C1 -- "Polls & injects HintBlock" --> F1["MessageContext[\"state.context\"]"]
    D1 -- "Dispatches job" --> G1["ReMeApp_run_job[\"ReMe.run_job('auto_memory')\"]"]
```
Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:20-26](), [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:103-109](), [examples/long_term_memory/reme/README.md:87-101]()

Natural Language Space to Code Entity Space: Component Interaction Flow
```mermaid
graph TD
    subgraph NaturalLanguageSpace["Natural Language Space"]
        N1["Application Initialization"] --> N2["Exposing Memory Tools"]
        N2 --> N3["Executing Memory Operation"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        C1["ReMeMiddleware__ensure_started[\"ReMeMiddleware._ensure_started()\"]"] --> C2["ReMeMiddleware_list_tools[\"ReMeMiddleware.list_tools()\"]"]
        C2 --> C3["MemorySearchTool___call__[\"_MemorySearchTool.__call__()\"]"]
    end

    N1 --> C1
    N2 --> C2
    N3 --> C3

    C1 --> D1["ReMeApp_start[\"ReMe.start()\"]"]
    C2 --> D2["_build_memory_tools[\"_build_memory_tools()\"]"]
    C3 --> D3["ReMeMiddleware__search[\"ReMeMiddleware._search()\"]"]
```
Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:111-113](), [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:51-53](), [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:88-129]()

## Configuration Parameters

The middleware uses a nested `Parameters` class inheriting from Pydantic's `BaseModel` to define user-tunable settings [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:131-137](). This schema is parsed by the Agent Service to render configuration forms [examples/long_term_memory/reme/README.md:49-50]().

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `chat_model` | `ChatModelBase \| None` | AgentScope chat model injected into the embedded app's default-named LLM component, fixed for the lifetime of the app. When `None`, the AgentScope ReMe config supplies the LLM. Needed for `auto_memory` write-back [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:140-149](). |
| `embedding_model` | `EmbeddingModelBase \| None` | AgentScope embedding model injected into the embedded app's default-named embedding component, fixed for the lifetime of the app. In the AgentScope minimal config, `None` keeps search keyword-only; providing a model enables vector search [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:151-161](). |
| `mode` | `Literal["static_control", "agent_control", "both"]` | How the agent retrieves from ReMe (write-back runs automatically in all modes) [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:163-173](). |
| `top_k` | `int` | Maximum number of memories retrieved per search query (default: 5) [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:175-177](). |

Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:131-177](), [examples/long_term_memory/reme/README.md:52-65]()

## Retrieval Modes

ReMe supports three retrieval modes:

1.  **`static_control`**:
    *   **Behavior**: The middleware initiates a search when a reply starts, running an asynchronous task concurrently with the reply [examples/long_term_memory/reme/README.md:90-91]().
    *   **Injection**: During `on_reasoning`, the middleware polls the background task. Once finished, it appends an `AssistantMsg` containing a `HintBlock` with retrieved memories to `state.context` [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:20-23](), [examples/long_term_memory/reme/README.md:92-94](). The message uses `name="memory"` and includes standard header and intro text [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:71-76]().
    *   **Best-Effort**: If reasoning completes before the background search task finishes, the hint is skipped for that turn [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:23](), [examples/long_term_memory/reme/README.md:94-99]().

2.  **`agent_control`**:
    *   **Behavior**: Exposes the `memory_search(query, limit)` tool directly to the agent [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:24-25](), [examples/long_term_memory/reme/README.md:108-109]().
    *   **Manual**: No automatic retrieval occurs. System prompt instructions guide the agent on when to invoke the tool [examples/long_term_memory/reme/README.md:121-123]().

3.  **`both` (Default)**:
    *   **Behavior**: Combines automatic background retrieval/injection with tool-based retrieval [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:26](), [examples/long_term_memory/reme/README.md:125-129]().

Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:17-27](), [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:163-173](), [examples/long_term_memory/reme/README.md:87-129]()

## Implementation Details

### Lazy Initialization
The middleware does not start the ReMe application upon instantiation. It invokes `_ensure_started()` lazily during the first hook call or when `list_tools()` is called [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:111-113]().

### Memory Injection and HintBlocks
During `on_reasoning`, completed background search tasks are polled, and their results are formatted into a `HintBlock` wrapped inside an `AssistantMsg` with `name="memory"` [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:71-76](), [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:20-23]().

Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:71-76](), [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:20-23]()

### Memory Search Tool and Write-Back Logic
The `memory_search` tool allows agents to query long-term memory explicitly [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:24-25](). The post-reply hook invokes `auto_memory`, which utilizes the configured `chat_model` to extract and persist conversation exchanges [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:14-16](). Providing an `embedding_model` configures the vector store for semantic search [examples/long_term_memory/reme/README.md:77-80]().

Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:14-16](), [examples/long_term_memory/reme/README.md:77-80](), [src/agentscope/middleware/_longterm_memory/_reme/_config.py:77-149]()

## Example Usage

The following example configures an agent with `ReMeMiddleware` in `both` mode:

```python
from agentscope.agent import Agent
from agentscope.middleware import ReMeMiddleware
from agentscope.tool import Toolkit
from agentscope.model import DashScopeChatModel
from agentscope.embedding import DashScopeEmbeddingModel
from agentscope.credential import DashScopeCredential

DashScopeCredential.set_api_key("YOUR_DASHSCOPE_API_KEY")
my_llm = DashScopeChatModel(model_name="qwen-max")
my_embedding = DashScopeEmbeddingModel(model_name="text-embedding-v2")

mw = ReMeMiddleware(
    workspace_dir=".reme_data",
    parameters=ReMeMiddleware.Parameters(
        chat_model=my_llm,
        embedding_model=my_embedding,
        mode="both"
    ),
)

agent = Agent(
    name="Assistant",
    model=my_llm,
    toolkit=Toolkit(tools=await mw.list_tools()),
    middlewares=[mw],
)
```
Sources: [src/agentscope/middleware/_longterm_memory/_reme/_middleware.py:115-129](), [examples/long_term_memory/reme/reme_demo.py:50-65]()

---

