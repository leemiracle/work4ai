<!-- source: DeepWiki mcp.deepwiki.com · repo openai/apps-sdk-ui · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/deploy-storybook.yml](.github/workflows/deploy-storybook.yml)
- [.gitignore](.gitignore)
- [.storybook-base/main.ts](.storybook-base/main.ts)

</details>



This document provides instructions for setting up the development environment and running the Storybook documentation platform locally. It covers prerequisites, installation steps, available npm scripts, and the build process. For detailed information about Storybook configuration options, see [Storybook Configuration](#3). For deployment and CI/CD details, see [CI/CD & Deployment](#7).

## Prerequisites

The repository requires the following software to be installed:

| Software | Version | Purpose |
|----------|---------|---------|
| Node.js | 20 | Runtime environment for building and running Storybook |
| npm | Latest (bundled with Node.js) | Package manager for dependency installation |
| Git | Any recent version | Version control for cloning the repository |

The Node.js version requirement is specified in the GitHub Actions workflow at [.github/workflows/deploy-storybook.yml:28]().

**Sources:** `.github/workflows/deploy-storybook.yml`

## Installation

### Clone the Repository

```bash
git clone https://github.com/openai/apps-sdk-ui.git
cd apps-sdk-ui
```

### Install Dependencies

Install all required packages using npm:

```bash
npm ci
```

The `npm ci` command (clean install) is used instead of `npm install` to ensure reproducible builds by strictly following the `package-lock.json` file. This is the same approach used in the CI/CD pipeline at [.github/workflows/deploy-storybook.yml:32]().

**Sources:** `.github/workflows/deploy-storybook.yml`

## Development Workflow

### Development Workflow Overview

```mermaid
graph TD
    START["Developer Environment"]
    CLONE["git clone repository"]
    INSTALL["npm ci"]
    DEV["npm run storybook"]
    LOCAL["Storybook Dev Server<br/>localhost:6006"]
    EDIT["Edit components/stories"]
    HMR["Hot Module Replacement<br/>Auto-refresh"]
    
    START --> CLONE
    CLONE --> INSTALL
    INSTALL --> DEV
    DEV --> LOCAL
    LOCAL --> EDIT
    EDIT --> HMR
    HMR --> LOCAL
    
    style START fill:#f9f9f9
    style LOCAL fill:#f9f9f9
    style HMR fill:#f9f9f9
```

**Sources:** `.github/workflows/deploy-storybook.yml`, `.storybook-base/main.ts`

### Running Storybook Locally

To start the Storybook development server:

```bash
npm run storybook
```

This command launches a local development server with hot module replacement (HMR), typically accessible at `http://localhost:6006`. Changes to component files and stories are automatically reflected in the browser without requiring a full page reload.

### Building for Production

To build a static version of Storybook for deployment:

```bash
npm run build-storybook
```

This command generates static HTML, CSS, and JavaScript files in the `storybook-static` directory (configurable via the `--output-dir` flag). The build command is defined at [.github/workflows/deploy-storybook.yml:35]() and uses Vite as the bundler.

**Sources:** `.github/workflows/deploy-storybook.yml`, `.storybook-base/main.ts`

## Build Process Architecture

### Build Pipeline Stages

```mermaid
graph LR
    subgraph "Source Files"
        STORIES["Story Files<br/>src/**/*.stories.*"]
        MDX["MDX Documentation<br/>src/**/*.mdx"]
        COMPONENTS["React Components<br/>src/components/*"]
        STORYBOOK_COMP["Storybook Components<br/>.storybook-base/components/*"]
    end
    
    subgraph "Configuration"
        MAIN_TS["main.ts<br/>StorybookConfig"]
        VITE_CONFIG["vite.config.mjs"]
        TS_CONFIG["tsconfig.json"]
    end
    
    subgraph "Build Tools"
        VITE["Vite Bundler<br/>@storybook/react-vite"]
        TS["TypeScript Compiler<br/>react-docgen-typescript"]
        ADDONS["Storybook Addons"]
    end
    
    subgraph "Output"
        STATIC["storybook-static/<br/>Static HTML/CSS/JS"]
        ASSETS["Static Assets<br/>from public/"]
    end
    
    STORIES --> VITE
    MDX --> VITE
    COMPONENTS --> VITE
    STORYBOOK_COMP --> VITE
    
    MAIN_TS --> VITE
    VITE_CONFIG --> VITE
    TS_CONFIG --> TS
    
    TS --> VITE
    ADDONS --> VITE
    
    VITE --> STATIC
    ASSETS --> STATIC
```

**Sources:** `.storybook-base/main.ts`, `.github/workflows/deploy-storybook.yml`

## File Structure Overview

After cloning and installing dependencies, the repository structure includes:

| Directory/File | Description | Version Control |
|----------------|-------------|-----------------|
| `.storybook-base/` | Storybook configuration and custom components | Tracked |
| `src/` | Source component files and stories | Tracked |
| `public/` | Static assets served by Storybook | Tracked |
| `node_modules/` | Installed npm dependencies | Ignored |
| `dist/` | Build output directory | Ignored |
| `storybook-static/` | Built Storybook static files | Ignored (generated) |
| `.next/` | Next.js build cache | Ignored |
| `__pycache__/` | Python cache files | Ignored |

Files and directories excluded from version control are defined in [.gitignore:1-17]().

**Sources:** `.gitignore`

## Story Discovery and Configuration

### Story Pattern Matching

Storybook automatically discovers story files using the patterns defined in [.storybook-base/main.ts:5]():

```
stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|ts|tsx)"]
```

This configuration matches:
- **MDX files**: Documentation pages with interactive examples
- **Story files**: Component stories in JavaScript or TypeScript

### Static Asset Serving

Static assets located in the `public/` directory are served by Storybook during development and included in production builds. This is configured via the `staticDirs` option at [.storybook-base/main.ts:52]().

**Sources:** `.storybook-base/main.ts`

## Build Configuration Details

### Vite Integration

The Storybook build process uses Vite as its bundler, configured through the `@storybook/react-vite` framework at [.storybook-base/main.ts:44-50]():

```mermaid
graph TB
    MAIN_TS["main.ts<br/>StorybookConfig"]
    FRAMEWORK["framework.name<br/>@storybook/react-vite"]
    VITE_CONFIG_PATH["builder.viteConfigPath<br/>./vite.config.mjs"]
    VITE_FINAL["viteFinal hook"]
    
    subgraph "Vite Customizations"
        ENV_VAR["IS_STORYBOOK=true<br/>Environment variable"]
        ALIAS["@storybookComponents<br/>Path alias"]
        ASSETS["assetsInclude<br/>sb-preview/runtime.js"]
        ESBUILD["esbuild.tsconfigRaw<br/>verbatimModuleSyntax: false"]
    end
    
    MAIN_TS --> FRAMEWORK
    FRAMEWORK --> VITE_CONFIG_PATH
    MAIN_TS --> VITE_FINAL
    
    VITE_FINAL --> ENV_VAR
    VITE_FINAL --> ALIAS
    VITE_FINAL --> ASSETS
    VITE_FINAL --> ESBUILD
```

The `viteFinal` hook at [.storybook-base/main.ts:53-76]() applies several customizations:

1. **Environment Variable**: Sets `IS_STORYBOOK=true` to enable conditional logic in components
2. **Path Alias**: Creates `@storybookComponents` alias pointing to `.storybook-base/components/` for convenient imports in MDX files
3. **Asset Includes**: Adds `/sb-preview/runtime.js` to prevent build errors
4. **TypeScript Configuration**: Overrides `verbatimModuleSyntax` to `false` for Storybook compatibility

**Sources:** `.storybook-base/main.ts`

### TypeScript Configuration

TypeScript integration is configured at [.storybook-base/main.ts:36-43]() using `react-docgen-typescript` for automatic prop documentation generation:

| Option | Value | Purpose |
|--------|-------|---------|
| `reactDocgen` | `"react-docgen-typescript"` | Documentation generator |
| `savePropValueAsString` | `true` | Preserve prop values as strings for display |
| `shouldRemoveUndefinedFromOptional` | `true` | Clean up optional prop types |
| `shouldExtractLiteralValuesFromEnum` | `true` | Extract enum values for documentation |

**Sources:** `.storybook-base/main.ts`

## CI/CD Build Process

The automated build and deployment process is triggered by pushes to the `main` branch or manual workflow dispatch. The pipeline consists of two jobs:

### Build Job

The build job executes the following steps on `ubuntu-latest`:

1. **Checkout**: Retrieves the repository code using `actions/checkout@v4`
2. **Node Setup**: Installs Node.js 20 with npm cache using `actions/setup-node@v4`
3. **Dependencies**: Runs `npm ci` to install packages
4. **Build**: Executes `npm run build-storybook --output-dir storybook-static`
5. **Upload**: Uploads the `storybook-static` directory as a GitHub Pages artifact

### Deploy Job

The deploy job runs after the build job completes and publishes the artifact to GitHub Pages using `actions/deploy-pages@v4`.

For complete CI/CD documentation, see [GitHub Actions Workflow](#7.1).

**Sources:** `.github/workflows/deploy-storybook.yml`

## Next Steps

After successfully running Storybook locally, you can:

1. **Explore the Design System**: Review design tokens and themes in [Design System](#5)
2. **Customize Themes**: Understand theme configuration in [Theme System](#5.2)
3. **Create Documentation Components**: Learn about custom components in [Documentation Components](#6)
4. **Configure Addons**: Explore custom addons in [Custom Addons](#4)

**Sources:** `.storybook-base/main.ts`, `.github/workflows/deploy-storybook.yml`, `.gitignore`

---

