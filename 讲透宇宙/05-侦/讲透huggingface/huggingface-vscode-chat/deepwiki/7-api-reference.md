<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/huggingface-vscode-chat · page 7 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/provider.ts](src/provider.ts)
- [src/types.ts](src/types.ts)
- [src/utils.ts](src/utils.ts)

</details>



This document provides a comprehensive reference for the extension's public and internal APIs. It covers the provider implementation, utility functions, and type definitions that together enable the Hugging Face chat integration with VS Code.

For configuration-related APIs and options, see [Configuration Reference](#6). For architectural patterns and design decisions, see [Architecture](#3).

## API Overview

The extension's API surface consists of three primary layers: the VS Code provider interface implementation, data conversion utilities, and type definitions for internal and external data structures.

```mermaid
graph TB
    subgraph "VS Code Extension API Surface"
        ProviderClass["HuggingFaceChatModelProvider<br/>(src/provider.ts)"]
        ExtActivation["Extension Activation<br/>(src/extension.ts)"]
    end
    
    subgraph "Core API Methods"
        PrepareInfo["prepareLanguageModelChatInformation()"]
        ProvideResponse["provideLanguageModelChatResponse()"]
        ProvideTokens["provideTokenCount()"]
        EnsureKey["ensureApiKey()"]
    end
    
    subgraph "Utility API Layer"
        ConvertMsg["convertMessages()"]
        ConvertTools["convertTools()"]
        ValidateReq["validateRequest()"]
        ValidateTools["validateTools()"]
        TryParse["tryParseJSONObject()"]
        SanitizeSchema["sanitizeSchema()"]
        SanitizeName["sanitizeFunctionName()"]
    end
    
    subgraph "Type Definitions API"
        OpenAITypes["OpenAIChatMessage<br/>OpenAIToolCall<br/>OpenAIFunctionToolDef"]
        HFTypes["HFModelItem<br/>HFProvider<br/>HFArchitecture<br/>HFModelsResponse"]
        BufferTypes["ToolCallBuffer"]
    end
    
    ProviderClass -->|implements| PrepareInfo
    ProviderClass -->|implements| ProvideResponse
    ProviderClass -->|implements| ProvideTokens
    ProviderClass -->|uses| EnsureKey
    
    PrepareInfo -->|calls| EnsureKey
    ProvideResponse -->|calls| ConvertMsg
    ProvideResponse -->|calls| ConvertTools
    ProvideResponse -->|calls| ValidateReq
    
    ConvertTools -->|calls| ValidateTools
    ConvertTools -->|calls| SanitizeSchema
    ConvertTools -->|calls| SanitizeName
    ConvertMsg -->|uses| TryParse
    
    PrepareInfo -->|returns| HFTypes
    ProvideResponse -->|consumes| OpenAITypes
    ProvideResponse -->|produces| BufferTypes
    
    ConvertMsg -->|produces| OpenAITypes
    ConvertTools -->|produces| OpenAITypes
```

**Sources:** [src/provider.ts](), [src/utils.ts](), [src/types.ts](), [src/extension.ts]()

## Core API Components

### Provider Interface

The `HuggingFaceChatModelProvider` class implements VS Code's `LanguageModelChatProvider` interface, providing the primary integration point with the editor's language model API.

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `prepareLanguageModelChatInformation()` | Discovers and returns available Hugging Face models | `Promise<LanguageModelChatInformation[]>` |
| `provideLanguageModelChatResponse()` | Streams chat completion responses with tool calling support | `Promise<void>` |
| `provideTokenCount()` | Estimates token count for messages or text | `Promise<number>` |

Detailed method signatures and implementation details are documented in [Provider API](#7.1).

**Sources:** [src/provider.ts:23-781]()

### Conversion Utilities

The utility layer transforms VS Code data structures into OpenAI-compatible formats for the Hugging Face Router API:

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `convertMessages()` | `LanguageModelChatMessage[]` | `OpenAIChatMessage[]` | Converts VS Code messages to OpenAI format |
| `convertTools()` | `LanguageModelChatRequestHandleOptions` | `{tools?, tool_choice?}` | Converts tool definitions with sanitization |
| `validateRequest()` | `LanguageModelChatMessage[]` | `void` (throws on error) | Validates tool call/result pairing |
| `validateTools()` | `LanguageModelChatTool[]` | `void` (throws on error) | Validates tool name format |
| `tryParseJSONObject()` | `string` | `{ok: boolean, value?}` | Safely parses JSON objects |

Complete function documentation is available in [Utility Functions API](#7.2).

**Sources:** [src/utils.ts:143-363]()

### Type System

The type definitions provide contracts between VS Code, the extension, and the Hugging Face API:

- **OpenAI Types**: `OpenAIChatMessage`, `OpenAIToolCall`, `OpenAIFunctionToolDef` - wire format for API requests
- **Hugging Face Types**: `HFModelItem`, `HFProvider`, `HFModelsResponse` - model discovery responses
- **Internal Types**: `ToolCallBuffer` - streaming state management

Type definitions are fully documented in [Type Definitions](#7.3).

**Sources:** [src/types.ts:1-85]()

## API Interaction Flow

The following diagram illustrates how API components interact during a typical chat request:

```mermaid
sequenceDiagram
    participant VSCode as "VS Code LM API"
    participant Provider as "HuggingFaceChatModelProvider"
    participant Utils as "Utility Functions"
    participant HF as "Hugging Face Router"
    
    VSCode->>Provider: provideLanguageModelChatResponse(model, messages, options, progress, token)
    
    activate Provider
    Provider->>Provider: Reset buffers (_toolCallBuffers, etc.)
    Provider->>Provider: ensureApiKey(silent=true)
    
    Provider->>Utils: validateRequest(messages)
    Utils-->>Provider: void (or throws)
    
    Provider->>Utils: convertMessages(messages)
    Utils-->>Provider: OpenAIChatMessage[]
    
    alt options.tools exists
        Provider->>Utils: convertTools(options)
        Utils->>Utils: sanitizeFunctionName(tool.name)
        Utils->>Utils: sanitizeSchema(tool.inputSchema)
        Utils-->>Provider: {tools: OpenAIFunctionToolDef[], tool_choice}
    end
    
    Provider->>Provider: estimateMessagesTokens(messages)
    Provider->>Provider: estimateToolTokens(tools)
    
    Provider->>HF: POST /v1/chat/completions
    
    loop Stream chunks
        HF-->>Provider: SSE chunk
        Provider->>Provider: processStreamingResponse(body, progress, token)
        Provider->>Provider: processDelta(parsed)
        
        alt Text content
            Provider->>Provider: processTextContent(content, progress)
            Provider->>Utils: tryParseJSONObject(argText)
            Provider->>VSCode: progress.report(TextPart/ToolCallPart)
        else SSE tool_calls
            Provider->>Provider: Buffer deltas (_toolCallBuffers.set)
            Provider->>Provider: tryEmitBufferedToolCall(index, progress)
            Provider->>Utils: tryParseJSONObject(buf.args)
            Provider->>VSCode: progress.report(ToolCallPart)
        end
    end
    
    HF-->>Provider: [DONE]
    Provider->>Provider: flushToolCallBuffers(progress, throwOnInvalid=false)
    deactivate Provider
    
    Provider-->>VSCode: Promise<void> resolves
```

**Sources:** [src/provider.ts:214-327](), [src/provider.ts:381-431](), [src/provider.ts:438-528](), [src/utils.ts:143-227]()

## Data Transformation Architecture

This diagram maps the transformation pipeline from VS Code types through internal processing to external API formats:

```mermaid
graph LR
    subgraph "VS Code Input Types"
        VSLM["LanguageModelChatMessage"]
        VSTool["LanguageModelChatTool"]
        VSText["LanguageModelTextPart"]
        VSToolCall["LanguageModelToolCallPart"]
        VSToolResult["LanguageModelToolResultPart"]
    end
    
    subgraph "Conversion Layer<br/>(src/utils.ts)"
        ConvMsg["convertMessages()<br/>lines 143-186"]
        ConvTools["convertTools()<br/>lines 192-227"]
        SanitName["sanitizeFunctionName()<br/>lines 27-37"]
        SanitSchema["sanitizeSchema()<br/>lines 68-136"]
        MapRole["mapRole()<br/>lines 310-321"]
    end
    
    subgraph "OpenAI Wire Format"
        OAIMsg["OpenAIChatMessage"]
        OAIToolCall["OpenAIToolCall"]
        OAIToolDef["OpenAIFunctionToolDef"]
    end
    
    subgraph "Response Types"
        VSResponse["LanguageModelResponsePart"]
        VSRespText["LanguageModelTextPart"]
        VSRespTool["LanguageModelToolCallPart"]
    end
    
    VSLM -->|input| ConvMsg
    VSText -->|extracted by| ConvMsg
    VSToolCall -->|extracted by| ConvMsg
    VSToolResult -->|extracted by| ConvMsg
    
    VSTool -->|input| ConvTools
    ConvTools -->|uses| SanitName
    ConvTools -->|uses| SanitSchema
    ConvMsg -->|uses| MapRole
    
    ConvMsg -->|produces| OAIMsg
    ConvMsg -->|produces| OAIToolCall
    ConvTools -->|produces| OAIToolDef
    
    OAIMsg -->|sent to HF Router| API["POST /v1/chat/completions"]
    OAIToolDef -->|sent to HF Router| API
    
    API -->|streams| StreamData["SSE chunks with<br/>tool_calls deltas"]
    StreamData -->|parsed by| ProcessDelta["processDelta()<br/>provider.ts:438-528"]
    ProcessDelta -->|emits| VSRespText
    ProcessDelta -->|emits| VSRespTool
    VSRespText -->|implements| VSResponse
    VSRespTool -->|implements| VSResponse
```

**Sources:** [src/utils.ts:143-186](), [src/utils.ts:192-227](), [src/provider.ts:438-528](), [src/types.ts:1-28]()

## Internal State Management API

The provider maintains several internal state maps and buffers for streaming response processing:

| Property | Type | Purpose | Location |
|----------|------|---------|----------|
| `_toolCallBuffers` | `Map<number, {id?, name?, args}>` | Accumulates streamed tool call deltas by index | [src/provider.ts:26-29]() |
| `_completedToolCallIndices` | `Set<number>` | Tracks emitted tool calls to prevent duplicates | [src/provider.ts:32]() |
| `_hasEmittedAssistantText` | `boolean` | Tracks if text was emitted before tool calls | [src/provider.ts:35]() |
| `_emittedBeginToolCallsHint` | `boolean` | Tracks whitespace flush for UI linkifier | [src/provider.ts:38]() |
| `_textToolParserBuffer` | `string` | Buffers partial control tokens | [src/provider.ts:41]() |
| `_textToolActive` | `{name?, index?, argBuffer, emitted?}` | Active text-embedded tool call state | [src/provider.ts:42-49]() |
| `_emittedTextToolCallKeys` | `Set<string>` | Deduplication for text-based tool calls | [src/provider.ts:50]() |
| `_emittedTextToolCallIds` | `Set<string>` | Identity-based deduplication | [src/provider.ts:51]() |

These state properties are reset at the beginning of each `provideLanguageModelChatResponse()` call [src/provider.ts:222-229]() and cleaned up in the finally block [src/provider.ts:422-430]().

**Sources:** [src/provider.ts:24-51](), [src/provider.ts:222-229](), [src/provider.ts:420-430]()

## Schema Sanitization API

The schema sanitization system ensures tool definitions are compatible with the Hugging Face Router API:

```mermaid
graph TD
    Input["Input Schema<br/>(from VS Code tool definition)"]
    
    Input --> Prune["pruneUnknownSchemaKeywords()<br/>src/utils.ts:39-66"]
    
    Prune --> CheckComposite{"Contains anyOf/<br/>oneOf/allOf?"}
    CheckComposite -->|Yes| FlattenComposite["Flatten to single schema<br/>(prefer string type)<br/>lines 75-88"]
    CheckComposite -->|No| CheckType
    
    FlattenComposite --> CheckType{"Type field<br/>present?"}
    CheckType -->|No| SetObject["Set type='object'<br/>lines 93-96"]
    CheckType -->|Yes| CheckNumber
    
    SetObject --> CheckNumber
    CheckNumber{"type='number' AND<br/>isIntegerLikePropertyName()?"}
    CheckNumber -->|Yes| CoerceInt["Coerce to type='integer'<br/>lines 98-101"]
    CheckNumber -->|No| CheckObjType
    
    CoerceInt --> CheckObjType
    CheckObjType{"type='object'?"}
    CheckObjType -->|Yes| RecurseProps["Recursively sanitize<br/>properties object<br/>lines 104-111"]
    CheckObjType -->|No| CheckArrayType
    
    RecurseProps --> ValidateRequired["Validate 'required' array<br/>lines 113-118"]
    ValidateRequired --> CheckAdditional["Check additionalProperties<br/>lines 120-123"]
    CheckAdditional --> Output
    
    CheckArrayType{"type='array'?"}
    CheckArrayType -->|Yes| SanitizeItems["Recursively sanitize<br/>items schema<br/>lines 125-133"]
    CheckArrayType -->|No| Output
    
    SanitizeItems --> Output["Sanitized Schema Output"]
```

**Sources:** [src/utils.ts:39-136](), [src/utils.ts:6-25]()

## Tool Calling Protocol Support

The extension supports two parallel tool calling protocols:

### SSE-Based Tool Calls

Standard Server-Sent Events format with `tool_calls` deltas:

```typescript
// Streamed delta format from Hugging Face Router
{
  choices: [{
    delta: {
      tool_calls: [{
        index: 0,
        id: "call_abc123",
        function: {
          name: "get_weather",
          arguments: "{\"location\":"  // streamed incrementally
        }
      }]
    }
  }]
}
```

Processing occurs in [src/provider.ts:488-520](), with buffering at [src/provider.ts:504-515]() and emission at [src/provider.ts:709-733]().

### Text-Embedded Tool Calls

Control token-based format embedded in content stream:

```typescript
// Format: <|tool_call_begin|>name:index<|tool_call_argument_begin|>{"arg":"val"}<|tool_call_end|>
const BEGIN = "<|tool_call_begin|>";
const ARG_BEGIN = "<|tool_call_argument_begin|>";
const END = "<|tool_call_end|>";
```

Processing occurs in [src/provider.ts:534-657]() with state machine parsing and incremental JSON validation.

**Sources:** [src/provider.ts:488-520](), [src/provider.ts:534-657](), [src/provider.ts:709-733]()

## Error Handling Patterns

The API uses consistent error handling patterns across all layers:

| Error Type | Detection Location | Handling Strategy |
|------------|-------------------|-------------------|
| Invalid API key | `ensureApiKey()` [src/provider.ts:358-373]() | Prompt user (non-silent) or return undefined |
| Invalid tool names | `validateTools()` [src/utils.ts:233-242]() | Throw with descriptive message |
| Malformed messages | `validateRequest()` [src/utils.ts:248-290]() | Throw when tool calls lack matching results |
| Invalid JSON tool args | `tryParseJSONObject()` [src/utils.ts:350-363]() | Return `{ok: false}` for safe handling |
| Token limit exceeded | `provideLanguageModelChatResponse()` [src/provider.ts:264-267]() | Throw before API call |
| API HTTP errors | `fetchModels()` [src/provider.ts:178-189]() | Throw with status and response text |
| Streaming parse errors | `processStreamingResponse()` [src/provider.ts:412-417]() | Silently ignore malformed SSE lines |

All errors are logged with contextual information using `console.error()` with structured data objects.

**Sources:** [src/provider.ts:358-373](), [src/utils.ts:233-242](), [src/utils.ts:248-290](), [src/utils.ts:350-363](), [src/provider.ts:264-267]()

## API Constants and Defaults

| Constant | Value | Location | Purpose |
|----------|-------|----------|---------|
| `BASE_URL` | `"https://router.huggingface.co/v1"` | [src/provider.ts:16]() | Hugging Face Router API endpoint |
| `DEFAULT_MAX_OUTPUT_TOKENS` | `16000` | [src/provider.ts:17]() | Default max completion tokens |
| `DEFAULT_CONTEXT_LENGTH` | `128000` | [src/provider.ts:18]() | Default context window size |
| Token estimate divisor | `4` | [src/provider.ts:65](), [src/provider.ts:342]() | Characters per token approximation |
| Tool name max length | `64` | [src/utils.ts:36]() | Maximum sanitized function name length |
| Max tools per request | `128` | [src/provider.ts:257-259]() | Hard limit on tool count |

**Sources:** [src/provider.ts:16-18](), [src/provider.ts:257-259](), [src/utils.ts:36]()

## API Extension Points

For detailed API usage and examples, refer to the following sub-sections:

- **[Provider API](#7.1)**: Complete method signatures, parameter details, and return types for `HuggingFaceChatModelProvider`
- **[Utility Functions API](#7.2)**: Function signatures, parameter validation rules, and transformation logic
- **[Type Definitions](#7.3)**: Complete TypeScript interface definitions and type aliases

---

