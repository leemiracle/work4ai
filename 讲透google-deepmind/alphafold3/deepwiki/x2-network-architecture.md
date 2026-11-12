<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphafold3 · extra page Network Architecture · fetched 2026-10-26 -->

# Network Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/alphafold3/model/components/haiku_modules.py](src/alphafold3/model/components/haiku_modules.py)
- [src/alphafold3/model/components/mapping.py](src/alphafold3/model/components/mapping.py)
- [src/alphafold3/model/feat_batch.py](src/alphafold3/model/feat_batch.py)
- [src/alphafold3/model/network/atom_cross_attention.py](src/alphafold3/model/network/atom_cross_attention.py)
- [src/alphafold3/model/network/confidence_head.py](src/alphafold3/model/network/confidence_head.py)
- [src/alphafold3/model/network/diffusion_head.py](src/alphafold3/model/network/diffusion_head.py)
- [src/alphafold3/model/network/diffusion_transformer.py](src/alphafold3/model/network/diffusion_transformer.py)
- [src/alphafold3/model/network/distogram_head.py](src/alphafold3/model/network/distogram_head.py)
- [src/alphafold3/model/network/featurization.py](src/alphafold3/model/network/featurization.py)
- [src/alphafold3/model/network/modules.py](src/alphafold3/model/network/modules.py)
- [src/alphafold3/model/network/noise_level_embeddings.py](src/alphafold3/model/network/noise_level_embeddings.py)
- [src/alphafold3/model/network/template_modules.py](src/alphafold3/model/network/template_modules.py)

</details>



## Purpose and Scope

This document details the neural network architecture of AlphaFold 3, focusing on the core modules implemented within the `src/alphafold3/model/network/` and `src/alphafold3/model/components/` directories. It covers the Haiku component library, the Evoformer/PairFormer trunk, template embedding modules, atom cross-attention, the denoising diffusion head and transformer, and the confidence head.

Sources: [`src/alphafold3/model/network/diffusion_head.py:110-141`]() [`src/alphafold3/model/network/confidence_head.py:38-71`]()

---

## 1. Haiku Component Library and Primitives

AlphaFold 3 leverages a custom DeepMind Haiku-based component library located in `src/alphafold3/model/components/haiku_modules.py` and `src/alphafold3/model/network/modules.py`. These modules provide optimized neural network primitives designed for structural biology modeling, supporting custom parameter shapes, upcasting for 16-bit precisions, and gated linear unit (GLU) kernels.

*   `hm.LayerNorm`: Extends `hk.LayerNorm` with an explicit `upcast` flag that casts `bfloat16`/`float16` inputs to `float32` during normalization to maintain numerical stability, and ensures weight parameters are represented as 1D vectors for weight compatibility across layouts [src/alphafold3/model/components/haiku_modules.py:50-60]().
*   `hm.Linear`: Custom linear layer supporting arbitrary input ranks, optional `tokamax` integration, custom initialization strings, and explicit TPU lane/sublane dimension configuration [src/alphafold3/model/components/haiku_modules.py:197-207]().
*   `modules.TransitionBlock`: Implements a feed-forward transition block utilizing gated linear units (GLUs) via `tokamax.gated_linear_unit` or standard swish-gated activations [src/alphafold3/model/network/modules.py:50-94]().

Sources: [`src/alphafold3/model/components/haiku_modules.py:50-122`]() [`src/alphafold3/model/network/modules.py:50-94`]()

---

## 2. Evoformer Trunk (PairFormer Architecture)

The trunk of AlphaFold 3 processes tokenized sequence and pairwise representations through iterative applications of PairFormer layers (`modules.PairFormerIteration`). Unlike older architectures that maintain explicit MSA representation rows throughout the entire network, AlphaFold 3 summarizes MSA features into single and pair representations early in the pipeline, reducing memory overhead while preserving evolutionary signals via profiles and summary statistics.

Sources: [`src/alphafold3/model/network/featurization.py:120-175`]() [`src/alphafold3/model/network/modules.py:50-138`]()

---

## 3. Template Modules

Templates are embedded into pairwise features via `TemplateEmbedding` and `SingleTemplateEmbedding` in `src/alphafold3/model/network/template_modules.py`. 

```mermaid
graph TD
    A["Templates"] -->| "SingleTemplateEmbedding" | B["Rigid3ArrayExtraction"]
    B -->| "dgram_from_positions" | C["DistogramComputation"]
    C -->| "PairFormerIteration" | D["TemplatePairEmbedding"]
    D -->| "SumReduction" | E["FinalTemplateEmbedding"]

    style A fill:#fff,stroke:#000,stroke-width:1px
    style B fill:#fff,stroke:#000,stroke-width:1px
    style C fill:#fff,stroke:#000,stroke-width:1px
    style D fill:#fff,stroke:#000,stroke-width:1px
    style E fill:#fff,stroke:#000,stroke-width:1px
```

*   `template_modules.make_backbone_rigid`: Extracts backbone rigid transformations (`geometry.Rigid3Array`) from atomic coordinate tensors using standard reference frame definitions (N, CA, C) [src/alphafold3/model/network/template_modules.py:76-116]().
*   `template_modules.dgram_from_positions`: Computes distogram tensors using squared Euclidean distances over configured bin boundaries [src/alphafold3/model/network/template_modules.py:46-73]().
*   `template_modules.TemplateEmbedding`: Iterates over multiple template structures using `jax.random.split` and aggregates individual template embeddings into a unified `[num_res, num_res, num_channels]` tensor [src/alphafold3/model/network/template_modules.py:118-201]().

Sources: [`src/alphafold3/model/network/template_modules.py:46-201`]()

---

## 4. Atom Cross Attention

Per-atom cross attention bridges token-level representations with full atom-level coordinates, particularly within the diffusion head and input/output interfaces. Defined in `src/alphafold3/model/network/atom_cross_attention.py`, it constructs per-atom conditioning using reference positions, element types (atomic numbers via one-hot encoding), charges, and atom name character features [src/alphafold3/model/network/atom_cross_attention.py:43-106]().

*   `atom_cross_att_encoder`: Maps fine-grained atomic details to queries and keys using `atom_layout.convert` indexing structures, allowing the network to operate on variable-sized atom subsets per token [src/alphafold3/model/network/atom_cross_attention.py:126-178]().

Sources: [`src/alphafold3/model/network/atom_cross_attention.py:34-178`]()

---

## 5. Diffusion Head and Diffusion Transformer

The denoising diffusion model predicts atomic coordinates iteratively. The architecture is housed in `src/alphafold3/model/network/diffusion_head.py` and `src/alphafold3/model/network/diffusion_transformer.py`.

```mermaid
graph TD
    A["BatchAndEmbeddings"] -->| "DiffusionHead._conditioning" | B["PairAndSingleConditioning"]
    B -->| "noise_embeddings" | C["NoiseLevelEmbeddings"]
    C -->| "Transformer" | D["DiffusionTransformerBlocks"]
    D -->| "AtomCrossAttention" | E["PredictedAtomCoordinates"]

    style A fill:#fff,stroke:#000,stroke-width:1px
    style B fill:#fff,stroke:#000,stroke-width:1px
    style C fill:#fff,stroke:#000,stroke-width:1px
    style D fill:#fff,stroke:#000,stroke-width:1px
    style E fill:#fff,stroke:#000,stroke-width:1px
```

*   `DiffusionHead`: Coordinates conditioning inputs, relative positional encodings, and noise level injections [src/alphafold3/model/network/diffusion_head.py:110-210]().
*   `noise_level_embeddings.noise_embeddings`: Applies fixed Fourier feature transformations based on scaled noise levels ($\sigma / \sigma_{\text{data}}$ where $\sigma_{\text{data}} = 16.0$) [src/alphafold3/model/network/diffusion_head.py:38-39, 189-201]().
*   `diffusion_transformer.Transformer`: Implements Adaptive Layer Normalization (`adaptive_layernorm`) and zero-initialization gating (`adaptive_zero_init`) derived from scalable diffusion transformer designs [src/alphafold3/model/network/diffusion_transformer.py:32-85, 189-196]().

Sources: [`src/alphafold3/model/network/diffusion_head.py:38-210`]() [`src/alphafold3/model/network/diffusion_transformer.py:32-196`]()

---

## 6. Confidence Head

The confidence head (`ConfidenceHead` in `src/alphafold3/model/network/confidence_head.py`) evaluates model outputs by predicting distograms of pairwise distance errors, pLDDT bins, Predicted Aligned Error (PAE), and Predicted Distance Error (PDE).

*   `ConfidenceHead._embed_features`: Combines target features and predicted pseudo-beta distograms with existing pair activations [src/alphafold3/model/network/confidence_head.py:72-99]().
*   PairFormer Stack: Uses an experimental layer stack of `modules.PairFormerIteration` blocks (`confidence_pairformer`) to refine pair and single representations conditioned on predicted structures [src/alphafold3/model/network/confidence_head.py:144-162]().
*   Logits & Expectation: Computes softmax probabilities over distance error bins and evaluates the expected error via linear combination with bin centers [src/alphafold3/model/network/confidence_head.py:170-198]().

Sources: [`src/alphafold3/model/network/confidence_head.py:38-198`]()

---

