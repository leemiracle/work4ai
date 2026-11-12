<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/dstoolkit-mlops-v2 · page 8 Glossary · fetched 2026-11-09 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.azure-pipelines/templates/platform_ci_pipeline.yml](.azure-pipelines/templates/platform_ci_pipeline.yml)
- [.github/workflows/platform_cd_workflow.yml](.github/workflows/platform_cd_workflow.yml)
- [.github/workflows/platform_ci_workflow.yml](.github/workflows/platform_ci_workflow.yml)
- [.github/workflows/storage_access_cleanup.yml](.github/workflows/storage_access_cleanup.yml)
- [config/config.yaml](config/config.yaml)
- [docs/how-to/GettingStarted.md](docs/how-to/GettingStarted.md)
- [docs/how-to/OnboardingNewModel.md](docs/how-to/OnboardingNewModel.md)
- [docs/how-to/TestInitialSetup.md](docs/how-to/TestInitialSetup.md)
- [mlops/common/config_utils.py](mlops/common/config_utils.py)
- [mlops/common/get_compute.py](mlops/common/get_compute.py)
- [mlops/common/get_environment.py](mlops/common/get_environment.py)
- [mlops/common/get_run_metadata.py](mlops/common/get_run_metadata.py)
- [mlops/common/get_workspace.py](mlops/common/get_workspace.py)
- [mlops/london_taxi/src/mlops_pipeline.py](mlops/london_taxi/src/mlops_pipeline.py)
- [mlops/sequence_model/src/mlops_pipeline.py](mlops/sequence_model/src/mlops_pipeline.py)

</details>



## Purpose and Scope

This page provides comprehensive technical definitions for codebase-specific terms, configuration parameters, orchestration constructs, and architectural patterns used across the `dstoolkit-mlops-v2` repository. Each term is tied directly to its implementation files, classes, and configuration schemas to assist developers, data scientists, and platform engineers in navigating the codebase.

---

## 1. Architectural & Platform Concepts

### Model Factory
The overarching architectural design pattern and codebase repository purpose (`dstoolkit-mlops-v2`). It standardizes the operationalization (MLOps) of Azure Machine Learning models by combining Infrastructure as Code (IaC), reproducible data pipelines, automated build validation, and multi-environment CI/CD workflows (`[docs/how-to/GettingStarted.md:1-8]()`).

### model_type
A string identifier representing the active machine learning use case or model variant being executed. Supported values in the reference repository include `london_taxi`, `docker_taxi`, and `sequence_model`. It dictates config loading, script paths, and directory resolution (`[.github/workflows/platform_ci_workflow.yml:9-11]`, `[config/config.yaml:27]()`).

### exec_environment
The target execution environment or stage (e.g., `pr`, `dev`, `ci`, `cd`) used to resolve environment-specific configuration blocks from `config.yaml` (`[.github/workflows/platform_ci_workflow.yml:6-8]`, `[config/config.yaml:12-71]()`).

### Platform CI/CD
Unified pipeline workflows implemented in GitHub Actions (`platform_ci_workflow.yml`, `platform_cd_workflow.yml`) and Azure DevOps templates that orchestrate build validation, pipeline execution, storage network security toggling, and deployment (`[.github/workflows/platform_ci_workflow.yml:1-154]`, `[.github/workflows/platform_cd_workflow.yml:1-175]()`).

### Build Validation
A pre-execution validation stage in the CI/CD pipeline that verifies dependencies, executes unit tests, performs code linting, and optionally builds Docker images prior to submitting Azure ML pipeline jobs (`[.github/workflows/platform_ci_workflow.yml:95-103]()`).

### OIDC / Workload Identity Federation
A token-based authentication mechanism allowing GitHub Actions or Azure DevOps pipelines to authenticate securely against Azure Resource Manager without storing static credentials or secrets (`[.github/workflows/platform_ci_workflow.yml:49-51]`, `[docs/how-to/GettingStarted.md:15]()`).

```mermaid
graph TD
    A["platform_ci_workflow.yml"] -->| "Inputs: model_type, exec_environment" | B["build_validation_workflow.yml"]
    B -->| "Validates code & tests" | C["execute-ml-job-pipeline"]
    C -->| "Invokes module" | D["mlops.model_type.src.mlops_pipeline"]
    
    classDef default stroke:#333,fill:#fff;
```
*Sources: [.github/workflows/platform_ci_workflow.yml:1-153](), [config/config.yaml:12-71]()*

---

## 2. Configuration & Data Layer

### MLOpsConfig
A Python utility class responsible for loading `config.yaml`, performing environment variable substitution via `os.path.expandvars`, and providing helper methods (`get_pipeline_config`, `get_deployment_config`) to extract targeted configuration blocks (`[mlops/common/config_utils.py:108-148]()`).

### DataAssetProvider
A wrapper class that manages asset retrieval from Azure ML (`ml_client.data.get`) and implements automatic fallback to synthetic data generation if registered datasets are missing or when running isolated validation checks (`[mlops/common/config_utils.py:9-106]()`).

### Synthetic Fallback
A resilience mechanism enabled via `allow_synthetic_fallback: true` in `config.yaml`. When active, if a referenced Azure ML dataset cannot be found, `DataAssetProvider` generates mock data (e.g., pickle files for sequence models) locally under `outputs/synthetic_data` (`[config/config.yaml:28-31]`, `[mlops/common/config_utils.py:58-86]()`).

### uri_folder
An Azure ML data asset type representing a folder path stored in a datastore, passed as an `Input` parameter to pipeline component definitions (`[mlops/london_taxi/src/mlops_pipeline.py:106]()`).

### workspaceblobstore
The default blob storage datastore associated with the Azure ML workspace, referenced during pipeline job configurations (`[mlops/sequence_model/src/mlops_pipeline.py:167]()`).

```mermaid
graph TD
    A["MLOpsConfig"] -->| "Parses" | B["config.yaml"]
    B -->| "Provides pipeline config" | C["DataAssetProvider"]
    C -->| "Dataset exists" | D["AzureML Data Asset (uri_folder)"]
    C -->| "Dataset missing & allow_synthetic_fallback=true" | E["_generate_synthetic_data()"]
    
    classDef default stroke:#333,fill:#fff;
```
*Sources: [config/config.yaml:12-41](), [mlops/common/config_utils.py:9-148]()*

---

## 3. Orchestration & Serving Models

### Component YAML
A declarative YAML file defining a discrete step in an Azure ML pipeline (e.g., prep, transform, train, predict, score, register), specifying its inputs, outputs, command script, and environment (`[mlops/london_taxi/src/mlops_pipeline.py:101]()`).

### Batch vs Online Deployment
* **Online Deployment**: Real-time HTTP scoring endpoints backed by managed virtual machine instances (`deployment_vm_size`) running a scoring script (`score.py`) for low-latency inference (`[config/config.yaml:93-106]()`).
* **Batch Deployment**: Asynchronous, cluster-backed job processing designed to score large datasets stored in blob storage in parallel chunks (`mini_batch_size`) (`[config/config.yaml:73-92]()`).

### approve_model
A governance and promotion step or tag applied to registered models in Azure ML/MLflow, designating them as approved for production staging or automated deployment workflows.

```mermaid
graph TD
    A["mlops_pipeline.py"] -->| "Loads component" | B["component.yml"]
    B -->| "Executes training & registration" | C["Azure ML Registered Model"]
    C -->| "CD Workflow" | D{ "Deployment Target" }
    D -->| "IS_ONLINE_DEPLOYMENT" | E["Online Endpoint (score.py)"]
    D -->| "IS_BATCH_DEPLOYMENT" | F["Batch Endpoint (score.py)"]
    
    classDef default stroke:#333,fill:#fff;
```
*Sources: [config/config.yaml:73-173](), [mlops/london_taxi/src/mlops_pipeline.py:101-114]()*

---

## Terminology Quick Reference

| Term | Category | Primary Code Entity / File | Description |
| :--- | :--- | :--- | :--- |
| `Model Factory` | Architecture | Repository Root | Solution template for Azure ML operationalization. |
| `model_type` | Configuration | `[config/config.yaml:27]()` | Discriminator for model workflows (`london_taxi`, etc.). |
| `exec_environment` | Pipeline | `[.github/workflows/platform_ci_workflow.yml:6-8]()` | Environment selector (`pr`, `dev`). |
| `MLOpsConfig` | Python Class | `[mlops/common/config_utils.py:108-148]()` | YAML configuration parser and resolver. |
| `DataAssetProvider`| Data Management | `[mlops/common/config_utils.py:9-106]()` | Resolves Azure ML datasets with fallback support. |
| `uri_folder` | Azure ML | `[mlops/london_taxi/src/mlops_pipeline.py:106]()` | Folder-type dataset reference. |
| `workspaceblobstore`| Infrastructure | `[mlops/sequence_model/src/mlops_pipeline.py:167]()` | Default workspace blob storage datastore. |
| `Component YAML` | Orchestration | `[mlops/london_taxi/components/prep.yml]()` | Step definition file for Azure ML pipelines. |

*Sources: [config/config.yaml:27-167](), [mlops/common/config_utils.py:9-148](), [mlops/london_taxi/src/mlops_pipeline.py:101-106]()