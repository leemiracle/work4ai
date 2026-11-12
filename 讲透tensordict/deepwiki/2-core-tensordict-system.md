<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/tensordict · page 2 Core TensorDict System · fetched 2026-10-21 -->

# Core TensorDict System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tensordict/_lazy.py](tensordict/_lazy.py)
- [tensordict/_td.py](tensordict/_td.py)
- [tensordict/base.py](tensordict/base.py)
- [test/test_tensordict.py](test/test_tensordict.py)

</details>



## Purpose and Scope

This document describes the fundamental TensorDict data structure system, including the abstract `TensorDictBase` interface and its core implementations (`TensorDict` and `LazyStackedTensorDict`). It covers the architectural design, internal data structures, and key concepts like batch semantics and device management.

For specific operations and methods:
- Creating and initializing TensorDicts: see [Creating and Initializing TensorDicts](#2.2)
- Accessing and modifying data: see [Accessing and Modifying Data](#2.3)
- Shape operations: see [Shape Operations and Transformations](#2.4)
- Storage and persistence: see [Storage and Persistence](#5)
- Neural network integration: see [Neural Network Integration](#4)

## System Architecture

The TensorDict system is built on an abstract interface pattern with multiple specialized implementations. The core hierarchy provides different storage and evaluation strategies while maintaining a consistent API.

```mermaid
graph TB
    subgraph "Abstract Interface"
        TDB["TensorDictBase<br/>(base.py)"]
    end
    
    subgraph "Core Implementations"
        TD["TensorDict<br/>(_td.py)<br/>Main eager implementation"]
        LTD["LazyStackedTensorDict<br/>(_lazy.py)<br/>Lazy stacking"]
        STD["_SubTensorDict<br/>(_td.py)<br/>Indexed view"]
    end
    
    subgraph "Storage Backends"
        PTD["PersistentTensorDict<br/>(persistent.py)<br/>HDF5-backed"]
    end
    
    subgraph "Internal Data"
        DICT["_StringOnlyDict<br/>Key-value storage"]
        BS["batch_size: torch.Size<br/>Leading dimensions"]
        DEV["device: torch.device<br/>Optional device"]
    end
    
    TDB --> TD
    TDB --> LTD
    TDB --> STD
    TDB --> PTD
    
    TD --> DICT
    TD --> BS
    TD --> DEV
    
    LTD --> |"stack_dim"| TD
    LTD --> |"tensordicts: list"| TDB
    
    style TDB fill:#f9f9f9,stroke:#333,stroke-width:2px
    style TD fill:#f9f9f9,stroke:#333,stroke-width:2px
    style LTD fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [tensordict/base.py:300-331](), [tensordict/_td.py:150-243](), [tensordict/_lazy.py:176-225]()

The system uses a layered architecture:

| Layer | Component | File | Responsibility |
|-------|-----------|------|----------------|
| Abstract Interface | `TensorDictBase` | `base.py` | Defines API contract for all implementations |
| Primary Implementation | `TensorDict` | `_td.py` | Eager tensor storage with dictionary semantics |
| Lazy Evaluation | `LazyStackedTensorDict` | `_lazy.py` | Deferred stacking of multiple TensorDicts |
| Indexed Views | `_SubTensorDict` | `_td.py` | Lazy indexed view over parent TensorDict |
| Persistence | `PersistentTensorDict` | `persistent.py` | Memory-mapped HDF5 storage |

## TensorDictBase Abstract Interface

`TensorDictBase` is the abstract base class that defines the contract for all TensorDict implementations. It inherits from `MutableMapping` and `TensorCollection`, providing dictionary-like semantics for tensor containers.

```mermaid
graph LR
    subgraph "Core Properties"
        BS["batch_size: torch.Size<br/>Leading dimensions shared<br/>by all tensors"]
        DEV["device: torch.device | None<br/>Optional device constraint"]
        NAMES["names: list[str] | None<br/>Dimension names"]
        LOCK["is_locked: bool<br/>Mutability flag"]
    end
    
    subgraph "Abstract Methods"
        GET["_get_str()<br/>_get_tuple()<br/>Key access"]
        SET["_set_str()<br/>_set_tuple()<br/>Key assignment"]
        INDEX["_index_tensordict()<br/>Batch indexing"]
        CLONE["clone()<br/>Deep copy"]
    end
    
    subgraph "Key Management"
        KEYS["keys()<br/>Keys iterator"]
        ITEMS["items()<br/>Key-value pairs"]
        VALUES["values()<br/>Values iterator"]
    end
    
    TDB["TensorDictBase"] --> BS
    TDB --> DEV
    TDB --> NAMES
    TDB --> LOCK
    TDB --> GET
    TDB --> SET
    TDB --> INDEX
    TDB --> CLONE
    TDB --> KEYS
    TDB --> ITEMS
    TDB --> VALUES
```

**Sources:** [tensordict/base.py:300-310](), [tensordict/base.py:559-648]()

### Key Characteristics

The abstract interface enforces several invariants:

1. **Batch Semantics**: All tensors must share the first `N` dimensions defined by `batch_size` [tensordict/base.py:301-302]()
2. **Device Consistency**: When a device is set, all tensors must reside on that device [tensordict/_td.py:254-257]()
3. **Nested Keys**: Keys can be strings or tuples of strings for nested access [tensordict/base.py:559-571]()
4. **Immutability Control**: Locking prevents structural modifications while allowing in-place updates [tensordict/base.py:307]()

### Critical Abstract Methods

Implementations must provide these core methods:

| Method | Purpose | Signature |
|--------|---------|-----------|
| `_get_str()` | Retrieve value by string key | `(key: str, default) -> Any` |
| `_get_tuple()` | Retrieve nested value | `(key: tuple, default) -> Any` |
| `_set_str()` | Set value by string key | `(key, value, inplace, validated) -> Self` |
| `_set_tuple()` | Set nested value | `(key, value, inplace, validated) -> Self` |
| `_index_tensordict()` | Index along batch dimensions | `(index: IndexType) -> Self` |

**Sources:** [tensordict/base.py:639-648]()

## TensorDict: Main Implementation

`TensorDict` is the primary concrete implementation that stores tensors in an eager dictionary-like structure. It uses `_StringOnlyDict` for internal storage, which enforces string-only keys at the top level.

```mermaid
graph TB
    subgraph "TensorDict Structure"
        TD["TensorDict Instance"]
        
        subgraph "Core Attributes"
            TD_DICT["_tensordict: _StringOnlyDict<br/>Maps str → Tensor | TensorDict"]
            BS_ATTR["_batch_size: torch.Size<br/>Shared leading dimensions"]
            DEV_ATTR["_device: torch.device | None<br/>Optional device constraint"]
            NAMES_ATTR["_td_dim_names: list[str] | None<br/>Dimension names"]
            LOCK_ATTR["_is_locked: bool<br/>Mutability state"]
        end
        
        subgraph "Internal Flags"
            SHARED["_is_shared: bool<br/>Shared memory status"]
            MEMMAP["_is_memmap: bool<br/>Memory-mapped status"]
            CACHE["_cache: dict | None<br/>Cached computations"]
        end
    end
    
    TD --> TD_DICT
    TD --> BS_ATTR
    TD --> DEV_ATTR
    TD --> NAMES_ATTR
    TD --> LOCK_ATTR
    TD --> SHARED
    TD --> MEMMAP
    TD --> CACHE
    
    TD_DICT --> |"string keys"| TENSOR["torch.Tensor"]
    TD_DICT --> |"nested keys"| NESTED_TD["TensorDict<br/>(recursive)"]
    TD_DICT --> |"non-tensor"| NON_TENSOR["NonTensorData"]
```

**Sources:** [tensordict/_td.py:150-259](), [tensordict/_td.py:266-267]()

### Initialization and Construction

The `TensorDict.__init__()` method handles several initialization patterns:

```mermaid
graph LR
    subgraph "Input Sources"
        SRC_DICT["dict[NestedKey, Tensor]"]
        SRC_TD["TensorDict"]
        SRC_KWARGS["**kwargs"]
    end
    
    subgraph "Initialization Steps"
        PARSE["_parse_batch_size()<br/>Infer or validate batch_size"]
        DEVICE["Handle device parameter<br/>auto-index CUDA devices"]
        SET_VALS["set() for each key-value<br/>Validate and cast"]
        SYNC["_sync_all()<br/>If non_blocking=None"]
        LOCK_OPT["lock_() if lock=True"]
    end
    
    SRC_DICT --> PARSE
    SRC_TD --> PARSE
    SRC_KWARGS --> PARSE
    PARSE --> DEVICE
    DEVICE --> SET_VALS
    SET_VALS --> SYNC
    SYNC --> LOCK_OPT
```

**Sources:** [tensordict/_td.py:250-322]()

Key initialization behaviors:

1. **Device Auto-indexing**: CUDA devices without explicit index use `torch.cuda.current_device()` [tensordict/_td.py:280-286]()
2. **Asynchronous Transfers**: `non_blocking=None` enables async transfer with sync after init [tensordict/_td.py:272-294]()
3. **Batch Size Parsing**: Can infer from source or require explicit specification [tensordict/_td.py:304]()
4. **Recursive Construction**: Nested dicts become nested TensorDicts [tensordict/_td.py:309-310]()

### Internal Storage: _StringOnlyDict

The `_StringOnlyDict` class provides string-only key enforcement at the top level, while nested structures handle tuples through recursive descent.

```mermaid
graph TB
    subgraph "_StringOnlyDict"
        DICT_IMPL["dict subclass<br/>String-only keys"]
        SETITEM["__setitem__<br/>Validates string keys"]
        GETITEM["__getitem__<br/>Standard dict access"]
    end
    
    subgraph "Key Access Patterns"
        STR_KEY["'key'<br/>Direct access"]
        TUPLE_KEY["('a', 'b', 'c')<br/>Nested access"]
        NESTED["'a' → TensorDict<br/>'b' → TensorDict<br/>'c' → Tensor"]
    end
    
    TD_INSTANCE["TensorDict._tensordict"] --> DICT_IMPL
    STR_KEY --> GETITEM
    TUPLE_KEY --> |"recursively"| NESTED
    
    DICT_IMPL --> SETITEM
    DICT_IMPL --> GETITEM
```

**Sources:** [tensordict/utils.py]() (referenced in imports), [tensordict/_td.py:266]()

### Value Validation and Setting

The `_set_str()` method performs validation and type conversion:

```mermaid
graph TB
    START["_set_str(key, value, inplace, validated)"]
    
    CHECK_LOCK["Check is_locked<br/>Raise if locked and not inplace"]
    
    VALIDATED{"validated?"}
    VALIDATE["_validate_value()<br/>- Check shape compatibility<br/>- Cast to device<br/>- Handle nested TDs"]
    
    INPLACE{"inplace?"}
    CONVERT["_convert_inplace()<br/>Check if key exists"]
    
    IN_TRUE["Update existing tensor<br/>data.copy_() or set_()"]
    IN_FALSE["Create new entry<br/>Store in _tensordict"]
    
    START --> CHECK_LOCK
    CHECK_LOCK --> VALIDATED
    VALIDATED -->|"No"| VALIDATE
    VALIDATED -->|"Yes"| INPLACE
    VALIDATE --> INPLACE
    INPLACE -->|"True"| IN_TRUE
    INPLACE -->|"False"| IN_FALSE
    INPLACE -->|"BEST_ATTEMPT"| CONVERT
    CONVERT --> IN_TRUE
    CONVERT --> IN_FALSE
```

**Sources:** [tensordict/_td.py]() (methods distributed across file), [tensordict/base.py]() (validation logic)

Key validation steps:
- **Shape Validation**: Ensure tensor shape matches or is compatible with `batch_size` [tensordict/base.py]()
- **Device Casting**: Convert tensors to tensordict's device if specified [tensordict/_td.py:310]()
- **Type Conversion**: Handle Python primitives, NumPy arrays, nested dicts [tensordict/base.py]()
- **Nested Structure**: Recursively convert nested dicts to nested TensorDicts [tensordict/_td.py:372-380]()

## LazyStackedTensorDict: Deferred Stacking

`LazyStackedTensorDict` provides a lazy view over a stack of TensorDicts without materializing the stacked tensors until accessed. This enables memory-efficient operations on collections of TensorDicts.

```mermaid
graph TB
    subgraph "LazyStackedTensorDict"
        LAZY["LazyStackedTensorDict"]
        
        subgraph "Core Attributes"
            TDS["tensordicts: list[TensorDictBase]<br/>Stack members"]
            SDIM["stack_dim: int<br/>Dimension along which to stack"]
            BS_L["_batch_size: torch.Size<br/>Computed from constituents"]
            HOOK_OUT["hook_out: Callable | None<br/>Post-get transformation"]
            HOOK_IN["hook_in: Callable | None<br/>Pre-set transformation"]
        end
        
        subgraph "Lazy Properties"
            VM["_is_vmapped: bool<br/>Hidden vmap dimension"]
            DIM_NAME["_td_dim_name: str | None<br/>Stack dimension name"]
        end
    end
    
    LAZY --> TDS
    LAZY --> SDIM
    LAZY --> BS_L
    LAZY --> HOOK_OUT
    LAZY --> HOOK_IN
    LAZY --> VM
    LAZY --> DIM_NAME
    
    TDS --> |"Contains"| TD1["TensorDict"]
    TDS --> |"Contains"| TD2["TensorDict"]
    TDS --> |"Contains"| TDN["TensorDict"]
```

**Sources:** [tensordict/_lazy.py:176-225](), [tensordict/_lazy.py:255-303]()

### Stack Dimension and Batch Size

The batch size is computed by inserting the stack length at `stack_dim`:

```mermaid
graph LR
    subgraph "Batch Size Computation"
        INPUT_BS["Input: td[0].batch_size<br/>[3, 4, 5]"]
        STACK["stack_dim=1<br/>len(tensordicts)=10"]
        OUTPUT_BS["Output: batch_size<br/>[3, 10, 4, 5]"]
    end
    
    INPUT_BS --> STACK
    STACK --> OUTPUT_BS
```

Formula: `batch_size = (*batch_size[:stack_dim], len(tensordicts), *batch_size[stack_dim:])`

**Sources:** [tensordict/_lazy.py:723-729]()

### Lazy Get Operation

The `_get_str()` method defers stacking until access:

```mermaid
graph TB
    START["_get_str(key, default)"]
    
    COLLECT["Collect tensors from each TD<br/>tensors = [td._get_str(key) for td in tensordicts]"]
    
    CHECK{"All same type?"}
    
    STACK_TENSOR["torch.stack(tensors, stack_dim)<br/>Materialize stacked tensor"]
    
    STACK_TD["LazyStackedTensorDict.lazy_stack()<br/>Return nested lazy stack"]
    
    HOOK{"hook_out?"}
    APPLY_HOOK["out = hook_out(out)"]
    
    RETURN["Return stacked value"]
    
    START --> COLLECT
    COLLECT --> CHECK
    CHECK -->|"Tensors"| STACK_TENSOR
    CHECK -->|"TensorDicts"| STACK_TD
    STACK_TENSOR --> HOOK
    STACK_TD --> HOOK
    HOOK -->|"Yes"| APPLY_HOOK
    HOOK -->|"No"| RETURN
    APPLY_HOOK --> RETURN
```

**Sources:** [tensordict/_lazy.py:1299-1412]()

Key behaviors:
- **Deferred Materialization**: Tensors only stacked when accessed [tensordict/_lazy.py:1313-1327]()
- **Nested Lazy Stacks**: TensorDict values result in nested LazyStackedTensorDict [tensordict/_lazy.py:1362-1378]()
- **Hook Integration**: `hook_out` applied after stacking for vmap support [tensordict/_lazy.py:1396-1398]()
- **Error Handling**: Shape mismatches raise informative errors [tensordict/_lazy.py:1399-1411]()

### Lazy Set Operation

Setting values on a lazy stack unbinds the value and distributes to constituents:

```mermaid
graph TB
    START["_set_str(key, value, inplace, validated)"]
    
    VALIDATE{"validated?"}
    VAL_STEP["_validate_value()<br/>Check shape, device"]
    
    CHECK_LIST{"isinstance(value, list)?"}
    
    UNBIND_LIST["_recursive_unbind_list()<br/>Split list by stack_dim"]
    
    UNBIND_TENSOR["value.unbind(stack_dim)<br/>Split tensor"]
    
    ZIP["zip(tensordicts, values)"]
    
    SET_EACH["For each (td, val):<br/>td._set_str(key, val, inplace, validated)"]
    
    START --> VALIDATE
    VALIDATE -->|"No"| VAL_STEP
    VALIDATE -->|"Yes"| CHECK_LIST
    VAL_STEP --> CHECK_LIST
    CHECK_LIST -->|"Yes"| UNBIND_LIST
    CHECK_LIST -->|"No"| UNBIND_TENSOR
    UNBIND_LIST --> ZIP
    UNBIND_TENSOR --> ZIP
    ZIP --> SET_EACH
```

**Sources:** [tensordict/_lazy.py:731-774]()

The distribution logic:
1. **List Handling**: Lists split according to stack_dim structure [tensordict/_lazy.py:759-762]()
2. **Tensor Unbinding**: Tensors unbind along stack_dim [tensordict/_lazy.py:764]()
3. **In-place Propagation**: `inplace` flag propagated to constituents [tensordict/_lazy.py:766-773]()

### Exclusive Keys and Heterogeneous Stacks

LazyStackedTensorDict tracks whether constituent TensorDicts have different keys:

```mermaid
graph LR
    subgraph "Exclusive Keys Detection"
        TD_A["TD A: keys={'a', 'b', 'c'}"]
        TD_B["TD B: keys={'a', 'b', 'd'}"]
        COMPARE["Compare keysets"]
        FLAG["_has_exclusive_keys = True"]
    end
    
    subgraph "Operations Affected"
        FAILS["Fails if exclusive:<br/>- to_dict()<br/>- state_dict()<br/>- flatten_keys()"]
        WORKS["Still works:<br/>- get(key)<br/>- set(key, value)<br/>- indexing"]
    end
    
    TD_A --> COMPARE
    TD_B --> COMPARE
    COMPARE --> FLAG
    FLAG --> FAILS
    FLAG --> WORKS
```

**Sources:** [tensordict/_lazy.py:444-456](), [tensordict/_lazy.py:161-173]()

## Batch Size and Device Semantics

### Batch Size Invariants

All tensors in a TensorDict must share the leading `N` dimensions defined by `batch_size`:

| TensorDict State | Tensor Shape Requirements | Example |
|------------------|---------------------------|---------|
| `batch_size=[3, 4]` | All tensors start with `[3, 4, ...]` | `[3, 4, 5]`, `[3, 4]`, `[3, 4, 10, 20]` |
| `batch_size=[]` | Tensors can have any shape | `[]`, `[5]`, `[10, 20]` |
| Nested TD | Nested TD must have compatible batch_size | Parent `[3, 4]`, child `[3, 4]` or `[3, 4, 5]` |

**Sources:** [tensordict/base.py:301-302]()

### Device Management

Device behavior depends on whether a device is specified:

```mermaid
graph TB
    subgraph "Device Scenarios"
        NO_DEV["device=None<br/>Multi-device allowed"]
        HAS_DEV["device='cuda:0'<br/>All tensors on device"]
    end
    
    subgraph "Set Behavior"
        NO_DEV_SET["Tensor stored as-is<br/>No device enforcement"]
        HAS_DEV_SET["Tensor cast to device<br/>td.to(device) automatic"]
    end
    
    subgraph "Get Behavior"
        NO_DEV_GET["Return tensor on<br/>original device"]
        HAS_DEV_GET["Return tensor on<br/>tensordict device"]
    end
    
    NO_DEV --> NO_DEV_SET
    NO_DEV --> NO_DEV_GET
    HAS_DEV --> HAS_DEV_SET
    HAS_DEV --> HAS_DEV_GET
```

**Sources:** [tensordict/_td.py:254-257](), [tensordict/_td.py:778-794]()

Device auto-indexing for CUDA:
- `device="cuda"` → `device="cuda:X"` where X is `torch.cuda.current_device()` [tensordict/_td.py:280-286]()
- Other device types (cpu, meta) handled without indexing [tensordict/_td.py:285-286]()

## Nested Keys and Recursive Structure

TensorDict supports nested structures through tuple keys:

```mermaid
graph TB
    subgraph "Flat vs Nested Keys"
        FLAT["Flat: td['a'] = tensor"]
        NESTED["Nested: td['a', 'b', 'c'] = tensor"]
    end
    
    subgraph "Storage Structure"
        ROOT["Root TensorDict<br/>_tensordict={'a': ...}"]
        LEVEL1["Nested TensorDict<br/>_tensordict={'b': ...}"]
        LEVEL2["Nested TensorDict<br/>_tensordict={'c': tensor}"]
    end
    
    subgraph "Access Methods"
        GET_TUPLE["_get_tuple(('a', 'b', 'c'))"]
        GET_CHAIN["td.get('a').get('b').get('c')"]
        BRACKET["td['a', 'b', 'c']"]
    end
    
    NESTED --> ROOT
    ROOT --> LEVEL1
    LEVEL1 --> LEVEL2
    
    GET_TUPLE --> ROOT
    GET_CHAIN --> ROOT
    BRACKET --> GET_TUPLE
```

**Sources:** [tensordict/base.py:559-571](), [tensordict/_td.py:843-857]()

Key access patterns:
- **String Key**: `td["key"]` → direct lookup in `_tensordict` [tensordict/_td.py]()
- **Tuple Key**: `td["a", "b"]` → recursive descent: `td.get("a").get("b")` [tensordict/base.py]()
- **Tuple of Length 1**: `td[("key",)]` → treated as string key [tensordict/base.py]()

## Internal State and Flags

TensorDict maintains several boolean flags to track state:

| Flag | Purpose | Set By | Effect |
|------|---------|--------|--------|
| `_is_locked` | Prevents structural changes | `lock_()` | Blocks new keys, allows in-place updates |
| `_is_shared` | Shared memory status | `share_memory_()` | Marks tensors in shared memory |
| `_is_memmap` | Memory-mapped status | `memmap_()` | Marks tensors as memory-mapped |
| `_is_vmapped` | Hidden vmap dimension | `_add_batch_dim()` | For functorch vmap integration |
| `_cache` | Cached computations | Various | Memoization of expensive operations |

**Sources:** [tensordict/_td.py:246-248](), [tensordict/base.py:303-312]()

### Locking Behavior

```mermaid
graph TB
    UNLOCKED["Unlocked State<br/>_is_locked=False"]
    LOCKED["Locked State<br/>_is_locked=True"]
    
    subgraph "Allowed When Locked"
        INPLACE["In-place updates<br/>td.set('key', value, inplace=True)"]
        INDEX["Indexing<br/>td[0] = other"]
        READ["Read operations<br/>td.get('key')"]
    end
    
    subgraph "Blocked When Locked"
        NEW_KEY["New keys<br/>td['new_key'] = value"]
        DELETE["Delete keys<br/>del td['key']"]
        UPDATE["Structural updates<br/>td.update(other)"]
    end
    
    UNLOCKED -->|"lock_()"| LOCKED
    LOCKED -->|"unlock_()"| UNLOCKED
    
    LOCKED --> INPLACE
    LOCKED --> INDEX
    LOCKED --> READ
    LOCKED --> |"Raises RuntimeError"| NEW_KEY
    LOCKED --> |"Raises RuntimeError"| DELETE
    LOCKED --> |"Raises RuntimeError"| UPDATE
```

**Sources:** [tensordict/base.py:307](), [tensordict/utils.py]() (_LOCK_ERROR constant)

## SubTensorDict: Indexed Views

`_SubTensorDict` provides a lazy indexed view over a parent TensorDict without copying data:

```mermaid
graph LR
    subgraph "SubTensorDict"
        SUB["_SubTensorDict"]
        SOURCE["_source: TensorDictBase<br/>Parent tensordict"]
        IDX["_idx: IndexType<br/>Index tuple"]
    end
    
    subgraph "Operations"
        GET["get(key)<br/>parent[idx].get(key)"]
        SET["set(key, value)<br/>parent.set_at_(key, value, idx)"]
    end
    
    PARENT["TensorDict<br/>batch_size=[10, 20]"]
    
    PARENT -->|"td[5]"| SUB
    SUB --> SOURCE
    SUB --> IDX
    SUB --> GET
    SUB --> SET
    GET --> PARENT
    SET --> PARENT
```

**Sources:** [tensordict/_td.py]() (_SubTensorDict class), [tensordict/base.py:633-637]()

SubTensorDict behavior:
- **Lazy Evaluation**: No data copied until materialized [tensordict/base.py:633-637]()
- **Pass-through Writes**: Sets propagate to parent via indexed assignment [tensordict/_td.py]()
- **Batch Size**: Computed from parent batch_size and index [tensordict/utils.py]() (_getitem_batch_size)

## Key Design Decisions

### 1. Eager vs Lazy Evaluation

| Implementation | Strategy | Use Case |
|----------------|----------|----------|
| `TensorDict` | Eager | General-purpose, small-medium data |
| `LazyStackedTensorDict` | Lazy stacking | Collections of TensorDicts, memory efficiency |
| `_SubTensorDict` | Lazy indexing | Views without copying |
| `PersistentTensorDict` | Lazy loading | Large datasets on disk |

**Sources:** [tensordict/_td.py:150-243](), [tensordict/_lazy.py:176-225]()

### 2. String-Only Top-Level Keys

Top-level keys must be strings, but nested access uses tuples:

```python
td["key"]           # Valid: string key
td[("a", "b")]      # Valid: nested tuple key
td[(0, "a")]        # Invalid: mixed type
```

This design prevents ambiguity between batch indexing and key access.

**Sources:** [tensordict/utils.py]() (_StringOnlyDict), [tensordict/base.py:559-571]()

### 3. Inplace Semantics

The `inplace` parameter has three modes:
- `inplace=False`: Always create new tensor (default for new keys)
- `inplace=True`: Must modify existing tensor (raises if key missing)
- `inplace=BEST_ATTEMPT_INPLACE`: Modify if exists, create if not

**Sources:** [tensordict/base.py:171-178]()

### 4. Validation and Type Coercion

Values undergo validation and coercion:
1. Python primitives → `torch.Tensor`
2. NumPy arrays → `torch.Tensor`
3. Dicts → nested `TensorDict`
4. Device casting if tensordict has device
5. Shape validation against `batch_size`

**Sources:** [tensordict/base.py]() (_validate_value methods)

---

**Primary Sources:**
- [tensordict/base.py:1-2000]()
- [tensordict/_td.py:1-2000]()
- [tensordict/_lazy.py:1-2000]()
- [test/test_tensordict.py:1-1000]()

---

