<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/agent-baselines · page 4 Agent Architecture · fetched 2026-10-26 -->

# Agent Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [solvers/smolagents/README.md](solvers/smolagents/README.md)
- [solvers/sqa/demo.sh](solvers/sqa/demo.sh)

</details>



This document provides an overview of the agent ecosystem in agent-baselines, focusing on the architectural patterns, interfaces, and organizational structure that enables a diverse collection of AI agents to work within a unified evaluation framework. The architecture is built on top of InspectAI's solver interface and supports modular agent implementations with specialized capabilities.

For detailed information about specific agent implementations, see [Basic Agents](#4.1), [SQA Solvers](#4.2), [Asta Router System](#4.3), and [Specialized Agents](#4.4). For setup and installation details, see [Installation and Dependencies](#2.1).

## InspectAI Solver Interface

The agent-baselines framework is built on top of InspectAI's standardized solver interface, which provides a consistent execution model for all agents regardless of their internal implementation. This architecture enables uniform evaluation, logging, and orchestration across diverse agent types.

**InspectAI Solver Interface Architecture**

```mermaid
graph TD
    subgraph "InspectAI Framework"
        CLI["inspect eval command"]
        SOLVER_INTERFACE["Solver Interface"]
        TASK_STATE["TaskState"]
        TOOLS["Tool Management"]
        SANDBOX["Sandbox Environment"]
    end
    
    subgraph "Agent Implementation Layer"
        SOLVER_FUNC["@solver decorated function"]
        AGENT_LOGIC["Agent Logic"]
        LLM_CLIENT["LLM Client"]
        TOOL_CALLS["Tool Invocations"]
    end
    
    subgraph "External Systems"
        LLM_APIS["LLM APIs (OpenAI, Anthropic)"]
        MODAL_PLATFORM["Modal Platform"]
        SEMANTIC_SCHOLAR["Semantic Scholar API"]
    end
    
    CLI --> SOLVER_INTERFACE
    SOLVER_INTERFACE --> TASK_STATE
    TASK_STATE --> TOOLS
    TOOLS --> SANDBOX
    
    SOLVER_INTERFACE --> SOLVER_FUNC
    SOLVER_FUNC --> AGENT_LOGIC
    AGENT_LOGIC --> LLM_CLIENT
    AGENT_LOGIC --> TOOL_CALLS
    
    LLM_CLIENT --> LLM_APIS
    TOOL_CALLS --> MODAL_PLATFORM
    TOOL_CALLS --> SEMANTIC_SCHOLAR
```

All agents in the repository implement the InspectAI solver pattern, which requires a function decorated with `@solver` that accepts a `TaskState` and returns a `TaskState`. This standardization enables consistent evaluation across all agent types using the `inspect eval` command.

**Sources:** [pyproject.toml:57](), [README.md:5](), [solvers/sqa/demo.sh:18-23]()

## Agent Categories and Specialization

The agent-baselines repository organizes agents into distinct categories based on their capabilities and target domains. This categorical structure reflects the modular dependency system and enables targeted deployment for specific task types.

**Agent Category Hierarchy**

```mermaid
graph TB
    subgraph "General Purpose Agents"
        REACT["react solver"]
        SMOL["smolagents solver"]
    end
    
    subgraph "Scientific Task Specialists"
        SQA["sqa_solver"]
        DATAVOYAGER["datavoyager solver"]
        PAPER_FINDER["paper_finder solver"]
        ARXIV_TABLES["arxivdigestables solver"]
        SUPER_AGENT["super solver"]
        E2E_DISCOVERY["e2e_discovery solver"]
    end
    
    subgraph "Task Router System"
        ASTA_V0["asta-v0 solver"]
        ROUTER["fewshot_textsim_router"]
    end
    
    subgraph "External Integration Agents"
        STORM["storm solver"]
        FUTUREHOUSE["futurehouse solver"]
        ELICIT["elicit_memorized solver"]
    end
    
    subgraph "Task Categories"
        SQA_TASKS["sqa_dev, sqa_test"]
        DISC_TASKS["discoverybench"]
        PAPER_TASKS["paperfinder"]
        TABLE_TASKS["arxivdigestables"]
        SUPER_TASKS["super repository tasks"]
        E2E_TASKS["e2e_discovery"]
    end
    
    ASTA_V0 --> ROUTER
    ROUTER -.-> SQA
    ROUTER -.-> DATAVOYAGER
    ROUTER -.-> PAPER_FINDER
    ROUTER -.-> ARXIV_TABLES
    ROUTER -.-> SUPER_AGENT
    ROUTER -.-> E2E_DISCOVERY
    
    SQA_TASKS --> SQA
    SQA_TASKS --> STORM
    SQA_TASKS --> FUTUREHOUSE
    DISC_TASKS --> DATAVOYAGER
    PAPER_TASKS --> PAPER_FINDER
    TABLE_TASKS --> ARXIV_TABLES
    SUPER_TASKS --> SUPER_AGENT
    E2E_TASKS --> E2E_DISCOVERY
```

### General Purpose Agents

General purpose agents provide foundational capabilities that work across multiple task types without domain-specific optimizations. These agents implement core patterns like ReAct loops and code-based tool execution.

| Agent | Implementation | Key Features |
|-------|---------------|--------------|
| `react` | Basic ReAct loop | LLM tool-calling, configurable max_steps |
| `smolagents` | HuggingFace CodeAgent | Python code execution, sandbox required |

### Scientific Task Specialists

Scientific task specialists are optimized for specific domains within scientific research and discovery. Each specialist includes domain-specific prompts, tools, and workflows tailored to their target tasks.

| Agent | Target Tasks | Specialization |
|-------|-------------|----------------|
| `sqa_solver` | SQA tasks | Literature Q&A with retrieval |
| `datavoyager` | DiscoveryBench | Data analysis and exploration |
| `paper_finder` | PaperFinder | Paper search and recommendation |
| `arxivdigestables` | Table generation | Literature review tables |
| `super` | Repository reproduction | Code analysis and execution |
| `e2e_discovery` | End-to-end discovery | Multi-step research workflows |

**Sources:** [README.md:26-48](), [pyproject.toml:29-54]()

## Modular Dependency System

The architecture employs a modular dependency system that allows selective installation of agent capabilities based on deployment requirements. This system prevents dependency conflicts while enabling rich functionality for specific agent types.

**Dependency Management Architecture**

```mermaid
graph TD
    subgraph "Core Dependencies"
        ASTABENCH["astabench==0.1.5"]
        PYTHON["Python >=3.11"]
    end
    
    subgraph "Optional Dependency Groups"
        DEV["dev extras"]
        SQA["sqa extras"]
        SMOL["smolagents extras"]
        DATA["datavoyager extras"]
        STORM["storm extras"]
        FUTURE["futurehouse_solver extras"]
        SUPER["super extras"]
        AZURE["azure extras"]
    end
    
    subgraph "Agent Implementations"
        SQA_SOLVER["agent_baselines/solvers/sqa/"]
        SMOL_SOLVER["agent_baselines/solvers/smolagents/"]
        DATA_SOLVER["agent_baselines/solvers/datavoyager/"]
        STORM_SOLVER["agent_baselines/solvers/storm/"]
        FUTURE_SOLVER["agent_baselines/solvers/futurehouse/"]
        SUPER_SOLVER["agent_baselines/solvers/super/"]
    end
    
    subgraph "Conflict Management"
        UV_CONFLICTS["uv.conflicts"]
        OVERRIDES["override-dependencies"]
    end
    
    ASTABENCH --> SQA_SOLVER
    ASTABENCH --> SMOL_SOLVER
    ASTABENCH --> DATA_SOLVER
    
    SQA --> SQA_SOLVER
    SMOL --> SMOL_SOLVER
    DATA --> DATA_SOLVER
    STORM --> STORM_SOLVER
    FUTURE --> FUTURE_SOLVER
    SUPER --> SUPER_SOLVER
    
    UV_CONFLICTS --> SQA
    UV_CONFLICTS --> STORM
    UV_CONFLICTS --> FUTURE
    OVERRIDES --> SQA
    OVERRIDES --> STORM
```

### Dependency Conflicts and Resolution

The system manages several dependency conflicts through explicit conflict declarations and override mechanisms:

| Conflict Type | Affected Extras | Resolution |
|---------------|----------------|------------|
| OpenAI version conflicts | `sqa`, `storm`, `futurehouse_solver` | Override to `openai==1.78.0` |
| Datasets version conflicts | `storm` | Override to `datasets~=3.2.0` |
| Mutual exclusions | `sqa` ↔ `storm`, `sqa` ↔ `futurehouse_solver` | Declared conflicts |

**Sources:** [pyproject.toml:66-80](), [pyproject.toml:14-54]()

## Solver Discovery and Registration

The framework uses InspectAI's solver discovery mechanism to locate and register agent implementations. Solvers are organized in the `agent_baselines/solvers/` directory structure and can be invoked using module paths.

**Solver Registration Pattern**

```mermaid
graph LR
    subgraph "Solver Structure"
        SOLVER_DIR["agent_baselines/solvers/{solver_name}/"]
        SOLVER_MODULE["{solver_name}.py"]
        SOLVER_FUNCTION["@solver decorated function"]
        SETUP_SCRIPT["setup.sh"]
        DEMO_SCRIPT["demo.sh"]
    end
    
    subgraph "InspectAI Discovery"
        MODULE_PATH["agent_baselines/solvers/{solver}/file.py@function"]
        REGISTRY["InspectAI Solver Registry"]
        EVAL_COMMAND["inspect eval --solver"]
    end
    
    subgraph "Environment Setup"
        UV_INSTALL["uv pip install -e .[extras]"]
        ENV_VARS["Environment Variables"]
        SANDBOX_CONFIG["Sandbox Configuration"]
    end
    
    SOLVER_DIR --> SOLVER_MODULE
    SOLVER_MODULE --> SOLVER_FUNCTION
    SOLVER_DIR --> SETUP_SCRIPT
    SOLVER_DIR --> DEMO_SCRIPT
    
    SOLVER_FUNCTION --> MODULE_PATH
    MODULE_PATH --> REGISTRY
    REGISTRY --> EVAL_COMMAND
    
    SETUP_SCRIPT --> UV_INSTALL
    SETUP_SCRIPT --> ENV_VARS
    DEMO_SCRIPT --> SANDBOX_CONFIG
```

### Solver Invocation Patterns

Solvers are invoked using the module path syntax that InspectAI recognizes:

```
agent_baselines/solvers/{solver_name}/{module}.py@{function_name}
```

For example, the SQA solver is invoked as:
```
agent_baselines/solvers/sqa/sqa.py@sqa_solver
```

Each solver directory includes standardized scripts:
- `setup.sh`: Environment setup and dependency installation
- `demo.sh`: Example invocation with limited samples
- `README.md`: Solver-specific documentation

**Sources:** [solvers/sqa/demo.sh:18-19](), [README.md:13-21](), [pyproject.toml:59-64]()

## Environment and Execution Contexts

The architecture supports multiple execution contexts to accommodate different agent requirements, from simple local execution to complex sandboxed environments with external service integration.

**Execution Context Architecture**

```mermaid
graph TD
    subgraph "Local Development"
        LOCAL_PYTHON["Python Environment"]
        LOCAL_DEPS["Local Dependencies"]
        LOCAL_TOOLS["Direct Tool Access"]
    end
    
    subgraph "Docker Environment"
        DOCKER_BASE["agent-baselines-base image"]
        DOCKER_SOLVER["solver-specific images"]
        CONTAINER_ENV["Containerized Environment"]
    end
    
    subgraph "Sandbox Environment"
        SANDBOX_COMPOSE["sandbox_compose.yaml"]
        ISOLATED_EXEC["Isolated Code Execution"]
        SANDBOX_TOOLS["SandboxToolManager"]
    end
    
    subgraph "External Services"
        MODAL_TOKEN["MODAL_TOKEN"]
        S2_API_KEY["S2_API_KEY"]
        LLM_KEYS["OPENAI_API_KEY, ANTHROPIC_API_KEY"]
        MABOOL_URL["MABOOL_URL"]
    end
    
    LOCAL_PYTHON --> DOCKER_BASE
    DOCKER_BASE --> DOCKER_SOLVER
    DOCKER_SOLVER --> CONTAINER_ENV
    CONTAINER_ENV --> SANDBOX_COMPOSE
    SANDBOX_COMPOSE --> ISOLATED_EXEC
    ISOLATED_EXEC --> SANDBOX_TOOLS
    
    LOCAL_TOOLS --> MODAL_TOKEN
    SANDBOX_TOOLS --> S2_API_KEY
    CONTAINER_ENV --> LLM_KEYS
    DOCKER_SOLVER --> MABOOL_URL
```

The smolagents solver specifically requires sandbox execution due to its code-based action mechanism, while other agents can run in simpler environments depending on their tool requirements.

**Sources:** [solvers/smolagents/README.md:9-11](), [solvers/sqa/demo.sh:6-16](), [README.md:16-21]()

---

