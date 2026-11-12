<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuBQL · extra page Fixed Ray Query · fetched 2026-10-26 -->

# Fixed Ray Query

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cuBQL/traversal/rayQueries.h](cuBQL/traversal/rayQueries.h)

</details>



## Purpose and Scope

This document describes the **fixed ray query** traversal template in cuBQL, which performs ray-BVH intersection queries where the ray's parametric interval `[tMin, tMax]` remains constant throughout traversal. Fixed ray queries are suitable for any-hit detection, shadow rays, and queries where the order of hits does not matter.

For ray queries where the parametric interval can shrink during traversal to find closest hits, see [Shrinking Ray Query](#7.1.2). For spatial ball queries using fixed or shrinking radii, see [Radius Queries](#7.2).

**Sources:** [cuBQL/traversal/rayQueries.h:18-69]()

---

## Overview

The `fixedRayQuery` namespace provides traversal templates that cast rays through a BVH without reordering child node traversal or shrinking the ray's parametric range. This design enables:

- **Unordered traversal**: Child nodes are visited in arbitrary order since hit distance does not affect which subtrees to explore
- **Constant ray interval**: `ray.tMin` and `ray.tMax` never change during traversal
- **Early termination**: User lambdas can signal to stop traversal immediately upon finding a satisfactory result
- **Any-hit semantics**: Useful for occlusion queries and shadow rays where any intersection suffices

The key distinction from shrinking ray queries is that fixed ray queries cannot prune subtrees based on previously found hits, as the search interval remains constant.

**Sources:** [cuBQL/traversal/rayQueries.h:18-22]()

---

## API Functions

### Fixed Ray Query Interface

```mermaid
graph TB
    subgraph "fixedRayQuery namespace"
        FL1["forEachLeaf(lambda, bvh, ray, dbg)"]
        FP1["forEachPrim(lambda, bvh, ray, dbg)"]
        
        FL2["forEachLeaf(lambda, bvh, AxisAlignedRay, dbg)"]
        FP2["forEachPrim(lambda, bvh, AxisAlignedRay, dbg)"]
    end
    
    subgraph "Input Types"
        RAY1["ray3f: General rays"]
        RAY2["AxisAlignedRay<axis,sign>: Axis-aligned rays"]
        BVH["bvh3f: BinaryBVH structure"]
        LAMBDA["Lambda: User callback"]
    end
    
    subgraph "Return Behavior"
        RET["Lambda returns:<br/>CUBQL_CONTINUE_TRAVERSAL<br/>CUBQL_TERMINATE_TRAVERSAL"]
    end
    
    RAY1 --> FL1
    RAY1 --> FP1
    RAY2 --> FL2
    RAY2 --> FP2
    BVH --> FL1
    BVH --> FP1
    BVH --> FL2
    BVH --> FP2
    LAMBDA --> FL1
    LAMBDA --> FP1
    LAMBDA --> FL2
    LAMBDA --> FP2
    
    FL1 --> RET
    FP1 --> RET
    FL2 --> RET
    FP2 --> RET
```

**Diagram: Fixed Ray Query API surface showing function overloads for general and axis-aligned rays**

The API provides four primary functions:

| Function | Ray Type | Invocation Target | Description |
|----------|----------|-------------------|-------------|
| `forEachLeaf` | `ray3f` | Leaf nodes | Invokes lambda once per leaf with array of primitive IDs |
| `forEachPrim` | `ray3f` | Individual primitives | Invokes lambda once per primitive ID within intersecting leaves |
| `forEachLeaf` | `AxisAlignedRay<axis,sign>` | Leaf nodes | Optimized traversal for axis-aligned rays |
| `forEachPrim` | `AxisAlignedRay<axis,sign>` | Individual primitives | Optimized primitive-level traversal for axis-aligned rays |

**Sources:** [cuBQL/traversal/rayQueries.h:24-68]()

---

## Function Signatures

### General Ray Traversal

```cpp
// Leaf-level callback
template<typename Lambda>
inline __cubql_both
void forEachLeaf(const Lambda &lambdaToExecuteForEachCandidate,
                 cuBQL::bvh3f bvh,
                 cuBQL::ray3f ray,
                 bool dbg=false);

// Primitive-level callback
template<typename Lambda>
inline __cubql_both
void forEachPrim(const Lambda &lambdaToExecuteForEachCandidate,
                 cuBQL::bvh3f bvh,
                 cuBQL::ray3f ray,
                 bool dbg=false);
```

### Axis-Aligned Ray Traversal

```cpp
// Leaf-level callback for axis-aligned rays
template<int axis, int sign, typename Lambda>
inline __cubql_both
void forEachLeaf(const Lambda &lambdaToExecuteForEachCandidate,
                 cuBQL::bvh3f bvh,
                 AxisAlignedRay<axis,sign> ray,
                 bool dbg=false);

// Primitive-level callback for axis-aligned rays
template<int axis, int sign, typename Lambda>
inline __cubql_both
void forEachPrim(const Lambda &lambdaToExecuteForEachCandidate,
                 cuBQL::bvh3f bvh,
                 AxisAlignedRay<axis,sign> ray,
                 bool dbg=false);
```

**Parameters:**
- `lambdaToExecuteForEachCandidate`: User-provided callback (see Lambda Interface below)
- `bvh`: BinaryBVH structure to traverse
- `ray`: Ray definition with origin, direction, tMin, and tMax
- `dbg`: Debug flag for diagnostic output (default: false)

**Sources:** [cuBQL/traversal/rayQueries.h:24-68]()

---

## Traversal Algorithm

### General Ray Traversal Flow

```mermaid
graph TD
    START["Start: Initialize stack with root node"]
    
    DESCEND["Descend Phase:<br/>Process current node"]
    
    INNER_CHECK{"Is node<br/>an inner node?<br/>(count == 0)"}
    
    FETCH_CHILDREN["Fetch children:<br/>n0 = nodes[offset+0]<br/>n1 = nodes[offset+1]"]
    
    INTERSECT["Test ray-box intersection:<br/>o0 = rayIntersectsBox(ray, n0.bounds)<br/>o1 = rayIntersectsBox(ray, n1.bounds)"]
    
    BOTH_HIT{"Both children<br/>intersect?"}
    ONE_HIT{"One child<br/>intersects?"}
    
    PUSH_STACK["Push one child to stack<br/>Set other as current node"]
    SET_NODE["Set intersecting child<br/>as current node"]
    DEAD_END["Mark as dead end<br/>(set count=0)"]
    
    LEAF_CHECK{"Is valid leaf?<br/>(count != 0)"}
    
    INVOKE_LAMBDA["Invoke lambda:<br/>result = lambda(primIDs+offset, count)"]
    
    TERMINATE_CHECK{"Lambda returned<br/>TERMINATE?"}
    
    POP_STACK["Pop next node from stack"]
    STACK_EMPTY{"Stack<br/>empty?"}
    
    RETURN["Return: Traversal complete"]
    
    START --> DESCEND
    DESCEND --> INNER_CHECK
    
    INNER_CHECK -->|Yes| FETCH_CHILDREN
    INNER_CHECK -->|No| LEAF_CHECK
    
    FETCH_CHILDREN --> INTERSECT
    INTERSECT --> BOTH_HIT
    
    BOTH_HIT -->|Yes| PUSH_STACK
    BOTH_HIT -->|No| ONE_HIT
    
    ONE_HIT -->|Yes| SET_NODE
    ONE_HIT -->|No| DEAD_END
    
    PUSH_STACK --> DESCEND
    SET_NODE --> DESCEND
    DEAD_END --> LEAF_CHECK
    
    LEAF_CHECK -->|Yes| INVOKE_LAMBDA
    LEAF_CHECK -->|No| POP_STACK
    
    INVOKE_LAMBDA --> TERMINATE_CHECK
    
    TERMINATE_CHECK -->|Yes| RETURN
    TERMINATE_CHECK -->|No| POP_STACK
    
    POP_STACK --> STACK_EMPTY
    STACK_EMPTY -->|Yes| RETURN
    STACK_EMPTY -->|No| DESCEND
```

**Diagram: Fixed ray query traversal algorithm showing stack-based iterative descent with ray-box intersection testing**

### Key Algorithm Characteristics

| Characteristic | Behavior |
|----------------|----------|
| **Traversal Order** | Unordered (children visited in arbitrary order) |
| **Stack Management** | 64-entry stack for node admin data |
| **Intersection Test** | `rayIntersectsBox(ray, box)` using slab method |
| **Ray Modification** | Ray parameters remain constant (no tMax shrinking) |
| **Termination** | Early exit when lambda returns `CUBQL_TERMINATE_TRAVERSAL` |
| **Dead Ends** | Nodes where both children fail intersection test |

**Sources:** [cuBQL/traversal/rayQueries.h:248-315]()

---

## Ray-Box Intersection

The core intersection test determines whether a ray intersects an axis-aligned bounding box:

```mermaid
graph LR
    RAY["Ray: origin, direction, tMin, tMax"]
    BOX["Box: lower, upper bounds"]
    
    COMPUTE_INV["Compute reciprocal direction:<br/>inv = rcp(ray.direction)"]
    
    COMPUTE_SLABS["Compute slab intersections:<br/>lo = (box.lower - ray.origin) * inv<br/>hi = (box.upper - ray.origin) * inv"]
    
    NEAR_FAR["Compute near/far:<br/>nr = min(lo, hi)<br/>fr = max(lo, hi)"]
    
    TIN_TOUT["Compute interval:<br/>tin = max(ray.tMin, reduce_max(nr))<br/>tout = min(ray.tMax, reduce_min(fr))"]
    
    TEST{"tin <= tout?"}
    
    HIT["Return: true<br/>(ray intersects box)"]
    MISS["Return: false<br/>(ray misses box)"]
    
    RAY --> COMPUTE_INV
    BOX --> COMPUTE_SLABS
    COMPUTE_INV --> COMPUTE_SLABS
    COMPUTE_SLABS --> NEAR_FAR
    NEAR_FAR --> TIN_TOUT
    TIN_TOUT --> TEST
    TEST -->|Yes| HIT
    TEST -->|No| MISS
```

**Diagram: Slab-based ray-box intersection algorithm using interval arithmetic**

The intersection test implementation uses the slab method, computing entry and exit distances for each axis and checking interval overlap:

**Sources:** [cuBQL/traversal/rayQueries.h:156-169]()

---

## Axis-Aligned Ray Optimization

For axis-aligned rays (rays parallel to a coordinate axis), fixed ray queries convert the ray to an axis-aligned bounding box and delegate to `fixedBoxQuery`:

```mermaid
graph TD
    AA_RAY["AxisAlignedRay<axis,sign>:<br/>origin, tMin, tMax"]
    
    COMPUTE_A["Compute endpoint A:<br/>A = origin + tMin * direction()"]
    COMPUTE_B["Compute endpoint B:<br/>B = origin + tMax * direction()"]
    
    CREATE_BOX["Create bounding box:<br/>rayAsBox = {min(A,B), max(A,B)}"]
    
    DELEGATE["Delegate to fixedBoxQuery:<br/>forEachLeaf(lambda, bvh, rayAsBox)"]
    
    AA_RAY --> COMPUTE_A
    AA_RAY --> COMPUTE_B
    COMPUTE_A --> CREATE_BOX
    COMPUTE_B --> CREATE_BOX
    CREATE_BOX --> DELEGATE
```

**Diagram: Axis-aligned ray traversal optimization that converts rays to boxes**

This optimization avoids the reciprocal direction computation and simplifies intersection tests to box-box overlaps.

**Sources:** [cuBQL/traversal/rayQueries.h:203-217]()

---

## Lambda Interface

### Lambda Signatures

Fixed ray queries support two callback patterns:

#### Leaf-Level Lambda

Invoked once per leaf node that intersects the ray:

```cpp
// Lambda signature for forEachLeaf
auto lambda = [](const uint32_t *leafPrims, size_t numPrims) -> int {
    // Process primitives in leaf
    // Return CUBQL_CONTINUE_TRAVERSAL or CUBQL_TERMINATE_TRAVERSAL
};
```

**Parameters:**
- `leafPrims`: Pointer to array of primitive IDs in the leaf (points to `bvh.primIDs + node.offset`)
- `numPrims`: Number of primitives in this leaf (value of `node.count`)

**Return Value:**
- `CUBQL_CONTINUE_TRAVERSAL`: Continue traversing remaining nodes
- `CUBQL_TERMINATE_TRAVERSAL`: Stop traversal immediately

#### Primitive-Level Lambda

Invoked once per primitive in leaves that intersect the ray:

```cpp
// Lambda signature for forEachPrim
auto lambda = [](uint32_t primID) -> int {
    // Process individual primitive
    // Return CUBQL_CONTINUE_TRAVERSAL or CUBQL_TERMINATE_TRAVERSAL
};
```

**Parameters:**
- `primID`: Single primitive ID from the leaf

**Return Value:**
- `CUBQL_CONTINUE_TRAVERSAL`: Continue processing remaining primitives and nodes
- `CUBQL_TERMINATE_TRAVERSAL`: Stop traversal immediately

**Sources:** [cuBQL/traversal/rayQueries.h:299-306](), [cuBQL/traversal/rayQueries.h:326-341]()

---

## Implementation Details

### Stack-Based Traversal

```mermaid
graph TB
    subgraph "Stack Structure"
        STACK["traversalStack[64]<br/>Array of node_t::Admin"]
        PTR["stackPtr:<br/>Points to next free slot"]
    end
    
    subgraph "Node Admin Fields"
        OFFSET["offset:<br/>Child node index<br/>or primitive offset"]
        COUNT["count:<br/>0 = inner node<br/>>0 = leaf with count prims"]
    end
    
    subgraph "Operations"
        PUSH["Push: *stackPtr++ = node.admin"]
        POP["Pop: node = *--stackPtr"]
        CHECK["Empty check: stackPtr == traversalStack"]
    end
    
    STACK --> PTR
    PTR --> PUSH
    PTR --> POP
    PTR --> CHECK
    
    OFFSET --> STACK
    COUNT --> STACK
```

**Diagram: Stack management for iterative BVH traversal using node administrative data**

The implementation uses a fixed-size stack of 64 entries to track nodes pending traversal. Each entry stores the `node_t::Admin` structure containing:
- `offset`: For inner nodes, index to first child; for leaves, offset into `primIDs` array
- `count`: Zero for inner nodes, primitive count for leaves

**Sources:** [cuBQL/traversal/rayQueries.h:255-259]()

---

### Child Node Processing

When both children of an inner node intersect the ray, the traversal:
1. Pushes one child's admin data to the stack
2. Sets the other child as the current node for immediate descent
3. No ordering is performed (arbitrary choice of which child to visit first)

```cpp
// From the implementation
bool o0 = rayIntersectsBox(ray,n0.bounds);
bool o1 = rayIntersectsBox(ray,n1.bounds);
if (o0) {
  if (o1) {
    *stackPtr++ = n1.admin;  // Push one child
  }
  node = n0.admin;  // Visit other child next
} else {
  if (o1) {
    node = n1.admin;
  } else {
    node.count = 0;  // Dead end
  }
}
```

**Sources:** [cuBQL/traversal/rayQueries.h:276-296]()

---

### Primitive-Level Wrapper

The `forEachPrim` functions wrap `forEachLeaf` with an intermediate lambda that iterates over primitives:

```mermaid
graph LR
    USER_LAMBDA["User's per-primitive lambda:<br/>lambda(primID)"]
    
    WRAPPER["Wrapper leaf lambda:<br/>Loops over leaf primitives"]
    
    FOREACH_LEAF["forEachLeaf:<br/>Core traversal implementation"]
    
    USER_LAMBDA --> WRAPPER
    WRAPPER --> FOREACH_LEAF
```

**Diagram: Primitive-level traversal implementation as wrapper around leaf-level traversal**

The wrapper lambda:
1. Receives a leaf's primitive array and count
2. Iterates over each primitive ID
3. Invokes the user lambda on each primitive
4. Returns `CUBQL_TERMINATE_TRAVERSAL` if any primitive lambda requests termination

**Sources:** [cuBQL/traversal/rayQueries.h:319-342]()

---

## Use Cases

### Shadow Ray Queries

Fixed ray queries are ideal for shadow rays where any intersection between a shading point and light source causes occlusion:

```cpp
bool isShadowed = false;
auto shadowLambda = [&](uint32_t primID) {
    if (rayIntersectsPrimitive(ray, primID)) {
        isShadowed = true;
        return CUBQL_TERMINATE_TRAVERSAL;
    }
    return CUBQL_CONTINUE_TRAVERSAL;
};
fixedRayQuery::forEachPrim(shadowLambda, bvh, shadowRay);
```

### Any-Hit Detection

Applications that need to detect whether a ray hits anything without caring about the closest hit:

```cpp
bool hasHit = false;
auto anyHitLambda = [&](const uint32_t *prims, size_t count) {
    hasHit = true;
    return CUBQL_TERMINATE_TRAVERSAL;
};
fixedRayQuery::forEachLeaf(anyHitLambda, bvh, ray);
```

### Batch Processing

When processing multiple rays where each ray's result is independent and order doesn't matter, fixed ray queries provide efficient unordered traversal without the overhead of maintaining sorted subtree access.

**Sources:** [cuBQL/traversal/rayQueries.h:18-22](), [cuBQL/traversal/rayQueries.h:38-45]()

---

## Comparison with Shrinking Ray Query

| Feature | Fixed Ray Query | Shrinking Ray Query |
|---------|----------------|---------------------|
| **Ray Interval** | Constant `[tMin, tMax]` | Shrinking `tMax` based on hits |
| **Traversal Order** | Unordered (arbitrary) | Front-to-back (ordered by hit distance) |
| **Use Case** | Any-hit, shadow rays, occlusion | Closest-hit, primary rays |
| **Pruning** | No dynamic pruning | Prunes subtrees beyond current hit |
| **Performance** | Lower overhead for any-hit | Better for closest-hit with distant hits |
| **Lambda Return** | Continue or terminate | Returns new `tMax` value |

For applications requiring closest-hit semantics or ray tracing where hits update the ray's valid interval, use [Shrinking Ray Query](#7.1.2) instead.

**Sources:** [cuBQL/traversal/rayQueries.h:18-22](), [cuBQL/traversal/rayQueries.h:71-75]()

---

## Performance Characteristics

### Computational Complexity

- **Stack depth**: Maximum 64 nodes (configurable)
- **Ray-box tests**: One test per inner node visited
- **Memory access pattern**: Sequential node array access with stack-based backtracking
- **Lambda invocations**: Once per intersecting leaf (or primitive for `forEachPrim`)

### Optimization Considerations

1. **Axis-aligned rays**: Automatically converted to box queries for efficiency
2. **Early termination**: Lambda-based termination avoids unnecessary traversal
3. **No sorting overhead**: Unordered traversal eliminates child node sorting costs
4. **Fixed stack**: No dynamic allocation during traversal

**Sources:** [cuBQL/traversal/rayQueries.h:255-259](), [cuBQL/traversal/rayQueries.h:203-217]()

---

