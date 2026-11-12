<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/hummingbird · extra page Tree-based Model Converters · fetched 2026-10-26 -->

# Tree-based Model Converters

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [hummingbird/ml/operator_converters/_gbdt_commons.py](hummingbird/ml/operator_converters/_gbdt_commons.py)
- [hummingbird/ml/operator_converters/_tree_commons.py](hummingbird/ml/operator_converters/_tree_commons.py)
- [hummingbird/ml/operator_converters/_tree_implementations.py](hummingbird/ml/operator_converters/_tree_implementations.py)
- [hummingbird/ml/operator_converters/lightgbm.py](hummingbird/ml/operator_converters/lightgbm.py)
- [hummingbird/ml/operator_converters/onnx/tree_ensemble.py](hummingbird/ml/operator_converters/onnx/tree_ensemble.py)
- [hummingbird/ml/operator_converters/sklearn/decision_tree.py](hummingbird/ml/operator_converters/sklearn/decision_tree.py)
- [hummingbird/ml/operator_converters/sklearn/gbdt.py](hummingbird/ml/operator_converters/sklearn/gbdt.py)
- [hummingbird/ml/operator_converters/sklearn/iforest.py](hummingbird/ml/operator_converters/sklearn/iforest.py)
- [hummingbird/ml/operator_converters/xgb.py](hummingbird/ml/operator_converters/xgb.py)
- [notebooks/LGBM-ONNX-example.ipynb](notebooks/LGBM-ONNX-example.ipynb)
- [notebooks/LGBM-ONNXML-example.ipynb](notebooks/LGBM-ONNXML-example.ipynb)
- [tests/test_lightgbm_converter.py](tests/test_lightgbm_converter.py)
- [tests/test_onnxml_decision_tree_converter.py](tests/test_onnxml_decision_tree_converter.py)
- [tests/test_sklearn_decision_tree_converter.py](tests/test_sklearn_decision_tree_converter.py)
- [tests/test_sklearn_gbdt_converter.py](tests/test_sklearn_gbdt_converter.py)
- [tests/test_sklearn_isolation_forest_converter.py](tests/test_sklearn_isolation_forest_converter.py)
- [tests/test_sklearn_scaler_converter.py](tests/test_sklearn_scaler_converter.py)
- [tests/test_xgboost_converter.py](tests/test_xgboost_converter.py)

</details>



This page documents the tree-based model converters in Hummingbird, which transform decision trees, random forests, gradient boosting, and other tree-based models from traditional ML frameworks into PyTorch/ONNX tensor computation for faster inference. This is a core component of Hummingbird's ability to accelerate tree-based models by leveraging hardware acceleration capabilities of neural network frameworks.

For information about linear model converters, see [Linear Model Converters](#4.1.1). For information about preprocessing converters, see [Preprocessing Converters](#4.1.3).

## Overview

Tree-based models (e.g., Decision Trees, Random Forests, Gradient Boosting) are very popular in traditional machine learning but typically execute inference using CPU-optimized code. Hummingbird converts these models into tensor operations that can be efficiently executed on modern hardware like GPUs or specialized ML accelerators.

```mermaid
graph LR
    subgraph "Source Models"
        sklearn["scikit-learn\nDecision Trees\nRandom Forests\nGradient Boosting"]
        xgb["XGBoost"]
        lgb["LightGBM"]
        onnxml["ONNX-ML\nTree Ensemble"]
    end

    subgraph "Hummingbird Conversion"
        params["Tree Parameter\nExtraction"]
        impl["Implementation Strategy\nSelection"]
        tensor["Tensor-Based\nImplementation"]
    end

    subgraph "Target Backends"
        torch["PyTorch"]
        torchscript["TorchScript"]
        onnx["ONNX"]
        tvm["TVM"]
    end

    sklearn & xgb & lgb & onnxml --> params
    params --> impl
    impl --> tensor
    tensor --> torch & torchscript & onnx & tvm
```

Sources: [hummingbird/ml/operator_converters/_tree_commons.py](), [hummingbird/ml/operator_converters/_tree_implementations.py]()

## Tree Implementation Strategies

Hummingbird offers three different strategies for implementing tree-based models as neural networks, each with different performance characteristics depending on the tree structure:

### 1. GEMM (General Matrix Multiplication)

The GEMM strategy converts tree decisions into matrix operations, which is efficient on GPUs for shallow trees (typically depth ≤ 3).

### 2. Tree Traversal

The Tree Traversal strategy simulates the traditional tree traversal algorithm using tensor operations. This approach is generally better for very deep trees (depth > 10).

### 3. Perfect Tree Traversal

The Perfect Tree Traversal strategy is optimized for trees of moderate depth (between 3 and 10), using an approach that assumes a perfectly balanced tree structure for more efficient memory access.

```mermaid
graph TB
    subgraph "Tree Implementation Strategies"
        direction TB
        gemm["GEMM Strategy"]
        trav["Tree Traversal Strategy"]
        perf["Perfect Tree Traversal Strategy"]
        
        gemm -->|"Shallow Trees\n(depth ≤ 3)"| shallow["Uses Matrix Multiplication\nGood for GPU acceleration\nWorks well with batched inputs"]
        trav -->|"Deep Trees\n(depth > 10)"| deep["Simulates traditional traversal\nHandles irregularly shaped trees\nGood for complex decision boundaries"]
        perf -->|"Medium Trees\n(3 < depth ≤ 10)"| medium["Optimized memory access\nBalanced traversal\nGood compromise of speed & flexibility"]
    end
```

Sources: [hummingbird/ml/operator_converters/_tree_implementations.py:14-32](), [hummingbird/ml/operator_converters/_tree_commons.py:181-207]()

## Tree Implementation Class Hierarchy

Hummingbird implements a comprehensive class hierarchy for tree-based models, with specialized implementations for different model types:

```mermaid
classDiagram
    class PhysicalOperator {
        Base class for all operators
    }
    class AbstracTreeImpl {
        +aggregation(x)
    }
    class AbstractPyTorchTreeImpl {
        +tree_parameters
        +n_features
        +classes
        +decision_cond
    }
    class TreeImpl {
        <<enumeration>>
        gemm
        tree_trav
        perf_tree_trav
    }
    
    PhysicalOperator <|-- AbstracTreeImpl
    AbstracTreeImpl <|-- AbstractPyTorchTreeImpl
    AbstractPyTorchTreeImpl <|-- GEMMTreeImpl
    AbstractPyTorchTreeImpl <|-- TreeTraversalTreeImpl
    AbstractPyTorchTreeImpl <|-- PerfectTreeTraversalTreeImpl
    
    GEMMTreeImpl <|-- GEMMDecisionTreeImpl
    GEMMTreeImpl <|-- GEMMGBDTImpl
    GEMMTreeImpl <|-- GEMMIsolationForestImpl
    
    TreeTraversalTreeImpl <|-- TreeTraversalDecisionTreeImpl
    TreeTraversalTreeImpl <|-- TreeTraversalGBDTImpl
    TreeTraversalTreeImpl <|-- TreeTraversalIsolationForestImpl
    
    PerfectTreeTraversalTreeImpl <|-- PerfectTreeTraversalDecisionTreeImpl
    PerfectTreeTraversalTreeImpl <|-- PerfectTreeTraversalGBDTImpl
    PerfectTreeTraversalTreeImpl <|-- PerfectTreeTraversalIsolationForestImpl
```

Sources: [hummingbird/ml/operator_converters/_tree_implementations.py:30-183](), [hummingbird/ml/operator_converters/_tree_implementations.py:458-630]()

## Conversion Process

The conversion of tree-based models follows a structured process:

```mermaid
graph TD
    A["Source Tree Model"] --> B["Extract Tree Parameters"]
    B --> C["Create TreeParameters Objects"]
    C --> D["Determine Max Tree Depth"]
    D --> E["Select Tree Implementation Strategy"]
    E --> F{"Which Strategy?"}
    F -->|"GEMM"| G1["Generate GEMM Parameters\n(weights & biases)"]
    F -->|"Tree Traversal"| G2["Generate Tree Traversal\nParameters"]
    F -->|"Perfect Tree Traversal"| G3["Generate Perfect Tree\nTraversal Parameters"]
    G1 & G2 & G3 --> H["Create PyTorch Implementation"]
    H --> I["Apply Post-Transform\n(if needed)"]
    I --> J["Return Converted Model"]
```

Sources: [hummingbird/ml/operator_converters/_tree_commons.py:210-228](), [hummingbird/ml/operator_converters/_tree_commons.py:443-473](), [hummingbird/ml/operator_converters/_gbdt_commons.py:68-183]()

## Tree Parameters Extraction

The first step in converting a tree-based model is extracting its parameters. Hummingbird uses a common internal representation called `TreeParameters` which contains:

- `lefts`: The indices of left child nodes
- `rights`: The indices of right child nodes
- `features`: The feature indices used for decisions at each node
- `thresholds`: The threshold values for each decision
- `values`: The output values at leaf nodes

This extraction process varies by the source model framework:

```mermaid
graph LR
    subgraph "Source-Specific Extraction"
        sklearn["Scikit-Learn\nExtraction"]
        xgb["XGBoost\nExtraction"]
        lgb["LightGBM\nExtraction"]
        onnx["ONNX-ML\nExtraction"]
    end
    
    subgraph "Common Representation"
        treeparam["TreeParameters"]
    end
    
    sklearn --> |"get_parameters_for_sklearn_common"| treeparam
    xgb --> |"_get_tree_parameters"| treeparam
    lgb --> |"_get_tree_parameters"| treeparam
    onnx --> |"_get_tree_parameters"| treeparam
```

Sources: [hummingbird/ml/operator_converters/_tree_commons.py:21-63](), [hummingbird/ml/operator_converters/xgb.py:62-81](), [hummingbird/ml/operator_converters/lightgbm.py:42-53](), [hummingbird/ml/operator_converters/onnx/tree_ensemble.py:19-180]()

## Implementation Strategy Selection

The choice of tree implementation strategy is determined by either explicit configuration or heuristics based on tree depth:

```mermaid
graph TD
    start["Tree-based Model"] --> A{"Implementation\nSpecified?"}
    A -->|"Yes"| B{"Which Strategy?"}
    A -->|"No"| C{"What is max_depth?"}
    
    B -->|"gemm"| D["GEMMTreeImpl"]
    B -->|"tree_trav"| E["TreeTraversalTreeImpl"]
    B -->|"perf_tree_trav"| F["PerfectTreeTraversalTreeImpl"]
    
    C -->|"max_depth ≤ 3"| D
    C -->|"3 < max_depth ≤ 10"| F
    C -->|"max_depth > 10"| E
```

Sources: [hummingbird/ml/operator_converters/_tree_commons.py:181-207]()

## Specialized Implementations

### Decision Trees and Random Forests

These implementations focus on single tree prediction or averaging predictions from multiple trees:

```python
# Decision Tree (simplified representation)
class GEMMDecisionTreeImpl:
    def aggregation(self, x):
        # Sum over all trees (for random forest)
        return x.sum(0).t()

class TreeTraversalDecisionTreeImpl:
    def aggregation(self, x):
        # Sum over all trees (for random forest)
        return x.sum(1)
```

Sources: [hummingbird/ml/operator_converters/sklearn/decision_tree.py:19-135](), [hummingbird/ml/operator_converters/_tree_implementations.py:458-527]()

### Gradient Boosting Models

These implementations handle the additive nature of gradient boosting models and apply appropriate post-transforms:

```python
# GBDT (simplified representation)
class GEMMGBDTImpl:
    def aggregation(self, x):
        # Sum tree predictions by class
        output = x.view(-1, self.n_gbdt_classes, self.n_trees_per_class).sum(2)
        # Apply sigmoid, softmax, etc.
        return self.post_transform(output)
```

Sources: [hummingbird/ml/operator_converters/_gbdt_commons.py:28-183](), [hummingbird/ml/operator_converters/_tree_implementations.py:531-630]()

### Isolation Forest

These implementations calculate anomaly scores:

```python
# Isolation Forest (simplified representation)
class GEMMIsolationForestImpl:
    def aggregation(self, x):
        output = x.sum(0).t()
        # Normalize and calculate anomaly score
        output = -1.0 * 2 ** (-output / self.average_path_length) - self.offset
        return output
```

Sources: [hummingbird/ml/operator_converters/sklearn/iforest.py:24-261]()

## Post-Transform Operations

After converting tree models, Hummingbird applies appropriate post-transforms based on the model type:

1. For binary classification: Sigmoid transformation
2. For multi-class classification: Softmax transformation
3. For regression: Identity or custom transformations (e.g., for Tweedie models)
4. For base prediction adjustment: Adding the initial prediction value

```mermaid
graph TD
    A["Tree Model Output"] --> B{"Model Type?"}
    
    B -->|"Binary Classifier"| C["Apply Sigmoid\n(0-1 Probability)"]
    B -->|"Multi-class Classifier"| D["Apply Softmax\n(Class Probabilities)"]
    B -->|"Regressor"| E["Identity or\nCustom Transform"]
    B -->|"Isolation Forest"| F["Anomaly Score\nCalculation"]
    
    C & D & E & F --> G["Apply Base Prediction\n(if applicable)"]
    G --> H["Final Prediction"]
```

Sources: [hummingbird/ml/operator_converters/_tree_commons.py:65-122](), [hummingbird/ml/operator_converters/_gbdt_commons.py:127-169]()

## Supported Models

Hummingbird can convert the following tree-based models:

| Model Type | Frameworks Supported | Implementation Strategies |
|------------|----------------------|---------------------------|
| Decision Trees | scikit-learn, ONNX-ML | GEMM, Tree Traversal, Perfect Tree Traversal |
| Random Forests | scikit-learn, ONNX-ML | GEMM, Tree Traversal, Perfect Tree Traversal |
| Gradient Boosting | scikit-learn, LightGBM, XGBoost, ONNX-ML | GEMM, Tree Traversal, Perfect Tree Traversal |
| Isolation Forest | scikit-learn | GEMM, Tree Traversal, Perfect Tree Traversal |

Sources: [hummingbird/ml/operator_converters/sklearn/decision_tree.py:130-135](), [hummingbird/ml/operator_converters/lightgbm.py:126-129](), [hummingbird/ml/operator_converters/xgb.py:154-156](), [hummingbird/ml/operator_converters/sklearn/iforest.py:265](), [hummingbird/ml/operator_converters/onnx/tree_ensemble.py:262-263]()

## Performance Considerations

Tree-based model conversion offers several performance advantages:

1. **Hardware Acceleration**: Converting tree-based models to tensor operations enables GPU acceleration
2. **Implementation Strategy Selection**: The optimal strategy varies by tree complexity:
   - GEMM: Best for shallow trees (depth ≤ 3), excellent on GPUs
   - Perfect Tree Traversal: Best for medium trees (3 < depth ≤ 10)
   - Tree Traversal: Best for deep trees (depth > 10)
3. **Precision Control**: Control numerical precision using `tree_op_precision_dtype` in `extra_config`:
   ```python
   extra_config = {constants.TREE_OP_PRECISION_DTYPE: "float64"}
   ```

Sources: [hummingbird/ml/operator_converters/_tree_implementations.py:97-106](), [tests/test_lightgbm_converter.py:464-469]()

## Example: Converting a Tree-based Model

Here's how conversion of a LightGBM model to ONNX works:

```mermaid
graph TB
    A["LightGBM Model"] --> B["Extract Tree Parameters\nvia model.booster_.dump_model()"]
    B --> C["Create TreeParameters\nObjects"]
    C --> D["Select Implementation\nStrategy"]
    D --> E["Convert to PyTorch\nImplementation"]
    E --> F["Convert to ONNX"]
    F --> G["ONNX Model"]
```

Example code:
```python
import numpy as np
import lightgbm as lgb
from hummingbird.ml import convert

# Create a LightGBM model
model = lgb.LGBMClassifier()
X = np.random.rand(1000, 28).astype(np.float32)
y = np.random.randint(2, size=1000)
model.fit(X, y)

# Convert to ONNX via Hummingbird
onnx_model = convert(model, "onnx")
```

Sources: [notebooks/LGBM-ONNX-example.ipynb:16-76]()

## Customization Options

Tree model converters support several customization options via `extra_config`:

| Option | Description | Possible Values |
|--------|-------------|-----------------|
| `tree_implementation` | Force a specific implementation strategy | `"gemm"`, `"tree_trav"`, `"perf_tree_trav"` |
| `tree_op_precision_dtype` | Set numerical precision | `"float32"`, `"float64"` |
| `post_transform` | Override default post-transform | `None`, `"SIGMOID"`, `"SOFTMAX"`, `"TWEEDIE"` |
| `base_prediction` | Specify a base prediction value | Float or array |

Sources: [hummingbird/ml/operator_converters/_tree_commons.py:181-207](), [hummingbird/ml/operator_converters/_tree_implementations.py:97-112](), [hummingbird/ml/operator_converters/_gbdt_commons.py:148-169]()

## Integration with Backends

Tree-based models can be converted to multiple backends:

```mermaid
graph LR
    subgraph "Tree-based Models"
        dt["Decision Trees"]
        rf["Random Forests"]
        gbdt["Gradient Boosting"]
        iforest["Isolation Forest"]
    end
    
    subgraph "Hummingbird Implementation"
        gemm["GEMM\nImplementation"]
        trav["Tree Traversal\nImplementation"]
        perf["Perfect Tree\nTraversal Implementation"]
    end
    
    subgraph "Target Backends"
        pytorch["PyTorch"]
        torchscript["TorchScript"]
        onnx["ONNX"]
        tvm["TVM"]
    end
    
    dt & rf & gbdt & iforest --> gemm & trav & perf
    gemm & trav & perf --> pytorch
    pytorch --> torchscript & onnx & tvm
```

Sources: [tests/test_lightgbm_converter.py:348-444](), [tests/test_xgboost_converter.py:292-338](), [tests/test_sklearn_isolation_forest_converter.py:107-126]()

## Summary

Hummingbird's tree-based model converters provide a sophisticated system for transforming traditional tree models into tensor-based operations. By offering multiple implementation strategies and backend targets, it allows for significant performance improvements through hardware acceleration while maintaining prediction accuracy. The conversion process handles a wide variety of tree-based models and provides customization options to optimize for specific use cases.

---

