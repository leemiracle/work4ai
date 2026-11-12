<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/tips · page 3 JAX / Scenic Implementation · fetched 2026-10-26 -->

# JAX / Scenic Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scenic/run_tips_inference.py](scenic/run_tips_inference.py)

</details>



The `scenic/` subsystem provides the native JAX and Flax implementation of TIPS and TIPSv2 models. It encompasses modular Flax architectures for vision and text encoding, configuration definitions for various model scales, utility functions for loading `.npz` checkpoints into parameter trees, feature visualization helpers, and an end-to-end inference pipeline script `[scenic/run_tips_inference.py:16-191]()`.

```mermaid
graph TD
    A["ConfigModule" / tips_model_config.py] -->|Variant Params| B["VisionEncoder" / scenic/models/tips.py]
    A -->|Variant Params| C["TextEncoder" / scenic/models/tips.py]
    D["Tokenizer" / scenic/models/text.py] --> C
    E[CheckpointFile] -->|Load Params| F["checkpoint.py" / load_checkpoint]
    F --> B
    F --> C
    B -->|Spatial & CLS Features| G["run_tips_inference.py" / main]
    C -->|Text Embeddings| G
    H["feature_viz.py" / PCAVisualizer & normalize] --> G
    G -->|Output Artifacts| I[output.jpg]

    subspan style="fill:none"
```
*Sources: [scenic/run_tips_inference.py:30-188]()*

---

## 3.1 Scenic Models (VisionEncoder, TextEncoder, ViT)

The model definitions are split across modular Flax files. `scenic/models/tips.py` houses the primary `VisionEncoder` and `TextEncoder` wrappers, while `scenic/models/vit.py` defines the underlying Vision Transformer backbone and `scenic/models/text.py` handles text transformer logic. These components support dual CLS tokens, configurable positional embedding grids, and contrastive temperature scaling.

For details, see [Scenic Models (VisionEncoder, TextEncoder, ViT)](#3.1).

*Sources: [scenic/run_tips_inference.py:39-42]()*, [scenic/run_tips_inference.py:101-127]()

---

## 3.2 Model Configuration

The subsystem utilizes a centralized configuration provider defined by `tips_model_config.get_config(variant)` in `tips.scenic.configs`. It supplies variant-specific hyperparameters such as network depth, attention heads, hidden dimensions, pooling strategies, number of class tokens (`num_cls_tokens`), and positional embedding grid shapes. TIPSv2 variants automatically receive expanded grids like `(32, 32)`.

For details, see [Model Configuration](#3.2).

*Sources: [scenic/run_tips_inference.py:39-40]()*, [scenic/run_tips_inference.py:98-106]()

---

## 3.3 Checkpoint Loading and Feature Visualization Utils

Model weights stored in `.npz` files are loaded directly into Flax parameter trees via utilities defined in `tips.scenic.utils.checkpoint`. Additionally, `tips.scenic.utils.feature_viz` provides feature normalization utilities (`normalize()`) and spatial PCA projection (`PCAVisualizer`) to compress high-dimensional spatial patch tokens into RGB-compatible representations for dense feature debugging and visualization.

For details, see [Checkpoint Loading and Feature Visualization Utils](#3.3).

*Sources: [scenic/run_tips_inference.py:41-43]()*, [scenic/run_tips_inference.py:109-112](), [scenic/run_tips_inference.py:177-182]()

---

## 3.4 run_tips_inference.py Pipeline

The script `scenic/run_tips_inference.py` serves as the primary entrypoint for running end-to-end JAX inference. It parses command-line arguments for model variants, input paths, and image dimensions, loads tokenizer assets, performs image and text preprocessing, runs forward passes through both encoders, computes cosine similarity with contrastive temperature scaling, and generates PCA feature artifacts.

For details, see [run_tips_inference.py Pipeline](#3.4).

*Sources: [scenic/run_tips_inference.py:16-191]()*

---

