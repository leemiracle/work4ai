<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/agent-eval · page 4 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/agenteval/cli.py](src/agenteval/cli.py)
- [src/agenteval/models.py](src/agenteval/models.py)

</details>



This document provides a deep dive into agent-eval's internal architecture, covering the core components, data flow, and design patterns that enable the system's three-stage evaluation pipeline. 

For information about using the CLI commands, see [CLI Reference](#3.3). For details about individual data processing steps, see [Data Processing Pipeline](#4.1). For external system integrations, see [External Integrations](#4.2).

## System Overview

Agent-eval implements a three-stage pipeline architecture that transforms agent evaluation configurations into published leaderboard results. The system is designed as an orchestration layer that coordinates between existing tools like Inspect AI, LiteLLM, and HuggingFace Hub.

### Core Pipeline Architecture

```mermaid
graph TB
    subgraph "CLI Layer"
        CLI["cli.py"]
        eval_command["eval_command()"]
        score_command["score_command()"] 
        publish_command["publish_command()"]
    end
    
    subgraph "Data Models"
        EvalConfig["EvalConfig"]
        EvalResult["EvalResult"]
        SubmissionMetadata["SubmissionMetadata"]
    end
    
    subgraph "Processing Modules"
        config_module["config.py"]
        score_module["score.py"]
        summary_module["summary.py"]
        upload_module["upload.py"]
    end
    
    subgraph "External Systems"
        InspectAI["Inspect AI"]
        HuggingFace["HuggingFace Hub"]
        LiteLLM["LiteLLM"]
    end
    
    CLI --> eval_command
    CLI --> score_command
    CLI --> publish_command
    
    eval_command --> config_module
    eval_command --> InspectAI
    eval_command --> EvalConfig
    
    score_command --> score_module
    score_command --> summary_module
    score_command --> EvalResult
    
    publish_command --> upload_module
    publish_command --> HuggingFace
    publish_command --> SubmissionMetadata
    
    score_module --> LiteLLM
    config_module --> EvalConfig
    EvalResult --> SubmissionMetadata
```

*Sources: [src/agenteval/cli.py:95-433](), [src/agenteval/models.py:1-90]()*

The architecture follows a clear separation of concerns where the CLI layer orchestrates the pipeline, data models provide structure, and processing modules handle the core logic.

## Data Flow Through Pipeline Stages

The system processes evaluation data through three distinct stages, each with specific inputs, outputs, and responsibilities.

### Three-Stage Data Transformation

```mermaid
graph LR
    subgraph "Stage 1: eval"
        YAMLConfig["YAML Config"]
        eval_command_func["eval_command()"]
        InspectEval["inspect eval-set"]
        RawLogs["Raw Logs"]
        agenteval_json["agenteval.json"]
    end
    
    subgraph "Stage 2: score"
        score_command_func["score_command()"]
        process_eval_logs["process_eval_logs()"]
        TaskResult["TaskResult[]"]
        compute_summary["compute_summary_statistics()"]
        ScoredResult["Scored EvalResult"]
    end
    
    subgraph "Stage 3: publish"
        publish_command_func["publish_command()"]
        upload_folder["upload_folder_to_hf()"]
        upload_summary["upload_summary_to_hf()"]
        HFLeaderboard["HF Leaderboard"]
    end
    
    YAMLConfig --> eval_command_func
    eval_command_func --> InspectEval
    InspectEval --> RawLogs
    eval_command_func --> agenteval_json
    
    RawLogs --> score_command_func
    agenteval_json --> score_command_func
    score_command_func --> process_eval_logs
    process_eval_logs --> TaskResult
    TaskResult --> compute_summary
    compute_summary --> ScoredResult
    
    ScoredResult --> publish_command_func
    publish_command_func --> upload_folder
    publish_command_func --> upload_summary
    upload_folder --> HFLeaderboard
    upload_summary --> HFLeaderboard
```

*Sources: [src/agenteval/cli.py:333-428](), [src/agenteval/cli.py:100-195](), [src/agenteval/cli.py:199-329]()*

Each stage produces artifacts that serve as inputs to the next stage, with `agenteval.json` serving as the central state file that accumulates data throughout the pipeline.

## Core Components and Responsibilities

### CLI Command Layer

The CLI layer in [src/agenteval/cli.py]() provides the primary interface and orchestrates all system operations. Each command has distinct responsibilities:

| Command | Function | Primary Responsibility |
|---------|----------|----------------------|
| `eval` | `eval_command()` | Execute evaluations via Inspect AI and initialize result tracking |
| `score` | `score_command()` | Process evaluation logs into structured results and compute metrics |
| `publish` | `publish_command()` | Upload results to HuggingFace and update leaderboards |

*Sources: [src/agenteval/cli.py:333-428](), [src/agenteval/cli.py:100-195](), [src/agenteval/cli.py:199-329]()*

### Data Model Layer

The data models in [src/agenteval/models.py]() provide the core data structures that flow through the system:

```mermaid
classDiagram
    class EvalConfig {
        +SuiteConfig suite_config
        +str split
    }
    
    class EvalResult {
        +list[EvalSpec] eval_specs
        +list[TaskResult] results
        +SubmissionMetadata submission
        +find_missing_tasks() list[str]
        +is_scored() bool
        +save_json() None
    }
    
    class SubmissionMetadata {
        +datetime submit_time
        +str username
        +str agent_name
        +str agent_description
        +str agent_url
        +str logs_url
        +str summary_url
    }
    
    EvalConfig <|-- EvalResult
    EvalResult *-- SubmissionMetadata
```

*Sources: [src/agenteval/models.py:12-18](), [src/agenteval/models.py:33-89](), [src/agenteval/models.py:20-31]()*

`EvalResult` serves as the central data structure that accumulates information throughout the pipeline, starting as a simple `EvalConfig` and growing to include results and submission metadata.

## State Management and Persistence

The system uses a file-based state management approach centered around the `agenteval.json` file, which serves as the persistent state store throughout the evaluation pipeline.

### State File Evolution

```mermaid
graph TB
    subgraph "eval Stage"
        InitialState["EvalConfig(suite_config, split)"]
        SaveInitial["save to agenteval.json"]
    end
    
    subgraph "score Stage"
        LoadState["load from agenteval.json"]
        AddResults["+ eval_specs, results"]
        SaveScored["save scored EvalResult"]
    end
    
    subgraph "publish Stage"
        LoadScored["load scored EvalResult"]
        AddSubmission["+ submission metadata"]
        SaveFinal["save final EvalResult"]
    end
    
    InitialState --> SaveInitial
    SaveInitial --> LoadState
    LoadState --> AddResults
    AddResults --> SaveScored
    SaveScored --> LoadScored
    LoadScored --> AddSubmission
    AddSubmission --> SaveFinal
```

*Sources: [src/agenteval/cli.py:400-403](), [src/agenteval/cli.py:124-155](), [src/agenteval/cli.py:260-327](), [src/agenteval/models.py:57-89]()*

The constant `EVAL_FILENAME = "agenteval.json"` [src/agenteval/cli.py:17]() defines the standard filename used across all commands for state persistence.

## Reproducibility and Validation

Agent-eval implements several mechanisms to ensure evaluation reproducibility and result validation.

### Git Reproducibility Verification

```mermaid
graph TB
    eval_start["eval command starts"]
    ignore_git{"--ignore-git flag?"}
    git_check["verify_git_reproducibility()"]
    
    subgraph "Git Validation"
        check_sha["get commit SHA"]
        check_origin["get remote origin"]
        check_dirty["check working directory"]
        check_untracked["check untracked files"]
        check_remote["verify commit on remote"]
    end
    
    validation_pass["validation passes"]
    abort_dirty["abort: uncommitted changes"]
    abort_unpushed["abort: commit not on remote"]
    proceed["proceed with evaluation"]
    
    eval_start --> ignore_git
    ignore_git -->|false| git_check
    ignore_git -->|true| proceed
    
    git_check --> check_sha
    check_sha --> check_origin
    check_origin --> check_dirty
    check_dirty --> check_untracked
    check_untracked --> check_remote
    
    check_remote --> validation_pass
    check_dirty -->|dirty| abort_dirty
    check_remote -->|not on remote| abort_unpushed
    validation_pass --> proceed
```

*Sources: [src/agenteval/cli.py:20-92](), [src/agenteval/cli.py:383-384]()*

The `verify_git_reproducibility()` function ensures that evaluations can be reproduced by requiring a clean working directory and verifying that the current commit exists on the remote repository.

## External System Integration Points

Agent-eval integrates with external systems through well-defined interfaces that abstract away implementation details.

### Integration Architecture

```mermaid
graph TB
    subgraph "agent-eval Core"
        eval_cmd["eval_command()"]
        score_cmd["score_command()"]  
        publish_cmd["publish_command()"]
    end
    
    subgraph "Inspect AI Integration"
        subprocess_call["subprocess.run()"]
        inspect_eval_set["inspect eval-set"]
        log_output["evaluation logs"]
    end
    
    subgraph "HuggingFace Integration"
        HfApi["HfApi()"]
        upload_folder_to_hf["upload_folder_to_hf()"]
        upload_summary_to_hf["upload_summary_to_hf()"]
    end
    
    subgraph "LiteLLM Integration"
        process_eval_logs_func["process_eval_logs()"]
        cost_extraction["cost computation"]
    end
    
    eval_cmd --> subprocess_call
    subprocess_call --> inspect_eval_set
    inspect_eval_set --> log_output
    
    score_cmd --> process_eval_logs_func
    process_eval_logs_func --> cost_extraction
    
    publish_cmd --> HfApi
    HfApi --> upload_folder_to_hf
    HfApi --> upload_summary_to_hf
```

*Sources: [src/agenteval/cli.py:408-421](), [src/agenteval/cli.py:249-250](), [src/agenteval/cli.py:277-278](), [src/agenteval/cli.py:313-323]()*

The system uses subprocess calls to Inspect AI rather than direct imports, maintaining loose coupling and allowing for independent evolution of the evaluation framework.

## Key Architectural Patterns

Agent-eval employs several key architectural patterns that enable its functionality:

1. **Pipeline Architecture**: Clear three-stage processing with distinct responsibilities
2. **State Accumulation**: Central state file that grows through pipeline stages  
3. **External Tool Orchestration**: Coordinates existing tools rather than reimplementing functionality
4. **Reproducibility-First Design**: Git-based validation ensures evaluations can be reproduced
5. **Schema-Driven Development**: Pydantic models serve as the contract between components

For detailed information about data processing within each stage, see [Data Processing Pipeline](#4.1). For specifics about external integrations, see [External Integrations](#4.2). For data model details, see [Data Models](#4.4).

*Sources: [src/agenteval/cli.py:1-433](), [src/agenteval/models.py:1-90]()*

---

