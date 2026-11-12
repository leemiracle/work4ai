<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/unilm · page 5 Document AI: Multimodal Models · fetched 2026-10-26 -->

# Document AI: Multimodal Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [layoutlm/README.md](layoutlm/README.md)
- [layoutlmft/layoutlmft/modules/decoders/re.py](layoutlmft/layoutlmft/modules/decoders/re.py)
- [layoutlmv3/README.md](layoutlmv3/README.md)
- [layoutlmv3/examples/run_xfund.py](layoutlmv3/examples/run_xfund.py)
- [layoutlmv3/layoutlmft/data/data_collator.py](layoutlmv3/layoutlmft/data/data_collator.py)
- [layoutlmv3/layoutlmft/data/xfund.py](layoutlmv3/layoutlmft/data/xfund.py)
- [layoutlmv3/layoutlmft/models/layoutlmv3/modeling_layoutlmv3.py](layoutlmv3/layoutlmft/models/layoutlmv3/modeling_layoutlmv3.py)
- [layoutxlm/README.md](layoutxlm/README.md)
- [trocr/README.md](trocr/README.md)
- [trocr/__init__.py](trocr/__init__.py)
- [trocr/data_aug.py](trocr/data_aug.py)
- [trocr/deit.py](trocr/deit.py)
- [trocr/pic_inference.py](trocr/pic_inference.py)
- [trocr/task.py](trocr/task.py)
- [trocr/unilm3-cased.model](trocr/unilm3-cased.model)
- [trocr/unilm_models.py](trocr/unilm_models.py)

</details>



## Purpose and Scope

This section provides an overview of multimodal foundation models designed for Document AI tasks, which combine text, layout (2D position), and image information for understanding visually-rich documents such as forms, receipts, and PDFs. These models represent a key application area of "The Big Convergence" vision, bridging vision and language modalities for document-centric tasks.

**Covered in this section:**
- Common architectural patterns for multimodal document understanding
- Key model families: LayoutLM series, TrOCR
- Input modalities: text tokens, bounding box coordinates, document images
- Typical downstream tasks: form understanding, receipt extraction, document VQA

**Related sections:**
- For DiT (Document Image Transformer) pre-training, see [DiT: Document Image Transformer](#2.3)
- For specific LayoutLM variants and training details, see subsections [5.1](#5.1), [5.2](#5.2), [5.3](#5.3)
- For TrOCR architecture and OCR applications, see [TrOCR: Transformer-based OCR](#5.4)

---

## Multimodal Document Understanding Architecture

### Core Modalities

Document AI models process three complementary modalities:

| Modality | Representation | Purpose |
|----------|---------------|---------|
| **Text** | Token IDs from tokenizer | Semantic content understanding |
| **Layout** | 2D bounding boxes `[x0, y0, x1, y1]` | Spatial relationship modeling |
| **Image** | Pixel values or patch embeddings | Visual appearance features |

```mermaid
graph TB
    subgraph "Input Document"
        DocImage["Document Image<br/>(PDF/Scan)"]
        OCRText["OCR Text<br/>+ Bounding Boxes"]
    end
    
    subgraph "Multimodal Embedding Layer"
        TextEmbed["Text Embeddings<br/>token_ids → hidden_dim"]
        LayoutEmbed["Layout Embeddings<br/>[x0,y0,x1,y1] → hidden_dim"]
        VisualEmbed["Visual Embeddings<br/>PatchEmbed or ResNet"]
    end
    
    subgraph "Transformer Encoder"
        SelfAttn["Multi-Head Self-Attention<br/>Cross-modal fusion"]
        FFN["Feed-Forward Network"]
    end
    
    subgraph "Task Heads"
        SeqLabel["Token Classification<br/>LayoutLMv3ForTokenClassification"]
        DocVQA["Document VQA<br/>Question Answering"]
        DocClass["Document Classification"]
    end
    
    DocImage --> VisualEmbed
    OCRText --> TextEmbed
    OCRText --> LayoutEmbed
    
    TextEmbed --> SelfAttn
    LayoutEmbed --> SelfAttn
    VisualEmbed --> SelfAttn
    
    SelfAttn --> FFN
    FFN --> SeqLabel
    FFN --> DocVQA
    FFN --> DocClass
```

**Sources:** [README.md:74-79](), [layoutlmv3/README.md:1-5]()

---

## LayoutLM Architecture Evolution

The LayoutLM family demonstrates progressive integration of visual features:

```mermaid
graph LR
    subgraph "LayoutLM v1 (KDD 2020)"
        v1_text["Text Tokens"]
        v1_layout["2D Position"]
        v1_combine["Transformer Encoder"]
        v1_text --> v1_combine
        v1_layout --> v1_combine
    end
    
    subgraph "LayoutLM v2 (ACL 2021)"
        v2_text["Text Tokens"]
        v2_layout["2D Position"]
        v2_image["Image Features<br/>ResNet-101"]
        v2_combine["Transformer Encoder<br/>+ Visual Attention"]
        v2_text --> v2_combine
        v2_layout --> v2_combine
        v2_image --> v2_combine
    end
    
    subgraph "LayoutLM v3 (ACM MM 2022)"
        v3_text["Text Tokens"]
        v3_layout["2D Position"]
        v3_patch["Patch Embeddings<br/>PatchEmbed Conv2D"]
        v3_unified["Unified Transformer<br/>+ Word-Patch Alignment"]
        v3_text --> v3_unified
        v3_layout --> v3_unified
        v3_patch --> v3_unified
    end
    
    v1_combine -.evolves to.-> v2_combine
    v2_combine -.evolves to.-> v3_unified
```

**Key evolution milestones:**
- **v1**: Text + layout only, BERT-style pre-training
- **v2**: Added ResNet-101 visual features, separate image encoder
- **v3**: Unified text-image masking with patch embeddings (similar to BEiT), word-patch alignment objective

**Sources:** [README.md:74-79](), [layoutlm/README.md:7-18](), [layoutlmv3/README.md:1-5]()

---

## LayoutLMv3 Implementation

### Model Architecture Components

```mermaid
graph TB
    subgraph "LayoutLMv3 Model Structure"
        Config["LayoutLMv3Config<br/>layoutlmv3/configuration_layoutlmv3.py"]
        
        subgraph "Embedding Layers"
            TextEmb["text_embed<br/>word_embeddings"]
            PosEmb["position_embeddings"]
            X_Emb["x_position_embeddings"]
            Y_Emb["y_position_embeddings"]
            H_Emb["h_position_embeddings"]
            W_Emb["w_position_embeddings"]
            PatchEmb["PatchEmbed<br/>Conv2d 16x16 patches"]
        end
        
        subgraph "Transformer Layers"
            Encoder["LayoutLMv3Encoder<br/>12 or 24 layers"]
            Attention["LayoutLMv3SelfAttention<br/>Multi-head attention"]
        end
        
        subgraph "Task-Specific Heads"
            TokenClass["LayoutLMv3ForTokenClassification<br/>sequence_output → classifier"]
            QA["LayoutLMv3ForQuestionAnswering<br/>start/end span prediction"]
            SeqClass["LayoutLMv3ForSequenceClassification"]
        end
    end
    
    Config --> TextEmb
    Config --> PatchEmb
    
    TextEmb --> Encoder
    PosEmb --> Encoder
    X_Emb --> Encoder
    Y_Emb --> Encoder
    H_Emb --> Encoder
    W_Emb --> Encoder
    PatchEmb --> Encoder
    
    Encoder --> Attention
    Encoder --> TokenClass
    Encoder --> QA
    Encoder --> SeqClass
```

**Sources:** [layoutlmv3/layoutlmft/models/layoutlmv3/modeling_layoutlmv3.py:50-76](), [layoutlmv3/layoutlmft/models/layoutlmv3/modeling_layoutlmv3.py:77-157]()

### Key Implementation Details

**PatchEmbed Layer:** Converts document images into patch embeddings using convolution.

```python
# From layoutlmv3/layoutlmft/models/layoutlmv3/modeling_layoutlmv3.py:50-76
class PatchEmbed(nn.Module):
    """Image to Patch Embedding"""
    def __init__(self, img_size=224, patch_size=16, in_chans=3, embed_dim=768):
        # Conv2d with kernel_size=patch_size, stride=patch_size
        self.proj = nn.Conv2d(in_chans, embed_dim, 
                             kernel_size=patch_size, stride=patch_size)
```

**Layout Embeddings:** Bounding boxes `[x0, y0, x1, y1]` are decomposed into separate embeddings for each dimension, normalized to `[0, 1000]` range.

```python
# Normalization example from layoutlmv3/layoutlmft/data/xfund.py:22-33
def box_norm(self, box, width, height):
    x0, y0, x1, y1 = box
    x0 = int((x0 / width) * 1000)  # Normalize to 0-1000
    y0 = int((y0 / height) * 1000)
    x1 = int((x1 / width) * 1000)
    y1 = int((y1 / height) * 1000)
    return [x0, y0, x1, y1]
```

**Segment IDs:** Group tokens belonging to the same text segment (same bounding box) for better relational modeling.

```python
# From layoutlmv3/layoutlmft/data/xfund.py:35-45
def get_segment_ids(self, bboxs):
    segment_ids = []
    for i in range(len(bboxs)):
        if bboxs[i-1] == bboxs[i]:
            segment_ids.append(segment_ids[-1])  # Same segment
        else:
            segment_ids.append(segment_ids[-1] + 1)  # New segment
```

**Sources:** [layoutlmv3/layoutlmft/models/layoutlmv3/modeling_layoutlmv3.py:50-76](), [layoutlmv3/layoutlmft/data/xfund.py:22-57]()

---

## Data Processing Pipeline

### XFUND Dataset Format

The XFUND dataset (cross-lingual form understanding) represents a typical Document AI dataset structure:

```mermaid
graph TB
    subgraph "Raw XFUND Data Structure"
        JSON["XFUND JSON File<br/>{documents: [...]}"]
        Doc["Document Entry<br/>{img: {...}, document: [...]}"]
        Img["Image Metadata<br/>{fname, width, height}"]
        Annot["Annotations<br/>[{text, box, label}, ...]"]
    end
    
    subgraph "Dataset Processing"
        Loader["xfund_dataset class<br/>layoutlmft/data/xfund.py"]
        BoxNorm["box_norm()<br/>Normalize to [0,1000]"]
        Tokenize["Tokenizer.tokenize()<br/>Subword tokenization"]
        SegmentID["get_segment_ids()<br/>Group by bbox"]
    end
    
    subgraph "Model Inputs"
        InputIDs["input_ids<br/>Token IDs"]
        BBox["bbox<br/>Normalized coordinates"]
        Labels["labels<br/>NER tags"]
        PixelVals["pixel_values<br/>Image tensor"]
    end
    
    JSON --> Doc
    Doc --> Img
    Doc --> Annot
    
    Annot --> Loader
    Img --> Loader
    
    Loader --> BoxNorm
    Loader --> Tokenize
    Loader --> SegmentID
    
    BoxNorm --> BBox
    Tokenize --> InputIDs
    Annot --> Labels
    Img --> PixelVals
```

**Label Schema for Named Entity Recognition:**

| Label | ID | Description |
|-------|----|-----------| 
| `O` | 0 | Outside any entity |
| `B-HEADER` | 1 | Beginning of header |
| `I-HEADER` | 2 | Inside header |
| `B-QUESTION` | 3 | Beginning of question |
| `I-QUESTION` | 4 | Inside question |
| `B-ANSWER` | 5 | Beginning of answer |
| `I-ANSWER` | 6 | Inside answer |

**Sources:** [layoutlmv3/layoutlmft/data/xfund.py:11-19](), [layoutlmv3/layoutlmft/data/xfund.py:59-80]()

### Data Collation

The `DataCollatorForKeyValueExtraction` handles batching with proper padding:

```mermaid
graph LR
    subgraph "Batch Samples"
        S1["Sample 1<br/>length=128"]
        S2["Sample 2<br/>length=95"]
        S3["Sample 3<br/>length=203"]
    end
    
    subgraph "DataCollatorForKeyValueExtraction"
        Pad["Dynamic Padding<br/>to max_length in batch"]
        BBoxPad["bbox padding<br/>with [0,0,0,0]"]
        LabelPad["label padding<br/>with -100"]
        SegValid["pre_calc_rel_mat()<br/>segment validity mask"]
    end
    
    subgraph "Batched Tensors"
        BatchInput["input_ids<br/>[batch_size, max_len]"]
        BatchBBox["bbox<br/>[batch_size, max_len, 4]"]
        BatchLabel["labels<br/>[batch_size, max_len]"]
        ValidSpan["valid_span<br/>[batch_size, max_len, max_len]"]
    end
    
    S1 --> Pad
    S2 --> Pad
    S3 --> Pad
    
    Pad --> BBoxPad
    Pad --> LabelPad
    Pad --> SegValid
    
    BBoxPad --> BatchBBox
    LabelPad --> BatchLabel
    SegValid --> ValidSpan
    Pad --> BatchInput
```

**Sources:** [layoutlmv3/layoutlmft/data/data_collator.py:15-22](), [layoutlmv3/layoutlmft/data/data_collator.py:24-56]()

---

## Training Workflow

### Fine-tuning Script Structure

The training workflow for LayoutLMv3 on XFUND dataset:

```mermaid
graph TB
    subgraph "run_xfund.py Training Script"
        Args["HfArgumentParser<br/>ModelArguments<br/>DataTrainingArguments<br/>TrainingArguments"]
        
        Dataset["xfund_dataset<br/>Load train/val JSON"]
        
        Model["AutoModelForTokenClassification.from_pretrained<br/>microsoft/layoutlmv3-base"]
        
        Collator["DataCollatorForKeyValueExtraction<br/>Handle padding/batching"]
        
        Trainer["transformers.Trainer<br/>Training loop"]
        
        Eval["Compute metrics<br/>precision/recall/f1"]
    end
    
    Args --> Dataset
    Args --> Model
    
    Dataset --> Collator
    Model --> Trainer
    Collator --> Trainer
    
    Trainer --> Eval
```

**Key Training Arguments:**

```bash
# From layoutlmv3/README.md:97-108
python -m torch.distributed.launch \
  --nproc_per_node=8 examples/run_xfund.py \
  --model_name_or_path microsoft/layoutlmv3-base-chinese \
  --output_dir path/to/output \
  --do_train --do_eval \
  --segment_level_layout 1 \
  --visual_embed 1 \
  --input_size 224 \
  --max_steps 1000 \
  --learning_rate 7e-5 \
  --per_device_train_batch_size 2
```

**Configuration Flags:**
- `segment_level_layout=1`: Enable segment-level layout features (group tokens by bbox)
- `visual_embed=1`: Enable visual embeddings from document images
- `input_size=224`: Image resolution for PatchEmbed layer

**Sources:** [layoutlmv3/examples/run_xfund.py:1-91](), [layoutlmv3/README.md:97-108]()

---

## Pre-trained Models and Benchmarks

### Available Checkpoints

| Model | Parameters | Languages | HuggingFace Path |
|-------|-----------|-----------|------------------|
| LayoutLMv3-Base | 133M | English | `microsoft/layoutlmv3-base` |
| LayoutLMv3-Large | 368M | English | `microsoft/layoutlmv3-large` |
| LayoutLMv3-Base-Chinese | 133M | Chinese | `microsoft/layoutlmv3-base-chinese` |

**Pre-training Data:**
- IIT-CDIP: 11M scanned document images (carefully excluding overlap with downstream datasets)
- Unlabeled document images for self-supervised masked visual-language modeling

**Sources:** [layoutlmv3/README.md:21-27](), [layoutlm/README.md:31-41]()

### Benchmark Results

**FUNSD (Form Understanding in Noisy Scanned Documents):**

| Model | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| BERT-Large | 0.6113 | 0.7085 | 0.6563 |
| RoBERTa-Large | 0.6780 | 0.7391 | 0.7072 |
| LayoutLM v1 | 0.7677 | 0.8195 | 0.7927 |
| LayoutLMv3-Base | 0.8955 | 0.9165 | 0.9059 |
| LayoutLMv3-Large | 0.9219 | 0.9210 | 0.9215 |

**XFUND Chinese (Multilingual Form Understanding):**

| Model | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| LayoutLMv3-Base-Chinese | 0.8980 | 0.9435 | 0.9202 |

**Sources:** [layoutlm/README.md:98-104](), [layoutlmv3/README.md:55-58](), [layoutlmv3/README.md:122-125]()

---

## Multimodal Fusion Mechanisms

### Unified Masking Strategy

LayoutLMv3 employs unified text-image masking for pre-training:

```mermaid
graph TB
    subgraph "Pre-training Objectives"
        MLM["Masked Language Modeling<br/>Mask 15% of text tokens"]
        MIM["Masked Image Modeling<br/>Mask 40% of image patches"]
        WPA["Word-Patch Alignment<br/>Predict if patch is masked"]
    end
    
    subgraph "Masking Strategies"
        TextMask["Text: Replace with [MASK]"]
        PatchMask["Patches: Zero out features"]
        AlignLabel["Binary labels:<br/>1=patch masked, 0=not masked"]
    end
    
    subgraph "Loss Functions"
        MLM_Loss["Cross-entropy<br/>over vocabulary"]
        MIM_Loss["Cross-entropy<br/>over visual tokens"]
        WPA_Loss["Binary cross-entropy"]
    end
    
    MLM --> TextMask
    MIM --> PatchMask
    WPA --> AlignLabel
    
    TextMask --> MLM_Loss
    PatchMask --> MIM_Loss
    AlignLabel --> WPA_Loss
```

**Word-Patch Alignment:** A novel pre-training objective that learns cross-modal alignment by predicting whether the image patch corresponding to a text word is masked. This helps the model learn fine-grained visual-textual correspondences.

**Sources:** [layoutlmv3/README.md:1-5](), [README.md:182-183]()

---

## Relationship to Other Modalities

Document AI multimodal models build upon and interact with other model families:

```mermaid
graph TB
    subgraph "Vision Models (Section 2)"
        BEiT["BEiT<br/>Masked image modeling"]
        DiT["DiT<br/>Document image pre-training"]
    end
    
    subgraph "Language Models (Section 3)"
        BERT["BERT/RoBERTa<br/>Text understanding"]
        UniLM["UniLM<br/>Unified NLU/NLG"]
    end
    
    subgraph "Document AI Models (Section 5)"
        LayoutLM["LayoutLM Series<br/>Text + Layout + Image"]
        TrOCR["TrOCR<br/>Vision encoder + text decoder"]
    end
    
    subgraph "Applications"
        FormKV["Form Understanding<br/>Key-value extraction"]
        DocVQA["Document VQA<br/>Question answering"]
        Receipt["Receipt Understanding<br/>SROIE dataset"]
    end
    
    BEiT -.visual encoder.-> LayoutLM
    BEiT -.visual encoder.-> TrOCR
    DiT -.document images.-> LayoutLM
    
    BERT -.text encoder.-> LayoutLM
    UniLM -.text decoder.-> TrOCR
    
    LayoutLM --> FormKV
    LayoutLM --> DocVQA
    LayoutLM --> Receipt
    TrOCR --> FormKV
```

**Key Integration Points:**
- **BEiT influence:** LayoutLMv3 adopts patch embedding and masked image modeling from BEiT
- **BERT backbone:** Text encoding follows BERT architecture (word embeddings + position embeddings)
- **TrOCR synergy:** Can provide text+bbox inputs for LayoutLM models
- **DiT collaboration:** DiT focuses on image-only pre-training while LayoutLM handles multimodal fusion

**Sources:** [README.md:63-65](), [README.md:74-77](), [README.md:95]()

---

