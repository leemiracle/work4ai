<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/AI-Researcher · extra page Multi-task Prompting (All-in-One) · fetched 2026-11-09 -->

# Multi-task Prompting (All-in-One)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmark/final/gnn/allinone.json](benchmark/final/gnn/allinone.json)

</details>



## Purpose and Scope

This document details the **All-in-One** benchmark task within the AI-Researcher evaluation framework, which assesses the system's capability to develop multi-task prompting methods for Graph Neural Networks (GNNs). The benchmark evaluates approaches that bridge the gap between pre-trained GNN models and diverse downstream graph tasks (node-level, edge-level, and graph-level) through unified prompting strategies inspired by natural language processing techniques.

For other GNN-related benchmarks, see [Graph Neural Networks](#5.2). For the overall benchmark evaluation framework, see [Benchmark System (Inno-Bench)](#3.3).

**Sources:** [benchmark/final/gnn/allinone.json:1-96]()

## Research Problem Overview

### Problem Domain

The All-in-One benchmark addresses a fundamental challenge in graph neural network research: the incompatibility between pre-training objectives and diverse downstream graph tasks. Traditional "pre-training and fine-tuning" workflows often result in **negative transfer**, where the pre-trained model performs poorly on target tasks due to misalignment between pretext tasks and application requirements.

The research tackles three primary challenges:

1. **Task Diversity Gap**: GNN tasks span node classification, edge prediction, and graph classification—each requiring different model outputs and optimization objectives
2. **Pre-training Incompatibility**: Binary edge prediction (common pre-training task) is structurally incompatible with node-level or graph-level downstream tasks
3. **Prompt Design Complexity**: Unlike text-based prompting in NLP, graph prompting must account for complex structural relationships and variable graph topologies

**Sources:** [benchmark/final/gnn/allinone.json:88-96]()

### Theoretical Foundation

```mermaid
graph TB
    subgraph "NLP Prompting Paradigm"
        NLP_PT["Pre-trained LM"]
        NLP_PROMPT["Text Prompts<br/>(Token Sequences)"]
        NLP_TASK["Unified Task Format"]
    end
    
    subgraph "Graph Prompting Challenge"
        GNN_PT["Pre-trained GNN"]
        GRAPH_STRUCT["Graph Structure<br/>(Nodes & Edges)"]
        NODE_TASK["Node-level Tasks"]
        EDGE_TASK["Edge-level Tasks"]
        GRAPH_TASK["Graph-level Tasks"]
    end
    
    subgraph "All-in-One Solution"
        PROMPT_GRAPH["Prompt Graph G_p<br/>(P tokens + structure)"]
        TASK_REFORM["Task Reformulation<br/>(τ-hop induced graphs)"]
        META_LEARN["Meta-learning<br/>(Prompt Initialization)"]
        UNIFIED["Unified Graph-level<br/>Task Format"]
    end
    
    NLP_PT --> NLP_PROMPT
    NLP_PROMPT --> NLP_TASK
    
    GNN_PT --> GRAPH_STRUCT
    GRAPH_STRUCT --> NODE_TASK
    GRAPH_STRUCT --> EDGE_TASK
    GRAPH_STRUCT --> GRAPH_TASK
    
    NODE_TASK --> TASK_REFORM
    EDGE_TASK --> TASK_REFORM
    GRAPH_TASK --> UNIFIED
    TASK_REFORM --> UNIFIED
    
    GNN_PT --> PROMPT_GRAPH
    PROMPT_GRAPH --> UNIFIED
    META_LEARN --> PROMPT_GRAPH
    
    NLP_PROMPT -.->|"Inspiration"| PROMPT_GRAPH
```

**Diagram: Conceptual Bridge from NLP Prompting to Graph Multi-task Framework**

The methodology adapts three key concepts from NLP prompting:
- **Prompt Tokens**: Learnable token sequences inserted into the input
- **Token Structure**: Relationships between prompt tokens
- **Inserting Patterns**: Methods for integrating prompts with original data

**Sources:** [benchmark/final/gnn/allinone.json:4-76]()

## Methodology Architecture

### Three-Component Framework

```mermaid
graph TB
    subgraph "Input Processing"
        ORIG_GRAPH["Original Graph G<br/>(V nodes, E edges, X features)"]
        TASK_TYPE["Task Type<br/>(node/edge/graph)"]
    end
    
    subgraph "Component 1: Prompt Graph Design"
        PROMPT_TOKENS["Prompt Tokens P<br/>|P| << N learnable vectors"]
        TOKEN_STRUCT["Token Structure<br/>(connections between tokens)"]
        INSERT_PATTERN["Inserting Pattern<br/>(integration function)"]
        
        PROMPT_TOKENS --> PROMPT_GRAPH_GP["Prompt Graph G_p"]
        TOKEN_STRUCT --> PROMPT_GRAPH_GP
        INSERT_PATTERN --> PROMPT_GRAPH_GP
    end
    
    subgraph "Component 2: Task Reformulation"
        NODE_TO_GRAPH["Node Task → τ-hop Induced Graph"]
        EDGE_TO_GRAPH["Edge Task → τ-hop Induced Graph"]
        GRAPH_KEEP["Graph Task → Keep Original"]
        
        REFORMED_GRAPH["Reformed Graph-level Task"]
    end
    
    subgraph "Component 3: Meta-Learning"
        META_INIT["Meta-learning Initialization"]
        TASK_BATCH["Multi-task Batch<br/>(support + query sets)"]
        ADAPT_PROMPT["Adaptive Prompt Update"]
    end
    
    subgraph "GNN Processing"
        MERGED_GRAPH["Merged Graph<br/>(G + G_p)"]
        PRETRAINED_GNN["Pre-trained GNN Encoder"]
        TASK_HEAD["Task-specific Head"]
    end
    
    ORIG_GRAPH --> NODE_TO_GRAPH
    ORIG_GRAPH --> EDGE_TO_GRAPH
    ORIG_GRAPH --> GRAPH_KEEP
    TASK_TYPE --> NODE_TO_GRAPH
    TASK_TYPE --> EDGE_TO_GRAPH
    
    NODE_TO_GRAPH --> REFORMED_GRAPH
    EDGE_TO_GRAPH --> REFORMED_GRAPH
    GRAPH_KEEP --> REFORMED_GRAPH
    
    REFORMED_GRAPH --> MERGED_GRAPH
    PROMPT_GRAPH_GP --> MERGED_GRAPH
    
    META_INIT --> PROMPT_TOKENS
    TASK_BATCH --> META_INIT
    ADAPT_PROMPT --> PROMPT_TOKENS
    
    MERGED_GRAPH --> PRETRAINED_GNN
    PRETRAINED_GNN --> TASK_HEAD
    TASK_HEAD --> OUTPUT["Task Predictions"]
```

**Diagram: All-in-One Multi-task Prompting Pipeline**

**Sources:** [benchmark/final/gnn/allinone.json:94-95]()

## Prompt Graph Design

### Component Structure

The prompt graph `G_p = (P, E_p, X_p)` consists of three learnable components that modify the original graph without altering the pre-trained GNN architecture.

#### Prompt Tokens

Prompt tokens are learnable node feature vectors added to the graph:

| Parameter | Description | Typical Value | Constraint |
|-----------|-------------|---------------|------------|
| `P` | Set of prompt tokens | 10 tokens | \|P\| << N (much smaller than node count) |
| `X_p` | Token feature vectors | Same dimension as node features | Initialized randomly or via meta-learning |
| Optimization | Updated via backpropagation | Adam optimizer | Learning rate: 0.001 |

The small size of the prompt set ensures computational efficiency and prevents overfitting to specific graph structures.

**Sources:** [benchmark/final/gnn/allinone.json:94]()

#### Token Structure

Token structure defines connections `E_p` between prompt tokens, enabling information flow within the prompt graph:

**Method 1: Tunable Binary Connections**
```
E_p = {(p_i, p_j) | A_ij = 1, where A is learnable adjacency matrix}
```

**Method 2: Dot-Product Threshold**
```
E_p = {(p_i, p_j) | x_i^T · x_j > θ, where θ is threshold}
```

The second method reduces parameters by computing connections dynamically from token features, pruning weak relationships to maintain sparsity.

**Sources:** [benchmark/final/gnn/allinone.json:94]()

#### Inserting Patterns

The inserting function `φ: G × G_p → G'` merges prompt tokens into the original graph:

**Pattern 1: Feature Addition**
```
For each node v ∈ V:
  x_v' = x_v + Σ_{p∈P} α_vp · x_p
  where α_vp is learned attention weight
```

**Pattern 2: Structural Augmentation**
```
G' = (V ∪ P, E ∪ E_p ∪ E_cross, X ∪ X_p)
where E_cross connects original nodes to prompt tokens
```

The choice of pattern depends on whether the downstream task requires explicit structural modifications or feature-space adjustments.

**Sources:** [benchmark/final/gnn/allinone.json:94]()

### Prompt Design Trade-offs

```mermaid
graph LR
    subgraph "Design Choices"
        SMALL_P["Small |P|<br/>(e.g., 10 tokens)"]
        LARGE_P["Large |P|<br/>(e.g., 100 tokens)"]
        
        BINARY_STRUCT["Binary Structure<br/>(sparse connections)"]
        DENSE_STRUCT["Dense Structure<br/>(full connections)"]
        
        FEATURE_INSERT["Feature Insertion<br/>(additive)"]
        STRUCT_INSERT["Structural Insertion<br/>(augmentative)"]
    end
    
    subgraph "Impacts"
        EFFICIENCY["Computational Efficiency"]
        EXPRESSIVENESS["Model Expressiveness"]
        GENERALIZATION["Cross-task Generalization"]
        OVERFITTING["Overfitting Risk"]
    end
    
    SMALL_P -->|"Improves"| EFFICIENCY
    SMALL_P -->|"Reduces"| EXPRESSIVENESS
    SMALL_P -->|"Enhances"| GENERALIZATION
    
    LARGE_P -->|"Increases"| EXPRESSIVENESS
    LARGE_P -->|"Raises"| OVERFITTING
    
    BINARY_STRUCT -->|"Maintains"| EFFICIENCY
    DENSE_STRUCT -->|"Increases"| EXPRESSIVENESS
    
    FEATURE_INSERT -->|"Preserves"| EFFICIENCY
    STRUCT_INSERT -->|"Modifies"| EXPRESSIVENESS
```

**Diagram: Prompt Design Trade-off Analysis**

**Sources:** [benchmark/final/gnn/allinone.json:94]()

## Task Reformulation Strategy

### Induced Graph Construction

To unify diverse graph tasks into a single graph-level format, the methodology constructs τ-hop induced subgraphs centered on target entities:

**Node-level Task Reformulation:**
```
For node classification on node v:
  1. Extract τ-hop neighborhood: N_τ(v) = {u | dist(u,v) ≤ τ}
  2. Create induced subgraph: G_v = (N_τ(v), E_v, X_v)
  3. Apply graph-level classification head to G_v
```

**Edge-level Task Reformulation:**
```
For edge prediction on edge (u,v):
  1. Extract τ-hop neighborhoods: N_τ(u) ∪ N_τ(v)
  2. Create induced subgraph: G_uv connecting both neighborhoods
  3. Apply graph-level classification head to G_uv
```

**Graph-level Tasks:**
Maintain original graph structure without modification.

### Parameter Configuration

| Parameter | Description | Typical Values | Impact |
|-----------|-------------|----------------|--------|
| `τ` | Neighborhood hop distance | 1-3 | Controls subgraph size and receptive field |
| Subgraph size | Number of nodes in induced graph | 10-100 | Affects computational cost |
| Overlap handling | How to manage overlapping subgraphs | Batch independently | Enables parallel processing |

Setting `τ = 1` captures immediate neighbors (first-order connections), while `τ = 2` includes second-order relationships. Larger values increase computational cost but may capture more relevant context.

**Sources:** [benchmark/final/gnn/allinone.json:94]()

### Task Reformulation Pipeline

```mermaid
graph TB
    subgraph "Original Task Formats"
        NODE_CLASS["Node Classification<br/>Input: node v<br/>Output: class label"]
        EDGE_PRED["Edge Prediction<br/>Input: node pair (u,v)<br/>Output: edge probability"]
        GRAPH_CLASS["Graph Classification<br/>Input: graph G<br/>Output: graph label"]
    end
    
    subgraph "Reformulation Process"
        EXTRACT_NEIGHBORHOOD["Extract τ-hop Neighborhood<br/>N_τ(v) or N_τ(u) ∪ N_τ(v)"]
        BUILD_SUBGRAPH["Build Induced Subgraph<br/>G_induced = (V_sub, E_sub, X_sub)"]
        APPLY_PROMPT["Apply Prompt Graph<br/>G' = φ(G_induced, G_p)"]
    end
    
    subgraph "Unified Format"
        GRAPH_LEVEL_TASK["Graph-level Task<br/>Input: subgraph G'<br/>Output: label"]
        GNN_ENCODER["Pre-trained GNN<br/>Processes G' → embedding"]
        READOUT["Graph Readout<br/>(sum/mean/max pooling)"]
        CLASSIFIER["Classification Head<br/>MLP or linear layer"]
    end
    
    NODE_CLASS --> EXTRACT_NEIGHBORHOOD
    EDGE_PRED --> EXTRACT_NEIGHBORHOOD
    GRAPH_CLASS --> APPLY_PROMPT
    
    EXTRACT_NEIGHBORHOOD --> BUILD_SUBGRAPH
    BUILD_SUBGRAPH --> APPLY_PROMPT
    
    APPLY_PROMPT --> GRAPH_LEVEL_TASK
    GRAPH_LEVEL_TASK --> GNN_ENCODER
    GNN_ENCODER --> READOUT
    READOUT --> CLASSIFIER
    CLASSIFIER --> PREDICTIONS["Unified Predictions"]
```

**Diagram: Task Reformulation to Unified Graph-level Format**

**Sources:** [benchmark/final/gnn/allinone.json:94-95]()

## Meta-Learning Integration

### Objective and Strategy

The meta-learning component addresses the challenge of finding effective prompt initializations that generalize across multiple graph tasks. Unlike task-specific fine-tuning, meta-learning discovers initialization parameters that enable rapid adaptation to new tasks with minimal examples.

**Meta-Learning Objective:**
```
min_θ Σ_T∈Tasks L_T(θ')
where θ' = θ - α∇_θ L_T^support(θ)
```

The objective optimizes for prompt parameters `θ` that, after one or few gradient steps on a task's support set, perform well on the task's query set.

### Meta-Learning Algorithm Structure

```mermaid
graph TB
    subgraph "Meta-Training Phase"
        TASK_SAMPLE["Sample Task Batch<br/>{T_1, T_2, ..., T_k}"]
        INIT_PROMPT["Initialize Prompt θ<br/>(random or learned)"]
        
        subgraph "Inner Loop (Per Task)"
            SUPPORT_SET["Support Set<br/>Few labeled examples"]
            ADAPT_STEP["Adaptation Step<br/>θ_i' = θ - α∇L_support(θ)"]
            QUERY_SET["Query Set<br/>Evaluation examples"]
            TASK_LOSS["Compute L_query(θ_i')"]
        end
        
        META_UPDATE["Meta-Update<br/>θ ← θ - β∇_θ Σ L_query(θ_i')"]
    end
    
    subgraph "Meta-Testing Phase"
        NEW_TASK["New Downstream Task"]
        ADAPTED_PROMPT["Adapt Prompt<br/>θ* = θ - α∇L_support(θ)"]
        FINAL_PRED["Final Predictions"]
    end
    
    TASK_SAMPLE --> INIT_PROMPT
    INIT_PROMPT --> SUPPORT_SET
    SUPPORT_SET --> ADAPT_STEP
    ADAPT_STEP --> QUERY_SET
    QUERY_SET --> TASK_LOSS
    TASK_LOSS --> META_UPDATE
    META_UPDATE -.->|"Iterate"| TASK_SAMPLE
    
    META_UPDATE --> NEW_TASK
    NEW_TASK --> ADAPTED_PROMPT
    ADAPTED_PROMPT --> FINAL_PRED
```

**Diagram: Meta-Learning Training and Deployment Pipeline**

### Hyperparameter Configuration

| Parameter | Description | Typical Value | Purpose |
|-----------|-------------|---------------|---------|
| `α` | Inner loop learning rate | 0.01 | Controls task-specific adaptation speed |
| `β` | Meta learning rate | 0.001 | Controls meta-parameter update magnitude |
| Support set size | Training examples per task | 5-20 samples | Determines few-shot capability |
| Query set size | Evaluation examples per task | 15-50 samples | Measures generalization |
| Task batch size `k` | Number of tasks per meta-batch | 4-16 tasks | Balances diversity and efficiency |

**Sources:** [benchmark/final/gnn/allinone.json:94]()

## Implementation Specifications

### Core Algorithm Flow

The complete implementation follows this sequence:

**Step 1: Graph Preprocessing**
```
Input: Original graph G = (V, E, X), task type
Process:
  - Normalize node features X
  - Apply task reformulation (if node/edge task)
  - Extract induced subgraphs with τ-hop neighborhoods
Output: Reformed graph G_reformed
```

**Step 2: Prompt Graph Construction**
```
Initialize:
  - Prompt tokens P with |P| = 10
  - Token features X_p ∈ R^{|P| × d} (d = feature dimension)
  - Token structure E_p (binary or threshold-based)
Process:
  - If meta-learned: Load θ_meta as initialization
  - Else: Random initialization with Xavier/Kaiming
Output: Prompt graph G_p = (P, E_p, X_p)
```

**Step 3: Graph Merging**
```
Input: G_reformed, G_p, inserting pattern φ
Process:
  - Apply φ to merge graphs: G' = φ(G_reformed, G_p)
  - Maintain node feature dimensions
  - Create cross-connections between original and prompt nodes
Output: Augmented graph G'
```

**Step 4: GNN Forward Pass**
```
Input: G', pre-trained GNN encoder
Process:
  - Pass G' through L-layer GNN
  - Apply message passing: h^(l+1) = σ(Â h^(l) W^(l))
  - Readout graph representation: h_G = READOUT({h_v | v ∈ V})
Output: Graph embedding h_G
```

**Step 5: Task Prediction**
```
Input: h_G, task-specific head
Process:
  - Apply classifier: y_pred = softmax(W_task h_G + b_task)
Output: Predictions y_pred
```

### Critical Implementation Details

**1. Computational Efficiency**
- Prompt token count must satisfy `|P| << |V|` to avoid memory overhead
- Use sparse attention mechanisms for token structure computation
- Batch multiple induced subgraphs for parallel processing

**2. Initialization Strategies**
- Poor prompt initialization significantly degrades performance
- Meta-learning provides robust initialization across tasks
- Alternative: Pre-train prompts on auxiliary graph tasks

**3. Integration with Pre-trained Models**
- Freeze pre-trained GNN parameters during prompt tuning
- Only update prompt parameters `θ = {X_p, E_p, φ_params}`
- Prevents catastrophic forgetting of pre-trained knowledge

**Sources:** [benchmark/final/gnn/allinone.json:94]()

### Input/Output Specifications

| Component | Input Format | Output Format | Dimensions |
|-----------|--------------|---------------|------------|
| **Original Graph** | Node features: `X ∈ R^{N×d}`<br/>Adjacency: `A ∈ {0,1}^{N×N}` | - | N nodes, d features |
| **Prompt Tokens** | Learned vectors: `X_p ∈ R^{|P|×d}` | - | |P| tokens (e.g., 10) |
| **Reformed Graph** | Induced subgraphs: `{G_1, G_2, ...}` | - | Variable size per task |
| **GNN Encoder** | Augmented graph `G'` | Node embeddings: `H ∈ R^{N×h}` | h = hidden dimension |
| **Readout Layer** | Node embeddings `H` | Graph embedding: `h_G ∈ R^h` | Single vector |
| **Classifier** | Graph embedding `h_G` | Probabilities: `y ∈ R^C` | C classes |

**Sources:** [benchmark/final/gnn/allinone.json:94]()

## Benchmark Configuration

### Task Definition Structure

The benchmark is defined in the configuration file with the following structure:

```mermaid
graph TB
    subgraph "allinone.json Configuration"
        TARGET["target:<br/>All in One: Multi-task Prompting for GNNs"]
        INSTANCE["instance_id: allinone"]
        
        subgraph "Source Papers"
            P1["Prompt Tuning for GNNs<br/>(rank 1, methodological)"]
            P2["Few-shot Learners<br/>(rank 2, conceptual)"]
            P3["Pre-training GNN Strategies<br/>(rank 3, methodological)"]
            P4["Graph Attention Networks<br/>(rank 4, methodological)"]
            P5["GCN Semi-supervised<br/>(rank 5, methodological)"]
            P6["Graph Contrastive Learning<br/>(rank 6, methodological)"]
            P7["Pre-trained LM Few-shot<br/>(rank 7, conceptual)"]
            P8["Graph Pre-training & Prompting<br/>(rank 8, component)"]
        end
        
        META["Metadata:<br/>authors, year, venue, citations"]
        TASKS["Task Definitions:<br/>task1 (implementation)<br/>task2 (research objectives)"]
    end
    
    TARGET --> INSTANCE
    INSTANCE --> P1
    INSTANCE --> P2
    INSTANCE --> P3
    INSTANCE --> P4
    INSTANCE --> P5
    INSTANCE --> P6
    INSTANCE --> P7
    INSTANCE --> P8
    INSTANCE --> META
    INSTANCE --> TASKS
    
    P1 -.->|"Primary methodology"| TASKS
    P2 -.->|"Conceptual inspiration"| TASKS
```

**Diagram: Benchmark Configuration Structure in allinone.json**

### Reference Paper Hierarchy

The benchmark defines 8 source papers ranked by relevance:

| Rank | Reference | Type | Role |
|------|-----------|------|------|
| 1 | Prompt Tuning for Graph Neural Networks | Methodological | Foundational prompt tuning principles for GNNs |
| 2 | Language models are few-shot learners | Conceptual | Inspiration for few-shot learning adaptation |
| 3 | Strategies For Pre-training GNNs | Methodological | Pre-training strategies integration |
| 4 | Graph Attention Networks | Methodological | Graph learning mechanisms |
| 5 | Semi-supervised classification with GCN | Methodological | Semi-supervised learning foundation |
| 6 | Graph contrastive learning with augmentations | Methodological | Contrastive learning methods |
| 7 | Making Pre-trained LMs Better Few-shot Learners | Conceptual | Few-shot prompting strategies |
| 8 | Graph pre-training and prompt tuning | Component | Direct integration strategy |

**Sources:** [benchmark/final/gnn/allinone.json:4-76]()

### Task Level Definitions

The benchmark specifies two task levels for AI-Researcher evaluation:

**Task 1: Implementation Focus (Level 1)**
- **Objective**: Implement the complete multi-task prompting methodology
- **Requirements**:
  - Prompt graph design with learnable tokens, structure, and inserting patterns
  - Task reformulation to graph-level format using τ-hop neighborhoods
  - Meta-learning integration for adaptive prompt initialization
- **Key Parameters**:
  - Prompt token count: `|P| = 10`
  - Neighborhood size: `τ = 1` (immediate neighbors)
  - Learning rate: `0.001` with Adam optimizer
- **Expected Outputs**: Model predictions for node/edge/graph classification tasks

**Task 2: Research Objectives (Level 2)**
- **Problem Domain**: Multi-task learning for diverse graph tasks
- **Core Challenges**:
  - Bridging gap between pre-training and downstream tasks
  - Designing effective graph prompting mechanisms
  - Learning robust prompt initializations
- **Intended Contributions**:
  - Unified prompting framework for graph tasks
  - Task reformulation strategy for compatibility
  - Meta-learning for multi-task generalization

**Sources:** [benchmark/final/gnn/allinone.json:94-96]()

## Evaluation Framework

### Publication Metadata

| Attribute | Value |
|-----------|-------|
| **Authors** | Xiangguo Sun, Hong Cheng, Jia Li, Bo Liu, Jihong Guan |
| **Year** | 2023 |
| **Venue** | Knowledge Discovery and Data Mining (KDD) |
| **Citations** | 86 |
| **URL** | http://arxiv.org/abs/2307.01504v2 |
| **Field** | Graph Neural Networks |
| **Topic** | Graph Neural Networks for NLP |

**Sources:** [benchmark/final/gnn/allinone.json:78-93]()

### Evaluation Dimensions

The AI-Researcher system evaluates generated research against expert-level implementations across five dimensions:

1. **Novelty**: Innovation in prompt design and multi-task adaptation strategies
2. **Experimental Rigor**: Comprehensiveness of task reformulation and meta-learning evaluation
3. **Theoretical Foundation**: Mathematical grounding of prompt graphs and meta-optimization
4. **Result Analysis**: Quality of performance analysis across diverse graph tasks
5. **Writing Quality**: Clarity and structure of technical exposition

For detailed information about the evaluation framework, see [Benchmark System (Inno-Bench)](#3.3).

**Sources:** [benchmark/final/gnn/allinone.json:1-96]()

### Key Innovation Assessment Criteria

The benchmark specifically evaluates AI-Researcher's ability to:

- **Unify Task Formats**: Successfully reformulate node/edge/graph tasks into unified format
- **Design Effective Prompts**: Create prompt graphs that enhance pre-trained model performance
- **Implement Meta-Learning**: Apply meta-learning for robust cross-task generalization
- **Bridge NLP Concepts**: Adapt NLP prompting principles to graph-structured data
- **Maintain Efficiency**: Keep computational overhead minimal (|P| << N constraint)

**Sources:** [benchmark/final/gnn/allinone.json:88-96]()

---

