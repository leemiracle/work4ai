# ReviewOps Auditor + Benchmark tests

The ReviewOps suite is synthetic, offline, and deterministic. The revised
v0.1.0 contract covers four explicit skills and five CLI commands:
`validate-config`, `normalize`, `audit-eval`, `benchmark`, and
`recommend-architecture`.

Run from the repository root:

```sh
npm run test:reviewops-auditor-benchmark
```

Tests are grouped by execution boundary:

- `unit/` imports reviewed source directly and is the coverage-gated suite;
- `integration/` exercises the public CLI, Markdown, and copied package;
- `security/` keeps adversarial input, redaction, and isolation checks easy to
  audit separately.

CI exposes one ReviewOps E2E check. Node 22.19, 24, and 26 compatibility runs
stay inside that check instead of multiplying GitHub status checks.

The fixture intentionally contains no customer data, provider credentials,
private URLs, real prompts, real diffs, or live integration.

## Required qualification coverage

Before release, the suite must demonstrate:

- strict schema and path validation for lane bundles, source-neutral exports,
  canonical records, protocols, labels, pricing, policies, and outputs;
- bounded normalization with accepted, rejected, duplicate, and reason-code
  reporting;
- fair-evaluation gates for pairing, held constants, allowed differences,
  blinding, leakage controls, adjudication, attribution, and exclusions;
- validity-gated global and per-slice root-cause, quality, cost, latency,
  confidence, stability, and frontier results;
- shadow-only reference-architecture gates, preserved contracts, human
  approval, rollback triggers, and no-posting language;
- secondary static diagnostics that cannot become causal proof without an
  observed, policy-bound shadow-path finding;
- hostile prompt and export data, redaction, path containment, regular-file
  checks, resource limits, stable errors, and text-accessible Markdown;
- copied-package execution without runtime `node_modules`, network,
  credentials, Git metadata, home-directory reads, or provider calls.

## Qualification record

Local revised-contract qualification on 2026-08-24:

- <code>npm run test:reviewops-auditor-benchmark</code>: 106 passed, 0 failed;
- unit coverage: 78 passed, 0 failed; at least 92.45% lines, 82.80%
  branches, and 95.10% functions;
- <code>npm run verify:reviewops-source</code>, <code>npm run validate</code>,
  and <code>npm run test:marketplace</code>: passed;
- <code>npm audit --prefix plugins/reviewops-auditor-benchmark --omit=dev</code>:
  0 vulnerabilities;
- both shipped entrypoints passed <code>node --check</code>;
- copied-package and isolated installed-fixture paths ran all five commands
  without credentials, network, provider calls, or writeback.

CI results remain unclaimed until CI actually completes.
