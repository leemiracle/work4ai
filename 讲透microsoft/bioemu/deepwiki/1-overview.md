<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/bioemu · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MODEL_CARD.md](MODEL_CARD.md)
- [README.md](README.md)

</details>



## Purpose and Scope

BioEmu (Biomolecular Emulator) is a deep learning model that samples from the approximated equilibrium distribution of structures for a protein monomer, given its amino acid sequence. BioEmu can efficiently generate diverse protein structures that emulate the thermodynamic ensemble, allowing for prediction of structural ensembles, folding free energies, and providing mechanistic hypotheses for protein behavior.

This overview page introduces the core components and architecture of BioEmu, outlining how the system transforms amino acid sequences into protein structure ensembles. For detailed installation instructions, see [Installation and Setup](#2), and for specific usage information, see [Core Functionality](#3).

Sources: [README.md:12-14](), [MODEL_CARD.md:14-16]()

## System Overview

BioEmu uses a combination of deep learning and molecular dynamics techniques to generate protein structure ensembles. The system consists of three primary components working in sequence:

```mermaid
flowchart TD
    User(["User"]) --> |"Amino Acid Sequence"| bioemu
    
    subgraph "BioEmu System"
        colabfold["ColabFold Integration\ngenerate MSA & embeddings"]
        sampler["Structure Sampling\ndiffusion model"]
        sidechain["Sidechain Reconstruction\n& MD Relaxation\n(optional)"]
        
        colabfold --> |"MSA & Embeddings"| sampler
        sampler --> |"Backbone Structures"| sidechain
    end
    
    bioemu --> |"Protein Structure Ensemble"| User
```

**Primary Components:**
1. **ColabFold Integration** - Generates multiple sequence alignments (MSA) and embeddings from the input amino acid sequence
2. **Structure Sampling** - Uses a diffusion model to generate diverse backbone structures
3. **Sidechain Reconstruction & MD Relaxation** - Optional post-processing to add sidechains and refine structures

Sources: [README.md:12-14](), [README.md:37-48](), [README.md:70-100]()

## Key Capabilities

BioEmu offers the following key capabilities:

| Capability | Description |
|------------|-------------|
| Efficient Structure Sampling | Generate thousands of statistically independent structures per hour on a single GPU |
| Conformational Diversity | Sample functionally relevant conformational changes, including cryptic pockets, local unfolding, and domain rearrangements |
| Thermodynamic Accuracy | Samples with relative free energy errors around 1 kcal/mol, validated against MD simulations and experimental data |
| Sidechain Reconstruction | Optional reconstruction of side-chains using HPacker |
| MD Relaxation | Optional molecular dynamics equilibration using OpenMM |

Sources: [MODEL_CARD.md:20-23](), [MODEL_CARD.md:90-94]()

## System Architecture

The following diagram shows the detailed architecture of BioEmu, including the main code components and their interactions:

```mermaid
flowchart TD
    User(["User"]) --> |"Sequence/FASTA"| sample["bioemu.sample.main()"]
    
    subgraph "External Dependencies"
        hf["HuggingFace Models\nmicrosoft/bioemu"]
        cf["ColabFold\nMSA generation"]
        hp["HPacker\nsidechain reconstruction"]
        omm["OpenMM\nMD simulation"]
    end
    
    subgraph "Core Components"
        sample
        get_embeds["bioemu.get_embeds()\nget_colabfold_embeds()"]
        diffusion["DiGConditionalScoreModel\nDiffusion/Denoising Process"]
        convert["bioemu.convert_chemgraph()\nsave_pdb_and_xtc()"]
        sidechain["bioemu.sidechain_relax.main()"]
    end
    
    sample --> get_embeds
    get_embeds --> cf
    sample --> hf
    sample --> diffusion
    diffusion --> convert
    convert --> |"backbone structures\ntopology.pdb, samples.xtc"| sidechain
    sidechain --> hp
    sidechain --> omm
    
    sidechain --> |"PDB + XTC files\nsamples_sidechain_rec.{pdb,xtc}\nsamples_md_equil.{pdb,xtc}"| User
```

This diagram shows how user inputs flow through the system to generate protein structures. The system leverages multiple external dependencies and core processing components to transform amino acid sequences into protein structure ensembles.

Sources: [README.md:37-48](), [README.md:70-100]()

## Data Transformations

BioEmu transforms data through several key stages as illustrated below:

```mermaid
graph LR
    seq["Amino Acid Sequence"] --> msa["Multiple Sequence Alignment\nvia ColabFold"]
    msa --> embeds["MSA Embeddings"]
    embeds --> chemgraph["ChemGraph\nProtein Representation"]
    chemgraph --> |"Diffusion Process\nDPM/Heun Denoiser"| sampled["Sampled ChemGraph"]
    sampled --> backbone["Backbone Atom Positions\ntopology.pdb, samples.xtc"]
    backbone --> |"Optional"| sidechain["All-Heavy-Atom Structures\nsamples_sidechain_rec.{pdb,xtc}"]
    sidechain --> |"Optional"| relaxed["MD Relaxed Structures\nsamples_md_equil.{pdb,xtc}"]
```

This diagram shows the progression from an input amino acid sequence to final structure outputs, with optional sidechain reconstruction and MD relaxation steps.

Sources: [README.md:37-48](), [README.md:70-100]()

## Usage Interfaces

BioEmu provides two main interfaces for users:

```mermaid
flowchart TD
    subgraph "User Interfaces"
        cli["Command Line Interface"]
        python_api["Python API"]
    end
    
    cli -->|"python -m bioemu.sample"| sample
    python_api -->|"from bioemu.sample import main"| sample
    
    cli -->|"python -m bioemu.sidechain_relax"| sidechain
    python_api -->|"from bioemu.sidechain_relax import main"| sidechain
    
    subgraph "Core Components"
        sample["Structure Sampling"]
        sidechain["Sidechain Reconstruction\n& MD Relaxation"]
    end
    
    sample -->|"Creates"| o1["topology.pdb\nsamples.xtc"]
    sidechain -->|"Creates"| o2["samples_sidechain_rec.pdb\nsamples_sidechain_rec.xtc\nsamples_md_equil.pdb\nsamples_md_equil.xtc"]
```

Users can interact with BioEmu through either a command-line interface or Python API. Both interfaces provide access to the core components of structure sampling and optional sidechain reconstruction/MD relaxation.

Sources: [README.md:37-48](), [README.md:70-100]()

## Performance Characteristics

BioEmu's performance varies with sequence length. The table below shows approximate sampling times for 1000 samples using an A100 GPU with 80GB VRAM:

| Sequence Length | Time (minutes) |
|----------------:|---------------:|
|             100 |              4 |
|             300 |             40 |
|             600 |            150 |

Sources: [README.md:52-58]()

## Limitations and Scope

BioEmu has the following limitations:

1. Only supports sampling structures of protein monomers
2. Limited support for multi-chain proteins or protein-protein interactions
3. Does not explicitly model interactions with other chemical entities like small molecules
4. Inherits biases from training data (AlphaFold2 predictions and molecular dynamics simulations)

Sources: [README.md:63](), [MODEL_CARD.md:136-139]()

## Model Architecture

BioEmu uses a DiG (Directed Graph) neural network architecture trained using a combination of:
- Denoising score matching on flexible protein structures from AlphaFold DB
- Property prediction fine-tuning to match experimental folding free energies
- Molecular dynamics data

The model parameters are automatically downloaded from HuggingFace (microsoft/bioemu) when first used.

Sources: [MODEL_CARD.md:102-103](), [README.md:50]()

---

