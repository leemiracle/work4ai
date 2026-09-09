> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/7-prompt-engineering](https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/7-prompt-engineering)
> DeepWiki deepseek-ai/DeepSeek-OCR-2

# Prompt Engineering

  Relevant source files 
 - [DeepSeek-OCR2-master/DeepSeek-OCR2-vllm/config.py](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-vllm/config.py)
 - [README.md](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1)
 
  This page documents the prompt engineering system for DeepSeek-OCR-2, which uses special control tokens and task-specific templates to direct model behavior at inference time. The system enables a single model to perform diverse OCR tasks through declarative prompt specifications rather than task-specific fine-tuning.

 For information about the underlying vision processing that responds to these prompts, see [Dynamic Resolution System](https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/6-dynamic-resolution-system). For implementation details of the model's inference methods, see [Transformers Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/3.1-transformers-inference) and [vLLM Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/3.2-vllm-inference).

 
---

 
## System Overview

 DeepSeek-OCR-2 uses a prompt-based control system where the model's behavior is determined by the combination of special tokens and natural language instructions in the input prompt. The system supports three primary control tokens that modify model processing:

 
| Token | Purpose | Effect |
|---|---|---|
| <image> | Visual input placeholder | Replaced with 256-1120 visual tokens based on image complexity |
| `< | grounding | >` |
| `< | ref | >...< |

 Sources: [README.md134-142](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L134-L142) [DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py17-18](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py#L17-L18)

 
### Prompt Processing Flow

 The following diagram shows how prompts are processed from user input to model execution:

 
```

```

 Sources: [README.md134-142](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L134-L142) [DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py17-25](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py#L17-L25)

 
---

 
## Special Tokens

 
### `<image>` Token

 The `<image>` token marks the position where visual embeddings will be inserted into the prompt. This token is replaced during preprocessing with variable-length visual embeddings.

 **Token Replacement Process:**

 
 - **Detection**: The tokenizer identifies `<image>` tokens in the input prompt
 - **Image Processing**: The image undergoes multi-crop processing (see [Global and Local Views](https://deepwiki.com/deepseek-ai/DeepSeek-OCR-2/6.2-global-and-local-views))
 - **Token Calculation**: System calculates exact token count: 
 - Base image (1024×1024): 256 tokens
 - Local crops (0-6 at 768×768): 144 tokens each
 - Total range: 256-1120 tokens
 - **Embedding Replacement**: Single `<image>` token replaced with actual visual embeddings
 
 **Key Parameters:**

 
| Parameter | Default | Description |
|---|---|---|
| base_size | 1024 | Base image resolution for global view |
| image_size | 768 | Resolution for local crop tiles |
| crop_mode | True | Enable/disable multi-crop processing |

 **Example Usage:**

 
```

```

 Sources: [README.md118-124](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L118-L124) [DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py17-25](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py#L17-L25)

 
### `<|grounding|>` Token

 The `<|grounding|>` token enables spatial awareness mode, allowing the model to predict coordinates and produce structured outputs with layout information.

 **Effects of Grounding Mode:**

 
 - **Coordinate Prediction**: Model can output bounding box coordinates
 - **Structured Output**: Enables markdown with layout preservation
 - **Spatial Relationships**: Better understanding of document structure
 - **Layout Awareness**: Maintains reading order and spatial hierarchy
 
 **When to Use:**

 
 - **Use `<|grounding|>`** for:

 
 - Document-to-markdown conversion
 - Structured OCR with layout preservation
 - Tasks requiring spatial coordinates
 - Document understanding with positional information
 - **Omit `<|grounding|>`** for:

 
 - Layout-free text extraction
 - General image description
 - Figure parsing (when layout is not critical)
 - Simple text recognition without coordinates
 
 **Example Comparison:**

 
```

```

 Sources: [README.md119-138](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L119-L138)

 
### `<|ref|>...<|/ref|>` Token Pair

 The `<|ref|>...<|/ref|>` token pair wraps reference text for localization tasks. The model searches for the specified text in the image and returns its location.

 **Usage Pattern:**

 
```

```

 **Output Format:**

 The model returns bounding box coordinates or location descriptions for the referenced text.

 **Use Cases:**

 
 - Finding specific text strings in documents
 - Locating keywords or phrases
 - Text-based region extraction
 - Document navigation by content
 
 Sources: [README.md141](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L141-L141)

 
---

 
## Task-Specific Prompts

 The following table provides production-ready prompt templates for common OCR tasks. These templates combine special tokens with natural language instructions to achieve specific behaviors.

 
### Prompt Template Reference

 
| Task | Prompt Template | Special Tokens | Output Type |
|---|---|---|---|
| Document to Markdown | `\n< | grounding | >Convert the document to markdown.` |
| General OCR | `\n< | grounding | >OCR this image.` |
| Layout-Free OCR | <image>\nFree OCR. | <image> | Plain text without layout |
| Figure Parsing | <image>\nParse the figure. | <image> | Figure description and data |
| Image Description | <image>\nDescribe this image in detail. | <image> | Detailed image description |
| Text Localization | `\nLocate < | ref | >text< |

 Sources: [README.md134-142](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L134-L142)

 
### Task Flow Diagram

 The following diagram maps task types to their prompt patterns and code entry points:

 
```

```

 Sources: [README.md86-142](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L86-L142) [DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py17-25](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py#L17-L25)

 
---

 
## Document-to-Markdown Conversion

 This is the primary use case for structured document processing. The prompt enables full layout preservation and markdown formatting.

 **Prompt Template:**

 
```

```

 **Configuration:**

 
```

```

 **Output Characteristics:**

 
 - Preserves document structure (headings, paragraphs, lists)
 - Maintains table formatting
 - Captures text hierarchy
 - Includes spatial layout information
 - Produces valid markdown syntax
 
 Sources: [README.md119-136](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L119-L136) [DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py18-25](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py#L18-L25)

 
---

 
## General OCR with Layout

 For general images requiring OCR with spatial awareness.

 **Prompt Template:**

 
```

```

 **Use Cases:**

 
 - Natural scene text recognition
 - Mixed content images
 - Images with complex layouts
 - When coordinate information is needed
 
 **Differences from Document Conversion:**

 
 - Less structured than markdown output
 - May not follow strict markdown syntax
 - Better for non-document images
 - Still maintains spatial relationships
 
 Sources: [README.md137](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L137-L137)

 
---

 
## Layout-Free OCR

 For extracting text without preserving spatial layout or structure.

 **Prompt Template:**

 
```

```

 **Configuration:**

 
```

```

 **Characteristics:**

 
 - No `<|grounding|>` token
 - Plain text output
 - No coordinate information
 - No layout preservation
 - Faster processing (no spatial computations)
 - Reading order may vary
 
 **When to Use:**

 
 - Simple text extraction needs
 - When layout is not important
 - When processing speed is critical
 - For text-only applications
 
 Sources: [README.md118-138](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L118-L138)

 
---

 
## Figure Parsing

 Specialized prompt for extracting information from figures, charts, and diagrams.

 **Prompt Template:**

 
```

```

 **Output Content:**

 
 - Figure type identification
 - Data extraction from charts/graphs
 - Legend interpretation
 - Axis labels and values
 - Visual element descriptions
 
 **Best For:**

 
 - Scientific figures
 - Charts and graphs
 - Diagrams with labels
 - Infographics
 
 Sources: [README.md139](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L139-L139)

 
---

 
## Image Description

 General-purpose visual understanding without OCR focus.

 **Prompt Template:**

 
```

```

 **Output Characteristics:**

 
 - Comprehensive visual description
 - Scene understanding
 - Object detection and relationships
 - May include text if present
 - Natural language narrative
 
 **Differences from OCR:**

 
 - Focus on visual content, not text extraction
 - Describes what is seen, not transcribing text
 - Useful for accessibility or content understanding
 - Can complement OCR tasks
 
 Sources: [README.md140](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L140-L140)

 
---

 
## Text Localization

 Finding and locating specific text strings within images.

 **Prompt Template:**

 
```

```

 **Example:**

 
```

```

 **Output Format:**

 The model returns bounding box coordinates or location descriptions:

 
 - Top-left and bottom-right coordinates
 - Relative position descriptions
 - Multiple locations if text appears multiple times
 
 **Use Cases:**

 
 - Document navigation
 - Keyword search in images
 - Form field location
 - Template matching
 
 Sources: [README.md141](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L141-L141)

 
---

 
## Code Integration Examples

 
### Transformers Backend Integration

 The following example shows complete prompt usage with the Transformers backend:

 
```

```

 Sources: [DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py1-25](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py#L1-L25)

 
### vLLM Backend Prompt Usage

 For vLLM inference, prompts are configured in the entry point scripts. The configuration parameters affect how the `<image>` token is processed:

 **Configuration in `config.py`:**

 
```

```

 **Usage in entry scripts:**

 The vLLM scripts (`run_dpsk_ocr2_image.py`, `run_dpsk_ocr2_pdf.py`, `run_dpsk_ocr2_eval_batch.py`) use prompts internally based on the task type. The `<image>` token replacement happens automatically through the `DeepseekOCR2MultiModalProcessor` class.

 Sources: [README.md86-103](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L86-L103)

 
---

 
## Prompt Engineering Best Practices

 
### Token Order

 The standard token order is:

 
 - `<image>` - Always first
 - Line break (`\n`)
 - Optional: `<|grounding|>` - If spatial awareness needed
 - Task instruction
 - Optional: `<|ref|>...<|/ref|>` - For localization
 
 **Correct:**

 
```

```

 **Incorrect:**

 
```

```

 
### Natural Language Instructions

 After the special tokens, use clear, concise natural language:

 **Effective Instructions:**

 
 - `Convert the document to markdown.`
 - `OCR this image.`
 - `Parse the figure.`
 - `Describe this image in detail.`
 
 **Less Effective:**

 
 - Overly verbose instructions
 - Ambiguous phrasing
 - Multiple conflicting requests
 
 
### Token Combination Rules

 
| Combination | Valid | Use Case |
|---|---|---|
| <image> only | ✓ | Layout-free tasks, descriptions |
| <image> + `< | grounding | >` |
| <image> + `< | ref | >` |
| `< | grounding | >+< |
| `< | grounding | >` only |
| `< | ref | >` only |

 
### Processing Parameters

 The prompt works in conjunction with processing parameters:

 
```

```

 Sources: [DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py25](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py#L25-L25)

 
---

 
## Prompt-to-Code Mapping

 The following diagram shows how prompts map to internal processing code:

 
```

```

 Sources: [DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py1-25](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py#L1-L25) [README.md118-124](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L118-L124)

 
---

 
## Summary

 DeepSeek-OCR-2's prompt engineering system provides:

 
 - **Three special tokens** (`<image>`, `<|grounding|>`, `<|ref|>...<|/ref|>`) for control
 - **Six primary task templates** covering document conversion, OCR, figure parsing, description, and localization
 - **Unified architecture** where behavior is controlled by prompts, not model architecture
 - **Dynamic token expansion** where `<image>` becomes 256-1120 visual tokens
 - **Declarative task specification** through natural language instructions
 
 The system's strength lies in its simplicity: developers specify tasks through clear prompts rather than managing multiple models or complex configuration. This approach enables rapid prototyping and easy adaptation to new OCR tasks without retraining.

 Sources: [README.md134-142](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/README.md?plain=1#L134-L142) [DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py1-25](https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/2f3699eb/DeepSeek-OCR2-master/DeepSeek-OCR2-hf/run_dpsk_ocr2.py#L1-L25)
