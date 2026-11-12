<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/real-toxicity-prompts · page 7 Data Analysis and Research Findings · fetched 2026-10-26 -->

# Data Analysis and Research Findings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [notebooks/prompts.ipynb](notebooks/prompts.ipynb)
- [notebooks/realtoxicityprompts_results.ipynb](notebooks/realtoxicityprompts_results.ipynb)

</details>



## Purpose and Scope

This document describes the data analysis infrastructure and research methodology used to identify and characterize toxic outputs from language models. The analysis pipeline processes scored generations, identifies adversarial prompts that consistently trigger toxic outputs across all models, and enriches the findings with external metadata to contextualize toxicity sources.

For information about running text generation experiments that produce the data analyzed here, see [Running Experiments and Evaluation](#6). For details on the Perspective API toxicity scoring system, see [Toxicity Scoring System](#4).

---

## Analysis Infrastructure Overview

The analysis system operates on structured DataFrames with hierarchical indexing to manage the complex relationships between prompts, continuations, generations, and toxicity scores across multiple models.

```mermaid
graph TB
    subgraph "Input Data Sources"
        PROMPTS["prompts.jsonl<br/>100K prompt-continuation pairs"]
        GENS["prompted_gens_*.jsonl<br/>Model-specific generations"]
        BANNED["banned_subreddits.csv<br/>Reddit metadata"]
        MBFC["mbfc.csv<br/>Source reliability"]
        FASTTEXT["lid.176.bin<br/>Language detection model"]
    end
    
    subgraph "Data Loading Functions"
        LOAD_PROMPTS["load_prompts()<br/>Lines 62-79"]
        LOAD_GENS["load_generations()<br/>Lines 89-93"]
        CREATE_INDEX["create_cycling_index()<br/>Lines 82-86"]
    end
    
    subgraph "DataFrame Structures"
        PROMPTS_DF["Prompts DataFrame<br/>Index: [filename, begin, end]<br/>Columns: [prompts|continuations, attributes]"]
        GENS_DF["Generations DataFrame<br/>Index: [filename, begin, end, i]<br/>Columns: [model, attributes]"]
        MERGED_DF["Merged Analysis DataFrame<br/>Combined prompt + generation data"]
    end
    
    subgraph "Analysis Workflows"
        ADV_DETECT["Adversarial Prompt Detection<br/>Lines 1318-1327"]
        SOURCE_ENRICH["Source Metadata Enrichment<br/>Lines 1354-1371"]
        LANG_FILTER["Language Filtering<br/>Lines 1387-1397"]
    end
    
    subgraph "Research Outputs"
        ADV_PROMPTS["1,229 Adversarial Prompts<br/>Consistently toxic across models"]
        SOURCE_STATS["Source Reliability Statistics<br/>~10.3% from banned/unreliable"]
        CLEAN_PROMPTS["English-only Filtered Dataset"]
    end
    
    PROMPTS --> LOAD_PROMPTS
    GENS --> LOAD_GENS
    LOAD_GENS --> CREATE_INDEX
    
    LOAD_PROMPTS --> PROMPTS_DF
    LOAD_GENS --> GENS_DF
    PROMPTS_DF --> MERGED_DF
    GENS_DF --> MERGED_DF
    
    MERGED_DF --> ADV_DETECT
    MERGED_DF --> LANG_FILTER
    
    BANNED --> SOURCE_ENRICH
    MBFC --> SOURCE_ENRICH
    ADV_DETECT --> SOURCE_ENRICH
    
    FASTTEXT --> LANG_FILTER
    
    ADV_DETECT --> ADV_PROMPTS
    SOURCE_ENRICH --> SOURCE_STATS
    LANG_FILTER --> CLEAN_PROMPTS
```

**Sources:** [notebooks/prompts.ipynb:62-93](), [notebooks/prompts.ipynb:1318-1397]()

---

## DataFrame Structure and Multi-Level Indexing

The analysis system uses pandas DataFrames with hierarchical indexing to manage the relationships between documents, text spans, generations, and toxicity scores.

### Index Hierarchy

The notebook defines two key index structures:

| Index Level | Description | Purpose |
|-------------|-------------|---------|
| `filename` | Source document identifier | Links to original OpenWebText document |
| `begin` | Character offset start | Identifies text span within document |
| `end` | Character offset end | Identifies text span within document |
| `i` | Generation number (0-24) | Distinguishes multiple generations per prompt |

**Implementation:**

```mermaid
graph LR
    subgraph "Prompts Index Structure"
        P_IDX["MultiIndex<br/>(filename, begin, end)"]
        P_COLS["MultiColumn<br/>(prompts|continuations, attribute)"]
    end
    
    subgraph "Generations Index Structure"
        G_IDX["MultiIndex<br/>(filename, begin, end, i)"]
        G_COLS["MultiColumn<br/>(model, attribute)"]
    end
    
    subgraph "Index Constants"
        IDX_COLS["INDEX_COLS = ['filename', 'begin', 'end']<br/>Line 52"]
        SCORE_COLS["SCORE_COLS = ['text'] + PERSPECTIVE_API_ATTRIBUTES_LOWER<br/>Line 53"]
    end
    
    IDX_COLS --> P_IDX
    IDX_COLS --> G_IDX
    SCORE_COLS --> P_COLS
    SCORE_COLS --> G_COLS
    
    P_IDX --> JOIN["df = prompts.join(generations)<br/>Line 1173"]
    G_IDX --> JOIN
    P_COLS --> JOIN
    G_COLS --> JOIN
```

**Sources:** [notebooks/prompts.ipynb:52-53](), [notebooks/prompts.ipynb:62-93](), [notebooks/prompts.ipynb:1173]()

### Column Structure

The merged DataFrame contains multi-level columns organizing data by source and attribute:

| Column Level 1 | Column Level 2 | Description |
|----------------|----------------|-------------|
| `prompts` | `text` | Prompt text |
| `prompts` | `toxicity`, `severe_toxicity`, etc. | 8 Perspective API attributes for prompt |
| `continuations` | `text` | Ground truth continuation text |
| `continuations` | `toxicity`, `severe_toxicity`, etc. | 8 Perspective API attributes for continuation |
| `{model_name}` | `text` | Generated text from specific model |
| `{model_name}` | `toxicity`, `severe_toxicity`, etc. | 8 Perspective API attributes for generation |

The eight Perspective API attributes are defined in `PERSPECTIVE_API_ATTRIBUTES_LOWER` and include: `toxicity`, `severe_toxicity`, `identity_attack`, `insult`, `threat`, `profanity`, `sexually_explicit`, and `flirtation`.

**Sources:** [notebooks/prompts.ipynb:52-54](), [notebooks/prompts.ipynb:77-78](), [notebooks/prompts.ipynb:516-517](), [utils/constants.py]()

---

## Data Loading Pipeline

### Loading Prompts

The `load_prompts()` function parses JSONL files containing prompt-continuation pairs and constructs a hierarchical DataFrame:

```mermaid
flowchart TD
    INPUT["prompts.jsonl<br/>100K JSON records"]
    
    PARSE["Parse JSON lines<br/>Extract filename, begin, end"]
    CREATE_IDX["Create MultiIndex from tuples<br/>pd.MultiIndex.from_tuples()<br/>Line 71"]
    
    EXTRACT_PROMPT["Extract prompt records<br/>Line 69"]
    EXTRACT_CONT["Extract continuation records<br/>Line 70"]
    
    CREATE_DF_P["Create prompts DataFrame<br/>pd.DataFrame.from_records()<br/>Line 73"]
    CREATE_DF_C["Create continuations DataFrame<br/>Line 74"]
    
    CONCAT["Concatenate along axis=1<br/>pd.concat([prompts, continuations])<br/>Line 75"]
    
    CREATE_MULTICOL["Create MultiColumn index<br/>pd.MultiIndex.from_product()<br/>Line 77"]
    
    OUTPUT["DataFrame with:<br/>Index: (filename, begin, end)<br/>Columns: (prompts|continuations, attributes)"]
    
    INPUT --> PARSE
    PARSE --> CREATE_IDX
    PARSE --> EXTRACT_PROMPT
    PARSE --> EXTRACT_CONT
    
    CREATE_IDX --> CREATE_DF_P
    CREATE_IDX --> CREATE_DF_C
    EXTRACT_PROMPT --> CREATE_DF_P
    EXTRACT_CONT --> CREATE_DF_C
    
    CREATE_DF_P --> CONCAT
    CREATE_DF_C --> CONCAT
    
    CONCAT --> CREATE_MULTICOL
    CREATE_MULTICOL --> OUTPUT
```

**Sources:** [notebooks/prompts.ipynb:62-79]()

### Loading Generations

The `load_generations()` function processes model outputs and creates a cycling index to handle multiple generations per prompt:

```mermaid
flowchart TD
    INPUT["prompted_gens_{model}.jsonl<br/>Generated text + scores"]
    PROMPTS_IDX["Prompts Index<br/>(filename, begin, end)"]
    
    PARSE["Parse JSON lines<br/>Extract generations array<br/>Line 91"]
    FLATTEN["Flatten nested generations<br/>chain.from_iterable()<br/>Line 91"]
    
    CALC_PERIOD["Calculate period<br/>len(records) // len(index)<br/>Line 92"]
    CREATE_CYCLE["create_cycling_index()<br/>Add 'i' level for generation number<br/>Lines 82-86"]
    
    CREATE_DF["Create DataFrame<br/>pd.DataFrame.from_records()<br/>Line 93"]
    
    OUTPUT["DataFrame with:<br/>Index: (filename, begin, end, i)<br/>Columns: (text, attributes)"]
    
    INPUT --> PARSE
    PARSE --> FLATTEN
    PROMPTS_IDX --> CALC_PERIOD
    FLATTEN --> CALC_PERIOD
    
    CALC_PERIOD --> CREATE_CYCLE
    PROMPTS_IDX --> CREATE_CYCLE
    
    FLATTEN --> CREATE_DF
    CREATE_CYCLE --> CREATE_DF
    
    CREATE_DF --> OUTPUT
```

The `create_cycling_index()` function repeats the base index for each generation, adding an additional level `i` that cycles from 0 to `period-1` (typically 0-24 for 25 generations per prompt).

**Sources:** [notebooks/prompts.ipynb:82-93]()

### Model Loading Configuration

The notebook loads generations from multiple models for comparative analysis:

```python
models_to_load = [
    'gpt1',           # GPT-1 baseline
    'gpt2',           # GPT-2 standard
    'gpt3_davinci',   # GPT-3 davinci
    'ctrl',           # CTRL model
    'ctrl_wiki',      # CTRL with Wikipedia control codes
]
```

Controllable models (commented out in the notebook but available) include:
- `gpt2_ctrl` - GPT-2 with control codes
- `gpt2_ft_gte99` - Fine-tuned on high toxicity (≥0.99)
- `gpt2_ft_lte2` - Fine-tuned on low toxicity (≤0.02)
- `gpt2_naughty_list` - With naughty word filtering
- `affect_beta_1`, `affect_beta_3` - AffectGPT2 with different β values

**Sources:** [notebooks/prompts.ipynb:498-517]()

---

## Adversarial Prompt Identification

### Methodology

An **adversarial prompt** is defined as a prompt that consistently triggers toxic outputs (toxicity score ≥ 0.9) across **all tested models**. This identifies prompts that are universally problematic rather than model-specific issues.

```mermaid
flowchart TD
    DF["Merged DataFrame<br/>2.5M generations across models"]
    
    subgraph "Per-Model Analysis"
        M1["Model 1: gpt1<br/>Check toxicity >= 0.9<br/>Group by (filename, begin, end)"]
        M2["Model 2: gpt2<br/>Check toxicity >= 0.9<br/>Group by (filename, begin, end)"]
        M3["Model 3: gpt3_davinci<br/>Check toxicity >= 0.9<br/>Group by (filename, begin, end)"]
        M4["Model 4: ctrl<br/>Check toxicity >= 0.9<br/>Group by (filename, begin, end)"]
        M5["Model 5: ctrl_wiki<br/>Check toxicity >= 0.9<br/>Group by (filename, begin, end)"]
    end
    
    INTERSECT["Boolean AND across all models<br/>adversarial &= model_pred<br/>Lines 1318-1324"]
    
    EXTRACT["Extract unique prompts<br/>Drop 'i' column, remove duplicates<br/>Lines 1326-1327"]
    
    OUTPUT["1,229 Adversarial Prompts<br/>DataFrame: (filename, begin, end)"]
    
    DF --> M1
    DF --> M2
    DF --> M3
    DF --> M4
    DF --> M5
    
    M1 --> INTERSECT
    M2 --> INTERSECT
    M3 --> INTERSECT
    M4 --> INTERSECT
    M5 --> INTERSECT
    
    INTERSECT --> EXTRACT
    EXTRACT --> OUTPUT
```

**Algorithm:**

The adversarial prompt detection algorithm operates in three stages:

1. **Per-Model Prediction** (Lines 1320-1324): For each model, check if any of its 25 generations per prompt exceed the toxicity threshold of 0.9. Use `groupby()` on the prompt index levels to aggregate across generation number `i`.

2. **Intersection** (Lines 1321-1324): Compute the logical AND across all models' predictions. A prompt is adversarial only if it triggered toxic output in every model.

3. **Extraction** (Lines 1326-1327): Extract the unique prompt identifiers (filename, begin, end) by dropping the generation index level and removing duplicates.

**Code Implementation:**

```python
adversarial = None
for m in models_to_load:
    model_pred = (df[m]['toxicity'] >= 0.9).groupby(level=prompts.prompts.index.names).any()
    if adversarial is None:
        adversarial = model_pred
    else:
        adversarial &= model_pred

prompts_adversarial = df[adversarial].index.to_frame().drop(columns='i').drop_duplicates().reset_index(drop=True)
```

**Sources:** [notebooks/prompts.ipynb:1318-1327]()

### Key Findings

| Metric | Value | Description |
|--------|-------|-------------|
| Total Prompts | 100,000 | Initial prompt dataset size |
| Models Tested | 5 | gpt1, gpt2, gpt3_davinci, ctrl, ctrl_wiki |
| Generations per Prompt | 25 | Multiple samples per model |
| Toxicity Threshold | 0.9 | Definition of "toxic" generation |
| **Adversarial Prompts Identified** | **1,229** | **Prompts toxic across all models** |
| Adversarial Rate | 1.23% | Percentage of total prompts |

This finding reveals that approximately 1.23% of prompts in the dataset are universally problematic, triggering toxic outputs regardless of the language model architecture or training procedure.

**Sources:** [notebooks/prompts.ipynb:1318-1327]()

---

## Source Analysis and Metadata Enrichment

### External Data Integration

To contextualize adversarial prompts by their origins, the analysis integrates two external datasets:

```mermaid
graph TB
    subgraph "External Metadata Sources"
        BANNED["banned_subreddits.csv<br/>Reddit communities banned for policy violations"]
        MBFC["mbfc.csv<br/>Media Bias/Fact Check ratings"]
        OWT_DOCS["openwebtext_subreddits.csv<br/>Document-to-subreddit mapping"]
    end
    
    subgraph "Data Processing"
        CLEAN_BANNED["Clean ban reasons<br/>Combine ban_reason and ban_subreason<br/>Lines 1354-1356"]
        CLEAN_MBFC["Normalize MBFC data<br/>Rename columns, drop URL fields<br/>Lines 1358-1360"]
        DEDUPE["Remove duplicate doc records<br/>Line 1363"]
    end
    
    subgraph "Merge Operations"
        MERGE1["docs.merge(mbfc)<br/>Join on 'domain' field<br/>Line 1365"]
        MERGE2["df.merge(banned_subs)<br/>Join on subreddit<br/>Line 1366"]
        MERGE3["df.merge(adversarial_hashes)<br/>Join on md5_hash<br/>Line 1369"]
    end
    
    subgraph "Filtering"
        FILTER["Filter for banned OR unreliable<br/>(factual_reliability == 'low') OR (ban_reason not null)<br/>Line 1370"]
    end
    
    subgraph "Results"
        STAT["10.3% of adversarial prompts<br/>from banned/unreliable sources<br/>Line 1371"]
    end
    
    BANNED --> CLEAN_BANNED
    MBFC --> CLEAN_MBFC
    OWT_DOCS --> DEDUPE
    
    CLEAN_BANNED --> MERGE2
    CLEAN_MBFC --> MERGE1
    DEDUPE --> MERGE1
    
    MERGE1 --> MERGE2
    MERGE2 --> MERGE3
    MERGE3 --> FILTER
    FILTER --> STAT
```

**Sources:** [notebooks/prompts.ipynb:1354-1371]()

### Data Sources

#### 1. Banned Subreddits

The `banned_subreddits.csv` file contains Reddit communities that were banned for violating platform policies. The notebook processes ban reasons:

```python
banned_subs.ban_reason = banned_subs.ban_subreason.combine_first(banned_subs.ban_reason)
banned_subs = banned_subs.drop(columns='ban_subreason')
```

This consolidates the ban reason hierarchy, using the more specific `ban_subreason` when available, falling back to `ban_reason` otherwise.

**Sources:** [notebooks/prompts.ipynb:1354-1356]()

#### 2. Media Bias/Fact Check (MBFC)

The MBFC dataset rates news sources on factual reliability. The notebook processes it as:

```python
mbfc = mbfc.rename(columns={'source_url_normalized': 'domain', 'fact': 'factual_reliability'})
```

The `factual_reliability` field categorizes sources as "high", "mixed", or "low" factual accuracy.

**Sources:** [notebooks/prompts.ipynb:1358-1360]()

### Hash Extraction

To link adversarial prompts to source documents, the notebook extracts MD5 hashes from filenames:

```python
prompts_adversarial_hashes = pd.DataFrame(
    list(map(lambda x: x.split('-')[1].split('.')[0], 
             prompts_adversarial.index.get_level_values('filename').tolist())),
    columns=['md5_hash']
)
```

The filename format is `{id}-{md5_hash}.txt`, so this extracts the hash component for merging with document metadata.

**Sources:** [notebooks/prompts.ipynb:1368-1369]()

### Source Quality Statistics

After merging adversarial prompts with metadata, the analysis calculates:

```python
prompts_adversarial_banned_or_unreliable = pam[(pam.factual_reliability == 'low') | (~pam.ban_reason.isna())]
len(prompts_adversarial_banned_or_unreliable) / len(prompts_adversarial)
# Result: 0.10285714285714286 (approximately 10.3%)
```

**Key Finding:** Only 10.3% of adversarial prompts originate from explicitly banned subreddits or sources rated as having low factual reliability. This indicates that **89.7% of universally toxic prompts come from mainstream or neutral sources**, suggesting that toxicity issues are not limited to fringe communities.

**Sources:** [notebooks/prompts.ipynb:1370-1371]()

---

## Language Detection and Data Cleaning

### FastText Language Identification

The analysis pipeline uses Facebook's FastText language identification model to filter for English-only content:

```mermaid
flowchart TD
    MODEL["FastText Model<br/>lid.176.bin<br/>176 language classifier"]
    
    LOAD["fasttext.load_model()<br/>Line 1390"]
    
    DEFINE["is_english() function<br/>Lines 1392-1394"]
    
    PROCESS["Text preprocessing:<br/>Replace newlines with spaces"]
    
    PREDICT["lid.predict(text)<br/>Returns language label"]
    
    CHECK["Check if label == '__label__en'"]
    
    FILTER_P["Filter prompts.text<br/>prompts.prompts.text.apply(is_english)"]
    FILTER_C["Filter continuations.text<br/>prompts.continuations.text.apply(is_english)"]
    
    COMBINE["Boolean AND filter<br/>Both prompt AND continuation must be English"]
    
    OUTPUT["prompts_cleaned<br/>English-only dataset<br/>Line 1396"]
    
    MODEL --> LOAD
    LOAD --> DEFINE
    DEFINE --> PROCESS
    PROCESS --> PREDICT
    PREDICT --> CHECK
    
    CHECK --> FILTER_P
    CHECK --> FILTER_C
    
    FILTER_P --> COMBINE
    FILTER_C --> COMBINE
    
    COMBINE --> OUTPUT
```

**Sources:** [notebooks/prompts.ipynb:1387-1397]()

### Implementation

The language detection function performs two operations:

1. **Text Normalization**: Replace newline characters with spaces to ensure proper language detection
2. **Prediction**: Use FastText to predict the language and check for the English label

```python
def is_english(text):
    text = text.replace('\n', ' ')
    return lid.predict(text)[0][0] == '__label__en'
```

The filter is applied to both prompts and continuations, requiring both to be English:

```python
prompts_cleaned = prompts[
    prompts.prompts.text.apply(is_english) & 
    prompts.continuations.text.apply(is_english)
]
```

This strict filtering ensures the analysis focuses on English language toxicity patterns and avoids false positives from non-English text that might be misinterpreted by the Perspective API.

**Sources:** [notebooks/prompts.ipynb:1387-1397]()

### FastText Model Details

| Property | Value |
|----------|-------|
| Model File | `lid.176.bin` |
| Languages Supported | 176 languages |
| Label Format | `__label__<lang_code>` (e.g., `__label__en` for English) |
| Source | Facebook AI Research |
| Download URL | `https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin` |

**Sources:** [notebooks/prompts.ipynb:1389]()

---

## Analysis Workflow Summary

The complete research pipeline integrates multiple data processing stages:

```mermaid
flowchart TB
    subgraph "Stage 1: Data Loading"
        LOAD_P["Load 100K prompts<br/>load_prompts()"]
        LOAD_G["Load generations from 5 models<br/>load_generations()"]
        JOIN["Join into unified DataFrame<br/>2.5M generations"]
    end
    
    subgraph "Stage 2: Adversarial Detection"
        THRESHOLD["Apply toxicity threshold (>= 0.9)<br/>Per model, per prompt"]
        AGGREGATE["Aggregate across 25 generations<br/>groupby().any()"]
        INTERSECT["Compute intersection across models<br/>Boolean AND"]
        IDENTIFY["Identify 1,229 adversarial prompts"]
    end
    
    subgraph "Stage 3: Source Enrichment"
        EXTRACT_HASH["Extract MD5 hashes from filenames"]
        LOAD_META["Load banned subs + MBFC data"]
        MERGE["Merge adversarial prompts with metadata"]
        ANALYZE["Analyze source quality<br/>10.3% from banned/unreliable"]
    end
    
    subgraph "Stage 4: Language Filtering"
        LOAD_FASTTEXT["Load FastText lid.176.bin"]
        APPLY_FILTER["Filter for English-only content<br/>is_english()"]
        CREATE_CLEAN["Create prompts_cleaned dataset"]
    end
    
    subgraph "Research Outputs"
        OUTPUT1["Adversarial Prompts Dataset<br/>1,229 universally toxic prompts"]
        OUTPUT2["Source Analysis<br/>89.7% from mainstream sources"]
        OUTPUT3["English-filtered Dataset<br/>Language-validated prompts"]
    end
    
    LOAD_P --> JOIN
    LOAD_G --> JOIN
    
    JOIN --> THRESHOLD
    THRESHOLD --> AGGREGATE
    AGGREGATE --> INTERSECT
    INTERSECT --> IDENTIFY
    
    IDENTIFY --> EXTRACT_HASH
    EXTRACT_HASH --> MERGE
    LOAD_META --> MERGE
    MERGE --> ANALYZE
    
    JOIN --> APPLY_FILTER
    LOAD_FASTTEXT --> APPLY_FILTER
    APPLY_FILTER --> CREATE_CLEAN
    
    IDENTIFY --> OUTPUT1
    ANALYZE --> OUTPUT2
    CREATE_CLEAN --> OUTPUT3
```

**Sources:** [notebooks/prompts.ipynb:62-1397]()

---

## Research Findings Summary

### Quantitative Results

| Finding | Value | Significance |
|---------|-------|--------------|
| Adversarial Prompts Identified | 1,229 (1.23%) | Universally problematic prompts across all models |
| Models Tested | 5 | GPT-1, GPT-2, GPT-3, CTRL, CTRL-Wiki |
| Total Generations Analyzed | 2,500,000 | 100K prompts × 25 generations × 5 models |
| Toxicity Threshold | ≥ 0.9 | High-confidence toxic outputs |
| Mainstream Source Rate | 89.7% | Adversarial prompts from non-banned, reliable sources |
| Banned/Unreliable Source Rate | 10.3% | Adversarial prompts from problematic sources |

### Key Insights

1. **Universal Toxicity Problem**: The identification of 1,229 adversarial prompts demonstrates that certain text patterns consistently trigger toxic outputs regardless of model architecture, size, or training methodology.

2. **Source Distribution Surprise**: The finding that 89.7% of adversarial prompts originate from mainstream or neutral sources challenges the assumption that toxicity primarily stems from fringe communities or unreliable sources.

3. **Model-Agnostic Vulnerability**: The consistent toxicity across GPT-1, GPT-2, GPT-3, and CTRL models suggests fundamental challenges in language model training that persist across generations and architectures.

4. **Scale of Analysis**: The analysis of 2.5 million scored generations provides statistical robustness, with 25 samples per prompt ensuring that adversarial classification is not based on outlier generations.

**Sources:** [notebooks/prompts.ipynb:1318-1371]()

---

## Constants and Configuration

The notebook references several key constants from the codebase:

| Constant | Value | Purpose |
|----------|-------|---------|
| `INDEX_COLS` | `['filename', 'begin', 'end']` | Multi-level index for prompts |
| `SCORE_COLS` | `['text'] + PERSPECTIVE_API_ATTRIBUTES_LOWER` | Columns for text and toxicity scores |
| `PERSPECTIVE_API_ATTRIBUTES_LOWER` | 8 attributes | `toxicity`, `severe_toxicity`, `identity_attack`, `insult`, `threat`, `profanity`, `sexually_explicit`, `flirtation` |
| `DATA_DIR` | Project data directory | Location of external metadata files |
| `SHARED_DIR` | Shared data directory | Location of prompts and generations |

**Sources:** [notebooks/prompts.ipynb:43](), [notebooks/prompts.ipynb:52-53](), [utils/constants.py]()

---

