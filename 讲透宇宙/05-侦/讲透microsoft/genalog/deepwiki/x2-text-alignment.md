<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/genalog · extra page Text Alignment · fetched 2026-10-26 -->

# Text Alignment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [genalog/text/alignment.py](genalog/text/alignment.py)
- [genalog/text/anchor.py](genalog/text/anchor.py)
- [genalog/text/ner_label.py](genalog/text/ner_label.py)

</details>



This document covers the text alignment algorithms implemented in genalog for aligning ground truth text with OCR output text. The alignment functionality enables comparison and analysis of OCR accuracy by establishing character-level and token-level correspondences between clean and noisy text versions.

For information about NER label propagation that uses text alignment, see [NER Label Propagation](#2.3.2). For broader text processing utilities, see [Text Processing](#2.3).

## Algorithm Overview

The genalog text alignment system provides two primary alignment strategies:

1. **Global Sequence Alignment**: Direct implementation using the Needleman-Wunsch algorithm via Bio.pairwise2
2. **Anchor-based Alignment**: Fast alignment scheme for longer documents using the RETAS approach

Both algorithms produce aligned text pairs where gaps are inserted to maintain character-level correspondence between ground truth and OCR text.

### Core Alignment Flow

```mermaid
graph TD
    A["Ground Truth Text"] --> B["tokenize()"]
    C["OCR Text"] --> D["tokenize()"]
    B --> E["align() or align_w_anchor()"]
    D --> E
    E --> F["Aligned GT String"]
    E --> G["Aligned OCR String"]
    F --> H["parse_alignment()"]
    G --> H
    H --> I["Token Mappings"]
    H --> J["Character Correspondences"]
```

Sources: [genalog/text/alignment.py:149-194](), [genalog/text/anchor.py:232-309]()

## Needleman-Wunsch Global Alignment

The core alignment algorithm implements global sequence alignment using the Needleman-Wunsch dynamic programming approach through the Bio.pairwise2 library.

### Alignment Configuration

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `MATCH_REWARD` | 1 | Reward for matching characters |
| `MISMATCH_PENALTY` | -0.5 | Penalty for character substitutions |
| `GAP_PENALTY` | -0.5 | Penalty for insertions/deletions |
| `GAP_EXT_PENALTY` | -0.5 | Penalty for extending gaps |
| `SPACE_MISMATCH_PENALTY` | 0.1 | Additional penalty for space mismatches |
| `GAP_CHAR` | "@" | Character used to represent gaps |

Sources: [genalog/text/alignment.py:12-20]()

### Alignment Algorithm Implementation

```mermaid
graph TB
    A["align(gt, noise, gap_char)"] --> B["tokenize(gt)"]
    A --> C["tokenize(noise)"]
    B --> D["_align_seg(gt, noise)"]
    C --> D
    D --> E["pairwise2.align.globalcs()"]
    E --> F["_select_alignment_candidates()"]
    F --> G["Aligned GT, Aligned OCR"]
    
    H["_align_seg()"] --> I["match_reward_fn()"]
    H --> J["Unicode Support<br/>(char list conversion)"]
    I --> K["Bio.pairwise2<br/>Needleman-Wunsch"]
    J --> K
    K --> L["_join_char_list()"]
```

The `align()` function in [genalog/text/alignment.py:149-194]() serves as the main entry point, ensuring that:
- Input validation handles empty strings appropriately
- Token count invariants are maintained between input and output
- Multiple alignment candidates are filtered to preserve ground truth token count

Sources: [genalog/text/alignment.py:28-86](), [genalog/text/alignment.py:88-147]()

## Fast Alignment with Anchors

For longer documents where O(N²) complexity becomes prohibitive, the anchor-based alignment scheme provides significant performance improvements by breaking text into smaller segments.

### RETAS Algorithm Implementation

```mermaid
graph TD
    A["align_w_anchor(gt, ocr)"] --> B["tokenize(gt, ocr)"]
    B --> C["find_anchor_recur()"]
    C --> D["get_anchor_map()"]
    D --> E["get_unique_words()"]
    E --> F["LCS(unique_words_gt, unique_words_ocr)"]
    F --> G["Anchor Points"]
    G --> H["Split into Segments"]
    H --> I["align() on each segment"]
    I --> J["Concatenate Results"]
    
    K["get_anchor_map()"] --> L["Counter(tokens)"]
    L --> M["unique_words.intersection()"]
    M --> N["get_word_map()"]
    N --> O["LCS.get_str()"]
```

The anchor-based approach uses the following strategy:

1. **Unique Word Identification**: Extract words that appear only once in each text
2. **Common Anchor Detection**: Find unique words present in both ground truth and OCR text
3. **LCS-based Filtering**: Use Longest Common Subsequence to identify reliable anchor points
4. **Recursive Segmentation**: Split long segments recursively until manageable sizes
5. **Segment Alignment**: Apply standard Needleman-Wunsch to each segment pair

Sources: [genalog/text/anchor.py:84-154](), [genalog/text/anchor.py:157-229](), [genalog/text/anchor.py:232-309]()

### Anchor Selection Criteria

```mermaid
graph LR
    A["All Tokens"] --> B["get_unique_words()"]
    B --> C["Counter < 2"]
    C --> D["Case Insensitive Filtering"]
    D --> E["Intersection GT ∩ OCR"]
    E --> F["LCS Filtering"]
    F --> G["Final Anchor Set"]
    
    H["Segment Length Check"] --> I["segment_len() > MAX_ALIGN_SEGMENT_LENGTH"]
    I --> J["find_anchor_recur()"]
    J --> K["Recursive Subdivision"]
```

Sources: [genalog/text/anchor.py:33-51](), [genalog/text/anchor.py:53-62]()

## Alignment Parsing and Token Mapping

After alignment, the `parse_alignment()` function converts character-level alignments into token-level mappings that support downstream applications like NER label propagation.

### Token Mapping Generation

```mermaid
graph TD
    A["parse_alignment(aligned_gt, aligned_noise)"] --> B["tokenize(aligned_gt)"]
    A --> C["tokenize(aligned_noise)"]
    B --> D["Token Boundary Detection"]
    C --> D
    D --> E["_find_next_token()"]
    E --> F["_is_valid_token()"]
    F --> G["Mapping Construction"]
    G --> H["gt_to_noise_mapping"]
    G --> I["noise_to_gt_mapping"]
    
    J["Token Relationships"] --> K["One-to-One"]
    J --> L["One-to-Many"]
    J --> M["Many-to-One"]
    J --> N["Many-to-Many"]
    J --> O["Missing Tokens"]
```

The parsing algorithm handles five distinct token relationship patterns:

1. **One-to-One**: Single GT token aligns to single OCR token
2. **One-to-Many**: Single GT token splits into multiple OCR tokens  
3. **Many-to-One**: Multiple GT tokens merge into single OCR token
4. **Many-to-Many**: Complex relationships requiring careful mapping
5. **Missing Tokens**: GT or OCR tokens with no correspondence

Sources: [genalog/text/alignment.py:322-471](), [genalog/text/alignment.py:224-297]()

### Token Validation and Gap Handling

```mermaid
graph LR
    A["_is_valid_token(token, gap_char)"] --> B["INVALID_TOKEN_REGEX"]
    B --> C["Match Gap Patterns"]
    C --> D["^\s*@*\s*$"]
    D --> E["Empty Strings"]
    E --> F["Whitespace Only"]
    F --> G["Valid Token Boolean"]
    
    H["Gap Character Selection"] --> I["GAP_CHAR_SET"]
    I --> J["Exclude SPECIAL_CHAR"]
    J --> K["Input Character Set"]
    K --> L["Set Difference"]
    L --> M["Available Gap Characters"]
```

The token validation ensures alignment integrity by identifying invalid tokens composed entirely of gap characters, whitespace, or empty strings. The gap character selection mechanism automatically chooses suitable gap characters that don't conflict with input text characters.

Sources: [genalog/text/alignment.py:299-320](), [genalog/text/ner_label.py:169-188]()

## Integration with NER Label Propagation

The alignment functionality serves as the foundation for NER label propagation, where named entity labels from clean ground truth text are transferred to corresponding OCR tokens.

### Alignment-Based Label Transfer

```mermaid
graph TD
    A["propagate_label_to_ocr()"] --> B["preprocess.join_tokens()"]
    B --> C["align_w_anchor() or align()"]
    C --> D["parse_alignment()"]
    D --> E["gt_to_ocr_mapping"]
    D --> F["ocr_to_gt_mapping"]
    E --> G["Label Propagation Logic"]
    F --> G
    G --> H["correct_ner_labels()"]
    H --> I["Corrected OCR Labels"]
    
    J["Label Relationship Handling"] --> K["B-Label Splitting"]
    J --> L["I-Label Correction"]
    J --> M["Missing Label Detection"]
```

The label propagation process leverages both mapping directions to handle complex multi-token entity scenarios where entity boundaries may shift between ground truth and OCR text.

Sources: [genalog/text/ner_label.py:190-237](), [genalog/text/ner_label.py:239-431]()

## Performance Characteristics

### Algorithm Complexity Comparison

| Algorithm | Time Complexity | Space Complexity | Best Use Case |
|-----------|----------------|------------------|---------------|
| `align()` | O(N²) | O(N²) | Short text segments (< 100 chars) |
| `align_w_anchor()` | O(N log N) typical | O(N) | Long documents, books, articles |

### Configuration Constants

The alignment behavior can be tuned through several configuration parameters defined in [genalog/text/alignment.py:12-20]():

- **MAX_ALIGN_SEGMENT_LENGTH**: 100 characters - threshold for triggering anchor-based segmentation
- **Scoring Parameters**: Control alignment quality vs. gap insertion tradeoffs
- **Gap Character Handling**: Automatic selection from printable ASCII excluding whitespace

Sources: [genalog/text/anchor.py:30](), [genalog/text/alignment.py:12-20]()

---

