# yaml-sigil-core

`yaml-sigil-core` parses and encodes
[`yaml-sigil`](https://github.com/NVIDIA/yaml-sigil-spec#tldr) documents. It
supplies the shared document helpers used by the API crates.

Use this crate when you need decomposition, payload invariants, signature
document parsing, protobuf wire helpers, or schema validation. Most callers
should start with
[`yaml-sigil-signing`](https://crates.io/crates/yaml-sigil-signing),
[`yaml-sigil-verification`](https://crates.io/crates/yaml-sigil-verification),
or
[`yaml-sigil-transcription`](https://crates.io/crates/yaml-sigil-transcription)
unless they need these lower-level helpers directly.

## Select the contract

Use `yaml_sigil_core::v1alpha1` for explicit specification selection, including
`v1alpha1::pb` for the protobuf facade. The unqualified paths remain the
`v1alpha1` default and re-export the same definitions. Values work through
either path without conversion. The specification identifier is independent
of the crate's SemVer; optional operations keep their existing feature gates.

## What It Provides

- YAML artifact decomposition and payload validation.
- Backend-neutral YAML signature-document parsing and canonical serialization.
- Stable owned and borrowed protobuf `SignedYamlArtifact` helpers backed by
  private [`buffa`](https://crates.io/crates/buffa) generated code.
- Opt-in complete-artifact resource limits for YAML and protobuf boundaries.
- Algorithm mapping for the `yaml-sigil` wire and YAML names.
- Optional JSON Schema validation with the `json-schema-validate` feature.
- Optional P-256 provider-input conversions with the `p256-encoding` feature.

The public extension-trait contract lives in
[`yaml-sigil-traits`](https://crates.io/crates/yaml-sigil-traits). This crate
provides implementation support for the published API crates in this
workspace.

Code generation obtains a verified Buf executable from the Cargo-resolved
[`buf-tools`](https://crates.io/crates/buf-tools) build dependency and feeds its
descriptor set to [`buffa-build`](https://crates.io/crates/buffa-build).
The workspace manifest declares the minimum `buf-tools` version requirement.
Neither a system `buf` nor a system `protoc` installation is required.

## P-256 provider encodings

Enable `p256-encoding` to use `p256_der_signature_to_raw` and
`p256_public_key_to_uncompressed`. The first helper parses a strict DER
signature into 64 big-endian `r || s` octets without changing high-S or low-S
values. The second validates a 33-octet compressed or 65-octet uncompressed
public point from *Standards for Efficient Cryptography 1 (SEC 1)* and returns
the required 65-octet uncompressed encoding.

Both helpers return fixed-size arrays or `P256EncodingError`. They delegate
encoding and point validation to RustCrypto and do not verify a signature
against a message. Malformed inputs, out-of-range signature components,
invalid points, and unsupported encodings are rejected. See the
[compiling examples and error contracts](https://docs.rs/yaml-sigil-core/latest/yaml_sigil_core/p256_encoding/index.html).

The feature is disabled by default for core-only consumers. The signing and
verification crates enable it and re-export the same helpers. Convert provider
bytes before building a key or returning a signature; algorithm boundaries
continue to require raw signatures and uncompressed public keys.

## YAML and Serde boundary

`SignatureDocument` and its Serde implementations form the stable public
data-model boundary. Concrete YAML dependencies remain implementation details.
The backend uses [`noyalib`](https://crates.io/crates/noyalib). Consumers can
select their own `noyalib` release or use another
Serde-compatible format or library when it represents the documented field
contract. This architectural boundary does not imply that independent YAML
backends accept or emit the same YAML.

Use `parse_signature_document` as the authoritative entry point for untrusted
YAML signature carriers. Direct Serde deserialization constructs the data model
without applying YamlSigil's YAML byte limit or parser resource budgets. It
also bypasses the document-count policy and the policies for duplicate keys,
merge keys, anchors, and tags.

Serde compatibility covers semantic values. It does not promise identical YAML
acceptance, resource policy, comments, scalar style, field order, or bytes
across backends. Use `serialize_signature_document` for canonical YAML output.
Retain the original carrier bytes when forwarding must preserve presentation or
byte identity. The text inside `CoreError::SignatureYaml` is an unstable
diagnostic intended for people. Do not parse it as a machine-readable interface.

The exact-pinned downstream fixture characterizes interoperability between
`noyalib` releases `0.0.53` and `0.0.57`. This same-library, cross-version test
does not establish cross-backend YAML portability or a permanent support
guarantee for either release.

## Protobuf facade

The public `pb` module exposes opaque owned messages and zero-copy borrowed
views. Only `yaml-sigil-core` depends on Buffa directly. Consumers using a
different protobuf implementation or Buffa release exchange encoded bytes
with the facade instead of sharing generated Rust types.

```rust
use yaml_sigil_core::v1alpha1::{
    AlgorithmId,
    pb::{SignedYamlArtifact, SignedYamlArtifactRef, YamlSigilSignature},
};

let signature =
    YamlSigilSignature::new(AlgorithmId::Ed25519, vec![1, 2, 3]);
let artifact =
    SignedYamlArtifact::new(b"message\n".to_vec(), Some(signature));

let mut wire = Vec::with_capacity(artifact.encoded_len().unwrap());
artifact.encode_into(&mut wire).unwrap();

let decoded = SignedYamlArtifactRef::decode(&wire).unwrap();
assert_eq!(decoded.payload(), b"message\n");
```

Borrowed payload, `keyid`, and signature accessors point into the input. Use
`to_owned` when data must outlive that input. Owned decode and re-encode retain
unknown fields and raw unknown algorithm numbers. Call
`discard_unknown_fields` to remove retained unknown data explicitly.

`DecodeError` and `EncodeError` expose non-exhaustive category enums through
`kind`. Their fields remain private, and their `Debug` and `Display` output
does not retain or print payload, signature, carrier, or unknown-field bytes.
Include a wildcard arm when matching an error category.

Construct messages with `SignedYamlArtifact::new` and
`YamlSigilSignature::new`, then update them through their mutation methods.
Decode and encode with the facade's `decode`, `encoded_len`, `encode_to_vec`,
and `encode_into` methods. All encode methods are fallible. Use `AlgorithmId`
for recognized values and `algorithm_wire_value` when forwarding an unknown
protobuf enum number.

## Resource boundaries

YamlSigil `v1alpha1` defines no maximum complete artifact size.
`ArtifactResourceLimits` provides an implementation-local, explicitly selected
policy. `DEFAULT_MAX_ARTIFACT_BYTES` defines its default ceiling. Use
`NonZeroUsize` with `with_max_artifact_bytes` to select another finite value,
or use `unbounded` to disable every optional resource dimension known to this
crate version.

The complete-artifact core helpers and the owned and borrowed
`SignedYamlArtifact` facades provide `_with_resource_limits` variants. Bounded
decode checks the original wire slice before Buffa processing. Bounded encode
uses one checked wire traversal for exact sizing and emission, including
retained unknown fields and nested groups. It applies resource policy before
the protobuf format ceiling and before allocation. A failed bounded
`encode_into` leaves the reusable destination unchanged.

Raw outer composition also preserves that order. Its outer result reports
resource rejection, and an admitted protobuf format rejection remains an inner
`pb::EncodeError`. Implementation crates that project a raw message from
component lengths use `pb::check_encoded_message_size` after applying the
selected resource policy.

Existing helpers remain unbounded by this policy. Adopt a bounded entry point
at the affected trust boundary, or enforce an equivalent earlier bound on the
original raw input. The existing 16,384-octet YAML signature-carrier
constraint is separate from complete artifact size. Protobuf format limits,
parser safeguards, address-space limits, allocator limits, and deployment
controls still apply.

Whole-artifact limits do not affect conformance results. Rejecting an artifact
under a local resource policy does not make it malformed or non-conforming.

## The Signature Document

The YAML form uses the fixed `YamlSigilSignature.v1alpha1` schema discriminator.
Its optional `keyid` is nonempty when present, contains no carriage return or
line feed, and is at most 1,024 UTF-8 octets. Its `signature` is an RFC 4648
section 5 URL-safe base64 value without padding. The protobuf form identifies
the schema through its message type and carries the signature as raw octets.

The YAML and protobuf algorithm identifiers map as follows:

| Wire value | YAML identifier | Protobuf identifier |
|-----------:|-----------------|---------------------|
| 1 | `ED25519_PUREEDDSA_RAW_RS64_CANONICAL` | `ALGORITHM_ED25519_PUREEDDSA_RAW_RS64_CANONICAL` |
| 2 | `ECDSA_SECP256R1_SHA256_RAW_RS64` | `ALGORITHM_ECDSA_SECP256R1_SHA256_RAW_RS64` |

Protobuf wire value `0`, `ALGORITHM_UNSPECIFIED`, is invalid. Read the
`yaml-sigil` specification for the complete
[signature-document semantics](https://github.com/NVIDIA/yaml-sigil-spec/blob/30b143f09630448abbace14cfae2188279536f56/README.md#the-signature-document)
and
[base64 requirements](https://github.com/NVIDIA/yaml-sigil-spec/blob/30b143f09630448abbace14cfae2188279536f56/base64-requirements.md).

## Third-party material

The crate source archive includes
[`THIRD_PARTY_NOTICES.md`](https://github.com/NVIDIA/yaml-sigil-rs/blob/main/crates/yaml-sigil-core/THIRD_PARTY_NOTICES.md),
which records the current scope, attribution, source terms, disclaimers,
intellectual-property caveats, and non-endorsement language for identified
third-party material.
