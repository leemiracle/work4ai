<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphafold · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/technical_note_v2.3.0.md](docs/technical_note_v2.3.0.md)
- [run_alphafold.py](run_alphafold.py)

</details>



## Purpose and Scope

This page provides a high-level introduction to the AlphaFold codebase architecture, its purpose, and its overall system design. It serves as the primary entry point for engineers and researchers to understand the prediction pipeline from sequence input to 3D structure.

For detailed technical instructions on environment setup, see **[Installation and Dependencies](#1.1)**.

## What is AlphaFold?

AlphaFold is a deep learning system developed by Google DeepMind that predicts the 3D structure of a protein from its amino acid sequence. This repository contains the implementation of the inference pipeline for AlphaFold v2, including:

*   **Monomer Prediction**: Single-chain protein folding using the CASP14-winning architecture [README.md:5-7]().
*   **Multimer Prediction**: AlphaFold-Multimer for predicting protein complexes [README.md:11-14]().
*   **Updated v2.3.0 Models**: Fine-tuned weights with a 2021-09-30 training cutoff and support for larger complexes [docs/technical_note_v2.3.0.md:8-22]().
*   **CASP15 Baselines**: Documentation and predictions for the CASP15 assessment [README.md:17-18]().

**Sources:** [README.md:1-28](), [docs/technical_note_v2.3.0.md:1-51]()

## System Architecture

The AlphaFold system is structured as a multi-stage pipeline that transitions from biological sequence data to numerical feature tensors, and finally to geometric 3D coordinates.

### High-Level Code Entity Mapping

The following diagram bridges the high-level functional stages with the specific code entities responsible for them.

```mermaid
graph TB
    subgraph "Entry & Orchestration"
        RD["docker/run_docker.py<br/>Container Launcher"]
        RA["run_alphafold.py<br/>Main Script"]
    end

    subgraph "Data Pipeline (Natural Language -> Code)"
        DP["alphafold/data/pipeline.py<br/>DataPipeline class"]
        DPM["alphafold/data/pipeline_multimer.py<br/>DataPipeline class"]
        TP["alphafold/data/templates.py<br/>TemplateHitFeaturizer"]
    end

    subgraph "Model Execution (JAX/Haiku Space)"
        RM["alphafold/model/model.py<br/>RunModel class"]
        MC["alphafold/model/config.py<br/>CONFIG / MODEL_PRESETS"]
        AFM["alphafold/model/modules.py<br/>AlphaFold module"]
    end

    subgraph "Structural Representation"
        RC["alphafold/common/residue_constants.py<br/>Chemical Constants"]
        PR["alphafold/common/protein.py<br/>Protein class"]
        AA["alphafold/model/all_atom.py<br/>atom37/atom14 logic"]
    end

    RD -- "executes" --> RA
    RA -- "instantiates" --> DP
    RA -- "instantiates" --> RM
    DP -- "calls" --> TP
    RM -- "uses" --> MC
    RM -- "calls" --> AFM
    AFM -- "references" --> RC
    PR -- "converts to PDB" --> RC
    AA -- "formats" --> PR
```

**Sources:** [run_alphafold.py:30-41](), [README.md:139-145](), [alphafold/model/model.py:38-50]()

## Prediction Pipeline Flow

The transformation of a FASTA file into a 3D structure follows a linear progression through four major stages.

### Pipeline Execution Diagram

```mermaid
graph LR
    subgraph "1. Data Acquisition"
        F["FASTA Input"] --> J["Jackhmmer / HHblits<br/>(MSA Generation)"]
        J --> T["HHsearch / HMMsearch<br/>(Template Search)"]
    end

    subgraph "2. Feature Engineering"
        T --> NP["Raw NumPy Features<br/>(feature_dict)"]
        NP --> TF["JAX Tensors<br/>(process_features)"]
    end

    subgraph "3. Neural Inference"
        TF --> EV["Evoformer Stack<br/>(MSA/Pair Processing)"]
        EV --> SM["Structure Module<br/>(3D Refinement)"]
        SM --> RC["Recycling Loop<br/>(3-20 iterations)"]
    end

    subgraph "4. Refinement & Output"
        RC --> AM["Amber Relaxation<br/>(OpenMM)"]
        AM --> PDB["Final PDB / CIF"]
    end
```

**Sources:** [run_alphafold.py:57-225](), [docs/technical_note_v2.3.0.md:41-45](), [README.md:151-164]()

## Core Components

### 1. Data Pipeline
The data pipeline is responsible for searching massive genetic databases (BFD, MGnify, UniRef90, PDB) to find evolutionary conserved patterns. It uses tools like `jackhmmer`, `hhblits`, and `hhsearch` to generate Multiple Sequence Alignments (MSAs) and structural templates [run_alphafold.py:71-113]().

### 2. Model Architecture
The neural network, implemented in JAX and Haiku, consists of the **Evoformer** (which processes MSA and residue-pair representations) and the **Structure Module** (which predicts 3D coordinates using Invariant Point Attention). The system supports different `model_preset` options such as `monomer`, `monomer_ptm`, and `multimer` [run_alphafold.py:168-175]().

### 3. Structural Representation
AlphaFold uses specialized representations like **atom37** (a dense representation of all heavy atoms) and **atom14** (an efficient representation for loss calculations). These are defined in `residue_constants.py` and managed via the `Protein` dataclass [run_alphafold.py:30-32]().

### 4. Relaxation and Scoring
Predicted structures can be "relaxed" using the Amber force field to resolve stereochemical violations [run_alphafold.py:50-55](). The model also outputs confidence metrics:
*   **pLDDT**: Local confidence per residue.
*   **pTM / ipTM**: Global confidence for the structure and interface [docs/technical_note_v2.3.0.md:47-51]().

**Sources:** [run_alphafold.py:30-41](), [README.md:151-164](), [docs/technical_note_v2.3.0.md:1-51]()

## Codebase Organization

| Directory | Description |
| :--- | :--- |
| `alphafold/common/` | Shared constants (residues, atoms) and basic data structures (`Protein`). |
| `alphafold/data/` | Logic for MSA generation, template searching, and multimer pairing. |
| `alphafold/model/` | JAX/Haiku implementation of the Evoformer, Structure Module, and model configs. |
| `alphafold/relax/` | Interface for OpenMM and Amber-based structure minimization. |
| `docker/` | Dockerfile and `run_docker.py` for environment isolation. |
| `scripts/` | Shell scripts for downloading the required 2.6TB+ genetic databases. |

**Sources:** [README.md:38-149](), [run_alphafold.py:15-41]()

## Next Steps

For detailed information on how to set up the environment and its requirements, please see the child page:
*   **[Installation and Dependencies](#1.1)** — Detailed breakdown of `setup.py`, `requirements.txt`, and system prerequisites.

**Sources:** [README.md:38-149]()

---

