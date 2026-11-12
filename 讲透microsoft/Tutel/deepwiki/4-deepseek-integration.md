<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Tutel · page 4 DeepSeek Integration · fetched 2026-10-26 -->

# DeepSeek Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [tutel/custom/custom_kernel.cpp](tutel/custom/custom_kernel.cpp)

</details>



This document describes Tutel's integration with DeepSeek large language models, specifically focusing on optimization for the DeepSeek 671B model which features a Mixture-of-Experts (MoE) architecture. Tutel provides specialized infrastructure to enable efficient inference with DeepSeek models across a variety of hardware platforms, with particular emphasis on optimized execution for FP4/FP8 precision levels.

## Overview of DeepSeek Support

Tutel is the first system to support DeepSeek 671B NVFP4 inference using A100/A800/H100/MI300 GPUs. The integration includes specialized operations, optimized communication patterns, and hardware-specific implementations to maximize throughput for both inference and reasoning tasks.

```mermaid
graph TB
    subgraph "Tutel DeepSeek Integration"
        DSMOE["DeepSeek MoE Support"] --> FP4["FP4 Support"]
        DSMOE --> FP8["FP8 Support"]
        
        FP4 --> NVGPUs["NVIDIA GPUs<br>A100/A800/H100/H800"]
        FP4 --> AMDGPUs["AMD GPUs<br>MI300"]
        FP8 --> AMDGPUs
        
        DSMOE --> SpecializedOps["Specialized Operations<br>deepseek_sigmoid_top_8_static_v2<br>glu_expert_bf16xf8_block_scal"]
        DSMOE --> Kernels["Optimized Kernels<br>tutel/ops"]
    end
```

Sources: [README.md:9-23](), [tutel/custom/custom_kernel.cpp:1036-1074](), [tutel/custom/custom_kernel.cpp:1359-1420]()

## Performance Benchmarks

Tutel significantly outperforms other frameworks when running DeepSeek models, as shown in the following performance measurements:

| Model | Machine Type | TRT-LLM | SGLANG | Tutel |
|-------|--------------|---------|--------|-------|
| DeepSeek-R1-FP4 | A100/A800 x 8 | Not Supported | Not Supported | 57 Decode TPS for bsz = 1 |
| DeepSeek-R1-FP4 | H100/H800 x 8 | Not Supported | Not Supported | 81 Decode TPS for bsz = 1 |
| DeepSeek-R1-FP4 | MI300 x 8 | Not Supported | Not Supported | 107 Decode TPS for bsz = 1 |
| DeepSeek-R1 (FP8) | A100/H100 x 8 | OoM | OoM | OoM |
| DeepSeek-R1 (FP8) | MI300 x 8 | Not Supported | 42 Decode TPS for bsz = 1 | 110 Decode TPS for bsz = 1 |

Sources: [README.md:12-23]()

## DeepSeek Model Architecture

The DeepSeek 671B model uses a specialized Mixture-of-Experts architecture with optimized components implemented in Tutel.

```mermaid
flowchart TB
    subgraph "DeepSeek 671B Model"
        Input["Input Tokens"] --> Embedding["Token Embedding"]
        Embedding --> TransformerBlocks["Transformer Blocks (1...N)"]
        
        subgraph "Transformer Block"
            Input1["Input"] --> RMSNorm1["RMSNorm<br>rmsnorm_bf16"]
            RMSNorm1 --> Attention["Multi-Head Attention<br>deepseek_r1_attn_f16xf8_block_scal"]
            Attention --> Residual1["Residual Connection + AllReduce<br>x_add_allreduce_y_f16"]
            Residual1 --> RMSNorm2["RMSNorm<br>rmsnorm_bf16"]
            RMSNorm2 --> MOE["MoE Layer"]
            MOE --> Residual2["Residual Connection + AllReduce<br>x_add_allreduce_y_f16"]
        end
        
        TransformerBlocks --> FinalRMSNorm["Final RMSNorm<br>rmsnorm_bf16"]
        FinalRMSNorm --> Output["Output Logits"]
    end
    
    subgraph "MoE Components"
        MOE -.-> Gating["Expert Gating<br>deepseek_sigmoid_top_8_static_v2"]
        MOE -.-> Experts["Expert FFN<br>glu_expert_bf16xf8_block_scal"]
        MOE -.-> AllReduce["AllReduce<br>x_add_allreduce_y_f16"]
    end
```

Sources: [tutel/custom/custom_kernel.cpp:1422-1629](), [tutel/custom/custom_kernel.cpp:1053-1074](), [tutel/custom/custom_kernel.cpp:1359-1420]()

## Specialized DeepSeek Operations

Tutel implements several specialized operations to optimize DeepSeek model execution:

1. **Expert Gating**: The `deepseek_sigmoid_top_8_static_v2` function implements a specialized sigmoid-based gating mechanism that selects the top-8 experts for each token.

2. **Expert Execution**: The `glu_expert_bf16xf8_block_scal` function implements the Gated Linear Unit (GLU) activation for experts with block-wise scaling for quantized weights.

3. **Attention Mechanism**: The `deepseek_r1_attn_f16xf8_block_scal` function implements an optimized multi-head attention mechanism specific to DeepSeek R1 models.

4. **Normalized Activation**: The `rmsnorm_bf16` function implements RMSNorm (Root Mean Square Layer Normalization) optimized for bfloat16 data type.

5. **All-Reduce**: The `x_add_allreduce_y_f16` function implements an optimized residual connection with distributed all-reduce.

Sources: [tutel/custom/custom_kernel.cpp:1053-1074](), [tutel/custom/custom_kernel.cpp:1359-1420](), [tutel/custom/custom_kernel.cpp:1118-1209](), [tutel/custom/custom_kernel.cpp:1048-1052](), [tutel/custom/custom_kernel.cpp:1292-1306]()

## Model Forward Pass

The following diagram illustrates the forward pass through a DeepSeek model using Tutel's optimized operations:

```mermaid
sequenceDiagram
    participant Input as "Input Tokens"
    participant Embed as "Token Embedding"
    participant Attn as "Attention Layer"
    participant MoE as "MoE Layer"
    participant Output as "Output Logits"
    
    Input->>Embed: token_emb.index_select()
    
    loop For each transformer layer
        Embed->>Attn: warp_rmsnorm_bf16()
        Attn->>Attn: warp_deepseek_r1_attn_f16xf8_block_scal()
        Attn->>Embed: warp_x_add_allreduce_y_f16()
        
        Embed->>MoE: warp_rmsnorm_bf16()
        
        MoE->>MoE: Generate logits (matmul or gate_gemm_out_bf16)
        MoE->>MoE: warp_deepseek_sigmoid_top_8_static_v2()
        MoE->>MoE: warp_glu_expert_f16xf8_block_scal()
        
        MoE->>Embed: warp_x_add_allreduce_y_f16()
    end
    
    Embed->>Output: warp_rmsnorm_bf16()
    Output->>Output: torch::matmul(x, weight_classify.t())
```

Sources: [tutel/custom/custom_kernel.cpp:1587-1629]()

## Weight Preparation and Cache Management

Before inference, DeepSeek models require specialized weight preparation and cache initialization:

```mermaid
graph TD
    subgraph "Weight Preparation"
        PrepWeights["deepseek_r1_prepare_weights"] --> TokenEmb["Load Token Embeddings"]
        PrepWeights --> CosCache["Initialize Rotation Cache<br>cos_sin"]
        PrepWeights --> KeyCache["Initialize Key Cache<br>key_cache"]
        PrepWeights --> ValCache["Initialize Value Cache<br>val_cache"]
        PrepWeights --> ExpertWeights["Load Expert Weights<br>moe_gate_up_ws, moe_down_ws"]
        PrepWeights --> ExpertScales["Load Expert Scales<br>moe_gate_up_ss, moe_down_ss"]
        PrepWeights --> AttnWeights["Load Attention Weights<br>qkv_a_projs, q_b_projs, etc."]
    end
```

Sources: [tutel/custom/custom_kernel.cpp:1422-1497](), [tutel/custom/custom_kernel.cpp:1500-1585]()

## Hardware-Specific Optimizations

Tutel implements various hardware-specific optimizations for different GPU architectures:

### NVIDIA GPUs (A100/A800, H100/H800)

- Optimized block sizes for kernel execution
- Specialized memory management for GPU memory
- Tensor core utilization for mixed precision operations
- NCCL communication optimizations for multi-GPU setups

### AMD MI300 GPUs

- Custom HIP kernels for AMD architecture
- ROCm-specific optimizations
- Specialized memory handling for MI300's architecture

Sources: [tutel/custom/custom_kernel.cpp:46-285](), [README.md:15-17]()

## FP8/FP4 Quantization Support

Tutel provides specialized support for FP8 and FP4 quantization:

```mermaid
graph TD
    subgraph "Quantization Support"
        InputBF16["BFloat16 Input"] --> Quantize["Quantization Operations"]
        
        Quantize --> FP8["FP8 Quantization<br>deepseek_r1_attn_f16xf8_block_scal<br>glu_expert_bf16xf8_block_scal"]
        Quantize --> FP4["FP4 Quantization<br>glu_expert_f16xf4_scal"]
        
        FP8 --> MatMul["Optimized Matrix Multiplication<br>warp_gemm_nt_bf16xfp8_block_scal"]
        FP4 --> MatMul
        
        MatMul --> Dequantize["Dequantization"]
        Dequantize --> OutputBF16["BFloat16 Output"]
    end
```

Sources: [tutel/custom/custom_kernel.cpp:1011-1046](), [tutel/custom/custom_kernel.cpp:1337-1356]()

## Usage Example

To use DeepSeek models with Tutel, you would typically follow these steps:

1. Download the model:
```
huggingface-cli download nvidia/DeepSeek-R1-FP4 --local-dir ./nvidia/DeepSeek-R1-FP4
```

2. Run inference using the appropriate Docker container:
```
# For A100/A800 (80G x 8):
docker run -it --rm --ipc=host --privileged -p 8000:8000 \
    --shm-size=1g --ulimit memlock=-1 --ulimit stack=67108864 --gpus=all -v /:/host -w /host$(pwd) \
    tutelgroup/deepseek-671b:a100x8-chat-20250401 --model_path ./nvidia/DeepSeek-R1-FP4 \
    --prompt "Calculate the indefinite integral of 1/sin(x) + x"
```

Sources: [README.md:27-49]()

## Communication Patterns for MoE

The DeepSeek integration leverages Tutel's optimized communication primitives for efficient execution of the Mixture-of-Experts architecture:

```mermaid
graph LR
    subgraph "Communication Optimizations"
        Input["Input Tokens"] --> TokenRouting["Token Routing<br>deepseek_sigmoid_top_8_static_v2"]
        TokenRouting --> AllToAll["All-to-All Communication<br>nccl_all_to_all_2d_async"]
        AllToAll --> ExpertExecution["Expert Execution<br>glu_expert_bf16xf8_block_scal"]
        ExpertExecution --> AllToAllReturn["All-to-All Return"]
        AllToAllReturn --> AllReduce["All-Reduce<br>x_add_allreduce_y_f16"]
        AllReduce --> Output["Output Tensor"]
    end
```

Sources: [tutel/custom/custom_kernel.cpp:702-783](), [tutel/custom/custom_kernel.cpp:1292-1306](), [tutel/custom/custom_kernel.cpp:1053-1074](), [tutel/custom/custom_kernel.cpp:1359-1420]()

---

