<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphageometry2 · page 5 Symbolic Elimination System · fetched 2026-10-26 -->

# Symbolic Elimination System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ddar.py](ddar.py)
- [elimination.py](elimination.py)

</details>



## Purpose and Scope

The Symbolic Elimination System is the algebraic constraint solver underlying DDAR's geometric reasoning capabilities. It maintains symbolic relationships between geometric quantities (distances, angles, ratios) and uses Gaussian elimination to deduce whether constraints are satisfied. This page provides an architectural overview of the elimination system and its integration with DDAR.

For detailed information about specific components:
- Linear combination arithmetic and Gaussian elimination internals: see [ElimCore and Linear Combinations](#5.1)
- Variable categorization and the LHS/RHS distinction: see [Elimination Variable Types](#5.2)
- Multiplicative and additive distance constraint systems: see [Distance Elimination Systems](#5.3)
- Angle constraint system and modular arithmetic: see [Angle Elimination System](#5.4)

Sources: [elimination.py:1-523](), [ddar.py:76-78]()

---

## System Architecture

The elimination system consists of three independent constraint solvers that maintain different types of geometric relationships. Each solver operates on its own variable space and uses a shared Gaussian elimination core.

```mermaid
graph TB
    subgraph "DDAR (ddar.py)"
        DDAR["DDAR class<br/>ddar.py:66"]
    end
    
    subgraph "Elimination Systems (elimination.py)"
        ElimDistMul["ElimDistMul<br/>line 321-346<br/>Multiplicative distances"]
        ElimDistAdd["ElimDistAdd<br/>line 400-425<br/>Additive distances"]
        ElimAngle["ElimAngle<br/>line 486-522<br/>Angles"]
        
        ElimCore["ElimCore<br/>line 127-194<br/>Gaussian Elimination"]
        
        ElimDistMul --> ElimCore
        ElimDistAdd --> ElimCore
        ElimAngle --> ElimCore
    end
    
    subgraph "Data Types"
        DistMul["DistMul<br/>line 234-319<br/>log(distance) expressions"]
        DistAdd["DistAdd<br/>line 349-398<br/>distance expressions"]
        FormalAngle["FormalAngle<br/>line 437-484<br/>angle expressions"]
        
        LinComb["LinComb<br/>line 48-125<br/>Linear combinations"]
        
        DistMul --> LinComb
        DistAdd --> LinComb
        FormalAngle --> LinComb
    end
    
    DDAR --> ElimDistMul
    DDAR --> ElimDistAdd
    DDAR --> ElimAngle
    
    ElimDistMul --> DistMul
    ElimDistAdd --> DistAdd
    ElimAngle --> FormalAngle
```

**Diagram: Elimination System Architecture and Code Organization**

Sources: [elimination.py:48-125](), [elimination.py:127-194](), [elimination.py:321-522](), [ddar.py:66-78]()

---

## DDAR Integration

DDAR creates one instance of each elimination system during initialization and uses them throughout the deduction process.

### Initialization in DDAR

```mermaid
graph LR
    subgraph "DDAR.__init__ (ddar.py:69-127)"
        Init["DDAR initialization"]
        
        CreateElimDistMul["self.elim_dist_mul = el.ElimDistMul()"]
        CreateElimDistAdd["self.elim_dist_add = el.ElimDistAdd()"]
        CreateElimAngle["self.elim_angle = el.ElimAngle()"]
        
        CreateDistVars["Create distance variables<br/>for each point pair<br/>lines 90-118"]
        CreateDirVars["Create direction variables<br/>for each point pair<br/>lines 97-108"]
    end
    
    Init --> CreateElimDistMul
    Init --> CreateElimDistAdd
    Init --> CreateElimAngle
    
    CreateElimDistMul --> CreateDistVars
    CreateElimDistAdd --> CreateDistVars
    CreateElimAngle --> CreateDirVars
```

**Diagram: DDAR Initialization of Elimination Systems**

| Elimination System | Purpose | Variable Example | Created At |
|-------------------|---------|------------------|------------|
| `elim_dist_mul` | Log-space distance ratios | `log(\|AB\|)` | [ddar.py:76]() |
| `elim_dist_add` | Linear distance sums | `\|AB\|` | [ddar.py:77]() |
| `elim_angle` | Angle equalities | `d(AB)` (direction) | [ddar.py:78]() |

Sources: [ddar.py:69-127](), [ddar.py:76-78](), [ddar.py:90-118]()

### Constraint Assertion and Query Flow

DDAR uses the elimination systems through two primary operations: asserting constraints and querying whether constraints are satisfied.

```mermaid
flowchart TD
    subgraph "Asserting Constraints"
        ForcePred["ddar.force_pred(pred)<br/>line 131-172"]
        
        TranslateAngle["pred_to_angle<br/>line 174-214"]
        TranslateMul["pred_to_dist_mul<br/>line 216-245"]
        TranslateAdd["pred_to_dist_add<br/>line 247-257"]
        
        ForceAngle["elim_angle.force_zero<br/>line 501-509"]
        ForceMul["elim_dist_mul.force_one<br/>line 330-333"]
        ForceAdd["elim_dist_add.force_zero<br/>line 409-412"]
    end
    
    subgraph "Querying Constraints"
        CheckPred["ddar.check_pred(pred)<br/>line 259-298"]
        
        SimplifyAngle["elim_angle.simplify<br/>line 511-514"]
        SimplifyMul["elim_dist_mul.simplify<br/>line 335-338"]
        SimplifyAdd["elim_dist_add.simplify<br/>line 414-417"]
        
        IsZero["angle.is_zero()"]
        IsOne["dist_mul.is_one()"]
        IsZeroAdd["dist_add.is_zero()"]
    end
    
    ForcePred --> TranslateAngle
    ForcePred --> TranslateMul
    ForcePred --> TranslateAdd
    
    TranslateAngle --> ForceAngle
    TranslateMul --> ForceMul
    TranslateAdd --> ForceAdd
    
    CheckPred --> SimplifyAngle
    CheckPred --> SimplifyMul
    CheckPred --> SimplifyAdd
    
    SimplifyAngle --> IsZero
    SimplifyMul --> IsOne
    SimplifyAdd --> IsZeroAdd
```

**Diagram: Constraint Assertion and Query Operations**

Sources: [ddar.py:131-172](), [ddar.py:174-257](), [ddar.py:259-298](), [elimination.py:330-333](), [elimination.py:409-412](), [elimination.py:501-509]()

---

## Core Concepts

### Linear Combinations

The `LinComb` class represents linear combinations of variables with rational coefficients. All constraint expressions are represented as `LinComb` instances.

```mermaid
graph TB
    LinComb["LinComb<br/>line 48-125"]
    
    Dict["d: dict[Any, Fraction]<br/>Maps variables to coefficients"]
    
    Operations["Operations:<br/>• __add__, __sub__<br/>• __mul__ (by scalar)<br/>• iadd_mul (in-place)<br/>• copy(), zero()"]
    
    LinComb --> Dict
    LinComb --> Operations
    
    Example["Example:<br/>3*x + 2*y - z<br/>= {x: 3, y: 2, z: -1}"]
    
    Dict --> Example
```

**Diagram: LinComb Structure and Operations**

| Method | Purpose | Line |
|--------|---------|------|
| `iadd_mul(other, coef)` | In-place add `other * coef` | [48-66]() |
| `__add__(other)` | Add two combinations | [76-79]() |
| `__mul__(coef)` | Multiply by scalar | [86-93]() |
| `singleton(v, coef)` | Create single-variable combination | [115-120]() |

Sources: [elimination.py:48-125]()

### Variable Types

Variables in the elimination system are categorized into three types:

```mermaid
graph TD
    ElimVar["ElimVar<br/>line 28-37<br/>Base class"]
    
    ElimLHS["ElimLHS<br/>line 40-41<br/>Left-hand side variables<br/>(can be eliminated)"]
    
    ElimRHS["ElimRHS<br/>line 44-45<br/>Right-hand side variables<br/>(constants, never eliminated)"]
    
    ElimVar --> ElimLHS
    ElimVar --> ElimRHS
    
    Examples["Examples:<br/>• ElimLHS: log(|AB|), |AB|, d(AB)<br/>• ElimRHS: log(2), log(3), pi"]
    
    ElimLHS --> Examples
    ElimRHS --> Examples
```

**Diagram: Variable Type Hierarchy**

The distinction between LHS and RHS variables determines which variables can be eliminated during Gaussian elimination. LHS variables represent unknown geometric quantities, while RHS variables represent known constants.

Sources: [elimination.py:28-45]()

### Gaussian Elimination Core

The `ElimCore` class implements Gaussian elimination to simplify constraint systems. It maintains a matrix where each row represents an eliminated variable expressed in terms of free variables.

**ElimCore State:**

| Field | Type | Purpose |
|-------|------|---------|
| `instantiated` | `dict[ElimVar, LinComb]` | Maps eliminated variables to their expressions |
| `free_to_usage` | `defaultdict[ElimVar, set[ElimVar]]` | Tracks which equations use each free variable |

**Core Operations:**

- `simplify(comb)` - Substitute eliminated variables with their definitions [elimination.py:134-143]()
- `add_constraint(comb)` - Add new constraint, performing elimination if possible [elimination.py:145-169]()
- `was_encountered(comb)` - Check if a variable has been seen [elimination.py:186-193]()

Sources: [elimination.py:127-194]()

---

## Three Elimination Systems

### ElimDistMul: Multiplicative Distance System

Represents distances in logarithmic space, allowing ratios to be expressed as differences. Variables represent `log(|AB|)` values.

**Key Operations:**
- `new_var(value, name)` - Create new distance variable [elimination.py:327-328]()
- `force_one(dist_mul)` - Assert that `dist_mul == 1` (i.e., `log(dist_mul) == 0`) [elimination.py:330-333]()
- `simplify(dist_mul)` - Reduce expression using known constraints [elimination.py:335-338]()

**Constraint Type Examples:**
- `|AB| / |CD| = k` → `log(|AB|) - log(|CD|) = log(k)`
- `|AB| * |CD| = |EF| * |GH|` → `log(|AB|) + log(|CD|) = log(|EF|) + log(|GH|)`

Sources: [elimination.py:321-346]()

### ElimDistAdd: Additive Distance System

Represents distances linearly, allowing segment addition on lines. Variables represent `|AB|` values directly.

**Key Operations:**
- `new_var(value, name)` - Create new distance variable [elimination.py:406-407]()
- `force_zero(dist_add)` - Assert that `dist_add == 0` [elimination.py:409-412]()
- `simplify(dist_add)` - Reduce expression using known constraints [elimination.py:414-417]()

**Constraint Type Examples:**
- `|AB| + |BC| = |AC|` (collinear points)
- `|AB| = |CD|` → `|AB| - |CD| = 0`

Sources: [elimination.py:400-425]()

### ElimAngle: Angle System

Represents angles modulo π (180°), treating angles as directions. Variables represent angles in units of π.

**Key Operations:**
- `new_var(value, name)` - Create new angle variable [elimination.py:498-499]()
- `const(num, denom)` - Create constant angle `num/denom * π` [elimination.py:492-493]()
- `force_zero(angle)` - Assert that angle equals `k*π` for some integer k [elimination.py:501-509]()
- `simplify(angle)` - Reduce expression using known constraints [elimination.py:511-514]()

**Special Constant:**
- `angle_unit` - Represents π, the unit angle [elimination.py:428-434]()

**Constraint Type Examples:**
- Parallel lines: `d(AB) - d(CD) = 0`
- Perpendicular lines: `d(AB) - d(CD) = π/2`
- Equal angles: `∠ABC - ∠DEF = 0`

Sources: [elimination.py:486-522](), [elimination.py:428-434]()

---

## Data Flow Through Elimination Systems

The following diagram shows how geometric predicates flow through the elimination system:

```mermaid
flowchart TD
    subgraph "Input"
        Predicate["AGPredicate<br/>(parsed from problem)"]
    end
    
    subgraph "Translation (ddar.py)"
        PredToAngle["pred_to_angle<br/>line 174-214"]
        PredToDistMul["pred_to_dist_mul<br/>line 216-245"]
        PredToDistAdd["pred_to_dist_add<br/>line 247-257"]
    end
    
    subgraph "Symbolic Form"
        FormalAngle["FormalAngle<br/>(LinComb of angle vars)"]
        DistMul["DistMul<br/>(LinComb of log-distance vars)"]
        DistAdd["DistAdd<br/>(LinComb of distance vars)"]
    end
    
    subgraph "Constraint System"
        ElimAngleCore["ElimAngle.core<br/>(ElimCore instance)"]
        ElimDistMulCore["ElimDistMul.core<br/>(ElimCore instance)"]
        ElimDistAddCore["ElimDistAdd.core<br/>(ElimCore instance)"]
    end
    
    subgraph "Output"
        Simplified["Simplified Expression<br/>(free variables only)"]
        Check["Boolean Result<br/>(is_zero/is_one check)"]
    end
    
    Predicate --> PredToAngle
    Predicate --> PredToDistMul
    Predicate --> PredToDistAdd
    
    PredToAngle --> FormalAngle
    PredToDistMul --> DistMul
    PredToDistAdd --> DistAdd
    
    FormalAngle --> ElimAngleCore
    DistMul --> ElimDistMulCore
    DistAdd --> ElimDistAddCore
    
    ElimAngleCore --> Simplified
    ElimDistMulCore --> Simplified
    ElimDistAddCore --> Simplified
    
    Simplified --> Check
```

**Diagram: End-to-End Data Flow Through Elimination Systems**

Sources: [ddar.py:174-257](), [elimination.py:134-143](), [elimination.py:330-338](), [elimination.py:409-417](), [elimination.py:501-514]()

---

## Why Three Separate Systems?

The elimination system maintains three independent constraint solvers because different geometric relationships require different algebraic representations:

| System | Representation | Best For | Example Constraint |
|--------|---------------|----------|-------------------|
| **ElimDistMul** | Logarithmic | Ratios, products, congruence | `|AB|/|CD| = |EF|/|GH|` |
| **ElimDistAdd** | Linear | Sums, collinear segments | `|AB| + |BC| = |AC|` |
| **ElimAngle** | Modular (mod π) | Directions, angle equality | `∠ABC = ∠DEF` |

During deduction, DDAR transfers information between systems when possible:
- `transfer_dist_add_mul()` - Synchronizes additive and multiplicative distances [ddar.py:582-620]()
- `transfer_dist_arc_mul()` - Relates arc lengths to chord lengths on circles [ddar.py:622-649]()

This multi-system architecture allows DDAR to represent complex geometric relationships precisely while maintaining computational efficiency through specialized constraint solvers.

Sources: [ddar.py:582-649](), [elimination.py:321-522]()

---

