<!-- source: DeepWiki mcp.deepwiki.com · repo openai/mle-bench · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [environment/Dockerfile](environment/Dockerfile)
- [environment/entrypoint.sh](environment/entrypoint.sh)
- [mlebench/cli.py](mlebench/cli.py)
- [mlebench/competitions/the-icml-2013-whale-challenge-right-whale-redux/prepare.py](mlebench/competitions/the-icml-2013-whale-challenge-right-whale-redux/prepare.py)
- [mlebench/registry.py](mlebench/registry.py)

</details>



## Purpose and Scope

This document describes the high-level architecture of MLE-bench, detailing its core components and their interactions. It provides a technical overview of how the system is organized to facilitate the evaluation of machine learning engineering capabilities of AI systems using Kaggle competitions as benchmark tasks.

## High-Level Architecture Overview

### MLE-bench Ecosystem Architecture

```mermaid
graph TB
    subgraph "External Data Sources"
        Kaggle["Kaggle API<br/>kaggle-api"]
        GitLFS["Git-LFS<br/>Large File Storage"]
    end
    
    subgraph "MLE-bench Core"
        Prepare["mlebench prepare<br/>cli.py:main()"]
        Dataset[("Competition Datasets<br/>75 competitions<br/>/data/")]
        Grade["mlebench grade<br/>cli.py:main()"]
        Aggregate["aggregate_grading_reports.py<br/>Leaderboard Generation"]
    end
    
    subgraph "Agent System"
        RunAgent["run_agent.py<br/>Agent Orchestrator"]
        Dummy["Dummy Agent<br/>agents/dummy/"]
        AIDE["AIDE Agent<br/>agents/aide/"]
        MLAgent["MLAgentBench Agent<br/>agents/mlagentbench/"]
        OpenHands["OpenHands Agent<br/>agents/opendevin/"]
    end
    
    subgraph "Container Infrastructure"
        BaseEnv["mlebench-env<br/>environment/Dockerfile"]
        Sysbox["Sysbox Runtime<br/>Enhanced Isolation"]
        Privileged["Privileged Mode<br/>for OpenHands/DinD"]
        GradingServer["grading_server.py<br/>environment/grading_server.py"]
    end
    
    subgraph "Output & Results"
        Runs[("runs/<run-group>/<br/>Submissions, Logs, Code")]
        Reports["Grading Reports<br/>JSONL Format"]
        Leaderboard["Leaderboard<br/>Any Medal %"]
    end
    
    Kaggle -->|"Download"| Prepare
    GitLFS -->|"Pull"| Dataset
    Prepare -->|"Creates"| Dataset
    Dataset -->|"Mounted in"| BaseEnv
    
    BaseEnv -->|"Base for"| Dummy
    BaseEnv -->|"Base for"| AIDE
    BaseEnv -->|"Base for"| MLAgent
    BaseEnv -->|"Base for"| OpenHands
    
    Sysbox -->|"Runs"| Dummy
    Sysbox -->|"Runs"| AIDE
    Sysbox -->|"Runs"| MLAgent
    Privileged -->|"Runs"| OpenHands
    
    RunAgent -->|"Orchestrates"| Dummy
    RunAgent -->|"Orchestrates"| AIDE
    RunAgent -->|"Orchestrates"| MLAgent
    RunAgent -->|"Orchestrates"| OpenHands
    
    Dummy -->|"Produces"| Runs
    AIDE -->|"Produces"| Runs
    MLAgent -->|"Produces"| Runs
    OpenHands -->|"Produces"| Runs
    
    Runs -->|"Input to"| Grade
    Grade -->|"Outputs"| Reports
    Reports -->|"Processed by"| Aggregate
    Aggregate -->|"Generates"| Leaderboard
    
    AgentSystem -->|"Submits to"| GradingServer
```

Sources: [mlebench/cli.py:13-221](), [environment/Dockerfile:1-92](), [environment/entrypoint.sh:1-20](), [README.md:1-70]()

MLE-bench consists of three main pipelines: (1) Dataset preparation from external sources via `mlebench prepare`, (2) Agent execution in isolated containers producing submissions via `run_agent.py`, and (3) Evaluation and leaderboard generation via `mlebench grade` and aggregation scripts. The system maintains strict separation between public training data (accessible to agents) and private test data (used only for evaluation). The container infrastructure provides two security models: Sysbox runtime for standard agents and privileged mode for OpenHands due to Docker-in-Docker requirements.

## Core Benchmarking System

### Registry System

The `Registry` is the central source of truth for all competition metadata. It maps competition IDs to `Competition` objects which encapsulate paths and logic.

```mermaid
classDiagram
    class Registry {
        +get_competition(id) Competition
        +list_competition_ids() list
        +get_data_dir() Path
        +get_lite_competition_ids() list
        +set_data_dir(Path) Registry
        +get_competitions_dir() Path
        +get_splits_dir() Path
    }
    
    class Competition {
        +id: str
        +name: str
        +description: str
        +grader: Grader
        +answers: Path
        +gold_submission: Path
        +sample_submission: Path
        +competition_type: str
        +prepare_fn: Callable
        +raw_dir: Path
        +private_dir: Path
        +public_dir: Path
        +checksums: Path
        +leaderboard: Path
    }
    
    Registry "1" --> "*" Competition : manages
```

Sources: [mlebench/registry.py:16-156]()

- **Registry**: Loads competition configurations from `mlebench/competitions/<id>/config.yaml` [mlebench/registry.py:81-82](). It handles the resolution of data directories and complexity splits (e.g., `low.txt` for Lite version) [mlebench/registry.py:128-134]().
- **Competition**: A frozen dataclass containing all paths required for preparation and grading. It dynamically imports the `prepare_fn` specified in the competition's config [mlebench/registry.py:90-109]().

### Command-Line Interface

The CLI, implemented in `mlebench/cli.py`, serves as the primary entry point for users and developers.

```mermaid
graph TD
    CLI["mlebench CLI (main)"] --> prepare["prepare"]
    CLI --> grade["grade"]
    CLI --> gradeample["grade-sample"]
    CLI --> dev["dev"]
    
    prepare --> prepareall["--all"]
    prepare --> preparelite["--lite"]
    prepare --> prepareid["--competition-id"]
    
    grade --> gradesub["--submission"]
    grade --> gradeout["--output-dir"]
    
    gradeample --> samplepath["submission_path"]
    gradeample --> sampleid["competition_id"]
```

Sources: [mlebench/cli.py:13-156]()

- **prepare**: Triggers `download_and_prepare_dataset` which uses competition-specific logic to transform raw Kaggle data into a structured format [mlebench/cli.py:185-191]().
- **grade**: Evaluates a batch of submissions provided in a JSONL file using `grade_jsonl` [mlebench/cli.py:192-196]().
- **grade-sample**: Grades a single CSV file for a specific competition using `grade_csv` [mlebench/cli.py:197-201]().

## Agent Execution Framework

### Docker Environment & Entrypoint

The benchmarking environment is standardized via a base Docker image defined in `environment/Dockerfile`.

- **Conda Management**: The image creates two primary environments: `agent` (for running the agent's ML code) and `mleb` (for internal tools like the grading server) [environment/Dockerfile:38-67]().
- **Permissions**: The `entrypoint.sh` script runs as root to set broad read/write permissions on `/home` (excluding the read-only `/home/data` volume) so that non-root agents can function [environment/entrypoint.sh:11-15]().
- **Grading Server**: The entrypoint automatically starts `grading_server.py` in the background, which listens for agent submission requests during the run [environment/entrypoint.sh:18]().

### Agent Execution Architecture

```mermaid
graph TB
    subgraph "Execution Layer"
        RunAgent["run_agent.py"]
        Container["Docker Container (mlebench-env)"]
        GradingServer["grading_server.py<br/>(Background)"]
    end
    
    subgraph "Agent Filesystem"
        DataMount["/home/data/ (Read-only)"]
        SubmissionDir["/home/submission/ (RW)"]
        LogsDir["/home/logs/ (RW)"]
        PrivateDir["/private/ (Restricted)"]
    end
    
    RunAgent -->|"Spawns"| Container
    Container -->|"Starts"| GradingServer
    Container -->|"Mounts"| DataMount
    Container -->|"Writes to"| SubmissionDir
    Container -->|"Writes to"| LogsDir
```

Sources: [environment/Dockerfile:72-92](), [environment/entrypoint.sh:1-20](), [mlebench/registry.py:98-100]()

### Data Flow & Preparation Logic

Each competition has a custom `prepare.py` script. For example, in `the-icml-2013-whale-challenge-right-whale-redux`:
1. **Unpack**: Extracts raw archives [mlebench/competitions/the-icml-2013-whale-challenge-right-whale-redux/prepare.py:14]().
2. **Split**: Distributes data based on timestamps or metadata into `public` (agent-visible) and `private` (grading-only) folders [mlebench/competitions/the-icml-2013-whale-challenge-right-whale-redux/prepare.py:23-35]().
3. **Format**: Generates `test.csv` (answers) and `sampleSubmission.csv` [mlebench/competitions/the-icml-2013-whale-challenge-right-whale-redux/prepare.py:81-88]().

## Evaluation and Results Pipeline

The evaluation pipeline translates agent outputs into leaderboard metrics.

```mermaid
sequenceDiagram
    participant Agent as Agent Container
    participant GS as grading_server.py
    participant CLI as mlebench grade
    participant Agg as aggregate_grading_reports.py
    
    Agent->>GS: Submit CSV via Flask API
    GS->>Agent: Validation Status
    Note over Agent: Container exits
    
    User->>CLI: Grade run outputs
    CLI->>CLI: Load private/test.csv
    CLI->>CLI: Run Grader.grade()
    CLI-->>User: grading_report.json
    
    User->>Agg: Aggregate by Experiment ID
    Agg->>Agg: Calculate Mean/SEM
    Agg-->>User: Final Leaderboard Score
```

Sources: [environment/grading_server.py:1-18](), [mlebench/cli.py:192-204](), [README.md:53-68]()

- **Grading Reports**: Individual runs generate a `grading_report.json` which includes the competition score and medal status [README.md:119-134]().
- **Aggregation**: The `aggregate_grading_reports.py` script groups these reports by `experiment_id` (defined in `runs/run_group_experiments.csv`) and calculates the "Any Medal Percentage" across the requested split (low, medium, high, or split75) [README.md:53-65]().

## Resource and Security Constraints

The architecture enforces strict limits to ensure reproducibility and security:
- **Resource Limits**: Standard evaluations are capped at 24 hours with specific CPU/RAM/GPU allocations [README.md:8-37]().
- **Isolation**: The `/private` directory inside the container is owned by root and restricted (mode 700) to prevent agents from reading ground truth answers [environment/Dockerfile:74]().
- **Runtime**: Agents typically run under the **Sysbox** runtime for enhanced isolation, except for those requiring Docker-in-Docker (like OpenHands), which use privileged mode [README.md:35]().

Sources: [environment/Dockerfile:74-92](), [README.md:8-37]()

---

