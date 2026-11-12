<!-- source: DeepWiki mcp.deepwiki.com · repo openucx/ucc · page 5 Collective Algorithms · fetched 2026-11-11 -->

# Collective Algorithms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/coll_patterns/recursive_knomial.h](src/coll_patterns/recursive_knomial.h)
- [src/coll_patterns/sra_knomial.h](src/coll_patterns/sra_knomial.h)
- [src/coll_score/ucc_coll_score_map.c](src/coll_score/ucc_coll_score_map.c)
- [src/components/tl/ucp/allgather/allgather_knomial.c](src/components/tl/ucp/allgather/allgather_knomial.c)
- [src/components/tl/ucp/allreduce/allreduce.c](src/components/tl/ucp/allreduce/allreduce.c)
- [src/components/tl/ucp/allreduce/allreduce.h](src/components/tl/ucp/allreduce/allreduce.h)
- [src/components/tl/ucp/allreduce/allreduce_knomial.c](src/components/tl/ucp/allreduce/allreduce_knomial.c)
- [src/components/tl/ucp/allreduce/allreduce_sra_knomial.c](src/components/tl/ucp/allreduce/allreduce_sra_knomial.c)
- [src/components/tl/ucp/bcast/bcast_sag_knomial.c](src/components/tl/ucp/bcast/bcast_sag_knomial.c)
- [src/components/tl/ucp/reduce_scatter/reduce_scatter_knomial.c](src/components/tl/ucp/reduce_scatter/reduce_scatter_knomial.c)
- [src/components/tl/ucp/scatter/scatter_knomial.c](src/components/tl/ucp/scatter/scatter_knomial.c)
- [src/components/tl/ucp/tl_ucp_service_coll.c](src/components/tl/ucp/tl_ucp_service_coll.c)
- [src/core/ucc_coll.c](src/core/ucc_coll.c)
- [src/utils/ucc_coll_utils.c](src/utils/ucc_coll_utils.c)
- [src/utils/ucc_coll_utils.h](src/utils/ucc_coll_utils.h)
- [test/gtest/utils/test_ep_map.cc](test/gtest/utils/test_ep_map.cc)

</details>



This page provides a detailed overview of the collective algorithms implemented in UCC (Unified Collective Communication) framework. It explains how collective algorithms are selected, their core concepts, and specific implementations for various collective operations. For information about specific collective operation types, see [Collective Operations](#2.3).

## Algorithm Selection Mechanism

UCC uses a scoring mechanism to select the most appropriate algorithm for a given collective operation based on various factors such as message size, memory type, and team topology.

```mermaid
flowchart TD
    A["Application"] --> B["ucc_collective_init()"]
    B --> C["ucc_coll_init()"]
    C --> D["ucc_coll_score_map_lookup()"]
    D --> E{"Select algorithm based on<br>- Message size<br>- Memory type<br>- Team size<br>- Coll type"}
    E -->|"Highest score"| F["Initialize selected algorithm"]
    E -->|"Not supported"| G["Fallback algorithm"]
    F --> H["Return task"]
    G --> H
```

The algorithm selection process works as follows:

1. The application calls `ucc_collective_init()` with the desired collective operation arguments
2. UCC uses the score map to identify the most appropriate algorithm based on:
   - Collective operation type (allreduce, broadcast, allgather, etc.)
   - Message size (different algorithms optimize for different size ranges)
   - Memory type (host, CUDA, ROCM, etc.)
   - Team size and topology

The score map is populated during initialization based on the configuration, and each algorithm registers its preferred operating ranges.

Sources: [src/coll_score/ucc_coll_score_map.c:79-112](), [src/core/ucc_coll.c:169-246]()

## Knomial Algorithms

Knomial algorithms are the foundation for many collective operations in UCC. They extend the concept of binomial algorithms by allowing each node to communicate with up to k nodes (radix) in each step rather than just one.

```mermaid
flowchart TD
    subgraph "Knomial Pattern"
        K0[["Rank 0 (ROOT)"]] --- K1[["Rank 1"]]
        K0 --- K2[["Rank 2"]]
        K0 --- K3[["Rank 3"]]
        K1 --- K4[["Rank 4"]]
        K1 --- K5[["Rank 5"]]
        K1 --- K6[["Rank 6"]]
        K2 --- K7[["Rank 7"]]
        K2 --- K8[["Rank 8"]]
    end
    
    subgraph "Node Types"
        N1[["BASE Node"]] --- N2[["PROXY Node"]]
        N2 --- N3[["EXTRA Node"]]
    end
```

UCC knomial algorithms define three types of nodes:
- **BASE**: Participates in the main loop of the recursive algorithm
- **PROXY**: Participates in the main loop and also communicates with EXTRA nodes
- **EXTRA**: Only communicates with its PROXY node

This organization allows for efficient handling of team sizes that aren't exact powers of the radix.

Sources: [src/coll_patterns/recursive_knomial.h:13-17](), [src/coll_patterns/recursive_knomial.h:84-128]()

### Key Concepts and Parameters:

1. **Radix (k)**: Number of peers a node communicates with in each step
2. **Iteration**: Current step in the recursive algorithm
3. **Node type**: Whether a node is BASE, PROXY, or EXTRA
4. **Block size/offset**: How data is partitioned among ranks

The knomial pattern is implemented with a flexible state machine that allows progress in a non-blocking manner, crucial for high-performance communication.

Sources: [src/coll_patterns/recursive_knomial.h:302-339]()

## Allreduce Algorithms

### Knomial Allreduce

The knomial allreduce algorithm utilizes recursive k-ary communication to efficiently reduce and broadcast data. This algorithm is optimized for latency and is typically selected for small to medium message sizes.

```mermaid
sequenceDiagram
    participant R0 as "Rank 0"
    participant R1 as "Rank 1"
    participant R2 as "Rank 2"
    participant R3 as "Rank 3"
    
    Note over R0,R3: Initial Data: Each rank has local data
    
    R1->>R0: Send data
    R3->>R2: Send data
    
    Note over R0,R1: Reduce R0+R1
    Note over R2,R3: Reduce R2+R3
    
    R2->>R0: Send reduced data
    
    Note over R0: Reduce R0+R2
    
    R0->>R2: Send final result
    R0->>R1: Send final result
    R2->>R3: Send final result
    
    Note over R0,R3: All ranks have complete reduction
```

The operation proceeds as follows:
1. Extra nodes send their data to their proxy nodes
2. Each rank exchanges data with loop peers based on the knomial pattern
3. Reduction operations are performed on received data in each step
4. After all iterations, all ranks have the complete reduced result

Sources: [src/components/tl/ucp/allreduce/allreduce_knomial.c:21-181]()

### SRA Knomial (Scatter-Reduce-Allgather)

SRA Knomial decomposes the allreduce operation into two distinct phases:
1. **Scatter-reduce**: Data is scattered and reduced among ranks
2. **Allgather**: Reduced segments are gathered to all ranks

This algorithm is optimized for bandwidth efficiency and typically selected for larger message sizes.

```mermaid
flowchart TD
    subgraph "SRA Allreduce"
        S["Input data"] --> SR["Scatter-Reduce Phase"]
        SR --> |"Reduced segments"| AG["Allgather Phase"]
        AG --> R["Complete reduction on all ranks"]
    end
    
    subgraph "Data Flow"
        D1["Original Data"] --> |"Split"| D2["Segments"]
        D2 --> |"Reduce"| D3["Reduced Segments"]
        D3 --> |"Gather"| D4["Complete Result"]
    end
```

The SRA algorithm is particularly efficient for large message sizes as it:
- Minimizes data transfer volume
- Distributes reduction work across ranks
- Pipelined execution for better resource utilization

Sources: [src/components/tl/ucp/allreduce/allreduce_sra_knomial.c:40-243]()

## Reduce-Scatter Algorithms

The Reduce-Scatter knomial algorithm performs reduction and scattering in a single operation. Each rank ends up with a portion of the complete reduction.

```mermaid
flowchart LR
    subgraph "Before"
        B1["Rank 0: A0,B0,C0,D0"]
        B2["Rank 1: A1,B1,C1,D1"]
        B3["Rank 2: A2,B2,C2,D2"]
        B4["Rank 3: A3,B3,C3,D3"]
    end
    
    subgraph "After"
        A1["Rank 0: A0+A1+A2+A3"]
        A2["Rank 1: B0+B1+B2+B3"]
        A3["Rank 2: C0+C1+C2+C3"]
        A4["Rank 3: D0+D1+D2+D3"]
    end
```

Key features include:
- Efficient calculation of segment sizes and offsets
- Support for different data distributions and memory types
- Optimized communication pattern based on the knomial structure

Sources: [src/components/tl/ucp/reduce_scatter/reduce_scatter_knomial.c:52-564]()

## Allgather Algorithms

The Allgather knomial algorithm efficiently gathers data from all ranks and distributes it to all participants. It supports both uniform and variable-sized data distributions.

```mermaid
flowchart LR
    subgraph "Before"
        B1["Rank 0: A"]
        B2["Rank 1: B"]
        B3["Rank 2: C"]
        B4["Rank 3: D"]
    end
    
    subgraph "After"
        A1["Rank 0: A,B,C,D"]
        A2["Rank 1: A,B,C,D"]
        A3["Rank 2: A,B,C,D"]
        A4["Rank 3: A,B,C,D"]
    end
```

The algorithm uses:
- Segment-based communication to minimize data transfer
- Efficient handling of non-uniform data distributions (allgatherv)
- Specialized patterns for different memory types

Sources: [src/components/tl/ucp/allgather/allgather_knomial.c:56-324]()

## Broadcast Algorithms

### SAG Knomial (Scatter-Allgather)

The SAG broadcast algorithm decomposes the broadcast operation into two phases:
1. **Scatter**: The root scatters portions of the data to all ranks
2. **Allgather**: All ranks exchange their portions to build the complete data

```mermaid
flowchart TD
    subgraph "SAG Broadcast"
        R["Root with complete data"] --> S["Scatter Phase"]
        S --> |"Scattered segments"| AG["Allgather Phase"]
        AG --> C["All ranks have complete data"]
    end
    
    subgraph "Data Flow Example (4 ranks)"
        D1["Root: ABCD"] --> |"Scatter"| D2["Rank 0: A<br>Rank 1: B<br>Rank 2: C<br>Rank 3: D"]
        D2 --> |"Allgather"| D3["All ranks: ABCD"]
    end
```

This algorithm is particularly effective for:
- Large message broadcasts
- Optimizing bandwidth utilization
- Distributing communication load across the network

Sources: [src/components/tl/ucp/bcast/bcast_sag_knomial.c:39-142]()

## Performance Considerations

Several factors influence algorithm performance and selection:

| Factor | Impact | Optimization |
|--------|--------|--------------|
| Message Size | Small messages favor latency-optimized algorithms<br>Large messages favor bandwidth-optimized algorithms | Use different algorithms based on message size thresholds |
| Memory Type | GPU memory requires different optimizations than host memory | Memory-type specific algorithm selection and tuning |
| Team Size | Some algorithms perform better with specific team sizes | Adjust radix based on team size |
| Network Topology | Network characteristics affect optimal communication patterns | Use topology-aware algorithms when available |
| Radix | Higher radix can reduce steps but increases per-step communication | Tune radix based on network capabilities |

Key tuning options:
- Adjust message size thresholds for algorithm selection
- Configure radix for knomial algorithms
- Enable pipelining for large messages
- Use topology awareness for optimized communication

Sources: [src/components/tl/ucp/allreduce/allreduce_sra_knomial.c:164-193](), [src/components/tl/ucp/allreduce/allreduce.h:23-24]()

## Algorithm Implementation Structure

The collective algorithm implementations in UCC follow a common pattern:

```mermaid
flowchart TD
    subgraph "Collective Algorithm Implementation"
        direction TB
        I["init() - Initialize algorithm"] --> P["post() - Start execution"]
        P --> G["progress() - Non-blocking progress"]
        G --> F["finalize() - Clean up resources"]
    end
    
    subgraph "Implementation Components"
        direction TB
        S1["Specialized data structures"] --> S2["Initialization logic"]
        S2 --> S3["Progress state machine"]
        S3 --> S4["Phase management"]
    end
```

Each algorithm implementation typically consists of:
1. **Initialization function**: Sets up algorithm-specific state
2. **Start function**: Begins algorithm execution
3. **Progress function**: Advances algorithm state, typically using a state machine approach
4. **Finalize function**: Cleans up resources

This structure enables non-blocking progress and efficient resource utilization across the framework.

Sources: [src/components/tl/ucp/allreduce/allreduce_knomial.c:183-269](), [src/components/tl/ucp/reduce_scatter/reduce_scatter_knomial.c:385-422]()

---

