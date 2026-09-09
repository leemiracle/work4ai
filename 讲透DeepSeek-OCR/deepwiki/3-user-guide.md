> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3-user-guide](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3-user-guide)
> DeepWiki deepseek-ai/DeepSeek-OCR

# User Guide

  Relevant source files 
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py)
 - [README.md](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1)
 
  This page provides a comprehensive guide for using DeepSeek-OCR in various scenarios. It covers the two main inference pathways (Transformers and vLLM), configuration options, prompt engineering, and output interpretation.

 For installation instructions and first-time setup, see [Getting Started](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/2-getting-started). For deep technical details on the model architecture, see [Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4-architecture). For developers extending the system, see [Developer Guide](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5-developer-guide).

 
## Overview

 DeepSeek-OCR provides two distinct inference pathways optimized for different use cases:

 
 - **Transformers Inference** ([Transformers Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.1-transformers-inference)) - Standard HuggingFace interface for development, experimentation, and single-image processing.
 - **vLLM Inference** ([vLLM Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.2-vllm-inference)) - High-throughput GPU-optimized path for production workloads, batch processing, and PDF documents.
 
 Both pathways use the same underlying model architecture but provide different execution environments and APIs. The system is highly configurable through a centralized configuration file and supports multiple operational modes for different resolution/performance trade-offs.

 
## Inference Pathway Selection

 The following decision tree helps determine which inference pathway to use:

 Title: Inference Selection Logic

 
```

```

 **Key Differences:**

 
| Aspect | Transformers | vLLM |
|---|---|---|
| Entry Point | model.infer() method | Script execution (run_dpsk_ocr_*.py) |
| Configuration | Function parameters | DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py1-43 |
| Output Mode | Synchronous | Streaming or batch |
| Throughput | Standard | High (~2500 tokens/s) |
| GPU Memory | Standard | Optimized |
| Use Case | Development, single images | Production, PDFs, batches |

 Sources: [README.md90-107](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L90-L107) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py1-43](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L1-L43)

 
## Common Usage Workflows

 
### Workflow 1: Single Image OCR (Transformers)

 Title: Transformers Inference Workflow

 
```

```

 **Code Reference:**

 
```

```

 Sources: [README.md168-183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L168-L183)

 
### Workflow 2: PDF Document Processing (vLLM)

 Title: vLLM PDF Pipeline

 
```

```

 **Configuration Required:**

 
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py24](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L24-L24) - `INPUT_PATH`: Path to PDF file.
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py25](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L25-L25) - `OUTPUT_PATH`: Directory for outputs.
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py8-12](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L8-L12) - Resolution and cropping settings.
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py13](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L13-L13) - `MAX_CONCURRENCY`: Batch size control.
 
 Sources: [README.md100-103](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L100-L103) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py1-43](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L1-L43)

 
### Workflow 3: Batch Evaluation (vLLM)

 Title: Batch Evaluation Architecture

 
```

```

 **Key Parameters:**

 
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py13](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L13-L13) - `MAX_CONCURRENCY=100`: GPU memory-limited batch size.
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py14](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L14-L14) - `NUM_WORKERS=64`: CPU-bound preprocessing parallelism.
 
 Sources: [README.md104-107](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L104-L107) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py13-14](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L13-L14)

 
## Operational Modes

 DeepSeek-OCR supports five operational modes that trade off between vision token count, image resolution, and GPU memory usage:

 
| Mode | Base Size | Image Size | Crop Mode | Vision Tokens | Use Case |
|---|---|---|---|---|---|
| Tiny | 512 | 512 | False | 64 | Extremely fast, low memory |
| Small | 640 | 640 | False | 100 | Quick processing |
| Base | 1024 | 1024 | False | 256 | Balanced |
| Large | 1280 | 1280 | False | 400 | High resolution |
| Gundam ⭐ | 1024 | 640 | True | 256 + n×100 | Adaptive, production-ready |

 **Current Active Mode (Gundam):**

 
```

```

 The **Gundam mode** is recommended for production use. It processes images with one global view and multiple local crops.

 Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py1-12](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L1-L12) [README.md191-199](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L191-L199)

 
## Configuration-to-Code Mapping

 The following diagram shows how configuration parameters in `config.py` affect system components:

 Title: Config Entity Space Mapping

 
```

```

 **Parameter Effects:**

 
 - **BASE_SIZE, IMAGE_SIZE**: Control vision encoder input dimensions.
 - **CROP_MODE**: Enables/disables dynamic cropping for multi-crop processing.
 - **MAX_CONCURRENCY**: Limits vLLM engine batch size to prevent GPU OOM.
 - **NUM_WORKERS**: Controls workers for image pre-processing (resize/padding).
 
 Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py1-43](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L1-L43)

 
## Prompt Engineering

 DeepSeek-OCR uses task-specific prompts to control output format and behavior.

 
### Common Prompt Templates

 
| Task | Prompt | Grounding |
|---|---|---|
| Document Markdown | `\n< | grounding |
| General OCR | `\n< | grounding |
| Free OCR | <image>\nFree OCR. | No |
| Figure Parsing | <image>\nParse the figure. | No |
| Image Description | <image>\nDescribe this image in detail. | No |
| Text Localization | `\nLocate < | ref |

 **Special Tokens:**

 
 - `<image>`: Required placeholder for image input.
 - `<|grounding|>`: Enables detection tags and coordinate output.
 - `<|ref|>...<|/ref|>`: Used to mark reference text for localization.
 
 For detailed prompt usage and examples, see [Working with Prompts](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.4-working-with-prompts).

 Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py27-37](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L27-L37) [README.md200-209](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L200-L209)

 
## Output Formats

 The system generates different output formats depending on the inference pathway:

 
### Transformers Output

 When using `model.infer()`:

 
 - **Text file**: Contains raw OCR output.
 - **Visualization**: Image with optional bounding boxes if `save_results=True`.
 
 
### vLLM Output

 
 - **Single Image**: Streaming output via `run_dpsk_ocr_image.py`.
 - **PDF Processing**: Generates `.mmd` (markdown), `_det.mmd` (raw with tags), and `_layouts.pdf` (visualizations).
 
 
### vLLM Specific: NGram Logits Processor

 For vLLM inference, a specialized `NGramPerReqLogitsProcessor` is used to handle repetitive structures like table tags:

 
 - `ngram_size`: Size of n-gram to check.
 - `window_size`: Lookback window.
 - `whitelist_token_ids`: Tokens exempt from repetition penalties (e.g., `<td>`, `</td>`).
 
 Sources: [README.md96-107](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L96-L107) [README.md119-164](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L119-L164)

 
## Next Steps

 
 - **For Transformers usage details**: See [Transformers Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.1-transformers-inference)
 - **For vLLM usage details**: See [vLLM Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.2-vllm-inference)
 - **For configuration tuning**: See [Configuration System](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.3-configuration-system)
 - **For prompt examples**: See [Working with Prompts](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.4-working-with-prompts)
 - **For output processing**: See [Understanding Output](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.5-understanding-output)
