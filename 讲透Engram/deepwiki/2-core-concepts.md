> 来源: [https://deepwiki.com/deepseek-ai/Engram/2-core-concepts](https://deepwiki.com/deepseek-ai/Engram/2-core-concepts)
> DeepWiki deepseek-ai/Engram

# Core Concepts

  Relevant source files 
 - [Engram_paper.pdf](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/Engram_paper.pdf)
 - [README.md](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1)
 - [figures/arch.png](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/figures/arch.png)
 
  
## Purpose and Scope

 This document explains the fundamental architectural concepts that underpin the Engram system: how it introduces **conditional memory** as a new sparsity axis for Large Language Models, how it achieves efficient knowledge lookup through N-gram embeddings, and how to optimally allocate model capacity between neural computation and static memory.

 For implementation details of these concepts, see [Implementation Guide](https://deepwiki.com/deepseek-ai/Engram/4-implementation-guide). For architectural integration patterns, see [Architecture](https://deepwiki.com/deepseek-ai/Engram/3-architecture). For experimental validation of these concepts, see [Experimental Validation](https://deepwiki.com/deepseek-ai/Engram/5-experimental-validation).

 
---

 
## Overview: The Dual Sparsity Paradigm

 Engram introduces a fundamental shift in how Large Language Models allocate computational resources. While traditional Mixture-of-Experts (MoE) architectures provide **conditional computation** (activating different neural pathways based on input), they lack a native mechanism for efficient **conditional memory** (retrieving static knowledge patterns). Engram addresses this gap by treating memory as a complementary sparsity axis.

 
```

```

 **Figure 1: Traditional vs. Engram-Augmented LLM Architecture**

 The core insight is that these two sparsity axes—conditional computation and conditional memory—are complementary and have an optimal allocation point. Engram enables models to offload static pattern matching to deterministic memory lookup, preserving neural capacity for dynamic reasoning tasks.

 **Sources:** [README.md32-40](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1#L32-L40) [Engram_paper.pdf1-300](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/Engram_paper.pdf#L1-L300)

 
---

 
## Conditional Memory vs Conditional Computation

 
### The Complementary Sparsity Axes

 Modern LLMs face a fundamental capacity bottleneck: all knowledge must be encoded in neural parameters. MoE addresses this by conditionally activating subsets of parameters, but this remains purely computational—no mechanism exists for direct knowledge retrieval. Engram introduces conditional memory as a second, orthogonal axis of sparsity.

 
```

```

 **Figure 2: Characteristics of Dual Sparsity Axes**

 
### Code Implementation Mapping

 The dual sparsity architecture manifests in the codebase through distinct component hierarchies:

 
| Sparsity Axis | Core Components | Key Characteristics | Code Reference |
|---|---|---|---|
| Conditional Computation (MoE) | TransformerBlock with MoE layers | Dynamically routes inputs to expert subnetworks | Mock implementation in demo |
| Conditional Memory (Engram) | Engram, NgramHashMapping, MultiHeadEmbedding | Deterministically retrieves N-gram embeddings | engram_demo_v1.py238-285 |

 The integration point occurs within `TransformerBlock`, where specific layers conditionally apply the Engram module:

 
```

```

 **Figure 3: Selective Layer Integration in TransformerBlock**

 The selective integration is controlled by `EngramConfig.engram_layer_ids`, which specifies which transformer layers receive Engram augmentation. This design preserves most layers as standard transformers while strategically inserting memory lookup at specific depths.

 **Sources:** [README.md34-35](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1#L34-L35) [engram_demo_v1.py25-40](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L25-L40) [engram_demo_v1.py287-298](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L287-L298)

 
---

 
## N-gram Embeddings and Scalable Lookup

 
### Static Knowledge Representation

 Engram stores static knowledge as multi-scale N-gram embeddings—dense vector representations of token sequences. Unlike traditional N-gram models that store discrete counts, Engram uses learnable embeddings that can be updated during training and efficiently retrieved during inference.

 
```

```

 **Figure 4: N-gram Embedding Pipeline**

 
### Deterministic Addressing via Hashing

 The efficiency of Engram's lookup mechanism relies on `NgramHashMapping`, which converts token sequences into deterministic hash addresses. This enables O(1) retrieval complexity regardless of vocabulary size.

 **Hash Function Implementation:**

 The core hashing logic in [engram_demo_v1.py45-90](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L45-L90) implements:

 
 - **Vocabulary Compression:** `CompressedTokenizer` reduces the effective vocabulary through normalization and deduplication
 - **N-gram Construction:** Generates multi-scale N-gram sequences from compressed tokens
 - **Layer-Specific Hashing:** Applies XOR mixing with layer ID to create unique hash spaces per transformer layer
 - **Prime Modulo:** Uses prime number vocabulary sizes to minimize hash collisions
 
 
```

```

 **Figure 5: Hash Addressing Components**

 
### Multi-Head Embedding Architecture

 The `MultiHeadEmbedding` class [engram_demo_v1.py144-167](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L144-L167) manages multiple vocabulary sizes efficiently using a single `nn.Embedding` layer with offset management:

 
| Component | Purpose | Configuration Parameter |
|---|---|---|
| CompressedTokenizer | Reduces vocabulary size | EngramConfig.compressed_vocab_size |
| NgramHashMapping | Generates hash addresses | EngramConfig.ngram_vocab_sizes (list of sizes for different N-grams) |
| MultiHeadEmbedding | Stores embedding tables | EngramConfig.ngram_embed_dim |

 The offset-based design allows a single embedding matrix to serve multiple N-gram vocabularies by partitioning address spaces.

 **Sources:** [README.md34](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1#L34-L34) [engram_demo_v1.py45-90](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L45-L90) [engram_demo_v1.py144-167](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L144-L167)

 
---

 
## Sparsity Allocation and U-Shaped Scaling Law

 
### The Capacity Trade-off

 A fundamental question in Engram's design is: **How should model capacity be allocated between neural computation (MoE) and static memory (Engram)?** Empirical investigation reveals a U-shaped scaling law governing this trade-off.

 
```

```

 **Figure 6: U-Shaped Scaling Law Conceptual Framework**

 
### Experimental Validation

 The U-shaped relationship is validated through systematic capacity sweeps under iso-parameter constraints, as shown in [figures/scaling_law.png](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/figures/scaling_law.png) The experimental setup varies:

 
 - **X-axis:** Ratio of capacity allocated to Engram vs. MoE
 - **Y-axis:** Model performance across evaluation benchmarks
 - **Controls:** Total parameter count and FLOPs held constant
 
 **Key Finding:** Pure MoE (left extreme) and pure Engram (right extreme) both underperform relative to balanced allocations. The optimal point typically occurs when ~20-30% of additional capacity is allocated to Engram, with the remainder in MoE experts.

 
### Configuration Parameters for Allocation

 The capacity allocation is controlled through configuration parameters:

 
```

```

 **Figure 7: Configuration Parameters Controlling Capacity Allocation**

 
### Mechanistic Interpretation

 The U-shaped curve reflects a fundamental trade-off:

 
 - **Too much MoE (left side):** Model wastes neural capacity reconstructing static patterns that could be directly retrieved
 - **Too much Engram (right side):** Model lacks sufficient dynamic computational capacity for complex reasoning and context-dependent tasks
 - **Optimal balance (center):** Static patterns handled by memory retrieval, preserving neural capacity for dynamic reasoning
 
 This mechanistic interpretation is further explored in [Research Foundation](https://deepwiki.com/deepseek-ai/Engram/7-research-foundation), which analyzes how Engram relieves early layers from static pattern reconstruction, preserving effective network depth.

 **Sources:** [README.md36-39](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1#L36-L39) [figures/scaling_law.png](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/figures/scaling_law.png) [engram_demo_v1.py25-40](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L25-L40)

 
---

 
## Implementation Architecture Overview

 The following diagram maps the core concepts to their concrete implementations in the codebase:

 
```

```

 **Figure 8: Concept-to-Code Mapping**

 This architecture enables the dual sparsity paradigm while maintaining clean separation of concerns. The `Engram` module encapsulates all memory lookup logic, the `NgramHashMapping` handles addressing, and configuration parameters control the allocation between conditional computation and conditional memory.

 **Sources:** [engram_demo_v1.py1-300](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L1-L300) [README.md43-50](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1#L43-L50)

 
---

 
## Summary

 The core concepts of Engram establish a new architectural paradigm for LLMs:

 
 - **Dual Sparsity:** Conditional memory (Engram) complements conditional computation (MoE) as orthogonal scaling axes
 - **Efficient Lookup:** N-gram embeddings with deterministic hashing enable O(1) memory retrieval without learned routing
 - **Optimal Allocation:** A U-shaped scaling law guides capacity distribution between neural parameters and static memory
 
 These concepts are realized through a modular implementation that integrates seamlessly with standard transformer architectures while maintaining clear separation between dynamic computation and static knowledge retrieval.

 For deeper understanding of the implementation details, see [Implementation Guide](https://deepwiki.com/deepseek-ai/Engram/4-implementation-guide). For architectural patterns and data flow, see [Architecture](https://deepwiki.com/deepseek-ai/Engram/3-architecture). For empirical validation across benchmarks, see [Experimental Validation](https://deepwiki.com/deepseek-ai/Engram/5-experimental-validation).
