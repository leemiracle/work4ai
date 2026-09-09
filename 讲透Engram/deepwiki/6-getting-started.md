> 来源: [https://deepwiki.com/deepseek-ai/Engram/6-getting-started](https://deepwiki.com/deepseek-ai/Engram/6-getting-started)
> DeepWiki deepseek-ai/Engram

# Getting Started

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1)
 - [engram_demo_v1.py](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py)
 
  This document provides a practical guide for users to begin working with the Engram repository. It covers environment setup, dependency installation, running the demonstration implementation, and understanding the demo's output and structure.

 For detailed architectural concepts, see [Core Concepts](https://deepwiki.com/deepseek-ai/Engram/2-core-concepts). For production implementation guidance, see [Implementation Guide](https://deepwiki.com/deepseek-ai/Engram/4-implementation-guide). For experimental validation details, see [Experimental Validation](https://deepwiki.com/deepseek-ai/Engram/5-experimental-validation).

 
---

 
## Prerequisites

 The Engram demo requires a Python environment with the following specifications:

 
| Requirement | Specification |
|---|---|
| Python Version | 3.8 or higher (recommended) |
| PyTorch | Latest stable version |
| Operating System | Linux, macOS, or Windows with WSL |
| Hardware | CPU sufficient for demo; GPU not required |
| Memory | Minimum 4GB RAM for small examples |

 **Important Notes:**

 
 - The provided demo ([engram_demo_v1.py1-423](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L1-L423)) is designed for demonstration purposes, not production deployment
 - Standard components (Attention, MoE, advanced hyper-connections) are mocked to focus on Engram module logic
 - The demo illustrates data flow and core algorithms without requiring distributed training infrastructure
 
 **Sources:** [README.md80-90](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1#L80-L90) [engram_demo_v1.py1-19](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L1-L19)

 
---

 
## Installation

 
### Step 1: Clone the Repository

 
```

```

 
### Step 2: Install Dependencies

 Install the required Python packages:

 
```

```

 **Dependency Purposes:**

 
| Package | Purpose | Used By |
|---|---|---|
| torch | Neural network implementation | All module components |
| numpy | N-gram hash computation | NgramHashMapping class |
| transformers | Tokenizer loading | CompressedTokenizer class |
| sympy | Prime number calculations | Hash table sizing logic |

 The installation is complete when all dependencies resolve without errors.

 **Sources:** [README.md80-83](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1#L80-L83) [engram_demo_v1.py22-36](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L22-L36)

 
---

 
## Running the Demo

 
### Basic Execution

 Execute the demo script from the repository root:

 
```

```

 
### Expected Output

 The demo processes a sample text through the Engram-augmented architecture and displays:

 
```
✅ Forward Complete!
input_ids.shape=torch.Size([1, 13])
output.shape=torch.Size([1, 13, 129280])
```

 This output confirms:

 
 - **Input Shape:** `[batch_size, sequence_length]` = `[1, 13]` for the demo text
 - **Output Shape:** `[batch_size, sequence_length, vocab_size]` = `[1, 13, 129280]` logits for next-token prediction
 
 **Sources:** [engram_demo_v1.py396-422](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L396-L422)

 
---

 
## Demo Execution Flow

 The following diagram traces the execution path from script invocation to output:

 
```

```

 **Sources:** [engram_demo_v1.py396-422](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L396-L422)

 
---

 
## Understanding the Demo Implementation

 
### Configuration Architecture

 The demo uses two configuration dataclasses that control system behavior:

 
```

```

 **Key Configuration Parameters:**

 
| Parameter | Value | Purpose |
|---|---|---|
| engram_vocab_size | [129280*5, 129280*5] | Hash table sizes for 2-gram and 3-gram embeddings |
| max_ngram_size | 3 | Generate up to 3-grams (bigrams and trigrams) |
| n_embed_per_ngram | 512 | Embedding dimension per N-gram type |
| n_head_per_ngram | 8 | Multi-head configuration for each N-gram type |
| layer_ids | [1, 15] | Transformer layers with Engram integration |
| hc_mult | 4 | Hyper-connection multiplicity (4 parallel paths) |

 **Sources:** [engram_demo_v1.py38-58](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L38-L58)

 
---

 
### Component Initialization Sequence

 The following diagram maps initialization order to specific code entities:

 
```

```

 **Sources:** [engram_demo_v1.py326-378](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L326-L378) [engram_demo_v1.py380-394](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L380-L394) [engram_demo_v1.py397-401](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L397-L401)

 
---

 
### Forward Pass Data Flow

 The demo processes input through three main phases:

 **Phase 1: Embedding and Preparation**

 
```

```

 **Phase 2: Engram Processing (Layer 1 and Layer 15)**

 
```

```

 **Phase 3: Output Projection**

 
```

```

 **Sources:** [engram_demo_v1.py409-419](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L409-L419) [engram_demo_v1.py358-378](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L358-L378) [engram_demo_v1.py389-394](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L389-L394)

 
---

 
## Demo Text Processing Example

 The demo uses a fixed input text to demonstrate the complete pipeline:

 
### Input Text

 
```
"Only Alexander the Great could tame the horse Bucephalus."
```

 
### Tokenization Process

 
```

```

 **Tokenization Details:**

 
| Stage | Shape | Vocabulary Size | Purpose |
|---|---|---|---|
| Raw Tokens | [1, 13] | 129,280 | Standard DeepSeek-V3 tokenization |
| Compressed Tokens | [1, 13] | ~80,000 (typical) | Normalized, deduplicated vocabulary |
| Hash Addresses | [1, 13, 16] | 16 heads (8 per N-gram type) | Per-layer N-gram embedding addresses |

 **Sources:** [engram_demo_v1.py403-405](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L403-L405) [engram_demo_v1.py60-121](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L60-L121) [engram_demo_v1.py298-303](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L298-L303)

 
---

 
## Interpreting Demo Output

 
### Success Indicators

 When the demo runs successfully, you should observe:

 
 - **No Errors:** Module initialization and forward pass complete without exceptions
 - **Shape Consistency:** Output shape matches expected `[batch_size, sequence_length, vocab_size]`
 - **Completion Message:** `✅ Forward Complete!` printed to console
 
 
### Output Tensor Analysis

 
```

```

 **Key Observations:**

 
 - The output represents **unnormalized logits** for next-token prediction
 - Each position in the sequence has a distribution over the entire vocabulary
 - For generation tasks, apply `softmax` along dimension 2, then sample or take `argmax`
 - The demo does **not** implement autoregressive generation; it performs a single forward pass
 
 **Sources:** [engram_demo_v1.py421-422](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L421-L422)

 
---

 
## Next Steps

 After successfully running the demo, consider the following paths:

 
### Understanding Components

 Explore individual components in depth:

 
 - **N-gram Hashing:** See [N-gram Hash Mapping](https://deepwiki.com/deepseek-ai/Engram/4.2-n-gram-hash-mapping) for deterministic addressing details
 - **Multi-Head Embeddings:** See [Multi-Head Embedding and ShortConv](https://deepwiki.com/deepseek-ai/Engram/4.4-multi-head-embedding-and-shortconv) for embedding architecture
 - **Configuration:** See [Configuration Reference](https://deepwiki.com/deepseek-ai/Engram/4.6-configuration-reference) for parameter tuning
 
 
### Architectural Concepts

 Understand the theoretical foundations:

 
 - **Conditional Memory:** See [Conditional Memory vs Conditional Computation](https://deepwiki.com/deepseek-ai/Engram/2.1-conditional-memory-vs-conditional-computation)
 - **Scaling Laws:** See [Sparsity Allocation and U-shaped Scaling Law](https://deepwiki.com/deepseek-ai/Engram/2.3-sparsity-allocation-and-u-shaped-scaling-law)
 - **Memory Hierarchy:** See [Memory Hierarchy and Offloading](https://deepwiki.com/deepseek-ai/Engram/3.4-memory-hierarchy-and-offloading)
 
 
### Experimental Results

 Review validation evidence:

 
 - **Performance Metrics:** See [Engram-27B Model Results](https://deepwiki.com/deepseek-ai/Engram/5.1-engram-27b-model-results)
 - **Long Context:** See [Long Context Evaluation](https://deepwiki.com/deepseek-ai/Engram/5.2-long-context-evaluation)
 - **Baseline Comparisons:** See [Baseline Comparisons](https://deepwiki.com/deepseek-ai/Engram/5.4-baseline-comparisons)
 
 
### Research Foundation

 Consult the research paper:

 
 - **PDF Document:** `Engram_paper.pdf` in repository root
 - **Paper Summary:** See [Paper Summary](https://deepwiki.com/deepseek-ai/Engram/7.1-paper-summary)
 - **Mechanistic Analysis:** See [Mechanistic Analysis](https://deepwiki.com/deepseek-ai/Engram/7.2-mechanistic-analysis)
 
 
### Modification Guidelines

 To experiment with the demo:

 
 - **Adjust N-gram Size:** Modify `max_ngram_size` in `EngramConfig` (lines 42-43)
 - **Change Integration Layers:** Modify `layer_ids` in `EngramConfig` (line 45)
 - **Alter Hyper-connections:** Modify `hc_mult` in `BackBoneConfig` (line 53)
 - **Test Different Text:** Replace the sample text at line 403
 
 **Important:** The demo is simplified for illustration. Production deployment requires:

 
 - Custom CUDA kernels for efficient N-gram hashing
 - Distributed training infrastructure (All2All communication)
 - Memory offloading mechanisms for large embedding tables
 - Integration with full Attention and MoE implementations
 
 **Sources:** [README.md78-93](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/README.md?plain=1#L78-L93) [engram_demo_v1.py1-19](https://github.com/deepseek-ai/Engram/blob/32b9c9e5/engram_demo_v1.py#L1-L19)
