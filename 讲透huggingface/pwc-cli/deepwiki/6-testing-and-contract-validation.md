<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/pwc-cli · page 6 Testing and Contract Validation · fetched 2026-10-26 -->

# Testing and Contract Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [standalone_cli/scripts/check_contract.py](standalone_cli/scripts/check_contract.py)
- [standalone_cli/tests/test_cli.py](standalone_cli/tests/test_cli.py)

</details>



The `pwc-cli` codebase employs a two-tier validation strategy to ensure functional correctness and documentation synchronization. This system prevents "documentation drift," where the actual CLI capabilities diverge from the instructions provided to users or AI agents.

The validation architecture consists of a comprehensive functional test suite and a specialized contract-checking script that performs static analysis on the CLI's command tree.

### Validation Overview

The testing and validation stack is divided into two primary areas:

1.  **Functional Testing**: A `pytest`-based suite that exercises the `argparse` parser, the `Client` transport, and the `skills` installation logic.
2.  **Contract Enforcement**: A validation script that performs a Deep-First Search (DFS) on the command parser to ensure every executable path is documented in both the human-readable guide and the machine-readable skill manifest.

### System Verification Flow

The following diagram illustrates how the validation tools bridge the gap between the code definitions and the external documentation assets.

**Natural Language to Code Entity Mapping: Validation Flow**
```mermaid
graph TD
    subgraph "Natural Language Space (Documentation)"
        [CLI_GUIDE.md]
        [SKILL.md]
    end

    subgraph "Code Entity Space (Logic)"
        [check_contract.py:main] --> |"DFS Traversal"| [cli.py:build_parser]
        [test_cli.py] --> |"Unit Tests"| [cli.py:main]
        [test_cli.py] --> |"Mocking"| [transport.py:Client]
    end

    [check_contract.py:main] -.-> |"Validates Parity"| [CLI_GUIDE.md]
    [check_contract.py:main] -.-> |"Validates Parity"| [SKILL.md]
    [cli.py:build_parser] -.-> |"Provides Schema"| [SKILL.md]
```
Sources: [standalone_cli/scripts/check_contract.py:68-82](), [standalone_cli/tests/test_cli.py:26-82]()

---

## Test Suite (test_cli.py)

The primary test suite focuses on verifying the `argparse` configuration and the handling of various input/output scenarios. It ensures that all subcommands are correctly wired to their respective handlers and that flags (like `--json`, `--include-evals`, or `--task`) correctly populate the namespace objects.

Key areas covered by the test suite include:
*   **Parser Integrity**: Verifying that internal-only commands (e.g., `auth`) are excluded from the public CLI build while all public commands are present.
*   **Transport Mocking**: Patterns for intercepting `urllib` calls to simulate API responses and network errors.
*   **Skill Installation**: Testing the atomic installation and symlinking logic used to deploy `SKILL.md` to agent directories.

For details, see [Test Suite (test_cli.py)](#6.1).

Sources: [standalone_cli/tests/test_cli.py:26-40](), [standalone_cli/tests/test_cli.py:98-123]()

---

## Contract Checker (check_contract.py)

The contract checker is a critical CI/CD component that ensures the `pwc-cli` remains "self-documenting." It uses a registry-based approach to compare the live code against static documentation files.

| Component | Responsibility |
| :--- | :--- |
| `COMMANDS` Registry | Defines the ground-truth list of expected subcommands. |
| `parser_commands()` | Dynamically discovers all commands in `build_parser()` via DFS. |
| Parity Check | Fails if the parser contains commands not in the registry, or vice versa. |
| Coverage Check | Ensures every research command is mentioned in `CLI_GUIDE.md` and `SKILL.md`. |

**Contract Discovery Logic**
```mermaid
graph LR
    [check_contract.py] -- "calls" --> [parser_commands]
    [parser_commands] -- "inspects" --> [argparse.ArgumentParser]
    [argparse.ArgumentParser] -- "yields" --> [choices]
    [choices] -- "recursive visit" --> [discovered_set]
    [discovered_set] -- "compare" --> [COMMANDS_registry]
```

For details, see [Contract Checker (check_contract.py)](#6.2).

Sources: [standalone_cli/scripts/check_contract.py:14-37](), [standalone_cli/scripts/check_contract.py:42-65]()

---

