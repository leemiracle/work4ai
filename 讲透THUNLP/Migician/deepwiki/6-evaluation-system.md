<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/Migician · page 6 Evaluation System · fetched 2026-11-02 -->

# Evaluation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [eval/utils.py](eval/utils.py)

</details>



The Evaluation System provides a comprehensive framework for benchmarking multi-image grounding capabilities across multiple Multimodal Large Language Models (MLLMs). It supports two evaluation paradigms—direct inference and Chain-of-Thought reasoning—and tests models on three major benchmarks: MIG-Bench (multi-image grounding), MIBench (multi-image understanding), and MMIU (forensic detection). The system handles seven different MLLM architectures and provides standardized metrics including IOU-based grounding accuracy and multiple-choice accuracy.

For information about the benchmarks themselves (MIG-Bench structure, task types, and data format), see [Benchmarks](#7). For training the Migician model that this system evaluates, see [Training Pipeline](#5).

## Overview

The evaluation system is located in the `eval/` directory and provides infrastructure for consistent, reproducible benchmarking across multiple model architectures. It abstracts model-specific preprocessing, handles multi-image inputs, extracts bounding box predictions, and computes standardized metrics.

**Sources:** [README.md:225-273](), [eval/utils.py:1-270]()

## Directory Structure

The evaluation system follows this organization:

```
eval/
├── MIG-Bench/                    # MIG-Bench benchmark dataset
│   ├── images/                   # Image files organized by task
│   │   ├── common/
│   │   ├── correspondence/
│   │   ├── group_grounding/
│   │   └── ...                   # 10 task types total
│   └── MIG_data.json            # Evaluation dataset with ground truth
│
├── eval_output/                  # Generated predictions and results
│
├── others/                       # MIBench and MMIU benchmarks
│
├── MIG_bench_eval.py            # Direct inference evaluation script
├── MIG_bench_cot.py             # Chain-of-Thought evaluation script
├── utils.py                      # Shared utility functions
├── chat.py                       # Model-specific chat interfaces
└── requirements.txt              # Evaluation dependencies
```

**Sources:** [README.md:228-247]()

## System Architecture

The evaluation system orchestrates multiple components to provide standardized benchmarking:

```mermaid
graph TD
    subgraph "Evaluation Scripts"
        DIRECT["MIG_bench_eval.py<br/>Direct Inference"]
        COT["MIG_bench_cot.py<br/>Chain-of-Thought"]
    end
    
    subgraph "Utility Layer"
        EXTRACT["extract_bbox()<br/>Bbox Parser"]
        IOU["calculate_iou()<br/>IOU Calculator"]
        PREPROC["Image Processors<br/>dynamic_preprocess()<br/>load_image_intenvl2()"]
        INDEX["get_image_index()<br/>Text Parser"]
    end
    
    subgraph "Model Adapters"
        M1["Migician"]
        M2["Qwen2-VL"]
        M3["InternVL2"]
        M4["MiniCPM-V_2.6"]
        M5["LLaVA-OneVision"]
        M6["mPLUG-Owl3"]
        M7["Mantis"]
    end
    
    subgraph "Benchmark Data"
        MIGB["MIG_data.json<br/>10 Task Types"]
        MIBB["MIBench<br/>Understanding"]
        MMIU["MMIU<br/>Forensics"]
    end
    
    subgraph "Output"
        METRICS["Metrics Report<br/>IOU@0.7/0.5/0.3<br/>Average IOU<br/>Accuracy"]
        JSON["eval_output/<br/>predictions.json"]
    end
    
    DIRECT -->|"uses"| EXTRACT
    DIRECT -->|"uses"| IOU
    DIRECT -->|"uses"| PREPROC
    COT -->|"uses"| EXTRACT
    COT -->|"uses"| IOU
    COT -->|"uses"| INDEX
    
    DIRECT -->|"loads"| MIGB
    DIRECT -->|"loads"| MIBB
    DIRECT -->|"loads"| MMIU
    COT -->|"loads"| MIGB
    
    DIRECT -->|"invokes"| M1
    DIRECT -->|"invokes"| M2
    DIRECT -->|"invokes"| M3
    COT -->|"invokes"| M1
    COT -->|"invokes"| M2
    
    M1 -->|"produces"| JSON
    M2 -->|"produces"| JSON
    M3 -->|"produces"| JSON
    
    JSON -->|"computed from"| METRICS
```

**Sources:** [README.md:225-273](), [eval/utils.py:19-145]()

## Supported Models

The evaluation system provides adapters for seven MLLM architectures, each with model-specific preprocessing and inference logic:

| Model | Hugging Face Path | Special Requirements |
|-------|-------------------|---------------------|
| **Migician** | `Michael4933/Migician` | Special tokens: `<\|object_ref_start\|>`, `<\|box_start\|>` |
| **Qwen2-VL** | `Qwen/Qwen2-VL-7B-Instruct` | `process_vision_info()` from qwen_vl_utils |
| **InternVL2** | `OpenGVLab/InternVL2-8B` | `dynamic_preprocess()`, custom device mapping |
| **MiniCPM-V_2.6** | `openbmb/MiniCPM-V-2_6` | Standard vision-language interface |
| **LLaVA-OneVision** | `llava-hf/llava-onevision-qwen2-7b-ov-hf` | HF transformers pipeline |
| **mPLUG-Owl3** | `mPLUG/mPLUG-Owl3-7B-241101` | Custom chat template |
| **Mantis** | `TIGER-Lab/Mantis-8B-Idefics2` | Idefics2 architecture |

**Sources:** [README.md:272-273]()

## Evaluation Workflow

### Direct Inference Pipeline

The direct inference approach (`MIG_bench_eval.py`) performs end-to-end evaluation in a single forward pass:

```mermaid
sequenceDiagram
    participant Script as MIG_bench_eval.py
    participant Data as MIG_data.json
    participant Utils as utils.py
    participant Model as MLLM
    participant Metrics as Metric Calculator
    
    Script->>Data: "Load benchmark"
    Data-->>Script: "List of test cases"
    
    loop For each test case
        Script->>Utils: "Preprocess images"
        Utils-->>Script: "Processed tensors"
        
        Script->>Model: "Generate with prompt + images"
        Model-->>Script: "Text response with bbox"
        
        Script->>Utils: "extract_bbox(response)"
        Utils-->>Script: "Parsed coordinates [x1,y1,x2,y2]"
        
        Script->>Utils: "calculate_iou(pred, gt)"
        Utils-->>Script: "IOU score (0-1)"
        
        Script->>Metrics: "Accumulate IOU"
    end
    
    Metrics-->>Script: "IOU@0.7, IOU@0.5, IOU@0.3, Average"
    Script->>Script: "Write results to eval_output/"
```

**Sources:** [README.md:243-244](), [eval/utils.py:19-83]()

### Chain-of-Thought Pipeline

The Chain-of-Thought approach (`MIG_bench_cot.py`) decomposes multi-image grounding into two phases:

```mermaid
graph LR
    subgraph "Phase 1: Description"
        IN1["Multi-Image Input"]
        Q1["Question about target"]
        M1["MLLM Inference"]
        DESC["Text Description"]
    end
    
    subgraph "Phase 2: Grounding"
        IN2["Individual Images"]
        DESC2["Description from Phase 1"]
        M2["MLLM Inference"]
        BBOX["Bounding Box"]
    end
    
    subgraph "Post-Processing"
        IDX["get_image_index()<br/>Extract image reference"]
        EXTRACT["extract_bbox()<br/>Parse coordinates"]
        IOU["calculate_iou()<br/>Compare with GT"]
    end
    
    IN1 --> M1
    Q1 --> M1
    M1 --> DESC
    
    DESC --> DESC2
    IN2 --> M2
    DESC2 --> M2
    M2 --> BBOX
    
    BBOX --> IDX
    BBOX --> EXTRACT
    IDX --> IOU
    EXTRACT --> IOU
```

**Sources:** [README.md:242-243](), [eval/utils.py:131-144]()

## Core Utility Functions

The `utils.py` module provides shared functionality used by both evaluation scripts:

### Bounding Box Extraction

The `extract_bbox()` function parses multiple bounding box formats from model outputs:

```mermaid
graph TD
    INPUT["Raw Model Output"]
    
    TRY1["Regex: r'\((\d+),\s*(\d+)\),\s*\((\d+),\s*(\d+)\)'<br/>Format: (x1,y1),(x2,y2)"]
    TRY2["Regex: r'\[(\d+\.\d+)...\]'<br/>Format: [0.3, 0.2, 0.4, 0.28]"]
    TRY3["Regex: r'\((\d+\.\d+),...\)'<br/>Format: (0.3,0.2),(0.4,0.28)"]
    TRY4["Regex: r'\[(\d+)...\]'<br/>Format: [28, 586, 362, 793]"]
    TRY5["Regex: r'<box>(\d+)...'<br/>Format: <box>826 704 993 984</box>"]
    
    NORM["Normalize to 0-1<br/>if value >= 1: divide by 1000"]
    OUTPUT["[x1, y1, x2, y2]<br/>Normalized coordinates"]
    FAIL["[0.0, 0.0, 0.0, 0.0]<br/>Default on parse failure"]
    
    INPUT --> TRY1
    TRY1 -->|"No match"| TRY2
    TRY2 -->|"No match"| TRY3
    TRY3 -->|"No match"| TRY4
    TRY4 -->|"No match"| TRY5
    TRY5 -->|"No match"| FAIL
    
    TRY1 -->|"Match found"| NORM
    TRY2 -->|"Match found"| NORM
    TRY3 -->|"Match found"| NORM
    TRY4 -->|"Match found"| NORM
    TRY5 -->|"Match found"| NORM
    
    NORM --> OUTPUT
```

The function handles Migician's native format `(x1,y1),(x2,y2)` as well as various alternative formats from other models. Coordinates are normalized to the 0-1 range for consistent IOU calculation.

**Sources:** [eval/utils.py:19-44]()

### IOU Calculation

The `calculate_iou()` function computes Intersection over Union between predicted and ground truth boxes:

**Formula:**
```
IOU = Intersection Area / Union Area
    = (Overlap Area) / (Area1 + Area2 - Overlap Area)
```

**Implementation Logic:**
1. Extract intersection bounds: `max(x1_a, x1_b)`, `max(y1_a, y1_b)`, `min(x2_a, x2_b)`, `min(y2_b, y2_b)`
2. Check for valid intersection: `x_right >= x_left` and `y_bottom >= y_top`
3. Calculate areas: intersection, box1, box2
4. Compute union: `area1 + area2 - intersection`
5. Return: `intersection / union`

**Sources:** [eval/utils.py:61-83]()

### Image Preprocessing

#### For Standard Models: `resize()`

Simple resizing to maximum dimension of 800 pixels while maintaining aspect ratio.

**Sources:** [eval/utils.py:85-93]()

#### For InternVL2: `dynamic_preprocess()`

Sophisticated preprocessing that splits images into grid blocks based on aspect ratio:

```mermaid
graph TD
    INPUT["Original Image<br/>width x height"]
    
    ASPECT["Calculate aspect_ratio<br/>= width / height"]
    
    RATIOS["Generate target_ratios<br/>(i,j) where i*j in [min_num, max_num]"]
    
    FIND["find_closest_aspect_ratio()<br/>Match to target grid"]
    
    RESIZE["Resize to<br/>target_width x target_height"]
    
    SPLIT["Split into blocks<br/>each of size image_size x image_size"]
    
    THUMB{use_thumbnail<br/>and blocks > 1?}
    
    ADD["Add thumbnail<br/>Full image at image_size x image_size"]
    
    OUTPUT["List of PIL Images<br/>Ready for transform"]
    
    INPUT --> ASPECT
    ASPECT --> RATIOS
    RATIOS --> FIND
    FIND --> RESIZE
    RESIZE --> SPLIT
    SPLIT --> THUMB
    THUMB -->|"Yes"| ADD
    THUMB -->|"No"| OUTPUT
    ADD --> OUTPUT
```

This function is critical for InternVL2's multi-scale image understanding. It divides images into an optimal grid layout (e.g., 2x3, 3x3) based on aspect ratio, then adds a thumbnail for global context.

**Sources:** [eval/utils.py:178-214](), [eval/utils.py:232-239]()

### Text Parsing

The `get_image_index()` function extracts image references from model responses:

| Pattern | Recognized Text | Returned Index |
|---------|----------------|----------------|
| 0 | `"first"`, `"Image-1"`, `"Image1"`, `"Image 1"`, `"1th"` | 0 |
| 1 | `"second"`, `"Image-2"`, `"Image2"`, `"Image 2"`, `"2th"` | 1 |
| 2 | `"third"`, `"Image-3"`, `"Image3"`, `"Image 3"`, `"3th"` | 2 |
| 3 | `"fourth"`, `"Image-4"`, `"Image4"`, `"Image 4"`, `"4th"` | 3 |
| 4 | `"fifth"`, `"Image-5"`, `"Image5"`, `"Image 5"`, `"5th"` | 4 |
| 5 | `"sixth"`, `"Image-6"`, `"Image6"`, `"Image 6"`, `"6th"` | 5 |
| -1 | No match found | -1 (error) |

This is essential for CoT evaluation where the model first identifies which image contains the target, then grounds it.

**Sources:** [eval/utils.py:131-144]()

## Benchmark Data Format

Test cases in `MIG_data.json` follow this structure:

```json
{
    "task": "reasoning",
    "images": [
        "./MIG-Bench/images/reasoning/case097_1.png",
        "./MIG-Bench/images/reasoning/case097_2.png"
    ],
    "question": "Which item in Image-2 share the similar feature of Image-1?",
    "answer": [0.418, 0.391, 0.595, 0.546],
    "additional_info": "Which item in Image-2 share the similar feature?",
    "need_format": true
}
```

**Key Fields:**
- `task`: Task type identifier (e.g., `"reasoning"`, `"common"`, `"correspondence"`)
- `images`: List of relative paths to image files
- `question`: Natural language query for the model
- `answer`: Ground truth bounding box `[x1, y1, x2, y2]` normalized to 0-1 range
- `additional_info`: Alternative question formulation (for CoT description phase)
- `need_format`: Boolean indicating whether post-processing is needed

**Sources:** [README.md:248-271]()

## Evaluation Metrics

The system reports multiple IOU-based metrics to capture grounding accuracy at different strictness levels:

### IOU Thresholds

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| **IOU@0.7** | IOU ≥ 0.7 | Strict: High-precision localization required |
| **IOU@0.5** | IOU ≥ 0.5 | Moderate: Standard detection threshold (COCO-style) |
| **IOU@0.3** | IOU ≥ 0.3 | Loose: Partial overlap acceptable |
| **Average IOU** | Mean of all IOUs | Overall localization quality |

### Metric Calculation

```mermaid
graph LR
    subgraph "For each test case"
        PRED["Predicted Box<br/>[x1,y1,x2,y2]"]
        GT["Ground Truth<br/>[x1,y1,x2,y2]"]
        CALC["calculate_iou()"]
        IOU["IOU Score<br/>0.0 to 1.0"]
    end
    
    subgraph "Aggregate"
        ACC7["Count where IOU >= 0.7"]
        ACC5["Count where IOU >= 0.5"]
        ACC3["Count where IOU >= 0.3"]
        AVG["Sum all IOUs"]
    end
    
    subgraph "Final Metrics"
        R7["IOU@0.7 = ACC7 / Total"]
        R5["IOU@0.5 = ACC5 / Total"]
        R3["IOU@0.3 = ACC3 / Total"]
        RA["Avg IOU = AVG / Total"]
    end
    
    PRED --> CALC
    GT --> CALC
    CALC --> IOU
    
    IOU --> ACC7
    IOU --> ACC5
    IOU --> ACC3
    IOU --> AVG
    
    ACC7 --> R7
    ACC5 --> R5
    ACC3 --> R3
    AVG --> RA
```

**Sources:** [README.md:272-273](), [eval/utils.py:61-83]()

### Additional Accuracy Metrics

For understanding benchmarks (MIBench, MMIU), the system computes multiple-choice accuracy:

```
Accuracy = Correct Predictions / Total Questions
```

This is handled by the `calculate()` function which checks if the ground truth label appears in the model's response.

**Sources:** [eval/utils.py:46-56]()

## Model-Specific Adaptations

### InternVL2 Device Mapping

For multi-GPU inference, the `split_model()` function distributes InternVL2 layers across GPUs:

**Strategy:**
1. Vision model → GPU 0
2. MLP projector → GPU 0  
3. Language model layers → Distributed evenly
4. First GPU treated as "half" capacity (also handles vision)
5. Output head → GPU 0

**Sources:** [eval/utils.py:241-266]()

### Qwen2-VL Special Token Handling

Migician and Qwen2-VL use special tokens for structured grounding:

- **Input tokens:** `<|object_ref_start|>`, `<|object_ref_end|>` to delimit grounding targets
- **Output tokens:** `<|box_start|>`, `<|box_end|>` to delimit bounding box coordinates

The `extract_bbox()` function specifically handles the `(x1,y1),(x2,y2)` format that Migician outputs between box tokens.

**Sources:** [README.md:138-155](), [eval/utils.py:19-44]()

## Multiprocessing Support

For efficient evaluation, `MIG_bench_eval.py` supports parallel processing across multiple test cases. The evaluation scripts can be configured to use multiple worker processes to accelerate inference across the benchmark dataset.

## Output Format

Results are written to `eval_output/` with two types of files:

**Prediction Files:**
```json
{
    "task": "reasoning",
    "predicted_bbox": [0.421, 0.388, 0.598, 0.551],
    "ground_truth": [0.418, 0.391, 0.595, 0.546],
    "iou": 0.89,
    "response": "The target is in the second image. <|box_start|>(421,388),(598,551)<|box_end|>"
}
```

**Summary Reports:**
```
=== MIG-Bench Results ===
IOU@0.7: 78.3%
IOU@0.5: 91.2%
IOU@0.3: 96.8%
Average IOU: 0.812

Per-Task Breakdown:
  common: 0.835
  correspondence: 0.791
  reasoning: 0.806
  ...
```

**Sources:** [README.md:272-273]()

---

This evaluation system provides a standardized, extensible framework for benchmarking multi-image grounding capabilities across diverse MLLM architectures, enabling fair comparison and systematic analysis of model performance.

---

