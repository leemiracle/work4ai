> 来源: [https://deepwiki.com/deepseek-ai/DeepEP/8-testing-and-validation](https://deepwiki.com/deepseek-ai/DeepEP/8-testing-and-validation)
> DeepWiki deepseek-ai/DeepEP

# Testing and Validation

  Relevant source files 
 - [tests/elastic/test_agrs.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_agrs.py)
 - [tests/elastic/test_engram.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_engram.py)
 - [tests/elastic/test_ep.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_ep.py)
 
  This page provides an overview of the DeepEP test suite. With the release of DeepEP V2, the testing infrastructure has been expanded to include a new suite for the `ElasticBuffer` (V2) while maintaining the legacy suite for the original `Buffer` (V1).

 The test suite is organized into functional areas: expert parallelism (EP), remote memory access (Engram), pipeline parallelism (PP), and all-gather reduce-scatter (AGRS).

 
---

 
## Test Suite Structure

 The codebase contains two distinct test directories reflecting the architectural evolution of the library.

 
| Directory | Target Version | Primary Interface | Key Files |
|---|---|---|---|
| tests/elastic/ | V2 | ElasticBuffer | test_ep.py, test_engram.py, test_pp.py, test_agrs.py, test_barrier.py |
| tests/legacy/ | V1 | Buffer | test_intranode.py, test_internode.py, test_low_latency.py |

 Distributed tests are typically launched across multiple GPUs using `torch.multiprocessing.spawn` for local testing [tests/elastic/test_engram.py124](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_engram.py#L124-L124) or via cluster orchestrators. Users should modify the `init_dist` function in `deep_ep/utils/envs.py` to match their specific cluster orchestration (e.g., SLURM, MPI, or manual).

 
---

 
## Distributed Orchestration and Utilities

 DeepEP provides a set of shared utilities in `deep_ep/utils/` to simplify distributed initialization, reference calculations, and performance measurement.

 
### Environment and Process Group

 The `deep_ep.utils.envs` module handles the lifecycle of the distributed environment.

 
 - **`init_dist`**: Initializes the process group, sets the local device, and handles rank/world size discovery [tests/elastic/test_engram.py15](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_engram.py#L15-L15)
 - **`dist_print`**: A utility for synchronized printing across ranks to prevent interleaved output [tests/elastic/test_engram.py26](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_engram.py#L26-L26)
 - **`init_seed`**: Ensures reproducible test data generation across ranks [tests/elastic/test_ep.py14](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_ep.py#L14-L14)
 
 
### Reference Implementations

 Correctness is validated against Python-based reference implementations in `deep_ep.utils.refs`. These functions simulate the expected behavior of the CUDA kernels for dispatch and combine operations.

 
 - **`ref_dispatch`**: Provides the ground truth for MoE token routing [tests/elastic/test_ep.py111](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_ep.py#L111-L111)
 - **`ref_combine`**: Provides the ground truth for token accumulation, including support for reduced combine recipes [tests/elastic/test_ep.py129-140](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_ep.py#L129-L140)
 
 
### Benchmarking Primitives

 DeepEP includes specialized benchmarking tools in `deep_ep.utils.testing`:

 
 - **`bench`**: Uses CUDA events to measure average, min, and max latency over multiple iterations.
 - **`bench_kineto`**: Integrates with the PyTorch Kineto profiler to extract fine-grained kernel durations (e.g., `engram_fetch_impl`, `engram_fetch_wait_impl`) and optionally export Chrome traces [tests/elastic/test_engram.py84-89](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_engram.py#L84-L89)
 - **`flush_l2_cache`**: Ensures cold-cache performance measurements by clearing the L2 cache between iterations [tests/elastic/test_agrs.py71](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_agrs.py#L71-L71)
 
 
### Logic and Gate Helpers

 
 - **`deep_ep.utils.gate`**: Provides `get_unbalanced_scores` to simulate MoE routing decisions with varying unbalanced ratios for stress testing [tests/elastic/test_ep.py75](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_ep.py#L75-L75)
 - **`deep_ep.utils.math`**: Provides `per_token_cast_to_fp8` and `per_token_cast_back` for validating FP8 quantization logic [tests/elastic/test_ep.py8-12](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_ep.py#L8-L12)
 
 
---

 
## Code Entity to System Mapping

 The following diagram maps the high-level testing concepts to the specific code entities used to orchestrate and validate the system.

 
```

```

 Sources: [tests/elastic/test_agrs.py9-26](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_agrs.py#L9-L26) [tests/elastic/test_engram.py7-9](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_engram.py#L7-L9) [tests/elastic/test_ep.py8-18](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_ep.py#L8-L18)

 
---

 
## Test Execution Flow

 V2 tests often involve complex session lifecycles, especially for AGRS and Engram features. The following diagram illustrates a typical stress test flow for All-Gather Reduce-Scatter.

 
```

```

 Sources: [tests/elastic/test_agrs.py121-135](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_agrs.py#L121-L135) [tests/elastic/test_engram.py53-68](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_engram.py#L53-L68)

 
---

 
## Detailed Test Suites

 For in-depth documentation of the specific test cases and their parameters, see the following child pages:

 
### [Elastic Test Suite (V2)](https://deepwiki.com/deepseek-ai/DeepEP/8.1-elastic-test-suite-(v2))

 Covers the modern `ElasticBuffer` interface.

 
 - **`test_ep.py`**: Exhaustive correctness and performance of V2 dispatch/combine, including FP8 round-trips, handle caching, and compute stream overlapping [tests/elastic/test_ep.py85-90](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_ep.py#L85-L90)
 - **`test_engram.py`**: Validates remote KV cache fetch (Engram) correctness by comparing against `all_gather` references and measures MPPS (Million Points Per Second) [tests/elastic/test_engram.py59-96](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_engram.py#L59-L96)
 - **`test_pp.py`**: Stress tests for the experimental Pipeline Parallelism send/recv API.
 - **`test_agrs.py`**: Validates All-Gather and Reduce-Scatter sessions, batched operations, and in-place memory usage under randomized stress conditions [tests/elastic/test_agrs.py113-140](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_agrs.py#L113-L140)
 - **`test_barrier.py`**: Profiles the latency of the symmetric memory barrier.
 
 
### [Legacy Test Suite (V1)](https://deepwiki.com/deepseek-ai/DeepEP/8.2-legacy-test-suite-(v1))

 Covers the archived `Buffer` interface for users maintaining NVSHMEM-based workflows.

 
 - **`test_intranode.py`**: Validates NVLink-only kernels and configuration tuning.
 - **`test_internode.py`**: Validates multi-node RDMA+NVLink kernels.
 - **`test_low_latency.py`**: Validates pure-RDMA low-latency kernels and specialized FP8/LogFMT formats.
 
 Sources: [tests/elastic/test_agrs.py1-140](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_agrs.py#L1-L140) [tests/elastic/test_engram.py1-101](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_engram.py#L1-L101) [tests/elastic/test_ep.py59-150](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/tests/elastic/test_ep.py#L59-L150)
