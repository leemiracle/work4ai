> 来源: [https://deepwiki.com/huggingface/transformers/11-peft-and-parameter-efficient-fine-tuning](https://deepwiki.com/huggingface/transformers/11-peft-and-parameter-efficient-fine-tuning)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# PEFT & Parameter-Efficient Fine-Tuning

  Relevant source files 
 - [docs/source/en/main_classes/peft.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/peft.md?plain=1)
 - [docs/source/en/peft.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/peft.md?plain=1)
 - [src/transformers/dynamic_module_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/dynamic_module_utils.py)
 - [src/transformers/integrations/peft.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py)
 - [src/transformers/modelcard.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modelcard.py)
 - [src/transformers/models/auto/auto_factory.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/auto_factory.py)
 - [tests/models/auto/test_configuration_auto.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/auto/test_configuration_auto.py)
 - [tests/models/auto/test_feature_extraction_auto.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/auto/test_feature_extraction_auto.py)
 - [tests/models/auto/test_image_processing_auto.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/auto/test_image_processing_auto.py)
 - [tests/models/auto/test_modeling_auto.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/auto/test_modeling_auto.py)
 - [tests/models/auto/test_tokenization_auto.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/auto/test_tokenization_auto.py)
 - [tests/models/auto/test_video_processing_auto.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/auto/test_video_processing_auto.py)
 - [tests/peft_integration/test_peft_integration.py](https://github.com/huggingface/transformers/blob/8f542025/tests/peft_integration/test_peft_integration.py)
 - [tests/utils/test_dynamic_module_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_dynamic_module_utils.py)
 
  The Hugging Face Transformers library provides a native integration with the [PEFT (Parameter-Efficient Fine-Tuning)](https://github.com/huggingface/transformers/blob/8f542025/PEFT (Parameter-Efficient Fine-Tuning)) library. This integration allows users to leverage methods like LoRA, IA3, and AdaLoRA directly within the `PreTrainedModel` lifecycle. By fine-tuning only a small set of extra parameters (adapters), memory usage for gradients and optimizer states is significantly reduced [docs/source/en/peft.md12-16](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/peft.md?plain=1#L12-L16)

 
## Architecture and Mixins

 The integration is primarily implemented via the `PeftAdapterMixin` class in `src/transformers/integrations/peft.py`. This mixin is injected into all `PreTrainedModel` classes, enabling them to handle adapter loading, management, and merging without requiring a standalone `PeftModel` wrapper [src/transformers/integrations/peft.py57-74](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L57-L74)

 
### Integration Data Flow

 The following diagram illustrates how a standard Transformer model transforms into an adapter-enabled model during the `from_pretrained` lifecycle.

 **Model-Adapter Initialization Flow**

 
```

```

 Sources: [src/transformers/integrations/peft.py80-145](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L80-L145) [src/transformers/models/auto/auto_factory.py31-35](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/auto_factory.py#L31-L35)

 
## Key Functions and Classes

 
### PeftAdapterMixin

 The core interface for parameter-efficient operations. It supports:

 
 - **`load_adapter`**: Loads adapter weights from a local path or Hub ID and injects them into the model [src/transformers/integrations/peft.py80-93](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L80-L93)
 - **`add_adapter`**: Attaches a new adapter configuration (e.g., `LoraConfig`) for training [docs/source/en/peft.md26-43](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/peft.md?plain=1#L26-L43)
 - **`set_adapter`**: Switches the active adapter when multiple are loaded [docs/source/en/peft.md160-167](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/peft.md?plain=1#L160-L167)
 - **`merge_adapter`**: Merges adapter weights into the base model's weights for faster inference [src/transformers/integrations/peft.py57-74](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L57-L74)
 - **`disable_adapters`**: Method to temporarily revert the model to its base state [tests/peft_integration/test_peft_integration.py165-167](https://github.com/huggingface/transformers/blob/8f542025/tests/peft_integration/test_peft_integration.py#L165-L167)
 
 
### Integration Helpers

 The library uses specific utilities to manage the PEFT lifecycle:

 
 - **`MIN_PEFT_VERSION`**: The integration requires `peft >= 0.19.1` [src/transformers/integrations/peft.py47](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L47-L47)
 - **`find_adapter_config_file`**: Scans a directory or Hub repo to determine if it contains an adapter [src/transformers/models/auto/auto_factory.py31](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/auto_factory.py#L31-L31)
 - **`check_peft_version`**: Ensures the installed version of PEFT meets requirements [src/transformers/integrations/peft.py27](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L27-L27)
 
 Sources: [src/transformers/integrations/peft.py27-50](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L27-L50) [src/transformers/models/auto/auto_factory.py31-35](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/auto_factory.py#L31-L35)

 
## Code Entity Mapping

 The library maps high-level PEFT concepts to specific internal logic for weight dispatching and configuration handling.

 **Conceptual to Implementation Mapping**

 
```

```

 Sources: [src/transformers/integrations/peft.py57-78](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L57-L78) [src/transformers/models/auto/auto_factory.py85-140](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/auto_factory.py#L85-L140) [tests/peft_integration/test_peft_integration.py73-82](https://github.com/huggingface/transformers/blob/8f542025/tests/peft_integration/test_peft_integration.py#L73-L82)

 
## Adapter Hotswapping

 A specialized feature, **Hotswapping**, allows substituting an existing LoRA adapter with a new one in-place. This is particularly useful when using `torch.compile`, as it avoids the need for recompilation when changing adapters [src/transformers/integrations/peft.py121-145](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L121-L145)

 To use hotswapping:

 
 - Call `enable_peft_hotswap(target_rank=max_rank)` to prepare the model before compilation [src/transformers/integrations/peft.py136](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L136-L136)
 - Load the initial adapter.
 - Call `load_adapter` again with the same `adapter_name` and `hotswap=True` (or `"auto"`) to replace weights without changing module structures [src/transformers/integrations/peft.py121-127](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L121-L127)
 
 Sources: [src/transformers/integrations/peft.py121-145](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/peft.py#L121-L145)

 
## Integration Test Suite

 The library maintains a robust test suite in `tests/peft_integration/test_peft_integration.py` to ensure compatibility between Transformers and PEFT.

 
| Test Case | Description |
|---|---|
| test_peft_from_pretrained | Verifies AutoModel correctly detects and loads remote adapters tests/peft_integration/test_peft_integration.py90-109 |
| test_peft_state_dict | Ensures get_adapter_state_dict returns only the adapter-specific keys (e.g., containing "lora") tests/peft_integration/test_peft_integration.py111-124 |
| test_peft_save_pretrained | Validates that save_pretrained on an adapter-enabled model saves adapter_model.safetensors and config, but not base weights tests/peft_integration/test_peft_integration.py126-146 |
| test_peft_enable_disable_adapters | Checks that disable_adapters correctly reverts model logits to base-model behavior tests/peft_integration/test_peft_integration.py147-175 |
| _check_lora_correctly_converted | Utility to verify if BaseTunerLayer modules from PEFT are injected into the model tests/peft_integration/test_peft_integration.py69-82 |

 Sources: [tests/peft_integration/test_peft_integration.py69-175](https://github.com/huggingface/transformers/blob/8f542025/tests/peft_integration/test_peft_integration.py#L69-L175)
