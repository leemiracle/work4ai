<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/CommonGen-Eval · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [data_utils.py](data_utils.py)
- [eval_utils.py](eval_utils.py)
- [scripts/Pallas-0.5.sh](scripts/Pallas-0.5.sh)
- [show_table.py](show_table.py)

</details>



## Purpose and Scope

This document describes the overall architecture of the CommonGen-Eval system, explaining how the major components interact to evaluate language models on concept-to-sentence generation tasks. It covers the three-tier architecture (data, execution, presentation), component interactions, data flow patterns, and storage organization.

For detailed information on specific subsystems:
- Data flow mechanics: see [Data Pipeline](#3.1)
- Model inference details: see [Inference System](#3.2)
- GPT-4 evaluation mechanics: see [Evaluation System](#3.3)
- Results processing: see [Results Aggregation](#6.1)

---

## Architectural Overview

The CommonGen-Eval system follows a **pipeline architecture** with three distinct stages: inference, evaluation, and aggregation. Each stage reads from and writes to specific directories, creating a clear separation of concerns.

### System Components Diagram

```mermaid
graph TB
    subgraph "Data_Layer[Data Layer]"
        HF_dataset["allenai/commongen_lite<br/>load_dataset()"]
        HF_eval["allenai/commongen_lite_eval<br/>evaluation ground truth"]
        Templates["instruct_template.md<br/>eval_template.md"]
    end
    
    subgraph "Inference_Stage[Inference Stage]"
        shell_scripts["scripts/*.sh<br/>model configurations"]
        vllm_infer["vllm_infer.py<br/>batch inference engine"]
        data_utils["data_utils.py<br/>load_eval_data()<br/>apply_template()<br/>save_outputs()"]
        fastchat["fastchat_conversation.py<br/>get_conv_template()"]
    end
    
    subgraph "Evaluation_Stage[Evaluation Stage]"
        evaluate_py["evaluate.py<br/>GPT-4 judge orchestrator"]
        eval_utils["eval_utils.py<br/>analyze_words()<br/>openai_chat_request()"]
    end
    
    subgraph "Aggregation_Stage[Aggregation Stage]"
        show_table["show_table.py<br/>leaderboard generation"]
        show_cases["show_cases.py<br/>case visualization"]
    end
    
    subgraph "Storage[Persistent Storage]"
        model_out["model_outputs/<br/>modelname.json"]
        eval_out["eval_outputs/<br/>modelname.eval_result.json"]
        agg_results["aggregated_eval_results.json"]
    end
    
    HF_dataset --> data_utils
    Templates --> data_utils
    data_utils --> vllm_infer
    fastchat --> data_utils
    shell_scripts --> vllm_infer
    vllm_infer --> model_out
    
    model_out --> evaluate_py
    HF_eval --> evaluate_py
    Templates --> evaluate_py
    eval_utils --> evaluate_py
    evaluate_py --> eval_out
    
    eval_out --> show_table
    HF_eval --> show_table
    show_table --> agg_results
    
    agg_results --> show_cases
```

**Sources**: [README.md:16-98](), [data_utils.py:1-94](), [show_table.py:1-122](), [eval_utils.py:1-158]()

---

## Three-Tier Logical Architecture

The system is organized into three logical tiers that separate configuration, execution, and presentation concerns.

```mermaid
graph LR
    subgraph "Tier1[Tier 1: Configuration]"
        T1A["Dataset<br/>400 test examples<br/>900 references"]
        T1B["fastchat_conversation.py<br/>50+ model templates"]
        T1C["Prompt Templates<br/>.md files"]
    end
    
    subgraph "Tier2[Tier 2: Execution]"
        T2A["vllm_infer.py<br/>Model inference"]
        T2B["evaluate.py<br/>GPT-4 evaluation"]
        T2C["Utilities<br/>data_utils.py<br/>eval_utils.py"]
    end
    
    subgraph "Tier3[Tier 3: Presentation]"
        T3A["show_table.py<br/>tabulate() output"]
        T3B["show_cases.py<br/>HTML visualization"]
    end
    
    T1A --> T2C
    T1B --> T2C
    T1C --> T2C
    T2C --> T2A
    T2C --> T2B
    T2A --> T3A
    T2B --> T3A
    T3A --> T3B
```

**Sources**: [README.md:48-97](), [data_utils.py:6-57](), [show_table.py:22-122]()

---

## Component Interaction Details

### Inference Pipeline Components

The inference pipeline transforms concept sets into model-generated sentences through several stages of processing.

```mermaid
flowchart TD
    A["load_eval_data()<br/>data_utils.py:34-57"]
    B["load_dataset()<br/>allenai/commongen_lite"]
    C["apply_template()<br/>data_utils.py:6-32"]
    D["get_conv_template()<br/>fastchat_conversation.py"]
    E["vllm_infer.py<br/>batch generation"]
    F["save_outputs()<br/>data_utils.py:72-88"]
    G["model_outputs/<br/>modelname.json"]
    
    B --> A
    A --> C
    D --> C
    C --> E
    E --> F
    F --> G
    
    A -.metadata.-> F
    A -.chat_history.-> F
```

| Component | Function | Key Outputs |
|-----------|----------|-------------|
| `load_eval_data()` | Loads dataset and formats as chat history | `id_strs`, `chat_history`, `model_inputs`, `metadata` |
| `apply_template()` | Applies model-specific conversation format | List of formatted prompt strings |
| `get_conv_template()` | Retrieves template for specific model | Conversation object with `get_prompt()` method |
| `save_outputs()` | Serializes results to JSON | `formatted_outputs` with instruction, output, metadata |

**Sources**: [data_utils.py:34-88](), [scripts/Pallas-0.5.sh:1-7]()

---

### Evaluation Pipeline Components

The evaluation pipeline compares model outputs against human references using both automated metrics and GPT-4 judgment.

```mermaid
flowchart TB
    A["model_outputs/<br/>modelname.json"]
    B["evaluate.py<br/>main orchestrator"]
    C["analyze_words()<br/>eval_utils.py:17-37"]
    D["openai_chat_request()<br/>eval_utils.py:100-156"]
    E["retry_handler()<br/>eval_utils.py:47-98"]
    F["eval_outputs/<br/>modelname.eval_result.json"]
    
    G["spacy.load()<br/>en_core_web_lg"]
    H["openai.ChatCompletion<br/>GPT-4 API"]
    
    A --> B
    B --> C
    B --> D
    C --> G
    D --> E
    E --> H
    D --> F
    C -.found_words<br/>found_pos_words.-> F
    D -.winner<br/>A/B/tie.-> F
```

| Function | Purpose | Returns |
|----------|---------|---------|
| `analyze_words()` | Lemmatizes and checks POS tags using spacy | `found_words`, `found_pos_words` (sets) |
| `openai_chat_request()` | Makes API call to GPT-4 with temperature=0 | List of response strings |
| `retry_handler()` | Decorator with exponential backoff for rate limits | Wrapped function with retry logic |

**Sources**: [eval_utils.py:17-156](), [README.md:99-147]()

---

### Aggregation Pipeline Components

The aggregation pipeline collects evaluation results from all models and generates comparative metrics.

```mermaid
flowchart LR
    A["eval_outputs/<br/>model1.eval_result.json<br/>model2.eval_result.json<br/>..."]
    B["show_table.py<br/>lines 69-112"]
    C["load_dataset()<br/>allenai/commongen_lite_eval"]
    D["analyze_words()<br/>for human refs"]
    E["aggregated_eval_results<br/>dictionary"]
    F["tabulate()<br/>GitHub/HTML format"]
    G["aggregated_eval_results.json"]
    
    A --> B
    C --> B
    C --> D
    D --> B
    B --> E
    E --> F
    E --> G
```

**Key Data Structures in show_table.py:**

```
aggregated_eval_results = {
  "ref_id": {
    "concept_set": [...],
    "human_ref": "...",
    "found_words": [...],
    "found_pos_words": [...],
    "len": int,
    "model_outputs": {
      "model_name": {
        "output": "...",
        "result": "win|lose|tie",
        "found_pos_words": [...],
        "found_words": [...],
        "len": int
      }
    }
  }
}
```

**Sources**: [show_table.py:24-122]()

---

## Data Flow Architecture

### End-to-End Data Flow with Code References

```mermaid
graph TD
    A["HuggingFace Dataset<br/>400 examples"]
    B["data_utils.load_eval_data()"]
    C["metadata dict<br/>id, concept_set keys"]
    D["model_inputs list<br/>templated prompts"]
    E["vllm_infer.py<br/>generation loop"]
    F["data_utils.save_outputs()"]
    G["model_outputs/modelname.json<br/>instruction, output, generator, id"]
    H["evaluate.py<br/>pairwise comparison"]
    I["eval_utils.analyze_words()<br/>spacy lemmatization"]
    J["eval_utils.openai_chat_request()<br/>GPT-4 judgment"]
    K["eval_outputs/modelname.eval_result.json<br/>winner, model_output, human_ref"]
    L["show_table.py<br/>aggregation loop lines 69-112"]
    M["aggregated_eval_results.json<br/>cross-model comparison"]
    N["tabulate()<br/>leaderboard output"]
    
    A --> B
    B --> C
    B --> D
    C --> E
    D --> E
    E --> F
    C --> F
    F --> G
    G --> H
    H --> I
    H --> J
    I --> K
    J --> K
    K --> L
    A --> L
    L --> M
    M --> N
```

**Sources**: [data_utils.py:34-88](), [show_table.py:69-122](), [eval_utils.py:17-156]()

---

## Storage Organization

### File System Structure

```
CommonGen-Eval/
├── model_outputs/
│   ├── Yi-34b-chat.json              # Generated by vllm_infer.py
│   ├── Llama-2-7b-chat-hf.json
│   ├── gpt-4-0613.json
│   └── ...
│
├── eval_outputs/
│   ├── Yi-34b-chat.eval_result.gpt-4-1106-preview.json
│   ├── Llama-2-7b-chat-hf.eval_result.gpt-4-1106-preview.json
│   └── aggregated_eval_results.json  # Generated by show_table.py
│
├── scripts/
│   ├── Pallas-0.5.sh
│   ├── Yi-34b-chat.sh
│   └── all_gpt_eval.sh
│
└── templates/
    ├── instruct_template.md
    └── eval_template.md
```

**JSON Schema Reference:**

**model_outputs/*.json** (generated by [data_utils.py:72-88]()):
```json
[
  {
    "instruction": "Given concepts, write sentence...",
    "output": ["Generated sentence"],
    "generator": "model_name",
    "id": "example_id",
    "concept_set": ["word_POS", ...]
  }
]
```

**eval_outputs/*.eval_result.json** (generated by `evaluate.py`):
```json
[
  {
    "concept_set": ["word_POS", ...],
    "human_ref": {"id": "ref_id", "ref": "Human sentence"},
    "model_output": ["Model sentence"],
    "winner": "model|human|tie"
  }
]
```

**Sources**: [data_utils.py:72-88](), [show_table.py:7-20, 69-99]()

---

## Execution Orchestration

### Shell Script Configuration Pattern

The system uses shell scripts to configure and launch model inference with specific parameters:

**Example: scripts/Pallas-0.5.sh**
```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 \
python vllm_infer.py \
    --data_name "commongen" \
    --model_name Mihaiii/Pallas-0.5 
    --tensor_parallel_size 4 
    --dtype bfloat16 \
    --output_folder "model_outputs/" \
    --top_p 1 
    --temperature 0 
    --batch_size 8 
    --max_tokens 128
```

**Common Parameters:**
| Parameter | Purpose | Typical Value |
|-----------|---------|---------------|
| `--data_name` | Dataset identifier | `"commongen"` |
| `--model_name` | HuggingFace model path | Model-specific |
| `--tensor_parallel_size` | GPU parallelization | 1, 2, 4, or 8 |
| `--temperature` | Sampling temperature | 0 (deterministic) |
| `--batch_size` | Inference batch size | 8 |
| `--max_tokens` | Max generation length | 128 |

**Sources**: [scripts/Pallas-0.5.sh:1-7](), [README.md:55-69]()

---

## Template Application System

### Model-Specific Template Selection

The `apply_template()` function in [data_utils.py:6-32]() uses conditional logic to select appropriate conversation templates:

```mermaid
flowchart TD
    A["apply_template()<br/>chat_history, model_name"]
    B{"Model name<br/>matching"}
    C["get_conv_template('tulu')"]
    D["get_conv_template('zephyr')"]
    E["get_conv_template('llama-2')"]
    F["get_conv_template('mistral')"]
    G["get_conv_template('Yi-34b-chat')"]
    H["get_conv_template('vicuna_v1.1')"]
    I["Direct chat format<br/>for GPT models"]
    J["conv.append_message()<br/>conv.get_prompt()"]
    K["model_inputs list"]
    
    A --> B
    B -->|"'tulu' in name"| C
    B -->|"'zephyr' in name"| D
    B -->|"'llama-2' in name"| E
    B -->|"'mixtral' or 'mistral'"| F
    B -->|"'yi' and 'chat'"| G
    B -->|"'vicuna' or 'pallas'"| H
    B -->|"'gpt-' in name"| I
    C --> J
    D --> J
    E --> J
    F --> J
    G --> J
    H --> J
    J --> K
    I --> K
```

**Sources**: [data_utils.py:6-32]()

---

## Metrics Calculation

The system computes multiple metrics for each model, calculated in [show_table.py:74-112]():

### Metric Computation Flow

```mermaid
flowchart LR
    A["Per-example results"]
    B["analyze_words()<br/>concept_set, output"]
    C["Coverage check<br/>len(found_words)==len(cs)"]
    D["PoS check<br/>len(found_pos_words)==len(cs)"]
    E["Win/tie count<br/>from GPT-4 judgment"]
    F["Aggregate metrics<br/>cover%, pos%, win_tie%"]
    G["Overall score<br/>cover × pos × win_tie"]
    
    A --> B
    B --> C
    B --> D
    A --> E
    C --> F
    D --> F
    E --> F
    F --> G
```

**Metric Formulas** (from [show_table.py:101-111]()):

| Metric | Calculation | Line Reference |
|--------|-------------|----------------|
| `cover%` | `sum(cover_ratios)/len * 100` | [show_table.py:108]() |
| `pos%` | `sum(pos_ratios)/len * 100` | [show_table.py:107]() |
| `win_tie%` | `(win_count+tie_count)/len * 100` | [show_table.py:105]() |
| `overall` | `(cover × pos × win_tie) / 10000` | [show_table.py:110]() |
| `len` | `sum(lens)/len` | [show_table.py:109]() |

**Sources**: [show_table.py:74-112](), [README.md:39-44]()

---

## Dependency Architecture

### Core Dependencies and Their Roles

```mermaid
graph TB
    A["CommonGen-Eval System"]
    
    B["vllm 0.2.6<br/>Model serving & batching"]
    C["transformers 4.36.2<br/>Model loading"]
    D["openai 0.28.0<br/>GPT-4 API client"]
    E["spacy 3.7.2<br/>NLP analysis"]
    F["datasets library<br/>HuggingFace integration"]
    G["tabulate 0.9.0<br/>Table formatting"]
    H["tenacity<br/>Retry decorator"]
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
    
    I["vllm_infer.py"]
    J["evaluate.py"]
    K["eval_utils.py:analyze_words()"]
    L["show_table.py"]
    M["eval_utils.py:retry_handler()"]
    
    B -.used by.-> I
    C -.used by.-> I
    D -.used by.-> J
    E -.used by.-> K
    F -.used by.-> I
    F -.used by.-> L
    G -.used by.-> L
    H -.used by.-> M
```

**Sources**: [README.md:48-53](), [eval_utils.py:1-14](), [show_table.py:1-4]()

---

## Extension Points

The architecture provides several extension points for adding new models or evaluation methods:

| Extension Point | Location | Mechanism |
|----------------|----------|-----------|
| **New Model Support** | [data_utils.py:9-27]() | Add conditional branch in `apply_template()` |
| **New Conversation Template** | `fastchat_conversation.py` | Add template via `get_conv_template()` |
| **New Evaluation Metrics** | [eval_utils.py:17-37]() | Extend `analyze_words()` or add new functions |
| **Custom Evaluation Judges** | [eval_utils.py:100-156]() | Modify `openai_chat_request()` model parameter |
| **Output Format Changes** | [data_utils.py:72-88]() | Modify `save_outputs()` formatting logic |
| **New Aggregation Methods** | [show_table.py:69-112]() | Add calculation loops for new metrics |

**Sources**: [data_utils.py:6-88](), [eval_utils.py:17-156](), [show_table.py:69-122]()

---

