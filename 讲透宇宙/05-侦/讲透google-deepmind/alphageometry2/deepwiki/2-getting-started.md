<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphageometry2 · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [parse.py](parse.py)
- [test.py](test.py)

</details>



This document provides an introduction to installing, running, and understanding the basic operation of the AlphaGeometry2 DDAR logical core test system. It covers the installation process, how to execute the test suite, and an overview of the problem format and execution flow.

For detailed instructions on running tests and interpreting results, see [Running the Test Suite](#2.1). For a comprehensive explanation of the problem format, see [Problem Format and Structure](#2.2). For understanding the overall system architecture, see [System Architecture](#3).

## Installation

The system requires Python 3 with NumPy. Installation is performed in a virtual environment:

```bash
$ sudo apt install python3
$ sudo apt install python3-pip
$ sudo apt install python3-venv
$ python3 -m venv ag2
$ source ag2/bin/activate
$ pip install numpy
```

**Sources:** [README.md:18-29]()

## Running the Test Suite

Execute the test suite using Python's module syntax:

```bash
$ python -m test
```

This command runs the `test.py` module, which serves as the test driver and orchestrator for the DDAR logical core. The test suite evaluates DDAR's performance on 26 IMO geometry problems divided into two categories.

**Sources:** [README.md:31-37](), [test.py:1-517]()

### Test Execution Flow

```mermaid
flowchart TD
    Start[["python -m test"]]
    Init["Load problems_without_aux<br/>and problems_with_aux<br/>dictionaries"]
    Category1["Print explanation_without_aux"]
    Loop1["For each problem in<br/>problems_without_aux"]
    Category2["Print explanation_with_aux"]
    Loop2["For each problem in<br/>problems_with_aux"]
    Done[["Test Complete"]]
    
    Start --> Init
    Init --> Category1
    Category1 --> Loop1
    Loop1 --> Process1["print_problem_and_solve()"]
    Process1 --> Check1{More problems<br/>in category 1?}
    Check1 -->|Yes| Loop1
    Check1 -->|No| Category2
    Category2 --> Loop2
    Loop2 --> Process2["print_problem_and_solve()"]
    Process2 --> Check2{More problems<br/>in category 2?}
    Check2 -->|Yes| Loop2
    Check2 -->|No| Done
    
    subgraph "print_problem_and_solve()"
        Parse["AGProblem.parse(pstring)"]
        CreateDDAR["DDAR(problem.points)"]
        Force["For each pred:<br/>ddar.force_pred(pred)"]
        Closure["ddar.deduction_closure()"]
        Check["ddar.check_pred(problem.goal)"]
        Output["Print 'Proven :-)' or<br/>'Problem not solved'"]
        
        Parse --> CreateDDAR
        CreateDDAR --> Force
        Force --> Closure
        Closure --> Check
        Check --> Output
    end
```

**Sources:** [test.py:490-516]()

## Output Format

The test suite produces output indicating which problems were tested and whether they were proven. Each problem execution generates a line of dots representing deduction iterations, followed by a success or failure message.

### Example Output Structure

| Output Component | Description | Example |
|-----------------|-------------|---------|
| Problem ID | IMO year and problem number | `Problem: 2005_p1` |
| Iteration Dots | Each dot represents one deduction cycle | `......` |
| Result | Proof status | `Proven :-)` |

**Example output:**
```
Problem: 2000_p1
..... Proven :-)

Problem: 2002_p2a
.... Proven :-)
```

Each dot in the output corresponds to one iteration of the deduction closure loop in `ddar.deduction_closure()`.

**Sources:** [README.md:39-125](), [test.py:490-507]()

## Problem Categories

The test suite contains two distinct problem categories that exercise different capabilities of the DDAR system:

```mermaid
graph TD
    TestSuite["test.py"]
    
    subgraph Cat1["Category 1: DDAR-Solvable"]
        Dict1["problems_without_aux<br/>dictionary"]
        Count1["15 problems"]
        Desc1["Problems solvable by<br/>DDAR's deductive reasoning alone"]
        Examples1["2000_p1, 2002_p2a, 2003_p4,<br/>2004_p5, 2005_p5, 2007_p4,<br/>2010_p4, 2012_p1, 2013_p4,<br/>2014_p4, 2015_p4, 2016_p1,<br/>2017_p4, 2022_p4, 2002_p2b"]
    end
    
    subgraph Cat2["Category 2: Auxiliary Points Required"]
        Dict2["problems_with_aux<br/>dictionary"]
        Count2["11 problems"]
        Desc2["Problems requiring strategic<br/>auxiliary points (manually provided)"]
        Examples2["2001_p5a, 2003_p4b, 2005_p1,<br/>2008_p1b, 2008_p6, 2009_p4a,<br/>2009_p4b, 2011_p6, 2013_p3,<br/>2019_p2, 2021_p3"]
    end
    
    TestSuite --> Dict1
    TestSuite --> Dict2
    Dict1 --> Count1
    Dict1 --> Desc1
    Dict1 --> Examples1
    Dict2 --> Count2
    Dict2 --> Desc2
    Dict2 --> Examples2
```

### Category 1: Problems Without Auxiliary Points

The `problems_without_aux` dictionary contains 15 IMO problems that DDAR can solve using only the given points and predicates. These problems test DDAR's core deductive capabilities: triangle similarity detection, cyclic quadrilateral identification, and circle detection.

### Category 2: Problems With Auxiliary Points

The `problems_with_aux` dictionary contains 11 challenging IMO problems that require strategic auxiliary (helper) points. These auxiliary points are manually included in the problem strings. In a complete AlphaGeometry2 system, a language model would generate these points automatically, but this repository tests only the logical core with pre-provided auxiliary constructions.

**Sources:** [test.py:22-479](), [README.md:90-125]()

## Problem String Format Overview

Problems are encoded as single-line strings with a specific syntax. The format defines points, their coordinates, predicates (given conditions), and the goal.

### Problem String Structure

```mermaid
flowchart LR
    ProbStr["Problem String"]
    
    subgraph Points["Point Definitions"]
        P1["a@0.0_0.0 = ;"]
        P2["b@1.0_0.0 = ;"]
        P3["c@0.5_0.866 = ;"]
    end
    
    subgraph Predicates["Given Predicates"]
        Pred1["cong a b b c"]
        Pred2["cong b c c a"]
        Pred3["perp a b c d"]
    end
    
    subgraph Goal["Goal"]
        G1["? cyclic a b c d"]
    end
    
    ProbStr --> Points
    Points --> Predicates
    Predicates --> Goal
```

**Format syntax:**
- **Point definition:** `name@x_y = ;` where `name` is the point identifier and `x_y` are coordinates
- **Predicates:** Comma-separated predicates after the `=` sign
- **Goal:** Follows the `?` symbol

**Example:**
```
a@0.0_0.0 = ; b@1.0_0.0 = ; c@0.5_0.866 = cong a b b c ? cong b c c a
```

**Sources:** [test.py:23-479](), [parse.py:111-148]()

## Execution Pipeline Overview

When a problem is tested, it flows through several processing stages:

```mermaid
flowchart TD
    Input["Problem String"]
    Parse["AGProblem.parse()<br/>parse.py"]
    AGProb["AGProblem object<br/>points, preds, goal"]
    InitDDAR["DDAR(points)<br/>ddar.py"]
    DdarObj["DDAR instance with<br/>FormalLines, FormalCircles,<br/>Elimination systems"]
    Force["For each pred:<br/>ddar.force_pred(pred)"]
    Constraints["Predicates translated to<br/>constraints in elimination systems"]
    Closure["ddar.deduction_closure()"]
    Deduced["Iteratively deduce new facts<br/>using inference rules"]
    Check["ddar.check_pred(goal)"]
    Result{Goal proven?}
    Success["Print 'Proven :-)'"]
    Failure["Print 'Problem not solved'"]
    
    Input --> Parse
    Parse --> AGProb
    AGProb --> InitDDAR
    InitDDAR --> DdarObj
    DdarObj --> Force
    Force --> Constraints
    Constraints --> Closure
    Closure --> Deduced
    Deduced --> Check
    Check --> Result
    Result -->|Yes| Success
    Result -->|No| Failure
```

**Key processing stages:**

1. **Parsing:** The problem string is parsed into an `AGProblem` object containing `AGPoint` objects, `AGPredicate` objects, and a goal predicate
2. **DDAR Initialization:** A `DDAR` instance is created with the problem's points, initializing geometric structures
3. **Constraint Assertion:** Each given predicate is translated into constraints via `ddar.force_pred()`
4. **Deduction Closure:** The `ddar.deduction_closure()` method iteratively applies inference rules until no new facts can be derived
5. **Goal Verification:** The goal predicate is checked using `ddar.check_pred()` to determine if it can be proven from the closed database

**Sources:** [test.py:490-507](), [parse.py:111-148]()

## Next Steps

This overview provides the foundation for using the system. For deeper understanding:

- See [Running the Test Suite](#2.1) for detailed execution instructions and output interpretation
- See [Problem Format and Structure](#2.2) for complete problem format specification
- See [System Architecture](#3) for understanding how components interact
- See [Problem-Solving Pipeline](#9) for a detailed walkthrough of problem execution

**Sources:** [README.md:1-163](), [test.py:1-517](), [parse.py:1-149]()

---

