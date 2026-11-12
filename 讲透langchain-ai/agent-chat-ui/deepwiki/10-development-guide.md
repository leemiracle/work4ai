<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/agent-chat-ui · page 10 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [eslint.config.js](eslint.config.js)
- [package.json](package.json)

</details>



This document provides an overview of the development workflow, tooling, and configuration for the agent-chat-ui codebase. It covers the build system, quality assurance tools, and development processes that contributors should be familiar with when working on the project.

For detailed information about specific aspects of development:
- Build scripts and CI/CD processes: see [Build and CI System](#10.1)
- TypeScript compiler settings: see [TypeScript Configuration](#10.2)
- Package management with pnpm: see [Dependency Management](#10.3)
- Next.js and ESLint configuration: see [Application Configuration](#10.4)

For information about the runtime architecture and deployment options, see [API Integration](#9).

## Development Workflow Overview

The agent-chat-ui project follows a standard Next.js development workflow with integrated code quality checks. The development process uses **pnpm** as the package manager (version 10.5.1), Next.js for the application framework, and automated CI/CD through GitHub Actions.

```mermaid
graph TB
    subgraph "Local Development"
        Clone["git clone repository"]
        Install["pnpm install"]
        Dev["pnpm dev"]
        LocalServer["Next.js Dev Server<br/>http://localhost:3000"]
        
        Clone --> Install
        Install --> Dev
        Dev --> LocalServer
    end
    
    subgraph "Code Quality"
        Format["pnpm format<br/>Prettier Write"]
        FormatCheck["pnpm format:check<br/>Prettier Check"]
        Lint["pnpm lint<br/>ESLint Check"]
        LintFix["pnpm lint:fix<br/>ESLint Fix"]
        
        LocalServer -.-> |Before Commit| Format
        LocalServer -.-> |Before Commit| LintFix
    end
    
    subgraph "Build and Deploy"
        Build["pnpm build<br/>Next.js Build"]
        Start["pnpm start<br/>Production Server"]
        
        Build --> Start
    end
    
    subgraph "CI/CD Pipeline"
        PR["Pull Request"]
        CIFormat["CI: Check formatting"]
        CILint["CI: Check linting"]
        CISpell["CI: Check spelling"]
        Merge["Merge to main"]
        
        PR --> CIFormat
        PR --> CILint
        PR --> CISpell
        CIFormat --> Merge
        CILint --> Merge
        CISpell --> Merge
    end
    
    LocalServer -.-> |Push Changes| PR
    Build -.-> |Verify Locally| PR
    FormatCheck -.-> |Matches CI| CIFormat
    Lint -.-> |Matches CI| CILint
```

**Sources**: [package.json:12-19](), [.github/workflows/ci.yml:21-75]()

## Common Development Commands

The following table lists the primary npm scripts available for development:

| Command | Purpose | Description |
|---------|---------|-------------|
| `pnpm dev` | Start development server | Runs Next.js in development mode with hot-reloading on port 3000 |
| `pnpm build` | Build for production | Creates an optimized production build in `.next/` directory |
| `pnpm start` | Start production server | Serves the production build created by `pnpm build` |
| `pnpm lint` | Check code quality | Runs ESLint to check for code quality issues |
| `pnpm lint:fix` | Fix code issues | Runs ESLint with auto-fix for resolvable issues |
| `pnpm format` | Format code | Runs Prettier to format all files according to style guide |
| `pnpm format:check` | Check formatting | Runs Prettier in check mode without modifying files |

**Sources**: [package.json:12-19]()

## Development Toolchain

The project uses a comprehensive set of tools to maintain code quality and consistency:

```mermaid
graph LR
    subgraph "Source Files"
        TS["TypeScript Files<br/>*.ts, *.tsx"]
        CSS["Styles<br/>Tailwind CSS"]
        MD["Documentation<br/>README.md"]
    end
    
    subgraph "Quality Tools"
        ESLint["ESLint<br/>eslint.config.js"]
        Prettier["Prettier<br/>.prettierrc"]
        Codespell["Codespell<br/>.codespellignore"]
        TSC["TypeScript Compiler<br/>tsconfig.json"]
    end
    
    subgraph "Framework"
        Next["Next.js 15.2.3<br/>next.config.js"]
        React["React 19.0.0"]
    end
    
    subgraph "Package Manager"
        PNPM["pnpm 10.5.1<br/>pnpm-lock.yaml"]
    end
    
    TS --> ESLint
    TS --> Prettier
    TS --> TSC
    TS --> Next
    
    MD --> Prettier
    MD --> Codespell
    
    CSS --> Prettier
    
    Next --> React
    ESLint --> Next
    
    PNPM --> |Manages| Next
    PNPM --> |Manages| React
    PNPM --> |Manages| ESLint
    PNPM --> |Manages| Prettier
```

**Sources**: [package.json:59-83](), [eslint.config.js:1-33](), [.github/workflows/ci.yml:56-75]()

### TypeScript and ESLint

The codebase is written entirely in TypeScript with strict type checking enabled. **ESLint** configuration extends the recommended configurations from `@eslint/js` and `typescript-eslint`, with additional plugins for React:

- `eslint-plugin-react-hooks`: Enforces Rules of Hooks
- `eslint-plugin-react-refresh`: Warns about non-component exports

Key ESLint rules configured in [eslint.config.js:20-31]():
- `@typescript-eslint/no-explicit-any`: Disabled (allows `any` type)
- `@typescript-eslint/no-unused-vars`: Warns on unused variables, with exceptions for underscore-prefixed names
- `react-refresh/only-export-components`: Warns when non-components are exported from component modules

### Code Formatting

**Prettier** is used for consistent code formatting across the codebase. The configuration includes:
- `prettier-plugin-tailwindcss`: Automatically sorts Tailwind CSS class names

Formatting is enforced in CI via the `format:check` script, which runs `prettier --check .` to verify all files match the style guide without modifying them.

**Sources**: [package.json:78](), [.github/workflows/ci.yml:22-37]()

### Spell Checking

The CI pipeline includes spell checking using **codespell** for both documentation and source code:

1. **README spelling check**: Validates spelling in `README.md` using exceptions from `.codespellignore`
2. **Code spelling check**: Validates spelling in all files under `src/` directory

These checks prevent common typos and maintain documentation quality.

**Sources**: [.github/workflows/ci.yml:56-75]()

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration. The workflow is defined in [.github/workflows/ci.yml]() and runs on:
- Every push to `main` branch
- Every pull request
- Manual workflow dispatch

```mermaid
graph TB
    subgraph "Trigger Events"
        Push["Push to main"]
        PR["Pull Request"]
        Manual["Manual Dispatch"]
    end
    
    subgraph "CI Jobs (Parallel)"
        FormatJob["format job<br/>ubuntu-latest<br/>Node 18.x"]
        LintJob["lint job<br/>ubuntu-latest<br/>Node 18.x"]
        ReadmeSpell["readme-spelling job<br/>ubuntu-latest"]
        CodeSpell["check-spelling job<br/>ubuntu-latest"]
    end
    
    subgraph "Format Job Steps"
        F1["actions/checkout@v4"]
        F2["pnpm/action-setup@v4<br/>version: 10.5.1"]
        F3["actions/setup-node@v4<br/>cache: pnpm"]
        F4["pnpm install"]
        F5["pnpm format:check"]
        
        F1 --> F2 --> F3 --> F4 --> F5
    end
    
    subgraph "Lint Job Steps"
        L1["actions/checkout@v4"]
        L2["pnpm/action-setup@v4<br/>version: 10.5.1"]
        L3["actions/setup-node@v4<br/>cache: pnpm"]
        L4["pnpm install"]
        L5["pnpm lint"]
        
        L1 --> L2 --> L3 --> L4 --> L5
    end
    
    Push --> FormatJob
    Push --> LintJob
    Push --> ReadmeSpell
    Push --> CodeSpell
    
    PR --> FormatJob
    PR --> LintJob
    PR --> ReadmeSpell
    PR --> CodeSpell
    
    Manual --> FormatJob
    Manual --> LintJob
    Manual --> ReadmeSpell
    Manual --> CodeSpell
    
    FormatJob --> F1
    LintJob --> L1
```

**Key CI Features**:

1. **Concurrency Control**: The workflow uses `cancel-in-progress: true` to automatically cancel outdated runs when new commits are pushed to the same PR
2. **Parallel Execution**: All four jobs (format, lint, readme-spelling, check-spelling) run in parallel for faster feedback
3. **Cache Optimization**: Node modules are cached using `actions/setup-node` with `cache: "pnpm"` to speed up installation
4. **Consistent Environment**: All jobs use `ubuntu-latest` runners with Node.js 18.x and pnpm 10.5.1

**Sources**: [.github/workflows/ci.yml:1-75]()

## Dependencies Structure

The project dependencies are organized into two categories in [package.json]():

**Runtime Dependencies** ([package.json:21-58]()):
- **LangGraph SDK**: Core integration packages (`@langchain/langgraph-sdk`, `@langchain/langgraph`, `@langchain/core`)
- **Next.js**: Application framework and React runtime
- **UI Libraries**: Radix UI primitives, Lucide icons, Framer Motion animations
- **Content Rendering**: `react-markdown`, `react-syntax-highlighter`, `rehype-katex`, `remark-gfm`
- **State Management**: `nuqs` for URL-based state
- **API Integration**: `langgraph-nextjs-api-passthrough` for production deployment
- **Utilities**: `date-fns`, `lodash`, `uuid`, `zod`

**Development Dependencies** ([package.json:59-83]()):
- **Type Definitions**: `@types/*` packages for TypeScript support
- **Build Tools**: Next.js, Tailwind CSS, PostCSS, esbuild
- **Code Quality**: ESLint, Prettier, typescript-eslint
- **Environment**: `dotenv` for local development

The `packageManager` field specifies `pnpm@10.5.1`, ensuring consistent dependency resolution across all development environments.

**Sources**: [package.json:21-87]()

## Local Development Setup

To set up a local development environment:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/langchain-ai/agent-chat-ui.git
   cd agent-chat-ui
   ```

2. **Install dependencies**:
   ```bash
   pnpm install
   ```
   The project enforces pnpm usage through the `packageManager` field.

3. **Configure environment variables**:
   Create a `.env.local` file with required configuration (see [Configuration System](#9.1) for details).

4. **Start development server**:
   ```bash
   pnpm dev
   ```
   The application will be available at `http://localhost:3000`.

5. **Verify setup**:
   ```bash
   pnpm lint
   pnpm format:check
   ```

For production builds:
```bash
pnpm build
pnpm start
```

**Sources**: [package.json:12-19](), [package.json:87]()

## Development Best Practices

When contributing to the codebase:

1. **Run quality checks before committing**:
   - Use `pnpm format` to auto-format code
   - Use `pnpm lint:fix` to auto-fix linting issues
   - Verify with `pnpm lint` and `pnpm format:check`

2. **Follow TypeScript conventions**:
   - Use typed components and hooks
   - Avoid `any` type when possible (though not strictly forbidden)
   - Prefix unused parameters with underscore (e.g., `_unused`)

3. **Component exports**:
   - Export only components from component files
   - Use separate files for utilities and constants

4. **Naming conventions**:
   - Use PascalCase for components and types
   - Use camelCase for functions and variables
   - Use underscore prefix for intentionally unused parameters

5. **Build verification**:
   - Run `pnpm build` locally to ensure production builds succeed
   - The CI pipeline does not run build checks, so this is a developer responsibility

**Sources**: [eslint.config.js:20-31](), [.github/workflows/ci.yml:21-75]()

---

For detailed information about specific development topics, see the child pages:
- [Build and CI System](#10.1): Detailed documentation of build scripts and CI/CD pipeline
- [TypeScript Configuration](#10.2): Compiler options and module resolution settings
- [Dependency Management](#10.3): pnpm usage and lockfile structure
- [Application Configuration](#10.4): Next.js, ESLint, and other configuration files

---

