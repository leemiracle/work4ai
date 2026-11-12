<!-- source: DeepWiki mcp.deepwiki.com · repo vllm-project/vllm · page 6 Serving APIs · fetched 2026-10-28 -->

# Serving APIs

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/design/endpoint_plugins.md](docs/design/endpoint_plugins.md)
- [docs/mkdocs/gen_files/generate_argparse.py](docs/mkdocs/gen_files/generate_argparse.py)
- [examples/features/openai_batch/README.md](examples/features/openai_batch/README.md)
- [tests/entrypoints/cohere/test_registry_and_args.py](tests/entrypoints/cohere/test_registry_and_args.py)
- [tests/entrypoints/launchers/render/__init__.py](tests/entrypoints/launchers/render/__init__.py)
- [tests/entrypoints/launchers/render/test_app_state.py](tests/entrypoints/launchers/render/test_app_state.py)
- [tests/entrypoints/launchers/test_balanced_accepts.py](tests/entrypoints/launchers/test_balanced_accepts.py)
- [tests/entrypoints/launchers/test_run_batch.py](tests/entrypoints/launchers/test_run_batch.py)
- [tests/entrypoints/openai/test_render_parity.py](tests/entrypoints/openai/test_render_parity.py)
- [tests/plugins/vllm_add_dummy_endpoint_plugin/setup.py](tests/plugins/vllm_add_dummy_endpoint_plugin/setup.py)
- [tests/plugins/vllm_add_dummy_endpoint_plugin/vllm_add_dummy_endpoint_plugin/__init__.py](tests/plugins/vllm_add_dummy_endpoint_plugin/vllm_add_dummy_endpoint_plugin/__init__.py)
- [tests/plugins_tests/test_endpoint_plugins.py](tests/plugins_tests/test_endpoint_plugins.py)
- [vllm/entrypoints/cli/benchmark/main.py](vllm/entrypoints/cli/benchmark/main.py)
- [vllm/entrypoints/cli/launch.py](vllm/entrypoints/cli/launch.py)
- [vllm/entrypoints/cli/main.py](vllm/entrypoints/cli/main.py)
- [vllm/entrypoints/cli/run_batch.py](vllm/entrypoints/cli/run_batch.py)
- [vllm/entrypoints/launchers/api_server/app_state.py](vllm/entrypoints/launchers/api_server/app_state.py)
- [vllm/entrypoints/launchers/api_server/entry.py](vllm/entrypoints/launchers/api_server/entry.py)
- [vllm/entrypoints/launchers/app.py](vllm/entrypoints/launchers/app.py)
- [vllm/entrypoints/launchers/launcher.py](vllm/entrypoints/launchers/launcher.py)
- [vllm/entrypoints/launchers/render/app_state.py](vllm/entrypoints/launchers/render/app_state.py)
- [vllm/entrypoints/launchers/render/entry.py](vllm/entrypoints/launchers/render/entry.py)
- [vllm/entrypoints/launchers/run_batch.py](vllm/entrypoints/launchers/run_batch.py)
- [vllm/entrypoints/openai/api_server.py](vllm/entrypoints/openai/api_server.py)
- [vllm/plugins/__init__.py](vllm/plugins/__init__.py)
- [vllm/plugins/endpoint_plugins/__init__.py](vllm/plugins/endpoint_plugins/__init__.py)
- [vllm/plugins/endpoint_plugins/interface.py](vllm/plugins/endpoint_plugins/interface.py)

</details>



## Purpose and Scope

The serving layer provides HTTP-facing interfaces between clients and vLLM inference components. This page summarizes the server entrypoints, request-rendering path, and related serving features; detailed implementation belongs in the child pages listed below. The legacy `vllm.entrypoints.openai.api_server` module re-exports launcher functions and is deprecated in favor of the launcher entrypoints. [vllm/entrypoints/openai/api_server.py:5-30]()

- For the FastAPI application, route registration, middleware, lifecycle, and endpoint families, see [OpenAI-Compatible API Server](#6.1).
- For chat message processing, multimodal content, templates, tokenizers, and renderers, see [Chat Utilities and Message Processing](#6.2).
- For tool and reasoning parsers and structured output, see [Tool Calling, Reasoning Parsers and Structured Output](#6.3).
- For dynamic LoRA adapter management, see [LoRA Adapter Management](#6.4).
- For the Rust HTTP/gRPC frontend and its engine integration, see [Rust Frontend (vllm-frontend-rs)](#6.5).
- For rendering and token-in-token-out scale-out serving, see [Scale-Out and Token-in-Token-out Serving](#6.6).

Sources: [vllm/entrypoints/openai/api_server.py:5-30]()

---

## System Architecture Overview

The Python serving path builds a FastAPI application, initializes its state using information from an `EngineClient`, and starts HTTP serving through the launcher. The engine client is created from `AsyncEngineArgs` and `VllmConfig`; it is shut down when its lifecycle context exits. [vllm/entrypoints/launchers/api_server/entry.py:34-65]()[vllm/entrypoints/launchers/api_server/entry.py:68-112]()[vllm/entrypoints/launchers/api_server/entry.py:115-161]()

### High-Level Component Diagram

```mermaid
graph LR
    Client["HTTP client"] --> "serve_http"
    "vllm serve CLI" --> "run_server"
    "run_server" --> "run_server_worker"
    "run_server_worker" --> "build_async_engine_client"
    "build_async_engine_client" --> "AsyncEngineArgs.from_cli_args"
    "AsyncEngineArgs.from_cli_args" --> "AsyncLLM.from_vllm_config"
    "run_server_worker" --> "build_and_serve"
    "build_and_serve" --> "build_app"
    "build_and_serve" --> "init_app_state"
    "build_and_serve" --> "serve_http"
    "build_app" --> "FastAPI application"
    "init_app_state" --> "app.state"
    "app.state" --> "EngineClient"
```

The CLI defines `serve` and other commands through its command modules; the server entrypoint then connects application construction, state initialization, and HTTP startup. The shown launcher code passes supported tasks and model configuration to `build_app` and initializes state before serving. [vllm/entrypoints/cli/main.py:39-64]()[vllm/entrypoints/launchers/api_server/entry.py:115-161]()

Sources: [vllm/entrypoints/cli/main.py:39-64](), [vllm/entrypoints/launchers/api_server/entry.py:115-161]()

---

## Serving Entity Mapping

This diagram connects user-facing concepts to named code entities. The compatibility module exposes launcher functions; the CLI includes serving commands; and the server entrypoint builds the application and engine client. [vllm/entrypoints/openai/api_server.py:5-20]()[vllm/entrypoints/cli/main.py:43-64]()[vllm/entrypoints/launchers/api_server/entry.py:34-40]()[vllm/entrypoints/launchers/api_server/entry.py:115-137]()

```mermaid
graph LR
    subgraph "Natural Language Space"
        "Start the API server"
        "Build the HTTP app"
        "Connect the inference engine"
        "Run batch inference"
        "Launch a rendering server"
    end

    subgraph "Code Entity Space"
        "vllm serve"
        "run_server"
        "build_and_serve"
        "build_app"
        "build_async_engine_client"
        "AsyncLLM.from_vllm_config"
        "vllm run-batch"
        "vllm.entrypoints.launchers.run_batch"
        "vllm launch render"
        "run_launch_fastapi"
    end

    "Start the API server" --> "vllm serve"
    "vllm serve" --> "run_server"
    "run_server" --> "build_and_serve"
    "Build the HTTP app" --> "build_app"
    "Connect the inference engine" --> "build_async_engine_client"
    "build_async_engine_client" --> "AsyncLLM.from_vllm_config"
    "Run batch inference" --> "vllm run-batch"
    "vllm run-batch" --> "vllm.entrypoints.launchers.run_batch"
    "Launch a rendering server" --> "vllm launch render"
    "vllm launch render" --> "run_launch_fastapi"
```

The CLI dispatches registered command modules, including the `serve` and `run_batch` modules. The `launch render` command invokes `run_launch_fastapi`; its documented role is to start a GPU-less rendering server for preprocessing and postprocessing. [vllm/entrypoints/cli/main.py:43-64]()[vllm/entrypoints/cli/launch.py:46-64]()

Sources: [vllm/entrypoints/cli/main.py:43-64](), [vllm/entrypoints/cli/launch.py:46-64]()

---

## Request Processing and Rendering

The renderer is a shared serving concern: the render-server state initializer constructs an `OnlineRenderer` and an `OnlineDerenderer` from the model configuration, chat-template settings, and parser-related options. It also initializes tokenization and render state. [vllm/entrypoints/launchers/render/app_state.py:22-32]()[vllm/entrypoints/launchers/render/app_state.py:48-108]()

The render server is distinct from the engine-backed API server: its state initializer documents that it does not require an `EngineClient`, sets `engine_client` to `None`, and disables stats logging. [vllm/entrypoints/launchers/render/app_state.py:27-32]()[vllm/entrypoints/launchers/render/app_state.py:110-120]()

### Rendering and Serving Path

```mermaid
graph LR
    "HTTP request" --> "FastAPI app"
    "FastAPI app" --> "app.state"
    "app.state" --> "OnlineRenderer"
    "OnlineRenderer" --> "renderer_from_config"
    "OnlineRenderer" --> "load_chat_template"
    "OnlineRenderer" --> "EngineClient"
    "EngineClient" --> "AsyncLLM"
    "vllm launch render" --> "init_render_app_state"
    "init_render_app_state" --> "OnlineRenderer"
    "init_render_app_state" --> "OnlineDerenderer"
    "init_render_app_state" --> "ServingTokenization"
    "init_render_app_state" --> "engine_client = None"
```

The diagram distinguishes the engine-backed server from the render-only initializer. The render initializer creates renderer, derenderer, and tokenization state directly from `VllmConfig`; the API server entrypoint instead builds an engine client and initializes app state before HTTP serving. [vllm/entrypoints/launchers/render/app_state.py:22-32]()[vllm/entrypoints/launchers/render/app_state.py:48-120]()[vllm/entrypoints/launchers/api_server/entry.py:68-112]()[vllm/entrypoints/launchers/api_server/entry.py:115-161]()

Sources: [vllm/entrypoints/launchers/render/app_state.py:22-32](), [vllm/entrypoints/launchers/render/app_state.py:48-120](), [vllm/entrypoints/launchers/api_server/entry.py:68-112](), [vllm/entrypoints/launchers/api_server/entry.py:115-161]()

---

## Serving Features and Entry Points

The serving surface includes an engine-backed HTTP application, a separate rendering launch path, batch execution, and endpoint plugins. The batch request schema shown in the launcher accepts chat completion, embedding, scoring, reranking, transcription, and translation request types; the batch runner uses the request URL to validate the body type. [vllm/entrypoints/launchers/run_batch.py:153-200]()

| Serving area | Code entry point | Scope |
|---|---|---|
| API server | `run_server`, `build_and_serve` | Builds the app, initializes state, and serves HTTP. [vllm/entrypoints/launchers/api_server/entry.py:115-161]() |
| Rendering server | `vllm launch render`, `run_launch_fastapi` | Launches a GPU-less server for preprocessing and postprocessing. [vllm/entrypoints/cli/launch.py:46-64]() |
| Batch runner | `vllm.entrypoints.launchers.run_batch` | Defines batch request bodies and URL-based request validation. [vllm/entrypoints/launchers/run_batch.py:153-200]() |
| Endpoint plugins | `EndpointPlugin`, `attach_endpoint_plugins` | Plugin hooks can attach routes and initialize plugin state. [tests/plugins_tests/test_endpoint_plugins.py:17-27]() |

For the API server details, see [OpenAI-Compatible API Server](#6.1); for batch-specific behavior, see that child page’s endpoint-family coverage. For render-only processing, see [Scale-Out and Token-in-Token-out Serving](#6.6). [vllm/entrypoints/launchers/api_server/entry.py:115-161]()[vllm/entrypoints/cli/launch.py:46-64]()

Sources: [vllm/entrypoints/launchers/api_server/entry.py:115-161](), [vllm/entrypoints/cli/launch.py:46-64](), [vllm/entrypoints/launchers/run_batch.py:153-200](), [tests/plugins_tests/test_endpoint_plugins.py:17-27]()

---

## Core Serving Subsystems and Their Relationships

The serving components connect transport and API handling to request preparation and engine execution. Specialized concerns—parsing, adapter management, Rust frontend, and scale-out rendering—are covered in child pages rather than expanded here. [vllm/entrypoints/launchers/api_server/entry.py:115-161]()[vllm/entrypoints/launchers/render/app_state.py:48-108]()

| Subsystem | Role in the overview | Details |
|---|---|---|
| OpenAI-Compatible API Server | FastAPI construction, app state, and HTTP lifecycle | [OpenAI-Compatible API Server](#6.1) |
| Chat Utilities and Message Processing | Rendering, templates, tokenization, and multimodal request preparation | [Chat Utilities and Message Processing](#6.2) |
| Tool Calling, Reasoning Parsers and Structured Output | Parser-related serving options are passed into renderer state | [Tool Calling, Reasoning Parsers and Structured Output](#6.3) |
| LoRA Adapter Management | Dynamic adapter APIs and lifecycle | [LoRA Adapter Management](#6.4) |
| Rust Frontend | Alternative OpenAI-compatible frontend | [Rust Frontend (vllm-frontend-rs)](#6.5) |
| Scale-Out and Token-in-Token-out Serving | Render and derender paths and token-oriented deployments | [Scale-Out and Token-in-Token-out Serving](#6.6) |

The Python API server initializes engine-backed app state, while the render initializer can prepare renderer and tokenization state without an engine client. These are related serving paths with different responsibilities; use the linked child pages for subsystem-level detail. [vllm/entrypoints/launchers/api_server/entry.py:115-161]()[vllm/entrypoints/launchers/render/app_state.py:27-32]()[vllm/entrypoints/launchers/render/app_state.py:110-120]()

Sources: [vllm/entrypoints/launchers/api_server/entry.py:115-161](), [vllm/entrypoints/launchers/render/app_state.py:27-32](), [vllm/entrypoints/launchers/render/app_state.py:110-120]()

---

This page maps the serving layer at a high level. For implementation details, follow the child-page links above.

---

