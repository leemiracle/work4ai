<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-core-java · page 8 System Operations (SysOp) · fetched 2026-11-02 -->

# System Operations (SysOp)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/main/java/com/openjiuwen/core/sysop/BaseCodeOperation.java](src/main/java/com/openjiuwen/core/sysop/BaseCodeOperation.java)
- [src/main/java/com/openjiuwen/core/sysop/BaseFsOperation.java](src/main/java/com/openjiuwen/core/sysop/BaseFsOperation.java)
- [src/main/java/com/openjiuwen/core/sysop/BaseOperation.java](src/main/java/com/openjiuwen/core/sysop/BaseOperation.java)
- [src/main/java/com/openjiuwen/core/sysop/BaseShellOperation.java](src/main/java/com/openjiuwen/core/sysop/BaseShellOperation.java)
- [src/main/java/com/openjiuwen/core/sysop/FsConstants.java](src/main/java/com/openjiuwen/core/sysop/FsConstants.java)
- [src/main/java/com/openjiuwen/core/sysop/OperationMode.java](src/main/java/com/openjiuwen/core/sysop/OperationMode.java)
- [src/main/java/com/openjiuwen/core/sysop/SysOperation.java](src/main/java/com/openjiuwen/core/sysop/SysOperation.java)
- [src/main/java/com/openjiuwen/core/sysop/SysOperationCard.java](src/main/java/com/openjiuwen/core/sysop/SysOperationCard.java)
- [src/main/java/com/openjiuwen/core/sysop/SysOperationToolAdapter.java](src/main/java/com/openjiuwen/core/sysop/SysOperationToolAdapter.java)
- [src/main/java/com/openjiuwen/core/sysop/ToolIdProxy.java](src/main/java/com/openjiuwen/core/sysop/ToolIdProxy.java)
- [src/main/java/com/openjiuwen/core/sysop/config/LocalWorkConfig.java](src/main/java/com/openjiuwen/core/sysop/config/LocalWorkConfig.java)
- [src/test/java/com/openjiuwen/core/sysop/local/LocalCodeOperationTest.java](src/test/java/com/openjiuwen/core/sysop/local/LocalCodeOperationTest.java)
- [src/test/java/com/openjiuwen/core/sysop/local/LocalShellOperationTest.java](src/test/java/com/openjiuwen/core/sysop/local/LocalShellOperationTest.java)

</details>



The System Operations (SysOp) subsystem provides a standardized interface for agents to interact with the underlying operating system. This includes executing shell commands, running arbitrary code (Python/JavaScript), and performing filesystem operations. The subsystem is designed to be environment-agnostic, supporting both direct local execution and isolated sandbox environments.

## Architecture Overview

The SysOp subsystem follows a provider-based architecture where operations are defined by their capabilities (Shell, Code, FS) and implemented based on the `OperationMode` [src/main/java/com/openjiuwen/core/sysop/OperationMode.java:16-18]().

### Core Components

| Component | Description |
| :--- | :--- |
| `SysOperation` | The primary facade for accessing system operations. It manages the lifecycle of specific operation instances (fs, code, shell) [src/main/java/com/openjiuwen/core/sysop/SysOperation.java:23-29](). |
| `SysOperationCard` | A configuration object that defines the `OperationMode`, identity, and specific environment settings (like `LocalWorkConfig`) for the operations [src/main/java/com/openjiuwen/core/sysop/SysOperationCard.java:16-27](). |
| `BaseOperation` | The abstract base class for all system operations, providing common metadata and tool generation logic [src/main/java/com/openjiuwen/core/sysop/BaseOperation.java:16-24](). |
| `SysOperationToolAdapter` | A utility that converts `SysOperation` methods into `LocalFunction` tools, allowing LLM agents to call system operations as standard tools [src/main/java/com/openjiuwen/core/sysop/SysOperationToolAdapter.java:29-54](). |

**Sources:**
- [src/main/java/com/openjiuwen/core/sysop/SysOperation.java:23-93]()
- [src/main/java/com/openjiuwen/core/sysop/SysOperationCard.java:16-119]()
- [src/main/java/com/openjiuwen/core/sysop/OperationMode.java:16-61]()
- [src/main/java/com/openjiuwen/core/sysop/SysOperationToolAdapter.java:29-86]()

---

## Operation Categories

System operations are grouped into three functional categories, each represented by a specialized base class:

### 1. Shell Operations
Provides methods for command execution, including synchronous execution, background processes, and streaming output for long-running tasks [src/main/java/com/openjiuwen/core/sysop/BaseShellOperation.java:23-89]().
*   **Key Methods:** `executeCmd`, `executeCmdStream`, `executeCmdBackground`.
*   **Details:** See [Local Shell and Code Execution](#8.1).

### 2. Code Execution
Allows for the execution of arbitrary scripts. It currently supports Python and JavaScript (via Node.js) [src/test/java/com/openjiuwen/core/sysop/local/LocalCodeOperationTest.java:83-117]().
*   **Key Methods:** `executeCode`, `executeCodeStream` [src/main/java/com/openjiuwen/core/sysop/BaseCodeOperation.java:31-42]().
*   **Details:** See [Local Shell and Code Execution](#8.1).

### 3. Filesystem Operations
Handles file and directory management, including reading, writing, and path manipulation [src/main/java/com/openjiuwen/core/sysop/SysOperation.java:58-60]().
*   **Constants:** Defines default chunk sizes for streaming operations (e.g., `DEFAULT_READ_STREAM_CHUNK_SIZE` = 8192) [src/main/java/com/openjiuwen/core/sysop/FsConstants.java:12-26]().
*   **Details:** See [Local Shell and Code Execution](#8.1).

---

## Execution Modes

The framework supports two primary modes of operation, configured via the `SysOperationCard`.

### Local Execution
In `LOCAL` mode, commands and code are executed directly on the host machine running the agent. Security is managed through `LocalWorkConfig`, which includes:
*   **Shell Allowlist:** A list of permitted commands (e.g., `ls`, `grep`, `python`) [src/main/java/com/openjiuwen/core/sysop/config/LocalWorkConfig.java:25-31]().
*   **Sandbox Root:** Restricting file operations to specific directories [src/main/java/com/openjiuwen/core/sysop/config/LocalWorkConfig.java:34-42]().

For implementation details, see [Local Shell and Code Execution](#8.1).

### Sandbox Execution
In `SANDBOX` mode, operations are offloaded to an isolated environment (e.g., JiuwenBox). This is the recommended mode for production environments to prevent unauthorized system access or resource exhaustion by the agent.

For configuration and gateway details, see [Sandbox Execution (JiuwenBox)](#8.2).

---

## Technical Mapping: Logic to Code

### SysOp Entity Relationship
The following diagram illustrates how high-level system operation requests are mapped to specific code entities and execution implementations.

```mermaid
graph TD
    "Agent/User" -- "Tool Call" --> "SysOperationToolAdapter"
    "SysOperationToolAdapter" -- "Extracts" --> "SysOperation"
    "SysOperation" -- "configures" --> "SysOperationCard"
    "SysOperationCard" -- "defines" --> "OperationMode"
    
    subgraph "Code Entity Space"
        "SysOperation" -- "delegates to" --> "BaseOperation"
        "BaseOperation" <|-- "BaseShellOperation"
        "BaseOperation" <|-- "BaseCodeOperation"
        "BaseOperation" <|-- "BaseFsOperation"
        
        "BaseShellOperation" -- "implements" --> "LocalShellOperation"
        "BaseCodeOperation" -- "implements" --> "LocalCodeOperation"
        "BaseFsOperation" -- "implements" --> "LocalFsOperation"
    end
```

**Sources:**
- [src/main/java/com/openjiuwen/core/sysop/SysOperation.java:58-92]()
- [src/main/java/com/openjiuwen/core/sysop/SysOperationToolAdapter.java:54-86]()
- [src/main/java/com/openjiuwen/core/sysop/BaseShellOperation.java:23-35]()

### Command Execution Flow
This diagram shows the path from a natural language "execute command" intent to the physical execution via `LocalShellOperation`.

```mermaid
graph LR
    subgraph "Natural Language Space"
        "NL_Intent[Run 'ls -la']"
    end

    subgraph "Code Entity Space"
        "NL_Intent" --> "ToolCall[executeCmd]"
        "ToolCall" --> "LocalShellOperation::executeCmd"
        "LocalShellOperation::executeCmd" --> "ProcessBuilder"
        "ProcessBuilder" --> "Stdout/Stderr[ExecuteCmdResult]"
    end
```

**Sources:**
- [src/main/java/com/openjiuwen/core/sysop/BaseShellOperation.java:59-60]()
- [src/test/java/com/openjiuwen/core/sysop/local/LocalShellOperationTest.java:99-107]()

---

