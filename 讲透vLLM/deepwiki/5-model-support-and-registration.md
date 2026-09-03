# Model Support and Registration

> 来源: https://deepwiki.com/vllm-project/vllm/5-model-support-and-registration 抓取日期: 2026-09-02
> 章节: 第 5 章 模型支持与注册

---

Relevant source files

  * [csrc/cpu/spec_decode_utils.cpp](https://github.com/vllm-project/vllm/blob/185cada3/csrc/cpu/spec_decode_utils.cpp)
  * [docs/models/supported_models.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1)
  * [tests/model_executor/test_eagle_quantization.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/model_executor/test_eagle_quantization.py)
  * [tests/models/multimodal/generation/test_common.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/multimodal/generation/test_common.py)
  * [tests/models/multimodal/generation/vlm_utils/model_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/multimodal/generation/vlm_utils/model_utils.py)
  * [tests/models/registry.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/registry.py)
  * [tests/models/test_adapters.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/test_adapters.py)
  * [tests/test_config.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/test_config.py)
  * [tests/v1/spec_decode/test_eagle.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_eagle.py)
  * [tests/v1/spec_decode/test_eagle_step_kernel.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_eagle_step_kernel.py)
  * [tests/v1/spec_decode/test_max_len.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_max_len.py)
  * [tests/v1/spec_decode/test_mtp.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_mtp.py)
  * [vllm/config/cache.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/cache.py)
  * [vllm/config/model.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py)
  * [vllm/config/scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/scheduler.py)
  * [vllm/config/speculative.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/speculative.py)
  * [vllm/config/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/utils.py)
  * [vllm/config/vllm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py)
  * [vllm/engine/arg_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py)
  * [vllm/model_executor/models/adapters.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/adapters.py)
  * [vllm/model_executor/models/arcee.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/arcee.py)
  * [vllm/model_executor/models/config.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/config.py)
  * [vllm/model_executor/models/deepseek_eagle.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/deepseek_eagle.py)
  * [vllm/model_executor/models/deepseek_eagle3.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/deepseek_eagle3.py)
  * [vllm/model_executor/models/hunyuan_v1.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/hunyuan_v1.py)
  * [vllm/model_executor/models/hunyuan_vision.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/hunyuan_vision.py)
  * [vllm/model_executor/models/llama4_eagle.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/llama4_eagle.py)
  * [vllm/model_executor/models/llama_eagle.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/llama_eagle.py)
  * [vllm/model_executor/models/llama_eagle3.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/llama_eagle3.py)
  * [vllm/model_executor/models/registry.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py)
  * [vllm/model_executor/models/transformers/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/transformers/__init__.py)
  * [vllm/model_executor/models/transformers/base.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/transformers/base.py)
  * [vllm/model_executor/models/transformers/causal.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/transformers/causal.py)
  * [vllm/model_executor/models/transformers/legacy.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/transformers/legacy.py)
  * [vllm/model_executor/models/transformers/moe.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/transformers/moe.py)
  * [vllm/model_executor/models/transformers/pooling.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/transformers/pooling.py)
  * [vllm/model_executor/models/transformers/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/transformers/utils.py)
  * [vllm/model_executor/models/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/utils.py)
  * [vllm/transformers_utils/config.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py)
  * [vllm/transformers_utils/configs/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/configs/__init__.py)
  * [vllm/transformers_utils/configs/hunyuan_vl.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/configs/hunyuan_vl.py)
  * [vllm/transformers_utils/model_arch_config_convertor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/model_arch_config_convertor.py)
  * [vllm/transformers_utils/processors/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/processors/__init__.py)
  * [vllm/utils/cpu_triton_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/cpu_triton_utils.py)
  * [vllm/v1/spec_decode/dflash.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/dflash.py)
  * [vllm/v1/spec_decode/draft_model.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/draft_model.py)
  * [vllm/v1/spec_decode/eagle.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/eagle.py)
  * [vllm/v1/spec_decode/llm_base_proposer.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/llm_base_proposer.py)
  * [vllm/v1/spec_decode/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/utils.py)
  * [vllm/v1/worker/cpu/shm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu/shm.py)
  * [vllm/v1/worker/cpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu_model_runner.py)

## Purpose and Scope

This document explains how vLLM determines which model implementation to use for a given model and how new models are registered in the system. It covers:

  * The model registry system that maps HuggingFace architectures to vLLM's model implementations.
  * Architecture detection and configuration loading mechanisms.
  * Model implementation backends (native vLLM and Transformers modeling backend).
  * Model capability interfaces and queries.
  * Multimodal model registration and data flow.

For information about using supported models, see the documentation at [docs/models/supported_models.md1-142](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L1-L142)

* * *

## Model Registry Architecture

The model registry is the central system that maps model architecture names from HuggingFace `config.json` files to vLLM's model implementation classes. When a user loads a model, vLLM queries this registry to determine which Python class should handle the model's execution.

### Registry Structure

The registry maintains separate dictionaries for different model types, such as text generation, pooling (embedding), and multimodal models.

**Model Registry Entities Mapping**

**Registry Mapping Format** Each registry entry maps an architecture name to a tuple `(module_name, class_name)`:

[vllm/model_executor/models/registry.py72-156](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L72-L156)

The module name is relative to `vllm.model_executor.models`, so `"llama"` refers to `vllm/model_executor/models/llama.py`.

For details, see [Model Registry and Architecture Detection](/vllm-project/vllm/5.1-model-registry-and-architecture-detection).

**Sources:** [vllm/model_executor/models/registry.py72-211](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L72-L211) [vllm/model_executor/models/registry.py213-278](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L213-L278) [vllm/model_executor/models/registry.py311-527](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L311-L527)

* * *

## Architecture Detection and Config Loading

vLLM supports multiple configuration formats and custom configuration classes for models that extend standard HuggingFace properties or define new architectures.

### Configuration Loading Flow

**Config Loading Logic**

**Custom Configuration Registry** The `_CONFIG_REGISTRY` in `vllm/transformers_utils/config.py` handles models with non-standard configurations or those requiring vLLM-specific overrides. It uses `LazyConfigDict` to load configuration classes on demand from `vllm.transformers_utils.configs`. [vllm/transformers_utils/config.py72-142](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py#L72-L142)

Model Type| Custom Config Class| Purpose  
---|---|---  
`afmoe`| `AfmoeConfig`| MoE specific parameters [vllm/transformers_utils/config.py73](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py#L73-L73)  
`eagle`| `EAGLEConfig`| Speculative decoding configuration [vllm/transformers_utils/config.py120](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py#L120-L120)  
`deepseek_v4`| `DeepseekV4Config`| Next-gen Deepseek support [vllm/transformers_utils/config.py89](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py#L89-L89)  
`flex_olmo`| `FlexOlmoConfig`| Hybrid architecture configuration [vllm/transformers_utils/config.py92](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py#L92-L92)  
  
vLLM also provides `VerifyAndUpdateConfig` classes to programmatically adjust model configurations during loading. For instance, `UnlimitedOCRForCausalLMConfig` disables prefix caching and selects optimized attention backends based on hardware capability. [vllm/model_executor/models/config.py18-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/config.py#L18-L170)

For details, see [Configuration Loading and Parsing](/vllm-project/vllm/5.2-configuration-loading-and-parsing).

**Sources:** [vllm/transformers_utils/config.py72-142](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py#L72-L142) [vllm/model_executor/models/config.py18-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/config.py#L18-L170) [vllm/transformers_utils/model_arch_config_convertor.py25-166](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/model_arch_config_convertor.py#L25-L166)

* * *

## Model Implementation Backends

vLLM supports two primary model backends:

### 1\. Native vLLM Implementations

Located in `vllm/model_executor/models/`, these are highly optimized implementations using vLLM's custom kernels and attention backends. They are explicitly registered in the `_TEXT_GENERATION_MODELS` or `_POOLING_MODELS` maps. [docs/models/supported_models.md10-14](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L10-L14) [vllm/model_executor/models/registry.py72-101](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L72-L101)

### 2\. Transformers Modeling Backend

For models without a native implementation, vLLM can use the "Transformers modeling backend". This allows running models directly from the HuggingFace `transformers` library while still benefiting from vLLM's PagedAttention and continuous batching. [docs/models/supported_models.md16-47](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L16-L47)

**Compatibility Requirements for Transformers Backend:**

  * Model must be a Transformers-compatible custom model (with `auto_map`). [docs/models/supported_models.md54-63](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L54-L63)
  * Attention layers must use `ALL_ATTENTION_FUNCTIONS`. [docs/models/supported_models.md86](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L86-L86)
  * Model must set `_supports_attention_backend = True`. [docs/models/supported_models.md87](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L87-L87)
  * For MoE, the sparse block must have an `experts` attribute inheriting from `nn.ModuleList`. [docs/models/supported_models.md80-83](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L80-L83)

For details, see [Transformers Modeling Backend](/vllm-project/vllm/5.3-transformers-modeling-backend).

**Sources:** [docs/models/supported_models.md16-142](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L16-L142) [vllm/model_executor/models/registry.py279-308](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L279-L308)

* * *

## Model Capability Interfaces

vLLM uses an interface system to query model capabilities dynamically via `vllm.model_executor.models.interfaces`. This avoids hardcoding architecture checks throughout the engine.

Interface / Function| Code Entity| Purpose  
---|---|---  
Multimodal Support| `supports_multimodal`| Function checking if model accepts non-text inputs. [vllm/model_executor/models/registry.py54](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L54-L54)  
Pipeline Parallel| `supports_pp`| Checks if model logic allows PP splitting. [vllm/model_executor/models/registry.py57](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L57-L57)  
Mamba Support| `supports_mamba_prefix_caching`| Identifies SSM models with prefix caching. [vllm/model_executor/models/registry.py53](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L53-L53)  
Transcription| `supports_transcription`| Interface for ASR models like Whisper. [vllm/model_executor/models/registry.py59](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L59-L59)  
Attention Free| `is_attention_free`| Identifies models like Mamba that don't use standard attention. [vllm/model_executor/models/registry.py50](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L50-L50)  
  
**Sources:** [vllm/model_executor/models/registry.py47-68](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L47-L68) [vllm/model_executor/models/interfaces_base.py61-68](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/interfaces_base.py#L61-L68)

* * *

## Multimodal Model Support

Multimodal models (VLMs, Audio-LLMs, Omni models) require special registration to handle diverse data types like images, video, and audio.

### Multimodal Registry

vLLM supports a wide range of multimodal architectures, including vision-language models and audio-to-text models.

**Supported Modalities:**

  * **Vision:** `Llava` [tests/models/multimodal/generation/test_common.py114-132](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/multimodal/generation/test_common.py#L114-L132) `Qwen2-VL` [vllm/model_executor/models/registry.py228](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L228-L228)
  * **Audio:** `Whisper` [vllm/model_executor/models/registry.py255](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L255-L255)
  * **Omni:** `Qwen3-Omni-Moe` handles text, audio, and vision modalities simultaneously.

### Configuration Adaptation

Models can define specialized processing info to handle multimodal input transformation. The `MultiModalConfig` manages modalities and their specific processing requirements. [vllm/config/model.py16-23](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py#L16-L23)

**Multimodal Data Flow**

For details, see [Multimodal Model Support](/vllm-project/vllm/5.4-multimodal-model-support) and [Multimodal Data Processing](/vllm-project/vllm/5.5-multimodal-data-processing).

**Sources:** [vllm/config/model.py16-23](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py#L16-L23) [vllm/model_executor/models/registry.py213-278](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L213-L278) [vllm/config/multimodal.py1-96](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/multimodal.py#L1-L96)

* * *

## Speculative Decoding Support

vLLM supports several speculative decoding methods, including draft models, EAGLE, and Medusa. These are configured via `SpeculativeConfig` and registered in the speculative decoding system.

**Speculative Methods Mapping**

[vllm/config/speculative.py69-79](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/speculative.py#L69-L79)

For details, see [Speculative Decoding](/vllm-project/vllm/4.5-speculative-decoding).

**Sources:** [vllm/config/speculative.py69-79](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/speculative.py#L69-L79) [vllm/transformers_utils/config.py144](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py#L144-L144)

* * *

## Child Pages

  * [Model Registry and Architecture Detection](/vllm-project/vllm/5.1-model-registry-and-architecture-detection) — Detailed mapping of HF architectures to vLLM implementations and capability queries.
  * [Configuration Loading and Parsing](/vllm-project/vllm/5.2-configuration-loading-and-parsing) — Documentation on `HFConfigParser`, `VerifyAndUpdateConfig`, and configuration adaptation.
  * [Transformers Modeling Backend](/vllm-project/vllm/5.3-transformers-modeling-backend) — Technical details on using the Transformers backend for non-native models.
  * [Multimodal Model Support](/vllm-project/vllm/5.4-multimodal-model-support) — Interface definitions and supported modalities for VLMs, Audio, and Omni models.
  * [Multimodal Data Processing](/vllm-project/vllm/5.5-multimodal-data-processing) — Handling of `MultiModalDataDict` and tensor conversion for images/audio/video.
