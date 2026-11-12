<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/H-Neurons · page 3 Core Concepts · fetched 2026-11-02 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [scripts/classifier.py](scripts/classifier.py)
- [scripts/extract_activations.py](scripts/extract_activations.py)

</details>



This page provides a detailed explanation of the theoretical and technical foundations underlying the H-Neurons system. It covers the definition of H-Neurons, the CETT (neuron Contribution) metric used to quantify neuron activity, the hallucination detection methodology, and the mathematical formulations that drive the identification process.

For practical implementation details of the pipeline stages, see [Pipeline Guide](#4). For configuration options and parameter tuning, see [Configuration & Options](#6).

---

## Overview

The H-Neurons framework is built on three core concepts that work together to identify and manipulate neurons associated with hallucination in large language models:

1. **H-Neurons**: A sparse subset of neurons in the feed-forward layers that are causally linked to hallucination occurrences
2. **CETT Metric**: A neuron contribution quantification method that measures each neuron's activation while accounting for layer output normalization
3. **Binary Classification**: A supervised learning approach that distinguishes between hallucinated and faithful responses based on neuron activations

---

## H-Neurons: Hallucination-Associated Neurons

### Definition

**H-Neurons** (Hallucination-associated Neurons) are individual neurons in a language model's feed-forward networks that exhibit significantly different activation patterns when the model generates hallucinated content versus factual content. These neurons are:

- **Sparse**: Only a small fraction of the total neurons in the model (typically hundreds to thousands out of millions)
- **Predictive**: Their activation patterns can reliably predict whether a response contains hallucinations
- **Causal**: Suppressing or scaling their activations directly affects hallucination rates

Sources: [README.md:14-14]()

### Identification Process

H-Neurons are identified through a binary classification task where a linear classifier (Logistic Regression) is trained to distinguish hallucinated responses from faithful ones. Neurons with positive coefficients in the trained classifier are designated as H-Neurons.

```mermaid
flowchart TB
    subgraph "Neuron Space"
        FFN["Feed-Forward Network<br/>(Millions of Neurons)"]
        ACT["Neuron Activations<br/>(CETT Values)"]
    end
    
    subgraph "Response Space"
        FAITH["Faithful Responses<br/>(Label: 0)"]
        HALL["Hallucinated Responses<br/>(Label: 1)"]
    end
    
    subgraph "Classification"
        LR["LogisticRegression<br/>(L1 Penalty)"]
        COEF["Coefficients<br/>(Neuron Weights)"]
    end
    
    subgraph "Identified H-Neurons"
        HNEURONS["Sparse Subset<br/>(Positive Coefficients)"]
        COUNT["Hundreds to Thousands<br/>out of Millions"]
    end
    
    FFN --> ACT
    FAITH --> LR
    HALL --> LR
    ACT --> LR
    LR --> COEF
    COEF --> HNEURONS
    HNEURONS --> COUNT
```

**Diagram: H-Neuron Identification Pipeline**

Sources: [scripts/classifier.py:108-117](), [README.md:17-17]()

### Properties

| Property | Description | Code Reference |
|----------|-------------|----------------|
| **Location** | Input to `down_proj` layer in FFN | [scripts/extract_activations.py:36-42]() |
| **Sparsity** | Enforced through L1 regularization | [scripts/classifier.py:108-111]() |
| **Sign** | Positive coefficients indicate H-Neurons | [scripts/classifier.py:117]() |
| **Generalizability** | Effective across in-domain and OOD scenarios | [README.md:20-20]() |

Sources: [scripts/classifier.py:108-117](), [scripts/extract_activations.py:36-42]()

---

## CETT Metric: Neuron Contribution Quantification

### Overview

The **CETT** metric (Neuron Contribution Extraction Through Transformations) quantifies the contribution of individual neurons during inference. It captures neuron activations while accounting for their magnitude, sign, and the overall layer output normalization.

### Implementation: CETTManager Class

The CETT metric is implemented in the `CETTManager` class, which uses forward hooks to capture activations at the `down_proj` layer input.

```mermaid
flowchart LR
    subgraph "FFN Module"
        UP["up_proj"]
        GATE["gate_proj"]
        ACT_FN["Activation"]
        DOWN["down_proj"]
    end
    
    subgraph "CETTManager"
        HOOK["Forward Hook<br/>register_forward_hook"]
        CAP_ACT["Capture Input<br/>self.activations"]
        CAP_NORM["Capture Output Norm<br/>self.output_norms"]
        WNORM["Precompute Weight Norms<br/>self.weight_norms"]
    end
    
    subgraph "Processing"
        ABS["Optional: abs()"]
        MAG["Optional: × weight_norms"]
        NORM["÷ (output_norms + 1e-8)"]
    end
    
    DOWN --> HOOK
    HOOK --> CAP_ACT
    HOOK --> CAP_NORM
    DOWN --> WNORM
    
    CAP_ACT --> ABS
    ABS --> MAG
    WNORM --> MAG
    MAG --> NORM
    CAP_NORM --> NORM
```

**Diagram: CETT Metric Computation Pipeline**

Sources: [scripts/extract_activations.py:26-66]()

### Mathematical Formulation

The CETT value for neuron $i$ in layer $l$ at token position $t$ is computed as:

$$
\text{CETT}_{l,t,i} = \frac{|\text{act}_{l,t,i}| \cdot \|\mathbf{w}_i^{\text{down}}\|_2}{\|\mathbf{o}_{l,t}\|_2 + \epsilon}
$$

Where:
- $\text{act}_{l,t,i}$: Activation of neuron $i$ (input to `down_proj`)
- $\mathbf{w}_i^{\text{down}}$: Weight vector for neuron $i$ in `down_proj` layer
- $\mathbf{o}_{l,t}$: Output vector of layer $l$ at token $t$
- $\epsilon = 10^{-8}$: Numerical stability constant

| Component | Symbol | Implementation | Code Location |
|-----------|--------|----------------|---------------|
| Neuron Activation | $\text{act}_{l,t,i}$ | `input[0]` in hook | [scripts/extract_activations.py:37]() |
| Absolute Value | $\|\cdot\|$ | `torch.abs(acts)` | [scripts/extract_activations.py:63]() |
| Weight Norm | $\|\mathbf{w}_i\|_2$ | `torch.norm(module.weight.data, dim=0)` | [scripts/extract_activations.py:48]() |
| Output Norm | $\|\mathbf{o}\|_2$ | `torch.norm(output.detach(), dim=-1)` | [scripts/extract_activations.py:38]() |
| Normalization | $\epsilon$ | `1e-8` | [scripts/extract_activations.py:66]() |

Sources: [scripts/extract_activations.py:55-66]()

### CETT Configuration Options

The CETT computation supports two boolean flags that modify the calculation:

```python
# From extract_activations.py parse_args()
parser.add_argument("--use_mag", action="store_true", default=True)
parser.add_argument("--use_abs", action="store_true", default=True)
```

| Flag | Effect | Mathematical Impact | Use Case |
|------|--------|---------------------|----------|
| `--use_abs` | Apply absolute value | $\text{act} \rightarrow |\text{act}|$ | Ignore activation sign, focus on magnitude |
| `--use_mag` | Multiply by weight norms | $\text{act} \rightarrow \text{act} \cdot \|\mathbf{w}\|_2$ | Weight contribution by downstream impact |

Sources: [scripts/extract_activations.py:22-23](), [scripts/extract_activations.py:63-64]()

### Tensor Shape Transformations

The `CETTManager.get_cett_tensor()` method performs the following transformations:

```mermaid
flowchart LR
    subgraph "Input Storage"
        ACTS_LIST["self.activations<br/>List[Tensor]<br/>len = num_layers"]
        NORMS_LIST["self.output_norms<br/>List[Tensor]<br/>len = num_layers"]
    end
    
    subgraph "Stacking & Transpose"
        STACK_ACTS["torch.stack()<br/>[layers, tokens, neurons]"]
        TRANS_ACTS["transpose(0,1)<br/>[tokens, layers, neurons]"]
        STACK_NORMS["torch.stack()<br/>[layers, tokens, 1]"]
        TRANS_NORMS["transpose(0,1)<br/>[tokens, layers, 1]"]
    end
    
    subgraph "Processing"
        APPLY["Apply abs(), mag()"]
        DIV["÷ (norms + 1e-8)"]
    end
    
    subgraph "Output"
        FINAL["transpose(0,1)<br/>[layers, tokens, neurons]"]
    end
    
    ACTS_LIST --> STACK_ACTS
    STACK_ACTS --> TRANS_ACTS
    NORMS_LIST --> STACK_NORMS
    STACK_NORMS --> TRANS_NORMS
    
    TRANS_ACTS --> APPLY
    APPLY --> DIV
    TRANS_NORMS --> DIV
    DIV --> FINAL
```

**Diagram: CETT Tensor Shape Transformations**

Sources: [scripts/extract_activations.py:55-66]()

---

## Hallucination Detection Methodology

### Binary Classification Framework

The H-Neurons system frames hallucination detection as a binary classification problem:

- **Positive Class (Label 1)**: Hallucinated/False responses
- **Negative Class (Label 0)**: Faithful/True responses (and potentially other tokens)

### Training Modes

The system supports two distinct training modes that define what constitutes the negative class:

```mermaid
flowchart TB
    subgraph "Data Sources"
        F_ANS["False Answer Tokens<br/>(Hallucinated)"]
        T_ANS["True Answer Tokens<br/>(Faithful)"]
        T_OTHER["True Other Tokens<br/>(Non-Answer)"]
        F_OTHER["False Other Tokens<br/>(Non-Answer)"]
    end
    
    subgraph "Mode: 1-vs-1"
        MODE1_POS["Positive (1)<br/>False Answer Tokens"]
        MODE1_NEG["Negative (0)<br/>True Answer Tokens"]
    end
    
    subgraph "Mode: 3-vs-1"
        MODE3_POS["Positive (1)<br/>False Answer Tokens"]
        MODE3_NEG["Negative (0)<br/>True Ans + True Other + False Other"]
    end
    
    F_ANS --> MODE1_POS
    T_ANS --> MODE1_NEG
    
    F_ANS --> MODE3_POS
    T_ANS --> MODE3_NEG
    T_OTHER --> MODE3_NEG
    F_OTHER --> MODE3_NEG
```

**Diagram: Training Mode Architectures**

Sources: [scripts/classifier.py:37-73](), [README.md:123-125]()

#### Mode Comparison

| Aspect | 1-vs-1 Mode | 3-vs-1 Mode |
|--------|-------------|-------------|
| **Positive Class** | False answer tokens | False answer tokens |
| **Negative Class** | True answer tokens only | True answer + True other + False other |
| **Purpose** | Maximize prediction accuracy | Isolate hallucination-specific neurons |
| **Data Loading** | [scripts/classifier.py:49-60]() | [scripts/classifier.py:63-72]() |
| **Recommendation** | Highest accuracy detection | Research/mechanistic analysis |
| **Sparsity** | Lower | Higher |

Sources: [README.md:123-125](), [scripts/classifier.py:30-73]()

### Regularization Strategies

The classifier supports two regularization penalties that produce fundamentally different models:

| Penalty | Effect | Coefficient Distribution | Use Case | Code Reference |
|---------|--------|-------------------------|----------|----------------|
| **L1** | Drives most weights to zero | Sparse (hundreds of non-zero) | Identifying specific H-Neurons for intervention | [scripts/classifier.py:108-109]() |
| **L2** | Shrinks all weights uniformly | Dense (all non-zero) | Maximum detection accuracy (+1-3%) | [scripts/classifier.py:108-109]() |

The regularization strength is controlled by the `C` parameter (inverse of regularization strength):

$$
\text{Loss} = \text{LogLoss}(y, \hat{y}) + \frac{1}{C} \cdot R(\mathbf{w})
$$

Where $R(\mathbf{w}) = \|\mathbf{w}\|_1$ for L1 or $R(\mathbf{w}) = \|\mathbf{w}\|_2^2$ for L2.

Sources: [scripts/classifier.py:108-111](), [README.md:127-135]()

---

## Token Region Extraction

### Region Types

The CETT metric can be computed over different token regions within a sequence, allowing focused analysis of specific parts of the model's response:

```mermaid
flowchart TB
    subgraph "Sequence Structure"
        SEQ["Full Sequence:<br/>[User Prompt | Assistant Header | Response | EOS]"]
    end
    
    subgraph "Region Identification"
        INPUT["Input Region<br/>[0, input_len]<br/>User prompt tokens"]
        OUTPUT["Output Region<br/>[output_start, output_end]<br/>Assistant response tokens"]
        ANSWER["Answer Tokens<br/>[ans_start, ans_end]<br/>Factual content within output"]
        OTHER["All Except Answer<br/>output \ answer_tokens<br/>Non-factual output tokens"]
    end
    
    SEQ --> INPUT
    SEQ --> OUTPUT
    OUTPUT --> ANSWER
    OUTPUT --> OTHER
```

**Diagram: Token Region Segmentation**

Sources: [scripts/extract_activations.py:68-97]()

### Region Identification Logic

The `get_region_indices()` function identifies token boundaries for each region:

| Region | Start Index | End Index | Implementation |
|--------|-------------|-----------|----------------|
| `input` | 0 | `user_ids.shape[1] - 1` | [scripts/extract_activations.py:75-76]() |
| `output` | `input_len + 1` | `len(full_tokens) - 1` | [scripts/extract_activations.py:80-81]() |
| `answer_tokens` | Found via pattern matching | `ans_start + len(answer_tokens)` | [scripts/extract_activations.py:87-91]() |
| `all_except_answer_tokens` | Concatenate segments | Before and after answer region | [scripts/extract_activations.py:135-141]() |

Sources: [scripts/extract_activations.py:68-97]()

### Aggregation Methods

After extracting CETT values for tokens in a region, the values are aggregated to produce a single vector per layer:

```python
# From extract_activations.py
if args.method == "mean": 
    final_act = selected_cett.mean(dim=1)  # Average over tokens
else: 
    final_act, _ = selected_cett.max(dim=1)  # Max over tokens
```

| Method | Operation | Output Shape | Use Case |
|--------|-----------|--------------|----------|
| `mean` | `torch.mean(dim=1)` | `[layers, neurons]` | Smooth, representative activation |
| `max` | `torch.max(dim=1)` | `[layers, neurons]` | Peak activation detection |

Sources: [scripts/extract_activations.py:149-150]()

---

## Code Entity Mapping

This diagram maps the core concepts to their implementing code entities:

```mermaid
flowchart TB
    subgraph "Concept: H-Neurons"
        CONCEPT_H["H-Neurons<br/>(Sparse Subset)"]
    end
    
    subgraph "Concept: CETT Metric"
        CONCEPT_CETT["CETT Metric<br/>(Neuron Contribution)"]
    end
    
    subgraph "Concept: Classification"
        CONCEPT_CLASS["Binary Classification<br/>(Hallucination Detection)"]
    end
    
    subgraph "Code: extract_activations.py"
        CETT_MGR["CETTManager<br/>class (lines 26-66)"]
        GET_CETT["get_cett_tensor()<br/>method (lines 55-66)"]
        HOOKS["_register_hooks()<br/>method (lines 35-42)"]
        WNORMS["_get_weight_norms()<br/>method (lines 44-49)"]
        REGIONS["get_region_indices()<br/>function (lines 68-97)"]
    end
    
    subgraph "Code: classifier.py"
        LOAD_DATA["load_data()<br/>function (lines 37-74)"]
        LR_MODEL["LogisticRegression<br/>sklearn.linear_model (line 108)"]
        EVAL["run_evaluation()<br/>function (lines 76-89)"]
        COEF_CHECK["model.coef_[0] > 0<br/>(line 117)"]
    end
    
    subgraph "Storage"
        NPY_FILES["act_{qid}.npy<br/>NumPy arrays"]
        PKL_MODEL["classifier.pkl<br/>Joblib serialization"]
    end
    
    CONCEPT_CETT --> CETT_MGR
    CONCEPT_CETT --> GET_CETT
    CETT_MGR --> HOOKS
    CETT_MGR --> WNORMS
    GET_CETT --> NPY_FILES
    REGIONS --> GET_CETT
    
    CONCEPT_CLASS --> LOAD_DATA
    CONCEPT_CLASS --> LR_MODEL
    NPY_FILES --> LOAD_DATA
    LR_MODEL --> EVAL
    LR_MODEL --> PKL_MODEL
    
    CONCEPT_H --> COEF_CHECK
    COEF_CHECK --> PKL_MODEL
```

**Diagram: Core Concepts to Code Entity Mapping**

Sources: [scripts/extract_activations.py:26-97](), [scripts/classifier.py:37-117]()

---

## Evaluation Metrics

The classifier's performance is assessed using five standard binary classification metrics:

| Metric | Formula | Implementation | Code Location |
|--------|---------|----------------|---------------|
| **Accuracy** | $\frac{TP + TN}{TP + TN + FP + FN}$ | `accuracy_score(y, preds)` | [scripts/classifier.py:80]() |
| **Precision** | $\frac{TP}{TP + FP}$ | `precision_recall_fscore_support(...)[0]` | [scripts/classifier.py:81]() |
| **Recall** | $\frac{TP}{TP + FN}$ | `precision_recall_fscore_support(...)[1]` | [scripts/classifier.py:81]() |
| **F1 Score** | $\frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$ | `precision_recall_fscore_support(...)[2]` | [scripts/classifier.py:81]() |
| **AUROC** | Area under ROC curve | `roc_auc_score(y, probs)` | [scripts/classifier.py:82]() |

Where:
- TP = True Positives (correctly identified hallucinations)
- TN = True Negatives (correctly identified faithful responses)
- FP = False Positives (faithful responses misclassified as hallucinations)
- FN = False Negatives (hallucinations misclassified as faithful)

Sources: [scripts/classifier.py:76-89]()

---

## Summary

The H-Neurons framework combines three core technical components:

1. **CETT Metric**: Quantifies neuron contributions through forward hooks on `down_proj` layers, incorporating weight norms and output normalization
2. **Binary Classification**: Trains a Logistic Regression model with L1/L2 regularization to distinguish hallucinated from faithful responses
3. **Sparse Neuron Identification**: Extracts neurons with positive coefficients as H-Neurons, creating an interpretable and causal model of hallucination

This foundation enables both detection (high-accuracy classification) and intervention (targeted neuron manipulation) capabilities. For implementation details, proceed to [Pipeline Guide](#4).

Sources: [README.md:1-162](), [scripts/extract_activations.py:1-156](), [scripts/classifier.py:1-132]()

---

