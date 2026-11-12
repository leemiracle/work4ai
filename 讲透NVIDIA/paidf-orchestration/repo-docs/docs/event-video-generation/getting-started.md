# Event Video Generation Getting Started

Complete the shared [Getting Started Guide](../getting-started.md) through
opening the Airflow UI, then return here to run Event Video Generation.

> **OSMO: EXTERNAL ENDPOINTS ONLY:** Never use
> `external_services: false` with `event_video_generation_dag_osmo`. Supply
> external VLM, LLM, and image-to-video URLs. Supply an external Cosmos
> Evaluator URL too whenever an evaluator check is enabled. The OSMO manifest
> cannot deploy any of these services.

## Run the Workflow

1. **Construct and Upload Input Data**:

   Upload one source image or a directory of source images to S3. Event Video
   Generation supports `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.tiff`, and
   `.webp` files. For example:

   ```text
   event-video-input/
      warehouse-entrance.jpg
      loading-dock.png
   ```

2. **Create a Starter Payload**:

   For in-cluster services, start with
   [`warehouse-safety-mix-internal-10.json`](../../payloads/dev/event_video_generation_dag/warehouse-safety-mix-internal-10.json).
   **This internal starter is for `event_video_generation_dag_k8s` only. Never
   use it with `event_video_generation_dag_osmo`.**
   For external endpoints, start with
   [`warehouse-safety-mix-external-10.json`](../../payloads/dev/event_video_generation_dag/warehouse-safety-mix-external-10.json).
   In either case, set:

   - `input_path` to your image or image-directory S3 path.
   - `output_directory` to your desired output path, for example
     `s3://<your-output-bucket>/<your-workflow>/output`.

   For external services, replace the VLM, LLM, and image-to-video URLs in
   `cosmos`; the checked-in payload contains deployment-specific values. Also
   replace `cosmos.cosmos_evaluator_service_url` with your Arbitrator root URL,
   or remove it to use the Kubernetes workflow's managed evaluator. Refer to the
   [Event Video Generation Payload Guide](payload-guide.md) for all fields and
   additional starter payloads.

   For `event_video_generation_dag_osmo`, use an external-services payload
   only. Supply all three inference endpoint URLs. OSMO cannot deploy a managed
   Cosmos Evaluator, so also supply an external Arbitrator URL whenever either
   evaluator check is enabled. Refer to
   [OSMO Payloads: External Endpoints Only](payload-guide.md#osmo-payloads-external-endpoints-only).

3. **Start the Workflow from the UI**:

   > Only run one workflow at a time to avoid long queueing times or unexpected
   > issues.

   1. From the Airflow home page, select **Dags** in the left sidebar.
   2. Select `event_video_generation_dag_k8s`, or
      `event_video_generation_dag_osmo` for an external-endpoint OSMO run.
   3. Click the trigger button in the upper-right corner.
   4. Under **Run Parameters**, replace `payload` with the JSON from the
      previous step.
   5. Select **Trigger** to start the run.

   To trigger, monitor, and stop the run without the UI, follow
   [Run Workflows with the Airflow REST API](../airflow-rest-api.md) with
   `DAG_ID=event_video_generation_dag_k8s` (or `event_video_generation_dag_osmo`).

4. **Monitor or Stop an Active Run**:

   Monitor progress in Airflow. To cancel a run, open the active DagRun in
   **Grid** or **Graph** view, find the running task, and mark it as failed.
   This lets the DAG run service shutdown and clean up its resources.

   **Do not delete the DagRun or DAG** from the UI. Deleting a run bypasses the
   shutdown path and can leave stale Deployments, Services, or GPU pods.

5. **Inspect the Workflow Output**:

   The final anomaly dataset is written to
   `<output_directory>/<run_id>/anomaly_dataset/`. Its `dataset.json` manifest
   lists every accepted scene and its video and annotation paths. Candidates
   that are incomplete or fail a configured Cosmos Evaluator quality gate are
   skipped and left out of the dataset; the run fails if no candidate is
   accepted. Augmentations that exhaust their Airflow retries are also left
   out while the run still reports `success`, so compare `total_scenes` in
   `dataset.json` with the number of processed images multiplied by
   `cosmos.num_augmentation`.

## Fine-Tuning and Calibration (Optional)

Event Video Generation uses Cosmos Evaluator to assess generated videos before
including them in the output dataset. Its physical plausibility checker uses a
learned classifier to score temporal plausibility; candidates that fail an
enabled quality gate are excluded from the dataset.

The [Physical Plausibility Checker notebook](https://github.com/NVIDIA/cosmos-evaluator/blob/main/docs/tutorials/train_physical_plausibility_checker.ipynb)
walks through preparing labeled videos, extracting frozen video embeddings,
training or fine-tuning a lightweight classifier, calibrating its operating
threshold, and exporting a checkpoint bundle. Use validation examples from your
application to choose the threshold, then assess the checker on held-out test
videos before deployment.

To use the exported checker, configure its checkpoint in Cosmos Evaluator as
described in [Model Setup](https://github.com/NVIDIA/cosmos-evaluator/blob/main/docs/checks/physical_plausibility.md#model-setup),
then point `cosmos.cosmos_evaluator_service_url` to that deployment's Arbitrator
root URL. See the [Cosmos Evaluator settings](payload-guide.md#cosmos-evaluator)
for enabling the check and configuring the endpoint in this workflow.
