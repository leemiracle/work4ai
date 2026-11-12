<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langchain · page 2 langchain-core Architecture · fetched 2026-10-26 -->

# langchain-core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/core/langchain_core/callbacks/base.py](libs/core/langchain_core/callbacks/base.py)
- [libs/core/langchain_core/callbacks/manager.py](libs/core/langchain_core/callbacks/manager.py)
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
- [libs/core/langchain_core/version.py](libs/core/langchain_core/version.py)
- [libs/core/pyproject.toml](libs/core/pyproject.toml)
- [libs/core/tests/unit_tests/callbacks/test_sync_callback_manager.py](libs/core/tests/unit_tests/callbacks/test_sync_callback_manager.py)
- [libs/core/tests/unit_tests/runnables/__snapshots__/test_fallbacks.ambr](libs/core/tests/unit_tests/runnables/__snapshots__/test_fallbacks.ambr)
- [libs/core/tests/unit_tests/runnables/__snapshots__/test_runnable.ambr](libs/core/tests/unit_tests/runnables/__snapshots__/test_runnable.ambr)
- [libs/core/tests/unit_tests/runnables/test_config.py](libs/core/tests/unit_tests/runnables/test_config.py)
- [libs/core/tests/unit_tests/runnables/test_configurable.py](libs/core/tests/unit_tests/runnables/test_configurable.py)
- [libs/core/tests/unit_tests/runnables/test_fallbacks.py](libs/core/tests/unit_tests/runnables/test_fallbacks.py)
- [libs/core/tests/unit_tests/runnables/test_runnable.py](libs/core/tests/unit_tests/runnables/test_runnable.py)
- [libs/core/tests/unit_tests/runnables/test_utils.py](libs/core/tests/unit_tests/runnables/test_utils.py)
- [libs/core/uv.lock](libs/core/uv.lock)

</details>





## Purpose and Scope

The `langchain-core` package serves as the foundational abstraction layer for the LangChain ecosystem [libs/core/README.md:1-21](). It defines modular, decoupled interfaces that enable seamless interoperability between model providers, tool developers, and framework components. This architecture abstracts core concepts such as execution units (Runnables), conversational messages, language models, prompts, tools, outputs, tracing, and retrieval primitives, providing a stable base for the rest of LangChain.

This page offers a high-level overview of these core abstractions and their relationships. Detailed technical content is available on dedicated child pages listed at the end.

---

## 2.1. Runnables and LCEL

At the core is the `Runnable` interface, representing a unit of executable work that can be invoked synchronously or asynchronously, batched, or streamed. It supports functional composition with operators like `|` (producing `RunnableSequence`) and mappings (producing `RunnableParallel`) to build complex execution pipelines [libs/core/langchain_core/runnables/base.py:133-197]().

Runnables are configurable via `RunnableConfig`, which propagates runtime metadata such as tags, concurrency limits, callbacks, and recursion limits dynamically through execution contexts [libs/core/langchain_core/runnables/config.py:57-78](). They support retries (`RunnableRetry`), fallbacks (`RunnableWithFallbacks`), and customizable configurable fields for flexible behavior [libs/core/langchain_core/fallbacks.py:37-66](), [libs/core/langchain_core/runnables/configurable.py:50-55](). Rate limiting is implemented via components such as the `InMemoryRateLimiter` [libs/core/rate_limiters.py:67-75]().

Runnables also provide introspection for graph construction and support rendering their execution graphs visually using Mermaid or other formats, aiding debugging and understanding of pipeline structures [libs/core/langchain_core/runnables/base.py:104-106]().

For more details, see [Runnables and LCEL](#2.1).

### LCEL Execution Flow Architecture

```mermaid
graph TD
    "UserInput" --> ["RunnableSequence"]
    ["RunnableSequence"] --> ["RunnableParallel"]
    ["RunnableParallel"] --> |"BranchA"| ["ChatOpenAI"]
    ["RunnableParallel"] --> |"BranchB"| ["StructuredTool"]
    ["ChatOpenAI"] --> ["RunnableRetry"]
    ["RunnableRetry"] --> ["InMemoryRateLimiter"]
```

Sources: `[libs/core/langchain_core/runnables/base.py:133-197]`, `[libs/core/langchain_core/runnables/config.py:57-78]`, `[libs/core/langchain_core/fallbacks.py:37-66]`, `[libs/core/rate_limiters.py:67-75]`

### 2.1.1. Graph Rendering and Visualization

Runnable compositions expose their graph structure which can be rendered in multiple formats including Mermaid diagrams, ASCII art, or PNG images. This feature helps visualize the sequencing and parallelism in the execution pipeline [libs/core/langchain_core/runnables/base.py:104-106]().

See [Graph Rendering and Visualization](#2.1.1) for implementation specifics.

Sources: `[libs/core/langchain_core/runnables/base.py:104-106]`

### 2.1.2. Streaming, Events and Chat History Runnables

Streaming methods (`astream_events` v1/v2) emit intermediate results progressively during execution, enabling reactive consumption of outputs. Stateful wrappers like `RunnableWithMessageHistory` integrate chat message history management with runnable execution to provide conversational context [libs/core/langchain_core/runnables/base.py:87-94](), [libs/core/callbacks/base.py:128-154]().

Details on streaming and chat-aware runnables are covered in [Streaming, Events and Chat History Runnables](#2.1.2).

Sources: `[libs/core/langchain_core/runnables/base.py:87-94]`, `[libs/core/callbacks/base.py:128-154]`

---

## 2.2. Messages and Content Blocks

Conversation in LangChain is modeled via the `BaseMessage` class hierarchy, with subclasses such as `HumanMessage`, `AIMessage`, `SystemMessage`, and `ToolMessage`. These message types encapsulate content, metadata, and support chunk merging for efficient streaming and resumption [libs/core/tests/unit_tests/runnables/test_runnable.py:46-47](). Messages also track token usage metadata for billing and monitoring purposes.

Underlying message content is organized as `ContentBlock`s, facilitating multi-modal and structured inputs to be seamlessly handled.

Refer to [Messages and Content Blocks](#2.2) for exhaustive details.

Sources: `[libs/core/tests/unit_tests/runnables/test_runnable.py:46-47]`

---

### 2.2.1. Block Translators for Providers

LangChain includes standardized content block translators that normalize conversational content and tool calls across different model providers, including OpenAI, Anthropic, Google GenAI, Bedrock, and Groq. This harmonization supports multi-provider interoperability and consistent event streaming [libs/core/callbacks/base.py:128-154]().

See [Block Translators for Providers](#2.2.1).

Sources: `[libs/core/callbacks/base.py:128-154]`

---

## 2.3. Language Model Base Classes

Base classes like `BaseChatModel` and `BaseLLM` define the interface for language model providers. They manage lifecycle operations such as invocation, prompt formatting, caching, streaming bridging, and maintenance of model metadata/profiles. These abstractions ensure that any concrete language model implementation can plug into runnable pipelines transparently [libs/core/tests/unit_tests/runnables/test_runnable.py:38-43]().

Implementation details and extension points reside in [Language Model Base Classes](#2.3).

Sources: `[libs/core/tests/unit_tests/runnables/test_runnable.py:38-43]`

---

## 2.4. Tools and Function Calling

Tools represent external capabilities and integrations within LangChain, formalized via classes like `BaseTool` and `StructuredTool`. The `@tool` decorator wraps Python callables to define argument schemas, enable injected arguments, and support structured invocation. This facilitates reliable function calling from language models with strict typing and validation [libs/core/tests/unit_tests/runnables/test_runnable.py:86]().

Tools naturally integrate with runnable execution graphs and messaging.

For more insight, see [Tools and Function Calling](#2.4).

### Model and Tool Integration Mapping

```mermaid
graph TD
    "UserPrompt" --> ["BaseChatModel"]
    ["BaseChatModel"] --> |"ToolCall"| ["StructuredTool"]
    ["StructuredTool"] --> ["ToolMessage"]
    ["ToolMessage"] --> ["BaseChatModel"]
```

Sources: `[libs/core/tests/unit_tests/runnables/test_runnable.py:86]`

---

## 2.5. Prompts and Example Selectors

Prompt construction is handled via `PromptTemplate` and `ChatPromptTemplate`. They support mustache or Python f-string formatting, few-shot prompting, and example selectors for dynamically choosing contextual examples. These facilities enable intricate prompt engineering within runnable chains [libs/core/tests/unit_tests/runnables/test_runnable.py:56-62]().

Explore the details in [Prompts and Example Selectors](#2.5).

Sources: `[libs/core/tests/unit_tests/runnables/test_runnable.py:56-62]`

---

## 2.6. Outputs, Output Parsers and Callbacks

Model outputs return structured types such as `Generation` and `ChatResult`. Output parsers—including JSON, XML, Pydantic model parsers, and tool-call parsers—convert raw outputs into usable Python objects. The `CallbackManager` orchestrates telemetry, usage monitoring, logging, and lifecycle event handling for runs [libs/core/callbacks/manager.py:55-98]().

See [Outputs, Output Parsers and Callbacks](#2.6) for in-depth information.

Sources: `[libs/core/callbacks/manager.py:55-98]`, `[libs/core/tests/unit_tests/runnables/test_runnable.py:48-52]`

---

## 2.7. Tracing and LangSmith Integration

Tracing infrastructure uses `BaseTracer` and the `LangChainTracer` to record execution runs with rich metadata, context propagation tokens, and gateway-specific data. Traces are schema-validated and exported to LangSmith for visualization and analysis of application runs [libs/core/tests/unit_tests/runnables/test_runnable.py:127-145]().

Details are found in [Tracing and LangSmith Integration](#2.7).

Sources: `[libs/core/tests/unit_tests/runnables/test_runnable.py:127-145]`

---

## 2.8. Retrieval Primitives: Documents, Vector Stores, Indexing

Retrieval abstractions unify document formats (`Document`, `Blob`), loading pipelines, embedding interfaces, vector stores (including `InMemoryVectorStore`), retrievers, and indexing APIs. This foundation supports building search, memory, and knowledge retrieval layers for LangChain applications [libs/core/tests/unit_tests/runnables/test_runnable.py:37]().

See [Retrieval Primitives: Documents, Vector Stores, Indexing](#2.8) for complete coverage.

Sources: `[libs/core/tests/unit_tests/runnables/test_runnable.py:37]`

---

## 2.9. Core Infrastructure: Serialization, Caches, Utils, Security

The core infrastructure layer contains serialization frameworks for saving/loading components with version schema, caching systems, global state management, Pydantic utilities, decorators for deprecation and beta features, SSRF protection, and system/environment info utilities [libs/core/tests/unit_tests/runnables/test_runnable.py:44-45]().

Refer to [Core Infrastructure: Serialization, Caches, Utils, Security](#2.9).

Sources: `[libs/core/tests/unit_tests/runnables/test_runnable.py:44-45]`

---

## Bridging Natural Language Space to Code Entities

The following diagrams illustrate how LangChain concepts bridge from natural language user interactions to concrete runnable and model classes in code, providing insight into the system architecture and flow.

### Conceptual Mapping: Natural Language Interaction to Runnable Execution

```mermaid
graph TD
    "UserInput:<NL_Message>" --> ["RunnableSequence:<ChatPromptTemplate>"]
    ["RunnableSequence:<ChatPromptTemplate>"] --> ["RunnableParallel:<ToolBranch><LLMBranch>"]
    ["RunnableParallel:<ToolBranch>"] --> ["StructuredTool:<BaseTool>"]
    ["RunnableParallel:<LLMBranch>"] --> ["BaseChatModel:<ProviderModel>"]
    ["BaseChatModel:<ProviderModel>"] --> ["RunnableWithFallbacks:<Retry/FallbackLogic>"]
    ["RunnableWithFallbacks:<Retry/FallbackLogic>"] --> ["RunnableRetry:<RetryPolicy>"]
    ["RunnableRetry:<RetryPolicy>"] --> ["InMemoryRateLimiter:<RateLimiting>"]
```

Sources: `[libs/core/langchain_core/runnables/base.py:133-197]`, `[libs/core/langchain_core/fallbacks.py:37-66]`, `[libs/core/langchain_core/runnables/retry.py:48-55]`, `[libs/core/rate_limiters.py:67-75]`

### Provider Messaging Flow in Code

```mermaid
graph TD
    "UserPrompt:<HumanMessage>" --> ["BaseChatModel:<_call_methods>"]
    ["BaseChatModel:<_call_methods>"] --> |"ToolCall"| ["StructuredTool:<@tool_decorator>"]
    ["StructuredTool:<@tool_decorator>"] --> ["ToolMessage:<ToolMessage>"]
    ["ToolMessage:<ToolMessage>"] --> ["BaseChatModel:<_streaming_call>"]
```

Sources: `[libs/core/tests/unit_tests/runnables/test_runnable.py:86]`

---

This overview presents `langchain-core` as a modular, composable platform that bridges human language inputs to code-level abstractions, enabling robust, scalable, and extensible large language model applications.

For detailed technical information, please consult the following child pages:

- [Runnables and LCEL](#2.1)
- [Messages and Content Blocks](#2.2)
- [Language Model Base Classes](#2.3)
- [Tools and Function Calling](#2.4)
- [Prompts and Example Selectors](#2.5)
- [Outputs, Output Parsers and Callbacks](#2.6)
- [Tracing and LangSmith Integration](#2.7)
- [Retrieval Primitives: Documents, Vector Stores, Indexing](#2.8)
- [Core Infrastructure: Serialization, Caches, Utils, Security](#2.9)

---

