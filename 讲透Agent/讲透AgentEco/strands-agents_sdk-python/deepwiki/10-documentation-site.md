<!-- source: DeepWiki mcp.deepwiki.com · repo strands-agents/sdk-python · page 10 Documentation Site · fetched 2026-10-27 -->

# Documentation Site

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/references/mdx-authoring.md](.agents/references/mdx-authoring.md)
- [site/AGENTS.md](site/AGENTS.md)
- [site/package-lock.json](site/package-lock.json)
- [site/package.json](site/package.json)
- [site/scripts/api-generation-python.py](site/scripts/api-generation-python.py)
- [site/src/components/overrides/MarkdownContent.astro](site/src/components/overrides/MarkdownContent.astro)
- [site/src/config/navigation.yml](site/src/config/navigation.yml)
- [site/src/content.config.ts](site/src/content.config.ts)
- [site/src/content/catalog/strands-github-storage.yaml](site/src/content/catalog/strands-github-storage.yaml)
- [site/src/content/docs/contribute/contributing/extensions.mdx](site/src/content/docs/contribute/contributing/extensions.mdx)
- [site/src/content/docs/integrations/storage/github.mdx](site/src/content/docs/integrations/storage/github.mdx)
- [site/src/pages/blog/og/[slug].png.ts](site/src/pages/blog/og/[slug].png.ts)
- [site/src/plugins/remark-mkdocs-snippets.ts](site/src/plugins/remark-mkdocs-snippets.ts)
- [site/src/plugins/vite-plugin-sdk-setup.ts](site/src/plugins/vite-plugin-sdk-setup.ts)
- [site/src/util/github.ts](site/src/util/github.ts)
- [site/src/util/integration-content.ts](site/src/util/integration-content.ts)
- [site/test-snippets/package.json](site/test-snippets/package.json)
- [site/test/languages-schema.test.ts](site/test/languages-schema.test.ts)
- [site/typedoc-tsconfig.json](site/typedoc-tsconfig.json)

</details>



This page provides a high-level overview of the documentation website infrastructure, built using Astro and Starlight. The site serves as the central hub for user guides, API references, examples, and integration catalog for the Strands Agents SDK.

The documentation site is structured to provide a seamless experience for authors and readers, leveraging content collections, automated API documentation generation, and custom components for rich content display.

For detailed information on specific aspects of the documentation site, refer to the following child pages:
- [Site Architecture and Navigation](#10.1) — Covers the Astro/Starlight site structure, navigation, content collections, Zod schemas, language faceting, and custom Markdown rendering.
- [Content Authoring and Code Snippets](#10.2) — Details MDX authoring conventions, code snippet inclusion, multi-language rendering components, and content synchronization pipelines.
- [API Documentation Generation](#10.3) — Explains the automated process for generating API documentation for both Python and TypeScript SDKs.

## Site Overview

The documentation site is a static site generated using Astro and the Starlight theme. It combines Markdown/MDX content with dynamically generated API documentation and an integration catalog. The site's configuration and content are managed within the `site/` directory of the monorepo.

### Key Features

*   **Multi-language support**: Content can be faceted by SDK language (Python/TypeScript).
*   **Automated API Reference**: API documentation for both Python and TypeScript SDKs is automatically generated and integrated.
*   **Integration Catalog**: A browsable catalog of official and community-contributed integrations.
*   **Content Collections**: Structured content for documentation, blog posts, changelogs, and authors.
*   **Custom Components**: Enhancements for code snippets, tabs, and contextual banners.

### Site Structure

The `site/` directory contains all the necessary files for the documentation website.

```
.
├── AGENTS.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SITE-ARCHITECTURE.md
├── src/
│   ├── components/               # Custom Astro components
│   │   ├── overrides/            # Starlight component overrides
│   │   └── ...
│   ├── config/                   # Site configuration (e.g., navigation.yml)
│   ├── content/                  # Content collections (docs, catalog, changelog, blog, authors)
│   │   ├── catalog/              # Community catalog entries (YAML files)
│   │   ├── docs/                 # Documentation content (Markdown/MDX)
│   │   │   ├── api/
│   │   │   │   ├── python/
│   │   │   │   │   └── _generated/   # Symlink to .build/api-docs/python
│   │   │   │   └── typescript/
│   │   │   │       └── _generated/   # Symlink to .build/api-docs/typescript
│   │   │   └── ...
│   │   └── ...
│   ├── data/                     # Bot-maintained data (e.g., catalog-stats.json)
│   ├── layouts/                  # Custom layouts
│   ├── pages/                    # Astro pages (e.g., integrations.astro)
│   ├── plugins/                  # Remark/Rehype plugins (e.g., remark-mkdocs-snippets)
│   ├── styles/                   # Global styles
│   └── util/                     # Utility functions
├── astro.config.mjs              # Astro configuration
├── package.json                  # Node.js dependencies and scripts
├── tsconfig.json                 # TypeScript configuration
├── scripts/                      # Build and utility scripts (e.g., api-generation-python.py)
└── test-snippets/                # TypeScript snippet test files
```
Sources: [site/AGENTS.md:59-99]()

## Site Architecture and Navigation

The documentation site leverages Astro's content collections and Starlight's schema-driven frontmatter validation. Navigation is centrally managed, and content can be faceted by language.

### Astro/Starlight Structure

The site is built on Astro with the Starlight theme, providing a robust framework for documentation. Content is organized into collections defined in `site/src/content.config.ts` [site/src/content.config.ts:1-164]().

### Navigation

The primary navigation structure (navbar and sidebar) is defined in `site/src/config/navigation.yml` [site/src/config/navigation.yml:1-44](). This YAML file acts as the central authority for how pages are presented and linked throughout the site.

### Content Collections and Schemas

Content is organized into several collections, each with a defined Zod schema for frontmatter validation:
*   `docs`: Main documentation pages, validated by `docsSchema` from Starlight, extended with custom fields like `languages`, `community`, and `experimental`. [site/src/content.config.ts:10-25]()
*   `catalog`: Integration entries, validated by `catalogEntrySchema`. [site/src/content.config.ts:97-164]()
*   `changelog`: Release notes, validated by `changelogFrontmatterSchema`. [site/src/content.config.ts:63-87]()
*   `blog`: Blog posts, validated by `blogSchema`. [site/src/content.config.ts:165-170]()
*   `authors`: Author profiles, validated by `authorSchema`. [site/src/content.config.ts:26-31]()

### Language Faceting

Pages can declare support for specific SDK languages (Python, TypeScript) using the `languages` frontmatter field. This drives contextual banners and filtering. The `docsLanguagesSchema` [site/src/content.config.ts:10-25]() ensures that if a feature is available in all languages, the field is omitted rather than explicitly listing all.

### MarkdownContent.astro Override

The `site/src/components/overrides/MarkdownContent.astro` [site/src/components/overrides/MarkdownContent.astro:1-33]() component overrides Starlight's default Markdown rendering to inject contextual banners for experimental features, community contributions, and language support based on page frontmatter.

For details, see [Site Architecture and Navigation](#10.1).

## Content Authoring and Code Snippets

Documentation content is primarily written in MDX, allowing for a mix of Markdown and Astro/React components. A key feature is the ability to embed code snippets directly from source files, ensuring examples are always runnable and up-to-date.

### MDX Authoring Conventions

MDX files (`.mdx`) are used for documentation pages. Common components like `<Tabs>`, `<Tab>`, and `<Syntax>` are globally available for multi-language content rendering.
*   `<Tabs>` and `<Tab>`: Used for displaying language-specific code blocks or content. [site/.agents/references/mdx-authoring.md:9-23]()
*   `<Syntax>`: Used for inline language-specific identifiers within prose. [site/.agents/references/mdx-authoring.md:27-30]()

### Code Snippet Inclusion

Code snippets are pulled directly from source files using the `remark-mkdocs-snippets` plugin. This plugin uses a `--8<--` directive to include specific regions of code files. Snippets are typically organized with separate files for imports and body, which are then combined into a single code block in the MDX. [site/.agents/references/mdx-authoring.md:77-81]()

### Integration Catalog

The integration catalog is populated from YAML files in `site/src/content/catalog/` [site/src/content/catalog/strands-github-storage.yaml:1-9](). Each YAML file represents an integration and is validated against `catalogEntrySchema`. This data is used to generate the `/integrations` page.

### Changelog Sync Pipeline

The changelog is synchronized using a script (`site/scripts/changelog/sync.ts`) [site/package.json:22]() that processes release information and generates changelog entries, validated by `changelogFrontmatterSchema`.

For details, see [Content Authoring and Code Snippets](#10.2).

## API Documentation Generation

The documentation site includes automatically generated API references for both Python and TypeScript SDKs. This ensures that the API documentation is always current with the codebase.

### Automated Generation Process

The API documentation is generated as part of the build process using specific tools for each language:
*   **Python**: `pydoc-markdown` is used to generate documentation from Python docstrings. A custom script `site/scripts/api-generation-python.py` [site/scripts/api-generation-python.py]() orchestrates this process, potentially using custom processors like `CustomGitSourceLinker`, `FilterProcessor`, and `CrossrefProcessor`.
*   **TypeScript**: `Typedoc` is used to generate documentation from TypeScript source code. The `site/scripts/api-generation-typescript.ts` [site/scripts/api-generation-typescript.ts]() script handles the TypeScript generation.

### Build Integration

The generation process is integrated into the site's build pipeline. The `vite-plugin-sdk-setup` [site/src/plugins/vite-plugin-sdk-setup.ts]() plugin triggers the API documentation generation before the Astro build. The `sdk:generate` npm script [site/package.json:19]() combines the Python and TypeScript generation steps.

### API Doc Generation Workflow

```mermaid
graph TD
    A[Developer Commits Code] --> B{GitHub Actions CI}
    B --> C[npm run sdk:generate]
    C --> C1[npm run sdk:generate:py]
    C --> C2[npm run sdk:generate:ts]

    C1 --> D[pydoc-markdown]
    D --> E[Python SDK Source]
    E --> F[Custom Processors]
    F --> G[Generated Python API Docs (Markdown)]

    C2 --> H[tsx scripts/api-generation-typescript.ts]
    H --> I[Typedoc]
    I --> J[TypeScript SDK Source]
    J --> K[Generated TypeScript API Docs (Markdown)]

    G --> L[site/src/content/docs/api/python/_generated/]
    K --> M[site/src/content/docs/api/typescript/_generated/]

    L --> N[Astro Build]
    M --> N

    N --> O[Published Documentation Site]
```
Sources: [site/package.json:17-19](), [site/scripts/api-generation-python.py](), [site/scripts/api-generation-typescript.ts](), [site/src/plugins/vite-plugin-sdk-setup.ts]()

For details, see [API Documentation Generation](#10.3).

---

