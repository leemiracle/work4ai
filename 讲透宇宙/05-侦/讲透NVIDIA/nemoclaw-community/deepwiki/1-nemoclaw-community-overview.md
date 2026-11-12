<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nemoclaw-community · page 1 NemoClaw Community — Overview · fetched 2026-10-26 -->

# NemoClaw Community — Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SUPPORT.md](SUPPORT.md)
- [examples/README.md](examples/README.md)
- [examples/recipes/partners/bluetier/x402-payment-gate/.dockerignore](examples/recipes/partners/bluetier/x402-payment-gate/.dockerignore)

</details>



NemoClaw Community is a collection of reference examples and blueprints for building constrained, inspectable agent workflows. The repository demonstrates how to compose Large Language Models (LLMs) with specialized runtime harnesses and secure execution environments to create reliable agentic systems.

### Purpose and Scope

The primary goal of this repository is to provide a library of reusable patterns that bridge the gap between raw model inference and production-ready agents. Each example illustrates a "NemoClaw Blueprint," which defines how an agent is wired to tools, how its network access is restricted, and how its internal reasoning is made observable to human operators.

For detailed architecture information, see [Core Concepts and Architecture](#1.1).

### The Three-Layer Architecture

NemoClaw blueprints are composed of three distinct layers that work together to define an agent's capabilities and boundaries:

| Layer | Responsibility | Code Entity / Symbol |
| :--- | :--- | :--- |
| **Model** | The inference engine and provider configuration. | `inference` provider |
| **Harness** | The agent runtime, skills, bridges, and state. | `sandbox` / `harness` |
| **OpenShell** | The sandbox, gateway, and L7 policy enforcement. | `openshell` CLI / `policy.yaml` |

The following diagram illustrates how these layers interact to form a functional agent system, mapping the conceptual layers to specific files and processes within the repository.

#### NemoClaw Blueprint Composition
```mermaid
graph TD
    subgraph "NemoClaw_Blueprint"
        [ModelLayer] --> [HarnessLayer]
        [HarnessLayer] --> [OpenShellLayer]
    end

    subgraph "Code_Entities"
        [ModelLayer] -.-> "inference_preflight.py"
        [HarnessLayer] -.-> "nemoclaw-start"
        [OpenShellLayer] -.-> "policy.yaml"
    end

    [HarnessLayer] -- "Tool Calls" --> [OpenShellLayer]
    [OpenShellLayer] -- "Egress Filtering" --> [External_Services]
    [OpenShellLayer] -- "Credential Injection" --> [ModelLayer]
```
Sources: [README.md:8-14](), [examples/README.md:6-7]()

### Example Catalog Taxonomy

Examples in the repository are organized by their artifact type and provenance to ensure a "shared-nothing" isolation between different agent implementations. This structure allows each example to remain independently deployable with its own lifecycle scripts.

*   **Recipes:** Complete, reusable workflows (e.g., Chief of Staff, PR Review Advisor). These are further divided by provenance: `nvidia`, `partners`, and `community`.
*   **Demos:** Specific field demonstrations, often involving complex hardware or GUI automation (e.g., `blender-omniverse-dgx-station`).
*   **Launchables:** Fast-path onboarding scripts, such as the `brev` notebook path for Hermes.
*   **Tools:** Standalone utilities like the `harness-engineering-playground` (`hep`).

For a full list of available examples and their classification rules, see [Example Catalog and Taxonomy](#1.2).

#### System Mapping: Example Types to Directory Structure
```mermaid
graph LR
    [Repository_Root] --> [examples_dir]
    
    subgraph "Artifact_Taxonomy"
        [examples_dir] --> [recipes]
        [examples_dir] --> [demos]
        [examples_dir] --> [launchables]
        [examples_dir] --> [tools]
    end

    subgraph "Provenance"
        [recipes] --> [nvidia_recipes]
        [recipes] --> [partner_recipes]
        [recipes] --> [community_recipes]
    end

    [nvidia_recipes] -.-> "recipes/nvidia/"
    [partner_recipes] -.-> "recipes/partners/"
    [community_recipes] -.-> "recipes/community/"
    [tools] -.-> "tools/harness-engineering-playground/"
```
Sources: [examples/README.md:6-52](), [examples/recipes/partners/bluetier/x402-payment-gate/.dockerignore:1-6]()

### Getting Started

To begin using NemoClaw Community, users must have a Linux host with Docker, the `openshell` CLI, and access to an OpenAI-compatible inference endpoint. The repository uses a standard bring-up/tear-down lifecycle across most recipes, typically managed by numbered scripts (e.g., `00-host-services.sh` through `03-sandbox.sh`).

For a step-by-step onboarding guide, see [Getting Started and Prerequisites](#1.3).

### Navigation and Child Pages

This wiki is organized into the following detailed sections:

*   **[Core Concepts and Architecture](#1.1)**: Deep dive into the Blueprint composition model, the OpenShell gateway, and the L7 proxy credential-substitution pattern.
*   **[Example Catalog and Taxonomy](#1.2)**: Detailed documentation on the directory layout rules, naming conventions, and the `.agents/skills` used for repository maintenance.
*   **[Getting Started and Prerequisites](#1.3)**: Environment setup, tool installation, and the standard agent lifecycle (bring-up to tear-down).

Sources: [README.md:28-44](), [SUPPORT.md:7-9]()

---

