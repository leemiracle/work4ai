# Paper Sweep — Median + IQR

n reps = 5 per cell; per-cell tables report medians unless labeled otherwise. The benchmark stdout summaries are means, so they are not expected to match these medians exactly. `decode_fit_*` columns come from a linear fit of e2e_median_ms vs tg for each (engine, variant, pp).

## Request Generation Throughput

| engine | variant | pp | tg | n | e2e_ms (median ± IQR/2) | request_gen_tps (median) | total_tps over e2e (median) |
|---|---|---:|---:|---:|---:|---:|---:|
| transformers | compiled-max-autotune | 18 | 0 | 5 | 6.46 ± 0.01 | 0.0 | 2786.4 |
| transformers | compiled-max-autotune | 128 | 0 | 5 | 7.57 ± 0.01 | 0.0 | 16909.2 |
| transformers | compiled-max-autotune | 512 | 0 | 5 | 24.53 ± 0.11 | 0.0 | 20872.1 |
| transformers | compiled-max-autotune | 2048 | 0 | 5 | 116.45 ± 0.41 | 0.0 | 17587.7 |
| transformers | compiled-max-autotune | 8192 | 0 | 5 | 842.74 ± 0.32 | 0.0 | 9720.6 |
| transformers | eager-sdpa | 18 | 0 | 5 | 9.37 ± 0.17 | 0.0 | 1920.8 |
| transformers | eager-sdpa | 128 | 0 | 5 | 10.76 ± 0.15 | 0.0 | 11891.1 |
| transformers | eager-sdpa | 512 | 0 | 5 | 27.32 ± 0.30 | 0.0 | 18740.8 |
| transformers | eager-sdpa | 2048 | 0 | 5 | 101.69 ± 0.07 | 0.0 | 20139.3 |
| transformers | eager-sdpa | 8192 | 0 | 5 | 497.80 ± 0.37 | 0.0 | 16456.6 |

## Derived Decode From Cross-TG Fit

| engine | variant | pp | n_tg_points | prefill_ms (fit intercept) | decode_ms_per_tok (fit) | decode_fit_tps |
|---|---|---:|---:|---:|---:|---:|
| transformers | compiled-max-autotune | 18 | 1 | n/a | n/a | n/a |
| transformers | compiled-max-autotune | 128 | 1 | n/a | n/a | n/a |
| transformers | compiled-max-autotune | 512 | 1 | n/a | n/a | n/a |
| transformers | compiled-max-autotune | 2048 | 1 | n/a | n/a | n/a |
| transformers | compiled-max-autotune | 8192 | 1 | n/a | n/a | n/a |
| transformers | eager-sdpa | 18 | 1 | n/a | n/a | n/a |
| transformers | eager-sdpa | 128 | 1 | n/a | n/a | n/a |
| transformers | eager-sdpa | 512 | 1 | n/a | n/a | n/a |
| transformers | eager-sdpa | 2048 | 1 | n/a | n/a | n/a |
| transformers | eager-sdpa | 8192 | 1 | n/a | n/a | n/a |

## Direct Phase Timings

Cells with `—` indicate the engine did not emit that same-request phase timer in run.jsonl. prefill_tps is prompt_tokens / prefill_ms; decode_direct_tps is generated_tokens / decode_ms. Note prefill_ms is pure prefill for grout/transformers but TTFT (prefill + 1 decode step) for vllm/sglang.

| engine | variant | pp | tg | prefill_ms (direct/TTFT) | prefill_tps | decode_ms (direct) | decode_direct_tps |
|---|---|---:|---:|---:|---:|---:|---:|
| transformers | compiled-max-autotune | 18 | 0 | 6.46 | 2786.4 | — | — |
| transformers | compiled-max-autotune | 128 | 0 | 7.57 | 16909.2 | — | — |
| transformers | compiled-max-autotune | 512 | 0 | 24.53 | 20872.1 | — | — |
| transformers | compiled-max-autotune | 2048 | 0 | 116.45 | 17587.7 | — | — |
| transformers | compiled-max-autotune | 8192 | 0 | 842.74 | 9720.6 | — | — |
| transformers | eager-sdpa | 18 | 0 | 9.37 | 1920.8 | — | — |
| transformers | eager-sdpa | 128 | 0 | 10.76 | 11891.1 | — | — |
| transformers | eager-sdpa | 512 | 0 | 27.32 | 18740.8 | — | — |
| transformers | eager-sdpa | 2048 | 0 | 101.69 | 20139.3 | — | — |
| transformers | eager-sdpa | 8192 | 0 | 497.80 | 16456.6 | — | — |
