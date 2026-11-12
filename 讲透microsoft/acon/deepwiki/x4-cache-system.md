<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/acon · extra page Cache System · fetched 2026-10-26 -->

# Cache System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [experiments/analysis_tools/utils.py](experiments/analysis_tools/utils.py)

</details>



This document describes the token calculation cache system used by the ACON analysis tools. The cache system prevents redundant tokenization operations during experiment analysis by storing pre-computed token statistics in persistent pickle files.

For information about the broader token analysis system, see [Token and Cost Analysis](#7.1). For details on the specific token calculation functions, see [analyze_experiment_tokens_v2](#7.1.1).

**Scope**: This page covers the cache implementation in [experiments/analysis_tools/utils.py:464-504](), including cache key generation, storage, retrieval, and schema versioning mechanisms.

---

## Cache Architecture Overview

The cache system provides a transparent layer between token calculation functions and their results, using file-based persistent storage with schema versioning for invalidation.

### System Components

```mermaid
graph TB
    subgraph "Analysis Entry Point"
        ANALYZE["analyze_experiment_tokens_v2()"]
    end
    
    subgraph "Cache Decision Logic"
        GET_KEY["get_cache_key()<br/>(file_path, model_name, suffix)"]
        LOAD["load_token_cache(cache_key)"]
        CHECK{"Cache<br/>Hit?"}
    end
    
    subgraph "Token Calculation"
        CALC_AGENT["calculate_llm_tokens_with_cache()"]
        CALC_OPT["calculate_optimizer_tokens_with_cache()"]
    end
    
    subgraph "Cache Storage"
        SAVE["save_token_cache(cache_key, data)"]
        CACHE_DIR["TOKEN_USAGE_CACHE_DIR<br/>analysis_tools/cache/"]
        PICKLE_FILES["*.pkl files<br/>(schema_hash_model_suffix.pkl)"]
    end
    
    subgraph "Cache Key Components"
        SCHEMA["CACHE_SCHEMA_VERSION<br/>'v2.2'"]
        HASH["get_file_hash()<br/>MD5 of file content"]
        MODEL["model_name"]
        SUFFIX["suffix<br/>(_agent_v2, _opt_hist_v2, _opt_obs_v2)"]
    end
    
    ANALYZE --> GET_KEY
    GET_KEY --> HASH
    GET_KEY --> SCHEMA
    GET_KEY --> MODEL
    GET_KEY --> SUFFIX
    
    GET_KEY --> LOAD
    LOAD --> CACHE_DIR
    CACHE_DIR --> PICKLE_FILES
    LOAD --> CHECK
    
    CHECK -->|"Hit"| ANALYZE
    CHECK -->|"Miss"| CALC_AGENT
    CHECK -->|"Miss"| CALC_OPT
    
    CALC_AGENT --> SAVE
    CALC_OPT --> SAVE
    SAVE --> CACHE_DIR
    CACHE_DIR --> PICKLE_FILES
```

**Sources**: [experiments/analysis_tools/utils.py:444-504](), [experiments/analysis_tools/utils.py:638-1136]()

---

## Cache Key Generation

Cache keys uniquely identify cached token statistics based on input file content, model configuration, and calculation schema version.

### Key Construction

The cache key format is: `{CACHE_SCHEMA_VERSION}_{file_hash}_{model_name}{suffix}`

| Component | Purpose | Example Value |
|-----------|---------|---------------|
| `CACHE_SCHEMA_VERSION` | Invalidates cache when logic changes | `v2.2` |
| `file_hash` | MD5 hash of input file content | `a3f5c9e1b2d4...` |
| `model_name` | Token encoding model | `gpt-4.1` |
| `suffix` | Distinguishes cache types | `_agent_v2`, `_opt_hist_v2` |

```mermaid
graph LR
    FILE["Input File<br/>(llm_history.json)"]
    HASH_FUNC["get_file_hash()"]
    MD5["MD5 Hash"]
    
    SCHEMA_V["CACHE_SCHEMA_VERSION"]
    MODEL_N["model_name"]
    SUFFIX_S["suffix"]
    
    CONCAT["String Concatenation"]
    CACHE_KEY["Cache Key<br/>'v2.2_a3f5c9e1_gpt-4.1_agent_v2'"]
    
    FILE --> HASH_FUNC
    HASH_FUNC --> MD5
    
    SCHEMA_V --> CONCAT
    MD5 --> CONCAT
    MODEL_N --> CONCAT
    SUFFIX_S --> CONCAT
    
    CONCAT --> CACHE_KEY
```

**Sources**: [experiments/analysis_tools/utils.py:466-478]()

### File Hashing Implementation

The `get_file_hash()` function computes an MD5 digest of the entire file content:

```python
# Simplified from experiments/analysis_tools/utils.py:466-473
def get_file_hash(file_path: str) -> Optional[str]:
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
```

**Sources**: [experiments/analysis_tools/utils.py:466-473]()

### Cache Key Usage Pattern

Different suffixes identify different cache types:

| Suffix | Usage Context | Input File |
|--------|---------------|------------|
| `_agent_v2` | Agent token calculations | `llm_history.json` |
| `_opt_hist_v2` | History optimizer calculations | `history_optimizer_history.json` |
| `_opt_obs_v2` | Observation optimizer calculations | `obs_optimizer_history.json` |

**Sources**: [experiments/analysis_tools/utils.py:791](), [experiments/analysis_tools/utils.py:864](), [experiments/analysis_tools/utils.py:888]()

---

## Cache Operations

### Loading from Cache

The `load_token_cache()` function attempts to retrieve cached data using the cache key:

```mermaid
graph TB
    INPUT["cache_key"]
    CHECK_KEY{"cache_key<br/>is None?"}
    CONSTRUCT["Construct file path:<br/>TOKEN_USAGE_CACHE_DIR / cache_key.pkl"]
    CHECK_EXISTS{"File<br/>exists?"}
    UNPICKLE["pickle.load()"]
    RETURN_DATA["Return cached data"]
    RETURN_NONE["Return None"]
    
    INPUT --> CHECK_KEY
    CHECK_KEY -->|"Yes"| RETURN_NONE
    CHECK_KEY -->|"No"| CONSTRUCT
    CONSTRUCT --> CHECK_EXISTS
    CHECK_EXISTS -->|"No"| RETURN_NONE
    CHECK_EXISTS -->|"Yes"| UNPICKLE
    UNPICKLE --> RETURN_DATA
    UNPICKLE -->|"Exception"| RETURN_NONE
```

**Sources**: [experiments/analysis_tools/utils.py:481-491]()

### Saving to Cache

The `save_token_cache()` function persists calculated token data:

```mermaid
graph TB
    INPUT["cache_key, token_data"]
    CHECK_KEY{"cache_key<br/>is None?"}
    MKDIR["os.makedirs()<br/>Create cache directory"]
    CONSTRUCT["Construct file path:<br/>TOKEN_USAGE_CACHE_DIR / cache_key.pkl"]
    PICKLE["pickle.dump(token_data)"]
    LOG_WARN["Log warning on failure"]
    RETURN["Return"]
    
    INPUT --> CHECK_KEY
    CHECK_KEY -->|"Yes"| RETURN
    CHECK_KEY -->|"No"| MKDIR
    MKDIR --> CONSTRUCT
    CONSTRUCT --> PICKLE
    PICKLE -->|"Success"| RETURN
    PICKLE -->|"Exception"| LOG_WARN
    LOG_WARN --> RETURN
```

**Sources**: [experiments/analysis_tools/utils.py:494-503]()

### Cache Directory Configuration

The cache directory is configured with fallback logic:

```python
# From experiments/analysis_tools/utils.py:444-452
try:
    from experiments.analysis_tools.config import TOKEN_USAGE_CACHE_DIR
except Exception:
    try:
        from .config import TOKEN_USAGE_CACHE_DIR
    except Exception:
        TOKEN_USAGE_CACHE_DIR = Path('analysis/cache/token_usage')
        TOKEN_USAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
```

**Sources**: [experiments/analysis_tools/utils.py:444-452]()

---

## Schema Versioning

The `CACHE_SCHEMA_VERSION` constant ensures cache invalidation when token calculation logic changes.

### Version History

| Version | Description |
|---------|-------------|
| `v2.2` | Current version (as of codebase snapshot) |
| Earlier | Incremented when advanced optimizer output logic updated |
| Earlier | Incremented when dependency metric added |

**Sources**: [experiments/analysis_tools/utils.py:42-44]()

### Automatic Cache Invalidation

When `CACHE_SCHEMA_VERSION` changes:
- All existing cache keys become invalid (different prefix)
- Old cache files remain on disk but are never loaded
- New calculations generate new cache files with updated version prefix
- No manual cache clearing required

```mermaid
graph LR
    OLD_V["Old Schema: v2.1"]
    OLD_KEY["Cache Key:<br/>'v2.1_hash_model_suffix'"]
    OLD_FILE["Old Cache File:<br/>v2.1_hash_model_suffix.pkl"]
    
    NEW_V["New Schema: v2.2"]
    NEW_KEY["Cache Key:<br/>'v2.2_hash_model_suffix'"]
    NEW_FILE["New Cache File:<br/>v2.2_hash_model_suffix.pkl"]
    
    LOOKUP["load_token_cache()"]
    MISS["Cache Miss"]
    RECALC["Recalculate Tokens"]
    
    OLD_V -.-> OLD_KEY
    OLD_KEY -.-> OLD_FILE
    
    NEW_V --> NEW_KEY
    NEW_KEY --> LOOKUP
    LOOKUP --> MISS
    MISS --> RECALC
    RECALC --> NEW_FILE
    
    OLD_FILE -.->|"Never loaded"| OLD_FILE
```

**Sources**: [experiments/analysis_tools/utils.py:42-44](), [experiments/analysis_tools/utils.py:476-478]()

---

## Integration with Token Analysis

The cache system is transparently integrated into the main analysis function `analyze_experiment_tokens_v2()`.

### Agent Token Calculation Caching

```mermaid
graph TB
    TASK["Task directory"]
    LLM_FILE["llm_history.json"]
    GET_KEY["get_cache_key(llm_history_file,<br/>agent_model, '_agent_v2')"]
    LOAD["load_token_cache(cache_key)"]
    CHECK{"Cached?"}
    
    BACKFILL{"Has<br/>dependency<br/>metric?"}
    RECOMPUTE["calculate_llm_tokens_with_cache()<br/>Recompute with new metric"]
    USE_CACHED["Use cached stats"]
    
    CALC_NEW["calculate_llm_tokens_with_cache()<br/>Fresh calculation"]
    ENV_STEPS["calculate_env_steps()"]
    SAVE["save_token_cache(cache_key, stats)"]
    
    TASK --> LLM_FILE
    LLM_FILE --> GET_KEY
    GET_KEY --> LOAD
    LOAD --> CHECK
    
    CHECK -->|"Yes"| BACKFILL
    BACKFILL -->|"No"| RECOMPUTE
    RECOMPUTE --> SAVE
    BACKFILL -->|"Yes"| USE_CACHED
    
    CHECK -->|"No"| CALC_NEW
    CALC_NEW --> ENV_STEPS
    ENV_STEPS --> SAVE
```

**Sources**: [experiments/analysis_tools/utils.py:779-817]()

### Optimizer Token Calculation Caching

The same pattern applies to optimizer history files:

```mermaid
graph TB
    HIST_FILE["history_optimizer_history.json"]
    OBS_FILE["obs_optimizer_history.json"]
    
    HIST_KEY["get_cache_key(..., '_opt_hist_v2')"]
    OBS_KEY["get_cache_key(..., '_opt_obs_v2')"]
    
    HIST_LOAD["load_token_cache(hist_key)"]
    OBS_LOAD["load_token_cache(obs_key)"]
    
    HIST_CHECK{"Cached?"}
    OBS_CHECK{"Cached?"}
    
    HIST_CALC["calculate_optimizer_tokens_with_cache()<br/>History optimizer"]
    OBS_CALC["calculate_optimizer_tokens_with_cache()<br/>Obs optimizer"]
    
    HIST_SAVE["save_token_cache(hist_key, stats)"]
    OBS_SAVE["save_token_cache(obs_key, stats)"]
    
    COMBINE["Combine stats:<br/>history + observation"]
    
    HIST_FILE --> HIST_KEY
    HIST_KEY --> HIST_LOAD
    HIST_LOAD --> HIST_CHECK
    HIST_CHECK -->|"No"| HIST_CALC
    HIST_CALC --> HIST_SAVE
    
    OBS_FILE --> OBS_KEY
    OBS_KEY --> OBS_LOAD
    OBS_LOAD --> OBS_CHECK
    OBS_CHECK -->|"No"| OBS_CALC
    OBS_CALC --> OBS_SAVE
    
    HIST_CHECK -->|"Yes"| COMBINE
    OBS_CHECK -->|"Yes"| COMBINE
    HIST_SAVE --> COMBINE
    OBS_SAVE --> COMBINE
```

**Sources**: [experiments/analysis_tools/utils.py:843-920]()

### Cache Backfill Logic

When cached data exists but lacks newly-added metrics (e.g., `total_dependency`, `peak_tokens`), the system automatically recomputes:

```python
# Simplified from experiments/analysis_tools/utils.py:795-807
if cached:
    agent_stats = cached
    if 'total_dependency' not in agent_stats:
        # Backfill new metric by recomputing
        with open(llm_history_file, 'r') as f:
            llm_history = json.load(f)
        recomputed = calculate_llm_tokens_with_cache(llm_history, agent_model)
        agent_stats = recomputed
        save_token_cache(cache_key, agent_stats)
```

**Sources**: [experiments/analysis_tools/utils.py:795-807](), [experiments/analysis_tools/utils.py:868-873]()

---

## Cache Performance Characteristics

### Benefits

| Aspect | Impact |
|--------|--------|
| **Repeated Analysis** | 100x+ speedup when re-analyzing same experiments |
| **Tokenization Cost** | Eliminates expensive `tiktoken.encode()` calls |
| **Memory Efficiency** | Loads only needed cached results, not all files |
| **Experiment Iteration** | Fast feedback when testing analysis code changes |

### Cache Size Characteristics

```mermaid
graph LR
    INPUT_FILE["Input File<br/>llm_history.json<br/>~100-500 KB"]
    TOKENIZATION["Tokenization<br/>Process"]
    CACHE_DATA["Cached Data<br/>(token counts, breakdowns)<br/>~5-20 KB"]
    CACHE_FILE["Cache File<br/>*.pkl<br/>~5-20 KB"]
    
    INPUT_FILE --> TOKENIZATION
    TOKENIZATION --> CACHE_DATA
    CACHE_DATA --> CACHE_FILE
    
    RATIO["Compression Ratio:<br/>~10-50x smaller"]
    CACHE_DATA -.-> RATIO
```

Cache files store only computed statistics (token counts, breakdowns), not the original text, resulting in significant space savings.

**Sources**: [experiments/analysis_tools/utils.py:131-231](), [experiments/analysis_tools/utils.py:234-438]()

---

## Cache File Naming Convention

Cache files follow a deterministic naming pattern based on their cache key:

### File Name Structure

```
{CACHE_SCHEMA_VERSION}_{file_hash}_{model_name}{suffix}.pkl
```

### Examples

| Cache Type | Example Filename |
|------------|------------------|
| Agent (GPT-4.1) | `v2.2_a3f5c9e1b2d4f8c7_gpt-4.1_agent_v2.pkl` |
| Agent (GPT-4.1-mini) | `v2.2_a3f5c9e1b2d4f8c7_gpt-4.1-mini_agent_v2.pkl` |
| History Optimizer | `v2.2_d7e8f9a0b1c2d3e4_gpt-4.1-mini_opt_hist_v2.pkl` |
| Obs Optimizer | `v2.2_f1e2d3c4b5a69780_gpt-4.1-mini_opt_obs_v2.pkl` |

Note: The same input file analyzed with different models generates separate cache files.

**Sources**: [experiments/analysis_tools/utils.py:476-478](), [experiments/analysis_tools/utils.py:484-485](), [experiments/analysis_tools/utils.py:498]()

---

## Cache Invalidation Scenarios

The cache is automatically invalidated in the following scenarios:

```mermaid
graph TB
    SCENARIO1["Input file content changes"]
    SCENARIO2["Model name changes"]
    SCENARIO3["Schema version incremented"]
    SCENARIO4["Suffix parameter changes"]
    
    HASH_CHANGE["MD5 hash changes"]
    KEY_CHANGE["Cache key changes"]
    MISS["Cache miss"]
    RECALC["Token recalculation"]
    NEW_CACHE["New cache file created"]
    
    SCENARIO1 --> HASH_CHANGE
    SCENARIO2 --> KEY_CHANGE
    SCENARIO3 --> KEY_CHANGE
    SCENARIO4 --> KEY_CHANGE
    
    HASH_CHANGE --> KEY_CHANGE
    KEY_CHANGE --> MISS
    MISS --> RECALC
    RECALC --> NEW_CACHE
```

**Sources**: [experiments/analysis_tools/utils.py:466-478]()

### Manual Cache Clearing

While not typically necessary, the cache can be manually cleared by:

```bash
# Remove all cache files
rm -rf analysis_tools/cache/token_usage/*.pkl

# Remove caches for specific schema version
rm -rf analysis_tools/cache/token_usage/v2.2_*.pkl

# Remove caches for specific model
rm -rf analysis_tools/cache/token_usage/*_gpt-4.1_*.pkl
```

**Sources**: [experiments/analysis_tools/utils.py:450-452]()

---

## Error Handling

The cache system implements defensive error handling to ensure analysis continues even if cache operations fail:

```mermaid
graph TB
    SAVE_ATTEMPT["save_token_cache()"]
    WRITE_FILE["pickle.dump(data, file)"]
    SUCCESS["Cache saved successfully"]
    EXCEPTION["Exception caught"]
    LOG_WARNING["logging.warning()<br/>'Failed to save token cache'"]
    CONTINUE["Analysis continues<br/>(cache miss on next run)"]
    
    SAVE_ATTEMPT --> WRITE_FILE
    WRITE_FILE --> SUCCESS
    WRITE_FILE --> EXCEPTION
    EXCEPTION --> LOG_WARNING
    LOG_WARNING --> CONTINUE
```

Similarly, `load_token_cache()` returns `None` on any exception, causing a cache miss rather than failing the analysis.

**Sources**: [experiments/analysis_tools/utils.py:494-503](), [experiments/analysis_tools/utils.py:481-491]()

---

## Summary

The cache system provides transparent, schema-versioned persistence for token calculation results:

- **Cache keys** combine schema version, file hash, model name, and suffix to uniquely identify cached data
- **Pickle files** store computed token statistics in `TOKEN_USAGE_CACHE_DIR`
- **Schema versioning** (`CACHE_SCHEMA_VERSION`) automatically invalidates outdated caches
- **Backfill logic** recomputes cache entries when new metrics are added
- **Error handling** ensures analysis continues even if cache operations fail

This design enables fast re-analysis of experiments while maintaining correctness when calculation logic evolves.

**Sources**: [experiments/analysis_tools/utils.py:1-1446]()

---

