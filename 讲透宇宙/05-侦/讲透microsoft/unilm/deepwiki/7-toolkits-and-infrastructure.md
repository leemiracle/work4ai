<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/unilm · page 7 Toolkits and Infrastructure · fetched 2026-10-26 -->

# Toolkits and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Diff-Transformer/README.md](Diff-Transformer/README.md)
- [Diff-Transformer/example.py](Diff-Transformer/example.py)
- [Diff-Transformer/imgs/code_highlight.png](Diff-Transformer/imgs/code_highlight.png)
- [Diff-Transformer/kernel/rotary.py](Diff-Transformer/kernel/rotary.py)
- [Diff-Transformer/multihead_attention.py](Diff-Transformer/multihead_attention.py)
- [Diff-Transformer/multihead_diffattn.py](Diff-Transformer/multihead_diffattn.py)
- [Diff-Transformer/multihead_flashdiff_1.py](Diff-Transformer/multihead_flashdiff_1.py)
- [Diff-Transformer/multihead_flashdiff_2.py](Diff-Transformer/multihead_flashdiff_2.py)
- [Diff-Transformer/rms_norm.py](Diff-Transformer/rms_norm.py)
- [retnet/README.md](retnet/README.md)
- [s2s-ft/README.md](s2s-ft/README.md)
- [s2s-ft/s2s_ft/configuration_minilm.py](s2s-ft/s2s_ft/configuration_minilm.py)
- [s2s-ft/s2s_ft/configuration_unilm.py](s2s-ft/s2s_ft/configuration_unilm.py)
- [s2s-ft/s2s_ft/modeling.py](s2s-ft/s2s_ft/modeling.py)
- [s2s-ft/s2s_ft/modeling_decoding.py](s2s-ft/s2s_ft/modeling_decoding.py)
- [s2s-ft/s2s_ft/tokenization_minilm.py](s2s-ft/s2s_ft/tokenization_minilm.py)
- [s2s-ft/s2s_ft/tokenization_unilm.py](s2s-ft/s2s_ft/tokenization_unilm.py)
- [unilm-v1/README.md](unilm-v1/README.md)

</details>



This page documents the reusable toolkits, optimized architectures, and infrastructure components that support the broader model ecosystem in the UniLM repository. These tools enable efficient fine-tuning, decoding, and deployment of pre-trained models across various tasks and modalities.

For pre-trained models themselves, see [Foundation Architectures](#1.1). For model-specific applications, see individual model pages such as [UniLM](#3.1), [MiniLM](#3.2), or [BEiT](#2.1).

## Overview

The repository provides three primary infrastructure categories:

1. **Fine-tuning Toolkits**: The s2s-ft package enables sequence-to-sequence fine-tuning of pre-trained models
2. **Efficient Architectures**: Differential Transformer and other architectural innovations for improved parameter efficiency
3. **Decoding and Deployment**: Tools for accelerated inference and production deployment

```mermaid
graph TB
    subgraph "Pre-trained Models"
        UniLM["UniLM v1/v2<br/>Unified Pre-training"]
        MiniLM["MiniLM<br/>Knowledge Distillation"]
        BEiT["BEiT Series<br/>Vision Models"]
        WavLM["WavLM<br/>Speech Processing"]
    end
    
    subgraph "Fine-tuning Infrastructure"
        S2SFT["s2s-ft Package<br/>run_seq2seq.py<br/>decode_seq2seq.py"]
        ModelLoading["Model Loading<br/>BertForSeq2SeqModel<br/>from_pretrained()"]
        Training["Training Loop<br/>label_smoothing<br/>gradient_accumulation"]
    end
    
    subgraph "Efficient Architectures"
        DiffTrans["Differential Transformer<br/>MultiheadFlashDiff1<br/>differential attention"]
        FlashAttn["FlashAttention<br/>flash_attn_func"]
        RMSNorm["RMSNorm<br/>FusedRMSNorm"]
    end
    
    subgraph "Decoding Infrastructure"
        BeamSearch["Beam Search<br/>beam_size parameter"]
        LengthPenalty["Length Penalty<br/>length_penalty"]
        AggressiveDec["Aggressive Decoding<br/>lossless speedup"]
    end
    
    UniLM --> S2SFT
    MiniLM --> S2SFT
    S2SFT --> Training
    S2SFT --> BeamSearch
    
    DiffTrans --> FlashAttn
    DiffTrans --> RMSNorm
    
    BeamSearch --> AggressiveDec
    
    style S2SFT fill:#f9f9f9
    style DiffTrans fill:#f9f9f9
    style AggressiveDec fill:#f9f9f9
```

**Sources:** [README.md:96-100](), [s2s-ft/README.md:1-2](), [Diff-Transformer/README.md:1-26]()

## s2s-ft: Sequence-to-Sequence Fine-tuning Toolkit

The `s2s-ft` package is a PyTorch-based toolkit designed to fine-tune pre-trained Transformer encoders for sequence-to-sequence language generation tasks. It supports multiple pre-trained model families including UniLM, MiniLM, BERT, and RoBERTa.

### Supported Model Types

The toolkit defines model type mappings in the configuration infrastructure:

| Model Type | Archive Map | Configuration |
|------------|-------------|---------------|
| `unilm` | UNILM_PRETRAINED_MODEL_ARCHIVE_MAP | UnilmConfig |
| `minilm` | MINILM_PRETRAINED_MODEL_ARCHIVE_MAP | MinilmConfig |
| `bert` | BERT_PRETRAINED_MODEL_ARCHIVE_MAP | BertConfig |
| `roberta` | ROBERTA_PRETRAINED_MODEL_ARCHIVE_MAP | RobertaConfig |

**Sources:** [s2s-ft/s2s_ft/modeling.py:29-63](), [s2s-ft/s2s_ft/configuration_unilm.py:36-45](), [s2s-ft/s2s_ft/configuration_minilm.py:36-38]()

### Core Components

```mermaid
graph LR
    subgraph "Data Preparation"
        RawData["Raw JSON Data<br/>src/tgt pairs"]
        Tokenizer["Tokenizer<br/>UnilmTokenizer<br/>MinilmTokenizer<br/>BertTokenizer"]
        Features["Feature Extraction<br/>max_source_seq_length<br/>max_target_seq_length"]
    end
    
    subgraph "Model Architecture"
        BertSeq2Seq["BertForSeq2SeqModel<br/>s2s_ft/modeling.py"]
        Encoder["Encoder Layers<br/>BertEncoder"]
        Decoder["Decoder Layers<br/>shared with encoder"]
        LMHead["LM Head<br/>BertLMPredictionHead"]
    end
    
    subgraph "Training"
        Loss["LabelSmoothingLoss<br/>label_smoothing parameter"]
        Optimizer["AdamW Optimizer<br/>learning_rate<br/>warmup_steps"]
        FP16["Mixed Precision<br/>fp16<br/>fp16_opt_level"]
    end
    
    subgraph "Decoding"
        BeamDec["Beam Search<br/>decode_seq2seq.py<br/>beam_size=5"]
        Constraints["Constraints<br/>forbid_duplicate_ngrams<br/>length_penalty"]
        Output["Generated Output<br/>model.split file"]
    end
    
    RawData --> Tokenizer
    Tokenizer --> Features
    Features --> BertSeq2Seq
    BertSeq2Seq --> Encoder
    Encoder --> Decoder
    Decoder --> LMHead
    
    BertSeq2Seq --> Loss
    Loss --> Optimizer
    Optimizer --> FP16
    
    BertSeq2Seq --> BeamDec
    BeamDec --> Constraints
    Constraints --> Output
```

**Sources:** [s2s-ft/s2s_ft/modeling.py:1-100](), [s2s-ft/s2s_ft/modeling_decoding.py:30-68](), [s2s-ft/README.md:40-61]()

### Input Format

The toolkit supports two dataset formats for flexibility:

**Text Format** - Each line contains a JSON object:
```json
{"src": "Messages posted on social media...", "tgt": "Threats to kill pupils..."}
```

**Tokenized Format** - Pre-tokenized with WordPiece tokens:
```json
{"src": ["messages", "posted", "on", "social", "media", ...], "tgt": ["threats", "to", "kill", ...]}
```

The code automatically detects the format by checking if the JSON values are lists or strings.

**Sources:** [s2s-ft/README.md:40-61]()

### Training Configuration

Key hyperparameters for fine-tuning:

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `model_type` | Pre-trained model family | `unilm`, `minilm`, `bert` |
| `max_source_seq_length` | Maximum source sequence length | 464, 512, 608 |
| `max_target_seq_length` | Maximum target sequence length | 48, 160 |
| `per_gpu_train_batch_size` | Batch size per GPU | 8, 16 |
| `gradient_accumulation_steps` | Gradient accumulation | 1, 2 |
| `learning_rate` | Learning rate | 7e-5, 1e-4 |
| `num_warmup_steps` | Warmup steps | 500, 1000 |
| `label_smoothing` | Label smoothing parameter | 0.1 |

The effective batch size is: `num_gpus × per_gpu_train_batch_size × gradient_accumulation_steps`

**Sources:** [s2s-ft/README.md:78-84](), [s2s-ft/README.md:126-144]()

### Model Loading and State Dictionary Conversion

The toolkit includes sophisticated model loading logic in `BertPreTrainedForSeq2SeqModel` that converts checkpoints from different model families:

```mermaid
graph TB
    Input["from_pretrained()<br/>pretrained_model_name_or_path"]
    
    subgraph "Model Type Detection"
        TypeCheck["Check model_type parameter"]
        ArchiveMap["supported_convert_pretrained_model_archive_map"]
    end
    
    subgraph "Checkpoint Loading"
        Cache["get_checkpoint_from_transformer_cache()"]
        StateDict["Load state_dict"]
        Convert["state_dict_convert[model_type]()"]
    end
    
    subgraph "Model Initialization"
        Config["BertForSeq2SeqConfig"]
        InitWeights["_init_weights()"]
        LoadState["load_state_dict()"]
    end
    
    Input --> TypeCheck
    TypeCheck --> ArchiveMap
    ArchiveMap --> Cache
    Cache --> StateDict
    StateDict --> Convert
    Convert --> Config
    Config --> InitWeights
    InitWeights --> LoadState
```

**Sources:** [s2s-ft/s2s_ft/modeling.py:78-120]()

### Label Smoothing Implementation

The toolkit implements label smoothing via `LabelSmoothingLoss` class:

```python
# Smoothing value distributed across vocabulary
smoothing_value = label_smoothing / (tgt_vocab_size - 2)
# Confidence for correct token
confidence = 1.0 - label_smoothing
# KL divergence loss between smoothed distribution and model prediction
```

**Sources:** [s2s-ft/s2s_ft/modeling_decoding.py:30-68]()

### Decoding Strategies

The `decode_seq2seq.py` script supports multiple decoding configurations:

| Parameter | Function | Example Values |
|-----------|----------|----------------|
| `beam_size` | Beam search width | 5, 8 |
| `length_penalty` | Length normalization | 0, 0.6, 0.9, 1.0 |
| `forbid_duplicate_ngrams` | Prevent n-gram repetition | flag |
| `forbid_ignore_word` | Constraints on specific tokens | "." |
| `min_len` | Minimum generation length | 1, 48 |
| `max_tgt_length` | Maximum generation length | 48, 160 |

**Sources:** [s2s-ft/README.md:102-106](), [s2s-ft/README.md:162-166]()

## Differential Transformer Architecture

The Differential Transformer introduces a novel attention mechanism that achieves parameter efficiency through differential attention, using half the number of attention heads compared to baseline Transformers while maintaining comparable performance.

### Architecture Innovation

```mermaid
graph TB
    subgraph "Standard Multi-Head Attention"
        StdQ["Q Projection<br/>embed_dim → embed_dim"]
        StdK["K Projection<br/>embed_dim → embed_dim"]
        StdV["V Projection<br/>embed_dim → embed_dim"]
        StdAttn["Attention<br/>softmax(QK^T/√d)V"]
        StdOut["Output Projection<br/>embed_dim → embed_dim"]
    end
    
    subgraph "Differential Attention"
        DiffQ["Q Projection<br/>embed_dim → embed_dim<br/>(2 × num_heads × head_dim)"]
        DiffK["K Projection<br/>embed_dim → embed_dim/n_rep<br/>(2 × num_kv_heads × head_dim)"]
        DiffV["V Projection<br/>embed_dim → embed_dim/n_rep<br/>(num_kv_heads × 2×head_dim)"]
        
        Split["Split into 2 groups<br/>q1, q2 / k1, k2"]
        
        Attn1["attn1 = flash_attn_func(q1, k1, v)"]
        Attn2["attn2 = flash_attn_func(q2, k2, v)"]
        
        Lambda["Lambda Calculation<br/>λ_full = λ_1 - λ_2 + λ_init"]
        DiffCalc["attn = attn1 - λ_full × attn2"]
        
        SubLN["RMSNorm<br/>subln layer"]
        Scale["Scale by (1 - λ_init)"]
        DiffOut["Output Projection"]
    end
    
    DiffQ --> Split
    DiffK --> Split
    DiffV --> Attn1
    DiffV --> Attn2
    
    Split --> Attn1
    Split --> Attn2
    
    Attn1 --> DiffCalc
    Attn2 --> Lambda
    Lambda --> DiffCalc
    
    DiffCalc --> SubLN
    SubLN --> Scale
    Scale --> DiffOut
```

**Sources:** [Diff-Transformer/multihead_flashdiff_1.py:30-113](), [Diff-Transformer/README.md:1-26]()

### Implementation Variants

The repository provides three implementation variants:

| Implementation | File | Purpose | FlashAttention Support |
|----------------|------|---------|------------------------|
| Naive | `multihead_diffattn.py` | Reference implementation | No |
| FlashDiff-1 | `multihead_flashdiff_1.py` | Optimized for flex_head_fa/xformers | Different qk/v dims supported |
| FlashDiff-2 | `multihead_flashdiff_2.py` | Optimized for standard flash-attention | Same qk/v dims required |

**Recommended:** Use `MultiheadFlashDiff1` for faster training and inference when using the customized FlashAttention implementation.

**Sources:** [Diff-Transformer/README.md:7-12]()

### Key Code Components

**Head Dimension Calculation:**
```python
# Differential attention uses half the heads with half the head dimension
self.head_dim = embed_dim // num_heads // 2
```

**Lambda Initialization Function:**
```python
def lambda_init_fn(depth):
    return 0.8 - 0.6 * math.exp(-0.3 * depth)
```

**Differential Attention Computation:**
```python
lambda_1 = torch.exp(torch.sum(self.lambda_q1 * self.lambda_k1, dim=-1).float()).type_as(q)
lambda_2 = torch.exp(torch.sum(self.lambda_q2 * self.lambda_k2, dim=-1).float()).type_as(q)
lambda_full = lambda_1 - lambda_2 + self.lambda_init
attn = attn1 - lambda_full * attn2
```

**Sources:** [Diff-Transformer/multihead_flashdiff_1.py:26-28](), [Diff-Transformer/multihead_flashdiff_1.py:56-111]()

### Multi-Head vs. Grouped-Query Attention

The architecture supports both MHA and GQA configurations:

```mermaid
graph LR
    subgraph "MHA Configuration"
        MHA_Diff["Differential Transformer<br/>num_heads=8<br/>num_kv_heads=None (8)"]
        MHA_Base["Baseline Transformer<br/>num_heads=16<br/>num_kv_heads=None (16)"]
    end
    
    subgraph "GQA Configuration"
        GQA_Diff["Differential Transformer<br/>num_heads=8<br/>num_kv_heads=4"]
        GQA_Base["Baseline Transformer<br/>num_heads=16<br/>num_kv_heads=8"]
    end
    
    subgraph "Parameter Count"
        Comparison["Same parameter count<br/>when comparing<br/>Diff(n heads) vs Base(2n heads)"]
    end
    
    MHA_Diff -.comparable.-> MHA_Base
    GQA_Diff -.comparable.-> GQA_Base
    
    MHA_Diff --> Comparison
    MHA_Base --> Comparison
    GQA_Diff --> Comparison
    GQA_Base --> Comparison
```

**Sources:** [Diff-Transformer/multihead_flashdiff_1.py:36-55](), [Diff-Transformer/example.py:4-19]()

### FlashAttention Integration

The implementation integrates with FlashAttention for efficiency:

```python
# Import customized flash attention supporting different qk/v dimensions
from flex_head_fa import flash_attn_func

# Or use standard flash attention
from flash_attn import flash_attn_func

# Usage in forward pass
attn1 = flash_attn_func(q1, k1, v, causal=True)
attn2 = flash_attn_func(q2, k2, v, causal=True)
```

**Rotary Position Embeddings** are applied before attention computation:
```python
q = apply_rotary_emb(q, *rel_pos, interleaved=True)
k = apply_rotary_emb(k, *rel_pos, interleaved=True)
```

**Sources:** [Diff-Transformer/multihead_flashdiff_1.py:7-8](), [Diff-Transformer/multihead_flashdiff_1.py:90-100](), [Diff-Transformer/kernel/rotary.py:1-50]()

### RMSNorm Layer

The architecture uses RMSNorm for normalization:

```python
# Attempt to use fused implementation from apex
try:
    from apex.normalization import FusedRMSNorm as RMSNorm 
except ModuleNotFoundError:
    # Fallback to custom implementation
    from rms_norm import RMSNorm

# Applied after differential attention
self.subln = RMSNorm(2 * self.head_dim, eps=1e-5, elementwise_affine=True)
attn = self.subln(attn)
```

**Sources:** [Diff-Transformer/multihead_flashdiff_1.py:8-12](), [Diff-Transformer/rms_norm.py:4-26]()

## Additional Infrastructure Components

### WavLM Speech Processing

WavLM provides pre-trained models for full-stack speech processing tasks, trained on 94k hours of audio data.

**Model Loading:**
```python
import torch
from WavLM import WavLM, WavLMConfig

checkpoint = torch.load('/path/to/wavlm.pt')
cfg = WavLMConfig(checkpoint['cfg'])
model = WavLM(cfg)
model.load_state_dict(checkpoint['model'])
```

**Feature Extraction:**
```python
# Extract last layer representation
rep = model.extract_features(wav_input_16khz)[0]

# Extract all layer representations
rep, layer_results = model.extract_features(
    wav_input_16khz, 
    output_layer=model.cfg.encoder_layers, 
    ret_layer_results=True
)[0]
layer_reps = [x.transpose(0, 1) for x, _ in layer_results]
```

**Available Models:**

| Model | Training Data | Parameters | Link |
|-------|---------------|------------|------|
| WavLM Base | 960 hrs LibriSpeech | ~95M | Azure Storage / Google Drive |
| WavLM Base+ | 94k hrs (Libri-Light + GigaSpeech + VoxPopuli) | ~95M | Azure Storage / Google Drive |
| WavLM Large | 94k hrs (Libri-Light + GigaSpeech + VoxPopuli) | ~300M | Azure Storage / Google Drive |

**Sources:** [wavlm/README.md:1-51](), [wavlm/README.md:18-23](), [wavlm/README.md:24-49]()

### DeltaLM Multilingual Translation

DeltaLM provides encoder-decoder pre-training for language generation and translation across 100+ languages.

**Model Checkpoints:**
- `deltalm-base`: 12-6 enc-dec layers, 768 hidden, 360M parameters
- `deltalm-large`: 24-12 enc-dec layers, 1024 hidden, 830M parameters

**Fine-tuning Process:**
```bash
# 1. Tokenize with Sentencepiece
spm_encode --model=spm.model --output_format=piece < train.src > train.spm.src

# 2. Binarize data
python preprocess.py --trainpref train.spm \
    --srcdict dict.txt --tgtdict dict.txt

# 3. Fine-tune
python train.py $data_bin \
    --arch deltalm_base \
    --pretrained-deltalm-checkpoint model.pt \
    --criterion label_smoothed_cross_entropy
```

**Sources:** [deltalm/README.md:1-167](), [deltalm/README.md:14-19](), [deltalm/README.md:42-126]()

### Aggressive Decoding

Aggressive Decoding provides lossless speedup for sequence-to-sequence generation:

- **Input-guided Aggressive Decoding**: 7x-9x speedup for tasks with highly similar inputs/outputs (e.g., Grammatical Error Correction)
- **Generalized Aggressive Decoding**: 3x-5x speedup for general seq2seq tasks with identical or better quality

**Sources:** [README.md:99](), [README.md:177-179]()

### LLMOps

The LLMOps repository provides general technology for enabling AI capabilities with Large Language Models and Multimodal LLMs.

**Source:** [README.md:109-110]()

## Usage Patterns

### Fine-tuning Pipeline with s2s-ft

```mermaid
graph TB
    subgraph "1. Data Preparation"
        Raw["Raw text data<br/>train/dev/test splits"]
        Format["Format as JSON<br/>src/tgt pairs"]
        Optional["Optional: Pre-tokenize<br/>with WordPiece"]
    end
    
    subgraph "2. Model Selection"
        SelectModel["Choose base model<br/>unilm/minilm/bert"]
        Download["Download checkpoint<br/>from blob storage"]
        Config["Set configuration<br/>max_seq_length, etc."]
    end
    
    subgraph "3. Training"
        Launch["Launch distributed training<br/>torch.distributed.launch"]
        Train["run_seq2seq.py<br/>--model_type unilm<br/>--fp16 --max_tokens"]
        Save["Save checkpoints<br/>--save_steps"]
    end
    
    subgraph "4. Decoding"
        Load["Load best checkpoint<br/>checkpoint_best.pt"]
        Decode["decode_seq2seq.py<br/>--beam_size 5<br/>--length_penalty"]
        Evaluate["Run evaluation<br/>ROUGE/BLEU/METEOR"]
    end
    
    Raw --> Format
    Format --> Optional
    Optional --> SelectModel
    
    SelectModel --> Download
    Download --> Config
    Config --> Launch
    Launch --> Train
    Train --> Save
    Save --> Load
    Load --> Decode
    Decode --> Evaluate
```

**Sources:** [s2s-ft/README.md:63-241]()

### Integration with Different Model Families

The toolkits support seamless integration across model families:

```mermaid
graph LR
    subgraph "Pre-trained Models"
        U1["UniLM v1<br/>unilm1-base-cased"]
        U2["UniLM v2<br/>unilm1.2-base-uncased"]
        ML["MiniLM<br/>minilm-l12-h384-uncased"]
        BR["BERT/RoBERTa<br/>bert-base-uncased"]
    end
    
    subgraph "s2s-ft Toolkit"
        ModelType["--model_type parameter"]
        StateConvert["state_dict_convert"]
        Tokenizer["Tokenizer selection"]
    end
    
    subgraph "Fine-tuned Models"
        FT_Sum["Summarization<br/>XSum, CNN/DM"]
        FT_QG["Question Generation<br/>SQuAD"]
        FT_Trans["Translation<br/>IWSLT14"]
    end
    
    U1 --> ModelType
    U2 --> ModelType
    ML --> ModelType
    BR --> ModelType
    
    ModelType --> StateConvert
    ModelType --> Tokenizer
    
    StateConvert --> FT_Sum
    StateConvert --> FT_QG
    StateConvert --> FT_Trans
```

**Sources:** [s2s-ft/s2s_ft/modeling.py:44-65](), [s2s-ft/README.md:63-301]()

### Differential Transformer Instantiation

Example usage comparing Differential Attention with standard attention:

```python
# Differential Attention with MHA (8 heads)
diff_attn_mha = MultiheadDiffAttn(
    embed_dim=1024, 
    depth=0,  # layer index
    num_heads=8, 
    num_kv_heads=None
)

# Comparable to baseline Attention with MHA (16 heads)
attn_mha = MultiheadAttention(
    embed_dim=1024, 
    depth=0, 
    num_heads=16, 
    num_kv_heads=None
)

# Both have similar parameter counts
```

**Sources:** [Diff-Transformer/example.py:1-20]()

## Environment and Dependencies

### s2s-ft Requirements

```bash
# Docker environment (recommended)
docker run -it --rm --runtime=nvidia --ipc=host \
    --privileged pytorch/pytorch:1.2-cuda10.0-cudnn7-devel bash

# Install dependencies
pip install --user methodtools py-rouge pyrouge nltk
python -c "import nltk; nltk.download('punkt')"

# Install NVIDIA Apex for mixed precision
git clone https://github.com/NVIDIA/apex.git
cd apex && git reset --hard de6378f5dae8fcf2879a4be8ecea8bbcb9e59d5
python setup.py install --cuda_ext --cpp_ext

# Install as package
cd s2s-ft && pip install --editable .
```

**Sources:** [s2s-ft/README.md:4-23]()

### Differential Transformer Requirements

- PyTorch
- FlashAttention (standard or customized `flex_head_fa`)
- Triton (for rotary embedding kernels)
- Optional: NVIDIA Apex for fused RMSNorm

**Sources:** [Diff-Transformer/multihead_flashdiff_1.py:1-12](), [Diff-Transformer/kernel/rotary.py:1-10]()

---

**Summary:** The toolkits and infrastructure in the UniLM repository provide production-ready components for fine-tuning, efficient attention mechanisms, and optimized decoding. The s2s-ft package offers comprehensive support for sequence-to-sequence tasks across multiple model families, while Differential Transformer enables parameter-efficient architectures. Together, these tools bridge pre-trained models to downstream applications with minimal friction and maximum efficiency.

---

