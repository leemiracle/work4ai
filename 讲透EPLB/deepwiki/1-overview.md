<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/EPLB · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [eplb.py](eplb.py)

</details>



The Expert-Parallelism Load Balancer (EPLB) is a specialized system designed to optimize the distribution of experts in machine learning models that employ expert parallelism, specifically for Mixture of Experts (MoE) architectures. EPLB addresses the critical challenge of load imbalance that occurs when different experts experience varying computational demands across GPUs, which can significantly reduce training efficiency.

For detailed information about implementation strategies, see [Architecture and Core Concepts](#2) and [Load Balancing Strategies](#2.1).

Sources: [README.md:1-5](), [eplb.py:131-147]()

## The Problem of Expert Parallelism

When using expert parallelism, different experts are assigned to different GPUs to enable parallel processing. However, the workload of these experts can vary significantly depending on the tokens being processed, leading to a situation where some GPUs are heavily loaded while others remain underutilized. This imbalance reduces the overall efficiency of the training process.

### System Context Diagram

```mermaid
flowchart LR
    A["Neural Network with MoE Layers"] --> B["Expert Parallelism"]
    B --> C["Load Imbalance Challenge"]
    C -->|"Solved by"| D["EPLB System"]
    D --> E["Optimized Expert Placement"]
    E --> F["Balanced GPU Utilization"]
    F --> G["Improved Training Performance"]
```

Sources: [README.md:3-5]()

## EPLB Solution Approach

EPLB implements a "redundant experts" strategy that:

1. Analyzes the load statistics of each expert
2. Duplicates heavily-loaded experts to create multiple replicas
3. Optimally places these replicas across available GPUs
4. Ensures balanced load distribution while considering network topology

The system provides two main load balancing strategies:

| Strategy | When Used | Key Characteristics |
|----------|-----------|---------------------|
| Hierarchical Load Balancing | When `num_groups % num_nodes == 0` | Optimizes for both load balance and network communication; Useful for prefilling stage |
| Global Load Balancing | When `num_groups % num_nodes != 0` | Focuses solely on global load balance; Used in decoding stage with larger expert-parallel size |

Sources: [README.md:5-9](), [README.md:17-32](), [eplb.py:150-156]()

## Core Components and Workflow

The main entry point to the system is the `rebalance_experts` function, which orchestrates the load balancing process. It is supported by two key algorithms:

1. `balanced_packing`: A greedy algorithm that packs weighted objects into bins to achieve balanced weight distribution
2. `replicate_experts`: An algorithm that determines how many replicas to create for each expert to minimize the maximum load

### Control Flow Diagram

```mermaid
flowchart TD
    A["Input: Expert Load Statistics"] --> B["rebalance_experts"]
    Z1["num_replicas"] --> B
    Z2["num_groups"] --> B
    Z3["num_nodes"] --> B
    Z4["num_gpus"] --> B
    
    B --> C{"num_groups % num_nodes == 0?"}
    C -->|"Yes"| D["rebalance_experts_hierarchical"]
    C -->|"No"| E["Global Load Balancing"]
    
    D --> F["balanced_packing"]
    D --> G["replicate_experts"]
    E --> F
    E --> G
    
    F --> H["Expert Placement Plan"]
    G --> H
    
    H --> I["physical_to_logical_map"]
    H --> J["logical_to_physical_map"]
    H --> K["expert_count"]
```

Sources: [eplb.py:5-41](), [eplb.py:44-71](), [eplb.py:131-162]()

### Hierarchical Load Balancing Workflow

```mermaid
flowchart TD
    A["Expert Load Statistics"] --> B["rebalance_experts_hierarchical"]
    
    subgraph Step1PackGroups["Step 1: Pack Groups to Nodes"]
        B --> C["Calculate tokens_per_group"]
        C --> D["balanced_packing"]
        D --> E["Create log2mlog/mlog2log mappings"]
    end
    
    subgraph Step2ReplicateExperts["Step 2: Replicate Experts Within Nodes"]
        E --> F["Calculate tokens_per_mlog"]
        F --> G["replicate_experts"]
        G --> H["Create phy2mlog/phyrank/mlogcnt"]
    end
    
    subgraph Step3PackPhysicalExperts["Step 3: Pack Physical Experts to GPUs"]
        H --> I["Calculate tokens_per_phy"]
        I --> J["balanced_packing"]
        J --> K["Create phy2pphy/pphy2phy mappings"]
    end
    
    K --> L["Final Result: physical_to_logical_map"]
    K --> M["Final Result: logical_to_physical_map"]
    K --> N["Final Result: expert_count"]
```

Sources: [eplb.py:74-129]()

### Expert Replication Process

```mermaid
flowchart LR
    A["Start with 1 replica per expert"] --> B["Calculate load per replica"]
    B --> C{"All replicas assigned?"}
    C -->|"No"| D["Select expert with highest load per replica"]
    D --> E["Assign new replica to this expert"]
    E --> F["Update load calculations"]
    F --> B
    C -->|"Yes"| G["Return mapping tensors"]
```

Sources: [eplb.py:44-71]()

### Balanced Packing Algorithm

```mermaid
flowchart TD
    A["Input: weighted objects"] --> B["Sort by weight in descending order"]
    B --> C["Initialize empty packs"]
    C --> D{"All objects assigned?"}
    D -->|"No"| E["Select pack with lowest current weight"]
    E --> F["Assign next object to selected pack"]
    F --> G["Update pack weight"]
    G --> D
    D -->|"Yes"| H["Return pack assignments"]
```

Sources: [eplb.py:5-41]()

## Integration and Usage

EPLB integrates into existing training pipelines through the `rebalance_experts` function [eplb.py:131-162](). This function serves as the primary interface for the system and takes the following parameters:

- `weight`: Load statistics tensor for all logical experts [layers, num_logical_experts]
- `num_replicas`: Number of physical experts (must be a multiple of `num_gpus`)
- `num_groups`: Number of expert groups
- `num_nodes`: Number of server nodes
- `num_gpus`: Number of GPUs (must be a multiple of `num_nodes`)

It returns three tensors:
- `physical_to_logical_map`: Maps physical experts to logical experts
- `logical_to_physical_map`: Maps logical experts to physical experts
- `expert_count`: Number of replicas for each logical expert

For comprehensive API documentation, see [API Reference](#3) and [rebalance_experts Function](#3.1).

Sources: [eplb.py:131-162](), [README.md:33-57]()

## Hierarchical vs. Global Load Balancing Strategies

```mermaid
flowchart LR
    A["Load Balancing Strategies"] --> B["Hierarchical Strategy"]
    A --> C["Global Strategy"]
    
    B --> D["Optimizes for node topology"]
    B --> E["Minimizes inter-node communication"]
    B --> F["Used when num_groups % num_nodes == 0"]
    
    C --> G["Simpler implementation"]
    C --> H["Focus solely on load balancing"]
    C --> I["Used when num_groups % num_nodes != 0"]
```

Sources: [README.md:17-32](), [eplb.py:150-156]()

## Key Benefits

- **Improved Training Efficiency**: Balanced load distribution across GPUs reduces idle time and maximizes hardware utilization
- **Network Topology Awareness**: The hierarchical strategy reduces inter-node communication by keeping related experts on the same node when possible
- **Flexibility**: Supports different parallel configurations and adapts to various hardware setups
- **Simple Integration**: Straightforward interface that integrates into existing training frameworks

Sources: [README.md:1-9]()

---

