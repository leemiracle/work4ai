# Event Video Generation Payload Guide

This guide describes the JSON payload you provide when triggering
`event_video_generation_dag_k8s` or `event_video_generation_dag_osmo` in
Airflow. The workflow turns each input image into one or more anomaly videos,
auto-labels the generated videos, and writes a ready-to-use anomaly dataset.

> **OSMO: EXTERNAL ENDPOINTS ONLY**
>
> `event_video_generation_dag_osmo` does not contain deployable inference or
> Cosmos Evaluator services. Every OSMO payload must set
> `external_services: true` and provide external VLM, LLM, and image-to-video
> URLs. If an evaluator check is enabled, the payload must also provide an
> external `cosmos.cosmos_evaluator_service_url`.
>
> **Do not submit an internal-services payload (`external_services: false`) to
> the OSMO DAG. It will fail because the OSMO manifest has no endpoint
> components to deploy.**

## Quick Start: Starter Payloads

Use one of these as your starting point. The repository also includes
[warehouse-falling external](../../payloads/dev/event_video_generation_dag/warehouse-falling-external-1.json),
and warehouse-safety mix variants for
[external](../../payloads/dev/event_video_generation_dag/warehouse-safety-mix-external-10.json)
and [in-cluster](../../payloads/dev/event_video_generation_dag/warehouse-safety-mix-internal-10.json)
services.

### In-cluster services (`external_services=false`)

> **Kubernetes DAG only. This mode is not supported by OSMO.**

Start with
[`warehouse-safety-mix-internal-10.json`](../../payloads/dev/event_video_generation_dag/warehouse-safety-mix-internal-10.json).
It deploys one shared VLM/LLM service and the image-to-video service in the
cluster. Replace its deployment-specific input and output S3 paths before
running it.

```json
{
  "input_path": "s3://<your-input-bucket>/<your-workflow>/input",
  "max_images": 1,
  "output_directory": "s3://<your-output-bucket>/<your-workflow>/output",
  "external_services": false,
  "cosmos": {
    "checker_overrides": {
      "metropolis.attribute_verification": true,
      "metropolis.physical_plausibility": true
    },
    "num_augmentation": 10,
    "variable_distribution": {
      "variables": {
        "anomaly_type": {
          "person_climbing": 0.2,
          "person_running": 0.2,
          "smoking_or_vaping": 0.2,
          "person_fighting": 0.2,
          "fire_or_smoke": 0.2
        },
        "env_type": { "warehouse": 1.0 }
      }
    }
  }
}
```

### External services (`external_services=true`)

Start with
[`warehouse-safety-mix-external-10.json`](../../payloads/dev/event_video_generation_dag/warehouse-safety-mix-external-10.json).
Replace its deployment-specific S3 paths and all service URLs. In particular,
replace or remove `cosmos.cosmos_evaluator_service_url`; removing it selects the
workflow's managed evaluator.

```json
{
  "input_path": "s3://<your-input-bucket>/<your-workflow>/input",
  "max_images": 1,
  "output_directory": "s3://<your-output-bucket>/<your-workflow>/output",
  "external_services": true,
  "cosmos": {
    "vlm_service_url": "https://<your-vlm-endpoint>/v1",
    "llm_service_url": "https://<your-llm-endpoint>/v1",
    "image2video_service_url": "https://<your-image2video-endpoint>/v1",
    "checker_overrides": {
      "metropolis.attribute_verification": true,
      "metropolis.physical_plausibility": true
    },
    "num_augmentation": 10,
    "variable_distribution": {
      "variables": {
        "anomaly_type": {
          "person_climbing": 0.2,
          "person_running": 0.2,
          "smoking_or_vaping": 0.2,
          "person_fighting": 0.2,
          "fire_or_smoke": 0.2
        },
        "env_type": { "warehouse": 1.0 }
      }
    }
  }
}
```

Both inline examples target the Kubernetes DAG and use its managed Cosmos
Evaluator. To use an existing evaluator instead, add
`cosmos.cosmos_evaluator_service_url` with its Arbitrator root URL. Evaluator
placement is independent of `external_services`, which controls the VLM/LLM and
image-to-video endpoints.

## OSMO Payloads: External Endpoints Only

`event_video_generation_dag_osmo` supports only external inference endpoints.
Its manifest defines OSMO batch tasks but no VLM or image-to-video endpoint
components, so an internal-services payload cannot deploy the services it
needs.

For every OSMO run:

- Set top-level `external_services` to `true`.
- Set `cosmos.external_services` to `true` or omit it so it inherits the
  top-level value.
- Supply `cosmos.vlm_service_url`, `cosmos.llm_service_url`, and
  `cosmos.image2video_service_url`.
- Keep `service_lifecycle.vlm_service.enabled` and
  `service_lifecycle.image2video_service.enabled` set to `false`, or omit
  `service_lifecycle` so the payload model fills those values.

Any OSMO payload with `external_services: false` is invalid for the deployed
manifest, even though the shared payload schema can parse it.

The OSMO DAG also has no managed Cosmos Evaluator components. When either
quality check remains enabled, set `cosmos.cosmos_evaluator_service_url` to an
external Arbitrator root URL. Alternatively, disable both checks explicitly:

```json
{
  "external_services": true,
  "cosmos": {
    "vlm_service_url": "https://<your-vlm-endpoint>/v1",
    "llm_service_url": "https://<your-llm-endpoint>/v1",
    "image2video_service_url": "https://<your-image2video-endpoint>/v1",
    "checker_overrides": {
      "metropolis.attribute_verification": false,
      "metropolis.physical_plausibility": false
    }
  }
}
```

The external starter payloads are suitable for OSMO after replacing their
deployment-specific paths and endpoint URLs. Do not use
`warehouse-safety-mix-internal-10.json` with the OSMO DAG. `OSMO_TOKEN`, `OSMO_URL`
and `OSMO_POOL` are deployment settings in `secrets.env`, not part of the runtime
payload. All supplied
service URLs must be reachable from the OSMO task network.

## Required Fields at a Glance

Every field has a default, so validation accepts an empty payload. The shipped
location and endpoint defaults are **non-working placeholders**, such as
`s3://<your-input-bucket>/<your-workflow>/input`. Always set the following
fields yourself:

- `input_path`
- `output_directory`

Set these fields when `external_services=true` (also the default):

- `cosmos.vlm_service_url`
- `cosmos.llm_service_url`
- `cosmos.image2video_service_url`

Set nothing extra for service endpoints when `external_services=false`: the
DAG deploys one shared VLM/LLM service and one image-to-video service, and you
may omit both `cosmos` and `service_lifecycle`. The Cosmos Evaluator is
configured separately as described in [Cosmos Evaluator](#cosmos-evaluator).

Consistency constraints:

- `cosmos.output_directory`, when set, must match top-level `output_directory`.
- `cosmos.external_services`, when set, must match top-level `external_services`.
- Omitted nested mode and output fields are populated from the top-level values.

## Top-Level Fields

- `input_path` (**string, always set this**): S3 location of one input image or
  a directory of images. A directory is scanned for `.jpg`, `.jpeg`, `.png`,
  `.bmp`, `.gif`, `.tiff`, and `.webp` files. The default is a placeholder path
  that fails at runtime.
- `max_images` (**integer, optional**, default: `10`): Maximum number of images
  selected from a directory after sorting. `0` or a negative value processes all
  matching images. It has no effect when `input_path` names one image.
- `output_directory` (**string, always set this**): Base S3 location for output.
  The workflow writes into `<output_directory>/<run_id>/...`. Its default is a
  placeholder path that fails at runtime.
- `external_services` (**boolean, optional**, default: `true`): Service mode.
  Set `false` to deploy a shared VLM/LLM service and an image-to-video service;
  set `true` to call the endpoints configured in `cosmos`. This switch does not
  select managed versus external Cosmos Evaluator.
- `service_lifecycle` (**object, optional**): Internal service deployment
  flags. Usually omit it; the DAG derives the flags from `external_services`.
  Set it only to override per-service replica counts.
- `cosmos` (**object, optional**): Image-to-video augmentation configuration:
  endpoint/model settings, number of videos per image, and anomaly/environment
  sampling. Refer to [`cosmos` Fields](#cosmos-fields).
- `enable_performance_reporting` (**boolean, optional**, default: `false`):
  Enables orchestration reporting. Refer to [Performance Reporting](#performance-reporting).

## Input and Output

Each input image requests `cosmos.num_augmentation` candidate videos. Every
candidate must pass its configured Cosmos Evaluator quality gates before the
DAG auto-labels it with detection and tracking, captioning, anomaly visual QA,
person-attribute visual QA, and person-attribute search. Cosmos output
validation skips, with a warning, any candidate that is missing artifacts or
fails a quality gate, and the run continues with the remaining accepted
candidates. Output validation, and therefore the run, fails only if no
candidate is accepted. Refer to [Cosmos Evaluator](#cosmos-evaluator).

The final dataset is written to:

```text
<output_directory>/<run_id>/anomaly_dataset/
  dataset.json
  <input_key>_aug0/
    raw/video.mp4
    contextual/
    sidecars/
```

`dataset.json` lists every accepted scene and its video, generated Cosmos
configuration, caption, metadata, and annotation paths. Intermediate generated
videos are under `<output_directory>/<run_id>/cosmos/`; auto-labeling artifacts
are under `<output_directory>/<run_id>/auto_labeling/`.

> **Note:** A run that reports `success` can contain fewer scenes than
> requested. Skipped candidates and Cosmos augmentations that exhaust their
> Airflow retries are left out of `dataset.json` without failing the run.
> Compare `total_scenes` in `dataset.json` with the number of processed images
> multiplied by `cosmos.num_augmentation`. The output validation task log
> lists a `Skipping ...` warning for each dropped candidate.

## `service_lifecycle` (Internal Service Overrides)

Use this only when `external_services=false` and you need to tune internal
service replica counts. The service objects are `vlm_service` (shared VLM/LLM)
and `image2video_service`; each accepts `enabled` and `replicas` (default `1`,
minimum `1`).

- When `external_services=false`, both services are enabled by default.
- When `external_services=true`, both services are disabled by default.
- Conflicting `enabled` values are normalized to the top-level service mode,
  while replica counts are retained.

Example override:

```json
{
  "external_services": false,
  "service_lifecycle": {
    "vlm_service": { "replicas": 2 },
    "image2video_service": { "replicas": 1 }
  }
}
```

There is no `service_lifecycle.llm_service` field. In internal mode,
`vlm_service` serves both multimodal and text-only requests; an `llm_service`
entry is ignored as an unknown field.

Internal augmentation concurrency is `max_concurrency` on the augmentation
task in the deployment manifest. If you increase image-to-video replicas, raise
that cap to match; otherwise extra replicas remain idle. External mode uses
`external_image2video_service_pool` instead.

## `cosmos` Fields

- `num_augmentation` (**integer, optional**, default: `1`, minimum: `1`):
  Number of candidate videos requested per input image.
- `vlm_service_url`, `llm_service_url`, `image2video_service_url` (**string,
  conditionally required**): Required when `external_services=true`.
- `vlm_model`, `llm_model`, `image2video_model` (**string, optional**): Model
  IDs sent to the services. The defaults are:
  - `vlm_model`: `Qwen/Qwen3.8-27B-FP8`
  - `llm_model`: `Qwen/Qwen3.8-27B-FP8`
  - `image2video_model`: `nvidia/Cosmos3-Super-Image2Video`
- `base_config_path` (**string, optional**): MSC-readable URI for a custom
  Cosmos YAML configuration. Omit it to use the bundled configuration. A
  custom configuration also determines which evaluator checks are available.
- `cosmos_evaluator_service_url` (**string, optional**): Root URL for an
  existing Cosmos Evaluator Arbitrator. When omitted and the selected Cosmos
  configuration enables evaluation, the DAG deploys the managed evaluator
  services declared in its Kubernetes manifest.
- `checker_overrides` (**object, optional**): Per-run strict boolean switches.
  EVG accepts `metropolis.attribute_verification` and
  `metropolis.physical_plausibility`.
- `variable_distribution` (**object, optional**): Weighted sampling of the
  anomaly and environment used to construct each generated video. If omitted,
  the deterministic default is `person_falling` in a `warehouse`.

### Cosmos Evaluator

The bundled configuration enables attribute verification and physical
plausibility as quality gates. The default empty `checker_overrides` object
leaves both enabled. To state that explicitly:

```json
{
  "cosmos": {
    "checker_overrides": {
      "metropolis.attribute_verification": true,
      "metropolis.physical_plausibility": true
    }
  }
}
```

Set either value to `false` to remove that checker for the run. If no checks
remain, the Cosmos Evaluator provider and its managed services are skipped.
Setting a checker to `true` retains it; it cannot add a checker absent from a
custom `base_config_path`. Unsupported checker names fail payload validation.

With no `cosmos_evaluator_service_url`, the DAG deploys the managed evaluator
stack when at least one effective checker remains. Supplying the URL disables
that managed stack and, when an effective checker remains, sends requests to
the external Arbitrator instead. Managed evaluator deployment applies to the
Kubernetes DAG; OSMO requires an external URL whenever a checker remains
enabled. Cosmos output validation skips, with a warning, any candidate that is
missing artifacts, has unreadable config or metadata, lacks evaluator results
while the evaluator is enabled, reports an evaluator operational failure, or
fails a quality gate. The DAG run continues with the remaining accepted
candidates; output validation fails if no candidate is accepted.

### `variable_distribution`

`variables` must contain exactly these two keys:

- `anomaly_type`: anomaly label -> non-negative sampling weight.
- `env_type`: environment label -> non-negative sampling weight.

Each distribution must contain at least one value and have a positive total
weight. Weights are relative, so they do not need to sum to one. For example:

```json
{
  "cosmos": {
    "variable_distribution": {
      "variables": {
        "anomaly_type": {
          "person_falling": 0.5,
          "person_running": 0.3,
          "person_fighting": 0.2
        },
        "env_type": {
          "warehouse": 1.0
        }
      }
    }
  }
}
```

Sampling is deterministic for a given payload: the DAG uses a fixed seed when
creating the per-augmentation configurations.

## Performance Reporting

Reporting is off by default. Enable it with one top-level flag:

```json
{
  "enable_performance_reporting": true
}
```

After output validation, it writes these files to
`<output_directory>/<run_id>/reports/`:

- `cdf_orchestration_stats.yaml`: run metadata, task timings, input-image,
  generated-video, and final-scene counts, plus throughput rates.
- `cdf_orchestration_stats.html`: a self-contained dashboard of the same
  data.

The report reads Airflow timing data through the REST API. An Airflow connection
named `airflow_api_default` must have a host plus either login/password or a
token in its `extra` field. When reporting is enabled, the report task is part
of EVG's outcome gates: the run waits for it, and a report failure fails the
DagRun. When reporting is disabled, the branch skips report generation and
writes no report files.

## Trigger the Run

1. Open the Airflow UI.
2. Enable `event_video_generation_dag_k8s`.
3. Choose **Trigger DAG w/ config**.
4. Under **Run Parameters**, replace `payload` with your payload JSON.
5. Start the run.
