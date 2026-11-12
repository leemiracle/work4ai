<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/spark-rapids-common · page 1 Spark RAPIDS Common Overview · fetched 2026-10-26 -->

# Spark RAPIDS Common Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of the `spark-rapids-common` repository, which serves as a centralized hub for reusable GitHub Actions, workflows, and common scripts used across the NVIDIA Spark RAPIDS ecosystem. The repository standardizes quality gates, project management automation, and development workflows to ensure consistency across multiple Spark RAPIDS projects.

For detailed information about specific quality validation systems, see [Quality Gates System](#2). For project management features, see [Project Management](#3). For automated merging capabilities, see [Automated Merging System](#4).

## Repository Architecture

The `spark-rapids-common` repository follows a modular architecture that separates reusable GitHub Actions from their consuming workflows. This design enables external repositories to reference standardized automation while maintaining flexibility in their specific implementations.

### Repository Structure Overview

```mermaid
graph TD
    subgraph "spark-rapids-common Repository Root"
        subgraph ".github/"
            subgraph "workflows/"
                WF1["license-header-check.yml"]
                WF2["markdown-link-check.yml"] 
                WF3["signoff.yml"]
                WF4["shell-check.yml"]
                WF5["pr-desc-check.yml"]
                WF6["auto-merge.yml"]
                WF7["add-to-project.yml"]
            end
            CODEOWNERS[".github/CODEOWNERS"]
            subgraph "ISSUE_TEMPLATE/"
                IT1["bug_report.md"]
                IT2["feature_request.md"]
            end
        end
        
        subgraph "Action Directories"
            A1["license-header-check/"]
            A2["markdown-link-check/"]
            A3["signoff-check/"]
            A4["shell-check/"]
            A5["pr-description-check/"]
            A6["add-to-project/"]
            A7["auto-merge/"]
            A8["action-helper/"]
            A9["checkout/"]
        end
        
        README["README.md"]
        CONTRIB["CONTRIBUTING.md"]
    end
```

**Sources:** [README.md:1-8]()

### Action Implementation Patterns

The repository implements three distinct architectural patterns for GitHub Actions, each optimized for different use cases and complexity levels.

```mermaid
graph TD
    subgraph "Composite Actions"
        CA1["license-header-check/action.yml"] --> CS1["runs: composite"]
        CA2["markdown-link-check/action.yml"] --> CS2["runs: composite"]
        CA3["shell-check/action.yml"] --> CS3["runs: composite"]
        CA4["pr-description-check/action.yml"] --> CS4["runs: composite"]
    end
    
    subgraph "Docker Actions"
        DA1["signoff-check/action.yml"] --> DD1["runs: docker"]
        DA2["auto-merge/action.yml"] --> DD2["runs: docker"]
        DA3["action-helper/action.yml"] --> DD3["runs: docker"]
        
        DD1 --> DF1["signoff-check/Dockerfile"]
        DD2 --> DF2["auto-merge/Dockerfile"] 
        DD3 --> DF3["action-helper/Dockerfile"]
    end
    
    subgraph "Wrapper Actions"
        WA1["checkout/action.yml"] --> WS1["runs: composite"]
        WA2["add-to-project/action.yml"] --> WS2["runs: composite"]
        
        WS1 --> UA1["actions/checkout@v4"]
        WS2 --> UA2["actions/add-to-project@v1.0.2"]
    end
```

**Sources:** [README.md:7]()

## Core Functionality

The repository provides three primary categories of functionality that support the entire Spark RAPIDS development lifecycle.

### Quality Assurance Pipeline

The quality assurance system implements multiple validation layers that execute in parallel during pull request events, ensuring code quality and legal compliance before merge approval.

| Action | Pattern | Primary Function | Consumer Usage |
|--------|---------|------------------|----------------|
| `license-header-check` | Composite | Validates NVIDIA copyright headers | `uses: NVIDIA/spark-rapids-common/license-header-check@main` |
| `markdown-link-check` | Composite | Validates markdown link integrity | `uses: NVIDIA/spark-rapids-common/markdown-link-check@main` |
| `signoff-check` | Docker | Enforces DCO sign-off compliance | `uses: NVIDIA/spark-rapids-common/signoff-check@main` |
| `shell-check` | Composite | Static analysis for shell scripts | `uses: NVIDIA/spark-rapids-common/shell-check@main` |
| `pr-description-check` | Composite | Validates PR description format | `uses: NVIDIA/spark-rapids-common/pr-description-check@main` |

### Project Management Automation

Project management components handle issue tracking, code ownership, and GitHub project board integration to streamline development workflows.

### Automated Branch Management

The automated merging system maintains branch currency and handles complex merge scenarios through Docker-based actions that interact with the GitHub API.

## Integration Patterns

### Cross-Repository Usage Flow

External repositories integrate with `spark-rapids-common` by referencing specific actions in their workflow files, creating a distributed but standardized development environment.

```mermaid
sequenceDiagram
    participant ExtRepo as "External Repository"
    participant GHA as "GitHub Actions Runner" 
    participant Common as "spark-rapids-common Actions"
    participant GitHub as "GitHub API"
    
    ExtRepo->>GHA: "Pull request event triggers workflow"
    GHA->>Common: "uses: NVIDIA/spark-rapids-common/license-header-check@main"
    Common->>Common: "Execute composite steps"
    Common->>GHA: "Return success/failure status"
    
    GHA->>Common: "uses: NVIDIA/spark-rapids-common/signoff-check@main"  
    Common->>GitHub: "Query commit signatures via API"
    GitHub->>Common: "Return DCO compliance status"
    Common->>GHA: "Return validation result"
    
    GHA->>ExtRepo: "Update pull request status checks"
```

**Sources:** [README.md:7]()

### Action Composition Architecture

Each action directory contains standardized files that define inputs, outputs, and execution logic, enabling consistent behavior across different repository contexts.

```mermaid
graph LR
    subgraph "Action Directory Structure"
        ActionYML["action.yml"] --> Inputs["inputs: parameters"]
        ActionYML --> Outputs["outputs: results"]
        ActionYML --> Runs["runs: execution_type"]
        
        subgraph "Composite Actions"
            Runs --> Steps["steps: - uses: actions/*"]
        end
        
        subgraph "Docker Actions"
            Runs --> Dockerfile["Dockerfile"]
            Dockerfile --> Scripts["entrypoint scripts"]
        end
    end
    
    subgraph "Consumer Workflow"
        WorkflowYML["workflow.yml"] --> Job["job: quality-checks"]
        Job --> Uses["uses: NVIDIA/spark-rapids-common/ACTION@main"]
        Uses --> With["with: input_parameters"]
    end
    
    Uses --> ActionYML
```

**Sources:** [README.md:7]()

## Repository Impact and Usage

The `spark-rapids-common` repository serves as a foundational component that standardizes development practices across the NVIDIA Spark RAPIDS ecosystem. By centralizing quality gates and automation workflows, it ensures consistent code quality, legal compliance, and project management practices across multiple consumer repositories.

Consumer projects benefit from this centralized approach by reducing duplicate workflow maintenance, ensuring consistent validation standards, and providing immediate access to updates and improvements in the shared automation infrastructure.

**Sources:** [README.md:1-8]()

---

