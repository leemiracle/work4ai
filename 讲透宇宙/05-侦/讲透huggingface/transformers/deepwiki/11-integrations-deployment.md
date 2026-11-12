<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/transformers · page 11 Integrations & Deployment · fetched 2026-10-26 -->

# Integrations & Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/en/_redirects.yml](docs/source/en/_redirects.yml)
- [docs/source/en/community_integrations/litert.md](docs/source/en/community_integrations/litert.md)
- [docs/source/en/main_classes/peft.md](docs/source/en/main_classes/peft.md)
- [docs/source/en/peft.md](docs/source/en/peft.md)
- [docs/source/en/perf_infer_gpu_multi.md](docs/source/en/perf_infer_gpu_multi.md)
- [docs/source/en/serve-cli/serving.md](docs/source/en/serve-cli/serving.md)
- [docs/source/en/serve-cli/serving_optims.md](docs/source/en/serve-cli/serving_optims.md)
- [docs/source/en/tensor_parallelism.md](docs/source/en/tensor_parallelism.md)
- [docs/source/zh/perf_infer_gpu_multi.md](docs/source/zh/perf_infer_gpu_multi.md)
- [examples/pytorch/transformers_serve_cb_eval_job.py](examples/pytorch/transformers_serve_cb_eval_job.py)
- [src/transformers/cli/add_new_model_like.py](src/transformers/cli/add_new_model_like.py)
- [src/transformers/cli/chat.py](src/transformers/cli/chat.py)
- [src/transformers/cli/serve.py](src/transformers/cli/serve.py)
- [src/transformers/cli/serving/__init__.py](src/transformers/cli/serving/__init__.py)
- [src/transformers/cli/serving/chat_completion.py](src/transformers/cli/serving/chat_completion.py)
- [src/transformers/cli/serving/completion.py](src/transformers/cli/serving/completion.py)
- [src/transformers/cli/serving/response.py](src/transformers/cli/serving/response.py)
- [src/transformers/cli/serving/server.py](src/transformers/cli/serving/server.py)
- [src/transformers/cli/serving/transcription.py](src/transformers/cli/serving/transcription.py)
- [src/transformers/cli/serving/utils.py](src/transformers/cli/serving/utils.py)
- [src/transformers/cli/system.py](src/transformers/cli/system.py)
- [src/transformers/cli/transformers.py](src/transformers/cli/transformers.py)
- [src/transformers/conversion_mapping.py](src/transformers/conversion_mapping.py)
- [src/transformers/core_model_loading.py](src/transformers/core_model_loading.py)
- [src/transformers/integrations/accelerate.py](src/transformers/integrations/accelerate.py)
- [src/transformers/integrations/hub_kernels.py](src/transformers/integrations/hub_kernels.py)
- [src/transformers/integrations/npu_flash_attention.py](src/transformers/integrations/npu_flash_attention.py)
- [src/transformers/integrations/peft.py](src/transformers/integrations/peft.py)
- [src/transformers/integrations/tensor_parallel.py](src/transformers/integrations/tensor_parallel.py)
- [src/transformers/modeling_flash_attention_utils.py](src/transformers/modeling_flash_attention_utils.py)
- [src/transformers/modeling_utils.py](src/transformers/modeling_utils.py)
- [src/transformers/utils/generic.py](src/transformers/utils/generic.py)
- [src/transformers/utils/kernel_config.py](src/transformers/utils/kernel_config.py)
- [tests/cli/conftest.py](tests/cli/conftest.py)
- [tests/cli/test_chat.py](tests/cli/test_chat.py)
- [tests/cli/test_serve.py](tests/cli/test_serve.py)
- [tests/kernels/test_kernels.py](tests/kernels/test_kernels.py)
- [tests/peft_integration/test_peft_integration.py](tests/peft_integration/test_peft_integration.py)
- [tests/tensor_parallel/test_tensor_parallel.py](tests/tensor_parallel/test_tensor_parallel.py)
- [tests/test_modeling_common.py](tests/test_modeling_common.py)
- [tests/utils/test_add_new_model_like.py](tests/utils/test_add_new_model_like.py)
- [tests/utils/test_core_model_loading.py](tests/utils/test_core_model_loading.py)
- [tests/utils/test_generic.py](tests/utils/test_generic.py)
- [tests/utils/test_modeling_utils.py](tests/utils/test_modeling_utils.py)

</details>



This page provides an overview of how the Hugging Face Transformers library integrates with external fine-tuning ecosystems, export frameworks for optimized runtimes, and the built-in command-line interface and serving stack.

Transformers bridges standard model weights and runtime environments via three main subsystems:

- **PEFT Integration**: Seamless injection, hotswapping, and training of parameter-efficient adapters (LoRA, IA³) using the `peft` library, implemented via the `PeftAdapterMixin` [src/transformers/integrations/peft.py:57-144]().
- **Model Export**: Serialization and conversion pipelines for targeting deployment runtimes such as ONNX and ExecuTorch through the `exporters/` infrastructure.
- **CLI & Serving Stack**: A command-line interface with utilities for chat, environment/version info, model downloads, and an OpenAI-compatible HTTP inference server (`transformers serve`) built on FastAPI and Uvicorn [src/transformers/cli/serve.py:15-126]().

```mermaid
title "Integrations & Deployment Architecture"
graph TD
    subgraph NaturalLanguageSpace["Natural Language Space"]
        PEFT["Parameter-Efficient Fine-Tuning (PEFT)"]
        EXPORT["Model Export & Optimization"]
        SERVING["OpenAI-Compatible HTTP Serving"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        PAM[PeftAdapterMixin\nsrc/transformers/integrations/peft.py]:::code
        EXP[HfExporter / OnnxExporter / ExecuTorchExporter\nsrc/transformers/exporters/]:::code
        SRV[Serve & ModelManager\nsrc/transformers/cli/serve.py]:::code
    end

    classDef code fill:none,stroke:#000,stroke-width:1px;

    PEFT --> PAM
    EXPORT --> EXP
    SERVING --> SRV
```

Sources: `src/transformers/integrations/peft.py:57-144`, `src/transformers/cli/serve.py:15-126`, `src/transformers/exporters/`

---

## 11.1. PEFT & Parameter-Efficient Fine-Tuning

The Transformers library seamlessly integrates with the PEFT (Parameter-Efficient Fine-Tuning) ecosystem through the `PeftAdapterMixin` class mixed into `PreTrainedModel` subclasses [src/transformers/integrations/peft.py:57-144](). This enables:

- Loading and injecting adapter weights (e.g., LoRA, IA³) from local storage or the Hugging Face Hub.
- Adding and managing multiple adapters within a single model instance.
- Activating, deactivating, and merging adapters flexibly.
- In-place hotswapping of adapters, facilitating efficient switching without recompilation when using `torch.compile`.

The integration requires `peft >= 0.20.0` [src/transformers/integrations/peft.py:46-48]() and supports all non-prompt learning PEFT methods (prompt tuning is outside this scope). The mixin supports trainability flags and low-CPU-memory loading modes for adapters.

Extensive integration tests verify functionality, including correct adapter injection, state dict consistency, save/load behavior, and enable/disable mechanics [tests/peft_integration/test_peft_integration.py:63-174]().

For in-depth usage and API details, see the dedicated child page [PEFT & Parameter-Efficient Fine-Tuning](#11.1).

Sources: `src/transformers/integrations/peft.py:46-144`, `tests/peft_integration/test_peft_integration.py:63-174`

---

## 11.2. Model Export

Transformers includes a robust export subsystem designed to convert models into formats optimized for serving and deployment. The `exporters/` subpackage provides:

- Base exporter infrastructure with configuration contracts (`ExportConfigMixin`).
- Specific exporters like `HfExporter`, `DynamoExporter` (for TorchDynamo), `OnnxExporter` (for ONNX format), and `ExecuTorchExporter` (for ExecuTorch runtime).
- Specialized modules such as `TorchExportableModuleForDecoderOnlyLM` to handle architectural constraints during export, particularly for decoder-only language models.

This export framework enables users to transform their models to run efficiently on a variety of backends that support hardware acceleration, optimized graph execution, and cross-platform interoperability.

For details on using the exporters and supported formats, refer to the child page [Model Export](#11.2).

Sources: `src/transformers/exporters/`

---

## 11.3. CLI & Serving

The Transformers command-line interface (CLI) exposes utilities that cover a range of developer and deployment workflows:

- Chat and interactive inference commands [src/transformers/cli/chat.py]().
- Serving models via an OpenAI-compatible HTTP API [src/transformers/cli/serve.py]().
- Downloading models and environment/version reporting [src/transformers/cli/system.py]().
- Scaffolding new model implementations with `add_new_model_like` [src/transformers/cli/add_new_model_like.py]().

The core HTTP server command `transformers serve` runs a highly modular FastAPI/Uvicorn-based server that supports multiple REST API endpoints compatible with OpenAI SDKs:

- `/v1/chat/completions` [src/transformers/cli/serving/chat_completion.py]()
- `/v1/completions` [src/transformers/cli/serving/completion.py]()
- `/v1/responses` [src/transformers/cli/serving/response.py]()
- `/v1/audio/transcriptions` [src/transformers/cli/serving/transcription.py]()
- `/v1/models` [src/transformers/cli/serving/model_manager.py]()
- `/load_model` [src/transformers/cli/serving/model_manager.py]()

The serving stack is implemented under `cli/serving/`, which contains a `ModelManager` for model lifecycle management [src/transformers/cli/serving/model_manager.py](), handlers for different request types (`ChatCompletionHandler` [src/transformers/cli/serving/chat_completion.py](), `CompletionHandler` [src/transformers/cli/serving/completion.py](), `TranscriptionHandler` [src/transformers/cli/serving/transcription.py](), `ResponseHandler` [src/transformers/cli/serving/response.py]()), and the main server builder function [src/transformers/cli/serving/server.py]().

```mermaid
title "Serving Stack Mapping to Code Entities"
graph TD
    subgraph "Serving Subpackage Code Entities"
        MM["ModelManager\nsrc/transformers/cli/serving/model_manager.py"]:::code
        CCH["ChatCompletionHandler\nsrc/transformers/cli/serving/chat_completion.py"]:::code
        COMP["CompletionHandler\nsrc/transformers/cli/serving/completion.py"]:::code
        RESP["ResponseHandler\nsrc/transformers/cli/serving/response.py"]:::code
        TRN["TranscriptionHandler\nsrc/transformers/cli/serving/transcription.py"]:::code
        SRV["build_server()\nsrc/transformers/cli/serving/server.py"]:::code
    end

    subgraph "REST API Routes"
        API1["/v1/chat/completions"]
        API2["/v1/completions"]
        API3["/v1/audio/transcriptions"]
        API4["/load_model"]
        API5["/v1/responses"]
    end

    API1 --> CCH
    API2 --> COMP
    API3 --> TRN
    API4 --> MM
    API5 --> RESP
    CCH --> RESP
    COMP --> RESP
    TRN --> RESP
    SRV --> CCH
    SRV --> COMP
    SRV --> TRN
    SRV --> MM
    SRV --> RESP
```

This serving infrastructure supports flexible device placement, quantization (e.g., BitsAndBytes), continuous batching, and attention backend selection to optimize throughput and latency for real-world deployments.

For complete details, see the child page on [CLI & Serving](#11.3).

Sources: `src/transformers/cli/serve.py:15-126`, `src/transformers/cli/serving/utils.py:15-30`, `src/transformers/cli/chat.py`, `src/transformers/cli/system.py`, `src/transformers/cli/add_new_model_like.py`, `src/transformers/cli/serving/chat_completion.py`, `src/transformers/cli/serving/completion.py`, `src/transformers/cli/serving/response.py`, `src/transformers/cli/serving/transcription.py`, `src/transformers/cli/serving/model_manager.py`, `src/transformers/cli/serving/server.py`

---

# Summary

The Integrations & Deployment section in Transformers integrates core model architectures with external ecosystems, deployment runtimes, and serving infrastructure by providing:

- *PEFT* integration for efficient adapter fine-tuning without heavy base model retraining.
- *Exporters* that convert PyTorch models into optimized formats for various runtimes such as ONNX and ExecuTorch.
- A *rich CLI and serving stack* enabling OpenAI-compatible REST APIs and command-line interactions for inference, serving, and management.

Each subsystem is designed to be modular, with clear code ownership and APIs to allow flexible extension and customization for a wide array of use cases in research and production.

For implementation-level details, usage instructions, and examples, please consult the linked child pages:

- [PEFT & Parameter-Efficient Fine-Tuning](#11.1)
- [Model Export](#11.2)
- [CLI & Serving](#11.3)

---

