> 来源: [https://deepwiki.com/deepseek-ai/EPLB/3-api-reference](https://deepwiki.com/deepseek-ai/EPLB/3-api-reference)
> DeepWiki deepseek-ai/EPLB

# API Reference

  Relevant source files 
 - [eplb.py](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py)
 
  This page provides a comprehensive reference for the Expert-Parallelism Load Balancer (EPLB) API, documenting all public functions, their parameters, return values, and usage notes. The EPLB system is designed to optimize expert placement in expert-parallelism machine learning training setups.

 For conceptual information about load balancing strategies, see [Load Balancing Strategies](https://deepwiki.com/deepseek-ai/EPLB/2.1-load-balancing-strategies). For examples of how to use these APIs in practice, see [Usage Examples](https://deepwiki.com/deepseek-ai/EPLB/4-usage-examples).

 
## Function Overview

 
```

```

 Sources: [eplb.py131-164](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L131-L164) [eplb.py74-129](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L74-L129) [eplb.py5-41](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L5-L41) [eplb.py44-71](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L44-L71) [eplb.py98-101](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L98-L101)

 
## Main Entry Point

 
### rebalance_experts

 
```

```

 **Function Signature:** `rebalance_experts(weight, num_replicas, num_groups, num_nodes, num_gpus)`

 **Purpose:**
 The main entry point for the expert-parallelism load balancer. This function determines the optimal placement of experts across GPUs to balance computational load.

 **Parameters:**

 
 - `weight` (torch.Tensor): A tensor of shape `[layers, num_logical_experts]` containing the load statistics for all logical experts.
 - `num_replicas` (int): The number of physical experts after replication. Must be a multiple of `num_gpus`.
 - `num_groups` (int): The number of expert groups.
 - `num_nodes` (int): The number of server nodes, where intra-node communication (e.g., NVLink) is faster.
 - `num_gpus` (int): The number of GPUs. Must be a multiple of `num_nodes`.
 
 **Returns:**

 
 - `physical_to_logical_map` (torch.Tensor): A tensor of shape `[layers, num_replicas]` mapping physical expert indices to logical expert indices.
 - `logical_to_physical_map` (torch.Tensor): A tensor of shape `[layers, num_logical_experts, X]` mapping logical expert indices to physical expert indices.
 - `expert_count` (torch.Tensor): A tensor of shape `[layers, num_logical_experts]` indicating the number of physical replicas for each logical expert.
 
 **Behavior Notes:**

 
 - The function chooses between hierarchical and global load balancing strategies based on whether `num_groups` is divisible by `num_nodes`.
 - When `num_groups % num_nodes == 0`, it uses hierarchical load balancing, which optimizes for node topology.
 - Otherwise, it falls back to global load balancing by treating the entire system as a single node.
 
 Sources: [eplb.py131-164](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L131-L164)

 
## Core Helper Functions

 
### balanced_packing

 
```

```

 **Function Signature:** `balanced_packing(weight, num_packs)`

 **Purpose:**
 Packs `n` weighted objects into `m` packs, ensuring each pack contains exactly `n/m` objects and the weights of all packs are as balanced as possible.

 **Parameters:**

 
 - `weight` (torch.Tensor): A tensor of shape `[X, n]` containing the weight of each item.
 - `num_packs` (int): The number of packs.
 
 **Returns:**

 
 - `pack_index` (torch.Tensor): A tensor of shape `[X, n]` containing the pack index of each item.
 - `rank_in_pack` (torch.Tensor): A tensor of shape `[X, n]` containing the rank of each item within its pack.
 
 **Constraints:**

 
 - `num_groups % num_packs == 0`: The number of groups must be divisible by the number of packs.
 
 **Algorithm:**

 
 - Items are sorted by weight in descending order.
 - Each item is assigned to the pack with the lowest current weight.
 - This greedy approach ensures weights are as balanced as possible across packs.
 
 Sources: [eplb.py5-41](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L5-L41)

 
### replicate_experts

 
```

```

 **Function Signature:** `replicate_experts(weight, num_phy)`

 **Purpose:**
 Replicates `num_log` logical experts to `num_phy` physical replicas, such that the maximum load of all replicas is minimized.

 **Parameters:**

 
 - `weight` (torch.Tensor): A tensor of shape `[X, num_log]` containing the weight of each logical expert.
 - `num_phy` (int): The total number of physical experts after replication.
 
 **Returns:**

 
 - `phy2log` (torch.Tensor): A tensor of shape `[X, num_phy]` mapping physical expert indices to logical expert indices.
 - `rank` (torch.Tensor): A tensor of shape `[X, num_phy]` containing the replica rank for each physical expert.
 - `logcnt` (torch.Tensor): A tensor of shape `[X, num_log]` indicating the number of replicas for each logical expert.
 
 **Constraints:**

 
 - `num_phy >= num_log`: The number of physical experts must be greater than or equal to the number of logical experts.
 
 **Algorithm:**

 
 - Start with one replica per logical expert.
 - Iteratively add replicas to the expert with the highest load per replica.
 - Continue until all `num_phy` replicas are assigned.
 
 Sources: [eplb.py44-71](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L44-L71)

 
### rebalance_experts_hierarchical

 
```

```

 **Function Signature:** `rebalance_experts_hierarchical(weight, num_physical_experts, num_groups, num_nodes, num_gpus)`

 **Purpose:**
 Implements a hierarchical load balancing strategy that optimizes for node topology and minimizes inter-node communication.

 **Parameters:**

 
 - `weight` (torch.Tensor): A tensor of shape `[num_moe_layers, num_logical_experts]` containing the weight of each logical expert.
 - `num_physical_experts` (int): The number of physical experts after replication.
 - `num_groups` (int): The number of expert groups.
 - `num_nodes` (int): The number of server nodes.
 - `num_gpus` (int): The number of GPUs.
 
 **Returns:**

 
 - `physical_to_logical_map` (torch.Tensor): A tensor mapping physical expert indices to logical expert indices.
 - `logical_to_physical_map` (torch.Tensor): A tensor mapping logical expert indices to physical expert indices.
 - `logical_count` (torch.Tensor): A tensor indicating the number of physical replicas for each logical expert.
 
 **Constraints:**

 
 - `num_logical_experts % num_groups == 0`: The number of logical experts must be divisible by the number of groups.
 - `num_groups % num_nodes == 0`: The number of groups must be divisible by the number of nodes.
 - `num_gpus % num_nodes == 0`: The number of GPUs must be divisible by the number of nodes.
 - `num_physical_experts % num_gpus == 0`: The number of physical experts must be divisible by the number of GPUs.
 
 Sources: [eplb.py74-129](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L74-L129)

 
## Data Flow

 
### Hierarchical Load Balancing Flow

 
```

```

 Sources: [eplb.py74-129](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L74-L129)

 
### Mapping Relationships

 
```

```

 Sources: [eplb.py131-164](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L131-L164)

 
## Parameter Constraints

 The following table summarizes the constraints on input parameters for the main API functions:

 
| Function | Parameter Constraints |
|---|---|
| rebalance_experts | • num_replicas must be a multiple of num_gpus• num_gpus must be a multiple of num_nodes |
| rebalance_experts_hierarchical | • num_logical_experts % num_groups == 0• num_groups % num_nodes == 0• num_gpus % num_nodes == 0• num_physical_experts % num_gpus == 0 |
| balanced_packing | • num_groups % num_packs == 0 |
| replicate_experts | • num_phy >= num_log |

 Sources: [eplb.py5-164](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L5-L164)

 
## Return Value Formats

 All functions return tensors with specific shapes and meanings:

 
| Function | Return Values | Shapes | Descriptions |
|---|---|---|---|
| rebalance_experts | physical_to_logical_maplogical_to_physical_mapexpert_count | [layers, num_replicas][layers, num_logical_experts, X][layers, num_logical_experts] | Maps physical experts to logical expertsMaps logical experts to physical expertsNumber of replicas per logical expert |
| balanced_packing | pack_indexrank_in_pack | [X, n][X, n] | Pack index for each itemRank within pack for each item |
| replicate_experts | phy2logranklogcnt | [X, num_phy][X, num_phy][X, num_log] | Logical expert ID for each physical expertReplica rank for each physical expertNumber of replicas for each logical expert |

 Sources: [eplb.py5-164](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L5-L164)
