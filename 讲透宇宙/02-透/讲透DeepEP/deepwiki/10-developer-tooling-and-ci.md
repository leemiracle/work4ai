> 来源: [https://deepwiki.com/deepseek-ai/DeepEP/10-developer-tooling-and-ci](https://deepwiki.com/deepseek-ai/DeepEP/10-developer-tooling-and-ci)
> DeepWiki deepseek-ai/DeepEP

# Developer Tooling and CI

  Relevant source files 
 - [.github/workflows/format.yml](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/.github/workflows/format.yml)
 - [format.sh](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh)
 
  This page provides an overview of the developer utilities, code quality tooling, and Continuous Integration (CI) workflows used in the DeepEP project. The project maintains high code standards through automated formatting, linting, and mandatory CI checks to ensure stability across both Python and C++/CUDA components.

 
### Overview of Developer Tooling

 DeepEP utilizes a unified entry point for code quality via the `format.sh` script [format.sh1-194](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L1-L194) This utility orchestrates multiple specialized tools to handle the diverse codebase:

 
 - **Python Formatting**: Managed by `yapf` [format.sh22-44](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L22-L44)
 - **Python Linting**: Managed by `ruff` [format.sh78-115](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L78-L115)
 - **C++/CUDA Formatting**: Managed by `clang-format` [format.sh127-177](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L127-L177)
 - **Version Pinning**: Tool versions are strictly enforced via `requirements-lint.txt` [format.sh17-20](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L17-L20)
 
 The tooling is designed to be run locally by developers before pushing code, but it is also the primary mechanism for validation in the CI pipeline.

 
### Tooling Workflow and Automation

 The following diagram illustrates the relationship between the developer's local environment, the formatting scripts, and the CI gate.

 **Code Quality and CI Workflow**

 
```

```

 Sources: [format.sh1-194](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L1-L194) [.github/workflows/format.yml1-28](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/.github/workflows/format.yml#L1-L28)

 
### Formatting and Linting Logic

 DeepEP employs an incremental formatting strategy. By default, `format.sh` identifies the `MERGEBASE` between the current `HEAD` and the `main` branch [format.sh60](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L60-L60) It then applies formatting only to the files that have changed, which significantly speeds up local development loops.

 Key features include:

 
 - **Incremental vs. Global**: Supports both `format_changed` [format.sh47-66](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L47-L66) (default) and `format_all` [format.sh42-44](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L42-L44) (via `--all` flag) [format.sh68-75](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L68-L75)
 - **C++/CUDA Workarounds**: To prevent `clang-format` from breaking specific CUDA pragmas, the script temporarily masks `#pragma unroll` as comments before formatting and restores them afterward [format.sh137-148](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L137-L148)
 - **Clean Workspace Enforcement**: The script concludes with a `git diff --quiet` check. If any tool modified a file, the script exits with code `1`, signaling a failure to the developer or CI runner [format.sh181-192](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L181-L192)
 
 For details on configuration settings and tool versions, see [Code Formatting and Linting](https://deepwiki.com/deepseek-ai/DeepEP/10.1-code-formatting-and-linting).

 
### Continuous Integration (CI)

 DeepEP uses GitHub Actions to automate code quality enforcement. The workflow is defined in `.github/workflows/format.yml` [format.yml1-28](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.yml#L1-L28)

 **CI Execution Architecture**

 
```

```

 Sources: [.github/workflows/format.yml1-28](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/.github/workflows/format.yml#L1-L28)

 The CI job runs on every `push` or `pull_request` targeting the `main` branch [format.yml3-8](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.yml#L3-L8) It requires a full git history (`fetch-depth: 0`) to correctly calculate the `merge-base` for incremental checks [format.yml17](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.yml#L17-L17)

 For details on CI triggers and environment setup, see [Continuous Integration](https://deepwiki.com/deepseek-ai/DeepEP/10.2-continuous-integration).

 
### Developer Utility Mapping

 The following diagram maps high-level developer intentions to the specific shell functions and tools invoked within the codebase.

 **Developer Intent to Code Entities**

 
```

```

 Sources: [format.sh42-44](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L42-L44) [format.sh47-66](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L47-L66) [format.sh86-105](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L86-L105) [format.sh136-148](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/format.sh#L136-L148)

 
---

 
## Child Pages

 
 - **[Code Formatting and Linting](https://deepwiki.com/deepseek-ai/DeepEP/10.1-code-formatting-and-linting)**: Detailed documentation of `format.sh`, tool configurations (`.clang-format`), and the pragma-unroll masking logic.
 - **[Continuous Integration](https://deepwiki.com/deepseek-ai/DeepEP/10.2-continuous-integration)**: Detailed documentation of the GitHub Actions workflow, runner requirements, and PR gating mechanisms.
