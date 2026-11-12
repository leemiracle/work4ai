<!-- source: DeepWiki mcp.deepwiki.com · repo modelscope/agentscope · page 3 Model Integration · fetched 2026-10-27 -->

# Model Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/model_examples/README.md](scripts/model_examples/README.md)
- [scripts/model_examples/minimax_call.py](scripts/model_examples/minimax_call.py)
- [scripts/model_examples/minimax_multiagent.py](scripts/model_examples/minimax_multiagent.py)
- [scripts/model_examples/minimax_multiagent_multimodal.py](scripts/model_examples/minimax_multiagent_multimodal.py)
- [scripts/model_examples/minimax_multimodal.py](scripts/model_examples/minimax_multimodal.py)
- [scripts/model_examples/run_tests.py](scripts/model_examples/run_tests.py)
- [src/agentscope/_utils/_audio.py](src/agentscope/_utils/_audio.py)
- [src/agentscope/credential/__init__.py](src/agentscope/credential/__init__.py)
- [src/agentscope/credential/_factory.py](src/agentscope/credential/_factory.py)
- [src/agentscope/credential/_minimax.py](src/agentscope/credential/_minimax.py)
- [src/agentscope/formatter/__init__.py](src/agentscope/formatter/__init__.py)
- [src/agentscope/formatter/_minimax_formatter.py](src/agentscope/formatter/_minimax_formatter.py)
- [src/agentscope/model/__init__.py](src/agentscope/model/__init__.py)
- [src/agentscope/model/_base.py](src/agentscope/model/_base.py)
- [src/agentscope/model/_openai_chat/_model.py](src/agentscope/model/_openai_chat/_model.py)
- [src/agentscope/model/_utils.py](src/agentscope/model/_utils.py)
- [tests/model_base_test.py](tests/model_base_test.py)
- [tests/model_openai_chat_test.py](tests/model_openai_chat_test.py)

</details>



## Purpose and Scope

This document describes AgentScope's model integration layer, which provides a unified interface for interacting with multiple Large Language Model (LLM) providers, embedding models, text-to-speech services, classifiers, speech recognition (ASR), and dynamic routing mechanisms. The integration layer abstracts provider-specific API differences while exposing common capabilities like tool calling, streaming, structured output, and multimodal content.

For information about how agents use these models, see [Agent System](#2). For details on message formatting and content blocks, see [Message Protocol and Content Blocks](#2.4). For tool integration with models, see [Tool System](#4).

Sources: [src/agentscope/model/_base.py:37-38](), [src/agentscope/credential/_factory.py:19-48]()

## Architecture Overview

AgentScope implements a provider abstraction pattern where all LLM integrations inherit from `ChatModelBase` [src/agentscope/model/_base.py:37-38]() and implement a unified interface. Each provider handles its own API communication, response parsing, and feature mapping while presenting a consistent interface to agents through `CredentialBase` [src/agentscope/model/_base.py:44-45]() and formatters [src/agentscope/formatter/__init__.py:1-68]().

### Core Model Hierarchy

The diagram below bridges the natural language concepts of model providers to their corresponding code entities in `agentscope.model`.

Title: "Model Integration Class Hierarchy"
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        NLP["DashScopeProvider" / "OpenAIProvider" / "GeminiProvider"]
    end

    subgraph "CodeEntitySpace"
        A["ChatModelBase"] --> B["src/agentscope/model/_base.py"]
        C["CredentialBase"] --> D["src/agentscope/credential/_base.py"]
        E["CredentialFactory"] --> F["src/agentscope/credential/_factory.py"]
        
        G["DashScopeChatModel"] --> H["src/agentscope/model/_dashscope.py"]
        I["OpenAIChatModel"] --> J["src/agentscope/model/_openai_chat.py"]
        K["GeminiChatModel"] --> L["src/agentscope/model/_gemini.py"]
        M["AnthropicChatModel"] --> N["src/agentscope/model/_anthropic.py"]
        O["OllamaChatModel"] --> P["src/agentscope/model/_ollama.py"]
        Q["DeepSeekChatModel"] --> R["src/agentscope/model/_deepseek.py"]
        S["XAIChatModel"] --> T["src/agentscope/model/_xai.py"]
        U["MoonshotChatModel"] --> V["src/agentscope/model/_moonshot.py"]
        W["VolcengineChatModel"] --> X["src/agentscope/model/_volcengine.py"]
        MM["MiniMaxChatModel"] --> MN["src/agentscope/model/_minimax.py"]
    end
    
    NLP -.-> G
    NLP -.-> I
    NLP -.-> K
    
    A --> G
    A --> I
    A --> K
    A --> M
    A --> O
    A --> Q
    A --> S
    A --> U
    A --> W
    A --> MM
```

Sources: [src/agentscope/model/_base.py:37-38](), [src/agentscope/credential/_factory.py:19-48](), [src/agentscope/model/__init__.py:8-18]()

### ChatModelBase and Provider Architecture

The `ChatModelBase` interface [src/agentscope/model/_base.py:37-38]() defines the contract for all chat models. Key patterns include `__call__` / `_call_api` for request execution [src/agentscope/model/_base.py:182-199](), response parsing, and tool formatting for mapping AgentScope tool schemas to provider-specific payloads. It also manages retry logic via `_get_retryable_exceptions` [src/agentscope/model/_base.py:101-109]() and supports listing models via the model card YAML system [src/agentscope/model/_base.py:135-180]().

For details, see [ChatModelBase and Provider Architecture](#3.1).

Sources: [src/agentscope/model/_base.py:37-180]()

## Provider Implementations

### DashScope Integration

The `DashScopeChatModel` class provides integration with Alibaba's DashScope API, supporting advanced features like multimodality, thinking parameters (`thinking_enable`, `thinking_budget`), and OpenAI-compatible client usage [src/agentscope/model/_dashscope.py:34-112]().

For details, see [DashScope Integration](#3.2).

Sources: [src/agentscope/model/_dashscope.py:34-112]()

### OpenAI and Compatible APIs

The integration covers standard OpenAI models and compatible providers like DeepSeek, XAI, Moonshot, Volcengine Ark, and MiniMax [src/agentscope/model/__init__.py:13-18]().

- **OpenAIChatModel & OpenAIResponseModel**: Support standard chat completions as well as reasoning models (o1, o3) [src/agentscope/model/_openai_chat.py:35-35](), [src/agentscope/model/_openai_response.py:25-35]().
- **DeepSeekChatModel**: Specialized for DeepSeek reasoning tracks (`reasoning_content`) [src/agentscope/model/_deepseek.py:26-77]().
- **MoonshotChatModel & VolcengineChatModel**: Integration for Moonshot AI (Kimi) and Volcengine Ark (Doubao) models with thinking mode support [src/agentscope/model/_moonshot.py:26-75](), [src/agentscope/model/_volcengine.py:25-80]().
- **MiniMaxChatModel**: Integrates MiniMax M-series models via their Anthropic-compatible API, supporting thinking parameters and multimodal input [src/agentscope/model/_minimax.py:26-75](), [src/agentscope/credential/_minimax.py:17-42](), [scripts/model_examples/minimax_call.py:34-45](), [scripts/model_examples/minimax_multiagent_multimodal.py:29-38]().

For details, see [OpenAI and Compatible APIs](#3.3).

Sources: [src/agentscope/model/_openai_chat.py:35-108](), [src/agentscope/model/_deepseek.py:26-77](), [src/agentscope/model/_moonshot.py:26-75](), [src/agentscope/model/_minimax.py:26-75](), [src/agentscope/credential/_minimax.py:17-42](), [scripts/model_examples/minimax_call.py:34-45](), [scripts/model_examples/minimax_multiagent_multimodal.py:29-38]()

### Gemini, Anthropic, and Ollama

- **GeminiChatModel**: Handles complex JSON schema sanitization and thinking parts for the Gemini API [src/agentscope/model/_gemini.py:33-140]().
- **AnthropicChatModel**: Manages event-based streaming and extended thinking modes [src/agentscope/model/_anthropic.py:27-96]().
- **OllamaChatModel**: Provides local model integration, supporting thinking models like `deepseek-r1` [src/agentscope/model/_ollama.py:25-53]().

For details, see [Gemini and Anthropic Integrations](#3.4).

Sources: [src/agentscope/model/_gemini.py:33-140](), [src/agentscope/model/_anthropic.py:27-96](), [src/agentscope/model/_ollama.py:25-53]()

## Message Formatters

The `FormatterBase` architecture is responsible for converting AgentScope's message history into the specific payload format required by each provider [src/agentscope/formatter/_formatter_base.py:1-25]().

| Formatter Class | Purpose | Source File |
|-----------------|---------|-------------|
| `ChatFormatter` | Standard single-agent conversation formatting. | `src/agentscope/formatter/_formatter_base.py` |
| `MultiAgentFormatter` | Handles multi-agent history flattening using shared transcripts. | `src/agentscope/formatter/_formatter_base.py` |
| `TruncatedFormatterBase` | Base for formatters supporting context window truncation. | `src/agentscope/formatter/_formatter_base.py` |

The `agentscope.formatter` package includes provider-specific implementations such as `DashScopeChatFormatter`, `OpenAIChatFormatter`, `AnthropicChatFormatter`, `GeminiChatFormatter`, `OllamaChatFormatter`, `DeepSeekChatFormatter`, `OpenAIResponseFormatter`, `MiniMaxChatFormatter`, `MoonshotChatFormatter`, `XAIChatFormatter`, and `VolcengineChatFormatter`, each with corresponding `MultiAgentFormatter` variants [src/agentscope/formatter/__init__.py:5-48]().

For details, see [Message Formatters](#3.5).

Sources: [src/agentscope/formatter/__init__.py:1-68]()

## Response and Message Structures

### ChatResponse and Content Blocks

All model providers return responses in a unified `ChatResponse` format [src/agentscope/model/_model_response.py:14-14](). During streaming, `_StreamAccumulator` [src/agentscope/model/_utils.py:199-204]() collects incremental deltas into structured content blocks such as `TextBlock`, `ThinkingBlock`, `ToolCallBlock`, and `DataBlock` [src/agentscope/model/_base.py:23-30]().

The diagram below bridges natural language response types to their concrete code entity classes.

Title: "Model Response Block Association"
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        NL_RESP["ChatResponse" / "StreamingAccumulator"]
    end

    subgraph "CodeEntitySpace"
        CR["ChatResponse"] --> C1["src/agentscope/model/_model_response.py"]
        TB["TextBlock"] --> B1["src/agentscope/message/_text_block.py"]
        TH["ThinkingBlock"] --> B2["src/agentscope/message/_thinking_block.py"]
        TC["ToolCallBlock"] --> B3["src/agentscope/message/_tool_call_block.py"]
        DB["DataBlock"] --> B4["src/agentscope/message/_data_block.py"]
    end
    
    NL_RESP -.-> CR
    CR -- "contains list of" --> TB
    CR -- "contains list of" --> TH
    CR -- "contains list of" --> TC
    CR -- "contains list of" --> DB
```

Sources: [src/agentscope/model/_model_response.py:14-14](), [src/agentscope/model/_utils.py:199-204](), [src/agentscope/model/_base.py:23-30]()

### Streaming, Structured Output, and Tool Calling

AgentScope supports advanced model features across providers:
- **Streaming Execution**: Accumulates chunks via `_StreamAccumulator` while forwarding deltas [src/agentscope/model/_utils.py:199-204]().
- **Structured Output**: Validates outputs against Pydantic models with automated schema generation and error handling [src/agentscope/model/_base.py:123-132](). The `_get_structured_output_fallback_exceptions` method [src/agentscope/model/_base.py:123-132]() allows providers to declare exceptions that trigger fallback strategies for structured output [tests/model_base_test.py:53-57]().
- **Tool Calling**: Configurable via `ToolChoice` modes (`auto`, `none`, `required`) with automated JSON argument repair [src/agentscope/model/_base.py:31-33]().

For details, see [Streaming, Structured Output, and Tool Calling](#3.6).

Sources: [src/agentscope/model/_base.py:31-204](), [tests/model_base_test.py:53-57]()

## Embedding, TTS, Classifiers, Routing, and ASR

In addition to core chat completions, AgentScope provides integrated subsystems for embeddings, speech synthesis, classification, speech recognition, and runtime model selection:

- **Embedding Models**: `EmbeddingModelBase` provides vector representations for text and multimodal content across providers with caching and RAG support. For details, see [Embedding Models](#3.7).
- **Text-to-Speech (TTS) Models**: `TTSModelBase` and `TTSMiddleware` integrate speech synthesis (DashScope/CosyVoice, OpenAI, Gemini) into agent pipelines. For details, see [Text-to-Speech (TTS) Models](#3.8).
- **Classifier Models**: The `agentscope.classifier` package defines `ClassifierModelBase`, question types (`BinaryQuestion`, `ChoiceQuestion`, `ScoreQuestion`, `BinaryCriteria`), and implementations like `JevClassifierModel`. For details, see [Classifier Models](#3.9).
- **Model Routing**: `ModelRouterMiddleware` and `ChatModelCandidate` enable dynamic per-request model selection, fallback chains, and app-layer model services. For details, see [Model Routing](#3.10).
- **Speech Recognition (ASR) Models**: The `agentscope.asr` package defines `ASRModelBase`, `ASRResponse`, and transcription model integrations. For details, see [Speech Recognition (ASR) Models](#3.11).

Sources: [src/agentscope/model/_base.py:37-38]()

---

