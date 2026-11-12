<!-- source: DeepWiki mcp.deepwiki.com · repo openai/mle-bench · page 3 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



This page provides an overview of the initial setup and basic workflows for using MLE-bench. It covers the foundational steps required to prepare your environment, obtain competition datasets, execute agents, and evaluate their submissions. For detailed installation instructions, see [Installation and Setup](#3.1). For a comprehensive walkthrough of your first evaluation, see [Quick Start Guide](#3.2).

The typical MLE-bench workflow consists of three sequential phases: (1) environment setup and dataset preparation, (2) agent execution, and (3) submission grading and leaderboard generation. Each phase produces artifacts that serve as inputs to the next.

## Overview of MLE-bench Workflows

The following diagram illustrates the complete workflow for evaluating agents on MLE-bench, from initial setup through leaderboard generation:

```mermaid
graph TB
    subgraph "Phase 1: Setup & Preparation"
        GitLFS["git lfs pull<br/>Pull LFS files"]
        PipInstall["pip install -e .<br/>Install mlebench"]
        Prepare["mlebench prepare<br/>--all or --lite or -c &lt;comp-id&gt;"]
        BuildEnv["docker build<br/>mlebench-env image"]
    end
    
    subgraph "Phase 2: Agent Execution"
        BuildAgent["docker build<br/>Agent-specific image"]
        RunAgent["python run_agent.py<br/>--agent-id &lt;agent&gt;<br/>--competition-set &lt;split.txt&gt;"]
        RunsDir["runs/&lt;run-group&gt;/<br/>metadata.json<br/>submissions<br/>logs<br/>code"]
    end
    
    subgraph "Phase 3: Evaluation"
        MakeSubmission["python experiments/<br/>make_submission.py<br/>--metadata metadata.json"]
        SubmissionJSONL["submission.jsonl"]
        Grade["mlebench grade<br/>--submission submission.jsonl"]
        GradingReport["&lt;run-group&gt;_grading_report.json"]
        Aggregate["python experiments/<br/>aggregate_grading_reports.py<br/>--experiment-id &lt;exp_id&gt;"]
        Leaderboard["Leaderboard Scores<br/>Any Medal %"]
    end
    
    GitLFS --> PipInstall
    PipInstall --> Prepare
    PipInstall --> BuildEnv
    Prepare --> BuildAgent
    BuildEnv --> BuildAgent
    BuildAgent --> RunAgent
    RunAgent --> RunsDir
    RunsDir --> MakeSubmission
    MakeSubmission --> SubmissionJSONL
    SubmissionJSONL --> Grade
    Grade --> GradingReport
    GradingReport --> Aggregate
    Aggregate --> Leaderboard
    
    style Prepare fill:#e1f5ff
    style RunAgent fill:#fff4e1
    style Grade fill:#e1f5ff
    style Leaderboard fill:#c8e6c9
```

**Sources:** [README.md:93-186](), [agents/README.md:1-65]()

## Prerequisites and System Requirements

Before using MLE-bench, ensure your system meets the requirements defined in `pyproject.toml` and the documentation:

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| Git LFS | Installed and configured | Pull large data files (CSVs, competition solutions) |
| Python | >=3.11 | Run `mlebench` CLI and scripts [pyproject.toml:8-8]() |
| Docker | >=7.1 (Python SDK) | Build and run agent containers [pyproject.toml:12-12]() |
| Sysbox Runtime | Installed (recommended) | Enhanced container-to-host isolation for security |
| NVIDIA Container Toolkit | Optional | GPU support for agent execution |
| Kaggle API | Credentials in `~/.kaggle/kaggle.json` | Download competition data [pyproject.toml:14-14]() |
| Disk Space | 3.3TB (full) or 158GB (lite) | Store prepared competition datasets |

**Sources:** [README.md:93-150](), [agents/README.md:12-16](), [pyproject.toml:8-34]()

## Core Commands and Directory Structure

The following diagram maps MLE-bench commands to the directories and files they interact with:

```mermaid
graph LR
    subgraph "Commands"
        PrepareCmd["mlebench prepare"]
        GradeSampleCmd["mlebench grade-sample"]
        GradeCmd["mlebench grade"]
        RunAgentCmd["python run_agent.py"]
    end
    
    subgraph "Input Sources"
        KaggleAPI["~/.kaggle/kaggle.json<br/>Kaggle credentials"]
        CompetitionSet["experiments/splits/<br/>*.txt files<br/>(e.g., low.txt, split75.txt)"]
    end
    
    subgraph "Data Directories"
        CacheDir["System cache dir<br/>(default location)"]
        DataDir["/data/<br/>Public competition data"]
        PrivateDir["/data_privateonly/<br/>Test labels & answers"]
    end
    
    subgraph "Execution Artifacts"
        RunsDir["runs/&lt;run-group&gt;/<br/>&lt;competition-id&gt;/"]
        SubmissionCSV["submission.csv"]
        MetadataJSON["metadata.json"]
        LogsDir["logs/"]
        CodeDir["code/"]
    end
    
    subgraph "Grading Outputs"
        SubmissionFile["submission.jsonl"]
        GradingReportJSON["&lt;run-group&gt;_grading_report.json"]
    end
    
    KaggleAPI --> PrepareCmd
    PrepareCmd --> DataDir
    PrepareCmd --> PrivateDir
    PrepareCmd --> CacheDir
    
    CompetitionSet --> RunAgentCmd
    DataDir --> RunAgentCmd
    RunAgentCmd --> RunsDir
    RunsDir --> SubmissionCSV
    RunsDir --> MetadataJSON
    RunsDir --> LogsDir
    RunsDir --> CodeDir
    
    SubmissionCSV --> GradeSampleCmd
    MetadataJSON --> SubmissionFile
    SubmissionFile --> GradeCmd
    GradeCmd --> GradingReportJSON
    
    style PrepareCmd fill:#e1f5ff
    style RunAgentCmd fill:#fff4e1
    style GradeCmd fill:#e1f5ff
```

**Sources:** [README.md:93-169](), [agents/README.md:29-47](), [pyproject.toml:40-40]()

## Dataset Preparation Options

MLE-bench provides three dataset preparation options to balance evaluation coverage with resource constraints:

### Preparation Commands

```mermaid
graph TB
    PrepareBase["mlebench prepare"]
    
    AllFlag["--all<br/>75 competitions<br/>~3.3TB<br/>~2 days preparation time"]
    LiteFlag["--lite<br/>22 competitions (Low split)<br/>~158GB<br/>Faster preparation"]
    CompFlag["-c &lt;competition-id&gt;<br/>Single competition<br/>Variable size<br/>Quick testing"]
    
    AllDataset["System cache dir/<br/>mlebench-data/<br/>75 competition dirs"]
    LiteDataset["System cache dir/<br/>mlebench-data/<br/>22 competition dirs"]
    SingleDataset["System cache dir/<br/>mlebench-data/<br/>&lt;competition-id&gt;/"]
    
    PrepareBase --> AllFlag
    PrepareBase --> LiteFlag
    PrepareBase --> CompFlag
    
    AllFlag --> AllDataset
    LiteFlag --> LiteDataset
    CompFlag --> SingleDataset
    
    AllDataset --> CompDirs["Each competition dir contains:<br/>- train/test splits<br/>- description.md<br/>- sample_submission.csv<br/>- metadata.json"]
    LiteDataset --> CompDirs
    SingleDataset --> CompDirs
```

The lite dataset is specifically designed for cost-effective evaluation and corresponds to the Low complexity split. See [Dataset Preparation](#4.1) for detailed information about the preparation process.

**Sources:** [README.md:130-150](), [README.md:60-92]()

## Agent Execution Workflow

The `run_agent.py` script orchestrates agent execution across multiple competitions. The following diagram shows the complete execution flow:

```mermaid
graph TB
    subgraph "Configuration Inputs"
        AgentID["--agent-id<br/>(e.g., aide, dummy, mlagentbench)"]
        CompSet["--competition-set<br/>(e.g., experiments/splits/low.txt)"]
        ContainerConfig["Container config<br/>(default.json or custom)"]
    end
    
    subgraph "Docker Images"
        BaseImage["mlebench-env<br/>Base environment"]
        AgentImage["&lt;agent-id&gt;<br/>Agent-specific image"]
    end
    
    subgraph "Execution"
        RunAgentPy["run_agent.py"]
        CreateRunGroup["Create runs/&lt;run-group&gt;/"]
        ForEachComp["For each competition:"]
        LaunchContainer["Launch container with:<br/>- /home/data/ mounted<br/>- /home/instructions.txt<br/>- Agent workspace dirs"]
        AgentExec["Agent executes<br/>Reads data<br/>Trains models<br/>Generates submission.csv"]
        CollectOutputs["Collect outputs:<br/>- submission.csv<br/>- logs/<br/>- code/<br/>- agent/"]
    end
    
    subgraph "Outputs"
        RunGroupDir["runs/&lt;run-group&gt;/"]
        CompSubdirs["&lt;competition-id&gt;/<br/>submission/<br/>logs/<br/>code/<br/>agent/"]
        MetadataFile["metadata.json<br/>(on completion)"]
    end
    
    AgentID --> RunAgentPy
    CompSet --> RunAgentPy
    ContainerConfig --> RunAgentPy
    BaseImage --> AgentImage
    AgentImage --> RunAgentPy
    
    RunAgentPy --> CreateRunGroup
    CreateRunGroup --> ForEachComp
    ForEachComp --> LaunchContainer
    LaunchContainer --> AgentExec
    AgentExec --> CollectOutputs
    
    CollectOutputs --> RunGroupDir
    RunGroupDir --> CompSubdirs
    RunGroupDir --> MetadataFile
    
    style RunAgentPy fill:#fff4e1
    style MetadataFile fill:#c8e6c9
```

The standard resource allocation for benchmarking is 24 hours runtime with 36 vCPUs, 440GB RAM, and one 24GB A10 GPU. These defaults are typically configured in container JSON files and can be customized per execution.

**Sources:** [agents/README.md:29-49](), [README.md:52-64](), [README.md:173-183]()

## Grading and Leaderboard Generation

After agent execution completes, submissions must be formatted and graded. The following diagram shows the evaluation pipeline:

```mermaid
graph TB
    subgraph "Prepare Submission"
        MetadataIn["runs/&lt;run-group&gt;/metadata.json"]
        MakeSubmissionPy["python experiments/make_submission.py<br/>--metadata metadata.json<br/>--output submission.jsonl"]
        SubmissionJSONL["submission.jsonl<br/>Each line: {competition_id, submission_path}"]
    end
    
    subgraph "Grade Submission"
        GradeCmd["mlebench grade<br/>--submission submission.jsonl<br/>--output-dir runs/&lt;run-group&gt;"]
        PrivateData["/data_privateonly/<br/>Ground truth test labels"]
        GradingReport["&lt;run-group&gt;_grading_report.json<br/>Per-competition scores"]
    end
    
    subgraph "Generate Leaderboard"
        ExperimentCSV["runs/run_group_experiments.csv<br/>Map run groups to experiment IDs"]
        AggregateScript["python experiments/aggregate_grading_reports.py<br/>--experiment-id &lt;exp_id&gt;<br/>--split {low,medium,high,split75}"]
        LeaderboardMetrics["any_medal_percentage<br/>Mean ± SEM across seeds"]
    end
    
    MetadataIn --> MakeSubmissionPy
    MakeSubmissionPy --> SubmissionJSONL
    SubmissionJSONL --> GradeCmd
    PrivateData --> GradeCmd
    GradeCmd --> GradingReport
    
    GradingReport --> ExperimentCSV
    ExperimentCSV --> AggregateScript
    AggregateScript --> LeaderboardMetrics
    
    style GradeCmd fill:#e1f5ff
    style LeaderboardMetrics fill:#c8e6c9
```

The grading process uses the private test data prepared during `mlebench prepare`, which is isolated from agents during execution. Leaderboard metrics should be computed using `aggregate_grading_reports.py` to capture agent variance [README.md:53-65]().

**Sources:** [README.md:154-169](), [README.md:33-49](), [agents/README.md:37-47](), [README.md:53-65]()

## Common Usage Patterns

The following table summarizes typical usage scenarios and their corresponding commands:

| Scenario | Commands | Expected Output |
|----------|----------|-----------------|
| **Quick environment test** | `python run_agent.py --agent-id dummy --competition-set experiments/splits/spaceship-titanic.txt` | Single run group with validation checks passed |
| **Lite evaluation (22 comps)** | `mlebench prepare --lite`<br/>`python run_agent.py --agent-id aide --competition-set experiments/splits/low.txt` | 158GB dataset, run group with 22 competition submissions |
| **Full benchmark (75 comps)** | `mlebench prepare --all`<br/>`python run_agent.py --agent-id aide --competition-set experiments/splits/split75.txt` | 3.3TB dataset, run group with 75 competition submissions |
| **Single competition dev** | `mlebench prepare -c spaceship-titanic`<br/>`python run_agent.py --agent-id aide --competition-set experiments/splits/spaceship-titanic.txt` | ~50MB dataset, single competition run for testing |
| **Grade single submission** | `mlebench grade-sample <path/to/submission.csv> <comp-id>` | Immediate score output to stdout |
| **Grade multiple submissions** | `python experiments/make_submission.py --metadata runs/<run-group>/metadata.json --output submission.jsonl`<br/>`mlebench grade --submission submission.jsonl --output-dir runs/<run-group>` | Grading report JSON file |
| **Generate leaderboard scores** | `python experiments/aggregate_grading_reports.py --experiment-id <exp_id> --split low` | `any_medal_percentage` with mean ± SEM [README.md:61-65]() |

**Sources:** [README.md:130-150](), [agents/README.md:31-47](), [README.md:154-169](), [README.md:33-49](), [README.md:61-65]()

## Security Considerations

MLE-bench employs a two-tier security model for agent execution:

```mermaid
graph TB
    subgraph "Sysbox Runtime (Recommended)"
        SysboxAgents["Most agents:<br/>- dummy<br/>- aide<br/>- mlagentbench"]
        SysboxFeatures["Enhanced isolation<br/>Container-to-host security<br/>No privileged mode required"]
    end
    
    subgraph "Privileged Mode (Special Case)"
        PrivilegedAgent["opendevin (OpenHands)<br/>Requires Docker-in-Docker"]
        EnvVar["Requires:<br/>I_ACCEPT_RUNNING_PRIVILEGED_CONTAINERS=True"]
        SecurityWarning["⚠ Reduced container-to-host isolation<br/>Acceptable for trusted environments only"]
    end
    
    subgraph "Access Controls (All Agents)"
        DataAccess["/data/ - Read only<br/>Public training data"]
        PrivateRestrict["/data_privateonly/ - No access<br/>Test labels isolated"]
        HomeAccess["/home/ - Read/Write<br/>Agent workspace"]
        ValidationScript["validate_submission.sh<br/>Format checking"]
    end
    
    SysboxAgents --> SysboxFeatures
    SysboxFeatures --> DataAccess
    SysboxFeatures --> PrivateRestrict
    SysboxFeatures --> HomeAccess
    SysboxFeatures --> ValidationScript
    
    PrivilegedAgent --> EnvVar
    EnvVar --> SecurityWarning
    SecurityWarning --> DataAccess
    SecurityWarning --> PrivateRestrict
    SecurityWarning --> HomeAccess
    SecurityWarning --> ValidationScript
    
    style SysboxFeatures fill:#c8e6c9
    style SecurityWarning fill:#ffe1e1
```

The `dummy` agent performs validation checks to verify the security model is properly configured [agents/README.md:52-58](). See [Container Security Models](#6.3) for complete details on isolation mechanisms.

**Sources:** [agents/README.md:60-64](), [agents/README.md:52-58]()

## Next Steps

After completing the initial setup, proceed to:

- **[Installation and Setup](#3.1)** - Detailed installation instructions, dependency management, and troubleshooting.
- **[Quick Start Guide](#3.2)** - Step-by-step walkthrough of running your first agent evaluation from start to finish.
- **[Dataset Preparation](#4.1)** - In-depth coverage of dataset preparation options, Git LFS configuration, and storage management.
- **[Running Agents](#4.2)** - Comprehensive guide to agent execution, configuration, and output management.
- **[Agent Implementations](#7)** - Detailed documentation for each available agent (aide, mlagentbench, opendevin, dummy).

For developers interested in extending MLE-bench or contributing new agents, see [Development Guide](#9).

**Sources:** [README.md:1-273](), [agents/README.md:1-65]()

---

