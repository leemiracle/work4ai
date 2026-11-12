<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/dstoolkit-mlops-v2 · page 4 Data Science Code (src) · fetched 2026-11-09 -->

# Data Science Code (src)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/how-to/DSScriptInputsAndOutputs.md](docs/how-to/DSScriptInputsAndOutputs.md)
- [docs/how-to/DataScienceScripts.md](docs/how-to/DataScienceScripts.md)
- [docs/media/aml_inputs_and_outputs.png](docs/media/aml_inputs_and_outputs.png)
- [docs/media/nyc-folder.png](docs/media/nyc-folder.png)
- [docs/media/test-folder.png](docs/media/test-folder.png)
- [src/london_src/predict/predict.py](src/london_src/predict/predict.py)
- [src/london_src/prep/prep.py](src/london_src/prep/prep.py)
- [src/london_src/register/register.py](src/london_src/register/register.py)
- [src/london_src/score/score.py](src/london_src/score/score.py)
- [src/london_src/train/train.py](src/london_src/train/train.py)
- [src/london_src/transform/transform.py](src/london_src/transform/transform.py)

</details>



## Purpose and Scope

The `src/` directory contains all data science source code, including data preparation, feature transformation, model training, batch prediction, scoring, and model registration scripts. Each model type (`london_src`, `docker_taxi_src`, and `sequence_model`) adheres to a shared step contract defined by Azure Machine Learning (AML) component configurations, command-line arguments via `argparse`, and experiment tracking via MLflow. 

This page provides a high-level architectural overview of the shared step contract and script layouts. For granular implementation details, refer to the child pages:
- [London Taxi Pipeline Steps](#4.1)
- [Docker Taxi Variant](#4.2)
- [Sequence Model](#4.3)

Sources: `docs/how-to/DataScienceScripts.md:1-134()`, `docs/how-to/DSScriptInputsAndOutputs.md:1-55()`

---

## Shared Step Contract & Architecture

Model pipelines execute as a sequence of discrete script components. Each script acts as a standalone CLI application that accepts data inputs and output paths through arguments, processes the payloads using Pandas/Scikit-Learn/PyTorch, and records metrics and models via MLflow.

```mermaid
graph TD
    sub5 ["Natural Language Space"]
    sub6 ["Code Entity Space"]

    sub5_1["Raw Data Ingestion"] --> sub6_1["src/london_src/prep/prep.py:main"]
    sub5_2["Feature Transformation"] --> sub6_2["src/london_src/transform/transform.py:main"]
    sub5_3["Model Training"] --> sub6_3["src/london_src/train/train.py:main"]
    sub5_4["Batch Prediction"] --> sub6_4["src/london_src/predict/predict.py:main"]
    sub5_5["Model Scoring"] --> sub6_5["src/london_src/score/score.py:main"]
    sub5_6["MLflow Registration"] --> sub6_6["src/london_src/register/register.py:main"]
```
*Figure 1: Bridging pipeline stages to entrypoint functions across the codebase.*

Sources: `src/london_src/prep/prep.py:16-49()`, `src/london_src/transform/transform.py:21-53()`, `src/london_src/train/train.py:23-61()`, `src/london_src/predict/predict.py:22-41()`, `src/london_src/score/score.py:21-61()`, `src/london_src/register/register.py:131-165()`

### MLflow Integration & Tracking Contract

All model training and evaluation scripts interact with MLflow to maintain reproducibility, log metrics (`mlflow.log_metric`), and persist model artifacts (`mlflow.sklearn.log_model` or equivalent framework loggers).

```mermaid
graph TD
    sub3 ["Tracking & Registration Concept"]
    sub4 ["Code Symbol Execution"]

    sub3_1["Active Run Initialization"] --> sub4_1["src/london_src/train/train.py:train_model"]
    sub3_2["Model Artifact Logging"] --> sub4_2["src/london_src/train/train.py:mlflow.sklearn.log_model"]
    sub3_3["Artifact Verification"] --> sub4_3["src/london_src/register/register.py:_artifact_exists_for_run"]
    sub3_4["Model Version Registration"] --> sub4_4["src/london_src/register/register.py:mlflow.register_model"]
```
*Figure 2: Mapping tracking concepts to MLflow utility functions.*

Sources: `src/london_src/train/train.py:118-154()`, `src/london_src/register/register.py:43-129()`

---

## Model Pipeline Implementations

### 4.1 London Taxi Pipeline Steps
The `london_src` package implements a classical tabular machine learning pipeline using `scikit-learn` Linear Regression on NYC/London taxi datasets. It steps through preparation (`prep.py`), feature engineering (`transform.py`), model fitting (`train.py`), inference (`predict.py`), evaluation (`score.py`), and registration (`register.py`).

For implementation details, see [London Taxi Pipeline Steps](#4.1).

Sources: `src/london_src/prep/prep.py:1-190()`, `src/london_src/transform/transform.py:1-169()`, `src/london_src/train/train.py:1-186()`, `src/london_src/predict/predict.py:1-135()`, `src/london_src/score/score.py:1-122()`, `src/london_src/register/register.py:1-190()`

### 4.2 Docker Taxi Variant
The `docker_taxi_src` package reuses the London Taxi modeling logic but executes inside a custom Docker build context environment rather than a standard curated conda environment. This allows custom OS-level package installations and specialized runtime configurations.

For implementation details, see [Docker Taxi Variant](#4.2).

Sources: `docs/how-to/DataScienceScripts.md:1-134()`

### 4.3 Sequence Model
The `sequence_model` package implements a deep learning sequence-based model. It incorporates custom tokenization (`tokenizer.py`), neural architecture definitions (`seq_model.py`), synthetic sequence data generation, benchmarking scripts, and extended MLflow tracking modules (`mlflow_ext`).

For implementation details, see [Sequence Model](#4.3).

Sources: `docs/how-to/DataScienceScripts.md:1-134()`

---

