# Local retention planning

The retention tools inventory local ledger metadata and return a review plan for copying selected records into an archive. They do not copy, move, delete, restore or release anything. No retention executor, automatic TTL cleanup, cloud cleanup or hold-release API is provided. Every inventory and plan reports `archive_execution_supported: false` and `removal_eligible: false`.

This is a bounded step toward the implementation plan's retention controls, not completion of enterprise retention, legal discovery, residency or compliance obligations. Customer retention owners choose actual periods and holds. The plugin supplies no compliance periods or certification.

## Trusted owner configuration

The trusted profile may contain `retention.policy` and `retention.holds`. These are not MCP arguments. Editing an engineering name, provider response, plan result or tool request cannot establish an owner policy or release a hold. `ownerRef`, `policyRef` and `evidenceRef` identify the owner's records; those strings do not authenticate an otherwise untrusted caller.

`retention.policy` has this strict shape:

| Field | Meaning |
| --- | --- |
| `version` | `1` |
| `ownerRef` | Bounded owner reference |
| `policyRef` | Bounded customer policy reference |
| `periods.expiredPreparationMs` | Optional owner-selected duration after an unattempted desktop preparation expires |
| `periods.terminalEvidenceMs` | Optional owner-selected duration after a supported final evidence timestamp |
| `periods.auditMs` | Optional owner-selected duration after an audit event's recorded time |

Durations are nonnegative safe integers in milliseconds. There are no defaults. Omitting a class's period protects that class. A zero duration is an explicit owner choice, not a recommendation. A successful or failed operation is not aged from its creation time or filesystem modification time as though that were its completion time.

`retention.holds` has `version: 1`, `ownerRef`, `evidenceRef`, `reviewedAt`, `expiresAt`, `complete` and `holds`. Times must be canonical UTC ISO strings with milliseconds. Candidate analysis requires `reviewedAt <= now < expiresAt` and `complete: true`, checked after the filesystem snapshot finishes. Hold information that expires during observation blocks candidates and plan preparation. This validity interval is the owner's explicit freshness interval for hold information, not a legal retention period.

Each hold has a unique bounded `id`, a `reason`, and either `scope: "profile"` or `scope: "records"` with unique `recordRefs` from an inventory. `complete: true` with `holds: []` is an explicit trusted observation of no holds. Missing, expired, future or incomplete hold information blocks candidates. An unresolved hold reference also makes dependency coverage incomplete. Known holds remain protective even when their snapshot is no longer fresh; expiry never releases them.

## Tool workflow

1. The profile owner supplies appropriate policy and a complete current holds snapshot through trusted configuration.
2. Call `fusion_retention_inventory`. It accepts no paths, periods, approval flags or provider credentials. Review `complete`, `inventory_complete`, `dependency_coverage_complete`, `issues`, counts and each entry's reasons.
3. Call `fusion_retention_prepare` with the returned `inventory_hash` and explicitly selected `record_refs`. The tool inventories again, checks the same source/policy/holds binding, and includes the complete dependency group. Any protected, held, unknown, missing or changed member blocks selection.
4. Review or retain the returned JSON through an independently authorized process. There is no execution step. The tool does not persist a plan or audit record in the inspected state root.

References have the form `entry:<SHA256>`. They are opaque references to inventory entries, not filesystem paths. The content-derived plan ID and hash bind source record byte hashes, dependency references, age anchors, selected periods, profile/execution-contract identity and trusted policy/holds hashes. A hash establishes content consistency, not an owner signature, WORM storage or future execution authority. `verifyRetentionPlan` checks static shape and content binding only.

## Scope and incomplete observations

The scope is `local_ledger_metadata_only`, not current provider state. The snapshot reads only recognized top-level JSON records in the profile's existing local state root. It neither initializes a missing directory nor repairs permissions. Credential-lock subtrees are excluded without enumeration. Native/private subtrees, unknown records, links, malformed JSON, unavailable files and unexpected file types are not followed or treated as removable. Unknown payloads, credential contents and unrestricted cached engineering text are never returned through the retention tools.

This absence-preserving guarantee applies to the retention methods themselves. Ordinary MCP/CLI runtime startup calls `engine.init()` first and can create an absent state root, including fixture state in fixture mode. Launching the server is therefore not an absence-preserving filesystem inspection. Once the runtime is initialized, retention inventory and preparation do not create records, repair permissions or initialize a subsequently missing ledger.

Artifact output files and directories, cloud staging, external caches and support bundles are outside this inventory. Their absence from a result does not mean they are empty, retained correctly or safe to remove. Unexpected directories or files can make the local observation incomplete. This implementation does not satisfy complete cross-system deletion obligations.

The planner reads at most 1,000 top-level entries and 64 MiB of record bytes per ordinary inventory, with a 16 MiB per-record ceiling and a 30-second observation budget. The time budget is checked between filesystem operations and does not preempt a pending filesystem or ACL check. The storage seam supports bounded lower or host-selected technical limits. A review plan contains at most 250 records after dependency closure. Limits protect the observation process; they are not retention periods. Exhaustion stays explicit and cannot convert the observed subset into a complete safe selection.

`total_entry_count` is null when a complete count cannot be established. `entry_count_lower_bound` and `unrepresented_entry_count_lower_bound` expose observed entries not represented in the returned metadata. Classification counts describe returned entries only. An empty entry list with `complete: false` never proves an empty state root.

The snapshot checks file privacy, regular-file/link identity, bounded reads, directory membership and unchanged identities. It preserves existing Windows private-storage ACL and identity checks without repermissioning files. Detected changes or an execution lock make the observation incomplete. This is not a filesystem transaction or a lock over future activity. Any future collector would need new source and authority checks before acting.

Optional document read restrictions also apply to cached records. Out-of-scope or unproven source groups expose opaque protected placeholders, not stored engineering payloads. Historical profile or execution-contract mismatches are preserved with explicit protection rather than silently grandfathered into current authority.

## Records that remain protected

| Records or evidence | Treatment |
| --- | --- |
| Executing, submitting, pending, running, validating, cancellation requested or unknown operations | Retained as unresolved work |
| Failed partial/unknown effects or incomplete post-operation validation | Retained pending reconciliation; a `failed` status is not proof of no effect |
| Desktop plans without a durable terminal timestamp | No invented completion date; terminal evidence remains protected |
| Idempotency records and their plans/jobs | Retained for replay protection and result lookup |
| Created-document records and producing plans | Retained for current document authority |
| Desktop job ownership records | Retained with their producer/artifact dependencies |
| Cloud jobs, including settled terminal jobs | Retained for ownership and budget accounting; current-period spending/submission counts must not disappear |
| Cloud batch manifests, children, replay records and conflict fences | Protected as a dependency group; missing materialization and uncertain validation remain visible |
| Incomplete or quarantined artifacts | Retained; no completion is inferred from available-looking files |
| Completed artifact manifests | Existing v1/v2 hashes are checked as stored metadata; no output-byte read or validation-grade upgrade occurs |
| Qualification reports with remaining documents, jobs, failed cleanup or missing receipts | Retained pending reconciliation |
| Current engineering handoff drafts | Hash-checked source/plan/artifact references remain protected; creating a package does not complete review or release |
| Fusion Manage review drafts and their preparation audits | Exact stored bindings are checked without provider reads; expiry never makes the draft removable, and caller source references are not interpreted as verified ledger dependencies |
| Unknown future handoff, batch or retention schemas | Protected with incomplete dependency coverage; no disposal semantics are guessed |
| Locks, temporary records, fixture state and credential fences | Never age-deleted by this planner |

Dependency selection includes both the retained dependent and its referenced evidence. A held or operationally necessary member protects the whole connected group. Thus an otherwise old audit or artifact record can remain protected because its producer or replay receipt is still needed. References are read from reviewed typed fields; arbitrary text is not interpreted as a dependency or an instruction.

Read-only qualification reports may provide final timestamps for their hash-bound result receipts when their cleanup is complete. These are local evidence facts, not a new Autodesk, engineering or manufacturing qualification. A copied historical receipt would retain its original limitations and unresolved review requirements.

## Validation boundary

Focused tests use temporary test-owned ledgers and synthetic cached records. They cover missing/stale owner information, transitive holds, replay/accounting dependencies, unknown and changing inventories, source scope, strict plan hashes, versioned artifact/handoff metadata and absence of planner writes. They do not inspect a user's vault or invoke Autodesk, cloud cleanup, model services or archival execution. Current platform evidence must be reported separately; implemented Windows checks alone do not establish Windows qualification.
