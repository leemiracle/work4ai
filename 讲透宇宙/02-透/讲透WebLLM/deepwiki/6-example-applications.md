> 来源: [https://deepwiki.com/mlc-ai/web-llm/6-example-applications](https://deepwiki.com/mlc-ai/web-llm/6-example-applications)
> DeepWiki mlc-ai/web-llm | Last indexed: 18 April 2025 (632d34

# Example Applications

  Relevant source files 
 - [examples/README.md](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1)
 - [examples/cache-usage/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/cache-usage/package.json)
 - [examples/embeddings/README.md](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/embeddings/README.md?plain=1)
 - [examples/embeddings/src/embeddings.html](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/embeddings/src/embeddings.html)
 - [examples/embeddings/src/embeddings.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/embeddings/src/embeddings.ts)
 - [examples/get-started-web-worker/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/get-started-web-worker/package.json)
 - [examples/json-mode/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/json-mode/package.json)
 - [examples/multi-round-chat/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/multi-round-chat/package.json)
 - [examples/next-simple-chat/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/next-simple-chat/package.json)
 - [examples/seed-to-reproduce/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/seed-to-reproduce/package.json)
 - [examples/streaming/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/streaming/package.json)
 
  
## Purpose and Scope

 This document provides an overview of the example applications included in the WebLLM repository. These examples demonstrate practical implementations of WebLLM for various use cases, from simple chat interfaces to advanced capabilities like embeddings and browser extensions. They serve as reference implementations that developers can use to build their own applications.

 For details on the core components used in these examples, see [Core Components](https://deepwiki.com/mlc-ai/web-llm/2-core-components). For information about worker integrations demonstrated in some examples, see [Worker Integrations](https://deepwiki.com/mlc-ai/web-llm/3-worker-integrations).

 
## Example Categories Overview

 WebLLM provides a diverse set of example applications organized into several categories:

 
```

```

 Sources: [examples/README.md1-52](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L1-L52)

 
## Example Application Structure

 Most example applications in the repository follow a similar structure, where the application code uses the WebLLM library to create an MLCEngine instance, load models, and interact with them through the provided APIs:

 
```

```

 Sources: [examples/README.md1-52](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L1-L52)

 
## Basic Examples

 
### Get Started Examples

 WebLLM provides several minimal "get started" examples to demonstrate basic usage:

 
 - **get-started**: A minimal example showing chat completion functionality
 - **get-started-web-worker**: Similar to get-started, but running the model in a web worker
 
 These examples demonstrate how to initialize the MLCEngine, load a model, and perform basic chat completion operations.

 
```

```

 Sources: [examples/README.md12-14](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L12-L14) [examples/README.md23](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L23-L23)

 
### Simple Chat Applications

 WebLLM includes complete chat application examples implemented in different programming languages:

 
 - **simple-chat-js**: A complete chat bot application in vanilla JavaScript
 - **simple-chat-ts**: A complete chat bot application in TypeScript
 - **simple-chat-upload**: Demonstrates how to upload local models instead of downloading from URLs
 
 These examples showcase a typical chat interface with model selection, conversation history, and streaming responses.

 Sources: [examples/README.md17-22](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L17-L22) [examples/README.md52-53](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L52-L53)

 
## Framework Integrations

 
### Next.js Integration

 The `next-simple-chat` example demonstrates how to integrate WebLLM into a Next.js application. This example is particularly useful for developers who want to build production-ready web applications with WebLLM.

 
```

```

 Sources: [examples/next-simple-chat/package.json1-27](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/next-simple-chat/package.json#L1-L27) [examples/README.md24](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L24-L24)

 
## Advanced API Capabilities

 WebLLM provides examples demonstrating various advanced API capabilities that mirror the OpenAI API:

 
### Streaming Example

 The `streaming` example demonstrates how to receive model outputs in real-time using asynchronous generators, enhancing the user experience for chat applications.

 Sources: [examples/streaming/package.json1-21](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/streaming/package.json#L1-L21) [examples/README.md34-35](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L34-L35)

 
### JSON Mode and Schema

 The `json-mode` and `json-schema` examples show how to:

 
 - Ensure model outputs are in JSON format
 - Validate outputs against specific JSON schemas
 - Use structured data from LLM responses in applications
 
 Sources: [examples/json-mode/package.json1-21](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/json-mode/package.json#L1-L21) [examples/README.md36-37](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L36-L37)

 
### Multi-round Chat

 The `multi-round-chat` example demonstrates optimized multi-turn conversations that reuse KV cache for better performance.

 Sources: [examples/multi-round-chat/package.json1-21](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/multi-round-chat/package.json#L1-L21) [examples/README.md25-26](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L25-L26)

 
### Other Advanced Features

 Additional examples showcase:

 
 - **seed-to-reproduce**: Using seed values for reproducible outputs
 - **function-calling**: Implementing function calling capabilities
 - **vision-model**: Processing requests with image inputs using Vision Language Models
 
 Sources: [examples/seed-to-reproduce/package.json1-21](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/seed-to-reproduce/package.json#L1-L21) [examples/README.md38-40](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L38-L40)

 
## Browser Extension Examples

 WebLLM can be integrated into browser extensions, enabling AI capabilities directly within the browser context:

 
 - **chrome-extension**: A basic Chrome extension without a persistent background
 - **chrome-extension-webgpu-service-worker**: A Chrome extension using service workers for a persistent background
 
 
```

```

 Sources: [examples/README.md43-45](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L43-L45)

 
## Special Use Cases

 
### Embeddings and RAG

 The `embeddings` example demonstrates:

 
 - Using WebLLM's embedding capabilities
 - Integration with Langchain.js
 - Implementing Retrieval-Augmented Generation (RAG) with WebLLM
 
 
```

```

 The example shows how to create a custom `WebLLMEmbeddings` class that implements Langchain's `EmbeddingsInterface`, allowing WebLLM to be used for both embeddings and LLM generation in a RAG pipeline.

 Sources: [examples/embeddings/src/embeddings.ts1-212](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/embeddings/src/embeddings.ts#L1-L212) [examples/README.md27-28](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L27-L28)

 
### Cache Management

 The `cache-usage` example demonstrates WebLLM's caching capabilities:

 
 - Support for both Cache API and IndexedDB cache
 - Cache configuration options
 - Utilities for checking, deleting, and managing cached models
 
 
```

```

 Sources: [examples/cache-usage/package.json1-21](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/cache-usage/package.json#L1-L21) [examples/README.md49-52](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L49-L52)

 
### Other Special Examples

 Additional specialized examples include:

 
 - **multi-models**: Loading multiple models concurrently in a single engine
 - **logit-processor**: Implementing custom token generation rules using logit processing
 
 Sources: [examples/README.md28-29](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L28-L29) [examples/README.md48-49](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L48-L49)

 
## Example Usage Patterns

 The example applications demonstrate several common usage patterns for WebLLM:

 
```

```

 Sources: [examples/README.md1-52](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/README.md?plain=1#L1-L52)

 
## Conclusion

 The example applications in the WebLLM repository provide developers with practical reference implementations for a wide range of use cases. From basic chat interfaces to advanced capabilities like embeddings and browser extensions, these examples demonstrate how to leverage WebLLM's features in real-world applications. Developers can use these examples as starting points for their own projects, adapting and extending them as needed.

 For more information on specific components used in these examples, refer to the documentation on [Core Components](https://deepwiki.com/mlc-ai/web-llm/2-core-components) and [API Reference](https://deepwiki.com/mlc-ai/web-llm/4-api-reference).
