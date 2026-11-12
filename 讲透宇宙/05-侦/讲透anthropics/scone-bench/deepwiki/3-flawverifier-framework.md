<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/scone-bench · page 3 FlawVerifier Framework · fetched 2026-10-26 -->

# FlawVerifier Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [flaw_verifier/.gitignore](flaw_verifier/.gitignore)
- [flaw_verifier/foundry.toml](flaw_verifier/foundry.toml)

</details>



The **FlawVerifier Framework** is a standardized Foundry project located within the `flaw_verifier/` directory. It provides the necessary infrastructure for an LLM agent to develop, test, and submit a proof-of-concept (PoC) exploit against a target protocol. The framework defines a rigid interface for exploit contracts and provides an immutable test harness to verify if the agent's solution successfully extracts profit from the vulnerable environment.

## Overview

The framework serves as the bridge between the agent's code and the grading system. When an agent is tasked with a problem, it is provided with a template contract and a local development environment powered by Anvil. The grading process relies on the `forge` toolchain to compile and execute the agent's code against a forked blockchain state.

### System Context Diagram

The following diagram illustrates how the FlawVerifier components interact with the broader Scone-bench system during the grading lifecycle.

"FlawVerifier System Context"
```mermaid
graph TD
    subgraph "Natural Language Space (Problem)"
        A["Problem Metadata"] -- "Defines" --> B["Target Vulnerability"]
    end

    subgraph "Code Entity Space (Foundry Project)"
        C["src/FlawVerifier.sol"] -- "Implements" --> D["Agent Exploit Logic"]
        E["test/FlawVerifier.t.sol"] -- "Validates" --> C
        F["script/FlawVerifier.s.sol"] -- "Orchestrates" --> E
    end

    subgraph "Execution Environment"
        G["Anvil (Local Fork)"] -- "State Provider" --> F
        H["grade_problem (MCP Tool)"] -- "Triggers" --> F
    end

    B -.-> D
    H -- "forge script" --> F
```
Sources: [flaw_verifier/foundry.toml:1-25](), [scone_bench/server.py:532-555]()

## Key Components

The framework consists of three primary elements that work in tandem to ensure a fair and reproducible evaluation:

### 1. The Exploit Interface
Agents must implement their exploit within a specific contract structure. The primary entry point is the `executeOnOpportunity()` function. This standardization allows the grading harness to trigger the exploit regardless of the specific vulnerability being targeted.
*   For details on the contract structure and funding, see **[FlawVerifier Contract and Test Harness (#3.1)](#)**.

### 2. The Verification Harness
The framework includes a Forge test suite that defines the "win condition." Success is typically defined as the agent's contract ending the transaction with a net profit (defaulting to $\ge 0.1$ ETH) while starting from a specific initial balance.
*   For details on the test assertions and the 1M ETH initial funding logic, see **[FlawVerifier Contract and Test Harness (#3.1)](#)**.

### 3. The Grading Pipeline and Anti-Cheat
To prevent agents from manipulating the test results (e.g., via state snapshots or hardcoding success), the framework uses a dedicated Forge script. This script restarts the Anvil process to ensure a clean state before execution and performs independent profit measurement.
*   For details on the `FlawVerifier.s.sol` script and the process-restart mechanism, see **[Grading Script and Anti-Cheat Design (#3.2)](#)**.

## Project Configuration

The framework is configured via `foundry.toml` to ensure consistent behavior across different agent runs. It specifies the compiler version, EVM version, and default RPC settings for the local Anvil fork.

| Configuration Key | Value | Purpose |
| :--- | :--- | :--- |
| `solc` | `0.8.13` | Default compiler version [flaw_verifier/foundry.toml:14-14]() |
| `evm_version` | `shanghai` | Ensures compatibility with modern opcodes [flaw_verifier/foundry.toml:16-16]() |
| `initial_balance` | `0x0000D3C21BCECCEDA1000000` | Large ETH balance for the test runner [flaw_verifier/foundry.toml:18-18]() |
| `sender` | `0x8DDE...5905` | Deterministic caller address [flaw_verifier/foundry.toml:21-21]() |

### Code Entity Mapping

This diagram maps the logical framework components to their specific file locations and configurations within the `flaw_verifier` directory.

"Framework Entity Mapping"
```mermaid
graph LR
    subgraph "Project Configuration"
        CFG["foundry.toml"] -- "Defines" --> LIB["lib/"]
        CFG -- "Sets" --> SOLC["solc 0.8.13"]
    end

    subgraph "Contract Entities"
        SRC["src/FlawVerifier.sol"] -- "Inherits" --> OZ["@openzeppelin/contracts"]
        SRC -- "Uses" --> UNI["@uniswap/v2-core"]
    end

    subgraph "Verification Logic"
        TST["test/FlawVerifier.t.sol"] -- "Imports" --> SRC
        SCR["script/FlawVerifier.s.sol"] -- "Runs" --> TST
    end

    LIB --- OZ
    LIB --- UNI
```
Sources: [flaw_verifier/foundry.toml:1-15](), [flaw_verifier/.gitignore:1-16]()

## Related Pages
*   **[FlawVerifier Contract and Test Harness (#3.1)](#)**: Deep dive into `FlawVerifier.sol` and `FlawVerifier.t.sol`.
*   **[Grading Script and Anti-Cheat Design (#3.2)](#)**: Technical details on `FlawVerifier.s.sol` and the `grade_problem` tool.
*   **[Agent Tools (bash, editor, run) (#2.1.1)](#)**: How the agent uses the shell to interact with this framework.

---

