<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/RULER · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [scripts/run.sh](scripts/run.sh)

</details>



## Purpose and Scope

This page provides a high-level architectural overview of the RULER framework, describing the major components, their responsibilities, and how they interact to perform long-context LLM evaluation. RULER operates as a sequential pipeline that generates synthetic benchmark data, obtains model predictions, and computes evaluation metrics across varying sequence lengths.

For detailed information about specific subsystems, see:
- Pipeline execution flow: [Pipeline Overview](#2.1)
- Data generation mechanics: [Data Generation Pipeline](#2.2)
- Model serving and inference: [Inference and Serving](#2.3)
- Metrics and evaluation: [Evaluation System](#2.4)
- Task-specific implementations: [Benchmark Tasks](#3)
- Configuration details: [Configuration System](#4)

## Architectural Layers

RULER is organized into five distinct layers that separate concerns and enable modular development:

```mermaid
graph TB
    subgraph ConfigLayer["Configuration Layer"]
        config_models["config_models.sh<br/>MODEL_SELECT()"]
        config_tasks["config_tasks.sh<br/>TASKS array"]
        synthetic_yaml["synthetic.yaml<br/>Task parameters"]
        constants["constants.py<br/>Templates & metrics"]
    end
    
    subgraph OrchLayer["Orchestration Layer"]
        run_sh["run.sh<br/>Main pipeline controller<br/>Lines 88-132: Main loop"]
    end
    
    subgraph DataLayer["Data Generation Layer"]
        prepare_py["prepare.py<br/>Task dispatcher"]
        niah_py["niah.py"]
        vt_py["variable_tracking.py"]
        cwe_py["common_words_extraction.py"]
        fwe_py["freq_words_extraction.py"]
        qa_py["qa.py"]
    end
    
    subgraph ServingLayer["Model Serving Layer"]
        serve_vllm["serve_vllm.py"]
        serve_trt["serve_trt.py"]
        sglang["sglang server"]
        model_wrap["model_wrappers.py<br/>HuggingFaceModel<br/>MambaModel"]
        client_wrap["client_wrappers.py<br/>OpenAIClient<br/>GeminiClient"]
    end
    
    subgraph InferenceLayer["Inference Layer"]
        call_api["call_api.py<br/>get_llm()<br/>process_batch()"]
    end
    
    subgraph EvalLayer["Evaluation Layer"]
        evaluate_py["evaluate.py<br/>Metrics computation"]
    end
    
    config_models --> run_sh
    config_tasks --> run_sh
    synthetic_yaml --> prepare_py
    constants --> prepare_py
    
    run_sh --> prepare_py
    run_sh --> call_api
    run_sh --> evaluate_py
    
    prepare_py --> niah_py
    prepare_py --> vt_py
    prepare_py --> cwe_py
    prepare_py --> fwe_py
    prepare_py --> qa_py
    
    run_sh -.launches.-> serve_vllm
    run_sh -.launches.-> serve_trt
    run_sh -.launches.-> sglang
    
    call_api --> model_wrap
    call_api --> client_wrap
    client_wrap --> serve_vllm
    client_wrap --> serve_trt
    client_wrap --> sglang
    
    style run_sh fill:#f9f9f9,stroke:#333,stroke-width:3px
    style prepare_py fill:#f9f9f9,stroke:#333,stroke-width:2px
    style call_api fill:#f9f9f9,stroke:#333,stroke-width:2px
    style evaluate_py fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [scripts/run.sh](), [scripts/config_models.sh](), [scripts/config_tasks.sh](), [scripts/synthetic.yaml](), [scripts/data/synthetic/constants.py](), [scripts/data/prepare.py](), [scripts/pred/call_api.py](), [scripts/eval/evaluate.py]()

### Layer Responsibilities

| Layer | Responsibility | Key Components |
|-------|---------------|----------------|
| **Configuration** | Define models, tasks, and parameters | `config_models.sh`, `config_tasks.sh`, `synthetic.yaml` |
| **Orchestration** | Control execution flow and coordinate components | `run.sh` |
| **Data Generation** | Create synthetic benchmark samples | `prepare.py`, task-specific generators |
| **Model Serving** | Provide model inference backends | `serve_vllm.py`, `serve_trt.py`, `sglang`, API clients |
| **Inference** | Generate predictions from models | `call_api.py`, wrappers in `model_wrappers.py`, `client_wrappers.py` |
| **Evaluation** | Compute metrics and determine effective length | `evaluate.py`, metrics in `eval/synthetic/constants.py` |

**Sources:** [scripts/run.sh:1-133](), [scripts/data/prepare.py](), [scripts/pred/call_api.py](), [scripts/eval/evaluate.py]()

## Core Component Architecture

The following diagram maps system components to their code implementations:

```mermaid
graph TB
    subgraph Orchestrator["Main Orchestrator"]
        run_sh_main["run.sh<br/>Lines 88-132: Main execution loop<br/>- Iterates SEQ_LENGTHS array<br/>- Iterates TASKS array<br/>- Coordinates 3 stages"]
    end
    
    subgraph ConfigSystem["Configuration System"]
        MODEL_SELECT["MODEL_SELECT function<br/>config_models.sh:Lines 16-200<br/>Returns: MODEL_PATH:TEMPLATE:FRAMEWORK:TOKENIZER"]
        TASKS_ARRAY["TASKS array<br/>config_tasks.sh<br/>Defines task list per benchmark"]
        SEQ_LENGTHS["SEQ_LENGTHS array<br/>config_tasks.sh<br/>e.g., 4096, 8192, 16384, 32768, 65536, 131072"]
    end
    
    subgraph DataGeneration["Data Generation"]
        prepare_main["prepare.py main()<br/>Lines 100-150<br/>- Loads task config from synthetic.yaml<br/>- Dispatches to task generators"]
        task_generators["Task Generators<br/>- niah.py: generate_input_output()<br/>- variable_tracking.py: generate_input_output()<br/>- common_words_extraction.py: generate_input_output()<br/>- freq_words_extraction.py: generate_input_output()<br/>- qa.py: generate_input_output()"]
        manifest_utils["manifest_utils.py<br/>write_manifest()<br/>Writes JSONL format"]
    end
    
    subgraph InferenceSystem["Inference System"]
        get_llm["call_api.py<br/>get_llm() factory<br/>Lines 20-80<br/>Returns model/client instance"]
        model_wrappers["model_wrappers.py<br/>- HuggingFaceModel<br/>- MambaModel<br/>process_batch() method"]
        client_wrappers["client_wrappers.py<br/>- VLLMClient<br/>- TRTLLMClient<br/>- SGLClient<br/>- OpenAIClient<br/>- GeminiClient<br/>process_batch() method"]
    end
    
    subgraph ServingBackends["Serving Backends"]
        vllm_server["serve_vllm.py<br/>Lines 62-68: vLLM launch<br/>--tensor-parallel-size GPUS"]
        trt_server["serve_trt.py<br/>Lines 70-73: TensorRT launch<br/>--model_path MODEL_PATH"]
        sglang_server["sglang launch_server<br/>Lines 75-83: SGLang launch<br/>--enable-flashinfer"]
    end
    
    subgraph EvaluationSystem["Evaluation System"]
        evaluate_main["evaluate.py main()<br/>Loads predictions JSONL<br/>Computes task metrics"]
        task_metrics["eval/synthetic/constants.py<br/>TASK_METRICS dict<br/>Maps task -> scoring function"]
    end
    
    run_sh_main -->|"Reads config"| MODEL_SELECT
    run_sh_main -->|"Reads tasks"| TASKS_ARRAY
    run_sh_main -->|"Iterates"| SEQ_LENGTHS
    
    run_sh_main -->|"1. Generate data<br/>Lines 98-107"| prepare_main
    run_sh_main -->|"2. Get predictions<br/>Lines 110-121"| get_llm
    run_sh_main -->|"3. Evaluate<br/>Lines 127-129"| evaluate_main
    
    prepare_main --> task_generators
    task_generators --> manifest_utils
    
    get_llm --> model_wrappers
    get_llm --> client_wrappers
    
    run_sh_main -."|Launches server<br/>Lines 62-84"|.-> vllm_server
    run_sh_main -."|Launches server"| .-> trt_server
    run_sh_main -."|Launches server"|.-> sglang_server
    
    client_wrappers -->|"HTTP requests"| vllm_server
    client_wrappers -->|"HTTP requests"| trt_server
    client_wrappers -->|"HTTP requests"| sglang_server
    
    evaluate_main --> task_metrics
```

**Sources:** [scripts/run.sh:88-132](), [scripts/config_models.sh:16-200](), [scripts/config_tasks.sh](), [scripts/data/prepare.py:100-150](), [scripts/pred/call_api.py:20-80](), [scripts/pred/model_wrappers.py](), [scripts/pred/client_wrappers.py](), [scripts/eval/evaluate.py](), [scripts/eval/synthetic/constants.py]()

## Data Flow Architecture

The following diagram shows how data flows through the system from configuration to results:

```mermaid
graph LR
    subgraph Inputs["Input Artifacts"]
        config_files["Config Files<br/>- MODEL_PATH<br/>- TASKS array<br/>- synthetic.yaml"]
        external_data["External Data<br/>- Paul Graham essays<br/>- SQuAD JSON<br/>- HotpotQA JSON"]
    end
    
    subgraph Stage1["Stage 1: Data Generation"]
        prepare["prepare.py<br/>Dispatcher"]
        task_gen["Task Generator<br/>generate_input_output()"]
        data_jsonl["data/TASK/validation.jsonl<br/>{index, input, outputs, length}"]
    end
    
    subgraph Stage2["Stage 2: Prediction Generation"]
        call_api_load["call_api.py<br/>Load data JSONL"]
        llm_instance["LLM Instance<br/>process_batch()"]
        pred_jsonl["pred/TASK/validation.jsonl<br/>{index, input, outputs, pred}"]
    end
    
    subgraph Stage3["Stage 3: Evaluation"]
        eval_load["evaluate.py<br/>Load pred JSONL"]
        metrics_compute["Compute metrics<br/>TASK_METRICS[task]"]
        results["Results<br/>- Task scores<br/>- Effective length<br/>- Performance table"]
    end
    
    config_files --> prepare
    external_data --> task_gen
    prepare --> task_gen
    task_gen --> data_jsonl
    
    data_jsonl --> call_api_load
    call_api_load --> llm_instance
    llm_instance --> pred_jsonl
    
    pred_jsonl --> eval_load
    eval_load --> metrics_compute
    metrics_compute --> results
    
    style data_jsonl fill:#f9f9f9,stroke:#333,stroke-width:2px
    style pred_jsonl fill:#f9f9f9,stroke:#333,stroke-width:2px
    style results fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [scripts/run.sh:98-129](), [scripts/data/prepare.py](), [scripts/pred/call_api.py](), [scripts/eval/evaluate.py]()

### Directory Structure

The pipeline creates a consistent directory structure for each model, benchmark, and sequence length:

```
ROOT_DIR/
└── MODEL_NAME/
    └── BENCHMARK/
        └── MAX_SEQ_LENGTH/
            ├── data/
            │   └── TASK/
            │       └── validation.jsonl
            └── pred/
                └── TASK/
                    └── validation.jsonl
```

**Sources:** [scripts/run.sh:91-95]()

## Execution Flow

The system executes as a nested loop controlled by `run.sh`:

```mermaid
sequenceDiagram
    participant User
    participant run.sh
    participant config
    participant Server
    participant prepare.py
    participant Task
    participant call_api.py
    participant LLM
    participant evaluate.py
    
    User->>run.sh: bash run.sh MODEL_NAME BENCHMARK
    activate run.sh
    
    run.sh->>config: Load MODEL_SELECT()
    config-->>run.sh: MODEL_PATH, FRAMEWORK, TOKENIZER
    
    run.sh->>config: Load TASKS array
    config-->>run.sh: [task1, task2, ..., taskN]
    
    opt If local serving framework
        run.sh->>Server: Launch server (vllm/trt/sglang)
        Note over Server: Server runs throughout pipeline
    end
    
    loop For each MAX_SEQ_LENGTH in SEQ_LENGTHS
        loop For each TASK in TASKS
            run.sh->>prepare.py: Generate data
            activate prepare.py
            prepare.py->>Task: Call generate_input_output()
            Task-->>prepare.py: Samples
            prepare.py-->>run.sh: data/TASK/validation.jsonl
            deactivate prepare.py
            
            run.sh->>call_api.py: Generate predictions
            activate call_api.py
            call_api.py->>LLM: process_batch()
            LLM-->>call_api.py: Predictions
            call_api.py-->>run.sh: pred/TASK/validation.jsonl
            deactivate call_api.py
        end
        
        run.sh->>evaluate.py: Compute metrics for all tasks
        activate evaluate.py
        evaluate.py-->>run.sh: Performance scores
        deactivate evaluate.py
    end
    
    run.sh-->>User: Complete benchmark
    deactivate run.sh
```

**Sources:** [scripts/run.sh:88-132]()

### Key Control Flow Patterns

| Pattern | Implementation | Purpose |
|---------|----------------|---------|
| **Outer Loop** | `for MAX_SEQ_LENGTH in "${SEQ_LENGTHS[@]}"` [run.sh:89]() | Test multiple context lengths |
| **Inner Loop** | `for TASK in "${TASKS[@]}"` [run.sh:97]() | Evaluate all tasks at each length |
| **Sequential Stages** | Lines 98→110→127 [run.sh]() | Data generation → Inference → Evaluation |
| **Conditional Serving** | `if [ "$MODEL_FRAMEWORK" == "vllm" ]` [run.sh:62]() | Launch appropriate server |
| **Factory Pattern** | `get_llm()` in [call_api.py]() | Abstract backend differences |

**Sources:** [scripts/run.sh:62-84](), [scripts/run.sh:88-132](), [scripts/pred/call_api.py]()

## Model Serving Architecture

RULER supports seven distinct inference backends through a unified interface:

```mermaid
graph TB
    subgraph ClientLayer["Client Layer - call_api.py"]
        get_llm_factory["get_llm() Factory Function<br/>Maps framework → implementation"]
    end
    
    subgraph LocalServers["Local Serving Frameworks"]
        VLLMClient["VLLMClient<br/>client_wrappers.py<br/>HTTP PUT to port 5000"]
        TRTLLMClient["TRTLLMClient<br/>client_wrappers.py<br/>HTTP PUT to port 5000"]
        SGLClient["SGLClient<br/>client_wrappers.py<br/>HTTP PUT to port 5000"]
        
        vllm_proc["vLLM Process<br/>serve_vllm.py<br/>PagedAttention"]
        trt_proc["TensorRT-LLM Process<br/>serve_trt.py<br/>Pre-built engines"]
        sglang_proc["SGLang Process<br/>sglang.launch_server<br/>FlashInfer enabled"]
    end
    
    subgraph DirectModels["Direct Model Loading"]
        HFModel["HuggingFaceModel<br/>model_wrappers.py<br/>AutoModelForCausalLM<br/>flash_attention_2"]
        MambaModel["MambaModel<br/>model_wrappers.py<br/>mamba_ssm<br/>gpt-neox tokenizer"]
    end
    
    subgraph ExternalAPIs["External API Services"]
        OpenAIClient["OpenAIClient<br/>client_wrappers.py<br/>OpenAI/Azure endpoints"]
        GeminiClient["GeminiClient<br/>client_wrappers.py<br/>Google Generative AI"]
    end
    
    get_llm_factory -->|"framework='vllm'"| VLLMClient
    get_llm_factory -->|"framework='trtllm'"| TRTLLMClient
    get_llm_factory -->|"framework='sglang'"| SGLClient
    get_llm_factory -->|"framework='hf'"| HFModel
    get_llm_factory -->|"framework='mamba'"| MambaModel
    get_llm_factory -->|"framework='openai'"| OpenAIClient
    get_llm_factory -->|"framework='gemini'"| GeminiClient
    
    VLLMClient -->|"HTTP requests"| vllm_proc
    TRTLLMClient -->|"HTTP requests"| trt_proc
    SGLClient -->|"HTTP requests"| sglang_proc
```

**Sources:** [scripts/pred/call_api.py](), [scripts/pred/client_wrappers.py](), [scripts/pred/model_wrappers.py](), [scripts/pred/serve_vllm.py](), [scripts/pred/serve_trt.py]()

### Backend Comparison

| Backend | Framework Value | Wrapper Class | Launch Method |
|---------|----------------|---------------|---------------|
| **vLLM** | `vllm` | `VLLMClient` | `serve_vllm.py` [run.sh:62-68]() |
| **TensorRT-LLM** | `trtllm` | `TRTLLMClient` | `serve_trt.py` [run.sh:70-73]() |
| **SGLang** | `sglang` | `SGLClient` | `sglang.launch_server` [run.sh:75-83]() |
| **HuggingFace** | `hf` | `HuggingFaceModel` | Direct loading |
| **Mamba** | `mamba` | `MambaModel` | Direct loading |
| **OpenAI** | `openai` | `OpenAIClient` | API calls |
| **Gemini** | `gemini` | `GeminiClient` | API calls |

**Sources:** [scripts/run.sh:62-84](), [scripts/pred/call_api.py](), [scripts/pred/client_wrappers.py](), [scripts/pred/model_wrappers.py]()

## Shared Utility Subsystem

All components rely on shared utilities for cross-cutting concerns:

```mermaid
graph TB
    subgraph CoreComponents["Core Pipeline Components"]
        prepare["prepare.py"]
        task_gens["Task Generators<br/>niah.py, vt.py, etc."]
        call_api["call_api.py"]
        evaluate["evaluate.py"]
    end
    
    subgraph Utilities["Utility Modules"]
        tokenizer_py["tokenizer.py<br/>- get_tokenizer()<br/>- nemo/hf/openai/gemini types<br/>- Unified count_tokens()"]
        
        template_py["template.py<br/>- Templates dict<br/>- 11 model templates<br/>- apply_template()"]
        
        manifest_utils["manifest_utils.py<br/>- write_manifest()<br/>- read_manifest()<br/>- JSONL I/O"]
        
        constants_data["data/synthetic/constants.py<br/>- TASKS dict<br/>- Task templates<br/>- tokens_to_generate<br/>- answer_prefix"]
        
        constants_eval["eval/synthetic/constants.py<br/>- TASK_METRICS dict<br/>- Scoring functions"]
    end
    
    prepare --> tokenizer_py
    prepare --> template_py
    prepare --> constants_data
    
    task_gens --> tokenizer_py
    task_gens --> manifest_utils
    task_gens --> constants_data
    
    call_api --> tokenizer_py
    call_api --> template_py
    
    evaluate --> constants_eval
    evaluate --> manifest_utils
```

**Sources:** [scripts/data/tokenizer.py](), [scripts/data/template.py](), [scripts/data/manifest_utils.py](), [scripts/data/synthetic/constants.py](), [scripts/eval/synthetic/constants.py]()

### Utility Module Responsibilities

| Module | Key Functions | Purpose |
|--------|---------------|---------|
| **tokenizer.py** | `get_tokenizer()`, `count_tokens()` | Multi-framework tokenization (NeMo, HuggingFace, OpenAI, Gemini) |
| **template.py** | `apply_template()`, `Templates` dict | Model-specific prompt formatting (11 templates) |
| **manifest_utils.py** | `write_manifest()`, `read_manifest()` | Standardized JSONL file I/O |
| **constants.py (data)** | `TASKS` dict | Task metadata: templates, token limits, answer prefixes |
| **constants.py (eval)** | `TASK_METRICS` dict | Task-specific scoring functions |

**Sources:** [scripts/data/tokenizer.py](), [scripts/data/template.py](), [scripts/data/manifest_utils.py](), [scripts/data/synthetic/constants.py](), [scripts/eval/synthetic/constants.py]()

## Key Design Principles

### 1. Configuration-Driven Architecture

All system behavior is controlled through configuration files rather than code modification:

- **Model Configuration:** `config_models.sh` `MODEL_SELECT()` function maps model names to paths, frameworks, and tokenizers
- **Task Selection:** `config_tasks.sh` defines task arrays per benchmark
- **Task Complexity:** `synthetic.yaml` specifies parameters controlling task difficulty
- **Templates:** `template.py` `Templates` dict defines prompt formats

**Sources:** [scripts/config_models.sh](), [scripts/config_tasks.sh](), [scripts/synthetic.yaml](), [scripts/data/template.py]()

### 2. Factory Pattern for Backend Abstraction

The `get_llm()` factory function [call_api.py]() provides a uniform interface across all seven inference backends. Every implementation provides a `process_batch()` method with consistent semantics:

```python
llm = get_llm(server_type, model_name_or_path, ...)
predictions = llm.process_batch(inputs, **generation_kwargs)
```

**Sources:** [scripts/pred/call_api.py]()

### 3. Sequential Processing Model

The nested loop structure [run.sh:88-132]() ensures:
- Data is generated once per (task, sequence_length) pair
- Predictions are generated immediately after data generation
- Evaluation occurs after all tasks complete at a given sequence length
- Results are incrementally available as the pipeline progresses

**Sources:** [scripts/run.sh:88-132]()

### 4. Tokenizer-Aware Generation

All task generators accept a tokenizer instance and use binary search to maximize context utilization while respecting `max_seq_length` constraints. This ensures samples precisely fit within model context windows.

**Sources:** [scripts/data/prepare.py](), [scripts/data/synthetic/niah.py](), [scripts/data/synthetic/variable_tracking.py](), [scripts/data/synthetic/common_words_extraction.py](), [scripts/data/synthetic/freq_words_extraction.py](), [scripts/data/synthetic/qa.py]()

### 5. Standardized Data Format

All pipeline stages communicate through JSONL files with consistent schema:

**Data Generation Output:**
```json
{
  "index": 0,
  "input": "prompt text...",
  "outputs": ["expected answer"],
  "length": 4096
}
```

**Prediction Output:**
```json
{
  "index": 0,
  "input": "prompt text...",
  "outputs": ["expected answer"],
  "pred": "model prediction"
}
```

**Sources:** [scripts/data/manifest_utils.py](), [scripts/data/prepare.py](), [scripts/pred/call_api.py]()

---

