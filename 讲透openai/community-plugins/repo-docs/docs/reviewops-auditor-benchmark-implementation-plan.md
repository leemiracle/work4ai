# ReviewOps Auditor + Benchmark implementation plan

- Status: operator-aligned implementation complete and locally qualified;
  clean PR open and CI confirmation pending
- Date: 2026-08-24
- Target repository: `tonyloehr/community-plugins`
- Package slug: `reviewops-auditor-benchmark`
- Display name: ReviewOps Auditor + Benchmark
- Release target: public v0.1.0, offline and read-only

## Why this plan changed

The first implementation followed an earlier three-skill MVP: static workflow
audit, imported-run benchmarking, and routing advice. The later planning
consensus sharpened the product around the evaluation owner's actual decision:

> Given an existing code-review controller, historical findings, a dated
> user-supplied pricing snapshot, and multiple model/harness candidates,
> identify the configuration that maximizes confirmed high/critical root-cause
> findings per dollar under fair, declared conditions.

That is a different product emphasis. The public package remains a safe,
offline scorer, but its primary job is now to establish whether an evaluation
is interpretable, measure root-cause outcomes by risk slice, and recommend a
reference architecture without replacing the existing review system.

The revised plan must not try to prove that any provider or model is better.
It must make a fair experiment the evaluation owner can trust, including an
honest answer when another model or architecture wins a lane or risk slice.

## Pre-alignment baseline

The repository already contains a qualified three-skill foundation. Its
existing evidence is useful, but it is not completion evidence for this
revised plan.

Baseline capabilities worth retaining:

- bundled, reproducible, offline CLI and bounded worker;
- strict JSON schemas, regular-file/root/symlink/hardlink checks, byte/line/
  depth/record ceilings, and worker time/memory limits;
- deterministic paired comparison, seeded confidence intervals, Pareto
  calculation, and explicit exclusions;
- redaction, Markdown escaping, stdout bounds, synthetic fixtures, copied-
  package tests, and clean-install/no-auth smoke coverage;
- read-only manifest with no MCP servers, apps, hooks, provider calls,
  network, subprocesses, writeback, or persistent state.

Baseline qualification recorded before this revision:

- 59 ReviewOps tests passed with aggregate coverage above the configured
  90% line / 80% branch / 90% function thresholds;
- build, strict schema validation, typecheck, lint, format check, marketplace
  validation, marketplace-wide tests, entrypoint syntax checks, source-bundle
  verification, npm runtime audit, diff whitespace checks, and clean isolated
  installation passed;

Those results remain historical evidence for reused safety machinery. They
must be rerun and expanded after the operator-aligned contracts, skills, fixtures,
bundles, and tests are implemented. No checklist item in this plan may be
marked complete solely from the earlier three-skill qualification.

## Executive decision

Build v0.1.0 as an explicitly invoked, vendor-neutral, offline evaluation
plugin. It reads declared sanitized local exports plus optional explicitly
opted-in bounded static workflow/prompt files treated as hostile and redacted
before output; it normalizes evidence, audits evaluation validity, computes
deterministic benchmark evidence, and emits a non-executable
reference-architecture recommendation.

The target public v0.1.0 package must contain four skills:

1. `normalize-review-runs` — validates and normalizes sanitized exports from
   an existing review/evaluation system into canonical, opaque records.
2. `audit-review-eval-validity` — checks whether a declared comparison lane
   is paired, controlled, blinded, and backed by declared leakage controls and
   adjudication evidence sufficient for its stated claim.
3. `benchmark-review-configs` — scores only validity-eligible imported runs
   with root-cause, risk-slice, quality, cost, latency, and stability metrics.
4. `recommend-review-reference-architecture` — reports the best supported
   default and per-slice architecture, preserves the existing controller
   boundary, and proposes only a shadow/no-posting next step.

Static workflow/prompt inspection remains available only as optional secondary
diagnostic context. It may suggest possible contributors to measured outcomes
or flag an observed safety concern. It is not the front door, is not causal
evidence, and is not required merely to rank a valid imported benchmark.

The public package must not:

- connect to a private evaluation database or any external service;
- invoke providers, replay PRs, execute validators, run shell commands, or
  fetch live pricing;
- replace, configure, or augment the existing controller, validator, dedupe
  layer, or posting flow;
- edit workflows, write files, open PRs, post comments, or authorize a
  production rollout;
- contain real prompts, diffs, labels, logs, prices, identifiers, URLs,
  customer names, or provider credentials.

Live execution, private data extraction, blinded adjudication operations, and
prospective shadow traffic remain in a private integration layer. The public
package defines and verifies the import contract that layer must satisfy.

## Product thesis

ReviewOps is an evidence layer around an existing reviewer, not a new reviewer.
It answers:

- Can the supplied runs be normalized without losing provenance or leaking
  private material?
- Was the comparison fair enough for the claimed lane: model-only, one-factor
  harness ablation, holistic best-system comparison, or no-posting shadow
  pilot?
- Which architecture maximizes confirmed high/critical root-cause findings
  per fully loaded dollar without worsening critical misses, hallucinations,
  root-cause quality, human review burden, or latency?
- Which model or harness wins globally and by declared PR/risk slice?
- Where do candidate architectures win or lose, and which conclusions are
  causal, holistic, descriptive, or unsupported?
- Did narrow skills, context changes, validators, retries, or routing changes
  help or hurt in a controlled lane?
- What reference architecture should be tried in shadow mode while preserving
  the current controller, validator, dedupe, and posting contracts?
- What cannot be concluded because pairing, blinding, labels, pricing,
  root-cause identity, or protocol evidence is missing?

Raw finding count, raw comment count, and accepted findings alone are
descriptive diagnostics. They are not primary success metrics.

## Goals, non-goals, and release boundary

| Area               | Public v0.1.0 must do                                                                                                       | Public v0.1.0 must not do                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Invocation         | Run only when the user explicitly names one of the four skills.                                                             | Trigger automatically on review, PR, repository open, or model response.                                        |
| Inputs             | Read bounded local JSON/JSONL exports, protocol files, pricing snapshots, and optional declared static diagnostic files.    | Read arbitrary files, follow links, crawl directories, accept URLs/tokens, or ask for raw private data in chat. |
| Normalization      | Convert a versioned sanitized export contract into canonical opaque records and report rejected-record counts/reason codes. | Connect to a database, infer missing provenance, or silently repair contradictory data.                         |
| Eval validity      | Fail closed on missing controls, pairing, blinding, adjudication, leakage, or lane provenance needed for the claim.         | Treat historical correlation, static lint, or provider identity as causal evidence.                             |
| Benchmark          | Compute deterministic global and per-slice root-cause, quality, cost, latency, and stability metrics for eligible lanes.    | Invoke models, fetch prices, use a model judge by default, or rank invalid comparisons.                         |
| Recommendation     | Emit a shadow-only, non-executable reference architecture with claim boundaries, gates, and human approval requirements.    | Replace the operator's controller, validator, dedupe, posting flow, or claim production readiness.              |
| Static diagnostics | Optionally attach bounded non-causal workflow/prompt signals as possible contributors.                                      | Make static workflow lint the primary product or a substitute for experiment validity.                          |
| Data handling      | Redact before output, use opaque IDs, and ship synthetic fixtures only.                                                     | Commit or reproduce private prompts, diffs, comments, logs, labels, prices, URLs, or identifiers.               |
| Runtime            | Use local deterministic code with no network, auth, commands, dynamic code, or provider SDKs.                               | Require OAuth, API keys, GitHub tokens, MCP servers, apps, or external services.                                |
| Persistence        | Emit validated JSON/Markdown to stdout/chat only.                                                                           | Write artifacts or mutable state in v0.1.0.                                                                     |

### Public/private split

Public package:

- four explicit skills and their safety contracts;
- strict schemas for sanitized source-neutral exports, normalized records,
  evaluation protocols, lane manifests, scorecards, and recommendations;
- deterministic normalization, validity, pairing, metrics, confidence,
  frontier, and recommendation code;
- optional bounded static diagnostic rules;
- synthetic adapter-conformance fixtures and deterministic tests;
- offline local CLI, redaction, provenance, and receipt verification.

Private integration layer:

- the operator's database/export adapter and any schema mapping from private
  storage;
- real PR corpus, prompts, diffs, traces, logs, labels, judge notes, prices,
  and organization-specific identifiers;
- live provider/model execution and controlled replay;
- blinded review operations and adjudicator workflow;
- GitHub API integration, comment publishing, rollout, and rollback actions;
- customer-specific model names, routing rules, validators, and tools when
  they are not safe to publish.

The public repository may document the adapter contract and ship synthetic
conformance data. It must not ship the private adapter or sample private data.

## Assumptions and decisions to validate early

1. The package slug remains `reviewops-auditor-benchmark`; the product
   reframing does not require a package rename before first release.
2. v0.1.0 remains offline, stdout-only, and read-only. The manifest declares
   only `Read`; no output-file flag, database access, network access, or
   writeback is added.
3. The marketplace has no `NONE` authentication policy. Use
   `policy.authentication: "ON_USE"` only if clean-install testing proves the
   synthetic workflow does not prompt for authentication or secrets. Any auth
   prompt, credential request, or implied secret setup blocks release.
4. The private adapter emits sanitized source-neutral exports. The public
   normalizer never connects to or names a private database.
5. Quality and architecture recommendations require a declared evaluation
   protocol, paired eligible cases, versioned root-cause labels, and blinded
   adjudication provenance. Without them, descriptive metrics may be shown
   but recommendation status is `INSUFFICIENT_EVIDENCE`.
6. Root-cause economics requires a declared `FULLY_LOADED` cost basis. A
   `MODEL_ONLY` snapshot may support descriptive model-cost reporting but
   cannot support the primary per-dollar architecture decision.
7. A recommendation is eligible only for at least 20 paired comparable cases
   globally and the policy's minimum per slice; 50 representative cases is
   the preferred private pilot target.
8. Static diagnostics are optional and non-causal. Missing static workflow or
   prompt files cannot by itself block a benchmark-only recommendation; only
   the versioned closed static-blocking predicate may block.
9. The existing controller, validator, dedupe policy, and posting policy are
   recorded as production-baseline contracts. A lane may evaluate declared
   candidate differences, but the plugin never labels them preserved,
   automatically adoptable, or authorized production behavior.
10. Four benchmark lane types are supported: `PORTABLE_CORE_MODEL`,
    `HARNESS_ABLATION`, `BEST_SYSTEM`, and `SHADOW_PILOT`. Each has a
    narrower claim boundary and required controls.

If an assumption changes, update this plan, schemas, threat model, fixtures,
skills, tests, and release checklist before implementation continues.

## Current implementation gap ledger

The existing foundation must be changed in these bounded areas:

| Gap                       | Required change                                                                                                                                     |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Three public skills       | Replace the public inventory with the four operator-aligned skills; remove static audit as a standalone primary skill.                              |
| Hidden normalization      | Add `normalize` CLI behavior, a sanitized export schema, normalization report schema, fixture, and tests.                                           |
| Static audit as primary   | Add an eval-validity engine and protocol schema; retain static analysis only as an optional secondary diagnostic section.                           |
| No lane contract          | Add lane type, declared difference axes, preservation contracts, controlled-field checks, and claim-boundary output.                                |
| Weak causal attribution   | Report `SINGLE_FACTOR`, `HOLISTIC_VARIANT`, `CONFOUNDED`, or `UNKNOWN`; never imply model causality from a holistic comparison.                     |
| No blinding provenance    | Add blinded identity, randomized order, human high/critical review, adjudicator independence, disagreement, leakage, and exclusion-policy evidence. |
| Finding-level economics   | Add stable root-cause identity/grouping, fully loaded cost basis, human-review minutes, and cost per confirmed high/critical root cause.            |
| No risk slices/replicates | Add declared slice taxonomy, per-slice scorecards, replicate IDs, stability metrics, and slice eligibility gates.                                   |
| Routing advice            | Replace it with a reference-architecture report that preserves existing contracts and nests any routing guidance as non-executable evidence.        |
| Old qualification         | Rebuild bundles, expand fixtures/tests, rerun clean install/security/quality gates, and record new evidence before PR.                              |

## User experience

### Safe first prompt

The README and manifest should lead with the credential-free normalization
fixture:

```text
Use $normalize-review-runs on the bundled synthetic fixture only. Explain the
normalization summary, provenance checks, safety boundaries, and next safe
step.
```

The second documented prompt should validate the synthetic experiment:

```text
Use $audit-review-eval-validity on the bundled synthetic fixture only. Explain
which comparison claim is supported, which controls are held constant, and
what would block a recommendation.
```

The third documented prompt should score only the synthetic valid lane:

```text
Use $benchmark-review-configs on the bundled synthetic fixture only. Explain
the eligible root-cause metrics, exclusions, confidence intervals, and risk
slice limitations.
```

The fourth documented prompt should produce only a synthetic shadow report:

```text
Use $recommend-review-reference-architecture on the bundled synthetic fixture
only. Explain the claim boundary, preserved production contracts, human
approval gate, and no-posting shadow next step.
```

The fixture is synthetic, fixed, plugin-relative, and deliberately
non-production. It must not scan the user's repository or contact a service.

### Real workflow sequence

```text
Explicit skill invocation
        ↓
Validate config, roots, paths, sizes, schemas, and redaction
        ↓
Normalize sanitized private-export records into canonical opaque records
        ↓
Audit lane, pairing, controls, blinding, leakage, and adjudication validity
        ↓
Score only validity-eligible comparisons and risk slices
        ↓
Emit claim-bounded reference architecture and shadow-only next step
```

The four skills share declared input contracts but remain independently useful:

1. normalize sanitized exports;
2. audit whether the experiment supports its stated claim;
3. benchmark eligible runs;
4. recommend a reference architecture from the evidence.

No skill invokes another skill, consumes a prior stdout report, or loads
undeclared inputs. Instead, `audit-eval`, `benchmark`, and
`recommend-architecture` independently run the same reviewed pure
normalization and validity modules in memory from the same declared lane
bundles. The standalone `normalize` command emits a bounded summary and
receipts, not a corpus. Missing prerequisites return a bounded, actionable
`PARTIAL`, `INSUFFICIENT_EVIDENCE`, or `BLOCKED` result.

## Shipped package shape

```text
.agents/plugins/marketplace.json
plugins/reviewops-auditor-benchmark/
  .codex-plugin/plugin.json
  README.md
  LICENSE
  THIRD_PARTY_NOTICES.txt
  package.json
  package-lock.json
  build.mjs
  assets/
    icon.svg
  schemas/
    common.schema.json
    config.schema.json
    config-validation.schema.json
    review-run-export.schema.json
    normalization-report.schema.json
    eval-protocol.schema.json
    adjudication-protocol.schema.json
    benchmark-manifest.schema.json
    candidate-config.schema.json
    decision-policy.schema.json
    tool-contract.schema.json
    validator-result.schema.json
    rubric.schema.json
    pricing-snapshot.schema.json
    run-record.schema.json
    case-label.schema.json
    eval-validity-report.schema.json
    benchmark-scorecard.schema.json
    reference-architecture-recommendation.schema.json
    static-diagnostic-report.schema.json
  rules/
    eval-validity-rules.json
    workflow-rules.json
    prompt-rules.json
    telemetry-rules.json
  scripts/
    reviewops.mjs
    reviewops-worker.mjs
  src/
    cli.mjs
    worker.mjs
    bounds.mjs
    paths.mjs
    redact.mjs
    yaml.mjs
    schema.mjs
    normalize/
      index.mjs
    eval/
      index.mjs
      lanes.mjs
      adjudication.mjs
      static-diagnostics.mjs
    benchmark/
      validity.mjs
      metrics.mjs
      paired.mjs
      pareto.mjs
      confidence.mjs
      slices.mjs
      stability.mjs
    recommend/
      index.mjs
      gates.mjs
      architecture.mjs
  fixtures/
    synthetic/
      README.md
      reviewops.config.json
      exports/
        review-runs.jsonl
      benchmark/
        benchmark-manifest.json
        eval-protocol.json
        adjudication-protocol.json
        candidate-a.json
        candidate-baseline.json
        case-labels.jsonl
        decision-policy.json
        pricing.json
        rubric.json
      diagnostics/
        workflows/code-review.yml
        prompts/reviewer.md
  skills/
    normalize-review-runs/
      SKILL.md
      agents/openai.yaml
    audit-review-eval-validity/
      SKILL.md
      agents/openai.yaml
    benchmark-review-configs/
      SKILL.md
      agents/openai.yaml
    recommend-review-reference-architecture/
      SKILL.md
      agents/openai.yaml
tests/reviewops-auditor-benchmark/
  README.md
  unit/
    audit-units.test.mjs
    benchmark-units.test.mjs
    eval-validity.test.mjs
    json.test.mjs
    normalize.test.mjs
    recommendation.test.mjs
    worker.test.mjs
  integration/
    accessibility.test.mjs
    packaged.test.mjs
    reviewops.test.mjs
  security/
    security.test.mjs
scripts/validate-reviewops-auditor-benchmark.mjs
scripts/verify-reviewops-source.mjs
.github/workflows/reviewops-auditor-benchmark.yml
```

The exact file split may remain smaller when a module would be a thin wrapper,
but every public contract above needs one reviewed implementation owner,
schema, negative tests, and user-facing documentation. Do not add abstraction
only to make the tree match the diagram.

Use a plugin-local private `package.json` and lockfile for build tooling.
`build.mjs` bundles reviewed source and exact pinned dependencies into the
shipped scripts; installed execution must not need `node_modules`.
`scripts/verify-reviewops-source.mjs` rebuilds in an isolated temp directory,
compares hashes, checks notices/lockfile metadata, and proves the copied
package has no ancestor dependency resolution.

## Packaging and manifest plan

### Marketplace entry

Append without reordering existing entries:

```json
{
  "name": "reviewops-auditor-benchmark",
  "source": {
    "source": "local",
    "path": "./plugins/reviewops-auditor-benchmark"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_USE"
  },
  "category": "Developer Tools"
}
```

### Manifest intent

The manifest must include:

- `name: "reviewops-auditor-benchmark"`;
- strict semver, initially `0.1.0`;
- a description that says it normalizes, validates, benchmarks, and
  recommends from imported review-run evidence offline;
- `skills: "./skills/"`;
- `interface.capabilities: ["Read"]`;
- no `mcpServers`, apps, hooks, commands, auth integrations, or write
  capability;
- HTTPS repository/homepage links and a reviewed local icon;
- default prompts that start with the synthetic normalization/eval-validity
  fixture and never imply automatic scanning, credentials, live execution, or
  provider preference.

Manifest, marketplace entry, README, CLI help, schemas, and four-skill
inventory must agree exactly. The plugin validator rejects unknown fields,
missing licenses/safety sections, invalid icons, symlinks, stale three-skill
names, and capability drift.

### Runtime dependency policy

Use a small bundled offline runtime:

- Node.js 22.19+ ESM and built-ins where possible;
- exact lockfile-pinned reviewed YAML/parser and JSON Schema dependencies;
- precompiled fixed schemas, with no user-supplied code generation;
- bounded `worker_threads` for YAML analysis and scoring;
- parent-side regular-file, byte, line, record, depth, timeout, memory, and
  stdout enforcement;
- no install scripts, dynamic imports from user paths, `eval`, `Function`,
  `child_process`, network modules, runtime package resolution, or ambient
  secret-bearing environment reads.

Every dependency needs a pinned version, license/notice review, reproducible
bundle receipt, and a reason it is preferable to a built-in.

## CLI contract

The shipped entrypoint exposes only these deterministic subcommands:

```sh
node ./scripts/reviewops.mjs validate-config --config <path>
node ./scripts/reviewops.mjs normalize --config <path> --format markdown
node ./scripts/reviewops.mjs audit-eval --config <path> --format markdown
node ./scripts/reviewops.mjs benchmark --config <path> --format markdown
node ./scripts/reviewops.mjs recommend-architecture --config <path> --format markdown
```

Contract rules:

- no command accepts a URL, token, header, shell command, executable path,
  provider credential, arbitrary glob, or live-service identifier;
- `--config` is required except for the fixed `--fixture synthetic` path;
- `--format` is limited to `json` or `markdown`;
- stdout is the only report channel; stderr contains only sanitized stable
  errors;
- exit code `0` means complete, `2` invalid/unsafe input, `3`
  insufficient evidence, and `4` internal failure;
- every result includes `schemaVersion`, `toolVersion`, `analysisAsOf`,
  `configDigest`, structural input digests, applied limits, redaction counts,
  warnings, status, and claim boundary;
- output ordering and JSON serialization are stable across reruns.

`analysisAsOf` is an explicit config value or injected test clock, never an
ambient scoring-core wall clock. Digests are of redacted structural
projections only; they must not hash raw prompts, diffs, logs, PR numbers, or
other low-entropy private values. Candidate/case/root-cause identities are
opaque exporter IDs or exporter-side HMACs whose key never enters the plugin.

`--fixture synthetic` resolves only a validator-hashed plugin-relative
fixture directory. It never falls back to the current repository. v0.1.0 has
no output-file flag.

## Input contract and bounds

Do not ask users to paste secrets, raw prompts, diffs, logs, comments, or
customer records into chat or config. The public plugin reads only declared
local files under approved roots and treats every byte as hostile data.

### Config

The authoritative config is strict JSON with `additionalProperties: false`.
One config may declare one to eight independent lane bundles. Every command
loads the same declared bundles; `benchmark` reports each lane separately,
and `recommend-architecture` aggregates only compatible eligible lanes.
Representative primary shape:

```json
{
  "schemaVersion": 1,
  "analysisAsOf": "2026-08-01T00:00:00Z",
  "repoRoot": ".",
  "inputRoots": ["."],
  "decisionPolicyPath": "local-inputs/decision-policy.json",
  "laneBundles": [
    {
      "bundleId": "portable-core",
      "exportPaths": ["local-inputs/portable-core/review-runs.jsonl"],
      "manifestPath": "local-inputs/portable-core/benchmark-manifest.json",
      "evalProtocolPath": "local-inputs/portable-core/eval-protocol.json",
      "adjudicationProtocolPath": "local-inputs/portable-core/adjudication-protocol.json",
      "candidateConfigPaths": ["local-inputs/portable-core/candidates.json"],
      "rubricPath": "local-inputs/portable-core/rubric.json",
      "pricingSnapshotPath": "local-inputs/portable-core/pricing.json",
      "caseLabelPaths": ["local-inputs/portable-core/case-labels.jsonl"]
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

`local-inputs/` is an example ignored private input root and must never be
committed with real data. `repoRoot` is exactly `.` and informational; the
runtime rejects absolute, parent-broadening, and sibling roots. Every
`inputRoots` entry is a relative descendant of the trusted invocation root.
The local CLI captures that root before config parsing. No config field can
broaden it.

Each lane bundle is self-contained and receipt-bound. The standalone
`normalize` command reports normalization status for its declared bundles;
later commands rerun that same pure normalization in memory. No command asks
the user to save stdout or trusts a user-supplied prior report. A lane bundle
declares exactly one source mode: `exportPaths` for source-neutral sanitized
exports or `canonicalRunRecordPaths` for private-adapter-produced canonical
records. Supplying both is `BLOCKED`; the example uses `exportPaths`.

Static diagnostics are optional and intentionally absent from the primary
example. An opt-in block may be added only when the operator wants non-causal
explanatory context:

```json
{
  "staticDiagnostics": {
    "bindings": [
      {
        "ruleId": "RO-WF-002",
        "path": ".github/workflows/code-review.yml",
        "laneId": "portable-core-2026-08",
        "variantId": "baseline",
        "architectureStructuralDigest": "sha256:6666666666666666666666666666666666666666666666666666666666666666",
        "applicableToShadowPath": true
      }
    ],
    "workflowPaths": [".github/workflows/code-review.yml"],
    "promptPaths": ["prompts/reviewer.md"],
    "telemetryPaths": [],
    "toolContractPaths": ["local-inputs/tool-contract.json"],
    "validatorResultPaths": ["local-inputs/validator-results.jsonl"]
  }
}
```

Its absence yields `staticDiagnosticContext: NOT_SUPPLIED`, not a failed
benchmark. A diagnostic may become a possible contributor or blocking input
only when it is explicitly bound to a rule/path/lane/variant, its architecture
digest matches that candidate, and shadow applicability is explicit; unbound
diagnostics remain safety annotations only. If
supplied, findings are clearly labeled non-causal and the
possible-contributor section is capped at three findings.

### Path policy

For every path:

1. anchor the trusted workspace root from invocation context;
2. resolve relative paths and canonicalize them;
3. open with no-follow semantics where supported and `fstat` before reading;
4. require a regular single-link file; reject symlinks, hardlinks, directories,
   sockets, devices, FIFOs, NUL bytes, and traversal;
5. compare canonical path/device/inode before and after open;
6. require containment in an explicitly declared relative input root;
7. enforce extension, count, byte, line, record, and nesting bounds before
   parsing;
8. never enumerate undeclared directories or follow globs.

Allowed extensions:

- JSON contracts/pricing/config: `.json`;
- run/export/label records: `.json` or `.jsonl`;
- optional workflow diagnostics: `.yml` or `.yaml`;
- optional prompt diagnostics: `.md` or `.txt`.

### Hard ceilings

Config may lower but never exceed compiled ceilings:

- 100 files;
- 2 MiB per workflow/prompt;
- 8 MiB per JSON/JSONL input file;
- 32 MiB total input;
- 10,000 records;
- 8 lane bundles;
- 1,000 findings per run;
- 256 risk slices and 32 replicates per case/variant;
- 128 KiB emitted evidence excerpt budget;
- 2 MiB total stdout;
- 5-second hard worker timeout;
- maximum JSON nesting depth 32.

A bound violation fails closed with a stable code and no partial unredacted
output. Worker output is emitted only after completion, schema validation,
redaction, and safe rendering.

## Public schemas and canonical records

All schemas use `additionalProperties: false`, version independently, reject
unknown enums, and validate before use and before output.

### Sanitized export and normalization report

The private adapter emits `review-run-export` records containing only opaque
IDs, structural digests, typed outcome fields, bounded counts, and provenance.
The public normalizer accepts no raw prompt, diff, comment body, log payload,
URL, token, command, or provider credential field.

Normalization must:

- validate schema versions and reject unknown fields;
- canonicalize stable IDs, timestamps, money, enum casing, and ordering;
- reject duplicate or contradictory case/variant/run/finding/root-cause IDs;
- preserve source/exporter version, source record count, dropped-record
  reasons, redaction counts, and structural receipts;
- emit a bounded `normalization-report` with counts, digests, reason codes,
  and receipts only; canonical records remain in bounded process memory for
  the current command and are never dumped as an unbounded stdout corpus;
- report `PARTIAL` for a standalone descriptive summary when whole records
  are rejected, and `BLOCKED` when provenance or safety is ambiguous;
- block causal ranking and architecture recommendation when rejected records
  could alter a case/variant/replicate cohort, unless each rejection is a
  predeclared, symmetric, provenance-backed exclusion under the lane's
  exclusion policy.

The public normalizer is not a database connector and does not infer absent
labels, costs, controls, or adjudication. It never repairs fields in place:
an invalid record is accepted whole or rejected whole with a stable reason.

### Identifier contract

Use two closed identifier formats:

- `opaqueDigestId`: `sha256:<64 lowercase hex>` for case, run, finding,
  root-cause, cohort, export, and structural-receipt identities that could
  otherwise reveal private data. These are produced by the private exporter,
  never by hashing a raw low-entropy value inside the plugin.
- `publicAlias`: `[a-z][a-z0-9._-]{0,63}` for public, non-sensitive lane,
  variant, rubric, policy, contract, and replicate names.

Schemas use shared `$defs` for both formats; examples and fixtures must be
valid against those definitions.

### Canonical run record

Each run carries only scoring evidence:

```json
{
  "schemaVersion": 1,
  "caseId": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "variantId": "baseline",
  "runId": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "replicateId": "replicate_001",
  "contextDigest": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "toolContractId": "review-tools-v1",
  "controllerContractId": "controller-v1",
  "validatorContractId": "validator-v1",
  "dedupePolicyId": "dedupe-v1",
  "postingPolicyId": "posting-v1",
  "reasoningClass": "standard",
  "retryPolicyId": "retry-v1",
  "timeoutPolicyId": "timeout-v1",
  "routingPolicyId": "routing-v1",
  "startedAt": "2026-08-01T00:00:00Z",
  "latencyMs": 12345,
  "usage": {
    "inputTokens": 0,
    "outputTokens": 0,
    "cachedInputTokens": 0
  },
  "cost": {
    "currency": "USD",
    "amountMicros": 0,
    "costBasis": "FULLY_LOADED",
    "costSource": "RECONSTRUCTED_COMPONENTS",
    "pricingSnapshotId": "pricing-2026-08-01",
    "components": {
      "modelMicros": 0,
      "toolingMicros": 0,
      "humanReviewMicros": 0
    }
  },
  "humanReviewMinutes": 0.0,
  "findings": [
    {
      "findingId": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
      "severity": "HIGH",
      "category": "SECURITY",
      "verification": "VERIFIED",
      "tags": ["cross-system"]
    }
  ],
  "adjudication": {
    "status": "ADJUDICATED",
    "rubricId": "review-rubric-v1",
    "labelVersion": "v1",
    "findingLabels": [
      {
        "findingId": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        "outcome": "ACCEPTED",
        "matchedRootCauseIds": [
          "sha256:3333333333333333333333333333333333333333333333333333333333333333"
        ]
      }
    ],
    "rootCauseAssessments": [
      {
        "rootCauseId": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
        "qualityScore": 1.0,
        "qualityRubricId": "review-rubric-v1"
      }
    ]
  }
}
```

Raw PR numbers, URLs, titles, paths, authors, diffs, prompt text, comment
bodies, and logs are not required and are rejected.

### Case labels, root causes, and risk slices

Case labels supply denominators independently of any candidate:

```json
{
  "schemaVersion": 1,
  "caseId": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "rubricId": "review-rubric-v1",
  "labelVersion": "v1",
  "riskSliceIds": ["auth", "cross-service"],
  "groundTruth": [
    {
      "rootCauseId": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
      "severity": "HIGH",
      "tags": ["cross-system"]
    }
  ],
  "provenance": {
    "kind": "USER_SUPPLIED",
    "sourceLabel": "redacted-local-labels"
  }
}
```

Rules:

- `rootCauseId` is stable within the exported corpus and never derived from
  candidate wording;
- multiple symptom findings may match one root cause, but confirmed root
  causes count once;
- one finding may match multiple root causes only when the rubric explicitly
  allows it;
- a root cause is confirmed only when at least one eligible accepted finding
  matches it under the versioned rubric;
- root-cause quality is read only from typed `rootCauseAssessments` tied to
  the same rubric/version; it is never inferred from finding text or count;
- slice taxonomy/version is declared in the manifest, not inferred from code
  paths or prompt text;
- a case may belong to multiple slices, while global denominators count it
  once;
- unknown, duplicate, contradictory, or cross-version matches block
  root-cause quality ranking.

### Pricing snapshot

Pricing is explicit, dated, user-supplied, and source-neutral:

```json
{
  "schemaVersion": 1,
  "snapshotId": "pricing-2026-08-01",
  "currency": "USD",
  "effectiveAt": "2026-08-01T00:00:00Z",
  "costBasis": "FULLY_LOADED",
  "provenance": {
    "kind": "USER_SUPPLIED",
    "sourceLabel": "redacted-local-snapshot"
  },
  "rates": [
    {
      "variantId": "baseline",
      "inputMicrosPerMillion": 0,
      "cachedInputMicrosPerMillion": 0,
      "outputMicrosPerMillion": 0,
      "toolingMicrosPerRun": 0,
      "humanReviewMicrosPerMinute": 0
    }
  ]
}
```

Money uses non-negative integer micros of the declared currency. Exactly one
cost source applies per run:

- `SUPPLIED_TOTAL`: exporter-supplied `amountMicros` is authoritative;
  when components are present, their exact integer sum must equal the total;
- `RECONSTRUCTED_COMPONENTS`: model, tooling, and human-review components
  are reconstructed from explicit snapshot rates, token counts, and
  `humanReviewMinutes`; their exact integer sum becomes `amountMicros`.

`FULLY_LOADED` requires known model, tooling, and human-review components.
`MODEL_ONLY` permits only descriptive model-cost reporting and is never
promoted to fully loaded. Human minutes are converted to money only through an
explicit `humanReviewMicrosPerMinute` rate; they are not double-counted when
a supplied total is authoritative. Reports distinguish supplied from
reconstructed cost and never fetch prices, silently mix currencies, or treat
stale/unsupported pricing as decision-ready.

### Benchmark manifest and lane contract

The benchmark manifest is the authoritative owner of lane identity/type,
baseline, allowed difference axes, cohort identity/window, execution mode,
slice taxonomy, and bundle receipts. It includes a required `lane` object:

```json
{
  "laneId": "portable-core-2026-08",
  "laneType": "PORTABLE_CORE_MODEL",
  "baselineVariantId": "baseline",
  "cohortSelectionDigest": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
  "cohortWindowId": "sha256:5555555555555555555555555555555555555555555555555555555555555555",
  "allowedDifferenceAxes": ["modelAlias"],
  "executionMode": "OFFLINE_REPLAY"
}
```

The engine derives `claimBoundary` from lane type plus attribution status; it
never accepts exporter-written free text as the claim. The manifest also
lists one structural receipt per required artifact kind:
`EXPORT`, `MANIFEST`, `EVAL_PROTOCOL`, `ADJUDICATION_PROTOCOL`,
`CANDIDATES`, `RUBRIC`, `PRICING`, and `CASE_LABELS`; include
`CANONICAL_RUNS` only when the private adapter supplies canonical records
instead of source-neutral exports. IDs/digests must cross-validate across the
bundle before scoring.

Supported lane types:

| Lane                  | Allowed claim                                      | Required controls                                                                                                                                                                            |
| --------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PORTABLE_CORE_MODEL` | Model comparison under equal declared conditions.  | Same corpus, prompt, controller/harness, context, tools, validator, dedupe, posting, reasoning class, retries, timeout, routing, rubric, and pricing semantics. Only model alias may differ. |
| `HARNESS_ABLATION`    | Effect of exactly one declared workflow component. | Same model and all controls except one allowed axis such as validator, context, skills, retries, verification, or routing.                                                                   |
| `BEST_SYSTEM`         | Best complete architecture comparison.             | Multiple declared model/harness differences are allowed; output is holistic system evidence, never model-only causality.                                                                     |
| `SHADOW_PILOT`        | Prospective silent comparison.                     | Same observed cohort/window, paired cases, complete provenance, and `executionMode: SHADOW_NO_POSTING`.                                                                                      |

Candidate/run provenance must expose bounded IDs or structural digests for:

- stable architecture ID and architecture structural digest;
- controller/harness;
- prompt/config;
- context;
- tool contract;
- validator;
- dedupe;
- posting;
- reasoning class;
- retry;
- timeout;
- routing;
- model alias;
- replicate.

The manifest separately records `productionBaselineContracts` for the
operator's existing controller, validator, dedupe, and posting policy.
Candidate/run contract IDs describe the evaluated architecture; they are not
automatically called preserved. For `SHADOW_PILOT`,
`executionMode: SHADOW_NO_POSTING` is an external side-effect suppression
mode while the production posting-policy ID remains unchanged metadata. If a
candidate changes controller, validator, dedupe, or posting contracts, the
report labels that difference explicitly and may describe it only as a
shadow candidate requiring separate private approval; it cannot present it as
an already-preserved or automatically adoptable default.

No raw prompt, command, diff, credential, provider request, or private
identifier enters the public contract.

### Evaluation and adjudication protocols

`eval-protocol` is authoritative for sampling, assignment, pairing,
exclusions, leakage-control declarations, and held-constant requirements. It
references the manifest lane ID and must not redefine lane type or allowed
axes. It must declare:

- protocol ID/version and intended claim;
- sampling frame, cohort selection digest, cohort window, inclusion and
  exclusion policy IDs;
- assignment and pairing method;
- replicate aggregation method (v0.1.0 accepts only `CASE_PRIMITIVES`) and
  symmetric missing-replicate policy;
- declared leakage controls, evidence status, and known contamination;
- held-constant fields;
- controller, validator, dedupe, posting, tool, context, retry, timeout, and
  routing preservation contracts;
- the manifest execution mode expected for shadow lanes.

`adjudication-protocol` is authoritative for review presentation/blinding and
references the manifest, rubric, and label versions. It must declare:

- protocol ID/version;
- variant identity `HIDDEN` or `VISIBLE`;
- presentation order `RANDOMIZED` or `FIXED`;
- high/critical review `HUMAN` or `OTHER`;
- declared adjudicator independence/provenance and its evidence status;
- disagreement policy ID and bounded disagreement counts/statuses;
- rubric ID and label version.

The scorer validates declarations and receipts; it cannot prove that the real
process was leakage-free or independent. Every such check is emitted as
`DECLARED` or `UNKNOWN`, never as proven runtime fact. Missing, visible,
fixed-order, non-human high/critical, or unreported disagreement evidence may
remain descriptive but cannot support a quality or architecture
recommendation.

## Eval-validity engine

### Pipeline

```text
Schema validation and normalization
              ↓
Protocol, lane, provenance, and blinding checks
              ↓
Pairing and explicit exclusions
              ↓
Attribution status and claim boundary
              ↓
Eligibility for metrics and recommendation
```

### Output

The `eval-validity-report` includes:

- status and stable reason codes;
- lane ID/type and engine-derived claim boundary;
- pairing coverage and exclusions;
- held-constant dimensions;
- intentionally changed dimensions;
- unexpected or missing dimensions;
- blinding, randomization, adjudication, disagreement, leakage, and
  exclusion-policy checks;
- attribution status;
- limitations and exact evidence required to become eligible.

Attribution statuses:

- `SINGLE_FACTOR` — exactly one declared treatment axis changed and every
  required preservation contract matches;
- `HOLISTIC_VARIANT` — multiple declared dimensions changed in a
  `BEST_SYSTEM` comparison; system-level ranking is allowed but component or
  model causality is not;
- `CONFOUNDED` — required controls are missing/mismatched or unexpected
  differences exist;
- `UNKNOWN` — supplied evidence is safe but insufficient to classify.

Behavior:

- malformed/contradictory provenance is `BLOCKED`;
- missing provenance, uncontrolled differences, failed blinding, or
  unsupported lane evidence is `INSUFFICIENT_EVIDENCE`;
- a valid `BEST_SYSTEM` lane may rank systems but must carry a holistic
  claim boundary;
- no quality ranking or architecture recommendation is emitted when
  eval-validity is incomplete;
- static workflow diagnostics cannot substitute for causal validity.

Initial reason/rule codes:

| ID          | Check                                                                                         |
| ----------- | --------------------------------------------------------------------------------------------- |
| `RO-EV-001` | Required lane contract is present and internally consistent.                                  |
| `RO-EV-002` | Cohort selection, window, assignment, and pairing are compatible.                             |
| `RO-EV-003` | Required held-constant fields match for the lane.                                             |
| `RO-EV-004` | Difference axes are declared and valid for the lane.                                          |
| `RO-EV-005` | Harness ablation changes exactly one allowed axis.                                            |
| `RO-EV-006` | Controller, validator, dedupe, and posting contracts are preserved or intentionally declared. |
| `RO-EV-007` | Retry, timeout, routing, context, and tool contracts match where required.                    |
| `RO-EV-008` | Adjudication is blinded/randomized and high/critical review is human.                         |
| `RO-EV-009` | Disagreement policy/results and adjudicator independence are present.                         |
| `RO-EV-010` | Leakage controls and exclusion policy provenance are declared.                                |
| `RO-EV-011` | Shadow lane declares `SHADOW_NO_POSTING`.                                                     |

Every rule requires valid, invalid, missing-evidence, and contradictory
fixtures plus a documented claim boundary.

### Optional static diagnostics

Static workflow, prompt, and telemetry analysis is a secondary section of
`audit-review-eval-validity`, only when explicitly configured. Existing
`RO-WF-*`, `RO-PR-*`, and `RO-TL-*` rules may be retained with these
limits:

- findings remain `OBSERVED`, `INFERRED`, or `UNKNOWN`;
- they never establish experiment validity or causal savings;
- a static finding blocks only when its rule ID appears in the decision
  policy's closed `blockingStaticRuleIds` list, its evidence is
  `OBSERVED`, its severity is `CRITICAL`, its confidence is `HIGH`, and
  it is explicitly bound by matching lane/variant/structural digests and
  marked applicable to the proposed shadow path;
- inferred/unknown hygiene findings become limitations or possible
  contributors, not recommendation blockers;
- missing diagnostics becomes `NOT_SUPPLIED`, not a failed eval.

The default policy's `blockingStaticRuleIds` list is empty because the public
plugin executes no workflow. A private operator policy may opt into a
versioned closed subset of `RO-WF-*`, `RO-PR-*`, and `RO-TL-*` rules. The
exact predicate above is the only static-diagnostic blocking path; unbound
diagnostics are safety annotations only.

The recommendation may include at most a small “possible contributors”
section:

- context/concurrency/timeout signals may relate to cost or latency;
- validation/dedupe/comment-budget signals may relate to false positives,
  hallucinations, or comment volume;
- permissions/supply-chain findings remain safety annotations.

Every link must say “possible contributor; not causal evidence.”

## Benchmark engine

### Pipeline

```text
Declared lane bundle + pricing snapshot
              ↓
Shared in-memory normalization and eval-validity stage
              ↓
Lane-aware pairing and exclusions
              ↓
Global and per-slice metric calculation
              ↓
Seeded paired confidence intervals and stability
              ↓
Pareto frontier with eligibility
              ↓
Reference-architecture recommendation gates
```

### Comparability gate

Two variants are scoreable only when:

- they share eligible paired case IDs after explicit exclusions;
- lane-required context, tool, controller, validator, dedupe, posting,
  reasoning, retry, timeout, routing, rubric, label, and pricing semantics
  match;
- differences are allowed by the declared lane;
- timestamps/pricing semantics are compatible;
- no unresolved duplicate case/variant/replicate record exists;
- no normalization rejection changes the cohort unless it is a predeclared,
  symmetric, provenance-backed exclusion;
- eval-validity status permits the requested claim.

The report lists every excluded case and reason. It never silently compares
unpaired samples or turns missing variants into failures.

### Decision metrics

Compute only metrics supported by supplied fields:

| Metric                                                   | Definition                                                                                                                        | Required evidence                                                   |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| High/critical root-cause recall                          | Unique confirmed high/critical root causes divided by labeled high/critical root causes.                                          | Versioned root-cause labels, matching, adjudication.                |
| Critical miss rate                                       | Missed critical root causes divided by labeled critical root causes.                                                              | Complete critical ground truth and adjudication.                    |
| Actionable precision                                     | Accepted adjudicated findings divided by accepted plus rejected findings.                                                         | Complete eligible finding adjudication.                             |
| Cross-system true positives                              | Unique confirmed root causes tagged cross-file/cross-system.                                                                      | Root-cause tags and matching.                                       |
| Symptoms per root cause                                  | Accepted symptom findings divided by unique confirmed root causes.                                                                | Stable finding/root-cause IDs.                                      |
| Hallucination rate                                       | Unverified or rejected claims divided by eligible findings.                                                                       | Verification/adjudication states.                                   |
| Human review minutes                                     | Imported human review effort per case and confirmed root cause.                                                                   | Typed bounded effort fields.                                        |
| Fully loaded cost per confirmed high/critical root cause | Eligible `FULLY_LOADED` cost divided by unique confirmed high/critical root causes. This is the primary economic decision metric. | Fresh fully loaded pricing/cost, root-cause identity, and severity. |
| Fully loaded cost per confirmed root cause               | Eligible `FULLY_LOADED` cost divided by all unique confirmed root causes. Descriptive/secondary only.                             | Fresh fully loaded pricing/cost and root-cause identity.            |
| Root-cause quality                                       | Versioned human/rubric score over confirmed root causes.                                                                          | Versioned rubric and labels.                                        |
| Finding stability                                        | Agreement over confirmed root-cause sets across paired replicates.                                                                | Replicate IDs and stable root-cause matches.                        |
| Latency p50/p95/p99                                      | Deterministic quantiles over eligible runs.                                                                                       | Latency milliseconds.                                               |
| Cost p50/p95/p99                                         | Deterministic quantiles over eligible fully loaded costs.                                                                         | Eligible cost basis.                                                |

Descriptive-only metrics may include cost per reviewed case, model-only cost,
token usage, raw finding count, accepted finding count, comment volume, and
cross-file finding count. They cannot select the winner by themselves.

For every metric emit denominator, coverage, eligibility, missingness,
exclusions, and seeded paired confidence interval where applicable. A zero
confirmed-root-cause denominator yields unavailable, never zero cost.

Finding stability is the macro-average pairwise Jaccard agreement over the
confirmed root-cause ID sets for every eligible case/variant replicate pair.
Cases whose compared sets are both empty are unavailable for stability rather
than scored as perfect agreement. Emit eligible case count, replicate-pair
count, denominator, and missingness.

### Risk slices

Compute one global scorecard and one scorecard per declared slice:

- slices come from exporter-supplied taxonomy/version, never inference;
- one case can belong to multiple slices, but global denominators count once;
- each slice has its own paired count, exclusions, metrics, frontier,
  limitations, and eligibility status;
- no per-slice architecture is recommended below the policy minimum;
- the decision policy predeclares at most eight `decisionSliceIds`; their
  recommendation intervals use the policy's fixed
  `sliceMultiplicityMethod` (default `HOLM_BONFERRONI`);
- additional declared slices are descriptive-only and cannot emit a winner;
- an unsupported slice remains `INSUFFICIENT_EVIDENCE`, never inherits the
  global winner silently.

### Multi-lane aggregation

`benchmark` reports each declared lane bundle independently and never pools
cases or metrics across lanes. `recommend-architecture` may aggregate up to
eight independently valid lane reports in memory only when they use the same
decision-policy ID, compatible rubric/label versions, compatible slice
taxonomy, compatible pricing semantics, cross-validated architecture IDs and
structural digests, matching production-baseline contracts, and either the
same case universe/cohort-selection digest or a predeclared compatible nested
cohort relationship.

Aggregation rules:

- `PORTABLE_CORE_MODEL` supports model-only evidence and best-model-by-slice
  reporting under equal controls;
- `HARNESS_ABLATION` supports one-component evidence only;
- `BEST_SYSTEM` may select a holistic default/per-slice architecture;
- `SHADOW_PILOT` may confirm or reject a no-posting prospective candidate;
- causal findings from portable-core/ablation lanes explain a recommendation
  but do not overwrite holistic metrics;
- no global winner is synthesized by averaging incompatible lanes;
- a lane with incompatible architecture identity, baseline contracts, cohort
  relationship, or pricing semantics remains lane-scoped and cannot explain
  or support another lane's architecture recommendation;
- when no eligible `BEST_SYSTEM` or `SHADOW_PILOT` lane exists, output
  remains lane-scoped or `INSUFFICIENT_EVIDENCE` for a default architecture.

### Statistics and determinism

- use paired deltas wherever possible;
- treat the case/PR as the inferential unit: use the protocol's fixed
  `replicateAggregation: CASE_PRIMITIVES` before any primary delta or
  bootstrap;
- for pooled ratio metrics, average each replicate-level primitive numerator
  and denominator within case/variant, then sum those case-level primitives
  across paired cases and recompute the ratio; for example, high/critical
  economics is `sum(mean(costMicros)) / sum(mean(confirmedHighCriticalRootCauses))`;
- a case with zero confirmed high/critical roots still contributes its cost
  and zero denominator; only a zero pooled denominator makes the ratio
  unavailable;
- for scalar tail metrics, compute the configured quantile over one
  case-level replicate mean per case/variant; stability is calculated
  separately from replicate sets;
- resample paired cases, never individual replicate rows; unbalanced or
  missing replicates block ranking unless symmetrically excluded under the
  predeclared policy, and every bootstrap draw recomputes pooled ratios from
  the sampled case primitives;
- use fixed seeded paired bootstrap intervals and publish seed, method,
  iteration count, and confidence level;
- use stable sort keys and deterministic tie-breaking;
- report sample size, denominator, exclusions, missingness, coverage, and
  interval for every decision metric;
- mark frontier dimensions `UNKNOWN` when required evidence is missing;
- never call an interval-overlap tie a winner unless the report explicitly
  labels a versioned policy choice;
- compute replicate stability with deterministic set agreement, not model
  judging.

### Pareto frontier

Default decision dimensions:

- maximize high/critical root-cause recall;
- minimize critical miss rate;
- maximize actionable precision;
- minimize hallucination rate;
- maximize root-cause quality;
- minimize fully loaded cost per confirmed high/critical root cause;
- minimize human review minutes;
- minimize p95 latency.

P99 cost/latency and finding stability are guardrails by default and may
become frontier dimensions only through a versioned policy. Missing required
dimensions remove a variant from automatic recommendation, not descriptive
display. The point-estimate Pareto frontier is descriptive only. A candidate
can become recommendation-eligible only when it is on that descriptive
frontier, passes every interval-backed pairwise policy gate, and is not tied
with another eligible frontier candidate under the versioned tie policy; the
engine does not imply interval-aware dominance from point estimates alone.

## Reference-architecture recommendation engine

### Output and boundary

The engine emits one of:

- `RECOMMENDED_FOR_SHADOW`;
- `NO_CHANGE_RECOMMENDED`;
- `INSUFFICIENT_EVIDENCE`;
- `BLOCKED_BY_SAFETY_GATE`.

The output is a non-executable architecture report, not routing authority. It
may include:

- best supported default architecture;
- best supported architecture by declared risk slice and, when an eligible
  portable-core lane exists, best model by slice under equal controls;
- lane type, attribution status, and allowed claim;
- where each opaque candidate wins or loses;
- fully loaded cost per confirmed high/critical root cause with intervals;
- non-inferiority results for high/critical recall, critical misses,
  hallucinations, precision, root-cause quality, human review, and latency;
- production-baseline and candidate controller, validator, dedupe, posting,
  tool, context, retry, timeout, and routing contract IDs, with explicit
  preserved/changed status;
- required private adapter/eval-harness/validator/human-approval stages;
- an optional bounded “possible contributors; not causal evidence” section;
- a shadow/no-posting pilot and exact evidence still required.

It must state:

> Preserve the production controller, validator, dedupe, and posting
> contracts. A shadow candidate may differ only as explicitly declared; this
> report authorizes no production change and performs no writeback.

It must not invent a new comment budget, suppression rule, escalation rule,
controller, validator, dedupe behavior, or posting behavior. Such behavior may
appear only when supplied by an explicit versioned operator policy and must
still be labeled non-executable.

### Decision policy contract

The versioned decision policy contains named fields for:

- confidence level, bootstrap iterations, and fixed seed;
- minimum paired cases globally and per slice;
- predeclared decision-slice IDs and fixed multiplicity method;
- minimum per-metric and root-cause coverage;
- maximum pricing age and required `FULLY_LOADED` cost basis;
- high/critical root-cause non-inferiority margin;
- critical-miss, hallucination, actionable-precision, root-cause-quality,
  human-review, and latency non-inferiority margins;
- minimum fully loaded cost-per-confirmed-high-critical-root-cause improvement;
- p95/p99 cost, p95/p99 latency, and stability guardrails;
- closed static-diagnostic blocking rule IDs and exact blocking predicate;
- interval-overlap/tie policy;
- closed exception types, approver field, expiry, and non-bypassable gates;
- shadow observation window and rollback thresholds.

Proposed starting shape:

```json
{
  "schemaVersion": 1,
  "policyId": "conservative-root-cause-v1",
  "confidenceLevel": 0.95,
  "bootstrapIterations": 10000,
  "bootstrapSeed": "reviewops-v1",
  "minimumPairedCases": 20,
  "minimumPairedCasesPerSlice": 20,
  "decisionSliceIds": ["auth", "cross-service"],
  "sliceMultiplicityMethod": "HOLM_BONFERRONI",
  "minimumMetricCoverage": 1.0,
  "minimumRootCauseCoverage": 1.0,
  "maxPricingAgeDays": 30,
  "requiredCostBasis": "FULLY_LOADED",
  "highCriticalRootCauseNonInferiorityMargin": 0.0,
  "criticalMissNonInferiorityMargin": 0.0,
  "hallucinationNonInferiorityMargin": 0.0,
  "actionablePrecisionNonInferiorityMargin": 0.0,
  "rootCauseQualityNonInferiorityMargin": 0.0,
  "minimumCostPerConfirmedHighCriticalRootCauseImprovementFraction": 0.3,
  "maximumHumanReviewRegressionFraction": 0.0,
  "maximumP95CostRegressionFraction": 0.0,
  "maximumP99CostRegressionFraction": 0.0,
  "maximumP95LatencyRegressionFraction": 0.0,
  "maximumP99LatencyRegressionFraction": 0.0,
  "minimumFindingStability": 0.8,
  "blockingStaticRuleIds": [],
  "allowedExceptionTypes": ["P95_LATENCY", "P99_COST", "HUMAN_REVIEW"],
  "tiePolicy": "NO_AUTOMATIC_WINNER",
  "shadowObservationDays": 14,
  "rollbackCriticalMisses": 0,
  "exceptions": []
}
```

These are proposed values, not silent runtime defaults. Missing or unapproved
fields produce `INSUFFICIENT_EVIDENCE`.

Each exception record must use one closed `allowedExceptionTypes` value,
include a named human approver, reason, scope, and expiry, and be printed in
the report. Exceptions may relax only the named latency/cost-tail/human-review
guardrail. They never bypass unsafe input, redaction, receipt/provenance,
normalization-cohort, eval-validity, blinding/adjudication, root-cause,
high/critical, critical-miss, fully loaded pricing, unexplained preservation-
contract, no-posting, or closed static-safety-blocker gates.

### Default recommendation gates

`RECOMMENDED_FOR_SHADOW` requires:

1. valid decision policy and safe inputs;
2. complete eval-validity result for the declared lane;
3. complete blinded/randomized/human high-critical adjudication evidence;
4. paired-case, root-cause, and metric coverage thresholds;
5. fresh `FULLY_LOADED` pricing evidence;
6. stable root-cause identity and matching coverage;
7. high/critical root-cause recall satisfies non-inferiority;
8. critical miss rate is not worse under the named margin;
9. hallucination and actionable precision satisfy their margins;
10. root-cause quality satisfies its margin;
11. fully loaded cost per confirmed high/critical root cause improves with
    interval support;
12. human review, p95/p99 latency, p95/p99 cost, and stability guardrails pass;
13. candidate is on the descriptive point-estimate frontier, passes every
    interval-backed pairwise gate, and is not tied under the versioned policy;
14. any emitted per-slice guidance has eligible slice evidence;
15. shadow plan preserves production contracts, labels candidate differences,
    and declares no posting/writeback;
16. no supplied static finding matches the policy's exact closed blocking
    predicate.

No exception may bypass the non-bypassable list above.
Missing optional static diagnostics is recorded as a limitation, not a gate
failure.

### Shadow pilot template

The report may emit a non-executable summary:

```yaml
status: RECOMMENDED_FOR_SHADOW
reference_architecture: candidate-a
production_baseline_contracts:
  controller: controller-v1
  validator: validator-v1
  dedupe: dedupe-v1
  posting: posting-v1
candidate_contract_differences: []
pilot:
  execution_mode: SHADOW_NO_POSTING
  minimum_cases: 20
  observation_window: 14_days
human_approval: required
```

It is documentation, not a file the plugin writes or applies.

## Skill contracts

Every skill includes valid frontmatter, an `agents/openai.yaml` wrapper, and
`policy.allow_implicit_invocation: false`. Prose independently requires
explicit use if host policy semantics change.

### `normalize-review-runs`

Allowed:

- ask for a config path or use the synthetic fixture;
- run only bundled `validate-config` and `normalize`;
- explain accepted/rejected records, provenance, redaction, and bounded
  normalization receipts;
- identify the smallest safe private-export improvement.

Forbidden:

- connecting to a database or provider;
- reading undeclared files or raw private data pasted in chat;
- inferring labels, prices, controls, or root causes;
- writing normalized files.

Stop on unsafe paths, unsupported schemas, ambiguous provenance, or redaction
failure.

### `audit-review-eval-validity`

Allowed:

- run only bundled `validate-config` and `audit-eval`;
- explain lane controls, pairing, blinding, leakage, exclusions, attribution
  status, and claim boundary;
- include optional declared static diagnostics as clearly non-causal context.

Forbidden:

- treating static workflow lint as causal evidence;
- executing workflows, validators, commands, providers, GitHub, or network;
- ranking a comparison whose validity is incomplete;
- silently loading benchmark or diagnostic inputs not declared.

Stop with `INSUFFICIENT_EVIDENCE` or `BLOCKED` when the claim is unsupported.

### `benchmark-review-configs`

Allowed:

- run shared in-memory normalization/eval-validity modules over the declared
  lane bundles, then validate pricing, rubric, labels, and decision policy;
- run only bundled `benchmark`;
- explain global/slice metrics, exclusions, intervals, frontier, and
  uncertainty;
- recommend additional private evidence to collect without asking for it in
  chat.

Forbidden:

- replaying PRs, invoking models, executing validators, or fetching pricing;
- accepting raw tokens, URLs, diffs, comments, logs, or customer records;
- ranking invalid, incomparable, unblinded, or unadjudicated quality evidence.

Stop when validity, pairing, root-cause labels, or required pricing is absent.

### `recommend-review-reference-architecture`

Allowed:

- recompute and combine validated eval and benchmark evidence in memory from
  the declared lane bundles;
- run only bundled `recommend-architecture`;
- emit claim-bounded default/per-slice architecture evidence, preserved
  contracts, gates, limitations, and shadow-only next step.

Forbidden:

- changing workflow, prompt, model, controller, validator, dedupe, routing,
  posting, or GitHub settings;
- posting comments, emitting executable mutation steps, or claiming
  production readiness;
- hiding missingness, contradictions, confounding, or safety warnings.

Stop when a non-bypassable gate is blocked; do not substitute intuition for
evidence.

## Safety-by-design threat model

| Asset / boundary                            | Threat                                                                                      | Mitigation                                                                                     | Required proof                                                                            |
| ------------------------------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Export, prompt, diff, comment, and log text | Prompt injection changes plugin behavior.                                                   | Treat content as inert data; fixed subcommands; no model/tool/shell execution from input.      | Hostile fixtures cannot alter paths, commands, output mode, or result.                    |
| Local filesystem                            | Traversal, symlink, hardlink, or special-file reads leak unrelated files.                   | Canonical containment, declared roots, regular single-link reads, hard ceilings.               | Tests for traversal, absolute paths, links, FIFOs, sockets, home/parent paths.            |
| Secrets/private data                        | Tokens, URLs, emails, paths, identifiers, or excerpts reach output/Git.                     | Redact before reporting; opaque IDs; synthetic fixtures; distribution scan.                    | Canary tests plus full shipped-file and changed-public-doc scan.                          |
| YAML/JSON parser                            | Alias bombs, duplicate keys, custom tags, deep nesting, or huge input causes DoS/ambiguity. | Safe parser options, duplicate rejection, depth/size/time/memory bounds.                       | Malformed/adversarial fixtures fail within limits.                                        |
| Experiment protocol                         | Missing controls or leakage creates a false causal claim.                                   | Strict protocol/lane schema, controlled-field checks, blinding gates, claim boundaries.        | Valid/invalid/missing/contradictory tests for every lane/rule.                            |
| Benchmark corpus                            | Crafted records game metrics or cause execution.                                            | Strict schemas, no dynamic code/command fields, duplicate rejection, provenance/pairing gates. | Fuzz/property and hostile-record tests.                                                   |
| Root-cause labels                           | Candidate findings become their own denominator or duplicate symptoms inflate wins.         | Independent case labels, stable root-cause IDs, rubric matching rules, dedupe.                 | Duplicate/cross-version/unknown/root-cause grouping tests.                                |
| Pricing/cost claims                         | Stale, model-only, or fabricated prices create false savings claims.                        | Dated user-supplied snapshot, cost basis, provenance, unknown states.                          | Missing/stale/mixed-basis tests fail closed.                                              |
| Recommendation                              | Report is mistaken for authority or replaces existing pipeline.                             | Shadow/no-posting wording, preserved contracts, no patches/writeback, human approval.          | Reports contain no executable mutation or production-ready claim.                         |
| Runtime environment                         | Ambient env, parent repo, Git, network, or installed packages affect behavior.              | Env isolation, copied-package tests, no network imports, no ancestor resolution.               | Hermetic tests with hostile env and no repo metadata.                                     |
| Supply chain                                | Bundled dependency/generated artifact is opaque or altered.                                 | Exact lockfile, notices, source/build receipt, hash verification.                              | Rebuild and notice/license checks in CI.                                                  |
| Public repository                           | Private corpus/identifier is committed.                                                     | Synthetic-only fixtures, private-path/secret scan, PR checklist.                               | CI scan covers the plugin and changed public docs and rejects forbidden markers/surfaces. |

Residual risk: imported labels can be biased, private exporters can be wrong,
and static diagnostics can miss runtime behavior. Every report states those
limits and never presents itself as proof of provider superiority or a
complete security audit.

## Redaction, privacy, and accessible rendering

Redaction occurs before stdout, errors, snapshots, or fixture assertions.
Redact:

- token-like values, private keys, auth headers, cookies, secrets, and
  credential values;
- non-public URLs, query strings, hostnames, repository remotes, and webhook
  endpoints;
- emails, usernames, home directories, absolute personal paths, and customer
  identifiers;
- raw prompts, diffs, comments, judge notes, and log payloads beyond safe
  structural summaries.

Prefer relative normalized paths, line ranges, structural digests, counts,
rule IDs, metric IDs, statuses, and short redacted summaries. If safe
summarization is uncertain, replace the whole value with `[REDACTED]` and
increment a count.

Safe rendering is separate from redaction. Strip/escape control characters,
ANSI/OSC, terminal hyperlinks, bidi controls, Markdown fences, link
destinations, HTML, and table delimiters from untrusted input. Markdown and
JSON must carry equivalent statuses, reasons, denominators, intervals, and
limitations. Markdown uses semantic headings/tables/lists, never color-only
meaning, and remains readable in a plain terminal or screen reader.

## Code quality standards

### Module and API discipline

- Keep CLI orchestration thin; put normalization, validity, pairing, metrics,
  slices, stability, gates, paths, and redaction in testable modules.
- Use ESM with checked JSDoc or TypeScript, explicit public contracts, and no
  implicit globals.
- Keep schemas versioned and backward-compatible within a minor release;
  reject unknown major versions.
- Use stable sanitized error codes; no stack traces by default.
- Inject clocks, seeds, filesystem adapters, and limits for deterministic
  tests.
- Stable-sort every list and deterministically serialize canonical JSON.
- No TODO/FIXME, debug logging, dead flags, broad silent catches,
  undocumented environment variables, or unreachable modes.
- Avoid dependencies unless they improve safety/correctness and pass pinned
  provenance/license review.

### Schema discipline

- Every object uses `additionalProperties: false`.
- Every enum is closed/documented.
- Numbers reject `NaN`, infinities, invalid negatives, and unsafe integers.
- Timestamps are RFC 3339 UTC; money has currency, snapshot, and cost basis.
- Digests use one fixed `sha256:<lowercase hex>` format where digests are
  required.
- Unknown/missing data is explicit and never silently changes denominators.
- IDs are opaque; no raw low-entropy private identifier is hashed in-plugin.

### Performance discipline

- Stream JSONL in bounded memory; do not split/load unbounded files.
- Parse each file once and cache only bounded structural summaries.
- Avoid quadratic matching; use bounded maps and stable IDs.
- Bound slices, replicates, findings, and root-cause relationships.
- Provide deterministic worker timeout/cancellation and test hard ceilings.

## Comprehensive implementation audit

Before release, maintain a traceability ledger. Every promise, safety boundary,
input mode, output field, metric, gate, and failure mode maps to:

1. implementation module;
2. schema/rule/metric ID;
3. positive and negative test;
4. README/skill documentation;
5. release command and captured evidence.

Minimum rows:

| Promise                                  | Implementation                   | Tests                                                  | Docs                 | Release evidence         |
| ---------------------------------------- | -------------------------------- | ------------------------------------------------------ | -------------------- | ------------------------ |
| Synthetic credential-free first run      | fixture loader + normalize CLI   | install, packaged, fixture assertions                  | README first prompt  | clean install transcript |
| Sanitized export normalization           | normalize modules/schemas        | malformed, duplicate, partial, provenance              | normalize skill      | contract suite           |
| Fair experiment validity                 | eval/lane/adjudication modules   | each lane, missing controls, blinding, leakage         | eval-validity skill  | validity suite           |
| Preserved pipeline contracts             | lane/provenance checks           | controller/validator/dedupe/posting mismatch           | README boundaries    | validity suite           |
| Imported runs strictly validated         | schema/normalize modules         | unknown field/version/contradiction                    | benchmark skill      | contract suite           |
| Paired comparison enforced               | paired module                    | missing/mismatched cohort/control cases                | benchmark limits     | benchmark suite          |
| Root-cause economics correct             | metrics/slices modules           | symptoms, zero denominator, cost basis                 | metric definitions   | benchmark suite          |
| Risk-slice/stability evidence            | slices/stability modules         | multi-slice, replicate, unsupported slice              | benchmark skill      | benchmark suite          |
| No unsupported recommendation            | gates/architecture modules       | every status/gate/no-writeback                         | recommendation skill | recommendation suite     |
| Static diagnostics non-causal            | static diagnostic/report modules | causal-wording regression                              | README limitations   | diagnostic suite         |
| Bounded regular-file reads               | paths/bounds modules             | traversal/link/special/oversize                        | data boundary        | security suite           |
| Prompt injection inert                   | fixed CLI/inert parser           | hostile fixtures                                       | every skill          | security suite           |
| No network/auth/writeback                | package/runtime surface          | static import, hostile env, installed smoke            | permissions          | packaged/security suite  |
| Public package/docs have no private data | distribution scanner             | canaries/full walk over plugin and changed public docs | release checklist    | validator output         |

## Test strategy

### Test layers

1. **Contract tests**
   - manifest/catalog/README/four-skill inventory agreement;
   - strict schema acceptance/rejection and output revalidation;
   - stable statuses/error codes;
   - no stale three-skill names or unknown manifest/config fields.

2. **Normalization tests**
   - sanitized export to canonical record flow;
   - duplicate/unknown/contradictory IDs, bad versions, partial records,
     missing provenance, stable ordering, and redaction;
   - synthetic adapter-conformance fixture without private adapter code.

3. **Eval-validity tests**
   - valid path for every lane;
   - portable-core prompt/tool/context/controller/validator/dedupe/posting/
     reasoning/retry/timeout/routing mismatch;
   - one-axis versus multi-axis harness ablation;
   - best-system holistic claim boundary;
   - shadow rejection when posting is not disabled;
   - cohort/assignment/order/leakage/exclusion provenance;
   - hidden versus visible identity, randomized versus fixed order, human
     high/critical review, adjudicator independence, disagreement reporting;
   - `SINGLE_FACTOR`, `HOLISTIC_VARIANT`, `CONFOUNDED`, and `UNKNOWN`.

4. **Benchmark tests**
   - normalization, lane-aware pairing, dedupe, metrics, intervals, frontier,
     deterministic outputs;
   - root-cause grouping across symptoms, zero confirmed denominator,
     critical misses, actionable precision, hallucination, root-cause quality;
   - `MODEL_ONLY` versus `FULLY_LOADED` cost, human review minutes,
     p50/p95/p99 cost/latency;
   - multi-slice denominators, bounded decision slices, multiplicity
     adjustment, unsupported slices, case-level replicate aggregation, and
     stability;
   - missing labels, stale pricing, unequal cohorts, contradictions, ties,
     dominated candidates, and descriptive-only evidence.

5. **Recommendation tests**
   - every recommendation status and new gate;
   - global and per-slice architecture output;
   - preserved controller/validator/dedupe/posting contracts;
   - cross-lane architecture identity, baseline-contract, cohort, and pricing
     compatibility;
   - no hardcoded replacement behavior, no executable mutation, no writeback;
   - missing static diagnostics does not block; only the exact closed
     static-blocking predicate may block; static findings never become causal
     claims.

6. **Static diagnostic tests**
   - optional safe/risky/ambiguous workflow/prompt/telemetry fixtures;
   - evidence classification, line attribution, redaction;
   - possible-contributor labels and bounded non-causal wording.

7. **Security tests**
   - prompt injection in every input type;
   - traversal, absolute path, symlink, hardlink, special file, hidden parent;
   - secret/URL/email/path/customer-like canaries;
   - YAML bombs, deep JSON, newline-dense JSONL, huge lines/records, duplicate
     keys, malformed UTF-8;
   - worker timeout/memory/stdout caps;
   - static scan for network, subprocess, dynamic code, environment leakage.

8. **Accessibility/output tests**
   - JSON/Markdown parity for statuses, gates, intervals, reasons, and
     limitations, lane type, attribution status, held/changed dimensions,
     preservation contracts, per-slice eligibility/exclusions, and non-causal
     contributor labels;
   - headings, tables, lists, plain-language labels, no color-only meaning;
   - plain-language summaries for decision-critical fields so users do not
     need to decode a wide table;
   - hostile Markdown/terminal content cannot create fake headings, links,
     fences, tables, ANSI/OSC, or bidi confusion.

9. **Packaged/isolation tests**
   - copy only installable plugin to a fresh temp directory;
   - run all documented commands with no `node_modules`, Git, network, home,
     parent repo, or ambient locale dependency;
   - reject symlinks and unlisted distribution files.

10. **Cold-install test**
    - add local marketplace, install in clean Codex home, and run documented
      synthetic normalization/eval/benchmark/recommendation paths;
    - prove no auth prompt, credential request, network call, or write;
    - verify installed package, not development source.

### Required scripts and release commands

Keep or add plugin-scoped scripts:

```json
{
  "scripts": {
    "validate:reviewops-auditor-benchmark": "node scripts/validate-reviewops-auditor-benchmark.mjs",
    "build:reviewops-auditor-benchmark": "npm --prefix plugins/reviewops-auditor-benchmark run build",
    "typecheck:reviewops-auditor-benchmark": "npm --prefix plugins/reviewops-auditor-benchmark run typecheck",
    "lint:reviewops-auditor-benchmark": "npm --prefix plugins/reviewops-auditor-benchmark run lint",
    "format:check:reviewops-auditor-benchmark": "npm --prefix plugins/reviewops-auditor-benchmark run format:check",
    "coverage:reviewops-auditor-benchmark": "npm --prefix plugins/reviewops-auditor-benchmark run coverage",
    "verify:reviewops-source": "node scripts/verify-reviewops-source.mjs",
    "test:reviewops-auditor-benchmark": "npm run build:reviewops-auditor-benchmark && npm run validate:reviewops-auditor-benchmark && npm run typecheck:reviewops-auditor-benchmark && npm run lint:reviewops-auditor-benchmark && npm run format:check:reviewops-auditor-benchmark && npm --prefix plugins/reviewops-auditor-benchmark run test && npm run coverage:reviewops-auditor-benchmark"
  }
}
```

Required local release commands:

```sh
npm run validate:marketplace
npm run validate:reviewops-auditor-benchmark
npm run build:reviewops-auditor-benchmark
npm run typecheck:reviewops-auditor-benchmark
npm run lint:reviewops-auditor-benchmark
npm run format:check:reviewops-auditor-benchmark
npm run coverage:reviewops-auditor-benchmark
npm run verify:reviewops-source
npm run test:reviewops-auditor-benchmark
npm run test:marketplace
npm run validate
git diff --check
```

Also run `node --check` on every shipped `.mjs` entrypoint,
`npm ci --ignore-scripts`, and `npm audit --omit=dev` when dependencies or
bundles change.

Coverage remains an aggregate 90% line / 80% branch / 90% function source
gate, but every lane, metric, recommendation gate, and safety boundary needs
an explicit negative test; coverage alone is not sufficient.

The full 106-test suite runs uninstrumented on every supported Node version.
Node 22.19 also runs coverage on the 78 deterministic unit suites so
instrumentation cannot distort the public CLI worker's fixed five-second
safety deadline; copied-package, accessibility, security, and CLI subprocess
tests still run uninstrumented as required end-to-end gates.

### Dedicated CI

The dedicated workflow must include:

- PR/push path filters for plugin, tests, validator, workflow, marketplace,
  package scripts, and plan/docs;
- `permissions: contents: read`, `persist-credentials: false`, pinned
  actions, concurrency cancellation;
- one visible ReviewOps E2E check instead of separate matrix, source, and
  copied-package checks;
- Node 22.19 full qualification, coverage, dependency audit, source
  verification, and pre-install copied-package smoke steps;
- Node 24 and 26 uninstrumented full-suite compatibility steps in the same
  E2E job;
- a 15-minute bounded job timeout;
- no live provider, database, GitHub, customer-data, or runtime-network test;
- explicit skipped-gate ledger when a platform check is unavailable.

A skip is never counted as a pass. Real installed-client/no-auth verification
remains a manual release gate if it cannot run hermetically in CI; any auth
prompt blocks release.

## Implementation phases

### Phase 0 — freeze operator-aligned boundary and decision contract

Deliverables:

- confirm four-skill inventory and CLI names;
- freeze lane types, claim boundaries, preservation-contract fields, eval and
  adjudication protocol fields;
- freeze root-cause identity, risk-slice, replicate, fully loaded cost, and
  decision-policy definitions;
- write/update ADR for “offline imported runs; private adapter/live runner”;
- approve public/private data classification and threat-model delta;
- verify marketplace auth policy remains credential-free for fixture use.

Exit criteria:

- no open question changes capabilities, auth, network, persistence, or
  private-data boundary;
- operator-facing primary metrics/gates and non-causal static-diagnostic boundary
  are agreed;
- private adapter conformance schema/fixture is approved;
- human reviewer signs off on the revised methodology and threat model.

### Phase 1 — update package surface, schemas, and synthetic fixtures

Deliverables:

- four skills, manifest prompts, README skeleton, CLI help, validator rules;
- new/renamed schemas and eval-validity rules;
- synthetic export, lane, protocol, adjudication, root-cause, slice,
  replicate, and fully loaded pricing fixtures;
- package/marketplace/root docs wired to the revised surface.

Exit criteria:

- validator rejects stale three-skill inventory and schema drift;
- marketplace validation passes;
- clean install discovers four explicit skills;
- no MCP/app/network/write capability exists.

### Phase 2 — implement explicit normalization

Deliverables:

- sanitized export schema and canonical normalization path;
- normalization report and stable partial/blocked outcomes;
- duplicate/provenance/redaction/receipt handling;
- synthetic adapter-conformance documentation and tests.

Exit criteria:

- safe valid exports normalize deterministically;
- malformed, private, duplicate, contradictory, and unsupported records fail
  closed;
- normalizer never connects to a database, writes output, or infers evidence.

### Phase 3 — implement eval validity and secondary static diagnostics

Deliverables:

- lane-aware validity engine, attribution statuses, reason codes, and report;
- pairing/control/preservation/blinding/leakage/exclusion/adjudication checks;
- optional static diagnostic integration with non-causal wording and relevant
  versioned closed-predicate blocking only.

Exit criteria:

- each lane's valid/invalid/missing/contradictory cases are tested;
- no invalid comparison can reach quality ranking;
- static diagnostics cannot substitute for validity or dominate the report.

### Phase 4 — extend benchmark scorer

Deliverables:

- lane-aware pairing and exclusions;
- root-cause grouping, critical misses, precision, hallucination, quality,
  fully loaded economics, human review, p99, slices, and stability;
- seeded paired intervals, frontier, deterministic synthetic expectations.

Exit criteria:

- repeated runs are byte-identical across supported Node versions;
- zero denominators, stale/mixed pricing, missing labels, bad slices,
  unpaired replicates, and ties are qualified or blocked;
- no quality winner is emitted without eligible validity/adjudication/root-
  cause evidence.

### Phase 5 — implement reference-architecture recommendation

Deliverables:

- recommendation statuses/gates and architecture report;
- default and per-slice evidence, preserved contracts, claim boundaries,
  non-inferiority, limitations, and non-executable shadow plan;
- optional bounded possible-contributors section.

Exit criteria:

- every gate has a test;
- no recommendation bypasses validity, blinding, root-cause, critical-miss,
  pricing, or no-posting gates;
- output contains no replacement controller behavior, executable mutation, or
  writeback instruction.

### Phase 6 — documentation, accessibility, and reviewer hardening

Deliverables:

- README install, four safe prompts, real-input flow, permissions, auth, data
  boundary, failures, metrics, claim boundaries, verification, limitations;
- complete skill safety contracts, stop conditions, and completion formats;
- accessible Markdown/JSON parity tests and docs;
- root README and PR evidence template updates.

Exit criteria:

- a cold-start user can understand what the plugin reads, measures, never
  does, and how to verify it without private data;
- every documented command/example is exercised;
- reviewer can identify capabilities, auth, file/network/write boundaries,
  private/public split, and methodological limits without reading source.

### Phase 7 — comprehensive qualification and clean PR

Deliverables:

- updated traceability ledger;
- full local command transcripts and CI evidence;
- clean-checkout/cold-install smoke evidence;
- dependency/license/notice/source-bundle review;
- independent security, methodology, code-quality, completeness, reliability,
  accessibility, and fixture reviews;
- clean branch/commit/PR description with known-limitations ledger.

Exit criteria:

- all required local and CI gates pass;
- no private data, secrets, personal paths, or customer identifiers remain;
- no unresolved high-severity safety, correctness, reliability, accessibility,
  or methodology finding remains;
- PR diff is minimal, reviewable, and contains no generated noise or dead
  compatibility surface.

### Phase 8 — private operator shadow pilot, outside public package

Deliverables:

- private exporter from existing review/eval data into the public contract;
- representative paired corpus and declared four benchmark lanes;
- blinded/randomized adjudication with human high/critical review;
- current fully loaded pricing and human-review effort;
- no-posting shadow comparison and operator feedback.

Success gates:

- high/critical root-cause recall preserved or improved;
- critical miss rate not worse;
- hallucination rate not increased and actionable precision/root-cause quality
  preserved or improved;
- fully loaded cost per confirmed high/critical root cause decreases with
  interval support;
- human review burden, p95/p99 cost, and p95/p99 latency satisfy guardrails;
- evidence identifies where each architecture wins by risk slice;
- evaluation owner agrees the recommendation is fair, bounded, and actionable.

Private results may inform generic schemas/rules, but no private artifact may
enter the public repository.

## Release checklist

Before requesting review:

- [ ] Package name, manifest, marketplace entry, README, CLI, and four skills
      agree.
- [ ] Only synthetic fixtures are present.
- [ ] Manifest capabilities are `Read` only; no MCP/app/auth/network/write
      surface.
- [ ] README says no database access, live replay, provider call, GitHub
      writeback, production mutation, or secrets in chat.
- [ ] Normalization, eval-validity, benchmark, recommendation, static
      diagnostic, accessibility, security, package, and install tests pass.
- [ ] Strict schemas cover lane, protocol, adjudication, preservation,
      root-cause, slice, replicate, and fully loaded cost contracts.
- [ ] Runtime dependencies are pinned, bundled, licensed, and reproducible.
- [ ] Distribution scan rejects links, non-regular files, private/token
      patterns, personal paths, forbidden runtime surfaces, and stale private
      examples.
- [ ] Every skill has explicit invocation, forbidden actions, stop conditions,
      and completion format.
- [ ] Every lane/rule/metric/gate has valid, boundary, invalid, and missing-
      evidence coverage.
- [ ] Markdown and JSON are accessible, semantically equivalent, and safely
      escaped.
- [ ] Clean isolated install and all synthetic CLI paths are verified with no
      auth/network/write.
- [ ] Commands, versions, pass/fail counts, skips, limitations, and security
      evidence are recorded.

Before release:

- [ ] PR opened from a clean branch, required CI green, review feedback
      resolved, and exact package diff approved.

## Resolved release decisions

1. Keep the slug/display name; make “Auditor” mean evaluation-validity audit,
   with static workflow audit demoted to optional diagnostics.
2. Public v0.1.0 targets four explicit skills and five CLI commands including
   `validate-config`.
3. Public v0.1.0 normalizes/scores imported sanitized exports only; database
   adapters, live replay, provider calls, GitHub integration, and writeback
   remain private/out of scope.
4. The primary economic objective is fully loaded cost per confirmed
   high/critical root cause, guarded by high/critical recall, critical
   misses, hallucination, actionable precision, root-cause quality, human
   review, latency, cost-tail, and stability evidence.
5. Model-only, one-factor ablation, holistic system, and shadow lanes have
   distinct claim boundaries; no holistic result is presented as model
   causality.
6. Quality recommendation requires versioned root-cause labels, blinded
   randomized adjudication, human high/critical review, disagreement
   reporting, and valid evaluation protocol evidence.
7. The recommendation preserves existing controller, validator, dedupe, and
   posting contracts and emits no executable production change.
8. Missing optional static diagnostics is a limitation, not a benchmark gate;
   supplied findings may block only through the versioned closed predicate.
9. Contained roots, bundled pinned dependencies, reproducible source/bundle
   verification, and synthetic-only public data remain mandatory.
10. Release approval requires security, methodology, dependency/license,
    accessibility, code-quality, completeness, and reliability evidence.

## Definition of done

The plugin is ready only when a new user can install it from a clean checkout,
run the synthetic fixture without credentials or network, discover and use all
four explicit skills, safely normalize declared sanitized exports, determine
whether a comparison is valid for its lane, obtain deterministic global and
per-slice root-cause economics, and receive either a conservative shadow-only
reference architecture or an honest insufficient-evidence result.

It is not done because the old three-skill happy path still passes. It is done
when malformed, hostile, private, ambiguous, stale, incomplete, unblinded,
confounded, oversized, and incomparable inputs fail safely; every public claim
has a schema, test, and documentation anchor; the installed package is
self-contained and reproducible; and the release diff contains no private data
or hidden authority.
