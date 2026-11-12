<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/dstoolkit-mlops-v2 · page 6 CI/CD Automation · fetched 2026-11-09 -->

# CI/CD Automation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.azure-pipelines/templates/platform_ci_pipeline.yml](.azure-pipelines/templates/platform_ci_pipeline.yml)
- [.github/workflows/london_taxi_cd_pipeline.yml](.github/workflows/london_taxi_cd_pipeline.yml)
- [.github/workflows/london_taxi_ci_pipeline.yml](.github/workflows/london_taxi_ci_pipeline.yml)
- [.github/workflows/platform_cd_workflow.yml](.github/workflows/platform_cd_workflow.yml)
- [.github/workflows/platform_ci_workflow.yml](.github/workflows/platform_ci_workflow.yml)
- [.github/workflows/sequence_model_ci_pipeline.yml](.github/workflows/sequence_model_ci_pipeline.yml)
- [.github/workflows/storage_access_cleanup.yml](.github/workflows/storage_access_cleanup.yml)

</details>



## Purpose and Scope
This page provides a high-level overview of the CI/CD automation pipelines driving build, validation, training, and deployment within the Model Factory (`dstoolkit-mlops-v2`) codebase. The platform utilizes GitHub Actions as its primary automation engine, supported by legacy Azure DevOps templates during the migration phase. 

For deep technical implementation details, consult the child pages linked throughout this document.

Sources:
- [.github/workflows/platform_ci_workflow.yml:1-18]()
- [.azure-pipelines/templates/platform_ci_pipeline.yml:1-11]()

---

## Platform CI/CD Workflows
The core execution logic is centralized in platform-level workflow templates that handle multi-stage orchestration, such as `platform_ci_workflow.yml` and `platform_cd_workflow.yml`. These workflows manage Azure Workload Identity authentication, conditional storage network access toggling for secure data stores, and cleanup routines.

```mermaid
graph TD
    sub:PlatformWorkflow ["Platform CI/CD Workflows"]
        ci["Platform CI Workflow<br>`.github/workflows/platform_ci_workflow.yml`"] --> storage["Enable Storage Access<br>`enable-storage-access`"]
        ci --> val["Build Validation<br>`build-validation`"]
        ci --> ml["Execute ML Job Pipeline<br>`execute-ml-job-pipeline`"]
        
        cd["Platform CD Workflow<br>`.github/workflows/platform_cd_workflow.yml`"] --> train["Execute Training Job<br>`execute-training-job`"]
        cd --> meta["Run Metadata Extraction<br>`get_run_metadata`"]
        cd --> deploy["Deploy Online<br>`deploy-online`"]

        cleanup["Storage Access Cleanup<br>`.github/workflows/storage_access_cleanup.yml`"] --> restore["Restore Storage Restrictions<br>`az storage account update`"]
        
        ci -.->|triggers cleanup| cleanup
```
*Figure 1: Platform CI/CD Workflow Execution Structure bridging natural language concepts to workflow files.*

For details, see [Platform CI/CD Workflows](#6.1).

Sources:
- [.github/workflows/platform_ci_workflow.yml:1-153]()
- [.github/workflows/platform_cd_workflow.yml:1-100]()
- [.github/workflows/storage_access_cleanup.yml:1-142]()

---

## Build Validation & Agent Setup
Before running Azure ML pipelines, changes undergo build validation to ensure code quality, lint compliance, and dependency resolution. The platform leverages composite actions like `configure_azureml_agent` and executes validation jobs spanning Docker containers and native virtual environments.

For details, see [Build Validation & Agent Setup](#6.2).

Sources:
- [.github/workflows/platform_ci_workflow.yml:72-78]()

---

## Per-Model CI/CD Entry Workflows
Individual model types (`london_taxi`, `docker_taxi`, `sequence_model`) define their own entrypoint CI/CD workflows. These per-model files define path-based triggers (e.g., listening to changes in `src/london_src/` or `mlops/london_taxi/`) and delegate execution by calling the core platform templates.

```mermaid
graph LR
    sub:EntryTriggers ["Model-Specific Entry Workflows"]
        lt_ci["London Taxi CI<br>`london_taxi_ci_pipeline.yml`"] -->|calls| plat_ci["Platform CI Template<br>`platform_ci_workflow.yml`"]
        lt_cd["London Taxi CD<br>`london_taxi_cd_pipeline.yml`"] -->|calls| plat_cd["Platform CD Template<br>`platform_cd_workflow.yml`"]
        seq_ci["Sequence Model CI<br>`sequence_model_ci_pipeline.yml`"] -->|calls| plat_ci
```
*Figure 2: Per-Model CI/CD Pipeline Delegation mapping model entry points to platform templates.*

For details, see [Per-Model CI/CD Entry Workflows](#6.3).

Sources:
- [.github/workflows/london_taxi_ci_pipeline.yml:1-43]()
- [.github/workflows/london_taxi_cd_pipeline.yml:1-40]()
- [.github/workflows/sequence_model_ci_pipeline.yml:1-36]()

---

## Legacy Azure DevOps Pipelines
To support legacy enterprise environments, the codebase retains Azure DevOps pipeline definitions and templates under `.azure-pipelines/`. These mirror the GitHub Actions stages but are deprecated and scheduled for removal.

For details, see [Legacy Azure DevOps Pipelines](#6.4).

Sources:
- [.azure-pipelines/templates/platform_ci_pipeline.yml:1-55]()

---

## Branching Strategy & Testing
The platform enforces strict branch protection policies on `main`. Pull requests require successful build validation, unit testing under `test/`, and security scans before merging.

For details, see [Branching Strategy & Testing](#6.5).

Sources:
- [.github/workflows/london_taxi_ci_pipeline.yml:12-21]()
- [.github/workflows/sequence_model_ci_pipeline.yml:4-13]()

---

