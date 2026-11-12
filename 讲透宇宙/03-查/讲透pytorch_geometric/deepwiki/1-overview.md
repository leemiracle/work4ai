<!-- source: DeepWiki mcp.deepwiki.com · repo pyg-team/pytorch_geometric · page 1 Overview · fetched 2026-10-21 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)
- [.github/actions/setup/action.yml](.github/actions/setup/action.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [CITATION.cff](CITATION.cff)
- [README.md](README.md)
- [docker/Dockerfile.xpu](docker/Dockerfile.xpu)
- [docs/requirements.txt](docs/requirements.txt)
- [docs/source/conf.py](docs/source/conf.py)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/install/installation.rst](docs/source/install/installation.rst)
- [docs/source/install/quick-start.html](docs/source/install/quick-start.html)
- [docs/source/modules/datasets.rst](docs/source/modules/datasets.rst)
- [docs/source/modules/nn.rst](docs/source/modules/nn.rst)
- [docs/source/notes/colabs.rst](docs/source/notes/colabs.rst)
- [docs/source/notes/installation.rst](docs/source/notes/installation.rst)
- [docs/source/notes/resources.rst](docs/source/notes/resources.rst)
- [pyproject.toml](pyproject.toml)
- [readthedocs.yml](readthedocs.yml)
- [torch_geometric/__init__.py](torch_geometric/__init__.py)
- [torch_geometric/datasets/__init__.py](torch_geometric/datasets/__init__.py)
- [torch_geometric/nn/__init__.py](torch_geometric/nn/__init__.py)
- [torch_geometric/typing.py](torch_geometric/typing.py)

</details>



PyTorch Geometric (PyG) is a geometric deep learning library built on PyTorch for creating, training, and deploying Graph Neural Networks (GNNs) and related models for structured data. This page provides a high-level introduction to PyG's architecture, design philosophy, and core components. For installation instructions, see [Installation and Setup](#1.1). For detailed architectural concepts, see [Architecture and Key Concepts](#1.2).

## Purpose and Scope

PyG addresses the challenge of applying deep learning to non-Euclidean data structures including graphs, point clouds, and meshes. The library provides:

- **158+ built-in datasets** spanning molecular, social, citation, and geometric domains.
- **50+ GNN layer implementations** via the `MessagePassing` abstraction.
- **Pre-built models** for molecular property prediction, node/edge/graph classification, and link prediction.
- **Scalable data loaders** for full-batch and mini-batch training on graphs with millions of nodes.
- **Flexible type system** supporting optional high-performance extensions.

The library targets researchers implementing new GNN architectures, practitioners applying GNNs to real-world problems, and anyone working with graph-structured data in PyTorch.

**Sources**: [README.md:23-57](), [pyproject.toml:5-32](), [torch_geometric/datasets/__init__.py:1-212]()

## Library Architecture

PyG follows a four-layer architecture that separates concerns between low-level computation, data management, neural network operations, and high-level models:

### Four-Layer System Architecture

```mermaid
graph TB
    subgraph "Layer 1: User Interface"
        Datasets["torch_geometric.datasets<br/>158+ datasets<br/>QM9, Planetoid, OGB"]
        Loaders["torch_geometric.loader<br/>NeighborLoader<br/>LinkNeighborLoader"]
        Models["torch_geometric.nn.models<br/>SchNet, DimeNet<br/>GCN, GAT, Node2Vec"]
    end
    
    subgraph "Layer 2: Core Abstraction"
        Data["torch_geometric.data<br/>Data, HeteroData<br/>Batch"]
        MessagePassing["torch_geometric.nn.conv.MessagePassing<br/>Inspector"]
        Conv["GNN Layers<br/>GCNConv, GATConv<br/>SAGEConv, GINConv"]
        Aggr["torch_geometric.nn.aggr<br/>Aggregation operators"]
    end
    
    subgraph "Layer 3: Infrastructure"
        TypeSystem["torch_geometric.typing<br/>Feature flags<br/>WITH_PYG_LIB, etc"]
        CustomTensors["Custom Tensors<br/>EdgeIndex, Index<br/>HashTensor"]
        Storage["torch_geometric.data.storage<br/>FeatureStore<br/>GraphStore"]
    end
    
    subgraph "Layer 4: Extensions"
        LLM["torch_geometric.llm<br/>G-Retriever, GLEM<br/>RAG pipelines"]
        Explain["torch_geometric.explain<br/>GNNExplainer"]
        Profile["torch_geometric.profile<br/>Performance analysis"]
    end
    
    Datasets --> Data
    Loaders --> Data
    Data --> Storage
    
    Models --> Conv
    Conv --> MessagePassing
    MessagePassing --> Aggr
    MessagePassing --> CustomTensors
    
    CustomTensors --> TypeSystem
    
    LLM --> Models
    Explain --> Models
```

**Layer 1 (User Interface)**: High-level entry points including dataset classes in [torch_geometric/datasets/\_\_init\_\_.py:1-248](), data loaders, and ready-to-use model implementations. Users typically interact with PyG at this layer.

**Layer 2 (Core Abstraction)**: The `Data` and `HeteroData` classes for representing graphs, the `MessagePassing` base class that implements the message passing paradigm, and 50+ convolutional layers in [docs/source/modules/nn.rst:16-29]().

**Layer 3 (Infrastructure)**: Custom tensor types (`EdgeIndex`, `Index`, `HashTensor`) that extend PyTorch tensors with graph-specific metadata, the type system in [torch_geometric/typing.py:12-26]() for managing optional dependencies, and pluggable storage backends.

**Layer 4 (Extensions)**: Cutting-edge features including LLM integration in [CHANGELOG.md:64-64](), explainability methods, and profiling tools.

**Sources**: [README.md:148-161](), [torch_geometric/nn/__init__.py:1-33](), [torch_geometric/datasets/__init__.py:121-248](), [torch_geometric/typing.py:1-113]()

## Data Processing Pipeline

The following diagram illustrates how data flows from raw sources through PyG's processing pipeline to trained models:

```mermaid
flowchart LR
    subgraph Input["Data Sources"]
        RawData["Raw Datasets<br/>torch_geometric.datasets.*<br/>Planetoid, QM9"]
        CustomData["Custom Graphs<br/>Data(x, edge_index)<br/>User-defined"]
    end
    
    subgraph Processing["Dataset Processing"]
        InMemory["InMemoryDataset<br/>process()<br/>All data in RAM"]
        OnDisk["Dataset<br/>Base class<br/>Streaming data"]
        Transform["Transforms<br/>NormalizeFeatures<br/>ToUndirected"]
    end
    
    subgraph Loading["Data Loading"]
        FullBatch["Direct access<br/>dataset[0]"]
        MiniBatch["DataLoader<br/>NeighborLoader<br/>LinkNeighborLoader"]
    end
    
    subgraph Structure["Data Structures"]
        DataObj["Data object<br/>x: node features<br/>edge_index: COO format"]
        BatchObj["Batch object<br/>Collated graphs<br/>batch index"]
    end
    
    subgraph Training["Model Training"]
        GNNModel["GNN Model<br/>MessagePassing layers<br/>forward(x, edge_index)"]
    end
    
    RawData --> InMemory
    RawData --> OnDisk
    CustomData --> DataObj
    
    InMemory --> Transform
    OnDisk --> Transform
    Transform --> DataObj
    
    DataObj --> FullBatch
    DataObj --> MiniBatch
    
    FullBatch --> DataObj
    MiniBatch --> BatchObj
    
    DataObj --> GNNModel
    BatchObj --> GNNModel
```

**Data Sources**: PyG provides 158+ datasets organized by domain: homogeneous graphs (social networks, citations), heterogeneous graphs (recommendation systems), hypergraphs, and synthetic datasets. See [torch_geometric/datasets/\_\_init\_\_.py:121-245]() for the complete list.

**Dataset Processing**: The `InMemoryDataset` class loads all data into memory, while the base `Dataset` class allows for streaming from disk. Both support `pre_transform` and `pre_filter` functions applied during the processing lifecycle.

**Data Loading**: Small graphs use direct indexing. Large graphs use `NeighborLoader` for neighbor sampling or `LinkNeighborLoader` for link prediction tasks, both producing mini-batches via the `Batch` collation mechanism.

**Data Structures**: `Data` objects store node features in `x`, graph connectivity in `edge_index` (COO format), and optional attributes. `Batch` objects combine multiple graphs by concatenating features and adjusting indices with a `batch` vector.

**Sources**: [README.md:58-113](), [torch_geometric/datasets/__init__.py:1-249](), [docs/source/index.rst:35-47]()

## MessagePassing Framework

The `MessagePassing` class is PyG's core abstraction for implementing GNN layers. All 50+ convolutional layers inherit from this base class:

```mermaid
graph TB
    subgraph "MessagePassing Lifecycle"
        Forward["forward(x, edge_index)<br/>User-defined entry point"]
        Propagate["propagate(edge_index, **kwargs)<br/>Orchestrates message passing"]
        Message["message(**kwargs)<br/>Compute messages for edges"]
        Aggregate["aggregate(inputs, index)<br/>Aggregate messages to nodes"]
        Update["update(aggr_out)<br/>Update node features"]
    end
    
    subgraph "Inspector System"
        Inspector["Inspector class<br/>Introspects method signatures"]
        Jinja["Jinja2 templates<br/>Code generation"]
    end
    
    subgraph "Core Implementations"
        GCNConv["GCNConv<br/>torch_geometric.nn.conv.GCNConv"]
        GATConv["GATConv<br/>torch_geometric.nn.conv.GATConv"]
        SAGEConv["SAGEConv<br/>torch_geometric.nn.conv.SAGEConv"]
    end
    
    Forward --> Propagate
    Propagate --> Message
    Message --> Aggregate
    Aggregate --> Update
    
    Propagate --> Inspector
    Inspector --> Jinja
    
    MessagePassing["MessagePassing base class<br/>torch_geometric.nn.conv.MessagePassing"] --> GCNConv
    MessagePassing --> GATConv
    MessagePassing --> SAGEConv
```

**Core Methods**: 
- `propagate()`: Main entry point that orchestrates the message passing flow.
- `message()`: Computes messages for each edge, accessing source (`_j`) and target (`_i`) node features.
- `aggregate()`: Combines messages arriving at each node (sum, mean, max, etc.) via [Aggregation System](#4.3) operators.
- `update()`: Final transformation of aggregated messages.

**Inspector and Code Generation**: The `Inspector` class uses Python introspection to automatically collect method arguments and generate optimized code via Jinja2 templates. This enables JIT compilation while maintaining a flexible Python interface.

**Concrete Implementations**: `GCNConv` implements graph convolutional networks, `GATConv` adds attention mechanisms, and `SAGEConv` provides GraphSAGE sampling-based aggregation.

**Sources**: [README.md:114-147](), [docs/source/modules/nn.rst:30-44](), [pyproject.toml:36-36]()

## Domain Applications and Models

PyG serves diverse research domains through specialized datasets and models:

| Domain | Datasets | Pre-built Models | Key Features |
|--------|----------|------------------|--------------|
| **Molecular ML** | `QM9`, `ZINC`, `MoleculeNet` | `SchNet`, `DimeNet`, `ProteinMPNN` | 3D coordinates, atomic numbers |
| **Social Networks** | `Reddit`, `Flickr`, `Facebook` | `Node2Vec`, `GraphSAGE` | Large-scale graphs, scalable loaders |
| **Citations** | `Planetoid` (Cora/Citeseer), `CoraFull` | `GCN`, `GAT`, `GATv2` | Node classification, homophily |
| **Knowledge Graphs** | `FB15k_237`, `WordNet18` | `RGCNConv`, `HGTConv` | Heterogeneous graphs, link prediction |
| **Point Clouds** | `ModelNet`, `ShapeNet`, `FAUST` | `PointNetConv`, `EdgeConv` | 3D geometric data, k-NN graphs |
| **Recommendations** | `MovieLens`, `AmazonBook` | `LightGCN`, `ARLinkPredictor` | Bipartite graphs, user-item interactions |

**Molecular Property Prediction**: Models like `SchNet` and `DimeNet` are designed for quantum chemistry, while `ProteinMPNN` targets structural biology.

**LLM Integration**: The `torch_geometric.llm` module provides tools for combining GNNs with Large Language Models, including RAG pipelines and models like `GRetriever`.

**Sources**: [torch_geometric/datasets/__init__.py:1-212](), [CHANGELOG.md:28-92](), [pyproject.toml:61-75]()

## Core Components Summary

### Data Structures
- **`Data`**: Homogeneous graphs with `x` (node features), `edge_index` (connectivity), and `y` (labels).
- **`HeteroData`**: Heterogeneous graphs with multiple node and edge types.
- **`Batch`**: Collated mini-batches with a `batch` index vector.
- **`EdgeIndex`**: Specialized tensor for graph connectivity with caching for CSR/CSC formats.

For details, see [Data Structures](#2).

### Neural Network Modules
- **`MessagePassing`**: Base class for all GNN layers implementing the message passing paradigm.
- **50+ Convolutional Layers**: `GCNConv`, `GATConv`, `SAGEConv`, `GINConv`, etc.
- **Aggregation Operators**: [Aggregation System](#4.3) base class for sum, mean, max, softmax, etc.
- **Pre-built Models**: `SchNet`, `Node2Vec`, `DeepGraphInfomax`, `TGN`.

For details, see [Message Passing Framework](#4) and [GNN Layers](#5).

### Data Loading
- **`Dataset`**: Abstract base class for datasets with `download()` and `process()` methods.
- **`DataLoader`**: PyTorch-compatible loader with graph-specific collation.
- **`NeighborLoader`**: Mini-batch sampling for large-scale graphs.

For details, see [Datasets](#3) and [Data Loading and Sampling](#3.3).

### Utilities and Extensions
- **Type System**: `torch_geometric.typing` with feature flags for `pyg-lib`, `torch-scatter`, etc.
- **Explainability**: `torch_geometric.explain` for interpreting GNN predictions.
- **Distributed**: Support for multi-GPU and multi-node training.

For details, see [Utilities](#8) and [Advanced Features](#7).

**Sources**: [torch_geometric/__init__.py:1-59](), [torch_geometric/typing.py:1-113](), [README.md:162-251]()

## Version and Compatibility

PyG 2.9.0 (latest) supports:
- **PyTorch**: 1.13 through 2.12+ (including support for `torch.compile`).
- **Python**: 3.10 through 3.14.
- **Optional Extensions**: `pyg-lib` (replaces `torch-cluster` and `torch-spline-conv`), `torch-scatter`, `torch-sparse`.
- **Device Support**: CPU, CUDA, MPS (Apple), XPU (Intel).

**Sources**: [CHANGELOG.md:30-48](), [torch_geometric/typing.py:12-26](), [torch_geometric/__init__.py:34-68]()

---

