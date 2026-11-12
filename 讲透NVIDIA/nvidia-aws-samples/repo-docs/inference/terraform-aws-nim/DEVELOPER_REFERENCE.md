# terraform-aws-nim — Developer Reference

Internal reference for contributors. For user-facing docs, see [README.md](README.md).

---

## Table of Contents

1. [Inference Protocols and the Choices in This Module](#inference-protocols-and-the-choices-in-this-module)
2. [Per-URI CodeBuild Architecture](#per-uri-codebuild-architecture)
3. [GPU Instance Reference](#gpu-instance-reference)
4. [NIM Model Profile Cache](#nim-model-profile-cache)
5. [Model Profile Auto-Selection Logic](#nim-model-profile-auto-selection-and-pre-caching)
6. [Design Decisions](#design-decisions)
7. [SageMaker Shim (Temporary)](#sagemaker-shim-temporary)
8. [EKS](#eks)
9. [Alpamayo-Specific Notes](#alpamayo-specific-notes)
10. [Open Questions](#open-questions)

---

## Inference Protocols and the Choices in This Module

Different NIM families use different inference protocols. This section is the single
reference for what each protocol is, why different NIMs picked different ones, what
patterns the broader industry uses for large payloads, and what the module supports today.

### REST vs GraphQL vs gRPC — three API styles

These are the three dominant **API styles** for service-to-service communication.
They sit on top of different transport choices and serialize data differently.

| Style | Transport | Schema | Wire format | Typical use |
|---|---|---|---|---|
| **REST** | HTTP/1.1 or HTTP/2 | None required (often documented via OpenAPI) | JSON (usually) | Web APIs, public APIs, simple CRUD, LLM inference today |
| **GraphQL** | HTTP (any version) | GraphQL schema (typed) | JSON | Frontend-driven APIs where clients pick which fields they want |
| **gRPC** | HTTP/2 (required) | Protocol Buffers (`.proto` files) | Binary protobuf | High-throughput strongly-typed internal APIs, ML inference with binary payloads |

Concrete shape difference for "get user 42":

```
REST:
  GET /users/42 HTTP/1.1
  → {"id": 42, "name": "Alice", "email": "alice@example.com"}

GraphQL:
  POST /graphql
  Body: {"query": "{ user(id: 42) { name } }"}
  → {"data": {"user": {"name": "Alice"}}}
  (client asked for only `name`; server didn't send `email`)

gRPC (wire is binary protobuf — shown conceptually):
  UserService/GetUser({id: 42})
  → User{id: 42, name: "Alice", email: "alice@example.com"}
```

### Transport protocols under the API styles

API style is the contract; transport protocol is the wire. Five transports matter for
modern web + ML APIs:

| Protocol | What it is | Streaming | Typical use |
|---|---|---|---|
| **HTTP/1.1** | Classic request/response over TCP. One request → one response. No multiplexing (head-of-line blocking when reusing a connection). | None (chunked transfer ≈ stream but limited) | Most REST APIs |
| **HTTP/2** | Binary framing, multiplexed (parallel streams on one TCP connection), server push, header compression | Yes (chunked frames) | Modern web, foundation for gRPC |
| **SSE (Server-Sent Events)** | One-way stream from server to client over HTTP. Server emits `data: ...\n\n` lines. | Server → client one-way | Streaming LLM tokens (OpenAI `stream: true`), live UI updates |
| **WebSockets** | Bidirectional persistent connection. Client and server upgrade from HTTP to WS, then send frames freely. | Bidirectional | Chat apps, multiplayer games, live dashboards |
| **gRPC** | RPC framework built on HTTP/2. Uses Protocol Buffers (binary schema) instead of JSON. Supports 4 call patterns: unary, server-streaming, client-streaming, bidirectional-streaming. | All 4 patterns | Internal microservices, ML inference, binary payloads |

Concrete performance differences (verified — see Sources):

- A 1000-byte JSON payload is typically ~300 bytes in protobuf (3× size reduction).
- gRPC is roughly 7× faster receiving and 10× faster sending vs REST for typical ML payloads.
- gRPC reduces inference latency by 40-60% vs REST in benchmarks.
- These gains scale with payload size — for text-sized LLM prompts the differences are
  small; for MB+ video/audio they're dominant.

### Why LLMs default to REST + JSON (not gRPC)

LLM inference uses REST + JSON across nearly every provider (OpenAI, Anthropic, NVIDIA
NIM-LLM, Bedrock, Cohere, Mistral, Groq, Together). Three reasons:

1. **OpenAI set the de facto standard.** When OpenAI launched the GPT-3 API in 2020,
   they chose REST + JSON. Every later provider wanted "drop-in compatible" so apps
   could swap providers — they adopted the OpenAI-compatible REST shape. The network
   effect locked in.

2. **Text payloads are small.** A long-context LLM request might be ~100 KB of JSON;
   gRPC's binary efficiency only matters at MB+ payloads. The protocol overhead
   savings aren't worth the developer-ergonomics tradeoff at LLM payload sizes.

3. **Developer ergonomics.** Every web developer can `curl` JSON. gRPC requires
   installing tooling, generating client code from `.proto` files (or using
   reflection), and learning protobuf semantics. For "ship a chatbot in 2 hours,"
   REST wins.

gRPC dominates inside ML infrastructure (Triton Inference Server, internal model
serving, computer-vision / audio pipelines) where you control both sides, payloads
are large/binary, and latency/throughput matter. The end-user-facing LLM APIs
stuck with REST because of standards-coordination + payload sizes.

### Why media NIMs use gRPC

Maxine NIMs (Synthetic Video Detector, Audio2Face, Studio Voice, Eye Contact, BNR)
expose **gRPC as the primary inference protocol**. The HTTP endpoint that some media
NIMs also expose is for admin/health probes only — actual inference goes over gRPC.

Reason: media payloads (video, audio) are tens to hundreds of MB. JSON-over-HTTP
would require base64-encoding binary data into the request body, inflating size by
~33% AND adding parse/serialize cost on both sides. For a 100 MB video that's an
extra ~33 MB on the wire and meaningful CPU on both client and server.

gRPC's protobuf `bytes` type + HTTP/2 streaming handles this natively — binary
bytes flow as-is, no encoding overhead. This is also why Triton Inference Server
(NVIDIA's general ML serving framework) supports both HTTP and gRPC: HTTP for
small payloads + dev ergonomics, gRPC for media and large tensors.

The tradeoff: media NIM customers can't simply `curl` the endpoint. They need a
gRPC client — typically a Python script using `grpc` + `grpcio-tools`, or a
language-specific client generated from the `.proto` schema. NVIDIA publishes
sample Python clients per Maxine NIM at
[NVIDIA-Maxine/nim-clients](https://github.com/NVIDIA-Maxine/nim-clients).

### OpenAI Spec vs OpenAPI Spec — different things, similar names

A frequent confusion. They're entirely different things.

|  | OpenAI Spec | OpenAPI Spec |
|---|---|---|
| What it is | The specific API shape OpenAI publishes — endpoints, request/response field names, etc. | A vendor-neutral standard for **describing** any REST API (a YAML/JSON document) |
| Who owns it | OpenAI (the company) | OpenAPI Initiative (Linux Foundation), formerly Swagger |
| Used for | Sending requests to OpenAI-compatible LLM servers | Generating clients, server stubs, and docs from a spec file |
| Example | `POST /v1/chat/completions` with `{"messages": [...], "model": "gpt-4"}` | An `openapi.yaml` file that says "this API has endpoint X with params Y returning Z" |

When people say "OpenAI-compatible API" they mean "implements the OpenAI Spec's
shape." A given API can have an `openapi.yaml` document (OpenAPI Spec) that
describes OpenAI's API (OpenAI Spec). They co-exist; they aren't interchangeable.

NVIDIA NIM-LLM implements OpenAI Spec for inference (`/v1/chat/completions`,
`/v1/completions`, `/v1/embeddings`). Its full schema can also be retrieved as an
OpenAPI document — but those are two separate facts.

### `max_tokens` — request size or response cap?

`max_tokens` is a **response-side cap**, not a request-size limit. Three things to know:

1. **Generation stops naturally OR at the cap, whichever comes first.** If you set
   `max_tokens: 100` and the model would naturally generate 80 tokens (ending at a
   sentence boundary / end-of-sequence), response is 80 tokens. If the model would
   keep going to 200, response is truncated at 100 and the response includes
   `finish_reason: "length"` so callers know it was cut.

2. **Truncated tokens are NOT queued.** The model literally stops sampling. You can't
   "get the rest" without re-issuing the request with the partial response as context.

3. **Request size is bounded separately by the model's context window** (`max_model_len`
   in vLLM, varies per model — e.g., 131072 for Llama-3.1). The context window counts
   **both input AND output tokens together**. A 131K-token model with a 100K-token
   prompt has at most 31K tokens of response headroom.

UI sliders like "fast / balanced / detailed" typically bundle `max_tokens` +
`temperature` + sometimes `top_p`:

```jsonc
// "Fast / concise"
{ "max_tokens": 200,  "temperature": 0.3 }

// "Balanced" (default)
{ "max_tokens": 1000, "temperature": 0.7 }

// "Detailed / creative"
{ "max_tokens": 4000, "temperature": 0.9, "top_p": 0.95 }
```

### Large-payload pattern (cloud-storage handoff)

For any payload that strains JSON-over-HTTP — large videos, audio, images,
multi-MB tensors — the industry-standard pattern is **don't put the payload in
the request body. Put it in cloud storage and pass a URL.**

Variations:

- **Pre-signed URLs**: Caller uploads to S3/GCS/Azure Blob directly (via a
  pre-signed PUT URL the API generates), then submits a short JSON request
  containing the URL. The API server fetches the content from storage at
  inference time.
- **Direct cloud-storage URI in the request**: Caller has already uploaded; just
  passes `s3://bucket/key` (or equivalent) in the JSON body. API fetches it.
- **Async pattern**: Caller uploads to S3 input prefix, API queues the request,
  writes output to S3 output prefix. (SageMaker async is this pattern — see below.)

Real-world examples:

- **Google Gemini API** accepts pre-signed S3/GCS/Azure URLs as input — supports
  up to 5 TB files. The API server pulls the content during processing.
- **AWS API Gateway** has a hard 10 MB payload limit. Anything bigger forces
  the pattern.
- **SageMaker async inference** uses S3 input + S3 output internally (see below).
- **YouTube uploads** use pre-signed URLs at scale.

NVIDIA NIM containers do not natively support a `file_url` input mode today —
they accept inline bytes via gRPC. For cloud deployments where the desired
shape is "drop a file in S3 → get a result in S3," the wrapper has to be built
at the deployment layer (Lambda + S3 event → call NIM via gRPC → write result
to S3). This module's `feat: S3-async wrapper for gRPC NIMs` follow-up issue
(see TODO.md) tracks adding this as an opt-in.

### SageMaker Async — and why we don't replicate it on EKS in Phase 1

[SageMaker async inference](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html)
is the AWS-platform equivalent of the S3-handoff pattern. The model is the same
container running synchronously; the **wrapping** is what makes it async:

1. Caller uploads payload to S3 (any bucket they own).
2. Caller calls `InvokeEndpointAsync` with `InputLocation = s3://bucket/key`.
3. SageMaker queues the request, returns `OutputLocation` immediately.
4. SageMaker pulls payload from S3, invokes the container's `/invocations` endpoint
   internally, writes the response to S3.
5. (Optional) SNS notification fires on success or error.
6. Caller polls S3 or listens to SNS for completion.

What SageMaker provides — and we'd have to rebuild on EKS:

- The `InvokeEndpointAsync` HTTPS API and request queue
- The S3 download into the container
- The S3 upload of the response
- The SNS notification
- Concurrency/queue management

For EKS-hosted NIMs, **none of that is built in**. To replicate the async pattern,
we'd need (at minimum): a Lambda that listens for S3 input events, downloads the
input, calls the NIM via gRPC, writes the response, fires SNS. Per Maxine NIM
that's a custom Lambda (because each NIM has different gRPC method names and
input/output protos).

This is meaningful engineering — tracked as a separate feature (`feat: S3-async
wrapper for gRPC NIMs`) and not in Phase 1 gRPC scope. The cleaner upstream
fix is for NIM containers to support `file_url` input directly (CSP-agnostic);
that's also the feedback already sent to the NIM team.

### grpcurl — `curl` for gRPC

[`grpcurl`](https://github.com/fullstorydev/grpcurl) is a single-binary CLI tool
that lets you invoke gRPC methods from the command line. Install via Homebrew
(`brew install grpcurl`) or from GitHub releases. It's the standard tool for
smoke-testing gRPC services.

How it differs from `curl`:

- `curl` speaks HTTP and emits/parses text or JSON. Can't speak gRPC because
  gRPC is binary protobuf over HTTP/2.
- `grpcurl` accepts JSON input — it converts JSON to protobuf bytes on the
  wire, then converts the response protobuf back to JSON for display. So you
  get JSON ergonomics without installing protoc or generating client code.
- Uses **gRPC reflection** when the server supports it
  ([gRPC Reflection Guide](https://grpc.io/docs/guides/reflection/)). With
  reflection enabled, grpcurl can list services and methods on the server
  without you supplying a `.proto` file. Most NIMs enable reflection.

Common commands:

```bash
# Standard gRPC health probe — works on any gRPC server with grpc.health.v1
grpcurl -plaintext <host>:<port> grpc.health.v1.Health/Check
# Expected response: {"status": "SERVING"}

# List services on a reflection-enabled server
grpcurl -plaintext <host>:<port> list

# Describe a specific method (uses reflection)
grpcurl -plaintext <host>:<port> describe <service.Method>

# Invoke a method with JSON input (-d flag)
grpcurl -plaintext -d '{"field": "value"}' <host>:<port> <service.Method>
```

For actual media-NIM inference (mp4 → scores, audio → text, etc.), `grpcurl` is
not the right tool because real video/audio bytes don't fit cleanly in JSON.
`grpcurl` is for **smoke-testing the wiring** (does the server respond? is the
service registered?); production inference uses language-specific clients.

### What this module supports today

| Deployment path | Protocol | Wire | Where in code |
|---|---|---|---|
| SageMaker NIM (any NIM family) | HTTP via Caddy shim → framework's native HTTP path | HTTPS via SageMaker's `InvokeEndpoint(Async)` | `shim/launch.sh` + Caddy config in `shim/` |
| SageMaker open-weight (vLLM) | HTTP via Caddy shim → vLLM HTTP | HTTPS via SageMaker | Same shim |
| EKS NIM-LLM / embedding / speech | HTTP via NLB → NIM HTTP endpoint | NLB TCP listener, HTTP/1.1 over the wire | `modules/eks-app/buildspecs/deploy-nim.yml` (Helm path) |
| EKS open-weight (vLLM) | HTTP via NLB → vLLM HTTP | NLB TCP listener, HTTP/1.1 over the wire | Same buildspec (kubectl path) |
| **EKS NIM gRPC (Phase 1)** | **gRPC via NLB → NIM gRPC endpoint** | **NLB TCP passthrough (HTTP/2 over the wire)** | **Same buildspec (kubectl gRPC path)** |

Phase 1 specifically scopes gRPC to the EKS NIM path. SageMaker gRPC is not in
scope because SageMaker's `/invocations` contract is HTTP-only — supporting gRPC
on SageMaker would require building a translation layer (`/invocations` HTTP →
internal gRPC call). Tracked as out-of-scope for Phase 1; revisit if a customer
needs it.

### Runtime findings — gRPC probe timeouts

The raw-kubectl gRPC path emits Deployment liveness + readiness probes using
Kubernetes' native `grpc:` probe type against the container's gRPC health port.
Default `timeoutSeconds: 1` is too tight for GPU-bound NIMs — under sustained
inference load, the CPU context that services the health RPC can be delayed
past a 1-second window while the GPU is mid-invocation, causing spurious
liveness failures and kubelet-initiated pod restarts even though the pod is
functionally healthy.

Symptom in real deployment (Maxine SVD on T4 under sustained load): pods
restarted repeatedly with `Warning Unhealthy: Liveness probe failed: timeout:
health rpc did not complete within 1s`. The pods themselves were serving
inference correctly — the restarts were purely probe-timeout artifacts.

Fix baked into the buildspec: both readiness and liveness gRPC probes carry
`timeoutSeconds: 10`. Provides 10x headroom over the observed worst-case
health-RPC latency without materially delaying legitimate liveness detection.
See [`modules/eks-app/buildspecs/deploy-nim.yml`](modules/eks-app/buildspecs/deploy-nim.yml)
gRPC probe emission block.

### Sources

- [IBM — gRPC vs REST](https://www.ibm.com/think/topics/grpc-vs-rest)
- [Uplatz — Architecting ML Inference: REST, gRPC, and Streaming Interfaces](https://uplatz.com/blog/architecting-ml-inference-a-definitive-guide-to-rest-grpc-and-streaming-interfaces/)
- [Latitude Blog — Serialization Protocols for Low-Latency AI Applications](https://latitude-blog.ghost.io/blog/serialization-protocols-for-low-latency-ai-applications/)
- [Boundev — gRPC vs REST](https://www.boundev.ai/blog/grpc-vs-rest-api-comparison-guide)
- [Toptal — gRPC vs REST](https://www.toptal.com/developers/grpc/grpc-vs-rest-api)
- [Inference Protocols and APIs — NVIDIA Triton Inference Server](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/customization_guide/inference_protocols.html)
- [NVIDIA NIM Maxine Synthetic Video Detector — Basic Inference](https://docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/basic-inference.html)
- [NVIDIA-Maxine/nim-clients](https://github.com/NVIDIA-Maxine/nim-clients)
- [Asynchronous inference — Amazon SageMaker AI](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html)
- [Gemini API — file input methods](https://ai.google.dev/gemini-api/docs/file-input-methods)
- [System Design Pattern: Handling Large Blobs with Presigned URLs (Medium)](https://medium.com/@priyasrivastava18official/system-design-pattern-handling-large-blobs-with-presigned-urls-the-secret-sauce-behind-0e73f4adbe63)
- [AWS — ML inference at scale using AWS serverless](https://aws.amazon.com/blogs/machine-learning/machine-learning-inference-at-scale-using-aws-serverless/)
- [grpcurl — GitHub](https://github.com/fullstorydev/grpcurl)
- [gRPC Reflection Guide](https://grpc.io/docs/guides/reflection/)

---

## Per-URI CodeBuild Architecture

One CodeBuild project per unique source URI (and per unique URI × instance_type combo for
caching). Two endpoints sharing the same `source_image_uri` share one base-sync project and
one shim project but get separate cache projects if they target different instance types.

**Why per-URI?** With a single looping project, any failure (e.g. NGC access denied for one
model) blocks all endpoints and loses the build log context for the successful ones. Per-URI
projects fail independently, can be retried individually, and produce clean per-image logs.

### Flowchart

```
source_image_uri (nvcr.io/... or <account>.dkr.ecr.<region>.amazonaws.com/...)
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  CodeBuild — base-sync                              │
│  Buildspec: buildspecs/base-sync.yml                │
│  One project per unique URI (sync_to_ecr = true)   │
│                                                     │
│  if nvcr.io URI → NGC auth (ngc_credentials)       │
│  if ECR URI     → IAM auth                          │
│  → docker pull → docker tag → docker push ECR:base  │
│                                                     │
│  Idempotent: skips if ECR tag already exists.       │
│  No Dockerfile — pure pull/push.                    │
└──────────────────────┬──────────────────────────────┘
                       │
           ┌───────────┴──────────────────┐
           ▼                              ▼
┌───────────────────────────┐  ┌──────────────────────────────────────────────────┐
│  CodeBuild — shim         │  │  CodeBuild — model-profile-cache                 │
│  One project per URI      │  │  One project per URI × instance_type             │
│  (SageMaker endpoints)    │  │  (only when enable_model_profile_cache = true)   │
│                           │  │                                                  │
│  pre_build: polls paired  │  │  pre_build: polls paired base-sync project       │
│  base-sync project        │  │  Build (CPU-only, no GPU fleet):                 │
│  Build:                   │  │    list-model-profiles → auto-select profile     │
│    docker build           │  │    (or prefix-match MODEL_PROFILE override)      │
│    shim/Dockerfile        │  │    download-to-cache -p <profile> → S3           │
│    → ECR:shim             │  │                                                  │
│                           │  │  Idempotent: skips if S3 prefix already warm.    │
│  SageMaker only.          │  └──────────────────────┬───────────────────────────┘
│  EKS uses ECR:base.       │                         │
└─────────┬─────────────────┘                         │
          │                               ┌───────────┴──────────┐
          ▼                               │                      │
┌─────────────────────┐               SageMaker              EKS
│  SageMaker endpoint │               aws s3 sync at         init container:
│  ECR:shim image     │               startup →               aws s3 sync →
│  realtime or async  │               MODEL_PROFILE_CACHE     emptyDir →
└─────────────────────┘               → /opt/nim/.cache       /opt/nim/.cache
```

### Trigger Sequencing (Terraform Actions)

All CodeBuild projects use `for_each` on the URI maps from `locals.tf`. Each project instance
has a paired `action "aws_codebuild_start_build"` and `terraform_data` trigger — one per URI
(or URI × instance_type for cache).

**Bug**: `depends_on` between `terraform_data` resources with `action_trigger` is silently
ignored — base-sync and shim/cache triggers fire in parallel regardless (GitHub issue #37930).

**Workaround**: Each downstream buildspec (`shim.yml`, `model-profile-cache.yml`) polls its
own paired base-sync project by name in `pre_build`. Two-phase approach:

1. **Wait for IN_PROGRESS** (up to 60s, 12 × 5s): poll `list-builds-for-project` until
   the current base-sync build shows as `IN_PROGRESS`. Without this, the downstream build
   might grab the previous apply's already-SUCCEEDED build ID and proceed immediately before
   the current base-sync has pushed any images.

2. **Wait for SUCCEEDED** (up to 30min, 180 × 10s): once an IN_PROGRESS build is found,
   poll until it completes. Fail loudly if it doesn't SUCCEED.

The `BASE_SYNC_PROJECT` env var injected per project points to the exact paired base-sync
project name. When `sync_to_ecr = false`, `BASE_SYNC_PROJECT` is empty and polling is skipped.

Remove this workaround once HashiCorp fixes the `action_trigger` + `depends_on` bug.

### `action` Blocks and `for_each`

`action` blocks support `for_each` (confirmed). `count` is NOT supported on action blocks.
The trigger resources (`terraform_data`) also use `for_each` — an empty map produces no
triggers, so projects only fire when their input map has entries.

```hcl
# codebuild.tf — representative pattern
action "aws_codebuild_start_build" "base_sync" {
  for_each = local.base_sync_map
  config {
    project_name = aws_codebuild_project.base_sync[each.key].name
    timeout      = 3600
  }
}

resource "terraform_data" "build_trigger_base_sync" {
  for_each = local.base_sync_map
  input    = jsonencode({ config = each.value, rebuild_token = local.rebuild_token })
  lifecycle {
    action_trigger {
      events  = [before_create, before_update]
      actions = [action.aws_codebuild_start_build.base_sync[each.key]]
    }
  }
}
```

### Project naming

Project names embed the sanitized canonical URI (dots replaced with `-`):

| Type | Pattern | Example |
|------|---------|---------|
| base-sync | `{prefix}-base-sync-{safe_canonical}` | `nim-dev-base-sync-llama-3-1-8b-instruct-1-8-3` |
| shim | `{prefix}-shim-{safe_canonical}` | `nim-dev-shim-llama-3-1-8b-instruct-1-8-3` |
| cache | `{prefix}-model-profile-cache-{safe_canonical}--{instance}` | `nim-dev-model-profile-cache-llama-3-1-8b-instruct-1-8-3--g6e-12xlarge` |

`safe_canonical` is derived from the `source_image_uri` image name + version with all dots
replaced by hyphens. CodeBuild project names allow only `[A-Za-z0-9\-_]`.

---

## GPU Instance Reference

TRT engines are **not portable across GPU architectures** (SM versions). Engines built on
L40S (SM89) will not load on H100 (SM90) or A100 (SM80). Each instance family writes to and
reads from a separate S3 prefix under `engines/<arch>/` (within the trt-cache bucket).

| Instance Family | GPU    | SM  | VRAM per GPU | GPUs (by size)¹ | Typical Avail. | SageMaker | EKS |
|-----------------|--------|-----|--------------|-----------------|----------------|-----------|-----|
| `ml.g5`  / `g5`   | A10G   | 86  | 24 GB      | 1/1/1/1/4/1/4/8 | High           | TBD†      | Yes |
| `ml.g6`  / `g6`   | L4     | 89  | 24 GB      | 1/1/1/1/4/1/4/8 | Medium         | Yes       | Yes |
| `ml.g6e` / `g6e`  | L40S   | 89  | 48 GB      | 1/1/1/1/4/4/8   | Low-Medium     | Validated | Yes |
| `ml.p4d` / `p4d`  | A100   | 80  | 40 GB      | 8               | Enterprise     | Yes       | Yes |
| `ml.p4de`/ `p4de` | A100   | 80  | 80 GB      | 8               | Enterprise     | Yes       | Yes |
| `ml.p5`  / `p5`   | H100   | 90  | 80 GB      | 8               | Very limited   | Yes       | Yes |
| `ml.p5e` / `p5e`  | H200   | 90  | 141 GB     | 8               | Very limited   | Yes       | Yes |

¹ GPU counts follow xlarge/2xl/4xl/8xl/12xl/16xl/24xl/48xl sizing. The `locals.tf`
`instance_gpu_count` table is the authoritative source for module behavior — see
[GPU resource requests and the NVIDIA device plugin](#gpu-resource-requests-and-the-nvidia-device-plugin).

**S3 model profile cache paths** — `nim-cache/{canonical}/{instance_type}/` where
`canonical = {image-name}-{version}` derived from `source_image_uri`:

| source_image_uri (example)                        | Instance type      | S3 prefix                                              |
|---------------------------------------------------|--------------------|--------------------------------------------------------|
| `nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3`   | `ml.g5.12xlarge`   | `nim-cache/llama-3.1-8b-instruct-1.8.3/g5.12xlarge/`  |
| `nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3`   | `ml.g6e.12xlarge`  | `nim-cache/llama-3.1-8b-instruct-1.8.3/g6e.12xlarge/` |
| `nvcr.io/nim/meta/llama-3.1-70b-instruct:1.2.0`  | `ml.p5.48xlarge`   | `nim-cache/llama-3.1-70b-instruct-1.2.0/p5.48xlarge/` |

The canonical segment ensures that different NIM versions never share a cache entry even on
the same instance type. The full EC2 instance type (not just the family) is used as the
second segment so profiles are GPU-count-specific — `ml.g6e.12xlarge` (4× L40S) and
`ml.g6e.48xlarge` (8× L40S) get separate prefixes.

EKS instance types have no `ml.` prefix — `locals.tf` strips it for both platforms so the
same S3 prefix works for SageMaker and EKS endpoints on the same instance type.

† g5 previously had a SageMaker startup timeout issue. Re-testing in progress;
see [Alpamayo-Specific Notes](#g5-re-test-plan).

---

## NIM Model Profile Cache

### How standard NGC NIMs work

Every NIM container ships a runtime stack and a model manifest. At startup, NIM detects the GPU,
selects the matching pre-compiled profile from the manifest, and downloads it from NGC
into `$NIM_CACHE_PATH` (default `/opt/nim/.cache`). On subsequent starts with the same cache
populated, NIM skips the NGC download entirely.

`download-to-cache` is the built-in CLI utility that performs this download ahead of time:

```bash
docker run --rm \
  -e NGC_API_KEY=$NGC_API_KEY \
  -v $LOCAL_CACHE:/opt/nim/.cache \
  $NIM_IMAGE \
  download-to-cache -p <profile-name>
```

### S3 cache flow

```
  [enable_model_profile_cache = true]
  CodeBuild #3 — model-profile-cache (CPU, no GPU fleet):
    list-model-profiles → select best profile for INSTANCE_TYPE
    download-to-cache -p <profile>
    aws s3 sync → S3:nim-cache/<canonical>/<instance-type>/
                        │
           ┌────────────┴───────────────┐
           │                            │
   SageMaker container              EKS pod
   launch.sh: aws s3 sync at        init container: aws s3 sync
   startup → /opt/nim/.cache         → emptyDir → /opt/nim/.cache
   NIM finds profile, skips NGC      NIM finds profile, skips NGC
```

### Variables

| Variable | Effect |
|---|---|
| `enable_model_profile_cache = true` | Creates nim-cache S3 bucket; triggers CPU CodeBuild job to pre-download model profile; wires `MODEL_PROFILE_CACHE` env to SageMaker container |
| `model_profile = null` | Auto-select best profile for `sagemaker_config.instance_type` (GPU arch + tp count + bf16) |
| `model_profile = "vllm-bf16-tp1"` | Prefix-match override — resolved to full profile name via `list-model-profiles` |

### Module usage example

```hcl
module "nim" {
  source         = "git::https://github.com/NVIDIA/nvidia-aws-samples.git//inference/terraform-aws-nim?ref=main"
  project_prefix = "nim-llama"
  environment    = "prod"

  ngc_credentials = { api_key = var.ngc_api_key }

  sagemaker_endpoints = {
    llama-3-1-8b-instruct = {
      source_image_uri           = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
      instance_type              = "ml.g6e.12xlarge"
      endpoint_type              = "realtime"
      enable_model_profile_cache = true
      container_startup_timeout  = 600  # warm S3 cache: ~7 min; cold: ~15-20 min
      # model_profile = null            # auto-select (recommended)
    }
  }
}
```

---

## NIM Model Profile Auto-Selection and Pre-Caching

### How NIMs select profiles natively

When a standard NGC NIM container starts on real GPU hardware, it runs a built-in
profile selection routine before starting the inference server:

1. Calls `nvidia-smi` (or equivalent CUDA device query) to detect:
   - GPU architecture (SM version, e.g. SM89 for L40S)
   - Number of visible GPUs
   - VRAM per GPU
2. Reads the model manifest (`/opt/nim/etc/default/model_manifest.yaml`) which lists every
   available profile and its hardware requirements (GPU arch, tp count, VRAM floor)
3. Selects the best matching profile — preferring TRT-LLM (lower latency) over vLLM,
   matching tp count to GPU count, preferring bf16 over fp8/int4 unless VRAM is tight
4. Calls `download-to-cache -p <full-profile-name>` to fetch that profile from NGC
   into `$NIM_CACHE_PATH` (default `/opt/nim/.cache`)
5. Starts the inference server, which reads from the populated cache

This is automatic and GPU-aware — no user input required when NIM has direct access to
the target GPU hardware and an NGC API key.

### Why we replicate this logic in Terraform

The module pre-caches the model profile to S3 **before** the SageMaker endpoint is
created, so the container syncs from S3 at startup (~5 min) instead of downloading from
NGC each time. This requires running `list-model-profiles` and `download-to-cache` in a
CodeBuild job.

**The problem:** we cannot use the same native auto-detection (nvidia-smi) that NIMs use
at runtime, because of how CodeBuild GPU support works.

### CodeBuild GPU limitations and cost

CodeBuild supports GPU instances only through **reserved capacity fleets** (`aws_codebuild_fleet`
with `compute_type = CUSTOM_INSTANCE_TYPE`). A fleet's `base_capacity` minimum is 1 —
meaning the fleet always has at least one instance running and **always incurs idle charges**,
even when no builds are running.

For a one-time profile pre-caching job (a few GB downloaded once, then cached in S3),
provisioning a dedicated GPU fleet is not cost-effective. An `ml.g6e.12xlarge`-equivalent
fleet running idle costs several dollars per hour for what amounts to a single 5-10 minute
download job.

**The ideal scenario** would be to run `download-to-cache` on the same exact instance
type as the inference compute — that way NIM's native auto-detection via `nvidia-smi`
would just work: detect the GPU, pick the right profile, download it. No custom logic
needed. But the fleet idle cost makes this impractical for a one-time pre-cache operation.

**The solution:** run profile selection on a standard CPU CodeBuild instance
(`BUILD_GENERAL1_LARGE`) with no GPU and no fleet. `list-model-profiles` and
`download-to-cache -p <name>` are both CPU-only operations — they do not require a GPU
to run. The NIM container can list and download profiles without a GPU present.

### `--all` is not viable

`download-to-cache --all` downloads profiles for every GPU architecture × tp count ×
precision combination available for the model. For even a small model (1B parameters),
this is 100 GB+, because TRT engines are compiled separately for each GPU family (A10G,
L40S, L4, H100, A100), and each combination of tp count and precision gets its own artifact.
For a 70B model, `--all` can exceed 500 GB. Never use `--all` as a default.

### How the module replicates NIM's auto-select logic

Since we run on CPU with no GPU, we cannot call `nvidia-smi`. Instead, the
`model-profile-cache.yml` buildspec derives the equivalent information from the
Terraform-provided `INSTANCE_TYPE` environment variable:

```bash
# Instance type → GPU count (mirrors NIM's GPU count detection)
case "${INSTANCE_TYPE:-}" in
  g5.48xlarge|g6e.48xlarge|p5.48xlarge) GPU_COUNT=8 ;;
  g6e.12xlarge|g6e.24xlarge|p3.8xlarge) GPU_COUNT=4 ;;
  *) GPU_COUNT=1 ;;
esac

# Instance type → GPU name (as it appears in TRT profile names)
case "${INSTANCE_TYPE:-}" in
  g5.*)  GPU_NAME="a10g" ;;
  g6e.*) GPU_NAME="l40s" ;;
  g6.*)  GPU_NAME="l4"   ;;
  p5.*)  GPU_NAME="h100" ;;
esac

# Run list-model-profiles (CPU-only — no GPU required)
RAW_PROFILES=$(docker run --rm -e NGC_API_KEY="$NGC_API_KEY" "$NIM_IMAGE" list-model-profiles)

# Parse "HASH NAME" pairs — handles both known output formats:
#   Old (e.g. llama 1.8.3):     "  <hash>: <name>"
#   New (e.g. nemotron 2.0.2):  "    - <hash> (<name>) [requires ...]"
# download-to-cache requires the SHA hash in newer NIMs; older NIMs accept the name.
PROFILE_PAIRS=$(echo "$RAW_PROFILES" | sed -E -n \
  -e 's/.*- ([a-f0-9]{40,}) \(([^)]+)\).*/\1 \2/p' \
  -e 's/.*([a-f0-9]{40,}): ([^ ]+).*/\1 \2/p')

ALL_PROFILES=$(echo "$PROFILE_PAIRS" | awk '{print $2}' | \
  grep -E '(tensorrt_llm|vllm|sglang).*tp[0-9]' | sort -u)

# Priority: TRT + GPU name + tp{N} + bf16 > vLLM + tp{N} + bf16 > tp1 fallback
SELECTED_PROFILE=$(echo "$ALL_PROFILES" | grep "tensorrt_llm-${GPU_NAME}-" | grep "tp${GPU_COUNT}" | grep "bf16" | head -1)

# Look up hash for the selected name — newer NIMs require the hash, not the name
SELECTED_HASH=$(echo "$PROFILE_PAIRS" | awk -v n="$SELECTED_PROFILE" '$2==n{print $1;exit}')
[ -z "$SELECTED_HASH" ] && SELECTED_HASH="$SELECTED_PROFILE"  # fallback: older NIMs accept name

download-to-cache -p "$SELECTED_HASH"
```

This produces the same result as NIM's native auto-detection — the correct profile for
the target GPU architecture and tp count — without requiring GPU hardware in the build
environment.

When `MODEL_PROFILE` is set (non-empty), the buildspec treats it as a prefix and resolves
it to a full profile name via `list-model-profiles` output rather than running the full
auto-select logic. This lets users specify a short prefix (`vllm-bf16-tp1`) without
knowing the full versioned name.

### NIM version compatibility

Three undocumented behavioral differences have been observed across NIM versions, all
without deprecation notices. All three are handled transparently by the module.

| Behavior | Older NIMs (e.g. llama-3.1-8b-instruct 1.8.3) | Newer NIMs (e.g. nemotron-3-nano 2.0.2+) |
|---|---|---|
| `list-model-profiles` output format | `<hash>: <name>` | `    - <hash> (<name>) [requires ...]` |
| `download-to-cache -p` accepts | Human-readable name (`vllm-bf16-tp1`) | SHA hash only (`81f09463...`) |
| Container entrypoint | Ships `/opt/nvidia/nvidia_entrypoint.sh` | Script absent; NIM command runs directly |

**Why we always pass the hash:** Old NIMs accept either name or hash; new NIMs only accept
the hash. Passing the hash is universally correct. The `PROFILE_PAIRS` sed block extracts
`HASH NAME` pairs from both output formats, selection logic works on the human-readable
name, and the hash is looked up before calling `download-to-cache`.

**How `model_profile` user input works with this:** When a user sets
`model_profile = "vllm-bf16-tp4"`, the buildspec:
1. Greps `ALL_PROFILES` (names only) for that prefix → resolves to the full name (e.g. `vllm-bf16-tp4-pp1-22.0`)
2. Looks up the SHA hash for that name in `PROFILE_PAIRS`
3. Passes the hash to `download-to-cache`

Users always supply human-readable name prefixes. The hash lookup is transparent.

**If a new NIM fails** with `Unknown profiles provided: {'some-name'}`:
1. Run the build with `debug = true` — this prints `PROFILE_PAIRS` and `ALL_PROFILES` to
   the CodeBuild log, showing both hashes and names as parsed.
2. Check whether `list-model-profiles` output matches either known format.
3. If it's a new third format, add a sed pattern to the `PROFILE_PAIRS` block in
   `buildspecs/model-profile-cache.yml` and document it here.

The buildspec emits `WARN: no hash found for '...'` when the hash lookup falls back to
the name — this is the signal that the format may have changed.

**If a new NIM fails at container startup** with `entrypoint not found` or equivalent:
Check `shim/launch.sh` — it falls back to running `ORIGINAL_CMD` directly when the
entrypoint script is absent. If a future NIM ships a different entrypoint path, update
`shim_config.nim_entrypoint` in the module call or make it per-endpoint.

### Terraform Actions orchestration

Each caching-enabled `(source_image_uri, instance_type)` combo gets its own `terraform_data`
trigger keyed by `local.cache_map`. When the combo's config changes, only that project re-runs:

```hcl
resource "terraform_data" "build_trigger_model_profile_cache" {
  for_each = local.cache_map  # one entry per URI × instance_type combo

  input = jsonencode({
    config        = each.value
    rebuild_token = each.value.force_rebuild ? timestamp() : "stable"
  })

  lifecycle {
    action_trigger {
      events  = [before_create, before_update]
      actions = [action.aws_codebuild_start_build.model_profile_cache[each.key]]
    }
  }
}

resource "aws_sagemaker_model" "nim" {
  depends_on = [
    terraform_data.build_trigger_shim,
    terraform_data.build_trigger_model_profile_cache,
  ]
  # ...
}
```

When a caching-enabled endpoint's `source_image_uri`, `instance_type`, or `model_profile`
changes, its `cache_map` entry changes, the trigger input changes, and Terraform re-runs only
that profile download before recreating the endpoint. Other endpoints are unaffected.

---

## Open Weight Inference Path

The module supports two fundamentally different deployment paths, selected per-endpoint by
which field is set:

| Field set | Path | Framework | Image source |
|-----------|------|-----------|--------------|
| `source_image_uri` | NIM | NVIDIA NIM runtime | `nvcr.io` or ECR |
| `model_id` | Open weight | vLLM (default) | `vllm/vllm-openai:latest` |

Everything in `locals.tf`, `codebuild.tf`, and `main.tf` branches on this split:
`local.nim_endpoints` and `local.open_weight_endpoints` are the filtered maps that gate
each downstream resource.

### NIM Profile Cache vs vLLM Recipe

These are the two startup-optimization mechanisms in the module. They are mutually exclusive
by path and work in completely different ways.

**NIM Profile Cache** (`enable_model_profile_cache = true`, NIM path only)

A NIM profile is a pre-compiled, pre-quantized model artifact — a TRT-LLM engine built for
a specific GPU architecture, tensor parallelism count, and precision. It is produced by
NVIDIA during NIM release and stored in NGC. At NIM startup, the container selects the best
matching profile for the current GPU, downloads it from NGC, and starts the inference server.

The module pre-downloads this profile to S3 before the endpoint starts. The CodeBuild
`model-profile-cache` project runs `list-model-profiles` and `download-to-cache` on a CPU
instance (no GPU needed for these commands), then uploads the result to S3. At container
startup, `launch.sh` syncs from S3 into `/opt/nim/.cache`. NIM finds the profile already
present and skips the NGC download.

Key properties:
- Applies only to NIM containers from `nvcr.io`
- TRT-LLM profiles are GPU-architecture-specific — an L40S profile won't load on H100
- Cuts startup from ~5-10 min (NGC download) to ~2-5 min (S3 sync)
- The artifact is a compiled engine; it cannot be reused across different hardware

**vLLM Recipe** (`enable_vllm_recipe = true`, open-weight path only)

A vLLM recipe is a JSON file at `https://recipes.vllm.ai/<org>/<repo>.json` maintained by
the vLLM community. It contains recommended CLI flags for `vllm serve` for a specific model —
things like `--tensor-parallel-size`, `--max-model-len`, `--enable-chunked-prefill`. These
are not compiled artifacts; they are configuration suggestions based on benchmarking.

The `weight-fetch` CodeBuild project fetches the recipe JSON and writes per-precision env
files to S3 alongside the model weights (`_recipe_{precision}.env`). At container startup,
`launch.sh` downloads and `source`s this file, which exports `RECIPE_BASE_ARGS` and
`RECIPE_EXTRA_ARGS`. These are prepended to the final `vllm serve` command before any
user-provided `extra_args` (user always wins).

Key properties:
- Applies only to open-weight models from HuggingFace (`model_source = "huggingface"`)
- No recipe is available for NGC models (`model_source = "ngc"`)
- Not a compiled artifact — just CLI flags. Works on any GPU architecture
- `vllm_precision` (default `"default"`) selects which variant's extra_args to use
- If no recipe exists for the model, `weight-fetch` logs a warning and the endpoint still
  deploys using vLLM defaults — non-fatal

**Precision key mismatch bug:** The recipe fetch writes files named by the precision keys in
the recipe JSON (e.g. `_recipe_bf16.env`, `_recipe_fp8.env`). If the recipe doesn't have a
`"default"` variant, `_recipe_default.env` is never written. `launch.sh` then logs
`"No recipe env at ... — using vLLM defaults"` and proceeds without recipe flags. To
diagnose: check the weight-fetch CodeBuild logs for `"Recipe written:"` lines — they show
which precision keys were found. Set `vllm_precision` to match an available key.

**Comparison table:**

| | NIM Profile Cache | vLLM Recipe |
|---|---|---|
| Path | NIM (`source_image_uri`) | Open weight (`model_id`) |
| Source | NGC (NVIDIA) | recipes.vllm.ai (community) |
| Content | Pre-compiled TRT-LLM engine | CLI flags for `vllm serve` |
| GPU-specific | Yes — one profile per GPU arch + tp | No — flags work on any GPU |
| S3 storage | `nim-cache/<canonical>/<instance-type>/` | `open-weights/.../_recipe_{precision}.env` |
| Startup effect | Skips NGC download; loads cached engine | Injects optimized flags into vLLM command |
| Fallback | Endpoint fails if profile not cached | Endpoint still deploys with vLLM defaults |
| Variable | `enable_model_profile_cache = true` | `enable_vllm_recipe = true` |

### Open weight CodeBuild flow

```
model_id + model_source
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  CodeBuild — weight-fetch                            │
│  Buildspec: buildspecs/weight-fetch.yml              │
│  One project per unique (model_source, model_id,    │
│  model_revision) combo                               │
│                                                      │
│  Idempotent: skips if S3 _COMPLETE marker present   │
│                                                      │
│  HF path:  hf download → /tmp/weights               │
│  NGC path: ngc registry model download-version      │
│  → aws s3 sync → s3://{model-assets}/{prefix}/      │
│  → echo -n | aws s3 cp - .../_COMPLETE              │
│                                                      │
│  If enable_vllm_recipe = true (HF only):            │
│  curl recipes.vllm.ai/<org>/<repo>.json             │
│  → write _recipe_{precision}.env per variant        │
└──────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  CodeBuild — shim (open weight variant)              │
│  One project per unique framework ("ow--vllm")       │
│  Shared across all vLLM endpoints                   │
│                                                      │
│  FROM vllm/vllm-openai:latest                       │
│  + AWS CLI + Caddy + launch.sh + caddy-config.json  │
│  → ECR:vllm-open-weight-shim                        │
└──────────────────────────────────────────────────────┘
       │
       ▼
SageMaker container startup (launch.sh):
  1. aws s3 sync OPEN_WEIGHTS_S3_URI → /opt/ml/model
  2. aws s3 cp RECIPE_ENV_S3_URI → source it
  3. Final cmd: NIM_CMD + RECIPE_BASE_ARGS + RECIPE_EXTRA_ARGS + VLLM_USER_ARGS
  4. Caddy on :8080 (routes /invocations → /v1/chat/completions, /ping → /health)
  5. vllm serve /opt/ml/model ...
```

### S3 bucket used by open weight path

`model_assets` (`{prefix}-model-assets-{hex}`) — intentionally does NOT contain "sagemaker"
in the name. This bucket is platform-neutral (SageMaker today, EKS later, potentially other
platforms). `AmazonSageMakerFullAccess` requires "sagemaker" in the bucket name to grant S3
access — since this bucket doesn't have it, `iam.tf` adds explicit `s3:GetObject` and
`s3:ListBucket` grants to the SageMaker execution role when open-weight endpoints are
configured.

### Shim: SageMaker-only and what it actually does

The shim is present for ALL SageMaker endpoints — both NIM and open-weight. It is not used
by EKS.

SageMaker requires every container to expose:
- `POST /invocations` — inference request endpoint
- `GET /ping` — health check

Neither vLLM nor NVIDIA NIM exposes these paths natively. Caddy rewrites them:
- `/invocations` → `/v1/chat/completions`
- `/ping` → `NIM_HEALTH_PATH` (NIM: `/v1/health/ready`, vLLM: `/health`)

The health path varies by framework and is set via `NIM_HEALTH_PATH` env var in the
SageMaker model definition (`main.tf`), not baked into the image. This is why one
`caddy-config.json` template works for both paths.

**What `shim_config` controls (NIM path):** The per-endpoint `shim_config` block and the
module-level `var.shim_config` control the Caddy backend port, the NIM entrypoint script
path, and the NIM start command — all baked into the shim image at build time via
`--build-arg`. A per-endpoint block takes priority over the module-level default.

**Open-weight shim build:** The open-weight shim entry in `shim_map` is framework-level
(`"ow--vllm"` key), not per-endpoint. All vLLM open-weight endpoints share one shim image.
Per-endpoint `shim_config` is not consulted because the shim image is shared — endpoint-
specific customization (start command, health path) happens at runtime via SageMaker model
definition env vars (`NIM_CMD`, `NIM_HEALTH_PATH`, `VLLM_USER_ARGS`), not at build time.

**What launch.sh does vs what Caddy does:** These are two separate concerns mixed in the
same container:
1. **Caddy (SageMaker-specific, permanent):** Protocol adaptation. Routes SageMaker's
   required paths to the framework's actual paths. Required for any SageMaker deployment
   regardless of model type.
2. **launch.sh S3 sync (SageMaker-specific today):** Downloads model weights or NIM profiles
   from S3 before the framework starts. SageMaker has no init container mechanism — this
   logic lives in launch.sh because it's the only place it can run. For EKS, this concern
   is handled by a Kubernetes init container or S3 CSI driver instead.

---

## Design Decisions

### S3 source for CodeBuild (no git clone)

`archives.tf` zips `shim/` and uploads it to S3. CodeBuild pulls it as an S3 source rather than cloning the repo. This eliminates git credentials from the CodeBuild IAM role entirely — ECR auth uses IAM, shim source comes from S3.

The `archive_file` data source runs on every plan and its `output_md5` is the canonical change-detection signal. When any file in `shim/` changes, `output_md5` changes, which flows into the `terraform_data` trigger inputs in `codebuild.tf`, causing the build to re-run.

### ECR-Always (no pull-through cache)

Every `source_image_uri` — NGC or ECR — lands in the module-managed ECR repository before
SageMaker or EKS touches it. Base-sync CodeBuild handles the push.

**Why not pull-through cache?**
- ECR pull-through cache repos cannot pre-exist before Terraform creates them, and Terraform
  cannot delete them cleanly (the repo has to be empty).
- Eventual consistency: the first pull can take minutes before the cache warms.
- Pull-through cache rules are per-account/region — collides with other users of the same account.
- Direct push is explicit, observable, and fully Terraform-managed.

### Map-of-objects gating pattern

Each platform is controlled by a typed `map(object({...}))` variable (`sagemaker_endpoints`,
`eks_clusters`, `eks_deployments`). An empty map (`{}`) means the platform is not deployed.
Resources are gated with `for_each` — an empty map produces zero resources with no extra guards.

This pattern avoids a sprawl of boolean feature flags. Adding a platform never breaks the
existing interface. Adding optional fields to a platform's object type is non-breaking.

### No provider block in the module

AWS provider v6 added per-resource `region` attribute. Every resource in this module sets
`region = var.region` instead of using a provider alias. This lets consumers pass a
single default provider configuration and override the region per-instantiation without
provider alias juggling.

### Input validation: `variable validation` vs `lifecycle.precondition`

Two mechanisms enforce constraints on inputs. They are not interchangeable.

**`variable validation` blocks** — same-variable field relationships only.

The condition expression may only reference the variable being declared (`var.<this_variable>`).
It cannot reference any other variable, local, data source, or resource. All fields of a
`map(object(...))` variable are part of the same value, so a `for` expression over map entries
can freely compare fields within each entry:

```hcl
# OK — source_image_uri and extra_args are both fields of the same sagemaker_endpoints entry
validation {
  condition = alltrue([
    for k, v in var.sagemaker_endpoints :
    v.source_image_uri == null || length(v.extra_args) == 0
  ])
}
```

Use this for: XOR between fields on the same entry, enum checks, NIM-only / open-weight-only
field guards, format constraints.

**`lifecycle.precondition` on `terraform_data.validation`** — cross-variable constraints.

`precondition` blocks can reference any resolved value: other variables, locals, data sources.
The check runs at plan time, after all variables are resolved. This module places these on a
dedicated `terraform_data.validation` resource in `main.tf` with no other side effects.

```hcl
# OK — comparing var.hf_credentials against entries in var.sagemaker_endpoints
resource "terraform_data" "validation" {
  lifecycle {
    precondition {
      condition = var.hf_credentials != null || !anytrue([
        for v in var.sagemaker_endpoints : v.model_source == "huggingface"
      ])
      error_message = "hf_credentials required when any endpoint uses model_source = \"huggingface\"."
    }
  }
}
```

Use this for: constraints that span two or more separate variables (e.g. credentials variable
vs endpoint entries variable).

**Decision rule:** if the constraint only touches fields within one variable → `validation`
block. If it compares two different variables → `precondition` on `terraform_data.validation`.

### `try()` for count-gated outputs

When a resource has `count = condition ? 1 : 0`, accessing `resource.name[0].attr` in a
ternary expression fails at plan time when `count = 0` — Terraform evaluates both branches.
Use `try(resource.name[0].attr, null)` in outputs instead.

### S3 bucket name must contain "sagemaker"

`AmazonSageMakerFullAccess` restricts S3 access to buckets whose names match `*sagemaker*`.
The bucket is named `sagemaker-nim-${name}-${environment}-${random_id.suffix.hex}`.

### Random suffix for S3 uniqueness

`random_id.suffix` (4-byte hex = 8 chars) replaces the old `s3_bucket_suffix` variable.
Stored in Terraform state — stable across applies, changes only on `taint` or destroy.

### Random suffix for SageMaker endpoint names

`random_id.endpoint_suffix` (4-byte hex = 8 chars) is appended to auto-generated endpoint
names: `{name_prefix}-{key}-{hex}`. This solves a documented race condition in the Terraform
AWS provider ([#40080](https://github.com/hashicorp/terraform-provider-aws/issues/40080)):

`DeleteEndpoint` returns HTTP 200 immediately, but SageMaker continues cleanup asynchronously.
While the endpoint is in `Deleting` state the name is still reserved. If Terraform immediately
tries to create a new endpoint with the same name (destroy + apply, or a failed apply retry),
SageMaker returns `ValidationException 400: Cannot create already existing endpoint`.

The random suffix ensures every new endpoint gets a unique name, so destroy + apply never
collides with an in-flight deletion. The suffix is stable across normal applies (stored in
Terraform state) — it only changes when the `random_id` resource is destroyed (i.e. on a
full `terraform destroy` followed by `terraform apply`, which is exactly when you want a
new name).

**`-replace` caveat:** When replacing an endpoint manually, you must also replace the
`random_id.endpoint_suffix` for that key. Without it, the new endpoint gets the same name as
the old one. Terraform issues `DeleteEndpoint` on the old resource, but SageMaker deletion is
async — the name is held in `Deleting` state for several minutes. Terraform then immediately
calls `CreateEndpoint` with the same name and hits `ValidationException: Cannot create already
existing endpoint`. Always run:

```bash
terraform apply \
  -replace='module.nim.random_id.endpoint_suffix["<key>"]' \
  -replace='module.nim.aws_sagemaker_endpoint_configuration.nim["<key>"]' \
  -replace='module.nim.aws_sagemaker_endpoint.nim["<key>"]'
```

**Failure modes and "already exists" risk — not all failures are equal:**

Two distinct failure types have different recovery implications.

`ResourceLimitExceeded` (quota=0): fails **synchronously** on the `CreateEndpoint` API call.
SageMaker never registers the endpoint name. The next `terraform apply` is safe — no stale
state, no `-replace` needed. Fix is a Service Quotas increase; ODCR cannot help.

`InsufficientInstanceCapacity` / container startup failure: fails **asynchronously**.
`CreateEndpoint` returns immediately with the endpoint in `Creating` state — the name is
registered in AWS. The endpoint then transitions to `Failed`. Terraform tries to delete it,
the provider's delete waiter exits early, and the name is still held. The next apply hits
`Cannot create already existing endpoint`. Use `-replace` as above.

**State drift on `Failed` endpoints:** The Terraform AWS provider does not write
`aws_sagemaker_endpoint` to state when SageMaker marks it `Failed` during creation. The
endpoint exists in AWS but Terraform has no record of it. The next apply fails with
`Cannot create already existing endpoint`. Recovery: `terraform import` the endpoint into
state, then replace it as above.

If a user provides `endpoint_name` explicitly in `sagemaker_endpoints`, no suffix is added —
they own the name and the collision risk.

### SageMaker object model and Terraform resource lifecycle

Understanding this section is prerequisite to reasoning about any endpoint change.
SageMaker separates concerns across three distinct object types:

| Object | Terraform resource | Contains | Has running compute? | Create/delete time |
|---|---|---|---|---|
| **Model** | `aws_sagemaker_model` | Container image URI + environment variables | No | Instantaneous |
| **EndpointConfig** | `aws_sagemaker_endpoint_configuration` | Model name + instance type + variant settings | No | Instantaneous |
| **Endpoint** | `aws_sagemaker_endpoint` | Reference to an EndpointConfig by name | **Yes** — running EC2 instances | 5–20 min |

Model and EndpointConfig are pure metadata. They contain no compute. Creating, replacing, or deleting them is instantaneous and has no effect on serving traffic. The Endpoint is the only object with running instances.

**Immutability:** SageMaker Models and EndpointConfigs are immutable. Any attribute change (including a single environment variable) requires destroy + create. Terraform plans these as `+/-` replacements.

#### Two ways to change what an endpoint serves

**Option A — UpdateEndpoint (in-place, no downtime):**
Provide a new `EndpointConfigName`. SageMaker performs a blue-green deployment internally: spins up new instances using the new config, runs health checks, switches traffic, then terminates old instances. The endpoint ARN and name are unchanged throughout. Takes 5–15 min.

Terraform issues `UpdateEndpoint` when `aws_sagemaker_endpoint.endpoint_config_name` changes without the endpoint resource itself being replaced.

**Option B — DeleteEndpoint + CreateEndpoint (full replace, causes downtime):**
Tears down all running instances before recreating. Takes 10–20 min with a traffic gap. Only happens when `aws_sagemaker_endpoint` is replaced (e.g., via `-replace` flag or when `endpoint_name` changes).

**The goal is always Option A.** The three content-keyed `random_id` resources in this module exist specifically to trigger UpdateEndpoint rather than endpoint replacement when model content changes.

#### How content changes propagate: the three random_ids

```
random_id.endpoint_suffix          # 4 bytes — stable; unique endpoint names during async deletion
random_id.model_content_suffix     # 2 bytes — rotates when image or environment changes
random_id.endpoint_config_suffix   # 2 bytes — rotates when model_content_suffix rotates
```

**`endpoint_suffix`** is stable by design. It only gives the endpoint a unique name to avoid the async-deletion race condition (see above). It does NOT track content.

**`model_content_suffix`** has keepers tracking the model's container image and environment:

```hcl
resource "random_id" "model_content_suffix" {
  for_each    = var.sagemaker_endpoints
  byte_length = 2
  keepers = {
    image       = "...ecr.../vllm-open-weight-shim"
    environment = jsonencode({ NIM_CMD = "vllm serve ... --served-model-name llama", ... })
  }
}
```

When `NIM_CMD` changes (or any env var, or the container image), keepers change → `random_id` generates a new hex → the SageMaker Model gets a **new name**:

```
Before:  nim-testing-dev-llama-8b-e5f6    (model_content_suffix hex = e5f6)
After:   nim-testing-dev-llama-8b-g7h8    (model_content_suffix hex = g7h8)
```

**`endpoint_config_suffix`** has a single keeper — the model suffix hex:

```hcl
resource "random_id" "endpoint_config_suffix" {
  for_each    = var.sagemaker_endpoints
  byte_length = 2
  keepers     = { model_suffix = random_id.model_content_suffix[each.key].hex }
}
```

When `model_content_suffix` rotates, `endpoint_config_suffix` also rotates → the EndpointConfig gets a new name → Terraform detects `endpoint_config_name` changed on `aws_sagemaker_endpoint` → issues `UpdateEndpoint`.

**On a stable apply (no content changes), both random_ids produce the same hex as before. Zero resources change.**

#### Why `create_before_destroy` is required on both Model and EndpointConfig

`UpdateEndpoint` requires the endpoint's **current** EndpointConfig to still exist at the moment the call is made. SageMaker uses it during the blue-green transition for rollback capability. If the old config is deleted first, SageMaker returns:

```
ValidationException: Could not find endpoint configuration "<old-config-name>"
```

`create_before_destroy = true` on `aws_sagemaker_endpoint_configuration` ensures the new config exists before the old one is deleted:

```
1. CREATE new EndpointConfig  ...-g7h8-cfg    (old ...-e5f6-cfg still alive)
2. UpdateEndpoint              endpoint uses ...-g7h8-cfg  ← SageMaker finds both configs ✓
3. DELETE old EndpointConfig  ...-e5f6-cfg
```

**`create_before_destroy` propagates upstream through the dependency graph.** The EndpointConfig depends on the Model (references it by name), so when the EndpointConfig has `create_before_destroy`, Terraform also tries to create the new Model before destroying the old one. If the Model name were stable (same name on replacement), this would hit:

```
ValidationException: Cannot create already existing model "<name>"
```

This is why the Model name must also change when content changes (`model_content_suffix`). With a new name, `create_before_destroy` on the Model creates `nim-...-g7h8` while `nim-...-e5f6` still exists — no collision.

#### Full apply sequence when model content changes

```
User changes extra_args: {} → { dtype = "bfloat16" }

Plan:
  model_content_suffix    e5f6 → g7h8  (env changed)
  endpoint_config_suffix  a1b2 → c3d4  (model_suffix changed)
  aws_sagemaker_model.open_weight["llama-8b"]             +/- (new name g7h8)
  aws_sagemaker_endpoint_configuration.nim["llama-8b"]    +/- (new name c3d4)
  aws_sagemaker_endpoint.nim["llama-8b"]                  ~   (endpoint_config_name changed)

Apply order (create_before_destroy):
  1. CREATE  model nim-testing-dev-llama-8b-g7h8             ← new name, no collision
  2. CREATE  config nim-testing-dev-llama-8b-8a0a22d8-c3d4-cfg  ← references new model
  3. ~       endpoint_config_name: ...-a1b2-cfg → ...-c3d4-cfg
             SageMaker UpdateEndpoint: blue-green deploy, no downtime
  4. DELETE  config nim-testing-dev-llama-8b-8a0a22d8-a1b2-cfg
  5. DELETE  model nim-testing-dev-llama-8b-e5f6

Endpoint ARN/name: unchanged throughout.
```

#### What stays stable vs what rotates

| Resource | Name includes | Stable across normal applies? | Changes when |
|---|---|---|---|
| `aws_sagemaker_endpoint` | `endpoint_suffix` | Yes | `-replace` or explicit destroy |
| `aws_sagemaker_model` | `model_content_suffix` | Yes | Image or environment changes |
| `aws_sagemaker_endpoint_configuration` | `endpoint_suffix` + `endpoint_config_suffix` | Yes | Model content changes |
| `aws_cloudwatch_log_group` | `endpoint_suffix` | Yes — follows endpoint name | Endpoint replaced |

### Pre-created CloudWatch log groups

SageMaker always writes endpoint logs to `/aws/sagemaker/Endpoints/{endpoint-name}`. If this
log group does not exist, SageMaker creates it automatically — but without a retention policy,
and without Terraform owning the lifecycle. This means `terraform destroy` leaves the log group
behind, and retention defaults to "Never expire."

The module pre-creates each endpoint's log group via `aws_cloudwatch_log_group.sagemaker_endpoint`
before the SageMaker model is deployed. Pre-creating the group with the exact name SageMaker
would use intercepts it — SageMaker writes to the existing group rather than creating a new one.
This gives Terraform ownership of the retention policy (`var.log_retention_days`, default 30 days).

**Multiple log streams per endpoint:** Each EC2 instance backing the endpoint gets its own
stream (`AllTraffic/{instance-id}`). After a replace or failure+redeploy, the old instance's
stream persists alongside the new one — this is expected. Logs from "deleted" endpoints also
persist because SageMaker never deletes log groups. The pre-created group with `retention_in_days`
ensures they expire automatically.

**Import on first apply:** If an endpoint already exists (e.g. created before the module was
first applied), import its log group before applying to avoid a name collision:

```bash
terraform import \
  'module.nim.aws_cloudwatch_log_group.sagemaker_endpoint["<key>"]' \
  /aws/sagemaker/Endpoints/<endpoint-name>
```

### Secrets: direct value XOR Secrets Manager ARN

Each credential (`ngc_credentials`, `hf_credentials`) accepts either `api_key`/`token`
(plaintext) or `secret_arn` (Secrets Manager ARN) — never both. The module reads the
secret via `data "aws_secretsmanager_secret_version"` (count-gated on the ARN field).
It does not create secrets.

---

## SageMaker Shim (Temporary)

SageMaker requires containers to expose:
- `GET /ping` → 200 when healthy
- `POST /invocations` → inference response

NIMs expose:
- `GET /v1/health/ready`
- `POST /v1/chat/completions`

The `shim/` directory contains a **Caddy reverse proxy** that adapts the NIM API to SageMaker's
protocol, plus the NIM startup wrapper (`launch.sh`).

### Shim files

| File | Purpose |
|------|---------|
| `shim/Dockerfile` | Generic, ARG-driven. Build-args: `NIM_CMD`, `NIM_ENTRYPOINT`, `CADDY_BACKEND_PORT` (empty = auto-detect from `NIM_HTTP_API_PORT` at runtime), `CUDA_DRIVER_LABEL` |
| `shim/caddy-config.json` | Caddy config. Maps `/invocations*` → `/v1/chat/completions`, `/ping*` → `${HEALTH_PATH}` (framework-specific: NIM = `/v1/health/ready`, vLLM = `/health`). Template variables substituted by `launch.sh` via sed before passing to Caddy. |
| `shim/launch.sh` | Starts NIM + Caddy. Syncs `MODEL_PROFILE_CACHE` from S3 at startup. Monitors NIM process — if NIM exits, kills Caddy immediately (prevents SageMaker startup timeout on failure) |
| `shim/asset-build.sh` | **Future PR** — custom NIM build (HF → ONNX → TRT). Not included in the shim Docker image. Alpamayo-specific. See file header for re-enable steps. |

### CUDA driver label

```dockerfile
LABEL com.amazonaws.sagemaker.inference.cuda.verified_versions=<cuda_version>
```

SageMaker reads this label to auto-select the inference AMI (driver version). Set via
`shim_config.cuda_driver_label`. Leave null for the SageMaker default AMI selection.

**Known AMI issues:**
- `al2023-ami-sagemaker-inference-gpu-4-1` (580.x driver, CUDA 13.0) — confirmed buggy by
  internal team member. Status unknown. Do not rely on explicit AMI 4-1 until re-verified.
- `al2023-ami-sagemaker-inference-gpu-3-1` (550.x driver) — insufficient for CUDA 13.0 container.
- Current working config: g6e, no CUDA label, SageMaker default AMI → driver >= 580.95 auto-selected.

### Removal checklist (when NVIDIA ships native SageMaker support)

When native SageMaker support is available, remove:
- `shim/` directory
- `shim_config` variable (mark `deprecated` first, then remove)
- CodeBuild #2 (shim project) from `codebuild.tf`
- `archives.tf` (shim source zip upload)

---

## Alpamayo-Specific Notes

Alpamayo is a custom NIM (HuggingFace weights → ONNX → TRT engines at build time).
It is not yet on NGC and does not use the standard model profile cache path.

The custom build path (`asset-build.sh`, GPU CodeBuild fleet, `enable_asset_build`) is
implemented but commented out pending a dedicated Future PR. Standard NGC NIMs (the primary
supported use case) use the `enable_model_profile_cache` path instead.

### Bootstrap (until Alpamayo is on NGC)

Alpamayo's base image comes from a Google Drive tarball (not yet on NGC). Manual bootstrap:

```bash
# 1. Download alpamayo-nim-<version>.tgz from Google Drive (file ID: TBD — see Q2)
gdown "https://drive.google.com/uc?id=<FILE_ID>" -O alpamayo-nim.tgz

# 2. Push to ECR (create ECR repo first via partial apply if needed)
docker load -i alpamayo-nim.tgz
REGION=us-east-1
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
ECR="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/alpamayo"
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR
docker tag alpamayo-nim:<version> ${ECR}:<version>
docker push ${ECR}:<version>

# 3. Use the ECR URI as source_image_uri with sync_to_ecr = false
# source_image_uri = "${ECR}:<version>"
# sync_to_ecr      = false
```

Once Alpamayo is on NGC, use the `nvcr.io/nim/nvidia/alpamayo-*` URI directly.

### Custom build path (Future PR)

The custom build pipeline is in `shim/asset-build.sh` (HF → ONNX → TRT) and
`buildspecs/asset-build.yml`. The corresponding CodeBuild fleet and project in `codebuild.tf`
are commented out. Re-enable by:

1. Uncommenting asset-build resources in `codebuild.tf`
2. Adding `asset-build.sh` back to `shim/Dockerfile` COPY + chmod
3. Setting `enable_asset_build = true` in the module call

### g5 Re-test Plan

g5 (A10G, SM86) was previously ruled out for SageMaker due to TRT build timeout (>3600s startup).
With model profile pre-caching, the timeout constraint no longer applies — the profile
is downloaded to S3 before the endpoint starts.

**Test sequence:**

1. **g6e baseline** — confirm ODCR wiring end-to-end on known-working instance. Run before
   touching g5.

2. **g5 + `cuda_driver_label = "13.0"`** — test CUDA label for auto-AMI-selection:
   - SageMaker should select a 580.x driver AMI without explicit `inference_ami_version`
   - Risk: may select AMI 4-1 (confirmed buggy) — verify if fixed

3. **g5 + `enable_model_profile_cache = true`** — full S3 cache flow:
   - CPU CodeBuild selects and downloads A10G profile to S3
   - SageMaker g5 endpoint syncs from S3 → ~2-5 min startup
   - Use `container_startup_timeout = 600`

**Open before starting:**
- Is AMI 4-1 bug fixed? Check with coworker who confirmed it.

---

## EKS

EKS support is fully implemented via `modules/eks-infra/` (cluster + Karpenter NodePool) and
`modules/eks-app/` (NIM deploy via Helm, open-weight deploy via kubectl, both triggered by
CodeBuild action). Both modules are wired in the root `main.tf` and exercised by
`examples/eks/nim/` and `examples/eks/open-weight/`.

### Why EKS does not need the shim

The SageMaker shim (`ECR:shim`) exists for two SageMaker-specific constraints:

1. **Port bridging** — SageMaker probes port 8080; NIM listens on 8000. Caddy is the only
   available mechanism because SageMaker gives you one container with one entrypoint.
2. **Process supervision** — `launch.sh` monitors the NIM PID and kills Caddy immediately when
   NIM exits, so SageMaker marks the endpoint `Failed` instead of waiting the full startup timeout.

**Neither constraint applies to EKS.** Kubernetes Service port mapping handles 8080→8000 natively.
Kubernetes liveness/readiness probes replace the PID-monitoring wrapper. **The NIM base image
(`ECR:base`) runs unmodified on EKS** — no Caddy, no `launch.sh`, no Dockerfile modifications.

### Auto Mode node visibility

EKS Auto Mode nodes are **not** visible in the EC2 console like regular instances. They appear only in:

- **EKS console → Clusters → \<name\> → Compute → Nodes** (status shows "Managed")
- `kubectl get nodes` — the node name is the raw EC2 instance ID (e.g. `i-059b03915c9f5037d`)

The OS is **Bottlerocket (EKS Auto, Nvidia)** — an AWS-supplied AMI pre-configured with:
- NVIDIA GPU drivers version-matched to the instance family
- NVIDIA container toolkit and device plugin
- containerd runtime

No GPU Operator, Network Operator, or manual driver installation is required or supported. Adding them to an Auto Mode cluster conflicts with the pre-installed drivers.

### Why GPU Operator and Network Operator are NOT needed

EKS Auto Mode provisions managed nodes using AWS-supplied AL2023 GPU AMIs. These AMIs ship with:

- NVIDIA GPU drivers pre-installed and version-matched to the instance family
- The NVIDIA container toolkit (device plugin)
- NVIDIA device plugin for Kubernetes (auto-configured by Auto Mode)

There is nothing to install. The GPU Operator and Network Operator are only required when
self-managing nodes (e.g. self-managed Karpenter or managed node groups with a base AMI that
does not include drivers). Do not add them to Auto Mode clusters — they conflict with the
pre-installed drivers.

### EKS Auto Mode: IAM requirements

Auto Mode needs more IAM permissions than a standard EKS cluster because AWS manages node
provisioning (Karpenter), load balancers (ALB/NLB controller), block storage (EBS CSI), and
networking (VPC CNI) on your behalf.

**Cluster role policies (all five required):**

| Policy | Purpose |
|--------|---------|
| `AmazonEKSClusterPolicy` | Core cluster management |
| `AmazonEKSComputePolicy` | Karpenter node provisioning |
| `AmazonEKSBlockStoragePolicy` | EBS CSI driver |
| `AmazonEKSLoadBalancingPolicy` | AWS Load Balancer controller |
| `AmazonEKSNetworkingPolicy` | VPC CNI plugin |

The cluster assume-role policy must also include `sts:TagSession` for Auto Mode session tagging.

**Node role policies:**

| Policy | Purpose |
|--------|---------|
| `AmazonEKSWorkerNodeMinimalPolicy` | Minimal permissions for Auto Mode nodes |
| `AmazonEKSWorkerNodePolicy` | Standard node permissions |
| `AmazonEC2ContainerRegistryPullOnly` | ECR pull (read-only) |
| `AmazonEC2ContainerRegistryReadOnly` | ECR describe/list |
| `AmazonEKS_CNI_Policy` | VPC CNI networking |

Both roles and all attachments are in `modules/eks-infra/iam.tf`.

### Karpenter NodePool: EKS Auto Mode vs self-managed

EKS Auto Mode uses a different Karpenter CRD API than self-managed Karpenter installs.

| | EKS Auto Mode | Self-managed Karpenter |
|---|---|---|
| NodeClass CRD | `nodeclasses.eks.amazonaws.com/v1` | `ec2nodeclasses.karpenter.k8s.aws/v1` |
| Default NodeClass | `default` (auto-created by AWS) | Must create manually |
| nodeClassRef group | `eks.amazonaws.com` | `karpenter.k8s.aws` |
| nodeClassRef kind | `NodeClass` | `EC2NodeClass` |

The module uses the Auto Mode API. Do NOT wait for `ec2nodeclasses.karpenter.k8s.aws` CRDs —
they do not exist in Auto Mode clusters.

The `cluster-setup` CodeBuild buildspec applies a single `NodePool` manifest using the
Auto Mode API:

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: {name_prefix}-gpu
spec:
  template:
    spec:
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: default
      requirements:
        - key: node.kubernetes.io/instance-type
          operator: In
          values: ["{GPU_INSTANCE_TYPE}"]
```

### Planned: EC2 On-Demand Capacity Reservation (ODCR) support (EKS only)

EC2 ODCRs guarantee GPU instance capacity in a specific AZ. For EKS, this means the
Karpenter NodePool can be constrained to launch nodes only from a reservation, ensuring
GPU availability even when on-demand capacity is scarce.

The stub exists in `main.tf` as a commented-out `capacity_reservation_config` block on
`aws_sagemaker_endpoint_configuration` -- but that is a different mechanism (SageMaker
Training Plans, not EC2 ODCRs). EKS ODCR support would be implemented differently:
an EC2 capacity reservation ARN would be added to the NodePool's `karpenter.sh/capacity-type`
or `capacity-reservation-id` node selector so Karpenter only provisions into the reserved
capacity.

This applies to EKS only. SageMaker capacity reservations use a separate mechanism
(Training Plan ARNs -- see Q3 in Open Questions).

---

### Helm chart types and nim_type resolution

NGC organizes NIM Helm charts under different orgs and repos depending on the NIM category.
The module derives the correct chart name and repo URL from `nim_type` automatically.

| `nim_type` | Helm chart name | Repo URL |
|------------|-----------------|----------|
| `llm` (default) | `nim-llm` | `https://helm.ngc.nvidia.com/nim/charts` |
| `embedding` | `text-embedding-nim` | `https://helm.ngc.nvidia.com/nim/snowflake/charts` |
| `speech` | `riva-api` | `https://helm.ngc.nvidia.com/nvidia/riva/charts` |
| `custom` | (none — must set explicitly) | (none — must set explicitly) |

**Resolution priority:** explicit `helm_chart_name` / `helm_chart_repo_url` override > `nim_type` default.
This allows overriding individual fields without abandoning the nim_type default for the other.

`locals.tf` implements the derivation:

```hcl
locals {
  nim_chart_defaults = { llm = {...}, embedding = {...}, speech = {...} }

  eks_helm_chart_name = {
    for k, v in var.eks_deployments.nim :
    k => v.helm_chart_name != null ? v.helm_chart_name : (
      v.nim_type != "custom" ? local.nim_chart_defaults[v.nim_type].helm_chart_name : null
    )
  }
}
```

### NGC Helm chart fetch: HTTPS, not OCI

NGC Helm charts use HTTPS fetch — not OCI (`oci://helm.ngc.nvidia.com/...`).

**Two fetch sources, checked in order by the deploy buildspec:**

1. `HELM_CHART_S3_URI` set → `aws s3 cp <uri> .` (custom/internal chart)
2. `HELM_CHART_VERSION` set → `helm fetch <repo_url>/<chart>-<version>.tgz --username='$oauthtoken' --password=<NGC_API_KEY>`

If neither is set the buildspec exits with a clear error. **NGC does not expose a chart index
(`index.yaml`)**, so `helm repo add` + `helm pull` return 403 Forbidden on the index endpoint
even with valid credentials. Always pin `helm_chart_version` for NGC charts.

The downloaded `.tgz` is installed with `helm upgrade --install`.

### Custom chart S3 upload

For internal NIMs (e.g. Alpamayo) that are not on NGC, pre-package the chart and upload it
to S3 before running `terraform apply`:

```bash
helm package ./alpamayo-nim-chart/
aws s3 cp alpamayo-nim-1.0.0.tgz s3://my-bucket/charts/
```

Then set in the module call:
```hcl
nim_type          = "custom"
helm_chart_s3_uri = "s3://my-bucket/charts/alpamayo-nim-1.0.0.tgz"
```

The CodeBuild role gets `s3:GetObject` on the chart bucket automatically (dynamic IAM statement
in `modules/eks-app/iam.tf`) when `helm_chart_s3_uri` is set.

**Format:** must be a `.tgz` produced by `helm package`. Plain `.zip` archives are not supported
by `helm upgrade --install`.

### Kubernetes objects created by the deploy buildspec

The `deploy-nim.yml` buildspec creates the following objects in the target namespace before
running `helm upgrade --install`:

| Object | Name | Purpose |
|--------|------|---------|
| `Namespace` | `var.namespace` (default `nim`) | Isolates NIM resources |
| `Secret` | `ngc-api-key` | Holds the NGC API key for NIM license validation at pod startup |
| `ServiceAccount` | `nim-sa` | Annotated with the IRSA role ARN for pod-level AWS credential injection |

The NIM pod's license validation calls NVIDIA's licensing server at every startup using the NGC
API key from the `ngc-api-key` secret. This is required even when the NIM image comes from ECR
(not directly from NGC) — the image contains the NIM runtime, which must validate its license
on startup.

### IRSA (IAM Roles for Service Accounts)

IRSA gives NIM pods IAM credentials without embedding keys in the pod spec. The `nim-sa`
ServiceAccount is annotated:

```yaml
eks.amazonaws.com/role-arn: "<nim_irsa_role_arn>"
```

When a pod runs under `nim-sa`, EKS injects temporary AWS credentials via a projected token
volume. The NIM pod uses these credentials to:
- Pull the NIM image from ECR (node IAM role handles this — IRSA is for pod-level access)
- `aws s3 sync` from the nim-cache bucket (init container, when `enable_model_profile_cache = true`)

The IRSA role is created in `modules/eks-infra/iam.tf` with:
- `s3:GetObject` + `s3:ListBucket` on the nim-cache bucket (when model profile caching is used)
- Trust policy restricted to the specific ServiceAccount in the specific namespace

### Model profile cache: init container approach

The module implements model profile cache delivery via a Kubernetes init container rather than
the S3 Files CSI driver. The init container runs `aws s3 sync` from the nim-cache bucket into
a shared `emptyDir` volume before the NIM container starts.

```
init container (amazon/aws-cli):
  aws s3 sync s3://{cache_bucket}/{cache_prefix}/ {cache_path}/
  → emptyDir volume at {cache_path}

NIM container:
  reads {cache_path}/ — finds profile already present, skips NGC download
```

**Why init container vs S3 CSI driver:**

The S3 CSI driver (GA April 2025) mounts S3 as a POSIX filesystem with zero startup penalty.
However, EKS Auto Mode support for the S3 CSI add-on was not confirmed at implementation time.
The init container approach works on any Kubernetes cluster without add-on dependencies.

**Planned: S3 Files CSI support (EKS only).** When EKS Auto Mode support for the S3 CSI
add-on is confirmed, the init container sync can be replaced with a direct S3 POSIX mount
at `/opt/nim/.cache`. This eliminates the ~2-5 min startup penalty entirely. The init
container approach will remain the default for clusters without the add-on.

The init container runs under the `nim-sa` ServiceAccount so it inherits the IRSA role's S3
permissions. No credentials are embedded in the pod spec.

**Startup penalty:** `aws s3 sync` adds ~2-5 min per pod creation. Without `enable_model_profile_cache`,
NIM downloads the profile from NGC at startup (~5-10 min). The init container cuts total startup from
~5-10 min (cold) to ~2-5 min (warm S3).

### GPU resource requests and the NVIDIA device plugin

**This is the most critical EKS-specific concept in this module. Read this before touching GPU counts.**

#### Two independent layers — both must match

NIM model profiles and Kubernetes GPU resource requests are **completely separate systems** that
must agree with each other. Confusion between them is the most common source of OOM crashes on EKS.

**Layer 1: NIM model profile** — encodes the TRT-LLM engine configuration for a specific GPU
setup. A profile named `tensorrt_llm-l40s-tp4-bf16` was compiled for 4× L40S GPUs with tensor
parallelism 4 and bf16 precision. When NIM loads this profile, it expects to distribute the model
across 4 GPU devices. The profile is the contract for *how* the model runs.

**Layer 2: Kubernetes GPU resource limits** — `nvidia.com/gpu: N` in the pod spec controls how
many GPU devices the NVIDIA device plugin exposes to the container. This happens at the container
runtime level before the NIM process starts. If the limit is `1`, the container's device
namespace contains exactly 1 GPU — the other 3 are invisible, not accessible, do not exist from
the process's perspective.

**The failure mode:** NIM starts, reads its 4-GPU profile, calls CUDA to initialize tensor
parallelism across 4 devices, and crashes because only 1 GPU device was mounted into the
container. This is the OOM/CUDA error observed during testing: it is not a NIM bug or a
profile selection bug. It is a resource limit mismatch.

#### Why SageMaker never had this problem

On SageMaker, you specify `instance_type = "ml.g6e.12xlarge"` in the endpoint config. SageMaker
provisions that instance and gives the **entire instance** to the container — all 4 L40S GPUs are
exposed automatically. There is no resource limit declaration. NIM sees 4 GPUs, loads the 4-GPU
profile, runs correctly.

On EKS, the NVIDIA device plugin enforces a strict 1:1 resource request to device exposure model.
The scheduler reads `nvidia.com/gpu: N` from the pod spec and passes exactly that many device
handles to the container runtime. The device plugin has no knowledge of NIM profiles and no way
to infer the right count from the workload.

**SageMaker = whole instance, implicit.  EKS = explicit request, must match the profile.**

#### How the module resolves this

`locals.tf` maintains an `instance_gpu_count` table mapping every supported EC2 instance type
to its GPU count. At plan time, each EKS deployment's GPU count is resolved:

```
eks_gpu_count[k] =
  v.gpu_count                                             # explicit override (non-null)
  ?? instance_gpu_count[clusters[v.cluster_key].instance_type]  # auto-derived from instance
  ?? 1                                                    # unknown type fallback
```

The resolved count flows through as an env var (`GPU_COUNT`) to the CodeBuild deploy project,
which writes it into both `resources.limits.nvidia.com/gpu` and `resources.requests.nvidia.com/gpu`
in the generated Helm values. This ensures the pod always requests all GPUs available on the node,
matching whatever multi-GPU profile NIM selects.

**Users never set `gpu_count` for standard deployments.** The module derives the correct value from
the `instance_type` already declared in `eks_clusters`. Override only when intentionally limiting
GPU access (e.g. testing, or co-locating multiple NIMs on a multi-GPU node).

#### The table must stay in sync with the cache buildspec

`buildspecs/model-profile-cache.yml` has its own `instance_type → GPU_COUNT` case statement
that it uses to select the correct tensor-parallel profile during pre-caching. Both tables must
agree — if they diverge, the pre-cached profile (e.g. `tp4`) will not match the GPU count
available to the pod (e.g. `1`), and NIM will fail to load the cached profile.

When adding a new instance type, update **both**:
1. `locals.tf` → `instance_gpu_count`
2. `buildspecs/model-profile-cache.yml` → `GPU_COUNT` case statement

#### Instance GPU count reference

| Instance type | GPU | Count | VRAM total |
|---------------|-----|-------|------------|
| g5.xlarge / g5.2xlarge / g5.4xlarge / g5.8xlarge / g5.16xlarge | A10G | 1 | 24 GB |
| g5.12xlarge / g5.24xlarge | A10G | 4 | 96 GB |
| g5.48xlarge | A10G | 8 | 192 GB |
| g6e.xlarge / g6e.2xlarge / g6e.4xlarge / g6e.8xlarge | L40S | 1 | 48 GB |
| g6e.12xlarge / g6e.24xlarge | L40S | 4 | 192 GB |
| g6e.48xlarge | L40S | 8 | 384 GB |
| p3.2xlarge | V100 | 1 | 16 GB |
| p3.8xlarge | V100 | 4 | 64 GB |
| p3.16xlarge / p3dn.24xlarge | V100 | 8 | 128/256 GB |
| p4d.24xlarge | A100 40 GB | 8 | 320 GB |
| p4de.24xlarge | A100 80 GB | 8 | 640 GB |
| p5.48xlarge | H100 80 GB | 8 | 640 GB |
| p5e.48xlarge / p5en.48xlarge | H200 | 8 | 1128 GB |

### CodeBuild NodePool polling

The `cluster-setup` and `nim-deploy` CodeBuild actions trigger in parallel (the `depends_on`
between `action_trigger` resources is broken — GitHub [#37930](https://github.com/hashicorp/terraform/issues/37930),
[#37975](https://github.com/hashicorp/terraform/issues/37975)). The `nim-deploy` buildspec
polls for the NodePool in `pre_build` before proceeding:

```bash
for i in $(seq 1 40); do
  if kubectl get nodepool "${NODE_POOL_NAME}" >/dev/null 2>&1; then
    break
  fi
  sleep 30
done
```

This ensures the NodePool exists before Helm deploys — if the NIM pod were scheduled before
the NodePool, Karpenter would have no GPU node class to provision against.

### Destroy-time cleanup: LBC-created security groups and ENIs

**Why this feels wrong but is unavoidable.**

When you run `terraform destroy`, you expect Terraform to clean up everything it created. For EKS,
that expectation breaks in one specific place: the AWS Load Balancer Controller (LBC).

#### The problem

The LBC is a Kubernetes controller running inside the cluster. When you create a `LoadBalancer`
Service (which the NIM Helm chart does), the LBC calls AWS APIs directly to provision an NLB,
associated security groups, and ENIs. These AWS resources are created **by the controller, not by
Terraform**. They never appear in Terraform state. Terraform has no record that they exist.

When `terraform destroy` runs, it destroys what it knows about — the EKS cluster, the Terraform-
managed security groups, the VPC — but it has no entry to delete for the LBC-created SGs and ENIs.
Those linger in the VPC. When Terraform tries to delete the VPC, AWS returns:

```
DependencyViolation: The vpc 'vpc-xxx' has dependencies and cannot be deleted.
```

The destroy hangs indefinitely. Without intervention it never completes.

#### Why the Kubernetes-side cleanup isn't enough

`modules/eks-app/main.tf` has a `terraform_data.helm_cleanup` destroy provisioner that runs
`helm uninstall` before the cluster is deleted. This signals the LBC to delete the NLB and its
SGs. The LBC does respond — but the deletion is **asynchronous**. `helm uninstall` returns before
AWS has finished deleting the ENIs and SGs. By the time Terraform moves on to VPC deletion, those
resources may still exist.

#### Why this is a fundamental Kubernetes controller limitation

The Kubernetes controller pattern intentionally decouples infrastructure from IaC tools. Controllers
watch Kubernetes objects and reconcile AWS state directly via the AWS SDK — no CloudFormation, no
Terraform, no state files. This gives controllers fine-grained, event-driven control but means any
AWS resources they create are invisible to IaC tooling.

The same issue affects:
- EBS CSI driver (creates EBS volumes for PersistentVolumeClaims)
- ExternalDNS (creates Route53 records for Services/Ingresses)
- Cluster Autoscaler (modifies ASG desired capacity)

AWS does not currently provide a mechanism to "hand off" controller-created resources to Terraform
ownership. This is a known gap in the EKS/Terraform integration.

#### The fix: `modules/eks-infra/cleanup.tf`

A `terraform_data` destroy provisioner in `modules/eks-infra/cleanup.tf` handles this. On every
destroy it finds and deletes LBC-created resources before VPC deletion proceeds:

```
destroy order:
  1. module.eks_app destroys — helm_cleanup runs → helm uninstall → LBC starts async NLB deletion
  2. module.eks_infra destroys:
     a. terraform_data.cleanup_lbc_resources destroy provisioner runs:
        - finds SGs tagged kubernetes.io/cluster/<name>=owned (LBC ownership tag)
        - deletes dependent ENIs (SG deletion fails if ENIs are attached)
        - revokes SG ingress rules
        - deletes SGs
        - retries 20× / 15s gaps (gives LBC async deletion time to complete naturally)
     b. aws_eks_cluster.nim deleted
     c. remaining eks-infra resources deleted
  3. example VPC/subnets deleted — no orphaned resources, no DependencyViolation
```

The `depends_on = [aws_eks_cluster.nim]` on the cleanup resource is what controls ordering:
Terraform reverses dependencies on destroy, so cleanup runs **before** the cluster is deleted —
which matters because we use the cluster name as the tag filter to find the right SGs.

`on_failure = continue` ensures the destroy completes even if the cleanup script encounters
resources that are already gone (idempotent).

#### What to do if destroy hangs before this fix is applied

If a destroy gets stuck on `aws_vpc.main`:

```bash
# Find LBC-created SGs by cluster tag
aws ec2 describe-security-groups \
  --filters "Name=tag:kubernetes.io/cluster/<cluster-name>,Values=owned" \
  --query 'SecurityGroups[*].[GroupId,GroupName]' --output table

# Find all ENIs still in the VPC
aws ec2 describe-network-interfaces \
  --filters "Name=vpc-id,Values=<vpc-id>" \
  --query 'NetworkInterfaces[*].[NetworkInterfaceId,Description,Status]' --output table

# Delete ENIs first, then SGs — VPC deletion will unblock immediately
aws ec2 delete-network-interface --network-interface-id eni-xxx
aws ec2 delete-security-group --group-id sg-xxx
```

Terraform does not need to be cancelled — once the blocking resources are deleted, the in-progress
`aws_vpc.main` destruction completes on its own within seconds.

### EKS cluster log group ownership

EKS automatically creates `/aws/eks/<name>/cluster` when the cluster writes its first control-plane
log. `AmazonEKSClusterPolicy` grants the cluster role `logs:CreateLogGroup`, which means EKS can
recreate the log group at any time — including during cluster shutdown, after Terraform has already
deleted it. This produces:

```
InvalidParameterException: The specified log group already exists
```

on the next `terraform apply`.

#### The fix: deny `logs:CreateLogGroup` on the cluster role

`modules/eks-infra/iam.tf` attaches an inline DENY policy to the EKS cluster role:

```hcl
resource "aws_iam_role_policy" "eks_cluster_deny_log_group_create" {
  policy = jsonencode({
    Statement = [{ Effect = "Deny", Action = "logs:CreateLogGroup", Resource = "*" }]
  })
}
```

This gives Terraform exclusive ownership of the log group:

- **During normal operation:** Terraform pre-creates the log group before the cluster starts.
  EKS finds it already there and just writes to it — `logs:CreateLogGroup` is never called.
  The DENY never fires.
- **During destroy:** Terraform deletes the cluster first (cluster `depends_on` the log group
  → reverse on destroy). EKS tries `CreateLogGroup` during shutdown → DENY blocks it.
  Terraform then deletes the log group cleanly. No orphan, no conflict on re-apply.

This is the approach used by the `terraform-aws-eks` community module
([issue #920](https://github.com/terraform-aws-modules/terraform-aws-eks/issues/920)).

### EKS vs SageMaker: full comparison

| | SageMaker | EKS |
|---|---|---|
| Image used | `ECR:shim` (NIM + Caddy + launch.sh) | `ECR:base` (NIM, unmodified) |
| Port handling | Caddy 8080→8000 in-process proxy | Kubernetes Service port mapping |
| Model profile delivery | `aws s3 sync` in `launch.sh` at startup | `aws s3 sync` in init container |
| Startup penalty | ~2-5 min S3 sync | ~2-5 min S3 sync (init container) |
| AWS CLI in NIM image | Yes (baked into shim Dockerfile) | No (init container is separate image) |
| Process supervision | `launch.sh` PID-monitors NIM; kills Caddy on exit | Kubernetes liveness/readiness probes |
| Inference protocol | SageMaker async (required for large payloads >6 MB) | Native HTTP via NLB |
| Driver control | SageMaker AMI selection via CUDA label | EKS Auto Mode AMI (AWS manages) |
| NGC API key | SageMaker model env var | Kubernetes Secret (`ngc-api-key`) |
| AWS credentials in pod | SageMaker execution role (instance-level) | IRSA (`nim-sa` ServiceAccount) |

### Autoscaling design

Optional pod autoscaling via `eks_clusters[*].enable_autoscaling = true` +
`eks_deployments[*].autoscaling = { ... }`. Customer-facing behavior is in the root README's
"Autoscaling on EKS" section. This section covers the design decisions.

Reference implementation this module builds on:
[Horizontal Autoscaling of NVIDIA NIM Microservices on Kubernetes](https://developer.nvidia.com/blog/horizontal-autoscaling-of-nvidia-nim-microservices-on-kubernetes/)
(NVIDIA blog). We adopt the KEDA + kube-prometheus-stack + DCGM substrate the blog outlines,
extend it to cover the open-weight (vLLM direct) and Maxine (gRPC / one-video-per-GPU) NIM paths,
and reject the blog's alternative `k8s-nim-operator` route because of the Maxine-support gap
documented below.

**Substrate: KEDA + kube-prometheus-stack + DCGM exporter (not HPA + prometheus-adapter, not
k8s-nim-operator).**

Reasoning:

- **KEDA over raw HPA + prometheus-adapter.** Raw HPA can scale on custom metrics only via the
  Custom Metrics API, which requires prometheus-adapter with hand-written rules mapping each
  Prometheus metric to a Kubernetes custom-metric name. That's one config change per NIM type
  we support — high maintenance, easy to get wrong. KEDA speaks PromQL directly inside a
  `ScaledObject.spec.triggers[].metadata.query`, no adapter, no rule map. Under the hood KEDA
  creates a `keda-hpa-<name>` HPA with metric type `External`, so we still get everything HPA
  gives us (behavior blocks, stabilization windows, `Pods` policies) — just without the
  prometheus-adapter tax.

- **We do not adopt `k8s-nim-operator` for LLM autoscaling.** The operator (v3.1.1, May 2026)
  supports LLM autoscaling correctly via `NIMService.spec.scale.hpa`, but it does NOT support
  Maxine (SVD, Studio Voice, BNR, Eye Contact, Relighting) — verified via
  `config/samples/nim/serving/`: no Maxine samples, and the reconciler's `NIM_TRITON_GRPC_PORT`
  env-var handling assumes Triton, not the bespoke gRPC servers Maxine ships. Since the module
  targets Maxine (SVD is a supported deployment path), we can't hand LLM to the operator and drop the rest —
  we'd still need our own substrate for Maxine. Running the operator alongside our own KEDA
  install for LLM and KEDA for Maxine is worst-of-both. Single substrate wins.

- **Cluster-wide addon install (not per-deployment).** KEDA + kps + DCGM are installed once per
  cluster by the existing `cluster-setup` CodeBuild action, gated by
  `terraform_data.cluster_setup_trigger.input.enable_autoscaling`. Per-deployment installs
  would duplicate infra, complicate namespace ownership, and break cross-deployment scaling
  visibility.

**Per-deployment ScaledObject emission.**

Three code paths in `deploy-nim.yml`, each with a different metric source and ServiceMonitor
posture — chosen empirically based on what each NIM family actually exposes:

| Path | Metric source | ServiceMonitor emitter |
| --- | --- | --- |
| NIM Helm (LLM/VLM/embed/rerank/speech) | Chart-emitted metrics endpoint | Chart itself (via `metrics.serviceMonitor.enabled=true` in generated values) |
| Open-weight (vLLM direct) | vLLM `/metrics` on port 8000 | Hand-emitted by buildspec, `path: /metrics`, `port: http` |
| gRPC (Maxine) | DCGM exporter (cluster-wide DaemonSet) | None — Maxine has no request-load metric on its `/v1/metrics` (only GPU/process/Python telemetry) |

The Maxine gap is documented at
[docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/observability.html](https://docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/observability.html) —
the enumerated metrics are `gpu_power_usage_watts`, `gpu_utilization`, `process_cpu_seconds_total`,
`python_gc_*`, and similar. No `num_requests_running`, no queue depth, no latency histograms. DCGM
is the only usable signal for Maxine autoscaling.

**Metric name derivation and the vLLM prefix subtlety.**

The NIM `nim-llm` Helm chart re-exports vLLM metrics but strips the `vllm:` prefix — a NIM's
`/v1/metrics` shows `gpu_cache_usage_perc`, not `vllm:gpu_cache_usage_perc`. This is confirmed
by:

- NVIDIA blog: [Horizontal Autoscaling of NVIDIA NIM Microservices on Kubernetes](https://developer.nvidia.com/blog/horizontal-autoscaling-of-nvidia-nim-microservices-on-kubernetes/) —
  HPA uses `metric.name: gpu_cache_usage_perc` verbatim
- k8s-nim-operator autoscaling sample: [`config/samples/nim/serving/standalone/autoscaling/llm.yaml`](https://github.com/NVIDIA/k8s-nim-operator/blob/main/config/samples/nim/serving/standalone/autoscaling/llm.yaml) —
  same bare name

By contrast, the open-weight path runs `vllm/vllm-openai:latest` directly (no NIM chart in the
loop), so vLLM emits `vllm:kv_cache_usage_perc` with the prefix — and the vLLM V1 metrics
refresh renamed `gpu_cache_usage_perc` → `kv_cache_usage_perc`
([vLLM stable metrics docs](https://docs.vllm.ai/en/stable/design/metrics/)). NIM has not
adopted the rename yet as of NIM 1.12.0. `local.autoscaling_metric_defaults` in `locals.tf`
uses `gpu_cache_usage_perc` for NIM and `vllm:kv_cache_usage_perc` for open-weight to match
these two different metric surfaces.

**Chart version pinning and the flag combinations that make things work.**

Every helm install in `modules/eks-infra/buildspecs/cluster-setup.yml` pins a version and
carries specific `--set` flags. Removing any of these results in silent failure — Prometheus
runs but scrapes nothing, or KEDA runs but sees no metrics. The non-obvious ones:

- `kube-prometheus-stack` (87.16.1) needs
  `prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false`. Default `true`
  auto-injects a `release: <helm-release-name>` matchLabel, restricting discovery to
  ServiceMonitors that carry the kps release label — but NIM ServiceMonitors carry the NIM
  chart's own release label. Setting the flag to `false` widens discovery to any label.
  Namespace discovery is intentionally NOT set via `--set` — the chart's else-branch already
  renders `serviceMonitorNamespaceSelector: {}` when unset, which matches all namespaces per
  standard LabelSelector semantics. An earlier iteration used
  `serviceMonitorNamespaceSelector.any=true`, which is syntactically wrong — `any` is a
  NamespaceSelector field, not a LabelSelector field. Two different types with same-ish names
  in the prometheus-operator API. Dropped. Confirmed by
  [`kube-prometheus-stack/values.yaml`](https://raw.githubusercontent.com/prometheus-community/helm-charts/main/charts/kube-prometheus-stack/values.yaml)
  (lines ~4441–4462) and the operator's
  [Prometheus CR template](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/templates/prometheus/prometheus.yaml).
- `dcgm-exporter` (4.8.3) needs three flags: `kubernetes.enablePodLabels=true`,
  `serviceMonitor.additionalLabels.release=kps`, and `serviceMonitor.honorLabels=true`.
  Chart defaults are `false`, `{}`, and `false` respectively. Rationale for each:
  - `enablePodLabels=true` — DCGM sources `pod` and `namespace` labels from the kubelet
    PodResources socket. Without it, metrics carry only node-level labels (`Hostname`, `gpu`,
    `UUID`) and our `pod=~"<deployment>-.*"` PromQL filter matches nothing.
  - `serviceMonitor.additionalLabels.release=kps` — DCGM's chart-installed ServiceMonitor
    doesn't stamp the release label kube-prometheus-stack expects. Without this,
    Prometheus ignores the ServiceMonitor entirely.
  - `serviceMonitor.honorLabels=true` — with `honorLabels=false` (chart default), Prometheus's
    scrape config auto-injects `namespace` and `pod` labels referring to the DCGM exporter's
    OWN pod (in the `monitoring` namespace), and renames DCGM's target-emitted `namespace`/
    `pod` labels (which refer to the workload pod being observed) to `exported_namespace` and
    `exported_pod`. That breaks the ScaledObject query, which filters by `namespace` and `pod`
    expecting workload semantics. Setting `honorLabels=true` makes DCGM's target labels
    canonical. Discovered at runtime — with `honorLabels=false` the ScaledObject query returned
    zero-value averages while DCGM metrics were flowing correctly; the fix was verified by
    inspecting the raw Prometheus target labels.
  Confirmed by [`dcgm-exporter/deployment/values.yaml`](https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/deployment/values.yaml).
- `KEDA` (2.20.1) — no special flags; standard `helm repo add kedacore` install works. KEDA
  chart is on the traditional Helm repo, NOT OCI as some outdated docs suggest.

Chart versions are current as of 2026-07 and should be reviewed periodically.

**HPA behavior vs KEDA cooldownPeriod: a real footgun.**

`ScaledObject.spec.cooldownPeriod` controls **only scale-to-zero delay** (from last active
trigger to zero replicas). For the common `min_replicas >= 1` case, cooldownPeriod is a no-op.
Scale-down between N and 1 is governed by the underlying HPA's
`behavior.scaleDown.stabilizationWindowSeconds`. The module's `autoscaling.scale_down_delay`
input feeds `advanced.horizontalPodAutoscalerConfig.behavior.scaleDown.stabilizationWindowSeconds`,
not `cooldownPeriod`, so it actually affects the common case.

Documented at [keda.sh/docs/latest/reference/scaledobject-spec/](https://keda.sh/docs/latest/reference/scaledobject-spec/).

**Cross-namespace ScaledObject semantics.**

A ScaledObject can only target Deployments in its own namespace (`scaleTargetRef` has no
namespace field). Prometheus, however, can be anywhere — the trigger's `serverAddress` is a
plain URL. The buildspec emits ScaledObjects in the deployment's namespace and points
`serverAddress` at
`http://kps-kube-prometheus-stack-prometheus.monitoring.svc.cluster.local:9090`. No RBAC
gotcha for the HTTP call; the only risk is a NetworkPolicy blocking cross-namespace traffic
(the module does not create NetworkPolicies).

**Destroy ordering.**

`terraform_data.autoscaling_cleanup` in `modules/eks-infra/cleanup.tf` has
`depends_on = [aws_eks_cluster.nim]` and `count = var.enable_autoscaling ? 1 : 0`. At destroy
time the dependency reverses: this resource is destroyed first, running its `when = destroy`
provisioner which `helm uninstall`s the three addons before the cluster teardown loop begins.
Ordering matters because Prometheus's StatefulSet PVCs need to drain cleanly, and KEDA needs
to remove its ScaledObjects across all namespaces before the cluster's API is torn down. Same
pattern as the existing `terraform_data.helm_cleanup` in `modules/eks-app/main.tf`, just
scoped to the addon stack instead of per-deployment resources.

---

## Variable defaults, null vs empty, and conditional resource patterns

This section exists because these decisions look arbitrary without context and are easy to
"fix" in ways that silently break things.

### Why inner maps default to `{}` and the outer object defaults to `{}`

```hcl
variable "sagemaker_endpoints" {
  type = object({
    # Inner maps use optional(..., {}) — empty map, not null.
    # An empty map means "nothing configured here" and is safe to pass directly to
    # for_each and length() with no guards. null would require defensive try() or
    # != null checks scattered everywhere the map is referenced.
    nim         = optional(map(object({...})), {})
    open_weight = optional(map(object({...})), {})
  })
  # Outer object defaults to {} so .nim and .open_weight are always accessible.
  # Callers who don't use SageMaker at all simply omit this variable entirely.
  default = {}
}
```

The rule (confirmed against aws-ia/terraform-aws-iam-identity-center,
aws-ia/terraform-aws-agentcore, and aws-games/cloud-game-development-toolkit):

- **Single optional object** (enable a whole feature or not) → `default = null`.
  `null` signals "not configured". Gate with `count = var.x != null ? 1 : 0`.
- **Map of objects** (zero or more instances of something) → `default = {}`.
  Empty map is naturally "nothing". `for_each` and `length()` handle it with no guards.

Do not change inner map defaults to `null`. Every `for_each` and `length()` downstream
would need a `try()` or `!= null` ternary wrapping it. Terraform does not short-circuit
`&&` ([issue #24128](https://github.com/hashicorp/terraform/issues/24128)), so
`var.x != null && var.x.field != null` errors when `var.x` is null.

### How resources are conditionally created

**Whole resource — `count`**

```hcl
# Create the model-assets S3 bucket only when at least one open-weight endpoint
# or EKS open-weight deployment is configured. length({}) = 0, so an empty map
# means count = 0 and no bucket is created.
resource "aws_s3_bucket" "model_assets" {
  count = length(var.sagemaker_endpoints.open_weight) > 0 ||
          length(var.eks_deployments.open_weight) > 0 ? 1 : 0
}
```

**One resource per map entry — `for_each`**

```hcl
# Creates one CodeBuild project per NIM endpoint. If the map is empty, no
# projects are created. each.key = endpoint name, each.value = endpoint config.
resource "aws_codebuild_project" "deploy" {
  for_each = var.sagemaker_endpoints.nim
  name     = "${local.name_prefix}-${each.key}-deploy"
}

# for_each also accepts an inline filter — only entries matching the condition
# get a resource. Empty result = no resources, no error.
resource "aws_codebuild_project" "cache" {
  for_each = {
    for k, v in var.sagemaker_endpoints.nim : k => v
    if v.enable_model_profile_cache
  }
}
```

**Optional block inside a resource — `dynamic`**

`count` only works on whole resources, not on blocks inside a resource (like a `statement`
inside an IAM policy document). `dynamic` is the solution. Its `for_each` is an on/off
switch: `[1]` renders the block once, `[]` skips it entirely. The `1` is a throwaway
value — the block body doesn't use it.

```hcl
data "aws_iam_policy_document" "example" {
  # Include the model-assets read statement only when open-weight is configured.
  # [1] = render once, [] = don't render. The 1 is never referenced inside content {}.
  dynamic "statement" {
    for_each = length(var.sagemaker_endpoints.open_weight) > 0 ? [1] : []
    content {
      actions   = ["s3:GetObject", "s3:ListBucket"]
      resources = [aws_s3_bucket.model_assets[0].arn]
    }
  }
}
```

---

## Known Implementation Pitfalls

### Never merge `.nim` and `.open_weight` maps into a single `for_each`

`var.sagemaker_endpoints.nim` and `var.sagemaker_endpoints.open_weight` are separate typed maps by design. Users naturally give them the same key when the same model is deployed both ways -- for example, both maps might have key `nemotron-9b` in an all-inference configuration.

Terraform's `merge()` is **last-wins on duplicate keys**. Any code that merges the two maps into one collapses both entries into a single entry, silently discarding one. This produces bugs that are invisible in plan output because both entries appear to exist as Terraform resources (`aws_sagemaker_endpoint.nim["nemotron-9b"]` and `aws_sagemaker_endpoint.open_weight["nemotron-9b"]`), but the underlying AWS names they compute are identical -- causing the second `Create*` call to fail with an "already exists" error.

**Rule:** Never use `merge(var.sagemaker_endpoints.nim, var.sagemaker_endpoints.open_weight)` or `merge(var.eks_deployments.nim, var.eks_deployments.open_weight)` in any resource or local. Always iterate each map independently. When AWS names must be unique across both, add a `-nim`/`-ow` type discriminator in the name string rather than relying on the user's key choice.

The same rule applies to `eks_deployments.nim` and `eks_deployments.open_weight`.

**Confirmed occurrences fixed:** `random_id.endpoint_suffix`, `sagemaker_endpoint_names`, `sagemaker_model_names`, `aws_cloudwatch_log_group.sagemaker_endpoint`, `eks_gpu_count`, `eks_app` module `name_prefix`.

---

## Open Questions

| ID | Status | Question |
|----|--------|---------|
| Q2 | Open | Google Drive file ID for `alpamayo-nim-<version>.tgz` — needed for bootstrap docs |
| Q3 | Open | `capacity_reservation_config` is not exposed by the hashicorp/aws provider. CloudFormation `AWS::SageMaker::EndpointConfig` supports it via `CapacityReservationConfig { MlReservationArn }` — the AWSCC provider may expose it (auto-generated from CFN schema) but is unconfirmed at runtime (known regressions: github.com/hashicorp/terraform-provider-awscc/issues/2268). `MlReservationArn` takes a **Training Plan ARN**, not an EC2 ODCR ARN. To enable: (1) add `hashicorp/awscc` to `versions.tf`; (2) create a Training Plan via `aws sagemaker search-training-plan-offerings` + `aws sagemaker create-training-plan`; (3) pass the ARN as `ml_reservation_arn` per endpoint; (4) add an `awscc_sagemaker_endpoint_config` resource in `main.tf` gated on `ml_reservation_arn != null`. TODO: (a) test AWSCC path, (b) file hashicorp/aws GitHub issue. |
| Q5 | Resolved | CodeBuild fleet with `CUSTOM_INSTANCE_TYPE` provisions the exact EC2 instance family configured in `sagemaker_config.instance_type`. No region-availability concern beyond normal EC2 availability. |
| Q6 | Open | Is SageMaker inference AMI 4-1 bug fixed? Who confirmed it broken, and what specifically failed? |
| Q7 | Open | EKS Auto Mode: what exact driver version does AWS ship for g5 and g6e accelerated AMIs? Run `nvidia-smi` on a fresh Auto Mode node before Phase 3 |
