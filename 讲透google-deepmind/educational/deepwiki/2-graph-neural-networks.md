<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/educational · page 2 Graph Neural Networks · fetched 2026-10-26 -->

# Graph Neural Networks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb](colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb)

</details>



## Purpose and Scope

This document provides a comprehensive guide to Graph Neural Networks (GNNs) as implemented in the DeepMind Educational repository. It focuses on the implementation and application of GNNs using the `jraph` library with JAX. The material covers fundamental graph concepts, different graph prediction tasks, and implementations of Graph Convolutional Networks (GCN) and Graph Attention Networks (GAT) with practical applications.

For information about other neural network implementations in the repository, see [Reinforcement Learning](#6) and [Language Models](#3).

## Fundamental Graph Concepts

A graph consists of nodes (vertices) and edges that connect nodes. Formally, a graph is defined as G = (V, E) where V is the set of vertices and E is the set of edges.

Graphs can be either **directed** (edges have a direction) or **undirected** (edges have no direction). For example, a citation network would be represented as a directed graph, while a friendship network would typically be undirected.

Key graph terminology:
- **Degree**: Number of edges incident on a node
- **In-degree**: Sum of incoming edges to a node
- **Out-degree**: Sum of outgoing edges from a node

Graphs can be represented in several ways:
1. **List of edges**: Pairs (u,v) indicating an edge from node u to node v
2. **Adjacency matrix**: A binary square matrix A where A[u,v]=1 if there's a connection between nodes u and v
3. **Adjacency list**: An array of lists where the ith list contains all nodes directly connected to node i

Graph representation diagram:

```mermaid
graph TD
    subgraph "Example Graph"
        N0(("0")) --> N1(("1"))
        N0 --> N3(("3"))
        N1 --> N2(("2"))
        N2 --> N0
        N3 --> N0
    end
    
    subgraph "Representations"
        EdgeList["Edge List: [(0,1), (0,3), (1,2), (2,0), (3,0)]"]
        AdjMatrix["Adjacency Matrix:
        [0 1 0 1]
        [0 0 1 0]
        [1 0 0 0]
        [1 0 0 0]"]
        AdjList["Adjacency List: [{1,3}, {2}, {0}, {0}]"]
    end
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:111-164]()

## Graph Prediction Tasks

GNNs can address three main types of prediction tasks:

1. **Node Classification**: Predicting properties of individual nodes (e.g., paper topics in a citation network)
2. **Link Prediction/Edge Classification**: Predicting whether an edge exists between nodes (e.g., friendships in a social network)
3. **Graph Classification**: Classifying entire graphs (e.g., properties of molecules)

Graph prediction tasks diagram:

```mermaid
graph LR
    subgraph "Graph Prediction Tasks"
        Node["Node Classification"] -.-> NodeEx["Example:<br>Paper Topic Classification"]
        Edge["Link Prediction"] -.-> EdgeEx["Example:<br>Friend Recommendation"]
        Graph["Graph Classification"] -.-> GraphEx["Example:<br>Molecule Property Prediction"]
    end
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:168-186]()

## Introduction to the jraph Library

`jraph` is a lightweight library for working with GNNs in JAX. The main data structure is `GraphsTuple`, which represents graphs and their features.

### GraphsTuple Structure

In `GraphsTuple`, edges are represented by two arrays of node indices: **senders** (source nodes) and **receivers** (destination nodes). Each index in these arrays corresponds to one edge, e.g., edge `i` goes from `senders[i]` to `receivers[i]`.

A `GraphsTuple` contains:
- `nodes`: Node features
- `edges`: Edge features
- `senders`: Indices of sender nodes for each edge
- `receivers`: Indices of receiver nodes for each edge
- `n_node`: Number of nodes per graph
- `n_edge`: Number of edges per graph
- `globals`: Global graph features

GraphsTuple structure diagram:

```mermaid
classDiagram
    class GraphsTuple {
        nodes: jnp.ndarray
        edges: jnp.ndarray
        senders: jnp.ndarray
        receivers: jnp.ndarray
        n_node: jnp.ndarray
        n_edge: jnp.ndarray
        globals: jnp.ndarray
    }
    
    class example_usage {
        graph = jraph.GraphsTuple(
            nodes=node_features,
            edges=edge_features,
            senders=sender_indices,
            receivers=receiver_indices,
            n_node=jnp.array([num_nodes]),
            n_edge=jnp.array([num_edges]),
            globals=global_features
        )
    }
    
    GraphsTuple --> example_usage
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:196-213](), [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:257-266]()

### Creating and Visualizing Graphs

`jraph` provides utilities for creating and manipulating graphs. The example below shows how to create a simple directed graph with 4 nodes and 5 edges:

```mermaid
graph TD
    subgraph "build_toy_graph() Function"
        Init["Create node features<br>Shape: [4, 1]"] --> Edges["Define edges with senders/receivers<br>5 edges total"]
        Edges --> Features["Add edge features<br>Shape: [5, 1]"]
        Features --> Metadata["Set n_node and n_edge<br>metadata"]
        Metadata --> Return["Return GraphsTuple"]
    end
    
    subgraph "Resulting Graph Structure"
        N0(("0")) --> N1(("1"))
        N0 --> N3(("3"))
        N1 --> N2(("2"))
        N2 --> N0
        N3 --> N0
    end
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:222-266](), [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:395-419]()

## Graph Convolutional Network (GCN)

A Graph Convolutional Network applies convolution operations to neighborhoods in a graph structure. Unlike standard CNNs that operate on regular grids, GCNs work on irregular graph structures.

### How GCN Works

GCN consists of two main steps:

1. **Message Computation**: Each node computes a feature vector (using an MLP)
2. **Message Aggregation**: Each node aggregates messages from its neighborhood to update its features

The key difference from CNNs is that GCNs apply the same weights to all neighbors (order-invariant), while CNNs assign different weights to each spatial position.

GCN operation diagram:

```mermaid
graph TD
    subgraph "GCN Layer Operation"
        Node1["Input Node Features"] --> UpdateFn["Update Function<br>(MLP)"]
        UpdateFn --> Messages["Node Messages"]
        Messages --> Aggregation["Neighborhood Aggregation<br>(Sum, Mean, Max)"]
        Aggregation --> Output["Updated Node Features"]
    end
    
    subgraph "Example: Node with 3 Neighbors"
        NodeA["Node A<br>Feature: hA"] --> NodeD["Node D"]
        NodeB["Node B<br>Feature: hB"] --> NodeD
        NodeC["Node C<br>Feature: hC"] --> NodeD
        Function["GCN Update:<br>h'D = f(hA + hB + hC)"]
    end
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:438-464]()

### GCN Implementation Components

A complete GCN implementation includes several key components:

1. **Node Update Function**: Transforms node features (typically an MLP)
2. **Self-Edges**: Optional edges connecting nodes to themselves
3. **Normalization**: Usually symmetric normalization based on node degrees to prevent numerical instabilities

```mermaid
flowchart TB
    Input["Input: GraphsTuple"] --> UpdateNode["1. Update Node Features<br>update_node_fn"]
    UpdateNode --> SelfEdges{"2. Add Self Edges?"}
    SelfEdges -- "Yes" --> AddSelf["Add self-connections"]
    SelfEdges -- "No" --> Normalize{"3. Use Normalization?"}
    AddSelf --> Normalize
    Normalize -- "Yes" --> NormAgg["Compute normalized aggregation<br>D^(-1/2)·A·D^(-1/2)·H"]
    Normalize -- "No" --> SimpleAgg["Simple aggregation"]
    NormAgg --> Output["Output: Updated GraphsTuple"]
    SimpleAgg --> Output
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:754-829]()

### Multi-Layer GCN Models

By stacking multiple GCN layers, nodes can incorporate information from larger neighborhoods (beyond 1-hop neighbors). This is similar to how stacking CNN layers expands the receptive field.

The `GraphConvolution` function in the repository provides a configurable GCN layer implementation with options for:
- Custom node update functions
- Different aggregation methods
- Adding self-edges
- Symmetric normalization

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:878-916]()

## Graph Attention Networks (GAT)

Graph Attention Networks extend GCNs by introducing an attention mechanism that learns to weigh the importance of different neighbor features during aggregation. This addresses a limitation in GCNs where all neighbors contribute equally.

### How GAT Works

In a GAT, each node's update is a weighted sum of its neighbors' features:

h'_i = ∑_(j ∈ N(i)) α_ij · W · h_j

Where:
- α_ij is the attention coefficient between nodes i and j
- W is a weight matrix
- h_j is the feature vector of node j

The attention mechanism computes coefficients through these steps:
1. Transform node features with a learnable weight matrix
2. Compute attention scores using a function of connected nodes' features
3. Normalize scores with softmax to get attention weights
4. Use weights for a weighted sum of neighbor features

GAT mechanism diagram:

```mermaid
flowchart TB
    subgraph "GAT Layer Operation"
        Input["Input: Node Features"] --> Transform["1. Transform Features<br>attention_query_fn"]
        Transform --> AttScore["2. Compute Attention Scores<br>e_ij = attention_logit_fn(h_i, h_j)"]
        AttScore --> Softmax["3. Normalize with Softmax<br>α_ij = softmax(e_ij)"]
        Softmax --> WeightedSum["4. Apply Weighted Sum<br>h'_i = ∑α_ij·W·h_j"]
        WeightedSum --> Output["5. Apply node_update_fn<br>(Optional)"]
    end
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:1281-1335]()

### GAT Implementation in jraph

The GAT implementation in jraph requires:
- `attention_query_fn`: Function to transform node features
- `attention_logit_fn`: Function to compute attention logits 
- `node_update_fn`: Function to update nodes after aggregation
- `add_self_edges`: Whether to add self-connections

The implementation calculates attention weights via softmax and applies them to create weighted node representations.

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:1346-1416](), [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:1436-1449]()

## Practical Applications

The tutorial demonstrates three practical applications of GNNs, each corresponding to a different graph prediction task:

### Node Classification: Zachary's Karate Club

This example uses a small social graph where nodes represent karate club members and edges represent interactions. The task is to predict which instructor each member follows.

```mermaid
flowchart TB
    subgraph "Karate Club Node Classification"
        Data["Dataset:<br>34 nodes (club members)<br>78 edges (interactions)"] --> Model["GNN Model<br>(GCN or GAT)"]
        Model --> Output["Output:<br>Instructor assignment<br>for each member"]
        Constraints["Only 2 nodes<br>(instructors)<br>have known labels"]
    end
    
    subgraph "Performance"
        GCN["GCN: ~91% accuracy"]
        GAT["GAT: ~97% accuracy"]
    end
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:949-1271]()

### Graph Classification: MUTAG Molecules

This example classifies molecular graphs based on their mutagenic effects.

```mermaid
flowchart TB
    subgraph "MUTAG Graph Classification"
        Data["Dataset:<br>188 molecular graphs<br>Node features = atom types<br>Edges = bonds"] --> Embedder["Feature Embedding"]
        Embedder --> GraphNet["Graph Network<br>with node, edge, global updates"]
        GraphNet --> Output["Binary Classification:<br>Mutagenic or Not"]
        Performance["Test accuracy: ~76%"]
    end
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:1603-2017]()

### Link Prediction: CORA Citation Network

This example predicts whether a citation exists between pairs of scientific papers.

```mermaid
flowchart TB
    subgraph "CORA Link Prediction"
        Data["Dataset:<br>2708 papers<br>Citation links<br>Bag-of-words features"] --> Split["Split edges into<br>train/val/test"]
        Split --> GNN["Graph Network<br>for Node Embedding"]
        GNN --> Decoder["Dot Product Decoder<br>score(i,j) = h_i · h_j"]
        Decoder --> Output["Predicted probability<br>of citation between papers"]
        Performance["ROC-AUC: ~84%"]
    end
```

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:2022-2488]()

## Graph Adversarial Attacks

The tutorial briefly introduces graph adversarial attacks, where small, carefully crafted perturbations to the graph structure or node features can fool GNN models.

Special challenges for graph adversarial attacks include:
1. **Discrete nature of graphs**: Unlike continuous pixel values, graph structure is discrete
2. **Node interdependence**: Perturbing one node can affect predictions for others
3. **Defining "imperceptibility"**: It's harder to define what makes a graph perturbation imperceptible

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:2496-2571]()

## Implementation Architecture

The following diagram shows the key components and their relationships in the jraph implementation:

```mermaid
classDiagram
    class jraph {
        GraphsTuple
        GraphNetwork
        GraphMapFeatures
        GraphConvolution
        GAT
        pad_with_graphs()
        segment_softmax()
    }
    
    class GraphsTuple {
        nodes
        edges
        senders
        receivers
        n_node
        n_edge
        globals
    }
    
    class GraphConvolution {
        update_node_fn
        aggregate_nodes_fn
        add_self_edges
        symmetric_normalization
    }
    
    class GAT {
        attention_query_fn
        attention_logit_fn
        node_update_fn
        add_self_edges
    }
    
    class GraphNetwork {
        update_node_fn
        update_edge_fn
        update_global_fn
    }
    
    jraph --> GraphsTuple
    jraph --> GraphConvolution
    jraph --> GAT
    jraph --> GraphNetwork
    GraphConvolution ..> GraphsTuple : operates on
    GAT ..> GraphsTuple : operates on
    GraphNetwork ..> GraphsTuple : operates on
```

## Summary

This document covered Graph Neural Networks as implemented in the DeepMind Educational repository using the jraph library with JAX. Key topics included:

- Fundamental graph concepts and representations
- Different types of graph prediction tasks
- GNN architectures: Graph Convolutional Networks and Graph Attention Networks
- Practical applications across node classification, graph classification, and link prediction
- Implementation details using the jraph library

The tutorial demonstrates how to build and train models for various graph-based tasks using real-world datasets.

Sources: [colabs/summer_schools/intro_to_graph_nets_tutorial_with_jraph.ipynb:2578-2586]()

---

