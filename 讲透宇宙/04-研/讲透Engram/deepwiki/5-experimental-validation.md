<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/Engram · page 5 Experimental Validation · fetched 2026-10-30 -->

# Experimental Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Engram_paper.pdf](Engram_paper.pdf)
- [README.md](README.md)
- [figures/27b_exp_results.png](figures/27b_exp_results.png)
- [figures/long_context_results.png](figures/long_context_results.png)
- [figures/scaling_law.png](figures/scaling_law.png)

</details>



This page provides a comprehensive overview of the empirical evidence validating Engram's effectiveness as a conditional memory mechanism for large language models. The experimental validation spans four primary dimensions: (1) performance improvements in the Engram-27B model across multiple domains, (2) scaling behavior to long contexts, (3) optimal capacity allocation between MoE and Engram sparsity axes, and (4) rigorous baseline comparisons under iso-parameter and iso-FLOPs constraints.

For implementation details of the Engram module, see [Implementation Guide](#4). For the theoretical foundation and mechanistic analysis, see [Research Foundation](#7).

---

## Experimental Methodology

The validation strategy employs a multi-faceted approach to establish Engram's effectiveness across different evaluation criteria. The methodology ensures fair comparisons through controlled experimental conditions and comprehensive domain coverage.

```mermaid
graph TB
    subgraph "Research Questions"
        Q1["Q1: Does conditional memory<br/>complement conditional computation?"]
        Q2["Q2: What is optimal<br/>sparsity allocation?"]
        Q3["Q3: Performance across<br/>diverse domains?"]
        Q4["Q4: Scaling to long contexts?"]
    end
    
    subgraph "Experimental Setup"
        MODEL["Engram-27B Model<br/>Base Implementation"]
        CONFIG["EngramConfig<br/>BackBoneConfig"]
        BASELINE["MoE Baselines<br/>Iso-parameter/Iso-FLOPs"]
    end
    
    subgraph "Evaluation Domains"
        KNOWLEDGE["Knowledge Tasks<br/>Factual Retrieval"]
        REASONING["Reasoning Tasks<br/>Complex Inference"]
        CODE["Code Generation<br/>Programming Tasks"]
        MATH["Mathematics<br/>Computational Tasks"]
    end
    
    subgraph "Experimental Results"
        R1["27b_exp_results.png<br/>Domain Performance"]
        R2["long_context_results.png<br/>Context Scaling"]
        R3["scaling_law.png<br/>Capacity Allocation"]
    end
    
    MODEL --> KNOWLEDGE
    MODEL --> REASONING
    MODEL --> CODE
    MODEL --> MATH
    
    CONFIG --> MODEL
    BASELINE --> MODEL
    
    KNOWLEDGE --> R1
    REASONING --> R1
    CODE --> R1
    MATH --> R1
    
    MODEL --> R2
    MODEL --> R3
    
    Q1 -.answered by.-> R1
    Q2 -.answered by.-> R3
    Q3 -.answered by.-> R1
    Q4 -.answered by.-> R2
```

**Sources:** [README.md:30-76](), [Diagram 5 from high-level system architecture]()

---

## Key Experimental Findings

The experimental validation establishes four primary findings that collectively demonstrate Engram's effectiveness as a general-purpose architectural component.

### Finding 1: Consistent Cross-Domain Improvements

The Engram-27B model demonstrates measurable performance improvements over MoE baselines across all evaluated domains under strict iso-parameter and iso-FLOPs constraints. This validates that conditional memory complements conditional computation as a distinct sparsity axis.

| Domain | Evaluation Focus | Key Result |
|--------|------------------|------------|
| Knowledge | Factual retrieval and recall | Improved accuracy on knowledge-intensive benchmarks |
| Reasoning | Complex multi-step inference | Enhanced performance on reasoning tasks |
| Code | Program synthesis and understanding | Better code generation quality |
| Mathematics | Computational problem-solving | Improved mathematical reasoning |

**Sources:** [figures/27b_exp_results.png](), [README.md:36-39]()

### Finding 2: Long-Context Scalability

Engram maintains performance when scaling to extended contexts (16K+ tokens) without degradation, demonstrating that the conditional memory mechanism does not introduce bottlenecks as sequence length increases.

**Sources:** [figures/long_context_results.png](), [README.md:67-71]()

### Finding 3: U-Shaped Capacity Allocation

The scaling law experiments reveal a U-shaped curve governing optimal capacity allocation between MoE neural computation and Engram static memory. This empirically confirms the theoretical prediction that both extreme allocations (all MoE or all Engram) are suboptimal, with peak performance achieved at an intermediate allocation point.

**Sources:** [figures/scaling_law.png](), [README.md:53-57](), [README.md:37]()

### Finding 4: Fair Baseline Comparisons

All comparisons maintain either:
- **Iso-parameter constraints**: Same total number of parameters
- **Iso-FLOPs constraints**: Same computational cost per forward pass

This ensures that observed improvements are attributable to the architectural innovation rather than increased model capacity or computation.

**Sources:** [README.md:38]()

---

## Experimental Pipeline

The following diagram illustrates the complete experimental pipeline from model implementation through evaluation to result generation.

```mermaid
flowchart TB
    subgraph "Model Implementation"
        DEMO["engram_demo_v1.py<br/>Core Implementation"]
        HASH["NgramHashMapping<br/>Deterministic Addressing"]
        EMB["MultiHeadEmbedding<br/>Static Memory Tables"]
        ENGRAM["Engram Module<br/>Fusion Logic"]
    end
    
    subgraph "Training Configuration"
        TRAIN_CFG["Training Parameters<br/>- Layer IDs: [1, 15]<br/>- N-gram sizes<br/>- Vocab compression"]
        MEMORY["N-gram Embeddings<br/>Device Memory (Training)<br/>Host Memory (Inference)"]
        SYNC["All2All Communication<br/>Distributed Training"]
    end
    
    subgraph "Evaluation Framework"
        ISO_PARAM["Iso-parameter Evaluation<br/>Match Total Parameters"]
        ISO_FLOPS["Iso-FLOPs Evaluation<br/>Match Computation Cost"]
        DOMAINS["Domain Benchmarks<br/>Knowledge/Reasoning/Code/Math"]
        CONTEXT["Long Context Tests<br/>2K to 16K+ tokens"]
    end
    
    subgraph "Result Artifacts"
        FIG1["27b_exp_results.png<br/>Cross-domain Performance"]
        FIG2["long_context_results.png<br/>Context Scaling Curves"]
        FIG3["scaling_law.png<br/>Allocation Trade-off"]
    end
    
    DEMO --> HASH
    DEMO --> EMB
    DEMO --> ENGRAM
    
    HASH --> TRAIN_CFG
    EMB --> MEMORY
    ENGRAM --> TRAIN_CFG
    
    TRAIN_CFG --> SYNC
    MEMORY --> SYNC
    
    SYNC --> ISO_PARAM
    SYNC --> ISO_FLOPS
    ISO_PARAM --> DOMAINS
    ISO_FLOPS --> DOMAINS
    ISO_PARAM --> CONTEXT
    
    DOMAINS --> FIG1
    CONTEXT --> FIG2
    ISO_PARAM --> FIG3
    ISO_FLOPS --> FIG3
```

**Sources:** [engram_demo_v1.py](), [README.md:30-76](), [Diagram 3 from high-level system architecture]()

---

## Result Interpretation Framework

Understanding the experimental results requires considering how Engram's architectural properties manifest in different evaluation scenarios.

### Performance Metrics

| Metric Category | Measurement Approach | Significance |
|----------------|----------------------|--------------|
| Domain Accuracy | Task-specific benchmarks | Direct performance comparison |
| Context Handling | Long sequence evaluation | Scalability validation |
| Capacity Efficiency | Iso-parameter/iso-FLOPs | Fair architectural comparison |
| Inference Overhead | Latency measurements | System efficiency |

### Mechanistic Interpretation

The mechanistic analysis suggests that Engram's performance improvements stem from relieving early transformer layers from static pattern reconstruction tasks. By offloading frequently-occurring N-gram patterns to dedicated memory lookup, the neural capacity is preserved for complex reasoning tasks that require dynamic computation.

**Sources:** [README.md:39]()

---

## Experimental Constraints and Controls

All experiments maintain strict controls to ensure validity of comparisons:

### Iso-Parameter Constraints
- Total parameter count held constant across Engram and baseline models
- N-gram embedding table size included in parameter budget
- Fair comparison of architectural efficiency

### Iso-FLOPs Constraints
- Computational cost per forward pass normalized
- Engram lookup operations counted in FLOPs budget
- Ensures performance improvements not due to increased computation

### Training Conditions
- Identical training data distribution
- Same optimization hyperparameters
- Synchronized random seeds for reproducibility

**Sources:** [README.md:38]()

---

## Detailed Sub-Pages

For comprehensive analysis of specific experimental dimensions, refer to the following sub-pages:

- **[Engram-27B Model Results](#5.1)**: Detailed breakdown of performance across knowledge, reasoning, code, and math domains with benchmark-specific analysis.

- **[Long Context Evaluation](#5.2)**: In-depth examination of scaling behavior from 2K to 16K+ token contexts, including perplexity curves and task-specific performance.

- **[Scaling Laws and Optimal Allocation](#5.3)**: Mathematical formulation and empirical validation of the U-shaped scaling law, including derivation of optimal capacity allocation formulas.

- **[Baseline Comparisons](#5.4)**: Comprehensive methodology for iso-parameter and iso-FLOPs evaluations, including detailed baseline model configurations and comparison protocols.

---

## Validation of Key Claims

The experimental results directly validate the key claims presented in the research paper:

```mermaid
graph LR
    subgraph "Theoretical Claims"
        C1["Conditional memory<br/>complements MoE"]
        C2["U-shaped allocation<br/>curve exists"]
        C3["Preserves effective<br/>depth"]
        C4["Scales to long<br/>contexts"]
    end
    
    subgraph "Experimental Evidence"
        E1["27b_exp_results.png<br/>Cross-domain gains"]
        E2["scaling_law.png<br/>Optimal allocation"]
        E3["Mechanistic analysis<br/>Layer utilization"]
        E4["long_context_results.png<br/>16K+ tokens"]
    end
    
    C1 --> E1
    C2 --> E2
    C3 --> E3
    C4 --> E4
```

**Sources:** [README.md:36-40](), [Engram_paper.pdf]()

---

## Reproducibility

The demonstration implementation is provided to facilitate reproducibility:

```bash
python engram_demo_v1.py
```

**Note:** The provided code at [engram_demo_v1.py]() is a demonstration version that mocks standard components (Attention/MoE/mHC) to focus on the Engram module's data flow. For full-scale experiments, refer to the complete implementation described in the paper.

**Sources:** [README.md:78-90]()

---

