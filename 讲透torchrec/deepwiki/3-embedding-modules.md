<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/torchrec · page 3 Embedding Modules · fetched 2026-10-21 -->

# Embedding Modules

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [torchrec/metrics/tests/test_tower_qps.py](torchrec/metrics/tests/test_tower_qps.py)
- [torchrec/metrics/tower_qps.py](torchrec/metrics/tower_qps.py)
- [torchrec/modules/embedding_modules.py](torchrec/modules/embedding_modules.py)
- [torchrec/modules/tests/test_embedding_modules.py](torchrec/modules/tests/test_embedding_modules.py)
- [torchrec/modules/utils.py](torchrec/modules/utils.py)

</details>



This document covers TorchRec's embedding modules system, which provides the core interface for processing sparse features in recommendation models. These modules handle the conversion of sparse categorical features represented as `KeyedJaggedTensor` into dense embeddings for downstream model components.

For detailed information about specific embedding module implementations, see [EmbeddingBagCollection and EmbeddingCollection](#3.1). For memory-optimized variants, see [Quantized Embedding Modules](#3.2). For distributed versions of these modules, see [Sharded Embedding Collections](#4.2).

## Overview

TorchRec's embedding modules serve as the foundational layer for embedding lookup operations in recommendation systems. They provide unsharded, single-device implementations that are primarily used for prototyping, testing, and small-scale deployments. For production-scale distributed training, these modules are typically wrapped by their sharded counterparts.

## Core Embedding Module Architecture

```mermaid
graph TD
    subgraph "Input Layer"
        KJT["KeyedJaggedTensor<br/>Sparse Features"]
        EBC_Config["EmbeddingBagConfig"]
        EC_Config["EmbeddingConfig"]
    end
    
    subgraph "Abstract Interfaces"
        EBC_Interface["EmbeddingBagCollectionInterface"]
        EC_Interface["EmbeddingCollectionInterface"]
    end
    
    subgraph "Concrete Implementations"
        EBC["EmbeddingBagCollection<br/>Pooled Embeddings"]
        EC["EmbeddingCollection<br/>Sequence Embeddings"]
    end
    
    subgraph "PyTorch Primitives"
        EmbeddingBag["nn.EmbeddingBag"]
        Embedding["nn.Embedding"]
    end
    
    subgraph "Output Layer"
        KT["KeyedTensor<br/>Pooled Output"]
        JT_Dict["Dict[str, JaggedTensor]<br/>Sequence Output"]
    end
    
    KJT --> EBC
    KJT --> EC
    EBC_Config --> EBC
    EC_Config --> EC
    
    EBC_Interface --> EBC
    EC_Interface --> EC
    
    EBC --> EmbeddingBag
    EC --> Embedding
    
    EBC --> KT
    EC --> JT_Dict
```

**Embedding Module Class Hierarchy**

Sources: [torchrec/modules/embedding_modules.py:52-74](), [torchrec/modules/embedding_modules.py:304-333]()

## Embedding Module Types

TorchRec provides two primary embedding module types, each serving different use cases:

| Module Type | Input | Output | Use Case | PyTorch Primitive |
|-------------|-------|--------|----------|-------------------|
| `EmbeddingBagCollection` | `KeyedJaggedTensor` | `KeyedTensor` | Pooled embeddings for dense layers | `nn.EmbeddingBag` |
| `EmbeddingCollection` | `KeyedJaggedTensor` | `Dict[str, JaggedTensor]` | Sequence embeddings for attention/RNN | `nn.Embedding` |

### EmbeddingBagCollection

The `EmbeddingBagCollection` performs pooling operations (sum, mean, max) on variable-length feature lists, producing fixed-size dense embeddings suitable for feedforward networks.

### EmbeddingCollection 

The `EmbeddingCollection` preserves sequence structure, returning individual embeddings for each sparse feature value, suitable for sequential modeling approaches.

Sources: [torchrec/modules/embedding_modules.py:97-171](), [torchrec/modules/embedding_modules.py:335-404]()

## Data Flow and Processing Pipeline

```mermaid
graph LR
    subgraph "Feature Processing"
        Features["KeyedJaggedTensor<br/>keys=['f1', 'f2']<br/>values=[0,1,2,3,4]<br/>offsets=[0,2,3,5]"]
        FeatureDict["features.to_dict()<br/>Dict[str, JaggedTensor]"]
        Features --> FeatureDict
    end
    
    subgraph "EmbeddingBagCollection Flow"
        EBC_Tables["embedding_bags<br/>nn.ModuleDict"]
        EBC_Lookup["embedding_bag(input, offsets)<br/>Pooling Operation"]
        EBC_Concat["process_pooled_embeddings<br/>torch.cat()"]
        EBC_Output["KeyedTensor<br/>Pooled Results"]
        
        FeatureDict --> EBC_Tables
        EBC_Tables --> EBC_Lookup
        EBC_Lookup --> EBC_Concat
        EBC_Concat --> EBC_Output
    end
    
    subgraph "EmbeddingCollection Flow"
        EC_Tables["embeddings<br/>nn.ModuleDict"]
        EC_Lookup["embedding(input)<br/>Individual Lookups"]
        EC_Construct["construct_jagged_tensors<br/>JaggedTensor Creation"]
        EC_Output["Dict[str, JaggedTensor]<br/>Sequence Results"]
        
        FeatureDict --> EC_Tables
        EC_Tables --> EC_Lookup
        EC_Lookup --> EC_Construct
        EC_Construct --> EC_Output
    end
```

**Data Flow Through Embedding Modules**

Sources: [torchrec/modules/embedding_modules.py:224-263](), [torchrec/modules/embedding_modules.py:458-490](), [torchrec/modules/utils.py:239-298]()

## Configuration and Table Management

Embedding modules are configured through configuration objects that define table properties and feature mappings:

```mermaid
graph TD
    subgraph "Configuration Objects"
        EBC_Config["EmbeddingBagConfig<br/>name, embedding_dim<br/>num_embeddings<br/>feature_names, pooling"]
        EC_Config["EmbeddingConfig<br/>name, embedding_dim<br/>num_embeddings<br/>feature_names"]
    end
    
    subgraph "Feature Mapping Logic"
        SharedFeatures["get_embedding_names_by_table()<br/>Handle Feature Sharing"]
        FeatureNames["_feature_names<br/>List[List[str]]"]
        EmbeddingNames["_embedding_names<br/>List[str]"]
    end
    
    subgraph "PyTorch Module Creation"
        ModuleDict["nn.ModuleDict<br/>embedding_bags / embeddings"]
        WeightInit["init_fn<br/>Parameter Initialization"]
    end
    
    EBC_Config --> SharedFeatures
    EC_Config --> SharedFeatures
    SharedFeatures --> FeatureNames
    SharedFeatures --> EmbeddingNames
    
    FeatureNames --> ModuleDict
    EmbeddingNames --> ModuleDict
    EBC_Config --> WeightInit
    EC_Config --> WeightInit
    WeightInit --> ModuleDict
```

**Configuration and Initialization Flow**

### Feature Sharing Support

TorchRec embedding modules support advanced feature sharing scenarios:

- **Shared Tables**: Multiple features can use the same embedding table
- **Shared Features**: A single feature can be used by multiple tables (with name disambiguation using `@` syntax)
- **Unique Naming**: The `get_embedding_names_by_table()` function handles naming conflicts automatically

Sources: [torchrec/modules/embedding_modules.py:75-94](), [torchrec/modules/embedding_modules.py:173-222](), [torchrec/modules/embedding_modules.py:406-456]()

## Integration with Distributed System

While embedding modules are unsharded implementations, they serve as the foundation for TorchRec's distributed embedding system:

```mermaid
graph TB
    subgraph "Development Workflow"
        Prototype["EmbeddingBagCollection<br/>EmbeddingCollection<br/>Local Development"]
        Wrapper["DistributedModelParallel<br/>Model Wrapper"]
        Sharded["ShardedEmbeddingBagCollection<br/>ShardedEmbeddingCollection<br/>Production Deployment"]
    end
    
    subgraph "Shared Components"
        Configs["EmbeddingBagConfig<br/>EmbeddingConfig<br/>Table Definitions"]
        Interfaces["EmbeddingBagCollectionInterface<br/>EmbeddingCollectionInterface<br/>Common API"]
        Utils["construct_jagged_tensors<br/>process_pooled_embeddings<br/>Utility Functions"]
    end
    
    Prototype --> Wrapper
    Wrapper --> Sharded
    
    Configs --> Prototype
    Configs --> Sharded
    Interfaces --> Prototype
    Interfaces --> Sharded
    Utils --> Prototype
    Utils --> Sharded
```

**Integration with Distributed Training**

The unsharded embedding modules provide:

1. **API Compatibility**: Same interface as distributed versions for easy migration
2. **Configuration Reuse**: Same config objects work with distributed implementations  
3. **Development Testing**: Local testing before distributed deployment
4. **Utility Sharing**: Common utility functions used across both implementations

Sources: [torchrec/modules/embedding_modules.py:52-74](), [torchrec/modules/embedding_modules.py:304-333](), [torchrec/modules/utils.py:239-348]()

## Performance Considerations

The embedding modules in this system are designed for correctness and ease of use rather than performance optimization:

- **Single Device**: No distributed computation or communication
- **No Kernel Optimization**: Uses standard PyTorch `nn.EmbeddingBag` and `nn.Embedding`
- **Development Focus**: Intended for prototyping and testing workflows
- **Memory Limitations**: All embeddings must fit in single device memory

For production deployments requiring performance optimization, use the distributed variants covered in [Sharded Embedding Collections](#4.2).

Sources: [torchrec/modules/embedding_modules.py:101-103](), [torchrec/modules/embedding_modules.py:339-341]()

---

