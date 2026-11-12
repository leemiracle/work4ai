<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/representations4d · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/RVM.png](assets/RVM.png)
- [assets/genception.png](assets/genception.png)
- [assets/moog.png](assets/moog.png)
- [assets/scaling_20M_20B.png](assets/scaling_20M_20B.png)

</details>



This page describes the purpose, scope, and organization of the `google-deepmind/representations4d` repository. It introduces the five core research projects contained in the repository, the shared concept of 4D video representations, and how the codebase is structured.

For step-by-step setup instructions, see [Installation and Setup](#1.1). For a reference listing of all pretrained model weights and loading mechanisms, see [Pretrained Checkpoints](#1.2).

Sources: [README.md:1-5]()

---

## Purpose

The `representations4d` repository is the official Google DeepMind release for research projects focused on learning **4D video representations** — spatial (3D) features enriched with a temporal dimension (+1D). Rather than focusing purely on semantic classification, these projects target perception tasks that require understanding geometry, motion, and 3D scene structure directly from video or multi-sensory visual streams.

The repository contains five major projects:

| Project | Short name | Paper | Key idea |
|---|---|---|---|
| Scaling 4D Representations | **4DS** | [arXiv:2412.15212](https://arxiv.org/abs/2412.15212) | MAE pretraining scales from 20M to 22B parameters on non-semantic 4D tasks [README.md:5-7]() |
| Moving Off-the-Grid | **MooG** | [NeurIPS 2024](https://openreview.net/pdf?id=rjSPDVdUaw) | Latent tokens move freely over space/time via cross-attention; next-frame prediction objective [README.md:11-13]() |
| Recurrent Video Masked Autoencoders | **RVM** | [arXiv:2512.13684](https://arxiv.org/abs/2512.13684) | Recurrent ViT with asymmetric masking and pixel reconstruction loss [README.md:15-17]() |
| Omnivorous DINOv2 | **Omnivorous** | [arXiv:2602.24181](https://arxiv.org/abs/2602.24181) | Lightweight post-training aligning features across sensory modalities like RGB and depth [README.md:19-21]() |
| GenCeption | **GenCeption** | [arXiv:2607.09024](https://arxiv.org/abs/2607.09024) | WAN 2.1 generative diffusion backbone fine-tuned as a feed-forward multi-task perception model [README.md:23-25]() |

Sources: [README.md:1-26]()

---

## What is a 4D Representation?

The term "4D" in this repository refers to **three spatial dimensions plus time**. The evaluation tasks shared across these models emphasize:
- **Depth and normal estimation** — inferring dense geometry from video [README.md:5-24]()
- **Camera pose estimation** — recovering 6-DoF camera motion across frames [README.md:5-23]()
- **Point, box, and object tracking** — following locations consistently over time [README.md:5-15]()
- **Dense multi-task perception** — semantic segmentation, reference video object segmentation (RefVOS), and 3D keypoints [README.md:23-24]()

Sources: [README.md:5-25]()

---

## Repository Organization

RepoLayoutDiagram
```mermaid
graph TD
    subgraph repo["google-deepmind/representations4d"]

        subgraph proj4DS["Scaling4DRepresentations"]
            mod4DS_model["representations4d/models/model.py"]
            mod4DS_readout["representations4d/models/readout.py"]
            mod4DS_ckpt["representations4d/utils/checkpoint_utils.py"]
        end

        subgraph projMooG["MovingOffTheGrid"]
            modMooG_modules["moog/modules.py"]
            modMooG_attn["moog/attention.py"]
            modMooG_conv["moog/conv.py"]
            modMooG_pos["moog/pos_embeddings.py"]
            modMooG_init["moog/initializers.py"]
        end

        subgraph projOmni["OmnivorousDINOv2"]
            modOmni_vit["omnivorous/vit.py"]
        end

        subgraph projGen["GenCeption"]
            modGen_pipe["genception/pipeline.py"]
            modGen_wan["genception/wan.py"]
            modGen_utils["genception/utils.py"]
        end

        subgraph infra["InfrastructureAndPackaging"]
            pkg["pyproject.toml"]
            ckpts["GCSCheckpointsStorage"]
        end
    end

    mod4DS_model --> pkg
    modMooG_modules --> pkg
    ckpts --> mod4DS_model
    ckpts --> modMooG_modules
    ckpts --> modOmni_vit
    ckpts --> modGen_pipe
```

Sources: [README.md:27-76](), [pyproject.toml:1-18]()

The repository is organized into distinct Python modules and package directories (`representations4d/`, `moog/`, `omnivorous/`, `genception/`), supported by a shared packaging configuration in `pyproject.toml` [pyproject.toml:1-18]().

---

## The Research Projects

### Scaling 4D Representations (4DS)
4DS investigates masked autoencoding (MAE) scaling laws with ViT-style video models on geometric tasks [README.md:5-7](). 
- For architecture details, see [4DS Model Architecture](#2.1).
- For the depth estimation demo, see [Depth Estimation Demo](#2.2).

Sources: [README.md:5-7]()

### Moving Off-the-Grid (MooG)
MooG decouples representation structure from rigid pixel grids using latent tokens that move freely via cross-attention [README.md:11-13]().
- For core model details, see [MooG Core Model](#3.1).
- For tracking inference, see [Inference Demo](#3.5).

Sources: [README.md:11-13]()

### Recurrent Video Masked Autoencoders (RVM)
RVM utilizes a recurrent transformer with asymmetric masking and pixel reconstruction loss for high parameter efficiency [README.md:15-17]().
- For architecture details, see [RVM Model Architecture](#4.1).
- For evaluation benchmarks, see [Evaluation Framework](#4.3).

Sources: [README.md:15-17]()

### Omnivorous Vision Encoders (Omnivorous DINOv2)
Omnivorous post-training adapts DINOv2 models to align features across multiple sensory modalities such as RGB, depth, and x-ray [README.md:19-21]().
- For ViT implementation details, see [ViT Implementation](#6.1).
- For cross-modal inference, see [Cross-Modal Inference Demo](#6.2).

Sources: [README.md:19-21]()

### GenCeption
GenCeption leverages the WAN 2.1 video generative diffusion backbone as a feed-forward multi-task perception model driven by text instructions [README.md:23-25]().
- For pipeline details, see [GenCeption Pipeline](#5.1).
- For inference demos, see [GenCeption Inference Demo](#5.4).

Sources: [README.md:23-25]()

---

## Project-to-Code Mapping

ProjectToCodeMappingDiagram
```mermaid
graph LR
    subgraph projects["ResearchProjects"]
        P1["4DS"]
        P2["MooG"]
        P3["RVM"]
        P4["Omnivorous"]
        P5["GenCeption"]
    end

    subgraph modules["CodeModulesAndNotebooks"]
        M1["representations4d/models/model.py"]
        M2["moog/modules.py"]
        M3["colabs/rvm_inference_demo.ipynb"]
        M4["omnivorous/vit.py"]
        M5["genception/pipeline.py"]
    end

    subgraph checkpoints["GCSCheckpoints"]
        C1["scaling4d_dist_b.npz"]
        C2["moog_ego4d_backbone_ckpt.npz"]
        C3["pretrain_rvm_small16_256.npz"]
        C4["omnivorous_dinov2-vit_b.safetensors"]
        C5["genception_14b_transformer.npz"]
    end

    P1 --> M1
    P1 --> C1
    P2 --> M2
    P2 --> C2
    P3 --> M3
    P3 --> C3
    P4 --> M4
    P4 --> C4
    P5 --> M5
    P5 --> C5
```

Sources: [README.md:58-76](), [pyproject.toml:1-18]()

---

## License

Software is licensed under the Apache License 2.0. Model weights and supplementary assets are licensed under CC-BY 4.0 [README.md:92-111](). This is not an official Google product.

Sources: [README.md:92-111]()

---

