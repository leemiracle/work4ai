<!-- source: DeepWiki mcp.deepwiki.com · repo openai/circuit_sparsity · page 5 Data Management and Utilities · fetched 2026-10-26 -->

# Data Management and Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [circuit_sparsity/registries.py](circuit_sparsity/registries.py)

</details>



This page documents the data structures, utility functions, and configuration constants defined in [`circuit_sparsity/registries.py`](circuit_sparsity/registries.py:1-206)(). These components provide the foundational layer for managing experimental data, computing loss functions, and performing common data transformations across the codebase.

For information about tokenization specifics, see [5.3](#5.3). For loss function details, see [5.2](#5.2). For the complete utility function reference, see [5.4](#5.4).

## Data Directory Structure

The repository uses a standardized directory layout for storing models, visualization artifacts, and training metrics on Azure Blob Storage. All paths are relative to the base URL defined in `MODEL_BASE_DIR`.

### Storage Layout Diagram

```mermaid
graph TB
    BASE["MODEL_BASE_DIR<br/>openaipublic.blob.core.windows.net/circuit-sparsity"]
    
    subgraph "models/"
        MODEL_DIR["models/{model_name}/"]
        BEEG["beeg_config.json<br/>GPTConfig serialization"]
        FINAL["final_model.pt<br/>Model checkpoint"]
    end
    
    subgraph "viz/"
        VIZ_PATH["viz/{experiment}/{model}/{task}/{sweep}/{k}/"]
        VIZ_DATA["viz_data.pkl<br/>Circuit masks, activations,<br/>samples, importances"]
        VIZ_EXTRA["Additional artifacts<br/>masks, histograms, buckets"]
    end
    
    subgraph "train_curves/"
        CURVES["train_curves/{model_name}/"]
        PROGRESS["progress.json<br/>Training metrics"]
    end
    
    subgraph "Local Cache"
        CACHE["CACHE_DIR<br/>~/data/dev/shm/cache"]
        CACHED_FILES["Cached remote files"]
    end
    
    BASE --> MODEL_DIR
    BASE --> VIZ_PATH
    BASE --> CURVES
    
    MODEL_DIR --> BEEG
    MODEL_DIR --> FINAL
    
    VIZ_PATH --> VIZ_DATA
    VIZ_PATH --> VIZ_EXTRA
    
    CURVES --> PROGRESS
    
    BASE -.fetched to.-> CACHE
    CACHE --> CACHED_FILES
```

**Sources:** [circuit_sparsity/registries.py:12-13](), [README.md:68-84]()

### Path Components

| Component | Purpose | Example |
|-----------|---------|---------|
| `{model_name}` | Identifies trained model checkpoint | `csp_yolo2`, `csp_sweep1_1x_l0200_afrac0.75` |
| `{experiment}` | Groups related experiments | `csp_yolo1`, `csp_bridge1` |
| `{task}` | Specifies the evaluation task | `bracket_counting`, `single_double_quote` |
| `{sweep}` | Pruning algorithm variant | `prune_v4`, `prune_v5_logitscaling` |
| `{k}` | Node budget for circuit | `1024`, `2048`, `4096` |

**Sources:** [README.md:68-85]()

## Core Data Structures

The `registries` module defines two primary dataclasses that structure experimental data throughout the codebase.

### Datapoint Class

```mermaid
classDiagram
    class Datapoint {
        +Tensor inputs
        +Tensor patch_from_inputs
        +Tensor pretrain_inputs
        +int target_tokid
        +int target_alt_tokid
    }
    
    class Task {
        +list~Datapoint~ xs
        +list~Datapoint~ xs_test
        +Callable loss_fn
        +Encoding enc
        +limit(n: int) Task
        +left_truncate_to_len(n: int) Task
    }
    
    Task "1" --> "*" Datapoint : contains
    Task --> "1" last_token_contrast_loss_fn : uses
```

**Sources:** [circuit_sparsity/registries.py:15-27]()

The `Datapoint` class encapsulates a single training or evaluation example:

| Field | Type | Purpose |
|-------|------|---------|
| `inputs` | `torch.Tensor` | Primary input token sequence, shape `(1, seq_len)` |
| `patch_from_inputs` | `torch.Tensor \| None` | Alternative input for patching/ablation experiments |
| `pretrain_inputs` | `torch.Tensor \| None` | Pretraining inputs (deprecated, used for scrubbing) |
| `target_tokid` | `int \| None` | Token ID of correct prediction |
| `target_alt_tokid` | `int \| None` | Token ID of incorrect alternative |

**Code Reference:** [circuit_sparsity/registries.py:16-27]()

### Task Class

The `Task` class groups datapoints with their associated loss function and tokenizer:

| Field | Type | Purpose |
|-------|------|---------|
| `xs` | `list[Datapoint]` | Training/evaluation datapoints (shuffled with seed 0) |
| `xs_test` | `list[Datapoint]` | Held-out test datapoints (shuffled with seed 0) |
| `loss_fn` | `Callable` | Loss function (typically `last_token_contrast_loss_fn`) |
| `enc` | `tiktoken.Encoding` | Tokenizer for decoding/encoding text |

**Code Reference:** [circuit_sparsity/registries.py:89-128]()

The `Task` class provides two transformation methods:

- **`limit(n: int) -> Task`**: Returns a new task with only the first `n` examples from both `xs` and `xs_test`
- **`left_truncate_to_len(n: int) -> Task`**: Truncates all input sequences to the last `n` tokens, preserving the final tokens

**Sources:** [circuit_sparsity/registries.py:101-128]()

### Data Flow in Task Processing

```mermaid
graph LR
    JSONL["JSONL files<br/>load_jsonls()"]
    OBS["dset_obs<br/>list of dicts"]
    XS["xs: list[Datapoint]<br/>get_xs_simple()"]
    TASK["Task<br/>xs, xs_test, loss_fn, enc"]
    
    JSONL -->|"read_file_cached()"| OBS
    OBS -->|"create Datapoint"| XS
    XS -->|"__post_init__<br/>shuffle(seed=0)"| TASK
    
    TASK -->|"limit(n)"| TASK_LIM["Limited Task<br/>First n examples"]
    TASK -->|"left_truncate_to_len(n)"| TASK_TRUNC["Truncated Task<br/>Last n tokens"]
```

**Sources:** [circuit_sparsity/registries.py:89-197]()

## Configuration Constants

Two module-level constants configure data access:

```python
MODEL_BASE_DIR = "https://openaipublic.blob.core.windows.net/circuit-sparsity"
CACHE_DIR = os.path.expanduser("~/data/dev/shm/cache")
```

- **`MODEL_BASE_DIR`**: Base URL for all remote data (models, visualization artifacts, training curves)
- **`CACHE_DIR`**: Local filesystem path where `tiktoken` and visualization data are cached

**Sources:** [circuit_sparsity/registries.py:12-13]()

## Loss Function Details

The primary loss function is `last_token_contrast_loss_fn`, which computes a contrastive loss on the final token prediction.

### Function Signature

```
last_token_contrast_loss_fn(
    x: Datapoint,
    logits: torch.Tensor,
    *,
    tokid: int | None = None,
    two_sided: bool = True,
    alt_tokid: int | None = None,
) -> torch.Tensor
```

**Sources:** [circuit_sparsity/registries.py:29-87]()

### Loss Computation Logic

```mermaid
graph TB
    START["Input: Datapoint x, logits"]
    
    CHECK_TWO["two_sided == True?"]
    UNPACK["logits_patched, logits_clean = logits"]
    SINGLE["logits_patched = logits"]
    
    CHECK_ALT["alt_tokid provided?"]
    
    TWO_TOKEN["Two-token softmax<br/>logps over [tokid, alt_tokid]"]
    TWO_LOSS["-(logps_patched[-1, 0] +<br/>logps_clean[-1, 1])"]
    
    FULL_VOCAB["Full vocabulary softmax"]
    FULL_LOSS["-(logps_patched[-1, tokid] +<br/>logsumexp(logps_clean[-1, all except tokid]))"]
    
    RETURN["Return loss"]
    
    START --> CHECK_TWO
    CHECK_TWO -->|Yes| UNPACK
    CHECK_TWO -->|No| SINGLE
    
    UNPACK --> CHECK_ALT
    SINGLE --> CHECK_ALT
    
    CHECK_ALT -->|Yes| TWO_TOKEN
    CHECK_ALT -->|No| FULL_VOCAB
    
    TWO_TOKEN --> TWO_LOSS
    FULL_VOCAB --> FULL_LOSS
    
    TWO_LOSS --> RETURN
    FULL_LOSS --> RETURN
```

**Sources:** [circuit_sparsity/registries.py:29-87]()

### Loss Components

| Mode | Purpose | Loss Calculation |
|------|---------|------------------|
| **Two-sided** | Maximize correct token prob on patched input AND minimize correct token prob on clean input | Contrastive: encourage opposite predictions |
| **Two-token** | Compare only target vs alternative | `log_softmax` over `[tokid, alt_tokid]` |
| **Full vocabulary** | Compare target vs all other tokens | `log_softmax` over entire vocabulary |

The function prioritizes `x.target_tokid` and `x.target_alt_tokid` if set, otherwise uses the explicit `tokid` and `alt_tokid` parameters.

**Sources:** [circuit_sparsity/registries.py:29-87]()

## Utility Functions

The `registries` module provides several helper functions for data manipulation and transformation.

### Data Processing Utilities

```mermaid
graph LR
    subgraph "List Operations"
        LIST_JOIN["list_join(xss)<br/>Flatten nested lists"]
        ONLY_ONE["only_one(xs)<br/>Assert single element"]
    end
    
    subgraph "Dictionary Operations"
        KEYMAP["keymap(fs, d)<br/>Apply functions to dict values"]
    end
    
    subgraph "Tensor Operations"
        PAD_CLIP["pad_or_clip_to_len(x, n, v)<br/>Left-pad or right-clip"]
    end
    
    subgraph "File Operations"
        LOAD_JSONLS["load_jsonls(paths)<br/>Load multiple JSONL files"]
    end
    
    subgraph "Functional Composition"
        LCOMPOSE["lcompose(*fs)<br/>Left-to-right composition"]
    end
```

**Sources:** [circuit_sparsity/registries.py:150-206]()

### Function Reference Table

| Function | Signature | Purpose |
|----------|-----------|---------|
| `list_join` | `(xss: list[list]) -> list` | Flattens nested lists (monadic join) |
| `keymap` | `(fs: dict[str, Callable], d: dict) -> dict` | Applies functions to dictionary values by key |
| `load_jsonls` | `(paths) -> list` | Loads and parses multiple JSONL files using `read_file_cached` |
| `pad_or_clip_to_len` | `(x, n, v) -> Tensor` | Left-pads with value `v` or right-clips tensor `x` to length `n` |
| `only_one` | `(xs) -> Any` | Asserts list has exactly one element and returns it |
| `get_xs_simple` | `(dset_obs) -> list[Datapoint]` | Converts dataset observations to `Datapoint` objects |
| `lcompose` | `(*fs) -> Callable` | Left-to-right function composition |

**Sources:** [circuit_sparsity/registries.py:150-206]()

### Retokenization

The `make_retokenizer` function creates a callable that converts token sequences from one encoding to another:

```mermaid
graph LR
    OLD_ENC["old_enc.decode(tokens)"]
    TEXT["Decoded text string"]
    NEW_ENC["enc.encode(text)"]
    NEW_TOKENS["New token sequence"]
    
    OLD_ENC --> TEXT
    TEXT --> NEW_ENC
    NEW_ENC --> NEW_TOKENS
    
    TENSOR_CHECK{"Input is<br/>torch.Tensor?"}
    UNWRAP["x.tolist()"]
    REWRAP["torch.tensor(result)"]
    
    TENSOR_CHECK -->|Yes| UNWRAP
    UNWRAP --> OLD_ENC
    NEW_TOKENS --> REWRAP
    
    TENSOR_CHECK -->|No| OLD_ENC
```

The retokenizer handles both list and `torch.Tensor` inputs, automatically converting between formats. It supports nested lists for batch processing.

**Sources:** [circuit_sparsity/registries.py:130-148]()

### Example: pad_or_clip_to_len Usage

This function is particularly useful for ensuring consistent sequence lengths:

```python
# If x has shape (120,) and n=256, v=0:
# Result: tensor([0, 0, ..., 0, x[0], x[1], ..., x[119]])  # 136 zeros prepended

# If x has shape (300,) and n=256:
# Result: x[-256:]  # Last 256 elements (left-clipped)
```

The function always preserves the **rightmost** (final) tokens when clipping, which is important for language models where the final tokens typically contain the prediction target.

**Sources:** [circuit_sparsity/registries.py:169-183]()

---

