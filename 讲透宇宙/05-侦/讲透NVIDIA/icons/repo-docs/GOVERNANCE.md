# Governance

This document describes how the NVIDIA Icons project is governed.

## Ownership

NVIDIA Icons is an open-source project owned and maintained by NVIDIA
Corporation. NVIDIA retains final authority over the project's direction,
branding, icon design, and releases, informed by community bug reports, icon
requests, and code contributions filed via GitHub. The icon artwork and code
are licensed under the terms in [LICENSE](./LICENSE). That license covers
copyrighted content only; it does **not** extend to NVIDIA's trademarks,
which remain NVIDIA property; see [NOTICE](./NOTICE) for the trademark
notice.

## Maintainers

The project is run by a group of maintainers listed in
[MAINTAINERS.md](./MAINTAINERS.md). Maintainers are responsible for:

- Reviewing and merging contributions.
- Triaging issues and icon requests.
- Cutting releases and publishing packages.
- Upholding the [Code of Conduct](./CODE_OF_CONDUCT.md).

## Decision-making

- **Day-to-day decisions** (bug fixes, documentation, dependency updates) are
  made by maintainers through the normal pull-request review process. At least
  one maintainer approval is required to merge.
- **Icon design decisions** (new icons, visual changes, icon removals) are **not**
  decided in this repository. They are owned by NVIDIA design/brand teams and
  reviewed internally. Community icon requests are collected via GitHub Issues
  and forwarded to those teams. Every icon request issue gets a real
  disposition, not silence: once reviewed, maintainers label it `accepted`,
  `declined`, or `duplicate`/`already covered` and close it with a one-line
  reason. There's no fixed turnaround time (see [SUPPORT.md](./SUPPORT.md)),
  but every request that's triaged is answered, not left open indefinitely.
- **Significant or contested decisions** (breaking API changes, license or
  governance changes, scope changes) are decided by the lead maintainer in
  consultation with NVIDIA stakeholders, and escalated per
  [MAINTAINERS.md](./MAINTAINERS.md) when needed.

## Contribution review

All changes land through GitHub Pull Requests that pass required CI checks and
the DCO sign-off requirement described in [CONTRIBUTING.md](./CONTRIBUTING.md).
Generated content under `packages/*/assets/`, `packages/*/src/generated/`,
`packages/*/src/icons/`, and `packages/*/src/iconTypes.ts` is produced by
NVIDIA's internal monorepo sync and is not modified through direct
contributions. [CONTRIBUTING.md](./CONTRIBUTING.md#sync-generated-content)
carries the per-package breakdown.

## Release authority

Releases are authorized and published by maintainers with publish rights.
Versioning follows semver as described in the [README](./README.md) and
[CHANGELOG.md](./CHANGELOG.md).

## Changes to this document

Changes to project governance are proposed via pull request and approved by the
lead maintainer on behalf of NVIDIA.
