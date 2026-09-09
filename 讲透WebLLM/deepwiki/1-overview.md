> 来源: [https://deepwiki.com/mlc-ai/web-llm/1-overview](https://deepwiki.com/mlc-ai/web-llm/1-overview)
> DeepWiki mlc-ai/web-llm | Last indexed: 18 April 2025 (632d34

# Overview

  Relevant source files 
 - [README.md](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1)
 - [examples/chrome-extension-webgpu-service-worker/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/chrome-extension-webgpu-service-worker/package.json)
 - [examples/chrome-extension/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/chrome-extension/package.json)
 - [examples/get-started/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/get-started/package.json)
 - [examples/logit-processor/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/logit-processor/package.json)
 - [package-lock.json](https://github.com/mlc-ai/web-llm/blob/632d3472/package-lock.json)
 - [package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json)
 - [site/_config.yml](https://github.com/mlc-ai/web-llm/blob/632d3472/site/_config.yml)
 - [site/index.md](https://github.com/mlc-ai/web-llm/blob/632d3472/site/index.md?plain=1)
 - [utils/vram_requirements/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/utils/vram_requirements/package.json)
 
  WebLLM is a high-performance in-browser language model inference engine that enables running LLMs directly in web browsers with WebGPU hardware acceleration. It allows developers to deploy and run language models client-side without requiring server support, enhancing privacy, reducing costs, and enabling personalized AI experiences.

 This page provides a general overview of WebLLM, its architecture, and key components. For detailed information about specific components, refer to their respective wiki pages.

 
 - For detailed architecture information, see [Architecture](https://deepwiki.com/mlc-ai/web-llm/1.1-architecture)
 - For getting started quickly, see [Getting Started](https://deepwiki.com/mlc-ai/web-llm/1.2-getting-started)
 - For core components documentation, see [Core Components](https://deepwiki.com/mlc-ai/web-llm/2-core-components)
 - For worker integrations, see [Worker Integrations](https://deepwiki.com/mlc-ai/web-llm/3-worker-integrations)
 
 Sources: [README.md17-25](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L17-L25) [package.json1-7](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L1-L7)

 
## What is WebLLM?

 WebLLM is an open-source project that brings language model inference directly to web browsers. It leverages WebGPU for hardware acceleration and provides a fully compatible OpenAI-style API for interacting with language models. The project allows running various open-source models such as Llama 3, Phi 3, Gemma, Mistral, and Qwen directly in the browser, completely client-side.

 As an npm package (`@mlc-ai/web-llm`), WebLLM provides a modular interface for integrating LLMs into web applications with minimal effort while maximizing performance.

 
```

```

 Sources: [README.md10-16](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L10-L16) [README.md17-26](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L17-L26) [README.md34-53](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L34-L53) [site/index.md9-18](https://github.com/mlc-ai/web-llm/blob/632d3472/site/index.md?plain=1#L9-L18)

 
## Core System Architecture

 WebLLM follows a modular architecture centered around the `MLCEngine`, which serves as the primary interface for applications. The system consists of several key components that handle different aspects of model loading, inference, and interaction.

 
```

```

 The system architecture can be divided into three main layers:

 
 - **Application Layer**: Client applications that use WebLLM, interacting through an OpenAI-compatible API
 - **Core Engine**: The main components of WebLLM including the MLCEngine, chat system, and worker integrations
 - **Runtime Layer**: Lower-level components that handle WebGPU acceleration, tokenization, and caching
 
 Sources: [README.md35-53](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L35-L53) [src/engine.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/engine.ts) [src/config.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/config.ts) [src/llm_chat.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/llm_chat.ts) [src/web_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts) [src/service_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/service_worker.ts) [src/embedding.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/embedding.ts)

 
## Key Components

 
### MLCEngine

 The `MLCEngine` is the central component of WebLLM. It provides an interface for:

 
 - Loading and managing models
 - Handling chat completions
 - Managing model lifecycle
 - Coordinating between the different components
 
 Applications primarily interact with WebLLM through the `MLCEngine` interface, which provides methods for creating chat completions, embedding text, and managing models.

 
### Chat Completion Pipeline

 The chat completion pipeline handles the process of generating responses to user inputs. It follows a sequence that involves:

 
 - **Preprocessing**: Converting input messages into model-ready format
 - **Inference**: Running the actual model computation
 - **Generation**: Sampling output tokens based on model logits
 - **Postprocessing**: Formatting the response for the application
 
 
```

```

 Sources: [README.md153-201](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L153-L201) [src/llm_chat.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/llm_chat.ts)

 
### Worker Integrations

 WebLLM supports different execution environments to optimize performance and user experience:

 
 - **Main Thread**: Direct execution in the main browser thread
 - **Web Worker**: Running in a separate thread to prevent UI blocking
 - **Service Worker**: Persistent background execution for chrome extensions and offline functionality
 
 
```

```

 Sources: [README.md203-301](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L203-L301) [src/web_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts) [src/service_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/service_worker.ts)

 
## Model Loading and Caching

 WebLLM efficiently manages model loading and caching to optimize performance:

 
```

```

 When loading a model, WebLLM:

 
 - Fetches model files and WASM libraries from specified URLs
 - Stores these in browser cache (Cache API or IndexedDB)
 - Initializes the tokenizer and TVM runtime
 - Prepares the WebGPU environment for inference
 
 Sources: [README.md118-151](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L118-L151) [src/engine.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/engine.ts)

 
## API Compatibility

 One of WebLLM's key features is its compatibility with the OpenAI API standard. This allows developers familiar with OpenAI's interfaces to easily integrate WebLLM into their applications.

 
| Feature | Support | Description |
|---|---|---|
| Chat Completions | ✓ | Generate responses to conversations |
| Streaming | ✓ | Stream responses token by token |
| JSON Mode | ✓ | Generate valid JSON output |
| Function Calling | Partial | Tool usage and function calling capabilities |
| Embeddings | ✓ | Generate vector embeddings from text |
| Temperature Control | ✓ | Control randomness in generation |
| Context Window | Model-dependent | Depends on the specific model loaded |

 Sources: [README.md306-313](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L306-L313) [src/engine.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/engine.ts)

 
## Getting Started Overview

 Integrating WebLLM into an application involves a few basic steps:

 
 - **Installation**: Add the package via npm, yarn, or direct import
 - **Create an Engine**: Initialize the `MLCEngine` with a model
 - **Generate Completions**: Use the OpenAI-compatible API to create chat completions
 
 Basic usage example:

 
```

```

 For more detailed information on getting started, see [Getting Started](https://deepwiki.com/mlc-ai/web-llm/1.2-getting-started).

 Sources: [README.md79-117](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L79-L117) [README.md153-173](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L153-L173) [examples/get-started/package.json1-20](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/get-started/package.json#L1-L20)

 
## Supported Models

 WebLLM supports a variety of open-source language models, including:

 
 - **Llama Family**: Llama 3, Llama 2, Hermes-2-Pro-Llama-3
 - **Phi**: Phi 3, Phi 2, Phi 1.5
 - **Gemma**: Gemma-2B
 - **Mistral**: Mistral-7B, Hermes-Mistral, NeuralHermes
 - **Qwen (通义千问)**: Qwen2 0.5B, 1.5B, 7B
 
 Custom models can also be integrated by compiling them to the MLC format. For information on adding custom models, see [Advanced Features](https://deepwiki.com/mlc-ai/web-llm/5-advanced-features).

 Sources: [README.md54-67](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L54-L67) [src/config.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/config.ts)

 
## Example Applications

 WebLLM includes numerous example applications that demonstrate different use cases and integration patterns:

 
 - **Simple Chat**: Basic chat interface
 - **Web Worker Integration**: Running in background threads
 - **Service Worker**: Persistent background execution
 - **Chrome Extensions**: Browser extension integration
 - **Function Calling**: Tool usage demonstrations
 - **JSON Mode**: Structured output generation
 
 For more information on example applications, see [Example Applications](https://deepwiki.com/mlc-ai/web-llm/6-example-applications).

 Sources: [README.md68-78](https://github.com/mlc-ai/web-llm/blob/632d3472/README.md?plain=1#L68-L78) [examples/get-started/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/get-started/package.json) [examples/chrome-extension/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/chrome-extension/package.json) [examples/chrome-extension-webgpu-service-worker/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/chrome-extension-webgpu-service-worker/package.json)
