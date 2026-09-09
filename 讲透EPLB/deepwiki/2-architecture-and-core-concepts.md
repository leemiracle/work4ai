> 来源: [https://deepwiki.com/deepseek-ai/EPLB/2-architecture-and-core-concepts](https://deepwiki.com/deepseek-ai/EPLB/2-architecture-and-core-concepts)
> DeepWiki deepseek-ai/EPLB

# Architecture and Core Concepts

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/README.md?plain=1)
 - [eplb.py](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py)
 
  This page provides a comprehensive overview of the Expert Parallelism Load Balancer (EPLB) architecture and explains the core concepts involved in solving the challenge of load balancing in expert-parallel machine learning systems. For specific details about different load balancing strategies, see [Load Balancing Strategies](https://deepwiki.com/deepseek-ai/EPLB/2.1-load-balancing-strategies). For information about the expert replication algorithm, see [Expert Replication Algorithm](https://deepwiki.com/deepseek-ai/EPLB/2.2-expert-replication-algorithm).

 
## Problem Statement

 When training large neural networks with Mixture of Experts (MoE) layers using expert parallelism, different experts are assigned to different GPUs. This distribution creates a fundamental challenge: the computational load of different experts varies significantly depending on the current input data, leading to load imbalance across GPUs.

 
```

```

 Sources: [eplb.py131-163](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L131-L163) [README.md3-8](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/README.md?plain=1#L3-L8)

 
## EPLB Solution Overview

 The Expert Parallelism Load Balancer tackles this challenge through a two-pronged approach:

 
 - **Expert Replication**: Duplicating heavily-loaded experts to distribute their workload
 - **Strategic Placement**: Packing experts onto GPUs to balance computational load
 
 Additionally, when possible, EPLB places experts from the same group on the same physical node to minimize inter-node communication overhead.

 
```

```

 Sources: [eplb.py131-163](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L131-L163) [README.md10-14](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/README.md?plain=1#L10-L14)

 
## System Architecture

 The EPLB system architecture consists of several interconnected components that work together to achieve balanced expert placement. The main components include:

 
```

```

 Sources: [eplb.py131-163](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L131-L163) [eplb.py74-129](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L74-L129)

 
### Main Components

 
 - **Strategy Selector**: Determines whether to use hierarchical or global load balancing based on system configuration.
 - **Balanced Packing Algorithm**: Distributes weighted objects across containers to minimize load imbalance.
 - **Expert Replication Algorithm**: Determines optimal duplication of experts to minimize maximum load per replica.
 - **Mapping Generators**: Creates the mapping from physical experts to logical experts and vice versa.
 
 
## Core Data Structures

 The EPLB system operates on several key data structures that represent the expert weights, their placement, and their replication count:

 
| Data Structure | Description | Shape |
|---|---|---|
| weight | Load statistics for each logical expert | [num_layers, num_logical_experts] |
| physical_to_logical_map | Maps each physical expert to its logical expert | [num_layers, num_replicas] |
| logical_to_physical_map | Maps each logical expert to its physical expert replicas | [num_layers, num_logical_experts, max_replicas] |
| expert_count | Number of replicas for each logical expert | [num_layers, num_logical_experts] |

 Sources: [eplb.py131-147](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L131-L147)

 
## Hierarchical Load Balancing Process

 When the number of expert groups is divisible by the number of nodes (`num_groups % num_nodes == 0`), EPLB uses a hierarchical approach that follows a three-step process:

 
```

```

 Sources: [eplb.py74-129](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L74-L129) [README.md19-25](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/README.md?plain=1#L19-L25)

 
## Global Load Balancing Process

 When the hierarchical approach is not suitable (`num_groups % num_nodes != 0`), EPLB uses a global load balancing policy that treats the system as having a single node and a single expert group, focusing solely on load balancing across all GPUs.

 
```

```

 Sources: [eplb.py154-156](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L154-L156) [README.md27-31](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/README.md?plain=1#L27-L31)

 
## Algorithm Details

 
### Expert Replication

 The expert replication algorithm iteratively assigns additional replicas to the experts with the highest load per replica:

 
```

```

 Sources: [eplb.py44-71](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L44-L71)

 
### Balanced Packing

 The balanced packing algorithm ensures that weighted objects are distributed evenly across packs:

 
```

```

 Sources: [eplb.py5-41](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L5-L41)

 
## Execution Flow

 The complete execution flow of the EPLB system demonstrates how all components interact:

 
```

```

 Sources: [eplb.py131-163](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L131-L163) [eplb.py74-129](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L74-L129) [eplb.py5-71](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L5-L71)

 
## System Configuration Parameters

 The EPLB system's behavior is controlled by several key configuration parameters:

 
| Parameter | Description |
|---|---|
| weight | Load statistics for each logical expert across layers |
| num_replicas | Total number of physical experts after replication (must be a multiple of num_gpus) |
| num_groups | Number of expert groups in the model |
| num_nodes | Number of server nodes in the system |
| num_gpus | Total number of GPUs (must be a multiple of num_nodes) |

 Sources: [eplb.py131-147](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/eplb.py#L131-L147)

 
## Benefits and Trade-offs

 
### Benefits

 
 - Improves training performance by balancing GPU utilization
 - Minimizes inter-node communication through strategic expert placement
 - Adapts to different hardware configurations through flexible strategy selection
 
 
### Trade-offs

 
 - Introduces computational overhead for calculating optimal placements
 - Requires accurate load statistics for optimal performance
 - May increase memory usage due to expert replication
 
 Sources: [README.md3-14](https://github.com/deepseek-ai/EPLB/blob/d52c72d5/README.md?plain=1#L3-L14)

 
## Summary

 The EPLB architecture provides an efficient solution to the load balancing challenge in expert-parallel machine learning systems. By employing a combination of expert replication and strategic placement, and adapting its strategy based on system configuration, EPLB achieves balanced GPU utilization and improved training performance.

 For more detailed information about the specific load balancing strategies, see [Load Balancing Strategies](https://deepwiki.com/deepseek-ai/EPLB/2.1-load-balancing-strategies). For an in-depth explanation of the expert replication algorithm, see [Expert Replication Algorithm](https://deepwiki.com/deepseek-ai/EPLB/2.2-expert-replication-algorithm). For information about the balanced packing algorithm, see [Balanced Packing Algorithm](https://deepwiki.com/deepseek-ai/EPLB/2.3-balanced-packing-algorithm).
