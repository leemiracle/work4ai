> 来源: [https://deepwiki.com/deepseek-ai/LPLB/4-api-reference](https://deepwiki.com/deepseek-ai/LPLB/4-api-reference)
> DeepWiki deepseek-ai/LPLB

# API Reference

  Relevant source files 
 - [lplb/__init__.py](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/__init__.py)
 - [lplb/eplb.py](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/eplb.py)
 - [lplb/planner.py](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py)
 
  This document provides comprehensive reference documentation for the LPLB public API. The API consists of two main components: the `Planner` class for dynamic per-batch load balancing and the `eplb` module for static expert rebalancing.

 For conceptual explanations of how these components work, see [Core Concepts](https://deepwiki.com/deepseek-ai/LPLB/3-core-concepts). For internal implementation details, see [System Architecture](https://deepwiki.com/deepseek-ai/LPLB/5-system-architecture).

 
---

 
## API Surface Overview

 The LPLB library exports a minimal, focused API surface designed for integration into Mixture-of-Experts models.

 
```

```

 **Sources:** [lplb/__init__.py1-4](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/__init__.py#L1-L4) [lplb/planner.py1-267](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L1-L267) [lplb/eplb.py1-191](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/eplb.py#L1-L191)

 
---

 
## Planner Class

 The `Planner` class is the main orchestrator for dynamic load balancing. Users instantiate a `Planner` with topology configuration, then call its methods to perform workload counting, LP optimization, and index mapping.

 
### Constructor

 
```

```

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| redundant_to_original | torch.Tensor | Mapping from redundant experts to original indices. Shape: [group_size, num_redundants]. Encodes the topology (e.g., Cube, Hypercube, Torus). Each entry specifies which rank's expert the redundant expert is copied from. |
| n_routed_experts | int | Total number of physical routed experts across all ranks (including redundants). |
| n_logical_routed_experts | int | Total number of logical routed experts (without redundancy). |
| ep_size | int \| None | Total number of expert parallelism ranks. Defaults to group.size(). Must be provided if group is None. |
| group | torch.distributed.ProcessGroup \| None | Expert parallelism communication group. If None, no workload reduction is performed (single-rank mode). |

 **Initialization Behavior:**

 The constructor performs several calculations to derive internal state:

 
 - Converts `redundant_to_original` to integer CUDA tensor stored as `self.r2o`
 - Computes the inverse mapping `self.o2r` via `argsort()`
 - Derives `group_size` and `num_redundants` from the shape of `r2o`
 - Calculates `n_group` as `ep_size / group_size`
 - Computes per-rank counts: `n_local_routed_experts`, `n_local_logical_routed_experts`
 - Determines `combined_redundant_experts` (number of redundant expert groups per rank)
 - Initializes default `phy2log` mapping via `update_redundancy_mapping()`
 - Creates a cached `CompiledSolver` instance via `_get_solver()`
 
 **Example:**

 
```

```

 **Sources:** [lplb/planner.py38-102](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L38-L102)

 
---

 
### init_from_deep_ep

 
```

```

 Initializes optimized communication using a DeepEP Buffer. This method should be called once if DeepEP integration is desired for faster workload synchronization.

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| buffer | deep_ep.Buffer | DeepEP Buffer instance providing optimized NVLINK/NVSHMEM communication primitives. |

 **Behavior:**

 
 - Sets `self.deep_ep_initialized = True` to enable optimized communication paths
 - Delegates to `self.solver.init_comm()` with configuration from the buffer: 
 - Device: CUDA
 - Use high-latency fallback: `not buffer.low_latency_mode`
 - Disable RDMA: `buffer.num_rdma_bytes == 0`
 
 This method is idempotent; calling it multiple times has no effect after the first call.

 **Example:**

 
```

```

 **Sources:** [lplb/planner.py104-113](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L104-L113)

 
---

 
### update_redundancy_mapping

 
```

```

 Updates the expert redundancy mapping based on historical workload statistics. This method runs EPLB (static load balancing) to reorder experts and create optimal redundancy configurations.

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| workload | torch.Tensor \| None | Historical workload statistics per logical expert. Shape: [n_logical_routed_experts]. If None, uses identity mapping without reordering. |

 **Returns:**

 
| Return Value | Type | Description |
|---|---|---|
| phy2log | torch.Tensor | Physical-to-logical expert mapping. Shape: [n_routed_experts]. Each entry indicates the logical expert ID of the corresponding physical expert. |
| log2phy | torch.Tensor | Logical-to-physical expert mapping. Shape: [n_logical_routed_experts, max_logcnt]. Each row contains the physical expert IDs (replicas) for a logical expert, padded with -1. |
| logcnt | torch.Tensor | Replica count per logical expert. Shape: [n_logical_routed_experts]. Currently always 2 (one original + one redundant). |

 **Algorithm:**

 
 - If `workload` is `None`, creates identity mapping
 - Otherwise, calls `rebalance_experts()` to: 
 - Reorder experts by load
 - Replicate high-load experts
 - Pack experts onto GPUs using balanced bin-packing
 - Sorts experts on each device by descending workload
 - Selects top experts for redundancy creation based on `combined_redundant_experts`
 - Applies topology-based redundancy using `self.r2o`
 - Constructs bidirectional mappings (`phy2log`, `log2phy`)
 - Stores `phy2log` in `self.phy2log` for use by solver
 
 **Example:**

 
```

```

 **Sources:** [lplb/planner.py115-182](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L115-L182)

 
---

 
### count_workload

 
```

```

 Counts the workload for each logical expert using a GPU-accelerated kernel that computes per-SM histograms.

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| idx | torch.Tensor | Logical expert indices selected by the router. Shape: arbitrary. Values in range [-1, n_logical_routed_experts). Value -1 indicates no expert (ignored in counting). |
| n_sms | int | Number of CUDA streaming multiprocessors to use. Typically obtained via torch.cuda.get_device_properties().multi_processor_count. |

 **Returns:**

 
| Return Value | Type | Description |
|---|---|---|
| local_workload | torch.Tensor | Total count per logical expert on this rank. Shape: [n_logical_routed_experts]. |
| local_workload_by_sm | torch.Tensor | Per-SM prefix sum of workload. Shape: [n_sms, n_logical_routed_experts]. Used internally by weighted_select_target(). |

 **Implementation:**

 Delegates to `self.solver.count_idx()` which launches `kernel_count_idx` on the GPU. The kernel uses atomic operations to build histograms in shared memory, then writes results to global memory.

 **Example:**

 
```

```

 **Sources:** [lplb/planner.py184-194](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L184-L194)

 
---

 
### solve_probs

 
```

```

 Solves the linear programming problem to compute optimal load distribution ratios between original and redundant experts.

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| workload | torch.Tensor | Per-expert workload statistics. Shape: [n_group * group_size * n_local_logical_routed_experts] (flattened), or equivalently the total number of logical experts across all ranks. |
| avail_counter | torch.Tensor | Feasible solution counter (for validation). Shape: [1]. Incremented if LP solver finds valid solution. |

 **Returns:**

 
| Return Value | Type | Description |
|---|---|---|
| o_weight | torch.Tensor | Load distribution ratio for redundant experts. Shape: [num_redundants, combined_redundant_experts]. Values sum to 1 across each redundant pair. |

 **Behavior:**

 
 - Reshapes `workload` into `[n_group, group_size, n_local_logical_routed_experts]`
 - If distributed mode (non-`None` `ep_group`) and DeepEP not initialized: 
 - Clones workload and performs `all_reduce()` across ranks
 - Delegates to `self.solver.solve()` which: 
 - Normalizes workload (max = 1)
 - Formulates LP constraints
 - Runs 5-iteration Interior Point Method on GPU
 - Validates convergence
 - Returns distribution ratios or uniform fallback (0.5)
 
 **Example:**

 
```

```

 **Sources:** [lplb/planner.py196-217](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L196-L217)

 
---

 
### weighted_select_target

 
```

```

 Maps logical expert indices to physical expert indices using the computed load distribution ratios. This mapping is deterministic based on per-SM workload prefixes, ensuring consistent load distribution.

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| idx | torch.Tensor | Logical expert indices. Shape: arbitrary. Values in range [-1, n_logical_routed_experts). |
| o_weight | torch.Tensor | Load distribution ratios from solve_probs(). Shape: [num_redundants, combined_redundant_experts]. |
| local_workload_by_sm | torch.Tensor | Per-SM workload prefix sum from count_workload(). Shape: [n_sms, n_logical_routed_experts]. |
| n_sms | int | Number of CUDA streaming multiprocessors. |

 **Returns:**

 
| Return Value | Type | Description |
|---|---|---|
| physical_idx | torch.Tensor | Physical expert indices. Same shape as idx. Values in range [-1, n_routed_experts). Value -1 preserved from input. |

 **Implementation:**

 Delegates to `self.solver.map_idx()` which launches `kernel_map_idx`. The kernel:

 
 - Looks up the logical expert's redundancy status
 - If not redundant, maps directly via `phy2log`
 - If redundant, uses `o_weight` threshold and per-SM prefix to deterministically select original or replica
 - Applies `o2r` inverse mapping to find physical index
 
 **Example:**

 
```

```

 **Sources:** [lplb/planner.py219-243](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L219-L243)

 
---

 
### run

 
```

```

 Main entry point that performs the complete load balancing pipeline: count workload, solve LP, and map indices.

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| idx | torch.Tensor | Logical expert indices from router. Shape: arbitrary. Values in range [-1, n_logical_routed_experts). |
| avail_counter | torch.Tensor | Feasible solution counter. Shape: [1]. |
| n_sms | int \| None | Number of CUDA SMs. If None, auto-detected from current device. |

 **Returns:**

 
| Return Value | Type | Description |
|---|---|---|
| physical_idx | torch.Tensor | Physical expert indices. Same shape as idx. Values in range [-1, n_routed_experts). |

 **Pipeline:**

 
```

```

 **Example:**

 
```

```

 **Sources:** [lplb/planner.py245-266](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L245-L266)

 
---

 
## EPLB Functions

 The `lplb.eplb` module provides static expert rebalancing functions. These are used internally by `Planner.update_redundancy_mapping()` but can also be called directly for offline analysis.

 
### rebalance_experts

 
```

```

 Main entry point for expert-parallelism load balancing. Determines whether to use hierarchical or global balancing policy based on topology.

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| weight | torch.Tensor | Load statistics for all logical experts. Shape: [layers, num_logical_experts]. Typically token counts per expert. |
| num_replicas | int | Total number of physical experts after replication. Must be multiple of num_gpus. |
| num_groups | int | Number of expert groups (for topology partitioning). |
| num_nodes | int | Number of server nodes. Intra-node communication (e.g., NVLink) is faster than inter-node. |
| num_gpus | int | Total number of GPUs. Must be multiple of num_nodes. |

 **Returns:**

 
| Return Value | Type | Description |
|---|---|---|
| physical_to_logical_map | torch.Tensor | Expert index of each replica. Shape: [layers, num_replicas]. |
| logical_to_physical_map | torch.Tensor | Replica indices for each expert. Shape: [layers, num_logical_experts, max_replicas]. Padded with -1. |
| expert_count | torch.Tensor | Number of physical replicas per logical expert. Shape: [layers, num_logical_experts]. |

 **Policy Selection:**

 
 - If `num_groups % num_nodes == 0`: Uses hierarchical load-balance policy (calls `rebalance_experts_hierarchical`)
 - Otherwise: Uses global load-balance policy (calls `rebalance_experts_hierarchical` with `num_groups=1`, `num_nodes=1`)
 
 **Example:**

 
```

```

 **Sources:** [lplb/eplb.py151-190](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/eplb.py#L151-L190)

 
---

 
### rebalance_experts_hierarchical

 
```

```

 Performs hierarchical load balancing with three-stage pipeline: pack groups to nodes, replicate experts within nodes, pack physical experts to GPUs.

 **Parameters:**

 Same as `rebalance_experts()` except:

 
| Parameter | Type | Description |
|---|---|---|
| num_physical_experts | int | Replaces num_replicas for clarity. Same meaning. |

 **Returns:**

 Same as `rebalance_experts()`.

 **Algorithm Pipeline:**

 
```

```

 **Example:**

 
```

```

 **Sources:** [lplb/eplb.py80-148](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/eplb.py#L80-L148)

 
---

 
### replicate_experts

 
```

```

 Replicates experts to minimize maximum load across all replicas. Uses greedy algorithm: repeatedly replicate the highest-loaded expert.

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| weight | torch.Tensor | Expert workload. Shape: [X, num_log] where X is batch dimension (e.g., layers × nodes). |
| num_phy | int | Total number of physical experts after replication. Must be ≥ num_log. |

 **Returns:**

 
| Return Value | Type | Description |
|---|---|---|
| phy2log | torch.Tensor | Logical expert ID of each physical expert. Shape: [X, num_phy]. |
| rank | torch.Tensor | Replica rank (0 for original, 1+ for copies). Shape: [X, num_phy]. |
| logcnt | torch.Tensor | Number of replicas per logical expert. Shape: [X, num_log]. |

 **Algorithm:**

 
 - Initialize first `num_log` physical experts as identity mapping (originals)
 - For each additional physical expert slot: 
 - Find logical expert with maximum `weight / logcnt` ratio
 - Create replica with `rank = logcnt`
 - Increment `logcnt` for that logical expert
 
 **Example:**

 
```

```

 **Sources:** [lplb/eplb.py49-77](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/eplb.py#L49-L77)

 
---

 
### balanced_packing

 
```

```

 Packs weighted items into bins such that each bin contains exactly `n/m` items and total weights are balanced. Uses greedy first-fit-decreasing heuristic.

 **Parameters:**

 
| Parameter | Type | Description |
|---|---|---|
| weight | torch.Tensor | Weight of each item. Shape: [X, n] where X is batch dimension. |
| num_packs | int | Number of packs (bins). Must divide n evenly. |

 **Returns:**

 
| Return Value | Type | Description |
|---|---|---|
| pack_index | torch.Tensor | Pack index of each item. Shape: [X, n]. Values in range [0, num_packs). |
| rank_in_pack | torch.Tensor | Rank of item within its pack. Shape: [X, n]. Values in range [0, n/num_packs). |

 **Algorithm:**

 
 - Sort items by weight (descending)
 - For each item: 
 - Find pack with minimum total weight that has room
 - Assign item to that pack
 - Update pack weight and item count
 
 **Special Case:**

 If `groups_per_pack == 1` (each item goes in its own pack), returns trivial assignment without sorting.

 **Example:**

 
```

```

 **Sources:** [lplb/eplb.py6-46](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/eplb.py#L6-L46)

 
---

 
## Data Flow Through API

 The following diagram illustrates how data flows through the Planner API during a typical load balancing operation:

 
```

```

 **Sources:** [lplb/planner.py245-266](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L245-L266) [lplb/planner.py184-243](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L184-L243)

 
---

 
## Type Reference

 
### Key Data Structures

 
| Type | Shape | Description |
|---|---|---|
| redundant_to_original (r2o) | [group_size, num_redundants] | Topology matrix. Entry [i,j] indicates which rank's expert is copied as redundant j on rank i. |
| original_to_redundant (o2r) | [group_size, num_redundants] | Inverse of r2o via argsort(). Used for reverse lookup during index mapping. |
| phy2log | [n_routed_experts] | Maps each physical expert to its logical expert ID. |
| log2phy | [n_logical_experts, max_replicas] | Maps each logical expert to its physical replica IDs. Padded with -1. |
| logcnt | [n_logical_experts] | Count of physical replicas per logical expert. |
| o_weight | [num_redundants, combined] | Load distribution ratios from LP solver. Values sum to 1 for each redundant pair. |
| local_workload | [n_logical_experts] | Per-expert token count on current rank. |
| local_workload_by_sm | [n_sms, n_logical_experts] | Per-SM prefix sum of workload. Used for deterministic mapping. |

 **Sources:** [lplb/planner.py38-267](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L38-L267)

 
---

 
## Relationship to Internal Components

 The public API delegates to internal components that perform the actual computation:

 
```

```

 For details on the internal implementation, see:

 
 - [C++ Extension and Runtime Compilation](https://deepwiki.com/deepseek-ai/LPLB/5.3-c++-extension-and-runtime-compilation)
 - [CUDA Kernel Implementation](https://deepwiki.com/deepseek-ai/LPLB/5.4-cuda-kernel-implementation)
 - [Linear Programming Solver](https://deepwiki.com/deepseek-ai/LPLB/5.5-linear-programming-solver)
 
 **Sources:** [lplb/planner.py17-35](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L17-L35) [lplb/planner.py95-102](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L95-L102)
