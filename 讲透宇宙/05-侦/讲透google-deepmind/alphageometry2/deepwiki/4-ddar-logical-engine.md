<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphageometry2 · page 4 DDAR Logical Engine · fetched 2026-10-26 -->

# DDAR Logical Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ddar.py](ddar.py)
- [elimination.py](elimination.py)
- [numericals.py](numericals.py)

</details>



## Purpose and Scope

The DDAR (Deductive Database for Automated Reasoning) logical engine is the core geometric reasoning system of AlphaGeometry2. This page documents the `DDAR` class in [ddar.py](), which serves as the central orchestrator for symbolic geometric reasoning. It maintains a database of geometric facts, translates predicates into algebraic constraints, performs iterative deductive inference, and verifies proof goals.

For information about the symbolic elimination systems that DDAR uses internally, see [Symbolic Elimination System](#5). For details about the numerical geometry primitives that support DDAR's calculations, see [Numerical Geometry Module](#6). For understanding how problems are parsed before being passed to DDAR, see [Problem Parsing and Data Structures](#7).

**Sources:** [ddar.py:1-87]()

## DDAR Class Overview

The `DDAR` class (defined at [ddar.py:66-1087]()) is initialized with a set of `AGPoint` objects and maintains three parallel representations of geometric knowledge:

1. **Symbolic constraint systems**: Three elimination systems for different algebraic domains
2. **Geometric object databases**: Collections of lines and circles with known relationships
3. **Lookup dictionaries**: Fast access structures mapping point pairs to geometric properties

```mermaid
graph TB
    subgraph "DDAR Class Structure"
        Init["__init__(points)<br/>[ddar.py:69-127]"]
        
        subgraph "Constraint Systems"
            ElimDistMul["elim_dist_mul<br/>ElimDistMul()<br/>Multiplicative distances"]
            ElimDistAdd["elim_dist_add<br/>ElimDistAdd()<br/>Additive distances"]
            ElimAngle["elim_angle<br/>ElimAngle()<br/>Angles"]
        end
        
        subgraph "Geometric Databases"
            Lines["lines: set[FormalLine]<br/>Collinear point groups"]
            Circles["circles: set[FormalCircle]<br/>Concyclic point groups"]
        end
        
        subgraph "Lookup Structures"
            PairToLine["pair_to_line<br/>dict[(AGPoint, AGPoint), FormalLine]"]
            PairToDistMul["pair_to_dist_mul<br/>dict[(AGPoint, AGPoint), DistMul]"]
            PairToDistAdd["pair_to_dist_add<br/>dict[(AGPoint, AGPoint), DistAdd]"]
            PairToDir["pair_to_dir<br/>dict[(AGPoint, AGPoint), FormalAngle]"]
        end
        
        subgraph "State Management"
            Points["points: list[AGPoint]<br/>Active points"]
            PointSubst["point_subst<br/>dict[AGPoint, AGPoint]<br/>Point equality tracking"]
        end
    end
    
    Init --> ElimDistMul
    Init --> ElimDistAdd
    Init --> ElimAngle
    Init --> Lines
    Init --> Circles
    Init --> PairToLine
    Init --> PairToDistMul
    Init --> PairToDistAdd
    Init --> PairToDir
    Init --> Points
    Init --> PointSubst
```

**Sources:** [ddar.py:66-127]()

## Core Data Structures

### Formal Geometric Objects

DDAR maintains two types of formal geometric objects that represent proven structural relationships:

| Class | Purpose | Key Attributes | Source |
|-------|---------|----------------|--------|
| `FormalLine` | Groups of collinear points | `points`, `main_pair`, `direction`, `value` | [ddar.py:33-48]() |
| `FormalCircle` | Groups of concyclic points | `defining_points`, `points`, `centers`, `value` | [ddar.py:50-64]() |

These objects are immutable and are replaced when new facts are discovered that extend them.

**Sources:** [ddar.py:33-64]()

### Point Pair Mappings

DDAR creates bidirectional mappings for every pair of numerically distinct points during initialization:

```mermaid
graph LR
    subgraph "For each point pair (a,b)"
        Dist["ng.distance(a.value, b.value)"]
        
        subgraph "Created Variables"
            DistMul["pair_to_dist_mul[a,b]<br/>DistMul variable<br/>log(|ab|)"]
            DistAdd["pair_to_dist_add[a,b]<br/>DistAdd variable<br/>|ab|"]
            Dir["pair_to_dir[a,b]<br/>FormalAngle variable<br/>direction(ab)"]
            Line["pair_to_line[a,b]<br/>FormalLine<br/>line through a,b"]
        end
    end
    
    Dist --> DistMul
    Dist --> DistAdd
    Dist --> Dir
    Dist --> Line
```

These mappings are symmetric: `pair_to_dist_mul[a,b]` and `pair_to_dist_mul[b,a]` reference the same variable.

**Sources:** [ddar.py:83-118]()

## Primary Operations

The DDAR class exposes three primary operations that external code uses:

### 1. Predicate Assertion: `force_pred`

Translates a geometric predicate into algebraic constraints and adds them to the database.

```mermaid
flowchart TD
    Input["force_pred(pred)<br/>[ddar.py:131-173]"]
    Replace["pred.replace_points(point_subst)<br/>Apply known point equalities"]
    
    Router{"pred.name?"}
    
    Coll["force_collinear(pred.points)<br/>[ddar.py:700-783]"]
    Angle["pred_to_angle(pred)<br/>[ddar.py:174-214]<br/>→ elim_angle.force_zero()"]
    DistMul["pred_to_dist_mul(pred)<br/>[ddar.py:216-245]<br/>→ elim_dist_mul.force_one()"]
    DistAdd["pred_to_dist_add(pred)<br/>[ddar.py:247-257]<br/>→ elim_dist_add.force_zero()"]
    Cyclic["force_concyclic(points, centers)<br/>[ddar.py:785-904]"]
    Overlap["force_equal_points(a, b)<br/>[ddar.py:937-1028]"]
    
    Input --> Replace
    Replace --> Router
    
    Router -->|"coll"| Coll
    Router -->|"angeq, para, perp,<br/>s_angle, aconst, eqangle"| Angle
    Router -->|"distmeq, cong,<br/>eqratio, rconst"| DistMul
    Router -->|"distseq"| DistAdd
    Router -->|"cyclic,<br/>cyclic_with_centers"| Cyclic
    Router -->|"overlap"| Overlap
```

**Sources:** [ddar.py:131-173](), [ddar.py:174-257]()

### 2. Deduction Closure: `deduction_closure`

Iteratively applies geometric inference rules until no new facts can be derived.

```mermaid
flowchart TD
    Start["deduction_closure(verbose, progress_dot)<br/>[ddar.py:301-357]"]
    Changed["changed = True"]
    Loop{"while changed"}
    
    UpdateCache["update_cache()<br/>[ddar.py:1036-1045]<br/>Simplify all pair mappings"]
    ResetChanged["changed = False"]
    
    Similar["search_similar(verbose)<br/>[ddar.py:359-438]<br/>Detect similar triangles"]
    Concyclic["search_concyclic()<br/>[ddar.py:440-481]<br/>Detect cyclic quads"]
    Circles["search_circles()<br/>[ddar.py:483-524]<br/>Detect equal radii"]
    Merge["merge_points()<br/>[ddar.py:526-580]<br/>Merge equal points"]
    TransferAddMul["transfer_dist_add_mul()<br/>[ddar.py:582-620]<br/>Sync distance systems"]
    TransferArcMul["transfer_dist_arc_mul()<br/>[ddar.py:622-649]<br/>Sync arcs/chords"]
    
    CheckChanged{"Any rule<br/>returned True?"}
    
    End["Return"]
    
    Start --> Changed
    Changed --> Loop
    Loop -->|"True"| UpdateCache
    UpdateCache --> ResetChanged
    ResetChanged --> Similar
    Similar --> Concyclic
    Concyclic --> Circles
    Circles --> Merge
    Merge --> TransferAddMul
    TransferAddMul --> TransferArcMul
    TransferArcMul --> CheckChanged
    CheckChanged -->|"Yes:<br/>changed = True"| Loop
    CheckChanged -->|"No"| Loop
    Loop -->|"False"| End
```

Each inference rule returns `True` if it discovered new facts, causing the loop to continue.

**Sources:** [ddar.py:301-357]()

### 3. Predicate Verification: `check_pred`

Queries the database to determine if a predicate is provably satisfied.

```mermaid
flowchart TD
    Input["check_pred(pred)<br/>[ddar.py:259-298]"]
    Replace["Replace points using point_subst<br/>(except for 'overlap')"]
    
    Router{"pred.name?"}
    
    CheckColl["check_collinear(points)<br/>[ddar.py:906-911]"]
    CheckAngle["pred_to_angle(pred)<br/>→ elim_angle.simplify()<br/>→ is_zero()?"]
    CheckDistMul["pred_to_dist_mul(pred)<br/>→ elim_dist_mul.simplify()<br/>→ is_one()?"]
    CheckDistAdd["pred_to_dist_add(pred)<br/>→ elim_dist_add.simplify()<br/>→ is_zero()?"]
    CheckCyclic["check_concyclic(points, centers)<br/>[ddar.py:913-933]"]
    CheckOverlap["check_equal_points(a, b)<br/>[ddar.py:1029-1032]"]
    CheckAcompute["Simplify angle and<br/>return value if constant"]
    
    Result["Return boolean or value"]
    
    Input --> Replace
    Replace --> Router
    
    Router -->|"coll"| CheckColl
    Router -->|"angeq, para, perp,<br/>s_angle, aconst, eqangle"| CheckAngle
    Router -->|"distmeq, cong,<br/>eqratio, rconst"| CheckDistMul
    Router -->|"distseq"| CheckDistAdd
    Router -->|"cyclic,<br/>cyclic_with_centers"| CheckCyclic
    Router -->|"overlap"| CheckOverlap
    Router -->|"acompute"| CheckAcompute
    
    CheckColl --> Result
    CheckAngle --> Result
    CheckDistMul --> Result
    CheckDistAdd --> Result
    CheckCyclic --> Result
    CheckOverlap --> Result
    CheckAcompute --> Result
```

**Sources:** [ddar.py:259-298]()

## Predicate Translation System

DDAR translates geometric predicates into three algebraic domains:

### Angle Predicates

The `pred_to_angle` method ([ddar.py:174-214]()) handles six predicate types:

| Predicate | Translation | Example |
|-----------|-------------|---------|
| `angeq` | Linear combination of angles equals constant | `angeq(A,B,C,D; coef1,coef2,const)` → `coef1·∠(AB) + coef2·∠(CD) = const·π` |
| `eqangle` | Angle equality | `eqangle(A,B,C,D,E,F,G,H)` → `∠(AB,CD) = ∠(EF,GH)` |
| `para` | Parallel lines | `para(A,B,C,D)` → `dir(AB) = dir(CD)` |
| `perp` | Perpendicular lines | `perp(A,B,C,D)` → `dir(AB) - dir(CD) = π/2` |
| `s_angle` | Signed angle | `s_angle(A,B,C,D; ang)` → `dir(AB) - dir(CD) = ang` |
| `aconst` | Angle constant | Same as `s_angle` |

**Sources:** [ddar.py:174-214]()

### Distance Ratio Predicates

The `pred_to_dist_mul` method ([ddar.py:216-245]()) handles multiplicative distance relationships:

| Predicate | Translation | Example |
|-----------|-------------|---------|
| `distmeq` | Product of distances | `distmeq(A,B,C,D; coef1,coef2,const)` → `\|AB\|^coef1 · \|CD\|^coef2 = const` |
| `cong` | Congruent segments | `cong(A,B,C,D)` → `\|AB\| = \|CD\|` |
| `rconst` | Ratio constant | `rconst(A,B,C,D; r)` → `\|AB\| / \|CD\| = r` |
| `eqratio` | Equal ratios | `eqratio(A,B,C,D,E,F,G,H)` → `\|AB\|/\|CD\| = \|EF\|/\|GH\|` |

These are converted to logarithmic form for linear algebra: `log(|AB|) + log(|CD|) = log(const)`.

**Sources:** [ddar.py:216-245]()

### Distance Sum Predicates

The `pred_to_dist_add` method ([ddar.py:247-257]()) handles additive distance relationships:

| Predicate | Translation |
|-----------|-------------|
| `distseq` | Linear combination of distances equals zero |

**Sources:** [ddar.py:247-257]()

## Geometric Inference Rules

DDAR implements four main categories of geometric inference that execute during deduction closure:

### Similar Triangle Detection

The `search_similar` method ([ddar.py:359-438]()) identifies similar triangles using four congruence criteria:

```mermaid
graph TB
    subgraph "search_similar Algorithm"
        Triangles["For each oriented triangle (a,b,c):<br/>- Check numerical non-degeneracy<br/>- Check if triangle was 'encountered'"]
        
        Compute["Compute signatures:<br/>- rat1 = |ab|/|ac|<br/>- ang1 = ∠(ab,ac)<br/>- rat2 = |cb|/|ca|<br/>- ang2 = ∠(cb,ca)<br/>- orient = orientation(a,b,c)"]
        
        subgraph "Match Against Four Dictionaries"
            SSS["sss[rat1, rat2]<br/>Side-Side-Side"]
            AA["aa[ang1, ang2]<br/>Angle-Angle<br/>(also aa[-ang1, -ang2])"]
            SAS["sas[ang1, rat1, orient]<br/>Side-Angle-Side<br/>(also sas[-ang1, rat1, -orient])"]
            SSA["ssa[ang, rat, orient]<br/>Side-Side-Angle<br/>(conditions apply)"]
        end
        
        Found["If match found:<br/>Add pair to similar_pairs"]
        ForceSimilar["For each similar pair:<br/>force_similar(triangle1, triangle2)<br/>[ddar.py:652-696]"]
    end
    
    Triangles --> Compute
    Compute --> SSS
    Compute --> AA
    Compute --> SAS
    Compute --> SSA
    SSS --> Found
    AA --> Found
    SAS --> Found
    SSA --> Found
    Found --> ForceSimilar
```

The `force_similar` method asserts four equality constraints per triangle pair:
1. Corresponding angles are equal (with sign depending on orientation)
2. Corresponding side ratios are equal

**Sources:** [ddar.py:359-438](), [ddar.py:652-696]()

### Cyclic Quadrilateral Detection

The `search_concyclic` method ([ddar.py:440-481]()) finds concyclic points by:

1. For each pair of points `(a,b)`, group all other points `c` by their inscribed angle `∠(cab)`
2. Points with equal inscribed angles lie on the same circle
3. Points with `|ca| = |cb|` can serve as circle centers (inscribed angle = half of arc)

```mermaid
flowchart TD
    Start["For each pair (a,b)"]
    GroupByAngle["For each point c:<br/>ang = ∠(cab)<br/>Group by ang"]
    
    CheckLine["If ang = 0:<br/>Add c to on_line"]
    CheckCenter["If |ca| = |cb|:<br/>halfang = ∠(acb) + π/2<br/>Add c as center for halfang"]
    CheckCircle["If ≥2 non-collinear points<br/>or ≥1 point + ≥1 center:<br/>Points lie on circle"]
    
    ForceCollinear["force_collinear([a,b,c])<br/>for c in on_line"]
    ForceConcyclic["force_concyclic(points, centers)"]
    
    Start --> GroupByAngle
    GroupByAngle --> CheckLine
    GroupByAngle --> CheckCenter
    GroupByAngle --> CheckCircle
    CheckLine --> ForceCollinear
    CheckCircle --> ForceConcyclic
```

**Sources:** [ddar.py:440-481]()

### Circle Detection from Equal Distances

The `search_circles` method ([ddar.py:483-524]()) detects circles by finding points equidistant from a center:

```mermaid
flowchart TD
    Start["For each point a (potential center)"]
    GroupByDist["Group all other points by<br/>dist_mul = get_dist_mul(a,b)"]
    
    Check["For each distance group"]
    Size{"len(distinct_points)"}
    
    Large["≥3 distinct points:<br/>force_concyclic(points, [a])"]
    Small["<3 distinct points:<br/>Store in last_small_circles<br/>(used by merge_points)"]
    
    Start --> GroupByDist
    GroupByDist --> Check
    Check --> Size
    Size -->|"≥3"| Large
    Size -->|"<3"| Small
```

**Sources:** [ddar.py:483-524]()

### Point Merging

The `merge_points` method ([ddar.py:526-580]()) identifies points that must be equal based on geometric constraints:

1. Find pairs of points `(a,b)` that are numerically identical: `num_identical(a,b)`
2. Find geometric objects (lines, circles) passing through both `a` and `b`
3. If two such objects intersect at `(a,b)` non-tangentially, then `a = b`
4. Execute `force_equal_points(a,b)` to merge them

**Sources:** [ddar.py:526-580]()

## Knowledge Transfer Operations

DDAR maintains consistency between different algebraic representations through transfer operations:

### Additive/Multiplicative Distance Synchronization

The `transfer_dist_add_mul` method ([ddar.py:582-620]()) ensures that:
- If `|AB|` in additive form equals `|CD|` in additive form
- Then `|AB|` in multiplicative form equals `|CD|` in multiplicative form (and vice versa)

This is implemented by normalizing both representations and cross-linking them.

**Sources:** [ddar.py:582-620]()

### Arc-Chord Synchronization

The `transfer_dist_arc_mul` method ([ddar.py:622-649]()) enforces that on circles:
- Equal chord lengths imply equal arc lengths (angles)
- Equal arc lengths imply equal chord lengths

This creates bidirectional constraints between the angle elimination system and distance elimination system.

**Sources:** [ddar.py:622-649]()

## Utility Methods

DDAR provides several helper methods for retrieving simplified values:

| Method | Purpose | Returns | Source |
|--------|---------|---------|--------|
| `get_dist_mul(a,b)` | Simplified multiplicative distance | `DistMul` | [ddar.py:1053-1055]() |
| `get_dist_add(a,b)` | Simplified additive distance | `DistAdd` | [ddar.py:1057-1059]() |
| `get_point_dir(a,b)` | Simplified direction angle | `FormalAngle` | [ddar.py:1061-1062]() |
| `get_dist_ratio(a,b,c,d)` | Ratio `\|cd\|/\|ab\|` | `DistMul` | [ddar.py:1047-1048]() |
| `get_point_angle(a,b,c,d)` | Angle `dir(cd) - dir(ab)` | `FormalAngle` | [ddar.py:1050-1051]() |
| `get_arc(circle,a,b)` | Arc angle on circle from `a` to `b` | `FormalAngle, AGPoint` | [ddar.py:1064-1071]() |
| `num_identical(a,b)` | Check if points numerically equal | `bool` | [ddar.py:128-129]() |
| `update_cache()` | Refresh cached simplified values | `None` | [ddar.py:1036-1045]() |

**Sources:** [ddar.py:1034-1071]()

## Relationship to Other Modules

```mermaid
graph TB
    subgraph "External Dependencies"
        Parse["parse.py<br/>AGPoint, AGPredicate, AGProblem"]
        Elim["elimination.py<br/>ElimDistMul, ElimDistAdd, ElimAngle<br/>DistMul, DistAdd, FormalAngle, LinComb"]
        Num["numericals.py<br/>NumPoint, NumLine, NumCircle<br/>distance, orientation, direction"]
    end
    
    subgraph "DDAR Core [ddar.py]"
        DDARClass["DDAR class"]
        FormalLine["FormalLine class"]
        FormalCircle["FormalCircle class"]
    end
    
    subgraph "External Users"
        Test["test.py<br/>Problem solving orchestration"]
    end
    
    Parse -->|"Provides point/predicate<br/>data structures"| DDARClass
    Elim -->|"Provides algebraic<br/>constraint systems"| DDARClass
    Num -->|"Provides numerical<br/>geometry operations"| DDARClass
    
    DDARClass -->|"Uses for<br/>initialization"| FormalLine
    DDARClass -->|"Uses for<br/>initialization"| FormalCircle
    
    FormalLine -->|"Stores numerical<br/>representation"| Num
    FormalCircle -->|"Stores numerical<br/>representation"| Num
    
    Test -->|"Creates DDAR instance<br/>Calls force_pred<br/>Calls deduction_closure<br/>Calls check_pred"| DDARClass
```

**Sources:** [ddar.py:1-31]()

## Design Patterns

### Dual Representation Strategy

DDAR maintains both symbolic (exact algebraic) and numerical (approximate floating-point) representations:

- **Symbolic**: `FormalAngle`, `DistMul`, `DistAdd` for exact reasoning via Gaussian elimination
- **Numerical**: `NumLine`, `NumCircle`, `NumPoint` for validation and heuristic search

All constraints are verified numerically before being asserted symbolically, preventing inconsistent assertions.

### Iterative Closure Pattern

The `deduction_closure` method uses a fixed-point iteration:
1. Apply all inference rules
2. If any rule discovered new facts, repeat from step 1
3. Otherwise, terminate

This guarantees that all derivable facts within the rule set are discovered.

### Immutable Object Replacement

`FormalLine` and `FormalCircle` objects are immutable. When new points are discovered on a line or circle, DDAR creates a new object and replaces all references to the old object in its lookup dictionaries.

**Sources:** [ddar.py:66-1087]()

---

