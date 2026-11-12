<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/smoothquant · page 5 Model Support · fetched 2026-10-30 -->

# Model Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/SmoothQuant.pdf](assets/SmoothQuant.pdf)
- [smoothquant/fake_quant.py](smoothquant/fake_quant.py)
- [smoothquant/smooth.py](smoothquant/smooth.py)

</details>



This page documents the model architectures and families supported by SmoothQuant's quantization techniques. It covers which Large Language Models (LLMs) are compatible with SmoothQuant's W8A8 (8-bit weight, 8-bit activation) quantization algorithm, how they are implemented, and the technical details for each model family.

## Supported Model Architectures

SmoothQuant currently supports several major LLM architecture families, each with model-specific implementation details to account for architectural differences.

```mermaid
graph TD
    SQ["SmoothQuant Core Algorithm"]
    
    SQ --> OPT["OPT Models"]
    SQ --> BLOOM["BLOOM Models"]
    SQ --> LLAMA["Llama Models\n(1/2/3)"]
    SQ --> MISTRAL["Mistral Models"]
    SQ --> MIXTRAL["Mixtral Models\n(Mixture of Experts)"]
    SQ --> FALCON["Falcon Models"]
    
    OPT --> OPT_IMPL["- OPTDecoderLayer\n- Int8OPTForCausalLM"]
    BLOOM --> BLOOM_IMPL["- BloomBlock"]
    LLAMA --> LLAMA_IMPL["- LlamaDecoderLayer\n- smooth_ln_fcs_llama_like"]
    MISTRAL --> MISTRAL_IMPL["- MistralDecoderLayer\n- smooth_ln_fcs_llama_like"]
    MIXTRAL --> MIXTRAL_IMPL["- MixtralDecoderLayer\n- MixtralSparseMoeBlock\n- smooth_ln_fcs_llama_like"]
    FALCON --> FALCON_IMPL["- FalconDecoderLayer\n- FalconAttention\n- FalconMLP"]
    
    class SQ,OPT,BLOOM,LLAMA,MISTRAL,MIXTRAL,FALCON,OPT_IMPL,BLOOM_IMPL,LLAMA_IMPL,MISTRAL_IMPL,MIXTRAL_IMPL,FALCON_IMPL main;
```

Sources: [smoothquant/smooth.py:1-161](), [smoothquant/fake_quant.py:141-351](), [README.md:87-109]()

## Model Implementation Details

### OPT (Open Pre-trained Transformer)

OPT models have the most complete implementation in SmoothQuant, including real INT8 inference support:

- **Smoothing**: Implemented for `OPTDecoderLayer` by applying smoothing to both attention and feedforward components
- **Quantization**: Supports both fake quantization (for simulation) and real INT8 inference
- **Real INT8 Support**: Available through the `Int8OPTForCausalLM` class which uses optimized INT8 GEMM kernels via [torch-int](https://github.com/Guangxuan-Xiao/torch-int)
- **Tested Sizes**: 125M, 1.3B, 2.7B, 6.7B, 13B, 30B, 66B, 175B

```mermaid
graph TD
    subgraph "OPT INT8 Implementation"
        OPT_FP16["OPTForCausalLM\n(FP16 Model)"] -- "smooth_lm()" --> OPT_SMOOTH["Smoothed OPT Model"]
        
        OPT_SMOOTH -- "Fake Quantization" --> OPT_SIM["Simulated INT8 OPT\n(quantize_opt())"]
        OPT_SMOOTH -- "Real Quantization" --> OPT_INT8["Int8OPTForCausalLM\n(Real INT8 inference)"]
        
        OPT_INT8 --> ATTENTION["INT8 Attention\n- q_proj\n- k_proj\n- v_proj\n- out_proj"]
        OPT_INT8 --> FFN["INT8 FFN\n- fc1\n- fc2"]
    end
```

Sources: [smoothquant/opt.py](), [smoothquant/smooth.py:75-90](), [smoothquant/fake_quant.py:141-180](), [README.md:41-54]()

### BLOOM Models

BLOOM models are supported through:

- **Smoothing**: Implemented for `BloomBlock` modules
- **Quantization**: Supported via fake quantization for simulation
- **Components**: Handles `input_layernorm`, `self_attention.query_key_value`, `post_attention_layernorm`, and `mlp.dense_h_to_4h`

Sources: [smoothquant/smooth.py:91-100]()

### Llama and Mistral Models

Llama (1/2/3) and Mistral models share architectural similarities and are handled similarly:

- **Smoothing**: Uses a specialized `smooth_ln_fcs_llama_like` function that handles RMSNorm instead of LayerNorm
- **Components**: 
  - Attention: `q_proj`, `k_proj`, `v_proj`, `o_proj`
  - MLP: `gate_proj`, `up_proj`, `down_proj`
- **Quantization**: Implemented in `quantize_llama_like` function
- **Tested Versions**: 
  - Llama-2: 7B, 13B, 70B
  - Llama-3: 8B, 70B
  - Mistral: 7B

```mermaid
graph TD
    subgraph "Llama/Mistral Implementation"
        LM_FP16["LlamaForCausalLM/\nMistralForCausalLM\n(FP16 Model)"] -- "smooth_lm()" --> LM_SMOOTH["Smoothed Model"]
        
        LM_SMOOTH -- "quantize_llama_like()" --> LM_QUANT["Quantized W8A8 Model"]
        
        LM_QUANT --> LM_ATTN["INT8 Attention Components\n- q_proj\n- k_proj\n- v_proj\n- o_proj"]
        LM_QUANT --> LM_MLP["INT8 MLP Components\n- gate_proj\n- up_proj\n- down_proj"]
    end
```

Sources: [smoothquant/smooth.py:48-71](), [smoothquant/smooth.py:126-141](), [smoothquant/fake_quant.py:183-230](), [README.md:87-103]()

### Mixtral Models (Mixture of Experts)

Mixtral models extend the Llama-like architecture with Mixture of Experts (MoE):

- **Smoothing**: Uses `smooth_ln_fcs_llama_like` but with special handling for the MoE components
- **Components**:
  - Regular attention components (`q_proj`, `k_proj`, `v_proj`)
  - MoE-specific: `block_sparse_moe.gate` and expert weights (`w1`, `w2`, `w3`)
- **Quantization**: Implemented in `quantize_mixtral` function
- **Tested Versions**: Mixtral-8x7B

Sources: [smoothquant/smooth.py:142-160](), [smoothquant/fake_quant.py:233-280](), [README.md:104-106]()

### Falcon Models

Falcon models have a unique architecture handled specifically:

- **Smoothing**: Special handling for different Falcon architecture variations (new decoder architecture, parallel attention)
- **Components**:
  - Attention: `self_attention.query_key_value`, `dense`
  - MLP: `dense_h_to_4h`, `dense_4h_to_h`
- **Quantization**: Implemented in `quantize_falcon` function
- **Tested Versions**: Falcon-7B, Falcon-40B

Sources: [smoothquant/smooth.py:101-125](), [smoothquant/fake_quant.py:283-310](), [README.md:107-109]()

## Quantization Implementation Architecture

SmoothQuant provides a unified interface for quantizing all supported models through the `quantize_model` function, which automatically selects the appropriate model-specific implementation.

```mermaid
graph TD
    subgraph "Quantization Implementation Flow"
        MODEL["Input Model"] --> MODEL_CHECK["Model Type Check"]
        
        MODEL_CHECK -- "OPTPreTrainedModel" --> OPT_QUANT["quantize_opt()"]
        MODEL_CHECK -- "LlamaPreTrainedModel/\nMistralPreTrainedModel" --> LLAMA_QUANT["quantize_llama_like()"]
        MODEL_CHECK -- "MixtralPreTrainedModel" --> MIXTRAL_QUANT["quantize_mixtral()"]
        MODEL_CHECK -- "FalconPreTrainedModel" --> FALCON_QUANT["quantize_falcon()"]
        
        OPT_QUANT --> W8A8["W8A8Linear.from_float()"]
        LLAMA_QUANT --> W8A8
        MIXTRAL_QUANT --> W8A8
        FALCON_QUANT --> W8A8
        
        W8A8 --> QUANT_WEIGHT["Weight Quantization\n- per_channel\n- per_tensor"]
        W8A8 --> QUANT_ACT["Activation Quantization\n- per_token\n- per_tensor"]
    end
```

Sources: [smoothquant/fake_quant.py:313-351](), [smoothquant/fake_quant.py:48-139]()

## Model Size Support and Performance

SmoothQuant has been tested and shows strong results across multiple model sizes:

| Model Type | Tested Model Sizes | Performance |
|------------|-------------------|-------------|
| OPT        | 125M to 175B      | Negligible loss (Real INT8 support) |
| Llama-2    | 7B, 13B, 70B      | PPL difference < 0.05 |
| Llama-3    | 8B, 70B           | PPL difference < 0.13 |
| Mistral    | 7B                | PPL difference < 0.03 |
| Mixtral    | 8x7B              | PPL difference < 0.06 |
| Falcon     | 7B, 40B           | PPL difference < 0.04 |

The quantization is particularly effective on larger models where memory constraints are most severe, enabling inference with significantly reduced memory requirements. For example, OPT-175B and BLOOM-176B can be quantized with negligible accuracy loss while achieving up to 2x memory reduction.

Sources: [README.md:87-110](), [README.md:119-121]()

## Model Integration Architecture

The following diagram illustrates how the model support components integrate with the rest of the SmoothQuant system:

```mermaid
graph TD
    subgraph "Model Support Integration"
        CALIB["calibration.py\nActivation Statistics"] --> SCALES["Activation Scales\n(.pt files)"]
        MODEL["Original FP16 Model"] --> SMOOTH["smooth.py\nsmooth_lm()"]
        SCALES --> SMOOTH
        
        SMOOTH -- "Model Type" --> BRANCHES["Model-Specific Implementations"]
        
        BRANCHES -- "OPT" --> OPT_IMPL["OPTDecoderLayer Implementation"]
        BRANCHES -- "BLOOM" --> BLOOM_IMPL["BloomBlock Implementation"]
        BRANCHES -- "Llama/Mistral" --> LLAMA_IMPL["LlamaDecoderLayer/\nMistralDecoderLayer Implementation"]
        BRANCHES -- "Mixtral" --> MIX_IMPL["MixtralDecoderLayer Implementation"]
        BRANCHES -- "Falcon" --> FALCON_IMPL["FalconDecoderLayer Implementation"]
        
        OPT_IMPL --> SMOOTHED["Smoothed Model"]
        BLOOM_IMPL --> SMOOTHED
        LLAMA_IMPL --> SMOOTHED
        MIX_IMPL --> SMOOTHED
        FALCON_IMPL --> SMOOTHED
        
        SMOOTHED --> QUANT["fake_quant.py\nquantize_model()"]
        
        QUANT -- "OPT" --> OPT_FQ["quantize_opt()"]
        QUANT -- "Llama/Mistral" --> LLAMA_FQ["quantize_llama_like()"]
        QUANT -- "Mixtral" --> MIX_FQ["quantize_mixtral()"]
        QUANT -- "Falcon" --> FALCON_FQ["quantize_falcon()"]
        
        OPT_FQ --> INT8["Quantized INT8 Model"]
        LLAMA_FQ --> INT8
        MIX_FQ --> INT8
        FALCON_FQ --> INT8
    end
```

Sources: [smoothquant/smooth.py:18-161](), [smoothquant/fake_quant.py:313-351]()

## Adding Support for New Models

When adding support for a new model architecture to SmoothQuant, developers need to:

1. **Implement smoothing support** in `smooth_lm` function in `smoothquant/smooth.py`
2. **Implement quantization support** by creating a new quantization function (like `quantize_opt` or `quantize_llama_like`)
3. **Update the model identification logic** in `quantize_model` function to recognize and route the new model type

The general pattern is to identify key components (attention, MLP/FFN) and apply the appropriate smoothing and quantization transformations for each.

Sources: [smoothquant/smooth.py:75-161](), [smoothquant/fake_quant.py:313-351]()

---

