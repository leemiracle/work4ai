<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/botorch · page 3 Transforms · fetched 2026-10-21 -->

# Transforms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [botorch/models/transforms/__init__.py](botorch/models/transforms/__init__.py)
- [botorch/models/transforms/input.py](botorch/models/transforms/input.py)
- [botorch/models/transforms/utils.py](botorch/models/transforms/utils.py)
- [test/models/transforms/test_input.py](test/models/transforms/test_input.py)
- [test/models/transforms/test_utils.py](test/models/transforms/test_utils.py)

</details>



The transform system in BoTorch provides a comprehensive infrastructure for preprocessing inputs and outcomes in Gaussian Process models. Transforms handle normalization, standardization, discretization, and other data preprocessing operations that are essential for effective Bayesian optimization. This system is designed to be modular, composable, and integrates seamlessly with BoTorch's model infrastructure.

For information about model fitting and training, see [Models](#2). For details about acquisition function construction, see [Acquisition Functions](#4).

## Transform System Architecture

The transform system is built around two main categories: input transforms that preprocess model inputs, and outcome transforms that preprocess model outputs. The system uses an abstract base class pattern with concrete implementations for common transformations.

**Transform System Overview**
```mermaid
graph TB
    subgraph "Transform Infrastructure"
        IT["InputTransform<br/>(Abstract Base)"]
        RT["ReversibleInputTransform<br/>(Abstract Base)"]
        AT["AffineInputTransform<br/>(Base for Linear Transforms)"]
    end
    
    subgraph "Core Input Transforms" 
        N["Normalize<br/>(Unit Cube Scaling)"]
        IS["InputStandardize<br/>(Zero Mean, Unit Variance)"]
        R["Round<br/>(Discretization)"]
        W["Warp<br/>(Kumaraswamy Warping)"]
    end
    
    subgraph "Transform Composition"
        CT["ChainedInputTransform<br/>(Sequential Application)"]
        BT["BatchBroadcastedInputTransform<br/>(Batch Broadcasting)"]
    end
    
    subgraph "Utility Functions"
        ST["subset_transform<br/>(Decorator)"]
        EU["expand_and_copy_tensor"]
        KW["kumaraswamy_warp"]
    end
    
    IT --> RT
    RT --> AT
    AT --> N
    AT --> IS
    IT --> R
    IT --> W
    IT --> CT
    IT --> BT
    
    N -.-> ST
    IS -.-> ST
    W -.-> KW
    BT -.-> EU
    
    style IT fill:#f9f9f9
    style CT fill:#e1f5fe
    style BT fill:#e1f5fe
```

Sources: [botorch/models/transforms/input.py:45-443](), [botorch/models/transforms/utils.py:116-128]()

## Input Transform Base Classes

The input transform system is built on a hierarchy of abstract base classes that define the core interface and behavior patterns.

**Input Transform Class Hierarchy**
```mermaid
graph TB
    subgraph "PyTorch Infrastructure"
        PM["torch.nn.Module"]
        ABC["abc.ABC"]
    end
    
    subgraph "Transform Base Classes"
        IT["InputTransform<br/>forward(), transform(), untransform()"]
        RIT["ReversibleInputTransform<br/>reverse property"]
        AIT["AffineInputTransform<br/>coefficient, offset"]
    end
    
    subgraph "Control Properties"
        TTE["transform_on_train: bool"]
        TEE["transform_on_eval: bool"] 
        TTF["transform_on_fantasize: bool"]
        OTM["is_one_to_many: bool"]
    end
    
    PM --> IT
    ABC --> IT
    IT --> RIT
    RIT --> AIT
    
    IT -.-> TTE
    IT -.-> TEE
    IT -.-> TTF
    IT -.-> OTM
    
    style IT fill:#e8f5e8
    style RIT fill:#fff3e0
    style AIT fill:#e1f5fe
```

Sources: [botorch/models/transforms/input.py:45-105](), [botorch/models/transforms/input.py:377-443](), [botorch/models/transforms/input.py:445-618]()

### InputTransform Base Class

The `InputTransform` class defines the core interface for all input transformations:

| Method | Purpose | Required Implementation |
|--------|---------|------------------------|
| `forward(X)` | Main entry point, handles mode-dependent application | Inherited |
| `transform(X)` | Core transformation logic | Abstract - must implement |
| `untransform(X)` | Reverse transformation | Optional |
| `preprocess_transform(X)` | Preprocessing without learning | Inherited |
| `equals(other)` | Equality comparison | Inherited |

The transform application is controlled by three boolean flags:
- `transform_on_train`: Apply during model training mode
- `transform_on_eval`: Apply during model evaluation mode  
- `transform_on_fantasize`: Apply during fantasize operations

Sources: [botorch/models/transforms/input.py:45-158]()

## Core Input Transform Implementations

### Normalize Transform

The `Normalize` transform scales inputs to the unit cube, typically centering them at 0.5. It supports both learned bounds (from training data) and fixed bounds.

```mermaid
graph LR
    subgraph "Normalize Transform Flow"
        X["Raw Inputs<br/>X ∈ [min, max]"]
        T["Transform<br/>(X - offset) / coefficient"]
        Y["Normalized Inputs<br/>Y ∈ [0, 1]"]
        
        subgraph "Parameters"
            O["offset = bounds[0]"]
            C["coefficient = bounds[1] - bounds[0]"]
            B["bounds: learned or fixed"]
        end
    end
    
    X --> T
    T --> Y
    O --> T
    C --> T
    B --> O
    B --> C
```

Key features:
- **Learned bounds mode**: Updates bounds from training data via `_update_coefficients()`
- **Fixed bounds mode**: Uses provided bounds without updates
- **Partial indexing**: Can transform only specified input dimensions
- **Batch support**: Handles batched transformations per batch dimension

Sources: [botorch/models/transforms/input.py:620-774]()

### InputStandardize Transform

The `InputStandardize` transform normalizes inputs to zero mean and unit variance:

```mermaid
graph LR
    subgraph "InputStandardize Transform"
        X["Raw Inputs"]
        SM["Compute Statistics<br/>mean, std"]
        T["Transform<br/>(X - mean) / std"]
        Y["Standardized Inputs<br/>μ=0, σ=1"]
    end
    
    X --> SM
    SM --> T
    T --> Y
    
    subgraph "Statistics Update"
        UD["_update_coefficients()"]
        MS["min_std threshold"]
        TM["torch.std_mean()"]
    end
    
    SM -.-> UD
    UD --> MS
    UD --> TM
```

The transform includes safeguards against numerical instability with `min_std` parameter to prevent division by very small standard deviations.

Sources: [botorch/models/transforms/input.py:776-853]()

### Round Transform

The `Round` transform handles discretization for integer and categorical variables:

```mermaid
graph TB
    subgraph "Round Transform Components"
        II["integer_indices<br/>List of integer parameter indices"]
        CF["categorical_features<br/>Dict mapping start_idx: cardinality"]
        
        subgraph "Rounding Methods"
            ER["Exact Rounding<br/>torch.round()"]
            AR["Approximate Rounding<br/>Differentiable with STE"]
        end
        
        subgraph "Categorical Handling"
            OH["One-Hot Encoding"]
            AM["torch.argmax()"]
        end
    end
    
    II --> ER
    II --> AR
    CF --> OH
    OH --> AM
    
    style ER fill:#e8f5e8
    style AR fill:#fff3e0
```

The transform supports both exact rounding (non-differentiable) and approximate rounding (differentiable) with straight-through estimators for gradient computation.

Sources: [botorch/models/transforms/input.py:855-1069]()

## Transform Composition

### ChainedInputTransform

The `ChainedInputTransform` enables sequential application of multiple transforms:

```mermaid
graph LR
    subgraph "Chained Transform Pipeline"
        X["Input X"]
        T1["Transform 1<br/>(e.g., Normalize)"]
        T2["Transform 2<br/>(e.g., Round)"]
        T3["Transform 3<br/>(e.g., Standardize)"]
        Y["Final Output"]
    end
    
    X --> T1
    T1 --> T2 
    T2 --> T3
    T3 --> Y
    
    subgraph "Reverse Flow"
        Y2["Transformed Input"]
        U3["Untransform 3"]
        U2["Untransform 2"] 
        U1["Untransform 1"]
        X2["Original Input"]
    end
    
    Y2 --> U3
    U3 --> U2
    U2 --> U1
    U1 --> X2
```

Forward transforms are applied in order, while untransforms are applied in reverse order to maintain correctness.

Sources: [botorch/models/transforms/input.py:284-375]()

### BatchBroadcastedInputTransform

The `BatchBroadcastedInputTransform` applies different transforms to different batch dimensions:

```mermaid
graph TB
    subgraph "Batch Broadcasting Example"
        X["Input Tensor<br/>shape: [2, n, d]"]
        
        subgraph "Transform Application"
            X0["X[0] → Transform 1"]
            X1["X[1] → Transform 2"]
        end
        
        subgraph "Results"
            Y0["Y[0] = T1(X[0])"]
            Y1["Y[1] = T2(X[1])"]
            Y["torch.stack([Y[0], Y[1]])<br/>shape: [2, n, d]"]
        end
    end
    
    X --> X0
    X --> X1
    X0 --> Y0
    X1 --> Y1
    Y0 --> Y
    Y1 --> Y
    
    style X fill:#e1f5fe
    style Y fill:#e8f5e8
```

This enables using batched GP models where different batch dimensions require different input preprocessing.

Sources: [botorch/models/transforms/input.py:160-282]()

## Transform Utilities and Helpers

### Subset Transform Decorator

The `subset_transform` decorator handles partial dimension transformation:

```python
@subset_transform
def _transform(self, X: Tensor) -> Tensor:
    # Transform logic here
    return transformed_X
```

This decorator automatically:
- Clones input tensors to avoid in-place modifications
- Applies transforms only to specified indices 
- Handles batch shape expansion when needed
- Returns properly shaped output tensors

**Subset Transform Logic Flow**
```mermaid
graph TD
    D["@subset_transform decorator"]
    C["Check for self.indices"]
    F["Full Transform"]
    P["Partial Transform"]
    CL["Clone Input X"]
    E["Expand for batch_shape"]
    A["Apply to X[..., indices]"]
    
    D --> C
    C -->|No indices| F
    C -->|Has indices| P
    P --> CL
    CL --> E
    E --> A
    
    style D fill:#fff3e0
    style P fill:#e8f5e8
```

Sources: [botorch/models/transforms/utils.py:116-128]()

### Specialized Transform Utilities

The transform system includes several utility functions for specific operations:

| Function | Purpose | Usage |
|----------|---------|-------|
| `kumaraswamy_warp()` | Warp inputs through Kumaraswamy CDF | Input warping transforms |
| `inv_kumaraswamy_warp()` | Inverse Kumaraswamy warping | Reversing warp transforms |
| `expand_and_copy_tensor()` | Expand tensors for batch operations | Batch processing |
| `interaction_features()` | Compute interaction terms | Feature engineering |

Sources: [botorch/models/transforms/utils.py:163-209](), [botorch/models/transforms/utils.py:94-113](), [botorch/models/transforms/utils.py:131-143]()

## Working with Transforms

### Transform Lifecycle

Transforms follow a standard lifecycle pattern within BoTorch models:

```mermaid
graph TD
    subgraph "Transform Integration"
        MI["Model Initialization"]
        IT["Input Transform Setup"]
        TD["Training Data Processing"]
        MT["Model Training"]
        P["Prediction Phase"]
        CO["Candidate Optimization"]
    end
    
    subgraph "Transform Operations"
        PP["preprocess_transform()"]
        FT["forward() in train mode"]
        FE["forward() in eval mode"]
        UT["untransform()"]
    end
    
    MI --> IT
    IT --> TD
    TD --> PP
    TD --> FT
    MT --> P
    P --> FE
    P --> CO
    CO --> UT
    
    style IT fill:#e1f5fe
    style PP fill:#e8f5e8
    style FT fill:#e8f5e8
    style FE fill:#fff3e0
```

### Best Practices

1. **Transform Ordering**: In chained transforms, apply normalization before standardization, and discretization last
2. **Batch Shapes**: Ensure transform batch shapes are compatible with model batch shapes
3. **Gradient Flow**: Use approximate rounding for differentiable optimization pipelines
4. **Preprocessing**: Use `preprocess_transform()` for baseline data in acquisition functions

Sources: [botorch/models/transforms/input.py:132-157](), [botorch/models/transforms/input.py:252-269](), [botorch/models/transforms/input.py:358-374]()

---

