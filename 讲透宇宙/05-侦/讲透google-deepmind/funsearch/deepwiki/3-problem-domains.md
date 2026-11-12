<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/funsearch · page 3 Problem Domains · fetched 2026-10-26 -->

# Problem Domains

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of the mathematical problem domains addressed by FunSearch. Each domain represents a distinct mathematical challenge for which FunSearch was used to discover novel solutions through program search with large language models. For information about the core algorithm and implementation details, see [Core Implementation](#2).

## Overview of Problem Domains

The FunSearch repository contains five mathematical problem domains, each implemented as a standalone directory with its own notebook and discovered solutions:

```mermaid
flowchart TD
    root["FunSearch Repository"] --> cap["cap_set/"]
    root --> adm["admissible_set/"]
    root --> bin["bin_packing/"]
    root --> cyc["cyclic_graphs/"]
    root --> cor["corner_free_sets/"]
    
    cap --> cap_nb["cap_set.ipynb"]
    adm --> adm_nb["admissible_set.ipynb"]
    bin --> bin_nb["bin_packing.ipynb"]
    cyc --> cyc_nb["cyclic_graphs.ipynb"]
    
    cap_nb --> cap_res["Cap sets in F₃ⁿ"]
    adm_nb --> adm_res["Bounds on cap set capacity"]
    bin_nb --> bin_res["Bin packing heuristics"]
    cyc_nb --> cyc_res["Independent sets"]
    cor --> cor_res["Sets satisfying constraints"]
```

Sources: [README.md:7-26]()

## Common Search Pattern

All problem domains utilize a similar approach to mathematical discovery through program search:

```mermaid
flowchart LR
    subgraph "FunSearch Pattern"
        direction TB
        spec["Problem Specification"] --> init["Initial Function"]
        init --> evolve["Function Evolution"]
        evolve --> improved["Improved Function"]
        improved --> discovery["Mathematical Discovery"]
    end
    
    subgraph "Priority Function Pattern"
        direction TB
        basic["Initial Priority Function"] --> evo["FunSearch Evolution"]
        evo --> optimized["Optimized Priority Function"]
    end
    
    evolve -.-> basic
    optimized -.-> improved
```

Sources: [README.md:7-26]()

Rather than directly evolving the solution, FunSearch typically evolves a "priority function" that guides a greedy algorithm to construct the solution step by step. This approach has proven effective across different mathematical domains.

## Problem Domain Descriptions

### Cap Sets

Cap sets are subsets of the three-dimensional space over the field with three elements (F₃ⁿ) that contain no three points in an arithmetic progression (no lines).

```mermaid
flowchart TD
    subgraph "Cap Set Problem Domain"
        problem["Find large subsets of F₃ⁿ with no lines"] --> greedy["Greedy Construction Algorithm"]
        greedy --> priority["priority() Function"]
        priority --> construct["construct_cap_set() Function"]
        construct --> result["Large Cap Sets"]
    end
    
    subgraph "Code Implementation"
        cap_notebook["cap_set.ipynb"]
        priority_func["priority(element, existing_set)"]
        cap_sets["Numerical Cap Set Representations"]
    end
    
    priority --> priority_func
    result --> cap_sets
    problem --> cap_notebook
```

Sources: [README.md:9-10]()

The `cap_set` directory contains functions discovered by FunSearch that construct large cap sets, as well as numerical representations of those sets.

### Admissible Sets

Admissible sets provide a way to establish lower bounds on the maximum size of cap sets in F₃ⁿ.

```mermaid
flowchart TD
    subgraph "Admissible Set Problem Domain"
        problem["Establish lower bounds on cap set size"] --> functions["evaluate(n,w) and solve(n,w)"]
        functions --> priority["priority(element, n, w)"]
        priority --> construct["Construct Admissible Sets"]
        construct --> bounds["Compute Capacity Bounds"]
    end
    
    subgraph "Code Implementation"
        adm_notebook["admissible_set.ipynb"]
        priority_func["priority(element, n, w)"]
        adm_sets["Numerical Admissible Set Representations"]
    end
    
    priority --> priority_func
    construct --> adm_sets
    problem --> adm_notebook
```

Sources: [README.md:12-14]()

The `admissible_set` directory contains functions discovered by FunSearch that construct large admissible sets, along with numerical representations of these sets.

### Bin Packing

The bin packing problem involves packing items of different sizes into a fixed number of bins to minimize wasted space. FunSearch focuses on the online version where items must be placed immediately upon arrival.

```mermaid
flowchart TD
    subgraph "Bin Packing Problem Domain"
        problem["Online 1D Bin Packing"] --> heuristic["Packing Heuristic"]
        heuristic --> next_bin["next_bin() Function"]
        next_bin --> evaluation["Performance Evaluation"]
    end
    
    subgraph "Code Implementation"
        bin_notebook["bin_packing.ipynb"]
        next_bin_func["next_bin(item, bins)"]
        eval_suite["Evaluation Suite"]
    end
    
    next_bin --> next_bin_func
    evaluation --> eval_suite
    problem --> bin_notebook
```

Sources: [README.md:16-18]()

The `bin_packing` directory contains heuristics discovered by FunSearch for online 1D bin packing problems and an evaluation suite to reproduce the results reported in the paper.

### Cyclic Graphs

This problem involves finding large independent sets in strong products of cyclic graphs - sets of vertices where no two vertices are adjacent.

```mermaid
flowchart TD
    subgraph "Cyclic Graphs Problem Domain"
        problem["Independent Sets in Cyclic Graphs"] --> construct["Construction Algorithm"]
        construct --> priority["priority() Function"]
        priority --> independent["Generate Independent Sets"]
    end
    
    subgraph "Code Implementation"
        cyc_notebook["cyclic_graphs.ipynb"]
        priority_func["priority(vertex, existing_set)"]
        ind_sets["Numerical Independent Set Representations"]
    end
    
    priority --> priority_func
    independent --> ind_sets
    problem --> cyc_notebook
```

Sources: [README.md:20-22]()

The `cyclic_graphs` directory contains functions discovered by FunSearch that construct large independent sets in strong products of cyclic graphs, as well as numerical representations of those sets.

### Corner-Free Sets

Corner-free sets are sets of indices satisfying specific combinatorial degeneration constraints.

```mermaid
flowchart TD
    subgraph "Corner-Free Sets Problem Domain"
        problem["Sets satisfying combinatorial constraints"] --> constraints["Degeneration Constraints"]
        constraints --> sets["Discovered Sets of Indices"]
    end
    
    subgraph "Code Implementation"
        corner_dir["corner_free_sets/"]
        numerical["Numerical Representations"]
    end
    
    sets --> numerical
    problem --> corner_dir
```

Sources: [README.md:24-26]()

The `corner_free_sets` directory contains the discovered sets of indices in numerical format, satisfying the combinatorial degeneration constraints described for the corners-free problem.

## Problem Domains in the FunSearch Pipeline

The following diagram illustrates how each problem domain integrates with the FunSearch evolutionary algorithm:

```mermaid
flowchart LR
    subgraph "FunSearch Pipeline"
        direction TB
        llm["LLM Code Generator"] --> programs["Candidate Programs"]
        programs --> evaluator["Evaluator"]
        evaluator --> selection["Program Selection"]
        selection --> llm
    end
    
    subgraph "Problem Domains"
        cap["Cap Set Domain:<br>priority() functions"]
        adm["Admissible Set Domain:<br>priority() functions"]
        bin["Bin Packing Domain:<br>next_bin() functions"]
        cyc["Cyclic Graphs Domain:<br>priority() functions"]
        cor["Corner-Free Sets Domain:<br>constraint functions"]
    end
    
    evaluator --- domains["Problem-Specific<br>Evaluation Functions"]
    domains --> cap
    domains --> adm
    domains --> bin
    domains --> cyc
    domains --> cor
```

Sources: [README.md:7-26](), [README.md:28-34]()

## Technical Implementation Table

| Problem Domain | Directory | Main Notebook | Evolved Functions | Output |
|----------------|-----------|---------------|-------------------|--------|
| Cap Sets | `cap_set/` | `cap_set.ipynb` | `priority()` | Large cap sets in F₃ⁿ |
| Admissible Sets | `admissible_set/` | `admissible_set.ipynb` | `priority()`, `evaluate()`, `solve()` | Lower bounds on cap set capacity |
| Bin Packing | `bin_packing/` | `bin_packing.ipynb` | `next_bin()` | Online packing heuristics |
| Cyclic Graphs | `cyclic_graphs/` | `cyclic_graphs.ipynb` | `priority()` | Independent sets in cyclic graphs |
| Corner-Free Sets | `corner_free_sets/` | N/A | Constraint functions | Sets satisfying constraints |

Sources: [README.md:7-34]()

## Usage and Exploration

All notebooks can be run in Google Colab without installation requirements:

- Cap Set: `cap_set.ipynb` ([README.md:43-44]())
- Admissible Set: `admissible_set.ipynb` ([README.md:46-48]())
- Bin Packing: `bin_packing.ipynb` ([README.md:50-51]())
- Cyclic Graphs: `cyclic_graphs.ipynb` ([README.md:53-54]())

These notebooks allow users to explore the discovered functions and verify the mathematical results reported in the FunSearch paper.

---

