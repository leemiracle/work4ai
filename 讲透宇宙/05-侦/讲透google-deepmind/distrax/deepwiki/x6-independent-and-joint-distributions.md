<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/distrax · extra page Independent and Joint Distributions · fetched 2026-10-26 -->

# Independent and Joint Distributions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [distrax/_src/bijectors/masked_coupling.py](distrax/_src/bijectors/masked_coupling.py)
- [distrax/_src/bijectors/masked_coupling_test.py](distrax/_src/bijectors/masked_coupling_test.py)
- [distrax/_src/distributions/dirichlet.py](distrax/_src/distributions/dirichlet.py)
- [distrax/_src/distributions/dirichlet_test.py](distrax/_src/distributions/dirichlet_test.py)
- [distrax/_src/distributions/independent_test.py](distrax/_src/distributions/independent_test.py)
- [distrax/_src/distributions/joint.py](distrax/_src/distributions/joint.py)
- [distrax/_src/distributions/joint_test.py](distrax/_src/distributions/joint_test.py)
- [distrax/_src/distributions/transformed_test.py](distrax/_src/distributions/transformed_test.py)

</details>



This document covers composite distributions that modify or combine other distributions: the `Independent` distribution, which reinterprets batch dimensions as event dimensions, and the `Joint` distribution, which combines multiple distributions into a single joint distribution. For information about bijector-based transformations, see [Transformed Distributions](#3.4.1). For information about discretization and truncation, see [Quantized and Clipped Distributions](#3.4.3).

## Independent Distribution

The `Independent` distribution wrapper reinterprets some number of rightmost batch dimensions of a base distribution as event dimensions. This is commonly used to create multivariate distributions from univariate ones or to change the statistical interpretation of existing distributions.

### Core Concept

The `Independent` distribution takes a base distribution and a parameter `reinterpreted_batch_ndims` that specifies how many batch dimensions to move into the event shape. This changes how log probabilities and other statistics are computed.

```mermaid
graph TD
    subgraph "Independent Distribution Wrapper"
        BASE["Base Distribution<br/>batch_shape=(2,3)<br/>event_shape=(4,)"]
        INDEP["Independent<br/>reinterpreted_batch_ndims=1"]
        RESULT["Resulting Distribution<br/>batch_shape=(2,)<br/>event_shape=(3,4)"]
        
        BASE --> INDEP
        INDEP --> RESULT
    end
    
    subgraph "Log Probability Behavior"
        ORIG_LP["Original: log_prob per (4,) event<br/>Output shape: (2,3)"]
        NEW_LP["Independent: log_prob per (3,4) event<br/>Output shape: (2,)"]
        
        ORIG_LP --> NEW_LP
    end
```

Sources: [distrax/_src/distributions/independent_test.py:41](), [distrax/_src/distributions/independent_test.py:184-207]()

### Key Implementation Classes

```mermaid
graph LR
    subgraph "Class Hierarchy"
        DIST["distribution.Distribution"]
        INDEP["independent.Independent"]
        
        DIST --> INDEP
    end
    
    subgraph "Core Properties"
        BATCH["batch_shape<br/>property"]
        EVENT["event_shape<br/>property"] 
        REINT["reinterpreted_batch_ndims<br/>parameter"]
        
        INDEP --> BATCH
        INDEP --> EVENT
        INDEP --> REINT
    end
    
    subgraph "Key Methods"
        SAMPLE["_sample_n()"]
        LOGPROB["log_prob()"]
        SLICE["__getitem__()"]
        
        INDEP --> SAMPLE
        INDEP --> LOGPROB
        INDEP --> SLICE
    end
```

Sources: [distrax/_src/distributions/independent_test.py:41](), [distrax/_src/distributions/independent_test.py:56-77]()

### Usage Patterns

The `Independent` distribution is commonly used in several scenarios:

| Use Case | Base Distribution | `reinterpreted_batch_ndims` | Result |
|----------|-------------------|----------------------------|---------|
| Multivariate from Univariate | `Normal(loc=[1,2,3], scale=[4,5,6])` | `1` | Multivariate Normal with independence assumption |
| Change Event Interpretation | `MultivariateNormalDiag` with batch dims | `1` or `2` | Different event/batch structure |
| TFP Compatibility | Any batched distribution | Variable | Match TFP `Independent` behavior |

The constructor supports both explicit `reinterpreted_batch_ndims` values and `None` for automatic inference.

Sources: [distrax/_src/distributions/independent_test.py:177-199](), [distrax/_src/distributions/independent_test.py:347-396]()

## Joint Distribution

The `Joint` distribution creates a single distribution over a tree structure of independent component distributions. All component distributions must have the same `batch_shape`, and the resulting samples maintain the tree structure of the input distributions.

### Core Concept

```mermaid
graph TD
    subgraph "Input Structure"
        DIST_DICT["distributions = {<br/>'cat': Categorical(...),<br/>'normal': Normal(...),<br/>'mvn': MultivariateNormalDiag(...)<br/>}"]
    end
    
    subgraph "Joint Distribution"
        JOINT["Joint(distributions)"]
        BATCH_CHECK["Validates same batch_shape<br/>across all distributions"]
        
        DIST_DICT --> JOINT
        JOINT --> BATCH_CHECK
    end
    
    subgraph "Output Operations"
        SAMPLE["sample() returns<br/>{<br/>'cat': cat_sample,<br/>'normal': normal_sample,<br/>'mvn': mvn_sample<br/>}"]
        LOGPROB["log_prob(value)<br/>sums log_probs<br/>across tree"]
        
        JOINT --> SAMPLE
        JOINT --> LOGPROB
    end
```

Sources: [distrax/_src/distributions/joint.py:34-67](), [distrax/_src/distributions/joint_test.py:30-76]()

### Tree Structure Support

The `Joint` distribution supports arbitrary tree structures using JAX's `tree` utilities:

```mermaid
graph LR
    subgraph "Supported Structures"
        SINGLE["Single Distribution<br/>Joint(normal_dist)"]
        TUPLE["Tuple Structure<br/>Joint((cat_dist, mvn_dist))"]
        LIST["List Structure<br/>Joint([cat_dist, mvn_dist])"]
        DICT["Dictionary Structure<br/>Joint({'a': dist1, 'b': dist2})"]
        NESTED["Nested Structure<br/>Joint({'cats': [cat1, cat2],<br/>'normals': (norm1, norm2)})"]
    end
    
    subgraph "Implementation Components"
        TREE_MAP["tree.map_structure()"]
        TREE_FLATTEN["tree.flatten()"]
        TREE_UNFLATTEN["tree.unflatten_as()"]
        
        SINGLE --> TREE_MAP
        TUPLE --> TREE_MAP
        LIST --> TREE_FLATTEN
        DICT --> TREE_UNFLATTEN
        NESTED --> TREE_MAP
    end
```

Sources: [distrax/_src/distributions/joint.py:53-54](), [distrax/_src/distributions/joint_test.py:243-291](), [distrax/_src/distributions/joint_test.py:115-153]()

### Core Methods Implementation

```mermaid
graph TD
    subgraph "Joint Class Methods"
        INIT["__init__(distributions)"]
        SAMPLE_N["_sample_n(key, n)"]
        SAMPLE_LP["_sample_n_and_log_prob(key, n)"]
        LOGPROB["log_prob(value)"]
        
        INIT --> SAMPLE_N
        INIT --> SAMPLE_LP
        INIT --> LOGPROB
    end
    
    subgraph "Key Operations"
        SPLIT_KEYS["jax.random.split(key, num_dists)"]
        MAP_SAMPLE["tree.map_structure(sample_fn, dists, keys)"]
        SUM_LOGPROBS["jnp.sum(jnp.stack(log_probs), axis=0)"]
        
        SAMPLE_N --> SPLIT_KEYS
        SAMPLE_N --> MAP_SAMPLE
        LOGPROB --> SUM_LOGPROBS
    end
    
    subgraph "Properties"
        BATCH_SHAPE["batch_shape: first_dist.batch_shape"]
        EVENT_SHAPE["event_shape: tree structure of event_shapes"]
        DTYPE["dtype: tree structure of dtypes"]
        
        INIT --> BATCH_SHAPE
        INIT --> EVENT_SHAPE
        INIT --> DTYPE
    end
```

Sources: [distrax/_src/distributions/joint.py:68-117](), [distrax/_src/distributions/joint.py:144-152]()

## Implementation Details

### Independent Distribution Architecture

The `Independent` distribution primarily modifies how dimensions are interpreted without changing the underlying sampling or probability computation logic:

| Operation | Base Distribution | Independent Wrapper |
|-----------|-------------------|-------------------|
| `sample()` | Returns samples with original shape | Same samples, same shape |
| `log_prob()` | Per-event log probability | Sums over reinterpreted dimensions |
| `batch_shape` | Original batch shape | Reduced by `reinterpreted_batch_ndims` |
| `event_shape` | Original event shape | Extended with reinterpreted dimensions |

Sources: [distrax/_src/distributions/independent_test.py:79-124]()

### Joint Distribution Architecture

The `Joint` distribution coordinates multiple independent distributions:

```mermaid
graph TB
    subgraph "Joint Distribution Internal Flow"
        INPUT["Tree of Distributions"]
        VALIDATE["Batch Shape Validation<br/>all dists must have same batch_shape"]
        STORE["Store as self._distributions"]
        
        INPUT --> VALIDATE
        VALIDATE --> STORE
    end
    
    subgraph "Sampling Flow"
        KEY_IN["Input PRNG Key"]
        SPLIT["jax.random.split(key, num_dists)"]
        MAP_SAMPLE["tree.map_structure(sample_fn)"]
        TREE_OUT["Tree-structured Output"]
        
        KEY_IN --> SPLIT
        SPLIT --> MAP_SAMPLE
        MAP_SAMPLE --> TREE_OUT
    end
    
    subgraph "Log Probability Flow"
        VALUE_IN["Tree-structured Input"]
        MAP_LOGPROB["tree.map_structure(log_prob_fn)"]
        FLATTEN["tree.flatten(log_probs)"]
        SUM["jnp.sum(log_probs, axis=0)"]
        SCALAR_OUT["Scalar Output"]
        
        VALUE_IN --> MAP_LOGPROB
        MAP_LOGPROB --> FLATTEN
        FLATTEN --> SUM
        SUM --> SCALAR_OUT
    end
```

Sources: [distrax/_src/distributions/joint.py:68-99](), [distrax/_src/distributions/joint.py:46-67]()

### KL Divergence and Advanced Operations

Both distributions support KL divergence computation:

- **Independent**: Uses the base distribution's KL divergence, with TFP compatibility through equivalence testing
- **Joint**: Implements `_kl_divergence_joint_joint` that sums KL divergences across corresponding tree elements

Sources: [distrax/_src/distributions/independent_test.py:304-344](), [distrax/_src/distributions/joint.py:144-152](), [distrax/_src/distributions/joint_test.py:331-344]()

---

