<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/distrax · extra page Bernoulli and Multinomial · fetched 2026-10-26 -->

# Bernoulli and Multinomial

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [distrax/_src/distributions/bernoulli.py](distrax/_src/distributions/bernoulli.py)
- [distrax/_src/distributions/log_stddev_normal_test.py](distrax/_src/distributions/log_stddev_normal_test.py)
- [distrax/_src/distributions/multinomial.py](distrax/_src/distributions/multinomial.py)
- [distrax/_src/distributions/multinomial_test.py](distrax/_src/distributions/multinomial_test.py)

</details>



This document covers the discrete probability distributions for binary outcomes (Bernoulli) and categorical count data (Multinomial) in Distrax. These distributions are fundamental building blocks for modeling categorical data and binary decisions in probabilistic machine learning.

For continuous probability distributions, see [Normal and Uniform Distributions](#3.2.1). For categorical distributions without fixed trial counts, see [Categorical Distribution](#3.1.1).

## Overview

Distrax provides two key discrete count distributions:

- **Bernoulli**: Models binary outcomes (0 or 1) with a single probability parameter
- **Multinomial**: Models count data across multiple categories with a fixed number of trials

Both distributions support parameterization via either probabilities or logits, follow the standard Distrax distribution interface, and maintain compatibility with TensorFlow Probability.

```mermaid
graph TB
    subgraph "Discrete Count Distributions"
        DIST["distribution.Distribution<br/>Base Class"]
        BERN["Bernoulli<br/>Binary outcomes"]
        MULT["Multinomial<br/>Categorical counts"]
    end
    
    subgraph "Parameterization"
        LOGITS["logits parameter<br/>Log-odds representation"]
        PROBS["probs parameter<br/>Probability representation"]
        COUNT["total_count<br/>Number of trials"]
    end
    
    subgraph "TFP Compatibility"
        TFP_BERN["tfd.Bernoulli"]
        TFP_MULT["tfd.Multinomial"]
    end
    
    DIST --> BERN
    DIST --> MULT
    
    LOGITS --> BERN
    PROBS --> BERN
    LOGITS --> MULT
    PROBS --> MULT
    COUNT --> MULT
    
    BERN --> TFP_BERN
    MULT --> TFP_MULT
```

Sources: [distrax/_src/distributions/bernoulli.py:36-43](), [distrax/_src/distributions/multinomial.py:40-43]()

## Bernoulli Distribution

The `Bernoulli` class models binary random variables that take values 0 or 1. It inherits from `distribution.Distribution` and provides the standard distribution interface.

### Parameters and Properties

| Parameter | Type | Description |
|-----------|------|-------------|
| `logits` | `Optional[Numeric]` | Log-odds of success (mutually exclusive with `probs`) |
| `probs` | `Optional[Numeric]` | Probability of success (mutually exclusive with `logits`) |
| `dtype` | `Union[jnp.dtype, type[Any]]` | Output data type (bool, integer, or floating-point) |

```mermaid
graph LR
    subgraph "Bernoulli Parameters"
        INPUT_LOGITS["logits<br/>Log-odds input"]
        INPUT_PROBS["probs<br/>Probability input"]
        DTYPE["dtype<br/>Output type"]
    end
    
    subgraph "Internal Representation"
        INTERNAL_LOGITS["_logits<br/>Stored logits"]
        INTERNAL_PROBS["_probs<br/>Stored probs"]
    end
    
    subgraph "Computed Properties"
        PROP_LOGITS["logits property<br/>Auto-converted"]
        PROP_PROBS["probs property<br/>Auto-converted"]
    end
    
    INPUT_LOGITS --> INTERNAL_LOGITS
    INPUT_PROBS --> INTERNAL_PROBS
    INTERNAL_LOGITS --> PROP_LOGITS
    INTERNAL_PROBS --> PROP_PROBS
    INTERNAL_LOGITS --> PROP_PROBS
    INTERNAL_PROBS --> PROP_LOGITS
```

Sources: [distrax/_src/distributions/bernoulli.py:44-74](), [distrax/_src/distributions/bernoulli.py:88-99]()

### Key Methods

The Bernoulli distribution implements all required distribution methods:

| Method | Purpose | Key Implementation Details |
|--------|---------|---------------------------|
| `_sample_n` | Generate samples | Uses uniform random variables with threshold comparison |
| `log_prob` | Log probability density | Numerically stable computation using `multiply_no_nan` |
| `prob` | Probability density | Direct probability computation |
| `cdf` | Cumulative distribution | Piecewise function based on support {0, 1} |
| `entropy` | Shannon entropy | Uses both probabilities and log probabilities |
| `mean` | Expected value | Returns `probs` directly |
| `variance` | Variance | Formula: `(1 - probs) * probs` |
| `mode` | Most likely value | Returns 1 if `probs > 0.5`, else 0 |

Sources: [distrax/_src/distributions/bernoulli.py:108-161]()

### Sampling Implementation

```mermaid
graph TD
    START["_sample_n(key, n)"]
    UNIFORM["Generate uniform(0,1)<br/>shape: (n,) + batch_shape"]
    COMPARE["uniform < probs"]
    CAST["Cast to self._dtype"]
    END["Return samples"]
    
    START --> UNIFORM
    UNIFORM --> COMPARE
    COMPARE --> CAST
    CAST --> END
```

Sources: [distrax/_src/distributions/bernoulli.py:108-114]()

## Multinomial Distribution

The `Multinomial` class models the number of successes in each category over a fixed number of independent trials. Each sample is a vector of counts that sum to `total_count`.

### Parameters and Properties

| Parameter | Type | Description |
|-----------|------|-------------|
| `total_count` | `Numeric` | Number of trials per sample |
| `logits` | `Optional[Array]` | Logits for each category (mutually exclusive with `probs`) |
| `probs` | `Optional[Array]` | Probabilities for each category (mutually exclusive with `logits`) |
| `dtype` | `Union[jnp.dtype, type[Any]]` | Output data type (integer or floating-point) |

The implementation automatically normalizes probabilities and handles broadcasting between `total_count` and the category parameters.

```mermaid
graph TB
    subgraph "Input Validation"
        CHECK_MUTUAL["Exactly one of<br/>logits/probs must be None"]
        CHECK_SHAPE["Last dimension >= 2<br/>for categories"]
        CHECK_DTYPE["Integer or floating-point<br/>dtype only"]
    end
    
    subgraph "Parameter Processing"
        NORMALIZE_PROBS["math.normalize(probs=probs)"]
        NORMALIZE_LOGITS["math.normalize(logits=logits)"]
        BROADCAST["lax.broadcast_shapes<br/>for batch dimensions"]
    end
    
    subgraph "Properties"
        EVENT_SHAPE["event_shape: (num_categories,)"]
        BATCH_SHAPE["batch_shape: broadcasted shape"]
        TOTAL_COUNT_PROP["total_count: broadcasted"]
    end
    
    CHECK_MUTUAL --> NORMALIZE_PROBS
    CHECK_MUTUAL --> NORMALIZE_LOGITS
    CHECK_SHAPE --> NORMALIZE_PROBS
    CHECK_SHAPE --> NORMALIZE_LOGITS
    NORMALIZE_PROBS --> BROADCAST
    NORMALIZE_LOGITS --> BROADCAST
    BROADCAST --> EVENT_SHAPE
    BROADCAST --> BATCH_SHAPE
    BROADCAST --> TOTAL_COUNT_PROP
```

Sources: [distrax/_src/distributions/multinomial.py:60-93]()

### Sampling Strategy

The multinomial sampling uses a sequential approach that handles variable `total_count` values efficiently:

```mermaid
graph TD
    SPLIT_KEYS["Split PRNG keys<br/>for batch dimensions"]
    RESHAPE["Reshape inputs<br/>for vectorization"]
    VMAP["jax.vmap(_sample_n_scalar)"]
    LOOP["lax.while_loop<br/>for each trial"]
    CATEGORICAL["jax.random.categorical<br/>sample category"]
    ONEHOT["jax.nn.one_hot<br/>convert to counts"]
    ACCUMULATE["Add to count vector"]
    RESHAPE_OUT["Reshape to final<br/>batch + event shape"]
    
    SPLIT_KEYS --> RESHAPE
    RESHAPE --> VMAP
    VMAP --> LOOP
    LOOP --> CATEGORICAL
    CATEGORICAL --> ONEHOT
    ONEHOT --> ACCUMULATE
    ACCUMULATE --> LOOP
    LOOP --> RESHAPE_OUT
```

Sources: [distrax/_src/distributions/multinomial.py:152-181]()

### Statistical Methods

The multinomial distribution provides comprehensive statistical computations:

| Method | Formula/Implementation |
|--------|----------------------|
| `log_prob` | `lgamma(total_count + 1) - sum(lgamma(counts + 1)) + sum(log_probs * counts)` |
| `entropy` | Uses vectorized computation with `lax.while_loop` for numerical stability |
| `mean` | `total_count * probs` |
| `variance` | `total_count * probs * (1 - probs)` |
| `covariance` | `total_count * (-probs_i * probs_j + diag(probs))` |

Sources: [distrax/_src/distributions/multinomial.py:143-281]()

## TensorFlow Probability Integration

Both distributions maintain full compatibility with TensorFlow Probability through:

### Equivalence Classes

```python
# Bernoulli
equiv_tfp_cls = tfd.Bernoulli

# Multinomial  
equiv_tfp_cls = tfd.Multinomial
```

### KL Divergence Registration

The Bernoulli distribution registers KL divergence computations with TFP's dispatch system:

```mermaid
graph LR
    DISTRAX_BERN["Bernoulli<br/>(Distrax)"]
    TFP_BERN["tfd.Bernoulli<br/>(TFP)"]
    KL_FUNC["_kl_divergence_bernoulli_bernoulli"]
    
    DISTRAX_BERN --> KL_FUNC
    TFP_BERN --> KL_FUNC
    KL_FUNC --> DISTRAX_BERN
    KL_FUNC --> TFP_BERN
```

Sources: [distrax/_src/distributions/bernoulli.py:42](), [distrax/_src/distributions/bernoulli.py:214-221](), [distrax/_src/distributions/multinomial.py:43]()

## Usage Patterns

### Bernoulli Distribution

```python
# Create from probabilities
bernoulli_probs = Bernoulli(probs=0.3)

# Create from logits
bernoulli_logits = Bernoulli(logits=0.5)

# Different output types
bernoulli_bool = Bernoulli(probs=0.7, dtype=bool)
bernoulli_int = Bernoulli(probs=0.7, dtype=int)
```

### Multinomial Distribution

```python
# Simple case: 10 trials, 3 categories
multinomial = Multinomial(total_count=10, probs=[0.2, 0.3, 0.5])

# Batch processing: different trial counts
multinomial_batch = Multinomial(
    total_count=[5, 10], 
    logits=[[0.1, -0.2, 0.3], [0.0, 0.5, -0.1]]
)
```

### Indexing and Slicing

Both distributions support advanced indexing that preserves the distribution type:

```python
# Batch indexing
batch_bernoulli = Bernoulli(probs=[[0.3, 0.7], [0.1, 0.9]])
single_bernoulli = batch_bernoulli[0]  # Returns Bernoulli with probs=[0.3, 0.7]

# Multinomial slicing
batch_multinomial = Multinomial(total_count=[3, 5], probs=[[0.2, 0.8], [0.4, 0.6]])
sliced_multinomial = batch_multinomial[..., -1]  # Proper indexing handling
```

Sources: [distrax/_src/distributions/bernoulli.py:162-167](), [distrax/_src/distributions/multinomial.py:282-291]()

---

