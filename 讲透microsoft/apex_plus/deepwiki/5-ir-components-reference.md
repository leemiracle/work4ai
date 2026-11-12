<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/apex_plus · page 5 IR Components Reference · fetched 2026-10-26 -->

# IR Components Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apex_plus/ir/block.py](apex_plus/ir/block.py)
- [apex_plus/ir/cell.py](apex_plus/ir/cell.py)
- [apex_plus/ir/task.py](apex_plus/ir/task.py)

</details>



This document provides a comprehensive reference for APEX+ Intermediate Representation (IR) components. The IR system represents neural network architectures as a hierarchical structure of blocks, cells, and tasks that can be mapped to parallel execution plans.

For device-specific execution details, see [Device Management Reference](#4). For model implementations that use these IR components, see [Model Support](#6). For transformer-level orchestration, see [Transformer IR](#5.4).

## IR Component Hierarchy

The APEX+ IR system uses a four-level hierarchy to represent neural network architectures:

```mermaid
graph TD
    Transformer["Transformer<br/>(Top Level)"]
    Block1["Block"]
    Block2["Block"]
    BlockN["Block..."]
    
    Cell1["Cell<br/>(MHA, MLP, etc.)"]
    Cell2["Cell"]
    Cell3["Cell"]
    Cell4["Cell"]
    
    Task1["Task<br/>(MHAHead, MLPFilter, etc.)"]
    Task2["Task"]
    Task3["Task"]
    Task4["Task"]
    Task5["Task"]
    Task6["Task"]
    
    Transformer --> Block1
    Transformer --> Block2
    Transformer --> BlockN
    
    Block1 --> Cell1
    Block1 --> Cell2
    Block2 --> Cell3
    Block2 --> Cell4
    BlockN --> Cell5
    BlockN --> Cell6
    
    Cell1 --> Task1
    Cell1 --> Task2
    Cell2 --> Task3
    Cell3 --> Task4
    Cell4 --> Task5
    Cell4 --> Task6
```

**Sources:** [apex_plus/ir/block.py:1-13](), [apex_plus/ir/cell.py:1-26](), [apex_plus/ir/task.py:1-25]()

## Core Base Classes

### Task Class

The `Task` class is the fundamental unit of computation in the IR system. Each task represents a specific neural network operation that can be profiled and scheduled.

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `get_type()` | Returns class name as task identifier | `str` |
| `get_param_size()` | Calculates parameter memory requirements | `int` |
| `get_kv_token_size()` | Calculates key-value cache memory per token | `int` |
| `is_attn()` | Identifies attention-related tasks | `bool` |

**Sources:** [apex_plus/ir/task.py:6-25]()

### Cell Class

The `Cell` class represents a logical grouping of related tasks, such as a multi-head attention mechanism or feed-forward network. Cells are the primary unit for parallelization strategies.

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `get_name()` | Returns class name as cell identifier | `str` |
| `get_tasks()` | Returns list of constituent tasks | `List[Task]` |
| `get_num_task_types()` | Returns number of distinct task types | `int` |
| `has_same_spec()` | Compares cell specifications for equivalence | `bool` |
| `is_attn()` | Checks if cell contains attention tasks | `bool` |

**Sources:** [apex_plus/ir/cell.py:6-26]()

### Block Class

The `Block` class represents a transformer layer containing multiple cells. Blocks are typically replicated across multiple transformer layers.

```mermaid
graph LR
    subgraph "Block Structure"
        Block["Block"]
        CellList["cells: List[Cell]"]
        Block --> CellList
        
        subgraph "Typical Cells"
            MHA["MHA Cell<br/>(Multi-Head Attention)"]
            MLP["MLP Cell<br/>(Feed Forward)"]
        end
        
        CellList --> MHA
        CellList --> MLP
    end
```

**Sources:** [apex_plus/ir/block.py:6-13]()

## Component Type Categories

### Attention Components

Attention components handle the self-attention mechanisms that are central to transformer architectures:

- **Multi-Head Attention (MHA)** - Standard attention with multiple parallel heads
- **Bidirectional MHA** - Attention that processes both directions  
- **Multi-Query Attention (MQA)** - Attention with shared key-value projections

For detailed specifications, see [Attention Components](#5.1).

### Feed-Forward Components  

Feed-forward components implement the position-wise neural networks in transformer layers:

- **MLP** - Standard multi-layer perceptron
- **GLU** - Gated Linear Unit with sigmoid gating
- **SwiGLU** - Swish-activated GLU variant
- **MoE** - Mixture of Experts with sparse activation

For detailed specifications, see [Feed-Forward Components](#5.2).

### Supporting Components

Additional components provide embedding, normalization, and output sampling:

- **Embedding layers** - Token and position embeddings
- **Sampling mechanisms** - Output token generation strategies

For detailed specifications, see [Other IR Components](#5.3).

## IR Component Relationships

```mermaid
graph TB
    subgraph "Base Classes"
        TaskBase["Task<br/>(apex_plus/ir/task.py)"]
        CellBase["Cell<br/>(apex_plus/ir/cell.py)"]
        BlockBase["Block<br/>(apex_plus/ir/block.py)"]
    end
    
    subgraph "Attention Implementations"
        MHACell["MHACell"]
        MQACell["MQACell"] 
        BiMHACell["BiMHACell"]
        MHAHead["MHAHead"]
        MQAHead["MQAHead"]
    end
    
    subgraph "Feed-Forward Implementations"
        MLPCell["MLPCell"]
        GLUCell["GLUCell"]
        SwiGLUCell["SwiGLUCell"]
        MoECell["MoECell"]
        MLPFilter["MLPFilter"]
        GLUFilter["GLUFilter"]
    end
    
    CellBase --> MHACell
    CellBase --> MQACell
    CellBase --> BiMHACell
    CellBase --> MLPCell
    CellBase --> GLUCell
    CellBase --> SwiGLUCell
    CellBase --> MoECell
    
    TaskBase --> MHAHead
    TaskBase --> MQAHead
    TaskBase --> MLPFilter
    TaskBase --> GLUFilter
    
    MHACell --> MHAHead
    MQACell --> MQAHead
    MLPCell --> MLPFilter
    GLUCell --> GLUFilter
    SwiGLUCell --> GLUFilter
    
    BlockBase --> MHACell
    BlockBase --> MLPCell
```

**Sources:** [apex_plus/ir/task.py:6-25](), [apex_plus/ir/cell.py:6-26](), [apex_plus/ir/block.py:6-13]()

## Key Design Patterns

### Abstract Interface Pattern

All IR components follow an abstract interface pattern where base classes define the contract and concrete implementations provide specific behavior:

- `Task` base class defines computation interface
- `Cell` base class defines task aggregation interface  
- Concrete implementations override abstract methods

### Composition Hierarchy

Components use composition to build complex structures:

- Blocks contain lists of Cells
- Cells contain lists of Tasks
- Tasks represent atomic operations

### Type Identification

Components provide both class-based and instance-based type identification:

- `get_name()` returns class name for cells
- `get_type()` returns class name for tasks
- `is_attn()` provides functional classification

**Sources:** [apex_plus/ir/cell.py:12-13](), [apex_plus/ir/cell.py:24-25](), [apex_plus/ir/task.py:11-12](), [apex_plus/ir/task.py:23-24]()

---

