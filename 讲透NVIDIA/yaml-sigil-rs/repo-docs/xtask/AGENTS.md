# xtask guidance

These instructions apply to the developer-only `xtask` crate.

Keep `cargo xtask check` and every namespace except `github` provider-neutral and
credential-free. Development commands may validate, package, import, profile,
or prepare local source, but they must not inspect GitHub, GitLab, runner, or
workflow environment state.

## Standard development commands

The xtask is an isolated workspace with its own committed `Cargo.lock`, Rust
1.95 minimum, and explicit library and binary targets. The root Cargo alias
runs `cargo run --locked --manifest-path xtask/Cargo.toml --`. Keep this
separation from the untracked product-workspace lockfile and release policy.
Use Clap derive, a thin binary entry point, testable command construction, and
the root parser's `CommandFactory::debug_assert()` invariant test.

`cargo xtask check` and its visible `ci` alias share one parser and execution
path. The canonical registry order is `markdown`, `protobuf`, `fmt`,
`versions`, `package-content`, `check`, `clippy`, `test`, `downstream`,
`machete`, `deny`, and `audit`. Run all steps by default and fail fast. Accept
mutually exclusive CSV `--only` and `--exclude` selectors; reject unknown,
empty, and fully excluded selections and deduplicate in registry order.

Share feature options between compilation, tests, coverage, and coverage-open.
Default to all features only without explicit options; allow `--features` with
`--no-default-features`. Keep all-feature locked xtask compilation and the
independent downstream fixture contracts outside product feature selection.
Keep Cargo Deny's all-feature policy independent of these build options.
Do not forward features to formatting. Generate missing ignored lockfiles for
selected dependency checks without requiring the tests to run first.

LLVM coverage writes `target/llvm-cov-html/html/index.html`; Tarpaulin writes
`target/coverage/tarpaulin/tarpaulin-report.html`. Both `coverage --open` and
`coverage-open` generate and verify a fresh report before opening it.
`coverage-view` retains the existing-report viewer with engine selection.

Tarpaulin uses `target/coverage/tarpaulin/build` for compilation so its cleanup
does not remove ordinary build outputs. Reports cover the root workspace;
Tarpaulin excludes the separate xtask and downstream fixture workspaces.

Profiling builds the `yaml-sigil-conformance` integration test
`e2e_buildtime_keys` with the `profiling` Cargo profile. Select its executable
from Cargo JSON messages and run it with `--test-threads=1` through Samply.
Preserve the 100-iteration default, `--iterations` option, and
`target/profile/profile.json` report. Both `profile --open` and `profile-open`
record a fresh profile; `profile-view` opens the saved result. Report the
Linux perf-event setting without modifying it.

Probe only selected tools. Distinguish a missing executable from a failed
launch or version probe, preserve the failure diagnostic, and give the exact
Cargo or rustup install instruction. See the root report and validation tool
instructions. Browser opening must pass paths as data, including through the
native Windows API; a missing desktop opener should print the report path.

Keep provider declarations and scripts aligned by review, never by parsing
workflow files in the xtask. Retain the existing Python candidate binder and
protected reporter because they run before candidate execution or credential
creation. Do not replace mature helpers or their callers without approval.
No image workflow or MCP server exists here, so omit those task handles.

The downstream registry includes `tests/downstream/v1alpha1-api` to exercise
explicit and default paths against the same selected traits dependency. Keep
it independent from product feature selection, alongside the protobuf,
Serde, and resource-policy fixtures.

Run formatting, Clippy with warnings denied, and tests for both workspaces via
`cargo xtask check`. Exercise narrowed selectors, feature combinations,
report generation, aliases, tool errors, and profiling artifact selection.
Optional report tools and browser access are not required by the default gate.

## Release boundaries

The only provider-specific namespace is `cargo xtask github`. Limit it to typed
release qualification and finalization for the exact compiled repository and
source-version package policy. Accept tokens only through environment
variables. Do not add an API passthrough, accept tokens as CLI arguments, or
parse, embed, test, or snapshot workflow YAML, triggers, permissions, job names,
Action pins, or secrets.

Release commands have these boundaries:

- `cargo xtask release activate --version <MAJOR.MINOR.PATCH>` selects the
  unpublished `<MAJOR.MINOR.PATCH>-rc.0` coordination safety stub from exact
  clean `origin/main`. It does not invoke release-plz or edit changelogs,
  leaves only the root `Cargo.toml` changed, and never updates a remote ref.
- `cargo xtask release prepare --base-ref refs/heads/main --version <SEMVER>` runs
  pinned release-plz
  update locally and may change only expected manifests and changelogs. When
  selecting the first release from an `rc.0` stub, starting its derived version
  as a prerelease, starting `rc.1` of the immediate next patch from unchanged
  stable package contents, advancing an unchanged `rc.N` to its next ordinal,
  or promoting the current same-version prerelease to stable, its bounded
  fallback uses pinned release-plz set-version after update, restores member
  version inheritance,
  and verifies release-plz's internal dependency synchronization. It rejects
  every other derived-version mismatch, refuses a pre-existing root lockfile,
  and removes only a root lockfile generated by its bounded tool invocation.
- `cargo xtask release check --base-ref refs/heads/main --version <SEMVER>` is
  non-publishing and requires
  the exact selected packages, versions, dependency order, and one crates.io
  traits version matching their shared exact or patch-compatible requirement,
  without any forge credential. Select four packages before `0.6` and
  five from `0.6` onward, including RCs; preserve the historical configuration
  for recovery.
- `cargo xtask github release qualify` reads exact GitHub and crates.io state
  and emits bounded workflow outputs without mutation.
- `cargo xtask github release finalize` uses a repository-scoped App token only
  after registry confirmation to create or verify deterministic annotated tags
  and immutable, zero-asset Releases.

Keep the root workspace lockfile untracked and keep `xtask/Cargo.lock`
committed. Run formatting, Clippy with warnings denied, and the xtask tests for
every change. Preserve bounded process output, safe-file handling, exact
package policy, and focused rejection tests.

The release commands may compare reviewed path names and opaque Git
blob identities across exact commits solely to prove release-policy provenance.
This narrow exception permits no workflow-content parsing, semantic validation,
provider-policy snapshots, or general workflow checks. Keep the required path
set and activation anchor under protected `main`; source trees remain data.

`release prepare` and `release check` take `--base-ref refs/heads/main` or a
canonical `refs/heads/support/M.N`. Detached checkouts must supply it. A named
local branch may infer `main` only when it contains current `origin/main`.
Support versions must match their base; preparation requires the next patch
or the next RC for that patch. Keep `release activate` main-only.

`github release start-support --repository OWNER/REPO --version M.N.P` is
read-only. It binds the compiled repository and package family, checks exact
current-main policy, verifies annotated App-tagged published source archives,
and requires a stable main successor outside the old line. It prints the
absent-ref push and a proposed enumerated inventory. It grants no activation
or publication authority. Never replace its opaque Git blob comparisons with
workflow-content inspection.

`github release rebind-policy` is read-only and fetches exact protected refs
anonymously into an isolated temporary object database. Local use requires
`--repository`; Actions binds the default repository and main ref. Carry the
qualified base, source, version, and fresh/recovery operation explicitly.

Support qualification and finalization validate the reviewed per-line
inventory. Current main selects the active line, fixed anchor, and required
paths. A fresh source must be the protected support tip and match current
policy. Recovery retains the original source on that lineage and checks
`source blob == recorded blob == historical main blob`; the historical main
commit must remain an ancestor of current main. Never let candidate-selected
paths replace the trusted historical inventory or initial main seed.
