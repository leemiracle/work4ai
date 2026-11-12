# Orca: Agent-Friendly Curator Workload Runner

## Summary

Orca is a Curator-facing tool layer for making curation workflows reproducible, inspectable, and agent-friendly. Its
first implementation should be small and deterministic. Its first job is to make this interaction work well:

```text
Hey Orca, run this benchmark on Slurm and tell me what happened.
```

Orca should help a developer or coding agent resolve a known benchmark or pipeline run, render the command, submit it to
an execution backend, monitor the job, collect bounded logs and artifacts, parse basic metrics, and produce a concise
report.

The first version should not be a bespoke chatbot, autonomous daemon, data platform, or curation-research system.
Instead, Orca should piggyback on repo-aware coding agents such as Codex, Claude Code, or a human shell. Orca owns the
CLI, JSON schemas, workload registry, run artifacts, and deterministic backend/log/artifact tools. The coding agent
owns natural-language interpretation and conversation with the user.

The near-term product promise is modest:

- Existing Cosmos Curator benchmarks and pipelines are easier to run on Slurm.
- Every run leaves a reproducible artifact.
- Results are easy for humans and agents to inspect.
- The tool surface is structured enough that stronger future agents can use it without special integration.

This is the smallest useful version of a curation-run contract. A benchmark is the safest first workload because it has
known inputs, known commands, expected outputs, metrics, and logs. If Orca captures those pieces consistently, the same
artifact shape can later support sampled manifest runs, bounded curation trials, evidence packs, and scale-up plans.

Slurm is an unblock for current Cosmos Curator users, not the center of the architecture. The durable value is the
Curator-specific understanding of workloads, manifests, metrics, samples, evidence, and review loops. Over time, Orca
should be able to delegate execution to other backends while preserving the same Curator run artifact.

The larger curation system can remain a direction of travel, but v0 should earn trust by improving the operational loop
people already perform manually.

## Relationship To OSMO

Orca should not be a competing physical AI orchestration framework.
[NVIDIA OSMO](https://developer.nvidia.com/osmo) is the broader workflow orchestration layer for physical AI: YAML
workflows, dependency management, dataset movement, scheduling, and execution across Kubernetes, cloud, on-prem, and edge
environments. Orca should not duplicate OSMO's control plane, scheduler, dataset service, authentication model, or
Kubernetes abstraction.

The boundary is:

- **OSMO** owns physical AI workflow execution infrastructure.
- **Slurm** owns HPC job scheduling where Curator users already run workloads.
- **Orca** owns Curator-specific workflow understanding: workload definitions, curation intent, manifests, run artifacts,
  metrics, representative samples, evidence packs, reports, and review feedback.

For Kubernetes-backed execution, Orca should delegate to OSMO: render or submit an OSMO workflow, query OSMO status and
logs, then ingest the resulting metadata and artifacts into the same Curator run artifact shape. For Slurm-backed
execution, Orca can wrap existing `cosmos-curator slurm submit` behavior. The execution backend should be replaceable;
the Curator-facing artifact and semantics should remain stable.

## Why Start Here

Cosmos Curator today is mostly a collection of useful video curation pipelines, benchmark scripts, and deployment
commands. That is a good starting point. The immediate pain is not that the pipelines lack autonomy. The immediate pain
is operational:

- Users have to remember benchmark names, command shapes, input paths, output paths, Pixi environments, and resource
  settings.
- Slurm submission, status polling, log lookup, and artifact collection are manual and cluster-specific.
- Results are often summarized ad hoc in chat, notebooks, or terminal scrollback.
- Failed jobs require a human to find the right log files, identify common errors, and decide what to try next.
- Coding agents can help, but only if the commands and outputs are structured, bounded, and reproducible.

The pragmatic move is to make current "dumb" pipeline runs legible before trying to make curation intelligent.

That means Orca should optimize for durable run facts before higher-level reasoning: what was requested, which data was
used, what command ran, what resources were requested, what outputs were produced, what metrics were observed, and which
examples or logs justify the summary.

## Design Bets

- **Use existing coding agents first.** Frontier coding agents are improving quickly at repo navigation, shell use, log
  reading, and tool calling. Orca should give them excellent tools instead of competing with them.
- **Keep the core deterministic.** Backend submission, status reconciliation, log collection, artifact copying, and
  metric parsing should be ordinary Python with typed inputs and outputs.
- **Make runs reproducible.** A successful interaction should leave enough state on disk to understand what was asked,
  what command ran, what the execution backend returned, what logs were collected, and what the result was.
- **Preserve curation shape.** Even for simple benchmark runs, artifacts should record input references, output
  references, metrics, samples, and lineage pointers so later curation trials do not need a different operational model.
- **Keep artifacts backend-neutral.** Slurm job IDs and OSMO workflow IDs are backend details. Orca should normalize
  them into a common Curator run artifact.
- **Prefer JSON over prose.** Human-friendly output is useful, but JSON is the primary contract for agents.
- **Defer autonomy.** Unattended monitoring, Slack routing, retries, scale-up decisions, and persistent memory can wait
  until the workload-runner loop is reliable.
- **Do not hide the command.** Orca should render the exact command before submission. The agent or user can decide
  whether to run it.

## MVP Scope

Given a known benchmark or pipeline run name and optional overrides, Orca v0 should target Slurm first and keep the
artifact shape backend-neutral:

1. Find the workload definition.
2. Validate required inputs, output paths, environment assumptions, and Slurm resource settings.
3. Render a concrete command and write a resolved run artifact.
4. Submit the resolved run to Slurm only through an explicit `submit` command.
5. Record the Slurm job ID and run metadata.
6. Poll status through `squeue` and `sacct`.
7. Collect bounded logs and declared artifacts.
8. Parse basic metrics when a workload exposes them.
9. Preserve input, output, artifact, metric, and sample references in the run directory.
10. Produce a short machine-readable and human-readable report.

Example user interaction:

```text
User:
  Run the captioning benchmark on Slurm with 4 nodes.

Agent:
  cosmos-curator orca workloads show captioning --json
  cosmos-curator orca run captioning --target slurm --nodes 4 --dry-run --json
  cosmos-curator orca submit <run_id> --json
  cosmos-curator orca status <run_id> --json
  cosmos-curator orca collect <run_id> --json
  cosmos-curator orca report <run_id> --json
```

Example final report:

```text
execution_status: failed
run_id: 20260429-153012-captioning
job_id: 12345
runtime: 41m
nodes: 4
inputs: 1000 videos
outputs: 997 records
failures: 3
throughput: 24.3 videos/min
top_errors:
  - decode_error: 2
  - missing_metadata: 1
artifacts:
  - .orca/runs/20260429-153012-captioning/logs/slurm-12345.out
  - .orca/runs/20260429-153012-captioning/artifacts/metrics.json
next_actions:
  - Inspect the three failed inputs.
  - Re-run with the decode-error skip flag if these failures are expected.
```

## Non-Goals For v0

Orca v0 should not include:

- A first-party chat runtime.
- A Slack bot.
- A web dashboard.
- A persistent daemon.
- A general physical AI workflow orchestrator.
- A Kubernetes control plane or OSMO replacement.
- Postgres state, leases, or durable work queues.
- Lance commit orchestration.
- Automatic pipeline synthesis.
- A trusted curation primitive catalog.
- Autonomous retries or scale-up.
- Sensor/action episode abstractions.
- Train/eval dataset promotion.
- Long-term curation memory.

These may become useful later, but none are required to prove the first interaction.

## Ownership Boundaries

Orca v0 has four actors:

- **Coding agent or human shell**: interprets natural language, chooses which Orca command to run, asks the user for
  approval, and explains the result.
- **Orca CLI**: validates workload definitions, renders commands, calls execution backends, records state, collects
  logs/artifacts, parses metrics, and emits JSON.
- **Execution backends**: run the actual benchmark or pipeline workloads. Slurm is the v0 backend. OSMO can become a
  Kubernetes-backed backend when that environment is available.
- **Existing Cosmos Curator**: provides the pipeline and benchmark entry points that actually process data.

This means "Orca agent" in v0 usually means "Codex or Claude Code using Orca tools." A dedicated Orca runtime should be
deferred until usage proves the need for unattended monitoring, notification routing, identity, audit, or a non-developer
UI.

## Architecture

```text
Developer
   |
   v
Codex / Claude Code / human shell
   |
   v
cosmos-curator orca CLI
   |
   +-- workload registry
   +-- run artifact store
   +-- log collector
   +-- artifact collector
   +-- metric parser
   |
   +-- execution backend adapters
       |
       +-- Slurm adapter -> cosmos-curator slurm submit -> Slurm
       |
       +-- OSMO adapter -> osmo workflow submit/query/logs -> OSMO / Kubernetes
       |
       v
   existing Cosmos Curator benchmark / pipeline commands
```

There is no persistent Orca service in v0. All state is stored in a run directory. The first backend should be Slurm
because that unblocks current Cosmos Curator workflows. The architecture should still treat Slurm as an adapter, not as
the product boundary.

## Run Artifact

Every Orca run writes a directory under a configurable root. The default can be `.orca/runs/<run_id>/`.

```text
.orca/runs/<run_id>/
  request.json
  workload.json
  resolved_command.sh
  inputs.json
  outputs.json
  resources.json
  submission.json
  status.json
  events.jsonl
  logs/
  artifacts/
  samples/
  metrics.json
  report.json
  report.md
```

The run artifact is the main durable interface. It lets a user or agent answer:

- What did the user ask for?
- Which workload definition was used?
- Which source inputs or manifests were used?
- What command was actually submitted?
- What resources were requested?
- Which backend job or workflow was created?
- What happened over time?
- Which outputs or output locations were produced?
- Which logs and artifacts were collected?
- Which representative samples were collected?
- What metrics were parsed?
- What should we do next?

The artifact should be useful even if no agent is involved. For v0, `inputs.json`, `outputs.json`, and `samples/` can be
thin pointers to existing manifests, output directories, and declared sample files. They do not need to solve the full
curation schema problem; they just need to make the run auditable and easy to compare.

The first implementation should assume declared workload inputs, outputs, artifacts, and samples are local filesystem
paths from the perspective of the `cosmos-curator orca` process. In practice, this can be a developer machine path or a
shared filesystem visible from the Slurm login environment. Orca may record non-local URI strings such as S3 paths as
pointers, but v0 should not attempt general object-store, SSH, or cluster-wide artifact copying for workload outputs.

## Workload Registry

A workload definition should be small and explicit. The first workloads can be benchmarks, smoke tests, or known
pipelines. A definition does not need to describe every possible pipeline detail. It only needs enough structure for
Orca to render, validate, run, and collect a known run.

Example shape:

```yaml
schema_version: 1
kind: benchmark
name: captioning-smoke
description: Caption a small video manifest on Slurm.
command:
  argv:
    - pixi
    - run
    - --as-is
    - -e
    - "{pixi_env}"
    - python
    - -m
    - "{entrypoint_module}"
    - --input-manifest
    - "{input_manifest}"
    - --output-dir
    - "{output_dir}"
defaults:
  pixi_env: default
  nodes: 1
  gres: "gpu:8"
  timeout: "02:00:00"
  job_name: captioning-smoke
inputs:
  required:
    - input_manifest
    - output_dir
outputs:
  declared:
    - "{output_dir}/captions.jsonl"
resources:
  slurm:
    login_node: "{login_node}"
    account: "{account}"
    partition: "{partition}"
    container_image: "{container_image}"
    container_mounts: "{container_mounts}"
    remote_files_path: "{remote_files_path}"
    num_nodes: "{nodes}"
    gres: "{gres}"
    time: "{timeout}"
    job_name: "{job_name}"
artifacts:
  include:
    - "{output_dir}/metrics.json"
    - "{output_dir}/samples/**"
samples:
  include:
    - "{output_dir}/samples/**"
metrics:
  json_paths:
    input_count: "$.input_count"
    output_count: "$.output_count"
    failure_count: "$.failure_count"
```

The exact schema can change while v0 is experimental, but the design goal is stable: workloads are named, inspectable,
command-renderable, and explicit about the inputs, outputs, artifacts, samples, and metrics Orca should preserve.
Execution-specific fields should live under backend-specific sections such as `resources.slurm` or a future
`resources.osmo`. The shared workload definition should remain about Curator intent, inputs, outputs, artifacts, samples,
and metrics.

For the Slurm backend, Orca should render the existing launcher shape rather than invent a second Slurm interface:
`cosmos-curator slurm submit <slurm options> -- <command.argv>`. The current Slurm CLI owns sbatch generation, container
launch, Ray bootstrap, and job ID parsing; Orca should provide typed resolution and run artifacts around that behavior.
Backend placeholders such as `login_node`, `account`, `partition`, `container_image`, and `container_mounts` can come
from Orca config, workload defaults, or command-line overrides.

## CLI Contract

All agent-facing commands should support `--json`. Human-readable output can be layered on top.

Initial commands:

```text
cosmos-curator orca workloads list --json
cosmos-curator orca workloads show <name> --json
cosmos-curator orca run <name> --target slurm [overrides...] --dry-run --json
cosmos-curator orca submit <run_id> --json
cosmos-curator orca status <run_id> --json
cosmos-curator orca logs <run_id> --json
cosmos-curator orca collect <run_id> --json
cosmos-curator orca report <run_id> --json
cosmos-curator orca cancel <run_id> --json
```

Useful supporting commands:

```text
cosmos-curator orca doctor --json
cosmos-curator orca runs list --json
cosmos-curator orca runs show <run_id> --json
```

Tool rules:

- JSON-in / JSON-out is the primary contract.
- Workload definitions should be inspectable before execution.
- Commands should never ask interactive prompts.
- Errors should be typed and actionable.
- Log output must be bounded by default.
- Artifact collection must follow declared allowlists or explicit user-provided local paths.
- Idempotent commands should report whether they changed anything.
- `run` should create or update a resolved run artifact and render the command without submitting backend work.
- `submit` should require an explicit resolved run ID and should be the only v0 command that creates backend work.
- `cancel` should require an explicit run ID and report the exact backend action taken.

Example typed error:

```json
{
  "ok": false,
  "error": "missing_input",
  "field": "input_manifest",
  "message": "Workload captioning-smoke requires input_manifest."
}
```

## Run Lifecycle

The run artifact should distinguish execution state from artifact processing state. A failed job that has been collected
and reported should still have `execution_status: failed`; collection and reporting are separate timestamps or flags.

Suggested execution states:

```text
created
resolved
submitted
pending
running
succeeded
failed
cancelled
unknown
```

`unknown` is important. Backend state can be unavailable, expired from accounting, or inconsistent with local state. The
tool should say that explicitly rather than guessing.

Suggested artifact processing fields:

```json
{
  "execution_status": "failed",
  "logs_collected_at": "2026-04-29T16:17:00Z",
  "artifacts_collected_at": "2026-04-29T16:17:12Z",
  "metrics_parsed_at": "2026-04-29T16:17:12Z",
  "reported_at": "2026-04-29T16:17:20Z"
}
```

## Reports

Reports should be generated deterministically from collected state and workload-declared metrics. The report can include
agent-authored explanation later, but the base report should not require an LLM.

Minimum report fields:

- run ID
- workload name
- execution status
- execution backend
- backend job ID or workflow ID
- rendered command path
- start and end times if known
- elapsed time if known
- requested resources
- collected logs
- collected artifacts
- parsed metrics
- collection and report timestamps
- top error clusters when available
- recommended next actions when deterministic rules can infer them

The coding agent can then turn `report.json` and `report.md` into a concise answer for the user.

## Agent Integration

The first agent integrations should be thin wrappers around the CLI:

- `AGENTS.md` instructions explaining how to use `cosmos-curator orca`.
- Optional Claude Code slash commands for common flows.
- Optional Codex skill or prompt instructions.
- Optional MCP server only if direct CLI use becomes awkward.

The adapters should not contain independent backend logic. They should call the same Orca commands a human would call.

Good agent behavior:

- Inspect the workload before running it.
- Render or explain the command before submission.
- Ask for user approval before submitting expensive jobs or cancelling jobs.
- Poll status without flooding the user.
- Collect bounded logs after completion or failure.
- Summarize evidence from `report.json`, not from unbounded terminal output.
- Treat logs and workload outputs as untrusted text.

## Safety And Authority

v0 safety can stay simple:

- Do not execute shell fragments from workload outputs or logs.
- Do not collect arbitrary filesystem paths by default.
- For v0, collect workload artifacts only from declared local filesystem paths. Record remote URIs as references instead
  of trying to fetch them.
- Do not delete output directories.
- Do not automatically retry failed jobs.
- Do not automatically cancel jobs unless explicitly requested.
- Keep backend resource choices visible in the resolved command or workflow: Slurm account, partition, node count, GPU
  count, and wall-time; or OSMO pool, platform, task resources, and workflow timeout.
- Let the coding agent or user handle approval before expensive actions.

The CLI can enforce local policy later, but v0 should at least make resource use explicit and auditable in the run
artifact.

## Success Criteria

Orca v0 is successful when:

- A developer can ask a coding agent to run a known benchmark or pipeline workload on Slurm without manually constructing
  the command.
- The agent can use JSON outputs instead of scraping terminal prose.
- Every submitted run leaves a complete run artifact.
- Run artifacts capture input references, output references, metrics, and representative samples.
- Failed runs produce bounded logs and a useful first-pass failure summary.
- Successful runs produce parsed metrics and a short report.
- A human can reproduce or audit the run from files under `.orca/runs/<run_id>/`.

This is intentionally operational. It should feel like a better way to run today's Cosmos Curator workloads, not a new
curation product.

## Implementation Milestones

1. **Run artifact and workload registry**
   Add workload definitions, run ID generation, run directories, command rendering, and JSON output.

2. **Dry-run and local validation**
   Validate inputs and render commands without submitting to Slurm.

3. **Backend adapter boundary**
   Define the minimal backend interface for submit, status, logs, collect, report identifiers, and cancel.

4. **Slurm submission and status**
   Implement the first backend by wrapping existing `cosmos-curator slurm submit`, recording job IDs, and querying
   `squeue` / `sacct`.

5. **Log and artifact collection**
   Copy bounded logs and declared artifacts into the run directory.

6. **Metrics and reports**
   Parse workload-declared metrics and emit `report.json` / `report.md`.

7. **Agent adapters**
   Add project instructions and optional slash commands or skills that teach coding agents to use the CLI.

## Direction Of Travel

If v0 proves useful, Orca can grow one step at a time:

```text
v0: run a known benchmark on Slurm with a reproducible run artifact
v1: compare two run artifacts
v2: run an existing pipeline on a sampled manifest
v3: delegate Kubernetes execution to OSMO while preserving the same run artifact
v4: produce trial evidence and scale-up plans
v5: assist curation tuning from human review and downstream eval results
```

This path preserves the larger possibility: Orca may eventually help users turn curation intent into reproducible
recipes, trials, evidence packs, and promoted train/eval datasets. That should remain a direction, not the v0 contract.

The durable bet is that better agents will be able to do more with the same structured substrate: workload definitions,
typed tools, bounded logs, metrics, reports, and reproducible run artifacts.

## Open Questions

- Where should workload definitions live: packaged defaults, repo-local files, user-local files, or all three?
- What is the smallest workload schema that can cover current Cosmos Curator smoke tests and representative Slurm
  benchmarks without pretending to be a full recipe schema?
- How should `cosmos-curator orca submit` invoke existing `cosmos-curator slurm submit` without duplicating Slurm config
  logic?
- What is the smallest OSMO adapter that can submit, query, collect logs, and map an OSMO workflow into a Curator run
  artifact?
- Which two or three real benchmarks or smoke pipelines should define the v0 acceptance test?
- What metrics do current workloads already emit, and what minimal changes would make them easier to parse?
- How should log collection find Slurm output paths across different clusters?
- After local-path artifact collection, which non-local path type should come next: shared cluster filesystems, S3, or
  another object store?
- What default bounds should apply to log size, artifact size, and polling frequency?
- Which agent adapter should come first: AGENTS.md-only, Claude slash command, Codex skill, or MCP?
