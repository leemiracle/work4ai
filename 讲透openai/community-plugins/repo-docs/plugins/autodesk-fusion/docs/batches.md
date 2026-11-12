# Bounded cloud batches

The W10 batch coordinator prepares and resumes explicit parameter variants of one installed, reviewed Fusion Automation recipe. Each variant maps to one durable single-variant job. It uses the same scoped authorization, source/activity checks, submission ledger, rate limiter and admission budget as an individual cloud job.

This is local orchestration and protocol coverage. Synthetic tests do not run Fusion, validate engineering output, establish paid service access or verify Autodesk billing. No example Automation recipe is enabled by this feature. Production use still requires the deployment's reviewed executable recipe, publisher/activity binding, authorization path, trusted stager, output validators, billing reconciliation and live qualification.

## Prepare and review the entire request

`fusion_cloud_batch_prepare` accepts these exact fields:

```json
{
  "request_key": "configured-order-2026-001",
  "recipe_id": "YOUR_INSTALLED_REVIEWED_RECIPE",
  "context": {
    "tenantId": "YOUR_CONFIGURED_TENANT",
    "sources": [],
    "destinationAlias": "YOUR_APPROVED_STAGING_ALIAS"
  },
  "variants": [
    { "variant_id": "small", "inputs": { "widthMm": 40 } },
    { "variant_id": "large", "inputs": { "widthMm": 60 } }
  ]
}
```

This is a schema example, not an executable or qualified recipe. Input names, types, enumerations and bounds come from the installed recipe. An empty source list is valid only for recipes that require no existing design. Otherwise supply every frozen source's `hubId`, `projectId`, `itemId`, `versionId`, `configurationId` and exact `resourceHash` as required by the existing Automation contract. The reviewed recipe and account must authorize those sources. The batch layer never substitutes the active desktop design, a latest-version name match or another account's source.

There must be 1–100 unique `variant_id` values, each matching `[A-Za-z0-9][A-Za-z0-9._-]{0,63}`. The whole count must also fit the installed recipe's `maxVariants`. Values are scalar strings, finite numbers or booleans; all inputs still pass the recipe validator. A batch has one common recipe, frozen source context and staging destination. Every prepared child has `variantCount: 1`; the caller cannot add a hidden multiplier. `requireHardCap`, `requireImmutableEngine` and `requireImmutableDependencies` are optional booleans in `context`, with their existing provider requirements unchanged.

The complete input is bounded to 2 MiB and the normal JSON structural limits. The resulting internal manifest is bounded to 4 MiB and those same structural limits, so a large repeated source graph can reach the bound before 100 variants. An oversized or malformed request fails without submitting work.

All variants complete `Automation.prepare` before a manifest or child ledger is created. Preparation checks parameter rules, exact source versions and hashes, activity/dependency bindings and destination eligibility. The coordinator additionally verifies that the returned prepared records match the requested inputs/context, each has a distinct request identity, and all use the same recipe version/hash, activity definition/dependencies and destination. A bad late variant consumes no workitem. Provider reads used during preparation can still consume API quota; preparation is not a promise of free cloud requests.

Only approved `object_storage` destinations are accepted. A Fusion project destination, CAD save or ERP publication is not part of this batch contract. The existing trusted transfer service receives each distinct prepared request ID and must isolate its staged output keys. The current Automation interface exposes a destination origin/prefix, but not a final output key before submission; the coordinator cannot prove key isolation in advance. This remains a stager and deployment qualification requirement. When trusted output receipts expose artifact IDs, an ID cannot be reused by another variant in the same batch. Identical content hashes under distinct artifact identities can be legitimate results.

An observed artifact-ID collision creates a permanent `cloudbatchconflict` receipt before the validator returns an error. Its deterministic ID is the owning batch ID, and its hash binds that batch's original plan/request, each involved child plan, the candidate/prior validation hashes, and bounded artifact/job identities. The original batch plan and validation receipts are retained. Involved job views become failed with `validation_usable: false` and `validation_disposition: historical_conflicted`; a cached passed validator receipt is historical evidence, not current acceptance. The whole batch is blocked from further submissions, including after restart. Subsequent provider success, changed validator output, or billing settlement cannot clear this fence. There is no clearing/reconciliation API: preserve the evidence and use an owner-reviewed reconciliation process before considering a separately scoped business request. Do not edit/delete a fence or invent replacement request keys to bypass it.

The response includes the batch `id`, immutable `plan_hash`, every ordered variant-to-job mapping, bounded requested-input/context projections, recipe version/hash, destination, expiry and aggregate admission estimate. Large input/context fields are explicitly omitted with exact hashes/counts and a job ID for the full stored request; they are never silently truncated. Review the full referenced inputs when omitted before resuming. Neither `approved: true` nor a caller-supplied receipt, account, cost amount, script, URL or success flag grants authority. The MCP schemas reject unsupported top-level fields.

## Durable identity and crash recovery

`request_key` is a safe 8–160 character business request key. Repeating the same key for the same profile and unchanged ordered request returns the existing batch, including across process restarts. Changing parameters, source context, variant identity or order under that key fails with `IDEMPOTENCY_CONFLICT`. A new key is a new business request and can produce new work; callers must not invent a replacement key to get around an unresolved earlier request.

The `cloudbatch` record contains the request-key hash, exact request/hash, immutable initial child records, stable child idempotency keys, profile/scope/account binding, budget period and expiry. Its ID is derived from the profile and request-key hash, so there is no separate batch-key record whose absence could create another batch after a crash. Each child has a `batch` owner binding containing `batch_id`, `variant_id` and `request_hash`; the child plan hash includes this binding. Existing individual jobs without a batch owner retain their prior hash format.

After whole-batch validation, one atomic manifest write records all initial child plans with `phase: materializing`. The coordinator writes those children under the shared execution lease, then records `phase: ready`. The phase is mutable progress and is excluded from the immutable plan hash. No submission path accepts a batch child before the ready fence. Standalone `fusion_cloud_job_submit` also rejects a ready batch's children; use the batch resume tool.

A crashed materialization can resume only after every existing child is still exactly its original unattempted prepared record. Missing children can then be created from their frozen records without preparing new provider requests. An attempted or changed child in an unsealed manifest blocks this recovery. Once the manifest is ready, a missing child is damaged-ledger evidence: it is never recreated, because a previous submission cannot be excluded. Do not delete a ledger file, change a phase or rewrite a hash to bypass this fence.

Hashes detect changed records within the private host ledger. They are not authentication against the local host owner and are not tamper-proof storage. There is no cross-service transaction or whole-batch rollback guarantee.

## Bounded explicit resume

`fusion_cloud_batch_resume` accepts only:

```json
{
  "batch_id": "THE_RETURNED_BATCH_ID",
  "plan_hash": "THE_RETURNED_64_CHARACTER_PLAN_HASH",
  "max_submissions": 2
}
```

`max_submissions` must be 1–100. One call processes at most that many unattempted children, sequentially, in the original request order. It does not start a worker loop, poll until completion, wait for a slot, increase policy limits or schedule another call. Another explicit resume call may advance remaining variants; it never duplicates the already attempted ones.

The coordinator checks every remaining local prepared child's integrity, profile and expiry before the first submission in a wave. The existing Automation submission path then rechecks the current recipe/activity, immutable source dependencies, delegated grant requirements and trusted host authority for each child before dispatch. A source or service change after an earlier child completed cannot roll that child back; it can block later children. Expired plans are not silently refreshed or replaced. Prepare and review a new explicitly scoped request only after reconciling the original batch, excluding any previously attempted variants unless new work is actually intended.

Before each workitem, the existing queue and cross-process profile lease serialize the admission check and durable intent. Global concurrency, total period submissions and cost exposure include other individual jobs and batches. The full estimated batch cost and submission count must fit the current budget when initially prepared, but preparation reserves no capacity. Other work, unresolved earlier-period exposure or reconciled actual-cost overruns can therefore block a later wave. Unknown work retains its reservation, and provider output validation does not settle billing. A provider-enforced ceiling is counted in full for each child; an estimated reservation is not an actual billing ceiling.

The result's `wave.attempted_variant_ids` lists children whose ledger records crossed into an attempted state. `wave.admission_blocked` reports why the wave stopped. A policy or budget rejection before intent leaves a child `prepared`, with no submission flag or cost reservation. A known no-effect attempt remains `failed` and is never retried; a later explicit resume can process other unattempted children. An `outcome_unknown` child blocks further batch admissions pending reconciliation. A leftover `submitting` intent is durably converted to `outcome_unknown` without another provider submit. Failure to save a provider response retains the same intent/reservation fence.

An inconsistent provider ID that belongs to another ledger job also becomes uncertain; the conflicting ID is not assigned to the new child or polled as though it belonged to that variant. A failed or uncertain attempt ends the current wave. Inspect and reconcile it before requesting more work. Cancellation remains the existing per-job qualified operation; it is not rollback, does not necessarily stop processing and does not release estimated exposure without trusted final billing evidence.

Every batch output-validator invocation records `validation_in_progress` in its child ledger before calling the trusted validator. A crash, failed result write, or failed conflict-receipt write leaves that intent unresolved. Such an intent blocks all remaining batch admissions and further batch validation calls, and cached batch validations are not usable for acceptance until the unknown outcome is reconciled. It has no automatic clearing path. A validator that returns a known failed/invalid result without an accepted collision observation may complete its intent as failed and be explicitly invoked again; this is a new validation read, never another workitem. A collision remains protected even if writing the individual job projections fails after the separate conflict receipt is saved.

Cancellation persists a freshly observed terminal status even when an earlier cancellation request already exists or the provider no longer supports cancellation in that state. These paths do not send another cancellation request and do not release reserved cost. A repeated cancel response and subsequent batch inspection therefore refer to the same durable observed status.

## Inspect, validate and settle each result

`fusion_cloud_batch_inspect({batch_id})` reads a coherent local manifest and child-ledger view without provider polling. It includes every variant's status, provider ID when unambiguous, exact plan/request identity, reservation, validation/billing receipt summaries, and cancellation state. The progress fields separate unmaterialized, prepared, active, uncertain, validating, succeeded, failed and cancelled items. Counts are not a substitute for the individual rows.

Batch reporting has its own fixed 4 MiB / 50,000-node response bound, independent of the original 4 MiB preparation-manifest admission bound. Full per-job validation receipts are not multiplied into the batch view: each summary records its exact stored `receipt_hash`, observed pass/fail/unresolved result, check counts, artifact count/bytes, usability, and `inspect_job_id`. Billing summaries similarly preserve the exact receipt hash, actual amount/currency, source and finality. `full_receipt_included: false` explicitly directs callers to `fusion_cloud_job_inspect`; that read returns the original stored evidence without revalidating or changing it.

Inputs are inlined only up to 32 scalar fields and 8 KiB per variant; common context is inlined only up to 32 KiB / 1,024 nodes, and destination metadata only up to 8 KiB / 64 nodes. Otherwise the value is `null` with an exact hash, completeness flag, count where relevant, and a job reference. The context hash covers the batch request context; the corresponding `job.prepared.context` additionally contains the fixed `variantCount: 1`. Up to eight prepared warnings of at most 1 KiB each are shown, with a full warning-list hash/count and explicit completeness flag. Normal credential redaction still applies to inline values. None of these projections truncate the durable request or receipt, drop a variant, or imply that omitted evidence passed validation.

Use each returned `job_id` with the existing operations:

1. `fusion_job_status` with `provider: "automation"` for an explicit bounded provider status read.
2. `fusion_cloud_job_validate` to invoke the trusted recipe output validator.
3. `fusion_cloud_job_settle` to invoke trusted final billing reconciliation.
4. `fusion_job_cancel` only when provider cancellation is qualified and actually intended.

Provider success stays `validating` until the exact-job output receipt supplies every required validator result, bounded artifact sizes, identities and hashes. `all_outputs_validated` is true only when all variants have successful trusted validation and no exposed artifact-ID collision. `billing_settled` is separate and cannot be true while unattempted or unmaterialized variants remain. Individual failure, missing validation integration and unsettled exposure stay visible. These flags report host-recorded evidence, not an independent certification of Autodesk engineering results. `publication_performed` remains false; the coordinator does not release staged outputs.

`output_conflict_receipt` and `output_identity_conflicts` expose durable collision evidence even when the conflicting candidate was correctly refused as a validation receipt. `validation_outcome_unknown` identifies an unresolved validation intent. Polling or settling an implicated job preserves its failed/unusable disposition while separately recording provider lifecycle or billing evidence; neither observation revalidates output bytes.

Tool-visible views apply the existing credential and signed-URL redaction. Batch error rows expose only bounded error codes/outcomes, not raw provider error messages or diagnostics. Internal immutable hashes continue to bind the original private records; a redacted display is not a replacement manifest to write back. Never place credentials in recipe parameters or source metadata.

## Retention and qualification

Retention must treat a batch as a dependency group. Protect the `cloudbatch` manifest, every `variants[].initial_job.id` child record, each child's replay record and the related intent/outcome evidence. Child replay IDs use the existing `hash({cloud: profile_id, key: variants[].idempotency_key})` format. Materializing or uncertain batches, missing ready children, pending output validation and unsettled cost must not be made resumable by removing records. Unknown schema or incomplete dependency coverage must be reported and protected rather than guessed safe to archive.

Also protect `cloudbatchconflict` and link its `batch_id`/`batch_plan_hash` and every `job_bindings[].job_id`/`plan_hash`. `assertCloudBatchConflictIntegrity` checks its bounded receipt/hash and can additionally verify the owning batch. An unresolved `cloudjob.validation_in_progress` or `output_identity_conflict` is protected evidence. Removing an already referenced conflict receipt fails closed; it never restores an implicated validation grade.

The offline tests in `tests/cloud-batches.test.mjs` exercise strict MCP schemas, whole-batch rejection, stable replay, partial materialization, missing-ready-child refusal, source/account/profile/expiry drift, shared admission limits, concurrent lease exclusion, durable uncertain intent, provider/artifact identity conflicts, trusted validation/settlement separation and redacted tool output. Collision tests include three-variant restart/resume, lost conflict/job writes, immutable original mappings, protected historical validation, and missing/altered/cross-bound evidence. Cancellation tests cover terminal observations through both early-return paths, no repeated DELETE, and retained reservations. A populated 100-variant synthetic ledger verifies large-receipt reporting, exact counts/hashes, explicit omissions, complete per-job drill-down, bounded JSON and no provider calls or ledger writes during inspection. The tests use private synthetic state and in-memory provider doubles. They establish neither live recipe execution nor tenant, storage, geometry, timing, entitlement, cancellation or billing qualification. W10 live acceptance still requires those deployment tests and responsible engineering/IT review under the full implementation plan.
