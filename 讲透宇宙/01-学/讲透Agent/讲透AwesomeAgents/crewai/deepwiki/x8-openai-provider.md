<!-- source: DeepWiki mcp.deepwiki.com · repo crewAIInc/crewAI · extra page OpenAI Provider · fetched 2026-10-26 -->

# OpenAI Provider

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/edge/ar/concepts/llms.mdx](docs/edge/ar/concepts/llms.mdx)

</details>



The OpenAI Provider provides native integration with OpenAI's Python SDK, supporting both the Chat Completions API and the Responses API. This implementation offers direct access to OpenAI-specific features including built-in tools (web search, file search, code interpreter), stateful multi-turn conversations, and Zero Data Retention (ZDR) compliance for reasoning models.

## Architecture Overview

The `OpenAICompletion` class provides the native implementation for OpenAI models, extending the `BaseLLM` abstract base class. The implementation is automatically selected by the LLM factory when using OpenAI model identifiers.

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        A["Model Selection & Provider Routing"]
        B["API Call Execution & Client Management"]
    end

    subgraph "CodeEntitySpace"
        subgraph "Factory Layer"
            LLM["LLM Factory<br/>crewai.llms.llm.LLM"]
            INFER["_infer_provider_from_model<br/>crewai.llms.llm.LLM._infer_provider_from_model"]
            VALIDATE["_validate_model_in_constants<br/>crewai.llms.llm.LLM._validate_model_in_constants"]
        end
        
        subgraph "OpenAI Implementation"
            OPENAI["OpenAICompletion<br/>crewai.llms.providers.openai.completion.OpenAICompletion"]
            CLIENT["OpenAI Client<br/>openai.OpenAI"]
            ASYNC_CLIENT["AsyncOpenAI Client<br/>openai.AsyncOpenAI"]
        end
        
        subgraph "API Selection"
            COMPLETIONS["_call_completions<br/>crewai.llms.providers.openai.completion.OpenAICompletion._call_completions"]
            RESPONSES["_call_responses<br/>crewai.llms.providers.openai.completion.OpenAICompletion._call_responses"]
        end
        
        subgraph "Base Components"
            BASELLM["BaseLLM<br/>crewai.llms.base_llm.BaseLLM"]
            EVENTS["Event Bus<br/>LLMCallStartedEvent / LLMCallCompletedEvent / LLMStreamChunkEvent"]
            HOOKS["LLM Hooks<br/>before_llm_call / after_llm_call"]
        end
    end

    A --> LLM
    B --> OPENAI
    
    LLM --> INFER
    INFER --> VALIDATE
    VALIDATE -->|"gpt-4o, o1-, etc"| OPENAI
    
    OPENAI --> BASELLM
    OPENAI --> CLIENT
    OPENAI --> ASYNC_CLIENT
    
    OPENAI -->|"api='completions'"| COMPLETIONS
    OPENAI -->|"api='responses'"| RESPONSES
    
    OPENAI --> EVENTS
    OPENAI --> HOOKS
```

**Diagram: OpenAI Provider Architecture**

Sources: [lib/crewai/src/crewai/llms/providers/openai/completion.py:149-264](), [lib/crewai/src/crewai/llms/base_llm.py:85-175]()

## Initialization and Configuration

The `OpenAICompletion` class is instantiated through the LLM factory or directly. Configuration includes API credentials, client parameters, and model-specific settings.

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        C["User Configuration & Parameter Mapping"]
    end

    subgraph "CodeEntitySpace"
        subgraph "Configuration Parameters"
            MODEL["model<br/>gpt-4o, o1-preview, etc"]
            API_KEY["api_key<br/>OPENAI_API_KEY env"]
            BASE_URL["base_url<br/>OPENAI_BASE_URL env"]
            TIMEOUT["timeout<br/>Request timeout"]
            TEMP["temperature<br/>Sampling temperature"]
            MAX_TOKENS["max_tokens<br/>max_completion_tokens"]
            STREAM["stream<br/>Enable streaming"]
            API_SELECT["api<br/>'completions' or 'responses'"]
        end
        
        subgraph "Responses API Parameters"
            INSTRUCTIONS["instructions<br/>System-level instructions"]
            STORE["store<br/>Store responses"]
            PREV_RESP["previous_response_id<br/>Multi-turn linking"]
            INCLUDE["include<br/>Additional data"]
            BUILTIN["builtin_tools<br/>web_search, file_search, etc"]
            AUTO_CHAIN["auto_chain<br/>Auto-track response IDs"]
            AUTO_REASON["auto_chain_reasoning<br/>ZDR compliance"]
        end
        
        subgraph "Client Setup"
            CLIENT_PARAMS["_get_client_params<br/>crewai.llms.providers.openai.completion.OpenAICompletion._get_client_params"]
            OPENAI_CLIENT["OpenAI client<br/>openai.OpenAI"]
            ASYNC_CLIENT["AsyncOpenAI client<br/>openai.AsyncOpenAI"]
        end
    end

    C --> MODEL
    MODEL --> CLIENT_PARAMS
    API_KEY --> CLIENT_PARAMS
    BASE_URL --> CLIENT_PARAMS
    TIMEOUT --> CLIENT_PARAMS
    
    CLIENT_PARAMS --> OPENAI_CLIENT
    CLIENT_PARAMS --> ASYNC_CLIENT
    
    API_SELECT -.->|"if 'responses'"| INSTRUCTIONS
    API_SELECT -.->|"if 'responses'"| BUILTIN
    API_SELECT -.->|"if 'responses'"| AUTO_CHAIN
```

**Diagram: OpenAI Configuration Flow**

### Basic Initialization

```python
from crewai import LLM

# Automatic provider inference
llm = LLM(model="gpt-4o")

# Advanced configuration with detailed parameters
llm = LLM(
    model="openai/gpt-4o",
    temperature=0.7,
    timeout=120,
    max_tokens=4000,
    api_key="sk-...",
    reasoning_effort="medium"  # For o1 models
)
```

### Client Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `model` | `str` | Model identifier (gpt-4o, o1-preview, etc) | `"gpt-4o"` |
| `api_key` | `str` | OpenAI API key | `OPENAI_API_KEY` env |
| `base_url` | `str` | Custom API base URL | `OPENAI_BASE_URL` env |
| `organization` | `str` | OpenAI organization ID | `None` |
| `project` | `str` | OpenAI project ID | `None` |
| `timeout` | `float` | Request timeout in seconds | `None` |
| `max_retries` | `int` | Maximum retry attempts | `2` |

### Completion Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `temperature` | `float` | Sampling temperature (0-2) | `None` |
| `top_p` | `float` | Nucleus sampling parameter | `None` |
| `max_tokens` | `int` | Maximum tokens (legacy) | `None` |
| `max_completion_tokens` | `int` | Maximum completion tokens (for newer models) | `None` |
| `stream` | `bool` | Enable streaming responses | `False` |
| `reasoning_effort` | `str` | Effort for o1 models: low, medium, high | `None` |

Sources: [docs/edge/ar/concepts/llms.mdx:148-172](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:186-248](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:332-359]()

## Chat Completions API vs Responses API

OpenAI offers two API primitives: the traditional Chat Completions API and the newer Responses API. The `api` parameter determines which is used.

```mermaid
graph TB
    subgraph "API Selection"
        CALL["call method<br/>crewai.llms.providers.openai.completion.OpenAICompletion.call"]
        CHECK{api parameter}
        
        CALL --> CHECK
        CHECK -->|"api='completions'"| COMP_PATH["_call_completions<br/>crewai.llms.providers.openai.completion.OpenAICompletion._call_completions"]
        CHECK -->|"api='responses'"| RESP_PATH["_call_responses<br/>crewai.llms.providers.openai.completion.OpenAICompletion._call_responses"]
    end
    
    subgraph "Chat Completions API"
        COMP_PATH --> PREP_COMP["_prepare_completion_params<br/>crewai.llms.providers.openai.completion.OpenAICompletion._prepare_completion_params"]
        PREP_COMP --> COMP_API["client.chat.completions.create"]
        COMP_API --> HANDLE_COMP["_handle_completion<br/>crewai.llms.providers.openai.completion.OpenAICompletion._handle_completion"]
    end
    
    subgraph "Responses API"
        RESP_PATH --> PREP_RESP["_prepare_responses_params<br/>crewai.llms.providers.openai.completion.OpenAICompletion._prepare_responses_params"]
        PREP_RESP --> RESP_API["client.responses.create"]
        RESP_API --> HANDLE_RESP["_handle_responses<br/>crewai.llms.providers.openai.completion.OpenAICompletion._handle_responses"]
    end
```

**Diagram: API Selection and Features**

### Chat Completions API (Default)

The traditional API supporting custom function calling and streaming. It is the standard interface for most GPT models.

### Responses API

The newer API with built-in tools and stateful conversations. It supports specific features like `web_search` and `file_search` natively. The Responses API is designed for multimodal native support, including text, images, and audio as core components.

Sources: [lib/crewai/src/crewai/llms/providers/openai/completion.py:149-177](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:361-428](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:618-738](), [docs/edge/ar/concepts/llms.mdx:191-193]()

## Built-in Tools (Responses API)

The Responses API provides access to OpenAI's built-in tools without requiring external implementations.

```mermaid
graph TB
    subgraph "Built-in Tool Types"
        WEB["web_search<br/>BUILTIN_TOOL_TYPES: web_search_preview"]
        FILE["file_search<br/>BUILTIN_TOOL_TYPES: file_search"]
        CODE["code_interpreter<br/>BUILTIN_TOOL_TYPES: code_interpreter"]
        COMPUTER["computer_use<br/>BUILTIN_TOOL_TYPES: computer_use_preview"]
    end
    
    subgraph "Configuration"
        INIT["builtin_tools parameter<br/>crewai.llms.providers.openai.completion.OpenAICompletion"]
        PARAMS["_prepare_responses_params<br/>crewai.llms.providers.openai.completion.OpenAICompletion._prepare_responses_params"]
    end
    
    subgraph "Result Extraction"
        PARSE["parse_tool_outputs parameter<br/>crewai.llms.providers.openai.completion.OpenAICompletion"]
        EXTRACT["_extract_builtin_tool_outputs<br/>crewai.llms.providers.openai.completion.OpenAICompletion._extract_builtin_tool_outputs"]
        RESULT["ResponsesAPIResult<br/>crewai.llms.providers.openai.completion.ResponsesAPIResult"]
    end
    
    INIT --> PARAMS
    PARAMS --> WEB
    PARAMS --> FILE
    PARAMS --> CODE
    PARAMS --> COMPUTER
    
    PARSE --> EXTRACT
    EXTRACT --> RESULT
```

**Diagram: Built-in Tools Architecture**

### ResponsesAPIResult Structure

The `ResponsesAPIResult` dataclass provides structured access to tool outputs including `web_search_results`, `file_search_results`, and `code_interpreter_results`.

Sources: [lib/crewai/src/crewai/llms/providers/openai/completion.py:112-147](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:1074-1156]()

## Auto-chaining for Multi-turn Conversations

The `auto_chain` feature automatically tracks and uses response IDs to maintain stateful conversations. When enabled, the provider stores the `_last_response_id` and injects it as `previous_response_id` in subsequent calls.

```mermaid
graph TB
    subgraph "Auto-chain Flow"
        ENABLE["auto_chain=True<br/>crewai.llms.providers.openai.completion.OpenAICompletion"]
        FIRST_CALL["First call()<br/>No previous_response_id"]
        RESPONSE1["Response with ID<br/>response.id"]
        STORE["Store to _last_response_id<br/>crewai.llms.providers.openai.completion.OpenAICompletion"]
        SECOND_CALL["Second call()"]
        USE["Use stored ID as<br/>previous_response_id<br/>crewai.llms.providers.openai.completion.OpenAICompletion._prepare_responses_params"]
    end
    
    ENABLE --> FIRST_CALL
    FIRST_CALL --> RESPONSE1
    RESPONSE1 --> STORE
    STORE --> SECOND_CALL
    SECOND_CALL --> USE
```

Sources: [lib/crewai/src/crewai/llms/providers/openai/completion.py:219](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:294-310](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:669-671](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:795-796]()

## Zero Data Retention (ZDR) Compliance

The `auto_chain_reasoning` feature enables Zero Data Retention compliance for reasoning models by preserving encrypted reasoning content. It extracts reasoning items using `_extract_reasoning_items` and prepends them to the input of the next call to preserve the chain-of-thought without unencrypted server storage.

Sources: [lib/crewai/src/crewai/llms/providers/openai/completion.py:169-177](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:648-651](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:799-802](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:1158-1185]()

## Streaming and Usage Tracking

The provider supports streaming responses via `LLMStreamChunkEvent`. Token usage is tracked internally using `_track_token_usage_internal` and can be retrieved via `get_usage_metrics()`.

Sources: [lib/crewai/src/crewai/llms/base_llm.py:541-567](), [lib/crewai/src/crewai/llms/base_llm.py:578-623](), [lib/crewai/src/crewai/llms/providers/openai/completion.py:1385-1514]()

---

