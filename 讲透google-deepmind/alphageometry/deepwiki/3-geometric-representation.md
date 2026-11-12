<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphageometry · page 3 Geometric Representation · fetched 2026-10-26 -->

# Geometric Representation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [numericals.py](numericals.py)

</details>



This page explains how AlphaGeometry represents geometric problems internally through a dual representation system: symbolic objects in a proof state graph for theorem proving, and numerical representations for validation and visualization. The geometric representation layer forms the foundation upon which both the deductive database and algebraic reasoning components operate.

## Overview

AlphaGeometry maintains geometric information in three interconnected modules:

1. **`geometry.py`**: Defines symbolic geometric objects (Point, Line, Circle, Angle, Segment) used in the proof graph
2. **`graph.py`**: Implements the proof state graph that tracks geometric relationships and dependencies
3. **`numericals.py`**: Provides numerical 2D geometry primitives for validation and visualization

Additional support comes from:
- **`problem.py`**: Defines problem structure (premises, goals, DAG nodes)
- **`graph_utils.py`**: Utilities for graph manipulation

Title: **Geometric Representation Architecture**

```mermaid
flowchart TD
    subgraph "Problem Input"
        PROB_DEF["problem.py<br/>Problem, Clause, Theorem"]
    end
    
    subgraph "Symbolic Layer"
        GEOM["geometry.py<br/>Point, Line, Circle<br/>Angle, Segment"]
        GRAPH["graph.py<br/>Proof State Graph<br/>Node, Edge Management"]
    end
    
    subgraph "Numerical Layer"
        NUM["numericals.py<br/>2D Geometry Engine<br/>Point, Line, Circle"]
    end
    
    subgraph "Reasoning Engines"
        DD["dd.py<br/>Deductive Database"]
        AR["ar.py<br/>Algebraic Reasoning"]
    end
    
    PROB_DEF --> GRAPH
    PROB_DEF --> GEOM
    
    GRAPH --> GEOM
    GEOM --> NUM
    
    GRAPH --> DD
    GRAPH --> AR
    
    DD --> GRAPH
    AR --> GRAPH
    
    NUM -.->|"validate"| GRAPH
```

Sources: [README.md:335-357]()

The symbolic layer represents geometric objects and their relationships as graph nodes and edges, enabling pattern matching and logical deduction. The numerical layer provides concrete 2D coordinate implementations that validate symbolic derivations and enable visualization.

## Symbolic Geometric Objects

The `geometry.py` module defines symbolic geometric objects that serve as nodes in the proof state graph. These objects maintain both symbolic relationships and numerical instantiations.

### Core Entity Types

Title: **Symbolic Geometric Entity Hierarchy**

```mermaid
classDiagram
    class Point {
        +name: str
        +num: numericals.Point
        +neighbors(type) list
    }
    
    class Line {
        +name: str
        +num: numericals.Line
        +neighbors(type) list
    }
    
    class Circle {
        +name: str
        +num: numericals.Circle
        +neighbors(type) list
    }
    
    class Angle {
        +points: list[Point]
        +measure: Expression
    }
    
    class Segment {
        +points: tuple[Point, Point]
        +length: Expression
    }
    
    Point -- Line: "lies on"
    Point -- Circle: "lies on"
    Point -- Angle: "defines"
    Point -- Segment: "endpoints"
```

Sources: [README.md:337]()

Each symbolic object maintains:
- A unique name for identification
- A reference to its numerical counterpart (`.num` attribute)
- A list of neighboring objects in the graph
- Derived properties (angles, distances, ratios)

### Graph Connections

The `neighbors()` method allows traversal between related geometric objects. For example, a `Point` can retrieve all `Line` objects it lies on, or all `Circle` objects it belongs to.

Sources: [README.md:337]()

## Proof State Graph

The `graph.py` module implements the central proof state graph that tracks all geometric facts and their dependencies.

### Graph Structure

Title: **Proof State Graph Structure**

```mermaid
flowchart TD
    subgraph "Graph Nodes"
        POINTS["Points<br/>(a, b, c, ...)"]
        LINES["Lines<br/>(AB, CD, ...)"]
        CIRCLES["Circles<br/>(O, ...)"]
    end
    
    subgraph "Graph Edges (Predicates)"
        COLL["coll(a,b,c)<br/>collinearity"]
        PARA["para(AB,CD)<br/>parallel"]
        PERP["perp(AB,CD)<br/>perpendicular"]
        CYCLIC["cyclic(a,b,c,d)<br/>concyclic"]
        EQANGLE["eqangle(a,b,c,d,e,f,g,h)<br/>equal angles"]
        CONG["cong(a,b,c,d)<br/>congruent segments"]
    end
    
    subgraph "Dependency Tracking"
        DEPS["Derivation Dependencies<br/>tracks proof steps"]
    end
    
    POINTS --> COLL
    LINES --> PARA
    LINES --> PERP
    POINTS --> CYCLIC
    POINTS --> EQANGLE
    POINTS --> CONG
    
    COLL --> DEPS
    PARA --> DEPS
    PERP --> DEPS
    CYCLIC --> DEPS
    EQANGLE --> DEPS
    CONG --> DEPS
```

Sources: [README.md:340]()

The graph maintains:
- **Nodes**: Geometric objects (points, lines, circles)
- **Edges**: Geometric predicates (relationships between objects)
- **Dependencies**: How each fact was derived (for proof reconstruction)

### Graph Operations

Key operations in `graph.py`:
- **Adding nodes**: Register new geometric objects
- **Adding edges**: Record new geometric relationships
- **Querying**: Find objects satisfying certain predicates
- **Traversal**: Navigate relationships for pattern matching
- **Dependency tracking**: Record derivation chains for proof generation

Sources: [README.md:340]()

## Problem Definition

The `problem.py` module defines the structure of geometry problems and their components.

### Problem Components

Title: **Problem Structure Hierarchy**

```mermaid
classDiagram
    class Problem {
        +premises: list[Clause]
        +goal: Clause
        +constructions: list[Construction]
    }
    
    class Clause {
        +predicate: str
        +args: list[Point]
    }
    
    class Theorem {
        +name: str
        +premises: list[Clause]
        +conclusion: Clause
    }
    
    class DAGNode {
        +fact: Clause
        +dependencies: list[DAGNode]
    }
    
    Problem --> Clause: "contains"
    Theorem --> Clause: "contains"
    DAGNode --> Clause: "wraps"
```

Sources: [README.md:341]()

A `Problem` consists of:
- **Premises**: Initial geometric facts (e.g., "ABC is a triangle", "D is on line BC")
- **Goal**: The theorem to be proven (e.g., "AD is perpendicular to BC")
- **Constructions**: Auxiliary points added during solving

A `Theorem` represents a deduction rule:
- **Premises**: Pattern to match in the graph
- **Conclusion**: New fact to derive if pattern matches

A `DAGNode` represents a derived fact in the proof DAG:
- **Fact**: The derived geometric relationship
- **Dependencies**: Previous facts used in the derivation

Sources: [README.md:341]()

## Numerical Geometry Engine

The `numericals.py` module provides concrete 2D Euclidean geometry implementations. This numerical layer validates symbolic derivations and enables visualization. See [Numerical Geometry Engine (3.1)](#3.1) for detailed documentation.

### Numerical Entities

Title: **Numerical Geometry Classes**

```mermaid
classDiagram
    class Point {
        +x: float
        +y: float
        +distance(Point|Line|Circle) float
        +midpoint(Point) Point
        +rotate(float, float) Point
        +foot(Line) Point
    }
    
    class Line {
        +coefficients: tuple[float, float, float]
        +parallel_line(Point) Line
        +perpendicular_line(Point) Line
        +intersect(Line|Circle) Point|tuple
        +is_parallel(Line) bool
        +is_perp(Line) bool
    }
    
    class Circle {
        +center: Point
        +radius: float
        +intersect(Line|Circle) tuple[Point, Point]
    }
    
    class HalfLine {
        +tail: Point
        +head: Point
        +line: Line
        +intersect(obj) Point
    }
    
    Line <|-- HalfLine
```

Sources: [numericals.py:46-145](), [numericals.py:147-312](), [numericals.py:318-371](), [numericals.py:388-440]()

### Key Operations

The numerical engine provides:

| Operation Category | Functions | Purpose |
|-------------------|-----------|---------|
| **Intersection** | `line_line_intersection()`, `line_circle_intersection()`, `circle_circle_intersection()` | Find intersection points between geometric objects |
| **Validation** | `check_coll()`, `check_para()`, `check_perp()`, `check_cyclic()`, `check_eqangle()`, `check_cong()` | Verify geometric predicates numerically |
| **Sketching** | `sketch_line()`, `sketch_circle()`, `sketch_bisect()`, `sketch_tangent()` | Generate numerical constructions from symbolic definitions |
| **Visualization** | `draw()`, `draw_point()`, `draw_line()`, `draw_circle()`, `highlight()` | Render geometric diagrams |

Sources: [numericals.py:577-586](), [numericals.py:511-547](), [numericals.py:481-504](), [numericals.py:660-710](), [numericals.py:749-843](), [numericals.py:1326-1337](), [numericals.py:1203-1238]()

### Numerical Validation

Each symbolic predicate has a corresponding numerical checker that validates it within tolerance `ATOM = 1e-12`:

Title: **Predicate Validation Flow**

```mermaid
flowchart LR
    PRED["Symbolic Predicate<br/>e.g., perp(AB, CD)"] --> CHECK["check() dispatcher<br/>numericals.py"]
    CHECK --> SPEC["Specific checker<br/>e.g., check_perp()"]
    SPEC --> GEOM["Geometric computation<br/>using Point, Line classes"]
    GEOM --> TOL["Tolerance check<br/>close_enough()"]
    TOL --> RESULT["True/False"]
```

Sources: [numericals.py:624-649](), [numericals.py:696-700](), [numericals.py:1241-1242]()

## Integration with System Components

The numerical representation integrates with other AlphaGeometry components:

### Checking in the Deductive Process

When the system derives new geometric facts through the deductive database, it can validate them numerically:

```mermaid
sequenceDiagram
    participant DD as "Deductive Database"
    participant GR as "Graph Representation"
    participant NR as "Numerical Representation"
    
    DD->>GR: Derive new relationship
    GR->>NR: Translate to numerical representation
    NR->>NR: Apply check_X() function
    Note over NR: Validate with numerical tolerance
    NR-->>GR: Validation result
    GR-->>DD: Accept/reject derivation
```

Sources: [numericals.py:624-646]()

### Visualization

The numerical representation enables visualization of geometric problems and solutions:

```mermaid
flowchart LR
    GR["Graph Representation"] --> NR["Numerical Representation"]
    NR --> VF["Visualization Functions"]
    VF --> R["Rendered Output"]
    
    subgraph "Visualization Components"
        DP["draw_point()"]
        DL["draw_line()"]
        DC["draw_circle()"]
        DA["draw_angle()"]
        H["highlight()"]
    end
```

Sources: [numericals.py:925-1189](), [numericals.py:1203-1238]()

## Error Handling

The system includes specific error classes to handle invalid geometric operations:

- `InvalidLineIntersectError`: When lines are parallel or don't intersect
- `InvalidQuadSolveError`: When solving quadratic equations fails (e.g., in circle-circle intersections)

Sources: [numericals.py:314-316](), [numericals.py:507-508]()

## Constants and Utilities

The system defines important constants and utility functions:

- `ATOM = 1e-12`: Tolerance for numerical equality checks
- `close_enough()`: Utility function for floating-point comparison
- `ang_of()`, `ang_between()`: Angular measurement utilities
- `random_points()`, `random_rfss()`: Functions to generate randomized points

Sources: [numericals.py:33](), [numericals.py:1241-1293]()

## Relationship to Proof System

The numerical representation primarily serves as a validation and visualization layer rather than the core proof mechanism:

```mermaid
flowchart TD
    subgraph "Input Problem"
        PD["Problem Definition"]
    end
    
    subgraph "Representation Layer"
        SR["Symbolic Graph Representation"]
        NR["Numerical Representation"]
    end
    
    subgraph "Proof System"
        DD["Deductive Database"]
        AR["Algebraic Reasoning"]
        LM["Language Model"]
    end
    
    subgraph "Validation & Output"
        VC["Validation Checking"]
        VZ["Visualization"]
    end
    
    PD --> SR
    PD --> NR
    
    SR --> DD
    SR --> AR
    
    DD --> LM
    AR --> LM
    
    LM --> SR
    
    NR --> VC
    NR --> VZ
    
    VC --> SR
```

The numerical representation ensures that geometric facts derived in the deductive process are mathematically valid, providing a concrete implementation of abstract geometric concepts.

Sources: [numericals.py:16-28]()

---

