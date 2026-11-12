<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn_projects · page 2 Core Infrastructure · fetched 2026-10-26 -->

# Core Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/build_test.yaml](.github/workflows/build_test.yaml)
- [.github/workflows/get_test_targets.sh](.github/workflows/get_test_targets.sh)
- [Dockerfile](Dockerfile)
- [docker-compose.yaml](docker-compose.yaml)
- [requirements.txt](requirements.txt)
- [rslp/config.py](rslp/config.py)
- [rslp/docker_entrypoint.py](rslp/docker_entrypoint.py)
- [rslp/landsat_vessels/Dockerfile](rslp/landsat_vessels/Dockerfile)
- [rslp/launcher_lib.py](rslp/launcher_lib.py)
- [rslp/lightning_cli.py](rslp/lightning_cli.py)
- [rslp/main.py](rslp/main.py)
- [rslp/rslearn_main.py](rslp/rslearn_main.py)
- [rslp/utils/rslearn.py](rslp/utils/rslearn.py)
- [tests/integration/forest_loss_driver/conftest.py](tests/integration/forest_loss_driver/conftest.py)
- [tests/integration/forest_loss_driver/inference/test_materialize_dataset.py](tests/integration/forest_loss_driver/inference/test_materialize_dataset.py)
- [tests/integration/forest_loss_driver/inference/test_model_predict.py](tests/integration/forest_loss_driver/inference/test_model_predict.py)
- [tests/unit/test_launcher_lib.py](tests/unit/test_launcher_lib.py)

</details>



This document covers the shared infrastructure components that support all applications within the rslearn_projects repository. The core infrastructure provides the foundational layer for dataset management, model training, containerization, and distributed job execution that all domain-specific applications build upon.

For application-specific systems that utilize this infrastructure, see [Forest Loss Driver System](#3), [Vessel Detection Systems](#4), and [Satlas System](#5). For deployment and CI/CD workflows that build upon this infrastructure, see [CI/CD and Deployment](#8).

## Infrastructure Architecture Overview

The core infrastructure consists of four primary subsystems that work together to provide a complete machine learning platform for remote sensing applications.

```mermaid
graph TB
    subgraph "Core ML Framework"
        rslearn_utils["`rslp/utils/rslearn.py`<br/>Dataset & Model Utilities"]
        lightning_cli["`CustomLightningCLI`<br/>Enhanced Training Interface"]
        base_config["`rslp/config.py`<br/>Base Configuration Classes"]
    end
    
    subgraph "Containerization Layer"
        dockerfile["`Dockerfile`<br/>Multi-stage Container Build"]
        docker_compose["`docker-compose.yaml`<br/>Local Development Setup"]
        entrypoint["`rslp/docker_entrypoint.py`<br/>Container Entry Point"]
    end
    
    subgraph "Job Management System"
        launcher_lib["`rslp/launcher_lib.py`<br/>Code & Job Management"]
        main_cli["`rslp/main.py`<br/>Workflow Dispatcher"]
        rslearn_main["`rslp/rslearn_main.py`<br/>Direct rslearn Integration"]
    end
    
    subgraph "CI/CD Pipeline"
        build_test["`build_test.yaml`<br/>GitHub Actions Workflow"]
        test_targets["`get_test_targets.sh`<br/>Smart Test Selection"]
    end
    
    rslearn_utils --> lightning_cli
    lightning_cli --> dockerfile
    launcher_lib --> entrypoint
    main_cli --> rslearn_main
    build_test --> dockerfile
    build_test --> docker_compose
    
    style rslearn_utils fill:#f9f9f9
    style lightning_cli fill:#f9f9f9
    style dockerfile fill:#f0f8ff
    style launcher_lib fill:#fff8f0
```

**Core Infrastructure Data Flow**

```mermaid
graph LR
    subgraph "Development Phase"
        code_changes["Code Changes"]
        launcher["launcher_lib.upload_code()"]
        gcs_storage[("GCS Code Storage<br/>projects/{project_id}/{experiment_id}/code.zip")]
    end
    
    subgraph "Execution Phase"
        docker_entry["docker_entrypoint.main()"]
        code_download["launcher_lib.download_code()"]
        custom_cli["CustomLightningCLI"]
        rslearn_ops["Dataset Operations<br/>materialize_dataset()<br/>run_model_predict()"]
    end
    
    subgraph "Infrastructure Services"
        checkpoint_mgmt["Checkpoint Management<br/>get_cached_checkpoint()"]
        wandb_integration["W&B Integration<br/>SaveWandbRunIdCallback"]
        cloud_storage[("Cloud Storage<br/>Checkpoints & Artifacts")]
    end
    
    code_changes --> launcher
    launcher --> gcs_storage
    gcs_storage --> docker_entry
    docker_entry --> code_download
    code_download --> custom_cli
    custom_cli --> rslearn_ops
    custom_cli --> checkpoint_mgmt
    custom_cli --> wandb_integration
    checkpoint_mgmt --> cloud_storage
    wandb_integration --> cloud_storage
```

Sources: [rslp/lightning_cli.py:1-365](), [rslp/utils/rslearn.py:1-162](), [rslp/launcher_lib.py:1-266](), [Dockerfile:1-48]()

## rslearn Framework Integration

The repository extends the core rslearn framework through a set of utility modules that provide standardized interfaces for dataset operations and model execution. The integration layer abstracts rslearn's complexity while adding project-specific functionality.

### Dataset Operations

The `rslp.utils.rslearn` module provides the primary interface for dataset lifecycle management through structured configuration classes and pipeline functions:

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `MaterializePipelineArgs` | Configuration for dataset materialization | Contains `PrepareArgs`, `IngestArgs`, `MaterializeArgs` |
| `ApplyWindowsArgs` | Parallel processing configuration | Controls workers, batch size, job distribution |
| `materialize_dataset()` | Execute complete dataset pipeline | Runs prepare → ingest → materialize sequence |
| `run_model_predict()` | Model inference execution | Wraps `CustomLightningCLI` for prediction tasks |

The materialization pipeline follows rslearn's three-stage approach:

```mermaid
graph LR
    subgraph "Dataset Materialization Pipeline"
        prepare["PrepareHandler<br/>prepare_args.retry_max_attempts<br/>prepare_args.retry_backoff"]
        ingest["IngestHandler<br/>ingest_args.ignore_errors<br/>ingest_args.retry_max_attempts"]
        materialize["MaterializeHandler<br/>materialize_args.ignore_errors<br/>materialize_args.retry_max_attempts"]
    end
    
    subgraph "Configuration Classes"
        pipeline_args["MaterializePipelineArgs"]
        prepare_args["PrepareArgs"]
        ingest_args["IngestArgs"]
        materialize_args["MaterializeArgs"]
        apply_windows["ApplyWindowsArgs"]
    end
    
    pipeline_args --> prepare_args
    pipeline_args --> ingest_args  
    pipeline_args --> materialize_args
    prepare_args --> apply_windows
    ingest_args --> apply_windows
    materialize_args --> apply_windows
    
    prepare_args --> prepare
    ingest_args --> ingest
    materialize_args --> materialize
    
    prepare --> ingest
    ingest --> materialize
```

### Model Execution Interface

The `run_model_predict()` function provides a standardized way to execute model inference across all applications:

```python
# From rslp/utils/rslearn.py:129-162
def run_model_predict(
    model_cfg_fname: str,
    ds_path: UPath,
    groups: list[str] = [],
    extra_args: list[str] = [],
) -> None
```

This function instantiates `CustomLightningCLI` with project-specific defaults and handles argument composition for different prediction scenarios.

Sources: [rslp/utils/rslearn.py:1-162](), [tests/integration/forest_loss_driver/inference/test_model_predict.py:1-90](), [tests/integration/forest_loss_driver/inference/test_materialize_dataset.py:1-94]()

## CustomLightningCLI and Training Infrastructure

The `CustomLightningCLI` class extends PyTorch Lightning's CLI with AI2-specific features for cloud-native machine learning workflows. It provides enhanced checkpoint management, experiment tracking, and distributed training capabilities.

### Enhanced Lightning CLI Features

```mermaid
graph TB
    subgraph "CustomLightningCLI Core Features"
        cli_args["CLI Arguments<br/>--rslp_project<br/>--rslp_experiment<br/>--rslp_description<br/>--autoresume<br/>--load_best"]
        checkpoint_mgmt["Checkpoint Management<br/>_get_checkpoint_path()<br/>get_cached_checkpoint()"]
        wandb_integration["W&B Integration<br/>SaveWandbRunIdCallback<br/>WandbLogger Configuration"]
    end
    
    subgraph "Cloud Storage Integration"
        gcs_checkpoints["GCS Checkpoint Storage<br/>CHECKPOINT_DIR template<br/>{rslp_prefix}/projects/{project_id}/{experiment_id}/{run_id}checkpoints/"]
        wandb_ids["W&B Run ID Storage<br/>upload_wandb_id()<br/>download_wandb_id()"]
        code_artifacts["Code Artifacts<br/>launcher_lib integration"]
    end
    
    subgraph "Training Enhancements"
        ddp_strategy["DDP Strategy<br/>find_unused_parameters=True"]
        model_checkpoint["ModelCheckpoint Callback<br/>save_last=True<br/>save_top_k=1<br/>monitor=val_loss"]
        auto_resume["Auto-resume Logic<br/>last.ckpt detection<br/>best checkpoint selection"]
    end
    
    cli_args --> checkpoint_mgmt
    checkpoint_mgmt --> gcs_checkpoints
    wandb_integration --> wandb_ids
    checkpoint_mgmt --> auto_resume
    wandb_integration --> model_checkpoint
    auto_resume --> ddp_strategy
```

### Checkpoint Management System

The checkpoint management system provides three distinct modes for handling model state:

| Mode | Flag | Behavior | Use Case |
|------|------|----------|----------|
| Default | None | Error if checkpoint exists | New training runs |
| Auto-resume | `--autoresume=true` | Resume if `last.ckpt` exists, else start fresh | Preemptible environments |
| Load Best | `--load_best=true` | Load best checkpoint, error if none exists | Inference tasks |

The checkpoint resolution logic [rslp/lightning_cli.py:171-259]() implements sophisticated best-checkpoint selection based on epoch numbering and fallback to `last.ckpt` only when no epoch-tagged checkpoints exist.

### Experiment Tracking Integration

The `SaveWandbRunIdCallback` class manages W&B run continuity across job restarts:

```mermaid
graph LR
    subgraph "W&B Integration Flow"
        fit_start["on_fit_start()"]
        get_wandb_id["wandb.run.id"]
        upload_id["launcher_lib.upload_wandb_id()"]
        config_update["wandb.config.update()"]
    end
    
    subgraph "Resume Flow"
        checkpoint_exists["Checkpoint Exists?"]
        download_id["launcher_lib.download_wandb_id()"]
        resume_run["Set trainer.logger.init_args.id"]
    end
    
    fit_start --> get_wandb_id
    get_wandb_id --> upload_id
    get_wandb_id --> config_update
    
    checkpoint_exists --> download_id
    download_id --> resume_run
```

Sources: [rslp/lightning_cli.py:1-365](), [rslp/launcher_lib.py:129-172]()

## Docker and Containerization

The containerization system provides a multi-stage Docker build that creates self-contained environments for training and inference. The system supports both local development and production deployment scenarios.

### Container Build Architecture

```mermaid
graph TB
    subgraph "Base Dependencies Layer"
        pytorch_base["pytorch/pytorch:2.5.0-cuda11.8-cudnn9-runtime"]
        system_deps["System Dependencies<br/>libpq-dev, ffmpeg, libsm6, libxext6, git, wget"]
        go_install["Go Installation<br/>go1.22.12.linux-amd64.tar.gz<br/>PATH update"]
    end
    
    subgraph "Specialized Tools Layer"
        tippecanoe["Tippecanoe Installation<br/>mapbox/tippecanoe<br/>build-essential, libsqlite3-dev, zlib1g-dev"]
        rslearn_install["rslearn Installation<br/>git clone + checkout RSLEARN_BRANCH<br/>pip install rslearn[extra]"]
    end
    
    subgraph "Application Layer"
        requirements["Requirements Installation<br/>requirements.txt"]
        code_copy["Code Copy<br/>COPY . /opt/rslearn_projects/"]
        satlas_build["Satlas Build<br/>go build smooth_point_labels_viterbi.go"]
    end
    
    pytorch_base --> system_deps
    system_deps --> go_install
    go_install --> tippecanoe
    tippecanoe --> rslearn_install
    rslearn_install --> requirements
    requirements --> code_copy
    code_copy --> satlas_build
```

### Container Entry Points

The system provides multiple entry points for different execution contexts:

| Entry Point | File | Purpose | Environment |
|-------------|------|---------|-------------|
| Docker Entry | `rslp/docker_entrypoint.py` | Production containers with code download | Beaker, distributed jobs |
| Direct Entry | `rslp/rslearn_main.py` | Local development, manual execution | Development environments |
| Workflow Dispatcher | `rslp/main.py` | Project-specific workflow execution | All environments |

The Docker entry point implements the code synchronization pattern:

```python
# From rslp/docker_entrypoint.py:6-23
def main() -> None:
    import os
    project_id = os.environ["RSLP_PROJECT"]
    experiment_id = os.environ["RSLP_EXPERIMENT"]
    from rslp.launcher_lib import download_code
    download_code(project_id, experiment_id)
    import rslp.rslearn_main
    rslp.rslearn_main.main()
```

### Development and Testing Setup

The `docker-compose.yaml` configuration provides a simplified setup for local testing and development:

- Builds the main Dockerfile without GPU requirements
- Mounts test data and provides environment variable injection
- Supports both unit and integration testing workflows

Sources: [Dockerfile:1-48](), [docker-compose.yaml:1-14](), [rslp/docker_entrypoint.py:1-28](), [rslp/rslearn_main.py:1-30]()

## Distributed Job Management and Orchestration

The job management system provides code distribution, experiment configuration, and hyperparameter sweep capabilities for distributed execution across cloud infrastructure.

### Code Distribution System

```mermaid
graph TB
    subgraph "Code Upload Phase"
        local_code["Local Code Repository"]
        make_archive["make_archive()<br/>ZIP creation with excludes"]
        code_excludes["CODE_EXCLUDES<br/>.git, __pycache__, .env, .mypy_cache<br/>lightning_logs, test_data, wandb"]
        upload_gcs["GCS Upload<br/>projects/{project_id}/{experiment_id}/code.zip"]
    end
    
    subgraph "Code Download Phase"
        container_start["Container Startup"]
        env_vars["Environment Variables<br/>RSLP_PROJECT, RSLP_EXPERIMENT"]
        download_gcs["GCS Download<br/>download_code()"]
        extract_code["Code Extraction<br/>shutil.unpack_archive()"]
    end
    
    local_code --> make_archive
    make_archive --> code_excludes
    code_excludes --> upload_gcs
    
    container_start --> env_vars
    env_vars --> download_gcs
    download_gcs --> extract_code
```

### Hyperparameter Management

The launcher library provides sophisticated hyperparameter sweep capabilities through configuration combination generation:

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `extract_parameters()` | Find list-valued parameters | Nested config dict | List of (path, values) tuples |
| `generate_combinations()` | Create parameter combinations | Base config + hyperparams | List of complete configs |
| `create_custom_configs()` | Generate config files | Config paths + output dir | Dict of run_id → config_path |

The system supports nested parameter specification and automatic cartesian product generation for comprehensive hyperparameter exploration.

### Experiment Metadata Management

W&B run ID persistence enables experiment continuity across job preemption and restart:

```python
# From rslp/launcher_lib.py:129-147
def upload_wandb_id(
    project_id: str, experiment_id: str, run_id: str | None, wandb_id: str
) -> None:
    rslp_prefix = UPath(os.environ["RSLP_PREFIX"])
    run_id_path = f"{run_id}/" if run_id else ""
    blob_path = WANDB_ID_BLOB_PATH.format(
        project_id=project_id, experiment_id=experiment_id, run_id=run_id_path
    )
    with (rslp_prefix / blob_path).open("w") as f:
        f.write(wandb_id)
```

Sources: [rslp/launcher_lib.py:1-266](), [rslp/main.py:1-76](), [tests/unit/test_launcher_lib.py:1-60]()

## CI/CD and Build Pipeline

The CI/CD system provides automated testing, container building, and artifact publishing through GitHub Actions workflows with intelligent test selection and multi-stage validation.

### Build and Test Workflow

```mermaid
graph TB
    subgraph "Build Stage"
        checkout["Checkout Repository<br/>actions/checkout@v4"]
        docker_login["Container Registry Login<br/>ghcr.io authentication"]
        metadata["Extract Metadata<br/>docker/metadata-action@v5<br/>SHA tags + latest"]
        build_push["Build and Push<br/>docker/build-push-action@v6<br/>Multi-platform support"]
    end
    
    subgraph "Test Stage"
        test_checkout["Test Checkout<br/>fetch-depth: 0"]
        gcp_auth["GCP Authentication<br/>google-github-actions/auth@v2"]
        compose_build["Docker Compose Build<br/>COMPOSE_DOCKER_CLI_BUILD=1"]
        smart_testing["Smart Test Selection<br/>get_test_targets.sh<br/>Unit + Integration"]
    end
    
    subgraph "Test Execution"
        unit_tests["Unit Tests<br/>pytest tests/unit"]
        integration_tests["Integration Tests<br/>pytest tests/integration<br/>GCS + BigTable + PubSub"]
        cleanup["Container Cleanup<br/>docker compose down"]
    end
    
    checkout --> docker_login
    docker_login --> metadata
    metadata --> build_push
    
    test_checkout --> gcp_auth
    gcp_auth --> compose_build
    compose_build --> smart_testing
    smart_testing --> unit_tests
    smart_testing --> integration_tests
    unit_tests --> cleanup
    integration_tests --> cleanup
```

### Intelligent Test Selection

The `get_test_targets.sh` script implements change-based test selection to optimize CI execution time:

```bash
# From .github/workflows/get_test_targets.sh:15-27
CHANGED_FILES=$(git diff --name-only origin/master...HEAD)

for dir in tests/$TEST_TYPE/*/; do
    dir_name=$(basename "$dir")
    if echo "$CHANGED_FILES" | grep -q "^rslp/$dir_name/"; then
        TEST_DIRS+=("tests/$TEST_TYPE/$dir_name/**")
    fi
done
```

This approach ensures that only relevant tests execute for specific application changes while maintaining comprehensive coverage for core infrastructure modifications.

### Container Registry Integration

The workflow publishes multi-tagged container images to GitHub Container Registry (GHCR):

- SHA-based tags for immutable references (`sha-<commit>`)
- Short SHA tags for convenience (`sha-<short>`)
- Latest tag for default branch commits
- Digest-based references for deployment systems

Sources: [.github/workflows/build_test.yaml:1-207](), [.github/workflows/get_test_targets.sh:1-28](), [requirements.txt:1-15]()

---

