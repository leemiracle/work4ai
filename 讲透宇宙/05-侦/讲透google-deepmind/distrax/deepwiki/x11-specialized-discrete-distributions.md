<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/distrax · extra page Specialized Discrete Distributions · fetched 2026-10-26 -->

# Specialized Discrete Distributions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [distrax/_src/distributions/categorical_uniform.py](distrax/_src/distributions/categorical_uniform.py)
- [distrax/_src/distributions/categorical_uniform_test.py](distrax/_src/distributions/categorical_uniform_test.py)
- [distrax/_src/distributions/mvn_diag_plus_low_rank_test.py](distrax/_src/distributions/mvn_diag_plus_low_rank_test.py)
- [distrax/_src/distributions/mvn_diag_test.py](distrax/_src/distributions/mvn_diag_test.py)
- [distrax/_src/distributions/one_hot_categorical_test.py](distrax/_src/distributions/one_hot_categorical_test.py)

</details>



This section covers specialized discrete distributions that extend beyond the fundamental discrete distributions. These distributions provide specific sampling behaviors and parameterizations for specialized use cases. For basic discrete distributions like Categorical, Bernoulli, and Multinomial, see [Categorical Distribution](#3.1.1) and [Bernoulli and Multinomial](#3.1.2).

## Overview

Distrax provides specialized discrete distributions that offer alternative representations or hybrid behaviors:

| Distribution | Purpose | Key Features |
|--------------|---------|-------------|
| `OneHotCategorical` | One-hot encoded categorical sampling | Samples vectors instead of indices |
| `CategoricalUniform` | Categorical-uniform mixture | Combines discrete choice with continuous uniform components |

These distributions maintain compatibility with JAX transformations and follow the standard Distribution interface.

## OneHotCategorical Distribution

The `OneHotCategorical` distribution extends the categorical distribution by sampling one-hot encoded vectors instead of integer indices. This is particularly useful in scenarios where downstream computations expect one-hot representations.

### Basic Usage and Parameterization

```mermaid
graph TB
    subgraph "OneHotCategorical Parameters"
        LOGITS["logits: Array<br/>Unnormalized log probabilities"]
        PROBS["probs: Array<br/>Normalized probabilities"]
        DTYPE["dtype: Optional<br/>Sample dtype (int32, int64, float32, float64)"]
    end
    
    subgraph "OneHotCategorical Distribution"
        OHC["OneHotCategorical"]
        NUMCAT["num_categories: int"]
        SAMPLE["sample() → one-hot vectors"]
        LOGPROB["log_prob(one_hot_value)"]
    end
    
    subgraph "Special Behaviors"
        NEGPROB["Negative probs → sample = -1"]
        NANPROB["NaN probs → sample = -1"]
        EXTREME["Extreme probs handled"]
    end
    
    LOGITS --> OHC
    PROBS --> OHC
    DTYPE --> OHC
    
    OHC --> NUMCAT
    OHC --> SAMPLE
    OHC --> LOGPROB
    
    OHC --> NEGPROB
    OHC --> NANPROB
    OHC --> EXTREME
```

Sources: [distrax/_src/distributions/one_hot_categorical_test.py:35-65](), [distrax/_src/distributions/one_hot_categorical_test.py:43-54]()

### Relationship to Categorical Distribution

The `OneHotCategorical` distribution maintains mathematical equivalence with `Categorical` while changing the sample representation:

```mermaid
graph LR
    subgraph "Input Space"
        LOGITS_IN["logits: [0.0, 1.0, -0.5]"]
        PROBS_IN["probs: [0.2, 0.5, 0.3]"]
    end
    
    subgraph "Categorical"
        CAT["Categorical"]
        CAT_SAMPLE["sample() → int<br/>0, 1, or 2"]
    end
    
    subgraph "OneHotCategorical"  
        OHC["OneHotCategorical"]
        OHC_SAMPLE["sample() → one-hot<br/>[1,0,0], [0,1,0], [0,0,1]"]
    end
    
    subgraph "Compatibility"
        KL["KL divergence compatible"]
        CROSS["Cross entropy compatible"]
        EQUIV["Mathematically equivalent"]
    end
    
    LOGITS_IN --> CAT
    LOGITS_IN --> OHC
    PROBS_IN --> CAT
    PROBS_IN --> OHC
    
    CAT --> CAT_SAMPLE
    OHC --> OHC_SAMPLE
    
    CAT --> KL
    OHC --> KL
    CAT --> CROSS
    OHC --> CROSS
    CAT --> EQUIV
    OHC --> EQUIV
```

Sources: [distrax/_src/distributions/one_hot_categorical_test.py:379-412](), [distrax/_src/distributions/one_hot_categorical_test.py:21-22]()

### Error Handling and Edge Cases

The `OneHotCategorical` distribution includes robust error handling for invalid probability configurations:

- **Negative probabilities after normalization**: Returns sample values of `-1`
- **NaN probabilities**: Returns sample values of `-1` 
- **Extreme probability values**: Handled gracefully with appropriate log probability calculations
- **Invalid dtype specifications**: Raises `ValueError` for boolean or complex dtypes

Sources: [distrax/_src/distributions/one_hot_categorical_test.py:67-86](), [distrax/_src/distributions/one_hot_categorical_test.py:55-64]()

## CategoricalUniform Distribution

The `CategoricalUniform` distribution represents a mixture of categorical and uniform distributions. It divides a continuous interval into discrete bins, each with uniform probability density within the bin and categorical probability weights between bins.

### Mathematical Formulation

Given an interval `[a, b]` and probability vector `p = [p_1, ..., p_K]`, the PDF is:
- `p(x) = p_k / C` if `(k-1)C ≤ x - a < kC` for `k = 1, ..., K`
- `p(x) = 0` otherwise
- Where `C = (b-a) / K`

```mermaid
graph TB
    subgraph "CategoricalUniform Components"
        INTERVAL["Interval [low, high]"]
        BINS["K bins of equal width C"]
        WEIGHTS["Categorical weights p_k"]
    end
    
    subgraph "Implementation"
        MIXTURE["MixtureSameFamily"]
        UNIFORM_COMP["Uniform components<br/>per bin"]
        CAT_MIXTURE["Categorical mixture<br/>distribution"]
    end
    
    subgraph "Key Methods"
        SAMPLE["_sample_n()<br/>via inverse CDF"]
        LOGPROB["log_prob()<br/>via mixture"]
        ENTROPY["entropy()<br/>sum of components"]
        ICDF["_inverse_cdf()<br/>quantile mapping"]
    end
    
    INTERVAL --> BINS
    BINS --> UNIFORM_COMP
    WEIGHTS --> CAT_MIXTURE
    
    UNIFORM_COMP --> MIXTURE
    CAT_MIXTURE --> MIXTURE
    
    MIXTURE --> SAMPLE
    MIXTURE --> LOGPROB
    MIXTURE --> ENTROPY
    SAMPLE --> ICDF
```

Sources: [distrax/_src/distributions/categorical_uniform.py:35-46](), [distrax/_src/distributions/categorical_uniform.py:119-126]()

### Implementation Architecture

The `CategoricalUniform` distribution is implemented as a wrapper around `MixtureSameFamily`:

```mermaid
graph LR
    subgraph "CategoricalUniform"
        CU["CategoricalUniform"]
        LOW["low: Numeric"]
        HIGH["high: Numeric"] 
        LOGITS["logits: Array"]
    end
    
    subgraph "Internal Mixture"
        MSF["MixtureSameFamily"]
        UNIFORM["Uniform components"]
        CATEGORICAL["Categorical mixture"]
    end
    
    subgraph "Helper Methods"
        LIMITS["_get_category_limits()"]
        MIXTURE_GET["_get_mixture()"]
        INV_CDF["_inverse_cdf()"]
    end
    
    CU --> LOW
    CU --> HIGH
    CU --> LOGITS
    
    CU --> LIMITS
    CU --> MIXTURE_GET
    CU --> INV_CDF
    
    MIXTURE_GET --> MSF
    MSF --> UNIFORM
    MSF --> CATEGORICAL
    
    LIMITS --> UNIFORM
    LOGITS --> CATEGORICAL
```

Sources: [distrax/_src/distributions/categorical_uniform.py:115-126](), [distrax/_src/distributions/categorical_uniform.py:85-89]()

### Broadcasting and Batch Operations

The `CategoricalUniform` distribution supports flexible broadcasting across its parameters:

| Parameter | Shape Requirements | Broadcast Behavior |
|-----------|-------------------|-------------------|
| `low` | Scalar or batch shape | Broadcasted to batch shape |
| `high` | Scalar or batch shape | Broadcasted to batch shape |  
| `logits` | `(..., K)` where K > 0 | Last dimension determines `num_bins` |

The batch shape is determined by: `jax.lax.broadcast_shapes(low.shape, high.shape, logits.shape[:-1])`

Sources: [distrax/_src/distributions/categorical_uniform.py:80-83](), [distrax/_src/distributions/categorical_uniform_test.py:26-123]()

## Distribution Relationships

These specialized discrete distributions maintain important relationships with core Distrax distributions:

```mermaid
graph TB
    subgraph "Core Discrete"
        CAT["Categorical"]
        BERN["Bernoulli"] 
        MULT["Multinomial"]
    end
    
    subgraph "Specialized Discrete"
        OHC["OneHotCategorical"]
        CU["CategoricalUniform"]
    end
    
    subgraph "Continuous"
        UNIFORM["Uniform"]
    end
    
    subgraph "Meta"
        MSF["MixtureSameFamily"]
    end
    
    CAT -.->|"mathematical equivalence"| OHC
    CAT -->|"mixture component"| CU
    UNIFORM -->|"bin components"| CU
    MSF -->|"implementation"| CU
    
    OHC -.->|"KL divergence"| CAT
    OHC -.->|"cross entropy"| CAT
```

Sources: [distrax/_src/distributions/one_hot_categorical_test.py:379-412](), [distrax/_src/distributions/categorical_uniform.py:22-23]()

---

