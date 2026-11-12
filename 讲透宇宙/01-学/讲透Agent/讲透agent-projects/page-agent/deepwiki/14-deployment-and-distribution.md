<!-- source: DeepWiki mcp.deepwiki.com · repo alibaba/page-agent · page 14 Deployment and Distribution · fetched 2026-10-29 -->

# Deployment and Distribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/deploy-website.yml](.github/workflows/deploy-website.yml)
- [.github/workflows/main-ci.yml](.github/workflows/main-ci.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



This document provides an overview of PageAgent's deployment and distribution strategy. PageAgent is distributed through four primary channels: NPM packages for programmatic integration, CDN-hosted scripts for quick testing, a Chrome Web Store extension for multi-page automation, and an MCP server for integration with AI editors like Cursor or Claude Desktop.

The project uses a monorepo structure with multiple publishable packages, a version synchronization system, and automated build pipelines for each distribution channel.

---

## Distribution Model Overview

PageAgent supports four distinct distribution models, each optimized for different use cases:

**Distribution Architecture**

```mermaid
graph TB
    subgraph "Source: Monorepo [package.json]"
        [PACKAGES] ["packages/*<br/>8 workspace packages"]
    end
    
    subgraph "Published NPM Packages"
        [NPM_MAIN] ["page-agent<br/>Main package"]
        [NPM_CORE] ["@page-agent/core<br/>Headless agent"]
        [NPM_LLMS] ["@page-agent/llms<br/>LLM client"]
        [NPM_PC] ["@page-agent/page-controller<br/>DOM operations"]
        [NPM_UI] ["@page-agent/ui<br/>Panel components"]
        [NPM_MCP] ["@page-agent/mcp<br/>MCP Server"]
    end
    
    subgraph "CDN Distribution"
        [CDN_JSDELIVR] ["jsDelivr CDN<br/>page-agent.demo.js"]
        [CDN_NPMMIRROR] ["npmmirror CDN<br/>China mirror"]
    end
    
    subgraph "Extension Distribution"
        [EXT_BUILD] ["Chrome Extension<br/>WXT Bundle"]
        [EXT_STORE] ["Chrome Web Store<br/>(.zip artifact)"]
    end
    
    subgraph "Website Deployment"
        [GH_PAGES] ["GitHub Pages<br/>Documentation site"]
    end
    
    [PACKAGES] --> [NPM_MAIN]
    [PACKAGES] --> [NPM_CORE]
    [PACKAGES] --> [NPM_MCP]
    [PACKAGES] --> [EXT_BUILD]
    [PACKAGES] --> [GH_PAGES]
    
    [NPM_MAIN] --> [CDN_JSDELIVR]
    [NPM_MAIN] --> [CDN_NPMMIRROR]
```

**Sources:** [package.json:6-23](), [.github/workflows/release.yml:36-45]()

### Distribution Channels

| Channel | Package/Artifact | Primary Use Case | Access Method |
|---------|------------------|------------------|---------------|
| **NPM Registry** | `page-agent`, `@page-agent/*` | Production integration in web apps | `npm install page-agent` |
| **CDN (jsDelivr/npmmirror)** | `page-agent.demo.js` IIFE bundle | Quick testing, bookmarklets | `<script src="...">` |
| **Chrome Web Store** | Extension `.zip` package | Multi-page automation across tabs | Browser extension install |
| **GitHub Pages** | Static documentation site | Documentation and demos | `https://alibaba.github.io/page-agent/` |
| **MCP** | `@page-agent/mcp` | IDE/AI Client control (Cursor/Claude) | `npx @page-agent/mcp` |

**Sources:** [.github/workflows/release.yml:36-45](), [.github/workflows/deploy-website.yml:28-40]()

---

## Monorepo Package Structure

PageAgent is organized as an npm workspaces monorepo containing eight packages. Six packages are public, while two are primarily for distribution artifacts (extension and website).

**Workspace Organization**

```mermaid
graph TB
    subgraph "Public Packages"
        [PA] ["page-agent<br/>Main integration"]
        [CORE] ["@page-agent/core<br/>Headless agent logic"]
        [LLMS] ["@page-agent/llms<br/>LLM client"]
        [PC] ["@page-agent/page-controller<br/>DOM operations"]
        [UI] ["@page-agent/ui<br/>Panel components"]
        [MCP] ["@page-agent/mcp<br/>MCP Server"]
    end
    
    subgraph "Distribution Packages"
        [EXT] ["@page-agent/ext<br/>Chrome extension"]
        [WEB] ["@page-agent/website<br/>Documentation site"]
    end
    
    [PA] --> [CORE]
    [PA] --> [UI]
    [PA] --> [PC]
    
    [CORE] --> [LLMS]
    [CORE] --> [PC]
    
    [EXT] --> [CORE]
    [EXT] --> [UI]
    
    [MCP] --> [CORE]
```

**Sources:** [package.json:6-15]()

---

## Build System Architecture

PageAgent uses specialized build tools for different distribution formats. The root build script [package.json:32]() orchestrates parallel tasks across the workspace.

**Build Pipeline Flow**

```mermaid
graph TD
    [START] ["npm run build"] --> [CLEAN] ["npm run cleanup"]
    [CLEAN] --> [EXECUTION] ["Build Scripts"]
    
    subgraph "Parallel Build Execution"
        [LIBS] ["npm run build:libs<br/>Vite Library Mode"]
        [WEB_BUILD] ["npm run build:website<br/>Vite SPA Mode"]
        [EXT_ZIP] ["npm run build:ext<br/>WXT + ZIP"]
    end
    
    [EXECUTION] --> [LIBS]
    [EXECUTION] --> [WEB_BUILD]
    [EXECUTION] --> [EXT_ZIP]
    
    [LIBS] --> [NPM] ["NPM Registry"]
    [WEB_BUILD] --> [GHP] ["GitHub Pages"]
    [EXT_ZIP] --> [STORE] ["Chrome Web Store"]
```

**Sources:** [package.json:28-45]()

### Build Commands

The root `package.json` provides coordinated build scripts:

```bash
# Build all library packages for NPM
npm run build:libs
# Triggers internal build-libs script

# Build documentation website
npm run build:website
# Triggers 'npm run build:website' in packages/website

# Build everything (libs + website + extension)
npm run build
# Triggers full pipeline
```

**Sources:** [package.json:28-36]()

---

## Version Management and CI/CD

The project maintains synchronized versions across all workspace packages and automates distribution via GitHub Actions.

### Continuous Integration
The `CI` workflow [ .github/workflows/ci.yml:1-30]() runs on every pull request to `main`, executing `node scripts/ci.js` to verify code quality. For code already merged to `main`, the `Main CI` workflow [ .github/workflows/main-ci.yml:1-30]() runs on a trusted self-hosted runner.

### Production Release
The `Release` workflow [ .github/workflows/release.yml:1-46]() is triggered by version tags (e.g., `v*`). It:
1. Builds all library packages using `npm run build:libs` [ .github/workflows/release.yml:34]().
2. Publishes all public packages to the NPM registry [ .github/workflows/release.yml:36-45]().
3. Automatically handles pre-release tags (like `beta`) for npm publishing by extracting the tag name [ .github/workflows/release.yml:39-42]().

### Website Deployment
The `Deploy Website` workflow [ .github/workflows/deploy-website.yml:1-41]() automatically deploys the website to GitHub Pages upon pushes to the `main` branch. It builds the site using `npm run build:website` and uploads the `packages/website/dist` directory as an artifact [ .github/workflows/deploy-website.yml:28-36]().

---

## Next Steps

For detailed information about specific distribution channels:

- **[Building for Production](#14.1)** — Detailed build configurations and production optimization.
- **[NPM Package Distribution](#14.2)** — Versioning strategy and publishing workflow.
- **[CDN and Bookmarklet](#14.3)** — Using the IIFE build for quick injection.
- **[Extension Distribution](#14.4)** — Packaging for the Chrome Web Store.

---

