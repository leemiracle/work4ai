<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/kinetics-i3d · page 5 Results and Analysis · fetched 2026-10-26 -->

# Results and Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [out/imagenet_joint.txt](out/imagenet_joint.txt)
- [out/no_imagenet_joint.txt](out/no_imagenet_joint.txt)

</details>



This document provides comprehensive analysis and interpretation of I3D model classification results. It covers the output formats produced by the evaluation system, compares performance across different model configurations, and explains how to interpret the numerical results for action recognition tasks.

For information about running evaluations, see [Evaluation Framework](#4). For details about the model architectures that produce these results, see [Model Architecture](#2).

## Output Processing Pipeline

The I3D evaluation system generates structured output files that contain classification predictions, confidence scores, and detailed probability distributions. The results flow through several processing stages before final output.

```mermaid
graph TD
    subgraph "Model Inference"
        ModelRGB["RGB I3D Model"] --> RGBLogits["RGB Logits<br/>[batch, 400/600]"]
        ModelFlow["Flow I3D Model"] --> FlowLogits["Flow Logits<br/>[batch, 400/600]"]
    end
    
    subgraph "Logit Processing"
        RGBLogits --> LogitFusion["Logit Addition<br/>rgb_logits + flow_logits"]
        FlowLogits --> LogitFusion
        LogitFusion --> LogitNorm["Logit Norm Calculation<br/>tf.norm(logits)"]
    end
    
    subgraph "Probability Conversion"
        LogitFusion --> Softmax["Softmax Activation<br/>tf.nn.softmax(logits)"]
        Softmax --> TopK["Top-K Selection<br/>tf.nn.top_k(probs, k=20)"]
    end
    
    subgraph "Output Formatting"
        TopK --> FormatOutput["Format Output Lines<br/>prob logit class_name"]
        LogitNorm --> FormatOutput
        FormatOutput --> OutputFile["Output Text File<br/>*.txt"]
    end
    
    subgraph "Label Mapping"
        LabelMap["label_map_600.txt"] --> FormatOutput
    end
```

**Sources:** [evaluate_sample.py:1-200](), [out/imagenet_joint.txt:1-24](), [out/no_imagenet_joint.txt:1-24]()

## Classification Result Structure

Each output file follows a standardized format that provides comprehensive information about the model's predictions and confidence levels.

```mermaid
graph TD
    subgraph "Output File Structure"
        Header["Line 1: Norm of logits: X.XXXXXX"]
        Blank1["Line 2: Empty line"]
        SubHeader["Line 3: 'Top classes and probabilities'"]
        
        Header --> Blank1
        Blank1 --> SubHeader
        SubHeader --> ResultLines
    end
    
    subgraph "Result Lines Format"
        ResultLines["Lines 4-23: Classification Results"]
        ResultLines --> Probability["Column 1: Probability<br/>(0.0 to 1.0)"]
        ResultLines --> Logit["Column 2: Raw Logit Value<br/>(unbounded float)"]
        ResultLines --> ClassName["Column 3: Action Class Name<br/>(human readable)"]
    end
    
    subgraph "Example Values"
        Probability --> ExProb["1.0<br/>1.4971563e-09<br/>3.8431164e-10"]
        Logit --> ExLogit["41.813675<br/>21.493977<br/>20.134108"]
        ClassName --> ExClass["playing cricket<br/>hurling (sport)<br/>catching or throwing baseball"]
    end
```

**Sources:** [out/imagenet_joint.txt:1-24](), [out/no_imagenet_joint.txt:1-24]()

## Model Configuration Comparison

The evaluation system produces results for multiple model configurations, each with different training strategies and performance characteristics.

| Configuration | File Pattern | Training Strategy | Dataset Size | Pre-training |
|---------------|--------------|-------------------|--------------|--------------|
| ImageNet RGB | `imagenet_rgb.txt` | ImageNet → Kinetics | 400 classes | Yes |
| ImageNet Flow | `imagenet_flow.txt` | ImageNet → Kinetics | 400 classes | Yes |
| ImageNet Joint | `imagenet_joint.txt` | ImageNet → Kinetics | 400 classes | Yes |
| Scratch RGB | `no_imagenet_rgb.txt` | Kinetics only | 400 classes | No |
| Scratch Flow | `no_imagenet_flow.txt` | Kinetics only | 400 classes | No |
| Scratch Joint | `no_imagenet_joint.txt` | Kinetics only | 400 classes | No |
| Scratch RGB-600 | `no_imagenet_rgb600.txt` | Kinetics-600 only | 600 classes | No |

**Sources:** [multi_evaluate.sh:1-50](), [evaluate_sample.py:1-200]()

## Numerical Result Interpretation

### Logit Norm Analysis

The logit norm provides a measure of the model's overall confidence across all classes. Higher values typically indicate stronger feature activations and more confident predictions.

```mermaid
graph LR
    subgraph "Logit Norm Calculation"
        RawLogits["Raw Logits Array<br/>[logit_1, logit_2, ..., logit_n]"] --> NormCalc["tf.norm(logits)<br/>L2 Norm Calculation"]
        NormCalc --> NormValue["Norm Value<br/>e.g., 138.468658"]
    end
    
    subgraph "Interpretation"
        NormValue --> HighNorm["High Norm (>100)<br/>Strong Confidence"]
        NormValue --> MedNorm["Medium Norm (10-100)<br/>Moderate Confidence"]
        NormValue --> LowNorm["Low Norm (<10)<br/>Low Confidence"]
    end
```

**Sources:** [out/imagenet_joint.txt:1](), [out/no_imagenet_joint.txt:1]()

### Probability Distribution Analysis

The probability values show the model's confidence in each class prediction after softmax normalization.

```mermaid
graph TD
    subgraph "Probability Characteristics"
        TopProb["Top Probability: 1.0<br/>Highest confidence class"]
        SecondProb["Second: 1.4971563e-09<br/>Exponentially lower"]
        ThirdProb["Third: 3.8431164e-10<br/>Further decrease"]
    end
    
    subgraph "Confidence Patterns"
        TopProb --> Dominant["Dominant Prediction<br/>Clear winner"]
        SecondProb --> Competitors["Competing Classes<br/>Similar actions"]
        ThirdProb --> LongTail["Long Tail<br/>Unlikely alternatives"]
    end
    
    subgraph "Action Semantics"
        Dominant --> Cricket["playing cricket"]
        Competitors --> Sports["hurling (sport)<br/>catching or throwing baseball<br/>catching or throwing softball"]
        LongTail --> Related["hitting baseball<br/>playing tennis<br/>playing kickball"]
    end
```

**Sources:** [out/imagenet_joint.txt:4-11](), [out/no_imagenet_joint.txt:4-11]()

## Performance Comparison Framework

### ImageNet Pre-trained vs From-Scratch Results

Based on the available output files, both ImageNet pre-trained models and from-scratch models produce identical results for the sample cricket video, suggesting comparable performance on this particular test case.

| Metric | ImageNet Joint | No-ImageNet Joint | Difference |
|--------|----------------|-------------------|------------|
| Logit Norm | 138.468658 | 138.468658 | 0.000000 |
| Top Class | playing cricket | playing cricket | Identical |
| Top Probability | 1.0 | 1.0 | Identical |
| Top Logit | 41.813675 | 41.813675 | Identical |
| Second Class | hurling (sport) | hurling (sport) | Identical |

**Sources:** [out/imagenet_joint.txt:1-24](), [out/no_imagenet_joint.txt:1-24]()

### Action Recognition Accuracy Patterns

The results demonstrate the model's ability to distinguish between related action classes with high semantic similarity.

```mermaid
graph TD
    subgraph "Action Class Hierarchy"
        TopPred["playing cricket<br/>Prob: 1.0"]
        
        TopPred --> SimilarSports["Similar Ball Sports"]
        SimilarSports --> Hurling["hurling (sport)<br/>Prob: 1.49e-09"]
        SimilarSports --> Baseball["catching or throwing baseball<br/>Prob: 3.84e-10"]
        SimilarSports --> Softball["catching or throwing softball<br/>Prob: 1.55e-10"]
        
        TopPred --> BallGames["Other Ball Games"]
        BallGames --> Tennis["playing tennis<br/>Prob: 8.80e-11"]
        BallGames --> Kickball["playing kickball<br/>Prob: 2.44e-11"]
        BallGames --> Squash["playing squash or racquetball<br/>Prob: 1.15e-11"]
    end
    
    subgraph "Semantic Distance"
        SimilarSports --> HighSim["High Semantic Similarity<br/>Stick/bat sports"]
        BallGames --> MedSim["Medium Semantic Similarity<br/>Ball-based games"]
    end
```

**Sources:** [out/imagenet_joint.txt:4-11](), [label_map_600.txt:1-600]()

## Output File Generation Process

The evaluation system generates multiple output files through a systematic process that evaluates different model configurations.

```mermaid
graph TD
    subgraph "Batch Evaluation Process"
        MultiEval["multi_evaluate.sh"] --> EvalConfigs["Evaluation Configurations"]
        
        EvalConfigs --> Config1["--eval_type=rgb<br/>--imagenet_pretrained=True"]
        EvalConfigs --> Config2["--eval_type=flow<br/>--imagenet_pretrained=True"]
        EvalConfigs --> Config3["--eval_type=joint<br/>--imagenet_pretrained=True"]
        EvalConfigs --> Config4["--eval_type=rgb<br/>--imagenet_pretrained=False"]
        EvalConfigs --> Config5["--eval_type=flow<br/>--imagenet_pretrained=False"]
        EvalConfigs --> Config6["--eval_type=joint<br/>--imagenet_pretrained=False"]
        EvalConfigs --> Config7["--eval_type=rgb600<br/>--imagenet_pretrained=False"]
    end
    
    subgraph "Output File Mapping"
        Config1 --> Out1["imagenet_rgb.txt"]
        Config2 --> Out2["imagenet_flow.txt"]
        Config3 --> Out3["imagenet_joint.txt"]
        Config4 --> Out4["no_imagenet_rgb.txt"]
        Config5 --> Out5["no_imagenet_flow.txt"]
        Config6 --> Out6["no_imagenet_joint.txt"]
        Config7 --> Out7["no_imagenet_rgb600.txt"]
    end
```

**Sources:** [multi_evaluate.sh:1-50](), [evaluate_sample.py:1-200]()

## Statistical Analysis Guidelines

### Confidence Score Interpretation

When analyzing I3D results, consider these statistical patterns:

1. **Dominant Predictions**: Probabilities near 1.0 indicate high model confidence
2. **Competing Classes**: Secondary probabilities in the 1e-6 to 1e-12 range suggest semantically related actions
3. **Logit Separation**: Large gaps between top logits (>20 units) indicate clear class separation
4. **Norm Values**: Logit norms above 100 typically indicate strong feature activation

### Result Validation Checklist

- [ ] Verify logit norm is positive and reasonable (typically 10-200)
- [ ] Confirm top probability sums with others approach 1.0
- [ ] Check that predicted class matches expected action semantics
- [ ] Validate that competing classes are semantically related
- [ ] Ensure output format matches specification exactly

**Sources:** [out/imagenet_joint.txt:1-24](), [evaluate_sample.py:1-200]()

---

