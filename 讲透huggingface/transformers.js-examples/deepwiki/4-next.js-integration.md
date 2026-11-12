<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/transformers.js-examples · page 4 Next.js Integration · fetched 2026-10-26 -->

# Next.js Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next-client/package-lock.json](next-client/package-lock.json)
- [next-client/package.json](next-client/package.json)
- [next-server/package-lock.json](next-server/package-lock.json)
- [next-server/package.json](next-server/package.json)
- [next-vercel-ai-sdk-v5/README.md](next-vercel-ai-sdk-v5/README.md)
- [next-vercel-ai-sdk-v5/package-lock.json](next-vercel-ai-sdk-v5/package-lock.json)
- [next-vercel-ai-sdk-v5/package.json](next-vercel-ai-sdk-v5/package.json)
- [next-vercel-ai-sdk-v5/src/app/chat-transport.ts](next-vercel-ai-sdk-v5/src/app/chat-transport.ts)
- [next-vercel-ai-sdk-v5/src/app/models.ts](next-vercel-ai-sdk-v5/src/app/models.ts)
- [next-vercel-ai-sdk-v5/src/app/page.tsx](next-vercel-ai-sdk-v5/src/app/page.tsx)
- [next-vercel-ai-sdk-v5/src/app/simple-chat-transport.ts](next-vercel-ai-sdk-v5/src/app/simple-chat-transport.ts)
- [next-vercel-ai-sdk-v5/src/app/worker.ts](next-vercel-ai-sdk-v5/src/app/worker.ts)
- [next-vercel-ai-sdk-v5/src/store/store.ts](next-vercel-ai-sdk-v5/src/store/store.ts)

</details>



## Purpose and Scope

This document provides an overview of the Next.js integration patterns available in the transformers.js-examples repository. It covers the architectural approaches for integrating `@huggingface/transformers` with Next.js applications, including server-side inference, client-side inference, and Vercel AI SDK integration patterns.

For detailed implementation of server-side inference using API routes, see [Server-Side Inference](#4.1). For browser-based model execution within Next.js, see [Client-Side Inference](#4.2). For comprehensive integration with Vercel AI SDK including chat interfaces and streaming, see [Vercel AI SDK Integration](#4.3).

---

## Integration Patterns Overview

The repository demonstrates three distinct approaches to integrating Transformers.js with Next.js applications, each optimized for different use cases and deployment scenarios.

### Pattern Comparison

| Pattern | Runtime | ONNX Backend | Use Case | Model Storage |
|---------|---------|--------------|----------|---------------|
| Server-Side | Node.js server | onnxruntime-node | API endpoints, batch processing | Server filesystem (~/.cache/huggingface) |
| Client-Side | Browser | onnxruntime-web | Privacy-focused, offline-capable | Browser IndexedDB |
| AI SDK Hybrid | Both | Both (configurable) | Rich chat UIs, streaming responses | Configurable per model |

**Integration Pattern Architecture**

```mermaid
graph TB
    subgraph NextServer["next-server"]
        NS_Route["app/api/classify/route.ts"]
        NS_Pipeline["pipeline()"]
        NS_ONNX["onnxruntime-node"]
        
        NS_Route --> NS_Pipeline
        NS_Pipeline --> NS_ONNX
    end
    
    subgraph NextClient["next-client"]
        NC_Component["Client Component"]
        NC_Pipeline["pipeline()"]
        NC_ONNX["onnxruntime-web"]
        
        NC_Component --> NC_Pipeline
        NC_Pipeline --> NC_ONNX
    end
    
    subgraph NextAISDK["next-vercel-ai-sdk-v5"]
        AI_Page["app/page.tsx"]
        AI_useChat["useChat hook"]
        AI_Transport["TransformersChatTransport"]
        AI_Store["useModelStore"]
        AI_Model["TransformersJSLanguageModel"]
        AI_Worker["worker.ts"]
        
        AI_Page --> AI_useChat
        AI_useChat --> AI_Transport
        AI_Transport --> AI_Store
        AI_Store --> AI_Model
        AI_Model --> AI_Worker
    end
    
    Browser["Browser Client"] --> NC_Component
    Browser --> AI_Page
    Browser -.HTTP API.-> NS_Route
    
    style NextServer fill:#f5f5f5,stroke:#333,stroke-width:2px
    style NextClient fill:#f5f5f5,stroke:#333,stroke-width:2px
    style NextAISDK fill:#f5f5f5,stroke:#333,stroke-width:2px
```

Sources: [next-server/package.json:1-25](), [next-client/package.json:1-25](), [next-vercel-ai-sdk-v5/package.json:1-59]()

---

## Shared Dependencies

All Next.js examples share the core `@huggingface/transformers` library but differ in their runtime backends and additional dependencies:

### Core Dependencies

- **@huggingface/transformers**: Version 3.7.1-3.8.1 across examples
- **next**: Version ^15.2.4 to 15.4.6
- **react**: Version ^19.0.0 to 19.1.0
- **react-dom**: Matches React version

### Runtime-Specific Backend Selection

The `@huggingface/transformers` library automatically selects the appropriate ONNX Runtime backend based on the execution environment:

```mermaid
graph LR
    Transformers["@huggingface/transformers"]
    
    subgraph ServerEnv["Server Environment"]
        ONNXNode["onnxruntime-node<br/>v1.21.0"]
        Native["Native Bindings<br/>Platform-specific"]
    end
    
    subgraph BrowserEnv["Browser Environment"]
        ONNXWeb["onnxruntime-web<br/>v1.22.0-dev"]
        WebGPU["WebGPU API"]
        WASM["WebAssembly"]
    end
    
    Transformers --> ONNXNode
    Transformers --> ONNXWeb
    
    ONNXNode --> Native
    ONNXWeb --> WebGPU
    ONNXWeb --> WASM
    
    style Transformers fill:#f9f9f9,stroke:#333,stroke-width:3px
```

Sources: [next-server/package-lock.json:179-190](), [next-vercel-ai-sdk-v5/package-lock.json:358-370]()

---

## Vercel AI SDK Integration Architecture

The `next-vercel-ai-sdk-v5` example demonstrates the most sophisticated integration pattern, bridging Transformers.js with the Vercel AI SDK through a custom transport layer.

### Custom ChatTransport Implementation

The `TransformersChatTransport` class implements the `ChatTransport` interface to enable Vercel AI SDK's `useChat` hook to work with Transformers.js models running in the browser.

**ChatTransport Data Flow**

```mermaid
sequenceDiagram
    participant Page as "page.tsx"
    participant useChat as "useChat hook"
    participant Transport as "TransformersChatTransport"
    participant Store as "useModelStore"
    participant Model as "TransformersJSLanguageModel"
    participant Worker as "Web Worker"
    
    Page->>useChat: sendMessage(text, files)
    useChat->>Transport: sendMessages(options)
    Transport->>Store: getModelInstance()
    
    alt Model not cached
        Store->>Model: transformersJS(modelId, config)
        Model->>Worker: initialize worker
        Worker-->>Model: worker ready
        Store-->>Transport: model instance
        Transport->>Model: createSessionWithProgress(callback)
        loop Download progress
            Model-->>Transport: progress updates
            Transport-->>useChat: UIMessageChunk (progress)
            useChat-->>Page: render progress
        end
    else Model cached
        Store-->>Transport: cached instance
    end
    
    Transport->>Model: streamText(messages)
    loop Token generation
        Model-->>Transport: text chunks
        Transport-->>useChat: UIMessageChunk (text-delta)
        useChat-->>Page: render streaming text
    end
```

Sources: [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:1-162](), [next-vercel-ai-sdk-v5/src/app/page.tsx:54-58]()

### Key Components and Their Roles

**TransformersChatTransport Class Structure**

```mermaid
classDiagram
    class ChatTransport {
        <<interface>>
        +sendMessages(options)
        +reconnectToStream(options)
    }
    
    class TransformersChatTransport {
        -getModel() Promise~TransformersJSLanguageModel~
        +sendMessages(options) Promise~ReadableStream~
        +reconnectToStream(options) Promise~ReadableStream|null~
    }
    
    class useModelStore {
        +selectedModel: string
        +modelInstance: TransformersJSLanguageModel | null
        +setSelectedModel(modelId)
        +getModelInstance() Promise~TransformersJSLanguageModel~
        +clearModelInstance()
    }
    
    class TransformersJSLanguageModel {
        +availability() Promise~string~
        +createSessionWithProgress(callback)
        +streamText(messages)
    }
    
    class TransformersJSWorkerHandler {
        +onmessage(msg)
    }
    
    ChatTransport <|-- TransformersChatTransport
    TransformersChatTransport --> useModelStore : uses
    useModelStore --> TransformersJSLanguageModel : manages
    TransformersJSLanguageModel --> TransformersJSWorkerHandler : delegates to
```

Sources: [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:17-161](), [next-vercel-ai-sdk-v5/src/store/store.ts:1-74](), [next-vercel-ai-sdk-v5/src/app/worker.ts:1-7]()

### Model State Management with Zustand

The `useModelStore` provides centralized model instance management to avoid redundant downloads and initialization:

**State Management Flow**

```mermaid
stateDiagram-v2
    [*] --> NoModel: Initial State
    
    NoModel --> SelectingModel: setSelectedModel(modelId)
    SelectingModel --> Downloading: getModelInstance() called
    
    Downloading --> CheckAvailability: Check availability()
    
    CheckAvailability --> CachedModel: "available"
    CheckAvailability --> InitializeModel: "not-available"
    
    InitializeModel --> ConfigureWorker: supportsWorker=true
    InitializeModel --> DirectInit: supportsWorker=false
    
    ConfigureWorker --> CreateWorker: new Worker(worker.ts)
    CreateWorker --> InstantiateModel: transformersJS(modelId, config)
    DirectInit --> InstantiateModel
    
    InstantiateModel --> CachedModel: Store instance
    
    CachedModel --> [*]: Model ready for inference
    
    CachedModel --> NoModel: clearModelInstance() or<br/>setSelectedModel(different model)
```

Sources: [next-vercel-ai-sdk-v5/src/store/store.ts:8-73](), [next-vercel-ai-sdk-v5/src/app/models.ts:1-51]()

### Progress Tracking During Model Downloads

The `TransformersChatTransport.sendMessages()` method implements granular progress tracking for model downloads, providing real-time feedback to the user:

**Progress Tracking Implementation**

```mermaid
graph TB
    SendMessages["sendMessages()"]
    CheckAvail["availability() check"]
    
    subgraph ProgressTracking["Progress Tracking Path"]
        CreateStream["createUIMessageStream()"]
        ProgressCallback["createSessionWithProgress(callback)"]
        FirstUpdate["Write initial progress<br/>data-modelDownloadProgress"]
        Updates["Write progress updates<br/>with percentage"]
        Complete["Write completion message"]
    end
    
    subgraph DirectPath["Direct Inference Path"]
        StreamText["streamText()"]
        UIStream["toUIMessageStream()"]
    end
    
    SendMessages --> CheckAvail
    CheckAvail -->|"available"| StreamText
    CheckAvail -->|"not-available"| CreateStream
    
    CreateStream --> ProgressCallback
    ProgressCallback --> FirstUpdate
    FirstUpdate --> Updates
    Updates --> Complete
    Complete --> StreamText
    
    StreamText --> UIStream
    
    style ProgressTracking fill:#f5f5f5,stroke:#333,stroke-width:2px
    style DirectPath fill:#f5f5f5,stroke:#333,stroke-width:2px
```

Sources: [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:38-52](), [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:54-151]()

The progress callback writes custom `data-modelDownloadProgress` message parts with the following structure:

```typescript
{
  type: "data-modelDownloadProgress",
  id: string,
  data: {
    status: "downloading" | "complete",
    progress: number,  // 0-100
    message: string
  }
}
```

Sources: [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:72-96]()

### Message Part Types and Rendering

The AI SDK integration handles multiple message part types, rendered conditionally in the UI:

| Part Type | Purpose | Rendering Location |
|-----------|---------|-------------------|
| `text` | Standard text content | `<Response>` component |
| `reasoning` | Model reasoning (e.g., DeepSeek) | `<Reasoning>` collapsible |
| `file` | Uploaded images | Image preview |
| `data-modelDownloadProgress` | Download progress | Progress bar |

Sources: [next-vercel-ai-sdk-v5/src/app/page.tsx:157-214]()

### Web Worker Configuration

Models can optionally use Web Workers for inference, configured per model in the `MODELS` array:

```typescript
// From models.ts
{
  id: "HuggingFaceTB/SmolLM2-360M-Instruct",
  name: "SmolLM2 360M",
  device: "webgpu",
  dtype: "q4",
  supportsWorker: true,  // Enable worker for this model
}
```

The store conditionally creates the worker based on `supportsWorker`:

```typescript
const workerConfig = modelConfig.supportsWorker
  ? {
      worker: new Worker(new URL("../app/worker.ts", import.meta.url), {
        type: "module",
      }),
    }
  : {};
```

Sources: [next-vercel-ai-sdk-v5/src/app/models.ts:9-51](), [next-vercel-ai-sdk-v5/src/store/store.ts:47-54]()

---

## Simplified ChatTransport Alternative

The repository includes a simplified version of the ChatTransport without progress tracking in `simple-chat-transport.ts`. This version is useful for understanding the minimal requirements:

**Comparison: Full vs Simplified Transport**

```mermaid
graph LR
    subgraph SimpleChatTransport["SimpleChatTransport"]
        S1["sendMessages()"]
        S2["getModel()"]
        S3["streamText()"]
        S4["toUIMessageStream()"]
        
        S1 --> S2
        S2 --> S3
        S3 --> S4
    end
    
    subgraph FullChatTransport["TransformersChatTransport"]
        F1["sendMessages()"]
        F2["availability() check"]
        F3A["Direct path"]
        F3B["Progress path"]
        F4["createSessionWithProgress()"]
        F5["progress callbacks"]
        F6["streamText()"]
        F7["toUIMessageStream()"]
        
        F1 --> F2
        F2 -->|cached| F3A
        F2 -->|not cached| F3B
        F3A --> F6
        F3B --> F4
        F4 --> F5
        F5 --> F6
        F6 --> F7
    end
    
    style SimpleChatTransport fill:#f5f5f5,stroke:#333,stroke-width:2px
    style FullChatTransport fill:#f5f5f5,stroke:#333,stroke-width:2px
```

Sources: [next-vercel-ai-sdk-v5/src/app/simple-chat-transport.ts:1-61](), [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:1-162]()

---

## Reasoning Extraction Middleware

The AI SDK integration uses `extractReasoningMiddleware` to parse and separate reasoning content from model output:

```typescript
wrapLanguageModel({
  model,
  middleware: extractReasoningMiddleware({
    tagName: "think",
  }),
})
```

This middleware extracts content within `<think>` tags from models like DeepSeek-R1, creating separate `reasoning` message parts that are rendered in a collapsible UI component.

Sources: [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:42-46](), [next-vercel-ai-sdk-v5/src/app/page.tsx:199-211]()

---

## Model Configuration System

The `MODELS` array in `models.ts` defines available models and their configurations:

**Model Configuration Structure**

```mermaid
graph TB
    MODELS["MODELS array"]
    
    subgraph ModelConfig["ModelConfig Interface"]
        id["id: string<br/>(Hugging Face model ID)"]
        name["name: string<br/>(Display name)"]
        device["device?: 'webgpu' | 'wasm'"]
        dtype["dtype?: 'q4' | 'q4f16' | 'fp32'"]
        isVision["isVisionModel?: boolean"]
        supportsWorker["supportsWorker?: boolean"]
    end
    
    subgraph ExampleConfigs["Example Configurations"]
        SmolLM["SmolLM2-360M-Instruct<br/>device: webgpu<br/>dtype: q4<br/>supportsWorker: true"]
        Gemma["gemma-3-270m-it-ONNX<br/>dtype: fp32<br/>supportsWorker: false"]
        SmolVLM["SmolVLM-256M-Instruct<br/>device: webgpu<br/>dtype: fp32<br/>isVisionModel: true"]
    end
    
    MODELS --> ModelConfig
    ModelConfig --> ExampleConfigs
    
    style ModelConfig fill:#f5f5f5,stroke:#333,stroke-width:2px
    style ExampleConfigs fill:#f5f5f5,stroke:#333,stroke-width:2px
```

Sources: [next-vercel-ai-sdk-v5/src/app/models.ts:3-51]()

The configuration controls:
- **device**: Hardware acceleration preference (WebGPU vs WebAssembly)
- **dtype**: Model quantization level affecting size and performance
- **isVisionModel**: Enables image input processing
- **supportsWorker**: Determines whether to offload to Web Worker

---

## UI Component Integration

The main page component demonstrates comprehensive integration with the AI SDK:

**Component Hierarchy and Data Flow**

```mermaid
graph TB
    Page["page.tsx<br/>ChatBotDemo component"]
    
    subgraph Hooks["React Hooks"]
        UseChat["useChat()<br/>messages, sendMessage, status"]
        UseModelStore["useModelStore()<br/>selectedModel, setSelectedModel"]
    end
    
    subgraph UIComponents["UI Component Tree"]
        Conversation["<Conversation>"]
        Message["<Message>"]
        MessageContent["<MessageContent>"]
        Response["<Response>"]
        Reasoning["<Reasoning>"]
        PromptInput["<PromptInput>"]
        ModelSelect["<PromptInputModelSelect>"]
        Progress["<Progress>"]
    end
    
    Page --> UseChat
    Page --> UseModelStore
    
    UseChat --> Conversation
    Conversation --> Message
    Message --> MessageContent
    MessageContent --> Response
    MessageContent --> Reasoning
    MessageContent --> Progress
    
    Page --> PromptInput
    PromptInput --> ModelSelect
    
    UseModelStore --> ModelSelect
    
    style Hooks fill:#f5f5f5,stroke:#333,stroke-width:2px
    style UIComponents fill:#f5f5f5,stroke:#333,stroke-width:2px
```

Sources: [next-vercel-ai-sdk-v5/src/app/page.tsx:48-360]()

### Key Event Handlers

| Handler | Purpose | Implementation |
|---------|---------|----------------|
| `handleSubmit` | Send message with text/files | [page.tsx:60-74]() |
| `handleFileChange` | Process image uploads | [page.tsx:76-80]() |
| `removeImage` | Remove uploaded image | [page.tsx:82-96]() |
| `handleSuggestionClick` | Click suggestion chip | [page.tsx:98-100]() |
| `copyMessageToClipboard` | Copy assistant response | [page.tsx:102-109]() |

---

## Build Configuration and Deployment

### Standalone Build Mode

Next.js 15 standalone mode creates self-contained builds suitable for containerized deployments:

```json
// next.config.js configuration (inferred from build output)
{
  "output": "standalone"
}
```

The standalone build includes:
- All dependencies bundled
- Node.js server files
- Static assets
- Optimized for Docker/container deployment

Sources: [next-server/package-lock.json:1-25]() (implied by Next.js 15.2.4 capabilities)

### Development vs Production

| Mode | Command | Features |
|------|---------|----------|
| Development | `npm run dev --turbopack` | Fast refresh, Turbopack bundler, source maps |
| Production | `npm run build && npm run start` | Optimized bundles, tree shaking, minification |

Sources: [next-server/package.json:5-9](), [next-vercel-ai-sdk-v5/package.json:5-9]()

---

## Cross-Cutting Concerns

### Error Handling in ChatTransport

The transport implements try-catch error handling with custom notification message parts:

```typescript
catch (error) {
  writer.write({
    type: "data-notification",
    data: {
      message: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
      level: "error",
    },
    transient: true,
  });
  throw error;
}
```

Sources: [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:138-148]()

### Abort Signal Support

All transport implementations support request cancellation through AbortSignal:

```typescript
const result = streamText({
  model: wrapLanguageModel({ model, middleware }),
  messages: prompt,
  abortSignal: abortSignal,  // Passed from useChat hook
});
```

Sources: [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:39-50]()

### Model Caching Strategy

Models are cached at two levels:
1. **Store level**: In-memory `modelInstance` in Zustand store
2. **Browser level**: ONNX model files cached in IndexedDB by onnxruntime-web

The `availability()` check determines if a model needs downloading:

```typescript
const availability = await model.availability();
if (availability === "available") {
  // Skip progress tracking, model is ready
}
```

Sources: [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:38-52]()

---

## TypeScript Type Integration

### TransformersUIMessage Type

The AI SDK integration uses custom message types from `@browser-ai/transformers-js`:

```typescript
import { TransformersUIMessage } from "@browser-ai/transformers-js";

const { messages, sendMessage, status, stop, regenerate } =
  useChat<TransformersUIMessage>({
    transport: new TransformersChatTransport(),
    experimental_throttle: 75,
  });
```

This provides type safety for message parts including custom data types like `data-modelDownloadProgress`.

Sources: [next-vercel-ai-sdk-v5/src/app/page.tsx:32-58]()

### ChatRequestOptions Extension

The transport's `sendMessages` method signature extends `ChatRequestOptions` to support additional metadata:

```typescript
async sendMessages(
  options: {
    chatId: string;
    messages: TransformersUIMessage[];
    abortSignal: AbortSignal | undefined;
  } & {
    trigger: "submit-message" | "submit-tool-result" | "regenerate-message";
    messageId: string | undefined;
  } & ChatRequestOptions,
): Promise<ReadableStream<UIMessageChunk>>
```

Sources: [next-vercel-ai-sdk-v5/src/app/chat-transport.ts:22-31]()

---

## Performance Considerations

### Throttling Configuration

The `useChat` hook is configured with throttling to reduce render frequency during streaming:

```typescript
useChat<TransformersUIMessage>({
  transport: new TransformersChatTransport(),
  experimental_throttle: 75,  // 75ms between updates
});
```

This prevents excessive re-renders while maintaining responsive UI updates.

Sources: [next-vercel-ai-sdk-v5/src/app/page.tsx:54-58]()

### Worker vs Main Thread Execution

The decision to use Web Workers is model-specific:

- **Worker execution**: Better for larger models (>500MB), prevents UI blocking
- **Main thread**: Simpler for small models (<100MB), avoids worker overhead

The `supportsWorker` flag in model configuration controls this behavior.

Sources: [next-vercel-ai-sdk-v5/src/app/models.ts:9-51](), [next-vercel-ai-sdk-v5/src/store/store.ts:47-59]()

---

