# S3 Compatibility Demo — Design & Plan

Demonstrates that **Hugging Face Storage Buckets speak the S3 API**: existing S3
tooling (AWS CLI, `boto3`) works against them unchanged, and the gateway even
honors modern **S3 conditional writes** (`If-None-Match` / `If-Match`) for safe
concurrent updates.

Reference: <https://huggingface.co/docs/hub/storage-buckets-s3>

## Audience & framing

Generic, reusable ~15–20 min talk track. No specific customer, no presenter
name. Anyone should be able to read the scripts and `TALK_TRACK.md` and run the
demo themselves. Keep docs brief and let the code speak.

## The pitch

> Your existing S3 tools and code work against HF Storage Buckets unchanged —
> point them at the gateway, and you get modern S3 conditional writes for safe
> concurrent updates.

## Talk track arc

| Phase | Story | Backed by |
|-------|-------|-----------|
| 0. Credentials & profile (pre-demo setup) | Generate S3 creds from an HF token; wire the AWS profile with the exact fields | `setup_profile.sh`, `check.sh` |
| 1. "Your S3 tools just work" (~5 min) | `mb` / `cp` / `ls` / `rm` through the AWS profile — no code changes | `demo_01_s3_basics.sh` |
| 2. Conditional operations (~8 min, the hero) | No-clobber create + compare-and-swap on a shared manifest; a conflicting writer gets a 412 instead of clobbering | `demo_02_conditional_ops.sh`, `conditional_writes.py` |
| 3. Reality check (~2 min, Q&A) | What's supported vs not | `TALK_TRACK.md` notes |

## Configuration facts (from the HF docs — do not paraphrase loosely)

### Generating S3 credentials (UI, done once before the demo)
1. Settings → Access Tokens (<https://huggingface.co/settings/tokens>). Create a
   token; its permission (**Read** or **Write**) becomes the S3 credential's
   permission. Conditional writes need **Write**.
2. Open the token's dropdown → **Generate S3 credentials**.
3. Copy the **access key ID** (prefixed `HFAK…`) and **secret access key** — the
   secret is shown only once.

### AWS profile — `~/.aws/config`
```ini
[profile hf]
region = us-east-1
endpoint_url = https://s3.hf.co/<namespace>
s3 =
    addressing_style = path
    multipart_threshold = 256MB
    multipart_chunksize = 256MB
request_checksum_calculation = when_required
response_checksum_validation = when_required
```
`<namespace>` = your HF username or org. Field rationale:
- `endpoint_url` — the gateway, scoped to your namespace.
- `region = us-east-1` — required; gateway is single-region.
- `addressing_style = path` — buckets are path segments, not subdomains.
- `request_checksum_calculation` / `response_checksum_validation = when_required`
  — AWS CLI ≥ 2.23 / recent boto3 send trailing CRC32 checksums (`aws-chunked`)
  by default, which the gateway does not parse. `when_required` disables that.
- `multipart_threshold` / `multipart_chunksize = 256MB` — optional; fewer parts
  on large uploads.

### AWS credentials — `~/.aws/credentials`
```ini
[hf]
aws_access_key_id = HFAK...
aws_secret_access_key = ...
```

### Conditional requests (the hero feature)
`If-Match` / `If-None-Match` are honored on **PutObject** and on the copy-source
of **CopyObject** — **not** on GetObject. AWS CLI ≥ 2.23 exposes these as
`aws s3api put-object --if-none-match / --if-match` and
`aws s3api copy-object --copy-source-if-none-match / --copy-source-if-match`.

### Limitations to mention (Phase 3)
Single-region (GetObject usually 302-redirects to CDN; aws-cli/botocore are
proxied). No ACLs, bucket policies, tagging, versioning, lifecycle, SSE,
notifications. `CopyObject` is same-namespace only. `ListObjectsV2` only. Key
rules: no leading/trailing `/`, no `//`, no `../`, no leading `./`, no trailing
`..`, no `\` or null bytes.

## Namespace / secret handling (decided)

- **Namespace** is supplied as a `--namespace` argument or the `HF_NAMESPACE`
  environment variable. Placeholder throughout docs/scripts is `your-username`.
  Nothing is hardcoded to a real user, and there is no presenter name anywhere.
- **Secrets never touch the repo.** `setup_profile.sh` writes only the
  non-secret `[profile hf]` block to `~/.aws/config`; it prints instructions to
  paste the `HFAK…` key/secret into `~/.aws/credentials` (shown once by HF).
- `.gitignore` guards against stray `.env`, `*.pem`, and credential files.

## File layout

```
s3_compat_demo/
  DESIGN.md                   # this file
  README.md                   # concise: prereqs, run order, links to HF docs
  TALK_TRACK.md               # narrated ~15-20 min script, sections + durations
  setup_profile.sh            # write [profile hf] to ~/.aws/config for a namespace (idempotent)
  check.sh                    # doctor: verify profile + connectivity, map errors -> fixes
  demo_01_s3_basics.sh        # mb / cp / ls / rm via the AWS profile
  demo_02_conditional_ops.sh  # If-None-Match:* create + If-Match:<etag> CAS via s3api (shows 412)
  conditional_writes.py       # PEP 723 boto3: two racing writers, no-clobber + CAS-with-retry
  sample_data/manifest.json   # tiny shared object for the CAS story
  cleanup.sh                  # remove demo objects/bucket + local temp
  tests/
    test_conditional_writes.py  # offline unit tests (mocked S3 client)
```

## Component contracts

### Shared conventions (all scripts)
- `set -euo pipefail` in every bash script.
- Namespace resolution helper: use `--namespace X` if given, else `$HF_NAMESPACE`,
  else default `your-username` with a visible warning that it's a placeholder.
- Profile name `hf`, bucket name default `s3-compat-demo` (override with
  `--bucket` / `$DEMO_BUCKET`).
- Echo the exact command before running it (demo readability), then run it.
- Concise top-of-file comment: what it does, usage line, prereqs.

### `setup_profile.sh`
- Usage: `./setup_profile.sh --namespace <ns>` (or `HF_NAMESPACE=...`).
- Idempotently write/replace the `[profile hf]` block in `~/.aws/config` with all
  fields above, substituting the namespace into `endpoint_url`.
- Do NOT write credentials; print the 3-step credential instructions and the
  exact `~/.aws/credentials` block to fill in.
- Back up `~/.aws/config` before editing.

### `check.sh`
- Verify: AWS CLI present and ≥ 2.23; `[profile hf]` exists; creds present;
  `aws --profile hf s3 ls` succeeds.
- Map common failures to fixes (checksum error → `when_required`; hostname
  resolve error → `addressing_style=path`; 403 → token lacks Write).

### `demo_01_s3_basics.sh`
- `mb` the demo bucket, `cp` a local file up, `ls`, `cp` back down, `rm`.
- Narrate that this is stock AWS CLI with only the endpoint/profile changed.

### `demo_02_conditional_ops.sh` (s3api, CLI-driven)
- No-clobber: `put-object --key manifest.json --if-none-match '*'` succeeds;
  a second identical call fails with **412 PreconditionFailed** (caught, printed
  as the expected outcome).
- CAS: `head-object` to read the ETag → modify locally → `put-object --if-match
  <etag>` succeeds; then show a stale-ETag `put-object --if-match <old-etag>`
  failing with 412.

### `conditional_writes.py` (PEP 723, boto3)
- Shebang `#!/usr/bin/env -S uv run --script`; inline deps: `boto3`.
- Reads endpoint/creds from the `hf` AWS profile (via `boto3.Session(profile_name=...)`)
  so it shares the same setup; namespace from `--namespace`/`HF_NAMESPACE`.
- Pure helpers (unit-testable, no I/O in the logic):
  - `create_if_absent(client, bucket, key, body) -> bool` — `put_object(IfNoneMatch='*')`;
    returns True on create, False on 412.
  - `compare_and_swap(client, bucket, key, mutate_fn, max_retries=5) -> dict` —
    read object + ETag, apply `mutate_fn(bytes) -> bytes`, `put_object(IfMatch=etag)`;
    on 412 re-read and retry; raise after `max_retries`.
  - `is_precondition_failed(ClientError) -> bool` — True for HTTP 412 /
    `PreconditionFailed`.
- `main()` runs a **deterministic sequential simulation** of two writers:
  writer A creates the manifest (wins), writer B's create is rejected; then A and
  B both attempt a CAS — B goes first and succeeds, A's stale-ETag CAS gets a 412
  and retries against the fresh object. Ordering is fixed (no threads) so output
  is reproducible.

### `tests/test_conditional_writes.py` (offline)
- Mock the boto3 S3 client (a small fake or `unittest.mock`). No network.
- Cover: `create_if_absent` returns True then False on 412; `compare_and_swap`
  succeeds first try; `compare_and_swap` retries once after a 412 then succeeds;
  `compare_and_swap` raises after exhausting retries; `is_precondition_failed`
  true/false cases.
- Run with `uv run --script` or `uv run pytest`.

### `cleanup.sh`
- Delete demo objects and the demo bucket (`aws --profile hf s3 rb --force` or
  object deletes then `rb`), remove local temp files. Namespace/bucket resolved
  the same way as the demo scripts. Safe to re-run.

## Testing & verification plan

- **Offline (must pass here):** `tests/test_conditional_writes.py` green under
  `uv run`; every shell script passes `bash -n` and (if available) `shellcheck`;
  `setup_profile.sh` produces a byte-correct profile block against a temp
  `AWS_CONFIG_FILE`.
- **Live (needs real `HFAK…` creds; left for PR review):** running the demos
  end-to-end against a real bucket to confirm the gateway returns 412 as
  documented. This will be flagged as not-run-here rather than assumed.

## Non-goals

No rclone/DuckDB scripts (mentioned only in the talk track). No versioning /
ACL / lifecycle demos (unsupported by the gateway). No multi-region behavior.
