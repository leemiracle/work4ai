<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/concordia · extra page Language Model Interface and Wrappers · fetched 2026-10-26 -->

# Language Model Abstraction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [concordia/document/interactive_document.py](concordia/document/interactive_document.py)
- [concordia/document/interactive_document_test.py](concordia/document/interactive_document_test.py)
- [concordia/language_model/call_limit_wrapper.py](concordia/language_model/call_limit_wrapper.py)
- [concordia/language_model/language_model.py](concordia/language_model/language_model.py)
- [concordia/language_model/no_language_model.py](concordia/language_model/no_language_model.py)
- [concordia/language_model/retry_wrapper.py](concordia/language_model/retry_wrapper.py)
- [concordia/testing/mock_model.py](concordia/testing/mock_model.py)

</details>



## Purpose and Scope

This document covers Concordia's language model abstraction layer, which provides a unified interface for integrating various language model providers into the simulation framework. The abstraction enables seamless switching between different language model backends while maintaining consistent behavior across agents and game masters.

For specific provider implementations, see [Provider Implementations](#2.4.2). For overall language model integration architecture, see [Language Model Integration](#2.4).

## Core Interface

The foundation of Concordia's language model abstraction is the `language_model.LanguageModel` interface, which defines two primary methods that all implementations must support:

| Method | Purpose | Returns |
|--------|---------|---------|
| `sample_text()` | Generate free-form text responses | `str` |
| `sample_choice()` | Select from predefined response options | `tuple[int, str, dict]` |

Both methods support configurable parameters for temperature, token limits, and seed values to ensure reproducible behavior when needed.

**Text Generation Flow**
```mermaid
graph TD
    subgraph "LanguageModel Interface"
        ST["sample_text()"]
        SC["sample_choice()"]
    end
    
    subgraph "Common Parameters"
        PROMPT["prompt: str"]
        TEMP["temperature: float"]
        TOKENS["max_tokens: int"]
        TERM["terminators: Collection[str]"]
        SEED["seed: int | None"]
    end
    
    subgraph "sample_text Flow"
        INPUT1["Prompt + Parameters"]
        PROCESS1["Provider-specific Processing"]
        OUTPUT1["Generated Text"]
    end
    
    subgraph "sample_choice Flow"
        INPUT2["Prompt + Response Options"]
        PROCESS2["Provider-specific Processing"]
        OUTPUT2["(index, selected_response, metadata)"]
    end
    
    PROMPT --> ST
    TEMP --> ST
    TOKENS --> ST
    TERM --> ST
    SEED --> ST
    
    PROMPT --> SC
    SEED --> SC
    
    ST --> INPUT1
    INPUT1 --> PROCESS1
    PROCESS1 --> OUTPUT1
    
    SC --> INPUT2
    INPUT2 --> PROCESS2
    PROCESS2 --> OUTPUT2
```

Sources: [concordia/language_model/google_cloud_custom_model.py:116-217](), [concordia/language_model/no_language_model.py:35-56]()

## Factory System

The language model factory system provides a centralized mechanism for instantiating different provider implementations based on configuration parameters. The main entry point is the `language_model_setup()` function in the utils module.

**Factory Architecture**
```mermaid
graph TD
    subgraph "Factory Function"
        SETUP["language_model_setup()"]
        PARAMS["api_type, model_name, api_key, device"]
    end
    
    subgraph "Supported Providers"
        AMAZON["amazon_bedrock"]
        GOOGLE_AI["google_aistudio_model"]
        GOOGLE_VERTEX["google_cloud_custom_model"]
        LANGCHAIN["langchain_ollama"]
        MISTRAL["mistral"]
        OLLAMA["ollama"]
        OPENAI["openai"]
        PYTORCH["pytorch_gemma"]
        TOGETHER["together_ai"]
    end
    
    subgraph "Implementation Classes"
        AMAZON_CLS["AmazonBedrockLanguageModel"]
        GOOGLE_AI_CLS["GoogleAIStudioLanguageModel"]
        VERTEX_CLS["VertexAI"]
        LANGCHAIN_CLS["LangchainOllamaLanguageModel"]
        MISTRAL_CLS["MistralLanguageModel"]
        OLLAMA_CLS["OllamaLanguageModel"]
        OPENAI_CLS["GptLanguageModel"]
        PYTORCH_CLS["PyTorchGemmaLanguageModel"]
        TOGETHER_CLS["Gemma2"]
    end
    
    subgraph "Special Cases"
        DISABLE["disable_language_model=True"]
        NO_LM["NoLanguageModel"]
    end
    
    PARAMS --> SETUP
    
    SETUP --> AMAZON
    SETUP --> GOOGLE_AI
    SETUP --> GOOGLE_VERTEX
    SETUP --> LANGCHAIN
    SETUP --> MISTRAL
    SETUP --> OLLAMA
    SETUP --> OPENAI
    SETUP --> PYTORCH
    SETUP --> TOGETHER
    
    AMAZON --> AMAZON_CLS
    GOOGLE_AI --> GOOGLE_AI_CLS
    GOOGLE_VERTEX --> VERTEX_CLS
    LANGCHAIN --> LANGCHAIN_CLS
    MISTRAL --> MISTRAL_CLS
    OLLAMA --> OLLAMA_CLS
    OPENAI --> OPENAI_CLS
    PYTORCH --> PYTORCH_CLS
    TOGETHER --> TOGETHER_CLS
    
    DISABLE --> NO_LM
```

The factory supports the following provider mappings:

| `api_type` Parameter | Implementation Class | Purpose |
|---------------------|---------------------|---------|
| `amazon_bedrock` | `AmazonBedrockLanguageModel` | AWS Bedrock models |
| `google_aistudio_model` | `GoogleAIStudioLanguageModel` | Google AI Studio API |
| `google_cloud_custom_model` | `VertexAI` | Google Cloud Vertex AI |
| `langchain_ollama` | `LangchainOllamaLanguageModel` | Ollama via LangChain |
| `mistral` | `MistralLanguageModel` | Mistral AI models |
| `ollama` | `OllamaLanguageModel` | Direct Ollama integration |
| `openai` | `GptLanguageModel` | OpenAI GPT models |
| `pytorch_gemma` | `PyTorchGemmaLanguageModel` | Local PyTorch Gemma |
| `together_ai` | `Gemma2` | Together AI platform |

Sources: [concordia/language_model/utils.py:30-82]()

## Debug and Testing Models

The abstraction includes specialized implementations for development and testing scenarios:

### NoLanguageModel
A minimal implementation that returns empty strings for `sample_text()` and the first option for `sample_choice()`. Useful for debugging simulation logic without language model dependencies.

### RandomChoiceLanguageModel
Extends `NoLanguageModel` but returns random choices in `sample_choice()`, enabling basic randomized behavior testing.

### BiasedMedianChoiceLanguageModel
Provides configurable bias toward median choices, with a `median_probability` parameter controlling the likelihood of selecting the middle option versus uniform random selection.

```mermaid
graph TD
    subgraph "Debug Models Hierarchy"
        BASE["NoLanguageModel"]
        RANDOM["RandomChoiceLanguageModel"]
        BIASED["BiasedMedianChoiceLanguageModel"]
    end
    
    subgraph "Behavior Patterns"
        EMPTY["sample_text() → empty string"]
        FIRST["sample_choice() → first option"]
        RAND["sample_choice() → random option"]
        MEDIAN["sample_choice() → median-biased"]
    end
    
    BASE --> RANDOM
    BASE --> BIASED
    
    BASE --> EMPTY
    BASE --> FIRST
    RANDOM --> RAND
    BIASED --> MEDIAN
```

Sources: [concordia/language_model/no_language_model.py:26-117]()

## Wrapper Functionality

### CallLimitLanguageModel

The `CallLimitLanguageModel` wrapper provides call limiting functionality to prevent excessive API usage during development and testing. It wraps any `LanguageModel` implementation and tracks the number of calls made.

**Call Limiting Behavior:**
- Tracks total calls across both `sample_text()` and `sample_choice()` methods
- Once limit is reached, returns empty strings for text generation
- Returns first option for choice selection after limit
- Displays warning messages when limit is exceeded
- Default limit: 1200 calls

```mermaid
graph TD
    subgraph "CallLimitLanguageModel Wrapper"
        WRAPPER["CallLimitLanguageModel"]
        COUNTER["Call Counter"]
        LIMIT["Max Calls Limit"]
    end
    
    subgraph "Wrapped Model"
        UNDERLYING["Underlying LanguageModel"]
    end
    
    subgraph "Call Flow"
        REQUEST["Method Call"]
        CHECK["Check Counter < Limit"]
        FORWARD["Forward to Underlying"]
        FALLBACK["Return Default Response"]
        INCREMENT["Increment Counter"]
    end
    
    REQUEST --> CHECK
    CHECK -->|"Under Limit"| FORWARD
    CHECK -->|"Over Limit"| FALLBACK
    FORWARD --> UNDERLYING
    FORWARD --> INCREMENT
    INCREMENT --> COUNTER
    
    WRAPPER --> UNDERLYING
    COUNTER --> LIMIT
```

Sources: [concordia/language_model/call_limit_wrapper.py:24-96]()

## Implementation Patterns

### Provider-Specific Configuration

Each provider implementation follows consistent patterns for initialization and configuration:

1. **Authentication**: API keys, credentials, or endpoint configuration
2. **Model Selection**: Specific model names or IDs for the provider
3. **Parameter Mapping**: Translation of common parameters to provider-specific formats
4. **Error Handling**: Retry logic, rate limiting, and failure recovery

### Example: VertexAI Implementation

The `VertexAI` class demonstrates typical implementation patterns:

- **Initialization**: Requires `endpoint_id`, `project_id`, and `location` parameters
- **Client Setup**: Initializes provider-specific client with appropriate endpoints
- **Prompt Wrapping**: Uses `_wrap_prompt()` to format prompts for the specific model
- **Retry Logic**: Implements exponential backoff with jitter for rate limiting
- **Parameter Translation**: Maps common parameters to Vertex AI format

Sources: [concordia/language_model/google_cloud_custom_model.py:75-217]()

### Common Interface Compliance

All implementations must override the `@override` decorated methods from the base `LanguageModel` interface, ensuring consistent behavior across different providers while allowing for provider-specific optimizations and features.

---

