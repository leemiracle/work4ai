<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/responsible-ai-toolbox · extra page Matrix Filter (Heatmap) · fetched 2026-10-26 -->

# Matrix Filter (Heatmap)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [erroranalysis/erroranalysis/_internal/cohort_filter.py](erroranalysis/erroranalysis/_internal/cohort_filter.py)
- [erroranalysis/erroranalysis/_internal/constants.py](erroranalysis/erroranalysis/_internal/constants.py)
- [erroranalysis/erroranalysis/_internal/matrix_filter.py](erroranalysis/erroranalysis/_internal/matrix_filter.py)
- [erroranalysis/erroranalysis/_internal/metrics.py](erroranalysis/erroranalysis/_internal/metrics.py)
- [erroranalysis/erroranalysis/_internal/surrogate_error_tree.py](erroranalysis/erroranalysis/_internal/surrogate_error_tree.py)
- [erroranalysis/erroranalysis/analyzer/error_analyzer.py](erroranalysis/erroranalysis/analyzer/error_analyzer.py)
- [erroranalysis/erroranalysis/version.py](erroranalysis/erroranalysis/version.py)
- [erroranalysis/requirements-object-detection.txt](erroranalysis/requirements-object-detection.txt)
- [erroranalysis/tests/common_utils.py](erroranalysis/tests/common_utils.py)
- [erroranalysis/tests/test_cohort_filter.py](erroranalysis/tests/test_cohort_filter.py)
- [erroranalysis/tests/test_error_report.py](erroranalysis/tests/test_error_report.py)
- [erroranalysis/tests/test_importances.py](erroranalysis/tests/test_importances.py)
- [erroranalysis/tests/test_matrix_filter.py](erroranalysis/tests/test_matrix_filter.py)
- [erroranalysis/tests/test_metrics.py](erroranalysis/tests/test_metrics.py)
- [erroranalysis/tests/test_surrogate_error_tree.py](erroranalysis/tests/test_surrogate_error_tree.py)

</details>



## Purpose and Scope

The Matrix Filter (also called the Heatmap) is a 2D or 1D visualization component in the Error Analysis Engine that bins data points along one or two features and computes error metrics for each bin. This document covers the algorithm, binning strategies, metric aggregation, and data structures used to generate the matrix visualization.

For information about the hierarchical error tree visualization, see [Surrogate Error Tree](#3.4.1). For information about filtering data with cohorts, see [Cohort Filtering](#3.4.3).

## Overview

The Matrix Filter enables users to identify error patterns by visualizing how model performance varies across different ranges of feature values. It supports:

- **1D or 2D matrices**: Analyze error distribution across one or two features
- **Multiple binning strategies**: Equal-width or quantile binning for continuous features
- **Categorical feature handling**: Direct grouping without binning for discrete features
- **Multiple metrics**: Error rate, precision, recall, F1, MSE, MAE, and more
- **Cohort filtering**: Apply filters before computing the matrix

**Primary Entry Point**: `BaseAnalyzer.compute_matrix()` and `BaseAnalyzer.compute_matrix_on_dataset()` in [erroranalysis/erroranalysis/analyzer/error_analyzer.py:251-313]()

**Core Implementation**: [erroranalysis/erroranalysis/_internal/matrix_filter.py]()

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:1-1025](), [erroranalysis/erroranalysis/analyzer/error_analyzer.py:251-313]()

## Architecture and Data Flow

The following diagram shows how the matrix filter computation flows through the system:

```mermaid
graph TB
    User["User via BaseAnalyzer"]
    
    subgraph "API Layer"
        CM["compute_matrix()<br/>features, filters, composite_filters"]
        CMD["compute_matrix_on_dataset()<br/>features, dataset"]
    end
    
    subgraph "Filter Layer"
        FFC["filter_from_cohort()<br/>Apply filters to dataset"]
    end
    
    subgraph "Matrix Computation"
        CMOD["compute_matrix_on_dataset()<br/>Core implementation"]
        
        subgraph "Feature Processing"
            DetectType["Detect feature type:<br/>categorical or continuous"]
            BinContinuous["bin_data()<br/>Equal-width or quantile"]
            UseCategorical["Use unique values<br/>for categorical"]
        end
        
        subgraph "Metric Calculation"
            Is2D{"2D matrix?"}
            Crosstab2D["pd.crosstab()<br/>for 2D matrix"]
            GroupBy1D["groupby + agg<br/>for 1D matrix"]
            AggFunc["_AggFunc or<br/>_MultiMetricAggFunc"]
        end
        
        subgraph "Output Construction"
            Matrix2D["matrix_2d()<br/>Build 2D JSON"]
            Matrix1D["matrix_1d()<br/>Build 1D JSON"]
        end
    end
    
    User --> CM
    User --> CMD
    CM --> FFC
    FFC --> CMOD
    CMD --> CMOD
    
    CMOD --> DetectType
    DetectType --> BinContinuous
    DetectType --> UseCategorical
    
    BinContinuous --> Is2D
    UseCategorical --> Is2D
    
    Is2D -->|Yes| Crosstab2D
    Is2D -->|No| GroupBy1D
    
    Crosstab2D --> AggFunc
    GroupBy1D --> AggFunc
    
    AggFunc --> Matrix2D
    AggFunc --> Matrix1D
    
    Matrix2D --> Output["Matrix JSON<br/>with bins and metrics"]
    Matrix1D --> Output
```

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:58-389](), [erroranalysis/erroranalysis/analyzer/error_analyzer.py:251-313]()

## Core Components

### Entry Points

The matrix filter is accessed through two main methods on `BaseAnalyzer`:

| Method | Description | Parameters |
|--------|-------------|------------|
| `compute_matrix()` | Applies filters then computes matrix | `features, filters, composite_filters, quantile_binning, num_bins` |
| `compute_matrix_on_dataset()` | Computes matrix on pre-filtered dataset | `features, dataset, quantile_binning, num_bins` |

Both methods delegate to `_compute_matrix()` and `_compute_matrix_on_dataset()` in [erroranalysis/erroranalysis/_internal/matrix_filter.py:322-389]().

Sources: [erroranalysis/erroranalysis/analyzer/error_analyzer.py:251-313](), [erroranalysis/erroranalysis/_internal/matrix_filter.py:58-76, 322-389]()

### Feature Detection and Binning

The algorithm determines whether to bin a feature based on:

1. **Categorical feature list**: Features in `analyzer.categorical_features` are not binned
2. **Unique value count**: If `unique_count > num_bins`, the feature is binned
3. **Binning method**: Equal-width (`pd.cut`) or quantile (`pd.qcut`)

```mermaid
graph LR
    Feature["Feature to analyze"]
    
    IsCat{"Is categorical<br/>or has few<br/>unique values?"}
    
    BinMethod{"Binning method?"}
    
    EqualWidth["pd.cut()<br/>Equal-width bins"]
    Quantile["pd.qcut()<br/>Quantile bins"]
    NoBin["Use unique values<br/>as categories"]
    
    AdjustEdge["adjust_bin_max_edge()<br/>Fix floating point issues"]
    
    Result["Binned/categorized<br/>feature values"]
    
    Feature --> IsCat
    IsCat -->|No| BinMethod
    IsCat -->|Yes| NoBin
    
    BinMethod -->|Equal width| EqualWidth
    BinMethod -->|Quantile| Quantile
    
    EqualWidth --> AdjustEdge
    Quantile --> AdjustEdge
    
    AdjustEdge --> Result
    NoBin --> Result
```

**Key Function**: `bin_data()` in [erroranalysis/erroranalysis/_internal/matrix_filter.py:417-501]()

The function handles edge cases:
- **Empty columns**: Returns empty bins gracefully
- **Duplicate edges**: Warns user when too many duplicates exist (e.g., many zeros)
- **Floating-point precision**: Adjusts max bin edge to include maximum value
- **Quantile edge adjustment**: Adds tolerance to leftmost bin to include boundary values

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:78-320, 417-501]()

### Metric Aggregation

The matrix filter uses aggregation function classes to compute metrics for each bin:

```mermaid
graph TB
    subgraph "Aggregation Strategy"
        BaseAgg["_BaseAggFunc<br/>Abstract base class"]
        
        SimpleAgg["_AggFunc<br/>Single metric aggregation"]
        MultiAgg["_MultiMetricAggFunc<br/>Multi-metric with confusion matrix"]
    end
    
    BaseAgg -.implements.-> SimpleAgg
    BaseAgg -.implements.-> MultiAgg
    
    subgraph "Methods"
        AggPair["_agg_func_pair()<br/>For pd.crosstab"]
        AggGrouped["_agg_func_grouped()<br/>For groupby"]
        FillNA["_fill_na_value()<br/>Default for empty bins"]
    end
    
    SimpleAgg --> AggPair
    SimpleAgg --> AggGrouped
    SimpleAgg --> FillNA
    
    MultiAgg --> AggPair
    MultiAgg --> AggGrouped
    MultiAgg --> FillNA
    
    subgraph "Metric Types"
        ErrorRate["ERROR_RATE<br/>Classification/regression"]
        Precision["PRECISION_SCORE<br/>Includes TP, FP"]
        Recall["RECALL_SCORE<br/>Includes TP, FN"]
        F1["F1_SCORE<br/>Includes TP, FP, FN, TN"]
        Regression["MAE, MSE, etc.<br/>Regression metrics"]
    end
    
    SimpleAgg -.used for.-> ErrorRate
    SimpleAgg -.used for.-> Regression
    MultiAgg -.used for.-> Precision
    MultiAgg -.used for.-> Recall
    MultiAgg -.used for.-> F1
```

**Aggregation Classes**:
- `_AggFunc` [erroranalysis/erroranalysis/_internal/matrix_filter.py:545-586](): For simple metrics like error rate, MAE, MSE
- `_MultiMetricAggFunc` [erroranalysis/erroranalysis/_internal/matrix_filter.py:588-676](): For precision/recall/F1 that need confusion matrix components

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:503-676]()

## Matrix Construction

### 1D Matrix

For a single feature, the algorithm:

1. Bins the feature (if continuous) or uses categories
2. Counts total instances per bin
3. Applies metric aggregation to error subset
4. Constructs JSON with intervals and metrics

The output structure for 1D matrices:

| Field | Type | Description |
|-------|------|-------------|
| `category1` | Array | Bin labels (e.g., intervals or category names) |
| `intervalMin` | Array | Minimum value for each interval (continuous only) |
| `intervalMax` | Array | Maximum value for each interval (continuous only) |
| `values` | Array | Metric values for each bin |
| `metricName` | String | Display name of the metric |

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:839-894]()

### 2D Matrix

For two features, the algorithm:

1. Bins both features independently
2. Creates a 2D crosstab of total counts
3. Creates a 2D crosstab of metric values using aggregation function
4. Constructs nested JSON structure

The output structure for 2D matrices:

```mermaid
graph LR
    Root["Matrix Object"]
    
    Cat1["category1[]<br/>Feature 1 bins"]
    Cat2["category2[]<br/>Feature 2 bins"]
    
    Matrix["matrix[]<br/>2D grid"]
    
    Row["Row object<br/>per category1 value"]
    
    Values["values[]<br/>Metric per category2"]
    Count["count[]<br/>Total instances"]
    FalseCount["falseCount[]<br/>Error instances"]
    
    Intervals1["intervalMin/Max<br/>for category1"]
    Intervals2["intervalMin/Max<br/>for category2"]
    
    Root --> Cat1
    Root --> Cat2
    Root --> Matrix
    Root --> Intervals1
    Root --> Intervals2
    
    Matrix --> Row
    Row --> Values
    Row --> Count
    Row --> FalseCount
```

**Key Functions**:
- `matrix_1d()` [erroranalysis/erroranalysis/_internal/matrix_filter.py:839-894](): Constructs 1D matrix JSON
- `matrix_2d()` [erroranalysis/erroranalysis/_internal/matrix_filter.py:678-837](): Constructs 2D matrix JSON

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:678-894]()

## Advanced Features

### Multi-Metric Output

For precision, recall, F1, and accuracy metrics with multi-class classification, the `_MultiMetricAggFunc` computes additional confusion matrix components:

```python
# Return structure from _multi_metric_result():
(metric_value, tp_sum, fp_sum, fn_sum, tn_sum, error)
```

This enables the UI to display:
- The primary metric value
- TP/FP/FN/TN counts for each bin
- Total error count

The confusion matrix is computed using `sklearn.metrics.multilabel_confusion_matrix()` with specified labels.

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:609-676]()

### Object Detection Support

For object detection tasks (`ModelTask.OBJECT_DETECTION`), the matrix filter:

1. Computes error labels using `ErrorLabeling` from `vision_explanation_methods`
2. Treats each image as having error if `len(error_list) > 0`
3. Only supports `ERROR_RATE` metric currently

This is implemented in [erroranalysis/erroranalysis/_internal/matrix_filter.py:129-145]():

```python
if analyzer.model_task == ModelTask.OBJECT_DETECTION:
    diff = [
        len(
            ErrorLabeling(
                ModelTask.OBJECT_DETECTION,
                pred_y[image_idx],
                true_y[image_idx]
            ).compute_error_list()
        ) > 0
        for image_idx in range(len(true_y))
    ]
```

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:129-145]()

### Binning Edge Cases

The implementation handles several edge cases in binning:

1. **Duplicate bin edges**: When quantile binning creates duplicate edges (e.g., many identical values), the algorithm warns the user and removes duplicates
   - See `warn_duplicate_edges()` [erroranalysis/erroranalysis/_internal/matrix_filter.py:404-414]()

2. **Floating-point precision**: When `pd.cut()` creates a max bin edge below the actual max value due to precision, the algorithm adjusts it
   - See `adjust_bin_max_edge()` [erroranalysis/erroranalysis/_internal/matrix_filter.py:481-501]()

3. **Zero-bin tolerance**: For quantile binning, adds tolerance to the leftmost bin to include boundary values
   - See [erroranalysis/erroranalysis/_internal/matrix_filter.py:454-465]()

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:404-501]()

## Integration with Error Analysis Pipeline

The matrix filter integrates with the broader error analysis system:

```mermaid
graph TB
    subgraph "User Interaction"
        Dashboard["Error Analysis Dashboard<br/>UI selects features"]
    end
    
    subgraph "Flask API Layer"
        GetMatrix["/get_matrix<br/>POST endpoint"]
        Input["ResponsibleAIDashboardInput<br/>.get_matrix()"]
    end
    
    subgraph "Analyzer Layer"
        BaseAnalyzer["BaseAnalyzer<br/>.compute_matrix()"]
        FilterCohort["filter_from_cohort()<br/>Apply user filters"]
    end
    
    subgraph "Matrix Filter Core"
        ComputeMatrix["compute_matrix_on_dataset()<br/>Core algorithm"]
        BinData["bin_data()<br/>Binning logic"]
        AggFunc["Aggregation functions<br/>Metric computation"]
        MatrixBuilder["matrix_1d() or matrix_2d()<br/>JSON construction"]
    end
    
    subgraph "Output"
        MatrixJSON["Matrix JSON<br/>Sent to UI"]
    end
    
    Dashboard -->|User selects features| GetMatrix
    GetMatrix --> Input
    Input --> BaseAnalyzer
    BaseAnalyzer --> FilterCohort
    FilterCohort --> ComputeMatrix
    
    ComputeMatrix --> BinData
    ComputeMatrix --> AggFunc
    ComputeMatrix --> MatrixBuilder
    
    MatrixBuilder --> MatrixJSON
    MatrixJSON --> Dashboard
```

Sources: [erroranalysis/erroranalysis/analyzer/error_analyzer.py:251-280](), [erroranalysis/erroranalysis/_internal/matrix_filter.py:58-389]()

## Configuration Parameters

The matrix filter accepts the following configuration:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `features` | list[str] | Required | One or two feature names to analyze |
| `filters` | list[dict] | `None` | Simple filters to apply before computing matrix |
| `composite_filters` | list[dict] | `None` | Nested filters with AND/OR operations |
| `quantile_binning` | bool | `False` | Use quantile binning instead of equal-width |
| `num_bins` | int | `8` | Number of bins for continuous features |

**Constants**: 
- `MatrixParams.BIN_THRESHOLD = 8` [erroranalysis/erroranalysis/_internal/constants.py:74-77]()
- `PRECISION = 100` for bin interval formatting [erroranalysis/erroranalysis/_internal/matrix_filter.py:48]()

Sources: [erroranalysis/erroranalysis/_internal/matrix_filter.py:58-389](), [erroranalysis/erroranalysis/_internal/constants.py:74-77]()

## Test Coverage

The matrix filter has comprehensive test coverage in [erroranalysis/tests/test_matrix_filter.py]():

| Test Category | Examples |
|---------------|----------|
| Basic functionality | `test_matrix_filter_iris`, `test_matrix_filter_cancer` |
| Filtering integration | `test_matrix_filter_iris_filters`, `test_matrix_filter_cancer_filters` |
| Quantile binning | `test_matrix_filter_iris_quantile_binning`, `test_matrix_filter_diabetes_quantile_binning` |
| Multiple metrics | `test_matrix_filter_wine_quantile_binning` with parametrized metrics |
| Edge cases | `test_bin_data_max_over_left_bound`, `test_matrix_filter_iris_invalid_num_bins` |
| Categorical features | `test_matrix_filter_titanic`, `test_matrix_filter_adult_census_quantile_binning` |
| Data types | `test_matrix_filter_iris_int64`, `test_matrix_filter_titanic_object_dtype_quantile` |

Sources: [erroranalysis/tests/test_matrix_filter.py:1-578]()

---

