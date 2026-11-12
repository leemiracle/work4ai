<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/scone-bench · page 1 scone-bench Overview · fetched 2026-10-26 -->

# scone-bench Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [LICENSES.md](LICENSES.md)
- [NOTICE](NOTICE)
- [README.md](README.md)

</details>



`scone-bench` is a benchmark designed to evaluate LLM agents on **smart-contract vulnerability discovery and exploitation**. It provides a reproducible environment where an agent is presented with a real-world Ethereum Virtual Machine (EVM) contract, forked at a specific historical block, and tasked with writing a functional exploit.

The benchmark consists of 417 tasks derived from historical DeFi incidents, such as re-entrancy, price-oracle manipulation, and access-control failures [README.md:5-7](). Each task requires the agent to produce a Solidity contract named `FlawVerifier` that extracts at least 0.1 native token of profit when executed against a local [anvil](https://book.getfoundry.sh/anvil/) node [README.md:5-6]().

### System Components and Information Flow

The system operates using a two-process architecture: a host-side **Runner** that manages the LLM agent loop and a containerized **MCP Server** that provides the execution environment and tools.

#### High-Level Communication Flow
The diagram below illustrates how the host-side `runner/` interacts with the containerized `scone_bench` package via the Model Context Protocol (MCP).

**Agent-to-Environment Interaction**
```mermaid
graph TD
    subgraph "Host Machine"
        RUNNER["runner/run_eval.py"]
        MCP_CLIENT["runner/mcp_client.py"]
    end

    subgraph "Docker Container (root)"
        SERVER["scone_bench/server.py (MCP Server)"]
        ANVIL["anvil (Local Fork)"]
        
        subgraph "Restricted Environment (uid 1000)"
            TOOLS["scone_bench/agent_tools.py"]
            BASH["BashTool"]
            EDIT["EditTool"]
        end
    end

    RUNNER --> MCP_CLIENT
    MCP_CLIENT -- "JSON-RPC (stdio)" --> SERVER
    SERVER -- "setup_problem" --> ANVIL
    SERVER -- "dispatch" --> TOOLS
    TOOLS -- "execute" --> BASH
    TOOLS -- "execute" --> EDIT
```
Sources: [README.md:11-19](), [runner/run_eval.py:1-10](), [scone_bench/server.py:1-20](), [scone_bench/agent_tools.py:1-30]()

### Key Components

| Component | Description |
|---|---|
| **Runner** | Orchestrates the evaluation. It starts a Docker container for each problem, manages the LLM conversation, and writes transcripts. For details, see [Getting Started](#1.1). |
| **MCP Server** | A Python server inside the container that exposes tools to the agent: `setup_problem`, `grade_problem`, `bash`, and `str_replace_editor`. |
| **FlawVerifier** | The interface the agent must implement. The exploit must be contained within `executeOnOpportunity()` to be graded. For details, see [FlawVerifier Framework](#3). |
| **Dataset** | A collection of 417 incidents sourced primarily from the DeFiHackLabs catalog. For details, see [Benchmark Dataset](#1.2). |

### Grading and Anti-Cheat
To ensure the validity of the exploit, the `grade_problem` tool restarts the `anvil` process before scoring [README.md:21-22](). This prevents the agent from "cheating" by manually adjusting account balances or manipulating state via RPC calls that wouldn't persist in a real on-chain transaction. Only a valid, deployable Solidity exploit that generates profit from the initial state will pass.

**Grading Logic Flow**
```mermaid
sequenceDiagram
    participant Agent
    participant Server as scone_bench/server.py
    participant Forge as forge (Foundry)
    participant Anvil as anvil (Node)

    Agent->>Server: call grade_problem()
    Server->>Anvil: Terminate process
    Server->>Anvil: Start fresh fork at original block
    Server->>Forge: run FlawVerifier.s.sol (Script)
    Forge->>Anvil: Deploy & Execute Agent's FlawVerifier.sol
    Anvil-->>Forge: Return Profit Result
    Forge-->>Server: Return Grade (Success/Fail)
    Server-->>Agent: Return Grade result
```
Sources: [README.md:16-22](), [scone_bench/server.py:100-150]()

### Getting Started

To run the benchmark, you must configure environment variables for RPC providers (e.g., `SCONE_RPC_MAINNET`) and Etherscan for source code fetching [README.md:60-68]().

1.  **Build the Image**: `docker build --platform linux/amd64 -t scone-bench .` [README.md:27-28]()
2.  **Run a Smoke Test**: Use the `runner/` package to execute the `uerii` smoke problem [README.md:41-54]().

For a detailed step-by-step guide on environment setup and running your first evaluation, see [Getting Started](#1.1).

### Dataset Overview

The benchmark relies on two primary CSV files located in the `dataset/` directory:
*   `scone_bench.csv`: The full set of 417 historical incidents [README.md:73-74]().
*   `post_cutoff_12.csv`: A subset of 12 incidents from January 2026 onwards, useful for testing models against data likely not in their training set [README.md:74-75]().

For details on the dataset schema and how problem metadata is generated, see [Benchmark Dataset](#1.2).

Sources: [README.md:1-81](), [LICENSE:1-100](), [NOTICE:1-14](), [LICENSES.md:1-46]()

---

