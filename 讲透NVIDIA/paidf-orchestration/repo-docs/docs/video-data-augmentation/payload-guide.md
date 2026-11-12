# Video Data Augmentation Payload Guide

This guide describes the JSON payload supplied to
`video_data_augmentation_dag_k8s` or `video_data_augmentation_dag_osmo`. The
workflow runs the same auto-labeling pipeline on each source video and each
Cosmos-generated variant:

> **OSMO: EXTERNAL ENDPOINTS ONLY**
>
> `video_data_augmentation_dag_osmo` does not contain deployable inference or
> Cosmos Evaluator services. Every OSMO payload must set
> `external_services: true` and provide all external VLM, LLM, and Cosmos
> Transfer URLs used by `cosmos`, `captioning`, `visual_qa`, and `reasoning`.
> If an evaluator check is enabled, the payload must also provide an external
> `cosmos.cosmos_evaluator_service_url`.
>
> **Do not submit an internal-services payload (`external_services: false`) to
> the OSMO DAG. It will fail because the OSMO manifest has no endpoint
> components to deploy.**

1. Video super resolution
2. Detection and tracking
3. Captioning
4. Visual question answering
5. Reasoning-label generation
6. Training-dataset export

Cosmos Transfer creates the variants between the input and output labeling
branches.

## Quick Start: Starter Payloads

Always replace the input and output locations. The defaults embedded in the
payload model are deployment-specific development paths and should not be used
for a new run.

### In-cluster services (`external_services=false`)

> **Kubernetes DAG only. This mode is not supported by OSMO.**

```json
{
  "input_path": "s3://<your-input-bucket>/<your-workflow>/input",
  "max_videos": 1,
  "output_directory": "s3://<your-output-bucket>/<your-workflow>/output",
  "external_services": false,
  "cosmos": {
    "num_augmentation": 1,
    "checker_overrides": {
      "metropolis.hallucination": true,
      "metropolis.attribute_verification": true,
      "metropolis.physical_plausibility": false
    },
    "variable_distribution": {
      "variables": {
        "weather": { "cloudy": 0.5, "sunny": 0.5 },
        "time_of_day": { "morning": 0.5, "afternoon": 0.5 }
      }
    }
  }
}
```

The workflow starts the internal language-model and Cosmos Transfer services.
It also starts the managed Cosmos Evaluator components required by the enabled
checks.

### External Services

```json
{
  "input_path": "s3://<your-input-bucket>/<your-workflow>/input",
  "max_videos": 1,
  "output_directory": "s3://<your-output-bucket>/<your-workflow>/output",
  "external_services": true,
  "cosmos": {
    "vlm_service_url": "https://<your-vlm-endpoint>/v1",
    "llm_service_url": "https://<your-llm-endpoint>/v1",
    "cosmos_transfer_service_url": "https://<your-cosmos-transfer-endpoint>/v1",
    "num_augmentation": 1,
    "checker_overrides": {
      "metropolis.hallucination": true,
      "metropolis.attribute_verification": true,
      "metropolis.physical_plausibility": false
    },
    "variable_distribution": {
      "variables": {
        "weather": { "cloudy": 0.5, "sunny": 0.5 },
        "time_of_day": { "morning": 0.5, "afternoon": 0.5 }
      }
    }
  },
  "captioning": {
    "vlm_service_url": "https://<your-vlm-endpoint>/v1",
    "llm_service_url": "https://<your-llm-endpoint>/v1",
    "enable_llm_summary": true
  },
  "visual_qa": {
    "vlm_service_url": "https://<your-vlm-endpoint>/v1",
    "llm_service_url": "https://<your-llm-endpoint>/v1"
  },
  "reasoning": {
    "llm_service_url": "https://<your-llm-endpoint>/v1"
  }
}
```

External mode controls the VLM, LLM, and Cosmos Transfer services. Cosmos
Evaluator placement is separate. On the Kubernetes DAG, omit
`cosmos.cosmos_evaluator_service_url` to use the managed evaluator, or set it to
an existing Arbitrator root URL. The OSMO requirements are described below.

## OSMO Payloads: External Endpoints Only

`video_data_augmentation_dag_osmo` supports only external inference endpoints.
Its manifest defines OSMO batch tasks and no deployable VLM, LLM, or Cosmos
Transfer endpoint components. For every OSMO run:

- Set top-level `external_services` to `true`.
- Supply every endpoint listed in the external-services example above:
  `cosmos.vlm_service_url`, `cosmos.llm_service_url`,
  `cosmos.cosmos_transfer_service_url`, the captioning VLM/LLM URLs, the visual
  QA VLM/LLM URLs, and the reasoning LLM URL.
- Keep all three `service_lifecycle.*.enabled` values `false`, or omit
  `service_lifecycle` so the model fills them from the top-level mode.

Any OSMO payload with `external_services: false` is invalid for the deployed
manifest, even though the shared payload schema can parse it.

The OSMO DAG also has no managed Cosmos Evaluator components. When any quality
check remains enabled, add an external Arbitrator URL:

```json
{
  "external_services": true,
  "cosmos": {
    "cosmos_evaluator_service_url": "https://<your-cosmos-evaluator-endpoint>",
    "checker_overrides": {
      "metropolis.hallucination": true,
      "metropolis.attribute_verification": true,
      "metropolis.physical_plausibility": false
    }
  }
}
```

You may instead disable all three checks, in which case no evaluator URL is
needed. The JSON above is only the evaluator portion of an OSMO payload; retain
all inference endpoint fields from the full external-services example.
`OSMO_TOKEN`, `OSMO_URL`, `OSMO_POOL` and the optional `OSMO_HF_CACHE_SEED_DIR` are
deployment settings in `secrets.env`, not runtime payload fields.
All supplied service URLs must be reachable from the OSMO task network.

## Fields to Set for Every Run

- `input_path`: An accessible video or directory of videos. The examples use
  S3 paths; the storage layer also accepts HTTP and HTTPS paths when the
  configured backend can read them.
- `output_directory`: The base S3 location for this workflow's results.
- `external_services`: `false` for workflow-managed services or `true` for
  existing endpoints.

When `external_services=true`, also set real values for:

- `cosmos.vlm_service_url`
- `cosmos.llm_service_url`
- `cosmos.cosmos_transfer_service_url`
- `captioning.vlm_service_url`
- `captioning.llm_service_url` when `captioning.enable_llm_summary=true`
- `visual_qa.vlm_service_url`
- `visual_qa.llm_service_url`
- `reasoning.llm_service_url`

The model supplies syntactically valid placeholder endpoint defaults. Those
placeholders can pass payload validation and then fail when a task calls them.
The current validator also does not explicitly require
`cosmos.cosmos_transfer_service_url`, but the Cosmos configuration uses it, so
external runs must provide it.

Nested `output_directory` and `external_services` fields can be omitted. The
DAG copies the top-level values into `cosmos`, `captioning`, `visual_qa`, and
`reasoning`; it also copies `output_directory` into the remaining task
sections. If a nested output directory is supplied, it must exactly match the
top-level value. Keep all nested service modes aligned with the top-level mode.

## Top-Level Fields

- `input_path` (**string**): A single video file or a directory prefix.
  Directory discovery includes `.mp4`, `.avi`, `.mov`, `.mkv`, and `.webm`.
- `max_videos` (**integer or null**, default: `1`): Limits a directory input.
  Use a positive integer for a bounded run. `null`, zero, and negative values
  process every matched video. Direct-file inputs always retain their one video
  for these unlimited values.
- `output_directory` (**string**): Base output location. Artifacts are grouped
  beneath `<output_directory>/<run_id>/`.
- `external_services` (**boolean**, default: `false`): Selects managed or
  external VLM, LLM, and Cosmos Transfer services.
- `service_lifecycle` (**object, optional**): Internal service enablement and
  replica counts. Omit it unless changing replicas.
- `cosmos`, `captioning`, `visual_qa`, `reasoning`, `training_export`,
  `super_resolution`, and `detection_and_tracking` (**objects, optional**):
  Per-stage settings described below.

Unknown fields are ignored by the top-level model and by several nested
models. Check spelling carefully because an ignored misspelling silently leaves
the default in effect.

## `service_lifecycle`

The lifecycle object contains:

- `vlm_service`
- `llm_service`
- `cosmos_transfer_service`

Each accepts `enabled` (**boolean**) and `replicas` (**integer**, minimum `1`,
default `1`). The `enabled` values must strictly match the top-level mode:

- `external_services=false`: all three must be `true`.
- `external_services=true`: all three must be `false`.

Omitted entries are filled correctly. A conflicting value fails payload
validation. On the Kubernetes DAG, the configured VLM service can serve both
the VLM and LLM roles even though the payload retains separate lifecycle keys.
The current Kubernetes manifest has no separate `llm_service` component, so
`llm_service.replicas` does not deploy additional replicas there; use
`vlm_service.replicas` to scale the shared language-model endpoint.

To increase replicas in internal mode:

```json
{
  "external_services": false,
  "service_lifecycle": {
    "vlm_service": { "enabled": true, "replicas": 2 },
    "cosmos_transfer_service": { "enabled": true, "replicas": 1 }
  }
}
```

Airflow pool capacity and cluster GPU capacity still limit actual concurrency.
Refer to [Advanced Usage](../advanced-usage.md#scale-internal-model-throughput).

## `cosmos` (Video Augmentation)

- `num_augmentation` (**integer**, default: `1`, minimum: `1`): Variants to
  generate for each input video.
- `vlm_service_url`, `llm_service_url`, `cosmos_transfer_service_url`
  (**strings**): Service roots used in external mode. The DAG normalizes a
  Cosmos Transfer root ending in `/v1` and calls its asynchronous
  `/v1/videos` route.
- `vlm_model`, `llm_model` (**strings**): Model IDs sent to the language-model
  services. The Kubernetes DAG selects `Qwen/Qwen3.8-27B-FP8` for its internal
  shared service.
- `cosmos_transfer_model` (**string**): Accepted by the shared payload model,
  but the VDA bundled Cosmos configuration currently fixes the transfer model
  to `nvidia/Cosmos3-Nano`; this payload value does not replace it.
- `base_config_path` (**string or null**): Optional MSC-readable URI for a
  custom Cosmos YAML configuration. Omit it to use VDA's bundled
  `cosmos_config.yaml`.
- `variable_distribution` (**object**): Weighted target attributes sampled
  once per generated variant. Always include this field when you provide a
  `cosmos` object; refer to the default behavior below.
- `checker_overrides` (**object**): Strict boolean switches for evaluator
  checks present in the selected Cosmos configuration.
- `cosmos_evaluator_service_url` (**string or null**): Existing Cosmos
  Evaluator Arbitrator root. Omit it to use the managed evaluator when checks
  remain enabled.

### Variable Distributions

When the entire `cosmos` object is omitted, VDA inserts its weather/time
distribution. When `cosmos` is present but `variable_distribution` is omitted
or empty, the shared `CosmosTaskConfig` currently falls back to its clothing
attribute distribution. Set a non-empty VDA distribution explicitly whenever
you include `cosmos` in a payload.

Each direct variable maps candidate values to non-negative numeric weights.
At least one value is required and the total weight must be positive. Weights
are relative and do not have to add up to `1`.

```json
{
  "cosmos": {
    "variable_distribution": {
      "variables": {
        "weather": { "cloudy": 2.0, "sunny": 1.0 },
        "time_of_day": { "morning": 1.0, "afternoon": 1.0 }
      }
    }
  }
}
```

The schema also supports lookup distributions and `conditional_variables`.
Every conditional variable names a `depends_on` parent and must provide a
distribution for every possible sampled parent value.

### Cosmos Evaluator

The bundled VDA Cosmos configuration contains three gated checks:

- `metropolis.hallucination`
- `metropolis.attribute_verification`
- `metropolis.physical_plausibility`

An empty `checker_overrides` leaves all three enabled. Set a check to `false`
to remove it for that run. Setting a check to `true` retains it; it cannot add
a check absent from a custom base configuration. Unsupported or misspelled
names fail validation/config generation.

When at least one check remains and no external evaluator URL is supplied, the
DAG starts the managed evaluator components declared in its manifest. Evaluator
placement does not follow `external_services`. If all three checks are disabled,
the evaluator provider and managed evaluator services are skipped. Managed
evaluator deployment is available on the Kubernetes DAG only; OSMO requires an
external evaluator URL whenever a check remains enabled.

Candidates that fail an enabled quality gate are removed from the output
auto-labeling branch. The run continues when at least one candidate passes and
fails when every candidate is rejected.

## Auto-labeling and Export Sections

### `captioning`

- `enable_llm_summary` (**boolean**, default: `true`)
- `vlm_service_url`, `llm_service_url` (**strings**, external mode)
- `vlm_model`, `llm_model` (**strings**)

If summaries are disabled, an external captioning LLM URL is not required.

### `visual_qa`

- `generation_mode` (**string**, default: `window-vlm-llm`)
- `input_source` (**string**, default: `auto`)
- `include_reasoning` (**boolean**, default: `true`)
- `media_mode` (**string**, default: `auto`)
- `vlm_service_url`, `llm_service_url`, `vlm_model`, `llm_model`

The shared model also accepts `question_bank_file`. In the VDA DAG, both VQA
branches explicitly load the checked-in
`configs/vqa_question_bank.json`, upload it beside each scene, and pass that
generated sidecar path to the container. Changing `visual_qa.question_bank_file`
in a VDA payload therefore has no effect.

The mode fields are passed to the data-curation container as strings; the
payload schema does not enumerate allowed values. The defaults above are the
tested VDA settings.

### `reasoning`

- `reasoning_mode` (**string**, default: `keep`)
- `llm_service_url`, `llm_model`

### `training_export`

- `formats` (**non-empty string list**, default: `["tao-vl-reason-v1.0"]`)
- `tasks` (**string list**, default: `[]`): Optional task-type filters.
- `description` (**string or null**)
- `license` (**string or null**, default: `CC BY-NC-ND 4.0`)
- `tags` (**string list**, default: `[]`)
- `copy_media` (**boolean**, default: `true`)
- `emit_media_root_as_null` (**boolean**, default: `false`)

The workflow produces separate training exports for the original-input branch
and the Cosmos-output branch.

### `super_resolution`

The payload section currently exposes only `output_directory`, which should be
omitted so it inherits the top-level value. Super-resolution algorithm settings
come from the workflow's bundled task configuration.

### `detection_and_tracking`

- `allow_model_download` (**boolean**, default: `true`): Allows the container
  to download a missing detection model.

Other detection settings come from the bundled task configuration.

## Output Layout

For a run ID shown in Airflow, inspect these prefixes:

```text
<output_directory>/<run_id>/
   cosmos/<video_key>/<augmentation_index>/
      output.mp4
      caption.txt
      metadata.json
      ...
   auto_labeling_input/<video_key>/<index>/...
   auto_labeling_output/<video_key>/<output_index>/...
   training_export/auto_labeling_input/...
   training_export/auto_labeling_output/...
```

End-of-pipeline validation requires each Cosmos candidate directory to contain
`output.mp4`, `caption.txt`, and `metadata.json`. It also requires non-empty
input/output auto-labeling and training-export prefixes. The current DAG keeps
the original-input and generated-output branches as separate datasets; it does
not create a single combined dataset manifest. `output_index` is assigned over
the candidates that reach output auto-labeling and can differ from the original
Cosmos augmentation index when an earlier candidate is missing or rejected.

## Checked-in Examples

The repository includes these development examples:

- [`single_video_w_internal_endpooint.json`](../../payloads/dev/video_data_augmentation_dag/single_video_w_internal_endpooint.json)
- [`single_video_w_external_endpoint.json`](../../payloads/dev/video_data_augmentation_dag/single_video_w_external_endpoint.json)

Use them only as structural references. Replace the placeholder bucket paths
and service URLs with values for the target environment.
For OSMO, also follow [OSMO Payloads: External Endpoints Only](#osmo-payloads-external-endpoints-only).

## Review Before Triggering

Review the payload against the required fields, service-mode invariants, and
endpoint rules above. Confirm that no development paths, placeholder endpoint
URLs, or misspelled options remain. Successful schema parsing is not enough on
its own because the runtime model ignores unknown fields in several sections
and does not reject every operationally required endpoint. Refer to the
[execution-target and capacity table](getting-started.md#choose-an-execution-target)
for the compute preflight.

## Trigger the Run

1. Open the Airflow UI.
2. Enable `video_data_augmentation_dag_k8s`, or
   `video_data_augmentation_dag_osmo` for an external-endpoint OSMO run.
3. Choose **Trigger DAG w/ config**.
4. Under **Run Parameters**, replace `payload` with your payload JSON.
5. Start the run.
