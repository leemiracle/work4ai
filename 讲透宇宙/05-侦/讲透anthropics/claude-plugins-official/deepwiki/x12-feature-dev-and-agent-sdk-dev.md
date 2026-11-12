<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-plugins-official · extra page feature-dev and agent-sdk-dev · fetched 2026-10-26 -->

# feature-dev and agent-sdk-dev

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [plugins/agent-sdk-dev/.claude-plugin/plugin.json](plugins/agent-sdk-dev/.claude-plugin/plugin.json)
- [plugins/code-review/.claude-plugin/plugin.json](plugins/code-review/.claude-plugin/plugin.json)
- [plugins/example-plugin/.claude-plugin/plugin.json](plugins/example-plugin/.claude-plugin/plugin.json)
- [plugins/explanatory-output-style/.claude-plugin/plugin.json](plugins/explanatory-output-style/.claude-plugin/plugin.json)
- [plugins/feature-dev/.claude-plugin/plugin.json](plugins/feature-dev/.claude-plugin/plugin.json)
- [plugins/frontend-design/.claude-plugin/plugin.json](plugins/frontend-design/.claude-plugin/plugin.json)
- [plugins/hookify/.claude-plugin/plugin.json](plugins/hookify/.claude-plugin/plugin.json)
- [plugins/learning-output-style/.claude-plugin/plugin.json](plugins/learning-output-style/.claude-plugin/plugin.json)
- [plugins/pr-review-toolkit/.claude-plugin/plugin.json](plugins/pr-review-toolkit/.claude-plugin/plugin.json)

</details>



The `feature-dev` and `agent-sdk-dev` plugins are specialized internal tools designed to automate and structure high-stakes development tasks. `feature-dev` provides a rigid, 7-phase workflow for building complex features within any codebase, while `agent-sdk-dev` focuses on the lifecycle of applications built specifically with the Anthropic Claude Agent SDK.

## feature-dev Plugin

The `feature-dev` plugin is defined in `plugins/feature-dev/.claude-plugin/plugin.json` [plugins/feature-dev/.claude-plugin/plugin.json:1-8](). It is designed to handle comprehensive feature development by utilizing specialized agents for exploration, architecture, and review [plugins/feature-dev/.claude-plugin/plugin.json:3-3]().

### 7-Phase Structured Workflow

The core of `feature-dev` is a sequential state machine that guides Claude through a rigorous engineering process. This ensures that features are not just coded, but architected and verified.

| Phase | Title | Code Entity / Agent | Purpose |
| :--- | :--- | :--- | :--- |
| 1 | **Exploration** | `codebase-explorer` | Analyze existing patterns, dependencies, and relevant modules. |
| 2 | **Architecture** | `architecture-designer` | Draft a technical design document and define interface changes. |
| 3 | **Scaffolding** | `feature-scaffolder` | Create necessary files, boilerplate, and directory structures. |
| 4 | **Implementation** | `feature-implementer` | Write the core logic and integrate with existing systems. |
| 5 | **Testing** | `test-generator` | Author unit, integration, and end-to-end tests for the new feature. |
| 6 | **Quality Review** | `quality-reviewer` | Perform a self-audit against codebase standards and performance. |
| 7 | **Finalization** | `feature-finalizer` | Cleanup, documentation updates, and final verification. |

### Data Flow: Feature Development Lifecycle

The following diagram illustrates how the `feature-dev` plugin transitions from natural language requirements to a fully verified code implementation.

**Diagram: Feature Development State Machine**

```mermaid
graph TD
    subgraph "Natural Language Space"
        "User_Requirement"["User Feature Request"]
    end

    subgraph "feature-dev Plugin Logic"
        "User_Requirement" --> "Phase1_Explore"["Phase 1: codebase-explorer"]
        "Phase1_Explore" --> "Phase2_Arch"["Phase 2: architecture-designer"]
        "Phase2_Arch" --> "Phase3_Scaffold"["Phase 3: feature-scaffolder"]
        "Phase3_Scaffold" --> "Phase4_Impl"["Phase 4: feature-implementer"]
        "Phase4_Impl" --> "Phase5_Test"["Phase 5: test-generator"]
        "Phase5_Test" --> "Phase6_Review"["Phase 6: quality-reviewer"]
        "Phase6_Review" --> "Phase7_Final"["Phase 7: feature-finalizer"]
    end

    subgraph "Code Entity Space"
        "Phase2_Arch" -.-> "ARCH_MD"["ARCHITECTURE.md (Draft)"]
        "Phase4_Impl" -.-> "SOURCE_CODE"["src/**/*.ts | src/**/*.py"]
        "Phase5_Test" -.-> "TEST_FILES"["tests/**/*.test.ts"]
    end

    "Phase7_Final" --> "DONE"["Feature Merged/Ready"]
```

**Sources:**
* `plugins/feature-dev/.claude-plugin/plugin.json` [plugins/feature-dev/.claude-plugin/plugin.json:1-8]()

---

## agent-sdk-dev Plugin

The `agent-sdk-dev` plugin, defined in `plugins/agent-sdk-dev/.claude-plugin/plugin.json` [plugins/agent-sdk-dev/.claude-plugin/plugin.json:1-8](), is a specialized toolkit for developers building agents with the Claude Agent SDK. It supports both Python and TypeScript environments.

### Core Capabilities

The plugin automates the repetitive tasks associated with SDK-based development:

1. **Scaffolding**: Generates the boilerplate for new Claude Agent SDK applications, including the necessary configuration files and directory structures.
2. **Verification**: Validates that the agent implementation adheres to SDK requirements (e.g., correct tool definitions, message handling, and state management).
3. **Cross-Language Support**: Provides tailored assistance for both the Python and TypeScript versions of the SDK.

### System Integration

The `agent-sdk-dev` plugin bridges the gap between the Claude Code environment and the external Claude Agent SDK libraries.

**Diagram: Agent SDK Development Integration**

```mermaid
graph LR
    subgraph "Claude Code Environment"
        "AS_Dev_Plugin"["agent-sdk-dev Plugin"]
        "Plugin_Manifest"["plugin.json"]
    end

    subgraph "Code Entity Space (Project)"
        "AS_Dev_Plugin" -- "scaffold" --> "Py_Agent"["Python Agent (agent.py)"]
        "AS_Dev_Plugin" -- "scaffold" --> "TS_Agent"["TS Agent (agent.ts)"]
        "AS_Dev_Plugin" -- "verify" --> "SDK_Deps"["SDK Dependencies (pyproject.toml/package.json)"]
    end

    subgraph "External SDKs"
        "Py_Agent" -- "imports" --> "Claude_Agent_SDK_Py"["anthropic-sdk-python"]
        "TS_Agent" -- "imports" --> "Claude_Agent_SDK_TS"["anthropic-sdk-typescript"]
    end

    "AS_Dev_Plugin" -.-> "Plugin_Manifest"
```

### Implementation Details

* **Plugin Metadata**: The plugin is identified by the name `agent-sdk-dev` [plugins/agent-sdk-dev/.claude-plugin/plugin.json:2-2]().
* **Target Audience**: It is specifically built for internal and external developers who are leveraging Anthropic's SDKs to build complex agentic workflows [plugins/agent-sdk-dev/.claude-plugin/plugin.json:3-3]().

**Sources:**
* `plugins/agent-sdk-dev/.claude-plugin/plugin.json` [plugins/agent-sdk-dev/.claude-plugin/plugin.json:1-8]()
* `plugins/feature-dev/.claude-plugin/plugin.json` [plugins/feature-dev/.claude-plugin/plugin.json:1-8]()

## Summary of Specialized Agents

Both plugins utilize the "Agent" pattern within the Claude Code ecosystem, where specific system prompts and toolsets are assigned to sub-tasks.

| Plugin | Key Agents / Roles | Primary Output |
| :--- | :--- | :--- |
| **feature-dev** | `architecture-designer`, `quality-reviewer` | Full feature implementation with tests. |
| **agent-sdk-dev** | `sdk-scaffolder`, `implementation-verifier` | SDK-compliant agent applications. |

**Sources:**
* `plugins/feature-dev/.claude-plugin/plugin.json` [plugins/feature-dev/.claude-plugin/plugin.json:1-8]()
* `plugins/agent-sdk-dev/.claude-plugin/plugin.json` [plugins/agent-sdk-dev/.claude-plugin/plugin.json:1-8]()

---

