<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/distrax · extra page Gamma and Beta Distributions · fetched 2026-10-26 -->

# Gamma and Beta Distributions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [distrax/_src/distributions/beta_test.py](distrax/_src/distributions/beta_test.py)
- [distrax/_src/distributions/gamma.py](distrax/_src/distributions/gamma.py)
- [distrax/_src/distributions/gamma_test.py](distrax/_src/distributions/gamma_test.py)
- [distrax/_src/utils/math.py](distrax/_src/utils/math.py)
- [distrax/_src/utils/math_test.py](distrax/_src/utils/math_test.py)

</details>



This document covers the implementation of Gamma and Beta distributions in Distrax, including their parameterizations, mathematical properties, and integration with TensorFlow Probability. These are continuous probability distributions commonly used in Bayesian statistics and machine learning applications.

For information about other continuous distributions like Normal and Uniform, see [Normal and Uniform Distributions](#3.2.1). For multivariate extensions, see [Multivariate Distributions](#3.3).

## Distribution Class Hierarchy

The Gamma and Beta distributions follow Distrax's standard distribution architecture, inheriting from the base `Distribution` class and implementing the required interface methods.

```mermaid
graph TB
    subgraph "Base Classes"
        DIST["distribution.Distribution<br/>Base Class"]
    end
    
    subgraph "Gamma Distribution"
        GAMMA["gamma.Gamma<br/>concentration, rate"]
        GAMMA_METHODS["Key Methods:<br/>• log_prob()<br/>• entropy()<br/>• cdf()<br/>• mean(), variance()<br/>• mode()"]
    end
    
    subgraph "Beta Distribution" 
        BETA["beta.Beta<br/>alpha, beta"]
        BETA_METHODS["Key Methods:<br/>• log_prob()<br/>• entropy()<br/>• cdf()<br/>• mean(), variance()<br/>• mode()"]
    end
    
    subgraph "TFP Integration"
        TFP_GAMMA["tfd.Gamma<br/>equiv_tfp_cls"]
        TFP_BETA["tfd.Beta<br/>equiv_tfp_cls"]
        KL_REG["KL Divergence<br/>Registration"]
    end
    
    DIST --> GAMMA
    DIST --> BETA
    GAMMA --> GAMMA_METHODS
    BETA --> BETA_METHODS
    GAMMA --> TFP_GAMMA
    BETA --> TFP_BETA
    TFP_GAMMA --> KL_REG
    TFP_BETA --> KL_REG
```

**Sources:** [distrax/_src/distributions/gamma.py:34-38](), [distrax/_src/distributions/gamma.py:158-161]()

## Gamma Distribution Implementation

The `Gamma` class implements the Gamma distribution with shape-rate parameterization, where samples are drawn from the positive real line.

### Parameters and Properties

The Gamma distribution is parameterized by two positive values:

| Parameter | Description | Mathematical Role |
|-----------|-------------|-------------------|
| `concentration` | Shape parameter (α) | Controls distribution shape |
| `rate` | Inverse scale parameter (β) | Controls distribution scale |

```mermaid
graph LR
    subgraph "Gamma Distribution Flow"
        PARAMS["Parameters:<br/>concentration (α)<br/>rate (β)"] 
        INIT["gamma.Gamma.__init__()"]
        PROPS["Properties:<br/>• batch_shape<br/>• event_shape = ()"]
        BROADCAST["Broadcasting:<br/>jax.lax.broadcast_shapes()"]
    end
    
    subgraph "Core Methods"
        SAMPLE["_sample_n()<br/>jax.random.gamma()"]
        LOGPROB["log_prob()<br/>α*log(β) + (α-1)*log(x)<br/>- β*x - lgamma(α)"]
        STATS["Statistics:<br/>• mean = α/β<br/>• variance = α/β²<br/>• mode = (α-1)/β"]
    end
    
    PARAMS --> INIT
    INIT --> PROPS
    INIT --> BROADCAST
    PROPS --> SAMPLE
    PROPS --> LOGPROB
    PROPS --> STATS
```

**Sources:** [distrax/_src/distributions/gamma.py:39-50](), [distrax/_src/distributions/gamma.py:84-91](), [distrax/_src/distributions/gamma.py:111-126]()

### Key Implementation Details

The Gamma distribution implements several mathematical functions with numerical stability considerations:

**Sampling:** Uses JAX's native `jax.random.gamma` for standard Gamma sampling, then scales by the rate parameter:
[distrax/_src/distributions/gamma.py:72-82]()

**Log Probability:** Computes the log PDF using the standard Gamma formula with `jax.lax.lgamma` for numerical stability:
[distrax/_src/distributions/gamma.py:84-91]()

**Statistics:** Provides closed-form expressions for mean, variance, and mode:
[distrax/_src/distributions/gamma.py:111-126]()

## Beta Distribution Implementation

The Beta distribution is parameterized by two positive shape parameters and produces samples in the interval [0, 1].

### Parameters and Mathematical Properties

| Parameter | Description | Mathematical Role |
|-----------|-------------|-------------------|
| `alpha` | First shape parameter (α) | Controls left skewness |
| `beta` | Second shape parameter (β) | Controls right skewness |

The Beta distribution uses the mathematical utilities in `math.py` for computing the beta function and its logarithm.

```mermaid
graph TB
    subgraph "Beta Function Utilities"
        LOG_BETA["math.log_beta(a, b)<br/>log Γ(a) + log Γ(b) - log Γ(a+b)"]
        MULTI_BETA["math.log_beta_multivariate(a)<br/>Σ log Γ(aₖ) - log Γ(Σ aₖ)"]
        LGAMMA["jax.lax.lgamma()<br/>Stable log-gamma computation"]
    end
    
    subgraph "Beta Distribution Usage"
        BETA_LOGPROB["Beta log_prob computation"]
        BETA_ENTROPY["Beta entropy calculation"]
        DIRICHLET["Dirichlet distribution<br/>(multivariate extension)"]
    end
    
    LOG_BETA --> BETA_LOGPROB
    LOG_BETA --> BETA_ENTROPY
    MULTI_BETA --> DIRICHLET
    LGAMMA --> LOG_BETA
    LGAMMA --> MULTI_BETA
```

**Sources:** [distrax/_src/utils/math.py:162-174](), [distrax/_src/utils/math.py:177-190](), [distrax/_src/distributions/beta_test.py:208-212]()

## TensorFlow Probability Integration

Both Gamma and Beta distributions maintain full compatibility with TensorFlow Probability through the equivalence system and KL divergence registration.

### KL Divergence Implementation

The Gamma distribution includes a specialized KL divergence computation for improved numerical stability:

```mermaid
graph LR
    subgraph "KL Divergence Components"
        T1["t1: β₂(log β₁ - log β₂)"]
        T2["t2: log Γ(β₂) - log Γ(β₁)"] 
        T3["t3: (α₁-α₂)ψ(α₁)"]
        T4["t4: (β₂-β₁)(α₁/β₁)"]
    end
    
    subgraph "Registration"
        KL_FUNC["_kl_divergence_gamma_gamma()"]
        TFP_REG["tfd.RegisterKL()<br/>All combinations"]
    end
    
    T1 --> KL_FUNC
    T2 --> KL_FUNC  
    T3 --> KL_FUNC
    T4 --> KL_FUNC
    KL_FUNC --> TFP_REG
```

**Sources:** [distrax/_src/distributions/gamma.py:135-155](), [distrax/_src/distributions/gamma.py:158-161]()

### Equivalence Testing Framework

Both distributions use the `EquivalenceTest` framework to ensure mathematical consistency with TensorFlow Probability:

| Test Category | Purpose | Implementation |
|---------------|---------|----------------|
| Parameter Broadcasting | Verify shape handling | [distrax/_src/distributions/gamma_test.py:34-50]() |
| Sampling Consistency | Cross-validate sampling | [distrax/_src/distributions/gamma_test.py:67-82]() |
| Statistical Properties | Verify moments and entropy | [distrax/_src/distributions/gamma_test.py:135-143]() |
| KL Divergence | Cross-validate KL computations | [distrax/_src/distributions/gamma_test.py:146-171]() |

## Mathematical Stability Features

The implementations include several numerical stability enhancements:

```mermaid
graph TB
    subgraph "Numerical Stability"
        LGAMMA_STABLE["jax.lax.lgamma()<br/>Stable log-gamma"]
        DIGAMMA_STABLE["jax.lax.digamma()<br/>Stable digamma function"]
        IGAMMA_STABLE["jax.lax.igamma()<br/>Regularized incomplete gamma"]
    end
    
    subgraph "Usage in Distributions"
        GAMMA_LOGPROB["Gamma.log_prob()"]
        GAMMA_ENTROPY["Gamma.entropy()"]
        GAMMA_CDF["Gamma.cdf()"]
        GAMMA_KL["Gamma KL divergence"]
        BETA_UTILS["Beta function utilities"]
    end
    
    LGAMMA_STABLE --> GAMMA_LOGPROB
    LGAMMA_STABLE --> GAMMA_ENTROPY
    LGAMMA_STABLE --> GAMMA_KL
    LGAMMA_STABLE --> BETA_UTILS
    DIGAMMA_STABLE --> GAMMA_ENTROPY
    DIGAMMA_STABLE --> GAMMA_KL
    IGAMMA_STABLE --> GAMMA_CDF
```

**Sources:** [distrax/_src/distributions/gamma.py:90](), [distrax/_src/distributions/gamma.py:100](), [distrax/_src/distributions/gamma.py:105](), [distrax/_src/utils/math.py:174]()

## Usage Patterns and Broadcasting

Both distributions support JAX's broadcasting semantics for batch operations:

**Parameter Broadcasting:** Parameters can have different shapes and will be broadcast to a common batch shape [distrax/_src/distributions/gamma.py:49-50]()

**Slicing Support:** Both distributions implement `__getitem__` for easy batch manipulation [distrax/_src/distributions/gamma.py:128-132]()

**JAX Integration:** Full compatibility with `jit`, `vmap`, and automatic differentiation through the JAX ecosystem [distrax/_src/distributions/gamma_test.py:173-175]()

**Sources:** [distrax/_src/distributions/gamma_test.py:34-50](), [distrax/_src/distributions/gamma_test.py:177-196](), [distrax/_src/distributions/beta_test.py:214-239]()

---

