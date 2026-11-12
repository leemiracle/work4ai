<!-- source: DeepWiki mcp.deepwiki.com · repo the-open-agent/openagent · page 5 Agent Tools & MCP Integration · fetched 2026-10-26 -->

# Agent Tools & MCP Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [controllers/message_writer.go](controllers/message_writer.go)
- [model/mcp.go](model/mcp.go)
- [object/merge_agent_tools.go](object/merge_agent_tools.go)
- [object/message_tool.go](object/message_tool.go)
- [object/resource_archive_tool.go](object/resource_archive_tool.go)
- [web/src/chat/GeneratedResourceList.js](web/src/chat/GeneratedResourceList.js)
- [web/src/chat/ToolCallSection.js](web/src/chat/ToolCallSection.js)
- [web/src/chat/toolCallStream.js](web/src/chat/toolCallStream.js)

</details>



OpenAgent features a comprehensive tool execution system that enables AI models to interact with the physical and digital world. The system supports a wide range of built-in capabilities—from web searching and shell execution to complex Windows desktop automation—and integrates the **Model Context Protocol (MCP)** for standardized communication with external tool servers.

## Tool System Architecture

The tool system is built around a unified execution loop that manages discovery, parameter normalization, and recursive feedback. Tools are associated with a `Store` [object/merge_agent_tools.go:23-25]() and are provided to the model during the chat lifecycle.

### Tool Execution Loop

The core orchestration logic resides in `QueryTextWithTools` [model/mcp.go:162-172](). When an AI model generates a tool call, the system enters a multi-round loop:

1.  **Call Detection**: The system monitors the model response and uses `normalizeToolCalls` to standardize outputs from various providers into OpenAI-compatible formats [model/mcp.go:139-160]().
2.  **Execution**: The orchestrator identifies the target tool (either a built-in or an external MCP tool) and invokes `callMcpTool` [model/mcp.go:194-205]().
3.  **Feedback**: Results are appended to the `RawMessage` history [model/mcp.go:197-202]().
4.  **Recovery**: If a tool fails, the system injects a `toolErrorRecoveryPrompt` [model/mcp.go:59-60]() to guide the model toward a correction rather than giving up [model/mcp.go:222-227]().

### Natural Language to Code Entity Mapping

The following diagram illustrates how high-level tool requests are translated into specific backend implementations and external connections.

**Tool Resolution Diagram**
```mermaid
graph TD
    "User"["User Natural Language"] -- "Chat Request" --> "MessagePipeline"["controllers.GetMessageAnswer"]
    "MessagePipeline" -- "Tool Definitions" --> "LLM"["LLM Provider"]
    "LLM" -- "Function Call" --> "ToolOrchestrator"["model.QueryTextWithTools"]
    
    subgraph "Code Entity Space"
        "ToolOrchestrator" -- "McpToolSet" --> "Registry"["object.buildMergedBuiltinRegistry"]
        "Registry" -- "Built-in" --> "ToolFactory"["tool.New"]
        "Registry" -- "External" --> "McpClient"["mcp.GetToolsFromURL"]
        
        "ToolFactory" --> "Office"["tool.OfficeTool"]
        "ToolFactory" --> "Shell"["tool.ShellTool"]
        "ToolFactory" --> "ResourceWrapper"["object.generatedResourceArchiveBuiltinTool"]
        
        "McpClient" --> "McpServer"["Remote MCP Server"]
    end
    
    "Office" -- "Result" --> "ToolOrchestrator"
    "McpServer" -- "Result" --> "ToolOrchestrator"
```
**Sources:** [model/mcp.go:162-212](), [object/merge_agent_tools.go:23-65](), [object/resource_archive_tool.go:30-49]()

---

## Built-in Tools

OpenAgent includes a variety of native tools that require no external servers. These are instantiated via the `tool.New` factory. A key feature is the **Resource Archiving Wrapper**, which automatically captures files created by tools (like Excel or Word reports) and saves them to the system's persistent storage [object/resource_archive_tool.go:72-101]().

| Tool Type | Description | Key Code Entity |
| :--- | :--- | :--- |
| `web_search` | Search via DuckDuckGo, Google, or Baidu. | `mcp.ToolSet.WebSearchEnabled` [object/merge_agent_tools.go:69-75]() |
| `shell` | Executes system shell commands. | `tool.ShellTool` |
| `office` | Manipulates Word, Excel, and PPT files. | `pptx_write`, `word_write`, `excel_write` [object/resource_archive_tool.go:51-58]() |
| `local_file` | File system operations. | `local_file_write` [object/resource_archive_tool.go:53]() |
| `gui` | Windows User Interface Automation (UIA). | `tool.WindowsUiaTool` |

For a full list of implementations and configuration options, see **[Built-in Tools](#5.1)**.

---

## MCP Server Integration

The **Model Context Protocol (MCP)** allows OpenAgent to connect to external servers. The system merges these external capabilities with built-in tools into a unified `McpToolSet` [object/merge_agent_tools.go:69-93]().

### Server Management
*   **Tool Discovery**: OpenAgent fetches tool schemas from remote MCP endpoints and converts them to the model's expected format using `reverseToolsToOpenAi` [model/mcp.go:85-107]().
*   **Session Handling**: Tool sessions are maintained via `ToolSession` [model/mcp.go:40-43](), which tracks the `McpToolSet` and accumulated `ToolMessages`.
*   **Streaming**: Tool call progress (deltas) is streamed to the frontend via SSE events like `tool-delta` and `tool-start` [controllers/message_writer.go:58-67]().

For details on connecting and managing MCP servers, see **[MCP Server Management](#5.2)**.

---

## Browser & Computer-Use Capabilities

OpenAgent push the boundaries of agentic behavior with its "Computer Use" capabilities. This system combines specialized tools with a remote desktop infrastructure.

**Infrastructure Mapping**
```mermaid
graph LR
    subgraph "Frontend (React)"
        "UI"["ToolCallCard.js"]
        "ResList"["GeneratedResourceList.js"]
    end

    subgraph "Backend (Go)"
        "Writer"["controllers.RefinedWriter"]
        "Archiver"["object.archiveGeneratedResourceFile"]
    end

    subgraph "Execution"
        "Browser"["tool.BrowserUseTool"]
        "Storage"["object.UploadFileToStorageSafe"]
    end

    "UI" -- "Renders Progress" --> "Writer"
    "Browser" -- "Generates File" --> "Archiver"
    "Archiver" -- "Persists" --> "Storage"
    "Storage" -- "URI" --> "ResList"
```
**Sources:** [controllers/message_writer.go:85-92](), [web/src/chat/ToolCallSection.js:70-130](), [object/resource_archive_tool.go:119-155]()

The frontend provides real-time visualization of tool execution through `ToolCallCard`, showing arguments, status (Executing/Done/Error), and output [web/src/chat/ToolCallSection.js:132-177]().

For details on the Guacamole tunnel and desktop UI, see **[Browser & Computer-Use Agent](#5.3)**.

---

## Administrative & Testing UI

OpenAgent provides specialized widgets for developers to debug tool execution:
*   **ToolCallSection**: React component for rendering streaming tool arguments and results in the chat interface [web/src/chat/ToolCallSection.js:190-210]().
*   **GeneratedResourceList**: Automatically displays download cards for any files (PDFs, Images, etc.) created during a tool session [web/src/chat/GeneratedResourceList.js:87-124]().
*   **ToolDelta Stream**: Client-side logic for merging incremental tool argument updates [web/src/chat/tool_delta_stream.js:35-62]().

**Sources:**
* `model/mcp.go`: [model/mcp.go:162-230]()
* `object/merge_agent_tools.go`: [object/merge_agent_tools.go:69-93]()
* `controllers/message_writer.go`: [controllers/message_writer.go:58-83]()
* `object/resource_archive_tool.go`: [object/resource_archive_tool.go:72-101]()
* `web/src/chat/ToolCallSection.js`: [web/src/chat/ToolCallSection.js:132-177]()

---

