> 来源: [https://deepwiki.com/deepseek-ai/Engram/1-home](https://deepwiki.com/deepseek-ai/Engram/1-home)
> DeepWiki deepseek-ai/Engram

# Home

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1)
 
  
## Purpose & Scope

 This documentation covers **DeepSeekMath-V2**, a mathematical reasoning system that achieves self-verifiable proof generation through a verifier-generator feedback loop. This page provides an overview of the system's architecture, capabilities, and achievements. For detailed information about specific subsystems, see:

 
 - System architecture and training pipeline: [System Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/2-system-architecture)
 - Evaluation benchmarks and competition results: [Evaluation & Results](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/3-evaluation-and-results)
 - Output data formats and schemas: [Data Formats & Outputs](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/4-data-formats-and-outputs)
 - Getting started with model usage: [Getting Started](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/5-getting-started)
 
 **Sources:** [README.md1-88](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L1-L88)

 
---

 
## What is DeepSeekMath-V2?

 DeepSeekMath-V2 is a large language model designed for rigorous mathematical reasoning with self-verification capabilities. Unlike traditional approaches that optimize only for correct final answers, DeepSeekMath-V2 verifies the comprehensiveness and rigor of every step in mathematical proofs. The system is built on the `DeepSeek-V3.2-Exp-Base` foundation model and trained through a three-stage process involving an LLM-based verifier and proof generator.

 **Key distinguishing features:**

 
| Feature | Traditional Approach | DeepSeekMath-V2 |
|---|---|---|
| Objective | Correct final answers | Rigorous step-by-step proofs |
| Verification | External (human/automated checker) | Self-verification via trained verifier |
| Training Signal | Answer correctness | Step-by-step proof validity |
| Applicability | Numerical problems with known answers | Open problems without solutions |

 The system addresses fundamental limitations of answer-only optimization: correct answers do not guarantee correct reasoning, and many mathematical tasks (theorem proving, open problems) require rigorous derivation rather than numerical solutions.

 **Sources:** [README.md30-45](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L30-L45)

 
---

 
## Core Innovation: Self-Verifiable Reasoning

 DeepSeekMath-V2's core innovation is the closed-loop feedback system between proof generation and verification. The system trains the generator to identify and resolve issues in its own proofs before finalizing them, creating mathematical reasoning that can be verified without external ground truth.

 
```

```

 **Diagram: Self-Verifiable Reasoning Architecture**

 The system maintains a generation-verification gap through continuous improvement:

 
 - **Initial Training:** Verifier learns to assess proof quality from labeled data
 - **Generator Training:** Uses verifier as reward model to produce rigorous proofs
 - **Iterative Improvement:** As generator improves, challenging proofs are used to train verifier, maintaining verification capability
 
 **Sources:** [README.md41-45](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L41-L45)

 
---

 
## Repository Structure

 The DeepSeek-Math-V2 repository contains evaluation results, documentation, and references to the foundation model. The actual model weights are hosted on Hugging Face.

 
```

```

 **Diagram: DeepSeek-Math-V2 Repository Structure**

 **Sources:** [README.md50-88](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L50-L88)

 
---

 
## Key Capabilities

 DeepSeekMath-V2 demonstrates strong performance across multiple mathematical domains through rigorous proof generation:

 
### Mathematical Domains

 
| Domain | Capabilities |
|---|---|
| Number Theory | Diophantine equations, prime factorization, divisibility |
| Geometry | Circle properties, coordinate geometry, tangency proofs |
| Combinatorics | Permutations, counting problems, combinatorial identities |
| Algebra | Polynomial functions, functional equations, algebraic manipulation |
| Analysis | Inequalities, limits, asymptotic behavior |
| Probability | Expected values, stochastic processes |
| Formal Methods | Theorem proving, proof assistant integration |

 
### Proof Generation Features

 
 - **Step-by-step derivation:** Complete reasoning chains beyond final answers
 - **Self-resolution:** Identifies and fixes issues before finalization
 - **Rigorous verification:** Validates logical consistency of each proof step
 - **Test-time compute scaling:** Improves results with additional inference compute
 
 **Sources:** [README.md34-45](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L34-L45)

 
---

 
## Evaluation Results Summary

 DeepSeekMath-V2 achieves gold-level performance on prestigious mathematical competitions and benchmarks:

 
### Competition Performance

 
| Competition | Year | Score | Achievement |
|---|---|---|---|
| IMO (International Mathematical Olympiad) | 2025 | 6/6 problems | Gold Medal |
| CMO (Chinese Mathematical Olympiad) | 2024 | 6/6 problems | Gold Medal |
| Putnam | 2024 | 118/120 points | Near-perfect |

 
### IMO-ProofBench

 DeepSeekMath-V2 was evaluated on IMO-ProofBench, a formal theorem proving benchmark developed by Google DeepMind. Results and detailed proofs are available in the `outputs/` directory.

 
```

```

 **Diagram: Evaluation Pipeline and Output Files**

 All model predictions are stored in structured JSONL format in the `outputs/` directory. Each file contains:

 
 - `question`: Original problem statement
 - `problem_idx`: Unique problem identifier
 - `model_prediction`: Object with `proof`, `average_automatic_rating`, and `human_rating`
 
 For detailed analysis of results, see [Evaluation & Results](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/3-evaluation-and-results). For schema documentation, see [Data Formats & Outputs](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/4-data-formats-and-outputs).

 **Sources:** [README.md47-65](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L47-L65)

 
---

 
## Model Access and Usage

 
### Quick Start

 
 - **Download Model:** Available on Hugging Face at `deepseek-ai/DeepSeek-Math-V2`
 - **Inference Setup:** Use the `deepseek-ai/DeepSeek-V3.2-Exp` repository for inference support
 - **Interactive Demo:** Try at `chat.deepseek.com`
 
 
```

```

 **Diagram: Model Access Channels**

 For detailed setup instructions, see [Getting Started](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/5-getting-started).

 **Sources:** [README.md67-70](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L67-L70)

 
---

 
## License and Attribution

 DeepSeekMath-V2 is released under the **Apache License 2.0**, which permits:

 
 - Commercial use
 - Modification
 - Distribution
 - Patent use
 
 Subject to:

 
 - License and copyright notice inclusion
 - State changes documentation
 
 For full legal terms, see [License & Legal](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/7.1-license-and-legal).

 **Sources:** [README.md72-73](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L72-L73)

 
---

 
## Community and Support

 
### Contact Channels

 
| Channel | Purpose | Link/Contact |
|---|---|---|
| Discord | Community discussion | discord.gg/Tc7c45Zzu5 |
| WeChat | Chinese community (中文社区) | QR code in repository |
| Twitter/X | Announcements | @deepseek_ai |
| Email | Support inquiries | service@deepseek.com |

 For community resources and detailed contact information, see [Community & Support](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/7.3-community-and-support).

 **Sources:** [README.md85-87](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L85-L87)

 
---

 
## Citation

 When using DeepSeekMath-V2 in research, please cite:

 
```

```

 **Sources:** [README.md75-82](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L75-L82)
