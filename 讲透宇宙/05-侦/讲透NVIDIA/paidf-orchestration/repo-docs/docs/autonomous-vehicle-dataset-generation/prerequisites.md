# Autonomous Vehicle Dataset Generation Prerequisites

Prepare your cluster once before running Autonomous Vehicle Dataset Generation.
These steps are for the cluster administrator. Complete the shared
[setup guide](../getting-started.md) first.

For Azure, implement the storage, dependency, credential helper, and checker
image-selection changes in the [Azure implementation plan](azure-support.md)
before running the workflow.

For embedding search, provide an accessible query video distinct from the source.
Azure queries require the changes in the implementation plan above.

## Check Capacity

Retrieval-only runs need one GPU for Curator. Generation needs four available
GPUs: two on the same node for Cosmos3-Nano, one for the generation task and one
for the required physical-plausibility checker. Curator uses one GPU earlier in
the run, which can be reused during generation. CDS and Milvus use CPU services.
The workflow manages these services; external-service mode is not a payload option.
Use the tested GPU configurations below when planning capacity.

Generation defaults to RGB input controls and does not require WSM manifests.
For `cosmos.control_mode: "wsm"`, prepare matching
[WSM controls](payload-guide.md#wsm-controls) before submission. Both modes
require physical-plausibility evaluation and the same GPU capacity.

### CPU and Memory

The [AV manifest](../../airflow/dags/workflows/autonomous_vehicle_dataset_generation_dag/configs/autonomous_vehicle_dataset_generation_k8s_manifest.yaml)
configures the Curator pod with these resources for both retrieval and generation runs:

| Resource | Request | Limit |
| --- | --- | --- |
| CPU | 16 CPUs | 32 CPUs |
| Memory | 128 GiB | 192 GiB |

The GPU node hosting Curator must have capacity for these requests alongside existing
workloads. These are configured scheduling requirements, not measured minimum hardware
or expected consumption. Leave capacity for the controller, CDS, Milvus and other workflow
pods, and provide the shared model cache and FFmpeg storage described in the setup guides.

### Hardware Used in Previous Runs

Successful development runs used these cluster configurations:

- **4 NVIDIA RTX PRO 6000 Blackwell GPUs:** retrieval and
  one-clip generation completed successfully.
- **8 NVIDIA H100 80 GB GPUs:** one-clip and three-clip generation completed
  successfully. H100 setup records include approximately 1 TiB of local disk
  and a 250 GiB shared model-cache allocation.

See [recorded run times](getting-started.md#how-long-does-a-run-take) when planning
a first run. Initial image and model downloads can add time.

<a id="ffmpeg-sidecar"></a>

## Shared FFmpeg Installation

Every run uses FFmpeg video tools at `/opt/ffmpeg`. Install them on shared
storage named `shared-ffmpeg`, which Kubernetes calls a *storage claim*.
Workflow containers mount this storage read-only, they do not install FFmpeg.

Have the cluster administrator create and fill this claim before the first run,
including retrieval-only runs. The controller Helm chart does not create it.
Choose an FFmpeg build that meets your licensing requirements and the requirements
below, and verify the claim is `Bound` with `kubectl get pvc shared-ffmpeg -n sdg-workflow`.

### Requirements

| Requirement | Value |
|-------------|-------|
| Storage | `shared-ffmpeg` in namespace `sdg-workflow`; `ReadWriteMany` allows access from multiple nodes. |
| Files | `bin/ffmpeg`, `bin/ffprobe` and shared libraries under `lib/` at the storage root. |
| Decoder | `h264` |
| Encoder | `libopenh264` for resampling RGB clips and extracting WSM control windows. |
| Version | FFmpeg 8.1.x with `libavcodec` 62, matching Curator 2.3.0's Python video reader. |
