# S3 Compatibility Demo — HF Storage Buckets

Hugging Face Storage Buckets speak the S3 API. This demo points stock AWS CLI
and `boto3` at the gateway, unchanged, and shows the gateway honoring modern
**S3 conditional writes** (`If-None-Match` / `If-Match`) for safe concurrent
updates.

> **The pitch:** Your existing S3 tools and code work against HF Storage Buckets
> unchanged — point them at the gateway, and you get conditional writes for safe
> concurrent updates.

Reference: <https://huggingface.co/docs/hub/storage-buckets-s3>

See `TALK_TRACK.md` for the narrated ~15–20 min walkthrough.

## Prerequisites

- **AWS CLI ≥ 2.23** — conditional-write flags landed in 2.23.
- **`uv`** — runs the boto3 script (`conditional_writes.py`).
- An **HF account with a Write token** — conditional writes require Write.

## Setup

1. **Generate S3 credentials.** Settings → Access Tokens
   (<https://huggingface.co/settings/tokens>). Create or pick a token — its
   permission (**Read** / **Write**) becomes the S3 credential's permission, so
   use **Write**. Open the token's dropdown → **Generate S3 credentials**. Copy
   the **access key ID** (`HFAK…`) and the **secret access key** (shown once).

2. **Write the AWS profile.** Substitutes your namespace (HF username or org)
   into the gateway endpoint and writes the `[profile hf]` block to
   `~/.aws/config`:

   ```bash
   ./setup_profile.sh --namespace your-username   # or: HF_NAMESPACE=your-username ./setup_profile.sh
   ```

   The profile it writes:

   ```ini
   [profile hf]
   region = us-east-1                              # required; gateway is single-region
   endpoint_url = https://s3.hf.co/your-username   # the gateway, scoped to your namespace
   s3 =
       addressing_style = path                     # buckets are path segments, not subdomains
       multipart_threshold = 256MB                 # note: fewer parts on large uploads
       multipart_chunksize = 256MB
   request_checksum_calculation = when_required    # recent CLI/boto3 send trailing CRC32
   response_checksum_validation = when_required    # checksums the gateway can't parse
   ```

3. **Paste your credentials** into `~/.aws/credentials` (never committed):

   ```ini
   [hf]
   aws_access_key_id = HFAK...
   aws_secret_access_key = ...
   ```

4. **Verify** the profile, credentials, and connectivity (maps common errors to
   fixes):

   ```bash
   ./check.sh
   ```

## Run order

```bash
./demo_01_s3_basics.sh                            # mb / cp / ls / rm through the AWS profile
./demo_02_conditional_ops.sh                      # conditional writes via aws s3api (shows a 412)
uv run conditional_writes.py --namespace your-username  # optional: the same story in boto3
./cleanup.sh                                      # remove demo objects/bucket + local temp
```

The three demo scripts pause for **Enter** between steps so you can talk through
each one as you present; pass `--no-pause` (or set `NO_PAUSE=1`) to run straight
through. `check.sh`, `setup_profile.sh`, and `cleanup.sh` don't pause.

The placeholder throughout is `your-username`; override it with `--namespace` or
`HF_NAMESPACE`. Note the difference: the **shell** scripts read the endpoint from
`[profile hf]` (their `--namespace` is informational), while
**`conditional_writes.py`** builds its own endpoint from the namespace — mirroring
the boto3 example in the HF docs — so pass it `--namespace`/`HF_NAMESPACE`.
`demo_02` and `conditional_writes.py` share `sample_data/manifest.json` as the
object under contention.

## What's supported vs not

- **Supported:** single-region S3 (GetObject is proxied through the gateway for
  the AWS CLI / boto3; other clients get a 302 to the nearest CDN edge);
  conditional writes on **PutObject** and on the **CopyObject** copy-source.
- **Not conditional on GetObject** — `If-Match` / `If-None-Match` apply to writes
  only.
- **Not supported:** ACLs, bucket policies, tagging, versioning, lifecycle, SSE,
  notifications. `CopyObject` is same-namespace only. `ListObjectsV2` only.
- **Key rules:** no leading/trailing `/`, no `//`, no `../`, no leading `./`, no
  trailing `..`, no `\` or null bytes.
