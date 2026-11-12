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

# Dataset references and cleanup in prepared filesystem batches

## Summary and user workflow

Status: proposed, not implemented. It extends
[prepared filesystem batches](../FILESYSTEM_TESTING.md#prepared-filesystem-batches)
and predates v2.0.0, so its Kubernetes details assume one claim per attempt;
revalidate them against per-claim Leases and namespace segments
([lifecycle](../KUBERNETES_ELBENCHO_LIFECYCLE.md)) before implementing.
This plan adds ordered reuse and deletion of datasets
produced earlier in the same batch; it does not add live append or a general
dependency scheduler.

The intended workflow is: write and retain a dataset, read it with several
configurations, then delete it. All groups are assembled before the batch starts.
Users need neither execute the writer first nor copy generated paths from logs.
Target names are already determined during reification; readiness is determined
at execution time.

Use an optional group label to avoid bookkeeping with execution numbers:

```bash
# Set env.sh for the desired write-only dataset(s).
./storage-tests/fs/nv-elbencho-sweep.sh \
    --batch --label seed --write-only --nodes 1

# Set batch to the results directory printed by the command above.
batch=/path/to/filesystem-batch-DATESTAMP

# Change read parameters in env.sh, then prepare readers.
./storage-tests/fs/nv-elbencho-sweep.sh \
    --append "$batch" --label read-small \
    --read-from-group seed --nodes 1,2

# Edit env.sh again for the next read sweep.
./storage-tests/fs/nv-elbencho-sweep.sh \
    --append "$batch" --label read-large \
    --read-from-group seed --nodes 1,2

# Cleanup requires no --nodes or benchmark sweep coordinates.
./storage-tests/fs/nv-elbencho-sweep.sh \
    --append "$batch" --label cleanup --delete-from-group seed

# Either entry point can inspect or execute the mixed batch.
./storage-tests/fs/nv-mdtest-elbencho.sh --list-groups "$batch"
./storage-tests/fs/nv-mdtest-elbencho.sh --start "$batch"
```

A write-only invocation still expands its configured sweep dimensions. Setting
one value in every dimension produces one dataset; a larger writer group produces
one dataset per write execution. `--read-from-group seed` explicitly applies the
entire requested read sweep to every dataset in that group. The preparation
summary prints the expansion and total cell count before execution.

For selective reuse, list the group and choose an execution:

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --list-groups "$batch" --json
./storage-tests/fs/nv-elbencho-sweep.sh \
    --append "$batch" --read-from-execution 0007 --nodes 1,2
./storage-tests/fs/nv-elbencho-sweep.sh \
    --append "$batch" --delete-from-execution 0007
```

Readers consume immutable datasets. Their normal read-target semantics must not
delete the source. Cleanup is an explicit final execution, and successful earlier
benchmark results remain available after the dataset is removed.

## CLI, identifiers, and ergonomic rules

### Names and reference selectors

Keep the prerequisite's distinction between a batch results tree, a sweep group
created by one invocation, and a globally numbered execution within that tree.

| Flag | Semantics |
|---|---|
| `--label NAME` | Optional immutable name for the newly created/appended group; valid on either launcher with `--batch` or `--append`. |
| `--read-from-group GROUP` | Append an IO read sweep for every retained dataset in the named or numbered earlier writer group. |
| `--read-from-execution ID` | Append an IO read sweep for the one retained dataset owned by the earlier execution ID. |
| `--delete-from-group GROUP` | Append one cleanup execution per retained dataset in the earlier writer group. |
| `--delete-from-execution ID` | Append one cleanup execution for the earlier execution's retained dataset. |
| `--list-groups RESULTS_DIR` | Inspect committed groups, labels, executions, dataset declarations, references, and locally known outcomes. |
| `--json` | With `--list-groups` only, emit structured JSON instead of the human table. |

Group IDs and execution IDs are separate namespaces, both retaining the
prerequisite's four-digit format. Reference flags determine the namespace. Group
selectors accept either the exact group ID or its label; execution selectors
accept an exact execution ID. No implicit "latest", index offset, filename
parsing, or arbitrary shell expression is accepted.

Labels are case-sensitive, batch-local, unique, and immutable. Accept
`[A-Za-z][A-Za-z0-9_-]{0,63}`; this excludes numeric IDs, path syntax, whitespace,
and reserved punctuation. Duplicate or invalid labels fail without committing a
group. Unlabelled groups remain usable through IDs. Labels are metadata, not
directory names, so adding this feature does not change the physical layout.

Named groups are the default ergonomic recommendation for people and automation.
IDs provide precise selection without requiring labels for every cell. There is
no second per-execution naming mechanism in this version.

### Argument validation and expansion

Reference read and deletion flags are available only in the IO launcher with
`--append`; they cannot create a new batch. The metadata launcher supports labels,
listing, and the shared lifecycle commands, but rejects reference workload flags
with an explanation that metadata sweeps do not retain reusable data.

Exactly one reference workload mode is permitted. It is mutually exclusive with
literal `--read-from`, `--write-only`, `--write-no-read`, `--delete-only`, and the
other reference selectors. Reference reads require normal `--nodes` and accept
the existing supported read options. Reference deletion rejects `--nodes`,
benchmark options, and irrelevant size/thread/depth settings; it derives its
execution entirely from the source dataset and common environment. Ignore
unrelated benchmark settings in env.sh when preparing cleanup.

Resolve references under the existing batch mutation lock. They must identify
already committed, earlier executions in the same draft batch. Append is still
forbidden after sealing, including after failure or completion.

A group source must be a write-only IO group whose every execution declares one
retained dataset. Do not silently select a subset, choose the first cell, or infer
coordinate matching. A reader or cleanup group is not a valid producer. An
execution source must meet the same producer requirement individually. Reject
missing, forward, foreign-batch, metadata, non-retaining, or malformed references.

For a group read, expand source executions in ascending global ID order. For each
source, expand the normal requested read sweep in its existing coordinate order.
Each reader cell references exactly one producer. There is no zip/matching
behavior between producer and consumer node counts or other coordinates. Cleanup
groups likewise expand in source-ID order, one cell per producer.

Calculate and validate the expanded total against the existing 9,999-cell limit
before committing anything. Print the source count, read cells per source,
resulting total, and assigned IDs. Do not reorder previously committed groups.

### Machine-readable output and listing

On successful create or append, emit these records on stdout only after the group
manifest commit succeeds:

```text
STORAGE_SCALE_TEST_RESULTS_DIR=/absolute/path/to/results
STORAGE_SCALE_TEST_GROUP_ID=0001
STORAGE_SCALE_TEST_GROUP_LABEL=seed
STORAGE_SCALE_TEST_EXECUTION_IDS=0001,0002
```

The label value is empty when omitted. These are literal key/value records;
consumers split on the first `=` and must not source or evaluate them as shell.
Use canonical IDs and comma-separated lists without spaces. File paths follow the
batch's existing supported-path validation. Human summaries must not reuse these
keys. Failures must not print success identifiers for an uncommitted group.

Printing is not a second commit boundary: a client can exit after committing but
before receiving stdout. Retrying an append is a new append, not implicitly
idempotent. Listing exposes the committed group; supplying a unique label lets a
retry detect that its intended group already exists without adding another.

Listing is local, works through either launcher without current env.sh or cluster
access, and validates the batch manifest. The table shows ordered group ID,
label, workload/mode, execution IDs and coordinates, producer references, planned
dataset paths, cell states, and known deletion outcomes.

JSON listing uses `schema_version: 1`, canonical results path, sealed state, and
an ordered `groups` array. Each group exposes its ID, optional label, workload,
mode, and ordered executions. Each execution exposes its ID, coordinates, cell
state, optional producer execution ID, optional declared dataset, and cleanup
outcome. A declared dataset includes logical root, read target, directory/file
kind, and producer identity. Unknown runtime outcomes are explicit nulls, never
assumed availability. Use the same manifest reader for table and JSON output.
JSON stdout contains only JSON; diagnostics go to stderr.

For Kubernetes, listing describes locally committed or collected evidence and
says so; it does not pretend to know live PVC contents. Live attempt inspection
remains `--status`. No new cluster calls are hidden in listing or reporting.

## Dataset identity, dependencies, and safety

### Planned and published dataset records

The producer's immutable definition declares the dataset root, read target, data
kind, and retained-data mode before execution. A single-file dataset's root is
the generated containing directory; its read target is the file inside it. A
directory dataset uses the directory as its read target. Cleanup removes the
dataset root in both cases.

Consumers save the producer ID and exact declaration digest, resolved at append
time. Keep the reference in the manifest and execution definition rather than
only replacing it with a pathname. Resolve human labels to immutable IDs at
preparation; execution never depends on a mutable name lookup.

For readers of a multi-dataset group, partition benchmark artifact directories
by producer ID as well as reader group ID. Reuse the existing datestamp-ending
results basename inside each source partition. Identical read coordinates
against two datasets must have different output destinations on SSH, Slurm,
the PVC, and local collection; separating only the rendered reports is too late.
The global execution ledger remains authoritative, and snapshots remain owned
by the reader group rather than duplicated as independent configurations.

On successful production, atomically publish a small dataset record beside the
producer's existing workload/completion evidence. Include batch identity,
producer ID, definition digest, normalized logical root/read target, data kind,
and ownership-marker digest. Producer SUCCESS is committed only after the record
and existing completion artifacts verify. Persist and collect this record on all
substrates, including legacy generated write-only layouts without exact-byte
workload metadata. Do not checksum benchmark payload files.

Consumers inherit the producer's saved data location, shape, and any existing
data-access constraint. Their own IO sizes, reader node/thread counts, durations,
and supported modes remain configurable. Infer directory versus single-file
behavior from the producer rather than requiring a redundant env.sh change.
Existing mode restrictions still apply, including single-file random-IO limits.
Do not resize, regenerate, or reinterpret the retained dataset using consumer
generation settings. Producer node count does not implicitly limit reader count
on shared storage.

For referenced targets, authority comes from the producer's saved TEST_DIRS, not
the reader's current TEST_DIRS. Include all producer roots and unrelated group
roots in the prerequisite's whole-batch storage validation. Configuration
snapshots distinguish requested reader settings from effective source-derived
settings so reports show what actually ran.

Runtime treefile-cache provenance is separate mutable evidence associated with
the consumer execution. It must not overwrite sealed group snapshots. Exclude
the marker from both new scans and reused caches, and reject a cache inconsistent
with the source's declared identity using existing cache validation.

### Readiness and ordering

Preparation and start validate declarations, membership, ordering, and safe
planned containment; they do not demand that a not-yet-executed producer's
directory already exist. Preserve the existing checks for literal --read-from
paths. Future referenced targets are a separate validated input form, not a
general relaxation of path validation.

Immediately before a reader begins, require producer SUCCESS, matching published
dataset evidence, and a live, valid retained target. Revalidate containment and
ownership on the actual worker-side filesystem. A readiness failure becomes an
ordinary failed cell with actionable diagnostics and stops later execution.

Validate dependencies again at sealing. All edges point backward to write-only
producers, so the existing sequential dispatcher needs no graph scheduler. The
same source can have many reader groups, each with independent settings.

For each dataset, allow at most one cleanup cell. Reject duplicate cleanup and
any new reader after that dataset's cleanup has been committed to the draft.
Group operations are all-or-nothing: if any source has already been scheduled
for cleanup, reject a group read or duplicate group cleanup rather than silently
skipping it. Cleanup need not be the final cell of the entire batch, but it must
follow every consumer of its particular dataset.

### Ownership and deletion boundaries

Reserve an ownership marker named `.storage-scale-test-dataset.json` directly
inside each generated retained root. Create it atomically as the workload identity
before measured writing, binding the root to the batch nonce, producer ID,
definition digest, and normalized path. Preserve it through producer completion.
Declare this filename as tool metadata and explicitly exclude it from treescan,
treefile generation, payload totals, and reader target enumeration. Marker
creation and verification never occur inside measured I/O.

Failed producer retries may rebuild only their own generated targets using the
existing cleanup guards. Successful producers are not silently rewritten to
repair missing data. The marker and authoritative record prevent a retrying
cleanup cell from deleting a replacement directory that happens to reuse a name.

Create an immutable batch ownership nonce for new reference-capable batches and
include it in the sealed manifest. Marker bytes are derived from the saved
producer declaration; validate their digest against the authoritative record
rather than evaluating marker contents as shell input.

Before deleting an existing dataset root:

- Validate the exact source declaration and published producer SUCCESS evidence.
- Require a strict generated descendant of the producer's saved configured root;
  reject the configured root itself and the PVC mount root.
- Reject symlinked target components, a mismatched or linked marker, and overlap
  with durable control state, results, another dataset, or tool state outside the
  owned dataset subtree.
- Apply live worker-side containment checks, including the Kubernetes PVC
  realpath rules. Do not trust a host-side path alone.
- Recheck ownership before the destructive operation. Never infer ownership from
  a basename pattern alone.

An already-absent root is an idempotent cleanup success after saved identity and
safe containment are validated. Lookup errors, permissions failures, corrupt
evidence, or partial surviving data are not absence. If a root exists without its
matching marker, refuse deletion and show the expected identity and exact path.

Implement bounded incremental deletion that preserves the root marker until
payload and caches are removed; remove the marker and root last. If interrupted
in that final interval and an unmarked root remains, remove it only if it is
verified empty. A nonempty unmarked root must fail closed. Never use recursive
removal of an unmarked root to make retries appear successful.

Dataset contents are trusted benchmark inputs, as in the existing contract.
Concurrent external mutation, hostile pathname replacement during deletion,
cross-batch sharing, and restoring externally deleted payload are outside the
automatic-recovery scope. Detect observable inconsistency, preserve evidence,
and report a safe next action rather than adopting unknown data.

## Execution, failure, resume, and collection

### Shared cleanup cell and resource sizing

Add an execution kind `cleanup` with mode `delete-retained-dataset`. It records
its producer reference, owned root, group membership, and one-node requirement.
It uses the existing PENDING/RUNNING/SUCCESS/FAILED ledger, emits logs and an
atomic deletion receipt, and produces no benchmark measurements.

The receipt binds cleanup ID, producer ID, dataset declaration, and verified
absence. Commit SUCCESS only after deletion and receipt publication succeed.
Keep receipt and result publication outside any measured benchmark I/O.
Interrupted cleanup is retryable even if the previous invocation removed the
root but failed to publish its receipt.

Use one selected worker for deletion because the fixture and execution contract
already require shared visibility; Kubernetes uses the coordinator's existing
PVC mount instead, as described below. Cleanup-only resumes require one eligible
node and must not start Elbencho services or require irrelevant IO sizing.
Initial allocation still covers the maximum requirement of the whole sealed
batch. Workloads on storage without the required shared visibility remain
unsupported; do not invent per-host dataset ownership.

Implement shared validation/deletion logic behind existing substrate adapters.
Do not call the standalone delete-only launcher from inside the batch or create
an unrelated results directory. Standalone literal --delete-only behavior remains
unchanged; this follow-on adds Kubernetes support for batch cleanup cells only.

### SSH and Slurm

SSH stages and executes the cleanup helper on one saved eligible host, retrieves
logs and receipt, and commits the existing local cell ledger. Read-only referenced
cells use their producer record while retaining the normal cell dispatch path.

Slurm executes cleanup as a one-node step within the current coordinator
allocation. Preserve exact job ownership, cancellation, service cleanup, and
nonzero exit propagation. Cleanup shares the batch's group context and artifacts
but must not accidentally call the IO or metadata benchmark functions.

On both substrates, producer dataset records and consumer/cleanup provenance
survive host interruption and resume. Cell-status success gates must verify the
correct artifact family for each workload kind.

### Kubernetes

Extend the sealed control-bundle manifest and typed coordinator protocol with
producer declarations, reference edges, and cleanup definitions. The coordinator
resolves references from verified bundle/PVC state without Kubernetes API
credentials or access to current client env.sh.

Map logical producer roots/read targets through the fixed PVC mount exactly once.
Keep the saved batch control root unchanged. Validate both planned and live
paths without requiring the PVC mount root to be writable.

Readers and cleanup operate within the same whole-sweep attempt, use existing
worker identities, and retain the PVC-wide Lease. Cleanup is confined to the
producer dataset subtree and cannot release the Lease or remove the attempt's
control/results tree.

Execute deletion directly in the coordinator Pod using its existing shared PVC
mount and workload UID/GID. Do not require kubectl exec, a service RPC, or API
credentials inside the coordinator. A cleanup-only resume schedules one
coordinator on an eligible node without starting a worker DaemonSet solely for
deletion. Record its exact Node/Job/Pod evidence; resource and publication
validators must distinguish cleanup executor evidence from benchmark worker
evidence and validate only the resources that the attempt actually declares.

Collect dataset records, reference provenance, and deletion receipts through the
existing bounded, verified publication protocol. Preserve predecessor evidence
needed by pending readers when resume submits only non-successful cells: a
successful producer omitted from the new attempt must still have its immutable
declaration and verified published dataset record staged as dependency evidence.
Those records do not create another execution or change its SUCCESS status.

Verify dependency membership against the sealed batch rather than requiring that
every referenced producer be an executable member of the new attempt. Keep exact
Job quiescence, cleanup journaling, Lease-last cleanup, and collection-gated resume.

### Failure and dataset lifetime

- Producer failure leaves its readers and cleanup pending. Resume retries that
  producer before its dependants under existing global execution ordering.
- Reader failure preserves the source dataset and leaves later cells pending.
  Resume retries non-successful cells without rewriting a successful producer.
- Cancellation follows the existing attempt lifecycle; it does not automatically
  run pending dataset cleanup or change successful producer status.
- Cleanup failure stops the batch. Resume retries deletion idempotently; it does
  not rerun successful reads or recreate data.
- External loss or replacement of a successful producer's dataset fails with a
  precise dependency/path diagnosis. Do not reset producer SUCCESS to repair it.
- Completed cleanup does not invalidate prior producer or reader SUCCESS. Dataset
  availability is derived from producer evidence and deletion receipts, distinct
  from historical benchmark outcomes.

Attempt collection and fixture cleanup must preserve intentionally retained
benchmark datasets until their explicit cleanup cell runs. Diagnostic or control
cleanup must not treat them as disposable attempt workspace.

Give every reference/cleanup failure an operation, execution and producer IDs,
affected path, reason, and safe next action. Extend the existing diagnostic
vocabulary for missing/invalid dependencies or dataset identity as necessary;
do not report these as generic API timeouts. Preserve primary errors if receipt
or diagnostic publication also fails.

The failure-policy classes and supported recovery scope in
[KUBERNETES_ELBENCHO_LIFECYCLE.md](../KUBERNETES_ELBENCHO_LIFECYCLE.md) remain
unchanged. Add the concrete reference and cleanup boundaries to its fault matrix
and evidence mappings; retain unsupported-disaster boundaries rather than
promising recovery from arbitrary payload corruption or external mutation.

## Reporting, documentation, and compatibility

Version the new manifest and artifact records. Earlier batch formats retain
their existing start/resume/report behavior; do not rewrite a sealed batch.
Reference operations require a batch created in the reference-capable format.
Reject attempts to add references to an older draft with instructions to create
a new batch. Listing older batches may show their IDs without labels or dataset
records, but must not infer missing ownership proof from raw paths.

Extend the batch report index with labels, producer/read/cleanup relationships,
planned dataset locations, locally verified production, and deletion outcomes.
Successful cleanup is an operational result, not a throughput sample. Do not
average measurements across producers or hide their different dataset settings.

Within a multi-source reader group, partition detailed reports by producer ID.
Use `reports/groups/<group-id>/sources/<producer-id>/` so identical reader
coordinates against different datasets do not collide or aggregate. Single-source
and non-reference groups retain the prerequisite's ordinary per-group layout.
Keep group-specific report.txt files and existing benchmark artifact names.

Specialized reporters resolve batch-aware discovery keys with producer identity
as well as group/execution identity. Existing single-run and cache-import behavior
stays compatible. Preserve source provenance in any batch-aware cached metrics
so export/import cannot erase the partition.

Allow group labels as well as numeric IDs in the unified reporter's existing
--groups selector. Keep --kind all|io|mdtest: all includes cleanup summaries;
benchmark-specific selections do not invoke metric parsers for cleanup groups.
A completed cleanup-only selection can successfully render its operational
summary even though it has no aggregate measurements. An unfinished selection
with neither successful measurements nor successful cleanup retains the existing
nonzero empty-result behavior.

Document the group-expansion rule prominently: a multi-cell writer creates
multiple datasets, and a group reader runs the requested sweep on every one.
Show labelled one-dataset and multi-dataset examples, exact-ID selection,
machine-readable creation/listing, sealing, failure/resume, and cancellation
retention. Describe how to inspect failed cleanup rather than rerunning the
original producer. Clarify that listing/reporting reflect collected evidence on
Kubernetes and do not perform remote observation implicitly.

Update both launcher help texts, README/recipes, design and requirements,
integration guidance, and the normative lifecycle document. Add only durable
reference/cleanup invariants to docs/CONTEXT.md. Keep the prepared-batch design
record linked to this plan without claiming dataset references are implemented.

## Tests, implementation order, and acceptance

### Fast semantic and fault tests

Use temporary result trees, fake adapters, and existing controlled fault hooks.
Cover:

- Stable labels/IDs, duplicate labels, numeric namespace separation, listing from
  either launcher, pure JSON stdout, and commit-before-output interruption.
- Named single-dataset references, explicit execution selection, multi-source
  deterministic expansion, reported counts, and the expanded ledger limit.
- Missing/forward/foreign references, invalid producer kinds, mutually exclusive
  flags, literal-path compatibility, and append-after-seal rejection.
- Source-derived paths and data kind despite changed consumer env.sh, normal
  read coordinate ordering, and snapshot isolation.
- Preparation before target existence, producer-success readiness, failed producer
  stopping, reader failure retention, and pending-dependency resume.
- Same-source multiple readers, duplicate cleanup, reader-after-cleanup rejection,
  and all-or-nothing group validation.
- Ownership records/markers, realpath containment, single-file deletion of its
  containing owned tree, control-root overlap, symlink substitution, replacement
  identity, corrupt records, and permission/lookup failures.
- Marker exclusion from treescan, cached treefiles, exact-byte/file totals, and
  read phases; marker creation outside measured I/O.
- Interruption before deletion, during payload removal, after root removal,
  before receipt publication, and before terminal status. Verify repeat cleanup,
  empty unmarked final-root recovery, and refusal of nonempty unmarked trees.
- Cleanup-only resource sizing and dispatch without benchmark services, success
  artifact gates, log/receipt collection, and primary-error preservation.
- Kubernetes dependency evidence for already-successful producers absent from
  resume selection, verified collection, and unchanged attempt cleanup/Lease gates.
- Reader report partitioning by source, no cleanup metrics, label selection,
  source-preserving cache roundtrips, and no report filename collisions.
- Supported macOS command adapters and quoted paths; no UID/GID ownership changes
  on the initiating host.

Test semantic outcomes and exact ownership boundaries, not entire generated
shell strings. Give normative fault rows focused evidence tests and verify their
references using the existing contract checks.

### Bounded real-fixture coverage

Add one retained-dataset batch scenario on SSH, Slurm, and Kubernetes using the
existing reusable fixture:

1. Prepare a labelled, small one-cell write-only group, two reader groups with
   different settings, and a labelled cleanup group.
2. Verify no producer executes during preparation and listing exposes all refs.
3. Start through the other launcher and inject one reader failure.
4. Verify producer SUCCESS and retained payload, later reads/cleanup pending.
5. Collect before resume on Kubernetes; resume without rerunning the producer.
6. Verify both reader groups finish before cleanup, final dataset absence,
   deletion receipt, separate reports, and retained benchmark history.
7. Collect final Kubernetes results and verify exact attempt cleanup and Lease
   release; tear the fixture down through the existing lifecycle.

Multi-source expansion, reverse ordering, and every deletion interruption belong
in fast tests rather than an expensive real Cartesian matrix. Reuse current
failure staging, deadlines, archive caching, and diagnostics. Run all existing
SSH/Slurm/Kubernetes scenarios as well, with Docker SBX locally and the manual
amd64/arm64 NFS workflow for final validation.

### Implementation sequence

1. Extend shared batch metadata with labels, producer declarations, backward
   references, deterministic expansion, listing, and semantic tests.
2. Publish dataset identity records/markers and implement referenced reads on all
   three adapters, including successful-producer evidence during resume.
3. Add shared cleanup execution, bounded marker-preserving deletion, receipts,
   substrate dispatch, and interruption tests.
4. Extend collection/publication validation and source-aware reporting, then
   synchronize documentation and normative fault evidence.
5. Add the bounded real scenario, run pinned checks and the complete Docker SBX
   suite, and verify the manual dual-architecture NFS workflow.

Acceptance requires retained dataset reuse without manual path discovery, named
group ergonomics for both one and many producers, precise selective IDs, safe
retryable cleanup, preserved first-failure/resume behavior, and attributable
reports. The complete prerequisite batch feature and existing standalone sweeps
must remain functional. No live append, cross-batch references, automatic
credentialed scheduler, arbitrary dependency graph, or expanded disaster-recovery
guarantee is introduced.
