<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langchainjs · page 4 Classic Package (@langchain/classic) · fetched 2026-10-26 -->

# Classic Package (@langchain/classic)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/langchain-classic/src/chat_models/universal.ts](libs/langchain-classic/src/chat_models/universal.ts)
- [libs/langchain-classic/src/hub/index.ts](libs/langchain-classic/src/hub/index.ts)
- [libs/langchain-classic/src/hub/node.ts](libs/langchain-classic/src/hub/node.ts)
- [libs/langchain-classic/src/hub/tests/inferModelProviderFromNamespace.test.ts](libs/langchain-classic/src/hub/tests/inferModelProviderFromNamespace.test.ts)
- [libs/langchain-classic/src/load/index.ts](libs/langchain-classic/src/load/index.ts)
- [libs/langchain-core/src/load/index.ts](libs/langchain-core/src/load/index.ts)
- [libs/langchain-core/src/load/serializable.ts](libs/langchain-core/src/load/serializable.ts)
- [libs/langchain-core/src/load/tests/index.test.ts](libs/langchain-core/src/load/tests/index.test.ts)
- [libs/langchain-core/src/load/validation.ts](libs/langchain-core/src/load/validation.ts)
- [libs/langchain-core/src/runnables/base.ts](libs/langchain-core/src/runnables/base.ts)
- [libs/langchain-core/src/runnables/history.ts](libs/langchain-core/src/runnables/history.ts)
- [libs/langchain/src/hub/base.ts](libs/langchain/src/hub/base.ts)
- [libs/langchain/src/hub/index.ts](libs/langchain/src/hub/index.ts)
- [libs/langchain/src/hub/node.ts](libs/langchain/src/hub/node.ts)
- [libs/langchain/src/hub/tests/hub.int.test.ts](libs/langchain/src/hub/tests/hub.int.test.ts)
- [libs/langchain/src/hub/tests/inferModelProviderFromNamespace.test.ts](libs/langchain/src/hub/tests/inferModelProviderFromNamespace.test.ts)
- [libs/langchain/src/load/index.ts](libs/langchain/src/load/index.ts)
- [libs/langchain/src/load/tests/load.test.ts](libs/langchain/src/load/tests/load.test.ts)

</details>



The `@langchain/classic` package serves as a high-level framework containing legacy implementations of core LangChain concepts such as chains, agents, memory, retrievers, vector store wrappers, and evaluation components. This package is designed to provide a comprehensive set of tools for building LLM-powered applications, often leveraging abstractions from `@langchain/core`.

This page provides a high-level overview of the `@langchain/classic` package. For detailed information on specific components, refer to the linked child pages.

---

## Chains and Legacy Agents

The `@langchain/classic` package includes various chain abstractions, such as `BaseChain`, `LLMChain`, SQL chains, and retrieval QA chains, which are fundamental building blocks for complex LLM applications. It also houses legacy agent implementations and toolkits that enable LLMs to interact with external environments.

Furthermore, this package provides a universal chat model loader, `initChatModel`, which dynamically imports and instantiates chat models from various providers based on configuration [libs/langchain-classic/src/chat_models/universal.ts:202-227](). This allows for flexible model switching without hardcoding provider-specific imports. The package also supports integration with the LangChain Hub for prompt management and dynamic loading of models associated with hub prompts [libs/langchain/src/hub/node.ts:131-162]().

For a deeper dive into the chain abstractions and legacy agent implementations, see [Chains and Legacy Agents](#4.1).

### Universal Chat Model Loading

The `initChatModel` function in `universal.ts` acts as a factory for chat models. It uses a `MODEL_PROVIDER_CONFIG` map to determine the correct package and class name for a given model provider [libs/langchain-classic/src/chat_models/universal.ts:52-126]().

```mermaid
graph TD
    A[User Request: initChatModel("gpt-4", "openai")] --> B{_inferModelProvider("gpt-4")}
    B --> C{MODEL_PROVIDER_CONFIG["openai"]}
    C --> D[getChatModelByClassName("ChatOpenAI", "openai")]
    D --> E{Dynamic Import: @langchain/openai}
    E --> F[Instantiate ChatOpenAI]
    F --> G[Return ChatOpenAI Instance]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#f9f,stroke:#333,stroke-width:2px
```
**Sources:**
- [libs/langchain-classic/src/chat_models/universal.ts:52-126]()
- [libs/langchain-classic/src/chat_models/universal.ts:145-195]()
- [libs/langchain-classic/src/chat_models/universal.ts:202-227]()

### LangChain Hub Integration

The `pull` function in `@langchain/classic/hub/node.ts` allows fetching prompts from the LangChain Hub. It can optionally instantiate a chat model if the prompt metadata specifies one, leveraging the `getChatModelByClassName` and `inferModelProviderFromNamespace` functions to dynamically load the correct provider package [libs/langchain/src/hub/node.ts:131-162]().

```mermaid
graph TD
    A[User Calls pull("owner/repo", { includeModel: true })] --> B{basePull("owner/repo")}
    B --> C[Get Prompt Manifest]
    C --> D{Check for Model Metadata in Manifest}
    D -- "Model Found" --> E{inferModelProviderFromNamespace(model.id)}
    E --> F{getChatModelByClassName(modelName, modelProvider)}
    F --> G[Load Model Class Dynamically]
    G --> H[Instantiate Model]
    H --> I[load(promptManifest, ..., modelImportMap)]
    I --> J[Return Loaded Runnable with Model]
    D -- "No Model" --> I
```
**Sources:**
- [libs/langchain/src/hub/node.ts:131-162]()
- [libs/langchain/src/hub/node.ts:156-162]()
- [libs/langchain/src/hub/node.ts:44-98]()
- [libs/langchain-classic/src/chat_models/universal.ts:145-195]()
- [libs/langchain-classic/src/hub/tests/inferModelProviderFromNamespace.test.ts:6-160]()

---

## Retrievers, Vector Store Wrappers, and Indexing

This section covers classic retriever implementations, such as self-query, multi-query, and contextual compression retrievers, which are crucial for efficient information retrieval from various data sources. It also includes document compressors that optimize the content passed to LLMs. The package provides base wrappers for integrating with different vector stores and offers an indexing API for managing and querying vector databases.

For detailed information on these components, see [Retrievers, Vector Store Wrappers, and Indexing](#4.2).

---

## Document Loaders and Text Splitters

The `@langchain/classic` package provides a collection of classic document loaders for ingesting data from diverse formats and sources. Complementing these loaders, the `@langchain/textsplitters` package (which is often used in conjunction with `@langchain/classic`) offers robust text splitting functionalities, including `RecursiveCharacterTextSplitter` and `TokenTextSplitter`, to prepare documents for processing by LLMs.

For more information on document loaders and text splitters, see [Document Loaders and Text Splitters](#4.3).

---

## Memory, Storage, and Caches

This part of the package deals with managing conversational memory, providing various chat message history backends. It also includes key-value stores for persistent storage, with implementations for file system, in-memory, and encoder-backed storage. Additionally, `@langchain/classic` offers LLM caching mechanisms, including those backed by MongoDB and Redis, to improve performance and reduce costs.

The `RunnableWithMessageHistory` class, though deprecated in favor of LangGraph's persistence, demonstrates how memory was integrated with runnables to manage chat history [libs/langchain-core/src/runnables/history.ts:106-152]().

For detailed information on memory, storage, and caching mechanisms, see [Memory, Storage, and Caches](#4.4).

---

## Serialization and Deserialization

The `@langchain/classic` package, like other LangChain packages, relies on the serialization and deserialization mechanisms provided by `@langchain/core`. The `load` function is critical for re-instantiating LangChain objects from their serialized representations.

```typescript
import { load } from "@langchain/classic/load";

// Example of loading a serialized chain
const serializedChain = `{"lc":1,"type":"constructor","id":["langchain","chains","llm","LLMChain"],"kwargs":{"prompt":{"lc":1,"type":"constructor","id":["langchain","prompts","prompt","PromptTemplate"],"kwargs":{"input_variables":["question"],"template":"What is {question}?"}},"llm":{"lc":1,"type":"constructor","id":["langchain","chat_models","openai","ChatOpenAI"],"kwargs":{"temperature":0.7}}}}`;

async function loadMyChain() {
  const chain = await load(serializedChain);
  console.log(chain);
}

loadMyChain();
```
**Sources:**
- [libs/langchain-classic/src/load/index.ts:24-41]()
- [libs/langchain-core/src/load/index.ts:1-157]()
- [libs/langchain-core/src/load/serializable.ts:97-175]()
- [libs/langchain-core/src/load/validation.ts:112-166]()

It's important to note the security implications of deserialization. The `load()` function can instantiate classes and invoke constructors based on the input, posing a risk if used with untrusted data [libs/langchain-classic/src/load/index.ts:11-14](). The system includes mechanisms to prevent secret injection and ensure safe deserialization by escaping user-provided objects and requiring explicit secret maps [libs/langchain-core/src/load/validation.ts:100-147](), [libs/langchain-core/src/load/tests/index.test.ts:19-31]().

**Sources:**
- [libs/langchain-classic/src/load/index.ts:11-14]()
- [libs/langchain-core/src/load/index.ts:83-157]()
- [libs/langchain-core/src/load/validation.ts:100-147]()
- [libs/langchain-core/src/load/tests/index.test.ts:19-31]()

---

