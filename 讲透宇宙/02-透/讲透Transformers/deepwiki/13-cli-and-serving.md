> 来源: [https://deepwiki.com/huggingface/transformers/13-cli-and-serving](https://deepwiki.com/huggingface/transformers/13-cli-and-serving)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# CLI & Serving

  Relevant source files 
 - [docs/source/en/_redirects.yml](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/_redirects.yml)
 - [docs/source/en/serve-cli/serving.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/serve-cli/serving.md?plain=1)
 - [docs/source/en/serve-cli/serving_optims.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/serve-cli/serving_optims.md?plain=1)
 - [examples/pytorch/transformers_serve_cb_eval_job.py](https://github.com/huggingface/transformers/blob/8f542025/examples/pytorch/transformers_serve_cb_eval_job.py)
 - [src/transformers/cli/add_new_model_like.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/add_new_model_like.py)
 - [src/transformers/cli/chat.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/chat.py)
 - [src/transformers/cli/serve.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serve.py)
 - [src/transformers/cli/serving/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/__init__.py)
 - [src/transformers/cli/serving/chat_completion.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/chat_completion.py)
 - [src/transformers/cli/serving/completion.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/completion.py)
 - [src/transformers/cli/serving/model_manager.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/model_manager.py)
 - [src/transformers/cli/serving/response.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/response.py)
 - [src/transformers/cli/serving/server.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/server.py)
 - [src/transformers/cli/serving/transcription.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/transcription.py)
 - [src/transformers/cli/serving/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/utils.py)
 - [src/transformers/cli/system.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/system.py)
 - [src/transformers/cli/transformers.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/transformers.py)
 - [src/transformers/integrations/gemma_quant.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/gemma_quant.py)
 - [src/transformers/quantizers/quantizer_gemma.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/quantizer_gemma.py)
 - [tests/cli/conftest.py](https://github.com/huggingface/transformers/blob/8f542025/tests/cli/conftest.py)
 - [tests/cli/test_chat.py](https://github.com/huggingface/transformers/blob/8f542025/tests/cli/test_chat.py)
 - [tests/cli/test_serve.py](https://github.com/huggingface/transformers/blob/8f542025/tests/cli/test_serve.py)
 - [tests/utils/test_add_new_model_like.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_add_new_model_like.py)
 - [utils/check_auto.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_auto.py)
 - [utils/check_dummies.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_dummies.py)
 - [utils/sort_auto_mappings.py](https://github.com/huggingface/transformers/blob/8f542025/utils/sort_auto_mappings.py)
 
  The `transformers` library provides a robust command-line interface (CLI) for interacting with models, managing environments, and deploying OpenAI-compatible inference servers. This infrastructure is designed to bridge the gap between local development and lightweight production serving, offering features like continuous batching, automatic model lifecycle management, and multimodal support.

 
## CLI Entry Points

 The main entry point for all command-line operations is the `transformers` command, managed in [src/transformers/cli/transformers.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/transformers.py) It routes subcommands to specialized modules.

 
| Command | Module | Purpose |
|---|---|---|
| serve | src/transformers/cli/serve.py | Launches an OpenAI-compatible FastAPI server. |
| chat | src/transformers/cli/chat.py | Interactive terminal-based chat interface. |
| add-new-model-like | src/transformers/cli/add_new_model_like.py | Scaffolding tool to create new model architectures based on existing ones. |
| env | src/transformers/cli/system.py | Prints system information (Python, PyTorch, GPU, etc.) for debugging. |

 
### Scaffolding New Models

 The `add-new-model-like` command automates the boilerplate involved in adding a new model architecture [src/transformers/cli/add_new_model_like.py98-120](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/add_new_model_like.py#L98-L120) It uses `libcst` to parse existing model files and generate a new model directory under `src/transformers/models/`, updating `__init__.py` files and `AutoMapping` registries automatically [src/transformers/cli/add_new_model_like.py164-180](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/add_new_model_like.py#L164-L180) The tool identifies classes inheriting from `PreTrainedConfig` and `PreTrainedModel` via a `ClassFinder` visitor to populate `auto_mappings.py` [src/transformers/cli/add_new_model_like.py36-66](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/add_new_model_like.py#L36-L66)

 **Sources:** [src/transformers/cli/transformers.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/transformers.py) [src/transformers/cli/add_new_model_like.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/add_new_model_like.py) [src/transformers/cli/system.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/system.py)

 
---

 
## Serving Architecture

 The `transformers serve` command initializes a FastAPI-based server [src/transformers/cli/serving/server.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/server.py) capable of handling multiple inference tasks. It is designed around a `ModelManager` that handles the loading/unloading of weights and a set of `Handlers` that map HTTP requests to model execution.

 
### System Data Flow: Request to Inference

 The following diagram illustrates how an incoming HTTP request is routed through the serving subpackage to the underlying Transformer model.

 
```

```

 **Sources:** [src/transformers/cli/serve.py129-137](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serve.py#L129-L137) [src/transformers/cli/serving/model_manager.py93-118](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/model_manager.py#L93-L118) [src/transformers/cli/serving/chat_completion.py108-150](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/chat_completion.py#L108-L150)

 
### Model Management & Lifecycle

 The `ModelManager` is responsible for thread-safe model loading and memory optimization [src/transformers/cli/serving/model_manager.py93-137](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/model_manager.py#L93-L137)

 
 - **Automatic Unloading**: Models are wrapped in a `TimedModel` class which starts a background `threading.Timer` upon initialization [src/transformers/cli/serving/model_manager.py43-66](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/model_manager.py#L43-L66) If no requests are received within the `model_timeout` period, the model and its associated processor are deleted, and `gc.collect()`/`reset_torch_cache()` are called to free resources [src/transformers/cli/serving/model_manager.py74-90](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/model_manager.py#L74-L90)
 - **Force Preloading**: Using the `--force-model` flag disables the timeout and keeps a specific model resident in memory [src/transformers/cli/serve.py136-137](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serve.py#L136-L137) [src/transformers/cli/serving/model_manager.py141-146](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/model_manager.py#L141-L146)
 - **Streaming Progress**: The server supports a `/load_model` endpoint that uses Server-Sent Events (SSE) to report progress via a custom `tqdm` class [src/transformers/cli/serving/model_manager.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/model_manager.py#L33-L33)
 
 
### Supported Endpoints

 
| Endpoint | Handler Class | Description |
|---|---|---|
| /v1/chat/completions | ChatCompletionHandler | Supports text, VLM, and multimodal chat src/transformers/cli/serving/chat_completion.py |
| /v1/completions | CompletionHandler | Legacy prompt-based completion src/transformers/cli/serving/completion.py |
| /v1/responses | ResponseHandler | Implementation of the OpenAI Responses API src/transformers/cli/serving/response.py |
| /v1/audio/transcriptions | TranscriptionHandler | STT support (e.g., Whisper) src/transformers/cli/serving/transcription.py |
| /health | N/A | Liveness check used by CLI tests to verify readiness tests/cli/test_serve.py72-85 |

 **Sources:** [src/transformers/cli/serve.py113-118](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serve.py#L113-L118) [src/transformers/cli/serving/model_manager.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/model_manager.py) [src/transformers/cli/serving/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/utils.py) [src/transformers/cli/serving/response.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/response.py)

 
---

 
## Response Parsing & Chat Templates

 To support complex features like **tool calling** and **reasoning (thinking)** blocks within a standard OpenAI-compatible stream, the serving layer uses a `ResponseParser` [src/transformers/cli/serving/utils.py31](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cli/serving/utils.py#L31-L31)

 
### Parsing Logic

 Because different models use different special tokens or XML-like tags for reasoning (e.g., `"] T4["Hello!"] end

 
```
subgraph "ResponseParser (utils.py)"
    RP["ResponseParser"]
    RT["ReasoningText"]
end

subgraph "SSE Delta (chat_completion.py)"
    D1["delta: {reasoning_content: 'I should check...'}"]
    D2["delta: {content: 'Hello!'}"]
end

T1 --> RP
T2 --> RP
T3 --> RP
RP -- "yield ReasoningText" --> RT
RT --> D1
T4 --> D2
```

 
```
**Sources:** [src/transformers/cli/serving/utils.py:95-194](), [src/transformers/cli/serving/chat_completion.py:192-205](), [src/transformers/cli/serving/response.py:98-150]()

---

## Performance Optimizations

The serving layer exposes several core library optimizations via CLI flags:

1.  **Continuous Batching**: Enabled via `--continuous-batching`. It uses the `ContinuousBatchingAPI` to interleave the prefill and decode phases of multiple requests [src/transformers/cli/serve.py:46-49](). Configuration parameters like `cb_block_size` and `cb_num_blocks` allow tuning the paged attention KV cache [src/transformers/cli/serve.py:83-97]().
2.  **Quantization**: Supports `bnb-4bit` and `bnb-8bit` runtime quantization via `BitsAndBytesConfig` [src/transformers/cli/serve.py:54-56]().
3.  **Attention Backends**: Users can force specific implementations like `flash_attention_2` or `sdpa`. On Apple Silicon (MPS), the server automatically defaults to `metal-flash-sdpa` if the `kernels` library is installed [src/transformers/cli/serving/model_manager.py:162-185]().
4.  **Torch Compile**: The `--compile` flag triggers `torch.compile` on the model's forward pass for reduced overhead in non-batched scenarios [src/transformers/cli/serve.py:53](). Note that this is currently incompatible with continuous batching [docs/source/en/serve-cli/serving_optims.md:85]().

**Sources:** [src/transformers/cli/serve.py](), [src/transformers/cli/serving/model_manager.py](), [docs/source/en/serve-cli/serving_optims.md]()

---

## Interactive Chat CLI

The `transformers chat` command provides a `RichInterface` for interacting with either a local `transformers serve` instance or a remote Hugging Face Inference Endpoint [src/transformers/cli/chat.py:113-120]().

### Key Features
- **Markdown Rendering**: Uses the `rich` library to render model outputs, including code blocks and reasoning sections [src/transformers/cli/chat.py:145-167](). It applies a workaround for Markdown line breaks by appending trailing spaces to lines [src/transformers/cli/chat.py:157-165]().
- **Session Management**: Supports commands like `!save` to export chat history to YAML and `!clear` to reset the context [src/transformers/cli/chat.py:87-103]().
- **Dynamic Settings**: Users can modify generation parameters (e.g., `temperature`, `max_new_tokens`) mid-session using the `!set` command [src/transformers/cli/chat.py:97-99]().
- **Streaming UI**: Uses `rich.live` to update the console output in real-time as tokens are received from the server [src/transformers/cli/chat.py:124-170]().

**Sources:** [src/transformers/cli/chat.py](), [tests/cli/test_chat.py]()
```
