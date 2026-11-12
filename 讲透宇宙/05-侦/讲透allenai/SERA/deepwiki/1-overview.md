<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SERA · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [assets/SERA.jpg](assets/SERA.jpg)
- [modules/SWE-agent/README.md](modules/SWE-agent/README.md)

</details>



## Purpose and Scope

This document provides a high-level introduction to the SERA repository, which consists of two main systems:

1. **SERA Data Generation System** - A multi-stage pipeline for generating synthetic training data from language models
2. **SWE-agent** - An autonomous software engineering agent that uses language models to perform coding tasks

This page explains the overall architecture, repository structure, and how these systems relate to each other. For detailed information about specific subsystems, refer to:
- SERA pipeline stages and configuration: [SERA Data Generation System](#2)
- SWE-agent capabilities and usage: [SWE-agent Module](#3)
- Development environment setup: [Development Environment](#4)
- Deployment and containerization: [Docker and Containerization](#5)

## Repository Structure

The SERA repository is organized into two primary layers: the root SERA system and the SWE-agent module located in `modules/SWE-agent/`.

### Directory Organization

```mermaid
graph TB
    root["SERA Repository Root"]
    
    root --> README["README.md"]
    root --> assets["assets/"]
    root --> sera["sera/"]
    root --> modules["modules/"]
    root --> gitignore[".gitignore"]
    
    sera --> main["sera/main.py"]
    sera --> config["sera/configs/"]
    sera --> datagen["sera/datagen/"]
    
    modules --> sweagent["modules/SWE-agent/"]
    modules --> code2flow["modules/code2flow/"]
    
    sweagent --> swereadme["README.md"]
    sweagent --> swecore["Python Application"]
    sweagent --> docker["Dockerfile"]
    sweagent --> devcontainer[".devcontainer/"]
    
    gitignore --> output_dirs["Ignored Output Directories:<br/>logs/, repos/, experiments/,<br/>outputs/, results/, testbed/"]
```

**Sources:** [.gitignore:1-227](), [README.md:1-185](), [modules/SWE-agent/README.md:1-105]()

### Key Directories and Artifacts

| Directory/File | Purpose |
|----------------|---------|
| `sera/` | SERA data generation pipeline source code |
| `sera/main.py` | Pipeline orchestrator and entry point |
| `sera/configs/` | YAML configuration files for experiments |
| `sera/datagen/` | Data generation modules and inference server scripts |
| `modules/SWE-agent/` | SWE-agent autonomous coding agent (git submodule) |
| `modules/code2flow/` | Code analysis utilities |
| `experiments/` | Generated experiment outputs (gitignored) |
| `outputs/` | Pipeline output data (gitignored) |
| `results/` | Evaluation results (gitignored) |
| `logs/` | Runtime logs (gitignored) |
| `repos/` | Cloned repository mirrors (gitignored) |

**Sources:** [.gitignore:1-10](), [.gitignore:174-178](), [README.md:7-16]()

## SERA Data Generation System

SERA (Soft-Verified Efficient Repository Agents) is a system for generating synthetic training data by having language models perform software engineering tasks on real codebases.

### Pipeline Architecture

```mermaid
flowchart LR
    input_repos["Repository<br/>Mirrors<br/>(repos)"]
    input_issues["PR Issues<br/>(pr_issues)"]
    input_config["Config YAML<br/>(sera/configs)"]
    
    main["sera/main.py<br/>Pipeline Orchestrator"]
    
    generate["Stage 0:<br/>generate"]
    distill1["Stage 1:<br/>distill_stage_one"]
    distill2["Stage 2:<br/>distill_stage_two"]
    eval["Stage 3:<br/>eval"]
    postprocess["Stage 4:<br/>postprocess"]
    
    output_exp["experiments/<br/>Experiment Data"]
    output_logs["logs/<br/>Pipeline Logs"]
    
    input_repos --> main
    input_issues --> main
    input_config --> main
    
    main --> generate
    generate --> distill1
    distill1 --> distill2
    distill2 --> eval
    eval --> postprocess
    
    postprocess --> output_exp
    main --> output_logs
```

**Sources:** [README.md:130-156](), [.gitignore:1-7]()

### Inference Server Integration

SERA supports multiple inference backends for data generation:

```mermaid
graph TB
    sera_pipeline["sera/main.py"]
    
    subgraph open_source["Open-Source Models"]
        glm45["GLM-4.5-Air<br/>launch_glm45.sh"]
        glm46["GLM-4.6<br/>launch_glm46.sh"]
        qwen["Qwen Models<br/>launch_qwen3_models.sh"]
    end
    
    subgraph closed_source["Closed-Source Models"]
        openai["OpenAI API"]
        anthropic["Anthropic API"]
        azure["Azure OpenAI"]
    end
    
    open_source --> sera_pipeline
    closed_source --> sera_pipeline
```

**Sources:** [README.md:18-32](), [README.md:86-94]()

### Configuration Profiles

SERA includes pre-configured experiment profiles for different use cases:

| Configuration | Purpose | Key Features |
|---------------|---------|--------------|
| `specialization_django` | Generate data for Django/Sympy repos from SWE-Bench | Uses existing SWE-Bench issues |
| `specialization_personal` | Generate data for custom repositories | Requires GitHub mirror organization |
| `specialization_anthropic` | Use closed-source models (Claude) | No inference server setup needed |
| `swesmith_scaling` | Large-scale data generation with sharding | Supports multi-server parallel execution |

**Sources:** [README.md:39-122]()

### Multi-Server Scaling

SERA supports horizontal scaling through dataset sharding across multiple inference servers:

```mermaid
graph LR
    dataset["Dataset<br/>(Issues/Commits)"]
    
    shard0["Shard 0<br/>distill.shard=0"]
    shard1["Shard 1<br/>distill.shard=1"]
    shard2["Shard 2<br/>distill.shard=2"]
    shard3["Shard 3<br/>distill.shard=3"]
    
    server0["Inference Server 0<br/>URL_1"]
    server1["Inference Server 1<br/>URL_2"]
    server2["Inference Server 2<br/>URL_3"]
    server3["Inference Server 3<br/>URL_4"]
    
    dataset --> shard0
    dataset --> shard1
    dataset --> shard2
    dataset --> shard3
    
    shard0 --> server0
    shard1 --> server1
    shard2 --> server2
    shard3 --> server3
```

**Sources:** [README.md:96-121]()

## SWE-agent Autonomous Software Engineering Agent

SWE-agent is an autonomous agent system that enables language models to perform software engineering tasks through configurable Agent-Computer Interfaces (ACIs).

### Core Capabilities

```mermaid
graph TB
    sweagent["SWE-agent<br/>modules/SWE-agent/"]
    
    aci["Agent-Computer<br/>Interface (ACI)"]
    lm["Language Model<br/>Integration"]
    ice["Isolated Computer<br/>Environment"]
    
    github_fix["Fix GitHub Issues<br/>(SWE-Bench)"]
    web_tasks["Web-based Tasks"]
    ctf["CTF Cybersecurity<br/>Challenges"]
    custom["Custom Coding<br/>Challenges"]
    
    sweagent --> aci
    sweagent --> lm
    aci --> ice
    lm --> ice
    
    ice --> github_fix
    ice --> web_tasks
    ice --> ctf
    ice --> custom
```

**Sources:** [modules/SWE-agent/README.md:15-22]()

### Language Model Support

SWE-agent integrates with multiple AI model providers:

| Provider | Models | Configuration |
|----------|--------|---------------|
| OpenAI | GPT-4o, GPT-4, etc. | Via OpenAI API |
| Anthropic | Claude Sonnet 3.5, 3.7 | Via Anthropic API |
| Azure | Azure-hosted OpenAI models | Via Azure OpenAI endpoint |
| Together AI | Various open models | Via Together API |
| Groq | Fast inference models | Via Groq API |
| Local/Custom | Any OpenAI-compatible server | Custom endpoint URL |

**Sources:** [modules/SWE-agent/README.md:1-45]()

### EnIGMA Cybersecurity Mode

SWE-agent includes EnIGMA mode for offensive cybersecurity (Capture The Flag) challenges, featuring:

- **Debugger**: Interactive debugging capabilities for binary analysis
- **Server Connection Tools**: Network interaction tools for CTF challenges  
- **Summarizer**: Handles long command outputs efficiently

**Sources:** [modules/SWE-agent/README.md:46-56]()

## System Integration and Data Flow

### SERA-to-SWE-agent Relationship

```mermaid
graph TB
    sera_gen["SERA Pipeline<br/>sera/main.py"]
    training_data["Generated<br/>Training Data"]
    model_training["Model Training<br/>sera/datagen/train/"]
    trained_model["Trained Model"]
    sweagent_use["SWE-agent<br/>Using Trained Model"]
    
    sera_gen --> training_data
    training_data --> model_training
    model_training --> trained_model
    trained_model --> sweagent_use
```

SERA generates synthetic training data by having language models solve coding tasks. This data is used to train more capable coding models, which can then be deployed in SWE-agent for autonomous software engineering.

**Sources:** [README.md:1-6](), [README.md:171-173](), [modules/SWE-agent/README.md:15-22]()

## Development and Deployment Infrastructure

### Containerization Stack

```mermaid
graph LR
    devcontainer[".devcontainer/<br/>VS Code Dev Container"]
    dockerfile["Dockerfile<br/>Production Image"]
    dockerignore[".dockerignore<br/>Build Exclusions"]
    
    dev_env["Development<br/>Environment"]
    prod_env["Production<br/>Deployment"]
    
    devcontainer --> dev_env
    dockerfile --> prod_env
    dockerignore --> dockerfile
```

**Sources:** [.gitignore:20-32]()

### Output and Artifact Management

The repository excludes various output directories from version control to keep the codebase clean:

| Directory | Purpose | Managed By |
|-----------|---------|------------|
| `logs/` | Pipeline execution logs | SERA |
| `repos/` | Cloned repository mirrors | SERA |
| `experiments/` | Experiment output data | SERA |
| `outputs/` | Generated dataset outputs | SERA |
| `results/` | Evaluation results | SWE-agent |
| `testbed/` | Test execution environments | SWE-agent |
| `trajectories/` | Agent execution traces | SWE-agent |

**Sources:** [.gitignore:1-10](), [.gitignore:174-178](), [.gitignore:20-32]()

## Licensing

The repository uses a dual-licensing structure:

- **SERA System**: Apache License 2.0
- **SWE-agent Module**: MIT License

For licensing details, see [Licensing](#8.1).

**Sources:** [modules/SWE-agent/README.md:93-94]()

## Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/allenai/SERA

# Create conda environment
conda create -n sera python=3.12

# Install packages
pip install -e . -e modules/code2flow -e modules/SWE-agent
```

**Sources:** [README.md:7-15]()

### Quick Start Examples

1. **Generate data from Django repositories:**
   ```bash
   python sera/main.py \
       --config-name=specialization_django \
       distill.model.name=openai/GLM-4.5-Air \
       distill.model.url=http://localhost:24444/v1
   ```

2. **Use SWE-agent to fix GitHub issues:**
   See [Agent Capabilities and Usage](#3.1) for detailed instructions.

**Sources:** [README.md:39-46](), [modules/SWE-agent/README.md:33-42]()

## External Resources

- **Technical Report**: https://allenai.org/papers/opencodingagents
- **Test SERA in Claude**: https://github.com/allenai/sera-cli
- **SWE-agent Documentation**: https://swe-agent.com
- **SWE-agent Discord**: https://discord.gg/AVEFbBn2rH

**Sources:** [README.md:3-5](), [modules/SWE-agent/README.md:9-11]()

---

