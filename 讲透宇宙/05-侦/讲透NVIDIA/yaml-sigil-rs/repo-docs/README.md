# yaml-sigil-rs

[![GitHub license](https://img.shields.io/github/license/NVIDIA/yaml-sigil-rs)](https://github.com/NVIDIA/yaml-sigil-rs/blob/main/LICENSE)
[![CI](https://github.com/NVIDIA/yaml-sigil-rs/actions/workflows/ci.yml/badge.svg)](https://github.com/NVIDIA/yaml-sigil-rs/actions/workflows/ci.yml)

`yaml-sigil-rs` provides Rust implementation crates for
[`yaml-sigil`](https://github.com/NVIDIA/yaml-sigil-spec#tldr). It depends on
[`yaml-sigil-traits`](https://crates.io/crates/yaml-sigil-traits) for the
public extension-trait contract. This workspace implements signing,
verification, transcription, protobuf wire helpers, YAML signature-document
parsing, and local conformance checks.

This repository includes the protobuf schema, signature-document JSON Schema,
curated conformance fixtures, and their third-party notices. Read
[`yaml-sigil-spec`](https://github.com/NVIDIA/yaml-sigil-spec) for the normative
specification.

NVIDIA-authored material is licensed under the
[Apache License 2.0](./LICENSE). Third-party test data, standards-derived
material, and their redistribution requirements are documented in
[`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md).

The `yaml-sigil-verification` source package also includes its scoped notice
for RFC 8032-derived constants, canonical-encoding rules, and a test-vector
value. The `yaml-sigil-signing` source package includes a scoped notice for
its RFC 8032-derived provider validation rules. Both crates retain source
terms for their *Standards for Efficient Cryptography 1 (SEC 1)* material.

Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) before proposing a change.

## Select the specification contract

Use each published crate's `v1alpha1` module to select the current
specification contract explicitly. For example, import signing operations
from `yaml_sigil_signing::v1alpha1` and protobuf helpers from
`yaml_sigil_core::v1alpha1::pb`. The generated JavaScript bindings expose the
same choice through `v1alpha1.sign`, `v1alpha1.verify`, `v1alpha1.compose`,
`v1alpha1.decompose`, and their resource-aware counterparts.

The unqualified Rust and JavaScript APIs remain the `v1alpha1` default. Rust
paths re-export the existing definitions, so types, trait implementations,
keys, and requests pass between both styles without conversion. Both use the
same selected `yaml-sigil-traits` dependency. JavaScript operations share the
existing result classes and resource-policy objects.

`v1alpha1` identifies specification behavior, independently of crate SemVer.
Selecting the namespace preserves feature requirements, runtime behavior,
and YAML and protobuf wire formats.

## Crates

The workspace provides four Rust implementation crates and a WebAssembly
binding crate. Most Rust applications start with
`yaml-sigil-signing` when producing signed documents and
`yaml-sigil-verification` when accepting them. The core and transcription
crates provide the shared document handling used by those higher-level APIs.

### [`yaml-sigil-core`](./crates/yaml-sigil-core/README.md)

[![yaml-sigil-core on crates.io](https://img.shields.io/crates/v/yaml-sigil-core.svg?label=yaml-sigil-core)](https://crates.io/crates/yaml-sigil-core)

This crate provides shared document operations. It recognizes document
boundaries, applies payload rules, reads and writes YAML signature documents,
handles the protobuf wire format, and maps signature
algorithms. It exposes a stable protobuf facade backed by private generated
code from [`buffa`](https://crates.io/crates/buffa). Its public
`SignatureDocument` Serde data model and YamlSigil-owned parser and serializer
keep the concrete YAML backend private. The implementation uses
[`noyalib`](https://crates.io/crates/noyalib). Its optional
`json-schema-validate` feature validates signature documents against the local
schema.

Serde is the stable public data-model boundary for `SignatureDocument`.
Consumers can exchange semantic values through Serde without depending on the
`noyalib` release selected by this workspace. Direct Serde deserialization does
not apply YamlSigil's YAML byte limit or parser policies, so use
`parse_signature_document` for untrusted YAML signature carriers. Serde
compatibility does not promise identical YAML acceptance, resource policy,
presentation, or bytes. Use `serialize_signature_document` for canonical YAML,
and retain the original carrier bytes when forwarding must be lossless.

The [YAML facade guide](./docs/yaml-facade.md) demonstrates parsing and
serialization through the core API. The
[protobuf facade guide](./docs/protobuf-facade.md) demonstrates owned and
borrowed decoding and exchanging wire bytes with Prost. Both include
small runnable examples.

The other implementation crates build on this layer, so most applications use
`yaml-sigil-core` indirectly.

### [`yaml-sigil-transcription`](./crates/yaml-sigil-transcription/README.md)

[![yaml-sigil-transcription on crates.io](https://img.shields.io/crates/v/yaml-sigil-transcription.svg?label=yaml-sigil-transcription)](https://crates.io/crates/yaml-sigil-transcription)

`compose` combines a document and its encoded signature information into a
YAML or protobuf artifact. `decompose` recovers the payload and
signature-carrier bytes. These operations are structural. They do not create
or verify a signature.

In a signing flow, `yaml-sigil-signing` uses transcription to assemble a YAML
artifact after creating its signature. During verification,
`yaml-sigil-verification` uses transcription to take a YAML or protobuf
artifact apart so it can read the signature information and check the
signature.

### [`yaml-sigil-signing`](./crates/yaml-sigil-signing/README.md)

[![yaml-sigil-signing on crates.io](https://img.shields.io/crates/v/yaml-sigil-signing.svg?label=yaml-sigil-signing)](https://crates.io/crates/yaml-sigil-signing)

Applications use this crate to turn a YAML or protobuf document into a signed
artifact. It prepares the document, creates the signature information with the
chosen signing key and algorithm, and packages the document and signature for
storage or transport.

Signing relies on `yaml-sigil-core` to apply the document rules and encode the
signature information. For YAML, it asks `yaml-sigil-transcription` to combine
the document and signature. For protobuf, it uses the core wire-format support.
The resulting artifact can be stored or transported for a recipient to process
with `yaml-sigil-verification`.

### [`yaml-sigil-verification`](./crates/yaml-sigil-verification/README.md)

[![yaml-sigil-verification on crates.io](https://img.shields.io/crates/v/yaml-sigil-verification.svg?label=yaml-sigil-verification)](https://crates.io/crates/yaml-sigil-verification)

Applications use this crate to check a signed artifact received from another
party. The application identifies the artifact as YAML or protobuf and
supplies the public keys it trusts. Verification then uses
`yaml-sigil-transcription` to take the artifact apart, uses `yaml-sigil-core`
to read it and enforce the document rules, and checks the signature.
`pre_verify` exposes the structural stage when you need to inspect an artifact
without performing cryptography.

Treat only the document bytes returned by `VerifierState::Verified` as
authenticated. The caller remains responsible for choosing the artifact form
and deciding which public keys are trusted.

### [`yaml-sigil-wasm`](./crates/yaml-sigil-wasm/README.md)

This crate exposes composition, decomposition, signing, and verification to
browser and Node.js WebAssembly consumers. Releases from `0.6.0-rc.1` include
its source package. The repository does not publish or retain generated
WebAssembly or an npm package. Select resource-aware operations to apply a
reusable artifact-size policy; the ordinary calls have no whole-artifact
limit.

### Signing and verification flow

1. A producer uses `yaml-sigil-signing` to sign a document.
2. Signing uses core document support and, for YAML, transcription to package
   the document and its signature as one artifact.
3. A recipient gives that artifact and its trusted public keys to
   `yaml-sigil-verification`.
4. Verification takes the artifact apart, checks that it follows the document
   rules, and reports whether its signature is valid for the document.

### Local cryptographic providers

Use RustCrypto convenience APIs or supply your own cryptographic provider.
Synchronous providers use a signing callback for each operation and
[`signature`](https://crates.io/crates/signature) 3.0 verification adapters.
Reuse signing adapters for that crate through `signature_signing_callback`.
Async operations use native provider traits. Your callback or adapter can
keep its private key or opaque handle in `ring`, `aws-lc-rs`, an HSM, or another
provider while YamlSigil handles payload preparation, artifact framing,
public-key checks, and verifier-state classification.

Signing builders validate canonical public-key bytes. Synchronous bindings
store only public material, and each operation receives its callback
separately. Async bindings also borrow their adapter. Qualified signing checks
every returned signature against the bound key and final payload, with no
synthetic signing request. Provider verification qualifies an exact adapter
instance with a bounded, public-only suite and tracks Ed25519 and P-256
independently. Explicitly named unqualified builders and operations are
available when a caller deliberately accepts the narrower assurance.

Direct `yaml-sigil-traits` implementations are also supported when you need
to own the complete operation. The [provider guide](./docs/crypto-providers.md)
explains the three choices, binding, async scheduling, optional limits, and
the tested and untested boundaries. Qualification offers narrower evidence
than complete conformance.

YamlSigil enforces the algorithm's public-key admissibility and signature
rules at this boundary. The provider remains responsible for private-key
generation quality, entropy, storage, access policy, and operational controls
that an opaque handle does not expose.

The provider boundary accepts message bytes and uses exactly 64 signature
octets. Prehashed input is unsupported. P-256 adapters apply SHA-256 once to
the supplied message bytes. Provider interoperability and qualification do not
establish or imply FIPS validation. That claim depends on the provider build,
configuration, platform, operational boundary, and deployment.

The runnable [`ring` and `aws-lc-rs` examples](./examples/README.md) implement
the public adapter traits, generate fresh Ed25519 or P-256 keys, and sign and
verify YAML artifacts. Both use `clap` and run their round-trip tests in CI.
The [`async-provider` example](./examples/async_provider.rs) signs and verifies
through a simulated P-256 service. It demonstrates awaitable key binding and
qualification, with both qualified and unqualified modes.

### Workspace-only support crates

- `yaml-sigil-conformance` exercises the implementation against the vendored
  fixture suite.
- `yaml-sigil-test-keys` provides deterministic key material for workspace
  tests. It is not a production key-management API.

### Choosing a document form

Callers select artifact forms through the public form enums. Bind each artifact
source, route, or storage class to one form before processing its bytes. Do not
sniff the bytes to select a form or retry the other form after structural or
verification failure. `v1alpha1` defines no magic bytes, media type, or required
file extension.

YAML decompose and verify operations require complete artifacts because
boundary selection uses the last constrained marker.

### Resource boundaries

YamlSigil `v1alpha1` defines no maximum complete YAML or protobuf artifact
size. The implementation crates expose one shared `ArtifactResourceLimits`
policy and explicit `_with_resource_limits` operations for complete artifact
inputs and outputs. `ArtifactResourceLimits::default()` selects
`DEFAULT_MAX_ARTIFACT_BYTES`. You can choose a lower ceiling, a higher ceiling,
or no additional byte limit.

```rust
use core::num::NonZeroUsize;
use yaml_sigil_core::v1alpha1::{
    ArtifactResourceLimits,
    pb::SignedYamlArtifactRef,
};

fn inspect(
    input: &[u8],
    limits: &ArtifactResourceLimits,
) -> Result<usize, Box<dyn std::error::Error>> {
    let artifact =
        SignedYamlArtifactRef::decode_with_resource_limits(input, limits)??;
    Ok(artifact.payload().len())
}

let default_limit = ArtifactResourceLimits::default();
let one_mib = ArtifactResourceLimits::unbounded()
    .with_max_artifact_bytes(NonZeroUsize::new(1024 * 1024).unwrap());
let thirty_two_mib = ArtifactResourceLimits::unbounded()
    .with_max_artifact_bytes(
        NonZeroUsize::new(32 * 1024 * 1024).unwrap(),
    );
let no_additional_limit = ArtifactResourceLimits::unbounded();
```

Resource-aware input operations check the original slice before parsing,
validation, copying, or cryptography. Resource-aware output operations perform
checked sizing before complete-output allocation. YAML signing uses a
conclusive lower bound for its earliest check and still checks the final exact
serialized size. A lower-bound rejection intentionally reports no exact output
size.

For an operation that produces protobuf through the raw outer composer, the
outer result reports resource rejection, a middle result preserves the
protobuf format error, and the existing operation return remains the inner
value. This keeps the selected resource ceiling ahead of the protobuf format
ceiling without changing portable trait outcomes.

The existing entry points remain unbounded by this optional policy. Merely
upgrading to a release that provides the bounded APIs does not remediate an
existing caller. Adopt a resource-aware operation at the affected trust
boundary, or establish that an equivalent earlier bound covers the original
raw input.

Protobuf format limits, parser safeguards, address-space limits, allocator
limits, and other deployment controls still apply. The existing 16,384-octet
YAML signature-carrier constraint is independent of complete artifact size.

A local whole-artifact rejection does not make an artifact malformed or
non-conforming, and whole-artifact limits do not change conformance results.

## Runnable examples

The [example index](./examples/README.md) links to runnable demonstrations and
their tests. The [GitHub key example](./examples/github-keys/README.md) signs
YAML and verifies it against public GitHub account keys or a supplied public key.

## Build

The development toolchain follows Rust `stable` through
`rust-toolchain.toml`. The minimum supported Rust version (MSRV) is Rust
`1.95.0`, as declared in the root `Cargo.toml`. Protobuf code generation uses
the Buf executable provided by the Cargo-resolved `buf-tools` build dependency.
Its minimum version requirement is declared in [Cargo.toml](Cargo.toml). A system
`buf` or `protoc` installation is not required. The first uncached build downloads
and verifies the corresponding official Buf release asset.

The root workspace publishes library crates and does not commit `Cargo.lock`.
Cargo may generate an ignored local lockfile while building or testing. The
standalone `xtask` helper keeps its own lockfile.

The complete developer validation commands appear at the end of this README.

Run the focused E2E fixture check with:

```shell
cargo test -p yaml-sigil-conformance --test e2e_buildtime_keys
```

### WebAssembly validation

Install the Rust 1.95 target and `wasm-pack` 0.15.x before running the local
source-only boundary validation. Node.js 20 or newer and Firefox must also be
on `PATH`.

```shell
rustup target add --toolchain 1.95.0 wasm32-unknown-unknown
cargo install --locked wasm-pack --version 0.15
cargo xtask wasm
```

The task checks the runtime crates and boundary for
`wasm32-unknown-unknown`, runs the schema-enabled suite under Node.js and
headless Firefox, and exercises the generated Node.js API. All generated
executable output stays in a temporary directory that the task removes before
returning. It also rejects any `.wasm` file retained in the workspace.

## Development checks

Run the full local validation gate or select checks while iterating:

```shell
cargo xtask check
cargo xtask check --only=fmt,clippy,test
cargo xtask check --exclude=audit
```

The registry runs in this order: `markdown`, `protobuf`, `fmt`, `versions`,
`package-content`, `check`, `clippy`, `test`, `downstream`, `machete`, `deny`,
and `audit`. It stops at the first failure. `cargo xtask ci` accepts the same
options and runs the same checks. Selectors are mutually exclusive, reject
unknown or empty selections, and run duplicate names only once in registry
order.

Compilation, tests, and coverage enable all workspace features by default. Use
`--features=json-schema-validate` or `--no-default-features` for a narrower
product build; those two flags may be combined. The separate xtask and
downstream fixture workspaces keep their own feature settings. Dependency
policy always checks all features, as configured in `deny.toml`.

## Coverage and profiling

Install the tools for the reports you need:

```shell
cargo install --locked cargo-llvm-cov
cargo install --locked cargo-tarpaulin
cargo install --locked samply
```

The selected task probes its required tool before doing other work. A missing
tool or a failed launch produces a diagnostic and an installation command.

Generate coverage with LLVM by default or choose Tarpaulin:

```shell
cargo xtask coverage
cargo xtask coverage --engine=tarpaulin
cargo xtask coverage --features=json-schema-validate --no-default-features
cargo xtask coverage --open
cargo xtask coverage-open --engine=tarpaulin
cargo xtask coverage-view
```

LLVM writes `target/llvm-cov-html/html/index.html`; Tarpaulin writes
`target/coverage/tarpaulin/tarpaulin-report.html`. Both `coverage --open` and
`coverage-open` generate a fresh report before opening it. Use
`coverage-view --engine=<ENGINE>` to open an existing report without rerunning
tests. Both generators accept the same feature options as `check`.

Tarpaulin uses `target/coverage/tarpaulin/build` for compilation so its cleanup
does not remove ordinary build outputs. Reports cover the root workspace;
Tarpaulin excludes the separate xtask and downstream fixture workspaces.

Record the focused E2E test with release-equivalent optimization and retained
debug symbols:

```shell
cargo xtask profile
cargo xtask profile --iterations 250
cargo xtask profile --open
cargo xtask profile-open
cargo xtask profile-view
```

The non-interactive default repeats the short E2E test 100 times and writes
Firefox Profiler data to `target/profile/profile.json`. Both `profile --open`
and `profile-open` record a fresh profile before launching Samply's browser
UI. Use `profile-view` to inspect a saved profile. Samply does not generate a
standalone HTML file. On Linux, the task reports the host's perf-event setting;
recording requires permission under the local system policy.

## Specification and conformance

The import task refreshes only the local artifacts this workspace owns.

```shell
cargo xtask update-spec
cargo xtask update-spec --ref origin/dev/example-branch
```

After reviewing a new specification revision, update the immutable
specification links in `crates/yaml-sigil-core/README.md` and
`crates/yaml-sigil-conformance/README.md`. Add a matching import review entry
to `docs/conformance-validation.md`, including when imported bytes and runtime
behavior remain unchanged. Update the same document whenever fixture plumbing,
expected outcomes, exposed behavior, or deliberate divergences change outside
an import.

## Release preparation

The release workflow publishes crates.io source packages for
`yaml-sigil-core`, `yaml-sigil-transcription`, `yaml-sigil-signing`,
`yaml-sigil-verification`, and, from `0.6.0-rc.1`, `yaml-sigil-wasm`. The
workspace default, conformance, test-key, and xtask packages remain
unpublished. Publication creates no executable artifacts or GitHub Release
assets.

Maintainers prepare one local, signed release pull request for an explicitly
selected version. See [`RELEASING.md`](RELEASING.md) for the complete
procedure. The typed preparation and non-publishing validation commands are:

```shell
cargo xtask release prepare --version MAJOR.MINOR.PATCH[-PRERELEASE] --base-ref refs/heads/main
cargo xtask release check --version MAJOR.MINOR.PATCH[-PRERELEASE] --base-ref refs/heads/main
```

## Developer validation

Run the complete CI sequence or its focused package-content check from the
workspace root. The per-crate list commands show the README, `LICENSE`, and
other files Cargo would place in each source package.

```shell
cargo xtask check
cargo xtask package-content
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-core
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-transcription
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-signing
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-verification
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-wasm
```

These checks do not upload anything. The package-content checks only list and
compare modeled source-package paths; full package assembly and publication
remain release-preparation operations.
