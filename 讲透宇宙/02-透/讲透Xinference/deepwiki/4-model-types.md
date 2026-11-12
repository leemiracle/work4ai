> 来源: [https://deepwiki.com/xorbitsai/inference/4-model-types](https://deepwiki.com/xorbitsai/inference/4-model-types)
> DeepWiki xorbitsai/inference | Last indexed: 30 July 2026 (d97e09

# Model Types

  Relevant source files 
 - [xinference/model/audio/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/__init__.py)
 - [xinference/model/audio/custom.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/custom.py)
 - [xinference/model/audio/engine.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/engine.py)
 - [xinference/model/audio/engine_family.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/engine_family.py)
 - [xinference/model/core.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/core.py)
 - [xinference/model/custom.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/custom.py)
 - [xinference/model/embedding/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/__init__.py)
 - [xinference/model/embedding/core.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py)
 - [xinference/model/embedding/custom.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/custom.py)
 - [xinference/model/embedding/embed_family.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/embed_family.py)
 - [xinference/model/embedding/model_spec.json](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/model_spec.json)
 - [xinference/model/embedding/tests/test_embedding_models.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/tests/test_embedding_models.py)
 - [xinference/model/flexible/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/flexible/__init__.py)
 - [xinference/model/flexible/core.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/flexible/core.py)
 - [xinference/model/image/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/image/__init__.py)
 - [xinference/model/llm/core.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/core.py)
 - [xinference/model/rerank/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/__init__.py)
 - [xinference/model/rerank/core.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py)
 - [xinference/model/rerank/model_spec.json](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/model_spec.json)
 - [xinference/model/rerank/tests/test_rerank.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/tests/test_rerank.py)
 - [xinference/model/utils.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/utils.py)
 - [xinference/model/video/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/video/__init__.py)
 
  
## Purpose and Scope

 This page provides an overview of the different model types supported by Xinference and their common infrastructure. Each model type serves a specific AI task and has its own family definitions, specification structures, and supported inference backends. For detailed information about specific model types, see:

 
 - Large Language Models: [Large Language Models](https://deepwiki.com/xorbitsai/inference/4.1-large-language-models)
 - Embedding Models: [Embedding Models](https://deepwiki.com/xorbitsai/inference/4.2-embedding-models)
 - Image Generation Models: [Image Generation Models](https://deepwiki.com/xorbitsai/inference/4.3-image-generation-models)
 - Audio Models: [Audio Models](https://deepwiki.com/xorbitsai/inference/4.4-audio-models)
 - Reranking Models: [Reranking Models](https://deepwiki.com/xorbitsai/inference/4.5-reranking-models)
 - Video Models: [Video Models](https://deepwiki.com/xorbitsai/inference/4.6-video-models)
 
 For information about the model registry and cache management system, see [Model Registry and Cache Management](https://deepwiki.com/xorbitsai/inference/2.4-model-registry-and-cache-management). For inference backend details, see [LLM Serving System](https://deepwiki.com/xorbitsai/inference/3-llm-serving-system).

 
---

 
## Supported Model Types

 Xinference supports seven distinct model types, each with specialized capabilities and implementations:

 
| Model Type | Primary Use Case | Key Abilities | Factory Function |
|---|---|---|---|
| LLM | Text generation, chat, reasoning | generate, chat, tools, vision, audio, omni, reasoning, hybrid | create_llm_model_instance |
| embedding | Text/document vectorization | Encode text to dense vectors | create_embedding_model_instance |
| image | Image generation from text | Text-to-image, image editing, OCR | create_image_model_instance |
| audio | Speech processing | Transcription, translation, text-to-speech | create_audio_model_instance |
| rerank | Document ranking | Score document relevance | create_rerank_model_instance |
| video | Video generation | Text-to-video | create_video_model_instance |
| flexible | Custom model types | User-defined behaviors | create_flexible_model_instance |

 Sources: [xinference/model/core.py20-124](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/core.py#L20-L124)

 
---

 
## Model Type Dispatch Architecture

 The following diagram illustrates how the system dispatches requests from the generic `create_model_instance` entry point to specific model implementations and their corresponding base classes.

 
```

```

 The `create_model_instance` function in [xinference/model/core.py20-124](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/core.py#L20-L124) serves as the central dispatcher. It cleans up arguments (e.g., removing `enable_thinking` for non-LLM types [xinference/model/core.py43-45](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/core.py#L43-L45)) and routes the request to type-specific creation logic.

 Sources: [xinference/model/core.py20-124](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/core.py#L20-L124) [xinference/model/embedding/core.py224-257](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L224-L257) [xinference/model/rerank/core.py224-257](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L224-L257)

 
---

 
## Model Family and Specification Hierarchy

 Xinference uses a structured hierarchy to define models. **Model Families** act as containers for metadata (name, max tokens, language), while **Model Specifications** define technical details like format, hub location, and quantization.

 
```

```

 
### Embedding Model Families

 The `EmbeddingModelFamilyV2` class ([xinference/model/embedding/core.py91-135](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L91-L135)) includes:

 
 - `dimensions`: Output vector size (e.g., 1024 for `bge-large-en` [xinference/model/embedding/model_spec.json5](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/model_spec.json#L5-L5)).
 - `max_tokens`: Context limit.
 - `model_specs`: Array of `EmbeddingSpecV1` objects ([xinference/model/embedding/core.py84-87](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L84-L87)).
 
 
### Reranking Model Families

 The `RerankModelFamilyV2` class ([xinference/model/rerank/core.py73-112](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L73-L112)) includes:

 
 - `type`: Can be `normal`, `LLM-based`, or `LLM-based layerwise` ([xinference/model/rerank/core.py189-207](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L189-L207)).
 - `model_specs`: Array of `RerankSpecV1` objects ([xinference/model/rerank/core.py67-70](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L67-L70)).
 
 Sources: [xinference/model/embedding/core.py50-135](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L50-L135) [xinference/model/rerank/core.py46-112](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L46-L112) [xinference/model/embedding/model_spec.json1-43](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/model_spec.json#L1-L43)

 
---

 
## Engine and Backend Selection

 Backends are selected based on the `model_format` and available libraries. The system checks compatibility using `match_json` and `check_lib` methods.

 
### Engine Registries

 Each model type maintains a registry of supported engines:

 
 - **Embedding**: `EMBEDDING_ENGINES` ([xinference/model/embedding/__init__.py36](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/__init__.py#L36-L36)) includes `sentence_transformers`, `flag`, `vllm`, and `llama.cpp`.
 - **Rerank**: Engines include `sentence_transformers`, `vllm`, and `llama.cpp` ([xinference/model/rerank/model_spec.json36-41](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/model_spec.json#L36-L41)).
 
 
### Engine Matching Logic

 The system uses the `match` method in base classes (e.g., `EmbeddingModel.match` [xinference/model/embedding/core.py191-205](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L191-L205)) to verify:

 
 - **Library Presence**: `check_lib()` ensures required packages (like `vllm` or `transformers`) are installed.
 - **Format Compatibility**: `match_json()` verifies if the model format (e.g., `ggufv2`) is supported by the engine (e.g., `llama.cpp`).
 
 Sources: [xinference/model/embedding/core.py176-205](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L176-L205) [xinference/model/rerank/core.py148-177](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L148-L177) [xinference/model/embedding/__init__.py72-121](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/__init__.py#L72-L121)

 
---

 
## Registration and Custom Models

 Xinference supports both built-in models (defined in `model_spec.json` files) and user-defined custom models.

 
### Built-in Registration

 Built-in models are registered via `_install()` functions in each model type's `__init__.py`. For example:

 
 - **Embedding**: Loads from `model_spec.json` and flattens quantizations ([xinference/model/embedding/__init__.py150-171](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/__init__.py#L150-L171)).
 - **Audio/Image**: Uses `install_models_with_merge` to handle updates and local caching ([xinference/model/image/__init__.py65-91](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/image/__init__.py#L65-L91) [xinference/model/audio/__init__.py73-96](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/__init__.py#L73-L96)).
 
 
### Custom Model System

 Custom models allow users to bring their own weights by specifying a `model_uri` ([xinference/model/embedding/core.py67](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L67-L67) [xinference/model/rerank/core.py51](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L51-L51)).

 
 - **Persistence**: Custom models can be persisted to disk in the `XINFERENCE_MODEL_DIR/v2/` directory ([xinference/model/embedding/__init__.py57-70](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/__init__.py#L57-L70)).
 - **Validation**: Custom families (e.g., `CustomEmbeddingModelFamilyV2`) undergo schema validation before registration.
 
 Sources: [xinference/model/embedding/__init__.py45-70](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/__init__.py#L45-L70) [xinference/model/image/__init__.py43-101](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/image/__init__.py#L43-L101) [xinference/model/audio/__init__.py43-63](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/audio/__init__.py#L43-L63) [xinference/model/custom.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/custom.py)

 
---

 
## Model Versioning and Descriptions

 The system generates standardized descriptions for all models, which are used by the API to list available models.

 
 - **Embedding Descriptions**: `to_description()` ([xinference/model/embedding/core.py106-121](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L106-L121)) provides model type, dimensions, max tokens, and engine.
 - **Version Info**: `to_version_info()` ([xinference/model/embedding/core.py123-134](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L123-L134)) includes the cache status and file location.
 - **Rerank Type Detection**: For unknown rerankers, the system can auto-detect the type (e.g., `LLM-based`) by inspecting the tokenizer class ([xinference/model/rerank/core.py189-207](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L189-L207)).
 
 Sources: [xinference/model/embedding/core.py106-134](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/core.py#L106-L134) [xinference/model/rerank/core.py88-112](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L88-L112) [xinference/model/rerank/core.py189-207](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/rerank/core.py#L189-L207)
