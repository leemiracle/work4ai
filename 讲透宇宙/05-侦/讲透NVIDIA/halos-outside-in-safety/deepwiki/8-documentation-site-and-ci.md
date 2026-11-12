<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/halos-outside-in-safety · page 8 Documentation Site and CI · fetched 2026-11-09 -->

# Documentation Site and CI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check-docs.yml](.github/workflows/check-docs.yml)
- [.github/workflows/preview-docs.yml](.github/workflows/preview-docs.yml)
- [.github/workflows/publish-docs.yml](.github/workflows/publish-docs.yml)
- [.github/workflows/staging-docs.yml](.github/workflows/staging-docs.yml)
- [docs/index.yml](docs/index.yml)
- [fern/docs.yml](fern/docs.yml)
- [fern/fern.config.json](fern/fern.config.json)
- [fern/redirects.yml](fern/redirects.yml)

</details>



## Purpose and Scope

This page provides a high-level overview of the documentation infrastructure for the Halos Outside-In Safety (HOISA) project. The documentation site is built using the **Fern** platform and authored in Markdown/MDX within `docs/` and `fern/`. Automated validation, preview generation, staging, and production publication are managed via GitHub Actions workflows in `.github/workflows/`.

This is a parent page. For detailed breakdowns of file structures, navigation configuration, redirects, and workflow execution steps, refer to the child pages:
- [Fern Docs Structure](#8.1) — Covers `fern/docs.yml` navigation, `fern/redirects.yml`, MDX organization under `docs/`, and image assets.
- [Docs CI/CD Workflows](#8.2) — Covers `check-docs`, `preview-docs`, `staging-docs`, `publish-docs`, and C API documentation generation pipelines, security secrets, concurrency gating, and environments.

Sources: [fern/docs.yml:1-27](), [.github/workflows/publish-docs.yml:1-76]()

---

## 8.1 Fern Docs Structure

The documentation portal is configured via `fern/docs.yml`, which defines the multi-source site instances, global themes, navbar links, and version definitions [fern/docs.yml:5-27](). Site navigation and hierarchical layout are structured through `docs/index.yml`, grouping content into sections such as Getting Started, Deployment Guide, Integration Guide, Safety Core Components, Closed-Loop Testing, and Reference [docs/index.yml:5-180](). 

To ensure continuity across versions, legacy Sphinx paths and renamed pages are mapped to their modern equivalents using regex rules in `fern/redirects.yml` [fern/redirects.yml:4-95](). All textual documentation is authored in MDX format, requiring strict self-closing tag syntax for elements like `<img>`.

For detailed information on directory organization, navigation mapping, redirects, and asset management, see [Fern Docs Structure](#8.1).

```mermaid
graph TD
    A[fern/docs.yml] --> B[docs/index.yml]
    B --> C[docs/index.mdx]
    B --> D[docs/getting-started/]
    B --> E[docs/deployment/]
    B --> F[docs/testing/]
    G[fern/redirects.yml] --> H[Legacy URL Mapping]
    
    sub: "Natural Language Space to Code Entity Space"
    sub_docs["Markdown & MDX Content"]:::noColor
    sub_config["Fern Configurations"]:::noColor
```
*Diagram: Relationship between Fern configuration, navigation trees, and documentation source directories.*

Sources: [fern/docs.yml:5-27](), [fern/redirects.yml:4-95](), [docs/index.yml:5-180]()

---

## 8.2 Docs CI/CD Workflows

Documentation quality, preview generation, and publishing are automated through a suite of GitHub Actions workflows:

- **`check-docs`**: Validates MDX file syntax (e.g., self-closing `<img>` tags), runs `fern check`, executes `fern docs md check`, and verifies link validity using `fern docs broken-links --strict` [.github/workflows/check-docs.yml:70-89]().
- **`preview-docs`**: Triggers on pull requests affecting `docs/` or `fern/`, builds an isolated documentation preview using `fern generate --docs --preview`, and posts the temporary preview URL back to the pull request [.github/workflows/preview-docs.yml:20-118]().
- **`staging-docs`**: Automatically builds and publishes a staging preview on pushes to the `main` branch [.github/workflows/staging-docs.yml:20-79]().
- **`publish-docs`**: Triggered by engineering release tags or manual dispatches, runs the validation checks first, and targets the production `production` environment for publication [.github/workflows/publish-docs.yml:21-76]().

Concurrency controls and secret gating (`DOCS_FERN_TOKEN`) prevent race conditions and secure publication endpoints. For details on workflow triggers, caching, concurrency groups, and step-by-step execution, see [Docs CI/CD Workflows](#8.2).

```mermaid
graph TD
    PR[Pull Request] -->|Triggers| Check[check-docs.yml]
    PR -->|Triggers| Preview[preview-docs.yml]
    Main[Push to main] -->|Triggers| Staging[staging-docs.yml]
    Tag[Release Tag] -->|Triggers| Publish[publish-docs.yml]
    
    Preview -->|fern generate --preview| FernAPI[BuildWithFern API]
    Staging -->|fern generate --preview| FernAPI
    Publish -->|fern generate --docs| FernProduction[Production Docs Site]

    sub: "Natural Language Space to Code Entity Space"
    Check -->|"check-docs.yml"| MDXCheck[MDX & Link Validation]
    Publish -->|"publish-docs.yml"| ProdEnv[GitHub Environment: production]
```
*Diagram: CI/CD workflow execution paths from code changes to documentation deployment.*

Sources: [.github/workflows/check-docs.yml:21-89](), [.github/workflows/preview-docs.yml:20-118](), [.github/workflows/staging-docs.yml:20-79](), [.github/workflows/publish-docs.yml:21-76]()

---

