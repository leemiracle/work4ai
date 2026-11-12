<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/distrax · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [distrax/__init__.py](distrax/__init__.py)
- [distrax/_src/distributions/clipped.py](distrax/_src/distributions/clipped.py)
- [distrax/_src/distributions/clipped_test.py](distrax/_src/distributions/clipped_test.py)
- [distrax/_src/utils/hmm.py](distrax/_src/utils/hmm.py)
- [distrax/_src/utils/hmm_test.py](distrax/_src/utils/hmm_test.py)
- [examples/hmm.py](examples/hmm.py)

</details>



## Purpose and Scope

Distrax is a JAX-native probability distribution library that provides implementations of probability distributions and bijective transformations (bijectors). It serves as a lightweight alternative to TensorFlow Probability (TFP) with emphasis on readability, extensibility, and JAX performance optimizations.

This document covers the overall architecture and design principles of Distrax. For specific distribution implementations, see [Distributions](#3). For bijector details, see [Bijectors](#4). For JAX-specific features and performance considerations, see [JAX Integration](#2.3).

**Sources:** [README.md:1-47](), [distrax/__init__.py:15]()

## Core Architecture

Distrax is built around two primary abstractions: `Distribution` and `Bijector` classes, with additional utilities for advanced probabilistic modeling. The library maintains strict compatibility with TensorFlow Probability while leveraging JAX's compilation and transformation capabilities.

### Main Library Components

```mermaid
graph TB
    subgraph "distrax Package"
        INIT["distrax/__init__.py<br/>Public API Entry Point"]
    end
    
    subgraph "Core Abstractions"
        DIST["Distribution<br/>Base Class"]
        BIJ["Bijector<br/>Base Class"]
        DISTLIKE["DistributionLike<br/>Type Alias"]
        BIJLIKE["BijectorLike<br/>Type Alias"]
    end
    
    subgraph "Distribution Categories"
        DISCRETE["Discrete Distributions<br/>Categorical, Bernoulli<br/>Multinomial"]
        CONTINUOUS["Continuous Distributions<br/>Normal, Gumbel<br/>Gamma, Uniform"]
        MULTIVARIATE["Multivariate Distributions<br/>MultivariateNormalDiag<br/>Dirichlet"]
        COMPOSITE["Composite Distributions<br/>Transformed, Independent<br/>Joint, Quantized"]
    end
    
    subgraph "Bijector Categories"  
        LINEAR["Linear Bijectors<br/>ScalarAffine, Shift<br/>DiagLinear"]
        NONLINEAR["Nonlinear Bijectors<br/>Tanh, Sigmoid<br/>RationalQuadraticSpline"]
        FLOW["Flow Bijectors<br/>MaskedCoupling<br/>Chain"]
    end
    
    subgraph "Utilities"
        HMM_UTIL["HMM<br/>Hidden Markov Models"]
        CONV["Conversion Utilities<br/>as_distribution, to_tfp"]
        MATH["Math Utilities<br/>multiply_no_nan"]
        TRANSFORM["Function Transformations<br/>register_inverse"]
    end
    
    INIT --> DIST
    INIT --> BIJ
    INIT --> DISTLIKE
    INIT --> BIJLIKE
    
    DIST --> DISCRETE
    DIST --> CONTINUOUS
    DIST --> MULTIVARIATE
    DIST --> COMPOSITE
    
    BIJ --> LINEAR
    BIJ --> NONLINEAR
    BIJ --> FLOW
    
    INIT --> HMM_UTIL
    INIT --> CONV
    INIT --> MATH
    INIT --> TRANSFORM
```

**Sources:** [distrax/__init__.py:17-89](), [README.md:48-137]()

### Code Entity Mapping

```mermaid
graph LR
    subgraph "Public API Exports"
        API_DIST["Distribution Classes<br/>Normal, Categorical<br/>MultivariateNormalDiag<br/>Bernoulli, Gamma"]
        API_BIJ["Bijector Classes<br/>Tanh, ScalarAffine<br/>Chain, MaskedCoupling<br/>Sigmoid, RationalQuadraticSpline"]
        API_UTIL["Utility Functions<br/>HMM, as_distribution<br/>to_tfp, register_inverse<br/>mc_estimate_kl"]
    end
    
    subgraph "Implementation Modules"
        DIST_SRC["distrax/_src/distributions/<br/>normal.py, categorical.py<br/>mvn_diag.py<br/>bernoulli.py, gamma.py"]
        BIJ_SRC["distrax/_src/bijectors/<br/>tanh.py, scalar_affine.py<br/>chain.py, masked_coupling.py<br/>sigmoid.py, rational_quadratic_spline.py"]
        UTIL_SRC["distrax/_src/utils/<br/>hmm.py, conversion.py<br/>transformations.py<br/>monte_carlo.py"]
    end
    
    API_DIST --> DIST_SRC
    API_BIJ --> BIJ_SRC  
    API_UTIL --> UTIL_SRC
```

**Sources:** [distrax/__init__.py:40-89](), [distrax/__init__.py:17-37](), [distrax/__init__.py:77-88]()

## Key Components

### Distribution System

The `Distribution` base class provides a uniform interface for probability distributions with methods for sampling, probability calculation, and shape handling. All distributions support JAX transformations and maintain compatibility with TensorFlow Probability.

| Distribution Type | Key Classes | Event Shape | Use Cases |
|------------------|-------------|-------------|-----------|
| Discrete | `Categorical`, `Bernoulli`, `Multinomial` | `()` or `(k,)` | Classification, discrete choice |
| Continuous | `Normal`, `Gumbel`, `Gamma`, `Uniform` | `()` | Regression, continuous modeling |
| Multivariate | `MultivariateNormalDiag`, `Dirichlet` | `(d,)` | Vector-valued variables |
| Composite | `Transformed`, `Independent`, `Joint` | Variable | Meta-distributions |

**Sources:** [distrax/__init__.py:40-75](), [README.md:49-107]()

### Bijector System

Bijectors implement invertible transformations with automatic Jacobian computation. They enable creation of complex distributions by transforming simpler base distributions through the `Transformed` class.

| Bijector Type | Key Classes | Transformation | Jacobian |
|--------------|-------------|----------------|----------|
| Linear | `ScalarAffine`, `Shift`, `DiagLinear` | `y = ax + b` | Constant or diagonal |
| Nonlinear | `Tanh`, `Sigmoid` | Element-wise | Element-wise |
| Flow | `MaskedCoupling`, `RationalQuadraticSpline` | Normalizing flows | Complex |
| Composite | `Chain`, `Inverse` | Composition | Product/inverse |

**Sources:** [distrax/__init__.py:17-37](), [README.md:138-255]()

### Utility System

```mermaid
graph TB
    subgraph "Core Utilities"
        CONV_UTIL["conversion.py<br/>as_distribution()<br/>as_bijector()<br/>to_tfp()"]
        MATH_UTIL["math.py<br/>multiply_no_nan()"]
        TRANSFORM_UTIL["transformations.py<br/>register_inverse()"]
    end
    
    subgraph "Advanced Features"
        HMM_CLASS["hmm.py<br/>HMM class<br/>forward(), backward()<br/>viterbi(), sample()"]
        MC_UTIL["monte_carlo.py<br/>mc_estimate_kl()<br/>estimate_kl_best_effort()<br/>mc_estimate_mode()"]
        IS_UTIL["importance_sampling.py<br/>importance_sampling_ratios()"]
    end
    
    subgraph "Integration Support"
        TFP_COMPAT["TFP Compatibility<br/>Cross-compatible API<br/>KL divergence registration"]
        JAX_SUPPORT["JAX Integration<br/>JIT compilation<br/>Automatic differentiation"]
    end
    
    CONV_UTIL --> TFP_COMPAT
    HMM_CLASS --> JAX_SUPPORT
    MC_UTIL --> JAX_SUPPORT
    TRANSFORM_UTIL --> JAX_SUPPORT
```

**Sources:** [distrax/__init__.py:77-88](), [distrax/_src/utils/hmm.py:47-324](), [examples/hmm.py:91-96]()

## JAX Integration

Distrax distributions and bijectors are designed as JAX-native implementations that support:

- **JIT Compilation**: All classes implement the `Jittable` interface for compilation optimization
- **Automatic Differentiation**: Native support for `jax.grad` and related transformations  
- **Vectorization**: Compatible with `jax.vmap` for batch operations
- **Functional Programming**: Immutable objects that work naturally with JAX transformations

```mermaid
graph LR
    subgraph "JAX Features"
        JIT["jax.jit<br/>Compilation"]
        GRAD["jax.grad<br/>Differentiation"] 
        VMAP["jax.vmap<br/>Vectorization"]
        RANDOM["jax.random<br/>PRNGKey"]
    end
    
    subgraph "Distrax Classes"
        JITTABLE["Jittable Interface<br/>_tree_flatten()<br/>_tree_unflatten()"]
        DIST_OPS["Distribution Methods<br/>sample(), log_prob()<br/>sample_and_log_prob()"]
        BIJ_OPS["Bijector Methods<br/>forward(), inverse()<br/>forward_and_log_det()"]
    end
    
    JIT --> JITTABLE
    GRAD --> DIST_OPS
    GRAD --> BIJ_OPS
    VMAP --> DIST_OPS
    VMAP --> BIJ_OPS
    RANDOM --> DIST_OPS
```

**Sources:** [README.md:257-278](), [README.md:280-294]()

## TensorFlow Probability Compatibility

Distrax maintains bidirectional compatibility with TensorFlow Probability through wrapper utilities and shared API conventions. This enables gradual migration and interoperability between the libraries.

### Compatibility Features

- **API Consistency**: Method signatures match TFP where possible (`sample`, `log_prob`, `kl_divergence`)
- **Cross-Library Usage**: TFP distributions work in Distrax meta-distributions and vice versa
- **Conversion Utilities**: `to_tfp()` wrapper for using Distrax objects in TFP contexts
- **KL Divergence Registration**: Automatic registration with TFP's KL divergence registry

```mermaid
graph TB
    subgraph "Distrax Objects"
        DX_DIST["Distrax Distributions<br/>Normal, Categorical"]
        DX_BIJ["Distrax Bijectors<br/>Tanh, ScalarAffine"]
        DX_META["Distrax Meta-distributions<br/>Independent, Transformed"]
    end
    
    subgraph "Compatibility Layer"
        TO_TFP["to_tfp() wrapper"]
        AS_DIST["as_distribution()"]
        KL_REG["KL Registry Integration"]
    end
    
    subgraph "TFP Objects"
        TFP_DIST["TFP Distributions<br/>tfd.Normal, tfd.Categorical"]
        TFP_BIJ["TFP Bijectors<br/>tfb.Tanh, tfb.Scale"]
        TFP_META["TFP Meta-distributions<br/>tfd.Sample, tfd.TransformedDistribution"]
    end
    
    DX_DIST --> TO_TFP
    DX_BIJ --> TO_TFP
    TO_TFP --> TFP_META
    
    TFP_DIST --> AS_DIST
    TFP_BIJ --> AS_DIST
    AS_DIST --> DX_META
    
    DX_DIST --> KL_REG
    TFP_DIST --> KL_REG
```

**Sources:** [README.md:76-136](), [README.md:173-195](), [distrax/__init__.py:78-80]()

## Public API Structure

The main entry point [distrax/__init__.py]() exports 160 public symbols organized into logical categories. The `__all__` tuple defines the complete public API surface, ensuring consistent imports and documentation.

| Category | Count | Examples |
|----------|-------|----------|
| Distribution Classes | 25 | `Normal`, `Categorical`, `MultivariateNormalDiag` |
| Bijector Classes | 18 | `Tanh`, `ScalarAffine`, `MaskedCoupling` |
| Utility Functions | 12 | `HMM`, `as_distribution`, `mc_estimate_kl` |
| Type Aliases | 2 | `DistributionLike`, `BijectorLike` |

**Sources:** [distrax/__init__.py:92-160](), [distrax/__init__.py:90]()

---

