<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/structured-data-models · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source/_static/custom.css](docs/source/_static/custom.css)
- [docs/source/api/evaluation.rst](docs/source/api/evaluation.rst)
- [docs/source/api/explain.rst](docs/source/api/explain.rst)
- [docs/source/api/models.rst](docs/source/api/models.rst)
- [docs/source/images/nvidia.svg](docs/source/images/nvidia.svg)
- [docs/source/index.md](docs/source/index.md)
- [docs/source/nim.md](docs/source/nim.md)
- [docs/source/tensor.md](docs/source/tensor.md)
- [sdm/__init__.py](sdm/__init__.py)
- [sdm/models/__init__.py](sdm/models/__init__.py)
- [sdm/models/kumo/__init__.py](sdm/models/kumo/__init__.py)
- [sdm/models/kumo/relational/__init__.py](sdm/models/kumo/relational/__init__.py)
- [sdm/models/kumo/timeseries/__init__.py](sdm/models/kumo/timeseries/__init__.py)
- [sdm/models/kumo/timeseries/anomaly/__init__.py](sdm/models/kumo/timeseries/anomaly/__init__.py)
- [sdm/models/kumo/timeseries/forecast/__init__.py](sdm/models/kumo/timeseries/forecast/__init__.py)
- [sdm/relational/__init__.py](sdm/relational/__init__.py)
- [sdm/tensor/__init__.py](sdm/tensor/__init__.py)

</details>



The `structured-data-models` (`sdm`) library provides GPU-native foundation models, tensor subclasses, and composable data processors tailored for tabular, relational, and time-series data [README.md:18-22](). By combining PyTorch-native tensor ergonomics with GPU-accelerated dataframe interoperability (such as `cudf`), `sdm` enables end-to-end in-context learning (ICL) and zero-shot inference workflows directly on hardware accelerators without unnecessary host-device data movement [README.md:40]().

Sources: `README.md:18-22`, `sdm/__init__.py:1-4`

## High-Level Architecture

The core data flow in `sdm` progresses through three main abstraction layers: dataframe-backed or raw tensors are losslessly encapsulated into structured tensor types, prepared via declarative processing recipes, and consumed by transformer-based foundation models supporting in-context learning and fast caching.

```mermaid
graph TD
        Raw[""RawDataFrame""] --> Infer[""sdm.infer_stypes()""]
        Infer --> Tensor[""sdm.tensor.TableTensor""]
        Tensor --> Rec[""sdm.processing.Recipe""]
        Rec --> Mdl[""sdm.models.ICLModel""]
```
Sources: `README.md:68-94`, `docs/source/tensor.md:9-17`

- **Tensor Layer (`sdm.tensor`):** Implements lossless tensor subclasses (`TableTensor`, `CategoricalTensor`, `StringTensor`, `VarLenTensor`, `NullableTensor`) that maintain table semantics while exposing multi-dimensional PyTorch tensors [docs/source/tensor.md:9-29]().
- **Processing and Recipes (`sdm.processing`):** Provides composable data transformation pipelines (`Recipe`) and processor contracts that handle feature scaling, missing value imputation, and categorical alignment.
- **Model Framework (`sdm.models`):** Houses the `ICLModel` base class and a comprehensive model zoo comprising tabular models (`TabICLv2`, `TabFM`, `KumoTabular`), relational models (`KumoRelational`), and time-series forecasters (`TimesFM3`, `KumoForecast`) [README.md:20]().

Sources: `README.md:20-22`, `docs/source/tensor.md:9-29`, `sdm/__init__.py:23-32`

## Repository Layout

The codebase is modularly organized into distinct functional subsystems handling tensors, feature processing, model architectures, relational graphs, neural network building blocks, and benchmarks.

```mermaid
graph TD
        Root[""sdm (Root Package)""] --> TensorPkg[""sdm.tensor (tensor subclasses)""]
        Root --> ProcPkg[""sdm.processing (Recipe and Processors)""]
        Root --> ModelPkg[""sdm.models (ICLModel and model zoo)""]
        Root --> RelPkg[""sdm.relational (RelationalData, Sampler)""]
        Root --> NNPkg[""sdm.nn (Attention, TransformerBlock)""]
```
Sources: `sdm/__init__.py:6-35`, `sdm/relational/__init__.py:6-8`

- `sdm/tensor/`: Lossless table representations and device-aware data containers [`sdm/tensor/__init__.py:6-11`]().
- `sdm/processing/`: Processor contracts, feature encoders, and execution pipelines [`sdm/__init__.py:32`]().
- `sdm/models/`: Foundation model reference implementations and inference caching [`sdm/models/__init__.py:13-18`]().
- `sdm/relational/`: Relational dataset containers, task specifications, and graph samplers [`sdm/relational/__init__.py:6-8`]().
- `sdm/nn/`: Custom Triton kernels, normalization layers, and attention mechanisms.
- `benchmark/`: Evaluation harnesses for tabular and relational benchmarks [README.md:97]().
- `examples/`: Quickstart scripts illustrating core workflows [README.md:96]().

Sources: `README.md:96-97`, `sdm/__init__.py:6-35`, `sdm/tensor/__init__.py:6-11`, `sdm/models/__init__.py:13-18`, `sdm/relational/__init__.py:6-8`

## Child Pages

For detailed documentation on specific subsystems, consult the following child pages:

- [Installation and Getting Started](#1.1) — Covers installation procedures, optional GPU dependencies (`cudf`, `pyg-lib`), quickstart fit/predict patterns, and benchmark usage.
- [Core Concepts: Semantic Types and Tasks](#1.2) — Explains the `Stype` enum, automatic type inference via `infer_stypes`, task definitions, estimator wrappers, and shared caching abstractions.

Sources: `README.md:24-97`, `sdm/__init__.py:14-16`

---

