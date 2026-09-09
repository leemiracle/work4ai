> 来源: [https://deepwiki.com/xorbitsai/inference/8-customization-and-extension](https://deepwiki.com/xorbitsai/inference/8-customization-and-extension)
> DeepWiki xorbitsai/inference | Last indexed: 30 July 2026 (d97e09

# Customization and Extension

  Relevant source files 
 - [doc/source/locale/zh_CN/LC_MESSAGES/models/custom.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/zh_CN/LC_MESSAGES/models/custom.po)
 - [doc/source/locale/zh_CN/LC_MESSAGES/models/virtualenv.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/zh_CN/LC_MESSAGES/models/virtualenv.po)
 - [doc/source/locale/zh_CN/LC_MESSAGES/user_guide/distributed_inference.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/zh_CN/LC_MESSAGES/user_guide/distributed_inference.po)
 - [doc/source/locale/zh_CN/LC_MESSAGES/user_guide/launch.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/zh_CN/LC_MESSAGES/user_guide/launch.po)
 - [doc/source/models/custom.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/models/custom.rst)
 - [doc/source/models/virtualenv.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/models/virtualenv.rst)
 - [doc/source/user_guide/distributed_inference.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/distributed_inference.rst)
 - [doc/source/user_guide/launch.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/launch.rst)
 - [xinference/model/audio/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/__init__.py)
 - [xinference/model/audio/custom.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/custom.py)
 - [xinference/model/audio/engine.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/engine.py)
 - [xinference/model/audio/engine_family.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/engine_family.py)
 - [xinference/model/custom.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/custom.py)
 - [xinference/model/embedding/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/__init__.py)
 - [xinference/model/embedding/custom.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/custom.py)
 - [xinference/model/embedding/embed_family.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/embed_family.py)
 - [xinference/model/flexible/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/flexible/__init__.py)
 - [xinference/model/flexible/core.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/flexible/core.py)
 - [xinference/model/image/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/image/__init__.py)
 - [xinference/model/rerank/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/__init__.py)
 - [xinference/model/video/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/video/__init__.py)
 
  This section covers advanced topics for extending Xinference beyond its built-in models and capabilities. Xinference provides a comprehensive extension system that allows users to:

 
 - Register custom models without modifying source code.
 - Define model specifications for new model families.
 - Configure chat templates and prompt formats.
 - Implement custom backend engines.
 - Utilize **Model Virtual Environments** to isolate model-specific dependencies and avoid version conflicts.
 
 For API-level model registration endpoints, see [Model Registration Endpoints](https://deepwiki.com/xorbitsai/inference/5.3-model-registration-endpoints). For environment configuration details, see [Environment Configuration](https://deepwiki.com/xorbitsai/inference/7.4-environment-configuration).

 
## Overview of Extensibility

 Xinference's extensibility is built around three core abstractions:

 
 - **Model Families** - Define a group of related models (e.g., the `qwen2.5-chat` family includes multiple sizes and quantizations).
 - **Model Specifications** - Describe specific model variants (format, size, quantization, download sources, and URIs).
 - **Engine Matching** - Automatically select optimal backend engines (vLLM, SGLang, Transformers, etc.) based on model specs and hardware.
 
 The system supports custom model registration for all model types:

 
 - Large Language Models (LLM)
 - Embedding Models
 - Image Generation Models
 - Audio Models (ASR/TTS)
 - Rerank Models
 - Video Models
 - Flexible Models (Custom launchers)
 
 Sources: [xinference/model/llm/llm_family.py128-208](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/llm_family.py#L128-L208) [xinference/model/embedding/core.py83-123](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L83-L123) [xinference/model/flexible/core.py28-61](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/flexible/core.py#L28-L61)

 
## Extension Architecture

 
```

```

 **Extension Architecture Diagram**

 The diagram shows how custom models flow through the registration system. Built-in models are loaded at startup, while custom models are validated dynamically. Starting from v2.0, **Model Virtual Environments** are enabled by default to ensure that each model runs with its required library versions without affecting the system environment.

 Sources: [xinference/model/llm/__init__.py116-134](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/__init__.py#L116-L134) [xinference/model/embedding/__init__.py50-70](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/__init__.py#L50-L70) [doc/source/models/virtualenv.rst63-70](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/models/virtualenv.rst#L63-L70) [xinference/model/audio/custom.py32-70](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/custom.py#L32-L70)

 
## Model Family Hierarchy

 
```

```

 **Model Family Class Hierarchy**

 This diagram shows the relationship between base and custom model family classes. `FlexibleModelSpec` allows for models that don't fit standard patterns by specifying a custom launcher and arguments.

 Sources: [xinference/model/llm/llm_family.py128-208](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/llm_family.py#L128-L208) [xinference/model/embedding/custom.py25-29](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/custom.py#L25-L29) [xinference/model/audio/custom.py32-36](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/custom.py#L32-L36) [xinference/model/flexible/core.py28-61](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/flexible/core.py#L28-L61)

 
## Key Extension Features

 
### Direct Launch Interface

 Since `v0.14.0`, you can launch existing models by passing a `model_path` directly to the launch interface. This bypasses the need for manual registration if the `model_family` is already supported by Xinference.

 Sources: [doc/source/models/custom.rst11-13](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/models/custom.rst#L11-L13)

 
### Model Virtual Environments

 Introduced to solve dependency conflicts (e.g., one model requiring an old version of `transformers` while another requires the latest).

 
 - **Default Behavior**: Enabled by default in v2.0 (`XINFERENCE_ENABLE_VIRTUAL_ENV=1`).
 - **Isolation**: Each model gets a dedicated environment created via the `uv` tool.
 - **Customization**: Users can specify additional packages at launch time using `--virtual-env-package` or `-vp`.
 
 Sources: [doc/source/models/virtualenv.rst21-32](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/models/virtualenv.rst#L21-L32) [doc/source/models/virtualenv.rst63-70](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/models/virtualenv.rst#L63-L70) [doc/source/models/virtualenv.rst104-110](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/models/virtualenv.rst#L104-L110)

 
### Flexible Models

 The `FlexibleModel` and `FlexibleModelSpec` classes allow users to integrate models with custom loading and inference logic. A `launcher` string identifies the execution strategy, and `launcher_args` provides configuration.

 Sources: [xinference/model/flexible/core.py28-61](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/flexible/core.py#L28-L61) [xinference/model/flexible/core.py81-123](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/flexible/core.py#L81-L123)

 
## Storage and Persistence

 Custom model definitions are persisted as JSON files in the `XINFERENCE_MODEL_DIR`.

 
| Model Type | Storage Path |
|---|---|
| LLM | {XINFERENCE_HOME}/v2/llm/ |
| Embedding | {XINFERENCE_HOME}/v2/embedding/ |
| Audio | {XINFERENCE_HOME}/v2/audio/ |
| Image | {XINFERENCE_HOME}/v2/image/ |
| Rerank | {XINFERENCE_HOME}/v2/rerank/ |

 Sources: [xinference/model/embedding/__init__.py57-59](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/__init__.py#L57-L59) [xinference/model/audio/__init__.py50-51](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/__init__.py#L50-L51) [xinference/model/image/__init__.py50-51](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/image/__init__.py#L50-L51) [xinference/model/rerank/__init__.py57-58](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/__init__.py#L57-L58)

 
## Child Pages

 For detailed implementation guides, refer to the following sub-sections:

 
 - **[Custom Model Registration](https://deepwiki.com/xorbitsai/inference/8.1-custom-model-registration)**: Explains the `register_model` API, persistence flags, and how to use `model_uri` for local weights.
 - **[Model Specifications and Schemas](https://deepwiki.com/xorbitsai/inference/8.2-model-specifications-and-schemas)**: Documents the JSON schema requirements for LLMs, embeddings, and other types, including required fields and validation rules.
 - **[Chat Templates and Prompt Formatting](https://deepwiki.com/xorbitsai/inference/8.3-chat-templates-and-prompt-formatting)**: Explains how to define Jinja2-based chat templates, stop tokens, and reasoning tags (start/end tags) for custom models.
 - **[Adding Custom Backend Engines](https://deepwiki.com/xorbitsai/inference/8.4-adding-custom-backend-engines)**: A guide for developers wanting to implement entirely new inference engines and register them via the `match_json` logic.
