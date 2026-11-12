# Code Selection and Simplification Patterns

After an initial implementation works, review the code for simplification opportunities. Cleaner model code is easier to maintain, review, and upstream. These patterns were identified during code reviews of MLX conversions.

## Start from the closest existing MLX model

Before writing a new model file from scratch, find the most similar existing model in `mlx-lm/mlx_lm/models/`. Many architectures share 90%+ of their structure with an existing implementation. Starting from the closest match:
- Reduces bugs from reimplementing boilerplate
- Naturally follows established MLX patterns
- Makes the diff for review much smaller

For example, GLM-5 (`glm_moe_dsa`) is essentially `glm4_moe_lite` with different defaults and a `rope_parameters` nested dict. Starting from `glm4_moe_lite` rather than `deepseek_v3` saved significant work.

## Reuse via Inheritance

Before writing a standalone model file, check whether the target model is architecturally identical (or nearly so) to an existing MLX model. Many models in mlx-lm are thin wrappers — 50-80 lines — that inherit from a parent and only override config mapping or weight sanitization.

**How to assess:** Compare the transformers `modeling_*.py` of the target model against existing MLX models. Focus on attention mechanism (standard, GQA, MLA, MLA+Indexer), MLP/MoE structure, and layer composition. If the only differences are config field names, nesting, or default values, inheritance is the right approach.

**Pattern 1 — Direct inheritance (text models):**
When the architecture is identical and only the config shape differs. Override `ModelArgs` (and optionally `sanitize()`), inherit everything else.

```python
from .deepseek_v32 import Model as DSV32Model

@dataclass
class ModelArgs(BaseModelArgs):
    rope_parameters: Dict  # GLM-5 nests rope config here
    rope_scaling: Dict = None
    rope_theta: Optional[float] = None

    def __post_init__(self):
        self.rope_scaling = self.rope_parameters
        self.rope_theta = self.rope_parameters["rope_theta"]

class Model(DSV32Model):
    def __init__(self, config: ModelArgs):
        super().__init__(config)
```

Examples: `glm_moe_dsa` → `deepseek_v32`, `qwen3_5_moe` → `qwen3_5`, `smollm3` → `llama`.

**Pattern 2 — VL wrapper (vision-language models):**
When the target is a VL model whose text backbone already exists in mlx-lm. Wrap the text model, strip vision weights in `sanitize()`, and remap `language_model.*` key prefixes.

```python
from . import qwen2

class Model(nn.Module):
    def __init__(self, args):
        self.language_model = qwen2.Model(args)

    def sanitize(self, weights):
        return {k: v for k, v in weights.items()
                if not k.startswith("model.visual")}
```

Examples: `pixtral` → `llama`, `qwen2_vl` → `qwen2`, `gemma3` → `gemma3_text`, `kimi_k25` → `deepseek_v3`.

**When to write standalone:** Only when the architecture genuinely differs from all existing models — novel attention mechanism, different layer composition, or unique MoE routing. If you find yourself copying 80%+ of an existing file, use inheritance instead.

**Exception to "transformers-as-source-of-truth" rule**. If a code path has already been implemented in MLX, and the current architecture uses it, and transformers has a partial implementation (based on comments or warnings raised in the source code), then it's fine to reuse the MLX implementation and not blindly follow the partial transformers implementation.

## Remove dead config branches

If the target model (or all known variants) only uses one value for a config parameter, remove the branch for the unused value:

```python
# BEFORE: supports q_lora_rank=None, but GLM-5 always has q_lora_rank=2048
if self.q_lora_rank is None:
    self.q_proj = nn.Linear(...)  # dead code
else:
    self.q_a_proj = nn.Linear(...)
    self.q_a_layernorm = nn.RMSNorm(...)
    self.q_b_proj = nn.Linear(...)

# AFTER: direct, no branching
self.q_a_proj = nn.Linear(...)
self.q_a_layernorm = nn.RMSNorm(...)
self.q_b_proj = nn.Linear(...)
```

This applies when [config analysis](./model-discovery-and-config-analysis.md) confirms only one variant exists across all target models. If multiple variants exist in the wild, keep the branches.

## Simplify `tie_word_embeddings`

When `tie_word_embeddings` is always `false` for the target architecture, create `lm_head` unconditionally and skip the conditional logic:

```python
# BEFORE
if not config.tie_word_embeddings:
    self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

# AFTER (when tie_word_embeddings is always false)
self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
```

Similarly, skip the `tie_word_embeddings` field in `ModelArgs` if it's never variable. In sanitize, don't conditionally pop `lm_head.weight`.

## Skip `make_cache()` when default works

The `make_cache()` method is only needed when layers require non-default cache types (e.g., `CacheList` for hybrid layers with both KV and SSM state, or dual caches for DSA indexers). If all layers use standard `KVCache`, the base class default handles it — don't define `make_cache()`.

Models that need `make_cache()`:
- Hybrid SSM + attention models (different cache types per layer)
- Models with DSA indexers (dual KV caches per layer)

Models that don't:
- Standard attention-only models
- MLA models without indexers (MLA still uses KVCache, just with compressed dimensions)

## Match epsilon values from reference implementations

Small numerical constants (epsilon values, normalization guards) should match the closest reference model, not just the transformers source:

```python
# glm4_moe_lite has this guard in MoE normalization
expert_weights = expert_weights / (expert_weights.sum(axis=-1, keepdims=True) + 1e-20)

# Our implementation should match, not omit the epsilon
```

These guards prevent division-by-zero in edge cases. While they may not affect typical inputs, omitting them creates a silent correctness risk. When in doubt, match what the closest working MLX model does.

## Simplify `shard()` to match patterns

The `shard()` method for distributed inference should follow the established pattern from the closest reference model. Don't add branches for config variants that are always one value:

```python
# BEFORE: branches on q_lora_rank existence
def shard(self, group=None):
    ...
    if hasattr(attn, "q_a_proj"):
        attn.q_a_proj = shard_linear(...)
    else:
        attn.q_proj = shard_linear(...)

# AFTER: direct (when q_lora_rank always exists)
def shard(self, group=None):
    ...
    attn.q_a_proj = shard_linear(...)
```

## General principles

1. **Fewer lines = fewer bugs.** Every branch is a potential source of errors. If a branch can't be exercised by any existing model variant, remove it.
2. **Match the ecosystem.** MLX model files follow consistent patterns. Deviating from them (e.g., different variable names, unusual control flow) makes code review harder and increases the chance of subtle bugs.
3. **Simplify after correctness.** Get the model working first with all branches intact, then simplify once you've confirmed which branches are active. This avoids accidentally removing code you actually need.
4. **Document in the PR, not in the code.** Don't add inline comments explaining intentional deviations from transformers (e.g., hardcoding a value, ignoring a code branch). The PR description, commit messages, and conversion report are where this context belongs (see "Minimize code comments" in SKILL.md).
