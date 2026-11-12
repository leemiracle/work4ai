<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/bioemu · page 5 Model Architecture · fetched 2026-10-26 -->

# Model Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MODEL_CARD.md](MODEL_CARD.md)
- [src/bioemu/config/denoiser/dpm.yaml](src/bioemu/config/denoiser/dpm.yaml)
- [src/bioemu/config/denoiser/heun.yaml](src/bioemu/config/denoiser/heun.yaml)
- [src/bioemu/models.py](src/bioemu/models.py)

</details>



This document provides a technical overview of the neural network architecture and diffusion model that powers BioEmu - a deep learning system for generating protein equilibrium structure ensembles. This page focuses specifically on the model architecture itself, including the neural network components, diffusion process, and how these components interact to produce protein structure ensembles.

For information about the overall system workflow, see [Core Functionality](#3).

## Overview

BioEmu uses the Distributional Graphormer (DiG) architecture trained with a combination of denoising score matching and property prediction fine-tuning (PPFT). The model has approximately 31 million parameters and generates protein structures through a diffusion-based process.

```mermaid
flowchart TD
    subgraph "BioEmu Model Architecture"
        direction LR
        input["Input:\nAmino Acid Sequence\n+ MSA Embeddings"]
        diffusion["Diffusion Model"]
        scoremodel["DiGConditionalScoreModel"]
        denoiser["Denoiser\n(DPM-Solver or Heun)"]
        output["Output:\nProtein Structure\nEnsemble"]

        input --> diffusion
        diffusion --> |"Forward Process\n(Add Noise)"| scoremodel
        scoremodel --> |"Score Prediction"| denoiser
        denoiser --> |"Reverse Process\n(Remove Noise)"| output
    end
```

Sources: [MODEL_CARD.md:100-102]()

## DiG Model Architecture

The core of BioEmu is based on the Distributional Graphormer (DiG) architecture, which is specifically designed to model protein structures while respecting their geometric constraints. The architecture consists of several key components that work together to generate physically plausible protein conformations.

```mermaid
flowchart TD
    subgraph "DiGConditionalScoreModel Architecture"
        input["ChemGraph Input\n(Protein Data)"]
        wrapper["DiGConditionalScoreModel"]
        dig["DistributionalGraphormer"]
        pos["Position Scores"]
        rot["Rotation Scores"]
        output["Updated ChemGraph"]
        
        input --> wrapper
        wrapper --> |"Processes inputs"| dig
        dig --> |"Predicts translation"| pos
        dig --> |"Predicts rotation"| rot
        pos --> output
        rot --> output
    end
```

Sources: [src/bioemu/models.py:326-384]()

### Key Components

The `DiGConditionalScoreModel` is a wrapper that converts between ChemGraph objects (the protein representation used throughout BioEmu) and the position/rotation tensors needed by the underlying DistributionalGraphormer neural network.

```mermaid
classDiagram
    class DiGConditionalScoreModel {
        +model_nn: DistributionalGraphormer
        +forward(ChemGraph, t) ChemGraph
    }
    
    class DistributionalGraphormer {
        +d_model: int
        +step_emb: SinusoidalPositionEmbedder
        +x1d_proj: Sequential
        +x2d_proj: Sequential
        +rp_proj: RelativePositionBias
        +st_module: StructureModule
        +forward(x, node_orientations, batch_index, t, context)
    }
    
    class SinusoidalPositionEmbedder {
        +dim: int
        +forward(time) Tensor
    }
    
    class RelativePositionBias {
        +num_buckets: int
        +max_distance: int
        +forward(relative_position) Tensor
    }
    
    class StructureModule {
        +forward()
    }
    
    DiGConditionalScoreModel --> DistributionalGraphormer
    DistributionalGraphormer --> SinusoidalPositionEmbedder
    DistributionalGraphormer --> RelativePositionBias
    DistributionalGraphormer --> StructureModule
```

Sources: [src/bioemu/models.py:19-384]()

#### DistributionalGraphormer

The core neural network is the `DistributionalGraphormer`, which uses a transformer-like architecture specifically adapted for protein structures:

1. **Time Embedding**: Uses `SinusoidalPositionEmbedder` to encode diffusion timesteps into a high-dimensional representation
2. **Representation Projections**: Projects 1D node features and 2D edge features to the model's dimensions
3. **Relative Position Encoding**: Uses `RelativePositionBias` to encode relative positions between residues
4. **Structure Module**: Processes the inputs to predict translation and rotation scores

The default configuration uses:
- Model dimension: 512
- Pair dimension: 256
- Number of layers: 8
- Number of heads: 32
- Hidden dimension: 1024

Sources: [src/bioemu/models.py:148-324]()

#### Embedding Components

The model uses several specialized embedding components:

1. **SinusoidalPositionEmbedder**: Encodes diffusion timesteps using sinusoidal functions, similar to positional encodings in transformers. This helps the model understand where in the diffusion process it's operating.

2. **RelativePositionBias**: Creates learned embeddings based on the relative positions between residues in the sequence. The resolution of the distance buckets decreases the further you go from the diagonal, providing more detail for nearby residues.

Sources: [src/bioemu/models.py:19-145]()

## Diffusion Model

BioEmu uses a diffusion-based approach to generate protein structures. The diffusion process involves:

1. **Forward Process**: Adding noise to a protein structure according to a predefined schedule
2. **Score Function**: Learning to predict the gradient of the log probability density (score)
3. **Reverse Process**: Using the score function to gradually denoise and generate samples

```mermaid
flowchart LR
    subgraph "BioEmu Diffusion Process"
        direction LR
        x0["Protein Structure\n(x₀)"]
        xt["Noisy Structure\n(xₜ)"]
        score["Score Prediction\n(∇ log p(xₜ))"]
        xnew["Updated Structure\n(xₜ₋₁)"]
        
        x0 -->|"Forward Process\n(Add Noise)"| xt
        xt -->|"Input to Score Model"| score
        score -->|"Denoising Step"| xnew
        xnew -->|"Repeat until t=0"| score
    end
```

Sources: [MODEL_CARD.md:102-103](), [src/bioemu/config/denoiser/dpm.yaml](), [src/bioemu/config/denoiser/heun.yaml]()

### Denoising Algorithms

BioEmu supports two main denoising algorithms for the reverse process:

#### DPM-Solver

A differential equation solver approach that can generate high-quality samples with fewer steps:
- Default steps: 30
- Epsilon time: 0.001
- Max time: 0.99

Sources: [src/bioemu/config/denoiser/dpm.yaml]()

#### Heun Denoiser

A second-order method that provides more accurate denoising:
- Default steps: 100
- Epsilon time: 0.001
- Max time: 0.99
- Noise parameter: 0.5

Sources: [src/bioemu/config/denoiser/heun.yaml]()

## Model Inputs and Outputs

The model operates on protein structures represented as `ChemGraph` objects:

### Inputs
- **Amino acid sequence**: The primary input defining the protein
- **MSA embeddings**: Evolutionary information derived from multiple sequence alignment
  - Node features: 384-dimensional (EVOFORMER_NODE_DIM)
  - Edge features: 128-dimensional (EVOFORMER_EDGE_DIM)
- **Diffusion time (t)**: Controls the noise level in the diffusion process

### Outputs
- **Position scores**: Translation vectors that are equivariant to global rotations
- **Rotation scores**: Invariant rotation updates in axis-angle representation

These scores are used by the denoising process to iteratively refine the protein structure.

```mermaid
flowchart TD
    subgraph "Data Flow Through Model"
        amino["Amino Acid Sequence"]
        msa["Multiple Sequence Alignment"]
        embeds["MSA Embeddings"]
        chemgraph["ChemGraph Representation"]
        noisy["Noisy ChemGraph"]
        score["Score Predictions"]
        denoised["Denoised Structure"]
        ensemble["Structure Ensemble"]
        
        amino --> msa
        msa --> embeds
        embeds --> chemgraph
        chemgraph --> |"Add Noise"| noisy
        noisy --> |"DiGConditionalScoreModel"| score
        score --> |"Denoising Step"| denoised
        denoised --> |"Multiple Samples"| ensemble
    end
```

Sources: [src/bioemu/models.py:15-17](), [src/bioemu/models.py:359-384]()

## Model Training Objectives

BioEmu's model is trained using a combination of two main objectives:

1. **Denoising Score Matching**: Trains the model to predict the gradient of the log probability density of protein structures. This objective is applied to:
   - Structures from the AlphaFold Database (AFDB)
   - Molecular dynamics simulation data

2. **Property Prediction Fine-Tuning (PPFT)**: An additional objective that helps the model match experimental folding free energies.

This dual training approach allows BioEmu to generate structurally diverse ensembles that match the thermodynamic properties of real proteins.

Sources: [MODEL_CARD.md:41-42](), [MODEL_CARD.md:102-103]()

## SE(3) Equivariance Properties

The model architecture is designed with specific equivariance properties to handle 3D protein structures correctly:

- Translation scores are equivariant to global rotations
- Rotation scores are invariant to global rotations and translations

This ensures that the model's predictions respect the physical symmetries of protein structures and are independent of the coordinate frame.

```mermaid
flowchart LR
    subgraph "Equivariance Properties"
        direction LR
        frame1["Input Frame 1"]
        score1["Score Prediction 1"]
        
        frame2["Input Frame 2\n(Rotated)"]
        score2["Score Prediction 2\n(Transformed)"]
        
        frame1 --> |"Model"| score1
        frame2 --> |"Model"| score2
        
        frame1 --> |"Rotation R"| frame2
        score1 --> |"Transform by R"| score2
    end
```

Sources: [src/bioemu/models.py:178-184](), [src/bioemu/models.py:305-306]()

## Summary

BioEmu's model architecture combines the Distributional Graphormer (DiG) with diffusion-based generative modeling to produce protein structure ensembles that accurately represent the thermodynamic equilibrium. The architecture's key strengths include:

1. Effective representation of protein structures through specialized embeddings
2. SE(3) equivariance properties that respect physical symmetries
3. Combination of denoising score matching and property prediction objectives
4. Support for multiple denoising algorithms with different speed/quality tradeoffs

This architecture enables BioEmu to efficiently generate thousands of structurally diverse protein conformations per hour on a single GPU, while maintaining high physical accuracy.

Sources: [MODEL_CARD.md:22-24](), [MODEL_CARD.md:100-103]()

---

