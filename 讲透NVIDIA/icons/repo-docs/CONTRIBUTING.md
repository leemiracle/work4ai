# Contributing to NVIDIA Icons

Thank you for your interest in contributing to NVIDIA Icons.

Worth knowing upfront: this repository is a one-way sync from NVIDIA's
internal design system, not a place where the icon set itself is designed in
the open. Code, docs, and bug-fix contributions are welcome and reviewed like
any open-source project; icon *design*, meaning what gets added, changed, or removed,
is decided internally, with community requests taken as input (see below).

Also worth knowing: parts of this project's code, docs, and governance files
were drafted with AI coding-assistant help and reviewed by a human maintainer
before merging, the same as any other contribution. Ongoing work of that kind
carries a `Co-Authored-By` trailer; this repository opens with a single
squashed commit, so trailers only appear from that point on.

## What contributions are accepted

- **Bug reports:** incorrect TypeScript types, broken package exports, build
  failures, install errors, accessibility issues in React components.
- **Documentation improvements:** typos, clarity improvements, missing usage
  examples.
- **Code fixes:** corrections to generated component logic (not generated
  content itself, which comes from the internal sync).

**Icon design contributions are not accepted as direct pull requests.**
If you need a new icon or find an existing icon is wrong, open an issue using the
Icon Request template on our
[new-issue page](https://github.com/NVIDIA/icons/issues/new/choose). NVIDIA
design and brand owners review all icon requests internally.

## Developer Certificate of Origin (DCO)

This project uses the [Developer Certificate of Origin (DCO)](https://developercertificate.org/).
All commits must include a `Signed-off-by` trailer:

```
Signed-off-by: Your Name <your.email@example.com>
```

Add it automatically with:

```sh
git commit --signoff
```

The `dco-check` job in this repo's GitHub Actions CI (visible on your PR, in
[`.github/workflows/ci.yml`](./.github/workflows/ci.yml)) will fail on
any commit that is missing the trailer.

### Full text of the DCO

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

## Prerequisites

- **Node.js 22.12 or newer.** That floor is the build toolchain's, not the
  packages': Vite requires it. What we publish still runs on any Node 22, so
  the `engines.node` in each `packages/*/package.json` stays `>=22`; only the
  root one is `>=22.12`. CI runs the full build and test suite on Node 22 and
  24 (see the `node-matrix` job). `.nvmrc` pins 24 for local development and
  for the single-version CI jobs; `nvm use` picks it up.
- **npm 10 or newer** (bundled with Node 22+). No other package manager is
  supported; this repo uses npm workspaces and ships a `package-lock.json`.
  Release tasks (`npm sbom`, `npm publish --provenance`) need npm >= 11.5;
  see `packageManager` in the root `package.json` for the exact version CI
  uses for those.

## How to contribute

1. Fork the repository.
2. Create a branch from `main`: `git checkout -b fix/my-fix`.
3. Make your changes. Add or update tests if applicable.
4. Ensure CI passes locally:
   ```sh
   npm ci
   npm run build
   npm run lint
   npm run typecheck
   npm run test
   npm run test:react-compat
   npm run verify:packaging
   ```
5. Commit with `--signoff`, using a [Conventional Commits](https://www.conventionalcommits.org/)
   message: `git commit --signoff -m "fix: describe the fix"`. `npm ci` installs
   a `commit-msg` git hook (via [husky](https://typicode.github.io/husky/)) that
   checks this locally; the `commitlint-check` CI job checks it again on the PR
   so the rule holds even if the hook was skipped or never installed.
6. Push your branch and open a pull request against `main`.

## Sync-generated content

These paths are populated by automated sync from NVIDIA's internal monorepo:

| Path | Packages |
|---|---|
| `assets/` | `gui-icons`, `micro-gui-icons` |
| `src/iconTypes.ts` | `gui-icons`, `micro-gui-icons` |
| `src/generated/` | `react-gui-icons`, `react-micro-gui-icons` |
| `src/icons/` | `react-gui-icons`, `react-micro-gui-icons` |

Do not edit these files manually; changes will be overwritten on the next
sync. `src/iconTypes.ts` is the one to watch: unlike the others it is a
single file rather than a directory, and it sits in `src/` beside
hand-maintained code like `index.ts`. Its own `DO NOT EDIT MANUALLY` header
is the only thing distinguishing it in a directory listing.

A fix that has to survive the sync belongs upstream in the generator, not
here. If you send a pull request against one of these paths, expect a
maintainer to ask for it to be filed internally instead.

## Code style

This project uses [Biome](https://biomejs.dev/) for linting and formatting.
Run `npm run lint:fix` to auto-format before committing.
