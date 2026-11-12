# Native credential builds and maintenance

The plugin loads an admitted native credential module; startup never compiles Rust, downloads a replacement binding, or installs dependencies. Native source builds are an explicit maintainer operation. Normal JavaScript package builds verify the admitted bytes and their receipts before assembling the bundle. A native module does not provide an Autodesk account, Fusion entitlement, or permission to access someone else's vault.

The original `@napi-rs/keyring` 1.3.0 platform binaries are withheld. The pinned upstream tree omitted and explicitly ignored `Cargo.lock`; its surviving provenance does not enumerate the resolved Rust dependencies. A wrapper MIT license and embedded compiler strings cannot reconstruct that missing build graph. The npm native dependency is therefore absent from this package.

Our source starts at [keyring-node commit e46be75c3ba8d5fde6b88a17c6153b87ffe4b946](https://github.com/Brooooooklyn/keyring-node/tree/e46be75c3ba8d5fde6b88a17c6153b87ffe4b946). [source-manifest.json](../native/source-manifest.json) identifies every packaged build input, the preserved community patch, and their combined source identity. [Cargo.lock](../native/source/Cargo.lock) is a **new exact resolution**, not the upstream publisher's missing lock. The patch propagates vault failures instead of treating them as missing entries, corrects nullable API annotations, and removes the macOS library's private build path. Rust and Cargo are pinned to `1.98.0`; individual receipts additionally record compiler hashes, the host, SDK, linker/compiler description, Node version, and output bytes. Different SDKs or hosts may produce different binaries.

[native-dependencies.json](native-dependencies.json) inventories the complete conservative lock graph, verified registry checksums, license provenance, and recorded target features. [UPSTREAM_NOTICES.txt](../native/UPSTREAM_NOTICES.txt) supplies the collected license texts, including NAPI notices recovered from exact published source commits, D-Bus's native-library terms, Rust standard-library notices, and compiler-builtins/libm/LLVM runtime attribution. Compiler-only copyright inputs are inventoried separately because rustc and LLVM build tools are not shipped. Optional, build, and other-platform dependencies remain in the inventory; inclusion does not assert linkage into every binary. Changing the source, lock, toolchain, or runtime dependencies requires corresponding inventory and notice review.

The build helper supports these **credential-broker** host targets, not Fusion desktop availability on every operating system:

| Host | Rust target |
| --- | --- |
| macOS arm64 | `aarch64-apple-darwin` |
| macOS x64 | `x86_64-apple-darwin` |
| Linux arm64, glibc | `aarch64-unknown-linux-gnu` |
| Linux x64, glibc | `x86_64-unknown-linux-gnu` |
| Windows arm64, MSVC | `aarch64-pc-windows-msvc` |
| Windows x64, MSVC | `x86_64-pc-windows-msvc` |

The single Autodesk Fusion E2E job builds and loads the macOS runner's host target. To check another target, run the same helper on its matching host using the table above. Local or hosted macOS evidence does not establish Windows, Linux, other SDK, or other workstation behavior. Consult the exact candidate and qualification records before making a platform claim.

Use this maintainer sequence:

1. **Review the inputs.** Select an exact repository commit, inspect the patch and dependency changes, and verify the committed source manifest and license inventory. Preserve the declared file bytes and line endings. Do not regenerate the lock or edit expected hashes simply to make a failing check pass.

2. **Prepare an appropriate host.** Install the pinned Rust toolchain and host target separately. Use the matching Node architecture, macOS developer tools, a glibc Linux build environment, or Windows Developer PowerShell with the required MSVC toolset and Windows SDK. The helper refuses a different target from its running Node host; it is not a cross-compilation interface.

3. **Produce an isolated candidate.** From the plugin directory, an Apple Silicon example is:

   ```sh
   node scripts/build-native.mjs --output /absolute/empty/fusion-native-candidate --target aarch64-apple-darwin
   ```

   Select an empty output directory outside the plugin tree whose parent already exists. The packaged [build helper](../scripts/build-native.mjs) verifies the exact source, uses a private Cargo cache and `cargo +1.98.0 build --locked --release`, rejects inherited build overrides and ancestor Cargo configuration, and preserves managed network routing. Cargo may retrieve the locked public crate sources during this explicit build. The helper checks diagnostics, remaps private paths, loads the module without constructing credential entries, and produces a `.node` candidate plus its `.build.json` receipt. It does not admit or publish them.

4. **Review CI provenance separately.** The repository-only workflow is `.github/workflows/autodesk-fusion.yml`; it is not an installed-plugin command. Its one `Autodesk Fusion E2E` job runs the full root suite on Node 22.19, 24 and 26, the runtime audit, and a host native build with candidate/receipt upload. All checks are sequential steps in that job; there is no separate native workflow or platform matrix. The native build does not access the vault or publish the candidate. Obtain artifacts from the exact reviewed repository, workflow, run ID, run attempt, and head commit. For pull requests, distinguish the checked-out merge commit from the PR head. Compare the receipt's source, helper, compiler, target, and output hashes with independently obtained evidence. Never accept an artifact merely because its filename or JSON claims the right identity.

5. **Qualify before release admission.** Review the actual platform module load, ABI/export behavior, linked libraries, deployment baseline, warnings, and private-path scan. Exercise the real OS credential service on the intended platform in a private qualification copy. Stage only the candidate and matching receipt there, build that copy to create its integrity receipt, then explicitly set `FUSION_TEST_OS_VAULT=1` when running `npm run test:vault`. The test uses unique synthetic entries in this plugin's namespace and verifies removal. Its default skip and protocol doubles are not OS qualification. A denied or unavailable vault requires a recorded limitation and normal operator remediation; do not bypass access controls. Keep the real-vault evidence separate from the helper's credential-free load receipt.

6. **Admit reviewed bytes.** After those checks, place the approved module under `native/` and its exact matching receipt under `native/receipts/`. [verify-native.mjs](../scripts/verify-native.mjs) checks the strict file tree, source/patch/lock identities, target format, module hashes, receipt consistency, and notice coverage during `npm run build`. Unexpected, missing, or inconsistent assets stop the build. Commit the reviewed inputs and evidence through the normal PR process, then rerun package tests. These consistency checks do not authenticate the builder or independently repeat OS-vault qualification.

Receipts and SHA-256 hashes are **not authenticated signatures**, notarization, reproducibility proofs, or production approval. Protect the repository and release channel, and apply enterprise signing and deployment controls separately. A model-supplied receipt cannot authorize native code installation.

Credential cleanup has its own failure semantics. Before writing secret chunks, `NativeTokenStore` persists private, nonsecret generation metadata. Replacement publication preserves a usable new grant even if removal of retired generations fails; retained receipts make that cleanup retryable. `cleanupStatus()` reports conservative counts without returning credentials. Persistent callers must retain the existing grant-lease serialization contract.

Logout strictly removes and independently checks known chunks before removing the current manifest. Denied or unverifiable deletion reports `CREDENTIAL_CLEANUP_INCOMPLETE`, possibly after partial removal; remaining manifests and receipts retain retry information. Retry after restoring normal vault access. Do not erase these records or refresh-intent fences to manufacture a successful logout.

Local deletion and Autodesk revocation are distinct. Successful local removal can coexist with uncertain provider revocation, which the OAuth result reports separately; failed local cleanup must never report `localCredentialsRemoved: true`. Neither operation cancels an Automation job nor revokes Codex's separately owned Data MCP authorization. Preserve unresolved cleanup and cloud-operation evidence until independently reconciled.
