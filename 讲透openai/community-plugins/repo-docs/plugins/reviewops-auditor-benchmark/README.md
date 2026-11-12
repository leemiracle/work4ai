# ReviewOps Auditor + Benchmark

ReviewOps is an offline evidence layer for an existing code-review system. It
normalizes declared sanitized exports, checks whether a comparison is fair,
benchmarks only eligible runs, and recommends a reversible shadow reference
architecture. It does not run reviews, call providers, post comments, or
change a repository.

Version 0.1.0 is intentionally read-only, stdout-only, and vendor-neutral.

## Four explicit skills

| Skill                                     | Result                                                                                                                       |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `normalize-review-runs`                   | Validates source-neutral exports and reports canonical record counts, rejects, duplicates, provenance, and receipts.         |
| `audit-review-eval-validity`              | Checks pairing, controls, blinding, adjudication, leakage, attribution, and claim boundaries.                                |
| `benchmark-review-configs`                | Scores only validity-eligible lanes with root-cause, risk-slice, quality, cost, latency, stability, and uncertainty metrics. |
| `recommend-review-reference-architecture` | Emits a claim-bounded, shadow/no-posting reference architecture with human approval and rollback gates.                      |

Every skill requires explicit invocation. Static workflow and prompt inspection
is optional secondary diagnostic context; it is not causal evidence and is
not required for a benchmark-only recommendation.

## Safe first run

Start a new Codex task after installation and use the bundled synthetic
fixture:

```text
Use $normalize-review-runs on the bundled synthetic fixture only. Explain the
normalization summary, provenance checks, safety boundaries, and next safe
step.
```

The fixture is fixed, synthetic, and non-production. It does not scan the
current repository, request credentials, make a network request, write a
file, execute a workflow, or replay a review.

## Install

Requires Node.js 22.19 or newer. From a reviewed local checkout:

```sh
codex plugin marketplace add .
codex plugin add reviewops-auditor-benchmark@community-plugins
```

Run the first command from the repository root, then start a new Codex task.
The GitHub-backed marketplace can be added with
`codex plugin marketplace add tonyloehr/community-plugins --ref main`.

## Permissions and authentication

The manifest declares only `Read`. The plugin has no MCP server, app, OAuth
flow, provider key, GitHub token, live pricing fetch, install hook, network
call, writeback path, or persistent state. The marketplace uses the
platform's `ON_USE` policy because the catalog has no auth-less value; the
plugin itself never authenticates and must not ask for a secret.

If installation or first use prompts for authentication, stop and report it
as a packaging defect. Do not supply a credential.

## Data boundary

The plugin reads only regular local files named in a strict JSON config:

- source-neutral exports, canonical records, labels, protocols, manifests,
  candidate configs, rubrics, policies, and pricing snapshots: `.json` or
  `.jsonl`;
- optional workflow diagnostics: `.yml` or `.yaml`;
- optional prompt diagnostics: `.md` or `.txt`.

The trusted root is the current project directory at invocation time. Config
paths must be relative descendants of declared `inputRoots`. Absolute paths,
`..`, symlinks, hardlinks, special files, undeclared directories, globs, URLs,
tokens, headers, executable paths, and command text are rejected. The config
cannot broaden the trusted root.

Keep private exports in an ignored local directory. Do not paste prompts,
diffs, logs, comment bodies, tokens, URLs, customer records, or private prices
into chat. Real case, run, finding, and root-cause IDs must be
`sha256:`-shaped opaque digests; public aliases are limited to stable
lower-case labels.

## Real-input contract

Create a strict JSON config in the project root or an ignored descendant. Its
shape is defined by
[`schemas/config.schema.json`](schemas/config.schema.json). A minimal lane
bundle looks like this:

```json
{
  "schemaVersion": 1,
  "analysisAsOf": "2026-08-01T00:00:00Z",
  "repoRoot": ".",
  "inputRoots": ["private-reviewops"],
  "decisionPolicyPath": "private-reviewops/decision-policy.json",
  "laneBundles": [
    {
      "bundleId": "model-only-lane",
      "manifestPath": "private-reviewops/benchmark-manifest.json",
      "evalProtocolPath": "private-reviewops/eval-protocol.json",
      "adjudicationProtocolPath": "private-reviewops/adjudication-protocol.json",
      "candidateConfigPaths": [
        "private-reviewops/candidate-baseline.json",
        "private-reviewops/candidate-a.json"
      ],
      "rubricPath": "private-reviewops/rubric.json",
      "pricingSnapshotPath": "private-reviewops/pricing.json",
      "caseLabelPaths": ["private-reviewops/case-labels.jsonl"],
      "exportPaths": ["private-reviewops/review-runs.jsonl"]
    }
  ],
  "limits": {
    "maxFiles": 50,
    "maxBytesPerFile": 1048576,
    "maxTotalBytes": 16777216,
    "maxRecords": 5000
  }
}
```

Each lane bundle must declare exactly one of `exportPaths` or
`canonicalRunRecordPaths`. It also declares a lane type, allowed difference
axes, preserved production contracts, evaluation protocol, adjudication
protocol, dated pricing basis, labels, rubric, and structural receipts.
Candidate configs and run records carry matching public `architectureId`
aliases plus opaque `architectureStructuralDigest` values so cross-lane
aggregation cannot silently mix architectures.
`PORTABLE_CORE_MODEL`, `HARNESS_ABLATION`, `BEST_SYSTEM`, and `SHADOW_PILOT`
lanes have different claim boundaries; a holistic lane is never described as
a model-only result.

The public schemas cover:

- `review-run-export` and canonical `run-record`;
- `eval-protocol` and `adjudication-protocol`;
- `benchmark-manifest`, `candidate-config`, `case-label`, `rubric`,
  `pricing-snapshot`, and `decision-policy`;
- `normalization-report`, `eval-validity-report`,
  `benchmark-scorecard`, `static-diagnostic-report`, and
  `reference-architecture-recommendation`.

The public package defines and verifies this import contract. Extraction from
a private database, live execution, blinded adjudication operations, and
prospective shadow traffic belong in a private integration layer and are not
shipped here.

Optional `staticDiagnostics.bindings` are explicit, closed records that name
the rule, declared path, lane, variant, and architecture digest. Omitted or
unmatched bindings keep a static finding non-blocking.

## CLI

Run <code>node ./scripts/reviewops.mjs --help</code> for the exact command
syntax and credential-free first run.

For contributor smoke tests from this plugin directory:

```sh
node ./scripts/reviewops.mjs validate-config --config <relative-config-path>
node ./scripts/reviewops.mjs normalize --config <relative-config-path> --format markdown
node ./scripts/reviewops.mjs audit-eval --config <relative-config-path> --format markdown
node ./scripts/reviewops.mjs benchmark --config <relative-config-path> --format markdown
node ./scripts/reviewops.mjs recommend-architecture --config <relative-config-path> --format markdown
```

For an installed plugin, use the same arguments with
`node <installed-plugin-root>/scripts/reviewops.mjs` while the working
directory remains the project being analyzed. Use `--fixture synthetic`
instead of `--config` only for the fixed bundled fixture. `--format` is
limited to `json` or `markdown`. Reports go to stdout; v0.1.0 has no output
file option.

The standalone `normalize` command emits only a bounded summary and receipts.
`audit-eval`, `benchmark`, and `recommend-architecture` independently load the
same declared lane bundles and run reviewed pure normalization and validity
logic in memory. No command consumes a prior stdout report.

## Results and failure behavior

Every JSON report includes schema and tool versions, explicit analysis time,
config and input digests, applied limits, redaction counts, warnings, claim
boundary, and limitations. Benchmark output includes lane validity, paired
denominators, metric-level missingness and exclusions, root-cause metrics,
risk slices, cost basis, latency, fixed-seed confidence intervals, stability,
and frontier eligibility.
Markdown preserves the same decision-critical statuses and reasons in
text-accessible headings and tables.
Cost values are integer micros; every benchmark metric carries an explicit
unit, and each lane reports its currency and cost basis.

| Status                  | Meaning                                                                                |
| ----------------------- | -------------------------------------------------------------------------------------- |
| `COMPLETE`              | Valid evidence supported the requested bounded analysis.                               |
| `PARTIAL`               | Safe analysis completed, but declared evidence or metrics were unavailable.            |
| `INSUFFICIENT_EVIDENCE` | Inputs were valid but cannot support the requested quality or architecture conclusion. |
| `BLOCKED`               | Unsafe, malformed, ambiguous, unsupported, or out-of-bounds input was rejected.        |
| `ERROR`                 | An internal failure occurred; only a sanitized stable error is emitted.                |

CLI exit code `0` means complete, `2` means invalid or unsafe input, `3`
means insufficient evidence, and `4` means internal failure.

## Safety boundaries

- Analyzed workflow, prompt, Markdown, shell, expression, log, and JSON text
  is hostile inert data. It is never executed, interpolated, rendered as
  instructions, or passed to a model.
- The plugin never follows referenced workflows, actions, scripts, links, or
  config files unless each file is separately declared.
- YAML analysis and benchmark scoring run in a bounded worker with a five-second
  hard timeout plus 128 MiB old-generation, 32 MiB young-generation, and 4 MiB
  stack ceilings. Bootstrap parsing is separately bounded by file, line,
  record, byte, and iterative JSON-depth limits.
- Redaction happens before evidence, errors, Markdown, or JSON reaches stdout.
  Reports prefer relative paths, line ranges, rule IDs, counts, and structural
  digests over raw content; stdout is capped at 2 MiB.
- Quality ranking requires valid paired comparable cases and versioned
  root-cause labels. Fully loaded cost is required for a primary per-dollar
  architecture decision. Missing evidence remains descriptive or
  `INSUFFICIENT_EVIDENCE`.
- Static diagnostics are secondary. Only an observed, critical, high-confidence
  diagnostic with a policy-listed rule and matching lane, variant, and
  architecture digest binding can block a shadow path; possible contributors
  are not causal proof.
- Recommendations are shadow-only and no-posting. They contain no patch,
  command, automatic route, GitHub comment, production-ready claim, or
  authorization to change a workflow.

## Accessibility

Markdown output uses headings, textual table headers, stable status words,
plain-language gate reasons, and explicit denominators. Meaning is never
conveyed by color alone. JSON carries the same status and reason fields for
assistive tools and automation.

## Verify or contribute

From the repository root:

```sh
npm run validate:marketplace
npm run validate:reviewops-auditor-benchmark
npm run verify:reviewops-source
npm run test:reviewops-auditor-benchmark
npm run test:marketplace
npm run validate
```

The package tests use synthetic fixtures and an isolated copied package. They
must pass without network, credentials, Git metadata, a home-directory read,
or runtime `node_modules`.

## Limitations

Static diagnostics cannot prove runtime permissions, cancellation, validation,
or comment behavior. Imported labels can be biased or incomplete. A scorecard
is not proof of reviewer quality, and a shadow recommendation is not approval
for production rollout. Live replay, provider calls, GitHub integration,
workflow edits, persistent artifacts, and customer-specific logic are outside
v0.1.0.
