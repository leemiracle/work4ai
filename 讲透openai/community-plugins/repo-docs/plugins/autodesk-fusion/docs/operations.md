# Operations, recovery and retention

Keep a private state root per administered profile and approved private artifact roots. Store profiles outside untrusted project content. Files are bounded JSON with opaque IDs; journals and manifests contain engineering metadata, so enterprise retention/DLP policy still applies even when tokens are redacted.

## Common states

| State/error | Next action |
| --- | --- |
| `DESKTOP_NOT_CONFIGURED`, native unavailable, pairing mismatch | Inspect the chosen endpoint, running Fusion process, selected provider and exact package/handler hash. Do not scan/fallback or disable pairing checks. |
| Busy UI/background work | Finish the actual command or wait for the reported job; do not terminate the user's command. |
| Stale state, configuration or asset | Reinspect, assess intervening edits and prepare a new plan within authority. Old hashes are not updated in place. |
| `pending` / `validating` | Poll the durable job; defer artifact completion until the actual provider result and required output checks. |
| `partial` / `outcome_unknown` / interrupted intent | Inspect the original plan, current model/provider job and staged outputs. Retain idempotency/budget records. Never resubmit to make the status look successful. |
| Execution lease held | Another process may be active. `fusionctl recover-lock` removes a lock only after proving its local PID stopped. This does not establish the operation outcome. |
| Credential refresh intent interrupted | Reauthorize through the correct provider owner. Do not replay a possibly rotated refresh token or copy tokens into a file. |
| Provider job succeeded but no validator | Install/qualify the trusted output-validation integration; processing success remains separate from engineering success. |
| Billing unknown or reservation exhausted | Reconcile through final trusted billing evidence. Cancel requests do not imply zero charge or free the reservation. |
| Missing/unknown feature or API representation | Treat as a capability/qualification gap. Do not use arbitrary reflection or silently downgrade an engineering requirement. |
| Batch validation intent or output-identity conflict | Inspect the exact batch and implicated child receipts. Preserve the fence and reservations; do not resume other variants or rerun validation to erase an unknown/colliding result. |
| Handoff source/producer/artifact changed | Inspect the original draft and current evidence. Prepare a new draft when authorized; do not rewrite old checks or infer reviewer approval. |
| Incomplete retention inventory or stale holds | Obtain a complete current owner observation and resolve scope/dependency/record problems. A partial inventory never authorizes cleanup. |

Read-only status and inspection are bounded. Retry/backoff applies only to qualified safe cloud reads; a submitted write is not blindly replayed on token errors, rate limits, disconnects, schema continuation or timeout. Profile grants expire and profile/module/handler changes invalidate preparation. Restart deliberately after a deployment change.

## Recovery

Use `fusion_changes_inspect`, `fusion_job_status`, `fusion_artifact_inspect` and `fusion_recovery_prepare` to reconstruct evidence. A compensating parameter/feature edit is a new operation against current state. Native undo, saved versions, external records and asynchronous jobs do not form one distributed transaction. Never discard unrelated unsaved work to recover a failed test.

A disabled mutation policy prevents new execution but does not revoke an existing external artifact, cancel an unsupported job or undo a posted candidate. If secrets or a workstation are compromised, use the authorization owner's revocation and host incident process; plugin profile changes alone cannot secure other clients under the same OS user.

## Retention and uninstall

Preserve unresolved plans, execution intents, job ownership, idempotency keys, credential-rotation fences, batch conflicts and budget exposure until reconciliation. Do not use broad directory deletion or automatic TTL cleanup to erase an uncertain operation. Archive completed evidence according to project policy, preserving hashes and source/contract references. Automatic destructive retention is intentionally not enabled in this implementation; an enterprise retention adapter must prove terminal-state selection and meet legal/project obligations before deletion.

Use `fusion_retention_inventory` for bounded existing-ledger metadata and `fusion_retention_prepare` for a dependency-complete copy-review plan. Trusted owner periods and complete unexpired holds come from profile configuration, never the model request. The retention methods are read-only: no absent-root creation, audit/plan persistence, archive copy, move or deletion. Normal MCP/CLI startup initializes the runtime first and can create its state root; the methods' absence-preserving guarantee does not apply to launching the server. Keep the returned JSON through an independently authorized process if needed. See [retention planning](retention.md) for scope, limits, protected records and the missing cross-system executor boundary.

Revoke direct APS authorization with the CLI or the enterprise owner; stop the Fusion add-in in the Scripts and Add-Ins UI; remove only its installed directory and profile-specific pairing/configuration. Removing the Codex plugin does not uninstall Fusion, delete CAD files, revoke unrelated Data MCP grants or stop Autodesk's separate native MCP server. Preserve or deliberately archive plugin state/artifacts rather than silently erasing them.

Use signed/notarized deployment and host controls where required. Native credential modules come from the included patched source and pinned lock/toolchain, with individual target receipts and collected dependency notices. The [native build guide](native-builds.md) describes admission and its limits. Current installed-OS/service behavior must be qualified independently. A source/runtime checksum is useful for drift and audit but is not a publisher signature or a compliance certification.

If credential removal returns `CREDENTIAL_CLEANUP_INCOMPLETE`, preserve the private state directory and retry after restoring vault access. Nonsecret generation receipts identify unfinished cleanup without containing tokens. Do not remove those receipts to make logout appear successful. Provider revocation and verified local deletion are distinct outcomes; old-generation cleanup after a successful new grant must not invalidate that new grant.
