# Advanced Usage

This section provides instructions for advanced configuration and usage of the project.

## Customization

This guide explains how the project code may be updated to add new DAGs or update the existing DAGs.

To bake DAG or plugin edits into a new Airflow image and roll the Helm release, follow [Publish the Airflow image](getting-started.md#start-airflow-and-run-workflows) in the Getting Started guide (`make build sdg-controller`, then `make install sdg-controller`).

## Update Model Selections

You can update models in two places, depending on whether you want per-run overrides or new defaults:

1. **Per workflow run (payload override):** Set `cosmos.vlm_model`, `cosmos.llm_model`, `cosmos.image_edit_model`, `event_and_person_attribute_search.vlm_model`, and `event_and_person_attribute_search.llm_model` in the trigger payload. Refer to the [Image Attribute Augmentation Payload Guide](image-attribute-augmentation/payload-guide.md#cosmos-fields-augmentation).
2. **Default in-cluster endpoint models:** Edit the workflow k8s manifest under `airflow/dags/workflows/<workflow>/configs/` (for example `image_attribute_augmentation_k8s_manifest.yaml`) under `deployment.components.endpoints.*`. Kubernetes profiles in those manifests use `in_cluster: true`.

When updating default in-cluster endpoint models:

- Update endpoint startup args in `container_args` (for example, `--model` and `--served-model-name`) and adjust the container image if needed.
- Ensure your Hugging Face token has access to the selected model repositories.
- Run `make build sdg-controller` to bake the updated manifests into the image, then `make install sdg-controller` to roll the deployment.

## Scale Internal Model Throughput

When `external_services` is `false`, workflows deploy an in-cluster model
endpoint. Augmentation task overlap inside one DAG run is capped by
`max_concurrency` on the augmentation task in that workflow's deployment
manifest (applied as `max_active_tis_per_dagrun`). Internal augmentation uses
`default_pool`; GPU endpoints and GPU batch tasks share `k8s_rtx6000_1`.

If you intend to run **more than one replica** of a model service, raise
`max_concurrency` on the augmentation task to match the replica count you pass
in the payload, and keep enough free slots in `k8s_rtx6000_1` for those
replicas. For example, with three replicas of the image-edit model service:

**Payload** (`service_lifecycle.image_edit_service.replicas`):

```json
"service_lifecycle": {
  "image_edit_service": {
    "enabled": true,
    "replicas": 3
  }
}
```

**Manifest** (augmentation task):

```yaml
augmentation:
  max_concurrency: 3
```

External augmentation still uses service pools in `deploy/values.yaml`
(`external_image_edit_service_pool`, `external_image2video_service_pool`, and
`cosmos_transfer_3_service_pool`). OSMO DAGs use `osmo_h100_1` or
`osmo_rtx6000_1` plus `OSMO_TOKEN` and `OSMO_URL`, and submit to the OSMO compute pool set
by `OSMO_POOL` (see `secrets.env.example` for the optional `OSMO_HF_CACHE_SEED_DIR`).
After editing `deploy/values.yaml`, run
`make install sdg-controller` so updated pools are created in Airflow. After
editing a baked manifest, rebuild and roll the Airflow image.

> **Warning:** `make install sdg-controller` runs `make uninstall` first, deleting
> all Jobs, Deployments, StatefulSets, Services and Pods in the target namespace
> (`sdg-workflow` by default), including other users' active runs and GPU services.
> Pods are force-deleted; PVCs are retained. Run this only during a maintenance
> window when no workflows or unrelated workloads are active in that namespace.


## Configure NFS Storage

The SDG controller expects a **`ReadWriteMany`** StorageClass named **`nfs`** by default (`deploy/values.yaml`). If your cluster does not already have one, install it with:

> **Warning:** `make install nfs` modifies the selected node's operating system and restarts its NFS services. Run it only during initial cluster preparation, before installing CDF Orchestration or mounting PVCs from that server. Do not rerun it while NFS-backed workloads are active, especially when the NFS server and Kubernetes workloads share the same node; interrupted NFS I/O can make the host unresponsive. Before running the installer, verify that the host permits privileged pods, host filesystem access, package installation, system service management, and NFS mounts.

```bash
make install nfs
```

This runs `scripts/install_nfs.sh`, which:

1. Creates the `nfs-system` namespace
2. Starts an **NFS server on a cluster node host** (using a privileged Job with host mount)
3. Deploys the [nfs-subdir-external-provisioner](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner)
4. Creates a StorageClass named **`nfs`**

### Default Node Selection

If you do not override anything, the script picks the **first node** returned by:

```bash
kubectl get nodes
```

That node’s **`InternalIP`** becomes the NFS server address. You can confirm what will be used:

```bash
kubectl get nodes
# first row under NAME → default NFS host

kubectl get node <that-node-name> -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}{"\n"}'
```

The install prints the resolved node and server IP before applying manifests.

### Override Variables

Pass Make variables or export environment variables before `make install nfs`:

| Variable | Default | Description |
|----------|---------|-------------|
| `NFS_NODE_HOSTNAME` | First node from `kubectl get nodes` | Node where the host NFS export is configured |
| `NFS_SERVER` | `InternalIP` of `NFS_NODE_HOSTNAME` | IP address the provisioner mounts (set explicitly if auto-detection is wrong) |
| `NFS_EXPORT_PATH` | `/srv/nfs/k8s` | Directory on the host exported over NFS |
| `NFS_STORAGE_CLASS` | `nfs` | Name of the StorageClass created |
| `NFS_NAMESPACE` | `nfs-system` | Namespace for the NFS provisioner and setup Job |
| `NFS_PROVISIONER_NAME` | `cluster.local/nfs-subdir-external-provisioner` | Provisioner name registered with Kubernetes |

**Example: use a specific node:**

```bash
make install nfs NFS_NODE_HOSTNAME=4u8g-gen-0375
```

**Example: set the server IP manually** (for example, when the node has multiple addresses or you use a floating IP):

```bash
make install nfs \
  NFS_NODE_HOSTNAME=4u8g-gen-0375 \
  NFS_SERVER=192.168.33.10
```

**Example: custom export path and StorageClass name:**

```bash
make install nfs \
  NFS_EXPORT_PATH=/data/nfs/k8s \
  NFS_STORAGE_CLASS=nfs-rwx
```

If you change `NFS_STORAGE_CLASS`, update matching `storageClassName` / `storageClass` fields in `deploy/values.yaml` before `make install sdg-controller`.

### Where PVC Data Lives on the Host

Each dynamically provisioned volume is a subdirectory under the export path:

```text
${NFS_EXPORT_PATH}/<namespace>-<pvc-name>-<pv-name>/
```

For example, with the default export path:

```text
/srv/nfs/k8s/sdg-workflow-ngc-model-cache-<pv-id>/
```

### Requirements for `make install nfs`

- **`envsubst`** (from the `gettext` package) must be on your PATH
- The target node must allow a **privileged** pod with **host PID/network** and a host filesystem mount (the setup Job installs `nfs-kernel-server` into the node’s root filesystem)
- Pick a node with enough **disk space** for PostgreSQL and the **500Gi** model-cache PVC defined in `deploy/values.yaml` (DAGs are not stored on NFS)

## Configure S3 Buckets

Airflow uses S3 for workflow **input** and **output**. DAG artifacts are **not** stored on S3.

1. **Workflow Input**: Workflows require input data on S3. For example, Image Attribute Augmentation reads person-crop images. Upload datasets with the AWS CLI, then set `input_path` in the payload. Starter payloads live under [`payloads/dev/`](../payloads/dev/).
2. **Workflow Output**: Datasets generated by the pipeline are published to S3 (`output_directory` and related payload fields).

Helm injects one credential set (`AWS_S3_BUCKET`, `AWS_S3_REGION`, `AWS_S3_ACCESS_KEY_ID`, `AWS_S3_SECRET_ACCESS_KEY`) as:

- Airflow variables `aws_access_key_id`, `aws_secret_access_key`, `aws_region`, `aws_bucket`
- A Multi-Storage Client profile for that same bucket

CDF Orchestration supports long-lived IAM user credentials consisting of an access key ID and secret access key. Temporary AWS STS credentials, including assumed-role credentials, are not supported because there is no session-token configuration field.

A typical layout on one bucket:

```
s3://$AWS_S3_BUCKET/input/<workflow>/
s3://$AWS_S3_BUCKET/output/<workflow>/
```

For example, after copying Image Attribute Augmentation images:

```
s3://<bucket-name>/input/image_attribute_augmentation/
s3://<bucket-name>/output/image_attribute_augmentation/
```

Then run `make setup` so Helm secret values match `secrets.env`. Missing required fields are prompted for interactively.

## Configure Other Storage Clients

`make setup` always requires the S3 values above, and the chart generates a
Multi-Storage Client (MSC) configuration containing only that S3 profile. To add
other storage, such as an Azure Blob Storage container or a second bucket, keep
that S3 profile and add the others in a Secret that you manage. DAG tasks read
the MSC configuration from the `multistorageclient_configuration_secret` Airflow
Variable, which `deploy/values.yaml` fills from a Kubernetes Secret.

Storage support varies by workflow. Check the workflow's payload guide before
using a provider other than S3; for example, the
[AV dataset generation payload guide](autonomous-vehicle-dataset-generation/payload-guide.md)
lists the providers its Curator stage supports.

1. **Export the generated configuration** after `make install sdg-controller`
   has created it, and keep the file owner-only because it contains credentials:

   ```bash
   kubectl get secret multistorageclient-configuration-secret -n sdg-workflow \
     -o jsonpath='{.data.multistorageclient_configuration_secret}' | base64 -d > msc-config.json
   chmod 600 msc-config.json
   ```

2. **Add profiles and path mappings** to `msc-config.json`. Keep the existing S3
   profile. Each new profile needs a `storage_provider` and, for cloud storage, a
   `credentials_provider`. Add a `path_mapping` entry for each native prefix that
   payloads or workflow outputs use, so it resolves to the new `msc://` profile.
   For example, an Azure container:

   ```json
   {
     "profiles": {
       "<existing-s3-profile>": { "...": "keep unchanged" },
       "<azure-profile>": {
         "storage_provider": {
           "type": "azure",
           "options": {
             "base_path": "<container>/<prefix>",
             "endpoint_url": "https://<account>.blob.core.windows.net"
           }
         },
         "credentials_provider": {
           "type": "AzureCredentials",
           "options": { "connection": "<azure-connection-string>" }
         }
       }
     },
     "path_mapping": {
       "...": "keep the existing S3 entries",
       "az://<container>/<prefix>/": "msc://<azure-profile>/"
     }
   }
   ```

3. **Create your Secret** in the controller namespace from the file, so the
   credentials do not appear in shell history:

   ```bash
   kubectl create secret generic cdf-storage-config -n sdg-workflow \
     --from-file=multistorageclient_configuration_secret=msc-config.json
   ```

4. **Point Airflow at your Secret.** In `deploy/values.yaml`, set the
   `secretName` of the `AIRFLOW_VAR_MULTISTORAGECLIENT_CONFIGURATION_SECRET`
   entry to `cdf-storage-config`, then run `make install sdg-controller`. Delete
   the local `msc-config.json`, or keep it in protected storage for later edits.

`make uninstall` and `make install sdg-controller` do not delete Secrets that you
create, so this configuration persists across reinstalls. If you change the S3
values in `secrets.env`, update the S3 profile in your Secret as well. When you
run the [storage mapping check](../skills/cdf-orchestration-preflight/scripts/storage_check.py),
pass `--config msc-config.json`, because by default it reads the chart-generated
Secret.
