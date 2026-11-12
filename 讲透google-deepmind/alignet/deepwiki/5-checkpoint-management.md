<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alignet · page 5 Checkpoint Management · fetched 2026-10-26 -->

# Checkpoint Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [bv_utils.py](bv_utils.py)
- [bv_vit.py](bv_vit.py)

</details>



The checkpoint management system provides utilities for loading, merging, and converting pre-trained model parameters from various formats and sources. This system enables the AligNet training pipeline to initialize models from checkpoints produced by Big Vision and other frameworks, handling format differences, structural mismatches, and resolution changes automatically.

This page covers the complete checkpoint loading and management infrastructure. For information about how checkpoints are used during model initialization in Kauldron, see [Kauldron Integration Wrappers](#4.4). For details about the training configuration that specifies which checkpoints to load, see [Training Configuration](#6.1).

## Overview

The checkpoint management system handles three primary challenges:

1. **Format Detection and Loading**: Automatically detecting and loading checkpoints from `.npz` (NumPy) or TensorStore formats
2. **Parameter Structure Alignment**: Merging loaded parameters with initialized model parameters, handling structural mismatches
3. **Format Conversion**: Converting between `scan` and `pyloop` encoder representations

```mermaid
graph TB
    subgraph "Input Sources"
        NPZ["checkpoint.npz<br/>NumPy format"]
        TS["checkpoint-dir/<br/>TensorStore format"]
        VANITY["Vanity Name<br/>e.g. 'SigLIP B/16 224'"]
    end
    
    subgraph "bv_utils.py Core Functions"
        LOAD_PARAMS["load_params()<br/>Main entry point<br/>Lines 211-266"]
        LOAD_NP["load_checkpoint_np()<br/>Lines 269-282"]
        LOAD_TS["load_checkpoint_ts()<br/>Lines 285-297"]
        TSLOAD["tsload()<br/>Low-level TensorStore<br/>Lines 300-353"]
    end
    
    subgraph "Format & Structure Processing"
        RECOVER_DTYPE["recover_dtype()<br/>Fix bfloat16<br/>Lines 412-418"]
        MERGE["merge_params()<br/>Align structures<br/>Lines 43-123"]
        PYLOOP_SCAN["pyloop_to_scan()<br/>Lines 458-482"]
        SCAN_PYLOOP["scan_to_pyloop()<br/>Lines 485-501"]
    end
    
    subgraph "bv_vit.py Functions"
        VIT_LOAD["load()<br/>High-level ViT loader<br/>Lines 504-535"]
        FIX_OLD["fix_old_checkpoints()<br/>Lines 413-455"]
        RESAMPLE["resample_posemb()<br/>High-res finetuning<br/>Lines 395-410"]
        VANITY_MAP["VANITY_NAMES<br/>Dict mapping<br/>Lines 539-604"]
    end
    
    subgraph "Output"
        PARAMS["Merged Parameters<br/>Ready for model init"]
    end
    
    NPZ --> LOAD_PARAMS
    TS --> LOAD_PARAMS
    VANITY --> VIT_LOAD
    
    LOAD_PARAMS --> LOAD_NP
    LOAD_PARAMS --> LOAD_TS
    LOAD_TS --> TSLOAD
    
    LOAD_NP --> RECOVER_DTYPE
    RECOVER_DTYPE --> MERGE
    TSLOAD --> MERGE
    
    VIT_LOAD --> LOAD_PARAMS
    LOAD_PARAMS --> FIX_OLD
    FIX_OLD --> PYLOOP_SCAN
    FIX_OLD --> SCAN_PYLOOP
    PYLOOP_SCAN --> MERGE
    SCAN_PYLOOP --> MERGE
    
    MERGE --> RESAMPLE
    RESAMPLE --> PARAMS
    
    VANITY_MAP -.->|"Resolves to path"| VIT_LOAD
```

**Sources**: [bv_utils.py:1-473](), [bv_vit.py:395-604]()

## Checkpoint Format Detection

The `load_params()` function serves as the unified entry point for loading checkpoints, automatically detecting the format based on the file path or extension.

### Format Types

| Format | Detection | Loading Function | Use Case |
|--------|-----------|------------------|----------|
| NumPy `.npz` | Presence of `.npz` in path | `load_checkpoint_np()` | Legacy Big Vision checkpoints, smaller models |
| TensorStore | Directory without `.npz` | `load_checkpoint_ts()` | New Big Vision format, large models, sharded loading |

### Submodel Extraction

The checkpoint path can include a colon-separated submodel indicator to extract specific components from multi-model checkpoints:

```python
# Examples from the code
"gs://path/to/checkpoint.npz:img"  # Extract image encoder from SigLIP
"gs://path/to/checkpoint:img/head"  # Extract nested component
```

The path parsing logic in [bv_utils.py:235-238]() uses a regex pattern to split the path and key:

```python
if match := re.match(r"^(.*?/.*?)(?::([\w/]+))?$", ckpt):
    ckpt, key = match.groups()
```

After loading, the submodel is extracted using `tree_get()` [bv_utils.py:263-264]():

```python
if key is not None:
    params = tree_get(params, key)
```

**Sources**: [bv_utils.py:211-266]()

## Loading Mechanisms

### NumPy Format Loading

The `load_checkpoint_np()` function loads `.npz` files and recovers the parameter tree structure:

```mermaid
graph LR
    INPUT["checkpoint.npz"]
    
    subgraph "load_checkpoint_np"
        NPLOAD["npload()<br/>Lines 454-469"]
        ITEMS["Extract items<br/>keys, values"]
        RECOVER["recover_tree()<br/>Lines 182-208"]
    end
    
    OUTPUT["Nested dict<br/>parameter tree"]
    
    INPUT --> NPLOAD
    NPLOAD --> ITEMS
    ITEMS --> RECOVER
    RECOVER --> OUTPUT
```

The `recover_tree()` function [bv_utils.py:182-208]() reconstructs nested dictionaries from flat parameter names using `/` as the separator:

```python
# Example transformation:
# Input: {"a/b/c": value1, "a/b/d": value2, "e": value3}
# Output: {"a": {"b": {"c": value1, "d": value2}}, "e": value3}
```

### TensorStore Format Loading

TensorStore checkpoints support efficient loading of large, sharded models directly to specific devices (CPU/TPU/GPU):

```mermaid
graph TB
    PATH["checkpoint-dir/"]
    
    subgraph "load_checkpoint_ts"
        READ_LAST["Read -LAST file<br/>Get step number<br/>Lines 291-293"]
        TSLOAD_CALL["tsload()<br/>Lines 297"]
    end
    
    subgraph "tsload Details"
        LIST["List array files<br/>Lines 332-334"]
        REGEX["Apply regex filter<br/>Lines 335-336"]
        RECOVER_TREE["recover_tree()<br/>Build structure<br/>Lines 337"]
        FLATTEN["tree_flatten_with_names<br/>Lines 339-340"]
        SPECS["Build tensorstore specs<br/>Lines 351"]
        DESERIALIZE["array_serial.run_deserialization<br/>Lines 352"]
    end
    
    OUTPUT["Sharded arrays<br/>on target devices"]
    
    PATH --> READ_LAST
    READ_LAST --> TSLOAD_CALL
    TSLOAD_CALL --> LIST
    LIST --> REGEX
    REGEX --> RECOVER_TREE
    RECOVER_TREE --> FLATTEN
    FLATTEN --> SPECS
    SPECS --> DESERIALIZE
    DESERIALIZE --> OUTPUT
```

Key features of TensorStore loading:
- **Automatic step resolution**: Reads the `-LAST` file to load the most recent checkpoint [bv_utils.py:291-293]()
- **Regex filtering**: Can load specific parameters matching a regex pattern [bv_utils.py:335-336]()
- **Sharded loading**: Loads arrays directly to specified device shardings [bv_utils.py:343-346]()
- **Concurrent loading**: Uses 64GB concurrent bandwidth for efficiency [bv_utils.py:352]()

**Sources**: [bv_utils.py:269-353]()

## Parameter Merging

The `merge_params()` function aligns loaded checkpoint parameters with initialized model parameters, handling structural mismatches through pattern-based exclusion.

### Merging Logic

```mermaid
graph TB
    LOADED["loaded<br/>From checkpoint"]
    INITED["inited<br/>From model.init()"]
    DONT_LOAD["dont_load<br/>Regex patterns"]
    
    subgraph "merge_params Function"
        COMPILE["check_and_compile_patterns<br/>Compile regexes<br/>Lines 126-150"]
        FLATTEN_L["Flatten loaded<br/>Lines 69-72"]
        FLATTEN_I["Flatten inited<br/>Lines 69-72"]
        
        DECIDE{"For each param<br/>in inited"}
        CHECK_EXISTS{"Exists in<br/>loaded?"}
        CHECK_PATTERN{"Matches<br/>dont_load?"}
        
        USE_LOADED["Use loaded value"]
        USE_INIT["Use init value<br/>Log info"]
        
        VERIFY["Verify coverage<br/>Lines 98-121"]
        UNFLATTEN["recover_tree<br/>Lines 123"]
    end
    
    OUTPUT["Merged params"]
    
    LOADED --> FLATTEN_L
    INITED --> FLATTEN_I
    DONT_LOAD --> COMPILE
    
    FLATTEN_L --> DECIDE
    FLATTEN_I --> DECIDE
    COMPILE --> CHECK_PATTERN
    
    DECIDE --> CHECK_EXISTS
    CHECK_EXISTS -->|Yes| CHECK_PATTERN
    CHECK_EXISTS -->|No| USE_INIT
    
    CHECK_PATTERN -->|No match| USE_LOADED
    CHECK_PATTERN -->|Match| USE_INIT
    
    USE_LOADED --> VERIFY
    USE_INIT --> VERIFY
    VERIFY --> UNFLATTEN
    UNFLATTEN --> OUTPUT
```

### Pattern-Based Exclusion

The `dont_load` parameter accepts regex patterns to exclude specific parameters from loading. Common use cases:

| Pattern | Purpose | Example |
|---------|---------|---------|
| `.*head.*` | Exclude task-specific heads | Don't load ImageNet head for new task |
| `.*posemb.*` | Exclude positional embeddings | Will be resampled separately |
| `triplet_head.*` | Exclude triplet-specific layers | New layers for AligNet training |

The pattern validation [bv_utils.py:144-148]() ensures patterns don't start with `/`, since Big Vision parameter names never have a leading slash:

```python
assert not pattern.startswith("/"), \
    f"Big vision parameter names never start with '/': '{pattern}"
```

### Error Handling

The merging process provides detailed diagnostics:

1. **Info logging**: Parameters that exist in only one source are logged [bv_utils.py:93-96]()
2. **Error on unhandled mismatches**: If mismatches aren't covered by `dont_load` patterns, raises `ValueError` with detailed information [bv_utils.py:102-121]()
3. **Special test indentation**: Uses `-` for params in model but not checkpoint, `+` for params in checkpoint but not model [bv_utils.py:112, 119]()

**Sources**: [bv_utils.py:43-150]()

## Format Conversion

The system supports conversion between two encoder representations used by different training configurations:

| Format | Structure | Use Case |
|--------|-----------|----------|
| `pyloop` | Separate params for each layer:<br/>`encoderblock_0`, `encoderblock_1`, ... | Python for-loop iteration |
| `scan` | Stacked params in single block:<br/>`encoderblock` with leading dimension | `lax.scan` for memory efficiency |

### PyLoop to Scan Conversion

```mermaid
graph LR
    subgraph "Input: pyloop format"
        EB0["encoderblock_0<br/>{LayerNorm, Attention, ...}"]
        EB1["encoderblock_1<br/>{LayerNorm, Attention, ...}"]
        EB_N["encoderblock_N<br/>{LayerNorm, Attention, ...}"]
    end
    
    subgraph "pyloop_to_scan"
        FIND["Find max index<br/>depth = max_idx + 1<br/>Lines 468-469"]
        STACK["np.stack all blocks<br/>Lines 475-477"]
        DELETE["Delete old blocks<br/>Lines 479-480"]
    end
    
    subgraph "Output: scan format"
        EBS["encoderblock<br/>{LayerNorm[depth], Attention[depth], ...}"]
    end
    
    EB0 --> FIND
    EB1 --> FIND
    EB_N --> FIND
    FIND --> STACK
    STACK --> DELETE
    DELETE --> EBS
```

The conversion uses `jax.tree.map` with a custom `stack` function [bv_vit.py:471-477]():

```python
def stack(*values):
    return np.stack(values)

t["encoderblock"] = jax.tree.map(
    stack, *[t[f"encoderblock_{lyr}"] for lyr in range(depth)]
)
```

### Scan to PyLoop Conversion

The reverse conversion extracts each layer's slice from the stacked parameters [bv_vit.py:485-501]():

```python
depth = len(t["encoderblock"]["LayerNorm_0"]["bias"])

for lyr in range(depth):
    block = jax.tree.map(lambda x, lyr=lyr: x[lyr], t["encoderblock"])
    t[f"encoderblock_{lyr}"] = block
```

### Automatic Detection

The `load()` function in [bv_vit.py:504-535]() automatically detects format mismatches and converts:

```python
# Detect attempts to load non-scan checkpoint into scan model
if model_cfg.get("scan") and "encoderblock" not in restored_params["Transformer"]:
    restored_params = pyloop_to_scan(restored_params)

if not model_cfg.get("scan") and "encoderblock" in restored_params["Transformer"]:
    restored_params = scan_to_pyloop(restored_params)
```

**Sources**: [bv_vit.py:458-522]()

## Positional Embedding Resampling

The `resample_posemb()` function enables high-resolution finetuning by resampling learned positional embeddings to match a new spatial resolution.

### Resampling Process

```mermaid
graph LR
    OLD["old posemb<br/>[1, N_old, D]<br/>e.g. [1, 196, 768]"]
    
    subgraph "resample_posemb"
        CHECK["Check if shapes match<br/>Lines 398-399"]
        SQRT["Compute grid sizes<br/>gs_old = sqrt(N_old)<br/>gs_new = sqrt(N_new)<br/>Lines 402-404"]
        RESHAPE["Reshape to 2D grid<br/>[gs_old, gs_old, D]<br/>Line 405"]
        ZOOM["scipy.ndimage.zoom<br/>Bilinear interpolation<br/>Lines 407-408"]
        RESHAPE2["Reshape back<br/>[1, gs_new*gs_new, D]<br/>Line 409"]
    end
    
    NEW["new posemb<br/>[1, N_new, D]<br/>e.g. [1, 784, 768]"]
    
    OLD --> CHECK
    CHECK -->|Different| SQRT
    CHECK -->|Same| NEW
    SQRT --> RESHAPE
    RESHAPE --> ZOOM
    ZOOM --> RESHAPE2
    RESHAPE2 --> NEW
```

### Example Resolution Changes

| Original Size | Grid Size | N | New Size | New Grid | N_new |
|---------------|-----------|---|----------|----------|-------|
| 224×224, patch 16 | 14×14 | 196 | 384×384 | 24×24 | 576 |
| 224×224, patch 16 | 14×14 | 196 | 448×448 | 28×28 | 784 |

The zoom factors are computed as [bv_vit.py:407]():

```python
zoom = (gs_new / gs_old, gs_new / gs_old, 1)
```

The third dimension (embedding dimension) is never resampled, only the spatial dimensions change.

### Integration with Loading

The `load()` function automatically applies resampling after merging [bv_vit.py:530-533]():

```python
if init_params and "pos_embedding" in init_params:
    restored_params["pos_embedding"] = resample_posemb(
        old=restored_params["pos_embedding"], new=init_params["pos_embedding"]
    )
```

**Sources**: [bv_vit.py:395-410, 530-533]()

## Fixing Legacy Checkpoints

The `fix_old_checkpoints()` function handles backwards compatibility with various older checkpoint formats.

### Handled Checkpoint Variations

```mermaid
graph TB
    INPUT["Input checkpoint"]
    
    subgraph "fix_old_checkpoints"
        UNFREEZE["flax.core.unfreeze<br/>convert_pre_linen<br/>Lines 416-418"]
        
        CHECK1{"Has posembed_input<br/>in Transformer?"}
        FIX1["Move to root pos_embedding<br/>Very old ViT format<br/>Lines 421-424"]
        
        CHECK2{"Has pos_embedding<br/>in Transformer?"}
        FIX2["Move to root pos_embedding<br/>Pre-2022 format<br/>Lines 427-429"]
        
        CHECK3{"Has N=sqrt(N)^2+1<br/>posemb shape?"}
        FIX3["Split cls+posemb<br/>Sum into cls token<br/>Lines 435-441"]
        
        CHECK4{"Has probe<br/>in root?"}
        FIX4["Create MAPHead_0<br/>Lines 444-453"]
    end
    
    OUTPUT["Fixed checkpoint"]
    
    INPUT --> UNFREEZE
    UNFREEZE --> CHECK1
    CHECK1 -->|Yes| FIX1
    CHECK1 -->|No| CHECK2
    FIX1 --> CHECK2
    
    CHECK2 -->|Yes| FIX2
    CHECK2 -->|No| CHECK3
    FIX2 --> CHECK3
    
    CHECK3 -->|Yes| FIX3
    CHECK3 -->|No| CHECK4
    FIX3 --> CHECK4
    
    CHECK4 -->|Yes| FIX4
    CHECK4 -->|No| OUTPUT
    FIX4 --> OUTPUT
```

Each fix is accompanied by logging to track which transformations are applied [bv_vit.py:422, 428, 438]().

**Sources**: [bv_vit.py:413-455]()

## Vanity Names and Model Zoo

The `VANITY_NAMES` dictionary provides human-readable aliases for commonly used checkpoints.

### Available Models

The dictionary maps friendly names to Google Cloud Storage paths. Key model families include:

| Model Family | Example Vanity Name | Checkpoint Path Pattern |
|--------------|---------------------|-------------------------|
| AugReg ViT | `"howto-i21k-B/16"` | `gs://vit_models/augreg/...` |
| DeiT-3 | `"deit3_B_224_1k"` | `gs://big_vision/zoo/deit3/...` |
| SigLIP | `"SigLIP B/16 224"` | `gs://big_vision/siglip/...:img` |
| SigLIP2 | `"SigLIP2 B/16 224"` | `gs://big_vision/siglip2/...:img` |

### SigLIP Checkpoints

SigLIP checkpoints are stored as two-tower models (image and text encoders). The vanity names use the `:img` suffix to extract only the image encoder [bv_vit.py:572-580]():

```python
"SigLIP B/16 224": "gs://big_vision/siglip/webli_en_b16_224_63724782.npz:img",
"SigLIP B/16 256": "gs://big_vision/siglip/webli_en_b16_256_60500360.npz:img",
```

### Usage in Loading Pipeline

The `load()` function resolves vanity names before loading [bv_vit.py:506]():

```python
init_file = VANITY_NAMES.get(init_file, init_file)
restored_params = bv_utils.load_params(init_file)
```

This allows configuration files to specify readable checkpoint names:

```python
# In config
cfg.init_transform = Loader(
    init_ckpt="SigLIP B/16 224",  # Human-readable
    dont_load=["head", "triplet_head"]
)
```

**Sources**: [bv_vit.py:539-604]()

## Complete Loading Pipeline

The following diagram shows the complete checkpoint loading pipeline from configuration to merged parameters:

```mermaid
graph TB
    subgraph "Configuration Input"
        CONFIG["Training Config<br/>init_ckpt path<br/>dont_load patterns"]
    end
    
    subgraph "bv_vit.load() - High Level"
        VANITY_RESOLVE["Resolve vanity name<br/>VANITY_NAMES.get()<br/>Line 506"]
        CALL_LOAD_PARAMS["bv_utils.load_params()<br/>Line 507"]
        FIX["fix_old_checkpoints()<br/>Line 509"]
        DETECT_FORMAT["Detect scan/pyloop<br/>Lines 512-521"]
    end
    
    subgraph "bv_utils.load_params() - Format Detection"
        PARSE["Parse path and key<br/>Lines 235-238"]
        CHECK_NPZ{"Contains .npz?<br/>Line 242"}
        LOAD_NPZ["load_checkpoint_np()<br/>recover_dtype()<br/>Lines 243-253"]
        LOAD_TS["load_checkpoint_ts()<br/>tsload()<br/>Lines 256-261"]
        EXTRACT_KEY["tree_get(params, key)<br/>Lines 263-264"]
    end
    
    subgraph "Parameter Processing"
        CONVERT_FORMAT["pyloop_to_scan or<br/>scan_to_pyloop<br/>Lines 516, 520"]
        MERGE["merge_params()<br/>Handle dont_load<br/>Line 524-526"]
        RESAMPLE["resample_posemb()<br/>Lines 530-533"]
    end
    
    subgraph "Output"
        FINAL["Merged, Converted<br/>Ready-to-use Parameters"]
    end
    
    CONFIG --> VANITY_RESOLVE
    VANITY_RESOLVE --> CALL_LOAD_PARAMS
    CALL_LOAD_PARAMS --> PARSE
    
    PARSE --> CHECK_NPZ
    CHECK_NPZ -->|Yes| LOAD_NPZ
    CHECK_NPZ -->|No| LOAD_TS
    
    LOAD_NPZ --> EXTRACT_KEY
    LOAD_TS --> EXTRACT_KEY
    EXTRACT_KEY --> FIX
    
    FIX --> DETECT_FORMAT
    DETECT_FORMAT --> CONVERT_FORMAT
    CONVERT_FORMAT --> MERGE
    MERGE --> RESAMPLE
    RESAMPLE --> FINAL
```

### Key Integration Points

The checkpoint management system integrates with the training pipeline through:

1. **Kauldron Loader**: The `Loader` class in [bv_wrapper.py]() uses the `init_transform` mechanism to call `bv_vit.load()` during model initialization
2. **Training Config**: The `cfg.init_transform` field in [configs/siglip.py]() specifies which checkpoint to load and which parameters to exclude
3. **Model Initialization**: The merged parameters replace the randomly initialized parameters before training begins

**Sources**: [bv_vit.py:504-535](), [bv_utils.py:211-266]()

## Utility Functions

### Tree Manipulation

| Function | Purpose | Location |
|----------|---------|----------|
| `tree_flatten_with_names()` | Flattens pytree with parameter names | [bv_utils.py:153-179]() |
| `recover_tree()` | Reconstructs nested dict from flat names | [bv_utils.py:182-208]() |
| `tree_get()` | Extracts subtree by path with helpful errors | [bv_utils.py:356-383]() |
| `tree_broadcast()` | Broadcasts prefix tree to full tree | [bv_utils.py:421-451]() |

### Data Type Handling

The `recover_dtype()` function [bv_utils.py:412-418]() fixes a NumPy limitation where `bfloat16` arrays are saved as `void` type:

```python
def recover_dtype(a):
    if hasattr(a, "dtype") and a.dtype.type is np.void:
        assert a.itemsize == 2, "Unknown dtype!"
        return a.view(jax.numpy.bfloat16)
    else:
        return a
```

This is automatically applied after loading `.npz` checkpoints [bv_utils.py:244]().

**Sources**: [bv_utils.py:153-469]()

---

