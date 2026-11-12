<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cccl-gha · page 8 Reference · fetched 2026-10-26 -->

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

