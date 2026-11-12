<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langchain-mcp-adapters · page 8 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [langchain_mcp_adapters/client.py](langchain_mcp_adapters/client.py)
- [langchain_mcp_adapters/sessions.py](langchain_mcp_adapters/sessions.py)
- [langchain_mcp_adapters/tools.py](langchain_mcp_adapters/tools.py)

</details>



This document provides comprehensive API reference documentation for the `langchain-mcp-adapters` library. It covers all public classes, functions, types, and protocols exposed by the library for converting MCP (Model Context Protocol) servers to LangChain-compatible components.

For specific implementation details and integration patterns, see the following pages:
- Client usage patterns: [Core Components](#2)
- Session lifecycle management: [Session Management and Transport](#3)
- Testing your MCP integrations: [Testing Framework](#6)

## API Organization

The library's API is organized into seven primary modules, each providing specialized functionality:

| Module | Primary Classes/Functions | Purpose |
|--------|---------------------------|---------|
| `client` | `MultiServerMCPClient` | Multi-server orchestration and unified tool/prompt/resource access [langchain_mcp_adapters/client.py:45-49]() |
| `tools` | `convert_mcp_tool_to_langchain_tool`, `load_mcp_tools`, `to_fastmcp` | Tool conversion and execution with interceptor support [langchain_mcp_adapters/tools.py:1-5]() |
| `prompts` | `convert_mcp_prompt_message_to_langchain_message`, `load_mcp_prompt` | Prompt message conversion to LangChain message types [langchain_mcp_adapters/prompts.py:1-5]() |
| `resources` | `convert_mcp_resource_to_langchain_blob`, `get_mcp_resource`, `load_mcp_resources` | Resource content conversion to Blob objects [langchain_mcp_adapters/resources.py:1-5]() |
| `sessions` | `create_session`, `Connection` types | Transport abstraction and session lifecycle management [langchain_mcp_adapters/sessions.py:1-5]() |
| `callbacks` | `Callbacks`, `CallbackContext`, `LoggingMessageCallback`, `ProgressCallback` | Event handling and notification protocols [langchain_mcp_adapters/callbacks.py:1-5]() |
| `interceptors`| `ToolCallInterceptor`, `MCPToolCallRequest`, `MCPToolCallResult` | Request/response modification and middleware [langchain_mcp_adapters/interceptors.py:1-5]() |

**Sources:** [langchain_mcp_adapters/client.py:1-261](), [langchain_mcp_adapters/tools.py:1-442](), [langchain_mcp_adapters/prompts.py:1-60](), [langchain_mcp_adapters/resources.py:1-104](), [langchain_mcp_adapters/sessions.py:1-432](), [langchain_mcp_adapters/callbacks.py:1-100]()

## Module and Class Hierarchy

The following diagram maps the relationships between the high-level orchestration client and the underlying adapter functions.

```mermaid
graph TB
    subgraph client_module["langchain_mcp_adapters.client"]
        MultiServerMCPClient["MultiServerMCPClient<br/>lines 45-250"]
    end
    
    subgraph tools_module["langchain_mcp_adapters.tools"]
        convert_tool["convert_mcp_tool_to_langchain_tool<br/>lines 175-330"]
        load_tools["load_mcp_tools<br/>lines 332-389"]
        to_fastmcp["to_fastmcp<br/>lines 417-465"]
        call_tool["_convert_call_tool_result<br/>lines 70-111"]
    end
    
    subgraph prompts_module["langchain_mcp_adapters.prompts"]
        convert_prompt["convert_mcp_prompt_message_to_langchain_message<br/>lines 14-36"]
        load_prompt["load_mcp_prompt<br/>lines 38-59"]
    end
    
    subgraph resources_module["langchain_mcp_adapters.resources"]
        convert_resource["convert_mcp_resource_to_langchain_blob<br/>lines 14-37"]
        get_resource["get_mcp_resource<br/>lines 40-58"]
        load_resources["load_mcp_resources<br/>lines 60-104"]
    end
    
    subgraph sessions_module["langchain_mcp_adapters.sessions"]
        create_session["create_session<br/>lines 383-454"]
        StdioConnection["StdioConnection<br/>lines 82-128"]
        SSEConnection["SSEConnection<br/>lines 129-163"]
        StreamableHttpConnection["StreamableHttpConnection<br/>lines 164-194"]
        WebsocketConnection["WebsocketConnection<br/>lines 195-206"]
    end
    
    subgraph callbacks_module["langchain_mcp_adapters.callbacks"]
        Callbacks["Callbacks<br/>lines 66-99"]
        CallbackContext["CallbackContext<br/>lines 18-23"]
    end
    
    MultiServerMCPClient -->|uses| create_session
    MultiServerMCPClient -->|uses| load_tools
    MultiServerMCPClient -->|uses| load_prompt
    MultiServerMCPClient -->|uses| load_resources
    MultiServerMCPClient -->|configures| Callbacks
    
    load_tools -->|calls| convert_tool
    convert_tool -->|uses| call_tool
    
    load_prompt -->|calls| convert_prompt
    load_resources -->|calls| get_resource
    get_resource -->|calls| convert_resource
    
    create_session -->|dispatches to| StdioConnection
    create_session -->|dispatches to| SSEConnection
    create_session -->|dispatches to| StreamableHttpConnection
    create_session -->|dispatches to| WebsocketConnection
```

**Sources:** [langchain_mcp_adapters/client.py:45-250](), [langchain_mcp_adapters/tools.py:70-465](), [langchain_mcp_adapters/sessions.py:82-454](), [langchain_mcp_adapters/callbacks.py:18-99]()

## Type System Overview

The library defines several `TypedDict`-based configuration types for transport and session parameters.

```mermaid
graph TB
    Connection["Connection<br/>Union Type<br/>sessions.py:207-209"]
    
    StdioConnection["StdioConnection<br/>TypedDict<br/>sessions.py:82-128"]
    SSEConnection["SSEConnection<br/>TypedDict<br/>sessions.py:129-163"]
    StreamableHttpConnection["StreamableHttpConnection<br/>TypedDict<br/>sessions.py:164-194"]
    WebsocketConnection["WebsocketConnection<br/>TypedDict<br/>sessions.py:195-206"]
    
    Connection -->|"transport='stdio'"| StdioConnection
    Connection -->|"transport='sse'"| SSEConnection
    Connection -->|"transport='streamable_http'"| StreamableHttpConnection
    Connection -->|"transport='websocket'"| WebsocketConnection
    
    StdioConnection -->|fields| stdio_fields["command: str<br/>args: list[str]<br/>env: dict[str,str]|None<br/>cwd: str|Path|None<br/>encoding: str<br/>encoding_error_handler: EncodingErrorHandler<br/>session_kwargs: dict|None"]
    
    SSEConnection -->|fields| sse_fields["url: str<br/>headers: dict|None<br/>timeout: float<br/>sse_read_timeout: float<br/>session_kwargs: dict|None<br/>httpx_client_factory: McpHttpClientFactory|None<br/>auth: httpx.Auth"]
    
    StreamableHttpConnection -->|fields| http_fields["url: str<br/>headers: dict|None<br/>timeout: timedelta<br/>sse_read_timeout: timedelta<br/>terminate_on_close: bool<br/>session_kwargs: dict|None<br/>httpx_client_factory: McpHttpClientFactory|None<br/>auth: httpx.Auth"]
    
    WebsocketConnection -->|fields| ws_fields["url: str<br/>session_kwargs: dict|None"]
    
    McpHttpClientFactory["McpHttpClientFactory<br/>Protocol<br/>sessions.py:60-80"]
    LoggingMessageCallback["LoggingMessageCallback<br/>Protocol<br/>callbacks.py:26-38"]
    ProgressCallback["ProgressCallback<br/>Protocol<br/>callbacks.py:41-55"]
    
    Callbacks["Callbacks<br/>Dataclass<br/>callbacks.py:66-99"]
    Callbacks -->|contains| LoggingMessageCallback
    Callbacks -->|contains| ProgressCallback
```

**Sources:** [langchain_mcp_adapters/sessions.py:60-209](), [langchain_mcp_adapters/callbacks.py:26-99]()

## Detailed API Sections

The following sections provide high-level summaries and links to child pages for detailed reference:

### [Client API](#8.1)

The `MultiServerMCPClient` is the primary entry point for managing multiple server connections simultaneously [langchain_mcp_adapters/client.py:45-49](). It handles tool discovery across servers and provides a unified interface for prompts and resources.

For details, see [Client API](#8.1).

**Sources:** [langchain_mcp_adapters/client.py:45-250]()

### [Tool Conversion API](#8.2)

Functions in this module convert `mcp.types.Tool` definitions into LangChain `BaseTool` objects [langchain_mcp_adapters/tools.py:175-180](). This includes handling JSON schemas, argument validation, and execution logic that bridges LangChain tool calls to MCP `callTool` requests.

For details, see [Tool Conversion API](#8.2).

**Sources:** [langchain_mcp_adapters/tools.py:175-465]()

### [Prompt Conversion API](#8.3)

Provides utilities to fetch MCP prompts and convert their message contents into LangChain `HumanMessage` or `AIMessage` formats [langchain_mcp_adapters/prompts.py:14-18](). It supports text and image content blocks.

For details, see [Prompt Conversion API](#8.3).

**Sources:** [langchain_mcp_adapters/prompts.py:14-59]()

### [Resource Conversion API](#8.4)

Enables loading data from MCP servers (text or binary) and wrapping them in LangChain `Blob` objects [langchain_mcp_adapters/resources.py:14-18](). This allows agents to consume server-provided documents or media.

For details, see [Resource Conversion API](#8.4).

**Sources:** [langchain_mcp_adapters/resources.py:14-104]()

### [Session API](#8.5)

Manages the lifecycle of MCP sessions across different transport layers including `stdio`, `sse`, `streamable_http`, and `websocket` [langchain_mcp_adapters/sessions.py:383-388](). It provides the `create_session` factory for abstracting transport-specific initialization.

For details, see [Session API](#8.5).

**Sources:** [langchain_mcp_adapters/sessions.py:82-454]()

### [Callback API](#8.6)

Defines protocols for handling asynchronous notifications from MCP servers, such as logging messages and progress updates during long-running tool executions [langchain_mcp_adapters/callbacks.py:26-55]().

For details, see [Callback API](#8.6).

**Sources:** [langchain_mcp_adapters/callbacks.py:3-99]()

### [Interceptor API](#8.7)

Defines the `ToolCallInterceptor` protocol which allows users to wrap tool execution logic [langchain_mcp_adapters/interceptors.py:112-117](). This is used for cross-cutting concerns like logging, caching, or modifying tool arguments before they reach the MCP server.

For details, see [Interceptor API](#8.7).

**Sources:** [langchain_mcp_adapters/interceptors.py:112-140]()

## Public Exports

The library explicitly exports the following public API through `__all__` declarations in `langchain_mcp_adapters/client.py`:

```python
__all__ = [
    "Callbacks",
    "McpHttpClientFactory",
    "MultiServerMCPClient",
    "SSEConnection",
    "StdioConnection",
    "StreamableHttpConnection",
    "WebsocketConnection",
]
```

**Sources:** [langchain_mcp_adapters/client.py:252-260]()

## Exception Handling

The library defines specific behaviors for error propagation:

| Error Type | Raised By | Condition |
|------------|-----------|-----------|
| `ValueError` | `MultiServerMCPClient` | Server name not found in connections [langchain_mcp_adapters/client.py:144-149]() |
| `_MCPToolExecutionError` | Converted tools | MCP tool call returns `isError=True` [langchain_mcp_adapters/tools.py:99-115]() |
| `NotImplementedError` | `MultiServerMCPClient` | Using client as a context manager (deprecated) [langchain_mcp_adapters/client.py:33-42]() |
| `RuntimeError` | `load_mcp_tools` | Tool pagination exceeds `MAX_ITERATIONS` (1000) [langchain_mcp_adapters/tools.py:356-358]() |

**Sources:** [langchain_mcp_adapters/client.py:33-149](), [langchain_mcp_adapters/tools.py:99-358]()

---

