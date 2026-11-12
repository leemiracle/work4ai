> 来源: [https://deepwiki.com/sgl-project/sglang/13-api-interfaces](https://deepwiki.com/sgl-project/sglang/13-api-interfaces)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# API Interfaces

  Relevant source files 
 - [docs/docs/developer_guide/overview.mdx](https://github.com/sgl-project/sglang/blob/94183a8d/docs/docs/developer_guide/overview.mdx?plain=1)
 - [docs/docs/developer_guide/serve_backend_plugins.mdx](https://github.com/sgl-project/sglang/blob/94183a8d/docs/docs/developer_guide/serve_backend_plugins.mdx?plain=1)
 - [python/sglang/cli/main.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/cli/main.py)
 - [python/sglang/cli/serve.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/cli/serve.py)
 - [python/sglang/cli/serve_backends.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/cli/serve_backends.py)
 - [python/sglang/cli/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/cli/utils.py)
 - [python/sglang/launch_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/launch_server.py)
 - [python/sglang/srt/compilation/backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/compilation/backend.py)
 - [python/sglang/srt/compilation/npu_piecewise_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/compilation/npu_piecewise_backend.py)
 - [python/sglang/srt/compilation/weak_ref_tensor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/compilation/weak_ref_tensor.py)
 - [python/sglang/srt/entrypoints/context.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/context.py)
 - [python/sglang/srt/entrypoints/grpc_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/grpc_server.py)
 - [python/sglang/srt/entrypoints/harmony_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/harmony_utils.py)
 - [python/sglang/srt/entrypoints/openai/protocol.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/protocol.py)
 - [python/sglang/srt/entrypoints/openai/serving_chat.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_chat.py)
 - [python/sglang/srt/entrypoints/openai/serving_completions.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_completions.py)
 - [python/sglang/srt/entrypoints/openai/serving_responses.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_responses.py)
 - [python/sglang/srt/entrypoints/openai/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/utils.py)
 - [python/sglang/srt/function_call/deepseekv32_detector.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/function_call/deepseekv32_detector.py)
 - [python/sglang/srt/function_call/kimik3_detector.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/function_call/kimik3_detector.py)
 - [python/sglang/srt/parser/reasoning_parser.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/parser/reasoning_parser.py)
 - [python/sglang/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/utils.py)
 - [test/registered/function_call/test_kimik3_detector.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/function_call/test_kimik3_detector.py)
 - [test/registered/sampling/test_sampling_mask.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/sampling/test_sampling_mask.py)
 - [test/registered/unit/cli/test_serve_backends.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/cli/test_serve_backends.py)
 - [test/registered/unit/entrypoints/openai/test_protocol.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/entrypoints/openai/test_protocol.py)
 - [test/registered/unit/entrypoints/openai/test_responses_protocol.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/entrypoints/openai/test_responses_protocol.py)
 - [test/registered/unit/entrypoints/openai/test_serving_chat.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/entrypoints/openai/test_serving_chat.py)
 - [test/registered/unit/entrypoints/openai/test_serving_completions.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/entrypoints/openai/test_serving_completions.py)
 - [test/registered/unit/entrypoints/openai/test_serving_responses.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/entrypoints/openai/test_serving_responses.py)
 - [test/registered/unit/entrypoints/openai/test_serving_responses_stream.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/entrypoints/openai/test_serving_responses_stream.py)
 - [test/registered/unit/entrypoints/openai/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/entrypoints/openai/utils.py)
 - [test/registered/unit/function_call/test_deepseekv4_detector.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/function_call/test_deepseekv4_detector.py)
 - [test/registered/unit/parser/test_kimik3_reasoning_parser.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/parser/test_kimik3_reasoning_parser.py)
 - [test/registered/unit/parser/test_reasoning_parser.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/parser/test_reasoning_parser.py)
 - [test/registered/utils/test_socket_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/utils/test_socket_utils.py)
 
  SGLang provides a comprehensive suite of user-facing interfaces designed for high-performance LLM and VLM serving. These range from programmatic Python APIs for integration into applications to industry-standard HTTP/OpenAI-compatible endpoints and high-throughput gRPC services.

 For information about the internal request processing pipeline, see [Request Processing Pipeline](https://deepwiki.com/sgl-project/sglang/4-request-processing-pipeline). For server configuration details, see [Server Configuration (ServerArgs)](https://deepwiki.com/sgl-project/sglang/3.2-server-configuration-(serverargs)).

 
## Python Engine API

 The `Engine` class is the primary entry point for programmatic access to SGLang's runtime (SRT). It manages the complex lifecycle of the tokenizer, scheduler, and detokenizer processes, abstracting away the inter-process communication (IPC) layer [python/sglang/srt/entrypoints/engine.py199-211](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L199-L211)

 For details, see [Python Engine API](https://deepwiki.com/sgl-project/sglang/13.1-python-engine-api).

 
### Engine Initialization

 The `Engine` can be initialized directly with keyword arguments (which are internally mapped to `ServerArgs`) or by passing a pre-constructed `ServerArgs` object [python/sglang/srt/entrypoints/engine.py230-240](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L230-L240) The `ServerArgs` class defines the configuration space for the engine, including model paths, quantization choices, and backend selections.

 
```

```

 
### Engine Architecture

 The `Engine` coordinates three main components: the `TokenizerManager` (running in the main process), and the `Scheduler` and `DetokenizerManager` (running in separate subprocesses) [python/sglang/srt/entrypoints/engine.py203-207](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L203-L207) Communication between these entities is handled via ZMQ IPC using specific request/response structures defined in `io_struct.py` [python/sglang/srt/managers/io_struct.py90](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L90-L90)

 Title: Engine Process and API Mapping

 
```

```

 Sources: [python/sglang/srt/entrypoints/engine.py199-211](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L199-L211) [python/sglang/srt/managers/io_struct.py90](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L90-L90) [python/sglang/srt/entrypoints/openai/serving_chat.py97-98](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_chat.py#L97-L98)

 
## HTTP Server and OpenAI API

 SGLang provides a FastAPI-based server that implements the OpenAI API protocol. This allows SGLang to serve as a drop-in replacement for existing OpenAI-compatible infrastructure.

 For details, see [HTTP Server and OpenAI-Compatible API](https://deepwiki.com/sgl-project/sglang/13.2-http-server-and-openai-compatible-api).

 
### Supported Protocols and Endpoints

 The server supports multiple protocols, including OpenAI, Anthropic, and Ollama, by wrapping the internal engine logic in protocol-specific serving classes.

 
| Endpoint | Handler Class | Purpose |
|---|---|---|
| /v1/chat/completions | OpenAIServingChat python/sglang/srt/entrypoints/openai/serving_chat.py202 | Chat completions with template formatting |
| /v1/completions | OpenAIServingCompletion python/sglang/srt/entrypoints/openai/serving_completions.py47 | Raw text completions |
| /v1/responses | OpenAIServingResponses python/sglang/srt/entrypoints/openai/serving_responses.py137 | Handler for Harmony and tool-centric responses |

 Title: HTTP Request to Internal Engine Mapping

 
```

```

 Sources: [python/sglang/srt/entrypoints/openai/serving_chat.py202](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_chat.py#L202-L202) [python/sglang/srt/entrypoints/openai/serving_completions.py47](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_completions.py#L47-L47) [python/sglang/srt/entrypoints/openai/serving_responses.py137](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_responses.py#L137-L137)

 
## Chat Templates and Conversation Formatting

 The `TemplateManager` handles the transformation of structured conversation messages into the specific prompt formats required by different models.

 For details, see [Chat Templates and Conversation Formatting](https://deepwiki.com/sgl-project/sglang/13.3-chat-templates-and-conversation-formatting).

 The system supports:

 
 - **Automatic Detection:** Automatically resolving reasoning and tool-call parsers based on the model path and configuration [python/sglang/srt/entrypoints/openai/serving_chat.py91-93](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_chat.py#L91-L93)
 - **Multi-modal Inputs:** Processing images, video, and audio through a unified input format [python/sglang/srt/entrypoints/openai/serving_chat.py102](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_chat.py#L102-L102)
 - **Tool Use Parsing:** Integrated `FunctionCallParser` for structured tool interactions [python/sglang/srt/entrypoints/openai/serving_chat.py84](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_chat.py#L84-L84)
 - **Reasoning Extraction:** Specialized parsing for reasoning traces via `ReasoningParser` [python/sglang/srt/parser/reasoning_parser.py50-62](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/parser/reasoning_parser.py#L50-L62)
 
 Sources: [python/sglang/srt/entrypoints/openai/serving_chat.py84-102](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_chat.py#L84-L102) [python/sglang/srt/parser/reasoning_parser.py50-62](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/parser/reasoning_parser.py#L50-L62)

 
## gRPC Server Interface

 For high-throughput environments, SGLang provides a gRPC interface. This interface is supported by the `smg-grpc-servicer` package [python/sglang/srt/entrypoints/grpc_server.py159-166](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/grpc_server.py#L159-L166)

 For details, see [gRPC Server Interface](https://deepwiki.com/sgl-project/sglang/13.4-grpc-server-interface).

 The gRPC implementation includes a lightweight HTTP sidecar to expose Prometheus metrics and profiling control [python/sglang/srt/entrypoints/grpc_server.py4-11](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/grpc_server.py#L4-L11)

 Sources: [python/sglang/srt/entrypoints/grpc_server.py1-11](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/grpc_server.py#L1-L11) [python/sglang/srt/entrypoints/grpc_server.py159-166](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/grpc_server.py#L159-L166)

 
## Specialized Model and Feature Support

 SGLang includes specialized support for advanced model architectures and protocols:

 
 - **Quantization Support:** Integration with various quantization methods such as FP8 and DeepGEMM [python/sglang/srt/entrypoints/openai/protocol.py168-172](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/protocol.py#L168-L172)
 - **Constrained Generation:** Support for JSON Schema and grammar constraints via `xgrammar` [python/sglang/srt/entrypoints/openai/protocol.py65-68](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/protocol.py#L65-L68)
 - **DeepSeek Support:** Specialized detectors for DeepSeek V3/V4 function calling and reasoning formats [python/sglang/srt/function_call/deepseekv32_detector.py21-71](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/function_call/deepseekv32_detector.py#L21-L71)
 - **Thinking Mode:** Support for specific encoding modes such as `CHAT` vs `THINKING` for reasoning-capable models [python/sglang/srt/entrypoints/openai/serving_chat.py14-19](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_chat.py#L14-L19)
 - **Usage Reporting:** Detailed token usage reporting, including cache hits across device, host, and storage tiers [python/sglang/srt/entrypoints/openai/protocol.py165-184](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/protocol.py#L165-L184)
 
 Sources: [python/sglang/srt/entrypoints/openai/protocol.py65-184](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/protocol.py#L65-L184) [python/sglang/srt/function_call/deepseekv32_detector.py21-71](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/function_call/deepseekv32_detector.py#L21-L71) [python/sglang/srt/entrypoints/openai/serving_chat.py14-19](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_chat.py#L14-L19)
