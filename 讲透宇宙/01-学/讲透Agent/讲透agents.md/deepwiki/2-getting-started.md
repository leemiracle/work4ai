<!-- source: DeepWiki mcp.deepwiki.com · repo agentsmd/agents.md · page 2 Getting Started · fetched 2026-10-21 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [package.json](package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)

</details>



This document provides step-by-step instructions for setting up the development environment and running the agents.md website locally. For information about the overall architecture, see [Architecture](). For detailed component documentation, see [Components]().

---

## Purpose and Scope

This guide covers:
- Installing dependencies using `pnpm`
- Running the Next.js development server with Turbopack
- Understanding available npm scripts
- Navigating the technology stack

---

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Required Version | Purpose |
|------|------------------|---------|
| Node.js | `^18.18.0`, `^19.8.0`, or `>= 20.0.0` | JavaScript runtime |
| pnpm | `9.15.1` | Package manager |

**Sources:** [pnpm-lock.yaml:1](), [package.json:26]()

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/agentsmd/agents.md.git
cd agents.md
```

### Step 2: Install Dependencies

The project uses `pnpm` as its package manager [package.json:26](). Install all dependencies:

```bash
pnpm install
```

This command reads [package.json:1-27]() and installs:
- **Core framework:** `next: 16.1.0`, `react: 19.2.3`, `react-dom: 19.2.3` [package.json:14-16]()
- **Styling:** `tailwindcss: 4.1.11`, `@tailwindcss/postcss: 4.1.11` [package.json:12,17]()
- **Analytics:** `@vercel/analytics: ^1.5.0` [package.json:13]()
- **Development tools:** `typescript: 5`, `@types/node: 20`, `@types/react: 19`, `@types/react-dom: 19`, `@svgr/webpack: ^8.1.0` [package.json:20-24]()

The lockfile [pnpm-lock.yaml:1]() ensures deterministic, reproducible installs.

**Dependency Installation Flow:**

```mermaid
graph TD
    "Dev"["Developer runs<br/>pnpm install"] --> "ReadPackage"["Read package.json<br/>Dependencies & Scripts"]
    "ReadPackage" --> "ReadLock"["Read pnpm-lock.yaml<br/>Lockfile v6.0"]
    "ReadLock" --> "FetchPkgs"["Fetch packages from registry"]
    "FetchPkgs" --> "InstallNext"["Install next@16.1.0<br/>+ Turbopack/SWC binaries"]
    "FetchPkgs" --> "InstallReact"["Install react@19.2.3<br/>react-dom@19.2.3"]
    "FetchPkgs" --> "InstallTailwind"["Install tailwindcss@4.1.11<br/>+ PostCSS plugin"]
    "FetchPkgs" --> "InstallDevDeps"["Install TypeScript 5.9.2<br/>@svgr/webpack@8.1.0"]
    "InstallNext" --> "NodeModules"["Populate node_modules/"]
    "InstallReact" --> "NodeModules"
    "InstallTailwind" --> "NodeModules"
    "InstallDevDeps" --> "NodeModules"
    "NodeModules" --> "Ready"["Development environment ready"]
```

**Sources:** [package.json:11-27](), [pnpm-lock.yaml:1-43](), [README.md:41-44]()

---

## Running the Development Server

### Start the Server

Use the `dev` script to start the Next.js development server with Turbopack enabled [package.json:6]():

```bash
pnpm run dev
```

This executes the command:
```json
"dev": "next dev --turbopack"
```

**What happens when you run this command:**

```mermaid
graph LR
    "DevCmd"["pnpm run dev"] --> "NextDev"["next dev --turbopack"]
    "NextDev" --> "Turbopack"["Turbopack bundler<br/>Rust-based compilation"]
    "NextDev" --> "LoadConfig"["Load next.config.js<br/>Tailwind config"]
    "Turbopack" --> "CompilePages"["Compile pages/_app.tsx<br/>pages/_document.tsx"]
    "LoadConfig" --> "InitTailwind"["Initialize Tailwind CSS 4.1.11"]
    "CompilePages" --> "StartServer"["Start HTTP server<br/>on localhost:3000"]
    "InitTailwind" --> "StartServer"
    "StartServer" --> "HMR"["Enable Hot Module Replacement"]
    "StartServer" --> "Ready"["Open http://localhost:3000<br/>in browser"]
```

### Access the Application

Once the server is running, open your browser and navigate to:

```
http://localhost:3000
```

**Sources:** [README.md:45-49](), [package.json:6]()

---

## Available Scripts

The [package.json:5-10]() defines the following scripts:

| Script | Command | Purpose |
|--------|---------|---------|
| `pnpm dev` | `next dev --turbopack` | Start development server with Turbopack |
| `pnpm build` | `next build` | Build production-optimized static assets |
| `pnpm start` | `next start` | Serve the production build |
| `pnpm lint` | `next lint` | Run ESLint checks |

**Script Execution Flow:**

```mermaid
graph TD
    "DevFlow"["Development Workflow"]
    "ProdFlow"["Production Workflow"]
    
    "DevFlow" --> "PnpmDev"["pnpm run dev"]
    "PnpmDev" --> "DevServer"["next dev --turbopack<br/>Port 3000"]
    "DevServer" --> "IterDev"["Iterative development<br/>HMR updates"]
    
    "ProdFlow" --> "PnpmBuild"["pnpm run build"]
    "PnpmBuild" --> "NextBuild"["next build<br/>Optimizes assets"]
    "NextBuild" --> "PnpmStart"["pnpm run start"]
    "PnpmStart" --> "ProdServer"["Production server"]
```

**Sources:** [package.json:5-10](), [README.md:40-49]()

---

## Technology Stack

### Core Framework and Libraries

```mermaid
graph TB
    subgraph "Frontend Framework"
        "Next"["next@16.1.0"]
        "React"["react@19.2.3"]
        "ReactDOM"["react-dom@19.2.3"]
    end
    
    subgraph "Build & Performance"
        "Turbopack"["Turbopack<br/>Rust bundler"]
        "SWC"["SWC<br/>Rust compiler"]
    end
    
    subgraph "Styling System"
        "Tailwind"["tailwindcss@4.1.11"]
        "TailwindPost"["@tailwindcss/postcss@4.1.11"]
    end
    
    subgraph "Development Tools"
        "TS"["typescript@5.9.2"]
        "SVGR"["@svgr/webpack@8.1.0"]
    end
    
    "Next" --> "React"
    "Next" --> "ReactDOM"
    "Next" --> "Turbopack"
    "Next" --> "SWC"
    "Tailwind" --> "TailwindPost"
    "Next" --> "TS"
    "Next" --> "SVGR"
```

### Key Technologies Explained

| Technology | Version | Role |
|------------|---------|------|
| **Next.js** | 16.1.0 | Pages Router framework [package.json:14]() |
| **React** | 19.2.3 | UI library [package.json:15]() |
| **Turbopack** | Enabled | Rust-based bundler for development [package.json:6]() |
| **Tailwind CSS** | 4.1.11 | Utility-first CSS framework [package.json:17]() |
| **TypeScript** | 5.9.2 | Type-safe development [pnpm-lock.yaml:42]() |

**Sources:** [package.json:11-25](), [pnpm-lock.yaml:14-43]()

---

## Verification Steps

After starting the development server, verify the setup:

1. **Check Server Output:** Ensure Next.js reports "Ready" and "Turbopack enabled" [package.json:6]().
2. **Verify Page Loads:** Visit `http://localhost:3000` [README.md:49]().
3. **Test HMR:** Edit a component file; the browser should update without a full refresh.

**Sources:** [README.md:45-49](), [package.json:6]()

---

