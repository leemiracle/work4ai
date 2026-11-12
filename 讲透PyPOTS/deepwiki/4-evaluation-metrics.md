<!-- source: DeepWiki mcp.deepwiki.com · repo WenjieDu/PyPOTS · page 4 Evaluation & Metrics · fetched 2026-10-21 -->

# Evaluation & Metrics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pypots/nn/functional/__init__.py](pypots/nn/functional/__init__.py)
- [pypots/nn/functional/error.py](pypots/nn/functional/error.py)
- [pypots/nn/functional/gathering.py](pypots/nn/functional/gathering.py)
- [pypots/nn/functional/normalization.py](pypots/nn/functional/normalization.py)
- [pypots/nn/modules/loss.py](pypots/nn/modules/loss.py)
- [pypots/nn/modules/metric.py](pypots/nn/modules/metric.py)
- [pypots/utils/metrics/__init__.py](pypots/utils/metrics/__init__.py)
- [pypots/utils/metrics/classification.py](pypots/utils/metrics/classification.py)
- [pypots/utils/metrics/clustering.py](pypots/utils/metrics/clustering.py)
- [pypots/utils/metrics/error.py](pypots/utils/metrics/error.py)

</details>



The PyPOTS evaluation framework provides a unified interface for calculating loss functions during training and performance metrics during validation and testing. The framework is designed with a dual-backend approach, supporting both **NumPy** for post-hoc evaluation and **PyTorch** for differentiable loss calculation within neural network modules.

## The Criterion Hierarchy

At the core of the evaluation system is the `Criterion` class, which extends PyTorch's `_Loss` [pypots/nn/modules/loss.py:17-34](). This base class introduces the `lower_better` attribute, allowing the system to understand whether a higher or lower value indicates superior model performance—a critical feature for automated model selection and hyperparameter optimization [pypots/nn/modules/loss.py:20-33]().

### Loss Functions vs. Performance Metrics

While both inherit from `Criterion`, PyPOTS distinguishes between them based on their typical use case:
*   **Loss Functions**: Implemented in `pypots.nn.modules.loss`, these are primarily used as optimization objectives (e.g., `MSE`, `MAE`, `RMSE`, `MRE`, `CrossEntropy`, `NLL`) [pypots/nn/modules/loss.py:54-134]().
*   **Performance Metrics**: Implemented in `pypots.nn.modules.metric`, these often involve non-differentiable operations or require CPU-side calculation (e.g., `Accuracy`, `PR_AUC`, `ROC_AUC`) [pypots/nn/modules/metric.py:17-67](). These classes typically perform a `torch.softmax` on logits and move data to the CPU via `.cpu().numpy()` before calling functional calculation utilities [pypots/nn/modules/metric.py:28-31](), [pypots/nn/modules/metric.py:47-48](), [pypots/nn/modules/metric.py:62-63]().

### Code Entity Map: Criterion System

```mermaid
graph TD
    subgraph "Base_Infrastructure"
        [torch.nn.modules.loss._Loss] --> [pypots.nn.modules.loss.Criterion]
        [pypots.nn.modules.loss.Criterion] -- "attr:lower_better" --> [Losses_&_Metrics]
    end

    subgraph "pypots.nn.modules.loss"
        [Losses_&_Metrics] --> [MSE]
        [Losses_&_Metrics] --> [MAE]
        [Losses_&_Metrics] --> [RMSE]
        [Losses_&_Metrics] --> [MRE]
        [Losses_&_Metrics] --> [CrossEntropy]
        [Losses_&_Metrics] --> [NLL]
    end

    subgraph "pypots.nn.modules.metric"
        [Losses_&_Metrics] --> [Accuracy]
        [Losses_&_Metrics] --> [PR_AUC]
        [Losses_&_Metrics] --> [ROC_AUC]
    end

    subgraph "pypots.nn.functional"
        [MSE] -. "calls" .-> [calc_mse]
        [Accuracy] -. "calls" .-> [calc_acc]
        [PR_AUC] -. "calls" .-> [calc_pr_auc]
        [ROC_AUC] -. "calls" .-> [calc_roc_auc]
    end
```
**Sources:** [pypots/nn/modules/loss.py:17-134](), [pypots/nn/modules/metric.py:17-67](), [pypots/nn/functional/error.py:106-155]()

---

## Dual-Backend Design

PyPOTS metrics are implemented to be backend-agnostic where possible. The internal `_check_inputs` utility [pypots/nn/functional/error.py:14-52]() automatically detects whether the inputs are NumPy arrays or PyTorch tensors and selects the appropriate library (`np` or `torch`) for computation [pypots/nn/functional/error.py:25]().

This design ensures that:
1.  **Training Efficiency**: Metrics can run on GPUs as PyTorch tensors during the training loop.
2.  **Flexible Evaluation**: Users can evaluate pre-computed NumPy results without needing to maintain a PyTorch environment or move data back to tensors.
3.  **Numerical Stability**: Imputation and regression metrics include a `1e-12` epsilon in denominators to prevent division-by-zero errors when masks are sparse [pypots/nn/functional/error.py:101-152]().

### Migration Note
The package `pypots.utils.metrics` is deprecated [pypots/utils/metrics/__init__.py:34](). All evaluation logic has been consolidated into `pypots.nn.functional` to provide a more consistent API for both functional calls and module-based criteria. Legacy imports in `pypots.utils.metrics` now trigger warnings and redirect to the functional implementations in `pypots.nn.functional.error`, `pypots.nn.functional.classification`, and `pypots.nn.functional.clustering` [pypots/utils/metrics/error.py:18-19](), [pypots/utils/metrics/classification.py:17-20](), [pypots/utils/metrics/clustering.py:21-22]().

---

## Metric Categories

Evaluation in PyPOTS is divided into three primary domains, each detailed in its own sub-page.

### Error & Regression Metrics
Used primarily for **Imputation** and **Forecasting** tasks. These metrics support boolean masking to evaluate models only on specific values (e.g. the "Observed-but-not-Input" strategy) [pypots/nn/functional/error.py:61-74]().
*   **Key Metrics**: `calc_mae`, `calc_mse`, `calc_rmse`, `calc_mre`, and `calc_quantile_crps` (Continuous Ranked Probability Score) for probabilistic/distributional evaluation [pypots/nn/functional/error.py:55-161](), [pypots/utils/metrics/error.py:21-28]().
*   For details, see [Error & Regression Metrics](#4.1).

### Classification & Clustering Metrics
Used for evaluating discrete label assignments and grouping performance.
*   **Classification**: Includes `calc_acc`, `calc_precision_recall_f1`, `calc_pr_auc`, and `calc_roc_auc` [pypots/utils/metrics/classification.py:22-28](). Classification metrics often involve a `torch.softmax` transformation of model logits before calculation in the `pypots.nn.modules.metric` wrappers [pypots/nn/modules/metric.py:28-62]().
*   **Clustering**: Includes both external validation (`calc_rand_index`, `calc_adjusted_rand_index`, `calc_nmi`, `calc_cluster_purity`) and internal validation (`calc_silhouette`, `calc_chs`, `calc_dbs`) [pypots/utils/metrics/clustering.py:24-34]().
*   For details, see [Classification & Clustering Metrics](#4.2).

### Visualization Utilities
Beyond scalar numbers, PyPOTS provides visual diagnostics to inspect model behavior via `pypots.utils.visual`.
*   **Imputation**: Overlaying observed, ground-truth, and imputed sequences to diagnose reconstruction quality.
*   **Clustering**: Visualizing cluster means with 95% confidence intervals and member distributions.
*   For details, see [Visualization Utilities](#4.3).

### Code Entity Map: Functional API

```mermaid
graph LR
    subgraph "User_Entry_Point"
        [pypots.nn.functional]
    end

    subgraph "pypots.nn.functional.error"
        [pypots.nn.functional] --> [calc_mae]
        [pypots.nn.functional] --> [calc_mse]
        [pypots.nn.functional] --> [calc_quantile_crps]
    end

    subgraph "pypots.nn.functional.classification"
        [pypots.nn.functional] --> [calc_acc]
        [pypots.nn.functional] --> [calc_roc_auc]
        [pypots.nn.functional] --> [calc_precision_recall_f1]
    end

    subgraph "pypots.nn.functional.clustering"
        [pypots.nn.functional] --> [calc_nmi]
        [pypots.nn.functional] --> [calc_rand_index]
        [pypots.nn.functional] --> [calc_internal_cluster_validation_metrics]
    end

    [calc_mae] --- [INPUTS_ERR]
    [calc_acc] --- [INPUTS_CLS]
    
    [INPUTS_ERR] -- "(predictions, targets, masks)" --> [Data]
    [INPUTS_CLS] -- "(predictions, targets)" --> [Data]
```
**Sources:** [pypots/nn/functional/error.py:55-161](), [pypots/utils/metrics/classification.py:9-28](), [pypots/utils/metrics/clustering.py:9-34](), [pypots/utils/metrics/__init__.py:36-60]()

---

