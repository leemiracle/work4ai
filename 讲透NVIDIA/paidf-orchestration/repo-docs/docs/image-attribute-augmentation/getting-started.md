# Image Attribute Augmentation Getting Started

Complete the shared [Getting Started Guide](../getting-started.md) through
opening the Airflow UI, then return here to run Image Attribute Augmentation.

## Run the Workflow

1. **Construct and Upload Input Data**:

   The Image Attribute Augmentation workflow requires a user-provided image
   dataset in S3. Build a local dataset with one folder per person ID, then
   upload that folder tree to the input location in S3 expected by the starter
   payloads:

   ```text
   input_data/
      person-0001/
         0001-front.jpg
         0001-side.jpg
      person-0002/
         0002-front.png
   ```

   Input data must be images of people. You can use the
   [RSTPReid Dataset](https://github.com/NjtechCVLab/RSTPReid-Dataset) or a
   similar open-source dataset if you do not have input images available.

2. **Create a Starter Payload**:

   Before triggering the workflow, create a payload that specifies:

   - Where the input images are stored in S3.
   - Where to write the output dataset.
   - Whether to use external VLM, LLM, and image-edit endpoints or deploy one
     shared VLM/LLM service and one image-edit service internally.
   - How many augmentations to attempt per person ID.
   - Which output attributes to generate and their distribution.

   To get started quickly, copy one of the
   [starter payloads](payload-guide.md#quick-start-starter-payloads) (one for
   in-cluster services and one for external endpoints), then set:

   - `input_path` to `s3://<your-input-bucket>/<your-workflow>/input`
   - `output_directory` to your desired output path, for example
     `s3://<your-output-bucket>/<your-workflow>/output`
   - For external endpoints, the VLM, LLM, and image-edit URLs in `cosmos` and
     the VLM and LLM URLs in `event_and_person_attribute_search`

   Both starters enable managed Cosmos attribute verification. Candidates that
   fail generation or verification are excluded and listed in
   `<output_directory>/<run_id>/cosmos_skipped.json`.

   Follow the [Image Attribute Augmentation Payload Guide](payload-guide.md)
   for detailed configuration instructions.

3. **Start the Workflow from the UI**:

   > Only run one workflow at a time to avoid long queueing times or unexpected
   > issues.

   1. From the Airflow home page, select **Dags** in the left sidebar.
   2. Select `image_attribute_augmentation_dag_k8s`.
   3. Click the trigger button in the upper-right corner.
   4. Under **Run Parameters**, replace `payload` with the JSON from the
      previous step.
   5. Select **Trigger** to start the run.

   To trigger, monitor, and stop the run without the UI, follow
   [Run Workflows with the Airflow REST API](../airflow-rest-api.md) with
   `DAG_ID=image_attribute_augmentation_dag_k8s`.

4. **Monitor or Stop an Active Run**:

   Monitor progress in Airflow. To cancel a run, open the active DagRun in
   **Grid** or **Graph** view, find the running task, and mark it as failed.
   This lets the DAG run service shutdown and clean up its resources.

   **Do not delete the DagRun or DAG** from the UI. Deleting a run bypasses the
   shutdown path and can leave stale Deployments, Services, or GPU pods.

5. **Inspect the Workflow Output**:

   The final dataset is written to
   `<output_directory>/<run_id>/augmented_dataset/`; its
   `augmented_data.json` file is the canonical summary manifest. `run_id` is
   shown in the Airflow UI after the DAG is triggered.
