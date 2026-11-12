<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/uplifting-biomolecular-modeling · extra page Per-Kit Tensor-Parallel Adapters · fetched 2026-10-26 -->

# Per-Kit Tensor-Parallel Adapters

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [af3_jax/opt/af3_jax_opt/tests/test_big.py](af3_jax/opt/af3_jax_opt/tests/test_big.py)
- [af3_torch/opt/af3_torch_opt/tests/test_n_gpu.py](af3_torch/opt/af3_torch_opt/tests/test_n_gpu.py)
- [boltz2/opt/boltz2_opt/prefetch.py](boltz2/opt/boltz2_opt/prefetch.py)
- [boltz2/opt/boltz2_opt/tests/test_ngpu.py](boltz2/opt/boltz2_opt/tests/test_ngpu.py)
- [boltz2/opt/boltz2_opt/tests/test_prefetch.py](boltz2/opt/boltz2_opt/tests/test_prefetch.py)
- [boltz2/opt/boltz2_opt/tp.py](boltz2/opt/boltz2_opt/tp.py)
- [boltz2/opt/boltz2_opt/writer.py](boltz2/opt/boltz2_opt/writer.py)
- [boltz2/stock/src/boltz/data/write/writer.py](boltz2/stock/src/boltz/data/write/writer.py)
- [boltzgen/opt/host/writer_levers/src/hl_levers.py](boltzgen/opt/host/writer_levers/src/hl_levers.py)
- [chai1/opt/chai1_opt/ngpu.py](chai1/opt/chai1_opt/ngpu.py)
- [common/opt_core/opt_core/host/outputs.py](common/opt_core/opt_core/host/outputs.py)
- [common/opt_core/opt_core/host_cache/bg_writer.py](common/opt_core/opt_core/host_cache/bg_writer.py)
- [common/opt_core/opt_core/kernels/apb/fpf_apb/__init__.py](common/opt_core/opt_core/kernels/apb/fpf_apb/__init__.py)
- [common/opt_core/opt_core/kernels/apb/fpf_apb/install.py](common/opt_core/opt_core/kernels/apb/fpf_apb/install.py)
- [common/opt_core/opt_core/mem/ngpu.py](common/opt_core/opt_core/mem/ngpu.py)
- [common/opt_core/opt_core/mem/offload.py](common/opt_core/opt_core/mem/offload.py)
- [common/opt_core/opt_core/mem/rowpair/msa.py](common/opt_core/opt_core/mem/rowpair/msa.py)
- [common/opt_core/opt_core/mem/torch_hostpair.py](common/opt_core/opt_core/mem/torch_hostpair.py)
- [common/opt_core/tests/test_rowpair_diffusion_043.py](common/opt_core/tests/test_rowpair_diffusion_043.py)
- [common/opt_core/tests/test_rowpair_hostslab_0513.py](common/opt_core/tests/test_rowpair_hostslab_0513.py)
- [common/opt_core/tests/test_rowpair_msa_043.py](common/opt_core/tests/test_rowpair_msa_043.py)
- [common/opt_core/tests/test_rowpair_rankdata_launch.py](common/opt_core/tests/test_rowpair_rankdata_launch.py)
- [common/opt_core/tests/test_rowpair_templ_zparked_0515.py](common/opt_core/tests/test_rowpair_templ_zparked_0515.py)
- [common/opt_core/tests/test_rowpair_trimul_ablock_05189.py](common/opt_core/tests/test_rowpair_trimul_ablock_05189.py)
- [esmfold2/opt/esmfold2_opt/tests/test_rowpair_feats.py](esmfold2/opt/esmfold2_opt/tests/test_rowpair_feats.py)
- [esmfold2/opt/esmfold2_opt/tp.py](esmfold2/opt/esmfold2_opt/tp.py)
- [opendde/opt/forward/fast_inference/levers/ACCEL/odde_accel_v2.py](opendde/opt/forward/fast_inference/levers/ACCEL/odde_accel_v2.py)
- [opendde/opt/forward/fast_inference/levers/OFFLOAD/odde_offload_trunk.py](opendde/opt/forward/fast_inference/levers/OFFLOAD/odde_offload_trunk.py)
- [opendde/opt/forward/fast_inference/levers/SAMPLER/odde_apb_bind.py](opendde/opt/forward/fast_inference/levers/SAMPLER/odde_apb_bind.py)
- [opendde/opt/opendde_opt/big.py](opendde/opt/opendde_opt/big.py)
- [opendde/opt/opendde_opt/chunklift.py](opendde/opt/opendde_opt/chunklift.py)
- [opendde/opt/opendde_opt/smalln.py](opendde/opt/opendde_opt/smalln.py)
- [opendde/opt/opendde_opt/stepgraph.py](opendde/opt/opendde_opt/stepgraph.py)
- [opendde/opt/opendde_opt/stockknob.py](opendde/opt/opendde_opt/stockknob.py)
- [opendde/opt/opendde_opt/tests/test_big_adapter.py](opendde/opt/opendde_opt/tests/test_big_adapter.py)
- [opendde/opt/opendde_opt/tests/test_big_resident_stepgraph.py](opendde/opt/opendde_opt/tests/test_big_resident_stepgraph.py)
- [opendde/opt/opendde_opt/tests/test_chunklift.py](opendde/opt/opendde_opt/tests/test_chunklift.py)
- [opendde/opt/opendde_opt/tests/test_ngpu.py](opendde/opt/opendde_opt/tests/test_ngpu.py)
- [opendde/opt/opendde_opt/tests/test_smalln.py](opendde/opt/opendde_opt/tests/test_smalln.py)
- [opendde/opt/opendde_opt/tests/test_stepgraph.py](opendde/opt/opendde_opt/tests/test_stepgraph.py)
- [opendde/opt/opendde_opt/tests/test_stock_knobs.py](opendde/opt/opendde_opt/tests/test_stock_knobs.py)
- [opendde/opt/opendde_opt/tests/test_tp_diffusion_cpu.py](opendde/opt/opendde_opt/tests/test_tp_diffusion_cpu.py)
- [opendde/opt/opendde_opt/tests/test_tp_kernels.py](opendde/opt/opendde_opt/tests/test_tp_kernels.py)
- [opendde/opt/opendde_opt/tp.py](opendde/opt/opendde_opt/tp.py)
- [opendde/opt/opendde_opt/tp_kernels.py](opendde/opt/opendde_opt/tp_kernels.py)
- [openfold3/opt/openfold3_opt/tests/test_tp_kernels_cpu.py](openfold3/opt/openfold3_opt/tests/test_tp_kernels_cpu.py)
- [openfold3/opt/openfold3_opt/tp_rowpair/env.py](openfold3/opt/openfold3_opt/tp_rowpair/env.py)
- [openfold3_ob0/opt/openfold3_ob0_opt/tests/test_tp_kernels_cpu.py](openfold3_ob0/opt/openfold3_ob0_opt/tests/test_tp_kernels_cpu.py)
- [openfold3_ob0/opt/openfold3_ob0_opt/tp_rowpair/env.py](openfold3_ob0/opt/openfold3_ob0_opt/tp_rowpair/env.py)
- [protenix_v1/opt/forward/v05_addon/ptxfpf/apb_ptx1.py](protenix_v1/opt/forward/v05_addon/ptxfpf/apb_ptx1.py)
- [protenix_v1/opt/protenix_v1_opt/ngpu.py](protenix_v1/opt/protenix_v1_opt/ngpu.py)
- [protenix_v1/opt/protenix_v1_opt/tests/test_ngpu.py](protenix_v1/opt/protenix_v1_opt/tests/test_ngpu.py)
- [protenix_v1/opt/protenix_v1_opt/tests/test_rank_hashseed.py](protenix_v1/opt/protenix_v1_opt/tests/test_rank_hashseed.py)
- [protenix_v1/opt/protenix_v1_opt/tests/test_stock_knobs.py](protenix_v1/opt/protenix_v1_opt/tests/test_stock_knobs.py)
- [protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/summary.py](protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/summary.py)
- [protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/trimul.py](protenix_v2/opt/forward/PTX_TP/PTX_TP_ADDON/ptx_tp/trimul.py)
- [protenix_v2/opt/forward/flashpairformer/src/ptx_msa_adapt/pwa_zcache.py](protenix_v2/opt/forward/flashpairformer/src/ptx_msa_adapt/pwa_zcache.py)
- [protenix_v2/opt/forward/flashpairformer/third_party/fpf_cueq_pad8exact/__init__.py](protenix_v2/opt/forward/flashpairformer/third_party/fpf_cueq_pad8exact/__init__.py)
- [protenix_v2/opt/forward/flashpairformer/third_party/fpf_pad8exact/__init__.py](protenix_v2/opt/forward/flashpairformer/third_party/fpf_pad8exact/__init__.py)
- [protenix_v2/opt/protenix_opt/apb_core.py](protenix_v2/opt/protenix_opt/apb_core.py)
- [protenix_v2/opt/protenix_opt/dtype_gate.py](protenix_v2/opt/protenix_opt/dtype_gate.py)
- [protenix_v2/opt/protenix_opt/sampler_poison_aside.py](protenix_v2/opt/protenix_opt/sampler_poison_aside.py)
- [protenix_v2/opt/protenix_opt/tests/test_dtype_gate.py](protenix_v2/opt/protenix_opt/tests/test_dtype_gate.py)
- [protenix_v2/opt/protenix_opt/tests/test_sampler_poison_aside.py](protenix_v2/opt/protenix_opt/tests/test_sampler_poison_aside.py)
- [protenix_v2/opt/protenix_opt/tests/test_sealed_third_party.py](protenix_v2/opt/protenix_opt/tests/test_sealed_third_party.py)
- [protenix_v2/opt/protenix_opt/tests/test_tp.py](protenix_v2/opt/protenix_opt/tests/test_tp.py)
- [protenix_v2/opt/protenix_opt/tests/test_tp_rebase_diffusion.py](protenix_v2/opt/protenix_opt/tests/test_tp_rebase_diffusion.py)
- [protenix_v2/opt/protenix_opt/tp.py](protenix_v2/opt/protenix_opt/tp.py)
- [rfdiffusion3/opt/forward/xattempt_addon/patched/rfd3/model/layers/pairformer_layers.py](rfdiffusion3/opt/forward/xattempt_addon/patched/rfd3/model/layers/pairformer_layers.py)
- [rosettafold3/opt/rosettafold3_opt/tests/test_ngpu.py](rosettafold3/opt/rosettafold3_opt/tests/test_ngpu.py)
- [rosettafold3/opt/rosettafold3_opt/tests/test_rowpair.py](rosettafold3/opt/rosettafold3_opt/tests/test_rowpair.py)

</details>



This page details how individual kits integrate the tensor-parallel (TP) functionality provided by `opt_core`'s `tp.py`, `ngpu.py`, and `rowpair_*.py` modules. It covers the mechanisms for wiring these core components into the kit's diffusion and confidence heads, and how mismatches or unsupported configurations lead to refusals.

## Tensor Parallelism Overview

Tensor parallelism, specifically row-sharded parallelism, is a technique used to distribute large tensors across multiple GPUs. Instead of replicating the entire tensor on each device, each GPU holds a slice (rows) of the tensor. This allows for processing models that would otherwise exceed the memory capacity of a single GPU. The `opt_core.mem.rowpair` module provides the foundational primitives for this sharding strategy.

The core `opt_core.mem.ngpu` module manages the multi-GPU environment, including device visibility checks and refusal logic for unsupported configurations. Kits integrate with these core modules to enable or disable tensor parallelism based on the selected mode and available hardware.

Sources:
- [common/opt_core/opt_core/mem/ngpu.py]()
- [rosettafold3/opt/rosettafold3_opt/tests/test_rowpair.py:1-12]()

## Kit Integration with `opt_core.mem.ngpu`

Each kit that supports tensor parallelism defines its own `ngpu.py` (or `tp.py`) module to interface with the `opt_core.mem.ngpu` functionality. This module is responsible for:
1.  **Determining Effective `n_gpu`**: Parsing command-line arguments (`--n_gpu`) and environment variables (e.g., `PROTENIX_OPT_N_GPU`) to establish the requested number of GPUs. Command-line arguments take precedence over environment variables.
2.  **Admitting or Refusing Configurations**: Based on the requested `n_gpu` and the current kit mode, the `ngpu.admit()` function (or its kit-specific wrapper) decides whether the configuration is supported.
3.  **Reporting `n_gpu` Status**: Generating standardized token text for `n_gpu` and sharding status (e.g., "n_gpu=2 sharding=rowpair") for activation, final, and exit logs.

### `n_gpu` Resolution and Refusal Logic

The `n_gpu` value is resolved from various sources, with command-line arguments having the highest priority.

```mermaid
graph TD
    A[Start] --> B{Is --n_gpu specified?};
    B -- Yes --> C[Use --n_gpu value];
    B -- No --> D{Is KIT_OPT_N_GPU env var set?};
    D -- Yes --> E[Use KIT_OPT_N_GPU value];
    D -- No --> F[Default to n_gpu = 1];
    C --> G[Validate n_gpu is positive integer];
    E --> G;
    F --> G;
    G -- Invalid --> H[Raise ValueError / TpError];
    G -- Valid --> I{Is n_gpu > 1?};
    I -- Yes --> J{Is mode "big"?};
    I -- No (n_gpu=1) --> K[Admit n_gpu=1 for any mode];
    J -- No --> L[Refuse: n_gpu>1 requires --mode big];
    J -- Yes --> M{Are visible GPUs >= n_gpu?};
    M -- No --> N[Refuse: n_gpu=P visible=V];
    M -- Yes --> O{Is n_gpu in kit's SUPPORTED_P?};
    O -- No --> P[Refuse: n_gpu=P not served by kit];
    O -- Yes --> Q[Admit n_gpu=P for "big" mode];
    H --> R[Exit with code 2 (Usage Error)];
    L --> R;
    N --> R;
    P --> R;
    K --> S[Proceed with execution];
    Q --> S;
```
**Diagram: `n_gpu` Resolution and Refusal Flow**

Sources:
- [protenix_v1/opt/protenix_v1_opt/tests/test_ngpu.py:14-29]()
- [protenix_v1/opt/protenix_v1_opt/tests/test_ngpu.py:47-51]()
- [protenix_v1/opt/protenix_v1_opt/tests/test_ngpu.py:54-61]()
- [protenix_v2/opt/protenix_opt/tests/test_tp.py:48-58]()
- [protenix_v2/opt/protenix_opt/tests/test_tp.py:60-70]()
- [rosettafold3/opt/rosettafold3_opt/tests/test_ngpu.py:29-33]()
- [rosettafold3/opt/rosettafold3_opt/tests/test_ngpu.py:45-52]()
- [opendde/opt/opendde_opt/tests/test_ngpu.py:31-35]()
- [opendde/opt/opendde_opt/tests/test_ngpu.py:38-45]()
- [boltz2/opt/boltz2_opt/tests/test_ngpu.py:37-41]()
- [boltz2/opt/boltz2_opt/tests/test_ngpu.py:44-55]()

### Standardized Token Text

Kits ensure that the `n_gpu` and sharding information is consistently reported in log lines. This allows external log parsers to reliably extract this information.

Example token text:
- `n_gpu=1 sharding=none` for single-GPU runs.
- `n_gpu=P sharding=rowpair` for multi-GPU tensor-parallel runs.

This token text appears in `ACTIVE`, `FINAL`, and `EXIT` lines.

Sources:
- [protenix_v1/opt/protenix_v1_opt/tests/test_ngpu.py:31-45]()
- [protenix_v2/opt/protenix_opt/tests/test_tp.py:85-95]()
- [rosettafold3/opt/rosettafold3_opt/tests/test_ngpu.py:14-26]()
- [opendde/opt/opendde_opt/tests/test_ngpu.py:16-27]()
- [boltz2/opt/boltz2_opt/tests/test_ngpu.py:17-30]()

## Wiring `rowpair_*.py` into Trunks and Heads

The `opt_core.mem.rowpair` module provides the core logic for row-sharded tensor parallelism. Kits integrate this by:
1.  **Defining `rowpair.plan()`**: This function outlines the sharding strategy, the modules to be installed, and any conflicts with other levers. For example, `rosettafold3`'s `rowpair.plan()` specifies "rowpair" sharding for `n_gpu > 1` and lists sites like "pair_init", "recycler", "distogram", "conf_head", "denoiser", and "dit" for installation.
2.  **Implementing `rowpair.launch_argv()` and `rowpair.run_ranks()`**: These functions handle the multi-process launch, ensuring each rank receives its correct `argv` and environment variables, including a consistent `PYTHONHASHSEED` for deterministic data pipeline behavior across ranks.
3.  **Integrating with Diffusion and Confidence Heads**: For models like AlphaFold3-family, the diffusion transformer (`dit`) and confidence heads are critical components that benefit from tensor parallelism. Kits like `opendde_opt` and `rosettafold3_opt` have specific `tp_diffusion.py` and `tp_rowpair.py` modules that bind the core's row-sharded primitives to these model parts.

### Example: RosettaFold3 `rowpair.plan()`

The `rosettafold3` kit's `rowpair.plan()` function details the tensor parallelism strategy.

```python
# rosettafold3/opt/rosettafold3_opt/rowpair.py (conceptual, based on test_plan_facts)
def plan(n_gpu: int, mode: str = "big") -> Dict[str, Any]:
    if n_gpu == 1:
        return {"sharding": "none", "installs": [], "conflicts": {}}
    if mode != "big":
        # Refusal logic handled by ngpu.admit() earlier
        pass
    
    # ... detailed plan for n_gpu > 1, mode="big"
    return {
        "sharding": "rowpair",
        "strategy": "F7.tensor_parallel",
        "lever": "rowpair",
        "sites": [
            {"site": "entry", "module": "..."},
            {"site": "pair_init", "module": "..."},
            {"site": "recycler", "module": "..."},
            {"site": "distogram", "module": "..."},
            {"site": "conf_head", "module": "..."},
            {"site": "denoiser", "module": "..."},
            {"site": "dit", "module": "..."},
            # ... other sharded sites
        ],
        "installs": [
            "ConfidenceHead.forward",
            "Recycler.forward",
            "FeatureInitializer.forward",
            # ... other patched methods
        ],
        "conflicts": {
            "fpf_trimul", "fpf_res", "graph", "dtk" # levers off by name under n_gpu > 1
        },
        "replicated": [
            "MSA representation is replicated" # example of replicated data
        ]
    }
```
The `plan()` function defines which parts of the model are sharded and which levers are incompatible with tensor parallelism.

Sources:
- [rosettafold3/opt/rosettafold3_opt/tests/test_rowpair.py:53-67]()

### Multi-Process Launch and Determinism

When `n_gpu > 1`, the kit's `fold.launch()` (or equivalent) invokes `rowpair.launch_argv()` which in turn uses `opt_core.mem.rowpair.launch.run_rank_processes` to start multiple Python interpreters, one for each GPU. A crucial aspect is ensuring deterministic behavior across these ranks. This is achieved by setting a consistent `PYTHONHASHSEED` environment variable for all rank processes.

```mermaid
graph TD
    A[Kit CLI Call] --> B{n_gpu > 1?};
    B -- Yes --> C[Kit's fold.launch()];
    C --> D[Calls rowpair.launch_argv()];
    D --> E[Prepares argv for each rank];
    E --> F[Sets consistent PYTHONHASHSEED];
    F --> G[Calls opt_core.mem.rowpair.launch.run_rank_processes];
    G --> H[Launches P Python interpreters];
    H --> I[Each interpreter runs with its rank's argv and env];
    I --> J[Data pipeline set/dict iteration orders are consistent];
    B -- No --> K[Kit's fold.launch() runs single process];
```
**Diagram: Multi-GPU Launch Flow**

Sources:
- [rosettafold3/opt/rosettafold3_opt/tests/test_rowpair.py:83-93]()
- [rosettafold3/opt/rosettafold3_opt/tests/test_rowpair.py:108-112]()
- [rosettafold3/opt/rosettafold3_opt/tests/test_ngpu.py:105-119]()

### Tensor-Parallel Kernels for Triangle Operations

Kits leverage `opt_core.mem.rowpair.triatt` and `opt_core.mem.rowpair.trimul_fused` for optimized triangle attention and multiplication operations in a row-sharded context. These core modules provide kernel dispatch mechanisms that can select between highly optimized kernels (e.g., `flash_triattn`, `fpf_v4`) or fallback to stock PyTorch implementations if the optimized kernels are not available or suitable for the given hardware/configuration.

For example, `openfold3_opt` and `openfold3_ob0_opt` define `tp_rowpair.pairstack` which binds these triangle kernels.

```mermaid
graph TD
    A[Model Layer (e.g., TriangleAttention)] --> B[Kit's tp_rowpair.pairstack.triatt_fns()];
    B --> C{ROWPAIR_TRIATT_CORE env var set to "torch"?};
    C -- Yes --> D[Use stock PyTorch implementation];
    C -- No --> E[Attempt to dispatch optimized kernel (e.g., flash_triattn)];
    E --> F{Is optimized kernel available and suitable?};
    F -- No --> G[Refuse by name (RowpairRefused)];
    F -- Yes --> H[Execute optimized kernel];
    D --> I[Return result];
    H --> I;
    G --> J[Fallback to stock PyTorch (if configured) or error];
```
**Diagram: Triangle Kernel Dispatch**

Sources:
- [openfold3_ob0/opt/openfold3_ob0_opt/tests/test_tp_kernels_cpu.py:61-69]()
- [openfold3_ob0/opt/openfold3_ob0_opt/tests/test_tp_kernels_cpu.py:88-96]()
- [openfold3_ob0/opt/openfold3_ob0_opt/tests/test_tp_kernels_cpu.py:99-108]()
- [openfold3/opt/openfold3_opt/tests/test_tp_kernels_cpu.py:61-69]()
- [openfold3/opt/openfold3_opt/tests/test_tp_kernels_cpu.py:88-96]()
- [openfold3/opt/openfold3_opt/tests/test_tp_kernels_cpu.py:99-108]()

## Host Memory Management for Row-Sharded Tensors

The `opt_core.mem.torch_hostpair` module provides mechanisms for managing host-pinned memory for row-sharded tensors. This is crucial for "big" mode, where the full tensor might not fit on a single GPU.
-   **`PinPool`**: Manages a pool of pinned (page-locked) host memory, allowing efficient DMA transfers between host and device. It enforces a byte budget and checks for available host RAM.
-   **`HostChunks`**: Provides a way to store and load contiguous tensor bytes in chunks from the `PinPool`. This is used for parking row slabs and for triangle multiplication row mirrors.
-   **`HostPair`**: Represents a pinned-host mirror of a pair tensor, allowing row blocks to be transferred to the device as needed.
-   **`LayerNormGuard`**: A mechanism to split large `LayerNorm` operations into smaller, row-wise blocks if the tensor size exceeds a certain limit (e.g., 2^31 elements), to avoid potential numerical issues or limitations in some PyTorch builds.

These components are used by kits to manage memory for large models, particularly in the "big" mode, where tensors are too large to reside entirely on a single GPU.

Sources:
- [common/opt_core/opt_core/mem/torch_hostpair.py:1-45]()
- [common/opt_core/opt_core/mem/torch_hostpair.py:90-90]()

## Refusals on Mismatch

A core principle of the optimization kits is "fail-loud, fail-early". If a requested configuration for tensor parallelism is not supported or conflicts with other settings, the system will refuse to activate the optimization and provide a clear reason. This prevents silent fallbacks to slower paths or incorrect behavior.

Common refusal scenarios include:
-   `n_gpu > 1` requested for a mode other than "big".
-   Fewer visible GPUs than requested `n_gpu`.
-   Requested `n_gpu` not in the kit's `SUPPORTED_P` set.
-   Core `opt_core.mem.rowpair` modules or specific kernel functions are absent or too old.
-   Attempting to run optimized kernels on CPU tensors when they are GPU-specific.

These refusals are typically raised as `ValueError`, `TpError`, `NGpuRefused`, or `RowpairRefused` exceptions, with detailed messages explaining the reason.

Sources:
- [protenix_v1/opt/protenix_v1_opt/tests/test_ngpu.py:47-51]()
- [protenix_v1/opt/protenix_v1_opt/tests/test_ngpu.py:54-61]()
- [protenix_v1/opt/protenix_v1_opt/tests/test_ngpu.py:79-89]()
- [protenix_v2/opt/protenix_opt/tests/test_tp.py:74-80]()
- [rosettafold3/opt/rosettafold3_opt/tests/test_ngpu.py:29-33]()
- [rosettafold3/opt/rosettafold3_opt/tests/test_ngpu.py:36-41]()
- [rosettafold3/opt/rosettafold3_opt/tests/test_ngpu.py:61-69]()
- [opendde/opt/opendde_opt/tests/test_ngpu.py:31-35]()
- [opendde/opt/opendde_opt/tests/test_ngpu.py:38-45]()
- [opendde/opt/opendde_opt/tests/test_ngpu.py:48-61]()
- [boltz2/opt/boltz2_opt/tests/test_ngpu.py:37-41]()
- [boltz2/opt/boltz2_opt/tests/test_ngpu.py:44-55]()
- [openfold3_ob0/opt/openfold3_ob0_opt/tests/test_tp_kernels_cpu.py:99-108]()
- [openfold3/opt/openfold3_opt/tests/test_tp_kernels_cpu.py:99-108]()

---

