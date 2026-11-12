<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/LLM-Rubric · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [poetry.lock](poetry.lock)
- [pyproject.toml](pyproject.toml)

</details>



This page provides an overview of how to set up and begin using the LLM-Rubric system for automated evaluation of natural language texts. It covers the prerequisites, system workflow, and points to detailed guides for installation and running your first evaluation.

For detailed information about the core concepts and architecture, see [Core Concepts](#3). For step-by-step guides on specific tasks, see [User Guides](#4).

## Prerequisites

The LLM-Rubric system requires:

- **Python 3.10**: The codebase is compatible with Python versions 3.10 through 3.12
- **Poetry**: Used for dependency management and installation
- **PyTorch 2.3.0**: The neural network framework used for the PersonalizedCalibrationNetwork

For complete installation instructions including platform-specific steps for PyTorch, see [Installation](#2.1).

**Sources:** [README.md:32-56](), [pyproject.toml:9-17]()

## System Workflow Overview

The LLM-Rubric evaluation process follows a structured workflow from raw data to final performance metrics:

```mermaid
graph TB
    subgraph "Data Inputs"
        CONV["Real Conversations<br/>data/real_data/"]
        RUBRIC["Manual Rubric<br/>9 Questions (Q0-Q8)"]
        SYNTH["Synthetic Training Data<br/>data/synthetic_data/"]
    end
    
    subgraph "Preprocessing"
        LLM["gpt-3.5-turbo-16k<br/>Machine Evaluations"]
        HUMAN["Human Judgments<br/>Ground Truth Annotations"]
    end
    
    subgraph "Baseline Computation"
        BS1["compute_machine_baseline.py<br/>expected_llm, argmax_llm, sample_llm"]
        BS2["compute_random_baseline.py<br/>Random predictions"]
        BS3["compute_human_baseline.py<br/>group_constant, ann_constant"]
    end
    
    subgraph "Model Training"
        HP["best_synth_cross-validation_hp.json<br/>Hyperparameters"]
        TRAIN["train_llm_rubric.py<br/>PersonalizedCalibrationNetwork"]
        SAVED["model_params.pkl<br/>judge_map.json"]
    end
    
    subgraph "Prediction & Evaluation"
        PRED["llm_rubric_predict.py<br/>Generate Predictions"]
        EVAL["evaluate.py<br/>Compute Metrics"]
        RESULTS["Performance Results<br/>Pearson, Spearman, Kendall, RMSE"]
    end
    
    CONV --> LLM
    RUBRIC --> LLM
    CONV --> HUMAN
    
    LLM --> BS1
    HUMAN --> BS2
    HUMAN --> BS3
    
    SYNTH --> TRAIN
    HP --> TRAIN
    TRAIN --> SAVED
    
    SAVED --> PRED
    LLM --> PRED
    PRED --> EVAL
    HUMAN --> EVAL
    
    BS1 --> EVAL
    BS2 --> EVAL
    BS3 --> EVAL
    
    EVAL --> RESULTS
```

**Workflow: End-to-End Evaluation Process**

The system operates in three main phases:

1. **Baseline Computation**: Establish comparison benchmarks using various strategies (machine-derived, human-derived, and random)
2. **Model Training**: Train the PersonalizedCalibrationNetwork on synthetic data with optimized hyperparameters
3. **Prediction & Evaluation**: Apply the trained model to real conversations and compute correlation metrics

**Sources:** [README.md:58-103]()

## Execution Pipeline

The following diagram shows how shell scripts orchestrate the Python modules to execute the complete pipeline:

```mermaid
graph LR
    subgraph "Shell Scripts"
        S1["run_real_data_baselines.sh"]
        S2["train_llm_rubric_for_real_data_eval.sh"]
        S3["predict_llm_rubric_for_real_data_eval.sh"]
    end
    
    subgraph "Python Modules"
        P1["llm_rubric.baselines.compute_machine_baseline"]
        P2["llm_rubric.baselines.compute_random_baseline"]
        P3["llm_rubric.baselines.compute_human_baseline"]
        P4["llm_rubric.train_llm_rubric"]
        P5["llm_rubric.llm_rubric_predict"]
    end
    
    subgraph "Core Components"
        C1["PersonalizedCalibrationNetwork<br/>llm_rubric.model.llm_rubric"]
        C2["Dataset<br/>llm_rubric.data.dataset"]
        C3["pd_utils<br/>Data transformation functions"]
    end
    
    S1 --> P1
    S1 --> P2
    S1 --> P3
    
    S2 --> P4
    P4 --> C1
    P4 --> C2
    P4 --> C3
    
    S3 --> P5
    P5 --> C1
    P5 --> C2
    P5 --> C3
```

**Execution Pipeline: Scripts to Code Entities**

**Sources:** [README.md:62-103]()

## Data Organization

The repository includes pre-processed data for immediate experimentation:

| Data Type | Location | Contents |
|-----------|----------|----------|
| Real Conversations | `data/real_data/` | Natural language conversations for evaluation |
| Human Judgments | `data/real_data/*.tsv` | Ground truth annotations from 13-24 judges |
| Machine Evaluations | `data/real_data/*_predictions.json` | LLM probability distributions per criterion |
| Synthetic Data | `data/synthetic_data/` | Training data with fold assignments |
| Hyperparameters | `experiments/real_data/best_synth_cross-validation_hp.json` | Pre-optimized model configuration |

The data formats follow specific schemas with TSV files for human judgments (columnar format with Q0-Q8 columns) and JSON files for machine evaluations (row-wise format with probability distributions).

For detailed information about data formats and schemas, see [Data Formats and Schema](#5.1).

**Sources:** [README.md:60-103]()

## Quick Start Summary

To begin using LLM-Rubric, follow these high-level steps:

1. **Install Dependencies**: Use Poetry to set up the virtual environment and install required packages
2. **Compute Baselines**: Run baseline scripts to establish comparison benchmarks
3. **Train Model**: Execute the training script on synthetic data with pre-configured hyperparameters
4. **Generate Predictions**: Apply the trained model to real conversation data
5. **Evaluate Results**: Compare model predictions against baselines using correlation metrics

Each step is automated through shell scripts that orchestrate the Python modules.

For a complete walkthrough with detailed commands and expected outputs, see [Quick Start Tutorial](#2.2).

For individual task guides, see:
- [Computing Baselines](#4.1)
- [Training a Model](#4.2)
- [Making Predictions](#4.3)
- [Evaluating Results](#4.4)

**Sources:** [README.md:58-103]()

## Expected Performance

When running the complete pipeline on the included real conversation data, the system produces:

- **Baselines**: Performance metrics for 7 baseline methods (3 machine-based, 2 human-based, 1 random, 1 LLM-Rubric)
- **Model Output**: Trained PersonalizedCalibrationNetwork parameters saved to `model_params.pkl`
- **Predictions**: Per-judge, per-criterion predictions on 223 conversation samples
- **Metrics**: Pearson, Spearman, and Kendall correlation coefficients plus RMSE

Typical results show:
- Pearson correlation: ~0.31
- Spearman correlation: ~0.37
- Kendall tau: ~0.29

These metrics indicate moderate to strong correlation between model predictions and human judge assessments.

**Sources:** [README.md:66-103]()

## Next Steps

After completing the quick start:

1. **Understand the Architecture**: Learn about the PersonalizedCalibrationNetwork and its judge-specific parameters ([Core Concepts](#3))
2. **Explore Hyperparameter Tuning**: Optimize model configuration for your own data ([Hyperparameter Tuning](#4.5))
3. **Work with Custom Data**: Adapt the system to evaluate your own conversation datasets ([Data Reference](#5))
4. **Extend the Model**: Modify the neural network architecture or training process ([Model Reference](#6))

**Sources:** [README.md:1-103]()

---

