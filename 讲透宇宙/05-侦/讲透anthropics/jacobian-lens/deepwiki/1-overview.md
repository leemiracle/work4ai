<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/jacobian-lens · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



The `jacobian-lens` project is the reference implementation for the paper [**Verbalizable Representations Form a Global Workspace in Language Models**](https://transformer-circuits.pub/2026/workspace/index.html). It provides tools to "read out" the internal states of decoder-only Transformers by transporting residual stream vectors into the final-layer basis using a linear Jacobian-based approximation [README.md:5-11]().

## What is a Jacobian Lens?

A Jacobian lens allows researchers to see what an internal activation is "disposed" to make the model say. Unlike a standard logit lens, which applies the model's unembedding directly to intermediate layers, the Jacobian lens uses a learned transport matrix $J_l$ to account for the transformations that occur between layer $l$ and the final layer [README.md:8-11]().

The core operation is defined as:
`lens_l(h) = unembed( J_l @ h )`, where `J_l = E[∂h_final / ∂h_l]` [README.md:16-17]().

The expectation $E$ is taken over a text corpus, summing cotangents over target positions and averaging over source positions [README.md:19-22]().

### System Architecture: From Space to Code

The following diagram bridges the conceptual "Natural Language Space" (prompts and tokens) to the "Code Entity Space" (classes and functions) within the `jlens` library.

**Natural Language to Code Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        [Prompt_String] --> [Token_Sequence]
        [Token_Sequence] --> [Model_Output]
    end

    subgraph "Code Entity Space (jlens)"
        [Prompt_String] -- "jlens.from_hf()" --> [HFLensModel]
        [HFLensModel] -- "jlens.vis.compute_slice()" --> [SliceData]
        [SliceData] -- "jlens.vis.build_page()" --> [Interactive_HTML]
        
        [HFLensModel] -- "jlens.fitting.fit()" --> [JacobianLens_Object]
        [JacobianLens_Object] -- ".apply()" --> [Lens_Logits]
    end

    [Lens_Logits] -- "unembed" --> [Token_Sequence]
```
Sources: [jlens/fitting.py:1-22](), [README.md:44-59](), [README.md:63-68]()

## Repository Organization

The repository is structured into the core library, evaluation datasets, and experimental suites used to validate the Global Workspace theory.

| Component | Path | Description |
|:---|:---|:---|
| **Core Library** | `jlens/` | Contains the `JacobianLens` class, fitting logic, and visualization tools. |
| **Data & Assets** | `jlens/data/` | Bundled assets and example prompts. |
| **Evaluations** | `data/evaluations/` | Six benchmark datasets (multi-hop, multilingual, etc.) [README.md:94-97](). |
| **Experiments** | `data/experiments/` | Eleven experiment datasets supporting paper claims (causal swaps, capacity, etc.). |
| **Tests** | `tests/` | Suite using a `TinyDecoder` for CI and verification. |

### Data Flow for Lens Application
This diagram illustrates how the `JacobianLens` interacts with a model (via the `LensModel` protocol) to produce interpretability data.

**Lens Application Logic**
```mermaid
graph LR
    subgraph "Input Processing"
        [User_Prompt] --> [HFLensModel]
        [JacobianLens] --> [HFLensModel]
    end

    subgraph "Core Execution"
        [HFLensModel] -- "ActivationRecorder" --> [Hidden_States]
        [Hidden_States] -- "JacobianLens.transport()" --> [Transported_Vectors]
        [Transported_Vectors] -- "Unembedding" --> [Lens_Logits]
    end

    subgraph "Output"
        [Lens_Logits] --> [jlens.vis.compute_slice]
        [jlens.vis.compute_slice] --> [Interactive_HTML_Page]
    end
```
Sources: [jlens/fitting.py:1-22](), [README.md:44-59](), [README.md:78-81]()

## Key Features

*   **Pre-fitted Lenses**: Support for loading lenses directly from the HuggingFace Hub using `JacobianLens.from_pretrained()` [README.md:53]().
*   **Fitting Suite**: Utilities for calculating the Jacobian estimator over a corpus using `jlens.fit()` [README.md:66]().
*   **Interactive Visualization**: A D3-based "Slice" view that shows the top-1 token and rank for every (position, layer) coordinate in a grid [README.md:82-89]().
*   **Model Agnostic**: An adapter-based approach (`from_hf`) that supports common architectures like Llama, Qwen, Mistral, and GPT-2 [README.md:25-26]().

## Child Sections

For detailed technical documentation, please refer to the following sub-pages:

*   **[Getting Started](#1.1)**: Installation via `pip install -e .` [README.md:37](), environment setup, and a quick-start walkthrough using `walkthrough.ipynb` [README.md:78-81]().
*   **[Key Concepts and Terminology](#1.2)**: Theoretical background on Jacobian transport, the residual stream, and the Global Workspace motivation.

Sources: [README.md:1-105](), [pyproject.toml:1-39](), [LICENSE:1-133]()

---

