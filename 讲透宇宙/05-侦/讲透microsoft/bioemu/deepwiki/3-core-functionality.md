<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/bioemu · page 3 Core Functionality · fetched 2026-10-26 -->

# Core Functionality

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/bioemu/convert_chemgraph.py](src/bioemu/convert_chemgraph.py)
- [src/bioemu/sample.py](src/bioemu/sample.py)

</details>



This document provides a comprehensive overview of BioEmu's core functionality - the essential processes that enable the system to generate protein structure ensembles from amino acid sequences. BioEmu combines machine learning techniques with molecular modeling to produce physically realistic protein conformations that approximate the equilibrium distribution of structures.

For installation instructions, see [Installation and Setup](#2). For details about the underlying model architecture, see [Model Architecture](#5).

## 1. Main Workflow

BioEmu's core functionality consists of three main processes:

1. **Structure Sampling**: Generates backbone-only protein structures from an amino acid sequence
2. **Format Conversion**: Converts the internal representation to standard molecular formats (PDB, XTC)
3. **Post-Processing** (optional): Reconstructs sidechains and performs MD relaxation

The following diagram illustrates this workflow:

```mermaid
flowchart TD
    User([User]) --> |"Input: Amino Acid Sequence"| sample["bioemu.sample.main()"]
    
    subgraph Core Functionality
        sample --> get_embeds["get_colabfold_embeds()"]
        get_embeds --> |"MSA & Embeddings"| generate["generate_batch()"]
        generate --> |"Diffusion Process"| diffusion["Denoiser (DPM/Heun)"]
        diffusion --> |"Sampled Structures"| convert["save_pdb_and_xtc()"]
        convert --> |"Optional"| sidechain["bioemu.sidechain_relax.main()"]
    end
    
    convert --> |"Output: topology.pdb, samples.xtc"| User
    sidechain --> |"Output: Reconstructed & Relaxed Structures"| User
```

Sources: [src/bioemu/sample.py:66-201](), [README.md:37-43]()

## 2. Structure Sampling

The structure sampling process begins with an amino acid sequence and produces a set of probable backbone conformations using a diffusion model.

### 2.1 Entry Point and Configuration

The main entry point for sampling is the `main()` function in `bioemu.sample`, which accepts:
- An amino acid sequence or FASTA file
- The number of samples to generate
- Output directory and other configuration parameters

```mermaid
flowchart LR
    subgraph "User Inputs"
        seq["sequence: str/Path"]
        num["num_samples: int"]
        out["output_dir: Path"]
        batch["batch_size_100: int"]
        model["model_name: str"]
    end
    
    subgraph "Sample Configuration"
        ckpt["maybe_download_checkpoint()"]
        denoiser["Denoiser Configuration"]
    end
    
    seq --> main["bioemu.sample.main()"]
    num --> main
    out --> main
    batch --> main
    model --> ckpt
    ckpt --> main
    denoiser --> main
    
    main --> |"Instantiates"| score["DiGConditionalScoreModel"]
    main --> |"Instantiates"| denoise["Denoiser"]
```

Sources: [src/bioemu/sample.py:66-101]()

### 2.2 Embedding Generation

For each sequence, BioEmu generates embeddings using ColabFold:

1. The sequence is passed to `get_colabfold_embeds()`
2. ColabFold creates a Multiple Sequence Alignment (MSA)
3. The MSA is converted to single-residue and pair-residue embeddings
4. Embeddings are cached for future use

```mermaid
flowchart TD
    seq["Amino Acid Sequence"] --> get_embeds["get_colabfold_embeds()"]
    get_embeds --> colabfold["ColabFold MSA Generation"]
    colabfold --> cache["Cache Embeddings"]
    cache --> single["single_embeds: (seq_len, n_features)"]
    cache --> pair["pair_embeds: (seq_len, seq_len, n_pair_features)"]
```

Sources: [src/bioemu/sample.py:229-246]()

### 2.3 Structure Generation

With embeddings in hand, BioEmu generates structures through:

1. Creating a `ChemGraph` representation with the embeddings
2. Running a diffusion model to sample protein backbones
3. Processing batches of samples with appropriate batch sizes based on sequence length

```mermaid
flowchart TD
    embeds["Embeddings"] --> chemgraph["ChemGraph Creation"]
    chemgraph --> batch["Batch Processing"]
    batch --> denoiser["Denoiser (DPM/Heun)"]
    denoiser --> |"Applies Score Model"| score["DiGConditionalScoreModel"]
    score --> |"Generates"| samples["Sampled ChemGraphs"]
    samples --> save["Save as NPZ files"]
```

Sources: [src/bioemu/sample.py:203-277]()

## 3. Structure Conversion

After generating samples, BioEmu converts them to standard molecular formats:

### 3.1 ChemGraph to Backbone Atoms

The `ChemGraph` representation is converted to backbone atom positions:

1. Positions and orientations are extracted from sampled ChemGraphs
2. These are processed to generate 3D coordinates for N, CA, C, O, and CB backbone atoms
3. The backbone atom positions are saved in Angstroms

```mermaid
flowchart LR
    pos["pos_nm: (batch, seq_len, 3)"] --> convert["save_pdb_and_xtc()"]
    orient["node_orientations: (batch, seq_len, 3, 3)"] --> convert
    seq["sequence: str"] --> convert
    
    convert --> get_atoms["get_atom37_from_frames()"]
    get_atoms --> |"Backbone Atoms"| frames["Atom Positions"]
    frames --> |"Filter"| physical["filter_unphysical_traj()"]
    physical --> |"Save"| files["PDB/XTC Files"]
```

Sources: [src/bioemu/convert_chemgraph.py:398-458]()

### 3.2 Filtering Unphysical Structures

By default, BioEmu filters generated structures based on physical criteria:

1. Maximum CA-CA distance between sequential residues (< 4.5 Å)
2. Maximum C-N distance between sequential residues (< 2.0 Å)
3. Minimum distance between non-bonded atoms (> 1.0 Å)

Only structures that satisfy these criteria are included in the final output.

```mermaid
flowchart TD
    traj["mdtraj.Trajectory"] --> |"CA-CA Distances"| ca_check["Check Sequential CA-CA distances"]
    traj --> |"C-N Distances"| cn_check["Check Sequential C-N distances"]
    traj --> |"Atom-Atom Distances"| clash["Check for steric clashes"]
    
    ca_check --> masks["AND Filtering Masks"]
    cn_check --> masks
    clash --> masks
    
    masks --> |"Select Valid Frames"| filtered["Filtered Trajectory"]
    filtered --> save["Save Filtered XTC"]
```

Sources: [src/bioemu/convert_chemgraph.py:296-395]()

## 4. Optional Post-Processing

BioEmu offers optional post-processing to enhance the generated structures:

### 4.1 Sidechain Reconstruction

After backbone generation, sidechains can be reconstructed using HPacker:

1. Takes the backbone-only PDB and XTC files as input
2. Uses HPacker to add sidechain heavy atoms
3. Outputs reconstructed all-heavy-atom structures

### 4.2 MD Relaxation

Optionally, structures can undergo molecular dynamics (MD) relaxation:

1. Energy minimization to resolve local clashes
2. Short NVT equilibration (if specified)
3. Outputs MD-equilibrated structures

```mermaid
flowchart LR
    pdb["topology.pdb"] --> sidechain["bioemu.sidechain_relax.main()"]
    xtc["samples.xtc"] --> sidechain
    
    subgraph "Post-Processing Options"
        direction TB
        sc["Sidechain Reconstruction"] --> min["Energy Minimization"]
        min --> nvt["Optional: NVT Equilibration"]
    end
    
    sidechain --> sc
    
    sc --> |"Output"| rec["samples_sidechain_rec.{pdb,xtc}"]
    nvt --> |"Output"| equil["samples_md_equil.{pdb,xtc}"]
```

Sources: [README.md:70-100]()

## 5. Data Flow Summary

The following diagram summarizes the data transformations that occur throughout BioEmu's core functionality:

```mermaid
graph LR
    subgraph "Input"
        seq["Amino Acid Sequence"]
    end
    
    subgraph "Embedding Generation"
        msa["Multiple Sequence Alignment"]
        embeds["MSA Embeddings"]
    end
    
    subgraph "Structure Sampling"
        chemgraph["ChemGraph"]
        diffusion["Diffusion Process"]
        sampled["Sampled ChemGraph"]
    end
    
    subgraph "Structure Conversion"
        backbone["Backbone Atom Positions"]
        filtering["Physical Filtering"]
        formats["PDB/XTC Files"]
    end
    
    subgraph "Optional Post-Processing"
        sidechain["Sidechain Reconstruction"]
        relaxed["MD Relaxation"]
    end
    
    seq --> msa
    msa --> embeds
    embeds --> chemgraph
    chemgraph --> diffusion
    diffusion --> sampled
    sampled --> backbone
    backbone --> filtering
    filtering --> formats
    formats --> sidechain
    sidechain --> relaxed
```

Sources: [src/bioemu/sample.py](), [src/bioemu/convert_chemgraph.py](), [README.md:70-100]()

## 6. Usage Examples

### Command Line Interface

```bash
python -m bioemu.sample --sequence GYDPETGTWG --num_samples 10 --output_dir ~/test-chignolin
```

### Python API

```python
from bioemu.sample import main as sample
sample(sequence='GYDPETGTWG', num_samples=10, output_dir='~/test_chignolin')
```

For sidechain reconstruction and MD relaxation:

```bash
python -m bioemu.sidechain_relax --pdb-path path/to/topology.pdb --xtc-path path/to/samples.xtc
```

Sources: [README.md:38-96]()

## 7. Performance Considerations

The sampling time depends on sequence length and available hardware. For reference, on an A100 GPU with 80GB VRAM:

| Sequence Length | Time (minutes) for 1000 samples |
|----------------:|--------------------------------:|
|             100 |                               4 |
|             300 |                              40 |
|             600 |                             150 |

Sources: [README.md:52-58]()

---

