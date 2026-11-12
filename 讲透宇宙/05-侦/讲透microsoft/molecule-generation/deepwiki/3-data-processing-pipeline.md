<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/molecule-generation · page 3 Data Processing Pipeline · fetched 2026-10-26 -->

# Data Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [molecule_generation/chem/molecule_dataset_utils.py](molecule_generation/chem/molecule_dataset_utils.py)
- [molecule_generation/cli/preprocess.py](molecule_generation/cli/preprocess.py)

</details>



The data processing pipeline transforms raw molecular data into training-ready datasets for MoLeR models. This comprehensive system converts SMILES strings through multiple stages of featurization, graph conversion, and trace generation to produce the structured data required for training and inference.

For information about training models with processed data, see [Training Models](#5). For details about the model architectures that consume this processed data, see [Model Architecture](#4).

## Pipeline Overview

The data processing pipeline consists of three main stages: input data loading, molecular featurization, and trace generation. The entire pipeline is orchestrated through the CLI command `molecule_generation preprocess` and can handle both initial preprocessing and fine-tuning scenarios.

### High-Level Data Flow

```mermaid
flowchart TD
    subgraph "Input Stage"
        SMILES_FILES["GuacaMol Format Files<br/>train.smiles<br/>valid.smiles<br/>test.smiles"] --> LOAD["load_smiles_data()"]
    end
    
    subgraph "Featurization Stage"
        LOAD --> CONVERT["smiles_to_mols()"]
        CONVERT --> FEAT["featurise_smiles_datapoints()"]
        FEAT --> METADATA["compute_smiles_dataset_metadata()"]
        METADATA --> ATOMFEAT["AtomFeatureExtractor"]
        METADATA --> MOTIFVOC["MotifVocabulary"]
        ATOMFEAT --> MOLTOGRAPH["molecule_to_graph()"]
        MOTIFVOC --> MOLTOGRAPH
    end
    
    subgraph "Output Stage"
        MOLTOGRAPH --> JSONL["*.jsonl.gz files<br/>(FeaturisedData)"]
        JSONL --> TRACEGEN["preprocess_jsonl_files()"]
        TRACEGEN --> TRACES["*.pkl trace files<br/>(Training datasets)"]
    end
    
    style SMILES_FILES fill:#f9f,stroke:#333,stroke-width:2px
    style TRACES fill:#9f9,stroke:#333,stroke-width:2px
```

**Core Data Processing Pipeline**

Sources: [molecule_generation/cli/preprocess.py:208-331](), [molecule_generation/chem/molecule_dataset_utils.py:242-346]()

### Pipeline Stages and File Formats

| Stage | Input Format | Output Format | Key Components |
|-------|-------------|---------------|----------------|
| Input Loading | `.smiles` files | Python dictionaries | `load_smiles_data()`, `DatasetPath` |
| Molecular Featurization | SMILES strings | Graph representations | `featurise_smiles_datapoints()`, `molecule_to_graph()` |
| Trace Generation | `.jsonl.gz` files | `.pkl` training files | `preprocess_jsonl_files()` |

Sources: [molecule_generation/cli/preprocess.py:42-48](), [molecule_generation/chem/molecule_dataset_utils.py:156-240]()

## Molecular Featurization Process

The featurization process transforms SMILES strings into rich graph representations containing atomic features, bond information, and optional motif annotations. This stage is handled primarily by the `FeaturisedData` class and supporting functions.

### Featurization Components

```mermaid
graph TB
    subgraph "SMILES Processing"
        SMILES["SMILES String"] --> RDKIT["MolFromSmiles()"]
        RDKIT --> MOL["RDKit Mol Object"]
    end
    
    subgraph "Feature Extraction"
        MOL --> ATOMEXT["AtomFeatureExtractor"]
        MOL --> MOTIFEXT["MotifVocabularyExtractor"]
        ATOMEXT --> ATOMFEAT["Atomic Features"]
        MOTIFEXT --> MOTIFVOC["MotifVocabulary"]
    end
    
    subgraph "Graph Construction"
        MOL --> ADJLIST["molecule_to_adjacency_lists()"]
        ATOMFEAT --> NODETYPE["Node Types & Features"]
        MOTIFVOC --> MOTIFINST["find_motifs_from_vocabulary()"]
        ADJLIST --> GRAPHREP["Graph Representation"]
        NODETYPE --> GRAPHREP
        MOTIFINST --> GRAPHREP
    end
    
    subgraph "Output Structures"
        GRAPHREP --> NODEFEATS["NodeFeatures<br/>real_valued_features<br/>categorical_features"]
        GRAPHREP --> GRAPHDICT["Graph Dictionary<br/>adjacency_lists<br/>node_types<br/>node_features"]
    end
```

**Molecular Featurization Components**

Sources: [molecule_generation/chem/molecule_dataset_utils.py:385-516](), [molecule_generation/chem/molecule_dataset_utils.py:48-54]()

### Core Featurization Functions

The `featurise_smiles_datapoints()` function serves as the main entry point for molecular featurization, coordinating between atom feature extraction and motif processing:

```mermaid
graph LR
    subgraph "FeaturisedData Class"
        INIT["__init__()"] --> COMPUTEMETA["compute_smiles_dataset_metadata()"]
        COMPUTEMETA --> FEATRAIN["featurise_mol_data(train)"]
        COMPUTEMETA --> FEAVALID["featurise_mol_data(valid)"]
        COMPUTEMETA --> FEATEST["featurise_mol_data(test)"]
    end
    
    subgraph "Feature Processing"
        FEATRAIN --> MOLTOGRAPH1["molecule_to_graph()"]
        FEAVALID --> MOLTOGRAPH2["molecule_to_graph()"]
        FEATEST --> MOLTOGRAPH3["molecule_to_graph()"]
        MOLTOGRAPH1 --> FEATOMS1["featurise_atoms()"]
        MOLTOGRAPH2 --> FEATOMS2["featurise_atoms()"]
        MOLTOGRAPH3 --> FEATOMS3["featurise_atoms()"]
    end
    
    subgraph "Output Properties"
        FEATOMS1 --> TRAINDATA["train_data"]
        FEATOMS2 --> VALIDDATA["valid_data"]
        FEATOMS3 --> TESTDATA["test_data"]
        COMPUTEMETA --> ATOMEXTRACT["atom_feature_extractors"]
        COMPUTEMETA --> MOTIFVOCAB["motif_vocabulary"]
    end
```

**FeaturisedData Class Structure**

Sources: [molecule_generation/chem/molecule_dataset_utils.py:167-240](), [molecule_generation/chem/molecule_dataset_utils.py:125-154]()

## Graph Representation and Data Structures

The pipeline converts molecular structures into standardized graph representations suitable for graph neural networks. The core data structures include adjacency lists, node features, and optional categorical labels.

### Graph Construction Process

The `molecule_to_graph()` function creates the final graph representation by combining structural and feature information:

| Component | Function | Output Structure |
|-----------|----------|------------------|
| Bond Information | `molecule_to_adjacency_lists()` | `List[List[Tuple[int, int]]]` |
| Atom Features | `featurise_atoms()` | `NodeFeatures` (real + categorical) |
| Node Types | `get_atom_symbol()` | List of atom symbols |
| Motif Annotations | `find_motifs_from_vocabulary()` | `List[MotifAnnotation]` |

Sources: [molecule_generation/chem/molecule_dataset_utils.py:453-516](), [molecule_generation/chem/molecule_dataset_utils.py:356-382]()

### Bond Type Processing

The system handles molecular bonds through a standardized dictionary mapping and Kekulization process:

```mermaid
graph TD
    subgraph "Bond Processing"
        MOL["RDKit Molecule"] --> KEKULE["_need_kekulize()"]
        KEKULE --> KEKULIZE["rdmolops.Kekulize()"]
        KEKULIZE --> STEREO["Chem.RemoveStereochemistry()"]
    end
    
    subgraph "Bond Type Mapping"
        STEREO --> BONDS["mol.GetBonds()"]
        BONDS --> BONDDICT["BOND_DICT<br/>SINGLE: 0<br/>DOUBLE: 1<br/>TRIPLE: 2"]
        BONDDICT --> ADJLIST["Adjacency Lists<br/>by Bond Type"]
    end
    
    subgraph "Output Structure"
        ADJLIST --> LIST0["Single Bond List"]
        ADJLIST --> LIST1["Double Bond List"]
        ADJLIST --> LIST2["Triple Bond List"]
    end
```

**Bond Type Processing and Adjacency List Generation**

Sources: [molecule_generation/chem/molecule_dataset_utils.py:45-46](), [molecule_generation/chem/molecule_dataset_utils.py:356-382]()

## CLI Preprocessing Interface

The preprocessing pipeline is primarily accessed through the `molecule_generation preprocess` command, which provides comprehensive options for customizing the featurization process.

### Command Structure and Arguments

The preprocessing CLI accepts three main directory arguments and numerous optional parameters for fine-tuning the process:

```mermaid
graph TD
    subgraph "Required Arguments"
        CLI["molecule_generation preprocess"] --> INPUTDIR["INPUT_DIR<br/>GuacaMol format files"]
        CLI --> OUTPUTDIR["OUTPUT_DIR<br/>Intermediate results"]
        CLI --> TRACEDIR["TRACE_DIR<br/>Final trace files"]
    end
    
    subgraph "Optional Parameters"
        CLI --> MOTIF["Motif Settings<br/>--motif-min-frequency<br/>--motif-max-vocab-size<br/>--motif-min-num-atoms"]
        CLI --> PRETRAINED["Fine-tuning<br/>--pretrained-model-path"]
        CLI --> PROCESS["Processing<br/>--num-processes<br/>--generation-order"]
        CLI --> FORMAT["Output Format<br/>--for-cgvae"]
    end
    
    subgraph "Execution Flow"
        INPUTDIR --> LOADDATA["load_smiles_data()"]
        LOADDATA --> RUNPREP["run_smiles_preprocessing()"]
        RUNPREP --> OUTPUTDIR
        RUNPREP --> TRACEDIR
    end
```

**CLI Preprocessing Interface and Options**

Sources: [molecule_generation/cli/preprocess.py:112-198](), [molecule_generation/cli/preprocess.py:208-331]()

### Generation Orders and Processing Options

The pipeline supports multiple generation order strategies through the `GENERATION_ORDER_CLS` mapping:

| Order Type | Class | Description |
|------------|-------|-------------|
| `bfs` | `BFSOrder` | Breadth-first search ordering |
| `bfs-random` | `BFSOrderRandom` | Randomized BFS (default) |
| `canonical` | `CanonicalOrder` | Canonical atom ordering |
| `random` | `RandomOrder` | Random atom ordering |
| `loop-closing` | `LoopClosingOrder` | Prioritizes loop-closing bonds |

Sources: [molecule_generation/cli/preprocess.py:33-39]()

## Fine-tuning and Model Compatibility

The preprocessing pipeline supports fine-tuning scenarios where new data must be compatible with existing trained models. This process reuses atom feature extractors and motif vocabularies from pretrained models.

### Fine-tuning Data Flow

```mermaid
graph TB
    subgraph "Fine-tuning Mode"
        PRETRAINED["Pretrained Model Path"] --> LOADMODEL["pickle.load()"]
        LOADMODEL --> METADATA["original_dataset_metadata"]
        METADATA --> ATOMEXT["feature_extractors"]
        METADATA --> MOTIFVOC["motif_vocabulary"]
        METADATA --> GENORDER["generation_order"]
    end
    
    subgraph "Compatibility Checks"
        GENORDER --> OVERRIDE1["Override generation_order"]
        MOTIFVOC --> OVERRIDE2["Override motif_extraction_settings"]
        ATOMEXT --> REUSE["Reuse AtomFeatureExtractor"]
    end
    
    subgraph "Processing"
        REUSE --> FEATDATA["featurise_smiles_datapoints()"]
        OVERRIDE1 --> TRACEGEN["preprocess_jsonl_files()"]
        FEATDATA --> TRACEGEN
    end
```

**Fine-tuning Compatibility Process**

Sources: [molecule_generation/cli/preprocess.py:243-267](), [molecule_generation/cli/preprocess.py:292-299]()

---

