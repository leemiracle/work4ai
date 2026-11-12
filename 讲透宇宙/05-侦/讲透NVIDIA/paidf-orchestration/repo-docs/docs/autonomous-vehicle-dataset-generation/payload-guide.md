# Autonomous Vehicle Dataset Generation Payload Guide

A *payload* is a JSON file containing your run settings. Follow
[Getting Started](getting-started.md#run-the-workflow) to submit it in Airflow.

## Choose an Example

| Example | What it does |
| --- | --- |
| [Find a clip](../../payloads/dev/autonomous_vehicle_dataset_generation_dag/cdf-avdg-real-retrieval.json) | Returns one clip similar to your example video. |
| [Rain](../../payloads/dev/autonomous_vehicle_dataset_generation_dag/cdf-avdg-rain-generation.json) | Creates one rainy variation using RGB controls. |
| [Snow](../../payloads/dev/autonomous_vehicle_dataset_generation_dag/cdf-avdg-snow-generation.json) | Creates one snowy variation using prepared WSM controls. |
| [Daylight](../../payloads/dev/autonomous_vehicle_dataset_generation_dag/cdf-avdg-day-generation.json) | Creates one daylight variation using RGB controls. |

Use `msc://<profile>/<path>` for storage locations. Replace the profile
placeholders with your configured Multi-Storage Client (MSC) profile names,
then set the paths and a unique collection name in each example. Rain and
daylight use RGB controls at 24 frames per second and 35 generation steps.
Snow selects [World Scenario Model (WSM) controls](#wsm-controls) at 10 frames
per second and 50 steps. All three starters generate 93 frames per variation.
The workflow starts and stops its own services and uses Cosmos3-Nano.

For Azure retrieval, use the inline example in the
[Azure implementation plan](azure-support.md#test-the-complete-workflow).
After implementing Azure support, adapt the rainy RGB starter for generation
with the same Azure input and query paths and a new output location.

## Inputs and Search

Start with the [complete retrieval example](getting-started.md#2-prepare-the-run-settings),
then adjust these fields:

| Setting | What to enter |
| --- | --- |
| `input_video_path` | Dataset folder containing `<scene-id>/camera_front_wide_120fov.mp4`. |
| `query_video` | Example video to find similar clips. Required for search. |
| `output_directory` | Writable results folder, separate from the inputs. |
| `collection_name` | Unique name for this run's search collection. |
| `search_mode` | `embedding` to search; `none` to prepare and index clips only. Default: `none`. |
| `limit` | Source scenes to process. Default: `1`; `null` means all. |
| `top_k` | Maximum matches to return. Default: `10`. |
| `collect_result_clips` | Copy matching clips to the results folder. Default: `true`. |

The workflow splits front-camera videos into 9.3-second clips and skips shorter
clips. It processes the query separately from `limit` and excludes all clips
from that source. A search with no remaining matches fails.

After completing the [Azure implementation plan](azure-support.md), use
`az://<container>/<key>` paths, for example
`input_video_path: "az://av-data/videos"`,
`query_video: "az://av-data/query/example.mp4"`, and
`output_directory: "az://av-data/results/run-001"`. Configured
`msc://<profile>/<key>` aliases also resolve to their actual containers. Keep
outputs outside the input prefixes and choose a unique collection for each run.

## Generate a Variation

Use a generation example above and change `cosmos.prompt` to describe your edit,
for example: “Add falling snow while preserving the road layout and vehicle
motion.” Keep `search_mode: "embedding"` and `cosmos.enabled: true`.

| Setting under `cosmos` | What it controls |
| --- | --- |
| `control_mode` | `rgb` (default) derives edge controls from retrieved clips; `wsm` uses prepared controls. |
| `prompt` | The requested change. Required for generation. |
| `num_clips` | Matching clips to use. Omit to use all eligible clips; cannot exceed `top_k`. |
| `num_augmentation` | Variations per clip, using the same prompt. Default: `1`. |
| `num_frames` | Output length. Default: `93`. |
| `fps` | Frames per second. RGB inputs are resampled; WSM controls must match. Default: `24`. |
| `plausibility_threshold` | Accept videos with plausibility strictly above this value, from `0` to `1`. Default: `0.5`. |
| `seed` | Optional number for repeatable generation settings. |

The camera is `camera_front_wide_120fov` and output size is `1280x720`.
Source videos and controls must cover the requested length. Asking for more
clips than are available fails the run.

## RGB Controls

RGB is the default when you omit `cosmos.control_mode`. The workflow validates
selected retrieved clips and resamples them to `cosmos.fps` without changing
playback speed. Each resampled clip must contain at least `cosmos.num_frames`
frames. Cosmos3-Nano derives edge controls from these clips to guide generation;
you do not need to prepare control videos or WSM manifests.

Appearance changes can begin at the first frame. Check the generated video to
confirm that the requested edit preserves the scene and motion.

<a id="optional-wsm"></a>

## WSM Controls

World Scenario Model (WSM) controls guide scene geometry. Set
`cosmos.control_mode: "wsm"` to use them alongside the selected RGB clips.
Only WSM mode requires these prepared controls; RGB and retrieval-only runs
do not. This workflow generates video variations, not still images.
Prepare them before the run using the upstream [annotation format](https://github.com/nvidia-cosmos/cosmos-transfer2.5/blob/main/docs/world_scenario_parquet.md)
and [renderer instructions](https://github.com/nvidia-cosmos/cosmos-transfer2.5/blob/main/docs/world_scenario_video_generation.md).
The workflow does not render these controls.

Place a manifest beside each source video that may be selected:

```text
av-input/scene-001/
   camera_front_wide_120fov.mp4
   wsm/
      wsm-manifest.json
      control.mp4
```

A *manifest* is a JSON file linking the source video to its control. This example
describes a 30-second control at 10 frames per second:

```json
{
  "schema_version": 1,
  "kind": "cdf-av-wsm",
  "controls": [
    {
      "source_video": "msc://<input-profile>/av-input/scene-001/camera_front_wide_120fov.mp4",
      "camera": "camera_front_wide_120fov",
      "start_ns": 0,
      "end_ns": 30000000000,
      "uri": "msc://<input-profile>/av-input/scene-001/wsm/control.mp4",
      "num_frames": 300,
      "fps": 10,
      "size": "1280x720"
    }
  ]
}
```

Replace the paths and measurements with your control's actual values.
`start_ns` and `end_ns` are times on the source video's timeline in nanoseconds
(one second is 1,000,000,000 nanoseconds). The control must cover the selected
clip and match the requested frame rate and size. The workflow extracts the
matching section automatically. Missing or misaligned controls fail the run.

<a id="optional-cosmos-evaluator"></a>

## Results and Checks

Each run writes a folder under `output_directory`, named from its run ID with
unsupported filename characters replaced by `-`.

| File | What to read |
| --- | --- |
| `results/` | Copies of retrieved clips when `collect_result_clips` is `true`. |
| `search_result.json` | Matching clips and source locations, or an indexing summary for `search_mode: "none"`. |
| `cosmos3-nano/videos/` | Published videos that passed physical-plausibility and media checks. May be empty. |
| `cosmos3-nano/result_manifest.json` | Accepted `outputs`, `rejected` and `failed` jobs, plus validation results. Present when output validation publishes a manifest. |

### Physical-Plausibility Evaluation

Physical-plausibility evaluation is enabled automatically whenever
`cosmos.enabled` is `true`. There is no separate enable step or evaluator toggle.
The workflow starts and cleans up the evaluator database, physical-plausibility
checker and Arbitrator services. Both RGB and WSM modes use
`metropolis.physical_plausibility` to filter generated candidates.

Reserve one GPU for the checker, included in the [four-GPU generation requirement](prerequisites.md#check-capacity).
Retrieval-only runs (`cosmos.enabled: false`) skip generation and evaluation.
External evaluator URLs, `base_config_path` and `checker_overrides` are not
supported payload fields.

Only videos with plausibility strictly above `cosmos.plausibility_threshold`
(default `0.5`) and passing media validation are published to `cosmos3-nano/videos/`.
The manifest lists their `published_video` paths under `outputs` and records
low-scoring candidates under `rejected`. Rejection alone does not fail the run;
a successful run can have an empty `outputs` list and no published videos.

Missing or invalid evaluation results, evaluator errors and media-validation
failures still fail the run. If the run fails before the manifest is written,
inspect its task logs and available per-video metadata. Physical plausibility
does not confirm the requested edit or scene preservation; watch the output
before using it.

<details>
<summary>Advanced settings</summary>

Usually leave these at their defaults:

| Setting | Default / purpose |
| --- | --- |
| `cosmos.num_inference_steps` | `35`: generation steps. |
| `cosmos.guidance_scale` | `5.0`: prompt guidance strength. |
| `cosmos.timeout_seconds` | `7200`: generation request timeout in seconds. |
| `pipeline` | `cosmos_video_search_milvus`: search pipeline. |
| `ingest_mode` | `documents`: sends embedding documents to the search service. |
| `pixi_env` | `default`: Curator execution environment. |
| `object_store_endpoint` | `null`: use the endpoint configured in your MSC storage profile. |
| `job_timeout_seconds` | `900`: indexing and search readiness timeout in seconds. |

External service URLs, model selection and custom generation templates are not
payload options. Unknown fields are rejected.

</details>
