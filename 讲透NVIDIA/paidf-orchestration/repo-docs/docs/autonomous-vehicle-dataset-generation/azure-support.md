# Use Azure Storage with AV Dataset Generation

The goal is to read source videos from Azure, process them, and save all results
back to Azure. This includes temporary files, search results, and generated
videos. Model files can stay on local storage.

This guide is an implementation plan. Complete the chart, task manifest,
storage helper, and task image changes below before running the Azure workflow.
Verify the complete workflow after implementing these changes.

## Choose the File Locations

The workflow needs three locations:

| Setting | What it contains | Example |
| --- | --- | --- |
| `input_video_path` | The videos to search and process | `az://av-data/videos` |
| `query_video` | A video used to find similar clips | `az://av-data/query/example.mp4` |
| `output_directory` | Files created by this run | `az://av-data/results/run-001` |

Here, `av-data` is the Azure container. All three locations can use the same
container, as shown, or different containers. Look up the access settings for
each location instead of assuming they are all the same.

Keep source videos in this layout beneath `input_video_path`:
`<scene-id>/camera_front_wide_120fov.mp4`.

## Configure Azure Access

Prepare storage settings, task images, and Curator credentials before starting
the workflow. Each task runs in its own container, so Azure access configured on
the host or in Airflow alone does not give every task the libraries and
credentials it needs. Check access from the task containers before running a
full test to catch these problems before spending GPU time on processing and
generation.

1. **Add storage configuration support.** Extend the
   [Helm Secret template](../../deploy/templates/secrets.yaml) to accept Azure
   MSC profiles through `global.secrets.multistorageClient.configuration`.
   The existing template generates S3 profiles; add support for this override
   before using it in a private values file such as
   `deploy/secret_values_dev.yaml`. Include that file when installing or
   upgrading the chart.

   - Set each profile's `storage_provider.options.base_path` to the container
     name, configure its Azure endpoint, and supply its credentials
     through a private connection string. Add path mappings when using `msc://`
     aliases.
   - Give input and query locations read/list access, and output locations
     write access. Keep credentials out of payloads and logs.
   - Have the chart write the profiles to
     `multistorageclient-configuration-secret` and pass them to Airflow and task
     containers as `MULTISTORAGECLIENT_CONFIGURATION`. Keep the private values file
     outside version control and include it on every Helm upgrade so the Azure
     profiles and credentials remain configured.
   - After changing the Secret, restart the Airflow scheduler, DAG processor,
     API server, and triggerer so they load the new settings.
   - **Check:** From a task container, read the source and query locations and
     write a small file to the output location using their configured profiles.

2. **Prepare the task images.** Install Azure dependencies in the Python
   environment used by each task.

   - Include MSC's Azure Blob extra in the Airflow image and Azure Blob support
     in the augmentation worker's `uv` environment. Curator 2.3.0 and Cosmos
     Dataset Search 1.2.0 already include Azure Blob support.
   - Build a custom physical-plausibility checker image from the
     [Cosmos Evaluator](https://github.com/NVIDIA/cosmos-evaluator) repository.
     Install `azure-identity` and its dependencies for the checker's bundled
     Python 3.13 environment. Install them with Python 3.13
     in a separate build stage, copy the installed packages into
     `/opt/azure-extra` in the checker image, and add that directory to
     `PYTHONPATH`, preserving any existing entries. Installing the package in
     an unrelated system Python environment will not make it available to the
     checker.
   - Update `is_remote_path` in `checks/utils/multistorage.py` to accept
     `az://` while keeping the existing schemes. In the published checker 2.0
     image, the module is at
     `/app/rest_api_deployment.runfiles/_main/checks/utils/multistorage.py`.
     The base checker recognizes `azure://` instead, so it rejects the
     generated video's `az://` path before downloading or scoring it.
     Include both changes in the rebuilt image so they are present whenever a
     new checker container starts.
   - Make the rebuilt images available to the compute nodes, either through an
     accessible container registry or by importing them into each node's
     Kubernetes container runtime. Select the augmentation image with the
     existing `avdg_augmentation_image` Airflow variable. Use a new tag after
     rebuilding so a node does not reuse a cached older image.
   - Set `container_image` for `cosmos_evaluator_physical_plausibility` in the
     [task manifest](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/configs/autonomous_vehicle_dataset_generation_k8s_manifest.yaml)
     to the rebuilt checker's image reference, including its tag. To select it
     through Airflow, first add an `avdg_physical_plausibility_image` variable
     override to that manifest. Setting the variable alone does not change the
     bundled checker image.
   - **Check:** In each task's Python environment, confirm Azure imports work.
     Confirm the checker can download and evaluate an `az://` video. Packages
     installed only on the host are not enough.

3. **Add Curator credential support.** Extend the
   [credential helper](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/callables/msc_credentials.py)
   to create Curator's Azure credential file from MSC secrets. Update the task
   startup command to call this helper before processing starts.

   - For Curator 2.3.0, write `/dev/shm/azure_creds_file` with one section per
     actual Azure container and an `azure_connection_string` entry in each
     section. Use container names rather than MSC profile aliases.
   - Give separate input, query, and output containers their own sections and
     credentials. This format cannot represent different credentials for the
     same container; resolve any conflicts before starting Curator.
   - Implement percent-sign escaping for URL-encoded SAS tokens in the
     credential helper so the values survive Curator's INI parser unchanged.
   - Set file permissions to `0600` and make the file readable by the processing
     user. Keep it private and keep its contents out of logs.
   - **Check:** From Curator's actual Pixi environment, read a source video and
     query video and write a small file to the output location.

## Code Changes

Follow these steps in order. The checks at the end of each step help catch
problems before starting a full run.

1. **Add shared functions for Azure files.** Use the Azure Blob SDK or the Azure
   support in Multi-Storage Client (MSC). MSC stores connection settings in
   named profiles.
   - Add functions to list files, check whether they exist, download them, and
     upload results. Have each function select the settings for the supplied
     file path.
   - Support `az://` paths and `msc://` profile names. Read the actual container
     from the profile's `base_path`; its name may differ from the profile name.
   - **Check:** Upload a small file, list it, download it, and compare its
     contents. Repeat with a profile name that differs from the container name.

2. **Find the source and query videos.** Edit the
   [run settings](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/models/payload.py),
   [video discovery](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/callables/input_preparation.py),
   and [processing configuration](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/callables/config_generation.py).

   - Allow the three Azure paths shown above. Look up the settings for each
     path separately so input, query, and output can use different containers.
   - Keep the source video directory layout and video limits. Include Azure
     query videos in the separate query-processing step.
   - Save the configuration files and video lists under `output_directory`.
     Apply the same file-access functions to WSM control videos if using that
     generation mode.
   - **Check:** Video discovery returns the expected source files, and the
     generated settings point to the correct query and output locations.

3. **Give Curator access to Azure.** Curator processes the source and query
   videos. Edit the
   [credential helper](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/callables/msc_credentials.py).

   - Confirm the Azure credential-file format supported by the installed
     Curator version. Add a helper command that writes that file from the
     configured secrets, with access restricted to the task user.
   - Document the exact file contents with secret values replaced by
     placeholders, its location, and the command that creates it. Handle
     different credentials for input, query, and output when needed.
   - Update the helper's configuration downloads and timing uploads to use the
     Azure file-access functions. Keep secret values out of run settings and logs.
   - **Check:** From the Curator container, create the credential file, read a
     source video and query video, and write a small file to the output location.
     This check must pass inside the processing container, not just in Airflow.

4. **Read processing results and check videos.** Edit
   [search-data loading](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/callables/cds_ingest.py)
   and [video checks](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/callables/media_probe.py).

   - Use the Azure functions to read Curator results and save the files needed
     for search. Preserve directory structure and keep downloads inside the
     intended local directory.
   - Download Azure videos before running the existing decoding checks, then
     save the check results to Azure. Treat unsupported remote paths as errors
     rather than trying to open them as local files.
   - **Check:** Process one source video and query, load their search data, and
     confirm that a downloaded video passes the decoding checks.

5. **Save generated videos and final results.** Start with
   [augmentation](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/callables/augmentation.py)
   and [result collection](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/callables/collect_results.py).

   - Follow the file paths passed to the shared Cosmos generation tasks and
     evaluator. Update each place that reads or writes files to use Azure or
     prepared local storage.
   - Save generated videos, evaluation results, summaries, and the final file
     list under `output_directory`. If a service does not support Azure paths,
     add the required file transfer or service support before continuing.
   - **Check:** Generate one video, open it, and confirm the final file list
     points to the saved video and evaluation results in Azure.

6. **Deploy and check the changes.** The workflow already copies its helper
   scripts into task containers when they start. Editing those scripts does
   not automatically require rebuilding every processing image.

   - Update the helper scripts and their startup commands in the
     [Kubernetes task configuration](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/configs/autonomous_vehicle_dataset_generation_k8s_manifest.yaml).
     Make sure the credential file is created before processing starts. If the
     helpers import a new shared module, include that module in the files sent
     to the task or install it in the task image.
   - Check whether each affected task already has the Azure library. In the
     Python environment used by that task, run
     `python -c "import azure.storage.blob"`. Curator uses a Pixi environment,
     so run this check through the same `pixi run` command used for processing.
   - If a required library is missing, add it to that task's image, build the
     image, publish it to the deployment's container registry, and update its
     `container_image` setting. Rebuild only images that need changes.
   - Run `make install` from the repository root for the local deployment.
     This builds and deploys the local platform images; processing images use
     the versions selected in the task configuration.
   - Reapply Azure storage settings if installation replaces them. Restart
     Airflow components that read those settings from their environment.
   - **Check:** Start a new test run. Confirm each task can import its code,
     read its credentials, and access Azure. A library or secret available only
     on the host machine is not enough.

## Test the Complete Workflow

Prepare Kubernetes, Airflow, FFmpeg, and model files using
[Prerequisites](prerequisites.md) and [Getting Started](getting-started.md).
Then:

1. Place a small dataset and a separate query video in Azure. For the example
   paths above, use this layout inside the `av-data` container:

   ```text
   videos/
     <scene-id>/
       camera_front_wide_120fov.mp4
   query/
     example.mp4
   ```

   Each source scene needs its own directory directly under `videos/`, with the
   exact filename shown. Set `input_video_path` to `az://av-data/videos` and
   `query_video` to `az://av-data/query/example.mp4`. Keep generated outputs
   outside both input directories, for example `az://av-data/results/run-001`.
   Check file sizes and checksums after copying.
2. Test Azure file access with these cases. Here, a container refer to an Azure
   Blob Storage container:

   - Dataset, query, and outputs use separate directories in the same container.
   - Dataset, query, and outputs each use a different container.
   - Input credentials allow reading, and output credentials allow writing.
     Check that each path uses the correct credentials.
   - An MSC profile name differs from the actual container name, and files are
     still found in the correct container.
   - Missing files and invalid paths produce clear errors.

3. **Run a search test without generation.** After implementing the Azure
   changes, open `autonomous_vehicle_dataset_generation_dag_k8s` in Airflow and
   trigger it using the procedure in [Getting Started](getting-started.md#run-the-workflow).
   Set the run's `payload` to:

   ```json
   {
     "input_video_path": "az://av-data/videos",
     "query_video": "az://av-data/query/example.mp4",
     "output_directory": "az://av-data/results/search-test-01",
     "collection_name": "azure_search_test_01",
     "search_mode": "embedding",
     "limit": 1,
     "top_k": 1,
     "collect_result_clips": true,
     "cosmos": {"enabled": false}
   }
   ```

   Use a query video distinct from the source video. Give every repeat a new
   collection name and output directory. One example workflow run is: find one
   source video, process it and use it to query for similar videos, and search for one matching
   clip. On Airflow check these steps pass:

   | Task | What to check |
   | --- | --- |
   | `input_preparation.prepare_input` | Finds one source video with the required scene layout. |
   | `generate_configs` and `build_curator_args` | Use Azure paths for source, query, configuration files, and outputs. |
   | `run_curator` | Processes both the query and source; saves clips and search data under `query_split/` and `split/`. |
   | `probe_curator_outputs` and `reconcile_curator_outputs` | Video decoding checks pass and the source summary is updated. |
   | `ingest_cds` | Loads the search data and saves `cds_ingest.parquet` and `cds_search_response.json`. |
   | `collect_results` and `validate_retrieval` | Save and validate `search_result.json` and copied clips under `results/`. |

   Files are saved under
   `az://av-data/results/search-test-01/<sanitized-run-id>/`. Open `search_result.json`,
   confirm `hits` contains a source clip rather than the query itself, and
   open a copied video from `results/`. Verify the complete DAG succeeds and
   service shutdown finishes. Generation tasks are expected to be skipped in this run.

4. **Run a separate generation test.** Continue only after the search test
   passes from step **3**. Start from the RGB generation example in
   [Getting Started](getting-started.md#run-the-workflow), use the same Azure
   input and query paths, and choose a new collection name and output directory.
   Set `cosmos.enabled` to `true` and provide the required generation prompt.
   Verify at least one accepted generated video, evaluation results, and the
   final file list in Azure. Open the video to check it works.

5. Confirm services shut down after both successful and failed runs. Repeat
   setup on a fresh machine using only the documented instructions.

Full Azure support is verified when the complete workflow succeeds, every
expected file is present and usable, and all tasks use Azure or prepared local
storage. Record the code version, container image versions, run settings without
secrets, and output locations.

## Finish the Setup Instructions

Once the changes work, document the exact commands for installing packages,
creating Azure secrets, applying storage settings, deploying task images, and
submitting a complete example run. Include expected results for each command.

Put installation requirements in [Prerequisites](prerequisites.md), the run
procedure in [Getting Started](getting-started.md), Azure path examples in the
[Payload Guide](payload-guide.md), and common errors in
[Troubleshooting](troubleshooting.md). Link to this guide from the
[main README](../../README.md).
