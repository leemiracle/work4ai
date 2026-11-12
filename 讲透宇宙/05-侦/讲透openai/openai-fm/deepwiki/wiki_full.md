# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [package.json](package.json)

</details>



This document provides a high-level introduction to the OpenAI.fm codebase, summarizing its purpose, core features, technology stack, and architectural patterns. For detailed setup instructions, see [Getting Started](#2). For in-depth technical documentation of individual subsystems, see [System Architecture](#3).

## Purpose

OpenAI.fm is a Next.js-based demonstration application that showcases OpenAI's text-to-speech capabilities through an interactive web interface. The application allows users to generate audio from text input, apply voice transformations through system prompts, visualize audio playback, and share configurations via persistent links.

**Sources:** [README.md:1-10]()

## Project Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Project Name** | `openai-fm` |
| **License** | MIT License |
| **Primary Language** | TypeScript |
| **Framework** | Next.js 15.3.6 with App Router |
| **Runtime** | React 19.0.0 |
| **Deployment Target** | Vercel Platform (recommended) |
| **External Dependencies** | OpenAI Speech API, PostgreSQL (optional) |

**Sources:** [package.json:1-4](), [LICENSE:1-19](), [README.md:1-8]()

## Core Features

The application implements four primary user-facing features:

1. **Audio Generation**: Text-to-speech synthesis using OpenAI's API with configurable voice selection (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`)
2. **Waveform Visualization**: Real-time audio amplitude visualization during playback using Web Audio API
3. **Download Capability**: Browser-based audio file download with service worker caching
4. **Share Functionality**: Persistent configuration storage enabling shareable URLs (requires PostgreSQL)

**Sources:** [README.md:7-10](), Diagram 1, Diagram 2

## Technology Stack

### Frontend Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| `next` | 15.3.6 | Application framework with SSR/SSG support |
| `react` | 19.0.0 | UI component library |
| `zustand` | 5.0.3 | State management (`AppStore`) |
| `@radix-ui/*` | Various | Accessible UI primitives (Switch, Toast, Icons) |
| `tailwindcss` | 4.x | Utility-first styling |
| `@uiw/react-codemirror` | 4.23.10 | Code snippet display |
| `wavesurfer.js` | 7.9.1 | Audio waveform visualization |

### Backend Technologies

| Technology | Purpose |
|-----------|---------|
| Next.js API Routes | Server-side request proxying |
| `@vercel/postgres` | PostgreSQL database client |
| OpenAI Speech API | `gpt-4o-mini-tts` model for audio synthesis |

### Build Tools

| Tool | Purpose |
|------|---------|
| TypeScript | Static type checking |
| ESLint | Code quality enforcement |
| PostCSS | CSS processing pipeline |
| Turbopack/Webpack | Module bundling |

**Sources:** [package.json:11-42]()

## System Architecture

### High-Level Component Topology

The following diagram maps the major system components to their code entity implementations:

```mermaid
graph TB
    subgraph Browser["Browser Environment"]
        ClientDynamicTTS["ClientDynamicTTS<br/>(src/components/ClientDynamicTTS.tsx)"]
        PlayButton["PlayButton<br/>(src/components/PlayButton.tsx)"]
        DownloadButton["DownloadButton<br/>(src/components/DownloadButton.tsx)"]
        ShareButton["ShareButton<br/>(src/components/ShareButton.tsx)"]
        AppStore["AppStore<br/>(Zustand store in component files)"]
        ServiceWorker["Service Worker<br/>(public/worker-*.js)"]
    end
    
    subgraph NextJS["Next.js Server"]
        RootLayout["RootLayout<br/>(src/app/layout.tsx)"]
        Page["Page<br/>(src/app/page.tsx)"]
        APIGenerate["/api/generate<br/>(src/app/api/generate/route.ts)"]
        APIShare["/api/share<br/>(src/app/api/share/route.ts)"]
        Middleware["Middleware<br/>(src/app/tmp.middleware.ts)"]
    end
    
    subgraph External["External Services"]
        OpenAISpeech["OpenAI Speech API<br/>/v1/audio/speech"]
        PostgresDB["PostgreSQL<br/>shares table"]
    end
    
    RootLayout --> Page
    Page --> ClientDynamicTTS
    ClientDynamicTTS --> PlayButton
    ClientDynamicTTS --> DownloadButton
    ClientDynamicTTS --> ShareButton
    
    PlayButton --> AppStore
    DownloadButton --> AppStore
    ShareButton --> AppStore
    
    PlayButton --> APIGenerate
    ShareButton --> APIShare
    DownloadButton --> ServiceWorker
    
    Middleware --> Page
    Middleware --> APIGenerate
    Middleware --> APIShare
    
    APIGenerate --> OpenAISpeech
    APIShare --> PostgresDB
```

**Sources:** Diagram 1, Diagram 4, [src/app/layout.tsx](), [src/app/page.tsx](), [src/components/ClientDynamicTTS.tsx](), [src/components/PlayButton.tsx](), [src/components/DownloadButton.tsx](), [src/components/ShareButton.tsx](), [src/app/api/generate/route.ts](), [src/app/api/share/route.ts]()

### Request Flow Architecture

The following diagram illustrates how user actions map to code execution paths:

```mermaid
sequenceDiagram
    participant User
    participant PlayButton as "PlayButton<br/>component"
    participant AppStore as "AppStore<br/>(Zustand)"
    participant APIGenerate as "/api/generate<br/>route.ts"
    participant OpenAI as "OpenAI API<br/>/v1/audio/speech"
    participant AudioContext as "Web Audio API<br/>AudioContext"
    participant ServiceWorker as "Service Worker<br/>worker-*.js"
    
    User->>PlayButton: "Click play button"
    PlayButton->>AppStore: "getState()"
    AppStore-->>PlayButton: "{input, prompt, voice}"
    PlayButton->>APIGenerate: "GET /api/generate?input=...&voice=..."
    APIGenerate->>OpenAI: "POST with model: 'gpt-4o-mini-tts'"
    OpenAI-->>APIGenerate: "Audio stream"
    APIGenerate-->>PlayButton: "Audio response"
    PlayButton->>AudioContext: "createAnalyser()"
    AudioContext-->>PlayButton: "Amplitude data"
    PlayButton->>ServiceWorker: "Cache audio blob"
    PlayButton->>PlayButton: "Audio.play()"
    PlayButton-->>User: "Playback + visualization"
```

**Sources:** Diagram 2, [src/components/PlayButton.tsx](), [src/app/api/generate/route.ts](), [public/worker-444eae9e2e1bdd6edd8969f319655e70.js]()

## Key System Components

### State Management: AppStore

The application uses Zustand for centralized state management. The store maintains:

- `input`: Text to be converted to speech
- `prompt`: System prompt for voice transformation
- `voice`: Selected voice identifier (`alloy` | `echo` | `fable` | `onyx` | `nova` | `shimmer`)
- `latestAudioUrl`: Most recently generated audio URL

All interactive components (`PlayButton`, `DownloadButton`, `ShareButton`, `CodeCopyButton`) access this shared state.

**Sources:** Diagram 1, Diagram 4, [src/components/PlayButton.tsx](), [src/components/DownloadButton.tsx](), [src/components/ShareButton.tsx]()

### API Proxy: /api/generate

Located at [src/app/api/generate/route.ts](), this Next.js API route serves as a secure proxy to the OpenAI Speech API. It:

1. Accepts query parameters: `input`, `prompt`, `voice`
2. Validates and truncates input to maximum lengths
3. Authenticates to OpenAI using `OPENAI_API_KEY` environment variable
4. Forwards requests to `https://api.openai.com/v1/audio/speech`
5. Streams audio response back to client

This architecture prevents exposure of the API key to client browsers.

**Sources:** [src/app/api/generate/route.ts](), Diagram 2, [README.md:27-36]()

### Persistence Layer: /api/share

Located at [src/app/api/share/route.ts](), this route handles configuration persistence:

- **POST**: Stores `{input, prompt, voice}` in PostgreSQL `shares` table, returns UUID hash
- **GET**: Retrieves configuration by hash from database

The database connection requires `POSTGRES_URL` environment variable. This feature is optional; the application functions without database connectivity.

**Sources:** [src/app/api/share/route.ts](), Diagram 3, [README.md:46-55](), [.env.example]()

### Audio Caching: Service Worker

The service worker at [public/worker-444eae9e2e1bdd6edd8969f319655e70.js]() implements client-side audio caching:

1. Intercepts audio URL requests
2. Stores audio blobs in browser cache
3. Serves cached content for subsequent plays
4. Enables offline playback and reduces API calls

Integration occurs in `DownloadButton` and `PlayButton` components via `postMessage` API.

**Sources:** [public/worker-444eae9e2e1bdd6edd8969f319655e70.js](), Diagram 2, [src/components/DownloadButton.tsx]()

### Dynamic Client Rendering

The `ClientDynamicTTS` component at [src/components/ClientDynamicTTS.tsx]() uses Next.js dynamic imports with `ssr: false` to prevent server-side rendering of browser-dependent code (Web Audio API, service worker registration). The main page component at [src/app/page.tsx]() imports this dynamically.

**Sources:** [src/components/ClientDynamicTTS.tsx](), [src/app/page.tsx](), Diagram 4

## Build and Development Configuration

### Package Management

The project uses npm with locked dependencies:

- [package.json:1-43]() defines dependencies and build scripts
- [package-lock.json]() ensures reproducible builds
- Scripts: `dev` (Turbopack), `build`, `start`, `lint`

**Sources:** [package.json:1-43](), Diagram 5

### Next.js Configuration

[next.config.ts]() configures:

- Webpack/Turbopack bundler settings
- SVGR loader for SVG-to-React-component transformation
- Content Security Policy headers
- HSTS headers (production)

**Sources:** [next.config.ts](), Diagram 5, Diagram 6

### Styling Pipeline

The styling system uses:

- TailwindCSS 4.x for utility classes
- [postcss.config.mjs]() for PostCSS integration
- [src/app/globals.css]() for CSS custom properties and global styles

**Sources:** [postcss.config.mjs](), [src/app/globals.css](), Diagram 4, Diagram 5

## Security Model

The application implements multiple security layers:

1. **Nonce-based CSP**: [src/app/tmp.middleware.ts]() injects unique nonces for inline scripts
2. **Static CSP Headers**: [next.config.ts]() defines Content Security Policy restricting resource origins
3. **HSTS**: HTTP Strict Transport Security enforced in production
4. **API Key Isolation**: OpenAI credentials stored server-side, never exposed to clients
5. **Environment Secrets**: `.env.local` for sensitive configuration (not committed to version control)

For comprehensive security documentation, see [Security Considerations](#5).

**Sources:** [src/app/tmp.middleware.ts](), [next.config.ts](), [.env.example](), Diagram 6

## Deployment

The application is designed for deployment on Vercel:

1. Automatic builds triggered by repository commits
2. Environment variables configured via Vercel dashboard
3. Optional Vercel PostgreSQL integration for sharing feature
4. Edge network distribution for global performance

The repository includes standard Vercel configuration files and follows Next.js deployment best practices.

**Sources:** [README.md:65-66](), Diagram 5

## Development Workflow

Typical development workflow:

```bash
# Install dependencies
npm install

# Start development server (Turbopack)
npm run dev

# Run linter
npm run lint

# Production build
npm run build

# Start production server
npm start
```

The development server runs at `http://localhost:3000` with hot module replacement enabled.

**Sources:** [package.json:5-10](), [README.md:38-63]()

## Project Structure Summary

| Directory/File | Purpose |
|---------------|---------|
| `src/app/` | Next.js App Router pages, layouts, API routes, middleware |
| `src/components/` | React components (PlayButton, ShareButton, etc.) |
| `public/` | Static assets (service worker, images, audio files) |
| `package.json` | Dependency manifest and build scripts |
| `next.config.ts` | Next.js framework configuration |
| `postcss.config.mjs` | CSS processing configuration |
| `eslint.config.mjs` | Code quality rules |
| `tsconfig.json` | TypeScript compiler settings |
| `.env.example` | Environment variable template |

**Sources:** [package.json](), [next.config.ts](), [postcss.config.mjs](), [README.md]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [package.json](package.json)

</details>



This page guides you through the initial setup and configuration of the OpenAI.fm application, including prerequisites, environment setup, and running the development server. For detailed installation instructions and package management, see [Installation and Setup](#2.1). For comprehensive environment variable configuration, see [Environment Configuration](#2.2).

## Purpose and Scope

OpenAI.fm is a Next.js application that demonstrates OpenAI's text-to-speech API capabilities. This guide covers:

- System prerequisites and requirements
- Quick start instructions
- Understanding the setup components
- Verifying your installation

This page provides an overview of the setup process. Detailed configuration and troubleshooting are covered in child pages.

## Prerequisites

Before starting, ensure you have the following:

| Requirement | Description | Documentation |
|------------|-------------|---------------|
| **Node.js** | JavaScript runtime (version 20 or higher recommended) | Based on `@types/node` version constraint in [package.json:35]() |
| **npm** | Node package manager (comes with Node.js) | Used by scripts in [package.json:5-9]() |
| **OpenAI API Key** | Required for text-to-speech functionality | See [OpenAI Platform](https://platform.openai.com) |
| **Git** | For cloning the repository | Standard version control tool |
| **PostgreSQL** (Optional) | Required only for sharing feature | See [README.md:46-56]() |

**Sources:** [package.json:32-42](), [README.md:14-66]()

## Quick Start Overview

The setup process consists of four essential steps:

1. Clone the repository from GitHub
2. Configure the OpenAI API key in environment variables
3. Install dependencies using npm
4. Start the development server

Optional: Configure PostgreSQL database for the sharing feature.

The following diagram illustrates the setup components and their relationships to actual files and code entities in the codebase:

### Setup Components and File Mapping

```mermaid
graph TD
    subgraph "Repository"
        Clone["git clone<br/>openai/openai-fm"]
    end
    
    subgraph "Configuration Files"
        EnvExample[".env.example<br/>Template"]
        EnvLocal[".env<br/>or .env.local<br/>Runtime Secrets"]
        PackageJSON["package.json<br/>Dependencies & Scripts"]
        PackageLock["package-lock.json<br/>Locked Versions"]
    end
    
    subgraph "Environment Variables"
        APIKey["OPENAI_API_KEY<br/>Required"]
        PostgresURL["POSTGRES_URL<br/>Optional"]
    end
    
    subgraph "NPM Scripts"
        DevScript["npm run dev<br/>Starts next dev --turbopack"]
        BuildScript["npm run build<br/>Runs next build"]
        StartScript["npm start<br/>Runs next start"]
        LintScript["npm run lint<br/>Runs next lint"]
    end
    
    subgraph "Runtime Components"
        NextDev["Next.js Dev Server<br/>Port 3000<br/>Turbopack enabled"]
        APIGenerate["/api/generate<br/>Requires OPENAI_API_KEY"]
        APIShare["/api/share<br/>Requires POSTGRES_URL"]
    end
    
    Clone --> PackageJSON
    Clone --> EnvExample
    
    EnvExample -.->|"Copy & configure"| EnvLocal
    
    EnvLocal --> APIKey
    EnvLocal --> PostgresURL
    
    PackageJSON --> DevScript
    PackageJSON --> BuildScript
    PackageJSON --> StartScript
    PackageJSON --> LintScript
    
    PackageJSON --> PackageLock
    PackageLock -.->|"Installs via"| NodeModules["node_modules/"]
    
    DevScript --> NextDev
    
    APIKey --> APIGenerate
    PostgresURL -.->|"Optional"| APIShare
    
    NextDev --> APIGenerate
    NextDev --> APIShare
```

**Sources:** [package.json:1-43](), [README.md:21-63](), [.env.example]()

## Setup Process Flow

The following sequence diagram shows the exact commands and file operations required to set up OpenAI.fm:

```mermaid
sequenceDiagram
    participant User
    participant Shell as "Terminal Shell"
    participant Git
    participant FileSystem as "File System"
    participant NPM as "npm"
    participant NextJS as "Next.js Server"
    
    User->>Shell: git clone https://github.com/openai/openai-fm.git
    Shell->>Git: Clone repository
    Git->>FileSystem: Create project directory
    FileSystem-->>Shell: Repository cloned
    
    User->>Shell: cd openai-fm
    
    Note over User,FileSystem: Configure Environment Variables
    
    User->>Shell: Create .env file
    Shell->>FileSystem: Copy .env.example to .env
    User->>FileSystem: Edit .env<br/>Set OPENAI_API_KEY=sk-...
    User->>FileSystem: (Optional) Set POSTGRES_URL
    
    Note over User,NPM: Install Dependencies
    
    User->>Shell: npm install
    Shell->>NPM: Read package.json
    NPM->>FileSystem: Read package-lock.json
    NPM->>NPM: Install dependencies<br/>to node_modules/
    NPM-->>Shell: Dependencies installed
    
    Note over User,NextJS: Start Development Server
    
    User->>Shell: npm run dev
    Shell->>NPM: Execute dev script
    NPM->>NextJS: next dev --turbopack
    NextJS->>FileSystem: Load .env file
    NextJS->>NextJS: Start server on port 3000
    NextJS-->>Shell: Server ready at http://localhost:3000
    
    User->>NextJS: Open browser to localhost:3000
    NextJS-->>User: Application loaded
```

**Sources:** [package.json:5-9](), [README.md:21-63]()

## Core Setup Commands

The following table provides the essential commands referenced in [package.json:5-9]():

| Command | Script Definition | Purpose |
|---------|------------------|---------|
| `npm run dev` | `next dev --turbopack` | Starts development server with Turbopack bundler |
| `npm run build` | `next build` | Creates production build in `.next/` directory |
| `npm start` | `next start` | Runs production server from build output |
| `npm run lint` | `next lint` | Runs ESLint to check code quality |

The `dev` script uses the `--turbopack` flag, which enables Next.js's Turbopack bundler for faster development builds.

**Sources:** [package.json:5-9]()

## Environment Variables Configuration

Two environment variables are used by the application:

| Variable | Required | Used By | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | [src/app/api/generate/route.ts]() | Authenticates requests to OpenAI Speech API |
| `POSTGRES_URL` | No | [src/app/api/share/route.ts]() | Connects to PostgreSQL for share persistence |

### Configuration Methods

You can configure environment variables using either method:

1. **Local .env file** (recommended for development):
   - Copy [.env.example]() to `.env` or `.env.local`
   - Add your API key: `OPENAI_API_KEY=sk-...`
   - Optionally add: `POSTGRES_URL=postgresql://...`

2. **System environment variables** (global):
   - Set `OPENAI_API_KEY` in your shell profile
   - See [README.md:31]() for platform-specific instructions

Next.js automatically loads variables from `.env.local` and `.env` files at startup. For detailed environment configuration, see [Environment Configuration](#2.2).

**Sources:** [README.md:27-56](), [.env.example]()

## Dependency Installation

The application's dependencies are defined in [package.json:11-42]() and locked to specific versions in [package-lock.json](). Running `npm install` performs the following:

1. Reads dependency definitions from `package.json`
2. Resolves exact versions from `package-lock.json`
3. Downloads packages to `node_modules/`
4. Links binary scripts (e.g., `next`, `eslint`)

### Key Dependencies

| Category | Packages | Purpose |
|----------|----------|---------|
| **Framework** | `next`, `react`, `react-dom` | Next.js application framework |
| **State Management** | `zustand`, `immer` | Global state store |
| **UI Components** | `@radix-ui/*` | Accessible UI primitives |
| **Code Editor** | `@codemirror/*`, `@uiw/react-codemirror` | Syntax-highlighted code display |
| **Audio** | `wavesurfer.js` | Audio waveform visualization |
| **Database** | `@vercel/postgres` | PostgreSQL client (optional) |
| **Styling** | `tailwindcss`, `@tailwindcss/postcss` | Utility-first CSS framework |
| **Build Tools** | `typescript`, `eslint` | Type checking and linting |

For a comprehensive reference of all dependencies, see [Dependencies Reference](#7).

**Sources:** [package.json:11-42]()

## Verifying Your Setup

After completing the setup, verify that the application is running correctly:

### Development Server Check

1. Start the development server: `npm run dev`
2. Look for console output: `Ready started server on 0.0.0.0:3000, url: http://localhost:3000`
3. Open `http://localhost:3000` in your browser
4. You should see the OpenAI.fm interface

### API Integration Check

1. Enter text in the input field
2. Click the **Play** button
3. Audio should be generated and play back
4. If you see an error, verify:
   - `OPENAI_API_KEY` is set correctly in `.env`
   - The API key is valid and has credits
   - Console shows any error messages from [src/app/api/generate/route.ts]()

### Optional: Share Feature Check

If you configured `POSTGRES_URL`:

1. Click the **Share** button
2. A share URL should be copied to clipboard
3. Opening the share URL should load your configuration
4. If this fails, verify:
   - `POSTGRES_URL` is set correctly
   - Database is accessible
   - The `shares` table exists (see [Database Integration](#3.6))

**Sources:** [README.md:57-63]()

## Architecture Context

Understanding what you just set up helps navigate the codebase. The following diagram maps the setup to runtime architecture:

```mermaid
graph TB
    subgraph "What You Set Up"
        Env[".env file<br/>OPENAI_API_KEY<br/>POSTGRES_URL"]
        Deps["node_modules/<br/>43 dependencies"]
        NextServer["next dev --turbopack<br/>localhost:3000"]
    end
    
    subgraph "Runtime Architecture"
        Browser["Client Browser"]
        AppServer["Next.js App Server"]
        Routes["API Routes"]
        External["External Services"]
    end
    
    subgraph "API Routes Details"
        GenerateRoute["/api/generate<br/>src/app/api/generate/route.ts"]
        ShareRoute["/api/share<br/>src/app/api/share/route.ts"]
    end
    
    subgraph "External Services"
        OpenAIAPI["OpenAI Speech API<br/>Requires OPENAI_API_KEY"]
        PostgresDB["PostgreSQL<br/>Requires POSTGRES_URL"]
    end
    
    NextServer --> Browser
    NextServer --> AppServer
    NextServer --> Routes
    
    Env -.->|"Loaded by"| NextServer
    Deps -.->|"Required by"| NextServer
    
    Routes --> GenerateRoute
    Routes --> ShareRoute
    
    GenerateRoute -->|"Authenticates with"| OpenAIAPI
    ShareRoute -->|"Queries"| PostgresDB
    
    Env -->|"Provides"| OpenAIAPI
    Env -.->|"Optional"| PostgresDB
```

**Sources:** [package.json:1-43](), [README.md:1-91](), [src/app/api/generate/route.ts](), [src/app/api/share/route.ts]()

The development server you started (`next dev --turbopack`) runs:

- **Client-side code**: React components in `src/components/` and `src/app/`
- **API routes**: Server-side endpoints in `src/app/api/`
- **Static assets**: Files from `public/` directory

For detailed architecture information, see [System Architecture](#3).

## Next Steps

After completing setup, you can:

1. **Explore the application**:
   - Try different voices and prompts
   - Test audio playback and download
   - Generate code snippets for API integration

2. **Review the architecture**:
   - See [System Architecture](#3) for component relationships
   - See [Frontend Components](#3.2) for UI component documentation
   - See [API Routes](#3.3) for server-side endpoint details

3. **Start development**:
   - See [Development Guide](#4) for tooling and workflows
   - See [Code Style and Linting](#4.1) for code standards
   - See [Build Process](#4.2) for production builds

4. **Configure optional features**:
   - See [Database Integration](#3.6) to enable sharing
   - See [Environment Configuration](#2.2) for advanced setup

**Sources:** [README.md:1-91]()

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Port 3000 already in use | Another process is using the port | Stop the other process or use `PORT=3001 npm run dev` |
| API key error | Missing or invalid `OPENAI_API_KEY` | Verify `.env` file contains valid key |
| Module not found | Dependencies not installed | Run `npm install` |
| Share feature fails | Missing `POSTGRES_URL` | Add PostgreSQL configuration or disable sharing |

For detailed troubleshooting, see [Installation and Setup](#2.1) and [Environment Configuration](#2.2).

**Sources:** [README.md:14-66]()

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



This document provides detailed instructions for installing dependencies, understanding the package management configuration, and running the OpenAI.fm application locally. It covers prerequisite software requirements, the installation workflow, and verification steps to ensure the application is properly configured.

For environment variable configuration (API keys and database connection strings), see [Environment Configuration](#2.2). For details on the build process and production optimizations, see [Build Process](#4.2).

---

## Prerequisites

OpenAI.fm is built on Next.js 15.3.6 and requires the following software to be installed on your system:

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| Node.js | 18.18.0+ | JavaScript runtime for Next.js |
| npm | 9.0.0+ | Package manager (included with Node.js) |
| Git | Any recent version | Version control (for cloning repository) |

**Verification Commands:**

```bash
node --version  # Should output v18.18.0 or higher
npm --version   # Should output 9.0.0 or higher
```

Sources: [package-lock.json:1-42](), [package.json:1-43](), README.md mentions Node.js requirement implicitly through Next.js

---

## Installation Workflow

The following diagram illustrates the complete installation process, mapping user actions to specific files and commands:

```mermaid
flowchart TD
    Clone["git clone<br/>openai/openai-fm"] --> CheckNode["Verify Node.js<br/>version ≥18.18.0"]
    CheckNode --> NPMInstall["npm install"]
    NPMInstall --> ReadPackage["Read package.json<br/>lines 11-30"]
    ReadPackage --> ResolveDeps["Resolve dependencies<br/>using package-lock.json"]
    ResolveDeps --> InstallProd["Install production deps<br/>29 packages"]
    ResolveDeps --> InstallDev["Install devDependencies<br/>8 packages"]
    InstallProd --> CreateNodeModules["Populate node_modules/<br/>directory"]
    InstallDev --> CreateNodeModules
    CreateNodeModules --> Verify["Verify installation<br/>npm list --depth=0"]
    Verify --> Ready["Ready to configure<br/>environment variables"]
    
    style Clone fill:#e1f5ff
    style NPMInstall fill:#fff3cd
    style CreateNodeModules fill:#d4edda
```

**Installation Process: From Repository Clone to Configured Application**

Sources: [package.json:1-43](), [package-lock.json:1-42](), [README.md:21-44]()

---

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/openai/openai-fm.git
cd openai-fm
```

This creates a local copy of the repository including all source files and configuration.

Sources: [README.md:21-25]()

### 2. Install Dependencies

Execute the following command in the project root directory:

```bash
npm install
```

This command performs the following operations:

1. Reads dependency specifications from [package.json:11-41]()
2. Uses [package-lock.json:1-42]() to resolve exact versions
3. Downloads and installs all packages into `node_modules/`
4. Generates or updates `package-lock.json` if needed

**What Gets Installed:**

The installation process downloads 37 direct dependencies (29 production + 8 development):

| Category | Count | Key Examples |
|----------|-------|--------------|
| Production | 29 | `next`, `react`, `react-dom`, `zustand`, `@vercel/postgres` |
| Development | 8 | `typescript`, `eslint`, `tailwindcss`, `@types/react` |

Sources: [package.json:11-41](), [package-lock.json:7-42]()

### 3. Dependency Resolution Details

```mermaid
graph TB
    subgraph "package.json"
        PJ_Deps["dependencies<br/>lines 11-30"]
        PJ_DevDeps["devDependencies<br/>lines 32-41"]
    end
    
    subgraph "package-lock.json"
        Lock["lockfileVersion: 3<br/>line 4"]
        Packages["packages section<br/>lines 6-end"]
    end
    
    subgraph "Installed Modules"
        Next["next@15.3.6<br/>SSR framework"]
        React["react@19.0.0<br/>UI library"]
        Zustand["zustand@5.0.3<br/>state management"]
        Postgres["@vercel/postgres@0.10.0<br/>database client"]
        Radix["@radix-ui/*<br/>UI primitives"]
        CodeMirror["@codemirror/*<br/>code editor"]
        TS["typescript@5.x<br/>type checking"]
        TW["tailwindcss@4.x<br/>styling"]
        ESLint["eslint@9.x<br/>linting"]
    end
    
    PJ_Deps --> Lock
    PJ_DevDeps --> Lock
    Lock --> Packages
    Packages --> Next
    Packages --> React
    Packages --> Zustand
    Packages --> Postgres
    Packages --> Radix
    Packages --> CodeMirror
    Packages --> TS
    Packages --> TW
    Packages --> ESLint
```

**Dependency Resolution: package.json to node_modules/**

Sources: [package.json:11-41](), [package-lock.json:1-42]()

---

## Understanding package.json Scripts

The [package.json:5-9]() file defines four npm scripts that control the application lifecycle:

### Available Scripts

| Script | Command | Purpose | When to Use |
|--------|---------|---------|-------------|
| `dev` | `next dev --turbopack` | Start development server with Turbopack | Local development |
| `build` | `next build` | Create production build | Before deployment |
| `start` | `next start` | Run production server | After building |
| `lint` | `next lint` | Run ESLint checks | Code quality verification |

### Script Details

**`npm run dev`**

Starts the Next.js development server with Turbopack (Next.js's Rust-based bundler):

```bash
npm run dev
# Executes: next dev --turbopack
# Server starts at: http://localhost:3000
# Features: Hot Module Replacement, Fast Refresh, instant feedback
```

The `--turbopack` flag enables faster build times during development compared to Webpack.

**`npm run build`**

Creates an optimized production build:

```bash
npm run build
# Executes: next build
# Output directory: .next/
# Optimizations: Minification, tree shaking, code splitting
```

This command must complete successfully before running `npm start`.

**`npm run start`**

Runs the production server:

```bash
npm run start
# Executes: next start
# Requires: Completed build in .next/
# Port: 3000 (default)
```

**`npm run lint`**

Runs ESLint with Next.js configuration:

```bash
npm run lint
# Executes: next lint
# Config: eslint.config.mjs
# Checks: All .ts, .tsx files in src/
```

Sources: [package.json:5-9]()

---

## Running the Application

### Development Mode

To run the application in development mode:

```bash
npm run dev
```

Expected output:

```
▲ Next.js 15.3.6
- Local:        http://localhost:3000
- Turbopack:    Enabled

✓ Ready in 1.2s
```

The application will be available at `http://localhost:3000`. The development server provides:

- **Hot Module Replacement (HMR)**: Changes to source files are reflected immediately
- **Fast Refresh**: React components update without losing state
- **Error Overlay**: Compilation errors displayed in browser
- **Turbopack**: Faster bundling than traditional Webpack

### Production Mode

For production deployment, execute:

```bash
npm run build
npm run start
```

The build process generates optimized bundles in `.next/` directory. The production server does not include development features like HMR.

Sources: [package.json:6-8](), [README.md:57-63]()

---

## Verification Steps

After installation, verify the setup:

### 1. Check Installed Packages

```bash
npm list --depth=0
```

Expected output should show all packages from [package.json:11-41]() without errors.

### 2. Verify TypeScript Configuration

```bash
npx tsc --noEmit
```

This checks for TypeScript compilation errors without generating output files.

### 3. Run Linter

```bash
npm run lint
```

Should complete without errors or warnings on a fresh installation.

### 4. Test Development Server

```bash
npm run dev
```

Navigate to `http://localhost:3000`. You should see the OpenAI.fm interface (though it will not be fully functional without environment variables configured - see [Environment Configuration](#2.2)).

Sources: [package.json:5-9]()

---

## Troubleshooting Common Issues

### Node Version Mismatch

**Symptom:** Error mentioning "engines" or unsupported Node version

**Solution:** Upgrade Node.js to version 18.18.0 or higher. Many dependencies require this minimum version as specified in [package-lock.json:49-50](), [package-lock.json:284-285]().

### Package Installation Failures

**Symptom:** `npm install` fails with ERESOLVE errors

**Solution:**

```bash
# Clear npm cache
npm cache clean --force

# Remove existing node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Port 3000 Already in Use

**Symptom:** `EADDRINUSE: address already in use :::3000`

**Solution:** Specify a different port:

```bash
PORT=3001 npm run dev
```

### Turbopack Errors

**Symptom:** Errors related to Turbopack during `npm run dev`

**Solution:** Fall back to Webpack:

```bash
# Modify package.json line 6 to remove --turbopack
"dev": "next dev"
```

Or run directly:

```bash
next dev
```

Sources: [package.json:6]()

---

## Post-Installation Next Steps

After successful installation:

1. **Configure Environment Variables** - Set up `OPENAI_API_KEY` and optional database connection (see [Environment Configuration](#2.2))
2. **Review Build Configuration** - Understand Next.js, TailwindCSS, and TypeScript settings (see [Build Process](#4.2))
3. **Explore Dependencies** - Review the complete dependency tree and their purposes (see [Dependencies Reference](#7))

The application is now installed but requires environment configuration before it can generate audio or persist shared configurations.

Sources: [README.md:27-56](), [package.json:1-43]()

---

## Key File References

The following files govern the installation process:

| File | Lines | Purpose |
|------|-------|---------|
| `package.json` | [5-9]() | npm script definitions |
| `package.json` | [11-30]() | Production dependency specifications |
| `package.json` | [32-41]() | Development dependency specifications |
| `package-lock.json` | [1-42]() | Locked dependency versions and integrity hashes |
| `README.md` | [38-44]() | Installation instructions |

Sources: [package.json:1-43](), [package-lock.json:1-42](), [README.md:38-63]()

---

# Page: Environment Configuration

# Environment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)

</details>



## Purpose and Scope

This document explains the environment variable configuration system for OpenAI.fm, including required and optional variables, configuration files, and how these variables are consumed by the application at runtime. For information about installing dependencies and running the application, see [Installation and Setup](#2.1). For details on how API routes use these environment variables to integrate with external services, see [API Routes](#3.3) and [Database Integration](#3.6).

---

## Environment Variables Overview

OpenAI.fm uses environment variables to configure external service integrations. The application requires one mandatory variable (`OPENAI_API_KEY`) and supports optional PostgreSQL configuration variables for the sharing feature.

### Variable Categories

| Category | Required | Variables | Purpose |
|----------|----------|-----------|---------|
| OpenAI API | Yes | `OPENAI_API_KEY` | Authenticates requests to OpenAI Speech API |
| PostgreSQL | No | `POSTGRES_URL`, `POSTGRES_PRISMA_URL`, `POSTGRES_URL_NO_SSL`, `POSTGRES_URL_NON_POOLING`, `POSTGRES_USER`, `POSTGRES_HOST`, `POSTGRES_PASSWORD`, `POSTGRES_DATABASE` | Enables share persistence feature |

**Sources:** [.env.example:1-8](), [README.md:27-55]()

---

## Configuration File Structure

The application follows the standard Next.js environment variable pattern using `.env` files that are loaded automatically by the framework.

```mermaid
graph LR
    subgraph "Version Control"
        EnvExample[".env.example<br/>Template (committed)"]
        Gitignore[".gitignore<br/>(excludes .env*)"]
    end
    
    subgraph "Local Development"
        EnvLocal[".env.local<br/>Actual secrets (not committed)"]
        EnvDevelopment[".env.development<br/>Optional overrides"]
    end
    
    subgraph "Next.js Runtime"
        ProcessEnv["process.env<br/>Runtime environment"]
    end
    
    subgraph "Application Code"
        APIGenerate["/api/generate<br/>Consumes OPENAI_API_KEY"]
        APIShare["/api/share<br/>Consumes POSTGRES_URL"]
    end
    
    EnvExample -.->|"Template for"| EnvLocal
    EnvExample -.->|"Documents format"| EnvDevelopment
    Gitignore -->|"Excludes"| EnvLocal
    Gitignore -->|"Excludes"| EnvDevelopment
    
    EnvLocal -->|"Loaded by Next.js"| ProcessEnv
    EnvDevelopment -->|"Loaded by Next.js"| ProcessEnv
    
    ProcessEnv -->|"process.env.OPENAI_API_KEY"| APIGenerate
    ProcessEnv -->|"process.env.POSTGRES_URL"| APIShare
```

**Diagram: Environment Variable Loading Flow**

The `.env.example` file serves as documentation and a template, showing the expected format and structure of required variables. Developers copy this to `.env.local` and populate it with actual secrets. Next.js automatically loads `.env.local` at runtime and makes variables available via `process.env`.

**Sources:** [.env.example:1-8](), [README.md:32-36](), [README.md:46-55]()

---

## OpenAI API Key Configuration

### Required Variable

The `OPENAI_API_KEY` environment variable is mandatory for the application to function. This key authenticates requests to the OpenAI Speech API endpoint used by the `/api/generate` route.

### Configuration Methods

The README documents two methods for setting the API key:

**Method 1: Global System Environment Variable**

Set the variable globally in your operating system environment. This method is useful for developers who use OpenAI API keys across multiple projects.

**Method 2: Project-Level .env File**

Create a `.env` or `.env.local` file in the project root:

```
OPENAI_API_KEY=<your_api_key>
```

This is the recommended method for project-specific configuration.

**Sources:** [README.md:27-36]()

### Runtime Usage

```mermaid
graph TB
    subgraph "Client Request"
        User["User clicks PlayButton"]
        PlayButton["PlayButton.tsx<br/>Constructs request"]
    end
    
    subgraph "API Route Handler"
        GenerateRoute["/api/generate/route.ts<br/>GET handler"]
        EnvAccess["process.env.OPENAI_API_KEY<br/>Retrieved from environment"]
        Validation["Validate API key exists<br/>Return 500 if missing"]
    end
    
    subgraph "External Service"
        OpenAIEndpoint["OpenAI API<br/>POST /v1/audio/speech<br/>Authorization: Bearer {key}"]
    end
    
    User --> PlayButton
    PlayButton -->|"GET /api/generate?input=..."| GenerateRoute
    GenerateRoute --> EnvAccess
    EnvAccess --> Validation
    Validation -->|"Include in Authorization header"| OpenAIEndpoint
    OpenAIEndpoint -.->|"Audio stream response"| GenerateRoute
    GenerateRoute -.->|"Proxied response"| PlayButton
```

**Diagram: OPENAI_API_KEY Usage Flow**

The API route at `src/app/api/generate/route.ts` accesses `process.env.OPENAI_API_KEY` to authenticate requests to OpenAI's Speech API. If the key is missing, the route returns a 500 error.

**Sources:** [README.md:16-36]()

---

## PostgreSQL Configuration (Optional)

### Overview

PostgreSQL configuration is optional and only required for the sharing feature. Without database configuration, the application functions normally but the ShareButton feature is disabled.

### Connection String Variables

The `.env.example` file documents eight PostgreSQL-related variables:

| Variable | Purpose | Required For |
|----------|---------|-------------|
| `POSTGRES_URL` | Standard PostgreSQL connection string | General database operations |
| `POSTGRES_PRISMA_URL` | Connection string optimized for Prisma with PgBouncer | ORM operations with connection pooling |
| `POSTGRES_URL_NO_SSL` | Connection string without SSL | Development environments |
| `POSTGRES_URL_NON_POOLING` | Direct connection without pooling | Migrations and admin tasks |
| `POSTGRES_USER` | Database username | Manual connection configuration |
| `POSTGRES_HOST` | Database host address | Manual connection configuration |
| `POSTGRES_PASSWORD` | Database password | Manual connection configuration |
| `POSTGRES_DATABASE` | Database name | Manual connection configuration |

**Sources:** [.env.example:1-8]()

### Connection String Format

The `.env.example` file shows the expected format for connection strings:

```
POSTGRES_URL="<CONNECTION_STRING>?sslmode=require"
```

Key components:
- `sslmode=require`: Enforces SSL/TLS encryption for connections
- `pgbouncer=true`: Indicates PgBouncer connection pooling (for `POSTGRES_PRISMA_URL`)
- `connect_timeout=15`: Sets connection timeout in seconds

**Sources:** [.env.example:1-4]()

### Runtime Integration

```mermaid
graph TB
    subgraph "Client Action"
        ShareButton["ShareButton.tsx<br/>User clicks Share"]
    end
    
    subgraph "API Route: /api/share"
        ShareRoute["route.ts<br/>POST/GET handlers"]
        PostgresEnv["process.env.POSTGRES_URL<br/>Retrieved at runtime"]
        DBConnection["Database client<br/>connection"]
        SharesTable["shares table<br/>INSERT/SELECT operations"]
    end
    
    subgraph "External Database"
        VercelPostgres["Vercel PostgreSQL<br/>or other hosted DB"]
    end
    
    subgraph "Fallback Behavior"
        NoDatabase["POSTGRES_URL undefined"]
        ErrorResponse["Return error response<br/>Share feature disabled"]
    end
    
    ShareButton -->|"POST /api/share<br/>{input, prompt, voice}"| ShareRoute
    ShareRoute --> PostgresEnv
    PostgresEnv -->|"If defined"| DBConnection
    PostgresEnv -->|"If undefined"| NoDatabase
    DBConnection --> SharesTable
    SharesTable -->|"SQL queries"| VercelPostgres
    NoDatabase --> ErrorResponse
    ErrorResponse -.-> ShareButton
    VercelPostgres -.->|"Query results"| SharesTable
    SharesTable -.-> ShareRoute
    ShareRoute -.->|"{id: hash}"| ShareButton
```

**Diagram: PostgreSQL Environment Variable Usage**

The `/api/share` route accesses `process.env.POSTGRES_URL` to establish a database connection. If the variable is undefined, the sharing feature fails gracefully with an error response.

**Sources:** [README.md:46-55](), [.env.example:1-8]()

---

## Environment Variable Loading Mechanism

### Next.js Built-in Support

Next.js automatically loads environment variables from `.env` files in the following priority order (highest to lowest):

1. `.env.local` - Local overrides, not committed to version control
2. `.env.development` - Development-specific variables (when `NODE_ENV=development`)
3. `.env.production` - Production-specific variables (when `NODE_ENV=production`)
4. `.env` - Default values for all environments

### Server-Side Only Access

All environment variables in OpenAI.fm are server-side only. They are accessed via `process.env` in API routes and are never exposed to the client browser. This is critical for security as both `OPENAI_API_KEY` and `POSTGRES_URL` contain sensitive credentials.

### Variable Prefix Convention

Next.js distinguishes between server-side and client-side environment variables:
- **Server-side only**: Any variable (e.g., `OPENAI_API_KEY`, `POSTGRES_URL`)
- **Client-side exposed**: Variables prefixed with `NEXT_PUBLIC_` (not used in this application)

Since OpenAI.fm does not use any `NEXT_PUBLIC_` prefixed variables, all configuration is server-side only.

**Sources:** [README.md:27-55]()

---

## Configuration Validation

### Missing API Key Handling

The application expects `OPENAI_API_KEY` to be present. The `/api/generate` route should validate the presence of this variable and return an appropriate error response if missing.

### Missing Database Configuration

The application gracefully handles missing PostgreSQL configuration. When `POSTGRES_URL` is undefined, the `/api/share` route returns an error, but other features remain functional.

### Deployment Considerations

When deploying to production (e.g., Vercel), environment variables must be configured in the hosting platform's dashboard rather than using `.env` files:

1. **Vercel Dashboard**: Project Settings → Environment Variables
2. **Production vs Preview**: Set variables for Production, Preview, and Development environments separately
3. **API Key Security**: Ensure `OPENAI_API_KEY` is marked as sensitive to prevent it from appearing in build logs

**Sources:** [README.md:65-66]()

---

## Configuration Examples

### Minimal Configuration (Required Only)

For basic functionality without sharing:

```
OPENAI_API_KEY=sk-proj-...your-key-here...
```

### Full Configuration (All Features)

For complete functionality including sharing:

```
OPENAI_API_KEY=sk-proj-...your-key-here...
POSTGRES_URL="postgresql://user:password@host.region.provider.com:5432/database?sslmode=require"
POSTGRES_PRISMA_URL="postgresql://user:password@host.region.provider.com:5432/database?sslmode=require&pgbouncer=true&connect_timeout=15"
POSTGRES_URL_NO_SSL="postgresql://user:password@host.region.provider.com:5432/database"
POSTGRES_URL_NON_POOLING="postgresql://user:password@host.region.provider.com:5432/database?sslmode=require"
POSTGRES_USER="user"
POSTGRES_HOST="host.region.provider.com"
POSTGRES_PASSWORD="password"
POSTGRES_DATABASE="database"
```

**Sources:** [.env.example:1-8](), [README.md:32-55]()

---

## Security Best Practices

### Version Control Exclusion

The `.gitignore` file ensures that `.env`, `.env.local`, `.env.development`, and `.env.production` files are never committed to version control. Only `.env.example` should be committed as it contains no actual secrets.

### API Key Protection

- Never commit actual API keys to version control
- Rotate API keys if they are accidentally exposed
- Use project-specific API keys rather than personal keys for shared projects
- Monitor API usage in the OpenAI dashboard to detect unauthorized usage

### Connection String Security

PostgreSQL connection strings contain sensitive credentials (username, password, host). These should be treated with the same security considerations as API keys.

**Sources:** [README.md:65-66](), [.env.example:1-8]()

---

## Relationship to Other Systems

```mermaid
graph TB
    subgraph "Configuration Layer"
        EnvExample[".env.example<br/>Documentation"]
        EnvLocal[".env.local<br/>Actual secrets"]
    end
    
    subgraph "Build & Runtime"
        NextConfig["next.config.ts<br/>Build configuration"]
        NextJS["Next.js Runtime<br/>Loads .env files"]
        ProcessEnv["process.env<br/>Runtime variables"]
    end
    
    subgraph "API Routes"
        GenerateRoute["/api/generate/route.ts<br/>Uses OPENAI_API_KEY"]
        ShareRoute["/api/share/route.ts<br/>Uses POSTGRES_URL"]
    end
    
    subgraph "External Services"
        OpenAI["OpenAI Speech API<br/>Requires authentication"]
        Postgres["PostgreSQL Database<br/>Requires connection"]
    end
    
    EnvExample -.->|"Template"| EnvLocal
    EnvLocal --> NextJS
    NextConfig --> NextJS
    NextJS --> ProcessEnv
    
    ProcessEnv --> GenerateRoute
    ProcessEnv --> ShareRoute
    
    GenerateRoute -->|"Authenticated requests"| OpenAI
    ShareRoute -->|"Database queries"| Postgres
```

**Diagram: Environment Configuration in System Context**

Environment variables connect the configuration layer to runtime API routes, which use these credentials to authenticate with external services. The configuration system integrates with Next.js's built-in environment variable loading mechanism.

**Sources:** [.env.example:1-8](), [README.md:27-55]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next.config.ts](next.config.ts)
- [package.json](package.json)

</details>



This document provides a comprehensive overview of the OpenAI.fm system architecture, including component relationships, data flow patterns, and integration points. The architecture follows a standard Next.js application pattern with server-side rendering, API routes, and client-side state management.

The system consists of five primary layers:
1. **Client Layer**: React components, Zustand state management, Service Worker caching
2. **Next.js Server Layer**: Page rendering, API routes, middleware
3. **External APIs**: OpenAI Speech API for text-to-speech generation
4. **Data Persistence**: Optional PostgreSQL database for sharing functionality
5. **Build System**: Next.js with Turbopack/Webpack, TailwindCSS, TypeScript

For detailed information on specific subsystems, see:
- **Section 3.1**: Next.js Application Structure
- **Section 3.2**: Frontend Components
- **Section 3.3**: API Routes
- **Section 3.4**: State Management
- **Section 3.5**: Audio Processing
- **Section 3.6**: Database Integration

## High-Level System Architecture

The following diagram shows the complete system architecture with specific code entities and their relationships:

**Diagram: Complete System Architecture with Code Entities**

```mermaid
graph TB
    subgraph ClientBrowser["Client Browser"]
        ServiceWorker["Service Worker<br/>public/worker-*.js<br/>Audio Caching"]
        ReactUI["React UI Components<br/>src/components/*.tsx"]
        AppStore["appStore<br/>src/lib/appStore.ts<br/>Zustand State"]
    end
    
    subgraph NextJsServer["Next.js Application Server"]
        RootLayout["RootLayout<br/>src/app/layout.tsx"]
        Page["Page<br/>src/app/page.tsx"]
        APIGenerate["API: /api/generate<br/>src/app/api/generate/route.ts"]
        APIShare["API: /api/share<br/>src/app/api/share/route.ts"]
        Middleware["Middleware<br/>src/app/tmp.middleware.ts"]
    end
    
    subgraph ExternalServices["External Services"]
        OpenAIAPI["OpenAI Speech API<br/>api.openai.com/v1/audio/speech"]
        PostgresDB["PostgreSQL<br/>Vercel Postgres"]
    end
    
    ReactUI -->|"Read/Write State"| AppStore
    ReactUI -->|"Fetch"| APIGenerate
    ReactUI -->|"POST/GET"| APIShare
    ServiceWorker -->|"Cache Audio"| ReactUI
    
    RootLayout -->|"Renders"| Page
    Page -->|"Dynamic Import"| ReactUI
    Middleware -->|"CSP Headers"| RootLayout
    
    APIGenerate -->|"POST /v1/audio/speech"| OpenAIAPI
    APIShare -->|"SQL Query"| PostgresDB
    
    style AppStore fill:#f9f9f9
    style OpenAIAPI fill:#f9f9f9
    style PostgresDB fill:#f9f9f9
```

Sources: [src/app/layout.tsx:1-30](), [src/app/page.tsx:1-20](), [src/app/api/generate/route.ts:1-100](), [src/app/api/share/route.ts:1-100](), [package.json:11-30]()

## Application Layer Architecture

The application is organized into distinct layers, each with specific responsibilities and interfaces.

**Diagram: Application Layers and Key Files**

```mermaid
graph TD
    subgraph PresentationLayer["Presentation Layer"]
        ClientDynamicTTS["ClientDynamicTTS<br/>src/components/ClientDynamicTTS.tsx<br/>Dynamic Import Boundary"]
        PlayButton["PlayButton<br/>src/components/PlayButton.tsx"]
        DownloadButton["DownloadButton<br/>src/components/DownloadButton.tsx"]
        ShareButton["ShareButton<br/>src/components/ShareButton.tsx"]
        CodeCopyButton["CodeCopyButton<br/>src/components/CodeCopyButton.tsx"]
        PlayingWaveform["PlayingWaveform<br/>src/components/PlayingWaveform.tsx"]
    end
    
    subgraph StateLayer["State Management Layer"]
        appStore["appStore<br/>src/lib/appStore.ts<br/>Zustand Store"]
    end
    
    subgraph ServerLayer["Server Layer"]
        generateRoute["GET /api/generate<br/>src/app/api/generate/route.ts"]
        shareRoute["POST/GET /api/share<br/>src/app/api/share/route.ts"]
    end
    
    subgraph UtilityLayer["Utility Layer"]
        copyText["copyText()<br/>src/lib/copyText.ts"]
        getCodeSnippet["getCodeSnippet()<br/>src/lib/getCodeSnippet.ts"]
    end
    
    PlayButton --> appStore
    DownloadButton --> appStore
    ShareButton --> appStore
    CodeCopyButton --> appStore
    
    PlayButton --> generateRoute
    ShareButton --> shareRoute
    
    ShareButton --> copyText
    CodeCopyButton --> copyText
    CodeCopyButton --> getCodeSnippet
    
    PlayButton --> PlayingWaveform
```

| Layer | Responsibilities | Key Files |
|-------|-----------------|-----------|
| Presentation | User interaction, rendering, visual feedback | `src/components/*.tsx` |
| State Management | Global application state (input, voice, prompt) | `src/lib/appStore.ts` |
| Server | API endpoints, OpenAI proxy, data persistence | `src/app/api/*/route.ts` |
| Utility | Shared functions (clipboard, code generation) | `src/lib/*.ts` |

Sources: [src/components/PlayButton.tsx:1-200](), [src/components/ShareButton.tsx:1-150](), [src/lib/appStore.ts:1-50](), [src/app/api/generate/route.ts:1-100](), [src/app/api/share/route.ts:1-100]()

## Component Hierarchy and Relationships

The component hierarchy follows Next.js conventions with server-side rendering at the root and client-side components for interactive features.

**Diagram: Component Hierarchy from Root to Leaves**

```mermaid
graph TD
    RootLayout["RootLayout<br/>src/app/layout.tsx<br/>Server Component"]
    Page["Page<br/>src/app/page.tsx<br/>Server Component"]
    ClientDynamicTTS["ClientDynamicTTS<br/>src/components/ClientDynamicTTS.tsx<br/>'use client' + dynamic()"]
    
    TTSInterface["TTS Interface Component<br/>Inferred from dynamic import"]
    
    PlayButton["PlayButton<br/>src/components/PlayButton.tsx<br/>'use client'"]
    DownloadButton["DownloadButton<br/>src/components/DownloadButton.tsx<br/>'use client'"]
    ShareButton["ShareButton<br/>src/components/ShareButton.tsx<br/>'use client'"]
    CodeCopyButton["CodeCopyButton<br/>src/components/CodeCopyButton.tsx<br/>'use client'"]
    
    ShareDialog["ShareDialog<br/>src/components/ShareDialog.tsx<br/>Radix UI Dialog"]
    PlayingWaveform["PlayingWaveform<br/>src/components/PlayingWaveform.tsx<br/>Canvas-based visualization"]
    
    RootLayout --> Page
    Page -->|"dynamic import"| ClientDynamicTTS
    ClientDynamicTTS -.->|"ssr: false"| TTSInterface
    
    TTSInterface --> PlayButton
    TTSInterface --> DownloadButton
    TTSInterface --> ShareButton
    TTSInterface --> CodeCopyButton
    
    ShareButton --> ShareDialog
    PlayButton --> PlayingWaveform
```

The dynamic import in `ClientDynamicTTS` prevents server-side rendering of client-only components that depend on browser APIs (Web Audio API, `navigator.clipboard`).

Sources: [src/app/layout.tsx:1-30](), [src/app/page.tsx:1-20](), [src/components/ClientDynamicTTS.tsx:1-10](), [src/components/PlayButton.tsx:1-200](), [src/components/ShareButton.tsx:1-150]()

## Primary Data Flows

### Audio Generation and Playback Flow

This is the core functionality of the application, involving multiple systems coordinating to generate and play audio.

**Diagram: Audio Generation Flow with Code References**

```mermaid
sequenceDiagram
    participant User
    participant PlayButton as PlayButton<br/>src/components/PlayButton.tsx
    participant appStore as appStore<br/>src/lib/appStore.ts
    participant generateAPI as /api/generate<br/>src/app/api/generate/route.ts
    participant OpenAI as OpenAI API<br/>api.openai.com/v1/audio/speech
    participant AudioContext as Web Audio API<br/>AudioContext, AnalyserNode
    participant ServiceWorker as Service Worker<br/>public/worker-*.js
    
    User->>PlayButton: "Click Play Button"
    PlayButton->>appStore: "getState()"
    appStore-->>PlayButton: "{input, prompt, voice}"
    
    PlayButton->>PlayButton: "generateId()<br/>Construct URL"
    PlayButton->>appStore: "setLatestAudioUrl(url)"
    
    PlayButton->>generateAPI: "GET /api/generate?input=...&prompt=...&voice=..."
    generateAPI->>generateAPI: "Truncate to MAX_LENGTH"
    generateAPI->>OpenAI: "POST /v1/audio/speech<br/>{model: 'gpt-4o-audio-preview', input, voice}"
    OpenAI-->>generateAPI: "Audio Stream (WAV/MP3)"
    generateAPI-->>PlayButton: "Stream Response"
    
    PlayButton->>AudioContext: "createAudioContext()<br/>createAnalyser()"
    AudioContext-->>PlayButton: "AnalyserNode"
    
    PlayButton->>ServiceWorker: "postMessage({type: 'CACHE_AUDIO'})"
    ServiceWorker->>ServiceWorker: "cache.put(url, response)"
    ServiceWorker-->>PlayButton: "postMessage({type: 'ADD_TO_CACHE'})"
    
    PlayButton->>AudioContext: "audio.play()"
    PlayButton->>PlayButton: "updateAmplitudes()"
    PlayButton-->>User: "Audio Playback + Waveform"
```

| Step | Component | Key Functions/Methods |
|------|-----------|----------------------|
| 1. User Input | `PlayButton` | Event handler, `handlePlay()` |
| 2. State Retrieval | `appStore` | Zustand `getState()` |
| 3. API Request | `/api/generate` | `GET` handler, input validation |
| 4. TTS Generation | OpenAI API | Model: `gpt-4o-audio-preview` |
| 5. Audio Analysis | Web Audio API | `AudioContext`, `AnalyserNode` |
| 6. Caching | Service Worker | `cache.put()`, `postMessage()` |
| 7. Playback | `HTMLAudioElement` | `.play()`, waveform updates |

Sources: [src/components/PlayButton.tsx:1-200](), [src/app/api/generate/route.ts:1-100](), [src/lib/appStore.ts:1-50]()

### Share Configuration Flow

The sharing feature allows users to persist and distribute TTS configurations via unique URLs.

**Diagram: Share Flow with Database Integration**

```mermaid
sequenceDiagram
    participant User
    participant ShareButton as ShareButton<br/>src/components/ShareButton.tsx
    participant appStore as appStore<br/>src/lib/appStore.ts
    participant shareAPI as /api/share<br/>src/app/api/share/route.ts
    participant PostgreSQL as PostgreSQL<br/>shares table
    participant copyText as copyText()<br/>src/lib/copyText.ts
    participant ShareDialog as ShareDialog<br/>src/components/ShareDialog.tsx
    
    User->>ShareButton: "Click Share Button"
    ShareButton->>appStore: "getState()"
    appStore-->>ShareButton: "{input, prompt, voice}"
    
    ShareButton->>shareAPI: "POST /api/share<br/>{input, prompt, voice}"
    shareAPI->>shareAPI: "Validate & clip input<br/>Generate UUID"
    shareAPI->>PostgreSQL: "INSERT INTO shares<br/>(id, input, prompt, voice, created_at)"
    PostgreSQL-->>shareAPI: "Success"
    shareAPI-->>ShareButton: "{id: 'abc123'}"
    
    ShareButton->>ShareButton: "Construct URL:<br/>window.location.origin + '#' + id"
    ShareButton->>copyText: "copyText(shareUrl)"
    copyText->>copyText: "navigator.clipboard.writeText()"
    copyText-->>ShareButton: "Success"
    
    ShareButton->>ShareDialog: "setOpen(true)"
    ShareDialog-->>User: "Display share URL"
    
    Note over User,PostgreSQL: Later: Recipient accesses shared URL
    
    User->>shareAPI: "GET /api/share?hash=abc123"
    shareAPI->>PostgreSQL: "SELECT * FROM shares WHERE id = 'abc123'"
    PostgreSQL-->>shareAPI: "{input, prompt, voice}"
    shareAPI-->>User: "Configuration JSON"
```

The `shares` table schema (inferred from API route):

| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR/UUID | Primary key, used in share URL hash |
| `input` | TEXT | User's input text for TTS |
| `prompt` | TEXT | System prompt for voice modification |
| `voice` | VARCHAR | Voice identifier (e.g., 'alloy', 'echo') |
| `created_at` | TIMESTAMP | Record creation timestamp |

Sources: [src/components/ShareButton.tsx:1-150](), [src/app/api/share/route.ts:1-100](), [src/lib/copyText.ts:1-20]()

### State Management Flow

The application uses Zustand for centralized state management, avoiding prop drilling across components.

**Diagram: State Management with appStore**

```mermaid
graph TB
    appStore["appStore<br/>src/lib/appStore.ts<br/>create() from zustand"]
    
    subgraph StateShape["State Shape"]
        input["input: string<br/>User text input"]
        prompt["prompt: string<br/>System prompt"]
        voice["voice: string<br/>Selected voice ID"]
        latestAudioUrl["latestAudioUrl: string<br/>Current audio URL"]
    end
    
    subgraph Consumers["State Consumers"]
        PlayButton["PlayButton<br/>Reads: input, prompt, voice<br/>Writes: latestAudioUrl"]
        DownloadButton["DownloadButton<br/>Reads: latestAudioUrl"]
        ShareButton["ShareButton<br/>Reads: input, prompt, voice"]
        CodeCopyButton["CodeCopyButton<br/>Reads: input, prompt, voice"]
    end
    
    appStore --> StateShape
    StateShape --> Consumers
    
    PlayButton -->|"setState()"| appStore
```

| State Property | Type | Purpose | Consumers |
|----------------|------|---------|-----------|
| `input` | `string` | Text to convert to speech | `PlayButton`, `ShareButton`, `CodeCopyButton` |
| `prompt` | `string` | System prompt for voice styling | `PlayButton`, `ShareButton`, `CodeCopyButton` |
| `voice` | `string` | Voice identifier ('alloy', 'echo', etc.) | `PlayButton`, `ShareButton`, `CodeCopyButton` |
| `latestAudioUrl` | `string` | URL of most recent audio generation | `PlayButton` (write), `DownloadButton` (read) |

Sources: [src/lib/appStore.ts:1-50](), [src/components/PlayButton.tsx:1-200](), [src/components/ShareButton.tsx:1-150](), [src/components/DownloadButton.tsx:1-100]()

## Build and Runtime Configuration

The application uses different configurations for development and production environments.

### Development Environment

```mermaid
flowchart LR
    Dev["npm run dev<br>Command"] -->|Uses| Turbo["Turbopack"]
    Turbo --> NextConfig["next.config.ts"]
    
    subgraph "Configuration"
        EnvFile[".env file"]
        CSPDev["Development CSP"]
    end
    
    NextConfig --> CSPDev
    Dev -->|Reads| EnvFile
    EnvFile -->|Required| OpenAIKey["OPENAI_API_KEY"]
    EnvFile -->|Optional| DBUrl["POSTGRES_URL"]
```

Sources: [next.config.ts:3-16](), [package.json:6](), [README.md:27-36]()

### Production Environment

```mermaid
flowchart LR
    Build["npm run build<br>Command"] -->|Uses| Webpack["Webpack"]
    Start["npm run start<br>Command"] -->|Serves| BuiltApp["Built Application"]
    
    subgraph "Configuration"
        NextConfig["next.config.ts"]
        CSPProd["Production CSP"]
        HSTS["Strict-Transport-Security"]
    end
    
    Webpack --> NextConfig
    NextConfig --> CSPProd
    NextConfig --> HSTS
```

Sources: [next.config.ts:3-54](), [package.json:7-8]()

## Technical Components in Detail

### Next.js Framework

The application is built on Next.js, which provides:

- Server-side rendering capabilities
- API route handling
- Build optimization
- Development tooling with Turbopack

The configuration in `next.config.ts` includes:

| Configuration | Purpose |
|---------------|---------|
| Content Security Policy | Security headers for controlling resource loading |
| SVG transformation | Converts SVG files to React components |
| HSTS headers | Enforces HTTPS in production |
| Turbopack settings | Optimizes development experience |

Sources: [next.config.ts:1-57]()

### OpenAI API Integration

The application connects to the OpenAI Speech API for text-to-speech conversion. Key aspects include:

- API key configuration through environment variables
- Speech model selection
- Audio format handling

Sources: [README.md:7-11]()

### Database Integration (Optional)

The application can optionally connect to a PostgreSQL database to enable the sharing feature:

- Uses the Vercel Postgres client
- Requires configuration via the `POSTGRES_URL` environment variable
- Only affects the sharing functionality; the core application works without it

Sources: [README.md:46-55](), [package.json:20]()

### Audio Visualization

Audio visualization is handled using WaveSurfer.js:

- Provides waveform visualization of audio data
- Allows for playback control
- Integrates with the React component structure

Sources: [package.json:29]()

## Security Considerations

The application implements several security measures in its architecture:

- Content Security Policy (CSP) headers to control resource loading
- Strict Transport Security (HSTS) headers in production
- SVG transformation to prevent XSS vulnerabilities

For more detailed information on security aspects, see [Security Considerations](#5).

Sources: [next.config.ts:5-54]()

## Deployment Architecture

The application is designed to be deployed as a complete Next.js application:

```mermaid
graph TD
    subgraph "Deployment Environment"
        NextServer["Next.js Server"]
        StaticAssets["Static Assets"]
    end
    
    subgraph "External Dependencies"
        OpenAIAPI["OpenAI API"]
        PostgresDB["PostgreSQL Database<br>(Optional)"]
    end
    
    User["User Browser"] --> NextServer
    User --> StaticAssets
    NextServer --> OpenAIAPI
    NextServer -.-> PostgresDB

    classDef optional stroke-dasharray: 5 5;
    class PostgresDB optional
```

Sources: [README.md:14-63]()

This architecture provides a balance of performance, maintainability, and extensibility, allowing the application to effectively demonstrate OpenAI's text-to-speech capabilities while providing a smooth user experience.

---

# Page: Next.js Application Structure

# Next.js Application Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next.config.ts](next.config.ts)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/app/page.tsx](src/app/page.tsx)

</details>



## Purpose and Scope

This document describes the Next.js application structure of OpenAI.fm, focusing on the App Router file organization, root layout configuration, main page component, and Next.js build configuration. This covers the foundational framework that all other application components build upon.

For information about specific UI components rendered within this structure, see [Frontend Components](#3.2). For details on API routing and server-side logic, see [API Routes](#3.3). For build tooling and development workflows, see [Build Process](#4.2).

## App Router Structure

OpenAI.fm uses the Next.js App Router (introduced in Next.js 13+) rather than the legacy Pages Router. The App Router uses file-system based routing with special files defining route segments.

### Directory Layout

```
src/app/
├── layout.tsx          # Root layout component
├── page.tsx            # Main page route ()
├── globals.css         # Global styles
├── tmp.middleware.ts   # Middleware for CSP nonce injection
└── api/
    ├── generate/
    │   └── route.ts    # /api/generate endpoint
    └── share/
        └── route.ts    # /api/share endpoint
```

The `src/app` directory serves as the root of the application routing structure. Each `page.tsx` file creates a route, while `layout.tsx` defines shared UI wrapping all routes at that level.

**Sources:** [src/app/layout.tsx:1-47](), [src/app/page.tsx:1-6]()

### File Naming Conventions

| File Name | Purpose | Rendered |
|-----------|---------|----------|
| `layout.tsx` | Defines UI shared across routes | Always |
| `page.tsx` | Defines unique UI for a route | When route matches |
| `route.ts` | Defines API endpoint handlers | N/A (API) |
| `globals.css` | Global styles imported in layout | Always |

**Sources:** [src/app/layout.tsx:4](), [src/app/page.tsx:1-6]()

## Root Layout Component

The root layout is defined in [src/app/layout.tsx:1-47]() and establishes the HTML document structure, metadata, and global styling for the entire application.

### Component Structure

```mermaid
graph TD
    RootLayout["RootLayout<br/>(src/app/layout.tsx)"]
    HTMLTag["<html lang='en'>"]
    BodyTag["<body>"]
    JetBrainsMono["JetBrains_Mono font<br/>from next/font/google"]
    Metadata["Metadata export<br/>title, description, OG tags"]
    GlobalCSS["globals.css<br/>TailwindCSS imports"]
    Children["children prop<br/>(page content)"]
    
    RootLayout --> Metadata
    RootLayout --> HTMLTag
    HTMLTag --> BodyTag
    BodyTag --> Children
    RootLayout --> JetBrainsMono
    JetBrainsMono --> BodyTag
    RootLayout --> GlobalCSS
    
    style RootLayout fill:#f9f9f9
    style Metadata fill:#f9f9f9
```

**Sources:** [src/app/layout.tsx:1-47]()

### Metadata Configuration

The `metadata` export at [src/app/layout.tsx:12-32]() defines SEO and social media metadata:

| Property | Value | Purpose |
|----------|-------|---------|
| `metadataBase` | `https://www.openai.fm` | Base URL for relative URLs |
| `title` | `"OpenAI.fm"` | Page title |
| `description` | Interactive TTS demo description | SEO description |
| `authors` | `[{ name: "OpenAI" }]` | Author metadata |
| `openGraph.title` | `"OpenAI.fm"` | Open Graph title |
| `openGraph.description` | TTS demo description | Open Graph description |
| `openGraph.images` | `/og-image.png` (1200x630) | Social media preview image |
| `twitter.card` | `"summary_large_image"` | Twitter card type |

The `metadataBase` at [src/app/layout.tsx:13]() ensures that relative paths in metadata (like the Open Graph image) resolve correctly in production.

**Sources:** [src/app/layout.tsx:12-32]()

### Font Configuration

The layout uses the JetBrains Mono font loaded via `next/font/google` at [src/app/layout.tsx:6-10]():

```typescript
const jetBrainsMono = JetBrains_Mono({
  weight: "400",
  subsets: [],
  preload: true,
});
```

This font is applied to the `<body>` element at [src/app/layout.tsx:41]() using the `clsx` utility to combine multiple class names. The `next/font/google` integration automatically optimizes font loading, generating CSS with font-display swap and self-hosting the font files.

**Sources:** [src/app/layout.tsx:6-10](), [src/app/layout.tsx:41]()

### HTML Structure

The root layout returns the following HTML structure [src/app/layout.tsx:39-45]():

```
<html lang="en">
  <body className="antialiased {jetBrainsMono.className}">
    {children}
  </body>
</html>
```

The `antialiased` class applies font smoothing, while `{children}` represents the content from nested routes (in this case, the page component).

**Sources:** [src/app/layout.tsx:39-45]()

## Main Page Component

The main page component is defined in [src/app/page.tsx:1-6]() and represents the root route (`/`) of the application.

```mermaid
graph LR
    PageTSX["page.tsx<br/>default export Page()"]
    ClientDynamicTTS["ClientDynamicTTS<br/>@/components/ClientDynamicTTS"]
    DynamicImport["dynamic() import<br/>client-side only"]
    TTSPage["Actual TTS UI<br/>(client component)"]
    
    PageTSX -->|"imports"| ClientDynamicTTS
    ClientDynamicTTS -->|"uses Next.js dynamic()"| DynamicImport
    DynamicImport -->|"loads at runtime"| TTSPage
    
    style PageTSX fill:#f9f9f9
    style ClientDynamicTTS fill:#f9f9f9
```

**Sources:** [src/app/page.tsx:1-6]()

### Component Implementation

The page component is minimal at [src/app/page.tsx:3-5]():

```typescript
export default function Page() {
  return <ClientDynamicTTS />;
}
```

This simplicity is intentional. The `Page` component itself is a Server Component (the default in App Router), but it immediately renders `ClientDynamicTTS`, which handles the dynamic import of the actual client-side UI. This pattern is necessary because the TTS interface requires browser APIs (Web Audio API, Service Workers) that are not available during server-side rendering.

**Sources:** [src/app/page.tsx:3-5]()

### Import Path Resolution

The import at [src/app/page.tsx:1]() uses the `@/` path alias:

```typescript
import ClientDynamicTTS from "@/components/ClientDynamicTTS";
```

This alias is configured in `tsconfig.json` to map `@/*` to `src/*`, enabling absolute imports and avoiding relative path complexity.

**Sources:** [src/app/page.tsx:1]()

## Next.js Configuration

The [next.config.ts:1-58]() file configures the Next.js build system, bundler behavior, SVG handling, and HTTP headers.

### Configuration Structure

```mermaid
graph TD
    NextConfig["nextConfig object<br/>(next.config.ts)"]
    Turbopack["turbopack rules<br/>Development bundler"]
    Webpack["webpack() function<br/>Production bundler"]
    Headers["headers() async function<br/>HTTP security headers"]
    DevIndicators["devIndicators: false<br/>Disable build indicator"]
    
    SVGRuleTurbo["*.svg → @svgr/webpack<br/>as: '*.js'"]
    SVGRuleWebpack["test: /\.svg$/i<br/>use: @svgr/webpack"]
    
    CSPHeader["Content-Security-Policy<br/>Restrict resource loading"]
    HSTSHeader["Strict-Transport-Security<br/>Force HTTPS (prod only)"]
    
    NextConfig --> Turbopack
    NextConfig --> Webpack
    NextConfig --> Headers
    NextConfig --> DevIndicators
    
    Turbopack --> SVGRuleTurbo
    Webpack --> SVGRuleWebpack
    
    Headers --> CSPHeader
    Headers --> HSTSHeader
    
    style NextConfig fill:#f9f9f9
```

**Sources:** [next.config.ts:1-58]()

### Bundler Configuration

#### Turbopack (Development)

The `turbopack` configuration at [next.config.ts:19-26]() defines rules for the development bundler:

```typescript
turbopack: {
  rules: {
    "*.svg": {
      loaders: ["@svgr/webpack"],
      as: "*.js",
    },
  },
}
```

This rule transforms SVG files into React components using `@svgr/webpack`, allowing SVG imports as JSX elements rather than URL strings.

**Sources:** [next.config.ts:19-26]()

#### Webpack (Production)

The `webpack()` function at [next.config.ts:30-37]() applies the same SVG transformation for production builds:

```typescript
webpack(config) {
  config.module.rules.push({
    test: /\.svg$/i,
    issuer: /\.[jt]sx?$/,
    use: ["@svgr/webpack"],
  });
  return config;
}
```

The `issuer` constraint ensures SVG files are only transformed when imported from JavaScript/TypeScript files (not CSS).

**Sources:** [next.config.ts:30-37]()

### HTTP Security Headers

The `headers()` async function at [next.config.ts:38-54]() configures HTTP security headers returned for all routes.

#### Content Security Policy (CSP)

The CSP is constructed at [next.config.ts:5-16]():

```typescript
const CSP = [
  "default-src 'self';",
  "script-src 'self' 'unsafe-eval' 'unsafe-inline' ;",
  "connect-src 'self';",
  "style-src 'self' 'unsafe-inline';",
  "img-src 'self'",
  "object-src 'none';",
  "frame-ancestors 'none';",
  IS_DEV ? null : "upgrade-insecure-requests;",
]
  .filter(Boolean)
  .join(" ");
```

| Directive | Value | Purpose |
|-----------|-------|---------|
| `default-src` | `'self'` | Default to same-origin only |
| `script-src` | `'self' 'unsafe-eval' 'unsafe-inline'` | Allow scripts from same origin, eval (React dev), inline |
| `connect-src` | `'self'` | Allow fetch/XHR to same origin only |
| `style-src` | `'self' 'unsafe-inline'` | Allow styles from same origin and inline |
| `img-src` | `'self'` | Allow images from same origin only |
| `object-src` | `'none'` | Block all plugins (Flash, Java, etc.) |
| `frame-ancestors` | `'none'` | Prevent embedding in iframes (clickjacking protection) |
| `upgrade-insecure-requests` | (prod only) | Auto-upgrade HTTP to HTTPS |

Note: `'unsafe-eval'` and `'unsafe-inline'` reduce security but are required for React's development mode and some styling approaches. For production deployments with stricter security requirements, consider implementing nonce-based CSP as demonstrated in [src/app/tmp.middleware.ts]().

**Sources:** [next.config.ts:5-16](), [next.config.ts:38-44]()

#### Strict Transport Security (HSTS)

In production (when `NODE_ENV !== "production"`), an HSTS header is added at [next.config.ts:46-51]():

```typescript
if (!IS_DEV) {
  headers.push({
    key: "Strict-Transport-Security",
    value: "max-age=31536000; includeSubDomains; preload",
  });
}
```

This header instructs browsers to only access the site via HTTPS for the next year (31536000 seconds), including all subdomains, and signals eligibility for browser HSTS preload lists.

**Sources:** [next.config.ts:3](), [next.config.ts:46-51]()

### Build Environment Detection

The `IS_DEV` constant at [next.config.ts:3]() determines the build environment:

```typescript
const IS_DEV = process.env.NODE_ENV !== "production";
```

This boolean is used to conditionally apply production-only security features (HSTS, CSP upgrade-insecure-requests) and avoid them in development where they would interfere with local HTTP workflows.

**Sources:** [next.config.ts:3]()

## Request Lifecycle

The following diagram shows how an incoming HTTP request flows through the Next.js application structure:

```mermaid
sequenceDiagram
    participant Browser
    participant NextServer as "Next.js Server"
    participant Headers as "headers() function<br/>next.config.ts"
    participant Middleware as "tmp.middleware.ts<br/>(optional)"
    participant Layout as "RootLayout<br/>layout.tsx"
    participant Page as "Page<br/>page.tsx"
    participant ClientDynamic as "ClientDynamicTTS"
    
    Browser->>NextServer: "GET /"
    NextServer->>Headers: "Call headers()"
    Headers-->>NextServer: "CSP, HSTS headers"
    
    alt Middleware exists
        NextServer->>Middleware: "Process request"
        Middleware-->>NextServer: "Inject nonce"
    end
    
    NextServer->>Layout: "Render RootLayout"
    Layout->>Layout: "Load JetBrains_Mono font<br/>Apply metadata"
    Layout->>Page: "Render children (Page)"
    Page->>ClientDynamic: "Render ClientDynamicTTS"
    ClientDynamic-->>Page: "Server: render dynamic() wrapper"
    Page-->>Layout: "Component tree"
    Layout-->>NextServer: "HTML with <html>, <body>"
    
    NextServer-->>Browser: "HTTP 200 + HTML + headers"
    
    Browser->>Browser: "Parse HTML, download JS bundles"
    Browser->>ClientDynamic: "Hydrate ClientDynamicTTS"
    ClientDynamic->>ClientDynamic: "Dynamic import client component"
    ClientDynamic->>Browser: "Render interactive TTS UI"
```

**Sources:** [next.config.ts:38-54](), [src/app/layout.tsx:1-47](), [src/app/page.tsx:1-6]()

### Server-Side Rendering (SSR)

1. **Request Reception**: Next.js server receives the HTTP request for `/`
2. **Header Application**: The `headers()` function at [next.config.ts:38-54]() adds CSP and HSTS headers to the response
3. **Layout Rendering**: `RootLayout` at [src/app/layout.tsx:34-46]() executes on the server, establishing HTML structure and metadata
4. **Page Rendering**: `Page` at [src/app/page.tsx:3-5]() renders on the server, outputting the `ClientDynamicTTS` wrapper
5. **HTML Response**: Complete HTML is sent to the browser with security headers

**Sources:** [next.config.ts:38-54](), [src/app/layout.tsx:34-46](), [src/app/page.tsx:3-5]()

### Client-Side Hydration

1. **HTML Parsing**: Browser parses the received HTML and begins downloading JavaScript bundles
2. **Font Loading**: Next.js font optimization loads JetBrains Mono with optimal performance
3. **React Hydration**: React hydrates the server-rendered HTML, making it interactive
4. **Dynamic Import**: `ClientDynamicTTS` performs a dynamic import (client-side only) to load the actual TTS UI
5. **Interactive UI**: The TTS interface becomes fully interactive with browser APIs available

This two-phase approach (SSR for shell + CSR for interactive components) optimizes both initial page load and interactivity.

**Sources:** [src/app/page.tsx:1-6]()

## Configuration File Dependencies

The following table summarizes how different configuration files relate to the Next.js application structure:

| File | Purpose | Referenced By |
|------|---------|---------------|
| `next.config.ts` | Build configuration, bundler rules, HTTP headers | Next.js build system |
| `src/app/layout.tsx` | Root HTML structure, metadata, fonts | Next.js App Router |
| `src/app/page.tsx` | Main page route component | Next.js App Router |
| `src/app/globals.css` | Global styles (imported in layout) | [src/app/layout.tsx:4]() |
| `tsconfig.json` | TypeScript configuration, path aliases | Next.js, TypeScript compiler |
| `postcss.config.mjs` | PostCSS plugins (TailwindCSS) | Next.js build system |

For detailed information on styling configuration, see [Styling System](#4.3). For build process details, see [Build Process](#4.2).

**Sources:** [next.config.ts:1-58](), [src/app/layout.tsx:1-47](), [src/app/page.tsx:1-6]()

---

# Page: Frontend Components

# Frontend Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/ClientDynamicTTS.tsx](src/components/ClientDynamicTTS.tsx)
- [src/components/CodeCopyButton.tsx](src/components/CodeCopyButton.tsx)
- [src/components/DownloadButton.tsx](src/components/DownloadButton.tsx)
- [src/components/PlayButton.tsx](src/components/PlayButton.tsx)
- [src/components/ShareButton.tsx](src/components/ShareButton.tsx)
- [src/components/ShareDialog.tsx](src/components/ShareDialog.tsx)

</details>



## Purpose and Scope

This document details the React component architecture of the OpenAI.fm application, covering the main interactive components responsible for audio generation, playback, download, sharing, and code snippet display. These components form the user interface layer and coordinate with the state management system ([3.4](#3.4)) and API routes ([3.3](#3.3)) to deliver the core text-to-speech functionality.

For information about the overall Next.js application structure and routing, see [Next.js Application Structure](#3.1). For details on how components access global state, see [State Management](#3.4). For audio processing internals beyond the UI layer, see [Audio Processing](#3.5).

---

## Component Architecture Overview

The frontend is composed of specialized, single-responsibility components that interact through the centralized Zustand store (`appStore`). The diagram below maps the component hierarchy to actual code entities:

**Diagram: Component Hierarchy and Dependencies**

```mermaid
graph TB
    ClientDynamicTTS["ClientDynamicTTS<br/>(ClientDynamicTTS.tsx)"]
    TTSPage["TTSPage<br/>(Dynamic Import)"]
    
    PlayButton["PlayButton<br/>(PlayButton.tsx)"]
    DownloadButton["DownloadButton<br/>(DownloadButton.tsx)"]
    ShareButton["ShareButton<br/>(ShareButton.tsx)"]
    CodeCopyButton["CodeCopyButton<br/>(CodeCopyButton.tsx)"]
    
    PlayingWaveformPlay["PlayingWaveform<br/>(PlayButton.tsx:10-35)"]
    PlayingWaveformDL["PlayingWaveform<br/>(DownloadButton.tsx:6-31)"]
    ShareDialog["ShareDialog<br/>(ShareDialog.tsx)"]
    
    ButtonUI["Button<br/>(ui/Button)"]
    Icons["Icons<br/>(ui/Icons)"]
    
    appStore["appStore<br/>(lib/store)"]
    useCopiedDelay["useCopiedDelay<br/>(hooks/useCopiedDelay)"]
    copyText["copyText<br/>(lib/copyText)"]
    getCodeSnippet["getCodeSnippet<br/>(lib/codeSnippet)"]
    
    ClientDynamicTTS -->|"dynamic import"| TTSPage
    TTSPage --> PlayButton
    TTSPage --> DownloadButton
    TTSPage --> ShareButton
    TTSPage --> CodeCopyButton
    
    PlayButton --> PlayingWaveformPlay
    DownloadButton --> PlayingWaveformDL
    ShareButton --> ShareDialog
    
    PlayButton --> ButtonUI
    DownloadButton --> ButtonUI
    ShareButton --> ButtonUI
    CodeCopyButton --> ButtonUI
    
    PlayButton --> Icons
    DownloadButton --> Icons
    ShareButton --> Icons
    CodeCopyButton --> Icons
    
    PlayButton --> appStore
    DownloadButton --> appStore
    ShareButton --> appStore
    CodeCopyButton --> appStore
    
    ShareButton --> useCopiedDelay
    CodeCopyButton --> useCopiedDelay
    
    ShareButton --> copyText
    CodeCopyButton --> copyText
    CodeCopyButton --> getCodeSnippet
    
    ShareDialog --> copyText
```

**Sources:** [src/components/ClientDynamicTTS.tsx](), [src/components/PlayButton.tsx](), [src/components/DownloadButton.tsx](), [src/components/ShareButton.tsx](), [src/components/CodeCopyButton.tsx](), [src/components/ShareDialog.tsx]()

---

## Main Interactive Components

### PlayButton Component

The `PlayButton` component handles audio generation, playback control, and real-time waveform visualization. It orchestrates the complete audio lifecycle from API request to audio playback.

**Component Structure:**

| Aspect | Implementation |
|--------|----------------|
| File Path | [src/components/PlayButton.tsx]() |
| State Management | `appStore.useState()`, `appStore.getState()`, `appStore.setState()` |
| Audio APIs | `HTMLAudioElement`, `AudioContext`, `AnalyserNode` |
| Key State Variables | `audioLoading`, `audioLoaded`, `isPlaying`, `amplitudeLevels` |

**Diagram: PlayButton Audio Generation Flow**

```mermaid
sequenceDiagram
    participant User
    participant PlayButton
    participant appStore
    participant GenerateAPI["/api/generate"]
    participant AudioElement["HTMLAudioElement"]
    participant AudioContext
    participant AnalyserNode
    participant PlayingWaveform
    
    User->>PlayButton: "Click Play"
    PlayButton->>appStore: "getState()"
    appStore-->>PlayButton: "{input, prompt, voice}"
    
    PlayButton->>PlayButton: "setAudioLoading(true)"
    PlayButton->>PlayButton: "crypto.randomUUID()"
    
    PlayButton->>appStore: "setState({latestAudioUrl: null})"
    
    PlayButton->>GenerateAPI: "GET /api/generate?input=...&voice=..."
    Note over PlayButton,GenerateAPI: URL constructed at line 80-85
    
    PlayButton->>appStore: "setState({latestAudioUrl: audioUrl})"
    
    PlayButton->>AudioElement: "new Audio()"
    Note over PlayButton,AudioElement: Line 94
    
    alt "Not Safari/iOS"
        PlayButton->>AudioContext: "new AudioContext()"
        PlayButton->>AudioContext: "createMediaElementSource(audio)"
        PlayButton->>AudioContext: "createAnalyser()"
        AudioContext->>AnalyserNode: "fftSize = 256"
        Note over PlayButton,AnalyserNode: Lines 100-109
    end
    
    PlayButton->>AudioElement: "audio.src = audioUrl"
    PlayButton->>AudioElement: "audio.autoplay = true"
    Note over PlayButton,AudioElement: Lines 152-153
    
    GenerateAPI-->>AudioElement: "Audio Stream"
    
    AudioElement->>PlayButton: "onplay event"
    PlayButton->>PlayButton: "setInterval(sample, 100)"
    Note over PlayButton: Line 135
    
    loop "Every 100ms"
        alt "Safari/iOS"
            PlayButton->>PlayButton: "generateRandomAmplitudes()"
            Note over PlayButton: Lines 51-54, 113-115
        else "Chrome/Firefox"
            PlayButton->>AnalyserNode: "getByteTimeDomainData(data)"
            AnalyserNode-->>PlayButton: "Uint8Array"
            PlayButton->>PlayButton: "Calculate amplitude"
            Note over PlayButton: Lines 118-124
        end
        PlayButton->>PlayButton: "setAmplitudeLevels()"
        PlayButton->>PlayingWaveform: "Update display"
    end
    
    PlayButton-->>User: "Visual waveform feedback"
```

**Key Implementation Details:**

1. **Browser Detection** [src/components/PlayButton.tsx:7-9](): The component detects Safari and iOS to use static animation instead of Web Audio API analysis
2. **Audio Context Setup** [src/components/PlayButton.tsx:100-109](): Creates `AudioContext`, connects `MediaElementSource` to `AnalyserNode` for real-time amplitude extraction
3. **Amplitude Sampling** [src/components/PlayButton.tsx:112-125](): Interval-based sampling at 100ms intervals, using either Web Audio API data or random values for incompatible browsers
4. **State Coordination** [src/components/PlayButton.tsx:76-77, 86](): Sets `latestAudioUrl` in the store for consumption by `DownloadButton`

**Sources:** [src/components/PlayButton.tsx:1-188]()

---

### DownloadButton Component

The `DownloadButton` component manages audio file downloads with Service Worker integration for caching. It can download from cached audio or trigger a fresh generation.

**Component Structure:**

| Aspect | Implementation |
|--------|----------------|
| File Path | [src/components/DownloadButton.tsx]() |
| Service Worker | Registration at [src/components/DownloadButton.tsx:67]() |
| Message Handling | `navigator.serviceWorker.addEventListener("message")` |
| Download Strategies | Cached blob download, fresh API request, pending cache download |

**Diagram: DownloadButton Download Strategies**

```mermaid
flowchart TD
    Start["User clicks Download"]
    GetState["appStore.getState()"]
    CheckURL{"latestAudioUrl<br/>exists?"}
    
    NoURL["Path 1: No URL<br/>Fresh Generation"]
    FreshAPI["POST /api/generate<br/>with FormData"]
    FreshBlob["Receive Blob"]
    CreateLinkFresh["Create &lt;a&gt; element"]
    DownloadFresh["Trigger download"]
    
    YesURL["Path 2: URL exists"]
    ClearURL["setState({latestAudioUrl: null})"]
    CheckDataURL{"dataUrl<br/>cached?"}
    
    HasDataURL["Path 2a: Use cached dataUrl"]
    CreateLinkCached["Create &lt;a&gt; element"]
    DownloadCached["Trigger download"]
    
    NoDataURL["Path 2b: Wait for SW cache"]
    ListenSW["Listen for ADD_TO_CACHE"]
    ReceiveSW["Receive blob from SW"]
    CreateLinkSW["Create &lt;a&gt; element"]
    DownloadSW["Trigger download"]
    
    Start --> GetState
    GetState --> CheckURL
    
    CheckURL -->|"No"| NoURL
    NoURL --> FreshAPI
    FreshAPI --> FreshBlob
    FreshBlob --> CreateLinkFresh
    CreateLinkFresh --> DownloadFresh
    
    CheckURL -->|"Yes"| YesURL
    YesURL --> ClearURL
    ClearURL --> CheckDataURL
    
    CheckDataURL -->|"Yes"| HasDataURL
    HasDataURL --> CreateLinkCached
    CreateLinkCached --> DownloadCached
    
    CheckDataURL -->|"No"| NoDataURL
    NoDataURL --> ListenSW
    ListenSW --> ReceiveSW
    ReceiveSW --> CreateLinkSW
    CreateLinkSW --> DownloadSW
```

**Key Implementation Details:**

1. **Service Worker Registration** [src/components/DownloadButton.tsx:64-70](): Registers worker file `worker-444eae9e2e1bdd6edd8969f319655e70.js` on component mount
2. **Message Event Handling** [src/components/DownloadButton.tsx:44-61](): Listens for `ADD_TO_CACHE` messages containing audio blob
3. **Filename Generation** [src/components/DownloadButton.tsx:81-84](): Constructs filename using voice and vibe parameters, format determined by browser type
4. **Three Download Paths**:
   - Fresh generation [src/components/DownloadButton.tsx:86-104](): POST to `/api/generate` when no cached URL
   - Cached blob [src/components/DownloadButton.tsx:127-132](): Direct download from `dataUrl` object URL
   - Pending cache [src/components/DownloadButton.tsx:109-124](): Wait for Service Worker to cache, then download
5. **Browser Format Detection** [src/components/DownloadButton.tsx:33-37](): Uses Chrome detection to determine WAV vs MP3 format

**Sources:** [src/components/DownloadButton.tsx:1-149]()

---

### ShareButton Component

The `ShareButton` component persists the current TTS configuration to the database and generates a shareable URL. It integrates with the `/api/share` endpoint ([3.3](#3.3)) and PostgreSQL database ([3.6](#3.6)).

**Component Structure:**

| Aspect | Implementation |
|--------|----------------|
| File Path | [src/components/ShareButton.tsx]() |
| API Endpoint | POST `/api/share` |
| State Hook | `useCopiedDelay()` for visual feedback |
| Dialog Component | `ShareDialog` for URL display |

**State Flow Table:**

| Step | Action | Code Reference |
|------|--------|----------------|
| 1 | User clicks Share | [src/components/ShareButton.tsx:45-49]() |
| 2 | Retrieve current state | [src/components/ShareButton.tsx:14]() `appStore.getState()` |
| 3 | POST to API | [src/components/ShareButton.tsx:17-23]() |
| 4 | Receive hash ID | [src/components/ShareButton.tsx:28-29]() |
| 5 | Construct URL | [src/components/ShareButton.tsx:30]() `origin/pathname#hash` |
| 6 | Copy to clipboard | [src/components/ShareButton.tsx:32]() `copyText()` |
| 7 | Show dialog | [src/components/ShareButton.tsx:33-34]() `setOpen(true)` |

**Key Implementation Details:**

1. **Request Payload** [src/components/ShareButton.tsx:22](): Sends JSON with `{input, prompt, voice}` from current state
2. **URL Construction** [src/components/ShareButton.tsx:30](): Uses fragment identifier (`#hash`) for client-side routing
3. **Error Handling** [src/components/ShareButton.tsx:24-27, 35-38](): Alerts user on API failure
4. **Copy Feedback** [src/components/ShareButton.tsx:10, 45-46](): Uses `useCopiedDelay()` hook to prevent double-clicks

**Sources:** [src/components/ShareButton.tsx:1-60]()

---

### CodeCopyButton Component

The `CodeCopyButton` component generates and copies code snippets demonstrating API usage. It reads the current `codeView` selection and application state to generate appropriate examples.

**Component Structure:**

| Aspect | Implementation |
|--------|----------------|
| File Path | [src/components/CodeCopyButton.tsx]() |
| Code Generation | `getCodeSnippet()` utility function |
| State Dependencies | `input`, `prompt`, `voice`, `codeView` from `appStore` |

**Code Generation Flow:**

```mermaid
flowchart LR
    Click["User clicks Copy"]
    CheckCopied{"Already<br/>copied?"}
    GetState["appStore.getState()"]
    ExtractState["Extract:<br/>input, prompt,<br/>voice, codeView"]
    Generate["getCodeSnippet(codeView,<br/>{input, prompt, voice})"]
    Copy["copyText(codeValue)"]
    UpdateUI["Show Check icon"]
    
    Click --> CheckCopied
    CheckCopied -->|"No"| GetState
    CheckCopied -->|"Yes"| Return["Return early"]
    GetState --> ExtractState
    ExtractState --> Generate
    Generate --> Copy
    Copy --> UpdateUI
```

**Key Implementation Details:**

1. **State Extraction** [src/components/CodeCopyButton.tsx:16](): Destructures `{input, prompt, voice, codeView}` from store
2. **Code Generation** [src/components/CodeCopyButton.tsx:17](): Delegates to `getCodeSnippet()` utility with view type and parameters
3. **Copy Trigger** [src/components/CodeCopyButton.tsx:26](): Invokes `trigger()` from `useCopiedDelay()` hook for UI feedback
4. **Conditional Rendering** [src/components/CodeCopyButton.tsx:30-38](): Shows either Check or Copy icon based on `copied` state

**Sources:** [src/components/CodeCopyButton.tsx:1-43]()

---

## Shared UI Components

### PlayingWaveform Component

The `PlayingWaveform` component is a reusable visualization element that renders animated waveform bars. It appears in both `PlayButton` and `DownloadButton` with different states.

**Component Signature:**

```typescript
PlayingWaveform({
  audioLoaded: boolean,
  amplitudeLevels: number[]
})
```

**Component Instances:**

| Location | Purpose | Amplitude Source |
|----------|---------|------------------|
| [src/components/PlayButton.tsx:10-35]() | Real-time playback visualization | Web Audio API or random values |
| [src/components/DownloadButton.tsx:6-31]() | Loading indicator | Static values `[0.04, 0.04, 0.04, 0.04, 0.04]` |

**Rendering Logic:**

1. **Container** [src/components/PlayButton.tsx:17](): Fixed size `w-[36px] h-[16px]`
2. **Bar Generation** [src/components/PlayButton.tsx:18-29](): Maps `amplitudeLevels` array to visual bars
3. **Height Calculation** [src/components/PlayButton.tsx:19](): Clamps amplitude values: `Math.min(Math.max(level * 30, 0.2), 1.9) * 100%`
4. **Animation** [src/components/PlayButton.tsx:20-21, 24](): Applies `animate-wave` class when `audioLoaded` is false, with staggered delays

**Sources:** [src/components/PlayButton.tsx:10-35](), [src/components/DownloadButton.tsx:6-31]()

---

### ShareDialog Component

The `ShareDialog` component provides a modal interface for displaying and copying shareable URLs. It uses Radix UI's Dialog primitive for accessibility.

**Component Props:**

```typescript
{
  shareUrl: string | null,
  open: boolean,
  onOpenChange: (open: boolean) => void
}
```

**Component Structure Table:**

| Element | Implementation | Purpose |
|---------|----------------|---------|
| Dialog.Root | [src/components/ShareDialog.tsx:15]() | Controls open state |
| Dialog.Overlay | [src/components/ShareDialog.tsx:17]() | Backdrop with fade animation |
| Dialog.Content | [src/components/ShareDialog.tsx:18]() | Centered modal container |
| Dialog.Title | [src/components/ShareDialog.tsx:19-21]() | "Share Link" header |
| Input field | [src/components/ShareDialog.tsx:26-30]() | Displays share URL |
| Copy button | [src/components/ShareDialog.tsx:34-43]() | Copies URL to clipboard |
| Close button | [src/components/ShareDialog.tsx:46-52]() | X icon in top-right |

**Key Implementation Details:**

1. **Radix UI Integration** [src/components/ShareDialog.tsx:2](): Imports from `radix-ui` package
2. **Animation Classes** [src/components/ShareDialog.tsx:17-18](): Uses `data-[state=open]:animate-*` selectors
3. **Copy Action** [src/components/ShareDialog.tsx:36-39](): Invokes `copyText()` utility on button click
4. **Input Default Value** [src/components/ShareDialog.tsx:29](): Displays `shareUrl ?? ""` to handle null state

**Sources:** [src/components/ShareDialog.tsx:1-60]()

---

## Dynamic Import Pattern

### ClientDynamicTTS Component

The `ClientDynamicTTS` component implements Next.js dynamic imports to prevent server-side rendering of browser-dependent code. This is critical for components using Web APIs like `AudioContext`, `navigator.serviceWorker`, and `navigator.userAgent`.

**Implementation:**

```typescript
// src/components/ClientDynamicTTS.tsx:1-11
"use client";
import dynamic from "next/dynamic";

const DynamicComponentWithNoSSR = dynamic(
  () => import("@/components/TTSPage"),
  { ssr: false }
);

export default function ClientDynamicTTS() {
  return <DynamicComponentWithNoSSR />;
}
```

**Technical Details:**

| Aspect | Value |
|--------|-------|
| Client Directive | `"use client"` at [src/components/ClientDynamicTTS.tsx:1]() |
| Dynamic Import | `next/dynamic` with `ssr: false` option |
| Target Component | `@/components/TTSPage` |
| Parent Component | Rendered by `page.tsx` ([3.1](#3.1)) |

**Why This Pattern:**

1. **Browser API Access**: Components like `PlayButton` and `DownloadButton` use `navigator.serviceWorker`, `AudioContext`, and `navigator.userAgent` which don't exist in Node.js environment
2. **SSR Prevention**: The `{ ssr: false }` option prevents Next.js from attempting to render during server-side generation
3. **Hydration Safety**: Ensures client-only code executes only in browser context

**Sources:** [src/components/ClientDynamicTTS.tsx:1-12]()

---

## Component Communication Patterns

### State Access Patterns

All main components access the centralized `appStore` using consistent patterns:

**Pattern Comparison Table:**

| Component | Read Pattern | Write Pattern | State Dependencies |
|-----------|--------------|---------------|-------------------|
| PlayButton | `appStore.getState()` [line 57] | `appStore.setState()` [lines 77, 86] | `input`, `prompt`, `voice` (read), `latestAudioUrl` (write) |
| DownloadButton | `appStore.useState()` [line 40], `appStore.getState()` [line 73] | `appStore.setState()` [line 107] | `latestAudioUrl` (read/write), `selectedEntry`, `input`, `prompt`, `voice` (read) |
| ShareButton | `appStore.getState()` [line 14] | None | `input`, `prompt`, `voice` (read) |
| CodeCopyButton | `appStore.getState()` [line 16] | None | `input`, `prompt`, `voice`, `codeView` (read) |

**Hook Usage Pattern:**

```typescript
// Reactive subscription (DownloadButton)
const latestAudioUrl = appStore.useState((s) => s.latestAudioUrl);

// One-time read (PlayButton, ShareButton, CodeCopyButton)
const { input, prompt, voice } = appStore.getState();
```

**Sources:** [src/components/PlayButton.tsx:57, 77, 86](), [src/components/DownloadButton.tsx:40, 73, 107](), [src/components/ShareButton.tsx:14](), [src/components/CodeCopyButton.tsx:16]()

---

### External Service Integration

Components integrate with external services through different mechanisms:

**Integration Patterns Diagram:**

```mermaid
graph LR
    PlayButton["PlayButton"]
    DownloadButton["DownloadButton"]
    ShareButton["ShareButton"]
    
    GenerateAPI["/api/generate<br/>(API Route)"]
    ShareAPI["/api/share<br/>(API Route)"]
    ServiceWorker["Service Worker<br/>(worker-*.js)"]
    
    PlayButton -->|"GET request"| GenerateAPI
    PlayButton -->|"Set latestAudioUrl"| appStore
    
    DownloadButton -->|"Read latestAudioUrl"| appStore
    DownloadButton -->|"POST request"| GenerateAPI
    DownloadButton -->|"Register & Listen"| ServiceWorker
    
    ServiceWorker -->|"ADD_TO_CACHE message"| DownloadButton
    
    ShareButton -->|"POST request"| ShareAPI
    
    subgraph "State Store"
        appStore["appStore<br/>(Zustand)"]
    end
```

**Communication Mechanisms:**

1. **HTTP Fetch**: `PlayButton`, `DownloadButton`, and `ShareButton` use `fetch()` for API calls
2. **Service Worker Messages**: `DownloadButton` communicates bidirectionally with Service Worker via `postMessage()` and event listeners
3. **State Store**: `PlayButton` writes `latestAudioUrl`, `DownloadButton` reads it for coordination

**Sources:** [src/components/PlayButton.tsx:80-86](), [src/components/DownloadButton.tsx:44-61, 64-70, 86-104](), [src/components/ShareButton.tsx:17-23]()

---

## Component Dependency Summary

The following table summarizes all external dependencies for each component:

| Component | State Management | Utilities | Hooks | UI Primitives | External APIs |
|-----------|-----------------|-----------|-------|---------------|---------------|
| PlayButton | `appStore` | None | None | `Button`, `Play` icon | `Audio`, `AudioContext`, `AnalyserNode` |
| DownloadButton | `appStore` | None | None | `Button`, `Download` icon | `navigator.serviceWorker`, `fetch()` |
| ShareButton | `appStore` | `copyText` | `useCopiedDelay` | `Button`, `Share` icon, `ShareDialog` | `fetch()` |
| CodeCopyButton | `appStore` | `copyText`, `getCodeSnippet` | `useCopiedDelay` | `Button`, `Copy`/`Check` icons | `navigator.clipboard` (via `copyText`) |
| ShareDialog | None | `copyText` | None | Radix `Dialog.*` | `navigator.clipboard` (via `copyText`) |
| ClientDynamicTTS | None | None | None | None | `next/dynamic` |

**Sources:** [src/components/PlayButton.tsx:1-6](), [src/components/DownloadButton.tsx:1-5](), [src/components/ShareButton.tsx:1-7](), [src/components/CodeCopyButton.tsx:1-6](), [src/components/ShareDialog.tsx:1-4](), [src/components/ClientDynamicTTS.tsx:1-3]()

---

# Page: API Routes

# API Routes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/api/generate/route.ts](src/app/api/generate/route.ts)
- [src/app/api/share/route.ts](src/app/api/share/route.ts)

</details>



## Purpose and Scope

This document details the Next.js API routes that provide backend functionality for the OpenAI.fm application. The two primary API routes are `/api/generate` for audio generation and `/api/share` for configuration persistence. These routes serve as secure proxies and data handlers, interfacing with the OpenAI Speech API and PostgreSQL database respectively.

For information about the frontend components that consume these routes, see [Frontend Components](#3.2). For database schema details, see [Database Integration](#3.6). For environment configuration of API keys and database connections, see [Environment Configuration](#2.2).

**Sources:** [src/app/api/generate/route.ts](), [src/app/api/share/route.ts]()

## API Routes Overview

The application implements two API route handlers located in the Next.js App Router structure:

| Route Path | File Location | HTTP Methods | External Service |
|------------|---------------|--------------|------------------|
| `/api/generate` | `src/app/api/generate/route.ts` | GET, POST | OpenAI Speech API |
| `/api/share` | `src/app/api/share/route.ts` | GET, POST | PostgreSQL via `@vercel/postgres` |

```mermaid
graph TB
    subgraph "Client Layer"
        PlayButton["PlayButton Component"]
        DownloadButton["DownloadButton Component"]
        ShareButton["ShareButton Component"]
    end
    
    subgraph "API Routes Layer"
        GenerateRoute["src/app/api/generate/route.ts<br/>GET & POST handlers"]
        ShareRoute["src/app/api/share/route.ts<br/>GET & POST handlers"]
    end
    
    subgraph "External Services"
        OpenAIAPI["OpenAI Speech API<br/>https://api.openai.com/v1/audio/speech"]
        PostgresDB["PostgreSQL Database<br/>shares table"]
    end
    
    subgraph "Validation Constants"
        Constants["MAX_INPUT_LENGTH: 1000<br/>MAX_PROMPT_LENGTH: 1000<br/>VOICES array"]
    end
    
    PlayButton -->|"GET /api/generate?input=...&voice=..."| GenerateRoute
    DownloadButton -->|"GET /api/generate?input=...&voice=..."| GenerateRoute
    ShareButton -->|"POST /api/share {input, prompt, voice}"| ShareRoute
    ShareButton -->|"GET /api/share?hash=uuid"| ShareRoute
    
    GenerateRoute -->|"validates against"| Constants
    ShareRoute -->|"imports"| Constants
    
    GenerateRoute -->|"POST with OPENAI_API_KEY"| OpenAIAPI
    ShareRoute -->|"INSERT/SELECT via sql tag"| PostgresDB
    
    OpenAIAPI -->|"audio stream"| GenerateRoute
    PostgresDB -->|"configuration data"| ShareRoute
    
    GenerateRoute -->|"audio stream"| PlayButton
    GenerateRoute -->|"audio stream"| DownloadButton
    ShareRoute -->|"share id or data"| ShareButton
```

**Diagram: API Routes Architecture**

This diagram illustrates the relationship between client components and API routes, showing the specific file paths and code entities involved in request handling.

**Sources:** [src/app/api/generate/route.ts](), [src/app/api/share/route.ts]()

## `/api/generate` Route - Audio Generation

The `generate` route serves as a secure proxy to the OpenAI Speech API, handling both GET and POST requests for audio generation. The route implements identical logic for both HTTP methods to support different client usage patterns.

### Route Handler Functions

The route exports two async functions:

- `GET(req: NextRequest)` - [src/app/api/generate/route.ts:9-69]()
- `POST(req: NextRequest)` - [src/app/api/generate/route.ts:71-129]()

### Request Parameters

Both handlers accept the same parameters, differing only in extraction method (query string vs. form data):

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| `input` | string | Yes | Truncated to `MAX_INPUT_LENGTH` (1000) | Text to be synthesized |
| `prompt` | string | No | Truncated to `MAX_PROMPT_LENGTH` (1000) | Instructions for voice generation |
| `voice` | string | Yes | Must be in `VOICES` array | Voice identifier |
| `vibe` | string | No | No validation | Used for filename generation |

**GET Handler Parameter Extraction:**
```typescript
const { searchParams } = new URL(req.url);
let input = searchParams.get("input") || "";
let prompt = searchParams.get("prompt") || "";
const voice = searchParams.get("voice") || "";
const vibe = searchParams.get("vibe") || "audio";
```
[src/app/api/generate/route.ts:10-19]()

**POST Handler Parameter Extraction:**
```typescript
const formData = await req.formData();
let input = formData.get("input")?.toString() || "";
let prompt = formData.get("prompt")?.toString() || "";
const voice = formData.get("voice")?.toString() || "";
const vibe = formData.get("vibe") || "audio";
```
[src/app/api/generate/route.ts:75-79]()

**Sources:** [src/app/api/generate/route.ts:1-130]()

### Response Format Selection

The route dynamically selects the audio response format based on the client's user agent:

```typescript
const ua = userAgent(req);
const response_format = ua.engine?.name === "Blink" ? "wav" : "mp3";
```
[src/app/api/generate/route.ts:12-13]()

- **Blink engine** (Chrome, Edge, Opera): Returns `wav` format
- **Other engines** (Firefox, Safari): Returns `mp3` format

**Sources:** [src/app/api/generate/route.ts:12-13](), [src/app/api/generate/route.ts:72-73]()

### OpenAI API Integration

```mermaid
sequenceDiagram
    participant Client as "Client (PlayButton/DownloadButton)"
    participant Handler as "GET/POST handler"
    participant Validator as "Input Validator"
    participant OpenAI as "OpenAI API<br/>api.openai.com/v1/audio/speech"
    
    Client->>Handler: "Request with input, prompt, voice"
    Handler->>Handler: "userAgent(req) to detect engine"
    Handler->>Handler: "Set response_format (wav/mp3)"
    Handler->>Validator: "input.slice(0, MAX_INPUT_LENGTH)"
    Handler->>Validator: "prompt.slice(0, MAX_PROMPT_LENGTH)"
    Handler->>Validator: "Check VOICES.includes(voice)"
    
    alt "Invalid voice"
        Handler-->>Client: "400 Invalid voice"
    end
    
    Handler->>OpenAI: "POST /v1/audio/speech"
    Note over Handler,OpenAI: "Authorization: Bearer ${OPENAI_API_KEY}<br/>Body: {model, input, response_format, voice, instructions}"
    
    alt "OpenAI API Error"
        OpenAI-->>Handler: "Error status"
        Handler-->>Client: "Error status with message"
    end
    
    OpenAI-->>Handler: "Audio stream (body)"
    Handler->>Handler: "Set headers:<br/>Content-Type, Content-Disposition, Cache-Control"
    Handler-->>Client: "Stream audio response"
```

**Diagram: /api/generate Request Flow**

The OpenAI API request is constructed as follows:

```typescript
const apiResponse = await fetch("https://api.openai.com/v1/audio/speech", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "gpt-4o-mini-tts",
    input,
    response_format,
    voice,
    ...(prompt && { instructions: prompt }),
  }),
});
```
[src/app/api/generate/route.ts:32-46]()

**Key Implementation Details:**

- **Model:** Hard-coded to `"gpt-4o-mini-tts"` [src/app/api/generate/route.ts:39]()
- **Authentication:** Uses `process.env.OPENAI_API_KEY` [src/app/api/generate/route.ts:35]()
- **Conditional Instructions:** The `instructions` field is only included if `prompt` is non-empty [src/app/api/generate/route.ts:44]()

**Sources:** [src/app/api/generate/route.ts:32-46](), [src/app/api/generate/route.ts:92-106]()

### Response Headers and Streaming

The route streams the OpenAI API response directly to the client with appropriate headers:

```typescript
const filename = `openai-fm-${voice}-${vibe}.${response_format}`;

return new Response(apiResponse.body, {
  headers: {
    "Content-Type": response_format === "wav" ? "audio/wav" : "audio/mpeg",
    "Content-Disposition": `inline; filename="${filename}"`,
    "Cache-Control": "no-cache",
  },
});
```
[src/app/api/generate/route.ts:53-62]()

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Type` | `audio/wav` or `audio/mpeg` | Identifies audio format |
| `Content-Disposition` | `inline; filename="openai-fm-{voice}-{vibe}.{format}"` | Suggests filename for downloads |
| `Cache-Control` | `no-cache` | Prevents browser caching of audio |

**Sources:** [src/app/api/generate/route.ts:53-62](), [src/app/api/generate/route.ts:113-122]()

## `/api/share` Route - Share Functionality

The `share` route provides persistence for TTS configurations, allowing users to save and retrieve their input, prompt, and voice settings via PostgreSQL.

### POST Handler - Create Share

The POST handler persists a new share configuration to the database:

```typescript
export async function POST(req: NextRequest) {
  try {
    const { input, prompt, voice } = await req.json();
    const clippedInput = input.slice(0, MAX_INPUT_LENGTH);
    const clippedPrompt = prompt.slice(0, MAX_PROMPT_LENGTH);
    const id = crypto.randomUUID();
    await sql`INSERT INTO shares (id, input, prompt, voice) VALUES (${id}, ${
      clippedInput ?? ""
    }, ${clippedPrompt ?? ""}, ${voice ?? ""});`;
    return Response.json({ id });
  } catch (err) {
    console.error("Error storing share params:", err);
    return new Response("An error ocurred.", { status: 500 });
  }
}
```
[src/app/api/share/route.ts:6-20]()

**Request Body Schema:**
```json
{
  "input": "string (truncated to 1000 chars)",
  "prompt": "string (truncated to 1000 chars)",
  "voice": "string"
}
```

**Response Schema:**
```json
{
  "id": "uuid-v4-string"
}
```

**Sources:** [src/app/api/share/route.ts:6-20]()

### GET Handler - Retrieve Share

The GET handler retrieves a previously saved configuration by its UUID:

```typescript
export async function GET(req: NextRequest) {
  try {
    const url = new URL(req.url);
    const hash = url.searchParams.get("hash");
    if (!hash) {
      return new Response("Not found", { status: 404 });
    }
    const { rows } = await sql<{
      input: string;
      prompt: string;
      voice: string;
    }>`SELECT input, prompt, voice FROM shares WHERE id = ${hash};`;
    if (rows.length === 0) {
      return new Response("Not found", { status: 404 });
    }
    return Response.json(rows[0]);
  } catch (err) {
    console.error("Error retrieving share params:", err);
    return new Response("An error ocurred.", { status: 500 });
  }
}
```
[src/app/api/share/route.ts:22-42]()

**Request Parameters:**
- `hash` (query parameter): UUID of the share to retrieve

**Response Schema:**
```json
{
  "input": "string",
  "prompt": "string",
  "voice": "string"
}
```

**Sources:** [src/app/api/share/route.ts:22-42]()

### Database Integration

```mermaid
graph LR
    subgraph "ShareButton Component"
        CreateShare["POST request<br/>{input, prompt, voice}"]
        RetrieveShare["GET request<br/>?hash=uuid"]
    end
    
    subgraph "route.ts handlers"
        POSTHandler["POST handler<br/>line 6-20"]
        GETHandler["GET handler<br/>line 22-42"]
    end
    
    subgraph "Database Operations"
        SQLInsert["sql INSERT INTO shares<br/>(id, input, prompt, voice)"]
        SQLSelect["sql SELECT * FROM shares<br/>WHERE id = hash"]
    end
    
    subgraph "PostgreSQL"
        SharesTable["shares table<br/>columns: id, input, prompt, voice"]
    end
    
    subgraph "Data Processing"
        Truncate["input.slice(0, MAX_INPUT_LENGTH)<br/>prompt.slice(0, MAX_PROMPT_LENGTH)"]
        UUID["crypto.randomUUID()"]
    end
    
    CreateShare --> POSTHandler
    POSTHandler --> Truncate
    POSTHandler --> UUID
    Truncate --> SQLInsert
    UUID --> SQLInsert
    SQLInsert --> SharesTable
    SharesTable -.->|"return {id}"| POSTHandler
    
    RetrieveShare --> GETHandler
    GETHandler --> SQLSelect
    SQLSelect --> SharesTable
    SharesTable -.->|"return {input, prompt, voice}"| GETHandler
```

**Diagram: /api/share Database Flow**

The route uses the `sql` template tag from `@vercel/postgres` for parameterized queries:

```typescript
import { sql } from "@vercel/postgres";
```
[src/app/api/share/route.ts:2]()

**Database Schema (inferred from queries):**

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (string) | Primary key, generated via `crypto.randomUUID()` |
| `input` | text | TTS input text (max 1000 chars) |
| `prompt` | text | TTS instructions (max 1000 chars) |
| `voice` | text | Voice identifier |

**Sources:** [src/app/api/share/route.ts:1-43]()

## Input Validation and Security

Both routes implement consistent input validation using shared constants:

```typescript
export const MAX_INPUT_LENGTH = 1000;
export const MAX_PROMPT_LENGTH = 1000;
```
[src/app/api/generate/route.ts:3-4]()

These constants are imported and reused in the share route:

```typescript
import { MAX_PROMPT_LENGTH, MAX_INPUT_LENGTH } from "../generate/route";
```
[src/app/api/share/route.ts:3]()

### Validation Rules

| Rule | Implementation | Location |
|------|----------------|----------|
| Input length | `input.slice(0, MAX_INPUT_LENGTH)` | [src/app/api/generate/route.ts:24](), [src/app/api/generate/route.ts:84](), [src/app/api/share/route.ts:9]() |
| Prompt length | `prompt.slice(0, MAX_PROMPT_LENGTH)` | [src/app/api/generate/route.ts:25](), [src/app/api/generate/route.ts:85](), [src/app/api/share/route.ts:10]() |
| Voice validation | `VOICES.includes(voice)` | [src/app/api/generate/route.ts:27](), [src/app/api/generate/route.ts:87]() |

**Voice Validation:**
```typescript
if (!VOICES.includes(voice)) {
  return new Response("Invalid voice", { status: 400 });
}
```
[src/app/api/generate/route.ts:27-29]()

The `VOICES` array is imported from the library module:
```typescript
import { VOICES } from "@/lib/library";
```
[src/app/api/generate/route.ts:8]()

**Sources:** [src/app/api/generate/route.ts:3-4](), [src/app/api/generate/route.ts:8](), [src/app/api/generate/route.ts:24-29](), [src/app/api/share/route.ts:3](), [src/app/api/share/route.ts:9-10]()

## Error Handling

Both routes implement consistent error handling patterns with try-catch blocks and appropriate HTTP status codes.

### `/api/generate` Error Responses

| Error Condition | Status Code | Response Message |
|-----------------|-------------|------------------|
| Invalid voice parameter | 400 | "Invalid voice" |
| OpenAI API error | Proxied status | "An error occurred while generating the audio." |
| Unexpected exception | 500 | "Error generating speech" |

**Implementation:**
```typescript
if (!apiResponse.ok) {
  return new Response(`An error occurred while generating the audio.`, {
    status: apiResponse.status,
  });
}
```
[src/app/api/generate/route.ts:47-51]()

```typescript
catch (err) {
  console.error("Error generating speech:", err);
  return new Response("Error generating speech", {
    status: 500,
  });
}
```
[src/app/api/generate/route.ts:63-68]()

### `/api/share` Error Responses

| Error Condition | Status Code | Response Message |
|-----------------|-------------|------------------|
| Missing hash parameter | 404 | "Not found" |
| Hash not found in database | 404 | "Not found" |
| Database error (POST) | 500 | "An error ocurred." |
| Database error (GET) | 500 | "An error ocurred." |

**Missing Hash Validation:**
```typescript
const hash = url.searchParams.get("hash");
if (!hash) {
  return new Response("Not found", { status: 404 });
}
```
[src/app/api/share/route.ts:25-27]()

**Empty Result Set:**
```typescript
if (rows.length === 0) {
  return new Response("Not found", { status: 404 });
}
```
[src/app/api/share/route.ts:34-36]()

**Sources:** [src/app/api/generate/route.ts:47-68](), [src/app/api/generate/route.ts:107-128](), [src/app/api/share/route.ts:16-19](), [src/app/api/share/route.ts:25-27](), [src/app/api/share/route.ts:34-40]()

## API Route Registration

Next.js App Router automatically registers these routes based on their file system location:

- `src/app/api/generate/route.ts` → `/api/generate`
- `src/app/api/share/route.ts` → `/api/share`

The routes are secured by Content Security Policy headers configured in [next.config.ts]() and [src/app/tmp.middleware.ts]() (see [Security Considerations](#5)).

**Sources:** [src/app/api/generate/route.ts](), [src/app/api/share/route.ts]()

---

# Page: State Management

# State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/CodeCopyButton.tsx](src/components/CodeCopyButton.tsx)
- [src/components/DownloadButton.tsx](src/components/DownloadButton.tsx)
- [src/components/PlayButton.tsx](src/components/PlayButton.tsx)
- [src/components/ShareButton.tsx](src/components/ShareButton.tsx)

</details>



## Purpose and Scope

This document explains the centralized state management system used throughout the OpenAI.fm application. The system is built on Zustand, a lightweight state management library that provides a simple API for managing global application state. This page covers the store structure, state fields, access patterns, and how components interact with the state store.

For information about how state is consumed in specific UI components, see [Frontend Components](#3.2). For details on how API routes interact with state data, see [API Routes](#3.3).

---

## Store Architecture

The application uses a single global store implemented with Zustand, exported as `appStore` from [src/lib/store]() (inferred from import statements). Zustand provides a minimal API surface with three primary methods for state interaction:

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `appStore.getState()` | Retrieve current state snapshot | State object |
| `appStore.setState(partial)` | Update state (partial or complete) | void |
| `appStore.useState(selector)` | React hook for reactive subscriptions | Selected value |

The store follows a centralized state pattern where all components access the same shared state instance, eliminating prop drilling and providing a single source of truth for application data.

**Sources:** [src/components/PlayButton.tsx:4](), [src/components/DownloadButton.tsx:4](), [src/components/ShareButton.tsx:4](), [src/components/CodeCopyButton.tsx:4]()

---

## State Schema

The `appStore` maintains the following state fields, which represent the complete application state at runtime:

```mermaid
classDiagram
    class appStore {
        +string input
        +string prompt
        +string voice
        +string codeView
        +string|null latestAudioUrl
        +SelectedEntry|null selectedEntry
        +getState() State
        +setState(partial) void
        +useState(selector) any
    }
    
    class SelectedEntry {
        +string name
    }
    
    appStore --> SelectedEntry
```

### State Fields

| Field | Type | Description | Used By |
|-------|------|-------------|---------|
| `input` | `string` | Text input to be converted to speech | All action components |
| `prompt` | `string` | System prompt for TTS generation | All action components |
| `voice` | `string` | Selected voice identifier | All action components |
| `codeView` | `string` | Selected code snippet view type | CodeCopyButton |
| `latestAudioUrl` | `string \| null` | URL of most recently generated audio | PlayButton, DownloadButton |
| `selectedEntry` | `object \| null` | Currently selected preset entry with `name` property | DownloadButton |

**Sources:** [src/components/PlayButton.tsx:57](), [src/components/DownloadButton.tsx:73-79](), [src/components/ShareButton.tsx:14](), [src/components/CodeCopyButton.tsx:16]()

---

## State Access Patterns

### Pattern 1: Snapshot Access with `getState()`

Components use `appStore.getState()` to retrieve a one-time snapshot of the current state. This pattern is used when components need to read state values without subscribing to changes, typically during event handlers or side effects.

**Example Usage:**
```typescript
// PlayButton.tsx:57
const { input, prompt, voice } = appStore.getState();
```

**Components Using This Pattern:**
- **PlayButton** [src/components/PlayButton.tsx:57]() - Reads TTS parameters before generating audio
- **DownloadButton** [src/components/DownloadButton.tsx:73-79]() - Reads state for download filename and API call
- **ShareButton** [src/components/ShareButton.tsx:14]() - Reads configuration to persist via `/api/share`
- **CodeCopyButton** [src/components/CodeCopyButton.tsx:16]() - Reads state to generate code snippet

**Sources:** [src/components/PlayButton.tsx:57](), [src/components/DownloadButton.tsx:73-79](), [src/components/ShareButton.tsx:14](), [src/components/CodeCopyButton.tsx:16]()

### Pattern 2: State Updates with `setState()`

Components use `appStore.setState()` to update state by providing a partial state object. Zustand merges the partial update with the existing state.

**Example Usage:**
```typescript
// PlayButton.tsx:77,86
appStore.setState({ latestAudioUrl: null });
appStore.setState({ latestAudioUrl: audioUrl });
```

**Update Operations:**
- **PlayButton** [src/components/PlayButton.tsx:77,86]() - Sets `latestAudioUrl` during audio generation lifecycle
- **DownloadButton** [src/components/DownloadButton.tsx:107]() - Clears `latestAudioUrl` after download

**Sources:** [src/components/PlayButton.tsx:77,86](), [src/components/DownloadButton.tsx:107]()

### Pattern 3: Reactive Subscription with `useState()`

Components use `appStore.useState()` with a selector function to subscribe to specific state slices. The component re-renders when the selected value changes.

**Example Usage:**
```typescript
// DownloadButton.tsx:40
const latestAudioUrl = appStore.useState((s) => s.latestAudioUrl);
```

**Subscriptions:**
- **DownloadButton** [src/components/DownloadButton.tsx:40]() - Subscribes to `latestAudioUrl` to enable download button and setup service worker listeners

**Sources:** [src/components/DownloadButton.tsx:40]()

---

## State Flow Diagrams

### Audio Generation State Flow

```mermaid
sequenceDiagram
    participant User
    participant PlayButton
    participant appStore
    participant API as "/api/generate"
    participant DownloadButton
    
    User->>PlayButton: "Click Play"
    PlayButton->>appStore: "getState()"
    appStore-->>PlayButton: "{input, prompt, voice}"
    
    PlayButton->>PlayButton: "Generate UUID"
    PlayButton->>appStore: "setState({latestAudioUrl: null})"
    
    PlayButton->>PlayButton: "Construct URL"
    PlayButton->>appStore: "setState({latestAudioUrl: url})"
    
    Note over DownloadButton: "Reactive subscription"
    appStore-->>DownloadButton: "latestAudioUrl changed"
    DownloadButton->>DownloadButton: "Setup SW listener"
    
    PlayButton->>API: "GET with params"
    API-->>PlayButton: "Audio stream"
    PlayButton->>PlayButton: "Audio.play()"
```

This diagram shows how `PlayButton` orchestrates state updates during audio generation. The component reads initial parameters via `getState()`, clears the previous audio URL, generates a new URL, and stores it via `setState()`. The `DownloadButton` component reactively responds to the state change through its `useState()` subscription.

**Sources:** [src/components/PlayButton.tsx:57,77,86](), [src/components/DownloadButton.tsx:40]()

### Share Functionality State Flow

```mermaid
sequenceDiagram
    participant User
    participant ShareButton
    participant appStore
    participant API as "/api/share"
    participant ShareDialog
    
    User->>ShareButton: "Click Share"
    ShareButton->>appStore: "getState()"
    appStore-->>ShareButton: "{input, prompt, voice}"
    
    ShareButton->>API: "POST /api/share"
    Note over API: "Persists to PostgreSQL"
    API-->>ShareButton: "{id: hash}"
    
    ShareButton->>ShareButton: "Construct URL with hash"
    ShareButton->>ShareButton: "copyText(shareUrl)"
    ShareButton->>ShareDialog: "setOpen(true)"
    ShareDialog-->>User: "Display share URL"
```

The share flow demonstrates one-directional state reading. `ShareButton` uses `getState()` to snapshot the current configuration, sends it to the API for persistence, and manages local UI state (`open`, `shareUrl`) without writing back to the global store.

**Sources:** [src/components/ShareButton.tsx:14,17-34]()

### Download Functionality State Flow

```mermaid
sequenceDiagram
    participant User
    participant DownloadButton
    participant appStore
    participant ServiceWorker
    participant API as "/api/generate"
    
    Note over DownloadButton: "Subscribed to latestAudioUrl"
    appStore-->>DownloadButton: "latestAudioUrl = url"
    DownloadButton->>ServiceWorker: "Listen for ADD_TO_CACHE"
    ServiceWorker-->>DownloadButton: "ADD_TO_CACHE + blob"
    DownloadButton->>DownloadButton: "setDataUrl(objectUrl)"
    
    User->>DownloadButton: "Click Download"
    DownloadButton->>appStore: "getState()"
    appStore-->>DownloadButton: "{selectedEntry, voice, etc}"
    
    alt "No latestAudioUrl"
        DownloadButton->>API: "POST /api/generate"
        API-->>DownloadButton: "Audio blob"
    else "Has dataUrl from cache"
        DownloadButton->>DownloadButton: "Use cached blob"
    end
    
    DownloadButton->>appStore: "setState({latestAudioUrl: null})"
    DownloadButton->>User: "Download file"
```

The download flow combines both state subscription and snapshot reading. The component subscribes to `latestAudioUrl` via `useState()` to setup service worker listeners, uses `getState()` during the download event to read filename parameters, and calls `setState()` to clear the audio URL after download.

**Sources:** [src/components/DownloadButton.tsx:40,73-79,107]()

---

## Component-Store Interaction Map

```mermaid
graph TB
    appStore["appStore<br/>(Zustand Store)"]
    
    subgraph "Read-Only Components"
        ShareButton["ShareButton<br/>getState()"]
        CodeCopyButton["CodeCopyButton<br/>getState()"]
    end
    
    subgraph "Read-Write Components"
        PlayButton["PlayButton<br/>getState() + setState()"]
        DownloadButton["DownloadButton<br/>useState() + getState() + setState()"]
    end
    
    subgraph "State Fields"
        input["input: string"]
        prompt["prompt: string"]
        voice["voice: string"]
        codeView["codeView: string"]
        latestAudioUrl["latestAudioUrl: string|null"]
        selectedEntry["selectedEntry: object|null"]
    end
    
    ShareButton -->|"reads"| input
    ShareButton -->|"reads"| prompt
    ShareButton -->|"reads"| voice
    
    CodeCopyButton -->|"reads"| input
    CodeCopyButton -->|"reads"| prompt
    CodeCopyButton -->|"reads"| voice
    CodeCopyButton -->|"reads"| codeView
    
    PlayButton -->|"reads"| input
    PlayButton -->|"reads"| prompt
    PlayButton -->|"reads"| voice
    PlayButton -->|"writes"| latestAudioUrl
    
    DownloadButton -->|"subscribes"| latestAudioUrl
    DownloadButton -->|"reads"| selectedEntry
    DownloadButton -->|"reads"| input
    DownloadButton -->|"reads"| prompt
    DownloadButton -->|"reads"| voice
    DownloadButton -->|"writes"| latestAudioUrl
    
    input --> appStore
    prompt --> appStore
    voice --> appStore
    codeView --> appStore
    latestAudioUrl --> appStore
    selectedEntry --> appStore
```

This diagram maps each component's interaction mode with the store:

- **Read-Only Components** (`ShareButton`, `CodeCopyButton`) - Use `getState()` to snapshot state for operations
- **Read-Write Components** (`PlayButton`, `DownloadButton`) - Both read and write state, with `DownloadButton` also using reactive subscriptions

**Sources:** [src/components/PlayButton.tsx:4,57,77,86](), [src/components/DownloadButton.tsx:4,40,73-79,107](), [src/components/ShareButton.tsx:4,14](), [src/components/CodeCopyButton.tsx:4,16]()

---

## State Lifecycle and Coordination

### Audio URL Management

The `latestAudioUrl` field coordinates state between `PlayButton` and `DownloadButton`:

1. **Initial State**: `latestAudioUrl` is `null`
2. **PlayButton Generation** [src/components/PlayButton.tsx:77]():
   - Clears `latestAudioUrl` to `null` before generation
   - Constructs new URL with UUID
   - Sets `latestAudioUrl` to the new URL [src/components/PlayButton.tsx:86]()
3. **DownloadButton Subscription** [src/components/DownloadButton.tsx:40,44-61]():
   - Reactive subscription detects URL change
   - Sets up service worker message listener for caching
   - Creates object URL from cached blob
4. **Post-Download Cleanup** [src/components/DownloadButton.tsx:107]():
   - Sets `latestAudioUrl` back to `null`
   - Triggers cleanup in subscription effect

**Sources:** [src/components/PlayButton.tsx:77,86](), [src/components/DownloadButton.tsx:40,44-61,107]()

### Code Snippet Generation

The `CodeCopyButton` reads multiple state fields to generate code snippets:

```typescript
// CodeCopyButton.tsx:16-17
const { input, prompt, voice, codeView } = appStore.getState();
const codeValue = getCodeSnippet(codeView, { input, prompt, voice });
```

The `codeView` field determines the snippet format (language/framework), while `input`, `prompt`, and `voice` provide the actual TTS configuration values.

**Sources:** [src/components/CodeCopyButton.tsx:16-17]()

### Download Filename Generation

The `DownloadButton` composes filenames from multiple state fields:

```typescript
// DownloadButton.tsx:73-84
const { selectedEntry, input, prompt, voice, latestAudioUrl: storeUrl } = appStore.getState();
const vibe = selectedEntry?.name.toLowerCase().replace(/ /g, "-") ?? "audio";
const filename = `openai-fm-${voice}-${vibe}.${IS_CHROME ? "wav" : "mp3"}`;
```

The filename incorporates:
- `voice` - Voice identifier
- `selectedEntry.name` - Preset name (or "audio" fallback)
- Browser detection for format extension

**Sources:** [src/components/DownloadButton.tsx:73-84]()

---

## State Access Summary

| Component | Access Pattern | Fields Read | Fields Written |
|-----------|---------------|-------------|----------------|
| **PlayButton** | `getState()` + `setState()` | `input`, `prompt`, `voice` | `latestAudioUrl` |
| **DownloadButton** | `useState()` + `getState()` + `setState()` | `latestAudioUrl`, `selectedEntry`, `input`, `prompt`, `voice` | `latestAudioUrl` |
| **ShareButton** | `getState()` | `input`, `prompt`, `voice` | None |
| **CodeCopyButton** | `getState()` | `input`, `prompt`, `voice`, `codeView` | None |

**Sources:** [src/components/PlayButton.tsx](), [src/components/DownloadButton.tsx](), [src/components/ShareButton.tsx](), [src/components/CodeCopyButton.tsx]()

---

## Store Implementation Details

While the actual store implementation file is not provided in the source files, we can infer the Zustand store structure from usage patterns:

```typescript
// Inferred store structure from usage
type State = {
  input: string;
  prompt: string;
  voice: string;
  codeView: string;
  latestAudioUrl: string | null;
  selectedEntry: { name: string } | null;
};

// Store API (Zustand standard)
interface AppStore {
  getState: () => State;
  setState: (partial: Partial<State>) => void;
  useState: <T>(selector: (state: State) => T) => T;
}
```

The store is accessed via a single import path `@/lib/store`, which exports the `appStore` instance that all components share.

**Sources:** [src/components/PlayButton.tsx:4](), [src/components/DownloadButton.tsx:4](), [src/components/ShareButton.tsx:4](), [src/components/CodeCopyButton.tsx:4]()

---

# Page: Audio Processing

# Audio Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [public/worker-444eae9e2e1bdd6edd8969f319655e70.js](public/worker-444eae9e2e1bdd6edd8969f319655e70.js)
- [src/app/api/generate/route.ts](src/app/api/generate/route.ts)
- [src/components/DownloadButton.tsx](src/components/DownloadButton.tsx)
- [src/components/PlayButton.tsx](src/components/PlayButton.tsx)

</details>



This document describes the audio processing workflow in OpenAI.fm, covering audio generation via the OpenAI TTS API, real-time waveform visualization using the Web Audio API, service worker caching, and download functionality.

## System Overview

The audio processing system handles the complete workflow from text input to audio playback. The core components are:

1. **API Route** (`/api/generate`) - Proxies requests to OpenAI's speech API
2. **PlayButton Component** - Manages audio playback and real-time visualization
3. **Service Worker** - Caches audio responses for offline access and downloads
4. **DownloadButton Component** - Provides audio download functionality
5. **Web Audio API Integration** - Real-time amplitude analysis for waveform visualization

### Complete Audio Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant PlayButton as "PlayButton.tsx"
    participant AppStore as "appStore (Zustand)"
    participant APIGenerate as "/api/generate"
    participant ServiceWorker as "worker-444eae9e2e1bdd6edd8969f319655e70.js"
    participant OpenAI as "api.openai.com/v1/audio/speech"
    participant AudioAPI as "Web Audio API"
    
    User->>PlayButton: "Click Play"
    PlayButton->>AppStore: "getState()"
    AppStore-->>PlayButton: "{input, prompt, voice}"
    PlayButton->>PlayButton: "crypto.randomUUID()"
    PlayButton->>AppStore: "setState({latestAudioUrl})"
    
    PlayButton->>APIGenerate: "GET /api/generate?input=...&voice=..."
    ServiceWorker->>ServiceWorker: "Intercept fetch event"
    ServiceWorker->>APIGenerate: "POST /api/generate (FormData)"
    APIGenerate->>APIGenerate: "Validate voice, truncate input/prompt"
    APIGenerate->>OpenAI: "POST with model: gpt-4o-mini-tts"
    OpenAI-->>APIGenerate: "Audio stream (WAV/MP3)"
    APIGenerate-->>ServiceWorker: "Response stream"
    ServiceWorker->>ServiceWorker: "responseClone.blob()"
    ServiceWorker->>PlayButton: "postMessage({type: 'ADD_TO_CACHE'})"
    ServiceWorker-->>PlayButton: "Original response stream"
    
    PlayButton->>PlayButton: "new Audio(), set src"
    PlayButton->>AudioAPI: "createMediaElementSource()"
    PlayButton->>AudioAPI: "createAnalyser(), fftSize=256"
    PlayButton->>AudioAPI: "source.connect(analyser)"
    
    loop "Every 100ms while playing"
        PlayButton->>AudioAPI: "getByteTimeDomainData()"
        AudioAPI-->>PlayButton: "Amplitude data"
        PlayButton->>PlayButton: "setAmplitudeLevels()"
    end
    
    PlayButton-->>User: "Audio playback + waveform animation"
```

Sources: [src/components/PlayButton.tsx:1-187](), [src/app/api/generate/route.ts:1-130](), [public/worker-444eae9e2e1bdd6edd8969f319655e70.js:1-56]()

## Audio Generation via `/api/generate`

The `/api/generate` API route acts as a secure proxy to OpenAI's TTS API, handling validation and request formatting.

### API Route Implementation Details

The route supports both GET and POST methods with identical logic. Key operations:

| Operation | Implementation | Location |
|-----------|----------------|----------|
| Input validation | Truncate to `MAX_INPUT_LENGTH` (1000 chars) | [src/app/api/generate/route.ts:24-25]() |
| Prompt validation | Truncate to `MAX_PROMPT_LENGTH` (1000 chars) | [src/app/api/generate/route.ts:25]() |
| Voice validation | Check against `VOICES` array from `@/lib/library` | [src/app/api/generate/route.ts:27-29]() |
| Format selection | WAV for Blink engine (Chrome), MP3 otherwise | [src/app/api/generate/route.ts:13](), [src/app/api/generate/route.ts:73]() |
| OpenAI API call | POST to `https://api.openai.com/v1/audio/speech` | [src/app/api/generate/route.ts:32]() |
| Model | `gpt-4o-mini-tts` | [src/app/api/generate/route.ts:39]() |
| Response streaming | Stream audio back to client | [src/app/api/generate/route.ts:56-62]() |

### Request/Response Format

**Request Parameters (Query or FormData)**:
- `input` - Text to convert to speech
- `prompt` - Optional instructions for the TTS model
- `voice` - Voice identifier (validated against `VOICES`)
- `vibe` - Used for filename generation

**Response**:
```
Content-Type: audio/wav | audio/mpeg
Content-Disposition: inline; filename="openai-fm-{voice}-{vibe}.{format}"
Cache-Control: no-cache
```

The response body is the audio stream from OpenAI's API, passed through directly to enable efficient streaming.

Sources: [src/app/api/generate/route.ts:1-130]()

## Web Audio API Integration

The `PlayButton` component uses the Web Audio API to perform real-time amplitude analysis for waveform visualization.

### Web Audio API Setup

The audio analysis pipeline is established when playback begins:

```mermaid
graph LR
    Audio["new Audio()"] --> MediaSource["createMediaElementSource()"]
    MediaSource --> Analyser["createAnalyser()"]
    Analyser --> Destination["ctx.destination"]
    
    Analyser --> Sample["getByteTimeDomainData()"]
    Sample --> Amplitude["Calculate average amplitude"]
    Amplitude --> State["setAmplitudeLevels()"]
    State --> Waveform["PlayingWaveform component"]
```

**Implementation Details:**

| Component | Code Entity | Purpose |
|-----------|-------------|---------|
| Audio Context | `audioContextRef.current = new AudioContext()` | Web Audio API context ([src/components/PlayButton.tsx:101]()) |
| Audio Source | `ctx.createMediaElementSource(audio)` | Connect HTML Audio to Web Audio API ([src/components/PlayButton.tsx:104]()) |
| Analyser Node | `ctx.createAnalyser(); analyser.fftSize = 256` | Analyze frequency/time domain data ([src/components/PlayButton.tsx:105-106]()) |
| Data Sampling | `analyserRef.current.getByteTimeDomainData(data)` | Get waveform amplitude data ([src/components/PlayButton.tsx:119]()) |
| Update Interval | `setInterval(sample, 100)` | Sample amplitude every 100ms ([src/components/PlayButton.tsx:135]()) |

### Amplitude Calculation and Visualization

The `sample()` function ([src/components/PlayButton.tsx:112-125]()) calculates amplitude by:

1. Retrieving time-domain data via `getByteTimeDomainData()`
2. Computing average deviation from center (128): `Math.abs(v - 128)`
3. Normalizing to 0-1 range: `avg / 128`
4. Updating a sliding window of 5 amplitude values

The `PlayingWaveform` component ([src/components/PlayButton.tsx:10-35]()) renders this as 5 animated vertical bars with:
- Height proportional to amplitude: `Math.min(Math.max(level * 30, 0.2), 1.9) * 100%`
- Staggered horizontal positioning: `left: ${idx * 6}px`
- CSS transitions for smooth animation

### Browser-Specific Behavior

| Browser | Implementation | Reason |
|---------|----------------|--------|
| Safari/iOS | Static random animation | Web Audio API restrictions ([src/components/PlayButton.tsx:49]()) |
| Chrome/Other | Real-time amplitude analysis | Full Web Audio API support |

Detection: `IS_SAFARI` and `IS_IOS` constants ([src/components/PlayButton.tsx:7-8]())

Sources: [src/components/PlayButton.tsx:1-187]()

## Audio Playback with HTML5 Audio Element

Playback uses the HTML5 `Audio` element with event listeners for state management:

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Loading: "handleSubmit() called"
    Loading --> Playing: "audio.onplay event"
    Playing --> Paused: "audio.onpause event"
    Playing --> Ended: "audio.onended event"
    Paused --> Playing: "resume playback"
    Ended --> Idle: "clearSampling()"
    
    state Playing {
        [*] --> SamplingAmplitude
        SamplingAmplitude --> UpdatingWaveform: "Every 100ms"
        UpdatingWaveform --> SamplingAmplitude
    }
```

**Event Handlers:**

| Event | Handler | Effect | Location |
|-------|---------|--------|----------|
| `onerror` | Error handler | Alert user, reset state | [src/components/PlayButton.tsx:127-132]() |
| `onplay` | Play handler | Start amplitude sampling, update UI | [src/components/PlayButton.tsx:134-139]() |
| `onpause` | Pause handler | Stop sampling, reset state | [src/components/PlayButton.tsx:150]() |
| `onended` | End handler | Stop sampling, reset state | [src/components/PlayButton.tsx:151]() |

The component maintains three state flags:
- `audioLoading` - Request in progress
- `audioLoaded` - Audio data loaded and playing
- `isPlaying` - Currently playing (not paused)

Sources: [src/components/PlayButton.tsx:1-187]()

## Service Worker Caching Strategy

The service worker (`worker-444eae9e2e1bdd6edd8969f319655e70.js`) implements a sophisticated caching strategy for audio responses.

### Service Worker Request Transformation

```mermaid
flowchart TD
    FetchEvent["fetch event for /api/generate"] --> CheckMethod{"request.method === 'GET'?"}
    CheckMethod -->|Yes| ExtractParams["Extract query params:<br/>input, prompt, voice, vibe"]
    CheckMethod -->|No| PassThrough["Pass through unmodified"]
    
    ExtractParams --> BuildFormData["new FormData()<br/>Append params"]
    BuildFormData --> ConvertPOST["Modify request:<br/>method = 'POST'<br/>body = formData<br/>Clear search params"]
    
    ConvertPOST --> FetchNetwork["fetch() modified request"]
    FetchNetwork --> CheckResponse{"Response OK &&<br/>Not range request?"}
    
    CheckResponse -->|Yes| CloneResponse["responseClone = response.clone()"]
    CheckResponse -->|No| ReturnOriginal["Return original response"]
    
    CloneResponse --> ExtractBlob["responseClone.blob()"]
    ExtractBlob --> NotifyClients["clients.postMessage({<br/>type: 'ADD_TO_CACHE',<br/>url: originalUrl,<br/>blob: blob<br/>})"]
    NotifyClients --> ReturnOriginal2["Return original response"]
```

**Key Operations:**

| Step | Implementation | Location |
|------|----------------|----------|
| Intercept requests | `addEventListener("fetch", ...)` | [public/worker-444eae9e2e1bdd6edd8969f319655e70.js:9-55]() |
| GET to POST conversion | `new FormData()` with params from URL | [public/worker-444eae9e2e1bdd6edd8969f319655e70.js:16-20]() |
| Clone response | `networkResponse.clone()` | [public/worker-444eae9e2e1bdd6edd8969f319655e70.js:37]() |
| Extract blob | `responseClone.blob()` | [public/worker-444eae9e2e1bdd6edd8969f319655e70.js:40]() |
| Notify clients | `client.postMessage({type: "ADD_TO_CACHE", ...})` | [public/worker-444eae9e2e1bdd6edd8969f319655e70.js:42-46]() |

**Why Convert GET to POST?**

The service worker converts GET requests to POST to work around browser caching behavior. The POST request with FormData ensures:
1. The request bypasses browser HTTP cache
2. The service worker has full control over caching
3. Audio blobs can be extracted and passed to client components

Sources: [public/worker-444eae9e2e1bdd6edd8969f319655e70.js:1-56]()

## Download Functionality

The `DownloadButton` component provides audio download capability using the cached audio blob from the service worker.

### Download Flow with Service Worker Integration

```mermaid
sequenceDiagram
    participant User
    participant DownloadButton as "DownloadButton.tsx"
    participant AppStore as "appStore"
    participant ServiceWorker as "Service Worker"
    participant DOM as "DOM (hidden link)"
    
    User->>DownloadButton: "Click Download"
    DownloadButton->>AppStore: "getState()"
    AppStore-->>DownloadButton: "{input, prompt, voice, latestAudioUrl}"
    
    alt "Audio already cached (dataUrl exists)"
        DownloadButton->>DOM: "createElement('a')<br/>link.href = dataUrl<br/>link.download = filename"
        DownloadButton->>DOM: "link.click()"
        DOM-->>User: "Browser download dialog"
    else "No latestAudioUrl (never played)"
        DownloadButton->>DownloadButton: "fetch('/api/generate', POST)"
        DownloadButton->>DownloadButton: "await res.blob()"
        DownloadButton->>DOM: "URL.createObjectURL(blob)"
        DownloadButton->>DOM: "link.click()"
        DOM-->>User: "Browser download dialog"
    else "latestAudioUrl exists but not cached yet"
        DownloadButton->>ServiceWorker: "Wait for ADD_TO_CACHE message"
        ServiceWorker-->>DownloadButton: "postMessage({blob})"
        DownloadButton->>DOM: "URL.createObjectURL(blob)"
        DownloadButton->>DOM: "link.click()"
        DOM-->>User: "Browser download dialog"
    end
```

### Implementation Details

**Service Worker Message Listener:**

The component registers a message listener for `ADD_TO_CACHE` events ([src/components/DownloadButton.tsx:44-61]()):

```typescript
const handler = (e: MessageEvent) => {
  if (e.data.type === "ADD_TO_CACHE" && e.data.url === latestAudioUrl) {
    objectUrl = URL.createObjectURL(e.data.blob);
    setDataUrl(objectUrl);
  }
};
navigator.serviceWorker.addEventListener("message", handler);
```

**Download States:**

| State | Condition | Action |
|-------|-----------|--------|
| Already cached | `dataUrl` exists | Immediate download from object URL ([src/components/DownloadButton.tsx:127-132]()) |
| Never played | `!latestAudioUrl` | Fetch directly, download blob ([src/components/DownloadButton.tsx:86-104]()) |
| Waiting for cache | `latestAudioUrl` but no `dataUrl` | Wait for service worker message ([src/components/DownloadButton.tsx:109-124]()) |

**Filename Generation:**

Format: `openai-fm-{voice}-{vibe}.{format}` where:
- `voice` - Selected voice from appStore
- `vibe` - Derived from `selectedEntry.name` or "audio"
- `format` - "wav" for Chrome (`IS_CHROME`), "mp3" otherwise

Browser detection: `navigator.userAgentData?.brands` ([src/components/DownloadButton.tsx:33-37]())

**Service Worker Registration:**

The component registers the service worker on mount ([src/components/DownloadButton.tsx:63-70]()):

```typescript
navigator.serviceWorker
  .register("/worker-444eae9e2e1bdd6edd8969f319655e70.js")
  .catch((err) => console.error("SW registration failed", err));
```

Sources: [src/components/DownloadButton.tsx:1-149](), [public/worker-444eae9e2e1bdd6edd8969f319655e70.js:1-56]()

## Audio Format Selection and Browser Compatibility

The system selects audio format based on browser capabilities to optimize compatibility and quality.

### Format Selection Logic

| Browser Engine | Format | Reason | Detection Method |
|----------------|--------|--------|------------------|
| Blink (Chrome/Edge) | WAV | Higher quality, better support | `userAgent(req).engine?.name === "Blink"` |
| Other (Safari/Firefox) | MP3 | Universal compatibility | Default fallback |

The format is determined server-side in the API route using Next.js's `userAgent()` helper:

```
const ua = userAgent(req);
const response_format = ua.engine?.name === "Blink" ? "wav" : "mp3";
```

**Locations:**
- GET handler: [src/app/api/generate/route.ts:12-13]()
- POST handler: [src/app/api/generate/route.ts:72-73]()

### Browser-Specific Considerations

**Safari and iOS Limitations:**

Safari and iOS have restrictions on the Web Audio API that affect waveform visualization:

```mermaid
graph TD
    DetectBrowser["Detect Browser"] --> IsSafariIOS{"IS_SAFARI || IS_IOS?"}
    
    IsSafariIOS -->|Yes| StaticAnimation["useStaticAnimation = true<br/>Generate random amplitudes"]
    IsSafariIOS -->|No| RealTimeAnalysis["Use Web Audio API<br/>Real-time amplitude analysis"]
    
    StaticAnimation --> Render["Render PlayingWaveform<br/>with animated bars"]
    RealTimeAnalysis --> Render
```

**Detection:**
- `IS_SAFARI`: `/^((?!chrome|android).)*safari/i.test(navigator.userAgent)` ([src/components/PlayButton.tsx:7]())
- `IS_IOS`: `/iPad|iPhone|iPod/.test(navigator.userAgent)` ([src/components/PlayButton.tsx:8]())
- `IS_CHROME`: `navigator.userAgentData?.brands` check ([src/components/DownloadButton.tsx:33-37]())

**Fallback Animation:**

For Safari/iOS, the component generates random amplitudes ([src/components/PlayButton.tsx:51-54]()):

```typescript
const generateRandomAmplitudes = () =>
  Array(5).fill(0).map(() => Math.random() * 0.06);
```

This provides visual feedback without relying on Web Audio API analysis.

Sources: [src/app/api/generate/route.ts:1-130](), [src/components/PlayButton.tsx:1-187](), [src/components/DownloadButton.tsx:1-149]()

## Technical Considerations

The audio processing system has several technical considerations to ensure optimal performance and user experience:

1. **Audio Format Handling**: The system must properly process the audio format returned by the OpenAI API.

2. **Browser Compatibility**: The audio playback relies on browser audio capabilities and must be compatible across different browsers.

3. **State Management**: Zustand is used to manage the application state, including audio playback state.

4. **Performance Optimization**: Audio processing and visualization are optimized to prevent performance issues, especially when handling longer audio samples.

5. **Error Handling**: The system includes error handling for API failures, audio loading issues, and playback problems.

6. **Responsive Design**: The waveform visualization adapts to different screen sizes, maintaining usability on various devices.

Sources: README.md, package.json

## Conclusion

The audio processing system in OpenAI.fm provides a seamless experience for users to generate, visualize, and play speech from text input. By leveraging OpenAI's Text-to-Speech API and WaveSurfer.js, the application offers a powerful demonstration of modern text-to-speech capabilities with an intuitive interface for interaction.

Sources: README.md, package.json

---

# Page: Database Integration

# Database Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [src/app/api/share/route.ts](src/app/api/share/route.ts)

</details>



This document details the optional PostgreSQL database integration in OpenAI.fm that enables the sharing feature. While the core text-to-speech functionality works without database connectivity, a PostgreSQL database is required to support the sharing capability.

## Purpose and Scope

The database integration in OpenAI.fm serves a specific purpose: enabling the sharing feature that allows users to create persistent URLs for their text-to-speech creations. This document covers:

- Database connection configuration via environment variables
- Integration with Vercel Postgres
- Database architecture and operation flow
- Setting up the database for development

For information about the overall application architecture, see [System Architecture](#3). For details on general environment configuration, refer to [Environment Configuration](#2.1).

Sources: [README.md:46-55](), [package.json:20]()

## Database Configuration

### Environment Variables

Database connectivity is configured through environment variables in a `.env` file at the project root. The following variables are used for PostgreSQL configuration:

| Variable | Purpose | Example |
|----------|---------|---------|
| POSTGRES_URL | Primary connection string with SSL | "postgresql://username:password@host:port/database_name?sslmode=require" |
| POSTGRES_PRISMA_URL | Connection string for Prisma with pgbouncer | "postgresql://username:password@host:port/database_name?sslmode=require&pgbouncer=true&connect_timeout=15" |
| POSTGRES_URL_NO_SSL | Connection without SSL | "postgresql://username:password@host:port/database_name" |
| POSTGRES_URL_NON_POOLING | Non-pooling connection with SSL | "postgresql://username:password@host:port/database_name?sslmode=require" |
| POSTGRES_USER | Database username | "default" |
| POSTGRES_HOST | Database host | "db.example.com" |
| POSTGRES_PASSWORD | Database password | "your_password" |
| POSTGRES_DATABASE | Database name | "openai_fm" |

The multiple connection string formats accommodate different operational contexts, such as environments with or without connection pooling and SSL requirements.

Sources: [.env.example:1-8]()

## Integration with Vercel Postgres

OpenAI.fm integrates with PostgreSQL using the `@vercel/postgres` package (version ^0.10.0) as specified in `package.json`. This package provides a simplified interface for connecting to and querying Vercel's PostgreSQL service.

### Database Connection Architecture

```mermaid
flowchart TD
    A["Next.js Application"] -->|"Reads"| B[".env Configuration"]
    B -->|"Configures"| C["@vercel/postgres Client"]
    C -->|"Connects to"| D["PostgreSQL Database"]
    E["Sharing Feature"] -->|"Uses"| C
    F["User"] -->|"Requests shared URL"| A
    A -->|"Queries"| C
```

Sources: [package.json:20](), [.env.example:1-8]()

## Database Operation Flow

Based on the sharing feature's purpose, the typical flow for database operations would be:

```mermaid
sequenceDiagram
    participant U as "User"
    participant A as "Application"
    participant V as "@vercel/postgres"
    participant DB as "PostgreSQL Database"
    
    U->>A: "Create text-to-speech content"
    U->>A: "Request to share content"
    A->>V: "Initialize connection"
    V->>DB: "Connect using POSTGRES_URL"
    A->>V: "Store sharing data"
    V->>DB: "Write data to database"
    DB-->>V: "Return success/ID"
    V-->>A: "Return result"
    A-->>U: "Provide sharing URL"
    
    Note over U,DB: "Later: Accessing shared content"
    
    U->>A: "Access sharing URL"
    A->>V: "Initialize connection"
    V->>DB: "Connect using POSTGRES_URL"
    A->>V: "Query by sharing ID"
    V->>DB: "Retrieve data"
    DB-->>V: "Return sharing data"
    V-->>A: "Return result"
    A-->>U: "Display shared content"
```

Sources: [README.md:46-55]()

## Setting Up the Database for Development

To enable the sharing feature during local development:

1. Create a PostgreSQL database instance (local or hosted)
2. Copy the `.env.example` file to create a `.env` file at the project root
3. Configure the database connection variables with your specific database details:

```
POSTGRES_URL="postgresql://username:password@host:port/database_name?sslmode=require"
POSTGRES_PRISMA_URL="postgresql://username:password@host:port/database_name?sslmode=require&pgbouncer=true&connect_timeout=15"
POSTGRES_URL_NO_SSL="postgresql://username:password@host:port/database_name"
POSTGRES_URL_NON_POOLING="postgresql://username:password@host:port/database_name?sslmode=require"
POSTGRES_USER="your_username"
POSTGRES_HOST="your_host"
POSTGRES_PASSWORD="your_password"
POSTGRES_DATABASE="your_database_name"
```

4. Restart the application to apply the database configuration

As noted in the README, this step is optional and only affects the sharing feature:

> "(Optional) Connect to a hosted database: If you want to use the sharing feature, you need to connect to a hosted postgres database."

Sources: [README.md:46-55](), [.env.example:1-8]()

## Vercel Postgres in Next.js Applications

The `@vercel/postgres` package provides database connectivity specifically optimized for Next.js applications deployed on Vercel. While the specific implementation details are not visible in the provided files, the standard integration approach for this package is as follows:

### Integration Architecture

```mermaid
flowchart LR
    A["Next.js API Routes / Server Components"] -->|"Import"| B["@vercel/postgres"]
    B -->|"Connect using environment variables"| C["PostgreSQL Database"]
    D["Sharing Feature API Endpoints"] -->|"Use"| A
```

This architecture leverages Next.js server components or API routes to handle database operations securely.

Sources: [package.json:20]()

## Security Considerations

When implementing the database integration:
- Connection strings contain sensitive credentials and should never be exposed to clients
- The default configuration uses SSL mode for secure connections (`sslmode=require`)
- Production deployments should use environment variables/secrets management rather than `.env` files
- Connection pooling is supported through the `POSTGRES_PRISMA_URL` for improved performance in production

Sources: [.env.example:1-8](), [README.md:46-55]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next.config.ts](next.config.ts)
- [package.json](package.json)

</details>



## Purpose and Scope

This document provides a comprehensive guide for developers working on the OpenAI.fm codebase. It covers the development toolchain, build process, configuration files, and workflows needed to develop, test, and deploy the application. For initial setup instructions, see [Getting Started](#2). For architecture and component details, see [System Architecture](#3). For security configuration specifics, see [Security Considerations](#5).

---

## Development Workflow and Scripts

The primary development interface is through npm scripts defined in [package.json:5-10](). These scripts control the development server, production builds, and code quality checks.

### Available Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `npm run dev` | `next dev --turbopack` | Starts development server with Turbopack bundler |
| `npm run build` | `next build` | Creates optimized production build |
| `npm run start` | `next start` | Runs production build locally |
| `npm run lint` | `next lint` | Executes ESLint validation |

### Development Server

The development server uses Turbopack, Next.js's high-performance bundler. The `--turbopack` flag in [package.json:6]() enables this experimental feature, which provides faster hot module replacement (HMR) and reduced startup times compared to Webpack.

```bash
npm run dev
```

This command:
- Starts the Next.js development server on `http://localhost:3000`
- Enables hot module replacement for instant updates
- Uses Turbopack for faster builds during development
- Loads environment variables from `.env.local`

### Production Build

The production build process optimizes the application for deployment:

```bash
npm run build
npm run start
```

The build process:
- Compiles TypeScript to JavaScript
- Bundles and minifies code using Webpack
- Optimizes static assets
- Generates optimized production pages in `.next/`
- Applies production-specific security headers (HSTS)

**Sources:** [package.json:5-10]()

---

## Build Configuration Architecture

The build system is configured through [next.config.ts](), which controls both development (Turbopack) and production (Webpack) bundling behavior.

### Build Configuration Flow

```mermaid
graph TD
    nextConfig["next.config.ts"]
    envCheck["Environment Check<br/>IS_DEV = NODE_ENV !== 'production'"]
    
    turbopack["Turbopack Configuration<br/>Development Only"]
    webpack["Webpack Configuration<br/>Production Build"]
    headers["HTTP Headers Configuration<br/>CSP, HSTS"]
    
    svgRuleTurbo["SVG Rule (Turbopack)<br/>turbopack.rules['*.svg']"]
    svgRuleWebpack["SVG Rule (Webpack)<br/>config.module.rules.push"]
    svgrLoader["@svgr/webpack Loader<br/>Transforms SVG → React Component"]
    
    cspBuilder["CSP Policy Builder<br/>Array.join with conditional"]
    cspHeader["Content-Security-Policy Header"]
    hstsHeader["Strict-Transport-Security Header<br/>Production Only"]
    
    nextConfig --> envCheck
    nextConfig --> turbopack
    nextConfig --> webpack
    nextConfig --> headers
    
    turbopack --> svgRuleTurbo
    webpack --> svgRuleWebpack
    svgRuleTurbo --> svgrLoader
    svgRuleWebpack --> svgrLoader
    
    headers --> cspBuilder
    envCheck --> cspBuilder
    cspBuilder --> cspHeader
    envCheck --> hstsHeader
```

**Diagram: Build Configuration Structure** - Shows how [next.config.ts]() configures different aspects of the build system including bundlers, asset loaders, and security headers.

**Sources:** [next.config.ts:1-58]()

---

## Build System Components

### Environment Detection

The configuration uses an environment check to differentiate between development and production builds:

```typescript
const IS_DEV = process.env.NODE_ENV !== "production";
```

This constant [next.config.ts:3]() controls:
- Whether to apply HSTS headers (production only)
- Whether to enforce HTTPS upgrades in CSP (production only)

### Turbopack Configuration

Turbopack rules are defined for development builds [next.config.ts:19-26]():

| Property | Value | Purpose |
|----------|-------|---------|
| `rules["*.svg"]` | `{loaders: ["@svgr/webpack"], as: "*.js"}` | Transforms SVG files to React components |
| `devIndicators` | `false` | Disables Next.js development indicators |

The SVG rule configuration enables importing SVG files as React components:

```typescript
import Logo from './logo.svg'; // Becomes a React component
```

### Webpack Configuration

For production builds, Webpack is configured through the `webpack` function [next.config.ts:30-37]():

```typescript
webpack(config) {
  config.module.rules.push({
    test: /\.svg$/i,
    issuer: /\.[jt]sx?$/,
    use: ["@svgr/webpack"],
  });
  return config;
}
```

This ensures consistent SVG handling between development (Turbopack) and production (Webpack) builds.

**Sources:** [next.config.ts:19-37]()

---

## Security Headers Configuration

Security headers are applied to all routes through the `headers` async function [next.config.ts:38-54]().

### Content Security Policy (CSP)

The CSP is built as an array and joined into a header string [next.config.ts:5-16]():

```typescript
const CSP = [
  "default-src 'self';",
  "script-src 'self' 'unsafe-eval' 'unsafe-inline' ;",
  "connect-src 'self';",
  "style-src 'self' 'unsafe-inline';",
  "img-src 'self'",
  "object-src 'none';",
  "frame-ancestors 'none';",
  IS_DEV ? null : "upgrade-insecure-requests;",
].filter(Boolean).join(" ");
```

| Directive | Value | Purpose |
|-----------|-------|---------|
| `default-src` | `'self'` | Only load resources from same origin |
| `script-src` | `'self' 'unsafe-eval' 'unsafe-inline'` | Allow scripts from same origin; `unsafe-eval` needed for development |
| `connect-src` | `'self'` | Restrict API calls to same origin |
| `style-src` | `'self' 'unsafe-inline'` | Allow styles from same origin and inline styles |
| `img-src` | `'self'` | Only load images from same origin |
| `object-src` | `'none'` | Disallow plugins (Flash, etc.) |
| `frame-ancestors` | `'none'` | Prevent clickjacking (no iframe embedding) |
| `upgrade-insecure-requests` | (production only) | Upgrade HTTP to HTTPS |

### HTTP Strict Transport Security (HSTS)

In production, HSTS is enforced [next.config.ts:46-51]():

```typescript
if (!IS_DEV) {
  headers.push({
    key: "Strict-Transport-Security",
    value: "max-age=31536000; includeSubDomains; preload",
  });
}
```

This header:
- Forces HTTPS for 1 year (`max-age=31536000`)
- Applies to all subdomains (`includeSubDomains`)
- Allows preloading in browser HSTS lists (`preload`)

**Sources:** [next.config.ts:5-54]()

---

## Dependency Management

Dependencies are managed through npm and locked in [package-lock.json](). The project uses two categories of dependencies defined in [package.json]().

### Production Dependencies

```mermaid
graph LR
    subgraph "Core Framework"
        next["next ^15.3.6"]
        react["react ^19.0.0"]
        reactDom["react-dom ^19.0.0"]
    end
    
    subgraph "State & Forms"
        zustand["zustand ^5.0.3<br/>State Management"]
        immer["immer ^10.1.1<br/>Immutable Updates"]
        rhf["react-hook-form ^7.54.2<br/>Form Handling"]
    end
    
    subgraph "UI Components"
        radixIcons["@radix-ui/react-icons ^1.3.2"]
        radixSwitch["@radix-ui/react-switch ^1.1.3"]
        radixToast["@radix-ui/react-toast ^1.2.6"]
        clsx["clsx ^2.1.1<br/>Conditional Classes"]
    end
    
    subgraph "Code Editor"
        codemirror["@uiw/react-codemirror ^4.23.10"]
        cmJS["@codemirror/lang-javascript ^6.2.3"]
        cmPython["@codemirror/lang-python ^6.1.7"]
        cmLegacy["@codemirror/legacy-modes ^6.5.0"]
        cmTheme["@uiw/codemirror-theme-duotone ^4.23.10"]
    end
    
    subgraph "Audio & Compression"
        wavesurfer["wavesurfer.js ^7.9.1<br/>Audio Visualization"]
        lzstring["lz-string ^1.5.0<br/>URL Compression"]
    end
    
    subgraph "Backend Services"
        vercelPG["@vercel/postgres ^0.10.0<br/>Database Client"]
    end
```

**Diagram: Production Dependencies Structure** - Maps the major dependency groups and their roles in the application.

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `typescript` | `^5` | TypeScript compiler |
| `eslint` | `^9` | Code linting |
| `eslint-config-next` | `15.2.2` | Next.js-specific ESLint rules |
| `@eslint/eslintrc` | `^3` | ESLint legacy config support |
| `tailwindcss` | `^4` | Utility-first CSS framework |
| `@tailwindcss/postcss` | `^4` | PostCSS plugin for Tailwind |
| `@types/node` | `^20` | Node.js type definitions |
| `@types/react` | `^19` | React type definitions |
| `@types/react-dom` | `^19` | React DOM type definitions |

### Dependency Installation

To install dependencies:

```bash
npm install
```

This command:
- Reads [package.json:11-42]()
- Installs exact versions from [package-lock.json]()
- Creates/updates `node_modules/` directory
- Verifies package integrity

**Sources:** [package.json:11-42]()

---

## Development Toolchain Integration

### Complete Development Pipeline

```mermaid
graph TD
    srcFiles["Source Files<br/>src/**/*.tsx, src/**/*.ts"]
    cssFiles["CSS Files<br/>src/app/globals.css"]
    svgFiles["SVG Assets<br/>*.svg"]
    
    typescript["TypeScript Compiler<br/>tsc"]
    postcss["PostCSS Processor<br/>postcss.config.mjs"]
    svgrLoader["SVGR Loader<br/>@svgr/webpack"]
    eslint["ESLint<br/>eslint.config.mjs"]
    
    turbopackDev["Turbopack<br/>Development Bundler"]
    webpackProd["Webpack<br/>Production Bundler"]
    
    nextDir[".next/ Directory<br/>Compiled Output"]
    
    devServer["Development Server<br/>localhost:3000"]
    prodServer["Production Server<br/>next start"]
    
    srcFiles --> typescript
    srcFiles --> eslint
    cssFiles --> postcss
    svgFiles --> svgrLoader
    
    typescript --> turbopackDev
    postcss --> turbopackDev
    svgrLoader --> turbopackDev
    eslint -.->|Validation| srcFiles
    
    typescript --> webpackProd
    postcss --> webpackProd
    svgrLoader --> webpackProd
    
    turbopackDev --> devServer
    webpackProd --> nextDir
    nextDir --> prodServer
```

**Diagram: Development Toolchain Flow** - Shows how source files are processed through various tools to produce development and production outputs.

**Sources:** [package.json:5-10](), [next.config.ts:19-37]()

---

## Development vs Production Differences

### Configuration Variations

| Aspect | Development | Production |
|--------|-------------|------------|
| Bundler | Turbopack (via `--turbopack` flag) | Webpack |
| CSP | No `upgrade-insecure-requests` | Includes `upgrade-insecure-requests` |
| HSTS | Not applied | Applied with 1-year max-age |
| Minification | Disabled for faster rebuilds | Enabled for smaller bundles |
| Source Maps | Enabled for debugging | Disabled or limited |
| Hot Reload | Enabled (HMR) | Not applicable |
| Environment | `NODE_ENV=development` | `NODE_ENV=production` |

### Environment Variable Behavior

The `IS_DEV` constant [next.config.ts:3]() controls conditional configuration:

```typescript
const IS_DEV = process.env.NODE_ENV !== "production";
```

This affects:
1. **CSP Header** [next.config.ts:13](): `upgrade-insecure-requests` directive is excluded in development
2. **HSTS Header** [next.config.ts:46-51](): Only applied in production

### Bundle Optimization

Production builds apply several optimizations not present in development:

- **Code Splitting**: Automatic splitting of JavaScript bundles
- **Tree Shaking**: Removal of unused exports
- **Minification**: Compression of JavaScript and CSS
- **Image Optimization**: Automatic image format conversion and resizing
- **Font Optimization**: Automatic font file optimization

**Sources:** [next.config.ts:3-54](), [package.json:6-8]()

---

## SVG Asset Handling

The project uses `@svgr/webpack` to transform SVG files into React components, configured identically for both Turbopack and Webpack.

### Turbopack SVG Configuration

[next.config.ts:19-26]() defines the Turbopack rule:

```typescript
turbopack: {
  rules: {
    "*.svg": {
      loaders: ["@svgr/webpack"],
      as: "*.js",
    },
  },
}
```

### Webpack SVG Configuration

[next.config.ts:30-37]() mirrors the Turbopack configuration:

```typescript
webpack(config) {
  config.module.rules.push({
    test: /\.svg$/i,
    issuer: /\.[jt]sx?$/,
    use: ["@svgr/webpack"],
  });
  return config;
}
```

### Usage Pattern

SVG files can be imported as React components:

```typescript
import IconName from './path/to/icon.svg';

// Use as component
<IconName className="w-6 h-6" />
```

The type definitions for SVG imports are provided in `global.d.ts` (see [Type Definitions](#4.4)).

**Sources:** [next.config.ts:19-37]()

---

## Code Quality and Validation

### ESLint Integration

ESLint is configured through `eslint.config.mjs` and executed via the npm script:

```bash
npm run lint
```

The configuration includes:
- Next.js-specific rules from `eslint-config-next`
- Flat config format support via `@eslint/eslintrc`
- TypeScript-aware linting

### Type Checking

TypeScript is configured through `tsconfig.json` (inferred from project structure). Type checking occurs:
- Automatically during development in IDEs
- During build process via `next build`
- Can be run manually: `npx tsc --noEmit`

### Pre-deployment Checklist

Before deploying changes:

1. **Lint validation**: `npm run lint`
2. **Type checking**: Ensure no TypeScript errors
3. **Build test**: `npm run build` succeeds
4. **Production test**: `npm run start` and manual testing

**Sources:** [package.json:9](), [next.config.ts:38-54]()

---

## Build Output Structure

The build process generates the `.next/` directory with the following structure:

```
.next/
├── cache/              # Build cache for faster rebuilds
├── server/             # Server-side code
│   ├── app/           # App router pages and API routes
│   └── chunks/        # Shared server chunks
├── static/            # Static assets with content hashes
│   ├── chunks/        # JavaScript chunks
│   └── css/           # Compiled CSS files
└── types/             # Generated TypeScript types
```

This output:
- Is generated by `npm run build`
- Should be excluded from version control (see [Version Control](#4.5))
- Is served by `npm run start`
- Is automatically deployed on Vercel platform

**Sources:** [next.config.ts:18-57]()

---

## Related Documentation

- For linting configuration details, see [Code Style and Linting](#4.1)
- For build process internals, see [Build Process](#4.2)
- For styling system configuration, see [Styling System](#4.3)
- For TypeScript type definitions, see [Type Definitions](#4.4)
- For version control practices, see [Version Control](#4.5)
- For deployment procedures, see [Getting Started](#2)
- For security header implementation, see [Security Considerations](#5)

---

# Page: Code Style and Linting

# Code Style and Linting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [eslint.config.mjs](eslint.config.mjs)

</details>



This document details the code style guidelines and linting configuration used in the OpenAI.fm project. It covers the ESLint setup, configuration approach, and workflow for enforcing code quality standards throughout the codebase. For information about the build process that incorporates these linting checks, see [Build Process](#4.2).

## Overview

The OpenAI.fm project enforces code style and quality through a combination of ESLint and TypeScript type checking. The configuration is designed to align with Next.js best practices, ensuring consistency and preventing common errors before they reach production.

## ESLint Configuration

The project uses ESLint with the new flat configuration format, which is defined in the root directory.

```mermaid
flowchart TD
    subgraph "Linting Configuration"
        Config["eslint.config.mjs"]
        Config --> NextCore["next/core-web-vitals"]
        Config --> NextTS["next/typescript"]
    end
    
    subgraph "Dependencies"
        ESLint["eslint@^9"]
        NextConfig["eslint-config-next@15.2.2"] 
        Compat["@eslint/eslintrc@^3"]
    end
    
    ESLint --> Config
    NextConfig --> NextCore
    NextConfig --> NextTS
    Compat --> Config
```

Sources: [eslint.config.mjs](), [package.json:32-41]()

### Configuration Details

The ESLint configuration extends two preset configurations from the Next.js ecosystem:

1. `next/core-web-vitals`: Includes rules optimized for Next.js applications with a focus on Core Web Vitals performance metrics
2. `next/typescript`: Provides TypeScript-specific linting rules

The configuration file uses the `@eslint/eslintrc` compatibility layer to incorporate these traditional configurations into the modern flat config system:

```mermaid
flowchart LR
    FlatCompat["FlatCompat"] -->|"Enables compatibility"| Traditional["Traditional ESLint configs"]
    Traditional -->|"Converted to"| FlatConfig["Flat configuration array"]
    FlatConfig -->|"Exported as"| ESLintConfig["ESLint configuration"]
```

Sources: [eslint.config.mjs:1-16]()

## Running Linting Checks

Developers can verify code quality by running the following command:

```
npm run lint
```

This command runs Next.js's built-in linting command, which checks all JavaScript and TypeScript files in the project according to the configuration.

Sources: [package.json:9]()

## TypeScript Integration

The project uses TypeScript throughout the codebase. The linting system works in conjunction with TypeScript to provide comprehensive code quality checks:

1. ESLint handles code style, common errors, and TypeScript-specific issues through the Next.js presets
2. TypeScript's compiler performs static type checking

The project is configured to ignore TypeScript build artifacts (`*.tsbuildinfo` and `next-env.d.ts`) in version control.

Sources: [package.json:35-41](), [.gitignore:40-42]()

## Linting in Development Workflow

The following diagram illustrates how linting integrates into the development workflow:

```mermaid
flowchart LR
    Dev["Local Development
    (npm run dev)"] --> Code["Code Changes"]
    
    Code --> IDELint["IDE Linting
    (Real-time feedback)"]
    IDELint --> |"Issues Found"| Fix["Fix Issues"]
    
    Code --> ManualLint["Manual Lint Check
    (npm run lint)"]
    ManualLint --> |"Failed"| Fix
    Fix --> Code
    
    ManualLint --> |"Passed"| Commit["Commit Code"]
    Commit --> Build["Build Process
    (npm run build)"]
```

Sources: [package.json:5-10]()

## Linting Architecture

The linting system architecture consists of several interconnected components:

```mermaid
flowchart TD
    subgraph "Developer Tools"
        RunLint["npm run lint"]
        IDE["IDE/Editor Integration"]
    end
    
    subgraph "Linting Engine"
        ESLint["ESLint Process"]
        NextLint["Next.js Lint Command"]
    end
    
    subgraph "Configuration"
        ESLintConfig["eslint.config.mjs"]
        Presets["Next.js Preset Rules"]
    end
    
    subgraph "Source Files"
        JS[".js files"]
        TS[".ts files"]
        TSX[".tsx files"]
    end
    
    RunLint --> NextLint
    IDE --> ESLint
    NextLint --> ESLint
    ESLint --> ESLintConfig
    ESLintConfig --> Presets
    Presets --> |"Applied to"| JS
    Presets --> |"Applied to"| TS
    Presets --> |"Applied to"| TSX
```

Sources: [eslint.config.mjs](), [package.json:5-10]()

## Code Style Guidelines

The project follows Next.js and React best practices through the extended configurations. While there are no custom rules defined beyond the Next.js presets, the following style guidelines are enforced:

| Category | Guidelines |
|----------|------------|
| **JavaScript/TypeScript** | ES6+ syntax, TypeScript type safety |
| **React Components** | Function components with hooks, proper prop typing |
| **Imports/Exports** | Proper module imports, no unused imports |
| **Performance** | Following Core Web Vitals best practices |
| **Accessibility** | React accessibility guidelines via Next.js rules |

Sources: [eslint.config.mjs:12-14]()

## Best Practices for Developers

To maintain code quality when working on the OpenAI.fm codebase:

1. **Configure your IDE** with ESLint integration for real-time feedback
2. **Run linting before commits** using `npm run lint`
3. **Address all linting warnings** as well as errors
4. **Verify TypeScript types** are correctly defined for all code

Sources: [package.json:9]()

## Example Linting Workflow

A typical workflow for a developer adding new features to the codebase:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant IDE as "IDE/Editor"
    participant Lint as "npm run lint"
    participant Git as "Version Control"
    
    Dev->>IDE: Edit code
    IDE->>Dev: Real-time linting feedback
    Dev->>Dev: Address IDE warnings
    Dev->>Lint: Run npm run lint
    Lint->>Dev: Report remaining issues
    Dev->>Dev: Fix reported issues
    Dev->>Lint: Re-run npm run lint
    Lint->>Dev: Confirm passing status
    Dev->>Git: Commit changes
```

Sources: [package.json:5-10]()

By adhering to these standards and utilizing the linting tools, the OpenAI.fm team maintains code quality and consistency throughout the project.

---

# Page: Build Process

# Build Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next.config.ts](next.config.ts)
- [package.json](package.json)
- [postcss.config.mjs](postcss.config.mjs)

</details>



This document details the build process for OpenAI.fm, explaining how the application is configured, built, and deployed in both development and production environments. It covers Next.js configuration, Turbopack integration, CSS processing, and asset handling. For information about code style and linting practices, see [Code Style and Linting](#4.1).

## Build System Overview

The OpenAI.fm application uses Next.js as its core framework with different build tools for development and production environments. Development builds leverage Turbopack for faster refresh times, while production builds use Webpack for optimization.

```mermaid
flowchart TD
    subgraph "Development Build"
        devCmd["npm run dev"] --> turbo["Turbopack"]
        turbo --> devServer["Next.js Dev Server"]
        devServer --> hotReload["Hot Module Replacement"]
    end
    
    subgraph "Production Build"
        buildCmd["npm run build"] --> webpack["Webpack"]
        webpack --> optimize["Optimization & Bundling"]
        optimize --> output["Static & Server Assets"]
        startCmd["npm run start"] --> serve["Next.js Server"]
        output --> serve
    end
    
    subgraph "Configuration"
        next["next.config.ts"]
        postcss["postcss.config.mjs"]
        pkg["package.json scripts"]
    end
    
    next --> turbo
    next --> webpack
    postcss --> turbo
    postcss --> webpack
    pkg --> devCmd
    pkg --> buildCmd
    pkg --> startCmd
```

Sources: [package.json:5-10](), [next.config.ts:18-37]()

## Build Scripts

The application defines the following build-related scripts in package.json:

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `next dev --turbopack` | Starts development server with Turbopack |
| `build` | `next build` | Creates production-optimized build |
| `start` | `next start` | Serves production build |
| `lint` | `next lint` | Runs ESLint for code quality checks |

Sources: [package.json:5-10]()

## Development Build Process

The development build is optimized for rapid iteration with hot module replacement.

```mermaid
flowchart LR
    dev["npm run dev"] --> nextDev["next dev --turbopack"]
    nextDev --> devServer["Development Server"]
    
    subgraph "Configuration Applied"
        turboRules["Turbopack Rules"]
        devCSP["Development CSP"]
        svgTransform["SVG Transformation"]
    end
    
    turboRules --> devServer
    devCSP --> devServer
    svgTransform --> devServer
```

Sources: [package.json:6](), [next.config.ts:19-26]()

### Turbopack Configuration

Turbopack is explicitly enabled in the development command and configured in `next.config.ts`. It includes custom rules for handling SVG files:

```mermaid
flowchart LR
    svgFile["*.svg files"] --> svgrLoader["@svgr/webpack loader"]
    svgrLoader --> jsComponent["React Components"]
    
    subgraph "next.config.ts turbopack rules"
        rule["*.svg rule"]
        loader["loaders: '@svgr/webpack'"]
        output["as: '*.js'"]
    end
    
    rule --> svgFile
    loader --> svgrLoader
    output --> jsComponent
```

Sources: [next.config.ts:19-26]()

## Production Build Process

The production build process creates optimized assets for deployment.

```mermaid
flowchart TD
    build["npm run build"] --> nextBuild["next build"]
    nextBuild --> webpack["Webpack Compilation"]
    
    webpack --> jsBundle["JavaScript Bundling"]
    webpack --> cssBundle["CSS Processing"]
    webpack --> svgProc["SVG Transformation"]
    
    jsBundle --> optimize["Optimization"]
    cssBundle --> optimize
    svgProc --> optimize
    
    optimize --> output["Production Build Output"]
    
    start["npm run start"] --> server["Production Server"]
    output --> server
    
    subgraph "Configuration Applied"
        webpackConfig["webpack() in next.config.ts"]
        postcssConfig["postcss.config.mjs"]
        securityHeaders["Production Security Headers"]
    end
    
    webpackConfig --> webpack
    postcssConfig --> cssBundle
    securityHeaders --> server
```

Sources: [package.json:7-8](), [next.config.ts:30-37](), [next.config.ts:38-54]()

### Webpack Configuration

For production builds, webpack is configured to handle SVG files similarly to Turbopack:

```mermaid
flowchart LR
    webpack["webpack() function"] --> configMod["config.module.rules.push"]
    configMod --> svgRule["test: /\.svg$/i"]
    svgRule --> jsxIssuer["issuer: /\.[jt]sx?$/"]
    jsxIssuer --> svgrLoader["use: '@svgr/webpack'"]
```

Sources: [next.config.ts:30-37]()

## CSS Processing

CSS processing is handled through PostCSS with Tailwind CSS integration.

```mermaid
flowchart LR
    cssFiles["CSS Files"] --> postcss["PostCSS"]
    postcss --> tailwind["@tailwindcss/postcss Plugin"]
    tailwind --> processedCSS["Processed CSS"]
    
    subgraph "postcss.config.mjs"
        plugins["plugins: '@tailwindcss/postcss'"]
    end
    
    plugins --> tailwind
```

Sources: [postcss.config.mjs:1-5]()

## SVG Processing

SVG files are processed consistently in both development and production environments to transform them into React components.

```mermaid
flowchart LR
    svg["SVG Files"] --> svgrWebpack["@svgr/webpack Loader"]
    svgrWebpack --> jsxComponent["React Components"]
    
    subgraph "Environment-specific Configuration"
        turbopackConfig["Turbopack Rules (Dev)"]
        webpackConfig["Webpack Rules (Prod)"]
    end
    
    turbopackConfig --> svgrWebpack
    webpackConfig --> svgrWebpack
```

Sources: [next.config.ts:19-26](), [next.config.ts:30-37]()

## Security Headers Configuration

Security headers are configured as part of the build process and differ between development and production environments.

```mermaid
flowchart TD
    nextConfig["next.config.ts"] --> headers["headers() function"]
    headers --> csp["Content-Security-Policy"]
    
    isDevCheck{"IS_DEV?"} --> |"Yes"| devHeaders["Development Headers"]
    isDevCheck --> |"No"| prodHeaders["Production Headers"]
    
    prodHeaders --> hsts["Strict-Transport-Security"]
    prodHeaders --> upgradeInsecure["upgrade-insecure-requests CSP directive"]
    
    csp --> allRoutes["Applied to /(.*) routes"]
    hsts --> allRoutes
```

Sources: [next.config.ts:5-16](), [next.config.ts:38-54]()

### Content Security Policy

A Content Security Policy is defined to enhance security by restricting which resources can be loaded:

```
default-src 'self';
script-src 'self' 'unsafe-eval' 'unsafe-inline';
connect-src 'self';
style-src 'self' 'unsafe-inline';
img-src 'self';
object-src 'none';
frame-ancestors 'none';
```

In production, an additional `upgrade-insecure-requests` directive is added.

Sources: [next.config.ts:5-16]()

## Environment-Based Configuration

The build process detects the environment to apply different configurations:

```mermaid
flowchart LR
    nodeEnv["process.env.NODE_ENV"] --> isDevCheck{"!== 'production'?"}
    
    isDevCheck --> |"Yes"| devEnv["IS_DEV = true"]
    isDevCheck --> |"No"| prodEnv["IS_DEV = false"]
    
    devEnv --> devConfig["Development Configuration:
    - No HSTS header
    - No upgrade-insecure-requests"]
    
    prodEnv --> prodConfig["Production Configuration:
    - HSTS header added
    - upgrade-insecure-requests added"]
```

Sources: [next.config.ts:3](), [next.config.ts:13](), [next.config.ts:46-51]()

## Build Configuration Files

The build process is controlled by several configuration files:

| File | Purpose |
|------|---------|
| `next.config.ts` | Configures Next.js, Turbopack, Webpack, and security headers |
| `postcss.config.mjs` | Configures CSS processing with Tailwind CSS |
| `package.json` | Defines build scripts and dependencies |

Sources: [next.config.ts](), [postcss.config.mjs](), [package.json]()

## Developer Experience Features

The build system includes features to enhance developer experience:

1. Development indicators are disabled (`devIndicators: false`) to provide a cleaner interface during development
2. Turbopack is used for faster refresh times in development
3. Hot Module Replacement for immediate feedback during development

Sources: [next.config.ts:27](), [package.json:6]()

---

# Page: Styling System

# Styling System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [postcss.config.mjs](postcss.config.mjs)
- [src/app/globals.css](src/app/globals.css)

</details>



## Purpose and Scope

This document describes the styling architecture for OpenAI.fm, which uses TailwindCSS integrated through PostCSS. The system defines a custom theming layer using CSS custom properties and TailwindCSS's `@theme` directive. This page covers the configuration, CSS variable system, global styles, and the build-time processing pipeline.

For information about the build process that compiles these styles, see [Build Process](#4.2). For the overall component architecture that consumes these styles, see [Frontend Components](#3.2).

---

## PostCSS Configuration

The styling system is configured through [postcss.config.mjs:1-5](), which defines a minimal PostCSS pipeline with a single plugin:

```javascript
plugins: ["@tailwindcss/postcss"]
```

This plugin handles the new TailwindCSS v4 CSS-first configuration approach, where TailwindCSS directives are written directly in CSS files rather than in a separate JavaScript configuration file. The PostCSS processor transforms the TailwindCSS-specific syntax (such as `@import "tailwindcss"` and `@theme`) into standard CSS.

**Sources:** [postcss.config.mjs:1-5]()

---

## TailwindCSS Integration

### Import Directive

The entry point for TailwindCSS is at the top of [src/app/globals.css:1]():

```css
@import "tailwindcss";
```

This single directive imports the entire TailwindCSS framework, including all utility classes, the preflight base styles, and the theme system. During the build process, PostCSS expands this import into the complete TailwindCSS stylesheet.

**Sources:** [src/app/globals.css:1]()

---

## CSS Custom Properties and Theming

The styling system defines two categories of CSS custom properties: **root-level variables** for semantic color values and **TailwindCSS theme variables** for exposing values to the utility class system.

### Root Variables

Root-level CSS custom properties are defined in [src/app/globals.css:3-8]():

| Variable | Value | Purpose |
|----------|-------|---------|
| `--background` | `#ececec` | Primary background color |
| `--foreground` | `#222` | Primary text color |
| `--primary` | `#ff4a00` | Brand accent color |
| `--page-max-width` | `1300px` | Maximum page width constraint |

These variables establish the semantic color palette and layout constraints. They are referenced by TailwindCSS theme variables and can also be used directly in component styles.

### Theme Variables - Inline

The `@theme inline` directive in [src/app/globals.css:10-17]() defines color tokens that are exposed to TailwindCSS utilities as CSS custom properties:

| Theme Variable | Value | Generated Utilities |
|----------------|-------|---------------------|
| `--color-background` | `var(--background)` | `bg-background`, `text-background` |
| `--color-foreground` | `var(--foreground)` | `bg-foreground`, `text-foreground` |
| `--color-primary` | `var(--primary)` | `bg-primary`, `text-primary` |
| `--color-screen` | `#f3f3f3` | `bg-screen`, `text-screen` |
| `--color-black-10` | `rgba(0, 0, 0, 0.1)` | `bg-black-10`, `text-black-10` |
| `--color-black-50` | `rgba(0, 0, 0, 0.5)` | `bg-black-50`, `text-black-50` |

The `inline` keyword indicates these values are kept as CSS custom properties in the generated output, allowing for dynamic runtime changes.

### Theme Variables - Static

The `@theme static` directive in [src/app/globals.css:19-31]() defines design tokens that are compiled into static values:

**Border Radius Scale:**
| Variable | Value |
|----------|-------|
| `--radius-xs` | `0.125rem` (2px) |
| `--radius-sm` | `0.25rem` (4px) |
| `--radius-md` | `0.375rem` (6px) |
| `--radius-lg` | `0.5rem` (8px) |
| `--radius-xl` | `0.75rem` (12px) |
| `--radius-2xl` | `1rem` (16px) |
| `--radius-3xl` | `1.5rem` (24px) |
| `--radius-4xl` | `2rem` (32px) |

**Shadow Definitions:**
| Variable | Value | Usage |
|----------|-------|-------|
| `--shadow-textarea` | Inset multi-layer shadow | Textarea input styling |

The `static` keyword indicates these values are inlined directly into utility classes at build time, resulting in smaller CSS bundles and better performance.

**Sources:** [src/app/globals.css:3-31]()

---

## Style Processing Pipeline

```mermaid
graph LR
    subgraph "Source Files"
        GlobalsCSS["globals.css<br/>• @import tailwindcss<br/>• :root variables<br/>• @theme directives"]
        ComponentTSX["Component .tsx files<br/>• className props<br/>• TailwindCSS utilities"]
    end
    
    subgraph "Build Configuration"
        PostCSSConfig["postcss.config.mjs<br/>@tailwindcss/postcss"]
    end
    
    subgraph "PostCSS Processing"
        TailwindPlugin["TailwindCSS Plugin<br/>• Parse @import<br/>• Parse @theme<br/>• Generate utilities<br/>• Apply preflight"]
        CSSTransform["CSS Transformation<br/>• Expand directives<br/>• Inline static values<br/>• Preserve inline vars"]
    end
    
    subgraph "Output"
        CompiledCSS["Compiled CSS<br/>• Preflight base styles<br/>• Utility classes<br/>• Custom properties<br/>• Global styles"]
    end
    
    subgraph "Runtime"
        Browser["Browser Rendering<br/>• Apply styles<br/>• Resolve CSS variables<br/>• Render components"]
    end
    
    GlobalsCSS --> TailwindPlugin
    PostCSSConfig --> TailwindPlugin
    ComponentTSX -.->|"Referenced by"| TailwindPlugin
    TailwindPlugin --> CSSTransform
    CSSTransform --> CompiledCSS
    CompiledCSS --> Browser
```

**Process Flow:**

1. **Source Parsing**: PostCSS reads [src/app/globals.css:1-56]() and detects the `@import "tailwindcss"` directive
2. **Plugin Execution**: The `@tailwindcss/postcss` plugin processes the TailwindCSS directives
3. **Theme Processing**: 
   - `@theme inline` variables are preserved as CSS custom properties
   - `@theme static` variables are compiled into static utility classes
4. **Utility Generation**: TailwindCSS generates utility classes based on theme values (e.g., `bg-primary`, `rounded-xl`)
5. **CSS Output**: The compiled CSS is injected into the application

**Sources:** [postcss.config.mjs:1-5](), [src/app/globals.css:1-31]()

---

## Global Base Styles

### Typography Configuration

The base HTML font configuration is defined in [src/app/globals.css:33-36]():

```css
html {
  font-size: 14px;
  line-height: 130%;
}
```

This establishes a **14px base font size** (smaller than the browser default of 16px) and a tight **130% line height** for compact text rendering. All `rem` units throughout the application are relative to this 14px base.

### Body Styling with Responsive Variants

The body element styling in [src/app/globals.css:38-50]() demonstrates TailwindCSS's `@variant` directive for responsive design:

```css
body {
  background-color: var(--background);
  color: var(--foreground);

  @variant sm {
    background-image: linear-gradient(
      to bottom right,
      #f8f8f8,
      var(--background) 20%
    );
    background-repeat: no-repeat;
  }
}
```

**Default (Mobile)**: Solid background color using `--background`

**Small screens and above**: Gradient background from `#f8f8f8` to `var(--background)` at 20%, creating a subtle diagonal fade effect

The `@variant sm` directive is TailwindCSS v4's syntax for applying styles at the `sm` breakpoint and above, equivalent to a `min-width` media query.

### SVG Normalization

[src/app/globals.css:52-55]() applies global SVG normalization:

```css
svg {
  display: block;
  flex-shrink: 0;
}
```

This ensures SVG elements:
- Render as block elements (avoiding inline spacing issues)
- Do not shrink in flex containers (`flex-shrink: 0`)

**Sources:** [src/app/globals.css:33-55]()

---

## Theme Architecture Diagram

```mermaid
graph TB
    subgraph "CSS Custom Properties Layer"
        RootVars[":root<br/>--background: #ececec<br/>--foreground: #222<br/>--primary: #ff4a00<br/>--page-max-width: 1300px"]
    end
    
    subgraph "TailwindCSS Theme Layer"
        InlineTheme["@theme inline<br/>--color-background<br/>--color-foreground<br/>--color-primary<br/>--color-screen<br/>--color-black-10<br/>--color-black-50"]
        StaticTheme["@theme static<br/>--radius-xs to --radius-4xl<br/>--shadow-textarea"]
    end
    
    subgraph "Generated Utilities"
        ColorUtils["Color Utilities<br/>bg-background<br/>text-foreground<br/>bg-primary<br/>bg-screen<br/>bg-black-10<br/>text-black-50"]
        RadiusUtils["Radius Utilities<br/>rounded-xs<br/>rounded-sm<br/>rounded-md<br/>rounded-lg<br/>rounded-xl<br/>rounded-2xl<br/>rounded-3xl<br/>rounded-4xl"]
        ShadowUtils["Shadow Utilities<br/>shadow-textarea"]
    end
    
    subgraph "Component Consumption"
        PlayButton["PlayButton.tsx<br/>className='bg-primary'"]
        Textarea["Textarea elements<br/>className='shadow-textarea rounded-md'"]
        OtherComponents["Other components<br/>Use utility classes"]
    end
    
    RootVars -->|"Referenced by"| InlineTheme
    InlineTheme -->|"Generates runtime"| ColorUtils
    StaticTheme -->|"Generates static"| RadiusUtils
    StaticTheme -->|"Generates static"| ShadowUtils
    
    ColorUtils --> PlayButton
    ColorUtils --> OtherComponents
    RadiusUtils --> Textarea
    RadiusUtils --> OtherComponents
    ShadowUtils --> Textarea
```

This diagram illustrates the three-layer theming architecture:

1. **CSS Custom Properties**: Root-level semantic variables
2. **TailwindCSS Theme Layer**: `@theme` directives that map to utility classes
3. **Generated Utilities**: The actual CSS classes consumed by components

The `inline` theme variables maintain the CSS custom property chain (allowing runtime theming), while `static` theme variables compile to fixed values (optimizing bundle size).

**Sources:** [src/app/globals.css:3-31]()

---

## Component Styling Workflow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant TSX as "Component .tsx"
    participant Tailwind as "TailwindCSS Engine"
    participant GlobalCSS as "globals.css"
    participant Browser as "Browser"
    
    Dev->>TSX: "Write className='bg-primary rounded-xl'"
    Dev->>GlobalCSS: "Define --color-primary<br/>Define --radius-xl"
    
    Note over TSX,GlobalCSS: Build Time
    
    TSX->>Tailwind: "Parse className attributes"
    GlobalCSS->>Tailwind: "Parse @theme directives"
    Tailwind->>Tailwind: "Generate utility classes<br/>.bg-primary { background-color: var(--color-primary) }<br/>.rounded-xl { border-radius: 0.75rem }"
    
    Note over Tailwind,Browser: Runtime
    
    Tailwind->>Browser: "Inject compiled CSS"
    TSX->>Browser: "Render HTML with classes"
    Browser->>Browser: "Apply styles<br/>Resolve CSS variables"
    Browser->>Browser: "Render UI"
```

**Workflow Steps:**

1. **Development**: Developer writes React components with `className` props using TailwindCSS utility classes
2. **Build Time**:
   - TailwindCSS scans all `.tsx` files for class usage
   - Processes `@theme` directives in [src/app/globals.css:10-31]()
   - Generates only the utility classes that are actually used (tree-shaking)
3. **Runtime**:
   - Browser loads the compiled CSS
   - Inline theme variables (like `--color-primary`) are resolved at runtime
   - Static theme values (like border radius) are already compiled into the CSS

**Sources:** [src/app/globals.css:1-56](), [postcss.config.mjs:1-5]()

---

## Styling System Integration Points

### Root Layout

The global stylesheet is imported in the root layout at [src/app/layout.tsx]() (referenced in Diagram 4), making all styles available throughout the application.

### Component Usage

Components throughout the codebase use TailwindCSS utilities. For example:
- **PlayButton**: Uses `bg-primary` for brand-colored buttons
- **ShareButton**: Uses radius utilities like `rounded-xl`
- **Input elements**: Use `shadow-textarea` for inset shadow effects

The styling system provides a **utility-first** approach where components compose styles from pre-generated classes rather than writing custom CSS.

### Responsive Design

The system supports TailwindCSS's responsive modifier syntax. The `@variant sm` in [src/app/globals.css:42-49]() demonstrates how breakpoint-specific styles are applied using the new v4 syntax.

**Sources:** [src/app/globals.css:1-56]()

---

## Key Design Decisions

### TailwindCSS v4 CSS-First Approach

The system uses TailwindCSS v4's new CSS-first configuration, where theme customization happens in CSS files using `@theme` directives rather than in a JavaScript configuration file. This approach:
- Reduces build complexity (no separate `tailwind.config.js`)
- Leverages native CSS custom properties
- Improves IDE autocomplete and type safety

### Inline vs Static Theme Values

The system strategically separates theme values:
- **Inline** (`@theme inline`): Color values that may need runtime theming
- **Static** (`@theme static`): Fixed design tokens (spacing, shadows) for better performance

### Minimal PostCSS Configuration

[postcss.config.mjs:1-5]() defines only a single plugin, keeping the build pipeline simple and reducing configuration overhead.

**Sources:** [postcss.config.mjs:1-5](), [src/app/globals.css:10-31]()

---

## Summary

The OpenAI.fm styling system is built on:

1. **TailwindCSS v4** integrated via [postcss.config.mjs:1-5]()
2. **CSS Custom Properties** for theming defined in [src/app/globals.css:3-8]()
3. **`@theme` Directives** for generating utility classes from [src/app/globals.css:10-31]()
4. **Global Base Styles** for typography and layout from [src/app/globals.css:33-55]()
5. **Utility-First Component Styling** where components compose pre-generated classes

This architecture provides a maintainable, performant styling system with clear separation between semantic design tokens and generated utility classes.

**Sources:** [postcss.config.mjs:1-5](), [src/app/globals.css:1-56]()

---

# Page: Type Definitions

# Type Definitions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [global.d.ts](global.d.ts)

</details>



## Purpose and Scope

This page documents the custom TypeScript type definitions used in the OpenAI.fm project. These definitions extend TypeScript's type system to support project-specific module imports, particularly SVG files imported as React components through the SVGR loader. The type definitions enable compile-time type checking for assets that are transformed during the build process.

For general TypeScript configuration and compiler settings, see [Build Process](#4.2). For information about how these types are used in React components, see [Frontend Components](#3.2).

**Sources:** [global.d.ts:1-6]()

---

## Overview

The project uses a single custom type definition file (`global.d.ts`) located at the project root. This file provides ambient module declarations that extend TypeScript's module resolution capabilities beyond standard `.ts` and `.tsx` files.

The type definitions serve two critical functions:
1. **Enable SVG imports as React components** - Allows TypeScript to recognize `.svg` files imported via SVGR loader
2. **Provide type safety for build-time transformations** - Ensures type checking for modules transformed by Webpack loaders

**Sources:** [global.d.ts:1-6]()

---

## Type Definition Architecture

The following diagram illustrates how custom type definitions integrate with the TypeScript compilation process:

```mermaid
graph TB
    subgraph "Source Files"
        Component["Component Files<br/>(*.tsx)"]
        SVGFile["SVG Assets<br/>(*.svg)"]
    end
    
    subgraph "Type System"
        GlobalDTS["global.d.ts<br/>Ambient Declarations"]
        TSCompiler["TypeScript Compiler<br/>tsc"]
        TSConfig["tsconfig.json<br/>Compiler Options"]
    end
    
    subgraph "Build Process"
        SVGRLoader["SVGR Loader<br/>(Webpack/Turbopack)"]
        NextBuild["Next.js Build"]
    end
    
    subgraph "Output"
        CompiledJS["Compiled JavaScript<br/>with Type Checking"]
    end
    
    Component -->|"import Logo from './logo.svg'"| TSCompiler
    SVGFile -->|"Referenced by import"| TSCompiler
    
    GlobalDTS -->|"Provides type for<br/>*.svg modules"| TSCompiler
    TSConfig -->|"Configures"| TSCompiler
    
    TSCompiler -->|"Type checks against<br/>module declaration"| NextBuild
    SVGFile -->|"Transformed to<br/>React component"| SVGRLoader
    SVGRLoader -->|"Runtime transformation"| NextBuild
    
    NextBuild --> CompiledJS
```

**Sources:** [global.d.ts:1-6](), [next.config.ts]()

---

## SVG Module Declaration

The primary type definition in the project declares SVG files as importable modules that export React components.

### Declaration Structure

The complete SVG module declaration is defined in [global.d.ts:1-5]():

```typescript
declare module "*.svg" {
  import * as React from "react";
  const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  export default ReactComponent;
}
```

### Type Components

| Component | Purpose | Type |
|-----------|---------|------|
| `declare module` | Creates ambient module declaration for pattern-matched imports | TypeScript keyword |
| `"*.svg"` | Wildcard pattern matching all `.svg` file imports | Module pattern |
| `ReactComponent` | Named constant representing the transformed component | `React.FunctionComponent` |
| `React.SVGProps<SVGSVGElement>` | Props interface for SVG elements | Generic type parameter |
| `export default` | Default export from the module | Export statement |

**Sources:** [global.d.ts:1-5]()

### Type Inference

When a component imports an SVG file, TypeScript uses this declaration to infer types. For example:

```typescript
// Example import in a component
import Logo from "./logo.svg";

// TypeScript infers:
// Logo: React.FunctionComponent<React.SVGProps<SVGSVGElement>>

// Usage is type-safe:
<Logo width={24} height={24} className="icon" />
```

The `React.SVGProps<SVGSVGElement>` type ensures that only valid SVG attributes can be passed as props, providing compile-time type safety for:
- Standard HTML attributes (`id`, `className`, `style`)
- SVG-specific attributes (`width`, `height`, `viewBox`, `fill`, `stroke`)
- React event handlers (`onClick`, `onMouseEnter`, etc.)
- ARIA attributes for accessibility

**Sources:** [global.d.ts:1-5]()

---

## Integration with Build System

The SVG type declaration works in conjunction with the SVGR loader configured in the Next.js build system. The following diagram shows the module resolution flow:

```mermaid
sequenceDiagram
    participant Source as "Component.tsx"
    participant TS as "TypeScript Compiler"
    participant GlobalDTS as "global.d.ts"
    participant Webpack as "Webpack/Turbopack"
    participant SVGR as "SVGR Loader"
    participant Output as "Compiled Output"
    
    Source->>TS: "import Icon from './icon.svg'"
    TS->>TS: "Resolve module type"
    TS->>GlobalDTS: "Match pattern *.svg"
    GlobalDTS-->>TS: "Type: React.FunctionComponent<br/>React.SVGProps<SVGSVGElement>"
    TS->>TS: "Type check usage"
    TS-->>Source: "Type checking complete"
    
    Note over Source,Output: Build Phase
    
    Source->>Webpack: "Build source file"
    Webpack->>SVGR: "Process .svg import"
    SVGR->>SVGR: "Transform SVG to<br/>React component"
    SVGR-->>Webpack: "React component code"
    Webpack->>Output: "Bundle with transformed<br/>SVG component"
```

**Sources:** [global.d.ts:1-5](), [next.config.ts]()

### Build Configuration

The type declaration coordinates with the SVGR loader configuration in `next.config.ts`, which transforms SVG files into React components at build time. The type definition ensures TypeScript understands this transformation will occur, preventing type errors during development.

The two-phase process:
1. **Type checking phase**: TypeScript uses `global.d.ts` to validate imports and usage
2. **Build phase**: Webpack/Turbopack uses SVGR to perform actual transformation

**Sources:** [global.d.ts:1-5](), [next.config.ts]()

---

## Ambient Declaration Scope

The following diagram illustrates the scope and visibility of ambient declarations in `global.d.ts`:

```mermaid
graph TB
    subgraph "Project Root"
        GlobalDTS["global.d.ts<br/>(Ambient Scope)"]
    end
    
    subgraph "src/app/"
        Layout["layout.tsx"]
        Page["page.tsx"]
        Middleware["tmp.middleware.ts"]
    end
    
    subgraph "src/components/"
        PlayButton["PlayButton.tsx"]
        DownloadButton["DownloadButton.tsx"]
        ShareButton["ShareButton.tsx"]
        OtherComponents["Other Components"]
    end
    
    subgraph "src/app/api/"
        Generate["generate/route.ts"]
        Share["share/route.ts"]
    end
    
    subgraph "public/"
        SVGAssets["*.svg files"]
    end
    
    GlobalDTS -.->|"Type definitions<br/>available globally"| Layout
    GlobalDTS -.->|"Type definitions<br/>available globally"| Page
    GlobalDTS -.->|"Type definitions<br/>available globally"| Middleware
    GlobalDTS -.->|"Type definitions<br/>available globally"| PlayButton
    GlobalDTS -.->|"Type definitions<br/>available globally"| DownloadButton
    GlobalDTS -.->|"Type definitions<br/>available globally"| ShareButton
    GlobalDTS -.->|"Type definitions<br/>available globally"| OtherComponents
    GlobalDTS -.->|"Type definitions<br/>available globally"| Generate
    GlobalDTS -.->|"Type definitions<br/>available globally"| Share
    
    Layout -.->|"Can import"| SVGAssets
    Page -.->|"Can import"| SVGAssets
    PlayButton -.->|"Can import"| SVGAssets
    DownloadButton -.->|"Can import"| SVGAssets
    ShareButton -.->|"Can import"| SVGAssets
    OtherComponents -.->|"Can import"| SVGAssets
```

The ambient module declaration in `global.d.ts` is automatically available to all TypeScript files in the project without requiring explicit imports. This is because:

1. **Ambient declarations are global** - TypeScript automatically includes `.d.ts` files in the project root
2. **No import needed** - Types are available in all `.ts` and `.tsx` files
3. **Pattern matching** - The `*.svg` pattern applies to any SVG import path

**Sources:** [global.d.ts:1-5]()

---

## File Location and Discovery

The `global.d.ts` file is located at the project root, which ensures TypeScript automatically discovers and includes it during compilation.

### TypeScript Module Resolution

TypeScript's default configuration includes all `.d.ts` files in the project root. The compiler:
1. Scans the project root for `*.d.ts` files
2. Includes them in the global type scope
3. Uses ambient declarations for module resolution

No explicit `include` or `types` configuration in `tsconfig.json` is required for root-level `.d.ts` files.

**Sources:** [global.d.ts:1-5]()

---

## Usage Patterns

The SVG module declaration enables several usage patterns throughout the codebase.

### Direct Component Usage

SVG files can be imported and used directly as React components:

```typescript
import IconName from "@/path/to/icon.svg";

function MyComponent() {
  return <IconName className="w-6 h-6" />;
}
```

### With TypeScript Props

The type declaration ensures full type safety for SVG attributes:

```typescript
import Logo from "./logo.svg";

// TypeScript validates all props
<Logo
  width={48}              // Valid: number
  height={48}             // Valid: number
  fill="currentColor"     // Valid: string
  className="logo"        // Valid: string
  invalidProp={true}      // Error: Property does not exist
/>
```

### In Component Libraries

The type definition supports importing SVGs in shared component libraries where type safety is critical:

```typescript
import * as React from "react";
import Icon from "./shared-icon.svg";

interface ButtonProps {
  icon?: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  label: string;
}

function Button({ icon: Icon, label }: ButtonProps) {
  return (
    <button>
      {Icon && <Icon className="button-icon" />}
      {label}
    </button>
  );
}
```

**Sources:** [global.d.ts:1-5]()

---

## Type Safety Verification

The type declaration provides compile-time safety that prevents common errors:

### Prevented Error Cases

| Error Scenario | TypeScript Behavior | Benefit |
|----------------|---------------------|---------|
| Importing non-existent SVG | Module not found error | Catches broken imports |
| Invalid SVG props | Type error on attribute | Prevents runtime errors |
| Wrong component type | Type mismatch error | Ensures correct usage |
| Missing SVG file | Build-time error | Early error detection |

### Validation Example

```typescript
// TypeScript prevents these errors at compile time:

import Icon from "./nonexistent.svg";
// Error: Cannot find module './nonexistent.svg'

<Icon invalidAttribute="value" />
// Error: Property 'invalidAttribute' does not exist

const icon: string = Icon;
// Error: Type 'FunctionComponent<SVGProps<SVGSVGElement>>' 
// is not assignable to type 'string'
```

**Sources:** [global.d.ts:1-5]()

---

## Relationship to Build System

The type definition works as part of a coordinated system with Next.js configuration:

```mermaid
graph LR
    subgraph "Type System"
        GlobalDTS["global.d.ts<br/>Type Declaration"]
        TSCompiler["TypeScript Compiler<br/>Type Checking"]
    end
    
    subgraph "Build Configuration"
        NextConfig["next.config.ts<br/>SVGR Loader Config"]
        Webpack["Webpack/Turbopack<br/>Module Bundler"]
    end
    
    subgraph "Development Experience"
        IDE["IDE/Editor<br/>IntelliSense"]
        DevServer["Development Server<br/>Hot Reload"]
    end
    
    GlobalDTS --> TSCompiler
    GlobalDTS --> IDE
    
    NextConfig --> Webpack
    TSCompiler --> DevServer
    Webpack --> DevServer
    
    IDE -.->|"Uses types for"| DevServer
```

This coordination ensures:
- **Development**: IDE provides autocomplete and type checking using `global.d.ts`
- **Type checking**: TypeScript compiler validates imports against type declarations
- **Build time**: Webpack/Turbopack transforms SVGs using SVGR loader
- **Runtime**: Transformed components match declared types exactly

**Sources:** [global.d.ts:1-5](), [next.config.ts]()

---

## Extending Type Definitions

While the current project only requires SVG module declarations, the `global.d.ts` file can be extended to support additional ambient module types.

### Potential Extensions

Additional module declarations can be added for other asset types transformed by Webpack loaders:

```typescript
// Example extensions (not in current codebase)

// Image formats
declare module "*.png" {
  const content: string;
  export default content;
}

// JSON files
declare module "*.json" {
  const value: any;
  export default value;
}

// CSS modules
declare module "*.module.css" {
  const classes: { [key: string]: string };
  export default classes;
}
```

These patterns follow the same structure as the SVG declaration but with different exported types based on how Webpack loaders transform the files.

**Sources:** [global.d.ts:1-5]()

---

## Best Practices

### Maintaining Type Definitions

When working with custom type definitions in this project:

1. **Keep declarations minimal** - Only declare types for build-time transformations
2. **Match loader behavior** - Type declarations should match actual Webpack loader output
3. **Use specific types** - Prefer `React.FunctionComponent<Props>` over `any`
4. **Document transformations** - Comment complex declarations with their purpose
5. **Avoid duplication** - Ambient declarations apply globally; don't redeclare in multiple files

### Verification Steps

To verify type definitions are working correctly:

1. Import an SVG file in a component
2. Check IDE autocomplete shows SVG props
3. Run `npm run build` to verify TypeScript compilation
4. Confirm no type errors during development

**Sources:** [global.d.ts:1-5]()

---

## Summary

The type definitions in OpenAI.fm provide essential TypeScript support for SVG imports transformed by SVGR. The single `global.d.ts` file at the project root:

- Declares `*.svg` imports as React components with type `React.FunctionComponent<React.SVGProps<SVGSVGElement>>`
- Provides compile-time type safety for SVG attributes
- Integrates seamlessly with the Next.js build system and SVGR loader
- Enables IDE features like autocomplete and type checking
- Prevents runtime errors through early compile-time validation

This minimal but crucial type definition enables type-safe usage of SVG assets throughout the application while maintaining full TypeScript compiler support and developer experience.

**Sources:** [global.d.ts:1-6]()

---

# Page: Version Control

# Version Control

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)

</details>



## Purpose and Scope

This document describes version control practices and configuration for the OpenAI.fm project. It covers the `.gitignore` configuration, which determines which files and directories are excluded from Git version control, and explains the rationale behind these exclusions.

For information about environment configuration and secrets management, see [Environment Configuration](#2.2). For information about the build process and generated artifacts, see [Build Process](#4.2).

## Version Control System

OpenAI.fm uses **Git** for version control. The repository is hosted at `https://github.com/openai/openai-fm` and follows standard Git workflows for collaborative development.

**Sources:** Repository context

## Gitignore Configuration

The project's version control exclusions are defined in [.gitignore:1-43](). This file prevents sensitive data, build artifacts, dependencies, and system-specific files from being committed to the repository.

### Ignored File Categories

The following diagram illustrates the major categories of excluded files and their relationships:

```mermaid
graph TD
    GitIgnore[".gitignore"]
    
    subgraph Dependencies["Dependencies (Lines 3-11)"]
        NodeModules["/node_modules"]
        PNP["/.pnp, .pnp.*"]
        Yarn[".yarn/* (with exceptions)"]
    end
    
    subgraph Build["Build Artifacts (Lines 13-21)"]
        Coverage["/coverage"]
        Next["/.next/"]
        Out["/out/"]
        BuildDir["/build"]
    end
    
    subgraph Environment["Environment & Secrets (Lines 33-35)"]
        EnvFiles[".env*"]
        EnvExample["!.env.example (tracked)"]
    end
    
    subgraph System["System & Debug Files (Lines 23-31)"]
        DS_Store[".DS_Store"]
        PEM["*.pem"]
        Logs["npm-debug.log*, yarn-debug.log*, etc."]
        PnpmLog[".pnpm-debug.log*"]
    end
    
    subgraph TypeScript["TypeScript Generated (Lines 40-42)"]
        TSBuildInfo["*.tsbuildinfo"]
        NextEnvDTS["next-env.d.ts"]
    end
    
    subgraph Deployment["Deployment (Lines 37-38)"]
        Vercel[".vercel"]
    end
    
    GitIgnore --> Dependencies
    GitIgnore --> Build
    GitIgnore --> Environment
    GitIgnore --> System
    GitIgnore --> TypeScript
    GitIgnore --> Deployment
```

**Sources:** [.gitignore:1-43]()

### Detailed Exclusion Rules

The following table documents each exclusion pattern and its purpose:

| Line(s) | Pattern | Purpose |
|---------|---------|---------|
| 4 | `/node_modules` | Excludes all npm dependencies installed via `npm install`. These are large, reproducible from `package-lock.json`, and should never be committed. |
| 5-6 | `/.pnp`, `.pnp.*` | Excludes Yarn Plug'n'Play runtime files (not used in this project, but commonly ignored). |
| 7-11 | `.yarn/*` with exceptions | Excludes Yarn cache while preserving patches, plugins, releases, and versions that should be tracked. |
| 14 | `/coverage` | Excludes test coverage reports generated during testing. |
| 17 | `/.next/` | **Critical:** Excludes Next.js build output directory. This contains compiled pages, API routes, and optimized assets generated by the build process described in [Build Process](#4.2). |
| 18 | `/out/` | Excludes static export output directory when using `next export`. |
| 21 | `/build` | Excludes alternative build directories. |
| 24 | `.DS_Store` | Excludes macOS system files that store folder metadata. |
| 25 | `*.pem` | **Security:** Excludes private key files used for SSL/TLS certificates. |
| 28-31 | `*-debug.log*`, `.pnpm-debug.log*` | Excludes debug logs from npm, yarn, and pnpm package managers. |
| 34 | `.env*` | **Security Critical:** Excludes all environment variable files that may contain secrets like `OPENAI_API_KEY` or `POSTGRES_URL`. |
| 35 | `!.env.example` | **Exception:** Tracks `.env.example` as a template showing required variables without actual secrets. See [Environment Configuration](#2.2). |
| 38 | `.vercel` | Excludes Vercel deployment configuration and cache. |
| 41 | `*.tsbuildinfo` | Excludes TypeScript incremental compilation cache files. |
| 42 | `next-env.d.ts` | Excludes Next.js auto-generated TypeScript declarations (regenerated on build). |

**Sources:** [.gitignore:1-43]()

## Version Control Workflow

The following diagram illustrates the workflow of file categorization during development:

```mermaid
flowchart LR
    subgraph Developer["Developer Workspace"]
        SourceCode["Source Files<br/>src/**/*.tsx"]
        ConfigFiles["Configuration<br/>next.config.ts<br/>package.json"]
        EnvLocal[".env.local<br/>(contains secrets)"]
        EnvExample[".env.example<br/>(template)"]
    end
    
    subgraph BuildProcess["Build Process"]
        NPMInstall["npm install"]
        NextBuild["next build"]
    end
    
    subgraph Generated["Generated Artifacts"]
        NodeModules["/node_modules"]
        NextDir["/.next/"]
        TSBuildInfo["*.tsbuildinfo"]
    end
    
    subgraph GitRepo["Git Repository"]
        TrackedFiles["Tracked Files:<br/>• Source code<br/>• Configuration<br/>• .env.example"]
        GitIgnore[".gitignore<br/>(exclusion rules)"]
    end
    
    SourceCode -->|"git add"| TrackedFiles
    ConfigFiles -->|"git add"| TrackedFiles
    EnvExample -->|"git add"| TrackedFiles
    EnvLocal -.->|"blocked by .gitignore"| GitIgnore
    
    NPMInstall --> NodeModules
    NextBuild --> NextDir
    NextBuild --> TSBuildInfo
    
    NodeModules -.->|"blocked by .gitignore"| GitIgnore
    NextDir -.->|"blocked by .gitignore"| GitIgnore
    TSBuildInfo -.->|"blocked by .gitignore"| GitIgnore
```

**Sources:** [.gitignore:1-43](), [package.json](), [next.config.ts]()

## Security-Critical Exclusions

### Environment Variable Files

Lines [.gitignore:34-35]() implement a critical security pattern:

```
.env*
!.env.example
```

This pattern:
1. **Excludes all `.env*` files** - Prevents accidental commits of files like `.env.local` that contain sensitive credentials (`OPENAI_API_KEY`, `POSTGRES_URL`)
2. **Tracks `.env.example`** - Preserves the template that documents required environment variables without exposing actual secrets

This approach is essential for the API routes that depend on secrets:
- [src/app/api/generate/route.ts]() requires `OPENAI_API_KEY` to authenticate with OpenAI's Speech API
- [src/app/api/share/route.ts]() requires `POSTGRES_URL` for database connections

**Sources:** [.gitignore:33-35](), [.env.example](), [src/app/api/generate/route.ts](), [src/app/api/share/route.ts]()

### Private Key Files

Line [.gitignore:25]() excludes `*.pem` files, which commonly contain:
- SSL/TLS private keys
- Authentication certificates
- SSH private keys

These files must never be committed to version control as they provide privileged access to systems and services.

**Sources:** [.gitignore:25]()

## Build Artifact Exclusions

### Next.js Build Output

The [.gitignore:17]() pattern excludes `/.next/`, which is the primary build output directory for Next.js. This directory contains:

| Subdirectory | Contents | Regeneration Source |
|--------------|----------|---------------------|
| `/.next/server/` | Server-rendered pages and API routes | Compiled from `src/app/**/*` |
| `/.next/static/` | Static assets, JS bundles, CSS | Optimized from source files and `public/` |
| `/.next/cache/` | Build cache for faster rebuilds | Generated during build |

These artifacts are:
- **Large** (typically 100MB+)
- **Machine-specific** (contain absolute paths)
- **Reproducible** (regenerated via `npm run build`)
- **Environment-specific** (dev vs. production builds differ)

**Sources:** [.gitignore:17](), [next.config.ts]()

### TypeScript Compilation Cache

Lines [.gitignore:41-42]() exclude TypeScript-generated files:

- `*.tsbuildinfo` - Incremental compilation cache enabling faster rebuilds
- `next-env.d.ts` - Auto-generated Next.js type declarations, regenerated on each build

These files are managed by the TypeScript compiler configured via `tsconfig.json` and should not be tracked.

**Sources:** [.gitignore:40-42]()

## Dependency Exclusions

### Node Modules

Line [.gitignore:4]() excludes `/node_modules`, which contains all npm dependencies. This directory:

- Is **reproducible** from [package-lock.json]() via `npm install`
- Contains **thousands of files** (50,000+ for typical Next.js projects)
- Is **platform-specific** (may contain native binaries)

The deterministic dependency tree is preserved in:
- [package.json]() - Declares direct dependencies and their version ranges
- [package-lock.json]() - Locks exact versions of all transitive dependencies

**Sources:** [.gitignore:4](), [package.json](), [package-lock.json]()

## Best Practices

### What to Commit

✅ **Always commit:**
- Source code: `src/**/*.tsx`, `src/**/*.ts`
- Configuration: `next.config.ts`, `package.json`, `postcss.config.mjs`, `eslint.config.mjs`
- Type declarations: `global.d.ts`
- Static assets: `public/**/*` (excluding generated service worker)
- Environment templates: `.env.example`
- Documentation: `README.md`, wiki pages

### What Never to Commit

❌ **Never commit:**
- Secrets or credentials: `.env.local`, API keys, passwords
- Build artifacts: `/.next/`, `/out/`, `/build`
- Dependencies: `/node_modules`
- Personal files: `.DS_Store`, IDE settings not shared by team
- Debug logs: `npm-debug.log*`, `yarn-error.log*`

### Verification Commands

To verify no ignored files are accidentally staged:

```bash
# Check what would be committed
git status

# Verify .gitignore patterns match correctly
git check-ignore -v <filename>

# List all tracked files
git ls-files
```

**Sources:** [.gitignore:1-43]()

## Relationship to Deployment

The [.gitignore:38]() pattern excludes `.vercel`, a directory created by Vercel CLI that contains:
- Deployment configuration
- Build cache
- Project linking metadata

This directory is local to each developer's machine and deployment environment. Vercel reads configuration from tracked files like `next.config.ts` and `package.json` instead.

**Sources:** [.gitignore:37-38](), [next.config.ts](), [package.json]()

---

# Page: Security Considerations

# Security Considerations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [next.config.ts](next.config.ts)
- [src/app/tmp.middleware.ts](src/app/tmp.middleware.ts)

</details>



## Purpose and Scope

This document covers the security mechanisms implemented in OpenAI.fm to protect against common web vulnerabilities and secure sensitive data. The application implements multiple layers of security including Content Security Policy (CSP), HTTP Strict Transport Security (HSTS), nonce-based script execution controls, and environment-based secrets management.

For information about API authentication and external service integration, see [API Routes](#3.3). For database schema and connection patterns, see [Database Integration](#3.6).

---

## Security Architecture Overview

The application employs a defense-in-depth strategy with security controls implemented at multiple layers:

```mermaid
graph TD
    Request["Incoming HTTP Request"]
    Middleware["middleware()<br/>src/app/tmp.middleware.ts"]
    NonceGen["Nonce Generation<br/>crypto.randomUUID()"]
    CSPMiddleware["CSP Header Injection<br/>nonce-based policy"]
    NextConfig["Next.js Config<br/>next.config.ts"]
    StaticCSP["Static CSP Headers<br/>headers()"]
    HSTS["HSTS Header<br/>Production Only"]
    Pages["Application Pages"]
    API["API Routes"]
    EnvSecrets["Environment Secrets<br/>.env.local"]
    
    Request --> Middleware
    Middleware --> NonceGen
    NonceGen --> CSPMiddleware
    CSPMiddleware --> Pages
    
    Request --> NextConfig
    NextConfig --> StaticCSP
    NextConfig --> HSTS
    StaticCSP --> Pages
    StaticCSP --> API
    HSTS --> Pages
    HSTS --> API
    
    API --> EnvSecrets
    
    Pages -.->|"reads x-nonce header"| NonceGen
```

**Diagram: Multi-Layer Security Architecture**

The security architecture operates at two primary levels:
1. **Request-time security** via middleware that generates unique nonces and applies dynamic CSP
2. **Static security** via Next.js configuration that applies CSP and HSTS headers to all routes

**Sources:** [src/app/tmp.middleware.ts](), [next.config.ts]()

---

## Content Security Policy (CSP)

### Static CSP Configuration

The application defines a baseline CSP in [next.config.ts:5-16]() that applies to all routes. This policy is constructed conditionally based on the environment:

| Directive | Value | Purpose |
|-----------|-------|---------|
| `default-src` | `'self'` | Only load resources from same origin |
| `script-src` | `'self' 'unsafe-eval' 'unsafe-inline'` | Allow same-origin scripts and inline scripts |
| `connect-src` | `'self'` | Restrict fetch/XHR to same origin |
| `style-src` | `'self' 'unsafe-inline'` | Allow same-origin and inline styles |
| `img-src` | `'self'` | Only load images from same origin |
| `object-src` | `'none'` | Block plugins (Flash, Java, etc.) |
| `frame-ancestors` | `'none'` | Prevent clickjacking via iframes |
| `upgrade-insecure-requests` | (production only) | Automatically upgrade HTTP to HTTPS |

The CSP string is constructed in [next.config.ts:5-16]() and applied via the `headers()` function in [next.config.ts:38-54]():

```mermaid
flowchart LR
    BuildCSP["Build CSP Array<br/>next.config.ts:5-16"]
    FilterNull["Filter null values<br/>.filter(Boolean)"]
    JoinString["Join with spaces<br/>.join(' ')"]
    HeadersFunc["headers() function<br/>next.config.ts:38"]
    ApplyAll["Apply to all routes<br/>source: '/(.*)' "]
    
    BuildCSP --> FilterNull
    FilterNull --> JoinString
    JoinString --> HeadersFunc
    HeadersFunc --> ApplyAll
```

**Diagram: Static CSP Construction Pipeline**

The conditional `IS_DEV` check in [next.config.ts:3]() determines whether `upgrade-insecure-requests` is included, allowing HTTP connections during local development.

**Sources:** [next.config.ts:5-16](), [next.config.ts:38-54]()

### Nonce-Based CSP Middleware

A more restrictive nonce-based CSP is applied to page navigations via the middleware in [src/app/tmp.middleware.ts](). This provides stronger protection against XSS attacks by requiring scripts and styles to include a unique nonce attribute.

```mermaid
sequenceDiagram
    participant Browser
    participant Middleware as middleware()<br/>tmp.middleware.ts
    participant Nonce as crypto.randomUUID()
    participant Headers as Request/Response Headers
    participant Page as Next.js Page
    
    Browser->>Middleware: "GET /"
    Middleware->>Nonce: "Generate unique ID"
    Nonce-->>Middleware: "UUID string"
    Middleware->>Middleware: "btoa(UUID)<br/>Base64 encode"
    Middleware->>Middleware: "Build CSP with nonce:<br/>script-src 'self' 'nonce-{nonce}'"
    Middleware->>Headers: "Set x-nonce header"
    Middleware->>Headers: "Set Content-Security-Policy header"
    Middleware->>Page: "Forward request with headers"
    Page-->>Browser: "HTML with nonce in inline scripts"
```

**Diagram: Nonce-Based CSP Request Flow**

The middleware implements the following security enhancements in [src/app/tmp.middleware.ts:9-52]():

1. **Nonce Generation** ([src/app/tmp.middleware.ts:11]()): Uses `crypto.randomUUID()` to generate a cryptographically random value, then Base64-encodes it via `btoa()`.

2. **Strict CSP Policy** ([src/app/tmp.middleware.ts:14-25]()): Constructs a CSP with the following key directives:
   - `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`: Scripts must either be same-origin or include the nonce attribute. The `strict-dynamic` directive allows nonce-authenticated scripts to load additional scripts.
   - `style-src 'self' 'nonce-${nonce}'`: Styles must be same-origin or include the nonce.
   - `img-src 'self' blob: data:`: Allow images from same-origin, blob URLs (for dynamically generated images), and data URIs.

3. **Header Injection** ([src/app/tmp.middleware.ts:32-50]()): The nonce and CSP are attached to both the incoming request headers (`x-nonce` custom header) and outgoing response headers (`Content-Security-Policy` standard header).

4. **Selective Application** ([src/app/tmp.middleware.ts:56-71]()): The middleware only runs for page navigations, excluding:
   - API routes (`/api/*`)
   - Static files (`/_next/static/*`)
   - Image optimization (`/_next/image/*`)
   - Prefetch requests (detected via `next-router-prefetch` header)

**Sources:** [src/app/tmp.middleware.ts:9-72]()

### CSP Comparison Table

| Aspect | Static CSP (next.config.ts) | Nonce-Based CSP (middleware) |
|--------|----------------------------|------------------------------|
| **Applied to** | All routes | Page navigations only |
| **script-src** | `'self' 'unsafe-eval' 'unsafe-inline'` | `'self' 'nonce-{value}' 'strict-dynamic'` |
| **style-src** | `'self' 'unsafe-inline'` | `'self' 'nonce-{value}'` |
| **img-src** | `'self'` | `'self' blob: data:` |
| **Nonce required** | No | Yes |
| **XSS protection** | Basic | Enhanced |
| **Implementation** | [next.config.ts:5-16]() | [src/app/tmp.middleware.ts:14-25]() |

**Sources:** [next.config.ts](), [src/app/tmp.middleware.ts]()

---

## HTTP Strict Transport Security (HSTS)

HSTS headers are configured in [next.config.ts:46-51]() to enforce HTTPS connections in production environments. This prevents protocol downgrade attacks and cookie hijacking.

```mermaid
graph TD
    IsDev{"IS_DEV check<br/>next.config.ts:3"}
    SkipHSTS["Skip HSTS<br/>Development"]
    AddHSTS["Add HSTS Header<br/>next.config.ts:47-50"]
    HeaderConfig["max-age=31536000<br/>includeSubDomains<br/>preload"]
    ApplyToAll["Apply to all routes<br/>source: '/(.*)' "]
    
    IsDev -->|"true"| SkipHSTS
    IsDev -->|"false (production)"| AddHSTS
    AddHSTS --> HeaderConfig
    HeaderConfig --> ApplyToAll
```

**Diagram: HSTS Configuration Logic**

The HSTS header in [next.config.ts:49]() includes three directives:

| Directive | Value | Purpose |
|-----------|-------|---------|
| `max-age` | `31536000` (1 year) | Duration browsers should remember to only use HTTPS |
| `includeSubDomains` | enabled | Apply HSTS to all subdomains |
| `preload` | enabled | Eligible for browser HSTS preload lists |

The HSTS header is only added when `IS_DEV` is false ([next.config.ts:46]()), allowing HTTP connections during local development without browser warnings.

**Sources:** [next.config.ts:3](), [next.config.ts:46-51]()

---

## Environment Secrets Management

Sensitive credentials and API keys are managed via environment variables to prevent hardcoding secrets in the codebase.

```mermaid
graph LR
    EnvExample[".env.example<br/>Template"]
    EnvLocal[".env.local<br/>Actual Secrets"]
    ProcessEnv["process.env<br/>Runtime Access"]
    APIGenerate["API Route<br/>/api/generate"]
    APIShare["API Route<br/>/api/share"]
    OpenAI["OpenAI API"]
    PostgreSQL[("PostgreSQL Database")]
    
    EnvExample -.->|"documents structure"| EnvLocal
    EnvLocal --> ProcessEnv
    ProcessEnv --> APIGenerate
    ProcessEnv --> APIShare
    APIGenerate --> OpenAI
    APIShare --> PostgreSQL
    
    style EnvLocal fill:#f9f9f9
    style EnvExample fill:#f9f9f9
```

**Diagram: Environment Variables Flow**

### Required Secrets

The application requires the following secrets for full functionality:

| Variable | Purpose | Required By | Example Location |
|----------|---------|-------------|------------------|
| `OPENAI_API_KEY` | OpenAI API authentication | `/api/generate` | Not in repo |
| `POSTGRES_URL` | Primary database connection | `/api/share` | [.env.example:1]() |
| `POSTGRES_PRISMA_URL` | Connection pooling | `/api/share` | [.env.example:2]() |
| `POSTGRES_URL_NON_POOLING` | Direct connection | `/api/share` | [.env.example:4]() |

### Environment File Structure

The [.env.example]() file serves as a template documenting all possible PostgreSQL connection string formats:

- **Standard Connection** ([.env.example:1]()): `POSTGRES_URL` with SSL mode required
- **Pooled Connection** ([.env.example:2]()): `POSTGRES_PRISMA_URL` with pgbouncer and connection timeout
- **Non-SSL Connection** ([.env.example:3]()): `POSTGRES_URL_NO_SSL` for development environments
- **Non-Pooling Connection** ([.env.example:4]()): `POSTGRES_URL_NON_POOLING` for direct database access

Additional connection parameters in [.env.example:5-8]() include:
- `POSTGRES_USER`: Database username
- `POSTGRES_HOST`: Database server hostname
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DATABASE`: Database name

### Secret Storage Best Practices

1. **Never commit** `.env.local` or `.env` files containing actual secrets
2. **Use** `.env.example` as documentation only, with placeholder values
3. **Store** production secrets in Vercel's environment variables dashboard
4. **Rotate** API keys and database passwords regularly
5. **Limit** database user permissions to minimum required (read/write on `shares` table only)

**Sources:** [.env.example:1-8]()

---

## Database Connection Security

PostgreSQL connections include SSL requirements to ensure encrypted data transmission.

### SSL Mode Configuration

The `sslmode=require` parameter in [.env.example:1,2,4]() enforces encrypted connections:

```mermaid
flowchart TD
    App["Application<br/>/api/share"]
    ConnString["Connection String<br/>POSTGRES_URL"]
    SSLMode["sslmode=require<br/>parameter"]
    SSL["SSL/TLS Encryption"]
    PostgreSQL[("PostgreSQL Server")]
    
    App --> ConnString
    ConnString --> SSLMode
    SSLMode --> SSL
    SSL --> PostgreSQL
    
    SSLMode -.->|"without SSL"| NoSSL["Connection Rejected"]
```

**Diagram: SSL Enforcement Flow**

### Connection String Parameters

The connection strings in [.env.example]() include several security-relevant parameters:

| Parameter | Value | Purpose | Line Reference |
|-----------|-------|---------|----------------|
| `sslmode` | `require` | Enforce SSL/TLS encryption | [.env.example:1,2,4]() |
| `pgbouncer` | `true` | Enable connection pooling | [.env.example:2]() |
| `connect_timeout` | `15` | Timeout in seconds | [.env.example:2]() |

The connection pooling configuration in [.env.example:2]() (`pgbouncer=true&connect_timeout=15`) provides additional security benefits:
- **Connection reuse** reduces connection overhead and limits resource exhaustion attacks
- **Timeouts** prevent hung connections from consuming server resources
- **Connection limits** can be enforced at the pooler level

**Sources:** [.env.example:1-4]()

---

## Security Headers Summary

The following table summarizes all security headers applied by the application:

| Header | Value Source | Applied To | Environment |
|--------|--------------|------------|-------------|
| `Content-Security-Policy` (static) | [next.config.ts:5-16]() | All routes | All |
| `Content-Security-Policy` (nonce) | [src/app/tmp.middleware.ts:14-25]() | Page navigations | All |
| `Strict-Transport-Security` | [next.config.ts:49]() | All routes | Production only |
| `x-nonce` (custom) | [src/app/tmp.middleware.ts:33]() | Page navigations | All |

### Security Header Verification

To verify security headers are properly applied:

1. **Development**: Run `npm run dev` and inspect network responses in browser DevTools
2. **Production Build**: Run `npm run build && npm start` to test production configuration
3. **HSTS Verification**: Check that HSTS header only appears in production builds
4. **Nonce Verification**: Inspect page HTML to confirm `<script>` tags include `nonce` attributes matching the `x-nonce` header value

**Sources:** [next.config.ts:38-54](), [src/app/tmp.middleware.ts:9-72]()

---

## Threat Mitigation Matrix

| Threat | Mitigation | Implementation | Effectiveness |
|--------|------------|----------------|---------------|
| **Cross-Site Scripting (XSS)** | Nonce-based CSP | [src/app/tmp.middleware.ts:16]() | High |
| **Script injection** | `script-src 'self' 'nonce-{value}'` | [src/app/tmp.middleware.ts:16]() | High |
| **Inline style injection** | `style-src 'self' 'nonce-{value}'` | [src/app/tmp.middleware.ts:17]() | High |
| **Clickjacking** | `frame-ancestors 'none'` | [next.config.ts:12](), [src/app/tmp.middleware.ts:23]() | High |
| **Protocol downgrade** | HSTS with preload | [next.config.ts:49]() | High (production) |
| **Man-in-the-middle** | SSL enforcement | [.env.example:1]() | High |
| **Cookie hijacking** | HSTS enforces HTTPS | [next.config.ts:49]() | High (production) |
| **API key exposure** | Environment variables | [.env.example]() | Medium (depends on deployment) |
| **SQL injection** | Parameterized queries (ORM) | API routes | High |
| **Plugin vulnerabilities** | `object-src 'none'` | [next.config.ts:11]() | High |

**Sources:** [next.config.ts](), [src/app/tmp.middleware.ts](), [.env.example]()

---

# Page: Static Assets

# Static Assets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [public/click.wav](public/click.wav)
- [public/favicon.ico](public/favicon.ico)
- [public/favicon.png](public/favicon.png)
- [public/favicon.svg](public/favicon.svg)
- [public/og-image.png](public/og-image.png)
- [public/pressed.wav](public/pressed.wav)
- [public/screenshot.jpg](public/screenshot.jpg)

</details>



This document catalogs the static assets stored in the `public/` directory and explains their roles within the OpenAI.fm application. Static assets include favicons, audio files, and social sharing images that are served directly by Next.js without processing.

For information about build-time asset processing (SVG-to-React conversion, CSS compilation), see [Build Process](#4.2). For service worker caching of generated audio, see [Audio Processing](#3.5).

---

## Overview

OpenAI.fm maintains a minimal set of static assets in the `public/` directory, which Next.js serves from the root path (`/`). These assets include branding elements (favicons), UI feedback sounds, and social media metadata images.

**Sources:** [public/](public)

---

## Static Asset Directory Structure

The following diagram shows all static assets and their purposes:

```mermaid
graph TD
    subgraph "public/"
        ClickWav["click.wav<br/>UI Feedback Audio"]
        FaviconIco["favicon.ico<br/>Legacy Browser Icon"]
        FaviconPng["favicon.png<br/>PNG Browser Icon"]
        FaviconSvg["favicon.svg<br/>SVG Browser Icon"]
        OgImage["og-image.png<br/>Social Media Preview"]
    end
    
    subgraph "Next.js Static Serving"
        PublicRoute["/public/* → /<br/>Automatic Static File Serving"]
    end
    
    subgraph "Application References"
        HTML["layout.tsx<br/>Favicon Links"]
        Metadata["Metadata API<br/>OpenGraph Image"]
        UIComponents["PlayButton.tsx<br/>Click Sound"]
    end
    
    ClickWav --> PublicRoute
    FaviconIco --> PublicRoute
    FaviconPng --> PublicRoute
    FaviconSvg --> PublicRoute
    OgImage --> PublicRoute
    
    PublicRoute --> HTML
    PublicRoute --> Metadata
    PublicRoute --> UIComponents
```

**Sources:** [public/click.wav](public/click.wav), [public/favicon.ico](public/favicon.ico), [public/favicon.png](public/favicon.png), [public/favicon.svg](public/favicon.svg), [public/og-image.png](public/og-image.png)

---

## Favicon System

OpenAI.fm provides favicons in three formats to ensure compatibility across browsers and devices:

| File | Format | Dimensions | Purpose |
|------|--------|------------|---------|
| `favicon.svg` | Vector (SVG) | 100×100 viewBox | Modern browsers with SVG support |
| `favicon.png` | Raster (PNG) | 100×100 pixels | Standard browsers |
| `favicon.ico` | Multi-resolution ICO | Multiple sizes | Legacy browser compatibility |

### Favicon Design

All favicon variants display the same design: an orange circle (`#FF4A00`) on a transparent background.

```mermaid
graph LR
    SVGSource["favicon.svg<br/>Vector Source<br/>&lt;circle fill='#FF4A00'/&gt;"]
    PNGRaster["favicon.png<br/>Rasterized Version<br/>100×100px"]
    ICOLegacy["favicon.ico<br/>ICO Container<br/>Multiple Sizes"]
    
    SVGSource -->|"Defines Brand Color"| PNGRaster
    SVGSource -->|"Defines Brand Color"| ICOLegacy
```

The SVG implementation is minimal:

```svg
<circle cx="49.5" cy="49.5" r="47.5" fill="#FF4A00"/>
```

**Sources:** [public/favicon.svg:1-4](public/favicon.svg:1-4), [public/favicon.png](public/favicon.png), [public/favicon.ico](public/favicon.ico)

### Favicon Integration

Favicons are referenced in the root layout through Next.js's metadata system. The application likely uses Next.js 13+ App Router conventions for favicon discovery, where files in `public/` named `favicon.*` are automatically served.

**Sources:** [src/app/layout.tsx](src/app/layout.tsx) (inferred from Next.js conventions)

---

## Audio Assets

### Click Sound (`click.wav`)

The application includes a WAV audio file for UI feedback, typically played when users interact with buttons or controls.

| Property | Value |
|----------|-------|
| File | `public/click.wav` |
| Format | WAV (RIFF container) |
| Sample Rate | 48 kHz (inferred from WAV header) |
| Channels | Stereo (inferred) |
| Purpose | UI interaction feedback |

```mermaid
graph LR
    ClickFile["public/click.wav"]
    AudioElement["HTML5 Audio Element"]
    UserInteraction["Button Click Event"]
    
    ClickFile -->|"Loaded via /click.wav"| AudioElement
    UserInteraction -->|"Triggers"| AudioElement
    AudioElement -->|"Plays"| AudioFeedback["User Hears Click"]
```

The click sound is likely triggered by UI components (such as `PlayButton`) to provide auditory feedback for user actions. The exact integration point would be in the component's event handlers.

**Sources:** [public/click.wav](public/click.wav), [src/components/PlayButton.tsx](src/components/PlayButton.tsx) (inferred usage)

---

## Social Media Assets

### Open Graph Image (`og-image.png`)

The `og-image.png` serves as the preview image when the application is shared on social media platforms (Twitter, Facebook, LinkedIn, etc.).

| Property | Value |
|----------|-------|
| File | `public/og-image.png` |
| Format | PNG |
| Dimensions | 1200×630 pixels (standard OG image size, inferred) |
| Purpose | Social media link previews |

```mermaid
graph TD
    OGImage["public/og-image.png<br/>1200×630 Preview Image"]
    
    subgraph "Meta Tags"
        OGTag["&lt;meta property='og:image' content='/og-image.png' /&gt;"]
        TwitterTag["&lt;meta name='twitter:image' content='/og-image.png' /&gt;"]
    end
    
    subgraph "Social Platforms"
        Twitter["Twitter Card Preview"]
        Facebook["Facebook Link Preview"]
        LinkedIn["LinkedIn Share Preview"]
    end
    
    OGImage --> OGTag
    OGImage --> TwitterTag
    OGTag --> Facebook
    OGTag --> LinkedIn
    TwitterTag --> Twitter
```

The Open Graph image is referenced through Next.js metadata configuration, which generates appropriate `<meta>` tags in the HTML `<head>`.

**Sources:** [public/og-image.png](public/og-image.png), [src/app/layout.tsx](src/app/layout.tsx) (metadata configuration)

---

## Asset Serving Flow

Next.js automatically serves files from the `public/` directory at the root URL path. The following diagram illustrates how static assets are requested and served:

```mermaid
sequenceDiagram
    participant Browser
    participant NextJS as "Next.js Server"
    participant FileSystem as "public/ Directory"
    
    Browser->>NextJS: GET /favicon.svg
    NextJS->>FileSystem: Read public/favicon.svg
    FileSystem-->>NextJS: File contents
    NextJS-->>Browser: Response with image/svg+xml
    
    Browser->>NextJS: GET /og-image.png
    NextJS->>FileSystem: Read public/og-image.png
    FileSystem-->>NextJS: File contents
    NextJS-->>Browser: Response with image/png
    
    Browser->>NextJS: GET /click.wav
    NextJS->>FileSystem: Read public/click.wav
    FileSystem-->>NextJS: File contents
    NextJS-->>Browser: Response with audio/wav
```

**Sources:** [next.config.ts](next.config.ts) (Next.js configuration)

---

## Asset Manifest

The complete inventory of static assets:

| Asset | Type | Size Category | Primary Consumer |
|-------|------|---------------|------------------|
| `favicon.svg` | Branding | Small (<1 KB) | Browser chrome |
| `favicon.png` | Branding | Small (~5 KB) | Browser chrome |
| `favicon.ico` | Branding | Small (~5 KB) | Legacy browsers |
| `og-image.png` | Metadata | Large (~50-200 KB) | Social media scrapers |
| `click.wav` | Audio | Medium (~5-20 KB) | UI components |

**Sources:** [public/](public)

---

## Caching and Performance

Static assets in the `public/` directory benefit from Next.js's built-in caching strategies:

- **Browser Caching:** Next.js sets appropriate `Cache-Control` headers for static assets
- **Service Worker:** Generated audio (not static files) is cached by the service worker at [public/worker-444eae9e2e1bdd6edd8969f319655e70.js](public/worker-444eae9e2e1bdd6edd8969f319655e70.js)
- **CDN Compatibility:** When deployed to Vercel or similar platforms, these assets are automatically served from a CDN

```mermaid
graph LR
    Request["Browser Request<br/>/favicon.svg"]
    CDN["CDN Cache<br/>(Vercel Edge)"]
    Origin["Next.js Server"]
    
    Request -->|"First request"| CDN
    CDN -->|"Cache miss"| Origin
    Origin -->|"Response + Cache-Control"| CDN
    CDN -->|"Cached response"| Request
    
    Request2["Subsequent Request"] -->|"Cache hit"| CDN
    CDN -->|"Instant response"| Request2
```

**Sources:** [next.config.ts](next.config.ts), [public/worker-444eae9e2e1bdd6edd8969f319655e70.js](public/worker-444eae9e2e1bdd6edd8969f319655e70.js)

---

## Development Considerations

When modifying static assets:

1. **Favicon Changes:** Update all three formats (`svg`, `png`, `ico`) to maintain consistency
2. **Audio Files:** Keep WAV files short (<1 second) and ensure sample rate is appropriate (44.1 kHz or 48 kHz)
3. **OG Images:** Follow Open Graph specifications (1200×630 px, <8 MB)
4. **File Naming:** Use lowercase, hyphen-separated names for consistency with web conventions

**Sources:** [public/](public)

---

# Page: Dependencies Reference

# Dependencies Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



This page provides a comprehensive reference for all project dependencies defined in [package.json:1-43]() and their locked versions in [package-lock.json:1-end](). It documents the purpose of each dependency, their version constraints, and how they integrate into the OpenAI.fm application architecture.

For information about the build process that uses these dependencies, see [Build Process](#4.2). For environment configuration affecting dependencies like `@vercel/postgres`, see [Environment Configuration](#2.2).

## Dependency Structure Overview

The project uses npm as its package manager with two distinct dependency categories: production dependencies required for runtime operation and development dependencies used only during the build process.

```mermaid
graph TB
    subgraph "Package Management"
        PackageJSON["package.json<br/>Defines version ranges"]
        PackageLock["package-lock.json<br/>Locks exact versions"]
    end
    
    subgraph "Production Dependencies"
        Framework["Framework<br/>next, react, react-dom"]
        StateManagement["State Management<br/>zustand, immer"]
        UIComponents["UI Components<br/>@radix-ui/*"]
        CodeEditor["Code Editor<br/>@codemirror/*, @uiw/*"]
        Database["Database<br/>@vercel/postgres"]
        AudioLib["Audio<br/>wavesurfer.js"]
        Utilities["Utilities<br/>clsx, lz-string, react-hook-form"]
    end
    
    subgraph "Development Dependencies"
        TypeSystem["Type System<br/>typescript, @types/*"]
        Linting["Linting<br/>eslint, eslint-config-next"]
        Styling["Styling<br/>tailwindcss, @tailwindcss/postcss"]
    end
    
    PackageJSON --> PackageLock
    PackageLock --> Framework
    PackageLock --> StateManagement
    PackageLock --> UIComponents
    PackageLock --> CodeEditor
    PackageLock --> Database
    PackageLock --> AudioLib
    PackageLock --> Utilities
    PackageLock --> TypeSystem
    PackageLock --> Linting
    PackageLock --> Styling
```

**Sources:** [package.json:1-43](), [package-lock.json:1-6]()

## Production Dependencies

Production dependencies are installed in deployed environments and required for the application to function at runtime. These are defined in [package.json:11-30]().

### Framework and Core Libraries

| Package | Version | Purpose | Usage in Codebase |
|---------|---------|---------|-------------------|
| `next` | ^15.3.6 | Next.js framework providing SSR, routing, and API routes | [src/app/layout.tsx](), [src/app/page.tsx](), [src/app/api/generate/route.ts]() |
| `react` | ^19.0.0 | React library for building UI components | All component files in [src/components/]() |
| `react-dom` | ^19.0.0 | React DOM rendering engine | [src/app/layout.tsx:26]() |

**Sources:** [package.json:24-27](), [package-lock.json:936-941]()

### State Management

| Package | Version | Purpose | Usage in Codebase |
|---------|---------|---------|-------------------|
| `zustand` | ^5.0.3 | Lightweight state management library | [src/lib/appStore.ts]() for global application state |
| `immer` | ^10.1.1 | Immutable state updates | Used with Zustand middleware for state mutations |

The `zustand` package provides the `appStore` which manages global state including `input`, `prompt`, `voice`, and `latestAudioUrl`.

**Sources:** [package.json:22,30](), [src/lib/appStore.ts]()

### UI Component Libraries

The project uses Radix UI primitives for accessible, unstyled components that are styled with TailwindCSS.

| Package | Version | Purpose | Code Usage |
|---------|---------|---------|------------|
| `@radix-ui/react-icons` | ^1.3.2 | Icon components | [src/components/PlayButton.tsx](), [src/components/DownloadButton.tsx]() |
| `@radix-ui/react-switch` | ^1.1.3 | Toggle switch component | Used for UI controls |
| `@radix-ui/react-toast` | ^1.2.6 | Toast notification system | [src/components/ShareButton.tsx]() for notifications |
| `radix-ui` | ^1.1.3 | Meta package for Radix UI | Provides additional Radix components |

**Sources:** [package.json:15-17,25](), [package-lock.json:1644-1651]()

```mermaid
graph LR
    subgraph "Radix UI Integration"
        RadixIcons["@radix-ui/react-icons"]
        RadixSwitch["@radix-ui/react-switch"]
        RadixToast["@radix-ui/react-toast"]
        RadixMeta["radix-ui"]
    end
    
    subgraph "Component Usage"
        PlayButton["PlayButton.tsx<br/>Uses icons"]
        DownloadButton["DownloadButton.tsx<br/>Uses icons"]
        ShareButton["ShareButton.tsx<br/>Uses toast"]
        UIControls["Various UI Controls<br/>Use switch"]
    end
    
    RadixIcons --> PlayButton
    RadixIcons --> DownloadButton
    RadixToast --> ShareButton
    RadixSwitch --> UIControls
    RadixMeta --> UIControls
```

**Sources:** [src/components/PlayButton.tsx](), [src/components/DownloadButton.tsx](), [src/components/ShareButton.tsx]()

### Code Editor Components

The application includes a code editor for displaying code snippets, powered by CodeMirror.

| Package | Version | Purpose | Integration Point |
|---------|---------|---------|-------------------|
| `@codemirror/lang-javascript` | ^6.2.3 | JavaScript syntax support | Code snippet display for JS examples |
| `@codemirror/lang-python` | ^6.1.7 | Python syntax support | Code snippet display for Python examples |
| `@codemirror/legacy-modes` | ^6.5.0 | Additional language modes | Extended language support |
| `@uiw/react-codemirror` | ^4.23.10 | React wrapper for CodeMirror | [src/components/CodeCopyButton.tsx]() |
| `@uiw/codemirror-theme-duotone` | ^4.23.10 | Theme for code editor | Visual styling for code display |

These packages work together to provide syntax-highlighted code examples showing how to use the OpenAI TTS API in different languages.

**Sources:** [package.json:12-14,18-19](), [package-lock.json:92-106]()

### Database Integration

| Package | Version | Purpose | Usage in Codebase |
|---------|---------|---------|-------------------|
| `@vercel/postgres` | ^0.10.0 | PostgreSQL client for Vercel | [src/app/api/share/route.ts]() for persisting share data |

The `@vercel/postgres` package provides the `sql` client used to store and retrieve share configurations in the `shares` table. This dependency is optional and only required if the sharing feature is enabled.

**Sources:** [package.json:20](), [src/app/api/share/route.ts]()

### Audio Processing

| Package | Version | Purpose | Usage in Codebase |
|---------|---------|---------|-------------------|
| `wavesurfer.js` | ^7.9.1 | Audio waveform visualization | [src/components/PlayingWaveform.tsx]() for visual feedback |

The `wavesurfer.js` library is used to create real-time waveform visualizations during audio playback, analyzing amplitude data from the Web Audio API.

**Sources:** [package.json:29](), [src/components/PlayingWaveform.tsx]()

### Utility Libraries

| Package | Version | Purpose | Code Usage |
|---------|---------|---------|------------|
| `clsx` | ^2.1.1 | Conditional CSS class utility | Used throughout components for dynamic className generation |
| `lz-string` | ^1.5.0 | String compression for URLs | [src/app/api/share/route.ts]() for compressing share data |
| `react-hook-form` | ^7.54.2 | Form state management | Form handling for TTS input fields |

**Sources:** [package.json:21,23,28]()

```mermaid
graph TB
    subgraph "Utility Dependencies Flow"
        clsx["clsx<br/>Conditional Classes"]
        lzstring["lz-string<br/>Compression"]
        reacthookform["react-hook-form<br/>Form Management"]
    end
    
    subgraph "Implementation"
        Components["UI Components<br/>Dynamic styling"]
        ShareAPI["api/share/route.ts<br/>URL compression"]
        Forms["Input Forms<br/>State management"]
    end
    
    clsx --> Components
    lzstring --> ShareAPI
    reacthookform --> Forms
```

**Sources:** [src/app/api/share/route.ts](), [src/components/]()

## Development Dependencies

Development dependencies are only installed during development and build processes. They are not included in production deployments. These are defined in [package.json:32-42]().

### Type System

| Package | Version | Purpose | Configuration |
|---------|---------|---------|---------------|
| `typescript` | ^5 | TypeScript compiler | [tsconfig.json]() defines compiler options |
| `@types/node` | ^20 | Node.js type definitions | Required for Node API types |
| `@types/react` | ^19 | React type definitions | Required for React component types |
| `@types/react-dom` | ^19 | React DOM type definitions | Required for ReactDOM types |

TypeScript provides static type checking across the entire codebase, with custom declarations in [global.d.ts:1-3]() for SVG module imports.

**Sources:** [package.json:35-37,41](), [global.d.ts:1-3]()

### Linting and Code Quality

| Package | Version | Purpose | Configuration File |
|---------|---------|---------|-------------------|
| `eslint` | ^9 | JavaScript/TypeScript linter | [eslint.config.mjs]() |
| `eslint-config-next` | 15.2.2 | Next.js ESLint configuration | Imported in [eslint.config.mjs]() |
| `@eslint/eslintrc` | ^3 | ESLint configuration utilities | Supports flat config format |

The linting setup uses ESLint v9's flat configuration format with Next.js-specific rules to enforce code quality and catch common errors.

**Sources:** [package.json:33,38-39](), [eslint.config.mjs]()

### Styling System

| Package | Version | Purpose | Configuration |
|---------|---------|---------|---------------|
| `tailwindcss` | ^4 | Utility-first CSS framework | [postcss.config.mjs]() |
| `@tailwindcss/postcss` | ^4 | TailwindCSS PostCSS plugin | [postcss.config.mjs:1-9]() |

TailwindCSS v4 processes utility classes defined in components and generates the final CSS output. The PostCSS plugin integrates TailwindCSS into the build pipeline.

**Sources:** [package.json:34,40](), [postcss.config.mjs:1-9]()

## Version Locking Mechanism

The [package-lock.json:1-end]() file locks exact dependency versions and their entire dependency trees, ensuring reproducible builds across environments.

```mermaid
graph TB
    subgraph "Version Management"
        Dev["Developer<br/>npm install"]
        PackageJSON["package.json<br/>^15.3.6 (range)"]
        PackageLock["package-lock.json<br/>15.3.6 (exact)"]
        Registry["npm Registry<br/>Package source"]
    end
    
    subgraph "Build Environments"
        LocalBuild["Local Development"]
        VercelBuild["Vercel Production"]
        CIBuild["CI Pipeline"]
    end
    
    Dev --> PackageJSON
    PackageJSON --> Registry
    Registry --> PackageLock
    PackageLock --> LocalBuild
    PackageLock --> VercelBuild
    PackageLock --> CIBuild
```

The lockfile structure at [package-lock.json:1-6]() includes:
- `lockfileVersion: 3` - npm lockfile format version
- `requires: true` - Automatic dependency resolution
- Package definitions with exact resolved versions and integrity hashes

**Sources:** [package-lock.json:1-6]()

## Dependency Graph by Feature

This diagram shows how dependencies map to application features, bridging between natural language system names and actual package names.

```mermaid
graph TB
    subgraph "Audio Generation Feature"
        AudioGenAPI["api/generate/route.ts"]
        NextRuntime["next@15.3.6<br/>API Routes"]
        ReactUI["react@19.0.0<br/>UI Layer"]
    end
    
    subgraph "State Management Feature"
        AppStore["lib/appStore.ts"]
        Zustand["zustand@5.0.3"]
        Immer["immer@10.1.1"]
    end
    
    subgraph "Sharing Feature"
        ShareAPI["api/share/route.ts"]
        PostgresClient["@vercel/postgres@0.10.0"]
        LZString["lz-string@1.5.0"]
    end
    
    subgraph "Waveform Visualization Feature"
        PlayingWaveform["components/PlayingWaveform.tsx"]
        Wavesurfer["wavesurfer.js@7.9.1"]
    end
    
    subgraph "Code Examples Feature"
        CodeCopyButton["components/CodeCopyButton.tsx"]
        CodeMirror["@uiw/react-codemirror@4.23.10"]
        JSLang["@codemirror/lang-javascript@6.2.3"]
        PyLang["@codemirror/lang-python@6.1.7"]
    end
    
    subgraph "UI Components Feature"
        PlayButton["components/PlayButton.tsx"]
        ShareButton["components/ShareButton.tsx"]
        RadixIcons["@radix-ui/react-icons@1.3.2"]
        RadixToast["@radix-ui/react-toast@1.2.6"]
    end
    
    AudioGenAPI --> NextRuntime
    AudioGenAPI --> ReactUI
    AppStore --> Zustand
    Zustand --> Immer
    ShareAPI --> PostgresClient
    ShareAPI --> LZString
    PlayingWaveform --> Wavesurfer
    CodeCopyButton --> CodeMirror
    CodeMirror --> JSLang
    CodeMirror --> PyLang
    PlayButton --> RadixIcons
    ShareButton --> RadixToast
    ShareButton --> RadixIcons
```

**Sources:** [package.json:11-30](), [src/app/api/generate/route.ts](), [src/app/api/share/route.ts](), [src/lib/appStore.ts](), [src/components/]()

## Dependency Version Constraints

The project uses semantic versioning with caret (^) ranges to allow compatible updates.

| Version Syntax | Meaning | Example | Allows |
|----------------|---------|---------|--------|
| `^15.3.6` | Compatible with 15.3.6 | `next: ^15.3.6` | 15.3.7, 15.4.0, but not 16.0.0 |
| `^19.0.0` | Compatible with 19.0.0 | `react: ^19.0.0` | 19.0.1, 19.1.0, but not 20.0.0 |
| `^5` | Compatible with 5.x.x | `typescript: ^5` | 5.0.0, 5.1.0, 5.9.9, but not 6.0.0 |
| `15.2.2` | Exact version | `eslint-config-next: 15.2.2` | Only 15.2.2 |

**Sources:** [package.json:11-42]()

## Optional Dependencies

Certain dependencies are functionally optional based on feature usage:

| Package | Condition | Feature Requirement |
|---------|-----------|---------------------|
| `@vercel/postgres` | Requires `POSTGRES_URL` environment variable | Share functionality via [api/share/route.ts]() |
| `wavesurfer.js` | UI enhancement only | Waveform visualization in [PlayingWaveform.tsx]() |

When `POSTGRES_URL` is not configured, the sharing API returns appropriate error responses at [src/app/api/share/route.ts]().

**Sources:** [.env.example](), [src/app/api/share/route.ts]()

## Peer Dependencies

Some packages have peer dependency requirements that are satisfied by the project:

```mermaid
graph LR
    subgraph "Radix UI Peer Dependencies"
        RadixSwitch["@radix-ui/react-switch"]
        RadixToast["@radix-ui/react-toast"]
        RadixIcons["@radix-ui/react-icons"]
    end
    
    subgraph "Required Peers"
        React["react@19.0.0"]
        ReactDOM["react-dom@19.0.0"]
        TypesReact["@types/react@19<br/>(dev)"]
    end
    
    RadixSwitch --> React
    RadixSwitch --> ReactDOM
    RadixSwitch --> TypesReact
    RadixToast --> React
    RadixToast --> ReactDOM
    RadixToast --> TypesReact
    RadixIcons --> React
```

All Radix UI components declare peer dependencies on `react`, `react-dom`, and optionally `@types/react`, which are satisfied by the versions installed at [package.json:26-27,36-37]().

**Sources:** [package-lock.json:2177-2204](), [package.json:26-27,36-37]()

## Build Tool Dependencies

Next.js includes built-in support for several tools that don't require separate packages:

| Built-in Tool | Purpose | Configuration |
|---------------|---------|---------------|
| Webpack / Turbopack | Module bundler | [next.config.ts]() |
| SWC | Fast TypeScript/JavaScript compiler | Enabled by default in Next.js 15 |
| SVGR | SVG to React component loader | Configured in [next.config.ts]() |

The `next` package at version 15.3.6 includes platform-specific SWC binaries as optional dependencies in [package-lock.json:952-1079]().

**Sources:** [next.config.ts](), [package-lock.json:952-1079]()

## Dependency Update Strategy

To update dependencies:

1. **Minor/Patch Updates**: Run `npm update` to update within caret ranges
2. **Major Updates**: Modify [package.json]() version constraints manually
3. **Lockfile Regeneration**: Run `npm install` to update [package-lock.json]()
4. **Verification**: Run `npm run build` and `npm run lint` to verify compatibility

The locked versions in [package-lock.json]() ensure consistent builds until explicitly updated.

**Sources:** [package.json:5-9](), [package-lock.json:1-6]()