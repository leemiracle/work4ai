<!-- source: DeepWiki mcp.deepwiki.com · repo openai/euphony · page 6 Infrastructure and Tooling · fetched 2026-10-26 -->

# Infrastructure and Tooling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build.yml](.github/workflows/build.yml)
- [.github/workflows/publish.yml](.github/workflows/publish.yml)
- [.prettierrc](.prettierrc)
- [agents.md](agents.md)
- [eslint.config.js](eslint.config.js)

</details>



Euphony utilizes a modern web development stack centered around **TypeScript**, **pnpm**, and **GitHub Actions**. The project enforces strict code quality through automated linting and formatting, while a template-driven scaffolding system ensures consistency across its custom LitElement components.

### Automation and Lifecycle

The project's lifecycle is managed through `pnpm` and pinned to **Node.js 22** via Corepack [.github/workflows/build.yml:20-23](). The infrastructure is designed to support two primary outputs: a standalone web application and a distributable library bundle.

**Tooling Integration Map**

```mermaid
graph TD
    subgraph "Local Development"
        [".prettierrc"] -- "Formatting" --> ["Source Code"]
        ["eslint.config.js"] -- "Linting" --> ["Source Code"]
        [".fttemplates"] -- "Scaffolding" --> ["New Components"]
    end

    subgraph "CI/CD Pipeline"
        ["Source Code"] -- "Push/PR" --> ["build.yml"]
        ["build.yml"] -- "pnpm build" --> ["dist/ (App)"]
        ["build.yml"] -- "pnpm build:library" --> ["lib/ (Library)"]
        ["Source Code"] -- "v* Tag" --> ["publish.yml"]
        ["publish.yml"] -- "npm publish" --> ["NPM Registry"]
    end

    style ["dist/ (App)"] stroke-dasharray: 5 5
    style ["lib/ (Library)"] stroke-dasharray: 5 5
```

Sources: [.github/workflows/build.yml:1-33](), [.github/workflows/publish.yml:1-36](), [eslint.config.js:1-61](), [.prettierrc:1-6]()

---

### CI/CD Workflows

Euphony employs two main GitHub Actions workflows to maintain code integrity and automate releases:

1.  **Build and Validation**: Triggered on every push to `main` and all pull requests. It ensures that both the standalone application and the library bundle compile successfully using `pnpm build` and `pnpm build:library` [.github/workflows/build.yml:3-32]().
2.  **Automated Publishing**: Triggered by version tags (e.g., `v1.0.0`). This workflow builds the library and publishes the package to the npm registry using OIDC for secure authentication [.github/workflows/publish.yml:3-35]().

For details, see [CI/CD Workflows](#6.1).

Sources: [.github/workflows/build.yml:3-32](), [.github/workflows/publish.yml:3-35]()

---

### Code Quality: Linting and Formatting

The codebase adheres to a strict style guide enforced by **ESLint** and **Prettier**. The configuration is designed to handle the specific requirements of Web Components and TypeScript.

*   **ESLint**: Uses `typescript-eslint` for type-aware linting and `eslint-plugin-lit` to validate Lit templates [eslint.config.js:3-12](). It enforces rules such as single quotes, mandatory semicolons, and restricted use of `var` [eslint.config.js:31-58]().
*   **Prettier**: Standardizes code formatting with an 80-character print width, single quotes, and no trailing commas to ensure diff readability [.prettierrc:2-5]().

**Linting Architecture**

```mermaid
graph LR
    ["eslint.config.js"] --> ["typescript-eslint"]
    ["eslint.config.js"] --> ["eslint-plugin-lit"]
    ["eslint.config.js"] --> ["eslint-plugin-wc"]
    
    subgraph "Rules Enforcement"
        ["typescript-eslint"] --> ["Type Safety"]
        ["eslint-plugin-lit"] --> ["Template Syntax"]
        ["Prettier"] --> ["Visual Consistency"]
    end
```

For details, see [Code Quality: Linting and Formatting](#6.2).

Sources: [eslint.config.js:1-61](), [.prettierrc:1-6]()

---

### Component Scaffolding Templates

To maintain the architectural pattern of the `euphony-*` components, the project uses a file template system located in `.fttemplates/`. This system allows developers to quickly generate new components with a standardized structure, including:

*   **Logic ([FTName].ts)**: A boilerplate `LitElement` class with lifecycle sections, Shadow DOM styles, and automatic registration in the `HTMLElementTagNameMap`.
*   **Styling ([FTName].css)**: A companion stylesheet with default flexbox centering and layout properties.

The system utilizes placeholders like `[FTName | paramcase]` for file naming and `[FTName | pascalcase]` for class definitions to ensure naming convention consistency.

For details, see [Component Scaffolding Templates](#6.3).

Sources: [agents.md:4-5](), [eslint.config.js:12-14]()

---

