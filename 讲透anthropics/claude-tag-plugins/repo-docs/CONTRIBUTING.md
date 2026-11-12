# Contributing to claude-tag-plugins

## Contributor License Agreement

Before we can merge your pull request, you must sign Anthropic's
[Contributor License Agreement](./CLA.md). The CLA bot will comment on your PR with
instructions the first time you open one.

## Setting up the environment

The only runtime dependencies are `curl` and `jq` (for the bundled scripts). No package
manager setup is needed. Clone the repo and you're ready:

```sh
git clone https://github.com/anthropics/claude-tag-plugins.git
cd claude-tag-plugins
```

To test a script against a real service, export the relevant environment variables and run
the script directly:

```sh
export GLEAN_BASE_URL="https://your-company-be.glean.com"
export GLEAN_API_TOKEN="your-token"
enterprise-search/skills/enterprise-search/scripts/es_search.sh "test query"
```

## Plugin structure

Each plugin lives under `<service>/` and must follow this layout exactly:

```
<service>/
├── .claude-plugin/plugin.json        # Manifest (name, description, version)
└── skills/<service>-api/
    ├── SKILL.md                      # Connection guide and core operations
    ├── references/                   # Full endpoint catalogs, read on demand
    └── scripts/                      # Executable helpers (where present)
```

### SKILL.md guidelines

- Describe how Claude should authenticate and call the API. Credentials must be referenced
  as environment variables — never hardcoded.
- Do not include specific performance numbers or benchmark claims without a citation.
- Keep prose qualitative; let the API reference docs carry the detail.

### Scripts

- Must be POSIX `sh` or `bash` with no dependencies beyond `curl` and `jq`.
- Must be executable (`chmod +x`).
- Exit `0` on success, `1` on any request or API error (error message to stderr).

### Reference docs

- Must be original summaries of the vendor API — not verbatim copies of vendor documentation.
  Vendor docs (Atlassian, Salesforce, Snowflake, etc.) carry restrictive terms; even
  substantial paraphrase can be an issue. Summarise the shape of the API in your own words.

## Adding a new plugin

1. Copy an existing plugin directory as a starting point.
2. Update `.claude-plugin/plugin.json` with the new service's name, description, and version.
3. Write `SKILL.md` — connection guide, core operations, pagination, error handling.
4. Add reference docs under `references/` as needed.
5. Add executable scripts under `scripts/` if the skill is richer for them.
6. Add a row to the plugins table in the root `README.md`.

## Modifying an existing plugin

- For API endpoint changes, update both `SKILL.md` (if the operation is documented there)
  and the relevant `references/*.md` file.
- For script changes, test against the real service before opening a PR.

## Pull request process

1. Fork the repo and create a branch from `main`.
2. Make your changes following the guidelines above.
3. Open a pull request against `main` with a clear description of what changed and why.
4. Sign the CLA when the bot prompts you (first-time contributors only).

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md).
Enforcement contact: opensource@anthropic.com.

## Reporting Security Issues

See [SECURITY.md](./SECURITY.md).
