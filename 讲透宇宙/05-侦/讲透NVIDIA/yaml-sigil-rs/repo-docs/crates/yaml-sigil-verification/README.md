# yaml-sigil-verification

`yaml-sigil-verification` verifies
[`yaml-sigil`](https://github.com/NVIDIA/yaml-sigil-spec#tldr) documents and
their signatures in YAML and protobuf forms.

Use this crate to check document structure, verify Ed25519 or ECDSA P-256
SHA-256 signatures, and retrieve payload bytes only after successful
verification. The result identifies the applicable `yaml-sigil` verifier state.

## Select the contract

Use `yaml_sigil_verification::v1alpha1` for explicit specification selection,
including provider modules and resource-aware operations. The unqualified
paths remain the `v1alpha1` default and name the same traits, key bindings,
results, and implementations. Values work through either path without
conversion. The specification identifier is independent of the crate's SemVer.

## API Surface

- `verify`, `verify_yaml`, and `verify_proto` run verification.
- Their `_with_resource_limits` variants apply an explicit complete-input
  policy before verification work.
- `pre_verify`, `pre_verify_yaml`, and `pre_verify_proto` run structural checks
  without cryptography.
- Their `_with_resource_limits` variants and
  `can_pre_verify_with_resource_limits` check the original encoded input.
- `verify_from_pre_verify` and its form-specific helpers reuse successful
  pre-verification results.
- `VerificationProviderBuilder` either qualifies one exact synchronous
  provider instance or constructs an explicitly unqualified provider.
- `verify_with_provider` and its metadata and pre-verification
  variants retain YamlSigil artifact handling around qualified provider keys.
- The corresponding `verify_with_unqualified_provider` functions make the
  qualification bypass explicit.
- `AsyncProviderVerifierFactory` and `AsyncProviderVerifier` support awaitable
  binding and verification. `AsyncVerificationProviderBuilder` offers async
  qualification and an explicitly unqualified builder.
- `ProviderAsyncVerifier` and `UnqualifiedProviderAsyncVerifier` implement
  `AsyncVerifier` with the corresponding bound keys. Async free functions also
  expose metadata and pre-verification reuse.
- `DefaultVerifier` and `DefaultAsyncVerifier` delegate to the free functions.
- `Verifier`, `AsyncVerifier`, result types, and capability types are
  re-exported from
  [`yaml-sigil-traits`](https://crates.io/crates/yaml-sigil-traits).
- `PublicKeys` accepts verifying keys from
  [`ed25519-dalek`](https://crates.io/crates/ed25519-dalek) and
  [`p256`](https://crates.io/crates/p256).
- `resolve_ed25519_verifying_key` and `resolve_p256_verifying_key` turn raw
  public-key bytes into those key types.

`PublicKeys` contains caller-supplied verification keys indexed by algorithm.
The artifact's unsigned `keyid` remains a deployment-specific lookup hint.
The shared traits leave key parsing to each implementation. This crate applies
its Ed25519 key-admissibility checks both when it resolves raw key bytes and
when a caller supplies an already constructed typed key.

`resolve_p256_verifying_key` accepts only the 65-byte uncompressed
`0x04 || X || Y` encoding from
*Standards for Efficient Cryptography 1 (SEC 1)*.

Bind each artifact source, route, or storage class to one `ArtifactForm` before
calling the verifier. Do not infer the form from artifact bytes or retry the
other form after structural or verification failure.

Only payload bytes returned by `VerifierState::Verified` are authenticated. A
signature document inside those bytes remains payload content.

## Local provider verification

`p256_der_signature_to_raw` converts strict DER signatures to 64-octet raw
`r || s` without changing high-S or low-S values.
`p256_public_key_to_uncompressed` validates compressed or uncompressed public
points and returns the required 65-octet uncompressed form. Both helpers return
`P256EncodingError` on invalid input. They are re-exported from
[`yaml-sigil-core`](https://crates.io/crates/yaml-sigil-core); see its
[encoding contracts and compiling examples](https://docs.rs/yaml-sigil-core/latest/yaml_sigil_core/p256_encoding/index.html).
Use them before the algorithm boundary. Verification does not automatically
convert DER signatures or compressed keys found in an artifact or provider
binding.

Add a direct dependency on
[`signature`](https://crates.io/crates/signature) 3.0. Implement
`signature::Verifier<[u8; 64]>` and `ProviderVerifier` for your bound provider
handle, then implement `ProviderVerifierFactory` for the type that creates
those handles. All three traits are public extension contracts. Keep each
handle bound to its own key even when the factory binds another key.

Follow the
[compiling adapter example](https://docs.rs/yaml-sigil-verification/latest/yaml_sigil_verification/provider/index.html#implement-a-verification-adapter)
through trait implementation, qualification, key binding, and
`verify_with_provider`. The provider traits and key types are re-exported at
the crate root and available in its public `provider` module. Bound keys are
opaque inputs to these artifact operations. Implementing the separate
`yaml_sigil_traits::verification::Verifier` contract means supplying the
complete operation, including artifact processing.

For complete `clap` commands using fresh Ed25519 or P-256 keys, see the
[`ring` and `aws-lc-rs` examples](https://github.com/NVIDIA/yaml-sigil-rs/tree/main/examples).
Both sign and verify YAML artifacts and execute round-trip tests in CI.
They demonstrate synchronous operations. The
[`async-provider` example](https://github.com/NVIDIA/yaml-sigil-rs/blob/main/examples/async_provider.rs)
demonstrates awaitable operations through a simulated service. The
[provider guide](https://github.com/NVIDIA/yaml-sigil-rs/blob/main/docs/crypto-providers.md)
describes the checks and tests for each integration choice. It covers qualified
and explicitly unqualified adapters as well as direct trait implementations.
Qualification offers narrower evidence than complete conformance.

Implement `ProviderVerifierFactory` to bind canonical public-key bytes to an
opaque local provider handle. Ed25519 keys use 32 canonical compressed octets.
P-256 keys use the 65-octet uncompressed encoding from
*Standards for Efficient Cryptography 1 (SEC 1)*. YamlSigil validates the key
before asking the factory to bind it and rejects malformed 64-octet
signatures before provider verification.

Bound `ProviderVerifier` handles must implement `Send + Sync`. Both qualified
and unqualified bound keys preserve those guarantees, so you can move or share
them across worker threads. Adapters with mutable state synchronize it
internally.

`VerificationProviderBuilder::qualify` runs a bounded, public-only fixed suite
once for the exact adapter instance it consumes. It records independent
Ed25519 and P-256 status. A rejected slot cannot create a qualified key, but it
does not disable another slot. Replacing or reconfiguring the adapter requires
qualification again. Finite qualification shows that the instance passes the
included suite; it is not proof for every possible input or future
configuration.

Both algorithm suites keep distinct key bindings live and interleave valid
signatures with cross-key rejection checks in both directions. They reject
common adapter mistakes such as caching the first key or retargeting an
existing handle when another key is bound. Keep each handle's key state or
stable key identifier separate, even when handles share a client.

The adapter remains trusted code. Qualification does not defend against an
implementation deliberately written to pass the fixed suite and misbehave
on other inputs.

Qualified results are authoritative. YamlSigil does not retry a provider
mismatch through RustCrypto. Implementations that can distinguish an
operational failure from a signature mismatch override
`ProviderVerifier::verify_provider`; YamlSigil keeps those outcomes separate.
`build_unqualified` and the explicitly named unqualified operations skip the
fixed suite while retaining YamlSigil's key and signature-structure checks.

The provider receives the exact extracted payload and a raw 64-octet
signature. P-256 adapters verify SHA-256 over those message bytes and accept
big-endian `r || s`, not DER. The development matrix exercises RustCrypto,
`ring`, and `aws-lc-rs` adapters. Provider support or qualification does not
establish or imply FIPS validation.

To bound provider verification, admit the original artifact with
`ArtifactResourceLimits::check_input_size` before calling a provider operation.
A bounded pre-verification response can also be passed to
`verify_from_pre_verify_with_provider`. Use the same admission and reuse with
async or explicitly unqualified variants. Admit the original input before any
artifact-dependent remote work.

Async binding can suspend and return a handle that borrows its factory or
client without a `'static` requirement. It cannot retain a borrow of the
temporary public-key input. Qualification awaits the same finite public suite
as sync qualification. Parsing and structural checks remain synchronous, and
verification awaits the adapter's classified result. The library selects no
runtime, timeout, retry, or remote cancellation policy. The guide explains
these scheduling boundaries and the difference from `DefaultAsyncVerifier`.

## Resource boundaries

Resource-aware verification, pre-verification, and the boolean summary check
the original complete input before form options, parsing, copying, or
cryptography. Their outer `ArtifactResourceResult` reports resource admission;
the inner result or verifier state preserves the existing contract.

Bounded pre-verification enforces complete-input size once while the original
encoded artifact is available. Continue with the existing
`verify_from_pre_verify` functions. They receive in-memory components and do
not reconstruct or recheck an encoded artifact.

YamlSigil `v1alpha1` defines no maximum complete artifact size. A local
resource-policy rejection remains separate from invocation errors, malformed
artifacts, failed cryptographic verification, and conformance results. A
deployment can choose a lower limit, a higher limit, or no additional limit;
`DEFAULT_MAX_ARTIFACT_BYTES` defines the explicit default. Existing
verification entry points and default trait implementations remain unbounded
by this policy. Adopt a bounded operation at the affected trust boundary or
enforce an equivalent earlier raw-input bound. Protobuf format limits, parser
safeguards, address-space limits, allocator limits, and deployment controls
still apply.

## YAML Signature-Document Behavior

The verifier advertises `AdvertisedConformanceProfile::Permissive`. Its YAML
decoder rejects duplicate known mapping keys under every profile and returns
`MalformedAttemptedSigned`; it does not select an effective value from
duplicate occurrences. The decoder also rejects unknown top-level fields,
which is stricter than the `Permissive` requirement.

Before parsing an unauthenticated YAML signature carrier, the verifier applies
these implementation-specific hard bounds:

| Parser dimension | Bound |
|------------------|------:|
| Markerless carrier bytes | 16,384 |
| Nesting depth | 16 |
| Alias expansions | 0 |
| Mapping keys | 8 |
| Sequence length | 16 |
| Parser events | 128 |
| Constructed nodes | 64 |
| Cumulative scalar bytes | 8,192 |
| Documents | 1 |
| Merge keys | 8 |

The parser rejects anchors, aliases, custom tags, and duplicate keys. These
values describe this Rust implementation; they are not portable `yaml-sigil`
limits except for the 16,384-octet markerless carrier limit. That carrier
constraint is independent of complete artifact size.

The verifier exposes parser observations when callers request them. It does not
provide RPC transport.

## Third-party material

NVIDIA-authored crate material is licensed under Apache-2.0. RFC 8032-derived
point-encoding and verification rules and a section 7.1 test-vector value in
`src/crypto.rs` retain their source attribution and terms. The qualification
vectors in `src/provider.rs` also retain their source attribution and terms.
The P-256 resolver and qualification public key follow point-encoding behavior
from *Standards for Efficient Cryptography 1 (SEC 1)*. The applicable notices
and source terms are retained in
[`THIRD_PARTY_NOTICES.md`](https://github.com/NVIDIA/yaml-sigil-rs/blob/main/crates/yaml-sigil-verification/THIRD_PARTY_NOTICES.md).
