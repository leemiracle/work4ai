> 来源: [https://deepwiki.com/xorbitsai/inference/1-overview](https://deepwiki.com/xorbitsai/inference/1-overview)
> DeepWiki xorbitsai/inference | Last indexed: 30 July 2026 (d97e09

# Overview

  Relevant source files 
 - [.git_archival.txt](https://github.com/xorbitsai/inference/blob/d97e0970/.git_archival.txt)
 - [.gitignore](https://github.com/xorbitsai/inference/blob/d97e0970/.gitignore)
 - [AGENTS.md](https://github.com/xorbitsai/inference/blob/d97e0970/AGENTS.md?plain=1)
 - [CLAUDE.md](https://github.com/xorbitsai/inference/blob/d97e0970/CLAUDE.md?plain=1)
 - [README.md](https://github.com/xorbitsai/inference/blob/d97e0970/README.md?plain=1)
 - [SECURITY.md](https://github.com/xorbitsai/inference/blob/d97e0970/SECURITY.md?plain=1)
 - [build_backend.py](https://github.com/xorbitsai/inference/blob/d97e0970/build_backend.py)
 - [build_web.py](https://github.com/xorbitsai/inference/blob/d97e0970/build_web.py)
 - [doc/review_po_translations.py](https://github.com/xorbitsai/inference/blob/d97e0970/doc/review_po_translations.py)
 - [doc/source/getting_started/release_notes.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/release_notes.rst)
 - [doc/source/locale/de/LC_MESSAGES/getting_started/release_notes.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/de/LC_MESSAGES/getting_started/release_notes.po)
 - [doc/source/locale/es/LC_MESSAGES/getting_started/release_notes.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/es/LC_MESSAGES/getting_started/release_notes.po)
 - [doc/source/locale/fr/LC_MESSAGES/getting_started/release_notes.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/fr/LC_MESSAGES/getting_started/release_notes.po)
 - [doc/source/locale/it/LC_MESSAGES/getting_started/release_notes.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/it/LC_MESSAGES/getting_started/release_notes.po)
 - [doc/source/locale/zh_CN/LC_MESSAGES/getting_started/release_notes.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/zh_CN/LC_MESSAGES/getting_started/release_notes.po)
 - [xinference/_compat.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/_compat.py)
 - [xinference/api/restful_api.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py)
 - [xinference/api/tests/test_admin.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/tests/test_admin.py)
 - [xinference/client/restful/restful_client.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/restful/restful_client.py)
 - [xinference/client/tests/test_client.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/tests/test_client.py)
 - [xinference/constants.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py)
 - [xinference/core/model.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py)
 - [xinference/core/supervisor.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py)
 - [xinference/core/tests/test_restful_api.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_restful_api.py)
 - [xinference/core/tests/test_types.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_types.py)
 - [xinference/core/worker.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py)
 - [xinference/deploy/cmdline.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py)
 - [xinference/deploy/test/test_cmdline.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/test/test_cmdline.py)
 - [xinference/types.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/types.py)
 
  Xinference (Xorbits Inference) is a comprehensive distributed model inference system designed to simplify the deployment and serving of AI models at scale. This page introduces the system's purpose, key features, and high-level architecture.

 For detailed information about specific subsystems, refer to:

 
 - Distributed actor architecture and cluster coordination: Page 2 (System Architecture)
 - LLM serving capabilities and backend engines: Page 3 (LLM Serving System)
 - Support for embedding, image, audio, rerank, and video models: Page 4 (Model Types)
 - OpenAI-compatible REST API: Page 5 (RESTful API)
 - Python client and CLI tools: Page 6 (Client Interfaces)
 - Production deployment strategies: Page 7 (Deployment)
 - Custom model registration and extension: Page 8 (Customization and Extension)
 
 **Sources:** [README.md1-41](https://github.com/xorbitsai/inference/blob/d97e0970/README.md?plain=1#L1-L41) [xinference/constants.py1-81](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py#L1-L81)

 
## What is Xinference?

 Xinference is an open-source platform that streamlines the deployment and serving of AI models. It provides a unified interface for six distinct model types:

 
| Model Type | Use Cases |
|---|---|
| Large Language Models (LLM) | Text generation, chat, reasoning, tool calling, vision-language |
| Embedding Models | Text embeddings, semantic search, retrieval |
| Image Models | Text-to-image, image-to-image, inpainting, OCR |
| Audio Models | Speech recognition (ASR), text-to-speech (TTS), voice cloning |
| Rerank Models | Document reranking, relevance scoring |
| Video Models | Text-to-video generation |

 The system abstracts away the complexity of different inference backends, hardware platforms, and deployment configurations behind a single, OpenAI-compatible API.

 **Distributed Python Package:** Xinference is distributed as a Python package with three primary command-line entry points defined in `xinference/deploy/cmdline.py`:

 
 - `xinference-local`: Combined supervisor and worker for single-machine deployment [xinference/deploy/cmdline.py179-230](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L179-L230)
 - `xinference-supervisor`: Cluster coordinator for distributed deployments [xinference/deploy/cmdline.py232-276](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L232-L276)
 - `xinference-worker`: Compute node that connects to a supervisor [xinference/deploy/cmdline.py279-340](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L279-L340)
 
 **Key Design Principles:**

 
 - **Hardware Agnostic**: Runs on NVIDIA GPUs, AMD GPUs, CPUs, and Apple Silicon (Metal) [README.md72-86](https://github.com/xorbitsai/inference/blob/d97e0970/README.md?plain=1#L72-L86)
 - **Backend Flexible**: Automatically selects the optimal inference engine (vLLM, SGLang, Transformers, llama.cpp, MLX) [README.md47-54](https://github.com/xorbitsai/inference/blob/d97e0970/README.md?plain=1#L47-L54)
 - **OpenAI Compatible**: RESTful API matches OpenAI's specification, enabling drop-in replacement [xinference/api/restful_api.py121-174](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L121-L174)
 
 **Sources:** [README.md37-99](https://github.com/xorbitsai/inference/blob/d97e0970/README.md?plain=1#L37-L99) [xinference/deploy/cmdline.py126-340](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L126-L340) [xinference/api/restful_api.py50-94](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L50-L94)

 
## High-Level Architecture

 Xinference follows a **layered architecture** with a distributed actor-based orchestration layer built on `xoscar`.

 **System Component Diagram**

 
```

```

 **Architecture Layers:**

 
 - **Client Layer**: Multiple interfaces communicate through the RESTful API [xinference/client/restful/restful_client.py48-72](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/restful/restful_client.py#L48-L72)
 - **API Layer**: FastAPI-based server in `xinference/api/restful_api.py` provides OpenAI-compatible endpoints with JWT authentication [xinference/api/restful_api.py160-210](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L160-L210)
 - **Orchestration Layer**: Built on `xoscar` actor framework: 
 - `SupervisorActor` coordinates worker selection and model registry [xinference/core/supervisor.py127-174](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L127-L174)
 - `WorkerActor` manages GPU allocation and isolated actor subpools [xinference/core/worker.py128-212](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L128-L212)
 - `StatusGuardActor` monitors cluster health [xinference/core/supervisor.py93-94](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L93-L94)
 - **Model Layer**: The `ModelActor` implements request concurrency limits via the `@request_limit` decorator and handles OOM errors via `@oom_check` [xinference/core/model.py88-201](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L88-L201)
 
 **Sources:** [xinference/core/supervisor.py127-174](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L127-L174) [xinference/core/worker.py128-212](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L128-L212) [xinference/core/model.py88-204](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L88-L204) [xinference/api/restful_api.py160-210](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L160-L210)

 
## Request Lifecycle

 Typical model launch and inference request flow:

 **Model Launch and Inference Request Flow**

 
```

```

 **Component Responsibilities:**

 
 - **SupervisorActor**: Maintains the `_worker_address_to_worker` registry and uses `IdleFirstLaunchStrategy` for worker selection [xinference/core/supervisor.py61-130](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L61-L130)
 - **WorkerActor**: Handles package installation in virtual environments and manages model subpools [xinference/core/worker.py130-212](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L130-L212)
 - **ModelActor**: Wraps the underlying engine and manages serving state, including `_serve_count` for rate limiting [xinference/core/model.py95-168](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L95-L168)
 
 **Sources:** [xinference/core/supervisor.py61-174](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L61-L174) [xinference/core/worker.py130-212](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L130-L212) [xinference/core/model.py88-168](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L88-L168)

 
## Model Types and Capabilities

 Xinference supports diverse model types, abstracted through specific handles in the client:

 
| Model Type | Handle Class | Key API Methods |
|---|---|---|
| LLM (Chat) | RESTfulChatModelHandle | chat(), generate() |
| LLM (Generate) | RESTfulGenerateModelHandle | generate() |
| Embedding | RESTfulEmbeddingModelHandle | create_embedding() |
| Rerank | RESTfulRerankModelHandle | rerank() |
| Image | RESTfulImageModelHandle | text_to_image(), image_to_image() |
| Audio | RESTfulAudioModelHandle | speech_to_text(), text_to_speech() |

 **LLM Capabilities:**

 
 - **Reasoning**: Support for extracting thinking process content via `reasoning_content` in chat chunks [xinference/types.py221-232](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/types.py#L221-L232)
 - **Tool Calling**: Support for function calling and tool definitions in `PytorchGenerateConfig` [xinference/types.py259-276](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/types.py#L259-L276)
 - **Vision/Audio**: Multimodal support for models like Qwen2-VL or Qwen2-Audio [README.md60-63](https://github.com/xorbitsai/inference/blob/d97e0970/README.md?plain=1#L60-L63)
 
 **Sources:** [xinference/client/restful/restful_client.py73-250](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/restful/restful_client.py#L73-L250) [xinference/types.py188-276](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/types.py#L188-L276)

 
## Deployment Modes

 Xinference supports flexible deployment modes suited for different environments:

 
| Mode | Command | Use Case |
|---|---|---|
| Local | xinference-local | Single-machine development; combines Supervisor and Worker xinference/deploy/cmdline.py179-230 |
| Distributed | xinference-supervisor + xinference-worker | Multi-node production clusters; supervisor routes to multiple workers xinference/deploy/cmdline.py232-340 |
| Docker | xprobe/xinference | Containerized environments with pre-configured backends README.md15-18 |

 **Configuration and Environment Variables:**

 
 - `XINFERENCE_HOME`: Base directory for data (default: `~/.xinference`) [xinference/constants.py71-81](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py#L71-L81)
 - `XINFERENCE_CACHE_DIR`: Directory for model weights [xinference/constants.py85](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py#L85-L85)
 - `XINFERENCE_AUTH_ADVANCED`: Toggle for database-backed authentication [xinference/constants.py96-110](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py#L96-L110)
 - `XINFERENCE_MAX_CONCURRENT_LAUNCHES`: Limit simultaneous model downloads/launches [xinference/core/worker.py60](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L60-L60)
 
 **Sources:** [xinference/deploy/cmdline.py179-340](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L179-L340) [xinference/constants.py18-110](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py#L18-L110) [xinference/core/worker.py51-71](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L51-L71)
