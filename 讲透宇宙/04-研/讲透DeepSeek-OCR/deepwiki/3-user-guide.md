<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-OCR · page 3 User Guide · fetched 2026-10-30 -->

# User Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py](DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py)
- [README.md](README.md)

</details>



This page provides a comprehensive guide for using DeepSeek-OCR in various scenarios. It covers the two main inference pathways (Transformers and vLLM), configuration options, prompt engineering, and output interpretation.

For installation instructions and first-time setup, see [Getting Started](#2). For deep technical details on the model architecture, see [Architecture](#4). For developers extending the system, see [Developer Guide](#5).

## Overview

DeepSeek-OCR provides two distinct inference pathways optimized for different use cases:

1.  **Transformers Inference** ([Transformers Inference](#3.1)) - Standard HuggingFace interface for development, experimentation, and single-image processing.
2.  **vLLM Inference** ([vLLM Inference](#3.2)) - High-throughput GPU-optimized path for production workloads, batch processing, and PDF documents.

Both pathways use the same underlying model architecture but provide different execution environments and APIs. The system is highly configurable through a centralized configuration file and supports multiple operational modes for different resolution/performance trade-offs.

## Inference Pathway Selection

The following decision tree helps determine which inference pathway to use:

Title: Inference Selection Logic
```mermaid
graph TD
    START["Select Inference Method"]
    
    Q1{"Processing<br/>multiple documents<br/>or PDFs?"}
    Q2{"Need streaming<br/>output?"}
    Q3{"Batch evaluation<br/>for benchmarks?"}
    Q4{"Maximum<br/>throughput<br/>required?"}
    Q5{"Development or<br/>experimentation?"}
    
    VLLM_PDF["run_dpsk_ocr_pdf.py<br/>(vLLM Path)"]
    VLLM_BATCH["run_dpsk_ocr_eval_batch.py<br/>(vLLM Path)"]
    VLLM_IMAGE["run_dpsk_ocr_image.py<br/>(vLLM Path)"]
    TF_INFER["model.infer()<br/>(Transformers Path)"]
    TF_SCRIPT["run_dpsk_ocr.py<br/>(Transformers Path)"]
    
    START --> Q1
    Q1 -->|Yes| Q3
    Q1 -->|No| Q2
    
    Q3 -->|Yes| VLLM_BATCH
    Q3 -->|No| VLLM_PDF
    
    Q2 -->|Yes| Q4
    Q2 -->|No| Q5
    
    Q4 -->|Yes| VLLM_IMAGE
    Q4 -->|No| Q5
    
    Q5 -->|Yes| TF_INFER
    Q5 -->|No| TF_SCRIPT
    
    VLLM_PDF --> VLLM_DESC["Concurrent processing<br/>~2500 tokens/s<br/>A100-40G"]
    VLLM_BATCH --> BATCH_DESC["Parallel evaluation<br/>MAX_CONCURRENCY=100"]
    VLLM_IMAGE --> IMG_DESC["Streaming output<br/>AsyncLLMEngine"]
    TF_INFER --> TF_DESC["Simple API<br/>Easy integration"]
```

**Key Differences:**

| Aspect | Transformers | vLLM |
| :--- | :--- | :--- |
| **Entry Point** | `model.infer()` method | Script execution (`run_dpsk_ocr_*.py`) |
| **Configuration** | Function parameters | [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:1-43]() |
| **Output Mode** | Synchronous | Streaming or batch |
| **Throughput** | Standard | High (~2500 tokens/s) |
| **GPU Memory** | Standard | Optimized |
| **Use Case** | Development, single images | Production, PDFs, batches |

Sources: [README.md:90-107](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:1-43]()

## Common Usage Workflows

### Workflow 1: Single Image OCR (Transformers)

Title: Transformers Inference Workflow
```mermaid
sequenceDiagram
    participant User
    participant Script as "run_dpsk_ocr.py"
    participant Model as "AutoModel"
    participant Infer as "model.infer()"
    participant Output as "Output Files"
    
    User->>Script: "Import model"
    Script->>Model: "AutoModel.from_pretrained()"
    Model-->>Script: "DeepseekOCRForCausalLM"
    
    User->>Script: "Call infer()"
    Script->>Infer: "prompt, image_file,<br/>output_path, base_size,<br/>image_size, crop_mode"
    
    Infer->>Infer: "Process image"
    Infer->>Infer: "Generate output"
    Infer->>Output: "Save results"
    
    Output-->>User: "OCR text + visualizations"
```

**Code Reference:**
```python
# [README.md:168-183]()
model = AutoModel.from_pretrained(model_name, 
    _attn_implementation='flash_attention_2', 
    trust_remote_code=True)

res = model.infer(tokenizer, 
    prompt="<image>\n<|grounding|>Convert the document to markdown. ", 
    image_file='your_image.jpg', 
    output_path='your/output/dir', 
    base_size=1024, 
    image_size=640, 
    crop_mode=True)
```

Sources: [README.md:168-183]()

### Workflow 2: PDF Document Processing (vLLM)

Title: vLLM PDF Pipeline
```mermaid
sequenceDiagram
    participant User
    participant Config as "config.py"
    participant Script as "run_dpsk_ocr_pdf.py"
    participant Engine as "vllm.LLM"
    participant Output as "Output Files"
    
    User->>Config: "Set INPUT_PATH (PDF)"
    User->>Config: "Set OUTPUT_PATH"
    User->>Config: "Configure parameters"
    
    User->>Script: "python run_dpsk_ocr_pdf.py"
    
    Script->>Config: "Load configuration"
    Config-->>Script: "BASE_SIZE, IMAGE_SIZE,<br/>CROP_MODE, MAX_CONCURRENCY"
    
    Script->>Engine: "Batch generate"
    Engine-->>Script: "OCR outputs (parallel)"
    
    Script->>Output: "Write *_det.mmd (raw)"
    Script->>Output: "Write *.mmd (processed)"
    Script->>Output: "Write *_layouts.pdf (visual)"
    
    Output-->>User: "Multiple output files"
```

**Configuration Required:**
*   [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:24]() - `INPUT_PATH`: Path to PDF file.
*   [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:25]() - `OUTPUT_PATH`: Directory for outputs.
*   [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:8-12]() - Resolution and cropping settings.
*   [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:13]() - `MAX_CONCURRENCY`: Batch size control.

Sources: [README.md:100-103](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:1-43]()

### Workflow 3: Batch Evaluation (vLLM)

Title: Batch Evaluation Architecture
```mermaid
graph LR
    subgraph "Input"
        DATASET["Dataset Directory<br/>(Images)"]
    end
    
    subgraph "Configuration"
        CONFIG["config.py<br/>INPUT_PATH<br/>MAX_CONCURRENCY<br/>NUM_WORKERS"]
    end
    
    subgraph "Processing"
        SCRIPT["run_dpsk_ocr_eval_batch.py"]
        WORKERS["NUM_WORKERS=64"]
        ENGINE["vllm.LLM<br/>Batch Processing"]
    end
    
    subgraph "Output"
        RESULTS["Evaluation Results<br/>(Per Image)"]
    end
    
    DATASET --> CONFIG
    CONFIG --> SCRIPT
    SCRIPT --> WORKERS
    WORKERS --> ENGINE
    ENGINE --> RESULTS
```

**Key Parameters:**
*   [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:13]() - `MAX_CONCURRENCY=100`: GPU memory-limited batch size.
*   [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:14]() - `NUM_WORKERS=64`: CPU-bound preprocessing parallelism.

Sources: [README.md:104-107](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:13-14]()

## Operational Modes

DeepSeek-OCR supports five operational modes that trade off between vision token count, image resolution, and GPU memory usage:

| Mode | Base Size | Image Size | Crop Mode | Vision Tokens | Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tiny** | 512 | 512 | False | 64 | Extremely fast, low memory |
| **Small** | 640 | 640 | False | 100 | Quick processing |
| **Base** | 1024 | 1024 | False | 256 | Balanced |
| **Large** | 1280 | 1280 | False | 400 | High resolution |
| **Gundam** ⭐ | 1024 | 640 | True | 256 + n×100 | Adaptive, production-ready |

**Current Active Mode (Gundam):**
```python
# [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:8-12]()
BASE_SIZE = 1024      # Global view resolution
IMAGE_SIZE = 640      # Local crop resolution  
CROP_MODE = True      # Enable dynamic cropping
MIN_CROPS = 2         # Minimum number of crops
MAX_CROPS = 6         # Maximum crops (GPU memory limited)
```

The **Gundam mode** is recommended for production use. It processes images with one global view and multiple local crops.

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:1-12](), [README.md:191-199]()

## Configuration-to-Code Mapping

The following diagram shows how configuration parameters in `config.py` affect system components:

Title: Config Entity Space Mapping
```mermaid
graph TB
    subgraph "config.py Parameters"
        P1["BASE_SIZE<br/>(line 8)"]
        P2["IMAGE_SIZE<br/>(line 9)"]
        P3["CROP_MODE<br/>(line 10)"]
        P4["MIN_CROPS/MAX_CROPS<br/>(lines 11-12)"]
        P5["MAX_CONCURRENCY<br/>(line 13)"]
        P6["NUM_WORKERS<br/>(line 14)"]
        P7["MODEL_PATH<br/>(line 17)"]
        P8["PROMPT<br/>(line 27)"]
    end
    
    subgraph "System Entities"
        VLLM_LLM["vllm.LLM"]
        TOKENIZER["AutoTokenizer"]
        LOGITS["NGramPerReqLogitsProcessor"]
        SAMPLING["SamplingParams"]
    end
    
    P1 --> VLLM_LLM
    P2 --> VLLM_LLM
    P3 --> VLLM_LLM
    P4 --> VLLM_LLM
    P6 --> VLLM_LLM
    
    P5 --> VLLM_LLM
    P8 --> SAMPLING
    
    P7 --> VLLM_LLM
    P7 --> TOKENIZER
```

**Parameter Effects:**
*   **BASE_SIZE, IMAGE_SIZE**: Control vision encoder input dimensions.
*   **CROP_MODE**: Enables/disables dynamic cropping for multi-crop processing.
*   **MAX_CONCURRENCY**: Limits vLLM engine batch size to prevent GPU OOM.
*   **NUM_WORKERS**: Controls workers for image pre-processing (resize/padding).

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:1-43]()

## Prompt Engineering

DeepSeek-OCR uses task-specific prompts to control output format and behavior.

### Common Prompt Templates

| Task | Prompt | Grounding |
| :--- | :--- | :--- |
| **Document Markdown** | `<image>\n<|grounding|>Convert the document to markdown.` | Yes |
| **General OCR** | `<image>\n<|grounding|>OCR this image.` | Yes |
| **Free OCR** | `<image>\nFree OCR.` | No |
| **Figure Parsing** | `<image>\nParse the figure.` | No |
| **Image Description** | `<image>\nDescribe this image in detail.` | No |
| **Text Localization** | `<image>\nLocate <|ref|>xxxx<|/ref|> in the image.` | Yes |

**Special Tokens:**
*   `<image>`: Required placeholder for image input.
*   `<|grounding|>`: Enables detection tags and coordinate output.
*   `<|ref|>...<|/ref|>`: Used to mark reference text for localization.

For detailed prompt usage and examples, see [Working with Prompts](#3.4).

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:27-37](), [README.md:200-209]()

## Output Formats

The system generates different output formats depending on the inference pathway:

### Transformers Output
When using `model.infer()`:
*   **Text file**: Contains raw OCR output.
*   **Visualization**: Image with optional bounding boxes if `save_results=True`.

### vLLM Output
*   **Single Image**: Streaming output via `run_dpsk_ocr_image.py`.
*   **PDF Processing**: Generates `.mmd` (markdown), `_det.mmd` (raw with tags), and `_layouts.pdf` (visualizations).

### vLLM Specific: NGram Logits Processor
For vLLM inference, a specialized `NGramPerReqLogitsProcessor` is used to handle repetitive structures like table tags:
*   `ngram_size`: Size of n-gram to check.
*   `window_size`: Lookback window.
*   `whitelist_token_ids`: Tokens exempt from repetition penalties (e.g., `<td>`, `</td>`).

Sources: [README.md:96-107](), [README.md:119-164]()

## Next Steps

*   **For Transformers usage details**: See [Transformers Inference](#3.1)
*   **For vLLM usage details**: See [vLLM Inference](#3.2)
*   **For configuration tuning**: See [Configuration System](#3.3)
*   **For prompt examples**: See [Working with Prompts](#3.4)
*   **For output processing**: See [Understanding Output](#3.5)

---

