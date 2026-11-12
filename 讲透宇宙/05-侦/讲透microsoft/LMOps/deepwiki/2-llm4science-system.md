<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/LMOps · page 2 LLM4Science System · fetched 2026-10-26 -->

# LLM4Science System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LLM4Science/PvsNP_31to36.ipynb](LLM4Science/PvsNP_31to36.ipynb)
- [LLM4Science/PvsNP_7to15.ipynb](LLM4Science/PvsNP_7to15.ipynb)
- [LLM4Science/PvsNP_main.ipynb](LLM4Science/PvsNP_main.ipynb)

</details>



## Purpose and Scope

The LLM4Science System is a research framework designed to explore fundamental mathematical problems, specifically the P vs NP problem, through interactive sessions with large language models. The system facilitates mathematical reasoning and theorem exploration by providing robust LLM integration infrastructure and structured conversation frameworks for investigating constraint satisfaction problems (CSPs), phase transitions, and complexity theory.

For information about the broader LMOps research initiative, see [Overview](#1). For details about the RRM evaluation framework, see [RRM-evaluation System](#3).

## System Architecture

The LLM4Science System consists of three main exploration notebooks that share common infrastructure for LLM interactions and mathematical reasoning:

```mermaid
graph TD
    subgraph "LLM4Science System"
        Main["`PvsNP_main.ipynb`"]
        Exploration1["`PvsNP_7to15.ipynb`"]
        Exploration2["`PvsNP_31to36.ipynb`"]
        
        subgraph "Common Infrastructure"
            GPT4["`gpt4_with_history`"]
            ChatBackoff["`chatcompletions_with_backoff`"]
            CompBackoff["`completions_with_backoff`"]
            Retry["`gptchatcompletion_with_backoff`"]
        end
        
        subgraph "OpenAI Integration"
            APIConfig["OpenAI API Configuration"]
            Azure["Azure OpenAI Service"]
        end
    end
    
    Main --> GPT4
    Exploration1 --> GPT4
    Exploration2 --> GPT4
    
    GPT4 --> ChatBackoff
    ChatBackoff --> Azure
    CompBackoff --> Azure
    Retry --> Azure
    
    Azure --> APIConfig
```

**LLM4Science System Architecture**

The system employs a modular design where each exploration notebook focuses on specific mathematical investigations while sharing robust LLM interaction infrastructure.

Sources: [LLM4Science/PvsNP_main.ipynb:1-93](), [LLM4Science/PvsNP_7to15.ipynb:1-97](), [LLM4Science/PvsNP_31to36.ipynb:1-111]()

## LLM Integration Infrastructure

The core infrastructure provides reliable interaction with GPT-4 through Azure OpenAI services with comprehensive error handling and retry mechanisms:

```mermaid
graph TD
    subgraph "LLM Integration Layer"
        History["`gpt4_with_history`"]
        Batch["Batch Processing Logic"]
        
        subgraph "Error Handling"
            BackoffChat["`chatcompletions_with_backoff`"]
            BackoffComp["`completions_with_backoff`"]
            TenacityRetry["`gptchatcompletion_with_backoff`"]
        end
        
        subgraph "OpenAI Client"
            ChatCompletion["`openai.ChatCompletion.create`"]
            Completion["`openai.Completion.create`"]
        end
        
        subgraph "Configuration"
            APIType["`openai.api_type = 'azure'`"]
            APIBase["`openai.api_base`"]
            APIKey["`openai.api_key`"]
            APIVersion["`openai.api_version`"]
        end
    end
    
    History --> Batch
    Batch --> BackoffChat
    BackoffChat --> ChatCompletion
    TenacityRetry --> ChatCompletion
    BackoffComp --> Completion
    
    ChatCompletion --> APIType
    ChatCompletion --> APIBase
    ChatCompletion --> APIKey
    ChatCompletion --> APIVersion
```

**LLM Integration Infrastructure**

### Core Functions

- **`gpt4_with_history`**: Main interface for GPT-4 interactions with conversation history management
- **`chatcompletions_with_backoff`**: Exponential backoff wrapper for chat completions using the `backoff` library
- **`completions_with_backoff`**: Exponential backoff wrapper for standard completions
- **`gptchatcompletion_with_backoff`**: Advanced retry mechanism using `tenacity` with configurable wait strategies

The retry mechanism implements a sophisticated wait chain: 3 attempts with 3-second delays, followed by 2 attempts with 5-second delays, then 10-second delays for subsequent attempts.

Sources: [LLM4Science/PvsNP_main.ipynb:59-90](), [LLM4Science/PvsNP_7to15.ipynb:64-90](), [LLM4Science/PvsNP_31to36.ipynb:78-104]()

## Mathematical Exploration Components

The system facilitates structured mathematical conversations across three main areas of investigation:

### P vs NP Theoretical Exploration

The main exploration focuses on fundamental complexity theory questions, employing philosophical and mathematical approaches to investigate the P vs NP problem:

```mermaid
graph LR
    subgraph "Philosophical Foundation"
        Phil["`Philosophical Perspective`"]
        Epistem["`Epistemological Questions`"]
        Nature["`Nature of Knowledge`"]
    end
    
    subgraph "Mathematical Approaches"
        Contradiction["`Proof by Contradiction`"]
        Reduction["`Problem Reduction`"]
        Construction["`Problem Construction`"]
    end
    
    subgraph "Target Problems"
        SAT["`Boolean Satisfiability`"]
        CSP["`Constraint Satisfaction`"]
        Clique["`Clique Problem`"]
        TSP["`Traveling Salesman`"]
    end
    
    Phil --> Contradiction
    Epistem --> Reduction
    Nature --> Construction
    
    Contradiction --> SAT
    Reduction --> CSP
    Construction --> Clique
    Construction --> TSP
```

**P vs NP Exploration Framework**

Sources: [LLM4Science/PvsNP_main.ipynb:114-284]()

### CSP Phase Transition Analysis

The system investigates constraint satisfaction problems with focus on phase transitions and symmetry properties:

```mermaid
graph TD
    subgraph "CSP Investigation"
        PhaseTransition["`Phase Transition Analysis`"]
        Symmetries["`Symmetry Exploitation`"]
        Hardness["`Instance Hardness`"]
    end
    
    subgraph "Model RB Framework"
        Variables["`Variables X = {x1, ..., xn}`"]
        Constraints["`Constraints C = {C1, ..., Cm}`"]
        Relations["`Symmetric Relations R*`"]
        Mappings["`Bijection Functions fi`"]
    end
    
    subgraph "Construction Techniques"
        Critical["`Critical Constraints`"]
        Fixed["`Fixed Points`"]
        Transformation["`Satisfiability Transformation`"]
    end
    
    PhaseTransition --> Variables
    Symmetries --> Relations
    Hardness --> Critical
    
    Variables --> Constraints
    Constraints --> Relations
    Relations --> Mappings
    
    Critical --> Fixed
    Fixed --> Transformation
```

**CSP and Model RB Analysis Framework**

Sources: [LLM4Science/PvsNP_7to15.ipynb:102-418](), [LLM4Science/PvsNP_main.ipynb:315-683]()

### Advanced Theorem Proving Strategies

The latest exploration focuses on constructing specific instances of Model RB that exhibit controllable satisfiability properties:

| Exploration Focus | Description | Key Techniques |
|------------------|-------------|----------------|
| **Critical Instances** | Instances with single critical constraints | Non-critical constraint satisfaction |
| **Delicate Balance** | Instances with unique solutions | Tight constraint coupling |
| **Fixed Points** | Sets invariant under transformations | Symmetry preservation |
| **Mapping Operations** | Satisfiability-altering transformations | Value swapping for k=2 cases |

The system explores two primary instance types:
1. **Unsatisfiable to Satisfiable**: Instances with mostly non-critical constraints and one critical constraint dependent on single variable assignment
2. **Satisfiable to Unsatisfiable**: Instances with delicate constraint balance having unique solutions that become unsatisfiable when critical constraints are modified

Sources: [LLM4Science/PvsNP_31to36.ipynb:114-369]()

## Model RB Specification

The system works with an enhanced Model RB definition that incorporates symmetry requirements for generating hard CSP instances:

### Core Model Components

```mermaid
graph TD
    subgraph "Model RB Instance I"
        Variables["`Variables X = {x1, ..., xn}`"]
        Domains["`Domains Di with |Di| = d = n^α`"]
        ConstraintSet["`Constraints C = {C1, ..., Cm}`"]
        Count["`m = rn ln d`"]
    end
    
    subgraph "Symmetric Relation R*"
        GenericDomain["`D* = {1, 2, ..., d}^k`"]
        SymmetryProp["`All permutations included`"]
        Size["`|R*| = (1-p)d^k`"]
    end
    
    subgraph "Constraint Generation"
        RandomVars["`Xi = k distinct variables`"]
        Bijections["`fi_j bijection functions`"]
        PermittedSets["`Ri isomorphic to R*`"]
    end
    
    Variables --> Domains
    Domains --> ConstraintSet
    ConstraintSet --> Count
    
    GenericDomain --> SymmetryProp
    SymmetryProp --> Size
    
    RandomVars --> Bijections
    Bijections --> PermittedSets
    PermittedSets --> Size
```

**Enhanced Model RB Structure**

### Assignment and Satisfiability Definitions

- **Assignment σ**: Function `σ: X → ∪Di` where `σ(xi) ∈ Di` for all variables
- **Constraint Satisfaction**: Constraint `Ci = (Xi, Ri)` satisfied when `(σ(xi1), σ(xi2), ..., σ(xik)) ∈ Ri`
- **Solution**: Assignment satisfying all constraints in set C
- **Satisfiability**: Instance I is satisfiable if solution σ exists

The enhanced model introduces separate bijection functions `fi_j` for each of the first `k-1` variables to increase complexity while preserving constraint symmetry requirements.

Sources: [LLM4Science/PvsNP_main.ipynb:704-717](), [LLM4Science/PvsNP_31to36.ipynb:118-369]()

---

