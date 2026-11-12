<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/distrax · extra page Multivariate Normal Distributions · fetched 2026-10-26 -->

# Multivariate Normal Distributions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [distrax/_src/distributions/mvn_diag_plus_low_rank.py](distrax/_src/distributions/mvn_diag_plus_low_rank.py)
- [distrax/_src/distributions/mvn_diag_plus_low_rank_test.py](distrax/_src/distributions/mvn_diag_plus_low_rank_test.py)
- [distrax/_src/distributions/mvn_diag_test.py](distrax/_src/distributions/mvn_diag_test.py)
- [distrax/_src/distributions/mvn_from_bijector.py](distrax/_src/distributions/mvn_from_bijector.py)
- [distrax/_src/distributions/mvn_from_bijector_test.py](distrax/_src/distributions/mvn_from_bijector_test.py)
- [distrax/_src/distributions/mvn_tri.py](distrax/_src/distributions/mvn_tri.py)
- [distrax/_src/distributions/one_hot_categorical_test.py](distrax/_src/distributions/one_hot_categorical_test.py)

</details>



This document covers Distrax's multivariate normal distribution implementations, which provide efficient, JAX-native distributions over vector-valued random variables. These distributions support various covariance structures including diagonal, full covariance via triangular decomposition, and diagonal-plus-low-rank parameterizations.

For discrete distributions over categorical variables, see [Discrete Distributions](#3.1). For univariate continuous distributions, see [Continuous Distributions](#3.2). For general information about bijectors and transformations used in these implementations, see [Bijectors and Transformations](#2.2).

## Architecture Overview

Distrax's multivariate normal distributions are built on a unified bijector-based architecture. All implementations extend `MultivariateNormalFromBijector`, which transforms a standard multivariate normal using linear bijectors to create distributions with different covariance structures.

```mermaid
graph TB
    subgraph "Core Architecture"
        MVNFB["MultivariateNormalFromBijector"]
        TRANS["Transformed"]
        INDEP["Independent"]
        NORMAL["Normal"]
    end
    
    subgraph "Bijector System"
        LINEAR["Linear (ABC)"]
        DIAG["DiagLinear"]
        TRI["TriangularLinear"]
        DLOWRANK["DiagPlusLowRankLinear"]
    end
    
    subgraph "Concrete Implementations"
        MVNDIAG["MultivariateNormalDiag"]
        MVNTRI["MultivariateNormalTri"]
        MVNDLR["MultivariateNormalDiagPlusLowRank"]
    end
    
    MVNFB --> TRANS
    TRANS --> INDEP
    INDEP --> NORMAL
    
    MVNFB --> LINEAR
    LINEAR --> DIAG
    LINEAR --> TRI
    LINEAR --> DLOWRANK
    
    MVNDIAG --> MVNFB
    MVNTRI --> MVNFB
    MVNDLR --> MVNFB
    
    MVNDIAG --> DIAG
    MVNTRI --> TRI
    MVNDLR --> DLOWRANK
```

**Sources:** [distrax/_src/distributions/mvn_from_bijector.py:51-93](), [distrax/_src/distributions/mvn_tri.py:62-118](), [distrax/_src/distributions/mvn_diag_plus_low_rank.py:88-176]()

## Core Implementation: MultivariateNormalFromBijector

The `MultivariateNormalFromBijector` class implements the mathematical transformation `x = A @ z + b`, where `z ~ N(0, I)` is a standard multivariate normal, `A` is a linear transformation matrix, and `b` is the location vector. This results in `x ~ N(b, A @ A.T)`.

```mermaid
graph LR
    subgraph "Standard MVN"
        Z["z ~ N(0, I)"]
    end
    
    subgraph "Linear Transformation"
        SCALE["scale: Linear"]
        SHIFT["shift: Shift"]
        CHAIN["Chain([Block(Shift(loc)), scale])"]
    end
    
    subgraph "Transformed MVN"
        X["x ~ N(loc, scale @ scale.T)"]
    end
    
    Z --> CHAIN
    SCALE --> CHAIN
    SHIFT --> CHAIN
    CHAIN --> X
```

**Key Components:**

| Component | Type | Purpose |
|-----------|------|---------|
| `loc` | `Array` | Mean vector (location parameter) |
| `scale` | `Linear` | Bijector implementing matrix multiplication |
| `bijector` | `Chain` | Composed transformation: shift then scale |
| `distribution` | `Independent` | Standard MVN base distribution |

**Sources:** [distrax/_src/distributions/mvn_from_bijector.py:51-93](), [distrax/_src/distributions/mvn_from_bijector.py:78-87]()

## Diagonal Covariance: MultivariateNormalDiag

For diagonal covariance matrices, `MultivariateNormalDiag` uses the `DiagLinear` bijector, making the transformation `x = diag(scale_diag) @ z + loc`. This is efficient for independent components with different variances.

```mermaid
graph TB
    subgraph "Parameters"
        LOC["loc: Array[..., k]"]
        SDIAG["scale_diag: Array[..., k]"]
    end
    
    subgraph "Implementation"
        DIAGLIN["DiagLinear(scale_diag)"]
        MVNFB1["MultivariateNormalFromBijector(loc, DiagLinear)"]
    end
    
    subgraph "Properties"
        COV["covariance: diag(scale_diag²)"]
        VAR["variance: scale_diag²"]
        STD["stddev: |scale_diag|"]
    end
    
    LOC --> MVNFB1
    SDIAG --> DIAGLIN
    DIAGLIN --> MVNFB1
    
    MVNFB1 --> COV
    MVNFB1 --> VAR
    MVNFB1 --> STD
```

**Sources:** [distrax/_src/distributions/mvn_diag_test.py:30-50](), [distrax/_src/distributions/mvn_from_bijector.py:128-134]()

## Triangular Scale: MultivariateNormalTri

`MultivariateNormalTri` uses triangular matrices for the scale parameter, typically the Cholesky decomposition of the covariance matrix. The `TriangularLinear` bijector handles either lower or upper triangular matrices.

```mermaid
graph TB
    subgraph "Parameters"
        LOC2["loc: Array[..., k]"]
        STRI["scale_tri: Array[..., k, k]"]
        ISLOWER["is_lower: bool"]
    end
    
    subgraph "Processing"
        TRIL["tril(scale_tri) if is_lower"]
        TRIU["triu(scale_tri) if not is_lower"]
        TRILIN["TriangularLinear(matrix, is_lower)"]
    end
    
    subgraph "Implementation"
        MVNFB2["MultivariateNormalFromBijector(loc, TriangularLinear)"]
    end
    
    LOC2 --> MVNFB2
    STRI --> TRIL
    STRI --> TRIU
    ISLOWER --> TRILIN
    TRIL --> TRILIN
    TRIU --> TRILIN
    TRILIN --> MVNFB2
```

**Sources:** [distrax/_src/distributions/mvn_tri.py:72-118](), [distrax/_src/distributions/mvn_tri.py:113-116]()

## Diagonal Plus Low-Rank: MultivariateNormalDiagPlusLowRank

This implementation supports covariance structures of the form `C = S @ S.T` where `S = diag(D) + U @ V.T`. This is efficient for modeling correlations with a low-rank structure plus independent noise.

```mermaid
graph TB
    subgraph "Parameters"
        LOC3["loc: Array[..., k]"]
        SDIAG2["scale_diag: Array[..., k]"]
        UMAT["scale_u_matrix: Array[..., k, r]"]
        VMAT["scale_v_matrix: Array[..., k, r]"]
    end
    
    subgraph "Scale Matrix Construction"
        DLRLIN["DiagPlusLowRankLinear(u_matrix, v_matrix, diag)"]
        SCALE_FORM["S = diag(scale_diag) + U @ V.T"]
    end
    
    subgraph "Implementation"
        MVNFB3["MultivariateNormalFromBijector(loc, DiagPlusLowRankLinear)"]
    end
    
    subgraph "Covariance"
        COV_FORM["C = S @ S.T"]
    end
    
    LOC3 --> MVNFB3
    SDIAG2 --> DLRLIN
    UMAT --> DLRLIN
    VMAT --> DLRLIN
    DLRLIN --> SCALE_FORM
    SCALE_FORM --> MVNFB3
    MVNFB3 --> COV_FORM
```

**Sources:** [distrax/_src/distributions/mvn_diag_plus_low_rank.py:88-176](), [distrax/_src/distributions/mvn_diag_plus_low_rank.py:168-175]()

## Statistical Methods and Properties

All multivariate normal implementations provide consistent statistical methods through the base `MultivariateNormalFromBijector` class:

| Method | Returns | Description |
|--------|---------|-------------|
| `mean()` | `Array[..., k]` | Distribution mean (equals `loc`) |
| `median()` | `Array[..., k]` | Distribution median (equals `loc`) |
| `mode()` | `Array[..., k]` | Distribution mode (equals `loc`) |
| `variance()` | `Array[..., k]` | Marginal variances |
| `stddev()` | `Array[..., k]` | Marginal standard deviations |
| `covariance()` | `Array[..., k, k]` | Full covariance matrix |
| `sample()` | `Array[..., k]` | Random samples |
| `log_prob()` | `Array[...]` | Log probability density |

The implementations optimize these methods based on the covariance structure. For example, diagonal distributions avoid constructing full covariance matrices when computing variance.

**Sources:** [distrax/_src/distributions/mvn_from_bijector.py:105-152](), [distrax/_src/distributions/mvn_from_bijector.py:128-134]()

## TensorFlow Probability Integration

Distrax multivariate normal distributions integrate seamlessly with TensorFlow Probability through KL divergence registration and type compatibility:

```mermaid
graph LR
    subgraph "Distrax MVN Types"
        DMVNFB["MultivariateNormalFromBijector"]
    end
    
    subgraph "TFP MVN Types"
        TFPMVNLO["tfd.MultivariateNormalLinearOperator"]
        TFPMVNDIAG["tfd.MultivariateNormalDiag"]
        TFPMVNTRIL["tfd.MultivariateNormalTriL"]
        TFPMVNDLR["tfd.MultivariateNormalDiagPlusLowRank"]
    end
    
    subgraph "KL Divergence Registration"
        KL1["KL(Distrax || Distrax)"]
        KL2["KL(Distrax || TFP)"]
        KL3["KL(TFP || Distrax)"]
    end
    
    DMVNFB -.->|"RegisterKL"| KL1
    DMVNFB -.->|"RegisterKL"| KL2
    TFPMVNLO -.->|"RegisterKL"| KL3
    
    KL1 --> DMVNFB
    KL2 --> TFPMVNLO
    KL3 --> DMVNFB
```

The KL divergence implementation in `_kl_divergence_mvn_mvn` handles different scale matrix structures efficiently, using diagonal optimizations when possible.

**Sources:** [distrax/_src/distributions/mvn_from_bijector.py:214-265](), [distrax/_src/distributions/mvn_from_bijector.py:241-253]()

## Usage Patterns and Broadcasting

All multivariate normal distributions support JAX broadcasting semantics for batch processing:

```mermaid
graph TB
    subgraph "Input Shapes"
        LOC_SHAPE["loc: (batch_dims..., event_dim)"]
        SCALE_SHAPE["scale parameters: (batch_dims..., ...)"]
    end
    
    subgraph "Broadcasting Rules"
        BROADCAST["jnp.broadcast_shapes(loc.shape[:-1], scale.batch_shape)"]
    end
    
    subgraph "Output Shapes"
        BATCH_SHAPE["batch_shape: broadcasted batch dimensions"]
        EVENT_SHAPE["event_shape: (event_dim,)"]
        SAMPLE_SHAPE["samples: (sample_shape..., batch_shape..., event_dim)"]
    end
    
    LOC_SHAPE --> BROADCAST
    SCALE_SHAPE --> BROADCAST
    BROADCAST --> BATCH_SHAPE
    BATCH_SHAPE --> EVENT_SHAPE
    EVENT_SHAPE --> SAMPLE_SHAPE
```

**Parameter Validation:**
- `loc` must have at least 1 dimension with the last dimension as the event dimension
- Scale parameters must be compatible with `loc.shape[-1]`
- Matrices must be square and properly sized for the event dimension

**Sources:** [distrax/_src/distributions/mvn_from_bijector.py:40-48](), [distrax/_src/distributions/mvn_from_bijector.py:75-77]()

---

