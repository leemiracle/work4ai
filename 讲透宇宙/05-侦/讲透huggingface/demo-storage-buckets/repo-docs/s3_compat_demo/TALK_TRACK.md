# Talk Track — S3 Compatibility (~15–20 min)

**The pitch:** Your existing S3 tools and code work against HF Storage Buckets
unchanged — point them at the gateway, and you get modern S3 conditional writes
for safe concurrent updates.

**Who it's for:** Anyone with an S3-based workflow — infra teams, data
engineers, ML pipelines — who wants HF storage without rewriting tooling.

Setup lives in `README.md`; assume the `hf` profile and credentials are already
in place before you present.

Each demo script **pauses for Enter between steps** — hit Enter when you're ready
to move to the next one, so you can talk over each result. (Run with `--no-pause`
to disable, e.g. for a dry run.)

| Phase | Story | Script | Duration |
|-------|-------|--------|----------|
| 0 | Credentials & profile (pre-demo) | `setup_profile.sh`, `check.sh` | — |
| 1 | "Your S3 tools just work" | `demo_01_s3_basics.sh` | ~5 min |
| 2 | Conditional operations (the hero) | `demo_02_conditional_ops.sh`, `conditional_writes.py` | ~8 min |
| 3 | Reality check (Q&A) | notes below | ~2 min |

---

## Phase 0 — Credentials & profile (pre-demo)

Done before you present; mention it in one breath. S3 credentials come from an
HF Access Token (Settings → Access Tokens → **Generate S3 credentials**), the
gateway endpoint is `https://s3.hf.co/<namespace>`, and the profile just needs a
few fields (single-region, path addressing, checksums `when_required`). If
anything looks off live, run the doctor:

```bash
./check.sh
```

---

## Phase 1 — "Your S3 tools just work" (~5 min)

> "This is stock AWS CLI. The only thing I've changed is the profile — it points
> at the HF gateway. No wrapper, no SDK, no new commands to learn."

Walk the lifecycle — make a bucket, upload, list, remove:

```bash
./demo_01_s3_basics.sh
```

> "`mb`, `cp`, `ls`, `rm` — exactly what your infra team already runs against
> AWS. Your existing scripts don't know the difference."

---

## Phase 2 — Conditional operations (~8 min, the hero)

This is the memorable moment. Frame the problem first:

> "Two writers, one object. With plain PUTs, last-writer-wins — one silently
> clobbers the other. S3 conditional writes turn that race into a safe,
> explicit outcome, and the HF gateway honors them."

Run the CLI version against the shared `sample_data/manifest.json`:

```bash
./demo_02_conditional_ops.sh
```

Narrate the two patterns as they scroll by:

- **No-clobber / create-only — `If-None-Match: *`.** First writer wins. The
  second identical create comes back **412 Precondition Failed**.
  > "The 412 is the win. A conflicting writer was *safely rejected* — not
  > silently overwritten. First writer keeps their object."

- **Compare-and-swap — `If-Match: <etag>`.** Read the object's ETag, modify it
  locally, write back conditioned on that ETag. A fresh ETag succeeds; a **stale
  ETag gets a 412**, telling you someone else changed it first — so you re-read
  and retry instead of stomping their update.
  > "This is optimistic concurrency: safe read-modify-write with no locks."

Then the same story in code, so the audience sees it works from `boto3` too:

```bash
uv run conditional_writes.py --namespace your-username
```

> "Same profile, same credentials — just boto3. Two writers race: one create
> wins, the other's is rejected; then a compare-and-swap catches a stale ETag
> and retries against the fresh object. Reproducible, no data lost."

**Takeaway to land:** a 412 is not an error to fear — it's the system telling you
a conflicting write was caught before it did damage.

---

## Phase 3 — Reality check (~2 min, Q&A)

Be upfront about the edges so nobody is surprised in production:

- **Single-region.** GetObject is proxied through the gateway for the AWS CLI /
  boto3; other clients get a 302 to the nearest CDN edge and follow it.
- **Conditional writes are on writes only** — PutObject and the CopyObject
  copy-source, **not** GetObject.
- **Not supported:** ACLs, bucket policies, tagging, versioning, lifecycle, SSE,
  notifications.
- **CopyObject is same-namespace only. `ListObjectsV2` only.**
- **Key rules:** no leading/trailing `/`, no `//`, no `../`, no leading `./`, no
  trailing `..`, no `\` or null bytes.

Reset the environment when you're done:

```bash
./cleanup.sh
```

**Wrap:** "Point your existing S3 tools at the gateway and they just work — plus
you get conditional writes for safe concurrent updates."
