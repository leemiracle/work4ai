# Review and publish

This repository distributes public Codex plugins. A release is ready only when
the marketplace entry, installable package, cold-start instructions, licenses,
and evidence all agree.

## Review checklist

- Confirm `.agents/plugins/marketplace.json` names only plugins intended for
  public distribution and points to existing `./plugins/<name>` directories.
- Confirm every manifest has accurate publisher, repository, website, version,
  capability, authentication, and license metadata.
- Check that plugin docs tell a cold-started Codex task what to do first, what
  inputs are safe, what it must never do, and how to stop when prerequisites are
  missing.
- Inspect code, skills, hooks, and setup commands for execution behavior and
  permissions, including dependency installation and update behavior.
- Identify files read or written, off-machine destinations, and the data sent
  to each destination. Check these against the declared capabilities and docs.
- Review dependency provenance, credential access, secret storage and redaction,
  and safe failure behavior. Review changes to these boundaries explicitly.
- Scan manifests, docs, fixtures, source archives, and media for secrets,
  personal paths, customer identifiers, private transcripts, and unpublished
  customer data.
- Review each plugin's license and third-party notices before redistribution.
- Confirm GitHub private vulnerability reporting is enabled before sharing the
  marketplace publicly.
- Run `npm run validate:marketplace`, `npm run test:marketplace`,
  `npm run validate`, and the deeper tests for every changed plugin.
- For Grafana release changes, review the full demo media and source receipts;
  skipped checks are not passes.

## Grafana verification

From a fresh checkout:

```sh
npm run validate
npm run verify:grafana:source
npm run test:grafana
```

The [Grafana test guide](../tests/grafana-observability/README.md) lists the
real-provider matrix, authentication, installed-client, source-rebuild, and
native Keychain commands with their platform requirements. The
[source/build guide](grafana-observability-source.md) explains the pinned source
archive and exact-byte rebuild process.

Before publishing a Grafana release, also run the applicable end-to-end gates:

```sh
npm run test:grafana:matrix
npm run test:grafana:auth
npm run test:grafana:installed
# macOS arm64 only:
npm run test:grafana:keychain
npm run test:grafana:handoff
```

If a required platform is unavailable, record the skipped gate and an explicit
reviewer-approved exception instead of treating it as a pass.

The recording in [demo media](media/README.md) illustrates a broader local
workflow and is not installed-plugin test evidence. Review it in full before
redistribution.

## Autodesk Fusion verification

Use Node.js 22.19 or newer and Python 3.12 or newer for development verification:

```sh
npm --prefix plugins/autodesk-fusion ci --ignore-scripts
npm run test:autodesk-fusion
```

The root master checks the committed distribution before rebuilding, runs the
repository's cold-package unit/integration/security tests, then runs the deeper
plugin and Python API contracts and validates the regenerated package. The
catalog-discovered `npm run test:marketplace` includes this same master. See the
[Fusion test guide](../tests/autodesk-fusion/README.md) for coverage and process
cleanup boundaries. The single `Autodesk Fusion E2E` job runs this master on
Node 22.19, 24 and 26 sequentially, and includes cold-package verification, the
runtime audit and a pinned host native source build with a candidate receipt.
Keep those checks together as required by [AGENTS.md](../AGENTS.md).

An implementation-preview PR must preserve the explicit limitations in the
[Fusion status report](autodesk-fusion-implementation-status.md). Synthetic
geometry, protocol doubles and local package tests do not qualify a licensed
Fusion build, Autodesk tenant, machine/post/tool combination or installed-Codex
workflow. Hosted CI, supported-OS/native builds, real credential service checks,
licensed acceptance scenarios and independent engineering/security review need
their own evidence. Do not enable real-provider managed writes or the disabled
Automation recipe just to make a setup or test result appear complete.

## Publish checklist

1. Review the complete diff, source receipts, media, and test results.
2. Confirm the GitHub Actions workflows cover the changed package paths and
   that all required test and security checks pass on the changes being merged.
3. Verify the applicable CLA and obtain approval of the latest changes from a
   CDE maintainer listed in `CODEOWNERS`. Merge through a pull request under the
   [maintainer policy](maintainer-guide.md). Missing CLA integration or required
   checks block merge until configured and verified. For the one-time CLA setup,
   follow the [reviewed bootstrap sequence](maintainer-guide.md#ci-and-cla-configuration)
   and keep external contribution merges blocked until enforcement is verified.
4. From a clean checkout of `main`, install the GitHub-backed marketplace:

   ```sh
   codex plugin marketplace add tonyloehr/community-plugins --ref main
   codex plugin add grafana-observability@community-plugins
   ```

5. Start a new Codex task and run the plugin's setup skill before sharing the
   release.

Publishing here and inclusion in OpenAI's official Plugins Directory are
separate reviews. This checklist does not replace required release approvals.
