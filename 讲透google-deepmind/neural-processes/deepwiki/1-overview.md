<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/neural-processes · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [attentive_neural_process.ipynb](attentive_neural_process.ipynb)
- [conditional_neural_process.ipynb](conditional_neural_process.ipynb)

</details>



This page describes the `google-deepmind/neural-processes` repository: its purpose, the three model variants it implements, their academic origins, and how the two Jupyter notebooks are organized. For environment setup and execution instructions, see [Getting Started](#1.1). For architecture details of each model, see [CNP Architecture](#2.1) and [ANP Architecture](#3.1).

---

## Repository Purpose

This repository provides self-contained, executable implementations of the **Neural Process** family of models, designed for 1D regression tasks. The models learn a distribution over functions from context point observations and predict outputs at target locations — analogous to Gaussian Processes, but with learned, amortized inference via neural networks.

There are two notebooks:

| Notebook | Models | Framework |
|---|---|---|
| `conditional_neural_process.ipynb` | CNP | TensorFlow 1.x + Keras |
| `attentive_neural_process.ipynb` | NP, ANP | TensorFlow 1.x (low-level) |

---

## Model Family and Academic Lineage

The three model variants form a lineage where each extends the previous by adding a key capability.

**Diagram: Model Family — Papers, Models, and Code Classes**

```mermaid
graph LR
  P1["\"Garnelo et al., ICML 2018\narxiv:1807.01613\""]
  P2["\"Garnelo et al., ICML Workshop 2018\narxiv:1807.01622\""]
  P3["\"Kim et al., ICLR 2019\narxiv:1901.05761\""]

  CNP["\"CNP\nConditionalNeuralProcess (Keras)\nconditional_neural_process.ipynb\""]
  NP["\"NP\nLatentModel(use_deterministic_path=True,\nattention=uniform)\nattentive_neural_process.ipynb\""]
  ANP["\"ANP\nLatentModel(use_deterministic_path=True,\nattention=multihead)\nattentive_neural_process.ipynb\""]

  P1 --> CNP
  P2 --> NP
  P3 --> ANP

  CNP -->|"adds LatentEncoder (z)"| NP
  NP -->|"replaces uniform_attention\nwith multihead_attention"| ANP
```

Sources: [README.md:1-17](), [attentive_neural_process.ipynb:583-682]()

| Model | Key Innovation | Notebook | Core Class |
|---|---|---|---|
| CNP | Deterministic encoder + mean aggregation | `conditional_neural_process.ipynb` | `ConditionalNeuralProcess` |
| NP | Adds latent variable `z` via `LatentEncoder` | `attentive_neural_process.ipynb` | `LatentModel` (uniform attention) |
| ANP | Replaces mean aggregation with cross-attention | `attentive_neural_process.ipynb` | `LatentModel` (multihead attention) |

---

## Repository File Map

**Diagram: Files and Their Primary Code Entities**

```mermaid
graph TD
  subgraph NB1["\"conditional_neural_process.ipynb\""]
    E1["\"Encoder\""]
    D1["\"Decoder\""]
    M1["\"ConditionalNeuralProcess\""]
    E1 --> M1
    D1 --> M1
  end

  subgraph NB2["\"attentive_neural_process.ipynb\""]
    GC["\"GPCurvesReader\n.generate_curves()\""]
    DE["\"DeterministicEncoder\""]
    LE["\"LatentEncoder\""]
    ATT["\"Attention\n(uniform/laplace/dot_product/multihead)\""]
    DEC["\"Decoder\""]
    LM["\"LatentModel\""]
    PF["\"plot_functions()\""]
    DE --> LM
    LE --> LM
    ATT --> DE
    DEC --> LM
  end

  README["\"README.md\""]
  CONTRIB["\"CONTRIBUTING.md\""]
  LICENSE["\"LICENSE (Apache 2.0)\""]
```

Sources: [README.md:1-59](), [attentive_neural_process.ipynb:101-103](), [attentive_neural_process.ipynb:375-418](), [attentive_neural_process.ipynb:439-492](), [attentive_neural_process.ipynb:513-562](), [attentive_neural_process.ipynb:583-682](), [attentive_neural_process.ipynb:821-890]()

---

## Notebook Summaries

### `conditional_neural_process.ipynb` — CNP

Implements the Conditional Neural Process using TensorFlow 1.x and Keras. Data is generated from random sine waves. The model encodes context points with a shared MLP (`Encoder`), mean-aggregates the representations into a global context vector `r`, then decodes at target locations with `Decoder`.

The output is a `tfd.MultivariateNormalDiag` distribution parameterized by predicted `mu` and `sigma`. Training uses negative log-likelihood via `log_prob` and `tf.GradientTape` with Adam.

For full architecture detail, see [CNP Architecture](#2.1). For the training loop, see [CNP Training and Evaluation](#2.2).

---

### `attentive_neural_process.ipynb` — NP and ANP

Implements both the Neural Process and Attentive Neural Process in a single notebook using TensorFlow 1.x. The key class is `LatentModel`, which is configured at construction time to select between NP and ANP behavior via the `attention` argument.

**Data generation** uses `GPCurvesReader.generate_curves()`, which samples from a Gaussian Process with a squared-exponential kernel. Each call returns an `NPRegressionDescription` namedtuple:

| Field | Description |
|---|---|
| `query` | Tuple of `((context_x, context_y), target_x)` |
| `target_y` | Ground truth y at target locations |
| `num_total_points` | Total number of data points |
| `num_context_points` | Number of context points |

Sources: [attentive_neural_process.ipynb:90-103](), [attentive_neural_process.ipynb:106-270]()

**NP mode** uses `Attention(rep='identity', att_type='uniform')` — equivalent to mean aggregation over context representations.

**ANP mode** uses `Attention(rep='mlp', att_type='multihead')` — full cross-attention with learned projections.

The `use_deterministic_path` constructor flag on `LatentModel` controls whether the deterministic encoder path is active alongside the latent path.

For full architecture detail, see [ANP Architecture](#3.1). For attention types, see [Attention Mechanisms](#3.2). For training details, see [ANP Training and Inference](#3.3).

---

## Shared Training Paradigm

Both notebooks follow the same conceptual training loop despite differing frameworks and model architectures.

**Diagram: Shared Training Loop — Mapping to Code**

```mermaid
flowchart LR
  DG["\"Data Generation\nGPCurvesReader.generate_curves()\nor generate_curve_data()\""]
  FWD["\"Forward Pass\nLatentModel.__call__(query, num_targets, target_y)\nor ConditionalNeuralProcess(context, query)\""]
  LOSS["\"Loss\n-log_prob(target_y)\n(NP/ANP: ELBO = log_p - KL/num_targets)\""]
  OPT["\"Optimizer\ntf.train.AdamOptimizer(1e-4)\nor tf.GradientTape + Adam\""]
  VIZ["\"Visualization\nplot_functions(target_x, target_y,\ncontext_x, context_y, pred_y, std)\nor plot_predictions()\""]

  DG --> FWD --> LOSS --> OPT
  OPT -->|"next step"| DG
  OPT -.->|"every PLOT_AFTER steps"| VIZ
```

Sources: [attentive_neural_process.ipynb:911-1085](), [attentive_neural_process.ipynb:912-948]()

Key training hyperparameters shared across both notebooks:

| Parameter | Typical Value | Purpose |
|---|---|---|
| `TRAINING_ITERATIONS` | 100,000 | Total gradient steps |
| `MAX_CONTEXT_POINTS` | 50 | Upper bound on context and target size |
| `PLOT_AFTER` | 10,000 | Interval between visualization outputs |
| `HIDDEN_SIZE` | 128 | Hidden layer size for all MLPs and latent dim |

Sources: [attentive_neural_process.ipynb:1011-1017]()

---

## Key Differences Between Notebooks

| Aspect | `conditional_neural_process.ipynb` | `attentive_neural_process.ipynb` |
|---|---|---|
| Models | CNP only | NP and ANP |
| Framework style | Keras `Model` subclass | Plain Python classes (`__call__`) |
| Data source | Random sine waves | GP with squared-exponential kernel |
| Latent variable | None | `LatentEncoder` → `z` |
| Context aggregation | Fixed mean pooling | `Attention` module (configurable) |
| Loss | NLL: `-log_prob(target_y)` | ELBO: `log_p - KL / num_targets` |
| Training | `tf.GradientTape` + Adam | `tf.train.AdamOptimizer` + session |

Sources: [README.md:9-17](), [attentive_neural_process.ipynb:38-42]()

---

