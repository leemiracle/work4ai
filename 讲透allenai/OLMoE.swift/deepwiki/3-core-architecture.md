<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/OLMoE.swift · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [OLMoE.swift.xcodeproj/project.pbxproj](OLMoE.swift.xcodeproj/project.pbxproj)
- [OLMoE.swift.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved](OLMoE.swift.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved)
- [OLMoE.swift/Model/Context.swift](OLMoE.swift/Model/Context.swift)
- [OLMoE.swift/Model/InferenceMetrics.swift](OLMoE.swift/Model/InferenceMetrics.swift)
- [OLMoE.swift/Model/KeyboardResponder.swift](OLMoE.swift/Model/KeyboardResponder.swift)
- [OLMoE.swift/Model/LLM.swift](OLMoE.swift/Model/LLM.swift)
- [OLMoE.swift/Model/Template.swift](OLMoE.swift/Model/Template.swift)
- [OLMoE.swift/Views/ContentView.swift](OLMoE.swift/Views/ContentView.swift)

</details>



## Purpose and Scope

This document outlines the foundational architecture of OLMoE.swift, explaining the major components and their interactions that enable on-device language model inference. It covers the system's structural design, key abstractions, and component relationships. For details on specific implementation aspects, see [Language Model System](#3.1) and [User Interface Flow](#3.2).

## System Overview

OLMoE.swift is built on a modular architecture that centers around a language model inference engine integrated with a SwiftUI-based interface. The system efficiently runs the OLMoE language model directly on device without requiring cloud connectivity.

### High-Level Architecture

```mermaid
graph TD
    A["OLMoE_swiftApp"] --> B["ContentView"]
    B --> C["BotView"]
    B --> D["ModelDownloadView"]
    B --> E["DisclaimerPageView"]
    B --> F["UnsupportedDeviceView"]
    
    C --> G["Bot/LLM"]
    G --> H["Template"]
    G --> I["Context"]
    G --> J["InferenceMetrics"]
    
    G --> K["llama.cpp"]
    
    subgraph "Language Model System"
        G
        H
        I
        J
        K
    end
    
    subgraph "UI Components"
        C
        D
        E
        F
    end
```

The application's entry point initializes `ContentView`, which serves as the main coordinator that conditionally renders different views based on the application state: device compatibility, model availability, and disclaimer acceptance.

Sources:
- [OLMoE.swift/Views/ContentView.swift:391-524]()
- [OLMoE.swift/OLMoE_swiftApp.swift]()

## Core Components

### Language Model System

At the heart of OLMoE.swift is the language model system, built on these key components:

#### LLM Class

The `LLM` class is the foundation for language model operations, providing:
- Model loading and initialization
- Token generation and stream processing
- Conversation history management
- State persistence for continuous conversations

```mermaid
classDiagram
    class LLM {
        +model: "Model"
        +history: "[Chat]"
        +template: "Template?"
        +output: "String"
        +metrics: "InferenceMetrics"
        +respond(to: "String"): "async"
        +stop(): "void"
        +clearHistory(): "async"
        +saveState(): "Data?"
        +restoreState(from: "Data"): "void"
    }
    
    class Bot {
        +modelFileURL: "URL"
        +init()
    }
    
    class InferenceActor {
        +shared: "InferenceActor"
    }
    
    Bot --|> LLM : "extends"
    LLM -- InferenceActor : "uses"
```

The `LLM` class uses the `@InferenceActor` global actor to ensure thread safety during inference operations, preventing race conditions when generating text or updating model state.

Sources:
- [OLMoE.swift/Model/LLM.swift:27-489]()
- [OLMoE.swift/Views/ContentView.swift:12-34]()

#### Template System

The `Template` struct defines formatting for different model architectures:

```mermaid
classDiagram
    class Template {
        +system: "Attachment"
        +user: "Attachment"
        +bot: "Attachment"
        +systemPrompt: "String?"
        +stopSequence: "String?"
        +prefix: "String"
        +preprocess: "Closure"
        +static OLMoE(): "Template"
        +static chatML(): "Template"
        +static alpaca(): "Template"
        +static llama(): "Template"
    }
    
    class Attachment {
        +prefix: "String"
        +suffix: "String"
    }
```

This system provides standardized message formatting for different model architectures. The `preprocess` closure transforms raw inputs into properly formatted prompts, while maintaining conversation context.

Sources:
- [OLMoE.swift/Model/Template.swift:13-171]()

#### Context Management

The `Context` class manages the interface to the llama.cpp library:

```mermaid
classDiagram
    class Context {
        +pointer: "OpaquePointer"
        +init("Model", "llama_context_params")
        +decode("llama_batch")
        +deinit()
    }
```

This thin wrapper ensures proper memory management and provides a clean Swift interface to the underlying C/C++ code of llama.cpp.

Sources:
- [OLMoE.swift/Model/Context.swift:12-29]()

#### Inference Process

The inference process follows this sequence:

```mermaid
sequenceDiagram
    participant User
    participant BotView as "BotView"
    participant Bot as "Bot (LLM)"
    participant Template as "Template"
    participant Context as "Context"
    participant LlamaCpp as "llama.cpp"
    
    User->>BotView: "Send message"
    BotView->>Bot: "respond(to: input)"
    BotView->>BotView: "Add message to history"
    
    Bot->>Template: "preprocess(input, history)"
    Template->>Bot: "Return formatted prompt"
    
    Bot->>Context: "Create/restore context"
    Bot->>Bot: "Start metrics tracking"
    Bot->>Context: "tokenizeAndBatchInput"
    Context->>LlamaCpp: "Encode tokens"
    
    loop Token Generation
        Bot->>Context: "predictNextToken"
        Context->>LlamaCpp: "llama_sampler_sample"
        LlamaCpp->>Context: "Return token"
        Context->>Bot: "Decode token"
        Bot->>BotView: "Stream token to UI"
        BotView->>User: "Update display"
    end
    
    Bot->>Bot: "Update history"
    Bot->>Bot: "Save state (if enabled)"
```

This streaming architecture enables real-time display of generated text while maintaining responsiveness.

Sources:
- [OLMoE.swift/Model/LLM.swift:401-463]()

#### Performance Metrics

The `InferenceMetrics` struct tracks model performance:

```mermaid
classDiagram
    class InferenceMetrics {
        +inferenceTokenCount: "Int32"
        +inputTokenCount: "Int32"
        +totalTokens: "Int32"
        +startTime: "TimeInterval"
        +endTime: "TimeInterval"
        +inferenceTokensPerSecond: "Double"
        +start(): "void"
        +recordToken(): "void"
        +stop(): "void"
        +reset(): "void"
    }
```

This component collects real-time performance data about token processing speed and counts, helping users understand model performance on their device.

Sources:
- [OLMoE.swift/Model/InferenceMetrics.swift:10-51]()

### Application Flow

The application follows a structured flow from launch to interactive chat:

```mermaid
graph TD
    A["App Launch"] --> B{"Check Device<br/>Compatibility"}
    B -->|"Supported"| C{"Model<br/>Downloaded?"}
    B -->|"Not Supported"| D["UnsupportedDeviceView"]
    
    D -->|"Web Version"| D1["WebView"]
    D -->|"Override"| C
    D -->|"Mock Model"| C2["Initialize Mock Bot"]
    
    C -->|"Yes"| E{"First Launch?"}
    C -->|"No"| F["ModelDownloadView"]
    F -->|"Download<br/>Complete"| E
    
    E -->|"Yes"| G["DisclaimerPageView"]
    E -->|"No"| H["Initialize Bot"]
    G -->|"Accept"| H
    H --> I["Show BotView"]
    
    I --> J["User Interaction Loop"]
    
    subgraph "Chat Interaction"
        J -->|"Send"| K["Process Input"]
        K --> L["Generate Response"]
        L --> J
        J -->|"Clear"| M["Reset Conversation"]
        M --> J
        J -->|"Share"| N["Format for Sharing"]
        N --> J
    end
```

This flow ensures that:
1. Only compatible devices run the model
2. Necessary model files are downloaded
3. Users accept required disclaimers
4. The chat interface is only shown when all prerequisites are met

Sources:
- [OLMoE.swift/Views/ContentView.swift:391-524]()
- [OLMoE.swift/Views/ContentView.swift:504-523]()

### Content View Architecture

The `ContentView` serves as the application's main coordinator:

```mermaid
graph TD
    A["ContentView"] --> B["@StateObject downloadManager"]
    A --> C["@StateObject disclaimerState"]
    A --> D["@State bot"]
    A --> E["@State showMetrics"]
    
    A --> F{"isSupportedDevice?"}
    F -->|"No"| G["UnsupportedDeviceView"]
    F -->|"Yes"| H{"isModelReady?"}
    
    H -->|"Yes"| I["BotView"]
    H -->|"No"| J["ModelDownloadView"]
    
    I --> K["ChatView"]
    I --> L["MessageInputView"]
    I --> M["Toolbar Actions"]
    
    subgraph "State Management"
        B
        C
        D
        E
    end
```

The `ContentView` manages the application flow based on device compatibility and model availability. It coordinates the transition between different views and manages application-wide state.

Sources:
- [OLMoE.swift/Views/ContentView.swift:392-523]()

## Integration with llama.cpp

OLMoE.swift leverages the llama.cpp library as its core inference engine:

```mermaid
graph TD
    A["OLMoE.swift"] --> B["LLM Class"]
    B --> C["Context"]
    C --> D["llama.cpp"]
    
    D --> E["llama_model"]
    D --> F["llama_context"]
    D --> G["llama_batch"]
    D --> H["llama_sampler"]
    
    B --> I["Template"]
    B --> J["InferenceMetrics"]
    
    subgraph "Swift Layer"
        A
        B
        C
        I
        J
    end
    
    subgraph "C/C++ Layer"
        D
        E
        F
        G
        H
    end
```

The integration with llama.cpp provides:
- Efficient model loading and execution
- Token generation and sampling
- Context management for long conversations
- Memory-efficient operation on mobile devices

Sources:
- [OLMoE.swift.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved:14-19]()
- [OLMoE.swift/Model/LLM.swift:131-132]()

## State Management

The application manages several types of state:

| State Type | Storage Mechanism | Purpose | Persistence |
|------------|-------------------|---------|-------------|
| Model State | `LLM.savedState` | Enables continued conversations | Session |
| Conversation History | `LLM.history` | Stores chat messages | Session |
| UI State | SwiftUI `@State` | Controls view appearance | Transient |
| App Configuration | `DisclaimerState` | Tracks onboarding status | Persistent |
| Model Availability | `BackgroundDownloadManager` | Tracks model downloads | Persistent |

This multi-layered state management approach ensures that:
1. Conversations can be paused and resumed
2. User preferences are preserved
3. The UI remains responsive
4. Model state is efficiently managed

Sources:
- [OLMoE.swift/Model/LLM.swift:495-539]()
- [OLMoE.swift/Views/ContentView.swift:393-407]()

## Performance Optimizations

Several optimizations enable efficient on-device inference:

1. **KV Cache Management**: For long conversations, the system trims the oldest tokens from the KV cache to maintain memory efficiency and performance.

```mermaid
graph LR
    A["Long Conversation"] --> B["KV Cache Full"]
    B --> C["trimKvCache()"]
    C --> D["Remove Oldest Tokens"]
    D --> E["Shift Newer Tokens"]
    E --> F["Update nPast Counter"]
    F --> G["Continue Generation"]
```

2. **Batch Processing**: Tokens are processed in batches for efficiency
3. **Thread Management**: The `@InferenceActor` global actor ensures thread-safe model operations
4. **State Persistence**: Model state can be saved and restored to avoid recomputation

Sources:
- [OLMoE.swift/Model/LLM.swift:364-384]()
- [OLMoE.swift/Model/LLM.swift:252-276]()

## Summary

The core architecture of OLMoE.swift is designed to:

1. Efficiently run language models on-device
2. Provide a responsive user experience
3. Manage system resources effectively
4. Ensure thread safety during inference
5. Support a variety of model architectures

This modular design separates concerns between the language model system, user interface components, and application flow management, creating a maintainable and extensible codebase.

Sources:
- [OLMoE.swift/Views/ContentView.swift]()
- [OLMoE.swift/Model/LLM.swift]()
- [OLMoE.swift/Model/Template.swift]()
- [OLMoE.swift/Model/Context.swift]()
- [OLMoE.swift/Model/InferenceMetrics.swift]()

---

