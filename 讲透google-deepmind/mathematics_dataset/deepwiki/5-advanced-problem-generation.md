<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mathematics_dataset · page 5 Advanced Problem Generation · fetched 2026-10-26 -->

# Advanced Problem Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mathematics_dataset/sample/arithmetic.py](mathematics_dataset/sample/arithmetic.py)
- [mathematics_dataset/sample/linear_system.py](mathematics_dataset/sample/linear_system.py)

</details>



This document covers specialized utilities for generating complex mathematical structures that serve as building blocks for more sophisticated problem types. The system provides two main advanced generation capabilities: controlled arithmetic expression generation and linear system construction with predetermined solutions.

For basic mathematical infrastructure like number generation and expression trees, see [Mathematical Infrastructure](#3.2). For how these utilities integrate into domain-specific problem generation, see [Mathematical Domain Modules](#4).

## System Overview

The advanced problem generation system consists of two primary utilities that generate mathematical structures with precise control over complexity and target outcomes:

```mermaid
graph TB
    subgraph "Domain_Modules" ["Domain Modules"]
        ALG["algebra.py"]
        ARITH_MOD["arithmetic.py (module)"]
        CALC["calculus.py"]
    end
    
    subgraph "Advanced_Generation" ["Advanced Generation Utilities"]
        ARITH_SAMPLE["sample/arithmetic.py"]
        LINEAR_SAMPLE["sample/linear_system.py"]
    end
    
    subgraph "Core_Infrastructure" ["Core Mathematical Infrastructure"]
        NUMBER["sample/number.py"]
        OPS["sample/ops.py"]
        POLY["sample/polynomials.py"]
    end
    
    subgraph "Generated_Structures" ["Generated Mathematical Structures"]
        EXPR["Arithmetic Expressions"]
        SYSTEMS["Linear Equation Systems"]
    end
    
    ALG --> ARITH_SAMPLE
    ALG --> LINEAR_SAMPLE
    ARITH_MOD --> ARITH_SAMPLE
    CALC --> ARITH_SAMPLE
    
    ARITH_SAMPLE --> EXPR
    LINEAR_SAMPLE --> SYSTEMS
    
    ARITH_SAMPLE --> NUMBER
    ARITH_SAMPLE --> OPS
    LINEAR_SAMPLE --> NUMBER
    LINEAR_SAMPLE --> OPS
    LINEAR_SAMPLE --> POLY
    
    EXPR --> "Target Value Problems"
    SYSTEMS --> "System Solving Problems"
```

**Sources:** [mathematics_dataset/sample/arithmetic.py:1-261](), [mathematics_dataset/sample/linear_system.py:1-145]()

## Arithmetic Expression Generator

The arithmetic expression generator creates mathematical expressions that evaluate to a specified target value while controlling complexity through entropy-based sampling.

### Core Generation Process

```mermaid
flowchart TD
    START["arithmetic(value, entropy, length=None)"] --> VALIDATE["Validate Parameters"]
    VALIDATE --> LENGTH_CALC{"Length Specified?"}
    
    LENGTH_CALC -->|No| LENGTH_EST["length_range_for_entropy(entropy)"]
    LENGTH_EST --> LENGTH_SAMPLE["Random length selection"]
    LENGTH_SAMPLE --> ENTROPY_ADJ["Entropy adjustment"]
    
    LENGTH_CALC -->|Yes| ENTROPY_ADJ
    ENTROPY_ADJ --> SAMPLE_ARGS["_SampleArgs(length, entropy)"]
    
    SAMPLE_ARGS --> RECURSIVE["_arithmetic(value, sample_args, add_sub, mul_div)"]
    
    RECURSIVE --> COUNT_CHECK{"sample_args.count == 0?"}
    COUNT_CHECK -->|Yes| CONSTANT["ops.Constant(value)"]
    COUNT_CHECK -->|No| OP_FILTER["Filter available operations"]
    
    OP_FILTER --> ADD_SUB_CHECK["_add_sub_filter()"]
    OP_FILTER --> MUL_FILTER["_mul_filter()"]
    OP_FILTER --> DIV_FILTER["_div_filter()"]
    
    ADD_SUB_CHECK --> OP_CHOICE["random.choice(allowed_ops)"]
    MUL_FILTER --> OP_CHOICE
    DIV_FILTER --> OP_CHOICE
    
    OP_CHOICE --> ADD_OP["_add_op()"]
    OP_CHOICE --> SUB_OP["_sub_op()"]
    OP_CHOICE --> MUL_OP["_mul_op()"]
    OP_CHOICE --> DIV_OP["_div_op()"]
    
    ADD_OP --> SPLIT_ENTROPY["sample_args.split(args)"]
    SUB_OP --> SPLIT_ENTROPY
    MUL_OP --> SPLIT_ENTROPY
    DIV_OP --> SPLIT_ENTROPY
    
    SPLIT_ENTROPY --> RECURSE["Recursive call for each argument"]
    RECURSE --> CONSTRUCT["Construct ops.Op tree"]
    
    CONSTANT --> RETURN["Return expression"]
    CONSTRUCT --> RETURN
```

**Sources:** [mathematics_dataset/sample/arithmetic.py:229-261](), [mathematics_dataset/sample/arithmetic.py:193-220]()

### Entropy Management and Operation Selection

The system uses a sophisticated entropy distribution mechanism through the `_SampleArgs` class:

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `peel(frac=1)` | Allocates portion of entropy to current operation | [mathematics_dataset/sample/arithmetic.py:38-42]() |
| `split(args)` | Distributes remaining entropy among child expressions | [mathematics_dataset/sample/arithmetic.py:44-61]() |

The operation selection follows these filtering rules:

```mermaid
graph TB
    VALUE_TYPE{"Value Type"}
    COUNT_CHECK{"Operation Count"}
    ENTROPY_CHECK{"Available Entropy"}
    
    VALUE_TYPE -->|Integer| INT_PATH["Integer operations available"]
    VALUE_TYPE -->|Rational| RAT_PATH["Rational operations available"]
    
    COUNT_CHECK -->|>= 2| MULTI_OP["Multi-argument operations"]
    COUNT_CHECK -->|< 2| SINGLE_OP["Single-argument operations"]
    
    ENTROPY_CHECK -->|Sufficient| COMPLEX_OP["Complex factorization allowed"]
    ENTROPY_CHECK -->|Limited| SIMPLE_OP["Simple operations only"]
    
    INT_PATH --> ADD_SUB_ALLOW["_add_sub_filter: Always allowed"]
    INT_PATH --> MUL_ALLOW["_mul_filter: Check _entropy_of_factor_split"]
    
    RAT_PATH --> ADD_SUB_ALLOW
    RAT_PATH --> MUL_ALLOW
    RAT_PATH --> DIV_ALLOW["_div_filter: Always allowed"]
    
    MUL_ALLOW --> FACTOR_ENTROPY["_entropy_of_factor_split(integer)"]
    FACTOR_ENTROPY --> FACTOR_CALC["sum(log10(mult + 1) for factors)"]
```

**Sources:** [mathematics_dataset/sample/arithmetic.py:63-128](), [mathematics_dataset/sample/arithmetic.py:95-103]()

### Operation Implementation Details

Each operation type implements specific logic for maintaining the target value:

| Operation | Strategy | Key Function |
|-----------|----------|--------------|
| Addition | `value = x + (value - x)` | [mathematics_dataset/sample/arithmetic.py:67-78]() |
| Subtraction | `value = (value + x) - x` or `value = x - (x - value)` | [mathematics_dataset/sample/arithmetic.py:81-92]() |
| Multiplication | Factor splitting with `_split_factors()` | [mathematics_dataset/sample/arithmetic.py:130-152]() |
| Division | Rational construction preserving value | [mathematics_dataset/sample/arithmetic.py:161-190]() |

**Sources:** [mathematics_dataset/sample/arithmetic.py:105-119](), [mathematics_dataset/sample/arithmetic.py:67-190]()

## Linear System Generator

The linear system generator creates systems of linear equations with predetermined solutions, ensuring mathematical consistency while controlling problem complexity.

### System Construction Process

```mermaid
flowchart TD
    START["linear_system(variables, solutions, entropy)"] --> VALIDATE["Validate inputs"]
    VALIDATE --> ENTROPY_SPLIT["Split entropy: matrix vs coefficients"]
    
    ENTROPY_SPLIT --> MATRIX_GEN["_invertible_matrix(degree, entropy_matrix)"]
    MATRIX_GEN --> MATRIX_LOOP{"Matrix valid?"}
    
    MATRIX_LOOP -->|No| MATRIX_REGEN["Regenerate matrix entries"]
    MATRIX_REGEN --> DET_CHECK["sympy.det(matrix) != 0"]
    DET_CHECK -->|False| MATRIX_REGEN
    DET_CHECK -->|True| TRIVIAL_CHECK["_is_trivial_in check"]
    
    MATRIX_LOOP -->|Yes| CONSTANT_CALC["constant = matrix @ solutions"]
    TRIVIAL_CHECK -->|Passes| CONSTANT_CALC
    TRIVIAL_CHECK -->|Fails| MATRIX_REGEN
    
    CONSTANT_CALC --> LENGTH_CALC{"Length specified?"}
    LENGTH_CALC -->|No| LENGTH_EST["Estimate from entropy and degree"]
    LENGTH_CALC -->|Yes| COEFF_DIST["polynomials.expanded_coefficient_counts"]
    LENGTH_EST --> COEFF_DIST
    
    COEFF_DIST --> ENTROPY_DIST["Distribute remaining entropy"]
    ENTROPY_DIST --> TERM_GEN["Generate coefficient terms"]
    
    TERM_GEN --> POLY_TERMS["polynomials.integers_with_sum"]
    POLY_TERMS --> MONOMIAL_BUILD["Build monomials for each equation"]
    MONOMIAL_BUILD --> EQUATION_SPLIT["_make_equals_zero_split"]
    
    EQUATION_SPLIT --> RETURN["Return list of ops.Eq"]
```

**Sources:** [mathematics_dataset/sample/linear_system.py:88-144](), [mathematics_dataset/sample/linear_system.py:68-85]()

### Matrix Generation and Validation

The system ensures mathematical validity through multiple validation layers:

```mermaid
graph TB
    subgraph "Matrix_Generation" ["Matrix Generation"]
        ENTROPY_DIST["Entropy distribution via Dirichlet"]
        ENTRY_GEN["number.integer() for each entry"]
        MATRIX_CONSTRUCT["Construct degree × degree matrix"]
    end
    
    subgraph "Validation_Layers" ["Validation Layers"]
        DET_CHECK["Determinant ≠ 0"]
        TRIVIAL_CHECK["Non-trivial constraint"]
        INVERTIBLE["Matrix invertibility"]
    end
    
    subgraph "System_Construction" ["System Construction"]
        SOLUTION_MULT["constant = matrix @ solutions"]
        COEFF_EXPANSION["Coefficient term expansion"]
        EQUATION_BUILD["Equation construction"]
    end
    
    ENTROPY_DIST --> ENTRY_GEN
    ENTRY_GEN --> MATRIX_CONSTRUCT
    MATRIX_CONSTRUCT --> DET_CHECK
    DET_CHECK --> TRIVIAL_CHECK
    TRIVIAL_CHECK --> INVERTIBLE
    
    INVERTIBLE --> SOLUTION_MULT
    SOLUTION_MULT --> COEFF_EXPANSION
    COEFF_EXPANSION --> EQUATION_BUILD
```

The non-triviality check prevents systems where one equation reduces to a single variable:

**Sources:** [mathematics_dataset/sample/linear_system.py:50-66](), [mathematics_dataset/sample/linear_system.py:68-85]()

### Equation Assembly

The final equations are constructed by distributing coefficient terms and creating balanced expressions:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| Monomial construction | Creates `term * variable^power` expressions | [mathematics_dataset/sample/linear_system.py:139]() |
| Zero-sum splitting | Randomly distributes terms between equation sides | [mathematics_dataset/sample/linear_system.py:32-47]() |
| Equation balancing | Ensures left side equals right side | [mathematics_dataset/sample/linear_system.py:45-47]() |

**Sources:** [mathematics_dataset/sample/linear_system.py:126-144](), [mathematics_dataset/sample/linear_system.py:32-47]()

## Integration with Problem Generation

These advanced utilities serve as foundational components for higher-level problem generation across multiple mathematical domains:

```mermaid
graph LR
    subgraph "Problem_Types" ["Generated Problem Types"]
        SOLVE_EQ["Solve for x in expression"]
        SIMPLIFY["Simplify complex expressions"]
        SYSTEM_SOLVE["Solve system of equations"]
        VALUE_FIND["Find expression value"]
    end
    
    subgraph "Utility_Usage" ["Utility Functions"]
        ARITH_GEN["arithmetic(target_value, entropy)"]
        LINEAR_GEN["linear_system(vars, solutions, entropy)"]
    end
    
    subgraph "Domain_Integration" ["Domain Modules"]
        ALG_MODULE["algebra.py problems"]
        ARITH_MODULE["arithmetic.py problems"]
        CALC_MODULE["calculus.py problems"]
    end
    
    ARITH_GEN --> SOLVE_EQ
    ARITH_GEN --> SIMPLIFY
    ARITH_GEN --> VALUE_FIND
    
    LINEAR_GEN --> SYSTEM_SOLVE
    
    ALG_MODULE --> ARITH_GEN
    ALG_MODULE --> LINEAR_GEN
    ARITH_MODULE --> ARITH_GEN
    CALC_MODULE --> ARITH_GEN
```

The entropy-based complexity control allows these utilities to generate problems appropriate for different difficulty levels while maintaining mathematical correctness and educational value.

**Sources:** [mathematics_dataset/sample/arithmetic.py:229-261](), [mathematics_dataset/sample/linear_system.py:88-144]()

---

