<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/aerial-cuda-accelerated-ran · page 9 pyaerial — Python ML Bindings · fetched 2026-10-26 -->

# pyaerial — Python ML Bindings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)

</details>



## Purpose and Scope

This page introduces `pyaerial` as the Python ML-oriented interface over cuPHY and summarizes how it relates to the repository’s model and data assets. It is a parent page: for API modules, bindings, installation, and tests, see [pyaerial API and pybind11 Bindings](#9.1); for neural-network models, conversion, and notebooks, see [ML Models and Jupyter Notebooks](#9.2).

Sources: [.gitattributes:5-10]()

### High-Level Architecture

The tracked assets include a channel-estimation ONNX model, a TensorRT engine, NumPy channel data, and an `aerial_mcore` wheel. These filenames establish the model and data artifacts represented in this overview; the available file contents do not specify runtime call paths between them. [.gitattributes:5-10]()

**Model and Data Artifacts**

```mermaid
graph LR
    subgraph "Natural Language Space"
        "Channel estimation model" --> "Optimized inference engine"
        "Channel data artifact"
    end

    subgraph "Code Entity Space"
        "channel_estimator.onnx" --> "channel_estimator_fp16-True_tf32-True.engine"
        "true_chs.npy"
        "ls_chs.npy"
    end

    "Channel estimation model" -. "represented by" .-> "channel_estimator.onnx"
    "Optimized inference engine" -. "represented by" .-> "channel_estimator_fp16-True_tf32-True.engine"
    "Channel data artifact" -. "includes" .-> "true_chs.npy"
    "Channel data artifact" -. "includes" .-> "ls_chs.npy"
```

Sources: [.gitattributes:5-9]()

### Component Overview

The repository tracks an `aerial_mcore` wheel alongside the cuPHY channel-estimation model and data artifacts. This page treats those assets as context for the Python ML bindings; it does not infer package modules or runtime behavior from the asset list. [.gitattributes:5-10]()

| Area | Tracked artifact |
|---|---|
| Python package distribution | `aerial_mcore-0.20261.508652.508652-py3-none-any.whl` |
| Channel-estimation model | `channel_estimator.onnx` |
| TensorRT engine | `channel_estimator_fp16-True_tf32-True.engine` |
| Channel data | `ls_chs.npy`, `true_chs.npy` |

For package structure, API modules, and pybind11 implementation, see [pyaerial API and pybind11 Bindings](#9.1).

Sources: [.gitattributes:5-10]()

### Machine Learning Integration

The tracked channel-estimation assets include an ONNX model, a TensorRT engine, and NumPy data files. The filenames indicate the artifact types but do not, by themselves, document how models are converted, loaded, or used. [.gitattributes:5-9]()

**ML Concepts Mapped to Repository Entities**

```mermaid
graph LR
    subgraph "Natural Language Space"
        "Neural network model"
        "GPU inference engine"
        "Channel reference data"
    end

    subgraph "Code Entity Space"
        "channel_estimator.onnx"
        "channel_estimator_fp16-True_tf32-True.engine"
        "true_chs.npy"
        "ls_chs.npy"
    end

    "Neural network model" -. "artifact" .-> "channel_estimator.onnx"
    "GPU inference engine" -. "artifact" .-> "channel_estimator_fp16-True_tf32-True.engine"
    "Channel reference data" -. "artifact" .-> "true_chs.npy"
    "Channel reference data" -. "artifact" .-> "ls_chs.npy"
```

Sources: [.gitattributes:5-9]()

For model details, conversion tooling, notebooks, and data-lake examples, see [ML Models and Jupyter Notebooks](#9.2).

Sources: [.gitattributes:5-9]()

### Development and Deployment

The repository’s Git LFS attributes list the `aerial_mcore` wheel as a tracked artifact. Build and installation procedures are outside the scope of this overview; see [pyaerial API and pybind11 Bindings](#9.1) for the package and binding details. [.gitattributes:10-10]()

Sources: [.gitattributes:10-10]()

---

