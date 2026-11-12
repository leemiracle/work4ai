> 来源: [https://deepwiki.com/mozilla-ai/llamafile/5-http-server-and-api](https://deepwiki.com/mozilla-ai/llamafile/5-http-server-and-api)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# HTTP Server and API

  Relevant source files 
 - [llama.cpp.patches/llamafile-files/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/llamafile-files/BUILD.mk)
 - [llama.cpp.patches/patches/common_arg.cpp.patch](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/common_arg.cpp.patch)
 - [llama.cpp.patches/patches/common_common.cpp.patch](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/common_common.cpp.patch)
 - [llama.cpp.patches/patches/tools_server_server-models.cpp.patch](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server-models.cpp.patch)
 - [llama.cpp.patches/patches/tools_server_server.cpp.patch](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server.cpp.patch)
 - [llama.cpp.patches/patches/vendor_cpp-httplib_httplib.cpp.patch](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/vendor_cpp-httplib_httplib.cpp.patch)
 - [llamafile/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk)
 
  The llamafile HTTP server provides a high-performance, local inference endpoint derived from `llama.cpp`'s server implementation. It is designed to be both a developer-friendly tool and a production-ready backend, supporting industry-standard APIs and advanced security features like sandboxing.

 The server is integrated directly into the llamafile executable and can be invoked in multiple execution modes (e.g., `--server` or the combined TUI+Server `AUTO` mode) [llamafile/chatbot_main.cpp158-160](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L158-L160) It handles model loading, state management, and request dispatching across various backends.

 
## Server Architecture and Execution

 The server's entry point is `server_main`, a patched version of `llama_server` that allows llamafile to inject custom logic for initialization, sandboxing, and lifecycle management [llama.cpp.patches/patches/tools_server_server.cpp.patch40-42](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server.cpp.patch#L40-L42)

 
### Request Lifecycle Diagram

 This diagram maps the flow of an HTTP request through the system components, from the network listener to the inference engine.

 
```

```

 **Sources:** [llama.cpp.patches/patches/tools_server_server.cpp.patch86-90](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server.cpp.patch#L86-L90) [llama.cpp.patches/patches/tools_server_server.cpp.patch141-145](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server.cpp.patch#L141-L145)

 
## Key Features

 
 - **OpenAI Compatibility**: Implements the `/v1/chat/completions` and `/v1/completions` endpoints, allowing llamafile to drop into existing workflows designed for OpenAI [llamafile/chatbot_api.cpp20-50](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp#L20-L50)
 - **Anthropic Messages API**: Support for Anthropic-style message formats and tool-calling structures.
 - **Web UI**: An embedded user interface available at `localhost:8080` (by default) for interactive testing and configuration.
 - **TLS/SSL Support**: Encrypted communication using `mbedTLS` [llamafile/BUILD.mk73-77](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk#L73-L77) The server supports `HTTPS` via `httplib::SSLServer` [llama.cpp.patches/patches/tools_server_server-models.cpp.patch132-144](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server-models.cpp.patch#L132-L144)
 - **Sandboxing**: Advanced security using `pledge()` and `unveil()` on supported platforms to restrict filesystem and network access [llama.cpp.patches/patches/tools_server_server.cpp.patch93-102](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server.cpp.patch#L93-L102)
 
 
## Execution Modes and Configuration

 Llamafile uses a sophisticated argument parsing system to distinguish between its own flags and those passed to the underlying `llama.cpp` server logic.

 
| Mode | Flag | Description |
|---|---|---|
| SERVER | --server | HTTP server only. Enables full sandboxing by default llamafile/args.cpp127 |
| AUTO | (default) | Combined TUI chat and HTTP server. Sandbox is disabled to allow the in-process TUI to connect to the server llama.cpp.patches/patches/tools_server_server.cpp.patch104-107 |
| CLI | --cli | Single prompt/response mode using chatbot_cli.cpp llamafile/chatbot_cli.cpp148-150 |
| CHAT | --chat | Interactive TUI only. No HTTP server is started llamafile/chatbot_main.cpp158-160 |

 **Sources:** [llamafile/args.cpp127](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/args.cpp#L127-L127) [llamafile/chatbot_main.cpp158-165](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L158-L165)

 
### Initialization Flow

 The following diagram illustrates how the server initializes, specifically highlighting the point where the sandbox is applied relative to model loading.

 
```

```

 **Sources:** [llamafile/args.cpp127](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/args.cpp#L127-L127) [llama.cpp.patches/patches/tools_server_server.cpp.patch56-145](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server.cpp.patch#L56-L145)

 
## API Endpoints and Compatibility

 For detailed information on supported routes, request/response schemas, and how llamafile patches `llama.cpp` to support specific tool-calling and multimodal features, see **[API Endpoints and Compatibility](https://deepwiki.com/mozilla-ai/llamafile/5.1-api-endpoints-and-compatibility)**.

 
## Security and Sandboxing

 Llamafile provides industry-leading security for LLM deployment via `pledge()` and `unveil()`. To learn about promise sets, Landlock LSM integration, and the `--confine-reads` flag, see **[Security and Sandboxing](https://deepwiki.com/mozilla-ai/llamafile/5.2-security-and-sandboxing)**.

 
## Integration Testing

 The server and API surface are verified using a comprehensive Python-based integration suite. These tests cover:

 
 - **SSL/TLS**: Verification of HTTPS serving and certificate handling [llama.cpp.patches/patches/vendor_cpp-httplib_httplib.cpp.patch46-52](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/vendor_cpp-httplib_httplib.cpp.patch#L46-L52)
 - **Multimodal**: API-based image description and question answering [llamafile/image.cpp20-40](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/image.cpp#L20-L40)
 - **Condition Variables**: Patches ensure stability under heavy load by working around Cosmopolitan/XNU futex limitations [llama.cpp.patches/patches/tools_server_server-models.cpp.patch17-30](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server-models.cpp.patch#L17-L30)
 
 **Sources:** [llamafile/BUILD.mk145-168](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk#L145-L168) [llama.cpp.patches/patches/tools_server_server-models.cpp.patch12-30](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/patches/tools_server_server-models.cpp.patch#L12-L30)
