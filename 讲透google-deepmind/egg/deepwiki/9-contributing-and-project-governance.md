<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/egg · page 9 Contributing and Project Governance · fetched 2026-10-26 -->

# Contributing and Project Governance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)

</details>



This page outlines the protocols for contributing to the `egg` codebase, the project's licensing terms, and the technical conventions maintained in the repository. As a Google DeepMind project, it follows specific open-source standards regarding legal agreements and community conduct.

## Contribution Workflow

The `egg` project utilizes a standard GitHub-centric workflow for all code changes. Every modification, whether from external contributors or internal project members, must undergo a formal review process.

### Contributor License Agreement (CLA)
Before any contribution can be accepted and merged, the contributor must have a signed Contributor License Agreement on file. This agreement clarifies the intellectual property rights associated with the contribution while allowing the project to redistribute the work under its open-source license.

*   **Requirement:** A CLA is generally required once per individual/employer across Google projects [CONTRIBUTING.md:3-13]().
*   **Verification:** Status can be checked or new agreements signed at [https://cla.developers.google.com/](https://cla.developers.google.com/).

### Pull Requests and Code Review
The project enforces a strict review policy to maintain code quality and architectural consistency across the RL training loops and neural network modules.

*   **Mechanism:** All submissions must be made via GitHub Pull Requests [CONTRIBUTING.md:17-20]().
*   **Reviewers:** At least one project member must review and approve the PR before it is merged.
*   **Community Standards:** Contributors are expected to adhere to [Google's Open Source Community Guidelines](https://opensource.google/conduct/) [CONTRIBUTING.md:24-25]().

### Development Cycle Diagram
The following diagram illustrates the flow from a local code change to the inclusion in the main `egg` repository.

**Code Contribution Flow**
```mermaid
graph TD
    subgraph "Contributor Space"
        "Local_Edit"["Edit Code/Docs"] --> "Sign_CLA"["Sign Google CLA"]
        "Sign_CLA" --> "Submit_PR"["GitHub Pull Request"]
    end

    subgraph "Review Space"
        "Submit_PR" --> "Automated_Tests"["CI / Smoke Tests"]
        "Automated_Tests" --> "Code_Review"["Maintainer Review"]
        "Code_Review" -- "Request Changes" --> "Local_Edit"
    end

    subgraph "Repository Space"
        "Code_Review" -- "Approve" --> "Merge"["Merge to main"]
        "Merge" --> "Apache_2_0"["Licensed under Apache 2.0"]
    end
```
Sources: [CONTRIBUTING.md:1-26](), [LICENSE:1-130]()

## Licensing

The `egg` codebase is distributed under the **Apache License, Version 2.0**. This is a permissive license that allows for free use, modification, and distribution of the software.

### Key Terms
*   **Grant of Copyright License:** Contributors grant a perpetual, worldwide, non-exclusive, no-charge, royalty-free copyright license [LICENSE:67-72]().
*   **Grant of Patent License:** Contributors grant a patent license for claims necessarily infringed by their contribution [LICENSE:74-82]().
*   **Redistribution:** You may redistribute the work in source or object form, provided you include a copy of the license and provide notice of modified files [LICENSE:90-99]().

Sources: [LICENSE:2-130]()

## Repository Conventions and .gitignore

To maintain a clean development environment, especially when dealing with JAX-compiled artifacts and Python distribution files, the project maintains a comprehensive `.gitignore` configuration.

### Ignored Artifacts
The repository ignores several categories of files to prevent accidental commits of local environment state or build artifacts:

| Category | Patterns Ignored |
| :--- | :--- |
| **Python Internals** | `__pycache__/`, `*.py[cod]`, `*$py.class` |
| **Build & Dist** | `build/`, `dist/`, `sdist/`, `wheels/`, `*.egg-info/` |
| **Virtual Envs** | `.Python`, `lib/`, `lib64/`, `bin/` |
| **Packaging** | `develop-eggs/`, `eggs/`, `.eggs/`, `MANIFEST` |

### Code Structure Mapping
The following diagram bridges the high-level project concepts to the physical file structure and the governance files that manage them.

**Governance and Repository Structure**
```mermaid
graph LR
    subgraph "Governance_Files"
        "LICENSE"["LICENSE (Apache 2.0)"]
        "CONTRIBUTING"["CONTRIBUTING.md (CLA/PR Policy)"]
        "GITIGNORE"[" .gitignore (Exclusions)"]
    end

    subgraph "Code_Entities"
        "EGG_LIB"["egg/lib/ (Core Utilities)"]
        "EGG_BASE"["egg/base.py (Protocols)"]
        "EXPERIMENTS"["experiments/ (Run Scripts)"]
    end

    "CONTRIBUTING" -. "Governs" .-> "EGG_BASE"
    "LICENSE" -. "Covers" .-> "EGG_LIB"
    "GITIGNORE" -. "Filters" .-> "EXPERIMENTS"
```
Sources: [.gitignore:1-25](), [CONTRIBUTING.md:1-26](), [LICENSE:1-130]()

---

