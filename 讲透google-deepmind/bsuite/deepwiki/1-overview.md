<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/bsuite · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [README.md](README.md)
- [bsuite/_metadata.py](bsuite/_metadata.py)
- [setup.py](setup.py)

</details>



This document introduces the bsuite (Behaviour Suite) repository, explaining its purpose as a comprehensive evaluation framework for reinforcement learning agents, its core architectural components, and how they work together to enable systematic RL research. For detailed information about specific components, see [Package Structure and Installation](#1.1), [Core Framework](#2), [Environments](#3), [Agent Implementations](#4), [Experiment Management](#5), and [Data and Analysis](#6).

## Purpose and Scope

bsuite is a collection of carefully-designed diagnostic environments and evaluation tools for reinforcement learning research. The system serves two primary objectives: (1) providing clear, informative problems that capture key issues in RL algorithm design, and (2) enabling systematic study of agent behavior through standardized benchmarks with automated evaluation and analysis.

The framework automates the entire research pipeline from experiment definition through execution to comprehensive analysis, supporting multiple machine learning frameworks and providing reproducible evaluation protocols for RL algorithms.

Sources: [README.md:11-21](), [setup.py:62-63]()

## System Architecture

The bsuite system consists of five major subsystems that work together to provide end-to-end evaluation capabilities:

### High-Level System Components

```mermaid
graph TB
    subgraph "Package Infrastructure"
        setup_py["setup.py<br/>Package Definition"]
        metadata["_metadata.py<br/>Version: 0.3.5"]
        ci["ci.yml<br/>Testing Pipeline"]
    end
    
    subgraph "Core Framework"
        base_agent["base.Agent<br/>select_action(), update()"]
        experiment["experiment.run<br/>Agent-Environment Loop"]
        sweep_system["sweep.SWEEP<br/>Parameter Management"]
        bsuite_load["bsuite.load_from_id<br/>Environment Factory"]
    end
    
    subgraph "Diagnostic Environments"
        env_experiments["experiments/<br/>bandit, deep_sea, cartpole"]
        env_base["base.Environment<br/>dm_env interface"]
        wrappers["Environment Wrappers<br/>Logging integration"]
    end
    
    subgraph "Agent Implementations"
        jax_baselines["baselines/jax/<br/>BootDQN, DQN, ActorCritic"]
        tf_baselines["baselines/tf/<br/>TensorFlow agents"]
        third_party["baselines/third_party/<br/>OpenAI, Dopamine"]
    end
    
    subgraph "Analysis Pipeline"
        logging_system["logging/<br/>CSV, SQLite, Terminal"]
        analysis_tools["analysis/<br/>results.ipynb, plotting"]
        reports["reports/<br/>Automated summaries"]
    end
    
    setup_py --> jax_baselines
    setup_py --> tf_baselines
    setup_py --> third_party
    
    base_agent --> jax_baselines
    base_agent --> tf_baselines
    base_agent --> third_party
    
    bsuite_load --> env_experiments
    env_experiments --> wrappers
    wrappers --> logging_system
    
    experiment --> logging_system
    sweep_system --> experiment
    
    logging_system --> analysis_tools
    analysis_tools --> reports
```

Sources: [setup.py:1-104](), [README.md:31-48](), [bsuite/_metadata.py:22]()

## Core Framework Integration

The system integrates multiple frameworks through a unified interface while maintaining framework-specific optimizations:

### Framework Support Structure

```mermaid
graph LR
    subgraph "Base Interface"
        base_agent_class["base.Agent<br/>Abstract interface"]
        dm_env["dm_env<br/>Environment protocol"]
    end
    
    subgraph "JAX Ecosystem"
        jax_deps["dm-haiku, jax, optax, rlax"]
        jax_agents["JAX Agents<br/>baselines/jax/"]
    end
    
    subgraph "TensorFlow Ecosystem"
        tf_deps["dm-sonnet, tensorflow, trfl"]
        tf_agents["TF Agents<br/>baselines/tf/"]
    end
    
    subgraph "Third-party Integration"
        third_deps["dopamine-rl, baselines"]
        third_agents["Third-party<br/>baselines/third_party/"]
    end
    
    subgraph "Utilities"
        gym_wrapper["GymFromDMEnv<br/>OpenAI Gym compatibility"]
        load_functions["load_and_record_*<br/>Logging integration"]
    end
    
    base_agent_class --> jax_agents
    base_agent_class --> tf_agents
    base_agent_class --> third_agents
    
    jax_deps --> jax_agents
    tf_deps --> tf_agents
    third_deps --> third_agents
    
    dm_env --> gym_wrapper
    dm_env --> load_functions
    
    load_functions --> jax_agents
    load_functions --> tf_agents
    load_functions --> third_agents
```

Sources: [setup.py:24-50](), [README.md:187-199]()

## Data Flow and Experiment Execution

The system orchestrates experiments through a standardized pipeline that maintains consistency across different agent implementations:

### Experiment Execution Pipeline

```mermaid
flowchart TD
    subgraph "Experiment Definition"
        sweep_ids["sweep.SWEEP<br/>All experiment IDs"]
        bsuite_id["bsuite_id string<br/>e.g., 'deep_sea/7'"]
        settings["SETTINGS<br/>Environment parameters"]
    end
    
    subgraph "Environment Loading"
        load_from_id["bsuite.load_from_id()"]
        load_and_record["load_and_record_to_*<br/>CSV, SQLite, Terminal"]
        env_instance["Environment Instance<br/>dm_env protocol"]
    end
    
    subgraph "Agent Execution"
        agent_step["agent.step(timestep)"]
        env_step["env.step(action)"]
        episode_loop["Episode Loop<br/>bsuite_num_episodes"]
    end
    
    subgraph "Data Collection"
        logging_wrappers["Logging Wrappers<br/>Automatic data capture"]
        storage_backends["Storage Backends<br/>csv_logging, sqlite_logging"]
    end
    
    subgraph "Analysis"
        data_loading["Data Loading<br/>Pandas integration"]
        analysis_notebook["results.ipynb<br/>Comprehensive analysis"]
        report_generation["Report Generation<br/>LaTeX summaries"]
    end
    
    sweep_ids --> bsuite_id
    bsuite_id --> load_from_id
    settings --> load_from_id
    
    load_from_id --> load_and_record
    load_and_record --> env_instance
    
    env_instance --> episode_loop
    episode_loop --> agent_step
    agent_step --> env_step
    env_step --> agent_step
    
    env_instance --> logging_wrappers
    logging_wrappers --> storage_backends
    
    storage_backends --> data_loading
    data_loading --> analysis_notebook
    analysis_notebook --> report_generation
```

Sources: [README.md:93-112](), [README.md:138-154](), [README.md:176-185]()

## Package Dependencies and Installation

The system supports flexible installation with optional dependencies for different use cases:

| Dependency Group | Key Libraries | Purpose |
|------------------|---------------|---------|
| Core | `dm_env`, `numpy`, `pandas`, `matplotlib` | Basic functionality |
| JAX Baselines | `jax`, `dm-haiku`, `optax`, `rlax` | JAX agent implementations |
| TF Baselines | `tensorflow`, `dm-sonnet`, `trfl` | TensorFlow agents |
| Third-party | `dopamine-rl`, `baselines` | External agent integration |
| Testing | `pytest-xdist`, `pytype`, `gym==0.20.0` | Development and CI |

The modular dependency structure allows users to install only the components they need:

- `pip install bsuite` - Core framework only
- `pip install bsuite[baselines_jax]` - Include JAX agents  
- `pip install bsuite[baselines]` - Include TensorFlow agents
- `pip install bsuite[testing]` - Include development tools

Sources: [setup.py:73-91](), [README.md:58-82]()

## Research Integration and Extensibility  

bsuite supports the complete research lifecycle from hypothesis testing to publication-ready results. The system provides:

- **Standardized Benchmarks**: Consistent evaluation across different algorithms
- **Automated Analysis**: Pre-built Jupyter notebooks for comprehensive evaluation
- **Publication Support**: LaTeX report generation for conference submissions
- **Framework Agnostic**: Support for JAX, TensorFlow, and third-party libraries
- **Extensible Design**: Clear interfaces for adding new environments and agents

The framework facilitates reproducible research by automating data collection within environments through the `load_and_record_*` functions, ensuring consistent logging across all experiments without constraining agent implementations.

Sources: [README.md:11-26](), [README.md:278-288](), [setup.py:95-103]()

---

