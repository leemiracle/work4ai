# Plan: CI failures still silently dropped from the by-PR dashboard

**Date:** 2026-07-15
**Status:** OPEN — reopen of [`plan-large-trace-read-limit-2026-07-03.md`](./plan-large-trace-read-limit-2026-07-03.md).
That plan is marked "mitigation shipped; source-side reduction implemented
(span_pruning, PR #12)", but a run from **11 days later** still loses a real
failure. Two fixes are required (below); the second is a gap the earlier plan
never covered.

## TL;DR

A genuinely-failing run rendered **green** on the by-PR dashboard. The trace was
in the backend, correctly tagged, and the runner lost **0%** of its spans — but
the trace-exporter read back only **37%** of `tests_torch`'s tests from the big
shard traces, and the one `ERROR` span happened to be among the 63% it dropped.

The dashboard's *only* failure signal is the aggregate gauge
`pytest_run_job_failed_tests = sum(status_code == "ERROR")`
(`trace_exporter.py:2568`). There is no per-test, PR-labelled outcome series to
fall back on, so **one lost `ERROR` span silently turns a red run green** — the
dashboard disagreeing with GitHub.

## Fresh evidence — run `29334708040`, PR #46766 (2026-07-14)

GitHub: `tests_torch [shard 4/8]` failed with a real assertion
(`MoonshineModelTest::test_training_loss_no_double_shift — AssertionError`),
`1 failed, 7882 passed`. Job log shows all traces exported `result=SUCCESS` and
`OTEL TRACE END ... job=tests_torch exit_code=1`. The by-PR dashboard shows the
job green.

`tests/compare_pr_to_github.py 46766 --run-id 29334708040`:

```
test_job          shards GH/exp  GH coll  exporter  %coll   flags
tests_torch          3/1         44574    16713     37%     !shard mismatch !undercount
tests_peft_integ.    1/1           45        45    100%
examples_torch       1/1           35        35    100%

# Runner span pipeline (what CI actually shipped, prod only):
test_job       GH collect  produced  exported  failed  lost%
tests_torch        44574    123020    123020       0      0%
```

Reading the two tables together localizes the loss precisely:

- **CI/runner is not at fault.** 123,020 spans produced, 123,020 confirmed
  shipped, 0 failed, 0% lost. Every span — including the `ERROR` span — reached
  the backend. Not an emission, transport, or PR-attribution problem.
- **The trace-exporter under-reads on the way back.** Only 16,713 / 44,574
  collected `tests_torch` tests (37%) were turned into rows; small jobs
  (`peft`, `examples`) came back at 100%. The loss is **size-correlated** — the
  documented fingerprint of large-trace read truncation.
- **Therefore the failure vanished.** The moonshine `ERROR` span was in the
  ~63% never read back → `pytest_run_job_failed_tests` for `tests_torch` = 0 →
  job renders green.

### The 2026-07-03 source-side fix is not effective here

The exporter in prod is `0.1.0+gfa98dc7` (top of `main`). span_pruning (PR #12)
was supposed to make traces ~one span per test (~83% smaller). But this run
produced **123,020 spans for 44,574 collected tests ≈ 2.76 spans/test** — far
from the ~1/test the plan targets (pre-pruning was ~5.9/test). So in this run
pruning was either **not active in the CI image, partially applied, or a
band-aid was reverted before traces were confirmed small**. The read is still
truncating, which is only possible if the traces are still large.

## Why this is worse than a count gap

`compare_pr_to_github.py` was built to catch *undercounts* (totals). This is the
same defect, but its consequence here is a **correctness inversion**: the
dashboard reports PASS for a run GitHub reports FAIL. That is the one thing an
observability dashboard must never do — it silently hides regressions from
reviewers who trust the green badge.

## The two fixes

### 1. Make the source-side reduction actually hold in prod (finish PR #12)

Verify span_pruning is deployed and effective in the **CI runner image** (the
`transformers-ci` pytest plugin, not the exporter):

- Confirm the installed plugin build contains the `pytest_runtest_setup/call/
  teardown` + `pytest_fixture_setup` suppression described in the 2026-07-03
  plan.
- On a fresh large run, check `produced / collected ≈ 1` (this run is 2.76) and
  that a `tests_torch` shard trace is single-digit MB with
  `GET /api/traces/<id>` returning 200.
- Only then revert the read-path band-aids (Tempo gRPC bump, httpTimeout 45→10,
  mem 4→2Gi, refetch 900→300).

Until `produced/collected ≈ 1`, the read path keeps truncating and failures keep
disappearing.

### 2. Make failure detection loss-resilient (new — not in the earlier plan)

Even with small traces, deriving job pass/fail *solely* by summing per-test
`ERROR` spans is fragile: any single lost span flips red→green. Add a floor that
cannot be silently lost:

- **Derive a run/job-level `failed` floor from the session/run span, not only
  from per-test spans.** The pytest run span already carries the overall outcome
  (the debug wrapper logs `OTEL TRACE END ... exit_code=1`). If the exporter
  reads the session span's status/exit code and sets
  `pytest_run_job_failed >= 1` whenever it is non-zero — regardless of how many
  per-test `ERROR` spans it managed to read — a truncated trace can *undercount*
  failures but can never report **zero** for a job that actually failed. Cheap,
  and it directly closes the red→green inversion.
- **Optionally** emit a per-run `pytest_run_dashboard_mismatch` signal by
  wiring the `compare_pr_to_github` reconciliation into the exporter (or a
  periodic job), alerting when exporter totals diverge from GitHub so silent
  drift is caught proactively rather than by eye.

Fix #1 restores completeness; fix #2 guarantees a failed run can never look
green even if completeness regresses again (it already has, twice).

## Verification

- `compare_pr_to_github.py 46766 --run-id 29334708040` → `tests_torch` back to
  `%coll ≈ 100`, no `!undercount` / `!shard mismatch`.
- The moonshine failure shows as a red `tests_torch` cell on the by-PR
  dashboard for PR #46766.
- `pytest_trace_exporter_trace_fetch_errors_total{reason="too_large"}` flat.
- Regression guard: with fix #2, a synthetic run whose per-test `ERROR` spans are
  all dropped but whose session span exit_code=1 still reports the job as failed.
