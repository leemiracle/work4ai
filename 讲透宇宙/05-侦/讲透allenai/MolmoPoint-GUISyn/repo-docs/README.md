<div align="center">
  <img src="data/logo.svg" alt="MolmoPoint Logo" width="800" style="margin-left:'auto' margin-right:'auto' display:'block'"/>
  <br>
</div>
<p align="center">
  <a href="https://github.com/allenai/MolmoPoint-GUISyn/blob/main/LICENSE">
    <img alt="GitHub License" src="https://img.shields.io/github/license/allenai/OLMo">
  </a>
  <a href="https://allenai.org/papers/molmopoint">
    <img alt="Paper" src="https://img.shields.io/badge/MolmoPoint-blog-F0529C">
  </a>
  <a href="https://huggingface.co/allenai/MolmoPoint-GUI-8B">
    <img alt="Model Checkpoints" src="https://img.shields.io/badge/%F0%9F%A4%97%20HF-Models-yellow">
  </a>
  <a href="https://huggingface.co/datasets/allenai/MolmoPoint-GUISyn">
    <img alt="MolmoPoint-GUISyn" src="https://img.shields.io/badge/%F0%9F%A4%97%20HF-Datasets-green">
  </a>
  <a href="https://huggingface.co/spaces/allenai/MolmoPoint-GUI-8B-Demo">
    <img alt="Demo" src="https://img.shields.io/badge/%F0%9F%A4%97%20HF-Demo-blue">
  </a>
</p>

Synthetic grounding data generation pipeline for training GUI agents. Given a text context description (e.g., "MacOS system, using VSCode") or a reference screenshot image, the pipeline uses an LLM to generate self-contained HTML, renders it as a screenshot, automatically extracts bounding boxes for all visible UI elements, and then annotates each element with semantic names and interaction intents.

## Installation

```bash
conda create --name guisyn python=3.11
conda activate guisyn
pip install -r requirements.txt
playwright install chromium
```

Then export your API keys:

```bash
export OPENAI_API_KEY=your-key      # if using GPT models
export ANTHROPIC_API_KEY=your-key   # if using Claude models
```

## Pipeline Overview

The pipeline has two stages:

1. **Generation** (`generate.py`): LLM generates HTML from a context description or reference image -> Playwright renders it to a screenshot -> bounding boxes are extracted for every visible element.

2. **Annotation** (`annotate.py`): An LLM annotates each bounding box with a human-readable name and 5 diverse interaction intents (e.g., "Click the Bold button to bold the selected text").

## Quick Start

### Generate a single example from text

```bash
python generate.py --context "MacOS system, using VSCode with a Python project open"
```

This creates a directory under `./output/data/<example_id>/` containing:
- `<id>.png` — rendered screenshot
- `<id>_bbox.png` — screenshot with bounding box overlays
- `<id>_bboxes.json` — extracted bounding boxes
- `page.html` — source HTML
- `metadata.json` — generation metadata

### Generate from a reference screenshot

```bash
python generate.py --reference_image path/to/screenshot.png
```

The model reproduces the reference image's appearance as HTML and extracts bounding boxes.

### Annotate an example

```bash
python annotate.py --mode demo --example_dir ./output/data/grounding-xxx
```

This adds `annotated_bboxes.json` to the example directory with semantic names and interaction intents for each UI element.

## Batch Generation (Large Scale)

For generating data at scale, the pipeline supports the OpenAI and Anthropic batch APIs.

### Step 1: Prepare batch prompts

Create a text file with one context description per line:

```
MacOS system, using VSCode with a Python project open
Windows 11 desktop, Chrome browser showing Gmail
Ubuntu terminal running htop with high CPU usage
```

Then generate and upload the batch:

```bash
# Text-based batch
python generate.py --mode batch_text \
    --batch_input_file contexts.txt \
    --upload_batch

# Image-based batch (one image path per line)
python generate.py --mode batch_image \
    --batch_input_file images.txt \
    --upload_batch
```

### Step 2: Process batch results

After the batch job completes, download the results JSONL and process it:

```bash
python generate.py --mode batch_process \
    --batch_response_file results.jsonl
```

### Step 3: Batch annotation

```bash
# Auto-discover all unannotated examples and submit
python annotate.py --mode batch --discover --upload_batch

# Process annotation results
python annotate.py --mode batch_process \
    --batch_response_file anno_results.jsonl
```

## Visualizer

A browser-based visualizer (`visualize.html`) is included for inspecting generated data. It overlays bounding boxes on screenshots and shows element names, intents, and HTML snippets on hover.

**Option 1: Open a folder directly** (no server needed) — click "Open Folder" and select an example directory.

**Option 2: Serve via HTTP** — run from the repo root:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080/visualize.html` and enter an example ID to load it.

## Key Arguments

### generate.py

| Argument | Default | Description |
|---|---|---|
| `--model_name` | `claude-sonnet-4-6` | LLM to use (must contain `gpt` or `claude`) |
| `--output_dir` | `./output` | Root output directory |
| `--context` | — | Text context for single generation |
| `--reference_image` | — | Path to reference screenshot |
| `--mode` | `demo` | `demo`, `batch_text`, `batch_image`, or `batch_process` |
| `--only_leaf_boxes` | `False` | Only keep leaf bounding boxes (filter parents) |
| `--seed` | `42` | Random seed |
| `--persona_cache` | — | JSON file to track used personas (prevents repeats) |

### annotate.py

| Argument | Default | Description |
|---|---|---|
| `--model_name` | `claude-sonnet-4-6` | LLM to use |
| `--output_dir` | `./output` | Root output directory |
| `--mode` | `demo` | `demo`, `batch`, or `batch_process` |
| `--example_dir` | — | Full path to example directory (demo mode) |
| `--discover` | `False` | Auto-discover unannotated examples (batch mode) |

## Project Structure

```
MolmoPoint-GUISyn/
├── generate.py                     # CLI: screenshot generation
├── annotate.py                     # CLI: bbox annotation
├── visualize.html                  # Browser-based data visualizer
├── pipeline/
│   ├── __init__.py
│   ├── grounding_generator.py      # GroundingGenerator class
│   ├── grounding_annotator.py      # GroundingAnnotator class
│   ├── bbox_extractor.py           # HTML -> bounding box extraction (Playwright)
│   └── llm_utils.py                # LLM API helpers (OpenAI & Anthropic)
├── data/
│   └── persona.jsonl               # Persona descriptions for diverse generation
├── requirements.txt
└── README.md
```

## Citation

If you use this codebase or our datasets in your work, please cite:

```bibtex
@article{clark2026molmopoint,
  title={MolmoPoint: Better Pointing for VLMs with Grounding Tokens},
  author={Clark, Christopher and Yang, Yue and Park, Jae Sung and Ma, Zixian and Zhang, Jieyu and Tripathi, Rohun and Salehi, Mohammadreza and Lee, Sangho and Anderson, Taira and Han, Winson and others},
  journal={arXiv preprint arXiv:2603.28069},
  year={2026}
}
```

```bibtex
@article{yang2025scaling,
      title={Scaling Text-Rich Image Understanding via Code-Guided Synthetic Multimodal Data Generation},
      author={Yang, Yue and Patel, Ajay and Deitke, Matt and Gupta, Tanmay and Weihs, Luca and Head, Andrew and Yatskar, Mark and Callison-Burch, Chris and Krishna, Ranjay and Kembhavi, Aniruddha and others},
      journal={arXiv preprint arXiv:2502.14846},
      year={2025}
}
```
