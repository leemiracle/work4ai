> 来源: [https://deepwiki.com/huggingface/transformers/9-attention-backends-and-kernel-integration](https://deepwiki.com/huggingface/transformers/9-attention-backends-and-kernel-integration)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Attention Backends & Kernel Integration

  Relevant source files 
 - [docs/source/en/attention_interface.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/attention_interface.md?plain=1)
 - [docs/source/en/cache_explanation.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/cache_explanation.md?plain=1)
 - [docs/source/en/kernel_doc/loading_kernels.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/kernel_doc/loading_kernels.md?plain=1)
 - [docs/source/en/kernel_doc/writing_kernels.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/kernel_doc/writing_kernels.md?plain=1)
 - [docs/source/en/main_classes/kernels.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/kernels.md?plain=1)
 - [docs/source/en/model_doc/kyutai_speech_to_text.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/model_doc/kyutai_speech_to_text.md?plain=1)
 - [docs/source/en/model_doc/reformer.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/model_doc/reformer.md?plain=1)
 - [docs/source/en/model_doc/rwkv.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/model_doc/rwkv.md?plain=1)
 - [docs/source/en/perplexity.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/perplexity.md?plain=1)
 - [docs/source/en/tokenizer_summary.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/tokenizer_summary.md?plain=1)
 - [docs/source/es/tokenizer_summary.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/es/tokenizer_summary.md?plain=1)
 - [docs/source/ko/cache_explanation.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ko/cache_explanation.md?plain=1)
 - [src/transformers/debug_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/debug_utils.py)
 - [src/transformers/integrations/flash_attention.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/flash_attention.py)
 - [src/transformers/integrations/hub_kernels.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/hub_kernels.py)
 - [src/transformers/integrations/npu_flash_attention.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/npu_flash_attention.py)
 - [src/transformers/integrations/sdpa_attention.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/sdpa_attention.py)
 - [src/transformers/modeling_flash_attention_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_flash_attention_utils.py)
 - [src/transformers/models/diffllama/modeling_diffllama.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/diffllama/modeling_diffllama.py)
 - [src/transformers/models/diffllama/modular_diffllama.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/diffllama/modular_diffllama.py)
 - [src/transformers/models/kyutai_speech_to_text/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/kyutai_speech_to_text/__init__.py)
 - [src/transformers/models/kyutai_speech_to_text/configuration_kyutai_speech_to_text.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/kyutai_speech_to_text/configuration_kyutai_speech_to_text.py)
 - [src/transformers/models/kyutai_speech_to_text/convert_kyutai_speech_to_text_to_hf.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/kyutai_speech_to_text/convert_kyutai_speech_to_text_to_hf.py)
 - [src/transformers/models/kyutai_speech_to_text/feature_extraction_kyutai_speech_to_text.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/kyutai_speech_to_text/feature_extraction_kyutai_speech_to_text.py)
 - [src/transformers/models/kyutai_speech_to_text/modeling_kyutai_speech_to_text.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/kyutai_speech_to_text/modeling_kyutai_speech_to_text.py)
 - [src/transformers/models/kyutai_speech_to_text/modular_kyutai_speech_to_text.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/kyutai_speech_to_text/modular_kyutai_speech_to_text.py)
 - [src/transformers/models/mimi/modeling_mimi.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mimi/modeling_mimi.py)
 - [src/transformers/models/moonshine/convert_usefulsensors_to_hf.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/moonshine/convert_usefulsensors_to_hf.py)
 - [src/transformers/models/moshi/modeling_moshi.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/moshi/modeling_moshi.py)
 - [src/transformers/utils/kernel_config.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/kernel_config.py)
 - [tests/kernels/test_kernels.py](https://github.com/huggingface/transformers/blob/8f542025/tests/kernels/test_kernels.py)
 
  The Hugging Face Transformers library employs a pluggable attention system designed to decouple high-level model architectures from low-level hardware-optimized attention kernels. This system allows models to switch between standard PyTorch implementations and highly optimized backends like FlashAttention-2, SDPA, and FlexAttention without changing the model's core logic.

 
## Pluggable Attention Architecture

 The attention system is governed by the `AttentionInterface`, which provides a consistent API for various backends [docs/source/en/attention_interface.md20-21](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/attention_interface.md?plain=1#L20-L21). Models specify their supported backends using attributes like `_supports_flash_attn`, `_supports_sdpa`, and `_supports_flex_attn` [src/transformers/models/kyutai_speech_to_text/modeling_kyutai_speech_to_text.py94-96](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/kyutai_speech_to_text/modeling_kyutai_speech_to_text.py#L94-L96).

 The following diagram illustrates the relationship between the `PreTrainedModel` configuration and the underlying attention dispatchers:

 
### Attention Dispatch Logic

 
```

```

 **Sources:** [src/transformers/modeling_utils.py30](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L30-L30), [src/transformers/integrations/sdpa_attention.py79-90](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/sdpa_attention.py#L79-L90), [src/transformers/integrations/flash_attention.py26-39](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/flash_attention.py#L26-L39), [docs/source/en/attention_interface.md132-140](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/attention_interface.md?plain=1#L132-L140), [src/transformers/models/mimi/modeling_mimi.py30](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mimi/modeling_mimi.py#L30-L30).

 
## Optimized Backends

 Transformers integrates several specialized backends to optimize memory usage and throughput:

 
| Backend | Implementation Source | Description |
|---|---|---|
| SDPA | sdpa_attention.py | PyTorch's native Scaled Dot Product Attention. Supports GQA and various device-specific optimizations for CUDA, NPU, and XPU src/transformers/integrations/sdpa_attention.py79-102. |
| FlashAttention | flash_attention.py | Integration for FlashAttention-2, 3, and 4. Handles non-transposed inputs, padding for specific head dimensions (e.g., MLA), and device-specific fallbacks src/transformers/integrations/flash_attention.py26-64. |
| FlexAttention | flex_attention.py | A framework for custom sparse, block-local, or sliding-window attention patterns docs/source/en/attention_interface.md26. |
| NPU Flash | npu_flash_attention.py | Specialized kernels for Ascend NPU hardware using npu_flash_attn_func variants src/transformers/modeling_flash_attention_utils.py169-172. |

 For a deep dive into implementation selection, paged attention variants (e.g., `paged|flash_attention_2`), and the registry system, see **[Flash Attention, SDPA & FlexAttention](https://deepwiki.com/huggingface/transformers/9.1-flash-attention-sdpa-and-flexattention)**.

 
## Hub-Loaded Custom Kernels

 The library supports loading compiled CUDA or Triton kernels directly from the Hugging Face Hub at runtime via the `kernels` library. This mechanism avoids local compilation issues and allows for rapid deployment of optimized operators like `RMSNorm`, `Rotary Embedding`, or `Mamba` scans [src/transformers/integrations/hub_kernels.py67-77](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/hub_kernels.py#L67-L77).

 
### Kernel Integration Mechanism

 
```

```

 **Sources:** [src/transformers/integrations/hub_kernels.py105-112](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/hub_kernels.py#L105-L112), [src/transformers/utils/kernel_config.py99-105](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/kernel_config.py#L99-L105), [src/transformers/models/diffllama/modeling_diffllama.py132-133](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/diffllama/modeling_diffllama.py#L132-L133), [src/transformers/integrations/hub_kernels.py143-174](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/hub_kernels.py#L143-L174).

 
### Key Components:

 
 - **`KernelConfig`**: A configuration class used to manage and update the mapping of model layers to Hub repositories [src/transformers/utils/kernel_config.py99-111](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/kernel_config.py#L99-L111).
 - **Monkey Patching**: The system uses `register_patch_mapping` to swap standard PyTorch forward passes with kernelized versions when `use_kernels=True` is passed to `from_pretrained` [src/transformers/integrations/hub_kernels.py27](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/hub_kernels.py#L27-L27), [tests/kernels/test_kernels.py66-68](https://github.com/huggingface/transformers/blob/8f542025/tests/kernels/test_kernels.py#L66-L68).
 - **Decorators**: Functions like `apply_rotary_pos_emb` are decorated with `@use_kernel_forward_from_hub("rotary_pos_emb")` to enable seamless Hub-based acceleration [src/transformers/models/diffllama/modeling_diffllama.py132-133](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/diffllama/modeling_diffllama.py#L132-L133).
 - **Fallback Logic**: The `FLASH_ATTN_KERNEL_FALLBACK` mapping provides community-maintained kernels when local packages are missing [src/transformers/modeling_flash_attention_utils.py65-71](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_flash_attention_utils.py#L65-L71).
 
 For details on the Hub kernel registry, custom configuration, and the `@use_kernelized_func` decorator, see **[Hub Kernels & Custom Kernel Loading](https://deepwiki.com/huggingface/transformers/9.2-hub-kernels-and-custom-kernel-loading)**.

 **Sources:**

 
 - `src/transformers/integrations/hub_kernels.py`
 - `src/transformers/modeling_flash_attention_utils.py`
 - `src/transformers/integrations/sdpa_attention.py`
 - `src/transformers/integrations/flash_attention.py`
 - `src/transformers/utils/kernel_config.py`
 - `docs/source/en/attention_interface.md`
 - `src/transformers/models/kyutai_speech_to_text/modeling_kyutai_speech_to_text.py`
 - `src/transformers/models/diffllama/modeling_diffllama.py`
 - `src/transformers/models/mimi/modeling_mimi.py`
 - `tests/kernels/test_kernels.py`
