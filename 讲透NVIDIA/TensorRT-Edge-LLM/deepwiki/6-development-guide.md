<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-Edge-LLM · page 6 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CODING_GUIDELINES.md](CODING_GUIDELINES.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



## Purpose and Scope

This page provides a comprehensive guide for developers contributing to the TensorRT-Edge-LLM project. It covers the development workflow, environment setup, coding standards, quality assurance tools, and contribution processes. This guide is designed for both internal NVIDIA developers and external open-source contributors.

For information about building the project for the first time, see [Installation](#2.2). For details on the CMake build system and cross-compilation, see [Build System](#5). For information on project architecture, see [Architecture](#4).

## Development Workflow Overview

The TensorRT-Edge-LLM project follows a fork-and-pull-request workflow with multiple quality gates enforced through automated tooling. Development contributions flow through local pre-commit checks, GitHub CI/CD validation, and human code review before integration into the main branch.

**Workflow: From Code to Merge**
```mermaid
graph TB
    [FORK] --> [CLONE]
    [CLONE] --> [SETUP]
    [SETUP] --> [ISSUE]
    [ISSUE] --> [BRANCH]
    [BRANCH] --> [CODE]
    
    [CODE] --> [COMMIT]
    [COMMIT] --> [PRECOMMIT]
    
    [PRECOMMIT] -- "Hooks Pass?" --> [HOOKS_PASS_YES]
    [PRECOMMIT] -- "Hooks Fail?" --> [FIX]
    [FIX] --> [CODE]
    
    [HOOKS_PASS_YES] --> [PUSH]
    [PUSH] --> [PR]
    [PR] --> [CI]
    [PR] --> [DCO]
    [CI] --> [REVIEW]
    [DCO] --> [REVIEW]
    
    [REVIEW] -- "Approved?" --> [APPROVAL_YES]
    [REVIEW] -- "Changes Requested?" --> [CHANGES]
    [CHANGES] --> [CODE]
    [APPROVAL_YES] --> [MERGE]

    subgraph "Local Development"
        [SETUP]["Setup: pre-commit install"]
        [CODE]["Write Code: Follow CODING_GUIDELINES.md"]
        [COMMIT]["git commit -s"]
        [PRECOMMIT]["pre-commit hooks"]
    end

    subgraph "Remote Process"
        [PR]["Pull Request: Conventional Commits"]
        [CI]["GitHub CI: Build + Test"]
        [DCO]["DCO: Sign-off Check"]
        [REVIEW]["Maintainer Review"]
    end
```
**Sources:** [CONTRIBUTING.md:80-98](), [CONTRIBUTING.md:133-146]()

## Repository Structure for Development

The project organizes development resources and guidelines in specific locations:

| Resource | File Path | Purpose |
|----------|-----------|---------|
| Coding Guidelines | `CODING_GUIDELINES.md` | C++ and Python style rules |
| Contribution Rules | `CONTRIBUTING.md` | PR process, DCO requirements |
| Pre-commit Config | `.pre-commit-config.yaml` | Automated quality checks |
| C++ Formatting | `.clang-format` | clang-format configuration |
| License Header | `LICENSE_HEADER` | Copyright header template |
| Issue Templates | `.github/ISSUE_TEMPLATE/` | Bug reports, feature requests |

**Sources:** [CONTRIBUTING.md:9-11](), [CONTRIBUTING.md:13-13](), [.pre-commit-config.yaml:1-72]()

## Setting Up Development Environment

### Initial Setup

Before contributing code, developers must configure their local environment. The project uses `pre-commit` to enforce code formatting and validation automatically.

**Environment Setup Flow**
```mermaid
graph LR
    [PIP_INSTALL] --> [PRECOMMIT_INSTALL]
    [PRECOMMIT_INSTALL] --> [HOOKS_READY]

    subgraph "Entity Mapping"
        [PIP_INSTALL]["pip install pre-commit"]
        [PRECOMMIT_INSTALL]["pre-commit install"]
        [HOOKS_READY]["git hooks active"]
    end
```

**Installation Commands:**

```bash
# Clone repository with submodules
git clone --recursive https://github.com/NVIDIA/TensorRT-Edge-LLM.git
cd TensorRT-Edge-LLM

# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

This setup ensures that every `git commit` automatically triggers formatting and validation checks. For detailed environment setup including build dependencies, see [Setting Up Development Environment](#6.1).

**Sources:** [CONTRIBUTING.md:36-42](), [CONTRIBUTING.md:82-91]()

## Code Quality Enforcement Layers

The project enforces code quality through multiple automated layers, each targeting different aspects of code consistency.

**Quality Gates**
```mermaid
graph TB
    subgraph "Local Hooks (.pre-commit-config.yaml)"
        [ISORT]["isort: Sort Imports"]
        [LICENSE]["insert-license: LICENSE_HEADER"]
        [CLANG]["clang-format: C++/CUDA"]
        [YAPF]["yapf: Python Formatting"]
        [SPELL]["codespell: Typo Check"]
        [AUTOFLAKE]["autoflake: Unused Imports"]
    end
    
    subgraph "CI & Review"
        [BUILD]["Build Validation"]
        [DCO_CHECK]["DCO Sign-off Verification"]
        [MAINTAINER]["Human Code Review"]
    end
    
    [COMMIT] --> [ISORT]
    [ISORT] --> [LICENSE]
    [LICENSE] --> [CLANG]
    [CLANG] --> [YAPF]
    [YAPF] --> [SPELL]
    [SPELL] --> [AUTOFLAKE]
    
    [AUTOFLAKE] --> [BUILD]
    [BUILD] --> [DCO_CHECK]
    [DCO_CHECK] --> [MAINTAINER]
    [MAINTAINER] --> [MERGE]
```
**Sources:** [.pre-commit-config.yaml:8-72](), [CONTRIBUTING.md:94-98](), [CONTRIBUTING.md:133-146]()

### Pre-commit Hook Details

The `.pre-commit-config.yaml` file configures several hooks that run on every commit:

| Hook | Repository | Purpose | Files Affected |
|------|-----------|---------|----------------|
| `isort` | pycqa/isort | Sort Python imports | `*.py` |
| `insert-license` | Lucas-C/pre-commit-hooks | Verify `LICENSE_HEADER` | `*.py`, `*.cpp`, `*.cu`, `*.h` |
| `yapf` | google/yapf | Format Python code | `*.py` |
| `clang-format` | pre-commit/mirrors-clang-format | Format C++/CUDA code | `*.cpp`, `*.cu`, `*.h`, `*.cuh` |
| `codespell` | codespell-project/codespell | Check spelling | All text files |
| `autoflake` | PyCQA/autoflake | Remove unused imports | `*.py` |

**Exclusion Patterns:**
- `3rdParty/*` - External code [.pre-commit-config.yaml:4-7]()
- `cpp/common/json/jsmn.h` - External JSON parser [.pre-commit-config.yaml:5-5]()
- `kernelSrcs/*` - CuTe DSL generated artifacts [.pre-commit-config.yaml:6-6]()

For detailed information on pre-commit hooks, see [Code Quality Tools](#6.4).

**Sources:** [.pre-commit-config.yaml:1-72](), [CONTRIBUTING.md:44-72]()

## Coding Standards Overview

The project maintains strict coding standards documented in `CODING_GUIDELINES.md`, primarily derived from the Google C++ Style Guide.

### Key C++ Standards

**Naming Conventions:**

| Entity Type | Convention | Example |
|-------------|-----------|---------|
| Filenames | Camel case, lowercase first | `thisIsAFilename.cpp` [CODING_GUIDELINES.md:44-46]() |
| Classes/Types | Camel case, uppercase first | `FooBarClass` [CODING_GUIDELINES.md:48-49]() |
| Local variables | Camel case, lowercase first | `localFooBar` [CODING_GUIDELINES.md:51-52]() |
| Member variables | Prefix `m`, camel case | `mNbFooValues` [CODING_GUIDELINES.md:63-65]() |
| Constants | Uppercase snake_case, prefix `k` | `kDIGIT_NUM` [CODING_GUIDELINES.md:67-70]() |

**Memory and Formatting:**
- Use smart pointers (`unique_ptr`, `shared_ptr`) [CODING_GUIDELINES.md:102-104]().
- Use Allman indentation (braces on new lines) [CODING_GUIDELINES.md:36-41]().
- 4 spaces indentation, no tabs [CODING_GUIDELINES.md:87-89]().
- Maximum 120 characters per line [CODING_GUIDELINES.md:92-94]().

For comprehensive C++ coding guidelines, see [Coding Standards](#6.2).

**Sources:** [CODING_GUIDELINES.md:1-180]()

### Key Python Standards

Python code is formatted using `black` and `yapf` with a line length of 120 characters [CONTRIBUTING.md:22-28]().

For comprehensive Python coding guidelines, see [Coding Standards](#6.2).

**Sources:** [CONTRIBUTING.md:22-28](), [.pre-commit-config.yaml:42-45]()

## Contributing Workflow

### Issue Creation
All changes must begin with a [TensorRT-Edge-LLM Issue Request](https://github.com/nvidia/TensorRT-Edge-LLM/issues) [CONTRIBUTING.md:4-7](). Issues must be approved by engineers prior to code submission [CONTRIBUTING.md:7-7]().

### Pull Request Submission
PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) [CONTRIBUTING.md:100-103](). 

**Examples:**
- `feat: Add support for starcoder-v2 FP8` [CONTRIBUTING.md:108-108]()
- `fix: a Memory leak issue in C++ runtime` [CONTRIBUTING.md:112-112]()

**DCO Sign-off:**
Contributors must "sign-off" commits using `git commit -s` to certify work originality [CONTRIBUTING.md:133-146]().

For detailed PR submission guidelines, see [Contributing Workflow](#6.3).

**Sources:** [CONTRIBUTING.md:4-7](), [CONTRIBUTING.md:100-146]()

## Debugging and Accuracy Validation

Accuracy validation involves comparing TensorRT engine outputs against HuggingFace reference models. This is facilitated by the `IDebugListener` interface for tensor injection and the `compare_hf_trt_tensors.py` script for validation.

For details, see [Debugging and Accuracy Validation](#6.6).

---

## Summary of Child Pages

For detailed information on specific development topics, refer to the following pages:
- [Setting Up Development Environment](#6.1) — Configuring tools and pre-commit.
- [Coding Standards](#6.2) — Detailed C++ and Python style guides.
- [Contributing Workflow](#6.3) — Step-by-step PR and issue process.
- [Code Quality Tools](#6.4) — In-depth look at linters and formatters.
- [Debugging and Accuracy Validation](#6.6) — Tools for model verification using `IDebugListener`.

---

