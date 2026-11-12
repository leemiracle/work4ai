# Sign and verify YAML with SSH-agent and GitHub keys

In this example, you sign and verify YAML documents with `yaml-sigil`
signatures using common `ssh` keys, then use GitHub to bind an identity to its
public keys.

> [!WARNING]
> Use this example for local experimentation. A matching signature does not
> validate the document's contents or authorize its use. Create a protected
> disposable demo key and review any agent confirmation before signing.

## Before you begin

These instructions target Linux with Bash and OpenSSH. You need Rust, Cargo,
`ssh-agent`, `ssh-keygen`, and `ssh-add`. The GitHub steps also need `gh` and
an authenticated GitHub account with permission to add and remove SSH signing
keys. The example itself makes anonymous discovery requests and never reads
a GitHub token.

Clone this repository and `cd` into its root; use one Bash session throughout.
Build the example once, then call `target/debug/examples/github-keys` directly.
Generated documents and public registration records stay under
`target/github-keys-demo/`. The private key stays in `~/.ssh/`.

```shell
cargo build --package yaml-sigil-examples --example github-keys
mkdir -p target/github-keys-demo
```

Signing with `--output` refuses existing paths. When repeating the walkthrough,
keep earlier output or explicitly remove only the generated files you intend
to replace. Do not overwrite an existing key.

## Walkthrough

### 1. Check the agent

```shell
ssh-add -l -E sha256
```

An exit status of `0` lists loaded keys. Status `1` with “The agent has no
identities” means the agent is reachable but empty; continue to key setup.
Status `2` means the agent cannot be reached. On Linux, start one for this
shell if your desktop does not already provide it, then repeat the check.

```shell
eval "$(ssh-agent -s)"
ssh-add -l -E sha256
```

An empty agent is expected after starting a new one.

### 2. Create and load a protected demo key

Enter a **non-empty passphrase** at the local `ssh-keygen` prompt and confirm
it. Enter it again when `ssh-add` asks. Keep it out of chat, logs, command
arguments, and repository files. The guard below refuses existing files and
symlinks at either demo path. If it refuses, inspect the existing key before
deciding whether to use it in a separate run.

```shell
demo_key="$HOME/.ssh/id_ed25519-github-yaml-sigil-signing-demo"
if [ -e "$demo_key" ] || [ -L "$demo_key" ] ||
   [ -e "$demo_key.pub" ] || [ -L "$demo_key.pub" ]; then
  printf '%s\n' 'Demo key path already exists; stopped before key creation.' >&2
else
  (umask 077; ssh-keygen -t ed25519 -C yaml-sigil-demo -f "$demo_key") &&
    ssh-add "$demo_key"
fi
```

Continue only after creating a passphrase-protected key and loading it
successfully. Capture its fingerprint for later commands.

```shell
demo_fingerprint="$(ssh-keygen -lf "$demo_key.pub" -E sha256 | awk '{print $2}')"
printf '%s\n' "$demo_fingerprint"
ssh-add -l -E sha256
```

The fingerprint must appear in the agent list. Protection belongs to key
setup and your agent. The example uses the SSH-agent interface and cannot
determine whether an agent protects a private key with a passphrase, a
keychain, or another mechanism.

### 3. Sign offline

Review the local unsigned fixture, then select the demo key by fingerprint.
No `--signer` is needed and no GitHub discovery occurs.

```shell
cat examples/github-keys/fixtures/unsigned.yaml
target/debug/examples/github-keys sign \
  --key-fingerprint "$demo_fingerprint" \
  --input examples/github-keys/fixtures/unsigned.yaml \
  --output target/github-keys-demo/signed-offline.yaml
```

Expect a matching public-key fingerprint and a successful write status on
stderr. The new file contains only the signed artifact. Agent-only signing
omits `keyid` because an agent identity does not identify a GitHub account.
Without a fingerprint, signing refuses multiple supported keys.

### 4. Verify without a signer

Try all supported public identities in the current agent, then select only
the demo fingerprint. Both commands verify locally and request no signatures.

```shell
target/debug/examples/github-keys verify \
  --input target/github-keys-demo/signed-offline.yaml
target/debug/examples/github-keys verify \
  --key-fingerprint "$demo_fingerprint" \
  --input target/github-keys-demo/signed-offline.yaml
```

Both should end with `Signature verified (N payload bytes).` and exit status
`0`. Verification leaves stdout empty and never prints unverified payloads.
The agent must remain reachable when you omit `--signer`.

### 5. Verify with a signer

Supply the complete OpenSSH public-key line. This verifies without an agent
or GitHub discovery. `--signer` takes a username or a quoted public-key line,
not a filename or fingerprint.

```shell
target/debug/examples/github-keys verify \
  --signer "$(cat "$demo_key.pub")" \
  --key-fingerprint "$demo_fingerprint" \
  --input target/github-keys-demo/signed-offline.yaml
```

Expect success. Now supply the published fixture's different public key.
Expect a nonzero exit and a signature mismatch, even though your agent still
holds the correct demo key. The explicit signer is a strict restriction.

```shell
target/debug/examples/github-keys verify \
  --signer "$(cat examples/github-keys/fixtures/ddurst-nvidia.pub-key)" \
  --input target/github-keys-demo/signed-offline.yaml
```

### 6. Verify the published fixture

> [!WARNING]
> The username command contacts GitHub's anonymous authentication-key and
> signing-key endpoints. It may fail because of network access or an anonymous
> API rate limit. A username trusts GitHub's current account-to-key association;
> it provides no identity continuity after account compromise, key replacement,
> or [username reuse](https://docs.github.com/en/account-and-profile/concepts/username-changes).
> Verification establishes neither signing time nor freshness and does not
> prevent replay.

```shell
target/debug/examples/github-keys verify \
  --signer ddurst-nvidia \
  --input examples/github-keys/fixtures/signed.yaml
```

Use the public-key snapshot immediately if discovery is unavailable. This
alternative needs neither GitHub nor an agent.

```shell
target/debug/examples/github-keys verify \
  --signer "$(cat examples/github-keys/fixtures/ddurst-nvidia.pub-key)" \
  --input examples/github-keys/fixtures/signed.yaml
```

Expect success with fingerprint
`SHA256:EVFfVelC8GKlyPd1Tl9KLhtfTqzLkAYXsH6LP7PdCQg`. This is the published
fixture's non-demo key. Leave its registration and signed fixtures unchanged.

### 7. Upload the demo public key

Check which GitHub account `gh` is using.

```shell
demo_account="$(gh api user --jq .login)"
printf '%s\n' "$demo_account"
```

Confirm that this is the account you intend to modify, then upload the demo
public key as a signing key.

```shell
gh ssh-key add "$demo_key.pub" --type signing --title yaml-sigil-demo
```

Save the account's public signing-key records, which include registration IDs
and public-key identities. Identify your new entry by its public key, since
titles need not be unique. Keep this record until cleanup is complete.

```shell
gh api --paginate --slurp user/ssh_signing_keys \
  > target/github-keys-demo/registrations.json
```

If upload reports an error, check [SSH and GPG keys](https://github.com/settings/keys)
before retrying. If any later step fails, remove the demo registration using
step 10 before ending the walkthrough.

### 8. Sign and verify through GitHub discovery

Select the confirmed account and the demo fingerprint. Discovery reads both
its authentication and signing key lists. The demo needs only a signing
registration. Anonymous API limits still apply, even though `gh` is logged in.

```shell
target/debug/examples/github-keys sign \
  --signer "$demo_account" --key-fingerprint "$demo_fingerprint" \
  --input examples/github-keys/fixtures/unsigned.yaml \
  --output target/github-keys-demo/signed-github.yaml
target/debug/examples/github-keys verify \
  --signer "$demo_account" --key-fingerprint "$demo_fingerprint" \
  --input target/github-keys-demo/signed-github.yaml
```

Expect signing and verification success with the demo fingerprint. Signing
includes the matching discovery URL as an optional, unsigned `keyid` hint.
Neither command falls back to unrelated agent keys if the account or
fingerprint restriction fails.

### 9. Verify the document offline

Verify the new artifact using the agent's public identities, then the explicit
public key. Neither command resolves its `keyid` URL.

```shell
target/debug/examples/github-keys verify \
  --key-fingerprint "$demo_fingerprint" \
  --input target/github-keys-demo/signed-github.yaml
target/debug/examples/github-keys verify \
  --signer "$(cat "$demo_key.pub")" \
  --input target/github-keys-demo/signed-github.yaml
```

Both should succeed. You can choose a public key independently of the
artifact's unsigned hint. Treat that choice as your trust decision.

### 10. Remove the demo registration

Open [SSH and GPG keys](https://github.com/settings/keys) for the account from
step 7. Find the `yaml-sigil-demo` signing key, check that its fingerprint
matches `demo_fingerprint`, and click **Delete**. Confirm that the entry is
gone. Leave your other keys, including the published fixture's key, in place.

Repeat step 9 after removal; offline verification still succeeds. Removing a
GitHub registration does not change signatures or revoke a locally trusted
public key. Username discovery no longer includes the removed registration.
Your local key files and loaded agent identity remain.

## Key selection

Omitting `--signer` uses public identities from your SSH agent. An explicit
username or public key restricts the accepted keys. `--key-fingerprint SHA256:…`
further restricts either mode. Signing needs one matching agent key;
verification tries the selected public keys until one verifies.

## Read and write documents

Both commands require `--input <FILE>`, `--input <URL>`, or `--input stdin`.
Documents are capped at 4 MiB, including signed output. `stdin` reads standard
input; `./stdin` names a file with that basename.
HTTP and HTTPS input URLs are fetched anonymously with a 20-second timeout.
The SSH agent may impose a smaller signing-request limit. Signing appends a
missing final newline to a nonempty payload and preserves the returned artifact
bytes without reserialization. The 4 MiB bound is example policy, separate
from the 16,384-octet signature-carrier constraint.

For standard input, use the document produced in step 3.

```shell
target/debug/examples/github-keys verify \
  --signer "$(cat "$demo_key.pub")" --input stdin \
  < target/github-keys-demo/signed-offline.yaml
```

You can also read a URL. This URL targets the published fixture on `main`.
If the URL is unavailable, use the local fixture instead.

```shell
target/debug/examples/github-keys verify \
  --signer "$(cat examples/github-keys/fixtures/ddurst-nvidia.pub-key)" \
  --input https://raw.githubusercontent.com/NVIDIA/yaml-sigil-rs/main/examples/github-keys/fixtures/signed.yaml
```

URL input makes a network request even with an explicit signer. Review a
local copy before signing. URL input is signed without a preview; HTTP permits
substitution in transit and HTTPS authenticates only the server connection.

Omitting `--output` writes the exact signed artifact to stdout. Progress and
results stay on stderr, ending with `====== STATUS ======`. Keep the streams
separate when capturing a YAML artifact; combining them produces a transcript.
Payloads may contain terminal controls, so send untrusted output to a new file
with `--output`.

### Progress stages

Signing checks the agent before reading input or contacting GitHub.

```text
====== 1/6 Check SSH agent ======
====== 2/6 Read unsigned YAML ======
====== 3/6 Resolve public keys ======
====== 4/6 Select SSH-agent key ======
====== 5/6 Sign YAML through the SSH agent ======
====== 6/6 Write signed YAML ======
====== STATUS ======
```

Verification checks agent availability only when no signer is supplied.

```text
====== 1/5 Check key source ======
====== 2/5 Read signed YAML ======
====== 3/5 Check signature metadata ======
====== 4/5 Resolve public keys ======
====== 5/5 Verify the signature ======
====== STATUS ======
```

## Fixtures

These fixtures distinguish signature validity from application validity.

| File | Expected result | Reason |
|------|-----------------|--------|
| [`unsigned.yaml`](./fixtures/unsigned.yaml) | Failure. | No signature is present; this is the input used to create the signed sample. |
| [`signed.yaml`](./fixtures/signed.yaml) | Success. | The signature matches the unchanged payload and the recorded Ed25519 key. |
| [`tampered-payload.yaml`](./fixtures/tampered-payload.yaml) | Failure. | The port changes from `8080` to `8081` without a new signature. |
| [`tampered-signature.yaml`](./fixtures/tampered-signature.yaml) | Failure. | A signature byte changes while the payload stays the same. |
| [`changed-keyid.yaml`](./fixtures/changed-keyid.yaml) | Success. | Changing the unsigned `keyid` hint leaves the signature intact; verification still uses the caller-selected signer. |
| [`signed-application-invalid.yaml`](./fixtures/signed-application-invalid.yaml) | Success. | The signature matches even though `port: not-an-integer` violates the illustrative application's integer-port rule. |

The last sample signs [`application-invalid.yaml`](./fixtures/application-invalid.yaml).
The example performs no application-level port check. Syntactically acceptable
YAML and a matching signature do not imply a usable application configuration.
The `changed-keyid.yaml` sample verifies in both username and direct-key modes
because changing the hint leaves the payload's cryptographic signature intact.
The unsigned and tampered samples fail in both modes.

### Fixture provenance

The `signed.yaml` and `signed-application-invalid.yaml` samples were created
with a dedicated `ddurst-nvidia` Ed25519 signing key through an SSH agent. The
[public-key snapshot](./fixtures/ddurst-nvidia.pub-key) contains that key's public
half. Live verification resolves keys through both of the account's public
key lists.
The matching fingerprint is:

```text
SHA256:EVFfVelC8GKlyPd1Tl9KLhtfTqzLkAYXsH6LP7PdCQg
```

The modified samples derive from `signed.yaml` through the changes listed
above.

## SSH agent signing

[`agent.rs`](./agent.rs) uses `russh` to connect to `SSH_AUTH_SOCK`. Start and
configure your agent outside the example. The example does not load, decrypt,
add, or remove keys.

The adapter implements `AsyncProviderSigner` and forwards the exact message
bytes supplied by `yaml-sigil`. `AsyncProviderSigningKeyBuilder::build`
validates the public key without a synthetic signing request. Qualified
signing verifies each returned signature locally before emitting an artifact.
The agent's ordinary Ed25519 signature supplies the required 64-byte `R || S`.
An OpenSSH `ssh-keygen -Y sign` SSHSIG envelope signs different bytes and
cannot be substituted. See the [crypto-provider guide](../../docs/crypto-providers.md).

Connection, key listing, and signing each have a 30-second timeout. The
example makes one signing request and never retries it. Failure or cancellation
closes the signing connection; it does not prove the agent did not sign.
Verification with an explicit signer needs no agent. Agent-only verification
requests public identities and performs the signature check locally; it never
requests a signature.

## Discovery and verification

[`main.rs`](./main.rs) keeps the public library calls visible. It binds the
agent signing key or calls `pre_verify_yaml_with_resource_limits`, checks the
signature metadata, and uses
`verify_from_pre_verify_yaml` with each caller-selected candidate Ed25519 key.
It accepts only `VerifierState::Verified`. The caller retains responsibility
for any use of the authenticated payload.

[`input.rs`](./input.rs) reads document bytes from the caller-selected source.
A document's origin never changes the expected account or key-discovery URLs.

[`github.rs`](./github.rs) implements the example's URL and HTTP policy.
It accepts a GitHub username and constructs two URLs.

- `https://api.github.com/users/USERNAME/keys`.
- `https://api.github.com/users/USERNAME/ssh_signing_keys`.

The username argument must omit the URL and `@` prefix.
This prevents credentials, alternate ports, extra path components, query strings,
or fragments from entering the URLs. Signing emits the URL containing the
matching key as the optional `keyid` hint. If a key appears in both lists,
the authentication-key URL is used. Verification selects both endpoints from
`--signer` independently of the artifact's hint. Requests use GitHub REST API
version `2026-03-10` and accept JSON. The example rejects redirects, non-`200`
statuses, and unexpected media types. Each request has a 20-second timeout.
A complete lookup is limited to 10 pages per resource and 256 KiB of response
bodies across both resources. These are example operational limits, separate
from artifact conformance; exceeding either limit fails discovery without
using a partial key set.

The example requests 100 entries per page and reads the next page number from
GitHub's `Link` header. Every request retains the caller-selected username,
including when GitHub's links use a numeric account alias. Unexpected origins,
resources, repeated or skipped page numbers, and changed page sizes are errors.
Discovery finishes both lists before selecting a signing key or verifying a
signature. An error in either list fails the operation even if a previous
response contained a matching key.

[`keys.rs`](./keys.rs) shares key decoding, admissibility checks, and fingerprint
filtering between GitHub discovery, explicit public keys, and agent identities.

Each JSON record must contain one OpenSSH public-key line in its `key` field.
The `ssh-key` parser decodes that line. The
base64 field contains an SSH wire blob with the algorithm and public-key data.
The example passes the extracted point to
`resolve_ed25519_verifying_key` for the library's admissibility check.
It deduplicates supported Ed25519 keys across both lists, reports their count,
and tries them until one verifies. A mismatch with one candidate does not skip
the remaining keys; verification fails if none match. Either list can be empty
or contain only unsupported algorithms when the other list has a supported
key. Malformed lines, inadmissible Ed25519 keys, and a combined list without
supported keys produce errors.

### GitHub key purposes

GitHub documents separate
[authentication-key](https://docs.github.com/en/rest/users/keys#list-public-keys-for-a-user)
and
[SSH signing-key](https://docs.github.com/en/rest/users/ssh-signing-keys#list-ssh-signing-keys-for-a-user)
REST resources. This example accepts ordinary Ed25519 keys from either
resource, regardless of their GitHub registration purpose. An existing
authentication key or a signing-only key is sufficient. GitHub's registration
categories do not change what `yaml-sigil` verifies or authorize the contents
of arbitrary YAML documents or their use by an application.

The `https://github.com/USERNAME.keys` shortcut exports authentication keys
without purpose metadata and can omit signing-only registrations. This example
queries both REST resources to include either registration type.

### GitHub API rate limits and offline runs

Both public key lists require no token or login. GitHub applies an anonymous
API rate limit shared by requests from the same public IP address. On a rate
limit response, the example reports `Retry-After` seconds or the Unix timestamp
in `X-RateLimit-Reset` when available. Retry after that time. It does not prompt
for GitHub credentials or retry through an authenticated path.
See [GitHub's rate-limit documentation](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

## Find the endpoint for other VCS systems

> [!NOTE]
> Only GitHub's public authentication-key and signing-key APIs are implemented
> here. The other rows identify discovery options for another application;
> supplying those URLs as `--signer` fails.

| Host | Account public-key URL | Response and access |
|------|------------------------|---------------------|
| [GitHub](https://github.com/) | `https://github.com/USERNAME.keys` | Public OpenSSH text export. |
| [GitHub SSH authentication keys](https://github.com/) | `https://api.github.com/users/USERNAME/keys` | Anonymous, paginated JSON; used by this example. |
| [GitHub SSH signing keys](https://github.com/) | `https://api.github.com/users/USERNAME/ssh_signing_keys` | Anonymous, paginated JSON; used by this example. |
| [GitLab.com](https://about.gitlab.com/) | `https://gitlab.com/USERNAME.keys` | OpenSSH text; instance access rules apply. |
| [Self-managed GitLab](https://about.gitlab.com/) | `https://YOUR-GITLAB-HOST/USERNAME.keys` | OpenSSH text; network and instance sign-in rules apply. |
| [Gitea](https://about.gitea.com/) | `https://GITEA-HOST/USERNAME.keys` | OpenSSH text; profile and instance visibility apply. |
| [Codeberg](https://codeberg.org/Codeberg) | `https://codeberg.org/USERNAME.keys` | OpenSSH text; profile visibility applies. |
| [Forgejo](https://codeberg.org/forgejo), including private instances | `https://FORGEJO-HOST/USERNAME.keys` | OpenSSH text; profile and instance visibility apply. |
| [Bitbucket Cloud](https://www.atlassian.com/) | `https://api.bitbucket.org/2.0/users/{selected_user}/ssh-keys` | Authenticated, paginated JSON. |
| [Bitbucket Data Center](https://www.atlassian.com/) | `https://HOST/rest/ssh/1.0/keys?user=USERNAME` | Authenticated, paginated JSON; target-user permissions apply. |
| [GitLawb](https://github.com/Gitlawb) | Decode the identity's `did:key:z6Mk...` locally. | Embedded Ed25519 public key; no documented `.keys` shortcut in the reviewed source. |

## Adapt the example for P-256

The executable remains Ed25519-only. For a P-256 variant, parse
`ecdsa-sha2-nistp256` with `ssh-key`, require its `NistP256` variant, and
use the native `p256` library to obtain the uncompressed point expected by
`resolve_p256_verifying_key`.

```rust
use anyhow::{Result, bail};
use p256::elliptic_curve::sec1::ToSec1Point;
use russh::keys::ssh_key::{PublicKey, public::EcdsaPublicKey};
use yaml_sigil_verification::v1alpha1::resolve_p256_verifying_key;

fn resolve_ssh_p256(line: &str) -> Result<p256::ecdsa::VerifyingKey> {
    let parsed = PublicKey::from_openssh(line)
        .map_err(|error| anyhow::anyhow!("invalid OpenSSH key: {error}"))?;
    let Some(EcdsaPublicKey::NistP256(point)) = parsed.key_data().ecdsa() else {
        bail!("expected an ordinary P-256 SSH public key");
    };
    let native = p256::PublicKey::from_sec1_bytes(point.as_bytes())
        .map_err(|_| anyhow::anyhow!("invalid P-256 point"))?;
    let uncompressed = native.to_sec1_point(false);
    Ok(resolve_p256_verifying_key(uncompressed.as_bytes())?)
}
```

For P-256 agent signing, an adapter must convert the SSH signature's integer
pair to fixed-width 64-byte `r || s` and use the provider's P-256 slot.
For verification, supply
the resolved key through `PublicKeys.p256` and enable that algorithm in
`VerifierOptions`. Resolve keys from the caller's selected account or explicit
public key, and bind signing to the matching agent key. Keep `keyid`
as an optional hint.

Pass the final message bytes unchanged; the P-256 agent operation must apply
SHA-256 exactly once. Do not substitute an SSH signature blob, DER encoding,
or an SSHSIG envelope, or prehash the message yourself.
The P-256 adaptation test covers public-key conversion and a local library
round trip. It does not implement or test P-256 agent signing.

## Tests and dependencies

```shell
cargo test --package yaml-sigil-examples --example github-keys
cargo xtask check
```

The target's `test = true` registration makes the existing workspace CI run
its tests. They cover CLI arguments, file/URL/stdin signing and verification,
stdout artifact bytes, progress steps, agent key selection, malformed
key records, pagination, later-page failures, anonymous rate limits, HTTP
response and read failures, document size boundaries, cumulative discovery limits,
caller-selected URLs, agent-only and direct-key signing and verification
without network
access, optional and changed `keyid` hints, fixture outcomes in both modes,
and the P-256 public-key recipe. Agent tests check exact message bytes,
refusals, malformed replies, wrong-key signatures, timeouts, and cancellation
without retries or partial artifacts.
The tests use synthetic private keys or the recorded public-key snapshot.
HTTP responses and agent peers are supplied locally to keep tests offline.
Live HTTP transport and GitHub verification are separate manual checks.

On Unix, run this additional test with OpenSSH installed. It starts an
isolated agent and loads a synthetic key without changing your existing agent.

```shell
cargo test --package yaml-sigil-examples --example github-keys \
  openssh_agent_round_trip -- --ignored
```

The example uses `clap`, `anyhow`, `russh` `0.63.3` and its `ssh-key` re-export,
Tokio, `ureq` `3.4`, `serde_json`, and the workspace's RustCrypto bindings and public
`yaml-sigil` APIs. They are development dependencies of the unpublished
example package, with usage documented in [`Cargo.toml`](../Cargo.toml).
