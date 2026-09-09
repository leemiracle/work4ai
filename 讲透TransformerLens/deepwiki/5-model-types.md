> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/5-model-types](https://deepwiki.com/TransformerLensOrg/TransformerLens/5-model-types)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Model Types

  Relevant source files 
 - [tests/acceptance/test_hooked_encoder.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_hooked_encoder.py)
 - [tests/acceptance/test_hooked_transformer.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_hooked_transformer.py)
 - [transformer_lens/HookedEncoder.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedEncoder.py)
 - [transformer_lens/HookedTransformer.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py)
 - [transformer_lens/factories/architecture_adapter_factory.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/factories/architecture_adapter_factory.py)
 - [transformer_lens/loading_from_pretrained.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/loading_from_pretrained.py)
 - [transformer_lens/model_bridge/generalized_components/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/__init__.py)
 - [transformer_lens/model_bridge/sources/transformers.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/sources/transformers.py)
 - [transformer_lens/model_bridge/supported_architectures/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/__init__.py)
 - [transformer_lens/tools/model_registry/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/__init__.py)
 - [transformer_lens/tools/model_registry/data/supported_models.json](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/supported_models.json)
 - [transformer_lens/tools/model_registry/data/verification_history.json](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/verification_history.json)
 - [transformer_lens/tools/model_registry/generate_report.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/generate_report.py)
 - [transformer_lens/utilities/architectures.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/utilities/architectures.py)
 - [transformer_lens/utils.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/utils.py)
 
  This document provides a high-level overview of the different model architectures supported by TransformerLens. It categorizes models into three primary functional types and introduces the specialized support for multimodal and audio processing.

 
## Overview

 TransformerLens supports a vast array of transformer architectures by mapping diverse model structures into a unified internal representation. This is achieved through two main pathways: the legacy `HookedTransformer` system and the modern `TransformerBridge` (v3.0) architecture.

 The library supports over 50 model families, including decoder-only (GPT-style), encoder-only (BERT-style), and encoder-decoder (T5-style) models.

 
```

```

 Sources: [transformer_lens/HookedTransformer.py105-113](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py#L105-L113) [transformer_lens/HookedEncoder.py40-49](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedEncoder.py#L40-L49) [transformer_lens/model_bridge/bridge.py27-40](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L27-L40)

 
## Functional Model Categories

 
### Decoder-Only Models

 The most common category, including the GPT, Llama, Mistral, and Claude-style models. These are typically used for text generation and are supported by both `HookedTransformer` and the new `TransformerBridge`.

 
 - **Key Families:** GPT-2, Llama (1, 2, 3, 3.1, 3.2), Mistral, Mixtral (MoE), Qwen, Phi, Gemma.
 - **Architecture:** Causal attention masks, typically using Rotary Positional Embeddings (RoPE) or Learned Embeddings.
 
 
### Encoder-Only Models (BERT)

 These models use bidirectional attention and are primarily used for tasks like classification, NER, and Masked Language Modeling (MLM).

 
 - **Implementation:** Handled by the `HookedEncoder` class.
 - **Key Tasks:** Supports MLM and Next Sentence Prediction (NSP) heads.
 - **For details, see [Encoder Models (BERT)](https://deepwiki.com/TransformerLensOrg/TransformerLens/5.2-encoder-models-(bert)).**
 
 Sources: [transformer_lens/HookedEncoder.py1-5](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedEncoder.py#L1-L5) [transformer_lens/HookedEncoder.py88-93](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedEncoder.py#L88-L93)

 
### Encoder-Decoder Models (T5)

 Sequence-to-sequence models that consist of a distinct encoder and decoder module.

 
 - **Implementation:** Handled by the `HookedEncoderDecoder` class or the `T5ArchitectureAdapter` in the bridge system.
 - **Key Models:** T5, MT5, Bart.
 - **For details, see [Encoder-Decoder Models (T5)](https://deepwiki.com/TransformerLensOrg/TransformerLens/5.3-encoder-decoder-models-(t5)).**
 
 Sources: [transformer_lens/model_bridge/supported_architectures/t5.py11-20](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/t5.py#L11-L20) [transformer_lens/factories/architecture_adapter_factory.py152-154](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/factories/architecture_adapter_factory.py#L152-L154)

 
### Multimodal and Audio Models

 TransformerLens v3.0 introduces support for models that process more than just text, including vision-language models and audio feature extractors.

 
 - **Vision-Language:** Support for LLaVA and Gemma 3 Multimodal variants.
 - **Audio:** Support for HuBERT and Wav2Vec2 architectures.
 - **For details, see [Multimodal and Audio Models](https://deepwiki.com/TransformerLensOrg/TransformerLens/5.4-multimodal-and-audio-models).**
 
 Sources: [transformer_lens/model_bridge/supported_architectures/gemma3_multimodal.py10-20](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/gemma3_multimodal.py#L10-L20) [transformer_lens/model_bridge/supported_architectures/hubert.py10-20](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/hubert.py#L10-L20)

 
## Architecture Mapping and Discovery

 TransformerLens uses an `ArchitectureAdapterFactory` to determine how to map a specific HuggingFace architecture string to the internal component system.

 
### Mapping Table (Selection)

 
| HF Architecture String | Adapter Class | Internal Category |
|---|---|---|
| GPT2LMHeadModel | GPT2ArchitectureAdapter | Decoder-Only |
| LlamaForCausalLM | LlamaArchitectureAdapter | Decoder-Only |
| BertForMaskedLM | BertArchitectureAdapter | Encoder-Only |
| T5ForConditionalGeneration | T5ArchitectureAdapter | Encoder-Decoder |
| LlavaForConditionalGeneration | LlavaArchitectureAdapter | Multimodal |
| HubertModel | HubertArchitectureAdapter | Audio |

 Sources: [transformer_lens/factories/architecture_adapter_factory.py83-161](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/factories/architecture_adapter_factory.py#L83-L161) [transformer_lens/tools/model_registry/__init__.py47-114](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/__init__.py#L47-L114)

 
## Component-Level Diversity

 The library supports a wide variety of sub-components that vary across these model types. The `GeneralizedComponent` system in the bridge architecture allows these different types to be hooked and analyzed uniformly.

 
```

```

 Sources: [transformer_lens/model_bridge/generalized_components/__init__.py114-161](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/__init__.py#L114-L161) [transformer_lens/model_bridge/sources/transformers.py37-162](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/sources/transformers.py#L37-L162)

 
## Next Steps

 
 - To learn how to load these models from the Hugging Face Hub, see [Loading Pretrained Models](https://deepwiki.com/TransformerLensOrg/TransformerLens/5.1-loading-pretrained-models).
 - For a deep dive into the 50+ supported adapters, see [Supported Architecture Adapters](https://deepwiki.com/TransformerLensOrg/TransformerLens/4.3-supported-architecture-adapters).
 - To check the verification status and numerical parity of specific models, see the [Model Registry](https://deepwiki.com/TransformerLensOrg/TransformerLens/9.1-model-registry).
