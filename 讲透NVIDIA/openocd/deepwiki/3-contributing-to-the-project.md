<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/openocd · page 3 Contributing to the Project · fetched 2026-10-26 -->

# Contributing to the Project

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLA.md](CLA.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This page provides an overview of the contribution pathways for NVIDIA's fork of OpenOCD. We welcome contributions in the form of bug reports, feature requests, documentation improvements, and code submissions. All contributors are expected to adhere to our [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md) [CODE_OF_CONDUCT.md:1-85]().

## Contribution Overview

The following diagram illustrates the high-level workflow for contributing to the repository, from initial engagement to code integration.

### Contribution Lifecycle
```mermaid
graph TD
    "User" -- "Identifies Issue" --> "GitHub_Issues"["GitHub Issues"]
    "GitHub_Issues" -- "Bug/Feature/Doc" --> "Triage_Process"["Triage (Tegra Debug Team)"]
    "Triage_Process" -- "Approved" --> "Development"["Development / Branching"]
    "Development" -- "Pull Request" --> "PR_Workflow"["Pull Request Workflow"]
    "PR_Workflow" -- "Verify CLA" --> "CLA_Signing"["CLA.md Signing"]
    "PR_Workflow" -- "Review" --> "CODEOWNERS_Review"["CODEOWNERS Review"]
    "CODEOWNERS_Review" -- "Merge" --> "Main_Branch"["Main Branch"]

    subgraph "Natural Language Space"
    "User"
    "Triage_Process"
    end

    subgraph "Code Entity Space"
    "GitHub_Issues"
    "CLA_Signing"
    "CODEOWNERS_Review"
    end
```
**Sources:** [CONTRIBUTING.md:1-9](), [CLA.md:4-31](), [.github/CODEOWNERS:1-10]()

---

## Reporting Issues

If you encounter a bug, require a new feature, or find an error in the documentation, you should file a GitHub issue using the appropriate template. The **Tegra Debug team** is responsible for evaluating and triaging these submissions [CONTRIBUTING.md:7-9]().

When reporting bugs, it is mandatory to provide diagnostic information to assist in reproduction:
*   **Environment Details**: Run the `print_env.sh` script and include its output in your report [CONTRIBUTING.md:5-6]().
*   **Build Logs**: Provide `config.log` if the issue relates to build or configuration failures.

For a detailed breakdown of issue templates, labels, and the triage lifecycle, see **[Issue Reporting Workflow](#3.1)**.

**Sources:** [CONTRIBUTING.md:1-9](), [print_env.sh:1-20]()

---

## Submitting Code and Pull Requests

Code contributions are managed through GitHub Pull Requests (PRs). Before a PR can be merged, two primary requirements must be met:

1.  **Contribution License Agreement (CLA)**: You must agree to the terms in `CLA.md`. This agreement grants NVIDIA the necessary licenses to distribute your "Submission" (Code and documentation) [CLA.md:4-31](). You must represent that the work is original or explicitly disclose third-party materials [CLA.md:32-39]().
2.  **Technical Review**: PRs are automatically routed to specific reviewers based on the `.github/CODEOWNERS` file.

### Submission Governance
| Requirement | Entity/File | Purpose |
| :--- | :--- | :--- |
| **Licensing** | [CLA.md:1-120]() | Defines rights for Code and Submissions. |
| **Conduct** | [CODE_OF_CONDUCT.md:1-85]() | Defines standards for professional interaction. |
| **Reviewers** | [.github/CODEOWNERS:1-10]() | Automates assignment of Tegra Debug team members. |

For details on PR templates, the signing process for the CLA, and automated review routing, see **[Pull Request Process and Contribution License Agreement](#3.2)**.

**Sources:** [CLA.md:4-69](), [CODE_OF_CONDUCT.md:42-53](), [CONTRIBUTING.md:1-11]()

---

## Standards and Conduct

NVIDIA maintains a professional environment for all contributors. The **Project Maintainers** have the authority to remove or reject any contribution (comments, commits, or code) that violates the standards defined in the Code of Conduct [CODE_OF_CONDUCT.md:43-52]().

*   **Positive Behavior**: Inclusive language, respectful viewpoints, and focusing on community benefit [CODE_OF_CONDUCT.md:21-29]().
*   **Enforcement**: Unacceptable behavior can be reported to `GitHub_Conduct@nvidia.com` [CODE_OF_CONDUCT.md:63-70]().

**Sources:** [CODE_OF_CONDUCT.md:1-85]()

---

