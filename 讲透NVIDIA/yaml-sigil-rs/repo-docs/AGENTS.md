# AGENTS.md

## Maintainer operations

Ordinary repository work does not require the maintainer guide. Before
performing or advising on hosted maintainer operations—authorizing pull-request
tests, merging, activating or synchronizing a coordination line, exceptional
integration, or reverting `main`—read
[`MAINTAINERS.md`](MAINTAINERS.md) completely.

Whenever a workflow or supporting policy changes, update the matching
procedure in `MAINTAINERS.md` in the same change. Keep that runbook concise,
coherent, and aligned with the executable behavior.

Ordinary copied-ref tests require protected equality for `ci.yml` and its
local `ci-trusted.yml` and `ci-candidate.yml` callees. The static router keeps
inactive matrix expressions out of skipped job names. Reviewed maintainer
staging uses a separate main-only route and canonical
`ci-testing/pr-<number>-<head-sha>` refs. Follow `MAINTAINERS.md` for exact-head
admission, the authoritative Linux aggregate, and automatic App reporting.
The reporter must authenticate the original writer, exact source, current
main ancestry and terminal result before its checks-only token can be used.

Use [`CONTRIBUTING.md`](CONTRIBUTING.md) to choose `main` or an advertised
breaking-change coordination base before starting work. Keep compatible and
protected-policy changes on `main`; target the active coordination branch only
for next-line work. A coordination branch never supplies its own CI policy.

Coordination branches are optional, temporary contribution bases. After
promotion and successful validation on `main`, target `main` for subsequent
work unless maintainers advertise a separately activated support line.
Retained recovery refs are closed to contribution intake and routine
synchronization. Follow the
[retirement procedure](MAINTAINERS.md#retire-abandon-or-restart-a-line).

## Project-Local Skill

Use the project-local
[YamlSigil Rust spec update skill](.agents/skills/yaml-sigil-rs-spec-update/SKILL.md)
when reviewing YamlSigil specification changes, importing local spec
artifacts, or reconciling this Rust implementation after spec updates.

Follow [`xtask/AGENTS.md`](xtask/AGENTS.md) when changing the developer task
crate or its release-command boundaries.

The standard development handles are `check` (`ci` alias), `coverage`,
`coverage-open`, `profile`, and `profile-open`. This repository owns no image
workflow or MCP server; do not add image or MCP tasks. Keep CI, workflows,
scripts, and command documentation aligned when these handles change without
making the xtask inspect provider declarations.

Prefer typed, portable Cargo xtasks for Cargo-aware development orchestration.
Inspect overlapping Python helpers and propose a migration before changing
one; obtain user approval before replacing a mature script or its callers.
Retain Python at the existing pre-checkout and protected-reporting boundaries,
where compiling candidate Rust would violate the trust model.

Follow [`docs/AGENTS.md`](docs/AGENTS.md) when changing documentation or
implementation behavior covered by a guide. It defines the update triggers
for the provider guide, conformance record, and YAML backend evaluation.
Follow [`examples/AGENTS.md`](examples/AGENTS.md) when changing runnable
examples or their shared CLI modules.

## Agent Documentation Standards

Project-local skills exist under `.agents/skills/` and should remain
discoverable by agents working in this repository. Maintain those skills
according to the
[Agent Skills specification](https://agentskills.io/specification), and
maintain this file according to the
[AGENTS.md standard](https://agents.md/). Keep both portable across compatible
agent clients, without assumptions about user-specific paths or session state.

## Commit messages

Use Conventional Commits for every commit. Format the subject as
`<type>(<optional scope>): <description>`, keep it under 72 characters, and
choose the smallest accurate type. Follow the sign-off requirements in
`CONTRIBUTING.md`.

## Scope

This repository implements YamlSigil `v1alpha1` for Rust consumers. It is
self-contained for normal clone, build, test, and publish workflows.

Each published crate exposes its current API through `v1alpha1`. Prefer
explicit imports in public examples and preserve the unqualified paths as the
same `v1alpha1` default. Keep re-exports explicit, type and trait identity
shared, and optional operations under their existing feature gates. The
specification identifier is independent of crate SemVer. Both paths use the
same selected `yaml-sigil-traits` contract; adopt a new traits release before
depending on paths it introduces.

The generated JavaScript `v1alpha1` namespace forwards the eight operations
to the existing boundary functions. Keep top-level operations and result and
policy classes available. Rust re-exports alone do not establish a JavaScript
export. Exercise both styles in `tests/downstream/v1alpha1-api` and the local
WebAssembly tests when changing this surface.

Local implementation inputs:

- `crates/yaml-sigil-core/spec/proto/yaml_sigil/v1alpha1/yaml_sigil.proto`
  for protobuf wire codegen.
- `crates/yaml-sigil-core/spec/schema/YamlSigilSignature.v1alpha1.schema.json`
  for the optional JSON Schema validation helper.
- `crates/yaml-sigil-conformance/fixtures/` for conformance tests.
- `THIRD_PARTY_NOTICES.md` and
  `crates/yaml-sigil-conformance/THIRD_PARTY_NOTICES.md` for notices that
  accompany imported conformance material.
- `crates/yaml-sigil-core/THIRD_PARTY_NOTICES.md` and
  `crates/yaml-sigil-verification/THIRD_PARTY_NOTICES.md` for independently
  packaged copied specification, constant, and reference-vector material.

There is no `source-spec` submodule. When the separate `yaml-sigil-spec`
repository changes, review it outside this checkout and import only the local
artifacts and code changes this implementation needs. Use
`cargo xtask update-spec` for the local proto/schema/fixture/notice import and
`.agents/skills/yaml-sigil-rs-spec-update/SKILL.md` for the review workflow.

The public extension-trait contract lives in the separately published
`yaml-sigil-traits` crate. Do not edit, generate, or publish traits from this
repository.

Keep generated protobuf code crate-private inside `yaml-sigil-core`. Expose
protobuf messages only through the private-field types in
`yaml_sigil_core::v1alpha1::pb` and its unqualified default, and do not expose
Buffa traits, generated modules, views, fields, or errors in public signatures.
Of the published crates, only `yaml-sigil-core` depends directly on Buffa.
Preserve unknown fields and raw
unknown algorithm numbers across owned decode and re-encode. Keep the Buffa
0.5 wire-characterization tests, the protobuf `tests/downstream` facade
fixtures, and the downstream resource-API fixture passing when changing
protobuf code or dependencies.

Keep Serde as the public data-model boundary for `SignatureDocument`. Keep
current and future concrete serialization backends private, including their
types, traits, errors, and feature selection. Direct Serde deserialization does
not replace the bounded and policy-configured `parse_signature_document` entry
point for untrusted YAML. Preserve the exact field names, required fields,
optional `keyid` behavior, and unknown-field rejection documented on
`SignatureDocument` as public API. Keep `serialize_signature_document`
canonical, treat `CoreError::SignatureYaml` text as unstable diagnostic output,
and compare semantic values rather than serialized bytes in backend
interoperability tests.

YamlSigil `v1alpha1` defines no maximum complete artifact size. Treat an
opt-in whole-artifact limit as implementation-local operational hardening, not
a conformance requirement. `ArtifactResourceLimits::default()` selects
`DEFAULT_MAX_ARTIFACT_BYTES` only when a caller explicitly passes it to a
resource-aware operation. Existing entry points remain unbounded by that
policy. Keep the 16,384-octet YAML signature-carrier constraint separate.
Publishing the bounded API does not remediate an existing caller; adoption at
the affected trust boundary or evidence of an equivalent earlier raw-input
bound is required.

## Third-party material and attribution

`THIRD_PARTY_NOTICES.md` is the canonical attribution and redistribution
record for imported standards text, test vectors, parameters, tables, and
other third-party material in this workspace. The matching notice beside
`crates/yaml-sigil-conformance` accompanies the imported fixtures. Import both
files from `yaml-sigil-spec` with `cargo xtask update-spec`; do not let the
copies diverge.

Crate-local `THIRD_PARTY_NOTICES.md` files cover third-party material packaged
by independently distributed crates. Reconcile those notices with the
canonical imported notice whenever the corresponding source material or terms
change.

When adding or changing third-party material:

- Update the authoritative notice in `yaml-sigil-spec` first, then use the
  documented import workflow. Record the exact source, version, section,
  copyright holder, applicable copying conditions, warranty disclaimer, and
  patent or other intellectual-property caveat.
- Read the source's own copyright notice and terms. For an RFC, check its
  publication stream and the BCP 78 or IETF Trust terms in effect on its
  publication date. Do not assume that RFC test data, tables, ABNF, or code
  blocks are IETF Code Components or covered by a BSD license.
- Ensure every file or other independently distributed material that mentions
  or references either SEC source identifies it by its full title:
  *Standards for Efficient Cryptography 1 (SEC 1)* or
  *Standards for Efficient Cryptography 2 (SEC 2)*. Use the full title on the
  first source reference in each file; the `SEC 1` and `SEC 2` short forms may
  follow within that file.
- Add a short provenance comment next to copied or derived constants,
  algorithms, encodings, validation rules, or test values. State when
  identified third-party material is not covered by a file's Apache-2.0
  declaration.
- Do not alter semantic fixture bytes to add attribution. For binary files,
  signed artifacts, parser inputs, or other exact-byte fixtures, put the
  provenance in the nearest `README.md`, a safe sidecar, and the authoritative
  generator source.
- Keep the `.gitattributes` rule for
  `crates/yaml-sigil-conformance/fixtures/**` marked `-text`; these are
  exact-byte inputs and must not undergo checkout line-ending conversion.
- Preserve applicable non-endorsement language. Do not present this workspace
  as an official publication of, or as affiliated with or endorsed by, a
  cited author, publisher, or standards organization.
- Verify every package containing identified third-party material includes
  the applicable crate-local notice. Keep notice files in explicit Cargo
  `include` lists when a package uses one.

Keep these instructions durable and repository-focused. Do not record private
correspondence, reviewer identities, or approval history in repository
documentation. Attribution-only imports may leave fixture bytes and runtime
behavior unchanged, but they still require an entry in
`docs/conformance-validation.md`.

## Documentation Style Guide

These rules apply to Markdown files in this Rust implementation workspace,
including README files, `docs/`, conformance notes, and release guidance.
Write like you are explaining the implementation to a colleague. Describe the
relevant behavior and whether this workspace, `yaml-sigil-traits`, or the
external specification owns it.

Use GitHub Flavored Markdown (GFM), as rendered in GitHub repository views,
unless a file documents a narrower renderer requirement. Rely on GitHub's
generated document outline for navigation.

Avoid renderer-specific inline attributes such as `{width=50%}` in new content
unless the file explicitly targets a separate renderer.

### Voice And Tone

- Use active voice. Write "`yaml-sigil-core` parses YAML signature documents
  with `noyalib`." not "YAML signature documents are parsed with `noyalib`."
- Use second person, `you`, when addressing the reader.
- Use present tense. Write "The command returns an error." not "The command
  will return an error."
- State facts. Do not hedge with "simply," "just," "easily," or "of course."

### Things To Avoid

These patterns make technical documentation harder to read. Remove them during
review.

| Pattern | Problem | Fix |
|---------|---------|-----|
| Unnecessary bold | "This is a **critical** conformance step" on routine instructions. | Reserve bold for UI labels, parameter names, and genuine warnings. |
| Repeated em dashes | "The fixture import -- which runs through `cargo xtask update-spec` -- refreshes local artifacts." | Use commas or split the sentence. Use em dashes sparingly. |
| Superlatives | "`yaml-sigil-rs` provides a powerful, robust, seamless signature experience." | Say which crate or API performs the work. |
| Hedge words | "Simply run `cargo xtask check`." | Write "Run `cargo xtask check`." |
| Emoji in prose | "Run tests before publish." with an emoji prefix. | Do not use emoji in documentation prose. |
| Rhetorical questions | "Want to validate fixtures?" | State the purpose directly. |

### Formatting Rules

- Never add line breaks inside an *italic* or **bold** span. If you must wrap
  the text, start the formatting again on the next line.
- Never add line breaks inside `[markdown](links)`.
- End every sentence with a period.
- Use `code` formatting for CLI commands, file paths, flags, parameter names,
  crate names, feature names, and literal values.
- Use `shell` code blocks for copyable CLI examples. Do not prefix commands
  with `$`.

  ```shell
  cargo xtask check
  ```

- Use `text` code blocks for transcripts, log output, and examples that should
  not be copied verbatim.
- Use tables for structured comparisons. Keep tables simple and avoid nested
  formatting.
- Use GitHub Flavored Markdown alert notices for non-normative notes and
  implementation asides when the content benefits from a visible notice label.
  Supported labels are `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`,
  `> [!WARNING]`, and `> [!CAUTION]`. Use plain Markdown blockquotes (`>`) for
  lower-emphasis asides. Do not use bold callouts or documentation-framework
  components this repository does not use.
- Use itemized bullet lists when the instructions clearly benefit from them.
- Do not number section titles. Write "Update conformance fixtures" not
  "Step 3: Update conformance fixtures."
- Do not use colons in titles. Write "Update conformance fixtures" not
  "Conformance: Update fixtures."
- Use colons only to introduce a list. Do not use colons as general-purpose
  punctuation between clauses.

### Repository-Specific Documentation Rules

- Write repository READMEs for human readers. Keep agent workflows and durable
  repository instructions in `AGENTS.md`.
- Use absolute links in READMEs packaged with published crates so the links work
  on crates.io and docs.rs.
- Prefer inline-code `yaml-sigil` in prose. Use “YAML Sigil” when code styling
  reads awkwardly.
- Reserve `YamlSigil` and `YamlSigil.v1alpha1` for code or exact identifiers.
- Usually omit the protocol version. When the version is necessary, write the
  lowercase inline-code form `v1alpha1`.
- Link other crates with inline-code names and absolute crates.io URLs.
- Explain behavior in ordinary language before introducing specification
  terminology.
- Keep conformance documentation specific. Name the fixture path, expected
  outcome, and divergence reason in `docs/conformance-validation.md`.
- When documenting spec imports, name the local artifact changed and avoid
  implying this repository owns the upstream specification.
- When documenting public APIs, distinguish re-exported `yaml-sigil-traits`
  contracts from implementation details in this workspace.

## Commands

Run from the repository root:

```shell
cargo xtask check
cargo xtask check --only=fmt,clippy,test
cargo xtask check --exclude=audit
cargo xtask package-content
cargo xtask update-spec
cargo xtask update-spec --ref origin/dev/example-branch
cargo xtask sync-workspace-versions
cargo xtask release activate --version MAJOR.MINOR.PATCH
cargo xtask release prepare --base-ref refs/heads/main --version MAJOR.MINOR.PATCH[-PRERELEASE]
cargo xtask release check --base-ref refs/heads/main --version MAJOR.MINOR.PATCH[-PRERELEASE]
cargo xtask wasm
cargo xtask coverage
cargo xtask coverage --open
cargo xtask coverage-open
cargo xtask coverage --engine=tarpaulin
cargo xtask coverage-view
cargo xtask profile
cargo xtask profile --iterations 250
cargo xtask profile --open
cargo xtask profile-open
cargo xtask profile-view
```

`cargo xtask check` runs every registered check in this order: `markdown`,
`protobuf`, `fmt`, `versions`, `package-content`, `check`, `clippy`, `test`,
`downstream`, `machete`, `deny`, and `audit`. It stops at the first failure.
`cargo xtask ci` is a visible alias with the same arguments and execution path.
Use either `--only=<csv>` or `--exclude=<csv>` to select checks. Empty or unknown
selections fail; duplicates run once in registry order.

Compilation, tests, and coverage enable all workspace features when no feature
option is supplied. They accept `--all-features`, `--features=<csv>`, and
`--no-default-features`; the last two may be combined. The independent locked
xtask and downstream fixture graphs keep their own feature contracts. Cargo Deny
always checks all features under `deny.toml`; build selectors do not narrow it.
Dependency checks generate a missing ignored root or downstream lockfile when
needed, so narrow `deny` and `audit` selections also work from a fresh checkout.

The default command sequence is:

```shell
rumdl check .
buf build crates/yaml-sigil-core
buf lint crates/yaml-sigil-core
buf format crates/yaml-sigil-core --diff --exit-code
cargo fmt --all --check
cargo fmt --manifest-path xtask/Cargo.toml --all --check
cargo xtask sync-workspace-versions --check
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-core
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-transcription
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-signing
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-verification
cargo package --list --allow-dirty --exclude-lockfile --package yaml-sigil-wasm
cargo check --workspace --all-targets --all-features
cargo check --locked --manifest-path xtask/Cargo.toml --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo clippy --locked --manifest-path xtask/Cargo.toml --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
cargo test --locked --manifest-path xtask/Cargo.toml
cargo test --manifest-path tests/downstream/Cargo.toml --package yaml-sigil-core-downstream-core-only
cargo test --manifest-path tests/downstream/Cargo.toml --package yaml-sigil-core-downstream-buffa-0-5
cargo test --manifest-path tests/downstream/Cargo.toml --package yaml-sigil-core-downstream-noyalib-0-0-53
cargo test --manifest-path tests/downstream/Cargo.toml --package yaml-sigil-downstream-resource-api
cargo test --manifest-path tests/downstream/Cargo.toml --package yaml-sigil-downstream-v1alpha1-api
cargo-machete --with-metadata
cargo deny --all-features check bans licenses sources -D warnings
cargo deny --manifest-path tests/downstream/Cargo.toml --locked check licenses sources -D warnings -A no-license-field -A unlicensed
cargo deny --manifest-path xtask/Cargo.toml --locked check bans licenses sources -D warnings -A unnecessary-skip -A unmatched-skip
cargo audit
cargo audit --file tests/downstream/Cargo.lock --no-fetch
cargo audit --file xtask/Cargo.lock
```

`cargo xtask wasm` is a separate provider-neutral local check for the
source-only `yaml-sigil-wasm` boundary. It requires Rust 1.95.0 with
`wasm32-unknown-unknown`, `wasm-pack` 0.15.x, Node.js 20 or newer, and
Firefox:

```shell
rustup target add --toolchain 1.95.0 wasm32-unknown-unknown
cargo install --locked wasm-pack --version 0.15
cargo xtask wasm
```

The task checks each runtime crate and both boundary feature sets for the
WebAssembly target, runs tests in Node.js and headless Firefox, and exercises
the generated Node.js bindings. It directs every generated executable into a
fresh temporary directory, reports cleanup failure, and rejects retained
`.wasm` files in the workspace. Keep it out of hosted workflows unless a
separate review establishes an artifact-safe need for that additional lane.

Keep the JavaScript resource-aware operations opt-in and aligned with the
shared Rust resource policy. Check byte-input lengths before allocating their
Rust copies, distinguish resource rejection from conformance outcomes, and
preserve the existing unbounded calls. Include policy configuration, exact
limits, and generated JavaScript result mapping in local WebAssembly tests.

Copied-ref CI first runs protected commit/release-path policy plus fixed-path
actionlint, ShellCheck, rumdl, cargo-machete, and `cargo-audit` against the
committed `xtask/Cargo.lock`. The root lockfile is intentionally absent, so the
full workspace audit inside the final `cargo xtask check` phase is candidate
execution, not trusted pre-execution policy evidence. The Cargo Deny checks
also run inside that final phase because they resolve candidate dependency
graphs. The downstream tests generate their separate ignored lockfile before
the downstream license, source, and RustSec checks consume it. A narrow
dependency-check selection resolves a missing lockfile without running tests. Candidate tools,
Cargo state, targets, temporary files, and materialized source stay under fresh
runner-temporary paths; no policy or privileged step follows candidate Rust.

The static package-content stage runs
`cargo package --list --allow-dirty --exclude-lockfile --package <crate>` for
each publishable crate and compares Cargo's modeled paths with the
committed exact inventory under `xtask/package-contents/`. `--allow-dirty`
permits source-tree inspection without changing tracked files.
`--exclude-lockfile` prevents Cargo from resolving unpublished local
dependencies while paths are listed; the validator adds Cargo's generated
package-local `Cargo.lock` path to the observed set before comparing it. The
stage does not assemble a `.crate` archive or publish anything. Run
`cargo xtask package-content` when you need only this check. Full package
validation with `cargo package` remains release-sequenced.

Publish only `yaml-sigil-core`, `yaml-sigil-transcription`,
`yaml-sigil-signing`, `yaml-sigil-verification`, and `yaml-sigil-wasm`
(starting at `0.6`) as crates.io `.crate`
source packages. Keep the workspace default, conformance, test-key, and xtask
packages unpublished. Do not distribute compiled native executables,
executable WebAssembly, installers, containers, retained CI or build outputs,
GitHub Release assets, or separately generated source archives. Local and
ephemeral compilation remains permitted for validation.

The xtask and `yaml-sigil-core` resolve their Buf executables through
`buf-tools` using the same minimum version requirement. Their separate Cargo
lockfiles may select different compatible releases. A system `buf` or `protoc`
installation is not required. Follow the coordinated upgrade workflow below
when changing any Buf-related version or installation control.

## Coordinated Buf upgrades

Cargo may select a newer compatible `buf-tools` release when resolving
dependencies. Use coordinated pull requests to raise every applicable minimum
requirement and verification surface. Do not infer the crate version from the
upstream Buf CLI version.

The controls have distinct roles:

- `buf-tools` is the Rust build dependency used by this workspace and its
  xtask. Its release suffix can differ from the Buf CLI version. Update the
  minimum requirements in `Cargo.toml` and `xtask/Cargo.toml`, then regenerate
  the committed `xtask/Cargo.lock`.
  The root workspace intentionally does not commit `Cargo.lock`, so do not add
  it merely for a Buf upgrade. CI obtains the executable only through this
  Cargo-resolved crate dependency; do not add a second provider-specific
  installer.
- `buf.lock` locks BSR or module dependencies, not the installed Buf CLI
  version. Do not update it solely because the CLI or `buf-tools` changed.

Coordinate these repository-specific surfaces:

- In `yaml-sigil-rs`, update `Cargo.toml`, `xtask/Cargo.toml`,
  `xtask/Cargo.lock`, the provider-neutral Buf checks in `xtask/src/ci.rs`, and
  their command documentation. Candidate CI obtains Buf through the same
  Cargo-resolved `buf-tools` dependency. Keep the build dependency in
  `tests/downstream/buffa-0-5/Cargo.toml` aligned with the workspace minimum.
- In `yaml-sigil-spec`, update its ordinary and protected
  `buf-toolchain` Cargo installation requirements, installer validation, and
  provider-neutral minimum CLI check. It has no product `buf-tools` dependency
  unless its current source proves otherwise.
- In `yaml-sigil-traits`, update only applicable current validation surfaces.
  It otherwise has no independent Buf product dependency unless its current
  source proves otherwise.

For each future coordinated upgrade:

- Review the selected Buf and `buf-tools` releases and confirm their published
  mapping.
- Make one coordinated change that updates every applicable minimum and
  verification surface.
- Regenerate only Cargo lockfiles already committed by the affected
  repository.
- Verify that no unplanned protobuf-generated output changed.
- Run the local Cargo and protected-policy suites, ShellCheck or Shuck,
  actionlint, and Markdown checks.
- Require successful ordinary and App-owned protected CI at the exact reviewed
  heads.
- Confirm that CI used the Cargo-resolved `buf-tools` executable and retained no
  artifacts.

Install `rumdl`, exact `cargo-audit` `0.22.2`, exact `cargo-deny` `0.20.2`,
and exact `cargo-machete` `0.9.2` with Cargo before running the wrapper:

```shell
rustup toolchain install 1.98.0 --component clippy,rustfmt
cargo +1.98.0 install rumdl
cargo +1.98.0 install --locked cargo-audit --version 0.22.2
cargo +1.98.0 install --locked cargo-deny --version 0.20.2
cargo +1.98.0 install --locked cargo-machete --version 0.9.2
```

Cargo Deny reads the repository-wide policy from `deny.toml` and the crate-specific
license exceptions for each graph from the nearest `deny.exceptions.toml`.
The root check resolves the uncommitted workspace graph, while the xtask check
uses its committed lockfile. The xtask command suppresses only warnings for
root-only duplicate-version skips in the shared policy; unapproved duplicates
still fail both checks.

Keep the cargo-audit, cargo-deny, and cargo-machete versions aligned with
hosted CI. Require `cargo-audit --version` to report exactly
`cargo-audit 0.22.2` and `cargo-deny --version` to report exactly
`cargo-deny 0.20.2`. The `--with-metadata` check resolves normal, development,
and build dependency names across all features, but remains an
unused-dependency heuristic; retain the all-target, all-feature Clippy and
test checks as the compilation proof.

Hosted CI runs this sequence through `cargo xtask check`. Keep its command
coverage, `xtask/src/ci.rs`, and the exact-command documentation above aligned
when changing the validation sequence. Do not make the xtask read, parse, or
test provider-specific workflow files. Validate provider configuration with
its native tooling.

The only permitted provider-specific xtask namespace is
`cargo xtask github`. Keep it limited to typed, repository-owned GitHub
operations that consolidate release automation. It must not become an
arbitrary `gh api` passthrough or a replacement for actionlint. It must never
parse, embed, snapshot, or validate workflow YAML, triggers, job names,
permissions, secrets, expressions, Action pins, or historical workflow files.
Accept tokens only through environment variables; never log them, serialize
them into fixtures, or pass them as command-line arguments.

The release commands may compare reviewed path names and opaque Git
blob identities across exact commits solely to prove release-policy provenance.
This narrow exception permits no workflow-content parsing, semantic validation,
provider-policy snapshots, or general workflow checks. Keep the required path
set and activation anchor under protected `main`; source trees remain data.

Within GitHub Actions, bind repository selection to GitHub's default
`GITHUB_ACTIONS` and `GITHUB_REPOSITORY` variables and require an exact match
with a compiled repository-policy table and the local package family. Do not
use the mutable `CI` variable or configurable environment values as a trust
switch. Local mutation commands must take an explicit repository and bind it
to that same table and checkout.

`cargo xtask check` and every non-`github` command must remain provider-neutral
and credential-free.

Python is permitted here only for the pre-checkout candidate binder, the
checkout-free protected reporter, and their deterministic fixtures. Those
policies must run before candidate materialization or App-token creation, as
applicable, and must not compile candidate-controlled Rust. Every Python file
added or materially changed must begin with comments explaining why Python is
justified at that boundary, then document its inputs, trust assumptions,
outputs, mutations, and fail-closed behavior. Keep it standard-library-only
unless a separately reviewed dependency is demonstrably needed. Use a
provider-neutral Cargo xtask for repository validation or maintenance logic
that does not require this pre-checkout boundary.

Keep
`.github/scripts/check-pull-request-commits.sh` identical across the YamlSigil
repositories. Small host-setup helpers may remain shell when moving them would
add complexity without consolidating policy.

The surviving provider helpers have deliberately narrow roles:

- `report_required_ci.py` and its focused fixture tests bind one terminal
  copied-ref run, its aggregate job's pre-execution policy/base attestation,
  exact contribution base, protected current `main`, and raw-author DCO
  identities before the scoped App creates the base-specific required verdict.
- `bind-candidate-pr.py` anonymously binds the open pull request, exact
  contribution base, protected current `main`, copied ref, ordered commit
  inventory, and optional canonical main or support release branch before source
  materialization.
- `materialize-candidate.sh` and its tests perform anonymous exact-head
  materialization while rejecting filters, ancestor Cargo configuration, and
  candidate-selected submodule behavior.
- `install-actionlint.sh` stages the checksum-verified Linux actionlint binary
  before candidate materialization, so no Action runs after candidate source
  exists.
- `check-trusted-tool-pins.sh` admits only the exact reviewed Rust baselines
  and rejects any workflow `tool:` scalar that names a floating or unexpected
  cargo-audit version without modeling workflow topology.
- `check-pull-request-commits.sh` enforces the shared exact-range, linear
  history, and DCO policy across all three YamlSigil repositories.
- `check-release-pull-request.sh` adds the canonical branch, single-commit, and
  release-file boundary for explicit version changes. A binder-validated
  repository-owned coordination promotion retains only its line's unpublished
  `rc.0` stub under the separate maintainer promotion procedure.
- `attach-release-source.sh` binds an already-qualified source only to local
  selected base refs immediately before the protected release-plz publication
  call; it never updates a remote.
- `remove-preinstalled-aws-tap.sh` performs one bounded macOS host cleanup
  before Rust setup.

Implement release qualification, same-source recovery, and deterministic
release-object finalization in the typed `cargo xtask github release` commands.
Do not add Python or shell helpers for those operations. Local version
preparation and content validation are provider-neutral under
`cargo xtask release`. The exact
release-plz dry run is a separate maintainer-operated acceptance step because
release-plz requires read-only forge association context.

`cargo xtask release activate --version MAJOR.MINOR.PATCH` creates only the
unpublished `MAJOR.MINOR.PATCH-rc.0` coordination safety stub from exact clean
`origin/main`. It updates the workspace version and internal requirements in
the root manifest without invoking release-plz or editing changelogs. Follow
`MAINTAINERS.md` for the separately authorized protected-ref transaction.

Release preparation always lets pinned release-plz update derive the
transaction first. The first release from an `rc.0` stub, starting its derived
version as a prerelease, starting `rc.1` of the immediate next patch from
unchanged stable package contents, advancing an unchanged `rc.N` to its next
ordinal, or promoting the current same-core prerelease to stable may invoke
pinned release-plz set-version afterward. Derived-version adjustments preserve
that version core; the unchanged-stable case advances only one patch to `rc.1`.
The xtask restores member workspace inheritance and verifies that
release-plz synchronized every internal
requirement. It rejects a pre-existing root `Cargo.lock` and removes only a
lockfile generated during its bounded release operations. Land any external
`yaml-sigil-traits` dependency change before creating the release branch. Run
the exact-head dry run from the canonical tracking branch, never from detached
HEAD.

Validate shell scripts under `.github/scripts` with Shuck before landing
changes. Install it from the `shuck-cli` crate and run it from the repository
root:

```shell
cargo install shuck-cli
shuck check .github/scripts
```

ShellCheck is an acceptable fallback:

```shell
shellcheck .github/scripts/check-pull-request-commits.sh
```

Hosted CI runs its pinned ShellCheck Action for these provider-specific scripts.
Keep this validation outside `cargo xtask check`.

Hosted CI pins its authoritative stable baseline to Rust `1.98.0` and runs an
independent Rust `1.95.0` lane on NVIDIA's `linux-amd64-cpu8` runner.
GitHub-hosted macOS and Windows jobs are advisory. Explicitly admitted copied
refs run public-workspace `cargo check` and `cargo test` without secrets,
OIDC, protected environments, cache saves, or retained artifacts. Complete
provider-neutral source, package, version-policy, and release-branch
validation remains authoritative on NVIDIA Linux. For copied refs, the
aggregate named by protected policy records the exact policy/base binding
and feeds the checkout-free App reporter; advisory conclusions never affect the
base-specific required verdict.

Treat every GitHub Action `uses:` pin update as a potential validation-behavior
change, even when the workflow inputs remain unchanged. While evaluating a
candidate update, compare the Action at the current and candidate immutable
SHAs, including its commands, inputs and defaults, runtime, and transitive
`uses:` dependencies. Determine whether those changes affect the local
`cargo xtask check` equivalent or this exact-command documentation. When an Action
update changes relevant behavior, reify it in hosted CI and, when applicable,
the xtask command plan and this file in the same change. Document any
intentional hosted-versus-local difference without making the xtask depend on
the hosted provider's configuration.

The root workspace does not commit `Cargo.lock`, so its Cargo checks must work
from a clean checkout without `--locked`. Keep fixture imports, version
synchronization, coverage, and profiling commands separate from CI unless the
workflow explicitly needs them.

### Coverage and profiling

Install the tools for the report engine you select:

```shell
cargo install --locked cargo-llvm-cov
cargo install --locked cargo-tarpaulin
cargo install --locked samply
```

Only the selected operation's tools are probed. Missing and installed-but-
unusable tools receive separate diagnostics with their installation command.
Keep these commands aligned with `xtask/src/reports.rs` and the guidance test
in `xtask/src/lib.rs`.

`cargo xtask coverage` uses LLVM coverage by default and writes
`target/llvm-cov-html/html/index.html`. `--engine=tarpaulin` writes
`target/coverage/tarpaulin/tarpaulin-report.html`. `coverage --open` and
`coverage-open` both generate a fresh report before opening it and accept the
same engine and feature options. Use `coverage-view --engine=<ENGINE>` to open
an existing report without rerunning tests.

Tarpaulin uses `target/coverage/tarpaulin/build` for compilation so its cleanup
does not remove ordinary build outputs. Reports cover the root workspace;
Tarpaulin excludes the separate xtask and downstream fixture workspaces.

`cargo xtask profile` builds the `yaml-sigil-conformance` integration test
`e2e_buildtime_keys` with release-equivalent optimization and debug symbols.
It selects the executable from Cargo JSON output, repeats the test 100 times
by default, and writes `target/profile/profile.json`. Use `--iterations` to
change the sample size. `profile --open` and `profile-open` both record a
fresh profile before opening Samply's interactive browser UI. Use
`profile-view` to inspect an existing profile. Samply does not produce a
standalone HTML file. On Linux, the task reports `perf_event_paranoid` and
leaves host permissions unchanged; follow local system policy when recording
is denied.

Begin performance work with focused source inspection, tests, benchmarks, or
timings. Run `cargo xtask profile` for a concrete CPU-performance question and
leave it non-interactive unless a human asks to open the browser. Report the
saved path for later inspection with `cargo xtask profile-view`.

## Cargo Features

The workspace uses `resolver = "3"` and Rust edition 2024.

| Area | Features | Notes |
|------|----------|-------|
| Protobuf codegen | n/a | Generated privately with `buffa` from the local `yaml_sigil.proto`, using Buf from `buf-tools`; public access uses `yaml_sigil_core::pb`. |
| YAML parser | n/a | Serde is public; YAML signature documents use a private `noyalib` backend. |
| JSON Schema helper | `json-schema-validate` | Exposes validation against the local signature-document schema. |

## Conformance

`crates/yaml-sigil-conformance` drives local fixture artifacts through the
public trait surfaces and core byte helpers. It is publish-disabled and exists
for this workspace and sibling implementation checks.

Any conformance-related change must update `docs/conformance-validation.md` in
the same commit. This includes fixture imports, fixture remapping, expected
outcome changes, ignored tests, public API surfaced because of a fixture, and
deliberate divergences.

Whole-artifact deployment limits do not change conformance outcomes. A local
resource-policy rejection does not make the artifact malformed or
non-conforming. Preserve this distinction when documenting or changing the
opt-in bounded APIs.

When a fixture would require going far outside the natural patterns of the Rust
crates in use, prefer recording a divergence in
`docs/conformance-validation.md` over inventing a workaround.

## Async

Sync and async trait pairs are defined in `yaml-sigil-traits` and re-exported
from the API crates. Async traits use native AFIT/RPITIT with explicit `+ Send`
returned futures and `Send + Sync` trait bounds. Do not add `async-trait`
unless a real consumer requires an object-safe shim and the tradeoff is
documented.

## Crypto And Secrets

- Never log private keys, seed material, tokens, or raw signatures on trusted
  fact surfaces.
- `SigningKey` debug output in `yaml-sigil-signing` is redacted by design.

## Local cryptographic providers

Synchronous signing binds canonical public-key bytes without storing a signer
and accepts a per-operation `FnOnce` callback without unconditional `Send` or
`Sync` bounds. Keep bindings and requests `Send + Sync`; callback captures
retain their own thread restrictions. Preserve `signature` 3.0 adapter reuse
through the forwarding helper. Synchronous verification retains its
`signature` operation traits.

Ed25519 provider signatures use canonical 64-octet `R || S`; P-256 provider
signatures use 64-octet big-endian `r || s`, never DER. Message callbacks apply
SHA-256 exactly once for P-256. The qualified P-256 digest operation hashes
the final complete payload once and supplies `&[u8; 32]`; its callback must
not hash again. It rejects other algorithms before calling and independently
verifies output against the final payload. Both callback forms leave the
profile's nonce sampling to the provider. Keep preparation, validation,
resource preflight, and framing shared, with zero calls on rejection before
signing and exactly one on an admitted signing operation.

Async providers implement the native `AsyncProviderSigner`,
`AsyncProviderVerifier`, and `AsyncProviderVerifierFactory` contracts. Keep
their futures `Send` and allow borrowed clients without a `'static`
requirement. Do not add a library-selected executor, synchronous shim, hidden
retry, or cancellation guarantee for an already submitted remote operation.
Retain the same qualified and explicitly unqualified choices for both modes.

Signing operations bind callback or adapter output to canonical public-key
bytes. The normal builder validates that key, and the operation self-verifies
every real output without issuing a synthetic signing request. Keep the
message-signing bypass named `unqualified`, and retain public-key and
signature-structure checks there.

Verification qualification remains bounded, public-only, non-serializable,
and owned by the exact adapter instance it tested. Track algorithm slots
independently, do not retry a qualified provider result through RustCrypto,
and keep provider failure distinct from signature mismatch. Replacing or
reconfiguring a provider requires qualification again.

Treat direct `yaml-sigil-traits` implementations as a supported third
integration choice. Keep the differences in runtime checks, regression
evidence, and integrator responsibilities current in
[`docs/crypto-providers.md`](docs/crypto-providers.md). Do not describe finite
qualification as complete conformance. Keep the existing RustCrypto key
types exposed until a concrete compatibility need justifies a new boundary.

Bounded provider signing reuses the standard signing preflight and final
output checks. Verification callers admit the original artifact with
`check_input_size` or bounded pre-verification before provider work. Keep
these optional resource policies separate from conformance.

Keep provider-specific crates out of the published API and ordinary
dependencies. Provider interoperability and qualification do not establish a
FIPS validation claim; that depends on the complete deployment boundary.

## Permanent Out Of Scope

Do not add gRPC servers, clients, gateways, transport adapters, generated
service stubs, or runtime bindings for the signing, verification, or
transcription service IDL. This repository owns the Rust library
implementation and the protobuf wire envelope helpers, not deployable RPC
services.

Consumers that need RPC transport wire it in their own deployment.

## Change Separation

Keep proto/schema imports, conformance fixture changes, crypto behavior
changes, CI edits, and unrelated formatting in separate commits or clearly
separated commit sections when possible.

`github release rebind-policy` owns the anonymous pre-authority rebind. Pass
`--base-ref`, `--source-root`, `--source-sha`, `--version`, and
`--operation fresh|recover` explicitly. Only current protected `main` supplies
executing policy. Use the shared, tested shell helper for source attachment.
Keep it identical across the two Rust repositories; it changes only selected
local refs.
The per-line JSON inventory excludes itself; compare opaque Git blob IDs,
never workflow contents. Recovery validates historical inventory and retained
protected-base lineage without demanding current-main content.

## Support release dispatch boundary

Support push CI runs the nonpublishing matrix. The publication workflow
runs only on main; its protected-main input helper binds canonical base, exact
source, optional initial version, and operation before source checkout. Every
later authority boundary passes the qualified version explicitly. Keep
`bind-release-invocation.sh` and its focused shell tests identical in the two
Rust repositories. Validate them with Shuck or ShellCheck and actionlint;
provider workflow parsing remains outside the xtask.
