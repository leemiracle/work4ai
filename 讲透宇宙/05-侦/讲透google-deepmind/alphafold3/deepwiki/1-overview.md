<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphafold3 · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [WEIGHTS_PROHIBITED_USE_POLICY.md](WEIGHTS_PROHIBITED_USE_POLICY.md)
- [docs/installation.md](docs/installation.md)
- [legal/WEIGHTS_TERMS_OF_USE-Bahasa-Indonesia.md](legal/WEIGHTS_TERMS_OF_USE-Bahasa-Indonesia.md)
- [legal/WEIGHTS_TERMS_OF_USE-Espanol-Latinoamerica.md](legal/WEIGHTS_TERMS_OF_USE-Espanol-Latinoamerica.md)
- [legal/WEIGHTS_TERMS_OF_USE-Francais-Canada.md](legal/WEIGHTS_TERMS_OF_USE-Francais-Canada.md)
- [legal/WEIGHTS_TERMS_OF_USE-Portugues-Brazil.md](legal/WEIGHTS_TERMS_OF_USE-Portugues-Brazil.md)
- [run_alphafold.py](run_alphafold.py)
- [run_alphafold_test.py](run_alphafold_test.py)

</details>



AlphaFold 3 is a state-of-the-art structure prediction system developed by Google DeepMind and Isomorphic Labs. It is capable of modeling a vast range of biomolecular systems, including proteins, nucleic acids (RNA/DNA), small molecules (ligands), and their complex interactions. The system integrates evolutionary information, chemical knowledge via the Chemical Component Dictionary (CCD), and a generative diffusion-based model to produce high-accuracy 3D coordinates and associated confidence metrics.

Sources: [README.md:3-24](), [run_alphafold.py:11-20]()

## Licensing and Usage Policies

The AlphaFold 3 system separates licensing between its source code and its model parameters:

*   **Source Code**: Licensed under the **Apache License, Version 2.0**. [run_alphafold.py:3-13]()
*   **Model Parameters**: Access to weights must be requested directly from Google. Use is strictly limited to non-commercial research by non-commercial organizations (e.g., universities, non-profits, and research institutes). [README.md:6-9](), [WEIGHTS_PROHIBITED_USE_POLICY.md:11-23]()
*   **Prohibited Uses**: Users must not use AlphaFold 3 outputs to train or create machine learning models for biomolecular structure prediction ("Derived Models"). Sharing parameters with commercial organizations is strictly prohibited. [WEIGHTS_PROHIBITED_USE_POLICY.md:80-84](), [WEIGHTS_PROHIBITED_USE_POLICY.md:30-32]()
*   **Citation**: Any publication disclosing findings arising from using this source code, model parameters, or outputs must cite the AlphaFold 3 Nature paper. [README.md:11-15](), [WEIGHTS_PROHIBITED_USE_POLICY.md:113-116]()

Sources: [run_alphafold.py:3-13](), [README.md:6-15](), [WEIGHTS_PROHIBITED_USE_POLICY.md:11-116]()

## System Architecture

AlphaFold 3 is structured as a two-stage pipeline: a **Data Pipeline** for biological search and a **Model Inference** stage for 3D structure generation. The architecture bridges natural language and JSON specifications into high-dimensional tensor representations using JAX and Haiku components.

### Pipeline Design and Code Entities

The diagram below maps the logical prediction stages from natural language concepts to their concrete Python module and class implementations in the codebase.

```mermaid
flowchart TD
    subgraph "Natural Language & Input Space"
        InputJSON[""Input JSON Spec"""] --> FoldingInput[""folding_input.Input"""]
    end

    subgraph "Code Entity Space: Stage 1 (CPU)"
        FoldingInput --> PipelineRun[""pipeline.DataPipeline.run"""]
        PipelineRun --> MSA[""Jackhmmer & Nhmmer Wrappers"""]
        PipelineRun --> Templates[""HMMsearch Template Search"""]
    end

    subgraph "Code Entity Space: Stage 2 (GPU)"
        PipelineRun --> Featurize[""featurisation.featurise_input"""]
        Featurize --> ModelRunner[""model.Model.predict"""]
        ModelRunner --> Diffusion[""diffusion Head Modules"""]
    end

    subgraph "Output Space"
        ModelRunner --> PostProc[""post_processing.process_inference_result"""]
        PostProc --> OutputFiles[""mmCIF & Confidence JSONs"""]
    end
```
Sources: [run_alphafold.py:48-59](), [run_alphafold.py:102-138]()

## Two-Stage Pipeline Flow

System execution is orchestrated by `run_alphafold.py`, managing the transition from sequences to 3D structures via configurable flags (`--run_data_pipeline` and `--run_inference`) [run_alphafold.py:102-111]().

### 1. Data Pipeline
This CPU-bound stage searches large genetic and structural databases to generate Multiple Sequence Alignments (MSAs) and structural templates [README.md:95-97]().
*   **MSA Generation**: Uses `Jackhmmer` for proteins and `Nhmmer` for RNA [run_alphafold.py:114-123]().
*   **Template Search**: Uses `HMMsearch` to find structural analogs in PDB [run_alphafold.py:129-133]().
*   **Database Management**: Queries databases like BFD, MGnify, UniProt, and RNAcentral [run_alphafold.py:147-210]().

### 2. Model Inference
This GPU-bound stage executes heavy tensor computations using JAX and Haiku [README.md:98-99](), [run_alphafold.py:61-63]().
*   **Featurization**: Converts biological inputs and pipeline results into numerical features via `featurisation.featurise_input` [run_alphafold.py:52]().
*   **Model Execution**: The `model.Model` class loads parameters (`params.py`) and executes neural network components [README.md:32-34](), [run_alphafold.py:56-57]().
*   **Diffusion Sampling**: Generates final 3D coordinates through iterative denoising [run_alphafold.py:55-59]().

### Data Flow: From JSON to Tensors

The diagram below bridges high-level biological input data models to low-level tensor representations across internal modules.

```mermaid
flowchart LR
    subgraph "Input Domain Entities"
        direction TB
        PC[""ProteinChain"""]
        RC[""RnaChain"""]
        L[""Ligand"""]
    end

    subgraph "Processing Modules"
        direction TB
        PI[""pipeline.DataPipeline""]
        FE[""featurisation.featurise_input""]
        CPP[""alphafold3.cpp C++ Extensions""]
    end

    subgraph "JAX Tensor Space"
        direction TB
        AL[""AtomLayout Tensors""]
        MF[""MSA Features""]
        TF[""TokenFeatures""]
    end

    PC & RC & L --> PI
    PI --> FE
    CPP -- "Structure Parsing" --> FE
    FE --> AL & MF & TF
```
Sources: [run_alphafold.py:48-64](), [run_alphafold.py:114-138]()

## System Design and Performance

The codebase relies on a modern Python stack optimized for high-performance computing:

| Component | Technology | Role | Source Citation |
| :--- | :--- | :--- | :--- |
| **Numerical Engine** | JAX | Automatic differentiation and GPU acceleration | [run_alphafold.py:62-63]() |
| **Neural Network** | Haiku | Functional neural network layers and modules | [run_alphafold.py:61]() |
| **C++ Extensions** | `alphafold3.cpp` | High-speed mmCIF parsing and structure manipulation | [run_alphafold.py:51]() |
| **Input Parsing** | tokamax | Tokenization and sequence processing utilities | [run_alphafold.py:65]() |

### Performance Optimizations
*   **XLA Compilation**: Uses JAX's Just-In-Time (JIT) compilation for inference acceleration [run_alphafold.py:62-63]().
*   **Staged Execution**: Separation of CPU-heavy search tasks from GPU-heavy inference steps [README.md:95-99]().

Sources: [run_alphafold.py:51-65](), [README.md:95-99]()

## Technical Documentation Roadmap

*   **[Installation Guide](2)**: System requirements, database setup, and Docker configuration [docs/installation.md:1-37]().
*   **[User Guide](3)**: Preparing JSON inputs and interpreting output files [README.md:101-107]().
*   **[Core Pipeline](4)**: Detailed explanation of input processing, data pipeline, and inference architecture.
*   **[Data Structures](5)**: Technical reference for internal representations of chains, structures, and tensors.
*   **[Performance Optimization](8)**: Strategies for hardware utilization, memory, and compilation.

Sources: [README.md:36-112](), [docs/installation.md:1-37]()

---

