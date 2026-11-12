---
name: transformers-to-mlx
description: Convert Hugging Face transformers language models to MLX format for Apple Silicon inference. Use when asked to convert a model from transformers to MLX, port a model to MLX, create an MLX implementation of a model, or test/validate an MLX model conversion. Triggers include mentions of "convert to MLX", "MLX implementation", "port to MLX", "mlx-lm", or requests involving both transformers and MLX frameworks.
---

# Transformers to MLX Model Conversion

## MLX-LM repo

In all circumstances refer to the following repo and branch unless overridden by the user.

GitHub repo: https://github.com/ml-explore/mlx-lm
Branch: main

## Workflow

### Phase 0: Set up working environment

1. Verify `uv` is installed, use it to create a virtual environment. Always use `uv pip install` (not plain `pip install`) to install packages in the environment — this avoids resolver conflicts and is significantly faster.
2. git clone the mlx-repo from GitHub. ALWAYS USE the repo and branch specified in the `MLX-LM repo` section above.
3. Install mlx-lm in editable mode in the environment
4. Install transformers locally too, to ensure we have the latest version of the code: https://github.com/huggingface/transformers. You can clone with `--depth 1` because it has many refs. Also install `accelerate` for `device_map` support.
5. Make sure `huggingface_hub` is installed too, to use the `hf` CLI for model download. It comes with the previous libraries as a dependency, so you may need to wait for it if you run stuff in parallel.
6. **Use the venv binaries directly** rather than activating: `.venv/bin/python script.py`, `.venv/bin/hf download ...`, `.venv/bin/mlx_lm.generate ...`. This avoids `source .venv/bin/activate` (which executes a shell script that triggers permission prompts and doesn't propagate to background commands). The CLI entry points and Python interpreter resolve their own environment from their installed location, so no activation is needed.
7. Discover and select target models, if the user did not provide a list of models to consider. Search the Hub for all models using the target architecture to convert, identify canonical variants across sizes, and confirm targets with the user. Use [Model Discovery and Config Analysis](references/model-discovery-and-config-analysis.md) to learn how.
8. Download a local copy of the model(s) from Hugging Face using the `hf` CLI. Save the models to local folders inside the project using `--local-dir`, this will allow you to read contents easily.

### Phase 1: Analyze Source Models

1. Read `config.json` for `model_type` and architecture details
2. Verify native transformers support in `.../transformers/models/<model_type>/`, residing in the virtual environment
3. Read the transformers `modeling_<model_type>.py` implementation carefully
4. If the model is a vision-language model, convert the text-generation backbone, but inform the user in your report. Do not proceed if the model is not a language model at all (and explain why).
5. Analyze config variance across target models and cross-reference with conditional code paths in transformers. See [Model Discovery and Config Analysis](references/model-discovery-and-config-analysis.md).
6. Pay special attention to unique or novel architecture variants the model may introduce. Highlight them in your report, and be vigilant for subtle bugs that may be difficult to detect in tests. Do some ad-hoc testing for them if necessary.

**Some key config fields to check:**
- `rope_parameters`, `position_embedding_type` - See section on RoPE later
- `layer_types` - For hybrid models (e.g., mamba + attention)
- Scalar multipliers: `embedding_multiplier`, `attention_multiplier`, `residual_multiplier`, `logits_scaling`
- `torch_dtype` or `dtype` or `text_config.dtype` — The model's intended runtime precision. Some models (especially VL wrappers) nest this inside `text_config` rather than exposing it as top-level `torch_dtype` (or `dtype`). If the converter can't find it, it skips the dtype casting step entirely, leaving stray float32 weights in the converted model. Verify which field the model uses and confirm `mlx_lm.convert` detects it. Use [`scripts/resolve_dtype.py`](scripts/resolve_dtype.py) to determine the expected dtype from the config (or the safetensors header as a fallback) and record the source — this becomes the basis for the dtype tests in Phase 4 and the manifest in Phase 8.

### Phase 2: Find Reference MLX Models

Examples from `mlx-lm/mlx_lm/models/`:
- Standard attention: `llama.py`
- MLA (Multi-head Latent Attention): `deepseek_v3.py` — see [MLA Reference](references/mla.md)
- MoE (Mixture of Experts): `deepseek_v3.py`, `mixtral.py`
- GatedDeltaNet (linear attention): `qwen3_next.py`, `qwen3_5.py`, `olmo_hybrid.py`
- Hybrid (Mamba + Attention): `nemotron_h.py`
- Sliding window: `mistral.py`

Start from the **closest existing model** rather than building from scratch — see [Code Selection and Simplification](references/code-selection-simplification.md).

### Phase 3: Create MLX Model

Create `mlx-lm/mlx_lm/models/<model_type>.py` (self-contained single file):

```python
@dataclass
class ModelArgs:
    # Config params with defaults
    position_embedding_type: str = "rope"  # Check for "nope"!

class Attention(nn.Module): ...
class MLP(nn.Module): ...
class DecoderLayer(nn.Module): ...
class LanguageModel(nn.Module): ...

class Model(nn.Module):
    def sanitize(self, weights): ...  # Convert weight names/shapes
    def shard(self, group): ...       # Distributed inference

    @property
    def cast_predicate(self):         # Keep specific weights in float32
        return lambda _, m, _: isinstance(m, MoEGate) and "bias" in m
```

**sanitize() patterns** — see [Weight Sanitization](references/weight-sanitization.md) for detailed guidance on how to make weights loading compatible with both transformers and MLX-converted weights. Here are some common examples:
- Stack experts: `experts.{N}.gate_proj` → `switch_mlp.gate_proj` shape `(num_experts, ...)`
- Remove: `rotary_emb.inv_freq`, extra layers (e.g., MTP heads)
- 3D MoE weights: May need reshape from `(num_experts, hidden, intermediate)`
- Shared/tied weights: Replicate from source blocks to all tied layers
- Different model sizes may use different weight formats — detect and branch
- MLA `kv_b_proj` splitting: dequantize → reshape by heads → split into `embed_q`/`unembed_out` — see [MLA Reference](references/mla.md)

**RoPE:**
- `rope_interleave=True` → `traditional=True` in MLX
- `position_embedding_type="nope"` → Do NOT apply RoPE at all
- `rope_parameters` nested dict: some models store RoPE config as `{"rope_theta": ..., "rope_type": ...}` instead of top-level fields — extract in `__post_init__`. See [MLA Reference](references/mla.md).
- **Null handling:** `rope_parameters` can be `null`, absent, or a dict with `null` values (e.g., `{"rope_theta": null}`). Use `.get()` with defaults and test for `None` explicitly in `__post_init__`. Verify the different paths the transformers codebase uses to deal with all variants present in the config files.

**Conversion and quantization:** Use `mlx_lm.convert` to validate sanitize and produce quantized models — see [Conversion and Quantization](references/conversion-and-quantization.md). Only do this after testing transformers weights, or if the model is [too large to run unquantized](references/large-models.md).

### Phase 4: Testing

**Note:** For very large models that can't fit in fp16 / bf16, the standard comparison workflow isn't feasible. Use the quantize-first strategy instead — see [Large Models](references/large-models.md). For models that require multiple machines, see [Distributed Inference](references/distributed-inference.md).

**Test 1: Generation comparison** (do first - easier to spot garbage output)

Pre-validation: run `mlx_lm.generate` with a prompt and verify the output is coherent. This will use the default sampling method taken from the model's `generation_config.json`.

Example:

```bash
mlx_lm.generate --model zai-org/GLM-4.7-Flash --prompt "Who are you?"
```

Use an appropriate prompt depending on the model capabilities (for example, is it a base model or does it use a chat template). If it's a base model, use an inviting prefix sentence to be continued, not just a single word. If it's a conversational model, ask an interesting question. If the model card mentions specific capabilities (for example, the model was trained for code generation), use a relevant topic.

If generated text is garbage, use the layer-by-layer tests to try to identify implementation mismatches.

For more controlled generation (greedy mode) and comparison with transformers, use the [compare_generation.py script](scripts/compare_generation.py).

When using this script, make a judgement call about whether the generations are semantically similar. They will rarely match exactly, because of differences in the compute device, kernel implementations, and other reasons.

Do not declare success if generation is not reasonable - check for numerical and implementation differences and iterate until you get a good quality output, using the transformers one as the quality reference.

**Test 2: Output dtype**

Resolve the expected dtype with [`scripts/resolve_dtype.py`](scripts/resolve_dtype.py) — it tries config fields first, then falls back to the most common dtype in the safetensors header. Always record the **source** in the conversion report (e.g., `config.dtype`, `safetensors header (BF16=292/293, F32=1/293)`) so reviewers know the basis for the check.

```bash
python scripts/resolve_dtype.py /path/to/model
# dtype: bfloat16
# source: safetensors header (BF16=292/293, F32=1/293)
```

Then run a forward pass and verify the output dtype matches with [`scripts/check_dtype.py`](scripts/check_dtype.py):

```bash
python scripts/check_dtype.py /path/to/model bfloat16
# {"output_dtype": "mlx.core.bfloat16", "expected_dtype": "bfloat16", "match": true}
```

Exits non-zero with a `FAIL:` message on stderr if the runtime dtype doesn't match.

A single float32 weight (e.g., a norm weight promoted by `v + 1.0` in sanitize) will silently propagate float32 through the entire model via dtype promotion, causing up to 5x slower inference on Apple Silicon.

The same script works after quantization — the runtime output dtype is unaffected by weight quantization (only the storage of matmul weights changes). Re-run it on the quantized model in Phase 5 to confirm.

**Test 3: Numerical comparison**

Use the [compare_predictions script](scripts/compare_predictions.py) to compare logits from a single forward pass and extract some statistics. **Use a prompt of at least 100 tokens** (e.g., a paragraph of text) — short prompts (5-10 tokens) can hide positional encoding bugs because RoPE error grows with position. A wrong `rope_theta` may pass top-1 comparison at 5 tokens but diverge significantly at 100+.

Point out any major differences you observe. A max logits difference in ~0.5-1.0 (or larger, for models with many layers where errors accumulate) is usual between CPU transformers and Metal MLX. If you see suspicious values, run a layer-by-layer comparison even if the generation test seemed to pass.

If you run a top-5 or top-10 comparison, include the top-10 list in the GitHub PR you'll open when you're done (unless they are identical).

**Test 4: Layer-by-layer** (if predictions don't match — and as a routine sanity check)

Use [`scripts/compare_layers.py`](scripts/compare_layers.py). One forward pass per framework captures the output of every decoder layer, the post-final-norm state, and the logits, then compares them side-by-side with absolute and relative diffs.

```bash
python scripts/compare_layers.py /path/to/model "<prompt>"
```

Read the table from the bottom up:
- **`logits` row**: the most important. If logits agree, the implementation is end-to-end correct even if hidden states drift along the way.
- **`post-norm` row**: hidden state after the final RMSNorm. Should be small relative diff.
- **`layer N` rows**: per-layer outputs. Look for the first sharp jump in `rel diff` — that's where divergence is introduced.

The script is architecture-agnostic: it wraps each entry in `model.[language_model.]model.layers` with a thin capture proxy (preserving the layer's class so `isinstance` checks in hybrid models keep working). It does NOT compare the embedding output, since pre-layer transforms (multipliers, per-layer scaling) differ across architectures and the embedding row is rarely informative.

Healthy implementations show <1% relative diff at every position. A pattern where mid-layer divergence is relatively large but the `logits` row is small usually means the divergence cancels out at the head — annoying but not a correctness bug.

Include results in the report.

**Test 5: Long sequence degradation**
- Run a prompt that generates a long sequence, such as "Write an HTML and JavaScript page implementing space invaders", or something appropriate depending on model capabilities. You can use `mlx_lm.generate -m 16384` to allow up to 16K tokens to be generated.
- Observe if the output turns to garbage after a while. This usually signals mistakes in RoPE.

### Phase 5: Quants

Use `mlx_lm.convert` to quantize the model. First, run `scripts/resolve_dtype.py` on the source checkpoint to confirm the storage dtype. If the model already deals with native quantized weights, skip this phase and inform the user. If it doesn't, try a simple quantization to 4 bits and run generation tests to verify whether results are coherent.

After quantization, re-run `scripts/check_dtype.py` against the quantized model with the same expected dtype as the unquantized one. The runtime dtype shouldn't change with quantization — only the storage of matmul weights does. A mismatch here usually means a stray float32 weight survived the quantize step.

### Phase 6: MLX Tests

When appropriate, create tests for the model you just converted, following the structure and criteria used in the mlx-lm repo.

### Phase 7: Report

Always include the following in your output report:

- The list of models and variants selected for conversion, and tested.
- Notable architecture decisions and novelties introduced.
- Non-trivial implementation details that are worth noting.
- The expected output dtype per variant and where it came from (e.g., `config.dtype` vs `safetensors header`). Use the results from `scripts/resolve_dtype.py`.
- At least a meaningful generation example of ~200 tokens or more.
- A summary of the numerical differences you found.
- Per-layer comparison results.
- Errors that you couldn't solve and pointers to analyze them.
- If changes to `mlx-lm` were needed, explain in detail what they were, and provide links to the equivalent transformers implementation. This should be rare (bugs or missing features).
- Reflect upon learnings that we could consider to incorporate back into the Skill for future reference. Trivial discoveries that are easy for you to replicate in future sessions are not necessary; focus on initial error cases that required some iteration.

Please, output this report in your conversation, and also create a markdown file for reference.

### Phase 8: GitHub PR

- **Create a feature branch** for your changes (e.g., `add-<model_type>`) — never commit directly to the main working branch. See [GitHub PR Workflow](references/github-pr-workflow.md) for details.
- ALWAYS ask for confirmation before submitting a PR. The user may have questions or want to run additional tests, or include more variants.
- Make sure the `gh` cli is authenticated.
- Ensure you use the github repo specified at the beginning of this document (even if it's not the canonical one).
- In the PR, include:
    * A suitable title. But please, prefix it with `[transformers-to-mlx skill]` for disclosure.
    * Also disclose that all tests and results were obtained with the skill.
    * Your summary report in the PR.
    * In addition to the summary report, include test commands and their outputs. For example, if you ran a long sequence generation with `mlx_lm.generate`, include the command and the full output. Also include the source code you used to compare numerical results, when appropriate. Same thing for the dtype tests and everything else.
- **After the mlx-lm PR is created**, generate a test manifest and open a PR to the test harness repo. See [GitHub PR Workflow — Test Manifest](references/github-pr-workflow.md#test-manifest) for the format and procedure.

## Critical Lessons

<!-- Note for the skill author: we may want to extract these to separate files depending
on the model type or type of pitfall -->

### Garbage Output Despite Loading

Model loading and generating without crashes does NOT mean it works. Always verify:
1. Output is coherent text (not "lylyly Usesfinite")
2. Top predictions match transformers
3. Logits statistics are in same ballpark

### Position Embeddings

This is a usual source of problems.

Check `position_embedding_type` in config:
- `"rope"` - Apply rotary position embeddings
- `"nope"` - Do NOT apply any position embeddings (common in hybrid models)

**RoPE config can vary across variants of the same architecture.** For example, OLMo-Hybrid base/SFT use `rope_theta=10000` while the DPO variant uses NoPE (no positional embeddings at all, via `rope_parameters: {rope_theta: null}`). Always diff RoPE-related config fields across ALL target checkpoints — base, SFT, DPO, and different sizes — before implementation.

```python
# Conditional RoPE
use_rope = getattr(args, 'position_embedding_type', 'rope') != 'nope'
if use_rope:
    self.rope = initialize_rope(...)
else:
    self.rope = None
```

### Scalar Multipliers

Some models (Granite, etc.) use scaling factors that MUST be applied exactly:
- `embedding_multiplier` - Scale embeddings before first layer
- `attention_multiplier` - Replace `1/sqrt(head_dim)` in attention
- `residual_multiplier` - Scale residual connections
- `logits_scaling` - Scale final logits

Missing any of these causes completely wrong predictions.

### Weight Key Names: Checkpoint vs Transformers Attributes

When building the MLX model, use the **transformers model attribute names** for your module definitions — not the raw checkpoint key names. These often differ: the checkpoint may use names like `Wqkv` or `gate_up_proj` while the transformers model class uses `q_proj`, `k_proj`, `gate_proj`, `up_proj`, etc.

The `sanitize()` method is where you remap checkpoint names to match the MLX model structure (which mirrors transformers attribute names). If the MLX model uses checkpoint names instead, weight loading will silently fail or require a convoluted sanitize.

To find the authoritative mapping, check `conversion_mapping.py` in the transformers model directory — see [Weight Sanitization](references/weight-sanitization.md#transformers-conversion_mappingpy).

### Numerical Precision

Some models define custom operations (e.g., gated RMSNorm, specialized activations) that are sensitive to precision. If the transformers code explicitly casts to float32, the MLX implementation must do the same:

```python
class GatedRMSNorm(nn.Module):
    def __call__(self, x, residual):
        original_dtype = x.dtype
        x = x.astype(mx.float32)
        norm = mx.rsqrt(mx.mean(x * x, axis=-1, keepdims=True) + self.eps)
        x = (x * norm).astype(original_dtype) * self.weight
        return x
```

Missing a float32 cast may not cause obvious errors in short sequences but leads to degraded output quality (e.g., repetition) in longer generations. When reading the transformers source, watch for `.float()`, `.to(torch.float32)`, or similar casts — they are there for a reason.

However, do check for MLX ops that may be internally upcasting in their implementation.

### Dtype Contamination After Conversion

A single float32 parameter in a non-quantized layer (norms, biases, gating weights) can silently poison the entire forward pass through MLX's dtype promotion rules. This causes no correctness errors — the model generates coherent text — but inference speed degrades dramatically (up to 5x slower) because all quantized matmuls run in float32 mode instead of bfloat16.

Common causes:
- Sanitize operations like `v + 1.0` promote bfloat16 norm weights to float32 (Python's `1.0` is float64/float32)
- Parameters initialized with `mx.ones()` or `mx.zeros()` default to float32 and persist if the checkpoint doesn't include them

The contamination path: float32 norm weight &rarr; `rms_norm` outputs float32 &rarr; quantized matmul receives float32 input &rarr; outputs float32 &rarr; residual addition promotes hidden state to float32 &rarr; every subsequent layer inherits float32.

**Always verify output dtype after conversion and after quantization** (see Phase 5).

### Hybrid and SSM Architectures

For models mixing layer types (e.g., Mamba + Attention) — see [Hybrid and SSM Models](references/hybrid-and-ssm-models.md) for detailed guidance:
1. Check `layer_types` config for per-layer architecture
2. Each layer may have MULTIPLE blocks (not just one):
   - Block 1: Mamba OR Attention
   - Block 2: MoE + shared_mlp (for ALL layers)
3. Both Mamba and Attention layers often share the same MoE/MLP block
4. `make_cache()` must return the right cache type per layer (e.g., `CacheList(KVCache(), ArraysCache())` for hybrid layers)
5. CUDA-only dependencies (`mamba_ssm`, `causal_conv1d`) won't install on macOS — transformers uses fallback implementations

### 3D MoE Weights

Expert weights may be stored as 3D tensors:
- Shape: `(num_experts, hidden_size, intermediate_size)`
- Need proper reshape in sanitize()
- SwitchGLU expects specific shapes

### Debugging Checklist

When predictions don't match:
1. **Embeddings** - Should match exactly (mean, std)
2. **After embedding scaling** - Check multiplier applied
3. **Layer-by-layer** - Find first divergence point
4. **Check config fields** - position_embedding_type, multipliers
5. **Layer structure** - All blocks applied? (MoE often missed)
6. **Attention scaling** - Verify the scale factor matches transformers exactly (some models use non-standard formulas like `(head_dim // 2) ** -0.5`)
7. **Precision casts** - Check for `.float()` / `.to(torch.float32)` in transformers code, especially in norms and activations (see Numerical Precision above)
8. **Repetitive output** - If the model generates repetitive or looping text, this may indicate a shape or transpose error in the attention or linear attention layers (e.g., head dimensions swapped, wrong reshape order), not a sampling issue

### Large Models

Models that consume a significant fraction of available RAM require special handling:
- Set `sudo sysctl iogpu.wired_limit_mb=<value>` to increase the wired memory limit
- Set `MLX_METAL_FAST_SYNCH=1` for faster GPU synchronization
- `mlx_lm.generate` may OOM due to `mx.async_eval` double-buffering — use a manual generation loop
- Very large MoE models suffer memory system thrashing even with selective `gather_qmm`
- For models too large for one machine, use tensor parallelism via `mlx.launch`

See [Large Models](references/large-models.md) and [Distributed Inference](references/distributed-inference.md) for detailed guidance.

### Changes to Shared mlx-lm Code

Some conversions require modifications to shared mlx-lm infrastructure (`ssm.py`, Metal kernels, `cache.py`), not just a new model file. These changes affect all models using the same code. See [Common Infrastructure Changes](references/mlx-common-infrastructure.md) for guidance on localizing fixes and avoiding regressions.

## General Guidance and Common Pitfalls

- **Minimize code comments.** Do not add comments unless the code would be legitimately confusing without one (which should be very rare). Comments must be reviewed just like code, so every unnecessary comment increases review burden. The PR description and tests provide all the context a reviewer needs.
- Greedy MLX decoding: `sampler=lambda x: mx.argmax(x, axis=-1)`, not `temperature=0`
- Don't override `eos_token_id` - use generation_config
- Use separate tokenizers for transformers/MLX tests
- `apply_chat_template`: use `tokenize=True, return_tensors="pt"` directly
- MPS limitations: use CPU for comparison tests
- Hybrid models: RoPE is often disabled (`position_embedding_type: "nope"`)
- Every layer may need MoE block, not just attention layers

## Output

Upon success, please save the mlx implementation in the appropriate place inside `mlx-lm/mlx_lm/models`, and generate a summary report with the results from the tests.

On failure (only declare when you run out of ideas after multiple iterations), please report your analysis as well as the results from tests you run.

## List of scripts

Bundled scripts in `scripts/` (relative to this skill):

| Script | Purpose |
|--------|---------|
| `resolve_dtype.py` | Resolve expected runtime dtype from config or safetensors header (Phase 1, Phase 4 / Test 2, Phase 5) |
| `check_dtype.py` | Verify a model's forward-pass output dtype matches an expected value (Phase 4 / Test 2, Phase 5) |
| `compare_generation.py` | Full text generation comparison (Phase 4 / Test 1) |
| `compare_predictions.py` | Forward pass comparison with tolerance analysis and top-k overlap (Phase 4 / Test 3) |
| `compare_layers.py` | Per-layer hidden state + logits comparison (Phase 4 / Test 4) |
| `debug_transformers.py` | Analyze transformers model (embeddings, logits, top predictions) |
| `debug_mlx.py` | Analyze MLX model (same output format as `debug_transformers.py`) |

**Recommended order for the comparison flow:**
1. `compare_generation.py` — quick sanity check (is output coherent?)
2. `compare_predictions.py` — numerical analysis (do predictions match?)
3. `compare_layers.py` — find divergence (where does it break?)

Usage:
```bash
# Resolve and verify dtype
python scripts/resolve_dtype.py /path/to/model
python scripts/check_dtype.py /path/to/model bfloat16

# Full generation comparison
python scripts/compare_generation.py /path/to/model --message "What is 2+2?"

# Numerical comparison with tolerance analysis
python scripts/compare_predictions.py /path/to/model "The quick brown fox..."

# Per-layer + logits comparison
python scripts/compare_layers.py /path/to/model "The quick brown fox..."
```

## References

| Reference | Purpose |
|-----------|---------|
| [Model Discovery and Config Analysis](references/model-discovery-and-config-analysis.md) | Hub search, config diffing, weight format detection |
| [Weight Sanitization](references/weight-sanitization.md) | sanitize() patterns, idempotency, shared weights, ordering |
| [Conversion and Quantization](references/conversion-and-quantization.md) | mlx_lm.convert usage, quantize-first workflow |
| [MLA](references/mla.md) | Multi-head Latent Attention, kv_b_proj splitting, rope_parameters |
| [Hybrid and SSM Models](references/hybrid-and-ssm-models.md) | Cache construction, layer dispatch, CUDA-only deps |
| [Large Models](references/large-models.md) | Wired memory, OOM workarounds, MoE memory pressure |
| [Distributed Inference](references/distributed-inference.md) | mlx.launch, hostfiles, rsync, tensor parallelism |
| [Common Infrastructure Changes](references/mlx-common-infrastructure.md) | Safe modifications to shared mlx-lm code |
| [GitHub PR Workflow](references/github-pr-workflow.md) | Feature branches, targeting correct repo, `gh pr edit` tips |
| [Code Simplification](references/code-selection-simplification.md) | Dead branch removal, reference model patterns |

<!-- Missing: training -->
