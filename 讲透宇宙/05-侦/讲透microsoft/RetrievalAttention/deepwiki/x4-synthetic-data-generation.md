<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RetrievalAttention · extra page Synthetic Data Generation · fetched 2026-10-26 -->

# Synthetic Data Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmark/ruler/data/synthetic/common_words_extraction.py](benchmark/ruler/data/synthetic/common_words_extraction.py)
- [benchmark/ruler/data/synthetic/niah.py](benchmark/ruler/data/synthetic/niah.py)
- [benchmark/ruler/data/synthetic/variable_tracking.py](benchmark/ruler/data/synthetic/variable_tracking.py)

</details>



This document describes the synthetic data generation system used by the RULER benchmark to create test datasets for long-context language model evaluation. The system generates three types of synthetic tasks: Needle in a Haystack (NIAH), Variable Tracking (VT), and Common Words Extraction (CWE).

For information about running these benchmarks, see [RULER Benchmark](#3.1). For evaluation metrics and scoring, see [Metrics and Scoring](#3.2.1).

## System Overview

The synthetic data generation system consists of three main components, each designed to test different aspects of long-context understanding:

```mermaid
graph TB
    subgraph "Synthetic Data Generation System"
        NIAH[niah.py<br/>"Needle in Haystack"]
        VT[variable_tracking.py<br/>"Variable Tracking"]  
        CWE[common_words_extraction.py<br/>"Common Words Extraction"]
    end
    
    subgraph "Shared Components"
        TOK[select_tokenizer<br/>"Tokenizer Interface"]
        UTILS[dump_jsonl<br/>"Output Utilities"]
        TEMPLATE[template<br/>"Prompt Templates"]
    end
    
    subgraph "Task-Specific Resources"
        ESSAY[PaulGrahamEssays.json<br/>"Haystack Content"]
        WORDS[wonderwords<br/>"Word Lists"]
        CONST[constants.py<br/>"Task Definitions"]
    end
    
    subgraph "Output Format"
        JSONL[validation.jsonl<br/>"Test Dataset"]
    end
    
    NIAH --> TOK
    VT --> TOK
    CWE --> TOK
    
    NIAH --> UTILS
    VT --> UTILS
    CWE --> UTILS
    
    NIAH --> ESSAY
    CWE --> WORDS
    VT --> CONST
    
    NIAH --> JSONL
    VT --> JSONL
    CWE --> JSONL
```

Sources: [benchmark/ruler/data/synthetic/niah.py:1-273](), [benchmark/ruler/data/synthetic/variable_tracking.py:1-207](), [benchmark/ruler/data/synthetic/common_words_extraction.py:1-167]()

## Data Generation Components

### Needle in a Haystack (NIAH)

The NIAH generator creates tasks where models must find specific information embedded in long contexts. The system supports multiple needle types and insertion strategies:

```mermaid
graph LR
    subgraph "NIAH Generation Pipeline"
        INPUT[generate_input_output<br/>"Main Generation Function"]
        NEEDLE[generate_random<br/>"Needle Creation"]
        HAYSTACK[haystack<br/>"Context Generation"]
        INSERTION[insertion_positions<br/>"Needle Placement"]
    end
    
    subgraph "Needle Types"
        NUMBERS[generate_random_number<br/>"7-digit Numbers"]
        WORDS[generate_random_word<br/>"Compound Words"]
        UUIDS[generate_random_uuid<br/>"UUID4 Strings"]
    end
    
    subgraph "Haystack Types"
        ESSAY_TYPE[essay<br/>"Paul Graham Essays"]
        REPEAT_TYPE[repeat<br/>"Repeated Sentences"]
        NEEDLE_TYPE[needle<br/>"Needle-only Content"]
    end
    
    INPUT --> NEEDLE
    INPUT --> HAYSTACK
    INPUT --> INSERTION
    
    NEEDLE --> NUMBERS
    NEEDLE --> WORDS
    NEEDLE --> UUIDS
    
    HAYSTACK --> ESSAY_TYPE
    HAYSTACK --> REPEAT_TYPE
    HAYSTACK --> NEEDLE_TYPE
```

Sources: [benchmark/ruler/data/synthetic/niah.py:126-196](), [benchmark/ruler/data/synthetic/niah.py:104-124](), [benchmark/ruler/data/synthetic/niah.py:78-90]()

The needle format follows a structured template:
- Template: `"One of the special magic {type_needle_v} for {key} is: {value}."`
- Keys and values are generated based on `type_needle_k` and `type_needle_v` parameters
- Multiple needles can be inserted at different depths using `DEPTHS` array

### Variable Tracking (VT)

The VT generator creates chains of variable assignments that models must track through noisy contexts:

```mermaid
graph TB
    subgraph "Variable Tracking Generation"
        CHAINS[generate_chains<br/>"Chain Generation"]
        NOISE[noise<br/>"Distractor Content"]
        MERGE[sentences<br/>"Context Assembly"]
    end
    
    subgraph "Chain Structure"
        INIT[VAR_XXX_=_number<br/>"Initial Assignment"]
        HOPS[VAR_YYY_=_VAR_XXX<br/>"Variable Hops"]
        QUERY[query<br/>"Target Value"]
    end
    
    subgraph "Context Assembly"
        POSITIONS[positions<br/>"Random Insertion"]
        CONTEXT[context<br/>"Final Context"]
        TEMPLATE_FORMAT[template.format<br/>"Question Template"]
    end
    
    CHAINS --> INIT
    CHAINS --> HOPS
    INIT --> QUERY
    
    CHAINS --> MERGE
    NOISE --> MERGE
    MERGE --> POSITIONS
    POSITIONS --> CONTEXT
    CONTEXT --> TEMPLATE_FORMAT
```

Sources: [benchmark/ruler/data/synthetic/variable_tracking.py:67-86](), [benchmark/ruler/data/synthetic/variable_tracking.py:87-127]()

The system generates variable chains with:
- Variables: 5-character uppercase strings (e.g., `"ABCDE"`)
- Initial values: Random 5-digit numbers (10000-99999)
- Chain length: Configurable via `num_hops` parameter
- Multiple chains: Configurable via `num_chains` parameter

### Common Words Extraction (CWE)

The CWE generator creates tasks where models must identify the most frequently occurring words in lists:

```mermaid
graph LR
    subgraph "CWE Generation Process"
        WORDS_INIT[words<br/>"Word Pool Creation"]
        SAMPLE[word_list_full<br/>"Word Sampling"]
        FREQ[word_list<br/>"Frequency Assignment"]
        FORMAT[context<br/>"List Formatting"]
    end
    
    subgraph "Word Sources"
        NOUNS[nounlist.txt<br/>"Noun Dictionary"]
        ADJS[adjectivelist.txt<br/>"Adjective Dictionary"]
        VERBS[verblist.txt<br/>"Verb Dictionary"]
    end
    
    subgraph "Frequency Configuration"
        COMMON[common_repeats<br/>"Common Word Frequency"]
        UNCOMMON[uncommon_repeats<br/>"Uncommon Word Frequency"]
        NUM_COMMON[common_nums<br/>"Number of Common Words"]
    end
    
    NOUNS --> WORDS_INIT
    ADJS --> WORDS_INIT
    VERBS --> WORDS_INIT
    
    WORDS_INIT --> SAMPLE
    SAMPLE --> FREQ
    
    COMMON --> FREQ
    UNCOMMON --> FREQ
    NUM_COMMON --> FREQ
    
    FREQ --> FORMAT
```

Sources: [benchmark/ruler/data/synthetic/common_words_extraction.py:65-81](), [benchmark/ruler/data/synthetic/common_words_extraction.py:72-81]()

The word list is formatted as numbered entries: `"1. word1 2. word2 3. word3 ..."`

## Common Generation Patterns

### Token Length Management

All generators use a common pattern for managing sequence length constraints:

```mermaid
graph TB
    subgraph "Length Management System"
        INIT[num_items<br/>"Initial Item Count"]
        LOOP[while_loop<br/>"Iterative Testing"]
        TOKENIZE[TOKENIZER.text_to_tokens<br/>"Token Counting"]
        CHECK[length_check<br/>"Length Validation"]
    end
    
    subgraph "Parameters"
        MAX_SEQ[max_seq_length<br/>"Maximum Sequence Length"]
        TOKENS_GEN[tokens_to_generate<br/>"Generation Buffer"]
        INCREMENTAL[incremental<br/>"Step Size"]
    end
    
    INIT --> LOOP
    LOOP --> TOKENIZE
    TOKENIZE --> CHECK
    CHECK --> MAX_SEQ
    CHECK --> TOKENS_GEN
    
    CHECK --> LOOP
    LOOP --> INCREMENTAL
```

Sources: [benchmark/ruler/data/synthetic/niah.py:199-230](), [benchmark/ruler/data/synthetic/variable_tracking.py:130-156](), [benchmark/ruler/data/synthetic/common_words_extraction.py:105-128]()

### Template System

All generators use a template-based approach for question formatting:

| Component | Purpose | Example |
|-----------|---------|---------|
| `{context}` | Long context content | Essay text, word lists, variable chains |
| `{query}` | Specific question target | Needle key, variable value, word count |
| `{type_needle_v}` | Task-specific type | `"numbers"`, `"words"`, `"uuids"` |

The template system handles singular/plural forms automatically in NIAH tasks [benchmark/ruler/data/synthetic/niah.py:183-188]().

## Configuration Parameters

### Common Parameters

| Parameter | Type | Purpose | Default |
|-----------|------|---------|---------|
| `max_seq_length` | int | Maximum sequence length | Required |
| `tokens_to_generate` | int | Generation buffer size | Required |
| `num_samples` | int | Number of samples to generate | Required |
| `random_seed` | int | Reproducibility seed | 42 |
| `template` | str | Question template | Task-specific |

### Task-Specific Parameters

**NIAH Parameters:**
- `num_needle_k`: Number of needle keys
- `num_needle_v`: Number of needle values per key
- `type_needle_k`: Key type (`"numbers"`, `"words"`, `"uuids"`)
- `type_needle_v`: Value type (`"numbers"`, `"words"`, `"uuids"`)
- `type_haystack`: Haystack type (`"essay"`, `"repeat"`, `"needle"`)

**VT Parameters:**
- `num_chains`: Number of variable chains
- `num_hops`: Number of hops per chain
- `add_fewshot`: Include few-shot examples

**CWE Parameters:**
- `freq_cw`: Common word frequency
- `freq_ucw`: Uncommon word frequency  
- `num_cw`: Number of common words

Sources: [benchmark/ruler/data/synthetic/niah.py:48-69](), [benchmark/ruler/data/synthetic/variable_tracking.py:43-58](), [benchmark/ruler/data/synthetic/common_words_extraction.py:42-57]()

## Output Format

All generators produce JSONL files with a consistent schema:

```mermaid
graph LR
    subgraph "JSONL Output Schema"
        RECORD["{<br/>record<br/>}"]
        INDEX[index<br/>"Sample Number"]
        INPUT[input<br/>"Question + Context"]
        OUTPUTS[outputs<br/>"Expected Answers"]
        LENGTH[length<br/>"Token Count"]
    end
    
    subgraph "File Structure"
        SAVE_DIR[save_dir<br/>"Output Directory"]
        SAVE_NAME[save_name<br/>"Task Name"]
        SUBSET[subset<br/>"validation|test"]
        JSONL_FILE[subset.jsonl<br/>"Final Output"]
    end
    
    RECORD --> INDEX
    RECORD --> INPUT
    RECORD --> OUTPUTS
    RECORD --> LENGTH
    
    SAVE_DIR --> JSONL_FILE
    SAVE_NAME --> JSONL_FILE
    SUBSET --> JSONL_FILE
    
    RECORD --> JSONL_FILE
```

Sources: [benchmark/ruler/data/synthetic/niah.py:249-255](), [benchmark/ruler/data/synthetic/variable_tracking.py:178-184](), [benchmark/ruler/data/synthetic/common_words_extraction.py:146-152]()

The output path follows the pattern: `{save_dir}/{save_name}/{subset}.jsonl`

Each record contains:
- `index`: Sequential sample number
- `input`: Complete prompt with context and question
- `outputs`: Expected answer(s) as list or string
- `length`: Total token count including generation buffer

---

