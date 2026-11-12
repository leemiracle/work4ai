# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)
- [.github/actions/workflow-results/action.yml](.github/actions/workflow-results/action.yml)

</details>



The CCCL-GHA repository provides a GitHub Actions workflow orchestration system for NVIDIA's CCCL (CUDA C++ Core Libraries) project. This system transforms a declarative matrix configuration into hundreds of parallelized CI/CD jobs that build and test multiple combinations of projects, compilers, CUDA versions, C++ standards, and hardware architectures.

This page provides a high-level introduction to the system architecture, core concepts, and data flow. For detailed configuration of `matrix.yaml`, see [Configuration Guide](#2). For workflow generation internals, see [Workflow Generation](#3). For job execution details, see [Job Execution](#5).

## System Purpose

CCCL-GHA addresses the challenge of testing a complex C++/CUDA codebase across a large matrix of configurations:
- Multiple projects (libcudacxx, CUB, Thrust)
- Multiple CUDA Toolkit versions
- Multiple host compilers (GCC, Clang, MSVC) with various versions
- Multiple C++ standards
- Multiple GPU architectures
- Both Linux and Windows operating systems

The system automates the generation, scheduling, execution, and reporting of these jobs while minimizing redundant builds through artifact sharing (producer/consumer pattern) and distributed compilation caching (sccache).

Sources: [.github/actions/workflow-build/action.yml:1-4](), [.github/actions/workflow-build/build-workflow.py:1-54]()

## High-Level Architecture

The system operates in four distinct phases:

```mermaid
graph LR
    Configuration["Configuration<br/>matrix.yaml"]
    Generation["Workflow Generation<br/>workflow-build action"]
    Dispatch["Job Dispatch<br/>dispatch workflows"]
    Execution["Job Execution<br/>run-job workflows"]
    Results["Results Collection<br/>workflow-results action"]
    
    Configuration --> Generation
    Generation --> Dispatch
    Dispatch --> Execution
    Execution --> Results
```

**Diagram: Four-Phase Architecture**

### Phase 1: Configuration

The `matrix.yaml` file defines all possible job combinations using a concise tag-based syntax. Each job specifies:
- `project`: Which CCCL component to build/test
- `jobs`: What operations to perform (build, test, etc.)
- `ctk`: CUDA Toolkit version
- `cxx`: Host compiler
- `cudacxx`: Device compiler (nvcc, clang)
- `std`: C++ standard
- `gpu`: Target GPU architecture
- Additional tags as needed

Sources: [.github/actions/workflow-build/build-workflow.py:4-24]()

### Phase 2: Workflow Generation

The `workflow-build` action transforms `matrix.yaml` into executable job definitions:

```mermaid
graph TB
    Input["matrix.yaml"]
    BuildPy["build-workflow.py"]
    PreparePy["prepare-workflow-dispatch.py"]
    WorkflowJSON["workflow.json"]
    DispatchJSON["dispatch.json"]
    
    Input --> BuildPy
    BuildPy --> WorkflowJSON
    WorkflowJSON --> PreparePy
    PreparePy --> DispatchJSON
    
    subgraph "Processing Pipeline"
        BuildPy
        PreparePy
    end
    
    subgraph "Output Artifacts"
        WorkflowJSON
        DispatchJSON
    end
```

**Diagram: Workflow Generation Pipeline**

The `build-workflow.py` script performs multi-stage processing:
1. Validates tags against schema
2. Sets default values
3. Explodes list values into individual jobs
4. Canonicalizes compiler names
5. Derives values (e.g., SM architecture from GPU name)
6. Applies exclusion rules
7. Groups jobs by dispatch category

Sources: [.github/actions/workflow-build/action.yml:74-109](), [.github/actions/workflow-build/build-workflow.py:811-919]()

### Phase 3: Job Dispatch

The `dispatch.json` file categorizes jobs into four groups:

| Category | OS | Pattern | Description |
|----------|----|---------| ------------|
| `linux_standalone` | Linux | Standalone | Independent jobs with no dependencies |
| `linux_two_stage` | Linux | Producer→Consumer | Build artifacts shared with test jobs |
| `windows_standalone` | Windows | Standalone | Independent jobs with no dependencies |
| `windows_two_stage` | Windows | Producer→Consumer | Build artifacts shared with test jobs |

Each category maps to a dedicated dispatch workflow that uses GitHub Actions matrix strategies to parallelize execution.

Sources: [.github/actions/workflow-build/build-workflow.py:28-35](), [.github/actions/workflow-build/build-workflow.py:507-539]()

### Phase 4: Job Execution

Jobs execute in isolated environments:
- **Linux**: Docker-outside-of-Docker (DOOD) pattern using devcontainers
- **Windows**: Native Docker containers

Each job produces artifacts including success markers, sccache statistics, and test results.

Sources: [.github/actions/workflow-build/build-workflow.py:379-445]()

### Phase 5: Results Collection

The `workflow-results` action aggregates job outcomes:

```mermaid
graph TB
    Download["Download Artifacts"]
    Fetch["Fetch Job Timing"]
    Parse["parse-job-times.py"]
    Summary["prepare-execution-summary.py"]
    Final["final-summary.py"]
    Verify["verify-job-success.py"]
    
    Output1["GitHub Step Summary"]
    Output2["PR Comment"]
    Output3["Slack Notifications"]
    Output4["SUCCESS Output"]
    
    Download --> Parse
    Fetch --> Parse
    Parse --> Summary
    Summary --> Final
    Final --> Output1
    Final --> Output2
    Final --> Output3
    Download --> Verify
    Verify --> Output4
```

**Diagram: Results Collection Pipeline**

The system generates comprehensive reports including:
- Pass/fail status by project and configuration
- Timing breakdown with overhead analysis
- sccache hit rate statistics
- Identification of "likely culprits" for failures

Sources: [.github/actions/workflow-results/action.yml:30-128]()

## Key Concepts

### Matrix Jobs

A **matrix job** is a single entry in the `matrix.yaml` workflow definition. Example:

```json
{
  "project": "libcudacxx",
  "jobs": ["build", "test"],
  "ctk": "12.0",
  "cxx": "gcc12",
  "cudacxx": "nvcc",
  "std": 17,
  "gpu": "t4"
}
```

Matrix jobs are processed into one or more **dispatch jobs** after tag explosion, canonicalization, and exclusion filtering.

Sources: [.github/actions/workflow-build/build-workflow.py:4-24]()

### Dispatch Groups

A **dispatch group** organizes related jobs together for UI clarity. Jobs in the same group share:
- Project
- CUDA Toolkit version  
- Compiler toolchain

Example dispatch group name: `"libcudacxx CTK12.0 nvcc GCC12"`

Sources: [.github/actions/workflow-build/build-workflow.py:345-359]()

### Job Patterns

**Standalone Jobs**: Execute independently with no dependencies. Example: a build-and-test job in a single step.

**Two-Stage Jobs**: Producer/consumer pattern where a build job creates artifacts consumed by multiple test configurations:

```mermaid
graph LR
    Producer["Producer<br/>(Build)"]
    Consumer1["Consumer 1<br/>(Test: GPU A)"]
    Consumer2["Consumer 2<br/>(Test: GPU B)"]
    Consumer3["Consumer 3<br/>(Test: Config C)"]
    
    Producer --> Consumer1
    Producer --> Consumer2
    Producer --> Consumer3
```

**Diagram: Two-Stage Producer/Consumer Pattern**

Sources: [.github/actions/workflow-build/build-workflow.py:493-504](), [.github/actions/workflow-build/build-workflow.py:517-534]()

### Devcontainers

**Devcontainers** are Docker images containing specific CUDA Toolkit and compiler versions. The system uses images from the `rapidsai/devcontainers` repository with the format:

- Linux: `rapidsai/devcontainers:{version}-cpp-{compiler}-cuda{ctk}`
- Windows: `rapidsai/devcontainers:{version}-cuda{ctk}-{compiler}`

The `.devcontainer/launch.sh` script selects and launches the appropriate container based on job requirements.

Sources: [.github/actions/workflow-build/build-workflow.py:404-412]()

### Job Artifacts

Each job produces artifacts in the `jobs/{job_id}/` directory:

| Artifact | Purpose |
|----------|---------|
| `success` | Marker file indicating job completion |
| `sccache_stats.json` | Compilation cache statistics |
| `cccl_meta_bench.csv` | Benchmark results (if applicable) |

Sources: [.github/actions/workflow-results/action.yml:36-42]()

## Data Flow

The following diagram maps the complete data flow from configuration to results:

```mermaid
graph TB
    MatrixYAML["matrix.yaml<br/>(Configuration)"]
    
    BuildWorkflowPy["build-workflow.py<br/>(Generation Script)"]
    PrepareDispatchPy["prepare-workflow-dispatch.py<br/>(Dispatch Splitter)"]
    
    WorkflowJSON["workflow.json<br/>(Full Job Specs)"]
    DispatchJSON["dispatch.json<br/>(Categorized Jobs)"]
    JobIDsJSON["job_ids.json<br/>(ID Mappings)"]
    
    DispatchWorkflows["workflow-dispatch-*-group-*<br/>(Dispatch Workflows)"]
    TwoStageWorkflows["workflow-dispatch-two-stage-*<br/>(Two-Stage Orchestration)"]
    RunJobWorkflows["workflow-run-job-*<br/>(Execution Workflows)"]
    
    JobArtifacts["jobs/{job_id}/<br/>(Job Artifacts)"]
    
    ParseTimePy["parse-job-times.py"]
    PrepareExecPy["prepare-execution-summary.py"]
    FinalSummaryPy["final-summary.py"]
    VerifySuccessPy["verify-job-success.py"]
    
    JobTimesJSON["results/job_times.json"]
    ExecSummaries["execution/*_summary.json"]
    
    GHSummary["GitHub Step Summary"]
    PRComment["PR Comment"]
    SlackNotif["Slack Notifications"]
    
    MatrixYAML --> BuildWorkflowPy
    BuildWorkflowPy --> WorkflowJSON
    BuildWorkflowPy --> JobIDsJSON
    WorkflowJSON --> PrepareDispatchPy
    PrepareDispatchPy --> DispatchJSON
    
    DispatchJSON --> DispatchWorkflows
    DispatchWorkflows --> RunJobWorkflows
    DispatchWorkflows --> TwoStageWorkflows
    TwoStageWorkflows --> RunJobWorkflows
    
    RunJobWorkflows --> JobArtifacts
    
    JobArtifacts --> ParseTimePy
    ParseTimePy --> JobTimesJSON
    JobTimesJSON --> PrepareExecPy
    PrepareExecPy --> ExecSummaries
    ExecSummaries --> FinalSummaryPy
    JobArtifacts --> VerifySuccessPy
    
    FinalSummaryPy --> GHSummary
    FinalSummaryPy --> PRComment
    FinalSummaryPy --> SlackNotif
```

**Diagram: Complete Data Flow with File Names**

Sources: [.github/actions/workflow-build/action.yml:1-140](), [.github/actions/workflow-results/action.yml:1-213]()

## Integration Points

The system integrates with external services:

### GitHub Actions API

- **Workflow Artifacts**: Upload/download job outputs
- **Job Timing Data**: Fetch execution duration via REST API
- **PR Comments**: Post results to pull requests
- **Step Summary**: Display results inline in workflow UI

Sources: [.github/actions/workflow-results/action.yml:30-34](), [.github/actions/workflow-results/action.yml:59-90](), [.github/actions/workflow-results/action.yml:130-153]()

### AWS S3 (sccache)

The system uses `sccache` for distributed compilation caching. Jobs access the `rapids-sccache-devs` S3 bucket using AWS credentials configured at runtime.

### Slack API

Notifications are sent to two channels:
- **Log Channel**: All workflow events (start, completion)
- **Alert Channel**: Failures only

Sources: [.github/actions/workflow-build/action.yml:47-59](), [.github/actions/workflow-build/action.yml:126-139](), [.github/actions/workflow-results/action.yml:179-212]()

## System Characteristics

| Characteristic | Implementation |
|----------------|----------------|
| **Scalability** | Matrix parallelization creates hundreds of concurrent jobs |
| **Efficiency** | Producer/consumer pattern avoids redundant builds; sccache reduces compilation time |
| **Isolation** | Devcontainers ensure reproducible builds |
| **Visibility** | Multi-channel reporting (GitHub UI, PR comments, Slack) |
| **Flexibility** | Declarative configuration supports complex job matrices |
| **Change Detection** | `inspect-changes` mechanism skips irrelevant jobs on PRs |

Sources: [.github/actions/workflow-build/action.yml:12-19]()

## Workflow Entry Points

Users interact with the system through two primary GitHub Actions:

### workflow-build Action

**Location**: `.github/actions/workflow-build/action.yml`

**Inputs**:
- `workflows`: Space-separated workflow names to execute
- `matrix_file`: Path to `matrix.yaml` (default: `ci/matrix.yaml`)
- `allow_override`: Enable override workflow mechanism
- `inspect_changes_script`: Script for change detection
- Slack tokens and channel IDs for notifications

**Outputs**:
- `workflow`: JSON object containing `dispatch.json` content

Sources: [.github/actions/workflow-build/action.yml:1-42]()

### workflow-results Action

**Location**: `.github/actions/workflow-results/action.yml`

**Inputs**:
- `github_token`: For PR comments
- `pr_number`: PR to comment on
- Slack tokens and channel IDs for notifications

**Outputs**:
- `success`: Boolean indicating whether all jobs passed

Sources: [.github/actions/workflow-results/action.yml:1-24]()

## Example Workflow Lifecycle

A typical workflow execution follows this sequence:

1. **Trigger**: PR opened or commit pushed
2. **Generation**: `workflow-build` action reads `matrix.yaml`, applies change detection, generates `dispatch.json`
3. **Dispatch**: Four group dispatch workflows distribute jobs across runners
4. **Execution**: Jobs run in parallel in isolated devcontainers
5. **Artifact Upload**: Each job uploads success markers and statistics
6. **Collection**: `workflow-results` action downloads artifacts, fetches timing data
7. **Analysis**: Python scripts parse results, identify failures, calculate statistics
8. **Reporting**: Summary posted to GitHub UI, PR comments, and Slack

Sources: [.github/actions/workflow-build/action.yml:61-109](), [.github/actions/workflow-results/action.yml:30-128]()

---

This overview provides the foundation for understanding CCCL-GHA. For detailed documentation on specific subsystems, refer to the child pages in this wiki.

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)
- [.github/actions/workflow-build/prepare-workflow-dispatch.py](.github/actions/workflow-build/prepare-workflow-dispatch.py)

</details>



## Purpose and Scope

This document describes the four-phase architecture of the CCCL GitHub Actions workflow orchestration system. It explains how the system transforms a declarative job matrix configuration into distributed, containerized CI/CD execution across Linux and Windows runners, and how data flows between the Configuration, Generation, Dispatch, and Execution phases.

For detailed information about specific configuration syntax, see [Configuration Guide](#2). For implementation details of individual execution environments, see [Job Execution](#5). For result aggregation mechanisms, see [Results and Reporting](#6).

## Architectural Overview

The system implements a pipeline architecture consisting of four sequential phases:

```mermaid
graph LR
    Configuration["Configuration Phase<br/>matrix.yaml<br/>.devcontainer/*"]
    Generation["Generation Phase<br/>build-workflow.py<br/>prepare-workflow-dispatch.py"]
    Dispatch["Dispatch Phase<br/>workflow-dispatch-*-group-*"]
    Execution["Execution Phase<br/>workflow-run-job-*<br/>workflow-dispatch-two-stage-*"]
    
    Configuration --> Generation
    Generation --> Dispatch
    Dispatch --> Execution
```

**Sources:** [.github/actions/workflow-build/action.yml:1-140](), [.github/actions/workflow-build/build-workflow.py:1-100]()

### Phase Responsibilities

| Phase | Primary Function | Key Inputs | Key Outputs |
|-------|-----------------|------------|-------------|
| Configuration | Define job matrix | `matrix.yaml`, `.devcontainer/` configs | Human-readable job specifications |
| Generation | Transform and optimize | Matrix definitions, change detection data | `workflow.json`, `dispatch.json` |
| Dispatch | Route and parallelize | `dispatch.json` by OS and pattern | Matrix-parallelized GitHub Actions jobs |
| Execution | Run commands | Job specifications, runner assignment | Build/test results, artifacts |

**Sources:** [.github/actions/workflow-build/build-workflow.py:1-60](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:1-20]()

## Configuration Layer

The configuration layer provides declarative definitions of all possible job combinations through two primary sources:

```mermaid
graph TB
    MatrixYAML["matrix.yaml"]
    DevContainer[".devcontainer/"]
    
    MatrixYAML --> Projects["projects:<br/>libcudacxx, cub, thrust"]
    MatrixYAML --> CTK["ctk_versions:<br/>11.1, 12.0, etc."]
    MatrixYAML --> HostCompilers["host_compilers:<br/>gcc, clang, msvc"]
    MatrixYAML --> DeviceCompilers["device_compilers:<br/>nvcc, clang"]
    MatrixYAML --> GPUs["gpus:<br/>t4, v100, a100"]
    MatrixYAML --> Jobs["jobs:<br/>build, test, examples"]
    MatrixYAML --> Workflows["workflows:<br/>pull_request, nightly"]
    
    DevContainer --> Images["Container definitions<br/>per CUDA+compiler combo"]
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:113-303](), [.github/actions/workflow-build/action.yml:20-23]()

The `matrix.yaml` file defines:
- **Projects**: Individual CCCL components (`libcudacxx`, `cub`, `thrust`)
- **CTK versions**: CUDA Toolkit versions with metadata like supported standards
- **Host compilers**: GCC, Clang, MSVC with version ranges and aliases
- **Device compilers**: NVCC, Clang with capability mappings
- **GPUs**: Physical hardware identifiers with SM architecture mappings
- **Jobs**: Build, test, example tasks with dependency relationships
- **Workflows**: Named collections of matrix jobs (e.g., `pull_request`, `nightly`)

**Sources:** [.github/actions/workflow-build/build-workflow.py:113-303]()

## Workflow Generation Phase

The generation phase transforms the declarative matrix into executable job specifications through a multi-stage processing pipeline.

### Generation Pipeline Components

```mermaid
graph TB
    Input["workflow-build Action<br/>.github/actions/workflow-build/action.yml"]
    
    InspectChanges["inspect-changes step<br/>Optional change detection"]
    BuildWorkflow["build-workflow.py<br/>Matrix transformation pipeline"]
    PrepareDispatch["prepare-workflow-dispatch.py<br/>OS/pattern splitting"]
    
    Input --> InspectChanges
    InspectChanges --> BuildWorkflow
    BuildWorkflow --> PrepareDispatch
    
    InspectChanges -.->|dirty_projects| BuildWorkflow
    
    BuildWorkflow --> WorkflowJSON["workflow/workflow.json"]
    BuildWorkflow --> JobIDs["workflow/job_ids.json"]
    BuildWorkflow --> RunnerSummary["workflow/runner_summary.json"]
    BuildWorkflow --> JobList["workflow/job_list.txt"]
    
    PrepareDispatch --> DispatchJSON["workflow/dispatch.json"]
    
    WorkflowJSON --> PrepareDispatch
```

**Sources:** [.github/actions/workflow-build/action.yml:61-109](), [.github/actions/workflow-build/build-workflow.py:922-1048]()

### build-workflow.py Processing Stages

The `build-workflow.py` script implements a sophisticated ETL pipeline:

```mermaid
graph TB
    MatrixInput["parse_workflow_matrix_jobs()<br/>Line 922"]
    
    Validate["validate_tags()<br/>Line 811-832<br/>Schema validation"]
    SetDefaults["set_default_tags()<br/>Line 834-843<br/>Apply defaults"]
    Explode["explode_tags()<br/>Line 886-899<br/>List → individual jobs"]
    Canonicalize["canonicalize_tags()<br/>Line 845-850<br/>Resolve aliases"]
    Derived["set_derived_tags()<br/>Line 852-875<br/>Compute sm, std, deps"]
    Exclude["remove_excluded_jobs()<br/>Line 796-808<br/>Filter exclusions"]
    ToDispatch["matrix_job_to_dispatch_group()<br/>Line 542-544<br/>Generate job specs"]
    Finalize["finalize_workflow_dispatch_groups()<br/>Line 583-721<br/>Deduplicate, assign IDs"]
    
    MatrixInput --> Validate
    Validate --> SetDefaults
    SetDefaults --> Explode
    Explode --> Canonicalize
    Canonicalize --> Derived
    Derived --> Explode
    Explode --> Exclude
    Exclude --> ToDispatch
    ToDispatch --> Finalize
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:811-960]()

#### Key Processing Functions

**Tag Validation** [`validate_tags()`](.github/actions/workflow-build/build-workflow.py:811-832)()
- Verifies all required tags are present
- Checks for unknown tags
- Validates GPU identifiers against defined set
- Ensures `cudacxx=clang` requires `cxx=clang`

**Tag Canonicalization** [`canonicalize_tags()`](.github/actions/workflow-build/build-workflow.py:845-850)()
- Converts CTK versions via `canonicalize_ctk_version()` [line 114-123]()
- Normalizes compiler names via `canonicalize_host_compiler_name()` [line 139-172]()
- Handles version aliases (e.g., `gcc10` → `gcc10`, `gcc` → `gcc<latest>`)

**Tag Explosion** [`explode_tags()`](.github/actions/workflow-build/build-workflow.py:886-899)()
- Recursively expands list-valued tags into individual jobs
- Example: `std: [17, 20]` generates two jobs with `std: 17` and `std: 20`
- Preserves non-exploded tags like `jobs` for scheduling optimization

**Derived Tags** [`set_derived_tags()`](.github/actions/workflow-build/build-workflow.py:852-875)()
- Computes `sm` from `gpu` when `sm: "gpu"` is specified
- Expands `std: "all"` to intersection of supported standards from CTK, compiler, and project
- Injects job dependencies from `jobs[*].needs` relationships
- Applies project-specific job mappings via `job_map`

**Sources:** [.github/actions/workflow-build/build-workflow.py:811-899]()

### Dispatch Group Generation

The `matrix_job_to_dispatch_group()` function [line 542-544]() converts matrix jobs into dispatch groups with two execution patterns:

```mermaid
graph TB
    MatrixJob["Matrix Job<br/>{project, ctk, cxx, cudacxx, ...}"]
    
    GenerateGroup["generate_dispatch_group_jobs()<br/>Line 507-539"]
    
    MatrixJob --> GenerateGroup
    
    GenerateGroup --> Standalone["standalone: []<br/>Independent jobs"]
    GenerateGroup --> TwoStage["two_stage: []<br/>Producer/consumer chains"]
    
    Standalone --> StandaloneJob["generate_dispatch_job_json()<br/>Line 481-490"]
    
    TwoStage --> Producer["producers: [job_json]"]
    TwoStage --> Consumers["consumers: [job_json, ...]"]
    
    Producer --> ProducerJob["generate_dispatch_job_json()<br/>Producer build job"]
    Consumers --> ConsumerJob["generate_dispatch_job_json()<br/>Test jobs"]
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:481-544]()

#### Job JSON Structure

Each `job_json` object contains:

| Field | Generator Function | Purpose |
|-------|-------------------|---------|
| `id` | GUID generator [line 78-96]() | Short unique identifier for GHA |
| `name` | `generate_dispatch_job_name()` [line 362-376]() | Human-readable job display name |
| `runner` | `generate_dispatch_job_runner()` [line 379-390]() | GHA runner label (OS, CPU, GPU) |
| `image` | `generate_dispatch_job_image()` [line 404-412]() | DevContainer image reference |
| `command` | `generate_dispatch_job_command()` [line 415-445]() | Shell script invocation with args |
| `cuda` | `generate_dispatch_job_ctk_version()` [line 393-395]() | CTK version for devcontainer |
| `host` | `generate_dispatch_job_host_compiler()` [line 398-401]() | Host compiler for devcontainer |
| `origin` | `generate_dispatch_job_origin()` [line 448-478]() | Metadata for result aggregation |

**Sources:** [.github/actions/workflow-build/build-workflow.py:362-490]()

### Workflow Finalization

The `finalize_workflow_dispatch_groups()` function [line 583-721]() performs critical post-processing:

**Validation** [line 586-599]():
- Ensures no two-stage group has more than one producer
- Raises error if multiple producers detected (not supported by dispatch workflows)

**Deduplication** [line 601-667]():
- Merges consumers for duplicate producers with notice messages
- Removes duplicate standalone jobs with notice messages
- Removes standalone jobs that appear as producers/consumers
- Warns about unavoidable duplicates in two-stage dependencies

**Sorting** [line 693-706]():
- Natural sort of dispatch group names (handles embedded numbers)
- Sorts jobs within groups by name

**ID Assignment** [line 708-719]():
- Assigns compact GUIDs to standalone jobs, two-stage groups, and all individual jobs
- GUIDs range from 1-3 characters, supporting up to 65,535 unique IDs

**Sources:** [.github/actions/workflow-build/build-workflow.py:583-721]()

## Dispatch Preparation

The `prepare-workflow-dispatch.py` script splits the monolithic `workflow.json` into four categorized dispatch workflows to optimize the GitHub Actions UI.

### Dispatch Splitting Logic

```mermaid
graph TB
    WorkflowJSON["workflow.json<br/>Unified job definitions"]
    
    SplitWorkflow["split_workflow()<br/>Line 25-76"]
    
    WorkflowJSON --> SplitWorkflow
    
    SplitWorkflow --> CheckOS{"is_windows(job)<br/>Line 21-22<br/>Checks runner prefix"}
    
    CheckOS -->|Linux standalone| LinuxStandalone["linux_standalone<br/>{keys, jobs}"]
    CheckOS -->|Linux two_stage| LinuxTwoStage["linux_two_stage<br/>{keys, jobs}"]
    CheckOS -->|Windows standalone| WindowsStandalone["windows_standalone<br/>{keys, jobs}"]
    CheckOS -->|Windows two_stage| WindowsTwoStage["windows_two_stage<br/>{keys, jobs}"]
    
    LinuxStandalone --> DispatchJSON["workflow/dispatch.json"]
    LinuxTwoStage --> DispatchJSON
    WindowsStandalone --> DispatchJSON
    WindowsTwoStage --> DispatchJSON
```

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:21-76]()

### Dispatch JSON Structure

Each category in `dispatch.json` contains:
- `keys`: Array of dispatch group names for matrix expansion
- `jobs`: Map of group names to job arrays or two-stage structures

The `strip_extra_info()` function [line 31-32]() removes the `origin` metadata before dispatch to reduce artifact size, as origin information is preserved in `workflow.json` for result processing.

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:31-76]()

## Dispatch Layer Architecture

The dispatch layer consumes `dispatch.json` and uses GitHub Actions matrix strategies to parallelize job execution. Four dispatch workflow types correspond to the four categories in `dispatch.json`:

```mermaid
graph TB
    DispatchJSON["workflow/dispatch.json"]
    
    DispatchJSON --> LinuxStandalone["workflow-dispatch-standalone-group-linux"]
    DispatchJSON --> LinuxTwoStage["workflow-dispatch-two-stage-group-linux"]
    DispatchJSON --> WindowsStandalone["workflow-dispatch-standalone-group-windows"]
    DispatchJSON --> WindowsTwoStage["workflow-dispatch-two-stage-group-windows"]
    
    LinuxStandalone --> LSMatrix["matrix:<br/>  group: $keys<br/>  job: $jobs[group]"]
    LinuxTwoStage --> LTMatrix["matrix:<br/>  group: $keys<br/>  pc: $jobs[group]"]
    WindowsStandalone --> WSMatrix["matrix:<br/>  group: $keys<br/>  job: $jobs[group]"]
    WindowsTwoStage --> WTMatrix["matrix:<br/>  group: $keys<br/>  pc: $jobs[group]"]
    
    LSMatrix --> RunJobLinux["workflow-run-job-linux<br/>Parallel execution"]
    LTMatrix --> TwoStageLinux["workflow-dispatch-two-stage-linux<br/>Producer → Consumers"]
    WSMatrix --> RunJobWindows["workflow-run-job-windows<br/>Parallel execution"]
    WTMatrix --> TwoStageWindows["workflow-dispatch-two-stage-windows<br/>Producer → Consumers"]
```

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:59-72]()

### Matrix Expansion Strategy

**Standalone workflows**: Each matrix entry corresponds to one job. The matrix iterates over both `group` (for organization) and `job` (the actual job specification).

**Two-stage workflows**: Each matrix entry corresponds to one producer/consumer chain (`pc`). The two-stage dispatch workflows handle dependency ordering internally.

This categorization ensures:
- No skipped jobs clutter the UI (each workflow only runs applicable jobs)
- Efficient parallelization via matrix strategies
- Clear separation between OS environments
- Proper handling of producer/consumer dependencies

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-76]()

## Execution Layer

The execution layer receives individual job specifications from the dispatch layer and runs commands in isolated containerized environments. Linux and Windows follow different execution patterns due to platform constraints.

### Linux Execution: Docker-outside-of-Docker (DOOD)

Linux jobs use an intermediate container strategy to avoid nested Docker performance issues:

```mermaid
graph TB
    DispatchJob["Job from<br/>workflow-dispatch-*"]
    
    RunJobLinux["workflow-run-job-linux"]
    
    DispatchJob --> RunJobLinux
    
    RunJobLinux --> IntermediateContainer["cruizba/ubuntu-dind:jammy-26.1.3<br/>Docker CLI + mounted socket"]
    
    IntermediateContainer --> Checkout["actions/checkout<br/>Repository code"]
    IntermediateContainer --> AWSSetup["AWS credentials<br/>for sccache"]
    IntermediateContainer --> Symlink["Path symlink<br/>match github.workspace"]
    IntermediateContainer --> LaunchScript[".devcontainer/launch.sh<br/>--cuda --host"]
    
    LaunchScript --> DevContainer["Job-specific container<br/>rapidsai/devcontainers:*"]
    
    DevContainer --> ExecuteCommand["Execute ci.sh wrapper<br/>contains COMMAND"]
    
    ExecuteCommand --> Artifacts["Upload artifacts:<br/>success, sccache_stats"]
```

The intermediate container has access to the host Docker daemon via a mounted socket, allowing it to launch devcontainers directly on the host without nesting. Path symlinks ensure the container's view of `github.workspace` matches the host path structure, which is necessary for volume mounts.

**Sources:** Based on system overview diagrams

### Windows Execution: Native Docker

Windows jobs run directly in Docker containers without an intermediate layer:

```mermaid
graph TB
    DispatchJob["Job from<br/>workflow-dispatch-*"]
    
    RunJobWindows["workflow-run-job-windows"]
    
    DispatchJob --> RunJobWindows
    
    RunJobWindows --> WindowsContainer["rapidsai/devcontainers:*-cuda*-cl*<br/>Native Windows container"]
    
    WindowsContainer --> PathTransform["Transform paths<br/>for Windows"]
    WindowsContainer --> ExecuteCommand["Execute PowerShell script<br/>ci/windows/*.ps1"]
    
    ExecuteCommand --> Artifacts["Upload artifacts:<br/>success, sccache_stats"]
```

**Sources:** Based on system overview diagrams

### DevContainer Selection

The `generate_dispatch_job_image()` function [.github/actions/workflow-build/build-workflow.py:404-412]() constructs image references:

**Linux format**: `rapidsai/devcontainers:{devcontainer_version}-cpp-{host_compiler}-cuda{ctk}`

**Windows format**: `rapidsai/devcontainers:{devcontainer_version}-cuda{ctk}-{host_compiler}`

Where:
- `devcontainer_version`: Global version identifier from `matrix.yaml`
- `host_compiler`: Compiler container tag + version (e.g., `gcc12`, `cl14.38`)
- `ctk`: CUDA Toolkit version (e.g., `11.1`, `12.0`)

**Sources:** [.github/actions/workflow-build/build-workflow.py:404-412]()

## Data Flow Summary

The complete data flow through the system:

```mermaid
graph TB
    Input["Inputs:<br/>matrix.yaml<br/>workflows flag<br/>dirty_projects"]
    
    Parse["parse_workflow_matrix_jobs()<br/>Line 922-959"]
    Process["preprocess_matrix_jobs()<br/>Line 902-919"]
    Exclude["remove_excluded_jobs()<br/>Line 796-808"]
    ToDispatch["matrix_job_to_dispatch_group()<br/>Line 542-544"]
    Finalize["finalize_workflow_dispatch_groups()<br/>Line 583-721"]
    
    Input --> Parse
    Parse --> Process
    Process --> Exclude
    Exclude --> ToDispatch
    ToDispatch --> Finalize
    
    Finalize --> Outputs["Outputs:<br/>workflow.json<br/>job_ids.json<br/>runner_summary.json"]
    
    Outputs --> PrepareDispatch["prepare-workflow-dispatch.py"]
    PrepareDispatch --> DispatchJSON["dispatch.json"]
    
    DispatchJSON --> DispatchWorkflows["Dispatch Workflows<br/>Matrix expansion"]
    DispatchWorkflows --> ExecutionWorkflows["Execution Workflows<br/>Container + command"]
    ExecutionWorkflows --> Results["Results:<br/>Artifacts, timing,<br/>sccache stats"]
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:922-1048](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:78-95](), [.github/actions/workflow-build/action.yml:74-124]()

### Key Artifacts

| Artifact | Producer | Consumer | Purpose |
|----------|----------|----------|---------|
| `matrix.yaml` | Human author | `build-workflow.py` | Job matrix definition |
| `workflow.json` | `build-workflow.py` | `prepare-workflow-dispatch.py`, results processing | Complete job specifications with origin metadata |
| `job_ids.json` | `build-workflow.py` | Results processing | Maps short IDs to full job names |
| `runner_summary.json` | `build-workflow.py` | GitHub Step Summary | Runner allocation statistics |
| `dispatch.json` | `prepare-workflow-dispatch.py` | Dispatch workflows | Categorized jobs for matrix expansion |
| Job artifacts | Execution workflows | `workflow-results` action | Success markers, sccache stats, benchmark data |

**Sources:** [.github/actions/workflow-build/build-workflow.py:979-1023](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:74-75](), [.github/actions/workflow-build/action.yml:119-124]()

## Component Interaction Patterns

### Composite Action Orchestration

The `workflow-build` composite action [.github/actions/workflow-build/action.yml:1-140]() orchestrates the generation phase:

```mermaid
sequenceDiagram
    participant Caller as "Calling Workflow"
    participant Action as "workflow-build Action"
    participant Inspect as "inspect-changes step"
    participant Build as "build-workflow.py"
    participant Prepare as "prepare-workflow-dispatch.py"
    participant Slack as "Slack API"
    
    Caller->>Action: Invoke with inputs
    Action->>Slack: Send start notification
    
    alt inspect_changes_script provided
        Action->>Inspect: Run change detection
        Inspect-->>Action: dirty_projects output
    end
    
    Action->>Build: Parse matrix + filter
    Build-->>Action: workflow.json + metadata
    
    Action->>Prepare: Split by OS/pattern
    Prepare-->>Action: dispatch.json
    
    Action->>Action: Set WORKFLOW output
    Action->>Action: Upload artifacts
    
    alt On failure
        Action->>Slack: Send error notification
    end
    
    Action-->>Caller: Return WORKFLOW output
```

**Sources:** [.github/actions/workflow-build/action.yml:44-140]()

### Error Handling and Notifications

The system implements resilient error handling:

- **Validation errors**: `build-workflow.py` raises exceptions with file location context using `error_message_with_matrix_job()` [line 109-110]()
- **GitHub annotations**: Errors/warnings/notices printed to stderr with `::error file=ci/matrix.yaml::` format
- **Slack notifications**: Two-channel strategy:
  - `slack_log`: Verbose notifications for all runs [line 47-59]()
  - `slack_alert`: Critical failures only [line 126-139]()
- **Artifact preservation**: `continue-on-error` used in results processing to ensure partial data is reported

**Sources:** [.github/actions/workflow-build/action.yml:47-139](), [.github/actions/workflow-build/build-workflow.py:109-110]()

---

# Page: Key Concepts

# Key Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)
- [.github/workflows/workflow-dispatch-two-stage-linux.yml](.github/workflows/workflow-dispatch-two-stage-linux.yml)

</details>



This page defines the core terminology and data structures used throughout the cccl-gha workflow orchestration system. Understanding these concepts is essential for navigating the codebase and comprehending how jobs flow from configuration to execution.

For details on how these concepts are generated from configuration files, see [Workflow Generation](#3). For information on how they execute in specific environments, see [Job Execution](#5).

---

## Matrix Jobs

A **matrix job** is a single configuration entry in `matrix.yaml` that defines a build or test job. Matrix jobs specify combinations of tags (parameters) such as project, compiler, CUDA version, and GPU architecture. The workflow generation pipeline transforms matrix jobs into executable dispatch jobs.

**Structure in YAML:**
```yaml
- project: libcudacxx
  ctk: 11.1
  cudacxx: nvcc
  cxx: gcc10
  std: [17, 20]
  sm: 75-real
  jobs: [build, test]
```

**Structure after parsing (JSON):**
```json
{
  "project": "libcudacxx",
  "ctk": "11.1",
  "cudacxx": "nvcc",
  "cxx": "gcc10",
  "std": 17,
  "sm": "75-real",
  "cpu": "amd64",
  "gpu": "t4",
  "jobs": ["build", "test"],
  "origin": {
    "filename": "ci/matrix.yaml",
    "workflow_name": "pull_request",
    "workflow_location": "ci/matrix.yaml:42 (job 3)"
  }
}
```

Matrix jobs undergo several transformations:
1. **Validation** - verify all required tags are present
2. **Default-setting** - fill in optional tags with defaults
3. **Explosion** - expand list values into individual jobs
4. **Canonicalization** - resolve aliases (e.g., `gcc10` → `gcc10`)
5. **Derived tags** - compute values (e.g., `sm` from `gpu`, `std: all`)
6. **Exclusion** - filter out invalid combinations

```mermaid
graph LR
    A["matrix.yaml entry"]
    B["parse_workflow_matrix_jobs()"]
    C["validate_tags()"]
    D["set_default_tags()"]
    E["explode_tags()"]
    F["canonicalize_tags()"]
    G["set_derived_tags()"]
    H["remove_excluded_jobs()"]
    I["matrix_job JSON"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:4-24](), [.github/actions/workflow-build/build-workflow.py:811-843](), [.github/actions/workflow-build/build-workflow.py:845-861](), [.github/actions/workflow-build/build-workflow.py:876-900](), [.github/actions/workflow-build/build-workflow.py:902-919]()

---

## Tags

**Tags** are named parameters that describe job configurations. Each tag has metadata defining whether it is required, its default value, and validation rules.

### Tag Categories

| Category | Tags | Description |
|----------|------|-------------|
| **Required** | `project`, `cudacxx`, `cxx`, `ctk` | Must be specified for every job |
| **Optional** | `std`, `sm`, `gpu`, `cpu`, `cmake_options` | Have default values or can be derived |
| **Computed** | `origin` | Added automatically by the system |
| **Special** | `jobs` | Left unexploded for scheduling optimization |

### Tag Processing Functions

```mermaid
graph TB
    subgraph "Tag Metadata"
        A["get_tag_info(tag)"]
        A1["tags[tag]['required']"]
        A2["tags[tag]['default']"]
    end
    
    subgraph "Tag Lookup"
        B["get_project(project)"]
        C["get_ctk(ctk_string)"]
        D["get_host_compiler(cxx_string)"]
        E["get_device_compiler(matrix_job)"]
        F["get_gpu(gpu_string)"]
        G["get_job_type_info(job)"]
    end
    
    subgraph "Tag Canonicalization"
        H["canonicalize_ctk_version(ctk_string)"]
        I["canonicalize_host_compiler_name(cxx_string)"]
    end
    
    subgraph "Derived Values"
        J["lookup_supported_stds(matrix_job)"]
        K["is_windows(matrix_job)"]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    
    H --> C
    I --> D
    
    D --> J
    E --> J
    C --> J
    B --> J
    
    D --> K
```

**Key Tag Functions:**
- `get_tag_info(tag)` - retrieves tag metadata from `matrix_yaml['tags']`
- `canonicalize_host_compiler_name(cxx_string)` - standardizes compiler names (e.g., `gcc` → `gcc12`, `gcc-10` → `gcc10`)
- `set_derived_tags(matrix_job)` - computes `sm` from `gpu`, expands `std: all`, applies project job maps

**Sources:** [.github/actions/workflow-build/build-workflow.py:284-303](), [.github/actions/workflow-build/build-workflow.py:132-173](), [.github/actions/workflow-build/build-workflow.py:852-875]()

---

## Dispatch Groups

A **dispatch group** is a named collection of jobs that share common configuration (project, CTK version, compilers). Dispatch groups organize jobs for parallel execution and are displayed as collapsible sections in GitHub Actions UI.

**Structure:**
```json
{
  "<group name>": {
    "standalone": [
      { "id": "ABC", "name": "...", "runner": "...", "image": "...", "command": "..." }
    ],
    "two_stage": [
      {
        "id": "DEF",
        "producers": [ { "id": "GHI", "name": "...", ... } ],
        "consumers": [ { "id": "JKL", "name": "...", ... } ]
      }
    ]
  }
}
```

**Group Name Format:**
```
{project_name} CTK{version} {compiler_info}
```

Examples:
- `libcudacxx CTK11.1 nvcc GCC`
- `Thrust CTK12.0 Clang`

```mermaid
graph TB
    A["matrix_job"]
    B["generate_dispatch_group_name()"]
    C["generate_dispatch_group_jobs()"]
    D["matrix_job_to_dispatch_group()"]
    E["dispatch_group JSON"]
    
    subgraph "Group Name Components"
        B1["project['name']"]
        B2["ctk version"]
        B3["device_compiler['name']"]
        B4["host_compiler['name']"]
    end
    
    subgraph "Job Classification"
        C1["Identify dependencies"]
        C2["Split standalone vs two_stage"]
        C3["Group producers with consumers"]
    end
    
    A --> B
    A --> C
    B --> D
    C --> D
    D --> E
    
    B --> B1
    B --> B2
    B --> B3
    B --> B4
    
    C --> C1
    C1 --> C2
    C2 --> C3
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:28-35](), [.github/actions/workflow-build/build-workflow.py:345-359](), [.github/actions/workflow-build/build-workflow.py:507-544](), [.github/actions/workflow-build/build-workflow.py:547-554]()

---

## Job Types: Standalone vs Two-Stage

The system supports two execution patterns based on job dependencies.

### Standalone Jobs

**Standalone jobs** execute independently without dependencies. Each job runs a complete workflow (build and test) in a single execution.

```mermaid
graph LR
    A["Dispatch Group"]
    B["Job 1"]
    C["Job 2"]
    D["Job 3"]
    
    A -->|parallel| B
    A -->|parallel| C
    A -->|parallel| D
```

**Characteristics:**
- No inter-job dependencies
- Execute in parallel
- Self-contained execution
- Typically used for simple test jobs

**Sources:** [.github/actions/workflow-build/build-workflow.py:536-537]()

### Two-Stage Jobs

**Two-stage jobs** implement a producer-consumer pattern where one job builds artifacts and multiple jobs consume them. This optimizes scenarios where compilation is expensive but testing across multiple configurations is needed.

```mermaid
graph TB
    A["Dispatch Group"]
    B["Producer Job"]
    C["Consumer Job 1"]
    D["Consumer Job 2"]
    E["Consumer Job N"]
    
    A --> B
    B -->|needs: producer| C
    B -->|needs: producer| D
    B -->|needs: producer| E
    
    subgraph "Parallel Execution"
        C
        D
        E
    end
```

**Two-Stage Structure:**
```json
{
  "id": "uniqueId",
  "producers": [
    {
      "id": "prodId",
      "name": "[C++17 GCC12] Build(amd64): sm{75}",
      "command": "\"./ci/build_libcudacxx.sh\" -std \"17\" -arch \"75-real\""
    }
  ],
  "consumers": [
    {
      "id": "cons1",
      "name": "[C++17 GCC12] Test(amd64, T4)",
      "command": "\"./ci/test_libcudacxx.sh\" -std \"17\""
    },
    {
      "id": "cons2",
      "name": "[C++20 GCC12] Test(amd64, V100)",
      "command": "\"./ci/test_libcudacxx.sh\" -std \"20\""
    }
  ]
}
```

**Dependency Declaration:**
```yaml
# In matrix.yaml jobs section:
jobs:
  test:
    needs: build  # test jobs depend on build jobs
```

**Workflow Implementation:**
The two-stage pattern is enforced by `workflow-dispatch-two-stage-linux.yml` and `workflow-dispatch-two-stage-windows.yml`:
- Producer runs first as a single job
- Consumers wait for producer completion (`needs: producer`)
- Consumers execute in parallel using matrix strategy (`fail-fast: false`)
- Artifacts are exchanged via GitHub Actions artifact storage

**Sources:** [.github/actions/workflow-build/build-workflow.py:37-43](), [.github/actions/workflow-build/build-workflow.py:493-504](), [.github/actions/workflow-build/build-workflow.py:517-534](), [.github/workflows/workflow-dispatch-two-stage-linux.yml:19-76]()

---

## Job JSON

A **job JSON** object represents a single executable job with all information needed to run it on a GitHub Actions runner.

**Complete Structure:**
```json
{
  "id": "ABC",
  "name": "[C++17 GCC12] Test(amd64, T4): sm{75}",
  "runner": "linux-amd64-gpu-t4-latest-1",
  "image": "rapidsai/devcontainers:24.10.00-cpp-gcc12-cuda11.1",
  "command": "\"./ci/test_libcudacxx.sh\" -std \"17\" -arch \"75-real\"",
  "cuda": "11.1",
  "host": "gcc12",
  "origin": {
    "filename": "ci/matrix.yaml",
    "workflow_name": "pull_request",
    "workflow_location": "ci/matrix.yaml:42 (job 3)",
    "original_matrix_job": "{project: libcudacxx, ...}",
    "matrix_job": {
      "project": "libcudacxx",
      "jobs": "Test",
      "cxx": "GCC12",
      "cxx_family": "GCC",
      "cudacxx": "nvcc11.1",
      "cudacxx_family": "nvcc",
      "std": 17,
      "sm": "75-real"
    }
  }
}
```

### Job JSON Fields

| Field | Purpose | Generated By |
|-------|---------|--------------|
| `id` | Compact unique identifier (1-3 chars) | GUID generator |
| `name` | Human-readable job description | `generate_dispatch_job_name()` |
| `runner` | GitHub Actions runner label | `generate_dispatch_job_runner()` |
| `image` | Docker container image | `generate_dispatch_job_image()` |
| `command` | Shell command to execute | `generate_dispatch_job_command()` |
| `cuda` | CUDA toolkit version for devcontainer | `generate_dispatch_job_ctk_version()` |
| `host` | Host compiler for devcontainer | `generate_dispatch_job_host_compiler()` |
| `origin` | Traceability metadata | `generate_dispatch_job_origin()` |

### GUID Generation

Unique job IDs are generated using a compact base64 encoding scheme that produces 1-3 character identifiers:

```mermaid
graph LR
    A["16-bit counter"]
    B["struct.pack('>H', i)"]
    C["base64.b64encode()"]
    D["Strip 'A' prefix and '=' suffix"]
    E["GUID: 'B', 'AB', 'Qx', etc."]
    
    A --> B
    B --> C
    C --> D
    D --> E
```

The generator produces up to 65,535 unique IDs before exhaustion.

**Sources:** [.github/actions/workflow-build/build-workflow.py:45-53](), [.github/actions/workflow-build/build-workflow.py:78-96](), [.github/actions/workflow-build/build-workflow.py:481-490](), [.github/actions/workflow-build/build-workflow.py:708-720]()

---

## Devcontainers

**Devcontainers** are Docker images containing specific combinations of CUDA toolkit and host compiler. Each job executes inside a devcontainer to ensure reproducible build environments.

### Devcontainer Image Naming

```
rapidsai/devcontainers:{version}-cpp-{host}-cuda{ctk}
rapidsai/devcontainers:{version}-cuda{ctk}-{host}  # Windows
```

**Examples:**
- `rapidsai/devcontainers:24.10.00-cpp-gcc12-cuda11.1` (Linux)
- `rapidsai/devcontainers:24.10.00-cuda12.0-cl14.39` (Windows)

### Devcontainer Components

```mermaid
graph TB
    subgraph "Image Selection Logic"
        A["matrix_job"]
        B["generate_dispatch_job_image()"]
        C["is_windows()?"]
        D["Linux format:<br/>-cpp-{host}-cuda{ctk}"]
        E["Windows format:<br/>-cuda{ctk}-{host}"]
        F["devcontainer image name"]
    end
    
    subgraph "Launch Parameters"
        G["cuda version"]
        H["host compiler"]
        I["launch.sh --cuda X --host Y"]
    end
    
    A --> B
    B --> C
    C -->|false| D
    C -->|true| E
    D --> F
    E --> F
    
    A --> G
    A --> H
    G --> I
    H --> I
```

**Key Configuration Values:**
- `devcontainer_version` - global version string from `matrix_yaml['devcontainer_version']`
- `host` - compiler tag (e.g., `gcc12`, `cl14.39`)
- `cuda` - CUDA toolkit version (e.g., `11.1`, `12.0`)

**Verification:**
The `verify-devcontainers` workflow ensures devcontainer configurations remain synchronized with generation scripts by running `make_devcontainers.sh --clean` and checking for modifications.

**Sources:** [.github/actions/workflow-build/build-workflow.py:393-413]()

---

## Workflows

A **workflow** is a named collection of matrix jobs defined in `matrix.yaml`. Workflows represent different CI/CD scenarios (pull requests, nightly builds, weekly tests).

**Common Workflows:**
- `pull_request` - jobs that run on every PR
- `nightly` - comprehensive testing run daily
- `weekly` - extended testing including expensive configurations
- `exclude` - special workflow defining job combinations to filter out
- `override` - emergency override that supersedes all other workflows

```mermaid
graph TB
    A["matrix.yaml"]
    
    subgraph "Workflow Definitions"
        B["workflows.pull_request"]
        C["workflows.nightly"]
        D["workflows.weekly"]
        E["workflows.exclude"]
        F["workflows.override"]
    end
    
    subgraph "Processing"
        G["parse_workflow_matrix_jobs(args, 'pull_request')"]
        H["parse_workflow_matrix_jobs(args, 'exclude')"]
        I["apply_matrix_job_exclusion()"]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    
    B --> G
    E --> H
    G --> I
    H --> I
```

### Workflow Selection

Workflows are selected via command-line arguments:
```bash
build-workflow.py matrix.yaml --workflows pull_request nightly
```

With override support:
```bash
build-workflow.py matrix.yaml --workflows pull_request --allow-override
```

If `override` workflow exists and is non-empty, it supersedes the specified workflows.

**Sources:** [.github/actions/workflow-build/build-workflow.py:922-959](), [.github/actions/workflow-build/build-workflow.py:1031-1048]()

---

## Exclusions

**Exclusions** define invalid or unsupported job combinations that should be filtered out. They are specified in the special `exclude` workflow in `matrix.yaml`.

### Exclusion Logic

An exclusion is a partial matrix job. A job is excluded if it matches **all** specified tags in any exclusion entry.

**Example Exclusion:**
```yaml
exclude:
  - cudacxx: clang
    sm: 90a  # Clang doesn't support sm_90a
  - project: thrust
    cxx: msvc
    std: 20  # Thrust + MSVC + C++20 is broken
```

### Partial Matching

Exclusions support partial list matching. If an exclusion matches some but not all values in a tag's list, only the matched values are removed:

```yaml
# Matrix job:
std: [17, 20]
cxx: gcc10

# Exclusion:
std: [20]
cxx: gcc10

# Result: std becomes [17] (20 is removed, 17 remains)
```

```mermaid
graph TB
    A["matrix_job"]
    B["get_excluded_matrix_jobs()"]
    C["For each exclusion"]
    D["apply_matrix_job_exclusion()"]
    E["All tags match?"]
    F["Partial match?"]
    G["Return None<br/>(exclude entirely)"]
    H["Remove matched values<br/>from tag lists"]
    I["No match?"]
    J["Return unchanged"]
    
    A --> C
    B --> C
    C --> D
    D --> E
    E -->|yes, complete| G
    E -->|yes, partial| F
    E -->|no| I
    F --> H
    I --> J
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:749-808]()

---

## Job Artifacts

**Job artifacts** are files produced during job execution and uploaded to GitHub Actions artifact storage for later retrieval or inter-job exchange.

### Artifact Types

| Artifact | Purpose | Producer | Consumer |
|----------|---------|----------|----------|
| `success` marker | Indicates job completion | All jobs | `workflow-results` |
| `sccache_stats.json` | Compilation cache statistics | Jobs using sccache | `workflow-results` |
| `cccl_meta_bench.csv` | Benchmark results | Benchmark jobs | `workflow-results` |
| Build artifacts | Compiled binaries, libraries | Producer jobs | Consumer jobs |

### Artifact Paths

Artifacts are organized by job ID:
```
jobs/
  {job_id}/
    success
    sccache_stats.json
    cccl_meta_bench.csv
```

### Two-Stage Artifact Flow

```mermaid
sequenceDiagram
    participant P as "Producer Job"
    participant S as "Artifact Storage"
    participant C1 as "Consumer Job 1"
    participant C2 as "Consumer Job N"
    
    P->>P: Execute build command
    P->>P: Create artifacts
    P->>S: Upload artifacts<br/>jobs/{id}/success<br/>jobs/{id}/build/*
    P->>S: Upload sccache_stats
    
    S->>C1: Download artifacts
    S->>C2: Download artifacts
    
    C1->>C1: Run tests with<br/>downloaded artifacts
    C2->>C2: Run tests with<br/>downloaded artifacts
    
    C1->>S: Upload test results
    C2->>S: Upload test results
```

**Sources:** Inferred from system architecture diagrams and two-stage workflow structure

---

## Origin Metadata

**Origin metadata** provides traceability from executed jobs back to their source configuration. This information is used for error reporting and execution summaries.

### Origin Structure

```json
{
  "origin": {
    "filename": "ci/matrix.yaml",
    "workflow_name": "pull_request",
    "workflow_location": "ci/matrix.yaml:42 (job 3)",
    "original_matrix_job": "{project: libcudacxx, ctk: 11.1, ...}",
    "matrix_job": {
      "project": "libcudacxx",
      "jobs": "Test",
      "cxx": "GCC12",
      "cxx_family": "GCC",
      "cudacxx": "nvcc11.1",
      "cudacxx_family": "nvcc",
      "std": 17,
      "sm": "75-real",
      "cpu": "amd64",
      "gpu": "t4",
      "ctk": "11.1"
    }
  }
}
```

### Origin Transformations

Origin metadata is transformed to be summary-friendly:
- `jobs` value becomes human-readable (e.g., `"build"` → `"Build"`)
- `cxx` becomes formatted (e.g., `"gcc12"` → `"GCC12"`)
- `cxx_family` is added for grouping (e.g., `"GCC"`)
- `cudacxx` becomes formatted (e.g., `"nvcc"` → `"nvcc11.1"`)
- `cudacxx_family` is added for grouping (e.g., `"nvcc"`)

These transformations enable hierarchical aggregation in execution summaries by project, job type, compiler family, etc.

**Sources:** [.github/actions/workflow-build/build-workflow.py:448-478]()

---

## Dispatch JSON Structure

The **dispatch JSON** is the final output of the workflow generation pipeline, organized for optimal GitHub Actions execution.

```mermaid
graph TB
    A["workflow.json"]
    B["prepare-workflow-dispatch.py"]
    
    subgraph "dispatch.json"
        C["linux_standalone"]
        D["linux_two_stage"]
        E["windows_standalone"]
        F["windows_two_stage"]
    end
    
    subgraph "Structure"
        G["jobs array"]
        H["pc-array<br/>(producer-consumer)"]
    end
    
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    
    C --> G
    E --> G
    D --> H
    F --> H
```

### Split Categories

The dispatch JSON splits jobs into four categories:

1. **`linux_standalone`** - Linux jobs without dependencies
2. **`linux_two_stage`** - Linux producer-consumer chains
3. **`windows_standalone`** - Windows jobs without dependencies
4. **`windows_two_stage`** - Windows producer-consumer chains

This organization allows the dispatch layer to:
- Target appropriate runner OS (Linux vs Windows)
- Use correct execution pattern (standalone vs two-stage)
- Avoid showing hundreds of skipped jobs in GitHub UI
- Parallelize execution efficiently

**Sources:** System architecture diagrams, inferred from dispatch workflow structure

---

# Page: Legal and Policies

# Legal and Policies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [LICENSE](LICENSE)
- [SECURITY.md](SECURITY.md)

</details>



## Purpose and Scope

This document describes the legal framework, community standards, and security policies that govern the cccl-gha repository. It covers licensing terms, code of conduct requirements, and security vulnerability reporting procedures. All contributors and users must comply with these policies.

For information about contributing code changes and development practices, see [Development and Contributing](#9). For system requirements and setup, see [System Requirements](#9.1).

---

## License Structure

The cccl-gha repository inherits licensing from its parent CCCL project, which employs a multi-license structure to accommodate different components with distinct heritage and requirements.

### License Hierarchy

```mermaid
graph TB
    subgraph "Primary Licenses"
        Apache["Apache License v2.0<br/>(Primary License)"]
        ApacheLLVM["Apache v2.0 with<br/>LLVM Exceptions"]
    end
    
    subgraph "Component-Specific Licenses"
        BSD3["BSD 3-Clause<br/>(CUB)"]
        UIUC["University of Illinois/NCSA<br/>Open Source License"]
        MIT["MIT License"]
        Boost["Boost Software License v1.0"]
        FreeBSD["FreeBSD License"]
        NVIDIA["NVIDIA SOFTWARE LICENSE"]
    end
    
    subgraph "Components"
        Thrust["Thrust Library"]
        Libcudacxx["libcu++ Library"]
        CUB["CUB Library"]
        Utilities["C++ Utilities<br/>(Iterator, Tuple, etc.)"]
        Complex["thrust::complex"]
        NVIDAProprietary["Some libcudacxx components"]
    end
    
    Apache --> Thrust
    ApacheLLVM --> Libcudacxx
    BSD3 --> CUB
    UIUC --> Libcudacxx
    MIT --> Libcudacxx
    Boost --> Utilities
    FreeBSD --> Complex
    NVIDIA --> NVIDAProprietary
    
    Utilities --> Thrust
    Complex --> Thrust
```

**License Component Mapping**

Sources: [LICENSE:1-467]()

### Apache License v2.0

The primary license governing Thrust and most of the codebase is Apache License v2.0 (January 2004). This license grants users the following permissions:

| Permission | Scope | Requirements |
|------------|-------|--------------|
| **Reproduce** | Unlimited copies in Source or Object form | Must include copy of License |
| **Prepare Derivative Works** | Create modified versions | Must mark modified files prominently |
| **Publicly Display/Perform** | Public use of the software | Retain copyright/patent/trademark notices |
| **Distribute** | Redistribute to third parties | Include NOTICE file if present |
| **Sublicense** | Grant sublicenses | Terms must be consistent with Apache License |

**Key Provisions:**

- **Copyright License**: Perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable [LICENSE:70-75]()
- **Patent License**: Includes patent rights for contributions [LICENSE:77-91]()
- **Patent Litigation Termination**: Patent licenses terminate if licensee initiates patent litigation [LICENSE:86-91]()
- **No Warranty**: Software provided "AS IS" without warranties [LICENSE:147-155]()
- **Limitation of Liability**: No liability for damages except as required by law [LICENSE:157-167]()

Sources: [LICENSE:1-205]()

### Apache v2.0 with LLVM Exceptions

The libcu++ library uses Apache License v2.0 with LLVM Exceptions, which provides additional flexibility:

**LLVM Exception 1 - Object Code Embedding:**
Portions of the software embedded into object code during compilation may be redistributed in object form without complying with Sections 4(a), 4(b), and 4(d) of the standard Apache License. This exception enables easier integration into proprietary software. [LICENSE:211-216]()

**LLVM Exception 2 - GPLv2 Compatibility:**
If combined with GPLv2-licensed software and a court determines conflicts exist, specific sections of the Apache License may be waived for the Combined Software only. [LICENSE:218-225]()

Sources: [LICENSE:209-225]()

### BSD 3-Clause License (CUB)

CUB's source code is released under the BSD 3-Clause license, which is more permissive than Apache but requires attribution:

| Requirement | Description |
|-------------|-------------|
| **Copyright Notice** | Must retain copyright notice in source redistributions |
| **Binary Notice** | Must reproduce notice in documentation for binary distributions |
| **Endorsement Restriction** | Cannot use NVIDIA name without permission |

The license explicitly disclaims warranties and limits liability. [LICENSE:441-466]()

Sources: [LICENSE:441-466]()

### Component-Specific Licensing

```mermaid
graph LR
    subgraph "Thrust Components"
        ThrustCore["Core Thrust<br/>Apache v2.0"]
        ThrustIterator["Boost-derived utilities<br/>Boost License"]
        ThrustComplex["Complex numbers<br/>FreeBSD License"]
    end
    
    subgraph "libcu++ Components"
        LibcuCore["Core libcu++<br/>Apache v2.0 + LLVM"]
        LibcuUnderlying["libc++ heritage<br/>Dual: UIUC + MIT"]
        LibcuNVIDIA["NVIDIA-specific<br/>NVIDIA SOFTWARE LICENSE"]
    end
    
    subgraph "License Requirements"
        Permissive["Permissive<br/>Minimal restrictions"]
        CopyleftCompatible["Copyleft Compatible<br/>Can mix with GPL"]
        Proprietary["Proprietary<br/>NVIDIA-specific terms"]
    end
    
    ThrustCore --> Permissive
    ThrustIterator --> Permissive
    ThrustComplex --> Permissive
    LibcuCore --> CopyleftCompatible
    LibcuUnderlying --> Permissive
    LibcuNVIDIA --> Proprietary
```

**Boost Software License v1.0:**
Thrust's iterator, tuple, system, and random number utilities are based on Boost libraries. The Boost license requires that copyright notices and disclaimers be included in all copies but permits derivative works in machine-executable object code form without these restrictions. [LICENSE:379-405]()

**FreeBSD License:**
The `thrust::complex` implementation is derived from FreeBSD with a permissive 2-clause BSD license requiring only copyright notice retention and disclaimer reproduction. [LICENSE:409-438]()

**NVIDIA SOFTWARE LICENSE:**
Some libcudacxx components are covered by NVIDIA's proprietary license with specific restrictions:

- Software licensed only for systems with NVIDIA GPUs [LICENSE:338]()
- Cannot reverse engineer, decompile, or disassemble [LICENSE:339]()
- Cannot modify or create derivative works [LICENSE:340]()
- Cannot use in safety-critical applications without agreement [LICENSE:343]()
- Subject to U.S. export control laws [LICENSE:363-364]()

Sources: [LICENSE:318-370](), [LICENSE:379-405](), [LICENSE:409-438]()

### License Identification System

The LICENSE file documents how to identify which license applies to specific code:

```mermaid
graph TB
    SourceFile["Source File"]
    
    Check1{"Separate directory<br/>with LICENSE.txt?"}
    Check2{"License terms<br/>at top of file?"}
    Check3{"Copyright notice<br/>references component?"}
    
    DirLicense["Use directory's<br/>LICENSE.txt"]
    FileLicense["Use file header<br/>license terms"]
    ComponentLicense["Use component-specific<br/>license from main LICENSE"]
    DefaultLicense["Use Apache v2.0<br/>(default)"]
    
    SourceFile --> Check1
    Check1 -->|Yes| DirLicense
    Check1 -->|No| Check2
    Check2 -->|Yes| FileLicense
    Check2 -->|No| Check3
    Check3 -->|Yes| ComponentLicense
    Check3 -->|No| DefaultLicense
```

The LICENSE file establishes a two-mechanism identification system:
1. Separate directory tree with its own LICENSE file [LICENSE:233-235]()
2. Specific license terms at the top of individual files [LICENSE:236-237]()

Sources: [LICENSE:228-237]()

---

## Code of Conduct

The repository follows the Contributor Covenant Code of Conduct version 1.4 to ensure a harassment-free environment for all participants.

### Governance Structure

```mermaid
graph TB
    subgraph "Community Participants"
        Contributors["Contributors"]
        Maintainers["Maintainers"]
        Community["Community Members"]
    end
    
    subgraph "Standards"
        Pledge["Harassment-free<br/>participation pledge"]
        Positive["Positive Behavior<br/>Standards"]
        Unacceptable["Unacceptable Behavior<br/>Examples"]
    end
    
    subgraph "Enforcement"
        Report["Report to<br/>GitHub_Conduct@nvidia.com"]
        Review["Review and<br/>Investigation"]
        Response["Appropriate<br/>Response"]
        Confidentiality["Maintain reporter<br/>confidentiality"]
    end
    
    subgraph "Scope"
        ProjectSpaces["Project Spaces<br/>(repositories, issues)"]
        PublicSpaces["Public Spaces<br/>(representing project)"]
    end
    
    Contributors --> Pledge
    Maintainers --> Pledge
    Community --> Pledge
    
    Pledge --> Positive
    Pledge --> Unacceptable
    
    Unacceptable --> Report
    Report --> Review
    Review --> Response
    Review --> Confidentiality
    
    Positive --> ProjectSpaces
    Positive --> PublicSpaces
```

### Standards of Behavior

**Positive Environment Contributions:**

| Behavior | Description |
|----------|-------------|
| **Inclusive Language** | Using welcoming and inclusive terminology |
| **Respectful Discourse** | Being respectful of differing viewpoints and experiences |
| **Constructive Criticism** | Gracefully accepting constructive feedback |
| **Community Focus** | Focusing on what is best for the community |
| **Empathy** | Showing empathy towards other community members |

[CODE_OF_CONDUCT.md:22-29]()

**Unacceptable Behaviors:**

| Behavior | Impact |
|----------|--------|
| **Sexualized Language/Imagery** | Creates hostile environment |
| **Trolling/Derogatory Comments** | Disrupts constructive dialogue |
| **Public/Private Harassment** | Violates personal safety |
| **Publishing Private Information** | Violates privacy (doxxing) |
| **Professionally Inappropriate Conduct** | Damages professional atmosphere |

[CODE_OF_CONDUCT.md:31-40]()

Sources: [CODE_OF_CONDUCT.md:20-40]()

### Maintainer Responsibilities

Project maintainers have explicit responsibilities and authority:

**Responsibilities:**
- Clarify standards of acceptable behavior [CODE_OF_CONDUCT.md:44-45]()
- Take appropriate and fair corrective action [CODE_OF_CONDUCT.md:45-46]()

**Authority:**
- Remove, edit, or reject contributions not aligned with Code of Conduct [CODE_OF_CONDUCT.md:48-50]()
- Ban contributors temporarily or permanently for inappropriate behavior [CODE_OF_CONDUCT.md:50-52]()

**Scope of Application:**
- Within project spaces (repositories, issues, documentation) [CODE_OF_CONDUCT.md:56-57]()
- In public spaces when representing the project [CODE_OF_CONDUCT.md:56-57]()
- Using official project email addresses [CODE_OF_CONDUCT.md:58-59]()
- Posting via official social media [CODE_OF_CONDUCT.md:59]()
- Acting as appointed representative at events [CODE_OF_CONDUCT.md:59-60]()

Sources: [CODE_OF_CONDUCT.md:42-62]()

### Enforcement Process

```mermaid
sequenceDiagram
    participant Reporter as "Reporter"
    participant Contact as "GitHub_Conduct@nvidia.com"
    participant ProjectTeam as "Project Team"
    participant Subject as "Subject of Complaint"
    
    Reporter->>Contact: Report incident
    Note over Reporter,Contact: All details provided
    
    Contact->>ProjectTeam: Review complaint
    Note over ProjectTeam: Investigation conducted
    
    ProjectTeam->>ProjectTeam: Determine response
    Note over ProjectTeam: Context-appropriate action
    
    ProjectTeam->>Reporter: Provide response
    Note over ProjectTeam,Reporter: Maintain confidentiality
    
    alt Violation Confirmed
        ProjectTeam->>Subject: Take corrective action
        Note over Subject: May include temporary/permanent ban
    end
    
    Note over Reporter,Subject: Project team maintains<br/>confidentiality throughout
```

**Enforcement Contact:** `GitHub_Conduct@nvidia.com` [CODE_OF_CONDUCT.md:66]()

**Process Guarantees:**
- All complaints reviewed and investigated [CODE_OF_CONDUCT.md:66-67]()
- Response deemed necessary and appropriate to circumstances [CODE_OF_CONDUCT.md:67-68]()
- Confidentiality maintained regarding reporter [CODE_OF_CONDUCT.md:68-69]()

**Maintainer Accountability:**
Maintainers who do not follow or enforce the Code of Conduct in good faith may face temporary or permanent repercussions as determined by project leadership. [CODE_OF_CONDUCT.md:72-74]()

Sources: [CODE_OF_CONDUCT.md:64-74]()

### Attribution

The Code of Conduct is adapted from the Contributor Covenant, version 1.4, available at https://www.contributor-covenant.org/version/1/4/code-of-conduct.html [CODE_OF_CONDUCT.md:78-79]()

Sources: [CODE_OF_CONDUCT.md:76-84]()

---

## Security Policies

NVIDIA is dedicated to the security and trust of software products and services, including all source code repositories. The repository follows specific procedures for reporting security vulnerabilities.

### Security Reporting Channels

**Critical Policy: Do not report security vulnerabilities through GitHub issues, pull requests, or discussions.** [SECURITY.md:5]()

```mermaid
graph TB
    subgraph "Vulnerability Discovery"
        Researcher["Security Researcher"]
        Developer["Developer"]
        User["User"]
    end
    
    subgraph "Reporting Channels"
        WebForm["Web Submission Form<br/>nvidia.com/submit-security-vulnerability"]
        Email["Email: psirt@nvidia.com<br/>(PGP encryption available)"]
    end
    
    subgraph "Required Information"
        ProductName["Product/Driver Name"]
        Version["Version/Branch"]
        Details["Vulnerability Details"]
    end
    
    subgraph "NVIDIA Response"
        PSIRT["Product Security<br/>Incident Response Team"]
        Evaluation["Security Evaluation"]
        Remediation["Patch/Fix Development"]
        Disclosure["Coordinated Disclosure"]
    end
    
    Researcher --> WebForm
    Developer --> Email
    User --> WebForm
    
    WebForm --> ProductName
    Email --> ProductName
    ProductName --> Version
    Version --> Details
    
    Details --> PSIRT
    PSIRT --> Evaluation
    Evaluation --> Remediation
    Remediation --> Disclosure
    
    Email -.->|"Use PGP key for<br/>sensitive information"| PSIRT
```

### Reporting Methods

**Primary Reporting Channels:**

| Method | Details | Use Case |
|--------|---------|----------|
| **Web Form** | [Security Vulnerability Submission Form](https://www.nvidia.com/object/submit-security-vulnerability.html) | Preferred for most reports |
| **Email** | `psirt@nvidia.com` | Encrypted communication option |

[SECURITY.md:10-11]()

**Email Reporting Guidelines:**

When reporting via email, the following practices are recommended:

1. **PGP Encryption:** Use NVIDIA's public PGP key for secure communication [SECURITY.md:12]()
   - Key available at: https://www.nvidia.com/en-us/security/pgp-key

2. **Required Information:** [SECURITY.md:13-14]()
   - Product/Driver name
   - Version/branch containing the vulnerability

Sources: [SECURITY.md:1-15]()

### Information Security Classification

When reporting vulnerabilities, include the following information structure:

```mermaid
graph LR
    subgraph "Vulnerability Report Components"
        Product["Product Identification<br/>- Product name<br/>- Component affected"]
        Version["Version Information<br/>- Specific version<br/>- Branch name<br/>- Commit SHA if known"]
        Description["Vulnerability Description<br/>- Type of vulnerability<br/>- Attack vector<br/>- Impact assessment"]
        Reproduction["Reproduction Steps<br/>- Minimal example<br/>- Environment details<br/>- Prerequisites"]
        Evidence["Supporting Evidence<br/>- Proof of concept<br/>- Screenshots<br/>- Logs"]
    end
    
    Product --> Version
    Version --> Description
    Description --> Reproduction
    Reproduction --> Evidence
```

For the cccl-gha repository specifically, reports should identify:
- Whether the vulnerability affects workflow generation, execution, or results collection
- Which scripts or actions are impacted
- Potential for privilege escalation or information disclosure
- Impact on CI/CD integrity

Sources: [SECURITY.md:13-14]()

### Responsible Disclosure

NVIDIA follows responsible disclosure practices:

1. **Acknowledgment:** NVIDIA's Product Security Incident Response Team (PSIRT) acknowledges receipt
2. **Evaluation:** Security team evaluates severity and scope
3. **Remediation:** Patches developed and tested
4. **Coordinated Disclosure:** Public disclosure coordinated with reporter
5. **Credit:** Security researchers appropriately credited (if desired)

The timeline and process follow industry-standard responsible disclosure practices, balancing the need for user protection with thorough remediation.

Sources: [SECURITY.md:1-15]()

---

## Compliance Summary

### License Compliance Checklist

When using or distributing code from this repository, ensure compliance with:

| Requirement | Components | Action Required |
|-------------|------------|-----------------|
| **Apache License Notice** | Thrust, most components | Include LICENSE file and NOTICE (if present) |
| **LLVM Exception Notice** | libcu++ | Include license with LLVM exceptions text |
| **BSD 3-Clause Notice** | CUB | Retain copyright notice in source/binary distributions |
| **Boost License Notice** | Iterator/Tuple utilities | Include copyright and disclaimer in copies |
| **Modified File Marking** | Any modified files | Mark files prominently with change notice |
| **NVIDIA GPU Restriction** | NVIDIA-licensed components | Use only with NVIDIA GPU systems |

### Export Control Compliance

The software is subject to United States export control laws and regulations:

- Cannot ship to embargoed countries [LICENSE:363-364]()
- Reporter must confirm not resident/citizen of embargoed country [LICENSE:365]()
- Subject to Bureau of Industry and Security regulations [LICENSE:363]()
- Subject to OFAC economic sanctions [LICENSE:363]()

Sources: [LICENSE:363-365]()

### Community Participation Requirements

All participants must:

1. **Follow Code of Conduct** in all project spaces [CODE_OF_CONDUCT.md:56-62]()
2. **Report violations** to `GitHub_Conduct@nvidia.com` [CODE_OF_CONDUCT.md:66]()
3. **Report security issues** via proper channels (not GitHub) [SECURITY.md:5]()
4. **Respect license terms** for all components used [LICENSE:1-467]()

Sources: [CODE_OF_CONDUCT.md:56-74](), [SECURITY.md:5](), [LICENSE:1-467]()

---

# Page: Configuration Guide

# Configuration Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)

</details>



## Purpose and Scope

This guide covers the configuration system for the cccl-gha workflow orchestration. The primary configuration artifact is the `matrix.yaml` file, which defines all possible job combinations (projects, CUDA versions, compilers, GPU architectures, etc.) that can be executed in CI workflows. This page provides an overview of the configuration structure, the tag system, and the processing pipeline that transforms human-readable configuration into executable jobs.

For detailed information on specific topics:
- Matrix YAML schema specification: see [Matrix YAML Structure](#2.1)
- Tag validation, defaults, and derived values: see [Tags and Parameters](#2.2)
- Job filtering and exclusion rules: see [Exclusions and Filtering](#2.3)
- The workflow generation pipeline: see [Workflow Generation](#3)
- Generated output formats: see [Generated Artifacts](#3.3)

---

## Configuration Architecture

The configuration system follows a declarative model where users specify **matrix jobs** in YAML format. Each matrix job describes a build/test configuration using a set of **tags** (key-value pairs). The `build-workflow.py` script processes these matrix jobs through multiple transformation stages to produce concrete job specifications that can be executed by GitHub Actions.

### Configuration to Execution Flow

```mermaid
graph TB
    subgraph "Configuration Layer"
        MatrixYAML["matrix.yaml<br/>Human-readable job definitions"]
        Workflows["workflows:<br/>pull_request, nightly, weekly"]
        TagDefs["tags:<br/>project, ctk, cxx, gpu, etc"]
        Exclusions["exclude:<br/>Invalid combinations"]
    end
    
    subgraph "Processing Pipeline (build-workflow.py)"
        Validate["validate_tags()<br/>Schema validation"]
        SetDefaults["set_default_tags()<br/>Fill optional values"]
        Explode["explode_tags()<br/>Expand list values"]
        Canonicalize["canonicalize_tags()<br/>Resolve aliases"]
        Derive["set_derived_tags()<br/>Compute sm, std:all"]
        Exclude["remove_excluded_jobs()<br/>Apply exclusions"]
    end
    
    subgraph "Output Artifacts"
        WorkflowJSON["workflow.json<br/>Fully specified jobs"]
        DispatchJSON["dispatch.json<br/>Grouped by OS/pattern"]
    end
    
    MatrixYAML --> Validate
    Workflows --> Validate
    TagDefs --> Validate
    Validate --> SetDefaults
    SetDefaults --> Explode
    Explode --> Canonicalize
    Canonicalize --> Derive
    Derive --> Exclude
    Exclusions --> Exclude
    Exclude --> WorkflowJSON
    WorkflowJSON --> DispatchJSON
    
    style MatrixYAML fill:#f9f9f9
    style WorkflowJSON fill:#f9f9f9
```

**Configuration Processing Pipeline**

Sources: [.github/actions/workflow-build/build-workflow.py:811-919](), [.github/actions/workflow-build/build-workflow.py:902-920]()

---

## Matrix Job Definition

A **matrix job** is a JSON/YAML object that describes a single build/test configuration. Matrix jobs are defined in the `matrix.yaml` file under named workflows (e.g., `pull_request`, `nightly`).

### Matrix Job Structure

```mermaid
graph LR
    subgraph "Input Matrix Job"
        Input["project: [libcudacxx, thrust]<br/>ctk: 11.1<br/>cxx: gcc10<br/>cudacxx: nvcc<br/>std: [17, 20]<br/>gpu: t4<br/>jobs: [build, test]"]
    end
    
    subgraph "After Tag Explosion"
        E1["project: libcudacxx<br/>ctk: 11.1<br/>cxx: gcc10<br/>cudacxx: nvcc<br/>std: 17<br/>gpu: t4<br/>jobs: [build, test]"]
        E2["project: libcudacxx<br/>ctk: 11.1<br/>cxx: gcc10<br/>cudacxx: nvcc<br/>std: 20<br/>gpu: t4<br/>jobs: [build, test]"]
        E3["project: thrust<br/>ctk: 11.1<br/>cxx: gcc10<br/>cudacxx: nvcc<br/>std: 17<br/>gpu: t4<br/>jobs: [build, test]"]
        E4["project: thrust<br/>ctk: 11.1<br/>cxx: gcc10<br/>cudacxx: nvcc<br/>std: 20<br/>gpu: t4<br/>jobs: [build, test]"]
    end
    
    subgraph "After Derived Tags"
        D1["project: libcudacxx<br/>ctk: 11.1<br/>cxx: gcc10<br/>cudacxx: nvcc<br/>std: 17<br/>gpu: t4<br/>sm: 75-real<br/>jobs: [build, test]"]
    end
    
    Input --> E1
    Input --> E2
    Input --> E3
    Input --> E4
    E1 --> D1
```

**Tag Explosion and Derivation Example**

Sources: [.github/actions/workflow-build/build-workflow.py:4-54](), [.github/actions/workflow-build/build-workflow.py:877-900]()

### Matrix Job Conceptual Model

The configuration system operates on these core concepts:

| Concept | Description | Example |
|---------|-------------|---------|
| **Matrix Job** | A set of tags describing a build/test configuration | `{project: thrust, ctk: 11.1, cxx: gcc10}` |
| **Tag** | A key-value pair in a matrix job | `ctk: 11.1` |
| **Tag Explosion** | Expanding list-valued tags into multiple jobs | `std: [17, 20]` → two jobs |
| **Tag Canonicalization** | Resolving aliases to standard forms | `gcc10` → `gcc10` (with version lookup) |
| **Derived Tag** | Tag computed from other tags | `sm: gpu` → `sm: 75-real` (from `gpu: t4`) |
| **Dispatch Group** | Collection of related jobs for UI organization | "Thrust CTK11.1 nvcc GCC" |

Sources: [.github/actions/workflow-build/build-workflow.py:4-54]()

---

## Tag System Overview

Tags are the fundamental building blocks of matrix jobs. Each tag represents a dimension of the configuration space (e.g., compiler version, CUDA toolkit, C++ standard).

### Tag Categories

```mermaid
graph TB
    subgraph "Core Tags"
        Project["project<br/>Required<br/>libcudacxx, cub, thrust"]
        Jobs["jobs<br/>Required<br/>build, test, examples"]
    end
    
    subgraph "Compiler Tags"
        CTK["ctk<br/>Required<br/>11.1, 12.0, 12.6"]
        CXX["cxx<br/>Required<br/>gcc10, gcc12, clang16"]
        CUDACXX["cudacxx<br/>Default: nvcc<br/>nvcc, clang"]
    end
    
    subgraph "Architecture Tags"
        CPU["cpu<br/>Default: amd64<br/>amd64, arm64"]
        GPU["gpu<br/>Conditional<br/>v100, t4, a100"]
        SM["sm<br/>Derived<br/>60, 75-real, gpu"]
    end
    
    subgraph "Language Tags"
        STD["std<br/>Conditional<br/>11, 14, 17, 20, all"]
    end
    
    subgraph "Metadata Tags"
        Origin["origin<br/>Auto-generated<br/>Workflow location"]
    end
```

**Tag Organization by Category**

Sources: [.github/actions/workflow-build/build-workflow.py:284-302](), [.github/actions/workflow-build/build-workflow.py:305-321]()

### Tag Properties

Each tag definition in `matrix.yaml` specifies:

| Property | Description | Effect |
|----------|-------------|--------|
| `required` | Must be present in every matrix job | Validation fails if missing |
| `default` | Value used if tag not specified | Makes tag optional |
| `validation` | Schema constraints | Type checking, allowed values |
| `derivation` | Computed from other tags | Not specified by user |

Sources: [.github/actions/workflow-build/build-workflow.py:284-302]()

### Tag Processing Stages

```mermaid
graph LR
    Input["Input Matrix Job"] --> V["validate_tags()<br/>Check required tags<br/>Check unknown tags"]
    V --> D["set_default_tags()<br/>Fill in defaults"]
    D --> E["explode_tags()<br/>Expand lists"]
    E --> C["canonicalize_tags()<br/>gcc10 → gcc10<br/>11.1 → 11.1"]
    C --> Der["set_derived_tags()<br/>sm: gpu → sm: 75-real<br/>std: all → std: [17,20]"]
    Der --> Output["Processed Matrix Job"]
```

**Tag Processing Pipeline**

Sources: [.github/actions/workflow-build/build-workflow.py:811-860](), [.github/actions/workflow-build/build-workflow.py:902-920]()

---

## Configuration File Structure

The `matrix.yaml` file is organized into top-level sections that define the vocabulary and rules for matrix jobs.

### Top-Level Sections

```yaml
# Version identifier for devcontainer images
devcontainer_version: "24.10"

# All supported C++ standards
all_stds: [11, 14, 17, 20, 23]

# Tag definitions and properties
tags:
  project:
    required: true
  ctk:
    required: true
  cxx:
    required: true
  std:
    default: null
  # ... more tags

# CUDA Toolkit versions and properties
ctk_versions:
  "11.1":
    stds: [11, 14, 17]
  "12.6":
    aka: "curr"
    stds: [11, 14, 17, 20, 23]

# Host compiler definitions
host_compilers:
  gcc:
    name: "GCC"
    exe: "g++"
    container_tag: "gcc"
    versions:
      "10":
        stds: [11, 14, 17, 20]
      "12":
        aka: "12.3"
        stds: [11, 14, 17, 20, 23]

# Device compiler definitions
device_compilers:
  nvcc:
    name: "nvcc"
    exe: "nvcc"
  clang:
    name: "clang++"
    exe: "clang++"

# GPU definitions
gpus:
  t4:
    sm: "75-real"
    testing: false
  a100:
    sm: "80"
    testing: true

# Project definitions
projects:
  libcudacxx:
    name: "libcu++"
    stds: [11, 14, 17, 20]
  thrust:
    name: "Thrust"
    stds: [14, 17, 20]

# Job type definitions
jobs:
  build:
    name: "Build"
    gpu: false
  test:
    name: "Test"
    gpu: true
    needs: "build"

# Workflow definitions
workflows:
  pull_request:
    - project: [libcudacxx, thrust]
      ctk: "12.6"
      cxx: gcc12
      std: [17, 20]
      gpu: t4
      jobs: [build, test]
  
  # Invalid combinations to exclude
  exclude:
    - ctk: "11.1"
      std: 20
```

**Matrix YAML Structure Overview**

Sources: [.github/actions/workflow-build/build-workflow.py:114-130](), [.github/actions/workflow-build/build-workflow.py:133-173](), [.github/actions/workflow-build/build-workflow.py:204-224]()

### Section Relationships

```mermaid
graph TB
    Tags["tags:<br/>Define schema<br/>required, defaults"]
    CTK["ctk_versions:<br/>Define CUDA versions<br/>supported stds"]
    HC["host_compilers:<br/>Define C++ compilers<br/>versions, stds"]
    DC["device_compilers:<br/>Define CUDA compilers<br/>nvcc, clang"]
    GPU["gpus:<br/>Define GPU types<br/>SM architectures"]
    Proj["projects:<br/>Define project configs<br/>libcudacxx, thrust, cub"]
    JobTypes["jobs:<br/>Define job types<br/>build, test, examples"]
    
    Workflows["workflows:<br/>Define matrix jobs<br/>pull_request, nightly"]
    Exclude["exclude:<br/>Invalid combinations"]
    
    Tags --> Workflows
    CTK --> Workflows
    HC --> Workflows
    DC --> Workflows
    GPU --> Workflows
    Proj --> Workflows
    JobTypes --> Workflows
    
    Workflows --> Exclude
    
    CTK -.->|stds intersection| Workflows
    HC -.->|stds intersection| Workflows
    Proj -.->|stds intersection| Workflows
    GPU -.->|sm derivation| Workflows
```

**Configuration Section Dependencies**

Sources: [.github/actions/workflow-build/build-workflow.py:323-338](), [.github/actions/workflow-build/build-workflow.py:852-876]()

---

## Workflow Definitions

Workflows are named collections of matrix jobs that define when and what to execute. Common workflows include `pull_request`, `nightly`, and `weekly`.

### Workflow Syntax

Each workflow entry in the `workflows` section is a list of matrix job objects:

```yaml
workflows:
  pull_request:
    # Example 1: Basic matrix job
    - project: libcudacxx
      ctk: "12.6"
      cxx: gcc12
      std: 17
      gpu: t4
      jobs: [build, test]
    
    # Example 2: Multi-value tags (will explode)
    - project: [libcudacxx, thrust, cub]
      ctk: "12.6"
      cxx: [gcc12, clang16]
      std: [17, 20]
      gpu: v100
      jobs: [build, test]
    
    # Example 3: Using derived tags
    - project: thrust
      ctk: "11.1"
      cxx: gcc10
      std: all          # Derives intersection of supported stds
      gpu: t4
      sm: gpu           # Derives from gpu definition
      jobs: test
```

Sources: [.github/actions/workflow-build/build-workflow.py:922-960]()

### Workflow Selection

The `build-workflow.py` script accepts a `--workflows` argument to select which workflows to process:

```bash
# Single workflow
build-workflow.py matrix.yaml --workflows pull_request

# Multiple workflows (will be merged)
build-workflow.py matrix.yaml --workflows pull_request nightly

# Workflow with filtering
build-workflow.py matrix.yaml --workflows pull_request --dirty-projects thrust
```

Sources: [.github/actions/workflow-build/build-workflow.py:1104-1136]()

---

## Tag Explosion Process

Tag explosion is the process of expanding list-valued tags into multiple matrix jobs, creating the Cartesian product of all possible combinations.

### Explosion Algorithm

```mermaid
graph TB
    Input["Input:<br/>project: [libcudacxx, thrust]<br/>std: [17, 20]<br/>ctk: 12.6"]
    
    CheckProject{"Is 'project'<br/>a list?"}
    ExplodeProject["Create job for<br/>each project value"]
    
    CheckStd{"Is 'std'<br/>a list?"}
    ExplodeStd["Create job for<br/>each std value"]
    
    Done["Output:<br/>4 matrix jobs"]
    
    Input --> CheckProject
    CheckProject -->|Yes| ExplodeProject
    CheckProject -->|No| CheckStd
    ExplodeProject --> CheckStd
    CheckStd -->|Yes| ExplodeStd
    CheckStd -->|No| Done
    ExplodeStd --> Done
```

**Tag Explosion Decision Flow**

### Explosion Example

| Input | After First Explosion | After Second Explosion |
|-------|----------------------|------------------------|
| `project: [a, b]`<br/>`std: [17, 20]`<br/>`ctk: 12.6` | `project: a, std: [17, 20], ctk: 12.6`<br/>`project: b, std: [17, 20], ctk: 12.6` | `project: a, std: 17, ctk: 12.6`<br/>`project: a, std: 20, ctk: 12.6`<br/>`project: b, std: 17, ctk: 12.6`<br/>`project: b, std: 20, ctk: 12.6` |

Sources: [.github/actions/workflow-build/build-workflow.py:877-900]()

### Non-Exploded Tags

The `jobs` tag is intentionally left as a list to optimize scheduling. Multiple job types in a single matrix entry allow the system to create producer/consumer dependencies efficiently:

```yaml
# This creates a two-stage job: build (producer) → test (consumer)
- project: thrust
  ctk: "12.6"
  cxx: gcc12
  jobs: [build, test]  # NOT exploded
```

Sources: [.github/actions/workflow-build/build-workflow.py:877-883](), [.github/actions/workflow-build/build-workflow.py:507-540]()

---

## Tag Canonicalization

Canonicalization resolves aliases and incomplete specifications to their standard forms, ensuring consistent processing downstream.

### Compiler Name Canonicalization

The `canonicalize_host_compiler_name()` function handles various input formats:

| Input Format | Canonical Output | Notes |
|--------------|------------------|-------|
| `gcc` | `gcc12` | Uses latest version |
| `gcc10` | `gcc10` | Already canonical |
| `gcc-12` | `gcc12` | Removes hyphen |
| `gcc-12.3` | `gcc12` | Uses major version |

The function first parses the input to extract compiler ID and version using regex `^([a-z]+)-?([\d\.]+)?$`, then looks up the compiler definition and resolves aliases.

Sources: [.github/actions/workflow-build/build-workflow.py:132-173]()

### CTK Version Canonicalization

CTK versions support aliases for convenience:

```yaml
ctk_versions:
  "12.6":
    aka: "curr"
    stds: [11, 14, 17, 20, 23]
```

Both `ctk: "12.6"` and `ctk: curr` resolve to the canonical version `"12.6"`.

Sources: [.github/actions/workflow-build/build-workflow.py:113-124]()

---

## Derived Tags

Derived tags are computed from other tags rather than specified by the user. This provides convenience and ensures consistency.

### SM Architecture Derivation

The special value `sm: gpu` automatically derives the SM architecture from the `gpu` tag:

```yaml
# Input
- project: thrust
  gpu: t4
  sm: gpu

# After derivation
- project: thrust
  gpu: t4
  sm: "75-real"  # Derived from gpu definition
```

Sources: [.github/actions/workflow-build/build-workflow.py:852-858]()

### Standard Version Derivation

The special value `std: all` computes the intersection of all supported C++ standards based on the CTK version, host compiler, device compiler, and project:

```yaml
# Input
- project: libcudacxx  # supports [11, 14, 17, 20]
  ctk: "12.6"          # supports [11, 14, 17, 20, 23]
  cxx: gcc12           # supports [11, 14, 17, 20, 23]
  std: all

# After derivation
- project: libcudacxx
  ctk: "12.6"
  cxx: gcc12
  std: [11, 14, 17, 20]  # Intersection of all constraints
```

The intersection logic is implemented in `lookup_supported_stds()`:

Sources: [.github/actions/workflow-build/build-workflow.py:323-338](), [.github/actions/workflow-build/build-workflow.py:859-861]()

### Job Dependency Derivation

Job types can specify dependencies using the `needs` property. The system automatically adds dependencies to the `jobs` list:

```yaml
# Job type definition
jobs:
  test:
    needs: build

# Input matrix job
- project: thrust
  jobs: [test]

# After derivation
- project: thrust
  jobs: [build, test]  # build added as dependency
```

Sources: [.github/actions/workflow-build/build-workflow.py:260-282](), [.github/actions/workflow-build/build-workflow.py:863-868]()

---

## Exclusions

The `exclude` workflow defines invalid tag combinations that should be filtered out. Exclusions are applied after all other processing stages.

### Exclusion Syntax

Exclusions use the same matrix job syntax but are interpreted as filter patterns:

```yaml
workflows:
  exclude:
    # Exclude all jobs with CTK 11.1 and C++20
    - ctk: "11.1"
      std: 20
    
    # Exclude specific compiler/GPU combinations
    - cxx: gcc10
      gpu: a100
    
    # Exclude multiple values
    - project: [libcudacxx, thrust]
      ctk: "11.1"
      std: [20, 23]
```

Sources: [.github/actions/workflow-build/build-workflow.py:748-751]()

### Exclusion Matching Logic

The `apply_matrix_job_exclusion()` function performs partial or complete exclusions:

```mermaid
graph TB
    Start["Matrix Job:<br/>std: [17, 20, 23]<br/>ctk: 11.1"]
    
    Exclusion["Exclusion:<br/>std: [20, 23]<br/>ctk: 11.1"]
    
    CheckTags{"All exclusion<br/>tags present?"}
    NoMatch["No exclusion<br/>Return original job"]
    
    CheckMatch{"All tag values<br/>match?"}
    PartialMatch["Partial match:<br/>Remove matched values<br/>Return std: [17], ctk: 11.1"]
    CompleteMatch["Complete match:<br/>Return None<br/>Job excluded"]
    
    Start --> CheckTags
    Exclusion --> CheckTags
    CheckTags -->|No| NoMatch
    CheckTags -->|Yes| CheckMatch
    CheckMatch -->|Partial| PartialMatch
    CheckMatch -->|Complete| CompleteMatch
```

**Exclusion Matching Decision Tree**

Sources: [.github/actions/workflow-build/build-workflow.py:753-794]()

### Exclusion Examples

| Original Matrix Job | Exclusion Pattern | Result | Reason |
|---------------------|-------------------|--------|--------|
| `ctk: 11.1, std: 20` | `ctk: 11.1, std: 20` | **Excluded** | Complete match |
| `ctk: 11.1, std: [17, 20]` | `ctk: 11.1, std: 20` | `ctk: 11.1, std: [17]` | Partial match |
| `ctk: 11.1, std: 20, cxx: gcc12` | `ctk: 11.1, std: 20` | **Excluded** | All exclusion tags match |
| `ctk: 12.6, std: 20` | `ctk: 11.1, std: 20` | **Not excluded** | ctk doesn't match |

Sources: [.github/actions/workflow-build/build-workflow.py:796-809]()

---

## Configuration Validation

The system performs comprehensive validation to catch errors early and provide helpful error messages.

### Validation Stages

```mermaid
graph TB
    Input["Matrix Job Input"]
    
    V1["Check required tags<br/>validate_tags()"]
    V2["Check unknown tags<br/>validate_tags()"]
    V3["Check tag value validity<br/>get_gpu(), get_ctk(), etc"]
    V4["Check cudacxx=clang<br/>requires cxx=clang"]
    
    Error1["Error: Missing<br/>required tag"]
    Error2["Error: Unknown tag"]
    Error3["Error: Invalid<br/>tag value"]
    Error4["Error: Invalid<br/>compiler combo"]
    
    Success["Validation Passed"]
    
    Input --> V1
    V1 -->|Missing| Error1
    V1 -->|OK| V2
    V2 -->|Unknown| Error2
    V2 -->|OK| V3
    V3 -->|Invalid| Error3
    V3 -->|OK| V4
    V4 -->|Invalid| Error4
    V4 -->|OK| Success
```

**Validation Flow**

Sources: [.github/actions/workflow-build/build-workflow.py:811-833]()

### Error Message Format

Validation errors include rich context to help locate and fix issues:

```
ci/matrix.yaml:42 (job 3): Missing required tag 'ctk'
  Input: {project: thrust, cxx: gcc12, std: 17, gpu: t4, jobs: [build, test]}
```

The error message includes:
- File path and line number
- Job index in the workflow
- Specific error description
- Original matrix job specification

Sources: [.github/actions/workflow-build/build-workflow.py:109-111](), [.github/actions/workflow-build/build-workflow.py:736-746]()

---

## Configuration Processing Reference

### Key Functions in build-workflow.py

| Function | Purpose | Line Range |
|----------|---------|------------|
| `parse_workflow_matrix_jobs()` | Parse and preprocess workflow matrix jobs | [922-960]() |
| `preprocess_matrix_jobs()` | Orchestrate validation, defaults, explosion, canonicalization | [902-920]() |
| `validate_tags()` | Validate required tags and tag names | [811-833]() |
| `set_default_tags()` | Fill in default values for optional tags | [834-843]() |
| `explode_tags()` | Recursively expand list-valued tags | [886-900]() |
| `canonicalize_tags()` | Resolve aliases to canonical forms | [845-850]() |
| `set_derived_tags()` | Compute derived tag values | [852-876]() |
| `remove_excluded_jobs()` | Apply exclusion filters | [796-809]() |
| `canonicalize_host_compiler_name()` | Canonicalize compiler names | [138-173]() |
| `canonicalize_ctk_version()` | Canonicalize CTK versions | [113-124]() |
| `lookup_supported_stds()` | Compute std intersection | [323-338]() |

Sources: [.github/actions/workflow-build/build-workflow.py:1-1140]()

### Configuration File Location

The primary configuration file is located at:
- **Repository path**: `ci/matrix.yaml` (expected location)
- **Command-line argument**: First positional argument to `build-workflow.py`
- **Environment context**: Specified in workflow-build action

The file path is stored in the global `matrix_yaml['filename']` variable after loading.

Sources: [.github/actions/workflow-build/build-workflow.py:1104-1128]()

---

## Common Configuration Patterns

### Pattern 1: Compiler Matrix

Test multiple compilers with the same configuration:

```yaml
- project: thrust
  ctk: "12.6"
  cxx: [gcc12, clang16, clang17]  # Expands to 3 jobs
  std: 17
  gpu: t4
  jobs: [build, test]
```

### Pattern 2: Standard Matrix

Test all supported C++ standards:

```yaml
- project: libcudacxx
  ctk: "12.6"
  cxx: gcc12
  std: all  # Derives [11, 14, 17, 20]
  gpu: v100
  jobs: test
```

### Pattern 3: Multi-Project Job

Run the same configuration across multiple projects:

```yaml
- project: [libcudacxx, thrust, cub]  # Expands to 3 jobs
  ctk: "12.6"
  cxx: gcc12
  std: 17
  gpu: t4
  jobs: [build, test]
```

### Pattern 4: Build-Once, Test-Many

Leverage two-stage jobs to build once and test on multiple GPUs:

```yaml
# Single build job will be created
# Multiple test jobs will be created (one per GPU)
- project: thrust
  ctk: "12.6"
  cxx: gcc12
  std: 17
  gpu: [v100, t4, a100]  # Expands test jobs only
  jobs: [build, test]
```

Sources: [.github/actions/workflow-build/build-workflow.py:493-540]()

### Pattern 5: Exclusion with Partial Match

Exclude specific standards from older CTK versions:

```yaml
workflows:
  pull_request:
    - project: thrust
      ctk: ["11.1", "12.6"]
      std: [17, 20, 23]
      # ... other tags

  exclude:
    - ctk: "11.1"
      std: [20, 23]  # Only std 17 will run for CTK 11.1
```

Sources: [.github/actions/workflow-build/build-workflow.py:753-794]()

---

## Next Steps

For detailed information on specific aspects of configuration:

- **Matrix YAML Schema**: See [Matrix YAML Structure](#2.1) for complete schema documentation
- **Tag System Details**: See [Tags and Parameters](#2.2) for tag properties, validation rules, and derived tag logic
- **Exclusion Rules**: See [Exclusions and Filtering](#2.3) for advanced exclusion patterns and dirty project filtering
- **Workflow Generation**: See [Workflow Generation](#3) for how configuration transforms into executable jobs
- **Testing Configuration**: See [Troubleshooting Guide](#8.4) for validating and debugging configuration changes

Sources: [.github/actions/workflow-build/build-workflow.py:1-1140]()

---

# Page: Matrix YAML Structure

# Matrix YAML Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)

</details>



This document provides detailed documentation of the `matrix.yaml` schema, which serves as the declarative configuration file for defining all possible job combinations in the CCCL CI system. The matrix defines projects, CUDA Toolkit versions, compilers, GPUs, job types, and workflows.

For information about how tags are validated, canonicalized, and processed during workflow generation, see [Tags and Parameters](#2.2). For information about exclusions and filtering mechanisms, see [Exclusions and Filtering](#2.3). For the complete workflow generation pipeline that processes this file, see [Workflow Generation](#3).

## Overview

The `matrix.yaml` file is located at `ci/matrix.yaml` and serves as the single source of truth for all CI job configurations. The file is parsed by `build-workflow.py` which loads it using YAML safe loading and preprocesses version numbers into strings.

**Purpose**: Define the complete configuration space for CCCL CI jobs, including:
- Available CUDA Toolkit (CTK) versions and their supported C++ standards
- Host compilers (gcc, clang, MSVC) with version-specific attributes
- Device compilers (nvcc, clang) for CUDA code compilation
- GPU architectures for testing
- Projects (libcudacxx, CUB, Thrust) with their requirements
- Job types (build, test, etc.) with execution characteristics
- Tags that parameterize job configurations
- Workflow definitions that combine these elements

Sources: [.github/actions/workflow-build/build-workflow.py:1123-1127]()

## Top-Level Schema Structure

```mermaid
graph TB
    MatrixYAML["matrix.yaml"]
    
    MatrixYAML --> CTKVersions["ctk_versions:<br/>CUDA Toolkit definitions"]
    MatrixYAML --> HostCompilers["host_compilers:<br/>C++ compiler definitions"]
    MatrixYAML --> DeviceCompilers["device_compilers:<br/>CUDA compiler definitions"]
    MatrixYAML --> GPUs["gpus:<br/>GPU architecture definitions"]
    MatrixYAML --> Projects["projects:<br/>Project configurations"]
    MatrixYAML --> Jobs["jobs:<br/>Job type definitions"]
    MatrixYAML --> Tags["tags:<br/>Parameter schema"]
    MatrixYAML --> Workflows["workflows:<br/>Job combinations"]
    MatrixYAML --> DevcontainerVersion["devcontainer_version:<br/>Container image version"]
    MatrixYAML --> AllStds["all_stds:<br/>Supported C++ standards"]
    
    CTKVersions --> GetCTK["get_ctk()"]
    HostCompilers --> GetHostCompiler["get_host_compiler()"]
    DeviceCompilers --> GetDeviceCompiler["get_device_compiler()"]
    GPUs --> GetGPU["get_gpu()"]
    Projects --> GetProject["get_project()"]
    Jobs --> GetJobTypeInfo["get_job_type_info()"]
    Tags --> GetTagInfo["get_tag_info()"]
    Workflows --> ParseWorkflowMatrixJobs["parse_workflow_matrix_jobs()"]
```

**Diagram: Matrix YAML Top-Level Structure**

The matrix file is preprocessed by `preprocess_matrix_yaml()` which normalizes all version keys to strings. Each top-level section has a corresponding getter function that validates and retrieves configuration data with appropriate defaults.

Sources: [.github/actions/workflow-build/build-workflow.py:1087-1101](), [.github/actions/workflow-build/build-workflow.py:126-302]()

## CTK Versions Section

The `ctk_versions` section defines available CUDA Toolkit versions and their properties.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `<version>` | object | Yes | Version string (e.g., "11.1", "12.0") as key |
| `<version>.stds` | list[int] | Yes | Supported C++ standards for this CTK version |
| `<version>.aka` | string | No | Alternative name/alias for this version |

### Example

```yaml
ctk_versions:
  "11.1":
    stds: [11, 14, 17]
  "12.0":
    stds: [11, 14, 17, 20]
    aka: "latest"
```

### Processing

The `canonicalize_ctk_version()` function resolves CTK version strings, including aliases defined in the `aka` field. The `get_ctk()` function retrieves the full CTK definition and adds the version string to the result.

```mermaid
graph LR
    Input["Input: 'latest'"]
    Canonicalize["canonicalize_ctk_version()"]
    GetCTK["get_ctk()"]
    Output["Output: {version: '12.0', stds: [11,14,17,20]}"]
    
    Input --> Canonicalize
    Canonicalize -->|"Resolves aka"| GetCTK
    GetCTK --> Output
```

**Diagram: CTK Version Resolution Process**

Sources: [.github/actions/workflow-build/build-workflow.py:113-129]()

## Host Compilers Section

The `host_compilers` section defines C++ compilers used for host code compilation.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `<id>` | object | Yes | Compiler family identifier (e.g., "gcc", "clang", "msvc") |
| `<id>.name` | string | Yes | Human-readable compiler name |
| `<id>.container_tag` | string | Yes | Tag used in devcontainer image names |
| `<id>.exe` | string | Yes | Compiler executable name |
| `<id>.versions` | object | Yes | Version-specific configurations |
| `<id>.versions.<version>` | object | Yes | Configuration for specific version |
| `<id>.versions.<version>.stds` | list[int] | Yes | Supported C++ standards |
| `<id>.versions.<version>.aka` | string | No | Alternative name for this version |

### Example

```yaml
host_compilers:
  gcc:
    name: "GCC"
    container_tag: "gcc"
    exe: "g++"
    versions:
      "10":
        stds: [11, 14, 17, 20]
      "12":
        stds: [11, 14, 17, 20, 23]
        aka: "latest"
  msvc:
    name: "MSVC"
    container_tag: "cl"
    exe: "cl.exe"
    versions:
      "14.29":
        stds: [14, 17, 20]
```

### Canonicalization

The `parse_cxx_string()` function parses compiler strings like "gcc", "gcc10", or "gcc-12" into `(id, version)` tuples. The `canonicalize_host_compiler_name()` function normalizes these to the format `"gcc10"` (no separator, explicit version). If no version is specified, the latest version is selected by sorting version strings numerically.

```mermaid
graph TB
    Input1["'gcc'"]
    Input2["'gcc10'"]
    Input3["'gcc-12'"]
    
    Parse["parse_cxx_string()"]
    
    Input1 --> Parse
    Input2 --> Parse
    Input3 --> Parse
    
    Parse --> Tuple1["('gcc', None)"]
    Parse --> Tuple2["('gcc', '10')"]
    Parse --> Tuple3["('gcc', '12')"]
    
    Canonicalize["canonicalize_host_compiler_name()"]
    
    Tuple1 --> Canonicalize
    Tuple2 --> Canonicalize
    Tuple3 --> Canonicalize
    
    Canonicalize -->|"Selects latest if None"| Output1["'gcc12'"]
    Canonicalize --> Output2["'gcc10'"]
    Canonicalize --> Output3["'gcc12'"]
```

**Diagram: Host Compiler Name Canonicalization**

The `is_windows()` function determines if a job targets Windows by checking if `container_tag == "cl"`.

Sources: [.github/actions/workflow-build/build-workflow.py:133-172](), [.github/actions/workflow-build/build-workflow.py:176-201](), [.github/actions/workflow-build/build-workflow.py:340-342]()

## Device Compilers Section

The `device_compilers` section defines compilers for CUDA device code.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `<id>` | object | Yes | Compiler identifier (e.g., "nvcc", "clang") |
| `<id>.name` | string | Yes | Human-readable compiler name |
| `<id>.exe` | string | Yes | Compiler executable name |

### Example

```yaml
device_compilers:
  nvcc:
    name: "NVCC"
    exe: "nvcc"
  clang:
    name: "Clang CUDA"
    exe: "clang++"
```

### Version Resolution

Unlike host compilers, device compiler versions are not defined in the matrix file. Instead, they are derived:
- For `nvcc`: version and supported standards come from the CTK version
- For `clang`: version and supported standards come from the host compiler

The `get_device_compiler()` function implements this logic and raises an exception for unknown device compilers.

```mermaid
graph TB
    MatrixJob["matrix_job"]
    GetDevice["get_device_compiler()"]
    
    MatrixJob --> GetDevice
    
    GetDevice --> CheckID{id == ?}
    
    CheckID -->|"'nvcc'"| GetCTK["get_ctk(matrix_job['ctk'])"]
    CheckID -->|"'clang'"| GetHostCompiler["get_host_compiler(matrix_job['cxx'])"]
    CheckID -->|"other"| Error["Exception: Cannot determine version"]
    
    GetCTK --> NVCCResult["version: ctk.version<br/>stds: ctk.stds"]
    GetHostCompiler --> ClangResult["version: host_compiler.version<br/>stds: host_compiler.stds"]
```

**Diagram: Device Compiler Version Derivation**

Sources: [.github/actions/workflow-build/build-workflow.py:204-223]()

## GPUs Section

The `gpus` section defines GPU architectures available for testing.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `<id>` | object | Yes | GPU identifier (e.g., "t4", "v100") |
| `<id>.sm` | string | Yes | CUDA compute capability (e.g., "75", "70") |
| `<id>.testing` | bool | No | Whether to use testing runner pool (default: false) |

### Example

```yaml
gpus:
  t4:
    sm: "75"
  v100:
    sm: "70"
    testing: true
  a100:
    sm: "80"
```

### Usage

The `get_gpu()` function retrieves GPU definitions and adds the `id` field to the result. If `testing` is not specified, it defaults to `false`. The GPU's `sm` value is used to derive the `sm` tag when `sm: "gpu"` is specified in a matrix job (see `set_derived_tags()`).

Sources: [.github/actions/workflow-build/build-workflow.py:227-238](), [.github/actions/workflow-build/build-workflow.py:852-857]()

## Projects Section

The `projects` section defines the CCCL projects (libraries) being tested.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `<id>` | object | Yes | Project identifier (e.g., "libcudacxx", "cub", "thrust") |
| `<id>.name` | string | No | Human-readable name (defaults to id) |
| `<id>.stds` | list[int] | Yes | C++ standards supported by this project |
| `<id>.job_map` | object | No | Maps generic job names to project-specific jobs |

### Example

```yaml
projects:
  libcudacxx:
    name: "libcu++"
    stds: [11, 14, 17, 20]
    job_map:
      test: [test_cpu, test_gpu]
  cub:
    name: "CUB"
    stds: [14, 17, 20]
  thrust:
    name: "Thrust"
    stds: [14, 17, 20]
```

### Job Mapping

The `job_map` field allows a single job name to expand into multiple project-specific jobs. This mapping is applied by `set_derived_tags()` after dependency resolution. For example, specifying `jobs: [test]` for the libcudacxx project expands to `jobs: [test_cpu, test_gpu]`.

Sources: [.github/actions/workflow-build/build-workflow.py:242-256](), [.github/actions/workflow-build/build-workflow.py:869-874]()

## Jobs Section

The `jobs` section defines job types and their execution characteristics.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `<id>` | object | Yes | Job type identifier (e.g., "build", "test") |
| `<id>.name` | string | No | Human-readable name (defaults to capitalized id) |
| `<id>.gpu` | bool | No | Whether job requires GPU access (default: false) |
| `<id>.needs` | string | No | Job dependency (for producer/consumer pattern) |
| `<id>.invoke` | object | No | Script invocation configuration |
| `<id>.invoke.prefix` | string | No | Script name prefix (defaults to id) |
| `<id>.invoke.args` | string | No | Additional script arguments (default: "") |

### Example

```yaml
jobs:
  build:
    name: "Build"
    gpu: false
    invoke:
      prefix: "build"
  test:
    name: "Test"
    gpu: true
    needs: "build"
    invoke:
      prefix: "test"
      args: "--verbose"
```

### Dependency Resolution

The `needs` field creates producer/consumer relationships. When a job declares a dependency, the system:
1. Adds the dependency to the `jobs` list if not present (via `set_derived_tags()`)
2. Separates producers and consumers during dispatch group generation
3. Creates two-stage dispatch groups (see `generate_dispatch_group_jobs()`)

The `get_job_type_info()` function fills in default values for optional fields.

Sources: [.github/actions/workflow-build/build-workflow.py:260-281](), [.github/actions/workflow-build/build-workflow.py:862-874](), [.github/actions/workflow-build/build-workflow.py:507-539]()

## Tags Section

The `tags` section defines the schema for all configuration parameters (tags) that can appear in matrix jobs.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `<id>` | object | Yes | Tag identifier (e.g., "std", "sm", "cpu") |
| `<id>.required` | bool | No | Whether tag must be specified (default: false) |
| `<id>.default` | any | No | Default value if not specified |

### Example

```yaml
tags:
  project:
    required: true
  ctk:
    required: true
  cxx:
    required: true
  cudacxx:
    default: "nvcc"
  std:
    # No default, not required
  sm:
    # No default, not required
  cpu:
    default: "amd64"
  gpu:
    # No default, not required
  cmake_options:
    # No default, not required
```

### Tag Processing

Tags are processed in a specific order during workflow generation:
1. **Validation**: `validate_tags()` checks for required tags and unknown tags
2. **Defaults**: `set_default_tags()` applies default values
3. **Explosion**: `explode_tags()` expands list-valued tags into separate jobs
4. **Canonicalization**: `canonicalize_tags()` normalizes compiler/CTK names
5. **Derived Tags**: `set_derived_tags()` computes `sm` from `gpu`, `std: all`, and job dependencies

The `get_tag_info()` function retrieves tag definitions and computes `required` status: a tag with a `default` is never required.

```mermaid
graph LR
    TagDef["Tag Definition"]
    HasDefault{Has default?}
    HasRequired{Has required?}
    
    TagDef --> HasDefault
    HasDefault -->|Yes| NotRequired["required: false"]
    HasDefault -->|No| HasRequired
    HasRequired -->|Yes| IsRequired["required: true"]
    HasRequired -->|No| DefaultNotRequired["required: false"]
```

**Diagram: Tag Required Status Computation**

### Important Tag List

The system maintains a sorted list of tags for consistent ordering in `get_all_matrix_job_tags_sorted()`:
- **Important tags** (always first): `project`, `jobs`, `cudacxx`, `cxx`, `ctk`, `gpu`, `std`, `sm`, `cpu`
- **Other tags** (middle, alphabetically sorted)
- **Noise tags** (always last): `origin`

Sources: [.github/actions/workflow-build/build-workflow.py:284-302](), [.github/actions/workflow-build/build-workflow.py:305-320]()

## Workflows Section

The `workflows` section defines named collections of matrix jobs that represent different CI scenarios.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `<workflow_name>` | list[object] | No | List of matrix job definitions |
| `exclude` | list[object] | No | Special workflow for exclusion rules |
| `override` | list[object] | No | Special workflow that supersedes all others |

### Matrix Job Format

Each matrix job in a workflow is an object with tag-value pairs:

```yaml
workflows:
  pull_request:
    - project: libcudacxx
      jobs: [build, test]
      ctk: "12.0"
      cxx: gcc12
      std: [17, 20]
      cpu: amd64
      gpu: t4
      sm: gpu
    
    - project: [cub, thrust]
      jobs: test
      ctk: "11.1"
      cxx: clang14
      cudacxx: clang
      std: all
```

### Matrix Job Explosion

List-valued tags (except `jobs`) are exploded into separate jobs by `explode_tags()`. The example above produces:
- 1st entry → 2 jobs (std=17, std=20)
- 2nd entry → 2 × N jobs (2 projects × N standards from `std: all`)

### Workflow Processing Flow

```mermaid
graph TB
    WorkflowDef["workflows:<br/>pull_request:<br/>- {matrix_job_1}<br/>- {matrix_job_2}"]
    
    FindLineNum["find_workflow_line_number()"]
    AddOrigin["Add origin metadata"]
    
    WorkflowDef --> FindLineNum
    FindLineNum --> AddOrigin
    
    AddOrigin --> Preprocess["preprocess_matrix_jobs()"]
    
    Preprocess --> Validate["validate_tags()"]
    Validate --> SetDefaults["set_default_tags()"]
    SetDefaults --> Explode["explode_tags()"]
    Explode --> Canonicalize["canonicalize_tags()"]
    Canonicalize --> Derived["set_derived_tags()"]
    Derived --> ExplodeAgain["explode_tags()<br/>(for derived lists)"]
    
    ExplodeAgain --> FilterDirty{dirty_projects<br/>filter?}
    FilterDirty -->|Yes| ApplyFilter["Filter by project"]
    FilterDirty -->|No| Skip1["Skip"]
    
    ApplyFilter --> RemoveExcluded["remove_excluded_jobs()"]
    Skip1 --> RemoveExcluded
    
    RemoveExcluded --> Sort["Sort tags by importance"]
    
    Sort --> Result["Processed matrix_jobs list"]
```

**Diagram: Workflow Matrix Job Processing Pipeline**

Sources: [.github/actions/workflow-build/build-workflow.py:922-959](), [.github/actions/workflow-build/build-workflow.py:902-919]()

## Special Workflows

### Exclude Workflow

The `exclude` workflow defines patterns that should be removed from all other workflows. It uses the same matrix job format but:
- Does not require all required tags to be present
- Only explodes and canonicalizes (no validation, defaults, or derived tags)
- Is processed by `get_excluded_matrix_jobs()` and applied by `remove_excluded_jobs()`

```yaml
workflows:
  exclude:
    # Exclude gcc10 + CTK 12.0 combinations
    - cxx: gcc10
      ctk: "12.0"
```

### Override Workflow

The `override` workflow supersedes all other workflows when:
1. The `--allow-override` flag is passed to `build-workflow.py`
2. The `override` workflow exists and is non-empty

When activated, the system prints a notice and processes only the override workflow, ignoring the `--workflows` argument. This is useful for debugging specific configurations.

Sources: [.github/actions/workflow-build/build-workflow.py:748-808](), [.github/actions/workflow-build/build-workflow.py:1031-1038]()

## Additional Top-Level Fields

### devcontainer_version

String field specifying the version tag for devcontainer images. Used when generating image names in `generate_dispatch_job_image()`.

Example:
```yaml
devcontainer_version: "24.10"
```

This produces image names like `rapidsai/devcontainers:24.10-cpp-gcc12-cuda12.0`.

### all_stds

List of all C++ standards supported across the system. Used by `lookup_supported_stds()` to compute the intersection of standards supported by the CTK, host compiler, device compiler, and project.

Example:
```yaml
all_stds: [11, 14, 17, 20, 23]
```

Sources: [.github/actions/workflow-build/build-workflow.py:323-337](), [.github/actions/workflow-build/build-workflow.py:404-412]()

## Complete Matrix Job Structure

After preprocessing, a fully specified matrix job contains all resolved tags and derived metadata:

```mermaid
graph TB
    subgraph "Input Matrix Job"
        Input["project: libcudacxx<br/>jobs: [test]<br/>ctk: '12.0'<br/>cxx: gcc12<br/>std: 17<br/>gpu: t4<br/>sm: gpu"]
    end
    
    subgraph "Processing"
        Validate["validate_tags()"]
        SetDefaults["set_default_tags()"]
        Canonicalize["canonicalize_tags()"]
        SetDerived["set_derived_tags()"]
    end
    
    subgraph "Output Matrix Job"
        Output["project: 'libcudacxx'<br/>jobs: ['test']<br/>ctk: '12.0'<br/>cudacxx: 'nvcc'<br/>cxx: 'gcc12'<br/>std: 17<br/>cpu: 'amd64'<br/>gpu: 't4'<br/>sm: '75'<br/>origin: {...}"]
    end
    
    Input --> Validate
    Validate --> SetDefaults
    SetDefaults --> Canonicalize
    Canonicalize --> SetDerived
    SetDerived --> Output
```

**Diagram: Matrix Job Transformation Example**

| Tag | Input Value | Processing | Output Value |
|-----|-------------|------------|--------------|
| `project` | `libcudacxx` | Validated | `"libcudacxx"` |
| `jobs` | `[test]` | Validated | `["test"]` |
| `ctk` | `12.0` | Canonicalized | `"12.0"` |
| `cudacxx` | (not specified) | Default applied | `"nvcc"` |
| `cxx` | `gcc12` | Canonicalized | `"gcc12"` |
| `std` | `17` | Validated | `17` |
| `cpu` | (not specified) | Default applied | `"amd64"` |
| `gpu` | `t4` | Validated | `"t4"` |
| `sm` | `gpu` | Derived from gpu | `"75"` |
| `origin` | (not specified) | Added by system | `{filename, workflow_name, workflow_location, original_matrix_job}` |

The `origin` field contains metadata for error reporting and result aggregation:
- `filename`: Path to matrix.yaml
- `workflow_name`: Name of the workflow this job came from
- `workflow_location`: File path and line number
- `original_matrix_job`: JSON representation of the original input

Sources: [.github/actions/workflow-build/build-workflow.py:736-745](), [.github/actions/workflow-build/build-workflow.py:811-861]()

## Related Code Entities Reference

| Function | Purpose | File Location |
|----------|---------|---------------|
| `preprocess_matrix_yaml()` | Normalize version keys to strings | [.github/actions/workflow-build/build-workflow.py:1087-1101]() |
| `canonicalize_ctk_version()` | Resolve CTK version aliases | [.github/actions/workflow-build/build-workflow.py:113-123]() |
| `get_ctk()` | Retrieve CTK definition | [.github/actions/workflow-build/build-workflow.py:126-129]() |
| `parse_cxx_string()` | Parse compiler string into (id, version) | [.github/actions/workflow-build/build-workflow.py:133-135]() |
| `canonicalize_host_compiler_name()` | Normalize host compiler names | [.github/actions/workflow-build/build-workflow.py:139-172]() |
| `get_host_compiler()` | Retrieve host compiler definition | [.github/actions/workflow-build/build-workflow.py:176-201]() |
| `get_device_compiler()` | Retrieve device compiler definition | [.github/actions/workflow-build/build-workflow.py:204-223]() |
| `get_gpu()` | Retrieve GPU definition | [.github/actions/workflow-build/build-workflow.py:227-238]() |
| `get_project()` | Retrieve project definition | [.github/actions/workflow-build/build-workflow.py:242-256]() |
| `get_job_type_info()` | Retrieve job type definition | [.github/actions/workflow-build/build-workflow.py:260-281]() |
| `get_tag_info()` | Retrieve tag schema definition | [.github/actions/workflow-build/build-workflow.py:284-302]() |
| `get_all_matrix_job_tags_sorted()` | Get ordered list of all tags | [.github/actions/workflow-build/build-workflow.py:305-320]() |
| `lookup_supported_stds()` | Compute supported C++ standards | [.github/actions/workflow-build/build-workflow.py:323-337]() |
| `is_windows()` | Check if job targets Windows | [.github/actions/workflow-build/build-workflow.py:340-342]() |
| `validate_tags()` | Validate matrix job tags | [.github/actions/workflow-build/build-workflow.py:811-832]() |
| `set_default_tags()` | Apply default tag values | [.github/actions/workflow-build/build-workflow.py:834-842]() |
| `canonicalize_tags()` | Normalize tag values | [.github/actions/workflow-build/build-workflow.py:845-849]() |
| `set_derived_tags()` | Compute derived tag values | [.github/actions/workflow-build/build-workflow.py:852-875]() |
| `explode_tags()` | Expand list-valued tags | [.github/actions/workflow-build/build-workflow.py:886-899]() |
| `preprocess_matrix_jobs()` | Full preprocessing pipeline | [.github/actions/workflow-build/build-workflow.py:902-919]() |
| `parse_workflow_matrix_jobs()` | Parse and process workflow definition | [.github/actions/workflow-build/build-workflow.py:922-959]() |
| `get_excluded_matrix_jobs()` | Parse exclude workflow | [.github/actions/workflow-build/build-workflow.py:748-750]() |
| `remove_excluded_jobs()` | Apply exclusion rules | [.github/actions/workflow-build/build-workflow.py:796-808]() |

Sources: [.github/actions/workflow-build/build-workflow.py:1-1140]()

---

# Page: Tags and Parameters

# Tags and Parameters

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)

</details>



This page documents the tag system used to define job configurations in `matrix.yaml`. Tags are key-value parameters that specify build configurations such as projects, compilers, CUDA versions, and GPU architectures. The workflow generation system processes these tags through multiple stages of validation, canonicalization, and derivation to produce fully-specified job definitions.

For information about the overall structure of `matrix.yaml`, see [Matrix YAML Structure](#2.1). For information about excluding specific tag combinations, see [Exclusions and Filtering](#2.3).

## Tag Concepts

A **tag** is a configuration parameter that appears in a matrix job definition. Each tag has:
- An **ID**: the key name used in `matrix.yaml` (e.g., `ctk`, `cxx`, `std`)
- A **required** status: whether the tag must be present in every job
- A **default** value: optional value used when tag is omitted
- Validation rules and canonicalization logic

Tags are defined in the `tags` section of `matrix.yaml` and referenced in workflow job definitions.

**Sources:** [.github/actions/workflow-build/build-workflow.py:285-302]()

## Tag Definitions

The following table lists all standard tags recognized by the system:

| Tag ID | Description | Required | Default | Example Values |
|--------|-------------|----------|---------|----------------|
| `project` | Target project to build/test | Yes | - | `libcudacxx`, `cub`, `thrust` |
| `jobs` | Job types to execute | Yes | - | `build`, `test`, `[build, test]` |
| `ctk` | CUDA Toolkit version | Yes | - | `11.1`, `12.0`, `12.6` |
| `cudacxx` | Device compiler | No | `nvcc` | `nvcc`, `clang` |
| `cxx` | Host compiler | Yes | - | `gcc10`, `gcc-12`, `clang16` |
| `cpu` | CPU architecture | No | `amd64` | `amd64`, `arm64` |
| `gpu` | GPU architecture for testing | Conditional | - | `t4`, `v100`, `a100` |
| `std` | C++ standard(s) | No | - | `17`, `20`, `all` |
| `sm` | CUDA compute capability | No | - | `75`, `80-real`, `gpu` |
| `cmake_options` | Additional CMake flags | No | - | `-DCMAKE_BUILD_TYPE=Debug` |

**Sources:** [.github/actions/workflow-build/build-workflow.py:285-302]()

## Tag Processing Pipeline

Tags undergo a multi-stage transformation pipeline before becoming job specifications. The following diagram illustrates this pipeline:

```mermaid
graph TB
    Input["Raw Matrix Job<br/>from matrix.yaml"]
    Validate["validate_tags()<br/>Check required tags,<br/>validate known tags"]
    Defaults["set_default_tags()<br/>Fill optional tags<br/>with default values"]
    Explode1["explode_tags()<br/>Expand list values<br/>into multiple jobs"]
    Canonicalize["canonicalize_tags()<br/>Resolve aliases<br/>(gcc10, 11.1)"]
    Derived["set_derived_tags()<br/>Compute derived values<br/>(sm: gpu, std: all)"]
    Explode2["explode_tags()<br/>Explode any newly<br/>derived lists"]
    Filter["remove_excluded_jobs()<br/>Apply exclusion rules"]
    Output["Finalized Matrix Job"]
    
    Input --> Validate
    Validate --> Defaults
    Defaults --> Explode1
    Explode1 --> Canonicalize
    Canonicalize --> Derived
    Derived --> Explode2
    Explode2 --> Filter
    Filter --> Output
```

**Diagram: Tag Processing Pipeline in preprocess_matrix_jobs()**

**Sources:** [.github/actions/workflow-build/build-workflow.py:902-919](), [.github/actions/workflow-build/build-workflow.py:922-959]()

## Required vs Optional Tags

### Required Tags

Required tags must be present in every matrix job definition (unless excluded by context). Missing required tags cause validation errors.

```python
# From get_tag_info()
if 'required' not in result:
    result['required'] = False

if 'default' in result:
    result['required'] = False  # Tags with defaults are never required
```

Validation occurs in `validate_tags()`:

```python
for tag in all_tags:
    tag_info = get_tag_info(tag)
    if tag not in matrix_job:
        if tag_info['required']:
            raise Exception(f"Missing required tag '{tag}'")
```

**Special validation rules:**
- If `cudacxx: clang` is specified, `cxx` must also be `clang` (validated at [build-workflow.py:820-822]())
- The `gpu` tag is conditionally required when job types require GPU execution

**Sources:** [.github/actions/workflow-build/build-workflow.py:293-299](), [.github/actions/workflow-build/build-workflow.py:811-832]()

### Optional Tags

Optional tags may be omitted. The system handles them in two ways:

1. **Tags with defaults**: Automatically filled by `set_default_tags()`
2. **Tags without defaults**: Left undefined, job specification adapts accordingly

Example from `set_default_tags()`:

```python
for tag in all_tags:
    if tag in matrix_job:
        continue
    
    tag_info = get_tag_info(tag)
    if tag_info['default']:
        matrix_job[tag] = tag_info['default']
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:834-843]()

## Tag Canonicalization

Canonicalization resolves aliases and normalizes tag values to standard formats. This allows flexible input syntax while maintaining consistent internal representation.

```mermaid
graph LR
    subgraph "CTK Version Canonicalization"
        CTK1["Input: '11.1'"]
        CTK2["Input: 'latest'<br/>(aka for 12.6)"]
        CTKOut["Output: '11.1'<br/>or '12.6'"]
        
        CTK1 --> CTKOut
        CTK2 --> CTKOut
    end
    
    subgraph "Host Compiler Canonicalization"
        CXX1["Input: 'gcc'"]
        CXX2["Input: 'gcc10'"]
        CXX3["Input: 'gcc-12'"]
        CXXOut["Output: 'gcc13'<br/>(latest)<br/>or 'gcc10'<br/>or 'gcc12'"]
        
        CXX1 --> CXXOut
        CXX2 --> CXXOut
        CXX3 --> CXXOut
    end
```

**Diagram: Tag Canonicalization Examples**

### CTK Version Canonicalization

The `canonicalize_ctk_version()` function handles CTK versions and their aliases:

```python
@memoize_result
def canonicalize_ctk_version(ctk_string):
    if ctk_string in matrix_yaml['ctk_versions']:
        return ctk_string
    
    # Check for aka's:
    for ctk_key, ctk_value in matrix_yaml['ctk_versions'].items():
        if 'aka' in ctk_value and ctk_string == ctk_value['aka']:
            return ctk_key
    
    raise Exception(f"Unknown CTK version '{ctk_string}'")
```

**Example:** If `matrix.yaml` defines `12.6: {aka: "latest"}`, then specifying `ctk: latest` resolves to `ctk: 12.6`.

**Sources:** [.github/actions/workflow-build/build-workflow.py:113-123]()

### Host Compiler Canonicalization

The `canonicalize_host_compiler_name()` function normalizes compiler specifications:

**Input formats supported:**
- `gcc` → uses latest version defined in `matrix.yaml`
- `gcc10` → uses version 10
- `gcc-12` → normalizes to `gcc12`

**Output format:** Always `{compiler_id}{version}` (e.g., `gcc12`, `clang16`)

```python
@memoize_result
def canonicalize_host_compiler_name(cxx_string):
    id, version = parse_cxx_string(cxx_string)
    
    if not version:
        # Use latest version
        version = max(hc_def['versions'].keys(), 
                     key=lambda x: tuple(map(int, x.split('.'))))
    
    # Check for version aliases
    if not version in hc_def['versions']:
        for version_key, version_data in hc_def['versions'].items():
            if 'aka' in version_data and version == version_data['aka']:
                version = version_key
    
    return f"{id}{version}"
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:132-172]()

### Canonicalization Entry Point

The main `canonicalize_tags()` function applies canonicalization to relevant tags:

```python
def canonicalize_tags(matrix_job):
    if 'ctk' in matrix_job:
        matrix_job['ctk'] = canonicalize_ctk_version(matrix_job['ctk'])
    if 'cxx' in matrix_job:
        matrix_job['cxx'] = canonicalize_host_compiler_name(matrix_job['cxx'])
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:845-850]()

## Derived Tags

Derived tags are computed values based on other tags. The system supports two primary derived tags: `sm` and `std`.

```mermaid
graph TB
    subgraph "Derived Tag: sm"
        SM_Input["sm: 'gpu'"]
        GPU_Tag["gpu: 't4'"]
        GPU_Lookup["get_gpu('t4')<br/>returns sm: '75'"]
        SM_Output["sm: '75'"]
        
        SM_Input --> GPU_Lookup
        GPU_Tag --> GPU_Lookup
        GPU_Lookup --> SM_Output
    end
    
    subgraph "Derived Tag: std"
        STD_Input["std: 'all'"]
        Context["ctk: '12.0'<br/>cxx: 'gcc12'<br/>project: 'libcudacxx'"]
        STD_Lookup["lookup_supported_stds()<br/>Intersect all stds"]
        STD_Output["std: [17, 20, 23]"]
        
        STD_Input --> STD_Lookup
        Context --> STD_Lookup
        STD_Lookup --> STD_Output
    end
```

**Diagram: Derived Tag Resolution**

### Derived SM (Compute Capability)

When `sm: gpu` is specified, the SM architecture is derived from the `gpu` tag:

```python
def set_derived_tags(matrix_job):
    if 'sm' in matrix_job and matrix_job['sm'] == 'gpu':
        if not 'gpu' in matrix_job:
            raise Exception("\"sm: 'gpu'\" requires tag 'gpu'.")
        gpu = get_gpu(matrix_job['gpu'])
        matrix_job['sm'] = gpu['sm']  # e.g., '75' for T4
```

**Example transformation:**
```yaml
# Input
gpu: t4
sm: gpu

# Output (after derivation)
gpu: t4
sm: 75
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:853-857]()

### Derived std (C++ Standard)

When `std: all` is specified, the system computes the intersection of supported standards across all relevant components:

```python
def lookup_supported_stds(matrix_job):
    stds = set(matrix_yaml['all_stds'])
    if 'ctk' in matrix_job:
        ctk = get_ctk(matrix_job['ctk'])
        stds = stds & set(ctk['stds'])
    if 'cxx' in matrix_job:
        host_compiler = get_host_compiler(matrix_job['cxx'])
        stds = stds & set(host_compiler['stds'])
    if 'cudacxx' in matrix_job:
        device_compiler = get_device_compiler(matrix_job)
        stds = stds & set(device_compiler['stds'])
    if 'project' in matrix_job:
        project = get_project(matrix_job['project'])
        stds = stds & set(project['stds'])
    return sorted(list(stds))
```

**Intersection logic:**
1. Start with all possible C++ standards
2. Intersect with CTK supported standards
3. Intersect with host compiler supported standards
4. Intersect with device compiler supported standards
5. Intersect with project-specific standards

**Example:**
```yaml
# Input
project: libcudacxx
ctk: 11.8
cxx: gcc10
std: all

# Output (after derivation)
project: libcudacxx
ctk: 11.8
cxx: gcc10
std: [17, 20]  # Intersection result
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:323-337](), [.github/actions/workflow-build/build-workflow.py:859-860]()

### Job Dependency Resolution

Derived tags also handle job dependencies. When a job type declares dependencies via the `needs` field, those dependencies are automatically added to the `jobs` list:

```python
# Add all deps before applying project job maps:
for job in matrix_job['jobs']:
    job_info = get_job_type_info(job)
    dep = job_info['needs']
    if dep and dep not in matrix_job['jobs']:
        matrix_job['jobs'].append(dep)
```

**Example:**
```yaml
# Input
jobs: [test]

# If test job needs build (from job definitions)
# Output (after derivation)
jobs: [test, build]
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:863-867]()

### Project Job Mapping

Projects can define job expansions via the `job_map` configuration. This allows project-specific job types to expand into multiple concrete jobs:

```python
# Apply project job map:
project = get_project(matrix_job['project'])
for original_job, expanded_jobs in project['job_map'].items():
    if original_job in matrix_job['jobs']:
        matrix_job['jobs'].remove(original_job)
        matrix_job['jobs'] += expanded_jobs
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:869-874]()

## Tag Explosion

Tag explosion converts list-valued tags into multiple distinct jobs. This enables concise matrix definitions that generate many configurations.

```mermaid
graph TB
    Input["Input Matrix Job:<br/>{project: 'cub',<br/>std: [17, 20],<br/>gpu: ['t4', 'v100']}"]
    
    ExplodeStd["Explode 'std' tag"]
    Job1["Job 1:<br/>{project: 'cub',<br/>std: 17,<br/>gpu: ['t4', 'v100']}"]
    Job2["Job 2:<br/>{project: 'cub',<br/>std: 20,<br/>gpu: ['t4', 'v100']}"]
    
    ExplodeGpu1["Explode 'gpu' in Job 1"]
    ExplodeGpu2["Explode 'gpu' in Job 2"]
    
    Output1["Output 1:<br/>{project: 'cub',<br/>std: 17,<br/>gpu: 't4'}"]
    Output2["Output 2:<br/>{project: 'cub',<br/>std: 17,<br/>gpu: 'v100'}"]
    Output3["Output 3:<br/>{project: 'cub',<br/>std: 20,<br/>gpu: 't4'}"]
    Output4["Output 4:<br/>{project: 'cub',<br/>std: 20,<br/>gpu: 'v100'}"]
    
    Input --> ExplodeStd
    ExplodeStd --> Job1
    ExplodeStd --> Job2
    Job1 --> ExplodeGpu1
    Job2 --> ExplodeGpu2
    ExplodeGpu1 --> Output1
    ExplodeGpu1 --> Output2
    ExplodeGpu2 --> Output3
    ExplodeGpu2 --> Output4
```

**Diagram: Tag Explosion Creating Cartesian Product**

### Explosion Algorithm

The `explode_tags()` function recursively expands list-valued tags:

```python
def explode_tags(matrix_job, explode_tag=None):
    if not explode_tag:
        explode_tag = next_explode_tag(matrix_job)
    
    if not explode_tag:
        return [matrix_job]  # No more lists to explode
    
    result = []
    for value in matrix_job[explode_tag]:
        new_job = copy.deepcopy(matrix_job)
        new_job[explode_tag] = value
        result.extend(explode_tags(new_job))  # Recursive
    
    return result
```

**Key characteristics:**
- Recursive: Explodes one tag, then recursively explodes remaining lists
- Cartesian product: Generates all combinations of list values
- Deep copy: Each output job is independent

**Sources:** [.github/actions/workflow-build/build-workflow.py:886-899]()

### Non-Exploded Tags

Certain tags are intentionally kept as lists to optimize GitHub Actions scheduling:

```python
def next_explode_tag(matrix_job):
    non_exploded_tags = ['jobs']
    
    for tag in matrix_job:
        if not tag in non_exploded_tags and isinstance(matrix_job[tag], list):
            return tag
    return None
```

The `jobs` tag remains as a list because it's processed differently during dispatch group generation, where producer/consumer relationships are analyzed.

**Sources:** [.github/actions/workflow-build/build-workflow.py:877-883]()

### Multiple Explosion Passes

The pipeline performs explosion twice:

1. **First pass**: After setting defaults, before canonicalization ([build-workflow.py:914]())
2. **Second pass**: After setting derived tags ([build-workflow.py:918]())

This two-pass approach is necessary because derived tags like `std: all` may produce lists that need explosion:

```yaml
# Input
std: all

# After derivation (becomes a list)
std: [17, 20, 23]

# After second explosion (three jobs)
Job 1: std: 17
Job 2: std: 20
Job 3: std: 23
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:902-919]()

## Tag Sorting

After all transformations, tags are sorted by "importance" for consistent output formatting:

```python
@static_result
def get_all_matrix_job_tags_sorted():
    all_tags = set(matrix_yaml['tags'].keys())
    
    # Always first, information dense:
    sorted_important_tags = ['project', 'jobs', 'cudacxx', 'cxx', 
                             'ctk', 'gpu', 'std', 'sm', 'cpu']
    
    # Always last, derived:
    sorted_noise_tags = ['origin']
    
    # In between: alphabetical
    sorted_tags = set(sorted_important_tags + sorted_noise_tags)
    sorted_meh_tags = sorted(list(all_tags - sorted_tags))
    
    return sorted_important_tags + sorted_meh_tags + sorted_noise_tags
```

This ensures that critical identifying information appears first when inspecting job definitions.

**Sources:** [.github/actions/workflow-build/build-workflow.py:305-320](), [.github/actions/workflow-build/build-workflow.py:956-957]()

## Complete Tag Processing Example

The following table shows a concrete example of a matrix job progressing through the entire tag pipeline:

| Stage | Input/Output |
|-------|--------------|
| **Raw Input** | `{project: "cub", ctk: "latest", cxx: "gcc", std: "all", gpu: "t4", sm: "gpu"}` |
| **After Validation** | ✓ All required tags present |
| **After Set Defaults** | `{project: "cub", ctk: "latest", cxx: "gcc", std: "all", gpu: "t4", sm: "gpu", cudacxx: "nvcc", cpu: "amd64"}` |
| **After First Explosion** | (No lists yet) |
| **After Canonicalization** | `{project: "cub", ctk: "12.6", cxx: "gcc13", std: "all", gpu: "t4", sm: "gpu", cudacxx: "nvcc", cpu: "amd64"}` |
| **After Derived Tags** | `{project: "cub", ctk: "12.6", cxx: "gcc13", std: [17, 20, 23], gpu: "t4", sm: "75", cudacxx: "nvcc", cpu: "amd64"}` |
| **After Second Explosion** | Three jobs: same as above with `std: 17`, `std: 20`, `std: 23` |
| **After Exclusions** | (Assume no exclusions match) |
| **Final Output** | Three complete, finalized matrix jobs ready for dispatch group generation |

**Sources:** [.github/actions/workflow-build/build-workflow.py:902-959]()

## Tag Origin Tracking

Each matrix job carries an `origin` tag that tracks provenance for error reporting and result aggregation:

```python
def get_matrix_job_origin(matrix_job, workflow_name, workflow_location):
    filename = matrix_yaml['filename']
    original_matrix_job = json.dumps(matrix_job, indent=None, separators=(', ', ': '))
    original_matrix_job = original_matrix_job.replace('"', '')
    return {
        'filename': filename,
        'workflow_name': workflow_name,
        'workflow_location': workflow_location,
        'original_matrix_job': original_matrix_job
    }
```

The `origin` tag includes:
- **filename**: Path to `matrix.yaml`
- **workflow_name**: Source workflow (e.g., `pull_request`, `nightly`)
- **workflow_location**: File path and line number
- **original_matrix_job**: The unexpanded job definition as written

This information is preserved through all transformations and included in job dispatch specifications for debugging and results reporting.

**Sources:** [.github/actions/workflow-build/build-workflow.py:736-745](), [.github/actions/workflow-build/build-workflow.py:938-942]()

---

# Page: Exclusions and Filtering

# Exclusions and Filtering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)

</details>



This document describes how to exclude specific job combinations from workflows and filter jobs based on changed files. These mechanisms reduce CI compute costs by preventing invalid configurations from executing and skipping unaffected projects.

For information about the overall matrix configuration structure, see [Matrix YAML Structure](#2.1). For details on the workflow generation pipeline where these filters are applied, see [build-workflow.py Pipeline](#3.1).

## Overview

The cccl-gha system provides two filtering mechanisms:

1. **Exclusions**: Declarative rules in `matrix.yaml` that remove invalid or unsupported job combinations (e.g., incompatible compiler versions with specific CUDA toolkits)
2. **Dirty Projects Filtering**: Dynamic filtering based on git diff analysis that runs only jobs for projects affected by code changes

Both filters are applied during the workflow generation phase, before jobs are dispatched to runners.

## Exclusion System

### Defining Exclusions

Exclusions are defined in a special `exclude` workflow within `matrix.yaml`. This workflow uses the same syntax as regular workflows but is never executed directly—it serves solely as a filter definition.

**Sources:** [.github/actions/workflow-build/build-workflow.py:748-750](), [.github/actions/workflow-build/build-workflow.py:922-929]()

**Example Exclusion Matrix:**

```yaml
workflows:
  exclude:
    - {ctk: '11.1', cxx: gcc13}  # GCC 13 not supported with CTK 11.1
    - {cudacxx: clang, gpu: v100}  # Clang CUDA incompatible with V100
    - {project: thrust, std: 11}  # Thrust requires C++14 minimum
```

### Exclusion Matching Logic

The exclusion matching algorithm evaluates each matrix job against all exclusion rules. A job is excluded if **all tags** specified in an exclusion rule match the job's corresponding tag values.

**Title: Exclusion Matching Decision Flow**

```mermaid
graph TB
    Job["Matrix Job"]
    Exclusions["Exclusion Rules<br/>from 'exclude' workflow"]
    
    Job --> Loop["For each exclusion rule"]
    Exclusions --> Loop
    
    Loop --> CheckTags["Check all exclusion tags<br/>against job tags"]
    
    CheckTags --> TagMissing{"Exclusion tag<br/>not in job?"}
    TagMissing -->|Yes| NoMatch["No match - job survives"]
    TagMissing -->|No| CheckValues
    
    CheckValues{"All exclusion<br/>values match<br/>job values?"}
    CheckValues -->|No| NoMatch
    CheckValues -->|Yes| Complete{"Complete match<br/>or partial?"}
    
    Complete -->|Partial| PartialMatch["Remove matched values<br/>from job tag"]
    Complete -->|Complete| FullMatch["Exclude job entirely"]
    
    PartialMatch --> NextRule["Check next exclusion"]
    NoMatch --> NextRule
    FullMatch --> Excluded["Job excluded"]
    NextRule --> MoreRules{"More<br/>exclusions?"}
    MoreRules -->|Yes| Loop
    MoreRules -->|No| Survive["Job survives"]
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:753-793](), [.github/actions/workflow-build/build-workflow.py:796-808]()

### Matching Rules

| Condition | Behavior | Example |
|-----------|----------|---------|
| Exclusion tag not present in job | No match—job not affected | Exclusion `{ctk: 11.1}` does not affect jobs without `ctk` tag |
| No exclusion values match job values | No match—job not affected | Exclusion `{cxx: gcc10}` does not affect `{cxx: gcc11}` |
| Partial match (some values match) | Remove matched values from list | Job `{std: [11, 14, 17]}` with exclusion `{std: 11}` becomes `{std: [14, 17]}` |
| Complete match (all values match) | Exclude job entirely | Job `{ctk: 11.1, cxx: gcc10}` fully matches exclusion `{ctk: 11.1, cxx: gcc10}` |

**Sources:** [.github/actions/workflow-build/build-workflow.py:753-793]()

### Partial Exclusions

The exclusion system supports **partial matches** for tags with list values. This is particularly useful for the `jobs` tag, which often contains multiple job types. If only some values in a list match the exclusion, those values are removed while preserving the rest.

**Example:**

```yaml
# Matrix job definition
- project: libcudacxx
  jobs: [build, test, benchmark]
  ctk: 11.1
  cxx: gcc10

# Exclusion rule
- project: libcudacxx
  jobs: benchmark
  ctk: 11.1
```

**Result:** The job survives with `jobs: [build, test]`—only `benchmark` is removed.

**Sources:** [.github/actions/workflow-build/build-workflow.py:777-791]()

### Processing Pipeline Integration

Exclusions are applied after tag explosion and canonicalization but before dispatch group generation:

**Title: Exclusion Application in Processing Pipeline**

```mermaid
graph LR
    Input["matrix.yaml<br/>workflow definitions"]
    
    Parse["parse_workflow_matrix_jobs()"]
    Validate["validate_tags()"]
    Defaults["set_default_tags()"]
    Explode1["explode_tags()"]
    Canon["canonicalize_tags()"]
    Derived["set_derived_tags()"]
    Explode2["explode_tags()<br/>(derived tags)"]
    
    Exclude["remove_excluded_jobs()"]
    GetExcluded["get_excluded_matrix_jobs()"]
    ApplyExclusion["apply_matrix_job_exclusion()"]
    
    Dispatch["matrix_job_to_dispatch_group()"]
    
    Input --> Parse
    Parse --> Validate
    Validate --> Defaults
    Defaults --> Explode1
    Explode1 --> Canon
    Canon --> Derived
    Derived --> Explode2
    
    Explode2 --> Exclude
    GetExcluded --> Exclude
    Exclude --> ApplyExclusion
    ApplyExclusion --> Dispatch
    
    style Exclude fill:#ffe6e6
    style GetExcluded fill:#ffe6e6
    style ApplyExclusion fill:#ffe6e6
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:902-919](), [.github/actions/workflow-build/build-workflow.py:922-959]()

## Change-Based Filtering (Dirty Projects)

### Overview

Change-based filtering reduces CI costs on pull requests by running only jobs for projects affected by code changes. This is implemented through an optional `inspect_changes_script` that performs git diff analysis.

**Sources:** [.github/actions/workflow-build/action.yml:12-19](), [.github/actions/workflow-build/action.yml:61-72]()

### Configuration

The `workflow-build` action accepts the following inputs for change detection:

| Input | Description | Required |
|-------|-------------|----------|
| `inspect_changes_script` | Path to script that outputs `dirty_projects` | No |
| `inspect_changes_base_sha` | Base git ref for diff comparison (e.g., `origin/main`) | No |

**Example Action Usage:**

```yaml
- uses: ./.github/actions/workflow-build
  with:
    workflows: pull_request
    inspect_changes_script: ./ci/inspect_changes.sh
    inspect_changes_base_sha: ${{ github.event.pull_request.base.sha }}
```

**Sources:** [.github/actions/workflow-build/action.yml:12-19]()

### Inspect Changes Script Requirements

The script must:
1. Accept two arguments: `base_sha` and `head_sha`
2. Perform git diff analysis between these refs
3. Output a `dirty_projects` variable to `GITHUB_OUTPUT`

**Example Output Format:**

```bash
# Script writes to GITHUB_OUTPUT:
dirty_projects=libcudacxx thrust
```

This indicates that only jobs with `project: libcudacxx` or `project: thrust` should execute.

**Sources:** [.github/actions/workflow-build/action.yml:61-72]()

### Integration with Workflow Generation

**Title: Dirty Projects Filtering Data Flow**

```mermaid
graph TB
    subgraph "GitHub Actions Context"
        EventData["Pull Request Event<br/>base.sha / head.sha"]
    end
    
    subgraph "Inspect Changes Step"
        Script["inspect_changes_script"]
        GitDiff["git diff analysis"]
        Output["GITHUB_OUTPUT<br/>dirty_projects"]
        
        EventData --> Script
        Script --> GitDiff
        GitDiff --> Output
    end
    
    subgraph "Build Workflow Step"
        BuildPy["build-workflow.py"]
        Args["--dirty-projects<br/>libcudacxx thrust"]
        Filter["Filter jobs where<br/>job['project'] in dirty_projects"]
        
        Output --> Args
        Args --> BuildPy
        BuildPy --> Filter
    end
    
    subgraph "Result"
        Filtered["Filtered matrix_jobs<br/>only affected projects"]
    end
    
    Filter --> Filtered
```

**Sources:** [.github/actions/workflow-build/action.yml:61-72](), [.github/actions/workflow-build/action.yml:74-88]()

### Filtering Implementation

The dirty projects filter is applied in `parse_workflow_matrix_jobs()` after tag preprocessing but before exclusion removal:

```python
# build-workflow.py:947-949
if args.dirty_projects != None:  # Explicitly check for None
    matrix_jobs = [job for job in matrix_jobs if job['project'] in args.dirty_projects]
```

**Key Points:**
- Checks explicitly for `None` to distinguish between "no filtering" and "empty list" (no projects changed)
- Simple list comprehension filter on the `project` tag
- Applied after tag explosion/canonicalization, so all jobs have a single `project` value
- Occurs **before** exclusion removal to avoid wasted computation

**Sources:** [.github/actions/workflow-build/build-workflow.py:947-949]()

### Empty Dirty Projects Behavior

If `dirty_projects` is an empty list (no relevant files changed), all jobs are filtered out:

```yaml
# No jobs generated → workflows skip entirely
workflow.json: {}
```

This results in no dispatch jobs and zero runner allocation, maximizing cost savings.

**Sources:** [.github/actions/workflow-build/build-workflow.py:947-949]()

## Combined Filtering Pipeline

**Title: Complete Filtering Pipeline**

```mermaid
graph TB
    Start["Input: matrix.yaml<br/>workflow definitions"]
    
    subgraph "Optional: Change Detection"
        InspectScript["inspect_changes_script<br/>runs git diff"]
        DirtyOut["Output: dirty_projects list"]
        InspectScript --> DirtyOut
    end
    
    subgraph "Workflow Parsing: parse_workflow_matrix_jobs()"
        Preprocess["preprocess_matrix_jobs()<br/>- validate_tags()<br/>- set_default_tags()<br/>- explode_tags()<br/>- canonicalize_tags()<br/>- set_derived_tags()"]
        
        DirtyFilter["Dirty Projects Filter<br/>job['project'] in dirty_projects"]
        
        ExcludeFilter["remove_excluded_jobs()<br/>- get_excluded_matrix_jobs()<br/>- apply_matrix_job_exclusion()"]
        
        Sort["Sort tags by importance"]
    end
    
    Output["Output: Filtered matrix_jobs"]
    
    Start --> Preprocess
    DirtyOut -.->|if provided| DirtyFilter
    Preprocess --> DirtyFilter
    DirtyFilter --> ExcludeFilter
    ExcludeFilter --> Sort
    Sort --> Output
    
    style DirtyFilter fill:#e6f3ff
    style ExcludeFilter fill:#ffe6e6
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:922-959]()

## Processing Order Rationale

The filtering pipeline applies filters in this specific order:

1. **Tag preprocessing** (validation, defaults, explosion, canonicalization)
2. **Dirty projects filter** (if enabled)
3. **Exclusion removal**
4. **Tag sorting**

**Rationale:**

| Step | Reason for Placement |
|------|---------------------|
| Preprocessing first | Ensures all tags are standardized before filtering logic runs |
| Dirty projects before exclusions | Avoids computing exclusions for jobs that will be filtered anyway—performance optimization |
| Exclusions before sorting | Sorting is cosmetic and should operate on final job set |

**Sources:** [.github/actions/workflow-build/build-workflow.py:902-959]()

## Exclusion Tag Validation

The exclusion workflow supports **partial tag validation**—exclusion rules do not need to specify all required tags. This is implemented via the `ignore_required` parameter:

```python
# build-workflow.py:811-829
def validate_tags(matrix_job, ignore_required=False):
    if not ignore_required:
        for tag in all_tags:
            tag_info = get_tag_info(tag)
            if tag not in matrix_job:
                if tag_info['required']:
                    raise Exception(f"Missing required tag '{tag}'")
```

When processing the `exclude` workflow:

```python
# build-workflow.py:902-909
if is_exclusion_matrix:
    for matrix_job in matrix_jobs:
        validate_tags(matrix_job, ignore_required=True)  # Skip required check
        for job in explode_tags(matrix_job):
            canonicalize_tags(job)
```

This allows exclusions like `{ctk: 11.1}` without specifying `project`, `cxx`, etc.

**Sources:** [.github/actions/workflow-build/build-workflow.py:811-829](), [.github/actions/workflow-build/build-workflow.py:902-919]()

## Error Reporting

Exclusion matching failures are reported with context through the `error_message_with_matrix_job()` function:

```python
# build-workflow.py:109-110
def error_message_with_matrix_job(matrix_job, message):
    return f"{matrix_job['origin']['workflow_location']}: {message}\n  Input: {matrix_job['origin']['original_matrix_job']}"
```

This provides:
- File name and line number where the job was defined
- Original job specification before preprocessing
- Specific error message

**Example Error:**

```
ci/matrix.yaml:42 (job 3): "sm: 'gpu'" requires tag 'gpu'.
  Input: {project: thrust, ctk: 11.1, cxx: gcc10, sm: gpu}
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:109-110]()

## Summary

| Feature | Purpose | Implementation |
|---------|---------|----------------|
| **Exclusions** | Remove invalid job combinations | `exclude` workflow in `matrix.yaml` + `remove_excluded_jobs()` |
| **Partial Exclusions** | Remove specific values from list tags | `apply_matrix_job_exclusion()` with update_dict logic |
| **Dirty Projects** | Run only affected projects on PRs | `inspect_changes_script` + `--dirty-projects` flag |
| **Processing Order** | Optimize performance | Dirty filter before exclusions to reduce computation |

Both filtering mechanisms reduce CI costs: exclusions prevent invalid configurations from ever being generated, while dirty projects filtering adapts to code changes dynamically. Together, they ensure only necessary, valid jobs execute.

**Sources:** [.github/actions/workflow-build/build-workflow.py:753-808](), [.github/actions/workflow-build/build-workflow.py:922-959](), [.github/actions/workflow-build/action.yml:12-19](), [.github/actions/workflow-build/action.yml:61-88]()

---

# Page: Workflow Generation

# Workflow Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)
- [.github/actions/workflow-build/prepare-workflow-dispatch.py](.github/actions/workflow-build/prepare-workflow-dispatch.py)

</details>



## Purpose and Scope

This document describes the workflow generation pipeline, which transforms a declarative configuration file (`matrix.yaml`) into dispatchable job definitions that can be executed by GitHub Actions workflows. The generation system parses, validates, expands, and organizes job definitions, producing structured JSON outputs optimized for parallel execution.

For information about configuring `matrix.yaml`, see [Configuration Guide](#2). For information about how generated jobs are dispatched and executed, see [Job Dispatch](#4) and [Job Execution](#5).

---

## Generation Pipeline Overview

The workflow generation system operates in two main phases: **job processing** (`build-workflow.py`) and **dispatch preparation** (`prepare-workflow-dispatch.py`), orchestrated by the `workflow-build` composite action.

**Pipeline Flow Diagram**

```mermaid
graph LR
    A["matrix.yaml"] --> B["build-workflow.py"]
    B --> C["workflow.json"]
    C --> D["prepare-workflow-dispatch.py"]
    D --> E["dispatch.json"]
    
    B --> F["job_ids.json"]
    B --> G["runner_summary.json"]
    B --> H["job_list.txt"]
    
    I["inspect-changes"] -.-> B
    J["--workflows flag"] --> B
    K["--dirty-projects"] -.-> B
```

The pipeline accepts a `matrix.yaml` configuration and optional filtering parameters, producing multiple output artifacts that describe the complete set of jobs to execute.

**Sources:** [.github/actions/workflow-build/action.yml:1-140](), [.github/actions/workflow-build/build-workflow.py:1-1140](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:1-96]()

---

## Input Processing

### Matrix YAML Loading

The `build-workflow.py` script loads and preprocesses the matrix configuration file:

```mermaid
graph TB
    A["Load matrix.yaml"] --> B["preprocess_matrix_yaml()"]
    B --> C["Convert CTK versions to strings"]
    B --> D["Convert compiler versions to strings"]
    C --> E["Store as global matrix_yaml"]
    D --> E
```

The preprocessing ensures all version numbers are consistently represented as strings, regardless of whether they were specified as numbers or strings in YAML.

**Key Functions:**
- `preprocess_matrix_yaml()` [.github/actions/workflow-build/build-workflow.py:1087-1101](): Normalizes version numbers to strings
- `main()` [.github/actions/workflow-build/build-workflow.py:1104-1139](): Entry point that loads the YAML file

**Sources:** [.github/actions/workflow-build/build-workflow.py:1087-1139]()

### Command-Line Arguments

The `workflow-build` action accepts several inputs that control generation:

| Input | Purpose | Passed to build-workflow.py as |
|-------|---------|-------------------------------|
| `workflows` | Space-separated list of workflow names (e.g., `pull_request nightly`) | `--workflows` |
| `allow_override` | If true, use `override` workflow when present | `--allow-override` |
| `inspect_changes_script` | Script to determine changed projects | Results in `--dirty-projects` |
| `matrix_file` | Path to matrix.yaml | Positional argument |

**Sources:** [.github/actions/workflow-build/action.yml:4-36](), [.github/actions/workflow-build/build-workflow.py:1105-1116]()

---

## Processing Stages

The `build-workflow.py` script transforms matrix jobs through multiple stages. Each stage operates on a list of matrix job objects.

### Stage 1: Validation

```mermaid
graph LR
    A["Matrix Job"] --> B["validate_tags()"]
    B --> C{All required<br/>tags present?}
    C -->|No| D["Error: Missing required tag"]
    C -->|Yes| E{All tags<br/>recognized?}
    E -->|No| F["Error: Unknown tag"]
    E -->|Yes| G["Validated Job"]
```

The `validate_tags()` function ensures each matrix job contains all required tags and no unrecognized tags:

- Checks for required tags: tags with `required: true` in the tags schema
- Validates tag names against known tags from `matrix_yaml['tags']`
- Special validation: if `cudacxx: clang`, requires `cxx` to contain `clang`

**Key Functions:**
- `validate_tags()` [.github/actions/workflow-build/build-workflow.py:811-832]()
- `get_tag_info()` [.github/actions/workflow-build/build-workflow.py:284-302]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:811-832](), [.github/actions/workflow-build/build-workflow.py:284-302]()

### Stage 2: Default Assignment

Tags with default values are populated if not specified:

```python
# Example: If 'cpu' tag has default: 'amd64', and job doesn't specify cpu:
# Input:  {'project': 'libcudacxx', 'ctk': '11.1'}
# Output: {'project': 'libcudacxx', 'ctk': '11.1', 'cpu': 'amd64'}
```

**Key Functions:**
- `set_default_tags()` [.github/actions/workflow-build/build-workflow.py:834-843]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:834-843]()

### Stage 3: Tag Explosion

Tags specified as lists are "exploded" into multiple jobs, one per value:

```mermaid
graph TB
    A["Input: {project: libcudacxx, std: [17, 20]}"] --> B["explode_tags()"]
    B --> C["Output 1: {project: libcudacxx, std: 17}"]
    B --> D["Output 2: {project: libcudacxx, std: 20}"]
```

The explosion process is recursive and handles multiple list-valued tags:

**Key Functions:**
- `explode_tags()` [.github/actions/workflow-build/build-workflow.py:886-899](): Recursively explodes list-valued tags
- `next_explode_tag()` [.github/actions/workflow-build/build-workflow.py:877-883](): Identifies next tag to explode (skips `jobs` tag)

**Exception:** The `jobs` tag is intentionally left unexploded to optimize dispatch scheduling [.github/actions/workflow-build/build-workflow.py:878]().

**Sources:** [.github/actions/workflow-build/build-workflow.py:877-899]()

### Stage 4: Canonicalization

Host compiler and CUDA toolkit version strings are normalized to canonical forms:

| Input Format | Canonical Output | Example |
|--------------|------------------|---------|
| `gcc` | `gccX` (latest version) | `gcc13` |
| `gcc-12` | `gccX` | `gcc12` |
| `gcc12` | `gccX` | `gcc12` |
| CTK aka | Version string | `current` → `12.5` |

```mermaid
graph LR
    A["gcc-12"] --> B["parse_cxx_string()"]
    B --> C["('gcc', '12')"]
    C --> D["canonicalize_host_compiler_name()"]
    D --> E["gcc12"]
```

**Key Functions:**
- `canonicalize_tags()` [.github/actions/workflow-build/build-workflow.py:845-850]()
- `canonicalize_ctk_version()` [.github/actions/workflow-build/build-workflow.py:113-123]()
- `canonicalize_host_compiler_name()` [.github/actions/workflow-build/build-workflow.py:138-172]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:113-172](), [.github/actions/workflow-build/build-workflow.py:845-850]()

### Stage 5: Derived Tags

Certain tag values are computed from other tags:

**SM Architecture Derivation:**
```python
# If sm: 'gpu', derive from gpu tag
# Input:  {'gpu': 't4', 'sm': 'gpu'}
# Output: {'gpu': 't4', 'sm': '75'}  # T4's SM architecture
```

**Standard Expansion:**
```python
# If std: 'all', compute supported standards from project/compiler/CTK
# Input:  {'std': 'all', 'ctk': '11.1', 'cxx': 'gcc12'}
# Output: {'std': [11, 14, 17, 20]}  # intersection of supported stds
```

**Dependency Resolution:**
```python
# If job type has 'needs' dependency, add producer to jobs list
# Input:  {'jobs': ['test']}  # test job needs 'build'
# Output: {'jobs': ['test', 'build']}
```

**Project Job Mapping:**
```python
# Apply project-specific job expansions
# If project has job_map: {'verify': ['verify_headers', 'verify_codegen']}
# Input:  {'jobs': ['verify']}
# Output: {'jobs': ['verify_headers', 'verify_codegen']}
```

**Key Functions:**
- `set_derived_tags()` [.github/actions/workflow-build/build-workflow.py:852-875]()
- `lookup_supported_stds()` [.github/actions/workflow-build/build-workflow.py:323-337]()
- `get_gpu()` [.github/actions/workflow-build/build-workflow.py:226-238]()

**Note:** After derived tags are set, the job may need to be exploded again if derived tags introduced new list values.

**Sources:** [.github/actions/workflow-build/build-workflow.py:852-875](), [.github/actions/workflow-build/build-workflow.py:323-337]()

### Stage 6: Exclusion Application

Jobs matching exclusion patterns are filtered out or have specific tag values removed:

```mermaid
graph TB
    A["Matrix Job"] --> B["For each exclusion pattern"]
    B --> C{All exclusion tags<br/>match job?}
    C -->|No| D["Keep job as-is"]
    C -->|Yes| E{Complete match<br/>or partial?}
    E -->|Complete| F["Remove job entirely"]
    E -->|Partial| G["Remove matched tag values"]
```

**Exclusion Matching Logic:**

An exclusion is a matrix job that specifies tag values to exclude. A job is excluded if **all** tags in the exclusion pattern match values in the job:

```python
# Exclusion: {'ctk': '11.1', 'cxx': 'gcc13'}
# Job 1: {'ctk': '11.1', 'cxx': 'gcc13', 'std': 17}  → EXCLUDED (all tags match)
# Job 2: {'ctk': '11.1', 'cxx': 'gcc12', 'std': 17}  → KEPT (cxx doesn't match)
```

**Partial Exclusions:**

If a job tag is a list and only some values match the exclusion, those values are removed:

```python
# Exclusion: {'ctk': '11.1', 'std': [17, 20]}
# Input:  {'ctk': '11.1', 'std': [17, 20, 23]}
# Output: {'ctk': '11.1', 'std': [23]}  # 17 and 20 removed
```

**Key Functions:**
- `remove_excluded_jobs()` [.github/actions/workflow-build/build-workflow.py:796-808]()
- `apply_matrix_job_exclusion()` [.github/actions/workflow-build/build-workflow.py:753-793]()
- `get_excluded_matrix_jobs()` [.github/actions/workflow-build/build-workflow.py:748-750]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:748-808]()

### Complete Processing Pipeline

The `preprocess_matrix_jobs()` function orchestrates these stages:

```mermaid
graph TB
    A["Raw Matrix Jobs"] --> B["validate_tags()"]
    B --> C["set_default_tags()"]
    C --> D["explode_tags()"]
    D --> E["canonicalize_tags()"]
    E --> F["set_derived_tags()"]
    F --> G["explode_tags() again"]
    G --> H["Fully Processed Jobs"]
    
    I["remove_excluded_jobs()"] --> J["Filtered Jobs"]
    H --> I
```

**Key Functions:**
- `preprocess_matrix_jobs()` [.github/actions/workflow-build/build-workflow.py:902-919]()
- `parse_workflow_matrix_jobs()` [.github/actions/workflow-build/build-workflow.py:922-959]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:902-959]()

---

## Dispatch Group Generation

After processing, matrix jobs are converted into dispatch groups. Each group represents a logical collection of related jobs (e.g., "libcudacxx CTK11.1 nvcc gcc12").

### Matrix Job to Dispatch Jobs

```mermaid
graph TB
    A["Matrix Job"] --> B["generate_dispatch_group_jobs()"]
    B --> C["Extract job types from 'jobs' tag"]
    C --> D["Analyze dependencies"]
    D --> E{Job has<br/>dependency?}
    E -->|No| F["Add to standalone"]
    E -->|Yes| G["Add to two_stage<br/>as producer/consumer"]
    
    F --> H["generate_dispatch_job_json()"]
    G --> I["generate_dispatch_two_stage_json()"]
    
    H --> J["Dispatch Group"]
    I --> J
```

**Dispatch Job Structure:**

Each dispatch job contains the information needed to execute it:

```json
{
  "id": "Aa",
  "name": "[C++17 gcc12] Test(amd64, T4): sm{75}",
  "runner": "linux-amd64-gpu-t4-latest-1",
  "image": "rapidsai/devcontainers:24.10.00-cpp-gcc12-cuda11.1",
  "cuda": "11.1",
  "host": "gcc12",
  "command": "\"./ci/test_libcudacxx.sh\" -std \"17\" -arch \"75\"",
  "origin": { ... }
}
```

**Key Generation Functions:**
- `generate_dispatch_job_json()` [.github/actions/workflow-build/build-workflow.py:481-490]()
- `generate_dispatch_job_name()` [.github/actions/workflow-build/build-workflow.py:362-376]()
- `generate_dispatch_job_runner()` [.github/actions/workflow-build/build-workflow.py:379-390]()
- `generate_dispatch_job_image()` [.github/actions/workflow-build/build-workflow.py:404-412]()
- `generate_dispatch_job_command()` [.github/actions/workflow-build/build-workflow.py:415-445]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:362-490]()

### Two-Stage Job Structure

Jobs with dependencies are organized as producer/consumer pairs:

```json
{
  "id": "Ab",
  "producers": [
    {
      "id": "Ac",
      "name": "[C++17 gcc12] Build(amd64)",
      ...
    }
  ],
  "consumers": [
    {
      "id": "Ad",
      "name": "[C++17 gcc12] Test(amd64, T4): sm{75}",
      ...
    },
    {
      "id": "Ae",
      "name": "[C++17 gcc12] Test(amd64, V100): sm{70}",
      ...
    }
  ]
}
```

**Key Functions:**
- `generate_dispatch_two_stage_json()` [.github/actions/workflow-build/build-workflow.py:494-504]()
- `generate_dispatch_group_jobs()` [.github/actions/workflow-build/build-workflow.py:507-539]()

**Limitation:** Only one producer per two-stage group is supported [.github/actions/workflow-build/build-workflow.py:586-599]().

**Sources:** [.github/actions/workflow-build/build-workflow.py:494-539]()

### Finalization and Deduplication

The `finalize_workflow_dispatch_groups()` function performs cleanup and optimization:

**Deduplication Steps:**

1. **Merge duplicate producers**: If multiple two-stage entries have identical producers, merge their consumers [.github/actions/workflow-build/build-workflow.py:602-640]()

2. **Remove duplicate standalone jobs**: Warn and remove duplicates [.github/actions/workflow-build/build-workflow.py:643-651]()

3. **Remove standalone jobs that appear in two-stage**: If a job appears both as standalone and in a two-stage group, remove the standalone version [.github/actions/workflow-build/build-workflow.py:654-667]()

4. **Sort dispatch groups and jobs**: Natural sort by name [.github/actions/workflow-build/build-workflow.py:694-706]()

5. **Assign unique IDs**: Generate short, unique IDs for all jobs and two-stage groups [.github/actions/workflow-build/build-workflow.py:708-719]()

**GUID Generation:**

The system generates compact unique IDs (1-3 characters) using base64 encoding:

```python
# Examples: "A", "AA", "AB", "Aa", "Ab", "Ac", ...
```

**Key Functions:**
- `finalize_workflow_dispatch_groups()` [.github/actions/workflow-build/build-workflow.py:583-721]()
- `generate_guids()` [.github/actions/workflow-build/build-workflow.py:78-93]()
- `compare_dispatch_jobs()` [.github/actions/workflow-build/build-workflow.py:557-563]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:78-93](), [.github/actions/workflow-build/build-workflow.py:583-721]()

---

## Dispatch Preparation

The `prepare-workflow-dispatch.py` script reorganizes the complete workflow into four categories to optimize GitHub Actions UI presentation.

### Splitting Strategy

```mermaid
graph TB
    A["workflow.json"] --> B["split_workflow()"]
    
    B --> C{Is job<br/>Windows?}
    C -->|No| D{Standalone or<br/>Two-Stage?}
    C -->|Yes| E{Standalone or<br/>Two-Stage?}
    
    D -->|Standalone| F["linux_standalone"]
    D -->|Two-Stage| G["linux_two_stage"]
    E -->|Standalone| H["windows_standalone"]
    E -->|Two-Stage| I["windows_two_stage"]
    
    F --> J["dispatch.json"]
    G --> J
    H --> J
    I --> J
```

**OS Detection:**

Windows jobs are identified by checking if the runner string starts with `'windows'` [.github/actions/workflow-build/prepare-workflow-dispatch.py:21-22]().

**Output Structure:**

```json
{
  "linux_standalone": {
    "keys": ["libcudacxx CTK11.1 nvcc gcc12", ...],
    "jobs": {
      "libcudacxx CTK11.1 nvcc gcc12": [
        {"id": "Aa", "name": "...", ...}
      ]
    }
  },
  "linux_two_stage": {
    "keys": ["Thrust CTK12.0 nvcc gcc13", ...],
    "jobs": {
      "Thrust CTK12.0 nvcc gcc13": [
        {"id": "Ab", "producers": [...], "consumers": [...]}
      ]
    }
  },
  "windows_standalone": { ... },
  "windows_two_stage": { ... }
}
```

**Cleanup:**

The `origin` field is removed from each job during splitting to reduce output size [.github/actions/workflow-build/prepare-workflow-dispatch.py:31-32]().

**Key Functions:**
- `split_workflow()` [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-75]()
- `is_windows()` [.github/actions/workflow-build/prepare-workflow-dispatch.py:21-22]()

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:1-96]()

---

## Generated Artifacts

The generation pipeline produces several files in the `workflow/` directory:

### workflow.json

Complete workflow specification with all dispatch groups and jobs. This is the primary output from `build-workflow.py`.

**Structure:**
```json
{
  "Group Name 1": {
    "standalone": [
      {"id": "...", "name": "...", "runner": "...", "image": "...", "command": "...", "origin": {...}}
    ],
    "two_stage": [
      {
        "id": "...",
        "producers": [{...}],
        "consumers": [{...}]
      }
    ]
  },
  "Group Name 2": { ... }
}
```

**Generated by:** `write_outputs()` [.github/actions/workflow-build/build-workflow.py:979-1023]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:979-1023]()

### dispatch.json

Workflow split by OS and execution pattern, optimized for GitHub Actions dispatch workflows.

**Structure:** See "Dispatch Preparation" section above.

**Purpose:** Enables four separate dispatch workflows to run only relevant jobs, avoiding cluttered UI with hundreds of skipped jobs.

**Generated by:** `split_workflow()` [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-75]()

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-75]()

### job_ids.json

Mapping from short job IDs to full job names for human-readable reporting:

```json
{
  "Aa": "libcudacxx CTK11.1 nvcc gcc12 [C++17 gcc12] Test(amd64, T4): sm{75}",
  "Ab": "Thrust CTK12.0 nvcc gcc13 [C++20 gcc13] Build(amd64)"
}
```

**Generated by:** `write_outputs()` [.github/actions/workflow-build/build-workflow.py:982-1005]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:982-1005]()

### runner_summary.json

Summary of runner allocation for the GitHub Step Summary:

```json
{
  "heading": "🏃‍ Runner counts (total jobs: 42)",
  "body": "| #    | Runner\n|------|------\n|   20 | `linux-amd64-gpu-t4-latest-1`\n|   15 | `linux-amd64-cpu16`\n|    7 | `windows-amd64-cpu16`\n"
}
```

**Generated by:** `write_outputs()` [.github/actions/workflow-build/build-workflow.py:1007-1017]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:1007-1017]()

### job_list.txt

Human-readable list of all jobs for debugging:

```
   1 id: Aa     standalone     [C++17 gcc12] Test(amd64, T4): sm{75}
   2 id: Ab     producers      [C++17 gcc12] Build(amd64)
   3 id: Ac     consumers      [C++17 gcc12] Test(amd64, V100): sm{70}
```

**Generated by:** `write_outputs()` [.github/actions/workflow-build/build-workflow.py:981-1022]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:981-1022]()

---

## workflow-build Action

The `workflow-build` composite action orchestrates the entire generation pipeline.

### Execution Sequence

```mermaid
graph TB
    A["Start"] --> B["Send Slack log notification"]
    B --> C{inspect_changes_script<br/>provided?}
    C -->|Yes| D["Run inspect-changes script"]
    C -->|No| E["Parse matrix file"]
    D --> E
    
    E["build-workflow.py"] --> F["Generate workflow.json"]
    F --> G["prepare-workflow-dispatch.py"]
    G --> H["Generate dispatch.json"]
    
    H --> I["Display runner summary"]
    I --> J["Display job list"]
    J --> K["Upload workflow/ artifacts"]
    
    K --> L{Success?}
    L -->|Yes| M["End"]
    L -->|No| N["Send Slack error notification"]
    N --> M
```

### Step Details

**Step 1: Slack Notification** [.github/actions/workflow-build/action.yml:47-59]()
- Sends initial notification to log channel if credentials provided
- Includes workflow type and run URL

**Step 2: Inspect Changes** [.github/actions/workflow-build/action.yml:61-72]()
- Conditionally runs change detection script
- Exports `dirty_projects` output for filtering

**Step 3: Parse Matrix** [.github/actions/workflow-build/action.yml:74-100]()
- Invokes `build-workflow.py` with appropriate flags
- Outputs workflow.json, job_ids.json, runner_summary.json, job_list.txt
- Displays runner summary and job list in GitHub Step Summary

**Step 4: Create Dispatch Workflows** [.github/actions/workflow-build/action.yml:102-109]()
- Invokes `prepare-workflow-dispatch.py`
- Generates dispatch.json

**Step 5: Set Outputs** [.github/actions/workflow-build/action.yml:111-117]()
- Sets `WORKFLOW` output to contents of dispatch.json (compact JSON)

**Step 6: Upload Artifacts** [.github/actions/workflow-build/action.yml:119-124]()
- Uploads entire `workflow/` directory as GitHub Actions artifact
- Used by downstream workflow-results action

**Step 7: Error Notification** [.github/actions/workflow-build/action.yml:126-139]()
- Sends Slack notification to alert and/or log channels on failure

### Action Inputs Reference

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `workflows` | string | Yes | - | Space-separated workflow names |
| `allow_override` | boolean | No | `false` | Use override workflow if present |
| `inspect_changes_script` | string | No | `""` | Path to change detection script |
| `inspect_changes_base_sha` | string | No | `""` | Base SHA for change detection |
| `matrix_file` | string | No | `ci/matrix.yaml` | Path to matrix configuration |
| `matrix_parser` | string | No | `""` | Custom parser script path |
| `slack_token` | string | No | - | Slack bot token |
| `slack_log` | string | No | - | Slack log channel ID |
| `slack_alert` | string | No | - | Slack alert channel ID |

### Action Outputs Reference

| Output | Description |
|--------|-------------|
| `workflow` | Complete dispatch.json as compact JSON string |

**Sources:** [.github/actions/workflow-build/action.yml:1-140]()

---

## Error Handling

The generation system includes comprehensive error reporting:

### Error Message Format

Errors include file location and context:

```
ci/matrix.yaml:42 (job 3): Missing required tag 'ctk'
  Input: {project: libcudacxx, cxx: gcc12, std: 17}
```

**Generated by:** `error_message_with_matrix_job()` [.github/actions/workflow-build/build-workflow.py:109-110]()

### Validation Errors

- Missing required tags [.github/actions/workflow-build/build-workflow.py:818-819]()
- Unknown tags [.github/actions/workflow-build/build-workflow.py:827-828]()
- Unknown CTK versions [.github/actions/workflow-build/build-workflow.py:123]()
- Unknown host compilers [.github/actions/workflow-build/build-workflow.py:151-152]()
- Unknown GPUs [.github/actions/workflow-build/build-workflow.py:831]()
- Clang device compiler without clang host compiler [.github/actions/workflow-build/build-workflow.py:821-822]()

### Warnings

Warnings are emitted as GitHub annotations:

```
::notice file=ci/matrix.yaml::Merging consumers for duplicate producer 'Build' in 'libcudacxx CTK11.1'
```

**Warning Types:**
- Duplicate producers being merged [.github/actions/workflow-build/build-workflow.py:621-632]()
- Duplicate standalone jobs being removed [.github/actions/workflow-build/build-workflow.py:648-649]()
- Standalone jobs removed due to two-stage presence [.github/actions/workflow-build/build-workflow.py:658-664]()
- Jobs appearing multiple times in two-stage groups [.github/actions/workflow-build/build-workflow.py:679-682]()

### Fatal Errors

Certain conditions cause immediate failure:

- Multiple producers in a single two-stage group [.github/actions/workflow-build/build-workflow.py:592-599]()
- GUID generator exhaustion (>65535 jobs) [.github/actions/workflow-build/build-workflow.py:92-93]()
- Missing matrix file [.github/actions/workflow-build/build-workflow.py:1119-1121]()
- Workflow not found in matrix file [.github/actions/workflow-build/build-workflow.py:929]()

**Sources:** [.github/actions/workflow-build/build-workflow.py:109-110](), [.github/actions/workflow-build/build-workflow.py:592-599](), [.github/actions/workflow-build/build-workflow.py:818-831]()

---

# Page: build-workflow.py Pipeline

# build-workflow.py Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)

</details>



## Purpose and Scope

This document describes the `build-workflow.py` processing pipeline, which transforms a human-readable `matrix.yaml` configuration into fully-specified job definitions ready for GitHub Actions dispatch. The pipeline performs multi-stage processing including validation, default-setting, tag explosion, canonicalization, derived tag computation, and exclusion filtering.

For information about the dispatch.json structure produced downstream from this pipeline, see [Dispatch Preparation](#3.2). For the overall workflow generation architecture, see [Workflow Generation](#3). For details on the matrix.yaml schema itself, see [Matrix YAML Structure](#2.1).

**Sources:** [.github/actions/workflow-build/build-workflow.py:1-1140]()

---

## Pipeline Overview

The `build-workflow.py` pipeline processes matrix job definitions through a series of transformations, converting compact YAML entries into complete job specifications.

```mermaid
graph TB
    Input["matrix.yaml<br/>workflows section"]
    
    PreProc["preprocess_matrix_yaml()<br/>Version key normalization"]
    
    Parse["parse_workflow_matrix_jobs()<br/>Main orchestrator"]
    
    Validate["validate_tags()<br/>Check required tags"]
    
    Defaults["set_default_tags()<br/>Fill optional parameters"]
    
    Explode1["explode_tags()<br/>First pass expansion"]
    
    Canonicalize["canonicalize_tags()<br/>Resolve aliases"]
    
    Derived["set_derived_tags()<br/>Compute sm, std:all, deps"]
    
    Explode2["explode_tags()<br/>Second pass expansion"]
    
    Exclude["remove_excluded_jobs()<br/>Filter combinations"]
    
    Convert["matrix_job_to_dispatch_group()<br/>Generate dispatch structure"]
    
    Finalize["finalize_workflow_dispatch_groups()<br/>Deduplicate & assign IDs"]
    
    Output["write_outputs()<br/>workflow.json, job_ids.json, etc."]
    
    Input --> PreProc
    PreProc --> Parse
    Parse --> Validate
    Validate --> Defaults
    Defaults --> Explode1
    Explode1 --> Canonicalize
    Canonicalize --> Derived
    Derived --> Explode2
    Explode2 --> Exclude
    Exclude --> Convert
    Convert --> Finalize
    Finalize --> Output
```

**Diagram: End-to-End Processing Pipeline**

The pipeline operates on **matrix jobs**, which are JSON objects representing individual job configurations. Each stage modifies these objects, progressively transforming them from terse YAML entries into complete job specifications.

**Sources:** [.github/actions/workflow-build/build-workflow.py:902-920](), [.github/actions/workflow-build/build-workflow.py:922-960](), [.github/actions/workflow-build/build-workflow.py:962-977]()

---

## Core Data Structures

The pipeline works with three primary data types, defined in the file header comments:

| Data Structure | Description | Key Fields |
|----------------|-------------|------------|
| **matrix_job** | Input configuration from matrix.yaml | `project`, `jobs`, `ctk`, `cxx`, `cudacxx`, `std`, `gpu`, `sm`, `cpu` |
| **dispatch_group_json** | Grouped jobs by configuration | `<group_name>: { standalone: [...], two_stage: [...] }` |
| **job_json** | Fully-specified executable job | `id`, `name`, `runner`, `image`, `command`, `origin` |

**Sources:** [.github/actions/workflow-build/build-workflow.py:4-54]()

### Matrix Job Structure

A matrix job evolves through the pipeline. Here's an example transformation:

**Input (matrix.yaml):**
```yaml
- project: [libcudacxx, cub, thrust]
  ctk: "11.1"
  cxx: gcc10
  std: all
  gpu: t4
  sm: gpu
```

**After Processing:**
```json
{
  "project": "libcudacxx",
  "jobs": ["build", "test"],
  "ctk": "11.1",
  "cudacxx": "nvcc",
  "cxx": "gcc10",
  "cpu": "amd64",
  "gpu": "t4",
  "sm": "75-real",
  "std": 17,
  "origin": { "filename": "ci/matrix.yaml", ... }
}
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:6-23]()

---

## Input Processing and Preprocessing

### Matrix YAML Loading

The pipeline begins by loading and normalizing the matrix YAML file:

```mermaid
graph LR
    LoadYAML["yaml.safe_load()<br/>Read matrix file"]
    
    PreProc["preprocess_matrix_yaml()<br/>Type normalization"]
    
    CTK["Convert CTK version keys<br/>to strings"]
    
    Compiler["Convert compiler version keys<br/>to strings"]
    
    Global["Store in global<br/>matrix_yaml variable"]
    
    LoadYAML --> PreProc
    PreProc --> CTK
    PreProc --> Compiler
    PreProc --> Global
```

**Diagram: Matrix YAML Preprocessing**

The `preprocess_matrix_yaml()` function ensures all version numbers are strings, preventing type mismatches during later lookups. This handles cases where YAML parsers interpret numeric values like `11.1` or `10` differently.

**Sources:** [.github/actions/workflow-build/build-workflow.py:1087-1101](), [.github/actions/workflow-build/build-workflow.py:1123-1127]()

### Workflow Selection and Filtering

The `parse_workflow_matrix_jobs()` function orchestrates the main processing:

```mermaid
graph TB
    Args["Command-line arguments<br/>--workflows, --dirty-projects"]
    
    Lookup["Look up workflow in<br/>matrix_yaml['workflows']"]
    
    LineNum["find_workflow_line_number()<br/>For error reporting"]
    
    Origin["Tag each matrix_job<br/>with origin info"]
    
    PreProcess["preprocess_matrix_jobs()<br/>Main processing"]
    
    DirtyFilter{{"dirty_projects<br/>specified?"}}
    
    ProjectFilter["Filter by<br/>job['project'] in dirty_projects"]
    
    ExcludeFilter["remove_excluded_jobs()<br/>Apply exclusions"]
    
    Sort["Sort tags by importance<br/>get_all_matrix_job_tags_sorted()"]
    
    Args --> Lookup
    Lookup --> LineNum
    LineNum --> Origin
    Origin --> PreProcess
    PreProcess --> DirtyFilter
    DirtyFilter -->|Yes| ProjectFilter
    DirtyFilter -->|No| ExcludeFilter
    ProjectFilter --> ExcludeFilter
    ExcludeFilter --> Sort
```

**Diagram: parse_workflow_matrix_jobs() Flow**

**Sources:** [.github/actions/workflow-build/build-workflow.py:922-960]()

---

## Tag Processing Stages

The `preprocess_matrix_jobs()` function applies a series of transformations to each matrix job:

### Stage 1: Validation

The `validate_tags()` function ensures matrix jobs conform to the schema:

| Validation Check | Error Condition |
|------------------|----------------|
| **Required tags** | Missing `project`, `jobs`, or other required tags |
| **Known tags** | Tag not in `matrix_yaml['tags']` |
| **Valid GPUs** | GPU string not in `matrix_yaml['gpus']` |
| **clang consistency** | `cudacxx: clang` requires `cxx: clang` |

The validation can be run in two modes:
- **Normal mode** (`ignore_required=False`): Enforces all required tags
- **Exclusion mode** (`ignore_required=True`): Only checks tag names, not requirements

**Sources:** [.github/actions/workflow-build/build-workflow.py:811-832]()

### Stage 2: Default Setting

The `set_default_tags()` function fills in missing optional tags using defaults from `matrix_yaml['tags']`:

```python
# Example tag definitions with defaults:
tags:
  cpu:
    default: "amd64"
  cudacxx:
    default: "nvcc"
  jobs:
    default: ["build"]
```

For each tag in the schema, if it has a `default` value and isn't present in the matrix job, the default is applied.

**Sources:** [.github/actions/workflow-build/build-workflow.py:834-843]()

### Stage 3: Tag Explosion (First Pass)

The `explode_tags()` function recursively expands list values into separate matrix jobs:

```mermaid
graph TB
    Input["Input matrix_job<br/>{project: [libcudacxx, cub],<br/>std: [17, 20]}"]
    
    NextTag["next_explode_tag()<br/>Find first list-valued tag<br/>(excluding 'jobs')"]
    
    FoundProject{{"Found 'project'<br/>as list?"}}
    
    Iterate["For each value in<br/>matrix_job['project']"]
    
    Clone["Create deep copy<br/>new_job = copy.deepcopy()"]
    
    Assign["new_job['project'] = value"]
    
    Recurse["explode_tags(new_job)<br/>Recursively process"]
    
    Result["Return list of<br/>fully-exploded jobs"]
    
    Input --> NextTag
    NextTag --> FoundProject
    FoundProject -->|Yes| Iterate
    Iterate --> Clone
    Clone --> Assign
    Assign --> Recurse
    Recurse --> Result
```

**Diagram: Tag Explosion Algorithm**

The `jobs` tag is intentionally **not exploded** to optimize scheduling. Multiple job types (e.g., `["build", "test"]`) remain together in a single matrix job for dependency analysis.

**Sources:** [.github/actions/workflow-build/build-workflow.py:877-900]()

### Stage 4: Canonicalization

The `canonicalize_tags()` function resolves aliases and standardizes naming:

```mermaid
graph LR
    CTK["canonicalize_ctk_version()<br/>11.8 → 11.8<br/>latest → 12.6"]
    
    CXX["canonicalize_host_compiler_name()<br/>gcc → gcc13<br/>gcc-10 → gcc10<br/>clang → clang18"]
    
    CTK --> CXX
```

**Diagram: Canonicalization Functions**

**CTK Canonicalization** ([.github/actions/workflow-build/build-workflow.py:113-124]()):
- Checks if the version string exists directly in `matrix_yaml['ctk_versions']`
- If not, searches for an `aka` field match (e.g., `latest`)
- Returns the canonical key

**Host Compiler Canonicalization** ([.github/actions/workflow-build/build-workflow.py:138-173]()):
- Parses the compiler string using regex: `([a-z]+)-?([\d\.]+)?`
- If no version specified, selects the highest version number
- Checks for version `aka` aliases
- Returns format: `{compiler_id}{version}` (e.g., `gcc10`)

**Sources:** [.github/actions/workflow-build/build-workflow.py:845-850]()

### Stage 5: Derived Tags

The `set_derived_tags()` function computes values from other tags:

| Derived Tag | Computation Logic |
|-------------|-------------------|
| **sm** | If `sm: "gpu"`, look up `matrix_yaml['gpus'][gpu]['sm']` |
| **std** | If `std: "all"`, call `lookup_supported_stds()` to find common standards |
| **jobs** | Add dependencies from `matrix_yaml['jobs'][job]['needs']` |
| **jobs** | Apply project-specific `job_map` expansions |

#### SM Architecture Derivation

```python
if matrix_job['sm'] == 'gpu':
    gpu = get_gpu(matrix_job['gpu'])
    matrix_job['sm'] = gpu['sm']  # e.g., "75-real" for T4
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:852-858]()

#### C++ Standard Derivation

The `lookup_supported_stds()` function computes the intersection of standards supported by all components:

```mermaid
graph LR
    AllStds["Start with<br/>matrix_yaml['all_stds']<br/>{11, 14, 17, 20, 23}"]
    
    CTK["Intersect with<br/>CTK supported stds"]
    
    CXX["Intersect with<br/>host compiler stds"]
    
    CUDACXX["Intersect with<br/>device compiler stds"]
    
    Project["Intersect with<br/>project stds"]
    
    Result["Return sorted<br/>common standards"]
    
    AllStds --> CTK
    CTK --> CXX
    CXX --> CUDACXX
    CUDACXX --> Project
    Project --> Result
```

**Diagram: C++ Standard Intersection Logic**

**Sources:** [.github/actions/workflow-build/build-workflow.py:323-338](), [.github/actions/workflow-build/build-workflow.py:859-861]()

#### Job Dependency Resolution

The pipeline automatically adds producer jobs when consumers are requested:

```python
for job in matrix_job['jobs']:
    job_info = get_job_type_info(job)
    dep = job_info['needs']  # e.g., 'test' needs 'build'
    if dep and dep not in matrix_job['jobs']:
        matrix_job['jobs'].append(dep)
```

Then project-specific job mappings are applied:

```python
project = get_project(matrix_job['project'])
for original_job, expanded_jobs in project['job_map'].items():
    if original_job in matrix_job['jobs']:
        matrix_job['jobs'].remove(original_job)
        matrix_job['jobs'] += expanded_jobs
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:863-875]()

### Stage 6: Tag Explosion (Second Pass)

After derived tags are set, `explode_tags()` runs again to expand any list values introduced by derivation (e.g., `std: "all"` became `[17, 20, 23]`).

**Sources:** [.github/actions/workflow-build/build-workflow.py:914-918]()

---

## Exclusion Filtering

The `remove_excluded_jobs()` function applies exclusion rules from the `exclude` workflow:

```mermaid
graph TB
    Jobs["List of matrix_jobs"]
    
    GetExcl["get_excluded_matrix_jobs()<br/>Parse 'exclude' workflow"]
    
    IterJobs["For each matrix_job"]
    
    IterExcl["For each exclusion rule"]
    
    Apply["apply_matrix_job_exclusion()<br/>Check match"]
    
    Matches{{"All tags<br/>match?"}}
    
    PartialMatch{{"Partial<br/>match?"}}
    
    Remove["Remove matched values<br/>from matrix_job"]
    
    Discard["Set matrix_job = None"]
    
    Keep["Keep matrix_job"]
    
    Collect["Collect non-None jobs"]
    
    Jobs --> GetExcl
    GetExcl --> IterJobs
    IterJobs --> IterExcl
    IterExcl --> Apply
    Apply --> Matches
    Matches -->|Yes, complete| Discard
    Matches -->|No| Keep
    Matches -->|Partial| PartialMatch
    PartialMatch --> Remove
    Remove --> IterExcl
    Discard --> Collect
    Keep --> Collect
```

**Diagram: Exclusion Application Logic**

### Exclusion Matching Algorithm

The `apply_matrix_job_exclusion()` function implements sophisticated partial matching:

1. **Tag presence check**: If an exclusion specifies a tag not in the matrix job, the exclusion doesn't apply
2. **Value matching**: For each exclusion tag, check if any specified values match the matrix job
3. **Complete vs. partial match**:
   - **Complete**: All tag values match → return `None` (discard job)
   - **Partial**: Some values match → remove matched values from matrix job
   - **No match**: No values match for any tag → return matrix job unchanged

**Example:**
```yaml
# Exclusion:
- project: libcudacxx
  std: [11, 14]

# Matrix job:
project: libcudacxx
std: [11, 14, 17]

# Result: std becomes [17] (partial removal)
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:753-808]()

---

## Dispatch Group Generation

After all matrix jobs are processed, they're converted to dispatch groups by `matrix_job_to_dispatch_group()`:

```mermaid
graph TB
    MatrixJob["Processed matrix_job"]
    
    GenName["generate_dispatch_group_name()<br/>Create group key"]
    
    GenJobs["generate_dispatch_group_jobs()<br/>Analyze job dependencies"]
    
    JobTypes["Extract job_types from<br/>matrix_job['jobs']"]
    
    AnalyzeDeps["For each job_type,<br/>check get_job_type_info()['needs']"]
    
    Standalone{{"Has dependency?"}}
    
    AddStandalone["Add to standalone set"]
    
    AddTwoStage["Add to two_stage dict<br/>{producer: [consumers]}"]
    
    BuildStandalone["For each standalone job:<br/>generate_dispatch_job_json()"]
    
    BuildTwoStage["For each producer/consumers:<br/>generate_dispatch_two_stage_json()"]
    
    Return["Return dispatch_group_json"]
    
    MatrixJob --> GenName
    MatrixJob --> GenJobs
    GenJobs --> JobTypes
    JobTypes --> AnalyzeDeps
    AnalyzeDeps --> Standalone
    Standalone -->|No| AddStandalone
    Standalone -->|Yes| AddTwoStage
    AddStandalone --> BuildStandalone
    AddTwoStage --> BuildTwoStage
    BuildStandalone --> Return
    BuildTwoStage --> Return
```

**Diagram: Dispatch Group Generation**

### Group Naming

The `generate_dispatch_group_name()` function creates human-readable group names:

```python
# Example output:
"libcudacxx CTK11.1 nvcc GCC"
"Thrust CTK12.6 Clang"
```

Format: `{project_name} CTK{version} {device_compiler} {host_compiler}`

**Sources:** [.github/actions/workflow-build/build-workflow.py:345-360]()

### Job JSON Generation

The `generate_dispatch_job_json()` function creates complete job specifications:

```mermaid
graph LR
    MatrixJob["matrix_job +<br/>job_type"]
    
    Runner["generate_dispatch_job_runner()<br/>Select runner"]
    
    Image["generate_dispatch_job_image()<br/>Devcontainer image"]
    
    Command["generate_dispatch_job_command()<br/>Build script invocation"]
    
    Name["generate_dispatch_job_name()<br/>Human-readable name"]
    
    Origin["generate_dispatch_job_origin()<br/>Trace to matrix.yaml"]
    
    JSON["Assemble job_json"]
    
    MatrixJob --> Runner
    MatrixJob --> Image
    MatrixJob --> Command
    MatrixJob --> Name
    MatrixJob --> Origin
    
    Runner --> JSON
    Image --> JSON
    Command --> JSON
    Name --> JSON
    Origin --> JSON
```

**Diagram: Job JSON Assembly**

**Sources:** [.github/actions/workflow-build/build-workflow.py:481-491]()

#### Runner Selection Logic

The `generate_dispatch_job_runner()` function determines the appropriate GitHub Actions runner:

| Job Type | Runner Format |
|----------|---------------|
| CPU-only | `{os}-{cpu}-cpu16` |
| GPU (non-testing) | `{os}-{cpu}-gpu-{gpu_id}-latest-1` |
| GPU (testing) | `{os}-{cpu}-gpu-{gpu_id}-latest-1-testing` |

**Sources:** [.github/actions/workflow-build/build-workflow.py:379-391]()

#### Image Selection

Devcontainer images follow this format:

```
# Linux:
rapidsai/devcontainers:{version}-cpp-{host}-cuda{ctk}

# Windows:
rapidsai/devcontainers:{version}-cuda{ctk}-{host}
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:404-413]()

#### Command Generation

The `generate_dispatch_job_command()` function builds the script invocation string:

```bash
# Example Linux command:
"./ci/build_libcudacxx.sh -std \"17\" -arch \"75-real\""

# Example Windows command:
"./ci/windows/test_thrust.ps1 -std \"20\" -cuda \"clang++\""
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:415-446]()

---

## Finalization and Deduplication

The `finalize_workflow_dispatch_groups()` function performs cleanup and assigns unique IDs:

```mermaid
graph TB
    Input["workflow_dispatch_groups<br/>(merged from all matrix jobs)"]
    
    CheckProd["Validate producer count<br/>(must be exactly 1)"]
    
    MergeConsumers["Merge consumers for<br/>duplicate producers"]
    
    DedupeStandalone["Remove duplicate<br/>standalone jobs"]
    
    RemoveOverlap["Remove standalone jobs<br/>that appear in two_stage"]
    
    WarnDupes["Warn about duplicate<br/>two_stage jobs"]
    
    RemoveEmpty["Delete groups with<br/>no jobs"]
    
    Sort["Natural sort groups<br/>and jobs within groups"]
    
    AssignIDs["Assign unique IDs<br/>using guid_generator"]
    
    Return["Return finalized<br/>dispatch groups"]
    
    Input --> CheckProd
    CheckProd --> MergeConsumers
    MergeConsumers --> DedupeStandalone
    DedupeStandalone --> RemoveOverlap
    RemoveOverlap --> WarnDupes
    WarnDupes --> RemoveEmpty
    RemoveEmpty --> Sort
    Sort --> AssignIDs
    AssignIDs --> Return
```

**Diagram: Finalization Pipeline**

### Producer Count Validation

The system enforces a single-producer constraint:

```python
for two_stage_json in group_json['two_stage']:
    num_producers = len(two_stage_json['producers'])
    if num_producers > 1:
        raise Exception("ci-dispatch-two-stage.yml currently only supports a single producer.")
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:586-600]()

### Consumer Merging

When duplicate producers are detected, their consumers are merged:

```python
if dispatch_job_in_container(producer, merged_producers):
    # Find matching consumers
    matching_consumers = merged_consumers[producer_index]
    # Merge unique consumers
    for consumer in consumers:
        if not dispatch_job_in_container(consumer, matching_consumers):
            matching_consumers.append(consumer)
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:601-640]()

### Job Comparison

The `compare_dispatch_jobs()` function checks equality by comparing:
- `name`
- `runner`
- `image`
- `command`

The `origin` field is intentionally **ignored** because different matrix entries can produce identical job specifications.

**Sources:** [.github/actions/workflow-build/build-workflow.py:557-572]()

### GUID Assignment

The `generate_guids()` generator produces compact unique IDs:

```python
# Generates base64-encoded 16-bit integers
# Strips leading 'A' characters and trailing '='
# Examples: "B", "AA", "AAD", "QA", "gA"
# Maximum: 65535 unique IDs
```

IDs are assigned to:
- Each standalone job
- Each two_stage group
- Each producer and consumer within two_stage groups

**Sources:** [.github/actions/workflow-build/build-workflow.py:78-96](), [.github/actions/workflow-build/build-workflow.py:708-720]()

---

## Output Generation

The `write_outputs()` function produces four output files:

```mermaid
graph TB
    FinalWorkflow["finalized_workflow_dispatch_groups"]
    
    Iterate["Iterate all jobs in<br/>all groups"]
    
    JobList["Build job_list.txt<br/>Human-readable listing"]
    
    JobIDs["Build job_ids.json<br/>{id: full_name}"]
    
    RunnerCounts["Count jobs per runner<br/>runner_summary.json"]
    
    WriteWorkflow["workflow/workflow.json<br/>Complete dispatch groups"]
    
    WriteIDs["workflow/job_ids.json<br/>ID mappings"]
    
    WriteList["workflow/job_list.txt<br/>Job listing"]
    
    WriteSummary["workflow/runner_summary.json<br/>Runner allocation table"]
    
    FinalWorkflow --> Iterate
    Iterate --> JobList
    Iterate --> JobIDs
    Iterate --> RunnerCounts
    
    FinalWorkflow --> WriteWorkflow
    JobIDs --> WriteIDs
    JobList --> WriteList
    RunnerCounts --> WriteSummary
```

**Diagram: Output File Generation**

### Output File Formats

| File | Purpose | Format |
|------|---------|--------|
| **workflow.json** | Complete dispatch group definitions | JSON object keyed by group name |
| **job_ids.json** | Maps short IDs to full job names | `{ "id": "Group Name Job Name", ... }` |
| **job_list.txt** | Human-readable job listing | Text with numbering and indentation |
| **runner_summary.json** | Runner allocation summary | `{ "heading": "...", "body": "markdown table" }` |

**Sources:** [.github/actions/workflow-build/build-workflow.py:979-1024]()

### Runner Summary Format

The runner summary JSON contains:

```json
{
  "heading": "🏃‍ Runner counts (total jobs: 247)",
  "body": "| #    | Runner\n|------|------\n|  120 | `linux-amd64-cpu16`\n..."
}
```

This is used by downstream reporting to show resource allocation.

**Sources:** [.github/actions/workflow-build/build-workflow.py:1010-1017]()

---

## Support Functions and Utilities

### Lookup Functions

The pipeline uses memoized lookup functions to fetch metadata:

```mermaid
graph TB
    GetCTK["get_ctk(ctk_string)<br/>CTK metadata"]
    
    GetHostCompiler["get_host_compiler(cxx_string)<br/>Host compiler metadata"]
    
    GetDeviceCompiler["get_device_compiler(matrix_job)<br/>Device compiler metadata"]
    
    GetGPU["get_gpu(gpu_string)<br/>GPU metadata"]
    
    GetProject["get_project(project)<br/>Project metadata"]
    
    GetJobType["get_job_type_info(job)<br/>Job type metadata"]
    
    GetTagInfo["get_tag_info(tag)<br/>Tag schema info"]
    
    MatrixYAML["matrix_yaml global variable"]
    
    MatrixYAML --> GetCTK
    MatrixYAML --> GetHostCompiler
    MatrixYAML --> GetDeviceCompiler
    MatrixYAML --> GetGPU
    MatrixYAML --> GetProject
    MatrixYAML --> GetJobType
    MatrixYAML --> GetTagInfo
```

**Diagram: Metadata Lookup Functions**

All lookup functions use the `@memoize_result` decorator for performance:

```python
@memoize_result
def get_ctk(ctk_string):
    result = matrix_yaml['ctk_versions'][ctk_string]
    result["version"] = ctk_string
    return result
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:126-303]()

### Host Compiler Parsing

The `parse_cxx_string()` function uses regex to extract compiler ID and version:

```python
# Input: "gcc10", "gcc-12", "clang", "clang-18"
# Regex: r'^([a-z]+)-?([\d\.]+)?$'
# Output: (id, version) tuple
# Examples:
#   "gcc10" → ("gcc", "10")
#   "gcc" → ("gcc", None)
#   "clang-18" → ("clang", "18")
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:132-136]()

### Origin Tracking

The `get_matrix_job_origin()` function creates traceback information:

```python
{
  "filename": "ci/matrix.yaml",
  "workflow_name": "pull_request",
  "workflow_location": "ci/matrix.yaml:42 (job 1)",
  "original_matrix_job": "{project: libcudacxx, ctk: 11.1, ...}"
}
```

This enables error messages like:

```
ci/matrix.yaml:42 (job 1): Missing required tag 'cxx'
  Input: {project: libcudacxx, ctk: 11.1, jobs: [test]}
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:736-746](), [.github/actions/workflow-build/build-workflow.py:109-111]()

### Error Reporting

The pipeline uses GitHub Actions annotations for errors and warnings:

```python
print(f"::error file=ci/matrix.yaml::{error_message}", file=sys.stderr)
print(f"::warning file=ci/matrix.yaml::Job '{job_name}' appears {count} times...", 
      file=sys.stderr)
print(f"::notice file=ci/matrix.yaml::Merging consumers...", file=sys.stderr)
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:598-599](), [.github/actions/workflow-build/build-workflow.py:621-632](), [.github/actions/workflow-build/build-workflow.py:679-682]()

---

## Command-Line Interface

The script supports two primary modes:

### Workflow Generation Mode

```bash
python build-workflow.py matrix.yaml \
  --workflows pull_request nightly \
  --dirty-projects libcudacxx thrust \
  --allow-override
```

**Arguments:**

| Argument | Purpose |
|----------|---------|
| `matrix_file` | Path to matrix.yaml |
| `--workflows` | List of workflow names to process |
| `--dirty-projects` | Filter jobs to specified projects only |
| `--allow-override` | Check for `override` workflow and use if present |

**Sources:** [.github/actions/workflow-build/build-workflow.py:1104-1116](), [.github/actions/workflow-build/build-workflow.py:1129-1136]()

### Devcontainer Info Mode

```bash
python build-workflow.py matrix.yaml --devcontainer-info
```

This mode extracts unique CTK/compiler combinations for devcontainer generation, outputting JSON to stdout.

**Sources:** [.github/actions/workflow-build/build-workflow.py:1050-1085](), [.github/actions/workflow-build/build-workflow.py:1131-1136]()

### Override Workflow Handling

When `--allow-override` is specified and a non-empty `override` workflow exists:

```python
if args.allow_override and 'override' in matrix_yaml['workflows']:
    override_matrix = matrix_yaml['workflows']['override']
    if override_matrix and len(override_matrix) > 0:
        print(f"::notice::Using 'override' workflow instead of '{workflow_names}'")
        workflow_names = ['override']
        write_override_matrix(override_matrix)
```

This creates `workflow/override.json` and processes only the override workflow.

**Sources:** [.github/actions/workflow-build/build-workflow.py:1031-1038]()

---

## Integration Points

### Upstream Inputs

- **matrix.yaml**: Configuration file defining all job combinations (see [Matrix YAML Structure](#2.1))
- **Command-line arguments**: Workflow selection and filtering options

### Downstream Consumers

- **prepare-workflow-dispatch.py**: Consumes `workflow.json` to create `dispatch.json` (see [Dispatch Preparation](#3.2))
- **workflow-results**: Uses `job_ids.json` and `runner_summary.json` for reporting (see [Results and Reporting](#6))
- **GitHub Actions workflows**: Consume dispatch groups for execution

**Sources:** [.github/actions/workflow-build/build-workflow.py:1019-1024]()

---

# Page: Dispatch Preparation

# Dispatch Preparation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/prepare-workflow-dispatch.py](.github/actions/workflow-build/prepare-workflow-dispatch.py)

</details>



This document explains how `prepare-workflow-dispatch.py` transforms the comprehensive `workflow.json` into `dispatch.json`, organizing jobs by operating system and execution pattern to optimize the GitHub Actions UI experience. This script is the final step in the workflow generation pipeline before jobs are dispatched for execution.

For information about the generation of `workflow.json`, see [build-workflow.py Pipeline](#3.1). For the structure of the output artifacts, see [Generated Artifacts](#3.3).

---

## Purpose and Problem Statement

The `prepare-workflow-dispatch.py` script addresses a specific GitHub Actions UI limitation: when workflows contain many jobs with conditional execution (using `if:` expressions), the UI displays all skipped jobs, creating visual clutter that obscures the jobs that actually ran. This is problematic for the CCCL workflow system, which may define hundreds of job configurations but only execute a subset based on the runner OS and execution pattern.

The solution is to split the monolithic `workflow.json` into four separate job collections, each targeting a specific combination of OS and execution pattern. This allows GitHub Actions workflows to dispatch only relevant jobs, eliminating skipped job entries from the UI.

**Core Problem:**
```
workflow.json → 400 jobs defined
├─ Linux jobs executed on Linux runners → 200 jobs relevant, 200 skipped
└─ Windows jobs executed on Windows runners → 200 jobs relevant, 200 skipped
```

**Solution:**
```
workflow.json → dispatch.json
├─ linux_standalone → only Linux standalone jobs
├─ linux_two_stage → only Linux two-stage chains
├─ windows_standalone → only Windows standalone jobs
└─ windows_two_stage → only Windows two-stage chains
```

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:1-8]()

---

## Input Structure: workflow.json

The script consumes `workflow.json` produced by `build-workflow.py`. This file is organized as a nested dictionary where:

- **Top level:** Group names (strings like `"thrust"`, `"cub"`, `"libcudacxx"`)
- **Group level:** Contains `standalone` and/or `two_stage` keys
- **Job level:** Individual job objects with complete configuration

### Expected Schema

```
{
  "group_name": {
    "standalone": [
      { "id": "...", "runner": "...", "origin": {...}, ... },
      ...
    ],
    "two_stage": [
      {
        "producers": [{ "id": "...", "runner": "...", "origin": {...}, ... }],
        "consumers": [{ "id": "...", "runner": "...", "origin": {...}, ... }, ...]
      },
      ...
    ]
  },
  ...
}
```

Each job object contains:
- `runner`: String identifying the GitHub Actions runner (e.g., `"linux-amd64-cpu16"`, `"windows-cpu8"`)
- `origin`: Metadata about the job's source configuration (removed during dispatch preparation)
- Additional job-specific fields (command, environment, etc.)

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:88-91]()

---

## Processing Logic

### OS Detection Algorithm

The script categorizes jobs by operating system using a simple heuristic: inspect the `runner` field of each job. The `is_windows()` function determines if a job targets Windows runners.

**OS Detection Flow:**

```mermaid
graph TB
    Job["Job Object"]
    CheckRunner["Check job['runner']"]
    IsWindows{"runner.startswith('windows')?"}
    Linux["Categorize as Linux"]
    Windows["Categorize as Windows"]
    
    Job --> CheckRunner
    CheckRunner --> IsWindows
    IsWindows -->|"Yes"| Windows
    IsWindows -->|"No"| Linux
```

**Implementation:**
- **Function:** `is_windows(job)` at [.github/actions/workflow-build/prepare-workflow-dispatch.py:21-22]()
- **Logic:** Returns `True` if `job['runner']` starts with `"windows"`, else `False`
- **Assumption:** All runners follow consistent naming conventions (e.g., `windows-cpu8`, `linux-amd64-gpu-v100-latest-1`)

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:21-22](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:42-57]()

---

### Job Categorization

The `split_workflow()` function performs a four-way categorization of all jobs:

| Category | Criteria | Target Workflow |
|----------|----------|-----------------|
| `linux_standalone` | Linux runner + standalone execution | `workflow-dispatch-standalone-group-linux` |
| `linux_two_stage` | Linux runner + producer/consumer pattern | `workflow-dispatch-two-stage-group-linux` |
| `windows_standalone` | Windows runner + standalone execution | `workflow-dispatch-standalone-group-windows` |
| `windows_two_stage` | Windows runner + producer/consumer pattern | `workflow-dispatch-two-stage-group-windows` |

**Categorization Process:**

```mermaid
graph TB
    Start["For each group in workflow.json"]
    ExtractStandalone["Extract standalone[] array"]
    ExtractTwoStage["Extract two_stage[] array"]
    
    StandaloneCheck{"standalone[] not empty?"}
    StandaloneOS{"is_windows(standalone[0])?"}
    AddWinStandalone["Add to windows_standalone"]
    AddLinuxStandalone["Add to linux_standalone"]
    
    TwoStageCheck{"two_stage[] not empty?"}
    TwoStageOS{"is_windows(two_stage[0]['producers'][0])?"}
    AddWinTwoStage["Add to windows_two_stage"]
    AddLinuxTwoStage["Add to linux_two_stage"]
    
    Start --> ExtractStandalone
    Start --> ExtractTwoStage
    
    ExtractStandalone --> StandaloneCheck
    StandaloneCheck -->|"Yes"| StandaloneOS
    StandaloneOS -->|"Yes"| AddWinStandalone
    StandaloneOS -->|"No"| AddLinuxStandalone
    
    ExtractTwoStage --> TwoStageCheck
    TwoStageCheck -->|"Yes"| TwoStageOS
    TwoStageOS -->|"Yes"| AddWinTwoStage
    TwoStageOS -->|"No"| AddLinuxTwoStage
```

**Key Implementation Details:**
- Groups may contain only `standalone`, only `two_stage`, or both
- OS determination uses the first job in each array as representative (assumes all jobs in a group use the same OS)
- Two-stage OS detection examines the first producer job at [.github/actions/workflow-build/prepare-workflow-dispatch.py:54]()

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-72]()

---

### Stripping Extra Information

Before adding jobs to the dispatch structure, the script removes the `origin` field from each job object using the `strip_extra_info()` function. This field contains metadata about the job's source in `matrix.yaml` (useful during workflow generation for debugging and validation) but is not needed during dispatch and execution.

**Stripping Process:**

```mermaid
graph LR
    JobWithOrigin["Job Object<br/>{id, runner, command, origin, ...}"]
    StripFunction["strip_extra_info(job)"]
    JobWithoutOrigin["Job Object<br/>{id, runner, command, ...}"]
    
    JobWithOrigin --> StripFunction
    StripFunction --> JobWithoutOrigin
```

**Applied to:**
- All standalone jobs at [.github/actions/workflow-build/prepare-workflow-dispatch.py:40]()
- All producer jobs at [.github/actions/workflow-build/prepare-workflow-dispatch.py:50]()
- All consumer jobs at [.github/actions/workflow-build/prepare-workflow-dispatch.py:52]()

This reduces the size of `dispatch.json` and ensures execution workflows receive only the data they need.

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:31-52]()

---

## Output Structure: dispatch.json

The script writes a single JSON file at `workflow/dispatch.json` with a consistent structure containing four top-level keys.

### Schema

```json
{
  "linux_standalone": {
    "keys": ["group1", "group2", ...],
    "jobs": {
      "group1": [/* standalone job objects */],
      "group2": [/* standalone job objects */],
      ...
    }
  },
  "linux_two_stage": {
    "keys": ["group1", "group2", ...],
    "jobs": {
      "group1": [
        {
          "producers": [/* producer job objects */],
          "consumers": [/* consumer job objects */]
        },
        ...
      ],
      ...
    }
  },
  "windows_standalone": {
    "keys": [...],
    "jobs": {...}
  },
  "windows_two_stage": {
    "keys": [...],
    "jobs": {...}
  }
}
```

### Field Descriptions

| Field | Type | Purpose |
|-------|------|---------|
| `keys` | `string[]` | List of group names in this category, used for GitHub Actions matrix expansion |
| `jobs` | `object` | Dictionary mapping group names to job arrays (standalone) or two-stage chain arrays |

**Keys Array Usage:**
The `keys` array enables efficient matrix iteration in dispatch workflows:

```yaml
strategy:
  matrix:
    group: ${{ fromJSON(needs.build.outputs.linux_standalone_keys) }}
steps:
  - name: Get jobs for group
    run: |
      jobs=$(echo '${{ needs.build.outputs.linux_standalone_jobs }}' | jq -r '.["${{ matrix.group }}"]')
```

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:59-75]()

---

## Implementation Walkthrough

### Main Function

The entry point orchestrates the transformation process:

```mermaid
graph TB
    Start["main()"]
    ParseArgs["Parse command line arguments<br/>workflow_json path"]
    CheckFile{"workflow.json exists?"}
    ErrorExit["Print error<br/>sys.exit(1)"]
    LoadJSON["Load workflow.json"]
    SplitWorkflow["Call split_workflow(workflow)"]
    WriteOutput["Write workflow/dispatch.json"]
    
    Start --> ParseArgs
    ParseArgs --> CheckFile
    CheckFile -->|"No"| ErrorExit
    CheckFile -->|"Yes"| LoadJSON
    LoadJSON --> SplitWorkflow
    SplitWorkflow --> WriteOutput
```

**Key Steps:**
1. **Argument Parsing** [.github/actions/workflow-build/prepare-workflow-dispatch.py:78-81](): Accepts `workflow_json` path
2. **File Validation** [.github/actions/workflow-build/prepare-workflow-dispatch.py:84-86](): Exits with error if file not found
3. **JSON Loading** [.github/actions/workflow-build/prepare-workflow-dispatch.py:88-89](): Parses workflow.json
4. **Splitting** [.github/actions/workflow-build/prepare-workflow-dispatch.py:91](): Calls `split_workflow()`
5. **Output** [.github/actions/workflow-build/prepare-workflow-dispatch.py:74-75](): Creates `workflow/` directory and writes `dispatch.json`

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:78-95]()

---

### Data Flow Diagram

The following diagram illustrates how data structures transform through the script:

**Data Transformation Pipeline:**

```mermaid
graph TB
    Input["workflow.json<br/>{group1: {standalone: [...], two_stage: [...]}, ...}"]
    
    InitContainers["Initialize 4 empty dictionaries:<br/>linux_standalone, linux_two_stage,<br/>windows_standalone, windows_two_stage"]
    
    IterateGroups["For each (group_name, group_json)"]
    
    ProcessStandalone["Process standalone[] array:<br/>- Strip origin field<br/>- Determine OS<br/>- Add to appropriate dict"]
    
    ProcessTwoStage["Process two_stage[] array:<br/>- Strip origin from producers/consumers<br/>- Determine OS from first producer<br/>- Add to appropriate dict"]
    
    BuildDispatch["Build dispatch object:<br/>{<br/>  'linux_standalone': {keys: [...], jobs: {...}},<br/>  'linux_two_stage': {keys: [...], jobs: {...}},<br/>  'windows_standalone': {keys: [...], jobs: {...}},<br/>  'windows_two_stage': {keys: [...], jobs: {...}}<br/>}"]
    
    WriteFile["Write to workflow/dispatch.json"]
    
    Input --> InitContainers
    InitContainers --> IterateGroups
    IterateGroups --> ProcessStandalone
    IterateGroups --> ProcessTwoStage
    ProcessStandalone --> BuildDispatch
    ProcessTwoStage --> BuildDispatch
    BuildDispatch --> WriteFile
```

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-75]()

---

## Code Entity Reference

### Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `write_json_file(filename, json_object)` | [.github/actions/workflow-build/prepare-workflow-dispatch.py:16-18]() | Writes formatted JSON to file with 2-space indentation |
| `is_windows(job)` | [.github/actions/workflow-build/prepare-workflow-dispatch.py:21-22]() | Returns `True` if job targets Windows runner |
| `split_workflow(workflow)` | [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-75]() | Core processing logic; categorizes and writes dispatch.json |
| `strip_extra_info(job)` (nested) | [.github/actions/workflow-build/prepare-workflow-dispatch.py:31-32]() | Deletes `origin` field from job object (mutates in-place) |
| `main()` | [.github/actions/workflow-build/prepare-workflow-dispatch.py:78-91]() | Entry point; handles CLI and orchestrates execution |

### Data Structures

**Input: `workflow` (dict)**
- Keys: Group names (strings)
- Values: Objects with optional `standalone` and `two_stage` keys

**Output: `dispatch` (dict)**
- Keys: `'linux_standalone'`, `'linux_two_stage'`, `'windows_standalone'`, `'windows_two_stage'`
- Values: Objects with `'keys'` (list) and `'jobs'` (dict) fields

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:1-95]()

---

## Integration with Workflow Generation

The `prepare-workflow-dispatch.py` script is invoked by the `workflow-build` composite action as the final step of the generation pipeline:

**Execution Context:**

```mermaid
graph LR
    BuildWorkflow["build-workflow.py"]
    WorkflowJSON["workflow/workflow.json"]
    PrepareDispatch["prepare-workflow-dispatch.py"]
    DispatchJSON["workflow/dispatch.json"]
    DispatchWorkflows["Dispatch Group Workflows"]
    
    BuildWorkflow -->|"generates"| WorkflowJSON
    WorkflowJSON -->|"input to"| PrepareDispatch
    PrepareDispatch -->|"generates"| DispatchJSON
    DispatchJSON -->|"consumed by"| DispatchWorkflows
```

**Invocation:** The `workflow-build` action calls this script after `build-workflow.py` completes, passing the path to `workflow/workflow.json` as the command-line argument.

For details on how the workflow-build action orchestrates this, see [workflow-build Action](#3.4). For how dispatch workflows consume the output, see [Job Dispatch](#4).

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:1-8]()

---

## Example Transformation

Consider a simplified `workflow.json` with mixed OS and execution patterns:

**Input (workflow.json):**
```json
{
  "thrust": {
    "standalone": [
      {"id": "thrust-gcc10-cpu", "runner": "linux-amd64-cpu16", "origin": {...}},
      {"id": "thrust-msvc-cpu", "runner": "windows-cpu8", "origin": {...}}
    ]
  },
  "cub": {
    "two_stage": [
      {
        "producers": [{"id": "cub-build", "runner": "linux-amd64-gpu-v100-latest-1", "origin": {...}}],
        "consumers": [
          {"id": "cub-test-sm70", "runner": "linux-amd64-gpu-v100-latest-1", "origin": {...}},
          {"id": "cub-test-sm80", "runner": "linux-amd64-gpu-a100-latest-1", "origin": {...}}
        ]
      }
    ]
  }
}
```

**Output (dispatch.json):**
```json
{
  "linux_standalone": {
    "keys": ["thrust"],
    "jobs": {
      "thrust": [
        {"id": "thrust-gcc10-cpu", "runner": "linux-amd64-cpu16"}
      ]
    }
  },
  "linux_two_stage": {
    "keys": ["cub"],
    "jobs": {
      "cub": [
        {
          "producers": [{"id": "cub-build", "runner": "linux-amd64-gpu-v100-latest-1"}],
          "consumers": [
            {"id": "cub-test-sm70", "runner": "linux-amd64-gpu-v100-latest-1"},
            {"id": "cub-test-sm80", "runner": "linux-amd64-gpu-a100-latest-1"}
          ]
        }
      ]
    }
  },
  "windows_standalone": {
    "keys": ["thrust"],
    "jobs": {
      "thrust": [
        {"id": "thrust-msvc-cpu", "runner": "windows-cpu8"}
      ]
    }
  },
  "windows_two_stage": {
    "keys": [],
    "jobs": {}
  }
}
```

Notice:
- `origin` fields removed from all jobs
- Linux and Windows standalone jobs separated into different categories
- Two-stage structure preserved but categorized by producer OS
- Empty categories still present in output (with empty `keys` and `jobs`)

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-75]()

---

# Page: Generated Artifacts

# Generated Artifacts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)
- [.github/actions/workflow-build/prepare-workflow-dispatch.py](.github/actions/workflow-build/prepare-workflow-dispatch.py)

</details>



## Purpose and Scope

This page documents the structure and content of the JSON artifacts produced by the workflow generation pipeline. These artifacts are intermediate outputs that bridge the gap between the human-readable `matrix.yaml` configuration and the GitHub Actions workflows that execute jobs.

For information about how these artifacts are created, see [build-workflow.py Pipeline](#3.1) and [Dispatch Preparation](#3.2). For information about how these artifacts are consumed, see [Job Dispatch](#4).

## Overview

The workflow generation pipeline produces five primary artifacts in the `workflow/` directory:

| Artifact | Purpose | Producer |
|----------|---------|----------|
| `workflow.json` | Complete workflow with all dispatch groups and job specifications | `build-workflow.py` |
| `job_ids.json` | Maps compact job IDs to human-readable full names | `build-workflow.py` |
| `job_list.txt` | Human-readable enumeration of all jobs | `build-workflow.py` |
| `runner_summary.json` | Runner allocation statistics and counts | `build-workflow.py` |
| `dispatch.json` | Workflow reorganized by OS and execution pattern | `prepare-workflow-dispatch.py` |

**Sources:** [.github/actions/workflow-build/build-workflow.py:979-1024](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-76]()

## Artifact Generation Flow

```mermaid
graph TB
    subgraph Input
        MatrixYAML["matrix.yaml"]
    end
    
    subgraph "build-workflow.py"
        ProcessPipeline["parse_workflow_dispatch_groups()"]
        Finalize["finalize_workflow_dispatch_groups()"]
        WriteOutputs["write_outputs()"]
    end
    
    subgraph "Primary Artifacts"
        WorkflowJSON["workflow.json<br/>(complete workflow)"]
        JobIDsJSON["job_ids.json<br/>(ID mappings)"]
        JobListTXT["job_list.txt<br/>(human-readable)"]
        RunnerSummaryJSON["runner_summary.json<br/>(statistics)"]
    end
    
    subgraph "prepare-workflow-dispatch.py"
        SplitWorkflow["split_workflow()"]
    end
    
    subgraph "Secondary Artifacts"
        DispatchJSON["dispatch.json<br/>(4 OS/pattern splits)"]
    end
    
    MatrixYAML --> ProcessPipeline
    ProcessPipeline --> Finalize
    Finalize --> WriteOutputs
    
    WriteOutputs --> WorkflowJSON
    WriteOutputs --> JobIDsJSON
    WriteOutputs --> JobListTXT
    WriteOutputs --> RunnerSummaryJSON
    
    WorkflowJSON --> SplitWorkflow
    SplitWorkflow --> DispatchJSON
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:979-1024](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:78-95]()

## workflow.json Structure

The `workflow.json` file contains the complete workflow specification organized into dispatch groups. Each dispatch group represents a logical collection of jobs with shared characteristics (project, CTK version, compiler).

### Schema

```mermaid
graph TB
    subgraph "workflow.json"
        Root["{ dispatch_groups }"]
    end
    
    subgraph "Dispatch Group"
        GroupName["'Group Name': { }"]
        Standalone["standalone: [ job_json, ... ]"]
        TwoStage["two_stage: [ two_stage_json, ... ]"]
    end
    
    subgraph "job_json"
        JobID["id: 'AB'"]
        JobName["name: '[config] Job(runner)'"]
        JobRunner["runner: 'linux-amd64-cpu16'"]
        JobImage["image: 'rapidsai/devcontainers:...'"]
        JobCommand["command: './ci/test_libcudacxx.sh ...'"]
        JobCuda["cuda: '11.1'"]
        JobHost["host: 'gcc12'"]
    end
    
    subgraph "two_stage_json"
        TwoStageID["id: 'CD'"]
        Producers["producers: [ job_json ]"]
        Consumers["consumers: [ job_json, ... ]"]
    end
    
    Root --> GroupName
    GroupName --> Standalone
    GroupName --> TwoStage
    
    Standalone --> JobID
    TwoStage --> TwoStageID
    TwoStage --> Producers
    TwoStage --> Consumers
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:28-53](), [.github/actions/workflow-build/build-workflow.py:507-544]()

### Dispatch Group Names

Dispatch group names are generated by `generate_dispatch_group_name()` and follow the pattern:

```
<Project Name> CTK<version> <Compiler Info>
```

Examples:
- `libcudacxx CTK11.1 nvcc GCC`
- `Thrust CTK12.0 clang`

**Sources:** [.github/actions/workflow-build/build-workflow.py:345-359]()

### Job JSON Fields

Each `job_json` object contains the following fields:

| Field | Type | Description | Generator Function |
|-------|------|-------------|-------------------|
| `id` | string | Compact unique ID (1-3 chars) | `next(guid_generator)` |
| `name` | string | Human-readable job name | `generate_dispatch_job_name()` |
| `runner` | string | GitHub Actions runner label | `generate_dispatch_job_runner()` |
| `image` | string | Docker image reference | `generate_dispatch_job_image()` |
| `command` | string | Shell command to execute | `generate_dispatch_job_command()` |
| `cuda` | string | CTK version for devcontainer | `generate_dispatch_job_ctk_version()` |
| `host` | string | Host compiler for devcontainer | `generate_dispatch_job_host_compiler()` |

The `origin` field present during generation is stripped before final output by `prepare-workflow-dispatch.py`.

**Sources:** [.github/actions/workflow-build/build-workflow.py:481-490](), [.github/actions/workflow-build/build-workflow.py:362-445]()

### Job Name Format

Job names generated by `generate_dispatch_job_name()` follow this format:

```
[<C++std> <compiler><version>] <JobType>(<cpu>, <gpu>):<sm{arch}><cmake_options>
```

Example: `[C++17 gcc12] Test(amd64, T4): sm{75}`

**Sources:** [.github/actions/workflow-build/build-workflow.py:362-376]()

### Two-Stage JSON Structure

Two-stage jobs contain exactly one producer and one or more consumers:

```json
{
  "id": "AB",
  "producers": [
    { "id": "CD", "name": "...", "runner": "...", ... }
  ],
  "consumers": [
    { "id": "EF", "name": "...", "runner": "...", ... },
    { "id": "GH", "name": "...", "runner": "...", ... }
  ]
}
```

The single-producer constraint is validated by `finalize_workflow_dispatch_groups()`.

**Sources:** [.github/actions/workflow-build/build-workflow.py:493-504](), [.github/actions/workflow-build/build-workflow.py:586-599]()

## job_ids.json Structure

The `job_ids.json` file maps compact job IDs to full human-readable names for debugging and reporting purposes.

### Schema

```json
{
  "AB": "libcudacxx CTK11.1 nvcc GCC [C++17 gcc12] Test(amd64, T4)",
  "CD": "Thrust CTK12.0 clang [C++20 clang16] Build(amd64)",
  ...
}
```

The mapping is constructed during `write_outputs()` and combines the dispatch group name with the job name.

**Sources:** [.github/actions/workflow-build/build-workflow.py:979-1024]()

## job_list.txt Structure

The `job_list.txt` file provides a human-readable enumeration of all jobs, organized hierarchically by dispatch group. This is primarily used for debugging and manual inspection.

### Format

```
     <Dispatch Group Name>:
   1 id: AB     standalone     [config] Job(runner)
   2 id: CD     producers      [config] Job(runner)
   3 id: EF     consumers      [config] Job(runner)
   4 id: GH     consumers      [config] Job(runner)
     <Next Dispatch Group>:
   5 id: IJ     standalone     [config] Job(runner)
   ...
```

The enumeration includes sequential job numbers, job IDs, job type (standalone/producers/consumers), and full job names.

**Sources:** [.github/actions/workflow-build/build-workflow.py:986-1005]()

## runner_summary.json Structure

The `runner_summary.json` file contains aggregate statistics about runner allocation across all jobs.

### Schema

```json
{
  "heading": "🏃‍ Runner counts (total jobs: 142)",
  "body": "| #    | Runner\n|------|------\n|  45  | `linux-amd64-cpu16`\n|  32  | `linux-amd64-gpu-t4-latest-1`\n..."
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `heading` | string | Summary heading with total job count |
| `body` | string | Markdown table of runner counts (sorted descending) |

The runner counts are accumulated in `process_job_array()` and formatted as a markdown table.

**Sources:** [.github/actions/workflow-build/build-workflow.py:986-1023]()

## dispatch.json Structure

The `dispatch.json` file reorganizes the complete workflow into four categories based on operating system and execution pattern. This split optimizes GitHub Actions UI by avoiding large numbers of skipped jobs.

### High-Level Structure

```mermaid
graph TB
    subgraph "dispatch.json"
        Root["{ 4 categories }"]
    end
    
    subgraph Categories
        LinuxSA["linux_standalone"]
        LinuxTS["linux_two_stage"]
        WindowsSA["windows_standalone"]
        WindowsTS["windows_two_stage"]
    end
    
    subgraph "Category Structure"
        Keys["keys: [ group_name, ... ]"]
        Jobs["jobs: { group_name: jobs_array }"]
    end
    
    Root --> LinuxSA
    Root --> LinuxTS
    Root --> WindowsSA
    Root --> WindowsTS
    
    LinuxSA --> Keys
    LinuxSA --> Jobs
```

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-76]()

### Category Schema

Each of the four categories has identical structure:

```json
{
  "linux_standalone": {
    "keys": ["Group A", "Group B", ...],
    "jobs": {
      "Group A": [ job_json, ... ],
      "Group B": [ job_json, ... ],
      ...
    }
  },
  "linux_two_stage": {
    "keys": ["Group C", ...],
    "jobs": {
      "Group C": [ two_stage_json, ... ],
      ...
    }
  },
  ...
}
```

The `keys` array provides group names in a format suitable for GitHub Actions matrix strategies, while `jobs` contains the actual job specifications.

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:59-75]()

### OS Detection

Jobs are categorized as Windows or Linux based on the runner field. The `is_windows()` function checks if the runner string starts with `"windows"`:

```python
def is_windows(job):
    return job['runner'].startswith('windows')
```

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:21-23]()

### Origin Field Stripping

The `split_workflow()` function removes the `origin` field from all jobs via `strip_extra_info()`. This field contains metadata used during generation (file locations, original matrix job specifications) but is not needed for execution.

**Sources:** [.github/actions/workflow-build/prepare-workflow-dispatch.py:31-52]()

## GUID Generation

All job IDs and two-stage IDs are assigned using a compact GUID generator that produces 1-3 character base64-encoded strings.

### GUID Algorithm

```mermaid
graph LR
    Counter["Counter: 0-65535"]
    Pack["struct.pack('>H', i)"]
    Base64["base64.b64encode()"]
    Strip["Strip 'A' prefix and '=' suffix"]
    GUID["GUID: 1-3 chars"]
    
    Counter --> Pack
    Pack --> Base64
    Base64 --> Strip
    Strip --> GUID
```

The generator produces up to 65,535 unique IDs before exhaustion. Examples: `"B"`, `"AB"`, `"QQ"`, `"ZYX"`.

**Sources:** [.github/actions/workflow-build/build-workflow.py:78-96]()

### GUID Assignment

GUIDs are assigned to jobs during `finalize_workflow_dispatch_groups()` after all merging and deduplication is complete:

- Standalone jobs receive individual IDs
- Two-stage job chains receive one ID for the chain itself
- Each producer and consumer within a two-stage chain receives individual IDs

**Sources:** [.github/actions/workflow-build/build-workflow.py:708-720]()

## Finalization Process

The `finalize_workflow_dispatch_groups()` function performs several critical transformations before artifacts are written:

### Deduplication and Merging

```mermaid
graph TB
    Input["Input: workflow_dispatch_groups"]
    
    ValidateProducers["Validate single producer per chain"]
    MergeConsumers["Merge consumers for duplicate producers"]
    DedupeStandalone["Remove duplicate standalone jobs"]
    RemoveOverlaps["Remove standalone/two-stage overlaps"]
    WarnDuplicates["Warn about remaining duplicates"]
    RemoveEmpty["Remove empty groups"]
    Sort["Sort groups and jobs naturally"]
    AssignGUIDs["Assign GUIDs"]
    
    Output["Output: finalized workflow"]
    
    Input --> ValidateProducers
    ValidateProducers --> MergeConsumers
    MergeConsumers --> DedupeStandalone
    DedupeStandalone --> RemoveOverlaps
    RemoveOverlaps --> WarnDuplicates
    WarnDuplicates --> RemoveEmpty
    RemoveEmpty --> Sort
    Sort --> AssignGUIDs
    AssignGUIDs --> Output
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:583-721]()

### Job Comparison

Jobs are compared using `compare_dispatch_jobs()`, which considers only:
- `name`
- `runner`
- `image`
- `command`

The `origin` field is explicitly ignored to allow jobs from different matrix specifications to be identified as duplicates.

**Sources:** [.github/actions/workflow-build/build-workflow.py:557-571]()

### Natural Sorting

Groups and jobs are sorted using natural sort keys that handle embedded numbers correctly (e.g., "CTK11" before "CTK12" rather than lexicographic "CTK12" before "CTK11").

**Sources:** [.github/actions/workflow-build/build-workflow.py:693-707]()

## File Output Locations

All artifacts are written to the `workflow/` directory relative to the execution location:

```
workflow/
├── workflow.json          # Complete workflow specification
├── job_ids.json          # ID to name mappings
├── job_list.txt          # Human-readable enumeration
├── runner_summary.json   # Runner allocation statistics
└── dispatch.json         # OS/pattern categorized workflow
```

The directory is created by `write_outputs()` if it does not exist.

**Sources:** [.github/actions/workflow-build/build-workflow.py:1019-1023](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:74-75]()

---

# Page: workflow-build Action

# workflow-build Action

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)

</details>



## Purpose and Scope

The `workflow-build` action is a composite GitHub Action that orchestrates the workflow generation pipeline, transforming a human-readable `matrix.yaml` configuration into executable job definitions organized for optimal GitHub Actions execution. This action coordinates the execution of Python scripts, handles change detection, manages artifact uploads, and sends Slack notifications throughout the generation process.

For information about the underlying matrix configuration format, see [Configuration Guide](#2). For details on the Python scripts orchestrated by this action, see [build-workflow.py Pipeline](#3.1) and [Dispatch Preparation](#3.2).

**Sources:** [.github/actions/workflow-build/action.yml:1-3]()

---

## Action Location and Type

The workflow-build action is implemented as a composite action located at `.github/actions/workflow-build/action.yml`. Composite actions execute multiple steps within a single action definition, allowing the orchestration of shell scripts, Python executables, and external actions without requiring a separate Docker container or JavaScript runtime.

**Sources:** [.github/actions/workflow-build/action.yml:43-44]()

---

## Inputs

The action accepts multiple inputs that control workflow generation behavior, change detection, and notification settings.

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `workflows` | Yes | - | Space-separated list of workflow names from matrix file to run (e.g., `"pull_request nightly"`) |
| `allow_override` | No | `"false"` | If `"true"`, honors the `override` workflow in matrix file, ignoring requested workflows |
| `inspect_changes_script` | No | `""` | Path to script that determines which projects need testing based on file changes |
| `inspect_changes_base_sha` | No | `""` | Base commit SHA for change detection comparison |
| `matrix_file` | No | `"ci/matrix.yaml"` | Path to matrix configuration file in consumer repository |
| `matrix_parser` | No | `""` | Path to custom matrix parser script; defaults to `build-workflow.py` from action directory |
| `slack_token` | No | - | Slack bot token for sending notifications; notifications disabled if not provided |
| `slack_log` | No | - | Slack channel ID for verbose log notifications |
| `slack_alert` | No | - | Slack channel ID for error/alert notifications |

**Sources:** [.github/actions/workflow-build/action.yml:4-36]()

---

## Outputs

The action produces a single output containing all dispatchable job definitions.

| Output | Description |
|--------|-------------|
| `workflow` | JSON string containing the `dispatch.json` structure with jobs organized by OS and execution pattern |

The output value is read from `workflow/dispatch.json` and exposed as a GitHub Actions output for downstream workflow consumption.

**Sources:** [.github/actions/workflow-build/action.yml:38-41](), [.github/actions/workflow-build/action.yml:111-117]()

---

## Execution Flow

The following diagram illustrates the sequential execution of steps within the workflow-build action, showing how data flows from inputs through processing stages to outputs.

```mermaid
graph TB
    subgraph Inputs["Action Inputs"]
        I1["workflows"]
        I2["matrix_file"]
        I3["inspect_changes_script"]
        I4["slack_token"]
    end
    
    subgraph Step1["Step: Send Slack log notification"]
        S1A["Check: slack_token != ''<br/>AND slack_log != ''"]
        S1B["slackapi/slack-github-action@v1.26.0"]
        S1C["Post: Workflow starting message"]
    end
    
    subgraph Step2["Step: Inspect changes"]
        S2A["Check: inspect_changes_script != ''<br/>AND inspect_changes_base_sha != ''"]
        S2B["Execute inspect-changes script"]
        S2C["Output: dirty_projects"]
        S2D["Export changes.md to workflow/"]
    end
    
    subgraph Step3["Step: Parse matrix file"]
        S3A["Execute matrix_parser<br/>(build-workflow.py)"]
        S3B["Pass --workflows flag"]
        S3C["Pass --allow-override if enabled"]
        S3D["Pass --dirty-projects if available"]
        S3E["Generate workflow/workflow.json"]
        S3F["Generate workflow/job_ids.json"]
        S3G["Generate workflow/runner_summary.json"]
    end
    
    subgraph Step4["Step: Create dispatch workflows"]
        S4A["Execute prepare-workflow-dispatch.py"]
        S4B["Read workflow/workflow.json"]
        S4C["Generate workflow/dispatch.json"]
    end
    
    subgraph Step5["Step: Set outputs"]
        S5A["Read workflow/dispatch.json"]
        S5B["Set WORKFLOW output"]
    end
    
    subgraph Step6["Step: Upload artifacts"]
        S6A["actions/upload-artifact@v4"]
        S6B["Upload workflow/ directory"]
        S6C["Artifact name: workflow"]
    end
    
    subgraph Step7["Step: Send Slack error notification"]
        S7A["Check: failure() AND slack_token<br/>AND (slack_alert OR slack_log)"]
        S7B["slackapi/slack-github-action@v1.26.0"]
        S7C["Post: Error message to channels"]
    end
    
    I1 --> S1A
    I4 --> S1A
    S1A -->|conditions met| S1B --> S1C
    
    I3 --> S2A
    S2A -->|conditions met| S2B --> S2C --> S2D
    
    I2 --> S3A
    I1 --> S3B
    S2C -.->|optional| S3D
    S3A --> S3E
    S3A --> S3F
    S3A --> S3G
    
    S3E --> S4B
    S4A --> S4B
    S4B --> S4C
    
    S4C --> S5A --> S5B
    
    S3E --> S6B
    S3F --> S6B
    S3G --> S6B
    S2D -.-> S6B
    S6A --> S6B --> S6C
    
    S5B -.->|on failure| S7A
    S6C -.->|on failure| S7A
    S7A -->|conditions met| S7B --> S7C
```

**Sources:** [.github/actions/workflow-build/action.yml:45-140]()

---

## Step 1: Send Slack Log Notification

The first step sends an initial notification to the Slack log channel indicating that workflow generation has started. This step is conditional and only executes when both `slack_token` and `slack_log` inputs are provided.

### Conditional Execution

```yaml
if: ${{inputs.slack_token != '' && inputs.slack_log != '' }}
```

The condition checks for non-empty string values. If either input is missing or empty, the step is skipped.

### Message Content

The Slack message includes:
- The workflow type (derived from `github.workflow` context variable, e.g., `pull_request`, `nightly`)
- A direct link to the GitHub Actions run summary page

### Environment Variables

- `SLACK_BOT_TOKEN`: Authentication token for Slack API
- `WORKFLOW_TYPE`: Name of the triggering workflow
- `SUMMARY_URL`: Constructed GitHub Actions run URL

**Sources:** [.github/actions/workflow-build/action.yml:47-59]()

---

## Step 2: Inspect Changes

The inspect changes step executes a user-provided script to determine which projects or dependencies have been modified, enabling selective job execution for efficiency.

### Conditional Execution

```yaml
if: ${{ inputs.inspect_changes_script != '' && inputs.inspect_changes_base_sha != '' }}
```

Both the script path and base SHA must be provided for this step to execute. This is typically used in pull request contexts where comparing the PR branch against the base branch is meaningful.

### Script Execution

The inspect-changes script is invoked with two arguments:
1. Base commit SHA (from `inputs.inspect_changes_base_sha`)
2. Current HEAD commit SHA (from `GITHUB_SHA` environment variable)

The script is expected to:
- Analyze git diff between the two commits
- Identify modified files relevant to the build system
- Determine which projects are "dirty" (need rebuilding)
- Output `dirty_projects` as a step output
- Write a summary to `GITHUB_STEP_SUMMARY`

### Output Capture

The step captures the `dirty_projects` output (typically a space-separated list of project names) using the step ID `inspect-changes`. This output is consumed by the matrix parser in Step 3.

### Artifact Preparation

The step copies the GitHub Step Summary to `workflow/changes.md` for inclusion in the final artifact upload, preserving the change detection report.

**Sources:** [.github/actions/workflow-build/action.yml:61-72]()

---

## Step 3: Parse Matrix File

This is the core workflow generation step that transforms the matrix configuration into a complete job definition set.

### Matrix Parser Selection

The action uses the `matrix_parser` input to determine which script to execute. If not provided, it defaults to `build-workflow.py` located in the action's own directory:

```bash
matrix_parser: ${{ inputs.matrix_parser && inputs.matrix_parser || '${GITHUB_ACTION_PATH}/build-workflow.py' }}
```

The `GITHUB_ACTION_PATH` environment variable is automatically set by GitHub Actions to point to the action's directory.

### Command Construction

The parser is invoked with the following arguments:

```bash
${{ env.matrix_parser }} ${{ inputs.matrix_file }}
    --workflows ${{ inputs.workflows }}
    ${{ env.allow_override }}
    ${{ env.dirty_projects_flag }} ${{ env.dirty_projects }}
```

#### Flag Processing

The action uses bash parameter expansion and conditional logic to construct optional flags:

- `allow_override`: Set to `--allow-override` if `inputs.allow_override == 'true'`, otherwise empty
- `dirty_projects_flag`: Set to `--dirty-projects` if `inspect_changes_script` input is provided, otherwise empty
- `dirty_projects`: Set to the output from Step 2 if available, otherwise empty

### Generated Outputs

The script generates multiple files in the `workflow/` directory:

| File | Description |
|------|-------------|
| `workflow.json` | Complete job definitions with all tags and parameters |
| `job_ids.json` | Mapping between job names and internal IDs |
| `runner_summary.json` | Runner allocation statistics and summary |
| `job_list.txt` | Human-readable list of all jobs |

### Console Output

The step uses GitHub Actions log groups to organize output:

- **Workflow**: Contents of `workflow.json`
- **Runners**: Formatted runner summary (also appended to `GITHUB_STEP_SUMMARY`)
- **Job List**: Contents of `job_list.txt`

**Sources:** [.github/actions/workflow-build/action.yml:74-101]()

---

## Step 4: Create Dispatch Workflows

This step transforms the complete `workflow.json` into optimized dispatch groups organized by operating system and execution pattern.

### Script Execution

The `prepare-workflow-dispatch.py` script is invoked directly from the action's directory:

```bash
"${GITHUB_ACTION_PATH}/prepare-workflow-dispatch.py" workflow/workflow.json
```

### Output Structure

The script generates `workflow/dispatch.json` with the following structure:

```json
{
  "linux_standalone": [...],
  "linux_two_stage": [...],
  "windows_standalone": [...],
  "windows_two_stage": [...]
}
```

Each array contains job definitions or producer/consumer chain definitions suitable for GitHub Actions matrix strategies.

### Console Output

The dispatch JSON is displayed in a log group for verification before proceeding to output generation.

**Sources:** [.github/actions/workflow-build/action.yml:102-109]()

---

## Step 5: Set Outputs

This step reads the generated `dispatch.json` and exposes it as a GitHub Actions output variable for consumption by downstream workflows.

### Output Format

The entire dispatch JSON is compacted (using `jq -c`) and set as the `WORKFLOW` output:

```bash
printf "WORKFLOW=%s\n" "$(cat workflow/dispatch.json | jq -c '.')" | tee -a "${GITHUB_OUTPUT}"
```

The `-c` flag ensures JSON is on a single line without whitespace, which is required for GitHub Actions output variables.

### Output Reference

Downstream workflows access this output using:

```yaml
${{ steps.workflow-build.outputs.workflow }}
```

The output is referenced by the step ID `outputs` and the output name `WORKFLOW`, which is mapped to the action-level output name `workflow` through the output definition.

**Sources:** [.github/actions/workflow-build/action.yml:111-117]()

---

## Step 6: Upload Artifacts

All generated files in the `workflow/` directory are uploaded as a GitHub Actions artifact for later retrieval and debugging.

### Artifact Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `name` | `workflow` | Artifact identifier used for download |
| `path` | `workflow/` | Directory containing all generated files |
| `compression-level` | `0` | No compression for faster upload/download |

### Artifact Contents

The uploaded artifact includes:

- `workflow.json`: Full job definitions
- `dispatch.json`: Dispatch-optimized job groups
- `job_ids.json`: Job ID mappings
- `runner_summary.json`: Runner statistics
- `job_list.txt`: Human-readable job list
- `changes.md`: Change detection summary (if Step 2 executed)

### Access from Other Jobs

Other jobs in the workflow can download these artifacts using:

```yaml
- uses: actions/download-artifact@v4
  with:
    name: workflow
```

**Sources:** [.github/actions/workflow-build/action.yml:119-124]()

---

## Step 7: Send Slack Error Notification

This conditional step sends an error notification to Slack channels if any previous step fails.

### Conditional Execution

```yaml
if: ${{ failure() && inputs.slack_token != '' && (inputs.slack_alert != '' || inputs.slack_log != '') }}
```

The step executes only when:
1. Any previous step has failed (`failure()` context check)
2. `slack_token` is provided
3. At least one of `slack_alert` or `slack_log` is provided

### Channel Selection Logic

The action constructs a channel list dynamically:

```yaml
channel-id: '${{ inputs.slack_log }}${{env.CHANNEL_SEP}}${{ inputs.slack_alert }}'
```

Where `CHANNEL_SEP` is a comma if both channels are provided, otherwise empty:

```yaml
CHANNEL_SEP: ${{ (inputs.slack_log != '' && inputs.slack_alert != '') && ',' || ''}}
```

This allows sending to:
- Only `slack_log` if `slack_alert` is not provided
- Only `slack_alert` if `slack_log` is not provided
- Both channels (comma-separated) if both are provided

### Error Message

The notification includes:
- Workflow type that encountered the error
- Direct link to the GitHub Actions run for investigation

**Sources:** [.github/actions/workflow-build/action.yml:126-139]()

---

## Integration with Workflow Generation Pipeline

The workflow-build action serves as the orchestration entry point for the workflow generation phase, as illustrated in the system architecture diagrams. The following diagram shows its relationship to other components:

```mermaid
graph TB
    subgraph Consumer["Consumer Workflow"]
        Trigger["Workflow Trigger<br/>(pull_request, schedule, etc.)"]
        UseAction["Step: uses<br/>NVIDIA/cccl-gha/.github/actions/workflow-build"]
        ConsumeOutput["Access: steps.*.outputs.workflow"]
    end
    
    subgraph ActionImpl["workflow-build Action"]
        ActionYAML["action.yml"]
        InspectScript["inspect-changes script<br/>(consumer-provided)"]
        BuildWorkflow["build-workflow.py<br/>(action-provided)"]
        PrepareDispatch["prepare-workflow-dispatch.py<br/>(action-provided)"]
    end
    
    subgraph Inputs["Configuration Inputs"]
        MatrixFile["matrix.yaml<br/>(consumer repo)"]
        WorkflowsFlag["workflows input"]
        ChangesConfig["inspect_changes_script<br/>inspect_changes_base_sha"]
    end
    
    subgraph Outputs["Generated Artifacts"]
        WorkflowJSON["workflow.json"]
        DispatchJSON["dispatch.json"]
        JobIDsJSON["job_ids.json"]
        RunnerSummary["runner_summary.json"]
    end
    
    subgraph NextStage["Dispatch Layer"]
        StandaloneLinux["workflow-dispatch-standalone-group-linux"]
        TwoStageLinux["workflow-dispatch-two-stage-group-linux"]
        StandaloneWindows["workflow-dispatch-standalone-group-windows"]
        TwoStageWindows["workflow-dispatch-two-stage-group-windows"]
    end
    
    Trigger --> UseAction
    MatrixFile --> ActionYAML
    WorkflowsFlag --> ActionYAML
    ChangesConfig -.-> ActionYAML
    
    UseAction --> ActionYAML
    ActionYAML --> InspectScript
    InspectScript -.->|dirty_projects| BuildWorkflow
    ActionYAML --> BuildWorkflow
    BuildWorkflow --> WorkflowJSON
    BuildWorkflow --> JobIDsJSON
    BuildWorkflow --> RunnerSummary
    
    ActionYAML --> PrepareDispatch
    WorkflowJSON --> PrepareDispatch
    PrepareDispatch --> DispatchJSON
    
    DispatchJSON --> ConsumeOutput
    ConsumeOutput -->|linux_standalone array| StandaloneLinux
    ConsumeOutput -->|linux_two_stage array| TwoStageLinux
    ConsumeOutput -->|windows_standalone array| StandaloneWindows
    ConsumeOutput -->|windows_two_stage array| TwoStageWindows
```

**Sources:** [.github/actions/workflow-build/action.yml:1-140]()

---

## Shell Configuration

All shell steps in the action use a consistent shell configuration for bash:

```yaml
shell: bash --noprofile --norc -euo pipefail {0}
```

This configuration ensures:
- `--noprofile --norc`: Skip profile/rc files for reproducible environment
- `-e`: Exit immediately if any command fails
- `-u`: Treat unset variables as errors
- `-o pipefail`: Return failure if any command in a pipeline fails

The `{0}` placeholder is replaced by GitHub Actions with the script content.

**Sources:** [.github/actions/workflow-build/action.yml:64](), [.github/actions/workflow-build/action.yml:76](), [.github/actions/workflow-build/action.yml:103](), [.github/actions/workflow-build/action.yml:113]()

---

## Error Handling Strategy

The workflow-build action employs a fail-fast strategy where any step failure causes immediate workflow termination (except for the Slack notification steps, which are conditional on failure). This ensures:

1. Downstream dispatch workflows do not execute with incomplete or corrupted job definitions
2. Slack notifications alert developers to generation failures before any jobs attempt to execute
3. Artifact uploads still occur even if notifications fail

The action does not use `continue-on-error: true` on generation steps, as invalid workflow definitions would cause cryptic errors in later stages. Fast failure with clear error messages at the generation stage improves debuggability.

**Sources:** [.github/actions/workflow-build/action.yml:126-139]()

---

## Usage Example

The following example demonstrates typical usage of the workflow-build action in a consumer repository:

```yaml
name: Pull Request CI

on:
  pull_request:
    branches: [main]

jobs:
  generate-workflow:
    runs-on: ubuntu-latest
    outputs:
      WORKFLOW: ${{ steps.build.outputs.workflow }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for change detection
      
      - uses: NVIDIA/cccl-gha/.github/actions/workflow-build@main
        id: build
        with:
          workflows: "pull_request"
          allow_override: "true"
          inspect_changes_script: "./ci/inspect-changes.sh"
          inspect_changes_base_sha: ${{ github.event.pull_request.base.sha }}
          matrix_file: "ci/matrix.yaml"
          slack_token: ${{ secrets.SLACK_BOT_TOKEN }}
          slack_log: ${{ secrets.SLACK_LOG_CHANNEL }}
          slack_alert: ${{ secrets.SLACK_ALERT_CHANNEL }}
```

This configuration:
- Runs on pull request events
- Checks out the full git history for change detection
- Enables override workflow support
- Provides a custom inspect-changes script
- Uses PR base commit for change comparison
- Sends Slack notifications on start and error

**Sources:** [.github/actions/workflow-build/action.yml:4-36]()

---

# Page: Job Dispatch

# Job Dispatch

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/workflow-dispatch-standalone-group-linux.yml](.github/workflows/workflow-dispatch-standalone-group-linux.yml)
- [.github/workflows/workflow-dispatch-standalone-group-windows.yml](.github/workflows/workflow-dispatch-standalone-group-windows.yml)
- [.github/workflows/workflow-dispatch-two-stage-group-linux.yml](.github/workflows/workflow-dispatch-two-stage-group-linux.yml)
- [.github/workflows/workflow-dispatch-two-stage-group-windows.yml](.github/workflows/workflow-dispatch-two-stage-group-windows.yml)

</details>



## Purpose and Scope

The Job Dispatch layer is responsible for distributing jobs from `dispatch.json` to appropriate execution environments using GitHub Actions matrix strategies. This layer acts as an intermediary between workflow generation (see [Workflow Generation](#3)) and actual job execution (see [Job Execution](#5)).

The dispatch system reads categorized job definitions from `dispatch.json` and spawns parallel GitHub Actions jobs based on operating system (Linux/Windows) and execution pattern (standalone/two-stage). Each dispatch workflow uses GitHub Actions' matrix feature to parallelize job execution while maintaining the correct dependency ordering for two-stage producer/consumer chains.

For details on specific execution patterns, see [Standalone Job Dispatch](#4.1), [Two-Stage Job Dispatch](#4.2), and [Producer-Consumer Pattern](#4.3).

---

## Dispatch Architecture Overview

The dispatch layer consists of four group dispatch workflows that consume `dispatch.json` and route jobs to execution workflows:

```mermaid
graph TB
    subgraph "dispatch.json Categories"
        DJ["dispatch.json"]
        LS["linux_standalone"]
        LT["linux_two_stage"]
        WS["windows_standalone"]
        WT["windows_two_stage"]
        
        DJ --> LS
        DJ --> LT
        DJ --> WS
        DJ --> WT
    end
    
    subgraph "Group Dispatch Workflows"
        LSGW["workflow-dispatch-standalone-group-linux.yml"]
        LTGW["workflow-dispatch-two-stage-group-linux.yml"]
        WSGW["workflow-dispatch-standalone-group-windows.yml"]
        WTGW["workflow-dispatch-two-stage-group-windows.yml"]
        
        LS -->|job-array| LSGW
        LT -->|pc-array| LTGW
        WS -->|job-array| WSGW
        WT -->|pc-array| WTGW
    end
    
    subgraph "Execution Layer"
        RJL["workflow-run-job-linux"]
        TSTL["workflow-dispatch-two-stage-linux.yml"]
        RJW["workflow-run-job-windows"]
        TSTW["workflow-dispatch-two-stage-windows.yml"]
        
        LSGW -->|matrix.include| RJL
        LTGW -->|matrix.include| TSTL
        WSGW -->|matrix.include| RJW
        WTGW -->|matrix.include| TSTW
    end
    
    TSTL -.->|producers/consumers| RJL
    TSTW -.->|producers/consumers| RJW
```

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml](), [.github/workflows/workflow-dispatch-two-stage-group-linux.yml](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml]()

---

## Dispatch.json Structure

The `dispatch.json` file is generated by `prepare-workflow-dispatch.py` and contains four top-level keys corresponding to the four dispatch workflows. Each category contains jobs organized by group name:

| Category | Structure | Content |
|----------|-----------|---------|
| `linux_standalone` | `jobs.<group-name>[array]` | Standalone Linux jobs |
| `linux_two_stage` | `jobs.<group-name>[array]` | Producer/consumer chains for Linux |
| `windows_standalone` | `jobs.<group-name>[array]` | Standalone Windows jobs |
| `windows_two_stage` | `jobs.<group-name>[array]` | Producer/consumer chains for Windows |

### Job Array Format (Standalone)

Each standalone job in the array contains the following fields:

```
{
  "id": "unique-job-identifier",
  "name": "Human-readable job name",
  "runner": "github-runner-label",
  "image": "docker-image-name",
  "command": "bash command to execute",
  "cuda": "CUDA version (Linux only)",
  "host": "host type (Linux only)"
}
```

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:10-13](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:10-13]()

### PC Array Format (Two-Stage)

Each two-stage entry in the array contains producer/consumer chain information:

```
{
  "id": "producer-job-id",
  "producers": [array of producer job definitions],
  "consumers": [array of consumer job definitions]
}
```

The `producers` and `consumers` arrays use the same structure as standalone job arrays but are processed differently to enforce dependency ordering.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:10-13](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml:10-13]()

---

## Matrix Strategy Mechanics

All four group dispatch workflows use GitHub Actions' matrix strategy with the `include` feature to parallelize job execution. The matrix is populated by parsing the JSON input directly from `dispatch.json`.

### Standalone Matrix Expansion

```mermaid
graph LR
    Input["job-array input:<br/>JSON string"]
    Parse["fromJSON(inputs.job-array)"]
    Matrix["strategy.matrix.include"]
    Jobs["Parallel GitHub Actions jobs<br/>(one per array entry)"]
    
    Input --> Parse
    Parse --> Matrix
    Matrix --> Jobs
```

The workflow definition uses:
```yaml
strategy:
  fail-fast: false
  matrix:
    include: ${{ fromJSON(inputs.job-array) }}
```

Each field in the job definition becomes accessible as `matrix.<field>`. For example, `matrix.id`, `matrix.name`, `matrix.command`, etc.

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:18-21](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:22-25]()

### Two-Stage Matrix Expansion

Two-stage workflows use the same matrix mechanism but expand producer/consumer chains instead of individual jobs:

```mermaid
graph LR
    Input["pc-array input:<br/>JSON string"]
    Parse["fromJSON(inputs.pc-array)"]
    Matrix["strategy.matrix.include"]
    Chains["Parallel producer/consumer chains<br/>(one per array entry)"]
    
    Input --> Parse
    Parse --> Matrix
    Matrix --> Chains
```

Each matrix entry invokes a two-stage execution workflow with:
- `producers: ${{ toJSON(matrix.producers) }}`
- `consumers: ${{ toJSON(matrix.consumers) }}`

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:16-28](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml:16-28]()

---

## Workflow Invocation Patterns

### Standalone Workflow Invocation

Standalone group workflows directly invoke execution actions within their matrix jobs:

```mermaid
sequenceDiagram
    participant Caller as "Calling Workflow"
    participant Group as "workflow-dispatch-standalone-group-*"
    participant Matrix as "Matrix Job (parallel)"
    participant Exec as "workflow-run-job-*"
    
    Caller->>Group: workflow_call with job-array
    Group->>Group: Parse JSON, setup matrix
    
    par Matrix Expansion
        Group->>Matrix: Spawn job 1
        Matrix->>Exec: Run with matrix.id, matrix.command, etc.
        Exec-->>Matrix: Job complete
        Matrix-->>Group: Job 1 complete
    and
        Group->>Matrix: Spawn job 2
        Matrix->>Exec: Run with matrix.id, matrix.command, etc.
        Exec-->>Matrix: Job complete
        Matrix-->>Group: Job 2 complete
    and
        Group->>Matrix: Spawn job N
        Matrix->>Exec: Run with matrix.id, matrix.command, etc.
        Exec-->>Matrix: Job complete
        Matrix-->>Group: Job N complete
    end
    
    Group-->>Caller: All jobs complete
```

**Linux Implementation:**
- Container: `cruizba/ubuntu-dind:jammy-26.1.3`
- Action: `./.github/actions/workflow-run-job-linux`
- Inputs: `id`, `command`, `image`, `runner`, `cuda`, `host`

**Windows Implementation:**
- Runner: Direct on `matrix.runner`
- Action: `./.github/actions/workflow-run-job-windows`
- Inputs: `id`, `command`, `image`

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:26-43](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:26-37]()

### Two-Stage Workflow Invocation

Two-stage group workflows invoke intermediate two-stage execution workflows, which handle producer/consumer dependency ordering:

```mermaid
sequenceDiagram
    participant Caller as "Calling Workflow"
    participant Group as "workflow-dispatch-two-stage-group-*"
    participant Matrix as "Matrix Job (parallel)"
    participant TwoStage as "workflow-dispatch-two-stage-*"
    
    Caller->>Group: workflow_call with pc-array
    Group->>Group: Parse JSON, setup matrix
    
    par Matrix Expansion
        Group->>Matrix: Spawn chain 1
        Matrix->>TwoStage: uses: workflow-dispatch-two-stage-*<br/>producers + consumers
        TwoStage-->>Matrix: Chain 1 complete
        Matrix-->>Group: Job 1 complete
    and
        Group->>Matrix: Spawn chain 2
        Matrix->>TwoStage: uses: workflow-dispatch-two-stage-*<br/>producers + consumers
        TwoStage-->>Matrix: Chain 2 complete
        Matrix-->>Group: Job 2 complete
    and
        Group->>Matrix: Spawn chain N
        Matrix->>TwoStage: uses: workflow-dispatch-two-stage-*<br/>producers + consumers
        TwoStage-->>Matrix: Chain N complete
        Matrix-->>Group: Job N complete
    end
    
    Group-->>Caller: All chains complete
```

The two-stage execution workflows are invoked with `uses:` rather than direct action calls, allowing them to define complex multi-job dependencies (see [Two-Stage Job Dispatch](#4.2) for details).

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:25-28](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml:25-28]()

---

## Parallel Execution and Failure Handling

All four dispatch workflows configure their matrix strategies with `fail-fast: false`, which ensures that a failure in one job does not cancel other parallel jobs. This is critical for comprehensive CI coverage—failures in specific configurations (e.g., one compiler or CUDA version) should not prevent testing other configurations.

### Job Naming

Matrix jobs are named using the `name` field from the job definition:

| Workflow Type | Naming Pattern |
|---------------|----------------|
| Linux Standalone | `"${{ matrix.name }}"` |
| Windows Standalone | `${{ matrix.name }}` |
| Linux Two-Stage | `${{ matrix.id }}` |
| Windows Two-Stage | `${{ matrix.id }}` |

The two-stage workflows use `id` instead of `name` because they represent producer/consumer chains rather than individual jobs.

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:17](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:17](), [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:17](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml:17]()

---

## Permissions and Security

All dispatch workflows request minimal necessary permissions:

```yaml
permissions:
  id-token: write    # For AWS OIDC authentication
  contents: read     # For repository checkout
```

The `id-token: write` permission enables AWS credential federation via GitHub's OIDC provider, allowing jobs to access S3 for sccache without storing long-lived credentials (see [Distributed Compilation Caching](#7.2)).

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:22-24](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:19-21](), [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:18-20](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml:18-20]()

---

## Linux-Specific Container Configuration

Linux standalone jobs run within an intermediate `cruizba/ubuntu-dind:jammy-26.1.3` container that provides Docker-in-Docker capabilities:

```yaml
container:
  image: cruizba/ubuntu-dind:jammy-26.1.3
  env:
    NVIDIA_VISIBLE_DEVICES: ${{env.NVIDIA_VISIBLE_DEVICES}}
```

This container configuration:
- Provides the Docker CLI for launching devcontainers
- Preserves GPU visibility via `NVIDIA_VISIBLE_DEVICES` environment variable
- Uses the host's Docker daemon through socket mounting (configured in the execution action)

Windows workflows do not use container configuration at this level; they execute directly on the runner with Docker available.

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:26-29]()

---

## Workflow Call Interface

The group dispatch workflows are designed to be invoked via `workflow_call` from parent orchestration workflows. They do not trigger on standard GitHub events (push, pull_request, etc.).

### Input Specification

| Workflow | Input Name | Type | Description |
|----------|-----------|------|-------------|
| `workflow-dispatch-standalone-group-linux.yml` | `job-array` | string | JSON array from `dispatch.json`'s `linux_standalone.jobs.<name>` |
| `workflow-dispatch-standalone-group-windows.yml` | `job-array` | string | JSON array from `dispatch.json`'s `windows_standalone.jobs.<name>` |
| `workflow-dispatch-two-stage-group-linux.yml` | `pc-array` | string | JSON array from `dispatch.json`'s `linux_two_stage.jobs.<name>` |
| `workflow-dispatch-two-stage-group-windows.yml` | `pc-array` | string | JSON array from `dispatch.json`'s `windows_two_stage.jobs.<name>` |

All inputs are marked as `required: true`, ensuring the calling workflow must provide valid job definitions.

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:7-13](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:7-13](), [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:7-13](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml:7-13]()

---

## Dispatch Workflow Mapping

The following table summarizes how `dispatch.json` categories map to dispatch workflows:

| dispatch.json Key | Dispatch Workflow | Target OS | Execution Pattern | Output Workflow/Action |
|-------------------|-------------------|-----------|-------------------|------------------------|
| `linux_standalone` | `workflow-dispatch-standalone-group-linux.yml` | Linux | Standalone | `workflow-run-job-linux` |
| `linux_two_stage` | `workflow-dispatch-two-stage-group-linux.yml` | Linux | Two-Stage | `workflow-dispatch-two-stage-linux.yml` |
| `windows_standalone` | `workflow-dispatch-standalone-group-windows.yml` | Windows | Standalone | `workflow-run-job-windows` |
| `windows_two_stage` | `workflow-dispatch-two-stage-group-windows.yml` | Windows | Two-Stage | `workflow-dispatch-two-stage-windows.yml` |

This separation enables:
1. **GitHub Actions UI Optimization**: Only relevant jobs appear in the workflow UI, rather than hundreds of skipped jobs
2. **OS-Specific Configuration**: Linux and Windows runners require different container and execution strategies
3. **Pattern-Specific Handling**: Standalone jobs can execute immediately, while two-stage jobs require dependency orchestration

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml](), [.github/workflows/workflow-dispatch-two-stage-group-linux.yml](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml]()

---

# Page: Standalone Job Dispatch

# Standalone Job Dispatch

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/workflow-dispatch-standalone-group-linux.yml](.github/workflows/workflow-dispatch-standalone-group-linux.yml)
- [.github/workflows/workflow-dispatch-standalone-group-windows.yml](.github/workflows/workflow-dispatch-standalone-group-windows.yml)

</details>



## Purpose and Scope

This document describes the standalone job dispatch subsystem, which routes independent jobs to appropriate execution environments using GitHub Actions matrix strategies. Standalone jobs execute in parallel without dependencies on other jobs, in contrast to the two-stage producer/consumer pattern documented in [Producer-Consumer Pattern](#4.3).

The dispatch mechanism consists of two workflow files that handle Linux and Windows jobs separately, consuming job definitions from `dispatch.json` and expanding them into parallel matrix executions. Each workflow delegates actual command execution to platform-specific execution actions documented in [Linux Execution Environment](#5.1) and [Windows Execution Environment](#5.2).

## Standalone Job Characteristics

Standalone jobs are independent execution units with the following properties:

- **No Dependencies**: Each job runs independently without waiting for other jobs to complete
- **Parallel Execution**: All jobs in the dispatch group run simultaneously (subject to runner availability)
- **Self-Contained**: Jobs do not produce artifacts for consumption by other jobs
- **Matrix-Based**: Jobs are dispatched using GitHub Actions matrix strategy for efficient parallelization
- **Isolated Failure**: Job failures do not block other jobs due to `fail-fast: false` configuration

Standalone jobs are suitable for:
- Compilation and testing tasks that do not share build artifacts
- Independent test suites across different configurations
- Validation jobs that run against different combinations of compilers, CUDA versions, and GPU architectures

**Sources:** Context from provided diagrams

## Dispatch Workflow Architecture

### Linux Standalone Dispatch

The `workflow-dispatch-standalone-group-linux.yml` workflow handles dispatch for Linux-based standalone jobs.

**Workflow Structure:**

```mermaid
graph TB
    DispatchJSON["dispatch.json<br/>linux_standalone section"]
    Caller["Calling Workflow<br/>(workflow-build)"]
    GroupDispatch["workflow-dispatch-standalone-group-linux.yml"]
    Matrix["GitHub Actions Matrix<br/>run-jobs"]
    Job1["Job: matrix.name[0]"]
    Job2["Job: matrix.name[1]"]
    JobN["Job: matrix.name[n]"]
    RunAction["workflow-run-job-linux<br/>Action"]
    DindContainer["cruizba/ubuntu-dind:jammy-26.1.3<br/>Intermediate Container"]
    DevContainer["DevContainer<br/>Job-specific image"]
    
    DispatchJSON -->|"job-array input"| Caller
    Caller -->|"workflow_call"| GroupDispatch
    GroupDispatch -->|"fromJSON(inputs.job-array)"| Matrix
    Matrix -->|"Parallel Execution"| Job1
    Matrix -->|"Parallel Execution"| Job2
    Matrix -->|"Parallel Execution"| JobN
    Job1 --> RunAction
    Job2 --> RunAction
    JobN --> RunAction
    RunAction --> DindContainer
    DindContainer --> DevContainer
```

**Key Components:**

| Component | Description | Reference |
|-----------|-------------|-----------|
| Workflow Name | `Workflow/Dispatch/StandaloneGroup/Linux` | [.github/workflows/workflow-dispatch-standalone-group-linux.yml:1]() |
| Trigger | `workflow_call` with `job-array` input | [.github/workflows/workflow-dispatch-standalone-group-linux.yml:8-13]() |
| Matrix Source | `fromJSON(inputs.job-array)` | [.github/workflows/workflow-dispatch-standalone-group-linux.yml:21]() |
| Job Name | `${{ matrix.name }}` | [.github/workflows/workflow-dispatch-standalone-group-linux.yml:17]() |
| Container Image | `cruizba/ubuntu-dind:jammy-26.1.3` | [.github/workflows/workflow-dispatch-standalone-group-linux.yml:27]() |
| Execution Action | `workflow-run-job-linux` | [.github/workflows/workflow-dispatch-standalone-group-linux.yml:36]() |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:1-44]()

### Windows Standalone Dispatch

The `workflow-dispatch-standalone-group-windows.yml` workflow handles dispatch for Windows-based standalone jobs.

**Workflow Structure:**

```mermaid
graph TB
    DispatchJSON["dispatch.json<br/>windows_standalone section"]
    Caller["Calling Workflow<br/>(workflow-build)"]
    GroupDispatch["workflow-dispatch-standalone-group-windows.yml"]
    Matrix["GitHub Actions Matrix<br/>run-jobs"]
    Job1["Job: matrix.name[0]"]
    Job2["Job: matrix.name[1]"]
    JobN["Job: matrix.name[n]"]
    RunAction["workflow-run-job-windows<br/>Action"]
    WindowsRunner["Windows Runner<br/>Native Execution"]
    
    DispatchJSON -->|"job-array input"| Caller
    Caller -->|"workflow_call"| GroupDispatch
    GroupDispatch -->|"fromJSON(inputs.job-array)"| Matrix
    Matrix -->|"Parallel Execution"| Job1
    Matrix -->|"Parallel Execution"| Job2
    Matrix -->|"Parallel Execution"| JobN
    Job1 --> RunAction
    Job2 --> RunAction
    JobN --> RunAction
    RunAction --> WindowsRunner
```

**Key Differences from Linux:**

| Aspect | Linux | Windows |
|--------|-------|---------|
| Container Strategy | Intermediate `ubuntu-dind` container | No intermediate container |
| GPU Environment | `NVIDIA_VISIBLE_DEVICES` env var in container | Passed directly to execution action |
| Runner | Specified in `matrix.runner` | Specified in `matrix.runner` |
| Execution Action | `workflow-run-job-linux` | `workflow-run-job-windows` |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-windows.yml:1-37]()

## Matrix Strategy and Job Expansion

### Matrix Configuration

Both workflows use identical matrix strategy configuration:

```mermaid
graph LR
    Input["inputs.job-array<br/>(JSON string)"]
    FromJSON["fromJSON() function"]
    Matrix["matrix.include<br/>(array of objects)"]
    Jobs["Parallel Jobs<br/>(one per matrix entry)"]
    
    Input --> FromJSON
    FromJSON --> Matrix
    Matrix --> Jobs
```

**Matrix Properties:**

- **Source**: `inputs.job-array` parameter containing JSON-encoded array from `dispatch.json`
- **Strategy**: `fail-fast: false` allows all jobs to complete even if some fail
- **Expansion**: `include: ${{ fromJSON(inputs.job-array) }}` creates one job per array element
- **Naming**: Each job uses `${{ matrix.name }}` for human-readable identification

**Example Matrix Structure:**

```json
[
  {
    "id": "cub-build-cpp20-gcc10-cuda11.1",
    "name": "cub build cpp20 gcc10 cuda11.1",
    "runner": "linux-amd64-cpu16",
    "image": "rapidsai/devcontainers:...",
    "command": "mkdir build && cmake ...",
    "cuda": "11.1",
    "host": "cpp20"
  },
  {
    "id": "thrust-test-cpp17-gcc11-cuda12.0",
    "name": "thrust test cpp17 gcc11 cuda12.0",
    "runner": "linux-amd64-gpu-v100-latest-1",
    "image": "rapidsai/devcontainers:...",
    "command": "ctest --output-on-failure",
    "cuda": "12.0",
    "host": "cpp17"
  }
]
```

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:18-21](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:22-25]()

### Parallelization Behavior

```mermaid
graph TB
    Start["Matrix Expansion"]
    Check{"Runner<br/>Available?"}
    Queue["Queued"]
    Execute["Running"]
    Complete["Complete"]
    
    Start --> Check
    Check -->|"Yes"| Execute
    Check -->|"No"| Queue
    Queue --> Check
    Execute --> Complete
    
    subgraph "Parallel Execution Pool"
        Execute
    end
```

**Parallelization Characteristics:**

| Property | Behavior |
|----------|----------|
| **Maximum Concurrency** | Limited by available runners matching `matrix.runner` specification |
| **Job Independence** | Jobs do not communicate or share state during execution |
| **Failure Handling** | `fail-fast: false` prevents cascading failures |
| **Resource Allocation** | Each job allocates its specified runner type independently |
| **Execution Order** | Non-deterministic; depends on runner availability |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:18-21](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:22-25]()

## Job Input Structure

### Required Matrix Fields

Each job in the matrix array must contain the following fields:

```mermaid
graph LR
    Job["Job Object<br/>(matrix entry)"]
    ID["id: string<br/>Unique job identifier"]
    Name["name: string<br/>Display name"]
    Runner["runner: string<br/>Runner label"]
    Image["image: string<br/>Container image"]
    Command["command: string<br/>Execution command"]
    
    Job --> ID
    Job --> Name
    Job --> Runner
    Job --> Image
    Job --> Command
```

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `id` | string | Unique identifier for artifact paths | `"cub-build-cpp20-gcc10-cuda11.1"` |
| `name` | string | Human-readable job name displayed in UI | `"cub build cpp20 gcc10 cuda11.1"` |
| `runner` | string | GitHub runner label | `"linux-amd64-gpu-v100-latest-1"` |
| `image` | string | Container image for devcontainer | `"rapidsai/devcontainers:24.08-..."` |
| `command` | string | Shell command to execute | `"mkdir build && cmake ..."` |

**Linux-Specific Fields:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `cuda` | string | CUDA version for environment setup | `"12.0"` |
| `host` | string | Host configuration identifier | `"cpp20"` |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:38-43](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:34-36]()

### Permissions Configuration

Both workflows require specific GitHub permissions:

```mermaid
graph LR
    Permissions["Job Permissions"]
    IDToken["id-token: write<br/>AWS credential federation"]
    Contents["contents: read<br/>Repository access"]
    
    Permissions --> IDToken
    Permissions --> Contents
```

| Permission | Level | Purpose |
|------------|-------|---------|
| `id-token` | `write` | Required for AWS OIDC federation to access sccache S3 bucket |
| `contents` | `read` | Required for repository checkout |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:22-24](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:19-21]()

## Execution Flow

### Linux Execution Sequence

```mermaid
sequenceDiagram
    participant Dispatch as "workflow-dispatch-standalone-group-linux"
    participant Matrix as "GitHub Matrix Strategy"
    participant Job as "run-jobs Job"
    participant Checkout as "actions/checkout@v4"
    participant Action as "workflow-run-job-linux"
    participant Dind as "ubuntu-dind Container"
    participant DevCon as "DevContainer"
    
    Dispatch->>Matrix: Parse fromJSON(inputs.job-array)
    Matrix->>Job: Create job for each matrix entry
    Note over Job: Runs in cruizba/ubuntu-dind:jammy-26.1.3
    Job->>Checkout: Clone repository
    Checkout-->>Job: Repository ready
    Job->>Action: Call with matrix parameters
    Action->>Dind: Setup Docker-outside-of-Docker
    Dind->>DevCon: Launch job-specific container
    DevCon->>DevCon: Execute matrix.command
    DevCon-->>Dind: Command output
    Dind-->>Action: Upload artifacts
    Action-->>Job: Job complete
    Job-->>Matrix: Report status
```

**Execution Steps:**

1. **Matrix Expansion**: GitHub Actions parses `job-array` JSON and creates parallel jobs
2. **Container Initialization**: Each job starts in `cruizba/ubuntu-dind:jammy-26.1.3` intermediate container
3. **Repository Checkout**: `actions/checkout@v4` clones the repository with `persist-credentials: false`
4. **Action Invocation**: `workflow-run-job-linux` action receives matrix parameters
5. **DevContainer Launch**: Action launches job-specific container using Docker-outside-of-Docker
6. **Command Execution**: The `matrix.command` executes inside the devcontainer
7. **Artifact Collection**: Success markers, logs, and sccache statistics are uploaded

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:26-43]()

### Windows Execution Sequence

```mermaid
sequenceDiagram
    participant Dispatch as "workflow-dispatch-standalone-group-windows"
    participant Matrix as "GitHub Matrix Strategy"
    participant Job as "run-jobs Job"
    participant Checkout as "actions/checkout@v4"
    participant Action as "workflow-run-job-windows"
    participant Runner as "Windows Runner"
    participant Docker as "Docker Container"
    
    Dispatch->>Matrix: Parse fromJSON(inputs.job-array)
    Matrix->>Job: Create job for each matrix entry
    Note over Job: Runs directly on Windows runner
    Job->>Checkout: Clone repository
    Checkout-->>Job: Repository ready
    Job->>Action: Call with matrix parameters
    Action->>Runner: Setup Windows environment
    Runner->>Docker: Launch Docker container
    Docker->>Docker: Execute matrix.command
    Docker-->>Runner: Command output
    Runner-->>Action: Upload artifacts
    Action-->>Job: Job complete
    Job-->>Matrix: Report status
```

**Key Differences:**

- No intermediate container; jobs run directly on Windows runner
- Docker container launched directly from runner (not Docker-outside-of-Docker)
- Fewer matrix parameters passed to execution action (no `cuda` or `host` fields)

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-windows.yml:26-37]()

## Integration with Dispatch Pipeline

### Data Flow from Generation to Execution

```mermaid
graph TB
    Matrix["matrix.yaml"]
    BuildPy["build-workflow.py"]
    WorkflowJSON["workflow.json"]
    PrepareDispatch["prepare-workflow-dispatch.py"]
    DispatchJSON["dispatch.json"]
    LinuxStandalone["linux_standalone section"]
    WindowsStandalone["windows_standalone section"]
    LinuxWorkflow["workflow-dispatch-standalone-group-linux.yml"]
    WindowsWorkflow["workflow-dispatch-standalone-group-windows.yml"]
    
    Matrix --> BuildPy
    BuildPy --> WorkflowJSON
    WorkflowJSON --> PrepareDispatch
    PrepareDispatch --> DispatchJSON
    DispatchJSON --> LinuxStandalone
    DispatchJSON --> WindowsStandalone
    LinuxStandalone -->|"job-array input"| LinuxWorkflow
    WindowsStandalone -->|"job-array input"| WindowsWorkflow
```

**Pipeline Stages:**

1. **Configuration**: `matrix.yaml` defines all possible job combinations
2. **Generation**: `build-workflow.py` expands, validates, and processes jobs into `workflow.json`
3. **Dispatch Preparation**: `prepare-workflow-dispatch.py` splits jobs by OS and execution pattern
4. **Standalone Extraction**: Jobs with `job_type: standalone` are placed in `linux_standalone` or `windows_standalone`
5. **Workflow Invocation**: Parent workflow calls standalone dispatch workflows with `job-array` input
6. **Matrix Execution**: Dispatch workflows expand matrix and execute jobs in parallel

**Sources:** Context from provided diagrams and workflow files

## Configuration Reference

### Linux Workflow Inputs

| Input | Required | Type | Description |
|-------|----------|------|-------------|
| `job-array` | Yes | string | JSON-encoded array from `dispatch.json`'s `linux_standalone.jobs.<name>` |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:10-13]()

### Windows Workflow Inputs

| Input | Required | Type | Description |
|-------|----------|------|-------------|
| `job-array` | Yes | string | JSON-encoded array from `dispatch.json`'s `windows_standalone.jobs.<name>` |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-windows.yml:10-13]()

### Shell Configuration

Both workflows use identical shell configuration:

```bash
bash --noprofile --norc -euo pipefail {0}
```

| Flag | Purpose |
|------|---------|
| `--noprofile` | Skip profile initialization for faster startup |
| `--norc` | Skip `.bashrc` for cleaner environment |
| `-e` | Exit immediately on error |
| `-u` | Treat unset variables as errors |
| `-o pipefail` | Pipeline fails if any command fails |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:3-5](), [.github/workflows/workflow-dispatch-standalone-group-windows.yml:3-5]()

## Comparison: Standalone vs Two-Stage Dispatch

| Aspect | Standalone Dispatch | Two-Stage Dispatch |
|--------|---------------------|-------------------|
| **Job Dependencies** | None; all jobs independent | Producer must complete before consumers |
| **Parallelization** | All jobs run simultaneously | Consumers wait for producer |
| **Use Case** | Independent builds/tests | Build artifacts shared across tests |
| **Artifact Flow** | Each job produces own artifacts | Producer artifacts consumed by consumers |
| **Matrix Structure** | Flat array of jobs | Array of producer/consumer chains |
| **Failure Impact** | Isolated; other jobs continue | Producer failure blocks all consumers |
| **Workflow Files** | `workflow-dispatch-standalone-group-*` | `workflow-dispatch-two-stage-group-*` |
| **Execution Pattern** | Single-stage | Producer → Multiple Consumers |

For detailed information about two-stage dispatch, see [Two-Stage Job Dispatch](#4.2) and [Producer-Consumer Pattern](#4.3).

**Sources:** Context from provided diagrams and workflow files

---

# Page: Two-Stage Job Dispatch

# Two-Stage Job Dispatch

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/workflow-dispatch-two-stage-group-linux.yml](.github/workflows/workflow-dispatch-two-stage-group-linux.yml)
- [.github/workflows/workflow-dispatch-two-stage-group-windows.yml](.github/workflows/workflow-dispatch-two-stage-group-windows.yml)
- [.github/workflows/workflow-dispatch-two-stage-linux.yml](.github/workflows/workflow-dispatch-two-stage-linux.yml)
- [.github/workflows/workflow-dispatch-two-stage-windows.yml](.github/workflows/workflow-dispatch-two-stage-windows.yml)

</details>



## Purpose and Scope

This document describes the **two-stage group dispatch workflows** that handle producer/consumer job chains with dependency ordering. These workflows form the dispatch layer for two-stage jobs, using GitHub Actions matrix strategies to parallelize multiple independent producer/consumer chains.

This page focuses on the group-level dispatch mechanism. For details on the actual producer/consumer execution pattern and artifact exchange, see [Producer-Consumer Pattern](#4.3). For standalone job dispatch, see [Standalone Job Dispatch](#4.1). For information about how jobs are categorized and prepared for dispatch, see [Dispatch Preparation](#3.2).

## Architecture Overview

The two-stage job dispatch system consists of two workflow layers that work together to execute producer/consumer chains:

```mermaid
graph TB
    subgraph "Input Layer"
        DispatchJSON["dispatch.json"]
        LinuxTwoStage["linux_two_stage.jobs"]
        WindowsTwoStage["windows_two_stage.jobs"]
        
        DispatchJSON --> LinuxTwoStage
        DispatchJSON --> WindowsTwoStage
    end
    
    subgraph "Group Dispatch Layer"
        LinuxGroup["workflow-dispatch-two-stage-group-linux.yml"]
        WindowsGroup["workflow-dispatch-two-stage-group-windows.yml"]
        
        LinuxTwoStage -->|"pc-array input"| LinuxGroup
        WindowsTwoStage -->|"pc-array input"| WindowsGroup
    end
    
    subgraph "Matrix Expansion"
        LinuxMatrix["Matrix Strategy<br/>fail-fast: false<br/>include: fromJSON(pc-array)"]
        WindowsMatrix["Matrix Strategy<br/>fail-fast: false<br/>include: fromJSON(pc-array)"]
        
        LinuxGroup --> LinuxMatrix
        WindowsGroup --> WindowsMatrix
    end
    
    subgraph "Two-Stage Execution Layer"
        LinuxExec["workflow-dispatch-two-stage-linux.yml"]
        WindowsExec["workflow-dispatch-two-stage-windows.yml"]
        
        LinuxMatrix -->|"foreach chain"| LinuxExec
        WindowsMatrix -->|"foreach chain"| WindowsExec
    end
    
    subgraph "Execution Components"
        Producer["Producer Job<br/>needs: none"]
        Consumers["Consumer Jobs<br/>needs: producer"]
        
        LinuxExec --> Producer
        LinuxExec --> Consumers
        WindowsExec --> Producer
        WindowsExec --> Consumers
    end
```

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml](), [.github/workflows/workflow-dispatch-two-stage-linux.yml](), [.github/workflows/workflow-dispatch-two-stage-windows.yml]()

The dispatch architecture has two levels:

1. **Group Dispatch Layer**: Receives an array of producer/consumer chains and uses GitHub Actions matrix strategies to parallelize their execution
2. **Two-Stage Execution Layer**: Enforces producer-before-consumer ordering and handles artifact exchange for each chain

This separation enables efficient parallelization while maintaining the dependency ordering required by the producer/consumer pattern.

## Linux Group Dispatch Workflow

The Linux group dispatch workflow is defined in `workflow-dispatch-two-stage-group-linux.yml` and serves as the entry point for dispatching Linux two-stage jobs.

### Workflow Interface

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `pc-array` | string | Yes | JSON string containing the `dispatch.json`'s `linux_two_stage.jobs.<name>` array of producer/consumer chains |

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:10-13]()

### Matrix Strategy

The workflow uses GitHub Actions matrix strategy to parallelize multiple producer/consumer chains:

```yaml
strategy:
  fail-fast: false
  matrix:
    include: ${{ fromJSON(inputs.pc-array) }}
```

Key characteristics:
- **`fail-fast: false`**: Allows all chains to execute even if one fails, ensuring comprehensive test coverage
- **`include: fromJSON(inputs.pc-array)`**: Dynamically constructs matrix from input JSON array
- **Matrix variable `${{ matrix.id }}`**: Used for job naming to identify each chain in the GitHub Actions UI

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:21-24]()

### Chain Dispatch

Each matrix iteration dispatches a single producer/consumer chain to the two-stage execution workflow:

```mermaid
graph LR
    GroupJob["dispatch-pcs<br/>name: matrix.id"]
    TwoStageWorkflow["workflow-dispatch-two-stage-linux.yml"]
    Inputs["producers: toJSON(matrix.producers)<br/>consumers: toJSON(matrix.consumers)"]
    
    GroupJob -->|"uses"| TwoStageWorkflow
    GroupJob -->|"with"| Inputs
```

The group workflow extracts `producers` and `consumers` arrays from each matrix entry and passes them as JSON strings to the two-stage execution workflow.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:25-28]()

### Permissions

Each dispatched chain job requires specific GitHub permissions:

| Permission | Access Level | Purpose |
|------------|--------------|---------|
| `id-token` | write | AWS credential federation via OIDC for sccache access |
| `contents` | read | Repository checkout |

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:18-20]()

## Windows Group Dispatch Workflow

The Windows group dispatch workflow (`workflow-dispatch-two-stage-group-windows.yml`) has an identical structure to the Linux version but dispatches to the Windows two-stage execution workflow.

### Key Differences from Linux

The Windows group dispatch workflow is architecturally identical to the Linux version with only these differences:

| Aspect | Linux | Windows |
|--------|-------|---------|
| Workflow file | `workflow-dispatch-two-stage-group-linux.yml` | `workflow-dispatch-two-stage-group-windows.yml` |
| Input parameter | `pc-array` from `linux_two_stage.jobs` | `pc-array` from `windows_two_stage.jobs` |
| Target execution workflow | `workflow-dispatch-two-stage-linux.yml` | `workflow-dispatch-two-stage-windows.yml` |
| Container runtime | Linux containers with DOOD | Windows Docker containers |

The matrix strategy, permissions, and dispatch logic remain identical across both platforms.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-windows.yml:1-29]()

## Input Data Structure

The `pc-array` input contains a JSON array where each element represents a producer/consumer chain with the following structure:

```mermaid
graph TB
    subgraph "pc-array Element"
        ChainID["id: string<br/>Chain identifier"]
        Producers["producers: array<br/>Producer job definitions"]
        Consumers["consumers: array<br/>Consumer job definitions"]
        
        ChainID -.->|"used for"| JobName["Job name in UI"]
        Producers -.->|"passed to"| TwoStageWorkflow["two-stage execution workflow"]
        Consumers -.->|"passed to"| TwoStageWorkflow
    end
    
    subgraph "Job Definition Fields"
        JobID["id: unique job identifier"]
        JobName2["name: display name"]
        JobCommand["command: script to execute"]
        JobImage["image: devcontainer image"]
        JobRunner["runner: GitHub runner label"]
        JobCuda["cuda: CUDA version (Linux only)"]
        JobHost["host: host type (Linux only)"]
    end
    
    Producers --> JobID
    Consumers --> JobID
```

### Producer Definition

Each element in the `producers` array is a complete job definition passed to the two-stage execution workflow. The two-stage execution workflows currently only support **single producer per chain**.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:20-21]()

### Consumer Definition

The `consumers` array contains multiple job definitions that will be executed in parallel after the producer completes. Each consumer receives the producer's artifacts.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:47-61]()

## Integration with Two-Stage Execution Workflows

The group dispatch workflows act as orchestrators that invoke the two-stage execution workflows:

```mermaid
sequenceDiagram
    participant Caller as "Upstream Workflow"
    participant GroupLinux as "workflow-dispatch-two-stage-group-linux.yml"
    participant Matrix as "Matrix Strategy"
    participant TwoStage as "workflow-dispatch-two-stage-linux.yml"
    participant Producer as "Producer Job"
    participant Consumer as "Consumer Jobs"
    
    Caller->>GroupLinux: Call with pc-array input
    Note over GroupLinux: fromJSON(pc-array) creates matrix
    
    GroupLinux->>Matrix: Expand matrix entries
    
    par Chain 1
        Matrix->>TwoStage: producers[0], consumers[]
        TwoStage->>Producer: Execute build
        Producer-->>TwoStage: Artifacts uploaded
        TwoStage->>Consumer: Execute tests (parallel)
        Consumer-->>Matrix: Complete
    and Chain 2
        Matrix->>TwoStage: producers[0], consumers[]
        TwoStage->>Producer: Execute build
        Producer-->>TwoStage: Artifacts uploaded
        TwoStage->>Consumer: Execute tests (parallel)
        Consumer-->>Matrix: Complete
    end
    
    Matrix-->>GroupLinux: All chains complete
    GroupLinux-->>Caller: Dispatch complete
```

### Workflow Calling Pattern

The group workflows use GitHub Actions' `uses:` syntax to invoke the execution workflows:

**Linux:**
```yaml
uses: ./.github/workflows/workflow-dispatch-two-stage-linux.yml
with:
  producers: ${{ toJSON(matrix.producers) }}
  consumers: ${{ toJSON(matrix.consumers) }}
```

**Windows:**
```yaml
uses: ./.github/workflows/workflow-dispatch-two-stage-windows.yml
with:
  producers: ${{ toJSON(matrix.producers) }}
  consumers: ${{ toJSON(matrix.consumers) }}
```

The `toJSON()` function serializes the matrix variables back to JSON strings, as the two-stage execution workflows expect string inputs that are later parsed with `fromJSON()`.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:25-28](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml:25-28]()

## Execution Flow

The complete execution flow from group dispatch to job completion:

```mermaid
graph TB
    subgraph "Phase 1: Group Dispatch"
        Input["pc-array JSON input"]
        Parse["fromJSON(inputs.pc-array)"]
        MatrixGen["Generate matrix entries"]
        
        Input --> Parse
        Parse --> MatrixGen
    end
    
    subgraph "Phase 2: Parallel Chain Dispatch"
        Chain1["Chain 1<br/>producers + consumers"]
        Chain2["Chain 2<br/>producers + consumers"]
        ChainN["Chain N<br/>producers + consumers"]
        
        MatrixGen --> Chain1
        MatrixGen --> Chain2
        MatrixGen --> ChainN
    end
    
    subgraph "Phase 3: Two-Stage Execution"
        direction TB
        Exec["workflow-dispatch-two-stage-*.yml"]
        ProducerJob["Producer Job<br/>workflow-run-job-*"]
        ConsumerMatrix["Consumer Matrix<br/>fail-fast: false"]
        
        Chain1 --> Exec
        Exec --> ProducerJob
        ProducerJob -->|"needs: producer"| ConsumerMatrix
    end
    
    subgraph "Phase 4: Job Execution"
        DevContainer["DevContainer/Docker"]
        Command["Execute command"]
        Artifacts["Upload/Download Artifacts"]
        
        ProducerJob --> DevContainer
        ConsumerMatrix --> DevContainer
        DevContainer --> Command
        Command --> Artifacts
    end
```

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml](), [.github/workflows/workflow-dispatch-two-stage-linux.yml]()

### Matrix Job Naming

Each matrix job is named using the `id` field from the chain definition:

```yaml
name: ${{ matrix.id }}
```

This ensures that each producer/consumer chain appears as a distinct job in the GitHub Actions UI, making it easy to identify and debug specific chains.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:17](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml:17]()

## Limitations and Constraints

### Single Producer Restriction

Both Linux and Windows two-stage execution workflows currently support only **one producer per chain**:

```yaml
# Accumulating results from multiple producers is not easily implemented. 
# For now, only a single producer is supported.
# The build-workflow.py script will emit an error if more than one producer is specified.
producer:
  name: ${{ fromJSON(inputs.producers)[0].name }}
```

The workflows access the producer using `fromJSON(inputs.producers)[0]`, extracting only the first element. The workflow generation system (specifically `build-workflow.py`) validates this constraint and emits an error if multiple producers are specified for a single chain.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:20-23](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:20-23]()

### Artifact Accumulation

The single producer limitation exists because accumulating results from multiple producers into a single artifact set for consumers is complex to implement. Each consumer would need to:
- Download artifacts from multiple producers
- Handle naming conflicts
- Merge or reconcile overlapping outputs
- Determine success criteria when producers have different outcomes

### No Cross-Chain Dependencies

Producer/consumer chains are independent and cannot depend on each other. Each chain is a self-contained execution unit with its own producer and consumers. If cross-chain dependencies are required, they must be expressed through separate workflow structures or manual coordination.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml:21-24]()

## Configuration Example

A typical `pc-array` input structure for a group dispatch workflow:

```json
[
  {
    "id": "thrust-build-test-chain",
    "producers": [
      {
        "id": "thrust-cpp17-gcc10-cuda12.0-build",
        "name": "thrust cpp17 gcc10 cuda12.0 [build]",
        "command": "cd thrust && cmake --build build",
        "image": "rapidsai/devcontainers:cuda12.0-gcc10",
        "runner": "linux-amd64-cpu16",
        "cuda": "12.0",
        "host": "cpp"
      }
    ],
    "consumers": [
      {
        "id": "thrust-cpp17-gcc10-cuda12.0-test-v100",
        "name": "thrust cpp17 gcc10 cuda12.0 [test v100]",
        "command": "cd thrust && ctest --test-dir build",
        "image": "rapidsai/devcontainers:cuda12.0-gcc10",
        "runner": "linux-amd64-gpu-v100-latest-1",
        "cuda": "12.0",
        "host": "cpp"
      },
      {
        "id": "thrust-cpp17-gcc10-cuda12.0-test-t4",
        "name": "thrust cpp17 gcc10 cuda12.0 [test t4]",
        "command": "cd thrust && ctest --test-dir build",
        "image": "rapidsai/devcontainers:cuda12.0-gcc10",
        "runner": "linux-amd64-gpu-t4-latest-1",
        "cuda": "12.0",
        "host": "cpp"
      }
    ]
  }
]
```

This structure allows a single build job to produce artifacts consumed by multiple test jobs running on different GPU architectures.

## Summary

The two-stage group dispatch workflows provide a scalable dispatch layer for producer/consumer job chains:

| Component | File | Purpose |
|-----------|------|---------|
| Linux Group Dispatch | `workflow-dispatch-two-stage-group-linux.yml` | Parallelize Linux producer/consumer chains using matrix strategy |
| Windows Group Dispatch | `workflow-dispatch-two-stage-group-windows.yml` | Parallelize Windows producer/consumer chains using matrix strategy |
| Linux Two-Stage Execution | `workflow-dispatch-two-stage-linux.yml` | Execute single Linux producer/consumer chain with dependency ordering |
| Windows Two-Stage Execution | `workflow-dispatch-two-stage-windows.yml` | Execute single Windows producer/consumer chain with dependency ordering |

The group workflows transform a flat array of chain definitions into parallel execution streams, while the two-stage execution workflows handle the producer-before-consumer ordering and artifact exchange within each chain. This architecture enables efficient parallelization while maintaining the dependencies required by build-once, test-many workflows.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-group-linux.yml](), [.github/workflows/workflow-dispatch-two-stage-group-windows.yml](), [.github/workflows/workflow-dispatch-two-stage-linux.yml](), [.github/workflows/workflow-dispatch-two-stage-windows.yml]()

---

# Page: Producer-Consumer Pattern

# Producer-Consumer Pattern

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/workflow-dispatch-two-stage-linux.yml](.github/workflows/workflow-dispatch-two-stage-linux.yml)
- [.github/workflows/workflow-dispatch-two-stage-windows.yml](.github/workflows/workflow-dispatch-two-stage-windows.yml)

</details>



## Purpose and Scope

This document explains the two-stage producer-consumer execution model used in the cccl-gha workflow system. It covers how a single producer job generates artifacts that multiple consumer jobs utilize, including the dependency ordering mechanism, artifact exchange via GitHub Actions artifact storage, and parallel consumer execution strategies.

For information about how two-stage jobs are dispatched and grouped, see [Two-Stage Job Dispatch](#4.2). For details about the actual execution environments where producer and consumer commands run, see [Linux Execution Environment](#5.1) and [Windows Execution Environment](#5.2).

## Pattern Overview

The producer-consumer pattern enables build-once, test-many workflows where expensive compilation steps (producers) are executed once, and their outputs are consumed by multiple test configurations (consumers) running in parallel. This pattern is particularly valuable for CUDA projects where compilation is time-consuming but testing across different GPU architectures, operating systems, or runtime configurations is necessary.

The pattern is implemented in two separate workflow files that handle Linux and Windows execution environments:
- `.github/workflows/workflow-dispatch-two-stage-linux.yml`
- `.github/workflows/workflow-dispatch-two-stage-windows.yml`

### Execution Flow Sequence

```mermaid
sequenceDiagram
    participant Dispatch as "workflow-dispatch-two-stage-group-*"
    participant Workflow as "workflow-dispatch-two-stage-*"
    participant Producer as "producer job"
    participant Artifacts as "GitHub Artifacts Storage"
    participant Consumer1 as "consumers[0]"
    participant ConsumerN as "consumers[N]"
    
    Dispatch->>Workflow: "workflow_call with producers/consumers inputs"
    
    Note over Workflow: "Extract fromJSON(inputs.producers)[0]"
    Workflow->>Producer: "Start single producer job"
    Producer->>Producer: "Execute command (e.g., build)"
    Producer->>Artifacts: "Upload build outputs"
    Producer-->>Workflow: "Job complete"
    
    Note over Workflow: "needs: producer dependency satisfied"
    
    par "Parallel Consumer Execution (fail-fast: false)"
        Workflow->>Consumer1: "Start matrix job"
        Consumer1->>Artifacts: "Download producer artifacts"
        Consumer1->>Consumer1: "Execute test command"
        Consumer1-->>Workflow: "Complete (success/failure)"
    and
        Workflow->>ConsumerN: "Start matrix job"
        ConsumerN->>Artifacts: "Download producer artifacts"
        ConsumerN->>ConsumerN: "Execute test command"
        ConsumerN-->>Workflow: "Complete (success/failure)"
    end
    
    Workflow-->>Dispatch: "All jobs complete"
```

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:1-76](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:1-62]()

## Workflow Structure

Both Linux and Windows two-stage workflows follow an identical structural pattern with platform-specific execution actions.

### Workflow Inputs

```mermaid
graph LR
    subgraph "workflow_call inputs"
        Producers["inputs.producers<br/>(string, JSON array)"]
        Consumers["inputs.consumers<br/>(string, JSON array)"]
    end
    
    subgraph "JSON Structure"
        ProducerArray["producers[0]:<br/>- id<br/>- name<br/>- command<br/>- image<br/>- runner<br/>- cuda<br/>- host"]
        ConsumerArray["consumers[*]:<br/>- id<br/>- name<br/>- command<br/>- image<br/>- runner<br/>- cuda<br/>- host"]
    end
    
    Producers --> ProducerArray
    Consumers --> ConsumerArray
```

The workflows receive two string inputs containing JSON-encoded arrays:
- `inputs.producers`: Array of producer job definitions
- `inputs.consumers`: Array of consumer job definitions

Each job definition contains metadata fields parsed from the `dispatch.json` file generated during the workflow generation phase.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:10-17](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:10-17]()

## Producer Job

The producer job executes a single command that generates artifacts for downstream consumption.

### Producer Job Definition

| Aspect | Linux Implementation | Windows Implementation |
|--------|---------------------|------------------------|
| Job name | `producer` | `producer` |
| Job selection | `fromJSON(inputs.producers)[0]` | `fromJSON(inputs.producers)[0]` |
| Execution action | `workflow-run-job-linux` | `workflow-run-job-windows` |
| Container | `cruizba/ubuntu-dind:jammy-26.1.3` | None (native) |
| Permissions | `id-token: write`, `contents: read` | `id-token: write`, `contents: read` |

The producer always uses the **first element** of the `producers` array. This is a current limitation documented in the workflow comments.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:20-46](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:20-39]()

### Producer Configuration Mapping

```mermaid
graph TB
    subgraph "dispatch.json Entry"
        DispatchProducer["linux_two_stage.jobs.&lt;name&gt;[*].producers[0]"]
    end
    
    subgraph "Workflow Parameters"
        ProducerName["name: fromJSON(inputs.producers)[0].name"]
        ProducerRunner["runs-on: fromJSON(inputs.producers)[0].runner"]
        ProducerId["id: fromJSON(inputs.producers)[0].id"]
        ProducerCommand["command: fromJSON(inputs.producers)[0].command"]
        ProducerImage["image: fromJSON(inputs.producers)[0].image"]
        ProducerCuda["cuda: fromJSON(inputs.producers)[0].cuda"]
        ProducerHost["host: fromJSON(inputs.producers)[0].host"]
    end
    
    subgraph "workflow-run-job-linux Action"
        RunAction["Executes command in devcontainer<br/>Uploads artifacts"]
    end
    
    DispatchProducer --> ProducerName
    DispatchProducer --> ProducerRunner
    DispatchProducer --> ProducerId
    DispatchProducer --> ProducerCommand
    DispatchProducer --> ProducerImage
    DispatchProducer --> ProducerCuda
    DispatchProducer --> ProducerHost
    
    ProducerId --> RunAction
    ProducerCommand --> RunAction
    ProducerImage --> RunAction
```

The producer job extracts configuration from the JSON array using `fromJSON()` and array indexing (`[0]`). On Linux, it also passes CUDA and host information for GPU job configuration.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:23-45](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:23-38]()

## Consumer Jobs

Consumer jobs execute in parallel after the producer completes, utilizing artifacts generated by the producer.

### Consumer Job Configuration

```mermaid
graph TB
    subgraph "Dependency Declaration"
        Needs["needs: producer"]
    end
    
    subgraph "Matrix Strategy"
        Strategy["strategy:<br/>  fail-fast: false<br/>  matrix:<br/>    include: fromJSON(inputs.consumers)"]
    end
    
    subgraph "Parallel Execution"
        Consumer1["Consumer Job 1<br/>matrix variables:<br/>- matrix.id<br/>- matrix.name<br/>- matrix.command<br/>- matrix.image<br/>- matrix.runner"]
        Consumer2["Consumer Job 2<br/>(same structure)"]
        ConsumerN["Consumer Job N<br/>(same structure)"]
    end
    
    Needs --> Strategy
    Strategy --> Consumer1
    Strategy --> Consumer2
    Strategy --> ConsumerN
```

Key characteristics of consumer execution:

| Feature | Value | Purpose |
|---------|-------|---------|
| `needs` | `producer` | Ensures producer completes before any consumer starts |
| `fail-fast` | `false` | Allows all consumers to run even if some fail |
| `strategy.matrix.include` | `fromJSON(inputs.consumers)` | Expands each consumer into a separate parallel job |
| `name` | `${{ matrix.name }}` | Human-readable job name in GitHub UI |

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:47-75](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:40-61]()

### Consumer Matrix Expansion

The `matrix.include` strategy creates a separate job for each element in the `consumers` array. Each matrix job receives its configuration through matrix context variables:

```mermaid
graph LR
    subgraph "inputs.consumers JSON Array"
        C0["[0]: {id, name, command, ...}"]
        C1["[1]: {id, name, command, ...}"]
        CN["[N]: {id, name, command, ...}"]
    end
    
    subgraph "Matrix Jobs"
        J0["Job: matrix.name[0]<br/>Variables: matrix.*"]
        J1["Job: matrix.name[1]<br/>Variables: matrix.*"]
        JN["Job: matrix.name[N]<br/>Variables: matrix.*"]
    end
    
    C0 --> J0
    C1 --> J1
    CN --> JN
    
    J0 -.-> Exec["All execute in parallel<br/>after producer completes"]
    J1 -.-> Exec
    JN -.-> Exec
```

Each consumer job accesses its configuration via `matrix.*` variables rather than array indexing, as GitHub Actions automatically populates these variables for each matrix job instance.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:58-61](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:47-50]()

## Artifact Exchange Mechanism

Producer and consumer jobs communicate through GitHub Actions' artifact storage system. The actual artifact upload and download logic is implemented within the `workflow-run-job-linux` and `workflow-run-job-windows` actions.

### Artifact Flow

```mermaid
graph TB
    subgraph "Producer Execution"
        ProducerCmd["Producer Command<br/>(e.g., build script)"]
        ProducerArtifacts["Build outputs<br/>in workspace"]
    end
    
    subgraph "workflow-run-job-* Action"
        Upload["Upload artifacts<br/>named by job ID"]
    end
    
    subgraph "GitHub Actions Storage"
        ArtifactStore["Artifact: jobs/&lt;producer-id&gt;/<br/>- success<br/>- output files"]
    end
    
    subgraph "Consumer Execution"
        Download["Download artifacts<br/>from producer ID"]
        ConsumerCmd["Consumer Command<br/>(e.g., test script)"]
    end
    
    ProducerCmd --> ProducerArtifacts
    ProducerArtifacts --> Upload
    Upload --> ArtifactStore
    ArtifactStore --> Download
    Download --> ConsumerCmd
```

The artifact naming convention uses the job ID to ensure uniqueness. Consumers must know the producer's job ID to download the correct artifacts. This coordination is handled by the workflow generation phase, which assigns consistent IDs to related producer-consumer chains.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:37-45](), [.github/workflows/workflow-dispatch-two-stage-linux.yml:67-75]()

## Dependency Ordering

The `needs: producer` directive in the consumer job definition enforces strict execution ordering.

### Dependency Graph

```mermaid
graph TB
    Producer["producer job<br/>runs-on: producer.runner"]
    
    Consumer1["consumers[0] job<br/>runs-on: matrix.runner<br/>needs: producer"]
    Consumer2["consumers[1] job<br/>runs-on: matrix.runner<br/>needs: producer"]
    ConsumerN["consumers[N] job<br/>runs-on: matrix.runner<br/>needs: producer"]
    
    Producer -->|"dependency satisfied"| Consumer1
    Producer -->|"dependency satisfied"| Consumer2
    Producer -->|"dependency satisfied"| ConsumerN
    
    Consumer1 -.->|"parallel execution"| Consumer2
    Consumer2 -.->|"parallel execution"| ConsumerN
```

GitHub Actions guarantees that:
1. The producer job must complete successfully before any consumer job starts
2. If the producer fails, all consumer jobs are skipped
3. Consumers execute concurrently once the producer succeeds

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:49](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:42]()

## Platform-Specific Differences

While both workflows follow the same structural pattern, they differ in execution environment details.

### Linux vs Windows Implementation

| Aspect | Linux | Windows |
|--------|-------|---------|
| Workflow file | `workflow-dispatch-two-stage-linux.yml` | `workflow-dispatch-two-stage-windows.yml` |
| Container image | `cruizba/ubuntu-dind:jammy-26.1.3` | None (runs natively) |
| Execution action | `workflow-run-job-linux` | `workflow-run-job-windows` |
| CUDA parameter | `cuda: ${{ ... .cuda }}` | Not passed |
| Host parameter | `host: ${{ ... .host }}` | Not passed |
| GPU environment | `NVIDIA_VISIBLE_DEVICES` env var | Not used |

Linux jobs run in a Docker-outside-of-Docker (DOOD) configuration with an intermediate container, while Windows jobs execute natively. Linux jobs also support GPU configuration through additional parameters.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:28-31](), [.github/workflows/workflow-dispatch-two-stage-linux.yml:44-45](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:28-38]()

## Current Limitations

### Single Producer Constraint

Both workflow files contain explicit comments noting a critical limitation:

```
# Accumulating results from multiple producers is not easily implemented. For now, only a single producer is supported.
# The build-workflow.py script will emit an error if more than one producer is specified.
```

This means:
- Only `producers[0]` is used; additional elements are ignored
- Multi-stage builds requiring multiple producer outputs are not supported
- The `build-workflow.py` script validates this constraint during workflow generation

The limitation exists because accumulating artifacts from multiple producers and making them all available to consumers requires more complex dependency orchestration than GitHub Actions' simple `needs` directive provides.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:20-21](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:20-21]()

### Fail-Fast Disabled

Consumer jobs use `fail-fast: false` to ensure comprehensive test coverage:

```yaml
strategy:
  fail-fast: false
  matrix:
    include: ${{ fromJSON(inputs.consumers) }}
```

This means:
- All consumer jobs execute even if one fails
- Partial test results are always available
- The workflow continues to completion regardless of individual consumer failures
- Overall workflow status depends on aggregating all consumer results

This design prioritizes comprehensive feedback over fast failure detection.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:58-61](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:47-50]()

## Permissions Model

Both producer and consumer jobs require specific GitHub Actions permissions:

| Permission | Scope | Purpose |
|------------|-------|---------|
| `id-token` | `write` | AWS credential federation for sccache access |
| `contents` | `read` | Repository checkout |

The `id-token: write` permission enables OpenID Connect (OIDC) authentication with AWS, allowing jobs to access the S3-based sccache bucket without storing credentials in repository secrets.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:25-27](), [.github/workflows/workflow-dispatch-two-stage-linux.yml:51-53](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:25-27](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:44-46]()

## Configuration Flow Summary

```mermaid
graph TB
    subgraph "Generation Phase"
        Matrix["matrix.yaml<br/>job definitions"]
        BuildWorkflow["build-workflow.py<br/>validates single producer"]
        PrepareDispatch["prepare-workflow-dispatch.py<br/>creates dispatch.json"]
    end
    
    subgraph "dispatch.json"
        LinuxTS["linux_two_stage.jobs.&lt;name&gt;[*]:<br/>- producers: [producer_def]<br/>- consumers: [consumer_defs...]"]
        WindowsTS["windows_two_stage.jobs.&lt;name&gt;[*]:<br/>- producers: [producer_def]<br/>- consumers: [consumer_defs...]"]
    end
    
    subgraph "Group Dispatch"
        LinuxGroup["workflow-dispatch-two-stage-group-linux<br/>Matrix: pc-array"]
        WindowsGroup["workflow-dispatch-two-stage-group-windows<br/>Matrix: pc-array"]
    end
    
    subgraph "Two-Stage Execution"
        LinuxExec["workflow-dispatch-two-stage-linux<br/>inputs.producers, inputs.consumers"]
        WindowsExec["workflow-dispatch-two-stage-windows<br/>inputs.producers, inputs.consumers"]
    end
    
    Matrix --> BuildWorkflow
    BuildWorkflow --> PrepareDispatch
    PrepareDispatch --> LinuxTS
    PrepareDispatch --> WindowsTS
    
    LinuxTS --> LinuxGroup
    WindowsTS --> WindowsGroup
    
    LinuxGroup --> LinuxExec
    WindowsGroup --> WindowsExec
```

The producer-consumer pattern integrates with the broader workflow system through a multi-stage generation and dispatch process. The `build-workflow.py` script enforces the single-producer constraint during generation, and `prepare-workflow-dispatch.py` organizes producer-consumer pairs into the `dispatch.json` structure consumed by the two-stage workflows.

**Sources:** [.github/workflows/workflow-dispatch-two-stage-linux.yml:1-76](), [.github/workflows/workflow-dispatch-two-stage-windows.yml:1-62]()

---

# Page: Job Execution

# Job Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)
- [.github/actions/workflow-run-job-windows/action.yml](.github/actions/workflow-run-job-windows/action.yml)

</details>



## Purpose and Scope

This page documents the job execution layer of the cccl-gha system, which is responsible for running individual build and test commands in isolated environments. Job execution occurs after the dispatch layer ([4](#4)) routes jobs to appropriate execution workflows, and before the results collection system ([6](#6)) aggregates outputs.

This page covers the high-level execution architecture, the two platform-specific execution actions (`workflow-run-job-linux` and `workflow-run-job-windows`), execution flow patterns, and artifact collection mechanisms. For detailed information about platform-specific execution environments, see [Linux Execution Environment](#5.1) and [Windows Execution Environment](#5.2). For devcontainer configuration and launching, see [Devcontainer System](#5.3). For AWS credentials and sccache configuration, see [Environment Setup](#5.4). For error handling and local reproduction, see [Error Handling and Reproducibility](#5.5).

## Overview

Job execution is the final phase where actual build and test commands run in containerized environments. Each job executes in an isolated Docker container with:

- A job-specific devcontainer image selected based on CUDA version and compiler
- AWS credentials for distributed compilation caching via sccache
- The repository code checked out at the appropriate commit
- Environment variables propagated from GitHub Actions
- GPU access (when required)

The execution layer produces artifacts including success markers, sccache statistics, and benchmark data that the results collection system consumes for reporting.

Sources: [.github/actions/workflow-run-job-linux/action.yml:1-201](), [.github/actions/workflow-run-job-windows/action.yml:1-99]()

## Execution Actions

The system provides two composite GitHub Actions for job execution, one per operating system:

### Linux Execution Action

**File**: `.github/actions/workflow-run-job-linux/action.yml`

**Inputs**:
- `id`: Unique job identifier used for artifact naming
- `command`: Shell command to execute in the container
- `image`: Docker image name (not directly used; devcontainer selected by CUDA/host)
- `runner`: GitHub Actions runner label (e.g., `linux-amd64-gpu-v100-latest-1`)
- `cuda`: CUDA version for devcontainer selection (e.g., `12.4`)
- `host`: Host compiler for devcontainer selection (e.g., `gcc12`)

**Container Strategy**: Docker-outside-of-Docker (DOOD) using `cruizba/ubuntu-dind:jammy-26.1.3` as intermediate container

### Windows Execution Action

**File**: `.github/actions/workflow-run-job-windows/action.yml`

**Inputs**:
- `id`: Unique job identifier
- `command`: PowerShell command to execute
- `image`: Docker image to use directly (e.g., Windows Server Core with MSVC)

**Container Strategy**: Native Docker execution on Windows host

Sources: [.github/actions/workflow-run-job-linux/action.yml:22-41](), [.github/actions/workflow-run-job-windows/action.yml:4-13]()

## Execution Action Mapping

```mermaid
graph TB
    subgraph "Dispatch Layer"
        LinuxDispatch["workflow-dispatch-*-linux"]
        WindowsDispatch["workflow-dispatch-*-windows"]
    end
    
    subgraph "Execution Actions"
        LinuxAction["workflow-run-job-linux<br/>action.yml"]
        WindowsAction["workflow-run-job-windows<br/>action.yml"]
    end
    
    subgraph "Action Inputs"
        LinuxInputs["inputs.id<br/>inputs.command<br/>inputs.image<br/>inputs.runner<br/>inputs.cuda<br/>inputs.host"]
        WindowsInputs["inputs.id<br/>inputs.command<br/>inputs.image"]
    end
    
    subgraph "Execution Steps"
        LinuxSteps["1. Install dependencies<br/>2. Checkout repo<br/>3. Add NVCC problem matcher<br/>4. Get AWS credentials<br/>5. Run command<br/>6. Prepare job artifacts<br/>7. Upload job artifacts"]
        WindowsSteps["1. Configure env<br/>2. Get AWS credentials<br/>3. Checkout repo<br/>4. Fetch image<br/>5. Prepare paths<br/>6. Run command<br/>7. Prepare job artifacts<br/>8. Upload job artifacts"]
    end
    
    subgraph "Outputs"
        Artifacts["GitHub Artifacts:<br/>jobs-{id}/success<br/>jobs-{id}/sccache_stats.json<br/>jobs-{id}/cccl_meta_bench.csv"]
    end
    
    LinuxDispatch --> LinuxAction
    WindowsDispatch --> WindowsAction
    
    LinuxAction --> LinuxInputs
    WindowsAction --> WindowsInputs
    
    LinuxInputs --> LinuxSteps
    WindowsInputs --> WindowsSteps
    
    LinuxSteps --> Artifacts
    WindowsSteps --> Artifacts
```

This diagram maps the dispatch workflows to their corresponding execution actions, showing the specific input parameters each action expects and the sequence of steps they execute. Both actions produce identical artifact structures for consumption by the results collection system.

Sources: [.github/actions/workflow-run-job-linux/action.yml:22-201](), [.github/actions/workflow-run-job-windows/action.yml:4-99]()

## Execution Flow

The following sequence diagram illustrates the complete execution lifecycle for a single job:

```mermaid
sequenceDiagram
    participant Dispatch as "Dispatch Workflow"
    participant Action as "workflow-run-job-*"
    participant Checkout as "actions/checkout@v4"
    participant AWS as "aws-actions/configure-aws-credentials@v4"
    participant Container as "Execution Container"
    participant Command as "User Command"
    participant Artifacts as "actions/upload-artifact@v4"
    
    Dispatch->>Action: Call with job parameters
    
    Note over Action: Setup Phase
    Action->>Action: Install dependencies (Linux only)
    Action->>Checkout: Checkout repository
    Checkout-->>Action: Repository at github.workspace
    Action->>Action: Add NVCC problem matcher (Linux only)
    Action->>AWS: Get AWS credentials for sccache
    AWS-->>Action: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
    
    Note over Action: Execution Phase
    Action->>Action: Configure container environment
    Action->>Container: Launch with mounted repo, AWS creds, env vars
    Container->>Container: Setup sccache configuration
    Container->>Command: Execute inputs.command
    Command-->>Container: Exit code, stdout/stderr
    
    alt Command succeeds
        Container-->>Action: Exit 0
    else Command fails
        Container->>Container: Generate reproduction instructions
        Container-->>Action: Exit non-zero
    end
    
    Note over Action: Artifact Collection Phase
    Action->>Action: Create jobs/{id} directory
    Action->>Action: Touch success marker
    Action->>Action: Find and copy sccache_stats.json
    Action->>Action: Find and copy cccl_meta_bench.csv/db/log
    Action->>Artifacts: Upload jobs directory
    Artifacts-->>Dispatch: Artifact available
```

This sequence shows the three distinct phases: setup (repository checkout and credential configuration), execution (running the command in a container), and artifact collection (gathering outputs for results processing).

Sources: [.github/actions/workflow-run-job-linux/action.yml:44-201](), [.github/actions/workflow-run-job-windows/action.yml:17-99]()

## Platform Execution Patterns

The following table compares the execution characteristics between Linux and Windows platforms:

| Aspect | Linux Execution | Windows Execution |
|--------|-----------------|-------------------|
| **Container Strategy** | Docker-outside-of-Docker (DOOD) | Native Docker on Windows host |
| **Intermediate Container** | `cruizba/ubuntu-dind:jammy-26.1.3` | None |
| **Devcontainer Selection** | Dynamic via `.devcontainer/launch.sh` with `--cuda` and `--host` flags | Static via `inputs.image` |
| **Repository Mount** | Complex: symlink + volume mount to match host paths | Direct: bind mount from host to `C:/{repo}` |
| **Command Shell** | Bash via generated `ci.sh` wrapper script | PowerShell via inline script |
| **GPU Access** | `--gpus device=${NVIDIA_VISIBLE_DEVICES}` when runner contains `-gpu-` | Not configured (Windows GPU runners not in use) |
| **Path Handling** | Requires `host_path()` transformation for volume mounts | Requires PowerShell path transformation (`\` to `/`) |
| **Environment Variable Injection** | Via `--env` flags to `launch.sh` | Via `[System.Environment]::SetEnvironmentVariable` in PowerShell |
| **Problem Matchers** | NVCC problem matcher added | Not configured |
| **Artifact Files** | `success`, `sccache_stats.json`, `cccl_meta_bench.{csv,db,log}` | `success`, `sccache_stats.json` |

Sources: [.github/actions/workflow-run-job-linux/action.yml:4-164](), [.github/actions/workflow-run-job-windows/action.yml:15-64]()

## Docker-Outside-of-Docker Pattern (Linux)

Linux execution uses a DOOD strategy to avoid performance issues with nested Docker (Docker-in-Docker). The pattern has three layers:

```mermaid
graph TB
    subgraph "Layer 1: GitHub Actions Runner Host"
        RunnerHost["Linux Runner Host"]
        DockerDaemon["Docker Daemon<br/>/var/run/docker.sock"]
        HostWorkspace["Host Filesystem<br/>/home/runner/_work"]
    end
    
    subgraph "Layer 2: Intermediate Container"
        DindContainer["cruizba/ubuntu-dind:jammy-26.1.3"]
        DockerCLI["Docker CLI"]
        RepoCheckout["Repository Checkout<br/>github.event.repository.name/"]
        CiShWrapper["ci.sh wrapper script"]
        Symlink["Symlink:<br/>GITHUB_WORKSPACE → PWD"]
        LaunchScript[".devcontainer/launch.sh"]
    end
    
    subgraph "Layer 3: DevContainer"
        DevContainer["Job-Specific DevContainer<br/>selected by CUDA + host"]
        ActualCommand["Execute COMMAND"]
    end
    
    RunnerHost --> DockerDaemon
    DockerDaemon -->|mounted at /var/run/docker.sock| DindContainer
    
    DindContainer --> DockerCLI
    DindContainer --> RepoCheckout
    DindContainer --> CiShWrapper
    DindContainer --> Symlink
    
    RepoCheckout --> LaunchScript
    CiShWrapper --> LaunchScript
    Symlink -->|ensures path consistency| LaunchScript
    
    DockerCLI -->|docker run on host daemon| DevContainer
    LaunchScript -->|orchestrates| DockerCLI
    
    DevContainer --> ActualCommand
    
    HostWorkspace -.->|volume mounts reference host paths| DevContainer
```

**Key Implementation Details**:

1. **Socket Mounting**: The runner host's Docker socket is mounted into the intermediate container, allowing the Docker CLI in `ubuntu-dind` to communicate with the host daemon: [.github/actions/workflow-run-job-linux/action.yml:6-8]()

2. **Path Symlink**: A critical symlink ensures the intermediate container's working directory matches the host's `github.workspace` path, because Docker volume mounts must reference host paths: [.github/actions/workflow-run-job-linux/action.yml:82-87]()

3. **Host Path Transformation**: The `host_path()` function converts container paths to host paths for volume mount specifications: [.github/actions/workflow-run-job-linux/action.yml:138-140]()

4. **Launch Script Invocation**: The `.devcontainer/launch.sh` script receives the `--docker` flag to use the host daemon, along with CUDA/host parameters to select the appropriate devcontainer: [.github/actions/workflow-run-job-linux/action.yml:144-164]()

Sources: [.github/actions/workflow-run-job-linux/action.yml:4-164]()

## Native Docker Pattern (Windows)

Windows execution uses a simpler pattern with direct Docker container invocation:

```mermaid
graph TB
    subgraph "Windows Runner Host"
        WindowsHost["Windows Runner"]
        WindowsDocker["Docker Desktop"]
        HostRepo["Host Repository<br/>github.workspace\repo"]
    end
    
    subgraph "Docker Container"
        WindowsContainer["Windows Container<br/>inputs.image"]
        MountedRepo["Mounted Repository<br/>C:/repo"]
        PowerShell["PowerShell"]
        SetEnv["Environment Variable Setup"]
        GitConfig["git config --global --add safe.directory"]
        Command["Execute inputs.command"]
    end
    
    WindowsHost --> WindowsDocker
    WindowsDocker --> WindowsContainer
    
    HostRepo -->|bind mount| MountedRepo
    
    WindowsContainer --> PowerShell
    PowerShell --> SetEnv
    SetEnv --> GitConfig
    GitConfig --> Command
```

**Key Implementation Details**:

1. **Path Transformation**: PowerShell converts Windows backslash paths to forward slashes for Docker mount compatibility: [.github/actions/workflow-run-job-windows/action.yml:40-46]()

2. **Environment Variable Injection**: PowerShell's `[System.Environment]::SetEnvironmentVariable` sets AWS credentials and sccache configuration inside the container: [.github/actions/workflow-run-job-windows/action.yml:55-62]()

3. **Git Safe Directory**: The repository mount path is added to Git's safe directory list to prevent ownership errors: [.github/actions/workflow-run-job-windows/action.yml:63]()

4. **Direct Docker Run**: Unlike Linux, Windows executes `docker run` directly from the runner without an intermediate container: [.github/actions/workflow-run-job-windows/action.yml:50-64]()

Sources: [.github/actions/workflow-run-job-windows/action.yml:40-64]()

## Artifact Collection

Both Linux and Windows execution actions follow an identical artifact collection pattern:

```mermaid
graph LR
    subgraph "Post-Execution"
        Complete["Command Completes"]
    end
    
    subgraph "Artifact Preparation"
        CreateDir["Create jobs/{id} directory"]
        TouchSuccess["Touch success marker"]
        FindFiles["Find and copy files"]
    end
    
    subgraph "Artifact Files"
        Success["jobs/{id}/success"]
        Sccache["jobs/{id}/sccache_stats.json"]
        Bench["jobs/{id}/cccl_meta_bench.csv"]
        BenchDB["jobs/{id}/cccl_meta_bench.db"]
        BenchLog["jobs/{id}/cccl_meta_bench.log"]
    end
    
    subgraph "Upload"
        Upload["actions/upload-artifact@v4<br/>name: jobs-{id}<br/>path: jobs"]
    end
    
    Complete --> CreateDir
    CreateDir --> TouchSuccess
    TouchSuccess --> FindFiles
    
    FindFiles --> Success
    FindFiles --> Sccache
    FindFiles --> Bench
    FindFiles --> BenchDB
    FindFiles --> BenchLog
    
    Success --> Upload
    Sccache --> Upload
    Bench --> Upload
    BenchDB --> Upload
    BenchLog --> Upload
```

**Artifact File Specifications**:

| File | Purpose | Always Present |
|------|---------|----------------|
| `success` | Marker file indicating job completed (even if tests failed) | Yes |
| `sccache_stats.json` | Compilation cache statistics from sccache | No (only if sccache used) |
| `cccl_meta_bench.csv` | Benchmark results in CSV format | No (only if benchmarks run) |
| `cccl_meta_bench.db` | Benchmark database | No (only if benchmarks run) |
| `cccl_meta_bench.log` | Benchmark execution log | No (only if benchmarks run) |

**Implementation Details**:

1. **Success Marker**: The `success` file is always created, even if the command failed. Its presence indicates the job executed, not that tests passed. Absence indicates the workflow or container setup failed: [.github/actions/workflow-run-job-linux/action.yml:173](), [.github/actions/workflow-run-job-windows/action.yml:74]()

2. **Find and Copy Pattern**: The `find_and_copy()` bash function searches the repository directory recursively for specific filenames and copies them to the results directory. Missing files are tolerated: [.github/actions/workflow-run-job-linux/action.yml:176-189](), [.github/actions/workflow-run-job-windows/action.yml:76-88]()

3. **Artifact Naming**: Artifacts are uploaded with the name pattern `jobs-{id}` where `id` is the unique job identifier. This allows the results collection system to download and merge artifacts from all jobs: [.github/actions/workflow-run-job-linux/action.yml:198-199](), [.github/actions/workflow-run-job-windows/action.yml:96-97]()

4. **No Compression**: Artifacts use `compression-level: 0` to speed up upload/download at the cost of storage space: [.github/actions/workflow-run-job-linux/action.yml:200](), [.github/actions/workflow-run-job-windows/action.yml:98]()

Sources: [.github/actions/workflow-run-job-linux/action.yml:166-201](), [.github/actions/workflow-run-job-windows/action.yml:65-99]()

## Error Handling and Reproduction Instructions

When a command fails during execution, the Linux action generates detailed reproduction instructions:

```mermaid
graph TB
    subgraph "ci.sh Wrapper Script"
        EvalCommand["eval COMMAND"]
        CheckExit["Check exit_code"]
    end
    
    subgraph "Failure Path"
        ErrorGroup["Open ::group:: in GitHub Actions"]
        CloneInstr["echo git clone instructions"]
        CheckoutInstr["echo git checkout SHA"]
        DockerInstr["echo .devcontainer/launch.sh command"]
        DocLinks["echo documentation links"]
        ErrorAnnotation["::error:: annotation"]
        Exit["exit with exit_code"]
    end
    
    EvalCommand --> CheckExit
    CheckExit -->|exit_code != 0| ErrorGroup
    ErrorGroup --> CloneInstr
    CloneInstr --> CheckoutInstr
    CheckoutInstr --> DockerInstr
    DockerInstr --> DocLinks
    DocLinks --> ErrorAnnotation
    ErrorAnnotation --> Exit
```

**Generated Instructions Example**:

The failure output includes:
1. Repository clone command with correct branch: `git clone --branch $GITHUB_REF_NAME --single-branch`
2. Commit checkout: `git checkout $GITHUB_SHA`
3. Docker launch command with exact parameters: `.devcontainer/launch.sh -d -c {cuda} -H {host} -- {command}`
4. Links to devcontainer documentation and CI overview

This allows developers to reproduce CI failures locally with identical container, compiler, and CUDA versions.

Sources: [.github/actions/workflow-run-job-linux/action.yml:94-108]()

## Integration Points

The execution layer integrates with several external systems:

| System | Integration Point | Purpose |
|--------|-------------------|---------|
| **GitHub Actions API** | `actions/checkout@v4` | Repository code checkout at specific commit |
| **GitHub Actions API** | `actions/upload-artifact@v4` | Artifact upload for results collection |
| **AWS IAM** | `aws-actions/configure-aws-credentials@v4` | OIDC authentication for sccache S3 bucket |
| **AWS S3** | Environment variables in container | sccache distributed compilation cache |
| **DevContainer System** | `.devcontainer/launch.sh` (Linux) | Dynamic container selection and launching |
| **Problem Matchers** | `.github/problem-matchers/problem-matcher.json` | NVCC error annotation in GitHub Actions UI |
| **Dispatch Layer** | Action inputs from workflow matrix | Job parameters and configuration |
| **Results Collection** | Uploaded artifacts | Success verification and reporting |

Sources: [.github/actions/workflow-run-job-linux/action.yml:52-65](), [.github/actions/workflow-run-job-linux/action.yml:144-164](), [.github/actions/workflow-run-job-windows/action.yml:26-31]()

---

# Page: Linux Execution Environment

# Linux Execution Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)

</details>



## Purpose and Scope

This document describes the Linux job execution environment used by the cccl-gha system. It covers the Docker-outside-of-Docker (DOOD) architecture, path management strategies, GPU resource allocation, and how jobs execute commands within devcontainers on Linux runners.

For Windows execution details, see [Windows Execution Environment](#5.2). For devcontainer configuration and verification, see [Devcontainer System](#5.3). For AWS credentials and sccache setup, see [Environment Setup](#5.4). For error handling and the `ci.sh` wrapper script, see [Error Handling and Reproducibility](#5.5).

---

## Architecture Overview

The Linux execution environment uses a **Docker-outside-of-Docker (DOOD)** pattern to avoid performance degradation and complexity issues associated with Docker-in-Docker. This three-layer architecture allows the system to run GitHub Actions (which require Node.js v20) while also supporting legacy Ubuntu 18.04-based devcontainers needed for older GCC versions.

**Container Hierarchy Diagram**

```mermaid
graph TB
    subgraph HostLayer["GitHub Actions Runner Host"]
        DockerDaemon["Docker Daemon<br/>/var/run/docker.sock"]
        HostGPU["NVIDIA GPU<br/>NVIDIA_VISIBLE_DEVICES"]
        HostWorkspace["Host Filesystem<br/>/home/runner/_work"]
    end
    
    subgraph IntermediateLayer["Intermediate Container: ubuntu-dind"]
        DindImage["cruizba/ubuntu-dind:jammy-26.1.3"]
        GitCheckout["Repository Checkout<br/>actions/checkout@v4"]
        CiShGenerator["ci.sh Generator"]
        AWSSetup["AWS Credentials Setup<br/>RUNNER_TEMP/.aws"]
        PathSymlink["Path Symlink Creation<br/>ln -s pwd github.workspace"]
        LaunchInvocation["launch.sh Invocation"]
    end
    
    subgraph DevcontainerLayer["Target Devcontainer"]
        DevImage["Job-Specific Image<br/>matrix.image"]
        CiShExecution["ci.sh Execution<br/>eval COMMAND"]
        SccacheClient["sccache Client"]
        CommandOutput["Build/Test Output"]
    end
    
    DockerDaemon -->|socket mounted| DindImage
    HostGPU -->|env var passed| DindImage
    HostWorkspace -->|volume mount| DindImage
    
    DindImage --> GitCheckout
    GitCheckout --> CiShGenerator
    CiShGenerator --> AWSSetup
    AWSSetup --> PathSymlink
    PathSymlink --> LaunchInvocation
    
    LaunchInvocation -->|docker run via host daemon| DevImage
    DockerDaemon -.->|actually launches| DevImage
    
    DevImage --> CiShExecution
    CiShExecution --> SccacheClient
    CiShExecution --> CommandOutput
    
    SccacheClient -.->|S3 API| AWSBucket["AWS S3<br/>rapids-sccache-devs"]
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:4-20]()

### Key Components

| Component | Description | Implementation |
|-----------|-------------|----------------|
| **Runner Host** | GitHub Actions runner with Docker daemon | Native Linux host with GPU support |
| **Intermediate Container** | `cruizba/ubuntu-dind:jammy-26.1.3` | Provides Docker CLI + Node.js v20 for GHA actions |
| **Target Devcontainer** | Job-specific image (e.g., `ubuntu18.04-gcc7-cuda11.1`) | Executes actual build/test commands |
| **Docker Socket** | `/var/run/docker.sock` | Mounted from host to intermediate container |
| **launch.sh** | Devcontainer launch script | Located in `.devcontainer/launch.sh` |
| **ci.sh** | Generated command wrapper | Created at runtime, mounted into devcontainer |

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:1-21]()

---

## Path Management and Symlinks

A critical challenge in the DOOD architecture is that Docker volume mounts must reference **host filesystem paths**, not paths as seen within the intermediate container. The system solves this through a symlink strategy.

**Path Transformation Strategy**

```mermaid
graph LR
    subgraph "Host Paths"
        HostWork["/home/runner/_work"]
        HostRepo["/home/runner/_work/repo-name/repo-name"]
    end
    
    subgraph "Intermediate Container Paths"
        ContainerPwd["PWD: /__w/repo-name/repo-name"]
        GitHubWorkspace["github.workspace symlink"]
        Symlink["ln -s PWD github.workspace"]
    end
    
    subgraph "Docker Volume Mount"
        MountSpec["--volume HOST_PATH:/__w"]
        HostPathFunc["host_path function<br/>sed s@/__w@/home/runner/_work@"]
    end
    
    subgraph "Devcontainer Paths"
        DevWorkspace["/__w/repo-name/repo-name"]
    end
    
    HostWork -.->|mounted as| ContainerPwd
    ContainerPwd --> Symlink
    Symlink --> GitHubWorkspace
    
    GitHubWorkspace -.->|used by| LaunchScript["launch.sh pwd command"]
    LaunchScript --> MountSpec
    HostPathFunc --> MountSpec
    MountSpec --> DevWorkspace
    
    HostRepo -.->|actual physical path| DevWorkspace
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:82-87](), [.github/actions/workflow-run-job-linux/action.yml:138-140]()

### Symlink Creation

The intermediate container creates a symlink to ensure that `$(pwd)` matches the `github.workspace` value used by GitHub Actions:

[.github/actions/workflow-run-job-linux/action.yml:82-87]()
```yaml
# Make a symlink in the container that matches the host's ${{github.workspace}}
mkdir -p "$(dirname "${{github.workspace}}")"
ln -s "$(pwd)" "${{github.workspace}}"
cd "${{github.workspace}}"
```

### Path Translation Function

The `host_path()` function translates container paths to host paths for Docker volume mounts:

[.github/actions/workflow-run-job-linux/action.yml:138-140]()
```bash
host_path() {
  sed "s@/__w@$(dirname "$(dirname "${{github.workspace}}")")@" <<< "$1"
}
```

This function replaces the container's `/__w` prefix with the host's actual workspace parent directory (typically `/home/runner/_work`).

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:78-87](), [.github/actions/workflow-run-job-linux/action.yml:138-164]()

---

## Job Execution Flow

**Execution Sequence Diagram**

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions Runner
    participant Dind as ubuntu-dind Container
    participant Host as Host Docker Daemon
    participant Dev as Devcontainer
    participant S3 as AWS S3 rapids-sccache-devs
    
    Note over GHA,Dind: Intermediate Container Launches
    GHA->>Dind: Start cruizba/ubuntu-dind:jammy-26.1.3
    Note over Dind: Mount /var/run/docker.sock from host
    
    Note over Dind: Install Dependencies
    Dind->>Dind: apt update && apt install tree git
    
    Note over Dind: Checkout Repository
    Dind->>Dind: actions/checkout@v4
    
    Note over Dind: Configure Problem Matchers
    Dind->>Dind: add-matcher problem-matcher.json
    
    Note over Dind: Setup AWS Credentials
    Dind->>Dind: aws-actions/configure-aws-credentials@v4
    Dind->>Dind: Create RUNNER_TEMP/.aws/config
    Dind->>Dind: Create RUNNER_TEMP/.aws/credentials
    
    Note over Dind: Path Management
    Dind->>Dind: ln -s $(pwd) github.workspace
    
    Note over Dind: Generate ci.sh Wrapper
    Dind->>Dind: cat > ci.sh (lines 89-109)
    Dind->>Dind: chmod +x ci.sh
    
    Note over Dind: Determine GPU Request
    Dind->>Dind: Check if RUNNER contains "-gpu-"
    Dind->>Dind: Set --gpus device=NVIDIA_VISIBLE_DEVICES
    
    Note over Dind: Launch Devcontainer
    Dind->>Host: .devcontainer/launch.sh --docker --cuda X --host Y
    Host->>Dev: docker run (via host daemon)
    Note over Dev: Volume mounts:<br/>- ci.sh:/ci.sh<br/>- .aws:/root/.aws<br/>- workspace:/__w
    
    Note over Dev: Execute Command
    Dev->>Dev: /ci.sh (bash wrapper)
    Dev->>Dev: eval "${COMMAND}"
    Dev->>S3: sccache GET/PUT requests
    S3-->>Dev: Cached compilation objects
    Dev->>Dev: Build/Test execution
    
    alt Command Succeeds
        Dev-->>Dind: Exit code 0
    else Command Fails
        Dev->>Dev: Generate reproduction instructions
        Dev-->>Dind: Exit code non-zero
    end
    
    Dind-->>GHA: Command complete
    
    Note over Dind: Prepare Artifacts
    Dind->>Dind: mkdir jobs/{id}
    Dind->>Dind: touch jobs/{id}/success
    Dind->>Dind: find_and_copy sccache_stats.json
    Dind->>Dind: find_and_copy cccl_meta_bench.csv
    
    Note over Dind: Upload Artifacts
    Dind->>GHA: actions/upload-artifact@v4
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:44-201]()

### Step-by-Step Breakdown

| Step | Description | Lines |
|------|-------------|-------|
| **Install Dependencies** | Install `tree` and `git` in intermediate container | [45-50]() |
| **Checkout Repo** | Clone repository using `actions/checkout@v4` | [51-55]() |
| **Add Problem Matcher** | Register NVCC error pattern matcher | [56-59]() |
| **AWS Credentials** | Obtain temporary credentials via OIDC | [60-65]() |
| **Run Command** | Core execution step (name matters for parsing) | [66-165]() |
| **Prepare Artifacts** | Create success marker and copy result files | [166-193]() |
| **Upload Artifacts** | Upload to GitHub Actions artifact storage | [195-200]() |

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:44-201]()

---

## GPU Resource Allocation

The system detects GPU runners by examining the `RUNNER` input value and configures GPU access accordingly.

**GPU Detection and Configuration**

```mermaid
graph TD
    RunnerInput["inputs.runner value"]
    GpuCheck{"Contains '-gpu-'?"}
    GpuRequest["gpu_request array"]
    GpuFlag["--gpus device=$NVIDIA_VISIBLE_DEVICES"]
    NoGpu["Empty array"]
    LaunchScript["launch.sh invocation"]
    
    RunnerInput --> GpuCheck
    GpuCheck -->|Yes| GpuFlag
    GpuCheck -->|No| NoGpu
    GpuFlag --> GpuRequest
    NoGpu --> GpuRequest
    GpuRequest --> LaunchScript
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:131-136]()

### GPU Detection Logic

[.github/actions/workflow-run-job-linux/action.yml:131-136]()
```bash
declare -a gpu_request=()

# Explicitly pass which GPU to use if on a GPU runner
if [[ "${RUNNER}" = *"-gpu-"* ]]; then
  gpu_request+=(--gpus "device=${NVIDIA_VISIBLE_DEVICES}")
fi
```

The `NVIDIA_VISIBLE_DEVICES` environment variable is set by the GitHub Actions runner and contains the specific GPU device ID(s) allocated to the job. This value is passed through to the devcontainer via the `--gpus` Docker flag.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:131-148]()

---

## Environment Variable Propagation

The system propagates critical GitHub Actions context variables and AWS credentials into the devcontainer to maintain CI environment consistency.

**Environment Variables Passed to Devcontainer**

| Variable | Purpose | Source |
|----------|---------|--------|
| `CI` | Indicates CI environment | Set to `true` in action |
| `COMMAND` | The command to execute | From `inputs.command` |
| `GITHUB_ENV` | Env file for setting variables | GitHub Actions context |
| `GITHUB_SHA` | Commit SHA being tested | GitHub Actions context |
| `GITHUB_PATH` | Path modification file | GitHub Actions context |
| `GITHUB_OUTPUT` | Output variable file | GitHub Actions context |
| `GITHUB_ACTIONS` | GitHub Actions flag | GitHub Actions context |
| `GITHUB_REF_NAME` | Branch/tag name | GitHub Actions context |
| `GITHUB_WORKSPACE` | Workspace directory path | GitHub Actions context |
| `GITHUB_REPOSITORY` | Repository slug (owner/repo) | GitHub Actions context |
| `GITHUB_STEP_SUMMARY` | Summary markdown file | GitHub Actions context |
| `VAULT_HOST` | Vault host (set to empty) | Explicitly disabled |

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:149-160]()

### launch.sh Invocation

[.github/actions/workflow-run-job-linux/action.yml:144-164]()
```bash
${{github.event.repository.name}}/.devcontainer/launch.sh \
  --docker \
  --cuda ${{inputs.cuda}} \
  --host ${{inputs.host}} \
  "${gpu_request[@]}" \
  --env "CI=$CI" \
  --env "VAULT_HOST=" \
  --env "COMMAND=$COMMAND" \
  --env "GITHUB_ENV=$GITHUB_ENV" \
  --env "GITHUB_SHA=$GITHUB_SHA" \
  --env "GITHUB_PATH=$GITHUB_PATH" \
  --env "GITHUB_OUTPUT=$GITHUB_OUTPUT" \
  --env "GITHUB_ACTIONS=$GITHUB_ACTIONS" \
  --env "GITHUB_REF_NAME=$GITHUB_REF_NAME" \
  --env "GITHUB_WORKSPACE=$GITHUB_WORKSPACE" \
  --env "GITHUB_REPOSITORY=$GITHUB_REPOSITORY" \
  --env "GITHUB_STEP_SUMMARY=$GITHUB_STEP_SUMMARY" \
  --volume "${{github.workspace}}/ci.sh:/ci.sh" \
  --volume "$(host_path "$RUNNER_TEMP")/.aws:/root/.aws" \
  --volume "$(dirname "$(dirname "${{github.workspace}}")"):/__w" \
  -- /ci.sh
```

The `launch.sh` script (documented in [Devcontainer System](#5.3)) uses these arguments to:
1. Select the appropriate devcontainer image based on `--cuda` and `--host` values
2. Configure Docker run arguments including GPU flags
3. Mount volumes for the repository, `ci.sh` script, and AWS credentials
4. Pass environment variables into the container
5. Execute `/ci.sh` as the container entrypoint

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:144-164]()

---

## AWS Credentials Configuration

AWS credentials are configured for sccache to access the `rapids-sccache-devs` S3 bucket for distributed compilation caching.

**AWS Credentials Flow**

```mermaid
graph TD
    OidcAction["aws-actions/configure-aws-credentials@v4"]
    AssumeRole["Assume IAM Role:<br/>arn:aws:iam::279114543810:role/gha-oidc-NVIDIA"]
    EnvVars["Environment Variables:<br/>AWS_ACCESS_KEY_ID<br/>AWS_SESSION_TOKEN<br/>AWS_SECRET_ACCESS_KEY"]
    ConfigFile["RUNNER_TEMP/.aws/config<br/>bucket=rapids-sccache-devs<br/>region=us-east-2"]
    CredFile["RUNNER_TEMP/.aws/credentials<br/>[default] section with keys"]
    VolumeMount["--volume RUNNER_TEMP/.aws:/root/.aws"]
    DevContainer["Devcontainer /root/.aws"]
    Sccache["sccache reads config"]
    
    OidcAction --> AssumeRole
    AssumeRole --> EnvVars
    EnvVars --> ConfigFile
    EnvVars --> CredFile
    CredFile --> VolumeMount
    ConfigFile --> VolumeMount
    VolumeMount --> DevContainer
    DevContainer --> Sccache
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:60-65](), [.github/actions/workflow-run-job-linux/action.yml:113-129]()

### IAM Role Assumption

[.github/actions/workflow-run-job-linux/action.yml:60-65]()
```yaml
- name: Get AWS credentials for sccache bucket
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::279114543810:role/gha-oidc-NVIDIA
    aws-region: us-east-2
    role-duration-seconds: 43200 # 12 hours
```

This action uses OpenID Connect (OIDC) to obtain temporary AWS credentials without storing long-lived secrets. The role duration is set to 12 hours to cover long-running build jobs.

### Credentials File Generation

[.github/actions/workflow-run-job-linux/action.yml:113-129]()
```bash
mkdir "$RUNNER_TEMP/.aws";

cat <<EOF > "$RUNNER_TEMP/.aws/config"
[default]
bucket=rapids-sccache-devs
region=us-east-2
EOF

cat <<EOF > "$RUNNER_TEMP/.aws/credentials"
[default]
aws_access_key_id=$AWS_ACCESS_KEY_ID
aws_session_token=$AWS_SESSION_TOKEN
aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
EOF

chmod 0600 "$RUNNER_TEMP/.aws/credentials"
chmod 0664 "$RUNNER_TEMP/.aws/config"
```

These files are mounted into the devcontainer at `/root/.aws`, where sccache automatically discovers them.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:113-129](), [.github/actions/workflow-run-job-linux/action.yml:162]()

---

## ci.sh Wrapper Script

The `ci.sh` wrapper script provides command execution with error handling and reproduction instructions.

**ci.sh Generation**

```mermaid
graph TD
    CommandInput["inputs.command"]
    EnvVar["COMMAND environment variable"]
    HeredocGen["cat > ci.sh heredoc<br/>lines 89-109"]
    ShebangLine["#!/usr/bin/env bash"]
    SetOptions["set -eo pipefail"]
    EchoUser["echo Running as whoami"]
    EchoCommand["echo COMMAND"]
    EvalCommand["eval COMMAND"]
    CaptureExit["exit_code=$?"]
    ErrorInstructions["::error:: reproduction instructions"]
    ChmodExec["chmod +x ci.sh"]
    VolumeMount["--volume ci.sh:/ci.sh"]
    Execution["/ci.sh in devcontainer"]
    
    CommandInput --> EnvVar
    EnvVar --> HeredocGen
    HeredocGen --> ShebangLine
    ShebangLine --> SetOptions
    SetOptions --> EchoUser
    EchoUser --> EchoCommand
    EchoCommand --> EvalCommand
    EvalCommand --> CaptureExit
    CaptureExit --> ErrorInstructions
    HeredocGen --> ChmodExec
    ChmodExec --> VolumeMount
    VolumeMount --> Execution
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:89-111]()

### Script Contents

[.github/actions/workflow-run-job-linux/action.yml:89-109]()
```bash
cat <<"EOF" > ci.sh
#! /usr/bin/env bash
set -eo pipefail
echo -e "\e[1;34mRunning as '$(whoami)' user in $(pwd):\e[0m"
echo -e "\e[1;34m${COMMAND}\e[0m"
eval "${COMMAND}" || exit_code=$?
if [ ! -z "$exit_code" ]; then
  echo -e "::group::️❗ \e[1;31mInstructions to Reproduce CI Failure Locally\e[0m"
  echo "::error:: To replicate this failure locally, follow the steps below:"
  echo "1. Clone the repository, and navigate to the correct branch and commit:"
  echo "   git clone --branch $GITHUB_REF_NAME --single-branch https://github.com/$GITHUB_REPOSITORY.git && cd $(echo $GITHUB_REPOSITORY | cut -d'/' -f2) && git checkout $GITHUB_SHA"
  echo ""
  echo "2. Run the failed command inside the same Docker container used by this CI job:"
  echo "   .devcontainer/launch.sh -d -c ${{inputs.cuda}} -H ${{inputs.host}} -- ${COMMAND}"
  echo ""
  echo "For additional information, see:"
  echo "   - DevContainer Documentation: https://github.com/NVIDIA/cccl/blob/main/.devcontainer/README.md"
  echo "   - Continuous Integration (CI) Overview: https://github.com/NVIDIA/cccl/blob/main/ci-overview.md"
  exit $exit_code
fi
EOF
```

The script uses:
- `set -eo pipefail`: Exit on error and propagate pipe failures
- `eval "${COMMAND}"`: Execute the command string (supports complex commands with semicolons, pipes, etc.)
- Conditional error handling that only triggers on failure
- GitHub Actions annotations (`::error::` and `::group::`) for UI integration
- Detailed reproduction instructions with exact git commands and Docker invocation

**Note:** The name "Run command" at [line 66]() is significant—it is parsed by `parse-job-times.py` to extract timing data.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:66-109]()

---

## Artifact Collection

After command execution, the system collects job artifacts for result reporting.

**Artifact Collection Process**

```mermaid
graph TD
    CommandComplete["Command Execution Complete"]
    CreateDir["mkdir jobs/$inputs.id"]
    SuccessMarker["touch jobs/$inputs.id/success"]
    FindAndCopy["find_and_copy function"]
    SearchRepo["find $repo -name filename"]
    CopyFile["cp filepath result_dir"]
    
    Files["Collected Files:<br/>- success (always)<br/>- sccache_stats.json (optional)<br/>- cccl_meta_bench.csv (optional)<br/>- cccl_meta_bench.db (optional)<br/>- cccl_meta_bench.log (optional)"]
    
    TreeDisplay["tree jobs/$inputs.id"]
    UploadArtifact["actions/upload-artifact@v4<br/>name: jobs-$inputs.id"]
    
    CommandComplete --> CreateDir
    CreateDir --> SuccessMarker
    SuccessMarker --> FindAndCopy
    FindAndCopy --> SearchRepo
    SearchRepo --> CopyFile
    CopyFile --> Files
    Files --> TreeDisplay
    TreeDisplay --> UploadArtifact
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:166-200]()

### find_and_copy Function

[.github/actions/workflow-run-job-linux/action.yml:176-184]()
```bash
find_and_copy() {
  filename="$1"
  filepath="$(find ${{github.event.repository.name}} -name "${filename}" -print -quit)"
  if [[ -z "$filepath" ]]; then
    echo "${filename} does not exist in repo directory."
    return 1
  fi
  cp -v "$filepath" "$result_dir"
}
```

This function searches the repository directory for files by name and copies them to the results directory. The `|| :` suffix makes failures non-fatal.

### Collected Artifacts

| Artifact | Purpose | Always Present |
|----------|---------|----------------|
| `success` | Marker indicating job completed | Yes |
| `sccache_stats.json` | Compilation cache statistics | No (build jobs only) |
| `cccl_meta_bench.csv` | Benchmark results CSV | No (benchmark jobs only) |
| `cccl_meta_bench.db` | Benchmark database | No (benchmark jobs only) |
| `cccl_meta_bench.log` | Benchmark execution log | No (benchmark jobs only) |

The artifacts are uploaded with `compression-level: 0` to minimize upload time, as the files are typically already compressed or small.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:166-200]()

---

## Action Inputs

The `workflow-run-job-linux` action accepts the following inputs:

| Input | Description | Required | Example |
|-------|-------------|----------|---------|
| `id` | Unique job identifier | Yes | `libcudacxx-gcc7-cuda11.1-tests` |
| `command` | Command to execute | Yes | `cmake --build build && ctest` |
| `image` | Docker image name | Yes | `ubuntu18.04-gcc7-cuda11.1` |
| `runner` | GitHub Actions runner label | Yes | `linux-amd64-cpu16` or `linux-amd64-gpu-v100-latest-1` |
| `cuda` | CUDA version for devcontainer selection | Yes | `11.1` |
| `host` | Host compiler for devcontainer selection | Yes | `gcc7` |

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:22-40]()

---

## Summary

The Linux execution environment implements a sophisticated Docker-outside-of-Docker pattern that enables:

1. **Compatibility**: Running modern GitHub Actions (Node.js v20) while supporting legacy Ubuntu 18.04 devcontainers
2. **Isolation**: Each job executes in a dedicated devcontainer with specific CUDA and compiler versions
3. **Performance**: DOOD avoids nested Docker overhead while maintaining containerization benefits
4. **GPU Access**: Seamless GPU allocation via `NVIDIA_VISIBLE_DEVICES` passthrough
5. **Distributed Caching**: Automatic sccache integration with AWS S3 for faster compilation
6. **Developer Experience**: Detailed error messages with exact reproduction instructions
7. **Path Consistency**: Symlink strategy ensures volume mounts work correctly across container layers

The system is implemented primarily in [.github/actions/workflow-run-job-linux/action.yml]() with integration points to `.devcontainer/launch.sh` for devcontainer selection and launching.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:1-201]()

---

# Page: Windows Execution Environment

# Windows Execution Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-run-job-windows/action.yml](.github/actions/workflow-run-job-windows/action.yml)

</details>



## Purpose and Scope

This document describes how jobs execute on Windows runners in the CCCL GitHub Actions workflow orchestration system. Unlike the Linux execution environment which uses a Docker-outside-of-Docker (DOOD) pattern [see page 5.1](#5.1), Windows jobs run Docker containers directly on the Windows host. This page covers the path transformation system, container configuration, environment variable propagation, and artifact collection specific to Windows execution.

For information about devcontainer configurations that define the Docker images used, see [Devcontainer System](#5.3). For details on environment setup including AWS credentials and sccache configuration, see [Environment Setup](#5.4).

## Execution Architecture

Windows job execution is implemented in the composite action `workflow-run-job-windows`, which runs directly on Windows GitHub Actions runners without an intermediate container layer. The architecture is simpler than the Linux DOOD pattern but requires special handling for path transformations between Windows and Unix conventions.

### Execution Flow Diagram

```mermaid
graph TB
    Dispatcher["workflow-dispatch-*-group-windows<br/>Matrix Job Dispatcher"]
    Action["workflow-run-job-windows<br/>Composite Action"]
    
    subgraph Runner["GitHub Actions Windows Runner"]
        Configure["Configure env<br/>lines 18-25"]
        AWS["Get AWS credentials<br/>lines 26-31"]
        Checkout["Checkout repo<br/>lines 32-36"]
        Pull["Fetch Docker Image<br/>lines 37-39"]
        PathPrep["Prepare paths for docker<br/>lines 40-46<br/>(PowerShell)"]
        DockerRun["Run command<br/>lines 47-64<br/>(bash + docker)"]
        Artifacts["Prepare job artifacts<br/>lines 65-91"]
        Upload["Upload job artifacts<br/>lines 93-98"]
    end
    
    subgraph Container["Windows Docker Container"]
        PSEnv["PowerShell Environment Setup<br/>SetEnvironmentVariable calls"]
        GitConfig["Git safe.directory config"]
        Command["Execute inputs.command"]
    end
    
    Dispatcher -->|"job definition"| Action
    Action --> Configure
    Configure --> AWS
    AWS --> Checkout
    Checkout --> Pull
    Pull --> PathPrep
    PathPrep -->|"HOST_REPO, MOUNT_REPO outputs"| DockerRun
    DockerRun -->|"docker run with mount"| PSEnv
    PSEnv --> GitConfig
    GitConfig --> Command
    Command -->|"artifacts generated"| Artifacts
    Artifacts --> Upload
    Upload -->|"jobs-{id} artifact"| Dispatcher
```

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:1-99]()

## Action Inputs and Outputs

The `workflow-run-job-windows` action accepts three required inputs:

| Input | Description | Example |
|-------|-------------|---------|
| `id` | Unique job identifier used for artifact naming | `libcudacxx-build-gcc11-cuda11.1` |
| `command` | Command to execute inside the container | `ci/windows_build.ps1` |
| `image` | Docker image to run | `rapidsai/devcontainers:25.02-cpp-gcc11-cuda11.8` |

The action produces one output from the "Prepare job artifacts" step:

| Output | Description | Value |
|--------|-------------|-------|
| `SUCCESS` | Indicates job completion (artifact upload success) | `true` |

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:4-13](), [.github/actions/workflow-run-job-windows/action.yml:66-69]()

## Path Transformation System

Windows uses backslash-separated paths (e.g., `D:\a\repository\cccl`) while Docker expects Unix-style forward-slash paths. The action performs path transformation in the "Prepare paths for docker" step using PowerShell.

### Path Transformation Logic

```mermaid
graph LR
    subgraph Input["GitHub Context Input"]
        GW["github.workspace<br/>(Windows backslash path)"]
        Repo["github.event.repository.name"]
    end
    
    subgraph PowerShell["PowerShell Transformation<br/>lines 40-46"]
        Concat["Concatenate:<br/>workspace \ repo_name"]
        Replace["Replace backslashes<br/>with forward slashes"]
        MountPath["Generate mount target:<br/>C:/{repo_name}"]
    end
    
    subgraph Output["Step Outputs"]
        HostRepo["HOST_REPO<br/>(Unix-style, host location)"]
        MountRepo["MOUNT_REPO<br/>(Container path)"]
    end
    
    GW --> Concat
    Repo --> Concat
    Concat --> Replace
    Replace --> HostRepo
    Repo --> MountPath
    MountPath --> MountRepo
    
    HostRepo -.->|"used in --mount source"| DockerRun["docker run command"]
    MountRepo -.->|"used in --mount target<br/>and --workdir"| DockerRun
```

**Path Transformation Implementation:**

The PowerShell script at lines 40-46 performs the following operations:

1. **HOST_REPO**: Constructs the full host path by joining `github.workspace` and repository name, then replaces all backslashes with forward slashes using `.Replace('\', '/')`. This produces a Unix-style path that Docker on Windows can understand, such as `D:/a/cccl-gha/cccl-gha/cccl`.

2. **MOUNT_REPO**: Creates a simple container-internal path as `C:/{repository_name}`, such as `C:/cccl`. This becomes both the mount target and working directory inside the container.

The outputs are written to `$env:GITHUB_OUTPUT` and consumed by the subsequent "Run command" step.

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:40-46]()

## Container Execution

The "Run command" step (lines 47-64) launches a Windows Docker container with the repository mounted and command executed. This step uses bash shell to invoke Docker, but the container itself runs PowerShell.

### Docker Run Command Structure

```mermaid
graph TB
    subgraph DockerCommand["docker run command<br/>lines 50-64"]
        Mount["--mount type=bind<br/>source=HOST_REPO<br/>target=MOUNT_REPO"]
        Workdir["--workdir MOUNT_REPO"]
        Image["Image: inputs.image"]
        Shell["powershell -c '...'"]
    end
    
    subgraph PowerShellBlock["PowerShell Commands<br/>lines 54-64"]
        SetEnv1["SetEnvironmentVariable<br/>AWS_ACCESS_KEY_ID"]
        SetEnv2["SetEnvironmentVariable<br/>AWS_SECRET_ACCESS_KEY"]
        SetEnv3["SetEnvironmentVariable<br/>AWS_SESSION_TOKEN"]
        SetEnvSccache["SetEnvironmentVariable<br/>SCCACHE_* variables"]
        GitSafe["git config --global --add<br/>safe.directory"]
        ExecCmd["Execute inputs.command"]
    end
    
    Mount --> Container["Windows Docker Container"]
    Workdir --> Container
    Image --> Container
    Shell --> SetEnv1
    SetEnv1 --> SetEnv2
    SetEnv2 --> SetEnv3
    SetEnv3 --> SetEnvSccache
    SetEnvSccache --> GitSafe
    GitSafe --> ExecCmd
    
    ExecCmd -.->|"generates"| Outputs["sccache_stats.json<br/>success marker"]
```

The Docker command uses:
- **Bind mount**: Connects the Windows host repository path to the container filesystem
- **Working directory**: Sets the container's current directory to the mounted repository
- **PowerShell execution**: All environment setup and command execution happens in PowerShell

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:47-64]()

## Environment Variable Propagation

Environment variables cannot be passed directly to Windows Docker containers via `-e` flags in the same way as Linux. Instead, the action uses PowerShell's `[System.Environment]::SetEnvironmentVariable` method inside the container to configure the execution environment.

### Environment Setup Process

| Variable Category | Variables | Purpose | Lines |
|-------------------|-----------|---------|-------|
| AWS Credentials | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` | Enable sccache S3 access | 55-57 |
| sccache Configuration | `SCCACHE_BUCKET`, `SCCACHE_REGION`, `SCCACHE_IDLE_TIMEOUT`, `SCCACHE_S3_USE_SSL`, `SCCACHE_S3_NO_CREDENTIALS` | Configure distributed compilation caching | 58-62 |

The environment variables are initially set in the GitHub Actions runner environment through two mechanisms:

1. **Static Configuration** (lines 18-25): The "Configure env" step appends sccache configuration to `$GITHUB_ENV`:
   - `SCCACHE_BUCKET=rapids-sccache-devs`
   - `SCCACHE_REGION=us-east-2`
   - `SCCACHE_IDLE_TIMEOUT=0`
   - `SCCACHE_S3_USE_SSL=true`
   - `SCCACHE_S3_NO_CREDENTIALS=false`

2. **Dynamic AWS Credentials** (lines 26-31): The `aws-actions/configure-aws-credentials@v4` action assumes an IAM role and sets `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` in the runner environment.

These runner-level environment variables are then explicitly propagated into the Docker container using PowerShell (lines 54-62), where each variable is accessed via `${{env.VARIABLE_NAME}}` and set inside the container using `SetEnvironmentVariable`.

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:18-31](), [.github/actions/workflow-run-job-windows/action.yml:54-62]()

## Git Configuration

The action configures Git's `safe.directory` setting to allow operations in the mounted repository. This is necessary because the repository is owned by a different user in the container context.

The command executed at line 63:
```
git config --global --add safe.directory '${{steps.paths.outputs.MOUNT_REPO}}'
```

This adds the container's mount path (e.g., `C:/cccl`) to Git's safe directory list, preventing "dubious ownership" errors when the `inputs.command` attempts to perform Git operations.

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:63]()

## Artifact Collection and Upload

After command execution completes, the "Prepare job artifacts" step (lines 65-91) collects job outputs and prepares them for upload. This step runs on the Windows runner (not in the container) and uses bash shell.

### Artifact Collection Flow

```mermaid
graph TB
    CommandComplete["inputs.command completes"]
    
    subgraph ArtifactPrep["Prepare job artifacts step<br/>lines 65-91"]
        SetSuccess["Set SUCCESS=true<br/>line 69"]
        CreateDir["Create jobs/{id} directory<br/>lines 71-72"]
        TouchSuccess["Create success marker file<br/>line 74"]
        DefineFunc["Define find_and_copy function<br/>lines 76-85"]
        CopySccache["find_and_copy sccache_stats.json<br/>line 87"]
        ListArtifacts["List job artifacts<br/>lines 89-91"]
    end
    
    subgraph UploadStep["Upload job artifacts step<br/>lines 93-98"]
        UploadAction["actions/upload-artifact@v4"]
        ArtifactName["name: jobs-{id}"]
        ArtifactPath["path: jobs"]
        Compression["compression-level: 0"]
    end
    
    CommandComplete --> SetSuccess
    SetSuccess --> CreateDir
    CreateDir --> TouchSuccess
    TouchSuccess --> DefineFunc
    DefineFunc --> CopySccache
    CopySccache --> ListArtifacts
    ListArtifacts --> UploadAction
    UploadAction --> ArtifactName
    ArtifactName --> ArtifactPath
    ArtifactPath --> Compression
```

### Artifact Files

The action collects the following artifacts:

| File | Location | Purpose | Required |
|------|----------|---------|----------|
| `success` | `jobs/{id}/success` | Marker file indicating job completion | Yes |
| `sccache_stats.json` | Found via `find` in repository | sccache statistics for cache hit rate analysis | No |

The `find_and_copy` function (lines 76-85) searches the repository checkout for matching files and copies them to the results directory. The function:
1. Uses `find` to locate the file by name anywhere in `${{github.event.repository.name}}` directory
2. Takes the first match (`-print -quit`)
3. Copies it to `jobs/{id}/` directory
4. Returns error code 1 if not found (suppressed with `|| true` for optional files)

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:65-98]()

## Artifact Upload Configuration

The `actions/upload-artifact@v4` action uploads collected artifacts with specific configuration:

- **Artifact Name**: `jobs-{id}` where `{id}` is the unique job identifier input. This naming convention allows the results collection system to download artifacts by job ID.
- **Artifact Path**: `jobs` directory containing the nested `{id}` subdirectory structure.
- **Compression Level**: `0` (no compression) to optimize upload speed, as the artifacts are typically small JSON files.

The uploaded artifacts are consumed by the `workflow-results` action [see page 6.1](#6.1) which downloads all `jobs-*` artifacts and aggregates their contents for summary generation.

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:93-98]()

## Comparison with Linux Execution

| Aspect | Windows | Linux |
|--------|---------|-------|
| **Container Launch** | Direct `docker run` from runner | Docker-outside-of-Docker via intermediate `ubuntu-dind` container |
| **Path Handling** | PowerShell transformation (backslash to forward-slash) | Symlink system for path consistency |
| **Environment Variables** | PowerShell `SetEnvironmentVariable` inside container | Passed via `-e` flags in `docker run` |
| **Shell Context** | PowerShell for setup and command execution | Bash for orchestration, devcontainer-specific shell for execution |
| **Script Wrapper** | Direct command execution | `ci.sh` wrapper script generated and mounted |
| **GPU Access** | Not documented in this action | `--gpus` flag and `NVIDIA_VISIBLE_DEVICES` |
| **Complexity** | Simpler single-layer architecture | Complex multi-layer with intermediate container |

The Windows execution model trades some features (like the reproduction script wrapper) for architectural simplicity, reflecting the differences in Docker implementation between Windows and Linux hosts.

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:1-99]()

---

# Page: Devcontainer System

# Devcontainer System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)
- [.github/workflows/verify-devcontainers.yml](.github/workflows/verify-devcontainers.yml)

</details>



## Purpose and Scope

The devcontainer system provides isolated, reproducible build environments for CCCL jobs across different CUDA versions, compilers, and operating systems. This page documents the devcontainer configuration directory structure, the container selection and launching mechanism (`launch.sh`), the generation process (`make_devcontainers.sh`), and the verification workflow that ensures configurations remain synchronized with their generation source.

For information about how devcontainers are invoked during Linux job execution, see [Linux Execution Environment](#5.1). For Windows execution environments which do not use devcontainers, see [Windows Execution Environment](#5.2). For AWS credential and sccache configuration within devcontainers, see [Environment Setup](#5.4).

---

## Devcontainer Directory Structure

The `.devcontainer/` directory contains pre-configured development container definitions organized by CUDA version and compiler. Each configuration consists of a `devcontainer.json` file that specifies the Docker image, environment variables, and container settings.

### Directory Organization

```
.devcontainer/
├── make_devcontainers.sh          # Generation script
├── launch.sh                      # Container selection and launch script
├── verify_devcontainer.sh         # Validation script for CI
├── cuda<VERSION>-<COMPILER>/      # Configuration directories
│   └── devcontainer.json          # DevContainer specification
└── ...
```

The directory structure follows a naming convention where each subdirectory is named `cuda<VERSION>-<COMPILER>` (e.g., `cuda11.1-gcc6`, `cuda12.0-llvm16`). Each subdirectory contains a `devcontainer.json` file that defines the container image, environment variables, mounts, and other configuration for that specific CUDA/compiler combination.

### DevContainer JSON Structure

Each `devcontainer.json` file typically specifies:

| Field | Purpose |
|-------|---------|
| `name` | Human-readable identifier (e.g., "CUDA 11.1 GCC 6") |
| `image` | Docker image reference (e.g., `rapidsai/devcontainers:...`) |
| `hostRequirements` | GPU requirements (`{"gpu": true}` for CUDA jobs) |
| `capAdd` | Linux capabilities (e.g., `["SYS_PTRACE"]` for debugging) |
| `securityOpt` | Security options (e.g., `["seccomp=unconfined"]`) |
| `remoteEnv` | Environment variables to set in the container |
| `workspaceFolder` | Working directory inside the container |
| `mounts` | Volume mounts for host filesystem access |

**Sources:** [.github/workflows/verify-devcontainers.yml:91-93]()

---

## Container Selection and Launching: launch.sh

The `launch.sh` script is the primary interface for selecting and launching devcontainers. It maps CUDA version and compiler arguments to the appropriate devcontainer configuration directory and invokes Docker with the correct parameters.

### Launch Script Invocation

```mermaid
graph TB
    subgraph "Caller Context"
        JobAction[".github/actions/workflow-run-job-linux"]
        CommandVar["COMMAND variable"]
        CudaInput["inputs.cuda"]
        HostInput["inputs.host"]
    end
    
    subgraph "launch.sh Script"
        LaunchScript[".devcontainer/launch.sh"]
        ParseArgs["Parse --cuda, --host, --docker flags"]
        SelectContainer["Select devcontainer directory<br/>based on CUDA/compiler"]
        LoadConfig["Load devcontainer.json"]
        BuildDockerArgs["Build docker run arguments:<br/>--volume, --env, --gpus"]
        ExecuteDocker["Execute docker run"]
    end
    
    subgraph "Docker Daemon"
        HostDaemon["Host Docker Daemon<br/>/var/run/docker.sock"]
        PullImage["Pull container image if needed"]
        CreateContainer["Create container with mounts"]
        RunCommand["Execute mounted /ci.sh script"]
    end
    
    JobAction --> CommandVar
    JobAction --> CudaInput
    JobAction --> HostInput
    CommandVar --> LaunchScript
    CudaInput --> LaunchScript
    HostInput --> LaunchScript
    
    LaunchScript --> ParseArgs
    ParseArgs --> SelectContainer
    SelectContainer --> LoadConfig
    LoadConfig --> BuildDockerArgs
    BuildDockerArgs --> ExecuteDocker
    
    ExecuteDocker --> HostDaemon
    HostDaemon --> PullImage
    PullImage --> CreateContainer
    CreateContainer --> RunCommand
```

**Diagram: launch.sh Container Selection and Execution Flow**

### Launch Script Parameters

The `launch.sh` script is invoked with the following flags (as seen in [.github/actions/workflow-run-job-linux/action.yml:144-164]()):

| Flag | Description | Example |
|------|-------------|---------|
| `--docker` | Use Docker execution mode (vs VSCode) | N/A |
| `--cuda <VERSION>` | CUDA version for container selection | `12.0`, `11.1` |
| `--host <COMPILER>` | Host compiler for container selection | `gcc10`, `llvm16` |
| `--gpus <SPEC>` | GPU device specification | `device=${NVIDIA_VISIBLE_DEVICES}` |
| `--env <VAR>` | Environment variables to pass through | `CI=true` |
| `--volume <MOUNT>` | Additional volume mounts | `/path/on/host:/path/in/container` |
| `-- <COMMAND>` | Command to execute in container | `/ci.sh` |

### GPU Request Handling

The script conditionally adds GPU access based on the runner type (lines 132-136 in action.yml):

```bash
declare -a gpu_request=()

# Explicitly pass which GPU to use if on a GPU runner
if [[ "${RUNNER}" = *"-gpu-"* ]]; then
  gpu_request+=(--gpus "device=${NVIDIA_VISIBLE_DEVICES}")
fi
```

The `--gpus` flag is then passed to `launch.sh` which includes it in the Docker command, enabling CUDA workloads to access GPU hardware.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:132-149]()

---

## Environment Variable Propagation

The `launch.sh` script receives numerous environment variables through `--env` flags that must be propagated into the devcontainer for proper GitHub Actions integration:

| Environment Variable | Purpose |
|---------------------|---------|
| `CI` | Indicates CI environment (triggers specific behaviors) |
| `COMMAND` | The actual command to execute (avoids shell escaping issues) |
| `GITHUB_WORKSPACE` | Workspace path for GitHub Actions context |
| `GITHUB_SHA` | Current commit SHA for reproduction instructions |
| `GITHUB_REF_NAME` | Branch or tag name |
| `GITHUB_REPOSITORY` | Repository slug (owner/repo) |
| `GITHUB_ENV` | Path to environment file for setting outputs |
| `GITHUB_PATH` | Path to path file for modifying PATH |
| `GITHUB_OUTPUT` | Path to output file for setting step outputs |
| `GITHUB_STEP_SUMMARY` | Path to step summary file for UI output |
| `GITHUB_ACTIONS` | Boolean indicating GitHub Actions environment |

These variables enable the devcontainer to interact with GitHub Actions' workflow commands and provide proper context for error reporting and reproduction instructions (see [.github/actions/workflow-run-job-linux/action.yml:149-160]()).

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:149-160]()

---

## Volume Mounts and Path Management

The `launch.sh` script configures three critical volume mounts to provide the devcontainer with access to necessary resources:

### Mount Configuration

```mermaid
graph LR
    subgraph "Host Filesystem"
        HostRepo["/<work_dir>/<repo>"]
        HostCiScript["/ci.sh (generated)"]
        HostAWS["/.aws directory"]
        HostWorkspace["/__w directory"]
    end
    
    subgraph "Devcontainer"
        ContainerRepo["/workspace (workspaceFolder)"]
        ContainerCi["/ci.sh (executable)"]
        ContainerAWS["/root/.aws"]
        ContainerW["/__w (volume root)"]
    end
    
    HostRepo -->|"--volume"| ContainerRepo
    HostCiScript -->|"--volume"| ContainerCi
    HostAWS -->|"--volume"| ContainerAWS
    HostWorkspace -->|"--volume"| ContainerW
```

**Diagram: Devcontainer Volume Mount Configuration**

The three volume mounts are configured as (from [.github/actions/workflow-run-job-linux/action.yml:161-163]()):

1. **CI Script Mount:** `--volume "${{github.workspace}}/ci.sh:/ci.sh"`
   - Mounts the generated wrapper script containing the command to execute
   - The script includes error handling and reproduction instructions

2. **AWS Credentials Mount:** `--volume "$(host_path "$RUNNER_TEMP")/.aws:/root/.aws"`
   - Provides sccache with S3 bucket credentials
   - The `host_path` function transforms container paths to host paths for DOOD

3. **Workspace Mount:** `--volume "$(dirname "$(dirname "${{github.workspace}}")"):/__w"`
   - Mounts the entire GitHub Actions workspace directory
   - Maintains path consistency between intermediate container and devcontainer

### Path Transformation: host_path Function

Because of the Docker-outside-of-Docker (DOOD) strategy, volume mounts must reference host paths, not intermediate container paths. The `host_path` function performs this transformation (lines 138-140):

```bash
host_path() {
  sed "s@/__w@$(dirname "$(dirname "${{github.workspace}}")")@" <<< "$1"
}
```

This function replaces the `/__w` prefix (the container's view) with the actual host path to the GitHub Actions workspace root, ensuring Docker can locate the files when creating mounts.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:138-164]()

---

## Container Generation: make_devcontainers.sh

The `make_devcontainers.sh` script generates all devcontainer configurations programmatically from a source definition. This ensures consistency across configurations and allows centralized management of common settings.

### Generation Process

```mermaid
graph TB
    subgraph "Input Sources"
        SourceDef["Source definition<br/>(script internals)"]
        MatrixYAML["ci/matrix.yaml<br/>(reference)"]
        BuildWorkflow["build-workflow.py<br/>(reference)"]
    end
    
    subgraph "make_devcontainers.sh Processing"
        ParseArgs["Parse --verbose, --clean flags"]
        CleanOld["Remove existing configs<br/>(if --clean)"]
        IterateCombos["Iterate CUDA/compiler combinations"]
        GenerateJSON["Generate devcontainer.json<br/>for each combination"]
        WriteFiles["Write to .devcontainer/cuda*-*/"]
    end
    
    subgraph "Generated Outputs"
        DevcontainerDirs[".devcontainer/cuda11.1-gcc6/<br/>.devcontainer/cuda12.0-llvm16/<br/>..."]
        DevcontainerJSON["devcontainer.json files"]
    end
    
    SourceDef --> IterateCombos
    MatrixYAML -.->|"Informs combinations"| IterateCombos
    BuildWorkflow -.->|"Canonicalization reference"| IterateCombos
    
    ParseArgs --> CleanOld
    CleanOld --> IterateCombos
    IterateCombos --> GenerateJSON
    GenerateJSON --> WriteFiles
    WriteFiles --> DevcontainerDirs
    DevcontainerDirs --> DevcontainerJSON
```

**Diagram: make_devcontainers.sh Generation Pipeline**

### Script Invocation

The script is invoked during the verification workflow with specific flags (from [.github/workflows/verify-devcontainers.yml:39]()):

```bash
./.devcontainer/make_devcontainers.sh --verbose --clean
```

| Flag | Purpose |
|------|---------|
| `--verbose` | Enable detailed logging during generation |
| `--clean` | Remove all existing devcontainer directories before generation |

The `--clean` flag ensures a complete regeneration, preventing stale configurations from persisting if combinations are removed from the generation logic.

### Post-Generation Validation

After running the generation script, the verification workflow checks for modifications to ensure the checked-in files match the generated output (lines 40-49):

```bash
if [[ $(git diff --stat) != '' || $(git status --porcelain | grep '^??') != '' ]]; then
  git diff --minimal
  git status --porcelain
  echo "::error:: Dev Container files are out of date or there are untracked files..."
  exit 1
fi
```

This enforcement ensures that any changes to the generation logic are accompanied by updates to the generated files, maintaining synchronization between source and output.

**Sources:** [.github/workflows/verify-devcontainers.yml:37-49]()

---

## Verification Workflow

The `verify-devcontainers.yml` workflow validates that devcontainer configurations are up-to-date and functional. It runs in two phases: file synchronization checking and functional container testing.

### Verification Workflow Architecture

```mermaid
graph TB
    subgraph "Trigger"
        WorkflowCall["workflow_call<br/>(from parent workflows)"]
        BaseSHA["inputs.base_sha<br/>(for PR context)"]
    end
    
    subgraph "Job: get-devcontainer-list"
        Checkout1["actions/checkout@v4"]
        SetupTools["Install jq, yq"]
        RunGenerate[".devcontainer/make_devcontainers.sh<br/>--verbose --clean"]
        CheckChanges["git diff, git status<br/>Fail if files out-of-date"]
        InspectChanges["Git diff analysis<br/>Check relevant files changed"]
        GetList["Find all devcontainer.json files"]
        OutputMatrix["Output devcontainers array + skip flag"]
    end
    
    subgraph "Job: verify-devcontainers (matrix)"
        Checkout2["actions/checkout@v4"]
        GetAWS["configure-aws-credentials@v4<br/>for sccache"]
        SetEnv["Set SCCACHE_* environment variables"]
        RunDevcontainer["devcontainers/ci@v0.3<br/>configFile: matrix.devcontainer.path"]
        VerifyScript[".devcontainer/verify_devcontainer.sh"]
    end
    
    subgraph "Conditional Execution"
        SkipCheck{"outputs.skip == 'true'?"}
        MatrixExpand["Matrix expands<br/>fromJson(outputs.devcontainers)"]
    end
    
    WorkflowCall --> BaseSHA
    BaseSHA --> Checkout1
    
    Checkout1 --> SetupTools
    SetupTools --> RunGenerate
    RunGenerate --> CheckChanges
    CheckChanges --> InspectChanges
    InspectChanges --> GetList
    GetList --> OutputMatrix
    
    OutputMatrix --> SkipCheck
    SkipCheck -->|"false"| MatrixExpand
    SkipCheck -->|"true"| Skip["Skip verification"]
    
    MatrixExpand --> Checkout2
    Checkout2 --> GetAWS
    GetAWS --> SetEnv
    SetEnv --> RunDevcontainer
    RunDevcontainer --> VerifyScript
```

**Diagram: verify-devcontainers Workflow Execution Flow**

### Phase 1: File Synchronization Check

The `get-devcontainer-list` job ensures devcontainer files are synchronized with their generation script:

#### Steps

1. **Setup Tools** (lines 31-36): Install `jq` for JSON processing and `yq` for YAML processing
2. **Generate Files** (line 39): Run `make_devcontainers.sh --verbose --clean` to regenerate all configurations
3. **Detect Changes** (lines 41-49): Use `git diff` and `git status` to detect modifications or untracked files
4. **Fail on Desync**: If changes are detected, fail with an error message instructing developers to run the generation script and commit changes

This check enforces that all devcontainer configurations in the repository are generated files, not manually edited, ensuring consistency and reproducibility.

**Sources:** [.github/workflows/verify-devcontainers.yml:20-49]()

### Phase 2: Change Detection (PR Context)

When the workflow is called with a `base_sha` input (indicating a pull request context), the verification workflow performs change detection to conditionally skip testing if irrelevant files changed:

#### Relevant File Patterns

The workflow checks for modifications to files matching the regex (from line 72):

```regex
^(.devcontainer|ci/matrix.yaml|.github/actions/workflow-build/build-workflow.py)
```

| Pattern | Rationale |
|---------|-----------|
| `.devcontainer` | Direct changes to devcontainer configurations |
| `ci/matrix.yaml` | Matrix changes may affect devcontainer requirements |
| `.github/actions/workflow-build/build-workflow.py` | Workflow generation logic may change container selection |

If no files matching these patterns have changed between the PR base and current HEAD, the workflow sets `skip=true` and bypasses container testing (lines 80-86).

**Sources:** [.github/workflows/verify-devcontainers.yml:50-86]()

### Phase 3: Container List Generation

The workflow discovers all devcontainer configurations by finding `devcontainer.json` files (lines 91-94):

```bash
devcontainers=$(find .devcontainer/ -name 'devcontainer.json' | while read -r devcontainer; do
  jq --arg path "$devcontainer" '{path: $path, name: .name}' "$devcontainer"
done | jq -s -c .)
```

This bash pipeline:
1. Finds all `devcontainer.json` files recursively
2. Extracts the `path` and `name` fields from each file using `jq`
3. Combines all entries into a JSON array with `jq -s -c`
4. Outputs the array as a matrix configuration for the next job

The output format is an array of objects: `[{path: "...", name: "..."}, ...]`

**Sources:** [.github/workflows/verify-devcontainers.yml:87-94]()

### Phase 4: Functional Container Testing

The `verify-devcontainers` job tests each devcontainer configuration using a GitHub Actions matrix strategy:

```yaml
strategy:
  fail-fast: false
  matrix:
    devcontainer: ${{fromJson(needs.get-devcontainer-list.outputs.devcontainers)}}
```

Each matrix entry represents one devcontainer configuration, allowing parallel testing with `fail-fast: false` to ensure all containers are tested even if some fail.

#### Testing Steps

1. **Checkout Repository** (lines 109-112)
2. **Configure AWS Credentials** (lines 116-121): Required for sccache, even though it's not actively used during verification
3. **Set Environment Variables** (lines 122-129): Configure sccache environment variables
4. **Run Devcontainer** (lines 130-141): Use `devcontainers/ci@v0.3` action with the configuration path from the matrix
5. **Execute Verification Script** (line 141): Run `.devcontainer/verify_devcontainer.sh` inside the container to validate functionality

The `devcontainers/ci` action handles pulling the Docker image, creating the container according to the `devcontainer.json` specification, and executing the `runCmd` within that environment.

#### Environment Variable Configuration

The workflow passes AWS credentials to the devcontainer through the `env:` field (lines 135-139):

```yaml
env: |
  SCCACHE_REGION=${{ env.SCCACHE_REGION }}
  AWS_ACCESS_KEY_ID=${{ env.AWS_ACCESS_KEY_ID }}
  AWS_SESSION_TOKEN=${{ env.AWS_SESSION_TOKEN }}
  AWS_SECRET_ACCESS_KEY=${{ env.AWS_SECRET_ACCESS_KEY }}
```

This ensures the container has access to sccache credentials, preventing the container from hanging while waiting for GitHub authentication (as noted in the comment on lines 114-115).

**Sources:** [.github/workflows/verify-devcontainers.yml:96-142]()

---

## Integration with Job Execution

Devcontainers are the primary execution environment for all Linux jobs in the CCCL CI/CD system. The integration follows the Docker-outside-of-Docker (DOOD) pattern described in [Linux Execution Environment](#5.1).

### Execution Flow Integration

```mermaid
sequenceDiagram
    participant Runner as GitHub Actions Runner
    participant Dind as cruizba/ubuntu-dind Container
    participant Launch as .devcontainer/launch.sh
    participant Daemon as Host Docker Daemon
    participant DevCon as Job-Specific Devcontainer
    
    Runner->>Dind: Start intermediate container<br/>(mount docker socket)
    Dind->>Dind: Checkout repository
    Dind->>Dind: Generate ci.sh wrapper script
    Dind->>Dind: Configure AWS credentials
    Dind->>Dind: Create symlink for path consistency
    Dind->>Launch: Execute with --cuda, --host, volumes
    Launch->>Launch: Parse arguments
    Launch->>Launch: Select devcontainer directory
    Launch->>Launch: Load devcontainer.json
    Launch->>Daemon: docker run with mounts and env vars
    Daemon->>DevCon: Create container on host
    DevCon->>DevCon: Execute /ci.sh
    DevCon-->>Daemon: Exit with status code
    Daemon-->>Launch: Return exit code
    Launch-->>Dind: Return exit code
    Dind->>Dind: Upload artifacts (success marker, etc.)
```

**Diagram: Devcontainer Integration with Linux Job Execution**

### Key Integration Points

| Component | Integration Detail |
|-----------|-------------------|
| **Container Selection** | `launch.sh` maps `inputs.cuda` and `inputs.host` from job definition to devcontainer directory |
| **Command Execution** | Generated `ci.sh` script is mounted as `/ci.sh` and executed as the container's command |
| **Path Consistency** | Symlink creation in intermediate container ensures `github.workspace` paths match host paths |
| **Credential Access** | AWS credentials for sccache are mounted from `$RUNNER_TEMP/.aws` to `/root/.aws` |
| **GPU Access** | `--gpus` flag passed to `launch.sh` enables CUDA workloads on GPU runners |
| **Artifact Collection** | Container has access to workspace for writing build outputs and test results |

The devcontainer system provides isolation, reproducibility, and flexibility while maintaining the performance benefits of DOOD (avoiding nested virtualization overhead). Each job runs in a clean container environment with only the necessary dependencies for its specific CUDA/compiler combination.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:66-164](), [.github/workflows/verify-devcontainers.yml:1-142]()

---

## Summary

The devcontainer system is a critical component of CCCL's CI/CD infrastructure, providing:

- **Isolation:** Each job runs in its own container with specific CUDA and compiler versions
- **Reproducibility:** Standardized configurations ensure consistent build environments across CI and local development
- **Maintainability:** Generated configurations from `make_devcontainers.sh` ensure consistency and simplify updates
- **Verification:** Automated testing via `verify-devcontainers.yml` ensures containers remain functional
- **Integration:** Seamless integration with GitHub Actions through the DOOD pattern and `launch.sh` script

The system supports local development through the same `launch.sh` interface used in CI, enabling developers to reproduce CI failures by running the exact same container configuration locally (see [Error Handling and Reproducibility](#5.5) for details on local reproduction workflows).

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:1-201](), [.github/workflows/verify-devcontainers.yml:1-142]()

---

# Page: Environment Setup

# Environment Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)
- [.github/actions/workflow-run-job-windows/action.yml](.github/actions/workflow-run-job-windows/action.yml)

</details>



## Purpose and Scope

This document describes the environment configuration process that occurs before job commands execute in their respective containers. This includes AWS credential acquisition for distributed compilation caching, sccache configuration, environment variable propagation to containers, and problem matcher installation for error detection. 

For information about the actual command execution and error handling, see [Error Handling and Reproducibility](#5.5). For details on devcontainer selection and launching, see [Devcontainer System](#5.3).

---

## AWS Credential Configuration

Both Linux and Windows execution environments acquire AWS credentials using OpenID Connect (OIDC) authentication to access the sccache S3 bucket for distributed compilation caching.

### OIDC Role Assumption

The system uses the `aws-actions/configure-aws-credentials@v4` action to assume an AWS IAM role without requiring long-lived credentials:

**Linux:**
[.github/actions/workflow-run-job-linux/action.yml:60-65]()

**Windows:**
[.github/actions/workflow-run-job-windows/action.yml:26-31]()

| Parameter | Value | Description |
|-----------|-------|-------------|
| `role-to-assume` | `arn:aws:iam::279114543810:role/gha-oidc-NVIDIA` | IAM role with S3 bucket access |
| `aws-region` | `us-east-2` | AWS region containing the sccache bucket |
| `role-duration-seconds` | `43200` | 12-hour session duration to cover long-running jobs |

The action populates three environment variables that are subsequently propagated to execution containers:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`

### Credential File Generation (Linux Only)

On Linux, the intermediate `ubuntu-dind` container generates AWS credential and configuration files that are mounted into the devcontainer:

[.github/actions/workflow-run-job-linux/action.yml:113-129]()

The files are created in `$RUNNER_TEMP/.aws/` with appropriate permissions (`0600` for credentials, `0664` for config) and mounted into the devcontainer at `/root/.aws/` to enable sccache to authenticate with S3.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:60-129](), [.github/actions/workflow-run-job-windows/action.yml:26-31]()

---

## Sccache Configuration

Sccache requires several environment variables to connect to the S3 bucket and manage compilation artifacts.

### Configuration Environment Variables

**Linux:**
Sccache configuration on Linux is provided through the AWS credential files (see above). The devcontainer reads these files automatically.

**Windows:**
Windows explicitly sets sccache environment variables before AWS credential acquisition:

[.github/actions/workflow-run-job-windows/action.yml:18-25]()

| Variable | Value | Purpose |
|----------|-------|---------|
| `SCCACHE_BUCKET` | `rapids-sccache-devs` | S3 bucket name for caching artifacts |
| `SCCACHE_REGION` | `us-east-2` | AWS region of the bucket |
| `SCCACHE_IDLE_TIMEOUT` | `0` | Prevents sccache from shutting down during long builds |
| `SCCACHE_S3_USE_SSL` | `true` | Enforces SSL for S3 connections |
| `SCCACHE_S3_NO_CREDENTIALS` | `false` | Indicates credentials are required |

These variables are then explicitly set inside the Docker container using PowerShell:

[.github/actions/workflow-run-job-windows/action.yml:54-62]()

### Credential Propagation Differences

```mermaid
graph TB
    subgraph Linux["Linux Environment"]
        LinuxAWS["aws-actions/configure-aws-credentials@v4"]
        LinuxEnv["Environment Variables:<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>AWS_SESSION_TOKEN"]
        LinuxFiles["Credential Files:<br/>$RUNNER_TEMP/.aws/config<br/>$RUNNER_TEMP/.aws/credentials"]
        LinuxMount["Volume Mount:<br/>--volume $RUNNER_TEMP/.aws:/root/.aws"]
        LinuxContainer["DevContainer:<br/>sccache reads from /root/.aws/"]
        
        LinuxAWS --> LinuxEnv
        LinuxEnv --> LinuxFiles
        LinuxFiles --> LinuxMount
        LinuxMount --> LinuxContainer
    end
    
    subgraph Windows["Windows Environment"]
        WinSccache["Set SCCACHE_* env vars"]
        WinAWS["aws-actions/configure-aws-credentials@v4"]
        WinEnv["Environment Variables:<br/>SCCACHE_BUCKET<br/>SCCACHE_REGION<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>AWS_SESSION_TOKEN"]
        WinPS["PowerShell SetEnvironmentVariable:<br/>Explicit propagation to container"]
        WinContainer["Windows Container:<br/>sccache reads env vars"]
        
        WinSccache --> WinEnv
        WinAWS --> WinEnv
        WinEnv --> WinPS
        WinPS --> WinContainer
    end
```
**Diagram: Sccache Credential Propagation on Linux vs Windows**

Linux uses file-based credential propagation through volume mounts, while Windows uses explicit environment variable injection via PowerShell commands inside the container.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:113-162](), [.github/actions/workflow-run-job-windows/action.yml:18-64]()

---

## Environment Variable Propagation

Jobs require access to GitHub Actions context variables and custom CI variables to function correctly.

### GitHub Actions Context Variables

The Linux workflow explicitly propagates critical GitHub Actions environment variables to the devcontainer:

[.github/actions/workflow-run-job-linux/action.yml:149-160]()

| Variable | Purpose |
|----------|---------|
| `CI` | Indicates running in CI environment |
| `GITHUB_ACTIONS` | Indicates running in GitHub Actions |
| `GITHUB_SHA` | Current commit SHA for reproducibility instructions |
| `GITHUB_REF_NAME` | Branch or tag name |
| `GITHUB_REPOSITORY` | Repository identifier (owner/repo) |
| `GITHUB_WORKSPACE` | Workspace path for file operations |
| `GITHUB_ENV` | File path for setting environment variables |
| `GITHUB_PATH` | File path for modifying PATH |
| `GITHUB_OUTPUT` | File path for setting step outputs |
| `GITHUB_STEP_SUMMARY` | File path for markdown summary |
| `VAULT_HOST` | Cleared to prevent vault access attempts |

### Command Environment Variable

The actual command to execute is passed as an environment variable rather than directly as a GitHub Actions input to avoid escaping issues with special characters:

[.github/actions/workflow-run-job-linux/action.yml:68-73]()

This approach prevents problems with commands containing semicolons, quotes, or other shell metacharacters (e.g., `-arch "60;70;80"`).

### Environment Variable Flow Diagram

```mermaid
graph LR
    subgraph GitHub["GitHub Actions Runner"]
        GHContext["GitHub Context:<br/>GITHUB_SHA<br/>GITHUB_REF_NAME<br/>GITHUB_REPOSITORY"]
        ActionInputs["Action Inputs:<br/>command<br/>runner<br/>cuda<br/>host"]
        AWSCreds["AWS Action Output:<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>AWS_SESSION_TOKEN"]
    end
    
    subgraph Container["ubuntu-dind Container"]
        EnvVars["Environment Variables"]
        LaunchScript[".devcontainer/launch.sh --env flags"]
    end
    
    subgraph DevContainer["DevContainer"]
        ExecEnv["Execution Environment:<br/>All variables available<br/>to executed command"]
    end
    
    GHContext --> EnvVars
    ActionInputs --> EnvVars
    AWSCreds --> EnvVars
    EnvVars --> LaunchScript
    LaunchScript --> ExecEnv
```
**Diagram: Environment Variable Propagation Chain**

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:66-164](), [.github/actions/workflow-run-job-windows/action.yml:54-64]()

---

## Problem Matcher Configuration

Problem matchers enable GitHub Actions to automatically detect and annotate errors in build output.

### NVCC Problem Matcher

The Linux workflow installs an NVCC problem matcher before command execution:

[.github/actions/workflow-run-job-linux/action.yml:56-59]()

This problem matcher is defined in the repository at the path `.github/problem-matchers/problem-matcher.json` and recognizes NVCC compiler error messages, converting them into GitHub Actions annotations that appear inline in pull request diffs and workflow logs.

Problem matchers scan output lines using regular expressions to extract:
- Error severity (warning, error)
- File path and line number
- Error message

These structured errors improve developer experience by highlighting failures directly in the GitHub UI rather than requiring manual log parsing.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:56-59]()

---

## Path Management

Path handling differs significantly between Linux and Windows due to Docker-outside-of-Docker (DOOD) requirements on Linux and native Windows path conventions.

### Linux Path Symlink Strategy

The Linux DOOD architecture requires special path handling because volume mounts executed from the intermediate `ubuntu-dind` container must reference the host's filesystem paths, not the intermediate container's paths.

[.github/actions/workflow-run-job-linux/action.yml:78-87]()

**Path Resolution Strategy:**

1. **Host Path:** The GitHub runner uses `${{github.workspace}}` (e.g., `/home/runner/work/cccl/cccl`)
2. **Container View:** The `ubuntu-dind` container sees a different path (e.g., `/__w/cccl/cccl`)
3. **Symlink Creation:** A symlink is created in the container at the host's `${{github.workspace}}` path pointing to the container's current directory
4. **Volume Mount Translation:** The `host_path()` function translates container paths to host paths by replacing `/__w` with the actual host workspace parent directory

[.github/actions/workflow-run-job-linux/action.yml:138-140]()

This ensures that when `.devcontainer/launch.sh` constructs volume mounts using `$(pwd)`, the resulting paths are valid on the host's Docker daemon.

### Linux Volume Mounts

The devcontainer receives three critical volume mounts:

[.github/actions/workflow-run-job-linux/action.yml:161-163]()

| Mount | Source | Target | Purpose |
|-------|--------|--------|---------|
| `ci.sh` script | `${{github.workspace}}/ci.sh` | `/ci.sh` | Wrapper script with command and error handling |
| AWS credentials | `$RUNNER_TEMP/.aws/` | `/root/.aws` | Sccache S3 authentication |
| Workspace | Host workspace parent | `/__w` | Repository code and build artifacts |

### Windows Path Transformation

Windows uses PowerShell to transform Windows-style paths to Docker-compatible paths:

[.github/actions/workflow-run-job-windows/action.yml:40-46]()

Example transformation:
- **Host Path:** `D:\a\cccl\cccl` → `D:/a/cccl`
- **Container Mount:** `C:/cccl`

The forward-slash conversion is necessary for Docker's mount syntax, while the drive letter mapping ensures the container has a clean working directory structure.

### Path Management Comparison

```mermaid
graph TB
    subgraph Linux["Linux Path Management"]
        L1["Host: /home/runner/work/cccl/cccl"]
        L2["ubuntu-dind Container: /__w/cccl/cccl"]
        L3["Symlink: /home/runner/work/cccl/cccl → /__w/cccl/cccl"]
        L4["host_path function: /__w → /home/runner/work"]
        L5["DevContainer Mount: /__w"]
        
        L1 -.->|"docker socket mount"| L2
        L2 --> L3
        L3 --> L4
        L4 --> L5
    end
    
    subgraph Windows["Windows Path Management"]
        W1["Host: D:\\a\\cccl\\cccl"]
        W2["PowerShell Transform: D:/a/cccl"]
        W3["Container Mount: C:/cccl"]
        
        W1 --> W2
        W2 --> W3
    end
```
**Diagram: Path Management Strategies by Operating System**

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:78-140](), [.github/actions/workflow-run-job-windows/action.yml:40-52]()

---

## Environment Setup Summary

The following table summarizes the environment setup differences between Linux and Windows execution:

| Aspect | Linux | Windows |
|--------|-------|---------|
| **AWS Credentials** | File-based (`/root/.aws/`) | Environment variables |
| **Credential Propagation** | Volume mount | PowerShell `SetEnvironmentVariable` |
| **Sccache Config** | AWS credential files | Explicit `SCCACHE_*` environment variables |
| **Path Handling** | Symlinks + `host_path()` translation | PowerShell string replacement |
| **GitHub Context** | Explicit `--env` flags to devcontainer | Inherited from runner (limited) |
| **Problem Matchers** | Installed via `::add-matcher::` | Not used |
| **Container Strategy** | DOOD with intermediate container | Direct Docker run |
| **Volume Mounts** | Repository + ci.sh + AWS credentials | Repository only |

**Environment Setup Execution Flow:**

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions Runner
    participant AWS as AWS OIDC Action
    participant Setup as Environment Setup
    participant Container as Execution Container
    
    GHA->>AWS: Assume IAM role
    AWS->>GHA: Return credentials
    
    alt Linux
        GHA->>Setup: Write credential files
        Setup->>Setup: Create path symlinks
        Setup->>Setup: Generate ci.sh wrapper
        Setup->>Container: Launch with volume mounts
    else Windows
        GHA->>Setup: Set SCCACHE_* env vars
        Setup->>Container: PowerShell SetEnvironmentVariable
    end
    
    Container->>Container: Execute command with<br/>full environment access
    Container->>GHA: Upload artifacts
```
**Diagram: Environment Setup Sequence**

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:45-165](), [.github/actions/workflow-run-job-windows/action.yml:18-98]()

---

# Page: Error Handling and Reproducibility

# Error Handling and Reproducibility

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)

</details>



## Purpose and Scope

This page documents the error handling mechanisms and reproducibility features built into the job execution system. It focuses on the `ci.sh` wrapper script that executes commands within devcontainers, the error detection logic, and the automatic generation of reproduction instructions when jobs fail.

For information about the execution environment setup, see [Linux Execution Environment](#5.1) and [Windows Execution Environment](#5.2). For environment variable configuration, see [Environment Setup](#5.4). For debugging strategies and troubleshooting common issues, see [Troubleshooting Guide](#8.4).

## The ci.sh Wrapper Script

All commands executed within devcontainers are wrapped in a dynamically generated `ci.sh` script. This wrapper provides error detection, user feedback, and reproduction instructions.

### Script Generation

The `ci.sh` script is generated inline during the "Run command" step of the `workflow-run-job-linux` action:

```bash
cat <<"EOF" > ci.sh
#! /usr/bin/env bash
set -eo pipefail
echo -e "\e[1;34mRunning as '$(whoami)' user in $(pwd):\e[0m"
echo -e "\e[1;34m${COMMAND}\e[0m"
eval "${COMMAND}" || exit_code=$?
if [ ! -z "$exit_code" ]; then
  # ... reproduction instructions ...
  exit $exit_code
fi
EOF
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:89-109]()

### Error Handling Configuration

The script uses strict error handling modes via `set -eo pipefail`:

| Flag | Purpose |
|------|---------|
| `-e` | Exit immediately if any command returns non-zero exit status |
| `-o pipefail` | Pipelines return the exit status of the last command to exit with non-zero status |

This ensures that errors are detected at the earliest point, preventing subsequent commands from executing with corrupted state.

### Error Detection Flow

```mermaid
flowchart TD
    A["ci.sh invoked"] --> B["set -eo pipefail"]
    B --> C["Echo command to stdout"]
    C --> D["eval COMMAND"]
    D --> E{"Command\nsucceeds?"}
    E -->|"exit_code=0"| F["Script exits normally"]
    E -->|"exit_code≠0"| G["Capture exit_code"]
    G --> H["Print reproduction instructions"]
    H --> I["exit with exit_code"]
    
    style G fill:#ffebee
    style H fill:#ffebee
    style I fill:#ffebee
```

**Title:** Error Detection and Handling Flow in ci.sh

The error detection mechanism captures the exit code from the `eval "${COMMAND}"` statement using the `||` operator. If the command fails, `exit_code` is set to the non-zero status, triggering the reproduction instruction block.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:94-108]()

## Reproduction Instructions

When a command fails, the system automatically generates comprehensive reproduction instructions using GitHub Actions' error annotation syntax.

### Instruction Template

The reproduction instructions follow a standardized format:

```mermaid
graph LR
    A["::error:: annotation"] --> B["Step 1: Clone repository"]
    B --> C["Step 2: Run in devcontainer"]
    C --> D["Documentation links"]
    
    B2["git clone + checkout"] -.-> B
    C2["launch.sh command"] -.-> C
    D2["DevContainer docs<br/>CI overview"] -.-> D
```

**Title:** Reproduction Instruction Components

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:96-107]()

### Generated Output

When a failure occurs, the following instructions are printed:

| Instruction Element | Value | Purpose |
|---------------------|-------|---------|
| Repository clone | `git clone --branch $GITHUB_REF_NAME --single-branch https://github.com/$GITHUB_REPOSITORY.git` | Ensures correct branch |
| Commit checkout | `git checkout $GITHUB_SHA` | Ensures exact commit match |
| Devcontainer command | `.devcontainer/launch.sh -d -c {cuda} -H {host} -- {COMMAND}` | Reproduces exact environment |
| DevContainer docs | `https://github.com/NVIDIA/cccl/blob/main/.devcontainer/README.md` | Reference material |
| CI overview | `https://github.com/NVIDIA/cccl/blob/main/ci-overview.md` | System context |

The instructions use GitHub Actions environment variables to populate exact values:

| Variable | Usage |
|----------|-------|
| `$GITHUB_REF_NAME` | Branch name for cloning |
| `$GITHUB_REPOSITORY` | Full repository path (e.g., `NVIDIA/cccl`) |
| `$GITHUB_SHA` | Exact commit SHA for checkout |
| `${{inputs.cuda}}` | CUDA version passed to `launch.sh` |
| `${{inputs.host}}` | Host compiler passed to `launch.sh` |

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:98-106]()

## Local Testing Workflow

Developers can reproduce CI failures locally using the provided `launch.sh` command.

### Reproduction Command Structure

```mermaid
flowchart LR
    A["launch.sh"] --> B["-d<br/>(daemonize)"]
    A --> C["-c CUDA_VERSION"]
    A --> D["-H HOST_COMPILER"]
    A --> E["-- COMMAND"]
    
    B --> F["Runs container<br/>in background"]
    C --> G["Selects devcontainer<br/>image"]
    D --> G
    E --> H["Executes failed<br/>command"]
```

**Title:** launch.sh Command Structure for Local Reproduction

The `-d` flag runs the container in detached mode, allowing interactive debugging. The CUDA version and host compiler arguments must match the CI job's configuration to ensure environment parity.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:102]()

### Environment Consistency

The local execution environment matches the CI environment through several mechanisms:

```mermaid
graph TB
    subgraph "CI Environment"
        A["launch.sh in CI"]
        B["--env CI=true"]
        C["--env GITHUB_*"]
        D["--volume .aws"]
        E["--gpus device"]
    end
    
    subgraph "Local Environment"
        F["launch.sh locally"]
        G["Same devcontainer image"]
        H["Optional: --env overrides"]
    end
    
    subgraph "Shared Configuration"
        I["CUDA version"]
        J["Host compiler"]
        K["Repository state"]
        L["Command string"]
    end
    
    A --> I
    A --> J
    F --> I
    F --> J
    K --> A
    K --> F
    L --> A
    L --> F
    
    G -.-> A
    G -.-> F
```

**Title:** Environment Consistency Between CI and Local Execution

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:144-164]()

## Command Execution Environment

The `ci.sh` script executes within a carefully configured environment to ensure reproducibility.

### Environment Variable Propagation

The following environment variables are explicitly passed to the devcontainer:

| Variable | Purpose | Required for Reproducibility |
|----------|---------|------------------------------|
| `CI` | Indicates CI execution context | Optional |
| `COMMAND` | The actual command to execute | **Required** |
| `GITHUB_SHA` | Commit identifier | **Required** |
| `GITHUB_REF_NAME` | Branch name | **Required** |
| `GITHUB_REPOSITORY` | Repository path | **Required** |
| `GITHUB_WORKSPACE` | Working directory path | **Required** |
| `AWS_ACCESS_KEY_ID` | sccache credentials | Optional |
| `AWS_SESSION_TOKEN` | sccache credentials | Optional |
| `AWS_SECRET_ACCESS_KEY` | sccache credentials | Optional |

The variables marked as **Required** are essential for the reproduction instructions to work correctly. The AWS credentials enable sccache functionality but are not necessary for basic reproduction.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:149-160](), [.github/actions/workflow-run-job-linux/action.yml:74-76]()

### Volume Mounts for Reproducibility

The `ci.sh` script and supporting files are mounted into the devcontainer:

```mermaid
graph LR
    subgraph "Host Filesystem"
        A["ci.sh<br/>(generated)"]
        B[".aws/credentials"]
        C[".aws/config"]
        D["/__w workspace"]
    end
    
    subgraph "Devcontainer"
        E["/ci.sh<br/>(mounted)"]
        F["/root/.aws/credentials"]
        G["/root/.aws/config"]
        H["/__w workspace<br/>(mounted)"]
    end
    
    A -->|"--volume"| E
    B -->|"--volume"| F
    C -->|"--volume"| G
    D -->|"--volume"| H
```

**Title:** File Mounts for ci.sh Execution

The `ci.sh` script is mounted at the root of the devcontainer filesystem, while the workspace maintains its path structure to ensure path consistency between host and container.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:161-163]()

## Error Output Formatting

The system uses GitHub Actions' logging annotations to make errors highly visible in the CI logs.

### Annotation Syntax

The error output uses the following GitHub Actions commands:

| Command | Purpose | Example |
|---------|---------|---------|
| `::error::` | Creates an error annotation in the workflow summary | `::error:: To replicate this failure locally...` |
| `::group::` | Creates collapsible log section | `::group::️❗ Instructions to Reproduce...` |
| `::endgroup::` | Closes collapsible section | Implied by subsequent group or end of step |

### Visual Formatting

The script uses ANSI color codes for terminal output:

| Color Code | Usage | Visual Effect |
|------------|-------|---------------|
| `\e[1;34m` | Command echo | Blue, bold |
| `\e[1;31m` | Error header | Red, bold |
| `\e[0m` | Reset | Returns to default |

Example output:

```
[1;34mRunning as 'root' user in /github/workspace:[0m
[1;34mmake -C libcudacxx/test[0m
... command output ...
::group::️❗ [1;31mInstructions to Reproduce CI Failure Locally[0m
::error:: To replicate this failure locally, follow the steps below:
...
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:92-93](), [.github/actions/workflow-run-job-linux/action.yml:96]()

## Path Management for Reproducibility

The Linux execution environment uses a symlink strategy to ensure path consistency between the CI environment and local reproduction.

### Host Path Resolution

```mermaid
flowchart TD
    A["GitHub workspace<br/>${{github.workspace}}"] --> B["e.g., /__w/cccl/cccl"]
    C["Container PWD"] --> D["e.g., /github/workspace/cccl"]
    E["Symlink creation"] --> F["ln -s $(pwd) ${{github.workspace}}"]
    
    D --> E
    B --> E
    
    F --> G["Container paths match<br/>host paths"]
    G --> H["Docker mounts work<br/>correctly"]
    G --> I["Reproduction command<br/>uses same paths"]
```

**Title:** Path Symlink Strategy for Reproducibility

The `host_path()` function transforms container paths to host paths when constructing Docker mount arguments:

```bash
host_path() {
  sed "s@/__w@$(dirname "$(dirname "${{github.workspace}}")")@" <<< "$1"
}
```

This transformation is critical because the intermediate `ubuntu-dind` container launches devcontainers on the host daemon, so mount paths must reference the host filesystem, not the intermediate container's view.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:82-87](), [.github/actions/workflow-run-job-linux/action.yml:138-140]()

## Artifact Collection After Errors

Even when jobs fail, the system attempts to collect diagnostic artifacts.

### Artifact Collection Flow

```mermaid
sequenceDiagram
    participant Command as ci.sh execution
    participant Prepare as Prepare job artifacts
    participant Upload as Upload artifacts
    
    Command->>Command: Command fails
    Command->>Command: Print reproduction instructions
    Command->>Prepare: Step executes (always runs)
    
    Note over Prepare: NOT marked as success<br/>(success marker not created)
    
    Prepare->>Prepare: find_and_copy sccache_stats.json
    Prepare->>Prepare: find_and_copy cccl_meta_bench.csv
    
    Prepare->>Upload: Upload partial artifacts
    
    Note over Upload: Artifacts available for debugging<br/>even though job failed
```

**Title:** Artifact Collection in Failed Jobs

The "Prepare job artifacts" step does not create the `success` marker file when a command fails, but it still attempts to collect diagnostic files like `sccache_stats.json` and benchmark data. This allows post-mortem analysis of failed jobs.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:166-200]()

### Conditional Artifact Collection

The `find_and_copy()` function uses the `|| :` operator to prevent failures in artifact collection from masking the original command failure:

```bash
find_and_copy() {
  filename="$1"
  filepath="$(find ${{github.event.repository.name}} -name "${filename}" -print -quit)"
  if [[ -z "$filepath" ]]; then
    echo "${filename} does not exist in repo directory."
    return 1
  fi
  cp -v "$filepath" "$result_dir"
}

find_and_copy "sccache_stats.json" || :
find_and_copy "cccl_meta_bench.csv" || :
```

The `|| :` pattern means "if this command fails, execute `:` (no-op) and continue," preventing artifact collection failures from affecting the job's final exit code.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:176-189]()

## Reproducibility Guarantees

The system provides the following reproducibility guarantees:

| Aspect | Guarantee | Implementation |
|--------|-----------|----------------|
| **Code Version** | Exact commit match | Instructions use `$GITHUB_SHA` for checkout |
| **Container Image** | Deterministic selection | CUDA version + host compiler uniquely identify devcontainer |
| **Command String** | Exact match | `$COMMAND` environment variable preserved in reproduction instructions |
| **Working Directory** | Path consistency | Symlink strategy ensures paths match between CI and local |
| **Error Exit Code** | Preserved | `ci.sh` exits with original command's exit code |

### Non-Reproducible Elements

The following elements are not guaranteed to be reproducible locally:

| Element | Reason | Mitigation |
|---------|--------|------------|
| **AWS sccache access** | Requires credentials | Local builds work without sccache, but slower |
| **GitHub API access** | Requires authentication | Not needed for command reproduction |
| **GPU availability** | Requires NVIDIA hardware | CPU-only commands still reproducible |
| **Timing** | Different hardware | Functional behavior reproducible, timing may vary |

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:98-106]()

---

# Page: Results and Reporting

# Results and Reporting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-results/action.yml](.github/actions/workflow-results/action.yml)
- [.github/actions/workflow-results/final-summary.py](.github/actions/workflow-results/final-summary.py)
- [.github/actions/workflow-results/parse-job-times.py](.github/actions/workflow-results/parse-job-times.py)
- [.github/actions/workflow-results/prepare-execution-summary.py](.github/actions/workflow-results/prepare-execution-summary.py)

</details>



The results and reporting subsystem aggregates execution data from all dispatched jobs, performs timing and success analysis, generates hierarchical summaries, and delivers notifications to multiple channels. This system operates after all jobs complete (or fail) and provides comprehensive feedback to developers through GitHub Step Summary, PR comments, and Slack notifications.

For information about how jobs execute and produce artifacts, see [Job Execution](#5). For details on the workflow generation that precedes job execution, see [Workflow Generation](#3).

## Overview

The `workflow-results` composite action ([.github/actions/workflow-results/action.yml]()) orchestrates a multi-stage pipeline that transforms raw job artifacts and GitHub API data into formatted reports. The pipeline is designed with fault tolerance: most steps use `continue-on-error: true` to ensure partial results are reported even if data collection fails.

**Pipeline Stages:**

```mermaid
graph LR
    subgraph "Input Sources"
        A1["workflow artifacts"]
        A2["job artifacts"]
        A3["GitHub API<br/>(jobs.json)"]
    end
    
    subgraph "Processing Scripts"
        B1["parse-job-times.py"]
        B2["prepare-execution-summary.py"]
        B3["final-summary.py"]
        B4["verify-job-success.py"]
    end
    
    subgraph "Intermediate Data"
        C1["results/job_times.json"]
        C2["execution/heading.txt"]
        C3["execution/projects/*_summary.json"]
    end
    
    subgraph "Output Channels"
        D1["GITHUB_STEP_SUMMARY"]
        D2["PR Comment"]
        D3["Slack Notifications"]
        D4["success output"]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> C1
    C1 --> B2
    B2 --> C2
    B2 --> C3
    C2 --> B3
    C3 --> B3
    B3 --> D1
    B3 --> D2
    B3 --> D3
    A2 --> B4
    B4 --> D4
```

**Sources:** [.github/actions/workflow-results/action.yml:1-213]()

## Artifact Collection

Job artifacts are produced during execution and uploaded to GitHub Actions artifact storage. The `workflow-results` action downloads these artifacts for analysis.

### Artifact Types

| Artifact Name | Content | Produced By |
|---------------|---------|-------------|
| `workflow` | `workflow.json`, `job_ids.json`, `runner_summary.json`, `override.json` (if applicable) | `workflow-build` action |
| `jobs-*` | Per-job artifacts: `success` marker, `sccache_stats.json`, `cccl_meta_bench.csv` | Individual job executions |

### Download Process

The action downloads artifacts in two stages:

1. **Workflow Artifacts** ([.github/actions/workflow-results/action.yml:30-34]()): Downloaded to `workflow/` directory using `actions/download-artifact@v4` with explicit `name: workflow`.

2. **Job Artifacts** ([.github/actions/workflow-results/action.yml:36-42]()): Downloaded to `jobs/` directory using pattern matching (`pattern: jobs-*`) with `merge-multiple: true` to consolidate all job artifacts into a single directory structure.

### Artifact Cleanup

Windows-produced artifacts may have incorrect line endings. The cleanup step ([.github/actions/workflow-results/action.yml:44-57]()) installs `dos2unix` and converts all files in the `jobs/` directory to Unix line endings.

**Directory Structure After Download:**

```
workflow/
├── workflow.json
├── job_ids.json
├── runner_summary.json
└── override.json (optional)

jobs/
├── <job_id_1>/
│   ├── success (marker file)
│   ├── sccache_stats.json
│   └── cccl_meta_bench.csv
├── <job_id_2>/
│   └── ... (may be incomplete if job failed)
└── ...
```

**Sources:** [.github/actions/workflow-results/action.yml:30-57]()

## Job Timing Analysis

The `parse-job-times.py` script ([.github/actions/workflow-results/parse-job-times.py]()) extracts timing data from the GitHub API and correlates it with job definitions to calculate execution durations and overhead.

### Data Sources

```mermaid
graph TB
    subgraph "Inputs"
        A["workflow.json<br/>job definitions"]
        B["results/jobs.json<br/>GitHub API data"]
    end
    
    subgraph "parse-job-times.py"
        C["generate_job_id_map()"]
        D["Process job times"]
        E["Extract 'Run command' step"]
        F["Calculate overhead"]
    end
    
    subgraph "Output"
        G["results/job_times.json<br/>{job_id: timing_data}"]
    end
    
    A --> C
    C --> D
    B --> D
    D --> E
    E --> F
    F --> G
```

**Sources:** [.github/actions/workflow-results/parse-job-times.py:1-130]()

### Job Name to ID Mapping

The `generate_job_id_map()` function ([.github/actions/workflow-results/parse-job-times.py:29-45]()) creates a mapping from GitHub's full job names to internal job IDs:

- **Standalone jobs**: `"{group_name} / {job['name']}"` → `job['id']`
- **Two-stage jobs**: `"{group_name} / {pc['id']} / {job['name']}"` → `job['id']`

This mapping is necessary because GitHub's job names differ from the internal job IDs used in artifact paths.

### Timing Calculations

For each job, the script extracts ([.github/actions/workflow-results/parse-job-times.py:68-108]()):

| Field | Calculation | Format |
|-------|-------------|--------|
| `started_at` | From `job['started_at']` | ISO 8601 timestamp |
| `completed_at` | From `job['completed_at']` | ISO 8601 timestamp |
| `started_epoch_secs` | Converted to Unix epoch | Seconds since 1970-01-01 |
| `completed_epoch_secs` | Converted to Unix epoch | Seconds since 1970-01-01 |
| `job_seconds` | `completed - started` | Float seconds |
| `job_duration` | Formatted `job_seconds` | HH:MM:SS string |
| `command_seconds` | Duration of "Run command" step | Float seconds |
| `command_duration` | Formatted `command_seconds` | HH:MM:SS string |

**Overhead Calculation:**
```
overhead_percent = (job_seconds - command_seconds) / command_seconds * 100
```

This identifies time spent on non-command activities (checkout, setup, artifact upload, etc.).

### Output Format: job_times.json

```json
{
  "job_id_abc123": {
    "name": "linux / Job Name",
    "started_at": "2024-05-09T06:52:20Z",
    "completed_at": "2024-05-09T07:15:35Z",
    "started_epoch_secs": 1715239940.0,
    "completed_epoch_secs": 1715241335.0,
    "job_duration": "0:23:15",
    "job_seconds": 1395.0,
    "command_duration": "0:20:10",
    "command_seconds": 1210.0
  }
}
```

**Sources:** [.github/actions/workflow-results/parse-job-times.py:48-111](), [.github/actions/workflow-results/action.yml:92-97]()

## Execution Summary Generation

The `prepare-execution-summary.py` script ([.github/actions/workflow-results/prepare-execution-summary.py]()) builds hierarchical summaries organized by project, tag, and tag value. It implements sophisticated logic to identify "likely culprits" for failures.

### Summary Hierarchy

```mermaid
graph TB
    Root["Overall Summary<br/>(all jobs)"]
    Root --> P1["Project: libcudacxx"]
    Root --> P2["Project: thrust"]
    Root --> P3["Project: cub"]
    
    P1 --> T1["Tag: ctk"]
    P1 --> T2["Tag: cxx"]
    P1 --> T3["Tag: gpu"]
    
    T1 --> V1["Value: 11.1"]
    T1 --> V2["Value: 12.0"]
    T1 --> V3["Value: 12.5"]
    
    T2 --> V4["Value: gcc9"]
    T2 --> V5["Value: gcc10"]
    T2 --> V6["Value: clang16"]
```

**Sources:** [.github/actions/workflow-results/prepare-execution-summary.py:102-162]()

### Summary Entry Structure

Each node in the hierarchy maintains ([.github/actions/workflow-results/prepare-execution-summary.py:55-99]()):

| Field | Type | Description |
|-------|------|-------------|
| `passed` | int | Count of successful jobs |
| `failed` | int | Count of failed jobs |
| `job_time` | float | Sum of `job_seconds` for all jobs |
| `command_time` | float | Sum of `command_seconds` for all jobs |
| `max_job_time` | float | Maximum `job_seconds` among all jobs |
| `sccache` | object | `{requests: int, hits: int}` aggregated across jobs |

### Likely Culprit Detection

The script identifies problematic tag values using two-level analysis ([.github/actions/workflow-results/prepare-execution-summary.py:254-280]()):

**Tag-Level Analysis:**
```python
def rank_tag(tag_summary):
    num_values = len(tag_summary['values'])
    num_failing_values = sum(1 for v in tag_summary['values'].values() if v['failed'] > 0)
    
    if num_values > 1 and num_failing_values == 1:
        return 0  # Likely culprit tag (rank highest)
    elif num_failing_values > 0 and num_failing_values < num_values:
        return 1  # Mixed results
    elif tag_failures > 0:
        return 2  # All values failing
    return 3  # No failures
```

**Value-Level Flags:**

| Condition | Flag | Meaning |
|-----------|------|---------|
| `failed == parent_failed` and `passed == 0` and `parent_size > 1` | 🔥 | Likely culprit: all tag failures attributable to this value, zero passes |
| `failed == parent_failed` and `passed > 0` and `parent_size > 1` | 🔍 | Suspicious: all tag failures include this value, but it has some passes |
| `passed == 0` | 🟥 | All jobs with this value failed |
| `failed > 0` | 🟨 | Some jobs with this value failed |
| `failed == 0` | 🟩 | All jobs with this value passed |

### Summary Statistics Formatting

The `get_summary_stats()` function ([.github/actions/workflow-results/prepare-execution-summary.py:195-221]()) formats metrics:

```
Pass: {percent:3}%/{total} | Total: {duration} | Avg: {duration} | Max: {duration} | Hits: {percent:3}%/{requests}
```

**Time Formatting** ([.github/actions/workflow-results/prepare-execution-summary.py:179-192]()):
- `>= 1 day`: `{days}d {hours:02}h`
- `>= 1 hour`: `{hours}h {minutes:02}m`
- `< 1 hour`: `{minutes}m {seconds:02}s`

### Output Files

```mermaid
graph LR
    A["prepare-execution-summary.py"]
    A --> B["execution/heading.txt"]
    A --> C["execution/projects/000_project1_summary.json"]
    A --> D["execution/projects/001_project2_summary.json"]
    A --> E["execution/projects/002_project3_summary.json"]
```

**execution/heading.txt** ([.github/actions/workflow-results/prepare-execution-summary.py:334]()): Single-line overall summary with walltime and aggregate statistics.

**execution/projects/NNN_projectname_summary.json** ([.github/actions/workflow-results/prepare-execution-summary.py:319-325]()): Per-project JSON with `heading` and `body` fields. Projects are sorted by failure count (descending), then total job count.

**Sources:** [.github/actions/workflow-results/prepare-execution-summary.py:328-344](), [.github/actions/workflow-results/action.yml:99-104]()

## Final Summary Assembly

The `final-summary.py` script ([.github/actions/workflow-results/final-summary.py]()) assembles all summary components into a single Markdown/HTML document with collapsible sections.

### Document Structure

```mermaid
graph TB
    A["final-summary.py"]
    B["execution/heading.txt"]
    C["execution/projects/*.json"]
    D["workflow/override.json"]
    E["workflow/changes.md"]
    F["workflow/runner_summary.json"]
    
    A --> Output["final_summary.md"]
    
    B -->|main heading| A
    C -->|per-project details| A
    D -->|override notice| A
    E -->|change detection| A
    F -->|runner allocation| A
```

**Sources:** [.github/actions/workflow-results/final-summary.py:1-67]()

### Summary Components

The script reads and formats ([.github/actions/workflow-results/final-summary.py:41-63]()):

1. **Main Heading** (from `execution/heading.txt`): Wraps all content in a `<details>` tag with the heading as the summary.

2. **Project Summaries** (from `execution/projects/*.json`): Each project rendered as a nested `<details>` within an unordered list.

3. **Override Matrix** (from `workflow/override.json`, optional): If present, displays the override matrix as a JSON code block.

4. **Change Detection** (from `workflow/changes.md`, optional): Displays detected file changes.

5. **Runner Summary** (from `workflow/runner_summary.json`, optional): Shows runner allocation statistics.

### Project Summary Format

Each `*_summary.json` file has the structure ([.github/actions/workflow-results/final-summary.py:19-22]()):

```json
{
  "heading": "🟨 project_name: Pass: 85%/120 | Total: 2h 15m | ...",
  "body": "```\n🚨 ctk: 12.5 🚨\n  🔥 12.5 ...\n  🟩 11.1 ...\n```"
}
```

The body is pre-formatted as a Markdown code block with emoji flags and statistics.

### Output Processing

The final summary is output to three destinations ([.github/actions/workflow-results/action.yml:106-128]()):

1. **stdout**: For GitHub Actions log viewing
2. **GITHUB_OUTPUT** (`SUMMARY`): URL-encoded for use in subsequent steps (PR comments)
3. **GITHUB_STEP_SUMMARY**: Direct copy for inline workflow UI display

**URL Encoding** ([.github/actions/workflow-results/action.yml:116-122]()): The summary is URL-encoded using Python's `urllib.parse.quote()` to safely pass special characters and newlines through GitHub Actions outputs.

**Sources:** [.github/actions/workflow-results/final-summary.py:41-63](), [.github/actions/workflow-results/action.yml:106-128]()

## Success Verification

The `verify-job-success.py` script ([.github/actions/workflow-results/action.yml:155-177]()) determines overall workflow success by checking for job success markers.

### Success Marker Detection

```mermaid
graph LR
    A["workflow/job_ids.json"]
    B["verify-job-success.py"]
    C["jobs/{job_id}/success"]
    D["success output"]
    
    A -->|list of job IDs| B
    B -->|check existence| C
    C -->|all present?| D
```

The script reads `workflow/job_ids.json` to obtain the list of expected job IDs, then checks if each job's `success` marker file exists at `jobs/{job_id}/success`. The script ([.github/actions/workflow-results/action.yml:160]()):

- Returns exit code `0` if all success markers exist
- Returns non-zero exit code if any markers are missing

### Override Matrix Handling

If `workflow/override.json` exists, the workflow was run with a manually specified matrix, indicating a non-standard configuration. In this case, the action fails all jobs unconditionally ([.github/actions/workflow-results/action.yml:169-175]()) to prevent accidental merges with incomplete testing.

### Success Output

The `success` output ([.github/actions/workflow-results/action.yml:22-24](), [.github/actions/workflow-results/action.yml:164-177]()) is set to:

- `true`: All jobs succeeded and no override matrix was used
- `false`: Any job failed or an override matrix was present

This boolean output can be used by calling workflows to determine whether to proceed with subsequent steps (e.g., deployment, merging).

**Sources:** [.github/actions/workflow-results/action.yml:155-177]()

## Notification System

The action delivers notifications to multiple channels based on workflow outcomes and configured credentials.

### Notification Channels

```mermaid
graph TB
    subgraph "Notification Targets"
        A["GitHub Step Summary<br/>(inline UI)"]
        B["PR Comment<br/>(via GitHub API)"]
        C["Slack Log Channel<br/>(verbose)"]
        D["Slack Alert Channel<br/>(failures only)"]
    end
    
    subgraph "Conditions"
        E["Always<br/>(if content available)"]
        F["If pr_number provided"]
        G["If slack_token provided"]
        H["If failure detected"]
    end
    
    E --> A
    F --> B
    G --> C
    H --> D
```

**Sources:** [.github/actions/workflow-results/action.yml:128-212]()

### GitHub Step Summary

Written directly to `${GITHUB_STEP_SUMMARY}` ([.github/actions/workflow-results/action.yml:128]()), this displays the full summary inline in the GitHub Actions workflow UI. No conditions required.

### PR Comment

Posted if both `github_token` and `pr_number` inputs are provided ([.github/actions/workflow-results/action.yml:130-153]()):

**Process:**
1. Retrieve `SUMMARY` output from `final-summary` step (URL-encoded)
2. Decode using `decodeURIComponent()` in JavaScript
3. Post comment via `github.rest.issues.createComment()`

**API Call:**
```javascript
github.rest.issues.createComment({
  owner: context.repo.owner,
  repo: context.repo.repo,
  issue_number: pr_number,
  body: decodedSummary
});
```

### Slack Log Notification

Sent to `slack_log` channel if both `slack_token` and `slack_log` are provided ([.github/actions/workflow-results/action.yml:179-195]()). Triggered with `if: always()` to ensure notification even on failure.

**Message Format:**
```
Workflow '{workflow_type}' has finished with status `{status}`:

{exec_summary}

Details: {summary_url}
```

**Variables:**
- `workflow_type`: `${{ github.workflow }}` (e.g., "nightly", "pull_request")
- `status`: `${{ steps.check-success.outcome }}` (e.g., "success", "failure")
- `exec_summary`: Content of `execution/heading.txt`
- `summary_url`: GitHub Actions run URL

### Slack Alert Notification

Sent to `slack_alert` channel only on failure ([.github/actions/workflow-results/action.yml:197-212]()). Triggered with `if: failure()`.

**Message Format:**
```
Workflow '{workflow_type}' has failed:

{exec_summary}

Details: {summary_url}
```

This provides a dedicated channel for critical alerts without verbose log noise.

### Action Inputs for Notifications

| Input | Required | Purpose |
|-------|----------|---------|
| `github_token` | No | Enables PR commenting and GitHub API access |
| `pr_number` | No | PR to comment on (requires `github_token`) |
| `slack_token` | No | Enables Slack notifications |
| `slack_log` | No | Slack channel ID for verbose logs |
| `slack_alert` | No | Slack channel ID for failure alerts |

**Sources:** [.github/actions/workflow-results/action.yml:4-19](), [.github/actions/workflow-results/action.yml:130-212]()

## Fault Tolerance

Most processing steps use `continue-on-error: true` to ensure partial results are reported:

| Step | continue-on-error | Rationale |
|------|-------------------|-----------|
| Download job artifacts | ✓ | Jobs may have failed before producing artifacts |
| Clean up job artifacts | ✓ | Line ending conversion is non-critical |
| Fetch workflow job info | ✓ | Timing data is optional |
| Parse job times | ✓ | Summary can be generated without timing |
| Prepare execution summary | ✓ | Partial summaries are better than none |
| Prepare final summary | ✓ | Step summary can still be written |
| Comment on PR | ✓ | PR comments are optional |
| Check for job success | ✗ | Success determination must be definitive |

The `check-success` step ([.github/actions/workflow-results/action.yml:155-177]()) does not use `continue-on-error` because it sets the `success` output that determines overall workflow status. This ensures that failures in success verification propagate correctly.

**Sources:** [.github/actions/workflow-results/action.yml:37-109](), [.github/actions/workflow-results/action.yml:155-177]()

---

# Page: Artifact Collection

# Artifact Collection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-results/action.yml](.github/actions/workflow-results/action.yml)
- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)
- [.github/actions/workflow-run-job-windows/action.yml](.github/actions/workflow-run-job-windows/action.yml)

</details>



## Purpose and Scope

This page documents the artifact collection system used to gather outputs from executed jobs for analysis and reporting. It covers the types of artifacts produced by jobs, the upload mechanisms in both Linux and Windows execution environments, and the download and cleanup processes performed by the results collection action.

For information about how these artifacts are analyzed for timing data, see [Job Timing Analysis](#6.2). For success verification using these artifacts, see [Success Verification](#6.5).

## Overview

The artifact collection system enables communication between job execution workflows and the results aggregation workflow. Each job produces a set of standard artifacts that indicate success status and provide performance metrics. These artifacts are uploaded to GitHub Actions artifact storage with structured naming conventions, then downloaded and merged by the `workflow-results` action for centralized analysis.

**Artifact Collection Flow**

```mermaid
graph TB
    subgraph "Job Execution"
        LinuxJob["workflow-run-job-linux"]
        WindowsJob["workflow-run-job-windows"]
        
        LinuxJob --> LinuxPrep["Prepare job artifacts<br/>(lines 166-194)"]
        WindowsJob --> WinPrep["Prepare job artifacts<br/>(lines 65-92)"]
        
        LinuxPrep --> LinuxUpload["Upload: jobs-{id}<br/>(lines 195-201)"]
        WinPrep --> WinUpload["Upload: jobs-{id}<br/>(lines 93-99)"]
    end
    
    subgraph "GitHub Artifacts Storage"
        Storage["Artifact: jobs-{id}<br/>Path: jobs/{id}/*"]
        
        LinuxUpload --> Storage
        WinUpload --> Storage
    end
    
    subgraph "Results Collection"
        Download["Download artifacts<br/>Pattern: jobs-*<br/>merge-multiple: true<br/>(lines 36-42)"]
        Cleanup["Clean up artifacts<br/>dos2unix conversion<br/>(lines 44-57)"]
        
        Storage --> Download
        Download --> Cleanup
    end
    
    subgraph "Merged Structure"
        MergedDir["jobs/<br/>  job-1/<br/>    success<br/>    sccache_stats.json<br/>    ...<br/>  job-2/<br/>    success<br/>    ..."]
        
        Cleanup --> MergedDir
    end
```

Sources: [.github/actions/workflow-run-job-linux/action.yml:166-201](), [.github/actions/workflow-run-job-windows/action.yml:65-99](), [.github/actions/workflow-results/action.yml:30-57]()

## Artifact Types

Each job produces a standard set of artifacts that serve different purposes in the results analysis pipeline.

| Artifact File | Purpose | Produced By | Required |
|--------------|---------|-------------|----------|
| `success` | Marker file indicating job completed successfully | All jobs | Yes |
| `sccache_stats.json` | Distributed compilation cache statistics | Jobs using sccache | No |
| `cccl_meta_bench.csv` | Benchmark results in CSV format | Benchmark jobs | No |
| `cccl_meta_bench.db` | Benchmark results database | Benchmark jobs | No |
| `cccl_meta_bench.log` | Benchmark execution logs | Benchmark jobs | No |

The `success` marker file is the only required artifact. Its presence or absence determines whether a job is considered successful by the verification system (see [Success Verification](#6.5)).

Sources: [.github/actions/workflow-run-job-linux/action.yml:173-189](), [.github/actions/workflow-run-job-windows/action.yml:74-87]()

## Upload Process

### Linux Job Artifacts

The Linux execution action collects artifacts after the job command completes in the devcontainer. The artifact preparation step is defined in [.github/actions/workflow-run-job-linux/action.yml:166-194]().

**Artifact Preparation Steps:**

1. **Create result directory**: `jobs/${{inputs.id}}/`
2. **Write success marker**: `touch "$result_dir/success"`
3. **Search and copy optional artifacts**: Uses `find_and_copy()` helper function
4. **Log artifact tree**: Displays collected artifacts in collapsible group

**File Search Implementation**

The `find_and_copy()` function searches the repository checkout directory for specific filenames and copies them to the results directory:

```bash
find_and_copy() {
  filename="$1"
  filepath="$(find ${{github.event.repository.name}} -name "${filename}" -print -quit)"
  if [[ -z "$filepath" ]]; then
    echo "${filename} does not exist in repo directory."
    return 1
  fi
  cp -v "$filepath" "$result_dir"
}
```

The search uses `find ... -print -quit` to locate the first matching file and terminates immediately. If no file is found, the function returns a non-zero exit code, but these failures are ignored using the `|| :` shell operator to prevent pipeline failures for optional artifacts.

**Upload Configuration**

Artifacts are uploaded using `actions/upload-artifact@v4` with the following parameters:

- **Name**: `jobs-${{inputs.id}}` (e.g., `jobs-abc123def456`)
- **Path**: `jobs` directory (contains `jobs/{id}/*` structure)
- **Compression Level**: `0` (no compression for performance)

Sources: [.github/actions/workflow-run-job-linux/action.yml:166-201]()

### Windows Job Artifacts

The Windows execution action follows a similar pattern but with platform-specific considerations. The artifact preparation is defined in [.github/actions/workflow-run-job-windows/action.yml:65-92]().

**Key Differences from Linux:**

1. **Limited artifact types**: Only collects `success` and `sccache_stats.json` (no benchmark artifacts)
2. **Tree command unavailable**: Uses `find` instead of `tree` for directory listing
3. **Line ending issues**: Windows artifacts may contain CRLF line endings that require cleanup

The `find_and_copy()` implementation is identical to Linux, but the invocation uses `|| true` instead of `|| :` (functionally equivalent).

Sources: [.github/actions/workflow-run-job-windows/action.yml:65-99]()

## Download and Merge Process

The `workflow-results` action downloads artifacts from all completed jobs and merges them into a unified directory structure.

**Download Workflow**

```mermaid
graph LR
    subgraph "Artifact Storage"
        A1["jobs-abc123"]
        A2["jobs-def456"]
        A3["jobs-ghi789"]
        AN["jobs-..."]
    end
    
    subgraph "Download Action"
        DL["actions/download-artifact@v4<br/>pattern: jobs-*<br/>merge-multiple: true"]
    end
    
    subgraph "Merged Directory"
        M["jobs/<br/>├── abc123/<br/>│   ├── success<br/>│   └── sccache_stats.json<br/>├── def456/<br/>│   └── success<br/>└── ghi789/<br/>    └── success"]
    end
    
    A1 --> DL
    A2 --> DL
    A3 --> DL
    AN --> DL
    
    DL --> M
```

Sources: [.github/actions/workflow-results/action.yml:36-42]()

**Download Configuration**

The download step is defined in [.github/actions/workflow-results/action.yml:36-42]():

```yaml
- name: Download job artifacts
  continue-on-error: true
  uses: actions/download-artifact@v4
  with:
    path: jobs
    pattern: jobs-*
    merge-multiple: true
```

**Key Configuration Details:**

- **Pattern matching**: `jobs-*` matches all artifacts uploaded with the standardized naming convention
- **Merge strategy**: `merge-multiple: true` combines all matching artifacts into a single directory tree
- **Error tolerance**: `continue-on-error: true` allows the workflow to continue even if no jobs succeeded (the verification step will catch this failure)
- **Destination path**: `jobs` directory relative to the workflow workspace

The merge strategy preserves the internal directory structure from each artifact. Since each job uploads its artifacts in a `jobs/{id}/` subdirectory, the merged result contains all job directories side-by-side: `jobs/job1/`, `jobs/job2/`, etc.

Sources: [.github/actions/workflow-results/action.yml:36-42]()

## Artifact Cleanup

After downloading artifacts, a cleanup step normalizes line endings and displays the merged directory structure. This step is defined in [.github/actions/workflow-results/action.yml:44-57]().

**Cleanup Operations**

```mermaid
graph TB
    subgraph "Cleanup Process"
        A["Downloaded artifacts<br/>(may have CRLF)"]
        B["Install dos2unix<br/>apt-get install dos2unix"]
        C["Convert line endings<br/>find jobs -type f -exec dos2unix"]
        D["Display tree<br/>tree jobs"]
        
        A --> B
        B --> C
        C --> D
    end
    
    subgraph "Output"
        E["Normalized artifacts<br/>(Unix LF line endings)"]
        F["Collapsible log group<br/>'Job artifacts'"]
        
        D --> E
        D --> F
    end
```

Sources: [.github/actions/workflow-results/action.yml:44-57]()

**Line Ending Normalization**

Windows jobs produce artifacts with CRLF (Carriage Return + Line Feed) line endings, which can cause issues when parsing files on Linux-based runners. The cleanup step converts all files to Unix-style LF line endings using `dos2unix`:

```bash
# Fix artifacts written on windows:
echo "::group::Fixing line endings in job artifacts"
sudo apt-get update
sudo apt-get install -y dos2unix
find jobs -type f -exec dos2unix -v {} \;
echo "::endgroup::"
```

The `find` command recursively processes all files in the `jobs` directory, applying `dos2unix` to each file. The `-v` flag provides verbose output showing which files were converted.

**Directory Visualization**

After normalization, the step displays the complete artifact directory tree in a collapsible GitHub Actions log group:

```bash
echo "::group::Job artifacts"
tree jobs
echo "::endgroup::"
```

This provides visibility into which artifacts were successfully collected from each job, aiding debugging when artifacts are missing.

**Error Tolerance**

The entire cleanup step uses `continue-on-error: true` to ensure the workflow proceeds even if:
- `dos2unix` installation fails
- Some files cannot be converted (binary files, permission issues)
- The `tree` command is unavailable

This resilience is critical because partial artifact collection is valuable even when some steps fail.

Sources: [.github/actions/workflow-results/action.yml:44-57]()

## Directory Structure

The artifact collection system produces a standardized directory hierarchy that subsequent analysis steps depend on.

**Complete Artifact Hierarchy**

```
workflow/                          # Downloaded from 'workflow' artifact
├── workflow.json                  # Complete job definitions
├── job_ids.json                   # Job ID mappings
├── runner_summary.json            # Runner allocation info
└── dispatch.json                  # Dispatch group categorization

jobs/                              # Downloaded from 'jobs-*' artifacts, merged
├── {job-id-1}/                    # Each job has its own subdirectory
│   ├── success                    # Marker file (required)
│   ├── sccache_stats.json         # sccache statistics (optional)
│   ├── cccl_meta_bench.csv        # Benchmark CSV (optional)
│   ├── cccl_meta_bench.db         # Benchmark database (optional)
│   └── cccl_meta_bench.log        # Benchmark logs (optional)
├── {job-id-2}/
│   ├── success
│   └── sccache_stats.json
└── {job-id-3}/
    └── success

results/                           # Created by analysis scripts
├── jobs.json                      # GitHub API job data
└── job_times.json                 # Parsed timing data

execution/                         # Created by summary scripts
├── heading.txt                    # Overall execution summary
└── projects/                      # Per-project summaries
    ├── project1_summary.json
    └── project2_summary.json
```

**Directory Usage by Analysis Steps**

| Directory | Created By | Used By | Purpose |
|-----------|------------|---------|---------|
| `workflow/` | workflow-build action | All analysis scripts | Job definitions and metadata |
| `jobs/` | workflow-run-job-* actions | verify-job-success.py, prepare-execution-summary.py | Job outputs and status |
| `results/` | workflow-results action | prepare-execution-summary.py, final-summary.py | Intermediate analysis data |
| `execution/` | prepare-execution-summary.py | final-summary.py | Hierarchical summaries |

**Job ID Format**

Job IDs in artifact names and directory paths follow the format generated by the workflow generation system. These IDs are deterministic based on job configuration and are used to correlate artifacts with job definitions in `workflow.json`.

Sources: [.github/actions/workflow-results/action.yml:30-57](), [.github/actions/workflow-run-job-linux/action.yml:170-172](), [.github/actions/workflow-run-job-windows/action.yml:71-72]()

## Artifact Naming Conventions

**Upload Naming**

Each job uploads its artifacts with a unique name combining a fixed prefix and the job ID:

```
jobs-{job-id}
```

For example:
- `jobs-libcudacxx-cpp17-gcc10-cuda12.0`
- `jobs-thrust-cpp20-nvcc11.8-gpu-v100`

This naming scheme enables:
1. **Pattern matching**: The `jobs-*` pattern downloads all job artifacts
2. **Uniqueness**: Each job's artifacts are isolated
3. **Traceability**: Artifact names correspond to job definitions in `workflow.json`

**Download Pattern Matching**

The download action uses glob pattern `jobs-*` which matches all artifacts starting with `jobs-`. The `merge-multiple: true` option instructs the action to extract all matching artifacts into the same `jobs/` directory, preserving their internal subdirectory structure.

**Artifact Name Collision Handling**

Since each job creates artifacts in a subdirectory named after its ID (`jobs/{id}/`), and job IDs are guaranteed unique by the workflow generation system, there are no collisions when merging multiple artifacts into the same parent directory.

Sources: [.github/actions/workflow-run-job-linux/action.yml:195-201](), [.github/actions/workflow-run-job-windows/action.yml:93-99](), [.github/actions/workflow-results/action.yml:36-42]()

## Error Handling

The artifact collection system implements multiple layers of error tolerance to ensure maximum data recovery even when individual jobs or collection steps fail.

**Upload-Side Error Handling**

1. **Optional artifact search**: The `find_and_copy()` function returns non-zero for missing files, but failures are ignored using `|| :` (Linux) or `|| true` (Windows)
2. **Success marker always written**: The `success` file is written unconditionally before attempting to collect optional artifacts
3. **Upload always attempted**: Even if optional artifacts fail to copy, the upload step executes

**Download-Side Error Handling**

1. **Download continues on error**: `continue-on-error: true` prevents workflow failure if no artifacts exist (e.g., all jobs failed before artifact upload)
2. **Cleanup continues on error**: Line ending conversion and tree display failures don't block subsequent analysis
3. **Verification detects missing artifacts**: The verify-job-success.py script explicitly checks for missing `success` markers (see [Success Verification](#6.5))

**Partial Success Scenarios**

The system gracefully handles these common failure modes:

| Scenario | Behavior | Impact |
|----------|----------|--------|
| Job fails before artifact upload | Download step continues; verify-job-success.py detects missing artifact | Workflow reports failure with specific job ID |
| Optional artifact missing | Success marker uploaded; analysis proceeds with available data | No sccache stats or benchmarks for that job |
| All jobs fail | Download returns no artifacts; continue-on-error prevents workflow abort | Verification step fails workflow with clear message |
| Line ending conversion fails | Subsequent scripts may encounter parse errors | Minimal impact; most scripts handle CRLF |

Sources: [.github/actions/workflow-run-job-linux/action.yml:176-189](), [.github/actions/workflow-run-job-windows/action.yml:77-87](), [.github/actions/workflow-results/action.yml:36-57]()

---

# Page: Job Timing Analysis

# Job Timing Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-results/parse-job-times.py](.github/actions/workflow-results/parse-job-times.py)

</details>



## Purpose and Scope

This document describes the `parse-job-times.py` script, which extracts timing data from GitHub Actions job execution and correlates it with workflow definitions. The script processes job duration information from the GitHub API, identifies the actual command execution time within each job, and calculates overhead from environment setup and teardown operations.

For information about how these timing results are aggregated and organized into execution summaries, see [Execution Summary Generation](#6.3). For details on artifact collection that precedes timing analysis, see [Artifact Collection](#6.1).

**Sources:** [.github/actions/workflow-results/parse-job-times.py:1-130]()

---

## Overview

The timing analysis system bridges GitHub Actions job execution data with the workflow configuration to produce structured timing metrics. It operates as part of the `workflow-results` action after all jobs complete.

```mermaid
graph LR
    subgraph "Inputs"
        A["workflow.json"]
        B["jobs.json<br/>(GitHub API)"]
    end
    
    subgraph "parse-job-times.py"
        C["generate_job_id_map()"]
        D["Parse timestamps"]
        E["Calculate durations"]
        F["Identify 'Run command' step"]
        G["Compute overhead"]
    end
    
    subgraph "Output"
        H["job_times.json"]
        I["Console report"]
    end
    
    A --> C
    B --> D
    C --> E
    D --> E
    E --> F
    F --> G
    G --> H
    G --> I
```

**Diagram: Timing Analysis Data Flow**

**Sources:** [.github/actions/workflow-results/parse-job-times.py:48-129]()

---

## Input Requirements

### workflow.json Structure

The `workflow.json` file defines the expected job hierarchy with group names, job names, and unique job IDs. This is the authoritative source for mapping GitHub Actions job names to internal job identifiers.

```mermaid
graph TB
    subgraph "workflow.json Structure"
        A["workflow.json"]
        B["Group Name"]
        C["standalone[]"]
        D["two_stage[]"]
        E["Job Object"]
        F["Producer/Consumer Chain"]
        G["Job ID"]
    end
    
    A --> B
    B --> C
    B --> D
    C --> E
    D --> F
    F --> E
    E --> G
```

**Diagram: workflow.json Hierarchy**

**Sources:** [.github/actions/workflow-results/parse-job-times.py:29-45]()

### jobs.json Structure

The `jobs.json` file is fetched from the GitHub Actions API and contains actual execution data for all jobs in the workflow run. Each job includes:

| Field | Description | Format |
|-------|-------------|--------|
| `name` | Full GitHub Actions job name | String (includes group and job name) |
| `started_at` | Job start timestamp | ISO 8601 (UTC) |
| `completed_at` | Job completion timestamp | ISO 8601 (UTC) |
| `steps[]` | Array of step execution data | Array of step objects |

**Sources:** [.github/actions/workflow-results/parse-job-times.py:10-15](), [.github/actions/workflow-results/parse-job-times.py:68-93]()

---

## Job ID Mapping

The `generate_job_id_map()` function creates a mapping from GitHub Actions job names to internal job IDs defined in `workflow.json`. This mapping is essential because GitHub's job names follow a hierarchical format while the timing analysis requires compact job IDs.

### Standalone Job Name Format

For standalone jobs:
```
{group_name} / {job_name}
```

Example: `pull_request / linux-gcc12-cuda12.2-x86_64-test`

### Two-Stage Job Name Format

For producer/consumer jobs:
```
{group_name} / {producer_consumer_id} / {job_name}
```

Example: `pull_request / thrust-linux-gcc12-cuda12.2-x86_64 / build`

```mermaid
graph TB
    subgraph "generate_job_id_map()"
        A["Iterate workflow.json"]
        B["Process standalone jobs"]
        C["Process two_stage jobs"]
        D["Build job_id_map"]
    end
    
    subgraph "Standalone Processing"
        E["name = group_name / job['name']"]
        F["job_id_map[name] = job['id']"]
    end
    
    subgraph "Two-Stage Processing"
        G["Iterate producers + consumers"]
        H["name = group_name / pc['id'] / job['name']"]
        I["job_id_map[name] = job['id']"]
    end
    
    A --> B
    A --> C
    B --> E
    E --> F
    F --> D
    C --> G
    G --> H
    H --> I
    I --> D
```

**Diagram: Job ID Mapping Algorithm**

**Sources:** [.github/actions/workflow-results/parse-job-times.py:29-45]()

---

## Time Extraction and Calculation

### Timestamp Parsing

Job timestamps are provided by GitHub in ISO 8601 format with UTC timezone. The script parses these using Python's `datetime.strptime()` with the format string `"%Y-%m-%dT%H:%M:%SZ"`.

```mermaid
graph LR
    A["started_at<br/>2024-05-09T06:52:20Z"]
    B["strptime()"]
    C["datetime object"]
    D["timestamp()"]
    E["started_epoch_secs"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    
    F["completed_at<br/>2024-05-09T07:15:40Z"]
    G["strptime()"]
    H["datetime object"]
    I["timestamp()"]
    J["completed_epoch_secs"]
    
    F --> G
    G --> H
    H --> I
    I --> J
```

**Diagram: Timestamp Processing Pipeline**

**Sources:** [.github/actions/workflow-results/parse-job-times.py:73-92]()

### Duration Calculation

The script calculates three timing metrics:

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| `job_seconds` | `completed_time - started_time` (total seconds) | Total job duration |
| `job_duration` | `str(timedelta(seconds=job_seconds))` | Human-readable total duration |
| `command_seconds` | Duration of "Run command" step | Actual command execution time |
| `command_duration` | `str(timedelta(seconds=command_seconds))` | Human-readable command duration |

**Sources:** [.github/actions/workflow-results/parse-job-times.py:82-108]()

### Command Step Identification

The script identifies the actual command execution time by searching for a step named `"run command"` (case-insensitive) within the job's step array.

```mermaid
graph TD
    A["Iterate job['steps']"]
    B{"step['name'].lower() == 'run command'?"}
    C["Parse step['started_at']"]
    D["Parse step['completed_at']"]
    E["command_seconds = completed - started"]
    F["Continue to next step"]
    G["command_seconds = 0"]
    
    A --> B
    B -->|Yes| C
    B -->|No| F
    F --> A
    C --> D
    D --> E
    A -->|No steps found| G
```

**Diagram: Command Step Detection Algorithm**

**Sources:** [.github/actions/workflow-results/parse-job-times.py:94-108]()

---

## Output Format

### job_times.json Structure

The script produces `results/job_times.json` with job IDs as keys and timing data as values:

```json
{
  "job_id_12345": {
    "name": "pull_request / linux-gcc12-cuda12.2-x86_64-test",
    "started_at": "2024-05-09T06:52:20Z",
    "completed_at": "2024-05-09T07:15:40Z",
    "started_epoch_secs": 1715238740.0,
    "completed_epoch_secs": 1715240140.0,
    "job_duration": "0:23:20",
    "job_seconds": 1400.0,
    "command_duration": "0:18:45",
    "command_seconds": 1125.0
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full GitHub Actions job name |
| `started_at` | string | ISO 8601 start timestamp |
| `completed_at` | string | ISO 8601 completion timestamp |
| `started_epoch_secs` | float | Unix epoch seconds (start) |
| `completed_epoch_secs` | float | Unix epoch seconds (completion) |
| `job_duration` | string | Human-readable total duration (H:MM:SS) |
| `job_seconds` | float | Total job duration in seconds |
| `command_duration` | string | Human-readable command duration (H:MM:SS) |
| `command_seconds` | float | Command execution duration in seconds |

**Sources:** [.github/actions/workflow-results/parse-job-times.py:85-108](), [.github/actions/workflow-results/parse-job-times.py:110-111]()

---

## Console Reporting

The script outputs two diagnostic reports to the GitHub Actions console using `::group::` annotations for collapsible display.

### Unmapped Jobs Report

Lists any jobs from `jobs.json` that could not be mapped to a job ID in `workflow.json`. This typically indicates:
- Jobs from other workflows in the same run
- Infrastructure jobs (e.g., workflow-build, workflow-results)
- Malformed job names

```mermaid
graph LR
    A["Filter jobs"]
    B["unknown_jobs = not in job_id_map"]
    C["jobs = in job_id_map"]
    D["Print ::group::Unmapped jobs"]
    E["Print job names"]
    F["Print ::endgroup::"]
    
    A --> B
    A --> C
    B --> D
    D --> E
    E --> F
```

**Diagram: Unmapped Jobs Processing**

**Sources:** [.github/actions/workflow-results/parse-job-times.py:64-115]()

### Job Times Report

Displays timing information in tabular format with overhead calculation:

```
Job        Command    Overhead   Name
---------- ---------- ---------- ----------
0:23:20    0:18:45    25         pull_request / linux-gcc12-cuda12.2-x86_64-test
0:15:30    0:12:00    29         pull_request / windows-msvc-cuda12.2-test
```

**Overhead Calculation:**
```
overhead = (job_seconds - command_seconds) * 100 / command_seconds
```

If `command_seconds` is zero (command step not found), overhead is set to 100% as a sentinel value.

**Sources:** [.github/actions/workflow-results/parse-job-times.py:117-125]()

---

## Integration with Results Pipeline

The `parse-job-times.py` script is invoked by the `workflow-results` action as the first data processing step. Its output (`job_times.json`) is consumed by subsequent analysis scripts:

```mermaid
graph LR
    A["workflow-results action"]
    B["parse-job-times.py"]
    C["job_times.json"]
    D["prepare-execution-summary.py"]
    E["final-summary.py"]
    
    A -->|Invokes| B
    B -->|Produces| C
    C -->|Consumed by| D
    C -->|Consumed by| E
```

**Diagram: Results Pipeline Integration**

The timing data enables:
- Per-project aggregation of execution times (see [Execution Summary Generation](#6.3))
- Identification of slow jobs requiring optimization
- Historical trending of build/test performance
- Overhead analysis for infrastructure improvements

**Sources:** [.github/actions/workflow-results/parse-job-times.py:1-130]()

---

# Page: Execution Summary Generation

# Execution Summary Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-results/prepare-execution-summary.py](.github/actions/workflow-results/prepare-execution-summary.py)

</details>



## Purpose and Scope

This document explains the execution summary generation subsystem, implemented in `prepare-execution-summary.py`, which transforms raw job data and timing information into hierarchical, human-readable summaries organized by project, tag, and value. The system calculates pass rates, timing statistics, sccache hit rates, and identifies likely culprits for failures.

For information about collecting timing data from GitHub Actions API, see [Job Timing Analysis](#6.2). For information about assembling these summaries into final reports for display, see [Final Summary and Reporting](#6.4).

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:1-366]()

## System Overview

The execution summary generator is a Python script that aggregates job results into a three-level hierarchy: **projects** → **tags** → **values**. Each level accumulates pass/fail counts, execution times, and sccache statistics. The system implements intelligent failure analysis that ranks tags to surface likely culprits—specific tag values that account for all failures in a dimension.

### Pipeline Diagram

```mermaid
graph TB
    subgraph "Inputs"
        WorkflowJSON["workflow.json<br/>(job definitions)"]
        JobTimesJSON["job_times.json<br/>(timing data)"]
        SuccessMarkers["jobs/{id}/success<br/>(marker files)"]
        SccacheStats["jobs/{id}/sccache_stats.json<br/>(cache statistics)"]
    end
    
    subgraph "prepare-execution-summary.py"
        ExtractJobs["extract_jobs()<br/>Flatten standalone/two-stage"]
        BuildSummary["build_summary()<br/>Hierarchical aggregation"]
        UpdateEntry["update_summary_entry()<br/>Accumulate statistics"]
        GetSccache["get_sccache_stats()<br/>Cached retrieval"]
        RankTags["rank_tag()<br/>Sort by failure pattern"]
        FormatStats["get_summary_stats()<br/>Format percentages/times"]
        GenerateHeading["get_summary_heading()<br/>Overall status"]
        GenerateProject["write_project_summary()<br/>Per-project output"]
    end
    
    subgraph "Outputs"
        HeadingTxt["execution/heading.txt<br/>Overall summary line"]
        ProjectSummaries["execution/projects/<br/>{idx}_{project}_summary.json"]
    end
    
    WorkflowJSON --> ExtractJobs
    ExtractJobs --> BuildSummary
    SuccessMarkers --> UpdateEntry
    JobTimesJSON --> UpdateEntry
    SccacheStats --> GetSccache
    GetSccache --> UpdateEntry
    UpdateEntry --> BuildSummary
    BuildSummary --> RankTags
    BuildSummary --> FormatStats
    FormatStats --> GenerateHeading
    FormatStats --> GenerateProject
    GenerateHeading --> HeadingTxt
    GenerateProject --> ProjectSummaries
    
    style WorkflowJSON fill:#e1f5ff
    style JobTimesJSON fill:#e1f5ff
    style HeadingTxt fill:#e1ffe1
    style ProjectSummaries fill:#e1ffe1
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:34-44](), [.github/actions/workflow-results/prepare-execution-summary.py:102-162](), [.github/actions/workflow-results/prepare-execution-summary.py:328-344]()

## Data Structures

### Summary Hierarchy

The system builds a nested dictionary structure with three levels of aggregation:

```mermaid
graph TB
    Root["summary<br/>{passed, failed, job_time, sccache}"]
    Projects["projects: {project_name: {...}}"]
    Project["project_name<br/>{passed, failed, job_time, sccache, tags}"]
    Tags["tags: {tag_name: {...}}"]
    Tag["tag_name<br/>{passed, failed, job_time, sccache, values}"]
    Values["values: {value_string: {...}}"]
    Value["value_string<br/>{passed, failed, job_time, sccache}"]
    
    Root --> Projects
    Projects --> Project
    Project --> Tags
    Tags --> Tag
    Tag --> Values
    Values --> Value
    
    Note1["Each level accumulates:<br/>- passed/failed counts<br/>- job_time/command_time<br/>- max_job_time<br/>- sccache requests/hits"]
    
    Note1 -.-> Root
    Note1 -.-> Project
    Note1 -.-> Tag
    Note1 -.-> Value
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:102-138]()

### Entry Statistics Schema

Each node in the hierarchy contains these fields:

| Field | Type | Description |
|-------|------|-------------|
| `passed` | `int` | Number of jobs that succeeded |
| `failed` | `int` | Number of jobs that failed |
| `job_time` | `float` | Total wall-clock time for all jobs (seconds) |
| `command_time` | `float` | Total command execution time (seconds) |
| `max_job_time` | `float` | Maximum single job duration (seconds) |
| `sccache.requests` | `int` | Total compilation requests |
| `sccache.hits` | `int` | Total cache hits |

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:55-98]()

## Job Extraction

The `extract_jobs()` function flattens the workflow structure to produce a single list of jobs, handling both standalone and two-stage patterns:

```mermaid
graph LR
    subgraph "workflow.json Structure"
        GroupName["group_name"]
        Standalone["standalone: [job, job, ...]"]
        TwoStage["two_stage: [{producers, consumers}, ...]"]
        Producers["producers: [job, ...]"]
        Consumers["consumers: [job, ...]"]
    end
    
    subgraph "extract_jobs() Logic"
        Iterate["Iterate groups"]
        CheckStandalone["Check 'standalone' key"]
        CheckTwoStage["Check 'two_stage' key"]
        ExtractProducers["Extract producers"]
        ExtractConsumers["Extract consumers"]
        Combine["Combine all jobs"]
    end
    
    subgraph "Output"
        FlatList["Flat list of all jobs"]
    end
    
    GroupName --> Iterate
    Iterate --> CheckStandalone
    Iterate --> CheckTwoStage
    CheckStandalone --> Standalone
    CheckTwoStage --> TwoStage
    TwoStage --> Producers
    TwoStage --> Consumers
    Standalone --> Combine
    Producers --> ExtractProducers
    Consumers --> ExtractConsumers
    ExtractProducers --> Combine
    ExtractConsumers --> Combine
    Combine --> FlatList
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:34-43]()

## Statistics Accumulation

### Job Success Detection

The `job_succeeded()` function determines whether a job passed by checking for a success marker file:

```python
# Returns True if jobs/{job_id}/success exists
job_succeeded(job)  # Line 12-14
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:12-14]()

### Update Algorithm

The `update_summary_entry()` function accumulates statistics into a summary entry:

```mermaid
graph TB
    Start["update_summary_entry(entry, job, job_times)"]
    InitCounters["Initialize passed/failed counters"]
    CheckSuccess["job_succeeded(job)"]
    IncrPassed["entry['passed'] += 1"]
    IncrFailed["entry['failed'] += 1"]
    CheckTiming["job_times available?"]
    AddTiming["Add job_time, command_time<br/>Update max_job_time"]
    GetSccache["get_sccache_stats(job['id'])"]
    CheckSccache["sccache data available?"]
    AddSccache["Add requests and hits<br/>from cache_hits.counts"]
    Return["Return updated entry"]
    
    Start --> InitCounters
    InitCounters --> CheckSuccess
    CheckSuccess -->|True| IncrPassed
    CheckSuccess -->|False| IncrFailed
    IncrPassed --> CheckTiming
    IncrFailed --> CheckTiming
    CheckTiming -->|Yes| AddTiming
    CheckTiming -->|No| GetSccache
    AddTiming --> GetSccache
    GetSccache --> CheckSccache
    CheckSccache -->|Yes| AddSccache
    CheckSccache -->|No| Return
    AddSccache --> Return
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:55-99]()

### Sccache Statistics

The system retrieves and caches sccache statistics using an LRU cache decorator:

```python
@functools.lru_cache(maxsize=None)
def get_sccache_stats(job_id)
```

The function reads `jobs/{job_id}/sccache_stats.json` and extracts:
- Total `compile_requests`
- Sum of hits across all languages in `cache_hits.counts`

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:46-52](), [.github/actions/workflow-results/prepare-execution-summary.py:82-97]()

## Hierarchical Aggregation

### Build Summary Process

The `build_summary()` function constructs the three-level hierarchy:

```mermaid
graph TB
    Start["build_summary(jobs, job_times)"]
    InitSummary["summary = {projects: {}}"]
    LoopJobs["For each job"]
    UpdateRoot["update_summary_entry(summary, job)"]
    GetMatrixJob["matrix_job = job['origin']['matrix_job']"]
    GetProject["project = matrix_job['project']"]
    InitProject["Initialize projects[project]"]
    UpdateProject["update_summary_entry(projects[project], job)"]
    LoopTags["For each tag in matrix_job<br/>(skip 'project')"]
    InitTag["Initialize tags[tag]"]
    UpdateTag["update_summary_entry(tags[tag], job)"]
    GetValue["value = str(matrix_job[tag])"]
    InitValue["Initialize values[value]"]
    UpdateValue["update_summary_entry(values[value], job)"]
    NaturalSort["Natural sort values by key"]
    RankTags["Sort tags by rank_tag()"]
    Return["Return summary"]
    
    Start --> InitSummary
    InitSummary --> LoopJobs
    LoopJobs --> UpdateRoot
    UpdateRoot --> GetMatrixJob
    GetMatrixJob --> GetProject
    GetProject --> InitProject
    InitProject --> UpdateProject
    UpdateProject --> LoopTags
    LoopTags --> InitTag
    InitTag --> UpdateTag
    UpdateTag --> GetValue
    GetValue --> InitValue
    InitValue --> UpdateValue
    UpdateValue --> LoopTags
    LoopTags -->|Done| NaturalSort
    NaturalSort --> RankTags
    RankTags --> Return
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:102-162]()

### Natural Sorting

Values within each tag are sorted using natural sort, which correctly handles embedded numbers:

```python
def natural_sort_key(key):
    return [(int(text) if text.isdigit() else text.lower()) 
            for text in re.split('(\d+)', key)]
```

Examples:
- `["gcc10", "gcc11", "gcc9"]` → `["gcc9", "gcc10", "gcc11"]`
- `["11", "17", "20"]` → `["11", "17", "20"]`

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:17-19](), [.github/actions/workflow-results/prepare-execution-summary.py:137-138]()

## Likely Culprit Detection

### Tag Ranking Algorithm

The `rank_tag()` function assigns a priority rank to each tag based on failure patterns:

| Rank | Condition | Description | Priority |
|------|-----------|-------------|----------|
| 0 | Multiple values, exactly 1 failing | **Likely culprit**: One value causes all failures | Highest |
| 1 | Multiple values, some failing | Mixed results suggest interaction effects | High |
| 2 | Single value, all failing | Entire dimension failed | Medium |
| 3 | No failures | All passed | Lowest |

```mermaid
graph TB
    Start["rank_tag(tag_summary)"]
    GetCounts["tag_failures = tag_summary['failed']<br/>num_values = len(values)<br/>num_failing_values = count(failed > 0)"]
    CheckMultiple{"num_values > 1?"}
    CheckOne{"num_failing_values == 1?"}
    Rank0["Return 0<br/>(Likely culprit)"]
    CheckSome{"0 < num_failing_values<br/>< num_values?"}
    Rank1["Return 1<br/>(Mixed results)"]
    CheckFailed{"tag_failures > 0?"}
    Rank2["Return 2<br/>(All failed)"]
    Rank3["Return 3<br/>(All passed)"]
    
    Start --> GetCounts
    GetCounts --> CheckMultiple
    CheckMultiple -->|Yes| CheckOne
    CheckMultiple -->|No| CheckFailed
    CheckOne -->|Yes| Rank0
    CheckOne -->|No| CheckSome
    CheckSome -->|Yes| Rank1
    CheckSome -->|No| CheckFailed
    CheckFailed -->|Yes| Rank2
    CheckFailed -->|No| Rank3
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:145-160]()

### Culprit Identification Logic

Within each tag, the system identifies suspicious values:

```mermaid
graph TB
    Start["For tag with failures"]
    CheckMultiple{"Multiple values?"}
    LoopValues["For each value in tag"]
    CheckMatch{"value.failed ==<br/>tag.failed?"}
    MarkSuspicious["Mark value as suspicious"]
    CheckPassed{"suspicious.passed == 0?"}
    MarkCulprit["Mark as likely culprit 🚨"]
    MarkInvestigate["Mark for investigation 🔍"]
    NoAction["No special marking"]
    
    Start --> CheckMultiple
    CheckMultiple -->|No| NoAction
    CheckMultiple -->|Yes| LoopValues
    LoopValues --> CheckMatch
    CheckMatch -->|Yes| MarkSuspicious
    CheckMatch -->|No| LoopValues
    MarkSuspicious --> CheckPassed
    CheckPassed -->|Yes| MarkCulprit
    CheckPassed -->|No| MarkInvestigate
```

A value is a **likely culprit** if:
1. The tag has multiple values
2. The value's failure count equals the tag's total failure count
3. The value has zero passing jobs

A value is **suspicious** if conditions 1 and 2 are met but some jobs passed.

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:254-264](), [.github/actions/workflow-results/prepare-execution-summary.py:291-295]()

## Formatting and Display

### Summary Statistics Formatting

The `get_summary_stats()` function generates a compact statistics line:

**Format**: `Pass: XXX%/total | Total: HHhMMm | Avg: HHhMMm | Max: HHhMMm | Hits: XXX%/requests`

```mermaid
graph LR
    Entry["summary entry"]
    CalcPass["percent = 100 * passed / total"]
    PassStr["Pass: XXX%/total"]
    CheckTime{"job_time<br/>available?"}
    FormatTotal["format_seconds(job_time)"]
    FormatAvg["format_seconds(job_time/total)"]
    FormatMax["format_seconds(max_job_time)"]
    TimeStr["Total/Avg/Max times"]
    CheckSccache{"sccache<br/>available?"}
    CalcHit["hit_percent = 100 * hits / requests"]
    HitStr["Hits: XXX%/requests"]
    Combine["Concatenate all parts"]
    
    Entry --> CalcPass
    CalcPass --> PassStr
    PassStr --> CheckTime
    CheckTime -->|Yes| FormatTotal
    CheckTime -->|No| CheckSccache
    FormatTotal --> FormatAvg
    FormatAvg --> FormatMax
    FormatMax --> TimeStr
    TimeStr --> CheckSccache
    CheckSccache -->|Yes| CalcHit
    CheckSccache -->|No| Combine
    CalcHit --> HitStr
    HitStr --> Combine
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:195-221]()

### Time Formatting

The `format_seconds()` function produces human-readable durations:

| Duration | Format |
|----------|--------|
| < 1 hour | `MMmSSs` |
| 1-23 hours | `HhMMm` |
| ≥ 24 hours | `DdHHh` |

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:179-192]()

### Status Flags

The system uses emoji flags to indicate status at each level:

| Flag | Meaning | Condition |
|------|---------|-----------|
| 🟩 | Success | All jobs passed |
| 🟨 | Partial failure | Some jobs passed, some failed |
| 🟥 | Total failure | No jobs passed |
| 🚨 | Likely culprit | Value responsible for all failures (0% pass rate) |
| 🔍 | Suspicious | Value responsible for all failures (but some passed) |
| 🔥 | High priority | Value marked as likely culprit in value line |

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:228-280](), [.github/actions/workflow-results/prepare-execution-summary.py:294-303]()

## Output Generation

### Overall Heading

The `get_summary_heading()` function creates the top-level summary line:

**Format**: `[flag] CI finished in [walltime]: [stats]`

Walltime is calculated by `get_walltime()`, which finds the earliest start and latest completion across all jobs:

```python
walltime = max(completed_epoch_secs) - min(started_epoch_secs)
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:224-235](), [.github/actions/workflow-results/prepare-execution-summary.py:165-176](), [.github/actions/workflow-results/prepare-execution-summary.py:334]()

### Project Summaries

Each project generates two components written to `execution/projects/{idx:03}_{project}_summary.json`:

```json
{
  "heading": "🟨 libcudacxx: Pass:  85%/234 | Total: 2h34m | Avg: 0m39s | Max: 4m12s | Hits:  78%/45231",
  "body": "```\n🚨 compiler: gcc9 🚨\n  🟩 gcc9              Pass:  45%/67 | ...\n  🔥 gcc10             Pass:   0%/12 | ...\n...\n```"
}
```

The body contains formatted tag and value lines within a code block.

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:319-325]()

### Tag and Value Lines

**Tag Line Format**: `[flag] tag_name[: value flag]`

The tag line includes a note with the suspicious or culprit value name when detected.

**Value Line Format**: `  [flag] value_name [stats]`

Value lines are indented two spaces and include left-aligned value names (padded to 20 characters) followed by statistics.

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:249-280](), [.github/actions/workflow-results/prepare-execution-summary.py:283-306](), [.github/actions/workflow-results/prepare-execution-summary.py:309-316]()

### Project Sorting

Projects are sorted to prioritize failures:

1. Primary sort: Number of failures (descending)
2. Secondary sort: Total number of jobs (descending)

This ensures projects with the most failures appear first in the output.

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:336-344]()

## File Outputs

### Output File Structure

```mermaid
graph TB
    ExecutionDir["execution/"]
    HeadingFile["heading.txt<br/>(single line summary)"]
    ProjectsDir["projects/"]
    Project0["000_libcudacxx_summary.json"]
    Project1["001_thrust_summary.json"]
    ProjectN["00N_project_summary.json"]
    
    ExecutionDir --> HeadingFile
    ExecutionDir --> ProjectsDir
    ProjectsDir --> Project0
    ProjectsDir --> Project1
    ProjectsDir --> ProjectN
    
    HeadingStructure["heading.txt content:<br/>[flag] CI finished in [walltime]: [stats]"]
    ProjectStructure["summary.json structure:<br/>{<br/>  heading: string,<br/>  body: string<br/>}"]
    
    HeadingFile -.-> HeadingStructure
    Project0 -.-> ProjectStructure
```

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:332-334](), [.github/actions/workflow-results/prepare-execution-summary.py:319-325]()

### Output Locations

| File | Purpose | Created By |
|------|---------|------------|
| `execution/heading.txt` | Overall CI status summary | `write_text()` called from `write_workflow_summary()` |
| `execution/projects/{idx:03}_{project}_summary.json` | Per-project detailed summary | `write_project_summary()` for each project |

The directory `execution/projects/` is created if it doesn't exist using `os.makedirs('execution/projects', exist_ok=True)`.

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:23-31](), [.github/actions/workflow-results/prepare-execution-summary.py:332]()

## Integration Points

### Input Dependencies

The script requires two command-line arguments:

```bash
prepare-execution-summary.py workflow.json job_times.json
```

- `workflow.json`: Generated by `build-workflow.py` (see [Workflow Generation](#3))
- `job_times.json`: Generated by `parse-job-times.py` (see [Job Timing Analysis](#6.2))

The job timing file is optional; if unavailable, timing statistics are omitted from the output.

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:347-361]()

### Artifact Dependencies

The script reads job-specific artifacts from the filesystem:

- `jobs/{job_id}/success`: Marker file indicating job success
- `jobs/{job_id}/sccache_stats.json`: Sccache compilation statistics

These artifacts are downloaded by the workflow-results action before this script runs (see [Artifact Collection](#6.1)).

Sources: [.github/actions/workflow-results/prepare-execution-summary.py:12-14](), [.github/actions/workflow-results/prepare-execution-summary.py:46-52]()

### Downstream Consumers

The generated files are consumed by:

- `final-summary.py`: Assembles heading and project summaries into complete reports (see [Final Summary and Reporting](#6.4))
- GitHub Actions workflows: Display in job summaries and PR comments

Sources: See [Final Summary and Reporting](#6.4)

## Example Output

### Heading Example

```
🟨 CI finished in 1h23m: Pass:  87%/456 | Total: 12h45m | Avg: 1m40s | Max: 8m23s | Hits:  82%/123456
```

### Project Summary Example

```json
{
  "heading": "🟨 thrust: Pass:  75%/128 | Total: 3h12m | Avg: 1m30s | Max: 5m45s | Hits:  85%/34567",
  "body": "```\n🚨 compiler: gcc10 🚨\n  🟩 gcc9              Pass: 100%/32 | Total:  48m | Avg: 1m30s | Max: 3m12s | Hits:  90%/8901\n  🔥 gcc10             Pass:   0%/16 | Total:  24m | Avg: 1m30s | Max: 2m45s | Hits:  75%/4567\n  🟩 gcc11             Pass: 100%/32 | Total:  52m | Avg: 1m37s | Max: 3m45s | Hits:  88%/9012\n🟩 ctk\n  🟩 11.1              Pass: 100%/32 | Total:  48m | Avg: 1m30s | Max: 3m12s | Hits:  87%/8901\n  🟨 12.0              Pass:  67%/48 | Total:  72m | Avg: 1m30s | Max: 4m23s | Hits:  83%/12345\n```"
}
```

In this example:
- The `compiler` tag is ranked first (rank 0) because `gcc10` is a likely culprit
- All failures occur with `gcc10`, which has 0% pass rate
- The `ctk` tag is ranked lower because failures are distributed across multiple values

---

# Page: Final Summary and Reporting

# Final Summary and Reporting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-results/final-summary.py](.github/actions/workflow-results/final-summary.py)

</details>



## Purpose and Scope

This document describes the final assembly stage of the results collection pipeline, specifically the `final-summary.py` script that generates the comprehensive HTML/Markdown report displayed to users. This script combines outputs from earlier processing stages into a unified, human-readable summary with collapsible sections.

For information about the artifact collection stage that precedes this, see [Artifact Collection](#6.1). For details on timing analysis, see [Job Timing Analysis](#6.2). For execution summary generation, see [Execution Summary Generation](#6.3). For multi-channel distribution of this final summary, see [Notification System](#6.6).

## System Overview

The `final-summary.py` script serves as the final aggregation point in the results pipeline. It reads structured data files produced by earlier stages and assembles them into a single HTML document with collapsible `<details>` sections. This document is rendered in GitHub's Step Summary UI, posted as PR comments, and sent to Slack channels.

```mermaid
graph TB
    subgraph "Input Files"
        A["execution/heading.txt<br/>Overall summary header"]
        B["execution/projects/*_summary.json<br/>Per-project summaries"]
        C["workflow/override.json<br/>Override matrix config"]
        D["workflow/changes.md<br/>Changed files report"]
        E["workflow/runner_summary.json<br/>Runner allocation stats"]
    end
    
    subgraph "final-summary.py"
        F["read_file()"]
        G["print_json_summary()"]
        H["print_summary_file()"]
        I["print_json_file()"]
        J["print_text_file()"]
        K["main()"]
        
        K --> F
        K --> G
        K --> H
        K --> I
        K --> J
    end
    
    subgraph "Output Stream"
        L["stdout<br/>HTML/Markdown"]
    end
    
    subgraph "Destinations"
        M["GITHUB_STEP_SUMMARY"]
        N["PR Comment"]
        O["Slack Channels"]
    end
    
    A --> K
    B --> K
    C --> I
    D --> J
    E --> H
    
    K --> L
    L --> M
    L --> N
    L --> O
```

**Sources:** [.github/actions/workflow-results/final-summary.py:1-68]()

## Output Format Structure

The generated report uses HTML `<details>` and `<summary>` tags to create collapsible sections, allowing users to drill down into specific projects or skip irrelevant information. The overall structure is:

| Section | Source File | Description |
|---------|------------|-------------|
| Top-level heading | `execution/heading.txt` | Overall pass/fail status and job counts |
| Project summaries | `execution/projects/*_summary.json` | Per-project details in collapsible `<li>` items |
| Override matrix | `workflow/override.json` | Optional override configuration (if present) |
| Changed files | `workflow/changes.md` | Git diff report (if present) |
| Runner summary | `workflow/runner_summary.json` | Runner allocation statistics |

The entire report is wrapped in a top-level `<details>` block that uses the heading text as its `<summary>`, making even the overall summary collapsible.

**Sources:** [.github/actions/workflow-results/final-summary.py:41-63]()

## Script Components

### File Reading Functions

The script provides several specialized functions for reading and printing different file formats:

```mermaid
graph LR
    subgraph "File Types"
        A["Plain Text<br/>.txt"]
        B["JSON Summary<br/>_summary.json"]
        C["Raw JSON<br/>.json"]
    end
    
    subgraph "Reader Functions"
        D["read_file()"]
        E["print_text_file()"]
        F["print_json_summary()"]
        G["print_summary_file()"]
        H["print_json_file()"]
    end
    
    A --> D
    D --> E
    
    B --> G
    G --> F
    
    C --> H
```

#### `read_file(filepath)`

Reads a text file and returns its contents with trailing whitespace stripped. Used as a building block by other functions.

**Sources:** [.github/actions/workflow-results/final-summary.py:9-11]()

#### `print_text_file(filepath)`

Prints the contents of a plain text file if it exists, followed by two newlines. Used for `workflow/changes.md`.

**Sources:** [.github/actions/workflow-results/final-summary.py:14-16]()

#### `print_json_summary(summary, heading_level)`

Prints a JSON object containing `heading` and `body` fields as a collapsible HTML section. The `heading_level` parameter (e.g., `3` for `<h3>`) controls the heading tag used in the `<summary>` element. The structure is:

```html
<details><summary><h{level}>{heading}</h{level}></summary>
{body}
</details>
```

**Sources:** [.github/actions/workflow-results/final-summary.py:19-22]()

#### `print_summary_file(filepath, heading_level)`

Loads a JSON file containing `heading` and `body` fields and passes it to `print_json_summary()`. Used for `workflow/runner_summary.json`.

**Sources:** [.github/actions/workflow-results/final-summary.py:25-28]()

#### `print_json_file(filepath, heading)`

Prints a raw JSON file in a code block within a collapsible section. Used for `workflow/override.json` to display the override matrix configuration. The JSON is formatted with 2-space indentation.

**Sources:** [.github/actions/workflow-results/final-summary.py:31-38]()

## Assembly Process

The `main()` function orchestrates the assembly of the final report in a specific order:

```mermaid
sequenceDiagram
    participant M as main()
    participant FS as File System
    participant O as stdout
    
    M->>FS: List execution/projects/
    FS-->>M: *_summary.json files
    
    M->>M: Sort by filename
    M->>FS: Load each JSON file
    FS-->>M: Project summaries
    
    M->>FS: Read execution/heading.txt
    FS-->>M: Overall heading
    
    M->>O: Print top-level <details> tag
    M->>O: Print <ul> with project <li> items
    
    loop For each project
        M->>O: Print project summary (h3)
    end
    
    M->>O: Close </ul>
    
    alt workflow/override.json exists
        M->>O: Print override matrix
    end
    
    alt workflow/changes.md exists
        M->>O: Print changes report
    end
    
    alt workflow/runner_summary.json exists
        M->>O: Print runner summary (h2)
    end
    
    M->>O: Close top-level </details>
```

### Project Summary Collection

The script scans the `execution/projects/` directory for files matching the regex `[0-9]+_.+_summary.json`. These files are named with a numeric prefix that indicates the number of failed jobs (e.g., `0_libcudacxx_summary.json` or `5_thrust_summary.json`), allowing them to be sorted alphabetically to list failing projects first.

**Sources:** [.github/actions/workflow-results/final-summary.py:42-49]()

### Hierarchical Structure Generation

The projects are rendered as an unordered list (`<ul>`) where each project is a list item (`<li>`) containing a collapsible section with heading level 3 (`<h3>`). This creates a visually organized hierarchy:

```
<details><summary>Overall Heading</summary>
  <ul>
    <li>
      <details><summary><h3>Project 1</h3></summary>
        Project 1 body
      </details>
    </li>
    <li>
      <details><summary><h3>Project 2</h3></summary>
        Project 2 body
      </details>
    </li>
  </ul>
</details>
```

**Sources:** [.github/actions/workflow-results/final-summary.py:51-57]()

### Optional Sections

The script conditionally includes additional sections if their source files exist:

1. **Override Matrix** (`workflow/override.json`): Displayed with heading "🛠️ Override Matrix" at heading level 3
2. **Changes Report** (`workflow/changes.md`): Plain text/markdown content from change detection
3. **Runner Summary** (`workflow/runner_summary.json`): Runner allocation statistics at heading level 2

**Sources:** [.github/actions/workflow-results/final-summary.py:59-61]()

## Integration with workflow-results Action

The `final-summary.py` script is invoked by the `workflow-results` composite action as the final step in the results processing pipeline:

```mermaid
graph TB
    subgraph "workflow-results Action Steps"
        A["1. Download Artifacts"]
        B["2. Fetch Job Info"]
        C["3. parse-job-times.py"]
        D["4. prepare-execution-summary.py"]
        E["5. final-summary.py"]
        F["6. verify-job-success.py"]
        
        A --> B
        B --> C
        C --> D
        D --> E
        E --> F
    end
    
    subgraph "Environment Variables"
        G["GITHUB_STEP_SUMMARY"]
        H["github.event.pull_request.number"]
    end
    
    subgraph "Output Targets"
        I["GitHub Step Summary UI"]
        J["PR Comment API"]
        K["Slack Webhook"]
    end
    
    E --> G
    G --> I
    E --> J
    E --> K
```

The action redirects the script's stdout to the `GITHUB_STEP_SUMMARY` file, which GitHub automatically renders in the workflow run UI. The same content is also used for PR comments and Slack notifications by downstream steps in the action.

**Sources:** [.github/actions/workflow-results/final-summary.py:1-68]()

## Output Destinations

The final summary report is distributed to multiple destinations to reach different audiences:

| Destination | Purpose | When Displayed |
|-------------|---------|----------------|
| GitHub Step Summary | Inline workflow UI display | Always |
| PR Comment | Developer feedback on pull requests | When `pr-number` input is provided |
| Slack Log Channel | Team visibility for all runs | Always (if Slack credentials configured) |
| Slack Alert Channel | Urgent failure notifications | Only on workflow failure |

Each destination receives the same HTML content, but may render it differently based on their Markdown/HTML support. GitHub's Step Summary and PR comments support full HTML with collapsible sections, while Slack converts the content to its block format.

For details on how these distributions are configured and executed, see [Notification System](#6.6).

**Sources:** [.github/actions/workflow-results/final-summary.py:1-68]()

## File Path Dependencies

The script expects the following directory structure to be present in the GitHub Actions workspace:

```
workspace/
├── execution/
│   ├── heading.txt              # Required: Overall summary header
│   └── projects/
│       ├── 0_project1_summary.json   # One or more project summaries
│       ├── 0_project2_summary.json
│       └── 5_project3_summary.json
└── workflow/
    ├── override.json            # Optional: Override matrix config
    ├── changes.md               # Optional: Changed files report
    └── runner_summary.json      # Optional: Runner statistics
```

These files are created by the `prepare-execution-summary.py` script (see [Execution Summary Generation](#6.3)) and the `build-workflow.py` script during workflow generation (see [Workflow Generation](#3)).

The script gracefully handles missing optional files by checking `os.path.exists()` before attempting to print them. If `execution/heading.txt` or the `execution/projects/` directory is missing, the script will fail with a Python exception.

**Sources:** [.github/actions/workflow-results/final-summary.py:14-61]()

## Summary JSON Schema

Each project summary JSON file follows the schema produced by `prepare-execution-summary.py`:

```json
{
  "heading": "Project Name (Passed: X/Y)",
  "body": "HTML/Markdown content with tables and collapsible sections"
}
```

The `heading` field contains a concise summary line, while the `body` field contains detailed HTML including:
- Pass/fail statistics tables
- Tag dimension breakdowns (e.g., by GPU, CUDA version, compiler)
- Likely culprit analysis
- sccache statistics
- Individual job failure details

**Sources:** [.github/actions/workflow-results/final-summary.py:19-28]()

---

# Page: Success Verification

# Success Verification

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-results/verify-job-success.py](.github/actions/workflow-results/verify-job-success.py)

</details>



## Purpose and Scope

This document describes the success verification subsystem, which determines the overall success or failure status of a workflow run by checking for the presence of success marker artifacts produced by individual jobs. This subsystem is part of the broader results collection pipeline and produces the final boolean output that determines workflow status.

For information about artifact collection mechanics, see [Artifact Collection](#6.1). For information about how the success status is incorporated into notifications, see [Notification System](#6.6). For details on final summary generation, see [Final Summary and Reporting](#6.4).

---

## Success Marker System

Each job that executes in the workflow produces a success marker artifact if and only if it completes successfully. This marker is a simple empty file located at a predictable path within the artifact structure.

### Marker File Convention

```
jobs/{job_id}/success
```

The presence of this file indicates successful job completion. The file has no contents—its existence is the signal. Jobs create this marker as the final step in their execution, after all commands have completed successfully.

**Sources:** [.github/actions/workflow-results/verify-job-success.py:19]()

### Job ID Mapping

The verification process uses a job ID mapping file that associates numeric job IDs with human-readable job names. This mapping is generated during the workflow generation phase and provides the complete list of jobs that should have executed.

The mapping has the structure:
```json
{
  "job_id_1": "job_name_1",
  "job_id_2": "job_name_2"
}
```

**Sources:** [.github/actions/workflow-results/verify-job-success.py:14]()

---

## Verification Process

### Script Overview

The success verification is performed by `verify-job-success.py`, a Python script that implements a simple but critical check: for every job that was supposed to run, verify that its success marker exists.

```mermaid
graph TB
    Input["job_ids.json"]
    Script["verify-job-success.py"]
    ArtifactDir["jobs/ directory<br/>(downloaded artifacts)"]
    
    Check1["Check jobs/job_id_1/success"]
    Check2["Check jobs/job_id_2/success"]
    CheckN["Check jobs/job_id_N/success"]
    
    Success["All markers found<br/>Exit code 0"]
    Failure["Missing markers<br/>Exit code 1"]
    
    Input --> Script
    ArtifactDir --> Script
    Script --> Check1
    Script --> Check2
    Script --> CheckN
    
    Check1 --> Success
    Check2 --> Success
    CheckN --> Success
    
    Check1 -.->|"marker missing"| Failure
    Check2 -.->|"marker missing"| Failure
    CheckN -.->|"marker missing"| Failure
```

**Diagram: verify-job-success.py Execution Flow**

**Sources:** [.github/actions/workflow-results/verify-job-success.py:1-31]()

### Command-Line Interface

The script accepts a single positional argument:

| Argument | Type | Description |
|----------|------|-------------|
| `job_id_map` | file path | Path to JSON file containing job ID to job name mappings |

Example invocation:
```bash
./verify-job-success.py job_ids.json
```

**Sources:** [.github/actions/workflow-results/verify-job-success.py:10-12]()

### Verification Algorithm

The verification algorithm is straightforward:

1. **Load job ID mapping**: Parse the JSON file to obtain the complete list of jobs that should have executed [.github/actions/workflow-results/verify-job-success.py:14]()

2. **Initialize success flag**: Start with `success = True` [.github/actions/workflow-results/verify-job-success.py:17]()

3. **Iterate through jobs**: For each job ID in the mapping [.github/actions/workflow-results/verify-job-success.py:18]():
   - Construct the expected success marker path: `jobs/{job_id}/success` [.github/actions/workflow-results/verify-job-success.py:19]()
   - Print verification message with job ID and name [.github/actions/workflow-results/verify-job-success.py:20]()
   - Check if the success marker file exists [.github/actions/workflow-results/verify-job-success.py:21]()
   - If missing, print failure message and set `success = False` [.github/actions/workflow-results/verify-job-success.py:22-23]()

4. **Exit with status**: If any markers are missing, exit with code 1; otherwise exit with code 0 [.github/actions/workflow-results/verify-job-success.py:25-26]()

**Sources:** [.github/actions/workflow-results/verify-job-success.py:9-31]()

### Output Format

The script produces console output for each job verification:

**Success case:**
```
Verifying job with id "12345": "libcudacxx-build-gcc12-cuda12.0"
```

**Failure case:**
```
Verifying job with id "12345": "libcudacxx-build-gcc12-cuda12.0"
Failed: Artifact "jobs/12345/success" not found
```

This output appears in the workflow-results action logs and helps identify which specific jobs failed.

**Sources:** [.github/actions/workflow-results/verify-job-success.py:20-22]()

---

## Integration with workflow-results Action

### Action Orchestration

The `verify-job-success.py` script is invoked as part of the `workflow-results` composite action. This action orchestrates multiple result processing steps in sequence.

```mermaid
graph TB
    subgraph "workflow-results Action"
        Download["Download all job artifacts"]
        ParseTimes["parse-job-times.py<br/>(timing analysis)"]
        PrepareExec["prepare-execution-summary.py<br/>(hierarchical aggregation)"]
        FinalSum["final-summary.py<br/>(report generation)"]
        VerifySuccess["verify-job-success.py<br/>(success verification)"]
    end
    
    subgraph "Outputs"
        StepSummary["GITHUB_STEP_SUMMARY"]
        PRComment["PR Comment"]
        SlackLog["Slack Log Channel"]
        SuccessOutput["SUCCESS output<br/>(true/false)"]
    end
    
    Download --> ParseTimes
    ParseTimes --> PrepareExec
    PrepareExec --> FinalSum
    FinalSum --> StepSummary
    FinalSum --> PRComment
    FinalSum --> SlackLog
    
    Download --> VerifySuccess
    VerifySuccess --> SuccessOutput
    SuccessOutput -.->|"if false"| SlackAlert["Slack Alert Channel"]
```

**Diagram: workflow-results Action Data Flow**

**Sources:** [.github/actions/workflow-results/verify-job-success.py:1-31]()

### Conditional Execution Pattern

The success verification step typically uses `continue-on-error: true` in the action configuration, allowing the verification to fail without preventing subsequent reporting steps from executing. This ensures that even when jobs fail, developers receive comprehensive summary reports with information about which jobs failed and why.

The verification script's exit code is captured separately and converted to a boolean output that can be consumed by subsequent workflow steps, typically to:
1. Determine whether to post to the Slack alert channel (failures only)
2. Set the overall workflow status (success vs failure)
3. Provide a machine-readable signal for automation tools

---

## Failure Scenarios

### Missing Success Markers

The most common failure scenario occurs when one or more jobs fail to complete successfully. Failed jobs do not create success marker artifacts, causing the verification script to detect their absence.

| Scenario | Cause | Verification Result |
|----------|-------|---------------------|
| Job command fails | Non-zero exit code in job execution | Marker not created, verification fails |
| Job times out | GitHub Actions timeout exceeded | Marker not created, verification fails |
| Job cancelled | Manual cancellation or dependency failure | Marker not created, verification fails |
| Artifact upload fails | GitHub API error during upload | Marker exists locally but not in artifacts, verification fails |
| Job skipped | Conditional logic skipped job execution | Job not in job_id_map, verification unaffected |

**Sources:** [.github/actions/workflow-results/verify-job-success.py:21-23]()

### Partial Workflow Execution

In some cases, a workflow may experience partial execution due to infrastructure issues, resource constraints, or GitHub Actions platform problems. The verification script detects these scenarios by comparing the expected job list (from job_ids.json) against the actual artifacts present.

### Non-Failure Early Termination

If a job completes all required steps but is marked as skipped or cancelled through GitHub Actions conditionals (e.g., `if:` expressions), it may not appear in the job_id_map at all. This is distinct from a failure—the verification script only checks jobs that were supposed to execute.

---

## Exit Code Contract

The script follows standard Unix conventions for exit codes:

| Exit Code | Meaning | Workflow Behavior |
|-----------|---------|-------------------|
| 0 | All jobs have success markers | Workflow considered successful |
| 1 | One or more jobs missing success markers | Workflow considered failed |

This exit code is typically captured and transformed into a boolean output by the workflow-results action:
- Exit code 0 → `SUCCESS=true`
- Exit code 1 → `SUCCESS=false`

The boolean output is then available to subsequent steps for conditional logic, such as posting to alert channels or setting final workflow status.

**Sources:** [.github/actions/workflow-results/verify-job-success.py:25-26]()

---

## Relationship to Other Verification Mechanisms

### Comparison with Job Status API

The verify-job-success.py script provides artifact-based verification, which is independent of GitHub Actions' job status API. This dual verification approach provides defense-in-depth:

1. **API-based status**: GitHub Actions reports job conclusions (success, failure, cancelled) through its API
2. **Artifact-based status**: Jobs explicitly signal success by creating marker files

The artifact-based approach is more reliable for detecting certain failure modes, such as:
- Jobs that appear successful in GitHub UI but failed to produce expected outputs
- Jobs where artifact upload succeeded but execution failed
- Jobs where final cleanup steps were skipped

### Interaction with Execution Summary

While `verify-job-success.py` provides a binary success/failure determination, the execution summary (see [Execution Summary Generation](#6.3)) provides detailed breakdowns of which specific job dimensions contributed to failures. The two mechanisms serve complementary purposes:

- **verify-job-success.py**: Authoritative success/failure determination for workflow status
- **prepare-execution-summary.py**: Diagnostic information about failure patterns and likely culprits

**Sources:** [.github/actions/workflow-results/verify-job-success.py:1-31]()

---

# Page: Notification System

# Notification System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/actions/workflow-results/action.yml](.github/actions/workflow-results/action.yml)

</details>



## Purpose and Scope

This document describes the notification system that delivers workflow status and results to multiple channels: Slack (log and alert channels), GitHub Pull Request comments, and GitHub Step Summary. The system provides real-time feedback on workflow execution, allowing teams to monitor CI/CD progress and quickly respond to failures.

For details on how execution summaries and timing data are generated, see [Execution Summary Generation](#6.3) and [Final Summary and Reporting](#6.4). For artifact collection mechanics, see [Artifact Collection](#6.1).

---

## Notification Channels Overview

The system delivers notifications through three primary channels, each serving different audiences and use cases:

| Channel | Audience | Trigger | Content |
|---------|----------|---------|---------|
| **Slack Log** | Team members, CI monitors | Always sent (start and completion) | Verbose details, execution summary, job statistics |
| **Slack Alert** | On-call engineers, maintainers | Failures only | Condensed error information, execution summary |
| **GitHub PR Comment** | PR authors, reviewers | PR workflows only | Comprehensive results with collapsible sections |
| **GitHub Step Summary** | Workflow viewers | Always generated | Same as PR comment, rendered in Actions UI |

Sources: [.github/actions/workflow-build/action.yml:1-140](), [.github/actions/workflow-results/action.yml:1-213]()

---

## Notification Architecture

The following diagram shows when and where notifications are sent throughout the workflow lifecycle:

**Diagram: Notification Flow Through Workflow Phases**

```mermaid
graph TB
    subgraph "Workflow Start Phase"
        BuildAction["workflow-build Action"]
        StartNotif["Slack Log Notification<br/>'Workflow starting...'"]
        BuildError["Build Error Detection"]
        ErrorNotif["Slack Error Notification<br/>(log + alert channels)"]
        
        BuildAction --> StartNotif
        BuildAction --> BuildError
        BuildError -->|"failure()"| ErrorNotif
    end
    
    subgraph "Execution Phase"
        Jobs["Job Execution<br/>(dispatch + run)"]
        Artifacts["Artifact Collection"]
        
        Jobs --> Artifacts
    end
    
    subgraph "Results Phase"
        ResultsAction["workflow-results Action"]
        ParseResults["Parse Results<br/>+ Generate Summary"]
        CheckSuccess["verify-job-success.py"]
        
        Artifacts --> ResultsAction
        ResultsAction --> ParseResults
        ParseResults --> CheckSuccess
    end
    
    subgraph "Final Notifications"
        PRComment["GitHub PR Comment"]
        StepSummary["GitHub Step Summary"]
        SlackLog["Slack Log Notification<br/>'Workflow finished...'"]
        SlackAlert["Slack Alert Notification<br/>(failures only)"]
        
        CheckSuccess --> PRComment
        CheckSuccess --> StepSummary
        CheckSuccess -->|"always()"| SlackLog
        CheckSuccess -->|"failure()"| SlackAlert
    end
    
    StartNotif -.->|"includes"| WorkflowLink["GitHub Actions Run URL"]
    ErrorNotif -.->|"includes"| WorkflowLink
    SlackLog -.->|"includes"| ExecSummary["Execution Summary Text"]
    SlackAlert -.->|"includes"| ExecSummary
    PRComment -.->|"includes"| FullSummary["Full HTML/Markdown Report"]
    StepSummary -.->|"includes"| FullSummary
```

Sources: [.github/actions/workflow-build/action.yml:47-139](), [.github/actions/workflow-results/action.yml:179-212]()

---

## Slack Integration

### Configuration Inputs

The Slack integration requires three inputs to function:

| Input | Purpose | Required |
|-------|---------|----------|
| `slack_token` | Bot token for authentication (`SLACK_BOT_TOKEN`) | Yes for any Slack notifications |
| `slack_log` | Channel ID for verbose notifications | Optional |
| `slack_alert` | Channel ID for critical alerts | Optional |

Both `workflow-build` and `workflow-results` actions accept these inputs identically. Notifications are skipped entirely if `slack_token` is empty.

Sources: [.github/actions/workflow-build/action.yml:28-36](), [.github/actions/workflow-results/action.yml:11-19]()

### Notification Timing and Conditions

**Diagram: Slack Notification Decision Logic**

```mermaid
graph TB
    subgraph "workflow-build Action"
        Build_Start{{"slack_token != ''<br/>AND slack_log != ''"}}
        Build_StartMsg["Send to slack_log:<br/>'Workflow starting...'"]
        
        Build_Error{{"failure() AND slack_token != ''<br/>AND (slack_alert OR slack_log)"}}
        Build_ErrorMsg["Send to channels:<br/>'Error while preparing'"]
        
        Build_Start -->|true| Build_StartMsg
        Build_Error -->|true| Build_ErrorMsg
    end
    
    subgraph "workflow-results Action"
        Results_Log{{"always() AND slack_token != ''<br/>AND slack_log != ''"}}
        Results_LogMsg["Send to slack_log:<br/>'Finished with status'"]
        
        Results_Alert{{"failure() AND slack_token != ''<br/>AND slack_alert != ''"}}
        Results_AlertMsg["Send to slack_alert:<br/>'Workflow has failed'"]
        
        Results_Log -->|true| Results_LogMsg
        Results_Alert -->|true| Results_AlertMsg
    end
```

Key behavioral notes:
- **Start notification**: Sent only to `slack_log`, only if both token and channel are provided [.github/actions/workflow-build/action.yml:47-59]()
- **Build error notification**: Sent to both `slack_log` and `slack_alert` if error occurs, channel IDs concatenated with comma separator [.github/actions/workflow-build/action.yml:126-139]()
- **Completion notification**: Always sent to `slack_log` regardless of workflow outcome [.github/actions/workflow-results/action.yml:179-195]()
- **Alert notification**: Sent only to `slack_alert` on failure [.github/actions/workflow-results/action.yml:197-212]()

Sources: [.github/actions/workflow-build/action.yml:47-139](), [.github/actions/workflow-results/action.yml:179-212]()

### Message Content and Format

The Slack messages use the `slackapi/slack-github-action@v1.26.0` action with the following structure:

**Start Notification** ([.github/actions/workflow-build/action.yml:47-59]()):
```
Workflow '[workflow_type]' starting...

Details: [github_actions_url]
```

**Error Notification** ([.github/actions/workflow-build/action.yml:126-139]()):
```
Workflow '[workflow_type]' encountered an error while preparing to run.

Details: [github_actions_url]
```

**Completion Notification** ([.github/actions/workflow-results/action.yml:179-195]()):
```
Workflow '[workflow_type]' has finished with status `[outcome]`:

[execution_summary]

Details: [github_actions_url]
```

**Alert Notification** ([.github/actions/workflow-results/action.yml:197-212]()):
```
Workflow '[workflow_type]' has failed:

[execution_summary]

Details: [github_actions_url]
```

The variables are populated from GitHub Actions context:
- `WORKFLOW_TYPE`: `${{ github.workflow }}` (e.g., "nightly", "weekly", "pr")
- `STATUS`: `${{ steps.check-success.outcome }}` ("success" or "failure")
- `EXEC_SUMMARY`: `${{ steps.final-summary.outputs.EXEC_SUMMARY }}` (from [execution/heading.txt]())
- `SUMMARY_URL`: Constructed as `https://github.com/${{github.repository}}/actions/runs/${{github.run_id}}`

Sources: [.github/actions/workflow-build/action.yml:50-59](), [.github/actions/workflow-results/action.yml:183-212]()

### Channel Selection Strategy

**Diagram: Channel Routing Logic**

```mermaid
graph LR
    subgraph "Build Phase"
        BuildStart["Workflow Start"]
        BuildError["Build Error"]
        
        BuildStart --> LogOnly["slack_log only"]
        BuildError --> BothChannels["slack_log + slack_alert"]
    end
    
    subgraph "Results Phase"
        ResultsSuccess["Success Outcome"]
        ResultsFailure["Failure Outcome"]
        
        ResultsSuccess --> LogAlways["slack_log<br/>(always)"]
        ResultsFailure --> LogAlways2["slack_log<br/>(always)"]
        ResultsFailure --> AlertOnly["slack_alert<br/>(failure only)"]
    end
```

The error notification in `workflow-build` uses a dynamic channel ID construction [.github/actions/workflow-build/action.yml:133-135]():
```yaml
CHANNEL_SEP: ${{ (inputs.slack_log != '' && inputs.slack_alert != '') && ',' || ''}}
# ...
channel-id: '${{ inputs.slack_log }}${{env.CHANNEL_SEP}}${{ inputs.slack_alert }}'
```

This concatenates both channels with a comma separator if both are provided, ensuring the error reaches maximum visibility.

Sources: [.github/actions/workflow-build/action.yml:133-135](), [.github/actions/workflow-results/action.yml:189-206]()

---

## GitHub PR Comments

### Comment Generation and Posting

PR comments are posted via the `actions/github-script@v7` action, which uses the GitHub REST API to create issue comments. The comment is only posted when all of the following conditions are met:

1. Workflow is not cancelled: `${{ !cancelled() }}`
2. PR number is provided: `inputs.pr_number != ''`
3. GitHub token is provided: `inputs.github_token != ''`

[.github/actions/workflow-results/action.yml:130-153]()

**Diagram: PR Comment Data Flow**

```mermaid
graph TB
    FinalSummary["final-summary.py"]
    URLEncode["URL Encoding<br/>(Python urllib.parse.quote)"]
    GHAOutput["GITHUB_OUTPUT<br/>SUMMARY variable"]
    ScriptEnv["Environment Variable<br/>COMMENT_BODY"]
    URLDecode["URL Decoding<br/>(decodeURIComponent)"]
    APICall["GitHub REST API<br/>issues.createComment"]
    
    FinalSummary -->|"final_summary.md"| URLEncode
    URLEncode -->|"url_encode_string()"| GHAOutput
    GHAOutput -->|"steps.final-summary.outputs.SUMMARY"| ScriptEnv
    ScriptEnv -->|"process.env.COMMENT_BODY"| URLDecode
    URLDecode --> APICall
    
    APICall -->|"Parameters"| Params["owner: context.repo.owner<br/>repo: context.repo.repo<br/>issue_number: PR_NUMBER<br/>body: decoded comment"]
```

The URL encoding/decoding mechanism handles multiline strings and special characters that would otherwise break GitHub Actions output passing [.github/actions/workflow-results/action.yml:116-122]():

```yaml
url_encode_string() {
  python3 -c "import sys; from urllib.parse import quote; print(quote(sys.stdin.read()))"
}

printf "SUMMARY=%s\n" "$(cat final_summary.md | url_encode_string)" | tee -a "${GITHUB_OUTPUT}"
```

The JavaScript in the `github-script` action then decodes it [.github/actions/workflow-results/action.yml:144]():
```javascript
const commentBody = decodeURIComponent(process.env.COMMENT_BODY);
```

Sources: [.github/actions/workflow-results/action.yml:106-153]()

### Comment Content

The comment body is identical to the GitHub Step Summary content, generated by `final-summary.py`. This includes:

- Overall workflow status header
- Project-by-project results with pass/fail counts
- Collapsible sections for detailed job information
- Links to individual job logs
- Sccache statistics
- Timing information

For details on summary generation, see [Final Summary and Reporting](#6.4).

Sources: [.github/actions/workflow-results/action.yml:112-128]()

---

## GitHub Step Summary

The GitHub Step Summary is written to the special `GITHUB_STEP_SUMMARY` file, which GitHub Actions automatically renders in the workflow UI [.github/actions/workflow-results/action.yml:128]():

```bash
cp final_summary.md ${GITHUB_STEP_SUMMARY}
```

This occurs in the "Prepare final summary" step, which uses `continue-on-error: true` to ensure partial results are displayed even if summary generation encounters errors [.github/actions/workflow-results/action.yml:106-128]().

The step summary is always generated regardless of:
- Whether PR comments are enabled
- Whether Slack notifications are configured
- Workflow success or failure status

This ensures workflow viewers always have access to results directly in the Actions UI.

Sources: [.github/actions/workflow-results/action.yml:106-128]()

---

## Notification Lifecycle and Error Handling

### Resilience Strategy

The notification system employs defensive programming to maximize information delivery even when components fail:

| Step | Error Handling | Rationale |
|------|----------------|-----------|
| Download job artifacts | `continue-on-error: true` | Some jobs may fail to upload artifacts |
| Clean up job artifacts | `continue-on-error: true` | Line ending conversion may fail on some files |
| Fetch workflow job info | `continue-on-error: true` | GitHub API rate limits or timeouts |
| Parse job times | `continue-on-error: true` | Missing or malformed timing data |
| Prepare execution summary | `continue-on-error: true` | Partial artifact collection |
| Prepare final summary | `continue-on-error: true` | Missing intermediate data |
| Comment on PR | `continue-on-error: true` | API permissions or rate limits |

[.github/actions/workflow-results/action.yml:37-132]()

The only step that does NOT use `continue-on-error` is "Check for job success" [.github/actions/workflow-results/action.yml:155-177](), which determines the overall workflow outcome and must fail if jobs failed.

**Diagram: Error Handling Flow**

```mermaid
graph TB
    DownloadArtifacts["Download Artifacts<br/>(continue-on-error)"]
    FetchJobInfo["Fetch Job Info<br/>(continue-on-error)"]
    ParseTimes["Parse Times<br/>(continue-on-error)"]
    PrepareExec["Prepare Exec Summary<br/>(continue-on-error)"]
    PrepareFinal["Prepare Final Summary<br/>(continue-on-error)"]
    CommentPR["Comment on PR<br/>(continue-on-error)"]
    CheckSuccess["Check Success<br/>(MUST SUCCEED)"]
    SendLog["Send Slack Log<br/>(always)"]
    SendAlert["Send Slack Alert<br/>(on failure)"]
    
    DownloadArtifacts --> FetchJobInfo
    FetchJobInfo --> ParseTimes
    ParseTimes --> PrepareExec
    PrepareExec --> PrepareFinal
    PrepareFinal --> CommentPR
    CommentPR --> CheckSuccess
    CheckSuccess --> SendLog
    CheckSuccess --> SendAlert
    
    DownloadArtifacts -.->|"partial data"| ParseTimes
    FetchJobInfo -.->|"partial data"| ParseTimes
    ParseTimes -.->|"partial data"| PrepareExec
    PrepareExec -.->|"partial data"| PrepareFinal
```

Sources: [.github/actions/workflow-results/action.yml:30-213]()

### Notification Ordering

Notifications are sent in this specific order:

1. **Workflow start** (Slack log) - First action in `workflow-build` [.github/actions/workflow-build/action.yml:47-59]()
2. **Build errors** (Slack log + alert) - If `workflow-build` fails [.github/actions/workflow-build/action.yml:126-139]()
3. **Job execution** - Jobs run, no notifications
4. **PR comment** - Posted after results are parsed [.github/actions/workflow-results/action.yml:130-153]()
5. **Workflow completion** (Slack log) - Always sent, uses `always()` condition [.github/actions/workflow-results/action.yml:179-195]()
6. **Workflow failure alert** (Slack alert) - Only on failure, uses `failure()` condition [.github/actions/workflow-results/action.yml:197-212]()

This ordering ensures that Slack logs receive a complete notification timeline (start → completion), while PR comments and alerts are sent only after all results are available.

Sources: [.github/actions/workflow-build/action.yml:47-139](), [.github/actions/workflow-results/action.yml:130-212]()

---

## Configuration Reference

### Required Credentials

| Credential | Source | Purpose | Scope |
|------------|--------|---------|-------|
| `SLACK_BOT_TOKEN` | Repository/Organization secret | Authenticate with Slack API | `chat:write` permission for specified channels |
| `GITHUB_TOKEN` | Built-in Actions token or PAT | Post PR comments, fetch job data | `pull-requests: write`, `actions: read` |

The GitHub token is typically provided as `${{ secrets.GITHUB_TOKEN }}`, which has appropriate permissions by default in the workflow's repository.

### Channel ID Format

Slack channel IDs are alphanumeric strings (e.g., `C01234ABCDE`), not channel names. To find a channel ID:

1. Right-click the channel in Slack
2. Select "View channel details"
3. Scroll to bottom, copy the Channel ID

Both `slack_log` and `slack_alert` can point to the same channel if desired, though this reduces alert signal-to-noise ratio.

Sources: [.github/actions/workflow-build/action.yml:28-36](), [.github/actions/workflow-results/action.yml:11-19]()

### Example Workflow Configuration

```yaml
- name: Build workflow
  uses: ./.github/actions/workflow-build
  with:
    workflows: "pull_request"
    slack_token: ${{ secrets.SLACK_BOT_TOKEN }}
    slack_log: "C01234ABCDE"  # #cccl-ci-log channel
    slack_alert: "C56789FGHIJ"  # #cccl-ci-alerts channel

# ... dispatch and execute jobs ...

- name: Collect results
  uses: ./.github/actions/workflow-results
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    pr_number: ${{ github.event.pull_request.number }}
    slack_token: ${{ secrets.SLACK_BOT_TOKEN }}
    slack_log: "C01234ABCDE"
    slack_alert: "C56789FGHIJ"
```

Sources: [.github/actions/workflow-build/action.yml:4-36](), [.github/actions/workflow-results/action.yml:4-19]()

---

## Integration Points

The notification system integrates with other subsystems:

- **Execution Summary Generation** ([#6.3](#6.3)): Provides the `execution/heading.txt` file used in Slack messages
- **Final Summary** ([#6.4](#6.4)): Generates `final_summary.md` used for PR comments and Step Summary
- **Success Verification** ([#6.5](#6.5)): Determines when to send alert notifications
- **Job Timing Analysis** ([#6.2](#6.2)): Provides timing data included in summaries

Sources: [.github/actions/workflow-results/action.yml:92-212]()

---

# Page: Advanced Topics

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)

</details>



This page covers specialized features and integration points designed for advanced users and system maintainers. These topics include intelligent change detection for efficient CI runs, distributed compilation caching via AWS S3, GPU resource management for CUDA workloads, and override matrix mechanisms for workflow customization.

For core workflow generation concepts, see [Workflow Generation](#3). For basic execution environment setup, see [Job Execution](#5). For results collection fundamentals, see [Results and Reporting](#6).

---

## Overview

The cccl-gha system provides four main advanced features:

| Feature | Purpose | Primary Configuration |
|---------|---------|----------------------|
| **Change Detection** | Skip unnecessary jobs when only specific files change | `inspect_changes_script` input |
| **Distributed Compilation Caching** | Accelerate builds via shared sccache on AWS S3 | AWS credentials + `.aws/config` |
| **GPU Resource Management** | Control GPU visibility and allocation for CUDA jobs | `NVIDIA_VISIBLE_DEVICES` + runner naming |
| **Override Matrix** | Replace standard workflow configurations with custom matrix | `allow_override` + override workflow in matrix.yaml |

These features operate at different phases of the workflow lifecycle: change detection occurs during configuration, GPU management during execution, sccache throughout the build process, and override matrix at the generation phase.

---

## Change Detection System

The change detection system performs git diff analysis to determine which projects need testing, allowing entire workflows to be skipped or filtered when irrelevant files change. This significantly reduces compute costs for large pull requests that only modify specific subsystems.

### Detection Workflow

```mermaid
graph TB
    Input["workflow-build inputs"]
    Script["inspect_changes_script<br/>(provided by consumer)"]
    BaseSHA["inspect_changes_base_sha<br/>(base commit)"]
    CurrentSHA["GITHUB_SHA<br/>(current commit)"]
    
    Step["Inspect changes step<br/>[action.yml:61-72]()"]
    DirtyOutput["dirty_projects output<br/>(space-separated list)"]
    ChangesSummary["workflow/changes.md<br/>(GITHUB_STEP_SUMMARY copy)"]
    
    BuildStep["Parse matrix step<br/>[action.yml:74-101]()"]
    DirtyFlag["--dirty-projects flag"]
    BuildPy["build-workflow.py"]
    FilteredJobs["Filtered workflow.json"]
    
    Input --> Script
    Input --> BaseSHA
    CurrentSHA --> Step
    Script --> Step
    BaseSHA --> Step
    
    Step --> DirtyOutput
    Step --> ChangesSummary
    
    DirtyOutput --> BuildStep
    BuildStep --> DirtyFlag
    BuildStep --> BuildPy
    DirtyFlag --> BuildPy
    BuildPy --> FilteredJobs
    
    style Script fill:#f9f9f9
    style FilteredJobs fill:#f9f9f9
```

**Change Detection Flow**

The detection process flows through the `workflow-build` action in two stages. First, if both `inspect_changes_script` and `inspect_changes_base_sha` inputs are provided, the script executes with the base SHA and current SHA as arguments. The script must output a `dirty_projects` variable to `GITHUB_OUTPUT` containing a space-separated list of affected projects.

Sources: [.github/actions/workflow-build/action.yml:61-72]()

### Configuration Interface

The change detection system integrates via three action inputs:

**Input: `inspect_changes_script`**
- Type: String (file path)
- Default: Empty (detection disabled)
- Example: `./ci/inspect-changes.sh`
- Purpose: Script that performs git diff analysis and identifies modified projects

**Input: `inspect_changes_base_sha`**
- Type: String (git SHA)
- Default: Empty
- Example: `${{ github.event.pull_request.base.sha }}`
- Purpose: Base commit reference for diff comparison

The script receives two positional arguments: `${base_ref} ${GITHUB_SHA}` and must produce output suitable for GitHub Actions' output mechanism.

Sources: [.github/actions/workflow-build/action.yml:12-19](), [.github/actions/workflow-build/action.yml:66-69]()

### Integration with Workflow Generation

When change detection is active, the workflow generation step receives modified flags:

```yaml
# Conditional flag generation
dirty_projects_flag: ${{ inputs.inspect_changes_script != '' && '--dirty-projects' || ''}}
dirty_projects: ${{ inputs.inspect_changes_script != '' && steps.inspect-changes.outputs.dirty_projects || ''}}

# build-workflow.py invocation with optional filtering
${{ env.matrix_parser }} ${{ inputs.matrix_file }}
    --workflows ${{ inputs.workflows }}
    ${{ env.dirty_projects_flag }} ${{ env.dirty_projects }}
```

The `--dirty-projects` flag passes the space-separated project list to `build-workflow.py`, which filters the matrix to include only jobs associated with modified projects. If no relevant projects changed, the generated workflow may be empty, avoiding all job execution.

Sources: [.github/actions/workflow-build/action.yml:79-88]()

### Artifacts and Summaries

The inspect changes step creates two outputs:

1. **`dirty_projects` output variable**: Space-separated list consumed by workflow generation
2. **`workflow/changes.md`**: Copy of `GITHUB_STEP_SUMMARY` for archival

The changes summary is uploaded as part of the workflow artifact bundle, providing a historical record of which files triggered testing.

Sources: [.github/actions/workflow-build/action.yml:70-72]()

---

## Distributed Compilation Caching

The system integrates Mozilla's `sccache` tool with AWS S3 to provide shared compilation caching across all CI jobs. This dramatically reduces build times for incremental changes by reusing compilation artifacts from previous runs and parallel jobs.

### AWS S3 Integration Architecture

```mermaid
graph TB
    subgraph "GitHub Actions Runner Host"
        GHA["GitHub Actions Runner"]
        AWSAction["aws-actions/configure-aws-credentials<br/>[action.yml:60-65]()"]
        EnvVars["Environment Variables:<br/>AWS_ACCESS_KEY_ID<br/>AWS_SESSION_TOKEN<br/>AWS_SECRET_ACCESS_KEY"]
    end
    
    subgraph "Intermediate Container (ubuntu-dind)"
        RunStep["Run command step<br/>[action.yml:66-165]()"]
        AWSConfigFile["$RUNNER_TEMP/.aws/config<br/>[action.yml:115-119]()"]
        AWSCredFile["$RUNNER_TEMP/.aws/credentials<br/>[action.yml:121-126]()"]
        VolumeMounts["Volume mount:<br/>--volume $RUNNER_TEMP/.aws:/root/.aws"]
    end
    
    subgraph "DevContainer"
        SccacheClient["sccache binary"]
        CompileCmd["Compilation commands<br/>(CXX=sccache g++)"]
        StatsJSON["sccache_stats.json<br/>(cache hit rates)"]
    end
    
    subgraph "AWS Cloud"
        S3Bucket["S3 Bucket:<br/>rapids-sccache-devs<br/>(us-east-2)"]
    end
    
    GHA --> AWSAction
    AWSAction --> EnvVars
    EnvVars --> RunStep
    RunStep --> AWSConfigFile
    RunStep --> AWSCredFile
    RunStep --> VolumeMounts
    
    VolumeMounts --> SccacheClient
    SccacheClient --> CompileCmd
    SccacheClient <--> S3Bucket
    CompileCmd --> StatsJSON
    
    style S3Bucket fill:#f9f9f9
    style StatsJSON fill:#f9f9f9
```

**Sccache AWS S3 Integration Flow**

The integration uses AWS OIDC authentication to obtain temporary credentials without storing secrets in the repository. The credentials propagate through three layers: GitHub Actions environment variables, intermediate container files, and finally into the devcontainer via volume mounts.

Sources: [.github/actions/workflow-run-job-linux/action.yml:60-65](), [.github/actions/workflow-run-job-linux/action.yml:113-129](), [.github/actions/workflow-run-job-linux/action.yml:162]()

### AWS Credential Configuration

The credential acquisition and propagation occurs in three steps:

**Step 1: OIDC Authentication**

The `aws-actions/configure-aws-credentials@v4` action uses GitHub's OIDC provider to assume an AWS IAM role without requiring long-lived credentials:

```yaml
- name: Get AWS credentials for sccache bucket
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::279114543810:role/gha-oidc-NVIDIA
    aws-region: us-east-2
    role-duration-seconds: 43200 # 12 hours
```

This action sets three environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SESSION_TOKEN`, and `AWS_SECRET_ACCESS_KEY`. The 12-hour duration ensures credentials remain valid for long-running nightly builds.

Sources: [.github/actions/workflow-run-job-linux/action.yml:60-65]()

**Step 2: Environment Variable Capture**

The Run command step explicitly captures these credentials as environment variables to pass them into the intermediate container:

```yaml
env:
  AWS_ACCESS_KEY_ID: "${{env.AWS_ACCESS_KEY_ID}}"
  AWS_SESSION_TOKEN: "${{env.AWS_SESSION_TOKEN}}"
  AWS_SECRET_ACCESS_KEY: "${{env.AWS_SECRET_ACCESS_KEY}}"
```

This explicit capture is necessary because the intermediate container doesn't automatically inherit the runner's environment.

Sources: [.github/actions/workflow-run-job-linux/action.yml:74-76]()

**Step 3: Configuration File Generation**

The intermediate container creates AWS configuration files in the runner's temporary directory:

```bash
# Create config file
cat <<EOF > "$RUNNER_TEMP/.aws/config"
[default]
bucket=rapids-sccache-devs
region=us-east-2
EOF

# Create credentials file
cat <<EOF > "$RUNNER_TEMP/.aws/credentials"
[default]
aws_access_key_id=$AWS_ACCESS_KEY_ID
aws_session_token=$AWS_SESSION_TOKEN
aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
EOF

# Set permissions
chmod 0600 "$RUNNER_TEMP/.aws/credentials"
chmod 0664 "$RUNNER_TEMP/.aws/config"
```

These files are then mounted into the devcontainer at `/root/.aws`, making them available to the `sccache` binary.

Sources: [.github/actions/workflow-run-job-linux/action.yml:113-129]()

### S3 Bucket Configuration

The S3 bucket `rapids-sccache-devs` is configured in the AWS config file and located in the `us-east-2` region. The bucket name appears in the config file's `[default]` section, where sccache automatically reads it.

Sccache uses this configuration to:
1. Check for cached compilation results before compiling
2. Upload new compilation results after successful compilation
3. Share artifacts across all CI jobs and developers

The shared cache provides significant speedups for:
- Template instantiation caching (C++ templates)
- Incremental builds after small changes
- Parallel job execution with overlapping compilation units

Sources: [.github/actions/workflow-run-job-linux/action.yml:115-119]()

### Statistics Collection

After job completion, sccache statistics are collected and uploaded as artifacts:

```bash
find_and_copy "sccache_stats.json" || :
```

The `sccache_stats.json` file contains cache hit rates, miss rates, compilation counts, and error information. These statistics are later aggregated by the results system to provide project-wide cache performance metrics.

Sources: [.github/actions/workflow-run-job-linux/action.yml:186]()

### Volume Mount Path Translation

A critical implementation detail: the AWS credentials directory is mounted using the `host_path()` function to translate container paths to host paths:

```bash
host_path() {
  sed "s@/__w@$(dirname "$(dirname "${{github.workspace}}")")@" <<< "$1"
}

# Mount AWS credentials
--volume "$(host_path "$RUNNER_TEMP")/.aws:/root/.aws"
```

This translation is necessary because the Docker CLI runs inside the intermediate container but launches containers on the host's Docker daemon. Volume mounts must reference paths as they exist on the host, not as seen by the intermediate container.

Sources: [.github/actions/workflow-run-job-linux/action.yml:138-140](), [.github/actions/workflow-run-job-linux/action.yml:162]()

---

## GPU Resource Management

The system provides sophisticated GPU resource management for CUDA workloads, including GPU detection, explicit device selection, and container-level GPU isolation. This ensures jobs on multi-GPU runners only access their allocated GPU device.

### GPU Detection and Allocation Flow

```mermaid
graph TB
    RunnerName["Runner name<br/>(inputs.runner)"]
    DetectionLogic["GPU detection logic<br/>[action.yml:131-136]()"]
    EnvVar["NVIDIA_VISIBLE_DEVICES<br/>(set by GHA runner)"]
    
    GPURequest["gpu_request array<br/>(bash array)"]
    GPUFlag["--gpus flag:<br/>device=$NVIDIA_VISIBLE_DEVICES"]
    
    LaunchScript["launch.sh invocation<br/>[action.yml:144-164]()"]
    DockerRun["docker run command<br/>(executed by launch.sh)"]
    
    DevContainer["DevContainer<br/>(GPU accessible)"]
    CUDAWorkload["CUDA commands<br/>(builds, tests)"]
    
    RunnerName --> DetectionLogic
    EnvVar --> DetectionLogic
    DetectionLogic --> GPURequest
    GPURequest --> GPUFlag
    GPUFlag --> LaunchScript
    LaunchScript --> DockerRun
    DockerRun --> DevContainer
    DevContainer --> CUDAWorkload
    
    style EnvVar fill:#f9f9f9
    style DevContainer fill:#f9f9f9
```

**GPU Resource Management Flow**

GPU allocation occurs through a combination of GitHub Actions runner naming conventions, environment variable detection, and Docker runtime GPU flags. The system automatically detects GPU availability and passes appropriate flags to the Docker daemon.

Sources: [.github/actions/workflow-run-job-linux/action.yml:131-136]()

### Runner-Based GPU Detection

The GPU detection logic uses runner name pattern matching to determine if GPU access should be requested:

```bash
declare -a gpu_request=()

# Explicitly pass which GPU to use if on a GPU runner
if [[ "${RUNNER}" = *"-gpu-"* ]]; then
  gpu_request+=(--gpus "device=${NVIDIA_VISIBLE_DEVICES}")
fi
```

This logic assumes GPU-enabled runners follow a naming convention that includes the substring `-gpu-`. When detected, the script constructs a `--gpus` flag that will be passed to Docker.

The `NVIDIA_VISIBLE_DEVICES` environment variable is set by the GitHub Actions runner infrastructure and contains a comma-separated list of GPU device IDs (e.g., `0`, `1,2`, or `GPU-<uuid>`). By passing this directly to Docker's `--gpus device=` parameter, the system ensures containers only see the specific GPU(s) allocated to the job.

Sources: [.github/actions/workflow-run-job-linux/action.yml:131-136]()

### Docker Runtime Integration

The GPU request array is passed to `launch.sh` using bash array expansion:

```bash
${{github.event.repository.name}}/.devcontainer/launch.sh \
  --docker \
  --cuda ${{inputs.cuda}} \
  --host ${{inputs.host}} \
  "${gpu_request[@]}" \
  --env "CI=$CI" \
  # ... additional flags
```

The `"${gpu_request[@]}"` expansion inserts the GPU flags into the argument list. If no GPU is detected, the array is empty and no flags are added. If a GPU is detected, the array contains `--gpus "device=${NVIDIA_VISIBLE_DEVICES}"`.

The `launch.sh` script forwards these flags to the underlying `docker run` command, which communicates with the NVIDIA Container Runtime to provide GPU access inside the devcontainer.

Sources: [.github/actions/workflow-run-job-linux/action.yml:144-164]()

### NVIDIA Container Runtime Requirements

The GPU integration depends on the host runner having:

1. **NVIDIA GPU drivers** installed on the host
2. **NVIDIA Container Runtime** (`nvidia-docker2`) installed
3. **Docker daemon configuration** that includes the NVIDIA runtime

The GitHub Actions runner environment provides these prerequisites for runners with names containing `-gpu-`. The container sees the GPU as if it were directly attached to the system, allowing full CUDA functionality including compilation, profiling, and execution.

### Multi-GPU Isolation

For runners with multiple GPUs, the `NVIDIA_VISIBLE_DEVICES` environment variable provides job-level isolation. GitHub Actions may schedule multiple concurrent jobs on the same multi-GPU runner, with each job seeing only its allocated GPU(s). This prevents resource contention and ensures reproducible performance.

Example scenarios:

| Runner GPUs | `NVIDIA_VISIBLE_DEVICES` | Container GPU View |
|-------------|--------------------------|-------------------|
| Single GPU (ID 0) | `0` | Single GPU at index 0 |
| Two GPUs, job 1 | `0` | Single GPU at index 0 |
| Two GPUs, job 2 | `1` | Single GPU at index 0 (remapped) |
| All GPUs | `0,1,2,3` | Four GPUs at indices 0-3 |

The NVIDIA Container Runtime automatically remaps device indices inside the container, so a container with `device=1` sees that GPU as index 0 from the container's perspective.

---

## Override Matrix Mechanism

The override matrix mechanism allows the requested workflows to be completely replaced when a non-empty `override` workflow exists in the matrix file. This enables testing custom configurations without modifying the standard workflow definitions.

### Override Decision Flow

```mermaid
graph TB
    Input["workflow-build inputs"]
    AllowOverride["allow_override input<br/>[action.yml:8-11]()"]
    RequestedWorkflows["workflows input<br/>(e.g., 'pull_request')"]
    
    MatrixFile["matrix.yaml"]
    OverrideWorkflow["'override' workflow<br/>(special workflow name)"]
    
    BuildStep["build-workflow.py invocation<br/>[action.yml:82-88]()"]
    AllowOverrideFlag["--allow-override flag<br/>(conditional)"]
    
    Decision{"override workflow<br/>exists and non-empty?"}
    UseOverride["Use override workflow<br/>(ignore workflows input)"]
    UseRequested["Use requested workflows<br/>(normal operation)"]
    
    WorkflowJSON["workflow.json<br/>(filtered jobs)"]
    
    Input --> AllowOverride
    Input --> RequestedWorkflows
    MatrixFile --> OverrideWorkflow
    
    AllowOverride --> BuildStep
    AllowOverrideFlag --> BuildStep
    RequestedWorkflows --> BuildStep
    OverrideWorkflow --> BuildStep
    
    BuildStep --> Decision
    Decision -->|Yes + allow_override=true| UseOverride
    Decision -->|No or allow_override=false| UseRequested
    
    UseOverride --> WorkflowJSON
    UseRequested --> WorkflowJSON
    
    style Decision fill:#f9f9f9
    style WorkflowJSON fill:#f9f9f9
```

**Override Matrix Decision Flow**

The override mechanism operates at the workflow generation phase, before any jobs are dispatched. When enabled, it checks for a special `override` workflow definition in the matrix file and uses it instead of the requested workflows.

Sources: [.github/actions/workflow-build/action.yml:8-11](), [.github/actions/workflow-build/action.yml:78]()

### Configuration Interface

The override system is controlled by a single action input:

**Input: `allow_override`**
- Type: String (boolean)
- Default: `"false"`
- Values: `"true"` or `"false"` (string literals)
- Purpose: Enable override matrix substitution

When set to `"true"`, the input is converted to the `--allow-override` flag for `build-workflow.py`:

```yaml
env:
  allow_override: ${{ inputs.allow_override == 'true' && '--allow-override' || ''}}
```

This conditional expression produces either `--allow-override` (if true) or an empty string (if false or unset).

Sources: [.github/actions/workflow-build/action.yml:78]()

### Build Workflow Invocation

The override flag is passed to the workflow generation script:

```bash
${{ env.matrix_parser }} ${{ inputs.matrix_file }} \
    --workflows ${{ inputs.workflows }} \
    ${{ env.allow_override }} \
    ${{ env.dirty_projects_flag }} ${{ env.dirty_projects }}
```

When `build-workflow.py` receives the `--allow-override` flag, it checks if a workflow named `override` exists in the matrix file and contains at least one job. If so, it ignores the `--workflows` argument and uses the override workflow instead.

This mechanism is particularly useful for:
- **Testing experimental configurations** without affecting standard CI
- **Debugging workflow generation** with minimal job sets
- **Running custom test matrices** in pull requests
- **Temporary workflow modifications** without changing workflow files

Sources: [.github/actions/workflow-build/action.yml:85-88]()

### Matrix File Structure

The override workflow is defined in `matrix.yaml` like any other workflow:

```yaml
workflows:
  pull_request:
    # ... standard PR jobs
  
  nightly:
    # ... nightly jobs
  
  override:
    # Custom jobs that replace requested workflows when allow_override=true
    - {project: 'libcudacxx', std: 17, ctk: '12.0', cxx: 'gcc12'}
```

If the `override` workflow is empty or absent, the system behaves normally and uses the requested workflows. This allows the override workflow to be committed to the repository without affecting standard CI operation unless explicitly enabled.

### Use Cases and Patterns

Common override patterns include:

**Minimal Test Set**: Quickly validate workflow generation changes with a single job
```yaml
override:
  - {project: 'libcudacxx', std: 17, ctk: '12.0', cxx: 'gcc12'}
```

**Specific Configuration Debugging**: Test a problematic compiler/CUDA combination in isolation
```yaml
override:
  - {project: 'thrust', std: 20, ctk: '11.8', cxx: 'clang16', gpu: 'v100'}
```

**Cross-Project Testing**: Validate changes across multiple projects with minimal configurations
```yaml
override:
  - {project: 'libcudacxx', std: 17, ctk: '12.0', cxx: 'gcc12'}
  - {project: 'cub', std: 17, ctk: '12.0', cxx: 'gcc12'}
  - {project: 'thrust', std: 17, ctk: '12.0', cxx: 'gcc12'}
```

The override workflow respects all standard matrix processing: tag expansion, canonicalization, exclusions, and two-stage job handling. It simply replaces the input workflow selection step.

---

## Summary of Advanced Features

| Feature | Trigger | Configuration Location | Output Impact |
|---------|---------|------------------------|---------------|
| Change Detection | PR file changes | `inspect_changes_script` input | Filters workflow.json by dirty_projects |
| Sccache Integration | Every job | AWS OIDC + `.aws/config` | Generates sccache_stats.json artifacts |
| GPU Management | Runner name pattern | Automatic via `-gpu-` runners | Adds --gpus flag to Docker invocation |
| Override Matrix | Explicit flag | `allow_override` input + matrix.yaml | Replaces requested workflows entirely |

These advanced features operate independently and can be combined. For example, a workflow can simultaneously use change detection to filter jobs, sccache for faster builds, GPU management for CUDA testing, and override matrix for custom configurations.

For implementation details of change detection filtering, see [Exclusions and Filtering](#2.3). For sccache statistics collection in results processing, see [Execution Summary Generation](#6.3). For GPU runner configuration and devcontainer integration, see [Linux Execution Environment](#5.1).

---

# Page: Change Detection

# Change Detection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/workflows/verify-devcontainers.yml](.github/workflows/verify-devcontainers.yml)

</details>



This document explains the change detection mechanisms used to optimize CI/CD resource utilization by selectively executing jobs based on file modifications. The system performs git diff analysis to identify changed files and projects, enabling conditional workflow execution and job filtering.

For information about how detected changes influence job generation and filtering, see [Configuration Guide](#2) and [Exclusions and Filtering](#2.3). For details on the workflow generation pipeline that consumes change detection outputs, see [Workflow Generation](#3).

---

## Overview

The change detection system implements two primary optimization strategies:

1. **Job Filtering**: Limits job execution to only projects affected by code changes using the `dirty_projects` mechanism
2. **Workflow Skipping**: Conditionally skips entire workflow runs when no relevant files have been modified

These mechanisms reduce unnecessary compute costs and provide faster feedback during pull request validation by avoiding redundant builds and tests.

**Key Components**:

| Component | Purpose | Integration Point |
|-----------|---------|-------------------|
| `inspect-changes-script` | Analyzes git diffs to identify changed projects | `workflow-build` action input |
| `dirty_projects` output | List of affected projects passed to job generation | `build-workflow.py` filtering |
| Base SHA resolution | Determines comparison baseline for git diff | PR merge base or specified commit |
| File pattern matching | Identifies relevant file paths using regex | Devcontainer verification workflow |

Sources: [.github/actions/workflow-build/action.yml:12-19]()

---

## Inspect Changes Script Integration

The `workflow-build` action accepts an optional `inspect-changes-script` that performs git diff analysis between a base SHA and the current HEAD commit.

### Configuration

```mermaid
graph LR
    Input1["inspect_changes_script<br/>(action input)"]
    Input2["inspect_changes_base_sha<br/>(action input)"]
    Step["Inspect changes step"]
    Output["dirty_projects output"]
    Summary["changes.md summary"]
    
    Input1 --> Step
    Input2 --> Step
    Step --> Output
    Step --> Summary
    
    Output --> BuildWorkflow["build-workflow.py --dirty-projects"]
    Summary --> Artifact["workflow artifact"]
```

**Inspect Changes Step Configuration**

The workflow-build action conditionally executes the inspect-changes step when both required inputs are provided:

[.github/actions/workflow-build/action.yml:61-72]()

**Input Parameters**:

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `inspect_changes_script` | Path to script that analyzes git diffs | No | `""` |
| `inspect_changes_base_sha` | Git SHA to use as comparison baseline | No | `""` |

The step only runs when both parameters are non-empty: `if: ${{ inputs.inspect_changes_script != '' && inputs.inspect_changes_base_sha != '' }}`

### Script Execution Flow

```mermaid
sequenceDiagram
    participant WFBuild as workflow-build action
    participant InspectScript as inspect-changes-script
    participant Git as Git Repository
    participant Output as Step Outputs
    
    WFBuild->>InspectScript: Execute with base_ref and GITHUB_SHA
    InspectScript->>Git: git diff base_ref..GITHUB_SHA
    Git-->>InspectScript: Changed files list
    InspectScript->>InspectScript: Analyze project dependencies
    InspectScript->>Output: Set dirty_projects output
    InspectScript->>Output: Write GITHUB_STEP_SUMMARY
    Output-->>WFBuild: dirty_projects available for next step
    WFBuild->>WFBuild: Copy summary to workflow/changes.md
```

The script receives two arguments:
1. `base_ref` - The baseline commit SHA for comparison
2. `GITHUB_SHA` - The current HEAD commit SHA

The script must output a `dirty_projects` value through GitHub Actions output mechanism and generate a summary in `GITHUB_STEP_SUMMARY`.

Sources: [.github/actions/workflow-build/action.yml:61-72]()

---

## Dirty Projects Filtering

The `dirty_projects` output from the inspect-changes step flows into the `build-workflow.py` script to filter job generation.

### Integration with Workflow Generation

```mermaid
graph TB
    InspectStep["Inspect changes step"]
    DirtyProjects["dirty_projects output"]
    BuildStep["Parse matrix file step"]
    Flag["--dirty-projects flag"]
    BuildWorkflow["build-workflow.py"]
    Matrix["matrix.yaml"]
    FilteredJobs["Filtered workflow.json"]
    
    InspectStep --> DirtyProjects
    DirtyProjects --> BuildStep
    BuildStep --> Flag
    BuildStep --> BuildWorkflow
    Matrix --> BuildWorkflow
    Flag --> BuildWorkflow
    BuildWorkflow --> FilteredJobs
```

**Conditional Flag Construction**

The build-workflow step constructs command-line arguments based on whether change detection is enabled:

[.github/actions/workflow-build/action.yml:74-88]()

**Environment Variable Resolution**:

| Variable | Condition | Value |
|----------|-----------|-------|
| `dirty_projects_flag` | `inspect_changes_script != ''` | `--dirty-projects` |
| `dirty_projects_flag` | `inspect_changes_script == ''` | `""` (empty) |
| `dirty_projects` | `inspect_changes_script != ''` | Output from inspect-changes step |
| `dirty_projects` | `inspect_changes_script == ''` | `""` (empty) |

When both values are non-empty, the `build-workflow.py` script receives the `--dirty-projects` flag with the project list, triggering job filtering logic.

### Filtering Behavior

When `--dirty-projects` is provided to `build-workflow.py`, the script:

1. Parses the provided project list
2. Compares against job definitions in `matrix.yaml`
3. Excludes jobs for projects not in the dirty list
4. Preserves jobs for changed projects and their dependencies

This ensures that only affected components are built and tested, while maintaining dependency integrity.

Sources: [.github/actions/workflow-build/action.yml:74-88]()

---

## Devcontainer Verification Change Detection

The `verify-devcontainers` workflow implements an independent change detection system to conditionally skip devcontainer validation when irrelevant files are modified.

### Workflow Architecture

```mermaid
graph TB
    Trigger["workflow_call trigger"]
    Input["base_sha input"]
    GetList["get-devcontainer-list job"]
    InspectChanges["Inspect changes step"]
    GitDiff["git diff analysis"]
    Regex["File pattern matching"]
    Skip["skip output"]
    VerifyJob["verify-devcontainers job"]
    
    Trigger --> Input
    Input --> GetList
    GetList --> InspectChanges
    InspectChanges --> GitDiff
    GitDiff --> Regex
    Regex --> Skip
    Skip -->|"skip='true'"| VerifyJob
    Skip -->|"skip='false'"| VerifyJob
    
    VerifyJob -.->|"Conditionally skipped"| End["Job skipped"]
```

**Conditional Execution Logic**

The verify-devcontainers job matrix only runs when the skip output is not 'true':

[.github/workflows/verify-devcontainers.yml:96-104]()

Sources: [.github/workflows/verify-devcontainers.yml:1-25]()

### Git Diff Analysis

The inspect-changes step performs merge base resolution and file filtering:

```mermaid
sequenceDiagram
    participant Step as Inspect changes step
    participant Git as Git Repository
    participant Regex as File Pattern Matcher
    participant Output as GitHub Output
    
    Step->>Git: git fetch origin --unshallow
    Step->>Git: git fetch origin base_sha
    Step->>Git: git merge-base GITHUB_SHA base_sha
    Git-->>Step: merge_base_sha
    
    Step->>Git: git diff --name-only merge_base_sha GITHUB_SHA
    Git-->>Step: all_dirty_files
    
    Step->>Regex: Filter with file_regex pattern
    Regex-->>Step: relevant_dirty_files
    
    alt No relevant files
        Step->>Output: skip=true
    else Relevant files found
        Step->>Output: skip=false
    end
```

**Implementation Details**:

[.github/workflows/verify-devcontainers.yml:50-86]()

**Key Operations**:

1. **Merge Base Resolution**: Determines the common ancestor commit between PR base and HEAD
2. **Full Diff**: Retrieves all modified files using `git diff --name-only`
3. **Pattern Filtering**: Applies regex to identify relevant files
4. **Skip Decision**: Sets output based on whether relevant files exist

Sources: [.github/workflows/verify-devcontainers.yml:50-86]()

---

## File Pattern Matching

The change detection system uses regular expressions to identify files that warrant workflow execution.

### Devcontainer Relevant Files

**Pattern Definition**:

[.github/workflows/verify-devcontainers.yml:72-73]()

```regex
^(.devcontainer|ci/matrix.yaml|.github/actions/workflow-build/build-workflow.py)
```

**Matched Paths**:

| Pattern Component | Matches | Purpose |
|------------------|---------|---------|
| `.devcontainer` | Any file under `.devcontainer/` directory | Devcontainer configurations and scripts |
| `ci/matrix.yaml` | The matrix configuration file | Job definitions that may affect devcontainers |
| `.github/actions/workflow-build/build-workflow.py` | Workflow generation script | Logic that processes matrix and generates jobs |

**Filtering Logic**:

[.github/workflows/verify-devcontainers.yml:67-78]()

The filtering uses a multi-stage process:

1. **Full Diff Listing**: Captures all changed files between merge base and HEAD
2. **Pattern Application**: `grep -E "${file_regex}"` filters the list
3. **Empty Check**: Tests if filtered list is empty to determine skip condition

The `|| true` suffix on the grep command prevents pipeline failure when no matches are found.

### Extensibility

Custom inspect-changes scripts can implement arbitrary file pattern matching logic tailored to specific project structures. Common patterns include:

- **Project-specific paths**: `^projects/specific_project/`
- **Build system files**: `(CMakeLists.txt|\.cmake)$`
- **Configuration files**: `(\.yaml|\.json|\.toml)$`
- **Documentation**: `(\.md|docs)` (typically excluded from build triggering)

Sources: [.github/workflows/verify-devcontainers.yml:65-86]()

---

## Benefits and Use Cases

### Resource Optimization

**Cost Reduction Scenarios**:

| Scenario | Without Change Detection | With Change Detection |
|----------|-------------------------|----------------------|
| Documentation-only PR | ~100 jobs execute | 0 jobs execute |
| Single project change | All projects build | Only affected project builds |
| Devcontainer-unrelated change | All devcontainers verify | Verification skipped |
| Configuration file update | All jobs run | Only relevant jobs run |

### Workflow Skip Conditions

```mermaid
graph TD
    PR["Pull Request Opened"]
    InspectChanges["Run inspect-changes-script"]
    Analyze["Analyze changed files"]
    
    CheckRelevant{"Relevant files<br/>changed?"}
    
    SkipWorkflow["Set skip=true<br/>Workflow skipped"]
    RunAll["Run all jobs"]
    
    CheckDirty{"dirty_projects<br/>empty?"}
    
    RunFiltered["Run filtered jobs<br/>for dirty projects"]
    
    PR --> InspectChanges
    InspectChanges --> Analyze
    Analyze --> CheckRelevant
    
    CheckRelevant -->|"No"| SkipWorkflow
    CheckRelevant -->|"Yes"| CheckDirty
    
    CheckDirty -->|"Yes"| RunAll
    CheckDirty -->|"No"| RunFiltered
```

**Common Skip Scenarios**:

- **Documentation Updates**: Changes only to `*.md` files outside of matrix configuration
- **CI Workflow Changes**: Modifications to workflows that don't affect matrix or devcontainers
- **GitHub Configuration**: Updates to issue templates, CODEOWNERS, or other repository settings
- **Non-Build Assets**: Changes to images, diagrams, or other non-executable files

### Fast Feedback

Change detection provides faster CI feedback by:

1. **Reducing Queue Time**: Fewer jobs means less competition for runner resources
2. **Faster Job Scheduling**: GitHub Actions can dispatch filtered jobs immediately
3. **Targeted Validation**: Developers see results for affected components without waiting for unrelated tests
4. **Incremental Development**: Enables rapid iteration on specific components

### Integration Pattern

**Typical Usage in Consumer Repository**:

```yaml
jobs:
  build-workflow:
    uses: ./.github/actions/workflow-build
    with:
      workflows: pull_request
      inspect_changes_script: ./ci/inspect_changes.sh
      inspect_changes_base_sha: ${{ github.event.pull_request.base.sha }}
      matrix_file: ci/matrix.yaml
```

The consumer repository provides:
- Custom `inspect_changes.sh` script with project-specific logic
- Base SHA from PR event context
- Matrix configuration with project definitions

Sources: [.github/actions/workflow-build/action.yml:12-19](), [.github/workflows/verify-devcontainers.yml:5-9]()

---

## Limitations and Considerations

### Dependency Tracking

The inspect-changes script must implement dependency resolution to avoid breaking transitive dependencies:

- **Library Changes**: If library A is modified, dependent projects B and C should also be marked dirty
- **Shared Headers**: Changes to common header files may affect multiple projects
- **Build System**: Modifications to CMake modules or build scripts may require full rebuild

### False Negatives

Change detection can produce false negatives (failing to detect necessary rebuilds) when:

- Dependencies are not properly tracked in the inspect-changes script
- Generated files are not considered in the analysis
- Cross-project integration points are not identified

### Merge Base Accuracy

The merge base calculation assumes:
- The base branch has been fetched: `git fetch origin --unshallow`
- The base SHA is available: `git fetch origin $BASE_SHA`
- The repository has sufficient history for merge-base resolution

Shallow clones may require `--unshallow` to access merge base commits.

Sources: [.github/workflows/verify-devcontainers.yml:56-59]()

---

## Summary

The change detection system provides intelligent workflow optimization through:

- **Git Diff Analysis**: Identifies modified files between base and HEAD commits
- **Project Filtering**: Limits job execution to affected components via `dirty_projects`
- **Workflow Skipping**: Conditionally bypasses entire workflows when irrelevant files change
- **Pattern Matching**: Uses regex to identify files warranting CI execution
- **Cost Optimization**: Reduces compute resource usage by avoiding unnecessary jobs

The system integrates with the workflow-build action through optional inputs and conditional step execution, enabling both full and filtered CI runs based on code change context.

Sources: [.github/actions/workflow-build/action.yml:12-88](), [.github/workflows/verify-devcontainers.yml:50-86]()

---

# Page: Distributed Compilation Caching

# Distributed Compilation Caching

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)
- [.github/actions/workflow-run-job-windows/action.yml](.github/actions/workflow-run-job-windows/action.yml)
- [.github/workflows/verify-devcontainers.yml](.github/workflows/verify-devcontainers.yml)

</details>



This document explains the integration of sccache (shared compilation cache) with AWS S3 for distributed compilation caching across GitHub Actions runners. It covers S3 bucket configuration, OIDC-based credential management, platform-specific integration strategies for Linux and Windows execution environments, and statistics collection.

For information about how jobs are executed in containers, see [Job Execution](#5). For details on artifact collection and reporting, see [Artifact Collection](#6.1).

## Overview

The cccl-gha system uses [sccache](https://github.com/mozilla/sccache) to cache compilation artifacts in AWS S3, significantly reducing build times by reusing previously compiled object files across workflow runs and different jobs. When a compiler invocation occurs, sccache checks if the same input has been compiled before; if so, it retrieves the cached result from S3 instead of recompiling.

The system implements different credential management strategies for Linux and Windows runners to provide seamless access to the shared S3 bucket while maintaining security through short-lived OIDC tokens.

**Key Components:**
- **S3 Bucket**: `rapids-sccache-devs` in `us-east-2` region
- **IAM Role**: `arn:aws:iam::279114543810:role/gha-oidc-NVIDIA`
- **Authentication**: GitHub OIDC-based temporary credentials (12-hour duration)
- **Statistics**: `sccache_stats.json` collected per job

## System Architecture

```mermaid
graph TB
    subgraph "GitHub Actions Runner"
        Runner["GitHub Runner<br/>(Linux or Windows)"]
        OIDCToken["GitHub OIDC Token"]
    end
    
    subgraph "AWS IAM"
        IAMRole["IAM Role<br/>gha-oidc-NVIDIA<br/>279114543810"]
        STSCreds["Temporary Credentials<br/>12-hour duration"]
    end
    
    subgraph "Linux Execution"
        DindContainer["ubuntu-dind Container"]
        AWSDir[".aws/config<br/>.aws/credentials"]
        DevContainer["Job DevContainer"]
        SccacheLinux["sccache client"]
    end
    
    subgraph "Windows Execution"
        DockerWindows["Windows Docker Container"]
        EnvVars["Environment Variables<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>AWS_SESSION_TOKEN<br/>SCCACHE_*"]
        SccacheWindows["sccache client"]
    end
    
    subgraph "AWS S3"
        S3Bucket["rapids-sccache-devs<br/>us-east-2"]
        CachedObjects["Compilation Artifacts"]
    end
    
    subgraph "Results"
        StatsFile["sccache_stats.json"]
        Artifacts["GitHub Artifacts"]
    end
    
    Runner --> OIDCToken
    OIDCToken -->|"aws-actions/configure-aws-credentials@v4"| IAMRole
    IAMRole --> STSCreds
    
    STSCreds -->|"Linux"| DindContainer
    DindContainer --> AWSDir
    AWSDir -->|"Volume mount"| DevContainer
    DevContainer --> SccacheLinux
    
    STSCreds -->|"Windows"| EnvVars
    EnvVars --> DockerWindows
    DockerWindows --> SccacheWindows
    
    SccacheLinux <-->|"GET/PUT objects"| S3Bucket
    SccacheWindows <-->|"GET/PUT objects"| S3Bucket
    S3Bucket --> CachedObjects
    
    SccacheLinux --> StatsFile
    SccacheWindows --> StatsFile
    StatsFile --> Artifacts
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:60-162](), [.github/actions/workflow-run-job-windows/action.yml:20-64]()

## AWS S3 Configuration

The system uses a dedicated S3 bucket for caching compilation artifacts across all CCCL builds.

**Configuration Details:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Bucket Name | `rapids-sccache-devs` | Shared cache storage |
| Region | `us-east-2` | AWS region (US East - Ohio) |
| IAM Role | `arn:aws:iam::279114543810:role/gha-oidc-NVIDIA` | OIDC-based authentication |
| Session Duration | 43200 seconds (12 hours) | Maximum job runtime allowance |
| SSL | Enabled | Secure data transfer |

The bucket is configured in AWS credential files (Linux) or environment variables (Windows) depending on the execution platform.

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:115-119](), [.github/actions/workflow-run-job-windows/action.yml:21-22]()

## Credential Management

### OIDC Authentication Flow

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions Runner
    participant Action as aws-actions/configure-aws-credentials
    participant OIDC as GitHub OIDC Provider
    participant IAM as AWS IAM
    participant STS as AWS STS
    participant Role as gha-oidc-NVIDIA
    
    GHA->>Action: Trigger authentication
    Action->>OIDC: Request OIDC token
    OIDC-->>Action: Return signed JWT token
    Action->>IAM: AssumeRoleWithWebIdentity
    Note over Action,IAM: Token includes repo/workflow context
    IAM->>Role: Validate trust policy
    Role->>STS: Generate temporary credentials
    STS-->>Action: Return access key, secret, session token
    Action->>GHA: Set environment variables
    Note over GHA: AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>AWS_SESSION_TOKEN
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:60-65](), [.github/actions/workflow-run-job-windows/action.yml:26-31]()

### IAM Role Configuration

The `aws-actions/configure-aws-credentials@v4` action is invoked at the beginning of each job execution to obtain temporary AWS credentials:

[.github/actions/workflow-run-job-linux/action.yml:60-65]()
```
- name: Get AWS credentials for sccache bucket
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::279114543810:role/gha-oidc-NVIDIA
    aws-region: us-east-2
    role-duration-seconds: 43200 # 12 hours
```

The action sets the following environment variables that are subsequently used by sccache:
- `AWS_ACCESS_KEY_ID`: Temporary access key
- `AWS_SECRET_ACCESS_KEY`: Temporary secret key  
- `AWS_SESSION_TOKEN`: Session token for temporary credentials

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:60-65](), [.github/actions/workflow-run-job-windows/action.yml:26-31]()

## Linux Credential Integration

On Linux, credentials are provided to devcontainers through AWS credential files mounted as volumes. This approach allows the sccache client inside containers to authenticate without requiring environment variable propagation.

### Credential File Generation

The workflow generates standard AWS credential files in the runner's temporary directory:

[.github/actions/workflow-run-job-linux/action.yml:113-129]()
```bash
mkdir "$RUNNER_TEMP/.aws";

cat <<EOF > "$RUNNER_TEMP/.aws/config"
[default]
bucket=rapids-sccache-devs
region=us-east-2
EOF

cat <<EOF > "$RUNNER_TEMP/.aws/credentials"
[default]
aws_access_key_id=$AWS_ACCESS_KEY_ID
aws_session_token=$AWS_SESSION_TOKEN
aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
EOF

chmod 0600 "$RUNNER_TEMP/.aws/credentials"
chmod 0664 "$RUNNER_TEMP/.aws/config"
```

### Volume Mounting Strategy

The `.aws` directory is mounted into the devcontainer at `/root/.aws`, making credentials available to sccache:

[.github/actions/workflow-run-job-linux/action.yml:162]()
```bash
--volume "$(host_path "$RUNNER_TEMP")/.aws:/root/.aws"
```

The `host_path` function transforms container paths to host paths, necessary for the Docker-outside-of-Docker (DOOD) architecture:

[.github/actions/workflow-run-job-linux/action.yml:138-140]()
```bash
host_path() {
  sed "s@/__w@$(dirname "$(dirname "${{github.workspace}}")")@" <<< "$1"
}
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:113-162]()

## Windows Credential Integration

On Windows, credentials are propagated as environment variables directly into the Docker container, as Windows Docker does not support the same volume mounting patterns as Linux.

### Environment Variable Configuration

Prior to credential acquisition, sccache-specific environment variables are configured:

[.github/actions/workflow-run-job-windows/action.yml:18-25]()
```bash
echo "SCCACHE_BUCKET=rapids-sccache-devs" | tee -a "${GITHUB_ENV}"
echo "SCCACHE_REGION=us-east-2" | tee -a "${GITHUB_ENV}"
echo "SCCACHE_IDLE_TIMEOUT=0" | tee -a "${GITHUB_ENV}"
echo "SCCACHE_S3_USE_SSL=true" | tee -a "${GITHUB_ENV}"
echo "SCCACHE_S3_NO_CREDENTIALS=false" | tee -a "${GITHUB_ENV}"
```

### Container Environment Propagation

AWS credentials and sccache configuration are injected into the container environment using PowerShell's `SetEnvironmentVariable`:

[.github/actions/workflow-run-job-windows/action.yml:54-64]()
```powershell
powershell -c "
  [System.Environment]::SetEnvironmentVariable('AWS_ACCESS_KEY_ID','${{env.AWS_ACCESS_KEY_ID}}');
  [System.Environment]::SetEnvironmentVariable('AWS_SECRET_ACCESS_KEY','${{env.AWS_SECRET_ACCESS_KEY}}');
  [System.Environment]::SetEnvironmentVariable('AWS_SESSION_TOKEN','${{env.AWS_SESSION_TOKEN }}');
  [System.Environment]::SetEnvironmentVariable('SCCACHE_BUCKET','${{env.SCCACHE_BUCKET}}');
  [System.Environment]::SetEnvironmentVariable('SCCACHE_REGION','${{env.SCCACHE_REGION}}');
  [System.Environment]::SetEnvironmentVariable('SCCACHE_IDLE_TIMEOUT','${{env.SCCACHE_IDLE_TIMEOUT}}');
  [System.Environment]::SetEnvironmentVariable('SCCACHE_S3_USE_SSL','${{env.SCCACHE_S3_USE_SSL}}');
  [System.Environment]::SetEnvironmentVariable('SCCACHE_S3_NO_CREDENTIALS','${{env.SCCACHE_S3_NO_CREDENTIALS}}');
  ...
"
```

**Sources:** [.github/actions/workflow-run-job-windows/action.yml:18-64]()

## Statistics Collection

After job execution, sccache statistics are collected as artifacts for analysis and reporting. The statistics file provides cache hit rates, data transfer metrics, and compilation counts.

### Artifact Collection Process

Both Linux and Windows execution workflows search for `sccache_stats.json` in the repository directory after command completion:

[.github/actions/workflow-run-job-linux/action.yml:186]()
```bash
find_and_copy "sccache_stats.json" || :
```

[.github/actions/workflow-run-job-windows/action.yml:87]()
```bash
find_and_copy "sccache_stats.json" || true # Ignore failures
```

The `find_and_copy` function locates the statistics file and copies it to the job results directory:

[.github/actions/workflow-run-job-linux/action.yml:176-184]()
```bash
find_and_copy() {
  filename="$1"
  filepath="$(find ${{github.event.repository.name}} -name "${filename}" -print -quit)"
  if [[ -z "$filepath" ]]; then
    echo "${filename} does not exist in repo directory."
    return 1
  fi
  cp -v "$filepath" "$result_dir"
}
```

### Artifact Structure

Statistics are uploaded with job-specific artifact names:

[.github/actions/workflow-run-job-linux/action.yml:195-200]()
```yaml
- name: Upload job artifacts
  uses: actions/upload-artifact@v4
  with:
    name: jobs-${{inputs.id}}
    path: jobs
    compression-level: 0
```

The uploaded artifact contains:
- `jobs/<job-id>/success`: Success marker file
- `jobs/<job-id>/sccache_stats.json`: Cache statistics (if generated)
- `jobs/<job-id>/cccl_meta_bench.csv`: Benchmark data (if generated)
- Additional benchmark files

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:166-200](), [.github/actions/workflow-run-job-windows/action.yml:65-98]()

## DevContainer Verification

The `verify-devcontainers` workflow also configures sccache credentials to ensure devcontainers can build without hanging on authentication prompts.

[.github/workflows/verify-devcontainers.yml:116-128]()
```yaml
- name: Get AWS credentials for sccache bucket
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::279114543810:role/gha-oidc-NVIDIA
    aws-region: us-east-2
    role-duration-seconds: 43200 # 12 hours
- name: Set environment variables
  run: |
    echo "SCCACHE_BUCKET=rapids-sccache-devs" >> $GITHUB_ENV
    echo "SCCACHE_REGION=us-east-2" >> $GITHUB_ENV
    echo "SCCACHE_IDLE_TIMEOUT=32768" >> $GITHUB_ENV
    echo "SCCACHE_S3_USE_SSL=true" >> $GITHUB_ENV
    echo "SCCACHE_S3_NO_CREDENTIALS=false" >> $GITHUB_ENV
```

Credentials are then passed to the `devcontainers/ci@v0.3` action:

[.github/workflows/verify-devcontainers.yml:135-139]()
```yaml
env: |
  SCCACHE_REGION=${{ env.SCCACHE_REGION }}
  AWS_ACCESS_KEY_ID=${{ env.AWS_ACCESS_KEY_ID }}
  AWS_SESSION_TOKEN=${{ env.AWS_SESSION_TOKEN }}
  AWS_SECRET_ACCESS_KEY=${{ env.AWS_SECRET_ACCESS_KEY }}
```

**Sources:** [.github/workflows/verify-devcontainers.yml:116-139]()

## Environment Variables Reference

The following table documents all environment variables related to sccache and AWS credentials:

| Variable | Platform | Value/Source | Purpose |
|----------|----------|--------------|---------|
| `AWS_ACCESS_KEY_ID` | Both | Set by `configure-aws-credentials` | Temporary access key for S3 |
| `AWS_SECRET_ACCESS_KEY` | Both | Set by `configure-aws-credentials` | Temporary secret key for S3 |
| `AWS_SESSION_TOKEN` | Both | Set by `configure-aws-credentials` | Session token for temporary credentials |
| `SCCACHE_BUCKET` | Windows | `rapids-sccache-devs` | S3 bucket name |
| `SCCACHE_REGION` | Windows | `us-east-2` | AWS region |
| `SCCACHE_IDLE_TIMEOUT` | Windows | `0` | Idle timeout (0 = infinite) |
| `SCCACHE_S3_USE_SSL` | Windows | `true` | Enable SSL/TLS for S3 |
| `SCCACHE_S3_NO_CREDENTIALS` | Windows | `false` | Use AWS credentials (not anonymous) |

### Platform Differences

**Linux:**
- Credentials stored in `$RUNNER_TEMP/.aws/credentials` and `$RUNNER_TEMP/.aws/config`
- Files mounted into container at `/root/.aws/`
- Bucket and region configured in `.aws/config`
- sccache reads credentials from standard AWS credential chain

**Windows:**
- All credentials passed as environment variables
- No credential files created
- Environment variables set directly in Docker container
- sccache reads credentials from environment

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:74-76,113-129](), [.github/actions/workflow-run-job-windows/action.yml:20-25,55-62]()

## Integration Flow

```mermaid
graph LR
    subgraph "Job Initialization"
        A["Workflow starts"]
        B["configure-aws-credentials"]
        C["Set AWS env vars"]
    end
    
    subgraph "Credential Setup"
        D1["Linux: Create .aws files"]
        D2["Windows: Set SCCACHE_* env"]
    end
    
    subgraph "Container Launch"
        E1["Linux: Mount .aws volume"]
        E2["Windows: Pass env vars"]
        F["DevContainer starts"]
    end
    
    subgraph "Compilation"
        G["sccache initialized"]
        H["Compiler invoked"]
        I["Cache check"]
        J1["Cache hit: Download"]
        J2["Cache miss: Compile + Upload"]
    end
    
    subgraph "Artifact Collection"
        K["Generate sccache_stats.json"]
        L["find_and_copy"]
        M["Upload to GitHub Artifacts"]
    end
    
    A --> B
    B --> C
    C --> D1
    C --> D2
    D1 --> E1
    D2 --> E2
    E1 --> F
    E2 --> F
    F --> G
    G --> H
    H --> I
    I --> J1
    I --> J2
    J1 --> K
    J2 --> K
    K --> L
    L --> M
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:60-200](), [.github/actions/workflow-run-job-windows/action.yml:18-98]()

---

# Page: GPU Resource Management

# GPU Resource Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)
- [.github/workflows/workflow-dispatch-standalone-group-linux.yml](.github/workflows/workflow-dispatch-standalone-group-linux.yml)

</details>



## Purpose and Scope

This document describes how the cccl-gha system detects, allocates, and manages NVIDIA GPU resources for CUDA workloads. It covers GPU detection logic, the `NVIDIA_VISIBLE_DEVICES` environment variable propagation, and Docker GPU access configuration through the container execution layers.

For general Linux job execution architecture, see [Linux Execution Environment](#5.1). For environment variable setup and configuration, see [Environment Setup](#5.4).

---

## GPU Detection and Allocation

The system automatically detects whether a job requires GPU access by examining the runner identifier string. Jobs scheduled on runners with names containing the substring `"-gpu-"` are identified as GPU-enabled jobs and receive appropriate GPU resource configuration.

### Runner-Based GPU Detection

The GPU detection logic occurs in the command execution step:

```mermaid
graph TB
    subgraph "Runner Assignment"
        A["matrix.runner<br/>(e.g., 'linux-amd64-gpu-v100-latest-1')"]
    end
    
    subgraph "GPU Detection Logic"
        B["Check if runner contains '-gpu-'"]
        C{"Contains<br/>'-gpu-'?"}
        D["Set gpu_request array:<br/>--gpus 'device=${NVIDIA_VISIBLE_DEVICES}'"]
        E["gpu_request remains empty"]
    end
    
    subgraph "Docker Launch"
        F["launch.sh invocation"]
        G["Docker run with GPU access"]
        H["Docker run without GPU"]
    end
    
    A --> B
    B --> C
    C -->|"Yes"| D
    C -->|"No"| E
    D --> F
    E --> F
    F --> G
    F --> H
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:131-148]()

The detection implementation:

| Component | Implementation | Location |
|-----------|----------------|----------|
| **Detection Pattern** | String match: `[[ "${RUNNER}" = *"-gpu-"* ]]` | [action.yml:134]() |
| **GPU Request Array** | `gpu_request+=(--gpus "device=${NVIDIA_VISIBLE_DEVICES}")` | [action.yml:135]() |
| **Launch Integration** | `"${gpu_request[@]}"` in launch.sh call | [action.yml:148]() |

---

## NVIDIA_VISIBLE_DEVICES Environment Variable

The `NVIDIA_VISIBLE_DEVICES` environment variable controls which GPU devices are visible to containerized processes. This variable originates at the GitHub Actions runner host level and must propagate through multiple container layers to reach the final devcontainer execution environment.

### Variable Propagation Architecture

```mermaid
graph TB
    subgraph "GitHub Runner Host"
        A["NVIDIA_VISIBLE_DEVICES<br/>Set by GitHub runner<br/>(e.g., '0' for single GPU)"]
    end
    
    subgraph "ubuntu-dind Container"
        B["container.env.NVIDIA_VISIBLE_DEVICES<br/>Propagated from host"]
        C["Bash environment<br/>$NVIDIA_VISIBLE_DEVICES"]
        D["gpu_request array construction:<br/>--gpus 'device=${NVIDIA_VISIBLE_DEVICES}'"]
    end
    
    subgraph "Devcontainer Launch"
        E["launch.sh --gpus argument"]
        F["Docker run --gpus device=X"]
    end
    
    subgraph "Target Devcontainer"
        G["NVIDIA_VISIBLE_DEVICES<br/>Inside devcontainer<br/>(GPU visible to CUDA runtime)"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
```

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:28-29](), [.github/actions/workflow-run-job-linux/action.yml:134-136]()

### Propagation Mechanism

The variable propagates through three distinct layers:

1. **Runner Host → ubuntu-dind Container**
   - Configured in workflow YAML: `container.env.NVIDIA_VISIBLE_DEVICES: ${{env.NVIDIA_VISIBLE_DEVICES}}`
   - Location: [.github/workflows/workflow-dispatch-standalone-group-linux.yml:28-29]()

2. **ubuntu-dind Container → Docker CLI Argument**
   - Shell expands variable: `--gpus "device=${NVIDIA_VISIBLE_DEVICES}"`
   - Location: [.github/actions/workflow-run-job-linux/action.yml:135]()

3. **Docker Argument → Target Devcontainer**
   - Docker runtime configures GPU visibility based on `--gpus` flag
   - Final container receives GPU access restricted to specified device

---

## Docker GPU Access Configuration

The `--gpus` flag is a Docker runtime parameter that controls GPU resource allocation to containers. The system uses this flag with the `device=` parameter to restrict GPU visibility to specific devices.

### GPU Flag Construction

```mermaid
graph LR
    subgraph "Conditional Logic"
        A["RUNNER variable"]
        B["Contains '-gpu-' substring?"]
        C["Declare gpu_request array"]
    end
    
    subgraph "Flag Construction"
        D["gpu_request+=(--gpus 'device=${NVIDIA_VISIBLE_DEVICES}')"]
        E["Empty gpu_request array"]
    end
    
    subgraph "Launch Invocation"
        F["launch.sh call"]
        G["${gpu_request[@]} expanded"]
        H["No GPU flags"]
    end
    
    A --> B
    B -->|"Yes"| C
    B -->|"No"| E
    C --> D
    D --> F
    E --> F
    F --> G
    F --> H
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:131-148]()

### Implementation Details

The GPU configuration implementation uses bash array expansion for clean optional argument handling:

| Step | Code Pattern | Purpose |
|------|--------------|---------|
| **Array Declaration** | `declare -a gpu_request=()` | Initialize empty array for GPU arguments |
| **Conditional Population** | `gpu_request+=(--gpus "device=${NVIDIA_VISIBLE_DEVICES}")` | Add GPU flag only for GPU runners |
| **Array Expansion** | `"${gpu_request[@]}"` | Expand to nothing (empty runners) or GPU flag (GPU runners) |

**Source:** [.github/actions/workflow-run-job-linux/action.yml:131-148]()

The constructed flag format is: `--gpus "device=${NVIDIA_VISIBLE_DEVICES}"`, where the device parameter specifies which GPU indices are accessible. For example, if `NVIDIA_VISIBLE_DEVICES=0`, only GPU 0 becomes visible to the container.

---

## GPU Resource Flow

The complete GPU resource management flow spans from runner assignment through container execution:

```mermaid
sequenceDiagram
    participant M as matrix.yaml
    participant D as Dispatch Workflow
    participant R as GitHub Runner Host
    participant U as ubuntu-dind Container
    participant L as launch.sh
    participant DC as Devcontainer
    
    M->>D: Job includes runner: "linux-amd64-gpu-v100-latest-1"
    D->>R: Schedule job on GPU runner
    Note over R: Runner has NVIDIA_VISIBLE_DEVICES<br/>set by GitHub (e.g., "0")
    R->>U: Launch ubuntu-dind container<br/>with env: NVIDIA_VISIBLE_DEVICES
    Note over U: Container receives GPU visibility<br/>from host environment
    U->>U: Detect GPU requirement:<br/>"$RUNNER" contains "-gpu-"
    U->>U: Construct gpu_request array:<br/>--gpus "device=${NVIDIA_VISIBLE_DEVICES}"
    U->>L: Invoke launch.sh with GPU arguments
    L->>DC: Docker run with:<br/>--gpus "device=0"
    Note over DC: CUDA runtime sees single GPU<br/>NVIDIA_VISIBLE_DEVICES=0
    DC->>DC: Execute CUDA workload<br/>with restricted GPU access
```

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:25-29](), [.github/actions/workflow-run-job-linux/action.yml:131-148]()

---

## GPU Allocation Strategy

The system implements a **single GPU per job** allocation strategy. Each job receives exclusive access to exactly one GPU device, enforced through `NVIDIA_VISIBLE_DEVICES` restriction.

### Single GPU Allocation Model

| Aspect | Implementation | Rationale |
|--------|----------------|-----------|
| **Device Isolation** | `NVIDIA_VISIBLE_DEVICES` set to single device ID | Prevents resource contention between parallel jobs |
| **Exclusive Access** | GitHub runner assignment to specific GPU | Ensures predictable performance characteristics |
| **Device Selection** | Controlled by GitHub runner infrastructure | GitHub manages physical GPU allocation |
| **Visibility Restriction** | Docker `--gpus device=` parameter | CUDA runtime only sees assigned GPU |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:29](), [.github/actions/workflow-run-job-linux/action.yml:135]()

### Allocation Enforcement Points

The allocation is enforced at three levels:

1. **Runner Level**: GitHub assigns jobs to runners with specific GPU hardware
2. **Container Environment**: `NVIDIA_VISIBLE_DEVICES` limits device visibility
3. **Docker Runtime**: `--gpus device=` parameter restricts container access

This multi-layer enforcement ensures that even if CUDA applications attempt to enumerate all GPUs, they only discover the single allocated device.

---

## Docker-Outside-of-Docker (DOOD) Considerations

The DOOD architecture introduces special considerations for GPU access, as GPU resources must be accessible through multiple container layers while maintaining proper device isolation.

### GPU Access Through Container Layers

```mermaid
graph TB
    subgraph "Host Level"
        A["GitHub Runner Host<br/>Physical GPU Hardware<br/>NVIDIA Drivers"]
        B["Docker Daemon<br/>/var/run/docker.sock"]
    end
    
    subgraph "Intermediate Layer"
        C["ubuntu-dind Container<br/>Docker CLI<br/>NVIDIA_VISIBLE_DEVICES from host"]
    end
    
    subgraph "Target Layer"
        D["Devcontainer<br/>CUDA Runtime<br/>GPU Access via --gpus flag"]
    end
    
    A --> B
    B -->|"Socket mounted into"| C
    C -->|"Docker run command via socket to"| B
    B -->|"Launches with GPU access"| D
    A -->|"Direct GPU access"| D
    
    style C fill:#f9f9f9
    style D fill:#f0f0f0
```

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:1-21]()

The DOOD pattern means the intermediate `ubuntu-dind` container does not need GPU access itself—it only needs the `NVIDIA_VISIBLE_DEVICES` environment variable to construct the correct `--gpus` argument. The actual GPU access is established directly between the host and the devcontainer when the Docker daemon (running on the host) launches the devcontainer.

### Key DOOD GPU Properties

| Property | Behavior | Implication |
|----------|----------|-------------|
| **Socket-Based Communication** | ubuntu-dind uses host Docker daemon | GPU resources managed by host daemon |
| **Environment Variable Visibility** | NVIDIA_VISIBLE_DEVICES visible in ubuntu-dind | Used for command construction only |
| **Direct GPU Mapping** | Host GPU mapped directly to devcontainer | No GPU access needed in intermediate container |
| **Driver Consistency** | Single driver instance on host | Avoids driver version mismatch issues |

**Sources:** [.github/actions/workflow-run-job-linux/action.yml:4-20]()

---

## Environment Variable Reference

The following environment variables are involved in GPU resource management:

| Variable | Set By | Used By | Purpose |
|----------|--------|---------|---------|
| **NVIDIA_VISIBLE_DEVICES** | GitHub runner infrastructure | ubuntu-dind container, Docker CLI | Specifies which GPU device(s) are visible |
| **RUNNER** | GitHub Actions | GPU detection logic | Identifies runner type for GPU requirement detection |
| **CUDA** | Job configuration input | launch.sh | Selects devcontainer with appropriate CUDA version |

**Sources:** [.github/workflows/workflow-dispatch-standalone-group-linux.yml:29](), [.github/actions/workflow-run-job-linux/action.yml:35-40](), [.github/actions/workflow-run-job-linux/action.yml:70](), [.github/actions/workflow-run-job-linux/action.yml:134]()

### Variable Lifecycle

1. **NVIDIA_VISIBLE_DEVICES**: Set by GitHub at runner creation → Propagated to ubuntu-dind → Used in `--gpus` flag → Visible in devcontainer
2. **RUNNER**: Set by GitHub Actions → Read in action.yml → Used for GPU detection
3. **CUDA**: Defined in matrix.yaml → Passed as input → Used for devcontainer selection

---

## Error Conditions and Edge Cases

### GPU Not Available

If a job is assigned to a GPU runner but the GPU is not accessible (driver issues, hardware failure), the devcontainer launch will fail when Docker attempts to attach GPU resources. The error typically manifests as:

```
Error response from daemon: could not select device driver "" with capabilities: [[gpu]]
```

### Incorrect Runner Assignment

If a job requiring GPU is mistakenly assigned to a non-GPU runner, the GPU detection logic will correctly skip GPU configuration. However, the CUDA runtime in the devcontainer will fail with:

```
CUDA error: no CUDA-capable device is detected
```

**Source:** [.github/actions/workflow-run-job-linux/action.yml:134-136]()

### Multiple GPU Visibility

The current implementation does not support jobs that require multiple GPUs. If `NVIDIA_VISIBLE_DEVICES` is set to multiple device IDs (e.g., "0,1"), the devcontainer will see all specified GPUs, but the system is designed and tested for single-GPU workloads.

---

# Page: Override Matrix

# Override Matrix

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/actions/workflow-results/action.yml](.github/actions/workflow-results/action.yml)

</details>



## Purpose and Scope

This document explains the override matrix mechanism, which allows a special `override` workflow in the matrix configuration to supersede standard workflow selections. This feature is designed for testing, debugging, and emergency scenarios where a specific subset of jobs must run instead of the normal workflow configuration.

For general matrix configuration, see [Configuration Guide](#2). For workflow generation details, see [Workflow Generation](#3).

---

## Overview

The override matrix mechanism provides a way to temporarily replace the requested workflows with a custom job configuration. When enabled, the system ignores the `workflows` input parameter and instead executes jobs defined in a special `override` workflow within the matrix file. As a safety measure, workflows run with override configurations always fail in the results phase to prevent accidental merges of code tested only with non-standard job sets.

**Sources:** [.github/actions/workflow-build/action.yml:8-11](), [.github/actions/workflow-results/action.yml:169-175]()

---

## Override Workflow Flow

The following diagram illustrates how the override mechanism intercepts the normal workflow generation process:

```mermaid
graph TB
    Input["workflow-build Action<br/>Input: workflows"]
    AllowOverride["Input: allow_override"]
    MatrixFile["matrix.yaml<br/>workflows:<br/>- pull_request<br/>- nightly<br/>- override"]
    
    BuildWorkflow["build-workflow.py"]
    OverrideCheck{"allow_override == true<br/>AND<br/>override workflow<br/>non-empty?"}
    
    NormalPath["Process requested<br/>workflows"]
    OverridePath["Process override<br/>workflow only"]
    
    WorkflowJSON["workflow/workflow.json"]
    OverrideMarker["workflow/override.json"]
    
    Results["workflow-results Action"]
    OverrideDetect{"override.json<br/>exists?"}
    FailJobs["Force failure<br/>success=false"]
    NormalCheck["Normal success<br/>verification"]
    
    Input --> BuildWorkflow
    AllowOverride --> BuildWorkflow
    MatrixFile --> BuildWorkflow
    
    BuildWorkflow --> OverrideCheck
    OverrideCheck -->|No| NormalPath
    OverrideCheck -->|Yes| OverridePath
    
    NormalPath --> WorkflowJSON
    OverridePath --> WorkflowJSON
    OverridePath --> OverrideMarker
    
    WorkflowJSON --> Results
    OverrideMarker --> Results
    
    Results --> OverrideDetect
    OverrideDetect -->|Yes| FailJobs
    OverrideDetect -->|No| NormalCheck
```

**Sources:** [.github/actions/workflow-build/action.yml:8-11,78,86-88](), [.github/actions/workflow-results/action.yml:169-175]()

---

## Configuration

### Defining an Override Workflow

The override workflow is defined in `matrix.yaml` alongside normal workflows like `pull_request`, `nightly`, and `weekly`. It uses the same structure as any other workflow definition:

```yaml
workflows:
  pull_request:
    # Normal PR jobs...
  
  nightly:
    # Normal nightly jobs...
  
  override:
    # Custom test jobs
    - {project: 'libcudacxx', ctk: '12.4', cxx: 'gcc12', std: '17', gpu: 'v100'}
    - {project: 'thrust', ctk: '12.4', cxx: 'clang18', std: '20'}
```

The `override` workflow can contain any valid job specifications using the standard tag system. It can be empty (no jobs) or contain a minimal set of jobs for targeted testing.

**Sources:** [.github/actions/workflow-build/action.yml:5-7]()

---

## Activation

### The allow_override Input

The override mechanism is controlled by the `allow_override` input to the `workflow-build` action:

| Input Parameter | Type | Default | Description |
|----------------|------|---------|-------------|
| `allow_override` | boolean | `false` | When `true`, requested workflows are ignored if a non-empty override workflow exists |

**Sources:** [.github/actions/workflow-build/action.yml:8-11]()

### Flag Processing

The `allow_override` input is converted to a command-line flag for the matrix parser:

```mermaid
graph LR
    Input["allow_override input<br/>'true' or 'false'"]
    EnvVar["Environment variable:<br/>allow_override"]
    Ternary{"value == 'true'?"}
    Flag["--allow-override"]
    Empty["(empty string)"]
    Parser["build-workflow.py<br/>--allow-override"]
    
    Input --> EnvVar
    EnvVar --> Ternary
    Ternary -->|Yes| Flag
    Ternary -->|No| Empty
    Flag --> Parser
    Empty --> Parser
```

The environment variable is constructed at [.github/actions/workflow-build/action.yml:78]() using a ternary expression:

```yaml
allow_override: ${{ inputs.allow_override == 'true' && '--allow-override' || ''}}
```

This is then passed to the matrix parser at [.github/actions/workflow-build/action.yml:87]():

```bash
${{ env.matrix_parser }} ${{ inputs.matrix_file }}           \
    --workflows ${{ inputs.workflows }}                      \
    ${{ env.allow_override }}                                \
    ${{ env.dirty_projects_flag }} ${{ env.dirty_projects }}
```

**Sources:** [.github/actions/workflow-build/action.yml:74-88]()

---

## Override Detection and Processing

### Matrix Parser Behavior

When `build-workflow.py` receives the `--allow-override` flag, it checks if:
1. An `override` workflow is defined in the matrix file
2. The `override` workflow contains at least one job

If both conditions are met, the parser ignores the `--workflows` argument and processes only the `override` workflow. Otherwise, it proceeds with the requested workflows normally.

### Override Marker File

When an override workflow is processed, the system creates a marker file at `workflow/override.json`. This file serves two purposes:
1. Documents that the workflow run used an override configuration
2. Triggers the failure mechanism in the results phase

**Sources:** [.github/actions/workflow-build/action.yml:85-88]()

---

## Override Enforcement

### Results Phase Detection

The `workflow-results` action checks for the presence of `workflow/override.json` during the success verification step:

```mermaid
graph TB
    CheckSuccess["Check for job success step"]
    VerifyJobs["verify-job-success.py<br/>Check success markers"]
    OverrideCheck{"workflow/override.json<br/>exists?"}
    
    Notice["::notice::<br/>Workflow matrix was overridden.<br/>Failing jobs."]
    DisplayOverride["Display override.json<br/>contents"]
    SetFailure["success=false<br/>exit 1"]
    
    SetSuccess["success=true"]
    
    CheckSuccess --> VerifyJobs
    VerifyJobs --> OverrideCheck
    
    OverrideCheck -->|Yes| Notice
    Notice --> DisplayOverride
    DisplayOverride --> SetFailure
    
    OverrideCheck -->|No| SetSuccess
```

The detection logic at [.github/actions/workflow-results/action.yml:169-175]():

```yaml
if [ -f workflow/override.json ]; then
  echo "::notice::Workflow matrix was overridden. Failing jobs."
  echo "Override matrix:"
  cat workflow/override.json | jq -c '.'
  echo "success=false" >> "${GITHUB_OUTPUT}"
  exit 1
fi
```

This ensures that even if all override jobs succeed, the overall workflow fails. This prevents code from being merged when it has only been tested against a non-standard job subset.

**Sources:** [.github/actions/workflow-results/action.yml:155-177]()

---

## Use Cases

### Testing New Job Configurations

The override mechanism is valuable when testing new job configurations before adding them to production workflows:

```yaml
override:
  # Test new CUDA 12.5 support
  - {project: 'cub', ctk: '12.5', cxx: 'gcc13', std: '20', gpu: 'h100'}
  - {project: 'thrust', ctk: '12.5', cxx: 'gcc13', std: '20', gpu: 'h100'}
```

### Debugging Specific Failures

When a specific combination fails in production, the override workflow allows isolated reproduction:

```yaml
override:
  # Reproduce clang18 + CUDA 12.4 + std=20 failure
  - {project: 'thrust', ctk: '12.4', cxx: 'clang18', std: '20', gpu: 'v100'}
```

### Emergency Hotfix Validation

In emergency situations requiring rapid validation of a critical fix, override can run a minimal job set:

```yaml
override:
  # Quick smoke test on primary platforms only
  - {project: 'libcudacxx', ctk: '12.4', cxx: 'gcc12', gpu: 'v100'}
  - {project: 'thrust', ctk: '12.4', cxx: 'gcc12', gpu: 'v100'}
  - {project: 'cub', ctk: '12.4', cxx: 'gcc12', gpu: 'v100'}
```

### Development Workflow Testing

Developers can test changes to the workflow generation system itself using controlled override configurations without affecting production workflow definitions.

**Sources:** [.github/actions/workflow-build/action.yml:8-11]()

---

## Safety Mechanisms

The override system includes multiple safety mechanisms to prevent misuse:

| Mechanism | Location | Purpose |
|-----------|----------|---------|
| Opt-in activation | `allow_override` input must be explicitly set to `true` | Prevents accidental override activation |
| Forced failure | Results phase always fails when override detected | Prevents merging code tested only with override jobs |
| Visual notification | GitHub Actions notice annotation | Makes override usage visible in workflow logs |
| Override marker file | `workflow/override.json` persisted as artifact | Provides audit trail of override usage |

**Sources:** [.github/actions/workflow-build/action.yml:8-11](), [.github/actions/workflow-results/action.yml:169-175]()

---

## Integration with Other Features

### Change Detection Compatibility

The override mechanism works alongside change detection (see [Change Detection](#7.1)). When both are active:
1. If override is triggered, `--dirty-projects` filtering is still applied
2. Override jobs not matching dirty projects are excluded
3. This allows testing specific configurations for only the changed code

### Dispatch Group Processing

Override jobs are processed through the same dispatch group mechanism as normal jobs:
- Split into standalone vs. two-stage patterns
- Categorized by operating system (Linux/Windows)
- Executed with identical infrastructure

This ensures override jobs have the same execution environment and reliability as production jobs.

**Sources:** [.github/actions/workflow-build/action.yml:79-88]()

---

## Limitations and Considerations

### Automatic Failure Requirement

The forced failure in the results phase is by design and cannot be disabled. This is a critical safety feature. If override jobs need to be merged, they must first be migrated to a production workflow (e.g., `pull_request`, `nightly`).

### Artifact Preservation

Even though override workflows fail, all artifacts (job results, timing data, summaries) are preserved and accessible for analysis.

### Notification Behavior

Override workflow failures trigger Slack alert notifications (if configured) like any other failure. Teams should be aware that override usage will generate these alerts.

**Sources:** [.github/actions/workflow-results/action.yml:197-212]()

---

## Example: Complete Override Workflow

The following example demonstrates a complete workflow run using override:

```mermaid
sequenceDiagram
    participant User
    participant GHA as GitHub Actions
    participant Build as workflow-build
    participant Parser as build-workflow.py
    participant Dispatch as Dispatch Layer
    participant Exec as Execution Layer
    participant Results as workflow-results
    
    User->>GHA: Trigger workflow with<br/>allow_override: true
    GHA->>Build: workflows: "pull_request"<br/>allow_override: true
    
    Build->>Parser: --workflows pull_request<br/>--allow-override
    Note over Parser: Detects non-empty<br/>override workflow
    Parser->>Parser: Ignore pull_request<br/>Process override only
    Parser-->>Build: workflow.json<br/>(override jobs)
    Parser-->>Build: override.json<br/>(marker file)
    
    Build->>Dispatch: dispatch.json
    Dispatch->>Exec: Execute override jobs
    Exec-->>Results: Job artifacts<br/>(all jobs succeed)
    
    Results->>Results: Check workflow/override.json
    Note over Results: File exists!
    Results->>Results: Force failure:<br/>success=false
    Results->>GHA: Workflow FAILED
    Results->>User: Slack alert:<br/>"Override was used"
```

**Sources:** [.github/actions/workflow-build/action.yml:74-88](), [.github/actions/workflow-results/action.yml:155-177,197-212]()

---

# Page: Reference

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/actions/workflow-results/action.yml](.github/actions/workflow-results/action.yml)

</details>



This page provides comprehensive reference documentation for developers working with or extending the cccl-gha system. It documents all action interfaces, file format specifications, environment variables, and troubleshooting procedures. This reference assumes familiarity with the system architecture; for architectural concepts, see [System Architecture](#1.1). For configuration details, see [Configuration Guide](#2). For execution environment details, see [Job Execution](#5).

## Action Interfaces

The system exposes two primary composite GitHub Actions that orchestrate the workflow generation and results collection pipelines.

### workflow-build Action Interface

The `workflow-build` action transforms a matrix configuration file into dispatchable job definitions.

**Location**: [.github/actions/workflow-build/action.yml]()

#### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `workflows` | Yes | - | Space-separated list of workflow names from matrix file to execute |
| `allow_override` | No | `"false"` | If `"true"`, honors `override` workflow in matrix file, superseding `workflows` parameter |
| `inspect_changes_script` | No | `""` | Path to script that detects which projects changed (enables dirty project filtering) |
| `inspect_changes_base_sha` | No | `""` | Git base SHA for change detection comparison |
| `matrix_file` | No | `"ci/matrix.yaml"` | Path to matrix configuration file in consumer repository |
| `matrix_parser` | No | `""` | Path to custom matrix parser script (defaults to bundled `build-workflow.py`) |
| `slack_token` | No | - | Slack Bot OAuth token for notifications (notifications disabled if omitted) |
| `slack_log` | No | - | Slack channel ID for verbose log notifications |
| `slack_alert` | No | - | Slack channel ID for alert notifications (errors only) |

Sources: [.github/actions/workflow-build/action.yml:4-36]()

#### Outputs

| Output | Description |
|--------|-------------|
| `workflow` | JSON string containing dispatch-ready job definitions, structured as `dispatch.json` |

The `workflow` output is a stringified JSON object with four arrays:
- `linux_standalone`: Jobs for standalone Linux execution
- `linux_two_stage`: Producer-consumer chains for Linux
- `windows_standalone`: Jobs for standalone Windows execution
- `windows_two_stage`: Producer-consumer chains for Windows

Sources: [.github/actions/workflow-build/action.yml:38-41]()

#### Processing Steps

```mermaid
graph TB
    Input1["inputs.workflows"]
    Input2["inputs.matrix_file"]
    Input3["inputs.inspect_changes_script"]
    
    Step1["Slack Log Notification<br/>(optional)"]
    Step2["Inspect Changes<br/>outputs.dirty_projects"]
    Step3["build-workflow.py<br/>Parse matrix → workflow.json"]
    Step4["prepare-workflow-dispatch.py<br/>Split by OS/type → dispatch.json"]
    Step5["Set Outputs<br/>WORKFLOW=dispatch.json"]
    Step6["Upload Artifacts<br/>name: workflow"]
    Step7["Slack Error Notification<br/>(on failure)"]
    
    Input1 --> Step3
    Input2 --> Step3
    Input3 --> Step2
    Step2 --> Step3
    
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> Step5
    Step5 --> Step6
    Step3 -.->|failure| Step7
    Step4 -.->|failure| Step7
    
    style Input1 fill:#f9f9f9
    style Input2 fill:#f9f9f9
    style Input3 fill:#f9f9f9
    style Step6 fill:#e8f5e9
```

**Diagram**: workflow-build action processing pipeline showing inputs, transformation steps, and output artifacts.

Sources: [.github/actions/workflow-build/action.yml:43-140]()

### workflow-results Action Interface

The `workflow-results` action collects job artifacts, analyzes results, generates summaries, and reports outcomes through multiple channels.

**Location**: [.github/actions/workflow-results/action.yml]()

#### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `github_token` | No | - | GitHub token for PR commenting (no comment posted if omitted) |
| `pr_number` | No | - | Pull request number to comment on (skipped if not provided) |
| `slack_token` | No | - | Slack Bot OAuth token for notifications |
| `slack_log` | No | - | Slack channel ID for verbose log notifications (always sent) |
| `slack_alert` | No | - | Slack channel ID for alert notifications (failures only) |

Sources: [.github/actions/workflow-results/action.yml:4-19]()

#### Outputs

| Output | Description | Values |
|--------|-------------|--------|
| `success` | Boolean indicating whether all jobs succeeded | `"true"` or `"false"` |

The `success` output is determined by:
1. Checking for `success` marker files in job artifacts ([verify-job-success.py]())
2. Detecting presence of `override.json` (forces failure when matrix override is active)

Sources: [.github/actions/workflow-results/action.yml:21-24]()

#### Processing Steps

```mermaid
graph TB
    A1["Download Workflow Artifacts<br/>name: workflow"]
    A2["Download Job Artifacts<br/>pattern: jobs-*"]
    A3["Clean Up Artifacts<br/>dos2unix conversion"]
    A4["Fetch Job Info<br/>GitHub API → results/jobs.json"]
    A5["parse-job-times.py<br/>workflow.json + jobs.json<br/>→ job_times.json"]
    A6["prepare-execution-summary.py<br/>workflow.json + job_times.json<br/>→ execution/*.json"]
    A7["final-summary.py<br/>Generate HTML/Markdown<br/>→ final_summary.md"]
    A8["Comment on PR<br/>(if github_token provided)"]
    A9["verify-job-success.py<br/>Check success markers<br/>→ success output"]
    A10["Slack Log Notification<br/>(always if token provided)"]
    A11["Slack Alert Notification<br/>(failures only)"]
    
    A1 --> A5
    A2 --> A3
    A3 --> A5
    A4 --> A5
    A5 --> A6
    A6 --> A7
    A7 --> A8
    A1 --> A9
    A2 --> A9
    A7 --> A10
    A9 --> A10
    A9 -.->|failure| A11
    
    style A1 fill:#e3f2fd
    style A2 fill:#e3f2fd
    style A9 fill:#ffebee
```

**Diagram**: workflow-results action processing pipeline showing artifact collection, analysis, and multi-channel reporting.

Sources: [.github/actions/workflow-results/action.yml:26-213]()

## File Format Specifications

### matrix.yaml Structure

The matrix configuration file defines all jobs using a hierarchical structure. See [Matrix YAML Structure](#2.1) for comprehensive documentation.

**Key Sections**:
- `workflows`: Named workflow definitions (e.g., `pull_request`, `nightly`)
- `projects`: List of projects to build/test
- Each job entry contains tags (CTK version, compiler, GPU, etc.)

**Example Structure**:
```yaml
workflows:
  pull_request:
    - {project: 'libcudacxx', std: 17, ctk: '12.0', cxx: ['gcc10', 'clang16']}
    - {project: 'thrust', gpu: 'v100', ctk: '11.8', cxx: 'gcc11'}
```

Sources: Referenced throughout [Configuration Guide](#2)

### workflow.json Schema

Generated by `build-workflow.py`, contains complete job specifications after tag processing.

**Structure**:
```json
{
  "jobs": [
    {
      "id": "unique-job-identifier",
      "name": "human-readable-name",
      "runner": "linux-amd64-gpu-v100-latest-1",
      "image": "rapidsai/devcontainers:...",
      "command": "ci/test.sh",
      "tags": {
        "project": "libcudacxx",
        "std": "17",
        "ctk": "12.0",
        "cxx": "gcc10",
        "gpu": "v100",
        "sm": "70"
      },
      "origin": {
        "workflow": "pull_request",
        "source": "ci/matrix.yaml:123"
      }
    }
  ]
}
```

**Key Fields**:
- `id`: Unique job identifier used for artifact paths and tracking
- `runner`: GitHub Actions runner label (e.g., `linux-amd64-gpu-v100-latest-1`)
- `image`: Docker/devcontainer image specification
- `command`: Shell command to execute
- `tags`: Fully resolved tag dictionary (all defaults applied, derived tags computed)
- `origin`: Provenance information for debugging

**Companion Files**:
- `job_ids.json`: Mapping of job IDs to array indices
- `job_list.txt`: Human-readable job list
- `runner_summary.json`: Runner allocation statistics

Sources: Generated by [build-workflow.py](); consumed by [prepare-workflow-dispatch.py](), [workflow-dispatch-* workflows]()

### dispatch.json Schema

Produced by `prepare-workflow-dispatch.py`, organizes jobs by execution pattern.

**Structure**:
```json
{
  "linux_standalone": [
    {
      "id": "job-id",
      "runner": "linux-amd64-cpu",
      "image": "container:tag",
      "command": "./build.sh"
    }
  ],
  "linux_two_stage": [
    {
      "producer": {
        "id": "producer-job-id",
        "runner": "linux-amd64-gpu-v100-latest-1",
        "image": "build-container",
        "command": "./compile.sh"
      },
      "consumers": [
        {
          "id": "consumer-1-id",
          "runner": "linux-amd64-gpu-t4-latest-1",
          "image": "test-container",
          "command": "./test.sh"
        }
      ]
    }
  ],
  "windows_standalone": [...],
  "windows_two_stage": [...]
}
```

**Dispatch Categories**:
- **standalone**: Independent jobs with no dependencies
- **two_stage**: Producer-consumer chains where producers build artifacts consumed by parallel test jobs

Each category is split by OS to route to appropriate execution workflows.

Sources: [prepare-workflow-dispatch.py](), [.github/actions/workflow-build/action.yml:102-109]()

### job_times.json Schema

Generated by `parse-job-times.py`, contains timing analysis for all jobs.

**Structure**:
```json
{
  "jobs": {
    "job-id-123": {
      "name": "Job Display Name",
      "status": "completed",
      "conclusion": "success",
      "duration_seconds": 245,
      "command_time_seconds": 180,
      "overhead_seconds": 65,
      "started_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:34:05Z",
      "runner": "linux-amd64-gpu-v100-latest-1",
      "tags": {
        "project": "thrust",
        "ctk": "12.0"
      }
    }
  },
  "summary": {
    "total_jobs": 150,
    "completed": 148,
    "failed": 2,
    "total_duration_seconds": 36000,
    "avg_overhead_seconds": 45
  }
}
```

**Timing Metrics**:
- `duration_seconds`: Total wall-clock time from job start to completion
- `command_time_seconds`: Actual command execution time (extracted from logs)
- `overhead_seconds`: Infrastructure overhead (checkout, setup, cleanup)

Sources: [parse-job-times.py](), [.github/actions/workflow-results/action.yml:92-97]()

### Job Artifact Files

Jobs produce standardized artifacts uploaded to GitHub Actions artifact storage.

#### Success Markers

**Path**: `jobs/{job_id}/success`

Empty marker file indicating job completed successfully. Presence checked by [verify-job-success.py]().

#### sccache Statistics

**Path**: `jobs/{job_id}/sccache_stats.json`

**Structure**:
```json
{
  "cache_hits": 1234,
  "cache_misses": 56,
  "cache_hit_rate": 0.956,
  "cache_size_bytes": 5242880000
}
```

Generated by sccache and uploaded by job execution workflows.

#### Benchmark Data

**Path**: `jobs/{job_id}/cccl_meta_bench.csv`

CSV format with benchmark results (schema varies by benchmark type).

Sources: [.github/actions/workflow-results/action.yml:36-57](), job execution workflows

## Environment Variables Reference

### GitHub Actions Context Variables

These standard GitHub Actions variables are available in all workflow steps.

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `GITHUB_WORKSPACE` | Absolute path to repository checkout | `/home/runner/work/cccl/cccl` |
| `GITHUB_SHA` | Commit SHA that triggered workflow | `abc123def456...` |
| `GITHUB_REF` | Full git ref that triggered workflow | `refs/heads/main` |
| `GITHUB_REPOSITORY` | Repository name in `owner/repo` format | `NVIDIA/cccl` |
| `GITHUB_RUN_ID` | Unique workflow run identifier | `1234567890` |
| `GITHUB_RUN_NUMBER` | Sequential run number for this workflow | `42` |
| `GITHUB_ACTOR` | Username that triggered workflow | `octocat` |
| `GITHUB_STEP_SUMMARY` | Path to step summary file | `/home/runner/work/_temp/_runner_file_commands/step_summary_...` |
| `GITHUB_OUTPUT` | Path to step outputs file | `/home/runner/work/_temp/_runner_file_commands/set_output_...` |

Sources: GitHub Actions documentation, used throughout all action.yml files

### AWS and sccache Variables

Required for distributed compilation caching via AWS S3.

| Variable | Description | Set By | Example |
|----------|-------------|--------|---------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key | Workflow secrets | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key | Workflow secrets | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_DEFAULT_REGION` | AWS region for S3 bucket | Workflow/job config | `us-east-1` |
| `SCCACHE_BUCKET` | S3 bucket name for cache storage | Workflow/job config | `rapids-sccache-devs` |
| `SCCACHE_REGION` | AWS region (redundant with above) | Workflow/job config | `us-east-1` |
| `SCCACHE_IDLE_TIMEOUT` | Daemon shutdown timeout in seconds | Workflow/job config | `0` (never) |
| `SCCACHE_S3_USE_SSL` | Enable SSL for S3 connections | Workflow/job config | `true` |

These variables are configured in Linux job execution via `.aws/config` and `.aws/credentials` files mounted into containers.

Sources: [Linux Execution Environment](#5.1), [Distributed Compilation Caching](#7.2)

### CUDA and GPU Variables

Control GPU resource allocation and CUDA runtime behavior.

| Variable | Description | Set By | Example |
|----------|-------------|--------|---------|
| `NVIDIA_VISIBLE_DEVICES` | GPU device IDs visible to container | Runner environment | `0` or `0,1` |
| `CUDA_VISIBLE_DEVICES` | CUDA-level GPU device filter | Job/workflow | `0` |
| `CUDAARCHS` | CMake CUDA architectures to build | Derived from `sm` tag | `70;75;80` |

The `NVIDIA_VISIBLE_DEVICES` variable controls Docker's `--gpus` flag, while `CUDA_VISIBLE_DEVICES` provides additional runtime filtering.

Sources: [GPU Resource Management](#7.3), [.devcontainer/launch.sh]()

### Custom System Variables

Variables specific to cccl-gha system operation.

| Variable | Description | Set By | Example |
|----------|-------------|--------|---------|
| `CI` | Indicates CI environment | GitHub Actions | `true` |
| `MATRIX_FILE` | Path to matrix configuration | workflow-build input | `ci/matrix.yaml` |
| `WORKFLOW_TYPE` | Workflow category for notifications | Workflow definition | `pull_request`, `nightly` |
| `SUMMARY_URL` | URL to workflow run summary | Constructed from GitHub context | `https://github.com/NVIDIA/cccl/actions/runs/1234567890` |
| `COMMAND` | Job command to execute | Passed through dispatch | `./ci/build_and_test.sh` |

Sources: [.github/actions/workflow-build/action.yml](), [.github/actions/workflow-results/action.yml]()

### Job Execution Environment Variables

Variables set within job execution containers.

```mermaid
graph TB
    subgraph "Runner Host"
        HostEnv["Host Environment<br/>GITHUB_*, AWS_*"]
    end
    
    subgraph "ubuntu-dind Container"
        DindEnv["Inherited + Local<br/>GITHUB_WORKSPACE<br/>AWS credentials"]
        LaunchSh["launch.sh"]
    end
    
    subgraph "DevContainer"
        DevEnv["Inherited + Overrides<br/>CUDA_VISIBLE_DEVICES<br/>CUDAARCHS<br/>PATH"]
        CiSh["ci.sh (job command)"]
    end
    
    HostEnv -->|"mount + env"| DindEnv
    DindEnv -->|"docker run -e"| DevEnv
    LaunchSh -->|"constructs"| DevEnv
    DevEnv --> CiSh
    
    style HostEnv fill:#f9f9f9
    style DevEnv fill:#e8f5e9
```

**Diagram**: Environment variable propagation through execution layers from GitHub Actions runner to devcontainer.

Sources: [Linux Execution Environment](#5.1), [.devcontainer/launch.sh]()

## Common Workflows and Patterns

### Adding a New Job to matrix.yaml

**Steps**:

1. **Identify the workflow** (e.g., `pull_request`, `nightly`)
2. **Add job entry** with required tags:
   ```yaml
   - project: 'my_project'
     ctk: '12.0'
     cxx: 'gcc11'
     gpu: 'v100'
     std: 17
     type: 'build'
   ```
3. **Verify tag validity** against schema (see [Tags and Parameters](#2.2))
4. **Add exclusions if needed** (see [Exclusions and Filtering](#2.3))
5. **Test locally** using workflow-build action

**Common Pitfalls**:
- Missing required tags (varies by job type)
- Invalid tag values (must match allowed values in schema)
- Conflicting exclusions (job may be silently filtered)

Sources: [Matrix YAML Structure](#2.1)

### Debugging Job Failures

#### Using ci.sh for Reproduction

Every job generates a `ci.sh` script that encapsulates its execution environment. To reproduce locally:

1. **Download ci.sh from failed job**:
   - Navigate to GitHub Actions run → Failed job → Artifacts
   - Download `jobs-{job_id}.zip`
   - Extract `ci.sh`

2. **Review the script**:
   ```bash
   cat ci.sh
   # Shows:
   # - Docker command used
   # - Environment variables
   # - Volume mounts
   # - Exact command executed
   ```

3. **Execute locally** (requires Docker):
   ```bash
   bash ci.sh
   ```

Sources: [Error Handling and Reproducibility](#5.5)

#### Analyzing Timing Data

Use `job_times.json` to identify performance bottlenecks:

```python
import json

with open('results/job_times.json') as f:
    times = json.load(f)

# Find jobs with high overhead
high_overhead = [
    (job_id, data['overhead_seconds'])
    for job_id, data in times['jobs'].items()
    if data['overhead_seconds'] > 60
]

print("Jobs with >60s overhead:")
for job_id, overhead in sorted(high_overhead, key=lambda x: x[1], reverse=True):
    print(f"  {job_id}: {overhead}s")
```

Sources: [Job Timing Analysis](#6.2)

#### Reading Execution Summaries

The `execution/` directory contains hierarchical summaries:

```
execution/
├── heading.txt              # Overall summary
├── libcudacxx_summary.json  # Per-project aggregation
└── thrust_summary.json
```

**Structure of project summary**:
```json
{
  "project": "thrust",
  "total_jobs": 50,
  "passed": 48,
  "failed": 2,
  "pass_rate": 0.96,
  "by_tag": {
    "ctk": {
      "11.8": {"passed": 24, "failed": 0},
      "12.0": {"passed": 24, "failed": 2}
    }
  },
  "likely_culprits": ["ctk:12.0"]
}
```

The `likely_culprits` array identifies tag values where ALL jobs with that tag failed, suggesting a systemic issue.

Sources: [Execution Summary Generation](#6.3)

### Testing Workflow Generation Locally

**Prerequisites**:
- Python 3.8+
- Checkout of cccl-gha repository
- A valid `matrix.yaml` file

**Steps**:

1. **Run build-workflow.py**:
   ```bash
   python3 .github/actions/workflow-build/build-workflow.py \
       path/to/matrix.yaml \
       --workflows pull_request \
       --output workflow/
   ```

2. **Inspect outputs**:
   ```bash
   cat workflow/workflow.json | jq '.jobs | length'
   cat workflow/job_list.txt
   cat workflow/runner_summary.json | jq '.'
   ```

3. **Test dispatch preparation**:
   ```bash
   python3 .github/actions/workflow-build/prepare-workflow-dispatch.py \
       workflow/workflow.json
   cat workflow/dispatch.json | jq '.linux_standalone | length'
   ```

Sources: [build-workflow.py Pipeline](#3.1), [Dispatch Preparation](#3.2)

### Interpreting Slack Notifications

#### Log Channel Format

Sent to `slack_log` for all workflow runs:

```
Workflow 'pull_request' has finished with status `success`:

📊 150 jobs total | ✅ 148 passed | ❌ 2 failed | ⏱️ 10h 15m
Pass rate: 98.7%

Details: https://github.com/NVIDIA/cccl/actions/runs/1234567890
```

#### Alert Channel Format

Sent to `slack_alert` only on failures:

```
Workflow 'nightly' has failed:

📊 200 jobs total | ✅ 180 passed | ❌ 20 failed | ⏱️ 12h 30m
Pass rate: 90.0%

Likely culprits:
  • ctk:12.0 + cxx:gcc10 (15 failures)
  • gpu:a100 (5 failures)

Details: https://github.com/NVIDIA/cccl/actions/runs/9876543210
```

Sources: [Notification System](#6.6), [.github/actions/workflow-results/action.yml:179-212]()

## Troubleshooting Guide

### Common Error Patterns

#### Error: "No jobs generated"

**Symptoms**: `workflow.json` is empty or contains zero jobs

**Causes**:
1. All jobs excluded by filters (check `--dirty-projects`)
2. Invalid workflow name (not present in `matrix.yaml`)
3. All jobs filtered by exclusion rules

**Resolution**:
```bash
# Check which workflows are defined
grep -A 5 "workflows:" ci/matrix.yaml

# Run without dirty-projects filter
python3 build-workflow.py ci/matrix.yaml --workflows pull_request

# Check exclusion rules
grep -A 10 "exclude:" ci/matrix.yaml
```

Sources: [build-workflow.py](), [Exclusions and Filtering](#2.3)

#### Error: "Missing required tag"

**Symptoms**: Build fails with message like `KeyError: 'ctk'`

**Causes**: Job definition missing required tag for its job type

**Resolution**:
1. Review job type requirements in [Tags and Parameters](#2.2)
2. Add missing tags with appropriate defaults:
   ```yaml
   - project: 'myproject'
     ctk: '12.0'  # Add this
     cxx: 'gcc11'
     # ... other required tags
   ```

Sources: [build-workflow.py tag validation](), [Tags and Parameters](#2.2)

#### Error: "Docker: no space left on device"

**Symptoms**: Job fails during Docker build/pull with disk space error

**Causes**: Accumulated Docker images/volumes on runner

**Resolution**:
- Runner cleanup happens automatically between workflow runs
- For local testing: `docker system prune -af`
- Reduce concurrent jobs if issue persists

Sources: Runner maintenance, [Job Execution](#5)

#### Error: "sccache connection timeout"

**Symptoms**: Compilation slow, warnings about sccache S3 connection failures

**Causes**:
1. Invalid AWS credentials
2. Network connectivity issues
3. S3 bucket not accessible

**Resolution**:
```bash
# Verify credentials are set
echo "AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:0:4}..."

# Test S3 access
aws s3 ls s3://rapids-sccache-devs/ --region us-east-1

# Check sccache logs in job output
grep -i sccache job_output.log
```

Compilation will proceed without cache if sccache fails (performance impact only).

Sources: [Distributed Compilation Caching](#7.2), [Environment Setup](#5.4)

### Diagnostic Commands

#### Inspect Job Execution Environment

```bash
# From within a devcontainer or ci.sh
env | grep -E '(GITHUB|CUDA|AWS|SCCACHE)'
docker inspect <container_id>
mount | grep github
```

#### Analyze Workflow Artifacts

```bash
# Download all artifacts
gh run download <run_id>

# Check job success markers
find jobs -name success -type f | wc -l

# Find failed jobs
find jobs -maxdepth 1 -type d | while read dir; do
  if [[ ! -f "$dir/success" ]]; then
    echo "Failed: $(basename $dir)"
  fi
done
```

#### Validate matrix.yaml

```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('ci/matrix.yaml'))"

# Count jobs that would be generated
python3 build-workflow.py ci/matrix.yaml \
    --workflows pull_request \
    | jq '.jobs | length'
```

Sources: Various scripts in `.github/actions/`

### Performance Debugging

#### Identifying Slow Jobs

```python
import json

with open('results/job_times.json') as f:
    times = json.load(f)

# Find slowest jobs
slowest = sorted(
    times['jobs'].items(),
    key=lambda x: x[1]['duration_seconds'],
    reverse=True
)[:10]

print("Top 10 slowest jobs:")
for job_id, data in slowest:
    duration = data['duration_seconds']
    cmd_time = data['command_time_seconds']
    overhead = data['overhead_seconds']
    print(f"{job_id}:")
    print(f"  Total: {duration}s | Command: {cmd_time}s | Overhead: {overhead}s")
```

#### sccache Effectiveness Analysis

```bash
# Aggregate sccache stats across all jobs
find jobs -name sccache_stats.json -exec jq -r \
  '[.cache_hits, .cache_misses] | @tsv' {} \; \
  | awk '{hits+=$1; misses+=$2} END {
      total=hits+misses;
      rate=hits/total*100;
      printf "Total: %d | Hits: %d | Misses: %d | Rate: %.1f%%\n",
        total, hits, misses, rate
    }'
```

Sources: [Job Timing Analysis](#6.2), [Distributed Compilation Caching](#7.2)

### Recovering from Partial Failures

When some jobs fail but others succeed, the results action still produces partial reports:

1. **Download available artifacts**: All successful job artifacts are collected
2. **Partial summaries generated**: Statistics exclude failed jobs with missing data
3. **Failure markers preserved**: `success=false` output ensures workflow fails appropriately

The `continue-on-error: true` directives in [.github/actions/workflow-results/action.yml]() ensure maximum data recovery.

Sources: [.github/actions/workflow-results/action.yml:37-104]()

---

This reference provides the foundational information needed to understand, debug, and extend the cccl-gha workflow orchestration system. For implementation details of specific components, refer to the corresponding sections linked throughout this document.

---

# Page: Action Inputs and Outputs

# Action Inputs and Outputs

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/action.yml](.github/actions/workflow-build/action.yml)
- [.github/actions/workflow-results/action.yml](.github/actions/workflow-results/action.yml)
- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)
- [.github/actions/workflow-run-job-windows/action.yml](.github/actions/workflow-run-job-windows/action.yml)

</details>



This page provides a complete reference of all inputs and outputs for the GitHub Actions in the CCCL workflow orchestration system. These actions encapsulate the core functionality of the CI/CD pipeline, from workflow generation to job execution and results collection.

For information about how these actions are invoked within workflows, see [Job Dispatch](#4). For details about the underlying scripts and data formats, see [File Format Specifications](#8.2).

## Overview of Actions

The CCCL-GHA system defines four composite GitHub Actions that form the execution pipeline:

```mermaid
graph LR
    Build["workflow-build<br/>Action"]
    Results["workflow-results<br/>Action"]
    RunLinux["workflow-run-job-linux<br/>Action"]
    RunWindows["workflow-run-job-windows<br/>Action"]
    
    Build -->|"dispatch.json"| Dispatch["Dispatch<br/>Workflows"]
    Dispatch -->|"Linux jobs"| RunLinux
    Dispatch -->|"Windows jobs"| RunWindows
    RunLinux -->|"job artifacts"| Results
    RunWindows -->|"job artifacts"| Results
    
    Build -.->|"Slack start"| Slack["Slack<br/>Channels"]
    Results -.->|"Slack summary"| Slack
    Results -.->|"PR comment"| GitHub["GitHub<br/>PR"]
```

**Actions by Phase:**
- **Generation Phase**: `workflow-build` - Transforms `matrix.yaml` into dispatchable job definitions
- **Execution Phase**: `workflow-run-job-linux` and `workflow-run-job-windows` - Execute individual jobs in isolated environments
- **Results Phase**: `workflow-results` - Aggregates results, generates summaries, and sends notifications

Sources: [.github/actions/workflow-build/action.yml](), [.github/actions/workflow-results/action.yml](), [.github/actions/workflow-run-job-linux/action.yml](), [.github/actions/workflow-run-job-windows/action.yml]()

---

## workflow-build Action

The `workflow-build` action orchestrates the workflow generation pipeline, transforming a matrix configuration file into dispatchable job definitions organized by OS and execution pattern.

**Location**: [.github/actions/workflow-build/action.yml:1-140]()

### Inputs

| Input Name | Type | Required | Default | Description |
|------------|------|----------|---------|-------------|
| `workflows` | string | **Yes** | - | Space-separated list of workflow names from the matrix file to execute (e.g., `"pull_request"`, `"nightly weekly"`) |
| `allow_override` | boolean | No | `"false"` | If `"true"`, the `workflows` parameter is ignored when a non-empty `override` workflow exists in the matrix file |
| `inspect_changes_script` | string | No | `""` | Path to a script that determines which projects need testing based on file changes. If empty, all jobs are included |
| `inspect_changes_base_sha` | string | No | `""` | Base Git SHA for the inspect-changes script to compare against. Required if `inspect_changes_script` is provided |
| `matrix_file` | string | No | `"ci/matrix.yaml"` | Path to the matrix configuration file in the consumer repository |
| `matrix_parser` | string | No | `""` | Path to a custom matrix parser script. If blank, uses `build-workflow.py` from the action directory |
| `slack_token` | string | No | - | Slack bot token for sending notifications. No notifications are sent if not provided |
| `slack_log` | string | No | - | Slack channel ID for verbose workflow start/error notifications |
| `slack_alert` | string | No | - | Slack channel ID for error-only notifications |

**Input Processing Flow:**

```mermaid
graph TB
    Workflows["workflows input<br/>(required)"]
    Override["allow_override input"]
    Matrix["matrix_file input<br/>(default: ci/matrix.yaml)"]
    Changes["inspect_changes_script<br/>+ base_sha"]
    
    Workflows --> BuildPy["build-workflow.py"]
    Override --> BuildPy
    Matrix --> BuildPy
    Changes --> InspectStep["Inspect changes step"]
    
    InspectStep -->|"dirty_projects"| BuildPy
    BuildPy --> Output["workflow.json<br/>job_ids.json<br/>runner_summary.json"]
    Output --> PrepareDisp["prepare-workflow-dispatch.py"]
    PrepareDisp --> Final["dispatch.json"]
```

Sources: [.github/actions/workflow-build/action.yml:4-36]()

### Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `workflow` | JSON string | Complete dispatch configuration as a JSON string containing the contents of `dispatch.json`. Contains four arrays: `linux_standalone`, `linux_two_stage`, `windows_standalone`, and `windows_two_stage` |

**Output Structure Mapping:**

```mermaid
graph TB
    subgraph "workflow Output"
        Output["WORKFLOW output<br/>(JSON string)"]
    end
    
    subgraph "Dispatch JSON Structure"
        LinuxStandalone["linux_standalone[]<br/>Standalone Linux jobs"]
        LinuxTwoStage["linux_two_stage[]<br/>Producer/consumer chains"]
        WindowsStandalone["windows_standalone[]<br/>Standalone Windows jobs"]
        WindowsTwoStage["windows_two_stage[]<br/>Producer/consumer chains"]
    end
    
    Output --> LinuxStandalone
    Output --> LinuxTwoStage
    Output --> WindowsStandalone
    Output --> WindowsTwoStage
    
    LinuxStandalone --> DispatchWF1["workflow-dispatch-<br/>standalone-group-linux"]
    LinuxTwoStage --> DispatchWF2["workflow-dispatch-<br/>two-stage-group-linux"]
    WindowsStandalone --> DispatchWF3["workflow-dispatch-<br/>standalone-group-windows"]
    WindowsTwoStage --> DispatchWF4["workflow-dispatch-<br/>two-stage-group-windows"]
```

The `workflow` output is a JSON-encoded string that must be parsed by consuming workflows. It is generated at [.github/actions/workflow-build/action.yml:115-117]() and contains the consolidated dispatch configuration.

Sources: [.github/actions/workflow-build/action.yml:38-41](), [.github/actions/workflow-build/action.yml:111-117]()

### Workflow Steps and Artifacts

The action executes the following steps in sequence:

1. **Send Slack log notification** ([.github/actions/workflow-build/action.yml:47-59]()) - Sends workflow start notification if Slack credentials are provided
2. **Inspect changes** ([.github/actions/workflow-build/action.yml:61-72]()) - Runs change detection script to identify dirty projects
3. **Parse matrix file** ([.github/actions/workflow-build/action.yml:74-100]()) - Executes `build-workflow.py` to generate `workflow.json`
4. **Create dispatch workflows** ([.github/actions/workflow-build/action.yml:102-109]()) - Executes `prepare-workflow-dispatch.py` to create `dispatch.json`
5. **Set outputs** ([.github/actions/workflow-build/action.yml:111-117]()) - Exports the `WORKFLOW` output
6. **Upload artifacts** ([.github/actions/workflow-build/action.yml:119-124]()) - Uploads the `workflow/` directory as an artifact
7. **Send Slack error notification** ([.github/actions/workflow-build/action.yml:126-139]()) - Sends error notification on failure

**Uploaded Artifacts:**

The action uploads a `workflow` artifact containing:
- `workflow.json` - Complete job definitions
- `dispatch.json` - Jobs categorized for dispatch
- `job_ids.json` - Job ID mappings
- `runner_summary.json` - Runner allocation summary
- `job_list.txt` - Human-readable job list
- `changes.md` - Change detection summary (if `inspect_changes_script` was used)

Sources: [.github/actions/workflow-build/action.yml:44-140]()

---

## workflow-results Action

The `workflow-results` action collects job artifacts, analyzes execution results, generates comprehensive summaries, and sends notifications to multiple channels.

**Location**: [.github/actions/workflow-results/action.yml:1-213]()

### Inputs

| Input Name | Type | Required | Default | Description |
|------------|------|----------|---------|-------------|
| `github_token` | string | No | - | GitHub token for API access. Required for fetching job timing data and posting PR comments. No PR comment is made if not provided |
| `pr_number` | string | No | - | Pull request number to comment on. Must be provided along with `github_token` for PR commenting to occur |
| `slack_token` | string | No | - | Slack bot token for sending notifications. No notifications are sent if not provided |
| `slack_log` | string | No | - | Slack channel ID for verbose notifications (always sent with workflow results) |
| `slack_alert` | string | No | - | Slack channel ID for alert notifications (only sent on failure) |

**Input Usage Matrix:**

| Feature | Required Inputs | Optional | Behavior |
|---------|----------------|----------|----------|
| PR Comment | `github_token`, `pr_number` | - | Posts formatted summary as PR comment |
| Job Timing Analysis | `github_token` | - | Fetches job data from GitHub API; timing analysis skipped if not provided |
| Slack Log Notification | `slack_token`, `slack_log` | - | Sends summary to log channel on workflow completion (always) |
| Slack Alert Notification | `slack_token`, `slack_alert` | - | Sends summary to alert channel on workflow failure only |

Sources: [.github/actions/workflow-results/action.yml:4-19]()

### Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `success` | boolean | String value `"true"` or `"false"` indicating whether all jobs succeeded. Set to `"false"` if any job failed or if the override matrix was used |

**Success Determination Logic:**

```mermaid
graph TD
    Start["Check for job success<br/>verify-job-success.py"]
    
    Start --> CheckMarkers{"All jobs have<br/>success markers?"}
    CheckMarkers -->|"No"| Fail1["success=false<br/>exit 1"]
    CheckMarkers -->|"Yes"| CheckOverride{"Override matrix<br/>exists?"}
    
    CheckOverride -->|"Yes"| Fail2["success=false<br/>exit 1<br/>(override detected)"]
    CheckOverride -->|"No"| Success["success=true<br/>exit 0"]
    
    Fail1 --> Output["Output:<br/>success"]
    Fail2 --> Output
    Success --> Output
```

The `success` output is determined at [.github/actions/workflow-results/action.yml:155-177]() by checking for `success` marker files in job artifacts and detecting override matrix usage.

Sources: [.github/actions/workflow-results/action.yml:21-24](), [.github/actions/workflow-results/action.yml:155-177]()

### Workflow Steps and Data Flow

The action executes a multi-stage pipeline with error tolerance (`continue-on-error: true` for most steps):

```mermaid
graph TB
    Download1["Download workflow artifacts<br/>(workflow)"]
    Download2["Download job artifacts<br/>(jobs-*)"]
    Cleanup["Clean up job artifacts<br/>(dos2unix)"]
    FetchJobs["Fetch workflow job info<br/>(GitHub API)"]
    ParseTimes["Parse job times<br/>(parse-job-times.py)"]
    PrepExec["Prepare execution summary<br/>(prepare-execution-summary.py)"]
    FinalSum["Prepare final summary<br/>(final-summary.py)"]
    Comment["Comment on PR"]
    CheckSuccess["Check for job success<br/>(verify-job-success.py)"]
    SlackLog["Send Slack log notification"]
    SlackAlert["Send Slack alert notification"]
    
    Download1 --> Download2
    Download2 --> Cleanup
    Cleanup --> FetchJobs
    FetchJobs --> ParseTimes
    ParseTimes --> PrepExec
    PrepExec --> FinalSum
    FinalSum --> Comment
    FinalSum --> CheckSuccess
    CheckSuccess --> SlackLog
    CheckSuccess --> SlackAlert
    
    style Download1 fill:#e1f5ff
    style CheckSuccess fill:#ffe1e1
```

**Step Details:**

1. **Download workflow artifacts** ([.github/actions/workflow-results/action.yml:30-34]()) - Downloads the `workflow` artifact uploaded by `workflow-build`
2. **Download job artifacts** ([.github/actions/workflow-results/action.yml:36-42]()) - Downloads all `jobs-*` artifacts with pattern matching and merging
3. **Clean up job artifacts** ([.github/actions/workflow-results/action.yml:44-57]()) - Fixes Windows line endings using `dos2unix`
4. **Fetch workflow job info** ([.github/actions/workflow-results/action.yml:59-90]()) - Calls GitHub API to get job timing data, saved to `results/jobs.json`
5. **Parse job times** ([.github/actions/workflow-results/action.yml:92-97]()) - Executes `parse-job-times.py` to extract timing information
6. **Prepare execution summary** ([.github/actions/workflow-results/action.yml:99-104]()) - Executes `prepare-execution-summary.py` to aggregate results by project/tag
7. **Prepare final summary** ([.github/actions/workflow-results/action.yml:106-128]()) - Executes `final-summary.py` to generate HTML/Markdown report
8. **Comment on PR** ([.github/actions/workflow-results/action.yml:130-153]()) - Posts the final summary as a PR comment if credentials are provided
9. **Check for job success** ([.github/actions/workflow-results/action.yml:155-177]()) - Verifies all jobs have success markers
10. **Send Slack log notification** ([.github/actions/workflow-results/action.yml:179-195]()) - Sends summary to log channel (always runs if configured)
11. **Send Slack alert notification** ([.github/actions/workflow-results/action.yml:197-212]()) - Sends alert to alert channel (only on failure)

Sources: [.github/actions/workflow-results/action.yml:26-213]()

### Intermediate Data Files

The action generates several intermediate files in the `results/` and `execution/` directories:

| File Path | Generator | Purpose |
|-----------|-----------|---------|
| `results/jobs.json` | GitHub API fetch | Raw job data from GitHub Actions |
| `results/job_times.json` | `parse-job-times.py` | Extracted timing information |
| `execution/heading.txt` | `prepare-execution-summary.py` | Overall execution summary |
| `execution/projects/*_summary.json` | `prepare-execution-summary.py` | Per-project detailed summaries |
| `final_summary.md` | `final-summary.py` | Complete formatted report |

Sources: [.github/actions/workflow-results/action.yml:59-128]()

---

## workflow-run-job-linux Action

The `workflow-run-job-linux` action executes individual jobs on Linux runners using a Docker-outside-of-Docker (DOOD) pattern to launch job-specific devcontainers.

**Location**: [.github/actions/workflow-run-job-linux/action.yml:1-201]()

**Architecture Overview:**

The action uses a three-layer execution model:
1. **GitHub Actions Runner Host** - Provides the Docker daemon and GPU access
2. **Intermediate Container** (`cruizba/ubuntu-dind:jammy-26.1.3`) - Has Docker CLI, mounts host socket
3. **Target Devcontainer** - Job-specific image selected by `.devcontainer/launch.sh`

Sources: [.github/actions/workflow-run-job-linux/action.yml:4-20]()

### Inputs

| Input Name | Type | Required | Description |
|------------|------|----------|-------------|
| `id` | string | **Yes** | Unique identifier for the job, used for artifact naming and organization |
| `command` | string | **Yes** | The shell command to execute inside the devcontainer |
| `image` | string | **Yes** | Docker image identifier (used by `.devcontainer/launch.sh` for image selection, not directly as a Docker image) |
| `runner` | string | **Yes** | The GitHub Actions `runs-on` value, used to detect GPU availability (e.g., `"linux-amd64-gpu-v100-latest-1"`) |
| `cuda` | string | **Yes** | CUDA version for devcontainer selection (e.g., `"12.4"`) |
| `host` | string | **Yes** | Host compiler for devcontainer selection (e.g., `"gcc12"`) |

**Input Usage in Execution Flow:**

```mermaid
graph LR
    ID["id input"]
    Command["command input"]
    Image["image input"]
    Runner["runner input"]
    CUDA["cuda input"]
    Host["host input"]
    
    ID --> Artifacts["Artifact naming:<br/>jobs-{id}"]
    Command --> CIScript["ci.sh wrapper<br/>script"]
    Image --> Launch["launch.sh<br/>(unused)"]
    Runner --> GPUCheck{"Runner contains<br/>'gpu'?"}
    CUDA --> Launch
    Host --> Launch
    
    GPUCheck -->|"Yes"| GPUFlag["--gpus device=<br/>$NVIDIA_VISIBLE_DEVICES"]
    GPUCheck -->|"No"| NoGPU["No GPU flag"]
    
    Launch --> DevContainer["Selected devcontainer"]
    CIScript --> DevContainer
    GPUFlag --> DevContainer
    NoGPU --> DevContainer
```

Sources: [.github/actions/workflow-run-job-linux/action.yml:22-40]()

### Outputs

This action has no explicit outputs. Success is communicated through:
- **Artifact upload**: A `jobs-{id}` artifact containing a `success` marker file
- **Job status**: The step's exit code determines workflow success/failure

Sources: [.github/actions/workflow-run-job-linux/action.yml:42]()

### Execution Steps

The action performs the following operations:

1. **Install dependencies** ([.github/actions/workflow-run-job-linux/action.yml:45-50]()) - Installs `tree` and `git` in the `ubuntu-dind` container
2. **Checkout repo** ([.github/actions/workflow-run-job-linux/action.yml:51-55]()) - Clones the repository into a subdirectory
3. **Add NVCC problem matcher** ([.github/actions/workflow-run-job-linux/action.yml:56-59]()) - Registers problem matcher for CUDA compiler errors
4. **Get AWS credentials** ([.github/actions/workflow-run-job-linux/action.yml:60-65]()) - Assumes AWS role for sccache S3 bucket access
5. **Run command** ([.github/actions/workflow-run-job-linux/action.yml:66-164]()) - Executes the job in a devcontainer
6. **Prepare job artifacts** ([.github/actions/workflow-run-job-linux/action.yml:166-193]()) - Collects output files
7. **Upload job artifacts** ([.github/actions/workflow-run-job-linux/action.yml:195-200]()) - Uploads the `jobs-{id}` artifact

**Key Implementation Details:**

### Path Management and DOOD Symlink Strategy

The action implements a critical path synchronization mechanism for DOOD:

```mermaid
graph TB
    HostWS["Host:<br/>${{github.workspace}}<br/>/home/runner/work/repo/repo"]
    ContainerPWD["Container:<br/>$(pwd)<br/>/__w/repo/repo"]
    Symlink["Symlink created:<br/>${{github.workspace}}<br/>→ $(pwd)"]
    
    HostWS -.->|"Actions sets this"| Context["GitHub Actions<br/>Context"]
    ContainerPWD -.->|"Container's actual path"| Context
    
    Context --> Symlink
    Symlink --> LaunchSh["launch.sh uses:<br/>$(pwd) for volume mounts"]
    LaunchSh --> HostDocker["Host Docker daemon<br/>receives host paths"]
    
    style Symlink fill:#ffe1e1
```

The symlink is created at [.github/actions/workflow-run-job-linux/action.yml:82-86]() to ensure that when `.devcontainer/launch.sh` constructs volume mount paths using `$(pwd)`, they match the host's path structure, which is necessary because the Docker CLI runs in the intermediate container but the daemon runs on the host.

Sources: [.github/actions/workflow-run-job-linux/action.yml:77-86]()

### Command Wrapper Script Generation

The action generates a `ci.sh` wrapper script ([.github/actions/workflow-run-job-linux/action.yml:89-109]()) that:
- Sets error handling with `set -eo pipefail`
- Prints the command being executed
- Executes the command from the `COMMAND` environment variable
- On failure, prints detailed reproduction instructions including:
  - Git clone command with correct branch and SHA
  - `.devcontainer/launch.sh` invocation with exact parameters
  - Links to documentation

Sources: [.github/actions/workflow-run-job-linux/action.yml:89-109]()

### AWS Credentials Configuration

AWS credentials are written to `$RUNNER_TEMP/.aws/` ([.github/actions/workflow-run-job-linux/action.yml:113-129]()):

```
$RUNNER_TEMP/.aws/
├── config          (mode 0664)
│   └── [default]
│       ├── bucket=rapids-sccache-devs
│       └── region=us-east-2
└── credentials     (mode 0600)
    └── [default]
        ├── aws_access_key_id
        ├── aws_session_token
        └── aws_secret_access_key
```

These files are mounted into the devcontainer at `/root/.aws/` ([.github/actions/workflow-run-job-linux/action.yml:162]()).

Sources: [.github/actions/workflow-run-job-linux/action.yml:113-129](), [.github/actions/workflow-run-job-linux/action.yml:162]()

### GPU Detection and Allocation

GPU access is conditional based on the `runner` input ([.github/actions/workflow-run-job-linux/action.yml:131-136]()):

```bash
declare -a gpu_request=()

if [[ "${RUNNER}" = *"-gpu-"* ]]; then
  gpu_request+=(--gpus "device=${NVIDIA_VISIBLE_DEVICES}")
fi
```

The `NVIDIA_VISIBLE_DEVICES` environment variable is provided by the GitHub runner and specifies which GPU device(s) should be visible to the container.

Sources: [.github/actions/workflow-run-job-linux/action.yml:131-136]()

### Environment Variable Propagation

The action explicitly propagates GitHub Actions context variables to the devcontainer ([.github/actions/workflow-run-job-linux/action.yml:149-160]()):

| Variable | Purpose |
|----------|---------|
| `CI` | Signals CI environment to scripts |
| `COMMAND` | Contains the command to execute |
| `GITHUB_SHA` | Current commit SHA |
| `GITHUB_REF_NAME` | Branch or tag name |
| `GITHUB_REPOSITORY` | Repository full name (`owner/repo`) |
| `GITHUB_WORKSPACE` | Workspace path for actions |
| `GITHUB_ACTIONS` | Indicates running in GitHub Actions |
| `GITHUB_ENV` | Path to environment file |
| `GITHUB_PATH` | Path to PATH modification file |
| `GITHUB_OUTPUT` | Path to output file |
| `GITHUB_STEP_SUMMARY` | Path to step summary file |

Sources: [.github/actions/workflow-run-job-linux/action.yml:149-160]()

### Artifact Collection

The action searches for specific output files ([.github/actions/workflow-run-job-linux/action.yml:176-189]()):

| Filename | Purpose | Failure Behavior |
|----------|---------|------------------|
| `success` | Created unconditionally to mark job success | Always created |
| `sccache_stats.json` | sccache compilation statistics | Ignored if missing |
| `cccl_meta_bench.csv` | Benchmark results (CSV) | Ignored if missing |
| `cccl_meta_bench.db` | Benchmark database | Ignored if missing |
| `cccl_meta_bench.log` | Benchmark logs | Ignored if missing |

Files are copied from anywhere in the repository to `jobs/{id}/` using a `find` command with `-print -quit` to select the first match.

Sources: [.github/actions/workflow-run-job-linux/action.yml:166-193]()

---

## workflow-run-job-windows Action

The `workflow-run-job-windows` action executes individual jobs on Windows runners using Docker containers with native Windows execution.

**Location**: [.github/actions/workflow-run-job-windows/action.yml:1-99]()

### Inputs

| Input Name | Type | Required | Description |
|------------|------|----------|-------------|
| `id` | string | **Yes** | Unique identifier for the job, used for artifact naming |
| `command` | string | **Yes** | PowerShell command to execute inside the Docker container |
| `image` | string | **Yes** | Full Docker image name to use (e.g., `"rapidsai/devcontainers:24.12-cpp-msvc2022-cuda12.6"`) |

**Comparison with Linux Action:**

| Feature | Linux Action | Windows Action |
|---------|--------------|----------------|
| **Container Strategy** | DOOD with intermediate container | Direct Docker execution |
| **Image Selection** | Via `cuda` + `host` inputs and `launch.sh` | Direct image name |
| **Path Management** | Complex symlink strategy | PowerShell path transformation |
| **GPU Access** | Via `--gpus` flag | Not implemented |
| **Shell** | Bash in devcontainer | PowerShell in container |

Sources: [.github/actions/workflow-run-job-windows/action.yml:4-13]()

### Outputs

This action has no explicit outputs. Success is communicated identically to the Linux action through artifact upload and job exit code.

Sources: [.github/actions/workflow-run-job-windows/action.yml:15]()

### Execution Steps

The action performs the following operations:

1. **Configure env** ([.github/actions/workflow-run-job-windows/action.yml:18-25]()) - Sets sccache environment variables
2. **Get AWS credentials** ([.github/actions/workflow-run-job-windows/action.yml:26-31]()) - Assumes AWS role for sccache access
3. **Checkout repo** ([.github/actions/workflow-run-job-windows/action.yml:32-36]()) - Clones the repository
4. **Fetch image** ([.github/actions/workflow-run-job-windows/action.yml:37-39]()) - Pulls the specified Docker image
5. **Prepare paths** ([.github/actions/workflow-run-job-windows/action.yml:40-46]()) - Converts Windows paths for Docker
6. **Run command** ([.github/actions/workflow-run-job-windows/action.yml:47-64]()) - Executes the command in the container
7. **Prepare job artifacts** ([.github/actions/workflow-run-job-windows/action.yml:65-91]()) - Collects output files
8. **Upload job artifacts** ([.github/actions/workflow-run-job-windows/action.yml:93-98]()) - Uploads the `jobs-{id}` artifact

### sccache Environment Configuration

The action sets sccache environment variables ([.github/actions/workflow-run-job-windows/action.yml:18-25]()):

| Variable | Value | Purpose |
|----------|-------|---------|
| `SCCACHE_BUCKET` | `rapids-sccache-devs` | S3 bucket name |
| `SCCACHE_REGION` | `us-east-2` | AWS region |
| `SCCACHE_IDLE_TIMEOUT` | `0` | Disable idle timeout |
| `SCCACHE_S3_USE_SSL` | `true` | Use HTTPS for S3 |
| `SCCACHE_S3_NO_CREDENTIALS` | `false` | Use provided credentials |

These are set in `GITHUB_ENV` and then propagated into the container via PowerShell's `SetEnvironmentVariable` calls ([.github/actions/workflow-run-job-windows/action.yml:55-62]()).

Sources: [.github/actions/workflow-run-job-windows/action.yml:18-25](), [.github/actions/workflow-run-job-windows/action.yml:55-62]()

### Path Transformation for Docker

Windows paths are transformed for Docker compatibility ([.github/actions/workflow-run-job-windows/action.yml:40-46]()):

```powershell
# Input:  C:\actions-runner\_work\cccl\cccl\cccl
# Output: C:/actions-runner/_work/cccl/cccl/cccl
HOST_REPO=${{ github.workspace }}\${{ github.event.repository.name }}".Replace('\', '/')

# Target mount path in container:
MOUNT_REPO=C:/${{ github.event.repository.name }}
```

The host path is mounted to a simplified path inside the container at [.github/actions/workflow-run-job-windows/action.yml:51]():

```bash
docker run \
  --mount type=bind,source="{HOST_REPO}",target="{MOUNT_REPO}" \
  --workdir "{MOUNT_REPO}" \
  {image} \
  powershell -c "{command}"
```

Sources: [.github/actions/workflow-run-job-windows/action.yml:40-64]()

### Environment Variable Injection

AWS credentials and sccache configuration are injected via PowerShell commands inside the container ([.github/actions/workflow-run-job-windows/action.yml:54-64]()):

```powershell
[System.Environment]::SetEnvironmentVariable('AWS_ACCESS_KEY_ID', '...');
[System.Environment]::SetEnvironmentVariable('AWS_SECRET_ACCESS_KEY', '...');
[System.Environment]::SetEnvironmentVariable('AWS_SESSION_TOKEN', '...');
[System.Environment]::SetEnvironmentVariable('SCCACHE_BUCKET', '...');
# ... etc
```

This approach is necessary because Windows Docker containers don't support the `--env` flag in the same way as Linux containers when using PowerShell commands.

Sources: [.github/actions/workflow-run-job-windows/action.yml:54-64]()

### Artifact Collection Differences

The Windows action collects fewer artifacts than the Linux action ([.github/actions/workflow-run-job-windows/action.yml:76-87]()):

| Artifact | Linux | Windows | Reason |
|----------|-------|---------|--------|
| `success` | ✓ | ✓ | Required marker |
| `sccache_stats.json` | ✓ | ✓ | Common output |
| `cccl_meta_bench.csv` | ✓ | ✗ | Not generated on Windows |
| `cccl_meta_bench.db` | ✓ | ✗ | Not generated on Windows |
| `cccl_meta_bench.log` | ✓ | ✗ | Not generated on Windows |

The Windows action also uses `find` instead of `tree` for listing artifacts due to tool availability ([.github/actions/workflow-run-job-windows/action.yml:89-91]()).

Sources: [.github/actions/workflow-run-job-windows/action.yml:65-91]()

---

## Action Dependency Graph

The following diagram shows how actions depend on each other and external systems:

```mermaid
graph TB
    subgraph "External Inputs"
        MatrixYAML["matrix.yaml<br/>(consumer repo)"]
        InspectScript["inspect-changes<br/>script"]
        GitHubAPI["GitHub Actions API"]
        SlackAPI["Slack API"]
        AWSS3["AWS S3<br/>(sccache)"]
    end
    
    subgraph "workflow-build Action"
        BuildAction["workflow-build<br/>composite action"]
        BuildPy["build-workflow.py"]
        PreparePy["prepare-workflow-dispatch.py"]
    end
    
    subgraph "Execution Actions"
        LinuxAction["workflow-run-job-linux"]
        WindowsAction["workflow-run-job-windows"]
        LaunchSh["launch.sh<br/>(Linux only)"]
        DevContainers["Devcontainer Images"]
    end
    
    subgraph "workflow-results Action"
        ResultsAction["workflow-results<br/>composite action"]
        ParseTimes["parse-job-times.py"]
        PrepareExec["prepare-execution-summary.py"]
        FinalSum["final-summary.py"]
        VerifySuccess["verify-job-success.py"]
    end
    
    MatrixYAML --> BuildAction
    InspectScript --> BuildAction
    BuildAction --> BuildPy
    BuildPy --> PreparePy
    
    BuildAction -->|"dispatch.json"| DispatchWF["Dispatch Workflows"]
    DispatchWF --> LinuxAction
    DispatchWF --> WindowsAction
    
    LinuxAction --> LaunchSh
    LaunchSh --> DevContainers
    LinuxAction --> AWSS3
    WindowsAction --> AWSS3
    
    LinuxAction -->|"job artifacts"| ResultsAction
    WindowsAction -->|"job artifacts"| ResultsAction
    GitHubAPI --> ResultsAction
    
    ResultsAction --> ParseTimes
    ResultsAction --> PrepareExec
    ResultsAction --> FinalSum
    ResultsAction --> VerifySuccess
    
    BuildAction -.->|"notifications"| SlackAPI
    ResultsAction -.->|"notifications"| SlackAPI
    ResultsAction -.->|"PR comments"| GitHubAPI
```

Sources: [.github/actions/workflow-build/action.yml](), [.github/actions/workflow-results/action.yml](), [.github/actions/workflow-run-job-linux/action.yml](), [.github/actions/workflow-run-job-windows/action.yml]()

---

## Summary of Critical Input/Output Patterns

### Required Input Combinations

The following table summarizes which input combinations are required for common use cases:

| Use Case | Required Inputs | Optional Inputs |
|----------|----------------|-----------------|
| **Basic workflow generation** | `workflows` (build), `matrix_file` | `matrix_parser`, `allow_override` |
| **Change-based filtering** | `workflows`, `inspect_changes_script`, `inspect_changes_base_sha` | - |
| **Slack notifications** | `slack_token`, `slack_log` or `slack_alert` | - |
| **Linux job execution** | `id`, `command`, `image`, `runner`, `cuda`, `host` | - |
| **Linux job with GPU** | All Linux inputs, `runner` containing `"-gpu-"` | - |
| **Windows job execution** | `id`, `command`, `image` | - |
| **Results with PR comment** | `github_token`, `pr_number` | - |
| **Results with job timing** | `github_token` | `pr_number` |
| **Results with Slack** | `slack_token`, `slack_log` or `slack_alert` | - |

### Data Flow Between Actions

```mermaid
graph LR
    subgraph "Build Phase"
        BuildIn["workflows input"]
        BuildOut["workflow output<br/>(dispatch.json)"]
    end
    
    subgraph "Execution Phase"
        ExecIn["Job parameters<br/>(id, command, etc.)"]
        ExecOut["Artifact:<br/>jobs-{id}/success"]
    end
    
    subgraph "Results Phase"
        ResultsIn["Job artifacts"]
        ResultsOut["success output<br/>(true/false)"]
    end
    
    BuildIn --> BuildOut
    BuildOut -.->|"via workflow.json<br/>in dispatch workflows"| ExecIn
    ExecIn --> ExecOut
    ExecOut --> ResultsIn
    ResultsIn --> ResultsOut
    
    BuildOut -.->|"uploaded artifact:<br/>workflow/"| ResultsIn
```

**Key Integration Points:**

1. **Build → Dispatch**: The `workflow` output from `workflow-build` is parsed by dispatch workflows to create job matrices
2. **Build → Results**: The `workflow` artifact contains `workflow.json` and `job_ids.json`, which are downloaded by `workflow-results`
3. **Execution → Results**: Each execution action uploads a `jobs-{id}` artifact that is downloaded by `workflow-results`
4. **Results → Caller**: The `success` output from `workflow-results` determines the overall workflow status

Sources: [.github/actions/workflow-build/action.yml:38-41](), [.github/actions/workflow-run-job-linux/action.yml:195-200](), [.github/actions/workflow-run-job-windows/action.yml:93-98](), [.github/actions/workflow-results/action.yml:21-24]()

---

# Page: File Format Specifications

# File Format Specifications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)
- [.github/actions/workflow-build/prepare-workflow-dispatch.py](.github/actions/workflow-build/prepare-workflow-dispatch.py)
- [.github/actions/workflow-results/parse-job-times.py](.github/actions/workflow-results/parse-job-times.py)

</details>



This page documents the schemas and formats of all configuration files, generated artifacts, and intermediate data structures used throughout the cccl-gha workflow orchestration system. For information about how these files are generated and processed, see [Workflow Generation](#3). For details on artifact collection, see [Artifact Collection](#6.1).

---

## File Lifecycle Overview

The following diagram shows how files flow through the system, from input configuration to final outputs:

```mermaid
graph LR
    subgraph "Input Configuration"
        MatrixYAML["matrix.yaml"]
    end
    
    subgraph "Workflow Generation (build-workflow.py)"
        WorkflowJSON["workflow.json"]
        JobIdsJSON["job_ids.json"]
        RunnerSummaryJSON["runner_summary.json"]
        JobListTXT["job_list.txt"]
    end
    
    subgraph "Dispatch Preparation (prepare-workflow-dispatch.py)"
        DispatchJSON["dispatch.json"]
    end
    
    subgraph "Job Execution Artifacts"
        SuccessMarker["jobs/{id}/success"]
        SccacheStats["jobs/{id}/sccache_stats.json"]
        BenchData["jobs/{id}/cccl_meta_bench.csv"]
    end
    
    subgraph "Results Processing"
        JobsJSON["jobs.json<br/>(GitHub API)"]
        JobTimesJSON["results/job_times.json"]
        ExecutionSummary["execution/*_summary.json"]
    end
    
    MatrixYAML --> WorkflowJSON
    WorkflowJSON --> JobIdsJSON
    WorkflowJSON --> RunnerSummaryJSON
    WorkflowJSON --> JobListTXT
    WorkflowJSON --> DispatchJSON
    
    DispatchJSON -.-> SuccessMarker
    DispatchJSON -.-> SccacheStats
    DispatchJSON -.-> BenchData
    
    WorkflowJSON --> JobTimesJSON
    JobsJSON --> JobTimesJSON
    JobTimesJSON --> ExecutionSummary
    SuccessMarker --> ExecutionSummary
    SccacheStats --> ExecutionSummary
```

Sources: [.github/actions/workflow-build/build-workflow.py:979-1024](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:59-76](), [.github/actions/workflow-results/parse-job-times.py:48-112]()

---

## Input Configuration Files

### matrix.yaml

The `matrix.yaml` file is the primary input configuration that defines all possible job combinations. It is located at `ci/matrix.yaml` in the consuming repository.

**Top-Level Structure:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `devcontainer_version` | string | Yes | Version tag for devcontainer images |
| `all_stds` | list[int] | Yes | All C++ standard versions supported system-wide |
| `workflows` | object | Yes | Named workflow definitions (e.g., `pull_request`, `nightly`) |
| `exclude` | list[object] | No | Matrix jobs to exclude (special workflow name) |
| `override` | list[object] | No | Override matrix (replaces all workflows if present) |
| `projects` | object | Yes | Project definitions (libcudacxx, cub, thrust, etc.) |
| `ctk_versions` | object | Yes | CUDA Toolkit version definitions |
| `host_compilers` | object | Yes | Host compiler definitions (gcc, clang, msvc) |
| `device_compilers` | object | Yes | Device compiler definitions (nvcc, clang) |
| `gpus` | object | Yes | GPU configuration definitions |
| `jobs` | object | Yes | Job type definitions (build, test, etc.) |
| `tags` | object | Yes | Tag metadata (required, defaults, validation) |

**Example Structure:**

```yaml
devcontainer_version: "24.06"
all_stds: [11, 14, 17, 20]

workflows:
  pull_request:
    - {project: libcudacxx, ctk: "12.4", cxx: gcc12, gpu: v100, std: all, jobs: [build, test]}
    - {project: cub, ctk: "11.1", cxx: [gcc9, gcc10], std: 17}
  
exclude:
  - {ctk: "11.1", cxx: gcc12}

projects:
  libcudacxx:
    name: "libcu++"
    stds: [11, 14, 17, 20]
    job_map:
      verify: [build, test]

ctk_versions:
  "11.1":
    stds: [11, 14, 17]
    aka: "11"
  "12.4":
    stds: [11, 14, 17, 20, 23]

host_compilers:
  gcc:
    name: "GCC"
    exe: "g++"
    container_tag: "gcc"
    versions:
      "9":
        stds: [11, 14, 17]
      "12":
        stds: [11, 14, 17, 20, 23]
        aka: "latest"

device_compilers:
  nvcc:
    name: "nvcc"
    exe: "nvcc"
  clang:
    name: "clang"
    exe: "clang++"

gpus:
  v100:
    sm: "70"
    testing: false
  t4:
    sm: "75"

jobs:
  build:
    name: "Build"
    gpu: false
    invoke:
      prefix: "build"
      args: ""
  test:
    name: "Test"
    gpu: true
    needs: build
    invoke:
      prefix: "test"

tags:
  project:
    required: true
  ctk:
    required: true
  cxx:
    required: true
  std:
    default: 17
  gpu:
    required: false
  jobs:
    required: true
```

**Matrix Job Format:**

Each entry in a workflow array becomes a "matrix job" after preprocessing. Matrix jobs support list expansion:

```yaml
# Input (compact)
- {project: [libcudacxx, cub], std: [17, 20], cxx: gcc12}

# Expands to 4 jobs (2 projects × 2 stds)
```

**Special Tag Values:**

- `std: all` - Expands to intersection of supported standards across CTK/compiler/project
- `sm: gpu` - Derives SM architecture from the `gpu` tag value

Sources: [.github/actions/workflow-build/build-workflow.py:1-54](), [.github/actions/workflow-build/build-workflow.py:113-337](), [.github/actions/workflow-build/build-workflow.py:834-876]()

---

## Generated Workflow Files

### workflow.json

Generated by `build-workflow.py`, this file contains the complete set of dispatch groups with fully specified job definitions.

**Structure:**

```json
{
  "<group_name>": {
    "standalone": [
      {
        "id": "<guid>",
        "name": "<human_readable_name>",
        "runner": "<runner_label>",
        "image": "<docker_image>",
        "command": "<shell_command>",
        "cuda": "<ctk_version>",
        "host": "<host_compiler_tag>",
        "origin": {
          "filename": "ci/matrix.yaml",
          "workflow_name": "pull_request",
          "workflow_location": "ci/matrix.yaml:42 (job 1)",
          "original_matrix_job": "{project: libcudacxx, ...}",
          "matrix_job": {
            "project": "libcudacxx",
            "jobs": "Build",
            "cxx": "GCC12",
            "cxx_family": "GCC",
            "cudacxx": "nvcc12.4",
            "cudacxx_family": "nvcc",
            "ctk": "12.4",
            "std": 17
          }
        }
      }
    ],
    "two_stage": [
      {
        "id": "<guid>",
        "producers": [
          {
            "id": "<guid>",
            "name": "<producer_name>",
            "runner": "<runner_label>",
            "image": "<docker_image>",
            "command": "<build_command>",
            "cuda": "<ctk_version>",
            "host": "<host_compiler_tag>",
            "origin": { /* same as above */ }
          }
        ],
        "consumers": [
          {
            "id": "<guid>",
            "name": "<consumer_name>",
            "runner": "<runner_label>",
            "image": "<docker_image>",
            "command": "<test_command>",
            "cuda": "<ctk_version>",
            "host": "<host_compiler_tag>",
            "origin": { /* same as above */ }
          }
        ]
      }
    ]
  }
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Compact unique identifier (1-3 chars, base64-encoded) |
| `name` | string | Human-readable job name for UI display |
| `runner` | string | GitHub Actions runner label (e.g., `linux-amd64-gpu-v100-latest-1`) |
| `image` | string | Full Docker image path (e.g., `rapidsai/devcontainers:24.06-cpp-gcc12-cuda12.4`) |
| `command` | string | Shell command to execute (e.g., `"./ci/build_libcudacxx.sh -std "17""`) |
| `cuda` | string | CUDA Toolkit version for devcontainer selection |
| `host` | string | Host compiler tag for devcontainer selection |
| `origin` | object | Traceability information linking back to matrix.yaml |

**Group Name Format:**

Group names follow the pattern: `<project_name> CTK<version> <compiler_info>`

Examples:
- `libcu++ CTK12.4 nvcc GCC`
- `CUB CTK11.1 clang`

Sources: [.github/actions/workflow-build/build-workflow.py:28-54](), [.github/actions/workflow-build/build-workflow.py:481-505](), [.github/actions/workflow-build/build-workflow.py:583-721]()

---

### dispatch.json

Generated by `prepare-workflow-dispatch.py`, this file reorganizes `workflow.json` into four categories to optimize GitHub Actions UI presentation.

**Structure:**

```json
{
  "linux_standalone": {
    "keys": ["<group_name_1>", "<group_name_2>"],
    "jobs": {
      "<group_name_1>": [
        {
          "id": "<guid>",
          "name": "<job_name>",
          "runner": "linux-amd64-cpu16",
          "image": "rapidsai/devcontainers:24.06-cpp-gcc12-cuda12.4",
          "command": "\"./ci/build_libcudacxx.sh\" -std \"17\"",
          "cuda": "12.4",
          "host": "gcc12"
        }
      ]
    }
  },
  "linux_two_stage": {
    "keys": ["<group_name_3>"],
    "jobs": {
      "<group_name_3>": [
        {
          "id": "<guid>",
          "producers": [ /* job objects without origin */ ],
          "consumers": [ /* job objects without origin */ ]
        }
      ]
    }
  },
  "windows_standalone": {
    "keys": [],
    "jobs": {}
  },
  "windows_two_stage": {
    "keys": [],
    "jobs": {}
  }
}
```

**Categories:**

| Category | Description | Consumed By |
|----------|-------------|-------------|
| `linux_standalone` | Linux jobs without dependencies | `workflow-dispatch-standalone-group-linux.yml` |
| `linux_two_stage` | Linux producer/consumer chains | `workflow-dispatch-two-stage-group-linux.yml` |
| `windows_standalone` | Windows jobs without dependencies | `workflow-dispatch-standalone-group-windows.yml` |
| `windows_two_stage` | Windows producer/consumer chains | `workflow-dispatch-two-stage-group-windows.yml` |

**Key Differences from workflow.json:**

1. Jobs are categorized by OS (Linux/Windows) and execution pattern (standalone/two-stage)
2. The `origin` field is removed from all job objects to reduce file size
3. Group names are duplicated in `keys` arrays for efficient iteration

Sources: [.github/actions/workflow-build/prepare-workflow-dispatch.py:1-96]()

---

### job_ids.json

A simple mapping file for resolving compact job IDs to human-readable names.

**Structure:**

```json
{
  "A": "libcu++ CTK12.4 nvcc GCC [C++17] Build(amd64, V100): sm{70}",
  "AB": "CUB CTK11.1 nvcc GCC C / libcu++ CTK11.1 nvcc GCC [C++17] Test(amd64, T4)",
  "AC": "Thrust CTK12.0 clang [C++20] Build(amd64)"
}
```

**Usage:**

This file is used by results processing scripts to convert job IDs back to full names for display in summaries and error messages.

Sources: [.github/actions/workflow-build/build-workflow.py:979-1024]()

---

### runner_summary.json

A formatted summary of runner allocations for display in GitHub Actions output.

**Structure:**

```json
{
  "heading": "🏃‍ Runner counts (total jobs: 42)",
  "body": "| #    | Runner\n|------|------\n|   15 | `linux-amd64-cpu16`\n|   12 | `linux-amd64-gpu-v100-latest-1`\n|    8 | `linux-amd64-gpu-t4-latest-1`\n|    5 | `windows-amd64-cpu16`\n|    2 | `linux-arm64-cpu16`\n"
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `heading` | string | Summary line with total job count |
| `body` | string | Markdown table with runner counts (sorted by count descending) |

Sources: [.github/actions/workflow-build/build-workflow.py:1010-1023]()

---

### job_list.txt

A plain text listing of all jobs with IDs for debugging and verification.

**Format:**

```
libcu++ CTK12.4 nvcc GCC:
   1 id: A      standalone     [C++17] Build(amd64, V100): sm{70}
   2 id: B      standalone     [C++20] Build(amd64, V100): sm{70}
CUB CTK11.1 nvcc GCC:
   3 id: C      producers      [C++17] Build(amd64)
   4 id: D      consumers      [C++17] Test(amd64, T4)
   5 id: E      consumers      [C++17] Test(amd64, V100)
```

**Columns:**

1. Sequential job number
2. Compact job ID
3. Job type (standalone, producers, consumers)
4. Human-readable job name

Sources: [.github/actions/workflow-build/build-workflow.py:979-1024]()

---

## Job Execution Artifacts

### Success Markers

Success markers are empty files created by jobs to indicate successful completion.

**Path:** `jobs/<job_id>/success`

**Format:** Empty file (0 bytes)

**Purpose:** These files are checked by `verify-job-success.py` to determine overall workflow success. The absence of this file for any job ID indicates failure.

**Creation:** Generated by the `workflow-run-job-*` workflows after successful command execution.

Sources: Referenced in workflow execution context

---

### sccache_stats.json

Statistics about distributed compilation cache usage.

**Path:** `jobs/<job_id>/sccache_stats.json`

**Structure:**

```json
{
  "stats": {
    "compile_requests": 1234,
    "cache_hits": {
      "counts": {
        "Rust": 0,
        "C/C++": 1100
      }
    },
    "cache_misses": {
      "counts": {
        "Rust": 0,
        "C/C++": 134
      }
    },
    "cache_timeouts": {
      "counts": {}
    },
    "cache_errors": {
      "counts": {}
    },
    "cache_write_errors": {
      "counts": {}
    }
  }
}
```

**Derived Metrics:**

The results processing computes:
- `cache_hit_rate` = cache_hits / compile_requests
- `total_hits` = sum of all cache_hits.counts values
- `total_misses` = sum of all cache_misses.counts values

**Usage:** Aggregated by `prepare-execution-summary.py` to show compilation cache effectiveness.

Sources: Referenced in sccache integration context

---

### Benchmark Data

**Path:** `jobs/<job_id>/cccl_meta_bench.csv`

**Format:** CSV file with benchmark results

**Structure:**

```csv
benchmark_name,time_ns,iterations,status
thrust.sort.int32,1234567,1000,passed
cub.device_reduce.sum,987654,500,passed
```

**Columns:**

| Column | Description |
|--------|-------------|
| `benchmark_name` | Fully qualified benchmark identifier |
| `time_ns` | Execution time in nanoseconds |
| `iterations` | Number of iterations run |
| `status` | Pass/fail status |

**Usage:** Used for performance regression analysis (future feature).

Sources: Referenced in benchmark artifact context

---

## Timing and Results Files

### jobs.json (GitHub API)

Retrieved from GitHub Actions API, this file contains metadata about all jobs in a workflow run.

**Retrieval:** Fetched via GitHub API by `workflow-results` action

**Relevant Structure (subset):**

```json
[
  {
    "id": 12345678,
    "name": "libcu++ CTK12.4 nvcc GCC / A / [C++17] Build(amd64, V100): sm{70}",
    "status": "completed",
    "conclusion": "success",
    "started_at": "2024-05-09T06:52:20Z",
    "completed_at": "2024-05-09T06:58:45Z",
    "steps": [
      {
        "name": "Run command",
        "status": "completed",
        "conclusion": "success",
        "started_at": "2024-05-09T06:53:10Z",
        "completed_at": "2024-05-09T06:58:30Z"
      }
    ]
  }
]
```

Sources: [.github/actions/workflow-results/parse-job-times.py:10-22]()

---

### job_times.json

Generated by `parse-job-times.py`, this file contains computed timing statistics for each job.

**Path:** `results/job_times.json`

**Structure:**

```json
{
  "A": {
    "name": "libcu++ CTK12.4 nvcc GCC / A / [C++17] Build(amd64, V100): sm{70}",
    "started_at": "2024-05-09T06:52:20Z",
    "completed_at": "2024-05-09T06:58:45Z",
    "started_epoch_secs": 1715239940.0,
    "completed_epoch_secs": 1715240325.0,
    "job_duration": "0:06:25",
    "job_seconds": 385.0,
    "command_duration": "0:05:20",
    "command_seconds": 320.0
  }
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full job name from GitHub Actions |
| `started_at` | string | ISO 8601 timestamp when job started |
| `completed_at` | string | ISO 8601 timestamp when job completed |
| `started_epoch_secs` | float | Unix epoch seconds (for sorting) |
| `completed_epoch_secs` | float | Unix epoch seconds (for sorting) |
| `job_duration` | string | Total job duration (HH:MM:SS) |
| `job_seconds` | float | Total job duration in seconds |
| `command_duration` | string | "Run command" step duration (HH:MM:SS) |
| `command_seconds` | float | "Run command" step duration in seconds |

**Overhead Calculation:**

Overhead percentage = `(job_seconds - command_seconds) / command_seconds * 100`

This metric identifies jobs with excessive setup/teardown time.

Sources: [.github/actions/workflow-results/parse-job-times.py:48-129]()

---

## Data Flow Diagram: Generation to Execution

```mermaid
graph TB
    subgraph "Generation Phase"
        BuildWorkflow["build-workflow.py"]
        MatrixYAML["matrix.yaml"]
        
        MatrixYAML --> BuildWorkflow
        BuildWorkflow --> WorkflowJSON["workflow.json<br/>{group_name: {standalone: [], two_stage: []}}"]
        BuildWorkflow --> JobIdsJSON["job_ids.json<br/>{id: full_name}"]
        BuildWorkflow --> RunnerSummary["runner_summary.json<br/>{heading, body}"]
        BuildWorkflow --> JobList["job_list.txt"]
    end
    
    subgraph "Dispatch Preparation"
        PrepareDispatch["prepare-workflow-dispatch.py"]
        
        WorkflowJSON --> PrepareDispatch
        PrepareDispatch --> DispatchJSON["dispatch.json<br/>{linux_standalone,<br/>linux_two_stage,<br/>windows_standalone,<br/>windows_two_stage}"]
    end
    
    subgraph "Job Execution"
        RunJob["workflow-run-job-*"]
        
        DispatchJSON --> RunJob
        RunJob --> Success["jobs/{id}/success"]
        RunJob --> SccacheStats["jobs/{id}/sccache_stats.json"]
        RunJob --> BenchData["jobs/{id}/cccl_meta_bench.csv"]
    end
    
    subgraph "Results Collection"
        ParseTimes["parse-job-times.py"]
        GitHubAPI["GitHub Actions API"]
        
        WorkflowJSON --> ParseTimes
        GitHubAPI --> JobsJSON["jobs.json"]
        JobsJSON --> ParseTimes
        ParseTimes --> JobTimesJSON["results/job_times.json<br/>{id: {name, durations, ...}}"]
    end
```

Sources: [.github/actions/workflow-build/build-workflow.py:979-1048](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:25-76](), [.github/actions/workflow-results/parse-job-times.py:48-112]()

---

## Code Entity Mapping: File Generators

This diagram maps file formats to the specific Python functions that generate them:

```mermaid
graph LR
    subgraph "build-workflow.py Functions"
        ParseWorkflow["parse_workflow_dispatch_groups()"]
        FinalizeGroups["finalize_workflow_dispatch_groups()"]
        WriteOutputs["write_outputs()"]
        WriteJSON["write_json_file()"]
        WriteTXT["write_text_file()"]
    end
    
    subgraph "Generated Files"
        WorkflowJSON["workflow.json"]
        JobIdsJSON["job_ids.json"]
        RunnerSummaryJSON["runner_summary.json"]
        JobListTXT["job_list.txt"]
    end
    
    ParseWorkflow --> FinalizeGroups
    FinalizeGroups --> WriteOutputs
    
    WriteOutputs --> WriteJSON
    WriteOutputs --> WriteTXT
    
    WriteJSON --> WorkflowJSON
    WriteJSON --> JobIdsJSON
    WriteJSON --> RunnerSummaryJSON
    WriteTXT --> JobListTXT
    
    subgraph "prepare-workflow-dispatch.py Functions"
        SplitWorkflow["split_workflow()"]
    end
    
    subgraph "Output"
        DispatchJSON["dispatch.json"]
    end
    
    WorkflowJSON --> SplitWorkflow
    SplitWorkflow --> DispatchJSON
    
    subgraph "parse-job-times.py Functions"
        ParseMain["main()"]
        GenJobIDMap["generate_job_id_map()"]
    end
    
    subgraph "Timing Output"
        JobTimesJSON["job_times.json"]
    end
    
    WorkflowJSON --> GenJobIDMap
    GenJobIDMap --> ParseMain
    ParseMain --> JobTimesJSON
```

Sources: [.github/actions/workflow-build/build-workflow.py:962-1048](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:78-95](), [.github/actions/workflow-results/parse-job-times.py:48-129]()

---

## File Location Summary

| File | Path | Generator | Consumer |
|------|------|-----------|----------|
| `matrix.yaml` | `ci/matrix.yaml` | Manual (input) | `build-workflow.py` |
| `workflow.json` | `workflow/workflow.json` | `build-workflow.py` | `prepare-workflow-dispatch.py`, `parse-job-times.py` |
| `dispatch.json` | `workflow/dispatch.json` | `prepare-workflow-dispatch.py` | Dispatch workflows |
| `job_ids.json` | `workflow/job_ids.json` | `build-workflow.py` | Results reporting |
| `runner_summary.json` | `workflow/runner_summary.json` | `build-workflow.py` | `workflow-build` action output |
| `job_list.txt` | `workflow/job_list.txt` | `build-workflow.py` | Manual inspection |
| `override.json` | `workflow/override.json` | `build-workflow.py` | Override detection |
| `success` | `jobs/<id>/success` | Job execution | `verify-job-success.py` |
| `sccache_stats.json` | `jobs/<id>/sccache_stats.json` | Job execution | `prepare-execution-summary.py` |
| `cccl_meta_bench.csv` | `jobs/<id>/cccl_meta_bench.csv` | Job execution | Future processing |
| `jobs.json` | N/A (API) | GitHub API | `parse-job-times.py` |
| `job_times.json` | `results/job_times.json` | `parse-job-times.py` | `prepare-execution-summary.py` |

Sources: [.github/actions/workflow-build/build-workflow.py:1019-1029](), [.github/actions/workflow-build/prepare-workflow-dispatch.py:74-75](), [.github/actions/workflow-results/parse-job-times.py:110-111]()

---

## Validation and Schema Enforcement

### Tag Validation in matrix.yaml

The `validate_tags()` function enforces schema compliance:

**Validation Rules:**

1. All required tags must be present (checked via `tags[tag].required`)
2. Unknown tags are rejected
3. Special constraints:
   - `cudacxx: clang` requires `cxx: clang`
   - `sm: gpu` requires `gpu` tag to be present
4. GPU values must exist in `gpus` dictionary

**Canonicalization:**

Tag values are normalized:
- `ctk: 11` → `ctk: "11.1"` (via `aka` mapping)
- `cxx: gcc` → `cxx: "gcc12"` (latest version)
- `cxx: gcc-12` → `cxx: "gcc12"` (hyphen to direct format)

Sources: [.github/actions/workflow-build/build-workflow.py:811-832](), [.github/actions/workflow-build/build-workflow.py:845-850]()

---

## Job ID Format

Job IDs use a compact base64 encoding scheme to keep GHA workflow names short.

### ID Generation Algorithm

```python
def generate_guids():
    i = 0
    while True:
        # Base64 encode 16-bit integer
        hash = base64.b64encode(struct.pack(">H", i)).decode('ascii')
        # Strip leading 'A's and trailing '='
        guid = re.sub(r'^A{0,2}', '', hash).removesuffix("=")
        yield guid
        i += 1
```

**ID Examples:**

| Index | Base64 | Stripped ID |
|-------|--------|-------------|
| 0 | `AAA=` | `` (empty, not used) |
| 1 | `AAE=` | `E` |
| 10 | `AAo=` | `o` |
| 100 | `AGQ=` | `GQ` |
| 1000 | `A+g=` | `+g` |

**Properties:**

- IDs are 1-3 characters long
- Maximum 65,535 unique IDs supported
- Characters include: `A-Z`, `a-z`, `0-9`, `+`, `/`

Sources: [.github/actions/workflow-build/build-workflow.py:78-96](), [.github/actions/workflow-build/build-workflow.py:708-719]()

---

# Page: Environment Variables

# Environment Variables

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)
- [.github/actions/workflow-run-job-windows/action.yml](.github/actions/workflow-run-job-windows/action.yml)

</details>



This page provides a comprehensive reference of all environment variables used throughout the cccl-gha workflow orchestration system. Environment variables are used to configure AWS credentials for distributed compilation caching, pass GitHub Actions context to devcontainers, control sccache behavior, and customize job execution.

For information about how these variables are configured during job execution, see [Environment Setup](#5.4). For details on AWS credential configuration specifically, see [Distributed Compilation Caching](#7.2).

---

## Overview

Environment variables serve four primary roles in the system:

1. **GitHub Actions Context**: Built-in variables that provide repository, workflow, and execution metadata
2. **AWS Credentials**: Authentication tokens for sccache S3 bucket access
3. **Sccache Configuration**: Settings that control distributed compilation caching behavior
4. **Custom CI Variables**: System-specific variables for command execution and debugging

The propagation of these variables differs between Linux and Windows execution environments due to the Docker-outside-of-Docker (DOOD) architecture used on Linux.

---

## GitHub Actions Context Variables

GitHub Actions automatically provides environment variables that describe the current workflow execution context. The system selectively propagates these variables into devcontainers to enable proper artifact handling, path resolution, and debugging.

### Core Context Variables

| Variable | Description | Used By | Propagated to Container |
|----------|-------------|---------|------------------------|
| `GITHUB_WORKSPACE` | Absolute path to the repository checkout on the runner | Path resolution, artifact collection | Yes (Linux & Windows) |
| `GITHUB_SHA` | Commit SHA that triggered the workflow | Reproduction instructions, debugging | Yes (Linux) |
| `GITHUB_REPOSITORY` | Repository name in `owner/repo` format | Reproduction instructions, debugging | Yes (Linux) |
| `GITHUB_REF_NAME` | Branch or tag name that triggered the workflow | Reproduction instructions | Yes (Linux) |
| `GITHUB_ACTIONS` | Always `true` when running in GitHub Actions | Conditional logic detection | Yes (Linux) |
| `GITHUB_ENV` | Path to file for setting environment variables | Dynamic configuration | Yes (Linux) |
| `GITHUB_PATH` | Path to file for adding to system PATH | Dynamic PATH updates | Yes (Linux) |
| `GITHUB_OUTPUT` | Path to file for setting step outputs | Cross-step communication | Yes (Linux) |
| `GITHUB_STEP_SUMMARY` | Path to file for writing workflow summary markdown | Results reporting | Yes (Linux) |

### Runner Context Variables

| Variable | Description | Set By | Usage |
|----------|-------------|--------|-------|
| `RUNNER_TEMP` | Temporary directory on the runner | GitHub Actions | AWS credential files, intermediate artifacts |
| `github.workspace` | GHA input expression for workspace path | GitHub Actions | Volume mount path calculations |
| `github.event.repository.name` | Repository name without owner | GitHub Actions | Checkout directory naming |

**Sources**: [.github/actions/workflow-run-job-linux/action.yml:66-164]()

---

## AWS Credential Variables

AWS credentials are obtained via OpenID Connect (OIDC) federation with the AWS IAM role and are used exclusively for accessing the sccache S3 bucket. These credentials are temporary and expire after 12 hours.

### Credential Variables

| Variable | Description | Lifecycle | Security |
|----------|-------------|-----------|----------|
| `AWS_ACCESS_KEY_ID` | Temporary AWS access key identifier | Set by `aws-actions/configure-aws-credentials@v4`, expires in 12 hours | Sensitive - never logged |
| `AWS_SECRET_ACCESS_KEY` | Temporary AWS secret access key | Set by `aws-actions/configure-aws-credentials@v4`, expires in 12 hours | Sensitive - never logged |
| `AWS_SESSION_TOKEN` | Temporary session token for assumed role | Set by `aws-actions/configure-aws-credentials@v4`, expires in 12 hours | Sensitive - never logged |

### OIDC Configuration

The system assumes the IAM role `arn:aws:iam::279114543810:role/gha-oidc-NVIDIA` in the `us-east-2` region with a 12-hour session duration.

**Linux Environment**: Credentials are written to `$RUNNER_TEMP/.aws/credentials` and `$RUNNER_TEMP/.aws/config` files, which are then mounted into the devcontainer at `/root/.aws/`.

```
[default]
aws_access_key_id=<value>
aws_session_token=<value>
aws_secret_access_key=<value>
```

**Windows Environment**: Credentials are passed directly as environment variables to the Docker container via PowerShell's `SetEnvironmentVariable` method.

**Sources**: [.github/actions/workflow-run-job-linux/action.yml:60-65](), [.github/actions/workflow-run-job-linux/action.yml:113-129](), [.github/actions/workflow-run-job-windows/action.yml:26-31](), [.github/actions/workflow-run-job-windows/action.yml:55-57]()

---

## Sccache Configuration Variables

Sccache (Shared Compilation Cache) configuration variables control how distributed compilation caching behaves. These variables are platform-specific in their configuration method but identical in function.

### Linux Sccache Configuration

On Linux, sccache configuration is provided via the AWS config file at `/root/.aws/config` mounted into the devcontainer:

```
[default]
bucket=rapids-sccache-devs
region=us-east-2
```

The bucket and region are hardcoded in the configuration file generation logic.

### Windows Sccache Configuration

| Variable | Value | Purpose |
|----------|-------|---------|
| `SCCACHE_BUCKET` | `rapids-sccache-devs` | S3 bucket name for cache storage |
| `SCCACHE_REGION` | `us-east-2` | AWS region for the S3 bucket |
| `SCCACHE_IDLE_TIMEOUT` | `0` | Disable idle timeout (keep daemon alive) |
| `SCCACHE_S3_USE_SSL` | `true` | Use HTTPS for S3 connections |
| `SCCACHE_S3_NO_CREDENTIALS` | `false` | Use AWS credentials (not anonymous) |

These variables are set in `GITHUB_ENV` and then explicitly passed to the Docker container's PowerShell environment.

**Sources**: [.github/actions/workflow-run-job-linux/action.yml:115-119](), [.github/actions/workflow-run-job-windows/action.yml:18-25](), [.github/actions/workflow-run-job-windows/action.yml:58-62]()

---

## Custom CI Variables

The system defines several custom environment variables to control job execution behavior and provide metadata to commands running inside devcontainers.

### Execution Control Variables

| Variable | Description | Set By | Scope |
|----------|-------------|--------|-------|
| `CI` | Set to `true` to indicate CI environment | Action YAML | All jobs (Linux & Windows) |
| `COMMAND` | The actual command string to execute | Action input via env var | Linux job execution |
| `RUNNER` | The GitHub Actions `runs-on` value (e.g., `linux-amd64-gpu-v100-latest-1`) | Action input | Linux GPU detection |
| `VAULT_HOST` | Set to empty string to disable Vault integration | Action logic | Linux devcontainer |

### Variable Usage Patterns

**`CI` Variable**: Set to `true` in all environments to enable CI-specific behavior in build scripts and tests.

```yaml
env:
  CI: true
```

**`COMMAND` Variable**: The command to execute is passed via an environment variable rather than a direct GitHub Actions input to avoid escaping issues with special characters (e.g., `-arch "60;70;80"` with semicolons).

```yaml
env:
  COMMAND: "${{inputs.command}}"
```

**`RUNNER` Variable**: Used to detect GPU availability. If the runner name contains `-gpu-`, the system adds the `--gpus` flag when launching the devcontainer.

```bash
if [[ "${RUNNER}" = *"-gpu-"* ]]; then
  gpu_request+=(--gpus "device=${NVIDIA_VISIBLE_DEVICES}")
fi
```

**`VAULT_HOST` Variable**: Explicitly set to empty string to disable HashiCorp Vault credential fetching in CI environments (credentials are provided via AWS OIDC instead).

**Sources**: [.github/actions/workflow-run-job-linux/action.yml:66-76](), [.github/actions/workflow-run-job-linux/action.yml:134-148]()

---

## GPU Resource Variables

GPU access is controlled via environment variables set by the GitHub Actions runner and passed to Docker containers.

| Variable | Description | Set By | Usage |
|----------|-------------|--------|-------|
| `NVIDIA_VISIBLE_DEVICES` | GPU device identifier(s) visible to the container | GitHub Actions runner | Passed to Docker via `--gpus device=${NVIDIA_VISIBLE_DEVICES}` |

The system detects GPU runners by checking if the `RUNNER` variable contains `-gpu-`. When detected, the `NVIDIA_VISIBLE_DEVICES` value is used to restrict container access to specific GPU devices.

```bash
gpu_request+=(--gpus "device=${NVIDIA_VISIBLE_DEVICES}")
```

This ensures proper GPU isolation when multiple GPU jobs run on the same physical runner.

**Sources**: [.github/actions/workflow-run-job-linux/action.yml:133-136]()

---

## Environment Variable Propagation Architecture

The following diagram illustrates how environment variables flow from GitHub Actions through the intermediate container to the final devcontainer on Linux (the more complex scenario).

### Linux Environment Variable Flow

```mermaid
graph TB
    subgraph "GitHub Actions Runner"
        GHA["GitHub Actions<br/>Context Variables"]
        AWS["AWS OIDC Action<br/>Credential Variables"]
        Input["Action Inputs<br/>(runner, command)"]
    end
    
    subgraph "Intermediate Container: ubuntu-dind"
        EnvVars["Environment Variables<br/>CI, RUNNER, COMMAND<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>AWS_SESSION_TOKEN"]
        FileAWS["$RUNNER_TEMP/.aws/<br/>credentials & config files"]
        FileCIsh["ci.sh wrapper script<br/>contains COMMAND"]
    end
    
    subgraph "DevContainer Launch"
        LaunchSh[".devcontainer/launch.sh"]
        EnvFlags["--env flags for each variable"]
        VolumeMounts["--volume mounts:<br/>ci.sh → /ci.sh<br/>.aws → /root/.aws<br/>repo → /__w"]
    end
    
    subgraph "DevContainer Execution"
        DevEnv["Container Environment:<br/>GITHUB_WORKSPACE<br/>GITHUB_SHA<br/>GITHUB_REPOSITORY<br/>CI, COMMAND, etc."]
        AWSFiles["/root/.aws/<br/>mounted credentials"]
        CIScript["/ci.sh<br/>executes COMMAND"]
    end
    
    GHA --> EnvVars
    AWS --> EnvVars
    AWS --> FileAWS
    Input --> EnvVars
    Input --> FileCIsh
    
    EnvVars --> LaunchSh
    FileAWS --> LaunchSh
    FileCIsh --> LaunchSh
    
    LaunchSh --> EnvFlags
    LaunchSh --> VolumeMounts
    
    EnvFlags --> DevEnv
    VolumeMounts --> AWSFiles
    VolumeMounts --> CIScript
    
    DevEnv --> CIScript
    AWSFiles --> CIScript
```

**Key Points**:

1. **Environment Variables**: Most variables are passed using `--env` flags to `docker run` command via `launch.sh`
2. **AWS Credentials**: Written to files in `$RUNNER_TEMP/.aws/` and mounted as a volume (not passed as environment variables to avoid logging)
3. **Command Execution**: The `COMMAND` string is embedded in `ci.sh` script and mounted as `/ci.sh` to avoid escaping issues
4. **Path Consistency**: Symlinks ensure that paths referenced inside containers match host paths (required for DOOD architecture)

**Sources**: [.github/actions/workflow-run-job-linux/action.yml:77-164]()

---

## Windows Environment Variable Propagation

Windows uses a simpler direct propagation model since it doesn't use the DOOD pattern.

```mermaid
graph TB
    subgraph "GitHub Actions Runner"
        GHA_WIN["GitHub Actions<br/>Context Variables"]
        AWS_WIN["AWS OIDC Action<br/>Credential Variables"]
        Input_WIN["Action Inputs<br/>(command, image)"]
    end
    
    subgraph "Windows Runner Shell"
        GHEnv["GITHUB_ENV file"]
        SccacheVars["SCCACHE_* variables<br/>written to GITHUB_ENV"]
    end
    
    subgraph "Docker Container"
        PSScript["PowerShell Script<br/>SetEnvironmentVariable calls"]
        ContainerEnv["Container Environment:<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>AWS_SESSION_TOKEN<br/>SCCACHE_BUCKET<br/>SCCACHE_REGION<br/>etc."]
        GitConfig["git config --global<br/>safe.directory"]
        CommandExec["Command Execution"]
    end
    
    GHA_WIN --> GHEnv
    AWS_WIN --> GHEnv
    Input_WIN --> PSScript
    
    SccacheVars --> GHEnv
    GHEnv --> PSScript
    
    PSScript --> ContainerEnv
    ContainerEnv --> GitConfig
    ContainerEnv --> CommandExec
```

**Key Differences from Linux**:

1. **Direct Propagation**: Environment variables are set directly in the PowerShell environment inside the container using `SetEnvironmentVariable`
2. **No File Mounting**: AWS credentials are passed as environment variables, not via mounted files
3. **Simpler Architecture**: No intermediate container; variables flow directly from runner to target container
4. **Explicit Setting**: Each variable is explicitly set via PowerShell commands in the Docker `run` command

**Sources**: [.github/actions/workflow-run-job-windows/action.yml:18-64]()

---

## Environment Variable Reference Table

This comprehensive table lists all environment variables used across the system:

| Variable | Category | Platform | Set By | Used In | Sensitive |
|----------|----------|----------|--------|---------|-----------|
| `CI` | Custom | Both | Action YAML | Build scripts, test detection | No |
| `COMMAND` | Custom | Linux | Action input | ci.sh execution | No |
| `RUNNER` | Custom | Linux | Action input | GPU detection | No |
| `VAULT_HOST` | Custom | Linux | Action logic | Devcontainer init | No |
| `GITHUB_WORKSPACE` | GitHub | Both | GitHub Actions | Path resolution | No |
| `GITHUB_SHA` | GitHub | Linux | GitHub Actions | Reproduction instructions | No |
| `GITHUB_REPOSITORY` | GitHub | Linux | GitHub Actions | Reproduction instructions | No |
| `GITHUB_REF_NAME` | GitHub | Linux | GitHub Actions | Reproduction instructions | No |
| `GITHUB_ACTIONS` | GitHub | Linux | GitHub Actions | CI detection | No |
| `GITHUB_ENV` | GitHub | Both | GitHub Actions | Dynamic env updates | No |
| `GITHUB_PATH` | GitHub | Linux | GitHub Actions | Dynamic PATH updates | No |
| `GITHUB_OUTPUT` | GitHub | Linux | GitHub Actions | Step outputs | No |
| `GITHUB_STEP_SUMMARY` | GitHub | Linux | GitHub Actions | Workflow summary | No |
| `RUNNER_TEMP` | GitHub | Both | GitHub Actions | Temp file storage | No |
| `AWS_ACCESS_KEY_ID` | AWS | Both | aws-actions/configure-aws-credentials | sccache authentication | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS | Both | aws-actions/configure-aws-credentials | sccache authentication | Yes |
| `AWS_SESSION_TOKEN` | AWS | Both | aws-actions/configure-aws-credentials | sccache authentication | Yes |
| `SCCACHE_BUCKET` | Sccache | Windows | Action logic | Cache bucket name | No |
| `SCCACHE_REGION` | Sccache | Windows | Action logic | AWS region | No |
| `SCCACHE_IDLE_TIMEOUT` | Sccache | Windows | Action logic | Daemon timeout | No |
| `SCCACHE_S3_USE_SSL` | Sccache | Windows | Action logic | HTTPS enforcement | No |
| `SCCACHE_S3_NO_CREDENTIALS` | Sccache | Windows | Action logic | Credential usage flag | No |
| `NVIDIA_VISIBLE_DEVICES` | GPU | Linux | GitHub runner | GPU device selection | No |

---

## Variable Security and Best Practices

### Sensitive Variables

AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`) are considered sensitive. The system takes precautions to prevent them from appearing in logs:

- **Linux**: Credentials are written to files with restricted permissions (`0600` for credentials, `0664` for config) and mounted as volumes rather than passed as environment variables
- **Windows**: Credentials are set via PowerShell's `SetEnvironmentVariable` which doesn't echo values
- **No Logging**: Credentials are never echoed or logged in any scripts

### File Permissions

```bash
chmod 0600 "$RUNNER_TEMP/.aws/credentials"
chmod 0664 "$RUNNER_TEMP/.aws/config"
```

The credentials file has owner-only read/write permissions, while the config file allows group read.

### Command Escaping

The `COMMAND` variable is passed via environment variable rather than direct GitHub Actions input to avoid shell escaping issues with special characters like semicolons, quotes, and parentheses that are common in compiler flags:

```bash
# Example command with special characters
-arch "60;70;80" -DCUDA_VERSION=12.0
```

Using `${{inputs.command}}` directly in shell scripts would require complex escaping. By dereferencing from `COMMAND` environment variable, the shell handles it correctly.

**Sources**: [.github/actions/workflow-run-job-linux/action.yml:66-76](), [.github/actions/workflow-run-job-linux/action.yml:113-129]()

---

## Debugging Environment Variables

When debugging job execution issues, several environment variables can be inspected:

```bash
# In the ci.sh script, the following are available:
echo "Workspace: ${GITHUB_WORKSPACE}"
echo "SHA: ${GITHUB_SHA}"
echo "Repository: ${GITHUB_REPOSITORY}"
echo "Branch: ${GITHUB_REF_NAME}"
echo "Command: ${COMMAND}"
echo "Runner: ${RUNNER}"
```

The reproduction instructions generated on failure reference these variables:

```bash
git clone --branch $GITHUB_REF_NAME --single-branch \
  https://github.com/$GITHUB_REPOSITORY.git
cd $(echo $GITHUB_REPOSITORY | cut -d'/' -f2)
git checkout $GITHUB_SHA
```

This ensures developers can exactly reproduce the failing commit state locally.

**Sources**: [.github/actions/workflow-run-job-linux/action.yml:89-109]()

---

# Page: Troubleshooting Guide

# Troubleshooting Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-results/action.yml](.github/actions/workflow-results/action.yml)
- [.github/actions/workflow-run-job-linux/action.yml](.github/actions/workflow-run-job-linux/action.yml)

</details>



This page provides practical guidance for diagnosing and resolving failures in the CCCL GitHub Actions workflow system. It covers common error patterns, log analysis techniques, local reproduction strategies, and component-specific debugging approaches. For information about the overall system architecture, see [System Architecture](#1.1). For details on individual components, refer to [Job Execution](#5) and [Results and Reporting](#6).

## Common Failure Patterns

### Job Execution Failures

The most common failure point is during the actual job execution phase. These failures are characterized by a non-zero exit code from the command executed inside the devcontainer.

**Failure Indicators:**
- Job artifacts contain no `success` marker file at `jobs/{job_id}/success`
- Error output includes reproduction instructions formatted by `ci.sh`
- GitHub Actions logs show exit code from the command execution

**Typical Causes:**
- Compilation errors (syntax errors, missing dependencies, incompatible flags)
- Test failures (assertion failures, segmentation faults, timeouts)
- Environment configuration issues (missing environment variables, incorrect paths)
- Resource exhaustion (out-of-memory, disk space issues)

Sources: [.github/actions/workflow-run-job-linux/action.yml:89-109]()

### Artifact Collection Failures

The results collection phase can fail when job artifacts are incomplete or malformed, typically manifesting as `continue-on-error: true` steps succeeding but producing invalid data.

```mermaid
graph TB
    JobExecution["Job Execution<br/>(workflow-run-job-linux)"]
    ArtifactUpload["Upload Artifacts<br/>actions/upload-artifact@v4"]
    ArtifactDownload["Download Artifacts<br/>actions/download-artifact@v4"]
    LineEndingFix["Fix Line Endings<br/>dos2unix"]
    ParseTimes["parse-job-times.py"]
    PrepareExec["prepare-execution-summary.py"]
    
    JobExecution -->|"success marker"| ArtifactUpload
    JobExecution -->|"sccache_stats.json"| ArtifactUpload
    JobExecution -->|"cccl_meta_bench.csv"| ArtifactUpload
    
    ArtifactUpload -->|"jobs-{id}"| ArtifactDownload
    ArtifactDownload --> LineEndingFix
    LineEndingFix --> ParseTimes
    LineEndingFix --> PrepareExec
    
    ParseTimes -.->|"failure:<br/>missing jobs.json"| Error1["No GitHub API data"]
    PrepareExec -.->|"failure:<br/>missing job_times.json"| Error2["Parse times failed"]
    LineEndingFix -.->|"failure:<br/>dos2unix not found"| Error3["Line ending conversion failed"]
```

**Debugging Artifact Collection Issues:**

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| `jobs.json` missing | GitHub API rate limit or permissions | Check `github_token` is provided and has appropriate scope |
| `job_times.json` missing | `parse-job-times.py` failed | Check logs for Python traceback, verify `workflow.json` structure |
| Line ending errors on Windows artifacts | Windows CRLF not converted | Verify `dos2unix` installation step succeeded |
| No job artifacts downloaded | All jobs failed before artifact upload | Check individual job logs for early failures |
| Partial artifact tree | Some jobs crashed without cleanup | Review jobs with no `success` marker but also no clear failure log |

Sources: [.github/actions/workflow-results/action.yml:30-58](), [.github/actions/workflow-run-job-linux/action.yml:166-201]()

### Docker-Outside-of-Docker (DOOD) Path Issues

Linux jobs use a DOOD strategy where path mismatches between the intermediate container and the host can cause mount failures.

```mermaid
graph LR
    subgraph "GitHub Runner Host"
        HostPath["/__w/repo/repo"]
    end
    
    subgraph "Intermediate Container<br/>(ubuntu-dind)"
        ContainerPwd["$(pwd)<br/>/github/workspace"]
        Symlink["ln -s"]
        GitHubWorkspace["${{github.workspace}}<br/>/__w/repo/repo"]
    end
    
    subgraph "Target Devcontainer"
        Mount["--volume<br/>/__w:/___w"]
        ActualPath["Workdir:<br/>/__w/repo/repo"]
    end
    
    HostPath -.->|"must match"| GitHubWorkspace
    ContainerPwd --> Symlink
    Symlink --> GitHubWorkspace
    GitHubWorkspace -->|"host_path() transform"| Mount
    Mount --> ActualPath
```

**Common Path-Related Errors:**

- **Mount path not found**: Occurs when `host_path()` function fails to transform container paths to host paths
- **Working directory mismatch**: Environment variables reference container paths but Docker sees host paths
- **AWS credentials inaccessible**: The `.aws` mount uses `$RUNNER_TEMP` which must be transformed correctly

**Debugging Steps:**
1. Check the "Run command" step output for path information:
   ```
   [host]      github.workspace: /__w/repo/repo
   [container] GITHUB_WORKSPACE: /github/workspace
   [container]              PWD: /github/workspace
   ```
2. Verify the symlink creation succeeded: `ln -s "$(pwd)" "${{github.workspace}}"`
3. Examine the `host_path()` function transformation at [.github/actions/workflow-run-job-linux/action.yml:138-140]()
4. Check that volume mounts reference the correct paths in the `launch.sh` invocation

Sources: [.github/actions/workflow-run-job-linux/action.yml:78-164]()

## Understanding Logs and Artifacts

### GitHub Actions Workflow Logs

GitHub Actions logs are organized hierarchically: workflow run → job → step. Each component of the CCCL workflow system produces logs at different levels.

**Log Locations by Component:**

```mermaid
graph TB
    WorkflowRun["Workflow Run<br/>(e.g., pull_request)"]
    
    subgraph "Workflow Generation"
        BuildJob["workflow-build Action"]
        BuildPy["build-workflow.py<br/>::group:: outputs"]
        PrepareDispatch["prepare-workflow-dispatch.py<br/>::group:: outputs"]
    end
    
    subgraph "Job Dispatch"
        GroupDispatch["Group Dispatch Job<br/>(standalone/two-stage)"]
        MatrixExpansion["Matrix expansion<br/>(implicit logs)"]
    end
    
    subgraph "Job Execution"
        RunJob["workflow-run-job-linux<br/>Step: Run command"]
        CiSh["ci.sh wrapper<br/>stdout/stderr"]
        DevContainer["Devcontainer<br/>command output"]
    end
    
    subgraph "Results Collection"
        ResultsAction["workflow-results Action"]
        ParseStep["parse-job-times.py<br/>::group:: outputs"]
        FinalSummary["final-summary.py<br/>GITHUB_STEP_SUMMARY"]
    end
    
    WorkflowRun --> BuildJob
    WorkflowRun --> GroupDispatch
    WorkflowRun --> ResultsAction
    
    BuildJob --> BuildPy
    BuildJob --> PrepareDispatch
    
    GroupDispatch --> MatrixExpansion
    MatrixExpansion --> RunJob
    
    RunJob --> CiSh
    CiSh --> DevContainer
    
    ResultsAction --> ParseStep
    ResultsAction --> FinalSummary
```

**Key Log Sections:**

| Log Section | Location | Contains |
|-------------|----------|----------|
| Workflow generation | `workflow-build` job → `build-workflow.py` step | Matrix processing, tag explosion, job definitions |
| Dispatch preparation | `workflow-build` job → `prepare-workflow-dispatch.py` step | Split by OS/type, dispatch group creation |
| Job execution preamble | Individual job → "Run command" step header | Path setup, symlink creation, environment info |
| Actual command output | Individual job → "Run command" step body | Build/test output, compilation logs, test results |
| Reproduction instructions | Individual job → "Run command" step (on failure) | Exact commands to reproduce locally |
| Artifact preparation | Individual job → "Prepare job artifacts" step | Success marker, sccache stats, benchmark data |
| Results download | `workflow-results` job → "Download job artifacts" step | Artifact tree structure |
| Timing analysis | `workflow-results` job → "Parse job times" step | Job duration calculation |
| Final summary | `workflow-results` job → "Prepare final summary" step → `GITHUB_STEP_SUMMARY` | Aggregated results, pass rates, culprit analysis |

Sources: [.github/actions/workflow-results/action.yml:92-128](), [.github/actions/workflow-run-job-linux/action.yml:66-165]()

### Artifact Structure

Artifacts uploaded by jobs follow a specific directory structure that the results collection system expects:

```
jobs/
├── {job_id_1}/
│   ├── success                    # Marker file indicating successful completion
│   ├── sccache_stats.json        # Compilation cache statistics
│   ├── cccl_meta_bench.csv       # Benchmark results (if applicable)
│   ├── cccl_meta_bench.db        # Benchmark database (if applicable)
│   └── cccl_meta_bench.log       # Benchmark logs (if applicable)
├── {job_id_2}/
│   └── success
└── {job_id_3}/
    ├── sccache_stats.json
    └── cccl_meta_bench.csv
```

**Interpreting Missing Artifacts:**

- **No `success` marker**: Job failed before the "Prepare job artifacts" step
- **No `sccache_stats.json`**: Build did not use sccache, or sccache stats not generated
- **No benchmark files**: Job is not a benchmark job, or benchmark execution failed
- **Empty job directory**: Job failed very early (e.g., Docker launch failure)

Sources: [.github/actions/workflow-run-job-linux/action.yml:166-201]()

### Interpreting the Final Summary

The final summary displayed in `GITHUB_STEP_SUMMARY` and PR comments provides hierarchical pass/fail statistics. Understanding its structure is critical for debugging.

**Summary Structure:**
```
Execution Summary:
├── Overall: X/Y jobs passed (Z%)
├── By Project:
│   ├── Project A: X/Y (Z%)
│   │   ├── By compiler: gcc10 X/Y, gcc11 X/Y
│   │   ├── By cuda: 12.0 X/Y, 12.6 X/Y
│   │   └── Likely culprit: cuda=11.1 (0% pass rate)
│   └── Project B: X/Y (Z%)
└── Sccache Statistics:
    ├── Total hits: X
    └── Hit rate: Y%
```

**"Likely Culprit" Detection:**

The summary identifies specific tag values responsible for all failures in a dimension. This logic is implemented in `prepare-execution-summary.py` and looks for tag values with 0% pass rate.

**Example Interpretation:**
```
libcudacxx: 45/50 (90%)
  Likely culprit: std=11 (0/5, 0%)
```
This indicates that all failures in the `libcudacxx` project had `std=11` as a common tag, suggesting C++11 compatibility issues.

Sources: [.github/actions/workflow-results/action.yml:99-128]()

## Reproducing Failures Locally

### Using the Reproduction Instructions

Every job failure includes formatted reproduction instructions in the logs. These instructions are generated by the `ci.sh` wrapper script and provide the exact commands needed to reproduce the failure.

**Reproduction Instruction Format:**

```mermaid
flowchart TB
    Failure["Command exits with<br/>non-zero code"]
    ErrorGroup["::error:: group<br/>Instructions to Reproduce"]
    Clone["git clone --branch {branch}<br/>--single-branch {repo}"]
    Checkout["git checkout {sha}"]
    Launch[".devcontainer/launch.sh<br/>-d -c {cuda} -H {host}<br/>-- {command}"]
    
    Failure --> ErrorGroup
    ErrorGroup --> Clone
    Clone --> Checkout
    Checkout --> Launch
    
    style ErrorGroup fill:#ffebee
```

**Example from Logs:**
```
::error:: To replicate this failure locally, follow the steps below:
1. Clone the repository, and navigate to the correct branch and commit:
   git clone --branch feature-branch --single-branch https://github.com/NVIDIA/cccl.git && cd cccl && git checkout abc123def456

2. Run the failed command inside the same Docker container used by this CI job:
   .devcontainer/launch.sh -d -c 12.0 -H gcc11 -- ci/test_libcudacxx.sh
```

**Key Parameters:**
- `-d`: Detach mode (optional, runs container in background)
- `-c {cuda}`: CUDA version (e.g., `11.1`, `12.0`, `12.6`)
- `-H {host}`: Host compiler (e.g., `gcc9`, `gcc10`, `gcc11`, `clang16`)
- `--`: Separator between launch.sh options and the command to execute

Sources: [.github/actions/workflow-run-job-linux/action.yml:89-109]()

### Manual Local Execution

For debugging, you may want to run commands interactively rather than through `ci.sh`.

**Interactive Container Launch:**
```bash
# Launch an interactive shell in the devcontainer
.devcontainer/launch.sh -c 12.0 -H gcc11

# Inside the container, manually execute the command
cd /path/to/repo
export CI=true
bash ci/test_libcudacxx.sh
```

**Mounting Local Files for Debugging:**
```bash
# Add custom volume mounts to access debugging tools
.devcontainer/launch.sh \
  -c 12.0 \
  -H gcc11 \
  --volume "$HOME/debug-scripts:/debug:ro" \
  -- /debug/custom-test.sh
```

**GPU Access for Local Reproduction:**

If reproducing a GPU-specific failure, ensure the Docker container has GPU access:
```bash
# Check that NVIDIA_VISIBLE_DEVICES is set
echo $NVIDIA_VISIBLE_DEVICES  # e.g., "0" or "0,1"

# Launch with GPU access (automatically handled by launch.sh)
.devcontainer/launch.sh --gpus "device=${NVIDIA_VISIBLE_DEVICES}" -c 12.0 -H gcc11 -- ci/test_thrust_gpu.sh
```

Sources: [.github/actions/workflow-run-job-linux/action.yml:131-164]()

### Debugging Devcontainer Selection

The `launch.sh` script selects devcontainer images based on CUDA and host compiler combinations. If a job fails with "image not found" errors, verify the devcontainer mapping.

**Devcontainer Selection Logic:**
```mermaid
graph LR
    Input["Input:<br/>--cuda {version}<br/>--host {compiler}"]
    Lookup["Lookup in<br/>.devcontainer/<br/>configurations"]
    Image["Resolved Image:<br/>rapidsai/devcontainers:..."]
    
    Input --> Lookup
    Lookup --> Image
    
    Lookup -.->|"Not Found"| Error["Error:<br/>Unsupported combination"]
```

**Verification Steps:**
1. Check `.devcontainer/` directory for configurations matching the CUDA/compiler pair
2. Run `make_devcontainers.sh --list` to see all available combinations (if implemented)
3. Verify the image exists in the container registry: `docker pull rapidsai/devcontainers:{tag}`

For more information on devcontainer system, see [Devcontainer System](#5.3).

Sources: [.github/actions/workflow-run-job-linux/action.yml:144-164]()

## Component-Specific Debugging

### Workflow Generation Issues

Failures during the workflow generation phase prevent jobs from being dispatched.

**Common Generation Errors:**

| Error Message | Location | Cause | Solution |
|---------------|----------|-------|----------|
| "Required tag missing" | `build-workflow.py` validation | Job definition lacks mandatory tags | Add missing tags to `matrix.yaml` |
| "Invalid tag value" | `build-workflow.py` validation | Tag value not in allowed list | Check allowed values in schema |
| "Exclusion pattern invalid" | `build-workflow.py` exclusions | Malformed exclusion rule | Fix exclusion syntax in `matrix.yaml` |
| "Circular tag dependency" | `build-workflow.py` derived tags | Derived tag depends on itself | Review derived tag definitions |

**Debugging Workflow Generation:**
1. Download the `workflow` artifact from the workflow run
2. Examine `workflow.json` for the expected job definitions
3. Check `job_ids.json` for job ID mappings
4. Review `runner_summary.json` for runner allocation

**Manual Generation Testing:**
```bash
# Run the generation pipeline locally
python3 .github/actions/workflow-build/build-workflow.py \
  --matrix ci/matrix.yaml \
  --workflows pull_request \
  --output workflow.json

# Check for errors in the output
cat workflow.json | jq '.jobs | length'
```

For detailed information on the generation pipeline, see [Workflow Generation](#3) and [build-workflow.py Pipeline](#3.1).

Sources: [.github/actions/workflow-results/action.yml:30-34]()

### Job Dispatch Failures

Dispatch failures occur when the group dispatch workflows fail to properly invoke execution workflows.

**Dispatch Failure Indicators:**
- No jobs appear in the "dispatched" section of the GitHub Actions UI
- Dispatch group jobs show "skipped" status
- `dispatch.json` is empty or malformed

**Debugging Dispatch Issues:**
```mermaid
graph TB
    DispatchJSON["dispatch.json<br/>artifact"]
    GroupWorkflow["Group Dispatch<br/>Workflow"]
    MatrixStrategy["Matrix Strategy<br/>fromJSON()"]
    ExecutionJobs["Execution Jobs<br/>(run-job-linux/windows)"]
    
    DispatchJSON -->|"parse JSON"| GroupWorkflow
    GroupWorkflow -->|"expand matrix"| MatrixStrategy
    MatrixStrategy -->|"spawn jobs"| ExecutionJobs
    
    GroupWorkflow -.->|"error:<br/>invalid JSON"| Error1["Check dispatch.json<br/>formatting"]
    MatrixStrategy -.->|"error:<br/>empty matrix"| Error2["No jobs matched<br/>OS/type criteria"]
    MatrixStrategy -.->|"error:<br/>matrix too large"| Error3["GitHub limit:<br/>256 jobs per matrix"]
```

**Resolution Steps:**
1. Download the `workflow` artifact and examine `dispatch.json`
2. Verify JSON syntax: `cat dispatch.json | jq .`
3. Check that the appropriate OS/type keys exist and contain arrays
4. Count jobs per matrix: `cat dispatch.json | jq '.linux_standalone | length'`
5. If matrix exceeds 256 jobs, review job filtering in `prepare-workflow-dispatch.py`

For more information on dispatch architecture, see [Job Dispatch](#4).

Sources: [.github/actions/workflow-results/action.yml:30-42]()

### Results Collection Failures

The results collection phase is resilient (most steps use `continue-on-error: true`), but understanding failures helps interpret incomplete results.

**Results Collection Flow with Failure Points:**

```mermaid
flowchart TB
    Download["Download Artifacts<br/>jobs-*"]
    FixLineEndings["dos2unix<br/>Convert CRLF"]
    FetchAPI["Fetch GitHub API<br/>job timing data"]
    ParseTimes["parse-job-times.py"]
    PrepareExec["prepare-execution-summary.py"]
    FinalSummary["final-summary.py"]
    VerifySuccess["verify-job-success.py"]
    
    Download --> FixLineEndings
    Download -.->|"continue-on-error"| F1["Partial artifacts OK"]
    
    FetchAPI --> ParseTimes
    FetchAPI -.->|"continue-on-error"| F2["No timing data"]
    
    FixLineEndings --> ParseTimes
    ParseTimes -.->|"continue-on-error"| F3["No job_times.json"]
    
    ParseTimes --> PrepareExec
    PrepareExec -.->|"continue-on-error"| F4["No exec summary"]
    
    PrepareExec --> FinalSummary
    FinalSummary -.->|"continue-on-error"| F5["No final summary"]
    
    FixLineEndings --> VerifySuccess
    VerifySuccess -->|"exit 1"| F6["Workflow fails"]
    
    style F6 fill:#ffebee
```

**Interpreting Partial Results:**

- **No timing data**: GitHub API call failed, but success/failure status still available
- **No execution summary**: Timing data missing, but job artifacts still processed
- **No final summary**: All data collection failed, but `verify-job-success.py` still determines pass/fail

**Common API Rate Limit Issues:**

If the GitHub API returns 403 or 429 errors:
1. Check if `github_token` input is provided: [.github/actions/workflow-results/action.yml:5-7]()
2. Verify token has `actions:read` scope
3. If rate limit exceeded, wait or use a different token

Sources: [.github/actions/workflow-results/action.yml:30-127](), [.github/actions/workflow-results/action.yml:155-178]()

### AWS Credentials and sccache Issues

Compilation caching via sccache requires AWS credentials configured correctly.

**AWS Configuration Setup:**

```mermaid
graph TB
    OIDC["GitHub OIDC<br/>aws-actions/configure-aws-credentials"]
    EnvVars["Environment Variables:<br/>AWS_ACCESS_KEY_ID<br/>AWS_SESSION_TOKEN<br/>AWS_SECRET_ACCESS_KEY"]
    ConfigFile["$RUNNER_TEMP/.aws/config<br/>bucket=rapids-sccache-devs<br/>region=us-east-2"]
    CredFile["$RUNNER_TEMP/.aws/credentials<br/>[default] credentials"]
    VolumeMount["Docker Volume Mount:<br/>--volume $RUNNER_TEMP/.aws:/root/.aws"]
    Container["Devcontainer<br/>sccache client"]
    
    OIDC --> EnvVars
    EnvVars --> ConfigFile
    EnvVars --> CredFile
    ConfigFile --> VolumeMount
    CredFile --> VolumeMount
    VolumeMount --> Container
```

**Common AWS/sccache Errors:**

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Unable to locate credentials" | `.aws` volume mount failed | Check `host_path()` transformation of `$RUNNER_TEMP` |
| "Access Denied" to S3 bucket | OIDC role lacks permissions | Verify IAM role `gha-oidc-NVIDIA` has S3 access |
| "sccache server failed to start" | Port already in use, or misconfiguration | Check sccache logs, restart server |
| "No such file or directory: sccache" | Binary not in PATH | Verify devcontainer includes sccache |
| Missing `sccache_stats.json` | Stats not collected before job end | Check if job calls sccache stats command |

**Debugging sccache:**

Inside a devcontainer:
```bash
# Check sccache is available
which sccache

# Start sccache server manually
sccache --start-server

# Check server status
sccache --show-stats

# Verify AWS credentials are accessible
ls -la /root/.aws/
cat /root/.aws/config
# (Do NOT cat credentials in logs - security risk)

# Test S3 access
aws s3 ls s3://rapids-sccache-devs/ --region us-east-2
```

For more information on sccache configuration, see [Environment Setup](#5.4) and [Distributed Compilation Caching](#7.2).

Sources: [.github/actions/workflow-run-job-linux/action.yml:60-129](), [.github/actions/workflow-run-job-linux/action.yml:186]()

## Advanced Debugging Techniques

### Analyzing Job Timing Data

Performance issues can be diagnosed using the `job_times.json` artifact generated by `parse-job-times.py`.

**Job Timing Structure:**
```json
{
  "job_id_123": {
    "runner": "linux-amd64-gpu-v100-latest-1",
    "started": "2024-01-01T12:00:00Z",
    "completed": "2024-01-01T12:15:30Z",
    "total_seconds": 930,
    "steps": {
      "Run command": {
        "started": "2024-01-01T12:01:00Z",
        "completed": "2024-01-01T12:14:00Z",
        "duration_seconds": 780
      }
    },
    "overhead_seconds": 150
  }
}
```

**Performance Analysis:**
- **High overhead**: Indicates slow artifact download, Docker image pull, or environment setup
- **Long "Run command" duration**: Actual build/test taking longer than expected
- **Inconsistent timing**: May indicate runner resource contention

**Calculating Overhead:**

Overhead is the time spent outside the "Run command" step, calculated as:
```
overhead = total_job_time - run_command_time
```

High overhead (>20% of total time) suggests:
- Slow artifact download (producer/consumer jobs)
- Docker image pull delays (check image size, registry latency)
- Slow repository checkout (large repo or slow network)

Sources: [.github/actions/workflow-results/action.yml:92-97]()

### Inspecting the CI Wrapper Script

Every job executes through a generated `ci.sh` wrapper script that provides error handling and reproduction instructions.

**CI Wrapper Breakdown:**

```bash
#! /usr/bin/env bash
set -eo pipefail                          # Exit on error, pipe failures

echo -e "\e[1;34mRunning as '$(whoami)' user in $(pwd):\e[0m"
echo -e "\e[1;34m${COMMAND}\e[0m"

eval "${COMMAND}" || exit_code=$?         # Execute command, capture exit code

if [ ! -z "$exit_code" ]; then
  # Generate reproduction instructions
  echo -e "::group::️❗ \e[1;31mInstructions to Reproduce CI Failure Locally\e[0m"
  echo "::error:: To replicate this failure locally, follow the steps below:"
  # ... (reproduction instructions)
  exit $exit_code                         # Propagate failure
fi
```

**Key Features:**
- **Error capture**: `|| exit_code=$?` prevents immediate script exit, allowing error reporting
- **Colored output**: ANSI escape codes for visibility (stripped in CI logs)
- **GitHub annotations**: `::error::` and `::group::` directives for UI integration

**Debugging ci.sh Failures:**

If the wrapper itself fails (not the command):
1. Check that `set -eo pipefail` is not causing premature exit
2. Verify `$COMMAND` environment variable is set correctly
3. Test command evaluation: `bash -c "eval \"${COMMAND}\""`

Sources: [.github/actions/workflow-run-job-linux/action.yml:89-109]()

### Debugging Docker Networking Issues

Container networking problems can prevent access to AWS S3, GitHub, or other external services.

**Network Debugging Checklist:**

```mermaid
graph TB
    Container["Devcontainer"]
    
    Container --> DNS["Test DNS:<br/>nslookup github.com"]
    Container --> Internet["Test Internet:<br/>curl https://www.google.com"]
    Container --> S3["Test S3:<br/>aws s3 ls s3://rapids-sccache-devs/"]
    Container --> GitHub["Test GitHub API:<br/>curl -H 'Authorization: token ...' https://api.github.com/user"]
    
    DNS -.->|"fails"| DNSIssue["Check /etc/resolv.conf<br/>Docker daemon DNS settings"]
    Internet -.->|"fails"| NetworkIssue["Check Docker network mode<br/>Firewall rules"]
    S3 -.->|"fails"| AWSIssue["Check AWS credentials<br/>IAM permissions"]
    GitHub -.->|"fails"| GHIssue["Check token validity<br/>Rate limits"]
```

**Inside Container Diagnostics:**
```bash
# Check network connectivity
ping -c 3 8.8.8.8                 # Basic internet
curl -I https://github.com         # HTTPS/GitHub access
nslookup s3.us-east-2.amazonaws.com # AWS DNS

# Check container network mode
docker inspect $(hostname) | jq '.[0].HostConfig.NetworkMode'

# Review container DNS configuration
cat /etc/resolv.conf
```

Sources: [.github/actions/workflow-run-job-linux/action.yml:144-164]()

### Enabling Verbose Logging

For deep debugging, increase log verbosity in various components.

**Python Script Debugging:**

Add `--verbose` or debug prints:
```bash
# Edit the workflow-results action.yml to add verbose flags
python3 "${GITHUB_ACTION_PATH}/parse-job-times.py" --verbose workflow/workflow.json results/jobs.json
```

**Docker Execution Debugging:**

Add `set -x` to see all executed commands:
```bash
# In the ci.sh generation, change the first line to:
set -exo pipefail
```

**launch.sh Debugging:**

The `launch.sh` script already uses `set -x` at [.github/actions/workflow-run-job-linux/action.yml:143]() to show Docker command construction.

**GitHub Actions Debugging:**

Enable step debugging by setting repository secrets:
- `ACTIONS_STEP_DEBUG=true`: Detailed step logs
- `ACTIONS_RUNNER_DEBUG=true`: Runner diagnostics

Sources: [.github/actions/workflow-run-job-linux/action.yml:143-164]()

### Manual Artifact Investigation

When automated results collection fails, manually inspect artifacts using the GitHub API or CLI.

**Using GitHub CLI:**
```bash
# List all artifacts for a workflow run
gh run view <run-id> --json artifacts

# Download specific artifact
gh run download <run-id> -n workflow
gh run download <run-id> -n jobs-<job-id>

# Extract and inspect
unzip workflow.zip
cat workflow/workflow.json | jq '.jobs[] | select(.id == "job_id_123")'
```

**Artifact Analysis:**
```bash
# Check which jobs succeeded
find jobs -name 'success' -printf '%h\n' | sed 's|jobs/||'

# List jobs with sccache stats
find jobs -name 'sccache_stats.json' -printf '%h\n' | sed 's|jobs/||'

# Compare expected vs actual jobs
comm -3 \
  <(cat workflow/job_ids.json | jq -r 'keys[]' | sort) \
  <(find jobs -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)
```

Sources: [.github/actions/workflow-results/action.yml:30-57]()

---

This troubleshooting guide provides the essential diagnostic techniques for resolving issues in the CCCL GitHub Actions workflow system. For component-specific details, refer to the appropriate sections: [Workflow Generation](#3), [Job Execution](#5), and [Results and Reporting](#6). For information on extending the system, see [Development and Contributing](#9).

---

# Page: Development and Contributing

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)
- [.github/workflows/verify-devcontainers.yml](.github/workflows/verify-devcontainers.yml)

</details>



This page provides guidance for developers who want to extend, modify, or contribute to the cccl-gha workflow orchestration system. It covers development environment setup, testing procedures, and strategies for extending the system with new functionality.

For information about using the system to define CI jobs, see [Configuration Guide](#2). For troubleshooting existing workflows, see [Troubleshooting Guide](#8.4). For detailed system requirements and dependencies, see [System Requirements](#9.1).

---

## Development Workflow Overview

The development cycle for cccl-gha follows a standard modify-test-validate pattern with automated verification to ensure generated artifacts remain synchronized with their source configurations.

```mermaid
graph TB
    subgraph "Modify Configuration"
        A["Edit matrix.yaml"]
        B["Edit build-workflow.py"]
        C["Edit devcontainer configs"]
    end
    
    subgraph "Generate Artifacts"
        D["Run build-workflow.py"]
        E["Run make_devcontainers.sh"]
        F["Generated:<br/>workflow.json<br/>dispatch.json<br/>devcontainer.json files"]
    end
    
    subgraph "Local Testing"
        G["Python unit tests<br/>(if applicable)"]
        H["Dry-run workflow generation"]
        I["Manual inspection<br/>of outputs"]
    end
    
    subgraph "CI Validation"
        J["verify-devcontainers workflow"]
        K["Build & test containers"]
        L["Check artifacts up-to-date"]
    end
    
    subgraph "Merge"
        M["All checks pass"]
        N["Commit changes"]
    end
    
    A --> D
    B --> D
    C --> E
    
    D --> F
    E --> F
    
    F --> G
    F --> H
    F --> I
    
    G --> J
    H --> J
    I --> J
    
    J --> K
    J --> L
    
    K --> M
    L --> M
    
    M --> N
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:1-1140](), [.github/workflows/verify-devcontainers.yml:1-142]()

---

## Key Files and Their Relationships

Understanding which files affect which outputs is critical for making targeted modifications without unintended side effects.

```mermaid
graph LR
    subgraph "Configuration Sources"
        matrix["ci/matrix.yaml<br/>Job definitions"]
        devconf[".devcontainer/<br/>*.yaml configs"]
        makedev[".devcontainer/<br/>make_devcontainers.sh"]
    end
    
    subgraph "Generation Scripts"
        buildwf["build-workflow.py<br/>parse_workflow_matrix_jobs()<br/>preprocess_matrix_jobs()<br/>finalize_workflow_dispatch_groups()"]
        prepdisp["prepare-workflow-dispatch.py"]
    end
    
    subgraph "Generated Artifacts"
        wfjson["workflow/workflow.json"]
        dispjson["workflow/dispatch.json"]
        devjson[".devcontainer/*/<br/>devcontainer.json"]
    end
    
    subgraph "Validation"
        verifydev["verify-devcontainers.yml<br/>make_devcontainers.sh --clean<br/>git diff check"]
    end
    
    matrix --> buildwf
    buildwf --> wfjson
    wfjson --> prepdisp
    prepdisp --> dispjson
    
    devconf --> makedev
    makedev --> devjson
    
    matrix --> verifydev
    buildwf --> verifydev
    devconf --> verifydev
    devjson --> verifydev
    
    style verifydev fill:#f9f9f9
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:1-1140](), [.github/workflows/verify-devcontainers.yml:1-142]()

---

## Making Configuration Changes

### Modifying Job Definitions

To add or modify CI job configurations, edit `ci/matrix.yaml`. The structure follows a hierarchical tag-based system where jobs are defined by combinations of tags like `project`, `ctk`, `cxx`, `gpu`, etc.

```yaml
workflows:
  pull_request:
    - {project: libcudacxx, ctk: "12.0", cxx: gcc12, std: 20, gpu: v100}
```

**Key Functions in build-workflow.py:**
- [`parse_workflow_matrix_jobs(args, workflow_name)`](.github/actions/workflow-build/build-workflow.py:922-959)() - Entry point for parsing a workflow
- [`preprocess_matrix_jobs(matrix_jobs, is_exclusion_matrix)`](.github/actions/workflow-build/build-workflow.py:902-919)() - Validates, sets defaults, explodes lists
- [`validate_tags(matrix_job, ignore_required)`](.github/actions/workflow-build/build-workflow.py:811-832)() - Ensures all required tags present
- [`set_default_tags(matrix_job)`](.github/actions/workflow-build/build-workflow.py:834-843)() - Fills in default values
- [`explode_tags(matrix_job, explode_tag)`](.github/actions/workflow-build/build-workflow.py:886-899)() - Converts list values to individual jobs

**Sources:** [.github/actions/workflow-build/build-workflow.py:811-959]()

### Adding New Tags

To add a new configuration dimension (e.g., a new compiler option), modify the `tags` section in `matrix.yaml` and update the processing pipeline:

| Step | Function | Purpose |
|------|----------|---------|
| 1. Define tag | `matrix.yaml` `tags:` section | Specify `required`, `default`, validation rules |
| 2. Canonicalization | [`canonicalize_tags()`](.github/actions/workflow-build/build-workflow.py:845-849)() | Normalize aliases to canonical form |
| 3. Derived values | [`set_derived_tags()`](.github/actions/workflow-build/build-workflow.py:852-875)() | Compute dependent values (e.g., `sm` from `gpu`) |
| 4. Job generation | [`generate_dispatch_job_*()` functions](.github/actions/workflow-build/build-workflow.py:393-445)() | Use tag in name/runner/command generation |

**Sources:** [.github/actions/workflow-build/build-workflow.py:113-173](), [.github/actions/workflow-build/build-workflow.py:845-875]()

### Modifying Devcontainer Generation

Devcontainer configurations are generated from templates. To modify the generation logic:

1. Edit templates in `.devcontainer/*.yaml`
2. Update [`.devcontainer/make_devcontainers.sh`]() script
3. Run `make_devcontainers.sh --verbose --clean` to regenerate
4. Commit both templates and generated `devcontainer.json` files

**Sources:** [.github/workflows/verify-devcontainers.yml:37-49]()

---

## Testing Changes Locally

### Dry-Run Workflow Generation

Test workflow generation without triggering actual CI jobs:

```bash
# Generate workflow for pull_request jobs
python3 .github/actions/workflow-build/build-workflow.py \
  ci/matrix.yaml \
  --workflows pull_request

# Check outputs
cat workflow/workflow.json
cat workflow/job_list.txt
cat workflow/runner_summary.json
```

The script produces three key outputs:
- `workflow/workflow.json` - Complete job specifications organized by dispatch group
- `workflow/job_list.txt` - Human-readable job listing with IDs
- `workflow/runner_summary.json` - Runner allocation statistics

**Sources:** [.github/actions/workflow-build/build-workflow.py:979-1023]()

### Testing with Dirty Projects Filter

Simulate PR-triggered CI that only runs jobs for modified projects:

```bash
python3 .github/actions/workflow-build/build-workflow.py \
  ci/matrix.yaml \
  --workflows pull_request \
  --dirty-projects libcudacxx cub
```

This uses the same filtering logic as the actual CI system when `inspect-changes-script` detects modified files.

**Sources:** [.github/actions/workflow-build/build-workflow.py:947-949]()

### Validating Devcontainers

Run the verification checks locally:

```bash
# Regenerate devcontainers and check for changes
./.devcontainer/make_devcontainers.sh --verbose --clean

# Should produce no git diff
git diff --stat
git status --porcelain
```

If changes are detected, the generated files were out of sync with templates. Commit the regenerated files.

**Sources:** [.github/workflows/verify-devcontainers.yml:37-49]()

---

## CI Validation System

The `verify-devcontainers` workflow enforces that all generated files remain synchronized with their source configurations.

### Verification Workflow Architecture

```mermaid
graph TB
    subgraph "get-devcontainer-list Job"
        A["Checkout repository"]
        B["Run make_devcontainers.sh --clean"]
        C{"git diff shows<br/>changes?"}
        D["FAIL:<br/>Files out of date"]
        E["Check for relevant file changes<br/>against base_sha"]
        F{"Relevant files<br/>modified?"}
        G["skip=true<br/>No testing needed"]
        H["skip=false<br/>Enumerate devcontainers"]
    end
    
    subgraph "verify-devcontainers Matrix Job"
        I["Configure AWS credentials<br/>for sccache"]
        J["Run devcontainers/ci action"]
        K["Execute verify_devcontainer.sh<br/>inside container"]
        L["SUCCESS:<br/>Container functional"]
    end
    
    A --> B
    B --> C
    C -->|Yes| D
    C -->|No| E
    E --> F
    F -->|No| G
    F -->|Yes| H
    H --> I
    I --> J
    J --> K
    K --> L
```

**Sources:** [.github/workflows/verify-devcontainers.yml:1-142]()

### Verification Steps

**Step 1: File Synchronization Check** ([verify-devcontainers.yml:37-49]())

Ensures generated devcontainer files match their generation scripts:

```yaml
- name: Run the script to generate devcontainer files
  run: |
    ./.devcontainer/make_devcontainers.sh --verbose --clean
- name: Check for changes
  run: |
    if [[ $(git diff --stat) != '' || $(git status --porcelain | grep '^??') != '' ]]; then
      git diff --minimal
      echo "::error:: Dev Container files are out of date..."
      exit 1
    fi
```

**Step 2: Change Detection** ([verify-devcontainers.yml:50-86]())

Skips expensive container builds if no relevant files changed:

```bash
file_regex="^(.devcontainer|ci/matrix.yaml|.github/actions/workflow-build/build-workflow.py)"
relevant_dirty_files=$(echo "${all_dirty_files}" | grep -E "${file_regex}" || true)
```

**Step 3: Container Functional Testing** ([verify-devcontainers.yml:96-142]())

Builds and tests each devcontainer using `devcontainers/ci` action:

```yaml
- name: Run in devcontainer
  uses: devcontainers/ci@v0.3
  with:
    configFile: ${{ matrix.devcontainer.path }}
    runCmd: |
      .devcontainer/verify_devcontainer.sh
```

**Sources:** [.github/workflows/verify-devcontainers.yml:1-142]()

---

## Common Development Tasks

### Adding a New Job Type

To add a new job type (e.g., `benchmark`):

1. **Define in matrix.yaml:**
   ```yaml
   jobs:
     benchmark:
       name: "Benchmark"
       gpu: true
       needs: build  # Optional dependency
       invoke:
         prefix: "benchmark"
         args: ""
   ```

2. **Add script:** Create `ci/benchmark_<project>.sh` (Linux) or `ci/windows/benchmark_<project>.ps1` (Windows)

3. **Update generation logic:** The existing [`generate_dispatch_job_command()`](.github/actions/workflow-build/build-workflow.py:415-445)() will automatically handle the new job type based on the `invoke` configuration.

4. **Test:** Run `build-workflow.py --workflows pull_request` and verify the new job appears in `workflow/job_list.txt`

**Sources:** [.github/actions/workflow-build/build-workflow.py:259-281](), [.github/actions/workflow-build/build-workflow.py:415-445]()

### Adding Exclusion Rules

Exclude invalid job combinations using the `exclude` workflow:

```yaml
workflows:
  exclude:
    - {ctk: "11.0", cxx: gcc12}  # GCC 12 not available in CTK 11.0 containers
    - {cudacxx: clang, gpu: v100}  # Clang CUDA doesn't support V100
```

Exclusions are processed by [`remove_excluded_jobs()`](.github/actions/workflow-build/build-workflow.py:796-808)() which uses [`apply_matrix_job_exclusion()`](.github/actions/workflow-build/build-workflow.py:753-793)() to match and filter jobs.

**Sources:** [.github/actions/workflow-build/build-workflow.py:749-808]()

### Modifying Job Naming Convention

Job names are generated by [`generate_dispatch_job_name()`](.github/actions/workflow-build/build-workflow.py:362-376)(). To modify the format:

```python
def generate_dispatch_job_name(matrix_job, job_type):
    job_info = get_job_type_info(job_type)
    std_str = ("C++" + str(matrix_job['std']) + " ") if 'std' in matrix_job else ''
    cpu_str = matrix_job['cpu']
    gpu_str = (', ' + matrix_job['gpu'].upper()) if job_info['gpu'] else ""
    # ... build name string
    return f"[{config_tag}] {job_info['name']}({cpu_str}{gpu_str}){extra_info}"
```

Changes here affect how jobs appear in GitHub Actions UI and PR comments.

**Sources:** [.github/actions/workflow-build/build-workflow.py:362-376]()

---

## Debugging Workflow Generation

### Understanding the Pipeline

The [`preprocess_matrix_jobs()`](.github/actions/workflow-build/build-workflow.py:902-919)() function applies transformations in a specific order:

```mermaid
graph LR
    A["Raw matrix job<br/>from YAML"]
    B["validate_tags()<br/>Check required tags"]
    C["set_default_tags()<br/>Fill in defaults"]
    D["explode_tags()<br/>List → individual jobs"]
    E["canonicalize_tags()<br/>Resolve aliases"]
    F["set_derived_tags()<br/>Compute sm, std"]
    G["explode_tags() again<br/>Derived lists"]
    H["Fully specified<br/>matrix job"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:902-919]()

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing required tag 'X'` | Job definition lacks required tag | Add tag to matrix.yaml or set default in `tags:` section |
| `Unknown tag 'X'` | Typo or unregistered tag | Check spelling, add to `tags:` if new |
| `Unknown CTK version 'X'` | Version not in `ctk_versions:` | Add version or use `aka:` alias |
| `ci-dispatch-two-stage.yml currently only supports a single producer` | Multiple producers in two-stage job | Combine into single build job or use separate dispatch groups |
| Dev Container files are out of date | Generated files not committed | Run `make_devcontainers.sh --clean` and commit |

**Sources:** [.github/actions/workflow-build/build-workflow.py:811-832](), [.github/actions/workflow-build/build-workflow.py:583-599]()

### Tracing Job Generation

Each generated job includes an `origin` object with source location information:

```python
def generate_dispatch_job_origin(matrix_job, job_type):
    origin = matrix_job['origin'].copy()  # filename, line number, original input
    origin_job = matrix_job.copy()
    # Transforms tags for execution summary
    origin['matrix_job'] = origin_job
    return origin
```

This enables [`error_message_with_matrix_job()`](.github/actions/workflow-build/build-workflow.py:109-110)() to provide precise error locations:

```
ci/matrix.yaml:42 (job 3): Missing required tag 'ctk'
  Input: {project: libcudacxx, cxx: gcc12, std: 20}
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:109-110](), [.github/actions/workflow-build/build-workflow.py:448-478]()

---

## Extension Points

### Custom Tag Processing

To add custom tag processing logic, add a new function to the pipeline in [`preprocess_matrix_jobs()`](.github/actions/workflow-build/build-workflow.py:902-919)():

```python
def preprocess_matrix_jobs(matrix_jobs, is_exclusion_matrix=False):
    result = []
    for matrix_job in matrix_jobs:
        validate_tags(matrix_job)
        set_default_tags(matrix_job)
        for job in explode_tags(matrix_job):
            canonicalize_tags(job)
            set_derived_tags(job)
            # ADD CUSTOM PROCESSING HERE
            custom_tag_processing(job)
            result.extend(explode_tags(job))
    return result
```

### Custom Dispatch Strategies

The system currently supports two dispatch patterns (standalone and two-stage). To add a new pattern:

1. **Define job relationships** in [`generate_dispatch_group_jobs()`](.github/actions/workflow-build/build-workflow.py:507-539)()
2. **Create dispatch workflow** similar to `workflow-dispatch-two-stage-*.yml`
3. **Update preparation** in `prepare-workflow-dispatch.py` to split jobs accordingly

**Sources:** [.github/actions/workflow-build/build-workflow.py:507-539]()

### Runner Selection Logic

Customize runner selection by modifying [`generate_dispatch_job_runner()`](.github/actions/workflow-build/build-workflow.py:379-390)():

```python
def generate_dispatch_job_runner(matrix_job, job_type):
    runner_os = "windows" if is_windows(matrix_job) else "linux"
    cpu = matrix_job['cpu']
    
    job_info = get_job_type_info(job_type)
    if not job_info['gpu']:
        return f"{runner_os}-{cpu}-cpu16"
    
    gpu = get_gpu(matrix_job['gpu'])
    suffix = "-testing" if gpu['testing'] else ""
    
    return f"{runner_os}-{cpu}-gpu-{gpu['id']}-latest-1{suffix}"
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:379-390]()

---

## Contributing Guidelines

### Pre-Commit Checklist

Before submitting a pull request:

- [ ] Run `build-workflow.py --workflows pull_request` locally and verify output
- [ ] Run `.devcontainer/make_devcontainers.sh --clean` and commit any changes
- [ ] Ensure no `git diff` after regenerating files
- [ ] Test exclusion rules if modified
- [ ] Verify runner counts in `workflow/runner_summary.json` are reasonable
- [ ] Check that `workflow/job_list.txt` contains expected jobs

### PR Validation

All PRs automatically trigger:

1. **Devcontainer Verification** - Ensures generated files are synchronized
2. **Container Build Tests** - Validates all devcontainer configurations work
3. **Change Detection** - Skips irrelevant tests if no configuration files changed

The `verify-devcontainers` workflow uses [`inspect-changes`](.github/workflows/verify-devcontainers.yml:50-86)() to determine if testing is necessary based on file regex:

```bash
file_regex="^(.devcontainer|ci/matrix.yaml|.github/actions/workflow-build/build-workflow.py)"
```

**Sources:** [.github/workflows/verify-devcontainers.yml:50-86]()

### Code Style

- **Python**: Follow PEP 8, use meaningful function names like `canonicalize_host_compiler_name()` rather than abbreviations
- **YAML**: Use consistent indentation (2 spaces), quote string values when ambiguous
- **Shell Scripts**: Use `set -euo pipefail`, quote variables, handle errors explicitly
- **Documentation**: Update wiki pages when adding new features, include code citations

**Sources:** [.github/actions/workflow-build/build-workflow.py:1-1140]()

---

# Page: System Requirements

# System Requirements

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)
- [.github/actions/workflow-results/parse-job-times.py](.github/actions/workflow-results/parse-job-times.py)

</details>



This page documents the technical prerequisites for developing, extending, or deploying the CCCL GitHub Actions workflow orchestration system. It covers Python dependencies, GitHub Actions capabilities, Docker configurations, and external service integrations required for the system to function.

For information about testing and validation procedures, see [Testing and Validation](#9.2). For guidance on modifying the system, see [Extending the System](#9.3).

## Python Environment

The workflow generation and results processing scripts require Python 3 with specific standard library modules.

### Python Version

**Minimum Version:** Python 3.7+

The scripts use f-string syntax and type hints that require Python 3.7 or later. The system has been tested primarily with Python 3.9 and 3.10.

### Standard Library Dependencies

All Python scripts rely exclusively on the standard library. No third-party packages are required.

**Required Modules:**

| Module | Used By | Purpose |
|--------|---------|---------|
| `argparse` | build-workflow.py, parse-job-times.py, prepare-workflow-dispatch.py, prepare-execution-summary.py, final-summary.py, verify-job-success.py | Command-line argument parsing |
| `yaml` | build-workflow.py | Parse matrix.yaml configuration |
| `json` | All scripts | JSON serialization/deserialization |
| `os` | All scripts | File system operations, environment variables |
| `sys` | All scripts | System-specific parameters, stderr output |
| `re` | build-workflow.py, prepare-execution-summary.py | Regular expression pattern matching |
| `base64` | build-workflow.py | GUID generation via base64 encoding |
| `struct` | build-workflow.py | Binary data packing for GUID generation |
| `copy` | build-workflow.py | Deep copying of matrix job objects |
| `functools` | build-workflow.py | Function decorators for memoization |
| `datetime` | parse-job-times.py | Time parsing and duration calculations |

**Diagram: Python Script Dependencies**

```mermaid
graph TB
    subgraph "Core Generation Scripts"
        BuildWorkflow["build-workflow.py"]
        PrepareDispatch["prepare-workflow-dispatch.py"]
    end
    
    subgraph "Results Processing Scripts"
        ParseTimes["parse-job-times.py"]
        PrepareExec["prepare-execution-summary.py"]
        FinalSummary["final-summary.py"]
        VerifySuccess["verify-job-success.py"]
    end
    
    subgraph "Standard Library Modules"
        Yaml["yaml"]
        Json["json"]
        Argparse["argparse"]
        Os["os"]
        Sys["sys"]
        Re["re"]
        Datetime["datetime"]
        Base64["base64"]
        Functools["functools"]
    end
    
    BuildWorkflow --> Yaml
    BuildWorkflow --> Json
    BuildWorkflow --> Argparse
    BuildWorkflow --> Os
    BuildWorkflow --> Sys
    BuildWorkflow --> Re
    BuildWorkflow --> Base64
    BuildWorkflow --> Functools
    
    PrepareDispatch --> Json
    PrepareDispatch --> Argparse
    PrepareDispatch --> Os
    
    ParseTimes --> Json
    ParseTimes --> Argparse
    ParseTimes --> Datetime
    ParseTimes --> Os
    ParseTimes --> Sys
    
    PrepareExec --> Json
    PrepareExec --> Os
    PrepareExec --> Re
    
    FinalSummary --> Json
    FinalSummary --> Argparse
    FinalSummary --> Os
    
    VerifySuccess --> Os
    VerifySuccess --> Argparse
    VerifySuccess --> Sys
```

Sources: [.github/actions/workflow-build/build-workflow.py:56-65](), [.github/actions/workflow-results/parse-job-times.py:1-8]()

### File System Requirements

The scripts require read/write access to specific directories:

- **Read Access:**
  - `ci/matrix.yaml` - Job configuration definitions
  - `.devcontainer/` - Container configuration files
  - GitHub Actions artifact downloads

- **Write Access:**
  - `workflow/` directory - Generated JSON files (workflow.json, dispatch.json, job_ids.json, runner_summary.json)
  - `results/` directory - Job timing and success marker files
  - `execution/` directory - Execution summary files

Sources: [.github/actions/workflow-build/build-workflow.py:1019-1028](), [.github/actions/workflow-results/parse-job-times.py:110-111]()

## GitHub Actions Requirements

The system relies on specific GitHub Actions features and configurations.

### Required GitHub Actions Features

**Diagram: GitHub Actions Feature Dependencies**

```mermaid
graph LR
    subgraph "Workflow Features"
        Matrix["Matrix Strategy<br/>workflow-dispatch-*-group-*"]
        Needs["Job Dependencies<br/>needs: keyword"]
        Artifacts["Artifact Storage<br/>upload/download-artifact"]
        Dispatch["workflow_dispatch<br/>Manual triggers"]
        Reusable["Reusable Workflows<br/>workflow_call"]
    end
    
    subgraph "API Requirements"
        RestAPI["GitHub REST API<br/>Job metadata fetch"]
        GraphQL["GraphQL API<br/>Optional: enhanced queries"]
    end
    
    subgraph "Composite Actions"
        WorkflowBuild["workflow-build<br/>action.yml"]
        WorkflowResults["workflow-results<br/>action.yml"]
    end
    
    Matrix --> Needs
    Needs --> Artifacts
    Dispatch --> Reusable
    
    WorkflowBuild --> Matrix
    WorkflowResults --> Artifacts
    WorkflowResults --> RestAPI
```

**Feature Details:**

| Feature | Minimum Version | Purpose |
|---------|-----------------|---------|
| Matrix Strategy | GitHub Actions v2+ | Parallel job execution across multiple configurations |
| `needs:` Dependencies | GitHub Actions v2+ | Producer/consumer two-stage workflow orchestration |
| Artifacts API | GitHub Actions v2+ | Transfer build outputs between producer/consumer jobs |
| `workflow_dispatch` | GitHub Actions v2+ | Manual workflow triggers with input parameters |
| Composite Actions | GitHub Actions v2+ | Reusable action definitions (workflow-build, workflow-results) |
| GitHub REST API | v3 | Fetch job timing metadata via `/repos/{owner}/{repo}/actions/runs/{run_id}/jobs` |

Sources: Architecture diagrams (Diagram 3, Diagram 6)

### Required Permissions

GitHub Actions workflows require the following token permissions:

```yaml
permissions:
  contents: read          # Read repository code
  actions: read           # Read workflow run metadata
  pull-requests: write    # Post PR comments with results
  issues: write          # Optional: Issue comment fallback
```

The `GITHUB_TOKEN` must have sufficient permissions to:
1. Download artifacts from the current workflow run
2. Fetch job metadata via REST API
3. Post comments to pull requests (for result summaries)

Sources: [.github/actions/workflow-results/parse-job-times.py:10-15]()

### Self-Hosted Runner Requirements

The system assumes access to self-hosted runners with specific labels:

**Linux Runners:**
- `linux-amd64-cpu16` - CPU-only jobs (16 cores)
- `linux-amd64-gpu-{gpu_id}-latest-1` - GPU jobs (e.g., `linux-amd64-gpu-t4-latest-1`)
- `linux-amd64-gpu-{gpu_id}-latest-1-testing` - Testing GPU runners

**Windows Runners:**
- `windows-amd64-cpu16` - CPU-only jobs
- `windows-amd64-gpu-{gpu_id}-latest-1` - GPU jobs

The runner label format is generated by `generate_dispatch_job_runner()` in [.github/actions/workflow-build/build-workflow.py:379-390]().

Sources: [.github/actions/workflow-build/build-workflow.py:379-390]()

## Docker Requirements

The execution environment depends on Docker for container isolation and reproducibility.

### Docker Engine Version

**Minimum Version:** Docker Engine 20.10+

Required for:
- BuildKit support (used in devcontainer builds)
- Docker Compose v2 specification support
- NVIDIA Container Runtime integration (for GPU jobs)

### Docker-in-Docker (DIND) Configuration

**Diagram: Docker Environment Hierarchy**

```mermaid
graph TB
    subgraph "Host: GitHub Actions Runner"
        HostDocker["Docker Daemon<br/>/var/run/docker.sock"]
        HostGPU["NVIDIA GPU<br/>nvidia-smi"]
    end
    
    subgraph "Intermediate: ubuntu-dind Container"
        DindImage["cruizba/ubuntu-dind:jammy-26.1.3"]
        DockerCLI["Docker CLI"]
        LaunchScript[".devcontainer/launch.sh"]
        SocketMount["/var/run/docker.sock<br/>mounted from host"]
    end
    
    subgraph "Target: DevContainer"
        DevImage["rapidsai/devcontainers:<br/>{version}-cpp-{compiler}-cuda{ctk}"]
        BuildCommand["Actual command execution"]
        Sccache["sccache binary"]
    end
    
    HostDocker --> SocketMount
    HostGPU -.->|NVIDIA_VISIBLE_DEVICES| DindImage
    
    SocketMount --> DockerCLI
    DindImage --> LaunchScript
    LaunchScript -->|docker run on host daemon| DevImage
    
    DevImage --> BuildCommand
    BuildCommand --> Sccache
```

**Linux Execution Pattern (DOOD - Docker-outside-of-Docker):**

The system uses a Docker-outside-of-Docker pattern to avoid nested Docker performance issues:

1. **Host Runner:** Runs Docker daemon with GPU support
2. **Intermediate Container (`cruizba/ubuntu-dind:jammy-26.1.3`):**
   - Mounts host Docker socket at `/var/run/docker.sock`
   - Contains Docker CLI but uses host daemon
   - Executes `.devcontainer/launch.sh` script
   - Path symlinks ensure consistency between container and host paths

3. **Target DevContainer (`rapidsai/devcontainers:*`):**
   - Launched by intermediate container using host daemon
   - Contains compilers, CUDA toolkit, and build tools
   - Executes actual build/test commands

Sources: Architecture diagrams (Diagram 4), [.github/actions/workflow-build/build-workflow.py:404-412]()

### NVIDIA Container Toolkit

**Required for GPU Jobs:**

- **NVIDIA Container Toolkit:** Version 1.11.0+
- **NVIDIA Driver:** Version compatible with CUDA toolkit versions used (see matrix.yaml)
- **Docker GPU Runtime:** Must be configured as default runtime or explicitly specified

**Configuration Check:**
```bash
# Verify NVIDIA runtime is available
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

The `--gpus` flag is automatically added to GPU jobs by `.devcontainer/launch.sh` based on the `NVIDIA_VISIBLE_DEVICES` environment variable.

Sources: Architecture diagrams (Diagram 4)

### DevContainer Images

The system requires access to pre-built devcontainer images:

**Image Naming Convention:**
```
rapidsai/devcontainers:{version}-cpp-{compiler}-cuda{ctk}
```

**Example Images:**
- `rapidsai/devcontainers:24.10-cpp-gcc12-cuda11.8`
- `rapidsai/devcontainers:24.10-cpp-clang16-cuda12.0`
- `rapidsai/devcontainers:24.10-cuda12.0-cl2022` (Windows)

The `devcontainer_version` is specified in `matrix.yaml` and images are generated by `generate_dispatch_job_image()` in [.github/actions/workflow-build/build-workflow.py:404-412]().

**Windows Container Requirements:**

Windows jobs run native Docker containers (not DIND) with images using the `cl` (MSVC) compiler tag.

Sources: [.github/actions/workflow-build/build-workflow.py:404-412]()

## AWS Prerequisites

The system integrates with AWS S3 for distributed compilation caching via sccache.

### AWS S3 Bucket

**Required Bucket:**
- **Name:** Configurable (commonly `rapids-sccache-devs` or similar)
- **Region:** Should match runner location for optimal performance
- **Purpose:** Store compilation artifacts for sccache distributed caching

**Diagram: AWS Integration Flow**

```mermaid
graph LR
    subgraph "GitHub Actions Secrets"
        AccessKey["AWS_ACCESS_KEY_ID"]
        SecretKey["AWS_SECRET_ACCESS_KEY"]
        SessionToken["AWS_SESSION_TOKEN<br/>(optional)"]
    end
    
    subgraph "Job Execution"
        EnvConfig["Environment Variables<br/>in devcontainer"]
        Sccache["sccache binary<br/>compilation cache client"]
    end
    
    subgraph "AWS S3"
        Bucket["S3 Bucket<br/>rapids-sccache-devs"]
    end
    
    AccessKey --> EnvConfig
    SecretKey --> EnvConfig
    SessionToken --> EnvConfig
    
    EnvConfig --> Sccache
    Sccache <-->|GET/PUT objects| Bucket
```

### AWS Credentials

**Required GitHub Secrets:**

| Secret Name | Required | Purpose |
|-------------|----------|---------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS IAM access key for S3 authentication |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS IAM secret key for S3 authentication |
| `AWS_SESSION_TOKEN` | No | Temporary session token for role assumption |
| `AWS_REGION` | No | AWS region (defaults to `us-east-1`) |

**IAM Permissions Required:**

The AWS credentials must have the following S3 permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::rapids-sccache-devs",
        "arn:aws:s3:::rapids-sccache-devs/*"
      ]
    }
  ]
}
```

The credentials are passed to devcontainers via volume mount of `~/.aws/` directory, as configured in `.devcontainer/launch.sh`.

Sources: Architecture diagrams (Diagram 4)

### Sccache Configuration

**Environment Variables:**

The following environment variables configure sccache behavior within devcontainers:

| Variable | Value | Purpose |
|----------|-------|---------|
| `SCCACHE_BUCKET` | Bucket name | S3 bucket for cache storage |
| `SCCACHE_REGION` | AWS region | S3 bucket region |
| `SCCACHE_IDLE_TIMEOUT` | `0` | Keep sccache server running |
| `SCCACHE_S3_USE_SSL` | `true` | Use HTTPS for S3 |

These are typically set in `.devcontainer/launch.sh` before launching the target container.

Sources: Architecture diagrams (Diagram 4, Diagram 5)

## External Service Requirements

Beyond AWS, the system integrates with additional external services.

### Slack Integration

**Optional Notification Service:**

- **Webhook URL:** Stored in GitHub secret `SLACK_WEBHOOK_URL`
- **Purpose:** Post workflow results to Slack channels
- **Channels:**
  - Log channel: All workflow summaries
  - Alert channel: Failure notifications only

**Required Webhook Permissions:**
- Post to specified channels
- Upload files (for detailed logs, optional)

Slack integration is optional; workflows function without it.

Sources: Architecture diagrams (Diagram 1, Diagram 5)

### GitHub API Access

**API Endpoints Used:**

1. **Jobs API:** `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs`
   - Fetches job timing metadata
   - Used by `parse-job-times.py`
   - Requires `actions: read` permission

2. **Issues/PR Comments API:** `POST /repos/{owner}/{repo}/issues/{issue_number}/comments`
   - Posts execution summaries to PRs
   - Used by `final-summary.py`
   - Requires `pull-requests: write` permission

3. **Artifacts API:** `actions/download-artifact@v4`
   - Downloads job artifacts for results processing
   - Built-in action handles authentication

Sources: [.github/actions/workflow-results/parse-job-times.py:10-15]()

## Development Environment Setup

For local development and testing of the workflow generation system.

### Local Development Requirements

**Minimum Setup:**

```bash
# Python 3.7+ with standard library
python3 --version

# PyYAML for matrix.yaml parsing
pip install pyyaml

# Git for repository access
git --version

# Optional: Docker for testing devcontainer scripts
docker --version
```

**Testing Workflow Generation Locally:**

```bash
# Generate workflows for pull_request trigger
python3 .github/actions/workflow-build/build-workflow.py \
  ci/matrix.yaml \
  --workflows pull_request

# Inspect generated workflow.json
cat workflow/workflow.json | jq .

# Validate dispatch.json structure
python3 .github/actions/workflow-build/prepare-workflow-dispatch.py \
  workflow/workflow.json
```

Sources: [.github/actions/workflow-build/build-workflow.py:1104-1139]()

### Validation Tools

**DevContainer Verification:**

The `verify-devcontainers` workflow ensures devcontainer configurations are up-to-date:

- Requires `devcontainers/ci` GitHub Action
- Tests each devcontainer image can be built
- Validates `make_devcontainers.sh` produces no changes

**Matrix Validation:**

The `build-workflow.py` script performs extensive validation:
- Tag validation ([.github/actions/workflow-build/build-workflow.py:811-832]())
- Compiler version canonicalization ([.github/actions/workflow-build/build-workflow.py:139-172]())
- CTK version validation ([.github/actions/workflow-build/build-workflow.py:113-123]())
- Exclusion rule application ([.github/actions/workflow-build/build-workflow.py:796-808]())

Sources: [.github/actions/workflow-build/build-workflow.py:811-832](), Architecture diagrams (Diagram 7)

## Summary of Dependencies

**Diagram: Complete Dependency Graph**

```mermaid
graph TB
    subgraph "Core System"
        System["CCCL GHA<br/>Workflow Orchestration"]
    end
    
    subgraph "Runtime Requirements"
        Python["Python 3.7+<br/>Standard Library + PyYAML"]
        Docker["Docker 20.10+<br/>DIND Support"]
        GHA["GitHub Actions<br/>Matrix, Artifacts, API"]
    end
    
    subgraph "Optional Components"
        GPU["NVIDIA Container Toolkit<br/>GPU Jobs Only"]
        AWS["AWS S3 + IAM<br/>sccache Only"]
        Slack["Slack Webhook<br/>Notifications Only"]
    end
    
    subgraph "Devcontainer Images"
        Images["rapidsai/devcontainers<br/>Pre-built images"]
    end
    
    System --> Python
    System --> Docker
    System --> GHA
    
    System -.->|optional| GPU
    System -.->|optional| AWS
    System -.->|optional| Slack
    
    Docker --> Images
    GPU --> Images
```

All components are required unless marked as optional. GPU support, AWS/sccache integration, and Slack notifications can be disabled for basic workflow generation and execution.

Sources: Architecture diagrams (all diagrams), [.github/actions/workflow-build/build-workflow.py:1-1140](), [.github/actions/workflow-results/parse-job-times.py:1-130]()

---

# Page: Testing and Validation

# Testing and Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/verify-devcontainers.yml](.github/workflows/verify-devcontainers.yml)

</details>



This document covers the testing and validation infrastructure for the cccl-gha system, focusing on the `verify-devcontainers` workflow that ensures devcontainer configurations remain functional and synchronized with their generation scripts. This page describes the automated checks that prevent configuration drift and verify container buildability.

For information about devcontainer runtime execution in CI jobs, see [Devcontainer System](#5.3). For troubleshooting CI failures, see [Troubleshooting Guide](#8.4).

---

## Purpose and Scope

The testing and validation system serves three primary functions:

1. **Configuration Synchronization**: Ensures checked-in devcontainer files match their generation scripts
2. **Build Verification**: Validates that each devcontainer image can be successfully built
3. **Runtime Testing**: Confirms containers can execute basic validation commands

The system is triggered during pull requests and workflow calls, with intelligent change detection to skip validation when unrelated files are modified.

Sources: [.github/workflows/verify-devcontainers.yml:1-142]()

---

## Verification Workflow Architecture

The `verify-devcontainers.yml` workflow implements a two-stage validation process: a preliminary stage that checks file synchronization and determines which containers need testing, followed by a parallelized stage that builds and tests each devcontainer.

```mermaid
graph TB
    WorkflowCall["workflow_call<br/>verify-devcontainers.yml"]
    
    subgraph "Stage 1: get-devcontainer-list"
        Checkout1["actions/checkout@v4"]
        InstallTools["Install jq and yq"]
        MakeScript["make_devcontainers.sh --verbose --clean"]
        CheckDiff["git diff check"]
        InspectChanges["inspect-changes step<br/>Check relevant files"]
        GetList["find .devcontainer/<br/>Extract paths and names"]
        
        Checkout1 --> InstallTools
        InstallTools --> MakeScript
        MakeScript --> CheckDiff
        CheckDiff --> InspectChanges
        InspectChanges --> GetList
    end
    
    subgraph "Stage 2: verify-devcontainers"
        Matrix["Matrix Strategy<br/>fromJson(devcontainers)"]
        Checkout2["actions/checkout@v4"]
        AWSCreds["aws-actions/configure-aws-credentials"]
        SetEnv["Set SCCACHE_* env vars"]
        DevcontainerCI["devcontainers/ci@v0.3"]
        VerifyScript["verify_devcontainer.sh"]
        
        Matrix --> Checkout2
        Checkout2 --> AWSCreds
        AWSCreds --> SetEnv
        SetEnv --> DevcontainerCI
        DevcontainerCI --> VerifyScript
    end
    
    WorkflowCall --> Checkout1
    GetList -->|"outputs.devcontainers<br/>outputs.skip"| Matrix
    
    Decision{"skip == 'true'"}
    InspectChanges --> Decision
    Decision -->|Yes| SkipValidation["Skip container testing"]
    Decision -->|No| Matrix
```

**Workflow Stages**

| Stage | Job Name | Purpose | Key Outputs |
|-------|----------|---------|-------------|
| 1 | `get-devcontainer-list` | Verify file synchronization and identify containers to test | `skip`, `devcontainers` |
| 2 | `verify-devcontainers` | Build and test each devcontainer in parallel | Job success/failure status |

Sources: [.github/workflows/verify-devcontainers.yml:1-142]()

---

## File Synchronization Validation

The first critical check ensures that devcontainer configuration files remain synchronized with their generation script. This prevents manual edits from creating drift between the source-of-truth generation logic and the checked-in files.

### Generation Script Execution

The workflow executes the generation script with clean mode to regenerate all devcontainer files:

```bash
./.devcontainer/make_devcontainers.sh --verbose --clean
```

The `--clean` flag removes existing generated files before regenerating them, ensuring a pristine state. The `--verbose` flag provides detailed output for debugging failures.

**File:** [.github/workflows/verify-devcontainers.yml:37-39]()

### Diff Detection

After regeneration, the workflow checks for any modifications or untracked files:

```bash
if [[ $(git diff --stat) != '' || $(git status --porcelain | grep '^??') != '' ]]; then
  git diff --minimal
  git status --porcelain
  echo "::error:: Dev Container files are out of date or there are untracked files."
  exit 1
fi
```

This check detects two types of discrepancies:
- **Modified files**: Existing devcontainer files that differ from generated output
- **Untracked files**: New files created by the generation script that weren't committed

**File:** [.github/workflows/verify-devcontainers.yml:40-49]()

### Failure Resolution

When this check fails, developers must:
1. Run `.devcontainer/make_devcontainers.sh` locally
2. Review the generated changes
3. Commit the updated files to the pull request

Sources: [.github/workflows/verify-devcontainers.yml:37-49]()

---

## Change Detection and Conditional Execution

To optimize CI resource usage, the workflow implements intelligent change detection that skips container testing when unrelated files are modified.

```mermaid
graph LR
    BaseInput["inputs.base_sha<br/>(PR base commit)"]
    FetchHistory["git fetch origin --unshallow<br/>git fetch origin $BASE_SHA"]
    MergeBase["merge_base_sha =<br/>git merge-base"]
    
    subgraph "File Analysis"
        AllDirty["all_dirty_files =<br/>git diff --name-only"]
        Regex["file_regex =<br/>'^(.devcontainer|ci/matrix.yaml|build-workflow.py)'"]
        Filter["relevant_dirty_files =<br/>grep -E file_regex"]
    end
    
    Condition{"relevant_dirty_files<br/>empty?"}
    
    BaseInput --> FetchHistory
    FetchHistory --> MergeBase
    MergeBase --> AllDirty
    AllDirty --> Filter
    Regex --> Filter
    Filter --> Condition
    
    Condition -->|Yes| SkipOutput["skip=true"]
    Condition -->|No| ContinueOutput["skip=false"]
```

### Relevant File Patterns

The change detection logic filters for files that could affect devcontainer functionality:

| Pattern | Description |
|---------|-------------|
| `^.devcontainer` | Devcontainer configuration files and scripts |
| `ci/matrix.yaml` | Matrix definitions that determine container requirements |
| `.github/actions/workflow-build/build-workflow.py` | Workflow generation logic that may affect container selection |

**File:** [.github/workflows/verify-devcontainers.yml:72]()

### Merge Base Calculation

The workflow uses `git merge-base` to find the common ancestor between the PR head and base, ensuring accurate diff calculation even when the PR branch is behind the target branch:

```bash
merge_base_sha=$(git merge-base $GITHUB_SHA $BASE_SHA)
all_dirty_files=$(git diff --name-only "${merge_base_sha}" "${GITHUB_SHA}")
```

**File:** [.github/workflows/verify-devcontainers.yml:59-67]()

### Conditional Job Execution

The `verify-devcontainers` job consumes the `skip` output to conditionally execute:

```yaml
needs: get-devcontainer-list
if: ${{ needs.get-devcontainer-list.outputs.skip != 'true' }}
```

When skipped, the entire matrix of container tests is bypassed, saving significant compute resources on PRs that only modify documentation or non-container code.

**File:** [.github/workflows/verify-devcontainers.yml:99]()

Sources: [.github/workflows/verify-devcontainers.yml:50-86](), [.github/workflows/verify-devcontainers.yml:96-99]()

---

## Devcontainer List Extraction

The workflow dynamically discovers all devcontainer configurations in the repository and prepares them for matrix execution.

### Discovery Process

```bash
devcontainers=$(find .devcontainer/ -name 'devcontainer.json' | while read -r devcontainer; do
  jq --arg path "$devcontainer" '{path: $path, name: .name}' "$devcontainer"
done | jq -s -c .)
```

This command:
1. Finds all `devcontainer.json` files recursively under `.devcontainer/`
2. Extracts the `path` (file location) and `name` (container display name) for each
3. Combines results into a single JSON array using `jq -s -c`

**File:** [.github/workflows/verify-devcontainers.yml:91-94]()

### Output Structure

The `devcontainers` output is a JSON array of objects:

```json
[
  {
    "path": ".devcontainer/cuda11.1-gcc7/devcontainer.json",
    "name": "cuda11.1-gcc7"
  },
  {
    "path": ".devcontainer/cuda12.0-gcc11/devcontainer.json",
    "name": "cuda12.0-gcc11"
  }
]
```

This structure is consumed by the matrix strategy in the next stage.

Sources: [.github/workflows/verify-devcontainers.yml:87-94]()

---

## Parallel Container Testing

The second stage builds and tests each devcontainer using a parallelized matrix strategy with `fail-fast: false` to ensure all containers are validated even if some fail.

```mermaid
graph TB
    MatrixInput["fromJson(devcontainers)"]
    
    subgraph "Matrix Expansion"
        Job1["Job: cuda11.1-gcc7"]
        Job2["Job: cuda12.0-gcc11"]
        JobN["Job: cuda12.4-gcc13"]
    end
    
    subgraph "Per-Job Steps"
        direction TB
        Checkout["actions/checkout@v4<br/>persist-credentials: false"]
        AWS["aws-actions/configure-aws-credentials<br/>role-to-assume: gha-oidc-NVIDIA<br/>role-duration-seconds: 43200"]
        EnvVars["Set SCCACHE_* env vars<br/>BUCKET, REGION, IDLE_TIMEOUT"]
        DevCI["devcontainers/ci@v0.3<br/>push: never<br/>configFile: matrix.devcontainer.path"]
        VerifyScript[".devcontainer/verify_devcontainer.sh"]
        
        Checkout --> AWS
        AWS --> EnvVars
        EnvVars --> DevCI
        DevCI --> VerifyScript
    end
    
    MatrixInput -.-> Job1
    MatrixInput -.-> Job2
    MatrixInput -.-> JobN
    
    Job1 --> Checkout
    Job2 --> Checkout
    JobN --> Checkout
```

### Matrix Configuration

```yaml
strategy:
  fail-fast: false
  matrix:
    devcontainer: ${{fromJson(needs.get-devcontainer-list.outputs.devcontainers)}}
```

**Key Settings:**
- `fail-fast: false`: Allows all containers to be tested even if one fails, providing comprehensive coverage
- `matrix.devcontainer`: Each element contains `path` and `name` properties from the discovery phase

**File:** [.github/workflows/verify-devcontainers.yml:101-104]()

### AWS Credential Configuration

AWS credentials are configured to enable sccache functionality within the containers, preventing authentication hangs:

```yaml
- name: Get AWS credentials for sccache bucket
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::279114543810:role/gha-oidc-NVIDIA
    aws-region: us-east-2
    role-duration-seconds: 43200 # 12 hours
```

The 12-hour duration ensures credentials remain valid for long-running builds.

**File:** [.github/workflows/verify-devcontainers.yml:116-121]()

### Environment Variable Propagation

Critical environment variables are set before container execution and explicitly passed to the devcontainer:

```yaml
- name: Set environment variables
  run: |
    echo "SCCACHE_BUCKET=rapids-sccache-devs" >> $GITHUB_ENV
    echo "SCCACHE_REGION=us-east-2" >> $GITHUB_ENV
    echo "SCCACHE_IDLE_TIMEOUT=32768" >> $GITHUB_ENV
    echo "SCCACHE_S3_USE_SSL=true" >> $GITHUB_ENV
    echo "SCCACHE_S3_NO_CREDENTIALS=false" >> $GITHUB_ENV
```

These are propagated into the container via the `env:` field in `devcontainers/ci`:

```yaml
env: |
  SCCACHE_REGION=${{ env.SCCACHE_REGION }}
  AWS_ACCESS_KEY_ID=${{ env.AWS_ACCESS_KEY_ID }}
  AWS_SESSION_TOKEN=${{ env.AWS_SESSION_TOKEN }}
  AWS_SECRET_ACCESS_KEY=${{ env.AWS_SECRET_ACCESS_KEY }}
```

**Files:** [.github/workflows/verify-devcontainers.yml:122-128](), [.github/workflows/verify-devcontainers.yml:135-139]()

Sources: [.github/workflows/verify-devcontainers.yml:101-142]()

---

## Devcontainer Build and Execution

The workflow uses the `devcontainers/ci@v0.3` action to build and run each devcontainer.

### Build Configuration

```yaml
- name: Run in devcontainer
  uses: devcontainers/ci@v0.3
  with:
    push: never
    configFile: ${{ matrix.devcontainer.path }}
    runCmd: |
      .devcontainer/verify_devcontainer.sh
```

**Configuration Details:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `push` | `never` | Prevents pushing built images to registries (testing only) |
| `configFile` | `matrix.devcontainer.path` | Specifies which devcontainer.json to build |
| `runCmd` | `verify_devcontainer.sh` | Command executed inside the built container |

**File:** [.github/workflows/verify-devcontainers.yml:130-141]()

### Verification Script Execution

The `verify_devcontainer.sh` script runs inside the built container to perform runtime validation. While the script content is not provided in the available files, typical verification steps include:

- Checking compiler availability and versions
- Verifying CUDA toolkit installation (for CUDA containers)
- Testing basic build tool functionality
- Validating environment variable propagation

The script must exit with status 0 for the container to be considered valid.

### Build Failure Handling

With `fail-fast: false`, individual container build failures do not halt the entire workflow. This allows:
- Identification of multiple broken containers in a single run
- Isolation of failures to specific configurations
- Comprehensive test coverage across all devcontainers

Sources: [.github/workflows/verify-devcontainers.yml:130-142]()

---

## Permissions and Security

The workflow employs a least-privilege permission model with specific grants for required operations.

### Default Permissions

```yaml
permissions:
  contents: read
```

At the workflow level, only read access to repository contents is granted.

**File:** [.github/workflows/verify-devcontainers.yml:16-17]()

### Job-Level Permission Escalation

The `verify-devcontainers` job requires additional permissions for AWS OIDC authentication:

```yaml
permissions:
  id-token: write
  contents: read
```

**Permission Purposes:**

| Permission | Access Level | Purpose |
|------------|--------------|---------|
| `id-token` | `write` | Required for OIDC token generation for AWS authentication |
| `contents` | `read` | Required for repository checkout |

**File:** [.github/workflows/verify-devcontainers.yml:105-107]()

### Credential Management

The workflow disables credential persistence in Git checkouts to prevent credential leakage:

```yaml
uses: actions/checkout@v4
with:
  persist-credentials: false
```

This ensures that the `GITHUB_TOKEN` used for checkout is not stored in the Git configuration, preventing unauthorized access from container code.

**Files:** [.github/workflows/verify-devcontainers.yml:28-30](), [.github/workflows/verify-devcontainers.yml:109-112]()

Sources: [.github/workflows/verify-devcontainers.yml:16-17](), [.github/workflows/verify-devcontainers.yml:105-112]()

---

## Shell Configuration

The workflow enforces strict error handling through Bash shell options:

```yaml
defaults:
  run:
    shell: bash -euo pipefail {0}
```

**Shell Options:**

| Option | Effect |
|--------|--------|
| `-e` | Exit immediately if any command returns non-zero status |
| `-u` | Treat unset variables as errors |
| `-o pipefail` | Propagate failures from any command in a pipeline |

These options ensure that errors in validation scripts or commands are immediately caught and reported, preventing silent failures.

**File:** [.github/workflows/verify-devcontainers.yml:12-14]()

Sources: [.github/workflows/verify-devcontainers.yml:12-14]()

---

## Testing Strategy Summary

The verification workflow implements a multi-layered testing strategy:

```mermaid
graph TB
    subgraph "Layer 1: Static Validation"
        FileSync["File Synchronization Check<br/>make_devcontainers.sh --clean"]
        ChangeDetect["Change Detection<br/>git diff with merge-base"]
    end
    
    subgraph "Layer 2: Build Validation"
        Discovery["Container Discovery<br/>find + jq"]
        BuildTest["devcontainers/ci build<br/>for each configuration"]
    end
    
    subgraph "Layer 3: Runtime Validation"
        VerifyScript["verify_devcontainer.sh<br/>inside built container"]
    end
    
    subgraph "Layer 4: Integration Validation"
        AWSAccess["AWS sccache access"]
        EnvProp["Environment propagation"]
    end
    
    FileSync --> ChangeDetect
    ChangeDetect --> Discovery
    Discovery --> BuildTest
    BuildTest --> VerifyScript
    VerifyScript --> AWSAccess
    VerifyScript --> EnvProp
```

**Validation Layers:**

1. **Static Validation**: Ensures configuration files are synchronized and filters for relevant changes
2. **Build Validation**: Verifies each devcontainer image can be successfully built
3. **Runtime Validation**: Confirms containers can execute validation commands
4. **Integration Validation**: Tests external service integration (AWS, environment variables)

This layered approach provides comprehensive coverage while optimizing execution time through early failure detection and conditional execution.

Sources: [.github/workflows/verify-devcontainers.yml:1-142]()

---

## Usage in CI Pipelines

The `verify-devcontainers` workflow is designed to be called from other workflows using `workflow_call`:

```yaml
name: Verify devcontainers
on:
  workflow_call:
    inputs:
      base_sha:
        type: string
        description: 'For PRs, set the base SHA to conditionally run this workflow only when relevant files are modified.'
        required: false
```

**Integration Pattern:**

```yaml
# In a parent workflow (e.g., pull_request.yml)
jobs:
  verify-containers:
    uses: ./.github/workflows/verify-devcontainers.yml
    with:
      base_sha: ${{ github.event.pull_request.base.sha }}
```

**Input Parameters:**

| Input | Type | Required | Purpose |
|-------|------|----------|---------|
| `base_sha` | `string` | No | PR base commit SHA for change detection; omit to force full validation |

When `base_sha` is omitted, the workflow skips change detection and validates all devcontainers unconditionally.

**File:** [.github/workflows/verify-devcontainers.yml:3-9]()

Sources: [.github/workflows/verify-devcontainers.yml:3-9]()

---

# Page: Extending the System

# Extending the System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/workflow-build/build-workflow.py](.github/actions/workflow-build/build-workflow.py)
- [.github/actions/workflow-results/prepare-execution-summary.py](.github/actions/workflow-results/prepare-execution-summary.py)

</details>



## Purpose and Scope

This page provides guidance for developers who want to extend the cccl-gha workflow orchestration system. It covers the primary extension points and modification patterns for:

- Adding new job types (e.g., benchmark, sanitizer checks)
- Supporting new platforms (e.g., ARM64, macOS)
- Customizing dispatch logic (e.g., new execution patterns)
- Adding result processors (e.g., custom metrics, analysis)

For general system architecture understanding, see [System Architecture](#1.1). For testing extended functionality, see [Testing and Validation](#9.2). For configuration syntax reference, see [Configuration Guide](#2).

---

## Extension Point Architecture

The system has four primary extension points corresponding to its processing phases:

**Extension Point Overview**

```mermaid
graph TB
    subgraph "Configuration Extension"
        A1["matrix.yaml<br/>workflows section"]
        A2["matrix.yaml<br/>tags definition"]
        A3["matrix.yaml<br/>jobs definition"]
    end
    
    subgraph "Generation Extension"
        B1["build-workflow.py<br/>get_job_type_info()"]
        B2["build-workflow.py<br/>generate_dispatch_job_*()"]
        B3["prepare-workflow-dispatch.py<br/>split_dispatch_jobs()"]
    end
    
    subgraph "Dispatch Extension"
        C1["workflow-dispatch-*-group-*<br/>matrix strategy"]
        C2["workflow-dispatch-two-stage-*<br/>dependency orchestration"]
    end
    
    subgraph "Results Extension"
        D1["prepare-execution-summary.py<br/>update_summary_entry()"]
        D2["final-summary.py<br/>format functions"]
        D3["parse-job-times.py<br/>extract_*()"]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B1
    B1 --> C1
    B2 --> C1
    B3 --> C2
    C1 --> D1
    C2 --> D1
    D1 --> D2
    C1 --> D3
```

**Sources:** [.github/actions/workflow-build/build-workflow.py](), [.github/actions/workflow-results/prepare-execution-summary.py]()

---

## Adding New Job Types

New job types are defined through a multi-layer approach that spans configuration, generation, and execution.

### Configuration Layer

Add the job definition to `matrix.yaml` under the `jobs` section:

```yaml
jobs:
  benchmark:
    name: "Benchmark"
    gpu: true
    needs: build
    invoke:
      prefix: benchmark
      args: "--verify"
```

The job definition schema includes:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Human-readable job name (defaults to capitalized job ID) |
| `gpu` | No | Whether job requires GPU access (default: `false`) |
| `needs` | No | Producer job dependency for two-stage pattern |
| `invoke.prefix` | No | Script name prefix (default: job ID) |
| `invoke.args` | No | Additional command-line arguments |

**Sources:** [.github/actions/workflow-build/build-workflow.py:260-282]()

### Generation Layer

The `get_job_type_info()` function retrieves job configuration and applies defaults. This function is memoized for performance:

```python
@memoize_result
def get_job_type_info(job):
    if not job in matrix_yaml['jobs'].keys():
        raise Exception(f"Unknown job '{job}'...")
    
    result = matrix_yaml['jobs'][job]
    result['id'] = job
    
    # Apply defaults
    if not 'name' in result:
        result['name'] = job.capitalize()
    # ... additional defaults
```

**Key generation functions** that reference job type information:

| Function | Line Range | Purpose |
|----------|------------|---------|
| `get_job_type_info()` | [260-282]() | Retrieve and normalize job configuration |
| `generate_dispatch_job_name()` | [362-376]() | Format human-readable job display name |
| `generate_dispatch_job_runner()` | [379-391]() | Select appropriate runner based on GPU requirement |
| `generate_dispatch_job_command()` | [415-445]() | Construct invocation command with parameters |
| `generate_dispatch_group_jobs()` | [507-539]() | Organize jobs into standalone/two-stage patterns |

**Sources:** [.github/actions/workflow-build/build-workflow.py:260-539]()

### Execution Layer

Create invocation scripts that the dispatch system will call. Scripts must follow naming conventions based on the `invoke.prefix` setting:

**Linux:**
```
./ci/{prefix}_{project_id}.sh
```

**Windows:**
```
./ci/windows/{prefix}_{project_id}.ps1
```

The command generation logic automatically constructs these paths and appends standard arguments (`-std`, `-arch`, `-cuda`, `-cmake-options`):

**Sources:** [.github/actions/workflow-build/build-workflow.py:415-445]()

### Dependency Handling

If your job has a `needs` field, it will automatically be organized into a two-stage producer/consumer pattern. The `generate_dispatch_group_jobs()` function handles this:

```python
two_stage = {}  # {producer: set([consumer, ...])}
for job_type in job_types:
    job_info = get_job_type_info(job_type)
    dep = job_info['needs']
    if dep:
        if dep in two_stage:
            two_stage[dep].add(job_type)
        else:
            two_stage[dep] = set([job_type])
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:517-526]()

---

## Supporting New Platforms

### Adding New Runner Types

Runners are specified through a naming convention pattern in `generate_dispatch_job_runner()`:

```
{os}-{cpu}-{resource_type}-{details}
```

Examples:
- `linux-amd64-cpu16`
- `linux-amd64-gpu-t4-latest-1`
- `windows-amd64-cpu16`

**Runner selection logic:**

```python
def generate_dispatch_job_runner(matrix_job, job_type):
    runner_os = "windows" if is_windows(matrix_job) else "linux"
    cpu = matrix_job['cpu']
    
    job_info = get_job_type_info(job_type)
    if not job_info['gpu']:
        return f"{runner_os}-{cpu}-cpu16"
    
    gpu = get_gpu(matrix_job['gpu'])
    suffix = "-testing" if gpu['testing'] else ""
    
    return f"{runner_os}-{cpu}-gpu-{gpu['id']}-latest-1{suffix}"
```

To add ARM64 support, you would:

1. **Add CPU architecture to matrix.yaml:**

```yaml
tags:
  cpu:
    required: true
    values: ['amd64', 'arm64']
```

2. **Ensure runners exist** with naming: `linux-arm64-cpu16`

3. **Add platform-specific devcontainers** if needed (see Devcontainer System below)

**Sources:** [.github/actions/workflow-build/build-workflow.py:379-391]()

### Devcontainer System Extension

Devcontainers are constructed based on CUDA toolkit version and host compiler:

```python
def generate_dispatch_job_image(matrix_job, job_type):
    devcontainer_version = matrix_yaml['devcontainer_version']
    ctk = matrix_job['ctk']
    host_compiler = generate_dispatch_job_host_compiler(matrix_job, job_type)
    
    if is_windows(matrix_job):
        return f"rapidsai/devcontainers:{devcontainer_version}-cuda{ctk}-{host_compiler}"
    
    return f"rapidsai/devcontainers:{devcontainer_version}-cpp-{host_compiler}-cuda{ctk}"
```

The `print_devcontainer_info()` function extracts all unique CTK/compiler combinations to generate devcontainer configurations:

**Sources:** [.github/actions/workflow-build/build-workflow.py:404-413](), [.github/actions/workflow-build/build-workflow.py:1050-1085]()

### Platform Detection

Platform-specific behavior is controlled by the `is_windows()` function, which checks the host compiler's `container_tag`:

```python
def is_windows(matrix_job):
    host_compiler = get_host_compiler(matrix_job['cxx'])
    return host_compiler['container_tag'] == 'cl'
```

This affects:
- Script path selection (`.sh` vs `.ps1`)
- Devcontainer image selection
- Runner naming

To add macOS support, you would need to:

1. Add detection logic for macOS compilers
2. Update path generation for macOS scripts
3. Modify devcontainer selection (or skip containerization)
4. Update runner selection logic

**Sources:** [.github/actions/workflow-build/build-workflow.py:340-343]()

---

## Customizing Dispatch Logic

### Dispatch Group Organization

**Dispatch Group Generation Flow**

```mermaid
graph LR
    A["matrix_job"] --> B["matrix_job_to_dispatch_group()"]
    B --> C["generate_dispatch_group_name()"]
    B --> D["generate_dispatch_group_jobs()"]
    D --> E1["standalone array"]
    D --> E2["two_stage array"]
    E1 --> F["merge_dispatch_groups()"]
    E2 --> F
    F --> G["finalize_workflow_dispatch_groups()"]
    G --> H1["Deduplicate jobs"]
    G --> H2["Merge duplicate producers"]
    G --> H3["Assign unique IDs"]
    H1 --> I["Final dispatch groups"]
    H2 --> I
    H3 --> I
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:542-722]()

### Group Name Generation

Group names organize jobs in the GitHub Actions UI. The naming convention is:

```
{project_name} CTK{version} {compiler_info}
```

This is generated by `generate_dispatch_group_name()`:

```python
def generate_dispatch_group_name(matrix_job):
    project = get_project(matrix_job['project'])
    ctk = matrix_job['ctk']
    device_compiler = get_device_compiler(matrix_job)
    host_compiler = get_host_compiler(matrix_job['cxx'])
    
    compiler_info = ""
    if device_compiler['id'] == 'nvcc':
        compiler_info = f"{device_compiler['name']} {host_compiler['name']}"
    # ...
    
    return f"{project['name']} CTK{ctk} {compiler_info}"
```

To customize grouping, modify this function. For example, to group by GPU architecture:

```python
return f"{project['name']} SM{matrix_job['sm']} {compiler_info}"
```

**Sources:** [.github/actions/workflow-build/build-workflow.py:345-359]()

### Deduplication and Finalization

The `finalize_workflow_dispatch_groups()` function performs critical post-processing:

**Finalization Operations:**

| Operation | Line Range | Purpose |
|-----------|------------|---------|
| Validate single producer | [587-599]() | Ensure two-stage jobs have exactly one producer |
| Merge duplicate producers | [602-640]() | Combine consumers for identical producers |
| Remove duplicate standalones | [643-651]() | Eliminate redundant standalone jobs |
| Check producer/consumer conflicts | [654-682]() | Remove standalones that appear in two-stage |
| Assign unique IDs | [708-720]() | Generate compact GUIDs for dispatch workflows |

**Sources:** [.github/actions/workflow-build/build-workflow.py:583-722]()

### Custom Execution Patterns

To add a new execution pattern beyond standalone/two-stage:

1. **Extend the dispatch group schema** in `generate_dispatch_group_jobs()`:

```python
dispatch_group_jobs = {
    "standalone": [],
    "two_stage": [],
    "three_stage": []  # New pattern
}
```

2. **Add generation logic** for the new pattern
3. **Create corresponding dispatch workflow** (e.g., `workflow-dispatch-three-stage-*.yml`)
4. **Update `prepare-workflow-dispatch.py`** to split jobs into the new category

**Sources:** [.github/actions/workflow-build/build-workflow.py:507-539]()

---

## Adding Result Processors

### Summary Generation Architecture

**Result Processing Pipeline**

```mermaid
graph TB
    A1["Job artifacts<br/>jobs/{id}/success"] --> B1["build_summary()"]
    A2["Job artifacts<br/>jobs/{id}/sccache_stats.json"] --> B1
    A3["job_times.json"] --> B1
    
    B1 --> C1["update_summary_entry()"]
    C1 --> D1["Aggregate by project"]
    C1 --> D2["Aggregate by tag"]
    C1 --> D3["Aggregate by value"]
    
    D1 --> E["summary object"]
    D2 --> E
    D3 --> E
    
    E --> F1["get_summary_stats()"]
    E --> F2["get_tag_line()"]
    E --> F3["get_value_line()"]
    
    F1 --> G["Formatted summaries"]
    F2 --> G
    F3 --> G
    
    G --> H1["execution/heading.txt"]
    G --> H2["execution/projects/*_summary.json"]
```

**Sources:** [.github/actions/workflow-results/prepare-execution-summary.py:102-162](), [.github/actions/workflow-results/prepare-execution-summary.py:195-316]()

### Extending Summary Data

The `update_summary_entry()` function is the primary integration point for new metrics:

```python
def update_summary_entry(entry, job, job_times=None):
    # Success/failure tracking
    if job_succeeded(job):
        entry['passed'] += 1
    else:
        entry['failed'] += 1
    
    # Timing information
    if job_times:
        time_info = job_times[job["id"]]
        entry['job_time'] += time_info["job_seconds"]
        entry['command_time'] += time_info["command_seconds"]
    
    # Sccache statistics
    sccache_stats = get_sccache_stats(job["id"])
    if sccache_stats:
        # Process and aggregate
```

To add custom metrics (e.g., memory usage, code coverage):

1. **Create artifact file** in job execution: `jobs/{id}/custom_metric.json`

2. **Add retrieval function:**

```python
@functools.lru_cache(maxsize=None)
def get_custom_metric(job_id):
    metric_file = f'jobs/{job_id}/custom_metric.json'
    if os.path.exists(metric_file):
        with open(metric_file) as f:
            return json.load(f)
    return None
```

3. **Extend `update_summary_entry()`:**

```python
custom_metric = get_custom_metric(job["id"])
if custom_metric:
    if 'custom' not in entry:
        entry['custom'] = {'total': 0, 'count': 0}
    entry['custom']['total'] += custom_metric['value']
    entry['custom']['count'] += 1
```

4. **Add display formatting** in `get_summary_stats()`:

```python
if 'custom' in summary:
    custom = summary['custom']
    avg = custom['total'] / custom['count']
    stats += f' | Custom: {avg:.2f}'
```

**Sources:** [.github/actions/workflow-results/prepare-execution-summary.py:55-99](), [.github/actions/workflow-results/prepare-execution-summary.py:195-221]()

### Hierarchical Aggregation

The `build_summary()` function creates a three-level hierarchy:

1. **Overall summary** - All jobs
2. **Per-project summary** - Jobs grouped by project
3. **Per-tag-value summary** - Jobs grouped by each tag's values

This structure is built by iterating through jobs and calling `update_summary_entry()` at each level:

```python
for job in jobs:
    update_summary_entry(summary, job, job_times)
    
    matrix_job = job["origin"]["matrix_job"]
    project = matrix_job["project"]
    
    # Project level
    update_summary_entry(projects[project], job, job_times)
    
    # Tag/value level
    for tag in matrix_job.keys():
        value = str(matrix_job[tag])
        update_summary_entry(tags[tag]['values'][value], job, job_times)
```

**Sources:** [.github/actions/workflow-results/prepare-execution-summary.py:102-162]()

### Culprit Detection Logic

The system automatically identifies "likely culprits" - tag values responsible for all failures in a dimension. This is implemented through tag ranking:

```python
def rank_tag(tag_summary):
    num_values = len(tag_summary['values'])
    num_failing_values = sum(1 for v in tag_summary['values'].values() 
                            if v['failed'] > 0)
    
    if num_values > 1:
        if num_failing_values == 1:
            return 0  # Likely culprit - one failing value
        elif num_failing_values > 0 and num_failing_values < num_values:
            return 1  # Mixed results
    elif tag_failures > 0:
        return 2  # All values fail
    return 3  # No failures
```

Tags are sorted by this rank, placing likely culprits first in the output. To customize detection logic, modify the `rank_tag()` function or the flag assignment in `get_tag_line()` and `get_value_line()`.

**Sources:** [.github/actions/workflow-results/prepare-execution-summary.py:145-160](), [.github/actions/workflow-results/prepare-execution-summary.py:249-280]()

### Custom Output Formats

The final summary generation occurs in `final-summary.py` (not shown in provided files), which consumes the intermediate JSON files:

- `execution/heading.txt` - Overall status
- `execution/projects/*_summary.json` - Per-project details

To add custom output destinations:

1. **Generate additional JSON/text files** in `prepare-execution-summary.py`
2. **Create new formatting script** that reads these files
3. **Integrate into workflow-results action** by adding steps

**Sources:** [.github/actions/workflow-results/prepare-execution-summary.py:319-345]()

---

## Code Extension Checklist

When extending the system, verify modifications at each layer:

| Layer | Files to Modify | Validation |
|-------|----------------|------------|
| **Configuration** | `ci/matrix.yaml` | Schema validation in `validate_tags()` |
| **Generation** | `build-workflow.py` | Run with `--workflows test` to verify output |
| **Dispatch** | `workflow-dispatch-*.yml` | Check generated `dispatch.json` structure |
| **Execution** | `ci/*.sh`, `ci/windows/*.ps1` | Test locally or in devcontainer |
| **Results** | `prepare-execution-summary.py` | Verify output JSON structure |

**Key validation functions:**

- [build-workflow.py:811-833]() - `validate_tags()`: Ensures all required tags present
- [build-workflow.py:583-722]() - `finalize_workflow_dispatch_groups()`: Validates dispatch structure
- [prepare-execution-summary.py:12-14]() - `job_succeeded()`: Validates artifact presence

**Sources:** [.github/actions/workflow-build/build-workflow.py](), [.github/actions/workflow-results/prepare-execution-summary.py]()