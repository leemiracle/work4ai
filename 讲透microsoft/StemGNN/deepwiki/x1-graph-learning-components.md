<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/StemGNN · extra page Graph Learning Components · fetched 2026-10-26 -->

# Graph Learning Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [models/base_model.py](models/base_model.py)

</details>



## Purpose and Scope

This document explains the graph learning components in the STemGNN architecture, specifically the mechanisms that automatically discover relationships between nodes (time series) in multivariate time-series data. These components transform raw temporal data into a learned graph structure that captures latent correlations.

This page covers:
- Temporal feature extraction using GRU
- Self-attention mechanism for learning node relationships
- Graph Laplacian computation
- Chebyshev polynomial approximation for multi-order graph convolutions

For information about how these learned graph structures are used in the spectral processing pipeline, see [StockBlockLayer](#4.3.2). For the overall neural network architecture, see [Neural Network Architecture](#4.3).

---

## Overview

The graph learning components in STemGNN address a fundamental challenge: given multiple time series without predefined relationships, how can the model automatically discover which series influence each other? Rather than requiring a pre-specified graph structure, STemGNN learns the graph directly from data using self-attention.

The process follows this pipeline:

```mermaid
graph LR
    A["Input Time Series<br/>batch × nodes × time_step"] --> B["GRU<br/>Temporal Feature Extraction"]
    B --> C["self_graph_attention()<br/>Compute Attention Matrix"]
    C --> D["latent_correlation_layer()<br/>Symmetrize & Normalize"]
    D --> E["get_laplacian()<br/>Graph Laplacian"]
    E --> F["cheb_polynomial()<br/>Multi-order Approximation"]
    F --> G["mul_L<br/>K × N × N<br/>Used in StockBlockLayer"]
    D --> H["attention<br/>N × N<br/>Learned Graph Structure"]
```

**Sources:** [models/base_model.py:78-180]()

---

## Component Architecture

### Model Initialization

The `Model` class initializes learnable parameters for the graph learning process:

| Parameter | Shape | Purpose |
|-----------|-------|---------|
| `weight_key` | `(unit, 1)` | Learnable weight for computing attention keys |
| `weight_query` | `(unit, 1)` | Learnable weight for computing attention queries |
| `GRU` | `(time_step, unit)` | Temporal feature extractor |

**Sources:** [models/base_model.py:88-92]()

---

## Temporal Feature Extraction

Before computing relationships between nodes, the model extracts temporal features using a GRU layer. This transforms raw time series values into learned representations that capture temporal patterns.

```mermaid
graph TB
    subgraph Input
        X["x<br/>batch × nodes × time_step"]
    end
    
    subgraph GRU["GRU Layer (self.GRU)"]
        P["Permute: (2,0,1)<br/>time_step × batch × nodes"]
        G["GRU Forward Pass<br/>Extract temporal patterns"]
        P2["Permute: (1,0,2)<br/>batch × nodes × unit"]
    end
    
    subgraph Output
        F["input<br/>batch × nodes × unit<br/>Temporal features"]
    end
    
    X --> P
    P --> G
    G --> P2
    P2 --> F
```

The GRU processes each time step sequentially, producing a `unit`-dimensional feature vector for each node. These features encode temporal dynamics and serve as input to the attention mechanism.

**Sources:** [models/base_model.py:137-138]()

---

## Self-Attention Mechanism

The self-attention mechanism learns which nodes have strong relationships by computing pairwise attention scores.

### Computation Flow

```mermaid
graph TB
    subgraph Input
        IN["input<br/>batch × nodes × unit"]
    end
    
    subgraph Transform["Linear Transformations"]
        K["key = input × weight_key<br/>batch × nodes × 1"]
        Q["query = input × weight_query<br/>batch × nodes × 1"]
    end
    
    subgraph Combine["Pairwise Combination"]
        R1["key.repeat(1,1,N)<br/>Broadcast keys"]
        R2["query.repeat(1,N,1)<br/>Broadcast queries"]
        ADD["key_broadcast + query_broadcast<br/>batch × (N×N) × 1"]
        RESHAPE["Reshape to batch × N × N"]
    end
    
    subgraph Activation
        LR["LeakyReLU<br/>Non-linear activation"]
        SM["Softmax(dim=2)<br/>Normalize per row"]
        DR["Dropout<br/>Regularization"]
    end
    
    subgraph Output
        ATT["attention<br/>batch × N × N<br/>Attention matrix"]
    end
    
    IN --> Transform
    K --> R1
    Q --> R2
    R1 --> ADD
    R2 --> ADD
    ADD --> RESHAPE
    RESHAPE --> LR
    LR --> SM
    SM --> DR
    DR --> ATT
```

### Implementation Details

The attention score between node `i` and node `j` is computed as:

```
attention[i,j] = softmax(LeakyReLU(key[i] + query[j]))
```

This creates a weighted adjacency matrix where high values indicate strong learned relationships.

| Step | Operation | Code Reference |
|------|-----------|----------------|
| 1. Permute input | `input.permute(0, 2, 1)` | [models/base_model.py:152]() |
| 2. Compute keys | `torch.matmul(input, self.weight_key)` | [models/base_model.py:154]() |
| 3. Compute queries | `torch.matmul(input, self.weight_query)` | [models/base_model.py:155]() |
| 4. Broadcast and combine | `key.repeat(...) + query.repeat(...)` | [models/base_model.py:156]() |
| 5. Apply activation | `self.leakyrelu(data)` | [models/base_model.py:159]() |
| 6. Normalize | `F.softmax(data, dim=2)` | [models/base_model.py:160]() |
| 7. Regularize | `self.dropout(attention)` | [models/base_model.py:161]() |

**Sources:** [models/base_model.py:151-162]()

---

## Graph Laplacian Computation

The attention matrix is converted into a graph Laplacian, a fundamental representation in graph signal processing that enables spectral graph convolutions.

### Laplacian Construction Pipeline

```mermaid
graph TB
    subgraph AttentionProcessing["latent_correlation_layer()"]
        A1["Compute self_graph_attention()<br/>batch × N × N"]
        A2["Average over batch<br/>torch.mean(attention, dim=0)<br/>N × N"]
        A3["Symmetrize<br/>0.5 × (attention + attention.T)<br/>Ensure undirected graph"]
    end
    
    subgraph DegreeComputation
        D1["Compute degree<br/>degree = torch.sum(attention, dim=1)<br/>N-dimensional vector"]
        D2["Degree matrix<br/>degree_l = torch.diag(degree)<br/>N × N diagonal matrix"]
    end
    
    subgraph Normalization
        N1["Inverse sqrt diagonal<br/>D^(-1/2) = diag(1/sqrt(degree))<br/>N × N"]
        N2["Normalized Laplacian<br/>L = D^(-1/2) × (D - A) × D^(-1/2)<br/>N × N"]
    end
    
    subgraph Output
        LAP["laplacian<br/>N × N<br/>Normalized graph Laplacian"]
    end
    
    A1 --> A2
    A2 --> A3
    A3 --> D1
    D1 --> D2
    D1 --> N1
    D2 --> N2
    A3 --> N2
    N1 --> N2
    N2 --> LAP
```

### Normalized vs Unnormalized Laplacian

The `get_laplacian` method supports both normalized and unnormalized Laplacians:

| Type | Formula | When to Use |
|------|---------|-------------|
| **Normalized** | `L = I - D^(-1/2) × A × D^(-1/2)` | Default; better for graphs with varying node degrees |
| **Unnormalized** | `L = D - A` | Simpler but sensitive to degree distribution |

Where:
- `A` is the adjacency (attention) matrix
- `D` is the diagonal degree matrix
- `I` is the identity matrix

**Implementation:**

```
if normalize:
    D = torch.diag(torch.sum(graph, dim=-1) ** (-1/2))
    L = I - D × graph × D
else:
    D = torch.diag(torch.sum(graph, dim=-1))
    L = D - graph
```

**Sources:** [models/base_model.py:106-119](), [models/base_model.py:136-149]()

---

## Chebyshev Polynomial Approximation

Graph convolutions require computing functions of the Laplacian matrix. Direct computation is expensive, so STemGNN uses Chebyshev polynomial approximation to efficiently approximate multi-hop graph operations.

### Mathematical Background

Chebyshev polynomials provide a recursive approximation:
- `T_0(L) = 0` (identity, no propagation)
- `T_1(L) = L` (1-hop neighbors)
- `T_2(L) = 2L × T_1(L) - T_0(L)` (2-hop neighbors)
- `T_3(L) = 2L × T_2(L) - T_1(L)` (3-hop neighbors)

### Implementation

```mermaid
graph TB
    subgraph Input
        L["laplacian<br/>N × N"]
    end
    
    subgraph Initialization
        L_exp["Expand dims<br/>1 × N × N"]
        T0["first_laplacian = zeros<br/>1 × N × N<br/>Order 0"]
        T1["second_laplacian = L<br/>1 × N × N<br/>Order 1"]
    end
    
    subgraph Recursion
        T2["third_laplacian<br/>= 2×L×T1 - T0<br/>Order 2"]
        T3["forth_laplacian<br/>= 2×L×T2 - T1<br/>Order 3"]
    end
    
    subgraph Output
        CAT["torch.cat([T0, T1, T2, T3], dim=0)<br/>4 × N × N<br/>Multi-order Laplacian"]
    end
    
    L --> L_exp
    L_exp --> T0
    L_exp --> T1
    T0 --> T2
    T1 --> T2
    L_exp --> T2
    T1 --> T3
    T2 --> T3
    L_exp --> T3
    T0 --> CAT
    T1 --> CAT
    T2 --> CAT
    T3 --> CAT
```

### Order Interpretation

| Order | Matrix | Captures |
|-------|--------|----------|
| 0 | Zeros | Node's own features (self-loop) |
| 1 | `L` | Direct neighbor information |
| 2 | `2L² - I` | 2-hop neighborhood |
| 3 | `2L³ - L` | 3-hop neighborhood |

The stacked result `mul_L` has shape `[4, N, N]`, providing multi-scale graph information that captures both local and global graph structure.

**Sources:** [models/base_model.py:121-134]()

---

## Integration with Forward Pass

The graph learning components integrate into the model's forward pass as follows:

```mermaid
graph TB
    subgraph ForwardMethod["Model.forward(x)"]
        START["Input x<br/>batch × nodes × time_step"]
        LLC["mul_L, attention = latent_correlation_layer(x)"]
        RESHAPE["X = x.unsqueeze(1).permute(0,1,3,2)"]
        
        subgraph StackLoop["For each StockBlockLayer"]
            SB["forecast, X = stock_block[i](X, mul_L)"]
        end
        
        COMBINE["Combine forecasts"]
        FC["Final FC layer"]
        OUT["Return forecast, attention"]
    end
    
    START --> LLC
    LLC --> RESHAPE
    RESHAPE --> SB
    SB --> COMBINE
    COMBINE --> FC
    FC --> OUT
```

### Data Flow Summary

1. **Input**: Raw time series `(batch, nodes, time_step)`
2. **Graph Learning**: `latent_correlation_layer()` produces:
   - `mul_L`: Multi-order Laplacian `(4, N, N)` for graph convolutions
   - `attention`: Learned adjacency matrix `(N, N)` for interpretability
3. **Processing**: Each `StockBlockLayer` uses `mul_L` for graph-aware feature extraction
4. **Output**: Forecasts and the attention matrix

**Sources:** [models/base_model.py:167-179]()

---

## Key Method Reference

### `latent_correlation_layer(x)`

**Purpose:** Orchestrates the entire graph learning pipeline.

**Input:** 
- `x`: Time series data `(batch, nodes, time_step)`

**Output:**
- `mul_L`: Multi-order Chebyshev Laplacian `(4, N, N)`
- `attention`: Learned attention matrix `(N, N)`

**Process:**
1. Extract temporal features via GRU
2. Compute self-attention scores
3. Average over batch and symmetrize
4. Compute normalized Laplacian
5. Generate Chebyshev polynomials

**Sources:** [models/base_model.py:136-149]()

### `self_graph_attention(input)`

**Purpose:** Compute pairwise attention scores between all nodes.

**Input:**
- `input`: Temporal features `(batch, nodes, unit)`

**Output:**
- `attention`: Attention matrix `(batch, N, N)`

**Sources:** [models/base_model.py:151-162]()

### `get_laplacian(graph, normalize)`

**Purpose:** Convert adjacency matrix to graph Laplacian.

**Parameters:**
- `graph`: Adjacency matrix `(N, N)`
- `normalize`: Boolean flag for normalization

**Output:**
- `L`: Graph Laplacian `(N, N)`

**Sources:** [models/base_model.py:106-119]()

### `cheb_polynomial(laplacian)`

**Purpose:** Compute Chebyshev polynomial approximation of graph filters.

**Input:**
- `laplacian`: Graph Laplacian `(N, N)`

**Output:**
- `multi_order_laplacian`: Stacked polynomials `(4, N, N)`

**Sources:** [models/base_model.py:121-134]()

---

## Configuration Parameters

Graph learning behavior is influenced by these model hyperparameters:

| Parameter | Type | Default | Impact on Graph Learning |
|-----------|------|---------|--------------------------|
| `units` | int | Varies by dataset | Dimensionality of GRU hidden state |
| `leaky_rate` | float | 0.2 | Slope for LeakyReLU in attention |
| `dropout_rate` | float | 0.5 | Regularization strength for attention |

These parameters are set during `Model` initialization and affect the expressiveness and regularization of the learned graph structure.

**Sources:** [models/base_model.py:79-80](), [models/base_model.py:102-103]()

---

## Summary

The graph learning components automatically discover latent relationships in multivariate time series through:

1. **GRU-based temporal feature extraction** that captures temporal patterns
2. **Self-attention mechanism** that computes pairwise node relationships
3. **Laplacian computation** that converts attention into a graph structure
4. **Chebyshev approximation** that enables efficient multi-hop graph operations

The resulting multi-order Laplacian `mul_L` and attention matrix `attention` are then used by the StockBlockLayer components (see [StockBlockLayer](#4.3.2)) for spectral graph convolution operations.

**Sources:** [models/base_model.py:78-180]()

---

