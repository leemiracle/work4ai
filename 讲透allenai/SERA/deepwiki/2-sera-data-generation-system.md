<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SERA · page 2 SERA Data Generation System · fetched 2026-10-26 -->

# SERA Data Generation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)

</details>



## Purpose and Scope

The SERA Data Generation System is a multi-stage pipeline for generating software engineering training data from language models. This document covers the pipeline architecture, configuration system, inference server integration, and data generation workflows. For information about installation and environment setup, see [Installation and Setup](#2.1). For details on inference server deployment, see [Inference Servers](#2.2). For pipeline stage internals, see [Pipeline Stages](#2.4). For scaling to multiple servers, see [Multi-Server Scaling](#2.5).

The SERA system transforms GitHub repositories and pull request issues into synthetic training data through a sequence of generation, distillation, evaluation, and postprocessing stages. It supports both open-source models (via inference servers) and closed-source models (via API calls), with built-in capabilities for horizontal scaling and fault tolerance.

---

## System Architecture Overview

The SERA data generation system consists of three primary layers: the configuration layer that defines experiment parameters, the orchestration layer that manages pipeline execution, and the inference layer that provides model endpoints.

### High-Level System Architecture

```mermaid
graph TB
    subgraph ConfigLayer["Configuration Layer"]
        ConfigFiles["Configuration Files<br/>sera/configs/*.yaml"]
        ConfigSchema["Config Schema<br/>sera/config_schema.py"]
        CLIArgs["CLI Arguments<br/>Hydra Override"]
    end
    
    subgraph OrchestratorLayer["Orchestration Layer"]
        MainPy["Main Orchestrator<br/>sera/main.py"]
        StageManager["Stage Manager<br/>stage_map"]
        ExperimentTracker["Experiment Tracker<br/>name + outputs/"]
    end
    
    subgraph InferenceLayer["Inference Layer"]
        OpenSourceServers["Open Source Servers<br/>GLM/Qwen/etc"]
        ClosedSourceAPIs["Closed Source APIs<br/>Anthropic/OpenAI"]
        ModelRouter["Model Router<br/>distill.model.url"]
    end
    
    subgraph PipelineStages["Pipeline Stages"]
        Generate["generate<br/>Stage 0"]
        DistillOne["distill_stage_one<br/>Stage 1"]
        DistillTwo["distill_stage_two<br/>Stage 2"]
        Eval["eval<br/>Stage 3"]
        Postprocess["postprocess<br/>Stage 4"]
    end
    
    subgraph DataLayer["Data Layer"]
        Repos["repos/<br/>Cloned Repositories"]
        Experiments["experiments/<br/>Generated Data"]
        Outputs["outputs/<br/>Final Dataset"]
        Logs["logs/<br/>Execution Logs"]
    end
    
    ConfigFiles --> ConfigSchema
    ConfigSchema --> MainPy
    CLIArgs --> MainPy
    
    MainPy --> StageManager
    StageManager --> Generate
    Generate --> DistillOne
    DistillOne --> DistillTwo
    DistillTwo --> Eval
    Eval --> Postprocess
    
    ModelRouter --> Generate
    ModelRouter --> DistillOne
    ModelRouter --> DistillTwo
    
    OpenSourceServers --> ModelRouter
    ClosedSourceAPIs --> ModelRouter
    
    Generate --> Repos
    DistillOne --> Experiments
    DistillTwo --> Experiments
    Eval --> Experiments
    Postprocess --> Outputs
    
    MainPy --> ExperimentTracker
    ExperimentTracker --> Logs
```

**Sources:** [README.md:1-184](), [.gitignore:1-227]()

---

## Pipeline Orchestration

The SERA pipeline is orchestrated by `sera/main.py`, which manages the sequential execution of five distinct stages. Each stage can be resumed independently, enabling fault tolerance for large-scale data generation runs.

### Stage Management System

The orchestrator uses a stage mapping system to control pipeline execution:

```mermaid
graph LR
    subgraph StageMap["stage_map Dictionary"]
        Pipeline["pipeline: -1"]
        Generate["generate: 0"]
        DistillOne["distill_stage_one: 1"]
        DistillTwo["distill_stage_two: 2"]
        EvalStage["eval: 3"]
        PostStage["postprocess: 4"]
    end
    
    subgraph ExecutionFlow["Execution Flow"]
        CheckStage["Check stage Parameter"]
        SkipCompleted["Skip Completed Stages"]
        ExecuteCurrent["Execute Current Stage"]
        SaveState["Save State to outputs/"]
    end
    
    subgraph ResumeLogic["Resume Logic"]
        MatchName["Match Experiment name"]
        LoadPrevious["Load Previous State"]
        ContinueFrom["Continue from stage"]
    end
    
    Pipeline --> Generate
    Generate --> DistillOne
    DistillOne --> DistillTwo
    DistillTwo --> EvalStage
    EvalStage --> PostStage
    
    CheckStage --> SkipCompleted
    SkipCompleted --> ExecuteCurrent
    ExecuteCurrent --> SaveState
    
    MatchName --> LoadPrevious
    LoadPrevious --> ContinueFrom
    ContinueFrom --> CheckStage
```

| Stage Name | Stage ID | Purpose | Output Location |
|------------|----------|---------|-----------------|
| `pipeline` | -1 | Complete pipeline execution | Full workflow |
| `generate` | 0 | Initial data generation | `repos/` directory |
| `distill_stage_one` | 1 | First distillation pass | `experiments/` directory |
| `distill_stage_two` | 2 | Second distillation pass | `experiments/` directory |
| `eval` | 3 | Evaluation of generated data | `experiments/` directory |
| `postprocess` | 4 | Final dataset creation | `outputs/` directory |

**Sources:** [README.md:130-156](), [.gitignore:1-7]()

---

## Configuration System

SERA uses Hydra for configuration management, with a base schema defined in `sera/config_schema.py` and multiple YAML configuration files for different specialization scenarios.

### Configuration Architecture

```mermaid
graph TB
    subgraph ConfigSchema["sera/config_schema.py"]
        BaseSchema["Base Configuration Schema"]
        DistillConfig["distill Configuration"]
        GenerateConfig["generate Configuration"]
        ModelConfig["model Configuration"]
        DockerConfig["docker Configuration"]
    end
    
    subgraph YAMLConfigs["sera/configs/*.yaml"]
        Django["specialization_django.yaml<br/>SWE-Bench Django/Sympy"]
        Personal["specialization_personal.yaml<br/>Custom Repositories"]
        Anthropic["specialization_anthropic.yaml<br/>Closed-Source Models"]
        SweSmith["swesmith_scaling.yaml<br/>Large-Scale Generation"]
    end
    
    subgraph RuntimeOverride["Runtime Configuration"]
        CLIOverride["CLI Arguments<br/>--config-name + params"]
        DistillModel["distill.model.name<br/>distill.model.url"]
        ShardConfig["distill.shard<br/>distill.total_shards"]
        DockerOrg["generate.docker.gh_mirror_org<br/>generate.docker.docker_org"]
    end
    
    BaseSchema --> DistillConfig
    BaseSchema --> GenerateConfig
    DistillConfig --> ModelConfig
    GenerateConfig --> DockerConfig
    
    Django --> CLIOverride
    Personal --> CLIOverride
    Anthropic --> CLIOverride
    SweSmith --> CLIOverride
    
    CLIOverride --> DistillModel
    CLIOverride --> ShardConfig
    CLIOverride --> DockerOrg
```

### Key Configuration Parameters

| Parameter Path | Purpose | Example Value |
|----------------|---------|---------------|
| `distill.model.name` | Model identifier for inference | `openai/GLM-4.5-Air` |
| `distill.model.url` | Inference server endpoint | `http://hostname:24444/v1` |
| `distill.shard` | Current shard index for parallel processing | `0` |
| `distill.total_shards` | Total number of shards | `4` |
| `generate.docker.gh_mirror_org` | GitHub organization for repository mirrors | `oca-repos` |
| `generate.docker.docker_org` | Docker organization for image persistence | Custom org name |
| `distill.args.pipeline_repo` | Path to PR issues for demonstration | `pr_issues/generated.json` |
| `stage` | Starting stage for resumed runs | `distill_stage_two` |
| `name` | Experiment identifier | Auto-generated or custom |

**Sources:** [README.md:37-169](), [sera/config_schema.py]()

---

## Specialization Modes

SERA supports three primary specialization modes, each tailored to different data generation scenarios. Each mode is configured through a dedicated YAML file that defines repositories, generation parameters, and model settings.

### Specialization Mode Comparison

| Mode | Config File | Target | Key Features |
|------|------------|---------|--------------|
| Django/Sympy | `specialization_django.yaml` | SWE-Bench repositories | Pre-configured for well-tested codebases |
| Personal Repos | `specialization_personal.yaml` | Custom repositories | Requires manual configuration of install commands |
| Closed-Source | `specialization_anthropic.yaml` | Anthropic/OpenAI models | No inference server required |

### Personal Repository Configuration

```mermaid
graph TB
    subgraph PersonalRepoConfig["Personal Repository Configuration"]
        RepoSpec["Repository Specification"]
        InstallSpec["Installation Specification"]
        DockerSpec["Docker Specification"]
        PRIssues["PR Issues Specification"]
    end
    
    subgraph RepoSpecDetails["Repository Details"]
        OrgName["org_name: OpenHands"]
        LastName["last_name: OpenHands"]
        Commits["commits: List of commit hashes"]
        TopLevel["top_level_folder: openhands"]
    end
    
    subgraph InstallSpecDetails["Installation Details"]
        InstallCmds["install_cmds:<br/>- pip install -e ."]
        TestCmd["test_cmd: null"]
        PythonVer["python_version: 3.12"]
    end
    
    subgraph DockerSpecDetails["Docker Details"]
        GHMirror["gh_mirror_org: oca-repos"]
        DockerOrg["docker_org: Custom"]
        ImagePersist["Persistent images via org"]
    end
    
    subgraph PRIssuesDetails["PR Issues Details"]
        ScrapedIssues["Scraped from GitHub"]
        IssueJSON["pr_issues/*.json"]
        PipelineRepo["distill.args.pipeline_repo"]
    end
    
    RepoSpec --> RepoSpecDetails
    InstallSpec --> InstallSpecDetails
    DockerSpec --> DockerSpecDetails
    PRIssues --> PRIssuesDetails
    
    RepoSpecDetails --> GHMirror
    InstallSpecDetails --> GHMirror
    DockerSpecDetails --> ImagePersist
    PRIssuesDetails --> PipelineRepo
```

### Example Personal Repository Configuration

For personal repositories, the YAML configuration requires explicit specification of installation commands, main code folders, and Python versions:

```yaml
- org_name: OpenHands
  last_name: OpenHands
  commits:
    - 29b77be807e0e6aab380d953c0d79a166df4f0cc
    - cc8b677f3ec324fb7b9de86229f727b25741a66c
  install_cmds:
    - "pip install -e ."
  test_cmd: null
  python_version: 3.12
  top_level_folder:
    - openhands
```

**Sources:** [README.md:49-84](), [sera/configs/specialization_personal.yaml]()

---

## Data Flow and Output Structure

The SERA pipeline generates multiple types of data artifacts across different stages, each stored in dedicated directories that are excluded from version control.

### Data Flow Diagram

```mermaid
graph TB
    subgraph InputData["Input Data"]
        GitHubRepos["GitHub Repositories"]
        PRIssuesDir["pr_issues/<br/>Scraped Issues"]
        ConfigYAML["Config YAML<br/>Specialization Settings"]
    end
    
    subgraph GenerateStage["Generate Stage (0)"]
        CloneRepos["Clone Repositories<br/>to repos/"]
        BuildContainers["Build Docker Containers"]
        InitGeneration["Initial Data Generation"]
    end
    
    subgraph DistillStageOne["Distill Stage One (1)"]
        FirstRollout["First Distillation Rollout"]
        ExperimentsOne["experiments/<br/>Stage 1 Output"]
    end
    
    subgraph DistillStageTwo["Distill Stage Two (2)"]
        SecondRollout["Second Distillation Rollout"]
        SyntheticPRs["Synthetic PR Creation"]
        ExperimentsTwo["experiments/<br/>Stage 2 Output"]
    end
    
    subgraph EvalStage["Eval Stage (3)"]
        EvaluateData["Evaluate Generated Data"]
        Metrics["Generate Metrics"]
        ExperimentsEval["experiments/<br/>Evaluation Results"]
    end
    
    subgraph PostprocessStage["Postprocess Stage (4)"]
        FinalDataset["Create Final Dataset"]
        OutputsDir["outputs/<br/>Final Training Data"]
    end
    
    subgraph PersistentData["Persistent Data"]
        LogsDir["logs/<br/>Execution Logs"]
        Metadata["metadata/<br/>Experiment Metadata"]
    end
    
    GitHubRepos --> CloneRepos
    PRIssuesDir --> FirstRollout
    ConfigYAML --> CloneRepos
    
    CloneRepos --> BuildContainers
    BuildContainers --> InitGeneration
    InitGeneration --> FirstRollout
    
    FirstRollout --> ExperimentsOne
    ExperimentsOne --> SecondRollout
    SecondRollout --> SyntheticPRs
    SyntheticPRs --> ExperimentsTwo
    
    ExperimentsTwo --> EvaluateData
    EvaluateData --> Metrics
    Metrics --> ExperimentsEval
    
    ExperimentsEval --> FinalDataset
    FinalDataset --> OutputsDir
    
    CloneRepos --> LogsDir
    FirstRollout --> LogsDir
    SecondRollout --> LogsDir
    EvaluateData --> Metadata
```

### Output Directory Structure

| Directory | Created By | Purpose | Gitignored |
|-----------|-----------|---------|------------|
| `repos/` | Generate stage | Cloned repository working copies | Yes |
| `experiments/` | Distill/Eval stages | Intermediate generation outputs | Yes |
| `outputs/` | Postprocess stage | Final training datasets | Yes |
| `logs/` | All stages | Execution logs and debugging info | Yes |
| `metadata/` | Pipeline | Experiment tracking metadata | Yes |
| `pr_issues/` | User script | Scraped GitHub issues | Yes |

**Sources:** [.gitignore:1-9](), [README.md:130-169]()

---

## Inference Server Integration

SERA supports multiple inference backends through a unified model routing system. The system can connect to open-source model servers or closed-source API endpoints.

### Inference Server Architecture

```mermaid
graph TB
    subgraph LaunchScripts["Inference Server Launch Scripts"]
        GLM45Script["launch_glm45.sh<br/>sera/datagen/inference/"]
        GLM46Script["launch_glm46.sh<br/>sera/datagen/inference/"]
        QwenScript["launch_qwen3_models.sh<br/>sera/datagen/inference/"]
    end
    
    subgraph ServerConfig["Server Configuration"]
        TPSetting["Tensor Parallelism<br/>TP Parameter"]
        PortSetting["Server Port<br/>PORT Parameter"]
        SeedSetting["Random Seed<br/>SEED Parameter"]
    end
    
    subgraph ServerEndpoints["Running Servers"]
        GLM45Server["GLM-4.5-Air Server<br/>http://hostname:port/v1"]
        GLM46Server["GLM-4.6 Server<br/>http://hostname:port/v1"]
        QwenServer["Qwen Models Server<br/>http://hostname:port/v1"]
    end
    
    subgraph ClosedSource["Closed-Source APIs"]
        AnthropicAPI["Anthropic API<br/>Claude Models"]
        OpenAIAPI["OpenAI API<br/>GPT Models"]
    end
    
    subgraph ModelRouter["SERA Model Router"]
        ModelName["distill.model.name<br/>openai/GLM-4.5-Air"]
        ModelURL["distill.model.url<br/>http://hostname:port/v1"]
        APIKeys["API Keys<br/>Environment Variables"]
    end
    
    GLM45Script --> TPSetting
    GLM45Script --> PortSetting
    GLM45Script --> SeedSetting
    TPSetting --> GLM45Server
    PortSetting --> GLM45Server
    SeedSetting --> GLM45Server
    
    GLM46Script --> GLM46Server
    QwenScript --> QwenServer
    
    GLM45Server --> ModelRouter
    GLM46Server --> ModelRouter
    QwenServer --> ModelRouter
    AnthropicAPI --> ModelRouter
    OpenAIAPI --> ModelRouter
    
    ModelName --> ModelRouter
    ModelURL --> ModelRouter
    APIKeys --> ModelRouter
```

### Inference Server Launch Parameters

Launch scripts accept three parameters: tensor parallelism, port, and seed.

**Example Usage:**
```bash
# Launch GLM-4.5-Air with TP=8, port=24444, seed=42
bash launch_glm45.sh 8 24444 42
```

| Script | Model | Server Format | Example URL |
|--------|-------|--------------|-------------|
| `launch_glm45.sh` | GLM-4.5-Air | OpenAI-compatible | `http://hostname:24444/v1` |
| `launch_glm46.sh` | GLM-4.6 | OpenAI-compatible | `http://hostname:24445/v1` |
| `launch_qwen3_models.sh` | Qwen family | OpenAI-compatible | `http://hostname:24446/v1` |

**Sources:** [README.md:19-31](), [sera/datagen/inference/launch_glm45.sh](), [sera/datagen/inference/launch_glm46.sh](), [sera/datagen/inference/launch_qwen3_models.sh]()

---

## GitHub Integration and Repository Mirroring

SERA requires GitHub organization infrastructure for mirroring repositories when working with personal codebases. This enables Docker container creation and persistent repository access.

### GitHub Mirroring Architecture

```mermaid
graph TB
    subgraph SourceRepos["Source Repositories"]
        PrivateRepo["Private Repository"]
        PublicRepo["Public Repository"]
        CustomRepo["Custom Repository"]
    end
    
    subgraph MirrorOrg["GitHub Mirror Organization"]
        OCARepos["oca-repos<br/>Public Mirror Org"]
        CustomOrg["Custom Org<br/>Private Mirrors"]
    end
    
    subgraph DockerRegistry["Docker Registry"]
        PublicImages["Public Docker Org<br/>Public Images"]
        PrivateImages["Custom Docker Org<br/>Private Images"]
    end
    
    subgraph GenerateProcess["Generate Stage Process"]
        CloneMirror["Clone from Mirror"]
        BuildContainer["Build Docker Image"]
        PushImage["Push to Registry"]
        PersistImage["Persistent Storage"]
    end
    
    subgraph Configuration["Configuration Settings"]
        GHMirrorOrg["generate.docker.gh_mirror_org<br/>oca-repos or custom"]
        DockerOrgSetting["generate.docker.docker_org<br/>Optional for persistence"]
    end
    
    PrivateRepo --> CustomOrg
    PublicRepo --> OCARepos
    CustomRepo --> OCARepos
    CustomRepo --> CustomOrg
    
    OCARepos --> CloneMirror
    CustomOrg --> CloneMirror
    
    CloneMirror --> BuildContainer
    BuildContainer --> PushImage
    
    PushImage --> PublicImages
    PushImage --> PrivateImages
    
    PublicImages --> PersistImage
    PrivateImages --> PersistImage
    
    GHMirrorOrg --> CloneMirror
    DockerOrgSetting --> PushImage
```

### Repository Mirroring Configuration

| Setting | Purpose | Default | Notes |
|---------|---------|---------|-------|
| `gh_mirror_org` | GitHub org for repository mirrors | `oca-repos` | Public visibility warning |
| `docker_org` | Docker org for image persistence | None | Requires push permissions |

**Important:** The `oca-repos` organization is publicly accessible. Any repositories mirrored there will be publicly viewable. For private codebases, create a custom GitHub organization.

**Sources:** [README.md:80-128](), [README.md:57-58]()

---

## PR Issues Scraping

SERA includes functionality to scrape historical pull request issues from GitHub repositories, which are then used as demonstrations in the distillation stages.

### PR Issues Scraping Workflow

```mermaid
graph LR
    subgraph ScrapingScript["scrape_github.py"]
        OrgParam["-o ORG_NAME"]
        RepoParam["-n REPO_NAME"]
        CountParam["-c N_ISSUES"]
    end
    
    subgraph GitHubAPI["GitHub API"]
        FetchIssues["Fetch Historical Issues"]
        IssueMetadata["Issue Text + Metadata"]
    end
    
    subgraph OutputStorage["pr_issues/ Directory"]
        GeneratedJSON["generated.json<br/>List of Issues"]
    end
    
    subgraph PipelineIntegration["Pipeline Integration"]
        PipelineRepo["distill.args.pipeline_repo<br/>Configuration Parameter"]
        DistillStageTwo["Distill Stage Two<br/>Uses as Demonstrations"]
    end
    
    OrgParam --> FetchIssues
    RepoParam --> FetchIssues
    CountParam --> FetchIssues
    
    FetchIssues --> IssueMetadata
    IssueMetadata --> GeneratedJSON
    
    GeneratedJSON --> PipelineRepo
    PipelineRepo --> DistillStageTwo
```

**Script Usage:**
```bash
python scrape_github.py -o ORG_NAME -n REPO_NAME -c N_ISSUES
```

**Pipeline Integration:**
```bash
python sera/main.py \
    --config-name=specialization_personal \
    distill.args.pipeline_repo=pr_issues/generated.json
```

**Sources:** [README.md:157-169](), [.gitignore:7]()

---

## Horizontal Scaling with Sharding

SERA supports horizontal scaling through dataset sharding, enabling parallel data generation across multiple inference servers. This is essential for large-scale data generation runs.

### Sharding Architecture

```mermaid
graph TB
    subgraph DatasetSharding["Dataset Sharding"]
        FullDataset["Complete Dataset"]
        Shard0["Shard 0<br/>distill.shard=0"]
        Shard1["Shard 1<br/>distill.shard=1"]
        Shard2["Shard 2<br/>distill.shard=2"]
        Shard3["Shard 3<br/>distill.shard=3"]
    end
    
    subgraph InferenceServers["Inference Server Pool"]
        Server1["Server 1<br/>URL_1:24444"]
        Server2["Server 2<br/>URL_2:24445"]
        Server3["Server 3<br/>URL_3:24446"]
        Server4["Server 4<br/>URL_4:24447"]
    end
    
    subgraph ParallelReplicas["Parallel Execution"]
        Replica0["Replica 0<br/>shard=0<br/>total_shards=4"]
        Replica1["Replica 1<br/>shard=1<br/>total_shards=4"]
        Replica2["Replica 2<br/>shard=2<br/>total_shards=4"]
        Replica3["Replica 3<br/>shard=3<br/>total_shards=4"]
    end
    
    subgraph OutputAggregation["Output Aggregation"]
        IndividualOutputs["Individual Shard Outputs"]
        MergedDataset["Merged Final Dataset"]
    end
    
    FullDataset --> Shard0
    FullDataset --> Shard1
    FullDataset --> Shard2
    FullDataset --> Shard3
    
    Shard0 --> Replica0
    Shard1 --> Replica1
    Shard2 --> Replica2
    Shard3 --> Replica3
    
    Server1 --> Replica0
    Server2 --> Replica1
    Server3 --> Replica2
    Server4 --> Replica3
    
    Replica0 --> IndividualOutputs
    Replica1 --> IndividualOutputs
    Replica2 --> IndividualOutputs
    Replica3 --> IndividualOutputs
    
    IndividualOutputs --> MergedDataset
```

### Sharding Configuration Parameters

| Parameter | Purpose | Value Range | Example |
|-----------|---------|-------------|---------|
| `distill.shard` | Current shard index | 0 to N-1 | `0` |
| `distill.total_shards` | Total number of shards | 1 to N | `4` |
| `distill.model.url` | Server URL for this shard | Valid URL | `http://server1:24444/v1` |

**Example Multi-Server Launch:**

```bash
# Replica 0
python sera/main.py \
    --config-name=swesmith_scaling \
    distill.shard=0 \
    distill.total_shards=4 \
    distill.model.url=URL_1

# Replica 1
python sera/main.py \
    --config-name=swesmith_scaling \
    distill.shard=1 \
    distill.total_shards=4 \
    distill.model.url=URL_2
```

**Use Case:** The SERA team uses this approach to scale SWESmith data generation to create the largest datasets, distributing workload across multiple GPU servers.

**Sources:** [README.md:96-122]()

---

## Fault Tolerance and Stage Resumption

SERA implements comprehensive fault tolerance through stage-based checkpointing and resumption capabilities. This is critical for large-scale runs where occasional model stalls (< 1%) can interrupt pipeline completion.

### Stage Resumption Architecture

```mermaid
graph TB
    subgraph InitialRun["Initial Run"]
        StartPipeline["Start Pipeline<br/>stage=pipeline"]
        ExecGenerate["Execute generate"]
        ExecDistillOne["Execute distill_stage_one"]
        StallDetected["Stall Detected<br/>Few trajectories hang"]
        UserKill["User Kills Process"]
    end
    
    subgraph StatePreservation["State Preservation"]
        SavedName["Experiment name Saved"]
        SavedOutputs["outputs/ Checkpointed"]
        SavedExperiments["experiments/ Preserved"]
        SavedLogs["logs/ Available"]
    end
    
    subgraph ResumeOptions["Resume Options"]
        ResumeAuto["Resume Automatically<br/>Same name + stage"]
        ResumeSkip["Skip to Next Stage<br/>stage=distill_stage_two"]
        ResumeRerun["Rerun Current Stage<br/>stage=distill_stage_one"]
    end
    
    subgraph ResumedExecution["Resumed Execution"]
        LoadState["Load Previous State"]
        SkipCompleted["Skip Completed Trajectories"]
        ContinueFromStage["Continue from Specified Stage"]
        CompleteRun["Complete Remaining Stages"]
    end
    
    StartPipeline --> ExecGenerate
    ExecGenerate --> ExecDistillOne
    ExecDistillOne --> StallDetected
    StallDetected --> UserKill
    
    UserKill --> SavedName
    UserKill --> SavedOutputs
    UserKill --> SavedExperiments
    UserKill --> SavedLogs
    
    SavedName --> ResumeAuto
    SavedName --> ResumeSkip
    SavedName --> ResumeRerun
    
    ResumeAuto --> LoadState
    ResumeSkip --> LoadState
    ResumeRerun --> LoadState
    
    LoadState --> SkipCompleted
    SkipCompleted --> ContinueFromStage
    ContinueFromStage --> CompleteRun
```

### Stage Map Reference

The `stage_map` dictionary in `sera/main.py` defines the resumption points:

```python
stage_map = {
    "pipeline": -1,           # Full pipeline execution
    "generate": 0,            # Initial generation
    "distill_stage_one": 1,   # First distillation
    "distill_stage_two": 2,   # Second distillation
    "eval": 3,                # Evaluation
    "postprocess": 4          # Final processing
}
```

### Resumption Examples

**Automatic Resume (Same Name):**
```bash
# Original run that stalled
python sera/main.py --config-name=specialization_django

# Rerun with same name - automatically resumes
python sera/main.py --config-name=specialization_django
```

**Skip to Next Stage:**
```bash
# Skip hanging trajectories, proceed to stage 2
python sera/main.py \
    --config-name=specialization_django \
    stage=distill_stage_two
```

**Resume from Specific Stage:**
```bash
# Resume from evaluation stage
python sera/main.py \
    --config-name=specialization_django \
    stage=eval
```

### Resumption Behavior

| Scenario | Behavior | Output |
|----------|----------|--------|
| Same experiment name, no stage parameter | Resume from last incomplete stage | Continue where left off |
| Same experiment name, explicit stage | Skip to specified stage | Use previous successful outputs |
| Different experiment name | Start fresh pipeline | New outputs directory |
| Hanging trajectories | Skip failed attempts | Proceed with successful ones |

**Sources:** [README.md:130-156]()

---

## Single Server Execution Modes

SERA provides pre-configured execution modes for common scenarios, each optimized for specific use cases. These modes can be run with a single inference server.

### Execution Mode Comparison

```mermaid
graph TB
    subgraph DjangoMode["Django/Sympy Specialization"]
        DjangoConfig["specialization_django.yaml"]
        DjangoTarget["SWE-Bench Repositories"]
        DjangoFeatures["Pre-tested Codebases<br/>Established Test Suites"]
    end
    
    subgraph PersonalMode["Personal Repository Specialization"]
        PersonalConfig["specialization_personal.yaml"]
        PersonalTarget["Custom Codebases"]
        PersonalFeatures["Flexible Configuration<br/>Custom Install Commands"]
    end
    
    subgraph AnthropicMode["Closed-Source Model Mode"]
        AnthropicConfig["specialization_anthropic.yaml"]
        AnthropicTarget["Claude/GPT Models"]
        AnthropicFeatures["No Inference Server<br/>API-based Generation"]
    end
    
    subgraph SharedComponents["Shared Components"]
        MainOrchestrator["sera/main.py"]
        ConfigOverrides["CLI Parameter Overrides"]
        PipelineStages["Five-Stage Pipeline"]
    end
    
    DjangoConfig --> MainOrchestrator
    PersonalConfig --> MainOrchestrator
    AnthropicConfig --> MainOrchestrator
    
    MainOrchestrator --> ConfigOverrides
    ConfigOverrides --> PipelineStages
```

### Django/Sympy Specialization

**Purpose:** Generate data from well-established SWE-Bench repositories with existing test suites.

**Command:**
```bash
python sera/main.py \
    --config-name=specialization_django \
    distill.model.name=openai/GLM-4.5-Air \
    distill.model.url=http://server:24444/v1
```

**Characteristics:**
- Pre-configured repository settings
- Established installation procedures
- Existing test commands
- SWE-Bench compatibility

### Personal Repository Specialization

**Purpose:** Generate data from custom codebases with user-defined configurations.

**Command:**
```bash
python sera/main.py \
    --config-name=specialization_personal \
    distill.model.name=openai/GLM-4.5-Air \
    distill.model.url=http://server:24444/v1 \
    generate.docker.gh_mirror_org=oca-repos
```

**Required Configurations:**
- `org_name`: GitHub organization
- `install_cmds`: Installation commands
- `top_level_folder`: Main code directory
- `python_version`: Python version for Docker
- `commits`: Specific commit hashes

### Closed-Source Model Mode

**Purpose:** Use commercial APIs (Anthropic, OpenAI) without managing inference servers.

**Command:**
```bash
python sera/main.py \
    --config-name=specialization_anthropic \
    generate.docker.gh_mirror_org=oca-repos
```

**Characteristics:**
- No `distill.model.url` required
- API keys via environment variables
- Built-in rate limiting
- Multiple provider support

**Sources:** [README.md:38-94](), [sera/configs/specialization_django.yaml](), [sera/configs/specialization_personal.yaml](), [sera/configs/specialization_anthropic.yaml]()

---

## Output Artifacts and Data Products

The SERA pipeline produces multiple types of artifacts across different stages, each serving specific purposes in the data generation workflow.

### Artifact Generation Flow

```mermaid
graph LR
    subgraph GitIgnoredArtifacts["Git-Ignored Artifacts"]
        LogsDir["logs/<br/>Execution Logs"]
        ReposDir["repos/<br/>Cloned Repositories"]
        ExperimentsDir["experiments/<br/>Intermediate Data"]
        OutputsDir["outputs/<br/>Final Datasets"]
        MetadataDir["metadata/<br/>Experiment Tracking"]
    end
    
    subgraph ArtifactTypes["Artifact Types by Stage"]
        GenerateArtifacts["Generate:<br/>Docker images<br/>Repository clones"]
        DistillArtifacts["Distill:<br/>Trajectories<br/>Rollouts"]
        EvalArtifacts["Eval:<br/>Metrics<br/>Evaluation results"]
        PostprocessArtifacts["Postprocess:<br/>Training datasets<br/>JSONL files"]
    end
    
    subgraph TrainingData["Training Data Products"]
        DatasetCache["sera/datagen/train/dataset_cache"]
        WandbLogs["sera/datagen/train/wandb"]
        FinalJSONL["Final training JSONL"]
    end
    
    GenerateArtifacts --> ReposDir
    GenerateArtifacts --> LogsDir
    
    DistillArtifacts --> ExperimentsDir
    DistillArtifacts --> LogsDir
    
    EvalArtifacts --> ExperimentsDir
    EvalArtifacts --> MetadataDir
    
    PostprocessArtifacts --> OutputsDir
    PostprocessArtifacts --> LogsDir
    
    OutputsDir --> DatasetCache
    OutputsDir --> FinalJSONL
```

### Directory Structure and Contents

| Directory | Stage | Content Type | Example Files |
|-----------|-------|--------------|---------------|
| `logs/` | All | Execution logs, debugging info | `pipeline.log`, `stage_*.log` |
| `repos/` | Generate | Cloned Git repositories | `django/`, `sympy/` |
| `experiments/` | Distill, Eval | Intermediate generation outputs | `rollout_*.json`, `metrics_*.json` |
| `outputs/` | Postprocess | Final training datasets | `training_data.jsonl` |
| `metadata/` | All | Experiment tracking data | `experiment_*.json` |
| `pr_issues/` | User script | Scraped GitHub issues | `repo_name_issues.json` |

### Training Data Integration

The final outputs are designed for integration with the training pipeline documented in `sera/datagen/train`:

- **Dataset Cache:** Processed datasets ready for training ([sera/datagen/train/dataset_cache]())
- **Weights & Biases:** Experiment tracking logs ([sera/datagen/train/wandb]())
- **JSONL Format:** Standard training data format

**Sources:** [.gitignore:1-13](), [README.md:172-173]()

---

## Summary

The SERA Data Generation System implements a sophisticated multi-stage pipeline for creating software engineering training data from language models. Key capabilities include:

1. **Multi-Stage Pipeline:** Five sequential stages (generate, distill×2, eval, postprocess) with individual resumption points
2. **Flexible Inference:** Support for both open-source model servers and closed-source APIs
3. **Horizontal Scaling:** Sharding support for parallel processing across multiple servers
4. **Fault Tolerance:** Stage-based checkpointing and automatic resumption
5. **Multiple Specializations:** Pre-configured modes for Django/Sympy, personal repositories, and closed-source models
6. **GitHub Integration:** Repository mirroring and Docker image persistence
7. **PR Issues Scraping:** Automated collection of historical issues for demonstrations

The system is designed for large-scale data generation with robust error handling and flexible configuration, supporting both research experimentation and production data pipelines.

For detailed information on specific subsystems, see:
- [Installation and Setup](#2.1)
- [Inference Servers](#2.2)
- [Specialization Configurations](#2.3)
- [Pipeline Stages](#2.4)
- [Multi-Server Scaling](#2.5)

**Sources:** [README.md:1-184](), [.gitignore:1-227](), [sera/config_schema.py]()

---

