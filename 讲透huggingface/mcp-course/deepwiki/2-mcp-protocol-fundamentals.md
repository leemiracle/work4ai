<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/mcp-course · page 2 MCP Protocol Fundamentals · fetched 2026-10-26 -->

# MCP Protocol Fundamentals

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [units/en/unit1/capabilities.mdx](units/en/unit1/capabilities.mdx)
- [units/en/unit1/key-concepts.mdx](units/en/unit1/key-concepts.mdx)

</details>



## Purpose and Scope

This document covers the foundational concepts, architecture, and communication mechanisms of the Model Context Protocol (MCP). It provides a comprehensive overview of how MCP solves the AI application integration challenge through standardized client-server communication patterns and capability abstractions.

For detailed implementation patterns of specific MCP components, see [MCP Clients](#3) and [MCP Servers](#4). For advanced application examples, see [Advanced Applications](#5).

## The Integration Challenge

MCP addresses the fundamental **M×N Integration Problem** that arises when connecting multiple AI applications to multiple external tools and data sources. Without standardization, developers must create individual integrations for each possible pairing, leading to exponential complexity.

### Problem: M×N Custom Integrations

```mermaid
graph TB
    subgraph "AI Applications"
        Claude["Claude Desktop"]
        Cursor["Cursor IDE"]
        Continue["Continue.dev"]
        Custom["Custom Apps"]
    end
    
    subgraph "External Capabilities"
        Git["Git Tools"]
        Slack["Slack API"]
        Weather["Weather API"]
        Database["Database"]
    end
    
    Claude -.-> Git
    Claude -.-> Slack
    Claude -.-> Weather
    Claude -.-> Database
    
    Cursor -.-> Git
    Cursor -.-> Slack
    Cursor -.-> Weather
    Cursor -.-> Database
    
    Continue -.-> Git
    Continue -.-> Slack
    Continue -.-> Weather
    Continue -.-> Database
    
    Custom -.-> Git
    Custom -.-> Slack
    Custom -.-> Weather
    Custom -.-> Database
```

**M×N Integration Problem**

Sources: [units/en/unit1/key-concepts.mdx:12-32]()

### Solution: M+N Standardized Protocol

```mermaid
graph TB
    subgraph "AI Applications (Hosts)"
        Claude["Claude Desktop"]
        Cursor["Cursor IDE"] 
        Continue["Continue.dev"]
        Custom["Custom Apps"]
    end
    
    subgraph "MCP Protocol Layer"
        Protocol["MCP Protocol<br/>JSON-RPC 2.0"]
    end
    
    subgraph "MCP Servers"
        GitServer["Git MCP Server"]
        SlackServer["Slack MCP Server"]
        WeatherServer["Weather MCP Server"]
        DBServer["Database MCP Server"]
    end
    
    Claude --> Protocol
    Cursor --> Protocol
    Continue --> Protocol
    Custom --> Protocol
    
    Protocol --> GitServer
    Protocol --> SlackServer
    Protocol --> WeatherServer
    Protocol --> DBServer
```

**M+N Solution with MCP**

Sources: [units/en/unit1/key-concepts.mdx:28-35]()

## Core Architecture

MCP defines a three-tier architecture with distinct roles and responsibilities for each component.

### Component Relationships

```mermaid
graph TB
    subgraph "Host Application"
        Host["Host<br/>(Claude Desktop, Cursor)"]
        Client["MCP Client<br/>(MCPClient, smolagents)"]
    end
    
    subgraph "External Process"
        Server["MCP Server<br/>(FastMCP, Gradio)"]
        Capabilities["Capabilities<br/>(Tools, Resources, Prompts)"]
    end
    
    subgraph "Transport Layer"
        Transport["Transport<br/>(stdio, HTTP+SSE)"]
        JSONRPC["JSON-RPC 2.0<br/>Message Protocol"]
    end
    
    Host --> Client
    Client <--> Transport
    Transport <--> JSONRPC
    JSONRPC <--> Server
    Server --> Capabilities
```

**MCP Architecture Components**

### Component Definitions

| Component | Description | Examples |
|-----------|-------------|----------|
| **Host** | User-facing AI application that orchestrates interactions | `Claude Desktop`, `Cursor IDE`, `smolagents` |
| **Client** | Protocol handler within Host managing Server communication | `MCPClient`, `@huggingface/tiny-agents` |  
| **Server** | External service exposing capabilities via MCP protocol | `FastMCP` servers, `gr.Interface(mcp_server=True)` |

Sources: [units/en/unit1/key-concepts.mdx:48-65]()

## MCP Capabilities

MCP defines four core capability types that Servers can expose to Clients, each with distinct control patterns and use cases.

### Capability Types and Control Patterns

```mermaid
graph LR
    subgraph "Control Patterns"
        User["User Control"]
        Model["Model Control"]
        App["Application Control"]
        Server["Server Control"]
    end
    
    subgraph "Capabilities"
        Tools["Tools<br/>get_weather()"]
        Resources["Resources<br/>read_file()"]
        Prompts["Prompts<br/>code_review()"]
        Sampling["Sampling<br/>createMessage()"]
    end
    
    Model --> Tools
    App --> Resources
    User --> Prompts
    Server --> Sampling
```

**MCP Capability Control Model**

### Capability Characteristics

| Capability | Controller | Direction | Side Effects | Approval Required | Example Code Entity |
|------------|------------|-----------|--------------|-------------------|-------------------|
| **Tools** | Model (LLM) | Client → Server | Yes | Yes | `get_weather()`, `send_slack_notification()` |
| **Resources** | Application | Client → Server | No (read-only) | Typically no | `read_file()`, `get_pr_templates()` |
| **Prompts** | User | Server → Client | No | No | `code_review()`, `suggest_template()` |
| **Sampling** | Server | Server → Client → Server | Indirectly | Yes | `createMessage()`, `analyze_file_changes()` |

Sources: [units/en/unit1/capabilities.mdx:13-228]()

### Discovery and Interaction Flow

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Note over Client,Server: Capability Discovery
    Client->>Server: tools/list
    Server->>Client: Available tools
    Client->>Server: resources/list  
    Server->>Client: Available resources
    Client->>Server: prompts/list
    Server->>Client: Available prompts
    
    Note over Client,Server: Tool Execution
    Client->>Server: tools/call get_weather
    Server->>Client: Weather data response
    
    Note over Client,Server: Resource Access
    Client->>Server: resources/read file://config.json
    Server->>Client: File contents
    
    Note over Client,Server: Sampling Request
    Server->>Client: sampling/createMessage
    Client->>Client: LLM Processing
    Client->>Server: Sampling response
```

**MCP Capability Discovery and Interaction Protocol**

Sources: [units/en/unit1/capabilities.mdx:229-238]()

## Protocol Overview

MCP uses JSON-RPC 2.0 as its core communication protocol, supporting multiple transport mechanisms for different deployment scenarios.

### Transport and Protocol Stack

```mermaid
graph TB
    subgraph "Application Layer"
        MCPMessages["MCP Messages<br/>(tools/call, resources/read)"]
    end
    
    subgraph "Protocol Layer"
        JSONRPC["JSON-RPC 2.0<br/>(request/response/notification)"]
    end
    
    subgraph "Transport Layer"
        stdio["stdio Transport<br/>(Local processes)"]
        SSE["HTTP+SSE Transport<br/>(Web services)"]
    end
    
    subgraph "Network Layer"
        LocalIPC["Local IPC<br/>(pipes, sockets)"]
        HTTP["HTTP Protocol<br/>(REST endpoints)"]
    end
    
    MCPMessages --> JSONRPC
    JSONRPC --> stdio
    JSONRPC --> SSE
    stdio --> LocalIPC
    SSE --> HTTP
```

**MCP Protocol Stack**

### Key Protocol Features

- **Bidirectional Communication**: Both Client and Server can initiate requests
- **Capability Negotiation**: Dynamic discovery of available Tools, Resources, and Prompts
- **Transport Flexibility**: Support for `stdio` (local) and `HTTP+SSE` (remote) transports
- **JSON-RPC 2.0 Compliance**: Standard request/response/notification patterns

For detailed protocol specifications and message formats, see [Communication Protocol](#2.2).

Sources: [units/en/unit1/key-concepts.mdx:1-93](), [units/en/unit1/capabilities.mdx:1-243]()

## Implementation Patterns

MCP implementations typically follow these common patterns based on the capability types they expose:

### Server Implementation Patterns

```mermaid
graph TB
    subgraph "Simple Servers"
        GradioServer["Gradio MCP Server<br/>gr.Interface(mcp_server=True)"]
        SingleTool["Single Tool Server<br/>@mcp.tool decorator"]
    end
    
    subgraph "Advanced Servers"
        FastMCPServer["FastMCP Server<br/>Multiple tools + resources"]
        WorkflowServer["Workflow Server<br/>Tools + Prompts + Sampling"]
    end
    
    subgraph "Specialized Servers"
        PRAgent["PR Agent Server<br/>analyze_file_changes()"]
        SlackAgent["Slack Agent Server<br/>send_slack_notification()"]
        HubAgent["Hub Agent Server<br/>get_recent_events()"]
    end
    
    GradioServer --> FastMCPServer
    SingleTool --> FastMCPServer
    FastMCPServer --> WorkflowServer
    WorkflowServer --> PRAgent
    WorkflowServer --> SlackAgent
    WorkflowServer --> HubAgent
```

**MCP Server Implementation Progression**

Sources: [units/en/unit1/key-concepts.mdx:77-89]()

## Conclusion

MCP Protocol Fundamentals establish the foundation for standardized AI application integration through:

1. **Problem Resolution**: Transforming M×N integration complexity into M+N standardization
2. **Clear Architecture**: Well-defined Host-Client-Server component relationships  
3. **Capability Abstraction**: Four distinct capability types with appropriate control boundaries
4. **Protocol Standardization**: JSON-RPC 2.0 with flexible transport options

This foundation enables the rich ecosystem of MCP implementations covered in subsequent sections, from simple [Gradio MCP Servers](#4.1) to complex [Advanced Applications](#5) involving workflow automation and multi-system integration.

For architectural details and capability specifications, see [Core Concepts and Architecture](#2.1). For protocol mechanics and message formats, see [Communication Protocol](#2.2).

Sources: [units/en/unit1/key-concepts.mdx:90-93](), [units/en/unit1/capabilities.mdx:239-243]()

---

