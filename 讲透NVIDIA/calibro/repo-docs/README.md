# Calibro

> This project is currently not accepting contributions.

**A unified data standard for benchmark and experiment data collection.**

Calibro is a comprehensive, platform-agnostic specification that defines what data should be captured when running a benchmark — field names, types, units, semantics, justifications, and collection methods. Any tool or platform that implements the Calibro standard produces results that are comparable, reproducible, and diagnostically complete — regardless of which team ran the benchmark or which infrastructure they used.

Raw benchmark data goes in messy and unstructured; Calibro indexes it into clean, well-defined categories.

## The Problem

Multiple teams and organizations run deep learning benchmarks and experiments. Each collects different data, in different formats, at different levels of completeness. There is no shared definition of "what a complete benchmark result looks like."

This creates real consequences:

- **Results are incomparable.** Team A reports throughput in tokens/s with no GPU model recorded. Team B reports throughput in requests/s on a different cluster. Neither result can be meaningfully compared because the environment context is missing or incompatible.
- **Failures are unexplainable.** A benchmark run fails or produces anomalous numbers — but without GPU telemetry, driver versions, or memory pressure data, root cause analysis is guesswork.
- **Results are irreproducible.** A container image tag points to a different build today than it did yesterday. Without immutable digests, SBOMs, and environment snapshots, "reproduce this result" is aspirational.
- **Every team reinvents collection.** Each benchmarking tool decides independently which data to capture, how to name it, and in what format — duplicating effort and ensuring that cross-tool analysis requires custom translation layers.

## The Vision

A single, authoritative specification that defines the complete picture of a benchmark result. Every field justified — why it matters for comparability, reproducibility, or diagnostics. Every field grounded — how to collect it at the lowest level, across heterogeneous hardware and software environments.

When Calibro is adopted:

- A benchmark result from any team, any tool, any cluster is **structurally identical** — same field names, same types, same units
- Any two results can be compared by querying shared fields without translation
- Failures come with the telemetry and context needed for root cause analysis
- Results are tied to immutable artifacts (image digests, SBOMs, git commits) — reproducibility by construction

## What Calibro Is

Calibro is a **data specification** — a normative data dictionary with machine-validatable schemas. For every field it defines:

1. **Name, type, and semantics** — the canonical field name, data type, unit, and whether it's required or optional
2. **Justification** — why this field needs to be collected (comparability? reproducibility? diagnostics? auditability?)
3. **Collection method** — the lowest-level command, file, or API call to obtain the value (e.g., GPU management queries for device model, vendor telemetry APIs for GPU utilization)

The specification is organized into a **shared core** (fields relevant to all benchmark types — GPU, CPU, memory, network, OS, drivers, containers, provenance) and **domain overlays** (fields specific to a workload type).

## What Calibro Is Not

Calibro does not specify:

- **How to collect** — that's implementation (tools and platforms reference Calibro as their data contract; collection methods in the spec are copy-paste ready recommendations, not requirements)
- **Where to store** — that's infrastructure
- **How to query or compare** — that's application logic

This repository publishes documentation for the Calibro specification. It intentionally excludes collector source code, SDKs, generated schemas, documentation-site applications, and deployment assets. External tools can use the documented standard as their data contract.

## Design Principles

- **Collect everything, filter at query time.** Calibro defines the maximal set; relevance is a query-time decision.
- **Non-invasive collection.** External observation only; collection overhead must not exceed 1–3%.
- **Data lifecycle model.** Six phases define when each field becomes available.
- **Immutable references.** Container images by sha256 digest, never mutable tags.
- **Domain extensible.** Shared core + domain-specific overlays.
- **Tiered compliance.** Base standard + required extensions for Kubernetes and Slurm.
- **Sensitive data redaction.** Environment variables redacted before storage.

See [spec/principles.md](spec/principles.md) for full definitions and rationale.
