<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/asta-bench · page 7 Evaluation Pipelines · fetched 2026-10-26 -->

# Evaluation Pipelines

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dvc.lock](dvc.lock)
- [dvc.yaml](dvc.yaml)
- [params.yaml](params.yaml)
- [scripts/log_errors.py](scripts/log_errors.py)

</details>



This page covers the automated evaluation workflow system built on DVC (Data Version Control) and the patterns for developing custom solvers. The DVC pipeline orchestrates comprehensive solver evaluations across multiple models, splits, and task configurations, while solver development patterns enable integration of diverse AI systems into the benchmark. For information about individual evaluation tasks and their implementation, see [Evaluation Tasks](#5).

## Pipeline Architecture

The evaluation pipeline system is defined in [dvc.yaml:1-489]() and uses DVC's matrix and foreach constructs to systematically evaluate multiple AI systems across standardized benchmarks. The pipeline consists of three main phases: solver execution, scoring, and result processing.

### DVC Pipeline Overview

```mermaid
graph TB
    subgraph "Solver Execution Stages"
        solve_sqa["solve_sqa<br/>Matrix: models × splits"]
        solve_elicit["solve_elicit<br/>Foreach: splits"]
        solve_storm["solve_storm<br/>Foreach: splits"]
        solve_llm["solve_llm<br/>Matrix: models × splits"]
        solve_memorized["solve_memorized<br/>Matrix: models × splits"]
        solve_futurehouse["solve_futurehouse<br/>Matrix: models × splits"]
    end
    
    subgraph "Scoring Stage"
        score_all_solvers["score_all_solvers<br/>Matrix: models × splits"]
    end
    
    subgraph "Post-processing Stages"
        log_errors["log_any_remaining_errors_and_record_scores"]
        extract_responses["extract_model_responses"]
        create_logs["create_nice_logs"]
    end
    
    subgraph "Configuration"
        params_yaml["params.yaml"]
        dvc_yaml["dvc.yaml"]
    end
    
    subgraph "Output Structure"
        solver_outputs["{split}_dvc_logs/solver_outputs/"]
        scored_outputs["{split}_dvc_logs/scored/"]
        debug_logs["{split}_dvc_logs/debug_logs/"]
        error_logs["{split}_dvc_logs/errors/"]
    end
    
    params_yaml --> solve_sqa
    params_yaml --> solve_llm
    dvc_yaml --> solve_sqa
    
    solve_sqa --> solver_outputs
    solve_elicit --> solver_outputs
    solve_storm --> solver_outputs
    solve_llm --> solver_outputs
    
    solver_outputs --> score_all_solvers
    score_all_solvers --> scored_outputs
    
    scored_outputs --> log_errors
    scored_outputs --> create_logs
    solver_outputs --> extract_responses
    
    log_errors --> error_logs
    create_logs --> debug_logs
    extract_responses --> debug_logs
```

**Sources:** [dvc.yaml:1-489](), [params.yaml:1-4]()

## Solver Execution Stages

The pipeline defines specialized stages for different solver categories, each with tailored execution parameters and output handling.

### SQA Solver Matrix Configuration

The `solve_sqa` stage demonstrates the matrix-based approach for running multiple language models:

```mermaid
graph LR
    subgraph "solve_sqa Matrix"
        matrix_def["Matrix Definition<br/>dvc.yaml:14-44"]
        models["Models:<br/>claude-3.7, gemini-2.5-pro<br/>claude-4.0, o3_high"]
        splits["Splits:<br/>dev, test"]
        
        matrix_def --> models
        matrix_def --> splits
    end
    
    subgraph "Execution Command Template"
        inspect_eval["inspect eval<br/>astabench/evals/sqa/task.py@sqa"]
        solver_param["--solver<br/>astabench/solvers/sqa/sqa.py@sqa_solver"]
        model_param["-S completion_model=${item.model}"]
        split_param["-T split=${item.split}"]
        
        inspect_eval --> solver_param
        solver_param --> model_param
        model_param --> split_param
    end
    
    subgraph "Output Management"
        log_pattern["INSPECT_EVAL_LOG_FILE_PATTERN<br/>task_sqa_solver_sqa_${item.model}"]
        output_file["${item.split}_dvc_logs/solver_outputs/<br/>task_sqa_solver_sqa_${item.model}.eval"]
        
        log_pattern --> output_file
    end
    
    models --> inspect_eval
    splits --> split_param
```

**Sources:** [dvc.yaml:14-44](), [dvc.yaml:25-38]()

### LLM Solver Configuration with Advanced Parameters

The `solve_llm` stage shows complex parameter handling for different model types:

```mermaid
graph TB
    subgraph "LLM Model Matrix"
        llm_defaults["llm_defaults anchor<br/>dvc.yaml:9-11"]
        model_configs["Model Configurations<br/>dvc.yaml:198-244"]
        
        subgraph "Model Examples"
            o4_mini["openai/o4-mini<br/>--reasoning-effort high<br/>--reasoning-tokens 8192"]
            claude4_thinking["anthropic/claude-sonnet-4<br/>--reasoning-tokens 8192<br/>suffix: -thinking"]
            gemini["google/gemini-2.5-pro-preview<br/>default args"]
        end
        
        llm_defaults --> model_configs
        model_configs --> o4_mini
        model_configs --> claude4_thinking
        model_configs --> gemini
    end
    
    subgraph "Execution Pattern"
        solver_cmd["astabench/solvers/sqa/<br/>formatted_llm.py@formatted_solver"]
        model_args["--model ${item.model.llm_name}<br/>${item.model.llm_args}"]
        output_naming["task_sqa_solver_<br/>${item.model.llm_name}${item.model.suffix}.eval"]
        
        solver_cmd --> model_args
        model_args --> output_naming
    end
    
    model_configs --> solver_cmd
```

**Sources:** [dvc.yaml:196-244](), [dvc.yaml:9-11](), [dvc.yaml:224-238]()

## Scoring and Post-processing

### Unified Scoring Stage

The `score_all_solvers` stage processes all solver outputs through a unified scoring framework:

```mermaid
graph TB
    subgraph "Scoring Matrix Configuration"
        solver_list["Solver Categories<br/>dvc.yaml:310-353"]
        
        subgraph "Retrieverless Solvers"
            retrieverless["openai/o4-mini<br/>anthropic/claude-sonnet-4<br/>google/gemini-2.5-pro<br/>is_retrieverless: true"]
        end
        
        subgraph "SQA Solvers"
            sqa_solvers["sqa_claude-3.7<br/>sqa_gemini-2.5-pro<br/>sqa_o3_high<br/>is_retrieverless: false"]
        end
        
        subgraph "Strong Baselines"
            baselines["elicit, storm, scispace<br/>fhouse_crow, fhouse_falcon<br/>openai_deep_research"]
        end
        
        solver_list --> retrieverless
        solver_list --> sqa_solvers
        solver_list --> baselines
    end
    
    subgraph "Scoring Process"
        copy_step["cp ${split}_dvc_logs/solver_outputs/<br/>task_sqa_solver_${model}.eval"]
        score_cmd["inspect score --overwrite<br/>--scorer astabench/evals/sqa/task.py@score_all"]
        scorer_params["-S scorer_model=${scorer_model}<br/>-S is_retrieverless=${is_retrieverless}"]
        
        copy_step --> score_cmd
        score_cmd --> scorer_params
    end
    
    solver_list --> copy_step
```

**Sources:** [dvc.yaml:308-376](), [dvc.yaml:358-368]()

### Post-processing Pipeline

```mermaid
graph LR
    subgraph "Error Analysis"
        log_errors_stage["log_any_remaining_errors_and_record_scores"]
        error_script["scripts/log_errors.py"]
        error_outputs["${split}_dvc_logs/errors/<br/>task_sqa_solver_${model}.md"]
        
        log_errors_stage --> error_script
        error_script --> error_outputs
    end
    
    subgraph "Response Extraction"
        extract_stage["extract_model_responses"]
        extract_script["scripts/extract_model_responses.py"]
        response_csv["${split}_dvc_logs/model_responses/<br/>task_sqa_solver_${model}_responses.csv"]
        
        extract_stage --> extract_script
        extract_script --> response_csv
    end
    
    subgraph "Debug Log Creation"
        debug_stage["create_nice_logs"]
        debug_script["scripts/create_debug_logs.py"]
        debug_files["rubric_eval.csv<br/>citation_eval.csv<br/>answer_precision_eval.csv"]
        
        debug_stage --> debug_script
        debug_script --> debug_files
    end
    
    scored_data["${split}_dvc_logs/scored/"] --> log_errors_stage
    scored_data --> debug_stage
    solver_data["${split}_dvc_logs/solver_outputs/"] --> extract_stage
```

**Sources:** [dvc.yaml:378-414](), [dvc.yaml:415-448](), [dvc.yaml:450-489]()

## Configuration Management

### Parameter System

The pipeline uses a centralized parameter system defined in `params.yaml`:

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `scorer_model` | `google/gemini-2.5-flash` | Model used for scoring evaluations |
| `sqa_scorer_version` | `may-23-2025` | Version identifier for SQA scoring logic |
| `sqa_solver_version` | `may-23-2025` | Version identifier for SQA solver logic |
| `limit` | `1000` | Maximum number of samples to evaluate |

**Sources:** [params.yaml:1-4]()

### Variable and Matrix Definitions

```mermaid
graph TB
    subgraph "Variable Anchors"
        llm_defaults_anchor["&llm_defaults<br/>llm_args: ''<br/>suffix: ''"]
    end
    
    subgraph "Matrix Usage Patterns"
        simple_matrix["Simple Matrix:<br/>model × split"]
        complex_matrix["Complex Matrix with Structs:<br/>model configs with args"]
        foreach_pattern["Foreach Pattern:<br/>splits only"]
        
        subgraph "Matrix Examples"
            solve_sqa_matrix["solve_sqa:<br/>models: [claude-3.7, gemini-2.5-pro]<br/>splits: [dev, test]"]
            solve_llm_matrix["solve_llm:<br/>model structs with llm_name, args, suffix<br/>splits: [dev, test]"]
            solve_elicit_foreach["solve_elicit:<br/>foreach: [dev, test]"]
        end
    end
    
    llm_defaults_anchor --> complex_matrix
    simple_matrix --> solve_sqa_matrix
    complex_matrix --> solve_llm_matrix
    foreach_pattern --> solve_elicit_foreach
```

**Sources:** [dvc.yaml:7-11](), [dvc.yaml:14-24](), [dvc.yaml:198-221](), [dvc.yaml:46-51]()

## Output Directory Structure

The pipeline generates a structured output hierarchy for each data split:

```mermaid
graph TB
    subgraph "Output Directory Structure"
        root_split["{split}_dvc_logs/"]
        
        subgraph "Primary Outputs"
            solver_outputs["solver_outputs/<br/>task_sqa_solver_{model}.eval"]
            scored_outputs["scored/<br/>task_sqa_solver_{model}.eval"]
        end
        
        subgraph "Analysis Outputs"
            error_outputs["errors/<br/>task_sqa_solver_{model}.md"]
            score_outputs["scores/<br/>task_sqa_solver_{model}.md"]
            response_outputs["model_responses/<br/>task_sqa_solver_{model}_responses.csv"]
        end
        
        subgraph "Debug Outputs"
            debug_rubric["debug_logs/<br/>task_sqa_solver_{model}_rubric_eval.csv"]
            debug_citation["debug_logs/<br/>task_sqa_solver_{model}_citation_eval.csv"]
            debug_precision["debug_logs/<br/>task_sqa_solver_{model}_answer_precision_eval.csv"]
        end
        
        root_split --> solver_outputs
        root_split --> scored_outputs
        root_split --> error_outputs
        root_split --> score_outputs
        root_split --> response_outputs
        root_split --> debug_rubric
        root_split --> debug_citation
        root_split --> debug_precision
    end
```

**Sources:** [dvc.yaml:43-44](), [dvc.yaml:374-376](), [dvc.yaml:411-413](), [dvc.yaml:447-448](), [dvc.yaml:485-488]()

## Error Handling and Retry Logic

The pipeline implements robust error handling through several mechanisms:

### Retry Configuration

Most solver stages include `--retry-on-error=10` parameters to handle transient failures. The error logging system captures and reports unresolved issues:

```python
# Error collection pattern from scripts/log_errors.py
error_samples = [
    {
        "id": sample.id,
        "question": sample.metadata["initial_prompt"],
        "error": json.loads(sample.error.model_dump_json())["traceback"],
    }
    for sample in log.samples
    if sample.error is not None
]
```

**Sources:** [dvc.yaml:35](), [scripts/log_errors.py:24-32]()

## Common Pipeline Workflows

### Running the Complete Pipeline

```bash
# Run all stages for development split
dvc repro

# Run specific solver stage
dvc repro solve_sqa@claude-3.7-dev

# Run scoring for specific model
dvc repro score_all_solvers@sqa_claude-3.7-dev
```

### Pipeline State Management

DVC tracks pipeline state through dependency graphs and checksums stored in [dvc.lock:1-1500](). Each stage defines:

- **Dependencies:** Input files and parameter values
- **Outputs:** Generated files with content hashes
- **Commands:** Exact command executed with resolved parameters

**Sources:** [dvc.lock:1-50](), [dvc.yaml:39-44](), [dvc.yaml:369-376]()

---

