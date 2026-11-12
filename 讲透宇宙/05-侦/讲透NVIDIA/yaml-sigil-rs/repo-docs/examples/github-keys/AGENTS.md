# GitHub key walkthrough

Follow the repository-root and [parent instructions](../AGENTS.md). Keep the
[README walkthrough](./README.md#walkthrough) as the source of copyable
commands for Linux readers. Build once from the repository root and invoke
the executable directly, as the README shows. Guide a human one step at a
time, or execute already-authorized steps sequentially. Check each expected
result before continuing.

## Protection and platform setup

This demo was developed on Linux. Agents may adapt shell syntax, paths, agent
services, Unix sockets or Windows named pipes, and secure prompting or keychain
integration for their platform. Preserve key selection and cleanup semantics.
Distinguish tested instructions from adaptations that have not been exercised.

The executable connects to `SSH_AUTH_SOCK` on Unix. On Windows it uses the
named pipe in `SSH_AUTH_SOCK`, defaulting to `\\.\pipe\openssh-ssh-agent`.
The Linux walkthrough and isolated OpenSSH tests have been exercised; macOS
keychain and Windows service adaptations have not. Keep platform adaptations
and agent execution guidance here, outside the Linux README.

Prefer a suitable protected ordinary Ed25519 key or a protected creation flow.
For a new walkthrough key, use the README's demo path and refuse existing files
or symlinks. Require a non-empty passphrase through a local secure prompt when
using passphrase protection. Keep passphrases out of chat, logs, command-line
arguments, and repository files. Load the key through the platform's agent
setup before running the example.

If practical protection cannot be integrated, explain why and display a
`[!WARNING]` before using an unprotected disposable key. Do not silently choose
that fallback for convenience. State that the fallback key has no encryption
at rest and preserve the same registration cleanup. The example uses the
SSH-agent interface and cannot determine how the agent protects its keys.
It cannot load or unlock keys itself. Hardware security-key variants such as
`sk-ssh-ed25519@openssh.com` are outside its ordinary Ed25519 support.

## Walkthrough sequence and expected outcomes

1. Check the agent. Distinguish unreachable service or socket from a reachable
   agent with no identities. Resolve availability before signing or agent-only
   verification.
2. Create and load a protected demo key. Confirm the public fingerprint appears
   in the intended agent. An isolated agent avoids changing existing identities.
3. Sign the local unsigned fixture without `--signer`, selecting the demo
   fingerprint. Expect a new artifact under `target/github-keys-demo/` and no
   GitHub request. Preserve existing outputs unless replacement is authorized.
4. Verify without a signer, first with all supported identities and then with
   the fingerprint. Both should succeed through local verification with no
   signing request.
5. Verify with the demo public key and expect success. Supply the different
   fixture public key and expect rejection, even while the demo key is loaded.
6. Verify the published `ddurst-nvidia` fixture. Explain anonymous endpoint
   availability and rate limits beside the command, then offer the immediately
   following public-snapshot command. Both should match the fixture fingerprint
   when discovery is available. Preserve its non-demo key, registration, public
   snapshot, signatures, and fixture bytes.
7. Confirm the GitHub account and register only the demo public half as a
   signing key. Record the baseline registrations, account, public identity,
   and new registration ID before proceeding. Preserve pre-existing entries.
8. Sign and verify using the account and demo fingerprint. Expect discovery of
   both authentication and signing keys, with a match to the demo key. An
   explicit signer and fingerprint always intersect; never retry with unrelated
   agent keys after a mismatch.
9. Verify the new document through agent identities and the explicit public
   key. Both should work without GitHub discovery, ignoring the unsigned
   `keyid` hint as an authority source.
10. Remove exactly the registration created in step 7. Recheck the account,
    numeric ID, public-key identity, title, and exclusion from the baseline
    before deletion. Confirm absence through a successful listing and preserve
    pre-existing registrations. Repeat offline verification after removal.

## Cleanup ownership

The human walkthrough uses GitHub's settings page for removal. For automated
execution, bind cleanup to the recorded numeric registration ID and public-key
identity, with the checks below.

Track any registration created during execution and clean it up even when a
later step fails. Arrange a cleanup handler before upload when automating the
walkthrough. If upload returns an ambiguous error, compare the recorded
baseline with a fresh listing using the demo public identity before retrying
or deleting. Never delete by title alone or infer absence from a network error.

Keep public recovery records under `target/github-keys-demo/` until cleanup is
confirmed. Report an unresolved registration explicitly with its ID and public
fingerprint. Local key-file deletion and agent-entry removal require separate
explicit instructions. Do not remove pre-existing agent identities or keys.

## Implementation and verification

Keep shared key decoding and filtering in `keys.rs`, GitHub discovery in
`github.rs`, and agent transport and signing in `agent.rs`. Keep public library
calls visible in `main.rs`. Verification may list identities but must never
request signatures. Explicit-public-key and username verification must work
without an agent. Preserve Ed25519-only support, bounds, timeouts, qualified
signing, artifact-only stdout, numbered progress, and the status separator.

Use `clap` derive and retain the parser construction invariant test. This
unpublished Cargo example keeps reusable scaffolding in its local modules;
do not expose it as a published library API or add MCP or tracing setup.
Run the README's focused tests and isolated OpenSSH test, then the parent's
full CI gate. Test offline execution, fingerprint filtering, duplicate and
unsupported identities, ambiguity, unavailable agents, strict mismatches,
fixture outcomes, and cleanup selection that preserves pre-existing entries.
Exercise the walkthrough when starting from the repository root and example
directory, changing to the repository root once before following its commands.
