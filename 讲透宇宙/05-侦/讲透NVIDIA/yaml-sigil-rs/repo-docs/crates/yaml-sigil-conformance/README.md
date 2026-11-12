# yaml-sigil-conformance

`yaml-sigil-conformance` runs local YamlSigil conformance fixtures against the
Rust implementation's public traits and byte-level helpers. This crate is used
only within the workspace.

## Implementation key bindings

The shared traits let each implementation choose its signing and verification
key types. The fixture runners test this workspace's RustCrypto implementation
with key types from
[`ed25519-dalek`](https://crates.io/crates/ed25519-dalek) and
[`p256`](https://crates.io/crates/p256). These are the same types accepted by
[`yaml-sigil-signing`](https://crates.io/crates/yaml-sigil-signing) and
[`yaml-sigil-verification`](https://crates.io/crates/yaml-sigil-verification).
The internal `ConformanceSigner`, `ConformanceAsyncSigner`,
`ConformanceVerifier`, and `ConformanceAsyncVerifier` adapter traits express
those bindings for the synchronous and asynchronous runners.

Key-resolution fixtures call the public resolver functions from
`yaml-sigil-verification`. Parsing raw key bytes belongs to the implementation,
not the portable contract in
[`yaml-sigil-traits`](https://crates.io/crates/yaml-sigil-traits).

## Conformance fixtures

The artifacts under `fixtures/` are curated imports from the
[YamlSigil specification conformance suite][upstream-conformance] at commit
`30b143f09630448abbace14cfae2188279536f56`. The upstream documentation is
authoritative for the fixture inventory, expected outcomes, provenance,
regeneration process, and deliberately incomplete coverage.

This repository imports the fixture artifacts that the Rust implementation
uses. It does not copy the upstream fixture README files, rebuild generators,
or vendor data. Rust-specific fixture mappings, validation results, and
divergences are recorded in
[`docs/conformance-validation.md`](../../docs/conformance-validation.md).

Exact-byte fixtures cannot carry inline attribution without changing the bytes
under test. Keep the local
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) with distributed copies of
the fixtures. It records the applicable attribution, source terms, warranty
disclaimers, intellectual-property caveats, and non-endorsement language.

## Updating fixtures

Run `cargo xtask update-spec` from the repository root to refresh the imported
artifacts and notices. When the imported specification revision changes,
update the pinned upstream link in this README and add a matching entry to
`docs/conformance-validation.md` in the same commit.

[upstream-conformance]: https://github.com/NVIDIA/yaml-sigil-spec/tree/30b143f09630448abbace14cfae2188279536f56/conformance
