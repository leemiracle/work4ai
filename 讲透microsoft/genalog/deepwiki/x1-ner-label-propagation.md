<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/genalog · extra page NER Label Propagation · fetched 2026-10-26 -->

# NER Label Propagation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [genalog/ocr/metrics.py](genalog/ocr/metrics.py)
- [genalog/text/alignment.py](genalog/text/alignment.py)
- [genalog/text/conll_format.py](genalog/text/conll_format.py)
- [genalog/text/ner_label.py](genalog/text/ner_label.py)

</details>



## Purpose and Scope

This document covers the Named Entity Recognition (NER) label propagation system in genalog, which transfers NER labels from clean ground truth text to OCR'd text containing recognition errors. This process is essential for creating labeled training datasets that enable robust NER models to handle real-world OCR noise.

For information about the underlying text alignment algorithms, see [Text Alignment](#2.3.1). For broader text processing utilities, see [Text Processing](#2.3).

## Overview

NER label propagation solves a critical challenge in synthetic dataset generation: when clean text with NER labels is processed through document generation and OCR, the resulting text contains errors that misalign with the original labels. The propagation system uses sequence alignment to map tokens between clean and OCR'd text, then transfers labels while handling complex cases like token splitting, merging, and missing tokens.

**Core Process Flow**

```mermaid
graph TD
    A["gt_labels: ['B-PLACE', 'I-PLACE', 'O']"] --> D[propagate_label_to_ocr]
    B["gt_tokens: ['New', 'York', 'is']"] --> D
    C["ocr_tokens: ['N', 'ewYork', 'is']"] --> D
    
    D --> E[_find_gap_char_candidates]
    E --> F[align_w_anchor or alignment.align]
    F --> G[alignment.parse_alignment]
    G --> H[Label Propagation Step 1]
    H --> I[Label Propagation Step 2a: Fix Trailing B-labels]
    I --> J[Label Propagation Step 2b: correct_ner_labels]
    J --> K["ocr_labels: ['B-PLACE', 'I-PLACE', 'O']"]
    K --> L["aligned_gt: 'N@ew York is'"]
    L --> M["aligned_ocr: 'N ew@York is'"]
```

Sources: [genalog/text/ner_label.py:190-431]()

## Core Algorithm Implementation

The main entry point `propagate_label_to_ocr()` handles gap character selection and delegates to the core implementation `_propagate_label_to_ocr()`. The algorithm operates in three phases:

### Phase 1: Text Alignment and Mapping

```mermaid
graph LR
    A[gt_tokens] --> B[preprocess.join_tokens]
    C[ocr_tokens] --> D[preprocess.join_tokens]
    B --> E[gt_txt]
    D --> F[ocr_txt]
    E --> G[align_w_anchor or alignment.align]
    F --> G
    G --> H[aligned_gt]
    G --> I[aligned_ocr]
    H --> J[alignment.parse_alignment]
    I --> J
    J --> K[gt_to_ocr_mapping]
    J --> L[ocr_to_gt_mapping]
```

The system first reconstructs full text strings from token lists, performs sequence alignment using either the anchor-based method or standard Needleman-Wunsch algorithm, then parses the alignment to create bidirectional token mappings.

Sources: [genalog/text/ner_label.py:384-402]()

### Phase 2: Naive Label Propagation

```mermaid
graph TD
    A[ocr_to_gt_mapping] --> B["for each OCR token mapping"]
    B --> C{"mapping empty?"}
    C -->|Yes| D["No label (missing token)"]
    C -->|No| E[_select_from_multiple_ner_labels]
    E --> F["Use first GT token's label"]
    F --> G[Append to ocr_labels]
    D --> G
```

For each OCR token, the system looks up which ground truth tokens it maps to. If multiple ground truth tokens map to one OCR token, `_select_from_multiple_ner_labels()` selects the first token's label as the representative.

Sources: [genalog/text/ner_label.py:405-414](), [genalog/text/ner_label.py:140-167]()

### Phase 3: Multi-Token Label Correction

The system addresses two critical issues with multi-token NER labels (B-LABEL, I-LABEL sequences):

**Step 2a: Trailing B-label Correction**
When one ground truth token splits into multiple OCR tokens, all OCR tokens initially receive the same label. For B-labels, only the first OCR token should keep the B-label; subsequent tokens should be converted to I-labels.

**Step 2b: Missing B-label Correction**
The `correct_ner_labels()` function scans for I-labels that lack proper B-label prefixes and converts them to B-labels when necessary.

Sources: [genalog/text/ner_label.py:416-428](), [genalog/text/ner_label.py:113-137]()

## Label Types and Conversion Functions

The system handles standard IOB (Inside-Outside-Begin) tagging with specific regex patterns and conversion utilities:

| Function | Purpose | Pattern |
|----------|---------|---------|
| `_is_begin_label()` | Identifies B-labels | `^\s*(B-)([a-z\|A-Z]+)\s*$` |
| `_is_inside_label()` | Identifies I-labels | `^\s*(I-)([a-z\|A-Z]+)\s*$` |
| `_convert_to_begin_label()` | I-label → B-label | Replace `I-` with `B-` |
| `_convert_to_inside_label()` | B-label → I-label | Replace `B-` with `I-` |

```mermaid
graph LR
    A["I-PLACE"] --> B[_convert_to_begin_label]
    B --> C["B-PLACE"]
    D["B-PLACE"] --> E[_convert_to_inside_label]
    E --> F["I-PLACE"]
    
    G["I-PLACE"] --> H[_is_inside_label]
    H --> I["True"]
    J["B-PLACE"] --> K[_is_begin_label]
    K --> L["True"]
```

Sources: [genalog/text/ner_label.py:19-83]()

## Gap Character Management

The propagation system requires a gap character for sequence alignment that doesn't appear in the input text. The `_find_gap_char_candidates()` function ensures alignment integrity:

```mermaid
graph TD
    A[gt_tokens + ocr_tokens] --> B["Extract all characters: input_char_set"]
    C[GAP_CHAR_SET] --> D["Available gap characters"]
    B --> E[gap_char_set.difference]
    D --> E
    E --> F[gap_char_candidates]
    F --> G{"alignment.GAP_CHAR available?"}
    G -->|Yes| H["Use default '@'"]
    G -->|No| I["Use any available candidate"]
    H --> J[Return selected gap_char]
    I --> J
```

If no suitable gap characters exist, the system raises `GapCharError` indicating the input character set is too large.

Sources: [genalog/text/ner_label.py:169-236](), [genalog/text/ner_label.py:25-33]()

## Integration with Text Alignment

NER label propagation depends heavily on the text alignment infrastructure. The system supports two alignment strategies:

| Strategy | Function | Use Case |
|----------|----------|----------|
| Standard | `alignment.align()` | Small text segments (O(N²) complexity) |
| Anchor-based | `anchor.align_w_anchor()` | Longer texts with anchor points |

The `use_anchor` parameter in `propagate_label_to_ocr()` controls which alignment method is used, defaulting to the faster anchor-based approach.

Sources: [genalog/text/ner_label.py:388-393]()

## Complex Mapping Scenarios

The propagation system handles various alignment patterns between ground truth and OCR tokens:

**Case Analysis from Code Comments**

```mermaid
graph TB
    subgraph "Multi-Token Labels"
        A1["Case 1: one-to-many<br/>gt: 'New York'<br/>ocr: 'New Yo rk'<br/>labels: B-p → B-p I-p I-p"]
        A2["Case 2: many-to-one<br/>gt: 'New York'<br/>ocr: 'NewYork'<br/>labels: B-p I-p → B-p"]
        A3["Case 3: many-to-many<br/>gt: 'New York'<br/>ocr: 'N ew York'<br/>labels: B-p I-p → B-p I-p"]
        A4["Case 4: missing I-tokens<br/>gt: 'New York'<br/>ocr: 'New'<br/>labels: B-p I-p → B-p"]
        A5["Case 5: missing B-tokens<br/>gt: 'New York City'<br/>ocr: 'York City'<br/>labels: B-p I-p I-p → B-p I-p"]
    end
    
    subgraph "Single-Token Labels"
        B1["Case 1: one-to-many<br/>gt: 'something'<br/>ocr: 'so me thing'<br/>labels: O → O O O"]
        B2["Case 2: many-to-one<br/>gt: 'is big'<br/>ocr: 'isbig'<br/>labels: V O → V"]
        B3["Case 3: many-to-many<br/>gt: 'this is huge'<br/>ocr: 'th isi shuge'<br/>labels: O V W → O O V"]
        B4["Case 4: missing tokens<br/>gt: 'is big'<br/>ocr: 'is'<br/>labels: O O → O"]
    end
```

Sources: [genalog/text/ner_label.py:252-279]()

## Usage in Dataset Generation

The propagation system integrates with the broader genalog pipeline through `conll_format.py`, which processes entire datasets:

```mermaid
graph LR
    A[clean_labels_dir] --> B[propagate_labels_sentences_multiprocess]
    C[ocr_text_dir] --> B
    B --> D[propagate_labels_sentence_single_file]
    D --> E[propagate_labels_sentences]
    E --> F[ner_label.propagate_label_to_ocr]
    F --> G[CoNLL formatted output]
    
    H[ProcessPoolExecutor] --> I[Parallel processing]
    I --> D
```

The `propagate_labels_sentences()` function extends basic label propagation to handle sentence boundaries, ensuring that OCR text is properly segmented to match the original sentence structure.

Sources: [genalog/text/conll_format.py:61-158](), [genalog/text/conll_format.py:244-280]()

## Error Handling and Validation

The system includes comprehensive validation for input data integrity:

| Validation | Error Type | Description |
|------------|------------|-------------|
| Token count mismatch | `ValueError` | `gt_tokens` and `gt_labels` have different lengths |
| Non-atomic tokens | `ValueError` | Tokens contain spaces (not atomic) |
| Invalid tokens | `ValueError` | Empty strings or whitespace-only tokens |
| Gap character conflicts | `GapCharError` | Tokens contain the gap character |
| Alignment failures | `ValueError` | Alignment produces wrong token count |

Sources: [genalog/text/ner_label.py:365-383]()

## Display and Formatting Utilities

The module provides utilities for visualizing label propagation results:

- `format_labels()`: Aligns tokens and labels for display
- `format_label_propagation()`: Shows complete propagation results with optional alignment visualization
- `_format_alignment()`: Displays character-level alignment with match indicators

These functions support debugging and validation of the propagation process by making the token-to-label mappings visually apparent.

Sources: [genalog/text/ner_label.py:433-527]()

---

