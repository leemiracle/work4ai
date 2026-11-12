# Benchmark Results

Committed B200 Qwen3-32B result bundle:

```text
benchmarks/results/final/b200_qwen3_32b/
```

`benchmarks/results/` is ignored by default; this final bundle is the
paper handoff data. Timestamped sweep directories remain local scratch unless
they are explicitly added.

## Bundles

| Bundle | Sweep |
|---|---|
| `tg_sweep_pp18/` | `pp=18`, `tg={36,128,512}` |
| `tg_sweep_pp18_8k/` | `pp=18`, `tg={36,128,512,2048,8192}` |
| `pp_sweep_tg36/` | `pp={18,128,512,2048}`, `tg=36` |
| `pp_sweep_tg36_8k/` | `pp={18,128,512,2048,8192}`, `tg=36` |

Each bundle contains `run.jsonl`, `aggregate.csv`, `aggregate.md`, and
`summary.txt`.

## Headline Numbers

Short TG sweep, `pp=18`:

| engine | tg=36 | tg=128 | tg=512 |
|---|---:|---:|---:|
| grout | 79.6 | 79.9 | 80.1 |
| sglang | 74.4 | 76.7 | 77.4 |
| vllm | 78.8 | 79.1 | 79.2 |

Long TG extension, `pp=18`, `tg=8192`:

| engine | request_gen_tps |
|---|---:|
| grout | 80.1 |
| sglang | 76.5 |
| vllm | 77.5 |

Short PP sweep, `tg=36`:

| engine | pp=18 | pp=128 | pp=512 | pp=2048 |
|---|---:|---:|---:|---:|
| grout | 79.8 | 79.0 | 75.3 | 61.4 |
| sglang | 73.9 | 73.9 | 72.2 | 59.9 |
| vllm | 77.9 | 77.7 | 73.8 | 60.7 |

Long PP extension, `tg=36`, `pp=8192`:

| engine | request_gen_tps | prefill_ms |
|---|---:|---:|
| grout | 37.2 | 513.78 |
| sglang | 36.7 | 507.12 |
| vllm | 37.3 | 491.55 |

Values are `request_gen_tps`. Use the bundle `aggregate.csv` files for the
full per-engine tables and roofline columns.
