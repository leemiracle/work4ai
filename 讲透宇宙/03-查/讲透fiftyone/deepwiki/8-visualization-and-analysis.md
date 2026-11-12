<!-- source: DeepWiki mcp.deepwiki.com · repo voxel51/fiftyone · page 8 Visualization and Analysis · fetched 2026-10-21 -->

# Analysis and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [fiftyone/__public__.py](fiftyone/__public__.py)
- [fiftyone/core/aggregations.py](fiftyone/core/aggregations.py)
- [fiftyone/core/clips.py](fiftyone/core/clips.py)
- [fiftyone/core/collections.py](fiftyone/core/collections.py)
- [fiftyone/core/dataset.py](fiftyone/core/dataset.py)
- [fiftyone/core/document.py](fiftyone/core/document.py)
- [fiftyone/core/expressions.py](fiftyone/core/expressions.py)
- [fiftyone/core/fields.py](fiftyone/core/fields.py)
- [fiftyone/core/frame.py](fiftyone/core/frame.py)
- [fiftyone/core/labels.py](fiftyone/core/labels.py)
- [fiftyone/core/odm/dataset.py](fiftyone/core/odm/dataset.py)
- [fiftyone/core/odm/document.py](fiftyone/core/odm/document.py)
- [fiftyone/core/odm/embedded_document.py](fiftyone/core/odm/embedded_document.py)
- [fiftyone/core/odm/mixins.py](fiftyone/core/odm/mixins.py)
- [fiftyone/core/odm/sample.py](fiftyone/core/odm/sample.py)
- [fiftyone/core/odm/utils.py](fiftyone/core/odm/utils.py)
- [fiftyone/core/patches.py](fiftyone/core/patches.py)
- [fiftyone/core/plots/__init__.py](fiftyone/core/plots/__init__.py)
- [fiftyone/core/plots/base.py](fiftyone/core/plots/base.py)
- [fiftyone/core/plots/manager.py](fiftyone/core/plots/manager.py)
- [fiftyone/core/plots/matplotlib.py](fiftyone/core/plots/matplotlib.py)
- [fiftyone/core/plots/plotly.py](fiftyone/core/plots/plotly.py)
- [fiftyone/core/plots/utils.py](fiftyone/core/plots/utils.py)
- [fiftyone/core/plots/views.py](fiftyone/core/plots/views.py)
- [fiftyone/core/sample.py](fiftyone/core/sample.py)
- [fiftyone/core/stages.py](fiftyone/core/stages.py)
- [fiftyone/core/video.py](fiftyone/core/video.py)
- [fiftyone/core/view.py](fiftyone/core/view.py)
- [tests/unittests/aggregation_tests.py](tests/unittests/aggregation_tests.py)
- [tests/unittests/dataset_tests.py](tests/unittests/dataset_tests.py)
- [tests/unittests/odm_tests.py](tests/unittests/odm_tests.py)
- [tests/unittests/patches_tests.py](tests/unittests/patches_tests.py)
- [tests/unittests/video_tests.py](tests/unittests/video_tests.py)
- [tests/unittests/view_tests.py](tests/unittests/view_tests.py)

</details>



The Analysis and Evaluation system in FiftyOne provides comprehensive tools for evaluating machine learning models and analyzing dataset quality. This system includes evaluation methods for classification, detection, segmentation, and regression tasks, along with visualization capabilities and run management infrastructure.

For information about data processing and format conversion, see [Data Processing](#5). For model integration and application workflows, see [Model Integration](#6).

## Evaluation Framework Architecture

The evaluation system is built on a hierarchical framework that provides consistent interfaces across different evaluation types while allowing specialized implementations for specific tasks.

### Core Evaluation Architecture

```mermaid
graph TD
    BaseEvaluationMethodConfig["BaseEvaluationMethodConfig"] --> ClassificationEvaluationConfig["ClassificationEvaluationConfig"]
    BaseEvaluationMethodConfig --> DetectionEvaluationConfig["DetectionEvaluationConfig"] 
    BaseEvaluationMethodConfig --> SegmentationEvaluationConfig["SegmentationEvaluationConfig"]
    BaseEvaluationMethodConfig --> RegressionEvaluationConfig["RegressionEvaluationConfig"]
    
    BaseEvaluationMethod["BaseEvaluationMethod"] --> ClassificationEvaluation["ClassificationEvaluation"]
    BaseEvaluationMethod --> DetectionEvaluation["DetectionEvaluation"]
    BaseEvaluationMethod --> SegmentationEvaluation["SegmentationEvaluation"]
    BaseEvaluationMethod --> RegressionEvaluation["RegressionEvaluation"]
    
    DetectionEvaluation --> COCOEvaluation["COCOEvaluation"]
    DetectionEvaluation --> OpenImagesEvaluation["OpenImagesEvaluation"]
    DetectionEvaluation --> ActivityNetEvaluation["ActivityNetEvaluation"]
    
    BaseEvaluationResults["BaseEvaluationResults"] --> ClassificationResults["ClassificationResults"]
    BaseEvaluationResults --> DetectionResults["DetectionResults"]
    BaseEvaluationResults --> SegmentationResults["SegmentationResults"]
    BaseEvaluationResults --> RegressionResults["RegressionResults"]
    
    DetectionResults --> COCODetectionResults["COCODetectionResults"]
```

Sources: [fiftyone/utils/eval/base.py:188-252](), [fiftyone/utils/eval/classification.py:136-159](), [fiftyone/utils/eval/detection.py:244-293](), [fiftyone/utils/eval/coco.py:30-120]()

### Run Management System

```mermaid
graph TD
    BaseRunConfig["BaseRunConfig"] --> BaseRun["BaseRun"]
    BaseRun --> register_run["register_run()"]
    BaseRun --> validate_run["validate_run()"]
    BaseRun --> cleanup["cleanup()"]
    
    BaseRunInfo["BaseRunInfo"] --> RunDocument["RunDocument"]
    RunDocument --> MongoDB[("MongoDB")]
    
    Dataset["Dataset"] --> runs_field["evaluation_runs"]
    runs_field --> RunDocument
    
    Session["Session"] --> plots["plots"]
    plots --> PlotManager["PlotManager"]
    PlotManager --> ResponsivePlot["ResponsivePlot"]
```

Sources: [fiftyone/core/runs.py:205-323](), [fiftyone/core/odm/runs.py:21-34](), [fiftyone/core/plots/manager.py:27-77]()

## Evaluation Types and Methods

### Classification Evaluation

The classification evaluation system supports standard accuracy-based evaluation, top-k evaluation, and binary classification scenarios.

```mermaid
graph TD
    evaluate_classifications["evaluate_classifications()"] --> ClassificationEvaluationConfig["ClassificationEvaluationConfig"]
    ClassificationEvaluationConfig --> SimpleEvaluationConfig["SimpleEvaluationConfig"]
    ClassificationEvaluationConfig --> TopKEvaluationConfig["TopKEvaluationConfig"]
    ClassificationEvaluationConfig --> BinaryEvaluationConfig["BinaryEvaluationConfig"]
    
    SimpleEvaluationConfig --> SimpleEvaluation["SimpleEvaluation"]
    TopKEvaluationConfig --> TopKEvaluation["TopKEvaluation"]
    BinaryEvaluationConfig --> BinaryEvaluation["BinaryEvaluation"]
    
    SimpleEvaluation --> ClassificationResults["ClassificationResults"]
    TopKEvaluation --> ClassificationResults
    BinaryEvaluation --> BinaryClassificationResults["BinaryClassificationResults"]
    
    ClassificationResults --> confusion_matrix["confusion_matrix()"]
    ClassificationResults --> report["report()"]
    BinaryClassificationResults --> plot_roc_curve["plot_roc_curve()"]
    BinaryClassificationResults --> plot_pr_curve["plot_pr_curve()"]
```

Sources: [fiftyone/utils/eval/classification.py:33-134](), [fiftyone/utils/eval/classification.py:261-367](), [fiftyone/utils/eval/classification.py:575-724]()

### Detection Evaluation

Detection evaluation includes multiple specialized methods for different evaluation protocols, with COCO-style evaluation being the most comprehensive.

```mermaid
graph TD
    evaluate_detections["evaluate_detections()"] --> DetectionEvaluationConfig["DetectionEvaluationConfig"]
    DetectionEvaluationConfig --> COCOEvaluationConfig["COCOEvaluationConfig"]
    DetectionEvaluationConfig --> OpenImagesEvaluationConfig["OpenImagesEvaluationConfig"]
    DetectionEvaluationConfig --> ActivityNetEvaluationConfig["ActivityNetEvaluationConfig"]
    
    COCOEvaluationConfig --> COCOEvaluation["COCOEvaluation"]
    OpenImagesEvaluationConfig --> OpenImagesEvaluation["OpenImagesEvaluation"]
    ActivityNetEvaluationConfig --> ActivityNetEvaluation["ActivityNetEvaluation"]
    
    COCOEvaluation --> COCODetectionResults["COCODetectionResults"]
    OpenImagesEvaluation --> DetectionResults["DetectionResults"]
    ActivityNetEvaluation --> DetectionResults
    
    COCODetectionResults --> mAP["mAP()"]
    COCODetectionResults --> mAR["mAR()"]
    COCODetectionResults --> plot_pr_curves["plot_pr_curves()"]
    
    compute_ious["compute_ious()"] --> DetectionEvaluation["DetectionEvaluation"]
    compute_ious --> use_masks["use_masks"]
    compute_ious --> use_boxes["use_boxes"]
```

Sources: [fiftyone/utils/eval/detection.py:33-242](), [fiftyone/utils/eval/coco.py:121-250](), [fiftyone/utils/eval/openimages.py:24-142](), [fiftyone/utils/iou.py:30-157]()

### IoU Computation Framework

```mermaid
graph TD
    compute_ious["compute_ious()"] --> Detection["Detection"]
    compute_ious --> Polyline["Polyline"]
    compute_ious --> Keypoint["Keypoint"]
    
    Detection --> compute_bbox_ious["_compute_bbox_ious()"]
    Detection --> compute_mask_ious["_compute_mask_ious()"]
    
    Polyline --> compute_polygon_ious["_compute_polygon_ious()"]
    Polyline --> compute_polyline_similarities["_compute_polyline_similarities()"]
    
    Keypoint --> compute_keypoint_similarities["_compute_keypoint_similarities()"]
    
    compute_ious --> sparse["sparse=True/False"]
    compute_ious --> classwise["classwise=True/False"]
    compute_ious --> iscrowd["iscrowd handling"]
```

Sources: [fiftyone/utils/iou.py:30-157](), [fiftyone/utils/iou.py:479-530](), [fiftyone/utils/iou.py:159-183]()

## Visualization and Plotting

### Plot Types and Hierarchy

```mermaid
graph TD
    Plot["Plot"] --> ResponsivePlot["ResponsivePlot"]
    ResponsivePlot --> InteractivePlot["InteractivePlot"]
    ResponsivePlot --> ViewPlot["ViewPlot"]
    
    InteractivePlot --> InteractiveHeatmap["InteractiveHeatmap"]
    InteractivePlot --> InteractiveScatter["InteractiveScatter"]
    
    plot_confusion_matrix["plot_confusion_matrix()"] --> InteractiveHeatmap
    plot_regressions["plot_regressions()"] --> InteractiveScatter
    plot_pr_curves["plot_pr_curves()"] --> PlotlyNotebookPlot["PlotlyNotebookPlot"]
    plot_roc_curve["plot_roc_curve()"] --> PlotlyNotebookPlot
    
    PlotManager["PlotManager"] --> Session["Session"]
    Session --> view["session.view"]
    PlotManager --> link_type["link_type: samples/frames/labels/view"]
```

Sources: [fiftyone/core/plots/base.py:19-84](), [fiftyone/core/plots/plotly.py:47-123](), [fiftyone/core/plots/manager.py:27-77]()

### Evaluation Results Visualization

| Plot Type | Function | Purpose | Interactive |
|-----------|----------|---------|-------------|
| Confusion Matrix | `plot_confusion_matrix()` | Classification accuracy visualization | Yes (cell selection) |
| PR Curves | `plot_pr_curves()` | Precision-recall analysis | No |
| ROC Curve | `plot_roc_curve()` | Binary classification performance | No |
| Regression Plot | `plot_regressions()` | Regression predictions vs ground truth | Yes (point selection) |

Sources: [fiftyone/core/plots/base.py:19-84](), [fiftyone/core/plots/plotly.py:427-516](), [fiftyone/core/plots/plotly.py:617-703]()

## Metrics and Computation

### COCO Evaluation Metrics

The COCO evaluation system provides comprehensive detection evaluation with mAP computation across multiple IoU thresholds.

```mermaid
graph TD
    COCOEvaluation["COCOEvaluation"] --> evaluate["evaluate()"]
    COCOEvaluation --> generate_results["generate_results()"]
    
    evaluate --> coco_evaluation_single_iou["_coco_evaluation_single_iou()"]
    generate_results --> compute_pr_curves["_compute_pr_curves()"]
    
    compute_pr_curves --> precision["precision[num_iou x num_classes x num_recall]"]
    compute_pr_curves --> recall["recall[num_recall]"]
    compute_pr_curves --> iou_threshs["iou_threshs"]
    
    COCODetectionResults["COCODetectionResults"] --> mAP["mAP()"]
    COCODetectionResults --> mAR["mAR()"]
    COCODetectionResults --> plot_pr_curves_method["plot_pr_curves()"]
    
    mAP --> classwise_AP["_classwise_AP"]
    mAR --> classwise_AR["_classwise_AR"]
```

Sources: [fiftyone/utils/eval/coco.py:121-250](), [fiftyone/utils/eval/coco.py:253-480](), [fiftyone/utils/eval/coco.py:710-835]()

### Custom Metrics Framework

The evaluation system supports custom metrics through an operator-based framework that integrates with the broader FiftyOne operator system.

```mermaid
graph TD
    BaseEvaluationMethod["BaseEvaluationMethod"] --> compute_custom_metrics["compute_custom_metrics()"]
    compute_custom_metrics --> get_custom_metrics["_get_custom_metrics()"]
    
    custom_metrics_config["config.custom_metrics"] --> metric_uris["metric URIs"]
    metric_uris --> get_operator["foo.get_operator()"]
    get_operator --> operator_compute["operator.compute()"]
    
    operator_compute --> custom_metric_value["metric value"]
    custom_metric_value --> results_custom_metrics["results.custom_metrics"]
    
    results_custom_metrics --> aggregate_key["aggregate_key"]
    results_custom_metrics --> label["label"]
    results_custom_metrics --> lower_is_better["lower_is_better"]
```

Sources: [fiftyone/utils/eval/base.py:224-277](), [fiftyone/utils/eval/base.py:208-222]()

## Integration with Dataset Management

### Evaluation Run Storage

```mermaid
graph TD
    Dataset["Dataset"] --> evaluation_runs["evaluation_runs"]
    evaluation_runs --> RunDocument["RunDocument"]
    
    RunDocument --> dataset_id["dataset_id"]
    RunDocument --> key["key"]
    RunDocument --> version["version"]
    RunDocument --> timestamp["timestamp"]
    RunDocument --> config["config"]
    RunDocument --> view_stages["view_stages"]
    RunDocument --> results["results (FileField)"]
    
    BaseRun["BaseRun"] --> register_run["register_run()"]
    register_run --> save_run_info["save_run_info()"]
    save_run_info --> RunDocument
    
    Dataset --> get_evaluation_info["get_evaluation_info()"]
    Dataset --> list_evaluations["list_evaluations()"]
    Dataset --> delete_evaluation["delete_evaluation()"]
```

Sources: [fiftyone/core/runs.py:299-323](), [fiftyone/core/runs.py:555-608](), [fiftyone/core/odm/runs.py:21-34]()

### Field Management and Schema Updates

The evaluation system automatically manages dataset schema updates when evaluation runs are registered, adding necessary fields for storing evaluation results.

```mermaid
graph TD
    register_samples["register_samples()"] --> is_frame_field["samples._is_frame_field()"]
    is_frame_field --> add_sample_field["dataset.add_sample_field()"]
    is_frame_field --> add_frame_field["dataset.add_frame_field()"]
    
    add_sample_field --> eval_key_field["eval_key"]
    add_sample_field --> tp_field["eval_key_tp"]
    add_sample_field --> fp_field["eval_key_fp"]
    add_sample_field --> fn_field["eval_key_fn"]
    
    DetectionEvaluation["DetectionEvaluation"] --> object_level_fields["Object-level fields"]
    object_level_fields --> eval_attr["object.eval_key"]
    object_level_fields --> id_attr["object.eval_key_id"]
    object_level_fields --> iou_attr["object.eval_key_iou"]
```

Sources: [fiftyone/utils/eval/detection.py:307-379](), [fiftyone/utils/eval/classification.py:285-306](), [fiftyone/utils/eval/segmentation.py:181-216]()

---

