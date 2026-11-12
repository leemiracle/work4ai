<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/representations4d · page 5 GenCeption · fetched 2026-10-26 -->

# GenCeption

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [assets/genception.png](assets/genception.png)
- [representations4d/genception/__init__.py](representations4d/genception/__init__.py)

</details>



GenCeption introduces a WAN 2.1 diffusion transformer fine-tuned as a single-step feed-forward multi-task video perception model capable of tasks such as depth estimation, surface normals, and Referring Video Object Segmentation (RefVOS) [representations4d/genception/__init__.py:16-29]().

## Purpose and Scope

This page serves as a high-level overview of the GenCeption module within the `representations4d` repository. Detailed technical documentation, internal implementations, and walkthroughs are maintained in dedicated child pages:
- **Pipeline and Model Execution**: Covered in [GenCeption Pipeline](#5.1).
- **Transformer and VAE Internals**: Covered in [WAN Model and VAE Internals](#5.2).
- **Depth Encoding and Rendering**: Covered in [Depth Encoding and Point Cloud Rendering Utilities](#5.3).
- **Inference Demonstrations**: Covered in [GenCeption Inference Demo](#5.4).

---

## High-Level Architecture

GenCeption reuses the WAN 2.1 video diffusion transformer backbone (`WanModel`) and video VAE (`AutoencoderKLWan`), adapting them for feed-forward perception tasks by performing a single-step forward pass at time $t=0$ [representations4d/genception/__init__.py:19-29]().

```mermaid
graph TD
    A["Video Input"] --> B["AutoencoderKLWan Encoding"]
    B --> C["Latent Representations"]
    D["Prompt Embeddings"] --> E["GenCeptionPipeline"]
    C --> E
    E --> F["WanModel Single-Step Forward (t=0)"]
    F --> G["Multi-Task Predictions (Depth, Normals, RefVOS)"]
    G --> H["Latent Normalization & Decoding"]
    H --> I["utils.py: Point Cloud / RGB Rendering"]

    sub: Code Entities
    classDef file fill:#f9f,stroke:#333,stroke-width:2px;
    class E representations4d/genception/pipeline.py:GenCeptionPipeline;
    class F representations4d/genception/model.py:WanModel;
    class H representations4d/genception/vae.py:AutoencoderKLWan;
    class I representations4d/genception/utils.py:utils;
```
*Figure 1: GenCeption system architecture linking pipeline, model, VAE, and utility modules.*

Sources: `representations4d/genception/__init__.py`, `representations4d/genception/pipeline.py`, `representations4d/genception/model.py`, `representations4d/genception/vae.py`, `representations4d/genception/utils.py`

---

## Sub-Topics and Child Pages

### 5.1. GenCeption Pipeline
The `GenCeptionPipeline` class manages configuration resolution from pretrained checkpoints, video encoding and decoding, prompt embedding handling, latent normalization, depth decoding, and executing the single-step transformer forward pass at $t=0$ [representations4d/genception/__init__.py:20](). 

For details, see [GenCeption Pipeline](#5.1).

### 5.2. WAN Model and VAE Internals
The core architecture consists of the `WanModel` transformer backbone (handling attention, embeddings, and normalization modules) paired with the `AutoencoderKLWan` video VAE incorporating causal-convolution caching [representations4d/genception/__init__.py:19,29]().

For details, see [WAN Model and VAE Internals](#5.2).

### 5.3. Depth Encoding and Point Cloud Rendering Utilities
Utility functions in `utils.py` handle video loading and saving, preprocessing and postprocessing, banana colormap transformations via `depth_to_rgb` and `rgb_to_depth_robust`, as well as depth unprojection and NumPy splatting point cloud rendering [representations4d/genception/__init__.py:21-28]().

For details, see [Depth Encoding and Point Cloud Rendering Utilities](#5.3).

### 5.4. GenCeption Inference Demo
Practical inference is illustrated through the `genception_inference_demo` notebook, demonstrating precomputed prompt embeddings, executing depth, normals, and RefVOS inference, decoding depth, and rendering point cloud flythroughs [representations4d/genception/__init__.py:16-29]().

For details, see [GenCeption Inference Demo](#5.4).

Sources: `representations4d/genception/__init__.py`

---

