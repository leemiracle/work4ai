<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-V3.2-Exp · extra page Weight Conversion · fetched 2026-10-30 -->

# Weight Conversion

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [inference/convert.py](inference/convert.py)

</details>



## Purpose and Scope

The Weight Conversion system transforms HuggingFace model checkpoints into a distributed inference format optimized for multi-GPU execution. This conversion process handles parameter renaming, expert sharding for MoE models, and tensor partitioning across model parallel ranks.

For information about using the converted weights in inference, see [Text Generation](#2.3.2). For details about the model architecture that consumes these weights, see [Model Implementation](#2.3.3).

## Conversion Flow Overview

```mermaid
graph TD
    HF["HuggingFace Checkpoint<br/>*.safetensors files"] 
    Convert["convert.py<br/>main()"]
    Mapping["Parameter Mapping<br/>mapping dict"]
    Sharding["Model Parallel Sharding<br/>tensor.narrow()"]
    ExpertDist["Expert Distribution<br/>n_local_experts"]
    Output["Distributed Checkpoints<br/>model{i}-mp{mp}.safetensors"]
    Tokenizer["Tokenizer Files<br/>*token*"]
    
    HF --> Convert
    Convert --> Mapping
    Convert --> Sharding
    Convert --> ExpertDist
    Mapping --> Output
    Sharding --> Output
    ExpertDist --> Output
    HF --> Tokenizer
    Tokenizer --> Output
```

Sources: [inference/convert.py:37-90](), [inference/convert.py:54-80]()

## Parameter Mapping System

The conversion process uses a comprehensive parameter name mapping to transform HuggingFace parameter names into the format expected by the distributed inference implementation. The `mapping` dictionary defines transformations for all model components.

### Core Parameter Mappings

| HuggingFace Name | Target Name | Shard Dimension |
|------------------|-------------|-----------------|
| `embed_tokens` | `embed` | 0 |
| `q_proj` | `wq` | 0 |
| `q_a_proj` | `wq_a` | None |
| `kv_a_proj_with_mqa` | `wkv_a` | None |
| `o_proj` | `wo` | 1 |
| `gate_proj` | `w1` | 0 |
| `down_proj` | `w2` | 1 |
| `up_proj` | `w3` | 0 |
| `lm_head` | `head` | 0 |

### Parameter Name Transformations

The conversion applies systematic string replacements to standardize parameter names:

- `model.` prefix removal
- `self_attn` → `attn`
- `mlp` → `ffn`  
- `weight_scale_inv` → `scale`
- `e_score_correction_bias` → `bias`

Sources: [inference/convert.py:11-34](), [inference/convert.py:60-69]()

## Model Parallelism and Tensor Sharding

```mermaid
graph LR
    subgraph "Original Tensor"
        FullTensor["param<br/>shape: [H, W]"]
    end
    
    subgraph "Sharding Logic"
        CheckDim["dim is not None?"]
        CalcSize["shard_size = size(dim) // mp"]
        Narrow["tensor.narrow(dim, offset, size)"]
    end
    
    subgraph "Distributed Tensors"
        Rank0["model0-mp4.safetensors<br/>shard [0:shard_size]"]
        Rank1["model1-mp4.safetensors<br/>shard [shard_size:2*shard_size]"]  
        Rank2["model2-mp4.safetensors<br/>shard [2*shard_size:3*shard_size]"]
        Rank3["model3-mp4.safetensors<br/>shard [3*shard_size:4*shard_size]"]
    end
    
    FullTensor --> CheckDim
    CheckDim --> CalcSize
    CalcSize --> Narrow
    Narrow --> Rank0
    Narrow --> Rank1
    Narrow --> Rank2
    Narrow --> Rank3
```

The sharding process partitions tensors along specific dimensions based on the `mapping` dictionary. Parameters with `dim=0` are split along the first dimension (typically input features), while `dim=1` parameters are split along the second dimension (typically output features). Parameters with `dim=None` are replicated across all ranks.

Sources: [inference/convert.py:76-79](), [inference/convert.py:51-52]()

## Expert Distribution for MoE Models

```mermaid
graph TD
    subgraph "Expert Assignment"
        TotalExperts["n_experts<br/>(e.g., 256)"]
        ModelParallel["mp<br/>(e.g., 8)"]
        LocalExperts["n_local_experts<br/>= n_experts // mp<br/>(32 per rank)"]
    end
    
    subgraph "Expert Filtering"
        ExpertParam["experts.{idx}.w1.weight"]
        CheckRange["idx >= i * n_local_experts<br/>idx < (i + 1) * n_local_experts"]
        Include["Include in rank i"]
        Skip["Skip for rank i"]
    end
    
    subgraph "Rank Distribution"
        Rank0["Rank 0<br/>Experts 0-31"]
        Rank1["Rank 1<br/>Experts 32-63"]
        Rank2["Rank 2<br/>Experts 64-95"]
        RankN["Rank 7<br/>Experts 224-255"]
    end
    
    TotalExperts --> LocalExperts
    ModelParallel --> LocalExperts
    ExpertParam --> CheckRange
    CheckRange --> Include
    CheckRange --> Skip
    Include --> Rank0
    Include --> Rank1
    Include --> Rank2
    Include --> RankN
```

Expert parameters are distributed across model parallel ranks by expert index. Each rank receives a contiguous range of experts, with `n_local_experts = n_experts // mp` experts per rank. The conversion logic filters expert parameters based on whether their index falls within the target rank's assigned range.

Sources: [inference/convert.py:72-75](), [inference/convert.py:51]()

## File Operations and Output Format

### Input Processing

The conversion processes all `.safetensors` files in the source directory using the `safetensors.torch.safe_open` interface. Each parameter tensor is loaded individually to minimize memory usage during conversion.

### Output Generation

The system generates `mp` output files named `model{i}-mp{mp}.safetensors`, where `i` ranges from 0 to `mp-1`. Each file contains the parameters assigned to that model parallel rank.

### Auxiliary Files

All tokenizer-related files matching the pattern `*token*` are copied directly from the source to the destination directory without modification.

Sources: [inference/convert.py:54-55](), [inference/convert.py:84-85](), [inference/convert.py:87-89]()

## Command Line Interface

The conversion script accepts four required arguments:

- `--hf-ckpt-path`: Source directory containing HuggingFace checkpoint files
- `--save-path`: Target directory for converted checkpoint files  
- `--n-experts`: Total number of experts in the MoE model
- `--model-parallel`: Model parallelism factor for distribution

The script validates that `n_experts` is divisible by `model_parallel` to ensure even expert distribution across ranks.

Sources: [inference/convert.py:92-100]()

---

