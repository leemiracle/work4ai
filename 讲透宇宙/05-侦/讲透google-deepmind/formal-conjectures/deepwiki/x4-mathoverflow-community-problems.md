<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/formal-conjectures · extra page MathOverflow Community Problems · fetched 2026-10-26 -->

# MathOverflow Community Problems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [FormalConjectures/Mathoverflow/339137.lean](FormalConjectures/Mathoverflow/339137.lean)
- [FormalConjectures/Mathoverflow/347178.lean](FormalConjectures/Mathoverflow/347178.lean)
- [FormalConjectures/Other/BeaverMathOlympiad.lean](FormalConjectures/Other/BeaverMathOlympiad.lean)
- [FormalConjectures/Other/EquationalTheories_677_255.lean](FormalConjectures/Other/EquationalTheories_677_255.lean)

</details>



This document covers mathematical problems sourced from MathOverflow community discussions, focusing on their formalization within the FormalConjectures repository. These problems represent contemporary research questions posed by the mathematical community on the MathOverflow platform.

For problems from academic papers, see [Arxiv Paper Problems](#3.2.1). For other research collections, see [Erdős Problems](#3.3).

## Overview

The MathOverflow problems collection contains formalizations of mathematical questions posted on the MathOverflow community platform. These problems span multiple mathematical domains, with particular emphasis on analysis and algebraic questions. Each problem preserves the original community context while providing rigorous Lean formulations suitable for formal verification.

## Problem Collection Structure

The MathOverflow problems are organized within the `FormalConjectures/Mathoverflow/` directory, with each problem file named after the corresponding MathOverflow question ID.

```mermaid
graph TD
    subgraph "MathOverflow Problems Directory"
        MO["FormalConjectures/Mathoverflow/"]
        MO347178["347178.lean"]
        MO339137["339137.lean"]
        
        MO --> MO347178
        MO --> MO339137
    end
    
    subgraph "Problem Components"
        Namespace["Problem Namespace"]
        MainTheorem["Main Theorem"]
        Variants["Theorem Variants"]
        Definitions["Supporting Definitions"]
    end
    
    subgraph "Core Integration"
        ProblemImports["ProblemImports"]
        AnswerSystem["answer() System"]
        CategoryAttr["@category Attributes"]
        AMSAttr["@AMS Attributes"]
    end
    
    MO347178 --> Namespace
    MO339137 --> Namespace
    
    Namespace --> MainTheorem
    Namespace --> Variants
    Namespace --> Definitions
    
    MainTheorem --> AnswerSystem
    MainTheorem --> CategoryAttr
    MainTheorem --> AMSAttr
    
    ProblemImports --> MO347178
    ProblemImports --> MO339137
```

Sources: [FormalConjectures/Mathoverflow/347178.lean:1-67](), [FormalConjectures/Mathoverflow/339137.lean:1-57]()

## Individual Problems

### MathOverflow 347178: Suprema and Gradients

This problem, posed by user Biagio Ricceri, investigates the relationship between the supremum of a C¹ function and the supremum of the function evaluated at gradient-shifted points.

```mermaid
graph TB
    subgraph "Problem 347178 Structure"
        MO347178File["347178.lean"]
        MO347178NS["Mathoverflow347178 namespace"]
        
        MainQ["mathoverflow_347178"]
        VariantBounded["mathoverflow_347178.variants.bounded_iff"] 
        VariantBoundedOnly["mathoverflow_347178.variants.bounded_only"]
    end
    
    subgraph "Mathematical Components"
        EuclideanSpace["EuclideanSpace ℝ (Fin n)"]
        ContDiff["ContDiff ℝ 1 f"]
        Gradient["gradient f x"]
        BddAbove["BddAbove (range f)"]
        Suprema["⨆ x, f x"]
    end
    
    subgraph "Formalization Details"
        CategoryOpenResearch["@category research open"]
        AMS26["@AMS 26"]
        AnswerSorry["answer(sorry)"]
    end
    
    MO347178File --> MO347178NS
    MO347178NS --> MainQ
    MO347178NS --> VariantBounded
    MO347178NS --> VariantBoundedOnly
    
    MainQ --> EuclideanSpace
    MainQ --> ContDiff
    MainQ --> Gradient
    MainQ --> BddAbove
    MainQ --> Suprema
    
    MainQ --> CategoryOpenResearch
    MainQ --> AMS26
    MainQ --> AnswerSorry
```

The main theorem `mathoverflow_347178` [FormalConjectures/Mathoverflow/347178.lean:35-40]() asks whether for C¹ functions f: ℝⁿ → ℝ with n ≥ 2, the equality sup_{x∈ℝⁿ} f(x) = sup_{x∈ℝⁿ} f(x + ∇f(x)) holds. Two variants explore related questions about boundedness equivalence and finite suprema cases.

Sources: [FormalConjectures/Mathoverflow/347178.lean:21-66]()

### MathOverflow 339137: Zero-One Polynomial Factorization

This problem, asked by user Sil, examines whether polynomials with coefficients in {0,1} tend to have factors with coefficients also in {0,1}.

```mermaid
graph TB
    subgraph "Problem 339137 Structure"
        MO339137File["339137.lean"]
        MO339137NS["Mathoverflow339137 namespace"]
        
        IsZeroOneDef["IsZeroOne definition"]
        MainTheorem["mathoverflow_339137"]
    end
    
    subgraph "Mathematical Components"
        Polynomial["ℝ[X]"]
        Monic["P.Monic"]
        Coeffs["P.coeffs"]
        NonNegCoeffs["∀ c ∈ P.coeffs, 0 ≤ c"]
        ProductRel["R = P * Q"]
    end
    
    subgraph "Formalization Details"
        CategoryOpenResearch["@category research open"]
        AMS12["@AMS 12"]
        IsZeroOneSubset["P.coeffs ⊆ {1}"]
    end
    
    MO339137File --> MO339137NS
    MO339137NS --> IsZeroOneDef
    MO339137NS --> MainTheorem
    
    IsZeroOneDef --> IsZeroOneSubset
    MainTheorem --> Polynomial
    MainTheorem --> Monic
    MainTheorem --> Coeffs
    MainTheorem --> NonNegCoeffs
    MainTheorem --> ProductRel
    
    MainTheorem --> CategoryOpenResearch
    MainTheorem --> AMS12
```

The `IsZeroOne` predicate [FormalConjectures/Mathoverflow/339137.lean:40]() defines polynomials whose nonzero coefficients are all 1. The main theorem [FormalConjectures/Mathoverflow/339137.lean:50-54]() states that if monic polynomials P and Q with non-negative coefficients have a product R that is zero-one, then both P and Q are zero-one polynomials.

Sources: [FormalConjectures/Mathoverflow/339137.lean:21-56]()

## Code Organization and Integration

The MathOverflow problems follow standardized organizational patterns that integrate with the core FormalConjectures infrastructure:

| Component | Implementation | Purpose |
|-----------|----------------|---------|
| File Structure | `FormalConjectures/Mathoverflow/{ID}.lean` | Organized by MathOverflow question ID |
| Namespace | `Mathoverflow{ID}` | Scoped problem definitions |
| Imports | `FormalConjectures.Util.ProblemImports` | Standard infrastructure access |
| Categories | `@category research open` | Research status classification |
| AMS Codes | `@AMS {code}` | Mathematical subject classification |
| Answer Status | `answer(sorry)` | Unknown resolution status |

```mermaid
graph LR
    subgraph "Standard Pattern"
        FileNaming["ID-based naming"]
        NamespaceConvention["Mathoverflow{ID} namespace"]
        ImportStructure["ProblemImports import"]
        AttributePattern["@category + @AMS attributes"]
        AnswerIntegration["answer() system usage"]
    end
    
    subgraph "Core Systems"
        ProblemImports["ProblemImports utility"]
        CategorySystem["Category attribute system"] 
        AMSSystem["AMS attribute system"]
        AnswerElaborator["answer() elaborator"]
    end
    
    subgraph "Quality Control"
        CategoryLinter["Category linter validation"]
        AMSLinter["AMS linter validation"] 
        CopyrightLinter["Copyright linter validation"]
    end
    
    FileNaming --> ProblemImports
    NamespaceConvention --> ProblemImports
    ImportStructure --> ProblemImports
    
    AttributePattern --> CategorySystem
    AttributePattern --> AMSSystem
    AnswerIntegration --> AnswerElaborator
    
    CategorySystem --> CategoryLinter
    AMSSystem --> AMSLinter
    ProblemImports --> CopyrightLinter
```

Sources: [FormalConjectures/Mathoverflow/347178.lean:17-18](), [FormalConjectures/Mathoverflow/339137.lean:17-18](), [FormalConjectures/Mathoverflow/347178.lean:28-29](), [FormalConjectures/Mathoverflow/339137.lean:32-33]()

## Mathematical Domain Coverage

The MathOverflow problems currently span two primary AMS classification areas:

| AMS Code | Domain | Problems | Examples |
|----------|---------|----------|----------|
| 26 | Real Functions | MathOverflow 347178 | Suprema equality, gradient analysis |
| 12 | Field Theory and Polynomials | MathOverflow 339137 | Zero-one coefficient factorization |

Each problem preserves the original MathOverflow context through documentation comments that include the original question URL and author attribution, maintaining traceability to the community source.

Sources: [FormalConjectures/Mathoverflow/347178.lean:34](), [FormalConjectures/Mathoverflow/339137.lean:49](), [FormalConjectures/Mathoverflow/347178.lean:24-26](), [FormalConjectures/Mathoverflow/339137.lean:28-30]()

---

