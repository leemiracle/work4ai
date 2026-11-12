# Running tokbench on Hugging Face Jobs

The Jobs path separates two kinds of reproducibility:

- the image digest, Cargo lockfile, source revision and input revision reproduce
  the software and data;
- repeated complete runs inside a Job, followed by runs on several Jobs,
  quantify timing noise and host-to-host variance.

A Jobs hardware flavor specifies allocated resources. It does not promise that
every Job lands on the same physical CPU model, so do not compare absolute MB/s
across Jobs without reading each run's `environment-before.json`.

The `blog-v1` profile also pins the benchmark process to one logical CPU from
each of eight distinct physical cores. This keeps the 1/2/4/8-thread scaling
sweep off sibling SMT threads. The selected CPU set and effective task affinity
are recorded in the environment manifest.

## Publish a commit-specific Docker Space

Push the tokbench commit first, then create a private Docker Space from the
clean checkout. The generated Space recipe pins both base-image digests and
clones the exact tokbench commit:

```bash
revision=$(git rev-parse HEAD)
python hf-jobs/publish_space.py \
  --repo-id "$USER/tokbench-jobs-${revision:0:7}"
```

The Space is an image builder and host. Benchmarks run on Jobs hardware, not on
the Space. A commit-specific Space is immutable by convention, so submit it
with `--allow-mutable-image`; do not update that Space to another tokbench
commit.

## Submit

Install a current `huggingface_hub`, log in, and use a writable Storage Bucket.
The test-data revision must be a commit SHA, not `main`:

```bash
python hf-jobs/submit.py \
  --image hf.co/spaces/<user>/tokbench-jobs-<commit> \
  --allow-mutable-image \
  --input-revision <tokenizers-test-data-commit> \
  --corpora-revision <tokbench-corpora-commit> \
  --bucket huggingface/tokbench-results
```

The default is `cpu-performance`, five independent process-level runs, five
timed repetitions per cell, and 1/2/4/8-thread scaling sweeps on English and
Chinese. Use `--models` or `--engines` with comma-separated names for a smaller
validation run. Jobs default to a 30-minute timeout, so the submitter requests
six hours.

To reproduce Section 01 of the tokenizers v1 blog, select its fixed eight-model
matrix. The profile measures encode, decode, 1/2/4/8-thread scaling on English
and Chinese, and call-level latency over 1,000 distinct 512-byte English
documents:

```bash
python hf-jobs/submit.py \
  --profile blog-v1 \
  --image hf.co/spaces/<user>/tokbench-jobs-<commit> \
  --allow-mutable-image \
  --input-revision <tokenizers-test-data-commit> \
  --corpora-revision <tokbench-corpora-commit> \
  --bucket huggingface/tokenizers-v1-benchmarks
```

`blog-v1` fixes the models, the `hf-tokenizers`, `pipeline`, and
`pipeline-no-cache` engines, English/Chinese scaling corpora, and eight-thread
ceiling. The third engine is the cache-disabled diagnostic used by Section 02.
Run the profile once with `--scaling-mode native-threads` and once with
`--scaling-mode independent-instances` when publishing both scaling views.
Use the default profile instead when overriding the rest of that matrix. A
model selection controls both the downloaded artifacts and the driver filter,
so a selected model cannot be silently absent from the Job.

The encode-only comparison against other Rust tokenizer libraries uses the
same eight models and 22 corpora without running the other measurement
families:

```bash
python hf-jobs/submit.py \
  --profile blog-v1-libraries \
  --image hf.co/spaces/<user>/tokbench-jobs-<commit> \
  --allow-mutable-image \
  --input-revision <tokenizers-test-data-commit> \
  --corpora-revision <tokbench-corpora-commit> \
  --bucket huggingface/tokenizers-v1-benchmarks
```

This runs `measure encode` for pipeline, kitoken, fastokens, tokie, tiktoken
and wordchipper, all compared with one shared `hf-tokenizers` baseline.
Add `--dry-run` to print the resolved, non-secret Job configuration without
submitting or consuming compute.

Scaling defaults to capability-based selection. Pass
`--scaling-mode native-threads` to require the engine's own pool, or
`--scaling-mode independent-instances` to run one single-threaded tokenizer
instance per harness thread.

For a cache-capacity experiment, use the default profile and pass, for example,
`--measure encode --engines pipeline --cache-capacity 8192`. The value is
forwarded to every repeated run and recorded in the report metadata. A value of
`0` disables the pipeline BPE cache; omitting the option keeps the upstream
65,536-entry default.

Gigatoken requires a nightly Rust toolchain and a different lockfile because
its upstream manifest uses nightly-only profile rustflags. Build a dedicated
image after pushing the tokbench commit:

```bash
revision=$(git rev-parse HEAD)
python hf-jobs/publish_space.py \
  --gigatoken \
  --repo-id "$USER/tokbench-jobs-gigatoken-${revision:0:7}"
```

Then run the same single-thread comparison with Gigatoken included:

```bash
python hf-jobs/submit.py \
  --profile blog-v1-libraries-gigatoken \
  --image hf.co/spaces/<user>/tokbench-jobs-gigatoken-<commit> \
  --allow-mutable-image \
  --input-revision <tokenizers-test-data-commit> \
  --corpora-revision <tokbench-corpora-commit> \
  --bucket huggingface/tokenizers-v1-benchmarks
```

The image recipe runs `hf-jobs/prepare_gigatoken.py` in its disposable checkout.
That script enables the exact Gigatoken revision recorded in the adapter and
installs `hf-jobs/Cargo.gigatoken.lock` as the build lockfile. The benchmark Job
uses that prebuilt binary. The image builds one crate at a time and uses LLVM's
linker to keep the fat-LTO build within the Docker Space builder's memory limit.
Both library profiles use one thread and do not
request CPU affinity because they do not run a scaling measurement.

The private `hf-internal-testing/tokenizers-test-data` input requires an HF
token. By default the submitter forwards the locally configured token as an
encrypted Job secret. It is not written to the environment manifest.

The corpora come from the public dataset instead and are pinned separately with
`--corpora-revision`, since the two repos move independently. Both SHAs are
mandatory: `main` is not reproducible.

## Artifacts

Each Job writes to `/outputs/$JOB_ID/` in the bucket:

- `run-01.json` through `run-05.json`: complete, independent reports;
- matching logs for diagnosis;
- the exact command for each run, with scaling order alternating between
  ascending and descending thread counts to expose temporal drift;
- `scaling-summary.json`, computed from paired points within each report;
- environment manifests captured before and after benchmarking;
- SHA-256 manifests for every input and output;
- the exact benchmark command.

Compute scaling efficiency within each report from its paired 1-thread and
8-thread points. Summarize that distribution across reports. Do not divide an
8-thread median pooled across reports by a separately pooled 1-thread median.

## View a completed Job

The native dashboard fetches through `huggingface_hub`, verifies the artifact
manifest, and displays the median of every complete `run-*.json` report. The
aggregate preserves median encode and decode metrics; the current native
dashboard renders its existing encode and scaling views:

```bash
make dash BUCKET=huggingface/tokbench-results JOB_ID=<job-id>
```

The aggregate keeps each thread-count result paired with its own run's
1-thread baseline before taking the median. The dashboard labels aggregated
data explicitly. To inspect one underlying run instead:

```bash
make dash BUCKET=huggingface/tokbench-results JOB_ID=<job-id> RUN=3
```

Local files use the same path. A directory is aggregated by default:

```bash
make dash RESULTS=results/<job-id>
make dash RESULTS=results/<job-id> RUN=3
make dash RESULTS=results/<job-id>/run-03.json
```
