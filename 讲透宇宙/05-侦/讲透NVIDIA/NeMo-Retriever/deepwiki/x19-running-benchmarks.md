<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-Retriever · extra page Running Benchmarks · fetched 2026-10-26 -->

# Running Benchmarks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nemo_retriever/harness/HANDOFF.md](nemo_retriever/harness/HANDOFF.md)
- [nemo_retriever/harness/examples/managed-helm-nrl-26.05.yaml](nemo_retriever/harness/examples/managed-helm-nrl-26.05.yaml)
- [nemo_retriever/harness/helm-profiles/all-optional.yaml](nemo_retriever/harness/helm-profiles/all-optional.yaml)
- [nemo_retriever/harness/helm-profiles/audio-video.yaml](nemo_retriever/harness/helm-profiles/audio-video.yaml)
- [nemo_retriever/harness/helm-profiles/core.yaml](nemo_retriever/harness/helm-profiles/core.yaml)
- [nemo_retriever/harness/helm-profiles/no-nims-external.yaml](nemo_retriever/harness/helm-profiles/no-nims-external.yaml)
- [nemo_retriever/harness/helm-profiles/split.yaml](nemo_retriever/harness/helm-profiles/split.yaml)
- [nemo_retriever/harness/test_configs.yaml](nemo_retriever/harness/test_configs.yaml)
- [nemo_retriever/harness/vidore_sweep.yaml](nemo_retriever/harness/vidore_sweep.yaml)
- [nemo_retriever/src/nemo_retriever/harness/artifacts.py](nemo_retriever/src/nemo_retriever/harness/artifacts.py)
- [nemo_retriever/src/nemo_retriever/harness/config.py](nemo_retriever/src/nemo_retriever/harness/config.py)
- [nemo_retriever/src/nemo_retriever/harness/helm_manager.py](nemo_retriever/src/nemo_retriever/harness/helm_manager.py)
- [nemo_retriever/src/nemo_retriever/harness/parsers.py](nemo_retriever/src/nemo_retriever/harness/parsers.py)
- [nemo_retriever/src/nemo_retriever/harness/run.py](nemo_retriever/src/nemo_retriever/harness/run.py)
- [nemo_retriever/src/nemo_retriever/utils/detection_summary.py](nemo_retriever/src/nemo_retriever/utils/detection_summary.py)
- [nemo_retriever/tests/test_detection_summary.py](nemo_retriever/tests/test_detection_summary.py)
- [nemo_retriever/tests/test_harness_config.py](nemo_retriever/tests/test_harness_config.py)
- [nemo_retriever/tests/test_harness_helm_manager.py](nemo_retriever/tests/test_harness_helm_manager.py)
- [nemo_retriever/tests/test_harness_run.py](nemo_retriever/tests/test_harness_run.py)

</details>



This page documents how to execute benchmark runs using the NeMo Retriever Library harness. The harness provides a CLI-driven workflow for running single benchmarks, sweeps (multiple runs in sequence), and nightly sessions with automated Slack reporting.

For information about recall evaluation metrics and adapters, see [Recall Evaluation](#5.3.2). For the overall harness architecture and artifact structure, see [Benchmarking Harness](#5.3).

## Benchmark Execution Modes

The harness supports three execution modes, each designed for different use cases:

```mermaid
graph LR
    subgraph "Single Run"
        RunCLI["retriever harness run<br/>--dataset jp20<br/>--preset single_gpu"]
        RunEntry["_run_entry()"]
        RunSingle["_run_single()"]
        RunArtifacts["Artifact Dir:<br/>jp20_20260305_120000/"]
    end
    
    subgraph "Sweep"
        SweepCLI["retriever harness sweep<br/>--runs-config nightly_config.yaml"]
        LoadRuns["load_runs_config()"]
        ExecuteRuns["execute_runs()"]
        SweepSession["Session Dir:<br/>sweep_20260305_120000/<br/>├─ run_001/<br/>├─ run_002/<br/>└─ session_summary.json"]
    end
    
    subgraph "Nightly"
        NightlyCLI["retriever harness nightly<br/>--runs-config nightly_config.yaml"]
        LoadNightly["load_nightly_config()"]
        ExecuteNightly["execute_runs()"]
        PostSlack["post_report_to_slack()"]
        NightlySession["Session Dir:<br/>nightly_20260305_120000/<br/>└─ session_summary.json"]
    end
    
    RunCLI --> RunEntry
    RunEntry --> RunSingle
    RunSingle --> RunArtifacts
    
    SweepCLI --> LoadRuns
    LoadRuns --> ExecuteRuns
    ExecuteRuns --> SweepSession
    
    NightlyCLI --> LoadNightly
    LoadNightly --> ExecuteNightly
    ExecuteNightly --> NightlySession
    ExecuteNightly --> PostSlack
```

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/run.py:515-582]()
- [nemo_retriever/harness/HANDOFF.md:40-49]()

## Single Run Command

Execute a single benchmark run with `retriever harness run`. This mode creates a standalone artifact directory and does not write session-level summaries.

### Basic Usage

```bash
# Run with preset dataset from test_configs.yaml
retriever harness run --dataset jp20 --preset single_gpu

# Run with direct dataset path
retriever harness run --dataset /datasets/nv-ingest/bo767 --preset single_gpu

# Add tags for tracking
retriever harness run --dataset jp20 --preset single_gpu --tag nightly --tag candidate

# Override specific tuning parameters
retriever harness run --dataset jp20 --preset single_gpu --override gpu_embed=0.5
```

**Sources:**
- [nemo_retriever/harness/HANDOFF.md:40-43]()
- [nemo_retriever/src/nemo_retriever/harness/run.py:515-541]()

### Command Options

The following table shows all available options for the `run` command:

| Option | Type | Description |
|--------|------|-------------|
| `--dataset` | string | Required. Dataset name from config or direct path |
| `--preset` | string | Preset name (e.g., `single_gpu`, `dgx_8gpu`) |
| `--config` | path | Path to harness test config YAML (default: `test_configs.yaml`) |
| `--run-name` | string | Optional label for the run artifact directory |
| `--override` | KEY=VALUE | Override tuning values. Repeatable |
| `--tag` | string | Run tag persisted in artifacts. Repeatable |
| `--recall-required` / `--no-recall-required` | flag | Override recall gating for this run |

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/run.py:515-541]()
- [nemo_retriever/tests/test_harness_run.py:155-171]()

### Run Execution Flow

The following diagram shows the internal flow when executing a single benchmark run:

```mermaid
graph TB
    CLI["run_command()"]
    Entry["_run_entry()"]
    LoadConfig["load_harness_config()"]
    MergeConfig["Merge: YAML → sweep → CLI → env"]
    ValidateConfig["cfg.validate()"]
    CreateArtifactDir["create_run_artifact_dir()"]
    BuildCommand["_build_command()"]
    CommandList["['python', '-m', 'nemo_retriever.examples.graph_pipeline', ...]"]
    RunSubprocess["_run_subprocess_with_tty()"]
    PTY["pty.openpty()<br/>Ray rich progress"]
    ParseMetrics["StreamMetrics.consume()"]
    CollectMetadata["_collect_run_metadata()<br/>host, gpu_count, cuda_driver"]
    EvaluateOutcome["_evaluate_run_outcome()"]
    WriteResults["write_json(results.json)"]
    
    CLI --> Entry
    Entry --> LoadConfig
    LoadConfig --> MergeConfig
    MergeConfig --> ValidateConfig
    ValidateConfig --> CreateArtifactDir
    CreateArtifactDir --> BuildCommand
    BuildCommand --> CommandList
    CommandList --> RunSubprocess
    RunSubprocess --> PTY
    PTY --> ParseMetrics
    ParseMetrics --> CollectMetadata
    CollectMetadata --> EvaluateOutcome
    EvaluateOutcome --> WriteResults
```

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/run.py:440-484]()
- [nemo_retriever/src/nemo_retriever/harness/run.py:354-437]()
- [nemo_retriever/src/nemo_retriever/harness/run.py:300-352]()

## Sweep Command

Execute multiple benchmark runs in sequence with `retriever harness sweep`. This mode creates a session directory containing individual run directories and a consolidated `session_summary.json`.

### Basic Usage

```bash
# Run all benchmarks defined in nightly_config.yaml
retriever harness sweep --runs-config nemo_retriever/harness/nightly_config.yaml

# Force a preset for all runs in the sweep
retriever harness sweep --runs-config nightly_config.yaml --preset single_gpu

# Add session tags
retriever harness sweep --runs-config nightly_config.yaml --tag nightly

# Dry run to preview the execution plan
retriever harness sweep --runs-config nightly_config.yaml --dry-run
```

**Sources:**
- [nemo_retriever/harness/HANDOFF.md:44-45]()
- [nemo_retriever/src/nemo_retriever/harness/run.py:543-582]()

### Sweep Configuration File

The sweep runs are defined in a YAML file with the following structure:

```yaml
# nemo_retriever/harness/nightly_config.yaml
preset: dgx_8gpu

runs:
  - name: jp20_dgx_8gpu
    dataset: jp20
  
  - name: bo20_dgx_8gpu
    dataset: bo20
  
  - name: earnings_dgx_8gpu
    dataset: earnings
    overrides:
      gpu_embed: 0.5
```

Each run entry supports:
- `name`: Run identifier used for the artifact directory name
- `dataset`: Dataset name or path
- `preset`: Override the top-level preset for this run
- `overrides`: Dictionary of tuning parameter overrides
- `recall_required`: Override recall gating for this run

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/config.py:328-339]()

### Sweep Execution Flow

```mermaid
graph TB
    SweepCLI["sweep_command()"]
    LoadRuns["load_runs_config()"]
    RunsList["[{name: 'r1', dataset: 'jp20'}, ...]"]
    CreateSession["create_session_dir()<br/>sweep_20260305_120000/"]
    LoopRuns["for run in runs"]
    RunEntry["_run_entry()<br/>run_name from config"]
    ArtifactDir["session_dir / run_name"]
    RunSingle["_run_single()"]
    AppendResult["run_results.append()"]
    WriteSession["write_session_summary()"]
    SessionJSON["session_summary.json"]
    
    SweepCLI --> LoadRuns
    LoadRuns --> RunsList
    RunsList --> CreateSession
    CreateSession --> LoopRuns
    LoopRuns --> RunEntry
    RunEntry --> ArtifactDir
    ArtifactDir --> RunSingle
    RunSingle --> AppendResult
    AppendResult --> LoopRuns
    LoopRuns --> WriteSession
    WriteSession --> SessionJSON
```

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/run.py:486-513]()
- [nemo_retriever/src/nemo_retriever/harness/run.py:543-582]()

## Helm Service Management

The harness includes a `HelmServiceManager` for benchmarks running in `service` mode where the harness manages the lifecycle of the NeMo Retriever service on Kubernetes.

### Managed Service Workflow

When `manage_service: true` and `run_mode: service` are configured, the harness performs the following steps:

1.  **Upgrade/Install**: Deploys the service using `helm upgrade --install` with the specified chart and values.
2.  **Service Discovery**: Resolves the main service name (falling back to a gateway if necessary).
3.  **Readiness Polling**: Polls the `/v1/health` endpoint until the service is ready.
4.  **Port Forwarding**: Establies a local port forward to the service.
5.  **Execution**: Executes the benchmark against the local forwarded port.
6.  **Teardown**: Stops port forwarding and uninstalls the Helm release (unless `keep_up: true`).

```mermaid
graph TD
    Harness["HarnessConfig<br/>manage_service=true"]
    HSM["HelmServiceManager"]
    HelmInstall["helm upgrade --install"]
    PollHealth["_poll_http_200(/v1/health)"]
    PortForward["kubectl port-forward"]
    RunBench["Execute Benchmark<br/>(service mode)"]
    Stop["HSM.stop()"]
    HelmUninstall["helm uninstall"]

    Harness --> HSM
    HSM --> HelmInstall
    HelmInstall --> PollHealth
    PollHealth --> PortForward
    PortForward --> RunBench
    RunBench --> Stop
    Stop --> HelmUninstall
```

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/helm_manager.py:1-200]()
- [nemo_retriever/tests/test_harness_helm_manager.py:49-144]()

### Helm Configuration Parameters

Key fields in `HarnessConfig` for Helm management:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `helm_chart` | None | Path or name of the Helm chart |
| `helm_release` | "nemo-retriever-harness" | Name of the Helm release |
| `helm_namespace` | None | Kubernetes namespace |
| `helm_values_file` | None | Path to a YAML values file |
| `helm_set` | {} | Dictionary of `--set` overrides |
| `helm_service_local_port` | 7670 | Local port for port-forwarding |

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/config.py:121-136]()
- [nemo_retriever/harness/examples/managed-helm-nrl-26.05.yaml:26-44]()

## Configuration System

The harness uses a multi-layer configuration system with a well-defined precedence order.

### Configuration Precedence

```mermaid
graph LR
    YAML["YAML Config<br/>test_configs.yaml"]
    Active["active: section"]
    Datasets["datasets: section"]
    Presets["presets: section"]
    Sweep["Sweep Overrides<br/>runs: overrides:"]
    CLI["CLI Overrides<br/>--override KEY=VALUE"]
    Env["Environment Variables<br/>HARNESS_*"]
    Final["Final HarnessConfig"]
    
    YAML --> Active
    YAML --> Datasets
    YAML --> Presets
    Active --> Merged["Merged Dict"]
    Datasets --> Merged
    Presets --> Merged
    Merged --> Sweep
    Sweep --> CLI
    CLI --> Env
    Env --> Final
    
    Note1["Lowest Precedence"]
    Note2["Highest Precedence"]
    YAML -.-> Note1
    Env -.-> Note2
```

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/config.py:244-325]()
- [nemo_retriever/tests/test_harness_config.py:51-76]()

### Tuning Parameters

The following tuning parameters can be overridden in presets or via CLI:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pdf_extract_workers` | 8 | Number of parallel PDF extraction tasks |
| `page_elements_workers` | 3 | Number of page-elements actors |
| `ocr_workers` | 3 | Number of OCR actors |
| `embed_workers` | 3 | Number of embedding actors |
| `gpu_page_elements` | 0.1 | GPU fraction per page-elements actor |
| `gpu_ocr` | 0.1 | GPU fraction per OCR actor |
| `gpu_embed` | 0.25 | GPU fraction per embedding actor |

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/config.py:51-68]()
- [nemo_retriever/harness/test_configs.yaml:28-45]()

## Artifact Structure

The harness generates structured artifacts for every run and session.

### Run Artifacts (results.json)

The `results.json` file is the authoritative record of a benchmark run, containing:

- **test_config**: The resolved `HarnessConfig` used for the run.
- **metrics**: Comprehensive flat dictionary of all collected metrics.
- **summary_metrics**: A curated subset of metrics for high-level reporting (pages, ingest timing, recall).
- **run_metadata**: Host info, GPU count, CUDA driver, and library versions.
- **failure_reason**: If the run failed, a string identifier for the failure (e.g., `missing_recall_metrics`).

**Sources:**
- [nemo_retriever/harness/HANDOFF.md:52-67]()
- [nemo_retriever/src/nemo_retriever/harness/run.py:390-437]()
- [nemo_retriever/tests/test_harness_run.py:64-77]()

### Detection Summary

The harness computes a deduped detection summary by reading metadata from the resulting LanceDB table or DataFrame. This provides insights into the quantity of elements (tables, charts, infographics) extracted.

- **Implementation**: `compute_detection_summary` in `nemo_retriever.utils.detection_summary`.
- **Deduplication**: Uses `(source_id, page_number)` as a key to ensure exploded rows don't double-count detections.
- **Output**: Written to a detection summary file (often hidden or in the artifact dir) and printed to stdout.

**Sources:**
- [nemo_retriever/src/nemo_retriever/utils/detection_summary.py:32-100]()
- [nemo_retriever/src/nemo_retriever/utils/detection_summary.py:157-162]()

## Pass/Fail Gating

The harness enforces pass/fail gating based on subprocess exit codes and recall requirements.

### Outcome Evaluation

```mermaid
graph TD
    Start["_evaluate_run_outcome()"]
    CheckRC["process_rc != 0?"]
    CheckRecallReq["recall_required?"]
    CheckRecallData["recall_metrics empty?"]
    
    FailRC["return_code = process_rc<br/>reason = 'subprocess_exit_N'<br/>success = false"]
    FailRecall["return_code = 98<br/>reason = 'missing_recall_metrics'<br/>success = false"]
    Pass["return_code = 0<br/>reason = ''<br/>success = true"]
    
    Start --> CheckRC
    CheckRC -->|yes| FailRC
    CheckRC -->|no| CheckRecallReq
    CheckRecallReq -->|yes| CheckRecallData
    CheckRecallReq -->|no| Pass
    CheckRecallData -->|yes| FailRecall
    CheckRecallData -->|no| Pass
```

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/run.py:269-298]()
- [nemo_retriever/tests/test_harness_run.py:29-61]()

### Recall-Required Behavior

When `recall_required: true` is set for a dataset:
1. The run must complete successfully (exit code 0).
2. Recall metrics must be present in the output (parsed via `StreamMetrics` or read from a summary JSON).
3. If recall metrics are missing despite being required, the harness returns code `98` (`missing_recall_metrics`).
4. If BEIR metrics are required but missing, the harness returns code `97` (`missing_beir_metrics`).

**Sources:**
- [nemo_retriever/src/nemo_retriever/harness/run.py:280-290]()
- [nemo_retriever/tests/test_harness_run.py:36-49]()

---

