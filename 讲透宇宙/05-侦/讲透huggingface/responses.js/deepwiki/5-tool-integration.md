<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/responses.js · page 5 Tool Integration · fetched 2026-10-26 -->

# Tool Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/mcp.ts](src/mcp.ts)
- [src/routes/responses.ts](src/routes/responses.ts)

</details>



This document provides a comprehensive guide to integrating and using external tools with responses.js. Tool integration enables LLMs to extend their capabilities by executing functions, accessing external systems, and performing actions beyond text generation. The system supports two primary tool types: basic function calls and MCP (Model Context Protocol) servers with sophisticated approval workflows.

For specific implementation details of function calling, see [Function Calling](#5.1). For MCP server integration, see [MCP Tools](#5.2). For approval mechanism configuration, see [Approval Workflows](#5.3).

## Tool Types Overview

The responses.js system supports two distinct tool integration approaches, each serving different use cases and complexity requirements.

```mermaid
graph TB
    subgraph "Tool Types"
        FunctionTools["Function Tools<br/>type: 'function'"]
        MCPTools["MCP Tools<br/>type: 'mcp'"]
    end
    
    subgraph "Function Tool Properties"
        FuncName["name: string"]
        FuncParams["parameters: FunctionParameters"]
        FuncDesc["description?: string"]
        FuncStrict["strict?: boolean"]
    end
    
    subgraph "MCP Tool Properties"
        MCPLabel["server_label: string"]
        MCPUrl["server_url: string"]
        MCPHeaders["headers?: Record<string, string>"]
        MCPAllowed["allowed_tools?: string[] | object"]
        MCPApproval["require_approval?: ApprovalConfig"]
    end
    
    FunctionTools --> FuncName
    FunctionTools --> FuncParams
    FunctionTools --> FuncDesc
    FunctionTools --> FuncStrict
    
    MCPTools --> MCPLabel
    MCPTools --> MCPUrl
    MCPTools --> MCPHeaders
    MCPTools --> MCPAllowed
    MCPTools --> MCPApproval
    
    subgraph "Processing Flow"
        ToolDiscovery["Tool Discovery"]
        ToolPreparation["Tool Preparation"]
        LLMIntegration["LLM Integration"]
        ToolExecution["Tool Execution"]
    end
    
    FunctionTools --> ToolDiscovery
    MCPTools --> ToolDiscovery
    ToolDiscovery --> ToolPreparation
    ToolPreparation --> LLMIntegration
    LLMIntegration --> ToolExecution
```

Sources: [src/routes/responses.ts:164-227](), [src/schemas.ts]()

## Tool Processing Architecture

The tool integration system operates through a multi-stage pipeline that handles tool discovery, preparation, execution, and result streaming. The architecture seamlessly integrates with the response generation process.

**Tool Processing Pipeline**

```mermaid
flowchart TD
    RequestReceived["postCreateResponse<br/>Request Received"]
    ValidateTools["Tool Validation<br/>Schema Check"]
    
    subgraph "Tool Discovery Phase"
        ProcessTools["Process req.body.tools"]
        FunctionToolPath["Function Tool<br/>Direct Integration"]
        MCPToolPath["MCP Tool<br/>Server Discovery"]
        ListMCPTools["listMcpToolsStream<br/>connectMcpServer"]
    end
    
    subgraph "Tool Preparation Phase"
        BuildToolsArray["Build ChatCompletionTool[]"]
        MapMCPTools["mcpToolsMapping<br/>Record<string, McpServerParams>"]
        FilterAllowedTools["Filter allowed_tools"]
    end
    
    subgraph "LLM Integration Phase"
        PreparePayload["ChatCompletionCreateParamsStreaming"]
        SendToLLM["client.chat.completions.create"]
        ProcessResponse["handleOneTurnStream"]
    end
    
    subgraph "Tool Execution Phase"
        DetectToolCall["delta.tool_calls"]
        CheckApproval["requiresApproval"]
        ExecuteTool["callMcpTool / Function Execution"]
        StreamResults["Tool Result Events"]
    end
    
    RequestReceived --> ValidateTools
    ValidateTools --> ProcessTools
    ProcessTools --> FunctionToolPath
    ProcessTools --> MCPToolPath
    
    FunctionToolPath --> BuildToolsArray
    MCPToolPath --> ListMCPTools
    ListMCPTools --> MapMCPTools
    MapMCPTools --> FilterAllowedTools
    FilterAllowedTools --> BuildToolsArray
    
    BuildToolsArray --> PreparePayload
    PreparePayload --> SendToLLM
    SendToLLM --> ProcessResponse
    
    ProcessResponse --> DetectToolCall
    DetectToolCall --> CheckApproval
    CheckApproval --> ExecuteTool
    ExecuteTool --> StreamResults
```

Sources: [src/routes/responses.ts:32-58](), [src/routes/responses.ts:146-415](), [src/routes/responses.ts:164-227]()

## Tool Discovery and Preparation

Tool discovery involves processing the `tools` array from the request and preparing them for LLM integration. The system handles both immediate function tools and dynamic MCP tool discovery.

**MCP Tool Discovery Process**

```mermaid
sequenceDiagram
    participant Handler as "innerRunStream"
    participant MCPClient as "connectMcpServer"
    participant MCPServer as "External MCP Server"
    participant LLM as "Chat Completion API"
    
    Handler->>Handler: "Process req.body.tools"
    Handler->>MCPClient: "connectMcpServer(tool)"
    MCPClient->>MCPServer: "StreamableHTTPClientTransport"
    alt HTTP Transport Fails
        MCPClient->>MCPServer: "SSEClientTransport"
    end
    MCPServer-->>MCPClient: "Connection Established"
    MCPClient-->>Handler: "Client Instance"
    
    Handler->>MCPServer: "mcp.listTools()"
    MCPServer-->>Handler: "Available Tools"
    Handler->>Handler: "Filter allowed_tools"
    Handler->>Handler: "Build ChatCompletionTool[]"
    Handler->>LLM: "Send tools with payload"
```

The tool preparation process transforms both function and MCP tools into a unified format for the LLM:

| Tool Type | Source | Transformation | Storage |
|-----------|--------|---------------|---------|
| Function | `req.body.tools` | Direct mapping to `ChatCompletionTool` | `tools` array |
| MCP | External server | `listTools()` → `ChatCompletionTool` | `mcpToolsMapping` record |

Sources: [src/routes/responses.ts:164-227](), [src/mcp.ts:10-33]()

## Tool Execution Flow

Tool execution occurs during LLM response streaming when the model generates tool calls. The system handles different execution paths based on tool type and approval requirements.

**Tool Call Processing**

```mermaid
graph TB
    subgraph "Tool Call Detection"
        DetectCall["delta.tool_calls[0].function?.name"]
        CheckType["Check Tool Type"]
        FunctionType["Function Tool"]
        MCPType["MCP Tool"]
    end
    
    subgraph "MCP Tool Processing"
        CheckApproval["requiresApproval()"]
        ApprovalRequired["Create mcp_approval_request"]
        DirectExecution["Create mcp_call"]
        WaitApproval["Wait for approval_response"]
        ExecuteApproved["callApprovedMCPToolStream"]
    end
    
    subgraph "Tool Execution"
        CallMCP["callMcpTool"]
        ConnectServer["connectMcpServer"]
        ExecuteTool["client.callTool"]
        FormatResult["McpResultFormatter.format"]
    end
    
    subgraph "Response Integration"
        UpdatePayload["Update payload.messages"]
        ContinueLLM["Next LLM Iteration"]
        StreamEvents["Tool Result Events"]
    end
    
    DetectCall --> CheckType
    CheckType --> FunctionType
    CheckType --> MCPType
    
    MCPType --> CheckApproval
    CheckApproval -->|True| ApprovalRequired
    CheckApproval -->|False| DirectExecution
    ApprovalRequired --> WaitApproval
    WaitApproval --> ExecuteApproved
    DirectExecution --> CallMCP
    ExecuteApproved --> CallMCP
    
    CallMCP --> ConnectServer
    ConnectServer --> ExecuteTool
    ExecuteTool --> FormatResult
    FormatResult --> UpdatePayload
    UpdatePayload --> ContinueLLM
    UpdatePayload --> StreamEvents
    
    FunctionType --> StreamEvents
```

Sources: [src/routes/responses.ts:564-768](), [src/routes/responses.ts:696-728](), [src/mcp.ts:35-56]()

## Integration with Response Generation

Tools are deeply integrated into the response streaming architecture, with specific event types for different tool operations and states.

**Tool-Related Stream Events**

| Event Type | Purpose | Data Fields |
|------------|---------|-------------|
| `response.mcp_list_tools.in_progress` | MCP tool discovery started | `sequence_number` |
| `response.mcp_list_tools.completed` | MCP tool discovery finished | `sequence_number` |
| `response.mcp_call.in_progress` | MCP tool execution started | `item_id`, `output_index` |
| `response.mcp_call.completed` | MCP tool execution finished | `sequence_number` |
| `response.function_call_arguments.delta` | Function call args streaming | `item_id`, `delta` |
| `response.mcp_call_arguments.delta` | MCP call args streaming | `item_id`, `delta` |

**Tool Result Integration**

The system maintains conversation continuity by updating the LLM payload with tool results:

```mermaid
graph LR
    subgraph "Tool Execution Result"
        ToolCall["Tool Call<br/>{id, name, arguments}"]
        ToolResult["Tool Result<br/>{output, error}"]
    end
    
    subgraph "Payload Update"
        AssistantMessage["Assistant Message<br/>role: 'assistant'<br/>tool_calls: [...]"]
        ToolMessage["Tool Message<br/>role: 'tool'<br/>tool_call_id: id<br/>content: result"]
    end
    
    subgraph "LLM Continuation"
        UpdatedPayload["payload.messages.push()"]
        NextIteration["Next handleOneTurnStream"]
        ContinuedResponse["Continued LLM Response"]
    end
    
    ToolCall --> AssistantMessage
    ToolResult --> ToolMessage
    AssistantMessage --> UpdatedPayload
    ToolMessage --> UpdatedPayload
    UpdatedPayload --> NextIteration
    NextIteration --> ContinuedResponse
```

The system implements iterative processing with a maximum of 5 iterations to handle tool chains while preventing infinite loops:

```mermaid
graph TB
    StartIteration["Start Iteration<br/>iterations = 0"]
    CheckMessages["previousMessageCount vs<br/>currentMessageCount"]
    HandleTurn["handleOneTurnStream"]
    UpdateCount["currentMessageCount =<br/>payload.messages.length"]
    CheckLimit["iterations < MAX_ITERATIONS<br/>(5)"]
    ContinueLoop["Continue Loop"]
    ExitLoop["Exit Loop"]
    
    StartIteration --> HandleTurn
    HandleTurn --> UpdateCount
    UpdateCount --> CheckMessages
    CheckMessages -->|New Messages| CheckLimit
    CheckMessages -->|No New Messages| ExitLoop
    CheckLimit -->|True| ContinueLoop
    CheckLimit -->|False| ExitLoop
    ContinueLoop --> HandleTurn
```

Sources: [src/routes/responses.ts:401-414](), [src/routes/responses.ts:729-755](), [src/routes/responses.ts:834-856]()

---

