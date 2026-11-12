<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/sentence-transformers · extra page Sparse Model Loss Functions · fetched 2026-10-26 -->

# Sparse Model Loss Functions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/package_reference/sparse_encoder/losses.md](docs/package_reference/sparse_encoder/losses.md)
- [docs/sparse_encoder/loss_overview.md](docs/sparse_encoder/loss_overview.md)
- [sentence_transformers/base/modality.py](sentence_transformers/base/modality.py)
- [sentence_transformers/base/modality_types.py](sentence_transformers/base/modality_types.py)
- [sentence_transformers/cross_encoder/__init__.py](sentence_transformers/cross_encoder/__init__.py)
- [sentence_transformers/cross_encoder/evaluation/__init__.py](sentence_transformers/cross_encoder/evaluation/__init__.py)
- [sentence_transformers/sentence_transformer/__init__.py](sentence_transformers/sentence_transformer/__init__.py)
- [sentence_transformers/sparse_encoder/__init__.py](sentence_transformers/sparse_encoder/__init__.py)
- [sentence_transformers/sparse_encoder/losses/__init__.py](sentence_transformers/sparse_encoder/losses/__init__.py)
- [sentence_transformers/sparse_encoder/losses/cached_splade.py](sentence_transformers/sparse_encoder/losses/cached_splade.py)
- [sentence_transformers/sparse_encoder/losses/sparse_angle.py](sentence_transformers/sparse_encoder/losses/sparse_angle.py)
- [sentence_transformers/sparse_encoder/losses/sparse_cosent.py](sentence_transformers/sparse_encoder/losses/sparse_cosent.py)
- [sentence_transformers/sparse_encoder/losses/sparse_cosine_similarity.py](sentence_transformers/sparse_encoder/losses/sparse_cosine_similarity.py)
- [sentence_transformers/sparse_encoder/losses/sparse_distill_kl_div.py](sentence_transformers/sparse_encoder/losses/sparse_distill_kl_div.py)
- [sentence_transformers/sparse_encoder/losses/sparse_margin_mse.py](sentence_transformers/sparse_encoder/losses/sparse_margin_mse.py)
- [sentence_transformers/sparse_encoder/losses/sparse_mse.py](sentence_transformers/sparse_encoder/losses/sparse_mse.py)
- [sentence_transformers/sparse_encoder/losses/sparse_multiple_negatives_ranking.py](sentence_transformers/sparse_encoder/losses/sparse_multiple_negatives_ranking.py)
- [tests/base/test_modality.py](tests/base/test_modality.py)

</details>



## Purpose and Scope

This page provides a comprehensive technical reference for the loss functions used to train `SparseEncoder` models within the sentence-transformers codebase. Sparse encoders require specialized loss functions that jointly optimize semantic learning objectives and sparsity-inducing regularizers to produce efficient sparse representations suitable for retrieval.

**Key architectural note:**  
Training a `SparseEncoder` generally requires *wrapper* loss functions that combine a main semantic loss with regularizers for sparsity control. The primary wrappers are `SpladeLoss` and `CSRLoss`.  
The only exception is the `SparseMSELoss`, which performs direct embedding-level distillation and can be utilized standalone.

Sources: [docs/sparse_encoder/loss_overview.md:1-86](), [sentence_transformers/sparse_encoder/losses/__init__.py:1-29]()

---

## Loss Architecture Overview

Sparse model loss functions are architected following a compositional design that cleanly separates the semantic learning objective from sparsity regularization. This layered design enhances modularity and supports flexible combinations of main losses and regularizers.

### Two-Layer Architecture Pattern

```mermaid
graph TB
    Input["Input: sentence_features + labels"]
    
    subgraph WrapperLoss["Layer 1: Wrapper Loss (SpladeLoss or CSRLoss)"]
        Wrapper["Wrapper Loss"]
        Wrapper_Purpose["Purpose: combine main loss and regularization"]
    end
    
    subgraph MainLoss["Layer 2: Main Loss"]
        BaseLoss["Main loss module<br/>(SparseMultipleNegativesRankingLoss, SparseMarginMSELoss, etc.)"]
        MainLoss_Purpose["Purpose: learn semantic similarity or ranking"]
    end
    
    subgraph Regularizers["Layer 3: Regularizers"]
        DocReg["Document Regularizer<br/>(default: FlopsLoss)"]
        QueryReg["Query Regularizer<br/>(default: FlopsLoss)"]
        Reg_Purpose["Purpose: enforce sparsity constraints"]
    end
    
    Output["Output: Dict of loss components {base_loss, doc_reg_loss, query_reg_loss}"]
    
    Input --> Wrapper
    Wrapper --> BaseLoss
    Wrapper --> DocReg
    Wrapper --> QueryReg
    BaseLoss --> Output
    DocReg --> Output
    QueryReg --> Output
    
    Wrapper_Purpose -.describes.-> Wrapper
    MainLoss_Purpose -.describes.-> BaseLoss
    Reg_Purpose -.describes.-> DocReg
    Reg_Purpose -.describes.-> QueryReg
```

**Note:**  
- The wrapper loss receives raw input batches and calls the model to produce sparse embeddings.  
- It then computes the main semantic loss from embeddings and labels.  
- Concurrently, it computes sparse regularization on query and document embeddings separately, weighted by hyperparameters.  
- Finally, it aggregates all components into a loss dictionary.  
- `SparseMSELoss` is a distinct loss that does not require wrapping and targets embedding-level distillation.

Sources: [sentence_transformers/sparse_encoder/losses/splade.py:15-163](), [sentence_transformers/sparse_encoder/losses/csr.py:129-229](), [docs/sparse_encoder/loss_overview.md:4-7]()

---

## Wrapper Losses

### SpladeLoss

`SpladeLoss` is the principal wrapper loss designed for SPLADE-style architectures, which leverage the `MLMTransformer` backbone with `SpladePooling` to produce sparse lexical-expansion embeddings.

#### Data Flow and Components

```mermaid
graph TB
    SF["Input: sentence_features (Iterable[dict])"]
    Model["self.model(sentence_feature) -> List[Tensor]"]
    
    subgraph Embeddings["Embeddings"]
        QueryEmb["embeddings[0] (query embedding)"]
        DocEmb["embeddings[1:] (document embeddings)"]
    end
    
    subgraph LossComputation["Loss Components"]
        BaseLoss["self.loss.compute_loss_from_embeddings(embeddings, labels)"]
        DocReg["self.document_regularizer.compute_loss_from_embeddings(concat(embeddings[1:]))"]
        QueryReg["self.query_regularizer.compute_loss_from_embeddings(embeddings[0])"]
    end
    
    subgraph OutputDict["Output Dictionary"]
        BL["base_loss"]
        DRL["document_regularizer_loss (weighted)"]
        QRL["query_regularizer_loss (weighted)"]
    end
    
    SF --> Model
    Model --> QueryEmb
    Model --> DocEmb
    QueryEmb --> BaseLoss
    DocEmb --> BaseLoss
    QueryEmb --> QueryReg
    DocEmb --> DocReg
    BaseLoss --> BL
    DocReg --> DRL
    QueryReg --> QRL
```

#### Important Parameters

| Parameter                        | Type                   | Purpose                                             |
|---------------------------------|------------------------|-----------------------------------------------------|
| `model`                         | `SparseEncoder`        | The underlying sparse model                          |
| `loss`                          | `nn.Module`            | Main semantic loss (e.g., `SparseMarginMSELoss`)    |
| `document_regularizer_weight`   | `float`                | Weight for document embedding sparsity regularizer  |
| `query_regularizer_weight`      | `float \| None`        | Weight for query embedding sparsity regularizer     |
| `document_regularizer`          | `nn.Module \| None`    | Custom doc regularizer, defaults to `FlopsLoss`     |
| `query_regularizer`             | `nn.Module \| None`    | Custom query regularizer, defaults to `FlopsLoss`   |
| `document_regularizer_threshold`| `int \| None`          | Min non-zero dims threshold for doc regularizer     |
| `query_regularizer_threshold`   | `int \| None`          | Min non-zero dims threshold for query regularizer   |
| `use_document_regularizer_only` | `bool`                 | Treat all inputs as documents, e.g., symmetric tasks|

#### Usage Example

```python
from sentence_transformers.sparse_encoder import SparseEncoder, losses

model = SparseEncoder("distilbert/distilbert-base-uncased")

loss = losses.SpladeLoss(
    model,
    loss=losses.SparseMarginMSELoss(model),
    document_regularizer_weight=3e-5,  # λ_d
    query_regularizer_weight=5e-5,     # λ_q
    document_regularizer_threshold=50, # ignore docs with fewer than 50 active dims
)
```

Sources: [sentence_transformers/sparse_encoder/losses/splade.py:15-204]()

---

### CSRLoss

`CSRLoss` is used with `SparseAutoEncoder` modules for training sparse encoders with Contrastive Sparse Representation learning objectives. It integrates reconstruction loss components that enforce faithful encoding-decoding of embeddings.

#### Data Flow and Components

```mermaid
graph TB
    SF["Input: sentence_features"]
    Model["self.model(sentence_feature) -> dict (embeddings and decoded)"]
    
    SE["sentence_embedding"]
    SEB["sentence_embedding_backbone"]
    DEK["decoded_embedding_k"]
    DE4K["decoded_embedding_4k"]
    DEA["decoded_embedding_aux"]
    DEKPB["decoded_embedding_k_pre_bias"]
    
    subgraph ReconstructionLosses["CSR Reconstruction Loss Components"]
        Lk["L_k = MSE(original, recons_k)"]
        L4k["L_4k = MSE(original, recons_4k) / 8"]
        LAux["L_aux = NMSE(recons_aux, residual) * beta"]
    end
    
    BaseLoss["self.loss.compute_loss_from_embeddings(sentence_embedding) * gamma"]
    
    Output["Loss dict: {reconstruction_loss_k, reconstruction_loss_4k, reconstruction_loss_aux, base_loss}"]
    
    SF --> Model
    Model --> SE
    Model --> SEB
    Model --> DEK
    Model --> DE4K
    Model --> DEA
    Model --> DEKPB
    
    SEB --> Lk
    DEK --> Lk
    
    SEB --> L4k
    DE4K --> L4k
    
    DEKPB --> LAux
    DEA --> LAux
    
    SE --> BaseLoss
    
    Lk --> Output
    L4k --> Output
    LAux --> Output
    BaseLoss --> Output
```

#### Hyperparameters

| Parameter | Type               | Default | Purpose                                           |
|-----------|--------------------|---------|---------------------------------------------------|
| `model`   | `SparseEncoder`    | \-      | SparseAutoEncoder model                            |
| `loss`    | `nn.Module \| None`| default: `SparseMultipleNegativesRankingLoss` | Main contrastive loss for semantic training |
| `beta`    | `float`            | 0.1     | Weight for auxiliary reconstruction loss (L_aux) |
| `gamma`   | `float`            | 1.0     | Weight for main contrastive loss                   |

#### Usage Example

```python
from sentence_transformers.sparse_encoder import SparseEncoder, losses

model = SparseEncoder("sentence-transformers/all-MiniLM-L6-v2")

loss = losses.CSRLoss(
    model,
    loss=losses.SparseMultipleNegativesRankingLoss(model),
    beta=0.1,   # auxiliary reconstruction weight
    gamma=1.0,  # main contrastive loss weight
)
```

Sources: [sentence_transformers/sparse_encoder/losses/csr.py:28-229]()

---

## Main Loss Functions

Main loss functions define the core semantic learning objective and are usually combined inside wrapper losses for sparse training. They implement a required interface method:

```python
def compute_loss_from_embeddings(
    self,
    embeddings: list[torch.Tensor],
    labels: torch.Tensor | None = None
) -> torch.Tensor | dict[str, torch.Tensor]:
    """
    Computes loss given model embeddings and optional labels.

    Args:
        embeddings: list of sparse tensor embeddings, one per input column.
        labels: optional ground truth labels/tensors.

    Returns:
        Single loss scalar or dictionary of loss components.
    """
```

### Main Losses Taxonomy & Data Formats

```mermaid
graph TB
    subgraph Contrastive ["Contrastive Family"]
        SMNRL["SparseMultipleNegativesRankingLoss"]
        SMNRL_Data["Data: (anchor, positive) pairs<br/>or (anchor, positive, negative) triplets"]
    end
    
    subgraph Triplet ["Triplet Family"]
        STL["SparseTripletLoss"]
        STL_Data["Data: (anchor, positive, negative) triplets"]
    end
    
    subgraph Regression ["Regression Family"]
        SCSL["SparseCoSENTLoss"]
        SAL["SparseAnglELoss"]
        SCSIM["SparseCosineSimilarityLoss"]
        REG_Data["Data: (sent_A, sent_B) pairs with float similarity scores [0,1]"]
    end
    
    subgraph Distillation ["Distillation Family"]
        SMSEL["SparseMSELoss (standalone)"]
        SMMSEL["SparseMarginMSELoss"]
        SDKLDL["SparseDistillKLDivLoss"]
        DIST_Data["Data: sentences + teacher embeddings"]
    end
    
    SMNRL_Data -.requires.-> SMNRL
    STL_Data -.requires.-> STL
    REG_Data -.requires.-> SCSL
    REG_Data -.requires.-> SAL
    REG_Data -.requires.-> SCSIM
    DIST_Data -.requires.-> SMSEL
    DIST_Data -.requires.-> SMMSEL
    DIST_Data -.requires.-> SDKLDL
```

---

### Contrastive Loss: SparseMultipleNegativesRankingLoss

- Implements InfoNCE loss using in-batch negatives.  
- Most commonly used for training sparse retrieval models.  
- Supports training on `(anchor, positive)` or `(anchor, positive, negative)` tuples.  

See: [sentence_transformers/sparse_encoder/losses/sparse_multiple_negatives_ranking.py]()

---

### Regression Losses

Train on pairs with continuous similarity scores in range [0,1].

- `SparseCoSENTLoss`: Circle loss variant specialized for sentence similarity.  
- `SparseAnglELoss`: Complex valued angle-based metric learning loss.  
- `SparseCosineSimilarityLoss`: Standard cosine similarity regression loss.

See: respective files in [sentence_transformers/sparse_encoder/losses/]()

---

### Triplet Loss: SparseTripletLoss

- Margin-based triplet loss enforcing `d(anchor, positive) + margin < d(anchor, negative)`.  
- Used when explicit triplet data with positives and negatives is available.

See: [sentence_transformers/sparse_encoder/losses/sparse_triplet.py]()

---

### Distillation Losses

Used for knowledge distillation from a teacher model.

- `SparseMSELoss`: Embedding-level MSE loss for directly copying sparse teacher embeddings. *Can be used standalone without wrapper.*  
- `SparseMarginMSELoss`: Uses margin differences for distillation of relative scores.  
- `SparseDistillKLDivLoss`: Distills the probability (softmax) distribution of teacher rankings.

See: [sentence_transformers/sparse_encoder/losses/sparse_mse.py](), [sparse_margin_mse.py](), [sparse_distill_kl_div.py]()

Sources: [sentence_transformers/sparse_encoder/losses/__init__.py:1-29](), [docs/sparse_encoder/loss_overview.md:43-62]()

---

## Regularizers

Regularizers enforce sparsity in sparse embeddings, promoting efficiency by penalizing embedding "density".

### FlopsLoss

- The default regularizer for `SpladeLoss` wrapper.  
- Implements squared L2 norm of mean embedding vector across batch, approximating the FLOPS cost of the sparse vectors.  
- Supports an optional `threshold` that masks out embeddings with fewer than `threshold` non-zero components.

#### Mathematical Expression

\[
\text{FlopsLoss} = \| \text{mean}(embeddings) \|_2^2
\]

With threshold mask \(m = \mathbf{1}[L_0(\text{embedding}) > \text{threshold}]\):

\[
embeddings = embeddings \times m
\]

#### Usage Illustration

```python
from sentence_transformers.sparse_encoder.losses import FlopsLoss

# Default usage inside SpladeLoss (no threshold)
loss = SpladeLoss(
    model,
    loss=SparseMultipleNegativesRankingLoss(model),
    document_regularizer_weight=3e-5,  # lambda_d
)

# Thresholded regularizer to ignore embeddings with <50 non-zero entries
loss = SpladeLoss(
    model,
    loss=SparseMultipleNegativesRankingLoss(model),
    document_regularizer_weight=3e-5,
    document_regularizer_threshold=50,
)

# Custom regularizer instance
custom_reg = FlopsLoss(model, threshold=100)
loss = SpladeLoss(
    model,
    loss=SparseMultipleNegativesRankingLoss(model),
    document_regularizer=custom_reg,
    document_regularizer_weight=3e-5,
)
```

**Note:**  
`FlopsLoss` is *not* used standalone as a primary loss but only as a sparsity regularizer inside wrappers.

Sources: [sentence_transformers/sparse_encoder/losses/flops.py:11-65]()

---

## Loss Selection Guide

### Decision Flowchart

```mermaid
graph TB
    Start{{"Model architecture?"}}
    
    SAE{{"Using SparseAutoEncoder module?"}}
    
    CSR["Use CSRLoss wrapper"]
    CSR_main["Main loss (default): SparseMultipleNegativesRankingLoss"]
    
    SPLADE["Use SpladeLoss wrapper"]
    
    DataFormat{{"Training data format?"}}
    
    Pairs["(anchor, positive) pairs"]
    Triplets["(anchor, pos, neg) triplets"]
    Scores["(sent_A, sent_B) with float similarity scores"]
    TeacherLabels["Teacher model embeddings / distillation labels"]
    
    SMNRL["SparseMultipleNegativesRankingLoss"]
    STL["SparseTripletLoss or SparseMultipleNegativesRankingLoss"]
    CoSENT["SparseCoSENTLoss or SparseAnglELoss or SparseCosineSimilarityLoss"]
    
    DistillType{{"Type of distillation?"}}
    
    EmbedLevel["Embedding-level distillation"]
    MarginDistill["Margin-based distillation"]
    ProbDistill["Probability distillation (KL-divergence)"]
    
    SMSE["SparseMSELoss (standalone)"]
    SMMSE["SparseMarginMSELoss (used with SpladeLoss)"]
    SDKLD["SparseDistillKLDivLoss (used with SpladeLoss)"]
    
    Start --> SAE
    SAE -->|Yes| CSR
    CSR --> CSR_main
    
    SAE -->|No| SPLADE
    SPLADE --> DataFormat
    
    DataFormat --> Pairs
    DataFormat --> Triplets
    DataFormat --> Scores
    DataFormat --> TeacherLabels
    
    Pairs --> SMNRL
    Triplets --> STL
    Scores --> CoSENT
    
    TeacherLabels --> DistillType
    DistillType --> EmbedLevel
    DistillType --> MarginDistill
    DistillType --> ProbDistill
    
    EmbedLevel --> SMSE
    MarginDistill --> SMMSE
    ProbDistill --> SDKLD
```

### Typical Training Scenarios

| Scenario                   | Data Format                            | Recommended Loss Setup                                          |
|----------------------------|--------------------------------------|----------------------------------------------------------------|
| General retrieval training  | `(anchor, positive)` pairs            | `SpladeLoss` + `SparseMultipleNegativesRankingLoss`            |
| Training with hard negatives| `(anchor, positive, negative_1, ...)`| `SpladeLoss` + `SparseMultipleNegativesRankingLoss`            |
| Semantic similarity scoring | `(sent_A, sent_B)` pairs + float scores| `SpladeLoss` + one of `SparseCoSENTLoss`, `SparseAnglELoss`, `SparseCosineSimilarityLoss` |
| Distillation simplified     | Sentences + teacher embeddings        | `SparseMSELoss` (standalone, no wrapper)                        |
| Distillation advanced       | Triplets + teacher margin or probabilities | `SpladeLoss` + `SparseMarginMSELoss` or `SparseDistillKLDivLoss`|
| Autoencoder-based training  | `(anchor, positive)` pairs             | `CSRLoss` (wraps main + reconstruction losses)                  |

### Hyperparameter Guidelines

- For `SpladeLoss`:  
  - `document_regularizer_weight`: typically 1e-5 to 5e-5 (default ~3e-5)  
  - `query_regularizer_weight`: typically slightly higher (3e-5 to 1e-4, default ~5e-5)  
  - Heuristic: queries get stronger sparsity regularization to encourage efficiency  
- For `CSRLoss`:  
  - `beta` (auxiliary reconstruction loss weight): 0.1  
  - `gamma` (contrastive loss weight): 1.0  

Sources: [docs/sparse_encoder/loss_overview.md:63-70](), [sentence_transformers/sparse_encoder/losses/splade.py:36-57]()

---

## Complete Training Example

### Example Using SpladeLoss and Distillation

```python
from datasets import Dataset
from sentence_transformers.sparse_encoder import SparseEncoder, SparseEncoderTrainer, losses

# Initialize models
student_model = SparseEncoder("distilbert/distilbert-base-uncased")
teacher_model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# Prepare dataset
train_dataset = Dataset.from_dict({
    "query": ["What is machine learning?", "How to train models?"],
    "passage1": ["ML is a branch of AI.", "Training involves optimization."],
    "passage2": ["ML uses algorithms.", "Models learn from data."],
})

# Compute teacher labels (margin)
def compute_labels(batch):
    emb_q = teacher_model.encode(batch["query"])
    emb_p1 = teacher_model.encode(batch["passage1"])
    emb_p2 = teacher_model.encode(batch["passage2"])
    # similarity function returns scalar
    return {
      "label": teacher_model.similarity_pairwise(emb_q, emb_p1) - teacher_model.similarity_pairwise(emb_q, emb_p2)
    }

train_dataset = train_dataset.map(compute_labels, batched=True)

# Loss config
loss = losses.SpladeLoss(
    student_model,
    loss=losses.SparseMarginMSELoss(student_model),
    document_regularizer_weight=3e-5,
    query_regularizer_weight=5e-5,
    document_regularizer_threshold=50,
)

# Trainer
trainer = SparseEncoderTrainer(
    model=student_model,
    train_dataset=train_dataset,
    loss=loss,
)
trainer.train()
```

### Example Using CSRLoss

```python
from datasets import Dataset
from sentence_transformers.sparse_encoder import SparseEncoder, SparseEncoderTrainer, losses

# Model with sparse autoencoder
model = SparseEncoder("sentence-transformers/all-MiniLM-L6-v2")

# Prepare dataset
train_dataset = Dataset.from_dict({
    "anchor": ["Machine learning is fascinating.", "I love programming."],
    "positive": ["AI is interesting.", "Coding is fun."],
    "negative": ["I don't like sports.", "Weather is bad today."],
})

# Setup CSRLoss with reconstruction + contrastive main loss
loss = losses.CSRLoss(
    model,
    loss=losses.SparseMultipleNegativesRankingLoss(model),
    beta=0.1,
    gamma=1.0,
)

trainer = SparseEncoderTrainer(
    model=model,
    train_dataset=train_dataset,
    loss=loss,
)
trainer.train()
```

Sources: [sentence_transformers/sparse_encoder/losses/splade.py:68-102](), [sentence_transformers/sparse_encoder/losses/csr.py:161-179]()

---

## Implementation Details

### Loss Return Format

Loss functions in the sparse encoder system return either:

1. A single scalar tensor (for backward compatibility and simplicity)  
2. A dictionary mapping names to scalar loss components

Wrapper losses that return dictionaries enable flexible monitoring and weighted aggregation during training.

**Example output from `SpladeLoss`:**

```python
{
    "base_loss": tensor(0.523),
    "document_regularizer_loss": tensor(0.042),   # = unscaled_loss * document_regularizer_weight
    "query_regularizer_loss": tensor(0.067),      # = unscaled_loss * query_regularizer_weight
}
# Final train loss = 0.523 + 0.042 + 0.067 = 0.632
```

### `compute_loss_from_embeddings` Method

Main losses define this method to compute their loss from embeddings and optional labels:

```python
def compute_loss_from_embeddings(
    self,
    embeddings: list[torch.Tensor],
    labels: torch.Tensor | None = None,
) -> torch.Tensor | dict[str, torch.Tensor]:
    """
    Args:
        embeddings: One tensor per input column (e.g., queries, docs).
        labels: Optional labels tensor.

    Returns:
        A scalar tensor or a dictionary of loss components.
    """
```

Wrapper losses call this method on their main loss and regularizers, allowing shared embedding computation and modular composition.

Sources: [sentence_transformers/sparse_encoder/losses/splade.py:137-162](), [sentence_transformers/sparse_encoder/losses/csr.py:189-206]()

---

## Summary Table of Loss Functions

| Loss Class                        | Wrapper Required | Input Data Format                                   | Labels                         | Primary Use Case                        |
|----------------------------------|------------------|----------------------------------------------------|--------------------------------|---------------------------------------|
| `SpladeLoss`                     | No (is a wrapper) | Any                                                | Any                            | General SPLADE sparse encoder training|
| `CSRLoss`                       | No (is a wrapper) | Any                                                | Any                            | SparseAutoEncoder models               |
| `SparseMultipleNegativesRankingLoss` | Yes (Splade/CSR) | `(anchor, positive)(+ negatives)` pairs/tuples    | None                           | Default contrastive retrieval loss    |
| `SparseCoSENTLoss`                | Yes (Splade/CSR) | `(sent_A, sent_B)` pairs                            | Float similarity in [0,1]      | Regression for semantic similarity    |
| `SparseAnglELoss`                 | Yes (Splade/CSR) | `(sent_A, sent_B)` pairs                            | Float similarity in [0,1]      | Advanced regression loss               |
| `SparseCosineSimilarityLoss`      | Yes (Splade/CSR) | `(sent_A, sent_B)` pairs                            | Float similarity in [0,1]      | Classic similarity regression         |
| `SparseTripletLoss`               | Yes (Splade/CSR) | `(anchor, positive, negative)` triplets            | None                           | Margin-based triplet learning          |
| `SparseMSELoss`                  | No (standalone)   | Sentences / teacher embeddings                      | Teacher sparse embeddings      | Embedding-level knowledge distillation|
| `SparseMarginMSELoss`             | Yes (Splade/CSR) | Triplets + margin scores                             | Teacher margin scores          | Margin distillation                    |
| `SparseDistillKLDivLoss`          | Yes (Splade/CSR) | Triplets + probability distributions                | Teacher softscores             | Probability distillation               |
| `FlopsLoss`                     | No (regularizer)  | N/A                                                | N/A                           | Sparsity regularization                |
| `CSRReconstructionLoss`           | No (internal)     | N/A                                                | N/A                           | Autoencoder reconstruction             |

Sources: [sentence_transformers/sparse_encoder/losses/__init__.py:1-29](), [docs/sparse_encoder/loss_overview.md:1-86]()

---

# Bridging Natural Language Concepts with Code Entities: Architecture and Loss Associations

```mermaid
graph LR
    subgraph Natural_Language_Space
      NL_SparseTraining["Sparse Model Training"]
      NL_SparsityControl["Sparsity Regularization"]
      NL_SemanticLearning["Semantic Representation Learning"]
      NL_Distillation["Knowledge Distillation"]
      NL_DataFormats["Training Data Formats"]
    end
    
    subgraph Code_Entity_Space
      SE_SparseEncoder["class SparseEncoder"]
      SE_SpladeLoss["class SpladeLoss"]
      SE_CSRLoss["class CSRLoss"]
      SE_FlopsLoss["class FlopsLoss"]
      SE_SparseMSELoss["class SparseMSELoss"]
      SE_SparseMarginMSELoss["class SparseMarginMSELoss"]
      SE_SparseMultipleNegatives["SparseMultipleNegativesRankingLoss"]
      SE_SparseDistillKLDivLoss["SparseDistillKLDivLoss"]
      SE_SparseCoSENTLoss["SparseCoSENTLoss"]
      SE_Trainer["class SparseEncoderTrainer"]
    end

    NL_SparseTraining -->|trained by| SE_Trainer
    NL_SparseTraining -->|uses wrapper| SE_SpladeLoss
    NL_SparseTraining -->|or wrapper| SE_CSRLoss

    NL_SparsityControl -->|implemented by| SE_FlopsLoss
    NL_SparsityControl -->|enforced by| SE_SpladeLoss
    NL_SparsityControl -->|enforced by| SE_CSRLoss

    NL_SemanticLearning -->|performed by| SE_SparseMultipleNegatives
    NL_SemanticLearning -->|performed by| SE_SparseMarginMSELoss
    NL_SemanticLearning -->|performed by| SE_SparseCoSENTLoss
    NL_SemanticLearning -->|performed by| SE_SparseDistillKLDivLoss

    NL_Distillation -->|loss| SE_SparseMSELoss
    NL_Distillation -->|loss| SE_SparseMarginMSELoss
    NL_Distillation -->|loss| SE_SparseDistillKLDivLoss

    NL_DataFormats -->|inputs for| SE_SpladeLoss
    NL_DataFormats -->|inputs for| SE_CSRLoss
```

# Bridging Natural Language Concepts with Code Entities: Loss Usage and Selection

```mermaid
graph TB
   DataFormat["User's Training Data Format"]
   
   AnchorPosPairs["(anchor, positive) pairs"]
   Triplets["(anchor, positive, negative) triplets"]
   SimilarityPairs["(sent_A, sent_B) with similarity scores"]
   TeacherEmbeddings["Teacher embeddings for distillation"]
   AutoEncoder["Using SparseAutoEncoder module?"]
   
   WrapperLossChoice["Select Wrapper Loss"]
   SpladeLossNode["SpladeLoss (MLMTransformer + SpladePooling)"]
   CSRLossNode["CSRLoss (SparseAutoEncoder)"]
   
   MainLossChoice["Select Main Loss"]
   SMNRLoss["SparseMultipleNegativesRankingLoss"]
   TripletLoss["SparseTripletLoss"]
   CoSENTLoss["SparseCoSENTLoss / SparseAnglELoss / SparseCosineSimilarityLoss"]
   SparseMSE["SparseMSELoss (standalone)"]
   MarginMSE["SparseMarginMSELoss"]
   KLDivLoss["SparseDistillKLDivLoss"]
   
   DataFormat --> AutoEncoder
   AutoEncoder -->|Yes| CSRLossNode
   AutoEncoder -->|No| WrapperLossChoice
   WrapperLossChoice --> SpladeLossNode
   
   DataFormat --> AnchorPosPairs
   DataFormat --> Triplets
   DataFormat --> SimilarityPairs
   DataFormat --> TeacherEmbeddings
   
   AnchorPosPairs --> MainLossChoice
   Triplets --> MainLossChoice
   SimilarityPairs --> MainLossChoice
   TeacherEmbeddings --> MainLossChoice
   
   MainLossChoice --> SMNRLoss
   MainLossChoice --> TripletLoss
   MainLossChoice --> CoSENTLoss
   
   TeacherEmbeddings -->|"Distillation Type?"| DistillType
   DistillType(("Distillation Type"))
   
   DistillType -->|Embedding-level| SparseMSE
   DistillType -->|Margin-based| MarginMSE
   DistillType -->|Probability-based| KLDivLoss
```

---

# Summary

This documentation outlined the sparse encoder loss function ecosystem:

- Wrapper losses (`SpladeLoss`, `CSRLoss`) combine main semantic losses and sparsity regularizers.  
- Main losses include contrastive, triplet, regression, and distillation variants tailored for sparse embeddings.  
- Regularizers such as `FlopsLoss` promote sparse and efficient vector representations.  
- The choice of loss depends on model architecture and available training data format.  
- Distillation losses provide advanced knowledge transfer mechanisms.

This modular design supports flexible, efficient training of sparse retrieval models aligned with recent research innovations.

---

Sources:  
- docs/sparse_encoder/loss_overview.md  
- sentence_transformers/sparse_encoder/losses/__init__.py  
- sentence_transformers/sparse_encoder/losses/splade.py  
- sentence_transformers/sparse_encoder/losses/csr.py  
- sentence_transformers/sparse_encoder/losses/flops.py  
- sentence_transformers/sparse_encoder/losses/sparse_mse.py  
- sentence_transformers/sparse_encoder/losses/sparse_margin_mse.py  
- sentence_transformers/sparse_encoder/losses/sparse_distill_kl_div.py

---

