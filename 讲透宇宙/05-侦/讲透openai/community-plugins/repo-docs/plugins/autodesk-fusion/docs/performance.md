# Local performance and stability evidence

`scripts/benchmark-local.mjs` measures the local portions of implementation-plan §18.5. It creates only synthetic providers and a new task-private state tree. It never loads `FUSION_PROFILE`, initializes native/add-in/cloud clients, accesses credentials, or contacts Autodesk. Importing the script is inert.

This is a workstation benchmark, not live Fusion qualification. No result qualifies CAD recompute, engineering correctness, network transfer, cloud queues, real transport reconnects, Autodesk event handlers, or manufacturing safety.

## Run a short local benchmark

From the plugin directory, first build the reviewed source. Supply a new absolute output directory whose parent already exists:

```sh
npm run build
node scripts/benchmark-local.mjs --output-root /absolute/task-cache/fusion-benchmark-001
```

The destination must not exist; existing directories and links are refused without repair or overwrite. The script creates private state beneath it, removes that state after observing locks and temporary records, and retains `benchmark.json`. On POSIX, the directory is mode 0700 and the report is mode 0600. The product's private-directory checks also apply. No user's runtime, profile, policy, or default configuration is edited.

The default uses 30 measured I/O samples, 300 schema/policy samples, 10 fixture reopen cycles, a fixed 100-operation batch, and 256 extra synthetic parameters. It starts no soak. Use `--help` for the bounded sample/reopen/fixture controls. Runtime depends on filesystem durability costs; no live operation is given an arbitrary deadline.

## What each lane measures

| Lane | Included work | Proposed local gate |
| --- | --- | --- |
| Schema | Synchronous `parseOperation` on a declared parameter update | Reported separately |
| Policy | Synchronous `authorize` on an already parsed in-memory fixture profile | Reported separately |
| Schema + policy | Both synchronous paths; no promises, filesystem or provider calls | Empirical p95 < 100 ms |
| Raw ledger read | `RecordStore.get`, file safety checks and JSON parsing | Reported separately |
| Terminal job status | Actual `engine.jobStatus`, code/profile checks, lease and plan/job bindings | Empirical p95 < 500 ms; zero provider dispatches |
| Initial fixture connection | New engine/store initialization, connection and capability reports | Observed maximum < 5 s |
| Fixture connection report | Warm engine report, local filesystem and fixture dispatch | Observed maximum < 5 s |
| Static capabilities | Synchronous capability report; no entitlement probe | Reported separately |
| Small inspection | Engine read, schema/policy, code checks, local store and three-parameter fixture | Empirical p95 < 3 s |
| Reopens | Fresh fixture engines, persistent readback, reports and close calls | Each observed cycle < 5 s |
| 100-operation batch | Prepare, execute and state/numeric readback for every sequential parameter update; reopen final result | All 100 succeed, 101 distinct states, final width 140 mm |
| Large synthetic collection | Bounded parameter prefix and complete, nonduplicated entity pagination | Exact counts, advancing offsets, page limit and completion metadata |

Module loading and initial receipt verification are reported separately. Normal I/O lanes discard three warmups; schema/policy lanes discard 20. Initial connection, reopens, batch operations and pagination report every observed sample without warmup. Per-call correctness checks are outside the latency samples except batch readback, which is explicitly part of its workload. Provider dispatch counters add a small disclosed instrumentation cost to engine lanes.

The terminal-job lane uses a local protocol double to produce a bound terminal broker receipt through real `prepare`/`execute` calls. It does not claim the stock fixture implements CAM. The measured terminal `jobStatus` requests omit expected-state and artifact refresh, and the harness checks that no provider call occurs during measurement.

The fixture-only profile uses the supported 600-plans/minute admission budget for the fixed 100-plan workload. These are 100 individually state-bound plans, not one atomic transaction. No real profile's rate limit is changed.

Large-fixture state contains one analytic body and a generated parameter collection, not a representative large CAD model. `parameters.list` has a bounded prefix contract (`parameters`, `total`, `truncated`), not cursor pagination. `entities.find` traverses canonical `entities`, `total`, `offset`, and `next_offset` responses. The script stops at a declared maximum page count and rejects duplicates, wrong totals, oversized pages and nonadvancing offsets. A build without canonical pagination is reported incomplete. Oversized limits, offsets and parameter-change arrays are also checked against the actual schema without provider dispatch.

## Optional bounded soak

Only start a soak deliberately. For example, this explicitly requests a two-hour **synthetic** session:

```sh
node scripts/benchmark-local.mjs --output-root /absolute/task-cache/fusion-soak-001 --soak-seconds 7200 --progress-seconds 5
```

The permitted duration is 0–14,400 seconds. A one-second pacing interval yields the event loop; inspections and capability reports run each cycle, with a fixture reopen every tenth cycle. A separate timer emits compact JSON progress. There is no blocking sleep, automatic long soak, network call or indefinite retry. SIGINT/SIGTERM request bounded local cleanup and preserve partial evidence; normal cleanup cannot be guaranteed after SIGKILL, power loss or filesystem failure.

RSS, used/total heap, external/array-buffer memory, active-resource types, process listener counts and open fixture-engine counts are sampled at phase boundaries and progress intervals. At most 512 observations are retained; dropped observations are counted, and sampled memory high-water marks are retained. Transient filesystem/immediate resources are excluded from the final resource-delta check; unexpected positive deltas make local stability incomplete for review. Remaining listeners, open engines, stale execution locks, temporary records, or failed cleanup are failures.

Provisional sampled growth guards are 128 MiB RSS and 64 MiB used heap after schema warmup. These are transparent local engineering guards, not calibrated capacity limits or proof that memory cannot grow. No forced garbage collection is used. The fixture owns no Autodesk socket or event handlers, so real handler-lifecycle evidence remains unavailable even after a long fixture soak.

## Read the report

The JSON record includes the platform, OS, CPU model/count, memory, Node/V8/libuv versions, declared fixture complexity, fixture/source/build/compiled-contract/harness hashes, sample counts and raw bounded latency samples, percentile definition, thresholds, checks, incomplete lanes, resource observations and cleanup results. Absolute task/profile paths and raw operation payloads are not embedded in the report.

Percentiles use empirical nearest rank: `sorted[ceil(p * n) - 1]`, without interpolation. The threshold comparison uses unrounded observations. Small dependent samples on one workstation do not establish a population p95, uncertainty bounds, an SLA, or statistical evidence of zero leaks. Compare runs only after reviewing source/contract hashes, runtime, workstation, fixture sizes, cache conditions, duration and sample sizes. Establish representative baselines with the responsible engineering owners before changing budgets or making performance commitments.

`local_status` is `passed`, `failed`, or `incomplete`. Every real Fusion/large-CAD/transport lane remains explicitly incomplete, so overall `status` cannot become full performance qualification from this script. Exit 0 means the measured local gates passed, exit 1 means a measured local failure, and exit 2 means incomplete local evidence or invalid setup. Source files that no longer match the captured compiled receipt make local evidence incomplete until rebuilt. A cleanup failure remains visible even if a workload otherwise passed.

The focused integration test verifies actual fixture/ledger execution, readback, pagination, inert imports, private output refusal and cleanup. It does not assert workstation timing or memory budgets as universal CI performance requirements.
