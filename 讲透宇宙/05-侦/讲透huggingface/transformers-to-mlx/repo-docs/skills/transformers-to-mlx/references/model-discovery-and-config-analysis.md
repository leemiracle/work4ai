# Model Discovery and Config Analysis

This reference covers two tasks that should be performed early in the conversion process:

1. Discovering which models use the target architecture
2. Analyzing config variance across those models to avoid surprises later

## Model Discovery

### Why This Matters

A single architecture may have multiple model sizes (e.g., 1.2B, 2.7B, 7B) with different config values or even different weight formats. Discovering them upfront prevents writing a `sanitize()` or model implementation that only works for one variant.

### How to Search

The `model_type` from `config.json` is automatically indexed as a tag on Hugging Face Hub. Use it as a filter for precise, zero-noise results:

```python
from huggingface_hub import HfApi

api = HfApi()
models = list(api.list_models(
    filter=["<model_type>", "transformers"],
    sort="downloads",
    direction=-1,
))

for m in models[:20]:
    print(f"{m.id:50s}  downloads={m.downloads}")
```

Or via the CLI:

```bash
hf models ls --filter "<model_type>,transformers" --sort downloads --limit 20
```

### Interpreting Results

Results will include the original models, fine-tunes, quantizations, and sometimes false positives. To identify the canonical (original) models:

- **Sort by downloads** — the originals are almost always at the top
- **Group by organization** — the original org typically has the base model and its variants (instruct, chat, etc.)
- **Look at model sizes** — different sizes from the same org often share the architecture but may differ in config values or weight format

Present the top results grouped by org to the user and ask which ones to target. For example:

> I found 120 models using the `zamba2` architecture. The Zyphra org appears to be the original author with these variants:
> - `Zyphra/Zamba2-1.2B` (base)
> - `Zyphra/Zamba2-1.2B-instruct`
> - `Zyphra/Zamba2-2.7B` (base)
> - `Zyphra/Zamba2-2.7B-instruct`
> - `Zyphra/Zamba2-7B` (base)
> - `Zyphra/Zamba2-7B-instruct`
>
> Which ones should we target?

Even if the user only cares about one size, it's worth downloading `config.json` from all canonical sizes to compare (see next section).

Always state the models you selected. When in doubt, ask the user for confirmation.

## Config Variance Analysis

### Procedure

After identifying the target models, compare their configs. **This includes variants at different training stages** (base, SFT, DPO, instruct) — not just different sizes. Training-stage variants of the same architecture can have fundamentally different runtime behavior (e.g., one may use RoPE, another might use NoPE).

1. **Download configs** from each target model (just the `config.json`, not the full weights):

```python
from huggingface_hub import hf_hub_download

configs = {}
for repo_id in target_models:
    path = hf_hub_download(repo_id, "config.json")
    with open(path) as f:
        configs[repo_id] = json.load(f)
```

2. **Diff the configs** — identify parameters that vary across sizes:

```python
all_keys = set()
for c in configs.values():
    all_keys.update(c.keys())

for key in sorted(all_keys):
    values = {repo: c.get(key) for repo, c in configs.items()}
    unique = set(str(v) for v in values.values())
    if len(unique) > 1:
        print(f"\n{key}:")
        for repo, val in values.items():
            print(f"  {repo}: {val}")
```

3. **Cross-reference with transformers source code** — for each parameter that varies, check whether the transformers modeling code has conditional logic for it.

### What to Look For in Transformers Source

The transformers `modeling_<model_type>.py` file is the **source of truth**. Search for conditional code paths:

```bash
# Find all config-dependent branches
grep -n "config\." modeling_<model_type>.py | grep -E "if|else|is None|is not None|!="
```

For each conditional, classify it:

| Category | Action |
|----------|--------|
| **Varies across target models** | Must implement both paths in MLX |
| **Single value across targets, but conditional exists** | Implement the observed path; add a comment noting the alternative |
| **Training-only** (dropout, initializer_range, etc.) | Ignore |

### Common Sources of Variance

These parameters frequently differ across model sizes and often require different code paths or `sanitize()` logic:

| Parameter pattern | What can change |
|-------------------|----------------|
| `num_hidden_layers`, `hidden_size`, etc. | Scale (no code change needed) |
| `q_lora_rank` (None vs int) | Entirely different projection architecture |
| `position_embedding_type` | Whether RoPE is applied at all |
| `rope_parameters`, `rope_theta` | RoPE frequency base — can be null (NoPE), vary across training stages |
| Layer type lists (`mlp_layer_types`, `layer_types`) | Which layers are MoE/dense/attention/mamba |
| `num_mem_blocks`, weight tying flags | How `sanitize()` must replicate shared weights |
| `n_group`, `mamba_ngroups` | Routing and SSM kernel behavior |
| `tie_word_embeddings` | Whether `lm_head` exists as a separate weight |

### Weight Format Variance

Config analysis alone is not enough. Different model sizes sometimes use **different weight naming conventions** in their checkpoints, even within the same architecture. This was observed in Zamba2 where the 7B used a legacy `model.blocks.*` format while 1.2B/2.7B used `model.layers.*`.

To check for this without downloading full weights:

```python
from huggingface_hub import hf_hub_download
from safetensors import safe_open

# Download just the index file
index_path = hf_hub_download(repo_id, "model.safetensors.index.json")
with open(index_path) as f:
    index = json.load(f)

# Examine the weight name patterns
weight_names = sorted(index["weight_map"].keys())
print(f"Sample weights from {repo_id}:")
for name in weight_names[:20]:
    print(f"  {name}")
```

Compare the weight name prefixes and patterns across all target sizes. If they differ, `sanitize()` must detect and handle both formats.

### Output of This Phase

After completing the analysis, present a summary to the user:

1. List of target models and their sizes
2. Config parameters that vary, with observed values
3. Conditional code paths in transformers that are affected
4. Any weight format differences detected
5. Recommendation on which paths to implement vs document

This information directly informs the `ModelArgs` dataclass (which fields need to exist), the model implementation (which conditionals to include), and `sanitize()` (which weight formats to handle).
