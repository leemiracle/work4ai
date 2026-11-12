<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/uplifting-biomolecular-modeling · extra page Rowpair Sharding Internals · fetched 2026-10-26 -->

# Rowpair Sharding Internals

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [af3_torch/opt/af3_torch_opt/forward.py](af3_torch/opt/af3_torch_opt/forward.py)
- [af3_torch/opt/af3_torch_opt/rowpair_xfold.py](af3_torch/opt/af3_torch_opt/rowpair_xfold.py)
- [af3_torch/opt/af3_torch_opt/tests/conftest.py](af3_torch/opt/af3_torch_opt/tests/conftest.py)
- [af3_torch/opt/forward/af3t/af3_torch/xfold/nn/paircond_rows.py](af3_torch/opt/forward/af3t/af3_torch/xfold/nn/paircond_rows.py)
- [boltz2/opt/boltz2_opt/big.py](boltz2/opt/boltz2_opt/big.py)
- [boltz2/opt/boltz2_opt/rowpair.py](boltz2/opt/boltz2_opt/rowpair.py)
- [boltz2/opt/boltz2_opt/rowpair_heads.py](boltz2/opt/boltz2_opt/rowpair_heads.py)
- [boltz2/opt/boltz2_opt/rowpair_msa.py](boltz2/opt/boltz2_opt/rowpair_msa.py)
- [boltz2/stock/src/boltz/model/modules/confidencev2.py](boltz2/stock/src/boltz/model/modules/confidencev2.py)
- [chai1/opt/chai1_opt/big.py](chai1/opt/chai1_opt/big.py)
- [chai1/opt/forward/eager_trunk/chai1_eager/trunk.py](chai1/opt/forward/eager_trunk/chai1_eager/trunk.py)
- [colabdesign/opt/colabdesign_opt/kernels/layers_transition.py](colabdesign/opt/colabdesign_opt/kernels/layers_transition.py)
- [colabdesign/opt/colabdesign_opt/lowercache.py](colabdesign/opt/colabdesign_opt/lowercache.py)
- [colabfold/opt/colabfold_opt/tests/test_transition.py](colabfold/opt/colabfold_opt/tests/test_transition.py)
- [colabfold/opt/colabfold_opt/transition.py](colabfold/opt/colabfold_opt/transition.py)
- [colabfold/opt/colabfold_opt/trimul_pallas.py](colabfold/opt/colabfold_opt/trimul_pallas.py)
- [common/opt_core/opt_core/kernels/transition/esm/ef2_pair_v2.py](common/opt_core/opt_core/kernels/transition/esm/ef2_pair_v2.py)
- [common/opt_core/opt_core/kernels/transition/esm_fused/__init__.py](common/opt_core/opt_core/kernels/transition/esm_fused/__init__.py)
- [common/opt_core/opt_core/mem/rowpair/ADAPTER_GUIDE.md](common/opt_core/opt_core/mem/rowpair/ADAPTER_GUIDE.md)
- [common/opt_core/opt_core/mem/rowpair/API.md](common/opt_core/opt_core/mem/rowpair/API.md)
- [common/opt_core/opt_core/mem/rowpair/__init__.py](common/opt_core/opt_core/mem/rowpair/__init__.py)
- [common/opt_core/opt_core/mem/rowpair/diffusion.py](common/opt_core/opt_core/mem/rowpair/diffusion.py)
- [common/opt_core/opt_core/mem/rowpair/dist.py](common/opt_core/opt_core/mem/rowpair/dist.py)
- [common/opt_core/opt_core/mem/rowpair/heads.py](common/opt_core/opt_core/mem/rowpair/heads.py)
- [common/opt_core/opt_core/mem/rowpair/launch.py](common/opt_core/opt_core/mem/rowpair/launch.py)
- [common/opt_core/opt_core/mem/rowpair/pairstack.py](common/opt_core/opt_core/mem/rowpair/pairstack.py)
- [common/opt_core/opt_core/mem/rowpair/shard.py](common/opt_core/opt_core/mem/rowpair/shard.py)
- [common/opt_core/opt_core/mem/rowpair/transition.py](common/opt_core/opt_core/mem/rowpair/transition.py)
- [common/opt_core/opt_core/mem/rowpair/triatt.py](common/opt_core/opt_core/mem/rowpair/triatt.py)
- [common/opt_core/opt_core/mem/rowpair/trunk.py](common/opt_core/opt_core/mem/rowpair/trunk.py)
- [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py](common/opt_core/opt_core/mem/rowpair_jax/alphafold.py)
- [common/opt_core/opt_core/mem/rowpair_jax/alphafold3.py](common/opt_core/opt_core/mem/rowpair_jax/alphafold3.py)
- [common/opt_core/tests/synthetic_af3.py](common/opt_core/tests/synthetic_af3.py)
- [common/opt_core/tests/synthetic_pair.py](common/opt_core/tests/synthetic_pair.py)
- [common/opt_core/tests/test_kt20c_pool_shrink.py](common/opt_core/tests/test_kt20c_pool_shrink.py)
- [common/opt_core/tests/test_rowpair_confidence_043.py](common/opt_core/tests/test_rowpair_confidence_043.py)
- [common/opt_core/tests/test_rowpair_confidence_fast_05213.py](common/opt_core/tests/test_rowpair_confidence_fast_05213.py)
- [common/opt_core/tests/test_rowpair_hostgather_043.py](common/opt_core/tests/test_rowpair_hostgather_043.py)
- [common/opt_core/tests/test_rowpair_launch_05183.py](common/opt_core/tests/test_rowpair_launch_05183.py)
- [common/opt_core/tests/test_rowpair_launch_results_043.py](common/opt_core/tests/test_rowpair_launch_results_043.py)
- [common/opt_core/tests/test_rowpair_opm_unsharded_043.py](common/opt_core/tests/test_rowpair_opm_unsharded_043.py)
- [common/opt_core/tests/test_rowpair_schedule.py](common/opt_core/tests/test_rowpair_schedule.py)
- [common/opt_core/tests/test_rowpair_template_043.py](common/opt_core/tests/test_rowpair_template_043.py)
- [common/opt_core/tests/test_rowpair_transition_face_0515.py](common/opt_core/tests/test_rowpair_transition_face_0515.py)
- [ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_esmc_hoist.py](ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_esmc_hoist.py)
- [ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_esmc_overlap.py](ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_esmc_overlap.py)
- [ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_esmc_rope.py](ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_esmc_rope.py)
- [ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_pairbias_attn.py](ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_pairbias_attn.py)
- [ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_sampler_graph.py](ef2inv/opt/forward/ESMFOLD2_DESIGN_FAST_INFERENCE_KIT_v1/k/test_ef2_sampler_graph.py)
- [esmfold2/opt/esmfold2_opt/rowchunk/__init__.py](esmfold2/opt/esmfold2_opt/rowchunk/__init__.py)
- [esmfold2/opt/esmfold2_opt/rowpair.py](esmfold2/opt/esmfold2_opt/rowpair.py)
- [esmfold2/opt/esmfold2_opt/rowpair_heads.py](esmfold2/opt/esmfold2_opt/rowpair_heads.py)
- [esmfold2/opt/esmfold2_opt/rowpair_msa.py](esmfold2/opt/esmfold2_opt/rowpair_msa.py)
- [esmfold2/opt/esmfold2_opt/tests/test_rowpair_adapter.py](esmfold2/opt/esmfold2_opt/tests/test_rowpair_adapter.py)
- [esmfold2/opt/forward/fast_inference/driver/ef2_mk_sampler.py](esmfold2/opt/forward/fast_inference/driver/ef2_mk_sampler.py)
- [esmfold2/opt/forward/fast_inference/driver/ef2_msa_v2.py](esmfold2/opt/forward/fast_inference/driver/ef2_msa_v2.py)
- [esmfold2/opt/forward/fast_inference/driver/ef2_pair_v2.py](esmfold2/opt/forward/fast_inference/driver/ef2_pair_v2.py)
- [esmfold2/opt/forward/fast_inference/driver/ef2_transition_cute.py](esmfold2/opt/forward/fast_inference/driver/ef2_transition_cute.py)
- [esmfold2/stock/src/esm/utils/structure/predicted_aligned_error.py](esmfold2/stock/src/esm/utils/structure/predicted_aligned_error.py)
- [mosaic/opt/mosaic_opt/levers.py](mosaic/opt/mosaic_opt/levers.py)
- [mosaic/opt/mosaic_opt/mosaic_fast/transition_fused.py](mosaic/opt/mosaic_opt/mosaic_fast/transition_fused.py)
- [opendde/opt/opendde_opt/tests/_tp_stub_engine.py](opendde/opt/opendde_opt/tests/_tp_stub_engine.py)
- [opendde/opt/opendde_opt/tests/test_tp_rank0_feats.py](opendde/opt/opendde_opt/tests/test_tp_rank0_feats.py)
- [opendde/opt/opendde_opt/tp_diffusion.py](opendde/opt/opendde_opt/tp_diffusion.py)
- [openfold3/opt/openfold3_opt/tests/test_no_refusal_notes.py](openfold3/opt/openfold3_opt/tests/test_no_refusal_notes.py)
- [openfold3/opt/openfold3_opt/tests/test_tp_host_census.py](openfold3/opt/openfold3_opt/tests/test_tp_host_census.py)
- [openfold3/opt/openfold3_opt/tp_rowpair/trunk.py](openfold3/opt/openfold3_opt/tp_rowpair/trunk.py)
- [openfold3_ob0/opt/openfold3_ob0_opt/tests/test_no_refusal_notes.py](openfold3_ob0/opt/openfold3_ob0_opt/tests/test_no_refusal_notes.py)
- [openfold3_ob0/opt/openfold3_ob0_opt/tests/test_tp_host_census.py](openfold3_ob0/opt/openfold3_ob0_opt/tests/test_tp_host_census.py)
- [openfold3_ob0/opt/openfold3_ob0_opt/tp_rowpair/trunk.py](openfold3_ob0/opt/openfold3_ob0_opt/tp_rowpair/trunk.py)
- [protenix_v1/opt/protenix_v1_opt/rowpair.py](protenix_v1/opt/protenix_v1_opt/rowpair.py)
- [protenix_v1/opt/protenix_v1_opt/tests/test_rowpair.py](protenix_v1/opt/protenix_v1_opt/tests/test_rowpair.py)
- [protenix_v1/opt/protenix_v1_opt/tests/test_tp_template_rows.py](protenix_v1/opt/protenix_v1_opt/tests/test_tp_template_rows.py)
- [protenix_v1/opt/protenix_v1_opt/tp.py](protenix_v1/opt/protenix_v1_opt/tp.py)
- [protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/diffusion.py](protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/diffusion.py)
- [protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/dist.py](protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/dist.py)
- [protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/template_real.py](protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/template_real.py)
- [protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/triatt.py](protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/triatt.py)
- [protenix_v2/opt/protenix_opt/tp_bind/diffusion.py](protenix_v2/opt/protenix_opt/tp_bind/diffusion.py)
- [protenix_v2/stock/src/protenix/model/tri_attention/autotune.py](protenix_v2/stock/src/protenix/model/tri_attention/autotune.py)
- [rosettafold3/opt/rosettafold3_opt/rowpair.py](rosettafold3/opt/rosettafold3_opt/rowpair.py)
- [rosettafold3/opt/rosettafold3_opt/tests/test_tp_conf_cpu.py](rosettafold3/opt/rosettafold3_opt/tests/test_tp_conf_cpu.py)
- [rosettafold3/opt/rosettafold3_opt/tp_conf.py](rosettafold3/opt/rosettafold3_opt/tp_conf.py)

</details>



This page details the internal mechanisms of rowpair sharding, a core component of the `opt_core` library for optimizing memory usage and enabling multi-GPU inference. It covers the fundamental concepts, data flow, key functions, and how different kits integrate with this sharding strategy. The primary purpose of rowpair sharding is to distribute large pair-wise tensors (e.g., `[N, N, C]` representations in protein modeling) across multiple GPUs, ensuring that no single GPU needs to hold the entire tensor.

## Core Concepts and Data Flow

Rowpair sharding operates on the principle that a pair tensor `X[N, N, C]` is ROW-SHARDED, meaning each rank `q` (GPU process) holds a contiguous slice of rows `X[q0:q1, :, :]`. This ensures that the full `N x N x C` tensor is never materialized on a single rank. The `opt_core.mem.rowpair.dist` module provides the foundational communication primitives and layout management for this strategy [common/opt_core/opt_core/mem/rowpair/dist.py:1-19]().

The sharding process involves:
1.  **Layout Definition**: The `Layout` class [common/opt_core/opt_core/mem/rowpair/dist.py:44-48]() defines how rows are partitioned across ranks. This can be an invariant grid or a balanced chunk-aligned partition.
2.  **Initialization**: Pair tensors are "born" as row shards on their respective ranks. For example, in Protenix, the `z_init` pair representation is initialized as a row shard [protenix_v1/opt/protenix_v1_opt/tp.py:11]().
3.  **Row-Local Operations**: Many operations on the pair tensor can be performed locally on each rank's row shard. This includes Layer Normalization, linear projections, and certain parts of attention mechanisms.
4.  **Collectives**: When operations require data from other ranks (e.g., for triangle multiplication, triangle attention bias, or transposing shards), `opt_core.mem.rowpair.dist` provides collective communication primitives like `all_gather_rows`, `transpose_shards`, and `ring_blocks` [common/opt_core/opt_core/mem/rowpair/dist.py:51-58](). These collectives ensure bit-preserving data movement.
5.  **Memory Management**: To further optimize memory, rowpair sharding employs strategies like parking shards on pinned host memory (`ROWPAIR_PARK_ZINIT`) [protenix_v1/opt/protenix_v1_opt/tp.py:13-15](), and managing host-resident features that are sliced to local rows only when needed [protenix_v1/opt/protenix_v1_opt/tp.py:50-56]().

### Rowpair Sharding Data Flow

The following diagram illustrates the general data flow for a pair tensor `Z` undergoing rowpair sharding across multiple ranks.

```mermaid
graph TD
    subgraph "Rank 0"
        A[Input Features] --> B{Initialize Z_shard [R0, N, C]}
        B --> C{Row-Local Operations on Z_shard}
        C --> D{Collective Operations (e.g., All-Gather Bias)}
        D --> E{Further Row-Local Operations}
        E --> F{Output Z_shard [R0, N, C]}
    end

    subgraph "Rank 1"
        A' --> B'{Initialize Z_shard [R1, N, C]}
        B' --> C'{Row-Local Operations on Z_shard}
        C' --> D'{Collective Operations (e.g., All-Gather Bias)}
        D' --> E'{Further Row-Local Operations}
        E' --> F'{Output Z_shard [R1, N, C]}
    end

    subgraph "Rank P-1"
        A'' --> B''{Initialize Z_shard [RP-1, N, C]}
        B'' --> C''{Row-Local Operations on Z_shard}
        C'' --> D''{Collective Operations (e.g., All-Gather Bias)}
        D'' --> E''{Further Row-Local Operations}
        E'' --> F''{Output Z_shard [RP-1, N, C]}
    end

    B -- "Distribute Rows" --> B'; B' -- "Distribute Rows" --> B''
    D -- "Exchange Data" --> D'; D' -- "Exchange Data" --> D''
    F -- "Gather/Assemble (Rank 0)" --> G[Full Output Tensor [N, N, C]]
    F' -- "Gather/Assemble (Rank 0)" --> G
    F'' -- "Gather/Assemble (Rank 0)" --> G
```
Sources:
- [protenix_v1/opt/protenix_v1_opt/tp.py:11]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:1-19]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:44-48]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:51-58]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:13-15]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:50-56]()

## Rowpair Sharding in Kits

Different kits integrate rowpair sharding by adapting their model's forward pass to operate on row shards. This involves identifying which parts of the model operate on the pair representation and replacing them with row-sharded equivalents provided by `opt_core.mem.rowpair`.

### Protenix Integration

In the Protenix kit, the `protenix_v1_opt.tp` module acts as the adapter for tensor-parallel execution [protenix_v1/opt/protenix_v1_opt/tp.py:4-6](). It maps Protenix's stock module statements to the core's callables, ensuring that the pair representation `z [N, N, c_z]` is row-sharded from its creation to its last read [protenix_v1/opt/protenix_v1_opt/tp.py:1-3]().

Key aspects of Protenix's integration:
*   **`RelpRows`**: Generates relative position encodings as per-token IDs, with rows built per row block [protenix_v1/opt/protenix_v1_opt/tp.py:9-10]().
*   **`trunk.init_pair_shard`**: Initializes the `z` tensor as a row shard [protenix_v1/opt/protenix_v1_opt/tp.py:11]().
*   **`trunk.recycle_shard_`**: Handles recycling of the `z` shard, including parking `z_init` on pinned host memory (`ROWPAIR_PARK_ZINIT`) [protenix_v1/opt/protenix_v1_opt/tp.py:12-15]().
*   **`template.template_embed_rows`**: Processes template embeddings, slicing dense template pair features to local rows [protenix_v1/opt/protenix_v1_opt/tp.py:16-19]().
*   **MSA Representation**: The MSA representation `m [S_msa, N|R, 64]` can be token-sharded or replicated. When token-sharded, rank `q` holds `m[:, r0:r1, :]` [protenix_v1/opt/protenix_v1_opt/tp.py:46-48]().
*   **Confidence Head**: The confidence head (`heads.ZTrunkPlan`) processes `z_trunk` rows, potentially serving them from host park memory (`ROWPAIR_CONF_PARK_ZTRUNK`) [protenix_v1/opt/protenix_v1_opt/tp.py:31-39]().

### Boltz2 Integration

The `boltz2_opt.rowpair` module handles rowpair sharding for Boltz2, specifically for the `z [1, N, N, 128]` pair representation [boltz2/opt/boltz2_opt/rowpair.py:1-3](). It ensures that `z` is row-sharded from its creation through recycling, template, MSA, Pairformer, and distogram head modules.

Key aspects of Boltz2's integration:
*   **Pair Init**: `z_init` rows are created as `z_init_1(s)[:, r0:r1, None] + z_init_2(s)[:, None, :]` plus relative position and token bond rows [boltz2/opt/boltz2_opt/rowpair.py:11-13]().
*   **Recycling**: `z_loc = z_init_loc + z_recycle(z_norm(z_loc))` is performed row-locally [boltz2/opt/boltz2_opt/rowpair.py:14]().
*   **Template Module**: `TemplateV2Module.forward` operates with `i` operands of its pair features sliced to the rows [boltz2/opt/boltz2_opt/rowpair.py:15-17]().
*   **MSA Representation**: Similar to Protenix, the MSA representation `m [1, S, N|R, 64]` can be token-sharded (`ROWPAIR_MSA_M_LAYOUT=token_sharded`) or replicated [boltz2/opt/boltz2_opt/rowpair.py:18-23]().
*   **OuterProductMean**: `msa.opm_rows_budgeted` is used for local output rows [boltz2/opt/boltz2_opt/rowpair.py:24-25]().
*   **PairWeightedAvg**: `msa.pwa_rows` is used, with bias from local `z` rows and softmax over `j` within a row [boltz2/opt/boltz2_opt/rowpair.py:26-28]().
*   **Confidence Head**: `boltz2_opt.rowpair_heads` handles the confidence pair initialization and processing on rows [boltz2/opt/boltz2_opt/rowpair.py:35-37]().

### RosettaFold3 Integration

The `rosettafold3_opt.rowpair` module adapts RF3's pair representation `Z_II [I, I, 128]` for row sharding [rosettafold3/opt/rosettafold3_opt/rowpair.py:1-3](). It rebinds RF3 statements to core statements, ensuring that each rank holds its rows `z[r0:r1, :, :]` [rosettafold3/opt/rosettafold3_opt/rowpair.py:9-11]().

Key aspects of RF3's integration:
*   **Input Featurization**: Rank 0 runs the pipeline and broadcasts featurized examples to other ranks (`rankdata.broadcast_features`) [rosettafold3/opt/rosettafold3_opt/rowpair.py:14-16]().
*   **Pair Init**: `FeatureInitializer.forward` uses `trunk.init_pair_shard` to create `z` as rows [rosettafold3/opt/rosettafold3_opt/rowpair.py:17]().
*   **Recycling**: `Recycler.forward` uses `trunk.recycle_shard_`, with `Z_init` parked on pinned host memory (`ROWPAIR_PARK_ZINIT`) [rosettafold3/opt/rosettafold3_opt/rowpair.py:18-20]().
*   **MSA Module**: `msa.msa_module_sharded` handles OPM, PWA, and MSA transition on shards [rosettafold3/opt/rosettafold3_opt/rowpair.py:22-23]().
*   **Pairformer Blocks**: `pairstack.pair_stack_` handles triangle multiplication, triangle attention, and transition operations on shards [rosettafold3/opt/rosettafold3_opt/rowpair.py:24-26]().
*   **Confidence Head**: `tp_conf.run_confidence_sharded` processes confidence embeddings and logits per row block [rosettafold3/opt/rosettafold3_opt/rowpair.py:28-29]().

Sources:
- [protenix_v1/opt/protenix_v1_opt/tp.py:1-6]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:9-10]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:11]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:12-15]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:16-19]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:46-48]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:31-39]()
- [boltz2/opt/boltz2_opt/rowpair.py:1-3]()
- [boltz2/opt/boltz2_opt/rowpair.py:11-13]()
- [boltz2/opt/boltz2_opt/rowpair.py:14]()
- [boltz2/opt/boltz2_opt/rowpair.py:15-17]()
- [boltz2/opt/boltz2_opt/rowpair.py:18-23]()
- [boltz2/opt/boltz2_opt/rowpair.py:24-25]()
- [boltz2/opt/boltz2_opt/rowpair.py:26-28]()
- [boltz2/opt/boltz2_opt/rowpair.py:35-37]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:1-3]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:9-11]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:14-16]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:17]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:18-20]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:22-23]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:24-26]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:28-29]()

## `opt_core.mem.rowpair` Modules

The `opt_core.mem.rowpair` package provides the shared runtime for rowpair sharding.

### `dist.py`: Communication Surface and Layout

The `dist.py` module is the core of the rowpair sharding mechanism, defining the communication surface, row layout, and bit-preserving data movement [common/opt_core/opt_core/mem/rowpair/dist.py:1-3]().

*   **`Layout` Class**: Manages the row partition, providing methods to determine local row bounds (`r0`, `r1`), number of local rows (`n_loc`), and ownership of global rows (`owner(i)`) [common/opt_core/opt_core/mem/rowpair/dist.py:44-48](). It supports both P-invariant grid and balanced chunk-aligned partitions.
*   **`comm()` / `get()`**: Returns the `Comm` object for the calling rank, which provides access to communication primitives like `bcast_`, `p2p`, `allreduce_`, and `allgather_obj` [common/opt_core/opt_core/mem/rowpair/dist.py:21-24]().
*   **`init_from_env()`**: Initializes the process group from environment variables (`ROWPAIR_{RANK,WORLD,LOCAL_RANK,ADDR,PORT}`) [common/opt_core/opt_core/mem/rowpair/dist.py:33-36]().
*   **`host_signal()` / `host_wait()`**: Provides a host-side key/value signaling mechanism between ranks, backed by the group's c10d store [common/opt_core/opt_core/mem/rowpair/dist.py:25-32](). This is used for coordination without spinning on GPU kernels.
*   **Collective Operations**:
    *   `all_gather_rows(x_shard, layout)`: Gathers `[R, ...]` shards from all ranks to form `[N, ...]` on every rank [common/opt_core/opt_core/mem/rowpair/dist.py:51]().
    *   `gather_rows_to_rank0(x_shard, layout)`: Gathers `[R, ...]` shards to `[N, ...]` on rank 0 only [common/opt_core/opt_core/mem/rowpair/dist.py:52]().
    *   `transpose_shards(z_shard, layout, chunks, …)`: Transposes a whole shard, effectively exchanging column slabs between ranks [common/opt_core/opt_core/mem/rowpair/dist.py:55]().
    *   `ring_blocks(x_shard, layout, rows=, dim=)`: Streams blocks of `x_shard` around the ring of ranks, double-buffered with `p2p_start` [common/opt_core/opt_core/mem/rowpair/dist.py:57-58]().

### `triatt.py`: Triangle Attention under Row Sharding

The `triatt.py` module implements triangle attention operations in a row-sharded context [common/opt_core/opt_core/mem/rowpair/triatt.py:1-3](). It ensures that every query row's softmax over all keys happens entirely on one rank.

*   **`gather_triangle_bias(tb_shard, layout)`**: Gathers the small `[R, N, H]` bias shard from each rank to form `[N, N, H]` on every rank [common/opt_core/opt_core/mem/rowpair/triatt.py:21]().
*   **`triatt_starting(attn_rows, z_shard, tb_full, layout, ...)`**: Handles the starting node of triangle attention, where queries, keys, and values are row-local, and the full triangle bias is available [common/opt_core/opt_core/mem/rowpair/triatt.py:22-25]().
*   **`triatt_ending(attn_rows, z_shard, tb_of, layout, ...)`**: Handles the ending node, which involves transposing the shard, running the starting form, and transposing the result back [common/opt_core/opt_core/mem/rowpair/triatt.py:26-27]().
*   **`TriAttFns`**: A callable that encapsulates the LayerNorm, bias computation, and attention logic for a triangle attention update [common/opt_core/opt_core/mem/rowpair/triatt.py:29-36]().
*   **`triangle_bias_shard()` / `triatt_update_jit_()`**: Provides an alternative "JIT" mode for triangle bias where the bias is kept sharded, and row windows are exchanged just-in-time (`ROWPAIR_TRIATT_BIAS=jit`) [common/opt_core/opt_core/mem/rowpair/triatt.py:38-46]().

### `trunk.py`: Trunk Driver

The `trunk.py` module provides the driver for the main pairformer trunk, orchestrating the row-sharded operations. It includes mechanisms for initializing, recycling, and parking pair shards.

*   **`init_pair_shard(rows_fn)`**: Initializes the pair representation as a row shard, using a provided function `rows_fn` to generate the initial rows [protenix_v1/opt/protenix_v1_opt/tp.py:11]().
*   **`recycle_shard_`**: Manages the recycling of the pair shard, often involving parking the initial shard (`z_init`) on the host to save device memory (`ROWPAIR_PARK_ZINIT`) [protenix_v1/opt/protenix_v1_opt/tp.py:12-15]().
*   **`ShardPark`**: A mechanism to park a shard on pinned host memory, releasing device memory, and retrieving it when needed [boltz2/opt/boltz2_opt/rowpair.py:54-56]().

### `heads.py`: Confidence Heads and Atom-Pair Helpers

The `heads.py` module provides row-sharded implementations for confidence heads and atom-pair helpers.

*   **`ZTrunkPlan`**: Manages the processing of `z_trunk` rows for confidence prediction, including serving `z_trunk` from host park memory or directly into the shard [protenix_v1/opt/protenix_v1_opt/tp.py:31-39]().
*   **`RowBlockReducer`**: Processes PAE and PDE rows of `z + z^T` per row block, consuming them to compute confidence metrics [protenix_v1/opt/protenix_v1_opt/tp.py:37-39]().
*   **Symmetrization**: Handles the symmetrization of pair tensors (`z + z^T`) by exchanging column slabs, ensuring bit-exactness [common/opt_core/tests/test_rowpair_confidence_043.py:11]().

### `launch.py`: Multi-Process Launch

The `launch.py` module is responsible for launching multiple processes for multi-GPU execution.

*   **`run_rank_processes(P, entry, ...)`**: Spawns `P` rank processes, each on a visible device, and manages their rendezvous and output streaming [rosettafold3/opt/rosettafold3_opt/rowpair.py:58-60]().
*   **Environment Variables**: Sets `ROWPAIR_{RANK,WORLD,LOCAL_RANK,ADDR,PORT}` for process group initialization [common/opt_core/opt_core/mem/rowpair/dist.py:33-36]().

### `rowpair_jax/alphafold.py`: JAX Integration

The `rowpair_jax/alphafold.py` module provides the AlphaFold-2 recipe for row-sharded pair stacks within a JAX/Haiku environment [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:1-3](). It rebinds Haiku module classes to bodies that operate on row blocks with collectives inserted.

*   **`EvoformerIteration.__call__`**: Uses `shard_map` over replicated MSA and row-sharded pair, with the stock body running on local blocks [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:13-14]().
*   **`TriangleMultiplication`**: The triangle contraction is completed over `k` for local output rows using `trimul.contract` [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:17]().
*   **`TriangleAttention`**:
    *   `per_row` (starting node): The non-batched pair bias is gathered using `triatt.bias_full` [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:18-19]().
    *   `per_column` (ending node): Involves an `all_to_all` for transposing column blocks to row blocks [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:20-21]().
*   **`apply_shardings()` / `wrap_runner()`**: Uses `jax.jit(in_shardings=, out_shardings=)` to manage sharding for the recycled pair, distogram logits, and aligned-error logits [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:32-33]().

### `rowpair_jax/alphafold3.py`: AlphaFold3 JAX Integration

This module extends the JAX integration for AlphaFold3-specific components, ensuring that the pair representation is sharded appropriately.

Sources:
- [common/opt_core/opt_core/mem/rowpair/dist.py:1-3]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:44-48]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:21-24]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:33-36]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:25-32]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:51]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:52]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:55]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:57-58]()
- [common/opt_core/opt_core/mem/rowpair/triatt.py:1-3]()
- [common/opt_core/opt_core/mem/rowpair/triatt.py:21]()
- [common/opt_core/opt_core/mem/rowpair/triatt.py:22-25]()
- [common/opt_core/opt_core/mem/rowpair/triatt.py:26-27]()
- [common/opt_core/opt_core/mem/rowpair/triatt.py:29-36]()
- [common/opt_core/opt_core/mem/rowpair/triatt.py:38-46]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:11]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:12-15]()
- [boltz2/opt/boltz2_opt/rowpair.py:54-56]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:31-39]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:37-39]()
- [common/opt_core/tests/test_rowpair_confidence_043.py:11]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:58-60]()
- [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:1-3]()
- [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:13-14]()
- [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:17]()
- [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:18-19]()
- [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:20-21]()
- [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:32-33]()

## Rank Environment and Hashseed

The multi-GPU environment for rowpair sharding is configured through specific environment variables.

*   **`ROWPAIR_{RANK,WORLD,LOCAL_RANK,ADDR,PORT}`**: These variables are set by the `opt_core.mem.rowpair.launch` module to define the distributed environment for each rank [common/opt_core/opt_core/mem/rowpair/dist.py:33-36]().
*   **Hashseed**: For deterministic behavior across ranks, especially in JAX environments, random number generator (RNG) states are carefully managed. For example, in RF3, rank 0's host RNG state is adopted by other ranks [rosettafold3/opt/rosettafold3_opt/rowpair.py:14-16](). In JAX, `haiku.body_frame` ensures RNG-less application within regions, with keys drawn outside [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:48-49]().

## Feature Digest Census

The "feature digest census" refers to the detailed reporting of how features are handled under rowpair sharding. This includes:

*   **Replicated Features**: Features that are replicated across all ranks are explicitly named in the report and schedule census (e.g., `s_inputs`, `s`, token-pair masks, atom tensors) [protenix_v1/opt/protenix_v1_opt/tp.py:50-51]().
*   **Host-Resident Features**: Features that reside on the host and are sliced to local rows only when needed are also named (e.g., `token_bonds`, template pair features, raw MSA features) [protenix_v1/opt/protenix_v1_opt/tp.py:51-56]().
*   **Placement Words (`TP_EXPORTS`)**: Environment variables like `ROWPAIR_PARK_ZINIT`, `ROWPAIR_MSA_HOST`, and `ROWPAIR_MSA_M_LAYOUT` are recorded in the `report()['tp_exports']` to indicate how specific memory optimizations are applied [boltz2/opt/boltz2_opt/rowpair.py:52-59]().
*   **Census Output**: The `opt_manifest.json` and `cell_census` provide detailed information about memory usage, kernel choices, and data movement, including bytes for gathered data and the state of various features (e.g., `msa_host`, `msa_m`, `opm_a`, `opm_b_gather_gib`) [boltz2/opt/boltz2_opt/rowpair.py:57-60]().

## `API.md` Contract

The `opt_core/mem/rowpair/API.md` file defines the contract for how kits should interact with the rowpair sharding mechanism. It outlines the expected interface words and the recipe for adapting modules. This contract ensures consistency and proper integration across different kits.

The `API.md` specifies:
*   **Input/Output**: Tensors in, tensors out, with no arithmetic on payloads except integer checksums [common/opt_core/opt_core/mem/rowpair/dist.py:1-2]().
*   **Row-Sharded Convention**: A pair tensor `X[N, N, C]` is row-sharded, with rank `q` holding `X[q0:q1, :, :]` [common/opt_core/opt_core/mem/rowpair/dist.py:5-6]().
*   **`Comm` Object**: All collective operations go through the `Comm` object returned by `comm()` [common/opt_core/opt_core/mem/rowpair/dist.py:14-16]().
*   **`Layout` Object**: The `Layout` class defines the row partition [common/opt_core/opt_core/mem/rowpair/dist.py:44-48]().
*   **P=1 Support**: The system is designed to support `P == 1` (single GPU) gracefully, with equality semantics and no communication [common/opt_core/opt_core/mem/rowpair/dist.py:18]().

This contract is crucial for kit developers to understand how to correctly implement rowpair sharding for their specific models, ensuring compatibility and optimal performance.

Sources:
- [common/opt_core/opt_core/mem/rowpair/dist.py:33-36]()
- [rosettafold3/opt/rosettafold3_opt/rowpair.py:14-16]()
- [common/opt_core/opt_core/mem/rowpair_jax/alphafold.py:48-49]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:50-51]()
- [protenix_v1/opt/protenix_v1_opt/tp.py:51-56]()
- [boltz2/opt/boltz2_opt/rowpair.py:52-59]()
- [boltz2/opt/boltz2_opt/rowpair.py:57-60]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:1-2]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:5-6]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:14-16]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:44-48]()
- [common/opt_core/opt_core/mem/rowpair/dist.py:18]()

---

