<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/formal-conjectures · extra page Arxiv Paper Problems · fetched 2026-10-26 -->

# Arxiv Paper Problems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [FormalConjectures/Arxiv/0911.2077/Conjecture6_3.lean](FormalConjectures/Arxiv/0911.2077/Conjecture6_3.lean)
- [FormalConjectures/Arxiv/0912.2382/CurlingNumberConjecture.lean](FormalConjectures/Arxiv/0912.2382/CurlingNumberConjecture.lean)
- [FormalConjectures/Arxiv/1601.03081/UniqueCrystalComponents.lean](FormalConjectures/Arxiv/1601.03081/UniqueCrystalComponents.lean)
- [FormalConjectures/Arxiv/1609.08688/sIncreasingrTuples.lean](FormalConjectures/Arxiv/1609.08688/sIncreasingrTuples.lean)
- [FormalConjectures/Arxiv/2107.12475/CollatzLike.lean](FormalConjectures/Arxiv/2107.12475/CollatzLike.lean)
- [FormalConjectures/Arxiv/2208.14736/ZariskiCancellation.lean](FormalConjectures/Arxiv/2208.14736/ZariskiCancellation.lean)

</details>



This document covers the formalization of mathematical conjectures and theorems sourced from academic papers published on arXiv. These formalizations represent contemporary research problems across diverse mathematical domains including combinatorics, number theory, probability theory, and algebraic geometry.

For problems from other academic sources, see [MathOverflow Community Problems](#3.2.2). For classical problem collections, see [Erdős Problems](#3.3).

## Organization Structure

The arXiv formalizations are organized by paper ID in the directory structure `FormalConjectures/Arxiv/{paper_id}/`, where each paper ID corresponds to the arXiv identifier. Each formalization includes complete bibliographic references and maintains connections to the original mathematical research.

```mermaid
graph TD
    ArxivRoot["FormalConjectures/Arxiv/"] --> Paper1["1609.08688/"]
    ArxivRoot --> Paper2["0911.2077/"]  
    ArxivRoot --> Paper3["1601.03081/"]
    ArxivRoot --> Paper4["0912.2382/"]
    ArxivRoot --> Paper5["2107.12475/"]
    ArxivRoot --> Paper6["2208.14736/"]
    
    Paper1 --> File1["sIncreasingrTuples.lean"]
    Paper2 --> File2["Conjecture6_3.lean"] 
    Paper3 --> File3["UniqueCrystalComponents.lean"]
    Paper4 --> File4["CurlingNumberConjecture.lean"]
    Paper5 --> File5["CollatzLike.lean"]
    Paper6 --> File6["ZariskiCancellation.lean"]
    
    File1 --> Namespace1["Arxiv.«1609.08688»"]
    File2 --> Namespace2["Arxiv.«0911.2077»"]
    File3 --> Namespace3["Arxiv.«1601.03081»"]
    File4 --> Namespace4["Arxiv.«0912.2382»"]
    File5 --> Namespace5["Arxiv.«2107.12475»"]
    File6 --> Namespace6["Arxiv.«2208.14736»"]
```

Sources: [FormalConjectures/Arxiv/1609.08688/sIncreasingrTuples.lean:1-232](), [FormalConjectures/Arxiv/0911.2077/Conjecture6_3.lean:1-57](), [FormalConjectures/Arxiv/1601.03081/UniqueCrystalComponents.lean:1-55](), [FormalConjectures/Arxiv/0912.2382/CurlingNumberConjecture.lean:1-57](), [FormalConjectures/Arxiv/2107.12475/CollatzLike.lean:1-51](), [FormalConjectures/Arxiv/2208.14736/ZariskiCancellation.lean:1-75]()

## Mathematical Domain Coverage

The arXiv paper problems span multiple mathematical disciplines with formal categorization through the `@AMS` attribute system.

```mermaid
graph LR
    subgraph "Number Theory (AMS 11)"
        NT1["IsCrystalWithComponents"]
        NT2["k (curling number)"]
        NT3["CollatzLike"]
    end
    
    subgraph "Combinatorics (AMS 5)"
        C1["lt₂ (2-less relation)"]
        C2["IsIncreasing₂"]
        C3["maximalLength (F function)"]
        C4["CollatzLike"]
    end
    
    subgraph "Probability Theory (AMS 60)"
        P1["arxiv.id0911_2077.conjecture6_3"]
        P2["PMF.binomial"]
        P3["cdf gaussianReal"]
    end
    
    subgraph "Algebra (AMS 13, 14)"
        A1["IsCancellative"]
        A2["MvPolynomial"]
        A3["AlgEquiv"]
    end
    
    subgraph "Real Functions (AMS 26)"
        R1["IsCrystalWithComponents"]
        R2["Real.sqrt"]
    end
    
    NT1 --> ArxivPaper1["1601.03081"]
    NT2 --> ArxivPaper2["0912.2382"] 
    NT3 --> ArxivPaper3["2107.12475"]
    
    C1 --> ArxivPaper4["1609.08688"]
    C2 --> ArxivPaper4
    C3 --> ArxivPaper4
    C4 --> ArxivPaper3
    
    P1 --> ArxivPaper5["0911.2077"]
    P2 --> ArxivPaper5
    P3 --> ArxivPaper5
    
    A1 --> ArxivPaper6["2208.14736"]
    A2 --> ArxivPaper6
    A3 --> ArxivPaper6
    
    R1 --> ArxivPaper1
    R2 --> ArxivPaper4
```

Sources: [FormalConjectures/Arxiv/1609.08688/sIncreasingrTuples.lean:44-228](), [FormalConjectures/Arxiv/0911.2077/Conjecture6_3.lean:45-54](), [FormalConjectures/Arxiv/1601.03081/UniqueCrystalComponents.lean:36-52](), [FormalConjectures/Arxiv/0912.2382/CurlingNumberConjecture.lean:52-54](), [FormalConjectures/Arxiv/2107.12475/CollatzLike.lean:40-48](), [FormalConjectures/Arxiv/2208.14736/ZariskiCancellation.lean:44-72]()

## Formalization Patterns

All arXiv formalizations follow consistent structural patterns using the repository's infrastructure.

| Component | Purpose | Example |
|-----------|---------|---------|
| `ProblemImports` | Standard imports | `import FormalConjectures.Util.ProblemImports` |
| Namespace | Paper organization | `namespace Arxiv.«1609.08688»` |
| Documentation | References and context | `/-! # The length of an $s$-increasing sequence...` |
| Category attributes | Research status | `@[category research open, AMS 5]` |
| Theorem statements | Formal conjectures | `theorem maximalLength_le_strong` |

### Common Infrastructure Usage

```mermaid
graph TD
    ProblemImports["ProblemImports"] --> AllFiles["All Arxiv Files"]
    
    subgraph "Attribute System"
        CategoryOpen["@category research open"]
        CategorySolved["@category research solved"] 
        CategoryTest["@category test"]
        CategoryAPI["@category API"]
        AMSClass["@AMS classification"]
    end
    
    subgraph "Theorem Structure"
        Definition["Mathematical Definitions"]
        Theorem["Theorem Statements"]
        Sorry["sorry placeholders"]
    end
    
    AllFiles --> CategoryOpen
    AllFiles --> CategorySolved
    AllFiles --> CategoryTest 
    AllFiles --> CategoryAPI
    AllFiles --> AMSClass
    
    AllFiles --> Definition
    AllFiles --> Theorem
    AllFiles --> Sorry
    
    CategoryOpen --> OpenProblems["Unsolved Conjectures"]
    CategorySolved --> SolvedProblems["Known Results"]
    CategoryTest --> Examples["Test Cases"]
    CategoryAPI --> Utilities["API Functions"]
```

Sources: [FormalConjectures/Arxiv/1609.08688/sIncreasingrTuples.lean:17-17](), [FormalConjectures/Arxiv/0911.2077/Conjecture6_3.lean:17-17](), [FormalConjectures/Arxiv/1601.03081/UniqueCrystalComponents.lean:17-17]()

## Featured Problems

### s-Increasing r-Tuples (1609.08688)

This formalization addresses combinatorial sequences with specific ordering properties, implementing the core `lt₂` relation and maximal length functions.

**Key Definitions:**
- `lt₂`: The 2-less relation between triples
- `IsIncreasing₂`: Pairwise 2-less property for sequences  
- `maximalLength`: Maximum length function `F(n)`

**Major Conjectures:**
- `maximalLength_le_strong`: Upper bound `F(n) ≤ n^(3/2)`
- `maximalLength_le_isBigO`: Asymptotic bound with iterated logarithm

Sources: [FormalConjectures/Arxiv/1609.08688/sIncreasingrTuples.lean:39-229]()

### Central Binomial Tail Bounds (0911.2077) 

Probability theory formalization focusing on binomial distribution tail bounds and normal approximations.

**Key Components:**
- `cdf (gaussianReal 0 1)`: Standard normal distribution function `Φ`  
- `PMF.binomial`: Binomial probability mass function
- Integration with `ProbabilityTheory` namespace

**Main Conjecture:**
- `arxiv.id0911_2077.conjecture6_3`: Lower bound for binomial tail probability

Sources: [FormalConjectures/Arxiv/0911.2077/Conjecture6_3.lean:32-54]()

### Zariski Cancellation Problem (2208.14736)

Algebraic geometry formalization addressing polynomial ring isomorphisms and cancellation properties.

**Core Definition:**
- `IsCancellative`: Cancellation property for finitely generated algebras

**Problem Variants:**
- `zariski_cancellation_problem`: Main conjecture for characteristic zero
- `zariski_cancellation_problem.variants.dim_one`: Single variable case (solved)
- `zariski_cancellation_problem.variants.false_pos_card`: Counterexample in positive characteristic

Sources: [FormalConjectures/Arxiv/2208.14736/ZariskiCancellation.lean:35-72]()

## Research Status Distribution

The arXiv problems demonstrate diverse solution statuses across the mathematical research spectrum:

| Status | Count | Examples |
|--------|--------|----------|
| `research open` | 5 | `maximalLength_le_strong`, `crystals_components_unique` |
| `research solved` | 5 | `maximalLength_le`, `zariski_cancellation_problem.variants.dim_one` |
| `test` | 6 | `lt₂_example_1`, `isCrystalWithComponents_35_5_7` |
| `API` | 8 | `not_lt₂`, `tripleProduct_const` |

Sources: [FormalConjectures/Arxiv/1609.08688/sIncreasingrTuples.lean:44-231](), [FormalConjectures/Arxiv/1601.03081/UniqueCrystalComponents.lean:36-52](), [FormalConjectures/Arxiv/2208.14736/ZariskiCancellation.lean:44-72]()

---

