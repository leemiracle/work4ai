<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphagenome_research · page 4 Model Architecture · fetched 2026-10-26 -->

# Model Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/alphagenome_research/model/__init__.py](src/alphagenome_research/model/__init__.py)

</details>



## Purpose and Scope

This document describes the AlphaGenome model architecture, including the JAX-based implementation, neural network components, data structures, and prediction pipeline. It covers the core model design, how DNA sequences are processed, and the various output modalities the model produces.

For information about the high-level DNA Model API for making predictions and scoring variants, see [DNA Model API](#4.1). For details on how the model is loaded from distribution platforms, see [Model Weights and Distribution](#2.3). For evaluation metrics and benchmarking, see [Evaluation System](#5).

## Overview

AlphaGenome is a unified DNA sequence model designed to predict regulatory variant effects across multiple genomic modalities. The model architecture is implemented in JAX and uses dm-haiku for neural network construction. It can process DNA sequences of up to 1 million base pairs and produces single base-pair resolution predictions for:

- Gene expression (RNA-seq)
- Splicing patterns (donor/acceptor sites)
- Chromatin accessibility (ATAC-seq, DNase-seq)
- Transcription factor binding (ChIP-seq)
- Chromatin contact maps

The architecture follows a three-layer design pattern:

1. **Core Model Layer**: JAX/Haiku neural network implementation
2. **Wrapper Layer**: DNA Model class providing high-level inference API
3. **Data Integration Layer**: Schemas and type definitions for inputs/outputs

Sources: [README.md:13-17](), [README.md:21-22]()

## System Architecture

```mermaid
graph TB
    subgraph "External Inputs"
        DNA["DNA Sequence<br/>(up to 1M bp)"]
        VAR["Variant Information<br/>genome.Variant"]
        ONTO["Ontology Terms<br/>(tissue/cell types)"]
        WEIGHTS["Model Weights<br/>(Orbax checkpoints)"]
    end
    
    subgraph "DNA Model Wrapper"
        FACTORY["Factory Methods<br/>create_from_kaggle()<br/>create_from_huggingface()"]
        DNAMODEL["DNA Model Class<br/>model/dna_model.py"]
        PREDICTOR["Prediction Methods<br/>predict_variant()<br/>predict_sequence()"]
    end
    
    subgraph "Core Model Implementation"
        HAIKU["Haiku Transform<br/>hk.transform()"]
        JAXCORE["AlphaGenome Core<br/>JAX Neural Network"]
        PRECISION["Mixed Precision<br/>hk.mixed_precision.set_policy()"]
        PARAMS["Model Parameters<br/>(replicated on devices)"]
    end
    
    subgraph "Data Structures"
        SCHEMAS["schemas.py<br/>Type Definitions"]
        BUNDLES["bundles.py<br/>BundleName enums"]
        DATABATCH["DataBatch<br/>Input Structure"]
        OUTPUTS["Model Outputs<br/>Multi-modal predictions"]
    end
    
    subgraph "Output Processing"
        EXTRACT["extract_predictions()<br/>Post-processing"]
        VARIANTOUT["VariantPrediction<br/>reference + alternate"]
        MODALITY["Output Modalities<br/>rna_seq, atac, dnase<br/>chip_tf, splice_*"]
    end
    
    WEIGHTS --> FACTORY
    FACTORY --> DNAMODEL
    
    DNA --> DNAMODEL
    VAR --> DNAMODEL
    ONTO --> DNAMODEL
    
    DNAMODEL --> PREDICTOR
    PREDICTOR --> HAIKU
    
    HAIKU --> JAXCORE
    PRECISION --> JAXCORE
    PARAMS --> JAXCORE
    
    SCHEMAS --> DATABATCH
    BUNDLES --> SCHEMAS
    DATABATCH --> JAXCORE
    
    JAXCORE --> OUTPUTS
    OUTPUTS --> EXTRACT
    
    EXTRACT --> VARIANTOUT
    VARIANTOUT --> MODALITY
    
    style JAXCORE fill:#f9f9f9
    style DNAMODEL fill:#f9f9f9
    style DATABATCH fill:#f9f9f9
```

**Figure 1: AlphaGenome Model Architecture Components**

This diagram shows how external inputs flow through the model layers. The DNA Model wrapper provides factory methods for loading weights and high-level prediction methods. The core JAX implementation uses Haiku transforms with mixed precision support. Data structures defined in schemas.py ensure type safety throughout the pipeline.

Sources: [README.md:80-95](), [README.md:100-138]()

## Core Components

### JAX and Haiku Implementation

The AlphaGenome model is implemented using JAX, a high-performance numerical computing library with automatic differentiation and XLA compilation. The neural network architecture is constructed using dm-haiku (Haiku), which provides a functional programming interface for building neural networks in JAX.

Key characteristics of the JAX/Haiku implementation:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Computation Framework | JAX | Automatic differentiation, JIT compilation, device parallelism |
| Neural Network Library | dm-haiku | Functional neural network construction and parameter management |
| Checkpoint Format | Orbax | Model weight serialization and restoration |
| Precision Policy | hk.mixed_precision | Mixed precision training and inference for efficiency |
| Device Support | CUDA/TPU | GPU acceleration (H100+) and TPU training (v3+) |

The Haiku `transform()` function converts stateful neural network code into pure functions that separate parameter initialization from forward pass computation. This functional approach enables efficient JAX transformations like `jit` (just-in-time compilation) and `pmap` (parallel map across devices).

Sources: [README.md:21-22](), [README.md:67-75](), [README.md:170]()

### Mixed Precision Support

The model supports mixed precision computation to optimize memory usage and inference speed. Mixed precision uses lower-precision (e.g., float16 or bfloat16) for most computations while maintaining critical operations in float32 for numerical stability.

The Haiku mixed precision policy (`hk.mixed_precision.set_policy()`) configures:
- Compute precision for layer operations
- Parameter storage precision
- Output precision for activations

This is particularly important for running on H100 GPUs and TPU accelerators where lower precision arithmetic provides significant performance benefits.

Sources: [README.md:67-71]()

### Data Structures and Schemas

The model uses strongly-typed data structures defined in `schemas.py` to ensure type safety and clear interfaces between components. These schemas define:

1. **Input Structures**: Format for DNA sequences, intervals, variants, and ontology terms
2. **Internal Representations**: Intermediate data formats used during model computation
3. **Output Structures**: Multi-modal prediction results with associated metadata

The `bundles.py` module defines the `BundleName` enumeration, which categorizes different output modalities:

- `ATAC`: ATAC-seq chromatin accessibility
- `DNASE`: DNase-seq chromatin accessibility  
- `RNA_SEQ`: Gene expression levels
- `CHIP_TF`: Transcription factor binding
- `SPLICE_DONOR`, `SPLICE_ACCEPTOR`, `SPLICE_POLYA`: Splicing predictions

Sources: [README.md:26]()

## Model Prediction Pipeline

```mermaid
flowchart TD
    subgraph "Input Preparation"
        INTERVAL["Genomic Interval<br/>genome.Interval"]
        VARIANT["Variant Specification<br/>genome.Variant"]
        TISSUE["Ontology Terms<br/>List[str]"]
        REQOUT["Requested Outputs<br/>List[OutputType]"]
    end
    
    subgraph "Sequence Extraction"
        FASTA["Reference Genome<br/>FASTA file"]
        REFSEQ["Reference Sequence<br/>extract + pad"]
        ALTSEQ["Alternate Sequence<br/>insert variant"]
    end
    
    subgraph "Input Encoding"
        ENCODE["One-hot Encoding<br/>A, C, G, T"]
        CONTEXT["Context Integration<br/>tissue embeddings"]
        BATCH["DataBatch Construction<br/>structured input"]
    end
    
    subgraph "Model Inference"
        PARAMS["Model Parameters<br/>(device-replicated)"]
        FORWARD["Forward Pass<br/>JAX JIT compiled"]
        JITFN["Core Model Function<br/>Haiku transformed"]
    end
    
    subgraph "Output Generation"
        RAWOUT["Raw Predictions<br/>(per-modality)"]
        REFPRED["Reference Predictions<br/>all modalities"]
        ALTPRED["Alternate Predictions<br/>all modalities"]
    end
    
    subgraph "Post-processing"
        EXTRACT["extract_predictions()"]
        FILTER["Filter by requested outputs"]
        STRUCTURE["VariantPrediction<br/>{reference, alternate}"]
    end
    
    INTERVAL --> REFSEQ
    INTERVAL --> ALTSEQ
    VARIANT --> ALTSEQ
    FASTA --> REFSEQ
    FASTA --> ALTSEQ
    TISSUE --> CONTEXT
    REQOUT --> FILTER
    
    REFSEQ --> ENCODE
    ALTSEQ --> ENCODE
    ENCODE --> BATCH
    CONTEXT --> BATCH
    
    BATCH --> FORWARD
    PARAMS --> FORWARD
    FORWARD --> JITFN
    
    JITFN --> RAWOUT
    RAWOUT --> REFPRED
    RAWOUT --> ALTPRED
    
    REFPRED --> EXTRACT
    ALTPRED --> EXTRACT
    EXTRACT --> FILTER
    FILTER --> STRUCTURE
    
    style JITFN fill:#f9f9f9
    style BATCH fill:#f9f9f9
    style STRUCTURE fill:#f9f9f9
```

**Figure 2: Model Prediction Pipeline Data Flow**

This diagram illustrates the end-to-end prediction pipeline from input preparation through output generation. The model performs dual predictions on both reference and alternate sequences, enabling variant effect quantification by comparing the outputs.

Sources: [README.md:100-138]()

### Prediction Methods

The DNA Model class provides several prediction methods:

| Method | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `predict_variant()` | Predict effect of a variant | Interval, Variant, Ontology terms, Output types | VariantPrediction (ref + alt) |
| `predict_sequence()` | Predict on sequence without variant | DNA sequence, Ontology terms, Output types | Model predictions |
| `score_variant()` | Compute variant effect score | Same as predict_variant | Numerical scores per modality |

The `predict_variant()` method is the primary interface, demonstrated in the quick start example:

```python
outputs = model.predict_variant(
    interval=interval,
    variant=variant,
    ontology_terms=['UBERON:0001157'],
    requested_outputs=[dna_model.OutputType.RNA_SEQ],
)
```

This returns a `VariantPrediction` object containing both reference and alternate predictions, allowing comparison to assess variant impact.

Sources: [README.md:97-138]()

## Output Modalities

The model produces predictions across multiple genomic modalities, each corresponding to different types of experimental data:

```mermaid
graph LR
    subgraph "Model Core"
        CORE["AlphaGenome<br/>JAX Model"]
    end
    
    subgraph "Output Heads"
        RNA["RNA_SEQ Head<br/>Gene expression"]
        ATAC["ATAC Head<br/>Chromatin accessibility"]
        DNASE["DNase Head<br/>Chromatin accessibility"]
        CHIP["CHIP_TF Head<br/>TF binding"]
        SD["SPLICE_DONOR Head<br/>Splice donor sites"]
        SA["SPLICE_ACCEPTOR Head<br/>Splice acceptor sites"]
        SP["SPLICE_POLYA Head<br/>PolyA sites"]
    end
    
    subgraph "Prediction Outputs"
        RNASEQ["RNA-seq Tracks<br/>Base-pair resolution"]
        ATACSEQ["ATAC-seq Tracks<br/>Accessibility scores"]
        DNASESEQ["DNase-seq Tracks<br/>Accessibility scores"]
        TFBIND["TF Binding Tracks<br/>Per-factor scores"]
        DONOR["Donor Probabilities<br/>Splice site strength"]
        ACCEPTOR["Acceptor Probabilities<br/>Splice site strength"]
        POLYA["PolyA Probabilities<br/>Cleavage sites"]
    end
    
    CORE --> RNA
    CORE --> ATAC
    CORE --> DNASE
    CORE --> CHIP
    CORE --> SD
    CORE --> SA
    CORE --> SP
    
    RNA --> RNASEQ
    ATAC --> ATACSEQ
    DNASE --> DNASESEQ
    CHIP --> TFBIND
    SD --> DONOR
    SA --> ACCEPTOR
    SP --> POLYA
    
    style CORE fill:#f9f9f9
```

**Figure 3: Model Output Modalities**

Each output head produces predictions at single base-pair resolution across the input sequence window. The model can simultaneously predict across all modalities or be configured to output specific subsets.

### Modality Characteristics

| Modality | Resolution | Output Type | Use Case |
|----------|-----------|-------------|----------|
| RNA_SEQ | Per base | Continuous expression levels | Gene expression prediction, eQTL analysis |
| ATAC | Per base | Continuous accessibility scores | Chromatin state, regulatory element identification |
| DNASE | Per base | Continuous accessibility scores | Open chromatin regions, enhancer prediction |
| CHIP_TF | Per base, per TF | Continuous binding scores | Transcription factor binding sites |
| SPLICE_DONOR | Per base | Probability [0,1] | Donor splice site prediction, sQTL analysis |
| SPLICE_ACCEPTOR | Per base | Probability [0,1] | Acceptor splice site prediction |
| SPLICE_POLYA | Per base | Probability [0,1] | Polyadenylation site prediction |

Sources: [README.md:13-17]()

## Device Management and Parallelism

The model supports execution across multiple accelerators for efficient inference:

```mermaid
graph TB
    subgraph "Model Parameters"
        CKPT["Checkpoint File<br/>Orbax format"]
        RESTORE["orbax.checkpoint.restore()"]
        PARAMS["Parameter Pytree"]
    end
    
    subgraph "Device Management"
        DEVICES["JAX Devices<br/>jax.devices()"]
        REPLICATE["Parameter Replication<br/>jax.device_put_replicated()"]
        SHARDING["Device Sharding<br/>(optional)"]
    end
    
    subgraph "Execution"
        PMAP["Parallel Map<br/>jax.pmap()"]
        JIT["JIT Compilation<br/>jax.jit()"]
        BATCH_PROCESS["Batch Processing<br/>across devices"]
    end
    
    subgraph "Hardware Support"
        GPU["NVIDIA GPUs<br/>(H100 recommended)"]
        TPU["TPUs<br/>(v3+ for training)"]
        CPU["CPU Fallback<br/>(limited performance)"]
    end
    
    CKPT --> RESTORE
    RESTORE --> PARAMS
    
    DEVICES --> REPLICATE
    PARAMS --> REPLICATE
    REPLICATE --> PMAP
    REPLICATE --> SHARDING
    
    PMAP --> JIT
    JIT --> BATCH_PROCESS
    
    BATCH_PROCESS --> GPU
    BATCH_PROCESS --> TPU
    BATCH_PROCESS --> CPU
    
    style PARAMS fill:#f9f9f9
    style BATCH_PROCESS fill:#f9f9f9
```

**Figure 4: Device Management and Parallelism**

The model parameters are replicated across available devices for parallel batch processing. JAX's `pmap` transformation enables data parallelism, where different examples in a batch are processed on different devices. JIT compilation optimizes the computation graph for the target hardware.

### Hardware Requirements

**Inference Requirements:**
- Minimum: NVIDIA H100 GPU with CUDA and cuDNN support
- Recommended: Multi-GPU setup for batch processing
- JAX installation with GPU support required

**Training Requirements:**
- Minimum: TPU v3 or higher
- Configuration for large-scale distributed training

The model leverages JAX's device abstraction to automatically utilize available accelerators. Users must ensure proper JAX installation with GPU/TPU support as documented in the [JAX installation guide](https://docs.jax.dev/en/latest/installation.html#nvidia-gpu).

Sources: [README.md:67-75]()

## Integration with Data I/O System

The model architecture integrates with the Data I/O system (see [Data I/O System](#3)) through well-defined interfaces:

```mermaid
graph LR
    subgraph "Data I/O Layer"
        DATASET["dataset.py<br/>TFRecord Loader"]
        GENOME["genome.py<br/>Variant Integration"]
        FASTA["fasta.py<br/>FastaExtractor"]
        BUNDLES["bundles.py<br/>BundleName"]
    end
    
    subgraph "Data Transformation"
        EXTRACT["Sequence Extraction"]
        VARIANT_INS["insert_reference_variant()<br/>insert_alternate_variant()"]
        BATCH_BUILD["DataBatch Construction"]
    end
    
    subgraph "Model Layer"
        SCHEMAS["schemas.py<br/>Type Definitions"]
        DNAMODEL["DNA Model Class"]
        CORE["AlphaGenome Core<br/>JAX Model"]
    end
    
    subgraph "Output Layer"
        PREDICTIONS["Multi-modal Predictions"]
        METRICS["Evaluation Metrics"]
    end
    
    DATASET --> BATCH_BUILD
    FASTA --> EXTRACT
    GENOME --> VARIANT_INS
    BUNDLES --> SCHEMAS
    
    EXTRACT --> VARIANT_INS
    VARIANT_INS --> BATCH_BUILD
    
    BATCH_BUILD --> DNAMODEL
    SCHEMAS --> DNAMODEL
    DNAMODEL --> CORE
    
    CORE --> PREDICTIONS
    PREDICTIONS --> METRICS
    
    style CORE fill:#f9f9f9
    style BATCH_BUILD fill:#f9f9f9
```

**Figure 5: Model Integration with Data I/O**

The Data I/O layer provides sequence extraction and variant integration functions that produce properly formatted inputs for the model. The `DataBatch` structure, defined in schemas, ensures type consistency between data loading and model inference. Bundle definitions from `bundles.py` specify which output modalities to generate.

Sources: [README.md:26]()

## Model Loading and Initialization

The DNA Model class provides factory methods that abstract the complexity of loading model weights and initializing the JAX computational graph:

### Factory Method Flow

```mermaid
flowchart TD
    USER["User Code"]
    
    subgraph "Factory Methods"
        KAGGLE["create_from_kaggle(model_id)"]
        HF["create_from_huggingface(model_id)"]
    end
    
    subgraph "Weight Download"
        KAGGLE_API["kagglehub.model_download()"]
        HF_API["huggingface_hub.snapshot_download()"]
        CACHE["Local Cache<br/>(~/.cache/)"]
    end
    
    subgraph "Model Construction"
        META["metadata_lib.load()<br/>Organism metadata"]
        RESTORE["orbax.checkpoint.restore()<br/>Parameter restoration"]
        HAIKU_INIT["hk.transform()<br/>Create pure functions"]
        PRECISION_SET["hk.mixed_precision.set_policy()"]
    end
    
    subgraph "DNA Model Instance"
        INSTANCE["DNA Model Object<br/>Ready for inference"]
        PARAMS_STORED["Parameters<br/>(device-replicated)"]
        PREDICT_FN["Prediction Functions<br/>(JIT-compiled)"]
    end
    
    USER --> KAGGLE
    USER --> HF
    
    KAGGLE --> KAGGLE_API
    HF --> HF_API
    
    KAGGLE_API --> CACHE
    HF_API --> CACHE
    
    CACHE --> META
    CACHE --> RESTORE
    
    META --> HAIKU_INIT
    RESTORE --> PARAMS_STORED
    PRECISION_SET --> HAIKU_INIT
    
    HAIKU_INIT --> PREDICT_FN
    PARAMS_STORED --> INSTANCE
    PREDICT_FN --> INSTANCE
    
    INSTANCE --> USER
    
    style INSTANCE fill:#f9f9f9
    style HAIKU_INIT fill:#f9f9f9
```

**Figure 6: Model Loading and Initialization Flow**

The factory methods handle:
1. Downloading weights from Kaggle or HuggingFace (requires acceptance of model terms)
2. Loading organism-specific metadata for proper configuration
3. Restoring checkpoint parameters using Orbax
4. Initializing the Haiku transform with mixed precision policies
5. Creating JIT-compiled prediction functions
6. Replicating parameters across available devices

Example usage:

```python
# Load from Kaggle
model = dna_model.create_from_kaggle('all_folds')

# Load from HuggingFace
model = dna_model.create_from_huggingface('all_folds')
```

Both methods return a fully initialized DNA Model instance ready for making predictions.

Sources: [README.md:54-63](), [README.md:84-95](), [README.md:171-176]()

## Summary

The AlphaGenome model architecture consists of:

1. **JAX/Haiku Core**: Functional neural network implementation with automatic differentiation and JIT compilation
2. **DNA Model Wrapper**: High-level API abstracting model complexity and providing intuitive prediction methods
3. **Type-Safe Data Structures**: Schemas ensuring consistency across data loading, model inference, and output processing
4. **Multi-Modal Output Heads**: Simultaneous predictions across RNA-seq, chromatin accessibility, TF binding, and splicing
5. **Device Management**: Support for multi-GPU and TPU execution with parameter replication and batch parallelism
6. **Distribution Infrastructure**: Factory methods for loading weights from Kaggle and HuggingFace

The architecture emphasizes:
- **Reproducibility**: Versioned checkpoints and metadata
- **Efficiency**: Mixed precision, JIT compilation, device parallelism
- **Usability**: Clean API separating low-level JAX operations from high-level prediction interface
- **Scalability**: Support for large sequences (up to 1M bp) and batch processing

For detailed information on using the DNA Model API, see [DNA Model API](#4.1). For evaluation workflows and metrics, see [Evaluation System](#5).

Sources: [README.md:13-31](), [README.md:67-75]()

---

