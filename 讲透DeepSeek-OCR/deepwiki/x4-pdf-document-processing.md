<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-OCR · extra page PDF Document Processing · fetched 2026-10-30 -->

# PDF Document Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py](DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py)

</details>



This page describes how to process multi-page PDF documents using the vLLM inference path. The `run_dpsk_ocr_pdf.py` script provides a production-ready pipeline for converting PDF documents to structured markdown with layout information, bounding box annotations, and visual overlays.

For single image processing, see [Single Image Processing](3.2.1). For batch evaluation on datasets, see [Batch Evaluation](3.2.3). For general vLLM inference concepts, see [vLLM Inference](3.2).

## Purpose and Scope

The PDF processing pipeline is designed for:
- **Multi-page document processing**: Academic papers, reports, books, forms.
- **Concurrent page processing**: Parallel preprocessing with `ThreadPoolExecutor` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:248-251]().
- **Batch GPU inference**: Process all pages in a single vLLM batch [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:268-271]().
- **Layout visualization**: Generate annotated PDFs with bounding boxes [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:218-220]().
- **Image extraction**: Automatically extract and save figures/charts from documents [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:183-190]().

The script produces three synchronized outputs: raw detection markup, cleaned markdown, and a visual layout PDF.

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:1-331]()

## PDF Processing Workflow

The following diagram shows the complete end-to-end workflow from PDF input to final outputs:

**Title: PDF Processing Pipeline**
```mermaid
graph TD
    INPUT["PDF Document<br/>(INPUT_PATH)"]
    
    CONVERT["pdf_to_images_high_quality()<br/>PyMuPDF/fitz<br/>DPI=144"]
    
    IMAGES["List[PIL.Image]<br/>One per page"]
    
    POOL["ThreadPoolExecutor<br/>max_workers=NUM_WORKERS<br/>(default: 64)"]
    
    PREPROC["process_single_image()<br/>Per-page preprocessing"]
    
    TOKENIZE["DeepseekOCRProcessor()<br/>.tokenize_with_images()<br/>CROP_MODE setting"]
    
    BATCH["batch_inputs<br/>List[dict]<br/>prompt + multi_modal_data"]
    
    VLLM["llm.generate()<br/>AsyncLLMEngine<br/>SamplingParams"]
    
    OUTPUTS["outputs_list<br/>Raw OCR with tags"]
    
    REMATCH["re_match()<br/>Extract bounding boxes"]
    
    DRAW["draw_bounding_boxes()<br/>Visual annotations"]
    
    EXTRACT["Extract cropped images<br/>Save to /images/"]
    
    CLEAN["Replace tags<br/>Clean markdown"]
    
    MMD_DET["*_det.mmd<br/>Raw detection output"]
    MMD["*.mmd<br/>Processed markdown"]
    PDF_OUT["*_layouts.pdf<br/>Visual annotations"]
    
    INPUT --> CONVERT
    CONVERT --> IMAGES
    IMAGES --> POOL
    POOL --> PREPROC
    PREPROC --> TOKENIZE
    TOKENIZE --> BATCH
    BATCH --> VLLM
    VLLM --> OUTPUTS
    OUTPUTS --> REMATCH
    REMATCH --> DRAW
    REMATCH --> EXTRACT
    REMATCH --> CLEAN
    DRAW --> PDF_OUT
    EXTRACT --> MMD
    CLEAN --> MMD
    OUTPUTS --> MMD_DET
```

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:64-330]()

## PDF to Image Conversion

The first stage converts PDF pages to high-quality images using PyMuPDF (`fitz`).

### Conversion Function

The `pdf_to_images_high_quality()` function handles PDF rendering:

**Function Signature**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:64-95]()

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pdf_path` | str | Required | Path to input PDF file |
| `dpi` | int | 144 | Rendering resolution |
| `image_format` | str | "PNG" | Output image format |

**Key Implementation Details**:
- Uses `fitz.Matrix(zoom, zoom)` where `zoom = dpi / 72.0` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:72-73]().
- Renders with `page.get_pixmap(matrix=matrix, alpha=False)` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:78]().
- Disables image size limits with `Image.MAX_IMAGE_PIXELS = None` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:79]().
- Converts RGBA to RGB by pasting on white background [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:87-90]().

**Title: PDF to PIL Image Conversion**
```mermaid
graph LR
    PDF["fitz.open(pdf_path)"]
    PAGES["Iterate pages<br/>page_count"]
    MATRIX["fitz.Matrix<br/>zoom = dpi/72"]
    PIXMAP["page.get_pixmap()"]
    CONVERT["pixmap.tobytes('png')"]
    PIL["PIL.Image.open()"]
    RGB["Convert RGBA→RGB<br/>White background"]
    OUTPUT["List[PIL.Image]"]
    
    PDF --> PAGES
    PAGES --> MATRIX
    MATRIX --> PIXMAP
    PIXMAP --> CONVERT
    CONVERT --> PIL
    PIL --> RGB
    RGB --> OUTPUT
```

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:64-95]()

## Concurrent Image Preprocessing

After PDF conversion, images are preprocessed in parallel using a thread pool.

### ThreadPoolExecutor Architecture

**Title: Concurrent Preprocessing Architecture**
```mermaid
graph TB
    IMAGES["List[PIL.Image]<br/>(N pages)"]
    
    EXECUTOR["ThreadPoolExecutor<br/>max_workers=NUM_WORKERS"]
    
    subgraph "Parallel Workers (64 threads default)"
        W1["Worker 1<br/>process_single_image()"]
        W2["Worker 2<br/>process_single_image()"]
        W3["Worker 3<br/>process_single_image()"]
        WN["Worker N<br/>process_single_image()"]
    end
    
    subgraph "Per-Worker Processing"
        PROC["DeepseekOCRProcessor()"]
        TOK["tokenize_with_images()<br/>bos=True, eos=True<br/>cropping=CROP_MODE"]
        CACHE["cache_item dict<br/>prompt + multi_modal_data"]
    end
    
    BATCH["batch_inputs<br/>List[dict]"]
    
    IMAGES --> EXECUTOR
    EXECUTOR --> W1
    EXECUTOR --> W2
    EXECUTOR --> W3
    EXECUTOR --> WN
    
    W1 --> PROC
    W2 --> PROC
    W3 --> PROC
    WN --> PROC
    
    PROC --> TOK
    TOK --> CACHE
    CACHE --> BATCH
```

### Process Single Image Function

The `process_single_image()` function [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:223-230]() creates a batch input dictionary for each page by calling `DeepseekOCRProcessor().tokenize_with_images()` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:234-242]().

**Preprocessing Steps per Image**:
1. Call `DeepseekOCRProcessor().tokenize_with_images()`.
2. Apply dynamic cropping if `CROP_MODE=True`.
3. Generate global view and local crops as defined in `config.py`.
4. Return structured batch input dictionary `cache_item`.

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:223-245](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:248-253]()

## Batch Inference with vLLM

Once all pages are preprocessed, they are passed to vLLM for batch inference.

### vLLM Engine Configuration

The LLM engine is initialized with production-optimized settings [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:32-44]():

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `model` | `MODEL_PATH` | Model identifier |
| `hf_overrides` | `{"architectures": ["DeepseekOCRForCausalLM"]}` | Custom model registration |
| `block_size` | 256 | KV cache block size |
| `enforce_eager` | False | Use CUDA graphs |
| `max_model_len` | 8192 | Maximum sequence length |
| `max_num_seqs` | `MAX_CONCURRENCY` (100) | Batch size limit |
| `gpu_memory_utilization` | 0.9 | GPU memory allocation |

### Sampling Parameters

The sampling configuration [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:48-54]() controls output generation:
- **Deterministic output**: `temperature=0.0`.
- **Repetition Control**: `NoRepeatNGramLogitsProcessor` with `ngram_size=20` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:46]().
- **Whitelist**: Allows table tags `<td>` (128821) and `</td>` (128822) to repeat [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:46]().

### Batch Generation Call

The inference is performed in a single batch for efficiency [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:268-271]():

```python
outputs_list = llm.generate(
    batch_inputs,           
    sampling_params=sampling_params
)
```

**Title: Batch Inference Pipeline**
```mermaid
graph LR
    BATCH["batch_inputs<br/>[page0, page1, ..., pageN]"]
    
    ENGINE["vLLM AsyncLLMEngine<br/>max_num_seqs=100"]
    
    subgraph "GPU Processing"
        VISION["Vision Encoding<br/>SAM + CLIP"]
        PROJ["MLP Projection"]
        LLM["Language Model<br/>DeepseekV2/V3"]
        LOGITS["NoRepeatNGramLogitsProcessor<br/>ngram_size=20"]
    end
    
    OUTPUTS["outputs_list<br/>[output0, output1, ..., outputN]"]
    
    BATCH --> ENGINE
    ENGINE --> VISION
    VISION --> PROJ
    PROJ --> LLM
    LLM --> LOGITS
    LOGITS --> OUTPUTS
```

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:32-54](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:268-271]()

## Post-Processing Pipeline

### Bounding Box Extraction

The `re_match()` function [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:123-135]() extracts structured annotations using the regex: `<|ref|>(.*?)<|/ref|><|det|>(.*?)<|/det|>`.

### Coordinate Extraction

The `extract_coordinates_and_label()` function [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:138-148]() parses the captured groups. Coordinates are denormalized from the [0, 999] range to pixel coordinates based on image size [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:177-181]().

### Bounding Box Visualization

The `draw_bounding_boxes()` function [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:151-215]() creates visual annotations.

**Title: Bounding Box Drawing Process**
```mermaid
graph TD
    IMAGE["Original PIL Image"]
    COPY["Create image copy"]
    DRAW1["ImageDraw.Draw()"]
    OVERLAY["Create RGBA overlay<br/>Transparent background"]
    DRAW2["ImageDraw.Draw(overlay)"]
    
    ITER["Iterate refs"]
    DENORM["Denormalize coordinates<br/>0-999 → pixel coords"]
    
    COLOR["Random color<br/>RGB + alpha"]
    
    RECT["Draw rectangle<br/>outline on main"]
    FILL["Draw filled rectangle<br/>on overlay (semi-transparent)"]
    TEXT["Draw label text<br/>with white background"]
    
    CROP{"label_type<br/>== 'image'?"}
    SAVE["Crop and save<br/>OUTPUT_PATH/images/"]
    
    PASTE["Paste overlay<br/>onto main image"]
    OUTPUT["Annotated Image"]
    
    IMAGE --> COPY
    COPY --> DRAW1
    COPY --> OVERLAY
    OVERLAY --> DRAW2
    
    DRAW1 --> ITER
    ITER --> DENORM
    DENORM --> COLOR
    
    COLOR --> RECT
    COLOR --> FILL
    COLOR --> TEXT
    
    DENORM --> CROP
    CROP -->|Yes| SAVE
    CROP -->|No| RECT
    
    RECT --> PASTE
    FILL --> PASTE
    TEXT --> PASTE
    PASTE --> OUTPUT
```

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:123-220]()

### Content Cleaning

The main loop [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:286-320]() performs the following:
1. **Repetition Detection**: Skips pages where the end-of-sentence token is missing if `SKIP_REPEAT` is enabled [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:289-293]().
2. **Tag Replacement**: Replaces `<|ref|>image<|/ref|>` tags with markdown image links [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:302-306]().
3. **Symbol Cleanup**: Normalizes LaTeX-style operators like `\coloneqq` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:313-314]().

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:286-320]()

## Output Files and Formats

| File | Extension | Purpose |
|------|-----------|---------|
| Raw detection | `*_det.mmd` | Complete model output with all tags [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:324-325](). |
| Processed markdown | `*.mmd` | Cleaned document with image links [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:321-322](). |
| Layout PDF | `*_layouts.pdf` | Visual verification with bounding boxes [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:328-329](). |
| Extracted images | `images/*.jpg` | Individual figures cropped from the PDF [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:186](). |

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:321-329]()

## Configuration and Performance Tuning

**Title: Configuration Hierarchy**
```mermaid
graph TB
    subgraph "Image Processing"
        BASE["BASE_SIZE=1024<br/>Global view resolution"]
        IMG["IMAGE_SIZE=640<br/>Local crop resolution"]
        CROP["CROP_MODE=True<br/>Enable dynamic cropping"]
        MIN["MIN_CROPS=2<br/>Minimum crops per page"]
        MAX["MAX_CROPS=6<br/>Maximum crops per page"]
    end
    
    subgraph "Concurrency Control"
        CONC["MAX_CONCURRENCY=100<br/>vLLM batch size limit"]
        WORK["NUM_WORKERS=64<br/>Preprocessing threads"]
    end
    
    subgraph "Processing Behavior"
        SKIP["SKIP_REPEAT=True<br/>Skip infinite loops"]
        PROMPT["PROMPT<br/>Task instruction"]
    end
    
    subgraph "I/O Paths"
        IN["INPUT_PATH<br/>PDF file path"]
        OUT["OUTPUT_PATH<br/>Output directory"]
        MODEL["MODEL_PATH<br/>Model identifier"]
    end
    
    BASE --> CROP
    IMG --> CROP
    CROP --> MIN
    CROP --> MAX
    
    CONC -.->|"Limits batch size"| WORK
```

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py:1-43](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:17-44]()

## Execution Flow

**Title: PDF Processing Sequence**
```mermaid
sequenceDiagram
    participant Main
    participant ThreadPool
    participant Workers
    participant vLLM
    participant PostProc
    
    Main->>Main: Load PDF → images (sequential)
    
    Main->>ThreadPool: Submit N images
    
    par Parallel Preprocessing
        ThreadPool->>Workers: process_single_image(image_0)
        ThreadPool->>Workers: process_single_image(image_1)
        ThreadPool->>Workers: process_single_image(image_N)
    end
    
    Workers-->>Main: batch_inputs (all pages)
    
    Main->>vLLM: llm.generate(batch_inputs)
    Note over vLLM: Single GPU batch<br/>Concurrent execution
    vLLM-->>Main: outputs_list
    
    loop For each page
        Main->>PostProc: re_match(output)
        PostProc-->>Main: bounding boxes
        Main->>PostProc: draw_bounding_boxes()
        PostProc-->>Main: annotated image
        Main->>PostProc: replace tags
        PostProc-->>Main: clean markdown
    end
    
    Main->>Main: Write output files
```

Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py:248-330]()

---

