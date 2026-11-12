---
name: handoff-fusion-engineering
description: Prepare a traceable local Fusion engineering review draft with source identities, artifacts and unresolved assurance gates. Not for sending, publication or release approval.
---

Use `fusion_handoff_prepare` to assemble the user's review evidence, and `fusion_handoff_inspect` to check an existing draft against current source and stored receipt state. Read [the handoff contract](../../docs/handoffs.md) when composing structured checks or interpreting freshness failures.

The accepted fields are `title`, `plan_ids`, `document_ids`, `requirements`, `assumptions`, `reviewers`, `checks` and `external_evidence`. Only the title is required; missing requirements, sources and checks stay explicit. Select actual producing plans to retain artifact and pending/uncertain job evidence. Do not invent unsupported `job_ids`, solver-result fields or approval flags.

Discover the active operation schemas and inspect the actual response before choosing check pointers. Automated handoff checks are limited to `document.inspect`, `parameters.list`, `geometry.measure`, `geometry.check` and `cam.inspect`. Numeric ranges require a value pointer and an exact observed unit pointer/string; there is no implicit unit conversion. Use identity assertions alongside array positions when the measured parameter or entity matters. Do not select credential fields or infer equality from redaction placeholders; rejected or redaction-altered comparisons cannot establish a result. Fixture values and response shapes do not qualify a live Fusion check.

Link requirements and reviewer IDs explicitly. Use manual procedures for unavailable solver, simulation, drawing, ECAD or engineering review work; they remain `not_run`. External evidence references and reported hashes are unfetched, unverified metadata. Reviewer assignments do not authenticate reviewers, notify them or record approval.

Known `freshness_gaps`, malformed coverage, changed source states and missing fingerprints prevent current use of dependent checks. A linked artifact must match its exact producing plan, document, preparation/completion source and implementation contract; an old-source or legacy receipt remains historical. Keep failed, pending and unknown plan outcomes visible. Do not rewrite a stored draft, drop unresolved evidence or refresh a stale assertion into a pass. Collect new observations into a new draft when the task calls for current evidence, keeping the original for comparison.

Return the local draft reference, its evidence scope and the unresolved decisions with their practical impact. A met criterion, screenshot, generated toolpath, setup sheet or provider success is not engineering, machine-collision or regulatory proof. These tools do not send the draft, publish artifacts, update enterprise systems or advance a release. Such actions require their own destination authority and qualified adapter; preparing an already authorized local draft does not require repetitive permission requests.
