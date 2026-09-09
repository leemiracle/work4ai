> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/9-advanced-topics](https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/9-advanced-topics)
> DeepWiki deepseek-ai/DeepSeek-OCR-2

# Advanced Topics

  Relevant source files 
 - [DeepSeek-OCR2-master/DeepSeek-OCR2-vllm/deepseek_ocr2.py](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-vllm/deepseek_ocr2.py)
 
  This page covers advanced customization and extension capabilities of DeepSeek-OCR-2. Topics include custom logits processors for generation control, weight loading and mapping mechanisms, and guidance on extending the model architecture with custom components.

 For basic inference usage, see [Quick Start Examples](https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/2.2-quick-start-examples). For understanding the underlying model architecture before customization, see [Core Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/4-core-architecture).

 
---

 
## 9.1 Custom Logits Processors

 Logits processors modify the model's output logits before token sampling, enabling control over generation behavior. DeepSeek-OCR-2 supports custom logits processors through the transformers generation interface.

 
### NoRepeatNGramLogitsProcessor

 The `NoRepeatNGramLogitsProcessor` prevents the model from generating repetitive n-gram sequences, which can occur during OCR of highly structured or tabular content.

 **Class Interface**:

 
| Parameter | Type | Description |
|---|---|---|
| ngram_size | int | Size of n-grams to track (must be ≥ 1) |
| window_size | int | Number of tokens to search backward for repetitions (must be ≥ 1) |
| whitelist_token_ids | Set[int] | Optional set of token IDs exempt from n-gram blocking |

 **Mechanism**:

 
```

```

 **Algorithm Steps**:

 
 - **Length Check**: If sequence length < `ngram_size`, no blocking occurs
 - **Prefix Extraction**: Extract last `ngram_size - 1` tokens as the current prefix
 - **Window Search**: Scan backward `window_size` tokens for n-grams matching the prefix
 - **Token Collection**: For each match, collect the token that followed the n-gram
 - **Whitelist Filtering**: Exclude any tokens in `whitelist_token_ids`
 - **Score Masking**: Set logits to `-inf` for all banned tokens
 
 **Usage Example Pattern**:

 
```

```

 **Configuration Recommendations**:

 
| Use Case | ngram_size | window_size | Rationale |
|---|---|---|---|
| Tables with repeated headers | 3-4 | 200-500 | Prevents column header repetition |
| Code OCR | 2-3 | 100-200 | Blocks repeated syntax patterns |
| Mathematical formulas | 4-5 | 50-100 | Prevents equation repetition |
| General documents | 3 | 200 | Balanced general-purpose setting |

 **Sources**: [process/ngram_norepeat.cpython-312.pyc1-21](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/process/ngram_norepeat.cpython-312.pyc#L1-L21)

 
---

 
## 9.2 Weight Loading and Mapping

 DeepSeek-OCR-2's vLLM implementation uses a custom weight loading system to map HuggingFace checkpoint weights to the vLLM model structure.

 
### Weight Mapping Architecture

 
```

```

 
### Weight Name Transformation

 The `load_weights` method in `DeepseekOCR2ForCausalLM` implements a two-stage transformation:

 **Stage 1: Prefix Handling** ([deepseek_ocr2.py562-574](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L562-L574)):

 
```

```

 **Stage 2: vLLM Mapper** ([deepseek_ocr2.py266-268](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L266-L268)):

 
```

```

 
### Complete Mapping Table

 
| HuggingFace Checkpoint Name | Intermediate Name | Final vLLM Model Name |
|---|---|---|
| model.sam_model.encoder.layers.0.weight | sam_model.encoder.layers.0.weight | sam_model.encoder.layers.0.weight |
| model.qwen2_model.layers.5.self_attn.q_proj.weight | qwen2_model.layers.5.self_attn.q_proj.weight | qwen2_model.layers.5.self_attn.q_proj.weight |
| model.projector.mlp.0.weight | projector.mlp.0.weight | projector.mlp.0.weight |
| model.view_seperator | view_seperator | view_seperator |
| embed_tokens.weight | language.embed_tokens.weight | language_model.embed_tokens.weight |
| layers.10.self_attn.q_proj.weight | language.layers.10.self_attn.q_proj.weight | language_model.layers.10.self_attn.q_proj.weight |
| norm.weight | language.norm.weight | language_model.norm.weight |
| lm_head.weight | language.lm_head.weight | language_model.lm_head.weight |

 
### Key Design Principles

 
 - **Component Isolation**: Vision components (SAM, Qwen2, projector) are identified by substring matching and kept separate from language model weights
 - **Prefix Normalization**: The `model.` prefix from HuggingFace checkpoints is stripped for vision components but language components receive a `language.` prefix
 - **Two-Pass Mapping**: First pass handles component categorization, second pass (via `WeightsMapper`) handles vLLM-specific naming conventions
 - **Automatic Loading**: `AutoWeightsLoader` automatically distributes weights to the correct submodules based on the final mapped names
 
 
### Custom Weight Loading

 To implement custom weight loading behavior:

 
```

```

 **Sources**: [deepseek_ocr2.py266-268](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L266-L268) [deepseek_ocr2.py562-583](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L562-L583)

 
---

 
## 9.3 Custom Model Extensions

 DeepSeek-OCR-2's modular architecture enables extension at multiple levels: vision encoders, projectors, and attention mechanisms.

 
### Extension Points Architecture

 
```

```

 
### 1. Custom Vision Encoders

 The vision encoding pipeline consists of two stages: initial feature extraction (SAM-ViT-B) and feature refinement (Qwen2 decoder-as-encoder).

 **Implementation Pattern** ([deepseek_ocr2.py291-295](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L291-L295)):

 
```

```

 **Custom Encoder Extension**:

 
```

```

 **Feature Dimension Constraints**:

 
| Component | Input Dimension | Output Dimension | Constraint |
|---|---|---|---|
| SAM Model | [B, 3, H, W] | [B, 1024, h, w] | Must match Qwen2 input |
| Qwen2 Model | [B, 1024, ...] | [B, N, 896] | Must match projector input |
| Projector | [B, N, 896] | [B, N, n_embed] | n_embed must match LM dimension |

 
### 2. Custom Projector Architectures

 The `MlpProjector` class supports 8 architecture variants ([deepseek_ocr2.py295](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L295-L295)), but custom projectors can be implemented:

 
```

```

 
### 3. Custom Attention Mechanisms

 Attention mechanisms can be customized in both SAM and Qwen2 components:

 **Flash Attention Replacement Pattern**:

 
```

```

 
### 4. Custom Special Tokens

 The `view_seperator` token ([deepseek_ocr2.py311](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L311-L311)) separates global and local image features. Additional custom tokens can be added:

 
```

```

 
### Extension Checklist

 When implementing custom extensions, ensure:

 
 - **Dimension Compatibility**: Output dimensions match downstream component expectations
 - **Device Placement**: Custom modules are moved to correct device/dtype (see [deepseek_ocr2.py337](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L337-L337))
 - **Weight Loading**: Update `load_weights` method to handle custom component weights
 - **vLLM Registration**: Register custom model with `@MULTIMODAL_REGISTRY.register_processor` if modifying multimodal processing
 - **Gradient Handling**: Wrap vision components with `torch.no_grad()` if training is disabled ([deepseek_ocr2.py387-389](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L387-L389))
 - **Memory Optimization**: Consider tensor cleanup (e.g., `del patches`) for large batch processing
 
 
### Performance Considerations

 
| Extension Type | Memory Impact | Compute Impact | Recommended Testing |
|---|---|---|---|
| Custom Vision Encoder | High (cached features) | High (per-image) | Profile with various image sizes |
| Custom Projector | Low | Low | Verify dimension alignment |
| Custom Attention | Medium | High (sequence length²) | Benchmark on long sequences |
| Custom Tokens | Minimal | Minimal | Verify embedding quality |

 **Sources**: [deepseek_ocr2.py264-583](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/deepseek_ocr2.py#L264-L583) [config.py48](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/config.py#L48-L48)
