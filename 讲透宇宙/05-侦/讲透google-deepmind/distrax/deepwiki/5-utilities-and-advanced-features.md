<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/distrax · page 5 Utilities and Advanced Features · fetched 2026-10-26 -->

# Utilities and Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [distrax/_src/distributions/beta_test.py](distrax/_src/distributions/beta_test.py)
- [distrax/_src/utils/hmm.py](distrax/_src/utils/hmm.py)
- [distrax/_src/utils/hmm_test.py](distrax/_src/utils/hmm_test.py)
- [distrax/_src/utils/math.py](distrax/_src/utils/math.py)
- [distrax/_src/utils/math_test.py](distrax/_src/utils/math_test.py)
- [distrax/_src/utils/transformations.py](distrax/_src/utils/transformations.py)
- [examples/hmm.py](examples/hmm.py)

</details>



This document covers the supporting utilities, mathematical functions, and advanced capabilities that extend Distrax's core distribution and bijector functionality. These utilities provide numerical stability, automatic function manipulation, cross-library compatibility, and specialized probabilistic models.

For core distribution implementations, see [Distributions](#3). For bijector transformations, see [Bijectors](#4).

## Mathematical Utilities

Distrax provides numerically stable mathematical functions and utilities that ensure robust computation across different numerical ranges and edge cases.

### Stable Arithmetic Operations

The `distrax._src.utils.math` module implements numerically stable versions of common operations:

| Function | Purpose | Key Feature |
|----------|---------|-------------|
| `multiply_no_nan` | Element-wise multiplication | Returns 0 when second operand is 0, even if first is NaN/infinite |
| `power_no_nan` | Element-wise exponentiation | Returns 1 when exponent is 0, regardless of base value |
| `mul_exp` | Multiply by exponential | Handles `x * exp(logp)` with zero gradient when `exp(logp)==0` |

These functions include custom JAX derivatives that properly handle symbolic zeros and maintain numerical stability during automatic differentiation.

### Probability and Normalization Functions

```mermaid
graph TB
    subgraph "Probability Utilities"
        norm["normalize()"]
        sum_last["sum_last()"]
        log_exp["log_expbig_minus_expsmall()"]
    end
    
    subgraph "Special Functions"
        log_beta["log_beta()"]
        log_beta_mv["log_beta_multivariate()"]
    end
    
    subgraph "Input Types"
        probs["probs: Array"]
        logits["logits: Array"]
        arrays["arrays: Array"]
    end
    
    subgraph "Output"
        normalized["Normalized probabilities"]
        reduced["Reduced arrays"]
        stable_log["Stable log computations"]
    end
    
    probs --> norm
    logits --> norm
    arrays --> sum_last
    arrays --> log_exp
    arrays --> log_beta
    arrays --> log_beta_mv
    
    norm --> normalized
    sum_last --> reduced
    log_exp --> stable_log
    log_beta --> stable_log
    log_beta_mv --> stable_log
```

The `normalize` function handles both probability and logit normalization, automatically detecting input type and applying appropriate normalization (direct division vs log-softmax).

**Sources:** [distrax/_src/utils/math.py:132-141](), [distrax/_src/utils/math.py:29-47](), [distrax/_src/utils/math.py:82-99]()

## Function Transformations

The `distrax._src.utils.transformations` module provides automatic function manipulation capabilities, particularly for creating inverse functions and computing Jacobian determinants.

### Automatic Function Inversion

```mermaid
graph TB
    subgraph "Inversion System"
        inv_fn["inv(fun)"]
        registry["_inverse_registry"]
        jaxpr["JAXPR Interpretation"]
    end
    
    subgraph "JAX Primitives"
        unary["Unary Operations<br/>tanh, exp, log, sqrt"]
        binary["Binary Operations<br/>mul, div, add, sub, pow"]
        custom["Custom Primitives<br/>via register_inverse()"]
    end
    
    subgraph "Inversion Process"
        trace["Trace to JAXPR"]
        reverse["Reverse Interpretation"]
        substitute["Substitute Inverses"]
    end
    
    subgraph "Output"
        inv_fun["Inverted Function"]
        composition["(inv(fun) ∘ fun)(x) = x"]
    end
    
    inv_fn --> trace
    trace --> reverse
    reverse --> substitute
    substitute --> inv_fun
    inv_fun --> composition
    
    registry --> unary
    registry --> binary
    registry --> custom
    
    unary --> substitute
    binary --> substitute
    custom --> substitute
```

The inversion system works by:
1. Tracing the input function to its JAXPR (JAX expression) representation
2. Interpreting the expression in reverse order
3. Substituting each primitive with its registered inverse operation
4. Handling both unary and binary operations with appropriate argument ordering

**Key Functions:**
- `inv(fun)` - Returns inverse function such that `(inv(fun) ∘ fun)(x) = x`
- `register_inverse(primitive, inverse_left, inverse_right=None)` - Registers custom inverse for JAX primitives

**Sources:** [distrax/_src/utils/transformations.py:129-138](), [distrax/_src/utils/transformations.py:110-127](), [distrax/_src/utils/transformations.py:68-95]()

### Jacobian Computation and Analysis

```mermaid
graph LR
    subgraph "Jacobian Utilities"
        log_det["log_det_scalar(fn)"]
        is_const["is_constant_jacobian(fn, x)"]
        stability["_check_numerical_stability()"]
    end
    
    subgraph "JAX AD System"
        jacfwd["jax.jacfwd()"]
        vmap["jax.vmap()"]
        make_jaxpr["jax.make_jaxpr()"]
    end
    
    subgraph "Analysis"
        trace_deps["_dependent_variables()"]
        check_prims["Check primitives"]
        warn["Stability warnings"]
    end
    
    subgraph "Output"
        log_det_jacobian["Log-det Jacobian"]
        const_flag["Boolean: is_constant"]
        warnings["Numerical warnings"]
    end
    
    log_det --> jacfwd
    jacfwd --> vmap
    vmap --> log_det_jacobian
    
    is_const --> make_jaxpr
    make_jaxpr --> trace_deps
    trace_deps --> const_flag
    
    stability --> check_prims
    check_prims --> warn
    warn --> warnings
```

- `log_det_scalar(fn)` - Automatically derives log-determinant of Jacobian using JAX autograd
- `is_constant_jacobian(fn, x=0.0)` - Experimental function to determine if Jacobian is constant
- Numerical stability checking warns about potentially unstable primitives like `tanh_p`

**Sources:** [distrax/_src/utils/transformations.py:166-176](), [distrax/_src/utils/transformations.py:141-163](), [distrax/_src/utils/transformations.py:178-186]()

## TensorFlow Probability Integration

Distrax provides seamless interoperability with TensorFlow Probability (TFP) through wrapper classes and shared interfaces. This enables users to mix Distrax and TFP distributions/bijectors freely.

### Cross-Library Compatibility

```mermaid
graph TB
    subgraph "Distrax Ecosystem"
        dx_dist["Distrax Distributions"]
        dx_bij["Distrax Bijectors"] 
        to_tfp["to_tfp() wrapper"]
    end
    
    subgraph "TFP Ecosystem"
        tfp_dist["TFP Distributions"]
        tfp_bij["TFP Bijectors"]
        tfp_meta["TFP Meta-distributions"]
    end
    
    subgraph "Shared Operations"
        kl_div["KL Divergence"]
        sample["Sampling"]
        log_prob["Log Probability"]
        transforms["Transformations"]
    end
    
    dx_dist --> to_tfp
    dx_bij --> to_tfp
    to_tfp --> tfp_meta
    
    tfp_dist --> dx_dist
    tfp_bij --> dx_bij
    
    dx_dist --> kl_div
    tfp_dist --> kl_div
    
    dx_dist --> sample
    tfp_dist --> sample
    
    dx_dist --> log_prob
    tfp_dist --> log_prob
    
    dx_bij --> transforms
    tfp_bij --> transforms
```

Key compatibility features:
- **Bidirectional interoperability**: TFP distributions work directly in Distrax meta-distributions
- **Wrapper functions**: `to_tfp()` enables Distrax objects to work in TFP contexts
- **Shared KL registry**: Cross-library KL divergence computations
- **Consistent APIs**: Similar method signatures and behavior across libraries

**Sources:** [README.md:77-91](), [README.md:124-136](), [README.md:173-194]()

## Hidden Markov Models

The `HMM` class provides a complete implementation of Hidden Markov Models with support for inference algorithms and parameter learning.

### HMM Architecture

```mermaid
graph TB
    subgraph "HMM Components"
        init_dist["init_dist: CategoricalLike<br/>Initial state distribution"]
        trans_dist["trans_dist: CategoricalLike<br/>Transition probabilities"]
        obs_dist["obs_dist: DistributionLike<br/>Observation distribution"]
    end
    
    subgraph "HMM Class"
        hmm_constructor["HMM.__init__()"]
        validation["Shape validation"]
        properties["Properties access"]
    end
    
    subgraph "Inference Methods"
        forward["forward()<br/>Forward probabilities"]
        backward["backward()<br/>Backward probabilities"]
        forward_backward["forward_backward()<br/>Complete inference"]
        viterbi["viterbi()<br/>Most likely path"]
    end
    
    subgraph "Sampling"
        sample["sample()<br/>Generate sequences"]
        states["Hidden states"]
        observations["Observations"]
    end
    
    init_dist --> hmm_constructor
    trans_dist --> hmm_constructor
    obs_dist --> hmm_constructor
    
    hmm_constructor --> validation
    validation --> properties
    
    properties --> forward
    properties --> backward
    properties --> forward_backward
    properties --> viterbi
    properties --> sample
    
    sample --> states
    sample --> observations
```

### HMM Inference Algorithms

The `HMM` class implements standard algorithms for probabilistic inference:

**Forward Algorithm** [`forward(obs_seq, length=None)`]:
- Computes forward probabilities `p(z_t, x_{1:t})`
- Returns log-likelihood and forward probability history
- Supports variable-length sequences via `length` parameter

**Backward Algorithm** [`backward(obs_seq, length=None)`]:
- Computes backward probabilities `p(x_{t+1:T}|z_t)`
- Used in combination with forward probabilities for full inference

**Forward-Backward Algorithm** [`forward_backward(obs_seq, length=None)`]:
- Combines forward and backward passes
- Returns marginal state probabilities `P(z_t|x_{1:T})`
- Provides complete posterior inference

**Viterbi Algorithm** [`viterbi(obs_seq)`]:
- Finds most probable state sequence
- Uses dynamic programming for efficient computation
- Returns sequence of most likely hidden states

**Sources:** [distrax/_src/utils/hmm.py:47-102](), [distrax/_src/utils/hmm.py:152-197](), [distrax/_src/utils/hmm.py:236-276](), [distrax/_src/utils/hmm.py:278-323]()

### HMM Usage Example

The HMM implementation supports complex probabilistic modeling scenarios, as demonstrated in the changepoint detection example:

```mermaid
graph LR
    subgraph "Data Generation"
        true_rates["True rates: [40, 3, 20, 50]"]
        true_durations["Durations: [10, 20, 5, 35]"]
        poisson_data["Poisson observations"]
    end
    
    subgraph "Model Construction"
        init_probs["Initial state probabilities"]
        trans_matrix["Transition matrix"]
        obs_poisson["Poisson(log_rate=log_rates)"]
        hmm_model["HMM(init_dist, trans_dist, obs_dist)"]
    end
    
    subgraph "Parameter Learning"
        loss_fn["Negative log-likelihood loss"]
        optax_adam["Optax Adam optimizer"]
        gradient_descent["Gradient descent training"]
    end
    
    subgraph "Inference"
        forward_backward_inf["Forward-backward inference"]
        viterbi_inf["Viterbi decoding"]
        changepoints["Inferred changepoints"]
    end
    
    true_rates --> poisson_data
    true_durations --> poisson_data
    
    init_probs --> hmm_model
    trans_matrix --> hmm_model
    obs_poisson --> hmm_model
    
    hmm_model --> loss_fn
    loss_fn --> optax_adam
    optax_adam --> gradient_descent
    
    gradient_descent --> forward_backward_inf
    gradient_descent --> viterbi_inf
    forward_backward_inf --> changepoints
    viterbi_inf --> changepoints
```

This example demonstrates rate changepoint detection in time series data using HMM parameter learning through gradient descent optimization.

**Sources:** [examples/hmm.py:91-96](), [examples/hmm.py:149-162](), [examples/hmm.py:191-207]()

---

