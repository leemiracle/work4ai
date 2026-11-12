<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/open_asr_leaderboard · extra page Multilingual Evaluation · fetched 2026-10-26 -->

# Multilingual Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nemo_asr/run_eval_ml.py](nemo_asr/run_eval_ml.py)
- [nemo_asr/run_nemo_ml.sh](nemo_asr/run_nemo_ml.sh)
- [nemo_asr/run_parakeet.sh](nemo_asr/run_parakeet.sh)

</details>



## Purpose and Scope

This document describes the multilingual evaluation system for NeMo ASR models, which evaluates models across multiple languages using language-specific datasets and normalization rules. This system is specifically designed for multilingual ASR models that support transcription in languages beyond English.

For standard English-only evaluation of NeMo models, see [Standard NeMo Evaluation](#4.1.1). For other multilingual-capable frameworks like Whisper, see [Whisper Models](#4.2.1).

**Key Characteristics:**
- Evaluates models on `fleurs`, `mcv` (Mozilla Common Voice), and `mls` (Multilingual LibriSpeech) datasets
- Applies language-specific text normalization (English vs. multilingual)
- Handles model-specific parameters (e.g., Canary's `pnc` settings)
- Supports 20+ languages including German, French, Italian, Spanish, Portuguese, and others

---

## System Architecture

The multilingual evaluation system consists of two main components: an orchestration script that iterates through dataset-language combinations, and an evaluation script that performs language-aware transcription and normalization.

**Multilingual Evaluation Pipeline**

```mermaid
flowchart TB
    subgraph "Orchestration Layer"
        SHELL["run_nemo_ml.sh<br/>Shell Orchestration"]
        CONFIG["EVAL_DATASETS<br/>Associative Array"]
        LOOP["Nested Loops<br/>dataset × language"]
    end
    
    subgraph "Configuration Data"
        FLEURS["fleurs: en de fr it es pt<br/>(+17 more languages)"]
        MCV["mcv: en de es fr it<br/>(+8 more languages)"]
        MLS["mls: es fr it pt<br/>(+3 more languages)"]
    end
    
    subgraph "Evaluation Layer"
        EVAL["run_eval_ml.py<br/>Python Evaluation Script"]
        LANG_DETECT["Language Detection<br/>from config_name or arg"]
        CACHE["audio_cache/<br/>{config_name}/{split}/"]
    end
    
    subgraph "Model Layer"
        NEMO_MODEL["ASRModel<br/>NeMo Model Loading"]
        CANARY_CHECK["Canary Model Check<br/>pnc parameter logic"]
        TRANSCRIBE["asr_model.transcribe()<br/>with source_lang & target_lang"]
    end
    
    subgraph "Normalization Layer"
        NORM_SWITCH["Language Check<br/>LANGUAGE == 'en'?"]
        EN_NORM["data_utils.normalizer<br/>English Normalization"]
        ML_NORM["data_utils.ml_normalizer<br/>Multilingual Normalization"]
    end
    
    subgraph "Output Layer"
        MANIFEST["write_manifest()<br/>JSONL per language"]
        SCORE["eval_utils.score_results()<br/>Aggregate across languages"]
    end
    
    SHELL --> CONFIG
    CONFIG --> FLEURS
    CONFIG --> MCV
    CONFIG --> MLS
    CONFIG --> LOOP
    
    LOOP --> EVAL
    EVAL --> LANG_DETECT
    LANG_DETECT --> CACHE
    CACHE --> NEMO_MODEL
    
    NEMO_MODEL --> CANARY_CHECK
    CANARY_CHECK --> TRANSCRIBE
    
    TRANSCRIBE --> NORM_SWITCH
    NORM_SWITCH -->|"LANGUAGE == 'en'"| EN_NORM
    NORM_SWITCH -->|"LANGUAGE != 'en'"| ML_NORM
    
    EN_NORM --> MANIFEST
    ML_NORM --> MANIFEST
    MANIFEST --> SCORE
```

**Sources:** [nemo_asr/run_nemo_ml.sh:1-96](), [nemo_asr/run_eval_ml.py:1-264]()

---

## Dataset Configuration

The multilingual evaluation system uses an associative array to define which languages are evaluated for each dataset. This configuration allows flexible specification of dataset-language combinations.

**Dataset-Language Mapping**

```mermaid
graph TB
    subgraph "Dataset Registry"
        EVAL_DATASETS["EVAL_DATASETS<br/>Associative Array"]
    end
    
    subgraph "FLEURS Dataset"
        FLEURS_KEY["Key: 'fleurs'"]
        FLEURS_LANGS["Languages:<br/>en de fr it es pt<br/>(Configurable: cs da el hr hu lt lv<br/>mt nl pl pt ro ru sk sl sv uk)"]
    end
    
    subgraph "Mozilla Common Voice"
        MCV_KEY["Key: 'mcv'"]
        MCV_LANGS["Languages:<br/>en de es fr it<br/>(Configurable: et lv nl pt ru sl sv uk)"]
    end
    
    subgraph "Multilingual LibriSpeech"
        MLS_KEY["Key: 'mls'"]
        MLS_LANGS["Languages:<br/>es fr it pt<br/>(Configurable: nl pl)"]
    end
    
    subgraph "Generated Config Names"
        CONFIGS["Examples:<br/>fleurs_en, fleurs_de<br/>mcv_es, mcv_fr<br/>mls_it, mls_pt"]
    end
    
    EVAL_DATASETS --> FLEURS_KEY
    EVAL_DATASETS --> MCV_KEY
    EVAL_DATASETS --> MLS_KEY
    
    FLEURS_KEY --> FLEURS_LANGS
    MCV_KEY --> MCV_LANGS
    MLS_KEY --> MLS_LANGS
    
    FLEURS_LANGS --> CONFIGS
    MCV_LANGS --> CONFIGS
    MLS_LANGS --> CONFIGS
```

| Dataset | Active Languages | Additional Supported Languages |
|---------|------------------|-------------------------------|
| **fleurs** | en, de, fr, it, es, pt | cs, da, el, hr, hu, lt, lv, mt, nl, pl, ro, ru, sk, sl, sv, uk |
| **mcv** | en, de, es, fr, it | et, lv, nl, pt, ru, sl, sv, uk |
| **mls** | es, fr, it, pt | nl, pl |

**Configuration Format:**
- Config names follow the pattern: `{dataset}_{language_code}`
- Example: `fleurs_de` for German FLEURS, `mcv_es` for Spanish Common Voice
- Languages use ISO 639-1 two-letter codes

**Sources:** [nemo_asr/run_nemo_ml.sh:19-26]()

---

## Orchestration Pattern

The shell script orchestrates evaluations by iterating through all configured dataset-language combinations and invoking the Python evaluation script for each.

**Orchestration Flow**

```mermaid
flowchart TD
    START["Start run_nemo_ml.sh"]
    INIT["Initialize Variables<br/>MODEL_ID, BATCH_SIZE, DEVICE_ID"]
    DATASET_LOOP["For each dataset in EVAL_DATASETS"]
    LANG_LOOP["For each language in dataset languages"]
    
    subgraph "run_evaluation Function"
        BUILD_CONFIG["Build config_name<br/>{dataset}_{language}"]
        ECHO_INFO["Echo evaluation parameters<br/>Model, Dataset, Language, Device"]
        INVOKE_PYTHON["python run_eval_ml.py<br/>with --config_name, --language"]
        CHECK_EXIT["Check exit code"]
        LOG_RESULT["Log success or failure"]
    end
    
    ALL_DONE{"All combinations<br/>completed?"}
    SCORE["eval_utils.score_results()<br/>Aggregate all results"]
    END["End"]
    
    START --> INIT
    INIT --> DATASET_LOOP
    DATASET_LOOP --> LANG_LOOP
    LANG_LOOP --> BUILD_CONFIG
    BUILD_CONFIG --> ECHO_INFO
    ECHO_INFO --> INVOKE_PYTHON
    INVOKE_PYTHON --> CHECK_EXIT
    CHECK_EXIT --> LOG_RESULT
    LOG_RESULT --> ALL_DONE
    ALL_DONE -->|No| LANG_LOOP
    ALL_DONE -->|Yes| SCORE
    SCORE --> END
```

**Function: `run_evaluation()`**

The `run_evaluation` function encapsulates the invocation of a single evaluation run:

```
Parameters:
  - dataset: Dataset name (e.g., "fleurs", "mcv", "mls")
  - language: Two-letter language code (e.g., "de", "fr", "es")

Execution:
  1. Construct config_name = "{dataset}_{language}"
  2. Log evaluation parameters
  3. Invoke: python run_eval_ml.py \
       --model_id="$MODEL_ID" \
       --dataset="$DATASETS" \
       --config_name="$config_name" \
       --language="$language" \
       --split="test" \
       --device="$DEVICE_ID" \
       --batch_size="$BATCH_SIZE"
  4. Check exit code and log result
```

**Sources:** [nemo_asr/run_nemo_ml.sh:29-64](), [nemo_asr/run_nemo_ml.sh:74-86]()

---

## Language Detection and Processing

The evaluation script automatically detects the target language from the configuration name and applies language-specific processing throughout the pipeline.

**Language Detection Logic**

```mermaid
flowchart TD
    START["run_eval_ml.py execution"]
    CHECK_ARG["Check --language argument"]
    ARG_PROVIDED{"Argument<br/>provided?"}
    USE_ARG["LANGUAGE = args.language"]
    PARSE_CONFIG["Parse config_name<br/>Split on '_'"]
    EXTRACT["Extract language code<br/>from second part"]
    FALLBACK{"Extraction<br/>successful?"}
    USE_EXTRACTED["LANGUAGE = extracted code"]
    USE_DEFAULT["LANGUAGE = 'en'<br/>(default fallback)"]
    SET_CACHE["Set CACHE_DIR<br/>audio_cache/{config_name}/{split}"]
    
    START --> CHECK_ARG
    CHECK_ARG --> ARG_PROVIDED
    ARG_PROVIDED -->|Yes| USE_ARG
    ARG_PROVIDED -->|No| PARSE_CONFIG
    PARSE_CONFIG --> EXTRACT
    EXTRACT --> FALLBACK
    FALLBACK -->|Yes| USE_EXTRACTED
    FALLBACK -->|No| USE_DEFAULT
    USE_ARG --> SET_CACHE
    USE_EXTRACTED --> SET_CACHE
    USE_DEFAULT --> SET_CACHE
```

**Example Language Detection:**

| config_name | Explicit --language | Detected LANGUAGE |
|-------------|--------------------|--------------------|
| `fleurs_de` | None | `de` (extracted) |
| `mcv_es` | None | `es` (extracted) |
| `fleurs_fr` | `fr` | `fr` (from argument) |
| `invalid` | None | `en` (default fallback) |

**Sources:** [nemo_asr/run_eval_ml.py:26-35]()

---

## Model-Specific Transcription

Different multilingual models require different transcription parameters. The evaluation script handles model-specific logic, particularly for Canary models.

**Canary Model PNC Parameter Logic**

```mermaid
flowchart TD
    START["Check model ID"]
    IS_CANARY{"'canary' in<br/>model_id?"}
    NOT_CANARY["Use standard transcription<br/>asr_model.transcribe(audio_files)"]
    IS_V2{"'v2' in<br/>model_id?"}
    
    subgraph "Canary v1 & Flash"
        CHECK_LANG_V1{"LANGUAGE<br/>== 'en'?"}
        PNC_NOPNC["pnc = 'nopnc'<br/>No punctuation for English"]
        PNC_PNC["pnc = 'pnc'<br/>Punctuation for other languages"]
    end
    
    subgraph "Canary v2"
        PNC_YES["pnc = 'pnc'<br/>Punctuation for all languages"]
    end
    
    TRANSCRIBE_CANARY["asr_model.transcribe(<br/>audio_files,<br/>pnc=pnc,<br/>source_lang=LANGUAGE,<br/>target_lang=LANGUAGE)"]
    
    START --> IS_CANARY
    IS_CANARY -->|No| NOT_CANARY
    IS_CANARY -->|Yes| IS_V2
    IS_V2 -->|Yes| PNC_YES
    IS_V2 -->|No| CHECK_LANG_V1
    CHECK_LANG_V1 -->|Yes| PNC_NOPNC
    CHECK_LANG_V1 -->|No| PNC_PNC
    PNC_NOPNC --> TRANSCRIBE_CANARY
    PNC_PNC --> TRANSCRIBE_CANARY
    PNC_YES --> TRANSCRIBE_CANARY
```

**Model Version Differences:**

| Model Version | Language | `pnc` Parameter | Rationale |
|--------------|----------|-----------------|-----------|
| Canary-1b (v1) | English | `'nopnc'` | English evaluation without punctuation |
| Canary-1b (v1) | Other languages | `'pnc'` | Non-English with punctuation |
| Canary-1b-v2 | All languages | `'pnc'` | Unified punctuation handling |
| Canary-1b-flash | English | `'nopnc'` | Same as v1 |
| Canary-1b-flash | Other languages | `'pnc'` | Same as v1 |
| Other NeMo models | All languages | N/A | Parameter not applicable |

**Sources:** [nemo_asr/run_eval_ml.py:150-159]()

---

## Language-Specific Normalization

The critical difference in multilingual evaluation is the use of language-aware text normalization. English text uses a comprehensive normalizer with abbreviation expansion, while other languages use a basic multilingual normalizer.

**Normalization Decision Tree**

```mermaid
flowchart TD
    START["Transcription completed"]
    EXTRACT["Extract transcriptions<br/>Handle tuple if needed"]
    GET_REFS["Get references from dataset"]
    CHECK_LANG{"LANGUAGE<br/>== 'en'?"}
    
    subgraph "English Processing"
        EN_NORM_REF["Normalize references<br/>data_utils.normalizer(ref)"]
        EN_NORM_PRED["Normalize predictions<br/>data_utils.normalizer(pred.text)"]
        EN_FEATURES["Applied transformations:<br/>- British→American spelling (799 mappings)<br/>- Contractions expansion<br/>- Number spelling<br/>- Symbol removal<br/>- Lowercasing"]
    end
    
    subgraph "Multilingual Processing"
        ML_NORM_REF["Normalize references<br/>data_utils.ml_normalizer(ref)"]
        ML_NORM_PRED["Normalize predictions<br/>data_utils.ml_normalizer(pred.text)"]
        ML_FEATURES["Applied transformations:<br/>- Symbol removal<br/>- Diacritic handling<br/>- Whitespace normalization<br/>- Lowercasing"]
    end
    
    WER_CALC["Calculate WER<br/>wer_metric.compute()"]
    
    START --> EXTRACT
    EXTRACT --> GET_REFS
    GET_REFS --> CHECK_LANG
    CHECK_LANG -->|Yes| EN_NORM_REF
    EN_NORM_REF --> EN_NORM_PRED
    EN_NORM_PRED --> EN_FEATURES
    CHECK_LANG -->|No| ML_NORM_REF
    ML_NORM_REF --> ML_NORM_PRED
    ML_NORM_PRED --> ML_FEATURES
    EN_FEATURES --> WER_CALC
    ML_FEATURES --> WER_CALC
```

**Normalization Comparison:**

| Feature | English Normalizer | Multilingual Normalizer |
|---------|-------------------|------------------------|
| **Function** | `data_utils.normalizer()` | `data_utils.ml_normalizer()` |
| **Underlying Class** | `EnglishTextNormalizer` | `BasicMultilingualTextNormalizer` |
| **Abbreviations** | ✓ 799 British→American mappings | ✗ Not applicable |
| **Contractions** | ✓ "don't" → "do not" | ✗ Language-dependent |
| **Number Spelling** | ✓ "2" → "two" | ✗ Language-dependent |
| **Symbol Removal** | ✓ Comprehensive | ✓ Basic |
| **Diacritics** | ✓ Remove (English) | ✓ Preserve or normalize |
| **Whitespace** | ✓ Normalize | ✓ Normalize |

**Sources:** [nemo_asr/run_eval_ml.py:170-175]()

---

## Audio Processing and Caching

The multilingual evaluation system uses the same audio caching strategy as standard evaluation but organizes files by language-specific configuration names.

**Audio Cache Structure**

```mermaid
graph TB
    subgraph "Cache Root"
        ROOT["audio_cache/"]
    end
    
    subgraph "Configuration Directories"
        FLEURS_EN["fleurs_en/test/"]
        FLEURS_DE["fleurs_de/test/"]
        MCV_ES["mcv_es/test/"]
        MLS_FR["mls_fr/test/"]
    end
    
    subgraph "Audio Files"
        FILE1["fleurs_en_0_sample1.wav"]
        FILE2["fleurs_en_1_sample2.wav"]
        FILE3["fleurs_de_0_sample1.wav"]
        FILE4["mcv_es_0_sample1.wav"]
    end
    
    subgraph "Processing Pipeline"
        DOWNLOAD["download_audio_files()<br/>Batch processing function"]
        CHECK["Check if file exists"]
        WRITE["soundfile.write()<br/>Write float32 audio"]
        COLLECT["Collect paths and durations"]
        SORT["Sort by duration (descending)"]
    end
    
    ROOT --> FLEURS_EN
    ROOT --> FLEURS_DE
    ROOT --> MCV_ES
    ROOT --> MLS_FR
    
    FLEURS_EN --> FILE1
    FLEURS_EN --> FILE2
    FLEURS_DE --> FILE3
    MCV_ES --> FILE4
    
    DOWNLOAD --> CHECK
    CHECK --> WRITE
    WRITE --> COLLECT
    COLLECT --> SORT
```

**Cache Directory Pattern:**
- Path format: `audio_cache/{config_name}/{split}/`
- Example: `audio_cache/fleurs_de/test/`
- Filename format: `{config_name}_{index}_{original_basename}.wav`
- Example: `fleurs_de_0_sample1.wav`

**Audio Processing Steps:**

1. **Dataset Mapping** [nemo_asr/run_eval_ml.py:71-107]()
   - Map over dataset in batches
   - Process audio from `array` or `bytes` format
   - Generate unique filenames with config_name prefix

2. **File Writing** [nemo_asr/run_eval_ml.py:92-94]()
   - Check if file already exists (cache hit)
   - Write as float32 at native sample rate
   - Create directory structure if needed

3. **Duration Collection** [nemo_asr/run_eval_ml.py:98-101]()
   - Use dataset-provided duration if available
   - Otherwise calculate: `len(audio_array) / sample_rate`
   - Store for RTFx calculation

4. **Sorting** [nemo_asr/run_eval_ml.py:131-136]()
   - Sort samples by duration in descending order
   - Minimizes padding waste in batched inference
   - Improves GPU utilization

**Sources:** [nemo_asr/run_eval_ml.py:21-24](), [nemo_asr/run_eval_ml.py:71-107](), [nemo_asr/run_eval_ml.py:131-136]()

---

## Warmup and Timing

The evaluation script performs a warmup phase before measuring inference time, ensuring stable RTFx (Real-Time Factor) metrics.

**Warmup and Evaluation Sequence**

```mermaid
sequenceDiagram
    participant Script as run_eval_ml.py
    participant Model as asr_model
    participant Timer as time.time()
    participant Results as Metrics
    
    Note over Script: warmup_round = 0 (Warmup)
    Script->>Script: Select first 4 batches of audio
    Script->>Timer: start_time = time.time()
    Script->>Model: transcribe(audio_files[:batch_size*4])
    Model-->>Script: Warmup transcriptions
    Script->>Timer: end_time = time.time()
    Note over Script: Discard warmup time
    
    Note over Script: warmup_round = 1 (Full Evaluation)
    Script->>Script: Select all audio files
    Script->>Timer: start_time = time.time()
    Script->>Model: transcribe(all_audio_files)
    Model-->>Script: Full transcriptions
    Script->>Timer: end_time = time.time()
    Script->>Script: total_time = end_time - start_time
    Script->>Results: Calculate RTFx and WER
```

**Warmup Configuration:**

| Phase | Warmup Round | Audio Files | Time Recorded |
|-------|-------------|-------------|---------------|
| **Warmup** | 0 | First `batch_size * 4` samples | ✗ Discarded |
| **Full Evaluation** | 1 | All samples | ✓ Used for RTFx |

**RTFx Calculation:**
```
total_audio_length = sum(all_data["durations"])  # in seconds
rtfx = total_audio_length / total_time
avg_time_per_sample = total_time / len(audio_files)
```

The RTFx metric indicates how many times faster than real-time the model processes audio:
- RTFx = 10.0 means the model processes 10 seconds of audio in 1 second
- RTFx = 0.5 means the model processes 1 second of audio in 2 seconds

**Sources:** [nemo_asr/run_eval_ml.py:138-164](), [nemo_asr/run_eval_ml.py:177-199]()

---

## Command-Line Interface

The `run_eval_ml.py` script accepts several arguments to configure the evaluation process.

**Command-Line Arguments**

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--model_id` | str | ✓ | - | Model identifier (HuggingFace ID or .nemo path) |
| `--dataset` | str | ✗ | `"nithinraok/asr-leaderboard-datasets"` | HuggingFace dataset repository |
| `--config_name` | str | ✓ | - | Config in format `<dataset>_<lang>` (e.g., `fleurs_en`) |
| `--language` | str | ✗ | `None` | Explicit language code (extracted from config_name if not provided) |
| `--split` | str | ✗ | `"test"` | Dataset split to evaluate |
| `--device` | int | ✗ | `-1` | GPU device ID (-1 for CPU, 0+ for GPU) |
| `--batch_size` | int | ✗ | `32` | Number of samples per batch |
| `--max_eval_samples` | int | ✗ | `None` | Limit evaluation to N samples (for testing) |
| `--no-streaming` | flag | ✗ | `False` | Download full dataset instead of streaming |

**Usage Examples:**

```bash
# Evaluate Parakeet on German FLEURS
python run_eval_ml.py \
  --model_id="nvidia/parakeet-tdt-0.6b-v3" \
  --dataset="nithinraok/asr-leaderboard-datasets" \
  --config_name="fleurs_de" \
  --language="de" \
  --split="test" \
  --device=0 \
  --batch_size=64

# Evaluate Canary v2 on Spanish MLS
python run_eval_ml.py \
  --model_id="nvidia/canary-1b-v2" \
  --config_name="mls_es" \
  --device=0 \
  --batch_size=32

# Test run with limited samples
python run_eval_ml.py \
  --model_id="nvidia/parakeet-tdt-0.6b-v3" \
  --config_name="mcv_fr" \
  --device=0 \
  --batch_size=16 \
  --max_eval_samples=100
```

**Sources:** [nemo_asr/run_eval_ml.py:209-264]()

---

## Results Storage and Aggregation

The evaluation script writes per-language results to JSONL manifest files and then aggregates them across all languages for a final score.

**Result Storage Flow**

```mermaid
flowchart TD
    subgraph "Per-Language Evaluation"
        CALC_METRICS["Calculate WER and RTFx<br/>for current language"]
        WRITE_MANIFEST["data_utils.write_manifest()<br/>Write JSONL file"]
        MANIFEST_PATH["results/{model_hash}/{dataset}/{config_name}_{split}.jsonl"]
    end
    
    subgraph "Manifest File Structure"
        MANIFEST_FORMAT["Per-line JSON objects:<br/>{<br/> 'reference': str,<br/> 'prediction': str,<br/> 'audio_length': float,<br/> 'transcription_time': float,<br/> 'wer': float,<br/> 'rtfx': float<br/>}"]
    end
    
    subgraph "Final Aggregation"
        ALL_COMPLETE{"All dataset-language<br/>combinations done?"}
        AGGREGATE["eval_utils.score_results()<br/>Aggregate across all manifests"]
        FINAL_SCORES["Final WER and RTFx<br/>averaged across languages"]
    end
    
    CALC_METRICS --> WRITE_MANIFEST
    WRITE_MANIFEST --> MANIFEST_PATH
    MANIFEST_PATH --> MANIFEST_FORMAT
    MANIFEST_FORMAT --> ALL_COMPLETE
    ALL_COMPLETE -->|No| CALC_METRICS
    ALL_COMPLETE -->|Yes| AGGREGATE
    AGGREGATE --> FINAL_SCORES
```

**Example Directory Structure:**

```
results/
└── nvidia_parakeet-tdt-0.6b-v3_abc123/
    ├── nithinraok_asr-leaderboard-datasets/
    │   ├── fleurs_en_test.jsonl
    │   ├── fleurs_de_test.jsonl
    │   ├── fleurs_fr_test.jsonl
    │   ├── mcv_en_test.jsonl
    │   ├── mcv_de_test.jsonl
    │   ├── mcv_es_test.jsonl
    │   ├── mls_es_test.jsonl
    │   ├── mls_fr_test.jsonl
    │   └── mls_it_test.jsonl
    └── aggregated_scores.json
```

**Aggregation Process:**

The `eval_utils.score_results()` function is called after all language evaluations complete:

```bash
cd ../normalizer
python -c "import eval_utils; eval_utils.score_results('${RUNDIR}/results', '${MODEL_ID}')"
```

This function:
1. Scans all JSONL manifest files for the given model
2. Computes average WER across all language-dataset combinations
3. Computes average RTFx across all language-dataset combinations
4. Writes aggregated scores to a summary file
5. Enables leaderboard comparison across models

**Sources:** [nemo_asr/run_eval_ml.py:180-206](), [nemo_asr/run_nemo_ml.sh:91-95]()

---

## Differences from Standard Evaluation

While multilingual evaluation follows the same core pipeline as standard English evaluation, several key differences exist:

| Aspect | Standard Evaluation ([4.1.1](#4.1.1)) | Multilingual Evaluation |
|--------|---------------------------------------|------------------------|
| **Script** | `run_eval.py` | `run_eval_ml.py` |
| **Datasets** | ESB benchmark (English only) | FLEURS, MCV, MLS (20+ languages) |
| **Config Names** | Simple dataset names | `{dataset}_{language}` format |
| **Language Detection** | Implicit (always English) | Explicit detection and tracking |
| **Normalization** | Always `data_utils.normalizer()` | Conditional: English vs. multilingual |
| **Model Parameters** | Standard transcription | Language-aware (e.g., Canary `pnc`, `source_lang`, `target_lang`) |
| **Cache Structure** | `audio_cache/{dataset}/{split}/` | `audio_cache/{config_name}/{split}/` |
| **Orchestration** | Iterate over datasets | Nested iteration: datasets × languages |
| **Results Aggregation** | Across English datasets | Across languages and datasets |

**When to Use Each:**

- **Standard Evaluation**: English-only models, ESB benchmark comparison, standard ASR models
- **Multilingual Evaluation**: Multilingual models (Canary, Parakeet multilingual variants), non-English languages, cross-lingual comparison

**Sources:** [nemo_asr/run_eval_ml.py:1-264](), [nemo_asr/run_nemo_ml.sh:1-96]()

---

## Summary

The multilingual evaluation system extends NeMo's ASR evaluation capabilities to support 20+ languages through:

1. **Flexible Configuration**: Associative array mapping datasets to language sets
2. **Automated Orchestration**: Shell script iterating through all dataset-language combinations
3. **Language-Aware Processing**: Conditional normalization based on language code
4. **Model-Specific Handling**: Special parameters for models like Canary
5. **Structured Caching**: Language-specific audio cache organization
6. **Cross-Lingual Aggregation**: Final scores averaged across all evaluated languages

This architecture enables fair comparison of multilingual ASR models by applying consistent evaluation protocols while respecting language-specific differences in text normalization and model configuration.

**Sources:** [nemo_asr/run_eval_ml.py:1-264](), [nemo_asr/run_nemo_ml.sh:1-96]()

---

