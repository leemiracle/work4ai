# yaml-sigil-transcription

`yaml-sigil-transcription` composes
[`yaml-sigil`](https://github.com/NVIDIA/yaml-sigil-spec#tldr) artifacts from
document and signature components. It also decomposes artifacts into those
components. Both operations support YAML and protobuf forms.

In the API, the document bytes are the `payload` and the encoded signature
component is the `signature_carrier`. `compose` joins them into an artifact,
while `decompose` recovers the payload and signature-carrier bytes. These
operations change document structure only. They do not verify a signature or
authenticate the payload. Use
[`yaml-sigil-verification`](https://crates.io/crates/yaml-sigil-verification)
for signature verification.

YAML composition requires payload bytes that form a valid UTF-8 stream without
a BOM and with a final line terminator when non-empty. Protobuf composition
treats payload bytes as opaque and preserves every accepted byte unchanged.

## Select the contract

Use `yaml_sigil_transcription::v1alpha1` for explicit specification selection.
The unqualified paths remain the `v1alpha1` default and name the same traits,
requests, results, and implementations. Values work through either path
without conversion. The specification identifier is independent of the
crate's SemVer.

## API Surface

- `compose` and `decompose` perform the byte operations.
- `compose_with_resource_limits` and `decompose_with_resource_limits` apply an
  explicit complete-artifact policy.
- `EncodeError` and `EncodeErrorKind` re-export the common protobuf format
  error used by resource-aware protobuf composition.
- `DefaultTranscriber` and `DefaultAsyncTranscriber` delegate to the free
  functions.
- `Transcriber`, `AsyncTranscriber`, request types, response types, and
  capability types are re-exported from
  [`yaml-sigil-traits`](https://crates.io/crates/yaml-sigil-traits).

This crate does not provide RPC transport. Consumers that need a service
boundary should wire the trait API into their own deployment.

## Resource boundaries

`compose_with_resource_limits` validates the request shape, computes the exact
YAML or protobuf output size with checked arithmetic, and applies the policy
before component scans and complete-output allocation. The outer result reports
resource rejection, and the inner result preserves a protobuf format error
when the selected form is protobuf. The existing `ComposeOutcome` remains the
admitted value.
`decompose_with_resource_limits` checks the original complete input before
form, outer-conformance, or artifact processing. Resource errors remain
separate from transcription outcomes.

`ArtifactResourceLimits::default()` selects `DEFAULT_MAX_ARTIFACT_BYTES`. You
can lower, raise, or disable that ceiling. Existing `compose`, `decompose`, and
default trait implementations remain unbounded by this policy. Callers must
adopt the bounded operations at the affected trust boundary or enforce an
equivalent earlier raw-input bound.

YamlSigil `v1alpha1` defines no maximum complete artifact size. These limits
are operational hardening and do not affect conformance results. The existing
16,384-octet YAML signature-carrier constraint remains separate and applies
where signature metadata is parsed.
