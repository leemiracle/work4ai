<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/agent-baselines · page 3 Evaluation Pipeline · fetched 2026-10-26 -->

# Evaluation Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [dvc.lock](dvc.lock)
- [dvc.yaml](dvc.yaml)
- [params.yaml](params.yaml)
- [pyproject.toml](pyproject.toml)

</details>



This document covers the DVC-based evaluation pipeline system used for running reproducible, large-scale agent benchmarks in the agent-baselines repository. The pipeline orchestrates evaluation of multiple solver implementations across different models, datasets, and configurations, with automatic caching, scoring, and result management.

For information about individual agent implementations, see [Agent Architecture](#4). For details on running simple evaluations without DVC, see [Running Evaluations](#3.2).

## Pipeline Architecture

The evaluation pipeline is built on DVC (Data Version Control) and consists of multiple interconnected stages that process solver outputs through evaluation, scoring, and post-processing steps. The pipeline supports matrix execution to run hundreds of solver/model/split combinations in parallel.

### Core Pipeline Flow

```mermaid
graph TD
    PARAMS["params.yaml<br/>Pipeline Configuration"]
    DVC_YAML["dvc.yaml<br/>Stage Definitions"]
    
    subgraph "Solver Execution Stages"
        SOLVE_SQA["solve_sqa<br/>SQA Solver Matrix"]
        SOLVE_LLM["solve_llm<br/>Retrieverless LLM Matrix"]
        SOLVE_STORM["solve_storm<br/>STORM Solver"]
        SOLVE_ELICIT["solve_elicit<br/>Elicit Memorized"]
        SOLVE_OTHER["solve_*<br/>Other Solvers"]
    end
    
    subgraph "Evaluation & Scoring"
        SCORE_ALL["score_all_solvers<br/>Universal Scoring Stage"]
    end
    
    subgraph "Post-Processing Stages"
        LOG_ERRORS["log_any_remaining_errors_and_record_scores<br/>Error Collection"]
        EXTRACT_RESP["extract_model_responses<br/>Response Extraction"]
        CREATE_LOGS["create_nice_logs<br/>Debug Log Generation"]
    end
    
    subgraph "Output Artifacts"
        SOLVER_OUTPUTS["{split}_dvc_logs/solver_outputs/<br/>Raw Evaluation Results"]
        SCORED_OUTPUTS["{split}_dvc_logs/scored/<br/>Scored Results"]
        ERROR_LOGS["{split}_dvc_logs/errors/<br/>Error Reports"]
        DEBUG_LOGS["{split}_dvc_logs/debug_logs/<br/>Debug CSVs"]
        RESPONSES["{split}_dvc_logs/model_responses/<br/>Response CSVs"]
    end
    
    PARAMS --> DVC_YAML
    DVC_YAML --> SOLVE_SQA
    DVC_YAML --> SOLVE_LLM
    DVC_YAML --> SOLVE_STORM
    DVC_YAML --> SOLVE_ELICIT
    DVC_YAML --> SOLVE_OTHER
    
    SOLVE_SQA --> SOLVER_OUTPUTS
    SOLVE_LLM --> SOLVER_OUTPUTS
    SOLVE_STORM --> SOLVER_OUTPUTS
    SOLVE_ELICIT --> SOLVER_OUTPUTS
    SOLVE_OTHER --> SOLVER_OUTPUTS
    
    SOLVER_OUTPUTS --> SCORE_ALL
    SCORE_ALL --> SCORED_OUTPUTS
    
    SCORED_OUTPUTS --> LOG_ERRORS
    SCORED_OUTPUTS --> CREATE_LOGS
    SOLVER_OUTPUTS --> EXTRACT_RESP
    
    LOG_ERRORS --> ERROR_LOGS
    CREATE_LOGS --> DEBUG_LOGS
    EXTRACT_RESP --> RESPONSES
```

Sources: [dvc.yaml:1-489](), [README.md:51-116]()

### Matrix Execution System

The pipeline uses DVC's matrix functionality to execute evaluations across multiple dimensions simultaneously:

```mermaid
graph LR
    subgraph "Matrix Dimensions"
        MODELS["Models<br/>claude-3.7, gemini-2.5-pro<br/>claude-4.0, o3_high"]
        SPLITS["Splits<br/>dev, test"]
        SOLVERS["Solver Types<br/>sqa, llm, storm<br/>elicit, futurehouse"]
    end
    
    subgraph "Generated Stages"
        STAGE1["solve_sqa@claude-3.7-dev"]
        STAGE2["solve_sqa@claude-3.7-test"]  
        STAGE3["solve_sqa@gemini-2.5-pro-dev"]
        STAGE4["solve_sqa@gemini-2.5-pro-test"]
        STAGE_N["... 400+ combinations"]
    end
    
    MODELS --> STAGE1
    SPLITS --> STAGE1
    SOLVERS --> STAGE1
    
    MODELS --> STAGE2
    SPLITS --> STAGE2
    SOLVERS --> STAGE2
    
    MODELS --> STAGE3
    SPLITS --> STAGE3
    SOLVERS --> STAGE3
    
    MODELS --> STAGE4
    SPLITS --> STAGE4
    SOLVERS --> STAGE4
    
    STAGE_N
```

Sources: [dvc.yaml:14-44](), [dvc.yaml:197-244](), [dvc.yaml:309-376]()

## Configuration System

### Parameter Management

The pipeline uses `params.yaml` for centralized configuration of evaluation parameters:

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `scorer_model` | Model used for scoring evaluations | `google/gemini-2.5-flash` |
| `sqa_scorer_version` | Version tag for scorer changes | `may-23-2025` |
| `sqa_solver_version` | Version tag for solver changes | `may-23-2025` |
| `limit` | Number of samples to evaluate | `1000` |

Sources: [params.yaml:1-5]()

### Stage Configuration Patterns

Each solver type has its own stage configuration with specific command patterns:

**SQA Solver Stage Example:**
```yaml
solve_sqa:
  matrix:
    model: [claude-3.7, gemini-2.5-pro, claude-4.0, o3_high]
    split: [dev, test]
  cmd: |
    INSPECT_EVAL_LOG_FILE_PATTERN=task_sqa_solver_sqa_${item.model}
    uv run --extra sqa
    inspect eval astabench/evals/sqa/task.py@sqa
    --solver agent_baselines/solvers/sqa/sqa.py@sqa_solver
    -S completion_model=${item.model}
    --limit=${limit}
```

Sources: [dvc.yaml:14-44]()

**Retrieverless LLM Stage Example:**
```yaml
solve_llm:
  matrix:
    model:
      - llm_name: openai/o4-mini
        llm_args: "--reasoning-effort high --reasoning-tokens 8192"
      - llm_name: anthropic/claude-sonnet-4-20250514
        llm_args: "--reasoning-tokens 8192"
```

Sources: [dvc.yaml:197-244]()

## Pipeline Stages

### Solver Execution Stages

The pipeline defines multiple solver execution stages, each targeting different agent types:

| Stage Name | Purpose | Solver Path | Extra Dependencies |
|------------|---------|-------------|-------------------|
| `solve_sqa` | SQA retrieval-augmented agents | `agent_baselines/solvers/sqa/sqa.py@sqa_solver` | `--extra sqa` |
| `solve_llm` | Direct LLM evaluation | `agent_baselines/solvers/sqa/formatted_llm.py@formatted_solver` | `--extra sqa` |
| `solve_storm` | Knowledge curation system | `agent_baselines/solvers/sqa/storm_solver.py@storm_solver` | `--extra storm` |
| `solve_elicit` | Memorized responses | `agent_baselines/solvers/sqa/elicit/memorized_solver.py@elicit_solver` | `--extra sqa` |
| `solve_futurehouse` | Literature review agents | `agent_baselines/solvers/futurehouse/futurehouse_solver.py` | `--extra futurehouse` |

Sources: [dvc.yaml:14-44](), [dvc.yaml:121-142](), [dvc.yaml:197-244](), [dvc.yaml:246-276]()

### Scoring and Post-Processing

All solver outputs go through a unified scoring pipeline:

```mermaid
graph TD
    SOLVER_OUT["Solver Output<br/>.eval files"]
    
    subgraph "Scoring Stage"
        COPY_FILE["Copy to scored/ directory"]
        INSPECT_SCORE["inspect score<br/>astabench/evals/sqa/task.py@score_all"]
    end
    
    subgraph "Post-Processing Stages"
        LOG_SCRIPT["scripts/log_errors.py<br/>Extract error summaries"]
        EXTRACT_SCRIPT["scripts/extract_model_responses.py<br/>Extract responses to CSV"]
        DEBUG_SCRIPT["scripts/create_debug_logs.py<br/>Generate debug CSVs"]
    end
    
    subgraph "Output Files"
        SCORED_EVAL["{split}_dvc_logs/scored/<br/>task_sqa_solver_{model}.eval"]
        ERROR_MD["{split}_dvc_logs/errors/<br/>task_sqa_solver_{model}.md"]
        RESPONSE_CSV["{split}_dvc_logs/model_responses/<br/>task_sqa_solver_{model}_responses.csv"]
        DEBUG_CSV["{split}_dvc_logs/debug_logs/<br/>*_rubric_eval.csv<br/>*_citation_eval.csv<br/>*_answer_precision_eval.csv"]
    end
    
    SOLVER_OUT --> COPY_FILE
    COPY_FILE --> INSPECT_SCORE
    INSPECT_SCORE --> SCORED_EVAL
    
    SCORED_EVAL --> LOG_SCRIPT
    SCORED_EVAL --> DEBUG_SCRIPT
    SOLVER_OUT --> EXTRACT_SCRIPT
    
    LOG_SCRIPT --> ERROR_MD
    EXTRACT_SCRIPT --> RESPONSE_CSV
    DEBUG_SCRIPT --> DEBUG_CSV
```

Sources: [dvc.yaml:308-376](), [dvc.yaml:415-448](), [dvc.yaml:450-488]()

## Execution Workflows

### Basic Pipeline Commands

**Run entire pipeline:**
```bash
dvc repro
```

**Force re-execution ignoring cache:**
```bash
dvc repro --force
```

**Run specific stage:**
```bash
dvc repro solve_sqa@claude-3.7
```

**Run stage and all downstream dependencies:**
```bash
dvc repro score_sqa --force --downstream
```

Sources: [README.md:62-90]()

### Pipeline Status and Debugging

**Check which stages need to run:**
```bash
dvc status
```

**View pipeline dependencies:**
```bash
dvc dag
```

**Check specific stage status:**
```bash
dvc status solve_sqa@claude-3.7
```

### File Naming Conventions

The pipeline uses consistent naming patterns for output files:

```mermaid
graph LR
    subgraph "File Naming Structure"
        PREFIX["task_sqa_solver_"]
        SOLVER_NAME["{solver_name}"]
        MODEL_NAME["{model_name}"]
        EXTENSION[".eval/.md/.csv"]
    end
    
    subgraph "Example Files"
        EVAL["task_sqa_solver_sqa_claude-3.7.eval"]
        ERROR["task_sqa_solver_storm.md"]
        RESPONSE["task_sqa_solver_elicit_responses.csv"]
        DEBUG["task_sqa_solver_sqa_gemini-2.5-pro_rubric_eval.csv"]
    end
    
    PREFIX --> SOLVER_NAME
    SOLVER_NAME --> MODEL_NAME  
    MODEL_NAME --> EXTENSION
    
    EXTENSION --> EVAL
    EXTENSION --> ERROR
    EXTENSION --> RESPONSE
    EXTENSION --> DEBUG
```

Sources: [dvc.yaml:26-38](), [dvc.yaml:442-448](), [dvc.yaml:479-488]()

## Output Management and Caching

### Directory Structure

The pipeline organizes outputs into split-specific directories:

```
{dev|test}_dvc_logs/
├── solver_outputs/          # Raw evaluation results
│   ├── task_sqa_solver_sqa_claude-3.7.eval
│   ├── task_sqa_solver_storm.eval
│   └── task_sqa_solver_elicit.eval
├── scored/                  # Scored evaluation results
│   ├── task_sqa_solver_sqa_claude-3.7.eval
│   └── task_sqa_solver_storm.eval
├── errors/                  # Error summaries
│   ├── task_sqa_solver_sqa_claude-3.7.md
│   └── task_sqa_solver_storm.md
├── debug_logs/             # Debug CSV files
│   ├── task_sqa_solver_sqa_claude-3.7_rubric_eval.csv
│   ├── task_sqa_solver_sqa_claude-3.7_citation_eval.csv
│   └── task_sqa_solver_sqa_claude-3.7_answer_precision_eval.csv
└── model_responses/        # Extracted model responses
    ├── task_sqa_solver_sqa_claude-3.7_responses.csv
    └── task_sqa_solver_storm_responses.csv
```

Sources: [dvc.yaml:44](), [dvc.yaml:374-376](), [dvc.yaml:411-413]()

### Collaboration and Versioning

**Pull latest results from team cache:**
```bash
dvc pull
```

**Push local results to shared cache:**
```bash
dvc push
```

**Check cache synchronization status:**
```bash
dvc status --cloud
```

The `dvc.lock` file tracks exact versions and hashes of all pipeline artifacts, enabling reproducible results across team members.

Sources: [README.md:101-115](), [dvc.lock:1-2]()

### Cache Management

DVC automatically caches outputs based on input dependencies and commands. The cache considers:
- Input file hashes (dependencies)
- Parameter values from `params.yaml`
- Stage command definitions
- Solver/scorer version parameters

When any of these change, the stage will re-execute on the next `dvc repro` run.

Sources: [README.md:76-84](), [dvc.yaml:39-42]()

---

