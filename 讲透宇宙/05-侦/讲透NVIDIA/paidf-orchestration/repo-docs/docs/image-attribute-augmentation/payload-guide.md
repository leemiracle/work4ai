# Image Attribute Augmentation Payload Guide

This guide describes the JSON payload you provide when triggering
`image_attribute_augmentation_dag_k8s` in Airflow.

## Quick Start: Starter Payloads

Use one of these as your starting point. Both examples spell out `cosmos` and
`event_and_person_attribute_search` so the payload shape is easy to follow; in
`external_services=false` mode you can omit both objects and take the defaults.

### In-cluster services (`external_services=false`)

```json
{
  "input_path": "s3://<your-input-bucket>/<your-workflow>/input",
  "output_directory": "s3://<your-output-bucket>/<your-workflow>/output",
  "external_services": false,
  "max_imgs": 1,
  "cosmos": {
    "checker_overrides": {
      "metropolis.attribute_verification": true
    },
    "num_augmentation": 1,
    "variable_distribution": {
      "variables": {
        "top_outer_color": { "black": 1.0 },
        "top_outer_type": { "hoodie": 1.0 },
        "bottom_type": { "jeans": 1.0 },
        "bottom_color": { "blue": 1.0 },
        "shoe_type": { "sneakers": 1.0 },
        "shoe_color": { "white": 1.0 }
      }
    }
  },
  "event_and_person_attribute_search": {
    "mode": "image_pas"
  }
}
```

### External services (`external_services=true`)

```json
{
  "input_path": "s3://<your-input-bucket>/<your-workflow>/input",
  "output_directory": "s3://<your-output-bucket>/<your-workflow>/output",
  "external_services": true,
  "max_imgs": 1,
  "cosmos": {
    "vlm_service_url": "https://<your-vlm-endpoint>/v1",
    "llm_service_url": "https://<your-llm-endpoint>/v1",
    "image_edit_service_url": "https://<your-image-edit-endpoint>/v1",
    "checker_overrides": {
      "metropolis.attribute_verification": true
    },
    "num_augmentation": 1,
    "variable_distribution": {
      "variables": {
        "top_outer_color": { "black": 1.0 },
        "top_outer_type": { "hoodie": 1.0 },
        "bottom_type": { "jeans": 1.0 },
        "bottom_color": { "blue": 1.0 },
        "shoe_type": { "sneakers": 1.0 },
        "shoe_color": { "white": 1.0 }
      }
    }
  },
  "event_and_person_attribute_search": {
    "mode": "image_pas",
    "vlm_service_url": "https://<your-vlm-endpoint>/v1",
    "llm_service_url": "https://<your-llm-endpoint>/v1"
  }
}
```

Both examples use the workflow's managed Cosmos Evaluator for attribute
verification. To use an existing evaluator instead, set
`cosmos.cosmos_evaluator_service_url` to its Arbitrator root URL. Evaluator
placement is independent of `external_services`, which controls the VLM/LLM
and image-edit endpoints.

## Required Fields at a Glance

Every field carries a default, so validation will not reject a payload that
omits these. The shipped defaults for locations and endpoints are **non-working
placeholders** such as `s3://<your-input-bucket>/<your-workflow>/input`, so a
payload that leaves them out is accepted and then fails at runtime when a task
tries to read the placeholder. Treat the fields below as required in practice
and always set them yourself.

Always set:

- `input_path`
- `output_directory`

Set when `external_services=true` (or omitted, since the default is `true`):

- `cosmos.vlm_service_url`
- `cosmos.llm_service_url`
- `cosmos.image_edit_service_url`
- `event_and_person_attribute_search.vlm_service_url`
- `event_and_person_attribute_search.llm_service_url`

Set nothing extra for VLM/LLM or image-edit endpoints when
`external_services=false`: the workflow deploys one shared VLM/LLM service and
one image-edit service. `cosmos` and `event_and_person_attribute_search` can be
omitted because the DAG builds them from top-level values. The Cosmos Evaluator
is configured separately as described in [Cosmos Evaluator](#cosmos-evaluator).

Consistency constraints:

- `cosmos.output_directory` and
  `event_and_person_attribute_search.output_directory` are optional and can be
  omitted from payloads.
- If either nested `output_directory` is set, it must match top-level
  `output_directory`.
- If set, `cosmos.external_services` and
  `event_and_person_attribute_search.external_services` must match top-level
  `external_services`.
- Omitted nested mode/output fields are populated from top-level values.

## Top-Level Fields

- `input_path` (**string, always set this**): S3 location of your input dataset. Image Attribute Augmentation
  expects one folder per person ID. Defaults to a placeholder path that does not
  exist, so omitting it fails at runtime rather than during validation.
- `output_directory` (**string, always set this**): Base S3 location for outputs. Image Attribute Augmentation
  writes its final dataset to `<output_directory>/<run_id>/augmented_dataset/`;
  `augmented_data.json` in that directory is the canonical summary manifest.
  The default is a placeholder path that does not exist.
- `external_services` (**boolean, optional**, default: `true`): Service mode.
  Set `false` to deploy a shared VLM/LLM service and an image-edit service;
  set `true` to call your endpoints. This switch does not select managed versus
  external Cosmos Evaluator. There are no top-level `vlm`/`llm` URL fields.
- `max_imgs` (**integer, optional**, default: `1`): Maximum number of person-ID
  folders to process. `null`, `0`, or a negative value means process all.
- `service_lifecycle` (**object, optional**): Internal service deployment flags.
  Usually omitted; Image Attribute Augmentation auto-populates it from
  `external_services`. Provide it only when you want to override per-service
  replica counts.
- `cosmos` (**object, optional**): Augmentation task config: how many
  augmentation candidates to attempt per person ID and which outfit attributes
  to sample.
  Set it when `external_services=true` so it carries real endpoint URLs, since
  the shipped URL defaults are placeholders. Refer to
  [`cosmos` Fields](#cosmos-fields-augmentation).
- `event_and_person_attribute_search` (**object, optional**): Attribute search
  task config: the pipeline mode and the models used to label augmented images.
  Set it when `external_services=true` so it carries real `vlm_service_url` and
  `llm_service_url` values.
  Refer to
  [`event_and_person_attribute_search` Fields](#event_and_person_attribute_search-fields).
- `enable_performance_reporting` (**boolean, optional**, default: `false`):
  Turns the orchestration report on. Refer to
  [Performance Reporting](#performance-reporting).

## `service_lifecycle` (Internal Service Overrides)

Use this only when `external_services=false` and you want to tune internal
service replica counts.

Fields:

- `vlm_service` (shared VLM/LLM) and `image_edit_service` (objects)
- `enabled` (**bool, optional**)
- `replicas` (**int, optional**, default: `1`, minimum: `1`)

Defaults from top-level `external_services`:

- If `external_services=false`, Image Attribute Augmentation enables both
  internal services by default.
- If `external_services=true`, Image Attribute Augmentation disables both
  internal services by default.

If you set `enabled` values that conflict with top-level `external_services`,
Image Attribute Augmentation normalizes `enabled` to match top-level mode during
validation and logs a warning. Replica counts you set are kept.

Example override:

```json
{
  "external_services": false,
  "service_lifecycle": {
    "vlm_service": { "replicas": 2 },
    "image_edit_service": { "replicas": 4 }
  }
}
```

There is no `service_lifecycle.llm_service` field. In internal mode,
`vlm_service` serves both multimodal and text-only requests; an `llm_service`
entry is ignored as an unknown field.

## `cosmos` Fields (Augmentation)

- `num_augmentation` (**integer, optional**, default: `1`): Number of
  augmentation candidates attempted per person ID.
- `vlm_service_url`, `llm_service_url`, `image_edit_service_url`
  (**string, conditionally required**): Required when `external_services=true`.
- `vlm_model`, `llm_model`, `image_edit_model` (**string, optional**): Model
  IDs sent to endpoints. Use values compatible with your deployed
  containers/endpoints.
- Default values used when omitted:
  - `vlm_model`: `Qwen/Qwen3.8-27B-FP8`
  - `llm_model`: `Qwen/Qwen3.8-27B-FP8`
  - `image_edit_model`: `Qwen/Qwen-Image-Edit-2511`
- Specify these fields when your endpoint/container expects model IDs that are
  different from the defaults, or when you want to override models per run.
- `variable_distribution` (**object, optional**): Controls attribute variety.
  If omitted, Image Attribute Augmentation uses a deterministic default outfit.
  A supplied object replaces that default; only the attributes present in the
  supplied object are sampled.
- `base_config_path` (**string, optional**): MSC-readable URI (`s3://`,
  `http://`, or `https://`) for a custom Cosmos YAML configuration. Omit it to
  use the bundled configuration. A custom configuration also determines which
  evaluator checks are available.
- `cosmos_evaluator_service_url` (**string, optional**): Root URL for an
  existing Cosmos Evaluator Arbitrator. When omitted and the selected Cosmos
  configuration enables evaluation, the DAG deploys the managed evaluator
  services declared in its Kubernetes manifest.
- `checker_overrides` (**object, optional**): Per-run checker switches. This DAG
  accepts only `metropolis.attribute_verification`, with a strict boolean value.

> **Internal image-edit replicas and concurrency:** If you deploy more than one
> internal image-edit replica (`service_lifecycle.image_edit_service.replicas`),
> set `max_concurrency` on the augmentation task in the deployment manifest to
> the same number. Otherwise Airflow limits throughput to that cap. Rebuild and
> roll the Airflow image after changing the manifest. Refer to
> [Scale internal model throughput](../advanced-usage.md#scale-internal-model-throughput).

### Cosmos Evaluator

The bundled Cosmos configuration enables
`metropolis.attribute_verification` as a quality gate. The default empty
`checker_overrides` object leaves that configuration unchanged. To state the
default explicitly:

```json
{
  "cosmos": {
    "checker_overrides": {
      "metropolis.attribute_verification": true
    }
  }
}
```

Set the value to `false` to remove the checker for that run. If no checks remain,
the Cosmos Evaluator provider and its managed services are skipped. Setting a
checker to `true` retains it; it cannot add a checker that is absent from a
custom `base_config_path`. Unsupported checker names fail payload validation.

With no `cosmos_evaluator_service_url`, the DAG deploys the managed evaluator
stack when an effective checker remains. Supplying the URL disables that
managed stack and, when an effective checker remains, sends requests to the
external Arbitrator instead.

Each generated candidate is checked before attribute search. Failed generation
or attribute verification removes that candidate from downstream processing and
records the reason in
`<output_directory>/<run_id>/cosmos_skipped.json`. The run fails if no candidate
passes.

### `variable_distribution`

Use this to control how outfit attributes are sampled.

- `variables`: attribute -> weighted choices.
- `conditional_variables` (optional): attribute distributions that depend on
  another sampled attribute.

Supplying `variable_distribution` **replaces** the built-in distribution rather
than merging with it. The schema permits a subset of attributes; only supplied
attributes are sampled and passed into the generated Cosmos configuration. For
a complete outfit description, include `top_outer_color`, `top_outer_type`,
`bottom_type`, `bottom_color`, `shoe_type`, and `shoe_color`. An attribute can
appear in either `variables` or `conditional_variables`. Omit
`variable_distribution` entirely to use the default outfit.

```json
{
  "cosmos": {
    "variable_distribution": {
      "variables": {
        "top_outer_color": { "black": 0.34, "blue": 0.33, "red": 0.33 },
        "top_outer_type": { "hoodie": 0.5, "vest": 0.5 },
        "bottom_type": { "jeans": 1.0 },
        "bottom_color": { "blue": 1.0 },
        "shoe_type": { "boots": 0.5, "sneakers": 0.5 }
      },
      "conditional_variables": {
        "shoe_color": {
          "depends_on": "shoe_type",
          "distributions": {
            "boots": { "black": 0.6, "brown": 0.4 },
            "sneakers": { "black": 0.5, "white": 0.5 }
          }
        }
      }
    }
  }
}
```

Validation rules:

- Every distribution must have a positive total weight.
- `variables` must contain at least one entry.
- `conditional_variables.<name>.depends_on` must reference a directly sampled
  parent available from `variables`.
- Conditional distributions must cover every possible parent value.

## `event_and_person_attribute_search` Fields

- `mode` (**string, optional**, default: `image_pas`): Pipeline mode passed to
  the attribute search service.
- `vlm_service_url`, `llm_service_url` (**string, conditionally required**):
  Both are required when `external_services=true`.
- `vlm_model`, `llm_model` (**string, optional**): Model IDs sent to
  endpoints. Use values compatible with your deployed containers/endpoints.
- Default values used when omitted:
  - `vlm_model`: `Qwen/Qwen3.8-27B-FP8`
  - `llm_model`: `Qwen/Qwen3.8-27B-FP8`
- Specify these fields when your endpoint/container expects model IDs that are
  different from the defaults, or when you want to override models per run.

## Performance Reporting

Reporting is off by default. Turn it on with one top-level flag:

```json
{
  "enable_performance_reporting": true
}
```

Set it to `false`, or leave it out, to turn reporting off.

### What It Produces

After output validation, two files are written to
`<output_directory>/<run_id>/reports/`:

- `cdf_orchestration_stats.yaml`: run metadata, per-task timings, workload
  counts (inputs, successful augmentations, final dataset) and throughput rates.
- `cdf_orchestration_stats.html`: a self-contained dashboard of the same
  data. Everything is embedded, so it opens straight from storage with no
  network access.

### Prerequisite: Airflow API connection

Timings come from the Airflow REST API, so an Airflow connection named
`airflow_api_default` must exist, with a host plus either a login and password
or a token in its `extra` field. If it is missing or incomplete, the report task
fails with an `AirflowApiError`.

### Effect on the run

Reporting observes the run instead of taking part in it. It hangs off
`validated_output` as its own terminal branch and is never upstream of
`pipeline_success`, so a failing report cannot fail an otherwise successful run
or delay `pipeline_success`. The DagRun remains active until the terminal report
branch finishes. When the flag is off, the branch short-circuits to
`performance_reporting.skip_report` and writes nothing.

## Full Example with External Services and Variety

```json
{
  "input_path": "s3://<your-input-bucket>/<your-workflow>/input",
  "output_directory": "s3://<your-output-bucket>/<your-workflow>/output",
  "external_services": true,
  "max_imgs": 10,
  "cosmos": {
    "vlm_service_url": "https://<your-vlm-endpoint>/v1",
    "llm_service_url": "https://<your-llm-endpoint>/v1",
    "image_edit_service_url": "https://<your-image-edit-endpoint>/v1",
    "num_augmentation": 3,
    "variable_distribution": {
      "variables": {
        "top_outer_color": { "black": 0.5, "blue": 0.5 },
        "top_outer_type": { "hoodie": 1.0 },
        "bottom_type": { "jeans": 1.0 },
        "bottom_color": { "blue": 1.0 },
        "shoe_type": { "boots": 0.5, "sneakers": 0.5 }
      },
      "conditional_variables": {
        "shoe_color": {
          "depends_on": "shoe_type",
          "distributions": {
            "boots": { "black": 0.6, "brown": 0.4 },
            "sneakers": { "black": 0.5, "white": 0.5 }
          }
        }
      }
    }
  },
  "event_and_person_attribute_search": {
    "mode": "image_pas",
    "vlm_service_url": "https://<your-vlm-endpoint>/v1",
    "llm_service_url": "https://<your-llm-endpoint>/v1"
  },
  "enable_performance_reporting": false
}
```

## Trigger the Run

1. Open the Airflow UI.
2. Enable `image_attribute_augmentation_dag_k8s`.
3. Choose **Trigger DAG w/ config**.
4. Under **Run Parameters**, replace `payload` with your payload JSON.
5. Start the run.
