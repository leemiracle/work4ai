<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Mu-Protein · page 2.3 μSearch System · patched2 2026-10-26 -->

# μSearch System
# μSearch System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of the μSearch system, the third and final stage of the μProtein framework pipeline. μSearch is a reinforcement learning-based protein optimization system that navigates fitness landscapes to discover improved protein variants. It leverages the fitness predictions from μFormer models to efficiently explore the protein sequence space and identify optimized proteins.

For detailed information about the fitness modeling component that feeds into μSearch, see [μFormer Architecture](#2.2). For implementation details of training μSearch systems, see [Training & Development](#4).

## System Overview

μSearch represents the optimization stage of the μProtein framework, where reinforcement learning algorithms are employed to navigate the protein fitness landscape constructed by μFormer. The system takes fitness predictions as an oracle and uses them to guide the search for protein variants with improved properties.

### μSearch Position in Framework Pipeline

```mermaid
flowchart LR
    subgraph "Stage 1"
        PMLM["PMLM Pretraining"]
    end
    
    subgraph "Stage 2"
        MUFORMER["μFormer Fitness Modeling"]
    end
    
    subgraph "Stage 3"
        MUSEARCH["μSearch RL Optimization"]
    end
    
    subgraph "Outputs"
        OPTIMIZED["Optimized Protein Variants"]
    end
    
    PMLM --> MUFORMER
    MUFORMER --> MUSEARCH
    MUSEARCH --> OPTIMIZED
    
    MUSEARCH -.->|"queries fitness"| MUFORMER
    MUFORMER -.->|"returns predictions"| MUSEARCH
```

Sources: [README.md:8-16]()

## Core Components

### Reinforcement Learning Framework

μSearch implements reinforcement learning algorithms specifically designed for protein sequence optimization. The system treats protein engineering as a sequential decision-making problem where each amino acid position represents a decision point in the optimization process.

```mermaid
graph TB
    subgraph "μSearch RL Framework"
        subgraph "Environment"
            FITNESS_ORACLE["Fitness Oracle (μFormer)"]
            PROTEIN_STATE["Protein Sequence State"]
            REWARD_FUNCTION["Fitness-based Rewards"]
        end
        
        subgraph "Agent"
            RL_POLICY["RL Policy Network"]
            ACTION_SPACE["Amino Acid Actions"]
            STATE_REPRESENTATION["Sequence Representation"]
        end
        
        subgraph "Search Strategy"
            EXPLORATION["Exploration Strategy"]
            EXPLOITATION["Exploitation Strategy"]
            TRAJECTORY_SAMPLING["Trajectory Sampling"]
        end
    end
    
    RL_POLICY --> ACTION_SPACE
    ACTION_SPACE --> PROTEIN_STATE
    PROTEIN_STATE --> FITNESS_ORACLE
    FITNESS_ORACLE --> REWARD_FUNCTION
    REWARD_FUNCTION --> RL_POLICY
    
    EXPLORATION --> RL_POLICY
    EXPLOITATION --> RL_POLICY
    TRAJECTORY_SAMPLING --> RL_POLICY
```

Sources: [README.md:8](), [README.md:16]()

### Fitness Landscape Navigation

The system efficiently navigates the high-dimensional protein fitness landscape by leveraging the μFormer predictions as a differentiable oracle. This allows for gradient-based optimization strategies while maintaining the flexibility of reinforcement learning for discrete sequence spaces.

```mermaid
graph TD
    subgraph "Fitness Landscape Navigation"
        subgraph "Input Processing"
            WILD_TYPE["Wild-type Protein Sequence"]
            TARGET_PROPERTIES["Target Fitness Properties"]
            CONSTRAINTS["Optimization Constraints"]
        end
        
        subgraph "Search Process"
            SEQUENCE_GENERATION["Sequence Variant Generation"]
            FITNESS_EVALUATION["μFormer Fitness Evaluation"]
            TRAJECTORY_OPTIMIZATION["RL Trajectory Optimization"]
        end
        
        subgraph "Output Generation"
            CANDIDATE_RANKING["Candidate Variant Ranking"]
            VALIDATION_FILTERING["Validation & Filtering"]
            OPTIMIZED_SEQUENCES["Final Optimized Sequences"]
        end
    end
    
    WILD_TYPE --> SEQUENCE_GENERATION
    TARGET_PROPERTIES --> TRAJECTORY_OPTIMIZATION
    CONSTRAINTS --> VALIDATION_FILTERING
    
    SEQUENCE_GENERATION --> FITNESS_EVALUATION
    FITNESS_EVALUATION --> TRAJECTORY_OPTIMIZATION
    TRAJECTORY_OPTIMIZATION --> CANDIDATE_RANKING
    CANDIDATE_RANKING --> VALIDATION_FILTERING
    VALIDATION_FILTERING --> OPTIMIZED_SEQUENCES
    
    FITNESS_EVALUATION -.->|"queries"| FITNESS_EVALUATION
```

Sources: [README.md:8](), [README.md:16]()

## Integration with μFormer

μSearch relies heavily on the μFormer system to provide accurate fitness predictions that guide the reinforcement learning process. This integration creates a closed-loop optimization system where the quality of fitness modeling directly impacts the effectiveness of the search process.

### Fitness Oracle Interface

```mermaid
sequenceDiagram
    participant MS as "μSearch RL Agent"
    participant MF as "μFormer Fitness Oracle"
    participant PS as "Protein Sequence Space"
    
    MS->>PS: Generate candidate sequence
    MS->>MF: Query fitness prediction
    MF->>MF: Encode sequence features
    MF->>MF: Predict mutational effects
    MF->>MS: Return fitness score
    MS->>MS: Update policy based on reward
    MS->>PS: Select next sequence variant
    
    Note over MS,MF: Iterative optimization loop
```

Sources: [README.md:8](), [README.md:15-16]()

## System Architecture

The μSearch system is organized within the `mu-search/` directory and follows a modular architecture that separates the reinforcement learning components from the protein-specific optimization logic.

### Directory Structure

| Component | Location | Purpose |
|-----------|----------|---------|
| Core RL System | `mu-search/` | Main reinforcement learning implementation |
| Configuration | `mu-search/README.md` | System documentation and setup |
| Integration Layer | Interface with `mu-former/` | Fitness oracle communication |

Sources: [README.md:16](), [README.md:22]()

## Optimization Process

The μSearch optimization process follows a systematic approach to protein engineering that balances exploration of novel sequences with exploitation of promising regions in the fitness landscape.

### Search Algorithm Flow

```mermaid
flowchart TD
    subgraph "Initialization"
        INIT_SEQUENCE["Initialize with wild-type sequence"]
        INIT_POLICY["Initialize RL policy"]
        INIT_ENVIRONMENT["Setup optimization environment"]
    end
    
    subgraph "Optimization Loop"
        POLICY_ACTION["Sample action from policy"]
        SEQUENCE_MUTATE["Apply mutation to sequence"]
        FITNESS_QUERY["Query μFormer for fitness"]
        REWARD_COMPUTE["Compute reward signal"]
        POLICY_UPDATE["Update RL policy"]
        CONVERGENCE_CHECK["Check convergence criteria"]
    end
    
    subgraph "Termination"
        FINAL_RANKING["Rank discovered variants"]
        OUTPUT_RESULTS["Output optimized sequences"]
    end
    
    INIT_SEQUENCE --> INIT_POLICY
    INIT_POLICY --> INIT_ENVIRONMENT
    INIT_ENVIRONMENT --> POLICY_ACTION
    
    POLICY_ACTION --> SEQUENCE_MUTATE
    SEQUENCE_MUTATE --> FITNESS_QUERY
    FITNESS_QUERY --> REWARD_COMPUTE
    REWARD_COMPUTE --> POLICY_UPDATE
    POLICY_UPDATE --> CONVERGENCE_CHECK
    
    CONVERGENCE_CHECK -->|"Continue"| POLICY_ACTION
    CONVERGENCE_CHECK -->|"Converged"| FINAL_RANKING
    
    FINAL_RANKING --> OUTPUT_RESULTS
```

Sources: [README.md:8](), [README.md:16]()

## Performance Characteristics

μSearch is designed to efficiently explore the vast protein sequence space while minimizing the number of fitness evaluations required. The reinforcement learning approach enables the system to learn from previous optimization attempts and progressively improve its search strategy.

### Key Performance Features

- **Sample Efficiency**: Reduces the number of fitness evaluations needed compared to exhaustive search
- **Scalability**: Handles proteins of varying lengths and complexity
- **Adaptability**: Learns optimization strategies specific to different protein families
- **Constraint Handling**: Incorporates biochemical and structural constraints into the search process

Sources: [README.md:8]()

## Future Extensions

The μSearch system provides a foundation for various protein engineering applications and can be extended to support multi-objective optimization, ensemble-based search strategies, and integration with experimental validation pipelines.

Sources: [README.md:8-16]()

---

