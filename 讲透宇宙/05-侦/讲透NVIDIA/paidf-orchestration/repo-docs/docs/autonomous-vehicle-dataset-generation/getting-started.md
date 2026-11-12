# Autonomous Vehicle Dataset Generation Getting Started

Find driving clips similar to an example video with Cosmos Curator and Cosmos Dataset Search.
Optionally generate rain, snow or daylight video variations with Cosmos3-Nano,
using RGB input controls by default or optional World Scenario Model (WSM) controls. Every generation
run includes physical-plausibility evaluation. The workflow manages its own services.

## Before You Start

Complete the [setup guide](../getting-started.md) and open Airflow.
Check the [AV prerequisites](prerequisites.md), including GPU capacity
and the shared FFmpeg installation at `/opt/ffmpeg`. Your workflow must be able
to read the input bucket and write to the output bucket.

See [Azure Support](azure-support.md) for the implementation and setup requirements for Azure inputs, intermediate artifacts, and outputs.

## Run the Workflow



### 1. Upload Your Videos

```text
msc://<input-profile>/
   av-input/scene-001/camera_front_wide_120fov.mp4
   av-query/camera_front_wide_120fov.mp4
```

Keep this folder layout and filename. Use videos at least 9.3 seconds long.
The workflow searches `av-input` for clips similar to the example in `av-query`.
It excludes clips from the example video's source.

### 2. Prepare the Run Settings

Copy these run settings to define your payload. Replace `<input-profile>` and
`<output-profile>` with your configured storage profile names and give `collection_name` a unique value for each new run:

For Azure, first complete the changes in the
[Azure implementation plan](azure-support.md). Then use the
[Azure input, query, and output paths](azure-support.md#choose-the-file-locations)
for `input_video_path`, `query_video`, and `output_directory` in the examples.
The remaining settings apply to both storage backends.

```json
{
  "input_video_path": "msc://<input-profile>/av-input",
  "output_directory": "msc://<output-profile>/av-output/retrieval",
  "collection_name": "replace-with-unique-av-retrieval",
  "search_mode": "embedding",
  "query_video": "msc://<input-profile>/av-query/camera_front_wide_120fov.mp4",
  "top_k": 1,
  "limit": 1,
  "collect_result_clips": true,
  "cosmos": {
    "enabled": false
  }
}
```

This searches one source video and requests one matching clip. The same
[starter file](../../payloads/dev/autonomous_vehicle_dataset_generation_dag/cdf-avdg-real-retrieval.json)
is available in the repository. See the [Payload Guide](payload-guide.md) to
change the number of inputs or results.

### 3. Start the Run

1. In Airflow, select **Dags**.
2. Open `autonomous_vehicle_dataset_generation_dag_k8s` and enable it if paused.
3. Click the trigger button in the upper-right corner.
4. Under **Run Parameters**, replace `payload` with your edited JSON.
5. Select **Trigger**. Follow progress in **Grid** or **Graph** view.

For API submission, monitoring and cancellation, follow
[Run Workflows with the Airflow REST API](../airflow-rest-api.md) with
`DAG_ID=autonomous_vehicle_dataset_generation_dag_k8s`.

### 4. Read the Results

Wait for Airflow to show `success`. With the example above, look under:

```text
msc://<output-profile>/av-output/retrieval/<run-folder>/
   search_result.json
   results/
```

Each run gets its own folder. `search_result.json` lists matches under `hits`;
`results/` contains copies of the matched clips. The `collect_results` task log
reports the exact result location.

## Next Step: Generate a Variation



To create a variation next, use the [rain example](../../payloads/dev/autonomous_vehicle_dataset_generation_dag/cdf-avdg-rain-generation.json).

After implementing Azure support, adapt this RGB starter using the same Azure
input and query paths and a new output location.

For prepared [World Scenario Model (WSM) controls](payload-guide.md#wsm-controls),
use the [snow example](../../payloads/dev/autonomous_vehicle_dataset_generation_dag/cdf-avdg-snow-generation.json),
which explicitly selects `cosmos.control_mode: "wsm"`.

Generation publishes accepted videos under `cosmos3-nano/videos/` and records
accepted, rejected and failed jobs in `cosmos3-nano/result_manifest.json`.
A run can succeed with no accepted videos. Watch accepted outputs to confirm
they also match your requested change. Physical-plausibility evaluation starts
automatically with `cosmos.enabled: true`. See [Physical-Plausibility Evaluation](payload-guide.md#physical-plausibility-evaluation).

## How Long Does a Run Take?

The table shows recorded task durations in **minutes** from a sample run. The run processed 20 input
scenes, about 20 seconds each, and generated one accepted RGB-controlled clip
with 100 frames at 24 frames per second, `1280x720` resolution and 35 generation
steps. The machine had **4 NVIDIA H100 80 GB GPUs**.


| Stage                                            | Time (min) |
| ------------------------------------------------ | ---------- |
| Curator processing                               | 4.63       |
| Input video checks and reconciliation            | 8.18       |
| CDS ingestion and search                         | 0.74       |
| Retrieve and validate matches                    | 0.73       |
| RGB preparation, resampling and checks           | 1.35       |
| Generation task (includes physical plausibility) | 5.84       |
| Output validation and publishing                 | 1.53       |
| Full run                                         | 31.80      |




## Troubleshooting


| Symptom                                                              | What to check                                                                                                                                                        |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Curator or a media probe pod stays `Pending`                         | Inspect pod events for unavailable resources or an absent/unbound `shared-ffmpeg` claim. Follow [Prerequisites](prerequisites.md).                                   |
| `No shared FFmpeg installation at /opt/ffmpeg`                       | The mounted claim lacks `bin/ffmpeg` or `bin/ffprobe`. Have the administrator fill it with a build meeting the [FFmpeg requirements](prerequisites.md#requirements). |
| H.264 decode or control extraction fails                             | Verify the FFmpeg libraries, H.264 decoder and `libopenh264` encoder against the [requirements](prerequisites.md#requirements).                                      |
| No matching clips remain                                             | Check the input videos and query. All clips from the query source are excluded; include a different source scene.                                                    |
| RGB input validation fails                                           | Check that the source decodes and has enough frames after resampling to `cosmos.fps`. See [RGB Controls](payload-guide.md#rgb-controls).                             |
| WSM validation fails in `wsm` mode                                   | Check each selected source's `wsm/wsm-manifest.json`, control coverage, camera, FPS and dimensions. See [WSM Controls](payload-guide.md#wsm-controls).               |
| Physical-plausibility results are missing or evaluation errors occur | Inspect the generation task and managed evaluator service logs. Missing or invalid results and evaluator errors fail the run.                                        |
| Run succeeds but `cosmos3-nano/videos/` is empty                     | Check `rejected` in the result manifest. Videos that do not pass `cosmos.plausibility_threshold` are filtered out.                                                   |




## Agent Usage

Ask your agent to use `cdf-autonomous-vehicle-dataset-generation` with your
input, query and output locations. For example:

> Prepare the rain-generation starter with default RGB controls using my configured
> storage profiles. Return the payload and Airflow steps; do not submit.



## Get Help or Stop a Run

If a run fails, open the first failed task's log. For missing video tools or
resource shortages, check [prerequisites](prerequisites.md). For missing matches
or controls, check [input settings](payload-guide.md#inputs-and-search) and
[WSM controls](payload-guide.md#wsm-controls).

To stop a run, mark its running task as failed so cleanup can run. Do not delete
the DagRun or DAG; doing so bypasses cleanup.



Set up the [shared FFmpeg installation](prerequisites.md#shared-ffmpeg-installation)
used by workflow containers at `/opt/ffmpeg`.
