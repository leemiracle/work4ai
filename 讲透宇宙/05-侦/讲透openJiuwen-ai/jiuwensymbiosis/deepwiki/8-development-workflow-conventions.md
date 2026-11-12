<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/jiuwensymbiosis · page 8 Development Workflow & Conventions · fetched 2026-11-02 -->

# Development Workflow & Conventions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/rules/code-style.md](.claude/rules/code-style.md)
- [.claude/rules/security.md](.claude/rules/security.md)
- [.claude/rules/testing.md](.claude/rules/testing.md)
- [.claude/skills/python-testing/SKILL.md](.claude/skills/python-testing/SKILL.md)
- [.claude/skills/review-architecture-change/SKILL.md](.claude/skills/review-architecture-change/SKILL.md)
- [.claude/skills/security-review/SKILL.md](.claude/skills/security-review/SKILL.md)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This page provides a high-level overview of the development workflow and conventions for contributing to the `jiuwensymbiosis` codebase. It covers contribution rules, coding standards, testing infrastructure, and tooling. For detailed information on each topic, please refer to the linked child pages.

## Contribution Guidelines

Contributing to `jiuwensymbiosis` involves a standard Fork & Pull Request (PR) workflow on GitCode. Developers are expected to set up their Python environment, clone their personal fork, and keep it synchronized with the upstream main branch. All contributions should be made through feature branches and submitted as PRs to the `upstream/main` branch.

The project adheres to specific development principles outlined in [.claude/rules/development-principles.md](). These principles guide decisions on demand and evidence, design investment, responsibility reuse, scope of changes, and validation results.

For detailed instructions on setting up your environment, GitCode workflow, and commit message conventions, see [CONTRIBUTING.md]().

Sources: [CONTRIBUTING.md:1-141]()

## Code Style, Safety & Review Rules

The `jiuwensymbiosis` project enforces strict coding standards and safety protocols to maintain code quality, security, and architectural integrity. These rules are primarily defined in the `.claude/rules/` directory and are used by AI agents (like Claude) for automated reviews.

### Code Style

Python code style is governed by `pyproject.toml` and enforced by `ruff` for formatting, linting, and import sorting. Key guidelines include:
- Python 3.11+ and a line length of 120 characters.
- Use of type annotations for new public interfaces.
- Absolute package imports and explicit public exports in `__init__.py`.
- Preference for immutable value records.
- Use of `jiuwensymbiosis.utils.logging.get_logger(__name__)` for logging in library code, avoiding `print()`.
- Adherence to `jiuwensymbiosis/errors.py` for exception handling.

For a comprehensive list of code style rules, refer to [.claude/rules/code-style.md]().

### Safety Rules

Physical safety and execution trust boundaries are paramount. The codebase includes `SafetyRail` and `RecoveryRail` to prevent unsafe operations and handle failures gracefully. Key safety rules include:
- Never bypassing `SafetyRail` checks for `z_min_safe`, `joint_limits`, and workspace boundaries.
- Preserving payload-aware recovery logic in `jiuwensymbiosis/rails/recovery.py`.
- Loading credentials at runtime from environment variables, never hardcoding them.
- Ensuring `clear_proxy_env()` is called before `import openjiuwen` to prevent proxy issues.
- Reviewing new dependencies for security impact using `pip-audit`.
- Special scrutiny for changes in `jiuwensymbiosis/rails/`, `adapters/*/lowlevel.py`, and `serving/`.

For a complete overview of security and physical safety rules, see [.claude/rules/security.md]().

### Review Rules

The project utilizes AI-assisted review processes. For architectural changes, the `review-architecture-change` skill is used to assess how modifications impact the system model, identifying responsibility shifts, dependency inversions, duplicate contracts, and state ownership splits. This skill reads `AGENTS.md` and relevant architecture documentation to establish a baseline and compare actual changes against intended constraints.

**Architecture Review Workflow**
```mermaid
graph TD
    A[Change Proposed] --> B{Invoke review-architecture-change skill};
    B --> C[Read AGENTS.md, rules, architecture docs];
    C --> D[Establish Base Model (pre-change)];
    C --> E[Establish Head Model (post-change)];
    D --> F{Compare Models};
    E --> F;
    F --> G[Identify Changes in Responsibilities, Contracts, Dependencies];
    G --> H[Check against Project Constraints (e.g., capability gating, state ownership)];
    H --> I[Assess Architectural Impact (Controlled Evolution, Debt, Corruption)];
    I --> J[Generate Review Report (Markdown/HTML)];
    J --> K[Provide Findings, Evidence, Consequences, Recommendations];
```
Sources: [.claude/skills/review-architecture-change/SKILL.md:1-111]()

For details on the architecture review process, refer to [.claude/skills/review-architecture-change/SKILL.md]().

For a summary of all Claude-specific rules and skills, see [CLAUDE.md]().

For details, see [Code Style, Safety & Review Rules](#8.1).

Sources: [.claude/rules/code-style.md:1-71](), [.claude/rules/security.md:1-69](), [.claude/skills/review-architecture-change/SKILL.md:1-111](), [CLAUDE.md:1-58]()

## Testing Infrastructure

The `jiuwensymbiosis` project employs a robust testing infrastructure to ensure reliability and correctness. Tests are categorized into unit and integration tests, with specific conventions for their placement and execution.

### Test Organization

- **Unit Tests**: Located in `tests/unit_tests/`, these are fast, deterministic, and hardware-free. They typically mirror the source subsystem's directory structure (e.g., `jiuwensymbiosis/tools/builder.py` has tests in `tests/unit_tests/tools/test_builder.py`).
- **Integration Tests**: Located in `tests/integration/`, these require real hardware, GPUs, or external services and are often skipped in CI.
- **Mocks**: Shared mock objects like `MockApi`, `MockArmEnvWrapper`, `MockPiperDriver`, and `MockScene` are available in `tests/mocks/` to facilitate hardware-free unit testing.

### Test Doubles and Fixtures

The `tests/conftest.py` file provides common fixtures, and `tests/helpers.py` offers lifecycle helpers like `make_mock_session` and `FakeCtx`. For LLM tests, `build_mock_model()` from `jiuwensymbiosis/agent/mock_model.py` is used via `RobotAgentConfig(model=...)` to avoid real credentials or hardware.

**Test Double Selection**
```mermaid
graph TD
    A[Need to Test] --> B{Hardware-free?};
    B -- Yes --> C{In-memory arm/common fixtures?};
    C -- Yes --> D[jiuwensymbiosis/env/mock.py, tests/conftest.py];
    B -- No --> E[Integration Test (real hardware/GPU)];
    C -- No --> F{API, Driver, Detector doubles?};
    F -- Yes --> G[tests/mocks/__init__.py];
    F -- No --> H{Session, Callback, Trace sink?};
    H -- Yes --> I[tests/helpers.py (make_mock_session, FakeCtx, RecordingRailSink)];
    H -- No --> J{LLM replacement?};
    J -- Yes --> K[jiuwensymbiosis/agent/mock_model.py (build_mock_model)];
    J -- No --> L{Calibration workflow dependencies?};
    L -- Yes --> M[tests/unit_tests/calibration/conftest.py];
    L -- No --> N[Consider creating a focused local fake];
```
Sources: [.claude/skills/python-testing/SKILL.md:27-42]()

### Testing Safety and Execution

Safety-related behaviors, such as `SafetyRail` enforcement, are tested by invoking the rail's callbacks directly with mock contexts and sessions. This ensures policy behavior is checked independently of the full execution path. Logging behavior is verified using `caplog`.

For detailed information on the testing workflow, test double selection, and specific testing rules, refer to [.claude/rules/testing.md]() and [.claude/skills/python-testing/SKILL.md]().

For details, see [Testing Infrastructure](#8.2).

Sources: [CONTRIBUTING.md:183-187](), [.claude/rules/testing.md:1-40](), [.claude/skills/python-testing/SKILL.md:1-98]()

## Logging, Utilities & Scripts

The codebase includes various utilities and scripts to aid development, debugging, and analysis.

### Logging

Logging in library code should use `jiuwensymbiosis.utils.logging.get_logger(__name__)` to ensure consistent configuration and proper handling by `TraceLogHandler` and file handlers. This central logging configuration is crucial for capturing execution traces and debugging. `print()` statements are reserved for user-facing CLI output.

### Proxy Management

The `jiuwensymbiosis/utils/proxy.py` module provides `clear_proxy_env()`, which is critical for preventing `httpx` from routing localhost traffic through HTTP proxies, especially when interacting with local vLLM or detection services. This function **must be called before `import openjiuwen`**.

### Analysis and Design Notes

The project includes tools for analyzing execution traces, such as `analyze_traces`. Design notes and miscellaneous scripts are also part of the `utils/` and `scripts/` directories, providing insights into specific functionalities or offering helper automation.

For details, see [Logging, Utilities & Scripts](#8.3).

Sources: [CONTRIBUTING.md:29-31](), [CONTRIBUTING.md:156-158](), [.claude/rules/code-style.md:53-55](), [.claude/rules/security.md:55-56]()

## Documentation Site (docs)

The `docs/` directory hosts the project's documentation site, which is structured to provide comprehensive information for various user needs.

### Documentation Structure

The documentation is bilingual and organized into standard categories:
- **Tutorials**: Step-by-step guides for common tasks.
- **How-to Guides**: Instructions for achieving specific goals.
- **Reference**: Detailed descriptions of APIs, configurations, and technical concepts.
- **Explanation**: High-level overviews and conceptual discussions.
- **Images**: Supporting visual assets.

When making changes to the codebase, it is essential to update the relevant documentation to reflect those changes. This includes updating API descriptions, configuration options, and any behavioral modifications.

For details, see [Documentation Site (docs)](#8.4).

---

