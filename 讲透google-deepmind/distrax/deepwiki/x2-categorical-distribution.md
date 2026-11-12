<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/distrax · extra page Categorical Distribution · fetched 2026-10-26 -->

# Categorical Distribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [distrax/_src/distributions/categorical.py](distrax/_src/distributions/categorical.py)
- [distrax/_src/distributions/categorical_test.py](distrax/_src/distributions/categorical_test.py)
- [distrax/_src/distributions/distribution_from_tfp_test.py](distrax/_src/distributions/distribution_from_tfp_test.py)

</details>



This document covers the `Categorical` distribution implementation in Distrax, a discrete probability distribution over categorical outcomes. The `Categorical` distribution models random variables that can take on one of K possible discrete values (categories), making it fundamental for classification tasks, sampling from discrete probability vectors, and multinomial modeling.

For information about other discrete distributions like `Bernoulli` and `Multinomial`, see [Bernoulli and Multinomial](#3.1.2). For the base distribution interface and common methods, see [Distribution Base Class](#2.1).

## Class Architecture

The `Categorical` class inherits from the base `Distribution` class and provides a JAX-native implementation of the categorical distribution with full TensorFlow Probability compatibility.

```mermaid
graph TB
    subgraph "Distribution Hierarchy"
        BASE["distribution.Distribution<br/>(Abstract Base Class)"]
        CAT["categorical.Categorical<br/>(Concrete Implementation)"]
        BASE --> CAT
    end
    
    subgraph "TFP Integration"
        TFP_CAT["tfd.Categorical<br/>(TFP Equivalent)"]
        CAT -.->|"equiv_tfp_cls"| TFP_CAT
    end
    
    subgraph "Core Parameters"
        LOGITS["logits: Array<br/>(Log probabilities)"]
        PROBS["probs: Array<br/>(Probabilities)"]
        DTYPE["dtype: jnp.dtype<br/>(Sample type)"]
    end
    
    subgraph "Key Methods"
        SAMPLE["_sample_n()"]
        LOGPROB["log_prob()"]
        PROB["prob()"]
        ENTROPY["entropy()"]
        MODE["mode()"]
        CDF["cdf()"]
    end
    
    CAT --> LOGITS
    CAT --> PROBS
    CAT --> DTYPE
    CAT --> SAMPLE
    CAT --> LOGPROB
    CAT --> PROB
    CAT --> ENTROPY
    CAT --> MODE
    CAT --> CDF
```

Sources: [distrax/_src/distributions/categorical.py:33-36](), [distrax/_src/distributions/categorical.py:20]()

## Parameterization

The `Categorical` distribution supports two mutually exclusive parameterization methods: logits or probabilities. Exactly one parameter must be provided during initialization.

| Parameter | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `logits` | `Array` | Log-probabilities (unnormalized) | Real values, automatically normalized |
| `probs` | `Array` | Probabilities (unnormalized) | Non-negative values, automatically normalized |
| `dtype` | `jnp.dtype` | Output sample type | Integer or floating-point types |

```mermaid
graph LR
    subgraph "Parameter Validation"
        INPUT["__init__(logits, probs, dtype)"]
        CHECK["Exactly one of logits/probs<br/>must be non-None"]
        NORM_LOGITS["math.normalize(logits=logits)"]
        NORM_PROBS["math.normalize(probs=probs)"]
        DTYPE_CHECK["dtype must be<br/>integer or floating"]
    end
    
    INPUT --> CHECK
    CHECK -->|"logits provided"| NORM_LOGITS
    CHECK -->|"probs provided"| NORM_PROBS
    INPUT --> DTYPE_CHECK
    
    subgraph "Internal Storage"
        STORED_LOGITS["self._logits"]
        STORED_PROBS["self._probs"]
        STORED_DTYPE["self._dtype"]
    end
    
    NORM_LOGITS --> STORED_LOGITS
    NORM_PROBS --> STORED_PROBS
    DTYPE_CHECK --> STORED_DTYPE
```

Sources: [distrax/_src/distributions/categorical.py:38-64](), [distrax/_src/distributions/categorical.py:52-55]()

### Dynamic Property Access

The distribution provides seamless conversion between logits and probabilities through computed properties:

```mermaid
graph TB
    subgraph "Property Access Pattern"
        LOGITS_PROP["logits property"]
        PROBS_PROP["probs property"]
        
        LOGITS_STORED["self._logits != None"]
        PROBS_STORED["self._probs != None"]
        
        LOG_CONV["jnp.log(self._probs)"]
        SOFTMAX_CONV["jax.nn.softmax(self._logits, axis=-1)"]
    end
    
    LOGITS_PROP --> LOGITS_STORED
    LOGITS_STORED -->|"True"| LOGITS_PROP
    LOGITS_STORED -->|"False"| LOG_CONV
    
    PROBS_PROP --> PROBS_STORED
    PROBS_STORED -->|"True"| PROBS_PROP
    PROBS_STORED -->|"False"| SOFTMAX_CONV
```

Sources: [distrax/_src/distributions/categorical.py:72-83]()

## Core Operations

### Sampling

The `_sample_n` method generates random categorical samples using JAX's efficient categorical sampling with automatic validity checking.

```mermaid
flowchart TD
    subgraph "Sampling Process"
        START["_sample_n(key, n)"]
        SHAPE["new_shape = (n,) + logits.shape[:-1]"]
        VALID["Check probabilities validity<br/>finite and non-negative"]
        SAMPLE["jax.random.categorical(key, logits, axis=-1)"]
        CAST["Cast to self._dtype"]
        MASK["Mask invalid samples to -1"]
        RETURN["Return masked samples"]
    end
    
    START --> SHAPE
    SHAPE --> VALID
    VALID --> SAMPLE
    SAMPLE --> CAST
    CAST --> MASK
    MASK --> RETURN
    
    subgraph "Validity Conditions"
        FINITE["jnp.all(jnp.isfinite(probs))"]
        NONNEG["jnp.all(probs >= 0)"]
        IS_VALID["jnp.logical_and(finite, nonneg)"]
    end
    
    VALID --> FINITE
    VALID --> NONNEG
    FINITE --> IS_VALID
    NONNEG --> IS_VALID
```

Sources: [distrax/_src/distributions/categorical.py:92-99]()

### Probability Calculations

The distribution provides both probability and log-probability computations with proper handling of out-of-domain values:

```mermaid
graph TB
    subgraph "Probability Methods"
        LOG_PROB["log_prob(value)"]
        PROB["prob(value)"]
        
        ONE_HOT["jax.nn.one_hot(value, num_categories)"]
        DOMAIN_CHECK["Check if value in [0, num_categories-1]"]
        
        LOG_CALC["sum(logits * one_hot_value)"]
        PROB_CALC["sum(probs * one_hot_value)"]
        
        LOG_MASK["jnp.where(outside_domain, -inf, log_result)"]
        PROB_RESULT["multiply_no_nan result"]
    end
    
    LOG_PROB --> ONE_HOT
    LOG_PROB --> DOMAIN_CHECK
    ONE_HOT --> LOG_CALC
    DOMAIN_CHECK --> LOG_MASK
    LOG_CALC --> LOG_MASK
    
    PROB --> ONE_HOT
    ONE_HOT --> PROB_CALC
    PROB_CALC --> PROB_RESULT
```

Sources: [distrax/_src/distributions/categorical.py:101-115]()

## Statistical Properties

The `Categorical` class implements key statistical methods with numerically stable computations:

| Method | Description | Implementation Detail |
|--------|-------------|----------------------|
| `entropy()` | Shannon entropy | Uses `mul_exp` for numerical stability |
| `mode()` | Most likely outcome | `argmax` of parameters |
| `cdf(value)` | Cumulative distribution | Cumulative sum with boundary handling |
| `num_categories` | Number of categories | Shape of last dimension |

```mermaid
graph LR
    subgraph "Statistical Methods"
        ENT["entropy()"]
        MODE["mode()"]
        CDF["cdf(value)"]
        
        subgraph "Entropy Computation"
            LOG_PROBS["log_probs = log_softmax or log(probs)"]
            MUL_EXP["math.mul_exp(log_probs, log_probs)"]
            NEG_SUM["-sum(mul_exp_result, axis=-1)"]
        end
        
        subgraph "Mode Computation"
            PARAM["Use _probs or _logits"]
            ARGMAX["jnp.argmax(parameter, axis=-1)"]
            CAST_MODE["Cast to self._dtype"]
        end
        
        subgraph "CDF Computation"
            CLIP["Clip value to [0, K-1]"]
            ONE_HOT_CDF["One-hot encode clipped value"]
            CUMSUM["Cumulative sum of probabilities"]
            BOUNDARY["Handle boundary cases"]
        end
    end
    
    ENT --> LOG_PROBS
    LOG_PROBS --> MUL_EXP
    MUL_EXP --> NEG_SUM
    
    MODE --> PARAM
    PARAM --> ARGMAX
    ARGMAX --> CAST_MODE
    
    CDF --> CLIP
    CLIP --> ONE_HOT_CDF
    ONE_HOT_CDF --> CUMSUM
    CUMSUM --> BOUNDARY
```

Sources: [distrax/_src/distributions/categorical.py:117-148]()

## TensorFlow Probability Integration

The `Categorical` distribution provides comprehensive TFP compatibility through KL divergence registration and API equivalence:

```mermaid
graph TB
    subgraph "KL Divergence Registration"
        KL_FUNC["_kl_divergence_categorical_categorical"]
        
        subgraph "Registered Pairs"
            D2D["Distrax → Distrax"]
            D2T["Distrax → TFP"]
            T2D["TFP → Distrax"]
            OH2D["OneHotCategorical → Distrax"]
            D2OH["Distrax → OneHotCategorical"]
        end
        
        KL_FUNC --> D2D
        KL_FUNC --> D2T
        KL_FUNC --> T2D
        KL_FUNC --> OH2D
        KL_FUNC --> D2OH
    end
    
    subgraph "KL Computation"
        LOGITS1["dist1.logits_parameter()"]
        LOGITS2["dist2.logits_parameter()"]
        VALIDATE["Validate same num_categories"]
        LOG_SOFT1["log_softmax(logits1)"]
        LOG_SOFT2["log_softmax(logits2)"]
        KL_CALC["sum(mul_exp(log_p1 - log_p2, log_p1))"]
    end
    
    KL_FUNC --> LOGITS1
    KL_FUNC --> LOGITS2
    LOGITS1 --> VALIDATE
    LOGITS2 --> VALIDATE
    VALIDATE --> LOG_SOFT1
    VALIDATE --> LOG_SOFT2
    LOG_SOFT1 --> KL_CALC
    LOG_SOFT2 --> KL_CALC
```

Sources: [distrax/_src/distributions/categorical.py:165-215](), [distrax/_src/distributions/categorical.py:204-215]()

## JAX Integration Features

The `Categorical` distribution is designed for seamless JAX integration with support for key transformations:

### Indexing and Slicing

The distribution supports advanced indexing operations that preserve the distribution type:

```mermaid
graph LR
    subgraph "Indexing Support"
        GETITEM["__getitem__(index)"]
        BATCH_INDEX["to_batch_shape_index()"]
        
        subgraph "Parameter Slicing"
            LOGITS_SLICE["Categorical(logits=logits[index])"]
            PROBS_SLICE["Categorical(probs=probs[index])"]
        end
        
        GETITEM --> BATCH_INDEX
        BATCH_INDEX --> LOGITS_SLICE
        BATCH_INDEX --> PROBS_SLICE
    end
    
    subgraph "VMAP Compatibility"
        VMAP_IN["vmap over inputs"]
        VMAP_OUT["vmap over outputs"]
        BATCH_OPS["Batched operations"]
    end
    
    GETITEM --> VMAP_IN
    LOGITS_SLICE --> VMAP_OUT
    PROBS_SLICE --> VMAP_OUT
    VMAP_IN --> BATCH_OPS
    VMAP_OUT --> BATCH_OPS
```

Sources: [distrax/_src/distributions/categorical.py:154-159](), [distrax/_src/distributions/categorical_test.py:412-453]()

### Numerical Stability

The implementation includes several numerical stability features for gradient computation and extreme values:

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| `mul_exp` usage | Replaces `exp(log_probs) * log_probs` | Handles -inf logits gracefully |
| `multiply_no_nan` | Safe multiplication with zeros | Prevents NaN propagation |
| Gradient clipping | Automatic handling of -inf logits | Maintains finite gradients |
| Validity masking | Sample masking for invalid distributions | Robust sampling behavior |

Sources: [distrax/_src/distributions/categorical.py:123](), [distrax/_src/distributions/categorical.py:109](), [distrax/_src/distributions/categorical_test.py:462-497]()

---

