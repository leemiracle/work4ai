---
name: yaml-sigil-rs-spec-update
description: Use when reviewing YamlSigil specification changes for yaml-sigil-rs, importing affected local proto/schema/conformance/notice artifacts, or reconciling this Rust implementation after spec changes.
---

# yaml-sigil-rs Spec Update

## Purpose

`yaml-sigil-rs` owns the Rust implementation crates for YamlSigil. It depends on
the separately published `yaml-sigil-traits` crate for the public trait and DTO
contract, and it owns only the local implementation inputs and distribution
notices needed by this workspace:

- `crates/yaml-sigil-core/spec/proto/yaml_sigil/v1alpha1/yaml_sigil.proto`
- `crates/yaml-sigil-core/spec/schema/YamlSigilSignature.v1alpha1.schema.json`
- `crates/yaml-sigil-conformance/fixtures/`
- `THIRD_PARTY_NOTICES.md`
- `crates/yaml-sigil-conformance/THIRD_PARTY_NOTICES.md`
- `crates/yaml-sigil-core/THIRD_PARTY_NOTICES.md` for the copied JSON Schema
  and related conformance material packaged by core.
- `crates/yaml-sigil-verification/THIRD_PARTY_NOTICES.md` for the locally
  maintained, crate-scoped notice that must remain aligned with imported
  source terms.

Run commands from the repository root. Paths in this skill are relative to that
root.

There is no `source-spec` submodule in this repository. Use this skill when
reviewing a `yaml-sigil-spec` update for impact on this workspace.

## Invariants

- Use the public GitHub URL for spec repository operations:
  `https://github.com/NVIDIA/yaml-sigil-spec.git`.
- Do not add `yaml-sigil-spec` back as a submodule.
- Import only local artifacts this implementation uses: `yaml_sigil.proto`, the
  signature-document JSON Schema, curated conformance fixtures, and the
  third-party notices that accompany those fixtures.
- Do not import service protos, Buf module files, rebuild generators, or vendor
  data unless the implementation starts using them directly.
- Do not edit, generate, or publish `yaml-sigil-traits` from this repository.
- If a spec delta requires trait or DTO contract changes, update
  `yaml-sigil-traits` first, then update this repository's dependency.
- Keep explicit `v1alpha1` and unqualified default paths bound to the same
  definitions and selected traits dependency. Preserve optional feature gates
  and separate specification identifiers from crate SemVer. Depend on a new
  traits path only after adopting the release that provides it.
- Keep updates scoped to this workspace's crates, tests, docs, CI, and xtask
  helpers.
- Leaving implementation code unchanged is a valid outcome when the spec delta
  only advances source text or does not require Rust implementation changes.
- Do not add gRPC servers, clients, gateways, transport adapters, or generated
  service stubs for signing, verification, or transcription service IDL.
- Keep Buffa-generated protobuf modules private to `yaml-sigil-core`. Preserve
  the stable private-field `yaml_sigil_core::v1alpha1::pb` facade and its
  unqualified default, unknown-field and raw enum-number forwarding, Buffa 0.5
  wire vectors, and both downstream facade fixtures.
- Treat whole-artifact limits as optional operational hardening for
  `v1alpha1`. The implementation-local resource API defaults to
  `DEFAULT_MAX_ARTIFACT_BYTES` only when a caller explicitly selects it. Do not
  import or alter specification artifacts for that API, and do not turn its
  default into a specification or conformance requirement. Keep the
  16,384-octet YAML signature-carrier rule separate.
- Review a future `v1alpha2` normative resource policy on its own terms. Its
  possibility does not establish a current normative limit.

## Workflow

1. Start from a clean worktree:

   ```shell
   git status --short
   ```

   Record the full specification commit in
   `crates/yaml-sigil-conformance/README.md` before refreshing it. Use that
   commit as `<old-spec-ref>` during delta review.

2. Refresh this repository's imported local artifacts from the target spec ref.
   The command defaults to `origin/main` and uses the public spec repository
   URL:

   ```shell
   cargo xtask update-spec
   cargo xtask update-spec --ref origin/dev/example-branch
   ```

   This imports only `yaml_sigil.proto`, the signature-document JSON Schema,
   the curated conformance fixture directories, and their third-party notices.
   It does not import service protos, Buf module files, rebuild generators, or
   vendor data.
   It also does not overwrite crate-local notices. Reconcile
   `crates/yaml-sigil-verification/THIRD_PARTY_NOTICES.md` with the imported
   canonical notice whenever the applicable RFC material or terms change.
   Apply the same review to `crates/yaml-sigil-core/THIRD_PARTY_NOTICES.md`
   when the imported JSON Schema or related conformance material changes.

3. Review the complete specification delta for implementation impact. Use the
   managed checkout under `target/spec-update/yaml-sigil-spec` or a separate
   temporary checkout to inspect it.

   First inspect the full repository diff stat so unlisted spec files are not
   missed:

   ```shell
   git -C target/spec-update/yaml-sigil-spec diff --stat <old-spec-ref>..<new-spec-ref>
   ```

   Then inspect the known implementation-relevant paths:

   ```shell
   git -C target/spec-update/yaml-sigil-spec diff --stat <old-spec-ref>..<new-spec-ref> -- \
     README.md \
     signing-api.md \
     verification-api.md \
     transcription-api.md \
     transcoding.md \
     base64-requirements.md \
     algorithms/ \
     proto/yaml_sigil/v1alpha1/yaml_sigil.proto \
     schema/YamlSigilSignature.v1alpha1.schema.json \
     conformance/
   ```

   Review any unlisted changed files that could affect imported artifacts,
   implementation behavior, conformance expectations, docs, CI, or xtask
   helpers. Update this path list when spec files move, new spec files take
   ownership of implementation behavior this workspace imports, or a spec update
   reveals a cleaner review path.

4. Check the imported artifact diff deliberately:

   ```shell
   git diff -- \
     crates/yaml-sigil-core/spec/ \
     crates/yaml-sigil-conformance/fixtures/ \
     THIRD_PARTY_NOTICES.md \
     crates/yaml-sigil-conformance/THIRD_PARTY_NOTICES.md \
     crates/yaml-sigil-core/THIRD_PARTY_NOTICES.md \
     crates/yaml-sigil-verification/THIRD_PARTY_NOTICES.md
   ```

   Revert an imported artifact only when the spec change is known to be
   irrelevant to this implementation and the omission is recorded in the commit
   or MR description.

5. Map spec changes to the affected workspace surfaces. Start with the paths
   below and include any other paths identified by the complete diff:

   - Each published crate's `src/v1alpha1.rs` and `src/lib.rs`: explicit
     version selection and compatible default re-exports. Keep the namespace
     inventory aligned with that crate's public items and feature gates.
   - `crates/yaml-sigil-wasm/src/versioned_js.rs`: JavaScript namespace
     forwarding to the existing boundary. Keep result and resource-policy
     classes shared with the top-level API and test the generated exports.
   - `crates/yaml-sigil-core/src/algorithm.rs`: canonical YAML `alg` strings,
     protobuf enum mapping, algorithm additions, and algorithm deprecations.
   - `crates/yaml-sigil-core/src/signature_doc.rs` and
     `crates/yaml-sigil-core/src/tier_a_schema.rs`: YAML signature document
     parsing, schema validation, and metadata extraction.
   - `crates/yaml-sigil-core/src/pb.rs`, `src/proto_outer.rs`, and
     `src/wire.rs`: the private generated-code boundary, stable facade,
     protobuf envelope structure, strictness, unknown-field forwarding, and
     wire encode/decode behavior.
   - `crates/yaml-sigil-signing/`: signing flow, output form behavior,
     canonical envelope generation, key and payload preconditions.
   - `crates/yaml-sigil-transcription/`: YAML/protobuf compose, decompose, and
     signed-artifact transcoding behavior.
   - `crates/yaml-sigil-verification/`: verifier state model, pre-verify paths,
     algorithm checks, key resolution, parser observations, and capability
     advertisement.
   - `crates/yaml-sigil-conformance/` and `docs/conformance-validation.md`:
     fixture coverage, divergence catalog, and API gaps discovered by
     conformance changes.
   - `crates/yaml-sigil-core/tests/protobuf_wire_compatibility.rs` and
     `tests/downstream/`: compatibility with characterized wire behavior and
     independently generated protobuf consumers.
   - `tests/downstream/v1alpha1-api/` and
     `crates/yaml-sigil-wasm/tests/`: interchange between explicit and default
     paths, shared traits and DTOs, and actual JavaScript namespace exports.
   - `crates/yaml-sigil-core/README.md` and
     `crates/yaml-sigil-conformance/README.md`: immutable links to the reviewed
     specification commit.
   - Root, conformance, and crate-local `THIRD_PARTY_NOTICES.md` files:
     imported attribution, independently packaged material, source terms,
     warranty disclaimers, patent/IP caveats, and non-endorsement language.
   - `Cargo.toml`: update `yaml-sigil-traits` when the public trait contract or
     coordinated dependency release changes. The root workspace intentionally
     does not commit `Cargo.lock`; do not add it during a specification update.
   - This skill: keep the map current when code moves, new crates take
     ownership of spec behavior, or a spec update reveals a cleaner review path.

   For every completed review, replace the full commit ID in both immutable
   README links and add a dated entry to the import review notes in
   `docs/conformance-validation.md`. Record which imported artifacts,
   conformance outcomes, public contracts, notices, and runtime behaviors did
   or did not change. Do this even when the importer produces no byte changes
   or the upstream delta affects only conformance generators and repository
   tooling. Leave implementation code unchanged when the review finds no
   implementation impact.

6. Run the quality loop appropriate to the change:

   ```shell
   cargo xtask check
   ```

   During fixture iteration, use
   `cargo test -p yaml-sigil-conformance --all-features` as a faster focused
   check. The final validation remains `cargo xtask check`.

7. Coordinate release order after review:

   Publish the four implementation libraries and, from `0.6` onward,
   `yaml-sigil-wasm` as crates.io `.crate` source packages. Keep conformance,
   test-key, and xtask packages unpublished. Update
   `yaml-sigil-traits` first when the public contract changes, then update this
   workspace's `yaml-sigil-traits` dependency.
