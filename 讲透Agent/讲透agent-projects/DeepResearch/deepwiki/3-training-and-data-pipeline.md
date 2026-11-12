<!-- source: DeepWiki mcp.deepwiki.com · repo Alibaba-NLP/DeepResearch · page 3 Training and Data Pipeline · fetched 2026-10-29 -->

# Training and Data Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [.gitignore](.gitignore)
- [Agent/AgentFounder/README.md](Agent/AgentFounder/README.md)
- [Agent/AgentFounder/assets/logo.png](Agent/AgentFounder/assets/logo.png)
- [Agent/AgentFounder/assets/main_performance.png](Agent/AgentFounder/assets/main_performance.png)
- [Agent/AgentScaler/README.md](Agent/AgentScaler/README.md)
- [Agent/AgentScaler/assets/main.png](Agent/AgentScaler/assets/main.png)
- [README.md](README.md)
- [WebAgent/WebLeaper/README.md](WebAgent/WebLeaper/README.md)
- [WebAgent/WebLeaper/assets/overview.png](WebAgent/WebLeaper/assets/overview.png)
- [WebAgent/WebLeaper/assets/performance_summary.png](WebAgent/WebLeaper/assets/performance_summary.png)
- [WebAgent/WebLeaper/assets/webleaper.jpg](WebAgent/WebLeaper/assets/webleaper.jpg)
- [inference/run_react_infer.sh](inference/run_react_infer.sh)

</details>



## Purpose and Scope

This document provides an overview of the complete training and data pipeline for Tongyi DeepResearch, covering data generation, model training phases, and quality metrics. The pipeline transforms raw data through three major stages: agentic continual pre-training, supervised fine-tuning (SFT), and reinforcement learning (RL).

For implementation details of specific components:
- Development pipeline stages: see [Development Pipeline Overview](#3.1)
- Synthetic data generation: see [Synthetic Data Generation](#3.2)
- Entity-intensive training data: see [WebLeaper](#3.3)
- Continual pre-training methodology: see [AgentFounder](#3.4)
- Environment scaling strategies: see [AgentScaler](#3.5)
- RL optimization methods: see [Reinforcement Learning Methods](#3.6)

For inference and evaluation infrastructure: see [Core Inference Engine](#2) and [Evaluation and Benchmarks](#5).

Sources: [README.md:42-47](), [WebAgent/WebLeaper/README.md:1-17]()

---

## Training Architecture Overview

The training pipeline employs a three-phase approach that progressively refines the model's capabilities:

1. **Agentic Continual Pre-training (CPT)**: Extends the base model's capabilities using large-scale agentic interaction corpora
2. **Supervised Fine-Tuning (SFT)**: Filters trajectories using quality metrics (ISR/ISE) to train on high-quality demonstrations
3. **Reinforcement Learning (RL)**: Further optimizes the model using Group Relative Policy Optimization (GRPO) with hybrid rewards

```mermaid
graph TB
    subgraph "Phase 1: Continual Pre-training"
        BaseModel["Base Model<br/>(e.g., Qwen3-30B-A3B)"]
        CPTData["Agentic Interaction<br/>Corpus"]
        CPTModel["CPT Model<br/>(AgentFounder-30B)"]
        BaseModel -->|"Extended<br/>Context 32K-128K"| CPTModel
        CPTData -->|"Large-Scale<br/>Agentic Data"| CPTModel
    end
    
    subgraph "Phase 2: Supervised Fine-Tuning"
        SFTData["Filtered SFT<br/>Trajectories"]
        ISRFilter["ISR > α<br/>(Coverage)"]
        ISEFilter["ISE > β<br/>(Efficiency)"]
        SFTModel["SFT Model"]
        
        SFTData --> ISRFilter
        SFTData --> ISEFilter
        ISRFilter --> SFTModel
        ISEFilter --> SFTModel
    end
    
    subgraph "Phase 3: Reinforcement Learning"
        RLData["On-Policy<br/>Trajectories"]
        HybridReward["Hybrid Reward<br/>System"]
        GRPO["Group Relative Policy<br/>Optimization"]
        FinalModel["Tongyi-DeepResearch<br/>30B-A3B"]
        
        RLData --> HybridReward
        HybridReward --> GRPO
        GRPO --> FinalModel
    end
    
    CPTModel --> SFTModel
    SFTModel --> FinalModel
```

**Figure 1: Three-Phase Training Pipeline**

Sources: [README.md:42-47](), [WebAgent/WebLeaper/README.md:12-15](), [WebAgent/WebLeaper/README.md:144-150]()

---

## Data Generation Ecosystem

The training pipeline sources data from multiple specialized systems, each contributing distinct capabilities. The data generation process is fully automated and scalable, producing diverse agentic interaction data.

```mermaid
graph TB
    subgraph "Raw Data Sources"
        Wikipedia["Wikipedia Tables<br/>(Structured Data)"]
        WebContent["Web Content<br/>(Raw Documents)"]
    end
    
    subgraph "WebLeaper Task Synthesis"
        BasicGen["Basic Variant<br/>Generator"]
        UnionGen["Union Variant<br/>Generator<br/>(Maximal Biclique)"]
        ReverseGen["Reverse-Union<br/>Generator<br/>(Fuzzed Anchors)"]
    end
    
    subgraph "AgentFounder Methods"
        FASPlanning["FAS: Planning<br/>Action Synthesis"]
        FASReasoning["FAS: Reasoning<br/>Action Synthesis"]
        HAS["HAS: Decision-Making<br/>Action Synthesis"]
    end
    
    subgraph "Trajectory Generation"
        ReactAgent["ReAct Agent<br/>(Tool-Using)"]
        SearchTool["Search Tool<br/>(Serper.dev)"]
        VisitTool["Visit Tool<br/>(Jina.ai)"]
    end
    
    subgraph "Quality Filtering"
        ISRFilter["ISR Filter<br/>(α = 0.3)"]
        ISEFilter["ISE Filter<br/>(β = 0.1)"]
    end
    
    subgraph "Training Corpora"
        CPTCorpus["CPT Corpus<br/>(32K-128K ctx)"]
        SFTCorpus["SFT Corpus<br/>(High ISR/ISE)"]
        RLCorpus["RL Corpus<br/>(~500 tasks)"]
    end
    
    Wikipedia --> BasicGen
    Wikipedia --> UnionGen
    Wikipedia --> ReverseGen
    
    BasicGen --> ReactAgent
    UnionGen --> ReactAgent
    ReverseGen --> ReactAgent
    
    FASPlanning --> CPTCorpus
    FASReasoning --> CPTCorpus
    HAS --> CPTCorpus
    
    ReactAgent --> SearchTool
    ReactAgent --> VisitTool
    SearchTool --> ISRFilter
    VisitTool --> ISRFilter
    
    ISRFilter --> ISEFilter
    ISEFilter --> SFTCorpus
    
    CPTCorpus --> SFTCorpus
    SFTCorpus --> RLCorpus
```

**Figure 2: Data Generation and Filtering Pipeline**

### Data Variant Characteristics

| Variant | Description | Implementation | Key Characteristics |
|---------|-------------|----------------|---------------------|
| **Basic** | Single-source, high-density tasks from homogeneous Wikipedia tables | Single table → root entity → 2nd-layer entities → attributes | Compact contexts, maximal valid actions, high entity density |
| **Union** | Multi-source tasks requiring intersection/union across sources | Maximal biclique enumeration over shared relation sets | Structure-aligned fusion, cross-source reasoning, realistic synthesis |
| **Reverse-Union** | Fuzzed attribute clues requiring deduction before search | Attribute-level clues → deduce anchor → pivot → union search | Forces anchor deduction, prevents keyword shortcuts, anti-shortcut robustness |

### Tree-Structured Information Seeking

WebLeaper models information-seeking as tree-structured reasoning:
- **Root (layer 1)**: Question entity
- **2nd Layer**: Key entities to retrieve
- **3rd Layer**: Attributes and linked entities

Each 2nd-layer node + its attributes forms a subtree. Tasks require retrieving both final and intermediate entities, with the number of targets $n$ providing stable efficiency signals as $\text{Var}(\text{ISE}) = \mathcal{O}(1/n)$.

Sources: [README.md:44](), [WebAgent/WebLeaper/README.md:36-49](), [WebAgent/WebLeaper/README.md:124-141](), [WebAgent/WebLeaper/README.md:38-48]()

---

## Quality Metrics and Filtering

### Information-Seeking Rate (ISR)

Measures the fraction of required entities retrieved:

$$
\text{ISR} = \frac{|R \cap O|}{|R|}
$$

where $R$ is the set of required entities and $O$ is the set of retrieved entities.

### Information-Seeking Efficiency (ISE)

Measures target entities discovered per action step:

$$
\text{ISE} = \frac{n}{T}
$$

where $n$ is the number of target entities and $T$ is the number of action steps.

**Key Property**: As $n$ increases, $\text{Var}(\text{ISE}) = \mathcal{O}(1/n)$, providing reliable efficiency signals during training.

### SFT Trajectory Selection Criteria

```mermaid
graph TD
    TrajectoryGen["Trajectory<br/>Generation"]
    CoverageCheck{"ISR > α?"}
    EfficiencyCheck{"ISE > β?"}
    Accepted["Accepted for<br/>SFT Training"]
    Rejected["Rejected"]
    
    TrajectoryGen --> CoverageCheck
    CoverageCheck -->|Yes| EfficiencyCheck
    CoverageCheck -->|No| Rejected
    EfficiencyCheck -->|Yes| Accepted
    EfficiencyCheck -->|No| Rejected
```

**Figure 3: SFT Trajectory Filtering Pipeline**

Typical threshold values:
- Coverage threshold: α = 0.3
- Efficiency threshold: β = 0.1

Sources: [WebAgent/WebLeaper/README.md:52-63](), [WebAgent/WebLeaper/README.md:66-79](), [WebAgent/WebLeaper/README.md:147-148]()

---

## Training Data Mix

### SFT Phase Data Composition

```mermaid
graph TB
    subgraph "SFT Data Mix"
        WebLeaperData["WebLeaper Tasks<br/>(Basic/Union/Reverse-Union)"]
        DeepSearchData["Deep-Search Data<br/>(e.g., WebSailor-V2)"]
        MixedSFT["Mixed SFT<br/>Training Data"]
        
        WebLeaperData -->|"Entity-Intensive<br/>Tasks"| MixedSFT
        DeepSearchData -->|"Long-Horizon<br/>Browsing"| MixedSFT
    end
    
    subgraph "Filtering Criteria"
        ISRThreshold["ISR > 0.3"]
        ISEThreshold["ISE > 0.1"]
        
        MixedSFT --> ISRThreshold
        MixedSFT --> ISEThreshold
    end
    
    subgraph "Training"
        FilteredSFT["Filtered SFT<br/>Corpus"]
        SFTTraining["Supervised<br/>Fine-Tuning"]
        
        ISRThreshold --> FilteredSFT
        ISEThreshold --> FilteredSFT
        FilteredSFT --> SFTTraining
    end
```

**Figure 4: SFT Data Composition and Training Flow**

The SFT data mix balances:
- **Entity-intensive tasks** from WebLeaper for efficient information retrieval
- **Deep-search data** to maintain long-horizon browsing capabilities

### RL Phase Data Composition

```mermaid
graph TB
    subgraph "RL Data Mix"
        WebLeaperRL["~500 WebLeaper<br/>Reserved Tasks"]
        LegacyBenchmark["Legacy Benchmark<br/>Data"]
        MixedRL["Mixed RL<br/>Training Data"]
        
        WebLeaperRL --> MixedRL
        LegacyBenchmark --> MixedRL
    end
    
    subgraph "Reward Systems"
        WebLeaperReward["R_WebLeaper<br/>(Soft F-score)"]
        LegacyReward["R_legacy<br/>(Original Metrics)"]
        
        WebLeaperRL --> WebLeaperReward
        LegacyBenchmark --> LegacyReward
    end
    
    subgraph "Optimization"
        GRPO["Group Relative Policy<br/>Optimization"]
        TokenGrad["Token-level<br/>Policy Gradients"]
        LOO["Leave-one-out<br/>Advantage Estimation"]
        
        WebLeaperReward --> GRPO
        LegacyReward --> GRPO
        GRPO --> TokenGrad
        GRPO --> LOO
    end
```

**Figure 5: RL Data Composition and Optimization Components**

Sources: [WebAgent/WebLeaper/README.md:144-150](), [README.md:46]()

---

## Hybrid Reward System

The RL phase employs a hybrid reward system to address the challenges of entity-intensive tasks:

### WebLeaper Reward (R_WebLeaper)

For entity-intensive tasks, uses a granular soft F-score reward that handles semantic variations:

$$
\mathcal{R}_{\text{WebLeaper}} = (1 + \omega^2) \frac{P \cdot R_c}{\omega^2 P + R_c}
$$

where:
- $P$ is soft precision over retrieved entities
- $R_c$ is soft recall over ground-truth entities
- $\omega$ is a weighting parameter

**Key Advantage**: Handles entity variations (e.g., "USA" vs. "United States") through semantic similarity rather than exact matching.

### Legacy Reward (R_legacy)

For traditional benchmark data, uses original reward functions (e.g., binary success/failure).

### Training Performance Impact

| Model Configuration | BrowseComp | GAIA | xbench-DS | WideSearch (SR) | WideSearch (Row F1) | WideSearch (Item F1) |
|---------------------|------------|------|-----------|-----------------|---------------------|----------------------|
| SFT Only | 37.80 | 69.9 | 69.0 | 1.5 | 23.0 | 45.4 |
| SFT + RL | **38.8** (+1.0) | **73.2** (+3.3) | **72.0** (+3.0) | **4.0** (+2.5) | **31.0** (+8.0) | **48.8** (+3.4) |

Sources: [WebAgent/WebLeaper/README.md:82-97](), [WebAgent/WebLeaper/README.md:113-121]()

---

## Training Innovations and Implementation

The pipeline incorporates several key innovations implemented through the GRPO framework:

```mermaid
graph TB
    subgraph "GRPO: Group Relative Policy Optimization"
        GroupSample["Group Sampling<br/>(k trajectories per task)"]
        BaselineEst["Baseline Estimation<br/>(group average reward)"]
        AdvCalc["Advantage Calculation<br/>(trajectory vs baseline)"]
        PolicyUpdate["Policy Update<br/>(PPO-like objective)"]
    end
    
    subgraph "Token-Level Components"
        TokenGrad["Token-level<br/>Policy Gradients"]
        ActionSegment["Action-level<br/>Segmentation"]
        GradAccum["Gradient<br/>Accumulation"]
    end
    
    subgraph "Hybrid Reward System"
        WebLeaperReward["R_WebLeaper<br/>(Soft F-score)"]
        LegacyReward["R_legacy<br/>(Binary/Original)"]
        RewardMix["Reward<br/>Aggregation"]
    end
    
    subgraph "Stabilization Techniques"
        LOO["Leave-one-out<br/>Advantage Estimation"]
        NegFilter["Selective Negative<br/>Sample Filtering"]
        AdvBroadcast["Advantage<br/>Broadcasting"]
    end
    
    GroupSample --> BaselineEst
    BaselineEst --> AdvCalc
    AdvCalc --> PolicyUpdate
    
    WebLeaperReward --> RewardMix
    LegacyReward --> RewardMix
    RewardMix --> AdvCalc
    
    PolicyUpdate --> TokenGrad
    TokenGrad --> ActionSegment
    ActionSegment --> GradAccum
    
    AdvCalc --> LOO
    AdvCalc --> NegFilter
    AdvCalc --> AdvBroadcast
```

**Figure 6: GRPO Implementation Architecture**

### Key Innovation Components

#### 1. Strictly On-Policy RL
- Tight integration between trajectory generation and model updates
- Rollouts generated using current policy state
- `ROLLOUT_COUNT=3` rollouts per task for sample efficiency

#### 2. Group Relative Policy Optimization (GRPO)
- Samples multiple trajectories (group) per task
- Estimates advantage relative to group average reward
- More stable than individual trajectory-based methods
- Handles non-stationary environments through relative comparisons

#### 3. Token-Level Policy Gradients
- Fine-grained optimization at individual token level
- Action-level segmentation for long trajectories
- Gradient accumulation across trajectory segments

#### 4. Leave-One-Out Advantage Estimation
- Robust advantage estimation by excluding current sample
- Reduces variance in advantage calculations
- Improves training stability

#### 5. Selective Negative Sample Filtering
- Filters out extremely poor samples that could destabilize training
- Maintains on-policy property while improving sample efficiency
- Balances exploration and exploitation

### Training Workflow

```mermaid
graph LR
    subgraph "Data Generation"
        CurrentPolicy["Current Policy<br/>(SFT Model)"]
        GenerateRollouts["Generate Rollouts<br/>(ROLLOUT_COUNT=3)"]
        ComputeRewards["Compute Rewards<br/>(Hybrid System)"]
    end
    
    subgraph "GRPO Update"
        GroupAdvantage["Group Advantage<br/>Estimation"]
        PolicyGradients["Compute Policy<br/>Gradients"]
        UpdateModel["Update Model<br/>Parameters"]
    end
    
    subgraph "Evaluation"
        ValidateModel["Validate on<br/>Benchmarks"]
        CheckConvergence{"Converged?"}
    end
    
    CurrentPolicy --> GenerateRollouts
    GenerateRollouts --> ComputeRewards
    ComputeRewards --> GroupAdvantage
    GroupAdvantage --> PolicyGradients
    PolicyGradients --> UpdateModel
    UpdateModel --> ValidateModel
    ValidateModel --> CheckConvergence
    CheckConvergence -->|No| CurrentPolicy
    CheckConvergence -->|Yes| FinalModel["Final Model"]
```

**Figure 8: RL Training Workflow Loop**

### Parallel Trajectory Generation

The training pipeline uses parallel workers for efficient trajectory generation:

```python
# From .env configuration
MAX_WORKERS = 30  # Parallel workers for rollout generation
```

This enables:
- Concurrent trajectory generation across multiple tasks
- Efficient utilization of computational resources
- Faster iteration cycles during RL training

Sources: [README.md:46](), [.env.example:43]()

---

## Training Configuration

### Base Model and Backbone

- **Backbone**: `Qwen3-30B-A3B-Thinking-2507`
- **Total Parameters**: 30.5 billion
- **Activated Parameters**: 3.3 billion per token (MoE architecture)
- **Context Length Extension**: 32K → 128K tokens (via two-stage CPT)
- **Model Download**: Available via HuggingFace and ModelScope

```bash
# Model paths from .env configuration
MODEL_PATH=/your/model/path  # Points to downloaded model weights
```

### Inference Sampling Parameters

Different temperature settings are used for different training phases:

```python
# SFT trajectory generation (WebLeaper)
temperature = 0.6
top_p = 0.95

# RL rollout generation (from .env)
TEMPERATURE = 0.85
PRESENCE_PENALTY = 1.1
```

### Training Hyperparameters

Key hyperparameters from `.env.example`:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `ROLLOUT_COUNT` | 3 | Number of on-policy rollouts per task |
| `TEMPERATURE` | 0.85 | Sampling temperature for RL phase |
| `PRESENCE_PENALTY` | 1.1 | Penalty to encourage diverse generation |
| `MAX_WORKERS` | 30 | Parallel workers for trajectory generation |

### Multi-GPU Training Setup

The training infrastructure uses distributed training across multiple GPUs. Example VLLM server configuration from `run_react_infer.sh`:

```bash
# 8-GPU setup for inference (similar setup used during training)
CUDA_VISIBLE_DEVICES=0 vllm serve $MODEL_PATH --host 0.0.0.0 --port 6001 &
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_PATH --host 0.0.0.0 --port 6002 &
# ... (6002-6008 for remaining GPUs)

# Distributed training environment variables
WORLD_SIZE=1  # Number of nodes
RANK=0        # Current node rank
```

### NCCL Configuration for Multi-GPU

From `.env.example`, the training setup includes optimized NCCL settings:

```bash
NCCL_IB_TC=16
NCCL_IB_SL=5
NCCL_IB_GID_INDEX=3
NCCL_SOCKET_IFNAME=eth
NCCL_IB_TIMEOUT=22
NCCL_MIN_NCHANNELS=4
```

Sources: [README.md:32](), [README.md:55](), [WebAgent/WebLeaper/README.md:150](), [.env.example:6-20](), [.env.example:36-43](), [inference/run_react_infer.sh:30-37]()

---

## Data Pipeline Implementation

### Tool-Based Trajectory Generation

Trajectories are generated using a ReAct-style agent with two primary tools, following the same architecture used for inference:

1. **Search Tool**: `Search(queries, filter_year)` → web results + snippets (via Serper.dev API)
2. **Visit Tool**: `Visit(urls, goal)` → summarized paragraphs with entity extraction (via Jina.ai API)

**ISE Computation Note**: ISE is computed primarily using entities from `Visit` actions, as entities found in `Search` snippets are often less precise and typically refined by subsequent `Visit` calls.

```mermaid
graph TB
    subgraph "Trajectory Generation Loop"
        Query["Task Query<br/>(n target entities)"]
        Think["Think Step<br/>(ReAct Loop)"]
        Action["Action Generation<br/>(JSON Format)"]
        Execute["Tool Execution"]
    end
    
    subgraph "Tool Layer"
        SearchTool["Search Tool<br/>SERPER_KEY_ID"]
        VisitTool["Visit Tool<br/>JINA_API_KEYS"]
        SerperAPI["Serper.dev API<br/>(Web + Scholar)"]
        JinaAPI["Jina.ai API<br/>(Page Reading)"]
    end
    
    subgraph "Entity Tracking"
        ExtractEntities["Extract Entities<br/>from Visit"]
        CountActions["Count Actions<br/>(T steps)"]
        ComputeMetrics["Compute ISR/ISE<br/>ISR = |R∩O|/|R|<br/>ISE = n/T"]
    end
    
    subgraph "Filtering Decision"
        CheckISR{"ISR > 0.3?"}
        CheckISE{"ISE > 0.1?"}
        AcceptTraj["Accept Trajectory<br/>(Add to SFT Corpus)"]
        RejectTraj["Reject Trajectory"]
    end
    
    Query --> Think
    Think --> Action
    Action --> Execute
    
    Execute --> SearchTool
    Execute --> VisitTool
    SearchTool --> SerperAPI
    VisitTool --> JinaAPI
    
    JinaAPI --> ExtractEntities
    Execute --> CountActions
    
    ExtractEntities --> ComputeMetrics
    CountActions --> ComputeMetrics
    
    ComputeMetrics --> CheckISR
    CheckISR -->|Yes| CheckISE
    CheckISR -->|No| RejectTraj
    CheckISE -->|Yes| AcceptTraj
    CheckISE -->|No| RejectTraj
```

**Figure 7: Trajectory Generation and Filtering Pipeline**

### Configuration Requirements

The trajectory generation process requires API credentials configured in `.env`:

```bash
# Search capability
SERPER_KEY_ID=your_key

# Page reading capability  
JINA_API_KEYS=your_key

# Summarization for Visit tool
API_KEY=your_key
API_BASE=your_api_base
SUMMARY_MODEL_NAME=your_summary_model_name
```

Sources: [WebAgent/WebLeaper/README.md:73-78](), [.env.example:49-61](), [README.md:102-105]()

---

## Training Phases Summary

| Phase | Purpose | Input | Output | Key Metrics |
|-------|---------|-------|--------|-------------|
| **Continual Pre-training** | Extend capabilities, maintain freshness | Base model + Agentic corpus | CPT model | Context length, reasoning performance |
| **Supervised Fine-Tuning** | Learn from high-quality demonstrations | CPT model + Filtered trajectories | SFT model | ISR, ISE, task success rate |
| **Reinforcement Learning** | Optimize policy for task completion | SFT model + On-policy rollouts | Final model | Soft F-score, benchmark scores |

### Continual Pre-training Focus

- Large-scale diverse agentic interaction data
- Extended context window (32K-128K tokens)
- Maintains model freshness
- Strengthens reasoning performance

### SFT Focus

- High ISR (coverage) and ISE (efficiency)
- Balance between entity-intensive and deep-search tasks
- Quality over quantity through strict filtering

### RL Focus

- On-policy trajectory generation
- Hybrid reward system for diverse task types
- Token-level optimization
- Stabilization in non-stationary environments

Sources: [README.md:44-46]()

---

## Integration with Agent Family

The training pipeline leverages innovations from multiple projects in the Deep Research Agent Family:

```mermaid
graph TB
    subgraph "Data Contributions"
        WebLeaper["WebLeaper<br/>Entity-Intensive Data"]
        WebShaper["WebShaper<br/>Formalized Tasks"]
        WebSailor["WebSailor-V2<br/>Deep-Search Data"]
    end
    
    subgraph "Training Methodologies"
        AgentFounder["AgentFounder<br/>Continual Pre-training"]
        AgentScaler["AgentScaler<br/>Environment Scaling"]
    end
    
    subgraph "Capability Extensions"
        ReSum["ReSum<br/>Context Summarization"]
        WebResearcher["WebResearcher<br/>Unbounded Reasoning"]
        WebWeaver["WebWeaver<br/>Evidence Structuring"]
    end
    
    subgraph "Final Model"
        TDR["Tongyi-DeepResearch<br/>30B-A3B"]
    end
    
    WebLeaper --> TDR
    WebShaper --> TDR
    WebSailor --> TDR
    AgentFounder --> TDR
    AgentScaler --> TDR
    ReSum -.-> TDR
    WebResearcher -.-> TDR
    WebWeaver -.-> TDR
```

**Figure 8: Integration with Deep Research Agent Family**

Each project contributes specialized capabilities:
- **WebLeaper**: Training framework and entity-intensive data variants
- **WebShaper**: Information-seeking formalization and data synthesis
- **WebSailor-V2**: Synthetic data generation and scalable RL techniques
- **AgentFounder**: Continual pre-training methodology with extended context
- **AgentScaler**: Principled environment scaling and two-phase fine-tuning

Sources: [README.md:190-210]()

---

