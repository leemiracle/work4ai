# Examples

These instructions supplement the repository-root
[`AGENTS.md`](../AGENTS.md) for work under `examples/`.

## Maintain the example index

Keep [`README.md`](./README.md) as the human-facing index of runnable examples
and shared support modules. Update it in the same change whenever you add,
remove, or rename an example or support module, or change an example's options,
input sources, output, supported features, limitations, dependencies, or test
commands. Keep source links and copyable run commands accurate.

Keep the introduction and index general. Put options, output conventions,
and limitations specific to an example or related group in that group's
section.

Keep shared agent instructions in this file and example-specific walkthroughs in
scoped `AGENTS.md` files. Put implementation explanations in the
example source so readers can follow the code without switching to the README.
Explain the purpose of each stage and the public contracts it demonstrates.
More inline commentary is appropriate here than in production library code.

Import implementation APIs through their explicit `v1alpha1` namespaces.
The unqualified defaults remain compatible; dedicated downstream regressions
exercise interchange between both styles. Keep examples on the traits release
selected by the workspace instead of depending on unreleased trait paths.

## CLI examples

Use `clap` derive for CLI argument parsing. Keep each command's options suited
to the behavior it demonstrates; unrelated examples need not share an input
format, algorithm, or output convention.

Keep shared CLI code in [`cli-common/`](./cli-common/). Reuse applicable
parsing, input/output, operation, and test helpers when examples demonstrate
the same flow. Examples using the same provider can share native adapters
there; link to those adapters from each entry point. Keep calls demonstrating
a distinct API choice visible in its entry point. Explain which helpers are
example scaffolding and which traits and functions belong to the public
library API.

Test every root parser with
`clap::CommandFactory::command().debug_assert()`, including commands assembled
through shared helpers. Exercise the same operation that the CLI invokes.

The provider-specific sections below apply when their named examples are
present. They do not require unrelated examples to implement provider APIs.

## Local cryptographic provider examples

The following conventions apply specifically to `ring_provider.rs` and
`aws_lc_provider.rs` and their shared implementation in `cli-common/`.

- Keep their equivalent options and behavior uniform.
- Accept unsigned YAML through `--payload FILE` or `--payload stdin`.
  Treat the argument as a filename or the literal `stdin`, never inline YAML.
  Omitting it displays and signs a document identifying itself as the default.
  Propagate input errors instead of substituting the default document.
- Support `--key-type p256` and `--key-type ed25519`, with P-256 as the default.
  Generate a fresh random key through the selected provider for each run.
- Print the unsigned document, public key and its type, verification result,
  and complete signed YAML artifact in that order. Label the public key's
  base64 encoding. Never print private keys or seed material.
- Delimit each stage with `====== Title ======` and put YAML below it. Keep
  the signed artifact last and preserve its returned bytes without
  reserializing. Explain that the full transcript is not one YAML stream.
- Keep both algorithms on qualified signing. Require qualified P-256
  verification. Make the native Ed25519 verification limitation and explicitly
  unqualified path visible in comments, help, and output. Never retry a failed
  verification through another provider or assurance path.
- Keep native keys behind provider handles and preserve each verifier's own
  public-key binding. Explain hashing, signature format, and error
  classification beside the native operations.
- Test both key types with default, file, and standard-input documents.
  Verify the printed artifact using the printed public key, including any
  authorized final-newline normalization.

## Async provider example

Keep `async_provider.rs` focused on awaitable P-256 operations through a
simulated service. Demonstrate both qualified and explicitly unqualified
choices, borrowed clients and handles, and separate operational failures from
signature mismatch. Keep provider adapter implementations in the entry point
and reuse the applicable YAML input/output helpers under `cli-common/`.

Keep blocking cryptography in the worker and await replies in the adapters.
Do not require a live HSM, KMS, SDK, or credentials to run the example or its
tests. Explain where real integrations own scheduling, timeouts, and remote
cancellation. Test both modes with default, file, and standard-input documents
and verify each printed artifact with its printed public key. Label both
signing and verification modes in the transcript.

## Explicitly unqualified provider example

Keep `ring_unqualified_provider.rs` focused on unqualified signing and
verification for both P-256 and Ed25519. Share native adapters with the other
`ring` example, but keep the unqualified builders and operation calls in this
entry point. Reuse applicable key selection and YAML transcript helpers.

Make the skipped signing output check, skipped verification qualification,
and implementer-owned risk prominent in the module introduction, CLI help,
comments beside each unqualified builder, runtime output, and README. Explain
the retained structural checks and the known Ed25519 acceptance difference.
Never imply that a generated-key round trip establishes full compatibility.

Use the local examples' key and payload options and four output stages, with
an additional warning stage first. Test both keys with default, file, and
stdin input and independently verify the printed artifacts. Neither the
example operation nor its tests require provider qualification.

## SSH-agent and GitHub key example

Follow [`github-keys/AGENTS.md`](./github-keys/AGENTS.md) for its protected-key,
offline-first walkthrough and exact registration cleanup. Keep the
[human walkthrough](./github-keys/README.md) and index aligned with optional
signers, fingerprint filtering, and public-only agent verification. Preserve
the published fixture's non-demo key and signed bytes.

## Validation and packaging

Keep the example package unpublished and its dependencies under
`dev-dependencies`. Register runnable Cargo examples explicitly in
`Cargo.toml` with `test = true` so the existing workspace CI compiles them
and executes at least a basic operation.

If a crypto provider is not supported on a platform, exclude that example
from CI on that platform and note why. These examples demonstrate integration
where it is possible; an individual provider's platform requirements must not
stall development. Keep supported combinations running, and record each
exclusion and its reason beside the configuration and in the README index.

Run focused tests while editing, then the repository's complete local CI gate
before committing. Run these commands from the repository root.

```shell
cargo test --package yaml-sigil-examples
cargo xtask check
```

Keep executable build outputs local and ephemeral. Follow the repository-root
instructions for hosted test admission and publication boundaries.
