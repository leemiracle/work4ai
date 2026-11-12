# Contributing to yaml-sigil-rs

`yaml-sigil-rs` is developed agent-first. Use agents to explore the workspace,
run diagnostics, and draft changes, then review the result as the responsible
author before submitting it.

Repository writers use [`MAINTAINERS.md`](MAINTAINERS.md) for exact-head test
authorization, protected-policy staging, merges, exceptions, and reverts.

## Understand your contribution

You must understand the contribution you submit. Explain what changed, why it
changed, and how it interacts with the rest of the implementation. Review
AI-assisted code, tests, and documentation until you can explain them without
consulting the agent.

## AI Usage

Use agents to assist your work. You are responsible for the contribution.

- **Do** use agents to read the codebase, run checks, generate drafts, and
  iterate on implementations.
- **Do** use the skills in `.agents/skills/`; they capture repository-specific
  workflows for spec updates and implementation review.
- **Do** question the agent until you understand the behavior, edge cases, and
  test impact of your change.
- **Do not** submit changes you cannot explain in your own words.
- **Do not** use agents as a substitute for reading the relevant code, specs,
  and maintainer guidance.

## Express release-version intent

Use an accurate Conventional Commit type and breaking-change marker when the
change itself establishes its release impact. Do not edit workspace or crate
versions on an ordinary feature or fix branch. State release impact in the pull
request when the commits do not make it clear. Maintainers select the exact
stable or prerelease version later and prepare the dedicated
`release-plz-manual-<version>` pull request described in `RELEASING.md`.

Do not edit the crate changelogs in an ordinary contribution. The canonical
maintainer release procedure runs pinned `release-plz` to generate them from
the integrated Conventional Commit history in the dedicated release pull
request.

All published crates share `[workspace.package].version`. Never change a
member version independently. A version change belongs only in the canonical
single-commit release pull request and must pass both checks:

```shell
cargo xtask sync-workspace-versions --check
cargo xtask release check --version MAJOR.MINOR.PATCH[-PRERELEASE]
```

Official RC and stable publication rejects an unsynchronized or dirty source
tree. Pull requests do not publish preview versions.

## Choose the pull-request base

Target `main` for changes compatible with the current public API. A maintainer
may advertise one protected `dev/MAJOR.MINOR.PATCH` coordination branch for a
breaking API or behavior change, work that depends on that unpromoted change,
or its migration documentation and tests. Do not invent a coordination branch.
When compatibility is uncertain, ask a maintainer before opening the pull
request.

Coordination branches are optional, temporary contribution bases. After
promotion and successful validation on `main`, target `main` for subsequent
work unless maintainers advertise a separately activated support line.
Retained recovery refs are closed to contribution intake and routine
synchronization. Follow the
[retirement procedure](MAINTAINERS.md#retire-abandon-or-restart-a-line).

Apply a fix needed by both lines to `main` first; the release coordinator moves
it forward. Protected CI, admission, and release-policy changes always target
`main`. Prepare releases from `main` or an activated support line, never
from a coordination ref.

Squash is the default integration method on either base. A trusted writer may
preserve an intentional commit series only through the separately authorized
procedure in [`MAINTAINERS.md`](MAINTAINERS.md).

## Preserve serialization backend boundaries

Serde is the intentional public data-model boundary for
`yaml_sigil_core::SignatureDocument`. Keep every concrete serialization
library, including the current YAML backend, private unless a separate API
decision deliberately exposes it. Do not add backend types through public
parameters, return values, trait bounds, associated types, re-exports, feature
flags, or error variants.

Preserve these boundaries when changing a serialization dependency:

- Preserve the exact Serde field names, required fields, optional `keyid`
  behavior, and unknown-field rejection documented on `SignatureDocument`.
  Treat changes to that representation as public API changes under SemVer.
- Keep `parse_signature_document` authoritative for untrusted YAML because it
  applies YamlSigil's byte limit and parser policies.
- Keep `serialize_signature_document` authoritative for canonical YAML output.
- Treat `CoreError::SignatureYaml` text as an unstable human diagnostic that
  callers must not parse.
- Test Serde interoperability by comparing `SignatureDocument` values, not
  serialized YAML bytes or presentation details.
- Describe an exact-pinned downstream dependency test as characterization of
  that selected release, not a permanent compatibility guarantee.

Apply the same rules to any serialization library adopted later. A dependency
visible in Cargo metadata or named as the current implementation does not make
it a required consumer integration.

## Pull-request CI

The repository uses `copy-pr-bot` for explicit contributor admission. A
repository writer reviews the exact latest pull-request head and comments:

```text
/ok to test <full-40-character-head-sha>
```

The bot copies only that authorized head to `pull-request/<number>`. Draft and
ready pull requests do not synchronize automatically. Every new head requires
a new review and exact-SHA authorization; a stale authorization never runs the
new head.

The exact-head command is the sole per-head human admission step. After the
authoritative candidate lanes finish, the protected reporter repeats every
live binding and the App writes `Required CI` for `main`, or
`Required CI [refs/heads/dev/MAJOR.MINOR.PATCH]` for the exact active
coordination base. A result for one base never satisfies another. Release
finalization has a separate reviewer gate and cannot authorize a candidate or
a different head.
The authoritative aggregate job records its pre-execution protected-policy SHA
and exact base ref/SHA; movement of either object invalidates the run.

The copied `.github/workflows/ci.yml`, `ci-trusted.yml`, and
`ci-candidate.yml` must exactly match protected current `main`. Coordinate a
proposed workflow change with a maintainer before requesting candidate testing.
Maintainers can explicitly stage a reviewed policy change through the separate
procedure in `MAINTAINERS.md`; ordinary copied-ref admission stays unchanged.

Candidate setup completes before source materialization. The checkout uses
anonymous Git transport, rejects requested Git filters, disables Git LFS, and
ignores candidate-selected submodule configuration. Candidate execution
receives no repository credential, secret, OIDC permission, protected
environment, trusted cache-save path, or retained artifact. No privileged
post-step consumes candidate-writable state.

Every human-authored pull-request commit must form a linear history from the
exact current pull-request base and contain the exact DCO identity required for
that author. Cryptographic signatures are optional for ordinary contributor
commits. A writer's command authorizes testing only and does not authorize
integration.

Before final authorization, fetch the current upstream pull-request base,
require the contributor branch to be linearly rebased onto that exact ref, and
push any rewritten branch back to the same fork with an exact lease. Confirm
every rewritten commit is DCO-compliant, then request testing for the new exact
SHA.

The authoritative candidate result is the NVIDIA-runner aggregate whose name
starts with `Candidate CI / Candidate CI (Linux)` and records the exact
protected-policy and base objects. A separate protected, checkout-free
reporter binds the workflow ID, run and attempt, repository, open pull request,
copied ref, current head,
authoritative job conclusion, and zero-artifact result before the
repository-scoped App creates the base-specific required verdict described
above. Stable macOS and Windows jobs are advisory and cannot influence that
verdict. The independent Rust `1.95.0` Linux lane protects the documented
minimum version.

#### Signing Off Your Work

* We require that all contributors "sign-off" on their commits. This certifies that the contribution is your original work, or you have rights to submit it under the same license, or a compatible license.

  * Any contribution which contains commits that are not Signed-Off will not be accepted.

* To sign off on a commit you simply use the `--signoff` (or `-s`) option when committing your changes:
  ```bash
  $ git commit -s -m "Add cool feature."
  ```
  This will append the following to your commit message:
  ```
  Signed-off-by: Your Name <your@email.com>
  ```

* Full text of the DCO (https://developercertificate.org/):

  ```
    Developer Certificate of Origin
    Version 1.1

    Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

    Everyone is permitted to copy and distribute verbatim copies of this
    license document, but changing it is not allowed.


    Developer's Certificate of Origin 1.1

    By making a contribution to this project, I certify that:

    (a) The contribution was created in whole or in part by me and I
        have the right to submit it under the open source license
        indicated in the file; or

    (b) The contribution is based upon previous work that, to the best
        of my knowledge, is covered under an appropriate open source
        license and I have the right under that license to submit that
        work with modifications, whether created in whole or in part
        by me, under the same open source license (unless I am
        permitted to submit under a different license), as indicated
        in the file; or

    (c) The contribution was provided directly to me by some other
        person who certified (a), (b) or (c) and I have not modified
        it.

    (d) I understand and agree that this project and the contribution
        are public and that a record of the contribution (including all
        personal information I submit with it, including my sign-off) is
        maintained indefinitely and may be redistributed consistent with
        this project or the open source license(s) involved.
  ```

## Compatible fixes for an older line

Target an advertised `support/M.N` only after maintainers have opened that
line. Keep the change compatible with that major/minor line and follow the
same DCO and review process. Main supplies CI policy and the required check is
specific to the selected support base. An older line receives fixes when
practical; no fixed support duration or response time is promised.
