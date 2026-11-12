<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/reward-bench · page 7 Data Pipeline & Utilities · fetched 2026-10-26 -->

# Data Pipeline & Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rewardbench/utils.py](rewardbench/utils.py)
- [tests/test_data.py](tests/test_data.py)

</details>



The RewardBench data pipeline provides a comprehensive system for loading, processing, and formatting preference datasets for reward model evaluation. This system handles multiple data sources, conversation formatting, and specialized evaluation scenarios including Best-of-N candidate selection and multi-response evaluation.

For information about model evaluation workflows, see [Model Evaluation](#5). For analysis of evaluation results, see [Analysis & Visualization](#8).

## Data Sources and Repositories

RewardBench pulls evaluation data from several HuggingFace repositories, each serving specific evaluation purposes:

| Repository | Purpose | Variable |
|------------|---------|----------|
| `allenai/reward-bench` | Core evaluation dataset | `CORE_EVAL_SET` |
| `allenai/pref-test-sets` | Extended preference test sets | `EXTRA_PREF_SETS` |
| `allenai/reward-bench-2` | RewardBench 2.0 multi-response dataset | `CORE_EVAL_SET_V2` |
| `ai2-adapt-dev/HERM_BoN_candidates` | Best-of-N candidate responses | `BON_CANDIDATES` |
| `allenai/reward-bench-results` | Evaluation results repository | `EVAL_REPO` |
| `allenai/reward-bench-2-results` | RewardBench 2.0 results repository | `EVAL_REPO_V2` |

### Data Pipeline Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        CORE_EVAL["allenai/reward-bench<br/>Core Evaluation Set"]
        PREF_SETS["allenai/pref-test-sets<br/>Extended Preference Sets"]
        RB2["allenai/reward-bench-2<br/>Multi-Response Dataset"]
        BON["ai2-adapt-dev/HERM_BoN_candidates<br/>Best-of-N Candidates"]
    end
    
    subgraph "Loading Functions"
        LOAD_EVAL["load_eval_dataset()"]
        LOAD_MULTI["load_eval_dataset_multi()"]
        LOAD_BON["load_bon_dataset()"]
        LOAD_BON_V2["load_bon_dataset_v2()"]
        LOAD_PROCESS["load_and_process_dataset()"]
    end
    
    subgraph "Processing Pipeline"
        CHAT_TEMPLATE["Chat Template Application"]
        TOKENIZER_PREP["prepare_dialogue_from_tokenizer()"]
        FASTCHAT_PREP["prepare_dialogue()"]
        CUSTOM_FORMAT["Custom Dialogue Formatting"]
    end
    
    subgraph "Specialized Processing"
        REROLL["reroll_and_score_dataset()"]
        TIES_PROC["process_single_model()"]
        CONV_MAP["map_conversations_testsets()"]
    end
    
    subgraph "Output Formats"
        PREF_DATA["Preference Data<br/>text_chosen, text_rejected"]
        INST_DATA["Instruction Data<br/>text, prompt"]
        MULTI_RESP["Multi-Response Data<br/>texts_chosen, texts_rejected"]
        BON_DATA["Best-of-N Data<br/>scores, results"]
    end
    
    CORE_EVAL --> LOAD_EVAL
    PREF_SETS --> LOAD_EVAL
    RB2 --> LOAD_MULTI
    BON --> LOAD_BON
    BON --> LOAD_BON_V2
    
    LOAD_EVAL --> CHAT_TEMPLATE
    LOAD_MULTI --> CHAT_TEMPLATE
    LOAD_BON --> CHAT_TEMPLATE
    LOAD_BON_V2 --> CHAT_TEMPLATE
    LOAD_PROCESS --> CHAT_TEMPLATE
    
    CHAT_TEMPLATE --> TOKENIZER_PREP
    CHAT_TEMPLATE --> FASTCHAT_PREP
    CHAT_TEMPLATE --> CUSTOM_FORMAT
    
    TOKENIZER_PREP --> PREF_DATA
    FASTCHAT_PREP --> PREF_DATA
    CUSTOM_FORMAT --> PREF_DATA
    
    TOKENIZER_PREP --> INST_DATA
    FASTCHAT_PREP --> INST_DATA
    
    LOAD_MULTI --> MULTI_RESP
    LOAD_BON --> REROLL
    LOAD_BON_V2 --> REROLL
    REROLL --> BON_DATA
    
    LOAD_MULTI --> TIES_PROC
    TIES_PROC --> BON_DATA
```

Sources: [rewardbench/utils.py:40-46](), [rewardbench/utils.py:298-421](), [rewardbench/utils.py:424-532]()

## Dataset Loading Pipeline

The data loading system provides multiple entry points for different evaluation scenarios:

### Core Dataset Loading

The `load_eval_dataset()` function serves as the primary interface for loading RewardBench evaluation data:

```mermaid
graph TB
    subgraph "load_eval_dataset Function Flow"
        START["load_eval_dataset()"]
        CORE_CHECK{"core_set?"}
        LOAD_CORE["load_dataset(CORE_EVAL_SET)"]
        LOAD_PREF["load_dataset(EXTRA_PREF_SETS)"]
        PROCESS_PREF["Process Multiple Subsets"]
        CUSTOM_CHECK{"custom_dialogue_formatting?"}
        TOKENIZER_CHECK{"usable_tokenizer?"}
        APPLY_TOKENIZER["prepare_dialogue_from_tokenizer()"]
        APPLY_FASTCHAT["prepare_dialogue()"]
        APPLY_CUSTOM["map_conversations()"]
        FILTER_TURNS["filter_long_turns()"]
        REMOVE_COLS["Remove Unwanted Columns"]
        RETURN["Return dataset, subsets"]
    end
    
    START --> CORE_CHECK
    CORE_CHECK -->|True| LOAD_CORE
    CORE_CHECK -->|False| LOAD_PREF
    LOAD_PREF --> PROCESS_PREF
    LOAD_CORE --> CUSTOM_CHECK
    PROCESS_PREF --> CUSTOM_CHECK
    CUSTOM_CHECK -->|False| TOKENIZER_CHECK
    CUSTOM_CHECK -->|True| APPLY_CUSTOM
    TOKENIZER_CHECK -->|True| APPLY_TOKENIZER
    TOKENIZER_CHECK -->|False| APPLY_FASTCHAT
    APPLY_TOKENIZER --> FILTER_TURNS
    APPLY_FASTCHAT --> FILTER_TURNS
    APPLY_CUSTOM --> FILTER_TURNS
    FILTER_TURNS --> REMOVE_COLS
    REMOVE_COLS --> RETURN
```

The function supports several key parameters:
- `core_set`: Boolean flag to select between core evaluation set and extended preference sets
- `custom_dialogue_formatting`: Enables custom formatting for specialized models
- `conv`: FastChat conversation template for dialogue formatting
- `tokenizer`: HuggingFace tokenizer with chat template support
- `keep_columns`: List of columns to retain in final dataset
- `max_turns`: Maximum conversation turns for filtering

Sources: [rewardbench/utils.py:298-421]()

### Multi-Response Dataset Loading

The `load_eval_dataset_multi()` function handles RewardBench 2.0 datasets with multiple response candidates:

- Loads from `CORE_EVAL_SET_V2` by default
- Supports custom dataset specification
- Handles `texts_chosen` and `texts_rejected` columns containing multiple responses
- Maintains `subset` and `num_correct` columns for ties evaluation

Sources: [rewardbench/utils.py:424-532]()

### Best-of-N Dataset Processing

The system provides two functions for Best-of-N evaluation:

- `load_bon_dataset()`: Processes legacy BON candidates from AlpacaEval and MT-Bench
- `load_bon_dataset_v2()`: Handles newer BON datasets with flexible response counts

Both functions unroll multiple candidate responses into individual dataset rows for evaluation.

Sources: [rewardbench/utils.py:584-686](), [rewardbench/utils.py:689-806]()

## Data Processing and Formatting

### Conversation Template System

RewardBench supports two primary conversation formatting approaches:

```mermaid
graph TB
    subgraph "Conversation Formatting Pipeline"
        INPUT["Raw Dataset"]
        TEMPLATE_CHECK{"Template Available?"}
        TOKENIZER_PATH["HuggingFace Tokenizer Path"]
        FASTCHAT_PATH["FastChat Template Path"]
        
        subgraph "Tokenizer Processing"
            TOKENIZER_PREP["prepare_dialogue_from_tokenizer()"]
            APPLY_CHAT_TEMPLATE["tokenizer.apply_chat_template()"]
            MULTI_TURN_PROC["Multi-turn Processing"]
            SINGLE_TURN_PROC["Single-turn Processing"]
        end
        
        subgraph "FastChat Processing"
            FASTCHAT_PREP["prepare_dialogue()"]
            CONV_TEMPLATE["Conversation.get_prompt()"]
            ROLE_MAPPING["Role Mapping"]
            MESSAGE_BUILDING["Message Building"]
        end
        
        OUTPUT["Formatted Conversations"]
    end
    
    INPUT --> TEMPLATE_CHECK
    TEMPLATE_CHECK -->|"check_tokenizer_chat_template()"| TOKENIZER_PATH
    TEMPLATE_CHECK -->|"FastChat conv provided"| FASTCHAT_PATH
    
    TOKENIZER_PATH --> TOKENIZER_PREP
    TOKENIZER_PREP --> APPLY_CHAT_TEMPLATE
    APPLY_CHAT_TEMPLATE --> MULTI_TURN_PROC
    APPLY_CHAT_TEMPLATE --> SINGLE_TURN_PROC
    
    FASTCHAT_PATH --> FASTCHAT_PREP
    FASTCHAT_PREP --> CONV_TEMPLATE
    CONV_TEMPLATE --> ROLE_MAPPING
    ROLE_MAPPING --> MESSAGE_BUILDING
    
    MULTI_TURN_PROC --> OUTPUT
    SINGLE_TURN_PROC --> OUTPUT
    MESSAGE_BUILDING --> OUTPUT
```

Sources: [rewardbench/utils.py:809-893](), [rewardbench/utils.py:896-985]()

### Data Format Specifications

The system handles multiple data format types:

**Preference Data Format:**
- `prompt`: Question or conversation context
- `chosen`: Preferred response
- `rejected`: Non-preferred response
- Output: `text_chosen`, `text_rejected`, `prompt`

**Instruction Data Format:**
- `messages`: Complete conversation turns
- `prompt`: Initial user prompt
- Output: `text`, `prompt`

**Multi-Response Format:**
- `chosen`: List of preferred responses
- `rejected`: List of non-preferred responses
- Output: `texts_chosen`, `texts_rejected`

Sources: [rewardbench/utils.py:167-295]()

## Specialized Processing Functions

### Best-of-N Rerolling

The `reroll_and_score_dataset()` function processes Best-of-N datasets by:

1. Grouping responses by completion count
2. Combining scores and text into lists
3. Applying tie-breaking penalties
4. Computing accuracy based on score rankings

```mermaid
graph TB
    subgraph "Best-of-N Processing"
        UNROLLED["Unrolled Dataset"]
        GROUP["Group by total_completions"]
        COMBINE["Combine scores and text"]
        CALC_RESULTS["Calculate results with tie penalty"]
        REROLLED["Rerolled Dataset"]
    end
    
    UNROLLED --> GROUP
    GROUP --> COMBINE
    COMBINE --> CALC_RESULTS
    CALC_RESULTS --> REROLLED
```

Sources: [rewardbench/utils.py:535-581]()

### Ties Evaluation Processing

The `process_single_model()` function handles ties evaluation datasets:

1. Groups samples by prompt ID and type (ref/tied)
2. Calculates per-prompt accuracy and margin statistics
3. Computes overall score using weighted combination of metrics
4. Applies tie-breaking using normalized margin scores

Key metrics computed:
- `ref_accuracy`: Accuracy on reference prompts
- `tied_accuracy`: Accuracy on tied prompts
- `correctness_preferred`: Margin-based correctness preference
- `correctness_preferred_hard`: Hard margin-based preference

Sources: [rewardbench/utils.py:1023-1098]()

## Results Management

### Hub Upload System

The `save_to_hub()` function manages result persistence:

```mermaid
graph TB
    subgraph "Results Upload Pipeline"
        RESULTS["results_dict"]
        LOCAL_SAVE["Save to ./results/"]
        BEAKER_CHECK{"save_metrics_for_beaker?"}
        BEAKER_SAVE["Save to /output/metrics.json"]
        HUB_CHECK{"local_only or debug?"}
        HUB_UPLOAD["Upload to HuggingFace Hub"]
        REPO_SELECT{"best_of_n?"}
        EVAL_REPO_TARGET["EVAL_REPO"]
        EVAL_REPO_V2_TARGET["EVAL_REPO_V2"]
    end
    
    RESULTS --> LOCAL_SAVE
    LOCAL_SAVE --> BEAKER_CHECK
    BEAKER_CHECK -->|True| BEAKER_SAVE
    BEAKER_CHECK -->|False| HUB_CHECK
    BEAKER_SAVE --> HUB_CHECK
    HUB_CHECK -->|False| HUB_UPLOAD
    HUB_CHECK -->|True| REPO_SELECT
    HUB_UPLOAD --> REPO_SELECT
    REPO_SELECT -->|False| EVAL_REPO_TARGET
    REPO_SELECT -->|True| EVAL_REPO_V2_TARGET
```

Sources: [rewardbench/utils.py:97-157]()

### Score Calculation

The `calculate_scores_per_section()` function computes weighted section scores:

- Takes example counts per test subset
- Applies subset-to-section mapping
- Calculates weighted averages based on example counts
- Returns section-level performance metrics

Sources: [rewardbench/utils.py:68-84]()

## Utility Functions

### Model Configuration Loading

The `load_model_config()` function provides model-specific configuration:

```python
def load_model_config(model_name):
    if model_name in REWARD_MODEL_CONFIG:
        return REWARD_MODEL_CONFIG[model_name]
    else:
        return REWARD_MODEL_CONFIG["default"]
```

Sources: [rewardbench/utils.py:988-996]()

### Data Type Utilities

- `torch_dtype_mapping()`: Maps string representations to PyTorch data types
- `check_tokenizer_chat_template()`: Validates tokenizer chat template availability

Sources: [rewardbench/utils.py:53-65](), [rewardbench/utils.py:87-94]()

### Column Management

The system provides flexible column filtering through `keep_columns` parameters in dataset loading functions, enabling:

- Retention of evaluation-specific columns
- Removal of unnecessary metadata
- Customization for different evaluation pipelines

Sources: [rewardbench/utils.py:304](), [rewardbench/utils.py:431]()

---

