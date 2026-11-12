<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/acon · page 3 Core Concepts · fetched 2026-10-26 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/concept.png](assets/concept.png)

</details>



This document introduces the fundamental concepts underlying the ACON framework. It covers the core abstractions (environments, agents, and context compressors), explains what context optimization is and why it matters for long-horizon agents, and provides an overview of the four-stage experimental pipeline.

For detailed information about specific topics:
- For setting up and running experiments, see [Running Experiments](#5)
- For benchmark-specific details, see [Benchmarks](#4)
- For configuration and customization, see [Configuration](#6)
- For analysis and optimization procedures, see [Analysis and Optimization](#7)

## What is ACON?

ACON (Agent Context Optimization) is a research framework for optimizing context compression in long-horizon LLM agents. The framework addresses a fundamental challenge: as agents execute multi-step tasks, their conversation history grows continuously, leading to increased token costs and potential context window limitations.

The framework provides:
- **Standardized abstractions** for environments, agents, and context compressors
- **Multi-benchmark support** across AppWorld, OfficeBench, and 8-objective QA
- **A four-stage pipeline** from baseline experiments to fully distilled local models
- **Analysis tools** for token usage, cost tracking, and prompt optimization

**Sources:** [README.md:1-41]()

## Core Abstractions

ACON defines three primary abstractions that work together to enable context-optimized agent execution:

```mermaid
graph TB
    subgraph "Core Abstractions in src/productive_agents/"
        ENV["Environment"]
        AGENT["Agent"]
        COMP["Context Compressor"]
    end
    
    subgraph "Environment Responsibilities"
        ENV_TASK["Load task specifications"]
        ENV_STATE["Maintain environment state"]
        ENV_OBS["Generate observations"]
        ENV_REWARD["Evaluate actions"]
    end
    
    subgraph "Agent Responsibilities"
        AGENT_PERCEIVE["Receive observations"]
        AGENT_REASON["Reason about actions"]
        AGENT_ACT["Execute actions"]
        AGENT_HIST["Manage history"]
    end
    
    subgraph "Compressor Responsibilities"
        COMP_HIST["Compress history"]
        COMP_OBS["Compress observations"]
        COMP_GUIDE["Apply guidelines"]
        COMP_MODEL["Use LLM for summarization"]
    end
    
    ENV --> ENV_TASK
    ENV --> ENV_STATE
    ENV --> ENV_OBS
    ENV --> ENV_REWARD
    
    AGENT --> AGENT_PERCEIVE
    AGENT --> AGENT_REASON
    AGENT --> AGENT_ACT
    AGENT --> AGENT_HIST
    
    COMP --> COMP_HIST
    COMP --> COMP_OBS
    COMP --> COMP_GUIDE
    COMP --> COMP_MODEL
    
    ENV_OBS -.observation.-> AGENT_PERCEIVE
    AGENT_ACT -.action.-> ENV_STATE
    AGENT_HIST -.raw history.-> COMP_HIST
    AGENT_PERCEIVE -.raw observation.-> COMP_OBS
    COMP_HIST -.compressed history.-> AGENT_REASON
    COMP_OBS -.compressed observation.-> AGENT_REASON
```

### Environment

The `Environment` abstraction represents the task execution environment. It is responsible for:
- Loading task specifications and initial state
- Maintaining the current state of the environment
- Generating observations in response to agent actions
- Evaluating action success and computing rewards

Each benchmark (AppWorld, OfficeBench, SmolAgents) implements this abstraction differently based on its domain requirements.

### Agent

The `Agent` abstraction implements the decision-making logic. It:
- Receives observations from the environment
- Reasons about what action to take next
- Executes actions by calling environment APIs
- Maintains a history of past observations and actions

The agent uses LLMs (either frontier models like GPT-4 or distilled local models) to perform reasoning.

### Context Compressor

The `Context Compressor` is responsible for reducing the size of the agent's context while preserving task-critical information. It operates on two types of inputs:

1. **History Compression**: Summarizes the sequence of past observations and actions
2. **Observation Compression**: Refines the current observation to remove redundant details

Compressors use LLM-based summarization guided by optimization guidelines.

**Sources:** [README.md:22-24](), [README.md:116-119]()

## The Context Optimization Problem

Long-horizon agents face a critical challenge: **unbounded memory growth**. As tasks progress through multiple steps, the agent's context accumulates:

```mermaid
graph LR
    T0["t=0<br/>Initial State"] --> T1["t=1<br/>Obs₁ + Action₁"]
    T1 --> T2["t=2<br/>Obs₁,₂ + Action₁,₂"]
    T2 --> T3["t=3<br/>Obs₁,₂,₃ + Action₁,₂,₃"]
    T3 --> TN["t=n<br/>Obs₁...ₙ + Action₁...ₙ"]
    
    subgraph "Without Compression"
        COST_GROWTH["Cost grows O(n²)<br/>Context size grows linearly"]
    end
    
    subgraph "With ACON Compression"
        COST_CONST["Cost grows O(n)<br/>Context size stays bounded"]
    end
    
    TN -.without compression.-> COST_GROWTH
    TN -.with compression.-> COST_CONST
```

Without compression, each LLM call includes all previous history, leading to:
- **Quadratic token costs**: Each step adds more tokens to be re-processed
- **Context window limits**: Eventually exceeding model capacity
- **Degraded performance**: Irrelevant details dilute important information

Context optimization addresses this by compressing history at each step, maintaining bounded context size while preserving task-critical information.

**Sources:** [README.md:22-23]()

## Four-Stage Experimental Pipeline

ACON follows a systematic four-stage pipeline that progresses from baseline measurements to fully optimized local models:

```mermaid
graph TB
    subgraph "Stage 1: Baseline"
        S1_DESC["Run frontier models<br/>(GPT-4, GPT-4o-mini)<br/>without compression"]
        S1_OUT["Baseline performance<br/>and token costs"]
    end
    
    subgraph "Stage 2: Context Optimization"
        S2_ANALYZE["Analyze baseline<br/>token usage patterns"]
        S2_OPT["Optimize compression<br/>guidelines using<br/>unified_update_history_prompt.py"]
        S2_VAL["Validate with<br/>run_ctxopt_pipeline.py"]
        S2_OUT["Optimized guidelines<br/>in YAML configs"]
        
        S2_ANALYZE --> S2_OPT
        S2_OPT --> S2_VAL
        S2_VAL --> S2_OUT
    end
    
    subgraph "Stage 3: Compressor Distillation"
        S3_DATA["Generate training data<br/>from history_optimizer_history.json"]
        S3_TRAIN["Fine-tune compressor LoRA<br/>on base model (Qwen3-14B)"]
        S3_OUT["Compressor LoRA adapter"]
        
        S3_DATA --> S3_TRAIN
        S3_TRAIN --> S3_OUT
    end
    
    subgraph "Stage 4: Agent Distillation"
        S4_DATA["Generate training data<br/>from llm_history.json"]
        S4_TRAIN["Fine-tune agent LoRA<br/>on base model + compressor LoRA"]
        S4_OUT["Complete local agent<br/>with stacked LoRAs"]
        
        S4_DATA --> S4_TRAIN
        S4_TRAIN --> S4_OUT
    end
    
    S1_OUT --> S2_ANALYZE
    S2_OUT --> S3_DATA
    S3_OUT --> S4_DATA
```

### Stage 1: Baseline

Establish baseline performance using frontier models without compression. This measures:
- Task success rates
- Token usage per task
- Total costs
- Performance bottlenecks

### Stage 2: Context Optimization

Optimize compression guidelines through automated prompt engineering:
1. Analyze token usage patterns from baseline experiments
2. Generate candidate compression guidelines
3. Evaluate each guideline on validation tasks
4. Select the best-performing configuration

The output is a YAML configuration file (e.g., `gpt-4.1-mini_history.yaml`) containing optimized compression instructions.

### Stage 3: Compressor Distillation

Train a local model to replicate the compression behavior:
1. Extract compression examples from `history_optimizer_history.json`
2. Fine-tune a LoRA adapter on a base model (e.g., Qwen3-14B)
3. The resulting model can perform compression locally without API calls

### Stage 4: Agent Distillation

Train a local model to replicate the agent reasoning:
1. Extract agent decision examples from `llm_history.json`
2. Fine-tune a second LoRA adapter on the base model
3. Stack both LoRA adapters to create a complete local agent

The final model performs both compression and reasoning locally, eliminating API dependencies.

**Sources:** [README.md:132-136]()

## Agent-Environment Interaction Flow

The following diagram shows how components interact during task execution:

```mermaid
sequenceDiagram
    participant ENV as Environment
    participant AGENT as Agent
    participant COMP as ContextCompressor
    participant LLM as LLM<br/>(Frontier or Local)
    
    ENV->>AGENT: Initial observation
    
    loop Each Step
        AGENT->>COMP: Compress history
        COMP->>LLM: Summarization request
        LLM->>COMP: Compressed history
        
        AGENT->>COMP: Compress observation
        COMP->>LLM: Refinement request
        LLM->>COMP: Compressed observation
        
        AGENT->>AGENT: Build prompt with<br/>compressed context
        AGENT->>LLM: Reasoning request
        LLM->>AGENT: Next action
        
        AGENT->>ENV: Execute action
        ENV->>ENV: Update state
        ENV->>AGENT: New observation
    end
    
    ENV->>AGENT: Task complete
```

### Execution Flow Details

1. **Initialization**: Environment loads the task and provides initial observation
2. **History Compression**: Agent sends accumulated history to compressor
3. **Observation Compression**: Agent sends current observation to compressor
4. **Reasoning**: Agent uses compressed context to determine next action
5. **Action Execution**: Environment processes action and updates state
6. **Iteration**: Process repeats until task completion

The key insight is that compression happens **before reasoning**, ensuring the agent always works with bounded context.

**Sources:** [README.md:22-24]()

## Configuration-Driven Design

ACON uses a layered configuration system to control all aspects of execution:

```mermaid
graph TB
    subgraph "Configuration Layers"
        PRIVATE["private_config.yaml<br/>API credentials"]
        BASE["base_config.yaml<br/>Default agent settings"]
        CTXOPT["context_opt/*.yaml<br/>Compression guidelines"]
        PROMPTS["prompts/*.jinja<br/>Prompt templates"]
    end
    
    subgraph "Runtime Assembly"
        LOADER["Configuration Loader"]
        MERGER["Config Merger"]
        RENDERER["Jinja Template Renderer"]
    end
    
    subgraph "Execution Components"
        AGENT_INST["Agent Instance"]
        COMP_INST["Compressor Instance"]
    end
    
    PRIVATE --> LOADER
    BASE --> LOADER
    CTXOPT --> LOADER
    PROMPTS --> RENDERER
    
    LOADER --> MERGER
    MERGER --> AGENT_INST
    MERGER --> COMP_INST
    RENDERER --> AGENT_INST
    RENDERER --> COMP_INST
```

### Configuration Components

| Component | Purpose | Example |
|-----------|---------|---------|
| `private_config.yaml` | API keys and credentials | OpenAI API key |
| `base_config.yaml` | Default agent settings | Model name, temperature, max tokens |
| `context_opt/*.yaml` | Compression guidelines | History/observation compression rules |
| `prompts/*.jinja` | Prompt templates | System prompts, user prompts |

The system merges these configurations at runtime, with later configurations overriding earlier ones. This enables easy experimentation by swapping configuration files without code changes.

**Sources:** [README.md:104-110]()

## Output and Traceability

ACON generates comprehensive outputs for each task execution, enabling detailed analysis and reproducibility:

```mermaid
graph TB
    subgraph "Task Execution"
        TASK["Task Execution"]
    end
    
    subgraph "Output Files per Task"
        HIST_OPT["history_optimizer_history.json<br/>Compression requests/responses"]
        LLM_HIST["llm_history.json<br/>Agent reasoning requests/responses"]
        ENV_HIST["env_history.json<br/>Environment state transitions"]
        RESULTS["results.json<br/>Task outcome and metrics"]
    end
    
    subgraph "Aggregated Outputs"
        SUMMARY["experiment_summary.json<br/>Cross-task statistics"]
    end
    
    subgraph "Analysis Tools"
        TOKEN_ANALYSIS["analyze_experiment_tokens_v2<br/>Token usage analysis"]
        COST_REPORT["Cost reports<br/>Markdown and CSV"]
        PROMPT_OPT["unified_update_history_prompt.py<br/>Prompt optimization"]
    end
    
    TASK --> HIST_OPT
    TASK --> LLM_HIST
    TASK --> ENV_HIST
    TASK --> RESULTS
    
    HIST_OPT --> SUMMARY
    LLM_HIST --> SUMMARY
    ENV_HIST --> SUMMARY
    RESULTS --> SUMMARY
    
    HIST_OPT --> TOKEN_ANALYSIS
    LLM_HIST --> TOKEN_ANALYSIS
    TOKEN_ANALYSIS --> COST_REPORT
    
    HIST_OPT --> PROMPT_OPT
    LLM_HIST --> PROMPT_OPT
```

### Output File Descriptions

- **`history_optimizer_history.json`**: Complete log of all compression operations, including input context, guidelines, and compressed output
- **`llm_history.json`**: Complete log of agent reasoning, including prompts sent to LLM and responses received
- **`env_history.json`**: Complete log of environment interactions, including actions executed and observations returned
- **`results.json`**: Task outcome (success/failure), final state, and execution metrics
- **`experiment_summary.json`**: Aggregated statistics across all tasks in the experiment

These outputs enable:
- Debugging agent behavior
- Analyzing token usage patterns
- Training distilled models
- Optimizing compression guidelines

**Sources:** [README.md:82-86]()

## Model Serving Options

ACON supports two model serving configurations, allowing seamless transitions from frontier to local models:

| Configuration | Compressor Model | Agent Model | Use Case |
|---------------|------------------|-------------|----------|
| **Frontier** | OpenAI API (e.g., gpt-4o-mini) | OpenAI API (e.g., gpt-4o) | Baseline experiments, optimization |
| **Local** | Base model + Compressor LoRA | Base model + Compressor LoRA + Agent LoRA | Production deployment, cost reduction |

The local configuration uses **stacked LoRA adapters** on a single base model (e.g., Qwen3-14B), where:
1. The compressor LoRA is applied for compression operations
2. Both LoRAs are stacked for agent reasoning operations

This architecture enables complete local execution without external API dependencies.

**Sources:** [README.md:132-136]()

## Summary

ACON provides a complete framework for context optimization in long-horizon agents:

1. **Core Abstractions**: Environment, Agent, and Context Compressor work together to enable bounded-context execution
2. **Four-Stage Pipeline**: Systematic progression from baseline to optimized to distilled models
3. **Configuration-Driven**: YAML configs and Jinja templates enable rapid experimentation
4. **Comprehensive Traceability**: Detailed outputs support analysis, debugging, and training
5. **Flexible Deployment**: Support for both frontier and local models

The framework standardizes context optimization research across multiple benchmarks while providing tools for every stage of the optimization process.

**Sources:** [README.md:1-142]()

---

