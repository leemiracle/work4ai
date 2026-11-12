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

# Kubernetes Elbencho Lifecycle and Fault Contract

This document is the normative lifecycle and failure contract for the
asynchronous kubectl substrate of the Elbencho filesystem IO and metadata
sweeps. It freezes
the states, legal transitions, invariants, linearization points, supported
fault boundaries, and explicit non-goals against which implementation and
review are evaluated. The historical design record explains why the feature
was built this way; this document defines the behavior that must remain true.
Both workloads use the same attempt and execution ledgers. Metadata cells
publish their per-iteration `.out` and `.csv` files; filesystem IO cells retain
their workload-specific completion artifacts.

Prepared filesystem batches add a local assembly phase before attempt creation.
`--batch` and `--append` publish only local immutable group snapshots, execution
definitions, and the versioned batch manifest. They create no Kubernetes or
claim resources. Start validates the complete saved profile and discovers
capacity, then permanently seals the manifest before entering the attempt
lifecycle below. A sealed batch remains immutable after submission failure. Its
saved profile freezes what the groups share: `KUBECTL_NAMESPACE` (the default
namespace of keys that name none; optional when every key names its namespace),
the node selector, image, pull policy, workload identity, and
`KUBECTL_SEQUENCER_IMAGE`, which is frozen as the image it resolves to (the
built-in default when unset) so that neither a later `env.sh` edit nor a newer
default changes how a prepared batch sequences its namespaces. Each group's
snapshot records its own roots, and so its claims and namespace.

## Failure policy and boundary

Failures have three support classes:

| Class | Expected frequency | Required behavior |
|---|---|---|
| Required recovery | Medium or high | Reconcile or retry automatically within a bounded deadline. If that fails, retain recoverable state and return actionable diagnostics. |
| Required diagnosis | Low | Fail closed, preserve authoritative evidence, identify the failed invariant or operation, and give the next safe action. Bespoke automatic recovery is not required. |
| Unsupported disaster or corruption | Very low or outside the trust model | Never claim success or delete ambiguously owned resources. Detect and report the inconsistency when possible, but make no recovery promise. |

Interruption safety applies immediately before and after the external-effect
boundaries listed under [Linearization points](#linearization-points). It does
not promise recovery from a kill between every pair of shell statements.
`TERM`, `INT`, command failures, and API failures are handled in the current
process. `SIGKILL`, Pod eviction, node loss, and host loss are reconciled by a
later lifecycle command.

An error never becomes a durable `ERROR`, `UNKNOWN`, or `AMBIGUOUS` lifecycle
state. Those are observations, not proven attempt facts. The command retains
the last proven state, exits nonzero, and reports the uncertainty.

## State machines

The attempt lifecycle comprises three authoritative state machines. Kubernetes Job
state is corroborating evidence, not a fourth source of lifecycle truth.

### Local attempt lifecycle

The local metadata controls which CLI operations may mutate an attempt:

```text
new -> PREPARED -> SUBMITTED -> TERMINAL -> COLLECTION_IN_PROGRESS -> COLLECTED
          |             |
          |             `-> CANCEL_REQUESTED -> TERMINAL
          `-> SUBMISSION_FAILED
```

The complete legal transition set is:

```text
new -> PREPARED
PREPARED -> SUBMITTED
PREPARED -> SUBMISSION_FAILED
SUBMITTED -> CANCEL_REQUESTED
SUBMITTED -> TERMINAL
CANCEL_REQUESTED -> TERMINAL
TERMINAL -> COLLECTION_IN_PROGRESS
COLLECTION_IN_PROGRESS -> COLLECTED
```

No transition leaves `COLLECTED` or `SUBMISSION_FAILED`. Resume creates a new
attempt; it never reopens its predecessor. Local `TERMINAL` means that the
remote outcome is durably terminal and measured I/O has ended. The exact Job
must additionally be terminal or verified absent before collection may
publish or remove remote state.

For a sealed batch, an initial `SUBMISSION_FAILED` attempt can be replaced by
`--resume` only when all execution cells remain `PENDING`, no predecessor or
creation intent remains, and the existing exact-resource journal proves every
resource deletion, claim Lease release, and reserved run-tree release. An
incomplete rollback retains the existing recovery gate. Ordinary completed
attempts still require collection before resume.

### PVC run lifecycle

The run tree on a claim is authoritative for benchmark progress until
collection:

```text
PREPARED -> RUNNING -> SUCCESS
    |          |
    |          `----> FAILED
    `---------------> CANCELLED
```

`PREPARED` may also become `FAILED`; `RUNNING` may become `CANCELLED`.
`SUCCESS`, `FAILED`, and `CANCELLED` are immutable terminal outcomes. Recovery
may reconstruct a missing terminal summary or publication manifest from a
consistent ledger, but may not change one terminal outcome into another.

Every `TEST_DIRS` key names its claim: `[NAMESPACE/]CLAIM:PATH`, the
namespace defaulting to `KUBECTL_NAMESPACE`. Its normalized form
`NAMESPACE/CLAIM:PATH` is the root's logical path, and every claim is mounted
at `/mnt/storage-scale-test/<claim>`, so the root's Pod path is
`/mnt/storage-scale-test/<claim>/<path>`. The roots of one target share a
namespace.

Durable run state resides at
`<control root>/.storage-scale-test/runs/<attempt-id>`. The control root of a
segment (see below) is the lexically first normalized root of every group in
its namespace, and the run tree lives on that root's claim. The control roots
are saved in the immutable attempt configuration. The hidden directory is
created by the configured workload identity; the claim's mount root need not
be writable. Each claim's Lease remains discoverable even when competing
invocations configure different test roots. Because a namespace's control
root is derived from all of the batch's groups in it, a resume keeps the same
control root even when only a later group's cells remain.

### Per-cell lifecycle

Each reified execution has this lifecycle:

```text
PENDING -> RUNNING -> SUCCESS
                  `-> FAILED
```

A cell never returns to `PENDING` within an attempt. Coordinator loss while a
cell is `RUNNING` turns it into a collectible failure; later cells remain
`PENDING`. Resume creates another attempt containing the cells that did not
succeed. Collected successful cells and their results remain immutable.

A batch control bundle retains the complete sealed manifest and every group's
immutable snapshots, with only the selected execution definitions on resume.
The coordinator verifies each included definition's committed membership and
group mapping and runs cells in isolated contexts. Publication keeps the global
execution ledger at the batch root while mapping each result and completion
artifact to its owning group directory. Collection verifies those exact mappings
and snapshot contents before importing results; it cannot reassign an artifact
to another group or rewrite a previously successful cell.

### Kubernetes Job evidence

The exact Job may be observed as:

```text
NOT_CREATED, CREATE_AMBIGUOUS, ACTIVE, COMPLETE, FAILED, or DELETED
```

With several segments, a coordinator Job may also be `SUSPENDED` (created,
not yet started), and a segment abandoned while suspended is `NOT_STARTED`
(journaled `segment-not-started[-s<k>]`).

Only the saved kind, name, namespace, UID, ownership nonce, and attempt labels
establish identity. A broad label query never establishes ownership. A failed
or externally deleted exact Job with a nonterminal run ledger is bounded
coordinator-loss evidence: a lifecycle command may recover the run to a
collectible failure when the saved identity and durable control state agree.

### Attempt identity: segments and claims

New attempts write identity schema 4. A *segment* is one namespace; the
identity lists the attempt's segments in run order and, for every segment,
the claims its Pods mount. Each claim records its namespace and namespace UID,
its name and UID, the PersistentVolume it is bound to and that PV's UID, and
the deterministic Lease name derived from the three UIDs. Claims are numbered
`j = 0..M-1` in sorted order (namespace, then claim name) across the whole
attempt: that is the Lease acquisition order. The order is byte order
(`LC_ALL=C`), whatever the locale of the host that writes or reads the
identity. Every segment has at least one claim, and no two claims share a PV.
An attempt has at most 16 segments and 32 claims; `kubectl_validate_test_dirs`
and batch preflight reject more claims, naming the limit, before any cluster
or claim mutation.

Attempts started by storage-scale-test v1.x (identity schemas 2 and 3, one
claim per target, configured with `KUBECTL_PVC` and `KUBECTL_PV`) are not
loaded: every lifecycle command refuses them, names the schema, and says to
collect the attempt with storage-scale-test v1.x before upgrading. It changes
nothing.

Segment 0 keeps the plain resource names and journal keys. Segment `k > 0`
inserts `-s<k>` after the attempt ID in names (`sst-elb-<id>-s<k>-workers`)
and appends it to journal keys (`workers-s<k>`); the sequencer RBAC keys
(`sequencer-role-s<k>`, `sequencer-binding-s<k>`) carry it for every segment.
The per-segment local files `remote-reservation.sh`, `worker-endpoints.tsv`,
`endpoint-drift.tsv`, `control-bundle` and `collected-state`, and the steps
`release-remote-run`, `segment-succeeded` and `segment-not-started`, take the
same suffix. Claim `j`'s Lease has the journal key `pvc-lease` (claim 0) or
`pvc-lease-c<j>`, and its release step is `release-` followed by that key.
Every Pod of a segment (workers, coordinator, helpers) carries the label
`storage-scale-test.nvidia.com/segment: "<k>"`, and every per-segment
selector, diagnostic capture, and readiness classification includes it.

Cleanup uses one enumeration derived from the saved identity: the sequencer,
sweep Jobs, DaemonSets in reverse segment order, transfer helpers, inspectors,
policies, then sequencer RBAC. Leases are released last, in reverse claim
order (claim 0 last).

### Segments and the sequencer

A plain run, or a batch whose groups all use one namespace, is one segment:
one worker DaemonSet, one coordinator Job (created unsuspended), and one set
of NetworkPolicies, all in that namespace; the workers, the coordinator and
the transfer helper mount every claim the namespace's groups use. Several
targets in one namespace therefore need no sequencer, ServiceAccount, Role,
RoleBinding or sequencer image.

A batch whose groups span namespaces has one segment per namespace that runs
at least one of the attempt's executions. Segments are ordered by the first
execution of each namespace in batch-ledger order, and each segment's cells
run in ledger order. Each execution belongs to the namespace of its group's
roots. Each segment `k` has:

- a Lease per claim of its namespace, a worker DaemonSet, and same-namespace
  NetworkPolicies;
- a run tree below its own control root;
- a coordinator Job in its namespace that mounts every claim of the namespace
  and runs only the executions of its namespace's groups, in global
  execution-ID order. Its control bundle holds just those definitions, the
  complete batch manifest and group snapshots, that segment's worker
  endpoints, and a `segment.tsv` row naming its index and namespace. The
  coordinator refuses, before any ledger mutation, a definition whose group's
  roots are in another namespace. Its control root is the first root of its
  own namespace. Each cell runs with its own group's roots, read from the
  group snapshot, so its generated targets and read-from path are checked as
  `NAMESPACE/CLAIM:PATH` against that group alone, never against the batch's
  union of roots, which may hold the same `claim:path` in another namespace
  or a root nested in another group's.

A one-segment batch attempt's bundle carries `segment.tsv` too, so every
batch coordinator knows its namespace among the batch's roots.

The claims, roots, control root and checked workload paths of a segment cover
every group of the batch in its namespace, not only the groups with cells in
this attempt, so a resume prepares the same storage.

Status and collector helpers (inspectors) touch only a segment's run tree,
so they mount only its control root's claim: a later deletion of another
claim of the segment never keeps them from starting, and the cluster
identity check still reports that claim as `IDENTITY_MISMATCH`.

Every rendered manifest quotes its name, namespace, node, claim, image and
node-selector strings, so valid names such as `123`, `1.5`, `yes`, `on` or
`null` stay YAML strings.

Prepare walks the segments in order through each phase: the cluster identity
of every claim, one node discovery, a transfer helper per segment with path
and access checks on its claims, every claim's Lease in claim order, every
run-tree reservation, then every segment's policies and workers, and finally
every segment's endpoints. A segment whose control root reaches storage that
an earlier segment's control root reaches finds that run tree and fails its
reservation; the error names the control root as a possible alias.

Submission uploads each segment's bundle through that segment's helper. With
several segments it then creates every coordinator Job with
`spec.suspend: true` (Kubernetes 1.24 or newer), followed by the sequencer's
ServiceAccount, Roles, RoleBindings, and Job. The sequencer runs
`KUBECTL_DEFAULT_SEQUENCER_IMAGE` (a pinned `docker.io/alpine/kubectl`) unless
`KUBECTL_SEQUENCER_IMAGE` names another digest-qualified image that provides
`sh`, `kubectl`, `grep`, and `sleep`; a batch in one namespace needs none of
this.

The *sequencer* is a Job in segment 0's namespace. It unsuspends Job 0, waits
for it to be `Complete`, unsuspends Job 1, and so on; on `Failed` it stops, so
later segments never start. Its loop re-derives progress from live Job state
after a restart. A coordinator exits 0 exactly when its published outcome is
`SUCCESS`, so `Complete` means the segment succeeded. The sequencer exits 0
when every Job is `Complete` or one `Failed`, 2 on bad input, 3 only when the
API server answers NotFound for a Job, 4 on a UID change, and 5 when
`kubectl`, `grep`, or `sleep` is missing or cannot run, or the mounted
ServiceAccount credentials are missing. Because `kubectl` ignores its
in-cluster configuration once a client flag such as `--request-timeout` is
given, the sequencer writes a kubeconfig that names the mounted ServiceAccount
token file (so a rotated token is picked up) and bounds every request with a
fixed 30 s `--request-timeout`. It re-observes every
`KUBECTL_SEQUENCER_POLL_SECONDS` (1 to 3600, default 10), which is validated and
read from the environment when the sequencer Job is rendered at submission,
not frozen with a prepared batch.

The sequencer is the one narrowly scoped exception to the rule that no Pod
holds Kubernetes API credentials. Only the sequencer Pod mounts a
ServiceAccount token. In every segment's namespace a Role grants that
ServiceAccount `get` and `patch` on exactly that segment's coordinator Job (by
`resourceNames`), and each patch carries a JSON-patch `test` of the Job's UID.
Coordinator, worker, and helper Pods still mount no token.

A resume plans its own segments from the cells that remain, so a resume that
leaves one namespace is a one-segment attempt without a sequencer. Batch
preflight before a sealed batch resumes plans the same way, from the
executions that have not succeeded: it checks the claims, the claim limit,
and the sequencer settings (the image reference, never pulled) only for those
segments, so a namespace or claim used only by succeeded executions may be
gone.

`validate_env.sh` checks only the one target, in the one namespace, that
`env.sh` describes, and creates only temporary owned Jobs, which it deletes.
Its sequencer checks are warnings unless `--sequencer` is given (S-23, S-28);
a batch spanning namespaces is checked per namespace by batch preflight when
it starts. See [DESIGN §3.4](DESIGN.md#34-configuration-validation).

### Public status projection

| Local state | Public status behavior |
|---|---|
| `PREPARED` | Report preparation, or reconcile a provably failed submission to `SUBMISSION_FAILED`. |
| `SUBMISSION_FAILED` | Report `SUBMISSION_FAILED`. |
| `SUBMITTED` | Project the validated run state and current-attempt progress as described below. |
| `CANCEL_REQUESTED` | Report pending cancellation and direct the user to retry `--cancel`. |
| `TERMINAL` | Report the validated terminal run outcome. |
| `COLLECTION_IN_PROGRESS` | Report the terminal outcome and resumable collection context. |
| `COLLECTED` | Report the locally verified terminal outcome without cluster access. |

Identity, authentication, query, and consistency failures return nonzero
instead of inventing another state value.

Public output uses `STATE=<outcome>`; during preparation it reports
`PREPARING`, a display projection rather than another durable state.
The outcome is refreshed after the execution scan; a transition refreshes counts
once. Counts remain bounded observations, not an atomic sweep-wide transaction.

A multi-segment attempt aggregates its segments. Their Jobs are observed last
segment first: segment `k+1` starts only after segment `k` is `Complete`, and
`Complete` never changes, so one pass cannot see a later segment started while
an earlier one still runs merely because the earlier one finished between two
observations. Segments before the current one (the first whose Job is not
`Complete`) succeeded; the current segment is observed through an inspector in
its namespace; later segments have not started. Counts span every segment.
`RUNNING` covers the gap between two segments, and `NEXT_ACTION=COLLECT`
follows once the last segment is terminal or any segment failed or was
cancelled. Status also starts the current segment's still-suspended Job when
every earlier Job is `Complete`, with the user's credentials and the same
UID-tested patch, which recovers a lost sequencer. A coordinator lost after
its last cell leaves a `Failed` (or deleted) Job, so the sequencer stops; when
lost-coordinator recovery proves the segment's ledger `SUCCESS`, status
journals `segment-succeeded[-s<k>]` (treated as `Complete` from then on) and
starts the next segment. Worker drift on the current segment or any later one
fails the attempt: the sequencer is deleted, the current Job is observed once
more, `stopped-by-drift` is journaled and the Job is deleted, the current
segment recovers to `FAILED`, and later segments are recorded as never started before
their suspended Jobs are deleted. If the current segment succeeded meanwhile
(its Job is `Complete` at that last observation, or its ledger is `SUCCESS`
after the deletion, which is then journaled `segment-succeeded[-s<k>]`),
status fails without touching it and the next `--status` fails the following
segment instead. The view adds `SEGMENT_COUNT`, `SEGMENT_CURRENT`, and per
segment `SEGMENT_<k>_NAMESPACE` and `SEGMENT_<k>_STATE` (`SUCCESS`, `FAILED`,
`CANCELLED`, `RUNNING`, `PENDING`, or `NOT_STARTED`), with `k` the 0-based
segment index; a one-segment attempt prints none of them. In
`CANCEL_REQUESTED`, status names the segment being cancelled (the first whose
Job is not `Complete`) with `SEGMENT_CURRENT`, `SEGMENT_<k>_NAMESPACE`, and its
exact Job in the `CANCELLATION_INCOMPLETE` diagnostic.

Cancellation linearizes first: `SUBMITTED -> CANCEL_REQUESTED`, then the
sequencer's exact deletion, and only then are the segments classified, so no
segment can start after that observation. It cancels the first segment that
has not succeeded exactly as a one-segment attempt is cancelled, and records
every later segment as never started before deleting its suspended Job. A
segment that succeeds while it is being cancelled passes cancellation to the
next one; so does a segment whose next one the sequencer started just before
it was stopped, which is then the one cancelled. Right before deleting a
coordinator Job, cancellation observes it again and leaves a `Complete` Job
and its ledger alone. The coordinator's `--finalize-cancelled` never
overwrites a terminal ledger: `SUCCESS` and `CANCELLED` keep their outcome
(only a bounded publication gap is repaired), and `FAILED` becomes `CANCELLED`
only when it is the failure that the coordinator's own TERM or INT handler
published while its Job was deleted (run-summary exit code 143 or 130). A
segment whose Job cancellation deleted but whose ledger is `SUCCESS` is
journaled `segment-succeeded[-s<k>]`. `--cancel` reports the outcome the
ledgers hold, which is `SUCCESS` when every segment finished first. Every step
is journaled or idempotent, so repeating an interrupted `--cancel` completes
it. Workers, run trees, and Leases remain until collection.

Collection gates every started segment (terminal run outcome and quiescent
exact Job; endpoint drift is checked on the last started segment), stops the
sequencer, streams each segment's state tree through a collector in its own
namespace that mounts the segment's control claim, then imports the segments in
order as `collected-state[-s<k>]` and journals `collection-published`.
Unstarted segments contribute no results. Cleanup then releases every
segment's run tree, deletes every owned object including the sequencer's
ServiceAccount, Roles, and RoleBindings, and releases the Leases in reverse
claim order. Each cleanup step is journaled, so an interrupted collection
resumes where it stopped.

At the results root, `run.status` and `run-summary.tsv` always describe the
attempt. A one-segment attempt publishes its own ledger files under their
plain names: `run.status`, `run-summary.tsv`, `startup-error.txt`, and
`coordinator-loss.tsv`. In a multi-segment attempt every segment publishes its
ledger files with the suffix of its namespace: `run-<namespace>.status`,
`run-summary-<namespace>.tsv`, `startup-error-<namespace>.txt`, and
`coordinator-loss-<namespace>.tsv`. After every started segment is imported,
collection publishes the attempt's aggregate outcome as `run.status`:
`SUCCESS` only when every segment ran and succeeded; otherwise the `FAILED` or
`CANCELLED` outcome of the segment that did not succeed (segments run in order
and nothing starts after one that did not succeed, so there is at most one);
and, when every segment that ran succeeded but later ones were abandoned,
`FAILED` if worker drift stopped the attempt (journaled `stopped-by-drift`)
and `CANCELLED` if a user's cancellation did. Worker drift never ends an
attempt `CANCELLED`. The aggregate `run-summary.tsv` (`scope attempt`) holds
the attempt's execution counts, a `reason worker-drift` row after `run_status`
when drift handling stopped the attempt, a `segments <N>` row, and one
`segment <k> <namespace> <outcome>` row per segment (`NOT_STARTED` for an
abandoned one). Both files are deterministic, and their digests are first
recorded in the attempt's local `results-aggregate.tsv`, so a repeated import
republishes identical bytes and a later attempt can supersede them. Every
other published path belongs to one execution or one group, or is a
byte-identical snapshot. A later attempt's collection removes every earlier
attempt's `run*.status` and `run-summary*` files, including an aggregate, and
replaces an earlier `startup-error*` or `coordinator-loss*` file only at a
path it publishes itself; the earlier copies remain in that attempt's
`collected-state[-s<k>]`. Status, cancel, collect, and resume read each
segment's ledger only from those local `collected-state[-s<k>]` copies.

`ATTEMPT` identifies the current attempt. `EXECUTION_SCOPE=CURRENT_ATTEMPT` and
`EXECUTIONS_{TOTAL,PENDING,RUNNING,SUCCEEDED,FAILED}` exclude previously
successful cells on resume. Only one progress view is emitted:
`PROGRESS_SOURCE=PVC` before publication, or `LOCAL` for verified collected
state. `RESULT_COLLECTION` is `PENDING`, `CLEANUP_PENDING`, or `COMPLETE`;
`NEXT_ACTION` is `WAIT`, `COLLECT`, `RESUME`, `INSPECT`, or `NONE`, and every
Kubernetes `--status` prints it: `SUBMISSION_FAILED` gives `RESUME` for a sealed
batch and `INSPECT` for a plain run, and `CANCEL_REQUESTED` gives `INSPECT`. A
sealed batch's status also prints `BATCH=SEALED` and, per group,
`GROUP_<NNNN>_KIND` and `GROUP_<NNNN>_TARGET`. When a cell failed, status
and collect print `FAILED_EXECUTION`, a batch's `FAILED_GROUP`, and
`FAILED_LOG` when a coordinator log was saved. A terminal run outcome permits
collect, which still enforces exact Job quiescence before import. Zero running
cells alone never permits it.

## Invariants

1. Attempt ID, ownership nonce, segment and claim identity (namespace, claim,
   bound PV, and their UIDs), control roots, configuration, image, workload
   identity, and execution definitions are immutable.
2. One attempt is current per result tree. The current pointer is atomic;
   historical attempt metadata remains immutable.
3. One mutating lifecycle command may operate on a result tree. Concurrent
   commands are rejected rather than queued.
4. One active sweep may own a claim. A deterministic namespaced Kubernetes
   Lease per claim, keyed by the namespace, PV, and PVC UIDs, is its global
   reservation; it is never renewed, expired, or stolen. An attempt acquires
   its claims' Leases in claim order (namespace, then claim) and releases them
   in reverse.
5. Every external create follows `durable intent -> create -> exact identity
   observation -> durable UID journal -> intent removal`.
6. Destructive operations require exact kind, name, namespace, UID, ownership
   nonce, and attempt identity. Operational lookup failure is not absence.
7. `PREPARED` may contain partial resources, but every possible resource is
   represented by a creation intent or exact resource journal.
8. `SUBMITTED` has an exact UID-journaled sweep Job per segment (one segment
   per namespace) and, with several segments, an exact UID-journaled
   sequencer Job.
9. The per-attempt coordinator lock in the segment's run tree gives one Job Pod
   authority to mutate the ledger; duplicate Job Pods exit first.
10. Node UID, architecture, resolved image identity, and Pod IPv4 address are
    frozen. A worker Pod name or UID may change only when the same Node and IP
    remain healthy; all other drift fails rather than retargeting the attempt.
11. A cell commits only when its artifacts, exit code, terminal cell state,
    summary, and publication manifest agree.
12. Scratch-to-PVC result publication never overlaps measured benchmark I/O.
13. A terminal run is collectible only when its ledger, summary, publication
    manifest, and exact Job quiescence agree.
14. Remote cleanup begins only after the complete local publication verifies.
15. `COLLECTED` means the local publication verifies, every remote run tree
    and every claim's Lease are gone, exact owned resources are gone, and no
    benchmark work remains.
16. Resume never reruns a collected successful cell.
17. Traversing, linked, contradictory, corrupt, or identity-mismatched state
    fails closed.
18. Supplemental diagnostic failure does not block safe cleanup or replace the
    primary error.

## Linearization points

| Operation | Linearization point |
|---|---|
| Attempt identity exists | Atomic rename of the complete attempt metadata directory. |
| Attempt becomes current and recoverable | Atomic replacement of `current-attempt` before external mutation. |
| Local transition | Atomic replacement of `state.sh`. |
| Claim ownership | API creation of the claim's deterministic Lease, followed by exact identity observation and durable UID journaling, in claim order. |
| Claim ownership release | UID-preconditioned deletion of the exact Lease after remote state, all other owned resources, and every later claim's Lease are gone. |
| A Kubernetes resource may exist | Creation intent is durable before `kubectl create`. |
| Kubernetes ownership is locally established | Exact UID-bearing resource journal is atomically published. |
| Submission succeeds | Exact Job UID is journaled and local state becomes `SUBMITTED`. With several segments, every Job is created suspended, and the sequencer's ServiceAccount, Roles, RoleBindings, and Job are journaled before `SUBMITTED`. |
| Segment starts | UID-tested patch of a suspended Job to `suspend: false`, made by the sequencer or by `--status` only after every earlier segment's Job is `Complete`. |
| Segment abandoned | Journal step `segment-not-started[-s<k>]` after observing the Job still suspended, before its exact deletion. |
| Drift stops a multi-segment attempt | Journal step `stopped-by-drift` before the current segment's Job is deleted. |
| Coordinator ownership | Atomic creation of `coordinator.lock`; owner-file completion is recoverable initialization. |
| Run becomes active | Atomic `run.status=RUNNING` after bundle, snapshots, ledger, and service validation. |
| Cell begins | Atomic `NNNN.status=RUNNING`. |
| Cell commits | Atomic replacement of the publication manifest after artifacts, exit code, terminal cell status, and summary. |
| Run commits its outcome | Terminal summary and status plus a consistent publication manifest. |
| Cancellation begins | `SUBMITTED -> CANCEL_REQUESTED` before exact Job deletion. With several segments, the sequencer's exact deletion follows and precedes any segment observation. |
| Collection publication begins | `TERMINAL -> COLLECTION_IN_PROGRESS` after bounded archive receipt and before extraction or result publication. The unpublished archive may exist while local state remains `TERMINAL`. |
| Local import checkpoint | Verified state is atomically installed as `collected-state[-s<k>]` after result merging. |
| Collection completes | Remote and resource cleanup completes, then local state becomes `COLLECTED`. |
| Resume succeeds | A new attempt becomes current under compare-and-swap against the collected predecessor, or a sealed batch's initial failed submission with complete rollback evidence. |

## Fault matrix

`Covered` means implementation and focused regression evidence exist.
`Acceptance pending` means local and kind coverage exists but the named
external environment must still be exercised. A future change that weakens a
covered row is a regression. Faults outside this matrix require an explicit
contract change rather than silently expanding the release boundary.

### Submission

| ID | Fault boundary | Class | Required result | Status |
|---|---|---|---|---|
| S-01 | Invalid configuration, path, PVC, selector, identity, or image | Required recovery | Reject before mutation and identify the field. | Covered |
| S-02 | Exit before unpublished identity installation | Required recovery | Ignore or remove opaque staging; no current attempt exists. | Covered |
| S-03 | Exit after current `PREPARED` publication | Required recovery | Later lifecycle command rolls forward or records `SUBMISSION_FAILED`. | Covered |
| S-04 | Concurrent command for one result tree | Required recovery | One lock owner; loser exits without mutation. | Covered |
| S-05 | Competing result trees reserve one PVC | Required recovery | One owner; loser rolls back without touching it. | Covered |
| S-06 | Exit around PVC Lease creation or journaling | Required recovery | Reconcile exact owner/intent; never steal the Lease. | Covered |
| S-07 | API accepts create but response is lost | Required recovery | Resolve deterministic identity, then journal or delete the exact object. | Covered |
| S-17 | Create request fails in transit and the object is absent | Required recovery | Resolve by exact-name GET, then adopt the object or resend the same manifest and nonce under the create-retry rules below. | Covered |
| S-08 | API visibility is delayed within the creation ambiguity horizon (defined below the table) | Required recovery | Wait and perform a later linearizable GET. | Covered |
| S-09 | Object appears after the creation ambiguity horizon (defined below the table) | Required diagnosis | Retain possible identity and print exact inspection/cleanup guidance. | Covered diagnostically; automatic recovery unsupported |
| S-10 | API 429, 5xx, timeout, or disconnect during observation | Required recovery | Bounded retry with jitter, then safe retry guidance. | Covered |
| S-11 | Credentials expire or network fails during submission | Required recovery | Preserve recoverable state; roll back only from exact evidence. | Covered locally; external acceptance pending |
| S-12 | Transfer Pod, policy, or worker cannot become Ready | Required recovery | Bounded rollback plus descriptions, logs, and events. | Covered |
| S-13 | Bundle upload is interrupted | Required recovery | Do not start the Job; remove the exact partial run. | Covered |
| S-14 | Exit after Job acceptance but before `SUBMITTED` | Required recovery | Quiesce exact Job and workers before releasing remote state. | Covered |
| S-15 | Submitter exits after `SUBMITTED` but before printing commands | Required diagnosis | Retain discoverable state under the supplied result directory. | Covered; lost stdout is accepted |
| S-16 | Original Teleport credential expires after handoff | Required recovery | Job continues; later client reports authentication and safely retries after login. | Acceptance pending |
| S-18 | An invalid claim-qualified root: `KUBECTL_PVC` or `KUBECTL_PV` still set, a key without its claim, an invalid namespace, claim or path, or a target whose roots span namespaces | Required recovery | Reject before any cluster or claim mutation, report every problem (with the replacement `TEST_DIRS` line for v1.x settings), and name the batch group. | Covered |
| S-19 | Exit after acquiring an earlier claim's Lease but before a later one | Required recovery | A later lifecycle command rolls back every journaled object and releases the acquired Leases in reverse claim order. | Covered |
| S-20 | A competitor holds a later claim's Lease | Required recovery | Roll back, releasing only this attempt's earlier Leases; never touch the competitor. | Covered |
| S-21 | One segment's workers never become Ready | Required recovery | Roll back every namespace: stop workloads, release every run tree, delete every object, release Leases in reverse claim order. | Covered |
| S-22 | Two segments' control roots reach the same storage | Required recovery | The later segment's run-tree reservation fails, the error names the control root as a possible alias, and everything rolls back. | Covered |
| S-23 | The sequencer's image, token, or RBAC is unavailable, or the probe is interrupted | Required recovery | With `--sequencer`, when the server version and sequencer permissions check out, `validate_env.sh` runs the checked-in sequencer (its effective image) against an absent Job in the target's namespace and reports success only on its NotFound exit code 3; any other result is an error with the keep-one-namespace fallback. Probe objects are deleted on every exit, including INT/TERM and lost create responses, by UID or by deterministic name after nonce verification. A refused RBAC object at submission rolls back every namespace. | Covered |
| S-24 | A policy or worker create fails after the transfer helpers exist | Required recovery | Leave the failed object to its creation intent or journal; the rollback releases every run tree through the helpers (or a fresh inspector when a helper is gone), deletes every object, releases the Leases, and records `SUBMISSION_FAILED`. | Covered |
| S-25 | An exit or lost create response leaves only a creation intent for a sequencer object (ServiceAccount, Role, RoleBinding, or Job) | Required recovery | The submitter's rollback, or a later status or collect, reconciles the intent by exact name and nonce, deletes the object, and completes the rollback. | Covered |
| S-26 | Several claims share one namespace | Required recovery | They form one segment: one Lease per claim in sorted order, and the segment's workers, coordinator and transfer helper mount every claim (status and collector helpers mount its control claim); every per-segment Pod selector includes the segment label. | Covered |
| S-27 | Several targets of one batch share one namespace | Required recovery | Submit one segment with one unsuspended coordinator Job and no sequencer, ServiceAccount, Role, RoleBinding or sequencer image. | Covered |
| S-28 | The cluster grants no sequencer RBAC or cannot run the sequencer image | Required recovery | Without `--sequencer`, `validate_env.sh` checks the sequencer RBAC, server version, and image (a short-lived Job that pulls it and runs `sh`, `kubectl`, `grep`, `sleep` and `kubectl version --client`, ending at once on an image-pull or container-config waiting reason) and reports problems only as warnings, so one-namespace use never fails because of them; with `--sequencer`, missing prerequisites are errors naming the keep-one-namespace fallback. | Covered |
| S-29 | Two namespaces of a batch use the same `claim:path`, or one group's root is nested in another group's | Required recovery | Each segment's control root is the first root of its own namespace; each cell's generated targets and read-from path are checked against its own group's roots as `NAMESPACE/CLAIM:PATH`, so a cell planning accepted runs, and a target on another namespace's root fails the cell before any benchmark I/O. A bundle without `segment.tsv` whose roots span namespaces fails before any state. | Covered |
| S-30 | Namespace or claim names whose locale collation differs from byte order (`a`, `a-b`, `ab`; `storage-test`, `storage-test-2`) | Required recovery | Claims and Leases are ordered, and the identity validated, in byte order under any locale. | Covered |
| S-31 | A valid name that plain YAML reads as a number, boolean or null (`123`, `1.5`, `yes`, `on`, `null`) | Required recovery | Every rendered manifest quotes it, so the API server receives a string. | Covered |
| S-32 | More claims than one attempt can hold (`KUBECTL_MAX_CLAIMS`, 32) | Required recovery | `kubectl_validate_test_dirs` and batch preflight reject them before any cluster or claim mutation and name the limit. | Covered |
| S-33 | `--read-from` and its `TEST_DIRS` key spell the default namespace differently | Required recovery | The launch-time check compares normalized `NAMESPACE/CLAIM:PATH` forms: accepted when they name the same claim and path, rejected for another namespace or claim. | Covered |

**Creation ambiguity horizon:** the longer of 30 seconds and
`KUBECTL_PROCESS_TIMEOUT_SECONDS` (default 30), measured from the creation
intent's modification time (refreshed before each create retry). Rolling back
an absent object waits out the horizon plus 2 seconds, then repeats the
exact-name GET before recording ambiguous absence (S-08, S-09).

**Create retry (S-17).** If `kubectl create` fails without an API verdict
(the S-10 transient classifier: process timeout, disconnect, 429, or HTTP
500/502/503/504), do an exact-name GET:

- Owned object present: adopt it after exact identity verification.
- Absent: re-send the same manifest and ownership nonce under the same intent,
  with jittered backoff, up to `KUBECTL_CREATE_ATTEMPTS` total requests
  (default 3).
- `AlreadyExists`: adopt only if the ownership nonce and run label match;
  otherwise `IDENTITY_MISMATCH`, with no delete and no retry.
- GET failure (not absence) or a permanent rejection (`Forbidden`, `Invalid`,
  quota, admission denial): stop without retry; a rejection still gets one
  exact identity verification.
- Retries exhausted: keep the intent, so S-08/S-09 rollback applies.
- A claim's Lease create is never retried: a foreign `AlreadyExists` there
  means claim contention (S-05).

### Coordinator and benchmark

| ID | Fault boundary | Class | Required result | Status |
|---|---|---|---|---|
| C-01 | Kubernetes starts a duplicate Job Pod | Required recovery | One coordinator-lock owner; duplicate exits without ledger mutation. | Covered |
| C-02 | Coordinator exits before or during startup initialization | Required recovery | Exact Job evidence converts the attempt into collectible failure while unstarted cells remain `PENDING`. | Covered |
| C-03 | Service or policy convergence is delayed | Required recovery | Retry within a fixed deadline, then publish startup failure and diagnostics. | Covered |
| C-04 | Benchmark cell exits nonzero | Required recovery | Preserve exit/evidence, stop later cells, permit collect and resume. | Covered |
| C-05 | Coordinator receives `TERM` or `INT` | Required recovery | Best-effort terminal publication; later command reconciles hard loss. | Covered |
| C-06 | Coordinator is killed or evicted during a cell | Required recovery | Lose only active scratch; preserve committed cells and recover interrupted cell. | Covered |
| C-07 | Exit during artifact, cell-state, summary, or manifest publication | Required recovery | Manifest identifies committed evidence; recovery repairs bounded gaps. | Covered |
| C-08 | Exit after terminal status but before terminal manifest | Required recovery | Repair only from a consistent durable ledger. | Covered |
| C-09 | Worker service dies during measured I/O | Required recovery | Fail the current cell without transparent benchmark retry. | Covered |
| C-10 | Worker container restart or same-Node/same-IP Pod replacement | Required recovery | Continue only after frozen semantic identity and health validate. | Covered |
| C-11 | Worker IP, Node UID, architecture, or image changes | Required recovery | Fail, collect, and resume under a new attempt. | Covered |
| C-12 | Worker DaemonSet is externally deleted | Required diagnosis | Refuse silent recreation; retain state and identify the missing exact object. | Covered |
| C-13 | PVC operation is temporarily unavailable | Required diagnosis | Fail safely, retain resources, and identify the PVC operation. | Covered |
| C-14 | PVC fills during benchmark or control publication | Required diagnosis | Report ENOSPC with exact Job/PVC evidence and the affected phase. Exact kernel-level attribution to workload versus ledger I/O is not guaranteed. | Covered |
| C-15 | PVC is permanently lost or corrupt | Unsupported | Fail closed without reconstruction. | Covered detection; automatic repair unsupported |

### Status and cancellation

| ID | Fault boundary | Class | Required result | Status |
|---|---|---|---|---|
| T-01 | Transient status API failure | Required recovery | Bounded retry; do not mutate without exact evidence. | Covered |
| T-02 | Client credentials expired | Required recovery | Report authentication and direct the user to reauthenticate and retry. | Covered locally; external acceptance pending |
| T-03 | PVC becomes terminal before Job controller convergence | Required recovery | Report terminal PVC state; collection still waits for exact quiescence. | Covered |
| T-04 | Exact Job fails or disappears while PVC is nonterminal | Required recovery | Recover coordinator loss from verified control and PVC state. | Covered |
| T-05 | Job says Complete but ledger is nonterminal | Required diagnosis | Refuse success and report both observations. | Covered |
| T-06 | User externally deletes exact Job | Required recovery | Treat as bounded coordinator loss when saved identity and PVC evidence agree. | Covered |
| T-07 | Cancel active work | Required recovery | Journal intent, delete exact Job, publish cancellation, retain collection data. | Covered |
| T-08 | Client exits during cancellation | Required recovery | Repeated `--cancel` resumes exact deletion and finalization. | Covered |
| T-09 | Status observes `CANCEL_REQUESTED` | Required recovery | Tell the user to retry `--cancel`; never report ordinary running state. | Covered |
| T-10 | Same resource name has another UID or nonce | Required diagnosis | Refuse deletion and report expected and observed identity. | Covered |
| T-11 | The sequencer is lost between segments | Required recovery | `--status` starts the next suspended Job with the UID-tested patch once every earlier Job is `Complete`. | Covered |
| T-12 | A segment fails | Required recovery | Later Jobs never start; status reports the failure and `NEXT_ACTION=COLLECT`. | Covered |
| T-13 | Worker drift on one unfinished segment | Required recovery | Stop the sequencer, journal `stopped-by-drift`, fail the current segment, abandon later segments, and permit collect and resume. | Covered |
| T-14 | A segment's coordinator is lost after its last cell committed | Required recovery | Recover its ledger to `SUCCESS`, record the segment as succeeded, and start the next segment. | Covered |
| T-15 | A segment completes, or the sequencer starts the next one, while cancellation or drift handling is under way | Required recovery | Stop the sequencer before classifying; never delete a `Complete` Job or overwrite a terminal ledger; cancel a next segment that already started; keep a segment that succeeded meanwhile; repeated `--cancel` completes. | Covered |
| T-16 | A segment completes and the next one starts between two Job observations | Required recovery | Observe segments last to first, so a consistent attempt never looks out of order. | Covered |

### Collection and resume

| ID | Fault boundary | Class | Required result | Status |
|---|---|---|---|---|
| R-01 | Collect is requested while exact Job is active | Required recovery | Refuse without publication or cleanup and print the next action. | Covered |
| R-02 | Collector cannot schedule or mount PVC | Required recovery | Preserve remote state, capture diagnostics, and permit retry. | Covered |
| R-03 | Authentication or network fails during archive stream | Required recovery | Remove partial local archive, retain remote source, and permit retry. | Covered |
| R-04 | Transfer exceeds collection deadline | Required recovery | Stop without remote cleanup and permit retry. | Covered |
| R-05 | Stream exceeds archive byte limit | Required diagnosis | Stop while receiving, delete partial local data, and preserve remote source. | Covered |
| R-06 | Received archive exceeds member limit | Required diagnosis | Stop while streaming archive metadata before extraction and preserve remote source. | Covered |
| R-07 | Archive has traversal, links, devices, or another attempt | Required diagnosis | Reject before extraction. | Covered |
| R-08 | Manifest is incomplete, conflicting, or cross-cell | Required diagnosis | Refuse publication and identify the row, cell, and path. | Covered |
| R-09 | Local receive, extraction, or merge hits ENOSPC | Required recovery | Preserve remote data, identify the local path, and permit retry after remediation. | Covered |
| R-10 | Client exits before local merge | Required recovery | Keep remote state authoritative and discard stale staging on retry. | Covered |
| R-11 | Client exits during per-file merge | Required recovery | Remove attempt-named incomplete files, accept only identical published digests, and continue. | Covered |
| R-12 | Client exits after `collected-state` during cleanup | Required recovery | Resume journaled cleanup without retransferring. | Covered |
| R-13 | Exact cleanup call fails transiently | Required recovery | Remain `COLLECTION_IN_PROGRESS`, report retained identities, and retry. | Covered |
| R-14 | Client exits after cleanup, including Lease deletion, but before its journal or `COLLECTED` | Required recovery | Status reports the publication locally; collect proves all preceding exact cleanup, reconciles only the released Lease identity, and marks collected. | Covered |
| R-15 | Collect is repeated after `COLLECTED` | Required recovery | Validate local publication without cluster credentials. | Covered |
| R-16 | Resume is requested before collection | Required recovery | Reject and print the required collect command. | Covered |
| R-17 | Concurrent resumes | Required recovery | At most one successor becomes current; reject the loser safely. | Covered |
| R-18 | Resume exits after publishing a new `PREPARED` attempt | Required recovery | Roll it back and restore the collected predecessor. | Covered |
| R-19 | Local attempt metadata or collected state is lost or corrupt | Unsupported | Refuse mutation; do not reconstruct ownership from labels. | Covered detection; automatic repair unsupported |
| R-20 | Cluster is replaced while PVC survives | Required diagnosis | Detect UID mismatch and refuse adoption or cleanup. | Covered |
| R-21 | Collect is interrupted between per-segment cleanups | Required recovery | Repeated collect resumes from the journaled per-segment and per-claim steps without retransfer. | Covered |
| R-22 | An attempt started by storage-scale-test v1.x (identity schema 2 or 3) is found | Required diagnosis | Refuse status, cancel, collect and resume without mutation, naming the schema and saying to collect the attempt with storage-scale-test v1.x. | Covered |
| R-23 | Resume of a batch spanning namespaces | Required recovery | Plan the new attempt's segments from the remaining cells; only namespaces with remaining cells get a segment, in ledger order. | Covered |
| R-24 | Several segments publish attempt-level diagnostics (`coordinator-loss.tsv`, `startup-error.txt`) | Required recovery | Import each at its own per-segment results-root path, keep every one, and let a resumed attempt supersede them. | Covered |
| R-25 | A multi-segment attempt is collected or resumed | Required recovery | Name every segment's results-root ledger files by its namespace, number status keys by segment, publish the attempt's aggregate outcome as `run.status` and `run-summary.tsv` (drift `FAILED`, user cancellation `CANCELLED`), and let a later attempt supersede both. | Covered |
| R-26 | A sealed batch resumes after a namespace or claim used only by succeeded executions was deleted | Required recovery | Preflight plans the executions that have not succeeded, as the resume submits them; it checks only their segments' claims and plans a sequencer only when they span namespaces. | Covered |
| R-27 | A segment's non-control claim is deleted while the attempt is unfinished | Required diagnosis | Status and collector helpers mount only the control claim, so they can start; the cluster identity check reports the deleted claim as `IDENTITY_MISMATCH` and nothing is adopted or cleaned up. | Covered |
| R-28 | Claim diagnostics for a claim name of up to 253 bytes, or a diagnostic file that cannot be written | Required diagnosis | Store each claim's evidence as `pvc-<N>.yaml` (N its position, its name on the first line); report a write failure on stderr without hiding it or replacing the primary error. | Covered |

### Regression evidence map

The matrix is enforced at the following layers. A `Covered` label requires an
assertion at the appropriate layer; merely reaching the branch is not evidence.

| Matrix IDs | Named primary evidence |
|---|---|
| S-01 | `test_runtime_configuration_rejects_every_invalid_field` |
| S-02, R-19 | `test_identity_is_complete_atomic_and_path_bound` |
| S-03, S-14 | `test_prepare_failure_terminalizes_only_after_successful_rollback` |
| S-04 | `test_s04_local_lifecycle_lock_rejects_a_concurrent_mutator` |
| S-05 | `test_intended_reservation_does_not_touch_competing_pvc_owner`, `test_pvc_lease_is_create_only_and_has_no_time_expiry` |
| S-06 | `test_interrupted_pvc_lease_creation_is_reconciled_by_exact_identity`, `test_pvc_lease_release_uses_uid_precondition_and_is_journaled`, `test_pvc_lease_release_clears_redundant_matching_creation_intent` |
| S-07, S-08, S-09 | `test_creation_intent_cleans_object_left_before_resource_journal`, `test_creation_intent_rechecks_absence_after_create_deadline`, `test_creation_absence_retains_possible_late_object_identity`, `test_create_only_verifies_exact_identity_before_returning_uid`, `test_delayed_pvc_lease_creation_uses_common_ambiguity_wait`, `test_creation_ambiguity_horizon_covers_kubectl_process_timeout`, `test_create_adopts_object_accepted_before_lost_response` |
| S-10, T-01 | `test_observational_calls_retry_only_transient_api_failures` |
| S-11, T-02 | `test_exhausted_observation_emits_actionable_diagnostic_envelope` |
| S-12 | `test_worker_readiness_timeout_captures_daemonset_diagnostics` |
| S-13 | `test_interrupted_bundle_upload_never_starts_job_and_rolls_back` |
| S-15 | `test_submission_prints_status_cancel_and_collect_commands` |
| S-16 | The dated external acceptance record described below; still pending |
| S-17 | `test_create_retries_absent_object_after_lost_response`, `test_create_adopts_object_accepted_before_lost_response`, `test_create_retry_adopts_own_object_on_already_exists`, `test_create_never_adopts_or_deletes_foreign_object`, `test_create_never_retries_permanent_api_rejection`, `test_create_observation_failure_is_not_absence`, `test_create_retry_exhaustion_retains_creation_intent` |
| S-18 | `test_invalid_group_root_is_rejected_before_mutation`, `test_group_roots_spanning_namespaces_are_rejected_before_mutation`, `test_kubectl_pvc_prints_the_exact_replacement` |
| S-19 | `test_exit_between_leases_is_rolled_back_by_a_later_status` |
| S-20 | `test_competitor_on_a_later_lease_releases_only_earlier_leases` |
| S-21 | `test_unready_target_rolls_back_both_namespaces_and_leases_in_reverse` |
| S-22 | `test_aliased_claims_fail_at_the_second_run_tree_reservation`, `test_reservation_script_reports_a_run_tree_reached_through_another_claim` |
| S-23 | `test_sequencer_probe_failure_is_an_error_with_the_fallback`, `test_sequencer_rbac_denial_rolls_back_every_namespace`, `test_probe_job_runs_the_real_sequencer_against_absent_jobs`, `test_probe_lost_create_response_is_cleaned_up_by_name`, `test_probe_never_deletes_a_foreign_object_of_its_name`, `test_probe_signal_mid_wait_still_deletes_every_object`, `test_probe_tolerates_transient_observation_failures`, `test_probe_exercises_a_cross_namespace_role_binding` |
| S-24 | `test_policy_create_failure_rolls_back_through_transfer_helpers` |
| S-25 | `test_sequencer_creation_intent_is_reconciled_by_rollback_and_collect` |
| S-26 | `test_claims_in_one_namespace_are_one_segment_that_mounts_every_claim` |
| S-27 | `test_one_namespace_batch_has_one_segment_and_no_sequencer` |
| S-28 | `test_default_sequencer_checks_only_warn_and_never_fail`, `test_image_check_fails_fast_on_a_fatal_waiting_reason`, `test_image_check_passes_and_deletes_its_job`, `test_sequencer_prerequisite_failures_are_errors_with_the_fallback` |
| S-29 | `test_mdtest_cell_checks_targets_against_its_own_namespace_roots`, `test_mdtest_cell_rejects_a_target_on_another_namespaces_root`, `test_read_from_is_checked_against_its_own_groups_roots`, `test_segment_control_root_is_chosen_from_its_own_namespace`, `test_bundle_without_segment_row_refuses_roots_spanning_namespaces` |
| S-30 | `test_identity_claim_order_is_byte_order_in_every_locale` |
| S-31 | `test_ambiguous_names_render_as_yaml_strings_in_helper_pods`, `test_ambiguous_names_render_as_yaml_strings_in_workloads` |
| S-32 | `test_validate_rejects_more_claims_than_one_attempt_mounts`, `test_kubectl_batch_preflight_rejects_more_claims_than_one_attempt_mounts` |
| S-33 | `test_kubectl_read_from_compares_normalized_claim_paths` |
| C-01 | `test_duplicate_coordinator_cannot_mutate_an_owned_attempt` |
| C-02 | `test_pre_running_crash_boundaries_recover_to_collectable_failure` |
| C-03 | `test_startup_endpoint_failure_publishes_a_collectible_terminal_ledger` |
| C-04 | `test_failure_overlay_preserves_first_failure_and_stops_later_cells` |
| C-05 | `test_signal_publishes_terminal_failure_without_erasing_scratch_evidence` |
| C-06 | `test_lost_coordinator_recovery_publishes_failed_running_cell` |
| C-07 | `test_crash_boundaries_never_advertise_uncommitted_terminal_cells` |
| C-08 | `test_lost_coordinator_repairs_terminal_status_manifest_window` |
| C-09 | `test_worker_service_failure_stops_current_cell_without_retry` |
| C-10 | `test_worker_endpoint_comparison_reports_replacement_and_ip_drift` |
| C-11 | `test_worker_endpoint_comparison_checks_all_frozen_identity_fields` |
| C-12, T-10 | `test_missing_worker_daemonset_emits_identity_diagnostics` |
| C-13 | `test_control_state_diagnostics_use_guarded_bounded_pvc_reads` |
| C-14 | `test_remote_pvc_enospc_has_distinct_diagnostics` |
| C-15 | `test_c15_permanent_pvc_loss_is_detected_without_adoption` |
| T-03 | `test_terminal_job_evidence_preserves_empty_active_field` |
| T-04, T-06 | `test_public_status_recovers_coordinator_loss_before_running` |
| T-05 | `test_completed_job_with_nonterminal_ledger_is_diagnosed` |
| T-07 | `test_cancel_recovery_publishes_collectable_terminal_ledger`, `test_finalize_cancelled_converts_the_failure_its_job_deletion_caused` |
| T-08 | `test_cancel_retries_after_job_delete_was_already_journaled`, `test_interrupted_multi_target_cancel_completes_when_repeated` |
| T-09 | `test_status_reports_incomplete_cancellation_as_retryable_failure`, `test_cancel_requested_status_names_the_segment_being_cancelled` |
| T-11 | `test_status_restarts_a_lost_sequencers_next_segment` |
| T-12 | `test_failed_segment_permits_collect_and_never_starts_later_targets` |
| T-13 | `test_drift_in_a_later_target_fails_the_attempt` |
| T-14 | `test_status_continues_after_a_segment_recovered_to_success` |
| T-15 | `test_cancel_keeps_a_segment_that_completed_before_its_deletion`, `test_cancel_keeps_success_published_while_the_job_was_deleted`, `test_cancel_also_cancels_a_segment_the_sequencer_started_first`, `test_drift_handling_keeps_a_segment_that_completed_meanwhile`, `test_single_target_cancel_keeps_a_job_that_completed_first`, `test_finalize_cancelled_never_overwrites_a_terminal_outcome` |
| T-16 | `test_segment_classification_observes_later_segments_first` |
| R-01 | `test_collect_active_attempt_reports_terminal_gate_and_next_action` |
| R-02 | `test_helper_template_is_rendered_and_removed_when_readiness_fails` |
| R-03, R-04, R-05 | `test_collection_stream_uses_its_operation_sized_deadline`, `test_collection_stream_failure_removes_partial_and_reports_auth`, `test_collection_retries_transient_transfer_and_publishes_complete_results`, `test_collection_never_retries_permanent_or_unknown_remote_errors`, `test_collection_retry_limit_keeps_bounded_error_history`, `test_collection_retries_share_one_deadline`, `test_collection_byte_limit_is_enforced_while_streaming`, `test_collection_changed_source_exhaustion_preserves_remote_data` |
| R-06, R-07, R-08 | `test_collection_archive_metadata_is_streamed_and_member_bounded`, `test_hostile_collection_archives_never_extract`, `test_collected_manifest_rejects_duplicate_semantic_rows`, `test_collected_manifest_requires_complete_terminal_evidence`, `test_collected_manifest_rejects_cross_execution_workload_substitution`, `test_changed_source_retry_still_rejects_content_corruption` |
| R-09, R-10, R-11 | `test_collection_capacity_checks_the_results_filesystem`, `test_collection_scavenges_only_owned_staging_paths`, `test_collection_merges_manifest_declared_execution_ledgers`, `test_collection_classifies_parent_creation_failure_as_local_io` |
| R-12, R-13 | `test_collection_recovery_retries_every_cleanup_stage` |
| R-14 | `test_status_projects_published_collection_after_remote_cleanup`, `test_collection_recovers_lease_delete_before_release_journal`, `test_collection_does_not_reconcile_lease_before_exact_cleanup` |
| R-15 | `test_collected_terminal_status_is_a_successful_query` |
| R-16 | `test_resume_before_collection_prints_exact_collect_command` |
| R-17 | `test_stale_resume_contender_cannot_replace_successful_attempt` |
| R-18 | `test_clean_failed_resume_restores_collected_predecessor_pointer` |
| R-20 | `test_r20_cluster_uid_mismatch_emits_structured_diagnosis` |
| R-21 | `test_collect_interrupted_between_per_target_cleanups_resumes` |
| R-22 | `test_v1_attempt_is_refused_with_the_collect_with_v1_message` |
| R-23 | `test_resume_plans_segments_only_for_namespaces_with_remaining_cells` |
| R-24 | `test_lost_coordinators_in_two_segments_collect_with_both_diagnostics`, `test_resume_after_two_lost_coordinators_reruns_and_merges_cleanly` |
| R-25 | `test_resume_plans_segments_from_the_namespaces_that_still_have_cells`, `test_collect_publishes_namespace_named_ledgers_and_the_aggregate`, `test_aggregate_outcome_of_a_cancelled_attempt_with_an_abandoned_segment` |
| R-26 | `test_kubectl_batch_preflight_checks_only_the_namespaces_still_to_run` |
| R-27 | `test_status_and_collector_helpers_mount_only_the_control_claim` |
| R-28 | `test_pvc_diagnostics_name_files_by_position_and_report_write_failures` |

Real tests validate cross-component behavior without reproducing every fast
branch. A matrix row may say `Covered` only while a focused assertion exercises
its decision boundary; new rows must add named evidence. Unsupported rows need
detection tests where the condition can be created safely, not recovery tests.

## Diagnostic contract

Every failure at a supported matrix boundary must identify, when known:

```text
operation, phase, attempt ID, last proven local state,
last proven remote state, exact Job evidence, normalized reason,
resource kind/name/namespace, expected and observed UID,
local and remote state paths, whether work may still be running,
and the next safe action
```

Normalized reasons are `AUTH`, `TIMEOUT`, `API_THROTTLED`,
`API_UNAVAILABLE`, `TRANSFER_FAILED`, `IDENTITY_MISMATCH`, `POD_UNSCHEDULABLE`, `IMAGE_PULL`,
`PVC_MOUNT`, `PVC_IO`, `ENOSPC`, `LOCAL_IO`, `PATH_REJECTED`,
`INSUFFICIENT_CAPACITY`, `ARCHIVE_INVALID`,
`LEDGER_INCONSISTENT`, `OWNERSHIP_AMBIGUOUS`, and
`CANCELLATION_INCOMPLETE`. `INVALID_LIFECYCLE_OPERATION` identifies a valid
request made from a state in which that operation is not legal; its diagnostic
must print the exact prerequisite command or next lifecycle action.
`TRANSFER_FAILED` identifies an unrecognized or remote-command transfer
failure; it does not claim an API outage. Collection retries positively
identified transient transport failures or tar's isolated changed-source
warning, making up to three attempts with backoff
within one transfer deadline (plus the timeout tool's five-second kill
grace). `KUBECTL_COLLECTION_TIMEOUT_SECONDS` (default 7200) is the total
deadline. Until a producer times out, each transfer is capped at
`KUBECTL_COLLECTION_ATTEMPT_TIMEOUT_SECONDS` (default one third of the total);
the following transfer may use the remaining deadline. Authentication,
identity, path, local-storage, archive-integrity,
and unknown failures remain fatal. Each failed transfer preserves bounded
stderr and producer/consumer status in local attempt diagnostics, including
when a later transfer succeeds; partial archives are discarded between tries.
Only the published `state/` subtree is transferred; uploaded control files
remain available locally. Changed-source warnings are never ignored: a retry
must finish cleanly and pass the same manifest hashes before publication.
Persistent changes and other tar errors remain fatal with remote data retained.

Control upload verifies a private staged archive and publishes only a
complete bundle. Transient transport failures get up to three attempts, each
bounded by `KUBECTL_CONTROL_UPLOAD_TIMEOUT_SECONDS` (default 120); a lost
acknowledgement is accepted only if the published files are byte-identical.
Auth, checksum, and other remote errors are fatal. Worker health checks probe
each endpoint up to three times; persistent failure fails the current cell, and
measured phases are never replayed.

For required-recovery faults, capture bounded Job, Pod, and DaemonSet
descriptions; relevant container logs and namespace events; durable PVC state;
the publication manifest; and exact retained resource identities. A failed
coordinator Job's log (its last 16 MiB) is saved once per segment as
`coordinator[-s<K>].log` in the attempt metadata. Store the
schema-versioned, bounded diagnostic bundle in the attempt's local Kubernetes
metadata, not in
the benchmark result/reporting contract. If diagnostic capture fails, retain
the primary error, continue safe cleanup, print copy-pasteable inspection
commands, and state whether data and resources were retained.

## Unsupported situations

The initial contract explicitly excludes:

- cooperative execution of concurrent mutating lifecycle commands;
- more than one active sweep on one PVC;
- automatic retry of a failed cell within the same attempt;
- transparent worker, endpoint, node, architecture, or image retargeting;
- automatic Kubernetes credential renewal or Teleport login;
- preservation of active-cell `emptyDir` scratch after hard Pod or node loss;
- automatic adoption after API-create visibility exceeds the ambiguity horizon;
- reconstruction after local attempt metadata loss or corruption;
- recovery after permanent PVC loss or corruption;
- recovery after namespace, PV, or PVC UID replacement;
- power-loss durability beyond the atomic-rename guarantees of the filesystems;
- malicious mutation of trusted local snapshots or PVC state;
- a compromised administrator, CNI, admission controller, service mesh, or
  storage driver that violates validated prerequisites;
- namespace policy that rejects the `Unconfined` seccomp profile required by
  Elbencho validation, worker, and coordinator Pods;
- IPv6-only networking, heterogeneous selected architectures, set-based node
  selectors, and Kubernetes delete-only.

Unsupported does not mean silent. Detectable violations fail closed and name
the violated prerequisite or invariant.

## External credential-expiry acceptance

Run this gate on a representative Teleport-mediated cluster using its real RWX
claim. It cannot be replaced by kind or fake-`kubectl` coverage.

1. Record cluster, namespace, PV, and PVC UIDs and the active Teleport session
   expiry. Preserve the invocation, tool version, image digest, and node/CNI
   facts with the test evidence.
2. Submit `baseline`, wait for durable `RUNNING`, and let the original client
   credential expire without touching the Job.
3. Prove the Job continues and reaches a durable terminal state while the
   submitting shell can no longer query the API.
4. From the expired shell, run status and collection. Require `AUTH`, the saved
   attempt identity, `may_still_be_running=unknown`, and an exact
   reauthentication-and-retry action; neither command may mutate local or
   remote state.
5. Reauthenticate in a new shell, rerun status and collection, validate the
   ordinary result/report contract, and prove exact resource cleanup.
6. Repeat credential expiry during a running cancellation and during archive
   collection. Reauthenticate and prove that repeated `--cancel` and
   `--collect` finish the journaled operations without unrelated deletion or
   retransferring verified publication.
7. Run `failure-resume`, `kubectl-cancel`, and
   `kubectl-coordinator-loss`; require the same recovery semantics established
   by the real fixture.
8. Point the saved results directory at credentials for a different cluster
   exposing the same object names. Namespace/PV/PVC UID validation must reject
   it before mutation.
9. Confirm that no namespace, PV, PVC, unrelated workload, retained benchmark
   dataset, or unrelated NetworkPolicy was changed.

Record this gate by date and environment in the release or PR evidence. Do not
claim the external acceptance criterion from simulated token expiry alone.

## Closure criteria

Lifecycle hardening is complete when:

1. The three authoritative state machines and exact transitions above are
   normative.
2. Fast tests execute every legal local edge and reject every other state pair.
3. The fault boundaries in this matrix are frozen.
4. Every required-recovery row has named before/after fault evidence proving no false
   success, unrelated deletion, hidden active attempt, or unrecoverable retry
   state, and proving eventual completion or collectible failure.
5. Every required-diagnosis row verifies its normalized reason and next action.
6. Real fixtures cover baseline, benchmark failure/resume, cancel, coordinator
   loss, endpoint drift, and interrupted collection.
7. External acceptance covers real credential expiry and the representative
   CNI/RWX environment.
8. No open defect violates an invariant or supported matrix row.
9. One final adversarial review is performed against this frozen contract.

Findings outside this contract become backlog or explicit design proposals;
they do not silently extend the release boundary.

As of 2026-10-12, repository-controlled criteria 1–6 and 8 have focused test
evidence, and the complete Docker SBX lifecycle passes every SSH, Slurm, and
kubectl scenario. Criterion 7 requires the real Teleport-mediated CNI/RWX
environment. Criterion 9 is the final review after that external gate.
