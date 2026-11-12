<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/uplifting-biomolecular-modeling · page 7 Testing and Verification Strategy · fetched 2026-10-26 -->

# Testing and Verification Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [af2ig/opt/af2ig_opt/tests/test_cli.py](af2ig/opt/af2ig_opt/tests/test_cli.py)
- [af3_torch/opt/af3_torch_opt/tests/test_core_adoption.py](af3_torch/opt/af3_torch_opt/tests/test_core_adoption.py)
- [boltzgen/opt/boltzgen_opt/tests/test_core_adoption.py](boltzgen/opt/boltzgen_opt/tests/test_core_adoption.py)
- [colabdesign/opt/colabdesign_opt/tests/test_hoist_prev.py](colabdesign/opt/colabdesign_opt/tests/test_hoist_prev.py)
- [colabdesign/opt/colabdesign_opt/tests/test_launchers.py](colabdesign/opt/colabdesign_opt/tests/test_launchers.py)
- [colabfold/opt/colabfold_opt/tests/test_weights_memo.py](colabfold/opt/colabfold_opt/tests/test_weights_memo.py)
- [common/opt_core/tests/test_core_gate.py](common/opt_core/tests/test_core_gate.py)
- [common/opt_core/tests/test_trimul_lever_gate.py](common/opt_core/tests/test_trimul_lever_gate.py)
- [ef2inv/opt/ef2inv_opt/tests/test_core_pin.py](ef2inv/opt/ef2inv_opt/tests/test_core_pin.py)
- [esmfold2/opt/esmfold2_opt/tests/test_core_missing.py](esmfold2/opt/esmfold2_opt/tests/test_core_missing.py)
- [evo2/opt/evo2_opt/tests/test_specdec_state.py](evo2/opt/evo2_opt/tests/test_specdec_state.py)
- [flashzoi/opt/flashzoi_opt/tests/test_multi.py](flashzoi/opt/flashzoi_opt/tests/test_multi.py)
- [genie3/opt/genie3_opt/_core.py](genie3/opt/genie3_opt/_core.py)
- [genie3/opt/genie3_opt/tests/test_activation_rules.py](genie3/opt/genie3_opt/tests/test_activation_rules.py)
- [genie3/opt/genie3_opt/tests/test_core.py](genie3/opt/genie3_opt/tests/test_core.py)
- [mosaic/opt/mosaic_opt/tests/test_core_adoption.py](mosaic/opt/mosaic_opt/tests/test_core_adoption.py)
- [mosaic/opt/mosaic_opt/tests/test_flashattn_lever.py](mosaic/opt/mosaic_opt/tests/test_flashattn_lever.py)
- [opendde/opt/opendde_opt/tests/test_core_gate.py](opendde/opt/opendde_opt/tests/test_core_gate.py)
- [opendde/stock/src/tests/test_atom_attention_decoder.py](opendde/stock/src/tests/test_atom_attention_decoder.py)
- [opendde/stock/src/tests/test_attention_pair_bias.py](opendde/stock/src/tests/test_attention_pair_bias.py)
- [opendde/stock/src/tests/test_featurizer_optimizations.py](opendde/stock/src/tests/test_featurizer_optimizations.py)
- [opendde/stock/src/tests/test_utils.py](opendde/stock/src/tests/test_utils.py)
- [openfold3/opt/openfold3_opt/tests/test_core_adoption.py](openfold3/opt/openfold3_opt/tests/test_core_adoption.py)
- [openfold3/stock/src/openfold3/tests/test_diffusion_loss.py](openfold3/stock/src/openfold3/tests/test_diffusion_loss.py)
- [openfold3/stock/src/openfold3/tests/test_validation_metrics.py](openfold3/stock/src/openfold3/tests/test_validation_metrics.py)
- [openfold3_ob0/opt/openfold3_ob0_opt/tests/test_core_adoption.py](openfold3_ob0/opt/openfold3_ob0_opt/tests/test_core_adoption.py)
- [openfold3_ob0/stock/src/openfold3/tests/test_confidence_metrics.py](openfold3_ob0/stock/src/openfold3/tests/test_confidence_metrics.py)
- [openfold3_ob0/stock/src/openfold3/tests/test_diffusion_loss.py](openfold3_ob0/stock/src/openfold3/tests/test_diffusion_loss.py)
- [openfold3_ob0/stock/src/openfold3/tests/test_validation_metrics.py](openfold3_ob0/stock/src/openfold3/tests/test_validation_metrics.py)
- [proteinmpnn/opt/proteinmpnn_opt/tests/test_core_adoption.py](proteinmpnn/opt/proteinmpnn_opt/tests/test_core_adoption.py)
- [proteinmpnn/opt/proteinmpnn_opt/tests/test_settings_det.py](proteinmpnn/opt/proteinmpnn_opt/tests/test_settings_det.py)
- [protenix_v1/opt/protenix_v1_opt/__main__.py](protenix_v1/opt/protenix_v1_opt/__main__.py)
- [protenix_v1/opt/protenix_v1_opt/tests/test_core_gate.py](protenix_v1/opt/protenix_v1_opt/tests/test_core_gate.py)
- [protenix_v1/opt/protenix_v1_opt/tests/test_core_names.py](protenix_v1/opt/protenix_v1_opt/tests/test_core_names.py)
- [protenix_v2/opt/protenix_opt/__main__.py](protenix_v2/opt/protenix_opt/__main__.py)
- [protenix_v2/opt/protenix_opt/_core.py](protenix_v2/opt/protenix_opt/_core.py)
- [protenix_v2/opt/protenix_opt/tests/test_core_adoption.py](protenix_v2/opt/protenix_opt/tests/test_core_adoption.py)
- [protenix_v2/opt/protenix_opt/tests/test_kit_paths.py](protenix_v2/opt/protenix_opt/tests/test_kit_paths.py)
- [protenix_v2/opt/protenix_opt/tests/test_stackgraph_plan.py](protenix_v2/opt/protenix_opt/tests/test_stackgraph_plan.py)
- [protenix_v2/stock/src/tests/test_attention_lddt_loss.py](protenix_v2/stock/src/tests/test_attention_lddt_loss.py)
- [protenix_v2/stock/src/tests/test_attention_pair_bias.py](protenix_v2/stock/src/tests/test_attention_pair_bias.py)
- [protenix_v2/stock/src/tests/test_dataset_vectorization.py](protenix_v2/stock/src/tests/test_dataset_vectorization.py)
- [protenix_v2/stock/src/tests/test_esm_loading.py](protenix_v2/stock/src/tests/test_esm_loading.py)
- [protenix_v2/stock/src/tests/test_featurizer_optimizations.py](protenix_v2/stock/src/tests/test_featurizer_optimizations.py)
- [protenix_v2/stock/src/tests/test_fused_dropout_add.py](protenix_v2/stock/src/tests/test_fused_dropout_add.py)
- [protenix_v2/stock/src/tests/test_utils.py](protenix_v2/stock/src/tests/test_utils.py)
- [pxdesign/opt/pxdesign_opt/tests/test_core_adoption.py](pxdesign/opt/pxdesign_opt/tests/test_core_adoption.py)
- [rfdiffusion1/opt/rfdiffusion1_opt/tests/test_core_gate_routes.py](rfdiffusion1/opt/rfdiffusion1_opt/tests/test_core_gate_routes.py)
- [rfdiffusion3/opt/rfdiffusion3_opt/tests/test_core_adoption.py](rfdiffusion3/opt/rfdiffusion3_opt/tests/test_core_adoption.py)
- [rfdiffusion3/opt/rfdiffusion3_opt/tests/test_core_gate_routes.py](rfdiffusion3/opt/rfdiffusion3_opt/tests/test_core_gate_routes.py)
- [rfdiffusion3/opt/rfdiffusion3_opt/tests/test_install_verb.py](rfdiffusion3/opt/rfdiffusion3_opt/tests/test_install_verb.py)
- [rfdiffusion3/opt/rfdiffusion3_opt/tests/test_merge_locks.py](rfdiffusion3/opt/rfdiffusion3_opt/tests/test_merge_locks.py)
- [rosettafold3/opt/rosettafold3_opt/tests/test_core_absent.py](rosettafold3/opt/rosettafold3_opt/tests/test_core_absent.py)
- [rosettafold3/opt/rosettafold3_opt/tests/test_core_pin.py](rosettafold3/opt/rosettafold3_opt/tests/test_core_pin.py)

</details>



This document outlines the comprehensive testing and verification strategy employed across the codebase. Given the complexity and performance-critical nature of biomolecular modeling, the testing surface is extensive, encompassing CPU-only behavioral tests, critical gate and refusal mechanisms, low-level kernel correctness, and parity with stock model implementations. This parent page provides a high-level overview, with detailed explanations and specific test examples linked in child pages.

The primary goal of this strategy is to ensure the correctness, robustness, and performance of the optimized kits while maintaining strict adherence to the behavior of their upstream stock counterparts. This involves verifying that optimizations do not introduce numerical inaccuracies or functional regressions, and that the system gracefully handles various environmental and configuration states.

## Activation, Gate and Refusal Tests

These tests focus on the system's startup and activation mechanisms, ensuring that kits engage correctly under specified conditions and refuse to activate when prerequisites are not met. This includes verifying the core gate's version checks, the autoloading process, and the behavior of the `install` verb. A critical aspect is the "fail-loud" principle, where the system explicitly reports reasons for refusal rather than silently failing or producing incorrect results. These tests also cover out-of-memory (OOM) propagation patterns to ensure predictable behavior under resource constraints.

For details, see [Activation, Gate and Refusal Tests](#7.1).

```mermaid
graph TD
    subgraph "Kit Activation Flow"
        A[User Command: `run.sh pred`] --> B{Core Gate Check};
        B -- "Core Missing/Stale/Unversioned" --> C[Refusal: `NOT ACTIVE` (Exit 3)];
        B -- "Core OK" --> D{Kit Autoload Hook};
        D -- "Mode Invalid/Unsupported" --> C;
        D -- "Mode Valid" --> E[Kit `stack.activate()`];
        E -- "Pins Unmet/Drift" --> F{Force Flag `AF2IG_OPT_FORCE=1`?};
        F -- "No" --> C;
        F -- "Yes" --> G[Kit Active: `ACTIVE` Line];
        G --> H[Run Prediction];
    end

    subgraph "Test Modules"
        T1["test_core_gate*.py"] --> B;
        T2["test_autoload.py"] --> D;
        T3["test_install_verb.py"] --> A;
        T4["test_cli.py"] --> A;
        T5["test_weights_memo.py"] --> E;
    end

    T1 & T2 & T3 & T4 & T5 --> C;

    style C fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#bfb,stroke:#333,stroke-width:2px
```
Sources:
- [rfdiffusion1/opt/rfdiffusion1_opt/tests/test_core_gate_routes.py:1-16]()
- [af3_torch/opt/af3_torch_opt/tests/test_core_adoption.py:56-73]()
- [pxdesign/opt/pxdesign_opt/tests/test_core_adoption.py:80-99]()
- [opendde/opt/opendde_opt/tests/test_core_gate.py:1-18]()
- [colabfold/opt/colabfold_opt/tests/test_weights_memo.py:1-3]()
- [af2ig/opt/af2ig_opt/tests/test_cli.py:76-90]()

## Numerics and Kernel Correctness Tests

This category ensures the numerical fidelity and functional correctness of the optimized kernels and core components. It includes rigorous testing of `opt_core` provider cells, end-to-end logic for `rowpair` sharding, and specific attention and feature tests for models like ESMFold2. Stock model loss and metric tests are performed to guarantee that optimized kits produce results numerically identical or within acceptable tolerances of their upstream counterparts. Synthetic fixtures are often used to isolate and test specific components.

For details, see [Numerics and Kernel Correctness Tests](#7.2).

```mermaid
graph TD
    subgraph "Numerical & Kernel Correctness"
        A[Synthetic Fixtures] --> B(opt_core Provider Cell Tests);
        B --> C{Kernel `admits()` / `select()`};
        C -- "Kernel Selected" --> D[Execute Optimized Kernel];
        C -- "Kernel Refused" --> E[Execute Fallback Kernel];
        D & E --> F(Numerical Output Comparison);
        F --> G{Stock Parity Check};
        G -- "Within Tolerance" --> H[Test Pass];
        G -- "Outside Tolerance" --> I[Test Fail];

        J[Rowpair Sharding Logic] --> K(Rowpair E2E Tests);
        K --> F;

        L[ESMFold2 Attention/Feature] --> M(ESMFold2 Specific Tests);
        M --> F;

        N[Stock Model Loss & Metrics] --> O(Loss/Metric Tests);
        O --> F;
    end

    subgraph "Code Entities"
        CE1["opt_core/kernels/*"] --> B;
        CE2["opt_core/mem/rowpair.py"] --> J;
        CE3["esmfold2/opt/esmfold2_opt/tests/*"] --> L;
        CE4["openfold3/stock/src/openfold3/tests/test_diffusion_loss.py"] --> N;
        CE5["openfold3/stock/src/openfold3/tests/test_validation_metrics.py"] --> N;
        CE6["openfold3/stock/src/openfold3/tests/test_confidence_metrics.py"] --> N;
    end
```
Sources:
- [openfold3_ob0/stock/src/openfold3/tests/test_diffusion_loss.py:15-30]()
- [openfold3_ob0/stock/src/openfold3/tests/test_validation_metrics.py:22-37]()
- [openfold3_ob0/stock/src/openfold3/tests/test_confidence_metrics.py:19-26]()
- [colabdesign/opt/colabdesign_opt/tests/test_hoist_prev.py:1-7]()
- [protenix_v2/opt/protenix_opt/tests/test_core_adoption.py:52-78]()

## CPU-Only Behavioral Tests

A significant portion of the test suite is designed to run on CPU, focusing on the behavioral aspects of the kits, independent of GPU hardware. These tests verify command-line interface (CLI) parsing, configuration loading, mode resolution, lever application, and reporting mechanisms. They ensure that the non-computational logic of the kits functions as expected across different environments and configurations. This includes testing the `pred --jobs <file>` functionality for multi-job execution and ensuring correct error handling and refusal messages.

```mermaid
graph TD
    subgraph "CPU-Only Behavioral Tests"
        A[CLI Parsing & Argument Validation] --> B{Valid Command?};
        B -- "No" --> C[Refusal: `EXIT_USAGE`];
        B -- "Yes" --> D[Configuration Loading];
        D --> E[Mode Resolution (`modes.resolve`)];
        E --> F[Lever Application (`stack.activate`)];
        F --> G[Reporting & Manifest Generation (`report.py`)];
        G --> H[Test Pass];

        I[Multi-Job Execution (`pred --jobs`)] --> J(Job File Parsing);
        J --> K{Job Valid?};
        K -- "No" --> C;
        K -- "Yes" --> L[Spawn Child Processes];
        L --> G;
    end

    subgraph "Code Entities"
        CE1["flashzoi/opt/flashzoi_opt/tests/test_multi.py"] --> I;
        CE2["af2ig/opt/af2ig_opt/tests/test_cli.py"] --> A;
        CE3["colabfold/opt/colabfold_opt/tests/test_weights_memo.py"] --> D;
    end
```
Sources:
- [flashzoi/opt/flashzoi_opt/tests/test_multi.py:1-4]()
- [af2ig/opt/af2ig_opt/tests/test_cli.py:1-2]()
- [colabfold/opt/colabfold_opt/tests/test_weights_memo.py:1-3]()

## Stock Parity Tests

Stock parity tests are crucial for validating that the optimized kits produce results that are functionally equivalent to their unoptimized, upstream counterparts. These tests typically involve running both the stock and optimized versions of a model on the same inputs and comparing their outputs, losses, or key metrics. The goal is to ensure that performance optimizations do not inadvertently alter the model's behavior or introduce regressions. This often involves comparing digests of weights, verifying that pinned versions of upstream code are maintained, and ensuring that the "off" mode of a kit truly behaves identically to the stock implementation.

Sources:
- [colabfold/opt/colabfold_opt/tests/test_weights_memo.py:63-79]()
- [colabdesign/opt/colabdesign_opt/tests/test_hoist_prev.py:27-34]()
- [af2ig/opt/af2ig_opt/tests/test_cli.py:63-74]()

---

