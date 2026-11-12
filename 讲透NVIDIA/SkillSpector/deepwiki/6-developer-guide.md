<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/SkillSpector · page 6 Developer Guide · fetched 2026-10-26 -->

# Developer Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [Makefile](Makefile)
- [README.md](README.md)
- [SECURITY.md](SECURITY.md)
- [docs/B.3.2-mcp-tool-poisoning.md](docs/B.3.2-mcp-tool-poisoning.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/SC4-osv-live-vulnerability-lookups.md](docs/SC4-osv-live-vulnerability-lookups.md)
- [tests/integration/__init__.py](tests/integration/__init__.py)
- [tests/unit/__init__.py](tests/unit/__init__.py)

</details>



This guide provides practical information for contributors looking to extend SkillSpector, maintain code quality, or understand the integration roadmap. SkillSpector is built on a **LangGraph** workflow [src/skillspector/graph.py:24-57](), and its modular nature allows for the easy addition of new analysis capabilities.

For a high-level understanding of the system architecture before diving into development, see [Core Architecture](#2).

## Adding Analyzer Nodes

SkillSpector's core strength lies in its parallel analyzer nodes. All analyzers are registered in a central registry and follow a specific protocol to ensure they can be executed within the LangGraph `StateGraph` [src/skillspector/graph.py:43-50]().

*   **Registration**: New nodes must be added to `ANALYZER_NODE_IDS` and mapped in the `ANALYZER_NODES` dictionary [src/skillspector/nodes/analyzers/__init__.py:12-42]().
*   **Protocols**: Analyzers should satisfy the `AnalyzerPlugin` protocol [src/skillspector/data_models.py:284-288]() and return an `AnalyzerNodeResponse` [src/skillspector/state.py:10-12]().
*   **Implementation**:
    *   **Static Analyzers**: Typically use the `run_static_patterns` helper to match regex-based rules [src/skillspector/nodes/analyzers/static_patterns.py:18-35]().
    *   **LLM Analyzers**: Should extend `LLMAnalyzerBase` to benefit from automatic batching, token budgeting, and line-numbered prompts [src/skillspector/llm_analyzer_base.py:46-78]().

For step-by-step instructions and code templates, see **[Adding Analyzer Nodes](#6.1)**.

### Analyzer Integration Map

The following diagram shows how a new analyzer class (e.g., `LLMAnalyzerBase`) relates to the graph state and the final report.

```mermaid
graph TD
    subgraph "Natural Language Space"
        "Security_Rule"["Security Rule"] --> "Prompt_Pattern"["Prompt/Pattern"]
    end

    subgraph "Code Entity Space"
        "Prompt_Pattern" --> "AnalyzerNode"["Analyzer Node (e.g., semantic_security_discovery)"]
        "AnalyzerNode" --> "LLMAnalyzerBase"["LLMAnalyzerBase.arun_batches()"]
        "LLMAnalyzerBase" --> "AnalyzerNodeResponse"["AnalyzerNodeResponse {findings: list[Finding]}"]
        "AnalyzerNodeResponse" --> "SkillspectorState"["SkillspectorState['findings']"]
        "SkillspectorState" --> "report_node"["report_node (SARIF generation)"]
    end
```

**Sources:** [src/skillspector/llm_analyzer_base.py:46-210](), [src/skillspector/state.py:14-55](), [src/skillspector/nodes/report.py:20-45]()

## Code Quality and CI

To maintain a robust and secure codebase, SkillSpector enforces strict linting, formatting, and testing standards.

*   **Linting & Formatting**: We use `ruff` for both linting and code formatting [Makefile:108-128](). Configuration is maintained in `pyproject.toml`.
*   **Automation**: The `Makefile` provides convenient targets for development:
    *   `make lint`: Runs `ruff check` [Makefile:109-111]().
    *   `make format`: Runs `ruff format` and `ruff check --fix` [Makefile:119-122]().
    *   `make test`: Runs unit and integration tests [Makefile:59-60]().
    *   `make test-ci`: Runs tests with Cobertura XML coverage for CI pipelines [Makefile:105-106]().

For details on CI configuration and coverage reporting, see **[Code Quality and CI](#6.2)**.

## MCP Server and Agent Integration

SkillSpector can be deployed as a Model Context Protocol (MCP) server, allowing AI agents (like Pi) to perform security scans dynamically.

*   **MCP Server**: The `mcp_server.py` implementation exposes a `scan_skill` tool [src/skillspector/mcp_server.py:12-45]().
*   **Pi Extension**: A TypeScript extension is provided to integrate SkillSpector directly into agentic workflows [extensions/skillspector.ts:1-20](). The extension registers the `skillspector_scan` tool [extensions/skillspector.ts:84-85]().

For details on the MCP architecture and extension configuration, see **[MCP Server and Pi Extension](#6.3)**.

### Pi Extension Execution Flow

This diagram associates the TypeScript extension logic with the underlying SkillSpector CLI execution.

```mermaid
graph TD
    subgraph "Natural Language Space"
        "User_Prompt"["'Use skillspector_scan on ./my-skill'"]
    end

    subgraph "Code Entity Space"
        "User_Prompt" --> "pi_registerTool"["pi.registerTool(name: 'skillspector_scan')"]
        "pi_registerTool" --> "execute_fn"["execute() in extensions/skillspector.ts"]
        "execute_fn" --> "buildScanArgs"["buildScanArgs() returns ['scan', target, '--format', ...]"]
        "buildScanArgs" --> "pi_exec"["pi.exec(bin, args)"]
        "pi_exec" --> "SkillSpector_CLI"["skillspector scan (CLI entry point)"]
        "SkillSpector_CLI" --> "redactSecrets"["redactSecrets(stdout)"]
    end
```

**Sources:** [extensions/skillspector.ts:66-81](), [extensions/skillspector.ts:84-142](), [docs/PI_EXTENSION.md:1-67]()

## Batch Scan Contrib Module

For large-scale analysis, the `contrib/batch_scan` module provides a high-concurrency runner capable of scanning entire directories of skills in parallel [README.md:170-185](). It features a multi-layer concurrency model and an `ApiKeyPool` to handle LLM rate limits.

For details on the batch scanning architecture, see **[Batch Scan Contrib Module](#6.4)**.

## Contribution Requirements

All contributors must adhere to the following legal and technical requirements:

1.  **DCO Sign-off**: Every commit must be signed off using `git commit -s`. The GitHub Actions CI verifies this via the `dco` job [.github/workflows/ci.yml:112-143]().
2.  **SPDX Headers**: Every new source file must include the standard SPDX license header [src/skillspector/graph.py:1-2]().
3.  **Tests**: New features or analyzers must include unit tests in `tests/unit/` or node-level tests in `tests/nodes/` [Makefile:63-64]().

## SkillTrap Integration Roadmap

The project is moving toward a hybrid analysis model. While SkillSpector handles static and semantic analysis, **SkillTrap** is a proposed dynamic analysis engine that runs skills in instrumented Docker containers.

### Static to Dynamic Flow

This diagram illustrates the planned integration where SkillSpector orchestrates SkillTrap as a subprocess to confirm ambiguous static findings.

```mermaid
graph LR
    subgraph "SkillSpector (Python)"
        "static_nodes"["Static Analyzers"] --> "meta_analyzer"["meta_analyzer (LLM)"]
        "meta_analyzer" --> "dynamic_runner"["dynamic_runner.py"]
    end

    subgraph "SkillTrap (Go)"
        "dynamic_runner" -- "subprocess call" --> "skilltrap_cli"["skilltrap analyze --json"]
        "skilltrap_cli" --> "docker_sandbox"["Docker Sandbox (Falco/strace)"]
        "docker_sandbox" --> "json_report"["JSON Report"]
    end

    "json_report" -- "parse" --> "report_node"["Final Merged Report"]
```

**Sources:** [docs/DEVELOPMENT.md:106-120](), [src/skillspector/graph.py:34-53](), [Makefile:153-154]()

---
**Sources:** [Makefile:1-154](), [docs/DEVELOPMENT.md:1-130](), [src/skillspector/graph.py:1-57](), [src/skillspector/nodes/analyzers/__init__.py:1-42](), [extensions/skillspector.ts:1-142](), [.github/workflows/ci.yml:112-143]()

---

