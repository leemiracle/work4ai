# Surface-Mount Technology (SMT) Defect Image Generation Payload Guide

After you have chosen a [workflow mode](getting-started.md#running-a-workflow),
use its starter payload to describe the images you want to generate. This guide
follows the same sequence as the DAG: select the component images, configure their
augmentation, then choose how AnomalyGen should use the resulting images.
The snippets show overrides to add to a starter payload, rather than complete
standalone payloads, and each is labeled with the path where it belongs.

## Contents

- [Payload Structure](#payload-structure)
- [Prepare the Golden Images](#prepare-the-golden-images)
  - [Select the Components to Render](#select-the-components-to-render)
  - [Use Another Board](#use-another-board)
  - [Adjust the Sim2real Output](#adjust-the-sim2real-output)
- [Map Components to AnomalyGen Classes](#map-components-to-anomalygen-classes)
- [Defects and Output Counts](#defects-and-output-counts)
- [Defect-Only Input](#defect-only-input)
- [Image-Edit and VLM Services](#image-edit-and-vlm-services)
  - [Image-Edit Service](#image-edit-service)
  - [AnomalyGen VLM](#anomalygen-vlm)
- [Top-Level Reference](#top-level-reference)

## Payload Structure

The payload separates image creation into two collections. `golden_generation`
defines simulation and augmentation settings, while `defect_generation` defines
the class mapping and defect requests applied to those golden images. Both
collections have a non-empty `configurations` list, with optional shared settings
in `defaults`. Each configuration has a unique `id` within its collection, which
also names its output folder.

The outline below shows where each group of settings belongs; `{...}` marks the
overrides described in the rest of this guide:

```text
{
  "api_version": "1.0",
  "pipeline_mode": "full",
  "input_scene": "s3://<bucket>/<scene>.zip",
  "output_directory": "s3://<bucket>/<output>",
  "external_services": false,
  "service_lifecycle": {"image_edit_service": {"replicas": 8}},
  "golden_generation": {
    "defaults": {
      "image_generation": {...},     // Simulation settings
      "simulation_output": {...},    // Simulation pass sent to augmentation
      "augmentation": {...}          // Prompt and image-edit settings
    },
    "configurations": [
      {"id": "golden-a"},
      {"id": "golden-b", "image_generation": {...}}
    ]
  },
  "defect_generation": {
    "defaults": {
      "anomaly_input": {...},        // Component types to AnomalyGen classes
      "anomaly_generation": {...}    // VLM, asset and model settings
    },
    "configurations": [
      {"id": "ic-bridge", "anomaly_generation": {"per_defect_counts": {"IC+bridge": 1}}}
    ]
  }
}
```

A golden configuration represents a batch: it runs simulation once and augments
all selected images. In full mode, the DAG runs every defect configuration
against each of these batches. For example, two golden configurations and three
defect configurations produce six AnomalyGen jobs, each receiving the images
from its corresponding golden batch.

To avoid repeating settings across variants, put common overrides in the
collection's `defaults` and only the differences in each configuration. The DAG
applies them over the checked-in SMT config files in this order:

```text
SMT config file → collection defaults → individual configuration
```

Dictionaries merge recursively, while lists and scalar values replace earlier
values. For defect selection, `per_defect_counts` replaces the whole dictionary
so that a variant's selection does not retain defects from its defaults.

> **Check component names carefully.** The DAG rejects unknown top-level fields
> and checks `simulation_output` and `anomaly_input`, but it accepts any other
> key under a collection's `defaults` or in a configuration. It reads only
> `image_generation`, `simulation_output` and `augmentation` for golden images,
> and `anomaly_input` and `anomaly_generation` for defects, so a misspelled or
> misplaced component name is ignored and the run uses the checked-in settings.
> Settings inside `image_generation`, `augmentation` and `anomaly_generation`
> pass to the components unchecked, so compare them with the config files.

## Prepare the Golden Images

Golden generation begins with the scene in `input_scene`. Within
`golden_generation.defaults` or an individual golden configuration, the following
overrides control what simulation renders and how the DAG processes those images:

| Override | What it controls |
| --- | --- |
| `image_generation` | Simulation settings: component selection, camera, lighting and rendering. |
| `simulation_output.pass_name` | Simulation pass whose images are used for augmentation; defaults to `component_focus`. |
| `simulation_output.image` | Optional single image, with a path relative to the simulation output directory. It must appear in the selected pass's manifest. Omit it to use all RGB images from that pass. |
| `augmentation` | Prompt and image-edit request parameters. |

The Artix preset renders four simulation passes: whole-board tiles
(`full_board`) and their segmentation masks (`full_board_roi`), which are also
stitched into full-board images, and close-up component crops
(`component_focus`) and their masks (`component_focus_roi`). Only the pass named
in `simulation_output.pass_name` is augmented; the others are saved with the
simulation output.

### Select the Components to Render

The [mixed-component example](../../payloads/dev/defect_image_generation_smt_dag/default_payload.json)
selects 24 ICs and 14 named capacitors. Its selection for the `component_focus`
pass is:

**Path:** `golden_generation.defaults.image_generation.capture.passes.component_focus`

```json
{
  "limits": {"max_images": 38},
  "roi_selection": [
    {"component_types": ["ic"], "count": 24, "padding": 0.5},
    {
      "refdes": ["C2", "C14", "C15", "C16", "C65", "C66", "C67", "C72", "C73", "C74", "C75", "C76", "C77", "C78"],
      "padding": 0.5
    }
  ]
}
```

The first selector uses the board's component metadata to choose ICs; without
`count`, a `component_types` selector chooses only one component. The second
uses `refdes` (reference designator) to choose particular capacitor instances,
such as `C2`. Both include space around each component through `padding`, and
`max_images` allows the pass to render all 38 selected components.

The example sets the same `limits` and `roi_selection` under
`component_focus_roi`, the pass that renders the matching segmentation masks. Do
the same when you change the selection; otherwise that pass keeps the preset's
24-IC selection and its masks no longer match your images.

After simulation, `simulation_output.pass_name` tells the DAG which pass to use
for augmentation. Leaving `simulation_output.image` unset sends all RGB images
from that pass to augmentation; supplying it limits augmentation to one listed
image.

### Use Another Board

The [simulation defaults](../../airflow/dags/workflows/defect_image_generation_dag/configs/smt/image_generation_config.yaml)
are a preset for the Artix board. When you use another scene, also override
these settings under `golden_generation.defaults.image_generation`:

- `scene.root` and `operations.solder_joints.options.solder_material_prim_path`:
  USD prim paths in the Artix scene, `/Board` and `/Board/Looks/SolderPaste`.
- `operations.solder_joints.options.components`,
  `annotations.component_classes.smt` and `annotations.geometry.components`: the
  Artix reference designators that receive generated solder joints and
  annotations. The preset fills all three from one YAML anchor, which a JSON
  payload cannot reuse, so set each of them.
- `roi_selection` and `limits` under `capture.passes.component_focus` and
  `capture.passes.component_focus_roi`: the components to render, as described
  above.
- `scan_grid` under `capture.passes.full_board` and
  `capture.passes.full_board_roi`: the whole-board tile grid, sized for the
  Artix board.

### Adjust the Sim2real Output

Each selected image is augmented with the prompt and image-edit settings in the
[augmentation config](../../airflow/dags/workflows/defect_image_generation_dag/configs/smt/cosmos_config.yaml).
To change them, add an `augmentation` override to the golden configuration or its
collection defaults. The outer `augmentation` key names the workflow component,
and everything inside it merges into that config file, so the file's own
`augmentation` section appears as a second level. For example, this changes the
image-edit seed from `0` to `2`:

**Path:** `golden_generation.defaults` or a golden configuration

```json
{
  "augmentation": {
    "augmentation": {
      "parameters": {
        "extra_body": {"seed": 2}
      }
    }
  }
}
```

Because dictionaries merge, the other `extra_body` settings keep their defaults:
`num_inference_steps` is `30`, `true_cfg_scale` is `4.0` and `negative_prompt`
lists artifacts to avoid, such as added text and glowing component bodies. These
are the settings released with the default model.

To change the prompt, override `captioning.llm.text`. Image-edit receives this
text directly; the SMT config does not use a language model to write prompts.
The default model, `nvidia/cdf-sim2real-smt-solderlight`, was fine-tuned on the
configured prompt only, so change it only when you serve a different image-edit
model.

**Path:** `golden_generation.defaults` or a golden configuration

```json
{
  "augmentation": {
    "captioning": {
      "llm": {
        "text": "Render this PCB component crop as a real inspection-line photograph under diffuse white light."
      }
    }
  }
}
```

These settings apply to every image in the golden batch. To replace the whole
augmentation config instead, upload your own copy to S3 and set
`cosmos.base_config_path` to its location. Keep its `image_edit` entry under
`endpoints`, which the DAG fills in with the service URL and model.

## Map Components to AnomalyGen Classes

Once the golden images are ready, the DAG prepares them for AnomalyGen. Simulation
identifies components using types such as `ic` and `capacitor`, while AnomalyGen
expects images in class folders such as `IC` and `passive_component`. In full
mode, connect those names with `anomaly_input`:

**Path:** `defect_generation.defaults`

```json
{
  "anomaly_input": {
    "class_by_component_type": {
      "ic": "IC",
      "capacitor": "passive_component"
    }
  }
}
```

The DAG preserves `component_type` through augmentation and uses this mapping
to place each image in the appropriate clean-image folder:

```text
anomaly_package/artifact/
  IC/clean_image/image_000000.png
  passive_component/clean_image/image_000001.png
```

Because each defect job receives the whole golden batch, every selected
component type needs an exact mapping. If one is missing, the run fails at the
`anomaly_package` task.

## Defects and Output Counts

With the input classes assigned, use `anomaly_generation` in each defect
configuration to choose a defect and request a number of outputs. This variant
requests three IC bridge images:

**Path:** an entry in `defect_generation.configurations`

```json
{
  "id": "ic-bridge",
  "anomaly_generation": {
    "per_defect_counts": {"IC+bridge": 3},
    "base_seed": 2
  }
}
```

Each key in `per_defect_counts` is a `class+defect` pair and its value is the
requested output count. `base_seed` sets AnomalyGen's starting random seed
(default `1`); change it to get different defects from the same inputs.

The shipped checkpoint is fine-tuned for UC1, AnomalyGen's PCB reference use
case, which supports three pairs. The starter payload requests each of them in
its own configuration:

- `IC+bridge`
- `passive_component+excess_solder`
- `passive_component+missing`

AnomalyGen resolves the total from these explicit counts. If `per_defect_counts`
is `null`, `num_sdg` supplies the total request count instead (default `1`);
explicit pairs make the desired defects clear.

These counts control output requests rather than input coverage. The DAG passes
them through unchanged, and AnomalyGen's Agentic Mask Generation (AMG) stage,
which uses the VLM to propose and judge defect masks, may reuse some clean
images or skip others. For example, requesting 24 outputs does not guarantee a
defect for each of 24 different inputs.

The full workflow and defect-only starter payloads have placeholder locations
for the UC1 recipe, checkpoint and shared assets under
`defect_generation.defaults.anomaly_generation.staging.fetch`; set them to your
S3 copies, as described in
[Prepare the payload](getting-started.md#prepare-the-payload). To use another
compatible model, replace these locations with its recipe, checkpoint and
shared assets.

## Defect-Only Input

If you already have clean component images, use `pipeline_mode: "defect"` to
start at AnomalyGen. In this mode you prepare the class folders yourself, with a
`clean_image/` folder inside each class:

```text
prepared-components/
  IC/
    clean_image/
      image_000000.png
      image_000001.png
  passive_component/
    clean_image/
      image_000002.png
```

Supply the S3 location of this dataset root, alongside the shared assets,
through `staging.fetch.input`. For example, replace the locations in this
fragment with your own:

**Path:** `defect_generation.defaults.anomaly_generation`

```json
{
  "staging": {
    "fetch": {
      "input": [
        "s3://your-bucket/anomalygen-assets/UC1/",
        "s3://your-bucket/prepared-components/"
      ]
    }
  }
}
```

AnomalyGen reads the class folders directly from the prepared dataset root.
Since the images are already classified, the DAG does not need simulation
metadata or a `class_by_component_type` mapping. The input list replaces the
defaults, so include the reference assets required by the recipe as well as your
clean images.

The shipped defect-only payload uses placeholder locations for the shared assets
and the prepared images; replace both with your own S3 paths. To reuse images
from a previous full run, list that run's
`defects/<golden_id>/<defect_id>/anomaly_package/artifact/` folder, which already
uses this layout. To reuse a golden-only run, sort its
`goldens/<golden_id>/augmentation/artifact/` images into class folders using the
component types in the adjacent `manifest.json`.

In full mode, the DAG builds and adds the golden batch itself, so the configured
input list should contain the shared reference assets rather than another
clean-image dataset.

## Image-Edit and VLM Services

The two model services have different roles: image-edit creates the golden
images, while the VLM helps AnomalyGen choose defect masks. Their settings are
independent.

Container versions, the image-edit checkpoint, GPU pools and volume mounts live
in the [SMT deployment manifest](../../airflow/dags/workflows/defect_image_generation_dag/configs/smt/defect_image_generation_k8s_manifest.yaml).
Keep per-run input locations and generation choices in the payload.

### Image-Edit Service

Image-edit is used only in `full` and `sim2real` modes. The `simulation` and
`defect` modes require no image-edit URL, regardless of `external_services`, and
keep the managed image-edit service disabled.

For internal image-edit, set `external_services: false` and tune
`service_lifecycle.image_edit_service.replicas`. Each replica uses one GPU; refer to
[service access and capacity](getting-started.md#check-service-access-and-capacity)
for sizing. Each augmentation task is a CPU pod calling the GPU service.
Concurrency of augmentation in one DAG run is `max_concurrency` on the
augmentation task in the deployment manifest (16), in both internal and external
mode. Airflow applies that value as `max_active_tis_per_dagrun`. Available
workers and service capacity still apply.

For an existing image-edit service, set `external_services: true` and provide
`cosmos.image_edit_service_url`:

**Path:** payload root

```json
{
  "external_services": true,
  "cosmos": {
    "image_edit_service_url": "http://image-edit.example.com:8000/v1",
    "image_edit_model": "nvidia/cdf-sim2real-smt-solderlight"
  }
}
```

The DAG calls the service through the OpenAI chat-completions API, which the
internal deployment serves with vLLM-Omni. It adds `/v1` to the internal
service's address itself but uses an external URL exactly as given, so include
`/v1`. Requests carry your NGC API key, so use a service that accepts it or needs
no key. `cosmos.image_edit_model` is optional and sets the model name in each
request; it defaults to the model the internal service runs. Changing the model
that the internal service runs requires a manifest update.

External mode skips the image-edit checkpoint download task entirely, so that
step requires no Hugging Face token or model-cache PVC. Full-mode AnomalyGen
retains its own checkpoint and storage requirements.

### AnomalyGen VLM

AnomalyGen uses the VLM only in `full` and `defect` modes. Set its models and
endpoint under `defect_generation.defaults.anomaly_generation`. `amg_gen_model`
proposes defect masks and `amg_judge_model` judges them; each must match a
`model` entry in `amg_endpoints`. Use GPT-6 Astra for both roles. The full
workflow and defect-only starter payloads leave the model and endpoint as
placeholders:

**Path:** `defect_generation.defaults.anomaly_generation`

```json
{
  "amg_gen_model": "<your-vlm-model>",
  "amg_judge_model": "<your-vlm-model>",
  "amg_endpoints": [
    {
      "model": "<your-vlm-model>",
      "base_url": "https://<your-vlm-endpoint>/v1"
    }
  ]
}
```

Set `model` to the name your endpoint uses for GPT-6 Astra, and `base_url` to
the endpoint's OpenAI-compatible base URL, including the version segment such as
`/v1`.

Set the endpoint's API key as `VLM_API_KEY` in `secrets.env` and apply it using
the [service setup steps](getting-started.md#check-service-access-and-capacity).
The DAG gives the same key to every entry in `amg_endpoints`, so each endpoint
you list must accept it.

## Top-Level Reference

The fields below tie these stage-specific settings together in a complete
payload. Use the linked [starter examples](getting-started.md#running-a-workflow) to
review them in context.

| Field | Purpose |
| --- | --- |
| `api_version` | Set to `"1.0"`. |
| `pipeline_mode` | `full` (default), `sim2real`, `simulation`, or `defect`. |
| `input_scene` | S3 scene or scene ZIP; required outside `defect` mode. |
| `output_directory` | Base output location; required in every mode. |
| `golden_generation` | Simulation and augmentation variants; required outside `defect` mode. |
| `defect_generation` | Class mapping and defect variants; required for `full` and `defect`. |
| `enable_performance_reporting` | `false` by default. Set `true` to write a YAML statistics file and an HTML dashboard to `<output_directory>/<run_id>/reports/`. The starter payloads set `true`. |
| `external_services` | `false` by default. Set `true` to use an existing image-edit endpoint. |
| `service_lifecycle.image_edit_service.replicas` | Internal image-edit replica count; defaults to `1`. The full and golden-only samples set `8`. |
| `service_lifecycle.image_edit_service.enabled` | Set by the DAG: `true` only for internal `full` and `sim2real` runs. Any value in the payload is replaced. |
| `cosmos` | Image-edit settings: `image_edit_service_url`, `image_edit_model` and `base_config_path`; refer to [Image-edit service](#image-edit-service) and [augmentation](#adjust-the-sim2real-output). The other fields of this shared object do not apply to SMT. |

When `enable_performance_reporting` is `true`, the report's simulation image
count includes unique RGB captures from every pass in every golden batch. It
excludes segmentation masks and derived images such as stitched outputs.
`simulation_output` only selects images for augmentation; it does not limit this
count and is ignored in simulation-only mode.
