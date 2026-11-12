<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langchain-mcp-adapters · page 4 MCP Servers · fetched 2026-10-26 -->

# MCP Servers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/servers/streamable-http-stateless/uv.lock](examples/servers/streamable-http-stateless/uv.lock)
- [tests/servers/__init__.py](tests/servers/__init__.py)
- [tests/servers/math_server.py](tests/servers/math_server.py)
- [tests/servers/weather_server.py](tests/servers/weather_server.py)

</details>



This document provides an overview of Model Context Protocol (MCP) servers and their role in the `langchain-mcp-adapters` ecosystem. MCP servers are external processes or services that expose tools, prompts, and resources through the Model Context Protocol, which the adapters translate into LangChain-compatible types.

For detailed information about:
- Understanding MCP server architecture and communication patterns, see [Understanding MCP Servers](#4.1)
- Example server implementations in the test suite, see [Example Servers](#4.2)
- Creating your own MCP servers, see [Creating Custom MCP Servers](#4.3)
- How the adapters connect to and manage MCP servers, see [MultiServerMCPClient](#2.1) and [Session Management and Transport](#3)

## What Are MCP Servers

MCP servers are standalone processes or network services that implement the Anthropic Model Context Protocol. They provide capabilities to LLM applications by exposing three types of entities:

| Entity Type | Purpose | Example |
|-------------|---------|---------|
| **Tools** | Functions that agents can invoke to perform actions | `add()`, `get_weather()` |
| **Prompts** | Pre-configured message templates for system instructions | `configure_assistant()` |
| **Resources** | Static or dynamic content accessible via URI schemes | `math://formulas`, `weather://forecast` |

The `langchain-mcp-adapters` library acts as a bridge, converting these MCP entities into LangChain types (`BaseTool`, `HumanMessage`/`AIMessage`, `Blob`) that can be used with LangChain agents and LangGraph workflows.

**Sources:** [tests/servers/math_server.py:6-34](), [tests/servers/weather_server.py:6-15]()

## MCP Server Architecture

### Server-Client Communication Model

```mermaid
graph TB
    subgraph "MCP_Server_Process"
        SERVER["FastMCP_Server_Instance"]
        TOOLS_REG["Tool_Registry<br/>@mcp.tool()"]
        PROMPTS_REG["Prompt_Registry<br/>@mcp.prompt()"]
        RESOURCES_REG["Resource_Registry<br/>@mcp.resource()"]
        TRANSPORT_HANDLER["Transport_Handler<br/>stdio/http/sse/websocket"]
    end
    
    subgraph "langchain-mcp-adapters_Client"
        SESSION["mcp.ClientSession"]
        ADAPTER["MultiServerMCPClient"]
    end
    
    subgraph "Protocol_Layer"
        INITIALIZE["initialize()"]
        LIST_TOOLS["list_tools()"]
        CALL_TOOL["call_tool()"]
        LIST_PROMPTS["list_prompts()"]
        GET_PROMPT["get_prompt()"]
        LIST_RESOURCES["list_resources()"]
        READ_RESOURCE["read_resource()"]
    end
    
    SERVER --> TOOLS_REG
    SERVER --> PROMPTS_REG
    SERVER --> RESOURCES_REG
    SERVER --> TRANSPORT_HANDLER
    
    TRANSPORT_HANDLER <-.transport.-> SESSION
    SESSION --> ADAPTER
    
    ADAPTER --> INITIALIZE
    INITIALIZE --> LIST_TOOLS
    INITIALIZE --> LIST_PROMPTS
    INITIALIZE --> LIST_RESOURCES
    
    LIST_TOOLS --> CALL_TOOL
    LIST_PROMPTS --> GET_PROMPT
    LIST_RESOURCES --> READ_RESOURCE
```

**Diagram: MCP Server Communication Architecture**

The server-client relationship follows a request-response pattern where:
1. The server starts and listens on a transport (stdio, HTTP, SSE, or WebSocket).
2. The client establishes a `ClientSession` via the appropriate transport mechanism.
3. The client calls `initialize()` to negotiate capabilities.
4. The client discovers available tools, prompts, and resources via `list_*()` methods.
5. The client invokes specific capabilities via `call_tool()`, `get_prompt()`, or `read_resource()`.

**Sources:** [tests/servers/math_server.py:37-38](), [tests/servers/weather_server.py:18-19]()

## Server Components

### FastMCP Server Instance

MCP servers are typically built using the `FastMCP` class from `mcp.server.fastmcp`. This provides a decorator-based API for registering tools, prompts, and resources:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")
```

The server name ("Math", "Weather", etc.) identifies the server in client connections.

**Sources:** [tests/servers/math_server.py:1-3](), [tests/servers/weather_server.py:1-3]()

### Tools Registration

Tools are Python functions decorated with `@mcp.tool()` that become callable operations for LLM agents:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return f"It's always sunny in {location}"
```

Key characteristics:
- Function signatures define the tool's input schema (parameter names and types).
- Docstrings provide the tool description exposed to LLM agents.
- Functions can be synchronous or asynchronous.
- Return values are serialized and sent back to clients.

**Sources:** [tests/servers/math_server.py:6-15](), [tests/servers/weather_server.py:6-9]()

### Prompts Registration

Prompts are template functions decorated with `@mcp.prompt()` that return message structures:

```python
@mcp.prompt()
def configure_assistant(skills: str) -> list[dict]:
    return [
        {
            "role": "assistant",
            "content": (
                f"You are a helpful assistant. You have these skills: {skills}. "
                "Always use only one tool at a time."
            ),
        },
    ]
```

Prompts return a list of message dictionaries with `role` and `content` fields, which the adapters convert to LangChain message types.

**Sources:** [tests/servers/math_server.py:18-28]()

### Resources Registration

Resources are content providers decorated with `@mcp.resource()` that respond to URI-based requests:

```python
@mcp.resource("math://formulas")
def get_math_formulas() -> str:
    """Get math formulas."""
    return "E = mc^2"

@mcp.resource("weather://forecast")
def get_weather_forecast() -> str:
    """Get weather forecast."""
    return "Sunny with a chance of clouds"
```

Resources are identified by URI schemes (e.g., `math://`, `weather://`) and can provide text or binary content.

**Sources:** [tests/servers/math_server.py:31-34](), [tests/servers/weather_server.py:12-15]()

## Transport Mechanisms

MCP servers support multiple transport mechanisms for client communication:

```mermaid
graph LR
    subgraph "Transport_Options"
        STDIO["stdio_Transport<br/>stdin/stdout"]
        HTTP["http_Transport<br/>Streamable_HTTP"]
        SSE["sse_Transport<br/>Server-Sent_Events"]
        WS["websocket_Transport<br/>Bidirectional"]
    end
    
    subgraph "Server_Startup"
        RUN["mcp.run(transport=...)"]
    end
    
    subgraph "Client_Connection"
        STDIO_CLIENT["stdio_client()"]
        HTTP_CLIENT["streamablehttp_client()"]
        SSE_CLIENT["sse_client()"]
    end
    
    STDIO --> RUN
    HTTP --> RUN
    SSE --> RUN
    WS --> RUN
    
    RUN -.-> STDIO_CLIENT
    RUN -.-> HTTP_CLIENT
    RUN -.-> SSE_CLIENT
```

**Diagram: MCP Server Transport Mechanisms**

| Transport | Use Case | Server Code | Client Code |
|-----------|----------|-------------|-------------|
| `stdio` | Local processes on user's machine | `mcp.run(transport="stdio")` | `stdio_client(StdioServerParameters)` |
| `http` | Stateless network services | `mcp.run(transport="http")` | `streamablehttp_client(url)` |
| `sse` | Server-sent events streaming | `mcp.run(transport="sse")` | `sse_client(url)` |
| `websocket` | Bidirectional real-time communication | `mcp.run(transport="websocket")` | WebSocket client |

**Sources:** [tests/servers/math_server.py:37-38](), [tests/servers/weather_server.py:18-19]()

## Server Lifecycle

### Startup Sequence

```mermaid
sequenceDiagram
    participant Process as "Server Process"
    participant FastMCP as "FastMCP Instance"
    participant Transport as "Transport Handler"
    participant Client as "ClientSession"
    
    Process->>FastMCP: Initialize mcp = FastMCP("Name")
    Process->>FastMCP: Register tools/prompts/resources
    Process->>FastMCP: mcp.run(transport="...")
    FastMCP->>Transport: Start transport listener
    Transport-->>Client: Accept connection
    Client->>Transport: initialize() request
    Transport->>FastMCP: Route to server
    FastMCP-->>Transport: Capabilities response
    Transport-->>Client: Server ready
    Client->>Transport: list_tools() / list_prompts() / list_resources()
    Transport->>FastMCP: Discovery requests
    FastMCP-->>Client: Registry contents
```

**Diagram: MCP Server Startup and Initialization**

1. **Server Creation**: The Python script instantiates `FastMCP` with a server name.
2. **Registration Phase**: Decorated functions are registered in the tool, prompt, and resource registries.
3. **Transport Start**: `mcp.run()` starts the appropriate transport listener.
4. **Client Connection**: The client establishes a connection via the transport.
5. **Initialization**: The client sends `initialize()` to negotiate protocol version and capabilities.
6. **Discovery**: The client lists available tools, prompts, and resources.
7. **Operation**: The client invokes specific capabilities as needed.

**Sources:** [tests/servers/math_server.py:1-38](), [tests/servers/weather_server.py:1-19]()

## Server Examples in Test Suite

The repository includes example MCP servers in the test suite:

| Server | File | Tools | Prompts | Resources | Transport |
|--------|------|-------|---------|-----------|-----------|
| Math | `tests/servers/math_server.py` | `add()`, `multiply()` | `configure_assistant()` | `math://formulas` | stdio |
| Weather | `tests/servers/weather_server.py` | `get_weather()` | - | `weather://forecast` | stdio |

These servers demonstrate:
- Tool registration with type-annotated parameters.
- Prompt templates with dynamic content.
- Resource URIs with custom schemes.
- Both synchronous and asynchronous tool implementations.

**Sources:** [tests/servers/math_server.py:1-39](), [tests/servers/weather_server.py:1-20]()

## Integration with Adapters

```mermaid
graph TB
    subgraph "MCP_Servers"
        MATH_SERVER["math_server.py<br/>add(), multiply()"]
        WEATHER_SERVER["weather_server.py<br/>get_weather()"]
    end
    
    subgraph "langchain-mcp-adapters"
        CLIENT["MultiServerMCPClient"]
        LOAD_TOOLS["load_mcp_tools()"]
        CONVERT["convert_mcp_tool_to_langchain_tool()"]
    end
    
    subgraph "LangChain_LangGraph"
        TOOLS["List[BaseTool]"]
        AGENT["create_agent()"]
        GRAPH["StateGraph"]
    end
    
    MATH_SERVER --> CLIENT
    WEATHER_SERVER --> CLIENT
    CLIENT --> LOAD_TOOLS
    LOAD_TOOLS --> CONVERT
    CONVERT --> TOOLS
    TOOLS --> AGENT
    TOOLS --> GRAPH
```

**Diagram: MCP Server to LangChain Integration Flow**

The adapters provide the translation layer:
1. **Discovery**: `MultiServerMCPClient` connects to servers and lists available capabilities.
2. **Conversion**: `load_mcp_tools()` retrieves tools from sessions and converts them using `convert_mcp_tool_to_langchain_tool()`.
3. **Usage**: Converted `BaseTool` instances work seamlessly with LangChain agents and LangGraph workflows.

For details on the conversion process, see [Tool Adapters](#2.2).

**Sources:** [tests/servers/math_server.py:6-15](), [tests/servers/weather_server.py:6-9]()

---

