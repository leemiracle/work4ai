# GitHub PR Workflow

Guidelines for submitting PRs from model conversion work.

## Feature Branch Workflow

Always create a feature branch for your changes — never commit directly to the main/conversions branch:

```bash
git checkout -b add-<model_type>
# ... make changes, commit ...
git push -u origin add-<model_type>
gh pr create --base conversions --head add-<model_type>
```

This keeps the base branch clean and makes it easy to iterate on review feedback without affecting other work.

## Targeting the Correct Repository

The skill specifies a target repo and branch at the top of SKILL.md. Always use that repo for PRs, even if it's a fork rather than the upstream project. Double-check with `git remote -v` before pushing.

**Common mistake:** Opening a PR against the upstream repo (e.g., `ml-explore/mlx-lm`) instead of the fork specified in the skill config. This creates noise for upstream maintainers and may leak in-progress work.

## PR Description

The canonical list of what the PR body must contain lives in **SKILL.md, Phase 8**. Read it before drafting the PR.

Operationally:
- The initial PR body should be **one focused write-up**, not split across several comments. Avoid pasting intermediate debugging output or results from wrong configurations.
- After opening the mlx PR, open the test manifest PR (see "Test Manifest" below).
- Then edit the mlx PR description (`gh pr edit <number> --body-file ...`) to add a pointer to the manifest PR so the maintainer can run the full battery via the harness.

## Editing PRs After Creation

If `gh pr create` fails or you need to update the PR:

```bash
# Update title
gh pr edit <number> --title "New title"

# Update body (use a file to avoid shell escaping issues)
gh pr edit <number> --body-file pr_body.md

# Add to existing PR by pushing more commits to the same branch
git push origin add-<model_type>
```

**Note:** `gh pr edit --body` with inline text can hit shell escaping issues with special characters. Writing the body to a temp file and using `--body-file` is more reliable.

## Test Manifest

After the mlx-lm PR is created, generate a test manifest and open a PR to `pcuenca/mlx-lm-tests`. The maintainer will merge the manifest PR and run the test harness against the model PR.

### Manifest format

```yaml
version: 1
pr:
  number: 42                       # mlx-lm PR number
  repo: pcuenca/mlx-lm             # mlx-lm repo (fork or upstream)
  branch: add-<model_type>         # PR head branch
model_type: <model_type>           # Python module name in mlx_lm/models/
variants:
  - repo_id: org/Model-7B
    type: base                     # "base" (completion) or "instruct" (chat)
    memory_gb: 16                  # estimated unquantized memory in GB
    expected_dtype: bfloat16       # expected forward-pass output dtype
  - repo_id: org/Model-7B-Instruct
    type: instruct
    memory_gb: 16
    expected_dtype: bfloat16
quantize: true                     # set false for natively quantized models
notes: >                           # optional, free-form context for the reviewer
  Any unusual aspects of this conversion worth noting.
```

### How to determine the fields

The source of truth is this schema from the `pcuenca/mlx-lm-tests` repo: https://github.com/pcuenca/mlx-lm-tests/blob/main/harness/manifest-schema.yaml

- **`pr.number`** and **`pr.branch`**: from the (fork of) mlx-lm PR you just opened.
- **`model_type`**: the Python module name (e.g., `olmo_hybrid`), same as the filename you created in `mlx_lm/models/`.
- **`type`**: `"base"` for completion/foundation models, `"instruct"` for chat/instruction-tuned models. This controls which prompts the harness uses.
- **`memory_gb`**: estimate from model size × 2 bytes (for bf16). A 7B model is ~14 GB.
- **`expected_dtype`**: resolve with `scripts/resolve_dtype.py` (config first, safetensors header as fallback). Use the same value you reported in the conversion report.
- **`quantize`**: `true` unless the model ships with native quantization (e.g., MXFP4).
- **`notes`**: highlight anything the test harness might not catch — e.g., per-variant RoPE differences, unusual architectures, known precision-sensitive operations.

### Procedure

1. Create the manifest as `manifests/pr-<N>.yaml` (where N is the mlx-lm PR number).
2. Fork `pcuenca/mlx-lm-tests` if you haven't already.
3. Push the manifest and open a PR:

```bash
# Clone your fork
gh repo fork pcuenca/mlx-lm-tests --clone
cd mlx-lm-tests

# Add the manifest
mkdir -p manifests
cp /path/to/manifest.yaml manifests/pr-<N>.yaml

# Commit and PR
git checkout -b manifest-pr-<N>
git add manifests/pr-<N>.yaml
git commit -m "Add test manifest for PR #<N> (<model_type>)"
git push -u origin manifest-pr-<N>
gh pr create --repo pcuenca/mlx-lm-tests \
  --title "Test manifest for PR #<N> (<model_type>)" \
  --body "Manifest for https://github.com/pcuenca/mlx-lm/pull/<N>"
```

Use the correct repository URL for the MLX fork we are working with.

## Multi-Model PRs

When converting multiple variants of the same architecture (e.g., dense + MoE), it's usually better to submit them as a single PR with clear commit separation, unless the implementations are substantially different.
