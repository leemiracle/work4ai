<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/torchrec · page 2 Core Data Structures · fetched 2026-10-21 -->

# Core Data Structures

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [torchrec/distributed/test_utils/multi_process.py](torchrec/distributed/test_utils/multi_process.py)
- [torchrec/distributed/test_utils/test_input.py](torchrec/distributed/test_utils/test_input.py)
- [torchrec/distributed/tests/test_pt2.py](torchrec/distributed/tests/test_pt2.py)
- [torchrec/distributed/tests/test_pt2_multiprocess.py](torchrec/distributed/tests/test_pt2_multiprocess.py)
- [torchrec/pt2/checks.py](torchrec/pt2/checks.py)
- [torchrec/pt2/utils.py](torchrec/pt2/utils.py)
- [torchrec/sparse/jagged_tensor.py](torchrec/sparse/jagged_tensor.py)
- [torchrec/sparse/tests/test_jagged_tensor.py](torchrec/sparse/tests/test_jagged_tensor.py)

</details>



This document describes TorchRec's fundamental data structures for handling sparse and dense feature data in recommendation systems. These data structures form the foundation for all higher-level embedding modules and distributed operations in TorchRec.

For information about embedding modules that use these data structures, see [Embedding Modules](#3). For details about distributed operations on these data structures, see [Distributed Training](#4).

## Overview

TorchRec provides three core data structures to efficiently represent recommendation system features:

| Data Structure | Purpose | Data Type |
|----------------|---------|-----------|
| `JaggedTensor` | Variable-length sequences per batch sample | Sparse |
| `KeyedJaggedTensor` | Named collection of `JaggedTensor`s | Sparse |
| `KeyedTensor` | Named collection of dense tensors | Dense |

These data structures are designed to handle the irregular nature of recommendation system features, where different samples may have different numbers of features (e.g., different numbers of items viewed by users).

## Data Structure Hierarchy

```mermaid
graph TD
    subgraph "Core Tensor Types"
        JT["JaggedTensor<br/>Single jagged dimension"]
        KJT["KeyedJaggedTensor<br/>Multiple named JaggedTensors"]
        KT["KeyedTensor<br/>Multiple named dense tensors"]
    end
    
    subgraph "Internal Components"
        Values["values: torch.Tensor<br/>Raw data values"]
        Lengths["lengths: torch.Tensor<br/>Sequence lengths per batch"]
        Offsets["offsets: torch.Tensor<br/>Cumulative offsets"]
        Weights["weights: torch.Tensor<br/>Optional feature weights"]
        Keys["keys: List[str]<br/>Feature names"]
    end
    
    subgraph "Operations"
        ToDict["to_dict()<br/>Convert to dictionary"]
        Split["split()<br/>Partition by keys"]
        Permute["permute()<br/>Reorder features"]
        ToDense["to_dense()<br/>Convert to list of tensors"]
    end
    
    JT --> Values
    JT --> Lengths
    JT --> Offsets
    JT --> Weights
    
    KJT --> JT
    KJT --> Keys
    
    KT --> Keys
    
    KJT --> ToDict
    KJT --> Split
    KJT --> Permute
    JT --> ToDense
```

Sources: [torchrec/sparse/jagged_tensor.py:562-1030](), [torchrec/sparse/jagged_tensor.py:1095-2000]()

## JaggedTensor

`JaggedTensor` represents a tensor with a *jagged dimension* - a dimension whose slices may be of different lengths. This is the fundamental building block for sparse features in recommendation systems.

### Core Components

A `JaggedTensor` consists of:
- **values**: The actual data in dense format
- **lengths** OR **offsets**: Describes how to interpret the jagged structure
- **weights** (optional): Per-value weights for weighted operations

```mermaid
graph LR
    subgraph "JaggedTensor Structure"
        Values["values=[1,2,3,4,5,6,7,8]"]
        Lengths["lengths=[2,0,3,3]"]
        Offsets["offsets=[0,2,2,5,8]"]
        Weights["weights=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]"]
    end
    
    subgraph "Logical Structure"
        Row0["Batch 0: [1,2]"]
        Row1["Batch 1: []"]
        Row2["Batch 2: [3,4,5]"]
        Row3["Batch 3: [6,7,8]"]
    end
    
    Values --> Row0
    Values --> Row1
    Values --> Row2
    Values --> Row3
    
    Lengths --> Row0
    Lengths --> Row1
    Lengths --> Row2
    Lengths --> Row3
```

Sources: [torchrec/sparse/jagged_tensor.py:562-603](), [torchrec/sparse/jagged_tensor.py:895-933]()

### Construction Methods

`JaggedTensor` provides multiple construction methods:

| Method | Purpose | Use Case |
|--------|---------|----------|
| `JaggedTensor(values, lengths/offsets, weights)` | Direct construction | When you have pre-computed sparse data |
| `JaggedTensor.from_dense_lengths()` | From 2D dense tensor + lengths | Converting from dense representations |
| `JaggedTensor.from_dense()` | From list of tensors | When each sample is a separate tensor |
| `JaggedTensor.empty()` | Empty tensor | Initialization |

### Key Operations

The `JaggedTensor` supports conversion between sparse and dense representations:

```mermaid
graph TD
    subgraph "Dense to Sparse"
        DenseList["List[torch.Tensor]<br/>[[1,2], [], [3,4,5]]"]
        DenseTensor["2D torch.Tensor + lengths<br/>[[1,2,0],[0,0,0],[3,4,5]]"]
    end
    
    subgraph "JaggedTensor"
        JT["values=[1,2,3,4,5]<br/>lengths=[2,0,3]"]
    end
    
    subgraph "Operations"
        ToPadded["to_padded_dense()"]
        ToList["to_dense()"]
    end
    
    DenseList -->|"from_dense()"| JT
    DenseTensor -->|"from_dense_lengths()"| JT
    JT -->|"to_dense()"| ToList
    JT -->|"to_padded_dense()"| ToPadded
```

Sources: [torchrec/sparse/jagged_tensor.py:636-717](), [torchrec/sparse/jagged_tensor.py:718-831]()

## KeyedJaggedTensor

`KeyedJaggedTensor` represents a collection of `JaggedTensor`s with associated feature names (keys). This is the primary data structure for sparse features in TorchRec.

### Structure and Components

```mermaid
graph TD
    subgraph "KeyedJaggedTensor"
        Keys["keys=['user_id', 'item_id', 'category']"]
        Values["values=[101,102,201,202,203,301]"]
        Lengths["lengths=[2,3,1]"]
        LengthPerKey["length_per_key=[2,3,1]"]
        Stride["stride=2 (batch_size)"]
    end
    
    subgraph "Logical View"
        UserFeature["user_id: [[101],[102]]"]
        ItemFeature["item_id: [[201,202,203],[]]"] 
        CategoryFeature["category: [[],[301]]"]
    end
    
    Keys --> UserFeature
    Keys --> ItemFeature
    Keys --> CategoryFeature
    
    Values --> UserFeature
    Values --> ItemFeature 
    Values --> CategoryFeature
```

Sources: [torchrec/sparse/jagged_tensor.py:1095-1200]()

### Key Operations

`KeyedJaggedTensor` provides several important operations for feature manipulation:

| Operation | Method | Purpose |
|-----------|--------|---------|
| Feature selection | `kjt["feature_name"]` | Extract single feature as `JaggedTensor` |
| Feature grouping | `split([1, 2, 1])` | Split into multiple `KeyedJaggedTensor`s |
| Feature reordering | `permute([2, 0, 1])` | Reorder features |
| Dictionary conversion | `to_dict()` | Convert to `Dict[str, JaggedTensor]` |

### Variable Stride Support

`KeyedJaggedTensor` supports variable stride per key for handling variable batch sizes across different features:

```mermaid
graph LR
    subgraph "Fixed Stride"
        FS_Keys["keys=['f1','f2']"]
        FS_Stride["stride=3"]
        FS_Lengths["lengths=[2,1,0,1,2,1]"]
    end
    
    subgraph "Variable Stride"
        VS_Keys["keys=['f1','f2']"] 
        VS_StridePerKey["stride_per_key_per_rank=[[3],[2]]"]
        VS_Lengths["lengths=[2,1,0,1,2]"]
        VS_Inverse["inverse_indices=(keys, indices)"]
    end
    
    FS_Keys --> VS_Keys
    FS_Stride -->|"convert_to_vb=True"| VS_StridePerKey
    FS_Lengths --> VS_Lengths
    VS_StridePerKey --> VS_Inverse
```

Sources: [torchrec/sparse/jagged_tensor.py:1500-1600](), [torchrec/pt2/utils.py:28-91]()

## KeyedTensor

`KeyedTensor` represents a collection of dense tensors with associated keys, typically used for embedding outputs and dense features.

### Structure

```mermaid
graph TD
    subgraph "KeyedTensor"
        Keys["keys=['user_emb', 'item_emb']"]
        Values["values=torch.Tensor<br/>shape: [batch_size, total_dim]"]
        KeyDim["key_dim=1"]
        LengthPerKey["length_per_key=[64, 32]"]
    end
    
    subgraph "Logical View"
        UserEmb["user_emb: [batch_size, 64]"]
        ItemEmb["item_emb: [batch_size, 32]"]
    end
    
    Keys --> UserEmb
    Values --> UserEmb
    Values --> ItemEmb
    LengthPerKey --> UserEmb
    LengthPerKey --> ItemEmb
```

### Key Operations

| Operation | Purpose |
|-----------|---------|
| `to_dict()` | Convert to dictionary of tensors |
| `regroup()` | Rearrange tensors into new groupings |
| `regroup_as_dict()` | Regroup and return as dictionary |

Sources: [torchrec/sparse/jagged_tensor.py:3000-4000]()

## PyTorch Integration

All core data structures integrate deeply with PyTorch:

### TorchScript Support

```mermaid
graph TD
    subgraph "TorchScript Compatibility"
        JT_Script["JaggedTensor<br/>@torch.jit.script"]
        KJT_Script["KeyedJaggedTensor<br/>@torch.jit.script"] 
        Operations["All operations<br/>TorchScript compatible"]
    end
    
    subgraph "PyTree Support"
        Flatten["pytree.tree_flatten()"]
        Unflatten["pytree.tree_unflatten()"]
    end
    
    JT_Script --> Operations
    KJT_Script --> Operations
    JT_Script --> Flatten
    KJT_Script --> Unflatten
```

Sources: [torchrec/sparse/jagged_tensor.py:1056-1064]()

### PT2 Compilation Support

TorchRec data structures support PyTorch 2.0 compilation through specialized utilities:

```mermaid
graph LR
    subgraph "PT2 Integration"
        KJT_Raw["KeyedJaggedTensor<br/>(with caches)"]
        KJT_Trace["kjt_for_pt2_tracing()"]
        KJT_Clean["Clean KJT<br/>(no caches)"]
        Compile["torch.compile()"]
    end
    
    KJT_Raw --> KJT_Trace
    KJT_Trace --> KJT_Clean
    KJT_Clean --> Compile
```

Sources: [torchrec/pt2/utils.py:28-91](), [torchrec/pt2/checks.py:1-99]()

## Memory Layout and Performance

The data structures are optimized for memory efficiency and performance:

### Memory Layout

```mermaid
graph TD
    subgraph "Contiguous Memory"
        Values["values: [v1,v2,v3,v4,v5,v6]<br/>Contiguous tensor"]
        Weights["weights: [w1,w2,w3,w4,w5,w6]<br/>Same shape as values"]
    end
    
    subgraph "Index Structures"
        Lengths["lengths: [2,0,3,1]<br/>Per-sequence lengths"]
        Offsets["offsets: [0,2,2,5,6]<br/>Cumulative offsets"]
    end
    
    subgraph "Benefits"
        GPU_Efficient["GPU-efficient<br/>vectorized operations"]
        Cache_Friendly["Cache-friendly<br/>sequential access"]
    end
    
    Values --> GPU_Efficient
    Lengths --> Cache_Friendly
```

### Device Movement

All data structures support efficient device movement with pinned memory optimization:

```mermaid
graph LR
    CPU["CPU Memory"] 
    Pinned["Pinned Memory<br/>pin_memory()"]
    GPU["GPU Memory<br/>non_blocking=True"]
    
    CPU --> Pinned
    Pinned --> GPU
```

Sources: [torchrec/sparse/jagged_tensor.py:54-66](), [torchrec/sparse/jagged_tensor.py:962-1009]()

---

