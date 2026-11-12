<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/personality_in_llms · page 5 Analysis System · fetched 2026-10-26 -->

# Analysis System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [analysis/construct_validity_analysis_template.ipynb](analysis/construct_validity_analysis_template.ipynb)
- [analysis/downstream_task_analysis_template.ipynb](analysis/downstream_task_analysis_template.ipynb)
- [analysis/trait_shaping_analysis_template.ipynb](analysis/trait_shaping_analysis_template.ipynb)

</details>



The Analysis System provides comprehensive tools for analyzing personality traits in Large Language Models through three specialized Jupyter notebook templates. This system enables researchers to evaluate trait shaping effectiveness, validate personality measures, and correlate psychometric scores with downstream behaviors. For information about the underlying psychometric framework, see [PsyBORGS Framework](#3). For details about data collection through inference, see [Inference System](#4).

## Overview

The Analysis System consists of three primary notebook templates that work together to provide complete personality analysis capabilities:

```mermaid
graph TB
    subgraph "Input Data"
        PKL["Personality Test Results<br/>(PKL files)"]
        AMS["AMS Predictions<br/>(CSV files)"]
        STATUS["Status Updates<br/>(Generated Content)"]
        ADMIN["Admin Sessions<br/>(JSON configs)"]
    end
    
    subgraph "Analysis Templates"
        TSA["trait_shaping_analysis_template.ipynb<br/>Trait Shaping Effectiveness"]
        DTA["downstream_task_analysis_template.ipynb<br/>Behavior Correlation Analysis"]
        CVA["construct_validity_analysis_template.ipynb<br/>Psychometric Validation"]
    end
    
    subgraph "Statistical Methods"
        CORR["Correlation Analysis<br/>pearsonr, spearmanr"]
        REL["Reliability Analysis<br/>alpha, omega, G6"]
        VAL["Validity Analysis<br/>Convergent/Discriminant"]
    end
    
    subgraph "Output"
        VIZ["Visualizations<br/>Histograms, Plots"]
        STATS["Statistical Reports<br/>Correlation Matrices"]
        SCORES["Scored DataFrames<br/>For Further Analysis"]
    end
    
    PKL --> TSA
    PKL --> DTA
    PKL --> CVA
    ADMIN --> TSA
    ADMIN --> CVA
    AMS --> DTA
    STATUS --> DTA
    
    TSA --> CORR
    TSA --> REL
    DTA --> CORR
    CVA --> VAL
    CVA --> REL
    
    CORR --> STATS
    REL --> STATS
    VAL --> STATS
    
    TSA --> VIZ
    DTA --> VIZ
    CVA --> VIZ
    
    TSA --> SCORES
    CVA --> SCORES
```

Sources: [analysis/trait_shaping_analysis_template.ipynb:1-706](), [analysis/downstream_task_analysis_template.ipynb:1-1401](), [analysis/construct_validity_analysis_template.ipynb:1-1298]()

## Analysis Templates

### Trait Shaping Analysis Template

The `trait_shaping_analysis_template.ipynb` evaluates how effectively models can simulate controlled personality traits. This template supports both independent trait shaping (one trait at a time) and multidimensional trait shaping (multiple traits simultaneously).

```mermaid
graph LR
    subgraph "Configuration"
        PATH["PATH<br/>Project Root"]
        PKL_PATH["PKL_PATH<br/>Results File"]
        ADMIN_SESSION_PATH["ADMIN_SESSION_PATH<br/>Config JSON"]
        MULTI_SHAPING["MULTI_SHAPING<br/>Boolean Flag"]
    end
    
    subgraph "Core Processing"
        LOAD["load_admin_session()<br/>survey_bench_lib"]
        SCORE["score_session()<br/>score_calculation"]
        EXTRACT["add_ordinal_levels()<br/>Extract Trait Levels"]
    end
    
    subgraph "Analysis Functions"
        CORR_MAIN["main()<br/>Correlation Computation"]
        REL_R["run_reliability_analysis_in_r()<br/>R-based Reliability"]
        DESC["describe_by_preambles()<br/>Descriptive Statistics"]
    end
    
    PATH --> LOAD
    PKL_PATH --> SCORE
    ADMIN_SESSION_PATH --> LOAD
    LOAD --> SCORE
    SCORE --> EXTRACT
    EXTRACT --> CORR_MAIN
    SCORE --> REL_R
    SCORE --> DESC
```

Key functionality includes:
- Loading and scoring personality test responses using [analysis/trait_shaping_analysis_template.ipynb:154-161]()
- Computing correlations between intended trait levels and observed scores [analysis/trait_shaping_analysis_template.ipynb:578-637]()
- Reliability analysis through R integration [analysis/trait_shaping_analysis_template.ipynb:514-535]()
- Descriptive statistics by personality prompts [analysis/trait_shaping_analysis_template.ipynb:221-275]()

Sources: [analysis/trait_shaping_analysis_template.ipynb:1-706]()

### Downstream Task Analysis Template

The `downstream_task_analysis_template.ipynb` analyzes how personality test scores correlate with generated content in downstream tasks, particularly social media status updates.

```mermaid
graph TB
    subgraph "Input Data Sources"
        UNIDIMENSIONAL["UNIDIMENSIONAL_SHAPING_SCORES<br/>Personality Test Scores"]
        STATUS_DATA["STATUS_UPDATES_DATA<br/>Generated Content"]
        AMS_DATA["AMS_DATA<br/>Automated Predictions"]
    end
    
    subgraph "Data Processing"
        GROUP["groupby('item_preamble_id')<br/>Consolidate Updates"]
        PIVOT["pivot()<br/>Transform AMS Data"]
        JOIN["join()<br/>Merge Datasets"]
    end
    
    subgraph "Scale Constants"
        IPIP_SCALES["IPIP_SCALE_IDS<br/>['IPIP300-EXT', 'IPIP300-AGR', ...]"]
        AMS_SCALES["AMS_SCALE_IDS_2<br/>['BIG5_Extraversion', ...]"]
        LVL_IDS["LVL_IDS<br/>['lvl-EXT', 'lvl-AGR', ...]"]
    end
    
    subgraph "Statistical Analysis"
        PEARSON["pearsonr()<br/>Linear Correlation"]
        SPEARMAN["spearmanr()<br/>Rank Correlation"]
    end
    
    UNIDIMENSIONAL --> JOIN
    STATUS_DATA --> GROUP
    AMS_DATA --> PIVOT
    GROUP --> JOIN
    PIVOT --> JOIN
    
    IPIP_SCALES --> PEARSON
    AMS_SCALES --> PEARSON
    LVL_IDS --> SPEARMAN
    
    JOIN --> PEARSON
    JOIN --> SPEARMAN
```

The template performs correlation analysis between:
- IPIP-300 personality scores and AMS predicted personality traits [analysis/downstream_task_analysis_template.ipynb:314-330]()
- Prompted personality levels and downstream personality predictions [analysis/downstream_task_analysis_template.ipynb:358-377]()

Sources: [analysis/downstream_task_analysis_template.ipynb:1-1401]()

### Construct Validity Analysis Template

The `construct_validity_analysis_template.ipynb` provides comprehensive psychometric validation of personality measures across different models and conditions.

```mermaid
graph TB
    subgraph "Personality Measures"
        BFI["BFI_SCALE_IDS<br/>Big Five Inventory"]
        IPIP["IPIP_SCALE_IDS<br/>IPIP-NEO-300"]
        PANAS["PA, NA<br/>Positive/Negative Affect"]
        VALIDATION["VALIDATION_SCALE_IDS<br/>11 Criterion Measures"]
    end
    
    subgraph "Validity Analysis Functions"
        CONVERGENT["get_convergent_corrs()<br/>Same-trait Correlations"]
        DISCRIMINANT["get_avg_discriminant_corrs()<br/>Different-trait Correlations"]
        MTMM["Multi-trait Multi-method Matrix"]
    end
    
    subgraph "Statistical Functions"
        CALC_P["calculate_pvalues()<br/>Significance Testing"]
        DIAG_OFFDIAG["get_diag_offdiag_diffs()<br/>Validity Ratios"]
        REL_R["run_reliability_analysis_in_r()<br/>Reliability Indices"]
    end
    
    BFI --> CONVERGENT
    IPIP --> CONVERGENT
    CONVERGENT --> DISCRIMINANT
    DISCRIMINANT --> MTMM
    
    MTMM --> DIAG_OFFDIAG
    BFI --> CALC_P
    IPIP --> CALC_P
    VALIDATION --> CALC_P
    
    BFI --> REL_R
    IPIP --> REL_R
```

Key validation analyses include:
- Multitrait-multimethod correlation matrices [analysis/construct_validity_analysis_template.ipynb:760-780]()
- Convergent and discriminant validity assessment [analysis/construct_validity_analysis_template.ipynb:839-921]()
- Cross-measure criterion validity [analysis/construct_validity_analysis_template.ipynb:1019-1138]()

Sources: [analysis/construct_validity_analysis_template.ipynb:1-1298]()

## Data Flow and Integration

The analysis system processes multiple data types through a standardized pipeline:

```mermaid
flowchart LR
    subgraph "Raw Data"
        PKL_RAW["df_raw_response_scores<br/>Pickled Results"]
        ADMIN_JSON["admin_session<br/>JSON Configuration"]
        STATUS_PKL["status_updates_raw<br/>Generated Content"]
        AMS_CSV["ams_predictions_raw<br/>CSV Predictions"]
    end
    
    subgraph "Processing Functions"
        SCORE_CALC["score_calculation.score_session()<br/>Apply Psychometric Scoring"]
        GROUP_FUNC["groupby().agg()<br/>Aggregate by Profile"]
        JOIN_FUNC["join()/merge()<br/>Combine Datasets"]
    end
    
    subgraph "Scored Data"
        SCORED_DF["scored_session_df<br/>Personality Scores"]
        JOINED_DF["df_grouped<br/>Multi-source Dataset"]
        FINAL_DF["scored_joined<br/>Complete Analysis Dataset"]
    end
    
    PKL_RAW --> SCORE_CALC
    ADMIN_JSON --> SCORE_CALC
    SCORE_CALC --> SCORED_DF
    
    STATUS_PKL --> GROUP_FUNC
    AMS_CSV --> GROUP_FUNC
    GROUP_FUNC --> JOINED_DF
    
    SCORED_DF --> JOIN_FUNC
    JOINED_DF --> JOIN_FUNC
    JOIN_FUNC --> FINAL_DF
```

The system uses standardized identifiers for data integration:
- `item_preamble_id`: Links personality prompts across datasets [analysis/downstream_task_analysis_template.ipynb:476-489]()
- `partial_id`: Extracted identifier for matching across experiments [analysis/downstream_task_analysis_template.ipynb:476-481]()
- `SPID` combinations: Simulated participant identifiers for joining measures [analysis/construct_validity_analysis_template.ipynb:639-704]()

Sources: [analysis/trait_shaping_analysis_template.ipynb:174-196](), [analysis/downstream_task_analysis_template.ipynb:471-490](), [analysis/construct_validity_analysis_template.ipynb:634-720]()

## Statistical Analysis Methods

### Correlation Analysis

The system implements multiple correlation methods to assess relationships between variables:

```mermaid
graph TB
    subgraph "Correlation Types"
        PEARSON["pearsonr()<br/>Linear Relationships"]
        SPEARMAN["spearmanr()<br/>Monotonic Relationships"]
    end
    
    subgraph "Analysis Contexts"
        TRAIT_LEVEL["Intended vs Observed Traits<br/>LVL_IDS → IPIP_SCALE_IDS"]
        CROSS_MEASURE["Cross-measure Validation<br/>BFI_SCALE_IDS ↔ IPIP_SCALE_IDS"]
        DOWNSTREAM["Personality → Behavior<br/>Test Scores → Generated Content"]
    end
    
    subgraph "Statistical Functions"
        MAIN_CORR["main()<br/>Trait Shaping Correlations"]
        CALC_PVAL["calculate_pvalues()<br/>Significance Testing"]
        GROUP_CORR["groupby().corr()<br/>Model-specific Analysis"]
    end
    
    PEARSON --> TRAIT_LEVEL
    SPEARMAN --> TRAIT_LEVEL
    PEARSON --> CROSS_MEASURE
    PEARSON --> DOWNSTREAM
    
    TRAIT_LEVEL --> MAIN_CORR
    CROSS_MEASURE --> CALC_PVAL
    DOWNSTREAM --> GROUP_CORR
```

Sources: [analysis/trait_shaping_analysis_template.ipynb:578-620](), [analysis/downstream_task_analysis_template.ipynb:314-377](), [analysis/construct_validity_analysis_template.ipynb:434-447]()

### Reliability Analysis

Reliability assessment uses R-based psychometric functions:

```mermaid
graph LR
    subgraph "R Integration"
        R_LAUNCH["launch_r_instance()<br/>Initialize R Environment"]
        R_SOURCE["r['source']()<br/>Load psychometric_utils.R"]
        R_CONVERT["pandas2ri.converter<br/>DataFrame Conversion"]
    end
    
    subgraph "Reliability Indices"
        ALPHA["Cronbach's Alpha<br/>Internal Consistency"]
        OMEGA["McDonald's Omega<br/>Composite Reliability"]
        G6["Guttman's Lambda 6<br/>Lower Bound Estimate"]
    end
    
    subgraph "Analysis Function"
        SUBSCALE_REL["subscale_reliability_r()<br/>Per-scale Computation"]
        COMPUTE_REL["compute_reliability_indices_per_scale()<br/>Batch Processing"]
    end
    
    R_LAUNCH --> R_SOURCE
    R_SOURCE --> SUBSCALE_REL
    R_CONVERT --> SUBSCALE_REL
    
    SUBSCALE_REL --> ALPHA
    SUBSCALE_REL --> OMEGA
    SUBSCALE_REL --> G6
    
    ALPHA --> COMPUTE_REL
    OMEGA --> COMPUTE_REL
    G6 --> COMPUTE_REL
```

The reliability analysis function iterates through all measures and scales in an admin session, computing multiple reliability indices with error handling [analysis/trait_shaping_analysis_template.ipynb:476-512]().

Sources: [analysis/trait_shaping_analysis_template.ipynb:451-535](), [analysis/construct_validity_analysis_template.ipynb:1164-1248]()

## Analysis Workflow

### Template Configuration

Each analysis template requires specific configuration parameters:

| Parameter | Trait Shaping | Downstream Task | Construct Validity |
|-----------|---------------|-----------------|-------------------|
| `PATH` | Project root directory | Project root directory | Project root directory |
| `PKL_PATH` | Results pickle file | Shaping scores pickle | Results pickle file |
| `ADMIN_SESSION_PATH` | Admin session JSON | N/A | Admin session JSON |
| `MULTI_SHAPING` | Boolean flag | N/A | N/A |
| `STATUS_UPDATES_DATA` | N/A | Generated content pickle | N/A |
| `AMS_DATA` | N/A | AMS predictions CSV | N/A |
| `MODEL_POINTER` | N/A | N/A | Model identifier string |

### Data Processing Pipeline

The analysis workflow follows a standardized sequence:

1. **Data Loading**: Import pickled results and configuration files [analysis/trait_shaping_analysis_template.ipynb:154-161]()
2. **Scoring**: Apply psychometric scoring using the PsyBORGS framework [analysis/trait_shaping_analysis_template.ipynb:174-196]()
3. **Data Transformation**: Extract levels, create identifiers, and join datasets [analysis/downstream_task_analysis_template.ipynb:476-490]()
4. **Statistical Analysis**: Compute correlations, reliability indices, and validity metrics
5. **Visualization**: Generate histograms, correlation matrices, and summary statistics

### Output Generation

The system produces multiple output types:
- **Scored DataFrames**: Can be saved for further analysis using `SAVE_SCORES_FILENAME` [analysis/trait_shaping_analysis_template.ipynb:205-208]()
- **Statistical Reports**: Correlation coefficients, p-values, and reliability indices
- **Visualizations**: Distribution plots and descriptive statistics tables

Sources: [analysis/trait_shaping_analysis_template.ipynb:1-706](), [analysis/downstream_task_analysis_template.ipynb:1-1401](), [analysis/construct_validity_analysis_template.ipynb:1-1298]()

---

