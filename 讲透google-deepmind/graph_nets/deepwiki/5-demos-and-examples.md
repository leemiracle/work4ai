<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/graph_nets · page 5 Demos and Examples · fetched 2026-10-26 -->

# Demos and Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [graph_nets/demos/graph_nets_basics.ipynb](graph_nets/demos/graph_nets_basics.ipynb)

</details>



This document provides an overview of the demonstration applications included in the Graph Nets library. These demos showcase the library's capabilities across different problem domains while illustrating how the same graph network architecture can be applied to various tasks.

## Overview

The Graph Nets library includes several demos that demonstrate how to create, manipulate, and train graph networks to reason about graph-structured data. These demos serve both as educational resources and as examples of practical applications of graph neural networks.

```mermaid
flowchart LR
    subgraph "Demos Available"
        ShortestPath["Shortest Path Demo"]
        Sort["Sort Demo"]
        Physics["Physics Demo"]
        Basics["Graph Nets Basics Demo"]
    end
    
    subgraph "Common Architecture"
        Input["Input Graph"] --> Encoder["Encoder<br>(GraphIndependent)"]
        Encoder --> Core["Core<br>(GraphNetwork)"]
        Core -->|"Hidden State"| Core
        Core --> Decoder["Decoder<br>(GraphIndependent)"]
        Decoder --> Output["Output Graph"]
    end
    
    ShortestPath -.- Architecture
    Sort -.- Architecture
    Physics -.- Architecture
    
    classDef nocolor fill:white,stroke:#333,stroke-width:1px;
    class Input,Encoder,Core,Decoder,Output,ShortestPath,Sort,Physics,Basics,Architecture nocolor;
```

Sources: [README.md:79-85]()

## Common Architecture: Encode-Process-Decode

All three task-based demos (shortest path, sort, physics) use the same graph network architecture, which highlights the flexibility of the approach. This architecture follows an Encode-Process-Decode pattern:

```mermaid
flowchart LR
    Input["Input Graph"] --> Encoder["Encoder<br>(GraphIndependent)"]
    Encoder --> Core["Core<br>(GraphNetwork)"]
    Core -->|"Hidden State"| Core
    Core --> Decoder["Decoder<br>(GraphIndependent)"]
    Decoder --> Output["Output Graph"]
    
    classDef nocolor fill:white,stroke:#333,stroke-width:1px;
    class Input,Encoder,Core,Decoder,Output nocolor;
```

1. **Encoder**: The input graph is first processed by a `GraphIndependent` module, which transforms node, edge, and global features independently without message passing.

2. **Core**: The encoded graph is then processed through multiple iterations by a `GraphNetwork` module, which performs message passing to update node, edge, and global features based on the graph structure.

3. **Decoder**: Finally, the processed graph is passed through another `GraphIndependent` module to produce the output graph.

This architecture allows the model to iteratively refine its representations through the core message-passing steps before producing the final output.

Sources: [README.md:83-85]()

## Shortest Path Demo

The shortest path demo trains a graph network to label the nodes and edges that form the shortest path between any two nodes in a graph.

```mermaid
flowchart LR
    subgraph "Shortest Path Problem"
        direction TB
        G["Input Graph"] -- "Encode-Process-Decode" --> P["Predicted Path"]
        
        subgraph "Example Visualization"
            direction TB
            I1[("Initial Step")] --- I2[("Intermediate Step")] --- I3[("Final Prediction")]
        end
    end
    
    classDef nocolor fill:white,stroke:#333,stroke-width:1px;
    class G,P,I1,I2,I3 nocolor;
```

Features:
- Creates random graphs for training
- Over multiple message-passing steps, the model refines its prediction of the shortest path
- Visualizes how the prediction evolves at each step

The demo illustrates how graph networks can learn to solve classic graph algorithms through neural message passing.

Sources: [README.md:95-102]()

## Sort Demo

The sort demo trains a graph network to sort a list of random numbers. The model learns to determine the correct order of elements in a sequence.

```mermaid
flowchart LR
    subgraph "Sort Problem"
        direction TB
        L["List as Graph"] -- "Encode-Process-Decode" --> S["Sorted List"]
        
        subgraph "Representation"
            direction TB
            N1["Node 1<br>Value: 3"] --- N2["Node 2<br>Value: 1"] --- N3["Node 3<br>Value: 4"]
            N4["Node 4<br>Value: 2"] --- N3
            N4 --- N1
        end
    end
    
    classDef nocolor fill:white,stroke:#333,stroke-width:1px;
    class L,S,N1,N2,N3,N4 nocolor;
```

Features:
- Represents lists as fully-connected graphs where each node contains a value
- After multiple message-passing steps, the model predicts which elements come next after each other
- The output is visualized as a matrix showing the predicted ordering relationships

This demo shows how graph networks can learn to reason about relational properties in data that isn't naturally graph-structured.

Sources: [README.md:106-113]()

## Physics Demo

The physics demo trains a graph network to predict the state of a mass-spring physical system in the next timestep.

```mermaid
flowchart LR
    subgraph "Physics Simulation"
        direction TB
        S0["State t"] -- "Encode-Process-Decode" --> S1["State t+1"]
        
        subgraph "Mass-Spring System"
            direction TB
            M1[("Mass 1")] <--> |"Spring"| M2[("Mass 2")]
            M2 <--> |"Spring"| M3[("Mass 3")]
            M3 <--> |"Spring"| M4[("Mass 4")]
            M4 <--> |"Spring"| M1
        end
    end
    
    classDef nocolor fill:white,stroke:#333,stroke-width:1px;
    class S0,S1,M1,M2,M3,M4 nocolor;
```

Features:
- Creates random mass-spring physical systems for training
- Learns to predict the next state of the system given the current state
- The model's predictions can be fed back as input to create a rollout of future trajectories
- Visualizes true and predicted system states over multiple steps

This demo is similar to the "interaction networks" model described in Battaglia et al. (2016) and demonstrates how graph networks can model physical systems and their dynamics.

Sources: [README.md:117-126]()

## Graph Nets Basics Demo

Unlike the task-specific demos, the Graph Nets Basics demo is a tutorial that introduces fundamental concepts of the library.

```mermaid
flowchart TD
    subgraph "Tutorial Topics"
        direction LR
        T1["Creating<br>GraphsTuple"] --> T2["Graph<br>Operations"]
        T2 --> T3["Using Graph<br>Networks"]
        T3 --> T4["Custom<br>Modules"]
    end
    
    subgraph "Code Examples"
        direction TB
        C1["utils_np.data_dicts_to_graphs_tuple()"]
        C2["utils_tf.data_dicts_to_graphs_tuple()"]
        C3["modules.GraphNetwork()"]
        C4["blocks.EdgeBlock, NodeBlock, GlobalBlock"]
    end
    
    T1 --- C1
    T1 --- C2
    T3 --- C3
    T4 --- C4
    
    classDef nocolor fill:white,stroke:#333,stroke-width:1px;
    class T1,T2,T3,T4,C1,C2,C3,C4 nocolor;
```

This tutorial contains step-by-step examples covering:
1. How to create and manipulate graphs
2. How to feed graphs into graph networks
3. How to build custom graph network modules

The tutorial serves as a comprehensive introduction to the Graph Nets library and its core concepts.

Sources: [README.md:130-134](), [graph_nets/demos/graph_nets_basics.ipynb:40-47]()

## Running the Demos

### In Browser with Colaboratory

The easiest way to try the demos is through Google Colaboratory, which allows you to run the notebooks in your browser without installing anything locally.

| Demo | Colaboratory Link |
|------|-------------------|
| Shortest Path | [Run in browser](https://colab.research.google.com/github/deepmind/graph_nets/blob/master/graph_nets/demos/shortest_path.ipynb) |
| Sort | [Run in browser](https://colab.research.google.com/github/deepmind/graph_nets/blob/master/graph_nets/demos/sort.ipynb) (or [TF2 version](https://colab.research.google.com/github/deepmind/graph_nets/blob/master/graph_nets/demos_tf2/sort.ipynb)) |
| Physics | [Run in browser](https://colab.research.google.com/github/deepmind/graph_nets/blob/master/graph_nets/demos/physics.ipynb) |
| Graph Nets Basics | [Run in browser](https://colab.research.google.com/github/deepmind/graph_nets/blob/master/graph_nets/demos/graph_nets_basics.ipynb) (or [TF2 version](https://colab.research.google.com/github/deepmind/graph_nets/blob/master/graph_nets/demos_tf2/graph_nets_basics.ipynb)) |

To run a demo in Colaboratory:
1. Click on the corresponding link
2. Follow the instructions in the notebook

Sources: [README.md:87-135]()

### On Local Machine

To run the demos locally:

1. Install the necessary dependencies:
```
pip install jupyter matplotlib scipy
```

2. Navigate to the demos directory:
```
cd <path-to-graph-nets-library>/demos
```

3. Launch Jupyter Notebook:
```
jupyter notebook
```

4. Open a demo through the Jupyter notebook interface.

Sources: [README.md:138-151]()

## Demo Implementation Details

For those interested in the internal workings of the demos, each follows a similar implementation pattern:

```mermaid
flowchart TD
    subgraph "Demo Implementation Structure"
        direction TB
        D1["Data Generation"] --> D2["Model Definition"]
        D2 --> D3["Training Loop"]
        D3 --> D4["Evaluation"]
        D4 --> D5["Visualization"]
    end
    
    subgraph "GraphNetwork Components Used"
        direction TB
        G1["modules.GraphIndependent<br>(Encoder)"]
        G2["modules.GraphNetwork<br>(Core)"]
        G3["modules.GraphIndependent<br>(Decoder)"]
    end
    
    D2 --- G1
    D2 --- G2
    D2 --- G3
    
    classDef nocolor fill:white,stroke:#333,stroke-width:1px;
    class D1,D2,D3,D4,D5,G1,G2,G3 nocolor;
```

Each demo uses `modules.GraphIndependent` for the encoder and decoder, and `modules.GraphNetwork` for the core processing steps. The demos showcase how to:

1. Structure graph data for different types of problems
2. Define appropriate network architectures
3. Train models on graph-structured data
4. Visualize and interpret the results

For detailed information about the Encode-Process-Decode architecture used in these demos, see the [EncodeProcessDecode Architecture](#6.1) page.

Sources: [README.md:82-85]()

---

