# Landing this in OLMo-core

The last time kernels from this repo landed in the training repo, the ladder reported −3%
tokens/sec and it took two days to establish that there was no steady-state regression at
all (the ladder repo's `kernels/gnorm/LADDER-REGRESSION.md`). Almost none of that time went
into the kernels.
This checklist exists so that does not happen twice.

## 1. The call site

**The unit of sharing is this package** (state as of 2026-09-08; the repo split below is
2026-09-09). OLMo-core gets it one of two ways, on two branches that are otherwise
identical:

- `caleb/cute-kda-vendored` — the package tree copied to `src/olmo_core/kernel_fun/`,
  byte-identical to this repo's `src/kernel_fun/` except the top-level `__init__.py`, which
  carries `VENDORED_FROM`. No private dependency, so no tokens. scaling-ladders'
  `caleb/cute-kda` points here.
- `caleb/cute-kda` (PR #837) — installs the package as a `kernel-fun` extra pinned to a sha.
  Needs a GitHub token everywhere the lock resolves.

> **The shas in both places changed meaning on 2026-09-09**, when this package moved out of
> the ladder repo — which held the name `allenai/kernel-fun` until that day and is now
> `allenai/kernel-fun-dev`, and where this tree was `packages/kernel-fun/` — into the repo
> that took the name, **`allenai/kernel-fun`** (this one). `VENDORED_FROM` and the pinned
> extra now name a commit HERE, and the extra's URL drops
> `#subdirectory=packages/kernel-fun`. The last pre-split vendoring was ladder sha
> `7a6983b`, which exists only in `kernel-fun-dev`; the ladder sha a family's *kernels*
> were cut from lives on in `src/kernel_fun/<family>/_provenance.py::SOURCE_COMMIT`
> (`6fc6309` today) and is a different number. When re-vendoring, bump `VENDORED_FROM` to a
> full kernel-fun sha and say so in the commit message — a bare sha is now ambiguous.

The extra's URL, for reference:

```
kernel-fun @ git+https://github.com/allenai/kernel-fun.git@<sha>
```

Three rules for that extra, from reading OLMo-core's build (2026-09-09):

- **Bare `kernel-fun`, no `[cu13]`/`[cu12]`.** OLMo-core's images already carry the CuTe
  DSL through the `fa4` extra (flash-attn-4 -> nvidia-cutlass-dsl), and the CUDA major is
  decided once, in the Dockerfile (`CUDA_VERSION_PATH`, and `FLASH_ATTN_4_EXTRAS='[cu13]'`
  on the B300 image). One extra then works on both the cu128 and cu130 images; the
  package's own CUDA extras are for environments that have no DSL at all. Nothing in the
  bare install replaces the image's torch/triton/fla — the floors are below both images.
- **The git URL cannot sit in the extra** if `ai2-olmo-core` is to keep publishing: PyPI
  rejects metadata with a direct-URL requirement (the pyproject says so at `dion`). Put
  the source in `[tool.uv.sources]` as `dion` does, or publish kernel-fun to PyPI and pin
  a version.
- **fla must be 0.5.2 on the branch that merges.** The package requires
  `fla-core>=0.5.2`; a branch still on flash-linear-attention 0.4.1 (the B300 image
  branch, today) would end up with a mixed `fla/` tree.

If a cu130 image is ever built with FA4's bare requirement, the package logs a
`CUDA 12 one (nvidia-cutlass-dsl-libs-cu12 without -cu13)` warning at first use — see
`support.cute_cuda_mismatch`. It warns rather than falls back, because the wrong-build DSL
may still compile; treat the line as a build-arg bug.

Both route `flash_linear_attn_api.py::dispatch_chunk_kda` and `dispatch_causal_conv1d` to
the package when `KimiDeltaAttentionConfig.use_cute_kernel=True`; that one flag drives BOTH
families (it is plumbed to the three Q/K/V `CausalConv1d`s). There is no other copy of
these kernels in OLMo-core — the old frozen `nn/attention/kda_cute/` tree went three ideas
stale before it was deleted, which is why the package exists. Do not reintroduce one.

**To ship a release:** commit/push **kernel-fun** (this repo — tag it if the version
moved); on OLMo-core's vendored branch re-copy the changed files, bump `VENDORED_FROM` to
the full kernel-fun sha, bump the scaling-ladders submodule; on the package branch bump
the sha in the extra and re-lock. Then §2–§3 below. Nothing in this flow touches the ladder
repo — a ladder commit only ever enters through `tools/vendor.py` (README, "Two repos").

The kda call site, for reference:

```python
# flash_linear_attn_api.py
if use_cute_kernel:
    from kernel_fun.kda import chunk_kda as cute_chunk_kda

    return cute_chunk_kda(
        q=q, k=k, v=v, g=g, beta=beta, A_log=A_log, dt_bias=dt_bias,
        scale=scale, initial_state=initial_state,
        output_final_state=output_final_state,
        use_qk_l2norm_in_kernel=use_qk_l2norm_in_kernel,
        use_gate_in_kernel=use_gate_in_kernel,
        cu_seqlens=cu_seqlens,
    )
```

The package decides internally and falls back to fla itself, so a packed-document batch or
a non-Blackwell node needs no branch in the caller (the old `cute_kda_supported` is gone).

**The conv call site**, same file, is the second family. `CausalConv1d.forward`
(`src/olmo_core/nn/convolution.py`) reaches the package through `dispatch_causal_conv1d`:

```python
# flash_linear_attn_api.py
def dispatch_causal_conv1d(x, weight, bias, activation, backend="triton", cu_seqlens=None):
    from kernel_fun.cconv import causal_conv1d

    return causal_conv1d(
        x=x, weight=weight, bias=bias, activation=activation, backend=backend,
        cu_seqlens=cu_seqlens,
    )
```

No flag: the package forwards anything off its box (bias, cu_seqlens, `activation=None`,
`backend="cuda"`) to fla itself, and `KERNEL_FUN_CCONV_DISABLE=1` is the whole-family
switch. Like the kda entry point, this one IS `torch.compiler.disable`d — as of
2026-09-04. It was not, on the theory that fla's conv is plain Python around an
autograd.Function and so is ours, so Dynamo would treat the two alike. The 30M mainline
ladder falsified that: Dynamo speculated OUR Function's backward (two tensor arguments is
the shape it agrees to trace; fla's eleven-argument one is not) and asserted inside
`cconv_bwd` on a symbolic `dy.stride(0)`. So this entry point costs ONE graph break that
fla does not — expect §3's break diff to show it, at three convs per KDA layer, and judge
it against the ~36 ms/step the kernels return rather than against zero.

Three things the caller should still do:

```python
kernel_fun.kda.warmup(K=head_dim, V=head_v_dim, HV=n_v_heads)   # before step 1
kernel_fun.cconv.warmup(B=microbatch, T=seq_len, D=(key_dim, value_dim))   # ditto
```

Do NOT call `versions()` from the model's `forward` to log it. Both entry points log it
themselves, once, the first time either family engages — and they are
`torch.compiler.disable`d, so the line costs no graph break. The caller-side version of
this cost two breaks in the KDA layer's compiled block and raised
`TypeError: unhashable type: 'dict'` through olmo-core's `lru_cache`-based `log_once`
(2026-09-04). `versions()` stays public for a startup log outside any compiled region.

The cconv autotune key is `(D, W, B, T)`, so its warmup must see the REAL microbatch and
sequence length and every channel count the layer convolves (q/k at `n_heads*head_dim`,
v at `expand_v` times that). A shape it has not seen re-autotunes at first use: a few
seconds, once, per shape — fine for training, but it is what a step-1 "regression" looks
like.

The old wrapper computed the gate activation in eager torch. Do not reintroduce that: pass
`use_gate_in_kernel=True` and let the package fuse it into the cumsum. At prod8192 the
eager form costs ~2 ms and ~2 GiB of saved activations per layer, which is a third of what
these kernels win.

## 2. Before the first real run

- [ ] `pytest -q` from this repo on a B300, green (`-m slow` adds the prod-shaped rows;
      the cconv tests also run on an H100).
- [ ] `PYTHONPATH=src python tools/prodtime.py` on that B300 — the package's own numbers at
      the production shapes, next to fla's, from the installed copy. (The ladder's
      `python -m loop bench kda --impl 000,005 --case prod8192_gate` and
      `... bench cconv --impl 000,001 --case prod8192_qk` are the recorded originals.)
- [ ] Confirm fla's Triton autotune cache directory is persistent and pre-warmed in the
      training image. Otherwise every rank re-autotunes at step 1 and the startup cost you
      just moved with `warmup()` comes back through another door.
- [ ] Grep the startup log for the `kernel-fun kda: engaged` line (and `cconv: engaged`).
      If either says `falling back` instead, the reason is on the same line — read it
      before looking at anything else. The `kernel-fun {...}` versions line appears just
      above the first of them; if it is missing, neither family ever engaged.

## 3. The A/B that settles it

Three arms, same GPU, same node, first step discarded, enough metric windows to be real
(the 1.4b gnorm run was killed after 7 windows, and half the "−3%" came from reading the
average anyway):

1. fla (`use_cute_kernel=False`, conv routed to fla)
2. kernel-fun, both families
3. kernel-fun with `KERNEL_FUN_DISABLE=1`

Arm 3 is the control that separates *the wrapper* from *the kernels*: it runs the same
call path and the same fallback logic but fla's kernels underneath. If arm 3 is not within
noise of arm 1, the problem is integration, not numerics, and no amount of kernel work will
fix it. If arm 2 disappoints, `KERNEL_FUN_KDA_DISABLE=1` / `KERNEL_FUN_CCONV_DISABLE=1`
split it by family without a config change.

A fourth arm exists only for a model whose KDA grid is below the chain-level floor —
`B * HV * (V//64) < 256`, which the small OLMoE3 candidate's B4/HV8/V256 is, at 128.
`KERNEL_FUN_KDA_MIN_CTAS=128` moves that floor so those calls dispatch here instead of
reporting `grid too small` and going to fla. It is a measured opt-in for one shape on one
box, not a better default: the b1 scan and dhu backwards keep their own 256-CTA floors and
stay on fla at that grid, so the arm is worth running only against arm 1, on the model you
intend to train, and only after the log stops saying `grid too small`. Set it for
`warmup()` too — it warms one grid per floor in play, and the stages this arm adds are
autotuned in step 1 otherwise.

Then:

- [ ] **`TORCH_LOGS=recompiles,graph_breaks`, diff arm 1 against arm 2.** Free — the Beaker
      launcher sets it already. At the kda call the counts must be EQUAL: fla's own
      `chunk_kda` is `@torch.compiler.disable`d too, so that one MOVES a break rather than
      adding one. At the conv, expect arm 2 to show exactly ONE more break per conv call
      (three per KDA layer) — see §1; more than that, or a recompile loop, is a bug.
      Do this first; it is the cheapest way to catch the failure mode that cost two days.
- [ ] **torch-profile ~20 steps, compare CPU gap time between GPU kernels** across arms.
      That is where a host-side regression shows up and no benchmark in this repo can see
      it. While you are in the profile, check that no `softplus` / `mul` / `to_copy` at
      `[B,T,HV,K]` survives — if they do, the gate is not fused and you are paying twice.
      And check the conv: `cconv_fwd_strip` / `cconv_bwd_strip` should be the only conv
      kernels, and `causal_conv1d_fwd_kernel` should appear NOWHERE in the backward (fla
      re-ran the forward there to rematerialize the pre-activation; ours does not).
- [ ] **`torch.cuda.memory_summary()` after ~5 steps**, both arms. Active memory should be
      within a few hundred MiB. The call caches used to pin ~24 GiB/rank at these shapes;
      that is fixed and tested, and this is the check that keeps it fixed.
- [ ] Report `throughput/device/TPS (actual avg)` with step 1 discarded.

## 4. What to expect

**kda.** At the production call the op measures **1.540x** (23.74 ms vs fla's 36.56 at
B=16, T=8192, H=HV=16, K=128, V=256; 2026-09-02). The 1.288x port was worth 1.037x
end-to-end on the 1.4b mainline ladder, which puts KDA at ~16% of step time; the same
arithmetic gives **~1.06x** here, i.e. about +6% tokens/sec. Relative to the branch's
current 1.545x chain the new wy stage is +0.03x on the op — real, small, and the same
arithmetic says ~+0.3 points of TPS. Do not expect to see it in a noisy A/B.

**cconv.** The 810m/B300 trace (the ladder's `profiles/810m-b300-20260901.md`) put the three conv calls
at ~50 ms of a ~520 ms step: bwd 35.0 + fwd 7.7 + the backward's own forward re-run 6.9.
At the measured 4.65x / 1.62x that is ~13 ms — **~36 ms/step back, about 7% of the step,
~1.075x tokens/sec at 810m**. The conv channel count is set by head count, which the
ladder pins from 810m up, so the fraction survives scale. This is the larger of the two
predictions and the easier one to see.

Both predictions assume the ops' step-time fractions are unchanged, and they are the
numbers to check against the A/B rather than to quote from. Judge the port on its fraction
of real step time — that is the one durable lesson from last time.
