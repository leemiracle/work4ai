<!-- source: DeepWiki mcp.deepwiki.com · repo agent0ai/agent-zero · page 12 Testing & Development · fetched 2026-10-29 -->

# Testing & Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [extensions/python/startup_migration/AGENTS.md](extensions/python/startup_migration/AGENTS.md)
- [extensions/python/startup_migration/_05_framework_dependencies.py](extensions/python/startup_migration/_05_framework_dependencies.py)
- [extensions/python/startup_migration/_10_self_update_manager.py](extensions/python/startup_migration/_10_self_update_manager.py)
- [tests/AGENTS.md](tests/AGENTS.md)
- [tests/chunk_parser_test.py](tests/chunk_parser_test.py)
- [tests/rate_limiter_test.py](tests/rate_limiter_test.py)
- [tests/test_fasta2a_client.py](tests/test_fasta2a_client.py)
- [tests/test_framework_dependencies.py](tests/test_framework_dependencies.py)
- [tests/test_self_update_runtime_sync.py](tests/test_self_update_runtime_sync.py)

</details>



This wiki page provides a high-level overview of the testing infrastructure, startup migrations, development workflows, skills, and documentation practices used in Agent Zero. The project employs a hybrid development model that balances containerized runtime safety with local IDE debugging and robust test automation.

As a parent page, this section introduces the core concepts and links to detailed child pages:
- For detailed test suite structures and patterns, see [Test Suite](#12.1).
- For hybrid setup and RFC mode instructions, see [Developer Setup & RFC Mode](#12.2).
- For developer skills and documentation layouts, see [Developer Skills & Documentation](#12.3).

---

### Development Philosophy & Runtimes

Agent Zero separates concerns between the **Framework Runtime** (managing the agent loop, backend server, and startup migrations) and the **Execution Runtime** (handling untrusted task code and container operations) [prompts/agent.system.main.environment.md:6-9](). 

- **Framework Runtime (`/opt/venv-a0`):** Runs Agent Zero core code, backend APIs, extension hooks, framework dependency enforcement [extensions/python/startup_migration/_05_framework_dependencies.py:21-25](), and self-update synchronization [extensions/python/startup_migration/_10_self_update_manager.py:36-47]().
- **Execution Runtime (`/opt/venv`):** Executes task code and isolated tool dependencies [prompts/agent.system.main.environment.md:7]().

Developers should maintain clear boundaries between these environments during troubleshooting and verification [prompts/agent.system.main.environment.md:9]().

Sources: [prompts/agent.system.main.environment.md:1-10](), [extensions/python/startup_migration/_05_framework_dependencies.py:21-42](), [extensions/python/startup_migration/_10_self_update_manager.py:36-47]()

---

### Test Suite Overview

Agent Zero relies on `pytest` for regression, security, integration, and contract tests under the `tests/` directory [tests/AGENTS.md:1-5](). Tests must remain deterministic, isolated from local runtime state, and independent of real API keys or network-only services [tests/AGENTS.md:16-17](). Startup migrations and environment synchronizations are also validated via automated tests [tests/test_framework_dependencies.py:27-58](), [tests/test_self_update_runtime_sync.py:45-65]().

For detailed test conventions, fixture usage, and module breakdowns, refer to [Test Suite](#12.1).

Sources: [tests/AGENTS.md:1-35](), [tests/test_framework_dependencies.py:27-58](), [tests/test_self_update_runtime_sync.py:45-65]()

---

### Developer Setup & RFC Mode

The recommended development workflow utilizes **RFC (Remote Function Call)** mode, where the framework runs natively on the developer's host machine while execution commands are routed to an isolated container environment. Startup migrations under `extensions/python/startup_migration/` ensure database schemas, framework dependencies (`_05_framework_dependencies.py`), and self-update components (`_10_self_update_manager.py`) are properly initialized and synchronized on startup.

For a comprehensive guide on IDE configuration, launch setups, and sync scripts, refer to [Developer Setup & RFC Mode](#12.2).

Sources: [extensions/python/startup_migration/_05_framework_dependencies.py:21-42](), [extensions/python/startup_migration/_10_self_update_manager.py:36-47](), [prompts/agent.system.main.environment.md:1-10]()

---

### Developer Skills & Documentation

Agent Zero incorporates built-in development skills (such as `a0-development`) to guide agents and human contributors through framework extension, API usage, and operations [skills/a0-development/SKILL.md:1-33](). Documentation is maintained alongside source code using `.dox.md` sidecar files and hierarchical `AGENTS.md` dox files (such as `tests/AGENTS.md` and `extensions/python/startup_migration/AGENTS.md`).

For details on the development skill workflows and the documentation tree, refer to [Developer Skills & Documentation](#12.3).

Sources: [tests/AGENTS.md:1-15](), [extensions/python/startup_migration/AGENTS.md:1-20](), [skills/a0-development/SKILL.md:1-33]()

---

### Developer Tooling & Architecture Mapping

The following diagrams bridge natural language development concepts to their concrete code entities within the repository.

Development Entity Map
```mermaid
graph TD
    subgraph "Natural Language Space"
        "Testing_Logic"["Testing & Validation"]
        "Model_Rate_Limiting"["Model Rate Limiting"]
        "Agent_Routing"["Agent-to-Agent Routing"]
    end

    subgraph "Code Entity Space"
        "tests_dir"["Suite: tests/"]
        "chunk_test"["Test: tests/chunk_parser_test.py"]
        "rate_test"["Test: tests/rate_limiter_test.py"]
        "fasta2a_test"["Test: tests/test_fasta2a_client.py"]
        "dev_skill"["Skill: skills/a0-development/SKILL.md"]
    end

    "Testing_Logic" --> "tests_dir"
    "Testing_Logic" --> "chunk_test"
    "Model_Rate_Limiting" --> "rate_test"
    "Agent_Routing" --> "fasta2a_test"
    "Testing_Logic" --> "dev_skill"
```
Sources: [tests/AGENTS.md:1-12](), [tests/chunk_parser_test.py:13-21](), [tests/rate_limiter_test.py:9-20](), [tests/test_fasta2a_client.py:15-40](), [skills/a0-development/SKILL.md:1-15]()

Runtime Separation Map
```mermaid
graph LR
    subgraph "Natural Language Space"
        "Framework_Runtime"["Framework Environment"]
        "Execution_Runtime"["Execution Environment"]
        "Doc_Workflow"["Documentation & DOX"]
    end

    subgraph "Code Entity Space"
        "env_prompt"["Prompt: prompts/agent.system.main.environment.md"]
        "venv_a0"["Virtualenv: /opt/venv-a0"]
        "venv_exec"["Virtualenv: /opt/venv"]
        "skill_ag"["DOX: tests/AGENTS.md"]
    end

    "Framework_Runtime" --> "venv_a0"
    "Execution_Runtime" --> "venv_exec"
    "Framework_Runtime" --> "env_prompt"
    "Doc_Workflow" --> "skill_ag"
```
Sources: [prompts/agent.system.main.environment.md:6-9](), [tests/AGENTS.md:1-15]()

---

### Child Pages

- **[Test Suite](#12.1)** — Covers the `tests/` directory structure, test files, static-assertion patterns, and `tests/AGENTS.md` guidelines.
- **[Developer Setup & RFC Mode](#12.2)** — Covers the hybrid development loop, VS Code launch configuration, RFC protocol, and synchronization scripts.
- **[Developer Skills & Documentation](#12.3)** — Covers the `a0-development` skill, reference documentation, build tools, and the `.dox.md` sidecar workflow.

---

