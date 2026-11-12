> 来源: [https://deepwiki.com/catalyst-team/catalyst/6-metrics-system](https://deepwiki.com/catalyst-team/catalyst/6-metrics-system)
> DeepWiki catalyst-team/catalyst | Last indexed: 21 April 2025 (e99f90

# Metrics System

  Relevant source files 
 - [catalyst/callbacks/metrics/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/__init__.py)
 - [catalyst/callbacks/metrics/accuracy.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/accuracy.py)
 - [catalyst/callbacks/metrics/cmc_score.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/cmc_score.py)
 - [catalyst/callbacks/metrics/recsys.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/recsys.py)
 - [catalyst/callbacks/mixup.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/mixup.py)
 - [catalyst/callbacks/sklearn_model.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/sklearn_model.py)
 - [catalyst/metrics/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/__init__.py)
 - [catalyst/metrics/_functional_metric.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/_functional_metric.py)
 - [catalyst/metrics/_r2_squared.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/_r2_squared.py)
 - [catalyst/metrics/functional/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/functional/__init__.py)
 - [catalyst/metrics/functional/_r2_squared.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/functional/_r2_squared.py)
 - [docs/api/callbacks.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/callbacks.rst)
 - [docs/api/metrics.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/metrics.rst)
 - [docs/api/utils.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/utils.rst)
 - [tests/catalyst/metrics/functional/test_r2_squared.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/tests/catalyst/metrics/functional/test_r2_squared.py)
 - [tests/catalyst/metrics/test_r2squared.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/tests/catalyst/metrics/test_r2squared.py)
 - [tests/pipelines/test_contrastive.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/tests/pipelines/test_contrastive.py)
 
  The Metrics System in Catalyst provides a structured approach for evaluating and tracking model performance during training, validation, and testing. This document explains the architecture, components, and usage of the metrics framework, including both built-in metrics and guidelines for creating custom ones.

 For metric integration with other systems, see [Callback System](https://deepwiki.com/catalyst-team/catalyst/3-callback-system) and [Logger System](https://deepwiki.com/catalyst-team/catalyst/7-logger-system).

 
## Overview

 The Metrics System is a core component of the Catalyst framework that enables the computation and tracking of performance metrics. It provides both functional implementations (pure functions) and object-oriented implementations (classes) of commonly used metrics, along with a standardized interface for creating custom metrics.

 
```

```

 Sources: [catalyst/metrics/__init__.py7-41](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/__init__.py#L7-L41) [catalyst/metrics/functional/__init__.py2-42](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/functional/__init__.py#L2-L42) [docs/api/metrics.rst16-206](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/metrics.rst#L16-L206)

 
## Metric Interfaces and Base Classes

 The Catalyst Metrics System is built around several core interfaces and base classes that provide a standardized way to define and use metrics.

 
### Core Interfaces

 
 - **IMetric**: The base interface for all metrics, providing common functionality.
 - **ICallbackBatchMetric**: Interface for metrics computed on each batch.
 - **ICallbackLoaderMetric**: Interface for metrics accumulated over an entire data loader.
 
 
### Base Classes

 
 - **AccumulativeMetric**: Base class for metrics that accumulate values over batches.
 - **AdditiveMetric**: Base class for metrics that can be added together.
 - **ConfusionMatrixMetric**: Base class for metrics based on confusion matrices.
 - **TopKMetric**: Base class for metrics computed at different K values (e.g., top-1, top-5 accuracy).
 - **FunctionalBatchMetric**: Wrapper for using functional metrics on a per-batch basis.
 - **FunctionalLoaderMetric**: Wrapper for using functional metrics on a per-loader basis.
 
 
```

```

 Sources: [docs/api/metrics.rst16-83](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/metrics.rst#L16-L83) [catalyst/metrics/_functional_metric.py1-233](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/_functional_metric.py#L1-L233)

 
## Types of Metrics

 The Metrics System supports two fundamental types of metrics, depending on when and how they're computed:

 
### Batch Metrics

 Batch metrics are computed on individual batches of data. They're useful for getting immediate feedback during training and can be logged at each step. These metrics are typically faster to compute but might be less stable.

 Example batch metrics include accuracy, precision, recall, and F1 score.

 
### Loader Metrics

 Loader metrics are accumulated over all batches in a data loader. They provide a more stable assessment of model performance but are only available after processing the entire dataset.

 Example loader metrics include CMC (Cumulative Matching Characteristics) scores and metrics that require processing the entire dataset at once.

 
### Functional vs Object-Oriented Metrics

 Catalyst provides both functional and object-oriented implementations of metrics:

 
 - **Functional metrics** are pure functions that compute a metric value from inputs and targets, e.g., `accuracy(outputs, targets)`.
 - **Object-oriented metrics** are classes that implement the IMetric interface, maintaining state and allowing for accumulation across batches.
 
 
```

```

 Sources: [catalyst/metrics/_functional_metric.py13-231](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/_functional_metric.py#L13-L231) [docs/api/metrics.rst40-83](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/metrics.rst#L40-L83)

 
## Metric Callbacks

 Metric callbacks are the bridge between the Runner system and the Metrics system. They use metric implementations to compute and log values during training.

 
### Base Metric Callbacks

 
 - **BatchMetricCallback**: Base class for callbacks that use ICallbackBatchMetric implementations.
 - **LoaderMetricCallback**: Base class for callbacks that use ICallbackLoaderMetric implementations.
 
 
### Metric-specific Callbacks

 Catalyst provides callbacks for all built-in metrics:

 
| Callback | Metric Type | Purpose |
|---|---|---|
| AccuracyCallback | Batch | Calculate accuracy@K |
| AUCCallback | Loader | Calculate Area Under the ROC Curve |
| PrecisionRecallF1SupportCallback | Batch | Calculate precision, recall, F1 score |
| CMCScoreCallback | Loader | Calculate Cumulative Matching Characteristics |
| R2SquaredCallback | Loader | Calculate R-squared for regression |
| HitrateCallback | Batch | Calculate Hitrate@K for recommendations |
| MAPCallback | Batch | Calculate Mean Average Precision |
| MRRCallback | Batch | Calculate Mean Reciprocal Rank |
| NDCGCallback | Batch | Calculate Normalized Discounted Cumulative Gain |
| IOUCallback, DiceCallback | Batch | Calculate segmentation metrics |

 
```

```

 Sources: [docs/api/callbacks.rst144-306](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/callbacks.rst#L144-L306) [catalyst/callbacks/metrics/accuracy.py1-206](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/accuracy.py#L1-L206) [catalyst/callbacks/metrics/recsys.py1-453](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/recsys.py#L1-L453) [catalyst/callbacks/metrics/cmc_score.py1-235](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/cmc_score.py#L1-L235)

 
## Built-in Metrics

 Catalyst provides a wide range of built-in metrics for different tasks.

 
### Classification Metrics

 
 - **Accuracy**: Accuracy@K for multiclass classification
 - **MultilabelAccuracy**: Accuracy for multilabel classification
 - **AUC**: Area Under the ROC Curve
 - **Precision/Recall/F1**: Both binary and multiclass versions
 - **ConfusionMatrix**: Confusion matrix and derived metrics
 
 
### Regression Metrics

 
 - **R2Squared**: Coefficient of determination for regression tasks
 
 Example usage of R2Squared metric:

 
```

```

 
### Segmentation Metrics

 
 - **IOU (Intersection over Union)**: For semantic segmentation
 - **Dice Coefficient**: For semantic segmentation
 - **Trevsky Index**: Generalization of Dice coefficient
 
 
### Recommendation System Metrics

 
 - **Hitrate**: Hit rate@K for recommendation systems
 - **MAP**: Mean Average Precision
 - **MRR**: Mean Reciprocal Rank
 - **NDCG**: Normalized Discounted Cumulative Gain
 
 
### Other Metrics

 
 - **CMCScore**: Cumulative Matching Characteristics for person re-identification
 - **ReidCMCScore**: CMC Score considering camera IDs
 
 Sources: [catalyst/metrics/__init__.py23-41](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/__init__.py#L23-L41) [docs/api/metrics.rst85-205](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/metrics.rst#L85-L205) [catalyst/metrics/_r2_squared.py1-67](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/_r2_squared.py#L1-L67) [catalyst/callbacks/metrics/recsys.py10-450](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/recsys.py#L10-L450)

 
## Creating Custom Metrics

 Catalyst provides several ways to create custom metrics, depending on the complexity and requirements.

 
### Using Functional Wrappers

 For simple cases, you can create a function and wrap it with `FunctionalBatchMetric` or `FunctionalLoaderMetric`:

 
```

```

 
### Implementing IMetric Interfaces

 For more complex metrics, you can implement one of the metric interfaces:

 
```

```

 
### Using scikit-learn Metrics

 Catalyst provides specific support for scikit-learn metrics through:

 
 - **SklearnBatchCallback**: For batch-based scikit-learn metrics
 - **SklearnLoaderCallback**: For loader-based scikit-learn metrics
 - **SklearnModelCallback**: For training a scikit-learn model during training
 
 
```

```

 Sources: [catalyst/metrics/_functional_metric.py13-231](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/metrics/_functional_metric.py#L13-L231) [catalyst/callbacks/sklearn_model.py1-145](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/sklearn_model.py#L1-L145)

 
## Integration with Runner and Logger

 Metrics are deeply integrated with both the Runner and Logger systems in Catalyst.

 
### Runner Integration

 The Runner calls metric callbacks at specific points in the training loop, which update and compute metrics. These metric values are stored in:

 
 - `runner.batch_metrics`: Metrics computed on the current batch
 - `runner.loader_metrics`: Metrics accumulated over the current loader
 - `runner.epoch_metrics`: Metrics accumulated over the entire epoch
 
 Metrics can be used for monitoring and early stopping through the `valid_metric` and `minimize_valid_metric` parameters in the `runner.train()` method.

 
### Logger Integration

 Computed metrics can be logged to various backend systems through the Logger system:

 
 - **TensorBoard**: Visualize metrics as curves
 - **WandB**: Log metrics to Weights & Biases
 - **MLflow**: Track metrics in MLflow experiments
 - **Neptune**: Log metrics to Neptune.ai
 - **CSV**: Save metrics to CSV files
 
 
```

```

 Sources: [catalyst/callbacks/metrics/accuracy.py93-115](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/accuracy.py#L93-L115) [catalyst/callbacks/metrics/cmc_score.py142-169](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/cmc_score.py#L142-L169)

 
## Best Practices and Usage Guidelines

 When using the Metrics System in Catalyst, consider the following best practices:

 
 - **Choose the right metric type**:

 
 - Use batch metrics for immediate feedback during training
 - Use loader metrics for more stable evaluation, especially with small batches
 - **Prefix and suffix**:

 
 - Use metric prefixes and suffixes to organize metrics when you have multiple metrics of the same type
 - **TopK metrics**:

 
 - For metrics like accuracy, hitrate, and MRR, use the `topk` parameter to compute metrics at different K values simultaneously
 - **Performance considerations**:

 
 - Batch metrics are computed on every batch, which can slow down training for complex metrics
 - Consider using `log_on_batch=False` for complex metrics to only compute them at the end of each loader
 - **Integration with callbacks**:

 
 - Use `ControlFlowCallback` to apply different metrics to different loaders
 - Use `MetricAggregationCallback` to compute new metrics from existing ones
 
 Sources: [catalyst/callbacks/metrics/accuracy.py76-91](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/accuracy.py#L76-L91) [catalyst/callbacks/metrics/recsys.py86-96](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/recsys.py#L86-L96) [catalyst/callbacks/metrics/cmc_score.py135-143](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/callbacks/metrics/cmc_score.py#L135-L143)

 
## Conclusion

 The Metrics System in Catalyst provides a flexible and extensible framework for evaluating model performance. With a wide range of built-in metrics and options for creating custom ones, it can handle most machine learning tasks while maintaining a clean and consistent API.

 By understanding the difference between batch and loader metrics, functional and object-oriented implementations, and how to integrate metrics with callbacks, you can effectively track and optimize your model's performance during training.
