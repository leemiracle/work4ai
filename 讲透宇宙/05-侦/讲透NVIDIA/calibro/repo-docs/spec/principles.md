# Calibro Design Principles

## 1. Collect Everything, Filter at Query Time

Calibro defines the **maximal set** of data that should be captured. Implementations may not be able to collect everything (e.g., GPU telemetry APIs unavailable on some clusters), but Calibro defines what "complete" looks like. What constitutes "the same configuration" for comparison purposes is a query-time decision, not a collection-time decision.

## 2. Non-Invasive Collection

Data collection must not interfere with the workload under test. Calibro assumes that data is gathered through external observation (image inspection, system interfaces, scheduler APIs, sidecar processes) rather than by modifying or instrumenting the benchmark container itself.

**Why this matters:** Some existing approaches run collector agents inside the test container to capture Python dependencies. While this gives perfect fidelity, it modifies the environment being tested — installed packages, running processes, memory usage. For benchmarking, where measurement must not affect results, this is unacceptable.

**Overhead budget:** Telemetry collection overhead must be measurable and must not exceed 1–3% of workload performance. Any collection method that introduces more than marginal overhead is not Calibro-compliant, regardless of how useful the data it captures may be.

## 3. Data Lifecycle Model

Data becomes available at different points in the benchmark lifecycle. Calibro organizes fields into six temporal phases:

| Phase | Name | When | What |
|---|---|---|---|
| 1 | Pre-Run | Before the workload starts | Image-level facts: SBOM, baked environment variables, image digest |
| 2 | Scheduling | At workload scheduling | Resource allocations, node assignment, user-declared metadata |
| 3 | Microbenchmark | After node assignment, before workload | Measured hardware performance: GPU bandwidth, collective throughput, storage I/O, CPU compute |
| 4 | Environment Snapshot | Once at workload start | Static hardware/software capture: GPU, CPU, memory, network, drivers, runtime env vars |
| 5 | Runtime Collection | Continuously during the workload | Time-series hardware telemetry + optional application metrics endpoint scraping |
| 6 | Results Harvest | After the workload exits | Benchmark output (metrics, logs, artifacts), execution status |

This phasing is part of Calibro (it defines *when* each field becomes available) but the implementation of each phase is not (that's up to the collecting tool/platform).

## 4. Domain Extensible

The specification is organized into a **shared core** (fields relevant to all benchmark types) and **domain overlays** (fields specific to a workload type). Each `CalibroResult` declares exactly one primary domain overlay through a protobuf `oneof`; unused overlays are omitted, not emitted as null or empty objects. New domains inherit all core fields and add a typed overlay as a new `domain_overlay` member. The first domain is LLM & multi-modal inference serving; future domains will cover training, fine-tuning, and other workload types.

Calibro defines the structure and required fields for benchmark results — not where or how they are stored. Implementations may write results to a directory, expose them via an HTTP endpoint, stream them to a database, or any combination. The standard is concerned with **what data is present and in what shape**, not the transport or storage mechanism.

**Multi-component workloads** (e.g., inference server + client + router) use a nested hierarchy of per-component objects. Each component carries its own environment data, telemetry, and failure context under its `component_id`. Flattened structures with dynamic key prefixes (e.g., `server_gpu_model`, `client_gpu_model`) are not Calibro-compliant — use nested objects instead.

## 5. Immutable References

Container image references in Calibro must be **immutable digests** (sha256:...), not mutable tags (:latest, :v1.2). Tags can point to different images over time; digests guarantee that two results referencing the same digest ran on identical container contents.

## 6. Sensitive Data Redaction

Environment variables may contain secrets. Calibro requires that implementations apply a configurable redaction pattern before storing environment data. Common patterns: `*SECRET*`, `*TOKEN*`, `*PASSWORD*`, `*KEY*`, `*CREDENTIAL*`.

## 7. Tiered Compliance Model

Calibro defines a **base standard** that applies to all execution environments plus **scoped environment context** that is required when a specific scheduler or platform is declared. This ensures the standard is universal without forcing cluster-only fields on local/manual, bare-metal CI, or other direct host runs.

| Tier | Applies when | What it adds |
|---|---|---|
| **Base** | Always | Core hardware (GPU, CPU, memory, network), drivers, optional containers, SBOM, provenance, execution context, telemetry, performance metrics, failure context |
| **Kubernetes** | `execution_context.scheduler_type` = kubernetes | Execution-level cluster context, node-level Kubernetes version/CNI/runtime facts, and component-instance pod/container placement including requests and limits |
| **Slurm** | `execution_context.scheduler_type` = slurm | Execution-level allocation context, node-level Slurm facts, and component-instance step/task/rank placement including bindings and visible devices |

**Tier detection is based on `execution_context.scheduler_type`**. This field is required and must be set explicitly by the collector; use `none` for local/manual runs without a scheduler. If `scheduler_type` = `kubernetes`, `ExecutionContext.kubernetes` is required and Kubernetes node/instance context is expected where nodes and component instances are scheduler-managed. If `scheduler_type` = `slurm`, `ExecutionContext.slurm` is required and Slurm node/instance context is expected where nodes and component instances are scheduler-managed. An implementer cannot skip scheduler context by claiming they did not "detect" the environment — scheduler use is a mandatory declaration, and absence of a scheduler is declared as `none`.

**Compliance is checked per tier.** A result from Kubernetes that passes base validation but is missing CNI information is "Calibro Base compliant" but not "Calibro+Kubernetes compliant." The scheduler context is not optional — if you're running on Kubernetes or Slurm, the matching scoped context is required.

Environment context is additive — it never overrides or contradicts base fields. It provides scheduler-specific context that makes the base data interpretable in that environment.

## 8. Schema Extensibility — Two-Tier Rule

Calibro is a normative standard, not a flexible data container. The value of Calibro comes from every consumer knowing exactly what every field means, how it's typed, and where it lives. Generic key-value buckets on stable schema layers would create a shadow schema that undermines comparability.

However, not all layers evolve at the same rate. The extensibility rule reflects this:

**Infrastructure and environment layers** (GPU, CPU, Memory, Network, Storage, OS, Drivers, Kubernetes, Slurm, Provenance, Scheduling) are **fully enumerated**. Every field must be defined in the spec with a canonical name, type, unit, and description. Teams propose new fields through the fast promotion process (Principle 9). No generic buckets.

**Domain-specific layers** (model configuration, inference parameters, benchmark metrics, domain overlays) may use **typed generic buckets** where the key space is driven by rapidly evolving external systems — new inference engines, quantization methods, model architectures, and serving configurations that change faster than any spec process can track.

**The test for whether a bucket is justified:** "Would refusing a bucket here force schema updates multiple times per week just to keep up with external ecosystem changes?" If yes, a typed bucket is appropriate. If no, enumerate the fields.

Existing fields that already follow this pattern: `inference_engine_config` (engine flags vary per engine version), `metric_metadata` (benchmark-specific context varies by tool), `microbench_test_params` (test parameters vary by test tool). These existing fields use `map<string, string>` and are grandfathered — they predate the typed bucket structure below. New domain-layer buckets must use the typed structure. Existing fields may be migrated to the typed structure when the protobuf schema is formalized.

### Typed Bucket Structure

Where generic buckets are permitted, each entry must carry enough metadata for consumers to interpret it without tribal knowledge:

| Attribute | Required | Description |
|---|---|---|
| `key` | Yes | Field name, must match `^[a-z][a-z0-9_]*$`. Soft naming conventions for common patterns (e.g., `*_p50`, `*_p99` for percentiles). |
| `value` | Yes | String-encoded value |
| `type` | Yes | Value type: `int`, `float`, `string`, `bool` |
| `unit` | No | Unit of measurement (e.g., `MiB`, `MHz`, `tokens/s`) |
| `description` | Yes | Human-readable purpose of this field |

### Naming Conventions

All bucket keys and proposed spec fields must follow these conventions:

- **Enforced:** Keys must match `^[a-z][a-z0-9_]*$` (lowercase snake_case, no leading digits). Rejected at schema validation if violated.
- **Soft conventions** (recommended, not enforced at validation):
  - Percentile suffixes: `*_p50`, `*_p90`, `*_p99`, `*_p999` (pattern: `*_p<NN>` or `*_p<NNN>`)
  - Team-prefixed keys in staging buckets: `team_*` (e.g., `team_kv_block_size`) to avoid collisions
  - Boolean fields: prefix with `is_` or `has_` where it improves clarity
  - Rate/throughput fields: suffix with `_per_s`, `_per_min`, etc.

These conventions apply to both domain-layer typed buckets and the backup staging bucket mechanism (Principle 9).

Bucket entries are **not** substitutes for spec fields. If a key appears consistently across teams, it should be promoted to a named field through the promotion process. Buckets are for genuinely dynamic, externally-driven key spaces — not for avoiding the spec process.

## 9. Promotion Process

> **Implementation status:** This principle describes the intended steady-state process. Automated intake tooling is planned. Until then, field proposals follow the standard pull request process with the same quality expectations described here.

The "no buckets on infrastructure layers" policy (Principle 8) depends entirely on field additions being fast. If the spec process takes weeks, teams will either bypass Calibro or log data outside it — both outcomes are worse than a generic bucket. This principle defines the process that makes the strict policy viable.

### Zero-Knowledge Entry Point

A team member should not need to know about the Calibro repository, protobuf files, or pull request conventions to propose a new field. Multiple intake channels lead to the same automated pipeline:

- **IDE and agent integrations** — slash commands (e.g., `/calibro add-field`) or natural-language descriptions of the need
- **Web chat widget** — lightweight component embeddable in documentation sites or wikis
- **Chat platform integrations** — for teams that work primarily in team chat tools

All channels connect to the same AI-powered intake backend.

### Adversarial Intake Agent

The intake agent is a **gatekeeper, not a helper**. Its mandate is to protect the standard by ensuring only well-formed, justified proposals reach a human reviewer. The agent:

- **Challenges necessity** — "What problem are you solving that existing fields can't cover?" If the need maps to an existing field, it redirects.
- **Challenges placement** — Proposes where the field belongs in the model hierarchy, requires a concrete argument to override.
- **Challenges type and semantics** — Pushes back on `string` for clearly numeric values, free-text where an enum would enforce comparability.
- **Challenges naming** — Enforces conventions strictly, rejects ambiguous or semantically overlapping names.
- **Refuses to create the pull request** until the proposal meets all quality gates. The conversational loop continues until the agent is satisfied — or the agent explicitly explains why the field does not belong in Calibro.

The goal: the pull request auto-created by the intake agent is indistinguishable from one written by a spec maintainer. The validation gate is a formality, not a filter.

### Automated Validation Gate

On pull request creation, an automated check runs as a safety net:

- Validates naming conventions against schema patterns
- Checks for duplicate or overlapping fields
- Verifies placement on the correct model
- Validates type/unit consistency
- Checks justification references one of the three pillars (reproducibility, comparability, diagnostics)
- Produces **PASS** (auto-notifies maintainer) or **NEEDS CHANGES** (feeds back to proposer)

NEEDS CHANGES from the validation gate should be a rare event — if it happens frequently, the intake agent's logic needs improvement.

### Single Human Handover

The maintainer is the only human in the loop. They see a clean, validated pull request and make a judgment call on intent: *"Should this field exist?"* — not whether it's well-formed (the automation already verified that).


### Backup Plan: Typed Staging Buckets

If the fast promotion process breaks down, a pre-designed backup mechanism — typed staging buckets — exists to prevent teams from logging data outside Calibro. This backup is currently **inactive**; it is enabled only when field promotion latency exceeds agreed thresholds and documented guardrails are met.

## 10. Versioning

The Calibro data standard is versioned with semantic versioning (`MAJOR.MINOR.PATCH`), applied to the **spec**, not the SDK. Spec and SDK have independent version streams — the SDK can be re-published for tooling fixes without a spec change, and spec evolution does not force an SDK release.

**MAJOR** bumps on changes that break conforming producers or consumers after the standard graduates to `1.0`: field removal, rename, type change, unit change, semantic redefinition, enum value removal, optional → required transition, or changes to compliance-tier contracts.

While Calibro remains in the pre-stable `0.x` line, a documented breaking schema change may ship as a MINOR bump when release documentation records the pre-1.0 exception, a migration note explains producer actions, and CI confirms the version moves forward at the published release boundary. An unpublished pre-1.0 minor may be refined before its release marker is cut; once a matching `spec-vX.Y` tag or release note exists, further proto/spec changes require the next version. This exception is deliberately narrow: it exists to let the machine contract catch up with reviewed design before `1.0`, not to weaken the post-1.0 compatibility rule.

**MINOR** bumps on additive changes: new optional field, new message, new enum value (appended), new domain overlay or environment context, required → optional relaxation, new typed-bucket entries.

**PATCH** bumps on changes that do not alter on-the-wire data shape: spec prose edits, collection-recommendation updates, justification edits, alias registry changes (aliases are informational and do not affect schema validation), `.proto` comment changes that do not alter generated code, and repository tooling changes.

**`calibro_version` field semantics.** Producers populate `calibro_version` with the spec MAJOR.MINOR they conform to (e.g., `"0.1"`, `"1.3"`). PATCH is excluded because patch changes do not alter data shape. Consumers compare `(major, minor)` tuples for compatibility — a consumer on `1.3` accepts data with matching major and any minor ≤ theirs; `2.0` must be explicitly opted into. The field must not carry the SDK version.

**Current spec version: 0.1** — pre-stable. Consumers should not hard-pin; minor-version churn is expected until the standard graduates to `1.0` (gated on closing the remaining open questions around adoption, mixed precision, GPU-hour accounting, and enum hardening).

Spec documents may describe design targets that require follow-up protobuf, JSON Schema, SDK, or validator changes. A producer should claim conformance to a new version only for the machine-enforced contract available in the generated schema and validators it uses. Design-only sections must explicitly say when producer conformance begins later than the version stamp.

Version bumps should be reflected in `spec/VERSION`, release notes, and git tags at the published release boundary.
