<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/jacobian-lens · page 2 Core Library (`jlens`) · fetched 2026-10-26 -->

# Core Library (`jlens`)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jlens/__init__.py](jlens/__init__.py)
- [jlens/_logging.py](jlens/_logging.py)

</details>



The `jlens` package provides the core infrastructure for fitting and applying Jacobian lenses to transformer models. It is designed to be model-agnostic via a protocol-based interface, while providing first-class support for HuggingFace Transformers.

The library is organized into four primary functional subsystems that manage the lifecycle of a lens: from defining model interfaces and recording activations to fitting the Jacobian matrices and visualizing the resulting token-space projections.

### Package Architecture

The following diagram illustrates how the core entities in the `jlens` package interact to transform raw model activations into interpretable token rankings.

**System Overview: From Model to Visualization**
```mermaid
graph TD
    subgraph "Model Interface Space"
        A["LensModel (Protocol)"] <|-- B["HFLensModel (Adapter)"]
        C["Layout (Dataclass)"] --> B
    end

    subgraph "Data Acquisition Space"
        B --> D["ActivationRecorder (Context Manager)"]
        D --> E["Hidden States / Residuals"]
    end

    subgraph "Mathematical Fitting Space"
        E --> F["jacobian_for_prompt()"]
        F --> G["fit()"]
        G --> H["JacobianLens (Artifact)"]
    end

    subgraph "Application & Analysis Space"
        H --> I["JacobianLens.apply()"]
        H --> J["compute_slice()"]
        J --> K["SliceData / HTML Page"]
    end

    style A stroke-dasharray: 5 5
```
**Sources:** [jlens/__init__.py:6-23](), [jlens/protocol.py:1-40](), [jlens/lens.py:1-15]()

---

### 2.1 Model Protocol and HuggingFace Adapter
To ensure compatibility across different model architectures, `jlens` uses a structural typing approach. The `LensModel` protocol defines the minimum set of methods and attributes a model must provide (e.g., `embed`, `unembed`, `layers`). 

The `HFLensModel` class serves as the primary implementation, wrapping `transformers` library models. It utilizes a `Layout` dataclass to map the internal module tree of various model families (Llama, Qwen, Mistral, etc.) to a standardized format. The `from_hf()` factory function automates this mapping by detecting the model type.

For details, see [Model Protocol and HuggingFace Adapter](#2.1).

**Sources:** [jlens/hf.py:1-50](), [jlens/protocol.py:1-40]()

---

### 2.2 Activation Recording and Hooks
The `ActivationRecorder` is a context manager used to capture the internal state of a model during a forward pass. It non-destructively attaches forward hooks to the residual blocks identified in the model's `Layout`. 

Beyond simple capture, the recorder is responsible for rooting the autograd graph at specific layers. This allows the library to compute gradients (and thus the Jacobian) efficiently by only backpropagating from the output to the target layer, rather than through the entire network.

For details, see [Activation Recording and Hooks](#2.2).

**Sources:** [jlens/hooks.py:1-60]()

---

### 2.3 Fitting the Jacobian Lens
The core mathematical contribution of the library is the estimation of the average input-output Jacobian $J_l$. This is handled by two main functions:
- `jacobian_for_prompt()`: Performs batched backward passes using one-hot cotangents to calculate the Jacobian for a single sequence.
- `fit()`: Orchestrates the fitting process over a large corpus, managing running means, checkpointing, and resumption.

The fitting process results in a `JacobianLens` object containing a matrix for each layer of the model.

For details, see [Fitting the Jacobian Lens](#2.3).

**Sources:** [jlens/fitting.py:1-100]()

---

### 2.4 Applying the Lens (`JacobianLens`)
The `JacobianLens` class is the central artifact of the library. It stores the fitted matrices and provides the `transport()` method to project hidden states from any layer into the final vocabulary space.

The class supports an `apply()` method that mimics a forward pass but includes the Jacobian transport and unembedding steps. It also features a "logit-lens" mode (`use_jacobian=False`) which serves as a baseline by skipping the Jacobian transformation and passing residuals directly to the unembedding head.

For details, see [Applying the Lens (`JacobianLens`)](#2.4).

**Sources:** [jlens/lens.py:1-120]()

---

### 2.5 Slice Visualization (`jlens.vis`)
To interpret the results, the `jlens.vis` module converts high-dimensional data into interactive visualizations. The `compute_slice()` function builds a `SliceData` object representing a grid of token ranks across every position and layer of a prompt.

The library supports rendering these slices as interactive HTML pages using D3.js. These can be embedded directly in notebooks via `notebook_iframe()` or saved as standalone files with sidecar data for large-scale analysis.

For details, see [Slice Visualization (`jlens.vis`)](#2.5).

**Sources:** [jlens/vis/compute.py:1-50](), [jlens/vis/page.py:1-80]()

---

### 2.6 Example Prompts and Data
The library includes a set of curated examples in `jlens/examples.py` to demonstrate specific behaviors like multi-hop reasoning or "top-down" information summoning. These are provided as `Example` dataclasses that can be easily formatted using `resolve_prompt()` to match a specific model's chat template.

For details, see [Example Prompts and Data](#2.6).

**Sources:** [jlens/examples.py:1-100]()

---

### Utility: Logging
The library provides an opt-in logging helper, `configure_logging`, which formats stderr output with elapsed time and delta time between log entries. This is particularly useful for monitoring long-running `fit()` operations in notebooks or scripts.

**Sources:** [jlens/_logging.py:1-54]()

---

