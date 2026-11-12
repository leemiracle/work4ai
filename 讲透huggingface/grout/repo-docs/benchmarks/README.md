# Qwen3 Benchmark Harness

This directory contains the benchmark harness used for the Grout paper runs.
It is intentionally separate from the normal `grout` inference CLI.

## Contents

| Path | Purpose |
|---|---|
| `src/bin/grout_bench.rs` | Grout timing binary. Built only with `--features benchmarks`. |
| `bench_sglang.py`, `bench_vllm.py`, `bench_llama_cpp.py`, `bench_trtllm.py` | Single-request wrappers for comparison engines. |
| `sweep_tg*.sh` | Decode-length sweeps at fixed prompt length. |
| `sweep_pp*.sh` | Prompt-length sweeps at fixed decode length. |
| `aggregate_sweep.py` | Builds median/IQR CSV and Markdown summaries from `run.jsonl`. |
| `make_prompts.py` | Generates exact-token prompt files for prompt-length sweeps. |
| `results/` | Generated outputs. Ignored by default except for explicitly added final bundles. |

## Local Layout

The scripts assume sibling checkouts and model directories:

```text
~/dev/grout/
~/dev/hf_models/qwen3_4b/
~/dev/hf_models/qwen3_32b/
~/dev/hf_models/qwen3_4b_f16.gguf
~/dev/bench_envs/vllm_env/
~/dev/bench_envs/sglang_env/
~/dev/bench_envs/trtllm_env/
~/dev/llama.cpp/
```

Override paths with `MODEL_HF`, `GGUF_PATH`, `BENCH_ENVS_DIR`, and
`LLAMA_CPP_DIR`.

## Build Grout

```bash
cargo build --release --features benchmarks --bin grout_bench
```

## Engine Versions

These are the versions used for the May 2026 benchmark runs:

| Engine | Version |
|---|---|
| Grout | this repository, using cuTile Rust `0.2.0` |
| vLLM | `0.18.0`, `torch==2.10.0`, `flashinfer-python==0.6.6` |
| SGLang | `0.5.9`, `torch==2.9.1`, `sgl-kernel==0.3.21`, `flashinfer-python==0.6.3` |
| TRT-LLM | `1.2.0`, `tensorrt==10.14.1.48.post1`, `torch==2.9.1` |
| llama.cpp | `e6ec21e` |

Create the Python environments outside this repository, for example under
`../bench_envs/`. The wrappers do not install dependencies.

## Benchmark Policy

- Model: Qwen3, fp16 weights, no quantization.
- Batch size: 1.
- Sampling: greedy.
- Prefix cache: disabled for every comparison engine.
- Decode length: fixed with EOS ignored or `min_tokens=tg`, depending on engine.
- Metric used for cross-engine plots: `request_gen_tps = generated_tokens / e2e_ms`.
- Aggregation: median and IQR over measured reps. No outlier filtering.
- Clocks: driver-controlled by default. Passing an MHz value to a sweep locks
  clocks for debugging, but paper runs should disclose whichever policy is used.

## Canonical Runs

RTX 5090 / sm_120, Qwen3-4B:

```bash
./benchmarks/sweep_tg_sm120.sh
./benchmarks/sweep_pp_sm120.sh
```

B200 / sm_100, Qwen3-32B:

```bash
MODEL_HF=../hf_models/qwen3_32b ./benchmarks/sweep_tg_sm100.sh
MODEL_HF=../hf_models/qwen3_32b ./benchmarks/sweep_pp_sm100.sh
```

Smoke runs:

```bash
BENCH_REPS=1 BENCH_REPS_LONG=1 WARMUP_REPS=1 ./benchmarks/sweep_tg_sm120.sh
BENCH_REPS=1 BENCH_REPS_LONG=1 WARMUP_REPS=1 ./benchmarks/sweep_pp_sm120.sh
```

Run one cell:

```bash
SWEEP_TG_VALUES=8192 ./benchmarks/sweep_tg_sm120.sh
SWEEP_PP_VALUES=8192 ./benchmarks/sweep_pp_sm120.sh
```

Optional engines:

```bash
SWEEP_ENABLE_LLAMA=1 ./benchmarks/sweep_tg_sm120.sh
SWEEP_ENABLE_TRTLLM=1 ./benchmarks/sweep_tg_sm120.sh
```

TRT-LLM is only wired into the TG sweep.

## Outputs

Each sweep writes:

```text
benchmarks/results/sweep/<timestamp>/
  run.jsonl
  aggregate.csv
  aggregate.md
  summary_<timestamp>.txt
```

`run.jsonl` is the raw per-rep source of truth. `aggregate.csv` contains the
median/IQR table used for plots. See `RESULTS.md` for the committed B200
result bundle.
