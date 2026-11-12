> [!WARNING]
> This is an experimental action and may change without deprecation. Use with caution.

# HF Jobs Action

A GitHub Action to run commands on [Hugging Face Jobs](https://huggingface.co/docs/hub/jobs) infrastructure with real-time log streaming.

## Usage

```yaml
- uses: huggingface/hf-jobs-action@main
  with:
    token: ${{ secrets.HF_TOKEN }}
    namespace: your-namespace
    image: ubuntu:22.04
    script: |
      echo "Hello from HF Jobs!"
      uname -a
```

## Inputs

| Name         | Required | Default      | Description                                                    |
| ------------ | -------- | ------------ | -------------------------------------------------------------- |
| `token`      | Yes      | —            | HF API token with `job.write` permission                       |
| `namespace`  | Yes      | —            | HF namespace (username or org)                                 |
| `image`      | Yes      | —            | Docker image to run                                            |
| `script`     | Yes      | —            | Shell script to execute in the container                       |
| `flavor`     | No       | `cpu-basic`  | Hardware flavor (`cpu-basic`, `cpu-upgrade`, `t4-small`, etc.) |
| `timeout`    | No       | `1200`       | Max seconds to wait for completion                             |
| `files`      | No       | —            | Newline-separated list of repo files to make available in job  |
| `files_dest` | No       | `/tmp/files` | Directory inside the container where files are downloaded      |
| `env`        | No       | `{}`         | Environment variables as JSON object                           |

## Outputs

| Name      | Description                    |
| --------- | ------------------------------ |
| `job_id`  | The ID of the created job      |
| `job_url` | URL to the job on Hugging Face |

## Examples

### Run with environment variables

```yaml
- uses: huggingface/hf-jobs-action@main
  with:
    token: ${{ secrets.HF_TOKEN }}
    namespace: my-org
    image: python:3.12-slim
    script: |
      pip install transformers
      python -c "import transformers; print(transformers.__version__)"
    env: '{"HF_TOKEN": "${{ secrets.HF_TOKEN }}"}'
```

### Run with files from your repo

```yaml
- uses: huggingface/hf-jobs-action@main
  with:
    token: ${{ secrets.HF_TOKEN }}
    namespace: my-org
    image: python:3.12-slim
    files: |
      scripts/train.py
      configs/model.yaml
    script: |
      pip install torch pyyaml
      python /tmp/files/train.py --config /tmp/files/model.yaml
```

Files are base64-encoded and embedded directly in the command, then decoded inside the container at `files_dest` (default `/tmp/files`). No external storage or extra dependencies needed.

### GPU job

```yaml
- uses: huggingface/hf-jobs-action@main
  with:
    token: ${{ secrets.HF_TOKEN }}
    namespace: my-org
    image: nvidia/cuda:12.4.0-runtime-ubuntu22.04
    flavor: t4-small
    script: nvidia-smi
```
