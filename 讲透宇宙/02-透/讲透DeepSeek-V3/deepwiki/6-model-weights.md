<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-V3 · page 6 Model Weights · fetched 2026-10-30 -->

# Model Weights

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README_WEIGHTS.md](README_WEIGHTS.md)

</details>



This document provides detailed information about the structure, organization, and technical specifications of the DeepSeek-V3 model weights. It covers the weight file composition, parameter distribution, FP8 quantization format, and loading mechanisms. For information about weight conversion for inference, see [Weight Conversion](#4.2).

## Weight Structure Overview

The DeepSeek-V3 weight file architecture consists of two primary components: the Main Model Weights and Multi-Token Prediction (MTP) Modules. Together, these components form the complete weight structure needed for model operation.

```mermaid
flowchart TD
    subgraph "DeepSeek-V3 Weight File Structure"
        MainModel["Main Model Weights<br>671B total params"]
        MTPModules["MTP Modules<br>11.5B unique params"]
        
        MainModel --> EmbedTokens["model.embed_tokens.weight<br>Shared with MTP"]
        MainModel --> HiddenLayers["model.layers.0 to model.layers.60<br>61 transformer layers"]
        MainModel --> OutputNorm["model.norm.weight"]
        MainModel --> LMHead["lm_head.weight<br>Shared with MTP"]
        
        MTPModules --> MTPEmbedTokens["embed_tokens<br>Points to model.embed_tokens.weight"]
        MTPModules --> ENorm["enorm<br>RMSNorm for speculative decoding"]
        MTPModules --> HNorm["hnorm<br>RMSNorm for speculative decoding"]
        MTPModules --> EHProj["eh_proj<br>Dimensionality reduction projection"]
        MTPModules --> Layer61["model.layers.61.self_attn<br>model.layers.61.mlp"]
        MTPModules --> SharedHead["shared_head<br>Points to lm_head.weight"]
    end
```

Sources: [README_WEIGHTS.md:11-49]()

### Main Model Weights

The Main Model Weights constitute the core of the DeepSeek-V3 architecture, containing the fundamental components required for the model's operation.

**Parameters:**
- **Total parameters**: 671B
- **Activation parameters**: 36.7B (including 0.9B for Embedding and 0.9B for the output Head)

**Structure:**
- **Embedding Layer**: `model.embed_tokens.weight`
- **Transformer Hidden Layers**: 61 layers from `model.layers.0` to `model.layers.60`
- **Output Layer**: `model.norm.weight` and `lm_head.weight`

### Multi-Token Prediction (MTP) Modules

The MTP Modules are specialized components that enhance the model's capabilities for multi-token prediction, enabling more efficient sequence generation.

**Parameters:**
- **Unique parameters**: 11.5B (excluding shared embedding and output head)
- **Activation parameters**: 2.4B (including shared components)

**Structure:**
- **Embedding**: Shares parameters with the Main Model's embedding layer
- **Normalization layers**: `enorm` & `hnorm` (RMSNorm parameters for speculative decoding)
- **Projection layer**: `eh_proj` (Dimensionality reduction on norm results)
- **Additional Transformer Layer**: `model.layers.61.self_attn` & `model.layers.61.mlp`
- **Output Head**: Shares parameters with the Main Model's output head (`lm_head.weight`)

Sources: [README_WEIGHTS.md:15-49]()

## Parameter Distribution and Architecture

The DeepSeek-V3 model implements a Mixture of Experts (MoE) architecture that allows it to have a large total parameter count while maintaining efficiency during inference by activating only a subset of parameters.

```mermaid
graph TD
    subgraph "DeepSeek-V3 Parameter Distribution and Code Loading"
        TotalParams["Total Parameters: 671B"]
        ActiveParams["Activated Parameters: 37B per token"]
        
        TotalParams --> MainActive["Main Model Active: 36.7B"]
        TotalParams --> MTPActive["MTP Modules Active: 2.4B<br>1.8B shared parameters"]
        
        MainActive --> EmbedMain["model.embed_tokens.weight<br>0.9B parameters"]
        MainActive --> TransformerMain["model.layers.0-60<br>61 Transformer layers"]
        MainActive --> HeadMain["lm_head.weight<br>0.9B parameters"]
        
        MTPActive --> EmbedMTP["embed_tokens reference<br>0.9B shared"]
        MTPActive --> NormProj["enorm, hnorm, eh_proj<br>Norm & projection layers"]
        MTPActive --> TransformerMTP["model.layers.61<br>1 additional layer"]
        MTPActive --> HeadMTP["shared_head reference<br>0.9B shared"]
        
        subgraph "Code Integration"
            ConfigLoader["config.json<br>num_hidden_layers=61<br>num_nextn_predict_layers=1"]
            ModelLoader["model.py<br>Transformer class"]
            WeightLoader["convert.py<br>Weight conversion"]
        end
        
        ConfigLoader --> ModelLoader
        ModelLoader --> MainActive
        ModelLoader --> MTPActive
        WeightLoader --> TotalParams
    end
```

The special architecture allows DeepSeek-V3 to have:
- **Total parameters**: 671B parameters across all experts
- **Active parameters during inference**: Only 37B parameters (5.5% of total)
- **Shared components**: 1.8B parameters shared between Main Model and MTP Modules

Sources: [README_WEIGHTS.md:15-40]()

## FP8 Weight Format

DeepSeek-V3 natively supports FP8 weight format with 128×128 block scaling, providing significant storage efficiency while maintaining model performance.

```mermaid
flowchart TD
    subgraph "FP8 Weight Format and Code Pipeline"
        OriginalWeights["Original FP16/BF16 Weights<br>safetensors format"]
        Blocking["Block Division<br>128×128 blocks"]
        ScaleCalc["Scale Calculation<br>per 128×128 block"]
        Quantization["FP8 Quantization<br>torch.float8_e4m3fn"]
        ScaleStorage["Scale Storage<br>weight_scale_inv as FP32"]
        
        OriginalWeights --> Blocking
        Blocking --> ScaleCalc
        ScaleCalc --> Quantization
        ScaleCalc --> ScaleStorage
        
        subgraph "Weight File Structure"
            FP8Weights["FP8 Weight Tensor<br>quantized weights"]
            ScaleValues["weight_scale_inv Tensor<br>dequantization scales"]
            ConfigFields["quantization_config<br>in config.json"]
        end
        
        subgraph "Code Integration"
            ConvertScript["convert.py<br>Checkpoint conversion"]
            FP8CastScript["fp8_cast_bf16.py<br>FP8 ↔ BF16 conversion"]
            KernelOps["kernel.py<br>fp8_gemm operations"]
        end
        
        Quantization --> FP8Weights
        ScaleStorage --> ScaleValues
        ConvertScript --> OriginalWeights
        FP8CastScript --> Quantization
        KernelOps --> FP8Weights
    end
```

### FP8 Configuration

The quantization configuration is specified in the `quantization_config` field of the model's `config.json`:

```json
"quantization_config": {
  "activation_scheme": "dynamic",
  "fmt": "e4m3",
  "quant_method": "fp8",
  "weight_block_size": [128, 128]
}
```

Key configuration details:
- **Format type**: `fp8` and `e4m3` (corresponding to `torch.float8_e4m3fn`)
- **Weight block size**: 128×128 matrix blocks
- **Activation quantization**: Dynamic activation quantization scheme

Sources: [README_WEIGHTS.md:60-82]()

### Dequantization Process

The dequantization process converts the FP8 weights back to higher precision during inference:

| Component | Description |
|-----------|-------------|
| `weight_scale_inv` | Float32 tensor storing dequantization scales |
| Block handling | Zero-padding for non-aligned blocks before scale calculation |
| Dequantization formula | `(128×128 weight block) * weight_scale_inv` |
| Runtime optimization | Online quantization at per-token-per-128-channel granularity |

The dequantization process enables high-precision computation while benefiting from the storage efficiency of FP8 weights.

Sources: [README_WEIGHTS.md:83-93]()

## Loading Mechanism

The model loading process follows specific rules to load both the Main Model Weights and the MTP Modules:

```mermaid
flowchart LR
    subgraph "Weight Loading Process and Code Flow"
        ConfigJSON["config.json<br>num_hidden_layers=61<br>num_nextn_predict_layers=1"]
        MainLoader["Main Model Loader<br>model.py Transformer.__init__"]
        MTPLoader["MTP Module Loader<br>NextTokenPredictionHead"]
        InferenceEngine["Inference Engine<br>generate.py"]
        
        ConfigJSON -->|"num_hidden_layers=61"| MainLoader
        ConfigJSON -->|"num_nextn_predict_layers=1"| MTPLoader
        
        MainLoader -->|"model.layers.0-60"| InferenceEngine
        MTPLoader -->|"model.layers.61"| InferenceEngine
        
        subgraph "Weight File Loading"
            SafetensorsLoader["safetensors loading"]
            DistributedLoader["torch.distributed<br>rank-based sharding"]
            QuantLoader["FP8 dequantization<br>weight_scale_inv"]
        end
        
        SafetensorsLoader --> MainLoader
        DistributedLoader --> MainLoader
        QuantLoader --> MainLoader
    end
```

Loading rules:
- **Main Model Weights**: Controlled by the `num_hidden_layers` parameter in `config.json`
- **MTP Modules**: Controlled by the `num_nextn_predict_layers` parameter in `config.json`
- **Layer ID assignment**: MTP Module layer IDs are appended immediately after the Main Model hidden layers
  - Example: With `num_hidden_layers = 61` and `num_nextn_predict_layers = 1`, the MTP Module's layer ID is `61`

Sources: [README_WEIGHTS.md:52-57]()

## Additional Weight File Configuration Fields

The DeepSeek-V3 weight files include several important configuration fields in the `config.json` file:

| Field | Description |
|-------|-------------|
| `model_type` | Set to `deepseek_v3` for this release |
| `num_nextn_predict_layers` | Number of MTP Modules (1 in the open-sourced V3 weights) |
| `quantization_config` | FP8 quantization configuration parameters |

These configuration fields are essential for properly loading and utilizing the model weights within the DeepSeek-V3 architecture.

Sources: [README_WEIGHTS.md:3-7]()

---

