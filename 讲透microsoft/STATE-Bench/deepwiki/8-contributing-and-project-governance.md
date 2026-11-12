<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/STATE-Bench · page 8 Contributing and Project Governance · fetched 2026-10-26 -->

# Contributing and Project Governance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)

</details>



This page provides an overview of how to contribute to STATE-Bench, the community standards we uphold, and the Microsoft open-source governance policies that apply to this repository. As an open-source project, we rely on community contributions to expand benchmark domains, improve agent interfaces, and refine evaluation protocols.

## Contribution Workflow

We welcome contributions ranging from bug fixes and documentation improvements to new benchmark tasks and domain environments. Most contributions require you to agree to a **Contributor License Agreement (CLA)** declaring that you have the right to grant us the rights to use your contribution [CONTRIBUTING.md:3-6]().

### Development Lifecycle
The project utilizes `uv` for dependency management and a suite of automated checks to ensure code quality. The general workflow for contributors involves:
1.  **Forking and Cloning**: Creating a local copy of the repository.
2.  **Environment Setup**: Using `uv sync` to install dependencies and `pre-commit` to set up git hooks.
3.  **Implementation**: Adhering to the existing architectural patterns in `state_bench/`.
4.  **Verification**: Running the `pytest` suite to ensure no regressions.
5.  **Pull Request**: Submitting changes for review, which triggers the automated CI pipeline.

For a deep dive into the technical requirements for contributions, including linting rules and test structures, see **[CI/CD and Code Quality](#8.1)**.

### Community Engagement
*   **Issues**: We use GitHub Issues to track bugs and feature requests [SUPPORT.md:5-7]().
*   **Code of Conduct**: All participants are expected to follow the Microsoft Open Source Code of Conduct [CODE_OF_CONDUCT.md:1-3]().
*   **Security**: Vulnerabilities should not be reported via public issues but rather through the Microsoft Security Response Center (MSRC) [SECURITY.md:11-13]().

For detailed information on legal, security, and support policies, see **[Community Policies](#8.2)**.

## Governance and Quality Standards

STATE-Bench maintains high standards for code health and community interaction. The following diagram illustrates the relationship between the contribution process and the governance frameworks.

### Contribution and Governance Relationship
"This diagram maps the human contribution process to the underlying policy and enforcement files."

```mermaid
graph TD
    subgraph "Contributor Actions"
        "User" -- "Submits PR" --> "CLA_Bot"["CLA-bot Check"]
        "User" -- "Runs Hooks" --> "PreCommit"["pre-commit hooks"]
    end

    subgraph "Governance Frameworks"
        "CLA_Bot" -- "Validates" --> "CONTRIBUTING"["CONTRIBUTING.md"]
        "Governance" -- "Standards" --> "COC"["CODE_OF_CONDUCT.md"]
        "Governance" -- "Legal" --> "LICENSE"["MIT License"]
        "Governance" -- "Safety" --> "SECURITY"["SECURITY.md"]
    end

    subgraph "Quality Enforcement"
        "PreCommit" -- "Configured by" --> "PreConfig"[".pre-commit-config.yaml"]
        "CI_Pipeline"["GitHub Actions CI"] -- "Runs" --> "Pytest"["tests/"]
    end

    "CONTRIBUTING" --> "CLA_Bot"
    "PreConfig" --> "CI_Pipeline"
```
**Sources:** [CONTRIBUTING.md:1-15](), [CODE_OF_CONDUCT.md:1-11](), [SECURITY.md:1-39](), [LICENSE:1-21](), [SUPPORT.md:1-16]()

## Code Quality and Automation

To maintain a reliable benchmarking framework, we enforce strict linting and testing via GitHub Actions. Every Pull Request is subjected to a CI pipeline that validates the environment and executes the test suite.

### Automation Infrastructure
"This diagram maps the CI/CD pipeline entities to the specific configuration files in the repository."

```mermaid
graph LR
    subgraph "CI/CD Pipeline (.github/workflows/)"
        "CI_YAML"["ci.yml"]
        "Pages_YAML"["pages.yml"]
    end

    subgraph "Code Quality Tools"
        "Ruff"["Ruff (Linter/Formatter)"]
        "Gitleaks"["Gitleaks (Secret Detection)"]
        "Pytest"["Pytest (Unit/Integration)"]
    end

    subgraph "Configuration Files"
        "PreConfig"[".pre-commit-config.yaml"]
        "UV_Lock"["uv.lock"]
    end

    "CI_YAML" -- "Syncs via" --> "UV_Lock"
    "CI_YAML" -- "Triggers" --> "Pytest"
    "PreConfig" -- "Defines" --> "Ruff"
    "PreConfig" -- "Defines" --> "Gitleaks"
```
**Sources:** [.pre-commit-config.yaml:1-40](), [.github/workflows/ci.yml:1-30]() (Note: Reference to standard GitHub workflow and pre-commit structures).

For details on the specific hooks and test categories, see **[CI/CD and Code Quality](#8.1)**.

## Licensing
The project is licensed under the **MIT License**, which allows for broad reuse and modification [LICENSE:1-21]().

| Policy | File Reference | Purpose |
| :--- | :--- | :--- |
| **Code of Conduct** | `CODE_OF_CONDUCT.md` | Establishing a welcoming and inclusive environment. |
| **Contributing** | `CONTRIBUTING.md` | Guidelines for PRs and CLA requirements. |
| **Security** | `SECURITY.md` | Procedures for reporting vulnerabilities to MSRC. |
| **Support** | `SUPPORT.md` | How to get help and file bug reports. |
| **License** | `LICENSE` | Legal terms for using and distributing the software. |

**Sources:** [LICENSE:1-21](), [CONTRIBUTING.md:1-15](), [SECURITY.md:1-39](), [CODE_OF_CONDUCT.md:1-11]()

---

