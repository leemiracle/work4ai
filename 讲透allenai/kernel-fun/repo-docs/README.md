# kernel-fun

> **Experimental, in development.** These kernels have only been tested on B300 GPUs, for
> the specific model configurations our training runs use. They exist to make those runs
> faster and are not tested for general use — outside that hardware and those shapes, treat
> both the correctness and the speed as unknown.

Drop-in replacements for flash-linear-attention's linear-attention ops, on Blackwell.

```python
from kernel_fun.kda import chunk_kda          # instead of: from fla.ops.kda import chunk_kda
from kernel_fun.cconv import causal_conv1d    # instead of: from fla.modules.convolution import causal_conv1d
```

Same signature, same returns. Any call this package does not implement — wrong
architecture, wrong shape, a flag it has never seen, a CUDA graph capture of a shape that
has not run eagerly yet — is forwarded to fla verbatim. Installing it can change how fast a
model trains, not what it computes beyond kernel-level rounding.

## Two repos — where to ship changes

Split out of the research ladder on 2026-09-09. Two repos, one direction of flow:

| | | |
|---|---|---|
| **`allenai/kernel-fun-dev`** | the research ladder | `loop/` + `kernels/<family>/ideas/*` — forks, falsifications, recorded bench rows and their `history/`. Nothing there is installable. |
| **`allenai/kernel-fun`** | this repo | the release artifact: the winning chain only, knobs frozen, dead branches gone. The only thing that builds a wheel, and the only route into OLMo-core. |

```
kernels/kda/ideas/005-*/  --(tools/vendor.py)-->  src/kernel_fun/kda/_kernels/  --(INTEGRATION.md §1)-->  OLMo-core
      ladder repo                                        this repo
```

- **A new kernel idea, or a change to one that is still being falsified:** the ladder. It
  owns the bench, the oracle and the `code_sha` that makes `code_unchanged_since` mean
  something.
- **A change to what ships** — a released stage, the fallback gate, the call cache, the
  public signatures, the tests, the version: **here**. Never by editing OLMo-core's copy.
- **A won ladder row that should ship:** `python tools/vendor.py --family <f> --from-commit
  <ladder sha>` here, then its checklist by hand, then a release ("Releasing" below).
  `tools/vendor.py` and `tools/drift.py` need a ladder checkout: they default to
  `../kernel-fun-dev` beside this repo, and take `--ladder PATH` or `$KERNEL_FUN_LADDER`.
- Version tags (`v0.2.0`, …) live **here**. `_provenance.py`'s `SOURCE_COMMIT` is a sha in
  the *ladder*; `VENDORED_FROM` in OLMo-core is a sha in *this* repo.

**On the names — `allenai/kernel-fun` means THIS repo, and only since 2026-09-09.** Before
that date it was the research ladder, which was renamed `kernel-fun-dev` to hand the name
over. Three consequences worth knowing:

- The pip/import name has been `kernel-fun` / `kernel_fun` throughout and did not change, so
  nothing downstream — OLMo-core's extra, `caleb/cute-kda-vendored`, the wheel — moved
  because of any of this.
- **`kernel-fun` in anything written before 2026-09-09 means the ladder, not this repo.**
  That includes commit messages, `git log` subjects, lockfiles, `VENDORED_FROM` shas and
  image tags. Check the date before chasing a path or resolving a sha; a pre-split
  `kernel-fun` sha will not exist in this repo's history, which starts at the split.
- The old redirect is gone. `allenai/kernel-fun` used to redirect to the renamed ladder;
  creating this repo under that name retired the redirect, which is exactly why it was done
  this way. Anything still pointing at that URL for the *ladder* now silently reaches the
  *package* — repoint it at `kernel-fun-dev`. A Beaker image named `kernel-fun-<date>` is
  the ladder's image and deliberately keeps that name (its `scripts/image.sh` explains why).

## Status and numbers

| family | status | production shape, B300 |
|---|---|---|
| `kda` | shipping | fwd+bwd **23.74 ms vs fla 36.56 = 1.540x** (gate + q/k norm in-op; B16 T8192 H=HV16 K128 V256) |
| `cconv` | shipping | isolated bwd **0.344 ms vs fla 1.597 = 4.65x**, fwd 0.190 vs 0.307 = 1.62x (B16 T8192 D2048 W4) |
| `gdn`, `gnorm` | to follow | — |

The kda numbers, measured 2026-09-02 on holmes-cs-aus-515 (the ladder's kda/005 record 001):

| row | fla | kernel-fun | |
|---|---|---|---|
| fwd+bwd, gate and norm in-op (the production call) | 36.56 ms | 23.74 ms | **1.540x** |
| fwd+bwd, pre-computed gate | 34.90 ms | 21.80 ms | 1.601x |
| fwd only | 7.50 ms | 5.95 ms | 1.260x |
| fwd+bwd at B=8 (the 1.4b ladder's real microbatch) | 17.80 ms | 11.30 ms | 1.575x |

(The previous release quoted 1.545x on the production row from a different node and day;
the fla baseline moved more than our chain did. Same-run, the transposed wy stage this
release adds is worth +0.03x on every prod row over the previous chain.)

The cconv numbers, measured 2026-09-01 on B300 (the ladder's cconv/001 record 002), one
call, isolated with CUDA events — the number a training step feels, since the bench's
fwd+bwd rows at this size are pinned by the harness's own per-iteration floor:

| call (B=16, T=8192, W=4, bf16 x, fp32 weight) | fla | kernel-fun | |
|---|---|---|---|
| backward, D=2048 (q/k) — dx and dw, no forward re-run | 1.597 ms | 0.344 ms | **4.65x** |
| forward, D=2048 (q/k) — silu fused | 0.307 ms | 0.190 ms | 1.62x |
| D=1024 and D=4096 | | | same ratios |

Both families re-measured from the installed package on 2026-09-02 (`tools/prodtime.py`,
holmes-cs-aus-515, same B300 under a live session so absolute ms run higher than the
records): kda **1.541x**, cconv fwd 1.62x / 1.63x and isolated bwd **4.25x** (D=2048) /
**4.60x** (D=4096). The ratios are the records'; the package runs the ladder's kernels.

At the 810m step (12 KDA layers, B=8) the trace put the three conv calls at ~50 ms of a
~520 ms step; these ratios predict ~13 ms, i.e. roughly **7% of the step** — larger than
the kda increment in this release. And 1.54x on kda at ~16% of step time predicts about
+6% tokens/sec. Confirm both on a real step before believing either; an op-level ratio is
not a training result.

## Install

```
pip install kernel-fun                                                          # from PyPI
pip install "kernel-fun @ git+ssh://git@github.com/allenai/kernel-fun.git@v0.2.0"  # or a tag
```

(`0.2.0` is the first non-pre-release on PyPI; `0.2.0.dev0`/`.dev1` were the rehearsals and
plain `pip install` skips them. Tags live in this repo, so a git pin takes `@v0.2.0` or a
sha. The URL no longer carries `#subdirectory=packages/kernel-fun` — that was the path
inside the ladder repo, before the 2026-09-09 split.)

The base install declares torch, triton and `fla-core` only, with loose floors, so it never
replaces the torch/triton a training image was built against. The CuTe DSL and cuda-python
are **not** dependencies: they ride in with the training image, and when they are missing
the kda family logs a reason and runs fla. An environment that needs them installed picks
the extra for its CUDA major — the CuTe DSL ships separate CUDA 12 and CUDA 13 library
wheels, and the bare `nvidia-cutlass-dsl` requirement is the CUDA 12 one:

```
pip install "kernel-fun[cu13] @ git+ssh://..."   # CUDA 13 torch (the production image)
pip install "kernel-fun[cu12] @ git+ssh://..."   # a cu128 torch; untested since the image moved
```

**Tested against** — the only stack these kernels have run on. Everything else is where the
version floors say it should work, not where anyone has checked:

| | |
|---|---|
| GPU | B300 (sm_103; `arch_ok` admits any sm_10x, so B200 too) |
| CUDA | 13.0 (torch `2.11.0+cu130`) |
| torch / triton | 2.11.0 / 3.6.0 |
| CuTe DSL | `nvidia-cutlass-dsl` 4.6.0.dev0, CUDA 13 libs |
| flash-linear-attention | 0.5.2 (`fla-core`; `TESTED_FLA` in `_common/compat.py`, warns on anything else) |
| Python | 3.12 |

The cconv family is Triton-only and gated at sm90, so an H100 runs it — at a speed nobody
has measured.

Prefer that over `pip install -e`, which writes a `.pth` pointing back into a checkout and
reintroduces "which copy am I running".

**Inside the kernel-tuning image** the ladder is baked at `/work` but this repo is not, so
clone it beside the ladder and put its `src/` on the path (`/work` is writable, and the
image has `openssh-client`):

```sh
git clone git@github.com:allenai/kernel-fun.git /work/kernel-fun
export PYTHONPATH=/work:/work/kernel-fun/src
```

In a session the ladder is `/work` itself — the tools' sibling default would look for
`/work/kernel-fun-dev`, which does not exist — so `export KERNEL_FUN_LADDER=/work` (or pass
`--ladder /work`) before running `tools/vendor.py` or `tools/drift.py` there.

`torch`, `triton` and `fla-core` are required. The CuTe DSL (`nvidia-cutlass-dsl`) and
`cuda-python` are deliberately **not** hard requirements: they arrive with the training
base image, and letting pip resolve them risks swapping that build out. Without them the
package still imports and still computes correctly — it just falls back to fla everywhere.
Install the `cute` extra if you need them.

## Using it

```python
import logging
import kernel_fun
from kernel_fun import kda, cconv

logging.getLogger("kernel_fun").setLevel(logging.INFO)   # one line per process per family
# `versions()` is logged for you the first time a family engages, from inside the
# torch.compiler.disable'd entry point. Call it yourself only OUTSIDE a compiled region.

kda.warmup(K=128, V=256, HV=16)                    # compile before step 1, not during it
cconv.warmup(B=microbatch, T=seq_len, D=(2048, 4096))   # autotune at the REAL B, T, D

q, _ = cconv.causal_conv1d(x=w_q(x), weight=conv_w, activation="silu")
o, ht = kda.chunk_kda(q, k, v, g, beta, A_log=A_log, dt_bias=dt_bias,
                      use_qk_l2norm_in_kernel=True, use_gate_in_kernel=True)
```

`warmup()` matters. Four `cute.compile` calls plus fla's Triton autotuning is tens of
seconds; paid inside step 1 it looks exactly like a regression — which is what a previous
port's reported "−3% tokens/sec" turned out to be. It also runs the fla compatibility probe,
so a version mismatch raises before the run rather than at step 40,000.

Both families have an `is_supported(...)` returning `(ok, reason)`. The reason string is
meant for a training log: a silent fallback reads as a correct 1.00x, and "did the kernels
actually run?" is the most expensive question a port can leave open. The package logs it
once per process.

### Supported — kda

`chunk_size=64`, `T % 64 == 0`, `K ∈ {64, 128}`, `V % 64 == 0`, bf16/fp16, sm100
(B200/B300), a grid of at least 256 CTAs (`B * HV * (V//64)`; `KERNEL_FUN_KDA_MIN_CTAS`
moves that one number and nothing else — see Switches). Under CUDA graph capture the shape must already
have run eagerly (fwd, and bwd if grads are needed): compile and autotune cannot be
captured, but a warm shape captures and replays bit-identically, on any stream. Within that:
`use_qk_l2norm_in_kernel`, `use_gate_in_kernel` (with `A_log`/`dt_bias`, fused into the
cumsum), `use_beta_sigmoid_in_kernel`, `allow_neg_eigval`, GVA (`HV > H`),
`initial_state=None`, `output_final_state=False`, fp32 `beta` (cast to q's dtype — the one
numerics deviation, covered by a test).

Stages also fall back individually below their own floors — most notably the MMA intra
backward, which needs `B * (T/64) * HV >= 1024` and otherwise uses a Triton kernel that is
faster at that size. `is_supported` reports the chain-level gate; the per-stage ones are
performance choices, and the launch-witness test is what pins them down. They do not
follow the chain-level gate down: at a configured 128 CTAs the b1 scan and dhu backwards
are still fla's, and what the opt-in buys is the forward scan, the transposed WY backward
and the intra backward.

Everything else goes to fla: `cu_seqlens` and packed documents, context parallel,
`safe_gate`, `state_v_first`, `disable_recompute`, `return_intermediate_states`,
`chunk_size=32`, and any argument the package does not recognize — a new fla flag degrades
to fla rather than being silently ignored.

### Supported — cconv

Exactly the KDA layer's mainline call: `activation` silu/swish, no bias, no residual, no
initial/final state, no `cu_seqlens`, `backend="triton"`, `W <= 4`, bf16/fp16 `x` of shape
`[B, T, D]` with any strides (production hands over a projection output and fla does not
force it contiguous either), a `[D, W]` weight in any float dtype, `dw` back in the weight's
dtype. Both kernels are Triton, so the arch floor is **sm90**, not sm100 — but they have
only been *timed* on B300; an H100 computes the same numbers at an unmeasured speed.

Everything else — bias, residual, conv state, packed documents, `activation=None`, an
explicit `backend="cuda"`/`"mix"`, any unrecognized flag — goes to fla verbatim.

### Switches

| variable | effect |
|---|---|
| `KERNEL_FUN_DISABLE=1` | forward everything to fla. The 2am switch. |
| `KERNEL_FUN_KDA_DISABLE=1`, `KERNEL_FUN_CCONV_DISABLE=1` | same, one family |
| `KERNEL_FUN_DEBUG=1` | log the fallback reason |
| `KERNEL_FUN_FALLBACK=1` | downgrade an fla-drift error to a warning + fallback |
| `KERNEL_FUN_KDA_MIN_CTAS=<n>` | move the kda chain-level CTA floor off 256. Per workload, per measurement |

All read per call, and a value that is not a positive integer is a warning and the default,
not an exception — a launcher typo should cost throughput, not the run. There are
deliberately no per-stage knobs: `MIN_CTAS` is the dispatch gate, not a stage, and bisecting
a stage means reaching for the research ladder, which keeps all of them.

`KERNEL_FUN_KDA_MIN_CTAS` is the one knob that can make things *slower*: 256 is where the
CuTe scans stop underfilling the GPU on the shapes measured so far, and lowering it is a
claim about one model on one box. The small OLMoE3 candidate (B4/T8192/HV8/K128/V256 — 128
CTAs) is the shape it exists for. Time it against the default before believing it, and give
`warmup()` the same environment the run will have: it warms one grid per floor in play.

## How it relates to the research repo

This package is a **release artifact**, not a mirror — see "Two repos" above for which
change goes where. The ladder (`allenai/kernel-fun-dev`, `kernels/<family>/ideas/*`) stays free
to fork and falsify; when an idea wins a recorded bench row, `tools/vendor.py` copies that
commit's kernels here and prints a checklist of the edits it cannot do (freeze the env
knobs, delete the branches they selected, unify the call cache). `_provenance.py` records
which ladder commit each family came from — its paths are ladder-relative, which is why
`tools/drift.py` needs a ladder checkout to report what has moved since. The real check that
the two agree is the parity test, not a hash.

For kda that is ~10 modules of the ladder's ~13k lines: the forward scan+readout and four of
the backward's seven stages. The rest of the chain is fla's own kernels at fla's own stage
boundaries — which is what makes a stage-by-stage comparison meaningful, and why the tests
can hold to fla's own tolerances. For cconv it is one module: both directions, whole.

## Releasing

Published to PyPI as [`kernel-fun`](https://pypi.org/project/kernel-fun/) by
`.github/workflows/release.yml`. Auth is **Trusted Publishing**: GitHub mints a short-lived
OIDC token for the job, PyPI checks four claims against a publisher entry it holds, and
trades it for an upload token good for minutes. No API token exists in this repo, in GitHub
secrets, or on anyone's laptop. The four claims are owner `allenai`, repository
`kernel-fun`, workflow filename `release.yml`, and the environment — so **renaming that
workflow file, or an environment, breaks publishing** until the entry on PyPI is edited to
match. That is the one non-obvious way this setup fails.

| index | trigger | environment |
|---|---|---|
| TestPyPI | Actions → Release → Run workflow, target `testpypi` | `testpypi`, ungated |
| PyPI | push a `v*` tag | `pypi`, manual approval, `v*` tags only |

Cutting a release:

```sh
# 1. bump __version__ in src/kernel_fun/__init__.py  (the ONLY place it lives)
# 2. rehearse on TestPyPI first -- it is the only way to exercise the real upload path
gh workflow run Release -f target=testpypi
# 3. tag; the build refuses a tag that disagrees with __version__, then waits for approval
git tag v0.2.0 && git push origin v0.2.0
```

Two things here cannot be undone, which is what the approval gate and the tag check are
for: **a version number is burnable once** — deleting `0.2.0` from PyPI does not let you
re-upload it, so a bad release is fixed by shipping `0.2.1`, never by replacing it — and a
release with a tag that disagrees with the metadata inside the wheel cannot be corrected in
place. Installing from TestPyPI needs both indexes, since torch and `fla-core` are not
mirrored there:

```sh
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ --pre kernel-fun
```

## Licensing

Apache-2.0 (`LICENSE`), matching the research ladder and Ai2's default. Three of the Triton
modules are derived from flash-linear-attention, which is MIT: `NOTICE` names them module by
module and reproduces the MIT terms, which keep applying to those portions.
`THIRD_PARTY_NOTICES.md` covers the rest of the dependency set — torch (BSD-3-Clause),
triton (MIT), and the NVIDIA-licensed CuTe DSL and cuda-python that arrive with the base
image — none of which are vendored here. All three files ship inside the wheel —
`license-files` in `pyproject.toml` puts them there, which is what makes the attribution
travel with an install rather than living only in this checkout.
