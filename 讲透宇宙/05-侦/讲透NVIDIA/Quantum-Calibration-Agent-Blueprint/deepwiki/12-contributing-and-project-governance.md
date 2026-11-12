<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Quantum-Calibration-Agent-Blueprint · page 12 Contributing and Project Governance · fetched 2026-10-26 -->

# Contributing and Project Governance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ATTRIBUTIONS](ATTRIBUTIONS)
- [Contributing.md](Contributing.md)
- [SECURITY.md](SECURITY.md)
- [docs/latest/developer-guide/contributing.mdx](docs/latest/developer-guide/contributing.mdx)
- [docs/latest/developer-guide/index.mdx](docs/latest/developer-guide/index.mdx)
- [fern/fern.config.json](fern/fern.config.json)
- [fern/latest.yml](fern/latest.yml)

</details>



This page outlines the standards, processes, and infrastructure used to maintain and evolve the Quantum Calibration Agent (QCA) blueprint. It covers the legal requirements for code contributions, the technical workflow for developers, and the documentation system that powers the project's external portal.

## Contribution Overview

The QCA project follows an issue-first development model. All functional changes, bug fixes, and feature implementations should begin with a discussion in a GitHub issue to ensure alignment with the project's "simplicity first" philosophy [docs/latest/developer-guide/index.mdx:42-49]().

### Workflow Summary
1.  **Issue Triage**: Report bugs or request features via GitHub Issues [Contributing.md:6-11]().
2.  **Implementation**: Discuss the approach with maintainers before opening a Pull Request [Contributing.md:19-24]().
3.  **Sign-off**: All commits must include a Developer Certificate of Origin (DCO) sign-off [Contributing.md:35-41]().
4.  **Review**: Maintainers review the PR for architectural fit, test coverage, and style compliance.

For a detailed step-by-step guide on setting up your environment and submitting code, see **[Contribution Guidelines](#12.1)**.

## Project Governance and Legal

### Developer Certificate of Origin (DCO)
To ensure all contributions are legally cleared, QCA requires the standard DCO sign-off. This is performed by appending `--signoff` or `-s` to git commit commands [Contributing.md:42-47](). This certifies that the contributor has the right to submit the work under the project's open-source license [Contributing.md:55-93]().

### Licensing and Attributions
The project is released under an open-source license, but incorporates various third-party components with their own licensing requirements (e.g., MIT, BSD 3-Clause). Notable dependencies include:
*   **DeepAgents**: NVIDIA Proprietary [ATTRIBUTIONS:70-75]().
*   **UI Components**: MIT License (Ivan Fioravanti, Mckay Wrigley) [ATTRIBUTIONS:16-62]().
*   **Core Libraries**: Typer, Rich, and h5py [ATTRIBUTIONS:79-130]().

### Security Reporting
Security vulnerabilities should **never** be reported via public GitHub issues. Instead, they must be directed to NVIDIA's Product Security Incident Response Team (PSIRT) via email at `psirt@nvidia.com` or the official submission form [SECURITY.md:7-12]().

## Documentation Infrastructure

The project uses **Fern** to generate and host its developer and user documentation. The documentation source is located in the `docs/` and `fern/` directories.

### Fern Configuration
The documentation portal is configured through several key files:
*   `fern/fern.config.json`: Defines the organization (`nvidia`) and Fern version [fern/fern.config.json:1-4]().
*   `fern/latest.yml`: Manages the navigation structure, mapping filesystem folders to site sections like "Quick Start", "User Guide", and "Developer Guide" [fern/latest.yml:1-24]().

### Documentation Content
The content is written in MDX, allowing for custom components and rich formatting. The `docs/latest/developer-guide/` directory contains the primary technical references for the system [docs/latest/developer-guide/index.mdx:1-30]().

For details on the documentation build process and branding assets, see **[Documentation Portal](#12.2)**.

## Technical Contribution Map

The following diagrams bridge the project's governance concepts and documentation structure to the physical codebase.

### Documentation to Code Entity Mapping
This diagram shows how the documentation sections in `fern/latest.yml` correspond to the core logic and tool implementations.

| Documentation Section | Code Entities | Purpose |
| :--- | :--- | :--- |
| **Developer Guide** | `core/`, `tools/` | Internal system logic and agent capabilities. |
| **User Guide** | `scripts/`, `data/workflows/` | Experiment execution and automation flows. |
| **Quick Start** | `cli.py`, `server.py` | Entry points for running the system. |

Sources: [fern/latest.yml:1-24](), [docs/latest/developer-guide/contributing.mdx:52-84]()

### Contribution Workflow and Enforcement
This diagram visualizes the path from a local code change to a merged contribution, highlighting the automated and manual checkpoints.

```mermaid
graph TD
    subgraph "Contributor Environment"
        "A[Local Edit]" --> "B[git commit -s]"
        "B" --> "C[pytest tests/unit/]"
    end

    subgraph "GitHub Enforcement"
        "D[Pull Request]" --> "E{DCO Check}"
        "E" -- "Fail" --> "F[Block Merge]"
        "E" -- "Pass" --> "G{Maintainer Review}"
        "G" -- "Approve" --> "H[Merge to main]"
    end

    "C" --> "D"
    "H" --> "I[Fern Docs Update]"

    style "E" stroke-dasharray: 5 5
    style "G" stroke-dasharray: 5 5
```
Sources: [Contributing.md:35-47](), [docs/latest/developer-guide/contributing.mdx:259-281](), [fern/latest.yml:1-24]()

## Child Pages
*   **[Contribution Guidelines](#12.1)**: Detailed setup instructions, Python coding standards (PEP 8, Google-style docstrings), and the PR checklist.
*   **[Documentation Portal](#12.2)**: Deep dive into the Fern configuration, custom MDX components, and the publication pipeline.

---

