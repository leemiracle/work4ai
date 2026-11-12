<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/pi-llama · page 4 Developer Tooling and CI · fetched 2026-10-26 -->

# Developer Tooling and CI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.oxfmtrc.json](.oxfmtrc.json)
- [.oxlintrc.json](.oxlintrc.json)
- [.prettierignore](.prettierignore)

</details>



This section provides an overview of the developer experience and automated quality assurance for the `pi-llama` codebase. The project prioritizes high-performance tooling to maintain code quality with minimal overhead.

The toolchain is centered around the `oxc` suite (Oxc Compiler), utilizing `oxfmt` for code formatting and `oxlint` for static analysis. These tools are integrated into a GitHub Actions pipeline to ensure that every contribution adheres to the project's standards.

### Tooling Architecture and Workflow

The following diagram illustrates how local configuration files guide the tooling during development and within the CI environment.

**Developer Tooling Flow**
```mermaid
graph TD
    subgraph "Local Environment"
        ["Developer Code"] -- "Formatting" --> ["oxfmt"]
        ["Developer Code"] -- "Linting" --> ["oxlint"]
        [".oxfmtrc.json"] -. "Configures" .-> ["oxfmt"]
        [".oxlintrc.json"] -. "Configures" .-> ["oxlint"]
    end

    subgraph "Continuous Integration (GitHub Actions)"
        ["ci.yml"] -- "Runs" --> ["check Job"]
        ["check Job"] -- "npx --yes oxfmt --check ." --> ["oxfmt CI"]
        ["check Job"] -- "npx --yes oxlint ." --> ["oxlint CI"]
    end

    ["oxfmt CI"] -- "Failure" --> ["Block Merge"]
    ["oxlint CI"] -- "Failure" --> ["Block Merge"]
```
Sources: [`.oxfmtrc.json:1-3`](), [`.oxlintrc.json:1-5`](), [`.github/workflows/ci.yml:1-19`]()

---

### Code Formatting
The project uses `oxfmt` to enforce a consistent coding style. A notable configuration choice is the use of tabs for indentation, as specified in the configuration file [`.oxfmtrc.json:1-3`](). 

To prevent conflicts between different formatting tools, certain file types are excluded from processing. For instance, JSON files are explicitly ignored via the Prettier ignore configuration [`.prettierignore:1-2`]().

For details on configuration and editor integration, see [Code Formatting](#4.1).

### Linting
Static analysis is handled by `oxlint`, which is configured to catch common errors and enforce specific logic structures. The primary rule enforced across the repository is the mandatory use of curly braces for all control-flow statements, such as `if`, `while`, and `for` loops [`.oxlintrc.json:3-3`](). This reduces ambiguity and prevents bugs during code refactoring.

For details on the rationale and full rule list, see [Linting](#4.2).

### Continuous Integration Pipeline
The CI pipeline is automated via GitHub Actions and is triggered on every push to the `main` branch and for all pull requests [`.github/workflows/ci.yml:3-7`](). The pipeline executes a single `check` job on an `ubuntu-latest` runner [`.github/workflows/ci.yml:9-10`]().

The pipeline uses `npx --yes` to execute the tools without requiring a local `node_modules` installation or interactive prompts, ensuring a fast and clean execution environment for the following steps:
1. **Formatting Check**: Verifies that all files comply with `oxfmt` rules [`.github/workflows/ci.yml:14-15`]().
2. **Linting Check**: Runs `oxlint` to identify any code quality or logic violations [`.github/workflows/ci.yml:17-18`]().

For details on the workflow configuration and trigger conditions, see [Continuous Integration Pipeline](#4.3).

**Tooling to Code Entity Mapping**
| Tool | Configuration File | CI Step Name | Purpose |
| :--- | :--- | :--- | :--- |
| `oxfmt` | [`.oxfmtrc.json`]() | `oxfmt (check)` | Enforces tab-based indentation |
| `oxlint` | [`.oxlintrc.json`]() | `oxlint` | Enforces mandatory curly braces |
| `GitHub Actions` | [`.github/workflows/ci.yml`]() | `check` | Orchestrates the quality gate |

Sources: [`.oxfmtrc.json:1-3`](), [`.oxlintrc.json:1-5`](), [`.github/workflows/ci.yml:8-19`]()

---

