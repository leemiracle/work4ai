<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Machine-readable results

`--to-json` writes one versioned JSON document for a filesystem report: what
was meant to run, what ran, and what it measured. It covers IO and metadata
(mdtest) executions. Warp and netbench have no such document.

## Producing it

```bash
./utils/extract-filesystem.py "$BATCH" --to-json                       # $BATCH/reports/results.json
./utils/extract-filesystem.py "$BATCH" --to-json --output-dir out      # out/results.json
./utils/extract-filesystem.py "$BATCH" --to-json --live-detail full --require-complete
./utils/extract-elbencho.py "$DIR" --to-json                           # $DIR/results.json
```

The document is always `<output-dir>/results.json`, beside the text reports.
`<output-dir>` defaults to `<batch>/reports` for a batch and to the input
directory otherwise.

An ordinary (non-batch) directory uses the same schema. `batch.root` is that
directory, the manifest fields are `null`, and it has one group, `"0000"`.

| Option | Meaning |
| --- | --- |
| `--to-json` | Also write the document. |
| `--live-detail LEVEL` | `none`, `summary` (default), `selected`, or `full`. IO only. See [Live detail](#live-detail). |
| `--require-complete` | Requires `--to-json`. Exit 3 after writing if `batch_outcome.complete` is false. |

Report filters (`--only-*`, `--groups`, `--kind`) apply and are recorded in
`generator.options`.

| Exit | Meaning |
| --- | --- |
| 0 | Document written. |
| 1 | A group report or fragment failed, or the document could not be written. Takes precedence over 3. |
| 2 | Usage error. |
| 3 | `--require-complete` and `batch_outcome.complete` is false. |

Gate on the document, not the exit status. Without `--require-complete`, an
incomplete batch exits 0.

The document is plain JSON. Live sidecars are always `.jsonl.zst`. Each
recorded `sha256` and `size_bytes` describes the stored bytes.

## Conventions

- **Units are in names:** `_bytes`, `_bytes_per_s`, `_ops_per_s`, `_us`
  (latency), `_ms` (measured times), `_s` (configured durations).
- **Rounding:** throughput to whole bytes/s (from elbencho MiB/s x 1048576);
  operation rates to 0.01; latencies to 0.1 us.
- **`null`** means not measured or not applicable; the enclosing `problems`
  list says why. Zero is a measured zero.
- **Enums** are lowercase `snake_case`. Tolerate unknown values and fields.
- **Paths** are relative to `batch.root`, which is absolute and
  symlink-resolved, except sidecar paths (`client_series.path`), which are
  relative to the document's directory. Paths to data outside the batch (for
  example `read_from`) are recorded as the run recorded them.
- **Histograms** are columnar: `{"buckets_us": [...], "counts": [...]}`,
  ascending.
- **Determinism:** keys in schema order; groups, executions, and phases in a
  fixed order. Two exports of the same inputs differ only in
  `generator.generated_at`.
- **Failed executions are not parsed.** Only ledger state `success`
  contributes results.

## Top level

| Field | Content |
| --- | --- |
| `schema`, `schema_version` | `storage-scale-test/filesystem-batch-results`, `"MAJOR.MINOR"` (currently `"1.0"`). |
| `generator` | `tool`, `version`, `generated_at` (UTC), `command`, `options` (`live_detail`, `shortfall_percent`, `min_slow_windows`, `only_nodes`, `only_threads`, `only_sizes`, `only_iodepths`, `groups`, `kind`; `null` when unused). |
| `batch` | `root`, `datestamp`, `manifest_version`, `manifest_sha256`, `sealed`, `substrate`. |
| `batch_outcome` | `complete`; `executions` counts (`total` plus one per `ledger_state`); `results` counts (one per `result_state`); `groups_reported`; `groups_not_reported`. |
| `groups` | One object per batch group. |
| `executions` | One object per committed execution, sorted by group, then ID. |
| `diagnostics` | Document-level `problems` entries, such as `execution_unmatched` and `no_execution_ledger`. |

`batch_outcome.complete` is true only when there is at least one execution and
every execution has ledger state `success` and result state `complete`. Check
it first. Filters never drop executions: a filtered execution is listed as
`not_reported`, so a filtered export is never complete.

## Groups

| Field | Content |
| --- | --- |
| `group_id`, `kind` | `kind` is `io` or `mdtest`. |
| `label` | Always `null` for now. |
| `output_relative` | The group's output directory. |
| `target` | `{"name", "recorded"}`: the storage target name and whether the run recorded it. |
| `settings_sha256` | `env_used_sh`, `env_used_yaml`. |
| `env_override` | Override files and the variables they set, or `null`. |
| `settings` | The group's `env_used.yaml`, as parsed. |
| `execution_ids` | The group's executions, in order. |

## Executions

Every execution carries `coordinates` and `coordinate_key`, whether or not it
has results. `dataset` and `results` are present only when parsed, and `null`
otherwise.

| Field | Content |
| --- | --- |
| `execution_id`, `group_id`, `kind`, `definition_sha256` | Identity. IDs are unique only within a batch. |
| `ledger_state` | `success`, `failed`, `pending`, `running`, `cancelled`, `interrupted`, or `unknown`. `unknown` appears only for ordinary directories without a ledger. |
| `result_state` | See below. |
| `problems` | `{"code", "detail", "phase"}` objects; `phase` may be `null`. `detail` is free text. |
| `coordinates` | Test parameters; see below. |
| `coordinate_key` | Identifies the test point across batches. Excludes the target, a group property. |
| `dataset` | IO only. |
| `result_files` | `{"path", "sha256", "size_bytes"}` for each raw result file. |
| `log` | Relative path of the execution log, or `null`. |
| `results` | IO or metadata results. |

| `result_state` | Meaning |
| --- | --- |
| `complete` | Every expected phase or iteration parsed and validated. |
| `partial` | Some were dropped or incomplete; `problems` says which. |
| `missing` | No result files. |
| `unparseable` | Result files exist, but none parse. |
| `not_reported` | Excluded by a report filter. |
| `not_run` | Ledger state is not `success`. |

| Problem code | Where | Meaning |
| --- | --- | --- |
| `phase_missing` | IO | A phase expected by `phase_plan` has no result. |
| `phase_unparseable` | IO | Result files exist but no phase parsed. |
| `percentiles_missing` | IO | Latency percentiles absent from the `.out` file. |
| `rates_missing` | IO | An `elbencho_first` rate is absent or malformed in the CSV; it is `null`. |
| `completion_incomplete` | IO | A phase did not complete all its work. |
| `live_csv_unreadable` | IO | The live CSV could not be analyzed. Does not change `result_state`. |
| `iteration_incomplete` | metadata | An iteration has partial or invalid data; listed on the iteration and, prefixed with its number, on the execution. |
| `iterations_missing` | metadata | Expected iterations have no result files. |
| `report_failed` | any | The group's report failed (`missing`). |
| `definition_unreadable` | any | The execution definition could not be parsed; `coordinates` is `null`. |
| `execution_unmatched` | `diagnostics` | Result files match no ledger execution. |
| `no_execution_ledger` | `diagnostics` | An ordinary directory has no `executions/`; ledger state is `unknown`. |

`phase_missing`, `percentiles_missing`, `rates_missing`, and
`completion_incomplete` make an IO execution `partial`.

### IO coordinates

Parsed from the execution definition.

| Field | Content |
| --- | --- |
| `nodes`, `threads_per_node`, `io_depth` | Counts. |
| `io_size_spec` | The sweep's size string, for provenance. |
| `phase_plan` | `write_read`, `write_only`, `write_no_read`, or `read_from`. |
| `write_block_size_bytes`, `write_access`, `read_block_size_bytes`, `read_access` | Parsed from `io_size_spec`. Access is `sequential` or `random`. `null` when the plan has no such phase. |
| `direct_io` | `true` for direct IO, `false` for buffered. |
| `run_to_completion`, `single_big_file`, `all_nodes_all_data` | Booleans. |
| `file_layout` | For example `worker-directories`. |

`coordinate_key` looks like `io/c004/s032/d016/w1M-seq/r4K-rand/dio`: nodes,
threads, depth, write and read size and access (`none` for an absent phase),
and `dio` or `bio`.

### IO dataset

`source` (`generated` or `read_from`), `read_from`,
`kubernetes_mapped_read_from`, `write_only_data_dir`, `layout`, `files_total`,
`bytes_total`, `treefile_source`, and `scanned_file_sizes`
(`count`, `avg_bytes`, `min_bytes`, `max_bytes`; `null` when no scan ran).

### IO results

`results.phases` has one object per phase that ran, in run order (`write`,
`read`, `delete`), and `results.workload` holds the termination and cleanup
states (`null` for layouts that record none).

| Phase field | Content |
| --- | --- |
| `phase`, `completion_state` | `completion_state` is a workload enum, or `null`. |
| `elbencho_first` | `ops_per_s`, `bytes_per_s`, `elapsed_ms`: elbencho's `[first]` column, the aggregate from phase start until the fastest worker thread finished. |
| `elbencho_last` | The same fields from the `[last]` column: until the slowest worker thread finished. |
| `latency_us` | `min`, `avg`, `max`, `p1`, `p50`, `p75`, `p99`. A missing percentile is `null`. |
| `histogram_us`, `work`, `configured_time_limit_s`, `command`, `live` | Latency histogram; expected and completed files and bytes; the configured limit; the recorded argv; the [live object](#live-object). |

The `delete` phase has only `phase`, `completion_state`, `work`, and
`elapsed_ms`.

Reports and tables use `elbencho_first`. Use `elbencho_last` for the rate the
whole fleet sustained.

### Metadata coordinates and results

Coordinates are `nodes`, `tasks_per_node`, `branch_factor`, `items_per_dir`,
and `iterations`. The key looks like `md/c002/t064/b4/i1000`.

`results.iterations` lists every iteration: `iteration`, `datestamp`, `state`
(`complete` or `incomplete`), `problems`, and `phases` (`create`, `stat`,
`delete`, each with `ops_per_s`, `elapsed_ms`, `latency_us` of
`min`/`avg`/`max`, and `histogram_us`). `results.aggregate` uses only complete
iterations: `iterations_expected`, `iterations_used`, and per phase `ops_per_s`
(`mean`, `stddev`, `min`, `max`), `mean_elapsed_ms`, `latency_us`
(`p0`, `p50`, `p90`, `p99`, `p100`), and `latency_method`
(`pooled_histogram_bucket`).

## Live detail

Live data comes from elbencho live CSVs, captured only for IO sweeps with
`ELBENCHO_LIVE_CSV_EXTENDED=1`. A domain is one execution and phase.

| `--live-detail` | Per domain |
| --- | --- |
| `none` | `live` is `{"reason": "not_requested"}`. |
| `summary` | Aggregate and fleet series, distribution statistics, every client's summary, diagnostics. |
| `selected` | `summary`, plus inline one-interval rates for the clients the report selects: persistent and transient slow clients, then representatives (bounded by `--client-max-timeseries-lines` and `--client-max-heatmap-rows`). |
| `full` | `summary`, plus every client's rates in a sidecar. |

Without an analysis, `live` is `{"reason": R}` with `R` one of `not_captured`,
`not_requested`, or `unreadable`.

### Live object

| Field | Content |
| --- | --- |
| `source` | `path`, `sha256`, `size_bytes` of the live CSV. |
| `configured_interval_ms` | `ELBENCHO_LIVEINT`, or `null`. |
| `client_mode` | `worker` or `service`; see below. |
| `domain` | `phase`, `mix_type`, `occurrence`. Further domains of a phase are counted in `diagnostics.additional_domains`. |
| `intervals`, `clients` | Counts. |
| `steady` | `start_ms`, `end_ms`, `end_source` (`elbencho_first`), and `reason` (`null`, `no_first_time`, `too_short`, or `no_steady_state`). See [live reports](FILESYSTEM_TESTING.md#live-client-and-latency-reports). |
| `aggregate_series` | Columnar: `elapsed_ms`, `bytes_per_s`, `ops_per_s`, `io_latency_avg_us` (fleet mean IO latency); `null` is a missing or invalid sample. |
| `fleet_series` | Columnar per-interval client statistics: `elapsed_ms`, `client_count`, `bytes_per_s_p10`, `_p50`, `_p90`, `_mean`, `_stddev`. |
| `fairness` | `null` without a steady window; else `interval`, `5s`, and `30s`, each `null` or `{window_ms, windows, jain {min, p10, p50}, jain_min_at_ms, share_below_0_95, min_over_median_p10, floor_p50, series {end_ms, clients, jain}}` over the windows inside the steady window. `min_over_median_p10` is the p10 of each window's slowest-client ratio; `floor_p50` is the expected Jain floor. |
| `latency` | `null` without steady latency; else `p50_us`, `p90_us`, `max_us`, `max_over_p50`, `cv`, `steady_mean_us` (op-weighted), `final_avg_us` (from `.out`), and Spearman `rho_jain_latency` and `rho_latency_throughput` over 5 s windows (`null` under 6). |
| `distribution` | Imbalance without per-client data: `client_mean_bytes_per_s` (`min`, `p10`, `p50`, `p90`, `max`, `cv`), `min_over_median`, `max_over_median`, `final_done_bytes` (`min`, `p50`, `max`, `cv`), `finish_elapsed_ms` (`min`, `p50`, `max`), `persistent_clients`, `transient_clients` (`null` when the steady window is unavailable). |
| `clients_summary` | `{"columns": [...], "rows": [[...]]}`, one row per client: `client`, `rank`, `service`, `kubernetes_node`, `kubernetes_pod`, `class`, `mean_bytes_per_s`, `median_bytes_per_s`, `mean_ratio_to_fleet_median`, `steady_bytes_per_s`, `steady_ratio`, `worst_5s_ratio`, `worst_5s_elapsed_ms`, `worst_30s_ratio`, `worst_30s_elapsed_ms`, `short_5s_share`, `final_done_bytes`, `finish_elapsed_ms`, `valid_samples`, `missing_samples`, `invalid_samples`. |
| `client_series` | `null` at `summary`; at `selected`, inline `clients`, `elapsed_ms`, and `bytes_per_s` (one list per client); at `full`, a sidecar reference `{"path", "sha256", "size_bytes", "clients", "intervals"}`. |
| `diagnostics` | `missing_samples`, `counter_resets`, `non_adjacent_samples`, and possibly `additional_domains`. |

### Slow-client classes

`class` is `persistent`, `transient`, or `ok`, by the rules in
[live reports](FILESYSTEM_TESTING.md#live-client-and-latency-reports); it and
the steady and worst-window columns are `null` without steady data.
`short_5s_share` is the share of steady 5 s windows below 1 - S.

`final_done_bytes` is a client's last cumulative `DoneBytes` (its work share
in time-bounded runs). `finish_elapsed_ms` is the first interval at which it
reached that value (the straggler signal in completion-bound runs).

### Client mode

A client row is a local worker thread (`worker`) or a remote elbencho service
(`service`). Executions on one node run threads; executions on more than one
node run services, on every substrate (SSH hosts, Slurm nodes, Kubernetes
worker Pods). On Kubernetes, `kubernetes_node` and `kubernetes_pod` come from
the collected `executions/<id>.workers.tsv`; elsewhere they are `null`.
"Clients" means threads in single-node runs.

### Sidecars

At `full`, each domain writes `results.live/<execution_id>.<phase>.jsonl.zst`
beside the document, referenced by `client_series.path`.
Earlier sidecars in that directory are removed before a batch export. Each is
zstd-compressed JSON Lines in source order:

```json
{"schema": "storage-scale-test/live-client-series", "schema_version": "1.0", "execution_id": "0014", "phase": "write", "clients": ["host001 [rank 0]", "..."]}
{"elapsed_ms": 1000, "bytes_per_s": [null, 1320000000, 1290000000]}
```

`bytes_per_s[i]` belongs to `clients[i]`; `null` is a missing or invalid
sample.

### Size

Estimates, before compression. A raw `.live.csv` is about 200 bytes per row.

| Scenario | Raw live CSV | `summary` (in `results.json`) | `full` sidecars |
| --- | --- | --- | --- |
| 256 clients, 2 x 300 s at 1 s | 31 MB | 270 KB | 1.7 MB |
| 1024 clients, 2 x 300 s at 1 s | 123 MB | 810 KB | 6.8 MB |
| 1024 clients, 2 x 3600 s at 1 s | 1.5 GB | 1.8 MB | 81 MB |

Figures are per execution. Over 200 executions of 1024 clients and an hour per
phase, `summary` totals about 360 MB and sidecars about 16 GB. Without live
data, an execution costs about 5-10 KB (IO) or 10-20 KB (metadata).

## Spot-checking with jq

These read the whole document but print only small tables; a 6 MB, 114-execution
batch answers each in about 0.1 s. Run them where the document is:

```bash
R=reports/results.json
cols() { column -t -s $'\t'; }
```

Overview: options, batch, and outcome counts.

```bash
jq '{schema_version, generated_at: .generator.generated_at, options: .generator.options,
     batch: (.batch | {datestamp, substrate, sealed}), outcome: .batch_outcome}' "$R"
```

Collection issues: every execution that is not `complete` or has problems,
then each problem's detail, then document-level diagnostics. No output means
none.

```bash
jq -r '.executions[] | select(.result_state != "complete" or (.problems | length) > 0)
  | [.group_id, .execution_id, .ledger_state, .result_state,
     (.problems | map(.code) | unique | join(",") | if . == "" then "-" else . end)]
  | @tsv' "$R" | cols
jq -r '.executions[] | .execution_id as $id | .problems[]
  | [$id, .code, (.phase // "-"), .detail] | @tsv' "$R"
jq -r '.diagnostics[] | [.code, .detail] | @tsv' "$R"
```

Groups, with target, size, result states, and whether an env override applied:

```bash
jq -r '.executions as $e | .groups[] | .group_id as $g
  | ($e | map(select(.group_id == $g))) as $mine
  | [$g, .kind, (.target.name // "-"), ($mine | length),
     ($mine | map(.result_state) | group_by(.) | map("\(.[0])=\(length)") | join(" ")),
     (if .env_override then "override" else "-" end)] | @tsv' "$R" | cols
```

Settings that differ between groups (what each group varied):

```bash
jq -r '[.groups[].settings | to_entries[]] | group_by(.key)
  | map(select((map(.value | tojson) | unique | length) > 1))[]
  | "\(.[0].key): \(map(.value | tojson) | unique | join(" | "))"' "$R"
```

All executions; add `select(.group_id == "0003")` after `.executions[] |`
for one group:

```bash
jq -r '.executions[] | [.group_id, .execution_id, .kind, .coordinate_key,
  .ledger_state, .result_state] | @tsv' "$R" | cols
```

One execution without the bulky histogram and live series:

```bash
jq --arg id 0001 '.executions[] | select(.execution_id == $id)
  | del(.results.phases[]?.histogram_us, .results.phases[]?.live.aggregate_series,
        .results.phases[]?.live.fleet_series, .results.phases[]?.live.clients_summary,
        .results.phases[]?.live.client_series)' "$R"
```

Logs of executions that need a look:

```bash
jq -r '.batch.root as $root | .executions[]
  | select(.ledger_state != "success" or .result_state != "complete")
  | "\(.execution_id) \(.ledger_state)/\(.result_state) \(if .log then "\($root)/\(.log)" else "(no log)" end)"' "$R"
```

IO results, one row per phase (GB/s is 10^9 bytes/s):

```bash
jq -r '(["id","coordinate_key","phase","first_GB/s","last_GB/s","first_IOPS","p99_us"]),
  (.executions[] | select(.kind == "io" and .results != null) | . as $e
   | .results.phases[] | select(.phase != "delete")
   | [$e.execution_id, $e.coordinate_key, .phase,
      (.elbencho_first.bytes_per_s | if . then . / 1e9 * 100 | round / 100 else null end),
      (.elbencho_last.bytes_per_s | if . then . / 1e9 * 100 | round / 100 else null end),
      .elbencho_first.ops_per_s, .latency_us.p99]) | @tsv' "$R" | cols
```

The same test point across storage targets, `elbencho_first` GB/s:

```bash
jq -r '(.groups | map({(.group_id): (.target.name // "?")}) | add) as $target
  | [.executions[] | select(.kind == "io" and .results != null) | . as $e
     | .results.phases[] | select(.phase != "delete")
     | {key: $e.coordinate_key, phase, target: $target[$e.group_id],
        gbps: (.elbencho_first.bytes_per_s | if . then . / 1e9 * 100 | round / 100 else null end)}]
  | (map(.target) | unique) as $targets
  | (["coordinate_key", "phase"] + $targets),
    (group_by([.key, .phase])[] | . as $rows
     | [.[0].key, .[0].phase] + [$targets[] as $t | $rows | map(select(.target == $t)) | first | .gbps])
  | @tsv' "$R" | cols
```

Metadata aggregates over the complete iterations:

```bash
jq -r '(["id","coordinate_key","iters","phase","mean_ops/s","stddev","p99_us"]),
  (.executions[] | select(.kind == "mdtest" and .results != null) | . as $e
   | .results.aggregate as $a | $a.phases[]
   | [$e.execution_id, $e.coordinate_key, "\($a.iterations_used)/\($a.iterations_expected)",
      .phase, .ops_per_s.mean, .ops_per_s.stddev, .latency_us.p99]) | @tsv' "$R" | cols
```

Live coverage, then client balance per analyzed phase:

```bash
jq -r '.executions[] | (.results.phases // [])[] | select(.phase != "delete")
  | .live.reason // "analyzed"' "$R" | sort | uniq -c
jq -r '(["id","phase","mode","clients","min/median","cv","persistent","transient","jain5s_p50","jain5s_min"]),
  (.executions[] | .execution_id as $id | (.results.phases // [])[]
   | select(.live.distribution?)
   | [$id, .phase, .live.client_mode, .live.clients, .live.distribution.min_over_median,
      .live.distribution.client_mean_bytes_per_s.cv,
      .live.distribution.persistent_clients, .live.distribution.transient_clients,
      .live.fairness["5s"].jain.p50, .live.fairness["5s"].jain.min])
  | @tsv' "$R" | cols
```

The five slowest clients of one phase:

```bash
jq -r --arg id 0001 --arg phase write '.executions[] | select(.execution_id == $id)
  | .results.phases[] | select(.phase == $phase) | .live.clients_summary
  | .columns as $c | .rows | map([$c, .] | transpose | map({(.[0]): .[1]}) | add)
  | map(select(.steady_ratio != null)) | sort_by(.steady_ratio) | .[:5][]
  | [.client, (.kubernetes_node // "-"), (.class // "-"), .steady_ratio,
     .worst_5s_ratio, .finish_elapsed_ms] | @tsv' "$R" | cols
```

A `full` sidecar: its header, then the slowest client per interval.

```bash
zstd -dc "$(dirname "$R")/results.live/0001.write.jsonl.zst" | jq -c 'if .schema
  then {execution_id, phase, clients: (.clients | length)}
  else {elapsed_ms, slowest_bytes_per_s: (.bytes_per_s | map(select(. != null)) | min)} end'
```

Where the document's bytes go, largest executions first:

```bash
jq -r '.executions[] | [.execution_id, (tojson | length)] | @tsv' "$R" | sort -k2 -nr | head
```

## Schemas and versioning

- `docs/schemas/filesystem-batch-results-1.schema.json`: the document.
- `docs/schemas/live-client-series-1.schema.json`: each sidecar line.

Both are JSON Schema 2020-12. `schema_version` is `MAJOR.MINOR`. A minor
version only adds optional fields or enum values; a major version renames,
removes, or changes the meaning or unit of a field, and its schema file name
changes. Check the major version; ignore unknown fields.

## Example

```python
import json
import sys

TARGET = {"io/c004/s032/d016/w1M-seq/r4K-rand/dio": 3.0e9}  # bytes/s

with open("results.json", encoding="utf-8") as stream:
    doc = json.load(stream)
if not doc["schema_version"].startswith("1."):
    sys.exit("unsupported schema")
if not doc["batch_outcome"]["complete"]:
    sys.exit("batch incomplete")

failed = []
for execution in doc["executions"]:
    target = TARGET.get(execution["coordinate_key"])
    phases = (execution["results"] or {}).get("phases", [])
    write = next((p for p in phases if p["phase"] == "write"), None)
    if target is not None and write:
        if write["elbencho_first"]["bytes_per_s"] < target:
            failed.append(execution["execution_id"])
sys.exit(f"below target: {failed}" if failed else 0)
```
