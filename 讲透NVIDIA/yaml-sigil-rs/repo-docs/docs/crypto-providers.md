# Cryptographic providers

`yaml-sigil-rs` can prepare and verify artifacts while your signing callback
or provider adapter performs the cryptographic operation. Your private key
can remain in a native library, an HSM, or a KMS. You can also implement the public
[`yaml-sigil-traits`](https://crates.io/crates/yaml-sigil-traits) contracts
directly when you need control over the complete operation.

The default convenience APIs accept `ed25519-dalek` and `p256` keys. Choose
them when your application already holds those RustCrypto key types.

Select implementation contracts through `yaml_sigil_signing::v1alpha1` and
`yaml_sigil_verification::v1alpha1`, including their `provider` and
`async_provider` modules. The unqualified defaults name the same traits,
provider bindings, and operations. Version selection requires no adapter
conversion or new qualification; use the traits release selected by your
dependency graph for direct trait implementations.

## Choose an integration path

| Path | What you gain | What you supply or give up |
|------|---------------|---------------------------|
| Qualified provider operations. | This workspace's artifact processing, key and signature checks, per-output signing verification, and finite verification-provider qualification. | A signing callback or provider adapter that meets the boundary's cryptographic behavior. Verification qualification needs the exact configured instance to bind the public test keys. |
| Explicitly unqualified provider operations. | The same artifact processing and structural checks, while using a provider with different cryptographic acceptance behavior or one that cannot run the qualification suite. | Your own evidence that its signing and verification behavior fits your requirements. Signing skips output self-verification; verification skips the fixed suite. |
| Direct `yaml-sigil-traits` implementation. | Your own associated key types, operations, async strategy, and choice of implementation helpers. No provider wrapper or qualification prerequisite. | The complete operation and evidence for its capabilities and conformance claims. The traits do not automatically run this workspace's checks. |

Choose a path based on which parts of the operation your application owns.
Unqualified operations perform cryptographic signing or verification;
the name identifies which additional evidence this workspace does not require.
Direct trait implementations can use `yaml-sigil-core` and other helpers
selectively, or own the operation entirely. Implementing a trait does not
establish conformance, and choosing that path does not fix a provider's
cryptographic compatibility difference. That difference may be acceptable
for your application.

Choose signing and verification independently. For example, the native
[`ring` and `aws-lc-rs` examples](../examples/README.md#local-cryptographic-providers)
use qualified signing for both algorithms and explicitly unqualified Ed25519
verification. Their pinned native verifiers reject some mixed-order cases
that this implementation accepts. They use qualified P-256 verification.

> [!WARNING]
> Unqualified signing skips independent output self-verification, and
> unqualified verification skips the fixed qualification suite. You, the
> integration implementer, own the additional risk and compatibility
> assessment. Structural checks cannot detect a validly encoded signature
> for the wrong message or key. A native sign/verify round trip does not prove
> compatibility across all inputs.

The dedicated
[`ring-unqualified-provider` example](../examples/README.md#explicitly-unqualified-provider)
selects that choice for both signing and verification with either algorithm.
It demonstrates retained structural checks and native verification without
requiring qualification. Its pinned `ring` verifier has the mixed-order
Ed25519 acceptance difference described above.

## Why bind a key

### Convert P-256 provider encodings

The signing and verification crates re-export two shared helpers from
`yaml_sigil_core::v1alpha1::p256_encoding`. Core-only callers enable the
`p256-encoding` feature explicitly.

| Helper | Accepted input | Output |
|--------|----------------|--------|
| `p256_der_signature_to_raw` | Strict DER with nonzero `r` and `s` below the curve order. | 64 big-endian `r || s` octets, preserving high-S and low-S values. |
| `p256_public_key_to_uncompressed` | A valid 33-octet compressed or 65-octet uncompressed P-256 point. | 65 uncompressed public-key octets. |

The point encodings come from
*Standards for Efficient Cryptography 1 (SEC 1)*. Unsupported tags, malformed
encodings, invalid points, and invalid signature components return
`P256EncodingError`. The helpers use RustCrypto's parsers; conversion does not
prove a signature equation or a provider's nonce behavior. Their rustdoc has
compiling examples and complete input and error contracts.

Apply conversion before binding a provider key or returning a provider
signature. The algorithm validators require uncompressed public keys and raw
signatures. The helper regressions cover padding, scalar ranges,
high-S preservation, invalid points, trailing data, and both compressed-key
parities. Verification regressions check valid converted signatures and
continued rejection of unconverted forms.

### Bind the canonical public key

Select one algorithm and its canonical public key before signing. The
synchronous signing builder validates and stores only that public material;
each operation supplies a callback separately. The async builder also borrows
its adapter. Qualified signing verifies every real output against the bound
key and final message before returning an artifact. A valid signature made
with the wrong private key therefore fails. Neither builder requests a
synthetic signing challenge or private-key bytes.

A verification factory binds exactly the supplied public key to a handle.
Each handle must preserve its own binding when the factory creates another
handle. Store the key or a stable key identifier in each handle. Handles can
share a client, but locking a shared "current key" only serializes access;
another bind can still change the key that an earlier handle uses.

Both qualification suites keep multiple bindings live and interleave valid
and cross-key checks. They recheck earlier handles after later binds and
require each handle to reject the other key's signature. These tests detect
several caching and handle-reuse mistakes. They do not prove every later
handle is correct.

Public-key validation also runs on the unqualified path. Ed25519 keys use 32
canonical compressed octets and must satisfy this implementation's key
admissibility rules. P-256 uses the 65-octet uncompressed point encoding from
*Standards for Efficient Cryptography 1 (SEC 1)*. Signature structural checks
require canonical Ed25519 `R || S` or in-range P-256 big-endian `r || s`, each
exactly 64 octets. An unqualified operation cannot bypass these checks; use
direct traits if your integration needs to own them.

The artifact's unsigned `keyid` is a lookup hint. It does not authorize a key,
prove identity, or replace a deployment trust policy. Select the artifact form
and trusted keys from application context before verification.

## Synchronous and asynchronous adapters

| Operation | Synchronous contract | Asynchronous contract |
|-----------|----------------------|-----------------------|
| Sign a message with an initialized handle. | Per-operation `FnOnce(&[u8]) -> Result<[u8; 64], SignError>`. | `AsyncProviderSigner`. |
| Sign a P-256 digest. | Qualified `FnOnce(&[u8; 32]) -> Result<[u8; 64], SignError>`. | No separate digest operation. |
| Verify with a bound handle. | `signature::Verifier<[u8; 64]>` and `ProviderVerifier`. | `AsyncProviderVerifier`. |
| Bind public bytes to a verifier. | `ProviderVerifierFactory`. | `AsyncProviderVerifierFactory`. |
| Select qualification. | `VerificationProviderBuilder::qualify` or `build_unqualified`. | `AsyncVerificationProviderBuilder::qualify().await` or `build_unqualified`. |

Pass the complete payload in every signing request. The library applies
authorized YAML final-newline handling before invoking the provider; protobuf
bytes remain unchanged. A message-signing callback or async adapter receives
those final bytes. For P-256 it hashes them with SHA-256 once and returns
64-octet big-endian `r || s`, never DER. Ed25519 returns canonical `R || S`.

`sign_with_p256_digest_provider` prepares the same payload and computes
SHA-256 once for a typed `&[u8; 32]` callback input. The callback signs that
digest without hashing again. The library checks its signature against the
bound key and complete final payload before emission. Independent verification
may hash the payload again. This operation rejects Ed25519 before calling;
there is no Ed25519 prehash or unqualified digest mode. Both P-256 callback
choices leave the profile's CSPRNG nonce sampling to the integration.
The [digest rustdoc example](../crates/yaml-sigil-signing/src/lib.rs) compiles
as part of the signing crate's tests.

Synchronous callbacks can borrow mutable sessions or thread-confined handles.
Bindings and requests remain `Send + Sync` because they store no callback or
private handle. Rust applies thread bounds to each callback's captures when
you move or share it. A shared provider can sign concurrently against the same
binding; local code can create successive callbacks borrowing one mutable
handle. The callback runs synchronously on the calling thread and can block it.
The library invokes it exactly once when the request reaches signing, with no
probe or retry. Earlier rejection makes no call.

Use `signature_signing_callback(&adapter)` to forward an existing
`signature::Signer<[u8; 64]>` implementation. It maps the adapter's error to
`SignError::KeyOperationFailure`, and it adds no unconditional thread bound.
The [compiling provider examples](../crates/yaml-sigil-signing/src/provider.rs)
show local mutable captures, handle reuse, and shared signing.

Verification adapters continue to receive the complete extracted message and
fixed-width signature. P-256 verification qualification requires both high-S
and low-S acceptance. Ed25519 qualification includes canonical mixed-order
inputs accepted by the slot's cofactored verification equation.

### Synchronous signing calls

Construct the public-key binding before signing, then supply a callback to
each operation. Builders and keys own only public-key material; requests
borrow the keys.

| Operation | Call |
|-----------|------|
| Bind an Ed25519 public key. | `ProviderSigningKeyBuilder::ed25519(bytes)` |
| Bind a P-256 public key. | `ProviderSigningKeyBuilder::ecdsa_p256_sha256(bytes)` |
| Sign with a qualified key. | `sign_with_provider(&request, callback)` |
| Sign with an unqualified key. | `sign_with_unqualified_provider(&request, callback)` |
| Sign a P-256 digest. | `sign_with_p256_digest_provider(&request, callback)` |
| Apply resource limits. | Pass `(&request, &limits, callback)` to the corresponding resource-aware operation. |

Supply your own closure or `signature_signing_callback(&adapter)` as the
callback. Callback failures propagate as
`SignOutcome::Signer`; use `SignError::KeyOperationFailure` for SDK failures.
Wrong-key, wrong-message, or malformed qualified output maps to the same
failure.

### Async operation boundaries

The async traits use native returned futures with `Send` guarantees and
`Send + Sync` adapters. An async adapter does not need a synchronous trait
implementation. Its factory's `Verifier<'factory>` associated type can borrow
a client or configuration. Binding can borrow temporary public-key input
until completion; the returned handle cannot retain that input borrow.
Neither the client nor the bound handle needs to be `'static`.

Fetch or initialize a remote signing key and obtain its public bytes before
using `AsyncProviderSigningKeyBuilder`. Its `build` and `build_unqualified`
methods perform local validation. Signing, verification binding,
qualification calls, and signature verification can suspend while awaiting
the provider.

`ProviderAsyncSigner` and `ProviderAsyncVerifier` implement the existing
re-exported `AsyncSigner` and `AsyncVerifier` traits using qualified provider
keys. `UnqualifiedProviderAsyncSigner` and
`UnqualifiedProviderAsyncVerifier` provide the explicit alternatives. Their
associated keys carry the adapter lifetime. The corresponding async free
functions cover these operations and expose metadata and pre-verification reuse.
`DefaultAsyncSigner` and `DefaultAsyncVerifier` perform local synchronous
cryptography when polled. Their futures do not offload that work.

Parsing, structural checks, output assembly, and qualified signing's local
self-verification remain synchronous work around the await. Public bound-key
types hide the implementation's dynamic dispatch. Internally, signing boxes
one future per operation; verification boxes a bound handle and one future
per operation, including qualification operations. The factory binding
contract itself uses a native returned future.

The library chooses no executor or blocking pool. `Send` allows an executor
to move a future between threads; it does not prove an SDK avoids blocking.
Place blocking operations appropriately in your adapter. Own your timeouts,
retry and concurrency policies, credentials, remote error translation, and
request cancellation semantics. Dropping a pending library future drops the
pending adapter future; it cannot promise to cancel an already submitted
remote operation. Dropped qualification exposes no partially qualified
provider.

The [`async-provider` example](../examples/README.md#asynchronous-provider)
uses a blocking worker with a private key store and awaits channel replies.
It demonstrates both choices with fresh P-256 keys and no external service.
The `ring` and `aws-lc-rs` examples demonstrate synchronous adapters only.

The [`github-keys` example](../examples/github-keys/README.md#ssh-agent-signing)
uses `russh` for asynchronous SSH-agent signing with an existing Ed25519 key.
Its [walkthrough](../examples/github-keys/README.md#walkthrough) starts with a
protected demo key and offline signing before introducing GitHub discovery.
Omitting `--signer` uses supported agent identities. A username or explicit
public key restricts the accepted keys. Either mode can filter by fingerprint.
Signing requires one matching agent key, binds its public key, and uses
qualified signing with an artifact limit. Verification tries selected public
keys locally through the default RustCrypto API, without signing requests.
An explicit verification signer needs no agent. The agent interface does not
reveal key protection.
The adapter owns connection and request timeouts. Dropping a signing request
closes its connection without retrying or claiming to undo the agent's work.

## Qualification and error handling

The costs below follow the current implementation's operations and allocation
sites. They are not benchmark timings. Payload size, native library behavior,
SDK scheduling, and service latency determine the cost of your integration.

### One-time qualification

Verification qualification consumes one configured adapter instance, runs a
finite public-only suite, and records each algorithm separately. Reuse that
instance for application bindings. Replacing or reconfiguring it requires
qualification again. State is opaque and non-serializable. A rejected slot
cannot create a qualified key; another qualified slot remains usable.

Qualification provides evidence for compatibility and catches common adapter
mistakes. You still choose and trust the adapter code. An implementation can
recognize the fixed inputs, pass them, and misbehave on other inputs; this
mechanism does not attempt to prevent deliberate evasion. Use per-handle key
state and test your adapter's actual configuration and lifecycle.

The synchronous and asynchronous suites make these adapter calls when all
checks succeed.

| Algorithm | Public-key binds | Signature verifications |
|-----------|------------------|-------------------------|
| Ed25519. | 3. | 12. |
| P-256. | 2. | 11. |
| Both slots. | 5. | 23. |

Both builders attempt Ed25519 and then P-256 sequentially, including async
qualification. Each slot stops at its first failure, but the builder still
attempts the other slot. Count SDK requests and network round trips separately
from adapter calls. An adapter may perform multiple requests or
internal retries for one call. The library adds no retry or deadline.
The implementation is in
[`provider.rs`](../crates/yaml-sigil-verification/src/provider.rs) and
[`async_provider.rs`](../crates/yaml-sigil-verification/src/async_provider.rs).

A service that cannot bind the suite's public keys cannot qualify through
this mechanism. The unqualified path remains available. A finite number of
qualification calls does not bound wall-clock time, remote billing, or
resource consumption inside a provider. Reuse qualified instances and bound
application keys to avoid repeating setup work for each artifact.

### Per-operation costs

Signing-key builders validate the supplied public key locally. Both signing
paths make zero synthetic signing calls during construction. Binding a
verification key validates its public bytes and calls the factory once;
remote binding costs depend on that adapter.

| Operation | Qualified provider | Unqualified provider | Direct traits |
|-----------|--------------------|----------------------|---------------|
| Sign an admitted message successfully. | One provider sign and one local cryptographic verification of its output. | One provider sign; no local cryptographic output verification. | Depends on the implementation and selected helpers. |
| Sign an admitted P-256 digest successfully. | One local SHA-256 pass to prepare the digest, one callback, and one local cryptographic output verification. | No digest operation. | Implementation-owned. |
| Verify an admitted, structurally valid signed artifact with a bound key. | One provider verification after local checks. Qualification is not repeated. | One provider verification after the same local checks. | Depends on the implementation and selected helpers. |
| Reuse a bound key. | No repeated builder or qualification calls. | No repeated builder calls. | Implementation-owned. |

Qualified signing's extra verification hashes the final message again and
performs local public-key cryptography. Its cost grows with payload size as
well as the algorithm's fixed cryptographic work. Unqualified signing omits
that check while retaining signature-structure validation. Qualified artifact
verification does not perform a second RustCrypto verification. Both
verification paths use the provider's result.

Both provider paths share artifact parsing, payload copying, framing, and
structural checks. Scanning, copying, and message hashing grow with payload
size; public-key and signature validation operate on fixed-size inputs.
Reusing a bound key avoids binding work, but verification still validates its
canonical public bytes at use. Synchronous signing accepts a generic callback
and adds no callback allocation or dynamic dispatch. The forwarding helper
can borrow a trait object when the caller chooses one. Synchronous verification
uses dynamic dispatch and factories return boxed handles.

Async provider operations add a boxed future for each sign or verification
call. The private verification bridge also boxes each bound handle, including
qualification handles. The factory's native binding future is not boxed by
the library. These allocation and dispatch costs also apply to async
qualification. Awaiting lets other tasks progress during provider I/O; it
does not accelerate local parsing or cryptography. Remote latency may dominate
these costs, so measure the actual SDK and workload.

The default RustCrypto convenience APIs need no provider qualification or
provider-future boxing. Direct trait implementations choose their own
allocation, dispatch, checks, and helper reuse. Neither comparison establishes
that one integration is always faster.

### Failures and retries

Qualification status is separate from `VerifierOptions` and artifact
processing capabilities. Explicitly disable algorithms your operation does
not offer. A capability list does not certify an arbitrary adapter or turn a
failed slot into a qualified one.

Both qualified and unqualified verification use the provider's verdict.
Neither retries through RustCrypto or another path. `SignatureMismatch`
becomes `SignedButFailedVerification`; `ProviderFailure` becomes
`InvocationError::KeyResolutionFailure`. Synchronous `ProviderVerifier` has
a default classification that treats every `signature::Error` as mismatch.
Override it when the provider can fail operationally. Async verification
requires an explicit classified outcome. Async signing errors and errors from
the synchronous `signature` forwarding helper become
`SignError::KeyOperationFailure`. Custom callbacks return `SignError` directly;
use `KeyOperationFailure` for SDK errors. Malformed signatures and failed
qualified output checks also become `SignError::KeyOperationFailure`.

An early malformed-input rejection or an opted-in resource preflight can
avoid provider calls. That does not imply zero local parsing or validation
work. A bad output or failed qualified self-check is discovered after the
signing call has already been paid for. YAML's exact final-size check can
also reject after signing, as described below. If your application retries,
it incurs the repeated provider and local work and owns the retry policy.

## Optional artifact limits

Whole-artifact limits are opt-in operational policy. They do not establish
conformance and do not alter the separate 16,384-octet YAML signature-carrier
constraint. Ordinary provider operations and trait facades remain unbounded
by this optional policy.

Use `sign_with_provider_and_resource_limits`,
`sign_with_unqualified_provider_and_resource_limits`, or
`sign_with_p256_digest_provider_and_resource_limits` for bounded synchronous
signing. Pass `(request, limits, callback)`. The async counterparts are
`sign_with_async_provider_and_resource_limits` and
`sign_with_unqualified_async_provider_and_resource_limits`.

These functions apply the signing preflight and exact output checks.
After request-shape validation, protobuf output computes the exact encoded
length before scanning caller buffers or invoking a provider. YAML first
checks a conclusive lower bound. It checks the exact serialized output size
after signing and carrier serialization, before allocating the complete
artifact. Escaping can make that final check necessary even after a successful
preflight. Resource rejection is the outer result, a protobuf encoding error
has its own middle layer, and the existing `SignOutcome` remains inside.

For verification, call
`ArtifactResourceLimits::check_input_size` on the original encoded artifact
before a provider operation, or call `pre_verify_with_resource_limits` and
pass its admitted response to a provider `verify_from_pre_verify` operation.
Both approaches work with sync or async and either qualification choice.
These checks reject oversized artifacts before artifact-dependent parsing,
copying, or verification. If binding itself requires remote work, apply
admission before that work too. Checking extracted payload length afterward
is not an equivalent encoded-input limit.

## Checklist of checks and evidence

These tables describe the checks and tests maintained in this workspace.
“Tested” means the named repository regressions exercise a behavior with test
adapters. It is narrower than a guarantee about an integrator's provider.

### Checks applied during an operation

| Check | Qualified provider | Unqualified provider | Direct traits |
|-------|--------------------|----------------------|---------------|
| Artifact framing, parsing, options, and verifier-state mapping. | Applied by this workspace. | Applied by this workspace. | Implementation-owned; helpers are optional. |
| Canonical admissible public keys and signature structure. | Applied locally. | Applied locally. | Implementation-owned. |
| Every real signature matches the bound key and final message. | Self-verified before returning an artifact. | No local cryptographic output check. | Implementation-owned. |
| P-256 digest callback input matches the final complete payload. | SHA-256 prepared locally after final payload handling. | No digest operation. | Implementation-owned. |
| Fixed verification qualification suite. | Required per algorithm and instance. | Not run. | Not required by the traits. |
| Bound provider verdict without fallback. | Authoritative. | Authoritative. | Implementation-owned. |
| Whole-artifact resource admission. | Only when explicitly selected. | Only when explicitly selected. | Implementation-owned. |

### Repository test coverage

| Test or evidence | Qualified provider | Unqualified provider | Direct traits |
|------------------|--------------------|----------------------|---------------|
| YAML and protobuf payload bytes, signing, verification, metadata, and pre-verification reuse. | Tested with sync and async adapters. | Tested with sync and async adapters. | Default RustCrypto trait implementations run the workspace suites. Custom implementations are not tested automatically. |
| Invalid keys, malformed signatures, provider failures, and no fallback. | Tested. | Tested through shared checks and explicit bypass cases. | Custom mappings are not tested automatically. |
| Ed25519 valid, invalid, and mixed-order verification cases. | Fixed qualification suite, with sync/async status and call-count parity tests. | Suite intentionally skipped; native generated-key round trips are tested. | Applicable local fixtures exercise only the default implementations. |
| P-256 high-S/low-S acceptance. | Fixed qualification suite and regressions. | Suite intentionally skipped; operation round trips are tested. | Applicable local fixtures exercise the defaults. |
| P-256 nonce generation and entropy failure. | Integrator-owned; self-verification cannot establish nonce selection. | Integrator-owned. | Default RustCrypto signers test rejection sampling, entropy failure, and fresh nonces through sync and async operations. Custom implementations remain integrator-owned. |
| P-256 provider-input conversions. | Shared helpers test DER and point validation, scalar preservation, and strict slot boundaries. | The same helpers are available before the boundary. | Shared helpers are available; custom integrations must select and test their use. |
| Multiple live handles and cross-key rejection in both directions for Ed25519 and P-256. | Sync and async suites reject cached, retargeted, invalidated, or overly broad key bindings in regressions. | Suite intentionally skipped; the adapter owns binding correctness. | Custom binding behavior is not tested automatically. |
| Protection against an adapter deliberately evading qualification. | Not provided; the adapter is trusted code. | Not provided. | Not provided by implementing traits. |
| Runnable YAML examples with fresh keys, file/stdin/default input, and independent checking of printed output. | Native examples test qualified signing for both algorithms and qualified P-256 verification; the async example tests qualified P-256. | The dedicated `ring` example tests both operations unqualified for both algorithms without qualification; the async example tests unqualified P-256. | No runnable custom direct-trait example; default trait implementations run workspace tests. |
| Borrowed clients and keys, `Send + Sync`, pending/wake/drop behavior. | Tested with controllable async adapters. | Borrowed-key round trips are tested; shared async plumbing retains the same contracts. | External traits require `Send`; runtime behavior of custom implementations is not tested here. |
| Mutable local message callbacks, borrowed session reuse, and callbacks that consume captures. | Tested without `Send` or `Sync` requirements; bindings and requests retain compile-time `Send + Sync` checks and concurrent signing tests. | Shares the callback contract; rejection, error, structural, and resource cases are tested. | Custom callback behavior is not tested automatically. |
| Exact P-256 digest after YAML normalization, opaque protobuf input, and empty payloads. | Tested through digest callbacks and both artifact verifiers, including double-hash, wrong-message, and wrong-key rejection. | No digest operation. | Custom digest operations are not tested automatically. |
| SSH-agent Ed25519 signing with a selected public key. | `github-keys` tests exact messages, key selection, refusals, malformed replies, wrong-key signatures, timeout, and cancellation. An opt-in Unix test uses an isolated OpenSSH agent. | No agent example. | No custom agent trait implementation. |
| Bounded signing rejects early and checks the exact final output. | Tested for both algorithms and forms, sync and async. | Tested for both algorithms and forms, sync and async. | Custom operations must implement their own policy. |
| Digest resource rejection and callback counts. | Zero calls on early rejection; one call on success or late YAML rejection, at exact and exceeded limits. | No digest operation. | Implementation-owned. |
| Input-size rejection before artifact-dependent provider verification. | Existing shared admission helper is available. | Tested with an operation counter. | Custom operations must select and test admission. |
| Every applicable conformance fixture against each provider. | Not tested. | Not tested. | Default implementations run the workspace fixture suites; arbitrary associated key types need test-driver adaptation. |
| RNG quality, nonce-generation policy, constant-time behavior, side channels, key storage, and service authorization. | Not established by qualification or output self-verification. | Not established. | Not established by implementing traits. |
| Real SDK scheduling, network cancellation, timeouts, rate limits, and all deployment platforms. | Integrator-owned; the agent example's focused tests do not cover every agent or platform. | Not tested. | Integrator-owned. |
| FIPS validation or other certification. | Not established. | Not established. | Not established. |

Evidence lives in the signing unit tests, including
[`callback_tests.rs`](../crates/yaml-sigil-signing/src/callback_tests.rs),
[`provider_paths.rs`](../crates/yaml-sigil-verification/tests/provider_paths.rs),
[`async_provider_tests.rs`](../crates/yaml-sigil-verification/src/async_provider_tests.rs),
compiling API rustdoc, and the runnable examples, including
[`ring_unqualified_provider.rs`](../examples/ring_unqualified_provider.rs).
These generated-key round trips do not establish a provider's acceptance
behavior across the full input space. The
[focused async fixture test](../crates/yaml-sigil-conformance/tests/provider_async.rs)
also covers P-256 high-S/low-S and malformed signatures through both provider
facades. The
[conformance record](./conformance-validation.md) names fixture coverage and
known implementation behavior. Keep qualification evidence distinct from
those complete artifact suites.

### Establishing complete conformance

Our qualification offers narrower evidence than complete conformance.
For any of the three paths, establish the following for the complete
implementation and the exact provider configuration you intend to claim.

- [ ] Identify every applicable normative requirement and advertised profile
  in the selected YamlSigil specification, including requirements not covered
  by available fixtures.
- [ ] Run the applicable artifact, algorithm, malformed-input, key-resolution,
  metadata, and runtime fixtures through the actual integration. Adapt the
  workspace test drivers where their RustCrypto associated-key bounds do not fit.
- [ ] Test correct signature generation as well as acceptance, including
  algorithm-specific randomness and nonce requirements. A signature that
  self-verifies does not prove how it was generated.
- [ ] Exercise each offered sync and async operation, supported form,
  configuration, and claimed profile. Verify capability advertisements and
  error classification against actual behavior.
- [ ] Resolve normative failures before claiming complete conformance.
  Document remaining deliberate divergences and the resulting narrower claim.

Separately validate deployment security and operational requirements. Neither
the fixture suite nor provider qualification certifies an HSM, KMS, library
build, or deployment as FIPS validated.

## Existing RustCrypto types

The `0.6` convenience APIs expose `ed25519-dalek` 3.x and `p256` 0.14
key types. Synchronous verification and optional signing adapters implement
`signature` 3.x traits; signing callbacks can call SDK operations directly.
Update your direct dependencies together; Cargo treats types and traits from
incompatible versions as distinct. See Cargo's
[version incompatibility guidance](https://doc.rust-lang.org/cargo/reference/resolver.html#version-incompatibility-hazards).

For P-256, replace `to_encoded_point` with `to_sec1_point` and `SigningKey::random`
with the `p256::elliptic_curve::Generate` trait. The
[`async-provider` example](../examples/async_provider.rs) uses
`try_generate_from_rng` with `rand` 0.10's fallible `SysRng`.
Public-key bytes, signature encodings, and the external `yaml-sigil-traits`
contracts retain their existing formats and behavior.

Default P-256 signing samples a fresh nonce from the system CSPRNG for each
signature. On browser and Node.js WebAssembly targets, it uses Web Crypto.
Entropy failure returns `SignError::KeyOperationFailure` without an artifact.
`DefaultAsyncSigner` performs that same operation on the polling thread.
Provider adapters retain responsibility for their own nonce generation;
qualification and output self-verification do not establish that behavior.

You can own an application wrapper and implement `TryFrom` into these existing
public types when conversion validates public bytes, or `From` when it is
infallible. Compiling examples accompany
[`resolve_ed25519_verifying_key`](../crates/yaml-sigil-verification/src/lib.rs)
and `resolve_p256_verifying_key`. This does not require exporting a provider's
private key. Opaque private-key operations use the provider adapters, and
direct traits permit entirely different associated key types.

We can introduce a library-owned wrapper if a concrete compatibility or
consumer requirement warrants it. Provider support does not itself require
that migration, and it makes no promise that today's RustCrypto types remain
the boundary indefinitely.
