<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuopt-examples · page 13 Contributing to cuopt-examples · fetched 2026-10-26 -->

# Contributing to cuopt-examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE.md](LICENSE.md)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

This document provides an overview of the contribution process for the `cuopt-examples` repository, including the types of contributions accepted, legal requirements, and code quality standards. It serves as the entry point for developers who want to add new examples, fix bugs, or improve documentation.

For detailed instructions on setting up your development environment, see [Development Environment Setup](#13.1). For comprehensive code quality requirements including pre-commit hooks and formatting tools, see [Code Quality Standards](#13.2). For step-by-step instructions on the Git workflow and pull request process, see [Contribution Workflow](#13.3). For guidance on filing bug reports and feature requests, see [Issue Templates and Bug Reporting](#13.4).

---

## Types of Contributions

The repository accepts three primary types of contributions, each with specific requirements and workflows:

| Contribution Type | Purpose | Requirements |
|------------------|---------|--------------|
| Bug Reports | Report problems with existing examples, workflows, or documentation | Use bug report template; include version, installation method, and reproducible example |
| Feature Requests | Propose new examples, workflows, or enhancements | File feature request issue; discuss design with team before implementation |
| Code Contributions | Implement bug fixes, new examples, or workflow improvements | Follow code quality standards; include documentation and README; sign-off commits with DCO |

**Sources:** [CONTRIBUTING.md:1-11]()

---

## Contribution Workflow Overview

The following diagram illustrates the complete contribution process from issue identification through merge:

**Figure 1: Contribution Lifecycle**
```mermaid
graph TD
    subgraph "Issue Identification"
        ["Identify Issue<br/>(good first issue,<br/>help wanted labels)"] --> ["Comment on Issue<br/>(claim work)"]
    end
    
    subgraph "Repository Setup"
        ["Fork Repository<br/>(github.com/NVIDIA/cuopt-examples)"] --> ["Create Feature Branch<br/>(add-new-workflow-example)"]
    end
    
    subgraph "Implementation"
        ["Write Code"] --> ["Add README.md"]
        ["Add README.md"] --> ["Add Documentation"]
        ["Add Documentation"] --> ["Create requirements.txt<br/>(if needed)"]
    end
    
    subgraph "Code Quality Checks"
        ["Run pre-commit hooks"] --> ["Black formatter"]
        ["Run pre-commit hooks"] --> ["isort import sorting"]
        ["Run pre-commit hooks"] --> ["flake8 PEP 8 checks"]
    end
    
    subgraph "Legal Compliance"
        ["Sign-off commit<br/>(git commit -s)"] --> ["Add Signed-off-by trailer"]
    end
    
    subgraph "Pull Request"
        ["Create Pull Request"] --> ["Code Review"]
        ["Code Review"] --> ["Update based on feedback"]
        ["Update based on feedback"] --> ["Team Merges PR"]
    end
    
    ["Comment on Issue<br/>(claim work)"] --> ["Fork Repository<br/>(github.com/NVIDIA/cuopt-examples)"]
    ["Create Feature Branch<br/>(add-new-workflow-example)"] --> ["Write Code"]
    ["Create requirements.txt<br/>(if needed)"] --> ["Run pre-commit hooks"]
    ["Black formatter"] --> ["Sign-off commit<br/>(git commit -s)"]
    ["isort import sorting"] --> ["Sign-off commit<br/>(git commit -s)"]
    ["flake8 PEP 8 checks"] --> ["Sign-off commit<br/>(git commit -s)"]
    ["Add Signed-off-by trailer"] --> ["Create Pull Request"]
```

**Sources:** [CONTRIBUTING.md:14-26](), [CONTRIBUTING.md:29-36]()

---

## Code Quality Infrastructure

The repository enforces code quality through automated tooling configured in `.pre-commit-config.yaml`. The following diagram shows the code quality checks and their configuration:

**Figure 2: Pre-commit Hook Architecture**
```mermaid
graph LR
    subgraph "Configuration"
        [".pre-commit-config.yaml"]
    end
    
    subgraph "Formatting & Linting Tools"
        ["black<br/>rev: 22.3.0<br/>--target-version py310<br/>--config pyproject.toml"]
        ["isort<br/>rev: 5.12.0<br/>--resolve-all-configs"]
        ["flake8<br/>rev: 7.1.1<br/>--config=.flake8"]
    end
    
    subgraph "Execution Methods"
        ["pre-commit run"]
        ["pre-commit run --all-files"]
        ["pre-commit install<br/>(automatic on commit)"]
    end
    
    subgraph "Targeted Code Entities"
        ["Python files<br/>(*.py)"]
        ["Cython files<br/>(*.pyx)"]
        ["Type stubs<br/>(*.pyi)"]
    end
    
    [".pre-commit-config.yaml"] --> ["black<br/>rev: 22.3.0<br/>--target-version py310<br/>--config pyproject.toml"]
    [".pre-commit-config.yaml"] --> ["isort<br/>rev: 5.12.0<br/>--resolve-all-configs"]
    [".pre-commit-config.yaml"] --> ["flake8<br/>rev: 7.1.1<br/>--config=.flake8"]
    
    ["black<br/>rev: 22.3.0<br/>--target-version py310<br/>--config pyproject.toml"] --> ["pre-commit run"]
    ["isort<br/>rev: 5.12.0<br/>--resolve-all-configs"] --> ["pre-commit run"]
    ["flake8<br/>rev: 7.1.1<br/>--config=.flake8"] --> ["pre-commit run"]
    
    ["pre-commit run"] --> ["pre-commit run --all-files"]
    ["pre-commit run --all-files"] --> ["pre-commit install<br/>(automatic on commit)"]
    
    ["black<br/>rev: 22.3.0<br/>--target-version py310<br/>--config pyproject.toml"] --> ["Python files<br/>(*.py)"]
    ["isort<br/>rev: 5.12.0<br/>--resolve-all-configs"] --> ["Python files<br/>(*.py)"]
    ["isort<br/>rev: 5.12.0<br/>--resolve-all-configs"] --> ["Cython files<br/>(*.pyx)"]
    ["isort<br/>rev: 5.12.0<br/>--resolve-all-configs"] --> ["Type stubs<br/>(*.pyi)"]
    ["flake8<br/>rev: 7.1.1<br/>--config=.flake8"] --> ["Python files<br/>(*.py)"]
```

**Sources:** [.pre-commit-config.yaml:1-33](), [CONTRIBUTING.md:49-90]()

---

## Developer Certificate of Origin (DCO)

All contributions must include a sign-off certifying that the contributor has the right to submit the code under the Apache 2.0 license. This is accomplished using the `--signoff` flag with `git commit`:

```bash
git commit -s -m "Add cool feature."
```

This appends the following trailer to the commit message:

```
Signed-off-by: Your Name <your@email.com>
```

**Pull requests containing commits without sign-off will not be accepted.** The DCO certifies that the contribution was created by you, or you have the rights to submit it, and that the record of the contribution is public. For the full text of the DCO, see [CONTRIBUTING.md:106-132]().

**Sources:** [CONTRIBUTING.md:91-133]()

---

## Example and Workflow Structure

New examples and workflows must follow a standardized directory structure to ensure consistency:

### Required Components

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| `README.md` | **Required** | High-level description, usage instructions, expected outputs |
| `notebook.ipynb` | **Required** | Jupyter notebook with implementation and documentation |

### Optional Components

| Component | Usage Guideline | Purpose |
|-----------|----------------|---------|
| `requirements.txt` | Only if dependencies cannot be installed in notebook | Lists package dependencies |
| `data/` | Only if data cannot be fetched within notebook | Example input data or generation scripts |
| `utils/` | Only if utility functions cannot be inline | Helper functions (prefer notebook-inline) |

The contribution guidelines emphasize **self-contained notebooks** to maximize portability. Install dependencies within the notebook when possible and implement utility functions directly in cells.

**Sources:** [CONTRIBUTING.md:145-161](), [CONTRIBUTING.md:163-174]()

---

## Python Code Style Requirements

All Python code must follow these standards:

| Standard | Tool/Reference | Enforcement |
|----------|---------------|-------------|
| Code formatting | Black (v22.3.0) | Pre-commit hook |
| Import sorting | isort (v5.12.0) | Pre-commit hook |
| PEP 8 compliance | flake8 (v7.1.1) | Pre-commit hook |
| Type hints | PEP 484 | Manual review |
| Docstrings | Google/NumPy style | Manual review |
| Function design | Single-purpose, focused | Manual review |

**Sources:** [CONTRIBUTING.md:134-144](), [.pre-commit-config.yaml:6-30]()

---

## Issue Templates

The repository provides structured issue templates to ensure high-quality bug reports:

### Bug Report Template Structure

The bug report template (`.github/ISSUE_TEMPLATE/bug_report.yml`) collects the following:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `version` | Text input | Yes | cuOpt version (e.g., "22.12") |
| `installation-method` | Dropdown | No | Docker, Pip, or Source installation |
| `description` | Textarea | Yes | Bug description and expected behavior |
| `mvr` | Textarea | No | Minimum reproducible example code |
| `env-details` | Textarea | No | Output from `print_env.sh` script |

The template automatically applies `bug` and `? - Needs Triage` labels.

**Sources:** [.github/ISSUE_TEMPLATE/bug_report.yml:1-86]()

---

## License and Copyright

All contributions are submitted under the **Apache License 2.0**. Every source file should include the appropriate SPDX license header:

```python
# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
```

The full license text is available in [LICENSE.md:1-202]().

**Sources:** [LICENSE.md:1-202](), [.github/ISSUE_TEMPLATE/bug_report.yml:1-14]()

---

## Next Steps for Contributors

To begin contributing:

1. **Environment Setup**: Follow [Development Environment Setup](#13.1) to install Docker and configure pre-commit hooks.
2. **Code Quality**: Review [Code Quality Standards](#13.2) for detailed requirements on formatting and documentation.
3. **Workflow Process**: Study [Contribution Workflow](#13.3) for step-by-step Git procedures.
4. **Issue Filing**: Use [Issue Templates and Bug Reporting](#13.4) to report bugs or request features.

**Sources:** [CONTRIBUTING.md:1-181]()

---

