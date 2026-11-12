# Releasing

Maintainer reference for publishing the `@nvidia` icon packages to npm.
Contributors do not need this; see [CONTRIBUTING.md](./CONTRIBUTING.md).

Releases run from [`.github/workflows/release.yml`](./.github/workflows/release.yml),
triggered by pushing a `v*.*.*` tag and gated on the `npm-publish` environment.

## How authentication works

The workflow uses npm Trusted Publishing (OIDC). There is no `NPM_TOKEN` in
this repository or in anyone's custody. GitHub mints a short-lived token
describing the workflow itself, npm validates it against a trusted publisher
registered on each package, and issues a credential scoped to that single run.

The same token is what Sigstore's Fulcio CA signs the provenance attestation
against. Fulcio only issues certificates to OIDC issuers it recognises, which
is why provenance is available on GitHub Actions and is not available from a
self-hosted CI runner.

## One-time setup

None of this lives in the repository, so it is easy to miss.

1. **Create the `npm-publish` environment** (Settings, then Environments) with
   required reviewers. This is the human approval gate. It also narrows the
   OIDC subject claim to `repo:NVIDIA/icons:environment:npm-publish`, so a
   workflow running on any other ref cannot mint a publish credential.

2. **Register a trusted publisher on each of the four packages** at
   npmjs.com, under the package's Settings:

   | Field | Value |
   |---|---|
   | Repository | `NVIDIA/icons` |
   | Workflow | `release.yml` |
   | Environment | `npm-publish` |

   All three must match the workflow exactly or npm refuses the exchange.

3. **Bootstrap** — only needed for a package name that has never been
   published. A trusted publisher cannot be registered for a name that does
   not exist yet; npm's CLI reference states the package must already exist.
   `release.yml` therefore cannot perform a package's first publish.

   The four current packages are past this. They were bootstrapped on
   2026-09-16 and all four now publish under pure OIDC, so nothing below is
   required to cut a release today. It is kept because adding a fifth package
   name means doing it again.

   Provenance and Trusted Publishing are separate npm features: `--provenance`
   has worked with a plain token plus `id-token: write` since npm 9.5.0, long
   before Trusted Publishing existed. So the fix for "a laptop publish can't
   be attested" is not a throwaway hand-seeded version: it's a **CI**
   publish authenticated with a short-lived token instead of OIDC. Bootstrap
   with a real release candidate, not a version nobody will ever install:

   | Step | Action |
   |---|---|
   | 1 | Create the `npm-publish` environment with required reviewers (see above), before doing anything else on npm |
   | 2 | Bump the new package's manifest to `X.Y.Z-rc.1`; land on `main` |
   | 3 | Mint a short-lived `@nvidia`-scope token **that bypasses 2FA** (see below); store it as an **environment secret on `npm-publish` only** (`NPM_BOOTSTRAP_TOKEN`), never a repo secret |
   | 4 | Restore the one-shot publish workflow (`git show v1.0.0:.github/workflows/bootstrap-publish.yml`), dispatch it with `dry_run: true`, inspect the output, then dispatch again with `dry_run: false` |
   | 5 | Approve the `npm-publish` environment when prompted; it publishes `X.Y.Z-rc.1`, public, attested, on the `next` dist-tag |
   | 6 | Register the trusted publisher on the package (Repository/Workflow/Environment as above); now possible, since the name exists |
   | 7 | Delete the token at npmjs.com, delete the `NPM_BOOTSTRAP_TOKEN` environment secret, and remove the workflow again |
   | 8 | Promote to `X.Y.Z`, tag `vX.Y.Z`, and let `release.yml` publish GA under pure OIDC |

   Step 4 restores a workflow rather than pointing at one because it is not
   kept in the tree between bootstraps. It is the only workflow that ever
   reads an npm token, and a token-authenticated publish path is worth its
   risk only while it is actually being used.

   The token type in step 3 is not a free choice. A granular access token is
   the obvious pick and it does not work: with 2FA required on writes for the
   publishing account, npm rejects the publish with `EOTP`, and there is no
   prompt to answer on a CI runner. It fails late, too: after the tarball is
   packed and after provenance has already been countersigned into Sigstore's
   public transparency log, which leaves a published attestation for a version
   that does not exist on the registry. The token has to be one npm accepts
   without a second factor.

   npm is actively restricting that kind of token. A publish using one already
   prints a deprecation notice pointing at
   <https://gh.io/npm-gat-bypass2fa-deprecation>. Check whether the mechanism
   still exists before planning a bootstrap around it; if it is gone, the
   remaining options are a first publish from a maintainer's machine with an
   interactive OTP (unattested, then immediately superseded by an attested
   release candidate from CI) or whatever first-publish path npm has replaced
   it with by then.

   That workflow refuses to publish anything without a prerelease identifier
   in the version, so GA can only ever go out through `release.yml` under
   OIDC. That's the entire point of this sequence: the version everyone
   actually installs is published with **zero credentials in existence**, and
   the pipeline (environment gate, dist-tag handling, provenance) has already
   been exercised once on the real scope before GA depends on it.

   No version is ever unpublished, no npm org plan requirement applies (this
   never uses `--access restricted`), and there is no 72-hour clock.

## Cutting a release

1. Land the version bump and changelog entries on `main`.
2. Tag the merged commit `vX.Y.Z` and push the tag.
3. The `tag-guard` job refuses any tag that is not an ancestor of `main`, then
   the `verify` job re-runs CI against the tagged tree. `verify` is a call into
   [`ci.yml`](./.github/workflows/ci.yml) rather than its own copy of the
   commands, so the release gate is the pull-request gate by construction and
   cannot fall behind it. `dco-check` and `commitlint-check` skip, being
   pull-request checks.
4. Approve the `npm-publish` environment when prompted.
5. The `publish` job publishes every package whose version matches the tag,
   in dependency order, and skips any version already on the registry.
6. The `github-release` job then creates the GitHub Release for the tag.

## Release notes

The GitHub Release body is assembled by
[`scripts/release-notes.mjs`](./scripts/release-notes.mjs) from two sources:
the `## [X.Y.Z]` section of the root [CHANGELOG.md](./CHANGELOG.md), and a
table of the packages that tag actually published, each linked to its exact
version on npm.

So the changelog entry has to land *before* the tag. Cut a tag without one and
the release still publishes, with a body that says the changelog entry is
missing: this runs after `npm publish` has already succeeded, and failing the
job would turn a finished release red without un-publishing anything.

Preview the body for a version before tagging it:

```sh
node ./scripts/release-notes.mjs 1.2.0 gui-icons react-gui-icons
```

A version with a prerelease identifier is marked as a GitHub prerelease, so it
does not take the repository's "Latest release" banner, for the same reason it
publishes to the `next` dist-tag. Re-running a release updates the existing
release rather than failing.

No build artifacts are attached. The tarballs are on the registry with
provenance; a copy attached here would be an unattested second channel that
can drift from the attested one.

Packages version independently, so a tag publishes only the packages that sit
at that version. A tag matching no package fails the run rather than
succeeding silently having published nothing.

Dist-tag is derived from the version, not fixed: anything with a prerelease
identifier (`-rc.1`, `-beta.2`, ...) publishes to `next`; everything else
publishes to `latest`. This matters because packages can be mid-prerelease
independently of each other; a `latest` install must never resolve to an
unfinished release.
