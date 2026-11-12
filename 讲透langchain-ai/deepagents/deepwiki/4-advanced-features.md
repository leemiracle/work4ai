<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/deepagents · page 4 Advanced Features · fetched 2026-10-26 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/code/deepagents_code/_ask_user_types.py](libs/code/deepagents_code/_ask_user_types.py)
- [libs/code/deepagents_code/ask_user.py](libs/code/deepagents_code/ask_user.py)
- [libs/code/deepagents_code/auto_mode.py](libs/code/deepagents_code/auto_mode.py)
- [libs/code/tests/unit_tests/test_ask_user_middleware.py](libs/code/tests/unit_tests/test_ask_user_middleware.py)
- [libs/code/tests/unit_tests/test_ask_user_types.py](libs/code/tests/unit_tests/test_ask_user_types.py)
- [libs/code/tests/unit_tests/test_auto_mode.py](libs/code/tests/unit_tests/test_auto_mode.py)

</details>



This page provides a high-level overview of the advanced functionality within the Deep Agents ecosystem, spanning both the core SDK and the `deepagents-code` application. Here, we introduce the Human-in-the-Loop (HITL) approval mechanisms including automated decision-making via classifier-assisted Auto mode, large tool result eviction to manage token budgets, sandbox integrations for safe execution, patterns for creating custom tools and middleware, streaming execution flow considerations, and security features with path validation and shell command controls.

For foundational usage, such as basic agent creation and middleware, see [Agent Creation (create_deep_agent)](#2.1) and [deepagents-code Application](#3).

---

## Human-in-the-Loop (HITL) Approval and Auto Mode

HITL approval enables user intervention during agent executions for safety-critical or security-sensitive operations. It acts as a gatekeeper before executing certain types of tool calls — for example, file modifications, shell commands, or credential access — allowing a user to review and authorize actions.

The `interrupt_on` agent configuration defines which tool calls trigger these interruptions, implemented within the HITL middleware [libs/code/deepagents_code/auto_mode.py:27-34](). 

To streamline this process, an Auto mode leverages a classifier-backed policy (`AutoModeHITLMiddleware`). This middleware automates approvals for routine, low-risk commands by evaluating the user's intent using a dedicated classifier model and applying predefined safety policies. It categorizes actions into decision types like destructive changes or credential access to decide when to require human review [libs/code/deepagents_code/auto_mode.py:63-78]().

Additionally, a shell allow-list bypasses review for frequently used, safe commands to reduce friction. YOLO ("You Only Live Once") mode permits skipping approval caches for certain testing or development purposes [libs/code/deepagents_code/auto_mode.py:70-74]().

### HITL and Auto Mode Flow

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        "UserIntent"["User Request"]
    end

    subgraph "CodeEntitySpace"
        "create_deep_agent"["create_deep_agent()"]
        "AutoModeHITLMiddleware"["AutoModeHITLMiddleware<br/>(auto_mode.py)"]
        "LangGraphPregel"["LangGraph Pregel<br/>(interrupt hook)"]
        "TextualUIAdapter"["TextualUIAdapter"]
        "ApprovalMenu"["ApprovalMenu<br/>(auto_mode.py)"]
        "ResumeCommand"["Command(resume=...)"]
    end

    "UserIntent" --> "create_deep_agent"
    "create_deep_agent" --> "AutoModeHITLMiddleware"
    "AutoModeHITLMiddleware" --> "LangGraphPregel"
    "LangGraphPregel" --> "TextualUIAdapter"
    "TextualUIAdapter" --> "ApprovalMenu"
    "ApprovalMenu" -- "User Input" --> "ResumeCommand"
    "ResumeCommand" --> "LangGraphPregel"
```

This flow illustrates how user input triggers execution via `create_deep_agent()`, which uses `AutoModeHITLMiddleware` for approval decisions. When a tool call matches `interrupt_on` criteria, LangGraph's Pregel runtime interrupts execution. The CLI adapter presents an approval menu to the user, who resumes or denies the action, feeding back into the runtime.

For a comprehensive technical dive, see [Human-in-the-Loop (HITL) Approval and Auto Mode](#4.1).

---

## Tool Result Eviction

Tool outputs can sometimes be very large, potentially exceeding token limits for the underlying language model context window. To address this, Deep Agents implements an eviction and offloading system that intercepts large tool results, stores them externally, and provides summaries or previews as lightweight stand-ins.

The eviction logic uses token thresholds to determine when to offload results. If the output size exceeds these thresholds, middleware such as `offload_middleware` intercepts and redirects storage to a dedicated backend location (e.g., `/large_tool_results/`) [libs/deepagents/deepagents/middleware/filesystem.py:82-88](). This preserves runtime efficiency and avoids choking the language model context.

Additionally, preview generation techniques produce truncated or summarized representations so that the agent and user can still see meaningful feedback without loading entire large outputs [libs/deepagents/deepagents/middleware/filesystem.py:85]().

For detailed implementation and usage, see [Tool Result Eviction](#4.2).

---

## Sandbox Integration

Sandbox backends provide isolated execution environments that encapsulate command execution, file operations, and other runtime activities. They abstract away host details and ensure secure, reproducible agent executions.

The key interface is the `SandboxBackendProtocol` [libs/deepagents/deepagents/backends/protocol.py:40-60](), which sandboxes implement. The system currently supports multiple sandbox providers, including:

- Local shell sandbox for straightforward command execution.
- LangSmith sandbox.
- Remote cloud sandboxes: Daytona, Modal, Runloop, and Vercel integrations [libs/deepagents/deepagents/backends/sandbox.py:3-61]().

These sandboxes provide implementations for essential operations like `execute()` and `upload_files()`. 

For instance, large file replacements during edits can be handled server-side by sandbox utilities, reducing client-server round-trips and complexity [libs/deepagents/tests/unit_tests/backends/test_sandbox_backend.py:26-34]().

### Sandbox Integration Overview Diagram

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        "AgentExec"["Agent Execution"]
    end

    subgraph "CodeEntitySpace"
        "SandboxBackendProtocol"["SandboxBackendProtocol<br/>(backends/protocol.py)"]
        "LocalShellSandbox"["LocalShellSandbox<br/>(backends/sandbox.py)"]
        "LangSmithSandbox"["LangSmithSandbox<br/>(backends/sandbox.py)"]
        "PartnerSandboxes"["Daytona / Modal / Runloop / Vercel<br/>(external integration)"]
        "ExecuteUpload"["execute(), upload_files()"]
    end

    "AgentExec" --> "SandboxBackendProtocol"
    "SandboxBackendProtocol" --> "LocalShellSandbox"
    "SandboxBackendProtocol" --> "LangSmithSandbox"
    "SandboxBackendProtocol" --> "PartnerSandboxes"
    "LocalShellSandbox" --> "ExecuteUpload"
    "LangSmithSandbox" --> "ExecuteUpload"
    "PartnerSandboxes" --> "ExecuteUpload"
```

For more information, see [Sandbox Integration](#4.3).

---

## Custom Development

### Custom Tools

Developers can extend the agent's capabilities by creating custom tools using the `StructuredTool` interface. This approach promotes strong argument validation using Pydantic schemas to ensure that language models produce correct, well-typed inputs for tool calls.

Built-in tools such as `fetch_url` serve as examples of how to develop managed tools within Deep Agents, combining schema validation and runtime logic [libs/deepagents/deepagents/middleware/filesystem.py:34-50]().

For best practices and technical details, see [Custom Tools Development](#4.4).

### Custom Middleware

Middleware allows interception and modification of agent execution flows. Implementing the `AgentMiddleware` interface provides hooks such as:

- `wrap_model_call`: To mutate or observe language model requests and responses.
- `wrap_tool_call`: To inspect or alter tool calls and their results.

Middleware ordering and state management are essential considerations for composing robust extensions [libs/deepagents/deepagents/middleware/filesystem.py:19-30]().

See [Custom Middleware Development](#4.5) for more details.

---

## Streaming and Execution Flow

Agent execution heavily relies on LangGraph's streaming event architecture, which enables responsive output streaming and efficient processing.

The CLI application uses `TextualUIAdapter` to consume these streams and render them interactively, while middleware components handle ongoing tool invocation and chunk processing [libs/deepagents/deepagents/middleware/filesystem.py:19-30](). The system supports features like model retry, incremental chunk handling, and interrupt processing.

### Streaming Execution Flow Diagram

```mermaid
graph TB
    subgraph "ExecutionFlow"
        "LangGraphGraph"["LangGraph Graph"]
        "StreamEvents"["astream_events"]
        "TextualUIAdapter"["TextualUIAdapter"]
    end

    subgraph "deepagents-codeEntities"
        "DeepAgentsApp"["DeepAgentsApp"]
        "MessageStore"["MessageStore"]
        "FilesystemMiddleware"["FilesystemMiddleware<br/>(middleware/filesystem.py)"]
    end

    "LangGraphGraph" --> "StreamEvents"
    "StreamEvents" --> "TextualUIAdapter"
    "TextualUIAdapter" --> "DeepAgentsApp"
    "DeepAgentsApp" --> "MessageStore"
    "LangGraphGraph" -- "ToolCall" --> "FilesystemMiddleware"
```

For in-depth explanation, see [Streaming and Execution Flow](#4.6).

---

## Security and Path Validation

Security is layered throughout Deep Agents, enforcing strict validation and sandboxing to prevent abuse or unintended consequences.

### Key Security Features

- **Path Validation**: The utility `validate_path` enforces canonicalization and disallows path traversal (`..`) attacks. It ensures all filesystem operations remain within designated roots [libs/deepagents/deepagents/backends/utils.py:80]().

- **Virtual Mode**: Filesystem backends can enforce virtual mode, which anchors file operations strictly to a root directory, rejecting any absolute or host-root paths [libs/deepagents/deepagents/backends/filesystem.py:155-172]().

- **Shell Command Patterns**: The AutoMode HITL middleware detects dangerous shell patterns to flag or require human approval for risky operations, such as credential assignment or unexpected flags [libs/code/deepagents_code/auto_mode.py:160-170]().

- **Secrets Detection**: Regex-based detections flag environment variables or shell variables resembling secrets, triggering maximum severity review.

### Security Boundary Diagram

```mermaid
graph LR
    subgraph "SecurityLayers"
        "validate_path"["validate_path<br/>(backends/utils.py)"]
        "_SHELL_CONTROL_RE"["_SHELL_CONTROL_RE Pattern<br/>(auto_mode.py)"]
        "virtual_mode"["virtual_mode (FilesystemMiddleware)<br/>(backends/filesystem.py)"]
    end

    "ToolCall" --> "validate_path"
    "validate_path" -- "Safe Path" --> "_SHELL_CONTROL_RE"
    "_SHELL_CONTROL_RE" -- "Allowed Shell Cmds" --> "virtual_mode"
    "virtual_mode" -- "Restricted Execution" --> "SandboxBackend"
```

For a thorough security discussion, see [Security and Path Validation](#4.7).

---

**Page Sources:**
* [libs/code/deepagents_code/auto_mode.py:1-184]()
* [libs/deepagents/deepagents/middleware/filesystem.py:1-94]()
* [libs/deepagents/deepagents/backends/protocol.py:40-60]()
* [libs/deepagents/deepagents/backends/sandbox.py:1-61]()
* [libs/deepagents/deepagents/backends/utils.py:70-90]()
* [libs/deepagents/deepagents/backends/filesystem.py:150-180]()

---

