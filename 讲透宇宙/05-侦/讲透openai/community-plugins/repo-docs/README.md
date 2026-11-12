# Community Plugins

A public, Git-backed marketplace of Codex plugins that developers, prospects,
and enterprise teams can inspect before they install. Each plugin is packaged
with its manifest, setup guide, tests, and license or third-party notices.

The CDE team stewards this collection of public plugins for enterprise use
cases. CDE maintainers review contributions and provide support through
repository issues on a best-effort basis; this
repository does not provide an enterprise support commitment or service-level
agreement.

Inclusion in OpenAI's official Plugins Directory requires a separate review. See
[OpenAI's plugin packaging docs](https://developers.openai.com/plugins/build/plugins)
for the distinction between public directory publishing and repo marketplaces.

## Add it to Codex

In Codex, choose **Add plugin marketplace** and use a repository slug or clone
URL, not a raw `marketplace.json` URL:

```text
Source: tonyloehr/community-plugins
Git ref: main
Sparse paths:
.agents/plugins
plugins
```

Those two sparse paths load the complete plugin catalog without pulling the
top-level test suites or demo media. Package-owned source, contract fixtures,
licenses and build receipts remain included. To fetch every repository file,
leave **Sparse paths** blank. To fetch only Grafana Observability, use these two
paths instead:

```text
.agents/plugins
plugins/grafana-observability
```

To fetch only ReviewOps Auditor + Benchmark, use:

```text
.agents/plugins
plugins/reviewops-auditor-benchmark
```

To fetch only React Native to SwiftUI, use:

```text
.agents/plugins
plugins/react-native-to-swiftui
```

To fetch only Autodesk Fusion interoperability, use:

```text
.agents/plugins
plugins/autodesk-fusion
```

Adding a marketplace makes its catalog available to browse. It does **not**
install, enable, or authenticate every plugin. After adding it, install only
the plugin you want.

The same flow from the CLI:

```sh
# Load the full catalog efficiently.
codex plugin marketplace add tonyloehr/community-plugins \
  --ref main \
  --sparse .agents/plugins \
  --sparse plugins

# Install one plugin from that catalog.
codex plugin add grafana-observability@community-plugins

# Or install the offline ReviewOps package.
codex plugin add reviewops-auditor-benchmark@community-plugins

# Or install the bounded native-migration workflow.
codex plugin add react-native-to-swiftui@community-plugins

# Or install the Fusion interoperability preview (starts in synthetic fixture mode).
codex plugin add autodesk-fusion@community-plugins
```

If you want a full checkout instead of a sparse one:

```sh
codex plugin marketplace add tonyloehr/community-plugins --ref main
```

The `@community-plugins` selector comes from the top-level `name` in
[the marketplace manifest](.agents/plugins/marketplace.json), not from the
GitHub URL. Start a new Codex task after installation so its skills and tools
are picked up.

## Available plugins

| Plugin                                                                         | Purpose                                                                                                                    | Learn more                                                                                                                |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [Grafana Observability](plugins/grafana-observability/README.md)               | Inspect administrator-approved, read-only Grafana evidence for infrastructure, APM, logs, IoT/edge, and business KPIs.     | [Guide](plugins/grafana-observability/README.md) · [23-second demo](docs/media/grafana-production-monitoring-demo-8x.mp4) |
| [ReviewOps Auditor + Benchmark](plugins/reviewops-auditor-benchmark/README.md) | Normalize sanitized review-run exports, audit evaluation validity, benchmark lanes, and emit shadow-only guidance offline. | [Guide](plugins/reviewops-auditor-benchmark/README.md)                                                                    |
| [React Native to SwiftUI](plugins/react-native-to-swiftui/README.md)           | Plan a bounded React Native/Expo feature migration, then port one explicitly approved slice with deterministic SwiftUI parity checks. | [Guide](plugins/react-native-to-swiftui/README.md) |
| [Autodesk Fusion](plugins/autodesk-fusion/README.md) | Connect typed CAD/CAM operations, scoped Autodesk data, reviewed cloud recipes and engineering evidence; live qualification required. | [Guide](plugins/autodesk-fusion/README.md) |

Grafana Observability requires Codex and Node.js 22.19 or newer. Its manifest
declares both `Read` and `Write`. `Write` is limited to
plugin-owned local audit and evidence files; it does not write to Grafana,
datasources, dashboards, services, or deployments.

Its default startup uses a credential-free fixture, so you can verify the
install without touching a Grafana instance:

```text
Use $setup-grafana-observability to check the fixture profile and available packs.
```

ReviewOps Auditor + Benchmark requires Codex and Node.js 22.19 or newer. Its
manifest declares only `Read`; it has no app, MCP server, authentication,
network call, model replay, workflow execution, or writeback path. Its first
run is also synthetic and credential-free:

```text
Use $normalize-review-runs on the bundled synthetic fixture only. Explain the normalization summary, provenance checks, safety boundaries, and next safe step.
```

React Native to SwiftUI requires Codex and Node.js 22.19 or newer. Its
manifest declares both `Read` and `Write`: planning is read-only, while
writes are limited to an explicitly approved target directory for one feature
slice. It has no app or MCP dependency, does not copy source or assets into
the plugin, and does not promise App Store approval. Its first run is a
read-only parity-planning prompt:

```text
Use $plan-react-native-port to inspect only the declared React Native feature and propose a SwiftUI parity contract. Do not edit files yet.
```

Autodesk Fusion requires Codex and Node.js 22.19 or newer. It declares `Read`
and `Write` for scoped desktop changes, local evidence and configured Autodesk
cloud operations. Authentication is `ON_USE`: the initial synthetic fixture
requires no Autodesk account or running Fusion process. Real desktop, cloud and
manufacturing use requires the appropriate license, profile, authority and
independent qualification; installation grants none of these.

```text
Use $setup-autodesk-fusion to check the synthetic fixture and explain the available connection modes. Do not connect to Autodesk or change a real model.
```

## Copy-paste Codex prompts

Browse before installing:

```text
Add the Git-backed marketplace from tonyloehr/community-plugins at ref main. Use sparse paths .agents/plugins and plugins. List the available plugins and recommend the best fit for this repository, but do not install or authenticate anything yet.
```

Install one plugin:

```text
If community-plugins is not already configured, add it from tonyloehr/community-plugins at ref main using sparse paths .agents/plugins and plugins/grafana-observability. Install grafana-observability@community-plugins, explain its permissions and authentication policy, and give me the credential-free smoke-test prompt for a new Codex task.
```

Install ReviewOps without private data:

```text
If community-plugins is not already configured, add it from tonyloehr/community-plugins at ref main using sparse paths .agents/plugins and plugins/reviewops-auditor-benchmark. Install reviewops-auditor-benchmark@community-plugins, explain its read-only offline boundary, and give me the synthetic-fixture smoke-test prompt for a new Codex task.
```

Install React Native to SwiftUI with a read-only first run:

```text
If community-plugins is not already configured, add it from tonyloehr/community-plugins at ref main using sparse paths .agents/plugins and plugins/react-native-to-swiftui. Install react-native-to-swiftui@community-plugins, explain its Read and Write boundaries and ON_USE authentication policy, and give me the read-only parity-planning prompt for a new Codex task.
```

Review before adoption:

```text
Review tonyloehr/community-plugins before I install it. Inspect .agents/plugins/marketplace.json, each plugin manifest, declared capabilities, authentication policy, external endpoints, licenses, and setup instructions. Flag anything that needs security or admin review.
```

## Update or remove

```sh
# Refresh the Git-backed marketplace snapshot.
codex plugin marketplace upgrade community-plugins

# Reinstall a plugin after a new version is published.
codex plugin add grafana-observability@community-plugins
codex plugin add reviewops-auditor-benchmark@community-plugins
codex plugin add react-native-to-swiftui@community-plugins
codex plugin add autodesk-fusion@community-plugins

# Remove the configured marketplace source.
codex plugin marketplace remove community-plugins
```

For an enterprise fork or private mirror, use its HTTPS or SSH clone URL and
make sure Git credentials already work non-interactively. Keep the same
`.agents/plugins/marketplace.json` and `plugins/<name>/` layout.

## Repository layout

Plugin master suites follow `npm run test:<plugin-name>` and are discovered by
`npm run test:marketplace`. Fusion's companion tests live under
[`tests/autodesk-fusion`](tests/autodesk-fusion/README.md), grouped into unit,
integration and security checks. The cold package suite needs no development
dependencies; the full master also rebuilds and runs the deeper Node/Python
contracts:

```sh
npm run test:autodesk-fusion:package
npm --prefix plugins/autodesk-fusion ci --ignore-scripts
npm run test:autodesk-fusion
```

Python 3.12 or newer is required for Fusion's development contract suite, not
for normal Codex startup. The test guide distinguishes synthetic, licensed,
installed-client and native-credential checks; a skipped gate is not a pass.

```text
.agents/plugins/marketplace.json      # Catalog and install policy
plugins/<plugin-name>/                 # One installable plugin
  .codex-plugin/plugin.json            # Required plugin manifest
  README.md                            # Cold-start setup and safety guidance
tests/<plugin-name>/                   # Plugin-specific verification
scripts/                               # Marketplace and package checks
```

## Trust and contributions

Treat every plugin as code you are choosing to run. Review its manifest,
capabilities, authentication policy, setup guide, and license before installing
it. This repository never needs credentials committed to it.

See [CONTRIBUTING.md](CONTRIBUTING.md) to add or update a plugin,
[SECURITY.md](SECURITY.md) to report a vulnerability, and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation expectations. The
repository is Apache-2.0 licensed; individual plugins may carry their own
license and third-party notices.

External contributions use pull requests from forks. CDE code owners review
the latest changes, and contributions must satisfy the CLA, test, and security
requirements before merging. Maintainers follow the
[repository access and merge policy](docs/maintainer-guide.md).
