<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/wikirace-llms · page 6 AI Model Integration · fetched 2026-10-26 -->

# AI Model Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/game-component.tsx](src/components/game-component.tsx)
- [src/lib/inference.tsx](src/lib/inference.tsx)

</details>



## Purpose and Scope

This document covers how the WikiRacing LLMs application integrates with language models to enable automated gameplay. The system provides a complete inference pipeline that allows AI models to play the WikiRacing game by analyzing Wikipedia article content, reasoning about optimal paths, and making navigation decisions.

For information about the game mechanics and user interface, see [Game Interface](#4.2). For details about the evaluation framework that tests models at scale, see [Parallel Evaluation System](#7).

## Architecture Overview

The AI model integration consists of three primary components: the inference client system, the game integration layer, and the prompt engineering pipeline. The system supports multiple AI providers and handles both streaming and non-streaming inference modes.

### Core Integration Architecture

```mermaid
graph TB
    GameComponent["GameComponent"]
    useInference["useInference Hook"]
    InferenceClient["InferenceClient (@huggingface/inference)"]
    buildPrompt["buildPrompt Function"]
    
    subgraph "AI Providers"
        FireworksAI["fireworks-ai"]
        Nebius["nebius"]
    end
    
    subgraph "Models"
        QwenModel["Qwen/Qwen3-235B-A22B"]
        GemmaModel["Gemma Models"]
        DeepSeekModel["DeepSeek Models"]
    end
    
    GameComponent --> useInference
    GameComponent --> buildPrompt
    useInference --> InferenceClient
    buildPrompt --> InferenceClient
    
    InferenceClient --> FireworksAI
    InferenceClient --> Nebius
    
    FireworksAI --> QwenModel
    FireworksAI --> GemmaModel
    Nebius --> QwenModel
    Nebius --> DeepSeekModel
```

Sources: [src/components/game-component.tsx:1-815](), [src/lib/inference.tsx:1-154]()

## Inference System Implementation

The inference system is built around the `useInference` hook and supporting functions that handle model communication, response streaming, and error management.

### useInference Hook Structure

```mermaid
graph TB
    useInference["useInference Hook"]
    
    subgraph "State Management"
        isLoading["isLoading: boolean"]
        partialText["partialText: string"]
        inferenceResult["inferenceResult: string"]
        error["error: string | null"]
    end
    
    subgraph "Core Function"
        inferenceInternal["inferenceInternal Function"]
    end
    
    subgraph "Return Object"
        status["status: 'thinking' | 'error' | 'done'"]
        inference["inference: Function"]
    end
    
    useInference --> isLoading
    useInference --> partialText
    useInference --> inferenceResult
    useInference --> error
    useInference --> inferenceInternal
    
    inferenceInternal --> status
    inferenceInternal --> inference
```

The `useInference` hook provides a stateful interface for model interactions with the following key features:

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Streaming Support | Real-time response updates | `chatCompletionStream` with async iteration |
| Error Handling | Comprehensive error management | Try-catch blocks with state updates |
| Loading States | Visual feedback during inference | `isLoading` state with derived `status` |
| Partial Results | Progressive text display | `partialText` updated per chunk |

Sources: [src/lib/inference.tsx:92-153]()

### Provider Configuration

The system supports multiple AI providers with different configurations:

```mermaid
graph LR
    InferenceRequest["Inference Request"]
    
    subgraph "Fireworks AI Provider"
        FireworksConfig["provider: 'fireworks-ai'"]
        FireworksModels["Qwen, Gemma, etc."]
    end
    
    subgraph "Nebius Provider"
        NebiusConfig["provider: 'nebius'"]
        NebiusModels["Qwen, DeepSeek, etc."]
    end
    
    InferenceRequest --> FireworksConfig
    InferenceRequest --> NebiusConfig
    
    FireworksConfig --> FireworksModels
    NebiusConfig --> NebiusModels
```

The inference functions switch between providers based on configuration:
- **Fireworks AI**: Used in the standalone `inference` function [src/lib/inference.tsx:26-36]()
- **Nebius**: Used in the streaming `useInference` hook [src/lib/inference.tsx:112-122]()

Sources: [src/lib/inference.tsx:4-41](), [src/lib/inference.tsx:92-153]()

## Game Integration Flow

The AI model integration within the game follows a structured flow from user action to model response to game state update.

### Model Move Execution Pipeline

```mermaid
sequenceDiagram
    participant GC as "GameComponent"
    participant BP as "buildPrompt"
    participant UI as "useInference"
    participant IC as "InferenceClient"
    participant Model as "AI Model"
    
    GC->>BP: buildPrompt(currentPage, targetPage, path, links)
    BP-->>GC: Formatted prompt string
    
    GC->>UI: inference({model, prompt, maxTokens})
    UI->>IC: chatCompletionStream({provider, model, messages})
    
    IC->>Model: HTTP POST with prompt
    Model-->>IC: Streaming response chunks
    
    loop For each chunk
        IC-->>UI: Response chunk
        UI-->>GC: Update partialText state
    end
    
    UI-->>GC: Final result with status
    GC->>GC: Parse <answer>N</answer> tags
    GC->>GC: Update game state with selected link
```

Sources: [src/components/game-component.tsx:218-298]()

### Prompt Construction

The `buildPrompt` function creates structured prompts that guide model behavior:

```mermaid
graph TB
    buildPrompt["buildPrompt Function"]
    
    subgraph "Input Parameters"
        current["current: string"]
        target["target: string"] 
        pathSoFar["path_so_far: string[]"]
        links["links: string[]"]
    end
    
    subgraph "Prompt Components"
        instructions["Game Instructions"]
        answerFormat["Answer Format Rules"]
        currentState["Current Game State"]
        availableLinks["Available Links (numbered)"]
        pathHistory["Path History"]
        reasoning["Reasoning Guidelines"]
    end
    
    buildPrompt --> current
    buildPrompt --> target
    buildPrompt --> pathSoFar
    buildPrompt --> links
    
    current --> currentState
    target --> currentState
    pathSoFar --> pathHistory
    links --> availableLinks
    
    instructions --> answerFormat
    answerFormat --> reasoning
```

The prompt structure includes:
- **Game Context**: Current article, target article, and path history
- **Available Actions**: Numbered list of clickable links
- **Response Format**: Strict XML tag requirements `<answer>NUMBER</answer>`
- **Reasoning Instructions**: Guidance for strategic thinking

Sources: [src/components/game-component.tsx:78-105]()

## Response Processing and Validation

The system implements robust response parsing to extract model decisions and handle edge cases.

### Answer Extraction Logic

| Step | Process | Error Handling |
|------|---------|----------------|
| 1. Regex Matching | Extract `<answer>N</answer>` tags | Log error if no match found |
| 2. Integer Parsing | Convert extracted text to number | Log error if `isNaN(answerInt)` |
| 3. Bounds Checking | Validate against available links | Log error if out of bounds |
| 4. Link Selection | Map number to actual link text | Continue with valid selection |

```mermaid
graph TB
    modelResponse["Model Response Text"]
    regexMatch["Regex: /<answer>(.*?)<\/answer>/"]
    intParsing["parseInt(answer)"]
    boundsCheck["1 <= answerInt <= links.length"]
    linkSelection["currentPageLinks[answerInt - 1]"]
    
    modelResponse --> regexMatch
    regexMatch --> intParsing
    intParsing --> boundsCheck
    boundsCheck --> linkSelection
    
    regexMatch -->|"No match"| errorNoAnswer["Log: No answer found"]
    intParsing -->|"isNaN"| errorInvalid["Log: Invalid answer"]
    boundsCheck -->|"Out of bounds"| errorBounds["Log: Link out of bounds"]
```

Sources: [src/components/game-component.tsx:254-278]()

## Authentication and Configuration

The AI integration requires proper authentication and configuration management for accessing model APIs.

### Authentication Flow

```mermaid
graph TB
    localStorage["window.localStorage"]
    apiKey["API Key Parameter"]
    inferenceCall["Inference Function Call"]
    
    subgraph "Auth Check Process"
        checkParam["Check apiKey parameter"]
        checkStorage["Get 'huggingface_access_token'"]
        throwError["Throw authentication error"]
    end
    
    inferenceCall --> checkParam
    checkParam -->|"Not provided"| checkStorage
    checkParam -->|"Provided"| InferenceClient
    checkStorage -->|"Found"| InferenceClient
    checkStorage -->|"Not found"| throwError
    
    localStorage --> checkStorage
    apiKey --> checkParam
```

The authentication system follows this hierarchy:
1. **Function Parameter**: Direct API key passed to inference functions
2. **Local Storage**: Fallback to stored Hugging Face access token
3. **Error State**: Throws error if no authentication available

Sources: [src/lib/inference.tsx:15-21](), [src/components/game-component.tsx:150-152]()

### Model Configuration Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `model` | `string` | `"Qwen/Qwen3-235B-A22B"` | Specifies which AI model to use |
| `maxTokens` | `number` | `512` | Limits response length |
| `apiKey` | `string` | `undefined` | Authentication token |
| `provider` | `string` | `"nebius"` | AI service provider |

Sources: [src/lib/inference.tsx:6-8](), [src/lib/inference.tsx:113-114]()

## Conversation and State Management

The game component maintains detailed conversation logs and manages the interaction state between human players, AI models, and the game system.

### Message Types and Structure

```mermaid
graph TB
    Message["Message Interface"]
    
    subgraph "Message Roles"
        user["user: Human/System prompts"]
        assistant["assistant: Model responses"]
        game["game: Status updates"]
        result["result: Final outcomes"]
        error["error: Error messages"]
    end
    
    subgraph "Message Metadata"
        page["page: Current article"]
        links["links: Available options"]
        status["status: Game state"]
        path["path: Route taken"]
    end
    
    Message --> user
    Message --> assistant
    Message --> game
    Message --> result
    Message --> error
    
    game --> page
    game --> links
    result --> status
    result --> path
```

The conversation system tracks all interactions and provides rich context for debugging and analysis. Each message type serves a specific purpose in the game flow and user interface.

Sources: [src/components/game-component.tsx:67-76](), [src/components/game-component.tsx:310-312]()

---

