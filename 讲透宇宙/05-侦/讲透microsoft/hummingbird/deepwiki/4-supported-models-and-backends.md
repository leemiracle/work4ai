<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/hummingbird · page 4 Supported Models and Backends · fetched 2026-10-26 -->

# Supported Models and Backends

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [hummingbird/ml/operator_converters/__init__.py](hummingbird/ml/operator_converters/__init__.py)
- [hummingbird/ml/operator_converters/_linear_implementations.py](hummingbird/ml/operator_converters/_linear_implementations.py)
- [hummingbird/ml/operator_converters/sklearn/linear.py](hummingbird/ml/operator_converters/sklearn/linear.py)
- [hummingbird/ml/supported.py](hummingbird/ml/supported.py)
- [tests/test_lightgbm_converter.py](tests/test_lightgbm_converter.py)
- [tests/test_sklearn_decision_tree_converter.py](tests/test_sklearn_decision_tree_converter.py)
- [tests/test_sklearn_isolation_forest_converter.py](tests/test_sklearn_isolation_forest_converter.py)
- [tests/test_sklearn_linear_converter.py](tests/test_sklearn_linear_converter.py)
- [tests/test_sklearn_scaler_converter.py](tests/test_sklearn_scaler_converter.py)
- [tests/test_sklearn_sv_converter.py](tests/test_sklearn_sv_converter.py)
- [tests/test_xgboost_converter.py](tests/test_xgboost_converter.py)

</details>



This document provides a comprehensive overview of the machine learning models that Hummingbird can convert and the target backends it supports. Hummingbird serves as a bridge between traditional ML frameworks and neural network execution environments, enabling faster inference while maintaining the familiar training interfaces. For details about how the conversion process works, see [Model Conversion Pipeline](#3.1).

## Supported Input Models

Hummingbird can convert a wide variety of machine learning models from popular frameworks into tensor-based representations for efficient inference.

### scikit-learn Models

```mermaid
graph TD
    subgraph "scikit-learn Models"
        sk["scikit-learn"]
        sk --> sk_tree["Tree-based Models"]
        sk --> sk_linear["Linear Models"]
        sk --> sk_svm["SVM Models"]
        sk --> sk_nn["Neural Networks"]
        sk --> sk_nb["Naive Bayes"]
        sk --> sk_preproc["Preprocessing"]
        sk --> sk_other["Other Models"]
        
        sk_tree --> dt["DecisionTreeClassifier/Regressor"]
        sk_tree --> rf["RandomForestClassifier/Regressor"]
        sk_tree --> et["ExtraTreesClassifier/Regressor"]
        sk_tree --> gb["GradientBoostingClassifier/Regressor"]
        sk_tree --> hgb["HistGradientBoostingClassifier/Regressor"]
        sk_tree --> iforest["IsolationForest"]
        
        sk_linear --> lr["LinearRegression"]
        sk_linear --> logr["LogisticRegression/CV"]
        sk_linear --> sgd["SGDClassifier"]
        sk_linear --> ridge["Ridge/RidgeCV"]
        sk_linear --> lasso["Lasso"]
        sk_linear --> enet["ElasticNet"]
        
        sk_svm --> lsvc["LinearSVC/SVR"]
        sk_svm --> svc["SVC/NuSVC"]
        
        sk_nn --> mlp["MLPClassifier/Regressor"]
        
        sk_nb --> bnb["BernoulliNB"]
        sk_nb --> gnb["GaussianNB"]
        sk_nb --> mnb["MultinomialNB"]
        
        sk_preproc --> scaler["Standard/MinMax/RobustScaler"]
        sk_preproc --> enc["OneHotEncoder/LabelEncoder"]
        sk_preproc --> norm["Normalizer"]
        sk_preproc --> kbins["KBinsDiscretizer"]
        
        sk_other --> kmeans["KMeans"]
        sk_other --> knn["KNeighborsClassifier/Regressor"]
        sk_other --> mix["BayesianGaussianMixture"]
    end
```

Sources: [hummingbird/ml/supported.py:17-71](hummingbird/ml/supported.py:17-71), [hummingbird/ml/supported.py:123-285]()

### Gradient Boosting Frameworks

```mermaid
graph TD
    subgraph "Gradient Boosting Frameworks"
        lgbm["LightGBM"]
        xgb["XGBoost"]
        
        lgbm --> lgbm_cls["LGBMClassifier"]
        lgbm --> lgbm_reg["LGBMRegressor"]
        lgbm --> lgbm_rank["LGBMRanker"]
        lgbm --> lgbm_boost["Booster"]
        
        xgb --> xgb_cls["XGBClassifier"]
        xgb --> xgb_reg["XGBRegressor"]
        xgb --> xgb_rank["XGBRanker"]
    end
```

Sources: [hummingbird/ml/supported.py:73-81](hummingbird/ml/supported.py:73-81), [hummingbird/ml/supported.py:310-329](), [tests/test_lightgbm_converter.py](), [tests/test_xgboost_converter.py]()

### Other Supported Frameworks

```mermaid
graph TD
    subgraph "Other Frameworks"
        onnx["ONNX-ML"]
        spark["SparkML"]
        prophet["Prophet"]
        
        onnx --> onnx_lin["LinearClassifier/Regressor"]
        onnx --> onnx_tree["TreeEnsembleClassifier/Regressor"]
        onnx --> onnx_svm["SVMClassifier"]
        onnx --> onnx_prep["Preprocessing Operators"]
        onnx --> onnx_ops["Basic Operators"]
        
        onnx_prep --> onnx_enc["LabelEncoder/OneHotEncoder"]
        onnx_prep --> onnx_norm["Normalizer/Scaler"]
        onnx_prep --> onnx_imputer["Imputer"]
        
        onnx_ops --> onnx_math["Add/Div/Mul/Sum"]
        onnx_ops --> onnx_shape["Reshape/Concat/Gather"]
        
        spark --> spark_feat["Bucketizer/VectorAssembler"]
        spark --> spark_lin["LogisticRegressionModel"]
        
        prophet --> prophet_model["Prophet"]
    end
```

Sources: [hummingbird/ml/supported.py:83-107](hummingbird/ml/supported.py:83-107), [hummingbird/ml/supported.py:289-307](), [hummingbird/ml/supported.py:334-373]()

## Supported Target Backends

Hummingbird converts the source ML models into one of several neural network inference frameworks:

```mermaid
graph TD
    subgraph "Target Backends"
        pytorch["PyTorch"]
        ts["TorchScript"]
        onnx["ONNX"]
        tvm["TVM"]
    end
    
    pytorch --> pytorch_features["GPU Acceleration<br>Dynamic Computation<br>All Models Supported"]
    ts --> ts_features["Production Deployment<br>Serialization<br>Optimized Execution"]
    onnx --> onnx_features["Cross-Platform<br>Hardware Accelerators<br>Standardized Format"]
    tvm --> tvm_features["Hardware-specific Optimization<br>Specialized Accelerators<br>Compile-time Optimization"]
```

Sources: [hummingbird/ml/supported.py:10-15](hummingbird/ml/supported.py:10-15), [hummingbird/ml/supported.py:387-412]()

## Conversion Process Flow

```mermaid
flowchart LR
    A["Source Model"]
    B["Hummingbird Converter"]
    C["Target Backend Model"]
    
    A --> B
    B --> C
    
    subgraph "Source Model Types"
        A1["scikit-learn"]
        A2["LightGBM"]
        A3["XGBoost"]
        A4["ONNX-ML"]
        A5["SparkML"]
    end
    
    subgraph "Conversion Process"
        B1["Parse Model"]
        B2["Create Topology"]
        B3["Convert Operators"]
        B4["Generate Backend Code"]
    end
    
    subgraph "Target Backends"
        C1["PyTorch"]
        C2["TorchScript"]
        C3["ONNX"]
        C4["TVM"]
    end
    
    A1 & A2 & A3 & A4 & A5 --> B
    B1 --> B2 --> B3 --> B4
    B --> C1 & C2 & C3 & C4
```

Sources: [hummingbird/ml/supported.py](), [hummingbird/ml/operator_converters/__init__.py]()

## Tree-Based Model Implementation Strategies

Tree-based models (such as Random Forests, Decision Trees, Gradient Boosting models, etc.) can be implemented in different ways in Hummingbird, each with different performance characteristics:

```mermaid
graph TD
    subgraph "Tree Implementation Strategies"
        A["Tree-based Model"]
        A --> B["Implementation Strategy"]
        
        B --> C["GEMM<br>(Matrix Multiplication)"]
        B --> D["Tree Traversal"]
        B --> E["Perfect Tree Traversal"]
        
        C --> C_desc["Optimized for large batch sizes<br>Uses hardware-accelerated matrix ops"]
        D --> D_desc["Direct tree traversal logic<br>Better for small batch sizes"]
        E --> E_desc["Optimized for balanced trees<br>Best performance for specific cases"]
    end
```

The implementation strategy can be selected using the `tree_implementation` configuration parameter:

```python
# Example usage
import hummingbird.ml
# Convert using GEMM implementation
model_gemm = hummingbird.ml.convert(model, "torch", 
                                   extra_config={"tree_implementation": "gemm"})
# Convert using tree traversal implementation
model_trav = hummingbird.ml.convert(model, "torch", 
                                   extra_config={"tree_implementation": "tree_trav"})
# Convert using perfect tree traversal implementation
model_perf = hummingbird.ml.convert(model, "torch", 
                                   extra_config={"tree_implementation": "perf_tree_trav"})
```

Sources: [hummingbird/ml/supported.py:526-527](hummingbird/ml/supported.py:526-527), [tests/test_lightgbm_converter.py:30-35](), [tests/test_xgboost_converter.py:35-42](), [tests/test_sklearn_decision_tree_converter.py:31-39](), [tests/test_sklearn_isolation_forest_converter.py:26-30]()

## Configuration Options

Hummingbird provides several configuration options that can be specified during conversion:

| Configuration Option | Description | Possible Values |
|----------------------|-------------|----------------|
| `tree_implementation` | Tree implementation strategy | "gemm", "tree_trav", "perf_tree_trav" |
| `tree_op_precision_dtype` | Data type for tree thresholds | "float32", "float64" |
| `onnx_model_name` | Name for output ONNX model | Any string |
| `onnx_target_opset` | Target ONNX opset version | Integer (default: 11) |
| `tvm_max_fuse_depth` | Maximum operation fusion depth for TVM | Integer (default: 50) |
| `tvm_pad_prediction_inputs` | Pad inputs for variable batch sizes in TVM | Boolean |
| `input_names` | Names for input tensors | List of strings |
| `output_names` | Names for output tensors | List of strings |
| `container` | Return container or just model | Boolean |
| `n_threads` | Number of threads for scoring | Integer |
| `batch_size` | Batch size for inference partitioning | Integer |
| `remainder_size` | Maximum size for remainder model | Integer |
| `max_string_length` | Maximum string feature length | Integer |

These configuration options can be passed to the `convert` function through the `extra_config` parameter:

```python
# Example usage
import hummingbird.ml
# Convert with custom configuration
model_converted = hummingbird.ml.convert(
    model, 
    "torch",
    extra_config={
        "tree_implementation": "gemm",
        "n_threads": 4
    }
)
```

Sources: [hummingbird/ml/supported.py:524-569](hummingbird/ml/supported.py:524-569)

## Operator Conversion Process

```mermaid
flowchart TD
    A["Input ML Model"] --> B{"Framework Type"}
    
    B --> B1["scikit-learn Model"]
    B --> B2["LightGBM Model"]
    B --> B3["XGBoost Model"]
    B --> B4["ONNX-ML Model"]
    B --> B5["SparkML Model"]
    
    B1 & B2 & B3 & B4 & B5 --> C["Operator Name Mapping"]
    
    C --> D["Get Appropriate Converter"]
    
    D --> D1["Linear Model Converters"]
    D --> D2["Tree-based Model Converters"]
    D --> D3["Preprocessing Converters"]
    D --> D4["SVM Converters"]
    D --> D5["Other Specialized Converters"]
    
    D1 & D2 & D3 & D4 & D5 --> E["Convert to Target Backend"]
    
    E --> F1["PyTorch Implementation"]
    E --> F2["TorchScript Implementation"]
    E --> F3["ONNX Implementation"]
    E --> F4["TVM Implementation"]
```

Sources: [hummingbird/ml/supported.py:461-505](), [hummingbird/ml/operator_converters/__init__.py:19-58](hummingbird/ml/operator_converters/__init__.py:19-58)

## Example Linear Model Conversion

This example shows how a scikit-learn linear model is converted to a PyTorch implementation:

```mermaid
flowchart LR
    A["scikit-learn LinearModel"] --> B["Extract Parameters"]
    B --> B1["coefficients"]
    B --> B2["intercepts"]
    B --> B3["classes"]
    
    B1 & B2 & B3 --> C["Create LinearModel PyTorch Module"]
    
    C --> D["Forward Method"]
    D --> D1["Matrix Multiplication + Bias"]
    D1 --> D2["Apply Activation Function"]
    D2 --> D3["Return Predictions"]
    
    C --> E["PyTorch Model"]
```

Sources: [hummingbird/ml/operator_converters/sklearn/linear.py:18-114](hummingbird/ml/operator_converters/sklearn/linear.py:18-114), [hummingbird/ml/operator_converters/_linear_implementations.py:16-84](hummingbird/ml/operator_converters/_linear_implementations.py:16-84)

## Compatibility Matrix

The following table summarizes the compatibility between input model types and target backends:

| Input Model Type | PyTorch | TorchScript | ONNX | TVM |
|------------------|---------|-------------|------|-----|
| scikit-learn     | ✓       | ✓           | ✓    | ✓   |
| LightGBM         | ✓       | ✓           | ✓    | ✓   |
| XGBoost          | ✓       | ✓           | ✓    | ✓   |
| ONNX-ML          | ✓       | ✓           | ✓    | ✓   |
| SparkML          | ✓       | ✓           | ✓    | ✓   |
| Prophet          | ✓       | ✓           | ✗    | ✗   |

Sources: [hummingbird/ml/supported.py](), [tests/test_lightgbm_converter.py:349-444](), [tests/test_xgboost_converter.py:272-337](), [tests/test_sklearn_decision_tree_converter.py:504-535]()

## Conclusion

Hummingbird supports a wide range of machine learning models from various frameworks and can convert them to multiple target backends for efficient inference. The library provides flexible configuration options, particularly for tree-based models, allowing users to optimize for specific use cases.

For more detailed information about specific converters and their implementations, see [Operator Converters](#4.1).

---

