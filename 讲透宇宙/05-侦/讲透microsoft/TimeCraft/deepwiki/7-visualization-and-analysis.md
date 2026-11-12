<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TimeCraft · page 7 Visualization and Analysis · fetched 2026-10-26 -->

# Visualization and Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [figures/TarDiff_result.png](figures/TarDiff_result.png)
- [figures/pt_like_word_small.png](figures/pt_like_word_small.png)
- [figures/timedp_indomain.png](figures/timedp_indomain.png)

</details>



This document covers the visualization tools and analysis components available in the TimeCraft framework for understanding model outputs, evaluating performance, and interpreting results from time series generation tasks. These tools support both the main TimeCraft system and its specialized implementations (TarDiff and DiGA).

For information about the core inference and generation processes, see [Inference and Generation](#6.2). For details about the specialized systems that these tools analyze, see [TarDiff: EHR Time Series Generation](#3.1) and [DiGA: Market Trading Data Generation](#3.2).

## Overview

The visualization and analysis infrastructure provides comprehensive tools for:
- Visualizing generated time series data
- Comparing synthetic vs. real data distributions  
- Evaluating model performance across different conditioning modes
- Analyzing cross-domain generation capabilities
- Monitoring training progress and convergence

```mermaid
graph TB
    subgraph "Generated Outputs"
        TS["Time Series Data"]
        SYNTH["Synthetic Samples"]
        REAL["Real Data"]
    end
    
    subgraph "Visualization Tools"
        PLOT["Plotting Functions"]
        DIST["Distribution Analysis"]
        COMP["Comparison Tools"]
    end
    
    subgraph "Analysis Components"
        TSTR["TSTR Evaluation"]
        TSRTR["TSRTR Protocol"]
        PERF["Performance Metrics"]
    end
    
    subgraph "Results"
        FIG["Result Figures"]
        METRICS["Metric Reports"]
        EVAL["Evaluation Summaries"]
    end
    
    TS --> PLOT
    SYNTH --> DIST
    REAL --> COMP
    
    PLOT --> FIG
    DIST --> TSTR
    COMP --> TSRTR
    
    TSTR --> METRICS
    TSRTR --> EVAL
    PERF --> METRICS
```

**Visualization and Analysis Pipeline**

Sources: [figures/TarDiff_result.png](), system architecture diagrams

## Result Visualization

The framework generates comprehensive visual results for different system outputs. The primary visualization capabilities include plotting generated time series, comparing distributions, and showing model performance across different conditions.

```mermaid
graph LR
    subgraph "TarDiff Results"
        TD_OUT["TarDiff Output"]
        TD_FIG["TarDiff Figures"]
    end
    
    subgraph "DiGA Results"
        DG_OUT["DiGA Output"]  
        DG_FIG["DiGA Figures"]
    end
    
    subgraph "TimeCraft Results"
        TC_OUT["TimeCraft Output"]
        TC_FIG["TimeCraft Figures"]
    end
    
    subgraph "Visualization Engine"
        PLOT_ENGINE["Plotting Engine"]
        COMP_ENGINE["Comparison Engine"]
        METRIC_ENGINE["Metrics Engine"]
    end
    
    TD_OUT --> PLOT_ENGINE
    DG_OUT --> PLOT_ENGINE  
    TC_OUT --> PLOT_ENGINE
    
    PLOT_ENGINE --> TD_FIG
    PLOT_ENGINE --> DG_FIG
    PLOT_ENGINE --> TC_FIG
    
    COMP_ENGINE --> TD_FIG
    COMP_ENGINE --> DG_FIG
    COMP_ENGINE --> TC_FIG
    
    METRIC_ENGINE --> TD_FIG
    METRIC_ENGINE --> DG_FIG
    METRIC_ENGINE --> TC_FIG
```

**Result Visualization Architecture**

Sources: [figures/TarDiff_result.png]()

## Performance Evaluation

The analysis infrastructure implements standardized evaluation protocols for assessing the quality and utility of generated time series data.

### TSTR (Train Synthetic, Test Real) Protocol

The TSTR protocol evaluates the quality of synthetic data by training models on generated samples and testing on real data. This measures how well the synthetic data captures the underlying patterns needed for downstream tasks.

### TSRTR (Train Synthetic, Test Real, Train Real) Protocol  

The TSRTR protocol provides a more comprehensive evaluation by comparing performance when training on synthetic data versus real data, helping assess the utility of generated samples for data augmentation.

```mermaid
graph TB
    subgraph "Evaluation Protocols"
        TSTR_PROTO["TSTR Protocol"]
        TSRTR_PROTO["TSRTR Protocol"]
    end
    
    subgraph "Data Sources"
        SYNTH_DATA["Synthetic Data"]
        REAL_DATA["Real Data"]
    end
    
    subgraph "Evaluation Steps"
        TRAIN_SYNTH["Train on Synthetic"]
        TEST_REAL["Test on Real"]
        TRAIN_REAL["Train on Real"]
        COMPARE["Compare Results"]
    end
    
    subgraph "Metrics"
        ACCURACY["Accuracy Metrics"]
        UTILITY["Utility Scores"]
        QUALITY["Quality Measures"]
    end
    
    SYNTH_DATA --> TRAIN_SYNTH
    REAL_DATA --> TEST_REAL
    REAL_DATA --> TRAIN_REAL
    
    TSTR_PROTO --> TRAIN_SYNTH
    TSTR_PROTO --> TEST_REAL
    
    TSRTR_PROTO --> TRAIN_SYNTH
    TSRTR_PROTO --> TEST_REAL
    TSRTR_PROTO --> TRAIN_REAL
    
    TRAIN_SYNTH --> COMPARE
    TEST_REAL --> COMPARE
    TRAIN_REAL --> COMPARE
    
    COMPARE --> ACCURACY
    COMPARE --> UTILITY
    COMPARE --> QUALITY
```

**Evaluation Protocol Architecture**

Sources: System architecture diagrams, evaluation framework references

## Analysis Components

The framework provides several specialized analysis components for different aspects of time series generation and evaluation.

### Distribution Analysis

Tools for analyzing the statistical properties of generated time series compared to real data, including:
- Marginal distribution comparisons
- Temporal correlation analysis
- Spectral analysis
- Statistical distance measurements

### Cross-Domain Analysis

Specialized analysis for evaluating the cross-domain generation capabilities of the TimeCraft system:
- Domain transfer quality assessment
- Semantic prototype effectiveness
- Few-shot learning performance evaluation

### Conditioning Analysis

Analysis tools for evaluating different conditioning modes:
- Text-based conditioning effectiveness
- Prototype-based generation quality
- Target-aware adaptation performance

```mermaid
graph TB
    subgraph "Analysis Types"
        DIST_ANALYSIS["Distribution Analysis"]
        DOMAIN_ANALYSIS["Cross-Domain Analysis"] 
        COND_ANALYSIS["Conditioning Analysis"]
    end
    
    subgraph "Analysis Tools"
        STAT_TOOLS["Statistical Tools"]
        DOMAIN_TOOLS["Domain Tools"]
        COND_TOOLS["Conditioning Tools"]
    end
    
    subgraph "Metrics Output"
        DIST_METRICS["Distribution Metrics"]
        DOMAIN_METRICS["Domain Metrics"]
        COND_METRICS["Conditioning Metrics"]
    end
    
    DIST_ANALYSIS --> STAT_TOOLS
    DOMAIN_ANALYSIS --> DOMAIN_TOOLS
    COND_ANALYSIS --> COND_TOOLS
    
    STAT_TOOLS --> DIST_METRICS
    DOMAIN_TOOLS --> DOMAIN_METRICS
    COND_TOOLS --> COND_METRICS
```

**Analysis Component Architecture**

Sources: System architecture diagrams, analysis framework references

## Integration with Core Systems

The visualization and analysis tools are integrated with the core TimeCraft systems to provide seamless evaluation and monitoring capabilities.

### TimeCraft Integration

The main TimeCraft system provides analysis hooks for:
- Semantic prototype visualization
- Cross-domain generation assessment
- Multi-modal conditioning evaluation

### TarDiff Integration

The TarDiff system includes specialized analysis for:
- EHR time series quality assessment
- Clinical performance evaluation
- Healthcare-specific metrics

### DiGA Integration

The DiGA system provides analysis capabilities for:
- Market data generation quality
- Trading strategy performance
- Financial metric evaluation

```mermaid
graph TB
    subgraph "Core Systems"
        TIMECRAFT["TimeCraft Core"]
        TARDIFF["TarDiff System"]
        DIGA["DiGA System"]
    end
    
    subgraph "Analysis Integration"
        TC_ANALYSIS["TimeCraft Analysis"]
        TD_ANALYSIS["TarDiff Analysis"]
        DG_ANALYSIS["DiGA Analysis"]
    end
    
    subgraph "Visualization Output"
        TC_VIZ["TimeCraft Visualizations"]
        TD_VIZ["TarDiff Visualizations"]
        DG_VIZ["DiGA Visualizations"]
    end
    
    TIMECRAFT --> TC_ANALYSIS
    TARDIFF --> TD_ANALYSIS
    DIGA --> DG_ANALYSIS
    
    TC_ANALYSIS --> TC_VIZ
    TD_ANALYSIS --> TD_VIZ
    DG_ANALYSIS --> DG_VIZ
```

**System Integration Architecture**

Sources: [figures/TarDiff_result.png](), system architecture diagrams

---

