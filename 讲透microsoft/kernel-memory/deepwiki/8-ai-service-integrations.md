<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/kernel-memory · page 8 AI Service Integrations · fetched 2026-10-26 -->

# AI Service Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.gitmodules](.gitmodules)
- [README.md](README.md)

</details>



This document covers the AI service integrations within Kernel Memory, including text generation and embedding generation services. It explains the abstraction layer that allows Kernel Memory to work with multiple AI providers, configuration patterns, and integration mechanisms.

For detailed information about specific text generation implementations, see [Text Generation Services](#5.1). For embedding generation details, see [Embedding Generation Services](#5.2).

## AI Service Architecture

Kernel Memory uses a pluggable architecture for AI services, allowing multiple providers to be integrated through common interfaces. The system supports both text generation for RAG responses and embedding generation for semantic search.

```mermaid
graph TB
    subgraph "Core Interfaces"
        ITG["ITextGenerator"]
        ITEG["ITextEmbeddingGenerator"]
        ITEGB["ITextEmbeddingBatchGenerator"]
        ITT["ITextTokenizer"]
    end
    
    subgraph "OpenAI Implementation"
        OAITG["OpenAITextGenerator"]
        OAITEG["OpenAITextEmbeddingGenerator"]
        OAIC["OpenAIConfig"]
    end
    
    subgraph "Ollama Implementation"
        OLTG["OllamaTextGenerator"]
        OLTEG["OllamaTextEmbeddingGenerator"]
        OLC["OllamaConfig"]
    end
    
    subgraph "Anthropic Implementation"
        ATG["AnthropicTextGeneration"]
        AC["AnthropicConfig"]
    end
    
    subgraph "Kernel Memory Core"
        KMB["KernelMemoryBuilder"]
        SC["SearchClient"]
        PH["Pipeline Handlers"]
    end
    
    ITG --> OAITG
    ITG --> OLTG
    ITG --> ATG
    
    ITEG --> OAITEG
    ITEG --> OLTEG
    ITEGB --> OAITEG
    ITEGB --> OLTEG
    
    OAITG --> OAIC
    OAITEG --> OAIC
    OLTG --> OLC
    OLTEG --> OLC
    ATG --> AC
    
    KMB --> ITG
    KMB --> ITEG
    SC --> ITG
    PH --> ITEG
```

Sources: [extensions/OpenAI/OpenAI/OpenAITextGenerator.cs:28](), [extensions/OpenAI/OpenAI/OpenAITextEmbeddingGenerator.cs:27](), [extensions/Ollama/Ollama/OllamaTextGenerator.cs:17](), [extensions/Ollama/Ollama/OllamaTextEmbeddingGenerator.cs:17](), [extensions/Anthropic/AnthropicTextGeneration.cs:19]()

## Text Generation Service Integration

Text generation services implement the `ITextGenerator` interface and are used primarily for answering questions in the RAG system. Each implementation provides streaming text generation with configurable parameters.

### Common Interface Pattern

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `GenerateTextAsync` | Stream text generation with options | `IAsyncEnumerable<GeneratedTextContent>` |
| `CountTokens` | Count tokens in input text | `int` |
| `GetTokens` | Tokenize input text | `IReadOnlyList<string>` |
| `MaxTokenTotal` | Maximum context window size | `int` |

### Supported Text Generation Services

```mermaid
graph LR
    subgraph "Text Generation Services"
        OpenAI["OpenAI/Azure OpenAI<br/>OpenAITextGenerator"]
        Ollama["Ollama<br/>OllamaTextGenerator"]
        Anthropic["Anthropic Claude<br/>AnthropicTextGeneration"]
        LLamaSharp["LlamaSharp<br/>(via extensions)"]
    end
    
    subgraph "Common Features"
        Streaming["Streaming Responses"]
        TokenUsage["Token Usage Tracking"]
        Options["TextGenerationOptions"]
        Context["Request Context Support"]
    end
    
    OpenAI --> Streaming
    OpenAI --> TokenUsage
    Ollama --> Streaming
    Anthropic --> Streaming
    
    Options --> OpenAI
    Options --> Ollama
    Options --> Anthropic
    
    Context --> Ollama
```

Sources: [extensions/OpenAI/OpenAI/OpenAITextGenerator.cs:127-195](), [extensions/Ollama/Ollama/OllamaTextGenerator.cs:94-151](), [extensions/Anthropic/AnthropicTextGeneration.cs:100-131]()

## Embedding Generation Service Integration

Embedding generation services implement `ITextEmbeddingGenerator` and optionally `ITextEmbeddingBatchGenerator` for efficient batch processing during document ingestion.

### Batch Processing Support

The `ITextEmbeddingBatchGenerator` interface enables efficient processing of multiple text chunks in a single API call:

```mermaid
graph TD
    subgraph "Batch Processing Flow"
        Input["Text Chunks"]
        Check{"Supports Batch?"}
        Batch["GenerateEmbeddingBatchAsync"]
        Single["GenerateEmbeddingAsync"]
        Output["Embedding[]"]
    end
    
    subgraph "Implementation Examples"
        OpenAIBatch["OpenAITextEmbeddingGenerator<br/>MaxBatchSize: configurable"]
        OllamaBatch["OllamaTextEmbeddingGenerator<br/>MaxBatchSize: configurable"]
    end
    
    Input --> Check
    Check -->|Yes| Batch
    Check -->|No| Single
    Batch --> Output
    Single --> Output
    
    Batch --> OpenAIBatch
    Batch --> OllamaBatch
```

Sources: [service/Abstractions/AI/ITextEmbeddingBatchGenerator.cs:13-31](), [extensions/OpenAI/OpenAI/OpenAITextEmbeddingGenerator.cs:143-156](), [extensions/Ollama/Ollama/OllamaTextEmbeddingGenerator.cs:110-148]()

## Configuration and Dependency Injection

AI services are configured through strongly-typed configuration classes and registered via dependency injection extensions.

### Configuration Pattern

Each AI service provider uses a dedicated configuration class:

| Provider | Configuration Class | Key Properties |
|----------|-------------------|----------------|
| OpenAI | `OpenAIConfig` | `ApiKey`, `TextModel`, `EmbeddingModel`, `MaxTokenTotal` |
| Ollama | `OllamaConfig` | `Endpoint`, `TextModel`, `EmbeddingModel` |
| Anthropic | `AnthropicConfig` | `ApiKey`, `TextModelName`, `MaxTokenOut` |

### Dependency Injection Extensions

```mermaid
graph TB
    subgraph "KernelMemoryBuilder Extensions"
        WithOpenAI["WithOpenAITextGeneration()"]
        WithOllama["WithOllamaTextGeneration()"]
        WithOllamaEmb["WithOllamaTextEmbeddingGeneration()"]
    end
    
    subgraph "Service Collection Extensions"
        AddOpenAI["AddOpenAITextGeneration()"]
        AddOllama["AddOllamaTextGeneration()"]
        AddOllamaEmb["AddOllamaTextEmbeddingGeneration()"]
    end
    
    subgraph "Registration Targets"
        ITGReg["ITextGenerator"]
        ITEGReg["ITextEmbeddingGenerator"]
        Singleton["Singleton Lifetime"]
    end
    
    WithOpenAI --> AddOpenAI
    WithOllama --> AddOllama
    WithOllamaEmb --> AddOllamaEmb
    
    AddOpenAI --> ITGReg
    AddOllama --> ITGReg
    AddOllamaEmb --> ITEGReg
    
    ITGReg --> Singleton
    ITEGReg --> Singleton
```

Sources: [extensions/Ollama/Ollama/DependencyInjection.cs:20-56](), [extensions/Ollama/Ollama/DependencyInjection.cs:64-124]()

## Token Management and Context Handling

All AI service implementations include sophisticated token management and context handling capabilities.

### Tokenization Support

Each service uses appropriate tokenizers for accurate token counting:

- **OpenAI**: `O200KTokenizer` for GPT-4, `CL100KTokenizer` for GPT-3.5 and embeddings
- **Ollama**: Configurable tokenizer via `OllamaModelConfig.Tokenizer`  
- **Anthropic**: `CL100KTokenizer` as default fallback

### Context Provider Integration

Services support runtime configuration overrides through `IContextProvider`:

```mermaid
graph LR
    subgraph "Runtime Context"
        CP["IContextProvider"]
        RC["RequestContext"]
        Override["Model Name Override"]
    end
    
    subgraph "Service Implementation"
        Generate["GenerateTextAsync()"]
        ModelName["Dynamic Model Selection"]
        Config["Static Configuration"]
    end
    
    CP --> RC
    RC --> Override
    Override --> Generate
    Generate --> ModelName
    Config --> ModelName
```

Sources: [extensions/Ollama/Ollama/OllamaTextGenerator.cs:99](), [extensions/Ollama/Ollama/OllamaTextEmbeddingGenerator.cs:116](), [extensions/Anthropic/AnthropicTextGeneration.cs:105]()

## Error Handling and Resilience

AI service implementations include comprehensive error handling for HTTP operations and service-specific exceptions.

### Exception Types

- **OpenAI**: `OpenAIException` with transient error detection via `HttpOperationException`
- **Ollama**: Standard HTTP client exceptions with retry logic
- **Anthropic**: Custom exception handling through `RawAnthropicClient`

The implementations distinguish between transient errors (suitable for retry) and permanent failures using status code analysis.

Sources: [extensions/OpenAI/OpenAI/OpenAITextGenerator.cs:160-163](), [extensions/OpenAI/OpenAI/OpenAITextEmbeddingGenerator.cs:136-139]()

---

