# Conformance validation

This document records how `yaml-sigil-rs` uses its local conformance fixture
tree:

```text
crates/yaml-sigil-conformance/fixtures/
```

The fixture tree is a curated import of the spec conformance artifacts used by
this Rust implementation. It intentionally omits upstream rebuild generators
and vendor data. Spec changes are reviewed separately, then fixture artifacts
are imported here only when this implementation needs them.

Every conformance-related change must update this document in the same commit.
That includes fixture imports, fixture removals, fixture-to-API remapping,
expected outcome changes, ignored tests, API additions discovered through a
fixture, and deliberate divergences.

## Namespace compatibility

Each published implementation crate exposes `v1alpha1` alongside the
unqualified default. Re-exports preserve type and trait identity, including
the selected `yaml-sigil-traits` contract and optional feature gates.
`crates/yaml-sigil-conformance/tests/conformance_default.rs` runs the existing
sync and async suites through namespaced default implementations. The smoke
suites retain unqualified imports. Fixture bytes, expected outcomes,
algorithm profiles, imported artifacts, and wire behavior are unchanged.

`tests/downstream/v1alpha1-api` passes requests, key bindings, results,
resource policies, owned protobuf values, and borrowed views between both
styles. It also uses the selected traits directly and checks provider signing
and YAML serialization. The fixture uses the workspace's `~0.4.1` requirement
and checks that direct and re-exported traits retain the same identity.
Existing protobuf wire-characterization and independent-consumer tests
continue to check the retained paths.

`crates/yaml-sigil-wasm/tests/wasm.rs` checks Rust namespace interoperability.
`crates/yaml-sigil-wasm/tests/generated_api.cjs` mixes JavaScript namespace
and top-level calls for all eight operations, including shared result classes
and resource-policy objects. Both styles run `tests/byte_inputs.cjs` relative
to that crate. Rust binding tests run in Node.js and Firefox; generated
JavaScript tests run in Node.js. Success, invocation, resource, and
cryptographic outcomes remain unchanged.

## Suite Layout

`crates/yaml-sigil-conformance` exposes one sync suite per fixture directory
and async siblings where the exercised trait surface has async APIs. Downstream
implementations can call the same `run_*_suite` helpers to compare behavior.

| Fixture directory | Sync suite | Async suite | Surface exercised |
|-------------------|------------|-------------|-------------------|
| `yaml-decomposition/` | `run_yaml_decomposition_suite` | `run_yaml_decomposition_suite_async` | `(Async)Transcriber::decompose` on YAML form |
| `protobuf-conformance/` | `run_protobuf_outer_suite` | `run_protobuf_outer_suite_async` | `(Async)Transcriber::decompose` on protobuf form |
| `schema-alignment/` | `run_schema_alignment_suite` | `run_schema_alignment_suite_async` | `(Async)Verifier::pre_verify` and `verify` |
| `key-id/` | `run_keyid_suite`, `run_keyid_compose_suite` | `run_keyid_suite_async`, `run_keyid_compose_suite_async` | `(Async)Verifier::pre_verify` and `(Async)Transcriber::compose` |
| `base64/` | `run_base64_suite` | n/a | Core base64 helper behavior |
| `alg-ed25519/` | `run_ed25519_suite` | `run_ed25519_suite_async` | `(Async)Verifier::verify`, key resolution, signing |
| `alg-ecdsa/` | `run_ecdsa_suite` | `run_ecdsa_suite_async` | `(Async)Verifier::verify`, key resolution, signing |
| `transcoding/` | `run_transcoding_suite` | n/a | YAML ↔ protobuf transcoding and effective-field preservation |
| `verification-runtime/` | `run_verification_runtime_suite` | `run_verification_runtime_suite_async` | `(Async)Verifier::pre_verify`, `verify`, and key resolution |
| `yaml-signature-conformance/` | `run_yaml_signature_suite` | `run_yaml_signature_suite_async` | `(Async)Verifier::pre_verify` and `verify` over YAML signature documents |

Primary entry points:

- `crates/yaml-sigil-conformance/tests/conformance_default.rs`
- `crates/yaml-sigil-conformance/tests/conformance_default_smoke.rs`
- `crates/yaml-sigil-conformance/tests/conformance_default_smoke_async.rs`
- `crates/yaml-sigil-conformance/tests/e2e_buildtime_keys.rs`
- `crates/yaml-sigil-conformance/tests/yaml_metadata_conformance.rs`

The conformance tests exercise this workspace's implementation crates.
Their verifier and signer bounds are specialized to this implementation's
RustCrypto key bindings. Key-resolution cases call the implementation-owned
free functions; the portable traits intentionally do not prescribe key parsers.

## Expected Behavior Summary

The private backends are `noyalib` `0.0.57` and `jsonschema` `0.56`. The
`yaml-signature-conformance/` and `schema-alignment/` suites check their
expected parsing and validation outcomes. The downstream Serde fixture uses
`noyalib` `0.0.53` to check the public data-model boundary across versions.

The `0.6` implementation uses `ed25519-dalek` 3, `curve25519-dalek` 5,
`p256` 0.14, `signature` 3, and `sha2` 0.11. The `alg-ed25519/` and
`alg-ecdsa/` suites check canonical mixed-order Ed25519 acceptance,
noncanonical and small-order key rejection, and P-256 high-S/low-S acceptance.
Provider qualification and artifact round trips exercise the public key
types.

Default P-256 signing in `crates/yaml-sigil-signing/src/lib.rs` follows the
[profile's nonce-generation requirement](https://github.com/NVIDIA/yaml-sigil-spec/blob/98140c77464af0a1cae2c6a650a1adeb9493e5f2/algorithms/02-ECDSA_SECP256R1_SHA256_RAW_RS64.md#signing).
It hashes the final payload once with SHA-256 and rejection-samples an
independent nonce in `1..n` from the system CSPRNG. RustCrypto's prehashed
primitive consumes that nonce directly. A zero `R` or `S` restarts sampling;
entropy failure returns `KeyOperationFailure` without an artifact or a
deterministic fallback. `DefaultSigner`, `DefaultAsyncSigner`, and bounded
RustCrypto signing use this nonce-generation policy. Default Ed25519 signing
is deterministic.

The signing unit tests check that a supplied test nonce determines `R`
independently of the payload, reject zero and out-of-range candidates, exercise
a constructed zero-`S` retry, and propagate entropy failure. Default sync and
async tests verify fresh `R` components and valid signatures for both forms,
empty payloads, repaired YAML final newlines, and opaque protobuf bytes.
The `alg-ecdsa/two-nonce-instability.*` fixtures expect `Verified`. Those fixed
artifacts test verification; the runtime tests exercise nonce generation.

WebAssembly uses the `getrandom` Web Crypto backend.
`crates/yaml-sigil-wasm/tests/wasm.rs` checks fresh P-256 `R` components and
valid signatures in Node.js and Firefox while retaining exact resource-limit
checks. `crates/yaml-sigil-wasm/tests/generated_api.cjs` also injects a Web
Crypto failure and requires `signer_error` with `key_operation_failure` and
no output artifact through the default and bounded JavaScript operations.
The byte-input regressions in `crates/yaml-sigil-wasm/tests/byte_inputs.cjs`
verify each fresh P-256 signature and compare payloads, metadata, and artifact
lengths instead of requiring identical signatures across calls.

Local WebAssembly regression coverage lives in
`crates/yaml-sigil-wasm/tests/wasm.rs` and
`crates/yaml-sigil-wasm/tests/generated_api.cjs`. Its opt-in bounded operations
accept exact byte ceilings and return `resource_error` above them, while the
unbounded operations accept otherwise valid complete artifacts larger than
4 MiB. These operational rejections do not classify artifacts as malformed or
non-conforming. Tests also preserve YAML and protobuf round trips, algorithm
verification, newline repair, selector errors, and output-copy behavior on
Node.js and Firefox. Native admission tests in
`crates/yaml-sigil-wasm/src/resource.rs` verify that rejected sizes never
invoke the byte-copy or processing closure. These tests supplement the
imported conformance fixtures without declaring a divergence.

Byte-input regressions in `crates/yaml-sigil-wasm/src/bytes.rs` and
`crates/yaml-sigil-wasm/tests/byte_inputs.cjs` exercise intrinsic metadata,
fixed-length copying, detached and out-of-bounds views, shared-buffer growth,
and all byte parameters in the eight generated JavaScript operations. Valid
views preserve their admitted bytes. Invalid views and copy exceptions return
`invocation_error` with `invalid_byte_input`, no output bytes, and a reusable
resource policy. These JavaScript invocation checks do not change imported
fixtures, artifact classification, or protocol conformance outcomes.

The current fixture and regression set covers:

- YAML decomposition marker handling, unsigned artifacts, malformed carrier
  ranges, constant-memory final-marker selection, marker-dense payloads, UTF-8
  preconditions, BOM rejection, and payload-side YAML document-end markers.
- Protobuf outer-envelope duplicate and unknown-field handling plus malformed
  field numbers, tags, wire types, truncated varints, overflowing varints, and
  lengths under both supported `OuterConformance` modes.
- Protobuf Compose and signing preserve arbitrary caller payload octets exactly
  and do not apply YAML-specific UTF-8, BOM, or final-line-terminator handling.
- YAML ↔ protobuf transcoding for empty, Boolean-like, null-like, and
  numeric-looking base64url signature strings.
- Verification runtime classification for successful ECDSA verification,
  unsupported algorithms, and cryptographic mismatch in both artifact forms.
- YAML/protobuf algorithm mapping, malformed algorithm identifiers, and
  empty-signature precedence over runtime algorithm support.
- `keyid` presence, emptiness, UTF-8 byte bounds, CR/LF rejection, and
  lookup-hint handling.
- URL-safe no-padding base64 behavior, including invalid alphabet, padding,
  whitespace, length, and trailing-bit cases.
- Ed25519 happy paths, noncanonical encodings, small-order configured keys,
  stable re-signing, and algorithm-parameter rejection.
- ECDSA P-256/SHA-256 happy paths, ACVP-derived vectors, high-S/low-S
  acceptance, invalid component ranges, wrong-size signatures, bad keys, and
  nonce-instability fixtures.
- YAML signature-document schema identity, universal known-key duplicate
  rejection, the markerless carrier byte limit, document count, mapping root,
  declared field types, explicit document-end handling, and unknown-key
  behavior under the implementation's advertised profile.

When a fixture exercises behavior that the Rust implementation cannot or
should not represent naturally, record the divergence here rather than adding
an unnatural workaround.

## Import Review Notes

- 2026-09-23: Reviewed and refreshed local artifacts from public
  `NVIDIA/yaml-sigil-spec` `main` at
  `30b143f09630448abbace14cfae2188279536f56`, advancing the reviewed revision
  from `98140c77464af0a1cae2c6a650a1adeb9493e5f2`. The eight-commit delta
  extends the non-normative implementation kit's runnable-example and Buf
  guidance, updates conformance-generator comments and development tooling,
  and revises CI and repository maintenance. These upstream files are not
  imported into this workspace.

  `cargo xtask update-spec` produces no artifact changes. The local proto,
  JSON Schema, curated fixture bytes and mappings, expected outcomes,
  imported and crate-local notices, public contracts, and runtime behavior
  remain unchanged. The core and conformance README links now identify the
  reviewed specification revision. No conformance divergence is added.

  The coordinated
  [`yaml-sigil-traits` update](https://github.com/NVIDIA/yaml-sigil-traits/pull/126)
  advances its specification pin and notice link to the same revision without
  changing public trait or DTO definitions. This workspace retains
  `yaml-sigil-traits` `0.4.0`; no dependency or API reconciliation is needed.
- 2026-09-17: Reviewed and refreshed local artifacts from public
  `NVIDIA/yaml-sigil-spec` `main` at
  `98140c77464af0a1cae2c6a650a1adeb9493e5f2`, advancing the reviewed revision
  from `bcfa1e05a61fc27c6fd814a3910e7a24a560f038`. The delta adds a
  non-normative language implementation kit, a fixture discovery manifest,
  glossary text, and repository validation and maintenance changes. The kit
  and manifest do not replace the normative specification or fixture
  expectations and are not imported into this workspace.

  `cargo xtask update-spec` produces no artifact changes. The local proto,
  JSON Schema, curated fixture bytes and mappings, expected outcomes,
  imported and crate-local notices, public contracts, and runtime behavior
  remain unchanged. The core and conformance README links now identify the
  reviewed specification revision.

  Public `NVIDIA/yaml-sigil-traits` `main` at
  `9d35be595f0e5133f01808542740095f8e574169` pins the same specification
  revision. Its public trait and DTO definitions remain unchanged since the
  previous review. This workspace already depends on `yaml-sigil-traits`
  `0.4.0`, so no dependency or API reconciliation is needed.
- 2026-09-06: Replaced the public generated protobuf types with the
  private-field `yaml_sigil_core::pb` facade. The Buffa 0.5 characterization
  vectors and independent downstream fixture confirm the same field numbers,
  known and unknown algorithm values, optional `keyid`, arbitrary payloads,
  absent and duplicate fields, unknown fields, groups, and malformed-input
  outcomes under Buffa 0.9.2. Owned decoding preserves unknown fields until an
  explicit discard. Borrowed views retain input-backed fields. Specification
  inputs, conformance fixture bytes, suite mappings, expected outcomes, and
  notices are unchanged.
- 2026-09-06: Reviewed and imported `yaml-sigil-spec` `origin/main` at
  `bcfa1e05a61fc27c6fd814a3910e7a24a560f038`. The specification delta since
  `07d76b3624265af9632568abcb4bac5143af5a8e` changes repository and
  conformance-rebuilder tooling. The latest P-256 changes reject invalid
  private and nonce scalars and validate vendored ACVP public keys before
  fixture generation. The local proto, JSON Schema, curated fixture bytes,
  expected outcomes, imported notices, and runtime behavior are unchanged.

  `yaml-sigil-traits` advances to `0.4.0-rc.4` at
  `04a5cecd79dc605b8ab41cc29f302bad95a6b620`. Its pinned specification now
  matches this import. The public trait and DTO shapes are unchanged, so the
  Rust implementation requires no API reconciliation.
- 2026-08-24: Scoped Compose payload-stream validation to YAML form and added
  protobuf round-trip regressions for invalid UTF-8, BOM-prefixed, and
  non-line-terminated payload bytes. Specification inputs, schemas, fixture
  bytes, public API shapes, dependencies, and notices are unchanged.
- 2026-08-21: Added signing and verification round-trip regressions for
  arbitrary protobuf payload octets. Protobuf signing now passes caller bytes
  unchanged into the signature and artifact even when newline appending is
  enabled. YAML output retains its existing authorized newline-appending
  behavior. Specification inputs, schemas, fixture bytes, public API shapes,
  dependencies, and notices are unchanged.
- 2026-08-13: Marked `crates/yaml-sigil-conformance/fixtures/**` as `-text` in
  `.gitattributes` so checkout preserves every fixture byte on Linux, macOS,
  and Windows, including intentional CRLF and binary artifacts. No fixture
  bytes, mappings, expected outcomes, runtime behavior, dependencies, or
  notice obligations changed.
- 2026-08-11: Consolidated the 11 imported fixture README files into
  `crates/yaml-sigil-conformance/README.md`, which links to the authoritative
  conformance documentation at the exact imported `yaml-sigil-spec` revision,
  `07d76b3624265af9632568abcb4bac5143af5a8e`. The spec importer now leaves
  fixture documentation, rebuild generators, and vendor data upstream while
  continuing to copy every fixture artifact and the applicable notices. No
  fixture bytes, fixture mappings, expected outcomes, public APIs, or runtime
  behavior changed.
- 2026-08-03: Imported `yaml-sigil-spec` at
  `07d76b3624265af9632568abcb4bac5143af5a8e`. The import adds paired
  transcoding fixtures for empty and YAML-ambiguous signature strings, three
  malformed protobuf varint fixtures, YAML document-boundary and declared-type
  fixtures, and a paired ECDSA runtime-classification suite. Sync and async
  suites now exercise every applicable fixture through the public Rust
  surfaces. The transcoding suite compares parsed string values and effective
  protobuf fields instead of prescribing one permitted YAML scalar spelling.

  Existing runtime behavior already satisfies every new expected outcome. The
  serializer emits YAML strings for ambiguous base64url values, protobuf
  decomposition rejects truncated and overflowing varints, YAML parsing
  enforces the new carrier boundaries and types, and verification preserves
  the supported, unsupported, and cryptographic-failure state distinctions.
  The protobuf schema, JSON Schema, algorithm definitions, base64 rules, and
  notice files are unchanged.

  `yaml-sigil-traits` advanced to
  `ae29756e4e72c4dc63a99cc6e6d2d52ed1f79597`. It updates specification pins and
  documentation to describe `PublicKeys` as caller-supplied verification keys
  and `SignedButFailedVerification` as an attempted cryptographic verification
  failure. Trait and DTO shapes and the crate version remain unchanged, so no
  `Cargo.toml` change is required.
- 2026-07-30: Imported `yaml-sigil-spec` at
  `22150d6d182048f36238bdaea705e8aaffb93f2c`. This attribution-only import
  expands the canonical and conformance notice files with the applicable NIST
  FIPS 180-4 and FIPS 186-5 context, RFC 8032 and RFC 4648
  intellectual-property caveats, RFC 3629 terms, the pinned Protocol Buffers
  documentation license, and conformance-rebuilder distribution details. The
  fixture documentation records the same provenance.

  `alg-ed25519/configured-key-small-order.txt` now identifies Table 1 and
  Appendix B of *Taming the Many EdDSAs* and states that the eight numeric
  values were reordered from the paper. Its eight key encodings are unchanged.
  Fixture outcomes, runtime behavior, proto and schema artifacts, and the
  public Rust contract are unchanged. The independently distributed
  `yaml-sigil-verification` notice now carries the corresponding RFC 8032
  reproduction and intellectual-property context for `src/crypto.rs`.

  `yaml-sigil-traits` advanced to
  `402db3f9729672dc8852f32e991b1081793b3e85`, which only advances its pinned
  specification to the same revision. It does not change traits or DTO shapes,
  so no `Cargo.toml` change is required.
- 2026-07-29: Imported `yaml-sigil-spec` at
  `be15ed9ac71d1fc601dc9e5cf6d1f1a87c695dae`. The import adds
  `yaml-signature-conformance/oversized-carrier.yaml`,
  `yaml-decomposition/marker-dense.yaml`, and six malformed protobuf fixtures:
  `invalid-field-zero.binpb`, `out-of-range-field-number.binpb`,
  `overflowing-tag-varint.binpb`, `oversized-length.binpb`,
  `invalid-wire-type-6.binpb`, and `invalid-wire-type-7.binpb`. The sync and
  async suites exercise every fixture. The signature-document JSON Schema
  change is descriptive only. The artifact proto and all notice files are
  unchanged.

  Earlier Rust changes already reject duplicate YAML keys, bound parser work,
  retain one final-marker candidate, reject invalid protobuf tags, and validate
  protobuf lengths without a host-width assumption. This import closes the
  shared-fixture and documentation gap around that behavior. Verification now
  applies the 16,384-octet limit directly to markerless carrier bytes instead
  of counting the transcription-owned marker.

  `yaml-sigil-traits` advanced to
  `9396edb23e6db1d15ee3a85100372cd427118cc8`, but that commit only advances its
  pinned specification to the same revision. It does not change traits or DTO
  shapes, so this workspace intentionally retains its existing dependency
  resolution at `f5edd39c340a239145e9a97f164bffcebffe9e28`.
- 2026-07-29: Imported `yaml-sigil-spec` `origin/main` at
  `0a4421362a36b684ac6217ec00bc9e16be24e370`. The Ed25519 `S`-boundary
  protobuf fixtures now retain the valid `R` component from RFC 8032 section
  7.1 Test 1, so `S >= L` is their only canonical-encoding violation. The
  duplicate-signature YAML fixture now uses two distinct, independently valid
  base64url encodings, so duplicate-key handling is its only structural
  failure. Fixture names, expected outcomes, suite mappings, proto and schema
  artifacts, notices, runtime behavior, and the public contract are unchanged.
  Validation resolves `yaml-sigil-traits` at
  `f5edd39c340a239145e9a97f164bffcebffe9e28`, which only advances its pinned
  specification and does not change the Rust contract.
- 2026-07-29: Imported `yaml-sigil-spec` `origin/main` at
  `beb065696cdbfb526566e45628c5eb9aa86579ac`. The imported notices classify
  RFC 8032 section 7.1 values as attributed IRTF Stream test-vector material
  under the applicable IETF Trust and BCP 78 framework, not as Revised-BSD
  Code Components. They preserve the 2017 RFC copyright context and warranty
  disclaimer, the RFC 4648 copying conditions and warranty disclaimer, and
  the 2009 source notice for
  *Standards for Efficient Cryptography 1 (SEC 1)* and 2010 source notice for
  *Standards for Efficient Cryptography 2 (SEC 2)*, plus their patent/IP
  caveats. Imported fixture documentation and comment-capable sidecars now
  carry short provenance references. Proto and schema artifacts, semantic
  fixture bytes, fixture names, expected outcomes, runtime behavior, and the
  public contract are unchanged. Validation resolves `yaml-sigil-traits` at
  `94a39f934c4ccf0d13dfaf442d25fdbd9a5f32b5`, whose corresponding changes are
  also attribution-only.
- 2026-07-29: Imported `yaml-sigil-spec` `origin/main` at
  `332b83c04e80e1efb1d233340899b920050b0124`. The import adds YAML and
  protobuf fixtures that require `PreVerify` to accept empty signature octets
  and `Verify` to return `MalformedAttemptedSigned` before disabled-algorithm
  classification. The schema-alignment sync and async suites assert that
  ordering with ECDSA disabled. The import also adds wrong-schema and
  missing-schema YAML fixtures. The YAML signature-document sync and async
  suites assert `MetadataParseFailure` at pre-verify and
  `MalformedAttemptedSigned` at full verification for both fixtures under
  every advertised profile branch. The verifier already implements both
  behaviors, so no runtime change is required. The workspace Git dependency
  resolves `yaml-sigil-traits` at
  `561726b78816249b510489d350dc69412deecc59`, which documents the same
  stage boundaries and precedence without changing the public contract shape.
- 2026-07-28: Imported `yaml-sigil-spec` `origin/main` at
  `6fcf410d8e714971bfae086183e4964debb0ffd1`. The imported fixture README
  clarifies that `Permissive` YAML decoders may reject duplicate known mapping
  keys or accept them using documented effective-value semantics. This
  implementation documents and retains duplicate rejection. Fixture bytes,
  fixture names, suite mappings, and expected outcomes are unchanged. The
  implementation also bounds YAML parser depth, constructed nodes, alias
  expansion, and related parser resources before decoding unauthenticated
  signature-carrier bytes. The workspace Git dependency resolves
  `yaml-sigil-traits` at `d289b249d097a58267b48d0289b21036ce65c3f6`,
  which requires exact canonical YAML `alg` strings; core mapping and verifier
  regression tests now reject surrounding whitespace.
- 2026-07-27: Imported `yaml-sigil-spec` `origin/main` at
  `5e995b6566ba467bf237d8db07aff279bb6349bd`. The import adds the
  marker-injection artifacts and clarifies the strict JSON Schema profile.
  YAML and protobuf verification reject CR or LF in `keyid`, and YAML Compose
  rejects `keyid-marker-injection.carrier.txt` as
  `InvalidSignatureCarrier`. YAML signature carriers must end after one
  document. The Rust implementation removes the unreachable post-selection
  marker outcome. Other fixture bytes and expected outcomes are unchanged.
- 2026-07-09: Imported `yaml-sigil-spec` `origin/main` at
  `75468ac0b665ea4edfc3a1d113de23276f9632ba`. The imported proto change is
  comment-only, and the JSON Schema change adds only its non-semantic
  `$comment` annotation. Generated Rust behavior, fixture bytes, fixture names,
  suite mappings, and expected outcomes are unchanged.
- 2026-07-09: Imported `yaml-sigil-spec` `origin/main` at
  `189ee8a747749c3b65e9f68fe9bdbda6d70e9c39`. The import adds the complete
  third-party notices at the workspace root and beside the conformance crate,
  including the complete CC BY 4.0 legal code and RFC 8032 copyright-context
  link, and updates fixture provenance wording. Fixture bytes, fixture names,
  suite mappings, and expected outcomes are unchanged.
- 2026-06-16: Imported `yaml-sigil-spec` `origin/main` at
  `aafcc3b432f5b7397e756d2033224bf3d0853c1b`. The imported conformance
  fixture changes are README wording updates only; fixture bytes, fixture
  names, suite mappings, and expected outcomes are unchanged. The imported
  protobuf schema change is comment-only and does not change wire identity or
  generated Rust behavior.
- 2026-06-22: Added coverage-only unit tests for conformance fixture helpers,
  the base64 profile table, YAML signature profile branching, and Tier A schema
  rejection cases. Fixture bytes, fixture names, suite mappings, and expected
  outcomes are unchanged.
- 2026-06-23: Imported `yaml-sigil-spec` `origin/chore/ddurst/prelaunch` at
  `f33c1bc3452b24137dfecac67267c8898a02a02c`. The imported fixture changes add
  `yaml-decomposition/invalid-utf8-no-marker.yaml`,
  `yaml-decomposition/invalid-utf8-before-marker.yaml`,
  `yaml-decomposition/bom-signed.yaml`, and
  `yaml-decomposition/bom-no-marker.yaml`. The YAML decomposition suite now
  asserts `MalformedAttemptedSigned` at transcription and `StructuralFailure`
  at pre-verify for those fixtures.

## YAML parser budgets

The verifier applies the following hard bounds before constructing application
objects from unauthenticated markerless signature-carrier bytes:

| Parser dimension | Implementation bound |
|------------------|---------------------:|
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

The parser rejects anchors, aliases, custom tags, and duplicate keys. The
numeric parser-resource bounds are implementation-specific. YamlSigil
standardizes only the 16,384-octet markerless carrier limit.

## Whole-artifact resource policy

YamlSigil `v1alpha1` defines no maximum complete YAML or protobuf artifact
size. `yaml-sigil-rs` provides opt-in `ArtifactResourceLimits` operations as
implementation-local operational hardening. `DEFAULT_MAX_ARTIFACT_BYTES`
defines the explicitly selected default. A caller may apply a smaller or
larger bound, or no additional library-level bound. Existing unbounded
operations do not select this policy implicitly.

Whole-artifact limits do not affect conformance results. Rejecting an artifact
under a local resource policy does not make it malformed or non-conforming.
The 16,384-octet markerless YAML signature-carrier constraint remains separate
from complete artifact size. Protobuf format limits, parser safeguards,
address-space limits, allocator limits, and deployment controls still apply
when no additional whole-artifact bound is selected.

The resource API adds no fixture, fixture remapping, expected-outcome change,
or deliberate conformance divergence. Availability alone does not remediate an
existing unbounded caller. The caller must adopt a resource-aware operation at
the affected trust boundary or demonstrate an equivalent earlier bound on the
original raw input.

## Local cryptographic provider boundaries

`crates/yaml-sigil-core/src/p256_encoding.rs` provides optional conversions
for provider inputs. Signing and verification re-export the helpers. Tests
require strict DER, nonzero in-range signature components, valid public points,
and fixed 64-octet signature and 65-octet public-key outputs. They preserve high-S
and low-S values and reject malformed, trailing, and unsupported encodings.
`crates/yaml-sigil-verification/src/crypto.rs` verifies converted low-S and
high-S signatures while retaining rejection of unconverted DER and compressed
public keys at the existing slot boundaries. Fixture bytes, expected outcomes,
algorithm identifiers, and artifact formats do not change.

The core crate's notice now includes the applicable existing point-encoding
terms from *Standards for Efficient Cryptography 1 (SEC 1)*. The canonical
imported notice and conformance fixture notices remain unchanged.

The sync and async provider-aware operations reuse the same payload extraction,
signature-structure checks, public-key admissibility rules, artifact framing,
and verifier-state mapping as the RustCrypto convenience operations. The
message operation receives final payload bytes and exchanges fixed 64-octet
signatures. The synchronous P-256 digest operation instead supplies the
SHA-256 digest of those final bytes to its signing callback. It retains the
complete payload in the request and emitted artifact.

Qualified signing validates the canonical public-key binding and self-verifies
every real output before returning an artifact. Synchronous keys store only
public material; each operation supplies its callback separately.
Qualified verification runs a bounded, public-only fixed suite for each
algorithm slot on one exact configured adapter instance. Qualification is an
implementation-local interoperability check, not a YamlSigil conformance
result or a FIPS validation claim. Unqualified builders and operations make a
deliberate bypass explicit while retaining structural checks.

The provider API adds no conformance fixture, fixture remapping,
expected-outcome change, or deliberate divergence. Development tests exercise
RustCrypto, `ring`, and `aws-lc-rs` adapters. The expected Ed25519 qualification
failure for providers that reject a permitted cofactored-equation vector is
recorded as a provider-slot result and does not change artifact
classification or the advertised conformance profile.

Both algorithm qualification suites check multiple live public-key bindings
and cross-key rejection in both directions. The Ed25519 suite revisits the
original handle after binding each mixed-order case, then rechecks the later
handle after using the first. P-256 also checks low-S and high-S acceptance.
Sync and async regression tests reject factories that cache the first key,
retarget or invalidate existing handles, or accept signatures for another
bound key. These checks reuse existing attributed inputs and exercise
ordinary adapter mistakes; they do not defend against deliberate suite
evasion by trusted adapter code. Provider key types also have
compile-time `Send + Sync` checks and a test that signs and verifies across
worker threads. These checks add no conformance fixture or change to artifact
classification.

`crates/yaml-sigil-signing/src/callback_tests.rs` tests borrowed mutable
callbacks with thread-confined state, callbacks that consume their captures,
adapter error mapping, final payload bytes and digests, malformed output,
wrong-key and wrong-message rejection, and double-hash rejection. Resource
tests require zero calls on preflight rejection and one call on admitted
signing, including late YAML exact-size rejection. The digest cases in
`crates/yaml-sigil-verification/tests/provider_paths.rs` expect `Verified` for
YAML and protobuf artifacts, including empty inputs and opaque protobuf
bytes, through the existing verifier. Shared-key concurrency and sync/async
parity tests remain in place. These callback APIs add no imported fixture,
expected fixture outcome, or conformance divergence. Deterministic signatures
in callback tests isolate byte binding; they do not establish nonce compliance
for an integration.

`crates/yaml-sigil-verification/src/async_provider_tests.rs` exercises both
algorithms and artifact forms through the public async provider functions and
`AsyncSigner`/`AsyncVerifier` facades. Expected results preserve final YAML
newlines, arbitrary protobuf payload bytes, metadata, and pre-verification
reuse. Tests check qualified and unqualified behavior, malformed-input and
key rejection before provider work, operational errors distinct from
signature mismatch, borrowed `Send` futures, and pending/wake/drop behavior.
Qualification status and call counts match the synchronous fixed suite,
including mixed-order Ed25519 cases and faulty P-256 key bindings.

`crates/yaml-sigil-conformance/tests/provider_async.rs` runs focused fixture
checks through the public provider-backed `AsyncVerifier` facades, with a
borrowed factory and `Send` futures. Both qualified and unqualified paths
expect `Verified` for existing `alg-ecdsa/{high-s,low-s}.{yaml,binpb}` fixtures.
They expect `MalformedAttemptedSigned` without a provider verification call
for `alg-ecdsa/invalid-r-zero.binpb`, `invalid-s-equals-n.binpb`, and
`signature-{63,65}-bytes.binpb`. Both paths use the same fixture bytes and
expected classifications as the default implementation.

Bounded signing tests compare sync and async provider behavior for both
algorithms and forms on qualified and unqualified paths. Oversized preflight
requests invoke no signer. YAML serialization expansion can instead reject
after signing, before complete artifact allocation; an exact fitting limit
succeeds. Verification reuses the original-input admission helper or bounded
pre-verification. These resource results remain operational policy, not
conformance outcomes.

The [`provider guide`](./crypto-providers.md) maintains the tested and untested
checklist across qualified providers, unqualified providers, and direct
`yaml-sigil-traits` implementations. Finite qualification and successful
signature self-verification do not establish complete conformance, randomness
quality, SDK scheduling safety, or deployment certification. The generic
fixture runners use RustCrypto key types; test each provider implementation
through the applicable adapter paths.

[`examples/ring_unqualified_provider.rs`](../examples/ring_unqualified_provider.rs)
tests explicitly unqualified signing and verification with fresh P-256 and
Ed25519 keys for default, file, and standard-input YAML. Each operation expects
`Verified`; the tests independently verify its printed artifact using the
printed public key through the RustCrypto convenience API. Neither the
example nor its tests requires provider qualification. These generated samples
test integration and output handling, not complete conformance. The pinned
`ring` verifier's mixed-order Ed25519 acceptance difference remains. No fixture
bytes or expected fixture outcomes change.

## Known Behaviors

- `Verifier` advertises `AdvertisedConformanceProfile::Permissive`. The private
  protobuf decoder behind the stable facade uses last-wins behavior for
  duplicate inner fields, so advertising a stricter unified inner profile
  would be misleading.
- Known YAML duplicate mapping keys are rejected during signature-document
  parsing under every profile. Unknown YAML fields also reject, which is
  stricter than `Permissive` requires.
- A YAML signature carrier must contain exactly one document through EOF.
  Additional carrier documents and content after `...` are rejected. Signed
  payloads may contain multiple YAML documents.
- YAML merge keys are treated as ordinary mapping keys for signature-document
  parsing.
- YAML anchors, aliases, and custom tags are rejected during
  signature-document parsing.
- Unknown YAML signature-document fields are rejected during
  signature-document parsing.
- YAML signature base64 is decoded without trimming or other normalization.
  Quoted signature scalars containing leading or trailing whitespace are
  rejected.
- Canonical signature-document serialization rejects noncanonical `schema`
  and `alg` values and invalid base64url signatures. Empty or YAML-ambiguous
  base64url signatures use double-quoted scalar form so transcoding preserves
  their string value and decoded octets.
- Empty signature octets can pass through transcription/decomposition and
  pre-verification. Full verification rejects them before runtime
  algorithm-support classification.
- Ed25519 verification rejects small-order public keys at the point of use,
  including typed keys supplied without the byte-oriented key-resolution
  helper.
- Ed25519 verification also rejects noncanonical compressed public-key
  encodings during byte resolution and when supplied as already constructed
  typed keys.
- Ed25519 signature validation requires `R` to decode from its exact canonical
  compressed point form and `S` to be a canonical scalar. Verification uses
  the slot's cofactored equation and accepts canonical `R` points outside the
  prime-order subgroup when that equation holds.
- The independently packaged `yaml-sigil-verification` crate retains its
  applicable RFC 8032 and *Standards for Efficient Cryptography 1 (SEC 1)*
  source terms in its crate-local `THIRD_PARTY_NOTICES.md`. The
  `yaml-sigil-signing` crate also retains the applicable source terms for its
  provider validation rules in its crate-local `THIRD_PARTY_NOTICES.md`.
- P-256 byte-oriented key resolution accepts only the slot's 65-octet
  uncompressed `0x04 || X || Y` point encoding. Compressed point encodings and
  malformed or inadmissible points produce `KeyResolutionFailure`.
- ECDSA verification classifies raw signatures with `r` or `s` outside
  `(0, n)` as `MalformedAttemptedSigned`. Structurally valid signatures that
  fail the signature equation remain `SignedButFailedVerification`.
- Protobuf outer-envelope parsing rejects field number zero, field numbers
  above the protobuf 29-bit maximum, and overflowing tag varints before
  applying `OuterConformance` unknown-field behavior.
- Protobuf length prefixes use checked pointer-width conversion so malformed
  wire bytes produce the same outcome on 32-bit and 64-bit targets.
- Protobuf-form payload bytes are arbitrary octets; YAML-form payload bytes
  remain constrained by the YAML envelope rules.
- Callers bind each artifact source, route, or storage class to one form before
  verification. They do not select a form by inspecting artifact bytes or retry
  the other form after failure.

## Updating Fixtures

When importing fixtures from a spec checkout:

1. Copy only the fixture directories that `yaml-sigil-conformance` uses.
2. Do not copy `rebuild-rs/`, ACVP vendor corpora, or generator-only files.
3. Update suite code and this document together if fixture names, categories,
   or expected outcomes change.
4. Run `cargo test -p yaml-sigil-conformance --all-features` while iterating.
5. Run `cargo xtask check` as the final validation gate.
