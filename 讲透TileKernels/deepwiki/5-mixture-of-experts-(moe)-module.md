> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/5-mixture-of-experts-%28moe%29-module](https://deepwiki.com/deepseek-ai/TileKernels/5-mixture-of-experts-%28moe%29-module)
> DeepWiki deepseek-ai/TileKernels

# Mixture of Experts (MoE) Module

  Relevant source files 
 - [tile_kernels/moe/__init__.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/__init__.py)
 - [tile_kernels/moe/common.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/common.py)
 - [tile_kernels/moe/scoring.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/scoring.py)
 
  The Mixture of Experts (MoE) module provides a suite of high-performance TileLang kernels designed to handle the sparse routing and dispatch logic required for MoE transformer architectures. This subsystem manages the entire lifecycle of a token through an MoE layer: from initial expert selection (routing) and load-balancing loss calculation to the physical movement of data (dispatch/expand) and final result aggregation (reduction).

 The module is optimized for large-scale models, supporting features like group-based routing, tensor-parallel masking, and fused scaling during data movement.

 
### System Architecture Overview

 The MoE pipeline is divided into three primary stages, as illustrated in the diagram below:

 
#### MoE Pipeline Logic

 
```

```

 **Sources:** [tile_kernels/moe/__init__.py1-11](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/__init__.py#L1-L11) [tile_kernels/moe/common.py4-53](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/common.py#L4-L53)

 
---

 
### Routing and Selection

 The routing subsystem determines which experts should process which tokens. It supports complex selection logic, including **Top-K** and **Grouped Top-K** selection.

 
 - **Scoring Functions**: The module supports multiple activation functions for expert gates via the `ScoringFunc` enum, including `SIGMOID`, `SQRTSOFTPLUS`, `SOFTMAX`, and `IDENTITY` [tile_kernels/moe/scoring.py5-9](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/scoring.py#L5-L9)
 - **Grouped Selection**: For architectures that organize experts into groups, the `get_topk_group_idx` macro implements a stable-sort selection of groups based on the sum of their top-performing experts [tile_kernels/moe/common.py4-53](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/common.py#L4-L53)
 - **Mapping Construction**: Once experts are selected, `get_fused_mapping_kernel` builds the index structures required to scatter tokens into contiguous expert buffers.
 
 For details on the routing kernels and scoring logic, see [MoE Routing Kernels](https://deepwiki.com/deepseek-ai/TileKernels/5.1-moe-routing-kernels).

 **Sources:** [tile_kernels/moe/scoring.py5-27](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/scoring.py#L5-L27) [tile_kernels/moe/common.py4-53](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/common.py#L4-L53)

 
---

 
### Dispatch and Reduction

 Once the routing mapping is established, the module handles the high-bandwidth data movement between the global token buffer and expert-specific buffers.

 
 - **Expand (Dispatch)**: The `expand_to_fused_kernel` scatters tokens to their assigned experts. It supports an optional `expand_to_fused_with_sf` variant which applies scaling factors during the copy to facilitate quantized expert execution [tile_kernels/moe/__init__.py3](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/__init__.py#L3-L3)
 - **Reduce (Aggregation)**: After expert computation, the `reduce_fused_kernel` gathers the results and performs a weighted sum (based on gate scores) to produce the final token representation [tile_kernels/moe/__init__.py2](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/__init__.py#L2-L2)
 
 For details on data movement and weight normalization, see [MoE Dispatch and Reduction Kernels](https://deepwiki.com/deepseek-ai/TileKernels/5.2-moe-dispatch-and-reduction-kernels).

 **Sources:** [tile_kernels/moe/__init__.py2-3](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/__init__.py#L2-L3)

 
---

 
### Load Balancing and Parallelism

 To ensure efficient utilization of hardware, the MoE module includes utilities for load balancing and multi-GPU coordination:

 
 - **Auxiliary Loss**: The `aux_fi_kernel` calculates load-balancing metrics (auxiliary loss) to prevent expert collapse during training [tile_kernels/moe/__init__.py5](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/__init__.py#L5-L5)
 - **Tensor Parallelism**: The `mask_indices_by_tp_kernel` allows the MoE layer to mask out expert indices that do not reside on the local rank in a Tensor Parallel (TP) configuration [tile_kernels/moe/__init__.py7](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/__init__.py#L7-L7)
 - **Group Counting**: `group_count_kernel` and `inplace_unique_group_indices_kernel` are used to calculate the dynamic workload per expert, which is critical for managing variable-length expert buffers [tile_kernels/moe/__init__.py4-6](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/__init__.py#L4-L6)
 
 
#### Code Entity Mapping

 The following diagram maps high-level MoE operations to the specific TileLang kernel implementations.

 
```

```

 **Sources:** [tile_kernels/moe/__init__.py1-11](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/__init__.py#L1-L11) [tile_kernels/moe/scoring.py5-9](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/scoring.py#L5-L9) [tile_kernels/moe/common.py4-53](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/common.py#L4-L53)

 
---

 
### Child Pages

 
 - **[MoE Routing Kernels](https://deepwiki.com/deepseek-ai/TileKernels/5.1-moe-routing-kernels)**: Detailed reference for the routing pipeline kernels, including `topk_gate`, `get_fused_mapping`, and auxiliary load-balancing loss calculation.
 - **[MoE Dispatch and Reduction Kernels](https://deepwiki.com/deepseek-ai/TileKernels/5.2-moe-dispatch-and-reduction-kernels)**: Documentation for the high-performance data movement kernels: `expand_to_fused` (scatter), `reduce_fused` (gather/sum), and `normalize_weight`.
