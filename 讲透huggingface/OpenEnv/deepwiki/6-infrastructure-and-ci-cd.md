<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/OpenEnv · page 6 Infrastructure and CI/CD · fetched 2026-10-26 -->

# Infrastructure and CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE/release.md](.github/PULL_REQUEST_TEMPLATE/release.md)
- [.github/workflows/build_documentation.yml](.github/workflows/build_documentation.yml)
- [.github/workflows/build_pr_documentation.yml](.github/workflows/build_pr_documentation.yml)
- [.github/workflows/deploy-hf-env.yml](.github/workflows/deploy-hf-env.yml)
- [.github/workflows/discovery-catalog.yml](.github/workflows/discovery-catalog.yml)
- [.github/workflows/docker-build.yml](.github/workflows/docker-build.yml)
- [.github/workflows/manage-hf-collection.yml](.github/workflows/manage-hf-collection.yml)
- [.github/workflows/openspiel_base_build.yml](.github/workflows/openspiel_base_build.yml)
- [.github/workflows/package-ci.yml](.github/workflows/package-ci.yml)
- [.github/workflows/publish-pypi.yml](.github/workflows/publish-pypi.yml)
- [.github/workflows/publish-testpypi.yml](.github/workflows/publish-testpypi.yml)
- [.github/workflows/test.yml](.github/workflows/test.yml)
- [.github/workflows/upload_pr_documentation.yml](.github/workflows/upload_pr_documentation.yml)
- [.github/workflows/validation-runtime.yml](.github/workflows/validation-runtime.yml)

</details>



The OpenEnv infrastructure is designed to support a highly distributed, containerized ecosystem where environments can be built, tested, and deployed independently or as a unified collection. The system relies on a multi-tier Docker hierarchy, comprehensive GitHub Actions workflows, automated Hugging Face Spaces publishing, and rigorous validation runtimes.

For details on specific areas, see the child pages:
- [Docker Image Pipeline](#6.1)
- [Hugging Face Spaces Deployment](#6.2)
- [Testing and CI](#6.3)
- [Environment Validation Framework](#6.4)

## Deployment Pipeline Overview

The deployment pipeline automates the transition from local development to production-ready Hugging Face Spaces and container registries. It handles version pinning, dependency resolution, lockfile validation, and metadata generation across the environment catalog.

### Environment Deployment Flow
The following diagram illustrates the relationship between the local codebase, CI/CD workflows, artifact registries, and Hugging Face Spaces.

**Deployment Architecture**
```mermaid
graph TD
    subgraph "Source Control (GitHub)"
        [REPO_ROOT] --> [envs_dir]
        [REPO_ROOT] --> [core_src]
    end

    subgraph "CI/CD (GitHub Actions)"
        [docker-build.yml] --> |"build-base"| [openenv-base]
        [docker-build.yml] --> |"build-envs"| [env-specific-images]
        [deploy-hf-env.yml] --> [prepare_hf_deployment.sh]
        [validation-runtime.yml] --> [reproduce.py]
    end

    subgraph "Artifact Registries"
        [openenv-base] --> [GHCR]
        [env-specific-images] --> [GHCR]
    end

    subgraph "Production and Validation"
        [prepare_hf_deployment.sh] --> |"Staging"| [hf-staging]
        [hf-staging] --> |"Push"| [HF_Spaces]
        [manage_hf_collection.py] --> |"Update"| [HF_Collection]
    end

    [core_src] -.-> [openenv-base]
    [envs_dir] -.-> [env-specific-images]
```
Sources: [.github/workflows/docker-build.yml:1-17](), [.github/workflows/deploy-hf-env.yml:43-114](), [.github/workflows/validation-runtime.yml:13-52]()

## Docker Image Hierarchy

OpenEnv utilizes a two-tier Docker build strategy to minimize build times and ensure consistency across diverse environments. The foundational `openenv-base` image contains the core library and common system dependencies, while individual environment images build upon it [.github/workflows/docker-build.yml:18-62](). Specialized environments like `openspiel_env` leverage intermediate base images (`openspiel-base`) to pre-compile heavy C++ dependencies [.github/workflows/openspiel_base_build.yml:60-63]().

For details, see [Docker Image Pipeline](#6.1).

Sources: [.github/workflows/docker-build.yml:1-154](), [.github/workflows/openspiel_base_build.yml:1-110]()

## Hugging Face Spaces Management

Deployment to Hugging Face Spaces is orchestrated via the `deploy-hf-env.yml` workflow and `scripts/prepare_hf_deployment.sh` [.github/workflows/deploy-hf-env.yml:1-114](). This pipeline stages environments, ensures correct dependency pinning, and pushes version-suffixed spaces [.github/workflows/deploy-hf-env.yml:21-25](). Nightly and scheduled syncs via `manage_hf_collection.py` update central Hugging Face collections [.github/workflows/manage-hf-collection.yml:1-58]().

For details, see [Hugging Face Spaces Deployment](#6.2).

Sources: [.github/workflows/deploy-hf-env.yml:1-114](), [.github/workflows/manage-hf-collection.yml:1-58]()

## Testing and CI

The CI infrastructure guarantees correctness across core abstractions, environments, and packaging. Workflows include `test.yml` for pull requests and pushes [.github/workflows/test.yml:1-105](), environment-specific lockfile checks [.github/workflows/test.yml:19-66](), documentation builds [.github/workflows/build_documentation.yml:1-18](), discovery catalog generation [.github/workflows/discovery-catalog.yml:1-57](), and PyPI publishing via `publish-pypi.yml` [.github/workflows/publish-pypi.yml:1-160]().

For details, see [Testing and CI](#6.3).

Sources: [.github/workflows/test.yml:1-215](), [.github/workflows/publish-pypi.yml:1-160](), [.github/workflows/discovery-catalog.yml:1-57]()

## Environment Validation Framework

OpenEnv features a dedicated validation runtime (`tests/validation_runtime`) executed through `validation-runtime.yml` [.github/workflows/validation-runtime.yml:1-52](). It verifies protocols, runs exact-wheel Docker acceptance suites via `scripts/validation/reproduce.py`, and inspects evidence bundles [.github/workflows/validation-runtime.yml:34-44]().

For details, see [Environment Validation Framework](#6.4).

Sources: [.github/workflows/validation-runtime.yml:1-52]()

---

