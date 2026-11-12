> 来源: [https://deepwiki.com/mlc-ai/web-llm/3-worker-integrations](https://deepwiki.com/mlc-ai/web-llm/3-worker-integrations)
> DeepWiki mlc-ai/web-llm | Last indexed: 18 April 2025 (632d34

# Worker Integrations

  Relevant source files 
 - [src/extension_service_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/extension_service_worker.ts)
 - [src/message.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/message.ts)
 - [src/service_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/service_worker.ts)
 
  This page documents WebLLM's worker integration system, which enables running language models in background threads or persistent service workers to maintain UI responsiveness in web applications. These integrations allow model inference to run outside the main thread, providing better performance and user experience.

 For information about the core engine that powers these workers, see [MLCEngine](https://deepwiki.com/mlc-ai/web-llm/2.1-mlcengine).

 
## Worker Integration Architecture

 WebLLM provides three main worker integration options:

 
```

```

 Sources: [src/web_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts) [src/service_worker.ts18-149](https://github.com/mlc-ai/web-llm/blob/632d3472/src/service_worker.ts#L18-L149) [src/extension_service_worker.ts18-102](https://github.com/mlc-ai/web-llm/blob/632d3472/src/extension_service_worker.ts#L18-L102)

 
## Communication Protocol

 All worker integrations use a common message protocol for communication:

 
```

```

 Sources: [src/message.ts15-163](https://github.com/mlc-ai/web-llm/blob/632d3472/src/message.ts#L15-L163)

 
## Web Worker Integration

 The Web Worker integration allows running WebLLM in a dedicated background thread.

 
### Architecture

 
```

```

 
### Key Features

 
 - **Asynchronous Model Loading**: Models are loaded in the background thread
 - **Promise-based Communication**: Uses a UUID-based message system with promises for request handling
 - **Multiple Model Support**: Can load and manage multiple models in the same worker
 
 Sources: [src/web_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts)

 
## Service Worker Integration

 Service Workers enable persistent background execution, allowing WebLLM models to continue running even when the page is not active.

 
### Architecture

 
```

```

 
### Key Features

 
 - **Persistence**: Continues running in the background even when the browser tab is closed
 - **Heartbeat System**: Uses periodic messages to keep the service worker alive
 - **Client Registry**: Maintains a registry of connected clients to route messages
 - **State Maintenance**: Can maintain model state across page reloads
 
 
### Service Worker Lifecycle

 
```

```

 Sources: [src/service_worker.ts18-253](https://github.com/mlc-ai/web-llm/blob/632d3472/src/service_worker.ts#L18-L253)

 
## Chrome Extension Integration

 A specialized version of the Service Worker integration designed for Chrome extensions.

 
### Architecture

 
```

```

 
### Key Features

 
 - **Chrome Extension API Integration**: Uses Chrome's `runtime.connect` API
 - **Port-based Communication**: Communicates via Chrome extension messaging ports
 - **Extension ID Support**: Optionally connects to external extensions via their ID
 - **Disconnect Callback**: Provides a callback mechanism when the port disconnects
 
 Sources: [src/extension_service_worker.ts1-195](https://github.com/mlc-ai/web-llm/blob/632d3472/src/extension_service_worker.ts#L1-L195)

 
## Creating Worker Instances

 WebLLM provides factory functions to create each type of worker:

 
| Worker Type | Factory Function | Source File |
|---|---|---|
| Web Worker | CreateWebWorkerMLCEngine | web_worker.ts |
| Service Worker | CreateServiceWorkerMLCEngine | service_worker.ts |
| Extension Worker | CreateServiceWorkerMLCEngine | extension_service_worker.ts |

 
### Usage Example for Service Worker

 The following outlines how to integrate a service worker with WebLLM:

 
 - Register a service worker in your web application
 - Create a ServiceWorkerMLCEngine instance
 - Use it like a regular MLCEngine
 
 Sources: [src/service_worker.ts192-213](https://github.com/mlc-ai/web-llm/blob/632d3472/src/service_worker.ts#L192-L213)

 
## Request Handling Flow

 
```

```

 
## Message Types

 The worker integrations handle various message types:

 
| Request Kind | Description | Used In |
|---|---|---|
| reload | Load or reload models | All workers |
| chatCompletionNonStreaming | Process non-streaming chat completion | All workers |
| chatCompletionStreamInit | Initialize streaming chat completion | All workers |
| completionStreamNextChunk | Get next chunk from streaming completion | All workers |
| keepAlive | Keep service worker active | Service/Extension workers |
| runtimeStatsText | Get runtime statistics | All workers |
| interruptGenerate | Interrupt ongoing generation | All workers |
| embedding | Generate embeddings | All workers |

 Sources: [src/message.ts18-37](https://github.com/mlc-ai/web-llm/blob/632d3472/src/message.ts#L18-L37)

 
## Comparison of Worker Types

 
| Feature | Web Worker | Service Worker | Extension Worker |
|---|---|---|---|
| Persistence | ❌ Terminates when page closes | ✅ Can persist after page closes | ✅ Can persist throughout browser session |
| Keep-alive | ❌ Not needed | ✅ Periodic heartbeat | ✅ Periodic heartbeat |
| Client tracking | ❌ Single client | ✅ Multiple clients | ✅ Multiple clients |
| Installation | No extra steps | Requires service worker registration | Requires Chrome extension |
| Use case | Complex web apps | PWAs, offline-capable apps | Browser extensions |

 Sources: [src/web_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts) [src/service_worker.ts18-253](https://github.com/mlc-ai/web-llm/blob/632d3472/src/service_worker.ts#L18-L253) [src/extension_service_worker.ts18-195](https://github.com/mlc-ai/web-llm/blob/632d3472/src/extension_service_worker.ts#L18-L195)
