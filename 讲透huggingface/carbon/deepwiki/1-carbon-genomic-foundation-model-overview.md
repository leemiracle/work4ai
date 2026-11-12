<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/carbon · page 1 Carbon: Genomic Foundation Model — Overview · fetched 2026-10-26 -->

# Carbon: Genomic Foundation Model — Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [tech-report.pdf](tech-report.pdf)
- [uv.lock](uv.lock)

</details>



Carbon is a family of genomic foundation models developed by Hugging Face, designed to serve as a backbone for DNA and RNA sequence analysis. Trained on approximately **1 trillion tokens (6 trillion base pairs)** [README.md:4-5](), Carbon utilizes a hybrid architecture to bridge natural language processing capabilities with high-resolution genomic modeling.

The project provides a comprehensive ecosystem including pretraining data mixtures, a multi-task zero-shot evaluation suite, and fine-tuning recipes for specialized biological tasks [README.md:8-15]().

### Model Family

The Carbon family consists of three model scales tailored for different computational budgets and use cases [README.md:28-32](). All models utilize a `LlamaDecoderLayer` backbone and are compatible with the Hugging Face `transformers` library via `trust_remote_code=True` [README.md:61-70]().

| Model | Params | Notes |
|---|---|---|
| [`HuggingFaceBio/Carbon-500M`](https://huggingface.co/HuggingFaceBio/Carbon-500M) | 500M | Draft model for speculative decoding. |
| **[`HuggingFaceBio/Carbon-3B`](https://huggingface.co/HuggingFaceBio/Carbon-3B)** | 3B | **Flagship.** Matches or beats Evo2 7B. |
| [`HuggingFaceBio/Carbon-8B`](https://huggingface.co/HuggingFaceBio/Carbon-8B) | 8B | Larger model for more performance. |

For architectural details, routing mechanisms, and loading patterns, see **[Model Family and Architecture](#1.1)**.

**Sources:** [README.md:28-32](), [README.md:61-70]()

### Core Innovations

#### Hybrid Tokenization and DNA Routing
Carbon employs a **hybrid tokenizer** strategy [README.md:34](). It uses Byte Pair Encoding (BPE) for standard English text and a specialized **6-mer** tokenizer for DNA sequences. Switching between these modes is handled by a `<dna>` tag [README.md:35-37](). This allows the model to process metadata or instructions in natural language while maintaining the precise resolution required for genomic data [README.md:72-74]().

#### Pretraining and Hybrid Loss
The models were trained using a specialized fork of Megatron-LM: [huggingface/Megatron-LM-Carbon](https://github.com/huggingface/Megatron-LM-Carbon) [README.md:103-104](). A key technical contribution is the **Hybrid Loss**, which bridges the gap between coarse 6-mer tokenization and single-nucleotide resolution [README.md:107]().

#### Data Mixture
The training corpus is **eukaryote-heavy by design** (90%), focusing on functional genomic regions (RefSeq) and mRNA transcripts (OpenGenome2), while including a 10% prokaryote fraction (GTDB v220 + IMG/PR) to support cross-species generalization [README.md:88-99]().

For a deep dive into the 1T token dataset composition, see **[Pretraining Corpus and Data Mixture](#1.2)**.

### Repository Structure

The repository is organized to support the full lifecycle of genomic model development, from environment setup to downstream application.

#### High-Level System Map
The following diagram illustrates the relationship between the core components of the Carbon ecosystem.

```mermaid
graph TD
    subgraph "Data_&_Training"
        [carbon-pretraining-corpus] --> [Megatron-LM-Carbon]
        [Megatron-LM-Carbon] --> [Checkpoints_500M_3B_8B]
    end

    subgraph "Inference_Logic"
        [Checkpoints_500M_3B_8B] --> [AutoTokenizer]
        [Checkpoints_500M_3B_8B] --> [AutoModelForCausalLM]
        [AutoTokenizer] -- "routes_via_<dna>_tag" --> [6-mer_DNA_Space]
        [AutoTokenizer] -- "default" --> [BPE_Text_Space]
    end

    subgraph "Applications"
        [AutoModelForCausalLM] --> [evaluation_suite]
        [AutoModelForCausalLM] --> [finetuning_recipes]
    end
```
**Sources:** [README.md:1-24](), [README.md:34-37](), [README.md:85-106]()

### Getting Started

Carbon requires **Python 3.12** [pyproject.toml:9]() and uses `uv` for environment management [README.md:41-45](). The repository defines several dependency groups to manage the complex requirements of genomic backends:

*   **Core**: Basic runtime including `vllm==0.19.1`, `accelerate`, and `datasets` [pyproject.toml:11-17]().
*   **Evaluation**: Tools for benchmarking, adding `pandas` [pyproject.toml:26-28]().
*   **Evo2**: Integration with the Evo2 framework, including `flash-attn` and `transformer-engine` [pyproject.toml:29-34]().

For installation steps and quick-start inference examples, see **[Getting Started: Installation and Environment](#1.3)**.

### Evaluation and Fine-Tuning

Carbon includes a standardized suite of seven zero-shot evaluations [README.md:112-113](). These scripts allow for direct comparison across model families like GENERator and Evo2 using a single backend flag [README.md:127-129]().

*   **Variant Effect Prediction (VEP):** BRCA2, TraitGym, and ClinVar [README.md:136-138]().
*   **Generative Tasks:** Sequence recovery [README.md:133]().
*   **Perturbation Tasks:** CAG repeat insertion and synonymous codon substitution [README.md:134-135]().
*   **Long-context:** Genome-NIAH (up to 786 kbp) [README.md:139]().

#### Component Interaction Diagram
This diagram shows how the `evaluation/` and `finetuning/` scripts interact with the model backends.

```mermaid
graph LR
    subgraph "Backends"
        [transformers_AutoModel]
        [vortex_evo2_runtime]
    end

    subgraph "Evaluation_Scripts"
        [vep_eval_py]
        [sequence_recovery_py]
        [genome_niah_eval_py]
        [perturbation_tasks_py]
    end

    subgraph "Fine-Tuning_Recipes"
        [finetuning_deepstarr]
        [finetune_promoter_py]
    end

    [vep_eval_py] -- "Inference" --> [transformers_AutoModel]
    [sequence_recovery_py] -- "Inference" --> [transformers_AutoModel]
    [sequence_recovery_py] -- "Inference" --> [vortex_evo2_runtime]
    [finetuning_deepstarr] -- "FSDP2_Training" --> [transformers_AutoModel]
    [finetune_promoter_py] -- "Trainer" --> [transformers_AutoModel]
```
**Sources:** [README.md:124-142](), [pyproject.toml:26-34]()

---

### Child Pages
*   **[Model Family and Architecture](#1.1)**: Details on the 500M/3B/8B models, 6-mer tokenization, and routing.
*   **[Pretraining Corpus and Data Mixture](#1.2)**: Breakdown of RefSeq, OpenGenome2, and GTDB data sources.
*   **[Getting Started: Installation and Environment](#1.3)**: Environment setup with `uv` and basic inference examples.

---

