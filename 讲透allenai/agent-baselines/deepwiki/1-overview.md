<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/agent-baselines · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



## Purpose and Scope

The agent-baselines repository provides baseline implementations of AI agents designed for evaluation against the AstaBench benchmarking suite. This framework serves as a comprehensive testbed for comparing different agent architectures, from general-purpose ReAct agents to specialized scientific task solvers. The repository implements agents as InspectAI solvers, enabling standardized evaluation across multiple tasks and models.

This document covers the high-level architecture and core systems within agent-baselines. For detailed installation instructions, see [Installation and Dependencies](#2.1). For information about running evaluations, see [Evaluation Pipeline](#3). For specific agent implementations, see [Agent Architecture](#4).

## High-Level System Architecture

The agent-baselines framework is built around a modular architecture that separates agent implementations, evaluation infrastructure, and dependency management:

```mermaid
graph TB
    subgraph "Project Configuration"
        pyproject["pyproject.toml<br/>Central configuration"]
        setuptools["setuptools.build_meta<br/>Build backend"]
    end
    
    subgraph "Dependency Management"
        core_deps["astabench==0.1.5<br/>Core dependency"]
        dev_deps["dev extras<br/>pytest, mypy, black"]
        sqa_deps["sqa extras<br/>ai2-scholar-qa==0.7.0"]
        smol_deps["smolagents extras<br/>smolagents==1.17.0"]
        data_deps["datavoyager extras<br/>autogen-agentchat==0.6.4"]
        storm_deps["storm extras<br/>knowledge-storm"]
        future_deps["futurehouse_solver extras<br/>futurehouse-client==0.3.19"]
        super_deps["super extras<br/>websocket-client, nbconvert"]
    end
    
    subgraph "Agent Implementation Layer"
        inspect_cli["inspect CLI<br/>inspect_ai._cli.main:main"]
        solver_interface["InspectAI Solver Interface<br/>Standardized execution"]
    end
    
    subgraph "Evaluation Infrastructure"
        dvc_pipeline["dvc.yaml<br/>Pipeline orchestration"]
        docker_system["Dockerfile system<br/>Containerized execution"]
        makefile["Makefile<br/>Developer interface"]
    end
    
    pyproject --> core_deps
    pyproject --> dev_deps
    pyproject --> sqa_deps
    pyproject --> smol_deps
    pyproject --> data_deps
    pyproject --> storm_deps
    pyproject --> future_deps
    pyproject --> super_deps
    
    pyproject --> inspect_cli
    inspect_cli --> solver_interface
    
    core_deps --> solver_interface
    sqa_deps --> solver_interface
    smol_deps --> solver_interface
    
    solver_interface --> dvc_pipeline
    docker_system --> solver_interface
    makefile --> docker_system
```

Sources: [pyproject.toml:1-112](), [README.md:1-116]()

## Agent Solver Ecosystem

The repository implements multiple specialized agents as InspectAI solvers, organized by task domain and capability:

```mermaid
graph TD
    subgraph "InspectAI Integration"
        inspect_eval["inspect eval command<br/>Entry point execution"]
        astabench_core["astabench==0.1.5<br/>Benchmark framework"]
    end
    
    subgraph "General Purpose Solvers"
        react_solver["react solver<br/>/solvers/react/"]
        smolagents_solver["smolagents solver<br/>/solvers/smolagents/"]
    end
    
    subgraph "Scientific Task Solvers"
        sqa_solver["sqa solver<br/>/solvers/sqa/<br/>ai2-scholar-qa dependency"]
        datavoyager_solver["datavoyager solver<br/>/solvers/datavoyager/<br/>autogen-agentchat dependency"]
        paper_finder_solver["paper_finder solver<br/>/solvers/paper_finder/"]
        tables_solver["arxivdigestables solver<br/>/solvers/arxivdigestables/"]
        super_solver["super solver<br/>/solvers/super/<br/>websocket-client dependency"]
        e2e_solver["e2e_discovery solver<br/>/solvers/e2e_discovery/"]
    end
    
    subgraph "Routing System"
        asta_v0_solver["asta-v0 solver<br/>/solvers/asta-v0/<br/>Task routing logic"]
    end
    
    subgraph "External Integration Solvers"
        storm_solver["storm solver<br/>/solvers/storm/<br/>knowledge-storm dependency"]
        futurehouse_solver["futurehouse solver<br/>/solvers/futurehouse/<br/>futurehouse-client dependency"]
    end
    
    inspect_eval --> astabench_core
    astabench_core --> react_solver
    astabench_core --> smolagents_solver
    astabench_core --> sqa_solver
    astabench_core --> datavoyager_solver
    astabench_core --> paper_finder_solver
    astabench_core --> tables_solver
    astabench_core --> super_solver
    astabench_core --> e2e_solver
    astabench_core --> asta_v0_solver
    astabench_core --> storm_solver
    astabench_core --> futurehouse_solver
    
    asta_v0_solver -.-> sqa_solver
    asta_v0_solver -.-> datavoyager_solver
    asta_v0_solver -.-> paper_finder_solver
    asta_v0_solver -.-> tables_solver
    asta_v0_solver -.-> super_solver
    asta_v0_solver -.-> e2e_solver
```

Sources: [pyproject.toml:29-54](), [README.md:26-49]()

## Key Components

### Project Configuration

The project uses a centralized configuration approach through `pyproject.toml`, which defines the build system, dependencies, and tooling configuration:

| Component | Purpose | Configuration Location |
|-----------|---------|------------------------|
| Build System | Package building with setuptools | [pyproject.toml:1-3]() |
| Core Dependencies | AstaBench integration | [pyproject.toml:10-12]() |
| Optional Dependencies | Modular solver requirements | [pyproject.toml:14-54]() |
| Package Discovery | Agent baselines module inclusion | [pyproject.toml:59-64]() |
| Tool Configuration | Development and quality tools | [pyproject.toml:81-111]() |

### Dependency Conflicts and Resolution

The project manages complex dependency conflicts between different solver implementations using UV's conflict resolution system:

```mermaid
graph LR
    subgraph "Conflict Groups"
        sqa_group["sqa extra<br/>ai2-scholar-qa==0.7.0"]
        storm_group["storm extra<br/>knowledge-storm"]
        futurehouse_group["futurehouse_solver extra<br/>futurehouse-client==0.3.19"]
        smolagents_group["smolagents extra<br/>smolagents==1.17.0"]
    end
    
    subgraph "UV Conflict Resolution"
        conflict_1["Conflict: sqa ↔ storm<br/>pyproject.toml:68"]
        conflict_2["Conflict: sqa ↔ futurehouse_solver<br/>pyproject.toml:69"]
        conflict_3["Conflict: storm ↔ smolagents<br/>pyproject.toml:70"]
    end
    
    subgraph "Override Dependencies"
        openai_override["openai==1.78.0<br/>Override for sqa compatibility"]
        datasets_override["datasets~=3.2.0<br/>Override for STORM compatibility"]
    end
    
    sqa_group --> conflict_1
    storm_group --> conflict_1
    sqa_group --> conflict_2
    futurehouse_group --> conflict_2
    storm_group --> conflict_3
    smolagents_group --> conflict_3
    
    conflict_1 --> openai_override
    conflict_1 --> datasets_override
    conflict_2 --> openai_override
    conflict_3 --> datasets_override
```

Sources: [pyproject.toml:66-79]()

### Development and Quality Infrastructure

The project includes comprehensive development tooling integrated through the configuration system:

| Tool Category | Tools | Purpose |
|---------------|-------|---------|
| Code Formatting | `black==24.2.0`, `isort`, `autoflake` | Consistent code style |
| Testing | `pytest`, `pytest-asyncio` | Test execution and async support |
| Type Checking | `mypy==1.15`, `pandas-stubs` | Static type analysis |
| Linting | `flake8==7.2.0`, `flake8-pyproject` | Code quality checks |

The testing configuration supports both synchronous and asynchronous tests with strict loop isolation and optional expensive test markers.

Sources: [pyproject.toml:15-25](), [pyproject.toml:102-111]()

## Project Structure

The repository is organized around solver implementations with supporting infrastructure:

```
agent_baselines/
├── solvers/                    # Individual agent implementations
│   ├── react/                 # Basic ReAct agent
│   ├── smolagents/            # HuggingFace CodeAgent integration  
│   ├── sqa/                   # ScholarQA system
│   ├── datavoyager/           # Data analysis agent
│   ├── paper_finder/          # Paper search agent
│   ├── arxivdigestables/      # Literature table generator
│   ├── super/                 # Repository reproduction agent
│   ├── e2e_discovery/         # End-to-end discovery agent
│   ├── asta-v0/               # Task routing system
│   ├── storm/                 # Knowledge curation system
│   └── futurehouse/           # Literature review agent
├── dvc.yaml                   # DVC pipeline configuration
├── pyproject.toml             # Project configuration and dependencies
└── Makefile                   # Developer interface commands
```

Each solver directory contains standardized `setup.sh` and `demo.sh` scripts for installation and demonstration, providing a consistent interface across different agent implementations.

Sources: [README.md:13-14](), [README.md:49](), [pyproject.toml:59-64]()

---

