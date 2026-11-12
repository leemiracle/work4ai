<!-- source: DeepWiki mcp.deepwiki.com · repo openai/gpt-oss · page 6 Client Applications · fetched 2026-10-26 -->

# Client Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gpt_oss/chat.py](gpt_oss/chat.py)
- [gpt_oss/responses_api/api_server.py](gpt_oss/responses_api/api_server.py)

</details>



This document covers the client applications and interfaces provided for interacting with gpt-oss models. These applications demonstrate different interaction patterns and serve as reference implementations for building custom interfaces. For information about the underlying inference backends, see [Inference Backends](#4). For details about the tools and capabilities exposed through these clients, see [Tools and Capabilities](#5).

## Client Architecture Overview

The gpt-oss ecosystem provides multiple client applications that interface with different inference backends through standardized protocols. The primary communication formats are the `openai-harmony` encoding for direct model interaction and the `Responses API` for programmatic and web access.

**Client Applications Architecture**

```mermaid
graph TB
    subgraph "Client_Applications"
        ["gpt_oss.chat"]
        ["streamlit_chat.py"]
        ["gradio_chat.py"]
        ["gpt_oss.responses_api.serve"]
        ["Agent_SDK_Examples"]
    end
    
    subgraph "Protocol_Layer"
        ["HarmonyEncoding"]
        ["Responses_API_SSE"]
    end
    
    subgraph "Inference_Backends"
        ["Triton_Generator"]
        ["Torch_Generator"] 
        ["VLLM_Generator"]
        ["Metal_Backend"]
        ["Ollama_Backend"]
    end
    
    subgraph "Tool_Integration"
        ["SimpleBrowserTool"]
        ["PythonTool"]
        ["apply_patch"]
    end
    
    ["gpt_oss.chat"] --> ["HarmonyEncoding"]
    ["gpt_oss.chat"] --> ["Triton_Generator"]
    ["gpt_oss.chat"] --> ["Torch_Generator"]
    ["gpt_oss.chat"] --> ["VLLM_Generator"]
    
    ["streamlit_chat.py"] --> ["Responses_API_SSE"]
    ["gradio_chat.py"] --> ["Responses_API_SSE"]
    ["gpt_oss.responses_api.serve"] --> ["Responses_API_SSE"]
    ["Responses_API_SSE"] --> ["Metal_Backend"]
    ["Responses_API_SSE"] --> ["Ollama_Backend"]
    
    ["Agent_SDK_Examples"] --> ["Responses_API_SSE"]
    
    ["gpt_oss.chat"] --> ["SimpleBrowserTool"]
    ["gpt_oss.chat"] --> ["PythonTool"]
    ["gpt_oss.chat"] --> ["apply_patch"]
    ["gpt_oss.responses_api.serve"] --> ["SimpleBrowserTool"]
    ["gpt_oss.responses_api.serve"] --> ["PythonTool"]
```

Sources: [gpt_oss/chat.py:62-79](), [gpt_oss/responses_api/api_server.py:100-102](), [gpt_oss/chat.py:87-102]()

## Terminal Chat Interface

The terminal chat interface provides a command-line application for interactive conversations with gpt-oss models. The implementation is located in `gpt_oss.chat` and supports multiple inference backends with optional tool integration. For details, see [Terminal Chat Interface](#6.1).

### Core Implementation

The main chat loop implemented in the `gpt_oss.chat` module provides:

1.  **Backend Selection**: Dynamically imports and initializes `TokenGenerator` variants based on the `--backend` argument [gpt_oss/chat.py:62-77]().
2.  **System Message Construction**: Builds `SystemContent` with `ReasoningEffort` and tool configurations [gpt_oss/chat.py:81-102]().
3.  **Interactive Loop**: Processes user input via `input()` and broadcasts it across distributed nodes if necessary [gpt_oss/chat.py:49-58]().
4.  **Stream Parsing**: Uses `StreamableParser` from `openai-harmony` to handle real-time token generation and tool dispatch [gpt_oss/chat.py:221-230]().

**Terminal Chat Implementation Flow**

```mermaid
graph TD
    ["main()"] --> ["Backend_Selection"]
    ["Backend_Selection"] --> ["TritonGenerator"]
    ["Backend_Selection"] --> ["TorchGenerator"] 
    ["Backend_Selection"] --> ["VLLMGenerator"]
    
    ["main()"] --> ["SystemContent"]
    ["SystemContent"] --> ["with_reasoning_effort()"]
    ["SystemContent"] --> ["with_tools()"]
    
    ["main()"] --> ["Interactive_Loop"]
    ["Interactive_Loop"] --> ["get_user_input()"]
    ["Interactive_Loop"] --> ["generator.generate()"]
    ["Interactive_Loop"] --> ["StreamableParser"]
    
    ["StreamableParser"] --> ["Tool_Dispatch"]
    ["Tool_Dispatch"] --> ["SimpleBrowserTool"]
    ["Tool_Dispatch"] --> ["PythonTool"]
    ["Tool_Dispatch"] --> ["apply_patch"]
```

Sources: [gpt_oss/chat.py:49-102](), [gpt_oss/chat.py:171-200]()

## Web Interfaces

The gpt-oss repository includes web-based chat interfaces that provide rich UI controls for configuring model behavior and tools. These interfaces communicate with gpt-oss models through the Responses API protocol. For details, see [Web Interfaces](#6.2).

### Common Features

Web interfaces typically provide:

| Feature | Description | Implementation |
| :--- | :--- | :--- |
| **Model Configuration** | Backend and parameter selection | `ResponsesRequest` fields |
| **Tool Integration** | Enable/disable browser and python tools | `SimpleBrowserTool` / `PythonTool` |
| **Streaming Responses** | Real-time message display | `StreamingResponse` (SSE) |
| **Reasoning Effort** | Control model depth | `get_reasoning_effort` |

Sources: [gpt_oss/responses_api/api_server.py:9-25](), [gpt_oss/responses_api/api_server.py:74-85]()

## Responses API Server

The Responses API server provides an HTTP/SSE interface compatible with the Responses API specification. This server implementation demonstrates how to expose gpt-oss models through standardized web APIs. For details, see [Responses API Server](#6.3).

### Server Architecture

The server, created via `create_api_server`, supports multiple inference backends and implements core Responses API endpoints using FastAPI [gpt_oss/responses_api/api_server.py:100-103]().

**Responses API Server Architecture**

```mermaid
graph TD
    ["serve.py"] --> ["create_api_server()"]
    ["create_api_server()"] --> ["FastAPI_App"]
    
    ["FastAPI_App"] --> ["POST_/v1/responses"]
    ["FastAPI_App"] --> ["generate_response()"]
    
    ["generate_response()"] --> ["encoding.parse_messages_from_completion_tokens()"]
    ["generate_response()"] --> ["Tool_Execution_Logic"]
    
    ["Tool_Execution_Logic"] --> ["SimpleBrowserTool"]
    ["Tool_Execution_Logic"] --> ["PythonTool"]
    
    ["generate_response()"] --> ["ResponseObject"]
```

Sources: [gpt_oss/responses_api/api_server.py:100-136](), [gpt_oss/responses_api/api_server.py:153-196]()

## Agent SDK Examples

The gpt-oss project provides examples for integrating with modern Agent SDKs in both Python and TypeScript. These examples demonstrate how to build agentic applications using the Model Context Protocol (MCP) and standard AI SDKs. For details, see [Agent SDK Examples](#6.4).

### Integration Patterns

- **Python SDK**: Uses `AsyncOpenAI` client pointing to the Responses API server, combined with `MCPServerStdio` for tool discovery.
- **TypeScript SDK**: Implements compatibility tests and agentic loops using the Responses API schema.

Sources: [gpt_oss/responses_api/types.py:60-61](), [gpt_oss/responses_api/api_server.py:10-22]()

---

