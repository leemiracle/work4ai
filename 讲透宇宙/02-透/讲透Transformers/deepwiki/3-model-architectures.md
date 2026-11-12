> 来源: [https://deepwiki.com/huggingface/transformers/3-model-architectures](https://deepwiki.com/huggingface/transformers/3-model-architectures)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Model Architectures

  Relevant source files 
 - [docs/source/en/model_doc/falcon_mamba.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/model_doc/falcon_mamba.md?plain=1)
 - [docs/source/en/model_doc/zamba.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/model_doc/zamba.md?plain=1)
 - [src/transformers/models/bamba/modeling_bamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/bamba/modeling_bamba.py)
 - [src/transformers/models/bamba/modular_bamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/bamba/modular_bamba.py)
 - [src/transformers/models/cohere/modeling_cohere.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/cohere/modeling_cohere.py)
 - [src/transformers/models/cohere2/configuration_cohere2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/cohere2/configuration_cohere2.py)
 - [src/transformers/models/cohere2/modeling_cohere2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/cohere2/modeling_cohere2.py)
 - [src/transformers/models/cohere2/modular_cohere2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/cohere2/modular_cohere2.py)
 - [src/transformers/models/dbrx/modeling_dbrx.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/dbrx/modeling_dbrx.py)
 - [src/transformers/models/falcon_h1/modeling_falcon_h1.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/falcon_h1/modeling_falcon_h1.py)
 - [src/transformers/models/falcon_h1/modular_falcon_h1.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/falcon_h1/modular_falcon_h1.py)
 - [src/transformers/models/falcon_mamba/configuration_falcon_mamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/falcon_mamba/configuration_falcon_mamba.py)
 - [src/transformers/models/falcon_mamba/modeling_falcon_mamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/falcon_mamba/modeling_falcon_mamba.py)
 - [src/transformers/models/falcon_mamba/modular_falcon_mamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/falcon_mamba/modular_falcon_mamba.py)
 - [src/transformers/models/gemma/modeling_gemma.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma/modeling_gemma.py)
 - [src/transformers/models/gemma/modular_gemma.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma/modular_gemma.py)
 - [src/transformers/models/gemma2/modeling_gemma2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma2/modeling_gemma2.py)
 - [src/transformers/models/gemma2/modular_gemma2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma2/modular_gemma2.py)
 - [src/transformers/models/gemma3/configuration_gemma3.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/configuration_gemma3.py)
 - [src/transformers/models/gemma3/modeling_gemma3.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py)
 - [src/transformers/models/gemma3/modular_gemma3.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modular_gemma3.py)
 - [src/transformers/models/gemma3n/configuration_gemma3n.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3n/configuration_gemma3n.py)
 - [src/transformers/models/gemma3n/modeling_gemma3n.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3n/modeling_gemma3n.py)
 - [src/transformers/models/gemma3n/modular_gemma3n.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3n/modular_gemma3n.py)
 - [src/transformers/models/granitemoe/modeling_granitemoe.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/granitemoe/modeling_granitemoe.py)
 - [src/transformers/models/granitemoehybrid/modeling_granitemoehybrid.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/granitemoehybrid/modeling_granitemoehybrid.py)
 - [src/transformers/models/granitemoeshared/modeling_granitemoeshared.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/granitemoeshared/modeling_granitemoeshared.py)
 - [src/transformers/models/helium/configuration_helium.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/helium/configuration_helium.py)
 - [src/transformers/models/jamba/configuration_jamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/jamba/configuration_jamba.py)
 - [src/transformers/models/jamba/modeling_jamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/jamba/modeling_jamba.py)
 - [src/transformers/models/jetmoe/modeling_jetmoe.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/jetmoe/modeling_jetmoe.py)
 - [src/transformers/models/llama/modeling_llama.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/llama/modeling_llama.py)
 - [src/transformers/models/mamba/modeling_mamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mamba/modeling_mamba.py)
 - [src/transformers/models/mamba2/configuration_mamba2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mamba2/configuration_mamba2.py)
 - [src/transformers/models/mamba2/modeling_mamba2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mamba2/modeling_mamba2.py)
 - [src/transformers/models/mistral/modeling_mistral.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mistral/modeling_mistral.py)
 - [src/transformers/models/mixtral/modeling_mixtral.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mixtral/modeling_mixtral.py)
 - [src/transformers/models/olmo/modeling_olmo.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/olmo/modeling_olmo.py)
 - [src/transformers/models/olmoe/modeling_olmoe.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/olmoe/modeling_olmoe.py)
 - [src/transformers/models/persimmon/modeling_persimmon.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/persimmon/modeling_persimmon.py)
 - [src/transformers/models/phi/modeling_phi.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/phi/modeling_phi.py)
 - [src/transformers/models/phi3/modeling_phi3.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/phi3/modeling_phi3.py)
 - [src/transformers/models/phimoe/modeling_phimoe.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/phimoe/modeling_phimoe.py)
 - [src/transformers/models/qwen2/modeling_qwen2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/qwen2/modeling_qwen2.py)
 - [src/transformers/models/qwen2_moe/modeling_qwen2_moe.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/qwen2_moe/modeling_qwen2_moe.py)
 - [src/transformers/models/stablelm/modeling_stablelm.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/stablelm/modeling_stablelm.py)
 - [src/transformers/models/starcoder2/modeling_starcoder2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/starcoder2/modeling_starcoder2.py)
 - [src/transformers/models/t5gemma2/configuration_t5gemma2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/t5gemma2/configuration_t5gemma2.py)
 - [src/transformers/models/t5gemma2/modeling_t5gemma2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/t5gemma2/modeling_t5gemma2.py)
 - [src/transformers/models/t5gemma2/modular_t5gemma2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/t5gemma2/modular_t5gemma2.py)
 - [src/transformers/models/zamba/configuration_zamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/zamba/configuration_zamba.py)
 - [src/transformers/models/zamba/modeling_zamba.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/zamba/modeling_zamba.py)
 - [src/transformers/models/zamba2/modeling_zamba2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/zamba2/modeling_zamba2.py)
 - [src/transformers/models/zamba2/modular_zamba2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/zamba2/modular_zamba2.py)
 - [tests/models/bamba/test_modeling_bamba.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/bamba/test_modeling_bamba.py)
 - [tests/models/deepseek_v3/test_modeling_deepseek_v3.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/deepseek_v3/test_modeling_deepseek_v3.py)
 - [tests/models/falcon_h1/test_modeling_falcon_h1.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/falcon_h1/test_modeling_falcon_h1.py)
 - [tests/models/falcon_mamba/test_modeling_falcon_mamba.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/falcon_mamba/test_modeling_falcon_mamba.py)
 - [tests/models/gemma3/test_modeling_gemma3.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/gemma3/test_modeling_gemma3.py)
 - [tests/models/gemma3n/test_modeling_gemma3n.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/gemma3n/test_modeling_gemma3n.py)
 - [tests/models/jamba/test_modeling_jamba.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/jamba/test_modeling_jamba.py)
 - [tests/models/mamba/test_modeling_mamba.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/mamba/test_modeling_mamba.py)
 - [tests/models/mamba2/test_modeling_mamba2.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/mamba2/test_modeling_mamba2.py)
 - [tests/models/t5gemma2/test_modeling_t5gemma2.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/t5gemma2/test_modeling_t5gemma2.py)
 - [tests/models/zamba/test_modeling_zamba.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/zamba/test_modeling_zamba.py)
 - [tests/models/zamba2/test_modeling_zamba2.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/zamba2/test_modeling_zamba2.py)
 
  The `transformers` library provides a diverse ecosystem of model architectures, ranging from large-scale autoregressive language models to specialized vision and audio processors. These architectures are implemented following a "single-file-per-model" philosophy, ensuring that the code for a specific model like Llama or Mistral is self-contained and readable.

 This page provides a high-level taxonomy of the model families available in the library. For implementation details, specific hyperparameters, and usage guides, refer to the respective child pages.

 
### Architectural Taxonomy

 The codebase categorizes models based on their structural paradigms and the modalities they process. Most modern implementations inherit from `PreTrainedModel` [src/transformers/modeling_utils.py40](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L40-L40) and utilize shared utilities for attention, normalization, and rotary embeddings.

 
#### 1. Decoder-Only Language Models (LLMs)

 Modern Large Language Models (LLMs) primarily follow the decoder-only transformer architecture. These models are optimized for autoregressive generation and share common components such as:

 
 - **Normalization**: `LlamaRMSNorm` [src/transformers/models/llama/modeling_llama.py53](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/llama/modeling_llama.py#L53-L53) `GemmaRMSNorm` [src/transformers/models/gemma/modeling_gemma.py64](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma/modeling_gemma.py#L64-L64) or `Gemma3RMSNorm` [src/transformers/models/gemma3/modeling_gemma3.py136](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L136-L136)
 - **Positional Encoding**: Rotary Positional Embeddings (RoPE) via `LlamaRotaryEmbedding` [src/transformers/models/llama/modeling_llama.py73](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/llama/modeling_llama.py#L73-L73) or `Gemma3RotaryEmbedding` [src/transformers/models/gemma3/modeling_gemma3.py156](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L156-L156)
 - **Attention**: Grouped-Query Attention (GQA) and Sliding Window Attention as seen in `MistralAttention` [src/transformers/models/mistral/modeling_mistral.py122](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mistral/modeling_mistral.py#L122-L122) and `Gemma2Attention` [src/transformers/models/gemma2/modeling_gemma2.py46](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma2/modeling_gemma2.py#L46-L46)
 
 For details, see [Decoder-Only Language Models (LLMs)](https://deepwiki.com/huggingface/transformers/3.1-decoder-only-language-models-(llms)).

 
#### 2. Mixture-of-Experts (MoE) Models

 MoE models scale parameter counts efficiently by replacing dense MLP layers with sparse blocks. They utilize a routing mechanism to activate only a subset of "experts" for each token. Key entities include:

 
 - **Routers**: `MixtralTopKRouter` [src/transformers/models/mixtral/modeling_mixtral.py96](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mixtral/modeling_mixtral.py#L96-L96)
 - **Sparse Blocks**: `MixtralSparseMoeBlock` [src/transformers/models/mixtral/modeling_mixtral.py114](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mixtral/modeling_mixtral.py#L114-L114) and `Qwen2MoeMLP` [src/transformers/models/qwen2_moe/modeling_qwen2_moe.py130](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/qwen2_moe/modeling_qwen2_moe.py#L130-L130)
 - **Expert Stacking**: `MixtralExperts` [src/transformers/models/mixtral/modeling_mixtral.py57](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mixtral/modeling_mixtral.py#L57-L57) stores weights as 3D tensors for efficient dispatch.
 
 For details, see [Mixture-of-Experts (MoE) Models](https://deepwiki.com/huggingface/transformers/3.2-mixture-of-experts-(moe)-models).

 
#### 3. State Space & Hybrid Models

 These models move beyond standard self-attention, using State Space Models (SSMs) to achieve linear scaling with sequence length.

 
 - **Pure SSM**: `MambaModel` utilizes selective scan operations like `mamba_selective_scan` [src/transformers/models/mamba/modeling_mamba.py175](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mamba/modeling_mamba.py#L175-L175)
 - **Hybrid Models**: Interleave SSM layers with standard attention layers, as seen in `JambaAttention` [src/transformers/models/jamba/modeling_jamba.py151](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/jamba/modeling_jamba.py#L151-L151) being used alongside Mamba blocks.
 
 For details, see [State Space & Hybrid Models](https://deepwiki.com/huggingface/transformers/3.3-state-space-and-hybrid-models).

 
#### 4. Encoder-Decoder & Seq2Seq Models

 Classic transformer architectures used for translation and summarization. These models consist of an encoder that processes the input and a decoder that generates the output using cross-attention. This family includes T5, BART, and recent adaptations like `T5Gemma2Model` [src/transformers/models/t5gemma2/modeling_t5gemma2.py1](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/t5gemma2/modeling_t5gemma2.py#L1-L1)

 For details, see [Encoder-Decoder & Sequence-to-Sequence Models](https://deepwiki.com/huggingface/transformers/3.4-encoder-decoder-and-sequence-to-sequence-models).

 
#### 5. Vision & Vision-Language Models (VLMs)

 Vision models utilize architectures like ViT to process images as patches. VLMs extend this by fusing vision encoders with LLM decoders.

 
 - **Vision Configuration**: `SiglipVisionConfig` [src/transformers/models/gemma3/modular_gemma3.py62](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modular_gemma3.py#L62-L62)
 - **Multimodal Fusion**: `Gemma3ForConditionalGeneration` [src/transformers/models/gemma3/modeling_gemma3.py58](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L58-L58) integrates vision features into the causal decoding stream via `image_hidden_states` [src/transformers/models/gemma3/modeling_gemma3.py73](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L73-L73)
 
 For details, see [Vision & Vision-Language Models](https://deepwiki.com/huggingface/transformers/3.5-vision-and-vision-language-models).

 
#### 6. Audio & Speech Models

 Audio models process raw waveforms or spectrograms. They often use convolutional front-ends followed by transformer blocks. Modern audio-capable models incorporate audio hidden states directly into the model output.

 For details, see [Audio & Speech Models](https://deepwiki.com/huggingface/transformers/3.6-audio-and-speech-models).

 
#### 7. Multimodal Omni Models

 Omni models are designed to handle text, image, and audio natively within a unified architecture.

 
 - **Multimodal Processing**: `Gemma3Processor` handles the composition of different input types.
 - **Unified Output**: `Gemma3ModelOutputWithPast` [src/transformers/models/gemma3/modeling_gemma3.py66](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L66-L66) includes fields for `image_hidden_states` [src/transformers/models/gemma3/modeling_gemma3.py73](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L73-L73)
 
 For details, see [Multimodal Omni & Specialized Models](https://deepwiki.com/huggingface/transformers/3.7-multimodal-omni-and-specialized-models).

 
### Architecture Mapping: Natural Language to Code Entities

 The following diagrams illustrate how high-level architectural concepts are represented by specific classes and functions in the codebase.

 
#### Autoregressive Generation Flow

 This diagram maps the conceptual "Next Token Prediction" process to internal model components.

 
```

```

 Sources: [src/transformers/models/llama/modeling_llama.py26](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/llama/modeling_llama.py#L26-L26) [src/transformers/models/llama/modeling_llama.py138](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/llama/modeling_llama.py#L138-L138) [src/transformers/models/mistral/modeling_mistral.py14](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mistral/modeling_mistral.py#L14-L14)

 
#### Multimodal Architecture Integration

 This diagram shows how different modalities are unified in recent "Omni" architectures like Gemma 3.

 
```

```

 Sources: [src/transformers/models/gemma3/modeling_gemma3.py106](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L106-L106) [src/transformers/models/gemma3/modeling_gemma3.py65](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L65-L65) [src/transformers/models/gemma3/modeling_gemma3.py66](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L66-L66)

 
### Summary Table of Model Families

 
| Family | Key Base Class | Primary Modality | Distinctive Feature |
|---|---|---|---|
| LLMs | LlamaForCausalLM | Text | RoPE, GQA, RMSNorm |
| MoE | MixtralForCausalLM | Text | MixtralSparseMoeBlock |
| SSM | MambaForCausalLM | Text | mamba_selective_scan |
| Multimodal | Gemma3ForConditionalGeneration | Image/Text | image_hidden_states |
| Seq2Seq | T5Gemma2ForConditionalGeneration | Text | Cross-Attention, Encoder-Decoder |

 Sources: [src/transformers/models/llama/modeling_llama.py1-6](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/llama/modeling_llama.py#L1-L6) [src/transformers/models/mixtral/modeling_mixtral.py114](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mixtral/modeling_mixtral.py#L114-L114) [src/transformers/models/mamba/modeling_mamba.py175](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mamba/modeling_mamba.py#L175-L175) [src/transformers/models/gemma3/modeling_gemma3.py58](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma3/modeling_gemma3.py#L58-L58) [src/transformers/models/t5gemma2/modeling_t5gemma2.py1](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/t5gemma2/modeling_t5gemma2.py#L1-L1)
