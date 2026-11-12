# Contributing

Thanks for helping make these plugins useful, inspectable, and safe to share.
This is a public Codex marketplace, so a plugin is ready only when a new user
can understand and verify it from a cold start.

## Add or update a plugin

1. Put the package at `plugins/<plugin-name>/`. Use lower-case kebab-case, and
   keep the folder name, marketplace entry name, and manifest `name` identical.
2. Add `plugins/<plugin-name>/.codex-plugin/plugin.json` with accurate public
   metadata, capabilities, authentication behavior, version, repository URL,
   and license.
3. Add or update the entry in
   `.agents/plugins/marketplace.json`. Local source paths must be
   `./plugins/<plugin-name>`.
4. Include a plugin `README.md` that explains the first safe prompt,
   prerequisites, permissions, authentication, data boundaries, and failure
   behavior.
5. Keep tests, fixtures, licenses, and third-party notices with the plugin or
   in clearly named companion folders.
6. Add one `test:<plugin-name>` master suite to `package.json`. It should
   run the plugin's functional, integration/E2E, security, and packaged checks
   as applicable. The marketplace-wide CI job discovers each catalog entry
   and runs that matching test script; plugin-specific CI should expose one
   master job that invokes the same master suite. Put Node versions, native
   builds, audits and reproducibility checks in sequential steps in that job;
   do not split them across platform matrices or additional plugin workflows.
   See [AGENTS.md](AGENTS.md) for the repository's organization convention.

Never commit credentials, OAuth tokens, customer data, private URLs, personal
paths, or generated caches.

## Validate locally

Node.js 22.19 or newer is required for the repository checks:

```sh
npm run validate:marketplace
npm run test:marketplace
npm run validate
```

Run the changed plugin's own test suite too. For Grafana Observability:

```sh
npm run verify:grafana:source
npm run test:grafana
```

The deeper provider, authentication, install, and native-platform checks are in
[the Grafana test guide](tests/grafana-observability/README.md).

For Autodesk Fusion, use the same root master-suite convention:

```sh
# Cold packaged checks do not need development dependencies or Autodesk access.
npm run test:autodesk-fusion:package
# Install only the pinned development dependencies for the complete master.
npm --prefix plugins/autodesk-fusion ci --ignore-scripts
npm run test:autodesk-fusion
```

The [Fusion test guide](tests/autodesk-fusion/README.md) describes its root
unit/integration/security checks, deeper plugin contracts, Python requirement
and explicit external qualification gates. Marketplace CI installs packages'
locked development dependencies without lifecycle scripts before invoking the
catalog-discovered master suites. Autodesk's single `Autodesk Fusion E2E` job
runs its master on Node 22.19, 24 and 26, plus the runtime audit and a host native
source build. Other-platform and licensed-provider qualification are documented
separately from that hosted job.

## Pull requests

External contributors should fork the repository and open a pull request from
their fork. Direct write access is reserved for verified OpenAI full-time
employees who maintain the project.

Keep pull requests focused. Describe:

- what the plugin does and who it is for;
- what commands or code it executes, which files it reads or writes, and what
  data it sends off the machine and to which destinations;
- dependency changes, authentication, and how secrets are stored and redacted;
- how a reviewer can reproduce the happy path and a safe failure path;
- the tests you ran and any intentionally skipped gates;
- license or third-party-notice changes.

Use the [review and publish checklist](docs/review-and-publish.md) before asking
for review. New plugins should include their own validation coverage and update
the marketplace-wide checks when they introduce a new package shape.

Before merging, a CDE maintainer listed in `CODEOWNERS` must approve the latest
changes, the applicable OpenAI Contributor License Agreement (CLA) must be
verified, and all required test and security checks must pass. New changes
require renewed code-owner review. Maintainers must confirm the CLA integration
is configured; a missing check is not evidence of a signed CLA. See the
[maintainer guide](docs/maintainer-guide.md) for the required repository controls.

Read [the Community Plugins CLA](CLA.md). When the CLA Assistant asks, sign by
posting exactly `I have read the CLA Document and I hereby sign the CLA` in your
pull request. Each contributor must sign for themselves; maintainers must also
verify coauthor attribution and any third-party contributions. Ask a maintainer
to coordinate with Legal if your employer requires a corporate CLA.

Report suspected vulnerabilities using the private route in
[SECURITY.md](SECURITY.md), rather than including exploit details in a public
issue or pull request.
