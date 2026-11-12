<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/poml · page 6 Language Model Integration · fetched 2026-10-26 -->

# Language Model Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/vscode/configuration.md](docs/vscode/configuration.md)
- [examples/110_code_review.poml](examples/110_code_review.poml)
- [examples/assets/110_sample_code.py](examples/assets/110_sample_code.py)
- [examples/expects/110_code_review.txt](examples/expects/110_code_review.txt)
- [packages/poml-vscode/command/testCommand.ts](packages/poml-vscode/command/testCommand.ts)
- [packages/poml-vscode/settings.ts](packages/poml-vscode/settings.ts)

</details>



This document covers how POML integrates with various language model providers to execute prompts and handle responses. It explains the provider routing system, message format conversion, streaming capabilities, and tool integration.

For information about configuring language model settings in VS Code, see [Provider Configuration](#6.1). For details about defining response schemas and tools within POML documents, see [Response Schemas and Tools](#6.2).

## Architecture Overview

POML's language model integration is built around a flexible provider system that supports multiple AI services through a unified interface. The system handles provider routing, message format conversion, streaming responses, and tool calling.

### Provider Integration Architecture

```mermaid
graph TB
    subgraph "POML Document Processing"
        A[PomlFile] --> B["PreviewResponse"]
        B --> C["Message[]"]
        B --> D["responseSchema"]
        B --> E["tools"]
        B --> F["runtime config"]
    end
    
    subgraph "Provider Routing"
        G["TestCommand.routeStream()"] --> H["getActiveVercelModelProvider()"]
        H --> I["Provider Factory"]
        I --> J["createOpenAI()"]
        I --> K["createAnthropic()"]
        I --> L["createGoogleGenerativeAI()"]
        I --> M["createAzure()"]
        I --> N["vscode.lm API"]
    end
    
    subgraph "Stream Processing"
        O["streamText()"] --> P["TextStreamPart"]
        Q["streamObject()"] --> R["ObjectStreamPart"]
        S["vscodeModelStream()"] --> T["VS Code Stream"]
        U["azureAiStream()"] --> V["SSE Stream"]
    end
    
    C --> G
    D --> G
    E --> G
    F --> G
    
    G --> O
    G --> Q
    G --> S
    G --> U
    
    P --> W["processStreamChunk()"]
    R --> W
    T --> W
    V --> W
```

Sources: [packages/poml-vscode/command/testCommand.ts:259-273](), [packages/poml-vscode/command/testCommand.ts:526-591]()

## Provider Configuration System

The language model integration supports multiple providers with flexible configuration options. Settings can be specified globally or overridden at runtime within POML documents.

### Provider Settings Structure

```mermaid
graph LR
    subgraph "Settings Management"
        A["SettingsManager"] --> B["Settings.getForResource()"]
        B --> C["LanguageModelSetting"]
    end
    
    subgraph "Configuration Schema"
        C --> D["provider: LanguageModelProvider"]
        C --> E["model: string"]
        C --> F["apiKey: ApiConfigValue"]
        C --> G["apiUrl: ApiConfigValue"]
        C --> H["temperature?: number"]
        C --> I["maxTokens?: number"]
    end
    
    subgraph "Provider Types"
        J["vscode"] --> D
        K["openai"] --> D
        L["anthropic"] --> D
        M["google"] --> D
        N["microsoft"] --> D
        O["openaiResponse"] --> D
    end
    
    subgraph "API Configuration"
        P["string | {provider: string}"] --> F
        P --> G
    end
```

Sources: [packages/poml-vscode/settings.ts:4-16](), [packages/poml-vscode/settings.ts:62-70]()

### Provider-Specific Configuration

| Provider | Factory Function | Purpose |
|----------|------------------|---------|
| `vscode` | `vscode.lm.selectChatModels()` | GitHub Copilot integration |
| `openai` | `createOpenAI().chat` | OpenAI API |
| `openaiResponse` | `createOpenAI().responses` | OpenAI with response format |
| `anthropic` | `createAnthropic()` | Anthropic Claude |
| `google` | `createGoogleGenerativeAI()` | Google Gemini |
| `microsoft` | `createAzure()` | Azure OpenAI |

Sources: [packages/poml-vscode/command/testCommand.ts:550-580]()

## Message Format Conversion

The system converts POML messages to provider-specific formats, handling rich content types including text, images, tool calls, and tool results.

### Message Conversion Pipeline

```mermaid
graph TD
    subgraph "POML Message Format"
        A["Message[]"] --> B["speaker: 'human'|'ai'|'system'|'tool'"]
        A --> C["content: RichContent"]
        C --> D["string | ContentPart[]"]
        D --> E["ContentMultiMediaBinary"]
        D --> F["ContentMultiMediaToolRequest"]
        D --> G["ContentMultiMediaToolResponse"]
    end
    
    subgraph "Provider Conversions"
        H["pomlMessagesToVercelMessage()"] --> I["ModelMessage[]"]
        J["pomlMessagesToVsCodeMessage()"] --> K["LanguageModelChatMessage[]"]
        L["toMessageObjects()"] --> M["OpenAI/Azure format"]
    end
    
    subgraph "Content Type Mapping"
        N["TextPart"] --> I
        O["ImagePart"] --> I
        P["ToolCallPart"] --> I
        Q["ToolResultPart"] --> I
    end
    
    A --> H
    A --> J
    A --> L
    
    E --> O
    F --> P
    G --> Q
```

Sources: [packages/poml-vscode/command/testCommand.ts:622-673](), [packages/poml-vscode/command/testCommand.ts:717-756]()

### Speaker Role Mapping

The system maps POML speaker types to provider-specific roles:

| POML Speaker | Vercel AI | VS Code API | OpenAI/Azure |
|--------------|-----------|-------------|--------------|
| `human` | `user` | `User` | `user` |
| `ai` | `assistant` | `Assistant` | `assistant` |
| `system` | `system` | `User` | `system` |
| `tool` | `tool` | `User` | `tool` |

Sources: [packages/poml-vscode/command/testCommand.ts:623-628](), [packages/poml-vscode/command/testCommand.ts:723-741]()

## Stream Processing and Response Handling

The system provides real-time streaming of language model responses with different handling strategies based on response type and provider capabilities.

### Stream Routing Logic

```mermaid
graph TD
    subgraph "Stream Routing Decision"
        A["routeStream()"] --> B{"provider === 'vscode'?"}
        B -->|Yes| C["vscodeModelStream()"]
        B -->|No| D{"Azure AI endpoint?"}
        D -->|Yes| E["azureAiStream()"]
        D -->|No| F{"responseSchema && !tools?"}
        F -->|Yes| G["handleResponseSchemaStream()"]
        F -->|No| H["handleRegularTextStream()"]
    end
    
    subgraph "Stream Processing"
        I["streamText()"] --> J["TextStreamPart"]
        K["streamObject()"] --> L["ObjectStreamPart"]
        M["model.sendRequest()"] --> N["VS Code Stream"]
        O["createSseStream()"] --> P["SSE Events"]
    end
    
    subgraph "Chunk Processing"
        Q["processStreamChunk()"] --> R["text-delta"]
        Q --> S["tool-call"]
        Q --> T["finish"]
        Q --> U["reasoning-delta"]
    end
    
    G --> K
    H --> I
    C --> M
    E --> O
    
    J --> Q
    L --> Q
    N --> Q
    P --> Q
```

Sources: [packages/poml-vscode/command/testCommand.ts:259-273](), [packages/poml-vscode/command/testCommand.ts:372-400]()

### Response Chunk Types

The system handles various stream chunk types with specific formatting:

| Chunk Type | Processing | Output Format |
|------------|------------|---------------|
| `text-delta` | Direct output | Raw text |
| `tool-call` | Format tool info | `Tool call (id) name Input: {...}` |
| `reasoning-delta` | O1 model reasoning | Raw reasoning text |
| `finish` | Usage statistics | `[Usage: input=N, output=N, total=N]` |
| `abort` | Cancellation | `[Aborted]` |

Sources: [packages/poml-vscode/command/testCommand.ts:372-417]()

## Tool Integration

The system supports tool calling through provider-specific implementations, converting POML tool definitions to the appropriate format for each provider.

### Tool Conversion Architecture

```mermaid
graph TD
    subgraph "POML Tool Definition"
        A["tools: {name, parameters, description, type}[]"] --> B["Tool Schema Validation"]
        B --> C{"type === 'function'?"}
        C -->|No| D["Error: Unsupported tool type"]
        C -->|Yes| E["Tool Processing"]
    end
    
    subgraph "Provider Tool Formats"
        F["toVercelTools()"] --> G["Tool with jsonSchema()"]
        H["toVsCodeTools()"] --> I["LanguageModelChatTool[]"]
        J["Azure AI"] --> K["OpenAI tool format"]
    end
    
    subgraph "Tool Execution Flow"
        L["ContentMultiMediaToolRequest"] --> M["ToolCallPart"]
        N["ContentMultiMediaToolResponse"] --> O["ToolResultPart"]
        P["richContentToVercelToolResult()"] --> Q["Formatted tool output"]
    end
    
    E --> F
    E --> H
    E --> J
    
    M --> L
    O --> N
    Q --> O
```

Sources: [packages/poml-vscode/command/testCommand.ts:675-692](), [packages/poml-vscode/command/testCommand.ts:821-837]()

### VS Code Tool Integration

The VS Code provider has specific handling for tool calls and results:

```mermaid
graph LR
    subgraph "VS Code Tool Flow"
        A["POML Tool Request"] --> B["LanguageModelToolCallPart"]
        B --> C["callId, name, input"]
        D["Tool Response"] --> E["LanguageModelToolResultPart"]
        E --> F["callId, content[]"]
        G["richContentToVsCodeMessageContent()"] --> H["Flattened string content"]
    end
    
    I["Image content"] --> J["[Image: placeholder text]"]
    K["Mixed content"] --> L["JSON.stringify() fallback"]
```

Sources: [packages/poml-vscode/command/testCommand.ts:799-819](), [packages/poml-vscode/command/testCommand.ts:762-819]()

## Error Handling and Monitoring

The system provides comprehensive error handling, abort controls, and telemetry reporting for language model interactions.

### Generation Control System

```mermaid
graph TD
    subgraph "Abort Control"
        A["GenerationController"] --> B["abortControllers: AbortController[]"]
        A --> C["cancellationTokens: CancellationTokenSource[]"]
        D["getNewAbortController()"] --> E["New AbortController"]
        F["getNewCancellationToken()"] --> G["New CancellationTokenSource"]
        H["abortAll()"] --> I["Cancel all active operations"]
    end
    
    subgraph "Error Handling"
        J["try/catch blocks"] --> K["Provider errors"]
        L["onError callbacks"] --> M["Stream errors"]
        N["API validation"] --> O["Configuration errors"]
    end
    
    subgraph "Telemetry Reporting"
        P["TelemetryEvent.PromptTestingStart"] --> Q["Request parameters"]
        R["TelemetryEvent.PromptTestingEnd"] --> S["Response data"]
        T["TelemetryEvent.PromptTestingError"] --> U["Error details"]
        V["TelemetryEvent.PromptTestingAbort"] --> W["Abort events"]
    end
```

Sources: [packages/poml-vscode/command/testCommand.ts:41-80](), [packages/poml-vscode/command/testCommand.ts:184-236]()

### Provider Validation

The system performs comprehensive validation before executing requests:

| Validation Type | Check | Error Message |
|-----------------|-------|---------------|
| Provider set | `!setting.provider` | "Language model provider is not configured" |
| Model set | `!setting.model` | "Language model is not configured" |
| API key | `!apiKey && provider !== 'vscode'` | "API key is not configured" |
| VS Code API | `!vscode.lm?.selectChatModels` | "VS Code language model API is not available" |

Sources: [packages/poml-vscode/command/testCommand.ts:138-152](), [packages/poml-vscode/command/testCommand.ts:420-422]()

---

