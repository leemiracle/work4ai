# Getting Started Guide

This guide walks through how to deploy the Cosmos Data Factory Orchestration onto a Kubernetes cluster and run your first workflow.

## Prerequisites

To use CDF Orchestration, install the CLI tools, configure a Kubernetes cluster with GPUs, set up a bucket, and provide secrets for NVIDIA NGC and Hugging Face APIs.

The following sections describe how to set these up.

For a fresh Linux host, use the [Linux bootstrap guide](../skills/cdf-orchestration-preflight/references/bootstrap.md)
to prepare missing tools, Kubernetes, GPU support and shared storage.

### Tools

Verify the installation of the following CLI tools before proceeding. These tools are used to build the Airflow image, deploy the Helm chart, and upload workflow input data to your cloud storage.

| Tool | Version | Installation Instructions | Verification |
|------|---------|---------------------------| ------------ |
| **kubectl** | **1.26+** | https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/ | Verify installation by running `kubectl version` |
| **helm** | **3.x** | https://helm.sh/docs/intro/install/ | Verify installation by running `helm version` |
| **docker** | **29.6.0+** | https://docs.docker.com/engine/install/ubuntu/ | Verify installation by running `docker --version` |
| **aws** | **2.x** | https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html | Verify installation by running `aws --version` |
| **CUDA** | **13.x.x** | https://docs.nvidia.com/cuda/cuda-installation-guide-linux/ | Run `nvidia-smi` on each GPU worker node in the target Kubernetes cluster and confirm the driver supports CUDA 13.x. The displayed `CUDA Version` indicates driver compatibility, not the installed CUDA Toolkit version. |
| **python3** | **3.11.x** | https://www.python.org/downloads/ | Verify installation by running `python3 --version`. The setup scripts and the preflight audit require 3.11 for the supported configuration. Preflight warns about other Python versions rather than rejecting them. |
| **uv** | **0.9+** (local development only) | https://docs.astral.sh/uv/getting-started/installation/ | Verify installation by running `uv --version`. Needed only to run DAG code or tests locally with `uv sync --frozen --all-packages`; deployment does not use it. |

### Kubernetes Cluster

CDF Orchestration is a Helm chart that is deployed on a Kubernetes cluster. Workflows run **in-cluster** with the KubernetesExecutor (task pods use the cluster Airflow is installed on). Before installing the chart, ensure that your Kubernetes cluster is configured correctly by following these steps:

1. **Cluster Configuration**: Set the `KUBECONFIG` environment variable to the Kubernetes config file for the cluster where you want to deploy CDF Orchestration. `make setup` embeds this kubeconfig in the deployment so Airflow can access the cluster. The API server address in the kubeconfig must therefore be reachable from the Airflow pods; loopback addresses such as `127.0.0.1` and `localhost` will not work. **K3s is not supported.** Refer to Kubernetes [configuration documentation](https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/) for details on the configuration.

2. **Storage**: Default Helm values expect a **`nfs`** StorageClass for PostgreSQL and the NGC model-cache PVC. DAGs and plugins are **not** stored on a DAG PVC; they are baked into the Airflow image. If your cluster does not already provide NFS, run `make install nfs` first. If you use a different `ReadWriteMany` StorageClass, set `storageClassName` in `deploy/values.yaml`. Refer to [Configure NFS storage](advanced-usage.md#configure-nfs-storage) for more details.

   > **Warning:** `make install nfs` modifies the selected node's operating system and restarts its NFS services. Run it only during initial cluster preparation, before installing CDF Orchestration or mounting PVCs from that server. Do not rerun it while NFS-backed workloads are active, especially when the NFS server and Kubernetes workloads share the same node; interrupted NFS I/O can make the host unresponsive. Before running the installer, verify that the host permits privileged pods, host filesystem access, package installation, system service management, and NFS mounts.

   **Shared FFmpeg installation (Autonomous Vehicle Dataset Generation only):** Curator and the workflow's video-validation pods decode H.264 with an FFmpeg build that the user must install. Mount it read-only at `/opt/ffmpeg`. Create and fill the claim as described in [Shared FFmpeg Installation](autonomous-vehicle-dataset-generation/prerequisites.md#shared-ffmpeg-installation).

3. **GPUs**: GPU requirements depend on the workflow and whether you deploy internal services. Install the [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/overview.html) (or equivalent) whenever the selected workflow requests `nvidia.com/gpu`:
   - **Image Attribute Augmentation:** Every batch stage runs on a CPU profile, so external mode needs no GPUs. Internal mode deploys two GPU endpoints: one shared VLM/LLM service and one image-edit service. The managed attribute-verification checker is CPU-only in this workflow, so enabling it adds no GPUs.
   - **Event Video Generation:** Augmentation, detection and tracking, captioning, and visual QA request one GPU per pod in **both** service modes, but they run one stage at a time, so one batch GPU is enough to make progress. Event and person attribute search is CPU-only. The two managed Cosmos Evaluator checkers are enabled by default and deploy in both service modes, adding one GPU each, so external mode needs three GPUs by default. Internal mode adds three more (one shared VLM/LLM service and two for image-to-video, which uses two GPUs in the default profile), for six total. Supplying an existing evaluator URL or disabling the checks removes the two checker GPUs, leaving one (external) or four (internal).
   - **Video Data Augmentation:** Every Kubernetes batch stage requests a GPU. Internal mode adds one GPU for the shared language-model endpoint and two for Cosmos Transfer. Each enabled managed evaluator checker (hallucination, attribute verification, and physical plausibility) requires one GPU. An internal run with all three managed checkers enabled therefore needs seven GPUs to make forward progress and recommends eight GPUs for normal two-branch overlap. Refer to the [VDA capacity table](video-data-augmentation/getting-started.md#choose-an-execution-target).
   - **SMT Defect Image Generation:** Simulation and AnomalyGen GPU tasks use an RTX 6000 compute pool.
   - **Autonomous Vehicle Dataset Generation:** Retrieval-only runs need one GPU. Generation needs four available GPUs: two on the same node for Cosmos3-Nano, one for the generation task and one for required physical-plausibility evaluation. The workflow manages its own services and uses RGB input controls by default; pre-generated World Scenario Model (WSM) controls are optional. See [AV prerequisites](autonomous-vehicle-dataset-generation/prerequisites.md#check-capacity) for tested hardware and shared FFmpeg requirements.

   Eight GPUs are recommended to ensure success for all workflows, but you can decrease that number depending on the target workflow. Check the workflow-specific guides and free-versus-total cluster capacity before starting a run.

### Buckets and Credentials

Cloud storage is used for **workflow input** and **workflow output**. DAG code is not uploaded to storage; it is built into the Airflow image. This guide uses **one bucket and one IAM credential set** for both input and output. Refer to [Configure Cloud Storage](advanced-usage.md#configure-s3-buckets) for layout examples.

Before continuing, ensure that you have an S3 bucket set up and an IAM user with long-lived AWS access keys. The IAM user must have `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject` permissions for the bucket. Visit [Amazon S3](https://aws.amazon.com/s3/) to get started with S3 if this is not already configured. To proceed to the next step, ensure that you know your bucket name, bucket region, access key ID, and secret access key.

> **Important:** CDF Orchestration supports IAM user credentials consisting of an access key ID and secret access key. Temporary AWS STS credentials, including assumed-role credentials, are not supported because the configuration does not accept an AWS session token.

Set these values in `secrets.env`:

```bash
AWS_S3_BUCKET=
AWS_S3_REGION=
AWS_S3_ACCESS_KEY_ID=
AWS_S3_SECRET_ACCESS_KEY=
```

`make setup` writes that single credential set into Helm as `global.secrets.aws`. Airflow receives `AIRFLOW_VAR_AWS_*` and a Multi-Storage Client profile named after `AWS_S3_BUCKET`. These S3 values are required for every deployment. To use other storage clients alongside this S3 profile, refer to [Configure Other Storage Clients](advanced-usage.md#configure-other-storage-clients).

### Secrets

This project requires the following secrets:
- **NGC API Key**: Obtain an [NGC API Key](https://org.ngc.nvidia.com/account/api-key). This is used to pull docker containers from NGC and to populate the `nvcf_default` Airflow connection (API key only; workflows still run on in-cluster Kubernetes, not NVCF). `make build sdg-controller` also uses this key to push the Airflow image, so it must have push access to an NGC org/team registry path (see [Set the Airflow image repository and tag](#start-airflow-and-run-workflows)).
- **Hugging Face Token**: This is used for Hugging Face model downloads for LLM/VLM/image-edit services. To create the token:
   - If you use reference models such as [Cosmos-Guardrail1](https://huggingface.co/nvidia/Cosmos-Guardrail1), [Cosmos-Transfer2.5](https://huggingface.co/nvidia/Cosmos-Transfer2.5-2B), or [Qwen-Image-Edit-2511](https://huggingface.co/Qwen/Qwen-Image-Edit-2511), read and accept their terms.
   - If you use different models, read and accept the terms for the model repositories your deployment uses.
   - Create a new [Hugging Face Token](https://huggingface.co/settings/tokens) with read permissions for those repositories.
   - Refer to [Update Model Selections](advanced-usage.md#update-model-selections) for where models are configured.
- **S3 Credentials**: Refer to the instructions from the [previous step](#buckets-and-credentials) for AWS credential setup.

Optional secrets:
- **OSMO_TOKEN**, **OSMO_URL** and **OSMO_POOL**: Required only if you trigger OSMO DAGs (`*_dag_osmo`). `OSMO_URL` is your OSMO service URL and `OSMO_POOL` is the OSMO compute pool the tasks run on. Optionally set `OSMO_HF_CACHE_SEED_DIR`, a pre-populated Hugging Face cache mounted on your pool that OSMO video augmentation uses instead of downloading models with `HF_TOKEN`.
- **VLM_API_KEY**: Required to generate defects with SMT Defect Image Generation's recommended GPT-6 Astra endpoint. If it is not set, SMT AnomalyGen falls back to the NGC key, which works only with endpoints that accept it.
- **LLM_API_KEY**: Optional model endpoint credential.

After the secrets are ready, set them up in the repo using the following steps:

1. **Clone the Repo**:

   ```bash
   git clone <repo-url> sdg-workflow
   cd sdg-workflow
   ```

2. **Copy secrets template**:

   ```bash
   cp secrets.env.example secrets.env
   ```

3. **Fill `secrets.env`**: Open the file and set `NGC_API_KEY`, `HF_TOKEN`,
   `AWS_S3_BUCKET`, `AWS_S3_REGION`, `AWS_S3_ACCESS_KEY_ID` and
   `AWS_S3_SECRET_ACCESS_KEY`, using the credentials described above. Complete this
   before running preflight or `make setup`.

   Set `OSMO_TOKEN`, `OSMO_URL` and `OSMO_POOL` if you will run OSMO DAGs. Set `VLM_API_KEY` and `LLM_API_KEY`
   when required by your model endpoints, as described under [Secrets](#secrets).
   Leave unused optional values empty.

### Check Prerequisites with Preflight

After filling `secrets.env` and setting `KUBECONFIG`, run the read-only audit from
the repository root:

```bash
python3 skills/cdf-orchestration-preflight/scripts/preflight.py audit \
  --repo-root "$PWD" --kubeconfig "$KUBECONFIG" --format json
```

Follow the [preflight instructions](../skills/cdf-orchestration-preflight/SKILL.md#run-the-audit)
to configure controller image access and add any required image or probe arguments.
Resolve `BLOCKED` or `UNVERIFIED` installation checks and rerun until
`install_readiness` is `READY` before deploying. `run_readiness` can be `BLOCKED`
before Airflow is installed; it describes whether workflows can run, separately
from whether the controller can be installed.

## Start Airflow and Run Workflows

1. **Run setup**:

   `make setup` loads `secrets.env`, prompting for missing values, and generates the files that
   `make install` uses later. It regenerates both files from `secrets.env` rather than merging with
   their existing content:

   - `secrets.env` is rewritten with normalized values for only the variables setup manages. Any
     other variables, such as extra `AWS_S3_*_DAG_*`, `AWS_S3_*_INPUT_*` or `AWS_S3_*_OUTPUT_*`
     credential sets, are removed.
   - `deploy/secret_values_dev.yaml` is written with the secrets for Helm. Its `global.secrets.aws`
     block is reset from `AWS_S3_BUCKET`, `AWS_S3_REGION`, `AWS_S3_ACCESS_KEY_ID` and
     `AWS_S3_SECRET_ACCESS_KEY`, so edits made directly to that block are overwritten.

   If you keep custom values in either file, back it up before running setup and re-apply the
   values afterward. Then run:

   ```bash
   make setup
   ```

   Setup **does not** deploy Airflow or rebuild the image. Its output takes effect when you run
   `make install sdg-controller` in step 4.

2. **Set the Airflow image repository and tag**:

   Edit `AIRFLOW_IMAGE_REPOSITORY` and `AIRFLOW_IMAGE_TAG` in `make/common.mk` so `make build` pushes to a registry path you can write. The repository default is a placeholder, and `make build sdg-controller` stops until you replace it:

   ```makefile
   AIRFLOW_IMAGE_REPOSITORY ?= nvcr.io/<your-org>/<your-team>/sdg-workflow-airflow
   AIRFLOW_IMAGE_TAG ?= latest
   ```

   Replace the repository with your NGC org/team path (the first path segment is the registry host used for `docker login`). Set a tag you control; avoid a shared `latest` if other builds publish to the same path. `NGC_API_KEY` in `secrets.env` must be allowed to push that repository.

   You can still override either variable on the command line without editing the file:

   ```bash
   AIRFLOW_IMAGE_REPOSITORY=nvcr.io/<your-org>/<your-team>/sdg-workflow-airflow AIRFLOW_IMAGE_TAG=<tag> make build sdg-controller
   ```

   **Optional: local registry.** To publish to a registry on the build machine, start one and set `AIRFLOW_IMAGE_REPOSITORY` in `make/common.mk` to that address before `make build sdg-controller`:

   ```bash
   docker run -d -p 5000:5000 --restart=always --name sdg-registry registry:2
   ```

   Use a host and port the cluster nodes can pull from. `localhost` works when the kubelet runs on this machine; otherwise use this machine's reachable address (the same reachability constraint as the API server in [Kubernetes cluster](#kubernetes-cluster)):

   ```makefile
   AIRFLOW_IMAGE_REPOSITORY ?= <host>:5000/sdg-workflow-airflow
   AIRFLOW_IMAGE_TAG ?= dev
   ```

   The build logs in with `NGC_API_KEY` and pushes `$(AIRFLOW_IMAGE_REPOSITORY):$(AIRFLOW_IMAGE_TAG)`. A registry started this way does not require its own credentials, and that login succeeds. It serves HTTP, so each node that pulls the image must allow `<host>:5000` as an insecure registry.

3. **Publish the Airflow image**:

   DAGs and plugins are **baked into the Airflow image** (`docker/Dockerfile.airflow` copies `airflow/dags` and `airflow/plugins`). Publish that image before the first Helm install, and again after you edit files under `airflow/dags` or `airflow/plugins`, or change runtime dependencies in `airflow/pyproject.toml`:

   ```bash
   make build sdg-controller
   ```

   This rebuilds the Airflow image, pushes `$(AIRFLOW_IMAGE_REPOSITORY):$(AIRFLOW_IMAGE_TAG)`, and writes that repository and tag into `deploy/values.yaml`.

4. **Install the Airflow Helm Chart**:

   > **Warning:** `make install sdg-controller` runs `make uninstall` first, deleting
   > all Jobs, Deployments, StatefulSets, Services and Pods in the target namespace
   > (`sdg-workflow` by default), including other users' active runs and GPU services.
   > Pods are force-deleted; PVCs are retained. Run this only during a maintenance
   > window when no workflows or unrelated workloads are active in that namespace.

   ```bash
   make install sdg-controller
   ```

   This will:

   1. Update Helm chart dependencies
   2. Uninstall any existing release and delete workloads and services throughout the namespace
   3. Install/upgrade the `sdg-workflow-controller` release in namespace `sdg-workflow` using the Airflow image already set in `deploy/values.yaml`

   Wait for the success message. Helm uses a **10 minute** timeout; large clusters or slow image pulls may need a retry.

   Helm value or secret changes alone do not need a rebuild: `make install sdg-controller` is enough. After a DAG or plugin rebuild, run install so the dag-processor loads `/opt/airflow/dags` from the new image (refresh interval is 30 seconds).

5. **Forward the Airflow UI port**:

   ```bash
   make port-forward
   ```

   This will:
   - Forward the Airflow API server to `http://localhost:8080` (also bound on `0.0.0.0` so other machines on the network can open the UI).

6. **Open the Airflow UI**:

   Open `http://localhost:8080` (or `http://<your-IP-Address>:8080`) in a browser window.

   Use `admin` / `admin` as the credentials by default

   > Note: Change default credentials before any production use.

7. **Choose a Workflow**

   Select the workflow that matches your data-generation goal, then follow its
   dedicated guide for input preparation, payload authoring, and execution.
   Starter JSON lives under [`payloads/dev/`](../payloads/dev/).

   | Workflow | Airflow DAG | Purpose | Getting Started |
   | --- | --- | --- | --- |
   | Image Attribute Augmentation | `image_attribute_augmentation_dag_k8s` | Generate clothing-attribute variations for person images. | [Open guide](image-attribute-augmentation/getting-started.md) |
   | Event Video Generation | `event_video_generation_dag_k8s` | Generate and auto-label anomaly videos from source images. | [Open guide](event-video-generation/getting-started.md) |
   | Video Data Augmentation | `video_data_augmentation_dag_k8s` | Create Cosmos Transfer variants and auto-label source and accepted generated videos into separate training exports. | [Open guide](video-data-augmentation/getting-started.md) |
   | SMT Defect Image Generation | `defect_image_generation_smt_dag_k8s` | Simulate SMT component images, augment, and generate defects. | [Open guide](defect-image-generation/getting-started.md) |
   | Autonomous Vehicle Dataset Generation | `autonomous_vehicle_dataset_generation_dag_k8s` | Retrieve driving clips or generate Cosmos3-Nano video variants with default RGB or optional WSM controls and physical-plausibility evaluation. | [Open guide](autonomous-vehicle-dataset-generation/getting-started.md) |

   Event Video Generation and Video Data Augmentation also register
   `event_video_generation_dag_osmo` and `video_data_augmentation_dag_osmo`.
   **OSMO supports external endpoints only. Never trigger either OSMO DAG with
   `external_services: false`.** Their manifests cannot deploy inference or
   Cosmos Evaluator services. Provide an external evaluator URL when checks are
   enabled, and follow the OSMO section in the corresponding payload guide.
   NVCF platform DAGs are not included in this deployment.

## Stop a Running Workflow and Clean Up Kubernetes Resources

Do **not** delete the DAG or the DAG run from the UI. That skips shutdown tasks
and leaves GPU Deployments, Services, and pods in `sdg-workflow`.

1. **Copy the run id** of the workflow you are stopping (Grid view → the
   active run). This is the Airflow **run id**, not the DAG id. Example:
   `manual__2026-09-21T17:00:00+00:00`.

2. **Mark the run failed.** Open the running task (or the DAG run) and choose
   **Mark Failed**. Prefer marking the **running task** failed so the DAG can
   still execute `fail_pipeline` and service shutdown. Marking only the DAG
   run failed can skip those tasks.

3. **Sweep leftover cluster objects** with `k8s_resource_cleanup_dag`. Open
   that DAG → **Trigger**. Set **`target_run_id`** to the run id from step 1
   (JSON config `{"target_run_id": "<run_id>"}` also works). Trigger it.

   Cleanup deletes Deployments, Services, and Pods labeled
   `created-by=k8s-plugin` and `airflow-run-id` matching that source run. It
   does **not** match on DAG id. Successful and failed workflow runs already
   enqueue this DAG with the same conf; trigger it yourself when you marked a
   run failed and services are still up.

   Leave `target_run_id` empty only if you intend to delete **every**
   k8s-plugin resource in the namespace, including other people's runs.

To do the same without the UI, see
[Stop a Run](airflow-rest-api.md#stop-a-run) in the REST API guide.

## Uninstall the Helm Chart

To uninstall the CDF Orchestration helm chart, run:

```bash
make uninstall
```

> Note: On uninstall, **PVCs are preserved**.
>
> To delete all persistent data:
> ```bash
> kubectl delete pvc --all -n sdg-workflow
> ```
> This deletes the history of DAG runs, model caches, and other data, including the
> `shared-ffmpeg` storage claim; reinstall FFmpeg as described in
> [Shared FFmpeg Installation](autonomous-vehicle-dataset-generation/prerequisites.md#shared-ffmpeg-installation)
> before the next AV run.


## Next Steps

Author a runtime payload for your chosen workflow:

- [Image Attribute Augmentation payload guide](image-attribute-augmentation/payload-guide.md)
- [Event Video Generation payload guide](event-video-generation/payload-guide.md)
- [Video Data Augmentation payload guide](video-data-augmentation/payload-guide.md)
- [SMT Defect Image Generation payload guide](defect-image-generation/payload-guide.md)
- [Autonomous Vehicle Dataset Generation payload guide](autonomous-vehicle-dataset-generation/payload-guide.md)
- Example payloads: [`payloads/dev/`](../payloads/dev/)

Refer to [Advanced Usage](advanced-usage.md) for deployment customization.

## Appendix

### Developer Commands

Run `make help` for the full list of available developer commands.

| Command | Description |
|---------|-------------|
| `make setup` | Validate secrets; generate Helm secret values |
| `make install nfs` | Install NFS StorageClass (one-time cluster prep) |
| `make build sdg-controller` | Build and push the Airflow image; update the image repository and tag in `deploy/values.yaml` |
| `make install sdg-controller` | Deploy/upgrade the controller using the Airflow image in `deploy/values.yaml` |
| `make port-forward` | Forward Airflow UI to `localhost:8080` |
| `make uninstall` | Uninstall the Helm release (keeps PVCs) |
| `make help` | Show available targets |
