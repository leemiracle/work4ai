<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-Agent-Toolkit-UI · page 5 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [package.json](package.json)

</details>



This document provides comprehensive guidance for developers working on the AIQ Toolkit-UI project. It covers development environment setup, coding standards, testing procedures, and deployment processes. For information about the overall system architecture, see [Core Architecture](#2). For authentication-specific development details, see [Authentication](#4).

## Overview

The AIQ Toolkit-UI is a Next.js-based React application that provides a chat interface for AI agents and workflows. The development environment supports TypeScript, modern React patterns, and includes comprehensive tooling for code quality, testing, and deployment.

## Development Environment Setup

### Prerequisites and Installation

The project requires Node.js and npm for package management. The development stack is built around Next.js 14 with React 18 and TypeScript.

```mermaid
graph TB
    subgraph "Development Prerequisites"
        NodeJS["Node.js Runtime"]
        NPM["npm Package Manager"]
        Git["Git Version Control"]
    end
    
    subgraph "Core Development Stack"
        NextJS["next: 14.2.25"]
        React["react: ^18.2.0"]
        TypeScript["typescript: 4.9.5"]
    end
    
    subgraph "Development Tools"
        ESLint["eslint: 8.36.0"]
        Prettier["prettier: ^2.8.7"]
        Vitest["vitest: ^0.29.7"]
        Tailwind["tailwindcss: ^3.3.3"]
    end
    
    NodeJS --> NPM
    NPM --> NextJS
    NextJS --> React
    NextJS --> TypeScript
    
    NPM --> ESLint
    NPM --> Prettier
    NPM --> Vitest
    NPM --> Tailwind
```

**Development Environment Architecture**

Sources: [package.json:1-76]()

### Package Scripts and Development Workflow

The project provides several npm scripts for different development tasks:

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `next dev` | Start development server with hot reload |
| `build` | `next build` | Create production build |
| `start` | `next start` | Start production server |
| `lint` | `next lint` | Run ESLint code quality checks |
| `format` | `prettier --write .` | Format code using Prettier |
| `test` | `vitest` | Run test suite |
| `coverage` | `vitest run --coverage` | Generate test coverage report |

Sources: [package.json:5-12]()

## Code Quality and Testing Framework

### Linting and Formatting Pipeline

```mermaid
graph LR
    subgraph "Code Quality Pipeline"
        Developer["Developer Code"]
        ESLintCheck["eslint: 8.36.0<br/>next lint"]
        PrettierFormat["prettier: ^2.8.7<br/>--write ."]
        TypeCheck["typescript: 4.9.5<br/>Type Validation"]
    end
    
    subgraph "Configuration Files"
        ESLintConfig["eslint-config-next"]
        PrettierConfig["prettier-plugin-tailwindcss<br/>@trivago/prettier-plugin-sort-imports"]
        TailwindConfig["@tailwindcss/typography"]
    end
    
    Developer --> ESLintCheck
    Developer --> PrettierFormat  
    Developer --> TypeCheck
    
    ESLintCheck --> ESLintConfig
    PrettierFormat --> PrettierConfig
    TypeCheck --> TailwindConfig
```

**Code Quality Enforcement Architecture**

Sources: [package.json:51-75]()

### Testing Infrastructure

The project uses Vitest as the primary testing framework with coverage reporting capabilities:

- **Test Runner**: `vitest: ^0.29.7`
- **Coverage**: `@vitest/coverage-c8: ^0.29.7`
- **DOM Testing**: `jsdom: ^21.1.1` with `@types/jsdom: ^21.1.1`
- **Additional Testing Utilities**: `@mozilla/readability: ^0.4.4`, `endent: ^2.1.0`

Sources: [package.json:52-75]()

## Dependency Management

### Production Dependencies Architecture

```mermaid
graph TB
    subgraph "Frontend Framework"
        NextJS["next: 14.2.25"]
        React["react: ^18.2.0"]
        ReactDOM["react-dom: ^18.2.0"]
    end
    
    subgraph "Authentication & Security"
        NextAuth["next-auth: ^4.24.7"]
        JWT["jsonwebtoken: ^9.0.2<br/>jwt-decode: ^4.0.0"]
    end
    
    subgraph "Content Processing"
        ReactMarkdown["react-markdown: ^8.0.5"]
        RemarkGFM["remark-gfm: ^3.0.1"]
        RemarkMath["remark-math: ^5.1.1"]
        RehypeMathjax["rehype-mathjax: ^4.0.2"]
        SyntaxHighlighter["react-syntax-highlighter: ^15.5.0"]
    end
    
    subgraph "Data Visualization"
        ChartJS["chart.js: ^4.4.1<br/>react-chartjs-2: ^5.2.0"]
        Recharts["recharts: ^2.12.7"]
        ForceGraph["react-force-graph-2d: ^1.25.5"]
    end
    
    subgraph "Utilities & Integration"
        Lodash["lodash: ^4.17.21"]
        I18Next["i18next: ^22.4.13<br/>next-i18next: ^13.2.2"]
        DatadogRUM["@datadog/browser-rum: ^5.11.0"]
        PPTXGen["pptxgenjs: ^3.12.0"]
    end
    
    NextJS --> React
    NextJS --> ReactDOM
    NextJS --> NextAuth
    
    React --> ReactMarkdown
    ReactMarkdown --> RemarkGFM
    ReactMarkdown --> RemarkMath
    ReactMarkdown --> RehypeMathjax
    React --> SyntaxHighlighter
    
    React --> ChartJS
    React --> Recharts
    React --> ForceGraph
```

**Production Dependencies Hierarchy**

Sources: [package.json:14-49]()

### Key Development Dependencies

| Category | Packages | Purpose |
|----------|----------|---------|
| **Type Definitions** | `@types/node`, `@types/react`, `@types/react-dom`, `@types/uuid` | TypeScript type definitions |
| **Build Tools** | `autoprefixer`, `postcss`, `tailwindcss` | CSS processing and styling |
| **Code Quality** | `eslint-config-next`, `prettier-plugin-tailwindcss` | Linting and formatting |
| **Testing** | `@vitest/coverage-c8`, `jsdom` | Test execution and coverage |

Sources: [package.json:51-75]()

## Contributing Workflow

### Pull Request Process

The project follows a structured contribution workflow as defined in the contributing guidelines:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Fork as "Forked Repository"
    participant Local as "Local Environment"
    participant QualityGates as "Quality Gates"
    participant PR as "Pull Request"
    participant Main as "Main Repository"
    
    Dev->>Fork: "Fork project on GitHub"
    Fork->>Local: "git clone https://github.com/NVIDIA/AIQ Toolkit-UI.git"
    Local->>Local: "git checkout -b my-branch-name"
    
    Dev->>Local: "Make changes"
    Local->>QualityGates: "npm run lint"
    Local->>QualityGates: "npm run format"
    Local->>QualityGates: "npm run test"
    
    QualityGates->>Local: "Validation passed"
    Local->>Fork: "git push origin my-branch-name"
    Fork->>PR: "Submit pull request"
    PR->>Main: "Merge to main branch"
```

**Contribution Workflow Sequence**

Sources: [CONTRIBUTING.md:1-42]()

### Contribution Types

The project welcomes the following types of contributions:

- **Bug fixes**: Resolving identified issues
- **New features**: Adding functionality 
- **Documentation improvements**: Enhancing project documentation
- **Code optimizations**: Performance and maintainability improvements
- **Translations**: Internationalization support
- **Tests**: Expanding test coverage

Sources: [CONTRIBUTING.md:9-18]()

### Branch Management

```mermaid
graph LR
    subgraph "Repository Structure"
        MainRepo["NVIDIA/AIQ Toolkit-UI<br/>main branch"]
        Fork["Developer Fork<br/>forked repository"]
        FeatureBranch["Feature Branch<br/>my-branch-name"]
    end
    
    subgraph "Development Process"
        Clone["git clone"]
        Checkout["git checkout -b"]
        Changes["Code Changes"]
        Commit["git commit"]
        Push["git push"]
        PullRequest["Pull Request"]
    end
    
    MainRepo --> Fork
    Fork --> Clone
    Clone --> Checkout
    Checkout --> FeatureBranch
    FeatureBranch --> Changes
    Changes --> Commit
    Commit --> Push
    Push --> PullRequest
    PullRequest --> MainRepo
```

**Git Workflow for Contributions**

Sources: [CONTRIBUTING.md:22-41]()

## Build and Deployment

### Build Process Architecture

The application uses Next.js build system with support for standalone deployment:

```mermaid
graph TB
    subgraph "Build Pipeline"
        SourceCode["Source Code<br/>TypeScript + React"]
        NextBuild["next build<br/>Production Build"]
        OutputBundle["Build Output<br/>.next/ directory"]
        StandaloneMode["Standalone Mode<br/>Self-contained deployment"]
    end
    
    subgraph "Build Dependencies"
        TypeScriptCompiler["typescript: 4.9.5"]
        PostCSS["postcss: ^8.4.21"]
        Autoprefixer["autoprefixer: ^10.4.14"]
        TailwindCSS["tailwindcss: ^3.3.3"]
    end
    
    subgraph "Runtime Environment"
        NextStart["next start<br/>Production Server"]
        RuntimeEnv["next-runtime-env: ^1.3.0<br/>Environment Configuration"]
    end
    
    SourceCode --> NextBuild
    NextBuild --> OutputBundle
    OutputBundle --> StandaloneMode
    
    TypeScriptCompiler --> NextBuild
    PostCSS --> NextBuild
    Autoprefixer --> NextBuild
    TailwindCSS --> NextBuild
    
    StandaloneMode --> NextStart
    NextStart --> RuntimeEnv
```

**Build and Deployment Architecture**

Sources: [package.json:7-8](), [package.json:74]()

### Development vs Production Modes

| Mode | Command | Purpose | Key Features |
|------|---------|---------|--------------|
| **Development** | `npm run dev` | Local development | Hot reload, source maps, development logging |
| **Production** | `npm run build && npm run start` | Production deployment | Optimized bundles, minification, performance optimizations |

The build process compiles TypeScript, processes CSS through PostCSS and Tailwind, and creates optimized bundles for production deployment.

Sources: [package.json:6-8]()

---

