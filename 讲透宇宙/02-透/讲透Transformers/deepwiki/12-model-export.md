> 来源: [https://deepwiki.com/huggingface/transformers/12-model-export](https://deepwiki.com/huggingface/transformers/12-model-export)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Model Export

  Relevant source files 
 - [docs/source/en/internal/generation_utils.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/internal/generation_utils.md?plain=1)
 - [docs/source/en/main_classes/text_generation.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/text_generation.md?plain=1)
 - [docs/source/ko/internal/generation_utils.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ko/internal/generation_utils.md?plain=1)
 - [src/transformers/cache_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py)
 - [src/transformers/generation/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/__init__.py)
 - [src/transformers/generation/candidate_generator.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/candidate_generator.py)
 - [src/transformers/generation/configuration_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/configuration_utils.py)
 - [src/transformers/generation/logits_process.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/logits_process.py)
 - [src/transformers/generation/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py)
 - [src/transformers/generation/watermarking.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/watermarking.py)
 - [src/transformers/integrations/executorch.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py)
 - [src/transformers/masking_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/masking_utils.py)
 - [tests/generation/test_candidate_generator.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_candidate_generator.py)
 - [tests/generation/test_logits_process.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_logits_process.py)
 - [tests/generation/test_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_utils.py)
 - [tests/utils/test_cache_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_cache_utils.py)
 - [tests/utils/test_masking_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_masking_utils.py)
 
  Model export in the Transformers library facilitates the transition from research-oriented PyTorch modules to production-ready formats such as **ONNX** and **ExecuTorch**. This subsystem leverages `torch.export` and `torch.compile` infrastructure to ensure that complex generative models—specifically those utilizing KV caching and dynamic attention—can be deployed on diverse hardware backends.

 
## Core Export Architecture

 The export infrastructure is designed around the principle of wrapping `PreTrainedModel` instances into export-friendly containers that satisfy the strict requirements of `torch.export`.

 
### TorchExportableModuleForDecoderOnlyLM

 The `TorchExportableModuleForDecoderOnlyLM` class is a specialized wrapper for decoder-only language models [src/transformers/integrations/executorch.py187-192](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L187-L192). It standardizes the forward pass to accept `input_ids` and `cache_position`, which are critical for models using `StaticCache` during deployment [src/transformers/integrations/executorch.py236-241](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L236-L241).

 Key responsibilities include:

 
 - **Cache Initialization**: It initializes a `StaticCache` based on the model's configuration and a provided `max_cache_len` [src/transformers/integrations/executorch.py205-212](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L205-L212).
 - **Attribute Management**: It mirrors essential model attributes like `config`, `generation_config`, and `device` to the wrapper level [src/transformers/integrations/executorch.py221-224](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L221-L224).
 - **Forward Logic**: It ensures the model is called with `use_cache=True` and passes the `StaticCache` instance explicitly to the underlying model's forward method [src/transformers/integrations/executorch.py240-241](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L240-L241).
 
 
### Visual-Language Model (VLM) Export

 For multimodal models, `TorchExportableModuleForVLM` provides a structured approach to export distinct components of the pipeline [src/transformers/integrations/executorch.py35-43](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L35-L43):

 
 - **Vision Encoder**: Processes raw pixels into visual features [src/transformers/integrations/executorch.py69-91](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L69-L91).
 - **Connector/Projector**: Maps visual features into the text embedding space [src/transformers/integrations/executorch.py93-116](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L93-L116).
 - **Text Decoder**: Generates text using the combined embeddings [src/transformers/integrations/executorch.py118-143](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L118-L143).
 
 
### Data Flow for ExecuTorch Export

 The following diagram illustrates how a standard `PreTrainedModel` is transformed into an ExecuTorch-compatible `ExportedProgram`.

 **Diagram: Model Export Pipeline**

 
```

```

 **Sources:** [src/transformers/integrations/executorch.py187-241](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L187-L241), [src/transformers/integrations/executorch.py45-67](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L45-L67)

 
---

 
## Integration with KV Caching

 Exporting generative models requires a static representation of the KV cache to avoid dynamic memory allocation during inference.

 
### StaticCache and Exporting

 The `StaticCache` class is the primary mechanism for exportable KV caching [src/transformers/cache_utils.py92](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L92-L92). Unlike `DynamicCache`, it pre-allocates tensors of a fixed `max_cache_len` [src/transformers/cache_utils.py105-120](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L105-L120).

 During the export process:

 
 - The `TorchExportableModuleForDecoderOnlyLM` creates a `StaticCache` [src/transformers/integrations/executorch.py205](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L205-L205).
 - The `forward` method uses `cache_position` to index into the pre-allocated tensors [src/transformers/integrations/executorch.py236-241](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L236-L241).
 - This allows `torch.export` to trace the graph without encountering dynamic shape changes related to the cache size.
 
 
### Component Mapping for Export

 
| Entity | Role in Export | File Reference |
|---|---|---|
| StaticCache | Pre-allocated KV storage for fixed-shape tracing. | src/transformers/cache_utils.py92 |
| cache_position | Tensor indicating the index in StaticCache for new tokens. | src/transformers/integrations/executorch.py236 |
| max_cache_len | Defines the static boundary for the exported model's memory. | src/transformers/integrations/executorch.py201 |
| torch.export.Dim | Used to define dynamic sequence lengths within static cache bounds. | src/transformers/integrations/executorch.py129 |

 **Sources:** [src/transformers/cache_utils.py86-121](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L86-L121), [src/transformers/integrations/executorch.py118-143](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L118-L143)

 
---

 
## Exporting for Specific Backends

 
### ExecuTorch Integration

 ExecuTorch requires models to be exported via `torch.export`. The library provides `export_with_dynamic_cache` and `register_dynamic_cache_export_support` to facilitate this [tests/utils/test_cache_utils.py69](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_cache_utils.py#L69-L69).

 The process typically involves:

 
 - Wrapping the model in `TorchExportableModuleForDecoderOnlyLM` [src/transformers/integrations/executorch.py187](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L187-L187).
 - Defining `dynamic_shapes` for `input_ids` and `cache_position` [src/transformers/integrations/executorch.py131-134](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L131-L134).
 - Calling the `.export()` method which invokes `torch.export.export` [src/transformers/integrations/executorch.py254-266](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L254-L266).
 
 
### ONNX Export

 Modern ONNX exports for LLMs increasingly rely on the same `StaticCache` and `torch.export` logic used for ExecuTorch to handle modern LLM architectures. This ensures that the generated ONNX graph contains fixed-size KV cache buffers that are updated in-place using `cache_position` indices. The `convert_and_export_with_cache` utility is used to bridge these gaps [tests/utils/test_cache_utils.py57](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_cache_utils.py#L57-L57).

 **Diagram: Entity Association (Code Space)**

 
```

```

 **Sources:** [src/transformers/integrations/executorch.py35-67](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L35-L67), [src/transformers/integrations/executorch.py187-212](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L187-L212), [src/transformers/cache_utils.py92](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L92-L92)

 
---

 
## Handling Dynamic Constraints

 To maintain performance while remaining within static export constraints, the library uses `torch.export.Dim` to represent the current sequence length as a dynamic variable that is strictly less than `max_cache_len` [src/transformers/integrations/executorch.py128-129](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L128-L129).

 
```

```

 **Sources:** [src/transformers/integrations/executorch.py129-134](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py#L129-L134)

 This approach ensures that the exported graph is valid for any sequence length up to the pre-allocated cache limit, enabling efficient execution on mobile and edge devices via ExecuTorch. The `ExportConfigMixin` and `HfExporter` (not shown in full but referenced in architecture) provide the high-level orchestration for these low-level `torch.export` calls.
