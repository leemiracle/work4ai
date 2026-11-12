<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/representations4d · page 4 Recurrent Video Masked Autoencoders (RVM) · fetched 2026-10-26 -->

# Recurrent Video Masked Autoencoders (RVM)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/RVM.png](assets/RVM.png)

</details>



This page introduces Recurrent Video Masked Autoencoders (RVM), a self-supervised video representation learning approach that models temporal structure using an asymmetric masking objective and pixel reconstruction loss. It serves as the parent overview for RVM within the `representations4d` repository.

RVM equips standard Vision Transformer (ViT) image encoders with a lightweight recurrent state to carry temporal information frame-by-frame. For deep technical details, architectural breakdowns, code walkthroughs, and benchmark scripts, refer to the child pages linked below.

---

## 4.1. RVM Model Architecture

RVM's core architecture is encapsulated in the `VideoSiamMAE` framework [README.md:15-17](). Rather than attending over full video clips in a single global tensor, RVM processes frames sequentially. Each incoming video frame is tokenized via patch embedding and combined with sinusoidal 2D positional embeddings. A standard ViT encoder processes the unmasked tokens, while a recurrent core (`GatedTransformerCore`) updates and carries latent temporal states across timesteps using GRU-style gating and cross-attention mechanisms.

For a comprehensive breakdown of `VideoSiamMAE`, the patch tokenizer (`PatchEmbedding` and `SincosPosEmb`), encoder `PreNormBlocks`, and the recurrent gating mechanics, see the child page: [RVM Model Architecture](#4.1).

Sources: [README.md:15-17](), [colabs/rvm_inference_demo.ipynb:269-287]()

---

## 4.2. Inference Demo

The inference pipeline demonstrates how to recover pretrained model checkpoints, extract dense spatio-temporal features from video clips, and perform downstream tasks such as label propagation without fine-tuning [README.md:47](). Utilizing notebooks like `rvm_inference_demo`, users can load weights (such as ViT-S, ViT-B, ViT-L, or ViT-H variants), run frame-by-frame feature extraction, and visualize representations using PCA or k-means clustering.

For step-by-step code examples covering checkpoint recovery (`recover_tree`), feature extraction (`extract_features`), and label propagation, see the child page: [Inference Demo](#4.2).

Sources: [README.md:47](), [colabs/rvm_inference_demo.ipynb:518-542]()

---

## 4.3. Evaluation Framework

To measure representation quality, RVM relies on a standardized evaluation pipeline (`rvm_evaluation_demo`) that tests frozen feature extractors across standard video understanding benchmarks [README.md:50](). These include video object segmentation on DAVIS (evaluating Jaccard and boundary F-measure metrics), keypoint tracking on JHMDB (computing PCK), and video instance parsing on VIP (measuring mIoU).

For details on the evaluation pipeline, pluggable feature extraction interfaces, label propagation internals, and dataset-specific metrics, see the child page: [Evaluation Framework](#4.3).

Sources: [README.md:50](), [colabs/rvm_inference_demo.ipynb:835-879]()

---

## 4.4. Runtime and Memory Benchmarks

RVM is designed for high parameter efficiency and streaming capability, achieving up to 30× greater parameter efficiency compared to traditional video models in the small-model regime [README.md:15-17](). The evaluation suite measures latency scaling against frame counts and compares memory footprints across model sizes (ViT-S through ViT-H) and baseline architectures.

For methodology details, comparative latency tables, and memory scaling analyses, see the child page: [Runtime and Memory Benchmarks](#4.4).

Sources: [README.md:15-17]()

---

