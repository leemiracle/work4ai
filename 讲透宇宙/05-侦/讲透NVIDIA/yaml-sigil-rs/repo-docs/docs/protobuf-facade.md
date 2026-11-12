# Protobuf facade

Use `yaml_sigil_core::v1alpha1::pb` to read and write protobuf envelopes without
importing a protobuf library. Applications that already use another
protobuf library can exchange wire bytes with the facade while keeping their
own message types.

The unqualified `yaml_sigil_core::pb` path remains the `v1alpha1` default.
Both paths name the same owned messages, borrowed views, and facade errors.
Generated protobuf modules remain private.

## Run the example

Run this command from the repository root.

```shell
cargo run --package yaml-sigil-examples --example protobuf-facade
```

The [example source](../examples/protobuf_facade.rs) demonstrates three flows.

- Construct an envelope through the core facade, encode it, and decode it
  into both an owned value and a borrowed view.
- Decode the facade's output with Prost and compare the application fields.
- Construct a Prost message independently, encode it, and decode its output
  with the core facade.

The command uses built-in data and prints the result of each comparison. Its
payload includes a NUL and an invalid UTF-8 byte. The protobuf payload is
opaque bytes and does not have to be YAML text. Its signature bytes are
illustrative encoding data. The example performs no signature verification.

## Core types

`SignedYamlArtifact` owns a payload and an optional `YamlSigilSignature`.
Construct them with `new`, inspect fields through accessors, and use setters
to change fields. `encode_to_vec` returns a fallible wire encoding;
`SignedYamlArtifact::decode` returns an owned decoded value.

`SignedYamlArtifactRef::decode` provides borrowed inspection. Payload,
signature bytes, and string fields borrow the input buffer, so that buffer
must outlive the view. Use `to_owned` when the decoded value must outlive its
input.

These public types and their errors belong to `yaml-sigil-core`. Buffa and
its generated types remain private implementation details. Consumers need
no direct Buffa dependency, even though it appears transitively in the
dependency graph.

## Exchange bytes with Prost

The examples package pins [`prost`](https://crates.io/crates/prost) to
`0.14.4` as a development dependency. The example declares `AppArtifact`,
`AppSignature`, and `AppAlgorithm` locally using Prost's
[derive annotations](https://docs.rs/prost/0.14.4/prost/#serializing-existing-types).
It needs no additional code generator or build script.

The declarations follow the field numbers, wire types, optional-field
presence, and enum values in the
[local wire schema](../crates/yaml-sigil-core/spec/proto/yaml_sigil/v1alpha1/yaml_sigil.proto).
In particular, `keyid` is an `Option<String>` in the application model, so
its absence survives both interoperability directions. The algorithm field
stores its raw `i32` value, following Prost's enum representation.

Exchange encoded bytes between the libraries using each library's encode and
decode methods. Compare decoded fields; interoperable encodings need not
contain identical bytes.

The owned core facade preserves unknown fields and raw unknown algorithm
numbers when decoding and re-encoding. This example checks the declared
fields with the pinned Prost release; it does not establish unknown-field
retention through another library. Keep original wire bytes when forwarding
must preserve their exact encoding.

## Decoding and verification

Protobuf decoding is structural. It does not establish complete artifact
validity or verify a signature. Use `yaml-sigil-verification` with trusted
keys when you need authenticated payload bytes.

The example uses small built-in messages. For external input, the facade also
offers `decode_with_resource_limits` methods that check an explicitly chosen
whole-artifact policy before parsing. Such limits are application policy,
separate from signature verification and conformance.

## Tests

The example tests run all three flows with present and absent `keyid` values
and exercise binary payload bytes. The
[core-only consumer fixture](../tests/downstream/core-only/Cargo.toml) tests
owned and borrowed protobuf decoding with `yaml-sigil-core` as its sole
direct dependency. The runnable interoperability example itself also uses
Prost.

```shell
cargo test --package yaml-sigil-examples --example protobuf-facade
cargo test --manifest-path tests/downstream/Cargo.toml \
  --package yaml-sigil-core-downstream-core-only
```
