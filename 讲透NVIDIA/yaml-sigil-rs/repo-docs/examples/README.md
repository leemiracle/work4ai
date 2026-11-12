# Examples

Runnable examples demonstrate the public `yaml-sigil` APIs. Run the commands
below from the repository root.

Examples select each implementation crate's `v1alpha1` namespace explicitly.
The unqualified APIs remain compatible defaults and use the same types,
traits, and specification behavior. Crate SemVer is independent of this
specification identifier.

## Example index

| Example | Demonstrates |
|---------|--------------|
| [`ring_provider.rs`](./ring_provider.rs) | Native `ring` signing and verification adapters. |
| [`aws_lc_provider.rs`](./aws_lc_provider.rs) | Native `aws-lc-rs` signing and verification adapters. |
| [`ring_unqualified_provider.rs`](./ring_unqualified_provider.rs) | Explicitly unqualified `ring` signing and verification, with implementer-owned compatibility risk. |
| [`async_provider.rs`](./async_provider.rs) | Awaitable P-256 signing and verification through a simulated service, including key binding and qualification. |
| [`github-keys`](./github-keys/README.md) | Ed25519 signing and local verification with agent identities, an explicit public key, or GitHub discovery. |
| [`yaml_facade.rs`](./yaml_facade.rs) | YAML signature-document parsing and serialization through the core facade. |
| [`protobuf_facade.rs`](./protobuf_facade.rs) | Core protobuf encoding, owned and borrowed decoding, and wire interoperability with Prost. |

## Serialization facades

These commands use built-in data and take no arguments. `yaml-facade` prints
a canonical YAML signature carrier after checking its semantic round trip.
`protobuf-facade` checks core encoding and decoding, then exchanges protobuf
bytes in both directions with Prost and prints each result. Signature values
in both examples are illustrative; the examples perform no cryptography.

```shell
cargo run --package yaml-sigil-examples --example yaml-facade
cargo run --package yaml-sigil-examples --example protobuf-facade
```

The YAML flow uses the core API without directly importing a YAML backend.
The protobuf flow adds `prost` `0.14.4` as an example development dependency
and uses annotated application types without adding a code generator.
Neither example directly imports Buffa or Noyalib. The guides explain the
[YAML data-model boundary](../docs/yaml-facade.md) and
[protobuf wire boundary](../docs/protobuf-facade.md).

Both targets have `test = true`, so workspace CI runs their round-trip tests.
The tests cover optional `keyid`, YAML quoting, binary protobuf payloads, and
both Prost interoperability directions. Run them with these commands.

```shell
cargo test --package yaml-sigil-examples --example yaml-facade
cargo test --package yaml-sigil-examples --example protobuf-facade
```

## GitHub account keys

The [`github-keys` example](./github-keys/README.md) signs through an SSH agent
with a qualified asynchronous provider and verifies locally with public keys.
Omit `--signer` to use supported agent identities, or restrict keys to a GitHub
username or explicit OpenSSH public key. Both commands accept
`--key-fingerprint`. The [numbered walkthrough](./github-keys/README.md#walkthrough)
builds the executable once, creates and loads a protected demo key, signs and
verifies offline, then adds GitHub discovery. Remove the demo registration
through GitHub's settings page afterward. Generated documents stay under
`target/github-keys-demo/`.

You can verify the published fixture without an agent or GitHub access.

```shell
cargo build --package yaml-sigil-examples --example github-keys
target/debug/examples/github-keys verify \
  --signer "$(cat examples/github-keys/fixtures/ddurst-nvidia.pub-key)" \
  --input examples/github-keys/fixtures/signed.yaml
```

Both commands accept file, URL, or standard input with a 4 MiB document limit.
Signing prints artifact bytes to stdout and progress to stderr. Verification
lists public agent identities when no signer is supplied and never requests
a signature. Explicit-signer verification needs no agent. Workspace CI runs
the offline HTTP and agent tests. The example README also documents an
optional isolated OpenSSH test.

## Shared modules

The [`cli-common` module](./cli-common/mod.rs) contains shared CLI helpers.
It defines the local provider examples' `clap` interface and connects input
handling to YamlSigil operations. It also formats output and supplies test
helpers.
The [`yaml_io` helpers](./cli-common/yaml_io.rs) share YAML file, standard-input,
and default-document handling and transcript output across the provider examples.
The [`key_type` module](./cli-common/key_type.rs) supplies key selection for
examples offering both algorithms. The two `ring` examples share
[native keys and adapters](./cli-common/ring.rs), while selecting their own
qualified or unqualified operations.

## Local cryptographic providers

The `ring-provider` and `aws-lc-provider` commands sign a YAML document with a
fresh random key, then verify the artifact through public provider adapters.
[`cli-common/ring.rs`](./cli-common/ring.rs) and
[`aws_lc_provider.rs`](./aws_lc_provider.rs) contain the native cryptographic
operations and key bindings, with comments explaining each layer's contract.
The options and behavior below apply to both commands.

These examples use synchronous providers. Wrapping their calls in an async
function still runs the native cryptography synchronously. They do not
implement `AsyncProviderSigner` or `AsyncProviderVerifier`, and they have no
awaitable factory. Use the async example below for that integration contract.
The [provider guide](../docs/crypto-providers.md) describes the three supported
integration choices and their tested boundaries.

```shell
cargo run --package yaml-sigil-examples --example ring-provider
cargo run --package yaml-sigil-examples --example aws-lc-provider
```

### Input and key selection

Both commands accept the same options.

| Option | Behavior |
|--------|----------|
| `--key-type p256` | Generate an ECDSA P-256 key and use SHA-256. This is the default. |
| `--key-type ed25519` | Generate an Ed25519 key. Native verification uses the explicitly unqualified path described below. |
| `--payload FILE` | Read the unsigned YAML document from a UTF-8 file. |
| `--payload stdin` | Read the unsigned YAML document from standard input through EOF. |
| `--help` | Show command usage. |

`--payload` takes a filename or the literal `stdin`, rather than inline YAML.
Use `./stdin` to name a file whose basename is `stdin`. Omitting the option
uses a document that explicitly identifies itself as the default. YAML signing
appends a final newline when the input needs one.

```shell
cargo run --package yaml-sigil-examples --example ring-provider -- \
  --key-type ed25519 --payload document.yaml
cargo run --package yaml-sigil-examples --example aws-lc-provider -- \
  --key-type p256 --payload stdin < document.yaml
```

### Output

Both commands print these stages, with a `====== Title ======` heading before
each stage and YAML below it.

1. The unsigned document, labeled as default, file, or standard input.
2. The provider, key type, and generated public key encoded as base64.
3. The verification result and whether provider verification is qualified.
4. The complete signed YAML artifact.

The headings delimit a terminal transcript. They are distinct from YAML
comments and document markers; the complete transcript is not one YAML stream.
Copy only the body after `====== Signed YAML artifact ======` to obtain the
artifact. The command prints the returned artifact without reserializing it.
Private keys remain inside the process and are never printed.

### Provider behavior

The adapters implement `signature::Signer<[u8; 64]>`,
`signature::Verifier<[u8; 64]>`, `ProviderVerifier`, and
`ProviderVerifierFactory`. They pass the final message bytes unchanged to the
provider and use fixed-width signatures. Each verifier owns its public-key
bytes, preserving its binding when the factory creates another verifier.

Both algorithms use qualified signing, which self-verifies every signature
before returning an artifact. P-256 verification requires successful provider
qualification. The pinned libraries' Ed25519 verifiers reject some mixed-order
signatures accepted by YamlSigil, so their Ed25519 slots cannot qualify.
Selecting Ed25519 explicitly uses unqualified native verification for this
generated-key demonstration. It still checks signatures and retains structural
validation. The output labels that path and its limitation; a successful round
trip does not qualify the provider. Neither path retries a verification failure.

Both native signing examples validate public bytes with the builder, then
borrow their `signature` adapter through `signature_signing_callback` for each
operation. The binding stores no private-key handle. See the
[provider guide](../docs/crypto-providers.md#synchronous-signing-calls)
for public-key binding and callback usage.

The `aws-lc-rs` example uses the same pinned `non-fips` build as the workspace's
provider tests. This choice avoids FIPS-specific build-tool and platform
requirements while demonstrating the adapter contracts. These examples
demonstrate interoperability; they make no FIPS validation claim.

On Windows x86-64, the development dependencies enable `prebuilt-nasm` so
`aws-lc-rs` can use its bundled assembly objects when NASM is absent. An
installed NASM still takes precedence. This keeps both examples available on
the Windows CI runner. See the provider's
[Windows build requirements](https://aws.github.io/aws-lc-rs/requirements/windows.html#prebuilt-nasm-objects).

### Tests

The unpublished `yaml-sigil-examples` workspace member registers both example
targets with `test = true`. `cargo xtask check` compiles
them during all-target Clippy and executes their tests during
`cargo test --workspace --all-features`.

Each target tests its `clap` command and both key types. Round trips cover the
default document and inputs from files or stdin. The tests exercise the same
operation as the CLI, then verify the printed artifact using the printed
public key. Run only these tests with the following command.

```shell
cargo test --package yaml-sigil-examples
```

## Explicitly unqualified provider

> [!WARNING]
> The `ring-unqualified-provider` example skips independent signing output
> self-verification and the fixed verification-provider qualification suite.
> You, the integration implementer, own the additional risk and the assessment
> of whether its cryptographic behavior meets your requirements. A native
> round trip does not establish YamlSigil compatibility.

[`ring_unqualified_provider.rs`](./ring_unqualified_provider.rs) calls the
unqualified builders directly from its entry point and uses the unqualified
signing and verification operations. It supports P-256 and Ed25519 and generates
a fresh random key on each run. The native adapters come from
[`cli-common/ring.rs`](./cli-common/ring.rs). Neither the operation nor its
tests require qualification, and it never retries through another path.
Its signing call also supplies a per-operation forwarding callback while
retaining the explicitly unqualified output checks.

```shell
cargo run --package yaml-sigil-examples --example ring-unqualified-provider
cargo run --package yaml-sigil-examples --example ring-unqualified-provider -- \
  --key-type ed25519 --payload document.yaml
cargo run --package yaml-sigil-examples --example ring-unqualified-provider -- \
  --key-type p256 --payload stdin < document.yaml
```

The key and payload options follow the
[local examples' input conventions](#input-and-key-selection). P-256 is the
default. Both key choices use unqualified signing and verification. Omitting
`--payload` selects the labeled default YAML document. The command prints a
warning stage first, then the unsigned document, public key and type,
verification result, and final signed YAML artifact. All five stages use
`====== Title ======` separators. The full transcript is not one YAML stream.

Unqualified operations still validate canonical admissible public keys,
signature structure, and artifacts. They still call `ring` to sign and
verify. Structural checks cannot detect a validly encoded signature for the
wrong message or key, so unqualified signing can return such an artifact.
Verification uses the native provider's verdict without an independent
cryptographic check. In particular, the pinned `ring` verifier rejects some
mixed-order Ed25519 signatures that YamlSigil accepts. Decide whether that
difference is acceptable for your integration; running this example does
not resolve it. The [provider guide](../docs/crypto-providers.md) describes
the three supported paths and the evidence needed for a conformance claim.

Workspace CI compiles this target and tests its parser and both key types.
Round trips cover the default document and inputs from files or stdin. The
tests independently verify the printed artifact with its printed public key
through the RustCrypto convenience API. That checks these generated samples and
the example's wiring; it does not qualify the adapter or cover every possible
input.
Run these tests with `cargo test --package yaml-sigil-examples`.

## Asynchronous provider

The `async-provider` command signs and verifies a YAML document using a fresh
P-256 key generated inside a simulated service worker. It implements
`AsyncProviderSigner`, `AsyncProviderVerifier`, and
`AsyncProviderVerifierFactory`, then uses the provider-backed `AsyncSigner`
and `AsyncVerifier` facades. The factory and its handles borrow a client.

```shell
cargo run --package yaml-sigil-examples --example async-provider
cargo run --package yaml-sigil-examples --example async-provider -- \
  --provider-mode unqualified --payload document.yaml
cargo run --package yaml-sigil-examples --example async-provider -- \
  --payload stdin < document.yaml
```

| Option | Behavior |
|--------|----------|
| `--provider-mode qualified` | Self-verify signing outputs and qualify verification before binding the application key. This is the default. |
| `--provider-mode unqualified` | Explicitly skip those additional checks for both operations. Structural checks remain. |
| `--payload FILE` or `--payload stdin` | Read unsigned YAML from the selected source. Omit for the labeled default document. |
| `--help` | Show command usage. |

This example supports only P-256. It shares the local examples' four output
stages, base64 public-key display, final signed YAML artifact, and
`====== Title ======` transcript separators. The result explicitly labels
both signing and verification as qualified or unqualified. It never prints
the private key.

The worker uses `p256` message operations with randomized signing and receives
requests over a bounded channel. Adapters await replies, so the current-thread
Tokio runtime can make progress while the worker performs cryptography. The
worker simulates a service; it requires no credentials or external connection.
A production HSM, KMS, or network client needs its own adapter. Queue capacity does
not bound payload size, and dropping an awaiting request does not undo work
already accepted by the worker. A real adapter owns SDK scheduling, deadlines,
remote cancellation, concurrency, and retry policy.

The target has `test = true`, so workspace CI compiles it with Clippy and runs
its tests. These cover the parser and round trips in both provider modes,
using the default document and inputs from files or stdin. Tests independently
verify the printed artifact using the printed public key. The command
`cargo test --package yaml-sigil-examples` runs these tests together with the
native provider examples.
