<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langchain · page 8 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/core/langchain_core/callbacks/base.py](libs/core/langchain_core/callbacks/base.py)
- [libs/core/langchain_core/callbacks/manager.py](libs/core/langchain_core/callbacks/manager.py)
- [libs/core/langchain_core/messages/ai.py](libs/core/langchain_core/messages/ai.py)
- [libs/core/langchain_core/messages/base.py](libs/core/langchain_core/messages/base.py)
- [libs/core/langchain_core/messages/tool.py](libs/core/langchain_core/messages/tool.py)
- [libs/core/langchain_core/messages/utils.py](libs/core/langchain_core/messages/utils.py)
- [libs/core/langchain_core/output_parsers/string.py](libs/core/langchain_core/output_parsers/string.py)
- [libs/core/langchain_core/rate_limiters.py](libs/core/langchain_core/rate_limiters.py)
- [libs/core/langchain_core/runnables/base.py](libs/core/langchain_core/runnables/base.py)
- [libs/core/langchain_core/runnables/branch.py](libs/core/langchain_core/runnables/branch.py)
- [libs/core/langchain_core/runnables/config.py](libs/core/langchain_core/runnables/config.py)
- [libs/core/langchain_core/runnables/configurable.py](libs/core/langchain_core/runnables/configurable.py)
- [libs/core/langchain_core/runnables/fallbacks.py](libs/core/langchain_core/runnables/fallbacks.py)
- [libs/core/langchain_core/runnables/passthrough.py](libs/core/langchain_core/runnables/passthrough.py)
- [libs/core/langchain_core/runnables/retry.py](libs/core/langchain_core/runnables/retry.py)
- [libs/core/langchain_core/runnables/schema.py](libs/core/langchain_core/runnables/schema.py)
- [libs/core/langchain_core/runnables/utils.py](libs/core/langchain_core/runnables/utils.py)
- [libs/core/langchain_core/utils/_merge.py](libs/core/langchain_core/utils/_merge.py)
- [libs/core/langchain_core/utils/formatting.py](libs/core/langchain_core/utils/formatting.py)
- [libs/core/tests/unit_tests/callbacks/test_sync_callback_manager.py](libs/core/tests/unit_tests/callbacks/test_sync_callback_manager.py)
- [libs/core/tests/unit_tests/messages/test_utils.py](libs/core/tests/unit_tests/messages/test_utils.py)
- [libs/core/tests/unit_tests/prompts/__snapshots__/test_chat.ambr](libs/core/tests/unit_tests/prompts/__snapshots__/test_chat.ambr)
- [libs/core/tests/unit_tests/runnables/test_config.py](libs/core/tests/unit_tests/runnables/test_config.py)
- [libs/core/tests/unit_tests/runnables/test_configurable.py](libs/core/tests/unit_tests/runnables/test_configurable.py)
- [libs/core/tests/unit_tests/runnables/test_runnable.py](libs/core/tests/unit_tests/runnables/test_runnable.py)
- [libs/core/tests/unit_tests/runnables/test_utils.py](libs/core/tests/unit_tests/runnables/test_utils.py)
- [libs/core/tests/unit_tests/test_messages.py](libs/core/tests/unit_tests/test_messages.py)
- [libs/core/tests/unit_tests/utils/test_formatting.py](libs/core/tests/unit_tests/utils/test_formatting.py)
- [libs/langchain_v1/langchain/agents/factory.py](libs/langchain_v1/langchain/agents/factory.py)
- [libs/langchain_v1/langchain/agents/middleware/__init__.py](libs/langchain_v1/langchain/agents/middleware/__init__.py)
- [libs/langchain_v1/langchain/agents/middleware/context_editing.py](libs/langchain_v1/langchain/agents/middleware/context_editing.py)
- [libs/langchain_v1/langchain/agents/middleware/todo.py](libs/langchain_v1/langchain/agents/middleware/todo.py)
- [libs/langchain_v1/langchain/agents/middleware/tool_selection.py](libs/langchain_v1/langchain/agents/middleware/tool_selection.py)
- [libs/langchain_v1/langchain/agents/middleware/types.py](libs/langchain_v1/langchain/agents/middleware/types.py)
- [libs/langchain_v1/langchain/agents/structured_output.py](libs/langchain_v1/langchain/agents/structured_output.py)
- [libs/langchain_v1/tests/unit_tests/agents/test_response_format.py](libs/langchain_v1/tests/unit_tests/agents/test_response_format.py)
- [libs/model-profiles/langchain_model_profiles/cli.py](libs/model-profiles/langchain_model_profiles/cli.py)
- [libs/model-profiles/tests/unit_tests/test_cli.py](libs/model-profiles/tests/unit_tests/test_cli.py)
- [libs/partners/anthropic/langchain_anthropic/data/_profiles.py](libs/partners/anthropic/langchain_anthropic/data/_profiles.py)
- [libs/partners/deepseek/langchain_deepseek/data/_profiles.py](libs/partners/deepseek/langchain_deepseek/data/_profiles.py)
- [libs/partners/fireworks/langchain_fireworks/data/_profiles.py](libs/partners/fireworks/langchain_fireworks/data/_profiles.py)
- [libs/partners/groq/langchain_groq/data/_profiles.py](libs/partners/groq/langchain_groq/data/_profiles.py)
- [libs/partners/huggingface/langchain_huggingface/data/_profiles.py](libs/partners/huggingface/langchain_huggingface/data/_profiles.py)
- [libs/partners/mistralai/langchain_mistralai/data/_profiles.py](libs/partners/mistralai/langchain_mistralai/data/_profiles.py)
- [libs/partners/openai/langchain_openai/data/_profiles.py](libs/partners/openai/langchain_openai/data/_profiles.py)
- [libs/partners/openrouter/langchain_openrouter/data/_profiles.py](libs/partners/openrouter/langchain_openrouter/data/_profiles.py)
- [libs/partners/perplexity/langchain_perplexity/data/_profiles.py](libs/partners/perplexity/langchain_perplexity/data/_profiles.py)
- [libs/partners/xai/langchain_xai/data/_profiles.py](libs/partners/xai/langchain_xai/data/_profiles.py)

</details>





## Purpose and Scope
This page provides a technical glossary of core terms, classes, interfaces, and design patterns specific to the LangChain monorepo architecture. Each term is paired with its functional definition, architectural role, and precise code pointers within the repository.

---

## 1. Core Abstractions & LCEL

### Runnable
- **Definition**: `Runnable` is the core abstraction representing a unit of work that supports invocation, batching, streaming, transformation, and composition.
- **Implementation**: The abstract generic class `Runnable[Input, Output]` defines essential methods:
  - `invoke(input, config)`: Synchronously transforms a single input to output.
  - `ainvoke(input, config)`: Asynchronous counterpart to `invoke`.
  - `batch(inputs, config)`: Processes a batch of inputs efficiently, by default running `invoke` in parallel.
  - `abatch(inputs, config)`: Async batch version.
  - `stream(input, config)`: Streams output tokens for a single input synchronously.
  - `astream(input, config)`: Async streaming output.
  - `astream_log(input, config)`: Streams output with intermediate logs (deprecated in favor of `astream`).
  
  Runnables optionally expose schemas describing input, output, and configuration. They can be composed into sequences or parallel collections, enabling complex pipelines.
- **Composition**:
  - `RunnableSequence`: Runs runnables sequentially, chaining output to input.
  - `RunnableParallel`: Runs runnables in parallel, with the same input sent to all, returning a dictionary of results.
- **Usage Example**:
  ```python
  from langchain_core.runnables import RunnableLambda

  # Compose two transformations in sequence
  sequence = RunnableLambda(lambda x: x + 1) | RunnableLambda(lambda x: x * 2)
  result = sequence.invoke(1)  # returns 4
  ```
- **Code Pointer**: Implementation and docs near lines 133-212 in `libs/core/langchain_core/runnables/base.py`


### LCEL (LangChain Expression Language)
- **Definition**: LCEL is the idiomatic, declarative language for composing `Runnable` objects into directed execution graphs supporting sequential and parallel execution.
- **Key Concepts**:
  - `RunnableSequence` composes runnables sequentially via the `|` operator or Python lists.
  - `RunnableParallel` composes runnables concurrently via dicts or explicit construction.
- **Code Pointer**: Composition details in `libs/core/langchain_core/runnables/base.py:161-178`

### RunnableConfig
- **Definition**: Configuration container passed to runnable methods to manage runtime execution control such as retries, concurrency, callbacks, tracing tags, and metadata.
- **Implementation**: `RunnableConfig` is a typed Pydantic model or dict-like structure that is merged and propagated automatically during runnable composition and execution.
- **Code Pointer**: Defined in `libs/core/langchain_core/runnables/config.py`, used throughout runnable methods ([libs/core/langchain_core/runnables/base.py:52-65]() references it).


```mermaid
title Runnable and LCEL Composition Framework
graph TD
    subgraph NL["Natural Language Concepts"]
        direction TB
        ChainRequest["Chain Execution Request"] --> ConfigPropagation["Configuration Propagation"]
        Pipeline["Composable Pipeline"] --> ParallelFanout["Parallel Fan-Out"]
    end

    subgraph CodeEntities["Code Entities"]
        direction TB
        RunnableConfig["RunnableConfig"]
        Runnable["Runnable[Input, Output]"]
        RunnableSequence["RunnableSequence"]
        RunnableParallel["RunnableParallel"]
    end

    ChainRequest --> RunnableConfig
    ConfigPropagation --> RunnableConfig
    Pipeline --> Runnable
    Pipeline --> RunnableSequence
    ParallelFanout --> RunnableParallel

    classDef class fill:none,stroke:#000,stroke-width:1px;
```

*Sources: [libs/core/langchain_core/runnables/base.py:133-212](), [libs/core/langchain_core/runnables/config.py]()


---

## 2. Messages & Content

### AIMessageChunk
- **Definition**: A partial incremental stream chunk representing an AI-generated response fragment during chat streaming.
- **Implementation**: A subclass of `BaseMessageChunk` specialized for AI messages. Contains fields for the chunk content, streaming flags, tool call chunks, and usage metadata (tokens counts). Supports merging with other chunks to progressively assemble complete message outputs.
- **Code Pointer**: `libs/core/langchain_core/messages/ai.py` (definition), referenced in message utils [libs/core/langchain_core/messages/utils.py:36]()

### ContentBlock
- **Definition**: A unit of structured content inside messages, represented as dictionaries with a mandatory `type` key indicating content type (e.g., `"text"`, `"image"`, `"reasoning"`, `"tool_output"`).
- **Implementation**: ContentBlocks can carry text, URLs, embedded data, reasoning metadata, images, audio, video, and tool call results. Used heavily in message serialization, chunking, and provider interoperability.
- **Code Pointer**: Implementations and formatting utilities in `libs/core/langchain_core/messages/utils.py:142-205`

```mermaid
title Streaming Messages and Content Blocks
graph TD
    subgraph NL["Streaming & Message Content"]
        direction TB
        TokenStream["Incremental Stream Tokens"] --> ChunkAggregation["Chunk Aggregation"]
        MediaPayload["Multimodal & Tool Payload"] --> StructuredBlock["ContentBlock Typed Dict"]
    end

    subgraph CodeEntities["Code Entities"]
        direction TB
        AIMessageChunk["AIMessageChunk"]
        BaseMessageChunk["BaseMessageChunk"]
        FormatContentBlockXML["_format_content_block_xml()"]
    end

    TokenStream --> AIMessageChunk
    AIMessageChunk --> BaseMessageChunk
    MediaPayload --> FormatContentBlockXML

    classDef class fill:none,stroke:#000,stroke-width:1px;
    classDef function fill:none,stroke:#000,stroke-width:1px;
```

*Sources: [libs/core/langchain_core/messages/ai.py](), [libs/core/langchain_core/messages/utils.py:142-205]()



---

## 3. Model Profiles & Metadata

### ModelProfile
- **Definition**: A data model schema describing characteristics and capabilities of a language model including token limits, supported input/output modalities, and feature flags (structured output, tool calling, reasoning).
- **Usage**: Enables runtime model selection and feature detection in agents and runtime components.
- **Code Pointer**: Typically auto-generated in partner packages under `data/_profiles.py` such as `libs/partners/openrouter/langchain_openrouter/data/_profiles.py`, following schema definitions in `libs/core/langchain_core/language_models/model_profile.py` (not fully shown here).

### output_version
- **Definition**: A version tag for response formats from chat models (commonly OpenAI-based) to track breaking changes or extensions in API schemas.
- **Usage**: Helps differentiate and maintain compatibility with evolving provider APIs and SDKs.
- **Code Pointer**: Managed internally in provider integration code such as `libs/partners/openai/langchain_openai`.

### augmentations
- **Definition**: TOML configuration files used to augment or override auto-generated model profile data with manual capabilities or feature flags (e.g., `profile_augmentations.toml`).
- **Usage**: Applied at generation/build time using the `langchain-profiles` CLI tool to enhance model metadata.
- **Code Pointer**: Typically found within partner data directories (e.g., `libs/partners/openai/langchain_openai/data/profile_augmentations.toml`) and referred by profile-generation logic.

---

## 4. Agents & Execution

### middleware
- **Definition**: Middleware are modular plugins intercepting agent runtime lifecycle phases to influence state, logic, retries, limits, fallback models, summarization, PII redaction, and tool selection.
- **Implementation**: Middleware subclasses implement `AgentMiddleware` interface with hooks like:
  - `wrap_model_call`: Wraps or replaces the invocation of the underlying chat model.
  - `wrap_tool_call`: Wraps or replaces the execution of a tool call.
  
  Middleware are composed in a pipeline to modify inputs and outputs dynamically.
- **Code Pointer**: Types and interfaces in `libs/langchain_v1/langchain/agents/middleware/types.py:87-106`, middleware registrations and exports in `libs/langchain_v1/langchain/agents/middleware/__init__.py:31-51`.

### tool_node
- **Definition**: The graph execution node in `langgraph` that orchestrates resolving and executing tool calls invoked by the model during agent execution.
- **Usage**: Enables execution of BaseTool or dict-defined tools dynamically within agent runnable graphs.
- **Code Pointer**: Created within agent factory in `libs/langchain_v1/langchain/agents/factory.py:35`

```mermaid
title Agent Middleware & Tool Node Execution
graph TD
    subgraph NL["Agent Execution & Interception"]
        direction TB
        AgentRequest["Agent Request Interception"] --> MiddlewarePipeline["Middleware Hook Pipeline"]
        ToolCallExec["Model-Initiated Tool Call Execution"] --> ToolNodeExec["ToolNode Execution in LangGraph"]
    end

    subgraph CodeEntities["Code Entities"]
        direction TB
        AgentMiddleware["AgentMiddleware"]
        ModelRequest["ModelRequest"]
        ToolNode["ToolNode"]
    end

    AgentRequest --> AgentMiddleware
    AgentRequest --> ModelRequest
    ToolCallExec --> ToolNodeExec

    classDef class fill:none,stroke:#000,stroke-width:1px;
```

*Sources: [libs/langchain_v1/langchain/agents/middleware/types.py:87-106](), [libs/langchain_v1/langchain/agents/middleware/__init__.py:31-51](), [libs/langchain_v1/langchain/agents/factory.py:30-38]()


---

## 5. Testing & Infrastructure

### standard tests
- **Definition**: A reusable, comprehensive suite of conformance and integration tests validating chat models, tools, retrievers, vector stores, and stores against LangChain interface contracts.
- **Implementation**: Pytest framework with fixtures and snapshots supporting partner and core packages.
- **Code Pointer**: Located in the `libs/standard-tests` package.

### cassette
- **Definition**: Recorded API interaction files used in testing to replay and mock external HTTP calls to language model providers, enabling offline and consistent integration tests.
- **Implementation**: Usually YAML or JSON files managed by VCR.py or similar libraries.
- **Code Pointer**: Found in partner test directories such as `libs/partners/openai/tests/`

---

# Summary Table of Key Terms and Locations

| Term             | Role / Description                               | Primary Code Location(s)                             |
|------------------|-------------------------------------------------|----------------------------------------------------|
| Runnable         | Abstract composable work unit                    | `libs/core/langchain_core/runnables/base.py:133`   |
| LCEL             | Runnable composition language & constructs      | `libs/core/langchain_core/runnables/base.py:161`   |
| RunnableConfig   | Runtime config used by Runnables                 | `libs/core/langchain_core/runnables/config.py`     |
| AIMessageChunk   | Incremental AI streaming message chunk           | `libs/core/langchain_core/messages/ai.py`          |
| ContentBlock     | Typed dictionary representing message content    | `libs/core/langchain_core/messages/utils.py:142-205` |
| ModelProfile     | Model capabilities metadata                       | `libs/partners/*/data/_profiles.py`                 |
| output_version   | Version tag for response API formats              | Provider-specific (e.g., OpenAI integrations)      |
| augmentations    | TOML overrides for model profiles                 | Partner data directories with profile augmentations|
| middleware       | Agent lifecycle interception plugins              | `libs/langchain_v1/langchain/agents/middleware/`   |
| tool_node        | Execution node for resolving model-invoked tools | `libs/langchain_v1/langchain/agents/factory.py:35` |
| standard tests   | Interface and conformance test suite               | `libs/standard-tests/`                              |
| cassette         | Recorded network interactions for test mocking    | `libs/partners/*/tests/`                            |

---

This glossary bridges the conceptual natural language AI domain to precise code entities in LangChain, providing developers and integrators detailed understanding of architecture and interfaces.

*Sources: [libs/core/langchain_core/runnables/base.py:133-212](), [libs/core/langchain_core/runnables/config.py](), [libs/core/langchain_core/messages/ai.py](), [libs/core/langchain_core/messages/utils.py:142-205](), [libs/langchain_v1/langchain/agents/middleware/types.py:87-106](), [libs/langchain_v1/langchain/agents/middleware/__init__.py:31-51](), [libs/langchain_v1/langchain/agents/factory.py:30-38]()*