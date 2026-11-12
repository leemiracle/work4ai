<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Samples and Cookbooks

1. [About Curation and Retrieval](README.md)
2. [Installation](installation.md)
3. [Samples and Cookbooks](samples-and-cookbooks.md)
4. [Get Started](getting-started.md)
5. [Cosmos Curator](operations-curator.md)
6. [Data Mining](operations-tao-mining.md)
7. [Cosmos Dataset Search](operations-cds.md)
8. [VLM and LLM Endpoints](vlm-llm-endpoints.md)
9. [Troubleshooting](troubleshooting.md)

Cookbooks ship engine-native configs. Traffic and warehouse sample MP4s come
from NGC, not from this repository. Stage them into each cookbook `videos/`
folder before Path A. Do not commit secrets into cookbook files.

Index: [`../../cookbook/README.md`](../../cookbook/README.md).

## Download VSS Sample Clips

The clips are the NGC resource
`nvidia/vss-developer/dev-profile-sample-data:3.2.0`. That archive mixes
traffic, warehouse, and unused videos in one folder. Curator treats **every**
file under `videos/` as input, so do not point `DATA_DIR` at the mixed extract.
Copy the mapped files into each cookbook instead.

### Install NGC CLI

NGC CLI version 4.10.0 or later is required to download this resource.
Authenticate with an NGC API key. External customers typically have no NGC
org or team; if the CLI prompts for those fields, leave them empty.

Download NGC CLI. ARM64 Linux:

```bash
curl -sLo "/tmp/ngccli.zip" \
  https://api.ngc.nvidia.com/v2/resources/nvidia/ngc-apps/ngc_cli/versions/4.10.0/files/ngccli_arm64.zip
```

AMD64 Linux:

```bash
curl -sLo "/tmp/ngccli.zip" \
  https://api.ngc.nvidia.com/v2/resources/nvidia/ngc-apps/ngc_cli/versions/4.10.0/files/ngccli_linux.zip
```

Install:

```bash
sudo mkdir -p /usr/local/bin
sudo unzip -qo /tmp/ngccli.zip -d /usr/local/lib
sudo chmod +x /usr/local/lib/ngc-cli/ngc
sudo ln -sfn /usr/local/lib/ngc-cli/ngc /usr/local/bin/ngc
ngc --version
```

Configure the CLI with your API key. Do not put the key on the command line.
For how to create a key, refer to NGC API keys in the NGC documentation.

```bash
ngc config set
```

NGC CLI downloads: https://ngc.nvidia.com/setup/installers/cli

NGC CLI documentation: https://docs.ngc.nvidia.com/cli/index.html

You can use NGC CLI as below, or download the same resource from the NGC UI.

```bash
# Download sample data
ngc registry resource download-version \
  nvidia/vss-developer/dev-profile-sample-data:3.2.0

EXTRACT_DIR=./sample-data
mkdir -p "${EXTRACT_DIR}"
tar -xf dev-profile-sample-data_v3.2.0/dev-profile-sample-data.tar.gz \
  -C "${EXTRACT_DIR}"

rm -rf dev-profile-sample-data_v3.2.0
```

The extract layout is `sample-data/dev-profile-sample-data/*.mp4`.

### Copy Clips into the Cookbooks

Use copies, not symlinks. Make bind-mounts the cookbook directory into the
Curator container; a host symlink that points outside that mount is not
visible inside the container. Keep the NGC filenames; recipes read every MP4
under `videos/`.

```bash
SRC=./sample-data/dev-profile-sample-data

mkdir -p cookbook/traffic-video-analytics/videos
cp "${SRC}/sample-sim-jaywalking.mp4" \
  "${SRC}/sample-sim-traffic.mp4" \
  cookbook/traffic-video-analytics/videos/

mkdir -p cookbook/warehouse-safety/videos
cp "${SRC}/warehouse_safety_0001.mp4" \
  "${SRC}/warehouse_safety_0002.mp4" \
  "${SRC}/sample-warehouse-ladder.mp4" \
  "${SRC}/warehouse_sample.mp4" \
  cookbook/warehouse-safety/videos/
```

| Cookbook | Files to copy into `videos/` |
|----------|------------------------------|
| `traffic-video-analytics` | `sample-sim-jaywalking.mp4`, `sample-sim-traffic.mp4` |
| `warehouse-safety` | `warehouse_safety_0001.mp4`, `warehouse_safety_0002.mp4`, `sample-warehouse-ladder.mp4`, `warehouse_sample.mp4` |

Leave these extract files unused (they do not belong to either cookbook):
`sample-sim-box-conveyor.mp4`, `sample-drone-bridge.mp4`.

Keep docs and other non-media files **outside** `videos/`.

## Which Sample to Use

| Goal | Cookbook / sample | What you must change |
|------|-------------------|----------------------|
| Curator traffic first-run | `cookbook/traffic-video-analytics/split-minimal.yaml` | Stage NGC clips into `videos/` (above); `DATA_DIR` is the cookbook dir (both clips, CE1 + captions) |
| Path D CDS ingest of that CE1 output | [Cosmos Dataset Search](operations-cds.md) | Collection **id**; `CURATOR_DIR` = `output/split-minimal`; public GA |
| Curator traffic video | `cookbook/traffic-video-analytics/` | Optional: point `DATA_DIR` at a work dir with your MP4s; VLM endpoints for full `split.yaml` |
| Curator warehouse first-run | `cookbook/warehouse-safety/split-minimal.yaml` | Stage NGC clips into `videos/` (above); `DATA_DIR` is the cookbook dir (`limit: 1`) |
| Curator PhysicalAI-AV multi-cam first-run | `cookbook/physical-ai-av/caption-multicam.yaml` | HF login + `python -m adapters.physical_ai_av.prepare_sessions --output-dir $DATA`; uses `videos/<uuid>/` session folders; VLM/LLM endpoints |
| Curator PhysicalAI-AV SAM3 events | `cookbook/physical-ai-av/split-singlecam.yaml` or `split-multicam.yaml` | Same prepare step; `PIXI_ENV=sam3`; VLM/LLM endpoints |
| Curator warehouse video | `cookbook/warehouse-safety/` | Optional: point `DATA_DIR` at a work dir with your MP4s; VLM endpoints for full `split.yaml` |
| Nearest neighbors | `cookbook/nearest-neighbor-mining/` | Ensure `DATA_DIR` has `S.parquet` / `B.parquet`; adjust YAML paths if needed |
| Unique neighbor matching | `cookbook/unique-neighbor-matching/` | Same S/B layout; add detections for `class_stratified` |
| Image embeddings | Make recipe in [Data Mining](operations-tao-mining.md) | `rows.json` filepaths under `DATA_DIR` |
| Text embeddings | Make recipe in [Data Mining](operations-tao-mining.md) | parquet with `text` column |

Mining cookbooks need **no API keys** beyond registry login to pull the image.
Curator caption stages might need Hugging Face tokens and, for endpoint-backed cookbooks,
live vision-language model (VLM) and large language model (LLM) services.
Refer to [VLM and LLM Endpoints](vlm-llm-endpoints.md).

## Nearest Neighbor Mining

```text
data/nearest-neighbor-mining/
  S.parquet    # targets (query set)
  B.parquet    # candidates (source pool)
```

```bash
make run-data-mining-select \
  DATA_DIR=$PWD/data/nearest-neighbor-mining \
  TMM_CONFIG_FILE=cookbook/nearest-neighbor-mining/tmm.yaml \
  TDM_EMBEDDING_BACKEND=ce1
```

Minimal parquet schema: identity column + embedding vectors. See
[Get Started](getting-started.md) Path B for the three-image CLIP
staging commands.

## Unique Neighbor Matching

```text
data/unique-neighbor-matching/
  S.parquet
  B.parquet
```

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  TMM_UNM_CONFIG_FILE=cookbook/unique-neighbor-matching/unm.yaml
```

For stratified runs, add COCO JSON files or KITTI label directories as described
in [Data Mining](operations-tao-mining.md).

## Curator Cookbooks

Traffic and warehouse are experiment kits. After you copy the NGC clips above:

- `cookbook/traffic-video-analytics/videos/`
- `cookbook/warehouse-safety/videos/`

PhysicalAI-AV does not ship MP4s. Download and extract sessions first:
[`../../cookbook/physical-ai-av/README.md`](../../cookbook/physical-ai-av/README.md).

Run Path A without editing YAML I/O:

```bash
make run-pipeline \
  CONFIG_FILE=cookbook/traffic-video-analytics/split-minimal.yaml \
  DATA_DIR=$PWD/cookbook/traffic-video-analytics \
  MODELS_DIR=/path/to/models

make run-pipeline \
  CONFIG_FILE=cookbook/warehouse-safety/split-minimal.yaml \
  DATA_DIR=$PWD/cookbook/warehouse-safety \
  MODELS_DIR=/path/to/models
```

To try other MP4s, copy them into a work directory with a `videos/` folder
and pass that directory as `DATA_DIR`. Keep `CONFIG_FILE` pointing at the
cookbook YAML.
Details: [`../../cookbook/traffic-video-analytics/README.md`](../../cookbook/traffic-video-analytics/README.md)
and [`../../cookbook/warehouse-safety/README.md`](../../cookbook/warehouse-safety/README.md).
