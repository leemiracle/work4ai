# Grafana source and reproducible builds

The installable plugin is generated output. Its reviewed, portable source is
stored in [`vendor/grafana-observability-source`](../vendor/grafana-observability-source),
not in a developer's external checkout. Do not edit the `.source.part-*` files.

## Verify

From the repository root, with Node.js 22.19 or newer:

```sh
# No install, network, native loading, or credentials; works across platforms.
npm run verify:grafana:source

# macOS arm64: fresh extraction, locked install, exact-byte rebuild.
node scripts/verify-grafana-source.mjs --rebuild

# Also typecheck and run the reviewed source qualification suites.
node scripts/verify-grafana-source.mjs --rebuild --test
```

Add `--offline` to a rebuild command when all locked npm packages are already
cached. Rebuilding requires npm 10 or newer. The verifier uses a private temporary
directory, disables npm lifecycle scripts, compares every generated file, and
removes its temporary tree afterward. It never changes the checked-in package.

`--test` builds clean public-workspace test dependencies and runs the Grafana
adapter/MCP, credential profile, authority CLI, observability CLI, security,
provider-runtime, and distribution-regression suites. The tests use synthetic
fixtures, disposable local HTTP/TLS servers, and temporary state; they do not
read a user's Keychain or contact production. Git and OpenSSL must be available
for the complete suite.

The recorded qualification ran `--rebuild --test --offline` from this archive on
macOS arm64 with Node.js 26.0.0: **183 tests passed, zero failed or skipped**, and
all **64 generated files matched byte-for-byte**. This is separate from the
packaged Node.js 22.19 compatibility checks in the
[verification guide](../tests/grafana-observability/README.md).

Linux, Windows, and macOS x64 can verify source/archive/output hashes. They cannot
rebuild this **macOS arm64 native candidate** with this command. The platform gate
is intentional: the verifier does not spoof npm's platform or architecture.

## What is pinned

| Artifact | Purpose |
| --- | --- |
| [`source.tar.gz`](../vendor/grafana-observability-source/source.tar.gz) | Authoritative qualified first-party source, build helpers, lockfile, schemas, static plugin inputs, and focused tests: 327 files, about 556 KB compressed. |
| [`manifest.json`](../vendor/grafana-observability-source/manifest.json) | SHA-256 and byte length for the archive, every source file, all 64 generated files, the lockfile, native asset, and review patch. Also records the observed upstream revision and changed-file inventory. |
| [`qualification.patch`](../vendor/grafana-observability-source/qualification.patch) | Human-readable 18-file change from the public-normalized pre-qualification source to this distribution. Its headers contain repository-relative paths. |

The source archive SHA-256 is
`5fc0e01c25d33701416751064a71ebf315abd38ab9418570a3fad1b0451ef106`.
The manifest is authoritative when a reviewed update changes this snapshot.

The uncompressed TAR is deterministic: sorted paths, regular files only, fixed
mode and timestamps, no symlinks, and bounded decompression. The checked-in gzip
file is independently pinned by its exact byte length and SHA-256. Gzip
recompression can differ between compression libraries: Node.js 26.0.0 with zlib
1.2.12 and Node.js 22.19.0 with zlib 1.3.1-470d3a2 produced different compressed
bytes from identical TAR contents. The regression checks exact decoded TAR bytes
and repeatability within each encoder, not cross-zlib gzip equality. Normal
verification does not rewrite the authoritative archive.

The snapshot contains no `node_modules`,
Git history, build caches, generated runtime, native binaries, credentials,
customer evidence, or video. A source capture scans for common credential/private
key indicators; that scan supplements review and is not a guarantee about arbitrary
future inputs. Static plugin inputs are also checked against the installable copy.

## Bundled provenance and its limit

The repository ships the reviewed source snapshot needed to reproduce this
distribution. It was captured from a private development checkout whose remote,
branch, and unpublished revision are intentionally not part of the public
release contract. Public verification is therefore based on the
content-addressed archive, exact generated-file receipts, and reversible review
patch in this repository—not an unreachable upstream URL or Git commit.

The public-normalized pre-qualification baseline contains 321 files. Publisher
and unreachable-checkout labels were normalized before its hash was recorded;
that normalization does not change the functional source. Its tree SHA-256 is
`7e5d82af3ddafb49c3eb6aa2b35273f5980657c265008ee22c0758d4a24c1cc4`.
The qualification patch is relative to that public-normalized baseline, **not** directly
to a published Git commit. The provenance regression test reverses the patch and
verifies the exact baseline tree and changed-file inventory. No unrelated upstream
history or worktree changes are included or reset.

The reviewed changes cover:

- Native loader staging that remains linked until macOS `dlopen` finishes, plus
  strict handling and erasure of the pinned addon's actual `null`/byte-array ABI.
- Platform-independent CLI help/version without weakening credential-command gates.
- A fixed, enrolled Tempo search GET route and bounded native Tempo/Loki response
  projection, with scope proved from actual provider data before normalization.
- Regression tests and updates to legacy fixtures that assumed Tempo POST/dataframes.
- Distribution manifest links, the README release allowlist, five explicitly allowed
  nonsecret launch settings, and verified client-launch guidance. Setup is based
  on effective permissions; a Viewer role label alone does not prove read-only access.

## Canonical build

The snapshot retains the upstream `buildPluginArtifacts` implementation in
`scripts/plugin-build-lib.mjs` and the `grafana-observability` descriptor in
`scripts/plugin-descriptors.mjs`. The verifier invokes those helpers for
`darwin/arm64`, not a second bundler implementation. Esbuild 0.28.1 bundles four
entrypoints for Node 22: the MCP server, credential CLI, authority CLI, and provider
worker. The canonical builder writes integrity-checked source shards, schemas,
legal notices, and the target-native asset.

The native addon is the locked npm artifact
`@napi-rs/keyring-darwin-arm64@1.3.0`: 491,232 bytes, SHA-256
`9627560bd2490b8495504df6b48dafe0153883aab09fd8eee976f826c74a6fff`.
The builder checks its bytes before packaging. This reproduces the distribution
using that pinned native artifact; it does **not** claim to rebuild the addon's
Rust/Mach-O binary from native source.

## Review and update

To inspect the source without installing anything:

```sh
node scripts/verify-grafana-source.mjs --extract /tmp/grafana-source-review
```

The destination must not already exist. Install locked dependencies only in that
extracted tree, make reviewed source/test changes, and use the canonical
`buildPluginArtifacts` helper with the packaged plugin directory as `outputRoot` when
regenerating a release. Keep its explicit `targetPlatform: "darwin"` and
`targetArchitecture: "arm64"`. Synchronize intentionally changed static plugin
files separately; the capture command rejects mismatched static inputs.

After refreshing the normalized qualification patch against the recorded baseline,
run from the repository root:

```sh
node scripts/verify-grafana-source.mjs --capture-source /absolute/path/to/reviewed-source
node scripts/verify-grafana-source.mjs --rebuild --test
node --test tests/grafana-observability/source-provenance.test.mjs
```

Capture is an explicit maintainer operation: it rebuilds the supplied source and
requires exact equality with the already-regenerated package before replacing the
archive and receipts. `--source /absolute/path/to/prepared-source` verifies an
unchanged extracted tree with already-installed dependencies without fetching them.
To recover the public-normalized baseline for a new review diff, extract the current
snapshot into another fresh directory and apply the existing `qualification.patch`
with `git apply --reverse` there. Diff only the reviewed source inputs, not installed
dependencies or generated output; the provenance test checks the reverse relation.

This is a bounded source qualification, not the entire upstream repository's test
or publishing pipeline. Real provider versions, authenticated access, packaged
Keychain behavior, and installed-client qualification are separate checks recorded
in the [verification guide](../tests/grafana-observability/README.md). The
bundled [live-stack matrix](../tests/grafana-observability/support/live-stack/matrix.json),
not an upstream synthetic version string, records the real Grafana release pins.
