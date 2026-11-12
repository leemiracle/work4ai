<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/poml · extra page Language Server Features · fetched 2026-10-26 -->

# Language Server Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [eslint.config.js](eslint.config.js)
- [packages/poml-vscode/lsp/server.ts](packages/poml-vscode/lsp/server.ts)
- [packages/poml-vscode/panel/content.tsx](packages/poml-vscode/panel/content.tsx)
- [packages/poml-vscode/panel/panel.ts](packages/poml-vscode/panel/panel.ts)
- [packages/poml-vscode/panel/types.ts](packages/poml-vscode/panel/types.ts)
- [packages/poml/util/xmlContentAssist.js](packages/poml/util/xmlContentAssist.js)

</details>



This document covers the Language Server Protocol (LSP) features provided by the POML VS Code extension, including diagnostics, code completion, hover documentation, and interactive debugging capabilities.

For information about the preview and testing interface, see [Preview and Testing](#5.3.2). For details about the prompt gallery and chat functionality, see [Prompt Gallery and Chat](#5.3.3).

## Overview

The POML Language Server provides comprehensive language support through the VS Code Language Server Protocol, enabling real-time error detection, intelligent code completion, contextual documentation, and interactive expression evaluation for `.poml` files.

## Architecture

The LSP implementation centers around the `PomlLspServer` class, which handles all language service requests and integrates with the core POML processing engine.

```mermaid
graph TB
    subgraph "VS Code Client"
        EDITOR["Text Editor"]
        DIAG_UI["Diagnostic UI"]
        HOVER_UI["Hover Popup"]
        COMPLETION_UI["Completion List"]
        CODELENS_UI["Code Lenses"]
    end
    
    subgraph "Language Client"
        LSP_CLIENT["LanguageClient"]
        CLIENT_OPTIONS["LanguageClientOptions"]
    end
    
    subgraph "Language Server Process"
        LSP_SERVER["PomlLspServer"]
        CONNECTION["createConnection"]
        TEXT_DOCS["TextDocuments"]
    end
    
    subgraph "LSP Capabilities"
        DIAGNOSTICS["onDiagnostic"]
        HOVER["onHover"] 
        COMPLETION["onCompletion"]
        CODELENS["onCodeLens"]
        EXECUTE_CMD["onExecuteCommand"]
        PREVIEW["onPreview"]
    end
    
    subgraph "POML Core Integration"
        POML_FILE["PomlFile"]
        READ_ENGINE["read()"]
        WRITE_ENGINE["writeWithSourceMap()"]
        ERROR_COLLECTION["ErrorCollection"]
    end
    
    subgraph "Caching & Performance"
        COMPUTATION_CACHE["ComputationCache"]
        DIAGNOSTIC_CACHE["DiagnosticCache"] 
        ENCODING_CACHE["EncodingCache"]
        THROTTLING["Request Throttling"]
    end
    
    %% Client connections
    EDITOR --> LSP_CLIENT
    LSP_CLIENT --> CONNECTION
    CONNECTION --> LSP_SERVER
    LSP_SERVER --> TEXT_DOCS
    
    %% Capability connections  
    LSP_SERVER --> DIAGNOSTICS
    LSP_SERVER --> HOVER
    LSP_SERVER --> COMPLETION
    LSP_SERVER --> CODELENS
    LSP_SERVER --> EXECUTE_CMD
    LSP_SERVER --> PREVIEW
    
    %% Core integration
    DIAGNOSTICS --> POML_FILE
    HOVER --> POML_FILE
    COMPLETION --> POML_FILE
    CODELENS --> POML_FILE
    PREVIEW --> READ_ENGINE
    PREVIEW --> WRITE_ENGINE
    DIAGNOSTICS --> ERROR_COLLECTION
    
    %% Performance systems
    LSP_SERVER --> COMPUTATION_CACHE
    LSP_SERVER --> DIAGNOSTIC_CACHE
    LSP_SERVER --> ENCODING_CACHE
    LSP_SERVER --> THROTTLING
    
    %% UI feedback
    DIAGNOSTICS --> DIAG_UI
    HOVER --> HOVER_UI
    COMPLETION --> COMPLETION_UI
    CODELENS --> CODELENS_UI
```

Sources: [packages/poml-vscode/lsp/server.ts:1-837](), [packages/poml-vscode/extension.ts:76-112]()

## Server Initialization

The LSP server is initialized through the VS Code extension activation process, creating a separate Node.js process for language services.

```mermaid
graph LR
    subgraph "Extension Activation"
        ACTIVATE["activate()"]
        ACTIVATE_CLIENT["activateClient()"]
    end
    
    subgraph "Server Setup"
        SERVER_MODULE["dist/server.js"]
        SERVER_OPTIONS["ServerOptions"]
        CLIENT_OPTIONS["LanguageClientOptions"]
        LANGUAGE_CLIENT["LanguageClient"]
    end
    
    subgraph "LSP Server Process"
        POML_LSP_SERVER["PomlLspServer"]
        CONNECTION_SETUP["createConnection()"]
        CAPABILITY_REGISTRATION["InitializeResult"]
    end
    
    ACTIVATE --> ACTIVATE_CLIENT
    ACTIVATE_CLIENT --> SERVER_MODULE
    ACTIVATE_CLIENT --> SERVER_OPTIONS
    ACTIVATE_CLIENT --> CLIENT_OPTIONS
    SERVER_OPTIONS --> LANGUAGE_CLIENT
    CLIENT_OPTIONS --> LANGUAGE_CLIENT
    
    LANGUAGE_CLIENT --> POML_LSP_SERVER
    POML_LSP_SERVER --> CONNECTION_SETUP
    POML_LSP_SERVER --> CAPABILITY_REGISTRATION
```

### Supported Capabilities

The server registers the following LSP capabilities during initialization:

| Capability | Feature | Implementation Method |
|------------|---------|---------------------|
| `textDocumentSync` | Incremental document sync | `TextDocumentSyncKind.Incremental` |
| `completionProvider` | Code completion with resolve | `onCompletion`, `onCompletionResolve` |
| `diagnosticProvider` | Pull-based diagnostics | `onDiagnostic` |
| `hoverProvider` | Hover documentation | `onHover` |
| `codeLensProvider` | Interactive code lenses | `onCodeLens` |
| `executeCommandProvider` | Command execution | `onExecuteCommand` |

Sources: [packages/poml-vscode/lsp/server.ts:151-165](), [packages/poml-vscode/extension.ts:84-104]()

## Diagnostic System

The diagnostic system provides real-time error detection and reporting for POML files through a pull-based diagnostic model with caching optimization.

```mermaid
graph TB
    subgraph "Diagnostic Request Flow"
        CLIENT_REQUEST["Diagnostic Request"]
        DOCUMENT_PARAMS["DocumentDiagnosticParams"]
        CACHE_CHECK["DiagnosticCache Check"]
    end
    
    subgraph "Cache Management"
        CACHE_HIT["Unchanged Report"]
        CACHE_MISS["Validate Document"]
        CACHE_UPDATE["Update Cache"]
    end
    
    subgraph "Validation Process"
        GET_OPTIONS["getAssociatedOptions()"]
        PREVIEW_REQUEST["onPreview() with returnAllErrors"]
        ERROR_PROCESSING["Process Error Types"]
    end
    
    subgraph "Error Types"
        READ_ERROR["ReadError"]
        WRITE_ERROR["WriteError"] 
        SYSTEM_ERROR["SystemError"]
        UNKNOWN_ERROR["Unknown Error"]
    end
    
    subgraph "Diagnostic Output"
        DIAGNOSTIC_ITEMS["Diagnostic[]"]
        SEVERITY_MAPPING["Severity Mapping"]
        RELATED_INFO["Related Information"]
    end
    
    CLIENT_REQUEST --> DOCUMENT_PARAMS
    DOCUMENT_PARAMS --> CACHE_CHECK
    CACHE_CHECK --> CACHE_HIT
    CACHE_CHECK --> CACHE_MISS
    
    CACHE_MISS --> VALIDATE_DOCUMENT["validateTextDocument()"]
    VALIDATE_DOCUMENT --> GET_OPTIONS
    GET_OPTIONS --> PREVIEW_REQUEST
    PREVIEW_REQUEST --> ERROR_PROCESSING
    
    ERROR_PROCESSING --> READ_ERROR
    ERROR_PROCESSING --> WRITE_ERROR
    ERROR_PROCESSING --> SYSTEM_ERROR
    ERROR_PROCESSING --> UNKNOWN_ERROR
    
    READ_ERROR --> DIAGNOSTIC_ITEMS
    WRITE_ERROR --> DIAGNOSTIC_ITEMS  
    SYSTEM_ERROR --> DIAGNOSTIC_ITEMS
    UNKNOWN_ERROR --> DIAGNOSTIC_ITEMS
    
    DIAGNOSTIC_ITEMS --> SEVERITY_MAPPING
    DIAGNOSTIC_ITEMS --> RELATED_INFO
    DIAGNOSTIC_ITEMS --> CACHE_UPDATE
```

### Error Type Mapping

The diagnostic system maps POML errors to LSP diagnostic severities:

| Error Type | LSP Severity | Source Label |
|------------|-------------|--------------|
| `ReadError` | Warning | "POML Reader" |
| `WriteError` | Warning | "POML Writer" | 
| `SystemError` | Error | "POML System (please report)" |
| Unknown/String | Error | "POML Unknown Error (please report)" |

Sources: [packages/poml-vscode/lsp/server.ts:497-687](), [packages/poml-vscode/lsp/server.ts:601-677]()

## Hover Documentation

The hover system provides contextual documentation for POML components and their parameters by analyzing the cursor position and querying the component registry.

### Hover Token Resolution

```mermaid
graph LR
    subgraph "Hover Request"
        HOVER_PARAMS["HoverParams"]
        CURSOR_POSITION["position"]
        TEXT_OFFSET["offsetAt()"]
    end
    
    subgraph "Token Analysis"
        POML_FILE["new PomlFile()"]
        GET_HOVER_TOKEN["getHoverToken()"]
        HOVER_TOKEN["PomlToken"]
    end
    
    subgraph "Documentation Query"
        TOKEN_TYPE_CHECK["token.type check"]
        COMPONENT_DOC["queryDocumentationForComponent()"]
        PARAMETER_DOC["queryDocumentationForParameter()"]
    end
    
    subgraph "Component Registry"
        FIND_COMPONENT["findComponentByAlias()"]
        COMPONENT_SPEC["component.spec()"]
        FORMAT_DOC["formatComponentDocumentation()"]
        FORMAT_PARAM["formatParameterDocumentation()"]
    end
    
    HOVER_PARAMS --> CURSOR_POSITION
    CURSOR_POSITION --> TEXT_OFFSET
    TEXT_OFFSET --> POML_FILE
    POML_FILE --> GET_HOVER_TOKEN
    GET_HOVER_TOKEN --> HOVER_TOKEN
    
    HOVER_TOKEN --> TOKEN_TYPE_CHECK
    TOKEN_TYPE_CHECK --> COMPONENT_DOC
    TOKEN_TYPE_CHECK --> PARAMETER_DOC
    
    COMPONENT_DOC --> FIND_COMPONENT
    PARAMETER_DOC --> FIND_COMPONENT
    FIND_COMPONENT --> COMPONENT_SPEC
    COMPONENT_SPEC --> FORMAT_DOC
    COMPONENT_SPEC --> FORMAT_PARAM
```

The hover response includes:
- Markdown-formatted documentation content
- Source range highlighting  
- Component or parameter-specific information

Sources: [packages/poml-vscode/lsp/server.ts:689-751](), [packages/poml-vscode/lsp/documentFormatter.ts]()

## Code Completion

The completion system provides intelligent suggestions for POML components, attributes, and values based on cursor context and component definitions.

### Completion Flow

```mermaid
graph TB
    subgraph "Completion Request"
        COMPLETION_PARAMS["TextDocumentPositionParams"]
        CURSOR_OFFSET["offsetAt(position)"]
        GET_COMPLETIONS["pomlFile.getCompletions()"]
    end
    
    subgraph "Suggestion Types"
        ELEMENT_SUGGESTION["Element Suggestions"]
        ATTRIBUTE_SUGGESTION["Attribute Suggestions"] 
        VALUE_SUGGESTION["Value Suggestions"]
    end
    
    subgraph "Completion Items"
        COMPLETION_ITEM["CompletionItem"]
        ITEM_KIND["CompletionItemKind"]
        TEXT_EDIT["TextEdit"]
        TELEMETRY_CMD["Telemetry Command"]
    end
    
    subgraph "Resolution Process"
        COMPLETION_RESOLVE["onCompletionResolve()"]
        DETAIL_INFO["item.detail"]
        DOCUMENTATION["item.documentation"]
        QUERY_DOC["Query Documentation"]
    end
    
    COMPLETION_PARAMS --> CURSOR_OFFSET
    CURSOR_OFFSET --> GET_COMPLETIONS
    GET_COMPLETIONS --> ELEMENT_SUGGESTION
    GET_COMPLETIONS --> ATTRIBUTE_SUGGESTION
    GET_COMPLETIONS --> VALUE_SUGGESTION
    
    ELEMENT_SUGGESTION --> COMPLETION_ITEM
    ATTRIBUTE_SUGGESTION --> COMPLETION_ITEM
    VALUE_SUGGESTION --> COMPLETION_ITEM
    
    COMPLETION_ITEM --> ITEM_KIND
    COMPLETION_ITEM --> TEXT_EDIT
    COMPLETION_ITEM --> TELEMETRY_CMD
    
    COMPLETION_ITEM --> COMPLETION_RESOLVE
    COMPLETION_RESOLVE --> DETAIL_INFO
    COMPLETION_RESOLVE --> DOCUMENTATION
    COMPLETION_RESOLVE --> QUERY_DOC
```

### Completion Item Types

| Suggestion Type | VSCode Kind | Label Source | Documentation Source |
|----------------|-------------|--------------|---------------------|
| Element | `CompletionItemKind.Class` | `suggestion.element` | Component spec |
| Attribute | `CompletionItemKind.Property` | `suggestion.attribute` | Parameter spec |
| Attribute Value | `CompletionItemKind.Value` | `suggestion.value` | Parameter values |

Sources: [packages/poml-vscode/lsp/server.ts:753-832]()

## Code Lenses and Expression Evaluation

Code lenses provide interactive "Evaluate" buttons for expressions within POML files, enabling real-time expression evaluation without running the full pipeline. Results are displayed in a dedicated output channel.

### Code Lens Discovery and Execution Flow

```mermaid
graph TB
    subgraph "Code Lens Discovery"
        CODELENS_PARAMS["CodeLensParams"]
        POML_FILE["new PomlFile()"]
        GET_EXPRESSIONS["getExpressionTokens()"]
        EXPRESSION_TOKENS["PomlToken[]"]
    end
    
    subgraph "Lens Generation"
        TOKEN_FILTER["Filter Valid Expressions"]
        CREATE_COMMAND["Create Execute Command"]
        POSITION_MAPPING["Map to VSCode Range"]
        CODELENS_ARRAY["CodeLens[]"]
    end
    
    subgraph "Expression Evaluation"  
        EXECUTE_COMMAND["onExecuteCommand()"]
        EVALUATE_EXPR["poml.evaluateExpression"]
        FILE_PARSING["Parse File with Context"]
        EXPRESSION_EVAL["getExpressionEvaluations()"]
    end
    
    subgraph "Result Notification"
        EVALUATION_MESSAGE["EvaluationMessage"]
        EVALUATION_NOTIFICATION["EvaluationNotification"]
        OUTPUT_CHANNEL["POML Debug Channel"]
    end
    
    CODELENS_PARAMS --> POML_FILE
    POML_FILE --> GET_EXPRESSIONS
    GET_EXPRESSIONS --> EXPRESSION_TOKENS
    
    EXPRESSION_TOKENS --> TOKEN_FILTER
    TOKEN_FILTER --> CREATE_COMMAND
    CREATE_COMMAND --> POSITION_MAPPING
    POSITION_MAPPING --> CODELENS_ARRAY
    
    CREATE_COMMAND --> EXECUTE_COMMAND
    EXECUTE_COMMAND --> EVALUATE_EXPR
    EVALUATE_EXPR --> FILE_PARSING
    FILE_PARSING --> EXPRESSION_EVAL
    
    EXPRESSION_EVAL --> EVALUATION_MESSAGE
    EVALUATION_MESSAGE --> EVALUATION_NOTIFICATION
    EVALUATION_NOTIFICATION --> OUTPUT_CHANNEL
```

### Expression Evaluation Details

The evaluation system handles multiple expressions and provides detailed feedback:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| Command Structure | `poml.evaluateExpression` | `[uri, text, rangeStart, rangeEnd]` |
| Expression Discovery | Token parsing | `pomlFile.getExpressionTokens()` |
| Context Integration | File context loading | `getAssociatedOptions()` context files |
| Result Processing | Multiple evaluations | Truncated at 1024 chars per result |
| Notification System | Real-time feedback | `EvaluationNotification` to client |

The evaluation message types include:
- **Info**: Successful evaluation results
- **Warning**: No evaluations found for expression
- **Error**: Parsing or evaluation errors

Sources: [packages/poml-vscode/lsp/server.ts:213-323](), [packages/poml-vscode/extension.ts:117-123](), [packages/poml-vscode/panel/types.ts:74-79]()

## Preview Integration

The LSP server provides a custom `poml/preview` method that integrates with the webview panel system for real-time document rendering and token counting.

### Preview Request Processing

```mermaid
graph TB
    subgraph "Preview Request"
        PREVIEW_PARAMS["PreviewParams"]
        REQUEST_THROTTLING["Throttle Management"]
        CACHE_CHECK["Computation Cache"]
    end
    
    subgraph "Document Processing"
        GET_TEXT["Get Document Text"]
        LOAD_CONTEXT["Load Context Files"]
        LOAD_STYLESHEET["Load Stylesheet Files"]
        READ_STEP["read() Processing"]
    end
    
    subgraph "Output Generation"
        SPEAKER_MODE_CHECK["speakerMode check"]
        WRITE_WITH_SOURCEMAP["writeWithSourceMap()"]
        RICH_CONTENT["RichContent Generation"]
        TOKEN_COUNTING["Token Count Calculation"]
    end
    
    subgraph "Response Assembly"
        PREVIEW_RESPONSE["PreviewResponse"]
        ERROR_HANDLING["Error Collection"]
        TELEMETRY["Usage Telemetry"]
        CACHE_UPDATE["Update Cache"]
    end
    
    PREVIEW_PARAMS --> REQUEST_THROTTLING
    REQUEST_THROTTLING --> CACHE_CHECK
    CACHE_CHECK --> GET_TEXT
    
    GET_TEXT --> LOAD_CONTEXT
    LOAD_CONTEXT --> LOAD_STYLESHEET  
    LOAD_STYLESHEET --> READ_STEP
    
    READ_STEP --> SPEAKER_MODE_CHECK
    SPEAKER_MODE_CHECK --> WRITE_WITH_SOURCEMAP
    WRITE_WITH_SOURCEMAP --> RICH_CONTENT
    RICH_CONTENT --> TOKEN_COUNTING
    
    TOKEN_COUNTING --> PREVIEW_RESPONSE
    PREVIEW_RESPONSE --> ERROR_HANDLING
    ERROR_HANDLING --> TELEMETRY
    TELEMETRY --> CACHE_UPDATE
```

### Preview Response Structure

| Field | Type | Description |
|-------|------|-------------|
| `rawText` | `string` | Original document content |
| `ir` | `string` | Intermediate representation |
| `content` | `RichContent \| Message[]` | Rendered output |
| `error` | `string \| any[]` | Error information |
| `sourceMap` | `SourceMapRichContent[] \| SourceMapMessage[]` | Source mapping data |
| `tokens` | `{perMessage?: number[]; total: number}` | Token counts |

Sources: [packages/poml-vscode/lsp/server.ts:331-495](), [packages/poml-vscode/panel/types.ts:53-71]()

## Performance Optimization

The LSP server implements several performance optimization strategies to ensure responsive language services, including multi-layer caching, dynamic request throttling, and telemetry-driven optimization.

### Caching Strategy

```mermaid
graph TB
    subgraph "Cache Types"
        COMPUTATION_CACHE["ComputationCache<br/>Map<string, ComputationCache>"]
        DIAGNOSTIC_CACHE["DiagnosticCache<br/>Map<string, DiagnosticCache>"]
        ENCODING_CACHE["EncodingCache<br/>Map<string, Tiktoken>"]
        ASSOCIATED_OPTIONS["AssociatedOptions<br/>Map<string, WebviewUserOptions>"]
    end
    
    subgraph "Cache Keys and Data"
        REQUEST_KEY["JSON.stringify(params)"]
        FILE_URI["File URI"]
        CONTENT_HASH["SHA256 Content Hash"]
        MODEL_NAME["Model Name (gpt-4o, etc)"]
        FILE_CONTENT["fileContent"]
        LATEST_COMPUTED_TIME["latestComputedTime"]
    end
    
    subgraph "Performance Features"
        THROTTLING["Dynamic Request Throttling"]
        LAZY_COMPUTATION["Lazy Computation"]
        INCREMENTAL_SYNC["TextDocumentSyncKind.Incremental"]
        BUFFER_CLEARING["BufferCollection.clear()"]
    end
    
    subgraph "Cache Invalidation"
        DOCUMENT_SAVE["documents.onDidSave()"]
        DIAGNOSTIC_REFRESH["diagnostics.refresh()"]
        CACHE_DELETE["diagnosticCache.delete()"]
    end
    
    REQUEST_KEY --> COMPUTATION_CACHE
    FILE_URI --> DIAGNOSTIC_CACHE
    CONTENT_HASH --> DIAGNOSTIC_CACHE
    MODEL_NAME --> ENCODING_CACHE
    FILE_URI --> ASSOCIATED_OPTIONS
    
    FILE_CONTENT --> DIAGNOSTIC_CACHE
    LATEST_COMPUTED_TIME --> COMPUTATION_CACHE
    
    COMPUTATION_CACHE --> THROTTLING
    DIAGNOSTIC_CACHE --> LAZY_COMPUTATION
    ENCODING_CACHE --> INCREMENTAL_SYNC
    ASSOCIATED_OPTIONS --> BUFFER_CLEARING
    
    DOCUMENT_SAVE --> DIAGNOSTIC_REFRESH
    DIAGNOSTIC_REFRESH --> CACHE_DELETE
    CACHE_DELETE --> BUFFER_CLEARING
```

### Dynamic Throttling Algorithm

The server implements adaptive throttling based on real-time computation performance:

| Parameter | Initial Value | Update Formula | Constraints |
|-----------|---------------|----------------|-------------|
| `throttleTime` | 10ms | `throttleTime * 0.9 + allocatedTime * 0.1` | 10ms - 1000ms |
| `allocatedTime` | N/A | `elapsed * 2` | Double actual time |
| Cache check | N/A | `requestedTime < latestComputedTime` | Skip if newer exists |

### Token Counting Optimization

The encoding cache optimizes token counting for different language models:

```mermaid
graph LR
    subgraph "Model Support"
        MODEL_REQUEST["Token Count Request"]
        MODEL_LOOKUP["encodingCache.get()"]
        ENCODING_FOR_MODEL["encodingForModel()"]
        TIKTOKEN_ENCODING["Tiktoken"]
    end
    
    subgraph "Content Processing"
        RICH_CONTENT["RichContent"]
        STRING_CONTENT["String Content"]
        IMAGE_CONTENT["ContentMultiMediaBinary"]
        STRUCTURED_CONTENT["JSON Serialized Content"]
    end
    
    subgraph "Token Calculation"
        ENCODE_TEXT["enc.encode()"]
        IMAGE_ESTIMATION["estimateImageTokens()"]
        IMAGE_DIMENSIONS["getImageWidthHeight()"]
        TOTAL_TOKENS["Sum all tokens"]
    end
    
    MODEL_REQUEST --> MODEL_LOOKUP
    MODEL_LOOKUP --> ENCODING_FOR_MODEL
    ENCODING_FOR_MODEL --> TIKTOKEN_ENCODING
    
    RICH_CONTENT --> STRING_CONTENT
    RICH_CONTENT --> IMAGE_CONTENT
    RICH_CONTENT --> STRUCTURED_CONTENT
    
    STRING_CONTENT --> ENCODE_TEXT
    IMAGE_CONTENT --> IMAGE_DIMENSIONS
    IMAGE_DIMENSIONS --> IMAGE_ESTIMATION
    STRUCTURED_CONTENT --> ENCODE_TEXT
    
    ENCODE_TEXT --> TOTAL_TOKENS
    IMAGE_ESTIMATION --> TOTAL_TOKENS
```

Sources: [packages/poml-vscode/lsp/server.ts:78-113](), [packages/poml-vscode/lsp/server.ts:325-363](), [packages/poml-vscode/lsp/server.ts:486-534](), [packages/poml-vscode/lsp/server.ts:180-186]()

## Testing Infrastructure

The LSP server includes comprehensive testing through integration tests that verify all major language service features.

### Test Coverage

| Test Case | Verification | Method |
|-----------|--------------|--------|
| Diagnostics | Error detection for invalid files | `getDiagnostics()` |
| Clean Files | No diagnostics for valid files | Empty diagnostic array |
| Hover | Documentation display | `executeHoverProvider()` |
| Completion | Attribute suggestions | `executeCompletionItemProvider()` |
| Preview | Content generation | Custom LSP request |
| Expression Evaluation | Code lens execution | `executeCommand()` |

Sources: [packages/poml-vscode/tests/lsp.test.ts:1-131]()

---

