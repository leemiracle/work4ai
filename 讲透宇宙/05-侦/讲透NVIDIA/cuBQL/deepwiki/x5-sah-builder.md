<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuBQL · extra page SAH Builder · fetched 2026-10-26 -->

# SAH Builder

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cuBQL/builder/cuda/gpu_builder.h](cuBQL/builder/cuda/gpu_builder.h)
- [cuBQL/builder/cuda/sah_builder.h](cuBQL/builder/cuda/sah_builder.h)

</details>



## Purpose and Scope

The SAH Builder constructs high-quality BVHs optimized for ray tracing applications using the Surface Area Heuristic (SAH). This builder evaluates multiple split candidates across each axis and selects splits that minimize the expected ray traversal cost. It produces trees with better spatial partitioning than simpler builders like the radix builder, at the cost of longer construction time.

This document covers the SAH builder implementation, algorithm phases, data structures, and integration with the dispatcher. For general BVH construction concepts, see [Builder Algorithms](#6.2). For the fast spatial median builder, see [Radix Builder](#6.2.1). For configuration options, see [BuildConfig](#5.3).

**Sources**: [cuBQL/builder/cuda/sah_builder.h:1-581](), [cuBQL/builder/cuda/gpu_builder.h:31-42]()

---

## Overview

The SAH builder is selected by setting `BuildConfig::buildMethod = BuildConfig::SAH` and is currently restricted to 3-dimensional data with `float` or `double` coordinate types. The dispatcher in `gpuBuilder` performs type checking and routing to the SAH implementation.

### When to Use SAH Builder

| Use Case | SAH Builder | Radix Builder |
|----------|-------------|---------------|
| Ray tracing applications | ✓ Optimal | Limited quality |
| Real-time construction | Limited (slower) | ✓ Fast |
| k-NN spatial queries | Good | ✓ Better |
| High-quality offline builds | ✓ Optimal | Acceptable |
| Non-3D or non-float data | ✗ Not supported | ✓ Supported |

The SAH builder typically produces BVHs with 20-40% better ray tracing performance compared to spatial median builders, but requires approximately 2-5× longer construction time.

**Sources**: [cuBQL/builder/cuda/gpu_builder.h:31-42](), [cuBQL/builder/cuda/sah_builder.h:393-399]()

---

## Builder Dispatch and Type Restrictions

```mermaid
graph TB
    subgraph "gpuBuilder Dispatcher"
        GP["gpuBuilder&lt;T,D&gt;"]
        CHK{"BuildConfig::SAH?"}
        TYPE{"is3f&lt;T,D&gt;::value?"}
    end
    
    subgraph "Type Validation"
        IS3F["is3f&lt;float,3&gt;::value = true"]
        NOT3F["is3f&lt;T,D&gt;::value = false"]
    end
    
    subgraph "SAH Implementation"
        CAST["Type cast to BinaryBVH&lt;float,3&gt;"]
        SAHIMPL["sahBuilder_impl::sahBuilder"]
        REAL3["real3_sahBuilder&lt;T&gt;"]
        F3["Template specialization<br/>BinaryBVH&lt;float,3&gt;"]
        D3["Template specialization<br/>BinaryBVH&lt;double,3&gt;"]
    end
    
    ERR["throw runtime_error:<br/>'SAH builder not supported<br/>for this type of BVH'"]
    
    GP --> CHK
    CHK -->|Yes| TYPE
    CHK -->|No| OTHER["radixBuilder or elhBuilder"]
    
    TYPE --> IS3F
    TYPE --> NOT3F
    
    IS3F --> CAST
    NOT3F --> ERR
    
    CAST --> SAHIMPL
    SAHIMPL --> F3
    SAHIMPL --> D3
    F3 --> REAL3
    D3 --> REAL3
```

The dispatcher uses the `is3f<T,D>` template trait to validate types at compile time. Only `float` and `double` types with dimension `D=3` pass validation. The implementation casts the BVH reference to the appropriate specialized type before invoking the builder.

**Sources**: [cuBQL/builder/cuda/gpu_builder.h:13-42](), [cuBQL/builder/cuda/sah_builder.h:393-399](), [cuBQL/builder/cuda/sah_builder.h:548-564]()

---

## Key Data Structures

### TempNode Structure

The `TempNode<box_t>` union represents intermediate node states during construction. It uses a discriminated union to minimize memory footprint while storing different information for each node state.

```mermaid
graph LR
    subgraph "TempNode Union"
        UNION["TempNode&lt;box_t&gt;<br/>16-byte aligned"]
        
        subgraph "openBranch Variant"
            OB_CB["centBounds: AtomicBox"]
            OB_CNT["count: uint32_t"]
        end
        
        subgraph "openNode Variant"
            ON_CB["centBounds: AtomicBox"]
            ON_OFF["offset: uint32_t"]
            ON_DIM["dim: int8_t"]
            ON_BIN["bin: int8_t"]
            ON_ATOMIC["atomicSideDeciderBits: int32_t"]
        end
        
        subgraph "doneNode Variant"
            DN_OFF["offset: uint32_t"]
            DN_CNT["count: uint32_t"]
        end
    end
    
    UNION --> OB_CB
    UNION --> ON_CB
    UNION --> DN_OFF
```

| Variant | Purpose | Fields |
|---------|---------|--------|
| `openBranch` | Active node collecting primitives | `centBounds`, `count` |
| `openNode` | Node ready to split | `centBounds`, `offset`, `dim`, `bin`, `atomicSideDeciderBits` |
| `doneNode` | Finalized leaf node | `offset`, `count` |

The `centBounds` field stores the bounding box of primitive centroids (not the primitives themselves) for computing split positions.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:20-46]()

### SAHBins Structure

The `SAHBins<box_t>` structure maintains binning information for split evaluation across all three spatial dimensions.

```mermaid
graph TB
    subgraph "SAHBins Structure"
        SAHB["SAHBins&lt;box_t&gt;"]
        
        subgraph "dims[3] Array"
            D0["dims[0]: X-axis"]
            D1["dims[1]: Y-axis"]
            D2["dims[2]: Z-axis"]
        end
        
        subgraph "Each Dimension"
            B0["bins[0]"]
            B1["bins[1]"]
            BDOTS["..."]
            B15["bins[15]"]
        end
        
        subgraph "Each Bin (16-byte aligned)"
            BOUNDS["bounds: AtomicBox"]
            COUNT["count: int"]
        end
    end
    
    SAHB --> D0
    SAHB --> D1
    SAHB --> D2
    
    D0 --> B0
    D0 --> B1
    D0 --> BDOTS
    D0 --> B15
    
    B0 --> BOUNDS
    B0 --> COUNT
```

The structure uses 16 bins per dimension (constant `numBins = 16`), resulting in 48 total bins per node. Each bin accumulates:
- `bounds`: Spatial extent of primitives whose centroids fall in this bin
- `count`: Number of primitives in this bin

**Sources**: [cuBQL/builder/cuda/sah_builder.h:48-57]()

---

## Algorithm Phases

The SAH builder executes a multi-phase algorithm with iterative refinement. Each phase launches GPU kernels that operate on temporary data structures.

```mermaid
graph TD
    START["Input: boxes[numPrims]"]
    
    subgraph "Phase 1: Initialization"
        INIT["initState kernel:<br/>Initialize buildState, nodeStates[0:1]<br/>Set root as OPEN_BRANCH"]
        INITP["initPrims kernel:<br/>Initialize primStates[numPrims]<br/>Filter invalid boxes<br/>Accumulate to root centBounds"]
    end
    
    subgraph "Phase 2: Iterative Refinement Loop"
        DLNUM["Download buildState->numNodes<br/>to host"]
        CHECK{"numNodes == numDone?"}
        
        CLOSE["closeOpenNodes kernel:<br/>Convert OPEN_NODE -> DONE_NODE<br/>from previous iteration"]
        
        subgraph "SAH Processing Block"
            BATCH["Process nodes in batches<br/>of maxActiveSAHs"]
            CLEAR["clearBins kernel:<br/>Reset SAHBins for batch"]
            BIN["binPrims kernel:<br/>Accumulate prims into bins"]
            SELECT["selectSplits kernel:<br/>Evaluate SAH cost<br/>Choose split or make leaf"]
        end
        
        UPDATE["updatePrims kernel:<br/>Move prims to child nodes<br/>or mark done"]
    end
    
    subgraph "Phase 3: Sort and Finalize"
        SORT["cub::DeviceRadixSort:<br/>Sort primStates by nodeID"]
        WRITE["writePrimsAndLeafOffsets kernel:<br/>Extract primIDs array<br/>Set leaf offsets"]
        NODES["writeNodes kernel:<br/>Copy TempNode -> BinaryBVH::Node"]
    end
    
    REFIT["gpuBuilder_impl::refit:<br/>Bottom-up bounds tightening"]
    
    START --> INIT
    INIT --> INITP
    INITP --> DLNUM
    
    DLNUM --> CHECK
    CHECK -->|Yes: Done| SORT
    CHECK -->|No: Continue| CLOSE
    
    CLOSE --> BATCH
    BATCH --> CLEAR
    CLEAR --> BIN
    BIN --> SELECT
    SELECT --> UPDATE
    UPDATE --> DLNUM
    
    SORT --> WRITE
    WRITE --> NODES
    NODES --> REFIT
    REFIT --> END["Output: BinaryBVH"]
```

**Sources**: [cuBQL/builder/cuda/sah_builder.h:401-546]()

---

## Phase 1: Initialization

### initState Kernel

The `initState` kernel initializes the build state with a root node and a dummy node:

```mermaid
graph LR
    subgraph "Initial Node Configuration"
        N0["nodes[0]:<br/>OPEN_BRANCH<br/>count=0<br/>centBounds=empty"]
        N1["nodes[1]:<br/>DONE_NODE<br/>offset=0<br/>count=0"]
        BS["buildState->numNodes = 2"]
    end
    
    INIT["initState<<<1,1>>>"] --> N0
    INIT --> N1
    INIT --> BS
```

Node 0 serves as the root, while node 1 is a placeholder that remains unused.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:104-120](), [cuBQL/builder/cuda/sah_builder.h:426-429]()

### initPrims Kernel

The `initPrims` kernel processes each primitive in parallel:

| Operation | Description |
|-----------|-------------|
| Validity check | If `box.lower <= box.upper`, primitive is valid |
| Valid primitives | Assigned `nodeID=0`, `done=false`, added to root via `atomicAdd` and `atomic_grow` |
| Invalid primitives | Assigned `nodeID=(uint32_t)-1`, `done=true`, excluded from tree |

The kernel accumulates the centroid bounds of all valid primitives into `nodes[0].openBranch.centBounds` using atomic operations.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:122-146](), [cuBQL/builder/cuda/sah_builder.h:430-433]()

---

## Phase 2: Iterative Refinement Loop

The main construction loop continues until all nodes are finalized. Each iteration processes active nodes in batches constrained by `maxActiveSAHs`, the maximum number of concurrent SAH evaluations.

### Batch Size Calculation

```cpp
int maxActiveSAHs = 4 + numPrims / (8 * SAHBins<box_t<T,D>>::numBins);
```

This formula limits memory usage for SAH bins. Typical values:
- 1M primitives: ~8,200 nodes per batch
- 10M primitives: ~78,000 nodes per batch

**Sources**: [cuBQL/builder/cuda/sah_builder.h:419](), [cuBQL/builder/cuda/sah_builder.h:458-461]()

### closeOpenNodes Kernel

Before processing a new wave of nodes, `closeOpenNodes` converts `OPEN_NODE` states from the previous iteration to `DONE_NODE`. This occurs when a node was marked for splitting but never received primitives (degenerate case).

**Sources**: [cuBQL/builder/cuda/sah_builder.h:203-228](), [cuBQL/builder/cuda/sah_builder.h:446-448]()

### clearBins Kernel

For each batch of nodes, `clearBins` resets the SAH bin arrays:

```mermaid
graph LR
    CLEAR["clearBins<<<divRoundUp(numSAH,32), 32>>>"]
    
    subgraph "Per Thread tid"
        LOOP["for d in [0,1,2]:<br/>  for b in [0,15]:<br/>    sahBins[tid].dims[d].bins[b].count = 0<br/>    sahBins[tid].dims[d].bins[b].bounds.set_empty()"]
    end
    
    CLEAR --> LOOP
```

**Sources**: [cuBQL/builder/cuda/sah_builder.h:362-375](), [cuBQL/builder/cuda/sah_builder.h:463-464]()

### binPrims Kernel

The `binPrims` kernel distributes primitives into SAH bins across all three dimensions:

```mermaid
graph TB
    START["binPrims: primID thread"]
    GETPS["ps = primStates[primID]"]
    CHECKDONE{"ps.done?"}
    CHECKRANGE{"nodeID in<br/>[sahNodeBegin, sahNodeEnd)?"}
    
    GETBOX["primBox = primBoxes[primID]"]
    GETCENT["centBounds = nodes[nodeID]<br/>.openBranch.centBounds"]
    
    subgraph "For Each Dimension d=0,1,2"
        CALCREL["rel = (prim_d - lo) / (hi - lo)"]
        CALCBIN["bin = int(rel * numBins)<br/>clamped to [0, 15]"]
        GROW["atomic_grow(sahBins[nodeID].dims[d].bins[bin].bounds, primBox)"]
        ADD["atomicAdd(&sahBins[nodeID].dims[d].bins[bin].count, 1)"]
    end
    
    START --> GETPS
    GETPS --> CHECKDONE
    CHECKDONE -->|Yes| RETURN["return"]
    CHECKDONE -->|No| CHECKRANGE
    CHECKRANGE -->|No| RETURN
    CHECKRANGE -->|Yes| GETBOX
    GETBOX --> GETCENT
    GETCENT --> CALCREL
    CALCREL --> CALCBIN
    CALCBIN --> GROW
    GROW --> ADD
```

The binning formula computes the relative position of each primitive's centroid within the node's centroid bounds and maps it to a bin index. The use of `1e-20f` in the denominator prevents division by zero for degenerate cases.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:148-201](), [cuBQL/builder/cuda/sah_builder.h:469-472]()

---

## SAH Cost Evaluation

The `evaluateSAH` device function computes the optimal split plane by evaluating all possible split positions across three dimensions.

### Cost Formula

For each candidate split at bin `b` in dimension `d`, the cost is:

```
cost = surfaceArea(leftBox) * leftCount + surfaceArea(rightBox) * rightCount
```

The function also considers making a leaf node with cost:

```
leafCost = surfaceArea(nodeBounds) * totalCount
```

A leaf is created if:
1. `leafCost < bestCost`, AND
2. `totalCount <= maxAllowedLeafSize`

### Evaluation Algorithm

```mermaid
graph TD
    START["evaluateSAH"]
    INITBEST["bestCost = infinity<br/>splitDim = -1"]
    
    subgraph "For Each Dimension d"
        RPASS["Right-to-left pass:<br/>Accumulate rAreas[b]<br/>rCount = sum of bins[b:15]"]
        LEAFTEST{"totalCount <= maxAllowedLeafSize<br/>AND leafCost < bestCost?"}
        LPASS["Left-to-right pass:<br/>For each bin b:<br/>  Compute lArea, lCount<br/>  Compute rArea, rCount<br/>  Evaluate cost"]
        CMPBEST{"cost < bestCost?"}
        UPDATEBEST["bestCost = cost<br/>splitDim = d<br/>splitBin = b"]
    end
    
    START --> INITBEST
    INITBEST --> RPASS
    RPASS --> LEAFTEST
    LEAFTEST -->|Yes| MARKLEAF["splitDim = -1"]
    LEAFTEST -->|No| LPASS
    MARKLEAF --> LPASS
    LPASS --> CMPBEST
    CMPBEST -->|Yes| UPDATEBEST
    CMPBEST -->|No| LPASS
    UPDATEBEST --> LPASS
```

The two-pass approach (right-to-left precomputation followed by left-to-right evaluation) allows constant-time cost computation for each split candidate. Surface area is computed via the `surfaceArea` function on `box_t<T,D>` types.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:59-102]()

---

## selectSplits Kernel

The `selectSplits` kernel processes each active node to determine its fate: become a leaf or split into children.

```mermaid
graph TB
    SELECT["selectSplits: nodeID thread"]
    GETCOUNT["count = nodes[nodeID]<br/>.openBranch.count"]
    CHECKSPLIT{"count > makeLeafThreshold?"}
    
    EVALSAH["evaluateSAH:<br/>splitDim, splitBin"]
    CHECKLEAF{"splitDim < 0<br/>AND count <= maxAllowedLeafSize?"}
    
    subgraph "Make Leaf Path"
        SETDONE["nodeStates[nodeID] = DONE_NODE"]
        SETCOUNT["nodes[nodeID].doneNode.count = count"]
        SETOFF["nodes[nodeID].doneNode.offset = -1"]
    end
    
    subgraph "Make Inner Path"
        SETOPEN["nodeStates[nodeID] = OPEN_NODE"]
        STOREDIM["nodes[nodeID].openNode.dim = splitDim<br/>nodes[nodeID].openNode.bin = splitBin"]
        ALLOCCHILDREN["offset = atomicAdd(&buildState->numNodes, 2)"]
        INITCHILDREN["For side in [0,1]:<br/>  childID = offset + side<br/>  nodeStates[childID] = OPEN_BRANCH<br/>  nodes[childID].openBranch.count = 0<br/>  nodes[childID].openBranch.centBounds.set_empty()"]
    end
    
    SELECT --> GETCOUNT
    GETCOUNT --> CHECKSPLIT
    CHECKSPLIT -->|Yes| EVALSAH
    CHECKSPLIT -->|No| CHECKLEAF
    EVALSAH --> CHECKLEAF
    
    CHECKLEAF -->|Yes| SETDONE
    CHECKLEAF -->|No| SETOPEN
    
    SETDONE --> SETCOUNT
    SETCOUNT --> SETOFF
    
    SETOPEN --> STOREDIM
    STOREDIM --> ALLOCCHILDREN
    ALLOCCHILDREN --> INITCHILDREN
```

**Key Fields**:
- `openNode.dim`: Split dimension (0, 1, 2, or -1 for degenerate case)
- `openNode.bin`: Split bin index [0, 15]
- `openNode.offset`: Index of first child in `nodes` array
- `doneNode.offset`: Set to `(uint32_t)-1` initially; later atomically minimized by primitives

**Sources**: [cuBQL/builder/cuda/sah_builder.h:230-285](), [cuBQL/builder/cuda/sah_builder.h:477-481]()

---

## updatePrims Kernel

The `updatePrims` kernel reassigns each active primitive to its appropriate child node or marks it as done.

### Side Selection Logic

```mermaid
graph TB
    UPDATE["updatePrims: primID thread"]
    GETSTATE["nodeState = nodeStates[primState.nodeID]"]
    CHECKDONE{"nodeState == DONE_NODE?"}
    
    GETOPEN["openNode = nodes[primState.nodeID].openNode"]
    CHECKDIM{"openNode.dim == -1?"}
    
    subgraph "Degenerate Case"
        ATOMIC["side = atomicAdd(&openNode.atomicSideDeciderBits, 1) & 1"]
    end
    
    subgraph "Normal Split"
        CALCBIN["Recompute primitive's bin<br/>in split dimension"]
        CMP["side = (prim_bin >= openNode.bin) ? 1 : 0"]
    end
    
    ASSIGN["newNodeID = openNode.offset + side<br/>atomicAdd(&nodes[newNodeID].openBranch.count, 1)<br/>atomic_grow(nodes[newNodeID].openBranch.centBounds, primBox.center())<br/>primState.nodeID = newNodeID"]
    
    UPDATE --> GETSTATE
    GETSTATE --> CHECKDONE
    CHECKDONE -->|Yes| MARKDONE["primState.done = true<br/>return"]
    CHECKDONE -->|No| GETOPEN
    GETOPEN --> CHECKDIM
    CHECKDIM -->|Yes| ATOMIC
    CHECKDIM -->|No| CALCBIN
    CALCBIN --> CMP
    ATOMIC --> ASSIGN
    CMP --> ASSIGN
```

**Degenerate Case Handling**: When `dim == -1`, all primitives have identical centroids along every axis. The kernel distributes them evenly between children using an atomic counter to alternate assignments.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:287-335](), [cuBQL/builder/cuda/sah_builder.h:494-496]()

---

## Phase 3: Sort and Finalize

### Radix Sort by Node ID

After all primitives are assigned to leaf nodes, the `PrimState` array is sorted by `nodeID` using CUB's `DeviceRadixSort`. The `PrimState` structure is 64 bits:

```
PrimState:
  [63:32] = nodeID (sort key)
  [31:0]  = primID (value)
```

The sort operates on bits 32-63 to group primitives by their leaf node.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:501-519]()

### writePrimsAndLeafOffsets Kernel

This kernel performs two operations in a single pass:

```mermaid
graph LR
    WRITE["writePrimsAndLeafOffsets:<br/>offset thread"]
    
    subgraph "Operation 1"
        EXTRACT["bvhItemList[offset] = primStates[offset].primID"]
    end
    
    subgraph "Operation 2"
        CHECKVALID{"primStates[offset].nodeID >= 0?"}
        ATOMICMIN["atomicMin(&nodes[nodeID].doneNode.offset, offset)"]
    end
    
    WRITE --> EXTRACT
    WRITE --> CHECKVALID
    CHECKVALID -->|Yes| ATOMICMIN
```

**Operation 1**: Extracts primitive IDs into the final `bvh.primIDs` array in sorted order.

**Operation 2**: Uses `atomicMin` to set each leaf node's offset to the first occurrence of its node ID in the sorted array. This works because the array is sorted by node ID, so the minimum offset corresponds to the first primitive in each leaf.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:337-360](), [cuBQL/builder/cuda/sah_builder.h:525-528]()

### writeNodes Kernel

The `writeNodes` kernel copies administrative data from temporary nodes to the final `BinaryBVH::Node` structure:

```cpp
finalNodes[nodeID].admin.offset = tempNodes[nodeID].doneNode.offset;
finalNodes[nodeID].admin.count  = tempNodes[nodeID].doneNode.count;
```

Bounding box data is **not** written here; it will be computed in the subsequent refit phase.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:377-390](), [cuBQL/builder/cuda/sah_builder.h:534-536]()

---

## Memory Allocation and Cleanup

The SAH builder allocates several temporary arrays on the GPU:

| Array | Size | Purpose |
|-------|------|---------|
| `tempNodes` | `2 * numPrims` | Temporary node states during construction |
| `nodeStates` | `2 * numPrims` | Node state flags (OPEN_BRANCH, OPEN_NODE, DONE_NODE) |
| `primStates` | `numPrims` | Per-primitive state (nodeID, primID, done flag) |
| `buildState` | `1` | Global build state (node counter) |
| `sahBins` | `maxActiveSAHs` | SAH binning information for active nodes |
| `sortedPrimStates` | `numPrims` | Sorted copy for radix sort output |
| `d_temp_storage` | Variable | CUB temporary storage for radix sort |

All allocations use the provided `GpuMemoryResource` and are freed before the function returns. The `_ALLOC` and `_FREE` macros handle allocation/deallocation with proper error checking.

**Sources**: [cuBQL/builder/cuda/sah_builder.h:413-424](), [cuBQL/builder/cuda/sah_builder.h:537-543]()

---

## Integration with gpuBuilder

The SAH builder integrates into the main dispatch pipeline through type specialization:

```mermaid
graph TB
    DISP["gpuBuilder&lt;T,D&gt;(bvh, boxes, numBoxes,<br/>buildConfig, stream, memResource)"]
    
    CHECK{"buildConfig.buildMethod<br/>== BuildConfig::SAH?"}
    
    TYPECHECK{"is3f&lt;T,D&gt;::value?"}
    
    CAST["Cast to BinaryBVH&lt;float,3&gt; &"]
    
    CALL["sahBuilder_impl::sahBuilder"]
    
    SPEC{"Template specialization:<br/>float,3 or double,3?"}
    
    REAL3F["real3_sahBuilder&lt;float&gt;"]
    REAL3D["real3_sahBuilder&lt;double&gt;"]
    
    REFIT["gpuBuilder_impl::refit"]
    
    ERR["throw runtime_error"]
    
    DISP --> CHECK
    CHECK -->|Yes| TYPECHECK
    CHECK -->|No| OTHER["Other builders"]
    
    TYPECHECK -->|true| CAST
    TYPECHECK -->|false| ERR
    
    CAST --> CALL
    
    CALL --> SPEC
    SPEC -->|float,3| REAL3F
    SPEC -->|double,3| REAL3D
    
    REAL3F --> REFIT
    REAL3D --> REFIT
```

The dispatcher also sets default configuration values if not explicitly specified:

```cpp
if (buildConfig.makeLeafThreshold == 0)
    buildConfig.makeLeafThreshold = 1;
```

**Sources**: [cuBQL/builder/cuda/gpu_builder.h:31-42](), [cuBQL/builder/cuda/sah_builder.h:393-399](), [cuBQL/builder/cuda/sah_builder.h:548-564]()

---

## Configuration Parameters

The SAH builder respects the following `BuildConfig` fields:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `buildMethod` | `enum` | N/A | Must be `BuildConfig::SAH` |
| `makeLeafThreshold` | `int` | `1` | Minimum primitives to attempt splitting |
| `maxAllowedLeafSize` | `int` | `MAX_INT` | Maximum primitives per leaf node |

**makeLeafThreshold**: Nodes with count ≤ this value skip SAH evaluation and become leaves immediately (unless they exceed `maxAllowedLeafSize`).

**maxAllowedLeafSize**: Hard limit on leaf size. Even if the SAH cost favors a leaf, nodes exceeding this count must split.

**Sources**: [cuBQL/builder/cuda/gpu_builder.h:32-35](), [cuBQL/builder/cuda/sah_builder.h:250-256]()

---

## Performance Characteristics

### Complexity Analysis

| Metric | Complexity |
|--------|-----------|
| Time | O(N log N) expected, O(N²) worst case |
| Space | O(N) temporary storage |
| GPU Memory | ~16N bytes (temporary arrays) |
| Kernel Launches | O(log N) iterations × 5-10 kernels per iteration |

The iterative refinement typically requires 15-30 iterations for balanced scenes, depending on primitive distribution.

### Comparison with Radix Builder

```mermaid
graph LR
    subgraph "Build Time (10M prims)"
        RADIX_T["Radix: ~13ms"]
        SAH_T["SAH: ~30-50ms"]
    end
    
    subgraph "Traversal Quality (ray tracing)"
        RADIX_Q["Radix: Baseline"]
        SAH_Q["SAH: 20-40% fewer<br/>box intersections"]
    end
    
    subgraph "Memory Usage"
        RADIX_M["Radix: ~10N bytes"]
        SAH_M["SAH: ~16N bytes"]
    end
```

The SAH builder is recommended when:
- Ray tracing performance is critical
- Build time is not a bottleneck (offline or infrequent construction)
- Scene geometry is 3D with float or double precision

**Sources**: [cuBQL/builder/cuda/gpu_builder.h:43-48](), [cuBQL/builder/cuda/sah_builder.h:1-581]()

---

## Limitations and Future Work

### Current Limitations

1. **Type Restriction**: Only supports `float` and `double` with `D=3`
2. **Binning Resolution**: Fixed at 16 bins per dimension; may be suboptimal for highly non-uniform distributions
3. **Batch Processing**: Memory-constrained batching may increase iteration count for very large datasets
4. **No Spatial Splits**: Pure object partitioning; does not support splitting primitives across multiple leaves

### Extension Points

The SAH builder could be extended to:
- Support arbitrary dimension `D` by generalizing the binning loop
- Support integer coordinate types with appropriate bin calculation
- Adjust bin count based on primitive distribution
- Implement spatial splits for overlapping geometry

**Sources**: [cuBQL/builder/cuda/sah_builder.h:393-399](), [cuBQL/builder/cuda/sah_builder.h:48-57]()

---

