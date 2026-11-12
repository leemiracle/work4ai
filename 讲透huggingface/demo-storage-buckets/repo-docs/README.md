# demo-storage-buckets

Runnable demos for **Hugging Face Storage Buckets** — Xet-backed cloud object
storage on the Hugging Face Hub. Each subdirectory is a self-contained demo with
its own README and a presenter talk track.

New to Storage Buckets? Start with the docs:
<https://huggingface.co/docs/hub/storage-buckets>

## [`basic_demo/`](./basic_demo/)

The essentials: checkpoint dedupe with Xet, bucket basics + CDN pre-warming,
filesystem access via `hf-mount`, and incremental dataset sync.
See [`basic_demo/TALK_TRACK.md`](./basic_demo/TALK_TRACK.md).

## [`s3_compat_demo/`](./s3_compat_demo/)

The S3-compatible API: point stock AWS CLI and `boto3` at the gateway unchanged,
and use S3 conditional writes (`If-None-Match` / `If-Match`) for safe concurrent
updates. See [`s3_compat_demo/TALK_TRACK.md`](./s3_compat_demo/TALK_TRACK.md).
