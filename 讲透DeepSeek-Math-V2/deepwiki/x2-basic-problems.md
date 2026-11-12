<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-Math-V2 · extra page Basic Problems · fetched 2026-10-30 -->

# Basic Problems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [figures/IMO-ProofBench.png](figures/IMO-ProofBench.png)
- [outputs/IMO-ProofBench-Basic.jsonl](outputs/IMO-ProofBench-Basic.jsonl)

</details>



## Purpose and Scope

This page documents the **IMO-ProofBench Basic Problems** subset, which represents the foundational tier of the IMO-ProofBench benchmark system. Basic problems focus on fundamental theorem proving with standard verification methods, as opposed to the formal representations and proof tactics used in Advanced Problems (see [Advanced Problems](#3.2.2) for the higher-tier subset).

The Basic Problems subset tests DeepSeek-Math-V2's ability to generate clear, step-by-step mathematical proofs for foundational mathematical theorems while maintaining rigorous verification of each reasoning step. These problems serve as a baseline for evaluating proof generation quality before progressing to formal proof assistant integration.

For overall IMO-ProofBench system architecture, see [IMO-ProofBench](#3.2). For information on output data schemas across all benchmarks, see [JSONL Schema](#4.1).

---

## Overview

The IMO-ProofBench Basic Problems constitute a curated collection of mathematical theorem proving tasks designed to evaluate fundamental proof generation capabilities. Unlike competition problems that require discovering novel solution approaches, these problems test the model's ability to formally construct proofs for established mathematical statements with clear verification criteria.

**Key Characteristics:**
- **Natural Language Proofs**: Solutions are expressed in human-readable mathematical language with LaTeX formatting, not formal proof assistant syntax
- **Standard Verification**: Verification relies on the LLM-based verifier component rather than formal proof checkers
- **Foundational Coverage**: Problems span basic mathematical domains including elementary number theory, algebra, geometry, and combinatorics
- **Step-by-Step Reasoning**: Each proof must demonstrate clear logical progression from premises to conclusion

**Diagram: Basic Problems Within IMO-ProofBench Hierarchy**

```mermaid
graph TB
    subgraph "IMO-ProofBench Benchmark"
        PB["IMO-ProofBench<br/>Google DeepMind"]
        
        subgraph "Basic Problems Tier"
            BASIC["Basic Problems<br/>Natural Language Proofs"]
            BASIC_VER["Standard LLM-based<br/>Verification"]
            BASIC_OUT["IMO-ProofBench-Basic.jsonl"]
        end
        
        subgraph "Advanced Problems Tier"
            ADV["Advanced Problems<br/>Formal Representations"]
            ADV_VER["Proof Assistant<br/>Integration"]
            ADV_OUT["IMO-ProofBench-Advanced.jsonl"]
        end
        
        PB --> BASIC
        PB --> ADV
        BASIC --> BASIC_VER
        BASIC --> BASIC_OUT
        ADV --> ADV_VER
        ADV --> ADV_OUT
    end
    
    subgraph "DeepSeek-Math-V2 Components"
        GEN["Proof Generator<br/>Natural Language"]
        VER["LLM-based Verifier<br/>Step Validation"]
    end
    
    BASIC --> GEN
    BASIC_VER --> VER
    
    GEN -->|Generates| BASIC_OUT
    VER -->|Validates| BASIC_OUT
```

Sources: Diagrams 1, 3, and 4 from system architecture overview; table of contents structure

---

## Data Structure

Basic problems follow a standardized JSONL format consistent across all DeepSeek-Math-V2 evaluation outputs. Each line in `outputs/IMO-ProofBench-Basic.jsonl` represents a single problem-solution pair.

### Record Schema

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | The theorem statement or problem to prove, typically in LaTeX-formatted mathematical notation |
| `problem_idx` | string | Unique identifier for the problem within the Basic subset (e.g., "basic_001", "basic_002") |
| `model_prediction` | object | Container for the model's generated proof and evaluation metrics |

### Model Prediction Object

| Field | Type | Description |
|-------|------|-------------|
| `proof` | string | Complete step-by-step mathematical proof in natural language with LaTeX formatting |
| `average_automatic_rating` | float | Numeric score (typically 0.0-10.0) from the LLM-based verifier evaluating proof correctness |
| `human_rating` | int | Optional human expert rating (typically 0-10) when available for validation |

**Diagram: Basic Problems Data Structure**

```mermaid
graph LR
    subgraph "IMO-ProofBench-Basic.jsonl"
        RECORD["JSONL Record<br/>One per line"]
        
        subgraph "Top-level Fields"
            Q["question<br/>string"]
            IDX["problem_idx<br/>string"]
            PRED["model_prediction<br/>object"]
        end
        
        subgraph "model_prediction Object"
            PROOF["proof<br/>string<br/>Step-by-step derivation"]
            AUTO["average_automatic_rating<br/>float<br/>LLM verifier score"]
            HUMAN["human_rating<br/>int<br/>Expert validation"]
        end
        
        RECORD --> Q
        RECORD --> IDX
        RECORD --> PRED
        
        PRED --> PROOF
        PRED --> AUTO
        PRED --> HUMAN
    end
    
    subgraph "Generation Process"
        GEN_COMP["Generator Component"]
        VER_COMP["Verifier Component"]
    end
    
    GEN_COMP -->|Produces| PROOF
    VER_COMP -->|Evaluates| AUTO
```

Sources: Diagram 3 from system architecture (data flow); section 4 objectives from table of contents

---

## Problem Categories

Basic problems are organized across fundamental mathematical domains, each testing different aspects of proof construction ability:

### Number Theory
- **Prime factorization properties**
- **Divisibility rules and proofs**
- **Modular arithmetic theorems**
- **Greatest common divisor relationships**

### Algebra
- **Polynomial identity proofs**
- **Functional equation solutions**
- **Inequality derivations**
- **System of equations solving**

### Geometry
- **Basic Euclidean geometry theorems**
- **Coordinate geometry proofs**
- **Circle and tangent properties**
- **Triangle congruence and similarity**

### Combinatorics
- **Counting principle applications**
- **Basic permutation and combination proofs**
- **Pigeonhole principle examples**
- **Graph theory fundamentals**

**Problem Domain Distribution Table**

| Domain | Typical Problem Types | Verification Complexity |
|--------|----------------------|------------------------|
| Number Theory | Divisibility, primes, GCD/LCM | Medium - requires arithmetic validation |
| Algebra | Identities, inequalities, equations | Low-Medium - algebraic manipulation checks |
| Geometry | Euclidean proofs, coordinate geometry | Medium-High - spatial reasoning validation |
| Combinatorics | Counting, permutations, pigeonhole | Medium - combinatorial logic verification |

Sources: Diagram 4 (mathematical domains covered); system capabilities overview

---

## Verification Process

The verification process for Basic Problems differs from Advanced Problems by relying on the LLM-based verifier component rather than formal proof assistants. This approach evaluates natural language proofs for mathematical rigor without requiring formal syntax.

**Diagram: Basic Problems Verification Pipeline**

```mermaid
graph TB
    subgraph "Input Stage"
        PROBLEM["Basic Problem<br/>Theorem Statement"]
        QUESTION["question field<br/>Natural language + LaTeX"]
    end
    
    subgraph "Generation Stage"
        GENERATOR["Proof Generator<br/>DeepSeek-Math-V2"]
        STEPS["Multi-step Derivation<br/>Lemmas + Cases + Conclusion"]
    end
    
    subgraph "Verification Stage"
        VERIFIER["LLM-based Verifier"]
        
        subgraph "Verification Checks"
            LOGICAL["Logical Consistency<br/>Step-to-step validity"]
            COMPLETE["Completeness<br/>All cases covered"]
            CORRECT["Correctness<br/>Mathematically sound"]
        end
        
        VERIFIER --> LOGICAL
        VERIFIER --> COMPLETE
        VERIFIER --> CORRECT
    end
    
    subgraph "Output Stage"
        RATING["average_automatic_rating<br/>Numeric score"]
        OUTPUT["IMO-ProofBench-Basic.jsonl<br/>Recorded result"]
    end
    
    PROBLEM --> QUESTION
    QUESTION --> GENERATOR
    GENERATOR --> STEPS
    STEPS --> VERIFIER
    
    LOGICAL --> RATING
    COMPLETE --> RATING
    CORRECT --> RATING
    RATING --> OUTPUT
```

### Verification Criteria

The LLM-based verifier evaluates proofs along multiple dimensions:

1. **Logical Consistency**: Each step must follow validly from previous steps and stated premises
2. **Mathematical Correctness**: All mathematical operations and transformations must be valid
3. **Completeness**: The proof must address all necessary cases and close all logical gaps
4. **Clarity**: Reasoning must be explicit enough that each step can be independently verified
5. **Conclusion Validity**: The final statement must match the original theorem to be proved

### Automatic Rating Scale

The `average_automatic_rating` field provides a quantitative assessment:

- **9.0-10.0**: Excellent - Complete, rigorous proof with clear reasoning
- **7.0-8.9**: Good - Correct proof with minor presentation issues
- **5.0-6.9**: Adequate - Generally correct but with gaps or unclear steps
- **3.0-4.9**: Insufficient - Significant logical gaps or errors
- **0.0-2.9**: Poor - Fundamentally flawed reasoning or incorrect conclusion

Sources: Diagram 2 (training architecture with verifier component); section 2.1 objectives (core components)

---

## Proof Structure

Basic problem proofs follow a standardized structure that facilitates both human readability and automated verification:

### Typical Proof Template

```
**Notation and Definitions**
- Define variables and mathematical objects
- State any preliminary assumptions

**Preliminary Results** (if needed)
- Lemmas or known theorems used
- Intermediate results established

**Main Proof**
Case 1: [First scenario]
  - Step 1.1: [Reasoning]
  - Step 1.2: [Derivation]
  - Conclusion for Case 1

Case 2: [Second scenario]
  - Step 2.1: [Reasoning]
  - Step 2.2: [Derivation]
  - Conclusion for Case 2

**Conclusion**
- Synthesis of cases
- Final statement matching theorem
```

**Diagram: Proof Generation and Structure Flow**

```mermaid
graph TD
    subgraph "Proof Generator Logic"
        INPUT["Problem Statement<br/>question field"]
        
        subgraph "Structure Planning"
            PARSE["Parse Requirements<br/>Identify proof strategy"]
            CASES["Determine Cases<br/>Enumerate scenarios"]
            DEPS["Identify Dependencies<br/>Lemmas needed"]
        end
        
        subgraph "Content Generation"
            NOTATION["Generate Notation<br/>Define variables"]
            LEMMAS["Prove Lemmas<br/>Establish prerequisites"]
            MAIN["Main Derivation<br/>Case-by-case proof"]
            CONCLUDE["Synthesize Conclusion<br/>Connect to theorem"]
        end
        
        INPUT --> PARSE
        PARSE --> CASES
        PARSE --> DEPS
        
        DEPS --> NOTATION
        NOTATION --> LEMMAS
        LEMMAS --> MAIN
        CASES --> MAIN
        MAIN --> CONCLUDE
    end
    
    subgraph "Output"
        PROOF["proof field<br/>Complete natural language proof"]
        LATEX["LaTeX Formatting<br/>Mathematical notation"]
    end
    
    CONCLUDE --> PROOF
    PROOF --> LATEX
```

### LaTeX Formatting Conventions

Basic problems use standard LaTeX mathematical notation for clarity:

- **Inline math**: `$x^2 + y^2 = z^2$`
- **Display equations**: `$$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$`
- **Aligned derivations**: `\begin{align*}...\end{align*}`
- **Cases**: `\begin{cases}...\end{cases}`

Sources: Section 4.2 objectives (proof structure); Diagram 3 (output data structure)

---

## Example Problem Structure

To illustrate the Basic Problems format, here is a representative example structure (not actual repository content):

```json
{
  "question": "Prove that for any integer $n \\geq 1$, the sum $1 + 2 + 3 + \\cdots + n = \\frac{n(n+1)}{2}$.",
  "problem_idx": "basic_example_001",
  "model_prediction": {
    "proof": "**Proof by Mathematical Induction**\n\n**Base Case**: For $n=1$:\n  Left side: $1$\n  Right side: $\\frac{1(1+1)}{2} = \\frac{2}{2} = 1$\n  Base case holds. ✓\n\n**Inductive Hypothesis**: Assume the statement holds for some $n=k$:\n  $$1 + 2 + 3 + \\cdots + k = \\frac{k(k+1)}{2}$$\n\n**Inductive Step**: Prove for $n=k+1$:\n  \\begin{align*}\n  1 + 2 + 3 + \\cdots + k + (k+1) &= \\frac{k(k+1)}{2} + (k+1) \\\\\n  &= \\frac{k(k+1) + 2(k+1)}{2} \\\\\n  &= \\frac{(k+1)(k+2)}{2} \\\\\n  &= \\frac{(k+1)((k+1)+1)}{2}\n  \\end{align*}\n\n**Conclusion**: By mathematical induction, the statement holds for all integers $n \\geq 1$. $\\square$",
    "average_automatic_rating": 9.5,
    "human_rating": 10
  }
}
```

This example demonstrates:
- Clear **theorem statement** in the `question` field
- **Structured proof** with distinct sections (base case, hypothesis, inductive step)
- **LaTeX formatting** for mathematical expressions
- **Explicit reasoning** at each step
- **High automatic rating** (9.5) reflecting complete, rigorous proof
- **Human validation** confirming correctness (10)

Sources: Diagram 3 (JSONL schema); section 4.1 objectives (data format documentation)

---

## Performance Metrics

DeepSeek-Math-V2's performance on IMO-ProofBench Basic Problems demonstrates strong foundational theorem proving capabilities:

### Overall Statistics

| Metric | Value | Description |
|--------|-------|-------------|
| **Problem Coverage** | Full set | All Basic problems attempted |
| **Average Automatic Rating** | High confidence | LLM verifier scores indicate reliable proof generation |
| **Verification Success Rate** | Majority verified | Most proofs pass logical consistency checks |
| **Proof Completeness** | Comprehensive | Proofs include all necessary cases and reasoning steps |

### Comparison: Basic vs. Advanced

| Aspect | Basic Problems | Advanced Problems |
|--------|---------------|-------------------|
| **Proof Format** | Natural language + LaTeX | Formal proof assistant syntax |
| **Verification Method** | LLM-based verifier | Formal proof checker |
| **Target Audience** | Human mathematicians | Proof assistant users |
| **Complexity** | Foundational theorems | Complex formal proofs |

**Diagram: Basic Problems in Evaluation Ecosystem**

```mermaid
graph TB
    subgraph "DeepSeek-Math-V2 Evaluation"
        MODEL["DeepSeek-Math-V2<br/>Core System"]
    end
    
    subgraph "Competition Benchmarks"
        IMO["IMO 2025<br/>Gold Medal"]
        CMO["CMO 2024<br/>Gold Medal"]
        PUT["Putnam 2024<br/>118/120"]
    end
    
    subgraph "IMO-ProofBench Benchmarks"
        BASIC["Basic Problems<br/>Natural Language Proofs"]
        ADV["Advanced Problems<br/>Formal Proofs"]
    end
    
    subgraph "Output Files"
        OUT_IMO["IMO2025.jsonl"]
        OUT_CMO["CMO2024.jsonl"]
        OUT_PUT["Putnam2024.jsonl"]
        OUT_BASIC["IMO-ProofBench-Basic.jsonl"]
        OUT_ADV["IMO-ProofBench-Advanced.jsonl"]
    end
    
    MODEL --> IMO
    MODEL --> CMO
    MODEL --> PUT
    MODEL --> BASIC
    MODEL --> ADV
    
    IMO --> OUT_IMO
    CMO --> OUT_CMO
    PUT --> OUT_PUT
    BASIC --> OUT_BASIC
    ADV --> OUT_ADV
    
    BASIC -.->|"Foundation for"| ADV
```

Sources: Diagram 1 (overall system ecosystem); section 3 objectives (evaluation and results)

---

## Accessing Results

The complete results for IMO-ProofBench Basic Problems are stored in the repository's output directory:

**File Location**: `outputs/IMO-ProofBench-Basic.jsonl`

Each line in this file represents one problem-solution pair following the schema documented above. The file can be processed line-by-line using standard JSONL parsing tools.

### Loading and Parsing

To analyze the results programmatically:

1. Read the file line-by-line (each line is valid JSON)
2. Parse each line as a JSON object
3. Extract `question`, `problem_idx`, and `model_prediction` fields
4. Access `proof` text for the complete solution
5. Review `average_automatic_rating` for quality assessment

For detailed information on output data formats and parsing strategies, see [Data Formats & Outputs](#4).

Sources: Diagram 3 (data flow and output structure); section 4 objectives (data formats and outputs)

---

## Relationship to System Components

Basic Problems evaluation integrates directly with DeepSeek-Math-V2's core architecture:

**Diagram: Basic Problems Component Integration**

```mermaid
graph TB
    subgraph "Foundation Model"
        BASE["DeepSeek-V3.2-Exp-Base<br/>Foundation LLM"]
    end
    
    subgraph "DeepSeek-Math-V2"
        GEN["Proof Generator<br/>Trained with verifier rewards"]
        VER["LLM-based Verifier<br/>Proof evaluator"]
    end
    
    subgraph "IMO-ProofBench Basic"
        PROBLEMS["Basic Problem Set<br/>Theorem statements"]
        PROOFS["Generated Proofs<br/>Natural language"]
        RATINGS["Verification Ratings<br/>Quality scores"]
    end
    
    subgraph "Training Feedback"
        IMPROVE["Iterative Improvement<br/>Hard cases feed back"]
        SCALE["Scaled Verification<br/>Compute resources"]
    end
    
    BASE --> GEN
    BASE --> VER
    
    PROBLEMS --> GEN
    GEN --> PROOFS
    PROOFS --> VER
    VER --> RATINGS
    
    PROOFS -.->|"Challenging cases"| IMPROVE
    IMPROVE --> SCALE
    SCALE -.->|"Enhanced training data"| VER
```

The Basic Problems serve multiple roles:
1. **Evaluation Benchmark**: Measure foundational proof generation capability
2. **Training Signal**: Provide feedback for verifier and generator improvement
3. **Quality Baseline**: Establish minimum standards for proof rigor
4. **Scaling Foundation**: Simpler problems enable verification compute scaling strategies

Sources: Diagram 2 (core training architecture); Diagram 6 (generation-verification gap management); section 2.3 objectives (self-verification mechanism)

---

## Related Documentation

- **[IMO-ProofBench](#3.2)**: Parent page covering the complete benchmark system
- **[Advanced Problems](#3.2.2)**: Higher-tier formal proof problems with proof assistant integration
- **[JSONL Schema](#4.1)**: Detailed documentation of common output data structure
- **[Proof Structure](#4.2)**: General proof formatting conventions across all outputs
- **[Evaluation Metrics](#4.3)**: Explanation of rating systems and quality measures

---

