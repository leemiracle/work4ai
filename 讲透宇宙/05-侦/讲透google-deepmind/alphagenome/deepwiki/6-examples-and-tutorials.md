<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphagenome · page 6 Examples and Tutorials · fetched 2026-10-26 -->

# Examples and Tutorials

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [colabs/quick_start.ipynb](colabs/quick_start.ipynb)
- [docs/source/tutorials/index.md](docs/source/tutorials/index.md)

</details>



This section provides practical tutorials demonstrating key workflows with the AlphaGenome SDK. Each tutorial is a self-contained Jupyter notebook that can be run in Google Colab or locally.

The tutorials cover:
- Basic prediction workflows (quick_start.ipynb)
- Batch processing of variants (batch_variant_scoring.ipynb)
- Interactive variant analysis (variant_scoring_ui.ipynb)
- Visualization techniques (visualization_modality_tour.ipynb)
- Complete research workflows (example_analysis_workflow.ipynb)
- Biological context mapping (tissue_ontology_mapping.ipynb)

## Tutorial Structure and Dependencies

The tutorials build on each other, starting with basic concepts and progressing to advanced workflows.

**Tutorial Dependency Graph**

```mermaid
graph TB
    QS["quick_start.ipynb<br/>Basic Predictions"]
    BVS["batch_variant_scoring.ipynb<br/>Batch Processing"]
    VMT["visualization_modality_tour.ipynb<br/>Visualization"]
    VSU["variant_scoring_ui.ipynb<br/>Interactive UI"]
    EAW["example_analysis_workflow.ipynb<br/>Complete Workflow"]
    TOM["tissue_ontology_mapping.ipynb<br/>Ontology Mapping"]
    
    QS --> BVS
    QS --> VMT
    QS --> VSU
    BVS --> EAW
    VMT --> EAW
    TOM --> EAW
    
    style QS fill:#e1f5ff
    style EAW fill:#fff3e0
```

**Sources:** [colabs/quick_start.ipynb:1-100](), [docs/source/tutorials/index.md:1-56]()

## Core Concepts Across Tutorials

All tutorials use these fundamental SDK components:

**Key SDK Components**

```mermaid
graph LR
    subgraph "Model Interface"
        DC["dna_client.create()"]
        PM["predict_sequence()"]
        PI["predict_interval()"]
        PV["predict_variant()"]
        SV["score_variant()"]
    end
    
    subgraph "Data Structures"
        GI["genome.Interval"]
        GV["genome.Variant"]
        TD["TrackData"]
        VO["VariantOutput"]
    end
    
    subgraph "Analysis Tools"
        VS["variant_scorers"]
        TS["tidy_scores()"]
        GA["gene_annotation"]
    end
    
    subgraph "Visualization"
        PC["plot_components"]
        TA["TranscriptAnnotation"]
        VA["VariantAnnotation"]
    end
    
    DC --> PM
    DC --> PI
    DC --> PV
    DC --> SV
    
    PM --> TD
    PI --> TD
    PV --> VO
    SV --> TS
    
    GI --> PI
    GV --> PV
    
    GA --> TA
    TD --> PC
```

**Sources:** [colabs/quick_start.ipynb:90-152]()

## Batch Variant Scoring Tutorial

The batch variant scoring tutorial demonstrates efficient processing of multiple genomic variants using the AlphaGenome API. This workflow is essential for large-scale genomic analyses.

### Core Workflow Components

```mermaid
graph LR
    subgraph "Input Preparation"
        VCF_FILE["VCF DataFrame<br/>variant_id, CHROM, POS, REF, ALT"]
        VAR_DEF["genome.Variant<br/>chromosome, position, reference_bases, alternate_bases"]
    end
    
    subgraph "Scoring Configuration"
        SCORERS["variant_scorers.RECOMMENDED_VARIANT_SCORERS"]
        SEQ_LEN["dna_client.SUPPORTED_SEQUENCE_LENGTHS"]
        ORG["dna_client.Organism"]
    end
    
    subgraph "Processing Pipeline"
        SCORE_VAR["dna_model.score_variant()"]
        TIDY["variant_scorers.tidy_scores()"]
    end
    
    subgraph "Output"
        RESULTS["AnnData with raw_score, quantile_score"]
        CSV["variant_scores.csv"]
    end
    
    VCF_FILE --> VAR_DEF
    VAR_DEF --> SCORE_VAR
    SCORERS --> SCORE_VAR
    SEQ_LEN --> SCORE_VAR
    ORG --> SCORE_VAR
    SCORE_VAR --> TIDY
    TIDY --> RESULTS
    RESULTS --> CSV
```

**Sources:** [colabs/batch_variant_scoring.ipynb:666-790]()

### Variant Scorer Types

The tutorial demonstrates multiple scorer types available through `variant_scorers.RECOMMENDED_VARIANT_SCORERS`:

| Scorer Type | Output Type | Description |
|-------------|-------------|-------------|
| `GeneMaskLFCScorer` | `RNA_SEQ` | Gene expression predictions |
| `CenterMaskScorer` | `ATAC` | Chromatin accessibility |
| `CenterMaskScorer` | `DNASE` | DNase hypersensitivity |
| `CenterMaskScorer` | `CHIP_HISTONE` | Histone modifications |
| `CenterMaskScorer` | `CHIP_TF` | Transcription factor binding |

**Sources:** [colabs/batch_variant_scoring.ipynb:718-738]()

### Data Processing Pattern

```python
# Core pattern from the tutorial
for i, vcf_row in tqdm(vcf.iterrows(), total=len(vcf)):
    variant = genome.Variant(
        chromosome=str(vcf_row.CHROM),
        position=int(vcf_row.POS),
        reference_bases=vcf_row.REF,
        alternate_bases=vcf_row.ALT,
        name=vcf_row.variant_id,
    )
    interval = variant.reference_interval.resize(sequence_length)
    
    variant_scores = dna_model.score_variant(
        interval=interval,
        variant=variant,
        variant_scorers=selected_scorers,
        organism=organism,
    )
```

**Sources:** [colabs/batch_variant_scoring.ipynb:765-781]()

## Research Workflow Example: TAL1 Locus Analysis

The example analysis workflow demonstrates a complete research pipeline for studying oncogenic variants near the TAL1 gene associated with T-cell acute lymphoblastic leukemia.

### Analysis Pipeline Architecture

```mermaid
graph TB
    subgraph "Data Preparation"
        GTF["gene_annotation.filter_protein_coding()"]
        TSL["gene_annotation.filter_transcript_support_level()"]
        LT["gene_annotation.filter_to_longest_transcript()"]
        TE["transcript_utils.TranscriptExtractor"]
    end
    
    subgraph "Variant Generation"
        OV["oncogenic_tal1_variants()"]
        BG["generate_background_variants()"]
        INF["inference_df()"]
    end
    
    subgraph "Prediction & Analysis"
        PRED["dna_model.score_variant()"]
        COMP["Oncogenic vs Background Comparison"]
    end
    
    subgraph "Visualization"
        TA["plot_components.TranscriptAnnotation"]
        VA["plot_components.VariantAnnotation"]
        PLOT["plot_components.plot()"]
    end
    
    GTF --> TSL
    TSL --> LT
    LT --> TE
    TE --> TA
    
    OV --> BG
    BG --> INF
    INF --> PRED
    PRED --> COMP
    
    TA --> PLOT
    VA --> PLOT
    COMP --> PLOT
```

**Sources:** [colabs/example_analysis_workflow.ipynb:165-183](), [colabs/example_analysis_workflow.ipynb:213-354]()

### Key Analysis Functions

The workflow defines several utility functions for variant analysis:

| Function | Purpose | Key Parameters |
|----------|---------|----------------|
| `oncogenic_tal1_variants()` | Load known disease variants | Returns DataFrame with variant data |
| `generate_background_variants()` | Create control variants | `variant`, `max_number=100` |
| `vcf_row_to_variant()` | Convert DataFrame row to Variant | `vcf_row: pd.Series` |
| `inference_df()` | Prepare variants for prediction | `qtl_df`, `input_sequence_length` |

**Sources:** [colabs/example_analysis_workflow.ipynb:275-354]()

### Genomic Interval Processing

```mermaid
graph LR
    subgraph "Interval Definition"
        TAL1["genome.Interval<br/>chr1:47209255-47242023"]
        RESIZE["interval.resize(sequence_length)"]
    end
    
    subgraph "Annotation Loading"
        GENCODE["GENCODE v46 annotations"]
        FILTER["Protein coding + TSL 1"]
        EXTRACT["longest_transcript_extractor.extract()"]
    end
    
    subgraph "Variant Positioning"
        UNIQUE["unique_positions = variants['POS'].unique()"]
        LABELS["Manual label positioning"]
        VAR_ANNOT["plot_components.VariantAnnotation"]
    end
    
    TAL1 --> RESIZE
    GENCODE --> FILTER
    FILTER --> EXTRACT
    UNIQUE --> LABELS
    LABELS --> VAR_ANNOT
    EXTRACT --> VAR_ANNOT
```

**Sources:** [colabs/example_analysis_workflow.ipynb:165-183](), [colabs/example_analysis_workflow.ipynb:787-833]()

## Common Data Structures and Patterns

### Variant Creation Pattern

All tutorials follow a consistent pattern for creating `genome.Variant` objects:

```python
variant = genome.Variant(
    chromosome=str(chrom),        # Must be string format
    position=int(pos),            # 1-based coordinates
    reference_bases=ref,          # Reference allele
    alternate_bases=alt,          # Alternate allele
    name=variant_id,             # Optional identifier
)
```

**Sources:** [colabs/batch_variant_scoring.ipynb:766-772](), [colabs/example_analysis_workflow.ipynb:284-291]()

### Scoring and Output Processing

```mermaid
graph LR
    subgraph "Scoring Process"
        SV["dna_model.score_variant()"]
        PARAMS["interval, variant, variant_scorers, organism"]
    end
    
    subgraph "Result Processing" 
        RAW["Raw AnnData results"]
        TIDY["variant_scorers.tidy_scores()"]
        DF["Tidy DataFrame"]
    end
    
    subgraph "Output Columns"
        META["variant_id, scored_interval, gene_info"]
        TRACK["output_type, track_name, biosample_name"]
        SCORES["raw_score, quantile_score"]
    end
    
    PARAMS --> SV
    SV --> RAW
    RAW --> TIDY
    TIDY --> DF
    DF --> META
    DF --> TRACK  
    DF --> SCORES
```

**Sources:** [colabs/batch_variant_scoring.ipynb:775-783]()

### Visualization Integration

The tutorials demonstrate integration with the visualization system through `plot_components`:

| Component | Purpose | Key Parameters |
|-----------|---------|----------------|
| `TranscriptAnnotation` | Gene structure display | `transcript_extractor.extract(interval)` |
| `VariantAnnotation` | Variant position markers | `variants`, `labels`, `use_default_labels` |
| `plot_components.plot()` | Main plotting function | `tracks`, `annotations`, `interval`, `title` |

**Sources:** [colabs/example_analysis_workflow.ipynb:810-833]()

---

