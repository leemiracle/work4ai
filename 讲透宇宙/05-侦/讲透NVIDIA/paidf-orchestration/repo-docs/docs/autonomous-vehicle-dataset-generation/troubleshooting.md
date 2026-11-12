# Autonomous Vehicle Dataset Generation Troubleshooting

Read the first failed task’s log in Airflow and any validation files written
before the failure. Early failures may leave no result manifest.

| Symptom | What to check |
| --- | --- |
| Pod stays `Pending` | Read pod events. Check resources and whether `cosmos-curator-ffmpeg` is `Bound`. |
| `No FFmpeg sidecar at /opt/ffmpeg` | Fill the claim using the [prerequisite guide](prerequisites.md#ffmpeg-sidecar). |
| Embedding query has no matching span | For an S3 query, check the query pass in `run_curator` and the run's `query_split/` export. The query must decode and produce a span under the configured splitting/minimum-length settings. Non-S3 source/span references still require a match in the corpus export. |
| PyAV cannot decode H.264 | Use the documented FFmpeg 8.1 sidecar with an H.264 decoder; inspect the Curator log for loaded library versions. |
| Curator remains `Running` after embedding cleanup | Check writer logs and output-object timestamps: clip uploads may still be active. Wait for the task result before retrying the run. |
| Invalid WSM or generated video | Read the named file's validation error. Fix dimensions, FPS, coverage or decoding; don’t bypass the check. |
| Evaluator services stay `Pending` | Evaluation is enabled by default. Check capacity for physical plausibility. |
| Run succeeds but `videos/` is empty | Check `rejected` in `result_manifest.json`. All candidates may have failed the plausibility threshold; this is a valid empty result. |
| Evaluator reports an operational failure | Inspect the Arbitrator and checker logs using the reported request ID. An execution failure is not a quality verdict. |
| Polling returns `404 Video not found` | Inspect the managed Cosmos3 service logs, job storage and pod restarts. Keep the job ID. |
| Azure import fails inside a task | Build custom task images with the dependencies described in the [Azure implementation plan](azure-support.md#configure-azure-access). Check imports in the actual task Python environment; host packages do not propagate into containers. |
| Azure access fails after a Helm upgrade | Confirm the chart implements the `global.secrets.multistorageClient.configuration` override, include the private values file on the upgrade, and restart Airflow components after Secret changes. Check each path's profile and actual container name. |
| Checker rejects `video_path` with an unsupported URI scheme | The base checker 2.0 recognizes `azure://` but not `az://`. Build a custom checker with the URI fix and select its image in the task manifest as described in the [Azure implementation plan](azure-support.md#configure-azure-access). Keep the normal `az://` payload paths. |

Keep FFmpeg on the shared claim; installing it in the Airflow image won’t fix
the compute pods.
