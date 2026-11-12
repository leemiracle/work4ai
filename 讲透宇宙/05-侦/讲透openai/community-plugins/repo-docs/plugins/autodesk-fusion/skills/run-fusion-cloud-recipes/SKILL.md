---
name: run-fusion-cloud-recipes
description: Prepare, submit and reconcile reviewed Fusion Automation jobs with exact sources, scoped authorization and explicit budgets. Not for arbitrary model-generated cloud scripts.
---

Inspect `fusion_cloud_status`, authorization owner, reviewed recipes, scope and admission budget. Never reuse native MCP tokens, distribute a client secret or request a PAT.

Choose an installed recipe and declared typed inputs. Freeze exact source versions/configuration/hashes. A generic signed activity does not constrain code, data or cost.

Use `fusion_cloud_job_prepare` to resolve actual dependencies and reservation. Required hard-cap or immutability guarantees remain blockers when unsupported; do not weaken them silently.

For a bounded batch, use `fusion_cloud_batch_prepare` with one approved recipe, frozen common source context, approved object-storage destination, a stable request key and explicit unique variant IDs. Review the whole prepared mapping before submission. `fusion_cloud_batch_resume` admits only the requested bounded wave of unattempted children; it does not refresh expiry, bypass per-job budgets or publish into Fusion/ERP. Use `fusion_cloud_batch_inspect` after interruption, and retain each child job ID for detailed status, output validation and billing.

Submit the unchanged plan with an existing compute grant and unique idempotency key. Durable intent/reservation precedes submission. Lost acknowledgments and unknown states never justify blind resubmission.

Poll the plugin job ID. Provider success remains validating until trusted output checks pass. Cancel only where qualified; cancellation is not rollback or free compute. Final billing comes from the trusted reconciliation adapter; unknown exposure retains its reservation.

Unknown validation intent or a recorded output-identity collision blocks the batch. Do not clear records, regenerate keys, revalidate to erase a conflict or submit remaining variants as a workaround. A receipt ID collision check does not prove physical storage-key isolation; that is part of the trusted stager's qualification.

Report processing, validation, artifact and cost evidence separately. Offline mocks do not establish geometry, residency, metering or service compatibility. See [enterprise recipes](../../docs/enterprise.md) and [batch recovery](../../docs/batches.md).
