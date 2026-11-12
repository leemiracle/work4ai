# Storage Providers

This module provides storage providers for various cloud providers, implementing the `StorageProvider` protocol for
consistent storage operations across different backends.

## Available Storage Providers

| Provider | Description |
|---------|-------------|
| [`S3StorageProvider`](#s3-storage-provider) | Amazon S3 and S3-compatible storage services with encryption, multipart uploads, and presigned URLs |
| [`AzureBlobStorageProvider`](#azure-blob-storage-provider) | Azure Blob Storage with account-key or SAS-token auth, chunked parallel transfers, and SAS presigned URLs |
| [`LocalStorageProvider`](#local-storage-provider) | Local filesystem storage for development and testing |

## Factory

Each checker service uses **two** storage providers per process: one for downloading request inputs and one for
uploading checker outputs. The direction is configured independently so a single deployment can, for example, download
inputs from S3 while persisting outputs to a local directory.

```python
from services.framework.storage_providers.factory import (
    build_input_storage_provider,
    build_output_storage_provider,
)
from services.settings_base import SettingsBase

settings = SettingsBase()
input_provider = build_input_storage_provider(settings)
output_provider = build_output_storage_provider(settings, key_prefix="my-output-prefix/")
```

`build_input_storage_provider` dispatches on `settings.input_storage_type` and `build_output_storage_provider`
dispatches on `settings.output_storage_type`. Each setting reads its dedicated environment variable first and falls
back to `COSMOS_EVALUATOR_STORAGE_TYPE` when the dedicated variable is unset, so existing single-mode deployments
continue to work without changes:

| Direction | Primary env var                  | Fallback env var          | Default |
|-----------|----------------------------------|---------------------------|---------|
| Input     | `COSMOS_EVALUATOR_INPUT_STORAGE_TYPE`  | `COSMOS_EVALUATOR_STORAGE_TYPE` | `s3`    |
| Output    | `COSMOS_EVALUATOR_OUTPUT_STORAGE_TYPE` | `COSMOS_EVALUATOR_STORAGE_TYPE` | `s3`    |

The supported `_TYPE` values are:
- `"s3"` -- creates an `S3StorageProvider`
- `"azure"` -- creates an `AzureBlobStorageProvider` (requires one of `COSMOS_EVALUATOR_STORAGE_SECRET_KEY` /
  `COSMOS_EVALUATOR_STORAGE_SESSION_TOKEN` as the credential)
- `"local"` -- creates a `LocalStorageProvider` using `key_prefix` as the base directory

### Addressing the target

`COSMOS_EVALUATOR_STORAGE_URL` names the target collection and how to reach it in one value, parsed by
`utils/storage_url.parse_storage_url` into the bucket or container, the Azure storage account, a non-default endpoint
origin, and the AWS region. Addressing the target once keeps those components consistent by construction, where
separate variables can disagree -- a region that contradicts the endpoint's, or a container on the wrong account.

| Backend | Accepted forms | Parsed as |
|---------|----------------|-----------|
| `s3` | `s3://my-bucket` | bucket only; valid only for a named-cluster provider, whose cluster credentials supply the region and endpoint (the plain S3 provider rejects it, see below) |
| `s3` | `https://my-bucket.s3.us-west-2.amazonaws.com` | bucket + region (virtual-hosted style) |
| `s3` | `https://s3.us-west-2.amazonaws.com/my-bucket` | bucket + region (path style) |
| `s3` | `https://pbss.s8k.io/my-bucket` | bucket + endpoint origin, for an S3-compatible cluster |
| `azure` | `https://myacct.blob.core.windows.net/my-container` | account + container |
| `azure` | `http://127.0.0.1:10000/devstoreaccount1/my-container` | account + container + endpoint origin (Azurite, private link) |

The URL names a container, never a key inside it; a deeper path is rejected rather than silently discarded. Local
storage takes no URL, since it resolves keys under the base directory its caller supplies.

Talking to AWS with no region in the URL is an error rather than a silent default, because AWS rejects every request
signed for the wrong region. A custom endpoint is exempt: S3-compatible clusters are not region-scoped.

The backend is configured rather than inferred from the URL, because only the public cloud hostnames are
self-identifying: `https://pbss.s8k.io/my-bucket` is indistinguishable from a private Azure endpoint, so inferring the
backend would silently address the wrong cloud.

`COSMOS_EVALUATOR_INPUT_STORAGE_URL` and `COSMOS_EVALUATOR_OUTPUT_STORAGE_URL` override it per direction, each falling
back to the shared value. They are needed only when the two directions address different targets -- a deployment
reading inputs from S3 and writing outputs to Azure has no single URL that can serve both.

Mixed-mode example - download inputs from S3, write outputs locally:

```bash
COSMOS_EVALUATOR_STORAGE_TYPE=s3
COSMOS_EVALUATOR_OUTPUT_STORAGE_TYPE=local
COSMOS_EVALUATOR_STORAGE_URL=https://my-input-bucket.s3.us-west-2.amazonaws.com
```

> Note: `S3StorageProvider.download_from_url` accepts arbitrary `s3://` and presigned `https://` URLs, so the input
> provider can pull from any bucket regardless of `COSMOS_EVALUATOR_STORAGE_URL`. It also accepts `file://` URIs and
> plain filesystem paths (absolute or relative); see
> [Local-URL fast path on the S3 provider](#local-url-fast-path-on-the-s3-provider) below.

### Credentials

Three settings carry the credentials for every backend, so a deployment supplies one credential set whichever cloud it
addresses:

| Setting | Environment variable | S3 | Azure |
|---------|----------------------|----|-------|
| `storage_access_key` | `COSMOS_EVALUATOR_STORAGE_ACCESS_KEY` | access key ID | unused |
| `storage_secret_key` | `COSMOS_EVALUATOR_STORAGE_SECRET_KEY` | secret access key | account key |
| `storage_session_token` | `COSMOS_EVALUATOR_STORAGE_SESSION_TOKEN` | STS session token | pre-minted SAS token |

Each is read only under its own `COSMOS_EVALUATOR_` name. The ambient `AWS_*` / `AZURE_*` variables are deliberately
not read into these fields, since credentials exported for one target would then be signed into requests for another --
an `AWS_SECRET_ACCESS_KEY` would become the Azure account key.

S3 reads the standard `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` separately, as a fallback
used only when none of the three settings above is set (`SettingsBase.s3_credentials`). The two sets are taken whole,
never merged, since a session token only validates with the key pair it was issued with. The fallback exists because
boto3 reads those variables from the process environment but not from the env files `SettingsBase` loads for local
runs, such as `~/.aws/.env`. When both sets are empty the provider config carries no credentials, which hands
resolution to boto3's own chain: the shared config files and instance metadata. Named-cluster providers resolve
credentials from their cluster-prefixed variables instead (see `_build_cluster`).

### Per-service overrides

Each service's `Settings` class declares its own `env_prefix` (`ARBITRATOR_`, `ATTRIBUTE_VERIFICATION_`, `DATABASE_`,
`HALLUCINATION_`, `OBJECTS_`). The canonical source is the per-service `Settings` classes themselves
(`services/**/settings.py`), and the list above can be derived programmatically from each subclass's
`model_config["env_prefix"]` plus the aliased fields injected by `SettingsBase.__pydantic_init_subclass__`
(e.g. `storage_url` / `COSMOS_EVALUATOR_STORAGE_URL`) if a generator is preferred to this hand-maintained list.
`SettingsBase.__pydantic_init_subclass__` walks every aliased field on the subclass and prepends a
`<env_prefix><FIELD_NAME_UPPER>` alias at the top of its `AliasChoices`. The result is that any service can retarget any
aliased setting individually without changing the deployment-wide defaults. The storage_* fields therefore have the
following alias precedence (highest -> lowest), illustrated for `input_storage_url`:

1. `<SERVICE_PREFIX>INPUT_STORAGE_URL` (e.g. `ATTRIBUTE_VERIFICATION_INPUT_STORAGE_URL`)
2. `COSMOS_EVALUATOR_INPUT_STORAGE_URL`
3. `input_storage_url` (Python kwarg / lowercase env)

The `*_storage_type` fields use the same shape with the umbrella `COSMOS_EVALUATOR_STORAGE_TYPE` sitting under the
per-direction `COSMOS_EVALUATOR_*_STORAGE_TYPE`. The per-direction URLs fall back to `storage_url` in the factory
rather than through the alias chain, so a `<SERVICE_PREFIX>STORAGE_URL` retargets both directions at once. The same
alias rule applies to every aliased field on `SettingsBase`, including `env` and `log_level`.

Worked example - flip attribute_verification alone to local storage while every other service stays on S3:

```bash
export ATTRIBUTE_VERIFICATION_INPUT_STORAGE_TYPE=local
export ATTRIBUTE_VERIFICATION_OUTPUT_STORAGE_TYPE=local
```

## Building output keys: `make_key_prefix`

Each `StorageProvider` exposes `make_key_prefix(*parts) -> str` so callers can join a per-request
`output_storage_prefix` with service-internal segments without knowing which backend they are talking to. The two
backends interpret the parts differently because object stores and filesystems treat leading slashes differently:

| Backend | Semantics |
|---------|-----------|
| `LocalStorageProvider` | Pathlib semantics: the first non-empty part is taken as-is so an absolute path (`/tmp/output`) anchors at the filesystem root, while a relative path resolves against the CWD when used as a key. Tail parts have leading slashes stripped to prevent accidental re-anchoring. The result ends with `/`. |
| `S3StorageProvider` | Strips leading and trailing slashes from every part, drops empties, joins with `/`, and ends with `/`. Leading slashes are not meaningful in S3 keys and break URL round-trip in `utils/s3.parse_s3_url`. |
| `AzureBlobStorageProvider` | Identical to the S3 semantics -- blob names are opaque strings with no notion of an absolute path, and a leading slash breaks URL round-trip in `utils/azure.parse_azure_url`. |

Examples:

```python
s3_provider.make_key_prefix("/tmp/x", "objects_single_view", "cam_front")
# -> "tmp/x/objects_single_view/cam_front/"

local_provider.make_key_prefix("/tmp/x", "objects_single_view", "cam_front")
# -> "/tmp/x/objects_single_view/cam_front/"

local_provider.make_key_prefix("rel-dir", "objects_single_view", "cam_front")
# -> "rel-dir/objects_single_view/cam_front/"
```

Callers concatenate with a filename to build the final key:

```python
prefix = output_storage_provider.make_key_prefix(
    request.output_storage_prefix, "objects_single_view", request.camera_name
)
await output_storage_provider.store_file(local_path, f"{prefix}{filename}", ...)
```

## S3 Storage Provider

### Quick Start

```python
from services.framework.storage_providers import S3StorageProvider
from services.framework.storage_providers.config import S3Config

# Configure and create provider
config = S3Config(bucket_name="my-bucket")
storage = S3StorageProvider(config)

# Basic operations
await storage.store({"key": "value"}, "data.json")
data = await storage.retrieve("data.json")
exists = await storage.exists("data.json")
await storage.delete("data.json")
await storage.close()
```

### Configuration

```python
config = S3Config(
    bucket_name="my-bucket",                    # Required
    aws_access_key_id="key",                   # Optional (use IAM roles)
    aws_secret_access_key="secret",            # Optional
    region_name="us-east-1",                   # Default region
    endpoint_url="https://s3.example.com",     # For S3-compatible services
    server_side_encryption="AES256",           # AES256 or aws:kms
    storage_class="STANDARD",                  # Storage class
    max_concurrency=10                         # Concurrent operations
)
```

### Advanced Usage

```python
# Context manager
async with S3StorageProvider(config) as storage:
    await storage.store("data", "key.txt")

# With metadata
await storage.store(
    data="document",
    key="file.txt",
    metadata={"author": "user", "category": "doc"}
)

# Copy objects
await storage.copy("source.txt", "destination.txt")

# Presigned URLs
url = await storage.generate_presigned_url("file.txt", expiration=3600)

# Custom endpoints (MinIO, DigitalOcean Spaces, etc.)
config = S3Config(
    bucket_name="bucket",
    endpoint_url="https://minio.example.com",
    use_ssl=False
)
```

### Error Handling

```python
from services.framework.storage_providers.exceptions import (
    StorageNotFoundError, StoragePermissionError, S3StorageError
)

try:
    data = await storage.retrieve("file.txt")
except StorageNotFoundError:
    # Handle missing file
except StoragePermissionError:
    # Handle access denied
except S3StorageError as e:
    # Handle S3-specific errors
    print(f"AWS Error: {e.aws_error_code}")
```

### Local-URL fast path on the S3 provider

`S3StorageProvider.download_from_url` accepts more than just `s3://` and presigned `https://` URLs. When the URL is
recognized as local by `utils/local.is_local_url`, the call short-circuits and delegates to
`utils/local.symlink_local_url` -- the same helper that backs `LocalStorageProvider.download_from_url`. This avoids any
boto3 / aiohttp round-trip and keeps cross-provider semantics in lock-step.

Recognized local-URL forms:

- `file:///abs/path/foo.mp4` -- standard empty-authority `file://` URI.
- `file://localhost/abs/path/foo.mp4` -- RFC 8089 `localhost` form, equivalent to the empty-authority form.
- `/abs/path/foo.mp4` -- absolute filesystem path with no URL scheme.
- `rel/path/foo.mp4`, `./foo.mp4`, `foo.mp4` -- relative path resolved against the current working directory.

Schemes `s3://`, `http(s)://`, `gs://`, etc. are *not* local and fall through to the normal S3 / HTTP code paths.

Materialisation mechanism: the destination is created as a **symlink** to the source, never a copy. Code that mutates
the destination will mutate the source; callers that need an independent copy should `shutil.copy2` the result. If the
destination already exists (including a dangling symlink) it is unlinked before the new symlink is created. The
destination's parent directory is created on demand. A missing source raises `FileNotFoundError`.

### Download tuning

`download_from_url` fetches `https://` URLs itself over aiohttp, so its budgets are `S3Config` fields rather than
botocore settings. An object at or above `multipart_threshold` whose server advertises range support is fetched with
concurrent `Range` requests; anything else uses a single streaming GET.

| Field | Default | Purpose |
|-------|---------|---------|
| `multipart_threshold` | 64 MB | Minimum object size before switching to concurrent ranged GETs |
| `multipart_chunksize` | 16 MB | Size of each ranged part |
| `max_concurrency` | 10 | Maximum ranged parts in flight |
| `download_chunk_size` | 1 MiB | Read size when streaming a response to disk |
| `download_sock_connect_timeout` | 30 s | Socket connect timeout |
| `download_sock_read_timeout` | 300 s | Per-read inactivity timeout (replaces aiohttp's default 300 s *total* cap) |
| `download_max_attempts` | 3 | Attempts (initial + retries) per transfer |
| `download_retry_backoff_base` | 0.5 s | Delay before the first retry |
| `download_retry_backoff_factor` | 2.0 | Delay multiplier after each failed attempt |

Transient failures -- `ClientPayloadError`, connection errors, socket timeouts, and 5xx responses -- are retried with
exponential backoff. Non-transient failures (4xx, a refused redirect, a server declining the `Range` request) fail on
the first attempt so the caller's error or fallback path runs without delay. In the ranged path each part retries
independently, releasing its concurrency slot while it backs off, so one flaky connection cannot demote the whole
object to the slower single-stream path.

Retries matter here because aiohttp 3.14 reports a *complete* response as a `ContentLengthError` ("received N of N
bytes") when the connection closes while its parser is paused by read back-pressure. `download_chunk_size` is the
other half of that mitigation: it is passed as the session's `read_bufsize`, which raises the reader's high-water mark
to twice the chunk size, so a larger chunk keeps the parser unpaused for most of a transfer. Worst-case buffering is
`max_concurrency * 2 * download_chunk_size` (20 MiB at the defaults).

## Testing

```bash
# Run S3 storage tests
dazel test //services/framework/storage_providers/tests:s3_storage_provider_test
```

## Azure Blob Storage Provider

### Quick Start

```python
from services.framework.storage_providers.azure_blob_storage_provider import AzureBlobStorageProvider
from services.framework.storage_providers.config import AzureBlobConfig

config = AzureBlobConfig(container_name="my-container", account_name="myaccount", account_key="...")
async with AzureBlobStorageProvider(config) as storage:
    await storage.store({"key": "value"}, "data.json")
    data = await storage.retrieve("data.json")
    urls = await storage.store_file(Path("results.json"), "clip123/results.json", "application/json")
    # urls.raw == "azure://my-container/clip123/results.json"
    # urls.presigned == "https://myaccount.blob.core.windows.net/my-container/clip123/results.json?<read SAS>"
```

### Settings mapping

Every field comes from the shared `COSMOS_EVALUATOR_STORAGE_*` settings; nothing here is Azure-specific:

| `AzureBlobConfig` field | Source | Environment variable |
|---------------------|--------|----------------------|
| `container_name` | storage URL path | `COSMOS_EVALUATOR_STORAGE_URL` |
| `account_name` | storage URL hostname, or its first path segment behind a custom endpoint | `COSMOS_EVALUATOR_STORAGE_URL` |
| `endpoint_url` | storage URL origin, when it is not the public blob host | `COSMOS_EVALUATOR_STORAGE_URL` |
| `account_key` | `storage_secret_key` | `COSMOS_EVALUATOR_STORAGE_SECRET_KEY` |
| `sas_token` | `storage_session_token` | `COSMOS_EVALUATOR_STORAGE_SESSION_TOKEN` |
| `trusted_internal_hosts` | `storage_trusted_internal_hosts` | `COSMOS_EVALUATOR_STORAGE_TRUSTED_INTERNAL_HOSTS` |

`storage_access_key` is unused by this backend, since Azure's Shared Key scheme identifies the signer by the account
name the URL already carries. Sharing the secret fields with S3 is safe because neither is read from an ambient
`AWS_*` / `AZURE_*` variable; see [Credentials](#credentials). All of them also pick up per-service `<PREFIX>_*`
aliases for free, as described in [Per-service overrides](#per-service-overrides).

`endpoint_url` is the service *origin* (e.g. `http://127.0.0.1:10000` for Azurite); the account name is appended as the
first path segment, matching the layout Azurite and private endpoints use. Addressing the public
`https://<account>.blob.core.windows.net` host leaves it unset.

### URL forms

`store` and `store_file` record `azure://<container>/<blob>` as the raw URL -- scheme-tagged like `s3://`, already
recognized by `checks/utils/multistorage.is_remote_path`, and unaffected if the account's endpoint later changes.
`download_from_url` reads that form back, plus the HTTPS forms:

- `azure://<container>/<blob>` -- no account, so it is resolved against the configured one using this provider's
  credential.
- `https://<account>.blob.core.windows.net/<container>/<blob>[?<sas>]` -- the public endpoint. A SAS in the query is
  used as-is and no credential is attached; without one the configured credential is used.
- `<endpoint_url>/<account>/<container>/<blob>[?<sas>]` -- the path-style form, recognized only when `endpoint_url` is
  configured.

Local URLs (`file://` URIs and plain filesystem paths) short-circuit through the same
[`utils/local.symlink_local_url`](#local-url-fast-path-on-the-s3-provider) fast path the S3 provider uses.

> **Scope boundary:** any other URL -- including a presigned `https://` URL on a non-Azure host -- is rejected with
> `AzureBlobStorageError` rather than handed to the Azure SDK. Deployments that need to read arbitrary presigned URLs
> should set `COSMOS_EVALUATOR_INPUT_STORAGE_TYPE=s3`, whose provider fetches any HTTPS URL over plain HTTP and so
> already handles presigned URLs from any cloud, while keeping `COSMOS_EVALUATOR_OUTPUT_STORAGE_TYPE=azure`.

### Presigned URLs

With `account_key` set, `generate_presigned_url` mints a fresh blob SAS with the requested lifetime, mapping the
protocol's S3-flavored `operation` argument onto Azure permissions: `put_object` yields a create+write SAS, anything
else a read-only one. With only `sas_token` configured there is no signing key, so the configured token is appended
instead and the URL's real expiry is whatever that token carries -- `expiration` cannot be honored, and a line is
logged saying so.

### Transfers

The Azure SDK splits large blobs into chunks and fans them out itself, so `AzureBlobConfig` has a single
`max_concurrency` knob (default 10) and needs no equivalent of the S3 provider's
[hand-rolled ranged downloader](#download-tuning).

### Error handling

Azure exceptions are mapped onto the same backend-neutral errors the S3 provider raises, so callers need no
provider-specific handling:

| Azure exception | Raised as |
|-----------------|-----------|
| `ResourceNotFoundError` | `StorageNotFoundError` |
| `ClientAuthenticationError` | `StorageAuthenticationError` |
| `HttpResponseError` (403) | `StoragePermissionError` |
| `HttpResponseError` (quota error codes) | `StorageQuotaExceededError` |
| `ServiceRequestError` | `StorageConnectionError` |
| anything else | `AzureBlobStorageError` (carries `container` and `error_code`) |

### Testing

```bash
dazel test //services/framework/storage_providers/tests:azure_blob_storage_provider_test
dazel test //services/framework/storage_providers/utils/tests:azure_test
```

## Local Storage Provider

The `LocalStorageProvider` stores files on the local filesystem. It is useful for development, testing, and
environments without cloud storage.

```python
from services.framework.storage_providers.local_storage_provider import LocalStorageProvider

provider = LocalStorageProvider(base_path="/tmp/cosmos-evaluator-output")
async with provider as p:
    urls = await p.store_file(Path("results.json"), "clip123/results.json", "application/json")
    # urls.raw contains the local file path; urls.presigned is None
```

Key behaviors:
- `store_file` copies files into the `base_path` directory.
- `download_from_url` delegates to the shared `utils/local.symlink_local_url` helper, which symlinks `file://` URIs and
  plain filesystem paths into `destination`. The same helper backs the local-URL fast path on
  `S3StorageProvider.download_from_url`.
- `generate_presigned_url` returns the local filesystem path (presigned URLs don't apply to local storage).
- `make_key_prefix` uses pathlib semantics: an absolute first part anchors at filesystem root, so a per-request
  `output_storage_prefix` of `/tmp/output` writes to `/tmp/output/...` regardless of `base_path`. See the
  [Building output keys](#building-output-keys-make_key_prefix) section above.

## Adding New Storage Providers

To add new storage providers, implement the `StorageProvider` protocol:

1. Create provider class implementing the protocol
2. Add Pydantic configuration class (if needed)
3. Register the new type in `factory.py`
4. Write comprehensive unit tests

Example structure:
```bash
storage_providers/
├── s3_storage_provider.py           # Amazon S3
├── azure_blob_storage_provider.py   # Azure Blob Storage
├── local_storage_provider.py        # Local filesystem
├── gcs_storage_provider.py          # Google Cloud Storage (future)
├── factory.py                       # Provider factory
├── utils/                           # URL helpers, grouped by URL family
│   ├── s3.py                        #   parse_s3_url, S3UrlComponents, is_presigned_url_s3
│   ├── azure.py                     #   parse_azure_url, AzureBlobUrlComponents, is_azure_blob_url
│   └── local.py                     #   is_local_url, symlink_local_url
└── tests/                           # Unit tests for each provider
```
