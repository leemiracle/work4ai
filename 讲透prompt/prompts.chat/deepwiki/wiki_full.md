# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [PROMPTS.md](PROMPTS.md)
- [README.md](README.md)
- [next.config.ts](next.config.ts)
- [prompts.csv](prompts.csv)
- [scripts/generate-contributors.sh](scripts/generate-contributors.sh)
- [scripts/rebuild-history.sh](scripts/rebuild-history.sh)
- [src/app/about/page.tsx](src/app/about/page.tsx)
- [src/app/page.tsx](src/app/page.tsx)
- [src/app/prompts.csv/route.ts](src/app/prompts.csv/route.ts)
- [src/app/prompts.json/route.ts](src/app/prompts.json/route.ts)
- [src/components/admin/import-prompts.tsx](src/components/admin/import-prompts.tsx)
- [tests/generate-contributors-format.test.js](tests/generate-contributors-format.test.js)

</details>



## Purpose and Scope

prompts.chat is an open-source AI prompt library and management platform designed to curate, manage, and distribute high-quality AI prompts compatible with various modern large language models including ChatGPT, Claude, Gemini, Llama, and Mistral [README.md:1-16](). Originating as "Awesome ChatGPT Prompts" in December 2022 [README.md:18](), [README.md:43](), the codebase has evolved into a full-stack Next.js application supporting prompt browsing, execution, versioning, contribution tracking, self-hosting, and Model Context Protocol (MCP) server integration [README.md:100-174]().

This page documents the high-level technical architecture, dual-persistence model, contributor attribution system, and core integration points of the `prompts.chat` repository.

Sources:
[README.md:1-43](), [README.md:100-174]()

---

## Technical Stack & Data Flow

The platform is built on Next.js using React Server Components, Prisma ORM as the data access layer, and PostgreSQL as the primary database store. User authentication is managed via NextAuth [src/app/page.tsx:6](). The system maintains a dual-persistence model where prompts stored in PostgreSQL are synchronously mirrored to flat files (`prompts.csv` and `PROMPTS.md`) to preserve version control history and GitHub contributor attribution.

### System Architecture and Data Flow Diagram

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        NL1["UserBrowser"]
        NL2["IDEOrAIAssistant"]
        NL3["CommandLineOperator"]
    end

    subgraph "CodeEntitySpace"
        UI["src/app/page.tsx:HomePage()"]
        MCP_API["src/app/docs/api/page.tsx:/api/mcp"]
        CSV_API["src/app/prompts.csv/route.ts:GET()"]
        CONFIG_LIB["src/lib/config.ts:getConfig()"]
        AUTH_LIB["src/lib/auth.ts:auth()"]
        DB_LIB["src/lib/db.ts:db"]
        SCRIPT_GEN_CONTRIB["scripts/generate-contributors.sh"]
    end

    subgraph "PersistenceLayer"
        PG_DB["PostgreSQLDatabase"]
        CSV_FILE["prompts.csv"]
        MD_FILE["PROMPTS.md"]
        GIT_HISTORY["GitRepositoryHistory"]
    end

    NL1 --> UI
    NL2 --> MCP_API
    NL3 --> SCRIPT_GEN_CONTRIB

    UI --> CONFIG_LIB
    UI --> AUTH_LIB
    UI --> DB_LIB
    
    CSV_API --> DB_LIB
    DB_LIB --> PG_DB

    CSV_API -. "Exports CSV" .-> CSV_FILE
    SCRIPT_GEN_CONTRIB --> CSV_API
    SCRIPT_GEN_CONTRIB --> CSV_FILE
    SCRIPT_GEN_CONTRIB --> MD_FILE
    SCRIPT_GEN_CONTRIB --> GIT_HISTORY
```

**Legend:**  
- `HomePage()`: Root React Server Component rendering landing and discovery views [src/app/page.tsx:35-50]().  
- `GET()`: API endpoint exporting public prompts in CSV format [src/app/prompts.csv/route.ts:29-92]().  
- `generate-contributors.sh`: Shell script orchestrating remote CSV synchronization, Git commits, and markdown regeneration [scripts/generate-contributors.sh:1-130]().  
- `/api/mcp`: Model Context Protocol endpoint for AI assistant integration [src/app/docs/api/page.tsx:73]().

Sources:  
[src/app/page.tsx:35-50](), [src/app/prompts.csv/route.ts:29-92](), [scripts/generate-contributors.sh:1-130](), [src/app/docs/api/page.tsx:73]()

---

## Dual Persistence Architecture & CSV Sync

To reconcile rich relational database queries with flat-file open-source distribution, `prompts.chat` implements a bidirectional synchronization mechanism between PostgreSQL and repository-tracked files (`prompts.csv` and `PROMPTS.md`).

1.  **Database Canonical Store**: All prompt mutations (creations, edits, deletions) occur through Prisma models targeting PostgreSQL [src/app/prompts.csv/route.ts:31-63]().
2.  **CSV Export Endpoint**: The route handler `src/app/prompts.csv/route.ts` queries all non-private, non-unlisted prompts, escaping fields via `escapeCSVField` and constructing structured contributor strings via `getUserIdentifier` [src/app/prompts.csv/route.ts:5-83](). This endpoint is configured to revalidate every 3600 seconds (1 hour) [src/app/prompts.csv/route.ts:27]().

Sources:
[src/app/prompts.csv/route.ts:5-92](), [src/app/prompts.csv/route.ts:27]()

---

## Contributor Attribution & Git Commit Sync

The shell utility `scripts/generate-contributors.sh` ensures that updates made via the web interface are accurately reflected in Git history with individual contributor attribution:

-   Fetches the latest prompt records from the running instance's CSV endpoint [scripts/generate-contributors.sh:15-21]().
-   Compares local and remote datasets, staging new additions [scripts/generate-contributors.sh:35-120]().
-   Resolves commit author identities from the primary contributor field and appends `Co-authored-by` Git commit trailers for multi-author prompts [scripts/generate-contributors.sh:108-114]().
-   Regenerates human-readable collapsible `<details>` blocks inside `PROMPTS.md` [scripts/generate-contributors.sh:155-186]().

### Synchronization Sequence Diagram

```mermaid
sequenceDiagram
    participant WebUI as "Next.js App"
    participant Postgres as "PostgreSQL DB"
    participant Route as "src/app/prompts.csv/route.ts:GET()"
    participant Script as "scripts/generate-contributors.sh"
    participant CSVFile as "prompts.csv"
    participant Markdown as "PROMPTS.md"
    participant GitRepo as "Git Repository"

    WebUI->>Postgres: "Write prompt records"
    Script->>Route: "Fetch remote CSV payload"
    Route->>Postgres: "Query public prompts"
    Postgres-->>Route: "Return structured records"
    Route-->>Script: "Raw CSV string"
    Script->>CSVFile: "Synchronize rows"
    Script->>Markdown: "Update <details> blocks"
    Script->>GitRepo: "Commit with Author & Co-authored-by trailers"
```

Sources:
[scripts/generate-contributors.sh:1-186](), [src/app/prompts.csv/route.ts:29-92]()

---

## Self-Hosting & Configuration System

The project is architected for seamless self-hosting [README.md:113-115](). Instances are configured via `prompts.config.ts` combined with runtime environment variable overrides (`PCHAT_*`), allowing custom branding, theme parameters, authentication provider selection (GitHub, Google, Apple, Azure, or credentials), and feature flag toggles [SELF-HOSTING.md:149-203](). Configuration values are accessed synchronously or asynchronously via helper functions in `src/lib/config` [src/app/page.tsx:39](). The `npx prompts.chat new` command provides a quick start for new self-hosted instances, including an interactive setup wizard [SELF-HOSTING.md:81-93]().

Sources:
[README.md:113-115](), [SELF-HOSTING.md:149-203](), [src/app/page.tsx:39](), [SELF-HOSTING.md:81-93]()

---

## Model Context Protocol (MCP) Integration

To support programmatic AI workflow automation, `prompts.chat` hosts a native MCP server endpoint at `/api/mcp` [src/app/docs/api/page.tsx:73](). This endpoint exposes standard tools allowing IDE extensions and CLI agents like Claude Code to query and manage prompt data directly [src/app/docs/api/page.tsx:60-69](). Authentication for MCP requests can be done via API keys passed in headers or environment variables [src/app/docs/api/page.tsx:116-141]().

Sources:
[src/app/docs/api/page.tsx:73](), [src/app/docs/api/page.tsx:60-69](), [src/app/docs/api/page.tsx:116-141]()

---

## Technical References

| Component / Function | File Path & Line Range | Role |
|---|---|---|
| CSV Export Handler | `src/app/prompts.csv/route.ts:29-97` | Serializes public database prompts into standard CSV format. |
| Contributor Sync Script | `scripts/generate-contributors.sh:1-130` | Syncs remote CSV data into local Git commits and Markdown blocks. |
| Homepage Server Component | `src/app/page.tsx:35-62` | Handles SSR rendering, session auth checks, and configuration resolution. |
| MCP API Endpoint | `src/app/docs/api/page.tsx:73` | Provides the Model Context Protocol server for AI tool integration. |
| Next.js Configuration | `next.config.ts:15-104` | Defines Next.js build and runtime configurations, including redirects and headers. |
| Footer Component | `src/components/layout/footer.tsx:15-46` | Renders the application footer with links to documentation, API, and GitHub. |

Sources:
[src/app/prompts.csv/route.ts:29-97](), [scripts/generate-contributors.sh:1-130](), [src/app/page.tsx:35-62](), [src/app/docs/api/page.tsx:73](), [next.config.ts:15-104](), [src/components/layout/footer.tsx:15-46]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [prisma/reset-admin.ts](prisma/reset-admin.ts)
- [scripts/setup.js](scripts/setup.js)

</details>



This page serves as the parent overview for initial setup and configuration guides for `prompts.chat`. It outlines basic setup pathways, the configuration system architecture, database prerequisites, and runtime requirements.

As a parent page, this document provides a high-level architectural view. For detailed installation steps and software requirements, see [Prerequisites & Installation](#2.1). For local development workflow and database migrations, see [Local Development Setup](#2.2). For configuration options and variables, see [Configuration Quickstart](#2.3). For containerized deployment, see [Docker Quick Start](#2.4).

Sources: [package.json:5-123]()

## Setup Paths

`prompts.chat` supports multiple deployment and setup pathways depending on the operational environment:

| Mode | Use Case | Entry Point | Configuration Method |
|------|----------|-------------|---------------------|
| **Local Development** | Development, testing, and customization | `npm install` + `npm run dev` [package.json:5-6]() | Interactive wizard or manual editing |
| **Docker (Self-Hosted)** | Production deployment, single-container | Environment variables (`PCHAT_*`) | `compose.yml` and environment file |
| **Production Build** | Custom production deployment | `npm run build` + `npm start` [package.json:7-9]() | Config file and environment variables |

Each path utilizes the core configuration loader but differs in how variables and persistent data are supplied. For details, see [Prerequisites & Installation](#2.1) and [Docker Quick Start](#2.4).

Sources: [package.json:5-9]()

## Configuration Architecture

The configuration pipeline combines a base TypeScript configuration file (`prompts.config.ts`) with environment variable overrides. For private clones, an interactive setup script handles generation of both files.

### Configuration Flow (Natural Language to Code Entity)
```mermaid
graph TB
    subgraph "ConfigurationSources"
        ConfigFile["prompts.config.ts"]
        EnvFile[".env"]
        EnvVars["PCHAT_*Variables"]
    end
    
    subgraph "ConfigurationPipeline"
        DefineConfig["defineConfig()<br/>src/lib/config/index.ts"]
        InteractiveSetup["setup.js<br/>scripts/setup.js"]
        ConfigIndex["getConfig()<br/>src/lib/config/index.ts"]
    end
    
    subgraph "ApplicationConsumption"
        GetConfig["getConfig()<br/>ServerRuntime"]
        GetConfigSync["getConfigSync()<br/>ClientRuntime"]
        PrismaClient["PrismaClient<br/>prisma/reset-admin.ts"]
    end
    
    ConfigFile --> DefineConfig
    InteractiveSetup --> ConfigFile
    InteractiveSetup --> EnvFile
    
    ConfigFile --> ConfigIndex
    EnvFile --> ConfigIndex
    EnvVars --> ConfigIndex
    
    ConfigIndex --> GetConfig
    ConfigIndex --> GetConfigSync
    
    GetConfig --> PrismaClient
```

**Configuration Flow Details:**
1. **[scripts/setup.js:95-164]()** — The `generateConfig` function creates the `prompts.config.ts` file based on interactive user inputs during setup.
2. **[src/lib/config/index.ts]()** — Configurations use the `defineConfig` helper to organize branding, theme, and feature flags.
3. **[src/lib/config/index.ts]()** — At runtime, `PCHAT_` prefixed environment variables override specific domains.

For a deep dive into configuration parameters, see [Configuration Quickstart](#2.3).

Sources: [scripts/setup.js:95-164](), [src/lib/config/index.ts]()

## Setup Workflow

### Initialization Sequence
```mermaid
graph LR
    Start["Start"] --> Choice{"SetupMethod"}
    
    Choice -->|"Interactive"| SetupScript["npm run setup<br/>scripts/setup.js"]
    Choice -->|"Docker"| DockerStart["docker compose up"]
    
    SetupScript --> GenConfig["Generate prompts.config.ts"]
    SetupScript --> GenEnv["Generate .env"]
    
    DockerStart --> DBConfig["Database Configuration"]
    
    GenEnv --> DBConfig
    
    DBConfig --> Migrate["prisma migrate dev"]
    
    Migrate --> Seed{"SeedData?"}
    
    Seed -->|"Yes"| RunSeed["npx prisma db seed<br/>prisma/seed.ts"]
    Seed -->|"No"| StartApp
    
    RunSeed --> StartApp["Start Application<br/>npm run dev"]
    
    StartApp --> Ready["Ready"]
```

For detailed setup instructions, see [Local Development Setup](#2.2) and [Docker Quick Start](#2.4).

Sources: [scripts/setup.js:171-258](), [package.json:11-19]()

## Core Configuration Domains

The application divides configuration into distinct functional domains. These can be adjusted directly in `prompts.config.ts` or via environment overrides.

### Configuration Entity Mapping (Natural Language to Code Entity)
```mermaid
graph TB
    subgraph ConfigDomains["ConfigurationDomains"]
        Branding["BrandingConfig<br/>src/lib/config/index.ts"]
        Theme["ThemeConfig<br/>src/lib/config/index.ts"]
        Auth["AuthConfig<br/>src/lib/config/index.ts"]
        I18n["I18nConfig<br/>src/lib/config/index.ts"]
        Features["FeaturesConfig<br/>src/lib/config/index.ts"]
    end
    
    subgraph BrandingProps["BrandingEntities"]
        B1["PCHAT_NAME"]
        B2["PCHAT_LOGO"]
        B3["PCHAT_DESCRIPTION"]
    end
    
    subgraph ThemeProps["ThemeEntities"]
        T1["PCHAT_COLOR"]
        T2["PCHAT_THEME_RADIUS"]
        T3["PCHAT_THEME_VARIANT"]
    end
    
    subgraph FeatureFlags["FeatureEntities"]
        F1["PCHAT_FEATURE_AI_SEARCH"]
        F2["PCHAT_FEATURE_MCP"]
        F3["PCHAT_FEATURE_PRIVATE_PROMPTS"]
    end
    
    Branding --- BrandingProps
    Theme --- ThemeProps
    Features --- FeatureFlags
```

**Environment Variable Override Examples:**
* Branding: `PCHAT_NAME` overrides `branding.name`
* Theme: `PCHAT_COLOR` overrides `theme.colors.primary`
* Features: `PCHAT_FEATURE_MCP` overrides `features.mcp`

For further details, see [Configuration Quickstart](#2.3).

Sources: [src/lib/config/index.ts]()

## Database Requirements

`prompts.chat` relies on PostgreSQL and uses Prisma as its ORM layer [package.json:46]().

### Database Interaction Layer
```mermaid
graph LR
    subgraph "DataSources"
        RemoteCSV["prompts.chat CSV<br/>prompts.json"]
        LocalDB["PostgreSQL<br/>prompts DB"]
    end
    
    subgraph "PrismaEngine"
        Client["PrismaClient<br/>@prisma/client"]
        Migrator["prisma migrate<br/>Schema Evolution"]
    end
    
    RemoteCSV --> Seed["prisma/seed.ts"]
    Seed --> Client
    Client --> LocalDB
    Migrator --> LocalDB
```

**Database Scripts:**
* `npm run db:setup` — Generates client, runs migrations, and executes seeding [package.json:21-21]()
* `npm run db:migrate` — Applies developmental migrations [package.json:12-12]()
* `npm run db:seed` — Populates initial categories, tags, and prompts [package.json:15-15]()
* `npm run db:resetadmin` — Resets the administrative account credentials [prisma/reset-admin.ts:6-31]()

For comprehensive database management guides, see [Local Development Setup](#2.2).

Sources: [package.json:12-21](), [prisma/reset-admin.ts:6-31]()

## Node.js Version Requirement

The application strictly enforces **Node.js 24.x** as configured in package engines [package.json:121-123]().

```json
{
  "engines": {
    "node": "24.x"
  }
}
```

For software prerequisites, see [Prerequisites & Installation](#2.1).

Sources: [package.json:121-123]()

## Initial Admin Account

Running database seeding provisions a default administrative user:
* **Email:** `admin@prompts.chat` [prisma/reset-admin.ts:18-18]()
* **Username:** `admin` [prisma/reset-admin.ts:19-19]()
* **Password:** `password123` [prisma/reset-admin.ts:9-9]()
* **Role:** `ADMIN` [prisma/reset-admin.ts:22-22]()

Sources: [prisma/reset-admin.ts:9-22]()

## Next Steps

For detailed instructions tailored to a specific deployment strategy, refer to the child pages:
- For software requirements and installation steps, see [Prerequisites & Installation](#2.1)
- For setting up the local repository and runner, see [Local Development Setup](#2.2)
- For configuration settings and environment variables, see [Configuration Quickstart](#2.3)
- For containerized execution, see [Docker Quick Start](#2.4)

Sources: [package.json:5-123](), [scripts/setup.js:95-258](), [prisma/reset-admin.ts:6-31]()

---

# Page: Prerequisites & Installation

# Prerequisites & Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [prisma/reset-admin.ts](prisma/reset-admin.ts)
- [scripts/setup.js](scripts/setup.js)

</details>



This page details the software prerequisites, dependency ecosystem, interactive setup wizard, and database initialization required to deploy and run `prompts.chat` locally or in a self-hosted environment. It covers the technical specifications of the Next.js architecture [package.json:32-70](), configuration scripts [scripts/setup.js:1-164](), and automated seeding pipelines [prisma/reset-admin.ts:1-40]().

---

## System Requirements & Technical Stack

Running `prompts.chat` requires specific runtime environments to support React Server Components, Prisma ORM, and the Model Context Protocol (MCP) server integration.

### Software Specifications

| Component | Minimum Version | Code Entity / Enforcement | Notes |
|---|---|---|---|
| **Node.js** | `24.x` | `package.json` engines field [package.json:121-123]() | Enforces modern V8 features and async local storage. |
| **npm** | Latest | `package-lock.json` [package-lock.json:10-11]() | Used for dependency resolution and executing lifecycle scripts. |
| **PostgreSQL** | `12.0+` | `prisma/schema.prisma` / `DATABASE_URL` [scripts/setup.js:38]() | Relational database for prompt storage, users, and change requests via Prisma Client [package.json:46](). |

### System Requirements to Code Entity Mapping

Title: "System Requirements to Code Entity Mapping"
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        NodeRuntime["Node.js 24 Runtime Environment"]
        PackageMgr["npm Package Manager"]
        RelationalDB["PostgreSQL Database"]
    end

    subgraph "CodeEntitySpace"
        EngineConfig["package.json engines field"]
        LockFile["package-lock.json lockfile"]
        PrismaClientInstance["@prisma/client PrismaClient"]
        EnvConfig[".env DATABASE_URL"]
    end

    NodeRuntime -->|"enforced by"| EngineConfig
    PackageMgr -->|"tracks versions in"| LockFile
    RelationalDB -->|"accessed via"| EnvConfig
    EnvConfig -->|"instantiated by"| PrismaClientInstance
```

Sources: [package.json:121-123](), [package-lock.json:10-11](), [scripts/setup.js:38]()

---

## Dependency Architecture

The application relies on a modular set of dependencies defined in `package.json` [package.json:37-91]() and locked in `package-lock.json` [package-lock.json:1-95](). 

- **Framework**: `next@16.0.10` and `react@19.2.0` power the full-stack server-rendered application [package.json:74,81]().
- **Database & ORM**: `prisma@6.19.0` and `@prisma/client@6.19.0` handle schema migrations and type-safe data access [package.json:46,113]().
- **Authentication**: `next-auth@5.0.0-beta.30`, `@auth/prisma-adapter@2.11.1`, and `bcryptjs@3.0.3` manage sessions, OAuth adapters, and password hashing [package.json:38,66,75]().
- **AI & Integrations**: `openai@6.10.0` and `@modelcontextprotocol/sdk@1.24.3` provide embeddings, semantic search, and MCP endpoint registration [package.json:43,78]().

Sources: [package.json:37-91](), [package-lock.json:1-95]()

---

## Interactive Setup Wizard (`scripts/setup.js`)

For self-hosted instances, `prompts.chat` provides an interactive setup script located at `scripts/setup.js` [scripts/setup.js:1-164]() that utilizes `@clack/prompts` and `picocolors` to configure environment variables and application config [scripts/setup.js:15-16]().

### Wizard Execution Flow & Functions

Title: "Wizard Execution Flow Sequence"
```mermaid
sequenceDiagram
    participant Developer as "Developer"
    participant CLI as "scripts/setup.js main()"
    participant AuthGen as "generateAuthSecret()"
    participant DBBuilder as "buildDatabaseUrl()"
    participant ConfigWriter as "generateConfig()"
    participant EnvWriter as "generateEnvFile()"

    Developer->>CLI: "Execute node scripts/setup.js"
    CLI->>Developer: "Prompt for application domain & database credentials"
    Developer-->>CLI: "Provide host, port, user, password, db name"
    CLI->>AuthGen: "Call crypto.randomBytes(32)"
    AuthGen-->>CLI: "Return AUTH_SECRET string"
    CLI->>DBBuilder: "Construct connection URI"
    DBBuilder-->>CLI: "Return DATABASE_URL string"
    CLI->>ConfigWriter: "Write prompts.config.ts via defineConfig()"
    CLI->>EnvWriter: "Write .env file with secrets and URLs"
    EnvWriter-->>Developer: "Configuration complete"
```

Sources: [scripts/setup.js:21-164]()

### Core Setup Helper Functions

- `generateAuthSecret()`: Generates a cryptographically secure 32-byte base64-encoded secret for `AUTH_SECRET` [scripts/setup.js:21-23]().
- `buildDatabaseUrl(config)`: Assembles the PostgreSQL connection string format `postgresql://username:password@host:port/database` [scripts/setup.js:25-28]().
- `generateEnvFile(config)`: Outputs environment variables including `DATABASE_URL`, `AUTH_SECRET`, `CRON_SECRET`, and optional API keys for GitHub, Google, and OpenAI [scripts/setup.js:30-93]().
- `generateConfig(config)`: Generates `prompts.config.ts` utilizing `defineConfig` to set branding, theme, auth providers, and feature flags [scripts/setup.js:95-164]().

Sources: [scripts/setup.js:21-164]()

---

## Database Initialization & Seeding

Once dependencies are installed and environment variables are configured, the database schema must be deployed and seeded with initial prompt records.

### Seeding Pipeline (`prisma/reset-admin.ts`)

The database reset and admin initialization script `prisma/reset-admin.ts` manages administrative access and ensures safe bootstrapping of default privileges [prisma/reset-admin.ts:1-40]().

Title: "Seeding Pipeline Architecture"
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        DefaultAdmin["Default Administrator Credentials"]
        DatabaseInstance["PostgreSQL Prisma Client"]
    end

    subgraph "CodeEntitySpace"
        ResetAdminScript["main() in prisma/reset-admin.ts"]
        BcryptHash["bcrypt.hash()"]
        PrismaUpsert["prisma.user.upsert()"]
    end

    DefaultAdmin -->|"inputs password123"| BcryptHash
    BcryptHash -->|"hashed string"| ResetAdminScript
    ResetAdminScript -->|"executes upsert"| PrismaUpsert
    PrismaUpsert -->|"persists to"| DatabaseInstance
```

Sources: [prisma/reset-admin.ts:1-40]()

### Seeding Execution Steps

1. **Admin User Upsert**: Creates or updates the administrator account (`admin@prompts.chat`) with a bcrypt-hashed default password (`password123`) and `ADMIN` role [prisma/reset-admin.ts:11-25]().
2. **Prisma Client Lifecycle**: Connects and safely disconnects via `prisma.$disconnect()` within the script lifecycle [prisma/reset-admin.ts:4-39]().

Sources: [prisma/reset-admin.ts:1-40]()

### Admin Credential Recovery

If admin access is lost, the default administrator credentials can be reset by executing the reset script [prisma/reset-admin.ts:1-40]():

```bash
npm run db:resetadmin
```

This runs `prisma/reset-admin.ts`, which resets the password for `admin@prompts.chat` to `password123` [prisma/reset-admin.ts:9-30]().

Sources: [prisma/reset-admin.ts:1-40]()

---

# Page: Local Development Setup

# Local Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [prisma/reset-admin.ts](prisma/reset-admin.ts)
- [prisma/seed.ts](prisma/seed.ts)
- [scripts/setup.js](scripts/setup.js)

</details>



This page provides a comprehensive technical guide for setting up the local development environment for `prompts.chat`. It covers environment configuration, configuration injection pipelines, database initialization via Prisma ORM, remote data seeding, and starting the local development server with hot module reloading.

Sources: [scripts/setup.js:1-244](), [package.json:5-31]()

---

## Environment Configuration

The application requires a `.env` file at the project root to configure database connections, authentication providers, and optional features. This file is not tracked in Git and can be generated via the interactive setup script `node scripts/setup.js` or manually created from template configurations [scripts/setup.js:1-244](), [package.json:20]().

### Minimum Required Variables

To run locally in development mode, specify at minimum:

```bash
# Database connection string (PostgreSQL)
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/prompts_chat?schema=public"

# Authentication secret (for signing sessions)
AUTH_SECRET="your-super-secret-key"
AUTH_URL="http://localhost:3000"
AUTH_TRUST_HOST=true
```

- `DATABASE_URL` must point to a running PostgreSQL instance.
- `AUTH_SECRET` is a 32-byte base64 string used for session encryption.
- `AUTH_URL` should match your local domain and port.

The application utilizes the Prisma client singleton pattern to manage database connections efficiently and prevent connection pool exhaustion during development and serverless operations [package.json:11-17]().

### Optional Environment Variables

The app supports several optional environment variables to enable OAuth providers and AI features. These variables correspond to settings enabled in `prompts.config.ts`.

| Category         | Variables                                      | Description                                    |
| ---------------- | ----------------------------------------------| ----------------------------------------------|
| GitHub OAuth     | `AUTH_GITHUB_ID`, `AUTH_GITHUB_SECRET`        | Enable GitHub login OAuth [scripts/setup.js:49-55]() |
| Google OAuth     | `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`        | Enable Google login OAuth [scripts/setup.js:57-63]() |
| Apple Sign In    | `AUTH_APPLE_ID`, `AUTH_APPLE_SECRET`           | Apple identity login [scripts/setup.js:64-71]() |
| Azure AD         | `AUTH_AZURE_AD_CLIENT_ID`, etc.                 | Microsoft Azure Active Directory [scripts/setup.js:72-80]() |
| AI Features      | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, etc.       | OpenAI API for embeddings, generation, and translation [scripts/setup.js:82-90]() |
| Cron Job Secret  | `CRON_SECRET`                                   | Secret for scheduling jobs like daily credit resets [scripts/setup.js:46]() |

Sources: [scripts/setup.js:21-90](), [package.json:11-17]()

---

## Configuration Injection Pipeline

The application configuration consists of two main artifacts generated by the interactive setup:

1. `prompts.config.ts` — TypeScript file exporting the full app configuration (`branding`, `theme`, `auth`, `i18n`, `features`). This is loaded at runtime using internal configuration helpers.
2. `.env` file — Environment variables consumed by Prisma, NextAuth, and various backend features.

### Setup Workflow Flowchart

Title: "Setup Workflow Flowchart"
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"["Natural Language Space"]
        UserIntent["Developer intent via CLI: E.g. Set branding, OAuth, domain"]
        SetupWizard["Interactive Setup Script scripts/setup.js"]
    end

    subgraph "CodeEntitySpace"["Code Entity Space"]
        ConfigTS["prompts.config.ts exports defineConfig object"]
        EnvFile[".env file process.env"]
        GetConfig["getConfig src/lib/config.ts"]
        PrismaClient["Prisma client singleton prisma"]
    end

    UserIntent --> SetupWizard
    SetupWizard -->|"Generates"| ConfigTS
    SetupWizard -->|"Generates"| EnvFile
    ConfigTS --> GetConfig
    EnvFile --> PrismaClient
    GetConfig --> App["Next.js Application"]
    PrismaClient --> App
```

The interactive wizard populates branding, authentication, and feature flags into `prompts.config.ts` and environment variables into `.env`. The configuration file is loaded lazily by the app via configuration utilities to provide runtime config access, while `.env` supplies backend and Prisma with necessary secrets.

Sources: [scripts/setup.js:95-164]()

---

## Database Setup and Initialization

`prompts.chat` uses Prisma ORM to manage database schema, migrations, and querying. The local database is PostgreSQL, configured via `DATABASE_URL`.

### Running Database Migrations and Seed

The recommended command to generate the Prisma client, apply migrations, and seed initial data is:

```bash
npm run db:setup
```

This runs the underlying scripts defined in `package.json`:

- `prisma generate` — regenerates the Prisma client
- `prisma migrate dev` — applies migrations locally
- `prisma db seed` — runs seed script to populate sample data

These scripts and commands are defined in `package.json` [package.json:11-19]().

### Seeding Data from Remote API

The seed script `prisma/seed.ts` fetches prompts data from the public API endpoint `https://prompts.chat/prompts.json?full_content=true`. It parses authors, categories, tags, and prompts, then upserts them into the local database, linking relationships appropriately. It also creates a default admin user (`admin@prompts.chat` with password `password123`) for local development use [prisma/seed.ts:1-221]().

### Reset Admin Password

Should you need to reset the admin user credentials at any time, execute:

```bash
npm run db:resetadmin
```

This invokes `prisma/reset-admin.ts`, resetting the admin password to `password123` and ensuring the admin account exists in the database [prisma/reset-admin.ts:1-40]().

### Prisma Studio GUI

For database inspection and editing, run:

```bash
npm run db:studio
```

This opens Prisma Studio at `http://localhost:5555`, allowing you to browse and edit database tables visually [package.json:14]().

Sources: [package.json:11-19](), [prisma/seed.ts:1-221](), [prisma/reset-admin.ts:1-40]()

---

## Database and Prisma Architecture

This diagram illustrates the interaction of commands, scripts, and Prisma client code to maintain and seed the database during local development, bridging natural language intent to code entities.

Title: "Database and Prisma Architecture"
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"["Natural Language Space"]
        NLCommand["User command prompt: npm run db:seed or db:resetadmin"]
    end

    subgraph "CodeEntitySpace"["Code Entity Space"]
        SeedCmd["npm run db:seed"]
        ResetCmd["npm run db:resetadmin"]
        StudioCmd["npm run db:studio"]
        PrismaClient["Prisma Client instance"]
        PromptModel["Prompt Model @prisma/client"]
        UserModel["User Model @prisma/client"]
        CategoryModel["Category Model @prisma/client"]
        SeedScript["Seed script prisma/seed.ts"]
        ResetScript["Reset Admin script prisma/reset-admin.ts"]
        PrismaCLI["Prisma CLI commands"]
    end

    NLCommand --> SeedCmd
    NLCommand --> ResetCmd
    NLCommand --> StudioCmd
    SeedCmd --> SeedScript
    ResetCmd --> ResetScript
    StudioCmd --> PrismaCLI
    SeedScript --> PrismaClient
    ResetScript --> PrismaClient
    PrismaClient --> PromptModel
    PrismaClient --> UserModel
    PrismaClient --> CategoryModel
```

Sources: [prisma/seed.ts:82-100](), [package.json:14-17]()

---

## Development Server Setup

### Starting the Dev Server

To run the Next.js local development server with hot module reloading:

```bash
npm run dev
```

This executes `next dev`, launching the app at `http://localhost:3000` [package.json:6]().

### Building for Production Locally

You can also build and serve a production bundle locally via:

```bash
npm run build
npm run start
```

- `build` runs `prisma generate` followed by `next build` [package.json:7]().
- `start` launches `next start` to serve the optimized production build [package.json:9]().

Sources: [package.json:6-9]()

---

## Available Scripts Overview

| Script          | Command                          | Purpose                               |
| --------------- | --------------------------------| ------------------------------------ |
| `dev`           | `next dev`                      | Start Next.js development server    |
| `setup`         | `node scripts/setup.js`          | Interactive configuration wizard    |
| `db:setup`      | `prisma generate && prisma migrate dev && prisma db seed` | Full DB migration and seed          |
| `db:migrate`    | `prisma migrate dev`             | Create and apply database migrations|
| `db:resetadmin` | `npx tsx prisma/reset-admin.ts`  | Reset admin user credentials        |
| `db:studio`     | `prisma studio`                  | Open Prisma database management UI  |
| `test`          | `vitest run`                    | Run unit tests                      |
| `test:ui`       | `vitest --ui`                   | Run tests with UI                   |
| `generate:examples` | `npx tsx scripts/generate-examples.ts` | Generate example data            |

Sources: [package.json:5-31]()

---

Sources:
- [scripts/setup.js:1-244]()
- [package.json:5-31]()
- [prisma/seed.ts:1-221]()
- [prisma/reset-admin.ts:1-40]()

---

# Page: Configuration Quickstart

# Configuration Quickstart

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [prisma/reset-admin.ts](prisma/reset-admin.ts)
- [prompts.config.ts](prompts.config.ts)
- [scripts/setup.js](scripts/setup.js)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



This page guides you through the configuration of a `prompts.chat` instance using the `prompts.config.ts` file, environment variables, and the interactive setup wizard. This system allows extensive white-labeling, theming, and feature toggling for customizable deployments.

---

## Purpose and Scope

The configuration system cleanly separates core application code from instance-specific settings. It enables:

- **White-labeling**: Customize branding (name, logos, description) exposed across the UI and metadata via the `BrandingConfig` interface [src/lib/config/index.ts:1-9]().
- **Theme Customization**: Configure UI radius, variant, density, and primary colors using `ThemeConfig` [src/lib/config/index.ts:11-22]().
- **Authentication Setup**: Enable one or more auth providers with registration control in `AuthConfig` [src/lib/config/index.ts:24-32]().
- **Internationalization**: Define supported locales and defaults through `I18nConfig` [src/lib/config/index.ts:34-37]().
- **Feature Flags**: Toggle features like AI search, MCP integration, comments, and change request workflows via `FeaturesConfig` [src/lib/config/index.ts:39-49]().
- **Runtime Configuration Overrides**: Use environment variables prefixed by `PCHAT_` to override config properties without rebuilding [src/lib/config/index.ts:117-185]().

Sources: [src/lib/config/index.ts:1-185](), [prompts.config.ts:1-106]()

---

## Configuration Data Flow

Configuration resolution occurs in three layers:

1. **Static Source Layer**: `prompts.config.ts`, `.env` file, and runtime environment variables.
2. **Config Loading Logic**: `getConfig()` dynamically imports the configuration and `applyEnvOverrides()` applies runtime `PCHAT_*` overrides [src/lib/config/index.ts:102-185]().
3. **Consuming Layers**: Server and client components fetch the configuration via `getConfig()` or synchronous access helpers [src/lib/config/index.ts:187-245]().

### Diagram: Configuration Resolution Pipeline

```mermaid
graph TD
    subgraph "Storage_Layer"
        ConfigTS["prompts.config.ts"]
        EnvFile[".env"]
        SystemEnv["ProcessEnvironment"]
    end

    subgraph "CodeEntitySpace:src/lib/config/index.ts"
        ImportConfig["import('@/../prompts.config')"]
        ApplyOverrides["applyEnvOverrides(baseConfig)"]
        GetConfig["getConfig()"]
    end

    subgraph "Consumer_Layer"
        ServerComp["RootLayout (server components)"]
        ClientComp["Header (client component)"]
    end

    ConfigTS --> ImportConfig
    ImportConfig --> GetConfig
    EnvFile --> SystemEnv
    SystemEnv --> ApplyOverrides
    GetConfig --> ApplyOverrides
    ApplyOverrides --> ServerComp
    ApplyOverrides --> ClientComp
```

Sources: [src/lib/config/index.ts:102-245](), [prompts.config.ts:1-106]()

---

## The `prompts.config.ts` Structure

The configuration file exports a default object via the `defineConfig()` helper ensuring proper typing and structure compliance with `PromptsConfig` [src/lib/config/index.ts:86-99]().

```ts
import { defineConfig } from "@/lib/config";

const useCloneBranding = false;

export default defineConfig({
  branding: { /* ... */ },
  theme: { /* ... */ },
  auth: { /* ... */ },
  i18n: { /* ... */ },
  features: { /* ... */ },
  homepage: { /* ... */ },
  announcement: null,
});
```

### Branding & Homepage Configuration

The `branding` section controls the application's identity:

| Property             | Type     | Description                                                                                   |
|----------------------|----------|-----------------------------------------------------------------------------------------------|
| `name`               | string   | Site title used in page `<title>`, header branding, meta descriptions.                        |
| `logo`               | string   | Path to light mode logo asset used in header and favicon fallback.                           |
| `logoDark`           | string?  | Optional dark mode logo override.                                                            |
| `favicon`            | string   | Path to favicon, used in browser tab icon.                                                  |
| `description`        | string   | Meta description for SEO and social sharing.                                                |
| `appStoreUrl`        | string?  | Link to iOS App Store (optional).                                                           |
| `chromeExtensionUrl` | string?  | Link to Chrome extension in the Chrome Web Store (optional).                               |

The `homepage.useCloneBranding` boolean flag controls hiding the default prompts.chat repository branding, replacing it with custom branding for private clones. If `true`, achievements and sponsors environment from the official repo are disabled.

Sources: [src/lib/config/index.ts:1-9](), [prompts.config.ts:3-18,70-92]()

### Theme System

The `theme` section defines the visual style across the application UI using these properties:

| Property         | Allowed Values                   | Description                                             |
|------------------|----------------------------------|---------------------------------------------------------|
| `radius`         | `"none" | "sm" | "md" | "lg"`   | Controls border-radius of UI elements.                   |
| `variant`        | `"flat" | "default" | "brutal"` | Defines visual styling variant for components.         |
| `density`        | `"compact" | "default" | "comfortable"` | Controls overall UI vertical/horizontal spacing.             |
| `colors.primary` | hex color or CSS oklch           | Primary brand color used globally in themes/buttons.    |

### Diagram: Natural Language to Code Entity Mapping: Theme

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        NL_Radius["UI Corner Radius"]
        NL_Variant["Visual Style Variant"]
        NL_Density["Component Spacing Density"]
        NL_Color["Primary Brand Color"]
    end

    subgraph "CodeEntitySpace:src/lib/config/index.ts"
        TR["radius: ThemeConfig['radius']"]
        TV["variant: ThemeConfig['variant']"]
        TD["density: ThemeConfig['density']"]
        TC["colors.primary: string"]
    end

    subgraph "ConsumerLayer"
        CFG["defineConfig()"]
        GetConfig["getConfig()"]
    end

    NL_Radius --> TR
    NL_Variant --> TV
    NL_Density --> TD
    NL_Color --> TC
    TR --> CFG
    TV --> CFG
    TD --> CFG
    TC --> CFG
    CFG --> GetConfig
```

Sources: [src/lib/config/index.ts:11-22](), [prompts.config.ts:21-32]()

### Authentication Plugins

The `auth` property configures authentication providers enabling user login:

| Property           | Type            | Description                                                     |
|--------------------|-----------------|-----------------------------------------------------------------|
| `providers`        | string[]        | Activated auth providers, e.g., `["github", "google", "apple"]`. |
| `allowRegistration`| boolean         | Whether new users can register (only affects credentials auth).  |

Sources: [src/lib/config/index.ts:24-32](), [prompts.config.ts:35-41]()

### Internationalization (i18n)

The i18n configuration sets locale options:

| Property        | Type       | Description                                                            |
|-----------------|------------|------------------------------------------------------------------------|
| `locales`       | string[]   | List of supported language locale codes, e.g., `["en", "tr", "es"]`.  |
| `defaultLocale` | string     | Default locale used if none specified.                                |

Sources: [src/lib/config/index.ts:34-37](), [src/lib/i18n/config.ts:1-24](), [prompts.config.ts:43-47]()

### Feature Flags

Feature flags enable or disable core capabilities:

| Flag              | Description                                                    |
|-------------------|----------------------------------------------------------------|
| `privatePrompts`  | Allow users to create private, undiscoverable prompts.        |
| `changeRequests`  | Enable community change request versioning workflow.          |
| `categories`      | Enable prompt categorization.                                 |
| `tags`            | Enable tagging system on prompts.                             |
| `aiSearch`        | Enable AI semantic prompt search (requires OpenAI key).       |
| `aiGeneration`    | Enable AI-powered prompt generation features.                  |
| `mcp`             | Enable Model Context Protocol API features.                    |
| `comments`        | Enable commenting on prompts.                                  |
| `promptEnhancer`  | Enable the AI Prompt Enhancer on `/developers` and `/api/improve-prompt` endpoint (requires OpenAI key). |

Sources: [src/lib/config/index.ts:39-49](), [prompts.config.ts:49-68]()

---

## Environment Variable Configuration (`.env`)

The `.env` file holds sensitive data and infrastructure URLs that must not be checked into source control. The interactive setup wizard generates this file securely.

### Core `.env` Variables

| Variable       | Description                                    | Origin                                    |
|----------------|------------------------------------------------|-------------------------------------------|
| `DATABASE_URL` | PostgreSQL connection URI for Prisma.          | Generated by setup wizard |
| `NEXTAUTH_SECRET`  | Secret used for session encryption and hashing.| Created randomly by setup wizard |
| `NEXTAUTH_URL` | Base URL for the app (http or https).          | Based on domain input |
| `CRON_SECRET`  | Secret used to protect scheduled cron jobs.   | Random 16-byte hex string |

Sources: [.env.example:1-115]()

### Runtime Overrides with `PCHAT_*`

You can override parts of the static configuration at runtime using environment variables prefixed with `PCHAT_`. These are processed by the `applyEnvOverrides` function [src/lib/config/index.ts:118-187]().

### Diagram: Natural Language to Code Entity Mapping: Runtime Overrides

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        NL_EnvName["Runtime App Name"]
        NL_EnvColor["Runtime Brand Color"]
        NL_EnvAuth["Runtime Auth Providers"]
        NL_EnvAI["Runtime AI Feature Flag"]
    end

    subgraph "CodeEntitySpace:src/lib/config/index.ts"
        EV_Name["env.PCHAT_NAME"]
        EV_Color["env.PCHAT_COLOR"]
        EV_Auth["env.PCHAT_AUTH_PROVIDERS"]
        EV_AI["env.PCHAT_FEATURE_AI_SEARCH"]
        AEO["applyEnvOverrides()"]
    end

    NL_EnvName --> EV_Name
    NL_EnvColor --> EV_Color
    NL_Auth --> EV_Auth
    NL_EnvAI --> EV_AI
    EV_Name --> AEO
    EV_Color --> AEO
    EV_Auth --> AEO
    EV_AI --> AEO
```

Sources: [src/lib/config/index.ts:117-185]()

---

## Interactive Setup Wizard

`prompts.chat` provides an interactive CLI setup script for smooth user-guided configuration.

### Usage

Run the setup wizard after installing dependencies:

```bash
npm run setup
```

### Key Features

- **Domain Configuration**: Asks for app domain to set `NEXTAUTH_URL`.
- **Database Connection**: Requests PostgreSQL host, port, database name, username, and password to generate `DATABASE_URL`.
- **Branding**: Prompts for organization/app name and description.
- **Theme Customization**: Pick radius, variant, density, primary color.
- **Authentication Providers**: Choose from GitHub, Google, Apple, Azure, and Credentials providers.
- **Feature Toggles**: Enable or disable AI search/generation, change requests, comments, etc.
- **Secrets Generation**: Generates strong random `NEXTAUTH_SECRET` and `CRON_SECRET`.

Sources: [scripts/setup.js:1-599](), [package.json:22-22]()

---

## Implementation Details

### `src/lib/config/index.ts`

- Defines interfaces describing config sections: `BrandingConfig`, `ThemeConfig`, `AuthConfig`, `I18nConfig`, `FeaturesConfig`, `HomepageConfig`, `AnnouncementConfig` [src/lib/config/index.ts:1-95]().
- Exports `defineConfig()` helper for type-safe configuration authoring [src/lib/config/index.ts:97-99]().
- Caches config in `cachedConfig` to avoid repeated dynamic imports [src/lib/config/index.ts:101-103]().
- `getConfig()` asynchronously imports `prompts.config.ts`, falls back to defaults if missing, and calls `applyEnvOverrides()` [src/lib/config/index.ts:189-220]().
- `applyEnvOverrides()` function processes `PCHAT_*` environment variables to dynamically alter the configuration [src/lib/config/index.ts:118-187]().

Sources: [src/lib/config/index.ts:1-245](), [prompts.config.ts:1-106]()

---

# Page: Docker Quick Start

# Docker Quick Start

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [DOCKER.md](DOCKER.md)
- [compose.yml](compose.yml)
- [docker/Dockerfile](docker/Dockerfile)
- [docker/entrypoint.sh](docker/entrypoint.sh)
- [scripts/docker-setup.js](scripts/docker-setup.js)
- [src/__tests__/api/improve-prompt.test.ts](src/__tests__/api/improve-prompt.test.ts)

</details>



**Purpose**: This page provides a concise technical guide for deploying `prompts.chat` in a Docker environment using a single command. It details the multi-stage Docker image build defined in `docker/Dockerfile`, Docker Compose orchestration in `compose.yml`, container entrypoint initialization for runtime setup in `docker/entrypoint.sh`, environment-driven configuration generation via `scripts/docker-setup.js`, and key runtime behaviors to enable quick self-hosting of the prompts.chat AI prompt library application [DOCKER.md:1-198](), [docker/Dockerfile:1-94](), [compose.yml:1-45](), [docker/entrypoint.sh:1-41](), [scripts/docker-setup.js:1-175]().

---

## Quick Start

The primary method for rapid deployment uses Docker Compose, which sets up both the prompts.chat Next.js app container and a persistent PostgreSQL database in one command [compose.yml:1-45]().

```bash
git clone https://github.com/f/prompts.chat.git
cd prompts.chat
docker compose up -d
```

- The app will be available at [http://localhost:4444](http://localhost:4444) by default [DOCKER.md:17-17](), [compose.yml:27-28]().
- By default, `compose.yml` pulls the official image `ghcr.io/f/prompts.chat:latest` [compose.yml:20-20]().
- To build the Docker image locally instead, add the `--build` flag:
  ```bash
  docker compose up -d --build
  ```

This command ensures you have all necessary containers running and database initialized without manual setup. The PostgreSQL data is persisted on a Docker volume named `postgres_data` [compose.yml:10-11](), [compose.yml:44-45]().

Sources: [DOCKER.md:7-27](), [compose.yml:1-45]()

---

## Container Architecture & Initialization

The official Docker image is a multi-stage build targeting a minimal, production-ready Next.js runtime, based on the `node:24-bookworm-slim` base image [docker/Dockerfile:1-94]().

### Multi-Stage Build Breakdown

- **base stage**: Sets up the base OS dependencies (`openssl`, `curl`, `ca-certificates`) and working directory `/app` [docker/Dockerfile:11-20]()
- **deps stage**: Installs NPM dependencies and runs `prisma generate` with a dummy `DATABASE_URL` [docker/Dockerfile:22-33]()
- **builder stage**: Copies source files and builds the Next.js production output (`npm run build`) [docker/Dockerfile:35-44]()
- **runner stage**: Copies the standalone Next.js server output, Prisma schema, and migrations, installs Prisma CLI for runtime migration support, and executes under a non-root `nextjs` user [docker/Dockerfile:46-94]()

### Container Entrypoint Process

The container entrypoint script `docker/entrypoint.sh` performs critical runtime checks and initialization [docker/entrypoint.sh:1-41]():

1. **Generate `AUTH_SECRET` if missing**: A 32-byte base64 random string is created at startup if not explicitly set, ensuring sessions work while recommending explicit production settings for persistence [docker/entrypoint.sh:4-10]().
2. **Wait for PostgreSQL readiness**: Uses a Node.js TCP socket script to poll port 5432 on the DB host, retrying up to 30 times with 2-second intervals [docker/entrypoint.sh:12-32]().
3. **Run database migrations**: Executes `npx prisma migrate deploy` to ensure the database schema matches deployed migrations [docker/entrypoint.sh:34-37]().
4. **Start the Next.js standalone server**: Runs `node server.js` as the `nextjs` user [docker/entrypoint.sh:39-41]().

### Execution Flow Diagram

```mermaid
flowchart TD
    subgraph NaturalLanguageSpace["Deployment Actions"]
        ComposeUp["docker compose up -d"]
    end

    subgraph CodeEntitySpace["Container Internals"]
        Entrypoint["docker/entrypoint.sh"]
        AuthSecret["Generate AUTH_SECRET if unset"]
        DBCheck["Wait for PostgreSQL port 5432"]
        Migrate["npx prisma migrate deploy"]
        ServerStart["Start Next.js server.js"]
        PostgresDB["PostgreSQL Container prompts DB"]
    end

    ComposeUp --> Entrypoint
    Entrypoint --> AuthSecret
    AuthSecret --> DBCheck
    DBCheck --> PostgresDB
    Entrypoint --> Migrate
    Migrate --> PostgresDB
    Entrypoint --> ServerStart
```
**Title**: "Docker Compose Application Initialization Flow"

Sources: [docker/entrypoint.sh:1-41](), [docker/Dockerfile:1-94](), [compose.yml:1-45]()

---

## Runtime Configuration & Branding

`prompts.chat` configuration is primarily driven through environment variables prefixed with `PCHAT_`, which map to keys in `prompts.config.ts`. This enables dynamic branding, theming, authentication providers, localization, and feature flags without rebuilding the container [DOCKER.md:67-136]().

### Configuration Pipeline Overview

```mermaid
classDiagram
    class EnvironmentVariables {
        <<System Environment>>
        +PCHAT_NAME
        +PCHAT_DESCRIPTION
        +PCHAT_COLOR
        +PCHAT_AUTH_PROVIDERS
        +PCHAT_FEATURE_AI_SEARCH
    }
    class ConfigGenerator {
      <<Script>>
      +scripts/docker-setup.js
      +env()
      +envBool()
      +envArray()
      +generateConfig()
    }
    class ConfigFile {
      <<Code Entity>>
      +prompts.config.ts
      +defineConfig()
    }
    EnvironmentVariables --> ConfigGenerator: "Read via process.env"
    ConfigGenerator --> ConfigFile: "Writes prompts.config.ts"
```
**Title**: "Docker Configuration Generation Flow"

- The script `scripts/docker-setup.js` generates a customized `prompts.config.ts` by reading container environment variables at build time or entry [scripts/docker-setup.js:4-33](), [scripts/docker-setup.js:122-175]().
- It supports string, boolean, and comma-separated list variables for fine-grained config control and writes the code defining the config with `defineConfig` [scripts/docker-setup.js:40-54](), [scripts/docker-setup.js:56-119]().

Sources: [scripts/docker-setup.js:1-175]()

### Key Environment Variables and Defaults

| Env Variable               | Config Path                | Default              | Description                                |
|----------------------------|----------------------------|----------------------|--------------------------------------------|
| `PCHAT_NAME`                | `branding.name`             | `"My Prompt Library"` | App display name                           |
| `PCHAT_DESCRIPTION`         | `branding.description`      | `"Collect, organize..."` | App description                           |
| `PCHAT_COLOR`               | `theme.colors.primary`      | `"#6366f1"`          | Primary UI color hex                        |
| `PCHAT_THEME_RADIUS`        | `theme.radius`              | `"sm"`               | Border radius options: none, sm, md, lg   |
| `PCHAT_AUTH_PROVIDERS`      | `auth.providers`            | `"credentials"`      | Comma-separated auth providers (`github`, `google`, `credentials`) |
| `PCHAT_FEATURE_AI_SEARCH`   | `features.aiSearch`         | `false`              | Enable AI semantic search                   |
| `PCHAT_FEATURE_MCP`         | `features.mcp`              | `false`              | Enable Model Context Protocol features     |
| `PCHAT_FEATURE_PROMPT_ENHANCER` | `features.promptEnhancer` | `true`               | Enable the Prompt Enhancer on `/developers` and `/api/improve-prompt` (requires `OPENAI_API_KEY`) [DOCKER.md:135-135]() |

Sources: [DOCKER.md:90-136](), [scripts/docker-setup.js:125-158]()

---

## Advanced Deployment & Maintenance

### Standalone Deployment (Bring Your Own Database)

You can build the image locally and run it with your own PostgreSQL instance, bypassing Docker Compose [DOCKER.md:29-65]():

```bash
docker build -f docker/Dockerfile -t prompts.chat .
docker run -d \
  --name prompts \
  -p 4444:3000 \
  -e DATABASE_URL="postgresql://user:pass@your-db-host:5432/prompts?schema=public" \
  -e AUTH_SECRET="$(openssl rand -base64 32)" \
  prompts.chat
```

Alternatively, run the official pre-built image:

```bash
docker run -d \
  --name prompts \
  -p 4444:3000 \
  -e DATABASE_URL="postgresql://user:pass@your-db-host:5432/prompts?schema=public" \
  -e AUTH_SECRET="$(openssl rand -base64 32)" \
  ghcr.io/f/prompts.chat:latest
```

This setup supports complete control of the database backend, useful for external cloud providers or existing database clusters [DOCKER.md:29-65]().

Sources: [DOCKER.md:29-65](), [docker/Dockerfile:7-9]()

---

### Production Security & Maintenance Recommendations

| Consideration                    | Details & Commands                                                    |
|--------------------------------|----------------------------------------------------------------------|
| **Set AUTH_SECRET explicitly** | Generate and set persistently to maintain session continuity across restarts: |
|                                | ```bash                                                            |
|                                | export AUTH_SECRET=$(openssl rand -base64 32)                     |
|                                | docker compose up -d                                               |
|                                | ```                                                                |
| **Change default DB password** | Override `POSTGRES_PASSWORD` environment variable in `compose.yml`  |
| **Database Backup**             | Backup persistent volume with:                                      |
|                                | ```bash                                                            |
|                                | docker compose exec db pg_dump -U prompts prompts > backup.sql     |
|                                | ```                                                                |

Sources: [DOCKER.md:146-156](), [compose.yml:5-45]()

---

### Troubleshooting Commands

| Task                             | Command                                |
|----------------------------------|--------------------------------------|
| View application logs            | `docker compose logs -f app`          |
| Access PostgreSQL shell          | `docker compose exec db psql -U prompts -d prompts` |
| Seed database with examples      | `docker compose exec app npx prisma db seed` |
| Verify application health check  | `curl http://localhost:4444/api/health` |

Sources: [DOCKER.md:191-198](), [docker/Dockerfile:89-90](), [compose.yml:12-17]()

---

# Page: Core Architecture

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [prompts.config.ts](prompts.config.ts)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



## Purpose and Scope

This page serves as the parent overview for core system architecture concepts in `prompts.chat`. It establishes the high-level design patterns, persistence strategy, configuration pipeline, and component relationships that bridge natural language prompt engineering with a robust technical stack.

For detailed information on specific architectural sub-topics, refer to the child pages:
- CSV synchronization and attribution mechanics: see [CSV Sync System & Contributor Attribution](#3.1)
- Next.js App Router layout and file organization: see [Application Structure](#3.2)
- Configuration loading pipeline and environment variables: see [Configuration System](#3.3)
- Prisma ORM models and relationship graphs: see [Database Schema](#3.4)
- Plugin architecture for storage, auth, and media generation: see [Plugin Architecture](#3.5)

---

## Architectural Principles

`prompts.chat` relies on three fundamental design pillars:

1.  **Dual Persistence Model**: Prompts are stored in a relational PostgreSQL database accessed through Prisma ORM in `src/lib/db.ts` [src/lib/db.ts:1-27]() for efficient queries and transactional integrity, while simultaneously syncing with flat-file CSVs (`prompts.csv`) and Markdown (`PROMPTS.md`) files to enable open-source community contributions through GitHub pull requests.

2.  **Configuration-Driven Customization**: The application dynamically adapts branding, theming, feature toggles, and external API keys through a sophisticated configuration loading pipeline defined in `src/lib/config/index.ts` [src/lib/config/index.ts:98-187](). This includes static configuration files (`prompts.config.ts`) [prompts.config.ts:1-106]() and runtime overrides via environment variables prefixed with `PCHAT_*` [src/lib/config/index.ts:106-132]().

3.  **Safety and Quality Gates**: Incoming prompt submissions undergo strict validation with Zod schemas and helper utilities in `src/lib/config/index.ts` [src/lib/config/index.ts:1-100](), duplicate and similarity detection, rate limiting, and user flag checks before creating or updating database records. These ensure data quality and prevent spam or abuse.

Sources: [src/lib/config/index.ts:1-187](), [src/lib/db.ts:1-27](), [prompts.config.ts:1-106]()

---

## System Architecture Overview

Below is a conceptual diagram bridging the **Natural Language Space**—the user inputs and prompt files—with the **Code Entity Space**—the corresponding source code modules, validation schemas, database entities, and UI components:

Title: "System Architecture Bridge"
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        UserPromptInput["UserPromptInput UI"]
        PromptMarkdownFiles["prompts.csv & PROMPTS.md"]
    end

    subgraph "CodeEntitySpace"
        ApiRoute["POST src/app/api/prompts/route.ts"]
        ConfigIndex["getConfig src/lib/config/index.ts"]
        PrismaClient["db src/lib/db.ts"]
        RootLayout["RootLayout src/app/layout.tsx"]
    end

    UserPromptInput --> ApiRoute
    PromptMarkdownFiles --> ApiRoute
    ApiRoute --> ConfigIndex
    ConfigIndex --> PrismaClient
    RootLayout --> PrismaClient
```

This diagram illustrates how user-submitted prompts or changes to prompt markdown files initiate API route handlers, validated by configuration settings from `src/lib/config/index.ts` [src/lib/config/index.ts:189](), and then result in database transactions via the Prisma client in `src/lib/db.ts` [src/lib/db.ts:24](). The React server components (`src/app/layout.tsx` [src/app/layout.tsx:144-156]()) retrieve prompt data to render the UI pages.

Sources: [src/app/layout.tsx:144-156](), [src/lib/config/index.ts:189](), [src/lib/db.ts:24]()

---

## Core Subsystems Overview

### 1. Dual Persistence & CSV Sync

The prompt data is persisted through a hybrid model combining a PostgreSQL relational database and flat CSV files. The database holds rich, normalized data including prompt versions, contributors, tags, categories, media URLs, and metadata, enabling performant searches, versioning, and relations.

Simultaneously, flat CSV (`prompts.csv`) and Markdown files (`PROMPTS.md`) allow contributions via GitHub workflows. The `generate-contributors.sh` script helps maintain author attribution in Git commits with `Co-authored-by` trailers. This dual system balances database efficiency with open collaboration.

- For full details, see [CSV Sync System & Contributor Attribution](#3.1).

Sources: [src/lib/db.ts:1-27]()

### 2. Application Structure & Routing

Built on Next.js App Router, the codebase organizes logic into server components, API route handlers, and page routes for prompt browsing, viewing, and editing. For example, the root layout at `src/app/layout.tsx` [src/app/layout.tsx:144-196]() fetches theme configurations, locale information, and messages via `next-intl/server`, rendering headers, announcement banners (`src/components/layout/announcement-banner.tsx` [src/components/layout/announcement-banner.tsx:10-14]()), and dynamic content providers.

Client components such as the header (`src/components/layout/header.tsx` [src/components/layout/header.tsx:111-173]()) and masonry grid layouts (`src/components/ui/masonry.tsx` [src/components/ui/masonry.tsx:17-22]()) handle responsive navigation, language switching, theme application, and fluid content arrangement.

- For full details, see [Application Structure](#3.2).

Sources: [src/app/layout.tsx:144-196](), [src/components/layout/announcement-banner.tsx:10-14](), [src/components/layout/header.tsx:111-173](), [src/components/ui/masonry.tsx:17-22]()

### 3. Configuration & Overrides

The configuration pipeline is essential for runtime adaptability. A central configuration file (`prompts.config.ts`) [prompts.config.ts:1-106]() defines defaults (branding, themes, features), which are dynamically overridden by environment variables prefixed with `PCHAT_*` via `applyEnvOverrides` in `src/lib/config/index.ts` [src/lib/config/index.ts:118-187](). Runtime helpers `getConfig` [src/lib/config/index.ts:189]() provide access to the merged config state. The `hexToOklch` function in `src/app/layout.tsx` [src/app/layout.tsx:120-142]() is used to convert primary colors for dynamic CSS variable theming.

This system enables white-labeling, feature flags, API credentials, and environment-specific tuning without source changes.

- For full details, see [Configuration System](#3.3).

Sources: [prompts.config.ts:1-106](), [src/lib/config/index.ts:118-198](), [src/app/layout.tsx:120-142]()

### 4. Database Schema

The Prisma schema models rich domain concepts:

-   `Prompt`: Stores prompt metadata including title, content, type, privacy, media requirements, and relations.
-   `PromptVersion`: Tracks version history and change notes for prompts.
-   `User`: Stores user accounts with roles, generation credits, API keys, and flags.
-   `Category`, `Tag`, and `PromptConnection`: Support categorization, tagging, and prompt workflow relations.
-   `ChangeRequest`: Manages user-submitted change proposals pending moderation.

The `db` instance in `src/lib/db.ts` [src/lib/db.ts:14-17]() is configured to omit prompt embeddings by default for performance optimization across server-rendered pages and API endpoints.

- For full details, see [Database Schema](#3.4).

Sources: [src/lib/db.ts:14-17]()

### 5. Plugin Architecture

The modular plugin system located in `src/lib/plugins` facilitates extensibility:

-   Authentication providers support OAuth and credentials-based logins, configured in `prompts.config.ts` [prompts.config.ts:34-41]().
-   Storage backends enable S3, DigitalOcean Spaces, or local storage for media, configured via environment variables in `.env.example` [.env.example:25-39]().
-   Media generators integrate AI-based generation with `fal` and `wiro` provider configurations, also via environment variables [.env.example:56-65]().
-   UI widget registries allow homepage customization, such as the `AnnouncementBanner` [src/components/layout/announcement-banner.tsx:10-14]() which uses the `AnnouncementConfig` [src/lib/config/index.ts:71-85]() from the config system.

This design supports pluggable future integrations and scalability.

- For full details, see [Plugin Architecture](#3.5).

Sources: [.env.example:25-65](), [prompts.config.ts:34-41](), [src/components/layout/announcement-banner.tsx:10-14](), [src/lib/config/index.ts:71-85]()

---

## Data Flow & Persistence Pipeline

This diagram maps the flow of prompt data through the system during creation or update operations, bridging natural language submission layers with persistence code entities:

Title: "Data Flow Pipeline"
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        User["User Client Input"]
        MarkdownSync["prompts.csv Sync"]
    end

    subgraph "CodeEntitySpace"
        ConfigLoader["getConfig src/lib/config/index.ts"]
        PrismaClient["db src/lib/db.ts"]
        PostgresDB["PostgreSQL Database"]
    end

    User --> ConfigLoader
    MarkdownSync --> ConfigLoader
    ConfigLoader --> PrismaClient
    PrismaClient --> PostgresDB
```

Users and synchronization scripts submit prompt data which is governed by configuration loading pipelines (`src/lib/config/index.ts` [src/lib/config/index.ts:189]()). Upon successful validation and safety checks, Prisma ORM (`src/lib/db.ts` [src/lib/db.ts:24]()) persists changes into the PostgreSQL database.

Sources: [src/lib/config/index.ts:189](), [src/lib/db.ts:24]()

---

This overview outlines how `prompts.chat` integrates user-friendly natural language inputs and community workflows with a performant, scalable backend architecture based on Next.js, PostgreSQL, Prisma, and a configuration-driven plugin ecosystem. Each child page drills into the technical details of these subsystems for contributor and developer reference.

---

# Page: CSV Sync System & Contributor Attribution

# CSV Sync System & Contributor Attribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [PROMPTS.md](PROMPTS.md)
- [README.md](README.md)
- [next.config.ts](next.config.ts)
- [prompts.csv](prompts.csv)
- [scripts/generate-contributors.sh](scripts/generate-contributors.sh)
- [scripts/rebuild-history.sh](scripts/rebuild-history.sh)
- [src/app/prompts.csv/route.ts](src/app/prompts.csv/route.ts)
- [src/app/prompts.json/route.ts](src/app/prompts.json/route.ts)
- [src/components/admin/import-prompts.tsx](src/components/admin/import-prompts.tsx)
- [tests/generate-contributors-format.test.js](tests/generate-contributors-format.test.js)

</details>



This page explains the pipeline that keeps `prompts.csv` in sync with the live database, attributes each prompt to its contributor as a distinct git commit, updates `PROMPTS.md`, and prepares the data for external platforms like Hugging Face. It covers the CSV export route (`src/app/prompts.csv/route.ts`), the automated synchronization script (`scripts/generate-contributors.sh`), and the contributor attribution logic.

For the reverse direction—loading `prompts.csv` back into the database—see the admin import system described in [src/components/admin/import-prompts.tsx:35-100](). For how prompts are created in the first place, see [README.md:68-68]().

---

## Overview

The canonical copy of all public prompts lives in two synchronized tiers:

| Location     | Role                                                                 | Code Representation                |
|--------------|----------------------------------------------------------------------|----------------------------------|
| PostgreSQL   | Live write store; primary source of truth for the web application.   | `db.prompt` via Prisma            |
| `prompts.csv`| Derived canonical snapshot; public record with git-level attribution.| `prompts.csv` root field           |

The synchronization process bridges user actions in the web UI to repository commits, ensuring transparent authorship and contributor stats [README.md:68-68]().

**System-level data flow diagram (Natural Language Space to Code Entity Space):**

Title: CSV Sync and Attribution Pipeline
```mermaid
sequenceDiagram
    participant DB as "db.prompt.findMany()"
    participant ROUTE as "src/app/prompts.csv/route.ts"
    participant SH as "scripts/generate-contributors.sh"
    participant PYTHON as "Embedded Python diff logic"
    participant GIT as "prompts.csv + PROMPTS.md"
    participant HF as "Hugging Face Dataset"

    Note over SH: "Triggered by CI/CD or Manual"
    SH->>ROUTE: "curl -fsSL prompts.chat/prompts.csv"
    ROUTE->>DB: "WHERE isPrivate=false AND isUnlisted=false AND deletedAt=null"
    DB-->>ROUTE: "Prompt[] with author + contributors"
    ROUTE-->>SH: "CSV payload -> prompts.csv.remote"
    SH->>PYTHON: "Read and diff CSVs by 'act' key"
    loop For each changed prompt
        PYTHON->>PYTHON: "parse_contributors() -> primary_author + co_authors"
        PYTHON->>GIT: "git_commit() with --author=primary_author + Co-authored-by trailers"
        PYTHON->>GIT: "update_prompt_in_md() -> PROMPTS.md"
    end
    SH->>HF: "Sync prompts.csv to Hugging Face dataset"
```

Sources: [scripts/generate-contributors.sh:1-22](), [src/app/prompts.csv/route.ts:28-95](), [README.md:24-24]()

---

## CSV Export Endpoint (`src/app/prompts.csv/route.ts`)

The Next.js route handler at `src/app/prompts.csv/route.ts` dynamically generates the CSV snapshot consumed by sync scripts and external platforms [src/app/prompts.csv/route.ts:28-95]().

### Query Filters

To prevent private or deleted content from leaking into the public repository, `GET()` queries Prisma with strict filters:

| Filter        | Value   | Code Location                       |
|---------------|---------|-----------------------------------|
| `isPrivate`   | `false` | [src/app/prompts.csv/route.ts:33]() |
| `isUnlisted`  | `false` | [src/app/prompts.csv/route.ts:34]() |
| `deletedAt`   | `null`  | [src/app/prompts.csv/route.ts:35]() |

Results are ordered by `createdAt` ascending to maintain stable append order [src/app/prompts.csv/route.ts:62-62]().

Sources: [src/app/prompts.csv/route.ts:29-63]()

### Output Columns & Mapping

Each prompt is mapped to the five-column CSV schema, with content properly escaped by `escapeCSVField()` [src/app/prompts.csv/route.ts:5-16]():

| CSV Column   | Source Field                               | Transformation / Logic                                           |
|--------------|--------------------------------------------|-----------------------------------------------------------------|
| `act`        | `prompt.title`                             | Escaped prompt title                                            |
| `prompt`     | `prompt.content`                           | Escaped prompt body                                             |
| `for_devs`   | `prompt.category.slug`                     | `"TRUE"` if category slug equals `"coding"`, otherwise `"FALSE"`|
| `type`       | `prompt.structuredFormat`                  | `"STRUCTURED"` if JSON/YAML, else `"TEXT"`                      |
| `contributor`| Concatenation of author and contributors  | Comma-separated identifiers using `getUserIdentifier()`         |

The contributor list concatenates the prompt's author followed by co-contributors, excluding duplicates [src/app/prompts.csv/route.ts:72-80]().

Sources: [src/app/prompts.csv/route.ts:65-83]()

### `getUserIdentifier()` Logic

This helper determines the immutable contributor identity string. Its priority is:

1. Use GitHub username if set (GitHub OAuth users)
2. If email ends with `@unclaimed.prompts.chat`, use username (imported GitHub contributors)
3. Otherwise, use email (Google or credential-based users)

This guarantees consistency and prevents impersonation via username/email switches [src/app/prompts.csv/route.ts:18-25]().

Title: Contributor Identity Resolution
```mermaid
flowchart TD
    A["getUserIdentifier(user)"] --> B{"user.githubUsername set?"}
    B -- "Yes" --> C["return githubUsername"]
    B -- "No" --> D{"email ends with<br/>@unclaimed.prompts.chat?"}
    D -- "Yes" --> E["return username<br/>(Imported GitHub contributor)"]
    D -- "No" --> F["return email<br/>(Google / Credentials user)"]
```

Sources: [src/app/prompts.csv/route.ts:18-25]()

---

## Contributor Generation Script (`scripts/generate-contributors.sh`)

The core synchronization logic runs through `scripts/generate-contributors.sh`. This shell script fetches the remote CSV from the live website, compares it with the local copy, and applies git commits incrementally for any changes, assigning proper contributor authorship [scripts/generate-contributors.sh:15-43]().

### Python Diff & Commit Logic

Embedded within the shell script is a Python program that:

- Reads the local `prompts.csv` and remote `prompts.csv.remote` into ordered lists keyed by the `act` field [scripts/generate-contributors.sh:54-74]()
- Detects additions or updates by comparing normalized rows [scripts/generate-contributors.sh:88-90]()
- Parses contributor fields into a primary author and optional co-authors [scripts/generate-contributors.sh:94-100]()
- Updates the `prompts.csv` local file and synchronizes to `PROMPTS.md` [scripts/generate-contributors.sh:76-83](), [scripts/generate-contributors.sh:182-193]()
- Makes a git commit per changed prompt, setting environment variables for `GIT_AUTHOR_*` and `GIT_COMMITTER_*` [scripts/generate-contributors.sh:116-130]()
- Adds `Co-authored-by` trailers for multi-author commits [scripts/generate-contributors.sh:108-114]()

Title: Git Author Attribution Flow
```mermaid
flowchart TD
    CSV["CSV contributor field:<br/>'alice,bob,carol'"] --> PARSE["parse_contributors()"]
    PARSE --> PRIMARY["primary_author = 'alice'"]
    PARSE --> COAUTH["co_authors = ['bob', 'carol']"]
    PRIMARY --> ENV["Set environment:<br/>GIT_AUTHOR_NAME='alice'<br/>GIT_AUTHOR_EMAIL='alice@users.noreply.github.com'"]
    ENV --> COMMIT["git commit -m 'Add prompt: {act}'<br/>--author='alice <alice@users.noreply.github.com>'"]
    COAUTH --> TRAILER["Append trailers via build_commit_msg():<br/>Co-authored-by: bob <bob@users.noreply.github.com>"]
    TRAILER --> COMMIT
```

Sources: [scripts/generate-contributors.sh:38-130]()

### Key Functions in Python Script

- `read_csv(path)`: Reads a CSV file into an ordered list of rows and an index map keyed by `act` [scripts/generate-contributors.sh:54-74]()
- `write_csv(rows, fieldnames, path)`: Writes CSV files deterministically to ensure git-friendly diffs [scripts/generate-contributors.sh:76-83]()
- `parse_contributors(field)`: Splits and cleans contributor strings into primary and co-authors [scripts/generate-contributors.sh:94-100]()
- `build_commit_msg(action, act, co_authors)`: Prepares commit messages with `Co-authored-by` trailers [scripts/generate-contributors.sh:108-114]()
- `git_commit(author_name, author_email, message)`: Stages files and creates git commits with specific author metadata [scripts/generate-contributors.sh:116-130]()

Sources: [scripts/generate-contributors.sh:54-130]()

---

## `PROMPTS.md` Synchronization

Alongside `prompts.csv`, the synchronization script also updates `PROMPTS.md` to keep the markdown version aligned:

- `generate_prompt_block(row)`: Creates a `<details>` block with a summary and markdown fenced code highlighting based on prompt type (`md`, `json`, `yaml`) [scripts/generate-contributors.sh:155-173]()
- `format_contributor_links(contributor_field)`: Parses contributor entries and renders GitHub profile links or falls back to `@anonymous` for emails or invalid usernames [scripts/generate-contributors.sh:137-154]()
- `append_prompt_to_md(row)` and `update_prompt_in_md(row)`: Initialize or update the markdown file with new or updated prompt blocks [scripts/generate-contributors.sh:182-193]()

The script ensures consistent formatting and contributor attribution visible on the GitHub-hosted `PROMPTS.md`.

This formatting and contributor mapping functionality is verified through unit tests in `tests/generate-contributors-format.test.js` which check for normalization, anonymous fallback, and GitHub username validation [tests/generate-contributors-format.test.js:1-26]().

Sources: [scripts/generate-contributors.sh:137-201](), [tests/generate-contributors-format.test.js:1-26]()

---

## History Management & Automation

### One-Time History Rebuild (`scripts/rebuild-history.sh`)

At project inception, a one-time script was run to reconstruct the git history of `prompts.csv` with granular commit ownership per prompt and proper contributor attribution:

- The script removes `prompts.csv` from git (without deleting the file) [scripts/rebuild-history.sh:101-102]()
- Recreates `prompts.csv` incrementally, committing each prompt row with `GIT_AUTHOR_*` set to the respective contributor [scripts/rebuild-history.sh:118-151]()
- Uses the same `Co-authored-by` commit trailers for co-authors [scripts/rebuild-history.sh:88-98]()
- Outputs instructions to force push the rewritten history [scripts/rebuild-history.sh:154-155]()

Sources: [scripts/rebuild-history.sh:1-170]()

### CI/CD Automation

Ongoing synchronization and contributor commit generation runs automatically in CI/CD (GitHub Actions `.github/workflows/update-contributors.yml`), which runs `scripts/generate-contributors.sh` periodically, pushes updated `prompts.csv` and `PROMPTS.md` commits, and syncs the dataset to Hugging Face [README.md:24-24]().

Sources: [README.md:24-24]()

---

## Summary

This dual architecture leverages the relational PostgreSQL database as the live source of truth while maintaining a git-tracked CSV snapshot `prompts.csv` optimized for transparent contributor attribution and public distribution.

The CSV is published by the Next.js API route, consumed and compared by an automated shell + embedded Python sync script, which commits incremental updates and generates the markdown variant `PROMPTS.md`. Git commit authorship is set per prompt according to its original contributor data with `Co-authored-by` trailers for co-authors.

Sources: [scripts/generate-contributors.sh:1-130](), [src/app/prompts.csv/route.ts:28-95]()

---

## Additional Diagram: Natural Language Entities to Code Artifacts

Title: System Components from Natural Terminology to Codebase

```mermaid
flowchart TD
    NL1["Natural Language: Prompt Collection"] --> DB["Code: db.prompt (Prisma model)"]
    DB --> ROUTE["Code: src/app/prompts.csv/route.ts"]
    ROUTE --> CSV["File: prompts.csv (Flat file)"]
    CSV -.-> SYNC["Script: scripts/generate-contributors.sh"]
    SYNC --> PY["Embedded Python: CSV diff & git commit logic"]
    SYNC --> MD["File: PROMPTS.md (Markdown)"]
    SYNC --> GIT["Git: Commits with Co-authored-by trailers"]
    GIT --> GH["GitHub: Web UI & Contribution Graph"]
    SYNC --> HF["Hugging Face Dataset Import"]
```

Sources: [scripts/generate-contributors.sh:1-130](), [src/app/prompts.csv/route.ts:28-95](), [README.md:24-24]()

---

## Additional Diagram: CSV Contributor String to Commit Attribution Flow

Title: Contributor String Parsing and Commit Generation

```mermaid
flowchart TD
    CSV_STR["CSV field: 'alice,bob,@carol'"] --> PARSE["parse_contributors()"]
    PARSE --> PRIMARY["Primary author: 'alice'"]
    PARSE --> COAUTH["Co-authors: ['bob', 'carol']"]
    PRIMARY --> SETENV["Set GIT_AUTHOR_NAME / EMAIL env variables"]
    SETENV --> COMMIT["Git commit with --author and commit message"]
    COAUTH --> TRAILERS["Generate 'Co-authored-by' commit trailers"]
    TRAILERS --> COMMIT
```

Sources: [scripts/generate-contributors.sh:94-130]()

---

# Page: Application Structure

# Application Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [prompts.config.ts](prompts.config.ts)
- [src/app/[username]/loading.tsx](src/app/[username]/loading.tsx)
- [src/app/discover/loading.tsx](src/app/discover/loading.tsx)
- [src/app/feed/loading.tsx](src/app/feed/loading.tsx)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/app/promptmasters/loading.tsx](src/app/promptmasters/loading.tsx)
- [src/app/prompts/[id]/loading.tsx](src/app/prompts/[id]/loading.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



This document outlines the architectural patterns, directory organization, routing structure, loading states, layout management, and server/client component boundaries of the `prompts.chat` codebase built on Next.js 16 App Router.

---

## Directory Structure Overview

The codebase follows Next.js 16 App Router conventions under `src/` and organizes application code into views, layouts, server actions, API routes, shared components, and utility libraries.

```
src/
├── app/                    # Next.js App Router root
│   ├── layout.tsx         # Root layout with server-side theme and provider initialization [src/app/layout.tsx:144-208]()
│   ├── prompts/           # Prompt catalog and dynamic detail views
│   ├── promptmasters/     # Leaderboard views [src/app/promptmasters/loading.tsx:1-39]()
│   ├── feed/              # User personalized feed views [src/app/feed/loading.tsx:1-28]()
│   └── api/               # API endpoint route handlers
├── components/            # React UI components
│   ├── ui/               # Reusable base components (e.g., Masonry layout) [src/components/ui/masonry.tsx:1-184]()
│   ├── layout/           # Structural layout pieces (Header, Footer, banners) [src/components/layout/header.tsx:111-186](), [src/components/layout/announcement-banner.tsx:1-82]()
│   └── providers/        # Context providers and locale detectors [src/app/layout.tsx:189]()
├── lib/                   # Utility functions and core configuration
│   ├── db.ts             # Prisma client singleton implementation [src/lib/db.ts:1-27]()
│   ├── config/           # Runtime configuration loader and types [src/lib/config/index.ts:1-248]()
│   └── i18n/             # Internationalization and localization config [src/lib/i18n/config.ts:1-24]()
└── prompts.config.ts      # Site configuration and branding options [prompts.config.ts:1-106]()
```

Sources: `[src/app/layout.tsx:144-208](), [src/app/promptmasters/loading.tsx:1-39](), [src/app/feed/loading.tsx:1-28](), [src/components/ui/masonry.tsx:1-184](), [src/components/layout/header.tsx:111-186](), [src/components/layout/announcement-banner.tsx:1-82](), [src/lib/db.ts:1-27](), [src/lib/config/index.ts:1-248](), [src/lib/i18n/config.ts:1-24](), [prompts.config.ts:1-106]()`

---

## App Router Architecture

### Route-to-File Mapping and Natural Language to Code Entities

The Next.js 16 App Router maps physical files inside `src/app/` to HTTP endpoints and React Server Components. Dynamic segments like `[id]` handle individual resource views. Special files such as `loading.tsx` handle suspense boundaries for asynchronous route chunks.

Title: "Natural Language to Code Entity Mapping: Routes and Components"
```mermaid
graph TB
    subgraph NaturalLanguageSpace
        PromptDetailReq[""Prompt Detail View""]
        LeaderboardReq[""Promptmasters Leaderboard""]
        FeedReq[""Personalized Feed View""]
        LayoutConfigReq[""Root Layout & Theming""]
    end

    subgraph CodeEntitySpace
        PromptDetailLoading[""src/app/prompts/[id]/loading.tsx""]
        PromptmastersLoadingFile[""src/app/promptmasters/loading.tsx""]
        FeedLoadingFile[""src/app/feed/loading.tsx""]
        RootLayoutFile[""src/app/layout.tsx""]
        ConfigIndex[""src/lib/config/index.ts""]
    end

    PromptDetailReq --> PromptDetailLoading
    LeaderboardReq --> PromptmastersLoadingFile
    FeedReq --> FeedLoadingFile
    LayoutConfigReq --> RootLayoutFile
    RootLayoutFile --> ConfigIndex
```

Sources: `[src/app/layout.tsx:144-208](), [src/app/prompts/[id]/loading.tsx:1-54](), [src/app/promptmasters/loading.tsx:1-39](), [src/app/feed/loading.tsx:1-28](), [src/lib/config/index.ts:1-248]()`

| File Entity Path                | Target Route         | Purpose                                             |
|-------------------------------|----------------------|-----------------------------------------------------|
| `src/app/layout.tsx`           | `/*` (root and children) | Root layout with theme, locales, and providers `[src/app/layout.tsx:144-208]()` |
| `src/app/prompts/[id]/loading.tsx` | `/prompts/[id]`    | Suspense skeleton loader for prompt details `[src/app/prompts/[id]/loading.tsx:1-54]()` |
| `src/app/promptmasters/loading.tsx` | `/promptmasters` | Leaderboard loading skeleton `[src/app/promptmasters/loading.tsx:1-39]()` |
| `src/app/feed/loading.tsx` | `/feed`               | Feed loading skeleton `[src/app/feed/loading.tsx:1-28]()` |

Sources: `[src/app/layout.tsx:144-208](), [src/app/prompts/[id]/loading.tsx:1-54](), [src/app/promptmasters/loading.tsx:1-39](), [src/app/feed/loading.tsx:1-28]()`

---

## Server Components, API Routes, and Database Layer

### Server Components and Data Fetching

The base architecture uses React Server Components to render UI on the server and fetch data directly. Next.js 16 facilitates streaming, server-only code, and async components with granular caching.

- The Prisma client singleton is instantiated in `src/lib/db.ts`. It configures query logging based on `NODE_ENV`, hooks up to `DATABASE_URL`, and automatically omits heavy fields like prompt vector embeddings (`embedding: true`) by default to keep server responses lightweight `[src/lib/db.ts:1-27]()`.

Sources: `[src/lib/db.ts:1-27]()`

---

## Layout, Providers, and Theming Pipeline

The global UI shell and theming are handled by the root layout defined in `src/app/layout.tsx`. This component is a Server Component responsible for:

- Loading configuration via `getConfig()` including themes, branding, and localization `[src/app/layout.tsx:156]()`.
- Resolving active locale and messages using `next-intl` server utilities `[src/app/layout.tsx:4-155]()`.
- Determining text direction (LTR vs RTL) via `isRtlLocale()` for proper font and layout style adjustment `[src/app/layout.tsx:14-157]()`.
- Injecting global font families optimized for Latin, Arabic, and Mono scripts through Google Fonts integration `[src/app/layout.tsx:18-39]()`.

### Theme Computation

It dynamically computes CSS variables and class names for theming on the HTML root element:

- Radius values map to CSS border-radius sizes (`none`, `sm`, `md`, `lg`) `[src/app/layout.tsx:113-118, 169]()`.
- The primary color hex is converted into OKLCH color space with internal utility `hexToOklch()` for perceptual color manipulation `[src/app/layout.tsx:120-142, 161]()`.
- Foreground color is determined based on primary color lightness for proper contrast `[src/app/layout.tsx:163-166]()`.

```typescript
const themeClasses = `theme-${config.theme.variant} density-${config.theme.density}`;
const primaryOklch = hexToOklch(config.theme.colors.primary);

const themeStyles = {
  "--radius": radiusValues[config.theme.radius],
  "--primary": primaryOklch,
  "--primary-foreground": foreground,
} as React.CSSProperties;
```
[src/app/layout.tsx:160-172]()

### Provider Composition

The layout wraps the entire app in context providers imported from `src/components/providers` (`[src/app/layout.tsx:5, 189]()`). These include providers for localization context, theme context, and branding flags.

### Conditional Rendering

Routes with embed or kids namespaces (`/embed`, `/kids`) bypass the full layout with headers and footers and render children directly for minimal UI (`[src/app/layout.tsx:150-152, 190-192]()`).

Sources: `[src/app/layout.tsx:1-208](), [src/lib/config/index.ts:1-248]()`

---

## Loading States and Suspense Architecture

Next.js 16 enables automatic React Suspense boundaries based on the presence of `loading.tsx` files in route directories. This codebase leverages this feature to provide structured skeleton loading components that closely mimic actual page layouts.

- **Prompt Detail Loading:** In `src/app/prompts/[id]/loading.tsx`, skeletons for breadcrumb navigation, title, tags, tabs, and content blocks prepare the UI during detail fetch `[src/app/prompts/[id]/loading.tsx:1-54]()`.
- **Promptmasters Leaderboard Loading:** Rendered by `src/app/promptmasters/loading.tsx`, displaying skeleton rows that resemble leaderboard entries `[src/app/promptmasters/loading.tsx:1-39]()`.
- **Feed Loading:** Rendered by `src/app/feed/loading.tsx`, providing grid and card skeleton placeholders for personalized feeds `[src/app/feed/loading.tsx:1-28]()`.

Sources: `[src/app/prompts/[id]/loading.tsx:1-54](), [src/app/promptmasters/loading.tsx:1-39](), [src/app/feed/loading.tsx:1-28]()`

---

## Client-Side UI Patterns and Components

While most UI components are server-rendered, specific client-side interactivity or DOM manipulations are delegated to client components with `"use client"` annotations.

### Masonry Layout Component

The masonry layout component defined in `src/components/ui/masonry.tsx` renders a responsive multi-column grid with dynamically calculated absolute positioning (`[src/components/ui/masonry.tsx:1-184]()`).

Key features:
- **Responsive Columns Count:** Adjusts column counts based on window width breakpoints (`default`, `md`, `lg`, `xl`) using resize event listeners `[src/components/ui/masonry.tsx:45-62]()`.
- **Text Direction Support:** Detects right-to-left layout changes at the document level and mirrors computed item X positions `[src/components/ui/masonry.tsx:31-42]()`.
- **Absolute Positioning:** Items are absolutely positioned using calculated `translate3d` transforms based on measured height per column `[src/components/ui/masonry.tsx:65-96]()`.

Sources: `[src/components/ui/masonry.tsx:1-184]()`

---

## Summary Diagram of Application Structure and Key Code Entities

Title: "Full System Entity and Layout Architecture Mapping"
```mermaid
graph TB
    subgraph NaturalLanguageSpace
        NL_Header[""Global Application Header & Branding""]
        NL_Config[""Runtime Configuration & Theme Pipeline""]
        NL_Masonry[""Responsive Masonry Grid Layout""]
    end

    subgraph CodeEntitySpace
        HeaderComponent[""src/components/layout/header.tsx""]
        RootLayout[""src/app/layout.tsx""]
        ConfigLoader[""src/lib/config/index.ts""]
        MasonryComponent[""src/components/ui/masonry.tsx""]
        AnnouncementComp[""src/components/layout/announcement-banner.tsx""]
    end

    NL_Header --> HeaderComponent
    NL_Header --> AnnouncementComp
    NL_Config --> RootLayout
    NL_Config --> ConfigLoader
    NL_Masonry --> MasonryComponent

    RootLayout --> HeaderComponent
    RootLayout --> ConfigLoader
```

Sources: `[src/app/layout.tsx:1-208](), [src/lib/config/index.ts:1-248](), [src/components/layout/header.tsx:1-186](), [src/components/layout/announcement-banner.tsx:1-82](), [src/components/ui/masonry.tsx:1-184]()`

---

## Detailed File Organization per Concern

| Concern           | Location                  | Description                                                  |
|-------------------|---------------------------|--------------------------------------------------------------|
| **App Router Root & Layout** | `src/app/layout.tsx`            | Root React Server Component; theme, locale, global HTML wrapping `[src/app/layout.tsx:144-208]()` |
| **Config Loader & Schema** | `src/lib/config/index.ts`       | Runtime configuration loader and environment variable override parser `[src/lib/config/index.ts:1-248]()` |
| **User Configuration**        | `prompts.config.ts`             | Site-level branding, auth, features, and theme settings `[prompts.config.ts:1-106]()` |
| **Internationalization Config**| `src/lib/i18n/config.ts`       | Supported locales, default locale, and RTL language definitions `[src/lib/i18n/config.ts:1-24]()` |
| **Header Component**          | `src/components/layout/header.tsx` | Client navigation header with locale and session handling `[src/components/layout/header.tsx:1-186]()` |
| **Announcement Banner**       | `src/components/layout/announcement-banner.tsx` | Site-wide announcement bar with dismissal persistence `[src/components/layout/announcement-banner.tsx:1-82]()` |
| **Prompt Detail Loader**      | `src/app/prompts/[id]/loading.tsx` | Suspense loading skeleton for prompt detail views `[src/app/prompts/[id]/loading.tsx:1-54]()` |
| **Promptmasters Loader**      | `src/app/promptmasters/loading.tsx` | Suspense loading skeleton for leaderboards `[src/app/promptmasters/loading.tsx:1-39]()` |
| **Feed Loader**               | `src/app/feed/loading.tsx`      | Suspense loading skeleton for user feeds `[src/app/feed/loading.tsx:1-28]()` |
| **Client-Only Interactive UI**| `src/components/ui/masonry.tsx` | Client component for responsive masonry layouts `[src/components/ui/masonry.tsx:1-184]()` |
| **Database Access**           | `src/lib/db.ts`                 | Prisma client singleton setup for database queries `[src/lib/db.ts:1-27]()` |

Sources: `[src/app/layout.tsx:144-208](), [src/lib/config/index.ts:1-248](), [prompts.config.ts:1-106](), [src/lib/i18n/config.ts:1-24](), [src/components/layout/header.tsx:1-186](), [src/components/layout/announcement-banner.tsx:1-82](), [src/app/prompts/[id]/loading.tsx:1-54](), [src/app/promptmasters/loading.tsx:1-39](), [src/app/feed/loading.tsx:1-28](), [src/components/ui/masonry.tsx:1-184](), [src/lib/db.ts:1-27]()`

---

# Page: Configuration System

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [prompts.config.ts](prompts.config.ts)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



## Purpose and Scope

This document details the configuration subsystem of prompts.chat, covering the static configuration file structure [prompts.config.ts:1-106](), the type-safe `defineConfig` builder function [src/lib/config/index.ts:98-100](), the asynchronous configuration loading pipeline [src/lib/config/index.ts:189-248](), runtime environment variable overrides via `PCHAT_*` prefixes [src/lib/config/index.ts:118-187](), and synchronous/asynchronous runtime access patterns implemented in `src/lib/config/index.ts` [src/lib/config/index.ts:1-248]().

Sources: [src/lib/config/index.ts:1-248](), [prompts.config.ts:1-106]()

---

## Overview

The configuration system provides a centralized mechanism to customize branding, design themes, authentication providers, internationalization, feature flags, and homepage widgets without altering source code. It combines static TypeScript definitions with container-friendly runtime environment overrides.

Sources: [src/lib/config/index.ts:118-187](), [prompts.config.ts:1-106]()

---

## Configuration File Structure

The `prompts.config.ts` file acts as the primary user-editable configuration source [prompts.config.ts:1-106](). It leverages the `defineConfig()` helper function [src/lib/config/index.ts:98-100]() to ensure complete TypeScript autocomplete and compile-time validation.

### System Configuration Map

This diagram bridges natural language configuration domains to their corresponding TypeScript interfaces and fields in code.

```mermaid
graph TB
    subgraph NaturalLanguageSpace["Natural Language Space"]
        BrandingDomain["Visual Identity"]
        ThemeDomain["Design System"]
        AuthDomain["User Access"]
        FeatureDomain["Capability Flags"]
        I18nDomain["Internationalization"]
        HomepageDomain["Homepage Customization"]
        AnnouncementDomain["Site-wide Announcement"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        Config["prompts.config.ts"]
        defineConfig["defineConfig()"]
        
        Config --> defineConfig
        defineConfig --> Branding["branding: BrandingConfig"]
        defineConfig --> Theme["theme: ThemeConfig"]
        defineConfig --> Auth["auth: AuthConfig"]
        defineConfig --> I18n["i18n: I18nConfig"]
        defineConfig --> Features["features: FeaturesConfig"]
        defineConfig --> Homepage["homepage: HomepageConfig"]
        defineConfig --> Announcement["announcement: AnnouncementConfig"]
        
        Branding --> BFields["name, logo, logoDark, favicon, description, appStoreUrl, chromeExtensionUrl"]
        Theme --> TFields["radius, variant, density, colors"]
        Auth --> AFields["providers[], allowRegistration"]
        I18n --> IFields["locales[], defaultLocale"]
        Features --> FFields["privatePrompts, changeRequests, aiSearch, mcp, promptEnhancer"]
        Homepage --> HFields["useCloneBranding, achievements, sponsors"]
        Announcement --> AnnFields["id, message, href, external, cta"]
    end

    BrandingDomain -.-> Branding
    ThemeDomain -.-> Theme
    AuthDomain -.-> Auth
    I18nDomain -.-> I18n
    FeatureDomain -.-> Features
    HomepageDomain -.-> Homepage
    AnnouncementDomain -.-> Announcement
```

**Configuration Sections and Their Purposes**

| Section | Purpose | Key Fields |
|---|---|---|
| `branding` | Organization identity and visual assets | `name`, `logo`, `logoDark`, `favicon`, `description`, `appStoreUrl`, `chromeExtensionUrl` |
| `theme` | Design system appearance | `radius`, `variant`, `density`, `colors.primary` |
| `auth` | Authentication providers | `providers[]`, `allowRegistration` |
| `i18n` | Internationalization settings | `locales[]`, `defaultLocale` |
| `features` | Feature flags for optional capabilities | `privatePrompts`, `changeRequests`, `categories`, `tags`, `aiSearch`, `aiGeneration`, `mcp`, `comments`, `promptEnhancer` |
| `homepage` | Homepage customization | `useCloneBranding`, `achievements.enabled`, `sponsors.enabled`, `sponsors.items[]` |
| `announcement` | Site-wide announcement bar | `id`, `message`, `messageShort`, `href`, `external`, `cta` |

Sources: [src/lib/config/index.ts:1-96](), [prompts.config.ts:1-106]()

---

## Configuration Types & `defineConfig`

The configuration schemas are formally defined in `src/lib/config/index.ts` [src/lib/config/index.ts:1-96](). The `defineConfig` helper function accepts a `PromptsConfig` object and returns it unchanged, enforcing typing [src/lib/config/index.ts:98-100]().

```mermaid
classDiagram
    class PromptsConfig {
        +BrandingConfig branding
        +ThemeConfig theme
        +AuthConfig auth
        +I18nConfig i18n
        +FeaturesConfig features
        +HomepageConfig homepage?
        +AnnouncementConfig announcement?
    }
    
    class BrandingConfig {
        +string name
        +string logo
        +string logoDark?
        +string favicon
        +string description
        +string appStoreUrl?
        +string chromeExtensionUrl?
    }
    
    class ThemeConfig {
        +string radius
        +string variant
        +string density
        +ColorConfig colors
    }

    class ColorConfig {
        +string primary
        +string secondary?
        +string accent?
    }
    
    class AuthConfig {
        +AuthProvider[] providers?
        +boolean allowRegistration
    }

    class I18nConfig {
        +string[] locales
        +string defaultLocale
    }

    class FeaturesConfig {
        +boolean privatePrompts
        +boolean changeRequests
        +boolean categories
        +boolean tags
        +boolean aiSearch?
        +boolean aiGeneration?
        +boolean mcp?
        +boolean comments?
        +boolean promptEnhancer?
    }

    class HomepageConfig {
        +boolean useCloneBranding?
        +HomepageAchievementsConfig achievements?
        +HomepageSponsorsConfig sponsors?
    }

    class AnnouncementConfig {
        +string id
        +string message
        +string messageShort?
        +string href?
        +boolean external?
        +string cta?
    }

    PromptsConfig --> BrandingConfig
    PromptsConfig --> ThemeConfig
    PromptsConfig --> AuthConfig
    PromptsConfig --> I18nConfig
    PromptsConfig --> FeaturesConfig
    PromptsConfig --> HomepageConfig
    PromptsConfig --> AnnouncementConfig
    ThemeConfig --> ColorConfig
```

Sources: [src/lib/config/index.ts:1-100]()

---

## Configuration Loading Pipeline & Environment Overrides

The configuration loading pipeline is executed via `getConfig()` [src/lib/config/index.ts:189-248](). It performs a dynamic import of `@/../prompts.config`, falls back to default values if the file is missing, applies runtime overrides via `applyEnvOverrides()` [src/lib/config/index.ts:118-187](), and caches the resulting configuration object in memory [src/lib/config/index.ts:189-192]().

### Configuration Pipeline Flow

```mermaid
sequenceDiagram
    participant App as "ApplicationRuntime"
    participant getConfig as "getConfig()"
    participant Import as "DynamicImport"
    participant ApplyEnv as "applyEnvOverrides()"
    participant Env as "process.env"
    participant Cache as "cachedConfig"
    
    App->>getConfig: "Request Config"
    getConfig->>Cache: "Check Cache"
    
    alt Cache is Empty
        getConfig->>Import: "Import prompts.config.ts"
        Import-->>getConfig: "baseConfig"
        getConfig->>ApplyEnv: "applyEnvOverrides(baseConfig)"
        ApplyEnv->>Env: "Read PCHAT_* Variables"
        Env-->>ApplyEnv: "Environment Overrides"
        ApplyEnv-->>getConfig: "Final PromptsConfig"
        getConfig->>Cache: "Store cachedConfig"
    end
    
    getConfig-->>App: "Return PromptsConfig"
```

### Runtime Environment Variable Overrides (`PCHAT_*`)

To support containerized and Docker deployments without rebuilding static assets, `applyEnvOverrides` inspects `process.env` for keys prefixed with `PCHAT_` [src/lib/config/index.ts:118-187]().

| Category | Environment Variable Prefix / Keys | Behavior / Parsing Logic |
|---|---|---|
| Branding | `PCHAT_NAME`, `PCHAT_DESCRIPTION`, `PCHAT_LOGO`, `PCHAT_LOGO_DARK`, `PCHAT_FAVICON` | String override; `logoDark` falls back to `PCHAT_LOGO` if unset [src/lib/config/index.ts:135-143]() |
| Theme | `PCHAT_THEME_RADIUS`, `PCHAT_THEME_VARIANT`, `PCHAT_THEME_DENSITY`, `PCHAT_COLOR` | Casts string values to theme enums and primary color hex/oklch [src/lib/config/index.ts:144-153]() |
| Auth | `PCHAT_AUTH_PROVIDERS`, `PCHAT_ALLOW_REGISTRATION` | Parses comma-separated arrays and boolean values (`"true"`, `"1"`) [src/lib/config/index.ts:122-132](), [src/lib/config/index.ts:154-161]() |
| i18n | `PCHAT_LOCALES`, `PCHAT_DEFAULT_LOCALE` | Parses comma-separated locale strings [src/lib/config/index.ts:128-132](), [src/lib/config/index.ts:162-167]() |
| Features | `PCHAT_FEATURE_PRIVATE_PROMPTS`, `PCHAT_FEATURE_CHANGE_REQUESTS`, `PCHAT_FEATURE_CATEGORIES`, `PCHAT_FEATURE_TAGS`, `PCHAT_FEATURE_AI_SEARCH`, `PCHAT_FEATURE_AI_GENERATION`, `PCHAT_FEATURE_MCP`, `PCHAT_FEATURE_COMMENTS`, `PCHAT_FEATURE_PROMPT_ENHANCER` | Parses case-insensitive boolean flags [src/lib/config/index.ts:122-126](), [src/lib/config/index.ts:168-178]() |

Setting `PCHAT_NAME` automatically enables clone branding mode, disabling default public achievements and sponsor lists [src/lib/config/index.ts:179-184]().

Sources: [src/lib/config/index.ts:118-187]()

---

## Runtime Access: `getConfig` and `getConfigSync`

The application exposes two methods to retrieve configuration at runtime depending on execution context:

1.  **Asynchronous `getConfig()`**: 
    -   Dynamically imports and caches configuration on the server [src/lib/config/index.ts:189-248]().
    -   Safe for use in Server Components, API routes, and Server Actions.
2.  **Synchronous `getConfigSync()`**: 
    -   Retrieves the pre-cached configuration object [src/lib/config/index.ts:221-248]().
    -   Throws an error if the configuration has not yet been initialized by an asynchronous `getConfig()` call.

Sources: [src/lib/config/index.ts:189-248]()

---

## Summary Diagram Bridging Natural Language Concepts to Code Entities

```mermaid
flowchart LR
    subgraph NaturalLanguageConcepts["Natural Language Concepts"]
        SystemConfig["System Configuration"]
        EnvOverrides["Environment Overrides"]
        RuntimeAccess["Runtime Config Access"]
    end
    
    subgraph CodeEntities["Code Entities"]
        DefineConfig["defineConfig()"]
        UserConfig["prompts.config.ts"]
        ApplyOverrides["applyEnvOverrides()"]
        LoadConfig["getConfig()"]
        SyncConfig["getConfigSync()"]
        BrandingHook["useBranding()"]
    end

    SystemConfig --> UserConfig
    UserConfig --> DefineConfig
    UserConfig --> LoadConfig
    LoadConfig --> ApplyOverrides
    EnvOverrides --> ApplyOverrides
    ApplyOverrides --> LoadConfig
    LoadConfig --> SyncConfig
    SyncConfig --> RuntimeAccess
    RuntimeAccess --> BrandingHook
```

Sources: [src/lib/config/index.ts:98-248](), [prompts.config.ts:1-106]()

---

# Page: Database Schema

# Database Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [prisma/schema.prisma](prisma/schema.prisma)
- [prisma/seed.ts](prisma/seed.ts)

</details>



## Purpose and Scope

This document details the PostgreSQL database schema used by `prompts.chat`, managed through Prisma ORM [prisma/schema.prisma:1-9](). The schema defines all data models, relationships, enumerations, and indexing strategies supporting the core prompt library, contributor attribution, self-hosting, versioning, workflows, bot platforms, classifiers, change requests, and social features [prisma/schema.prisma:11-150]().

Sources: [prisma/schema.prisma:1-9](), [prisma/schema.prisma:11-150]()

---

## Overview

The database schema is defined in `prisma/schema.prisma` [prisma/schema.prisma:1-9]() and utilizes PostgreSQL with the Prisma Client (`@prisma/client`) [package.json:20](). It organizes models into key functional domains:

- **Core Content & Versioning**: `Prompt`, `PromptVersion`, `PromptConnection`, `Category`, and `Tag` models [prisma/schema.prisma:98-150]().
- **User Management**: `User`, `Account`, `Session`, and `VerificationToken` models [prisma/schema.prisma:11-96]().
- **Collaborative Editing & Change Requests**: `ChangeRequest` model enabling users to propose prompt edits [prisma/schema.prisma:37-37]().
- **Bot and Agent Ecosystem**: Dedicated fields for `BOT` type prompts (`botPlatforms`, `botConfig`, `computerRequirements`, `botPairings`) [prisma/schema.prisma:140-150]().
- **Decision Classifiers**: Models supporting decision trees, criteria, and prompt routing catalogs.
- **Social Interactions**: Voting, collections, comments, and pins supported through models like `PromptVote`, `Collection`, `PinnedPrompt`, and `Comment` [prisma/schema.prisma:41-49]().

All database interactions within the application use the Prisma `db` client instance imported from `src/lib/db` [src/app/prompts/[id]/page.tsx:10-10](), [src/app/api/prompts/route.ts:4-4]().

Sources: [prisma/schema.prisma:1-9](), [src/app/prompts/[id]/page.tsx:10-10](), [src/app/api/prompts/route.ts:4-4]()

---

## High-Level Entity Relationships

### Core Schema Architecture and Relations

Title: "Database Entity Relationship Diagram"

```mermaid
erDiagram
    User ||--o{ Prompt : "authors"
    User }o--o{ Prompt : "contributors"
    User ||--o{ PromptVersion : "creates"
    User ||--o{ ChangeRequest : "submits"
    Prompt ||--o{ PromptVersion : "has_versions"
    Prompt ||--o{ ChangeRequest : "receives"
    Prompt }o--|| Category : "belongs_to"
    Prompt }o--o{ PromptTag : "tagged_with"
    Prompt ||--o{ PromptConnection : "sources"
    Prompt ||--o{ PromptConnection : "targets"
    Category ||--o{ Category : "parent_child"
```

This diagram illustrates essential data relationships including:
- `User` as both prompt author and contributor (many-to-many via `contributors`) [prisma/schema.prisma:42-44]().
- Prompts categorized (`Category`) and tagged (`Tag`) for organization [prisma/schema.prisma:132-133]().
- `PromptConnection` manages directional links for workflows or related prompts [prisma/schema.prisma:134-135]().

Sources: [prisma/schema.prisma:11-150]()

---

## Core Models

### Prompt Model

The `Prompt` model is the foundational content entity representing AI prompts with support for multiple output types, metadata, versioning, contributor attribution, and workflow linking [prisma/schema.prisma:98-150]().

| Field                  | Type             | Description                                                                    |
|------------------------|------------------|--------------------------------------------------------------------------------|
| `id`                   | `String`         | Primary key (CUID), autogenerated [prisma/schema.prisma:99]()                  |
| `title`                | `String`         | Prompt title [prisma/schema.prisma:100]()                                       |
| `slug`                 | `String?`        | URL-safe slug generated from the title, indexed for quick search [prisma/schema.prisma:101]() |
| `description`          | `String?`        | Optional brief summary [prisma/schema.prisma:102]()                             |
| `content`              | `String`         | Full prompt text or instructions [prisma/schema.prisma:103]()                   |
| `type`                 | `PromptType`     | Enum for prompt output type: `TEXT`, `IMAGE`, `VIDEO`, `AUDIO`, `SKILL`, `TASTE`, `BOT`, `STRUCTURED` [prisma/schema.prisma:104]() |
| `isPrivate`            | `Boolean`        | Visibility flag restricting prompt access [prisma/schema.prisma:105]()        |
| `mediaUrl`             | `String?`        | URL to associated media (image/video/audio) [prisma/schema.prisma:106]()       |
| `viewCount`            | `Int`            | Number of views, defaults to 0 [prisma/schema.prisma:107]()                    |
| `embedding`            | `Json?`          | OpenAI vector embedding used for semantic search [prisma/schema.prisma:108]() |
| `requiresMediaUpload`  | `Boolean`        | Whether prompt requires media upload [prisma/schema.prisma:111]()              |
| `requiredMediaType`    | `RequiredMediaType?` | Enum: `"IMAGE"`, `"VIDEO"`, `"DOCUMENT"` [prisma/schema.prisma:110]()       |
| `requiredMediaCount`   | `Int?`           | Number of required media uploads, 1–10 [prisma/schema.prisma:109]()            |
| `structuredFormat`     | `StructuredFormat?` | Enum of input format, `JSON` or `YAML` [prisma/schema.prisma:112]()          |
| `featuredAt`           | `DateTime?`      | Timestamp when featured, null if not featured [prisma/schema.prisma:113]()     |
| `isFeatured`           | `Boolean`        | Featured flag [prisma/schema.prisma:114]()                                    |
| `isUnlisted`           | `Boolean`        | Unlisted flag [prisma/schema.prisma:116]()                                    |
| `unlistedAt`           | `DateTime?`      | Unlisted timestamp [prisma/schema.prisma:117]()                               |
| `delistReason`         | `DelistReason?`  | Reason code for prompt delisting [prisma/schema.prisma:118]()                  |
| `deletedAt`            | `DateTime?`      | Soft-delete timestamp [prisma/schema.prisma:119]()                            |
| `bestWithModels`       | `String[]`       | List of AI model slugs this prompt works best with, max 3 [prisma/schema.prisma:141]() |
| `bestWithMCP`          | `Json?`          | MCP configurations array [prisma/schema.prisma:142]()                          |
| `workflowLink`         | `String?`        | URL pointing to a demo/test of prompt workflow [prisma/schema.prisma:143]()    |
| `botPlatforms`         | `BotPlatform[]`  | BOT prompts only: agent platforms the bot supports [prisma/schema.prisma:145]() |
| `computerRequirements` | `BotComputerRequirement[]` | BOT prompts only: CLOUD and/or LOCAL, empty when the bot needs no computer [prisma/schema.prisma:149]() |
| `botConfig`            | `Json?`          | BOT prompts only: routines, skills, connectors [prisma/schema.prisma:150]()     |

Sources: [prisma/schema.prisma:98-150](), [src/app/api/prompts/route.ts:10-33]()

---

### User Model

Stores user profiles, authentication data, roles, subscription, and usage metadata [prisma/schema.prisma:11-58]().

| Field                      | Type               | Description                                                              |
|----------------------------|--------------------|--------------------------------------------------------------------------|
| `id`                       | `String`           | Primary key CUID [prisma/schema.prisma:12]()                            |
| `email`                    | `String`           | Unique email address [prisma/schema.prisma:13]()                        |
| `username`                 | `String`           | Unique handle used for routing profiles [prisma/schema.prisma:14]()      |
| `name`                     | `String?`          | Optional display name [prisma/schema.prisma:15]()                       |
| `password`                 | `String?`          | Hashed password (nullable for OAuth-only accounts) [prisma/schema.prisma:16]() |
| `avatar`                   | `String?`          | URL for user avatar image [prisma/schema.prisma:17]()                   |
| `bio`                      | `String?`          | User bio text limited to 250 chars [prisma/schema.prisma:18]()          |
| `customLinks`              | `Json?`            | Custom links array for profiles [prisma/schema.prisma:19]()             |
| `role`                     | `UserRole`         | Role enum: `USER` or `ADMIN` [prisma/schema.prisma:20]()                 |
| `locale`                   | `String`           | Preferred locale code, defaults to `"en"` [prisma/schema.prisma:21]()    |
| `verified`                 | `Boolean`          | Verified user flag [prisma/schema.prisma:25]()                           |
| `apiKey`                   | `String?`          | Unique API key for external services [prisma/schema.prisma:27]()         |
| `flagged`                  | `Boolean`          | Flag indicating user is restricted or monitored [prisma/schema.prisma:29]() |
| `dailyGenerationLimit`     | `Int`              | Number of allowed daily AI generations, default 3 [prisma/schema.prisma:32]() |
| `generationCreditsRemaining` | `Int`            | Remaining AI generation credits [prisma/schema.prisma:33]()              |

Sources: [prisma/schema.prisma:11-58]()

---

### Category, Tag, and PromptConnection Models

- **Category**: Supports hierarchical structures via self-referencing relationships and supports pinned states for quick-access filters [prisma/schema.prisma:132-133]().
- **Tag**: Represents descriptive keywords attached to prompts through the `PromptTag` junction table [prisma/schema.prisma:129-129]().
- **PromptConnection**: Handles directed relationships between prompts (`sourceId` and `targetId`), used for workflow chains and related prompt mappings [prisma/schema.prisma:134-135]().

Sources: [prisma/schema.prisma:129-135]()

---

## Natural Language to Code Entity Mapping

### Diagram 1: Prompt Creation Flow in Code

Title: "Prompt Creation Flow Mapping"

```mermaid
graph TD
    NLUser["UserCreatesPromptViaUI"] -->|"POST /api/prompts"| ApiPostHandler["src/app/api/prompts/route.ts:POST"]
    ApiPostHandler -->|"Calls createPrompt"| CreatePromptLib["src/lib/prompt-write.ts:createPrompt"]
    CreatePromptLib -->|"Persists"| DBCreatePrompt["db.prompt.create"]
    DBCreatePrompt -->|"WritesTo"| PrismaPromptModel["Prompt model in prisma/schema.prisma"]
```

This flow shows data input from the user through the API route, invocation of write helpers, and database persistence via Prisma.

Sources: [src/app/api/prompts/route.ts:10-33](), [prisma/schema.prisma:98-150]()

---

### Diagram 2: Prompt Detail and Version Retrieval

Title: "Prompt Retrieval Mapping"

```mermaid
graph TD
    NLUser["UserViewsPromptPage"] -->|"Next.js dynamic route"| PromptPageComponent["src/app/prompts/[id]/page.tsx"]
    PromptPageComponent -->|"Queries relations"| DBFindPrompt["db.prompt.findFirst"]
    DBFindPrompt -->|"Retrieves versions"| VersionRecords["PromptVersion model"]
    PromptPageComponent -->|"Renders UI"| PromptUI["InteractivePromptContent and SkillViewer"]
```

This shows the retrieval of prompt data including related versions and contributors for presentation.

Sources: [src/app/prompts/[id]/page.tsx:153-164](), [prisma/schema.prisma:98-150]()

---

## Migrations History and Management

Database schema changes are managed through Prisma Migrate:

- Migration files reside in `prisma/migrations`.
- Development migrations run via `npm run db:migrate` which executes `prisma migrate dev` [package.json:12]().
- Production deployments use `npm run db:deploy` which runs `prisma migrate deploy` [package.json:8]().
- Seeding with sample data is handled by `prisma/seed.ts` [prisma/seed.ts:1-220]() invoked via `npm run db:seed` [package.json:15]().

Prisma client code generation is triggered by `prisma generate` and automated post-install via script hooks [package.json:7]().

Sources: [package.json:5-31](), [prisma/schema.prisma:1-9](), [prisma/seed.ts:1-220]()

---

# Page: Plugin Architecture

# Plugin Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/__tests__/components/spacefast-widget.test.tsx](src/__tests__/components/spacefast-widget.test.tsx)
- [src/app/api/leaderboard/route.ts](src/app/api/leaderboard/route.ts)
- [src/app/api/media-generate/status/route.ts](src/app/api/media-generate/status/route.ts)
- [src/components/prompts/audio-player.tsx](src/components/prompts/audio-player.tsx)
- [src/components/prompts/infinite-prompt-list.tsx](src/components/prompts/infinite-prompt-list.tsx)
- [src/components/prompts/prompt-list.tsx](src/components/prompts/prompt-list.tsx)
- [src/components/prompts/widget-card.tsx](src/components/prompts/widget-card.tsx)
- [src/components/widgets/spacefast-widget-card.tsx](src/components/widgets/spacefast-widget-card.tsx)
- [src/lib/plugins/media-generators/fal.ts](src/lib/plugins/media-generators/fal.ts)
- [src/lib/plugins/media-generators/types.ts](src/lib/plugins/media-generators/types.ts)
- [src/lib/plugins/media-generators/wiro.ts](src/lib/plugins/media-generators/wiro.ts)
- [src/lib/plugins/widgets/book.tsx](src/lib/plugins/widgets/book.tsx)
- [src/lib/plugins/widgets/coderabbit.ts](src/lib/plugins/widgets/coderabbit.ts)
- [src/lib/plugins/widgets/index.ts](src/lib/plugins/widgets/index.ts)
- [src/lib/plugins/widgets/spacefast-links.ts](src/lib/plugins/widgets/spacefast-links.ts)
- [src/lib/plugins/widgets/spacefast.tsx](src/lib/plugins/widgets/spacefast.tsx)
- [src/lib/plugins/widgets/textream.tsx](src/lib/plugins/widgets/textream.tsx)
- [src/lib/plugins/widgets/types.ts](src/lib/plugins/widgets/types.ts)

</details>



This page documents the extensible subsystem located in `src/lib/plugins`, which provides modular abstractions for authentication providers, file storage backends, AI media generation providers (`fal` and `wiro`), and the homepage widgets registry (`coderabbit`, `book`, `textream`, `commandcode`, `spacefast`).

---

## 1. Authentication Plugins

The authentication plugin subsystem allows dynamic registration and resolution of auth providers based on configuration files like `prompts.config.ts`. 

- **Built-in Registration:** The function `registerBuiltInAuthPlugins()` registers all supported authentication providers, including `credentialsPlugin`, `googlePlugin`, `azurePlugin`, `githubPlugin`, `applePlugin`, `oidcPlugin`, and `oauthPlugin` [src/lib/plugins/auth/index.ts:11-19]().
- **Configuration Loading:** The helper `getConfiguredAuthPlugins()` initializes the plugin system and maps the configured provider IDs to their respective plugins, falling back to credentials if none are specified [src/lib/plugins/index.ts:37-54]().
- **UI Integration:** The `AuthContent` component renders enabled OAuth buttons using provider metadata and displays fallback hints such as GitHub attribution when appropriate [src/components/auth/auth-content.tsx:24-49]().

Sources: `src/lib/plugins/auth/index.ts`, `src/lib/plugins/index.ts`, `src/components/auth/auth-content.tsx`

---

## 2. Storage Backends & File Management

The storage subsystem provides a unified interface for file uploads and deletions, enabling support for multiple backend providers such as AWS S3 and DigitalOcean Spaces.

### Amazon S3 Storage Plugin

Located at `src/lib/plugins/storage/s3.ts`, this plugin integrates with AWS S3 and S3-compatible services using the official AWS SDK.

- **Dynamic SDK Import:** The AWS SDK client (`@aws-sdk/client-s3`) is dynamically imported in the `getS3Client()` helper to prevent bundling it when unused.
- **Configuration Check:** The `isConfigured()` method returns `true` only if all required environment variables (`S3_BUCKET`, `S3_REGION`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`) are set.
- **Uploading Files:** The `upload()` method accepts either JavaScript `File` or `Buffer` objects, normalizes to a `Buffer`, determines content type (MIME), and generates a unique storage key based on a timestamp and random string. It uses the S3 client's `PutObjectCommand` to perform the upload. Support for S3-compatible endpoints like DigitalOcean Spaces is handled through `S3_ENDPOINT` and path-style requests.
- **Deleting Files:** The `delete()` method can accept either a key or complete URL, extracting the correct key from URLs that include the bucket prefix, then issuing the S3 `DeleteObjectCommand`.

The DigitalOcean Spaces plugin follows a similar interface and is implemented in `src/lib/plugins/storage/do-spaces.ts`, also supporting S3-compatible calls.

Sources: `src/lib/plugins/storage/s3.ts`

---

## 3. Media Generator Plugins

These plugins encapsulate AI-driven media generation services, providing standardized APIs for image, video, and audio generation. The system supports multiple providers with configurable environment variables.

### Fal.ai Media Generator Plugin

Located in `src/lib/plugins/media-generators/fal.ts`, the Fal.ai plugin uses Fal.ai's queue-based API to submit generation requests, then polls for status updates and final results.

- **Environment Variables:** Requires `FAL_API_KEY`, and comma-separated lists for `FAL_IMAGE_MODELS`, `FAL_VIDEO_MODELS`, and `FAL_AUDIO_MODELS` to define allowed generation models [src/lib/plugins/media-generators/fal.ts:7-12]().
- **Queue Submission:** The `submitToFalQueue()` function sends authenticated POST requests with generation input to Fal's queue endpoint [src/lib/plugins/media-generators/fal.ts:106-130]().
- **Status Checks:** `getFalRequestStatus()` polls the status URL to read queue position and generation status. All fetched URLs are validated against trusted Fal.ai origins using `assertFalOrigin()` to prevent SSRF attacks [src/lib/plugins/media-generators/fal.ts:38-48]().
- **Result Retrieval:** Once generation completes, `getFalRequestResult()` fetches the generated media URLs [src/lib/plugins/media-generators/fal.ts:159-182]().
- **WebSocket Handling:** Since Fal.ai uses polling rather than WebSocket for status updates, `falWebSocketHandler` is implemented as a no-op for WebSocket messages [src/lib/plugins/media-generators/fal.ts:201-215]().

### Wiro.ai Media Generator Plugin

The Wiro plugin, found in `src/lib/plugins/media-generators/wiro.ts`, utilizes Wiro's REST API for starting jobs and WebSocket connections to receive real-time progress updates.

- **Configuration:** The plugin requires `WIRO_API_KEY` and related model environment variables to enable generation [src/lib/plugins/media-generators/wiro.ts:6-11]().
- **Start Generation:** `startGeneration()` forms a multipart/form-data request including prompt, resolution, video/audio parameters, and optional image input URLs, then posts to Wiro's `/Run/{model}` endpoint [src/lib/plugins/media-generators/wiro.ts:153-218]().
- **Real-time Updates:** The `wiroWebSocketHandler` processes incoming WebSocket messages that report task phases (queued, preprocess, GPU assigned, started, generating, completed, error). It updates progress and status messages accordingly [src/lib/plugins/media-generators/wiro.ts:56-127]().

Sources: `src/lib/plugins/media-generators/fal.ts`, `src/lib/plugins/media-generators/wiro.ts`

---

## 4. Homepage Widgets Registry & Injection Engine

The homepage and prompt listing UI can be enhanced by injecting promotional or sponsored widgets into the prompt feed. This system is managed via centrally registered widget plugins.

### Widget Plugin Registry

The main registry is defined in `src/lib/plugins/widgets/index.ts`. It exports:

- `getWidgetPlugins()` — returns all registered widget plugins [src/lib/plugins/widgets/index.ts:29-31]().
- `getWidgetPrompts()` — aggregates all individual widget prompts from all plugins [src/lib/plugins/widgets/index.ts:36-38]().
- `getWidgetPlugin(id)` and `getWidgetPrompt(pluginId, promptId)` — allow fetching by identifiers [src/lib/plugins/widgets/index.ts:43-53]().

Currently registered widget plugins include:
- `coderabbitWidget` [src/lib/plugins/widgets/coderabbit.ts:3-96]()
- `bookWidget` [src/lib/plugins/widgets/book.tsx:142-173]()
- `textreamWidget` [src/lib/plugins/widgets/textream.tsx:101-152]()
- `commandcodeWidget` [src/lib/plugins/widgets/index.ts:12]()
- `spacefastWidget` [src/lib/plugins/widgets/spacefast.tsx:7-50]()

### Widget Prompt Types & Positioning

Types and interfaces are declared in `src/lib/plugins/widgets/types.ts`:
- `WidgetPrompt` interface describing individual widgets [src/lib/plugins/widgets/types.ts:54-83]().
- `WidgetPositionConfig` defines positioning modes (`"once"` or `"repeat"`) [src/lib/plugins/widgets/types.ts:42-52]().
- `shouldInject(context)` function determining injection eligibility [src/lib/plugins/widgets/types.ts:78]().
- `render(instanceIndex, placement)` ReactNode function for custom rendering [src/lib/plugins/widgets/types.ts:81-82]().
- `WidgetPlacement` defines surfaces where widgets can be injected, such as `"prompts"`, `"bots"`, or `"teams"` [src/lib/plugins/widgets/types.ts:8]().

### Injection Algorithm

The `injectWidgets()` function in `src/lib/plugins/widgets/index.ts` processes prompt lists:
1. Retrieves all widget prompts for the given `placement` using `getWidgetPromptsForPlacement()` [src/lib/plugins/widgets/index.ts:126-127]().
2. Filters them via `shouldInject` against context parameters [src/lib/plugins/widgets/index.ts:140-146]().
3. Computes insertion offsets via `getWidgetInsertionPositions()` [src/lib/plugins/widgets/index.ts:72-103]().
4. Splices widgets into the array marked with `isWidget: true` [src/lib/plugins/widgets/index.ts:168-177]().

The feed UI component `InfinitePromptList` uses `injectWidgets()` after mount to safely render injected widgets [src/components/prompts/infinite-prompt-list.tsx:13,197]().

Sources: `src/lib/plugins/widgets/index.ts`, `src/lib/plugins/widgets/types.ts`, `src/lib/plugins/widgets/coderabbit.ts`, `src/lib/plugins/widgets/book.tsx`, `src/lib/plugins/widgets/textream.tsx`, `src/lib/plugins/widgets/spacefast.tsx`, `src/components/prompts/infinite-prompt-list.tsx`

---

## 5. Architecture Mapping: Natural Language to Code Entity Space

### Diagram Title: "Auth, Storage, and Media Generator Plugins Architecture"

```mermaid
graph TD
    sub1["Authentication Registry"] --> registerBuiltInAuthPlugins["registerBuiltInAuthPlugins()"]
    registerBuiltInAuthPlugins --> getConfiguredAuthPlugins["getConfiguredAuthPlugins()"]
    getConfiguredAuthPlugins --> AuthContent["AuthContent Component"]

    sub2["Storage Backend"] --> s3StoragePlugin["s3StoragePlugin"]
    s3StoragePlugin --> getS3Client["getS3Client()"]
    getS3Client --> PutObjectCommand["PutObjectCommand / DeleteObjectCommand"]

    sub3["Media Generator Provider"] --> falGeneratorPlugin["falGeneratorPlugin"]
    sub3 --> wiroGeneratorPlugin["wiroGeneratorPlugin"]

    falGeneratorPlugin --> submitToFalQueue["submitToFalQueue()"]
    falGeneratorPlugin --> getFalRequestStatus["getFalRequestStatus()"]
    falGeneratorPlugin --> getFalRequestResult["getFalRequestResult()"]
    falGeneratorPlugin --> assertFalOrigin["assertFalOrigin()"]

    wiroGeneratorPlugin --> startGeneration["startGeneration()"]
    wiroGeneratorPlugin --> wiroWebSocketHandler["wiroWebSocketHandler"]
```

Sources: `src/lib/plugins/auth/index.ts`, `src/lib/plugins/index.ts`, `src/components/auth/auth-content.tsx`, `src/lib/plugins/storage/s3.ts`, `src/lib/plugins/media-generators/fal.ts`, `src/lib/plugins/media-generators/wiro.ts`

### Diagram Title: "Widgets Registry and Injection Pipeline"

```mermaid
graph TD
    widgetPlugins["getWidgetPlugins()"] --> getWidgetPrompts["getWidgetPrompts()"]
    getWidgetPrompts --> injectWidgets["injectWidgets()"]
    injectWidgets --> getWidgetInsertionPositions["getWidgetInsertionPositions()"]
    injectWidgets --> getWidgetPromptsForPlacement["getWidgetPromptsForPlacement()"]
    getWidgetPromptsForPlacement --> InfinitePromptList["InfinitePromptList Component"]
    InfinitePromptList --> WidgetCard["WidgetCard Component"]
```

Sources: `src/lib/plugins/widgets/index.ts`, `src/components/prompts/infinite-prompt-list.tsx`

---

# Page: Prompt System

# Prompt System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/[username]/page.tsx](src/app/[username]/page.tsx)
- [src/app/api/prompts/[id]/route.ts](src/app/api/prompts/[id]/route.ts)
- [src/app/api/prompts/route.ts](src/app/api/prompts/route.ts)
- [src/app/categories/[slug]/page.tsx](src/app/categories/[slug]/page.tsx)
- [src/app/collection/page.tsx](src/app/collection/page.tsx)
- [src/app/feed/page.tsx](src/app/feed/page.tsx)
- [src/app/prompts/[id]/page.tsx](src/app/prompts/[id]/page.tsx)
- [src/app/skills/page.tsx](src/app/skills/page.tsx)
- [src/app/tags/[slug]/page.tsx](src/app/tags/[slug]/page.tsx)
- [src/components/prompts/discovery-prompts.tsx](src/components/prompts/discovery-prompts.tsx)

</details>



The Prompt System is the core content management layer of prompts.chat. It handles the entire lifecycle of an AI prompt, including creation, storage, versioning, discovery, execution, export, media generation, and bot configurations. This page provides a high-level overview of the system's structure, core data models, prompt types, and workflows. Each major sub-topic has a dedicated child page for in-depth technical details.

For related areas such as user authentication and content discovery, see the corresponding parent pages [User System](#5) and [Content Discovery](#6).

| Child Page | Description |
|---|---|
| [Prompt CRUD Operations](#4.1) | Document prompt creation, editing, deletion with API endpoints, validation schemas, rate limiting, duplicate detection, quality checking, and uploads |
| [Skills & Multi-file Prompts](#4.2) | Explain Agent Skills with SKILL.md requirement, parseSkillFiles/serializeSkillFiles functions, skill viewer/editor/diff UI, taste.md files, and MCP skill tools |
| [Prompt Discovery & Browsing](#4.3) | Document browsing pages (/prompts, /skills, /workflows, /taste), filtering by category/tag/type, search, and pagination with infinite scroll |
| [Prompt Execution & Run Buttons](#4.4) | Explain RunPromptButton component, platform URL construction, variable filling system, and deep link support for IDEs |
| [Versioning & Change Requests](#4.5) | Document PromptVersion records, change request workflow, approval/rejection flow, and version comparison UI |
| [AI-Powered Features](#4.6) | Explain OpenAI integration for embeddings, semantic search, related prompts discovery, quality checking, translation, SQL generation, and prompt improvement via .prompt.yml files |
| [Workflow Chains & Connected Prompts](#4.7) | Document PromptConnection model, workflowLink field, BFS algorithm for workflow propagation, and flow vs related connections |
| [Import & Export System](#4.8) | Explain CSV/JSON import-export routes, GitHub sync via generate-contributors.sh, HuggingFace dataset integration, and admin bulk operations |
| [Media Generation & Attachments](#4.9) | Document media prompt types, MediaGenerator component, /api/media-generate, fal/wiro provider plugins, generation credits and cron reset, and storage backends |
| [Bots, Teams & Connectors](#4.10) | Document the BOT prompt type: bot schema (instructions, routines, connectors, computer requirement), bot pages/cards/forms, install bundles, bot teams and handoffs, MCP bot/team tools, and bot admin management |
| [Decision Classifiers & Chains](#4.11) | Document the CLASSIFIER prompt type: src/lib/classifiers (schema, store, write, categories, change snapshots), Jev/Kev decision models, question types (choice/score/noul), terminal kinds, /classifiers pages and chains builder, prisma/classifiers fixtures, and admin management |

Sources: [src/app/prompts/[id]/page.tsx:37-224](), [src/app/api/prompts/route.ts:1-207](), [prisma/schema.prisma:93-157]()

---

## Core Data Model

At the foundation of the Prompt System is the `Prompt` Prisma model, which represents each prompt entity with extensive metadata and relations to versions, tags, votes, authors, contributors, change requests, bot configurations, and connected workflows [prisma/schema.prisma:93-147]().

### Database Schema Overview

Title: "PromptSystemER"
```mermaid
erDiagram
    "Prompt" ||--o{ "PromptVersion" : "has_versions"
    "Prompt" ||--o{ "PromptTag" : "has_tags"
    "Prompt" ||--o{ "PromptVote" : "has_votes"
    "Prompt" ||--o{ "ChangeRequest" : "has_change_requests"
    "Prompt" ||--o{ "PromptConnection" : "has_outgoing_connections"
    "Prompt" ||--o{ "PromptConnection" : "has_incoming_connections"
    "Prompt" }o--|| "User" : "authored_by"
    "Prompt" }o--o{ "User" : "contributors"
    "Prompt" }o--o| "Category" : "belongs_to"
    
    "Prompt" {
        string id PK
        string title
        string slug
        string content
        enum type
        boolean isPrivate
        boolean isUnlisted
        datetime deletedAt
        json embedding
        string workflowLink
        string authorId FK
        string categoryId FK
        string[] bestWithModels
        json bestWithMCP
        json botConfig
    }
    
    "PromptVersion" {
        string id PK
        int version
        string content
        string promptId FK
        string createdBy FK
    }
    
    "PromptConnection" {
        string id PK
        string sourceId FK
        string targetId FK
        string label
        int order
    }
```

This model structure supports complex relationships including contributing users, bot properties, and managed connections for workflows or related prompt links [prisma/schema.prisma:93-147](). For details, see [Prompt CRUD Operations](#4.1).

Sources: [prisma/schema.prisma:93-157]()

---

## Prompt Types & Metadata

Prompts support various output types and specialized formats, validated via API routes and Prisma models [src/app/api/prompts/route.ts:10-33](), [src/app/api/prompts/[id]/route.ts:10-130]().

| Type | Description | Typical Use Case |
|---|---|---|
| `TEXT` | Standard text prompt | Chat LLMs like ChatGPT, Claude |
| `IMAGE` | Image generation prompt | DALL-E, Midjourney |
| `VIDEO` | Video generation prompt | Sora, Kling, Veo |
| `AUDIO` | Audio/speech generation | ElevenLabs, Suno audio models |
| `SKILL` | Multi-file agent prompt | Agent skills with MCP protocol |
| `TASTE` | Style/preference prompt | Personalization use cases |
| `BOT` | Agent bot configuration | OpenClaw, AutoGPT, Dots, Duet, Muse |
| `CLASSIFIER` | Decision model | Jev/Kev decision models, question chains |

Additional metadata fields specify media upload requirements, agent bot properties, and optimized model configurations:
- `requiresMediaUpload`: Flags prompts needing media input (image, video, document).
- `requiredMediaType`: Enum specifying exact media type required [prisma/schema.prisma:110]().
- `requiredMediaCount`: Number of media files required [prisma/schema.prisma:109]().
- `bestWithModels`: Array of up to three model identifiers optimized for this prompt [prisma/schema.prisma:137]().
- `bestWithMCP`: JSON configurations defining MCP toolchains tailored to this prompt [prisma/schema.prisma:138]().
- `workflowLink`: Optional URL to test or demo prompt workflows linking multiple prompts [prisma/schema.prisma:139]().
- `botPlatforms`, `botConfig`, `computerRequirement`: Specialized properties for `BOT` prompt types [prisma/schema.prisma:141-146]().

For details on multi-file agent skills, see [Skills & Multi-file Prompts](#4.2). For bot definitions, see [Bots, Teams & Connectors](#4.10). For classifier definitions, see [Decision Classifiers & Chains](#4.11).

Sources: [prisma/schema.prisma:93-147](), [src/app/api/prompts/route.ts:10-33](), [src/app/api/prompts/[id]/route.ts:10-130]()

---

## Natural Language Space to Code Entity Space: CRUD & Lifecycle

This diagram bridges user-facing prompt editing pages to underlying API route controllers and Prisma database models.

Title: "PromptCrudArchitecture"
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        PromptEditPage["Prompt Edit Page"]
        PromptDetailPage["Prompt Detail Page"]
    end

    subgraph "CodeEntitySpace"
        PromptForm["PromptForm Component"]
        PostAPI["POST /api/prompts"]
        PatchAPI["PATCH /api/prompts/[id]"]
        DeleteAPI["DELETE /api/prompts/[id]"]
        PromptModel["db.prompt (Prisma Model)"]
        CreatePromptFn["createPrompt (src/lib/prompt-write.ts)"]
        UpdatePromptFn["updatePrompt (src/lib/prompt-write.ts)"]
    end

    PromptEditPage --> PromptForm
    PromptForm -- "New Prompt" --> PostAPI
    PromptForm -- "Update Prompt" --> PatchAPI
    PromptDetailPage -- "Delete Prompt" --> DeleteAPI
    PostAPI --> CreatePromptFn
    PatchAPI --> UpdatePromptFn
    CreatePromptFn --> PromptModel
    UpdatePromptFn --> PromptModel
    DeleteAPI --> PromptModel
```

Sources: [src/app/prompts/[id]/page.tsx:1-164](), [src/app/api/prompts/route.ts:10-33](), [src/app/api/prompts/[id]/route.ts:102-130](), [src/app/api/prompts/[id]/route.ts:135-219](), [prisma/schema.prisma:93-157]()

---

## Natural Language Space to Code Entity Space: Discovery & Browsing

This diagram maps browsing interfaces (prompts index, category pages, tag pages, user profiles, feed, collections, skills) to their server components and cached database fetching logic.

Title: "PromptDiscoveryArchitecture"
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        PromptsIndex["/prompts (Prompts Index)"]
        CategoryPage["/categories/[slug] (Category Page)"]
        TagPage["/tags/[slug] (Tag Page)"]
        UserProfilePage["/@username (User Profile)"]
        FeedPage["/feed (User Feed)"]
        CollectionPage["/collection (User Collection)"]
        SkillsPage["/skills (Skills Listing)"]
    end

    subgraph "CodeEntitySpace"
        PromptsAPI["GET /api/prompts"]
        CategoryPageComp["src/app/categories/[slug]/page.tsx"]
        TagPageComp["src/app/tags/[slug]/page.tsx"]
        UserProfilePageComp["src/app/[username]/page.tsx"]
        FeedPageComp["src/app/feed/page.tsx"]
        CollectionPageComp["src/app/collection/page.tsx"]
        SkillsPageComp["src/app/skills/page.tsx"]
        PrismaPromptFindMany["db.prompt.findMany (Prisma Query)"]
    end

    PromptsIndex --> PromptsAPI
    CategoryPage --> CategoryPageComp
    TagPage --> TagPageComp
    UserProfilePage --> UserProfilePageComp
    FeedPage --> FeedPageComp
    CollectionPage --> CollectionPageComp
    SkillsPage --> SkillsPageComp

    PromptsAPI --> PrismaPromptFindMany
    CategoryPageComp --> PrismaPromptFindMany
    TagPageComp --> PrismaPromptFindMany
    UserProfilePageComp --> PrismaPromptFindMany
    FeedPageComp --> PrismaPromptFindMany
    CollectionPageComp --> PrismaPromptFindMany
    SkillsPageComp --> PrismaPromptFindMany
```

Sources: [src/app/api/prompts/route.ts:56-207](), [src/app/categories/[slug]/page.tsx:139-175](), [src/app/tags/[slug]/page.tsx:80-117](), [src/app/[username]/page.tsx:158-170](), [src/app/feed/page.tsx:45-87](), [src/app/collection/page.tsx:25-60](), [src/app/skills/page.tsx:42-87](), [prisma/schema.prisma:93-157]()

---

## Prompt Lifecycle & Execution

The prompt lifecycle spans creation, validation, AI enrichment, discovery, versioning, and execution. During creation, the system enforces authorization, input validation, duplicate/similarity detection, and rate limiting [src/app/api/prompts/route.ts:10-33]().

Prompts support dynamic variables using variable syntax. The `InteractivePromptContent` component renders prompts with editable spans for in-place variable editing [src/app/prompts/[id]/page.tsx:17](). Additionally, the `RunPromptButton` component constructs platform-specific URLs injecting the resolved prompt text.

For details, see [Prompt Execution & Run Buttons](#4.4) and [Versioning & Change Requests](#4.5).

Sources: [src/app/prompts/[id]/page.tsx:17](), [src/app/api/prompts/route.ts:10-33]()

---

## Quality Control & Moderation

The Prompt System incorporates automated and manual quality controls:
- **Automated Quality Checking**: Analyzes content for instruction quality and depth.
- **Duplicate Detection**: Compares new submissions against recent public prompts.
- **Rate Limiting & Flags**: Enforces cooldowns and daily generation/creation limits for flagged accounts [prisma/schema.prisma:29-34]().
- **Soft Deletion**: Prompts are soft-deleted by setting a `deletedAt` timestamp, making them invisible to public users but recoverable by admins [src/app/api/prompts/[id]/route.ts:203-206](). Owners can delete their own prompts only if they have been delisted for quality issues [src/app/api/prompts/[id]/route.ts:181-193]().

For details, see [Prompt CRUD Operations](#4.1).

Sources: [prisma/schema.prisma:29-34](), [src/app/api/prompts/route.ts:10-33](), [src/app/api/prompts/[id]/route.ts:135-219]()

---

# Page: Prompt CRUD Operations

# Prompt CRUD Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/[username]/page.tsx](src/app/[username]/page.tsx)
- [src/app/api/prompts/[id]/route.ts](src/app/api/prompts/[id]/route.ts)
- [src/app/api/prompts/route.ts](src/app/api/prompts/route.ts)
- [src/app/categories/[slug]/page.tsx](src/app/categories/[slug]/page.tsx)
- [src/app/collection/page.tsx](src/app/collection/page.tsx)
- [src/app/feed/page.tsx](src/app/feed/page.tsx)
- [src/app/prompts/[id]/edit/page.tsx](src/app/prompts/[id]/edit/page.tsx)
- [src/app/prompts/[id]/page.tsx](src/app/prompts/[id]/page.tsx)
- [src/app/skills/page.tsx](src/app/skills/page.tsx)
- [src/app/tags/[slug]/page.tsx](src/app/tags/[slug]/page.tsx)
- [src/components/prompts/discovery-prompts.tsx](src/components/prompts/discovery-prompts.tsx)
- [src/components/prompts/prompt-form.tsx](src/components/prompts/prompt-form.tsx)

</details>



This document covers the Create, Read, Update, and Delete (CRUD) operations for prompts in the `prompts.chat` system. It details the API endpoints, validation logic, authorization rules, file uploads, rate limiting, duplicate detection, quality checking, and persistence workflows that govern prompt lifecycle management.

For prompt discovery mechanisms (browsing, filtering, search), see [Prompt Discovery & Browsing](). For prompt execution and the `RunPromptButton`, see [Prompt Execution & Run Buttons](). For versioning and change request workflows, see [Versioning & Change Requests]().

---

## CRUD Operations Overview

The prompt CRUD system is implemented through Next.js API routes and server actions with validation, authorization, and media upload handling pipelines bridging user interfaces with PostgreSQL persistence.

**CRUD Architecture Overview**

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        PromptForm["PromptForm<br/>src/components/prompts/prompt-form.tsx"]
        PromptPage["PromptPage<br/>src/app/prompts/[id]/page.tsx"]
        EditPage["EditPromptPage<br/>src/app/prompts/[id]/edit/page.tsx"]
    end
    
    subgraph "CodeEntitySpace"
        CreateAPI["POST /api/prompts<br/>src/app/api/prompts/route.ts"]
        ListAPI["GET /api/prompts<br/>src/app/api/prompts/route.ts"]
        GetAPI["GET /api/prompts/[id]<br/>src/app/api/prompts/[id]/route.ts"]
        UpdateAPI["PATCH /api/prompts/[id]<br/>src/app/api/prompts/[id]/route.ts"]
        DeleteAPI["DELETE /api/prompts/[id]<br/>src/app/api/prompts/[id]/route.ts"]
        UploadAPI["POST /api/upload<br/>src/app/api/upload/route.ts"]
        CreatePromptFn["createPrompt()<br/>src/lib/prompt-write.ts"]
        UpdatePromptFn["updatePrompt()<br/>src/lib/prompt-write.ts"]
    end
    
    subgraph "DatabaseSpace"
        DB[("PostgreSQL<br/>prisma/schema.prisma")]
    end
    
    PromptForm -->|Create| CreateAPI
    PromptForm -->|Update| UpdateAPI
    PromptForm -->|Upload| UploadAPI
    EditPage -->|Load| GetAPI
    PromptPage -->|Display| GetAPI
    
    CreateAPI --> CreatePromptFn
    UpdateAPI --> UpdatePromptFn
    
    CreatePromptFn --> DB
    UpdatePromptFn --> DB
    DeleteAPI --> DB
    ListAPI --> DB
    GetAPI --> DB
```

Sources:
- [src/app/api/prompts/route.ts:10-33]()
- [src/app/api/prompts/[id]/route.ts:11-219]()
- [src/components/prompts/prompt-form.tsx:1-190]()
- [src/app/api/upload/route.ts:17-120]()

---

## Create Operation

### POST /api/prompts Endpoint

The create operation is exposed via `POST /api/prompts` [src/app/api/prompts/route.ts:10-33]() which authenticates users via session or admin API key [src/app/api/prompts/route.ts:12]() and delegates persistence logic to the `createPrompt` helper [src/app/api/prompts/route.ts:20]().

**Create Operation Flow with Code Entities**

```mermaid
sequenceDiagram
    participant Client as "PromptForm<br/>src/components/prompts/prompt-form.tsx"
    participant API as "POST /api/prompts<br/>src/app/api/prompts/route.ts"
    participant Auth as "getSessionOrAdminApiKeyUser()<br/>src/lib/admin-auth.ts"
    participant Writer as "createPrompt()<br/>src/lib/prompt-write.ts"
    participant DB as "db.prompt<br/>src/lib/db.ts"
    
    Client->>API: "fetch('/api/prompts', {method: 'POST'})"
    API->>Auth: "getSessionOrAdminApiKeyUser(request)"
    Auth-->>API: "user"
    
    alt "!user"
        API-->>Client: "401 unauthorized"
    end
    
    API->>Writer: "createPrompt(user, body)"
    Writer->>DB: "db.prompt.create()"
    DB-->>Writer: "prompt object"
    Writer-->>API: "result"
    
    alt "!result.ok"
        API-->>Client: "result.status result.body"
    end
    
    API-->>Client: "200 Success"
```

Sources:
- [src/app/api/prompts/route.ts:10-33]()
- [src/app/api/prompts/[id]/route.ts:102-130]()

### Authentication & Authorization

Mutations require user context provided by session checking or API keys. Authorization levels govern resource modifications.

**Authorization Levels:**

| Operation             | Requirement                  | Code Pointer                              |
|-----------------------|------------------------------|------------------------------------------|
| Create Prompt         | Authenticated User / API Key | [src/app/api/prompts/route.ts:12-18]()  |
| View Private Prompt   | Author or Admin              | [src/app/api/prompts/[id]/route.ts:59-64]() |
| Update Prompt         | Author or Admin              | [src/app/api/prompts/[id]/route.ts:108-115]() |
| Delete Prompt (Soft)  | Admin or Owner (if delisted) | [src/app/api/prompts/[id]/route.ts:176-192]() |

Sources:
- [src/app/api/prompts/route.ts:10-18]()
- [src/app/api/prompts/[id]/route.ts:59-64]()
- [src/app/api/prompts/[id]/route.ts:176-192]()

### Validation, Duplicate Detection & Quality Checking

Prompt submissions undergo client-side and server-side validation using Zod schemas, duplicate detection mechanisms, and AI quality checks.
*   **Validation Schemas**: Forms use React Hook Form combined with Zod resolvers (`PromptForm` [src/components/prompts/prompt-form.tsx:6-8]()) to validate titles, content, categories, tag selections, and media requirements.
*   **Duplicate Detection**: Checks are performed during prompt ingestion and creation to prevent identical or heavily overlapping prompt slugs and content hashes within categories.
*   **Quality Checking**: Automated moderation checks scan prompt content for spam, token anomalies, or missing formatting structures, flagging low-quality prompts for auto-delisting.

Sources:
- [src/components/prompts/prompt-form.tsx:1-55]()
- [src/app/api/prompts/route.ts:10-33]()

### File Uploads & Media Handling

Prompts supporting media attachments utilize `POST /api/upload` [src/app/api/upload/route.ts:17-120]() when storage plugins are enabled. The `MediaField` component [src/components/prompts/prompt-form.tsx:68-190]() handles the UI for media uploads and generation.

*   **Size Limits**: Enforces a 4MB maximum size for both images and videos (Vercel serverless limit) [src/components/prompts/prompt-form.tsx:102-106]().
*   **Type Validation**: Restricts uploads to allowed MIME types (`image/jpeg`, `image/png`, `image/gif`, `image/webp`, `video/mp4`, `audio/mpeg`, `audio/mp3`, `audio/wav`, `audio/ogg`) [src/components/prompts/prompt-form.tsx:110-117]().
*   **Media Generation**: Integrates with `/api/media-generate` to allow AI-powered media generation if providers are configured [src/components/prompts/prompt-form.tsx:88-96]().

Sources:
- [src/app/api/upload/route.ts:1-120]()
- [src/components/prompts/prompt-form.tsx:68-190]()

---

## Read Operations

### Single Prompt Retrieval

Prompts are retrieved via the `GET` handler in `src/app/api/prompts/[id]/route.ts` [src/app/api/prompts/[id]/route.ts:11-99](). 

*   **Public Access**: Prompts with `deletedAt: null` are accessible unless marked private [src/app/api/prompts/[id]/route.ts:51-64]().
*   **Private Access**: Author-only check via `prompt.authorId !== session?.user?.id` [src/app/api/prompts/[id]/route.ts:59]().
*   **Slug Support**: Frontend components parse URLs containing ID and slug segments. The `extractPromptId` function [src/app/prompts/[id]/edit/page.tsx:17-22]() handles this for edit pages.

### Prompt Listing & Filtering

The public API listing endpoint (`GET /api/prompts`) supports pagination, category filtering, tag filtering, type constraints, and sorting [src/app/api/prompts/route.ts:56-207]().

*   **Pagination**: `page` and `perPage` query parameters control results, with defaults and maximums enforced [src/app/api/prompts/route.ts:60-70]().
*   **Type Filtering**: The `type` query parameter allows filtering by `PromptType` (e.g., `TEXT`, `IMAGE`, `BOT`). By default, `BOT` and `CLASSIFIER` types are excluded from general listings [src/lib/prompt-list.ts:8](), unless explicitly requested [src/lib/prompt-list.ts:15]().
*   **Trending**: The `trending=1` parameter filters for prompts marked as trending [src/app/api/prompts/route.ts:130-133]().
*   **Workflows**: The `/workflows` page [src/app/workflows/page.tsx:1-174]() specifically queries for prompts that are part of a workflow chain, excluding `SKILL`, `BOT`, and `CLASSIFIER` types, and requiring outgoing connections that are not "related" [src/app/workflows/page.tsx:24-35]().

Sources:
- [src/app/api/prompts/[id]/route.ts:11-99]()
- [src/app/api/prompts/route.ts:56-207]()
- [src/app/prompts/[id]/edit/page.tsx:17-22]()

---

## Update & Delete Operations

### Updating Prompts (PATCH)

Updates are handled by `PATCH /api/prompts/[id]` [src/app/api/prompts/[id]/route.ts:102-130]() which verifies user session status and delegates to `updatePrompt` [src/app/api/prompts/[id]/route.ts:117](). The `EditPromptPage` [src/app/prompts/[id]/edit/page.tsx:1-124]() loads existing prompt data and passes it to the `PromptForm` for editing.

### Deletion (DELETE)

Prompt deletion is performed via soft deletion in `DELETE /api/prompts/[id]` [src/app/api/prompts/[id]/route.ts:135-219]().
*   **Ownership and Delist Rules**: Admins can delete any prompt. Authors can only delete prompts that have been automatically delisted for quality issues [src/app/api/prompts/[id]/route.ts:176-192]().
*   **Timestamping**: Sets the `deletedAt` field to the current timestamp [src/app/api/prompts/[id]/route.ts:195-198]().

Sources:
- [src/app/api/prompts/[id]/route.ts:102-219]()
- [src/app/prompts/[id]/edit/page.tsx:1-124]()

---

## Database Schema Reference

### Prompt Model

The core entity defined in `prisma/schema.prisma` [prisma/schema.prisma:94-147]().

| Field                 | Type                 | Description                                               |
|-----------------------|----------------------|-----------------------------------------------------------|
| `id`                  | String               | Primary Key (CUID)                                        |
| `title`               | String               | Prompt title                                             |
| `slug`                | String?              | URL-friendly slug generated from title                   |
| `description`         | String?              | Optional description of the prompt                       |
| `content`             | String               | The actual prompt instruction text                       |
| `type`                | PromptType           | TEXT, IMAGE, VIDEO, AUDIO, SKILL, TASTE, BOT, CLASSIFIER |
| `isPrivate`           | Boolean              | Visibility toggle                                        |
| `isUnlisted`          | Boolean              | Delisted from discovery feeds                            |
| `deletedAt`           | DateTime?            | Soft delete timestamp                                   |
| `mediaUrl`            | String?              | URL for attached media                                   |
| `requiresMediaUpload` | Boolean              | Indicates if upload is required for media                 |
| `bestWithModels`      | String[]             | Array of AI model slugs this prompt works best with (max 3) [prisma/schema.prisma:137]() |
| `workflowLink`        | String?              | URL to test/demo the workflow [prisma/schema.prisma:139]() |

Sources:
- [prisma/schema.prisma:94-147]()

---

# Page: Skills & Multi-file Prompts

# Skills & Multi-file Prompts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/api/prompts/[id]/skill/route.ts](src/app/api/prompts/[id]/skill/route.ts)
- [src/components/prompts/skill-viewer.tsx](src/components/prompts/skill-viewer.tsx)
- [src/lib/skill-files.ts](src/lib/skill-files.ts)

</details>



This page documents the **Skill** prompt type in prompts.chat, which enables managing complex multi-file bundles as a single prompt entity. It covers serialization format requirements (`SKILL.md`), key functions for parsing and serializing skill files, UI components for skill viewing, editing, and diff navigation, `taste.md` files, archive export routes, and Model Context Protocol (MCP) skill tools for programmatic agent interaction.

Sources: [src/lib/skill-files.ts:1-21](), [src/app/api/prompts/[id]/skill/route.ts:35-44]()

---

## Purpose & Scope

The skill system bridges natural language instructions with structured multi-file packaging. It allows developers and prompt engineers to package complete coding environments, instruction sheets, reference documentation, and scripts into a single database record (`Prompt.type = "SKILL"`). These records can then be parsed, inspected via a hierarchical file tree UI, downloaded as a `.skill` archive, or manipulated programmatically via the MCP server.

Sources: [src/lib/skill-files.ts:1-21](), [src/app/api/prompts/[id]/skill/route.ts:35-44]()

---

## What is a Skill?

A **Skill** is a specialized prompt entity stored in the database with `type = "SKILL"`. Unlike standard single-string prompts, a skill bundles multiple related files into a single serialized text string within the `Prompt.content` database field.

The entry point for every skill is `SKILL.md` (defined as `DEFAULT_SKILL_FILE`), which contains frontmatter metadata and top-level instructions. Skills are designed for consumption by AI coding tools and IDE agents (such as Cursor, Windsurf, and Claude Code).

- `DEFAULT_SKILL_FILE` = `"SKILL.md"` [src/lib/skill-files.ts:30-30]()
- Database query filter for skills: `type = "SKILL"` and `content` storing serialized multi-file payloads [src/app/api/prompts/[id]/skill/route.ts:35-44]()

Sources: [src/lib/skill-files.ts:30-30](), [src/app/api/prompts/[id]/skill/route.ts:35-44]()

---

## Serialization Format & Core Functions

To persist multiple files inside a single relational database text column without risk of injection or delimiter collisions, prompts.chat uses ASCII control characters as injection-proof file separators.

| Control Char | Name | ASCII Hex | Usage |
|--------------|------|-----------|-------|
| `\x1F` | Unit Separator | 0x1F | Marks start of file header (`FILE:<filename>`) [src/lib/skill-files.ts:4-15]() |
| `\x1E` | Record Separator | 0x1E | Marks end of file header [src/lib/skill-files.ts:4-15]() |

### Serialization Format Layout

```
[SKILL.md content]
\x1FFILE:<filename.ext>\x1E
[file content]
\x1FFILE:<another-file.js>\x1E
[another file content]
```

### Key Library Functions

- `parseSkillFiles(content: string): SkillFile[]`: Parses a serialized skill string into an array of `{ filename, content }` structures. Defaults to a single `SKILL.md` entry if content is empty or un-separated [src/lib/skill-files.ts:52-82]().
- `serializeSkillFiles(files: SkillFile[]): string`: Reconstructs a single serialized string from an array of `SkillFile` objects, ensuring `SKILL.md` always leads the payload [src/lib/skill-files.ts:88-105]().
- `sanitizeFilename(filename: string): string | null`: Server-side path sanitization utility that blocks path traversal sequences (like `..`), null bytes, and invalid characters to prevent Zip Slip vulnerabilities [src/lib/skill-files.ts:201-211]().
- `getLanguageFromFilename(filename: string): string`: Maps file extensions (e.g. `.ts`, `.md`, `.py`) to Monaco editor language identifiers [src/lib/skill-files.ts:110-194]().

Sources: [src/lib/skill-files.ts:1-211]()

---

## Skill File Tree Structure & Data Flow

To bridge the gap between flat database storage and the nested workspace expected by users, the frontend transforms flat `SkillFile` arrays into a hierarchical directory tree.

Title: "Skill Parsing and Tree Construction Data Flow"
```mermaid
graph TD
    subgraph "Natural Language Space"
        NLContent["PromptContentStringInDb"]
    end

    subgraph "Code Entity Space"
        NLContent -->|"parseSkillFiles(content)"| SkillFileArray["SkillFile[]"]
        SkillFileArray -->|"buildFileTree(files)"| TreeNodeHierarchy["TreeNode[]"]
        TreeNodeHierarchy -->|"TreeNodeItem"| SidebarUI["FileTreeSidebarUI"]
        TreeNodeHierarchy -->|"activeFile state"| MonacoEditor["Editor"]
    end
```
Sources: [src/components/prompts/skill-viewer.tsx:46-88](), [src/lib/skill-files.ts:52-82]()

---

## SkillViewer, Editor & Diff UI Components

The `SkillViewer` component (`src/components/prompts/skill-viewer.tsx`) provides a dual-pane workspace containing a file tree sidebar and a syntax-highlighted code editor. Additional components like editor wrappers and diff viewers provide full editing and version comparison capabilities.

- **File Tree Navigation:** Rendered via the recursive component `TreeNodeItem`, supporting folder expansion/collapse states and active file highlighting [src/components/prompts/skill-viewer.tsx:100-168]().
- **Language Detection:** Dynamically configures `@monaco-editor/react` using `getLanguageFromFilename` [src/components/prompts/skill-viewer.tsx:189-193](), [src/lib/skill-files.ts:110-194]().
- **Clipboard & Export Actions:** Provides utilities to copy active file contents to the clipboard or download individual files [src/components/prompts/skill-viewer.tsx:226-245]().
- **Filename Validation:** Client-side validation using `validateFilename` guards against duplicate filenames and reserved naming violations [src/lib/skill-files.ts:229-250]().

Sources: [src/components/prompts/skill-viewer.tsx:1-245](), [src/lib/skill-files.ts:110-194](), [src/lib/skill-files.ts:229-250]()

---

## Taste.md Files & Multi-File Artifacts

In addition to core executable skills (`SKILL.md`), prompts.chat supports specialized auxiliary files such as `taste.md`. These files capture stylistic guidelines, preferences, design tokens, and aesthetic constraints for AI agents. When bundled within a multi-file skill prompt or standalone taste record, `taste.md` provides contextual taste profiles that agents load alongside instructions to align output tone and style with user expectations.

Sources: [src/lib/skill-files.ts:30-46]()

---

## Archive Download Endpoint

Users can export an entire skill bundle as a `.skill` archive (ZIP format).

- **Route:** `GET /api/prompts/[id]/skill` [src/app/api/prompts/[id]/skill/route.ts:27-30]()
- **Implementation Details:**
  1. Parses the prompt ID, trimming any `.skill` extensions or slug suffixes [src/app/api/prompts/[id]/skill/route.ts:10-25]().
  2. Queries `db.prompt.findFirst` ensuring `type: "SKILL"`, `deletedAt: null`, and `isPrivate: false` [src/app/api/prompts/[id]/skill/route.ts:35-44]().
  3. Parses skill records using `parseSkillFiles` [src/app/api/prompts/[id]/skill/route.ts:51]() and sanitizes each filename via `sanitizeFilename` [src/app/api/prompts/[id]/skill/route.ts:63]().
  4. Bundles files into an archive using `JSZip` with DEFLATE compression [src/app/api/prompts/[id]/skill/route.ts:54-75]().
  5. Returns a binary response with `Content-Type: application/octet-stream` and a slugified attachment filename [src/app/api/prompts/[id]/skill/route.ts:81-86]().

Sources: [src/app/api/prompts/[id]/skill/route.ts:1-87]()

---

## MCP Skill Tools

The Model Context Protocol server at `/api/mcp` exposes dedicated tools for programmatic skill discovery, retrieval, creation, and incremental file manipulation.

Title: "MCP Skill Tool Execution Pipeline"
```mermaid
graph TD
    subgraph "Natural Language Space"
        AgentRequest["AgentMcpToolRequestPayload"]
    end

    subgraph "Code Entity Space"
        AgentRequest --> MCPRoute["ApiMcpEndpointHandler"]
        MCPRoute --> RateLimiter["rateLimiterInstance"]
        RateLimiter --> AuthCheck["authenticateApiKey"]
        AuthCheck --> DBQuery["db.prompt"]
        DBQuery --> SkillLib["parseSkillFiles / serializeSkillFiles"]
        SkillLib --> Persistence["PromptRecordPersistence"]
    end
```

### Available MCP Skill Tools
- **`search_skills`**: Searches prompts filtered by `type='SKILL'` and query parameters [src/pages/api/mcp.ts:130-175]().
- **`get_skill`**: Retrieves a skill prompt by ID or slug and parses its contents into individual files [src/pages/api/mcp.ts:213-230]().
- **`save_skill`**: Creates a new multi-file skill record for authenticated users [src/pages/api/mcp.ts:32-53]().
- **`add_file_to_skill`** / **`update_skill_file`** / **`remove_file_from_skill`**: Atomically modify individual files within an existing skill payload using parse-modify-serialize cycles.

### Rate Limiting & Security
MCP endpoints enforce strict rate limiting via `RateLimiter` instances defined in `src/lib/rate-limit.ts`:
- General requests: 20 req/min (`mcpGeneralLimiter`) [src/lib/rate-limit.ts:84]()
- Tool calls: 10 req/min (`mcpToolCallLimiter`) [src/lib/rate-limit.ts:87]()
- Write mutations (saves, file additions): 5 req/min (`mcpWriteToolLimiter`) [src/lib/rate-limit.ts:90]()
- AI tools: 2 req/min (`mcpAiToolLimiter`) [src/lib/rate-limit.ts:93]()

API key authentication uses an in-memory cache with a 5-minute TTL to optimize validation overhead [src/pages/api/mcp.ts:28-30]().

Sources: [src/pages/api/mcp.ts:1-53](), [src/pages/api/mcp.ts:130-230](), [src/lib/rate-limit.ts:22-93]()

---

# Page: Prompt Discovery & Browsing

# Prompt Discovery & Browsing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/__tests__/api/prompts.test.ts](src/__tests__/api/prompts.test.ts)
- [src/__tests__/lib/prompt-list.test.ts](src/__tests__/lib/prompt-list.test.ts)
- [src/__tests__/lib/seo.test.ts](src/__tests__/lib/seo.test.ts)
- [src/app/[username]/layout.tsx](src/app/[username]/layout.tsx)
- [src/app/categories/[slug]/layout.tsx](src/app/categories/[slug]/layout.tsx)
- [src/app/prompts/(list)/page.tsx](src/app/prompts/(list)/page.tsx)
- [src/app/tags/[slug]/layout.tsx](src/app/tags/[slug]/layout.tsx)
- [src/app/workflows/page.tsx](src/app/workflows/page.tsx)
- [src/components/prompts/prompt-filters.tsx](src/components/prompts/prompt-filters.tsx)
- [src/lib/prompt-list.ts](src/lib/prompt-list.ts)
- [src/lib/seo.ts](src/lib/seo.ts)

</details>



This document covers the technical implementation of prompt discovery, browsing interfaces, filtering mechanisms, search capabilities, and pagination with infinite scroll in the `prompts.chat` codebase. It elaborates on key routes, server-side data fetching, UI components, and the data flow that bridges user inputs to rendered prompt listings.

---

## Discovery Entry Points & Route Architecture

`prompts.chat` provides multiple specialized routes for browsing prompts, agent skills, workflows, and taste-based collections. Each route delegates to specific server components and data-fetching utilities.

Title: Discovery Routes to Code Entities Architecture
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        NLPrompts["Main Prompts Discovery (/prompts)"]
        NLSkills["Agent Skills Discovery (/skills)"]
        NLWorkflows["Workflows Discovery (/workflows)"]
        NLCats["Category Browsing (/categories/[slug])"]
        NLTags["Tag Browsing (/tags/[slug])"]
        NLUser["User Profile Discovery (/@username)"]
        NLCollection["User Collection (/collection)"]
        NLFeed["User Feed (/feed)"]
    end

    subgraph "CodeEntitySpace"
        CEPrompts["PromptsPage <br/> src/app/prompts/(list)/page.tsx"]
        CESkills["SkillsPage <br/> src/app/skills/page.tsx"]
        CEWorkflows["WorkflowsPage <br/> src/app/workflows/page.tsx"]
        CECats["CategoryLayout <br/> src/app/categories/[slug]/layout.tsx"]
        CETags["TagLayout <br/> src/app/tags/[slug]/layout.tsx"]
        CEUser["UserProfileLayout <br/> src/app/[username]/layout.tsx"]
        CECollection["CollectionPage <br/> src/app/collection/page.tsx"]
        CEFeed["FeedPage <br/> src/app/feed/page.tsx"]
        CEInfinite["InfinitePromptList <br/> src/components/prompts/infinite-prompt-list.tsx"]
    end

    NLPrompts --> CEPrompts
    CEPrompts --> CEInfinite
    NLSkills --> CESkills
    CESkills --> CEInfinite
    NLWorkflows --> CEWorkflows
    CEWorkflows --> CEInfinite
    NLCats --> CECats
    NLTags --> CETags
    CETags --> CETags
    NLUser --> CEUser
    NLCollection --> CECollection
    NLFeed --> CEFeed
```

- **`/prompts`**: Handled by `PromptsPage`, serving as the primary hub with client-side infinite scrolling (`InfinitePromptList`) [src/app/prompts/(list)/page.tsx:1-20](), [src/app/workflows/page.tsx:164-171]().
- **`/skills`**: Lists agent skills (`type: "SKILL"`) via `SkillsPage` [src/app/skills/page.tsx:1-100]().
- **`/workflows`**: Lists connected execution workflows via `WorkflowsPage` [src/app/workflows/page.tsx:10-109]().
- **`/categories/[slug]`**: Handled by `CategoryLayout`, validating range parameters before rendering category-filtered prompts [src/app/categories/[slug]/layout.tsx:21-39]().
- **`/tags/[slug]`**: Handled by `TagLayout`, enforcing tag validation and pagination bounds [src/app/tags/[slug]/layout.tsx:22-40]().
- **`/@username`**: Handled by `UserProfileLayout`, showing user-authored public/private prompts, contributions, and pinned items [src/app/[username]/layout.tsx:24-59]().
- **`/collection`**: Displays a user's bookmarked prompts via `CollectionPage` [src/app/collection/page.tsx:1-72]().
- **`/feed`**: Shows a personalized feed based on subscribed categories via `FeedPage` [src/app/feed/page.tsx:1-94]().

Sources:
[src/app/prompts/(list)/page.tsx:1-20](),
[src/app/skills/page.tsx:1-100](),
[src/app/workflows/page.tsx:10-174](),
[src/app/categories/[slug]/layout.tsx:21-39](),
[src/app/tags/[slug]/layout.tsx:22-40](),
[src/app/[username]/layout.tsx:24-59]()

---

## Main Prompts Page Implementation (`/prompts`)

The core browsing interface at `/prompts` parses search parameters (`q`, `type`, `category`, `tag`, `sort`, `ai`) to query the database, utilizing either AI semantic search or relational filtering via helper utilities like `promptListTypeWhere` [src/lib/prompt-list.ts:14-16]().

Title: Prompt Search and Filtering Data Flow
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        NLParams["URL Search Parameters q type category tag sort ai"]
    end

    subgraph "CodeEntitySpace"
        NLParams --> PromptsRoute["PromptsPage <br/> src/app/prompts/(list)/page.tsx"]
        PromptsRoute --> CheckAI{"isAISearchEnabled() & params.ai === '1'"}
        
        CheckAI -- "Yes" --> SemanticSearch["semanticSearch() <br/> src/lib/ai/embeddings.ts"]
        CheckAI -- "No" --> RelationalQuery["getCachedPrompts() <br/> Prisma db.prompt.findMany()"]

        SemanticSearch --> InfiniteList["InfinitePromptList <br/> src/components/prompts/infinite-prompt-list.tsx"]
        RelationalQuery --> InfiniteList
        
        InfiniteList --> InjectWidgets["injectWidgets() <br/> src/lib/plugins/widgets/index.ts"]
        InjectWidgets --> RenderGrid["Masonry Grid Rendering"]
    end
```

### Search & Filtering Logic
- When `ai=1` and `q` is specified, `semanticSearch()` evaluates vector embeddings across prompts [src/app/prompts/(list)/page.tsx:15-15]().
- Type filters are governed by `promptListTypeWhere()` which abstracts out `BOT` and `CLASSIFIER` records unless explicitly requested [src/lib/prompt-list.ts:14-16]().
- Visibility and hierarchy filters automatically enforce:
  - `isPrivate: false`
  - `isUnlisted: false`
  - `deletedAt: null`
  - Exclusion of intermediate flow steps via relational queries [src/app/workflows/page.tsx:20-36]().

Sources:
[src/app/prompts/(list)/page.tsx:1-20](),
[src/lib/prompt-list.ts:14-16](),
[src/app/workflows/page.tsx:20-36]()

---

## Category, Tag, and Profile Layout Guards

### Category Layout (`/categories/[slug]`)
- Validates category existence using `db.category.findUnique()` [src/app/categories/[slug]/layout.tsx:23-24]().
- Enforces strict out-of-range page interception via `isPageOutOfRange()` to return real `404` errors before rendering [src/app/categories/[slug]/layout.tsx:30-36]().

### Tag Layout (`/tags/[slug]`)
- Looks up tags by slug using `db.tag.findUnique()` [src/app/tags/[slug]/layout.tsx:24-24]().
- Verifies pagination offsets against `tagPromptsWhere()` counts [src/app/tags/[slug]/layout.tsx:30-37]().

### User Profile Layout (`/@username`)
- Parses `@username` identifiers, decoding percent-encoded strings and validating username existence case-insensitively [src/app/[username]/layout.tsx:25-37]().
- Verifies page limits for authenticated user sessions depending on private prompt visibility [src/app/[username]/layout.tsx:43-56]().

Sources:
[src/app/categories/[slug]/layout.tsx:21-39](),
[src/app/tags/[slug]/layout.tsx:22-40](),
[src/app/[username]/layout.tsx:24-59]()

---

## Skills, Workflows, and Curated Discovery

- **Skills (`/skills`)**: Queries agent skills using `getCachedSkills` where `type: "SKILL"` with keyword matching and sorting options [src/app/skills/page.tsx:13-100]().
- **Workflows (`/workflows`)**: Identifies execution chains using `getCachedWorkflows` which filters out skills and enforces strict non-related outgoing flow connections [src/app/workflows/page.tsx:10-109]().
- **Curated Discovery (`DiscoveryPrompts`)**: Aggregates featured, trending, latest, and most upvoted prompt groups [src/components/prompts/discovery-prompts.tsx:1-134]().

Sources:
[src/app/skills/page.tsx:13-100](),
[src/app/workflows/page.tsx:10-109](),
[src/components/prompts/discovery-prompts.tsx:1-134]()

---

## Infinite Scroll, Pagination, and Clamping

### Pagination Bounds & Validation
- Pagination parameters are safely parsed and clamped [src/__tests__/api/prompts.test.ts:105-118]().
- Request clamping ensures `perPage` values do not exceed configured backend limits (e.g., maximum 100 items per page) [src/__tests__/api/prompts.test.ts:115-118]().
- Malformed page parameters automatically fall back to page `1` and default items per page [src/__tests__/api/prompts.test.ts:90-103]().

Sources:
[src/__tests__/api/prompts.test.ts:90-118]()

---

## Widget Injection Pipeline

`injectWidgets` modifies prompt listings by weaving in sponsored or promotional widget prompts based on contextual rules.

Title: Widget Injection Pipeline Data Flow
```mermaid
graph TD
    Start["Call injectWidgets(items, context)"] --> FetchWidgets["Get all WidgetPlugins from registry"]
    FetchWidgets --> CheckShouldInject{"Evaluate widget.shouldInject(context)"}
    CheckShouldInject -- "True" --> CalcPos["Calculate insertion positions via getWidgetInsertionPositions()"]
    CalcPos --> Splice["Splice widgets into array with isWidget: true flag"]
    Splice --> End["Return mixed array of prompts and widgets"]
```

- **Positioning Modes**: Configured via widget position settings with modes such as once or repeat intervals.
- **Context Filtering**: Widgets define `shouldInject` functions to suppress insertion on specific routes or query parameters.

Sources:
[src/components/prompts/discovery-prompts.tsx:1-134]()

---

## Summary of Filtering & Sorting Strategies

| Filter Type | Implementation Mechanics | Code Reference |
| ----------- | ------------------------ | -------------- |
| Text Search | Prisma `contains` with `insensitive` mode; comma-separated terms map to `OR` clauses. Fallback to `semanticSearch()` when `ai=1`. | [src/app/prompts/(list)/page.tsx:15-15]() |
| Prompt Types | Managed via `promptListTypeWhere()` excluding `BOT` and `CLASSIFIER` by default. | [src/lib/prompt-list.ts:14-16]() |
| Category | Foreign key match via `categoryId` or category `slug` with layout guard checks. | [src/app/categories/[slug]/layout.tsx:23-24]() |
| Tag | Relation filter via tag association with layout validation. | [src/app/tags/[slug]/layout.tsx:24-24]() |
| Sort Options | Mapped to Prisma `orderBy` clauses (`createdAt`, `votes._count`, etc.). | [src/app/workflows/page.tsx:138-146]() |
| Trending | Filters prompts based on `trendingUntil` field using `trendingPromptListWhere()` [src/lib/prompt-list.ts:22-30](). | [src/lib/prompt-list.ts:22-30]() |
| Date Filter | Used on user profiles to filter prompts by `createdAt` within specific bounds [src/app/[username]/layout.tsx:50-51](). | [src/app/[username]/layout.tsx:50-51]()

Sources:
[src/app/prompts/(list)/page.tsx:15-15](),
[src/lib/prompt-list.ts:14-30](),
[src/app/categories/[slug]/layout.tsx:23-24](),
[src/app/tags/[slug]/layout.tsx:24-24](),
[src/app/workflows/page.tsx:138-146](),
[src/app/[username]/layout.tsx:50-51]()

---

# Page: Prompt Execution & Run Buttons

# Prompt Execution & Run Buttons

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/prompts.chat/src/__tests__/platforms.test.ts](packages/prompts.chat/src/__tests__/platforms.test.ts)
- [packages/prompts.chat/src/cli/platforms.ts](packages/prompts.chat/src/cli/platforms.ts)
- [packages/raycast-extension/src/utils.ts](packages/raycast-extension/src/utils.ts)
- [src/__tests__/lib/works-best-with.test.ts](src/__tests__/lib/works-best-with.test.ts)
- [src/components/prompts/interactive-prompt-content.tsx](src/components/prompts/interactive-prompt-content.tsx)
- [src/components/prompts/prompt-card.tsx](src/components/prompts/prompt-card.tsx)
- [src/components/prompts/run-prompt-button.tsx](src/components/prompts/run-prompt-button.tsx)
- [src/lib/works-best-with.ts](src/lib/works-best-with.ts)

</details>



## Purpose and Scope

This document provides an in-depth technical overview of the prompt execution system within `prompts.chat`. It covers the `RunPromptButton` component [src/components/prompts/run-prompt-button.tsx:1-431](), platform URL construction logic [packages/prompts.chat/src/cli/platforms.ts:62-134](), the dynamic variable filling system [src/components/prompts/interactive-prompt-content.tsx:43-68](), and deep link support for launching IDEs or AI platforms seamlessly [packages/prompts.chat/src/cli/platforms.ts:26-31]().

Sources: [src/components/prompts/run-prompt-button.tsx:1-431](), [packages/prompts.chat/src/cli/platforms.ts:62-134](), [src/components/prompts/interactive-prompt-content.tsx:43-68](), [packages/prompts.chat/src/cli/platforms.ts:26-31]()

---

## Platform Architecture & Data Model

External platforms are classified into typed categories via `Platform` interfaces, declared in web and CLI modules:
- `src/lib/run-platforms.ts` (Web UI runtime, imported by `src/components/prompts/run-prompt-button.tsx`)
- `packages/prompts.chat/src/cli/platforms.ts` (CLI utility)
- `packages/raycast-extension/src/utils.ts` (Raycast integration)

### Platform Categories

| Category | Description | Key Code Entity | Notable Platforms |
| --- | --- | --- | --- |
| Chat Platforms | Web-based AI assistants | `chatPlatforms` [packages/prompts.chat/src/cli/platforms.ts:41-60]() | ChatGPT, Claude, DeepSeek |
| Code Platforms | IDEs and code generation tools with deep links | `codePlatforms` [packages/prompts.chat/src/cli/platforms.ts:26-39]() | VS Code, Windsurf, Cursor, Goose |
| Image Platforms | Image generation services | `imagePlatforms` [packages/prompts.chat/src/cli/platforms.ts:11-16]() | Mitte.ai (Nano Banana, Flux 2) |
| Video Platforms | Video generation services | `videoPlatforms` [packages/prompts.chat/src/cli/platforms.ts:19-24]() | Mitte.ai (Veo 3.1, Sora 2) |

Each platform object conforms to the `Platform` interface containing `id`, `name`, `baseUrl`, `supportsQuerystring`, `isDeeplink`, and `sponsor` [packages/prompts.chat/src/cli/platforms.ts:1-8]().

### Platform Routing from Natural Language to Code Entities

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        NL_Chat["AI Chat Assistant"]
        NL_IDE["Developer IDE or Code Tool"]
        NL_Img["Image Generation Service"]
        NL_Vid["Video Generation Service"]
    end

    subgraph "CodeEntitySpace"
        CP["chatPlatforms array<br/>[packages/prompts.chat/src/cli/platforms.ts:41-60]"]
        CdP["codePlatforms array<br/>[packages/prompts.chat/src/cli/platforms.ts:26-39]"]
        IP["imagePlatforms array<br/>[packages/prompts.chat/src/cli/platforms.ts:11-16]"]
        VP["videoPlatforms array<br/>[packages/prompts.chat/src/cli/platforms.ts:19-24]"]
        IFace["Platform Interface<br/>[packages/prompts.chat/src/cli/platforms.ts:1-8]"]
    end

    NL_Chat --> CP
    NL_IDE --> CdP
    NL_Img --> IP
    NL_Vid --> VP

    IFace --> CP
    IFace --> CdP
    IFace --> IP
    IFace --> VP
```

Sources: [packages/prompts.chat/src/cli/platforms.ts:1-60](), [src/components/prompts/run-prompt-button.tsx:36-42](), [packages/raycast-extension/src/utils.ts:44-232]()

---

## URL Construction System

The `buildUrl` function formats execution targets by encoding prompt content, titles, and descriptions according to individual platform parameters [packages/prompts.chat/src/cli/platforms.ts:62-134]().

### URL Encoding and URI Schemes
- **IDE Deep Links**: `cursor`, `vscode`, and `vscode-insiders` append parameters via custom URI schemes (`?text=` or `?prompt=`) [packages/prompts.chat/src/cli/platforms.ts:72-76]().
- **Goose**: Packages a JSON payload containing prompt text, title, description, and activities into a base64-encoded string assigned to the `config` query parameter [packages/prompts.chat/src/cli/platforms.ts:77-88]().
- **Web Chat / Builders**: Appends query strings using platform-specific parameter names (`?q=`, `?prompt=`, `&prompt=`) [packages/prompts.chat/src/cli/platforms.ts:92-130]().

### URL Construction Flow

```mermaid
graph TD
    Start["buildUrl(platformId, baseUrl, promptText) <br/>[packages/prompts.chat/src/cli/platforms.ts:62]"] --> Switch{"platformId match"}

    Switch -->|cursor| Cursor["cursor://anysphere.cursor-deeplink/prompt?text=encoded <br/>[packages/prompts.chat/src/cli/platforms.ts:72-73]"]
    Switch -->|vscode, vscode-insiders| VSCode["vscode://GitHub.Copilot-Chat/chat?prompt=encoded <br/>[packages/prompts.chat/src/cli/platforms.ts:74-76]"]
    Switch -->|goose| Goose["goose://recipe?config=base64JSON <br/>[packages/prompts.chat/src/cli/platforms.ts:77-88]"]
    Switch -->|chatgpt| ChatGPT["https://chatgpt.com/?q=encoded <br/>[packages/prompts.chat/src/cli/platforms.ts:92-93]"]
    Switch -->|bolt| Bolt["https://bolt.new?prompt=encoded <br/>[packages/prompts.chat/src/cli/platforms.ts:90-91]"]
    Switch -->|default| Fallback["baseUrl + '?q=' + encoded <br/>[packages/prompts.chat/src/cli/platforms.ts:131-132]"]
```

Unit tests verifying correct URL generation are located at `packages/prompts.chat/__tests__/platforms.test.ts` [packages/prompts.chat/__tests__/platforms.test.ts:1-22]().

Sources: [packages/prompts.chat/src/cli/platforms.ts:62-134](), [packages/prompts.chat/__tests__/platforms.test.ts:1-22]()

---

## Variable Filling System

Prompts containing template variables structured as `${variableName:defaultValue}` support runtime input substitution [src/components/prompts/interactive-prompt-content.tsx:43-68]().

### Core Variable Functions
- `parseVariables(content: string)`: Scans strings for `${...}` blocks and extracts variable names and default fallback values [src/components/prompts/interactive-prompt-content.tsx:43-57]().
- `getUniqueVariables()`: Filters duplicate variable declarations to yield distinct form fields [src/components/prompts/interactive-prompt-content.tsx:60-68]().
- `hasVariables(content: string)`: Determines whether variable substitution UI is necessary [src/components/prompts/prompt-card.tsx:159]().
- `compilePrompt(template, values)`: Replaces template tokens with user-supplied values [packages/raycast-extension/src/utils.ts:31-42]().

### Variable Processing Data Flow

```mermaid
sequenceDiagram
    participant User
    participant PromptCard as "PromptCard<br/>[src/components/prompts/prompt-card.tsx]"
    participant InteractivePromptContent as "InteractivePromptContent<br/>[src/components/prompts/interactive-prompt-content.tsx]"
    participant RunPromptButton as "RunPromptButton<br/>[src/components/prompts/run-prompt-button.tsx]"
    participant Parser as "parseVariables<br/>[src/components/prompts/interactive-prompt-content.tsx:43]"

    User->>PromptCard: Click "Run" or "Copy"
    PromptCard->>PromptCard: Check `contentHasVariables` using `hasVariables(prompt.content)` [src/components/prompts/prompt-card.tsx:159]
    
    alt `contentHasVariables` is true
        PromptCard->>RunPromptButton: Call `handleRun` with `unfilledVariables` [src/components/prompts/run-prompt-button.tsx:146]
        RunPromptButton->>RunPromptButton: `openVariableDialog` called [src/components/prompts/run-prompt-button.tsx:152]
        RunPromptButton->>Parser: `parseVariables` (via `unfilledVariables` prop)
        Parser-->>RunPromptButton: `UnfilledVariable[]`
        User->>RunPromptButton: Input custom values in dialog
        RunPromptButton->>RunPromptButton: `handleVariableSubmit` [src/components/prompts/run-prompt-button.tsx:118]
        RunPromptButton->>RunPromptButton: `getContentWithVariables` (if provided) or uses original content [src/components/prompts/run-prompt-button.tsx:125-127]
        RunPromptButton->>RunPromptButton: Construct URL with final content
    else `contentHasVariables` is false
        PromptCard->>RunPromptButton: Call `handleRun` directly with original content [src/components/prompts/run-prompt-button.tsx:156]
        RunPromptButton->>RunPromptButton: Construct URL with original content
    end
    RunPromptButton->>User: Open URL or copy to clipboard
```

Sources: [src/components/prompts/prompt-card.tsx:159](), [src/components/prompts/interactive-prompt-content.tsx:43-68](), [src/components/prompts/run-prompt-button.tsx:108-172](), [packages/raycast-extension/src/utils.ts:9-42]()

---

## RunPromptButton Component Implementation

The `RunPromptButton` component manages platform selection menus, dispatches analytics events via `analyticsPrompt` [src/components/prompts/run-prompt-button.tsx:32](), and opens the constructed URLs.

### Responsive UI Rendering
- **Mobile (`useIsMobile === true`)**: Renders platforms inside a bottom sheet container (`<Sheet>`) [src/components/prompts/run-prompt-button.tsx:26-31]().
- **Desktop**: Renders platforms using nested dropdown menus (`<DropdownMenu>`) categorized by type [src/components/prompts/run-prompt-button.tsx:16-24]().

The component dynamically determines the default active tab ("chat" or "code") based on the prompt's category or parent category name, checking for keywords like "code" or "coding" [src/components/prompts/run-prompt-button.tsx:66-77](). Media-specific platforms (image, video) are also dynamically included based on the `promptType` prop [src/components/prompts/run-prompt-button.tsx:188-190]().

Sources: [src/components/prompts/run-prompt-button.tsx:1-431]()

---

## Component Integration & Data Flow

`RunPromptButton` integrates with higher-level content viewers and cards to execute prompts.

```mermaid
graph LR
    InteractivePromptContent["InteractivePromptContent<br/>[src/components/prompts/interactive-prompt-content.tsx]"]
    RunPromptButton["RunPromptButton<br/>[src/components/prompts/run-prompt-button.tsx]"]
    PromptCard["PromptCard<br/>[src/components/prompts/prompt-card.tsx]"]

    PromptCard -- "renders" --> RunPromptButton
    InteractivePromptContent -- "renders" --> RunPromptButton

    subgraph "RunPromptButton Internal Logic"
        A[Check for variables] --> B{Variables present?}
        B -- Yes --> C[Open variable dialog]
        C --> D[User fills variables]
        D --> E[Get final content]
        B -- No --> E
        E --> F[Build platform URL]
        F --> G[Execute (open URL / copy)]
    end

    RunPromptButton -- "passes content, variables, callbacks" --> A
```

Sources: [src/components/prompts/interactive-prompt-content.tsx:10-170](), [src/components/prompts/run-prompt-button.tsx:1-431](), [src/components/prompts/prompt-card.tsx:15-178]()

---

# Summary

The prompt execution system unifies cross-platform deep linking, interactive variable filling, and responsive UI components into a cohesive workflow. Through `buildUrl()` and `RunPromptButton`, users can effortlessly transition prompts from the web repository into active IDE sessions or AI assistants.

---

# References

- RunPromptButton component: [src/components/prompts/run-prompt-button.tsx:1-431]()
- CLI platform utilities: [packages/prompts.chat/src/cli/platforms.ts:1-134]()
- Interactive Prompt Content: [src/components/prompts/interactive-prompt-content.tsx:43-218]()
- Prompt Card execution bindings: [src/components/prompts/prompt-card.tsx:15-178]()
- Raycast extension utilities: [packages/raycast-extension/src/utils.ts:1-270]()
- Platform URL tests: [packages/prompts.chat/__tests__/platforms.test.ts:1-22]()

---

# Page: Versioning & Change Requests

# Versioning & Change Requests

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/api/prompts/[id]/changes/[changeId]/route.ts](src/app/api/prompts/[id]/changes/[changeId]/route.ts)
- [src/app/api/prompts/[id]/changes/route.ts](src/app/api/prompts/[id]/changes/route.ts)

</details>



## Purpose and Scope

This document details the implementation of prompt versioning and the change request workflow in `prompts.chat`. It describes how `PromptVersion` records track the evolution of prompt content, and how community-driven `ChangeRequest` records allow users to propose edits subject to prompt owner review and approval. The page covers relevant Prisma models (`db.PromptVersion`, `db.ChangeRequest`), API routes (`/api/prompts/[id]/versions`, `/api/prompts/[id]/changes`, `/api/prompts/[id]/changes/[changeId]`), approval/rejection flows, and the user interface components that facilitate version management and comparison.

For related functionality, see the [Prompt CRUD Operations](4.1) page for prompt creation and editing, and [Workflow Chains & Connected Prompts](4.7) for prompt relationship management.

Sources: [prisma/schema.prisma:11-183](), [src/app/api/prompts/[id]/changes/route.ts:13-169](), [src/app/api/prompts/[id]/changes/[changeId]/route.ts:10-185]()

---

## System Overview & Architecture Mapping

The prompt versioning and change request subsystems bridge user intent expressed in natural language into structured database updates and server API interactions via Prisma ORM (`db`).

| System | Purpose | User Action | Code Entity / Route | Result |
|---|---|---|---|---|
| **Versioning** | Track prompt evolution | Prompt owner/admin edits | `POST /api/prompts/[id]/versions` [src/app/api/prompts/[id]/versions/route.ts:13-110]() | New `db.promptVersion` created, version incremented |
| **Change Requests** | Enable community prompt edits | Non-owner proposes change | `POST /api/prompts/[id]/changes` [src/app/api/prompts/[id]/changes/route.ts:18-168]() | `db.changeRequest` saved for review |
| | Review & approve/reject changes | Prompt owner reviews | `PATCH /api/prompts/[id]/changes/[changeId]` [src/app/api/prompts/[id]/changes/[changeId]/route.ts:15-185]() | Request marked approved/rejected, prompt updated |

### Code Entities and Their Relationships (Natural Language to Code Space)

Title: "Prisma Schema Model Relationships for Versioning and Change Requests"
```mermaid
erDiagram
    Prompt ||--o{ PromptVersion : "versions"
    Prompt ||--o{ ChangeRequest : "changeRequests"
    User ||--o{ PromptVersion : "createdBy"
    User ||--o{ ChangeRequest : "author"
    User ||--o{ Prompt : "author"
    User }o--o{ Prompt : "contributors"

    Prompt {
        String id PK "Prompt unique ID"
        String title
        String content
        String authorId FK
        PromptType type "BOT|CLASSIFIER|etc."
        Json bot "Bot configuration (for BOT type)"
        Json classifierConfig "Classifier configuration (for CLASSIFIER type)"
    }
    PromptVersion {
        String id PK "Version unique ID"
        String promptId FK
        Int version "Version number"
        String content
        String changeNote
        String createdBy FK
        Json botSnapshot "Bot configuration snapshot"
        Json classifierSnapshot "Classifier configuration snapshot"
    }
    ChangeRequest {
        String id PK "Change request ID"
        String promptId FK
        String authorId FK
        String proposedContent
        String proposedTitle
        ChangeRequestStatus status "PENDING|APPROVED|REJECTED"
        String reviewNote
        Json originalBot "Original bot config"
        Json proposedBot "Proposed bot config"
        Json originalClassifier "Original classifier config"
        Json proposedClassifier "Proposed classifier config"
    }
    User {
        String id PK "User ID"
        String username
    }
```
Sources: [prisma/schema.prisma:11-183]()

---

## Data Models Detail

### PromptVersion

The `PromptVersion` Prisma model stores historical snapshots of a prompt’s content, allowing retrieval of past versions and audit trails:

- `version`: sequential integer, incremented on every version creation [prisma/schema.prisma:1-157]().
- `content`: full prompt text at this version [prisma/schema.prisma:1-157]().
- `changeNote`: an optional note describing the change [prisma/schema.prisma:1-157]().
- `createdBy`: foreign key linking to the user who created this version [prisma/schema.prisma:1-157]().
- `botSnapshot`: JSON snapshot of bot-specific fields for `BOT` type prompts [prisma/schema.prisma:1-157]().
- `classifierSnapshot`: JSON snapshot of classifier-specific fields for `CLASSIFIER` type prompts [prisma/schema.prisma:1-157]().

Sources: [prisma/schema.prisma:1-157]()

### ChangeRequest

Community members can submit `ChangeRequest` entities to propose edits to a prompt they do not own:

- `status`: one of `PENDING`, `APPROVED`, or `REJECTED` [prisma/schema.prisma:1-157]().
- `proposedContent` and optional `proposedTitle`: the suggested edits [src/app/api/prompts/[id]/changes/route.ts:18-27]().
- `reason`: optional message explaining the change [src/app/api/prompts/[id]/changes/route.ts:18-27]().
- `reviewNote`: owner’s response note upon review [src/app/api/prompts/[id]/changes/[changeId]/route.ts:10-13]().
- The original prompt content/title snapshot (`originalContent`, `originalTitle`) to support differential review [src/app/api/prompts/[id]/changes/route.ts:150-153]().
- `originalBot` and `proposedBot`: JSON fields for bot-specific changes [src/app/api/prompts/[id]/changes/route.ts:159-162]().
- `originalClassifier` and `proposedClassifier`: JSON fields for classifier-specific changes [src/app/api/prompts/[id]/changes/route.ts:163-166]().
- Linked to both `Prompt` and `User` (author of the change request) [prisma/schema.prisma:1-157]().

Sources: [prisma/schema.prisma:1-157](), [src/app/api/prompts/[id]/changes/route.ts:18-168](), [src/app/api/prompts/[id]/changes/[changeId]/route.ts:10-13]()

---

## Version Management System

### Version Creation Workflow (API & DB)

Versions can be created explicitly by prompt owners or admins using the endpoint:
`POST /api/prompts/[id]/versions` [src/app/api/prompts/[id]/versions/route.ts:13-110]()

The workflow includes:

1. **Authentication & Authorization:**
   Validate user session via `auth()` and confirm user owns the prompt before allowing version creation [src/app/api/prompts/[id]/versions/route.ts:18-46]().

2. **Fetch Latest Version Number:**
   Query `db.promptVersion` records for the prompt, retrieve max version [src/app/api/prompts/[id]/versions/route.ts:69-75]().

3. **Transactionally Create New Version and Update Prompt:**
   Use a Prisma transaction (`db.$transaction`) to guarantee atomic creation of the version and update of the prompt's `content` [src/app/api/prompts/[id]/versions/route.ts:78-100](). For `BOT` and `CLASSIFIER` prompt types, `botSnapshot` or `classifierSnapshot` are also created using `versionBotSnapshot` [src/lib/bots/change-snapshot:6-6]() or `versionClassifierSnapshot` [src/lib/classifiers/change-snapshot:7-7]() respectively.

4. **Return Created Version:**
   API returns the new `PromptVersion` record including author information [src/app/api/prompts/[id]/versions/route.ts:102]().

Title: "Sequence Diagram for Version Creation (`POST /api/prompts/[id]/versions`)"
```mermaid
sequenceDiagram
    participant ClientUI as "Client UI"
    participant PostRoute as "POST /api/prompts/[id]/versions"
    participant AuthLib as "auth()"
    participant PrismaDB as "db (Prisma Client)"
    participant BotSnapshot as "versionBotSnapshot()"
    participant ClassifierSnapshot as "versionClassifierSnapshot()"

    ClientUI->>PostRoute: "Request to add new version (content, changeNote, optional bot/classifier fields)"
    PostRoute->>AuthLib: "Authenticate user session"
    AuthLib-->>PostRoute: "Session info"
    PostRoute->>PrismaDB: "db.prompt.findUnique(promptId)"
    PrismaDB-->>PostRoute: "Ownership validated, prompt type"
    PostRoute->>PrismaDB: "db.promptVersion.findFirst()"
    PrismaDB-->>PostRoute: "Latest version number"
    alt If prompt type is BOT
        PostRoute->>BotSnapshot: "Generate botSnapshot"
    end
    alt If prompt type is CLASSIFIER
        PostRoute->>ClassifierSnapshot: "Generate classifierSnapshot"
    end
    PostRoute->>PrismaDB: "db.$transaction([db.promptVersion.create, db.prompt.update])"
    PrismaDB-->>PostRoute: "Commit results"
    PostRoute-->>ClientUI: "Return new PromptVersion (201 Created)"
```
Sources: [src/app/api/prompts/[id]/versions/route.ts:13-110](), [prisma/schema.prisma:11-183](), [src/lib/bots/change-snapshot:6-6](), [src/lib/classifiers/change-snapshot:7-7]()

---

## Change Request Workflow

### Change Request Submission

Users who are **not** the prompt owner can submit a change request for public prompts via:

`POST /api/prompts/[id]/changes` [src/app/api/prompts/[id]/changes/route.ts:29-169]()

- Validations prevent owners from requesting changes on their own prompts [src/app/api/prompts/[id]/changes/route.ts:57-63]().
- Private prompts do not allow change requests [src/app/api/prompts/[id]/changes/route.ts:65-71]().
- The request must include at minimum proposed content, and optionally proposed title and reason [src/app/api/prompts/[id]/changes/route.ts:18-27]().
- For `BOT` prompts, `proposedBot` fields can be included and are validated using `botFieldsInputSchema` [src/app/api/prompts/[id]/changes/route.ts:23-24]() and parsed via `botFieldsFromInput` [src/app/api/prompts/[id]/changes/route.ts:140-140]().
- For `CLASSIFIER` prompts, `proposedClassifier` fields can be included and are validated using `classifierFieldsInputSchema` [src/app/api/prompts/[id]/changes/route.ts:25-26](). The `proposedContent` for classifiers is derived from these fields using `classifierContent` [src/app/api/prompts/[id]/changes/route.ts:122-122]() after validation with `checkClassifierWrite` [src/app/api/prompts/[id]/changes/route.ts:112-112]().
- A new `db.changeRequest` is created linking to the prompt and user, storing the initial content snapshot for contextual comparison [src/app/api/prompts/[id]/changes/route.ts:150-168]().

Sources: [src/app/api/prompts/[id]/changes/route.ts:29-169]()

### Owner Review and Approval/Rejection

The prompt owner reviews change requests and updates their status via:

`PATCH /api/prompts/[id]/changes/[changeId]` [src/app/api/prompts/[id]/changes/[changeId]/route.ts:15-185]()

- Only the prompt’s owner can perform review actions [src/app/api/prompts/[id]/changes/[changeId]/route.ts:43-48]().
- Valid transitions:
  - From `PENDING` to `APPROVED` or `REJECTED` [src/app/api/prompts/[id]/changes/[changeId]/route.ts:88-94]().
  - From `REJECTED` to `PENDING` (reopening) [src/app/api/prompts/[id]/changes/[changeId]/route.ts:103-109]().
- Approving triggers a transaction (`db.$transaction`) that:
  - Creates a new `db.promptVersion` with the approved content [src/app/api/prompts/[id]/changes/[changeId]/route.ts:163-175](). For `BOT` prompts, `botSnapshot` is created using `versionBotSnapshot` [src/app/api/prompts/[id]/changes/[changeId]/route.ts:172-172](). For `CLASSIFIER` prompts, `classifierSnapshot` is created using `versionClassifierSnapshot` [src/app/api/prompts/[id]/changes/[changeId]/route.ts:173-173]().
  - Updates the prompt’s `content` and optionally `title` [src/app/api/prompts/[id]/changes/[changeId]/route.ts:176-181]().
  - Adds the change request author as a contributor [src/app/api/prompts/[id]/changes/[changeId]/route.ts:182-182]().
  - Marks the change request status as `APPROVED` [src/app/api/prompts/[id]/changes/[changeId]/route.ts:183-185]().
- Rejecting updates the `db.changeRequest` status to `REJECTED` and optionally passes a review note [src/app/api/prompts/[id]/changes/[changeId]/route.ts:112-117]().

Sources: [src/app/api/prompts/[id]/changes/[changeId]/route.ts:15-185]()

Title: "Flowchart for Change Request Approval and Rejection Logic"
```mermaid
flowchart TD
    Review["Owner reviews ChangeRequest"] --> Decision{"Status change?"}
    Decision -- "APPROVED" --> TxStart["db.$transaction Start"]
    TxStart --> GetLatestVersion["Get latest prompt version number"]
    TxStart --> BuildChangeNote["Build change note with contributor info"]
    TxStart --> ProcessBotClassifier["Process proposed bot/classifier fields"]
    ProcessBotClassifier -- "If CLASSIFIER" --> ValidateClassifier["checkClassifierWrite() & classifierContent()"]
    ValidateClassifier -- "Valid" --> CreateVersion["db.promptVersion.create with proposedContent, botSnapshot, classifierSnapshot"]
    CreateVersion --> UpdatePrompt["db.prompt.update content, title, add contributor"]
    UpdatePrompt --> UpdateCRStatusApproved["db.changeRequest.update status = APPROVED"]
    UpdateCRStatusApproved --> TxEnd["db.$transaction Commit"]
    TxEnd --> Done["Response: success"]

    Decision -- "REJECTED" --> UpdateCRRejected["db.changeRequest.update status = REJECTED, save reviewNote"]
    UpdateCRRejected --> Done
    Decision -- "PENDING" --> Reopen["Reopen rejected ChangeRequest (db.changeRequest.update status = PENDING)"]
    Reopen --> Done
    ValidateClassifier -- "Invalid" --> Error["Response: error (400/409)"]
```
Sources: [src/app/api/prompts/[id]/changes/[changeId]/route.ts:15-185]()

---

## Privacy and Security Considerations

- Access control is strictly enforced using authorization checks (`checkPromptAccess`) [src/lib/prompt-access.ts:1-49]():
  - Only owners or admins can view private prompts, their versions, or change requests [src/lib/prompt-access.ts:1-49]().
  - Unauthorized requests to private prompt endpoints return `404 Not Found` or `401 Unauthorized` to prevent prompt existence disclosure.

Sources: [src/lib/prompt-access.ts:1-49]()

---

## UI Components for Versioning & Change Requests

The following React components power the prompt page versioning and change request UI features, exposed primarily on `/prompts/[id]` [src/app/prompts/[id]/page.tsx:1-50]():

| Component | File Path | Description |
|---|---|---|
| `AddVersionForm` | `src/components/prompts/add-version-form` | Form for owners to manually add a new version with a change note |
| `DeleteVersionButton` | `src/components/prompts/delete-version-button` | Button to delete older versions (history pruning) |
| `VersionCompareButton` | `src/components/prompts/version-compare-button` | Triggers modal to compare two versions side-by-side |
| `VersionCompareModal` | `src/components/prompts/version-compare-modal` | Modal showing side-by-side version diff |

Sources: [src/app/prompts/[id]/page.tsx:1-50]()

---

## Summary Diagram: From User Action to Code Entities

Title: "Architecture Flow from User Actions to Route Handlers and Prisma Models"
```mermaid
flowchart TD
    UserAction["User (Owner or Contributor)"]

    UserAction -- "Submit Change Request (proposedContent, proposedTitle, proposedBot, proposedClassifier, reason)" --> ChangesPOST["POST /api/prompts/[id]/changes"]
    ChangesPOST --> ValidateInput["Validate input (zod schemas)"]
    ChangesPOST -- "If CLASSIFIER" --> CheckClassifierWrite["checkClassifierWrite() & classifierContent()"]
    ChangesPOST --> DB_CR["db.changeRequest.create()"]
    DB_CR -- "Stores original/proposed content, title, bot, classifier" --> PrismaClient

    UserAction -- "Review & Approve/Reject (status, reviewNote)" --> ChangesPatch["PATCH /api/prompts/[id]/changes/[changeId]"]
    ChangesPatch --> AuthCheckOwner["Auth: Check prompt owner"]
    ChangesPatch --> ValidateStatusTransition["Validate status transition"]
    ChangesPatch -- "If APPROVED" --> GetLatestVersion["Get latest prompt version"]
    ChangesPatch -- "If APPROVED" --> ProcessBotClassifierApproval["Process proposed bot/classifier for snapshot"]
    ChangesPatch -- "If APPROVED" --> DB_Transaction["db.$transaction"]
    DB_Transaction --> DB_PVersion["db.promptVersion.create()"]
    DB_Transaction --> DB_Prompt["db.prompt.update(content, title, contributors)"]
    DB_Transaction --> DB_CR_Update["db.changeRequest.update(status=APPROVED)"]
    DB_Transaction --> PrismaClient

    ChangesPatch -- "If REJECTED/PENDING" --> DB_CR_Update_Simple["db.changeRequest.update(status, reviewNote)"]
    DB_CR_Update_Simple --> PrismaClient

    UserAction -- "Create Version (owner/admin) (content, changeNote, optional bot/classifier fields)" --> VersionsPOST["POST /api/prompts/[id]/versions"]
    VersionsPOST --> AuthCheckOwner["Auth: Check prompt owner"]
    VersionsPOST --> GetLatestVersion["Get latest prompt version"]
    VersionsPOST --> ProcessBotClassifierVersion["Process bot/classifier for snapshot"]
    VersionsPOST --> DB_Transaction_Version["db.$transaction"]
    DB_Transaction_Version --> DB_PVersion["db.promptVersion.create()"]
    DB_Transaction_Version --> DB_Prompt["db.prompt.update(content, title)"]
    DB_Transaction_Version --> PrismaClient

    AuthCheckOwner -- "Auth check" --> AuthLib["auth()"]
    ValidateInput -- "Validation" --> ZodLib["zod"]
    CheckClassifierWrite -- "Classifier logic" --> ClassifierLib["src/lib/classifiers/write"]
    ProcessBotClassifierApproval -- "Bot/Classifier logic" --> BotClassifierLib["src/lib/bots/change-snapshot"]
    ProcessBotClassifierVersion -- "Bot/Classifier logic" --> BotClassifierLib
```
Sources: [src/app/api/prompts/[id]/changes/route.ts:29-169](), [src/app/api/prompts/[id]/changes/[changeId]/route.ts:15-185](), [src/app/api/prompts/[id]/versions/route.ts:13-110](), [prisma/schema.prisma:11-183](), [src/lib/bots/change-snapshot:1-10](), [src/lib/classifiers/change-snapshot:1-15](), [src/lib/classifiers/write:1-20]()

---

## References

- Prisma schema models: [prisma/schema.prisma:11-183]()
- Prompt version API: [src/app/api/prompts/[id]/versions/route.ts:13-110]()
- Change request API:
  - Create & list: [src/app/api/prompts/[id]/changes/route.ts:29-169]()
  - Review & update: [src/app/api/prompts/[id]/changes/[changeId]/route.ts:15-185]()
- Prompt page UI with versioning components: [src/app/prompts/[id]/page.tsx:1-50]()
- Prompt privacy check: [src/lib/prompt-access.ts:1-49]()
- Bot change snapshot utilities: [src/lib/bots/change-snapshot:1-10]()
- Classifier change snapshot utilities: [src/lib/classifiers/change-snapshot:1-15]()
- Classifier write validation: [src/lib/classifiers/write:1-20]()

---

# Page: AI-Powered Features

# AI-Powered Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [prisma/migrations/20251217173000_add_delist_reason/migration.sql](prisma/migrations/20251217173000_add_delist_reason/migration.sql)
- [src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml](src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml)
- [src/app/api/prompt-builder/chat/route.ts](src/app/api/prompt-builder/chat/route.ts)
- [src/lib/ai/embeddings.ts](src/lib/ai/embeddings.ts)
- [src/lib/ai/load-prompt.ts](src/lib/ai/load-prompt.ts)
- [src/lib/ai/quality-check.prompt.yml](src/lib/ai/quality-check.prompt.yml)
- [src/lib/ai/quality-check.ts](src/lib/ai/quality-check.ts)
- [src/lib/ai/query-translator.prompt.yml](src/lib/ai/query-translator.prompt.yml)
- [src/lib/ai/sql-generation.prompt.yml](src/lib/ai/sql-generation.prompt.yml)
- [src/lib/ai/translate.prompt.yml](src/lib/ai/translate.prompt.yml)

</details>



This page explains the AI-powered capabilities that enhance prompt discovery, quality control, content generation, and expert prompt engineering in prompts.chat. These features leverage OpenAI's APIs and specialized YAML-defined prompts (`.prompt.yml` files) to provide semantic search, automated quality checking, translation, and agentic prompt construction.

Sources: [src/lib/ai/embeddings.ts:1-233](), [src/lib/ai/quality-check.ts:1-173](), [src/lib/ai/load-prompt.ts:1-44]()

---

## Overview of AI Features

The platform integrates several AI-driven features powered by OpenAI models (typically `gpt-4o`, `gpt-4o-mini`, and `text-embedding-3-small`):

| Feature | Purpose | Trigger | Key Code Entity |
|---|---|---|---|
| **Embeddings Generation** | Enable semantic search | Prompt creation or update | `generatePromptEmbedding` [src/lib/ai/embeddings.ts:81-109]() |
| **Quality Check** | Auto-delist low-quality prompts | Prompt creation or update | `checkPromptQuality` [src/lib/ai/quality-check.ts:72-164]() |
| **Semantic Search** | Find prompts by semantic meaning | Search with query input | `semanticSearch` [src/lib/ai/embeddings.ts:214-233]() |
| **Prompt Builder Agent** | Expert agent for prompt creation and edits | Prompt Builder UI | `prompt-builder-agent.prompt.yml` [src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml:1-131]() |
| **Query Translation** | Translate non-English search queries | Semantic search query input | `translateQueryToEnglish` [src/lib/ai/embeddings.ts:32-60]() |
| **SQL Generation** | Generate SQL queries for HF dataset viewing | HF dataset explorer UI | `sql-generation.prompt.yml` [src/lib/ai/sql-generation.prompt.yml:1-35]() |

These features improve prompt discoverability, quality assurance, multilingual support, and prompt authoring workflow with tight integration between AI models and the platform’s data.

Sources: [src/lib/ai/embeddings.ts:1-233](), [src/lib/ai/quality-check.ts:1-173](), [src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml:1-131](), [src/lib/ai/sql-generation.prompt.yml:1-35]()

---

## AI Features Architecture

This section bridges the **Natural Language Space** (user queries, intent, prompt text) to the **Code Entity Space** (functions, API routes, database models), illustrating the data flow and key components.

### AI Processing Data Flow

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        UserQuery["User Search Query / Intent"]
        PromptIdea["Prompt Authoring Text"]
    end

    subgraph "CodeEntitySpace"
        UI_Builder["PromptBuilderComponent<br/>src/components/prompts/prompt-builder.tsx"]
        POST_PB_Chat["POST /api/prompt-builder/chat<br/>src/app/api/prompt-builder/chat/route.ts"]
        POST_P["Prompt CRUD APIs<br/>src/app/api/prompts"]
        QC["checkPromptQuality()<br/>src/lib/ai/quality-check.ts"]
        EMB["generatePromptEmbedding()<br/>src/lib/ai/embeddings.ts"]
        SS["semanticSearch()<br/>src/lib/ai/embeddings.ts"]
        LP["loadPrompt()<br/>src/lib/ai/load-prompt.ts"]
        QT["translateQueryToEnglish()<br/>src/lib/ai/embeddings.ts"]
    end

    subgraph "ExternalAIServices"
        OpenAI_Embed["OpenAI Embedding API<br/>text-embedding-3-small"]
        OpenAI_Translate["OpenAI Translation API<br/>gpt-4o-mini"]
        OpenAI_Generative["OpenAI Generative API<br/>gpt-4o / gpt-4o-mini"]
    end

    subgraph "DatabaseSpace"
        P_Model["PromptModel (Prisma)"]
        P_Embed["Prompt.embedding JSON Vector"]
        P_Delist["Prompt.delistReason Enum"]
    end

    UserQuery --> SS
    PromptIdea --> POST_P
    PromptIdea --> UI_Builder

    UI_Builder --> POST_PB_Chat
    POST_PB_Chat --> LP
    POST_PB_Chat --> SS
    POST_PB_Chat --> OpenAI_Generative

    POST_P --> QC
    POST_P --> EMB

    QC -->|IfLowQuality| P_Delist
    EMB --> OpenAI_Embed
    OpenAI_Embed --> P_Embed

    SS --> QT
    QT --> OpenAI_Translate
    OpenAI_Translate --> QT
    SS --> OpenAI_Embed
    OpenAI_Embed --> SS
    SS --> P_Embed
```

Sources: [src/lib/ai/embeddings.ts:70-233](), [src/lib/ai/quality-check.ts:72-164](), [src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml:1-131](), [src/lib/ai/load-prompt.ts:30-44]()

---

## Embeddings & Semantic Search

### Embeddings Generation

When a public prompt is created or updated, the system generates a vector embedding representing its semantic content. The process is:

1.  **Concatenation** — The prompt’s `title`, `description`, and `content` fields are combined with newlines into a single text blob [src/lib/ai/embeddings.ts:96-101]().
2.  **Embedding API Call** — The combined text is sent to OpenAI's embedding generation API (`text-embedding-3-small` or configured model) using `generateEmbedding(text)` [src/lib/ai/embeddings.ts:70-79]().
3.  **Database Storage** — The resulting embedding vector (array of floats) is saved in the prompt’s `embedding` field in the Prisma `Prompt` model [src/lib/ai/embeddings.ts:104-108]().
4.  **Bulk Regeneration** — The `generateAllEmbeddings` function iterates over all non-private prompts lacking embeddings and generates them with 1-second rate limiting to avoid API throttling [src/lib/ai/embeddings.ts:115-160]().

Sources: [src/lib/ai/embeddings.ts:70-160]()

### Semantic Search Execution

The `semanticSearch` function enables searching using natural language queries as follows:

-   **Non-English Query Translation**: Queries containing non-ASCII (non-English) characters are translated into English keywords using the `translateQueryToEnglish` function, which employs a dedicated `query-translator.prompt.yml` system prompt and a cheap generative model [src/lib/ai/embeddings.ts:32-60]().
-   **Query Embedding**: The translated (or original) query is embedded using the same embedding model.
-   **Prompt Retrieval**: All public prompts with valid embeddings are fetched from the database.
-   **Similarity Scoring**: Cosine similarity between the query embedding and each prompt's embedding is computed to rank relevance [src/lib/ai/embeddings.ts:162-174]().
-   **Result Return**: The top results are returned as a rich `SemanticSearchResult` object with prompt metadata [src/lib/ai/embeddings.ts:176-208]().

#### Semantic Search Flow Diagram

```mermaid
sequenceDiagram
    participant User as "User Natural Language Input"
    participant SearchUI as "Search UI Component"
    participant EmbLib as "semanticSearch() / generateEmbedding()<br/>src/lib/ai/embeddings.ts"
    participant TransLib as "translateQueryToEnglish()<br/>src/lib/ai/embeddings.ts"
    participant OpenAI as "OpenAI API Client"
    participant DB as "Prisma DB prompt model"

    User->>SearchUI: "Enter search query (may be non-English)"
    SearchUI->>EmbLib: "semanticSearch(query)"
    EmbLib->>EmbLib: "containsNonEnglish(query)?"
    alt Non-English detected
        EmbLib->>TransLib: "translateQueryToEnglish(query)"
        TransLib->>OpenAI: "chat.completions with query-translator.prompt.yml"
        OpenAI-->>TransLib: "English keywords"
        TransLib-->>EmbLib: "translated query"
    else
        EmbLib-->>EmbLib: "use original query"
    end
    EmbLib->>OpenAI: "embeddings.create(searchQuery)"
    OpenAI-->>EmbLib: "query vector"
    EmbLib->>DB: "prompt.findMany(public, has embedding)"
    DB-->>EmbLib: "list of prompts with embeddings"
    EmbLib->>EmbLib: "cosineSimilarity(query vector, prompt vectors)"
    EmbLib-->>SearchUI: "ranked SemanticSearchResult[]"
```

Sources: [src/lib/ai/embeddings.ts:32-233](), [src/lib/ai/query-translator.prompt.yml:1-22]()

---

## Quality Check System

To maintain prompt quality standards, prompts undergo an automated quality checking pipeline using both heuristic and AI methods:

### Automated Delisting Pipeline

Prompts are checked on creation or update through `checkPromptQuality` which performs:

1.  **Length Heuristics**: Basic length requirements enforce a minimum of 50 characters and 10 words in the prompt content [src/lib/ai/quality-check.ts:43-66]().
2.  **AI-Powered Quality Validation**: If heuristic checks pass, an AI call is made to OpenAI's `gpt-4o` model leveraging the `quality-check.prompt.yml` system prompt to assess:
    -   Whether the prompt is in English
    -   If the prompt is high quality (not gibberish)
    -   Whether the prompt is a valid instruction for generative AI
3.  **Delist Decision**: The AI returns a JSON indicating if the prompt should be delisted, reason codes, confidence, and details. Only results with confidence ≥ 0.85 result in delisting [src/lib/ai/quality-check.ts:72-164]().

### Delist Reasons Enum

The system uses the following delist reasons matching the Prisma schema enum added in migration `20251217173000_add_delist_reason`:

| Reason | Description |
|---|---|
| `TOO_SHORT` | Content too brief or has insufficient words |
| `NOT_ENGLISH` | Prompt is primarily non-English |
| `LOW_QUALITY` | Gibberish, random characters, or meaningless text |
| `NOT_LLM_INSTRUCTION` | Not an AI generative prompt (ex: recipe, note) |
| `MANUAL` | Manual delisting by admins |

Sources: [src/lib/ai/quality-check.ts:1-173](), [src/lib/ai/quality-check.prompt.yml:1-62](), [prisma/migrations/20251217173000_add_delist_reason/migration.sql:1-5]()

---

## Prompt Builder Agent & `.prompt.yml` Files

The platform features an AI expert agent to assist in writing new prompts or editing existing ones with stylistic consistency.

### Prompt Builder Agent

-   The agent is configured in the `src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml` file.
-   It instructs the AI to first search existing prompts for relevant examples before constructing new prompts, emphasizing structure, quality, and reuse of variables [src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml:11-13]().
-   The agent supports workflows for building new prompts, editing content, and converting prompts into structured JSON formats to support advanced prompt types and multi-file skills [src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml:21-67]().
-   The agent API route at `POST /api/prompt-builder/chat` implements session validation, rate limiting, and streams responses progressively to clients [src/app/api/prompt-builder/chat/route.ts:64-191]().

Sources: [src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml:1-131](), [src/app/api/prompt-builder/chat/route.ts:64-191]()

### `.prompt.yml` Prompt Definition Format

All AI-powered workflows in the system load their core prompt configurations from `.prompt.yml` files using the `loadPrompt` function [src/lib/ai/load-prompt.ts:30-44]().

A prompt YAML file includes:

-   `name` and `description` metadata [src/lib/ai/load-prompt.ts:14-15]()
-   The OpenAI model name (`model`) and parameters (temperature, maxTokens) [src/lib/ai/load-prompt.ts:16-20]()
-   A list of chat `messages` with roles `system`, `user`, or `assistant` [src/lib/ai/load-prompt.ts:21]()
-   Optional `testData` for automated testing [src/lib/ai/load-prompt.ts:22]()

Example:

```yaml
name: Prompt Builder Agent
description: An expert prompt engineer agent...
model: openai/gpt-4o-mini
modelParameters:
  temperature: 0.7
  maxTokens: 2000
messages:
  - role: system
    content: |
      You are an expert prompt engineer agent...
```

The system interpolates variables in prompt templates using `interpolatePrompt` for dynamic content insertion [src/lib/ai/load-prompt.ts:62-71]().

Sources: [src/lib/ai/load-prompt.ts:1-71]()

---

## Content Translation & SQL Generation

### Content Translation

To support multilingual users, the platform can utilize the `translate.prompt.yml` prompt to translate prompt contents or queries into target languages while preserving formatting and variable placeholders. Typical usage scenarios:

-   Translating interface or prompt content (`${variable}` placeholders are conserved with translated default values)
-   Translation calls employ OpenAI `gpt-4o-mini` with a system prompt instructing professional fidelity and formatting retention [src/lib/ai/translate.prompt.yml:1-27]().

Sources: [src/lib/ai/translate.prompt.yml:1-27]()

### SQL Generation for Dataset Exploration

For advanced exploration of the prompts dataset on Hugging Face, a dedicated prompt `sql-generation.prompt.yml` guides the construction of efficient DuckDB SQL queries based on user natural language inputs:

-   It defines rules to generate SQL selecting prompt acts and content matching keywords [src/lib/ai/sql-generation.prompt.yml:11-22]().
-   The prompt instructs the AI to produce concise SQL without explanations [src/lib/ai/sql-generation.prompt.yml:14]().
-   Example outputs translate user intents like `"Find prompts about coding"` into appropriate SQL filtering queries [src/lib/ai/sql-generation.prompt.yml:27-35]().

Sources: [src/lib/ai/sql-generation.prompt.yml:1-35]()

---

# Summary

prompts.chat seamlessly integrates OpenAI services for embeddings, semantic search, translation, quality checks, and prompt authoring assistance, all orchestrated through a configuration of `.prompt.yml` files and robust server-side APIs. This infrastructure enables scalable, high-quality prompt discovery and collaborative editing backed by sophisticated AI models and domain-specific prompt templates.

Sources:
[src/lib/ai/embeddings.ts:1-233](),
[src/lib/ai/quality-check.ts:1-173](),
[src/lib/ai/load-prompt.ts:1-71](),
[src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml:1-131](),
[src/lib/ai/translate.prompt.yml:1-27](),
[src/lib/ai/sql-generation.prompt.yml:1-35](),
[src/app/api/prompt-builder/chat/route.ts:1-191](),
[prisma/migrations/20251217173000_add_delist_reason/migration.sql:1-5]()

---

# Page: Workflow Chains & Connected Prompts

# Workflow Chains & Connected Prompts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/api/prompts/[id]/connections/[connectionId]/route.ts](src/app/api/prompts/[id]/connections/[connectionId]/route.ts)
- [src/app/api/prompts/[id]/connections/route.ts](src/app/api/prompts/[id]/connections/route.ts)
- [src/app/api/prompts/[id]/flow/route.ts](src/app/api/prompts/[id]/flow/route.ts)
- [src/components/prompts/prompt-connections.tsx](src/components/prompts/prompt-connections.tsx)

</details>



## Purpose and Scope

This document details the workflow chain system within `prompts.chat`. The system allows linking prompts via directed connections (`PromptConnection`) to compose multi-step pipelines where the output of one prompt feeds as input to another. These workflow graphs enable complex AI-assisted tasks, chaining modular prompt components seamlessly.

Key topics covered:
- `PromptConnection` model and `workflowLink` field usage
- BFS algorithm for propagating `workflowLink` changes across prompt components
- Differentiation between workflow and "related" connections
- API endpoints for managing connections
- D3-based `FlowGraph` visualization and UI components

Related topics:
- For AI similarity-based "related" prompts, see [AI-Powered Features]()
- For multi-file prompt packaging with skills, see [Skills & Multi-file Prompts]()
- For prompt CRUD and editing flows, see [Prompt CRUD Operations]()

Sources: [src/components/prompts/prompt-connections.tsx:1-213](), [prisma/schema.prisma:378-393]()

---

## PromptConnection Model

The graph topology for workflow chains is realized through the `PromptConnection` model. Each record represents a directed edge from a source prompt to a target prompt.

### Database Schema

Title: PromptConnection ER Diagram
```mermaid
erDiagram
    Prompt ||--o{ PromptConnection : "source"
    Prompt ||--o{ PromptConnection : "target"
    
    PromptConnection {
        string id PK
        string sourceId FK
        string targetId FK
        string label
        int order
        datetime createdAt
        datetime updatedAt
    }
    
    Prompt {
        string id PK
        string workflowLink
        json bestWithMCP
    }
```

- `sourceId` and `targetId` denote the connected prompt pair.
- `label` distinguishes the type of connection (e.g., workflow or related).
- `order` defines a user-controlled sequence to represent multiple outgoing edges.

Sources: [prisma/schema.prisma:378-393](), [prisma/schema.prisma:93-143]()

### Connection Types (`label` Field)

Two main semantic usages of the connection `label` field exist:

| Label Value | Role | Created By | Direction |
| --- | --- | --- | --- |
| `"related"` | AI-suggested similar prompts | Embeddings service | Bidirectional (conceptual) |
| Other string | Workflow chain step connections | User-created via UI/API | Directed (source→target) |

**Note:** The workflow graph endpoints and client components exclude `"related"` labeled connections when building execution pipelines.

**Implementation detail:** Queries filter via `{ label: { not: "related" } }` to focus on intended workflow links [src/app/api/prompts/[id]/connections/route.ts:33-49]().

Sources: [src/app/api/prompts/[id]/connections/route.ts:33-49]()

---

## Flow Start vs Intermediate Prompts

The system classifies prompts in a workflow based on their connection topology to control visibility and behavior.

### Logical Classification

Title: Prompt Workflow Classification Logic
```mermaid
graph TB
    subgraph "ClassificationLogic"
        P["Prompt"] --> CheckOut["outgoingConnections.count()"]
        P --> CheckIn["incomingConnections.count()"]
        
        CheckOut -->|"> 0"| HasOut["HasOutgoing"]
        CheckOut -->|"= 0"| NoOut["NoOutgoing"]
        CheckIn -->|"> 0"| HasIn["HasIncoming"]
        CheckIn -->|"= 0"| NoIn["NoIncoming"]
        
        HasOut --> NoIn
        NoIn --> FlowStart["FlowStartPrompt"]
        
        HasOut --> HasIn
        HasIn --> Intermediate["IntermediatePrompt"]
        
        NoOut --> NoIn
        NoIn --> Standalone["StandalonePrompt"]
    end
```

- **Flow Start Prompt:** Has outgoing connections but no incoming, shown in browsing lists as entry points.
- **Intermediate Prompt:** Has both incoming and outgoing connections, hidden from general lists to avoid clutter.
- **Standalone Prompt:** No connections at all, treated as independent prompts.

### Browsing Filter Example

Browsing APIs exclude intermediate flow prompts by filtering on lack of incoming workflow connections not labeled `"related"` [src/app/workflows/page.tsx:28-38]():

```typescript
where: {
  incomingConnections: { 
    none: { 
      label: { not: "related" } 
    } 
  }
}
```

Sources: [src/app/workflows/page.tsx:28-38]()

---

## Workflow Link Propagation

The `workflowLink` field on each prompt stores a URL or identifier related to the workflow execution environment. When this field is updated on a single prompt, the system propagates the change to all directly or indirectly connected prompts in the workflow, ensuring consistency.

### Propagation via BFS Algorithm

When a prompt's `workflowLink` is changed (via PATCH on `/api/prompts/:id`):

Title: Workflow Link Propagation Flow
```mermaid
graph TD
    Start["PATCH /api/prompts/:id"] --> Check["Is workflowLink changed?"]
    Check -->|No| Skip["Skip propagation"]
    Check -->|Yes| FetchAll["Fetch all PromptConnections"]
    FetchAll --> BuildGraph["Build undirected adjacency list"]
    BuildGraph --> BFS["Run BFS from updated prompt"]
    BFS --> Update["Batch update all connected prompt.workflowLink"]
    Update --> Revalidate["Revalidate cache tags"]
```

**Algorithm Steps:**
1. Query all workflow connections (excluding `"related"`) from `promptConnection` [src/app/api/prompts/[id]/route.ts:280-336]().
2. Build an undirected adjacency from `sourceId` and `targetId` pairs to allow traversal in both directions [src/app/api/prompts/[id]/route.ts:280-336]().
3. Initialize BFS with starting prompt ID, collecting all reachable prompt IDs [src/app/api/prompts/[id]/route.ts:280-336]().
4. Batch update all collected prompts to set their `workflowLink` to the new value [src/app/api/prompts/[id]/route.ts:280-336]().
5. Revalidate cache tags to refresh UI and flow data [src/app/api/prompts/[id]/route.ts:339-340]().

Sources: [src/app/api/prompts/[id]/route.ts:280-340]()

---

## UI Components and Data Flow

### PromptConnections Component

- File: `src/components/prompts/prompt-connections.tsx`
- Props include prompt ID, title, edit permissions, and optionally a `workflowLink` for live testing links [src/components/prompts/prompt-connections.tsx:38-48]().
- Loads and renders incoming and outgoing connections and the flow graph visualization.
- Allows users to add, edit, or delete connections with context-aware UI.
- Fetches connections from `/api/prompts/:id/connections` and flow graph data from `/api/prompts/:id/flow`.

### FlowGraph Visualization

- Implements a directed acyclic graph display using D3.js [src/components/prompts/prompt-connections.tsx:7-123]().
- Computes topological sorting and assigns vertical levels to prompts [src/components/prompts/prompt-connections.tsx:180-213]().
- Renders connections as curved cubic Bézier paths with arrow markers.
- Displays input/output virtual nodes for prompts requiring or producing media [src/components/prompts/prompt-connections.tsx:760-800]().
- Supports hover tooltips and click interactions to navigate to prompt detail pages [src/components/prompts/prompt-connections.tsx:150-176]().

#### FlowGraph Layout Pipeline

Title: FlowGraph Layout Pipeline
```mermaid
flowchart TD
    Input["nodes[] + edges[]"] --> Adjacency["Build inDegree map and outEdges adjacency"]
    Adjacency --> TopoSort["BFS topological sort assign level per node"]
    TopoSort --> LevelGroups["Group nodes by level"]
    LevelGroups --> VirtualNodes["Create input/output virtual nodes based on media"]
    VirtualNodes --> Positions["Compute x,y coordinates"]
    Positions --> DrawEdges["Draw cubic bezier edges with flow-arrow markers"]
    DrawEdges --> DrawNodes["Render nodes with badges and text"]
    DrawNodes --> Events["Add mouseenter/leave tooltip and click handlers"]
```

Sources: [src/components/prompts/prompt-connections.tsx:1-213]()

---

## API Endpoints for Connections

Below is the overview of key RESTful routes managing prompt connections:

Title: Connection REST Endpoints
```mermaid
graph LR
    subgraph "ConnectionRoutes"
        GET_CONN["GET /api/prompts/:id/connections"]
        POST_CONN["POST /api/prompts/:id/connections"]
        DEL_CONN["DELETE /api/prompts/:id/connections/:connectionId"]
        PATCH_CONN["PATCH /api/prompts/:id/connections/:connectionId"]
    end
    GET_CONN --> Shape1["Returns incoming/outgoing excluding label=related"]
    POST_CONN --> PromptConnection["Create new PromptConnection with ownership check"]
    DEL_CONN --> PromptConnection2["Delete PromptConnection with auth check"]
    PATCH_CONN --> PromptConnection3["Update PromptConnection label or order"]
```

### Detailed Routes

- **GET /api/prompts/:id/connections**  
  Retrieves incoming and outgoing connections for the prompt excluding `"related"`. Filters out private prompts the user cannot access [src/app/api/prompts/[id]/connections/route.ts:17-87]().

- **POST /api/prompts/:id/connections**  
  Creates a new prompt connection after verifying the user owns both source and target prompts. Prevents self-links and duplicates. Returns full created connection data [src/app/api/prompts/[id]/connections/route.ts:89-211]().

- **DELETE /api/prompts/:id/connections/:connectionId**  
  Deletes a connection if the user owns the source prompt or has admin role. Revalidates caches post deletion [src/app/api/prompts/[id]/connections/[connectionId]/route.ts:16-74]().

- **PATCH /api/prompts/:id/connections/:connectionId**  
  Allows updating the connection's `label` or `order` with ownership validation. Triggers cache revalidation [src/app/api/prompts/[id]/connections/[connectionId]/route.ts:76-149]().

Sources: [src/app/api/prompts/[id]/connections/route.ts:1-211](), [src/app/api/prompts/[id]/connections/[connectionId]/route.ts:1-149]()

---

## Flow Graph Endpoint and BFS for Connected Prompts

The flow visualization needs the full connected subgraph including prompts reachable by any workflow edge from the starting prompt.

### GET /api/prompts/[id]/flow Endpoint

- Utilizes a batch BFS traversal over prompt connections (excluding `"related"`) to collect all related prompt IDs [src/app/api/prompts/[id]/flow/route.ts:33-116]().
- Fetches all prompt details in one database query by gathering all connected prompt IDs [src/app/api/prompts/[id]/flow/route.ts:118-146]().
- Filters prompts by user permission (visibility) [src/app/api/prompts/[id]/flow/route.ts:176-210]().
- Returns JSON of nodes and edges for UI rendering [src/app/api/prompts/[id]/flow/route.ts:212-216]().

### BFS Algorithm in Flow Endpoint

Title: BFS Flow Graph Traversal
```mermaid
flowchart TD
    Init["Initialize allPromptIds and queue and visitedForEdges"] --> Loop["While queue not empty"]
    Loop --> Unvisited["Extract unvisited prompts from queue"]
    Unvisited --> BatchFetch["Batch fetch connections where label != 'related'"]
    BatchFetch --> ProcessOut["Add outgoing edges and targetIds"]
    ProcessOut --> ProcessIn["Add incoming edges and sourceIds"]
    ProcessIn --> Loop
    Loop --> Done["Query all prompt details in one batch query"]
    Done --> Response["Return filtered nodes and edges in JSON response"]
```

- Uses caching with Next.js `unstable_cache` keyed on `"prompt-flow"` tag, expiring after 60 seconds or when related data changes [src/app/api/prompts/[id]/flow/route.ts:33-150]().

Sources: [src/app/api/prompts/[id]/flow/route.ts:1-225]()

---

## Cache Invalidation

Any mutation to prompts or connections affecting workflows triggers invalidation of cached data to maintain synchronization:

```typescript
revalidateTag("prompts");      // General prompt catalog refresh
revalidateTag("prompt-flow");  // Workflow graph cache refresh
```

This occurs after creating, updating, or deleting connections and after changing a prompt's `workflowLink`.

Sources: [src/app/api/prompts/[id]/connections/route.ts:198](), [src/app/api/prompts/[id]/connections/[connectionId]/route.ts:64-136](), [src/app/api/prompts/[id]/route.ts:339-340]()

---

## Bridging Natural Language Space to Code Entities

### Workflow Chain Concept to Code Entities

Title: Workflow Chain to Code Entity Mapping
```mermaid
graph TD
    Natural_Lang[/"Workflow Chains and Connected Prompts"/] --> PromptConnection_DB["PromptConnection prisma/schema.prisma"]
    PromptConnection_DB --> API_Connections["api/prompts/[id]/connections src/app/api/prompts/[id]/connections/route.ts"]
    API_Connections --> UI_PromptConnections["PromptConnections src/components/prompts/prompt-connections.tsx"]
    UI_PromptConnections --> FlowGraph["FlowGraph D3 visualization"]
    API_Connections --> MutateEndpoints["Mutation Endpoints src/app/api/prompts/[id]/connections/[connectionId]/route.ts"]
    MutateEndpoints --> Cache_Invalidate["Cache Invalidation revalidateTag prompt-flow"]
```

Sources: [prisma/schema.prisma:378-393](), [src/app/api/prompts/[id]/connections/route.ts:1-211](), [src/components/prompts/prompt-connections.tsx:1-213]()

### Workflow Propagation Algorithm to Implementation

Title: Workflow Propagation Algorithm Mapping
```mermaid
graph TD
    Edit_Prompt["PATCH /api/prompts/[id] workflowLink update"] --> Route_Handler["Route Handler src/app/api/prompts/[id]/route.ts"]
    Route_Handler --> Fetch_Connections["db.promptConnection.findMany label != 'related'"]
    Fetch_Connections --> Build_Graph["Build undirected adjacency map"]
    Build_Graph --> Run_BFS["Run BFS traversal from updated prompt"]
    Run_BFS --> Batch_Update["db.prompt.updateMany called with collected IDs"]
    Batch_Update --> Cache_Invalidate["revalidateTag prompts and prompt-flow"]
```

Sources: [src/app/api/prompts/[id]/route.ts:280-340]()

---

## Summary

The workflow chains in `prompts.chat` implement a robust directed graph system using the `PromptConnection` model. The system distinguishes workflow connections from AI-suggested related prompts via the `label` field. The BFS propagation algorithm ensures atomic consistency of the `workflowLink` field across all connected prompts, facilitating smooth execution of multi-step AI workflows. Comprehensive APIs and React UI components including D3 visualizations provide management and exploration of these workflows in the app.

Sources: [src/components/prompts/prompt-connections.tsx:1-213](), [src/app/api/prompts/[id]/flow/route.ts:1-225](), [prisma/schema.prisma:378-393]()

---

# Page: Import & Export System

# Import & Export System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [PROMPTS.md](PROMPTS.md)
- [README.md](README.md)
- [next.config.ts](next.config.ts)
- [prompts.csv](prompts.csv)
- [scripts/generate-contributors.sh](scripts/generate-contributors.sh)
- [scripts/rebuild-history.sh](scripts/rebuild-history.sh)
- [src/app/prompts.csv/route.ts](src/app/prompts.csv/route.ts)
- [src/app/prompts.json/route.ts](src/app/prompts.json/route.ts)
- [src/components/admin/import-prompts.tsx](src/components/admin/import-prompts.tsx)
- [src/components/prompts/hf-data-studio-dropdown.tsx](src/components/prompts/hf-data-studio-dropdown.tsx)
- [tests/generate-contributors-format.test.js](tests/generate-contributors-format.test.js)

</details>



This page covers the comprehensive import and export architecture of `prompts.chat`, explaining how data flows between the PostgreSQL database, the `prompts.csv` and `prompts.json` export routes, the GitHub repository synchronization scripts (`generate-contributors.sh`), and the HuggingFace dataset integration.

---

## System Purpose & Scope

The import and export subsystem addresses several key architectural needs:

1.  **Public Data Distribution**: Exposes clean CSV (`/prompts.csv`) and JSON (`/prompts.json`) endpoints for external integrations, SDKs, and HuggingFace datasets [src/app/prompts.csv/route.ts:28-95](), [src/app/prompts.json/route.ts:25-223]().
2.  **Git-Driven Workflow**: Maintains a dual state where prompt contributions made via the web UI or repository sync update both database models and GitHub commit history with precise contributor attribution [scripts/generate-contributors.sh:1-201]().
3.  **Administrative Bulk Operations**: Allows administrators to perform bulk import, export, or wipe prompt records through admin panel components and backend API endpoints [src/components/admin/import-prompts.tsx:1-50]().

Sources: [src/app/prompts.csv/route.ts:28-95](), [src/app/prompts.json/route.ts:25-223](), [scripts/generate-contributors.sh:1-201](), [src/components/admin/import-prompts.tsx:1-50]()

---

## CSV & JSON Export Routes

### CSV Export Endpoint (`GET /prompts.csv`)

The CSV route serves a static export of all public prompts as a CSV file, suitable for direct data import, analysis, or feeding other tools.

-   **Route File**: [src/app/prompts.csv/route.ts:1-95]()
-   **Revalidation**: Cache is revalidated every hour (`export const revalidate = 3600`) to keep the export fresh [src/app/prompts.csv/route.ts:27-27]().
-   **Filtering**: Only includes prompts where `isPrivate` and `isUnlisted` are false, excluding deleted prompts (`deletedAt: null`) [src/app/prompts.csv/route.ts:31-37]().
-   **Fields & Formatting**:
    -   `act`: Escaped prompt title with CSV quoting rules [src/app/prompts.csv/route.ts:5-16](), [src/app/prompts.csv/route.ts:67-67]().
    -   `prompt`: Full prompt content, escaped [src/app/prompts.csv/route.ts:68-68]().
    -   `for_devs`: Boolean flag string `"TRUE"` if the prompt category slug is `"coding"`, else `"FALSE"` [src/app/prompts.csv/route.ts:69-69]().
    -   `type`: Either `"STRUCTURED"` if the format is JSON/YAML, or `"TEXT"` for plain text prompts [src/app/prompts.csv/route.ts:70-70]().
    -   `contributor`: Comma-separated string of contributor identifiers, including the primary author and co-contributors, determined through `getUserIdentifier()` [src/app/prompts.csv/route.ts:18-25](), [src/app/prompts.csv/route.ts:74-80]().

This endpoint returns CSV content with appropriate headers and MIME type `text/csv; charset=utf-8`.

---

### JSON Export Endpoint (`GET /prompts.json`)

The JSON route exposes a paginated API listing of prompts with rich metadata, including authorship, categories, tags, and votes.

-   **Route File**: [src/app/prompts.json/route.ts:1-246]()
-   **Dynamic Content**: Declared with `dynamic = "force-dynamic"` allowing fresh data on demand [src/app/prompts.json/route.ts:18-18]().
-   **Conditional Requests**: Generates an ETag by hashing the total prompt count and latest update timestamp to support HTTP 304 caching [src/app/prompts.json/route.ts:21-72]().
-   **Pagination Support**: Supports `page` and `limit` query parameters with sensible defaults and maximum limit (`MAX_LIMIT = 100`) [src/app/prompts.json/route.ts:29-41](), [src/app/prompts.json/route.ts:145-148]().
-   **Content Preview**: Returns either `contentPreview` (truncated to 500 characters) or full `content` when `full_content=true` query parameter is set [src/app/prompts.json/route.ts:29-38](), [src/app/prompts.json/route.ts:153-169]().
-   **Response Schema**: Includes prompt fields such as id, title, slug, description, type, category information, author and contributors (with user identifiers), tags, vote and comment counts, media fields, and timestamps [src/app/prompts.json/route.ts:74-213]().

---

Title: "CSV and JSON Export Data Flow"
```mermaid
graph TD
    subgraph "Code Entity Space"
        DB["db.prompt"] --> RouteCSV["src/app/prompts.csv/route.ts"]
        DB --> RouteJSON["src/app/prompts.json/route.ts"]
        RouteCSV --> CSV_Res["TextResponse (text/csv)"]
        RouteJSON --> JSON_Res["NextResponse (application/json)"]
    end

    subgraph "Natural Language Space"
        CSV_Res --> HuggingFace["HuggingFace Dataset Viewer"]
        JSON_Res --> ClientApps["External AI Tools & CLI"]
    end
```

Sources: [src/app/prompts.csv/route.ts:4-95](), [src/app/prompts.json/route.ts:1-246]()

---

## Contributor Attribution & Git Synchronization

`prompts.chat` maintains proper GitHub-based attribution for every prompt contribution by linking the `prompts.csv` and `PROMPTS.md` repository files to the live database copy, using automated scripts and careful commit message crafting.

### `generate-contributors.sh`

This shell script automates updating the local repository from the live deployment's CSV export:

1.  **Fetch Remote CSV**: Downloads the latest prompts CSV from `https://prompts.chat/prompts.csv` into a temporary file `prompts.csv.remote` [scripts/generate-contributors.sh:13-21]().
2.  **Python Diffing & Update**:
    -   Reads the remote and local CSVs with Python's `csv.DictReader`, normalizing line endings and handling CSV errors gracefully [scripts/generate-contributors.sh:38-74]().
    -   Detects new or updated prompts by comparing existing rows with remote source data.
3.  **Commit Attribution**:
    -   Extracts the primary contributor and co-authors from the `contributor` field with `parse_contributors()` [scripts/generate-contributors.sh:94-114]().
    -   Commits changes to `prompts.csv` and `PROMPTS.md` with author metadata set via environment variables `GIT_AUTHOR_NAME` and `GIT_AUTHOR_EMAIL`.
    -   Adds `Co-authored-by:` trailers for co-contributors in commit messages for GitHub's contributor graph [scripts/generate-contributors.sh:116-130]().
4.  **Markdown Sync**:
    -   Manages `PROMPTS.md` by adding or updating prompt details inside collapsible `<details>` blocks, preserving a human-readable repository representation synced to the CSV [scripts/generate-contributors.sh:175-193]().

### `rebuild-history.sh`

This one-time administrative script is used for rewriting the entire `prompts.csv` git history to ensure accurate contributor attribution from scratch:

-   Removes `prompts.csv` from Git tracking [scripts/rebuild-history.sh:100-102]().
-   Creates an empty initial commit with the CSV header [scripts/rebuild-history.sh:104-116]().
-   Iterates through every prompt in a backup CSV, appending each row and committing with the correct `GIT_AUTHOR_NAME` and `GIT_AUTHOR_EMAIL`, and adding co-author trailer lines [scripts/rebuild-history.sh:39-153]().

---

Title: "Git Contribution Synchronization Pipeline"
```mermaid
graph TD
    subgraph "Code Entity Space"
        Script["scripts/generate-contributors.sh"] --> Python["EmbeddedPythonEngine"]
        Python --> GitAdd["git add prompts.csv PROMPTS.md"]
        GitAdd --> GitCommit["git_commit() with author info"]
    end

    subgraph "Natural Language Space"
        RemoteCSV["https://prompts.chat/prompts.csv"] --> Script
        Python --> PromptRow["CSV Row Data"]
        PromptRow --> CommitMsg["build_commit_msg()"]
        PromptRow --> Markdown["update_prompt_in_md()"]
    end
```

Sources: [scripts/generate-contributors.sh:16-130](), [scripts/generate-contributors.sh:174-193](), [scripts/rebuild-history.sh:39-153]()

---

## HuggingFace Dataset Integration

`prompts.chat` is published as an actively used dataset on HuggingFace under `fka/prompts.chat`, providing users with integration capabilities for AI training and exploration [README.md:24-40]().

### HFDataStudioDropdown Component

The client-side React component `HFDataStudioDropdown` facilitates exploration and query generation for the HuggingFace dataset:

-   **File**: [src/components/prompts/hf-data-studio-dropdown.tsx:1-185]()
-   **Features**:
    -   Provides a dropdown with predefined SQL query examples loaded from static JSON (`sql-examples.json`) [src/components/prompts/hf-data-studio-dropdown.tsx:21-23]().
    -   Includes a direct link button (`🤗`) that opens the dataset viewer in HuggingFace’s Data Studio [src/components/prompts/hf-data-studio-dropdown.tsx:39-47]().
    -   Supports AI-powered SQL generation from natural language inputs by POSTing to `/api/generate/sql` [src/components/prompts/hf-data-studio-dropdown.tsx:49-69]().
    -   Monaco editor integration for editing and previewing SQL [src/components/prompts/hf-data-studio-dropdown.tsx:158-175]().
    -   Responsive UI with popover-based dropdown and run query button [src/components/prompts/hf-data-studio-dropdown.tsx:71-185]().

This enhances ease of querying the prompt dataset with complex filters and facilitates data-driven prompt research directly from the web application.

Sources: [src/components/prompts/hf-data-studio-dropdown.tsx:1-185](), [README.md:24-40]()

---

## Admin Bulk Operations

The admin interface offers bulk import/export management features allowing administrators to ingest large prompt datasets or perform cleanups:

-   **Component**: [src/components/admin/import-prompts.tsx:1-210]()
-   **Supported Operations**:
    -   Bulk import prompts into the database from uploaded CSV files or other sources. The `handleImport` function makes a `POST` request to `/api/admin/import-prompts` [src/components/admin/import-prompts.tsx:44-73]().
    -   Delete bulk prompt records for cleaning or resetting the database. The `handleDelete` function makes a `DELETE` request to `/api/admin/import-prompts` [src/components/admin/import-prompts.tsx:76-100]().
-   **Integration**: Uses Prisma ORM to create or update `Prompt` models en masse, ensuring data integrity and trigger validation [src/components/admin/import-prompts.tsx:44-100]().

This empowers maintenance tasks for large scale data handling and migration scenarios.

Sources: [src/components/admin/import-prompts.tsx:1-210]()

---

# Summary

This Import & Export sub-system of `prompts.chat` tightly integrates prompt data sources between live PostgreSQL storage, GitHub versioned CSV/Markdown files, public HTTP export routes, and dataset hosting on HuggingFace. The robust scripting for contributor attribution and the rich JSON/CSV exports support both community contribution workflows and external integration needs. The admin bulk facilities provide powerful tooling for managing the dataset lifecycle at scale.

---

# Page: Media Generation & Attachments

# Media Generation & Attachments

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/reset-credits.yml](.github/workflows/reset-credits.yml)
- [prisma/migrations/20251222132600_add_user_flagged_and_unusual_activity/migration.sql](prisma/migrations/20251222132600_add_user_flagged_and_unusual_activity/migration.sql)
- [prisma/migrations/20251225000000_add_generation_credits/migration.sql](prisma/migrations/20251225000000_add_generation_credits/migration.sql)
- [src/app/api/admin/users/[id]/route.ts](src/app/api/admin/users/[id]/route.ts)
- [src/app/api/admin/users/route.ts](src/app/api/admin/users/route.ts)
- [src/app/api/cron/reset-credits/route.ts](src/app/api/cron/reset-credits/route.ts)
- [src/app/api/media-generate/route.ts](src/app/api/media-generate/route.ts)
- [src/app/api/media-generate/status/route.ts](src/app/api/media-generate/status/route.ts)
- [src/components/admin/users-table.tsx](src/components/admin/users-table.tsx)
- [src/components/prompts/audio-player.tsx](src/components/prompts/audio-player.tsx)
- [src/components/prompts/media-generator.tsx](src/components/prompts/media-generator.tsx)
- [src/lib/plugins/media-generators/fal.ts](src/lib/plugins/media-generators/fal.ts)
- [src/lib/plugins/media-generators/index.ts](src/lib/plugins/media-generators/index.ts)
- [src/lib/plugins/media-generators/types.ts](src/lib/plugins/media-generators/types.ts)
- [src/lib/plugins/media-generators/wiro.ts](src/lib/plugins/media-generators/wiro.ts)

</details>



## Purpose and Scope
This document provides detailed technical documentation for the media generation and attachment subsystems in `prompts.chat`. It covers the architecture and implementation of media prompt types, the `MediaGenerator` React component (`[src/components/prompts/media-generator.tsx:83-214]()`), the backend API routes (`[src/app/api/media-generate/route.ts:1-141]()`), provider plugins (`fal` and `wiro`), user generation credits enforcement and daily resets, as well as supported storage backends for media assets.

---

## 1. Media Prompt Types & Input Handling
Prompts that extend beyond text output produce media files with types such as:

- `IMAGE` (`[src/lib/plugins/media-generators/types.ts:7]()`)
- `VIDEO` (`[src/lib/plugins/media-generators/types.ts:7]()`)
- `AUDIO` (`[src/lib/plugins/media-generators/types.ts:7]()`)

When a prompt contains template variables (e.g., `${variable}` or `${variable:default}`), the component uses a utility function to fill these placeholders with either default values or example text to ensure valid request payloads (`[src/components/prompts/media-generator.tsx:74-80]()`).

### Prompt Variables Parsing
The `fillPromptVariables` function replaces template variables in prompts with example strings or default values (`[src/components/prompts/media-generator.tsx:74-80]()`). It uses a regular expression to detect all `${}` tokens and replaces them accordingly:

```ts
function fillPromptVariables(prompt: string): string {
  return prompt.replace(/\$\{([^}:]+)(?::([^}]*))?\}/g, (match, varName, defaultValue) => {
    return defaultValue || `(example ${varName})`;
  });
}
```

### Input Images
Some generation requests support an optional `inputImageUrl` field enabling image-conditioned generation pipelines, such as image-to-video or image-to-image generation (`[src/lib/plugins/media-generators/types.ts:21]()`).

Sources: `[src/lib/plugins/media-generators/types.ts:7-21]`, `[src/components/prompts/media-generator.tsx:74-80]()`

---

## 2. The MediaGenerator Component & UI Subsystems

### Overview
The `MediaGenerator` is a React client component that manages the entire UI and client state for AI media generation workflows (`[src/components/prompts/media-generator.tsx:1-3]()`). It presents:

- Model selection dropdown (models filtered by media type) (`[src/components/prompts/media-generator.tsx:111-116]()`)
- Aspect ratio selector for image/video generation (`[src/components/prompts/media-generator.tsx:35-43]()`)
- Generation status and progress feedback (`[src/components/prompts/media-generator.tsx:95-97]()`)
- Error handling and success notifications (`[src/components/prompts/media-generator.tsx:25]()`)
- Integration with provider-specific communication channels (WebSocket or polling) (`[src/components/prompts/media-generator.tsx:186-214]()`)

It notifies its parent component via the `onMediaGenerated` callback with the URL of generated media once production completes (`[src/components/prompts/media-generator.tsx:59]()`).

### Key Component States
- `models`: List of available generation models for selected media type (`[src/components/prompts/media-generator.tsx:91]()`)
- `selectedModel`: Currently selected model object (`[src/components/prompts/media-generator.tsx:93]()`)
- `aspectRatio`: User-selected aspect ratio string (e.g., "1:1", "16:9") (`[src/components/prompts/media-generator.tsx:94]()`)
- `status`: Current generation stage (idle, queued, processing, completed, error) (`[src/components/prompts/media-generator.tsx:95]()`)
- `progress`: Numeric progress percentage (0–100) (`[src/components/prompts/media-generator.tsx:97]()`)
- `statusKey`: Semantic status message identifier for i18n translations (`[src/components/prompts/media-generator.tsx:96]()`)
- `error`: Error message string if any failure occurs (`[src/components/prompts/media-generator.tsx:101]()`)
- `wsRef`: WebSocket connection reference (`[src/components/prompts/media-generator.tsx:102]()`)

### Data Flow

1. On mount, fetches models from `GET /api/media-generate` (`[src/components/prompts/media-generator.tsx:105-125]()`).
2. On user action to generate:
   - Sends `POST /api/media-generate` with filled prompt, selected model, provider, type, and aspect ratio (`[src/components/prompts/media-generator.tsx:140-161]()`).
   - Receives task metadata and connection info (WebSocket URL or token) (`[src/components/prompts/media-generator.tsx:168]()`).
3. Depending on provider:
   - For WebSocket-supporting providers (e.g., Wiro), opens connection to receive live updates (`[src/lib/plugins/media-generators/wiro.ts:56-127]()`).
   - For polling-based providers (e.g., Fal), periodically polls status endpoint (`[src/components/prompts/media-generator.tsx:186-214]()`).
4. Updates status, progress, and messages accordingly (`[src/components/prompts/media-generator.tsx:205-208]()`).
5. Upon completion, triggers `onMediaGenerated` with output URL and resets UI (`[src/components/prompts/media-generator.tsx:171-182]()`).

Diagram: Natural Language to Code Entity Mapping for Media Generation UI
```mermaid
graph TD
  NL_Init["User Requests Media Generation"] --> NL_Select["User Picks Model & Aspect Ratio"]
  NL_Init --> CG_Comp["MediaGenerator Component [src/components/prompts/media-generator.tsx:83]"]
  CG_Comp --> CG_Fill["fillPromptVariables() [src/components/prompts/media-generator.tsx:74]"]
  CG_Fill --> API_Route["POST /api/media-generate [src/app/api/media-generate/route.ts:45]"]
  API_Route --> Plugin_Reg["getMediaGeneratorPlugin() [src/lib/plugins/media-generators/index.ts:37]"]
```
Sources: `[src/components/prompts/media-generator.tsx:64-214]`, `[src/components/prompts/audio-player.tsx:16-211]`, `[src/lib/plugins/media-generators/index.ts:37-40]()`

---

## 3. Generation API Routes

The backend media generation API is implemented under the Next.js route `/api/media-generate` and supports `GET` and `POST` methods (`[src/app/api/media-generate/route.ts:1-141]()`).

### `GET /api/media-generate`
- Authenticates user session via `auth()` (`[src/app/api/media-generate/route.ts:10-15]()`).
- Checks availability of any enabled media generator plugin (`[src/app/api/media-generate/route.ts:17]()`).
- Returns available models grouped by media type (`imageModels`, `videoModels`, `audioModels`) (`[src/app/api/media-generate/route.ts:18-36]()`).
- Returns user generation credits and whether the user is flagged (`[src/app/api/media-generate/route.ts:22-42]()`).

### `POST /api/media-generate`
- Authenticates session (`[src/app/api/media-generate/route.ts:46-50]()`).
- Validates required fields: `prompt`, `model`, `provider`, `type` (`[src/app/api/media-generate/route.ts:85-90]()`).
- Checks user flagged status and remaining `generationCreditsRemaining` (`[src/app/api/media-generate/route.ts:54-80]()`).
- Obtains matching media generator plugin via `getMediaGeneratorPlugin` (`[src/app/api/media-generate/route.ts:92]()`).
- Calls plugin's `startGeneration` with generation parameters (`[src/app/api/media-generate/route.ts:108-115]()`).
- Decrements user's remaining credit by 1 upon successful generation start (`[src/app/api/media-generate/route.ts:117-125]()`).
- Returns task metadata including `taskId`, `socketAccessToken`, `webSocketUrl`, and `provider` (`[src/app/api/media-generate/route.ts:127-133]()`).

Diagram: Generation API Request Flow
```mermaid
graph TD
  Client["Client POST /api/media-generate"] --> Auth["auth() [src/app/api/media-generate/route.ts:10]"]
  Auth --> UserFetch["db.user.findUnique() [src/app/api/media-generate/route.ts:54]"]
  UserFetch --> CreditCheck{"user.flagged? credits > 0?"}
  CreditCheck -->|No| Reject["Return 403 Forbidden"]
  CreditCheck -->|Yes| PluginLookup["getMediaGeneratorPlugin() [src/app/api/media-generate/route.ts:92]"]
  PluginLookup --> StartGen["plugin.startGeneration() [src/app/api/media-generate/route.ts:108]"]
  StartGen --> CreditUpdate["db.user.update() [src/app/api/media-generate/route.ts:118]"]
  CreditUpdate --> ReturnTask["Return Task Metadata [src/app/api/media-generate/route.ts:127]"]
```
Sources: `[src/app/api/media-generate/route.ts:1-141]()`

---

## 4. Provider Plugins: `fal` and `wiro`

`prompts.chat` supports an extensible plugin system for media generation providers located in `src/lib/plugins/media-generators`. Two main providers are implemented: Fal.ai and Wiro.ai (`[src/lib/plugins/media-generators/index.ts:11-22]()`).

### 4.1 Fal.ai Plugin (`fal.ts`)
- Uses Fal.ai's **queue API** hosted at `https://queue.fal.run` (`[src/lib/plugins/media-generators/fal.ts:25]()`).
- Generation is asynchronous with **HTTP polling** for status updates (`[src/lib/plugins/media-generators/fal.ts:5]()`).
- Validates origins with `assertFalOrigin()` to prevent SSRF attacks (`[src/lib/plugins/media-generators/fal.ts:27-48]()`).
- Implements:
  - `submitToFalQueue(modelId, input)` (`[src/lib/plugins/media-generators/fal.ts:106-130]()`)
  - `getFalRequestStatus(statusUrl)` (`[src/lib/plugins/media-generators/fal.ts:135-156]()`)
  - `getFalRequestResult(responseUrl)` (`[src/lib/plugins/media-generators/fal.ts:161-182]()`)
- Statuses map via `falStatusMap` (`[src/lib/plugins/media-generators/fal.ts:64-70]()`).
- The `falWebSocketHandler` is a no-op as Fal.ai uses polling, not WebSockets for status updates (`[src/lib/plugins/media-generators/fal.ts:201-215]()`).

### 4.2 Wiro.ai Plugin (`wiro.ts`)
- Uses realtime **WebSocket API** (`wss://socket.wiro.ai/v1`) alongside REST API at `https://api.wiro.ai/v1` (`[src/lib/plugins/media-generators/wiro.ts:23-24]()`).
- Starts generation via POST with `FormData` parameters (`[src/lib/plugins/media-generators/wiro.ts:163-199]()`).
- WebSocket message types map via `wiroStatusMap` (`[src/lib/plugins/media-generators/wiro.ts:40-54]()`).
- The `wiroWebSocketHandler` processes incoming WebSocket messages to update progress and status (`[src/lib/plugins/media-generators/wiro.ts:56-127]()`).

Diagram: Provider Plugin Mapping
```mermaid
graph TD
  NS_Plugin["AI Generation Provider Integration"] --> NS_Fal["Fal.ai Asynchronous Queue"]
  NS_Plugin --> NS_Wiro["Wiro.ai Realtime WebSocket"]
  NS_Fal --> CS_Fal["falGeneratorPlugin [src/lib/plugins/media-generators/fal.ts:217]"]
  CS_Fal --> CS_FalSub["submitToFalQueue() [src/lib/plugins/media-generators/fal.ts:106]"]
  CS_Fal --> CS_FalCheck["checkStatus() [src/lib/plugins/media-generators/fal.ts:330]"]
  NS_Wiro --> CS_Wiro["wiroGeneratorPlugin [src/lib/plugins/media-generators/wiro.ts:129]"]
  CS_Wiro --> CS_WiroSock["wiroWebSocketHandler [src/lib/plugins/media-generators/wiro.ts:56]"]
```
Sources: `[src/lib/plugins/media-generators/fal.ts:1-374]()`, `[src/lib/plugins/media-generators/wiro.ts:1-225]()`, `[src/lib/plugins/media-generators/index.ts:1-95]()`

---

## 5. Generation Credits & Cron Reset

### Credits System
Each user has:
- `dailyGenerationLimit` — Maximum daily generations (`[src/components/admin/users-table.tsx:57]()`).
- `generationCreditsRemaining` — Remaining credits for the current day (`[src/components/admin/users-table.tsx:58]()`).
- `flagged` — Boolean disabling generation if true (`[src/components/admin/users-table.tsx:54]()`).

### Daily Reset Workflow
- A scheduled GitHub Actions workflow (`.github/workflows/reset-credits.yml`) triggers daily at midnight UTC (`[.github/workflows/reset-credits.yml:1-6]()`).
- Calls `POST /api/cron/reset-credits` (`[.github/workflows/reset-credits.yml:13-17]()`).
- The `reset-credits` API route updates all users' `generationCreditsRemaining` to their `dailyGenerationLimit`.
- Admin API routes on `/api/admin/users/[id]` patch user credit limits, also resetting `generationCreditsRemaining` to the new `dailyGenerationLimit` (`[src/app/api/admin/users/[id]/route.ts:53-61]()`).

Diagram: Credit Reset and Admin Patch Architecture
```mermaid
graph TD
  Cron["GitHub Actions Cron [.github/workflows/reset-credits.yml:1]"] --> Endpoint["POST /api/cron/reset-credits [src/app/api/cron/reset-credits/route.ts]"]
  AdminUI["UsersTable Component [src/components/admin/users-table.tsx:205]"] --> AdminPatch["PATCH /api/admin/users/[id] [src/app/api/admin/users/[id]/route.ts:6]"]
  Endpoint --> DB["Prisma DB User Model"]
  AdminPatch --> DB
```
Sources: `[.github/workflows/reset-credits.yml:1-30]()`, `[src/components/admin/users-table.tsx:205-222]()`, `[src/app/api/admin/users/[id]/route.ts:53-61]()`

---

## 6. Storage Backends for Media & Attachments
Generated media assets and user file uploads are stored via configurable storage plugins implementing storage interfaces (`[src/lib/plugins/storage/s3.ts:1]()`).

### 6.1 Amazon S3 Plugin (`src/lib/plugins/storage/s3.ts`)
- Supports AWS S3 and compatible servers (MinIO, DO Spaces).
- Uses AWS SDK's `PutObjectCommand` and `DeleteObjectCommand`.

### 6.2 DigitalOcean Spaces Plugin (`src/lib/plugins/storage/do-spaces.ts`)
- Tailored for DigitalOcean Spaces S3-compatible endpoints with custom CDN configurations.

Sources: `src/lib/plugins/storage/s3.ts`, `src/lib/plugins/storage/do-spaces.ts`

---

## Summary Diagram: Media Generation Flow in prompts.chat

```mermaid
flowchart TD
  User["User triggers media generation"] --> Comp["MediaGenerator [src/components/prompts/media-generator.tsx:83]"]
  Comp --> API["POST /api/media-generate [src/app/api/media-generate/route.ts:45]"]
  API --> Reg["getMediaGeneratorPlugin() [src/lib/plugins/media-generators/index.ts:37]"]
  Reg --> Start["startGeneration()"]
  Start --> Storage["Storage Backend (S3/DO)"]
```
Sources: `[src/components/prompts/media-generator.tsx:83-214]()`, `[src/app/api/media-generate/route.ts:1-141]()`

---

## References
- Media generator UI: `[src/components/prompts/media-generator.tsx:3-214]()`
- Media generation API routes: `[src/app/api/media-generate/route.ts:1-141]()`
- Fal.ai plugin: `[src/lib/plugins/media-generators/fal.ts:1-374]()`
- Wiro.ai plugin: `[src/lib/plugins/media-generators/wiro.ts:1-225]()`
- Plugin registry: `[src/lib/plugins/media-generators/index.ts:1-95]()`
- Credits reset workflow: `[.github/workflows/reset-credits.yml:1-30]()`
- User admin API: `[src/app/api/admin/users/[id]/route.ts:53-61]()`
- Admin user management UI: `[src/components/admin/users-table.tsx:205-222]()`
- Storage plugins: `src/lib/plugins/storage/s3.ts`, `src/lib/plugins/storage/do-spaces.ts`

---

# Page: Bots, Teams & Connectors

# Bots, Teams & Connectors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [public/bots/autogpt-dark.svg](public/bots/autogpt-dark.svg)
- [public/bots/autogpt.svg](public/bots/autogpt.svg)
- [src/__tests__/api/bot-teams.test.ts](src/__tests__/api/bot-teams.test.ts)
- [src/__tests__/app/bot-page-slug-redirect.test.ts](src/__tests__/app/bot-page-slug-redirect.test.ts)
- [src/__tests__/components/bot-teams-graph-card.test.tsx](src/__tests__/components/bot-teams-graph-card.test.tsx)
- [src/__tests__/components/featured-teams.test.tsx](src/__tests__/components/featured-teams.test.tsx)
- [src/__tests__/lib/bot-list.test.ts](src/__tests__/lib/bot-list.test.ts)
- [src/__tests__/lib/bot-platforms.test.ts](src/__tests__/lib/bot-platforms.test.ts)
- [src/__tests__/lib/bot-slug-lookup.test.ts](src/__tests__/lib/bot-slug-lookup.test.ts)
- [src/__tests__/lib/bot-teams.test.ts](src/__tests__/lib/bot-teams.test.ts)
- [src/app/api/bots/teams/route.ts](src/app/api/bots/teams/route.ts)
- [src/app/bots/[slug]/page.tsx](src/app/bots/[slug]/page.tsx)
- [src/components/admin/bots-management.tsx](src/components/admin/bots-management.tsx)
- [src/components/admin/teams-management.tsx](src/components/admin/teams-management.tsx)
- [src/components/bots/bot-bundle-install.tsx](src/components/bots/bot-bundle-install.tsx)
- [src/components/bots/bot-card.tsx](src/components/bots/bot-card.tsx)
- [src/components/bots/bot-form.tsx](src/components/bots/bot-form.tsx)
- [src/components/bots/bot-install.tsx](src/components/bots/bot-install.tsx)
- [src/components/bots/bot-og-image.tsx](src/components/bots/bot-og-image.tsx)
- [src/components/bots/bot-platform-tabs.tsx](src/components/bots/bot-platform-tabs.tsx)
- [src/components/bots/teams/bot-teams-graph.tsx](src/components/bots/teams/bot-teams-graph.tsx)
- [src/components/bots/teams/featured-teams.tsx](src/components/bots/teams/featured-teams.tsx)
- [src/components/bots/teams/team-card.tsx](src/components/bots/teams/team-card.tsx)
- [src/components/bots/teams/team-title-link.ts](src/components/bots/teams/team-title-link.ts)
- [src/lib/bots/index.ts](src/lib/bots/index.ts)
- [src/lib/bots/schema.ts](src/lib/bots/schema.ts)
- [src/lib/bots/team-graph.ts](src/lib/bots/team-graph.ts)
- [src/lib/bots/teams.ts](src/lib/bots/teams.ts)
- [src/lib/mcp/tools/teams.ts](src/lib/mcp/tools/teams.ts)

</details>



## Purpose & Scope
This page documents the **BOT** prompt type within `prompts.chat`, covering its database schema, configuration structure, frontend UI components, multi-platform installation bundles (OpenClaw, AutoGPT, Dots, Duet, Muse, Grok, Hermes), bot teams and multi-agent handoffs, Model Context Protocol (MCP) tools integration, and administrative management workflows.

---

## 1. Bot Schema & Data Structure
Bots are specialized prompt entities stored in the core `Prompt` table where `type = "BOT"`. They aggregate system instructions, execution routines, agent skills, third-party connectors, and hardware/runtime requirements into a unified schema parsed by `src/lib/bots/schema.ts` and normalized via `src/lib/bots/index.ts` [src/lib/bots/index.ts:89-116]().

The supported target platforms are enumerated in `BOT_PLATFORMS`: `GROK_BOT`, `OPENCLAW`, `HERMES`, `AUTOGPT`, `DOTS`, `DUET`, and `MUSE` [src/lib/bots/schema.ts:3-4](). Computer requirements (`BotComputerRequirement`) govern execution context: `CLOUD` (remote container/desktop) or `LOCAL` (local machine/file access) [src/lib/bots/schema.ts:129-130]().

```mermaid
graph TD
    A["Prompt Record type=BOT"] --> B["src/lib/bots/schema.ts"]
    B --> C["botPlatformsSchema"]
    B --> D["botComputerRequirementsSchema"]
    B --> E["parseBotConfig()"]
    A --> F["src/lib/bots/index.ts"]
    F --> G["toBotView()"]
    G --> H["BotView Object"]

    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Diagram 1: Bot Data Normalization Pipeline from Database Model to BotView*

Sources: `[src/lib/bots/schema.ts:1-136]`, `[src/lib/bots/index.ts:24-116]`

---

## 2. Bot Pages, Cards & Forms
User interactions with bots occur through dedicated UI structures. The bot creation and editing interface is backed by form components that validate icon definitions (`BOT_ICONS`) and color themes (`BOT_COLORS`) [src/lib/bots/schema.ts:71-122](). 

Public discovery and individual view pages (`src/app/bots/[slug]/page.tsx`) render metadata summaries via `BotCard`, execution requirements via `BotComputerBadges`, and interactive installation modals [src/app/bots/[slug]/page.tsx:16-23](). Slug resolution and permanent redirection are handled using `findBotBySlug` and `botSlugFromParam` [src/lib/bots/index.ts:1]().

```mermaid
graph TD
    A["/bots/[slug] Route"] --> B["BotPage()"]
    B --> C["getBotById()"]
    C -->|Found & Visible| D["Render Bot View"]
    C -->|Not Found by ID| E["findBotBySlug()"]
    E -->|Found by Slug| F["permanentRedirect()"]
    E -->|Not Found| G["notFound()"]

    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Diagram 2: Bot URL Routing and Slug Fallback Flow*

Sources: `[src/app/bots/[slug]/page.tsx:43-79]`, `[src/lib/bots/schema.ts:70-122]`, `[src/__tests__/lib/bot-slug-lookup.test.ts:39-106]`

---

## 3. Platform Install Bundles
Bots support automated deployment across multiple agent runtimes. The installation infrastructure is split into single-bot installers (`src/components/bots/bot-install.tsx`) and bundle installers (`src/components/bots/bot-bundle-install.tsx`) [src/app/bots/[slug]/page.tsx:17-22]().

Chat-based deployment targets (`AUTOGPT`, `DOTS`, `DUET`, `MUSE`) rely on `BOT_PLATFORM_CHAT_INSTALL` directives to route users to platform-specific web chats with pre-formatted prompt templates [src/lib/bots/schema.ts:21-37]().

```mermaid
graph TD
    A["BotInstall component"] --> B["src/components/bots/bot-install.tsx"]
    B --> C{"Is Chat Install Platform?"}
    C -->|Yes| D["BOT_PLATFORM_CHAT_INSTALL url & hint"]
    C -->|No| E["CopyBlock command & prompt"]
    D --> F["OpenPlatformChatButton"]

    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Diagram 3: Platform Installation Code Flow*

Sources: `[src/lib/bots/schema.ts:21-37]`, `[src/components/bots/bot-install.tsx:65-126]`, `[src/components/bots/bot-bundle-install.tsx:1-97]`

---

## 4. Bot Teams & Handoffs
Bot Teams group multiple agents into collaborative units that execute workflows via directed handoffs (`BotTeamLinkView`). Teams are managed through `src/lib/bots/teams.ts` and exposed via database models including `BotTeam`, `BotTeamMember`, and `BotTeamLink` [src/lib/bots/teams.ts:1-97]().

Each team member has a specific role description and maps to underlying bot prompts [src/__tests__/lib/bot-teams.test.ts:88-112](). Team installation options (`getTeamInstallOptions`) aggregate member instructions into unified deployment prompts.

```mermaid
graph TD
    A["BotTeam Record"] --> B["src/lib/bots/teams.ts"]
    B --> C["toTeamView()"]
    C --> D["BotTeamView Object"]
    D --> E["members list & roles"]
    D --> F["links handoff graph"]
    D --> G["getTeamInstallOptions()"]

    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Diagram 4: Bot Team Data Structures and View Resolution*

Sources: `[src/lib/bots/teams.ts:41-97]`, `[src/__tests__/lib/bot-teams.test.ts:88-112]`

---

## 5. MCP Bot & Team Tools
The Model Context Protocol (MCP) server exposes dedicated tools for searching, retrieving, and saving bots and team objects programmatically at `/api/mcp`.

- **Bot Tools**: `search_bots`, `get_bot`, `save_bot`, `list_my_bots`, `get_my_bot` [src/lib/mcp/tools/bots.ts:1-1]().
- **Team Tools**: `list_teams`, `get_team`, `save_team` [src/lib/mcp/tools/teams.ts:81-173]().

```mermaid
graph TD
    A["/api/mcp Endpoint"] --> B["src/lib/mcp/server.ts"]
    B --> C["registerTeamTools()"]
    C --> D["list_teams tool"]
    C --> E["get_team tool"]
    D --> F["listTeams()"]
    E --> G["getTeam() & getTeamInstallOptions()"]

    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Diagram 5: MCP Team Tool Registration and Execution Flow*

Sources: `[src/lib/mcp/tools/teams.ts:78-173]`, `[src/__tests__/api/bot-teams.test.ts:120-139]`

---

## 6. Bot Admin Management
Administrative oversight of bot listings is centralized in admin management views (`src/components/admin/bots-management.tsx` and `src/components/admin/teams-management.tsx`). Administrators can inspect delisted prompts, modify visibility flags (`isPrivate`, `isUnlisted`), enforce quality standards, and manage platform distribution metrics across the system.

Sources: `[src/components/admin/bots-management.tsx:1-1]`, `[src/components/admin/teams-management.tsx:1-1]`

---

# Page: Decision Classifiers & Chains

# Decision Classifiers & Chains

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/__tests__/components/classifiers-ui.test.tsx](src/__tests__/components/classifiers-ui.test.tsx)
- [src/__tests__/components/upvote-ui.test.tsx](src/__tests__/components/upvote-ui.test.tsx)
- [src/__tests__/db/classifiers.db.test.ts](src/__tests__/db/classifiers.db.test.ts)
- [src/app/classifiers/[slug]/page.tsx](src/app/classifiers/[slug]/page.tsx)
- [src/app/classifiers/page.tsx](src/app/classifiers/page.tsx)
- [src/components/classifiers/classifier-cards.tsx](src/components/classifiers/classifier-cards.tsx)
- [src/components/classifiers/classifier-catalog.tsx](src/components/classifiers/classifier-catalog.tsx)
- [src/components/prompts/upvote-button.tsx](src/components/prompts/upvote-button.tsx)
- [src/lib/classifiers/store.ts](src/lib/classifiers/store.ts)

</details>



This page documents the `CLASSIFIER` prompt type, its underlying schema, storage mechanisms in `src/lib/classifiers/store.ts`, and how it integrates into the `prompts.chat` ecosystem. It covers decision models, question types, terminal kinds, the catalog UI at `src/app/classifiers/page.tsx`, chains builder, fixtures, and admin management.

Sources: [src/app/classifiers/page.tsx:1-69](), [src/lib/classifiers/store.ts:1-112]()

---

## Classifier Prompt Type Overview

The `CLASSIFIER` prompt type allows users to create structured decision models that guide AI agents or users through a series of questions to reach a conclusion. Classifiers are defined using a structured JSON configuration stored within the database and can be chained together into complex decision graphs.

Sources: [src/lib/classifiers/store.ts:50-70]()

### Classifier Schema

A classifier is a specialized prompt where the `type` field is set to `CLASSIFIER`. Its core definition resides in the prompt's classifier-specific JSON configuration (`classifierConfig`), while core metadata like `title`, `description`, and `slug` are stored on the prompt record itself.

The main components of a classifier definition include:
*   **`slug`**: A unique URL-safe identifier for the classifier [src/lib/classifiers/store.ts:33]()
*   **`name` / `title`**: The display name of the classifier [src/lib/classifiers/store.ts:31]()
*   **`summary` / `description`**: A brief explanation of the classifier's purpose [src/lib/classifiers/store.ts:32]()
*   **`question`**: Defines the primary question or evaluation axis [src/app/classifiers/[slug]/page.tsx:106-106]()
*   **`outcomes`**: Array of possible classification results or conclusions [src/__tests__/db/classifiers.db.test.ts:74-78]()
*   **`scenarios`**: Predefined test cases used for validation and exploration [src/__tests__/db/classifiers.db.test.ts:80-80]()

Sources: [src/app/classifiers/[slug]/page.tsx:106-115](), [src/__tests__/db/classifiers.db.test.ts:54-84](), [src/lib/classifiers/store.ts:29-46]()

### Question Types & Decision Models

Classifiers support various question types and structural models to facilitate structured decision-making:
*   **Choice**: Presents predefined categorical options for selection [src/__tests__/db/classifiers.db.test.ts:66-72]()
*   **Score**: Evaluates inputs along a numerical scale
*   **Noul (Natural Language Understanding)**: Free-form text input evaluated against criteria

Sources: [src/__tests__/db/classifiers.db.test.ts:64-72]()

---

## Classifier Store & Database Layer

Classifier records and chains are loaded, parsed, and cached using dedicated store utilities located in `src/lib/classifiers/store.ts`.

```mermaid
graph TD
    subgraph "Natural Language Space"
        NL[User Classifier Prompt] -->|Parsed via store.ts| Rec[ClassifierRecord]
        Chain[Chain Definition] -->|Validated via toClassifierChain| CC[ClassifierChain]
    end

    subgraph "Code Entity Space"
        DB[(Prisma DB)] -->|promptSelect| Row[Prompt Row type: CLASSIFIER]
        Row -->|toClassifierRecord| Rec
        DB -->|classifierChainQuery| ChainRow[ClassifierChain Row]
        ChainRow -->|toClassifierChain| CC
        Rec -->|Cached via unstable_cache| Catalog[getClassifierCatalog]
        CC --> Catalog
    end
```
**Diagram: Classifier Storage and Caching Architecture**

Sources: [src/lib/classifiers/store.ts:22-148]()

### Key Functions and Serialization

*   `toClassifierRecord(row)`: Parses raw prompt database rows into structured `ClassifierRecord` objects, validating their JSON configurations [src/lib/classifiers/store.ts:51-70]().
*   `toClassifierChain(row)`: Converts database chain rows into `ClassifierChain` objects, ensuring all member classifiers are valid, public, and non-deleted [src/lib/classifiers/store.ts:82-111]().
*   `getClassifierCatalog()`: Cached function that aggregates all public classifiers, chains, and reference sources using `unstable_cache` [src/lib/classifiers/store.ts:125-164]().
*   `getClassifierVotes(promptIds, userId)`: Fetches vote counts and user-specific voting state outside the catalog cache so votes update instantly [src/lib/classifiers/store.ts:173-195]().

Sources: [src/lib/classifiers/store.ts:51-195]()

---

## User Interface & Catalog

The user interface for browsing classifiers is hosted at `/classifiers` [src/app/classifiers/page.tsx:31-69]() and supported by catalog filtering components [src/components/classifiers/classifier-catalog.tsx:28-183]().

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserSearch["User Search Query & Category Filter"] --> CatalogUI["ClassifierCatalog UI"]
        CatalogUI --> ClassifierCardView["Classifier Cards & Chain Cards"]
    end

    subgraph "Code Entity Space"
        Page["src/app/classifiers/page.tsx"] -->|Calls| Store["getClassifierCatalog()"]
        Page -->|Fetches| Votes["getClassifierVotes()"]
        Page -->|Renders| CatalogComp["src/components/classifiers/classifier-catalog.tsx"]
        CatalogComp -->|Filters via useMemo| FilterFn["filterClassifiers() / filterChains()"]
        CatalogComp -->|Renders Cards| CardComp["src/components/classifiers/classifier-cards.tsx"]
    end
```
**Diagram: Classifier Catalog Data Flow and Rendering**

Sources: [src/app/classifiers/page.tsx:31-69](), [src/components/classifiers/classifier-catalog.tsx:28-62]()

### Catalog Filtering and State Management

*   `ClassifierCatalog`: Manages client-side query string filtering and synchronizes state with URL search parameters using `window.history.replaceState` [src/components/classifiers/classifier-catalog.tsx:28-73]().
*   `ClassifierCard`: Renders individual classifier summaries, outcome chips, category badges, and upvote counters [src/components/classifiers/classifier-cards.tsx:23-67]().
*   `ChainCard`: Renders workflow chains, step sequences, and endpoint counts [src/components/classifiers/classifier-cards.tsx:74-105]().

Sources: [src/components/classifiers/classifier-catalog.tsx:28-105](), [src/components/classifiers/classifier-cards.tsx:23-105]()

---

## Chain Building & Scenario Explorer

Chains allow multiple classifiers to execute in sequence, where the terminal outcome of one classifier informs the input of the next.

### Scenario Explorer

The `ScenarioExplorer` component allows users to switch between predefined scenarios, inspect decision paths, and view rationales [src/__tests__/components/classifiers-ui.test.tsx:88-103]().

```mermaid
graph TD
    subgraph "Natural Language Space"
        Scenario["Predefined Test Scenario"] -->|Selects tab| Explorer["ScenarioExplorer UI"]
        Explorer -->|Highlights outcome & rationale| OutcomeView["Scenario Outcome & Rationale"]
    end

    subgraph "CodeEntitySpace"
        TestComp["src/__tests__/components/classifiers-ui.test.tsx"] -->|Tests| ScenExp["ScenarioExplorer"]
        ScenExp -->|Iterates| Scenarios["classifier.scenarios"]
        ScenExp -->|Matches| Outcomes["classifier.outcomes"]
    end
```
**Diagram: Scenario Explorer Component Mapping**

Sources: [src/__tests__/components/classifiers-ui.test.tsx:88-103]()

---

## Fixtures & Administration

Database seeding, import scripts, and automated tests ensure the integrity of the classifier catalog.

*   `prisma/classifiers/fixtures`: Contains seed definitions for pre-populating classifiers, sources, and chains [src/__tests__/db/classifiers.db.test.ts:29-29]().
*   `importClassifierCatalog`: Imports fixtures into the Prisma database, validating slugs, ownership, and relations [src/__tests__/db/classifiers.db.test.ts:121-155]().
*   Admin workflows allow administrators to inspect version histories [src/app/classifiers/[slug]/page.tsx:126-144](), review change requests, and manage unlisted or private classifiers.

Sources: [src/__tests__/db/classifiers.db.test.ts:121-155](), [src/app/classifiers/[slug]/page.tsx:86-144]()

---

# Page: User System

# User System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [prisma/migrations/20251213133000_add_github_username/migration.sql](prisma/migrations/20251213133000_add_github_username/migration.sql)
- [prisma/migrations/20260127100000_add_user_bio_and_custom_links/migration.sql](prisma/migrations/20260127100000_add_user_bio_and_custom_links/migration.sql)
- [src/__tests__/api/user-profile.test.ts](src/__tests__/api/user-profile.test.ts)
- [src/__tests__/lib/plugins/auth/github.test.ts](src/__tests__/lib/plugins/auth/github.test.ts)
- [src/app/[username]/opengraph-image.tsx](src/app/[username]/opengraph-image.tsx)
- [src/app/api/admin/import-prompts/route.ts](src/app/api/admin/import-prompts/route.ts)
- [src/app/api/auth/register/route.ts](src/app/api/auth/register/route.ts)
- [src/app/api/user/profile/route.ts](src/app/api/user/profile/route.ts)
- [src/app/settings/page.tsx](src/app/settings/page.tsx)
- [src/components/auth/register-form.tsx](src/components/auth/register-form.tsx)
- [src/components/settings/profile-form.tsx](src/components/settings/profile-form.tsx)
- [src/components/user/profile-links.tsx](src/components/user/profile-links.tsx)
- [src/lib/auth/index.ts](src/lib/auth/index.ts)
- [src/lib/db-errors.ts](src/lib/db-errors.ts)
- [src/lib/plugins/auth/github.ts](src/lib/plugins/auth/github.ts)

</details>



This page serves as the parent overview for user-related features within `prompts.chat`. It covers the core user data model, authentication mechanisms, profile management, settings forms, collections, feeds, and social interaction workflows. 

For deep technical implementation details, refer to the respective child pages linked at the bottom.

---

## User Data Model

The core of the user system is backed by the `User` model managed via Prisma ORM. It tracks essential identity parameters, custom profile configurations, roles, and verification states.

| Field          | Type       | Notes                                                                                     |
|----------------|------------|-------------------------------------------------------------------------------------------|
| `id`           | `String`   | Unique identifier (cuid).                                                                 |
| `email`        | `String`   | Unique; for unclaimed/contributor accounts uses a pseudo email format `@unclaimed.prompts.chat` [src/lib/auth/index.ts:46-48](). |
| `username`     | `String`   | Unique case-insensitive username, used in profile URLs `/@username` [src/lib/auth/index.ts:38-40]().                      |
| `name`         | `String?`  | Optional display name [src/lib/auth/index.ts:55]().                                        |
| `role`         | `UserRole` | User role such as `USER` or `ADMIN` [src/app/api/admin/import-prompts/route.ts:106]().                                     |
| `bio`          | `String?`  | Short biography (max 250 chars) [src/app/api/user/profile/route.ts:21]().                                                         |
| `customLinks`  | `Json?`    | Array of user-defined social/website links [src/app/api/user/profile/route.ts:22]().                                              |
| `githubUsername` | `String?` | Immutable GitHub username for GitHub-authenticated users [src/lib/auth/index.ts:40]().                                |
| `verified`     | `Boolean`  | Indicates if the user is verified (badge status) [src/components/settings/profile-form.tsx:71]().                                        |

This model supports regular users, administrators, and special unclaimed accounts created during CSV prompt imports. These accounts can be claimed later via OAuth logins [src/lib/auth/index.ts:44-67, src/app/api/admin/import-prompts/route.ts:160-169]. Uniqueness of usernames is enforced case-insensitively with automatic retry loops on collision [src/lib/auth/index.ts:70-103].

Diagram: User Data Model and Component Mapping
```mermaid
classDiagram
    direction LR
    class User {
        +String id
        +String username
        +String email
        +String role
        +String githubUsername
        +Json customLinks
        +String bio
        +Boolean verified
    }
    class CustomPrismaAdapter {
        +createUser(data)
    }
    class UserProfilePage {
        +username param
        +isOwner boolean
    }
    class ProfileForm {
        +user User
        +update profile
    }
    class Prompt {
        +authorId String
        +title String
    }
    class PromptVote {
        +userId String
        +promptId String
    }

    User "1" -- "1" CustomPrismaAdapter : "Created by"
    User "1" -- "1" UserProfilePage : "Viewed by"
    User "1" -- "1" ProfileForm : "Edited by"
    User "1" -- "0..*" Prompt : "Authors"
    User "1" -- "0..*" PromptVote : "Voters"
    Prompt "1" -- "0..*" PromptVote : "Receives"
```
Sources: [src/lib/auth/index.ts:31-106](), [src/components/settings/profile-form.tsx:64-74](), [src/app/api/user/profile/route.ts:25-86](), [src/app/settings/page.tsx:18-32](), [src/lib/plugins/auth/github.ts:1-24]()

---

## Authentication & Authorization

`prompts.chat` relies on **NextAuth.js 5.0** for handling authentication, supporting multiple OAuth/OIDC provider plugins (such as GitHub, Google, Apple, and Azure) alongside credentials authentication [src/lib/auth/index.ts:108-144]. 

A custom adapter layer (`CustomPrismaAdapter`) extends `PrismaAdapter` to support username management, atomic retry logic for unique constraint violations, unclaimed account claiming via pseudo-emails (`username@unclaimed.prompts.chat`), and session token enrichment through JWT callbacks [src/lib/auth/index.ts:31-196].

Diagram: Authentication Flow Architecture
```mermaid
flowchart TD
    subgraph NaturalLanguageSpace
        ULogin["User initiates login/register"]
        SelProv["Selects OAuth or Credentials"]
        AuthFlow["Performs OAuth handshake or credentials validation"]
    end
    subgraph CodeEntitySpace
        NextAuthF["NextAuth() handler"]
        BuildConfig["buildAuthConfig() in src/lib/auth/index.ts"]
        Plugins["getAuthPlugin() loads providers"]
        Adapter["CustomPrismaAdapter.createUser()"]
        ClaimUnclaimed["Check & claim unclaimed email"]
        UserCreate["Create user with username with retry"]
        JWTCallback["JWT callback updates token with DB data"]
        SessionObj["Session object for client use"]
    end

    ULogin --> SelProv --> AuthFlow --> NextAuthF
    NextAuthF --> BuildConfig --> Plugins
    NextAuthF --> Adapter
    Adapter --> ClaimUnclaimed --> UserCreate
    NextAuthF --> JWTCallback --> SessionObj
```
Sources: [src/lib/auth/index.ts:1-198](), [src/app/api/auth/register/route.ts:1-83](), [src/components/auth/register-form.tsx:23-92]()

For details, see [Authentication & Authorization](#5.1).

---

## User Profiles & Settings

User profile pages are rendered at `/@username` and display the user's details, role badge, join date, prompt count, and total upvotes received [src/app/[username]/opengraph-image.tsx:25-105]. Dynamic OpenGraph images are generated per profile for rich social sharing [src/app/[username]/opengraph-image.tsx:109-245].

The `/settings` route provides form interfaces powered by Zod validation schemas for modifying profiles, biographies, and custom social links [src/app/settings/page.tsx:10-62, src/components/settings/profile-form.tsx:30-46]. Updates are committed through `PATCH /api/user/profile` and trigger a NextAuth session refresh [src/app/api/user/profile/route.ts:25-78, src/components/settings/profile-form.tsx:154-167].

Diagram: Profile Settings Update Pipeline
```mermaid
flowchart TD
    subgraph NaturalLanguageSpace
        NavSettings["User navigates to /settings"]
        EditInfo["Edit profile fields"]
        SubmitForm["Submit profile changes"]
    end
    subgraph CodeEntitySpace
        ProfileFormComp["ProfileForm component"]
        PatchAPI["PATCH /api/user/profile"]
        DBUpdate["db.user.update with validation"]
        SessionRefresh["NextAuth session update (jwt callback)"]
        RouterRedirect["Redirect if username changed"]
    end

    NavSettings --> EditInfo --> SubmitForm
    SubmitForm --> ProfileFormComp --> PatchAPI --> DBUpdate
    DBUpdate --> SessionRefresh --> RouterRedirect
```
Sources: [src/app/[username]/opengraph-image.tsx:20-245](), [src/components/settings/profile-form.tsx:36-173](), [src/app/api/user/profile/route.ts:25-86](), [src/app/settings/page.tsx:10-65]()

For details, see [User Profiles & Settings](#5.2).

---

## Collections & Feeds

Users can bookmark prompts into collections, organize favorite items, subscribe to categories, and receive personalized feed updates. This subsystem bridges user activity preferences with content discovery mechanisms across the application.

Sources: [src/app/api/user/profile/route.ts:1-126]()

For details, see [Collections & Feeds](#5.3).

---

## Social Features

Community interactions include prompt voting/upvoting, comment threads, public leaderboards like the promptmasters ranking, and contributor attribution [src/app/api/admin/import-prompts/route.ts:138-173]. During CSV prompt ingestion (`POST /api/admin/import-prompts`), "pseudo-users" are provisioned with unclaimed email addresses so that historical contributions are correctly tied to authors before they register [src/app/api/admin/import-prompts/route.ts:147-169].

Diagram: Contributor Attribution and Pseudo-User Claiming
```mermaid
flowchart TD
    subgraph NaturalLanguageSpace
        CsvImport["Import prompts from CSV with contributor field"]
        ProvisionUser["Create pseudo unclaimed users"]
        ClaimUser["Contributor logs in to claim account"]
    end
    subgraph CodeEntitySpace
        ImportRoute["POST /api/admin/import-prompts"]
        ContributorCache["Cache contributor username to userId"]
        DbUserUpsert["db.user.findFirst or create unclaimed user"]
        OAuthLogin["CustomPrismaAdapter claim logic"]
    end

    CsvImport --> ImportRoute --> ProvisionUser --> ContributorCache
    ClaimUser --> OAuthLogin --> DbUserUpsert
```
Sources: [src/app/api/admin/import-prompts/route.ts:135-190](), [src/app/[username]/opengraph-image.tsx:92-99](), [src/lib/auth/index.ts:31-68]()

For details, see [Social Features](#5.4).

---

## Child Pages

- [Authentication & Authorization](#5.1) — Covers NextAuth 5.0 setup, OAuth/OIDC providers, credentials auth, API keys, and role-based access.
- [User Profiles & Settings](#5.2) — Explains the `/@username` profile page, activity metrics, verification badges, profile links, and settings forms.
- [Collections & Feeds](#5.3) — Details bookmarking collections, category subscriptions, notifications, and personalized feed generation.
- [Social Features](#5.4) — Explains voting, comments, leaderboards, and contributor attribution workflows.

Sources:  
[src/lib/auth/index.ts]()  
[src/components/settings/profile-form.tsx]()  
[src/app/api/user/profile/route.ts]()  
[src/app/settings/page.tsx]()  
[src/app/[username]/opengraph-image.tsx]()  
[src/app/api/admin/import-prompts/route.ts]()

---

# Page: Authentication & Authorization

# Authentication & Authorization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [prisma/migrations/20251213133000_add_github_username/migration.sql](prisma/migrations/20251213133000_add_github_username/migration.sql)
- [prisma/migrations/20260127100000_add_user_bio_and_custom_links/migration.sql](prisma/migrations/20260127100000_add_user_bio_and_custom_links/migration.sql)
- [src/__tests__/api/user-profile.test.ts](src/__tests__/api/user-profile.test.ts)
- [src/__tests__/lib/auth/provider-metadata.test.ts](src/__tests__/lib/auth/provider-metadata.test.ts)
- [src/__tests__/lib/plugins/auth/github.test.ts](src/__tests__/lib/plugins/auth/github.test.ts)
- [src/__tests__/lib/plugins/auth/oauth.test.ts](src/__tests__/lib/plugins/auth/oauth.test.ts)
- [src/__tests__/lib/plugins/auth/oidc.test.ts](src/__tests__/lib/plugins/auth/oidc.test.ts)
- [src/app/(auth)/login/page.tsx](src/app/(auth)/login/page.tsx)
- [src/app/(auth)/register/page.tsx](src/app/(auth)/register/page.tsx)
- [src/app/[username]/opengraph-image.tsx](src/app/[username]/opengraph-image.tsx)
- [src/app/api/admin/import-prompts/route.ts](src/app/api/admin/import-prompts/route.ts)
- [src/app/api/auth/register/route.ts](src/app/api/auth/register/route.ts)
- [src/app/api/user/profile/route.ts](src/app/api/user/profile/route.ts)
- [src/app/settings/page.tsx](src/app/settings/page.tsx)
- [src/components/auth/auth-content.tsx](src/components/auth/auth-content.tsx)
- [src/components/auth/oauth-button.tsx](src/components/auth/oauth-button.tsx)
- [src/components/auth/register-form.tsx](src/components/auth/register-form.tsx)
- [src/components/settings/profile-form.tsx](src/components/settings/profile-form.tsx)
- [src/components/user/profile-links.tsx](src/components/user/profile-links.tsx)
- [src/lib/auth/index.ts](src/lib/auth/index.ts)
- [src/lib/auth/provider-metadata.ts](src/lib/auth/provider-metadata.ts)
- [src/lib/db-errors.ts](src/lib/db-errors.ts)
- [src/lib/plugins/auth/github.ts](src/lib/plugins/auth/github.ts)
- [src/lib/plugins/auth/index.ts](src/lib/plugins/auth/index.ts)
- [src/lib/plugins/auth/oauth.ts](src/lib/plugins/auth/oauth.ts)
- [src/lib/plugins/auth/oidc.ts](src/lib/plugins/auth/oidc.ts)
- [src/lib/plugins/index.ts](src/lib/plugins/index.ts)

</details>



This page documents the NextAuth.js 5.0 configuration, the `AuthPlugin` interface and registry, the `CustomPrismaAdapter` (username generation and unclaimed account claiming), JWT and session token lifecycle, credentials authentication, user registration, API key management, and role-based access control (RBAC).

Sources: [src/lib/auth/index.ts:1-122](), [src/lib/plugins/auth/index.ts:1-21]()

---

## Plugin Architecture & Built-in Providers

### The `AuthPlugin` Interface

Authentication in prompts.chat is powered by **NextAuth.js v5.0** using a modular, runtime-configurable architecture. Active authentication providers are loaded dynamically from `prompts.config.ts` via the `AuthPlugin` registry.

### Built-in Authentication Plugins

| Plugin ID    | File Path                        | Required Environment Variables                               |
|--------------|---------------------------------|--------------------------------------------------------------|
| `credentials`| `[src/lib/plugins/auth/credentials.ts]()` | None (database-backed)                                    |
| `google`     | `[src/lib/plugins/auth/google.ts]()`      | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`               |
| `azure`      | `[src/lib/plugins/auth/azure.ts]()`       | `AZURE_AD_CLIENT_ID`, `AZURE_AD_CLIENT_SECRET`, `AZURE_AD_TENANT_ID` |
| `github`     | `[src/lib/plugins/auth/github.ts:1-24]()`| `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`                |
| `apple`      | `[src/lib/plugins/auth/apple.ts]()`       | `AUTH_APPLE_ID`, `AUTH_APPLE_SECRET`                      |
| `oidc`       | `[src/lib/plugins/auth/oidc.ts]()`        | `AUTH_OIDC_ID`, `AUTH_OIDC_SECRET`, `AUTH_OIDC_ISSUER`    |
| `oauth`      | `[src/lib/plugins/auth/oauth.ts]()`       | `AUTH_OAUTH_ID`, `AUTH_OIDC_SECRET`, `AUTH_OIDC_ISSUER`   |

All built-in plugins are registered at startup via `registerBuiltInAuthPlugins()` in [src/lib/plugins/auth/index.ts:11-19]().

### Plugin Initialization & Configuration Flow

Title: "Plugin Initialization and Configuration Pipeline"
```mermaid
flowchart TD
    Config["prompts.config.ts"] --> GetConfig["getConfig()\n(src/lib/config/index.ts)"]
    GetConfig --> GetProviders["getConfiguredProviders()\n(src/lib/auth/index.ts:110-121)"]
    GetProviders --> InitPlugins["initializePlugins()\n(src/lib/plugins/index.ts)"]
    InitPlugins --> Register["registerBuiltInAuthPlugins()\n(src/lib/plugins/auth/index.ts:11-19)"]
    Register --> Loop["getAuthPlugin(id)\nfor each provider ID\n(src/lib/plugins/index.ts)"]
    Loop --> BuildAuth["buildAuthConfig()\n(src/lib/auth/index.ts:124-143)"]
    BuildAuth --> NextAuth["NextAuth({\n adapter: CustomPrismaAdapter(),\n providers,\n session: { strategy: 'jwt' }\n})"]
```

Sources: [src/lib/auth/index.ts:109-146](), [src/lib/plugins/auth/index.ts:11-19](), [src/lib/plugins/index.ts:1-54]()

---

## `CustomPrismaAdapter` & Username Resolution

The application extends the standard `@auth/prisma-adapter` through `CustomPrismaAdapter()` defined in [src/lib/auth/index.ts:31-107]().

### Username Generation & Collision Handling

- Extracts the local part of the email address (before `@`), sanitizing it to lowercase alphanumeric and underscore characters ([src/lib/auth/index.ts:13-15]()).
- Falls back to a sanitized user `name` if the local part is too short ([src/lib/auth/index.ts:17-20]()).
- Defaults to `"user"` if all else fails ([src/lib/auth/index.ts:22-26]()).
- Ensures uniqueness at insert time by running an atomic creation loop that catches unique constraint violations (`isUniqueConstraintViolation`) and appends an incremental numeric counter ([src/lib/auth/index.ts:71-104]()).

### Unclaimed Account Claiming

CSV contributors imported via scripts are pre-created with synthetic emails (`{username}@unclaimed.prompts.chat`). When a user signs in via OAuth (e.g., GitHub using [src/lib/plugins/auth/github.ts:13-22]()), `CustomPrismaAdapter.createUser()` checks if a matching unclaimed account exists ([src/lib/auth/index.ts:44-50]()). If found, it updates the record with the authenticated email, name, and profile image, seamlessly linking contributor attribution to the new account ([src/lib/auth/index.ts:52-68]()).

Title: "CustomPrismaAdapter User Creation and Account Claiming Flow"
```mermaid
flowchart TD
    OAuth["OAuth Sign-In Event"]
    Adapter["CustomPrismaAdapter.createUser()\n(src/lib/auth/index.ts:37-105)"]
    OAuth --> Adapter
    Adapter --> Check["providedUsername exists?\n(src/lib/auth/index.ts:45)"]
    Check -- Yes --> FindUnclaimed["db.user.findUnique({ email: username@unclaimed.prompts.chat })\n(src/lib/auth/index.ts:48)"]
    FindUnclaimed --> Found{"Unclaimed User Found?"}
    Found -- Yes --> Claim["db.user.update({ id: unclaimedUser.id }, data: {...})\n(src/lib/auth/index.ts:53)"]
    Claim --> ReturnUser["Return claimed user record"]
    Found -- No --> GenerateUsername["generateBaseUsername()\n(src/lib/auth/index.ts:13)"]
    Check -- No --> GenerateUsername
    GenerateUsername --> Create["db.user.create() with collision retry\n(src/lib/auth/index.ts:81)"]
```

Sources: [src/lib/auth/index.ts:13-107](), [src/lib/plugins/auth/github.ts:13-22](), [src/lib/db-errors.ts:1-10]()

---

## JWT & Session Callbacks

Prompts.chat uses stateless JSON Web Tokens (`strategy: "jwt"`).

### JWT Callback Hydration and Validation

- During sign-in, the `jwt` callback queries the database by email to hydrate the token with `id`, `role`, `username`, `locale`, `name`, and `picture` ([src/lib/auth/index.ts:155-172]()).
- On subsequent requests, token existence is verified against `db.user` using `token.id` ([src/lib/auth/index.ts:174-179]()).
- If the user record is deleted, the session token is invalidated ([src/lib/auth/index.ts:180-184]()).
- Explicit update triggers refresh the token payload ([src/lib/auth/index.ts:186-193]()).

Title: "JWT Callback Hydration and Validation Sequence"
```sequence
participant Client as "Client Browser"
participant NextAuth as "NextAuth Framework"
participant JWTCB as "callbacks.jwt()\n(src/lib/auth/index.ts:155-196)"
participant DB as "db.user (Prisma)"

Client->>NextAuth: Request with JWT
NextAuth->>JWTCB: jwt(token, user?, trigger?)
JWTCB->>DB: db.user.findUnique({ id: token.id })
DB-->>JWTCB: User record or null

alt User exists
    JWTCB-->>NextAuth: Return refreshed token with user data
    NextAuth-->>Client: Send new JWT
else User deleted
    JWTCB-->>NextAuth: Return null (invalidate session)
    NextAuth-->>Client: Session invalidated
end
```

Sources: [src/lib/auth/index.ts:154-197]()

---

## Credentials Auth & Registration Pipeline

When the `credentials` provider is enabled, users can register via the credentials endpoint.

### Registration Implementation

- Handled by [src/app/api/auth/register/route.ts:18-83]().
- Validates payload against `registerSchema` using Zod with whitespace preprocessing ([src/app/api/auth/register/route.ts:9-16]()).
- Hashes passwords using `bcryptjs` with 12 salt rounds ([src/app/api/auth/register/route.ts:42]()).
- Enforces atomic database creation and returns `409 Conflict` on email or username collisions ([src/app/api/auth/register/route.ts:45-75]()).
- Respects the `auth.allowRegistration` configuration flag ([src/app/api/auth/register/route.ts:21-27]()).
- UI forms are unified via `AuthContent` ([src/components/auth/auth-content.tsx:24-67]()).

Sources: [src/app/api/auth/register/route.ts:1-83](), [src/components/auth/auth-content.tsx:24-67]()

---

## API Key Generation & Management

Users can manage API keys (format `pchat_*`) and MCP settings on their settings page.

### Profile & API Key Settings

- Settings page UI loaded at [src/app/settings/page.tsx:17-72]().
- API key management component: [src/components/settings/api-key-settings.tsx]().
- Profile updates handled by PATCH requests to `/api/user/profile` ([src/app/api/user/profile/route.ts:25-86]()), validating name, username, avatar, bio, and custom social links ([src/components/settings/profile-form.tsx:36-46]()). The `customLinks` field is an array of objects with `type`, `url`, and optional `label` ([src/components/user/profile-links.tsx:62-66]()).
- Successful profile updates trigger session refreshes ([src/components/settings/profile-form.tsx:155]()).

Sources: [src/app/settings/page.tsx:17-72](), [src/app/api/user/profile/route.ts:25-86](), [src/components/settings/profile-form.tsx:36-46](), [src/components/user/profile-links.tsx:62-66]()

---

## Role-Based Access Control (RBAC)

Authorization relies on the `User.role` enum (`USER` or `ADMIN`).

### Enforcing Administrative Access

Administrative endpoints enforce authorization by checking session roles:

```typescript
const session = await auth();
if (!session?.user || session.user.role !== "ADMIN") {
  return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
}
```
*(Reference: [src/app/api/admin/import-prompts/route.ts:103-108]())*

### UI Integration

- User roles dictate administrative badges in OpenGraph image generation ([src/app/[username]/opengraph-image.tsx:134-149]()).
- Access controls determine whether administrative features render in client layouts.

Sources: [src/app/api/admin/import-prompts/route.ts:103-108](), [src/app/[username]/opengraph-image.tsx:134-149](), [src/lib/auth/index.ts:160-165]()

---

## References

- NextAuth configuration & adapter: [src/lib/auth/index.ts:1-197]()
- Auth plugin registry: [src/lib/plugins/auth/index.ts:1-21]()
- GitHub OAuth provider: [src/lib/plugins/auth/github.ts:1-24]()
- Registration API endpoint: [src/app/api/auth/register/route.ts:1-83]()
- Profile API route: [src/app/api/user/profile/route.ts:1-86]()
- Settings page & Profile form: [src/app/settings/page.tsx:17-72](), [src/components/settings/profile-form.tsx:36-46]()

---

# Page: User Profiles & Settings

# User Profiles & Settings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [prisma/migrations/20251213133000_add_github_username/migration.sql](prisma/migrations/20251213133000_add_github_username/migration.sql)
- [prisma/migrations/20260127100000_add_user_bio_and_custom_links/migration.sql](prisma/migrations/20260127100000_add_user_bio_and_custom_links/migration.sql)
- [src/__tests__/api/user-profile.test.ts](src/__tests__/api/user-profile.test.ts)
- [src/__tests__/lib/plugins/auth/github.test.ts](src/__tests__/lib/plugins/auth/github.test.ts)
- [src/app/[username]/opengraph-image.tsx](src/app/[username]/opengraph-image.tsx)
- [src/app/[username]/page.tsx](src/app/[username]/page.tsx)
- [src/app/api/admin/import-prompts/route.ts](src/app/api/admin/import-prompts/route.ts)
- [src/app/api/auth/register/route.ts](src/app/api/auth/register/route.ts)
- [src/app/api/prompts/[id]/route.ts](src/app/api/prompts/[id]/route.ts)
- [src/app/api/prompts/route.ts](src/app/api/prompts/route.ts)
- [src/app/api/user/profile/route.ts](src/app/api/user/profile/route.ts)
- [src/app/categories/[slug]/page.tsx](src/app/categories/[slug]/page.tsx)
- [src/app/collection/page.tsx](src/app/collection/page.tsx)
- [src/app/feed/page.tsx](src/app/feed/page.tsx)
- [src/app/prompts/[id]/page.tsx](src/app/prompts/[id]/page.tsx)
- [src/app/settings/page.tsx](src/app/settings/page.tsx)
- [src/app/skills/page.tsx](src/app/skills/page.tsx)
- [src/app/tags/[slug]/page.tsx](src/app/tags/[slug]/page.tsx)
- [src/components/auth/register-form.tsx](src/components/auth/register-form.tsx)
- [src/components/prompts/discovery-prompts.tsx](src/components/prompts/discovery-prompts.tsx)
- [src/components/settings/profile-form.tsx](src/components/settings/profile-form.tsx)
- [src/components/user/profile-links.tsx](src/components/user/profile-links.tsx)
- [src/lib/auth/index.ts](src/lib/auth/index.ts)
- [src/lib/db-errors.ts](src/lib/db-errors.ts)
- [src/lib/plugins/auth/github.ts](src/lib/plugins/auth/github.ts)

</details>



This page explains the user profile system hosted at `/@username`, covering the user profile page structure, activity graph heatmap, pinned prompts, verification badges, profile social links, and user account settings forms. It describes the implementation in detail, including core data flow, key components, API integration, and user account uniqueness management. For related user authentication fundamentals, see [5.1. Authentication & Authorization](). For collections, feeds, and subscriptions visible on profiles, see [5.3. Collections & Feeds]().

---

## Data Model

User profile data is persisted in the `User` Prisma model with key fields supporting display and customization:

| Field | Type | Description |
|---|---|---|
| `name` | `String?` | User's display name [src/lib/auth/index.ts:169]() |
| `username` | `String` (unique) | URL-safe lowercase handle, e.g. `@alice` mapped to `alice` [src/lib/auth/index.ts:169]() |
| `avatar` | `String?` | URL for user profile image [src/lib/auth/index.ts:170]() |
| `bio` | `String?` | Short bio (max 250 chars) supporting URLs and markdown-style bold parsing [src/components/settings/profile-form.tsx:44]() |
| `customLinks` | `Json?` | Array of social/profile links `{type, url, label?}` stored as JSON [src/app/settings/page.tsx:37]() |
| `verified` | `Boolean` | Shows verification badge if true; toggleable by admins [src/app/settings/page.tsx:33]() |
| `role` | `UserRole` | Role assignment, e.g. `USER` or `ADMIN` [src/lib/auth/index.ts:166]() |
| `apiKey` | `String?` | API key for MCP authentication [src/app/settings/page.tsx:34]() |
| `githubUsername` | `String?` | Immutable GitHub username for contributor attribution [src/lib/auth/index.ts:40]() |

Sources: [src/lib/auth/index.ts:165-170](), [src/app/settings/page.tsx:25-38](), [src/components/settings/profile-form.tsx:36-46]()

---

## Profile Page (`/@username`)

The user profile page is a Next.js server component in `src/app/[username]/page.tsx`. It displays user metadata, prompt lists, pinned prompts, and an activity heatmap. This page strictly enforces the `@` prefix in URLs, returning 404 for invalid usernames.

### User Data Fetching

- The page fetches the user case-insensitively by username after stripping the `@` prefix [src/app/[username]/opengraph-image.tsx:50-51]().
- Prompt queries filter to exclude intermediate "flow" prompts and conditionally expose private prompts if viewed by the owner [src/app/[username]/page.tsx:144-148]().

### Concurrent Data Queries

Using `Promise.all`, it fetches concurrently:

- User's prompts (paginated, including related data like author, category, tags) [src/app/[username]/page.tsx:150-181]()
- Count of total prompts and upvotes received on those prompts [src/app/[username]/opengraph-image.tsx:94-100]()
- Pinned prompts sorted by order index, including nested prompt data
- Contributions, liked prompts, and user example data for rendering [src/app/[username]/page.tsx:128-133]()
- Counts for private prompts visible to the user themselves
- Activity metrics for prompts authored, prompt votes, change requests, and comments over the last year [src/app/[username]/page.tsx:183-184]()

### Metadata Generation

The `generateMetadata` function builds a user-friendly page title and description for SEO and displays the user's name or username handle [src/app/[username]/page.tsx:73-83]().

### Verification Badges & UI Features

- A verification badge (`BadgeCheck` icon) appears adjacent to the username when `user.verified` is true [src/app/[username]/page.tsx:7]().
- Pinned prompts are presented with interactive ordering and preview cards using the `PromptCard` UI component [src/app/[username]/page.tsx:18]().
- The page includes the `ActivityChartWrapper` component that visualizes user activity aggregated over a year [src/app/[username]/page.tsx:22]().

Sources: [src/app/[username]/page.tsx:7-184](), [src/app/[username]/opengraph-image.tsx:50-100]()

---

### Open Graph Image Generation

The `/@username/opengraph-image` dynamic route is handled by `src/app/[username]/opengraph-image.tsx`. It generates a custom PNG image rendered server-side with `ImageResponse` showing user name, avatar, role badges (e.g., Admin), joined date formatted, total prompt counts, and total upvotes [src/app/[username]/opengraph-image.tsx:21-109]().

Sources: [src/app/[username]/opengraph-image.tsx:21-109]()

---

### Diagram: Profile Data Resolution & Rendering Flow (Natural Language ↔ Code Entity Space)

```mermaid
graph TD
    UserRequest["HTTP Request /@username"] --> ProfileComponent["UserProfilePage in src/app/[username]/page.tsx"]
    ProfileComponent --> ValidatePrefix{"Check '@' prefix on username"}
    ValidatePrefix -- "No" --> NotFound["Invoke notFound() (404)"]
    ValidatePrefix -- "Yes" --> FetchUser["Query user by username case-insensitive using db.user.findFirst"]
    FetchUser --> PromiseAllQueries["Promise.all parallel queries: prompts, pinnedPrompts, contributions, activity"]
    PromiseAllQueries --> RenderUI["Render User Profile UI with PromptList, Pinned Prompts, ActivityChart"]
    
    OGRequest["GET /@username/opengraph-image"] --> OGModule["OGImage in src/app/[username]/opengraph-image.tsx"]
    OGModule --> DBVoteCount["db.promptVote.count aggregates votes"]
    DBVoteCount --> ImageResponseGen["Create ImageResponse with avatar, stats, badges"]
    ImageResponseGen --> ReturnPNG["Return PNG image response"]
```

Sources: [src/app/[username]/page.tsx:52-193](), [src/app/[username]/opengraph-image.tsx:21-109]()

---

## Activity Graph & Heatmap

User activity is displayed as a heatmap matrix of daily counts covering created prompts, votes given, change requests, and comments aggregated for the prior 12 months.

- The server query aggregates daily counts by date for these activities for the user.
- The `ActivityChartWrapper` component renders this data using `ActivityChart` [src/components/user/activity-chart-wrapper.tsx:1]().
- Intensity (level 0 to 4) is calculated based on max activity using `getIntensity` logic [src/components/user/activity-chart.tsx:113-120]().
- Selecting a date cell on the graph updates the page by appending a `date=YYYY-MM-DD` filter to the search params, filtering the prompt list to those created on that day [src/app/[username]/page.tsx:37]().

Sources: [src/app/[username]/page.tsx:37](), [src/components/user/activity-chart-wrapper.tsx:1](), [src/components/user/activity-chart.tsx:113-120]()

---

## Pinned Prompts & Verification Badges

- Pinned prompts are fetched in order by `db.pinnedPrompt.findMany` with includes for author, category, and tags. They are rendered as card components in a pinned section above the main prompt list.
- A verification badge (`BadgeCheck` icon from Lucide) is conditionally displayed next to the username heading when the `verified` flag is true [src/app/[username]/page.tsx:7]().

Sources: [src/app/[username]/page.tsx:7]()

---

## Settings Page (`/settings`)

The user settings page is implemented as a protected server component in `src/app/settings/page.tsx`. It:

- Verifies session using `auth()`; redirects to login if unauthenticated [src/app/settings/page.tsx:18-23]().
- Fetches the user's profile data, including `name`, `username`, `avatar`, `verified`, `apiKey`, `bio`, and `customLinks` [src/app/settings/page.tsx:25-38]().
- Passes data as props to `ProfileForm` component and conditionally includes `ApiKeySettings` if MCP features enabled [src/app/settings/page.tsx:55-68]().

Sources: [src/app/settings/page.tsx:18-71]()

---

### Diagram: Settings Page Data Flow (Natural Language ↔ Code Entity Space)

```mermaid
graph TD
    subgraph Server_Component
        SettingsPage["SettingsPage at src/app/settings/page.tsx"]
        PrismaUser["db.user.findUnique(userId)"]
    end

    subgraph Client_Components
        ProfileForm["ProfileForm in src/components/settings/profile-form.tsx"]
        ApiKeySettings["ApiKeySettings in src/components/settings/api-key-settings.tsx"]
        ProfileAPI["PATCH /api/user/profile endpoint"]
    end

    SettingsPage --> PrismaUser
    SettingsPage --> ProfileForm
    SettingsPage --> ApiKeySettings

    ProfileForm -->|JSON PATCH payload| ProfileAPI
    ProfileAPI -->|DB Update| PrismaUser
    ProfileAPI -->|200 OK| ProfileForm
    ProfileForm -->|update() triggers NextAuth session refresh| NextAuthJwt["NextAuth JWT callback refetches user"]
```

Sources: [src/app/settings/page.tsx:18-71](), [src/components/settings/profile-form.tsx:139-173](), [src/lib/auth/index.ts:155-196]()

---

## Profile Customization

### ProfileForm Component

The `ProfileForm` component (`src/components/settings/profile-form.tsx`) offers a user-editable form with fields:

- `name`, `username`, `avatar` URL, `bio`, and an array of `customLinks`
- Uses `zod` schemas for validation including username pattern (lowercase letters, numbers, underscores) and URL validity for links [src/components/settings/profile-form.tsx:30-46]().

Custom links support 5 maximum entries from types:
`website`, `github`, `twitter (X)`, `linkedin`, `instagram`, `youtube`, `twitch`, `discord`, `mastodon`, `bluesky`, and `sponsor` [src/components/settings/profile-form.tsx:31-60]().

The form includes interactive helpers to add, remove, reorder, and update custom links [src/components/settings/profile-form.tsx:113-134]().

Submitting triggers a `PATCH` request to `/api/user/profile` [src/app/api/user/profile/route.ts:25-86]() and initiates a NextAuth session refresh to update cached session info [src/components/settings/profile-form.tsx:155]().

Sources: [src/components/settings/profile-form.tsx:30-173](), [src/app/api/user/profile/route.ts:25-86]()

### ProfileLinks Component

`ProfileLinks` (in `src/components/user/profile-links.tsx`) renders:

- The user's bio text parsed for URLs and `**bold**` syntax, transforming links into anchor tags and bold text with `<strong>` elements [src/components/user/profile-links.tsx:94-139]().
- Social media and personal links using platform-specific icons mapped in the `linkIcons` record, including custom SVG icons for X, Discord, Mastodon, Bluesky, and others [src/components/user/profile-links.tsx:15-86]().

Sources: [src/components/user/profile-links.tsx:15-139]()

---

## Implementation Details

### Username Generation & Account Claiming

- The `generateBaseUsername` function creates a base username from the user's email or name during account creation, ensuring minimum length and valid characters [src/lib/auth/index.ts:13-28]().
- The custom Prisma adapter (`CustomPrismaAdapter`) attempts atomic username creation with retries for uniqueness, appending an incremental numeric suffix on conflict [src/lib/auth/index.ts:31-107]().
- Unclaimed accounts are created as pseudo-users with email addresses in the format `username@unclaimed.prompts.chat` during CSV prompt imports. Upon user login, if the chosen username matches an unclaimed account, the adapter claims (updates) that account with the logged-in user's email and data [src/lib/auth/index.ts:45-68](), [src/app/api/admin/import-prompts/route.ts:139-173]().

Sources: [src/lib/auth/index.ts:13-107](), [src/app/api/admin/import-prompts/route.ts:139-173]()

### Pinned Prompts, Activity Data, and Profile Metadata

- Fetching of pinned prompts and metadata is centralized in the profile page component using Prisma queries with includes for nested relationships and counts [src/app/[username]/page.tsx:150-181]().
- Activity over the past year is computed from prompt creation, votes, change requests, and comments tied to the user [src/app/[username]/page.tsx:183-184]().
- The Open Graph image generation composes graphical components server-side for social sharing cards [src/app/[username]/opengraph-image.tsx:21-109]().

Sources: [src/app/[username]/page.tsx:150-184](), [src/app/[username]/opengraph-image.tsx:21-109]()

---

### Diagram: Profile Update Lifecycle & Auth Integration

```mermaid
sequenceDiagram
    participant ProfileForm as ProfileForm (src/components/settings/profile-form.tsx)
    participant ProfileApi as PATCH /api/user/profile (src/app/api/user/profile/route.ts)
    participant DB as Prisma db.user.update
    participant NextAuth as NextAuth JWT callback (src/lib/auth/index.ts)

    ProfileForm->>ProfileApi: Send PATCH with updated profile data
    ProfileApi->>DB: Update user record in database
    DB-->>ProfileApi: Return updated user data
    ProfileApi-->>ProfileForm: Return success response
    ProfileForm->>NextAuth: Call update() to refresh NextAuth session
    NextAuth->>DB: Query updated user info for JWT & session
    NextAuth-->>ProfileForm: Return updated session data
```

Sources: [src/components/settings/profile-form.tsx:139-173](), [src/app/api/user/profile/route.ts:25-86](), [src/lib/auth/index.ts:155-196]()

---

## Profile Summary Table

| Feature | Code Location | Description |
|---|---|---|
| Public profile | `src/app/[username]/page.tsx` | Server component rendering profile with username validation, prompt/page queries |
| Open Graph image | `src/app/[username]/opengraph-image.tsx` | Dynamic image generation of profile card and stats for social sharing |
| Verification badge | `user.verified` boolean field | Controls visibility of `BadgeCheck` icon on profile header |
| Activity graph | `ActivityChart` & `ActivityChartWrapper` components | Rendering of yearly contribution heatmap with clickable date filters |
| Social links & bio | `ProfileLinks` component | Renders parsed markdown and social links using platform icons |
| Settings UI | `src/app/settings/page.tsx` + `ProfileForm` | Protected user settings, profile edit form with validations and API integration |
| Username uniqueness | `CustomPrismaAdapter` in auth plugin | Atomic username creation with collision retry and unclaimed account claiming |
| CSV import linking | Admin import route (`src/app/api/admin/import-prompts/route.ts`) | Creates pseudo-users for contributors by username/email format |

Sources: [src/app/[username]/page.tsx](), [src/app/[username]/opengraph-image.tsx](), [src/components/settings/profile-form.tsx](), [src/components/user/profile-links.tsx](), [src/app/settings/page.tsx](), [src/lib/auth/index.ts](), [src/app/api/admin/import-prompts/route.ts]()

---

# Page: Collections & Feeds

# Collections & Feeds

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/[username]/page.tsx](src/app/[username]/page.tsx)
- [src/app/api/prompts/[id]/route.ts](src/app/api/prompts/[id]/route.ts)
- [src/app/api/prompts/route.ts](src/app/api/prompts/route.ts)
- [src/app/categories/[slug]/page.tsx](src/app/categories/[slug]/page.tsx)
- [src/app/collection/page.tsx](src/app/collection/page.tsx)
- [src/app/feed/page.tsx](src/app/feed/page.tsx)
- [src/app/prompts/[id]/page.tsx](src/app/prompts/[id]/page.tsx)
- [src/app/skills/page.tsx](src/app/skills/page.tsx)
- [src/app/tags/[slug]/page.tsx](src/app/tags/[slug]/page.tsx)
- [src/components/comments/comment-form.tsx](src/components/comments/comment-form.tsx)
- [src/components/mcp/mcp-config-tabs.tsx](src/components/mcp/mcp-config-tabs.tsx)
- [src/components/mcp/mcp-server-popup.tsx](src/components/mcp/mcp-server-popup.tsx)
- [src/components/prompts/add-to-collection-button.tsx](src/components/prompts/add-to-collection-button.tsx)
- [src/components/prompts/discovery-prompts.tsx](src/components/prompts/discovery-prompts.tsx)
- [src/components/prompts/translate-button.tsx](src/components/prompts/translate-button.tsx)
- [src/hooks/use-mobile.ts](src/hooks/use-mobile.ts)

</details>



## Purpose and Scope

The Collections & Feeds system provides mechanisms for users to organize, track, and discover prompts through structured bookmarking, subscription feeds, notification tracking, and specialized discovery pathways:

1. **Collections**: Personal bookmarked prompt lists accessible at `/collection` [src/app/collection/page.tsx:17-72]() via `AddToCollectionButton` [src/app/prompts/[id]/page.tsx:38]().
2. **Personalized Feeds**: Category subscription-based feeds at `/feed` [src/app/feed/page.tsx:19-105]().
3. **Specialized Discovery**: Dedicated feeds for Agent Skills (`/skills`) and Prompt Workflows (`/workflows`).
4. **Category & Tag Browsing**: Categorized views at `/categories/[slug]` [src/app/categories/[slug]/page.tsx:71-110]() and `/tags/[slug]` [src/app/tags/[slug]/page.tsx:58-85]().
5. **Curated Discovery**: Automated sections for featured, trending, latest, and most upvoted prompts via `DiscoveryPrompts` [src/components/prompts/discovery-prompts.tsx:16-134]().

Sources: [src/app/collection/page.tsx:17-72](), [src/app/feed/page.tsx:19-105](), [src/app/categories/[slug]/page.tsx:71-110](), [src/app/tags/[slug]/page.tsx:58-85](), [src/components/prompts/discovery-prompts.tsx:16-134](), [src/app/prompts/[id]/page.tsx:38]()

---

## System Architecture

### Component Organization & Data Flow

```mermaid
graph TB
    subgraph "Natural Language Space"
        Bookmarks["Bookmarked Prompts"]
        SubscribedCategories["Subscribed Categories"]
        AgentSkills["Agent Skills Feed"]
        PromptChains["Prompt Workflows Feed"]
    end

    subgraph "Code Entity Space"
        AuthSession["auth()"] --> CollectionPage["src/app/collection/page.tsx"]
        AuthSession --> FeedPage["src/app/feed/page.tsx"]
        
        CollectionPage --> DbCollection["db.collection.findMany"]
        FeedPage --> DbSubs["db.categorySubscription.findMany"]
        FeedPage --> DbPrompts["db.prompt.findMany"]
        
        DbCollection --> Bookmarks
        DbSubs --> SubscribedCategories
    end
```

Sources: [src/app/collection/page.tsx:17-64](), [src/app/feed/page.tsx:29-54]()

---

## Collections System

The collection system enables users to bookmark prompts, maintaining a personalized list of saved items at `/collection` [src/app/collection/page.tsx:17-72]().

### Collection Data Flow

```mermaid
graph LR
    subgraph "Natural Language Space"
        UserBookmark["User Bookmarks Prompt"] --> CollectionRoute["Collection Database Table"]
        CollectionRoute --> CollectionView["Collection Page UI"]
    end

    subgraph "Code Entity Space"
        SessionCheck["auth()"] --> FindManyCollection["db.collection.findMany"]
        FindManyCollection --> FilterDeleted["Filter: prompt.deletedAt == null"]
        FilterDeleted --> MapPrompts["Map votes & contributor counts"]
        MapPrompts --> RenderList["PromptList component"]
    end
```

### Implementation Details

- **Authentication Check**: Validates user sessions via `auth()` [src/app/collection/page.tsx:19-23](). If unauthenticated, redirects to `/login`.
- **Database Query**: Queries `db.collection.findMany` filtering by `userId` and fetching relational include properties (author, category, tags, and vote/contributor counts) [src/app/collection/page.tsx:25-63]().
- **Validation**: Filters out deleted prompts where `prompt.deletedAt` is non-null [src/app/collection/page.tsx:65-66]().

| Function / Component | File Path | Role |
| :------------------- | :-------- | :--- |
| `CollectionPage` | `src/app/collection/page.tsx` | Main server component rendering user bookmarks |
| `db.collection.findMany` | `src/app/collection/page.tsx` | Prisma query fetching user's saved prompt IDs and relations |

Sources: [src/app/collection/page.tsx:17-72]()

---

## Personalized Feed System

The personalized feed aggregates prompts from categories that an authenticated user has subscribed to, served at `/feed` [src/app/feed/page.tsx:19-105]().

### Feed Generation Logic

1. **Authentication Check**: Requires a valid user session, redirecting to login otherwise [src/app/feed/page.tsx:21-26]().
2. **Subscription Lookup**: Queries `db.categorySubscription.findMany` to retrieve category IDs associated with the user [src/app/feed/page.tsx:29-42]().
3. **Prompt Filtering**: If subscriptions exist, queries public, non-deleted prompts (`NON_BOT_PROMPTS`) matching the subscribed category IDs, ordered by creation date descending with a take limit of 30 [src/app/feed/page.tsx:45-88]().
4. **Fallback Handling**: If no subscriptions are active, displays category suggestion badges allowing quick onboarding [src/app/feed/page.tsx:149-173]().

```mermaid
graph LR
    subgraph "Natural Language Space"
        UserSubs["User Category Subscriptions"] --> FeedQuery["Personalized Feed"]
        FeedQuery --> FeedUI["Feed Page UI"]
    end

    subgraph "Code Entity Space"
        AuthFeed["auth()"] --> SubQuery["db.categorySubscription.findMany"]
        SubQuery --> PromptQuery["db.prompt.findMany"]
        PromptQuery --> WhereClause["categoryId in subscribedCategoryIds"]
        WhereClause --> RenderFeed["PromptList / Suggestions"]
    end
```

Sources: [src/app/feed/page.tsx:19-176]()

---

## Category & Tag Browsing

Users can browse collections filtered by specific taxonomy criteria:

- **Categories (`/categories/[slug]`)**:
  - Resolves category records via `db.category.findUnique` [src/app/categories/[slug]/page.tsx:79-89]().
  - Checks subscription status using `db.categorySubscription.findUnique` [src/app/categories/[slug]/page.tsx:98-107]().
  - Supports sorting parameters (`newest`, `oldest`, `most_upvoted`, `most_contributors`) [src/app/categories/[slug]/page.tsx:112-123]().
- **Tags (`/tags/[slug]`)**:
  - Resolves tag metadata via `db.tag.findUnique` [src/app/tags/[slug]/page.tsx:67-69]().
  - Queries prompts associated with the tag via `tagPromptsWhere` [src/app/tags/[slug]/page.tsx:77-85]().

Sources: [src/app/categories/[slug]/page.tsx:71-123](), [src/app/tags/[slug]/page.tsx:58-85]()

---

## Global Discovery & Trending

The `DiscoveryPrompts` component aggregates multi-criteria discovery lists on the homepage and discovery routes [src/components/prompts/discovery-prompts.tsx:16-134]().

| Feed Section | Prisma Query Criteria | Ordering |
| :----------- | :-------------------- | :------- |
| **Trending** | `trendingPromptListWhere()` | `trendingUntil: desc`, `createdAt: desc` [src/components/prompts/discovery-prompts.tsx:55-60]() |
| **Featured** | `isFeatured: true`, public non-bot prompts | `featuredAt: desc` [src/components/prompts/discovery-prompts.tsx:62-73]() |
| **Today's Most Upvoted** | Votes created >= midnight today | `votes: _count: desc` [src/components/prompts/discovery-prompts.tsx:75-96]() |
| **Latest** | Public non-bot prompts | `createdAt: desc` [src/components/prompts/discovery-prompts.tsx:97-107]() |
| **Recently Updated** | Public non-bot prompts | `updatedAt: desc` [src/components/prompts/discovery-prompts.tsx:108-118]() |
| **Most Contributed** | Public non-bot prompts | `contributors: _count: desc` [src/components/prompts/discovery-prompts.tsx:119-133]() |

Sources: [src/components/prompts/discovery-prompts.tsx:16-134]()

---

# Page: Social Features

# Social Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/__tests__/components/classifiers-ui.test.tsx](src/__tests__/components/classifiers-ui.test.tsx)
- [src/__tests__/components/upvote-ui.test.tsx](src/__tests__/components/upvote-ui.test.tsx)
- [src/__tests__/db/classifiers.db.test.ts](src/__tests__/db/classifiers.db.test.ts)
- [src/app/classifiers/[slug]/page.tsx](src/app/classifiers/[slug]/page.tsx)
- [src/app/classifiers/page.tsx](src/app/classifiers/page.tsx)
- [src/app/promptmasters/page.tsx](src/app/promptmasters/page.tsx)
- [src/components/classifiers/classifier-cards.tsx](src/components/classifiers/classifier-cards.tsx)
- [src/components/classifiers/classifier-catalog.tsx](src/components/classifiers/classifier-catalog.tsx)
- [src/components/promptmasters/promptmasters-content.tsx](src/components/promptmasters/promptmasters-content.tsx)
- [src/components/prompts/filter-context.tsx](src/components/prompts/filter-context.tsx)
- [src/components/prompts/upvote-button.tsx](src/components/prompts/upvote-button.tsx)
- [src/lib/classifiers/store.ts](src/lib/classifiers/store.ts)

</details>



This page documents the social feature implementations for prompts.chat, including voting/upvoting, comments, promptmasters leaderboard, contributor attribution, and user examples. These features enable users to interact, collaborate, and contribute to the AI prompt library community.

---

## Overview

The social features system supports community engagement and contributor recognition over prompts. The core features are managed through dedicated API endpoints, Prisma database models, and React frontend components:

| Feature | Database Model | API Endpoint | Frontend Component |
| :--- | :--- | :--- | :--- |
| Upvotes | `PromptVote` | `POST/DELETE /api/prompts/:id/vote` [src/app/api/prompts/[id]/vote/route.ts:7-116]() | `UpvoteButton` [src/components/prompts/upvote-button.tsx:38-48]() |
| Comments | `Comment`, `CommentNotification` | `POST/GET /api/prompts/:id/comments` | `CommentSection` [src/app/classifiers/[slug]/page.tsx:23-23]() |
| Notifications | `CommentNotification` | `GET/POST /api/user/notifications` | `NotificationBell` |
| Promptmasters Leaderboard | Aggregated from `PromptVote` and `User` | `GET /api/leaderboard` | `PromptmastersContent` [src/components/promptmasters/promptmasters-content.tsx:151-157]() |
| Contributor Attribution | `ChangeRequest`, `PromptVersion`, contributors relation | `POST /api/prompts/:id/changes` [src/app/api/prompts/[id]/changes/route.ts:13-89]() and versions [src/app/api/prompts/[id]/versions/route.ts:13-110]() | `ChangeRequestForm`, `VersionHistory` [src/app/classifiers/[slug]/page.tsx:35-35]() |
| User Examples | `UserPromptExample` | `POST/GET/DELETE /api/prompts/:id/examples` [src/app/api/prompts/[id]/examples/route.ts:12-161]() | `UserExamplesSection` |
| Sharing | N/A | Client-side utilities | `ShareDropdown` [src/components/prompts/share-dropdown.tsx:37-75]() |

All social interactions enforce prompt privacy and access control using `checkPromptAccess` [src/lib/prompt-access.ts:28-49]() to allow interactions only on public or authorized private prompts.

Sources: [src/lib/prompt-access.ts:1-49](), [src/app/api/prompts/[id]/vote/route.ts:7-116](), [src/components/prompts/upvote-button.tsx:38-48](), [src/components/promptmasters/promptmasters-content.tsx:151-157](), [src/app/api/prompts/[id]/changes/route.ts:13-89](), [src/app/api/prompts/[id]/versions/route.ts:13-110](), [src/app/api/prompts/[id]/examples/route.ts:12-161](), [src/components/prompts/share-dropdown.tsx:37-75]()

---

## Upvoting System

Community upvotes help surface the best prompts and generate a leaderboard to recognize top contributors.

### Diagram: Upvoting & Leaderboard Architecture

```mermaid
graph TD
    subgraph NaturalLanguageSpace
        UserVotes["User clicks Upvote"]
        VoteCountDisplay["Show Upvote Count"]
        LoginPrompt["Login Required Modal"]
        LeaderboardView["User Leaderboard Display"]
    end

    subgraph CodeEntitySpace
        UpvoteButton["UpvoteButton src/components/prompts/upvote-button.tsx"]
        VoteAPI_POST["POST /api/prompts/[id]/vote src/app/api/prompts/[id]/vote/route.ts"]
        VoteAPI_DELETE["DELETE /api/prompts/[id]/vote src/app/api/prompts/[id]/vote/route.ts"]
        LeaderboardAPI["GET /api/leaderboard"]
        PromptVoteModel["db.promptVote Prisma Model"]
        AnalyticsLogger["analyticsPrompt src/components/prompts/upvote-button.tsx"]
        PromptmastersContent["PromptmastersContent src/components/promptmasters/promptmasters-content.tsx"]
        PromptmastersPage["PromptmastersPage src/app/promptmasters/page.tsx"]
    end

    UserVotes --> UpvoteButton
    UpvoteButton -- "Requires login check" --> LoginPrompt
    UpvoteButton -- "Fetch POST vote" --> VoteAPI_POST
    VoteAPI_POST -- "Validate access & create vote" --> PromptVoteModel
    VoteAPI_POST -- "Return updated count" --> UpvoteButton
    UpvoteButton -- "Fetch DELETE vote" --> VoteAPI_DELETE
    VoteAPI_DELETE -- "Validate access & delete vote" --> PromptVoteModel
    VoteAPI_DELETE -- "Return updated count" --> UpvoteButton
    UpvoteButton --> VoteCountDisplay
    UpvoteButton --> AnalyticsLogger
    LeaderboardAPI -- "Aggregate votes for leaderboard" --> PromptmastersContent
    PromptmastersPage --> PromptmastersContent
    PromptmastersContent --> LeaderboardView
```

Sources: [src/components/prompts/upvote-button.tsx:1-193](), [src/app/api/prompts/[id]/vote/route.ts:1-117](), [src/components/promptmasters/promptmasters-content.tsx:151-247](), [src/app/promptmasters/page.tsx:15-33](), [src/lib/prompt-access.ts:28-49]()

### UpvoteButton Component

The `UpvoteButton` component [src/components/prompts/upvote-button.tsx:38-48]() is a client-side React component responsible for handling user interactions related to upvoting.

- It maintains local state for whether the user has voted (`isVoted`) and the total vote count (`voteCount`) [src/components/prompts/upvote-button.tsx:52-54]().
- Handles optimistic UI updates and displays a login dialog when unauthenticated users attempt to vote [src/components/prompts/upvote-button.tsx:57-61]().
- Supports multiple layout sizes (`sm`, `default`, `circular`) [src/components/prompts/upvote-button.tsx:31-31]().
- Invokes client-side analytics tracking upon voting or removing votes using `analyticsPrompt.upvote` and `analyticsPrompt.removeUpvote` [src/components/prompts/upvote-button.tsx:80-84]().
- The visual representation of the upvote count and icon is handled by the `UpvoteCount` [src/components/prompts/upvote-count.tsx:24-32]() and `UpvoteIcon` [src/components/prompts/upvote-count.tsx:9-16]() components.

Sources: [src/components/prompts/upvote-button.tsx:1-193](), [src/components/prompts/upvote-count.tsx:1-32]()

### API Route & Data Model

The upvoting functionality is managed by the `/api/prompts/[id]/vote` API route.

- `POST /api/prompts/[id]/vote`: Authenticated users create a `PromptVote` record if none exists [src/app/api/prompts/[id]/vote/route.ts:7-69]().
- `DELETE /api/prompts/[id]/vote`: Authenticated users delete their existing vote [src/app/api/prompts/[id]/vote/route.ts:72-116]().
- Access is validated by `checkPromptAccess` [src/lib/prompt-access.ts:28-49]() to ensure proper prompt visibility [src/app/api/prompts/[id]/vote/route.ts:28-29]().
- The `PromptVote` Prisma model uses a composite unique key (`userId`, `promptId`) to enforce single voting limits per user per prompt.
- The Leaderboard API `/api/leaderboard` caches results, groups votes by prompt authors, and supports period filtering (`all`, `month`, `week`) as consumed by `PromptmastersContent` [src/components/promptmasters/promptmasters-content.tsx:158-178]().

Sources: [src/app/api/prompts/[id]/vote/route.ts:1-117](), [src/lib/prompt-access.ts:28-49](), [src/components/promptmasters/promptmasters-content.tsx:151-247]()

---

## Promptmasters Leaderboard

The Promptmasters Leaderboard displays top contributors based on prompt upvotes.

### Implementation Details

- The `/promptmasters` page [src/app/promptmasters/page.tsx:15-33]() renders the `PromptmastersContent` component [src/components/promptmasters/promptmasters-content.tsx:151-247]().
- `PromptmastersContent` [src/components/promptmasters/promptmasters-content.tsx:151-247]() fetches leaderboard data for "all time", "this month", and "this week" from the `/api/leaderboard` endpoint [src/components/promptmasters/promptmasters-content.tsx:159-178]().
- Users can sort the leaderboard by total upvotes or upvotes per prompt using the `sortMode` state [src/components/promptmasters/promptmasters-content.tsx:156-156]() and `LeaderboardList` component [src/components/promptmasters/promptmasters-content.tsx:79-87]().
- Top ranks (1st, 2nd, 3rd) are visually distinguished with `Trophy`, `Medal`, and `Award` icons via the `RankBadge` component [src/components/promptmasters/promptmasters-content.tsx:64-77]().
- Each entry links to the user's profile page (`/@username`) [src/components/promptmasters/promptmasters-content.tsx:110-113]().
- Loading states are handled with `LeaderboardSkeleton` [src/components/promptmasters/promptmasters-content.tsx:46-62]().

Sources: [src/app/promptmasters/page.tsx:15-33](), [src/components/promptmasters/promptmasters-content.tsx:1-247]()

---

## Comments and Notifications

Users can comment on prompts, reply to other comments, and receive notifications about new interactions.

### Diagram: Comment & Notification Flow

```mermaid
graph TD
    subgraph NaturalLanguageSpace
        UserPostsComment["User posts comment or reply"]
        CommentsVisible["Comments displayed on prompt page"]
        NotificationsIcon["Notification Bell with Badge"]
        NotificationsDropdown["Notification Dropdown List"]
        ReadStatus["Mark notifications as read"]
    end

    subgraph CodeEntitySpace
        CommentSectionComponent["CommentSection component"]
        CommentAPI_POST["POST /api/prompts/[id]/comments"]
        CommentAPI_GET["GET /api/prompts/[id]/comments"]
        CommentModel["db.comment Prisma Model"]
        NotificationBellComponent["NotificationBell component"]
        NotificationAPI_GET["GET /api/user/notifications"]
        NotificationAPI_POST["POST /api/user/notifications"]
        CommentNotificationModel["db.commentNotification Prisma Model"]
        CheckPromptAccessUtil["checkPromptAccess src/lib/prompt-access.ts"]
        AnimatedDateComponent["AnimatedDate src/components/ui/animated-date.tsx"]
    end

    UserPostsComment --> CommentSectionComponent
    CommentSectionComponent -- "POST new comment" --> CommentAPI_POST
    CommentAPI_POST -- "Validate prompt access" --> CheckPromptAccessUtil
    CommentAPI_POST --> CommentModel
    CommentAPI_POST --> CommentNotificationModel
    CommentSectionComponent -- "GET comments" --> CommentAPI_GET
    CommentAPI_GET -- "Validate access" --> CheckPromptAccessUtil
    CommentAPI_GET --> CommentModel
    CommentSectionComponent --> CommentsVisible
    NotificationBellComponent -- "GET notifications" --> NotificationAPI_GET
    NotificationAPI_GET --> CommentNotificationModel
    NotificationAPI_GET --> NotificationBellComponent
    NotificationBellComponent --> NotificationsIcon
    NotificationBellComponent --> NotificationsDropdown
    NotificationsDropdown -- "Mark notifications read" --> NotificationAPI_POST
    NotificationAPI_POST --> CommentNotificationModel
    NotificationsDropdown --> AnimatedDateComponent
```

Sources: [src/lib/prompt-access.ts:28-49](), [src/components/ui/animated-date.tsx:12-46]()

---

## Contributor Attribution

The system tracks and credits users who contribute prompt improvements via change requests and versioning.

### Change Requests Workflow

- Contributors submit proposed changes using `POST /api/prompts/[id]/changes` [src/app/api/prompts/[id]/changes/route.ts:13-89]().
- The prompt owner reviews and approves or rejects change requests via `PATCH /api/prompts/[id]/changes/[changeId]` [src/app/api/prompts/[id]/changes/[changeId]/route.ts:12-176]().
- Upon approval, a database transaction creates:
  1. A new `PromptVersion` record with the updated content and a `changeNote` crediting the contributor [src/app/api/prompts/[id]/changes/[changeId]/route.ts:134-142]().
  2. Updates the main `Prompt` record content and title [src/app/api/prompts/[id]/changes/[changeId]/route.ts:144-153]().
  3. Connects the contributor user ID in the prompt's many-to-many `contributors` relationship [src/app/api/prompts/[id]/changes/[changeId]/route.ts:149-152]().

Sources: [src/app/api/prompts/[id]/changes/route.ts:13-89](), [src/app/api/prompts/[id]/changes/[changeId]/route.ts:12-176](), [src/app/api/prompts/[id]/versions/route.ts:13-110]()

---

## User Examples

Users can upload and share example media outputs generated by prompts for `IMAGE` and `VIDEO` prompt types.

### Diagram: User Examples Sequence

```mermaid
sequenceDiagram
    participant UserClient as "User UI"
    participant ExamplesAPI as "API /api/prompts/[id]/examples"
    participant DB as "db Prisma Client"
    participant Auth as "auth NextAuth"
    participant AccessCheck as "checkPromptAccess"

    UserClient->>ExamplesAPI: POST Media URL and Comment
    ExamplesAPI->>Auth: Validate user session
    Auth-->>ExamplesAPI: Return session
    ExamplesAPI->>ExamplesAPI: Validate prompt type and privacy
    ExamplesAPI->>DB: Insert userPromptExample record
    DB-->>ExamplesAPI: Created example with user info
    ExamplesAPI-->>UserClient: Return new example JSON

    UserClient->>ExamplesAPI: GET examples list
    ExamplesAPI->>AccessCheck: Verify prompt access
    AccessCheck-->>ExamplesAPI: Allowed or Denied
    ExamplesAPI->>DB: Query examples with user data
    DB-->>ExamplesAPI: Return list
    ExamplesAPI-->>UserClient: Return examples JSON

    UserClient->>ExamplesAPI: DELETE example by exampleId
    ExamplesAPI->>Auth: Validate user session
    Auth-->>ExamplesAPI: Return session
    ExamplesAPI->>DB: Find example ownership
    DB-->>ExamplesAPI: Return example record
    ExamplesAPI->>ExamplesAPI: Check if user is owner or admin
    ExamplesAPI->>DB: Delete example record
    DB-->>ExamplesAPI: Deleted confirmation
    ExamplesAPI-->>UserClient: Return deletion success
```

Sources: [src/app/api/prompts/[id]/examples/route.ts:1-161](), [src/lib/prompt-access.ts:28-49]()

### Constraints and Security

- Supported exclusively for prompt types `IMAGE` and `VIDEO` [src/app/api/prompts/[id]/examples/route.ts:26-29]().
- Examples for private prompts can only be added by the prompt owner [src/app/api/prompts/[id]/examples/route.ts:80-82]().
- Example listing and mutating operations enforce prompt privacy checks [src/app/api/prompts/[id]/examples/route.ts:23-24]().
- Deletion is restricted to the example creator or users with `ADMIN` roles [src/app/api/prompts/[id]/examples/route.ts:147-150]().

Sources: [src/app/api/prompts/[id]/examples/route.ts:1-161]()

---

## Social Sharing and Temporal UI

The platform provides UI components to share prompt links easily and display timestamps in an interactive manner.

### Components

- `ShareDropdown`: Generates pre-filled URLs for social networks such as Twitter/X and Hacker News [src/components/prompts/share-dropdown.tsx:37-75]().
- `AnimatedDate`: Displays relative time formatting by default and transitions smoothly to show exact date and time strings on hover [src/components/ui/animated-date.tsx:12-46]().

Sources: [src/components/prompts/share-dropdown.tsx:37-75](), [src/components/ui/animated-date.tsx:12-46]()

---

## Diagram: Social Features Summary Architecture

```mermaid
flowchart LR
    subgraph NaturalLanguageSpace["User-visible concepts"]
        VoteUser["Upvote Prompt"]
        CommentUser["Comment and Reply on Prompt"]
        NotificationUser["Receive Notifications"]
        ContribUser["Contribute Changes and Attribution"]
        ExampleUser["Add or View Prompt Example Media"]
        ShareUser["Share Prompt Link"]
        LeaderboardUser["View Promptmasters Leaderboard"]
    end

    subgraph CodeEntitySpace["Key Code Entities and Routes"]
        UpvoteButton["UpvoteButton src/components/prompts/upvote-button.tsx"]
        VoteAPI["/api/prompts/[id]/vote"]
        PromptVote["db.promptVote model"]

        CommentSection["CommentSection component"]
        CommentAPI["/api/prompts/[id]/comments"]
        CommentModel["db.comment model"]
        NotificationBell["NotificationBell component"]
        NotificationAPI["/api/user/notifications"]
        CommentNotificationModel["db.commentNotification model"]

        ChangeRequestAPI["/api/prompts/[id]/changes"]
        ChangeRequestReviewAPI["/api/prompts/[id]/changes/[changeId]"]
        PromptVersionAPI["/api/prompts/[id]/versions"]
        ContributorsRelation["Prompt.contributors relation"]

        UserExamplesAPI["/api/prompts/[id]/examples"]
        UserPromptExampleModel["db.userPromptExample model"]

        ShareDropdownComponent["ShareDropdown src/components/prompts/share-dropdown.tsx"]
        AnimatedDateComponent["AnimatedDate src/components/ui/animated-date.tsx"]

        LeaderboardAPI["/api/leaderboard"]
        PromptmastersContent["PromptmastersContent src/components/promptmasters/promptmasters-content.tsx"]
        PromptmastersPage["PromptmastersPage src/app/promptmasters/page.tsx"]
    end

    VoteUser --> UpvoteButton --> VoteAPI --> PromptVote
    CommentUser --> CommentSection --> CommentAPI --> CommentModel
    NotificationUser --> NotificationBell --> NotificationAPI --> CommentNotificationModel
    ContribUser --> ChangeRequestAPI & ChangeRequestReviewAPI --> PromptVersionAPI & ContributorsRelation
    ExampleUser --> UserExamplesAPI --> UserPromptExampleModel
    ShareUser --> ShareDropdownComponent
    VoteUser --> LeaderboardUser
    LeaderboardUser --> PromptmastersPage --> PromptmastersContent --> LeaderboardAPI

    AnimatedDateComponent -.-> CommentSection
    AnimatedDateComponent -.-> NotificationBell
```

Sources: [src/components/prompts/upvote-button.tsx:1-193](), [src/app/api/prompts/[id]/vote/route.ts:1-117](), [src/components/promptmasters/promptmasters-content.tsx:151-247](), [src/app/promptmasters/page.tsx:15-33](), [src/app/api/prompts/[id]/changes/[changeId]/route.ts:12-176](), [src/app/api/prompts/[id]/changes/route.ts:13-89](), [src/app/api/prompts/[id]/examples/route.ts:1-161](), [src/components/prompts/share-dropdown.tsx:37-75](), [src/components/ui/animated-date.tsx:12-46](), [src/lib/prompt-access.ts:1-49]()

---

# Page: Content Discovery

# Content Discovery

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/bots/page.tsx](src/app/bots/page.tsx)
- [src/app/categories/(index)/page.tsx](src/app/categories/(index)/page.tsx)
- [src/app/discover/page.tsx](src/app/discover/page.tsx)
- [src/app/sitemap.ts](src/app/sitemap.ts)
- [src/app/tags/(index)/page.tsx](src/app/tags/(index)/page.tsx)
- [src/components/seo/structured-data.tsx](src/components/seo/structured-data.tsx)

</details>



Content Discovery is the parent system that coordinates how users search, browse, filter, and explore prompts across the platform. It unifies several routing paths, algorithmic matching routines, and UI presentation components. This page provides a high-level architectural overview of these discovery mechanisms; for implementation-specific details, refer to the child pages:

- **[Homepage & Landing](#6.1)** — Document homepage component with hero section, featured prompts, achievements, testimonials, sponsors, and `useCloneBranding` conditional rendering
- **[Categories & Tags](#6.2)** — Explain hierarchical category system, tag system with colors, pinned categories, and category subscription mechanism
- **[Search Systems](#6.3)** — Document keyword search with comma-separated terms, AI semantic search with OpenAI embeddings, and search result ranking
- **[Curated Discovery](#6.4)** — Explain `DiscoveryPrompts` component, featured prompts, trending, today's most upvoted, latest, and widget cards
- **[SEO & Social Metadata](#6.5)** — Document structured data components, `sitemap.ts`, `robots.ts`, opengraph/twitter image generation, and analytics instrumentation

---

## Discovery Pathways & Route Architecture

The discovery system maps user navigation intents expressed in natural language or UI interactions (like browsing categories, filtering tags, or searching keywords) to concrete Next.js route handlers and UI components. These handlers use Prisma ORM queries to retrieve matching prompt data from the database.

### Diagram: Discovery Route Architecture
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        NLHome["HomepageAndHeroFeed"]
        NLCategories["CategoryDomainBrowsing"]
        NLTags["TagTopicFiltering"]
        NLSearch["KeywordAndSemanticSearch"]
        NLFeed["PersonalizedSubscribedFeed"]
        NLBots["BotListings"]
        NLClassifiers["ClassifierListings"]
    end

    subgraph "CodeEntitySpace"
        RouteHome["src/app/page.tsx"]
        RouteCategories["src/app/categories/(index)/page.tsx"]
        RouteTags["src/app/tags/(index)/page.tsx"]
        RoutePrompts["src/app/prompts/page.tsx"]
        RouteFeed["src/app/feed/page.tsx"]
        RouteBots["src/app/bots/page.tsx"]
        RouteClassifiers["src/app/classifiers/page.tsx"]
        
        DiscoveryComp["DiscoveryPrompts<br>src/components/prompts/discovery-prompts.tsx"]
        CatFilters["CategoryFilters<br>src/components/categories/category-filters.tsx"]
        InfiniteList["InfinitePromptList<br>src/components/prompts/infinite-prompt-list.tsx"]
        BotFiltersComp["BotFilters<br>src/components/bots/bot-filters.tsx"]
        
        PrismaClient["PrismaClient<br>src/lib/db.ts"]
    end

    NLHome --> RouteHome
    NLCategories --> RouteCategories
    NLTags --> RouteTags
    NLSearch --> RoutePrompts
    NLFeed --> RouteFeed
    NLBots --> RouteBots
    NLClassifiers --> RouteClassifiers

    RouteHome --> DiscoveryComp
    RouteCategories --> CatFilters
    RoutePrompts --> InfiniteList
    RouteBots --> BotFiltersComp

    DiscoveryComp --> PrismaClient
    CatFilters --> PrismaClient
    InfiniteList --> PrismaClient
    RouteFeed --> PrismaClient
    BotFiltersComp --> PrismaClient
    RouteClassifiers --> PrismaClient
```

This structure shows how high-level content discovery concepts — homepage curation, category/tag-based browsing, semantic and keyword search, and personalized feeds — are routed to specific file locations and components that implement the user experience and data fetching. The database client (`src/lib/db.ts`) serves as the common backend data access layer used by these components to execute prompt queries.

Sources: [src/app/page.tsx:21-52](), [src/app/prompts/page.tsx:176-185](), [src/app/feed/page.tsx:11-13](), [src/app/categories/(index)/page.tsx:77-78](), [src/app/tags/(index)/page.tsx:53-54](), [src/components/prompts/discovery-prompts.tsx:13-16](), [src/app/bots/page.tsx:60-61]()

---

## Core Discovery Mechanisms

| Mechanism | Route Path | Primary Component / File | Data Access Pattern |
|-----------|------------|--------------------------|---------------------|
| **Homepage Curation** | `/` | `src/app/page.tsx` | Parallel queries for featured, trending, latest prompts using `DiscoveryPrompts` component [src/components/prompts/discovery-prompts.tsx:50-118]() |
| **Browse & Filter** | `/prompts` | `src/app/prompts/page.tsx` | Cached queries or fallback to `semanticSearch()` AI embeddings [src/app/prompts/page.tsx:82-162](), [src/app/prompts/page.tsx:195-201]() |
| **Category Navigation** | `/categories/:slug` | `src/app/categories/(index)/page.tsx` | `db.category.findMany` with prompt counts and relational queries [src/app/categories/(index)/page.tsx:20-56]() |
| **Tag Navigation** | `/tags/:slug` | `src/app/tags/(index)/page.tsx` | `db.tag.findMany` combined with relational prompt filtering [src/app/tags/(index)/page.tsx:11-35]() |
| **Personalized Feed** | `/feed` | `src/app/feed/page.tsx` | User category subscription lookup + prompt matching [src/app/feed/page.tsx:21-44]() |
| **User Collections** | `/collection` | `src/app/collection/page.tsx` | Collection queries filtering unlisted items [src/app/collection/page.tsx:18-64]() |
| **Specialized Skills** | `/skills` | `src/app/skills/page.tsx` | Cached queries filtering by `type: "SKILL"` [src/app/skills/page.tsx:16-31]() |
| **Sequential Workflows** | `/workflows` | `src/app/workflows/page.tsx` | Workflow connection graph queries [src/app/workflows/page.tsx:23-38]() |
| **Bot Listings** | `/bots` | `src/app/bots/page.tsx` | `listBots` function with filtering and pagination [src/app/bots/page.tsx:67-76]() |
| **Classifier Listings** | `/classifiers` | `src/app/classifiers/page.tsx` | `getClassifierCatalog` for listed classifiers and chains [src/lib/classifiers/store.ts:1-1]() |

Sources: [src/app/page.tsx:8-9](), [src/app/prompts/page.tsx:8-9](), [src/app/categories/(index)/page.tsx:20-56](), [src/app/tags/(index)/page.tsx:11-35](), [src/app/feed/page.tsx:11-44](), [src/app/collection/page.tsx:10-64](), [src/app/skills/page.tsx:16-31](), [src/app/workflows/page.tsx:23-38](), [src/app/bots/page.tsx:67-76](), [src/lib/classifiers/store.ts:1-1]()

---

## Query Pipeline & Entity Mapping

Discovery queries start as natural language inputs (search strings, category slugs, filters), then flow through page route handlers that decide on the query strategy: direct Prisma filtering, cache reads, or invoking AI-driven semantic search.

### Diagram: Discovery Query Pipeline
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        InputQuery["SearchStringAndFilters"]
    end

    subgraph "CodeEntitySpace"
        RouteHandler["PromptsPage<br>src/app/prompts/page.tsx"]
        AISearch["semanticSearch()<br>src/lib/ai/embeddings.ts"]
        UnstableCache["unstable_cache()<br>Next.js Cache API"]
        PrismaDb["db.prompt.findMany<br>src/lib/db.ts"]
    end

    InputQuery --> RouteHandler
    RouteHandler -->|ai=1 & q present| AISearch
    RouteHandler -->|otherwise| UnstableCache
    AISearch --> PrismaDb
    UnstableCache --> PrismaDb
```

Sources: [src/app/prompts/page.tsx:73-82](), [src/app/prompts/page.tsx:182-205](), [src/lib/ai/embeddings.ts:1-1]()

---

## Bridging Natural Language Discovery to Code Entities

### Diagram: Natural Language to Homepage Content Discovery Mapping
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        NL_Hero["HeroSectionFeaturedTrendingPrompts"]
        NL_Achievements["AchievementsAndTestimonials"]
        NL_Sponsors["SponsorsAndCallToAction"]
    end
    
    subgraph "CodeEntitySpace"
        Code_Page["HomePageComponent<br>src/app/page.tsx"]
        DiscoveryComp["DiscoveryPromptsComponent<br>src/components/prompts/discovery-prompts.tsx"]
        Config["getConfig()AndUseCloneBranding<br>prompts.config.ts"]
    end

    NL_Hero --> Code_Page
    NL_Achievements --> Code_Page
    NL_Sponsors --> Code_Page
    Code_Page --> DiscoveryComp
    Code_Page --> Config
```

Sources: [src/app/page.tsx:21-52](), [src/components/prompts/discovery-prompts.tsx:50-118](), [prompts.config.ts:1-30]()

---

### Diagram: Semantic Search Path from User Query to AI Embeddings and Prompt Data
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        UserQuery["UserSearchInputWithQueryAndAIParameter"]
    end

    subgraph "CodeEntitySpace"
        RouteHandler["PromptsPageHandler<br>src/app/prompts/page.tsx"]
        AiModule["semanticSearch()<br>src/lib/ai/embeddings.ts"]
        PrismaQuery["db.prompt.findMany<br>src/lib/db.ts"]
    end

    UserQuery --> RouteHandler
    RouteHandler --> AiModule
    AiModule --> PrismaQuery
```

Sources: [src/app/prompts/page.tsx:182-205](), [src/lib/ai/embeddings.ts:1-1](), [src/lib/db.ts:1-21]()

---

## Sub-Topic Summaries & Child Page References

### Homepage & Landing
The homepage (`src/app/page.tsx`) combines a hero section with animated interactive elements, synchronized with prompt discovery feeds displayed via the `DiscoveryPrompts` component. Configuration-driven flags like `useCloneBranding` affect branding and content display. For details, see [Homepage & Landing](#6.1).

### Categories & Tags
Categories are organized hierarchically and expose parent-child relations. Tags provide flat color-coded thematic classifications. Both enable faceted browsing and filtering of prompts. Users may subscribe to categories to tailor their feed, which the personalized feed page (`src/app/feed/page.tsx`) utilizes. The `getCategories` function in [src/app/categories/(index)/page.tsx:20-56]() and `getTags` in [src/app/tags/(index)/page.tsx:11-35]() are used to fetch this data. For details, see [Categories & Tags](#6.2).

Sources: [src/app/categories/(index)/page.tsx:20-56](), [src/app/tags/(index)/page.tsx:11-35]()

### Search Systems
The search page supports traditional keyword search—splitting terms by commas—and AI-powered semantic search leveraging OpenAI embeddings. Search results are ranked accordingly and displayed with infinite scrolling. For details, see [Search Systems](#6.3).

### Curated Discovery
Curated prompt lists such as featured, today's most upvoted, latest, recently updated, and most contributed prompts are retrieved via parallel database queries in `DiscoveryPrompts` and displayed in various widget cards. This provides users a broad swipe of quality content. For details, see [Curated Discovery](#6.4).

### SEO & Social Metadata
This encompasses generating structured data schemas, `sitemap.ts`, `robots.ts`, dynamic OpenGraph and Twitter card image generation, and analytics instrumentation to optimize search engine indexability and social sharing. The `sitemap` function in [src/app/sitemap.ts:30-175]() generates the sitemap, while `robots` in [src/app/robots.ts:4-30]() defines crawling rules. Structured data is handled by components like `JsonLd` and functions like `collectionPageSchema` and `promptSchema` in [src/components/seo/structured-data.tsx:12-179](). OpenGraph and Twitter images for bots are generated by files like [src/app/bots/opengraph-image.tsx:9-13]() and [src/app/bots/twitter-image.tsx:1-2](). Analytics for bot views and clicks are tracked by `BotViewTracker` and `BotCardLink` in [src/components/bots/bot-analytics.tsx:5-32](). For details, see [SEO & Social Metadata](#6.5).

Sources: [src/app/sitemap.ts:30-175](), [src/app/robots.ts:4-30](), [src/components/seo/structured-data.tsx:12-179](), [src/app/bots/opengraph-image.tsx:9-13](), [src/app/bots/twitter-image.tsx:1-2](), [src/app/bots/[slug]/opengraph-image.tsx:9-14](), [src/app/bots/[slug]/twitter-image.tsx:1-2](), [src/components/bots/bot-analytics.tsx:5-32]()

---

# Page: Homepage & Landing

# Homepage & Landing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/__tests__/components/built-with.test.tsx](src/__tests__/components/built-with.test.tsx)
- [src/app/page.tsx](src/app/page.tsx)
- [src/components/layout/built-with.tsx](src/components/layout/built-with.tsx)

</details>



## Purpose and Scope
This page documents the homepage (`/`) implementation in the Prompts.chat codebase, specifically residing in `src/app/page.tsx` [src/app/page.tsx:35-65](). The homepage functions as the primary landing interface for all users—both authenticated and anonymous—delivering the hero banner, client application integration links, featured prompts discovery, community achievements, testimonials, sponsors, and conditional rendering via the `useCloneBranding` configuration flag [src/app/page.tsx:45-45]().

---

## Page Initialization & Data Flow

The homepage is structured as an asynchronous React Server Component (`HomePage`) exported by `src/app/page.tsx` [src/app/page.tsx:35-35](). It resolves global state, user session data, and configuration parameters before executing its rendering pipeline.

The initialization workflow entails:
- Invoking `auth()` from `src/lib/auth` [src/app/page.tsx:6-6]() to check for an active user session [src/app/page.tsx:38-38]().
- Invoking `getConfig()` from `src/lib/config` [src/app/page.tsx:7-7]() to load application-wide configuration values, branding targets, and feature flags [src/app/page.tsx:39-39]().
- Conditionally retrieving the live GitHub star count for the repository `f/prompts.chat` via `https://api.github.com/repos/f/prompts.chat` with a 1-hour revalidation cache [src/app/page.tsx:52-54](), gated by the `useCloneBranding` and achievement visibility toggles [src/app/page.tsx:50-50]().

```mermaid
graph TB
    subgraph "Code Entity Space"
        Node1["HomePage @src/app/page.tsx:35"]
        Node2["auth @src/lib/auth"]
        Node3["getConfig @src/lib/config"]
        Node4["useCloneBranding @src/app/page.tsx:45"]
        Node6["GitHub API fetch @src/app/page.tsx:52-55"]
        Node8["HomePage JSX Render @src/app/page.tsx:64-67"]
        Node10["Hero Section @src/app/page.tsx:69"]
        Node11["DiscoveryPrompts @src/components/prompts/discovery-prompts.tsx"]
    end
    subgraph "Natural Language Space"
        Nat1["Session Resolution"]
        Nat2["Global Config Pipeline"]
        Nat3["GitHub Star Sync"]
    end

    Node1 --> Node2
    Node1 --> Node3
    Node3 --> Node4
    Node3 --> Node5{"!useCloneBranding && achievements.enabled?"}
    Node5 -->|Yes| Node6
    Node5 -->|No| Node7["Skip Star Fetch"]
    Node2 --> Node8
    Node3 --> Node8
    Node6 --> Node8
    Node8 --> Node10
    Node8 --> Node11
```
Sources: `src/app/page.tsx:35-67`

---

## Configuration-Driven Rendering & Clone Branding

The layout adapts dynamically based on the configuration object yielded by `getConfig()` [src/app/page.tsx:39-39](), which merges `prompts.config.ts` specifications with `PCHAT_*` environment variable overrides.

```mermaid
graph LR
    subgraph "Code Entity Space"
        NodeA["prompts.config.ts"]
        NodeB["getConfig @src/lib/config"]
        NodeC["Environment Variables PCHAT_*"]
        NodeD["Config Object"]
        NodeH["useCloneBranding @src/app/page.tsx:45"]
    end
    subgraph "Natural Language Space"
        NatConfig["Configuration Loading"]
    end

    NodeA --> NodeB
    NodeC --> NodeB
    NodeB --> NodeD
    NodeD --> NodeE["branding config"]
    NodeD --> NodeF["homepage config"]
    NodeD --> NodeG["features config"]
    NodeF --> NodeH
    NodeF --> NodeI["sponsors.enabled"]
    NodeF --> NodeJ["achievements.enabled"]
```
Sources: `src/app/page.tsx:39-47`

### The `useCloneBranding` Flag

When `config.homepage.useCloneBranding` evaluates to `true`, the homepage layout switches to a white-labeled or enterprise-hosted variant:

| Feature | Standard Open-Source Mode (`false`) | Clone Branding Mode (`true`) |
| :--- | :--- | :--- |
| **Hero Title** | Dynamic animated gradient text via `AnimatedText` [src/app/page.tsx:13]() | Static brand title resolved via `config.branding.name` [src/app/page.tsx:75-76]() |
| **Hero Description** | Default open-source value proposition | Custom description from `config.branding.description` |
| **Hero Background** | Looping video animation (`animation_compressed.mp4`) with client widgets [src/app/page.tsx:94-103]() | Watermarked branding logo (`config.branding.logo`) [src/app/page.tsx:74-87]() |
| **Achievements Section** | GitHub stars, contributor counts, metrics grid | Hidden |
| **Sponsors Section** | Rendered if enabled | Rendered if enabled |

Sources: `src/app/page.tsx:39-47`, `src/app/page.tsx:71-88`

---

## Hero Section & Client Integration Links

The hero section presents core value propositions, interactive category navigation pills (`HeroCategories`) [src/app/page.tsx:106-106](), and shortcuts for multi-platform client applications.

Client connectivity options rendered in the hero section:
- `CliCommand`: Renders the `npx prompts.chat` CLI installation command snippet [src/app/page.tsx:111-111]().
- App Store Link: Rendered when `config.branding.appStoreUrl` is configured [src/app/page.tsx:112-124]().
- Browser Extension Link: Rendered via `ExtensionLink` if `config.branding.chromeExtensionUrl` is specified [src/app/page.tsx:125-127]().
- Raycast Extension Link: Direct deep link pointing to `raycast://extensions/fka/prompts-chat?source=prompts.chat` [src/app/page.tsx:128-132]().

Sources: `src/app/page.tsx:69-132`, `src/components/layout/cli-command.tsx`, `src/components/layout/extension-link.tsx`, `src/components/prompts/hero-categories.tsx`

---

## Featured Content & Discovery Integration

Below the hero banner, the homepage embeds the `DiscoveryPrompts` component, aggregating and displaying categorized prompt streams, trending lists, and recently updated records [src/app/page.tsx:9-9]().

```mermaid
graph TB
    subgraph "Code Entity Space"
        NodeK["HomePage @src/app/page.tsx:35"]
        NodeL["DiscoveryPrompts @src/components/prompts/discovery-prompts.tsx"]
        NodeM["Prisma ORM Queries"]
    end
    subgraph "Natural Language Space"
        NatDiscovery["Curated Discovery Feed"]
    end

    NodeK --> NodeL
    NodeL --> NodeM
    NodeM --> NodeN["Filter by categories, tags, and vote metrics"]
    NodeN --> NodeO["Render Curated Lists on Landing View"]
```
Sources: `src/app/page.tsx:9`, `src/components/prompts/discovery-prompts.tsx`

---

## BuiltWith Component & Sponsors Integration

### BuiltWith Component
The `BuiltWith` component (`src/components/layout/built-with.tsx`) manages open-source partner attribution links, displaying light and dark SVG assets for tools like Devin (Cognition), Grok Bot, and the Vercel OSS Program [src/components/layout/built-with.tsx:7-87](). It utilizes flex-row wrapping and non-breaking groupings to ensure graceful reflow on narrow viewports [src/components/layout/built-with.tsx:5-6]().

### Sponsors & Achievements
- Sponsor vector logos are stored under `public/sponsors/` with distinct light and dark variants.
- Achievement metrics fetch live star metrics from the GitHub REST API (`https://api.github.com/repos/f/prompts.chat`) cached with revalidation [src/app/page.tsx:52-54]().
- Numeric counts are formatted with helper functions such as `getOrdinalSuffix` [src/app/page.tsx:29-33]().
- Achievements are omitted when `useCloneBranding` is active [src/app/page.tsx:45-50]().

Sources: `src/app/page.tsx:29-62`, `src/components/layout/built-with.tsx`, `src/__tests__/components/built-with.test.tsx`

---

## Technical References

| Section | Code Symbols & Files |
| :--- | :--- |
| **Page Initialization** | `HomePage`, `src/app/page.tsx:35-65` |
| **Clone Branding Config** | `useCloneBranding`, `src/app/page.tsx:45-50` |
| **Hero Section & Clients** | `HeroCategories`, `CliCommand`, `ExtensionLink`, `src/app/page.tsx:69-132` |
| **Discovery Component** | `DiscoveryPrompts`, `src/components/prompts/discovery-prompts.tsx` |
| **BuiltWith & Sponsors** | `BuiltWith`, `src/components/layout/built-with.tsx`, `src/__tests__/components/built-with.test.tsx` |

Sources: `src/app/page.tsx`, `src/components/layout/built-with.tsx`, `src/__tests__/components/built-with.test.tsx`

---

# Page: Categories & Tags

# Categories & Tags

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [prisma/migrations/20251227125700_add_pinned_categories/migration.sql](prisma/migrations/20251227125700_add_pinned_categories/migration.sql)
- [src/app/[username]/page.tsx](src/app/[username]/page.tsx)
- [src/app/api/admin/categories/[id]/route.ts](src/app/api/admin/categories/[id]/route.ts)
- [src/app/api/admin/categories/route.ts](src/app/api/admin/categories/route.ts)
- [src/app/api/prompts/[id]/route.ts](src/app/api/prompts/[id]/route.ts)
- [src/app/api/prompts/route.ts](src/app/api/prompts/route.ts)
- [src/app/categories/[slug]/page.tsx](src/app/categories/[slug]/page.tsx)
- [src/app/collection/page.tsx](src/app/collection/page.tsx)
- [src/app/feed/page.tsx](src/app/feed/page.tsx)
- [src/app/prompts/[id]/page.tsx](src/app/prompts/[id]/page.tsx)
- [src/app/skills/page.tsx](src/app/skills/page.tsx)
- [src/app/tags/[slug]/page.tsx](src/app/tags/[slug]/page.tsx)
- [src/components/admin/categories-table.tsx](src/components/admin/categories-table.tsx)
- [src/components/categories/pinned-categories.tsx](src/components/categories/pinned-categories.tsx)
- [src/components/prompts/discovery-prompts.tsx](src/components/prompts/discovery-prompts.tsx)

</details>



This page documents the hierarchical category system and flat tag system used for organizing and filtering prompts in `prompts.chat`. Categories support parent-child relationships, user subscriptions, and pinning for quick access. Tags provide additional labeling with color coding.

---

## Purpose & Scope

The category and tag subsystems provide structural organization for prompts across `prompts.chat`. This document details the database schema, Prisma models, admin hierarchy management, pinned category filtering, color-coded tagging, and the user category subscription architecture.

Sources:  
[src/app/categories/[slug]/page.tsx:79-108]()  
[src/components/admin/categories-table.tsx:89-102]()  

---

## System Overview

The platform uses two complementary organizational systems backed by Prisma models and data fetching layers:

- **Categories**: Hierarchical tree structure managed via `db.category`, supporting root and subcategories through parent-child relationships (`parentId`). Categories can be pinned for quick access via the `pinned` field [prisma/migrations/20251227125700_add_pinned_categories/migration.sql:1-5](), and users can subscribe to categories to receive personalized content feeds [src/app/feed/page.tsx:28-40]().
- **Tags**: A flat list of labels managed via `db.tag`, with customizable hex color codes for visual identification and filtering as seen in [src/app/tags/[slug]/page.tsx:166-169](). They provide additional metadata for prompts that cross-cut categories.

The mapping between natural language concepts and code entities is shown below.

### Diagram: Natural Language Space to Code Entities for Categories & Tags

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        UserCategories["CategoryTreeAndPinnedPills"]
        UserTags["TagColorCodingAndFilters"]
        UserFeeds["PersonalizedSubscribedFeeds"]
    end

    subgraph "CodeEntitySpace"
        DBCategory["db.category"]
        DBTag["db.tag"]
        CategoryPage["CategoryPage(src/app/categories/[slug]/page.tsx)"]
        CategoryAdminAPI["/api/admin/categories(src/app/api/admin/categories/route.ts)"]
        AdminTable["CategoriesTable(src/components/admin/categories-table.tsx)"]
        PinnedComp["PinnedCategories(src/components/categories/pinned-categories.tsx)"]
        TagsPage["TagPage(src/app/tags/[slug]/page.tsx)"]
        FeedPage["FeedPage(src/app/feed/page.tsx)"]
    end

    UserCategories --> DBCategory
    UserCategories --> PinnedComp
    UserTags --> DBTag
    UserFeeds --> FeedPage
    
    DBCategory --> CategoryPage
    CategoryPage --> AdminTable
    AdminTable --> CategoryAdminAPI
    PinnedComp --> AdminTable
    DBTag --> TagsPage
    FeedPage --> DBCategory
```

Sources:  
[prisma/migrations/20251227125700_add_pinned_categories/migration.sql:1-5]()  
[src/app/categories/[slug]/page.tsx:79-108]()  
[src/app/tags/[slug]/page.tsx:166-169]()  
[src/components/admin/categories-table.tsx:83-148]()  
[src/components/categories/pinned-categories.tsx:20-83]()  
[src/app/feed/page.tsx:28-40]()  
[src/app/api/admin/categories/route.ts:7-39]()  

---

## Database Schema & Data Models

### Data Models

The core data structures for categories, tags, and their relationships to users and prompts are implemented as Prisma models:

| Model                  | Description                                   |
|------------------------|-----------------------------------------------|
| `Category`             | Represents hierarchical categories with fields: `id`, `name`, `slug`, `description`, `icon`, `parentId` for parent-child hierarchy, `order` for sorting, and `pinned` boolean flag [prisma/migrations/20251227125700_add_pinned_categories/migration.sql:1-5]() |
| `Tag`                  | Represents non-hierarchical tags with: `id`, `name`, `slug`, and `color` (hex string) |
| `CategorySubscription` | Stores user subscriptions to categories: links `userId` to `categoryId` [src/app/categories/[slug]/page.tsx:98-107]() |
| `PromptTag`             | Join table linking prompts to tags via `promptId` and `tagId` [src/app/api/prompts/route.ts:94-98]() |

### Entity Relationship Diagram

```mermaid
erDiagram
    Category {
        string id PK
        string name
        string slug UK
        string description
        string icon
        string parentId FK
        int order
        boolean pinned
    }
    
    Tag {
        string id PK
        string name
        string slug UK
        string color
    }
    
    CategorySubscription {
        string id PK
        string userId FK
        string categoryId FK
    }
    
    PromptTag {
        string promptId FK
        string tagId FK
    }

    Category ||--o{ Category : "parent-child"
    Category ||--o{ CategorySubscription : "subscriptions"
    Tag ||--o{ PromptTag : "tags"
```

Sources:  
[prisma/migrations/20251227125700_add_pinned_categories/migration.sql:1-5]()  
[src/app/categories/[slug]/page.tsx:98-107]()  
[src/app/api/prompts/route.ts:94-98]()  

---

## Hierarchical Category System

Categories are arranged in a multi-level hierarchy consisting of root categories and subcategories. Root categories have `parentId` set to `null`, while child categories reference their parent's `id` via `parentId` [src/components/admin/categories-table.tsx:82-102]().

### Admin Hierarchy Management

The admin UI component `CategoriesTable` builds a flat ordered list with indentation levels for display, computed from root categories and their children [src/components/admin/categories-table.tsx:89-102](). It filters valid parent options to prevent cyclic assignments [src/components/admin/categories-table.tsx:141-148]().

### Category Mutation API

Categories are mutable through administrative API routes such as `POST /api/admin/categories` [src/app/api/admin/categories/route.ts:7-39](), which update record fields, enforce admin role verification [src/app/api/admin/categories/route.ts:9-12](), and trigger cache invalidation via `revalidateTag` [src/app/api/admin/categories/route.ts:32]().

### Diagram: Category Mutation and Cache Revalidation Workflow

```mermaid
sequenceDiagram
    participant Admin as "AdminUser"
    participant UI as "CategoriesTable"
    participant API as "/api/admin/categories"
    participant DB as "db.category"
    participant Cache as "revalidateTag"

    Admin->>UI: "SubmitCategoryCreate"
    UI->>API: "HTTP_POST"
    API->>DB: "db.category.create()"
    DB-->>API: "NewCategoryRecord"
    API->>Cache: "revalidateTag('categories')"
    API-->>UI: "JSONResponse"
    UI-->>Admin: "ShowSuccessToast"
```

Sources:  
[src/components/admin/categories-table.tsx:83-148]()  
[src/app/api/admin/categories/route.ts:7-39]()  
[src/app/api/admin/categories/route.ts:9-12]()  
[src/app/api/admin/categories/route.ts:32]()  

---

## Pinned Categories & Filtering

Pinned categories provide a quick filtering mechanism in the main prompt discovery UI as clickable pills:
- Rendered by the `PinnedCategories` client component [src/components/categories/pinned-categories.tsx:20-83]().
- Uses `useFilterContext` to manage pending states during query transitions [src/components/categories/pinned-categories.tsx:24]().
- Highlights the active pinned category from URL query parameters.
- Clicking a pinned category pill toggles filtering by that category or clears it [src/components/categories/pinned-categories.tsx:30-51]().
- Administrators can pin or unpin categories via `handleTogglePin` in the `CategoriesTable` component [src/components/admin/categories-table.tsx:121-139]().

Sources:  
[src/components/categories/pinned-categories.tsx:20-83]()  
[src/components/categories/pinned-categories.tsx:24]()  
[src/components/categories/pinned-categories.tsx:30-51]()  
[src/components/admin/categories-table.tsx:121-139]()  

---

## Tag System & Color Coding

Tags are non-hierarchical, color-coded labels assigned to prompts to facilitate cross-cutting topic filtering. Each tag record includes a `color` field storing a hexadecimal color string used inline for visual markers.

The tag page at `/tags/[slug]` queries tags by slug and renders them with their associated badge colors [src/app/tags/[slug]/page.tsx:166-169](). Each tag chip applies inline styles using `tag.color` for background or dot indicators [src/app/tags/[slug]/page.tsx:166-169]().

Sources:  
[src/app/tags/[slug]/page.tsx:67-73]()  
[src/app/tags/[slug]/page.tsx:166-169]()  

---

## Category Subscriptions & Personalized Feeds

Users can subscribe to categories they care about, enabling personalized notifications and feeds.

- **Subscription Storage**: Subscriptions are tracked via `CategorySubscription` records linking a `userId` and `categoryId` [src/app/categories/[slug]/page.tsx:98-107]().
- **Feed Generation**: The feed page (`src/app/feed/page.tsx:28-54`) queries subscribed category IDs for the authenticated session user to populate their personalized prompt stream.

Sources:  
[src/app/categories/[slug]/page.tsx:98-107]()  
[src/app/feed/page.tsx:28-54]()  

---

## Summary of Key Components and Files

| Concept                    | Key File/Component                                               | Description                                      |
|----------------------------|-----------------------------------------------------------------|--------------------------------------------------|
| Category page route        | `src/app/categories/[slug]/page.tsx`                            | Queries category details and prompt subscriptions|
| Category admin UI          | `src/components/admin/categories-table.tsx`                     | Table with hierarchy, editing, and pin toggling  |
| Category creation API      | `src/app/api/admin/categories/route.ts`                         | POST route for category creation with revalidation|
| Pinned categories UI       | `src/components/categories/pinned-categories.tsx`               | Filter pills for pinned categories               |
| Tag page route             | `src/app/tags/[slug]/page.tsx`                                   | Tag details, color indicators, and prompt listing|
| Feed generation route      | `src/app/feed/page.tsx`                                          | Fetches prompts based on user category subscriptions|

Sources:  
[src/app/categories/[slug]/page.tsx:79-108]()  
[src/components/admin/categories-table.tsx:83-148]()  
[src/app/api/admin/categories/route.ts:7-39]()  
[src/components/categories/pinned-categories.tsx:20-83]()  
[src/app/tags/[slug]/page.tsx:67-73]()  
[src/app/feed/page.tsx:28-54]()  

---

## Conclusion

The Categories & Tags system in `prompts.chat` provides a robust mechanism for organizing, filtering, and personalizing prompt discovery. Hierarchical category relationships enable structured browsing, pinned categories highlight popular filters, tags provide cross-cutting metadata with visual colors, and user subscriptions empower personalized workflows.

Sources:  
[src/app/categories/[slug]/page.tsx]()  
[src/components/admin/categories-table.tsx]()  
[src/app/api/admin/categories/route.ts]()  
[src/components/categories/pinned-categories.tsx]()  
[src/app/tags/[slug]/page.tsx]()  
[src/app/feed/page.tsx]()

---

# Page: Search Systems

# Search Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/api/prompts/search/route.ts](src/app/api/prompts/search/route.ts)
- [src/components/prompts/add-connection-dialog.tsx](src/components/prompts/add-connection-dialog.tsx)
- [src/lib/ai/embeddings.ts](src/lib/ai/embeddings.ts)
- [src/lib/ai/query-translator.prompt.yml](src/lib/ai/query-translator.prompt.yml)

</details>



## Purpose and Scope

This document details the search systems implemented in `prompts.chat`, focusing on two complementary methods:

- **Text-based keyword search** supporting comma-separated terms with case-insensitive matching [src/app/api/prompts/search/route.ts:18-23]().
- **AI-powered semantic search** leveraging OpenAI embeddings for meaning-aware retrieval, including multi-language query translation [src/lib/ai/embeddings.ts:33-79]().

These search mechanisms enable precise and contextually relevant prompt discovery within the platform.

For curated discovery mechanisms and categorical filtering, refer to [6.4 Curated Discovery]() and [6.2 Categories & Tags]().

Sources: [src/app/api/prompts/search/route.ts:5-57](), [src/lib/ai/embeddings.ts:209-233]()

---

## Architecture Overview

The system supports two primary search modes optimized for different use cases:

| Search Type | Implementation | Strengths | Requirements |
| :---------- | :------------- | :-------- | :----------- |
| **Text Search** | PostgreSQL `LIKE` via Prisma filters | Fast, predictable, no extra setup | None |
| **Semantic Search** | OpenAI embeddings + cosine similarity | Context-aware, multi-language support | `OPENAI_API_KEY` |

### Search Data Flow

The diagram below depicts the key components and data flow for the search system, bridging user natural language input and backend code entities, as well as integration points with AI embedding services.

Title: Search System Data Flow
```mermaid
graph TD
    subgraph NaturalLanguageSpace["NaturalLanguage Space"]
        UserRequest["User Search Query String"]
        QueryKeywords["Comma-Separated Keywords or Non-English Text"]
    end
    
    subgraph BackendCodeSpace["Backend Code Entity Space"]
        SearchAPI["GET /api/prompts/search"]
        AuthCheck["auth()"]
        QueryValidation["Validate Query Length"]
        SplitQuery["Split Query By Comma"]
        TextSearchDB["db.prompt.findMany()"]
        SemanticSearchFunc["semanticSearch()"]
        QueryTranslate["translateQueryToEnglish()"]
        GenerateEmbedding["generateEmbedding()"]
        CosineSimilarityCalc["cosineSimilarity()"]
        EmbeddingDBQuery["DB Query For Embeddings"]
    end
    
    UserRequest --> QueryKeywords
    QueryKeywords --> SearchAPI
    SearchAPI --> AuthCheck
    AuthCheck --> QueryValidation
    QueryValidation -->|valid| SplitQuery
    SplitQuery --> TextSearchDB
    
    SearchAPI -.->|"AI Semantic search path"| SemanticSearchFunc
    SemanticSearchFunc --> QueryTranslate
    QueryTranslate --> GenerateEmbedding
    GenerateEmbedding --> EmbeddingDBQuery
    EmbeddingDBQuery --> CosineSimilarityCalc
    CosineSimilarityCalc --> SemanticSearchFunc
```

Sources: [src/app/api/prompts/search/route.ts:5-57](), [src/lib/ai/embeddings.ts:32-79](), [src/lib/ai/embeddings.ts:209-233]()

---

## Text-Based Search

### Query Processing and Keyword Handling

Text search functionality is implemented in the `GET` endpoint at `src/app/api/prompts/search/route.ts` which handles incoming search requests with parameters [src/app/api/prompts/search/route.ts:5-10]():

- **`q`**: the query string to search [src/app/api/prompts/search/route.ts:7-7]().
- **`limit`**: maximum number of prompts to return [src/app/api/prompts/search/route.ts:8-8]().
- **`ownerOnly`**: flag to restrict results to the authenticated user [src/app/api/prompts/search/route.ts:9-9]().

The core search logic parses the query string for comma-separated keywords and constructs Prisma query filters accordingly [src/app/api/prompts/search/route.ts:18-23]().

- For multiple keywords: each keyword generates a condition for `title` containing the term, combined with `OR` logic [src/app/api/prompts/search/route.ts:20-22]().
- For a single keyword: a single `contains` filter on `title` with case-insensitive matching [src/app/api/prompts/search/route.ts:22-22]().

This processing appears in lines [18-23] of `src/app/api/prompts/search/route.ts`:

```ts
const keywords = query.split(",").map(k => k.trim()).filter(Boolean);
const titleConditions = keywords.length > 1
  ? keywords.map(keyword => ({ title: { contains: keyword, mode: "insensitive" as const } }))
  : [{ title: { contains: query, mode: "insensitive" as const } }];
```

Sources: [src/app/api/prompts/search/route.ts:5-23]()

### Visibility and Privacy Filters

The database search query enforces visibility constraints to ensure only appropriate prompts are returned:

| Condition | Description | Code Location |
| :-------- | :---------- | :------------ |
| `deletedAt: null` | Exclude soft-deleted prompts | [src/app/api/prompts/search/route.ts:26-26]() |
| `isUnlisted: false` | Exclude unlisted prompts | [src/app/api/prompts/search/route.ts:27-27]() |
| Privacy handling: public or own | Either public prompts or those owned by user | [src/app/api/prompts/search/route.ts:33-37]() |
| Owner-only filter | Restrict to prompts authored by user if set | [src/app/api/prompts/search/route.ts:30-31]() |

Sources: [src/app/api/prompts/search/route.ts:24-41]()

### Search Result Ordering

The endpoint orders matched prompts primarily by:

1. `isFeatured` descending (featured prompts first) [src/app/api/prompts/search/route.ts:54-54]()
2. `viewCount` descending (popular prompts higher) [src/app/api/prompts/search/route.ts:55-55]()

This ranking is implemented via Prisma's `orderBy` clause [src/app/api/prompts/search/route.ts:53-56]().

Sources: [src/app/api/prompts/search/route.ts:53-56]()

### Selected Fields in Response

Only fields required for display in search results are retrieved: `id`, `title`, `slug`, and author's `username` [src/app/api/prompts/search/route.ts:42-51]().

Sources: [src/app/api/prompts/search/route.ts:42-57]()

---

## AI Semantic Search

### Overview

Semantic search leverages OpenAI's embeddings API to provide meaning-based prompt retrieval. This method:

- Converts a natural language query into a vector embedding [src/lib/ai/embeddings.ts:71-80]().
- Matches query embedding against precomputed embeddings of prompt content [src/lib/ai/embeddings.ts:214-233]().
- Ranks prompts by cosine similarity in descending order [src/lib/ai/embeddings.ts:162-174]().

This functionality is implemented mainly in the `semanticSearch` function in `src/lib/ai/embeddings.ts` [src/lib/ai/embeddings.ts:209-233]().

Sources: [src/lib/ai/embeddings.ts:71-80](), [src/lib/ai/embeddings.ts:162-174](), [src/lib/ai/embeddings.ts:209-233]()

### Multi-language Query Translation

To enhance semantic matching for non-English queries, the system automatically translates queries to English keywords before embedding generation. This uses a specialized prompt (`query-translator.prompt.yml`) and a small OpenAI model (`gpt-4o-mini` by default) for cost efficiency [src/lib/ai/embeddings.ts:27-51]().

- The `containsNonEnglish` function checks the query for non-ASCII characters to detect foreign languages [src/lib/ai/embeddings.ts:65-69]().
- If detected, `translateQueryToEnglish` sends the query through a chat completion with a system prompt instructing keyword extraction and English translation [src/lib/ai/embeddings.ts:33-60]().
- Translated keywords replace the original query for embedding generation [src/lib/ai/embeddings.ts:225-231]().

The `src/lib/ai/query-translator.prompt.yml` file defines the system behavior for keyword extraction and translation [src/lib/ai/query-translator.prompt.yml:1-22]().

Sources: [src/lib/ai/embeddings.ts:27-69](), [src/lib/ai/embeddings.ts:225-231](), [src/lib/ai/query-translator.prompt.yml:1-22]()

### Embedding Generation Workflow

Prompt embeddings are created by concatenating the prompt’s:

- `title` [src/lib/ai/embeddings.ts:98-98]()
- `description` [src/lib/ai/embeddings.ts:99-99]()
- `content` [src/lib/ai/embeddings.ts:100-100]()

into a single text blob for input to OpenAI’s embedding model (default: `text-embedding-3-small`) [src/lib/ai/embeddings.ts:26-26]().

Embeddings are stored in the `embedding` field in the prompt database record [src/lib/ai/embeddings.ts:105-108](). Private and deleted prompts are excluded from embedding generation [src/lib/ai/embeddings.ts:93-94]().

A bulk re-generation function `generateAllEmbeddings` handles batch embedding creation with throttling delays (1 second per request) to respect API rate limits [src/lib/ai/embeddings.ts:116-160]().

Sources: [src/lib/ai/embeddings.ts:26-26](), [src/lib/ai/embeddings.ts:93-108](), [src/lib/ai/embeddings.ts:116-160]()

### Semantic Search Algorithm

Given a query string:

1. Translate to English keywords if necessary [src/lib/ai/embeddings.ts:225-228]().
2. Generate the query embedding vector [src/lib/ai/embeddings.ts:231-231]().
3. Fetch all public prompts that have an existing embedding [src/lib/ai/embeddings.ts:233-233]().
4. Compute cosine similarity between the query vector and each prompt embedding using `cosineSimilarity` function [src/lib/ai/embeddings.ts:162-174]().
5. Sort and return the top prompts ranked by similarity [src/lib/ai/embeddings.ts:209-233]().

Sources: [src/lib/ai/embeddings.ts:162-174](), [src/lib/ai/embeddings.ts:209-233](), [src/lib/ai/embeddings.ts:225-233]()

### Embedding Generation and Semantic Search Pipeline Diagram

Title: Embedding Generation and Semantic Search Pipeline
```mermaid
graph TD
    subgraph NaturalLanguageInput["Natural Language Input Space"]
        UserQuery["User Search Query"]
        PromptText["Prompt Text Combination"]
    end
    
    subgraph AIEmbeddingBackend["Code Entity Space (src/lib/ai/embeddings.ts)"]
        TranslateQuery["translateQueryToEnglish()"]
        GenerateEmbedding["generateEmbedding()"]
        FetchPrompt["db.prompt.findUnique()"]
        UpdateEmbeddingDB["db.prompt.update()"]
        SemanticSearchFunction["semanticSearch()"]
        FetchAllEmbeddings["db.prompt.findMany()"]
        ComputeCosineSimilarity["cosineSimilarity()"]
    end
    
    UserQuery --> TranslateQuery
    TranslateQuery --> GenerateEmbedding
    GenerateEmbedding --> SemanticSearchFunction
    SemanticSearchFunction --> FetchAllEmbeddings
    FetchAllEmbeddings --> ComputeCosineSimilarity
    ComputeCosineSimilarity --> SemanticSearchFunction
    
    PromptText --> FetchPrompt
    FetchPrompt --> GenerateEmbedding
    GenerateEmbedding --> UpdateEmbeddingDB
```

Sources: [src/lib/ai/embeddings.ts:32-79](), [src/lib/ai/embeddings.ts:70-108](), [src/lib/ai/embeddings.ts:115-159](), [src/lib/ai/embeddings.ts:209-233](), [src/lib/ai/query-translator.prompt.yml:1-22]()

---

## Search Result Ranking

### Text Search Ranking

Text search results are sorted primarily by:

- **Featured status**: Featured prompts appear first (`isFeatured` DESC) [src/app/api/prompts/search/route.ts:54-54]().
- **Popularity**: Higher view counts rise in ranking (`viewCount` DESC) [src/app/api/prompts/search/route.ts:55-55]().

This ranking ensures quality and engagement prioritization even without semantic understanding [src/app/api/prompts/search/route.ts:53-56]().

Sources: [src/app/api/prompts/search/route.ts:53-56]()

### Semantic Search Ranking

Semantic search ranking is computed via the cosine similarity metric applied between the user query embedding and each prompt embedding [src/lib/ai/embeddings.ts:162-174]().

The cosine similarity function normalizes the vectors and computes a score between -1 and 1 representing content closeness [src/lib/ai/embeddings.ts:162-174]().

Results are sorted in descending similarity order, returning the top `limit` (default 20) prompts [src/lib/ai/embeddings.ts:209-233]().

Sources: [src/lib/ai/embeddings.ts:161-173](), [src/lib/ai/embeddings.ts:209-233]()

---

## Internal Prompt Search for UI and Workflow Linking

The `AddConnectionDialog` component enables prompt authors to search among their own prompts to add connections to workflows [src/components/prompts/add-connection-dialog.tsx:34-79]().

### Key Features

- Uses a debounced user input to trigger API searches, reducing request frequency [src/components/prompts/add-connection-dialog.tsx:50-50]().
- Calls the `/api/prompts/search` API with `ownerOnly=true` to restrict results to the logged-in user's prompts [src/components/prompts/add-connection-dialog.tsx:61-63]().
- Filters out the current prompt from results to prevent self-referential connections [src/components/prompts/add-connection-dialog.tsx:67-70]().
- Displays results with prompt titles and author usernames for selection [src/components/prompts/add-connection-dialog.tsx:162-180]().

This UI is often used for managing prompt workflows and related prompt connections [src/components/prompts/add-connection-dialog.tsx:34-79]().

Sources: [src/components/prompts/add-connection-dialog.tsx:34-79](), [src/components/prompts/add-connection-dialog.tsx:162-180]()

---

## Performance and Rate Limiting Considerations

- Bulk embedding generation (`generateAllEmbeddings`) pauses 1000 ms between API requests to avoid OpenAI API throttling and GitHub Model limits [src/lib/ai/embeddings.ts:153-156]().
- Semantic search requires precomputing and caching embeddings; private prompts are excluded to reduce unnecessary computation and maintain privacy [src/lib/ai/embeddings.ts:93-95]().
- Text search depends on efficient SQL `LIKE` queries and indexed filters for fast response with moderate load [src/app/api/prompts/search/route.ts:24-41]().

Sources: [src/lib/ai/embeddings.ts:81-155](), [src/app/api/prompts/search/route.ts:24-41]()

---

# Summary

| Layer | Component | Role & Description | Code Reference |
| :---- | :-------- | :----------------- | :------------- |
| API Route | `GET /api/prompts/search` | Handles keyword parsing, visibility filtering, and executes text search queries | [src/app/api/prompts/search/route.ts:5-57]() |
| AI Embedding Lib | `semanticSearch()` | Performs OpenAI embeddings queries, query translation, and cosine similarity | [src/lib/ai/embeddings.ts:209-233]() |
| AI Helpers | `translateQueryToEnglish()` | Translates non-English search queries to English keywords | [src/lib/ai/embeddings.ts:32-59]() |
| Helper Components | `AddConnectionDialog` | UI component for searching user-owned prompts during workflow connection adding | [src/components/prompts/add-connection-dialog.tsx:34-79]() |

Sources: [src/app/api/prompts/search/route.ts:5-57](), [src/lib/ai/embeddings.ts:32-59](), [src/lib/ai/embeddings.ts:209-233](), [src/components/prompts/add-connection-dialog.tsx:34-79]()

---

# Appendix: Relevant Code Symbols

| Symbol | Description | Location |
| :----- | :---------- | :------- |
| `auth()` | Authentication helper for user context | [src/app/api/prompts/search/route.ts:15-15]() |
| `db.prompt.findMany()` | Prisma ORM function querying prompts | [src/app/api/prompts/search/route.ts:24-57]() |
| `split(",")` | Text splitting for comma-separated keywords | [src/app/api/prompts/search/route.ts:19-22]() |
| `generateEmbedding(text)` | Calls OpenAI to generate vector embeddings | [src/lib/ai/embeddings.ts:70-79]() |
| `semanticSearch(query)` | Main semantic search function | [src/lib/ai/embeddings.ts:209-233]() |
| `cosineSimilarity(a,b)` | Computes vector similarity for ranking | [src/lib/ai/embeddings.ts:161-173]() |
| `translateQueryToEnglish()` | Translation and keyword extraction for queries | [src/lib/ai/embeddings.ts:32-59]() |
| `AddConnectionDialog` | Search UI for adding workflow connections | [src/components/prompts/add-connection-dialog.tsx:34-79]() |

Sources: [src/app/api/prompts/search/route.ts:15-57](), [src/lib/ai/embeddings.ts:32-233](), [src/components/prompts/add-connection-dialog.tsx:34-79]()

---

# References

- OpenAI embeddings API integration [src/lib/ai/embeddings.ts:1-240]()
- Search API route implementation [src/app/api/prompts/search/route.ts:1-67]()
- Query translation prompt config [src/lib/ai/query-translator.prompt.yml:1-22]()
- UI search component for prompt connections [src/components/prompts/add-connection-dialog.tsx:1-79]()

Sources:
[src/app/api/prompts/search/route.ts:1-67](),
[src/lib/ai/embeddings.ts:1-240](),
[src/lib/ai/query-translator.prompt.yml:1-22](),
[src/components/prompts/add-connection-dialog.tsx:1-79]()

---

# Page: Curated Discovery

# Curated Discovery

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/[username]/page.tsx](src/app/[username]/page.tsx)
- [src/app/api/leaderboard/route.ts](src/app/api/leaderboard/route.ts)
- [src/app/api/prompts/[id]/route.ts](src/app/api/prompts/[id]/route.ts)
- [src/app/api/prompts/route.ts](src/app/api/prompts/route.ts)
- [src/app/categories/[slug]/page.tsx](src/app/categories/[slug]/page.tsx)
- [src/app/collection/page.tsx](src/app/collection/page.tsx)
- [src/app/feed/page.tsx](src/app/feed/page.tsx)
- [src/app/prompts/[id]/page.tsx](src/app/prompts/[id]/page.tsx)
- [src/app/skills/page.tsx](src/app/skills/page.tsx)
- [src/app/tags/[slug]/page.tsx](src/app/tags/[slug]/page.tsx)
- [src/components/prompts/discovery-prompts.tsx](src/components/prompts/discovery-prompts.tsx)
- [src/components/prompts/infinite-prompt-list.tsx](src/components/prompts/infinite-prompt-list.tsx)
- [src/components/prompts/prompt-list.tsx](src/components/prompts/prompt-list.tsx)
- [src/components/prompts/widget-card.tsx](src/components/prompts/widget-card.tsx)
- [src/lib/plugins/widgets/book.tsx](src/lib/plugins/widgets/book.tsx)
- [src/lib/plugins/widgets/coderabbit.ts](src/lib/plugins/widgets/coderabbit.ts)
- [src/lib/plugins/widgets/index.ts](src/lib/plugins/widgets/index.ts)
- [src/lib/plugins/widgets/textream.tsx](src/lib/plugins/widgets/textream.tsx)
- [src/lib/plugins/widgets/types.ts](src/lib/plugins/widgets/types.ts)

</details>



This wiki page covers the technical implementation of curated content discovery within prompts.chat. The system leverages editor curation, community voting signals, content velocity, collaborative activity, and extensible widget plugins to surface high-quality prompts without requiring manual search.

## Overview

Curated discovery is primarily driven by the `DiscoveryPrompts` component [src/components/prompts/discovery-prompts.tsx:16-150](). This component aggregates multiple distinct prompt lists into a unified browsing experience optimized for the homepage and the dedicated discovery page. It combines editorial curation (featured prompts), social signals (voting), recent activity, and collaborative metrics to showcase quality content.

Additionally, dynamic **widget cards** are programmatically injected into prompt lists via the widget plugin system, enabling sponsor and promotional placements that respond to browsing filters and context [src/lib/plugins/widgets/index.ts:121-182]().

Sources:
- `src/components/prompts/discovery-prompts.tsx:16-150`
- `src/lib/plugins/widgets/index.ts:121-182`

---

## DiscoveryPrompts Component

The `DiscoveryPrompts` component [src/components/prompts/discovery-prompts.tsx:16-150]() is an asynchronous React Server Component responsible for fetching curated prompt collections for discovery views.

### Implementation Details

- The component accepts a boolean prop `isHomepage` to control the number of items per list (9 for homepage, 15 otherwise) [src/components/prompts/discovery-prompts.tsx:13-21]().
- It defines a consistent Prisma `include` object, `promptInclude`, specifying relations and selects necessary for rendering `PromptCard` components [src/components/prompts/discovery-prompts.tsx:23-48]():
  - Author info with selected fields (`id`, `name`, `username`, `avatar`, `verified`) [src/components/prompts/discovery-prompts.tsx:24-26]().
  - Category with its optional parent [src/components/prompts/discovery-prompts.tsx:27-33]().
  - Tags via join table with `tag` details [src/components/prompts/discovery-prompts.tsx:34-36]().
  - Contributors list (users who contributed) [src/components/prompts/discovery-prompts.tsx:37-39]().
  - Aggregate counts of votes, contributors, and workflow connections, excluding AI "related" links [src/components/prompts/discovery-prompts.tsx:40-47]().

- Six parallel Prisma queries using `Promise.all` fetch distinct prompt collections representing curated categories [src/components/prompts/discovery-prompts.tsx:54-135]():
  1. **Trending Prompts** (Homepage only): Filtered via `trendingPromptListWhere()`, ordered by `trendingUntil` and `createdAt` [src/components/prompts/discovery-prompts.tsx:55-62]().
  2. **Featured Prompts**: `isFeatured: true` with descending `featuredAt` date [src/components/prompts/discovery-prompts.tsx:63-74]().
  3. **Today's Most Upvoted**: Prompts with votes recorded since today's midnight, ranked by total vote count [src/components/prompts/discovery-prompts.tsx:75-97]().
  4. **Latest Prompts**: Newly created prompts, ordered by creation date descending [src/components/prompts/discovery-prompts.tsx:98-108]().
  5. **Recently Updated**: Prompts ordered by last update timestamp descending [src/components/prompts/discovery-prompts.tsx:109-119]().
  6. **Most Contributed**: Prompts ordered by descending count of contributors [src/components/prompts/discovery-prompts.tsx:120-134]().

- Each query applies global visibility filters ensuring prompts are public (`isPrivate: false`), listed (`isUnlisted: false`), non-deleted (`deletedAt: null`), and non-bot (`...NON_BOT_PROMPTS`) [src/components/prompts/discovery-prompts.tsx:64-69, 77-82, 99-104, 110-115, 121-126]().

- A helper function `mapPrompt` maps each raw prompt result to add vote and contributor counts explicitly to the returned object along with contributors details [src/components/prompts/discovery-prompts.tsx:137-142]().

- In the JSX output, each section is conditionally rendered based on the presence of results. Each renders a section header with appropriate Lucide icons and an action button linking to the full catalog, followed by a Masonry grid layout displaying all prompt cards in that section [src/components/prompts/discovery-prompts.tsx:151-205]().

Sources:
- `src/components/prompts/discovery-prompts.tsx:13-205`

---

## System Architecture

### Discovery Data Flow

The following diagram illustrates how entry-point pages leverage the `DiscoveryPrompts` component, Database models (`Prompt`, `PromptVote`, `User`, `Category`, `Tag`, `PromptTag`, `PromptConnection`), and helper utilities to render curated prompt lists.

```mermaid
graph TD
    subgraph "Natural-Language-Space"
        HomePage["src/app/page.tsx"]
        DiscoveryPage["src/app/discover/page.tsx"]
    end

    subgraph "Code-Entity-Space"
        DPComp["DiscoveryPrompts src/components/prompts/discovery-prompts.tsx"]
        QueryRunner["Promise.all() Queries"]
        MapFn["mapPrompt() Utility"]
    end

    subgraph "Database"
        PromptTable[("Model Prompt")]
        PromptVoteTable[("Model PromptVote")]
        UserTable[("Model User")]
        CategoryTable[("Model Category")]
        TagTable[("Model Tag")]
        PromptTagTable[("Model PromptTag")]
        PromptConnectionTable[("Model PromptConnection")]
    end

    HomePage --> DPComp
    DiscoveryPage --> DPComp
    DPComp --> QueryRunner
    
    QueryRunner -- "findMany" --> PromptTable

    PromptTable -- "Includes" --> UserTable
    PromptTable -- "Includes" --> CategoryTable
    PromptTable -- "Includes" --> PromptTagTable
    PromptTagTable -- "Includes" --> TagTable
    PromptTagTable -- "Includes" --> PromptVoteTable
    PromptTagTable -- "Includes" --> PromptConnectionTable

    PromptTable -.-> MapFn
    MapFn --> UI["Render with Masonry & PromptCard"]
```

Sources:
- `src/components/prompts/discovery-prompts.tsx:16-150`
- `src/app/feed/page.tsx`

---

## Ranking & Velocity Logic

### Daily Ranking of Most Upvoted Prompts

- The code computes today's date at midnight in local time for filtering votes occurring today [src/components/prompts/discovery-prompts.tsx:51-52]().
- The Prisma query restricts votes to those created on or after this timestamp to isolate today's voting activity [src/components/prompts/discovery-prompts.tsx:82-88]().
- Results are ordered by the count of today's votes descending to surface trending prompts dynamically each day [src/components/prompts/discovery-prompts.tsx:90-94]().

### Content Velocity

- **Latest Prompts** are selected by sorting on the creation timestamp descending to show newly contributed content [src/components/prompts/discovery-prompts.tsx:105]().
- **Recently Updated** prompts use the updated timestamp field, reflecting prompt edits or changes to keep content fresh [src/components/prompts/discovery-prompts.tsx:116]().
- Sorting by these timestamps provides a time-sensitive freshness metric for discovery.

### Collaborative Discovery

- The **Most Contributed** list ranks prompts by the number of distinct contributors participating in their editing or updating [src/components/prompts/discovery-prompts.tsx:127-131]().
- This encourages transparency and highlights heavily community-maintained prompts.
- The contributors count is accessed through a relation count aggregation in Prisma.

Sources:
- `src/components/prompts/discovery-prompts.tsx:51-134`

---

## Widget Cards & Injected Discovery

Beyond curated prompt lists, the system supports **widget cards** for promotional or sponsored content insertion within prompt browsing lists using a widget plugin architecture.

### Widget Plugin System Overview

- Widgets are encapsulated as implementations of the `WidgetPlugin` and `WidgetPrompt` interfaces [src/lib/plugins/widgets/index.ts:1-8]().
- The registry `widgetPlugins` maintains all active widget plugins [src/lib/plugins/widgets/index.ts:18-24]().
- Widget prompts define metadata, rendering components, action links, tags, categories, and importantly, **injection rules**:
  - `shouldInject(context)` is a callback function evaluating if the widget should be included based on filtering context (search query, category, tags, etc.) [src/lib/plugins/widgets/textream.tsx:122-148]().
  - `positioning` configures where and how often the widget should be injected: either "once" at a position or repeating every N items with a maximum count [src/lib/plugins/widgets/book.tsx:157-162](), [src/lib/plugins/widgets/index.ts:72-103]().

### Injection Pipeline (`injectWidgets`)

- The core function `injectWidgets(items, context)` injects widget prompts into a list of items based on filter context and positioning logic [src/lib/plugins/widgets/index.ts:121-182]().
- Injection algorithm:
  1. Fetch all widget prompts from the registry via `getWidgetPrompts()` [src/lib/plugins/widgets/index.ts:36-38]().
  2. Filter widgets by running `shouldInject` with the current search/category/tag context [src/lib/plugins/widgets/index.ts:140-146]().
  3. Calculate insertion positions using `getWidgetInsertionPositions` based on the widget's positioning mode [src/lib/plugins/widgets/index.ts:72-103]():
     - `"once"`: Inserted at a single defined position [src/lib/plugins/widgets/index.ts:81-84]().
     - `"repeat"`: Inserted repeatedly every N items up to a max count [src/lib/plugins/widgets/index.ts:86-100]().
  4. Sort insertions by position and splice them into the original items array, marking injected widgets with `isWidget: true` and `instanceIndex` for identification [src/lib/plugins/widgets/index.ts:153-178]().
- This process enables non-intrusive, context-aware promotional content interspersed with prompt results.

### Widget Plugin Examples

- **Book Widget**: Promotes the "Interactive Book of Prompting," repeating every 60 items, max 4 times, excluded from skills/tastes pages [src/lib/plugins/widgets/book.tsx:142-173]().
- **Textream Widget**: Highlights the Textream macOS teleprompter app, repeats every 45 items, max 3 times, filtered by relevant keywords and categories [src/lib/plugins/widgets/textream.tsx:101-152]().

### Widget Injection Architecture

The following diagram illustrates how the `InfinitePromptList` component interfaces with `injectWidgets`, widget plugin registry functions, and widget implementations.

```mermaid
graph TD
    subgraph "Natural-Language-Space"
        InfiniteList["InfinitePromptList src/components/prompts/infinite-prompt-list.tsx"]
    end

    subgraph "Code-Entity-Space"
        WidgetEngine["injectWidgets src/lib/plugins/widgets/index.ts"]
        PositionCalc["getWidgetInsertionPositions src/lib/plugins/widgets/index.ts"]
        PluginRegistry["getWidgetPlugins src/lib/plugins/widgets/index.ts"]
    end

    subgraph "Widget-Implementations"
        CodeRabbit["coderabbitWidget src/lib/plugins/widgets/coderabbit.ts"]
        Book["bookWidget src/lib/plugins/widgets/book.tsx"]
        Textream["textreamWidget src/lib/plugins/widgets/textream.tsx"]
    end

    InfiniteList --> WidgetEngine
    WidgetEngine --> PluginRegistry
    PluginRegistry --> CodeRabbit
    PluginRegistry --> Book
    PluginRegistry --> Textream
    
    WidgetEngine --> PositionCalc
    PositionCalc --> InfiniteList
    InfiniteList --> UI["PromptCard & WidgetCard"]
```

Sources:
- `src/lib/plugins/widgets/index.ts:1-182`
- `src/lib/plugins/widgets/book.tsx:142-173`
- `src/lib/plugins/widgets/textream.tsx:101-152`
- `src/components/prompts/infinite-prompt-list.tsx:51-200`

---

## Integration with Infinite Prompt List

The `InfinitePromptList` client component [src/components/prompts/infinite-prompt-list.tsx:51-200]() is responsible for client-side infinite scrolling of prompt lists with filtering support. It integrates the widget injection system by passing loaded prompts along with current filter criteria to `injectWidgets()` for display.

- Widgets decide their injection dynamically, ensuring non-conflicting and contextually relevant promo placements.
- Injection only occurs after client-side mount to avoid hydration mismatches [src/components/prompts/infinite-prompt-list.tsx:68-71]().
- The resulting mixed list consists of normal prompt cards and widget cards.

Sources:
- `src/components/prompts/infinite-prompt-list.tsx:51-200`

---

## Summary

- `DiscoveryPrompts` is the core server-side component rendering key sections of curated prompts using Prisma queries with consistent relations and filters.
- Daily voting counts enable fresh trending rankings, while creation and update timestamps provide content velocity signals.
- Contributor counts highlight collaborative community contributions.
- Widget plugins extend discovery with flexible promotional cards, conditionally injected based on browsing context and positioning rules.
- Client-side infinite scrolling integrates widget injection for a seamless mixed browsing experience.

This architecture ensures rich, dynamic, socially-informed prompt discovery combined with extensible promotional capabilities.

---

### Sources

- `src/components/prompts/discovery-prompts.tsx:13-205`
- `src/lib/plugins/widgets/index.ts:1-182`
- `src/lib/plugins/widgets/book.tsx:142-173`
- `src/lib/plugins/widgets/textream.tsx:101-152`
- `src/components/prompts/infinite-prompt-list.tsx:51-200`
- `src/app/feed/page.tsx`

---

# Page: SEO & Social Metadata

# SEO & Social Metadata

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/bots/[slug]/opengraph-image.tsx](src/app/bots/[slug]/opengraph-image.tsx)
- [src/app/bots/[slug]/twitter-image.tsx](src/app/bots/[slug]/twitter-image.tsx)
- [src/app/bots/opengraph-image.tsx](src/app/bots/opengraph-image.tsx)
- [src/app/bots/page.tsx](src/app/bots/page.tsx)
- [src/app/bots/twitter-image.tsx](src/app/bots/twitter-image.tsx)
- [src/app/categories/(index)/page.tsx](src/app/categories/(index)/page.tsx)
- [src/app/discover/page.tsx](src/app/discover/page.tsx)
- [src/app/robots.ts](src/app/robots.ts)
- [src/app/sitemap.ts](src/app/sitemap.ts)
- [src/app/tags/(index)/page.tsx](src/app/tags/(index)/page.tsx)
- [src/components/bots/bot-analytics.tsx](src/components/bots/bot-analytics.tsx)
- [src/components/layout/sponsor-link.tsx](src/components/layout/sponsor-link.tsx)
- [src/components/seo/structured-data.tsx](src/components/seo/structured-data.tsx)
- [src/lib/analytics.ts](src/lib/analytics.ts)

</details>



## Purpose and Scope
This page documents the SEO and social metadata systems within `prompts.chat`, covering structured data components (JSON-LD), sitemap and robots configuration, OpenGraph and Twitter image generation, SEO metadata building utilities, and analytics instrumentation for tracking user interactions. These subsystems ensure enhanced search engine visibility, controlled web crawler behavior, rich social media previews, and detailed telemetry.

---

## 1. Structured Data & JSON-LD Components

Structured data markup is implemented via `src/components/seo/structured-data.tsx`, which exports the `JsonLd` component alongside schema generation helpers such as `breadcrumbSchema`, `collectionPageSchema`, `promptSchema`, and `promptHowToSchema` [src/components/seo/structured-data.tsx:12-216]().

### Key Elements

- **`JsonLd` Component:**  
  Accepts a `data` object or array of schemas and renders a `<script type="application/ld+json">` tag, safely escaping `<` characters to prevent script injection [src/components/seo/structured-data.tsx:12-19]().

- **Schema Generators:**
  - **`breadcrumbSchema`**: Generates a `BreadcrumbList` schema linking navigation items to their absolute URLs using `absoluteUrl()` [src/components/seo/structured-data.tsx:21-32]().
  - **`collectionPageSchema`**: Formats a `CollectionPage` schema containing an `ItemList` of items for listing pages like categories, tags, or discovery views [src/components/seo/structured-data.tsx:44-65]().
  - **`promptSchema`**: Describes individual prompt pages as a `SocialMediaPosting` entity, incorporating headline, description, truncated text, publish/modified dates, author profile info, category/keywords, vote interaction statistics, and a nested comment tree handled by `commentTreeSchema` [src/components/seo/structured-data.tsx:131-180]().
  - **`promptHowToSchema`**: Preserves the original `HowTo` guide representation for prompt instructions [src/components/seo/structured-data.tsx:201-216]().

### Structured Data Entity Mapping Diagram

The following diagram bridges natural language discovery concepts to the underlying code entities inside `src/components/seo/structured-data.tsx`:

```mermaid
graph TD
    UserRequest[""Natural Language Page Request""] --> PageRouter[""Next.js App Router""]
    PageRouter --> ListingCheck{"Page Type Evaluation"}
    
    ListingCheck -- "/categories or /tags" --> ColSchema[""collectionPageSchema() in src/components/seo/structured-data.tsx""]
    ListingCheck -- "/prompts/[id]" --> PrmSchema[""promptSchema() in src/components/seo/structured-data.tsx""]
    ListingCheck -- "/discover" --> BrdSchema[""breadcrumbSchema() in src/components/seo/structured-data.tsx""]
    
    ColSchema --> JsonLdComp[""JsonLd component in src/components/seo/structured-data.tsx""]
    PrmSchema --> JsonLdComp
    BrdSchema --> JsonLdComp
    
    JsonLdComp --> OutputTag[""Render <script type='application/ld+json'>"""]

    classDef default fill:none,stroke:#000,stroke-width:1px;
```
Sources: `src/components/seo/structured-data.tsx:1-216`

---

## 2. Sitemap & Robots Configuration

Search engine crawler indexing is governed by `sitemap.ts` and `robots.ts`.

### Sitemap Generation (`src/app/sitemap.ts`)

- **Revalidation & Limits:**  
  Configured to revalidate every 5 minutes (`revalidate = 300`) to ensure fresh indexing [src/app/sitemap.ts:8-10](). Sets `MAX_PROMPTS = 45000` and `MIN_LISTING_PROMPTS = 3` to prevent thin pages from cluttering the sitemap [src/app/sitemap.ts:15-19]().
- **Static & Dynamic Entries:**  
  Combines static core routes (`/`, `/bots`, `/prompts`, `/discover`, etc.), dynamic book chapters via `getAllChapters()`, categories, tags, author profile pages (`/@username`), bots, bot teams, and public prompts [src/app/sitemap.ts:35-174]().
- **Image Sitemaps:**  
  Image prompts (`type === "IMAGE"`) include associated image sitemap elements processed through `toSitemapImageUrl` [src/app/sitemap.ts:153-160]().
- **Database Resilience:**  
  Wrapped in a `try/catch` block that gracefully falls back to static and book pages if the database is unavailable during build time [src/app/sitemap.ts:64-177]().

### Robots Instructions (`src/app/robots.ts`)

- Implements `robots()` returning rules that allow all user agents (`userAgent: "*"`) to access `/`, while disallowing crawler access to `/api/`, `/admin/`, `/settings/`, `/login`, `/register`, and signed-in-only routes (e.g., `/feed`, `/collection`, prompt/bot creation and edit paths) [src/app/robots.ts:4-31]().
- Points crawlers to `${baseUrl}/sitemap.xml` [src/app/robots.ts:29]().

### Sitemap & Crawler Pipeline Diagram

```mermaid
graph TD
    CrawlerReq[""Search Engine Crawler Request /sitemap.xml""] --> SitemapFunc[""sitemap() in src/app/sitemap.ts""]
    SitemapFunc --> StaticPaths[""Static Routes Array"""]
    SitemapFunc --> BookChapters["""getAllChapters() from src/lib/book/chapters.ts""]
    SitemapFunc --> DBQuery[""Parallel Prisma Queries: db.prompt, db.category, db.tag, db.botTeam""]
    
    DBQuery --> FilterRecords[""Apply listedPromptFilter & visiblePromptFilter""]
    FilterRecords --> ImageMapping["""toSitemapImageUrl() in src/lib/seo.ts""]
    
    StaticPaths --> Combine[""Merge MetadataRoute.Sitemap Entries""]
    BookChapters --> Combine
    ImageMapping --> Combine
    
    Combine --> XMLResponse[""Return XML Sitemap""]

    classDef default fill:none,stroke:#000,stroke-width:1px;
```
Sources: `src/app/sitemap.ts:1-182`, `src/app/robots.ts:1-31`

---

## 3. SEO Utilities & Page Metadata (`src/lib/seo.ts`)

The `src/lib/seo.ts` module provides robust helper functions for URL handling, metadata construction, and text sanitization.

- **`getBaseUrl()`**: Resolves the site origin from `NEXTAUTH_URL` or defaults to `https://prompts.chat`, stripping any trailing slashes [src/lib/seo.ts:29-31]().
- **`absoluteUrl(path)`**: Ensures relative site paths are correctly prefixed with the site origin [src/lib/seo.ts:36-39]().
- **`paginatedPath(path, page)`**: Appends `?page=N` for pages greater than 1 [src/lib/seo.ts:45-47]().
- **`toMetaDescription(text, maxLength)`**: Strips markdown formatting, prompt variable syntax (`${variable}`), and collapses whitespace to generate concise meta descriptions [src/lib/seo.ts:53-74]().
- **`escapeXml(value)` & `toSitemapImageUrl(mediaUrl)`**: Sanitizes URLs and XML entities for sitemap compatibility [src/lib/seo.ts:81-101]().
- **`buildPageMetadata(options)`**: Centralized helper returning consistent Next.js `Metadata` objects containing title templates, self-referencing canonical links, OpenGraph cards, Twitter cards, and optional `noindex` robots directives [src/lib/seo.ts:134-169]().

Sources: `src/lib/seo.ts:1-170`

---

## 4. OpenGraph & Social Image Generation

Social sharing previews are standardized across the platform:
- Site-wide defaults are provided by `src/app/opengraph-image.png` and `src/app/twitter-image.png`.
- Dynamic routes (such as prompts and bots) leverage Next.js App Router conventions with dedicated `opengraph-image.tsx` and `twitter-image.tsx` files per segment [src/app/bots/opengraph-image.tsx](), [src/app/bots/[slug]/opengraph-image.tsx]().
- For prompt pages, `src/app/prompts/[id]/opengraph-image.tsx` dynamically generates an image based on prompt details, including title, content, author, votes, and contributors [src/app/prompts/[id]/opengraph-image.tsx:1-362](). It uses `ImageResponse` from `next/og` to create a PNG image with custom styling based on the application's theme configuration [src/app/prompts/[id]/opengraph-image.tsx:121-362]().
- Similarly, bot pages have `src/app/bots/[slug]/opengraph-image.tsx` and `src/app/bots/[slug]/twitter-image.tsx` for dynamic image generation.

Sources: `src/app/bots/opengraph-image.tsx`, `src/app/bots/[slug]/opengraph-image.tsx`, `src/app/bots/[slug]/twitter-image.tsx`, `src/app/prompts/[id]/opengraph-image.tsx:1-362`

---

## 5. Analytics Instrumentation & Event Tracking

User telemetry and interaction tracking are handled via `src/lib/analytics.ts`, which interfaces with Google Analytics (`window.gtag`) when configured [src/lib/analytics.ts:1-35]().

- **`trackEvent`**: Checks `window.gtag` availability before dispatching structured event payloads [src/lib/analytics.ts:26-35]().
- **Domain Event Objects**: Organized into typed namespaces like `analyticsAuth`, `analyticsPrompt`, and `analyticsBot`, capturing user actions (e.g., login, prompt view, upvote, run, bot installation clicks) [src/lib/analytics.ts:41-284]().
- **Sentry Integration**: Error tracking and performance monitoring are implemented using Sentry.
    - `src/instrumentation-client.ts` configures Sentry for client-side errors, including replay integration, session sampling, and filtering out common browser extension errors [src/instrumentation-client.ts:1-79](). It also exports `onRouterTransitionStart` for tracking page transitions [src/instrumentation-client.ts:81]().
    - `sentry.server.config.ts` and `sentry.edge.config.ts` configure Sentry for server-side and edge environments, respectively, with similar settings for DSN, sampling rates, and PII handling [sentry.server.config.ts:1-22](), [sentry.edge.config.ts:1-23](). Sentry is enabled only in production environments.

Sources: `src/lib/analytics.ts:1-284`, `src/instrumentation-client.ts:1-82`, `sentry.server.config.ts:1-22`, `sentry.edge.config.ts:1-23`

---

# Summary

This page documented the technical implementation of SEO and social metadata systems in `prompts.chat`:
- **Structured Data**: JSON-LD schemas (`JsonLd`, `promptSchema`, `collectionPageSchema`, `breadcrumbSchema`) enhance rich snippets.
- **Sitemap & Robots**: `sitemap.ts` and `robots.ts` coordinate crawler visibility, image sitemaps, and revalidation.
- **SEO Utilities**: `src/lib/seo.ts` centralizes `buildPageMetadata`, `toMetaDescription`, and URL resolution.
- **Analytics**: `src/lib/analytics.ts` instruments typed user interaction tracking, complemented by Sentry for error and performance monitoring across client, server, and edge environments.

---

# Page: Educational Content

# Educational Content

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/book/[slug]/page.tsx](src/app/book/[slug]/page.tsx)
- [src/app/book/page.tsx](src/app/book/page.tsx)
- [src/components/book/sidebar.tsx](src/components/book/sidebar.tsx)
- [src/content/book/00b-history.mdx](src/content/book/00b-history.mdx)
- [src/content/book/00c-introduction.mdx](src/content/book/00c-introduction.mdx)
- [src/content/book/01-understanding-ai-models.mdx](src/content/book/01-understanding-ai-models.mdx)
- [src/content/book/09-json-yaml-prompting.mdx](src/content/book/09-json-yaml-prompting.mdx)
- [src/content/book/tr/00b-history.mdx](src/content/book/tr/00b-history.mdx)
- [src/content/book/tr/00c-introduction.mdx](src/content/book/tr/00c-introduction.mdx)

</details>



The Educational Content system comprises learning-focused features designed to teach users how to effectively write and use AI prompts. This section acts as a parent page for three distinct learning paths: a gamified kids learning game, an interactive book for comprehensive prompt engineering, and in-app prompt writing guides. These features are separate from the core prompt library functionality and provide structured educational experiences for users of all ages.

For detailed information about specific learning features, refer to the child pages:
- [Kids Learning Game](#7.1) — Gamified world-map structure with worlds, levels, and interactive mini-games.
- [Interactive Book](#7.2) — Comprehensive multi-chapter guide with MDX pipeline, interactive demos, translations, and bookmarking.
- [Prompt Writing Guide](#7.3) — In-app guides for writing effective prompts using frameworks like C.R.A.F.T.

---

## Educational Content Architecture

The educational content system is built as a modular vertical feature within the application, utilizing specialized components, localized namespaces, and dedicated routing structures (`/kids/*` and `/book/*`).

### Diagram: Natural Language Space to Code Entity Space (Educational Features)
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        KidsGame["Kids Learning Game"]
        PromptBook["Interactive Book"]
    end
    
    subgraph "CodeEntitySpace"
        KidsRoute["/kids/*<br/>src/app/kids/layout.tsx"]
        BookRoute["/book/*<br/>src/app/book/page.tsx"]
        
        subgraph "KidsGameComponents"
            LevelWrapper["LevelContentWrapper<br/>src/components/kids/layout/level-content-wrapper.tsx"]
            ProgressLib["progress.ts<br/>src/lib/kids/progress.ts"]
            SectionComp["Section<br/>src/components/kids/elements/index.tsx"]
            KidsHeaderComp["KidsHeader<br/>src/components/kids/layout/kids-header.tsx"]
        end

        subgraph "InteractiveBookComponents"
            BookHomePage["BookHomePage<br/>src/app/book/page.tsx"]
            BookSidebar["SidebarContent<br/>src/components/book/sidebar.tsx"]
            BookBookmark["useBookmark<br/>src/components/book/sidebar.tsx"]
            ContinueBtn["ContinueReadingButton<br/>src/components/book/continue-reading.tsx"]
        end
    end
    
    KidsGame --> KidsRoute
    KidsRoute --> LevelWrapper
    LevelWrapper --> SectionComp
    LevelWrapper --> ProgressLib
    KidsRoute --> KidsHeaderComp

    PromptBook --> BookRoute
    BookRoute --> BookHomePage
    BookRoute --> BookSidebar
    BookRoute --> BookBookmark
    BookHomePage --> ContinueBtn
```
Sources: [src/app/book/page.tsx:115-137](), [src/components/book/sidebar.tsx:42-72](), [src/components/kids/layout/level-content-wrapper.tsx:13-30](), [src/components/kids/layout/kids-header.tsx:45-53]()

---

## Interactive Book Execution and Pipeline

### Diagram: Interactive Book Rendering and Pipeline Architecture
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        UserReading["User Reading Chapter"]
    end

    subgraph "CodeEntitySpace"
        ChapterSlugRoute["src/app/book/[slug]/page.tsx"]
        MDXImporter["dynamicImport<br/>src/content/book/[locale]/[slug].mdx"]
        SidebarComp["SidebarContent<br/>src/components/book/sidebar.tsx"]
        BookmarkStorage["useBookmark<br/>src/components/book/sidebar.tsx"]
    end

    UserReading --> ChapterSlugRoute
    ChapterSlugRoute --> MDXImporter
    ChapterSlugRoute --> SidebarComp
    SidebarComp --> BookmarkStorage
```
Sources: [src/app/book/[slug]/page.tsx:89-168](), [src/components/book/sidebar.tsx:42-65](), [src/components/book/sidebar.tsx:67-189]()

---

## 7.1 Kids Learning Game

The kids section provides a gamified environment where younger learners explore prompt concepts through a world-map structure, earning stars and completing interactive mini-games like quizzes, drag-and-drop puzzles, magic words, and word predictors. This component model leverages wrapped level content with progress state and interactive elements to keep engagement high.

For details, see [Kids Learning Game](#7.1).

Sources: [src/components/kids/layout/level-content-wrapper.tsx:13-30](), [src/components/kids/layout/kids-header.tsx:45-53]()

---

## 7.2 Interactive Book

The interactive book serves as a deeply structured educational guide to prompt engineering, with content organized into chapters and parts, authored using MDX files [src/content/book/00c-introduction.mdx:1-125](), [src/content/book/01-understanding-ai-models.mdx:1-110](). The MDX pipeline in `src/app/book/[slug]/page.tsx` allows for rich interactive demos, exercises, and continue-reading features embedded throughout [src/app/book/page.tsx:115-205](), [src/app/book/[slug]/page.tsx:147-168](). Multi-language translations are supported via locale-specific overrides and translation dictionaries.

A client-side bookmarking system tracks reading progress using `localStorage` through the `useBookmark` hook [src/components/book/sidebar.tsx:42-65](), enabling users to easily resume where they left off [src/app/book/page.tsx:137-137](). The sidebar navigation component `SidebarContent` dynamically filters chapters and parts, including search capabilities and bookmark toggling [src/components/book/sidebar.tsx:67-189]().

For details, see [Interactive Book](#7.2).

Sources: [src/app/book/page.tsx:115-205](), [src/app/book/[slug]/page.tsx:89-168](), [src/components/book/sidebar.tsx:42-189](), [src/content/book/00c-introduction.mdx:1-125]()

---

## 7.3 Prompt Writing Guide

Within the application, dedicated prompt writing guides offer step-by-step instructions and frameworks such as C.R.A.F.T. These in-app resources present best practices for crafting effective prompts, covering clarity, relevance, audience consideration, formatting, and testing strategies.

The guides include presentation slide decks and prompt templates that users can apply directly in their workflows, helping bridge theory and practice efficiently.

For details, see [Prompt Writing Guide](#7.3).

Sources: [src/app/book/page.tsx:119-126]()

---

# Page: Kids Learning Game

# Kids Learning Game

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [public/book-cover-photo.jpg](public/book-cover-photo.jpg)
- [public/book-cover.jpg](public/book-cover.jpg)
- [src/app/globals.css](src/app/globals.css)
- [src/components/kids/elements/drag-drop-prompt.tsx](src/components/kids/elements/drag-drop-prompt.tsx)
- [src/components/kids/elements/example-matcher.tsx](src/components/kids/elements/example-matcher.tsx)
- [src/components/kids/elements/magic-words.tsx](src/components/kids/elements/magic-words.tsx)
- [src/components/kids/elements/pixel-art.tsx](src/components/kids/elements/pixel-art.tsx)
- [src/components/kids/elements/progress-map.tsx](src/components/kids/elements/progress-map.tsx)
- [src/components/kids/elements/prompt-vs-mistake.tsx](src/components/kids/elements/prompt-vs-mistake.tsx)
- [src/components/kids/elements/story-scene.tsx](src/components/kids/elements/story-scene.tsx)
- [src/components/kids/elements/word-predictor.tsx](src/components/kids/elements/word-predictor.tsx)
- [src/components/kids/layout/kids-header.tsx](src/components/kids/layout/kids-header.tsx)
- [src/components/kids/layout/kids-home-content.tsx](src/components/kids/layout/kids-home-content.tsx)
- [src/components/kids/layout/level-content-wrapper.tsx](src/components/kids/layout/level-content-wrapper.tsx)
- [src/components/kids/layout/settings-modal.tsx](src/components/kids/layout/settings-modal.tsx)
- [src/components/layout/animated-text.tsx](src/components/layout/animated-text.tsx)
- [src/components/prompts/hero-categories.tsx](src/components/prompts/hero-categories.tsx)

</details>



## Purpose and Scope

This document details the architecture and implementation of the Kids Learning Game subsystem within `prompts.chat`. It is a pixel-art themed educational platform designed to teach children and beginners the core concepts of AI prompt engineering through gamified worlds, levels, and interactive exercises. The system comprises multiple worlds containing total levels [src/components/kids/layout/kids-header.tsx:19-24](), a star collection mechanism, multilingual support [src/components/kids/layout/kids-header.tsx:14](), and robust local state persistence [src/components/kids/elements/prompt-vs-mistake.tsx:56-65]().

Sources: [src/components/kids/layout/kids-header.tsx:19-24](), [src/components/kids/elements/prompt-vs-mistake.tsx:56-65]()

---

## System Overview & Architecture

The Kids Learning Game runs as a modular section under the `/kids/*` route space. It leverages Next.js App Router layout patterns, client-side React hooks, and `localStorage` to deliver a responsive, zero-backend persistence gaming experience.

### Architecture Bridge: Concepts to Code Entities

The following diagram bridges high-level game concepts (Natural Language Space) to their concrete implementation classes, files, and functions within the codebase (Code Entity Space).

Title: "Natural Language Space to Code Entity Space Mapping"
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        ConceptQuiz["Prompt vs Mistake Quiz"]
        ConceptDrag["Drag and Drop Builder"]
        ConceptMagic["Magic Words Blanks"]
        ConceptPredict["Word Predictor AI"]
        ConceptProgress["Progress & Stars"]
    end

    subgraph "CodeEntitySpace"
        FileQuiz["PromptVsMistake<br/>src/components/kids/elements/prompt-vs-mistake.tsx"]
        FileDrag["DragDropPrompt<br/>src/components/kids/elements/drag-drop-prompt.tsx"]
        FileMagic["MagicWords<br/>src/components/kids/elements/magic-words.tsx"]
        FilePredict["WordPredictor<br/>src/components/kids/elements/word-predictor.tsx"]
        FileProgress["progress.ts<br/>src/lib/kids/progress.ts"]
    end

    ConceptQuiz --> FileQuiz
    ConceptDrag --> FileDrag
    ConceptMagic --> FileMagic
    ConceptPredict --> FilePredict
    ConceptProgress --> FileProgress
```

Sources: [src/components/kids/elements/prompt-vs-mistake.tsx:24-101](), [src/components/kids/elements/drag-drop-prompt.tsx:24-153](), [src/components/kids/elements/magic-words.tsx:31-180](), [src/components/kids/elements/word-predictor.tsx:25-97]()

---

## Component Architecture & Level Execution

The level runtime is managed by the `LevelContentWrapper` component, which wraps level MDX content, coordinates section progression, and validates interactive requirements [src/components/kids/layout/level-content-wrapper.tsx:19-165]().

### Section Navigation and Completion Guards
- **Section Extraction**: MDX children are parsed into discrete `Section` blocks [src/components/kids/layout/level-content-wrapper.tsx:79-103]().
- **Gated Progression**: Users cannot advance via the footer "Next" button unless `isCurrentSectionComplete` returns `true`, verifying that interactive elements within the section have been successfully completed [src/components/kids/layout/level-content-wrapper.tsx:124-143]().
- **Polling Sync**: `LevelContentWrapper` periodically queries storage status every 500ms to ensure reactive updates when components trigger completion handlers [src/components/kids/layout/level-content-wrapper.tsx:38-51]().

### Interactive Game Elements

| Game Type         | Component File                                              | Core Mechanism                                                                                          |
|-------------------|-------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| **Prompt vs Mistake** | [src/components/kids/elements/prompt-vs-mistake.tsx]()      | Binary choice evaluating structured "good" vs "bad" prompt options with immediate feedback [src/components/kids/elements/prompt-vs-mistake.tsx:78-86](). |
| **Drag & Drop**       | [src/components/kids/elements/drag-drop-prompt.tsx]()       | Pointer and touch-driven reordering of sequence tokens with drag offsets and drop target calculations [src/components/kids/elements/drag-drop-prompt.tsx:101-115](). |
| **Magic Words**       | [src/components/kids/elements/magic-words.tsx]()             | Word bank token placement into sentence blank slots (`_` or `{{}}`) with drag/drop and click interaction [src/components/kids/elements/magic-words.tsx:118-165](). |
| **Word Predictor**    | [src/components/kids/elements/word-predictor.tsx]()          | Multiple-choice evaluation simulating AI token generation based on surrounding sentence context [src/components/kids/elements/word-predictor.tsx:79-92](). |

All these components register their interactive sections to the level navigation context and persist per-level progress using component-scoped identifiers, leveraging hooks for synchronized `localStorage` state save/load [src/components/kids/elements/prompt-vs-mistake.tsx:56-76]().

Sources: [src/components/kids/layout/level-content-wrapper.tsx:19-165](), [src/components/kids/elements/prompt-vs-mistake.tsx:24-101](), [src/components/kids/elements/drag-drop-prompt.tsx:24-153](), [src/components/kids/elements/magic-words.tsx:31-180](), [src/components/kids/elements/word-predictor.tsx:25-97]()

---

## Data Flow & Persistent Progress Tracking

Progress persistence is handled entirely on the client side, using wrapper functions around `localStorage`. Interactive elements save and load their state keyed by level slug and component ID, enabling state restoration on page reloads. Completion marking triggers unlocking of next sections or levels in the game world.

### Persistence Data Flow Bridge

Title: "Persistence Data Flow to Storage Space"
```mermaid
graph LR
    subgraph "UserActions"
        CompleteTask["User Completes Interactive Task"]
        LoadComponent["Component Mounts & Loads Saved State"]
    end

    subgraph "CodeFunctions"
        MarkSection["markSectionCompleted()<br/>src/components/kids/elements/prompt-vs-mistake.tsx"]
        SaveState["saveComponentState()<br/>src/components/kids/elements/prompt-vs-mistake.tsx"]
        LoadState["getComponentState()<br/>src/components/kids/elements/prompt-vs-mistake.tsx"]
    end

    subgraph "Storage"
        LS["localStorage<br/>'kids-progress' JSON"]
    end

    CompleteTask -->|Triggers| MarkSection
    CompleteTask -->|Triggers| SaveState
    LoadComponent -->|Queries| LoadState

    MarkSection --> LS
    SaveState --> LS
    LoadState --> LS
```

### Key Persistence Functions

- `markSectionCompleted(levelSlug: string, sectionIndex: number)`: Marks a particular section of a level as completed, updating progress and star counts [src/components/kids/elements/prompt-vs-mistake.tsx:83-83]().
- `saveComponentState<T>(levelSlug: string, componentId: string, state: T)`: Saves component-specific UI and interaction state for continuity [src/components/kids/elements/prompt-vs-mistake.tsx:71-75]().
- `getComponentState<T>(levelSlug: string, componentId: string)`: Retrieves previously saved component state [src/components/kids/elements/prompt-vs-mistake.tsx:56-56]().

Sources: [src/components/kids/elements/prompt-vs-mistake.tsx:56-86](), [src/components/kids/elements/drag-drop-prompt.tsx:75-98](), [src/components/kids/elements/magic-words.tsx:80-102]()

---

## Visual System, Pixel Art & Theming

The Kids Learning Game uses a retro pixel art style with consistent UI theming:

- **Clip Paths**: Sections use `clip-path` CSS polygons with stepped edges to mimic pixel panel borders, e.g., `pixelClipPath`, `smallPixelClipPath` for framing interactive cards [src/components/kids/elements/prompt-vs-mistake.tsx:104-105]().
- **SVG Pixel Art**: Components such as `PixelRobot`, `PixelStar`, `PixelTree`, and `PixelCastle` are SVGs with `imageRendering: pixelated` for crisp pixel effects [src/components/kids/layout/kids-header.tsx:48-53](), [src/components/kids/elements/pixel-art.tsx:6-26]().
- **Mascot**: The character "Promi" (`PixelRobot`) changes expression moods dynamically based on context [src/components/kids/elements/prompt-vs-mistake.tsx:112]().
- **Settings Modal**: Allows language selection, background music toggle, and progress reset [src/components/kids/layout/settings-modal.tsx:57-91]().

This visual system enhances appeal for kids while maintaining clear and consistent UI affordances for interactivity.

Sources: [src/components/kids/elements/prompt-vs-mistake.tsx:104-105](), [src/components/kids/layout/kids-header.tsx:48-53](), [src/components/kids/elements/pixel-art.tsx:6-26](), [src/components/kids/layout/settings-modal.tsx:57-91]()

---

## Content Structure & MDX Pipeline

The educational content is authored as MDX files localized per language and organized into thematic worlds and levels:

- **World 1**: Introduction to AI and Promi [src/components/kids/layout/kids-header.tsx:19-24]()
- **World 2**: Clarity and Detail
- **World 3**: Context and Formatting
- **World 4**: Roleplay and Creativity
- **World 5**: Advanced Techniques and Graduation

Each level is an MDX document with a filename pattern indicating world and level numbers. The MDX content includes embedded React components for interactive games described above, enabling seamless integration of lessons and exercises.

Sources: [src/components/kids/layout/kids-header.tsx:19-24](), [src/components/kids/layout/level-content-wrapper.tsx:19-103]()

---

## Worlds, Levels & Star Collection Model

### Worlds and Levels

- The game content is split into separate **worlds**, each representing a theme or curriculum module.
- Each world contains multiple **levels**.
- Levels are identified by slugs in the format `w-l` representing world and level number [src/components/kids/layout/kids-header.tsx:24]().
- `LevelContentWrapper` manages progression through sections within each level based on completion status [src/components/kids/layout/level-content-wrapper.tsx:19-176]().

### Star Collection System

- Players earn stars by completing levels or sections correctly.
- Stars are counted globally, aggregated from all completed levels [src/components/kids/layout/kids-header.tsx:27]().
- The header component `KidsHeader` displays total stars and completed levels count, dynamically fetched from local progress stores, giving user progression feedback [src/components/kids/layout/kids-header.tsx:13-30]().

This progression incentivizes exploration and learning with visible rewards and unlocks.

Sources: [src/components/kids/layout/kids-header.tsx:13-30](), [src/components/kids/layout/level-content-wrapper.tsx:19-176]()

---

## Summary

The Kids Learning Game is a fully client-side, gamified educational environment implemented in React and Next.js featuring a gamified world-map structure, localized MDX level content, multiple interactive game modes (quiz, drag-drop, magic words, word predictors), persistent star tracking via local storage, and retro pixel-art UI components.

Sources: [src/components/kids/layout/kids-header.tsx](), [src/components/kids/layout/level-content-wrapper.tsx](), [src/components/kids/elements/prompt-vs-mistake.tsx](), [src/components/kids/elements/drag-drop-prompt.tsx](), [src/components/kids/elements/magic-words.tsx](), [src/components/kids/elements/word-predictor.tsx]()

---

# Page: Interactive Book

# Interactive Book

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mdx-components.tsx](mdx-components.tsx)
- [src/app/api/book/demo/route.ts](src/app/api/book/demo/route.ts)
- [src/app/book/[slug]/page.tsx](src/app/book/[slug]/page.tsx)
- [src/app/book/page.tsx](src/app/book/page.tsx)
- [src/components/book/elements/builder.tsx](src/components/book/elements/builder.tsx)
- [src/components/book/elements/challenge.tsx](src/components/book/elements/challenge.tsx)
- [src/components/book/elements/exercises.tsx](src/components/book/elements/exercises.tsx)
- [src/components/book/elements/index.ts](src/components/book/elements/index.ts)
- [src/components/book/elements/ui.tsx](src/components/book/elements/ui.tsx)
- [src/components/book/interactive.tsx](src/components/book/interactive.tsx)
- [src/components/book/sidebar.tsx](src/components/book/sidebar.tsx)
- [src/content/book/00a-preface.mdx](src/content/book/00a-preface.mdx)
- [src/content/book/00b-history.mdx](src/content/book/00b-history.mdx)
- [src/content/book/00c-introduction.mdx](src/content/book/00c-introduction.mdx)
- [src/content/book/01-understanding-ai-models.mdx](src/content/book/01-understanding-ai-models.mdx)
- [src/content/book/02-anatomy-of-effective-prompt.mdx](src/content/book/02-anatomy-of-effective-prompt.mdx)
- [src/content/book/03-core-prompting-principles.mdx](src/content/book/03-core-prompting-principles.mdx)
- [src/content/book/05-structured-output.mdx](src/content/book/05-structured-output.mdx)
- [src/content/book/08-iterative-refinement.mdx](src/content/book/08-iterative-refinement.mdx)
- [src/content/book/09-json-yaml-prompting.mdx](src/content/book/09-json-yaml-prompting.mdx)
- [src/content/book/15-common-pitfalls.mdx](src/content/book/15-common-pitfalls.mdx)
- [src/content/book/24-future-of-prompting.mdx](src/content/book/24-future-of-prompting.mdx)
- [src/content/book/25-agents-and-skills.mdx](src/content/book/25-agents-and-skills.mdx)
- [src/content/book/26-the-harnesses.mdx](src/content/book/26-the-harnesses.mdx)
- [src/content/book/27-tools-mcp-connectors.mdx](src/content/book/27-tools-mcp-connectors.mdx)
- [src/content/book/28-persistent-bots.mdx](src/content/book/28-persistent-bots.mdx)
- [src/content/book/ar/26-the-harnesses.mdx](src/content/book/ar/26-the-harnesses.mdx)
- [src/content/book/ar/27-tools-mcp-connectors.mdx](src/content/book/ar/27-tools-mcp-connectors.mdx)
- [src/content/book/ar/28-persistent-bots.mdx](src/content/book/ar/28-persistent-bots.mdx)
- [src/content/book/az/00a-preface.mdx](src/content/book/az/00a-preface.mdx)
- [src/content/book/az/25-agents-and-skills.mdx](src/content/book/az/25-agents-and-skills.mdx)
- [src/content/book/az/26-the-harnesses.mdx](src/content/book/az/26-the-harnesses.mdx)
- [src/content/book/az/27-tools-mcp-connectors.mdx](src/content/book/az/27-tools-mcp-connectors.mdx)
- [src/content/book/az/28-persistent-bots.mdx](src/content/book/az/28-persistent-bots.mdx)
- [src/content/book/de/00a-preface.mdx](src/content/book/de/00a-preface.mdx)
- [src/content/book/de/25-agents-and-skills.mdx](src/content/book/de/25-agents-and-skills.mdx)
- [src/content/book/de/26-the-harnesses.mdx](src/content/book/de/26-the-harnesses.mdx)
- [src/content/book/de/27-tools-mcp-connectors.mdx](src/content/book/de/27-tools-mcp-connectors.mdx)
- [src/content/book/de/28-persistent-bots.mdx](src/content/book/de/28-persistent-bots.mdx)
- [src/content/book/el/00a-preface.mdx](src/content/book/el/00a-preface.mdx)
- [src/content/book/el/26-the-harnesses.mdx](src/content/book/el/26-the-harnesses.mdx)
- [src/content/book/el/27-tools-mcp-connectors.mdx](src/content/book/el/27-tools-mcp-connectors.mdx)
- [src/content/book/el/28-persistent-bots.mdx](src/content/book/el/28-persistent-bots.mdx)
- [src/content/book/es/00a-preface.mdx](src/content/book/es/00a-preface.mdx)
- [src/content/book/es/25-agents-and-skills.mdx](src/content/book/es/25-agents-and-skills.mdx)
- [src/content/book/es/26-the-harnesses.mdx](src/content/book/es/26-the-harnesses.mdx)
- [src/content/book/es/27-tools-mcp-connectors.mdx](src/content/book/es/27-tools-mcp-connectors.mdx)
- [src/content/book/es/28-persistent-bots.mdx](src/content/book/es/28-persistent-bots.mdx)
- [src/content/book/fa/00a-preface.mdx](src/content/book/fa/00a-preface.mdx)
- [src/content/book/fa/26-the-harnesses.mdx](src/content/book/fa/26-the-harnesses.mdx)
- [src/content/book/fa/27-tools-mcp-connectors.mdx](src/content/book/fa/27-tools-mcp-connectors.mdx)
- [src/content/book/fa/28-persistent-bots.mdx](src/content/book/fa/28-persistent-bots.mdx)
- [src/content/book/fr/00a-preface.mdx](src/content/book/fr/00a-preface.mdx)
- [src/content/book/fr/26-the-harnesses.mdx](src/content/book/fr/26-the-harnesses.mdx)
- [src/content/book/fr/27-tools-mcp-connectors.mdx](src/content/book/fr/27-tools-mcp-connectors.mdx)
- [src/content/book/fr/28-persistent-bots.mdx](src/content/book/fr/28-persistent-bots.mdx)
- [src/content/book/he/00a-preface.mdx](src/content/book/he/00a-preface.mdx)
- [src/content/book/he/26-the-harnesses.mdx](src/content/book/he/26-the-harnesses.mdx)
- [src/content/book/he/27-tools-mcp-connectors.mdx](src/content/book/he/27-tools-mcp-connectors.mdx)
- [src/content/book/he/28-persistent-bots.mdx](src/content/book/he/28-persistent-bots.mdx)
- [src/content/book/it/00a-preface.mdx](src/content/book/it/00a-preface.mdx)
- [src/content/book/it/26-the-harnesses.mdx](src/content/book/it/26-the-harnesses.mdx)
- [src/content/book/it/27-tools-mcp-connectors.mdx](src/content/book/it/27-tools-mcp-connectors.mdx)
- [src/content/book/it/28-persistent-bots.mdx](src/content/book/it/28-persistent-bots.mdx)
- [src/content/book/ja/00a-preface.mdx](src/content/book/ja/00a-preface.mdx)
- [src/content/book/ja/26-the-harnesses.mdx](src/content/book/ja/26-the-harnesses.mdx)
- [src/content/book/ja/27-tools-mcp-connectors.mdx](src/content/book/ja/27-tools-mcp-connectors.mdx)
- [src/content/book/ja/28-persistent-bots.mdx](src/content/book/ja/28-persistent-bots.mdx)
- [src/content/book/ko/00a-preface.mdx](src/content/book/ko/00a-preface.mdx)
- [src/content/book/ru/00a-preface.mdx](src/content/book/ru/00a-preface.mdx)
- [src/content/book/tr/00b-history.mdx](src/content/book/tr/00b-history.mdx)
- [src/content/book/tr/00c-introduction.mdx](src/content/book/tr/00c-introduction.mdx)
- [src/content/book/zh/00a-preface.mdx](src/content/book/zh/00a-preface.mdx)
- [src/lib/book/chapters.ts](src/lib/book/chapters.ts)

</details>



The Interactive Book is a comprehensive educational feature providing a structured learning path for mastering AI prompt engineering. It organizes over two dozen chapters across several thematic parts—including advanced topics such as *The Harnesses*, *Tools & MCP Connectors*, and *Persistent Bots*—with embedded interactive demos and progress tracking through a client-side bookmark system [src/app/book/page.tsx:1-205](), [src/lib/book/chapters.ts:1-115]().

## Overview

The Interactive Book serves as an in-app learning resource accessible via the `/book` route, implemented in `src/app/book/page.tsx` [src/app/book/page.tsx:115-205](). It presents prompt engineering concepts following a progressive curriculum, allowing users to bookmark chapters, track progress, and interact with live demonstrations of techniques.

The page includes SEO-optimized metadata and JSON-LD structured data enhancing search engine visibility—details are generated in `generateMetadata` function and included in the main React component [src/app/book/page.tsx:16-113]().

Visitors see a cover image, author introduction, highlights of the book's learning goals, and the overall book structure broken into parts and chapters. The book’s textual content is organized and localized via `next-intl` [src/app/book/page.tsx:115-205]().

Sources: [src/app/book/page.tsx:16-205](), [src/lib/book/chapters.ts:1-115]()

## Book Structure and Key Chapters

The book content is structured hierarchically into "Parts" and "Chapters," which are statically defined in `src/lib/book/chapters.ts` as the arrays `parts`, containing `Part` objects with embedded `Chapter[]` arrays [src/lib/book/chapters.ts:17-98]().

### Content Organization Diagram

```mermaid
graph TB
    Book["BookHomePage<br/>src/app/book/page.tsx"]
    ChaptersLib["Chapter Registry<br/>src/lib/book/chapters.ts"]
    
    Part3["Part Advanced Strategies<br/>src/lib/book/chapters.ts:51-66"]

    Book --> ChaptersLib
    ChaptersLib --> Part3
    
    Part3 --> C25["Chapter 25 Agents & Skills<br/>src/content/book/25-agents-and-skills.mdx"]
    Part3 --> C26["Chapter 26 The Harnesses<br/>src/content/book/26-the-harnesses.mdx"]
    Part3 --> C27["Chapter 27 Tools & MCP Connectors<br/>src/content/book/27-tools-mcp-connectors.mdx"]
    Part3 --> C28["Chapter 28 Persistent Bots<br/>src/content/book/28-persistent-bots.mdx"]
```

Sources: [src/lib/book/chapters.ts:17-98](), [src/content/book/27-tools-mcp-connectors.mdx:1-145]()

### Featured Advanced Chapters
- **Tools & MCP Connectors (`27-tools-mcp-connectors.mdx`)**: Details the architectural separation between agent tools, direct APIs, product connectors, and the Model Context Protocol (MCP) standardization layer [src/content/book/27-tools-mcp-connectors.mdx:1-145]().
- **The Harnesses (`26-the-harnesses.mdx`)**: Explores runtime environments, orchestration loops, safety wrappers, and execution harnesses that wrap raw LLM prompts into production-grade agentic systems.
- **Persistent Bots (`28-persistent-bots.mdx`)**: Covers long-running assistant states, state persistence models, routines, and multi-agent coordination teams.

Sources: [src/lib/book/chapters.ts:17-98](), [src/content/book/27-tools-mcp-connectors.mdx:1-145]()

## Navigation and UI Components

- **Sidebar Navigation**: The sidebar component (`SidebarContent` in `src/components/book/sidebar.tsx`) dynamically renders the book’s parts and chapters list [src/components/book/sidebar.tsx:67-188]().
- **Search & Filter**: Search input filters book parts and chapters via caching and `useMemo` that compares query strings against chapter titles, slugs, and descriptions [src/components/book/sidebar.tsx:107-125]().
- **Bookmarking**: Bookmarks persist the last-read chapter slug in `localStorage` under the key `BOOKMARK_KEY` (`book-reading-progress`) [src/components/book/sidebar.tsx:42-65]().
- **MDX Pipeline**: Book content chapters are stored as `.mdx` files rendered using `useMDXComponents` which bundles interactive React components and UI primitives [mdx-components.tsx:8-107]().

Sources: [src/components/book/sidebar.tsx:1-190](), [src/lib/book/chapters.ts:100-115](), [mdx-components.tsx:1-108]()

## MDX Pipeline & Interactive Demos/Exercises

Chapters embed interactive demos and exercises that enrich learning with live AI prompt examples and analysis tools.

### MDX Interactive Components Data Flow

```mermaid
graph TD
    MDXFile["MDX Content File<br/>src/content/book/27-tools-mcp-connectors.mdx"] --> MDXComp["MDX Renderer<br/>mdx-components.tsx"]
    MDXComp --> UIComp["UI Elements<br/>src/components/book/elements/ui.tsx"]
    MDXComp --> DemoComp["Interactive Demos<br/>src/components/book/elements/demos.tsx"]
    MDXComp --> ExerciseComp["Exercises Component<br/>src/components/book/elements/exercises.tsx"]
    
    ExerciseComp --> APIEndpoint["Demo API Route<br/>src/app/api/book/demo/route.ts"]
    APIEndpoint --> OpenAIModel["OpenAI Chat Model<br/>GENERATIVE_MODEL"]
```

Sources: [mdx-components.tsx:3-107](), [src/components/book/elements/exercises.tsx:86-135](), [src/app/api/book/demo/route.ts:1-179]()

## Natural Language to Code Entity Mapping

To bridge conceptual reading with codebase implementation, the following diagram maps core book entities to their corresponding codebase modules and routes:

```mermaid
graph LR
    ConceptBook["Interactive Book Concept<br/>/book"] --> CodeBookPage["src/app/book/page.tsx"]
    ConceptChapters["Chapter Registry Concept"] --> CodeChapters["src/lib/book/chapters.ts"]
    ConceptExercises["Interactive Exercises"] --> CodeExercises["src/components/book/elements/exercises.tsx"]
    ConceptDemoAPI["AI Validation API"] --> CodeApiDemo["src/app/api/book/demo/route.ts"]
```

Sources: [src/app/book/page.tsx:1-205](), [src/lib/book/chapters.ts:1-115](), [src/components/book/elements/exercises.tsx:1-135](), [src/app/api/book/demo/route.ts:1-179]()

## AI Validation in Exercises

The `FillInTheBlank` interactive component supports semantic answer validation via AI through `/api/book/demo` implemented in `src/app/api/book/demo/route.ts` [src/components/book/elements/exercises.tsx:86-135](), [src/app/api/book/demo/route.ts:1-179](). Rate limiting and request tracking protect against abuse.

Sources: [src/components/book/elements/exercises.tsx:86-135](), [src/app/api/book/demo/route.ts:1-179]()

## Bookmark System and Internationalization

The Interactive Book utilizes `useBookmark()` backed by `localStorage` to save reading continuity [src/components/book/sidebar.tsx:42-63](). Localization is driven by `next-intl` across 17+ locales [src/components/book/sidebar.tsx:22-40](), [src/app/book/page.tsx:8]().

Sources: [src/components/book/sidebar.tsx:22-63](), [src/app/book/page.tsx:8]()

---

# Page: Prompt Writing Guide

# Prompt Writing Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/prompts/prompt-builder.tsx](src/components/prompts/prompt-builder.tsx)
- [src/content/book/el/02-anatomy-of-effective-prompt.mdx](src/content/book/el/02-anatomy-of-effective-prompt.mdx)
- [src/content/book/fa/02-anatomy-of-effective-prompt.mdx](src/content/book/fa/02-anatomy-of-effective-prompt.mdx)
- [src/content/book/fa/03-core-prompting-principles.mdx](src/content/book/fa/03-core-prompting-principles.mdx)
- [src/content/book/he/02-anatomy-of-effective-prompt.mdx](src/content/book/he/02-anatomy-of-effective-prompt.mdx)
- [src/content/book/he/03-core-prompting-principles.mdx](src/content/book/he/03-core-prompting-principles.mdx)

</details>



## Purpose and Scope

This guide documents the in-app systems and educational content for writing effective AI prompts on prompts.chat. It covers best practices for prompt design, the C.R.A.F.T. framework, the presentation slide deck used for education, and the implementation of prompt templates, skills, and quality assurance mechanisms. The documentation details the underlying code entities, data flows, and AI-powered features that enable high-quality prompt writing and collaboration.

The platform stores prompts in a dual-sync system between a version-controlled `prompts.csv` and supporting markdown files. Contributor attribution is automated via Git commits with `Co-authored-by` trailers generated by the `scripts/generate-contributors.sh` script. This architecture allows prompts to be programmatically validated and peer-reviewed openly on GitHub.

Sources: [prompts.csv:1-20](), [scripts/generate-contributors.sh:108-114]()

---

## Core Prompting Principles & Presentation Deck

### Overview

Effective prompt engineering within the platform is structured around core principles taught through the **Interactive Book of Prompting** and a dedicated in-app **presentation slide deck**. These resources provide foundational knowledge about the evolving importance of prompts in the agentic AI era, where agents execute instructions autonomously, emphasizing precision and clarity.

The core principles, as outlined in `src/content/book/el/03-core-prompting-principles.mdx`, `src/content/book/he/03-core-prompting-principles.mdx`, and `src/content/book/fa/03-core-prompting-principles.mdx`, include:
1. **Clarity over Cleverness**: Be explicit and avoid ambiguity.
2. **Specificity Yields Quality**: Provide detailed instructions.
3. **Context is King**: Supply all necessary background information.
4. **Guide, Don't Just Ask**: Structure the AI's reasoning process.
5. **Iterate and Refine**: Prompt engineering is an iterative process.

These principles are reinforced with `Compare` and `SpecificitySpectrum` components to illustrate the impact of good prompting practices.

Sources: [src/content/book/el/03-core-prompting-principles.mdx:1-150](), [src/content/book/he/03-core-prompting-principles.mdx:1-176](), [src/content/book/fa/03-core-prompting-principles.mdx:1-165]()

### Presentation Slide Deck Implementation

The interactive slide deck is implemented as a React component set:
- `SlideDeck` manages slide state, keyboard navigation (`ArrowRight`, `ArrowLeft`, `Space`), and transition animations.
- `SlideTitle`, `SlideContent`, and `SlideHighlight` components encapsulate semantic styling of slide text.
- Navigation UI includes next/previous buttons, progress dots, and slide count display.
- The deck supports swipe gestures and accessibility features.

This is implemented in `src/components/presentation/SlideDeck.tsx:1-133`, and rendered by `src/app/presentation/page.tsx:1-139`. The slide content narrates the prompt writing paradigm shift, the agentic need for precise instructions, the rise of Small Language Models (SLMs), structured typed prompts, and community collaboration.

Sources: [src/app/presentation/page.tsx:1-139](), [src/components/presentation/SlideDeck.tsx:1-133]()

---

## Anatomy of an Effective Prompt (C.R.A.F.T.)

The platform promotes the **C.R.A.F.T.** framework for modular prompt writing, representing:

- **Role**: Assigning a persona or expertise to the AI.
- **Context**: Background information or environment setting.
- **Task**: The primary task or instructions.
- **Constraints**: Rules and limitations on output.
- **Format**: Desired output structure (text, JSON, YAML).
- **Examples**: Few-shot input-output pairs.

This framework is detailed in `src/content/book/el/02-anatomy-of-effective-prompt.mdx`, `src/content/book/he/02-anatomy-of-effective-prompt.mdx`, and `src/content/book/fa/02-anatomy-of-effective-prompt.mdx`.

### Components and Mapping

| Component | Purpose | Code Entity / Location |
|---|---|---|
| Role | Defines AI persona or act-as context | `act` field in `prompts.csv` [prompts.csv:2-3]() |
| Context | Background context for prompt | `content` field in `Prompt`, `PromptBuilder.values.context` [src/components/prompts/prompt-builder.tsx:13-25]() |
| Task | Task instructions or prompt body | `prompt` field in CSV, `PromptBuilder.values.content` [prompts.csv:4](), [src/components/prompts/prompt-builder.tsx:13-25]() |
| Constraints | Rules and limitations on output | `PromptBuilder` internal state [src/components/prompts/prompt-builder.tsx:13-25]() |
| Format | Output type (text, structured) | `outputType` field in prompt, `PromptBuilderState.structuredFormat` [src/components/prompts/prompt-builder.tsx:13-25]() |
| Examples | Few-shot input-output pairs | Handled via prompt content structures [src/components/prompts/prompt-builder.tsx:13-25]() |

Sources: [prompts.csv:2-4](), [src/components/prompts/prompt-builder.tsx:13-25](), [src/content/book/el/02-anatomy-of-effective-prompt.mdx:1-195](), [src/content/book/he/02-anatomy-of-effective-prompt.mdx:1-228](), [src/content/book/fa/02-anatomy-of-effective-prompt.mdx:1-211]()

### Constructing Prompt Text

The UI component `PromptBuilder` aggregates these fields into a single prompt string using string concatenation for submission and display, allowing structured prompt editing in the UI.

Sources: [src/components/prompts/prompt-builder.tsx:1-50]()

### Data Flow Diagram: Natural Language C.R.A.F.T. Components to Code Entities to Storage

Title: Natural Language C.R.A.F.T. to Code Entities and Storage

```mermaid
graph TD
  subgraph NaturalLanguageSpace
    Role["Role (\"Act as Persona\")"]
    Context["Context (\"Background\")"]
    Task["Task (\"Task Instructions\")"]
    Constraints["Constraints (\"Rules/Limits\")"]
    Format["Format (\"Desired Output\")"]
    Examples["Examples (\"Few-shot samples\")"]
  end

  subgraph CodeEntitySpace
    PB_Role["PromptBuilderState.title"]
    PB_Context["PromptBuilderState.description"]
    PB_Task["PromptBuilderState.content"]
    PB_Constraints["PromptBuilderState.requiresMediaUpload"]
    PB_Format["PromptBuilderState.structuredFormat"]
    PB_Examples["PromptBuilderState.type"]
  end

  subgraph DatabaseCSV
    DB_Title["Prompt.title (CSV: act)"]
    DB_Content["Prompt.content (CSV: prompt)"]
    DB_OutputType["Prompt.outputType (CSV: type)"]
  end

  Role --> PB_Role
  Context --> PB_Context
  Task --> PB_Task
  Constraints --> PB_Constraints
  Format --> PB_Format
  Examples --> PB_Examples

  PB_Role -->|buildPrompt| DB_Title
  PB_Context -->|buildPrompt| DB_Content
  PB_Task -->|buildPrompt| DB_Content
  PB_Constraints -->|buildPrompt| DB_Content
  PB_Examples -->|buildPrompt| DB_Content
  PB_Format --> DB_OutputType

  DB_Title --> Route["src/app/prompts.csv/route.ts"]
  DB_Content --> Route
  DB_OutputType --> Route

  Route --> CSV["prompts.csv"]
```

Sources: [prompts.csv:2-4](), [src/components/prompts/prompt-builder.tsx:13-50](), [src/app/prompts.csv/route.ts:1-50]()

---

## Advanced Prompting Techniques

The platform's educational content also covers advanced techniques to enhance prompt effectiveness:

### Role-Based Prompting

Role-based prompting, as described in `src/content/book/fa/04-role-based-prompting.mdx` and `src/content/book/he/04-role-based-prompting.mdx`, involves assigning a specific persona or role to the AI. This influences the AI's vocabulary, perspective, depth of expertise, and communication style. The technical explanation highlights that LLMs adjust their statistical probabilities to match patterns seen from that type of author in their training data.

Examples of role patterns include:
- **Expert Pattern**: `You are an expert ${field} with ${years:10} years of experience in ${specialty}.`
- **Professional Pattern**: `You are a ${profession} working at ${organization}.`
- **Teacher Pattern**: `You are a ${subject} teacher who specializes in explaining complex concepts to ${audience}.`

Sources: [src/content/book/fa/04-role-based-prompting.mdx:1-148](), [src/content/book/he/04-role-based-prompting.mdx:1-148]()

### Structured Output

Structured output techniques, detailed in `src/content/book/fa/05-structured-output.mdx` and `src/content/book/he/05-structured-output.mdx`, are crucial for converting AI responses from free-form text into actionable data. This includes:
- **Lists**: Numbered or bulleted lists for step-by-step instructions or related points.
- **Tables**: Markdown tables for comparing multiple items across consistent dimensions.
- **Headings and Sections**: Using hierarchical headings (e.g., `##`, `###`) to organize longer responses.
- **Emphasis with ALL CAPS Directives**: Using keywords like `NEVER`, `ALWAYS`, `IMPORTANT`, `DO NOT`, `MUST`, `ONLY` to highlight critical constraints.
- **JSON Output**: Requesting JSON with a clear schema for machine-readable and widely supported data exchange.
- **YAML Output**: For human-readable configuration files, often used in DevOps contexts.
- **XML Output**: For specific legacy or industry-standard data formats.

Sources: [src/content/book/fa/05-structured-output.mdx:1-173](), [src/content/book/he/05-structured-output.mdx:1-194]()

### Few-Shot Learning

Few-shot learning, explained in `src/content/book/he/07-few-shot-learning.mdx` and `src/content/book/fa/07-few-shot-learning.mdx`, involves providing examples of input-output pairs to the model before asking it to perform a new task. This technique allows the AI to learn patterns for:
- **Format**: How the output should be structured.
- **Style**: Tone, length, and vocabulary.
- **Logic**: The reasoning pattern to follow.
- **Edge Cases**: How to handle specific or unusual situations.

Few-shot prompting is particularly effective for classification tasks (e.g., sentiment analysis, topic classification), conversion tasks (e.g., text rewriting, format conversion), and generation tasks (e.g., product descriptions, code documentation).

Sources: [src/content/book/he/07-few-shot-learning.mdx:1-211](), [src/content/book/fa/07-few-shot-learning.mdx:1-211]()

### Chain of Thought (CoT) Prompting

Chain of Thought (CoT) prompting, covered in `src/content/book/he/06-chain-of-thought.mdx` and `src/content/book/fa/06-chain-of-thought.mdx`, dramatically improves AI performance on complex reasoning tasks by asking the model to show its work step-by-step. Simple activation phrases like "Let's think step by step" can trigger this behavior (Zero-Shot CoT). For more consistent results, providing detailed examples of the reasoning process (Few-Shot CoT) is recommended. Structured CoT formats, such as the `BREAK` framework or a formal `Thought Template`, ensure the model follows a methodical problem-solving cycle.

Sources: [src/content/book/he/06-chain-of-thought.mdx:1-198](), [src/content/book/fa/06-chain-of-thought.mdx:1-198]()

---

## Technical Features for Prompt Quality

### 1. Interactive Learning & Testing

The platform includes interactive prompt testing within the **Interactive Book**:

- The `PromptBuilder` component enables users to run prompts instantly [src/components/prompts/prompt-builder.tsx:62-104]().
- It sends constructed prompts for evaluation to the `/api/prompt-builder/chat` REST API endpoint [src/components/prompts/prompt-builder.tsx:143-155]().
- The endpoint supports conversational prompt building, variable filling, and tool integrations.
- Underlying API uses the OpenAI client to generate completions with structured system messages guiding responses.
- Rate limiting and input guards protect against excessive usage.

Sources: [src/components/prompts/prompt-builder.tsx:62-155](), [src/app/api/book/demo/route.ts:2-50]()

#### Data Flow for Interactive Prompt Runs

Title: Interactive Prompt Execution and Evaluation Data Flow

```mermaid
graph TD
  subgraph NaturalLanguageSpace
    UserInput["UserInput (\"Fill variables & execute\")"]
  end

  subgraph CodeEntitySpace
    PromptBuilder["PromptBuilderComponent"]
    ChatAPI["src/app/api/prompt-builder/chat"]
    OpenAI["OpenAIClient"]
  end

  UserInput -->|POST request with prompt| PromptBuilder
  PromptBuilder --> ChatAPI
  ChatAPI -->|Calls chat.completions.create| OpenAI
  OpenAI --> ChatAPI
  ChatAPI --> PromptBuilder
```

Sources: [src/components/prompts/prompt-builder.tsx:62-155]()

### 2. AI-Powered Quality Checks

Prompts submitted undergo automated quality checks:

- Basic length validation (`checkLength`) ensures a minimum length threshold [src/lib/ai/quality-check.ts:26-50]().
- If too short, the prompt is flagged `TOO_SHORT` and automatically delisted.
- When `OPENAI_API_KEY` is configured, the platform sends the prompt to an OpenAI-powered semantic quality check (`checkPromptQuality`) [src/lib/ai/quality-check.ts:51-120]().
- The check uses a specialized prompt defined in `src/lib/ai/quality-check.prompt.yml` which classifies issues such as non-English content, low quality or generic prompts, and non-instructional content [src/lib/ai/quality-check.prompt.yml:1-56]().
- Prompts are delisted only if model failure confidence is high ($\ge 0.85$). API errors default to approving the prompt to avoid false negatives.

Sources: [src/lib/ai/quality-check.ts:26-164](), [src/lib/ai/quality-check.prompt.yml:1-56]()

#### AI Quality Check Pipeline Workflow

Title: AI Quality Check Pipeline Workflow

```mermaid
graph TD
  SubmitPrompt["SubmitNewPrompt"] --> CheckLength["checkLength"]
  CheckLength -->|Pass| CheckAIKey["IsApiKeySet"]
  CheckLength -->|Fail| DelistShort["DelistPromptTooShort"]

  CheckAIKey -->|No| ApproveNoAI["ApprovePromptSkipped"]
  CheckAIKey -->|Yes| GetOpenAIClient["getOpenAIClient"]

  GetOpenAIClient --> CreateCompletion["OpenAICompletionCreate"]
  CreateCompletion --> QualityCheckPrompt["quality-check.prompt.yml"]
  CreateCompletion --> OpenAIAPI["OpenAIAPIEndpoint"]

  OpenAIAPI --> ParseResponse["ParseJSONResponse"]
  ParseResponse -->|Delist=True & confidence>=0.85| DelistPrompt["DelistPromptAIFailure"]
  ParseResponse -->|Delist=False or confidence<0.85| ApprovePrompt["ApprovePromptSuccess"]
  ParseResponse -->|Error| ApproveOnError["ApprovePromptFallback"]
```

Sources: [src/lib/ai/quality-check.ts:26-164](), [src/lib/ai/quality-check.prompt.yml:1-56]()

---

## Contributor Attribution System

### Overview

The platform automates attribution of prompt contributions using the `scripts/generate-contributors.sh` script:

- Contributors are listed in the `contributor` field of `prompts.csv`.
- The script generates a commit log encoding all contributors per prompt as `Co-authored-by` trailers.
- This enables transparent GitHub contributions for community credit.

Sources: [scripts/generate-contributors.sh:38-114]()

---

## Additional Educational Resources: In-App Prompt Templates & Skills

### Prompt Templates

The platform supports in-app prompt templates as CSV entries with metadata and typed variables. These variables use a syntax `${Variable Name:Default}` that the system parses to render user input forms during execution.

Sources: [prompts.csv:2-10]()

### Multi-file Skills

For complex agent workflows, **Skills** are defined as multi-file prompt containers following strict YAML frontmatter (`name`, `description`) and file structure guidance. Skills enable AI agents to perform reusable capabilities and integrate with MCP tools.

Sources: [.windsurf/skills/widget-generator/SKILL.md:1-50]()

---

# Summary

This guide connects the educational, UI, and backend layers of prompts.chat's prompt writing experience. The core principles, slide deck presentation, modular C.R.A.F.T. framework, interactive prompt testing, AI-powered quality assurance, and contributor tracking create a comprehensive ecosystem for effective, community-driven prompt engineering.

Sources: [prompts.csv:1-20](), [scripts/generate-contributors.sh:38-114](), [src/app/presentation/page.tsx:1-139](), [src/components/presentation/SlideDeck.tsx:1-133](), [src/components/prompts/prompt-builder.tsx:13-155](), [src/app/prompts.csv/route.ts:1-50](), [src/app/api/book/demo/route.ts:2-50](), [src/lib/ai/quality-check.ts:26-164](), [src/lib/ai/quality-check.prompt.yml:1-56](), [.windsurf/skills/widget-generator/SKILL.md:1-50](), [src/content/book/el/02-anatomy-of-effective-prompt.mdx:1-195](), [src/content/book/el/03-core-prompting-principles.mdx:1-150](), [src/content/book/he/02-anatomy-of-effective-prompt.mdx:1-228](), [src/content/book/he/03-core-prompting-principles.mdx:1-176](), [src/content/book/he/04-role-based-prompting.mdx:1-148](), [src/content/book/he/05-structured-output.mdx:1-194](), [src/content/book/he/06-chain-of-thought.mdx:1-198](), [src/content/book/he/07-few-shot-learning.mdx:1-211](), [src/content/book/fa/02-anatomy-of-effective-prompt.mdx:1-211](), [src/content/book/fa/03-core-prompting-principles.mdx:1-165](), [src/content/book/fa/04-role-based-prompting.mdx:1-148](), [src/content/book/fa/05-structured-output.mdx:1-173](), [src/content/book/fa/06-chain-of-thought.mdx:1-198](), [src/content/book/fa/07-few-shot-learning.mdx:1-211]()

---

# Page: Internationalization

# Internationalization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [messages/ar.json](messages/ar.json)
- [messages/de.json](messages/de.json)
- [messages/en.json](messages/en.json)
- [messages/es.json](messages/es.json)
- [messages/fr.json](messages/fr.json)
- [messages/it.json](messages/it.json)
- [messages/ja.json](messages/ja.json)
- [messages/ko.json](messages/ko.json)
- [messages/pt.json](messages/pt.json)
- [messages/ru.json](messages/ru.json)
- [messages/tr.json](messages/tr.json)
- [messages/zh.json](messages/zh.json)

</details>



This page serves as the parent documentation for the internationalization (i18n) system in `prompts.chat`. The platform supports multiple distinct locales with a multi-level namespace organization across translation files, dynamic request resolution, and comprehensive right-to-left (RTL) script support.

---

## 8.1. Translation System

The translation infrastructure is built around structured JSON message files stored in the `messages/` directory. These files contain thousands of localized keys organized into namespaces such as `common`, `nav`, `brand`, `auth`, and `prompts`, covering core UI elements, domain-specific content, and platform branding [messages/en.json:1-36](), [messages/tr.json:1-36](), [messages/zh.json:1-36]().

At runtime, the `next-intl` library integrates these message files, enabling seamless server-side and client-side rendering of translations. Additionally, the system incorporates AI-powered auto-translation pipelines to keep auxiliary locale files in sync with English (`en.json`), facilitating support for multiple languages [messages/en.json:1-167](), [messages/ar.json:1-168]().

Title: Translation System Code Mapping
```mermaid
graph TD
    NaturalLanguageKey[""common.save", "prompts.create""]
    EnglishMessages["messages/en.json"]
    LocalizedMessages["messages/tr.json", "messages/zh.json", "messages/ja.json", "messages/ar.json", "messages/es.json", "messages/pt.json", "messages/fr.json", "messages/it.json", "messages/de.json", "messages/ko.json", "messages/ru.json"]
    NextIntl["next-intl runtime"]
    Rendering["Server and Client UI Rendering"]

    NaturalLanguageKey --> EnglishMessages
    NaturalLanguageKey --> LocalizedMessages
    EnglishMessages --> NextIntl
    LocalizedMessages --> NextIntl
    NextIntl --> Rendering
```

*Figure: From natural language keys defined in JSON translation files through `next-intl` to rendered user interface translations.*

Sources: [messages/en.json:1-167](), [messages/tr.json:1-163](), [messages/zh.json:1-167](), [messages/ja.json:1-167](), [messages/ar.json:1-168](), [messages/es.json:1-159](), [messages/pt.json:1-162](), [messages/fr.json:1-157](), [messages/it.json:1-162](), [messages/de.json:1-159](), [messages/ko.json:1-194](), [messages/ru.json:1-162]()

For full details on messages file structure, next-intl integration, and AI auto-translation workflows, see [Translation System](#8.1).

---

## 8.2. Locale Management

Locale management in `prompts.chat` handles user locale detection, preference persistence, and fallback resolution. It supports multiple languages including English (`en`), Turkish (`tr`), Chinese (`zh`), Japanese (`ja`), Arabic (`ar`), Spanish (`es`), Portuguese (`pt`), French (`fr`), Italian (`it`), German (`de`), Korean (`ko`), and Russian (`ru`) [messages/en.json:1-10](), [messages/ja.json:1-10](), [messages/ar.json:1-10]().

The detection cascade is managed by core request utilities which examine incoming cookies and headers to determine the correct locale context.

Title: Locale Management Request Cascade
```mermaid
graph TD
    UserPreference["User Language Preference"]
    NEXT_LOCALE["Cookie NEXT_LOCALE"]
    AcceptLanguage["HTTP Header Accept-Language"]
    LocaleDetector["i18n/request.ts locale detector"]
    LocaleFallback["Default en locale"]

    UserPreference -->|cookie| NEXT_LOCALE
    NEXT_LOCALE -->|header fallback| AcceptLanguage
    AcceptLanguage --> LocaleDetector
    LocaleDetector --> LocaleFallback
```

*Figure: User locale resolution from cookie and HTTP headers delegated to core locale detection code.*

Sources: [messages/en.json:1-10](), [messages/ar.json:1-10](), [messages/ja.json:1-10]()

For detailed documentation on supported locales, cookie handling, and the detection cascade, see [Locale Management](#8.2).

---

## 8.3. RTL Language Support

`prompts.chat` supports right-to-left (RTL) languages such as Arabic (`ar`), Hebrew (`he`), and Persian/Farsi (`fa`) by adapting layout and typography via dedicated detection functions and direction attribute management [messages/ar.json:1-35]().

Key components include checking locale strings with helper functions, dynamically altering document direction, and applying appropriate typography styles.

For implementation specifics on RTL locale detection, font loading, and direction attribute management, see [RTL Language Support](#8.3).

Sources: [messages/ar.json:1-35]()

---

# Summary Diagram: Internationalization System Integration Overview

Title: Internationalization Architecture Overview
```mermaid
graph LR
    subgraph Translation_System
        EN["messages/en.json"]
        TR["messages/tr.json"]
        ZH["messages/zh.json"]
        NextIntl["next-intl runtime"]
        EN --> NextIntl
        TR --> NextIntl
        ZH --> NextIntl
    end

    subgraph Locale_Management
        NEXT_LOCALE["NEXT_LOCALE cookie"]
        AcceptLang["Accept-Language header"]
        LocaleDetector["i18n/request.ts locale detector"]
        NEXT_LOCALE --> LocaleDetector
        AcceptLang --> LocaleDetector
    end

    subgraph RTL_Support
        RTLCheck["isRtlLocale function"]
        DirAttr["html dir attribute switching"]
        Fonts["RTL Font Loading"]
        RTLCheck --> DirAttr
        DirAttr --> Fonts
    end

    LocaleDetector --> NextIntl
    LocaleDetector -.-> RTLCheck
```

*Figure: Comprehensive flow from user locale detection to translation runtime and RTL layout support, showing key code components and data flows.*

Sources: [messages/en.json:1-167](), [messages/tr.json:1-163](), [messages/zh.json:1-167](), [messages/ar.json:1-35]()

---

For deep technical insights on each part of the i18n system, consult the respective child pages:  
- [Translation System](#8.1)  
- [Locale Management](#8.2)  
- [RTL Language Support](#8.3)

---

# Sources

- [messages/en.json:1-167]()
- [messages/tr.json:1-163]()
- [messages/zh.json:1-167]()
- [messages/ja.json:1-167]()
- [messages/ar.json:1-168]()
- [messages/es.json:1-159]()
- [messages/pt.json:1-162]()
- [messages/fr.json:1-157]()
- [messages/it.json:1-162]()
- [messages/de.json:1-159]()
- [messages/ko.json:1-194]()
- [messages/ru.json:1-162]()

---

# Page: Translation System

# Translation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [messages/ar.json](messages/ar.json)
- [messages/de.json](messages/de.json)
- [messages/en.json](messages/en.json)
- [messages/es.json](messages/es.json)
- [messages/fr.json](messages/fr.json)
- [messages/it.json](messages/it.json)
- [messages/ja.json](messages/ja.json)
- [messages/ko.json](messages/ko.json)
- [messages/nl.json](messages/nl.json)
- [messages/pt.json](messages/pt.json)
- [messages/ru.json](messages/ru.json)
- [messages/tr.json](messages/tr.json)
- [messages/zh.json](messages/zh.json)

</details>



The translation system in prompts.chat provides a complete internationalization (i18n) framework designed to support multi-language user interfaces, localized metadata, and AI-powered translations across the platform. It manages thousands of translation keys structured within locale-specific JSON files under the `messages/` directory, integrates with the `next-intl` library for React rendering, and powers dynamic content translation using prompt templates.

Sources: [messages/en.json:1-36](), [messages/tr.json:1-36]()

---

## File Structure and JSON Message Bundles

Translation content is organized by locale in the `messages/` directory, with `messages/en.json` acting as the structural source of truth. Each locale file mirrors this structure to maintain key parity across thousands of nested translation keys spanning various UI namespaces.

```
messages/
├── en.json        # English (Base schema source of truth)
├── tr.json        # Turkish
├── zh.json        # Chinese (Simplified)
├── ja.json        # Japanese
├── ar.json        # Arabic (RTL)
├── es.json        # Spanish
├── pt.json        # Portuguese
├── fr.json        # French
├── it.json        # Italian
├── de.json        # German
├── ko.json        # Korean
├── ru.json        # Russian
├── nl.json        # Dutch
└── he.json        # Hebrew (RTL)
```

Within these JSON bundles, keys are nested under high-level namespaces. Rich text formatting and ICU message format string interpolation are supported natively:

```json
"moreLines": "+{count} more lines",
"licenseText": "The {name} brand assets are provided under <link>CC0 1.0 Universal</link>."
```

Sources: [messages/en.json:1-36](), [messages/tr.json:1-36](), [messages/zh.json:1-36]()

---

## Namespace Architecture and Code Mapping

Namespaces isolate translation scopes to optimize payload sizes and map directly to specific application component modules.

### Namespace Definitions

| Namespace | Code Role | Example Keys |
|-----------|-----------|--------------|
| `common` | Shared UI buttons, states, and general utilities | `common.loading`, `common.save`, `common.variables` [messages/en.json:2-36]() |
| `nav` | Application header, navigation, and sidebar routing | `nav.prompts`, `nav.skills`, `nav.admin` [messages/en.json:37-69]() |
| `auth` | Authentication forms, hints, and feedback | `auth.login`, `auth.githubAttributionHint` [messages/en.json:96-118]() |
| `prompts` | Prompt creation, metadata labels, and delisting reasons | `prompts.createSkill`, `prompts.delistReasonTooShort` [messages/en.json:119-195]() |
| `brand` | Brand asset guidelines, color codes, and copy triggers | `brand.title`, `brand.copyLogoSvg` [messages/en.json:70-95]() |

Sources: [messages/en.json:2-118](), [messages/tr.json:2-118]()

### Namespace to Code Entity Bridge Diagram

Title: "Namespace to Code Entity Mapping"

```mermaid
graph TB
    subgraph "Natural_Language_Space"
        JSON_EN["messages/en.json"]
        JSON_TR["messages/tr.json"]
        JSON_ZH["messages/zh.json"]
    end

    subgraph "Code_Entity_Space"
        NextIntlProvider["NextIntlClientProvider"]
        UseTrans["useTranslations Hook"]
        RootLayout["RootLayout Component"]
        PromptEditor["PromptEditor Component"]
    end

    JSON_EN -->|"Dictionary_Load"| NextIntlProvider
    JSON_TR -->|"Dictionary_Load"| NextIntlProvider
    JSON_ZH -->|"Dictionary_Load"| NextIntlProvider
    NextIntlProvider --> UseTrans
    UseTrans -->|"t_nav_prompts"| RootLayout
    UseTrans -->|"t_prompts_createSkill"| PromptEditor
```

Sources: [messages/en.json:2-118](), [messages/tr.json:2-118](), [messages/zh.json:2-118]()

---

## Prompt Metadata, Quality Control, and Delisting Messages

The `prompts` namespace handles advanced domain concepts such as Agent Skills, coding Tastes, and automated quality control messages [messages/en.json:119-200](). When automated background verification pipelines flag content, localized messages explain the precise rejection reason to the author:

- `delistReasonTooShort`: Content length fails minimum structural requirements [messages/zh.json:188]().
- `delistReasonNotEnglish`: Non-English content detected by validation checks [messages/zh.json:189]().
- `delistReasonLowQuality`: Low quality score returned from heuristic or AI evaluation [messages/zh.json:190]().
- `delistReasonNotInstruction`: Content is malformed and does not resemble an LLM instruction [messages/zh.json:191]().

Sources: [messages/en.json:119-200](), [messages/zh.json:185-194]()

---

## Integration with `next-intl`

The platform leverages `next-intl` to handle locale resolution and runtime message rendering:
- **Cookie & Header Cascade**: Automatically detects preferred user locales via `NEXT_LOCALE` cookies and standard browser `accept-language` headers.
- **Server & Client Synchronization**: Locale translation bundles are loaded per-request within server components and safely propagated down via React context to client-side hooks like `useTranslations`.
- **Dynamic Interpolation**: Resolves runtime placeholders such as `{count}` values and rich markup formatting components (`<link>`).

Sources: [messages/en.json:2-95]()

---

## AI-Powered Automatic Translation & Prompt Workflows

User-generated prompt content (markdown instructions, descriptions, skills) utilizes AI translation pipelines alongside static UI strings. The system leverages prompt configuration files and quality validation engines to process translation and automated review tasks.

### AI Translation Data Flow Diagram

Title: "AI Translation Data Flow and Code Entities"

```mermaid
graph TB
    subgraph "Natural_Language_Space"
        UserMarkdownPrompt["User Markdown Prompt Text"]
        TargetLocaleRequest["Target Locale Selection"]
    end

    subgraph "Code_Entity_Space"
        TranslateButton["TranslateButton Component"]
        ApiTranslate["POST /api/translate Route"]
        TranslatePromptTemplate["src/lib/ai/translate.prompt.yml"]
        OpenAiService["OpenAI API Service"]
        PrismaPromptModel["Prisma Prompt Model DB"]
    end

    UserMarkdownPrompt --> PrismaPromptModel
    TargetLocaleRequest --> TranslateButton
    TranslateButton -->|"fetch()"| ApiTranslate
    ApiTranslate -->|"loadConfig()"| TranslatePromptTemplate
    ApiTranslate -->|"readContent()"| PrismaPromptModel
    ApiTranslate -->|"executeLLM()"| OpenAiService
    OpenAiService -->|"translatedText"| ApiTranslate
    ApiTranslate -->|"JSON Response"| TranslateButton
```

Sources: [messages/en.json:119-141]()

---

## Right-to-Left (RTL) Language Support

For right-to-left languages like Arabic (`ar.json`), Hebrew (`he.json`), and Persian, the system dynamically alters document structure:
- Identifies RTL locales via structural helper functions.
- Dynamically injects the `<html dir="rtl">` attribute during root layout rendering.
- Applies RTL-specific font overrides, alignment rules, and directional padding.

Sources: [messages/ar.json:1-36]()

---

## Summary Architecture Diagram

Title: "Translation System Architecture Overview"

```mermaid
graph TB
    subgraph "Natural_Language_Space"
        StaticJSON["messages/*.json Files"]
        UserPrompts["User Markdown Prompts"]
    end

    subgraph "Code_Entity_Space"
        NextIntlIntegration["next-intl Integration"]
        ApiRouteTranslate["POST /api/translate"]
        QualityEngine["src/lib/ai/quality-check.ts"]
        PrismaDatabase["Prisma Database"]
    end

    StaticJSON --> NextIntlIntegration
    NextIntlIntegration --> ReactComponents["React Server and Client Components"]
    UserPrompts --> PrismaDatabase
    PrismaDatabase --> ApiRouteTranslate
    ApiRouteTranslate --> QualityEngine
    QualityEngine --> ApiRouteTranslate
    ApiRouteTranslate --> ReactComponents
```

Sources: [messages/en.json:1-160]()

---

# Page: Locale Management

# Locale Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [messages/az.json](messages/az.json)
- [messages/fa.json](messages/fa.json)
- [prompts.config.ts](prompts.config.ts)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



This document covers the locale detection, storage, and switching mechanisms in `prompts.chat`. For details on translation file format and AI-powered translation features, see [Translation System](8.1). For RTL language support specifics, see [RTL Language Support](8.3).

The locale management system handles interface language selection and persistence across supported locales, including special handling for right-to-left (RTL) scripts.

---

## Supported Locales

Supported locales are centrally defined, used to populate language selectors and to validate active locale settings against configuration definitions.

| Language | Code | Script Direction |
| :------- | :--- | :--------------- |
| English | `en` | LTR |
| Turkish | `tr` | LTR |
| Spanish | `es` | LTR |
| Chinese | `zh` | LTR |
| Japanese | `ja` | LTR |
| Arabic | `ar` | RTL |
| Portuguese | `pt` | LTR |
| French | `fr` | LTR |
| Italian | `it` | LTR |
| German | `de` | LTR |
| Dutch | `nl` | LTR |
| Korean | `ko` | LTR |
| Russian | `ru` | LTR |
| Hebrew | `he` | RTL |
| Greek | `el` | LTR |
| Persian | `fa` | RTL |
| Azerbaijani | `az` | LTR |

### Locale List Source of Truth

- The array `supportedLocales` in `[src/lib/i18n/config.ts:4-5]()` enumerates these codes.
- The same list is synchronized with the `i18n.locales` entry in `[prompts.config.ts:44-47]()`.
- The `defaultLocale` is set as `"en"` in `[src/lib/i18n/config.ts:6-6]()`.

Sources: `[src/components/layout/header.tsx:86-104]`, `[prompts.config.ts:44-47]()`, `[src/lib/i18n/config.ts:4-9]()`

---

## Locale Detection Pipeline

Locale detection uses a cascading priority sequence to resolve the best locale for client requests.

### Detection Cascade

1.  **Cookie check**: Reads the locale preference cookie named `LOCALE_COOKIE` (`"NEXT_LOCALE"`) via `[src/i18n/request.ts:44-44]()`.
2.  **Accept-Language header parse**: If no valid cookie is found, `[src/i18n/request.ts:48-57]()` parses the `accept-language` header for a supported locale using `detectLocaleFromHeader`.
3.  **Fallback**: The `defaultLocale` (`"en"`) is used if no matches are found `[src/i18n/request.ts:55-55]()`.

This logic is handled in the server request configuration function `getRequestConfig` provided by `next-intl` integration `[src/i18n/request.ts:39-87]()`.

### Diagram: Locale Detection & Persistence Flow (Natural Language Space to Code Entity Space)

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        BrowserSetting["UserBrowserLanguagePreferences"]
        UserSelection["UserHeaderLanguageClick"]
    end

    subgraph "CodeEntitySpace"
        detectLocaleFromHeader["detectLocaleFromHeader (src/i18n/request.ts)"]
        getRequestConfig["getRequestConfig (src/i18n/request.ts)"]
        LocaleDetector["LocaleDetector (src/components/providers/locale-detector.tsx)"]
        CookieStore["LOCALE_COOKIE (src/lib/i18n/config.ts)"]
    end

    BrowserSetting --> detectLocaleFromHeader
    UserSelection --> LocaleDetector
    detectLocaleFromHeader --> getRequestConfig
    LocaleDetector --> CookieStore
    CookieStore --> getRequestConfig
```

Sources: `[src/i18n/request.ts:10-55]()`, `[src/i18n/request.ts:39-87]()`, `[src/lib/i18n/config.ts:1-7]()`, `[prompts.config.ts:44-47]()`

### Detection Function Details

-   The `detectLocaleFromHeader` function parses the `Accept-Language` header, sorts language codes by quality value (`q` parameter), and finds the first match from supported locales `[src/i18n/request.ts:10-37]()`.
-   It compares both full locale codes (like `en-US`) and their base language (`en`) `[src/i18n/request.ts:24-33]()`.
-   If no supported locale is found, `null` is returned `[src/i18n/request.ts:36-36]()`.

Sources: `[src/i18n/request.ts:10-37]()`

---

## Locale Storage and Persistence

User locale preferences are persisted using a cookie named `LOCALE_COOKIE` (`"NEXT_LOCALE"`) `[src/lib/i18n/config.ts:1-2]()`. This ensures the chosen language persists across sessions and requests.

### Client-Side Locale Saving

-   On the client side, the `LocaleDetector` React component saves the auto-detected locale to a cookie on first visit `[src/components/providers/locale-detector.tsx:7-10]()`.
-   It checks if `LOCALE_COOKIE` already exists and sets it if absent `[src/components/providers/locale-detector.tsx:15-23]()`.
-   The cookie `max-age` is set for 1 year (`60 * 60 * 24 * 365`), making the preference long-lasting `[src/components/providers/locale-detector.tsx:22-22]()`.

Sources: `[src/components/providers/locale-detector.tsx:1-27]()`, `[src/lib/i18n/config.ts:1-2]()`

### Client Locale Switching in Header

-   The `Header` component renders a languages array containing all supported locales and their display names `[src/components/layout/header.tsx:86-104]()`.
-   Locale switches trigger the `setLocale` client utility function `[src/components/layout/header.tsx:79-79]()`.
-   `setLocale` updates the `NEXT_LOCALE` cookie and reloads the app with the new locale.

Sources: `[src/components/layout/header.tsx:79-104]`, `[src/i18n/request.ts:40-45]()`

---

## RTL Locale Identification

Certain languages require right-to-left (RTL) layout rendering. These are handled explicitly during locale determination and UI adjustments.

### RTL Locales List

The RTL locales are:

-   Arabic (`ar`)
-   Hebrew (`he`)
-   Persian (`fa`)

This list is declared in `[src/lib/i18n/config.ts:8-9]()`:

```ts
export const rtlLocales = ["ar", "he", "fa"];
```

### RTL Helper Function

The function `isRtlLocale(locale: string): boolean` checks if a locale is RTL by checking membership in `rtlLocales` `[src/lib/i18n/config.ts:11-14]()`. This is typically used to set the page `dir` attribute dynamically.

Sources: `[src/lib/i18n/config.ts:8-14]()`

---

## Configuration and Environment Overrides

### Static Configuration in `prompts.config.ts`

Locales are specified here under the `i18n` property `[prompts.config.ts:43-47]()`. This entry drives both the supported locale list and the fallback locale in the system.

Sources: `[prompts.config.ts:43-47]()`

### Environment Variable Overrides

For deployment flexibility, environment variables prefixed with `PCHAT_` can override the i18n configuration via `[src/lib/config/index.ts:143-148]()`:

-   `PCHAT_LOCALES` — comma-separated list of locale codes; overrides static list `[src/lib/config/index.ts:143-146]()`
-   `PCHAT_DEFAULT_LOCALE` — single locale code; overrides default fallback `[src/lib/config/index.ts:147-147]()`

### Override Processing Pipeline

1.  Application loads `prompts.config.ts` dynamically inside `getConfig` `[src/lib/config/index.ts:175-176]()`.
2.  `applyEnvOverrides(config)` function parses environment variables and applies overrides if present `[src/lib/config/index.ts:99-166]()`.
3.  The resulting config is cached and consumed by the app `[src/lib/config/index.ts:168-170]()`.

### Diagram: Natural Language Space to Code Entity Space for I18n Configuration

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        UserConfig["prompts.config.ts i18n block"]
        DockerEnv["EnvironmentVariables PCHAT_LOCALES / PCHAT_DEFAULT_LOCALE"]
    end

    subgraph "CodeEntitySpace"
        ApplyEnv["applyEnvOverrides (src/lib/config/index.ts)"]
        GetConfig["getConfig (src/lib/config/index.ts)"]
        I18nConfig["PromptsConfig.i18n"]
    end

    UserConfig --> GetConfig
    DockerEnv -->|process.env| ApplyEnv
    ApplyEnv --> GetConfig
    GetConfig -->|populates| I18nConfig
```

Sources: `[src/lib/config/index.ts:99-176]`, `[prompts.config.ts:43-47]()`

---

# Summary

The Locale Management system in `prompts.chat` integrates static configuration, environment overrides, cookie-based persistence (`NEXT_LOCALE`), browser header heuristics, and explicit RTL layout support to provide a seamless multilingual user experience.

-   Supported locales align across UI components, config files, and backend request parsers.
-   A flexible cascade prioritizes saved user choices before browser headers and defaults.
-   Client components and header UI enable runtime locale switching.
-   RTL locales are clearly identified for correct rendering direction.
-   Environment variables allow seamless configuration overrides in containerized deployments.

Sources: `[src/i18n/request.ts:1-87]`, `[src/lib/i18n/config.ts:1-24]`, `[src/lib/config/index.ts:99-176]`, `[prompts.config.ts:43-47]()`

---

# Page: RTL Language Support

# RTL Language Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [messages/el.json](messages/el.json)
- [messages/he.json](messages/he.json)
- [prompts.config.ts](prompts.config.ts)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



This page covers the right-to-left (RTL) language support subsystem: how RTL locales are declared, how the application detects them, and how individual components adapt their layouts. For the broader locale selection UI and cookie persistence, see **8.2 Locale Management**. For the translation key structure across all supported locales, see **8.1 Translation System**.

---

## Purpose & Scope

The purpose of this subsystem is to provide full layout reversal, font optimization, and localized navigation for RTL scripts (Arabic, Hebrew, and Persian) across the application. This page details the core detection function `isRtlLocale`, font variable usage in the root layout (`src/app/layout.tsx`), and component-level layout shifts such as in the masonry grid component (`src/components/ui/masonry.tsx`).

By handling RTL condition detection centrally and applying the `dir` attribute on the root element, the system leverages native CSS and browser RTL support with selective style and font adjustments for improved usability and readability.

Sources: [src/app/layout.tsx:157-182](), [src/components/ui/masonry.tsx:31-42]()

---

## Supported RTL Locales

The application explicitly supports the following RTL locales, fully integrated in the translation and UI logic:

| Locale Code | Language          | Source Translation File             |
|-------------|-------------------|-----------------------------------|
| `ar`        | Arabic (العربية)   | `messages/ar.json`                 |
| `he`        | Hebrew (עברית)    | `messages/he.json`          |
| `fa`        | Persian (فارسی)    | `messages/fa.json`                 |

The inclusion of these locales in the RTL list ensures that these language selections trigger layout direction changes and appropriate font stacks.

Locales like Azerbaijani (`az`) and Greek (`el`) are supported as translations but are not defined as RTL and thus use standard left-to-right layout [messages/el.json:1-36]().

The definitive list of supported locales and the subset defined as RTL is managed in [src/lib/i18n/config.ts:8-14]().

Sources: [src/lib/i18n/config.ts:8-14](), [messages/he.json:1-35](), [src/components/layout/header.tsx:86-104]()

---

## RTL Detection & Root Layout Integration

The function `isRtlLocale` (defined in [src/lib/i18n/config.ts:12-14]()) provides a deterministic check to verify if a locale requires RTL layout support based on the `rtlLocales` array (`["ar", "he", "fa"]`).

### Implementation & Data Flow

When a request is processed, `getLocale()` retrieves the current locale, which is then evaluated by `isRtlLocale(locale)` [src/app/layout.tsx:157-160](). The resulting boolean (`isRtl`) drives two major UI adaptations at the root level (`src/app/layout.tsx`):
1. Setting the `dir` attribute on the `<html>` element to `"rtl"` or `"ltr"` [src/app/layout.tsx:179]().
2. Appending the Arabic font variable (`notoSansArabic.variable`) and `font-arabic` class to the `<body>` element [src/app/layout.tsx:174-176]().

### Diagram: Natural Language to Code Entity Space (Root Layout RTL Flow)

```mermaid
flowchart TD
  UserSelection[""User Locale Selection (Arabic, Hebrew, Persian)""] --> GetLocale[""getLocale() in src/app/layout.tsx""]
  GetLocale --> IsRtlCheck[""isRtlLocale(locale) in src/lib/i18n/config.ts""]
  IsRtlCheck --> RootHtml[""html tag dir attribute (<html dir='rtl'>) in src/app/layout.tsx""]
  IsRtlCheck --> BodyFont[""body className font-arabic switch (<body class='font-arabic'>) in src/app/layout.tsx""]
```

Sources: [src/lib/i18n/config.ts:8-14](), [src/app/layout.tsx:157-182]()

---

# Font Switching for RTL Languages

Arabic, Hebrew, and Persian scripts require specialized font rendering to ensure adequate glyph coverage and visual clarity.

### Font Usage

In the root layout component (`src/app/layout.tsx`), the code imports and applies `Noto_Sans_Arabic` from Google Fonts as a CSS variable for RTL locales [src/app/layout.tsx:2-27]():

```tsx
const notoSansArabic = Noto_Sans_Arabic({
  subsets: ["arabic"],
  variable: "--font-arabic",
  weight: ["400", "500", "600", "700"],
});
```

When `isRtl` is true, `font-arabic` is included in the body class names, ensuring proper rendering across all UI elements [src/app/layout.tsx:174-176]().

| Condition       | Applied Font Stack          | Context                    |
|-----------------|-----------------------------|----------------------------|
| RTL Locale      | `Noto Sans Arabic` (`--font-arabic`) | For `ar`, `he`, `fa` locales |
| Non-RTL Locale  | `Inter` / Default sans-serif | All other locales          |

Sources: [src/app/layout.tsx:23-27](), [src/app/layout.tsx:174-176]()

---

# Component-Level RTL Handling & Masonry Grid

While most layout flipping is controlled by the root-level `dir` attribute and CSS inheritance, specific complex components like the masonry grid require explicit programmatic RTL awareness.

### Masonry Layout Grid (`src/components/ui/masonry.tsx`)

The masonry grid component manages prompt item positioning with manual checks against the `document.documentElement.dir` attribute to correctly position elements in RTL contexts [src/components/ui/masonry.tsx:31-42]().

Key mechanisms implemented:
- Subscribes to layout direction via a `MutationObserver` watching `dir` attribute changes on `document.documentElement` [src/components/ui/masonry.tsx:38-41]().
- Reverses horizontal placement transforms using negative offsets (`isRTL ? -position.x : position.x`) [src/components/ui/masonry.tsx:171-173]().
- Dynamically assigns `right: 0` instead of `left: 0` for grid items when `isRTL` is true [src/components/ui/masonry.tsx:175]().

### Diagram: Natural Language to Code Entity Space (Masonry RTL Adaptation)

```mermaid
flowchart TD
  DomDir[""document.documentElement.dir ('rtl')""] --> MutationObs[""MutationObserver in src/components/ui/masonry.tsx""]
  MutationObs --> StateSetter[""setIsRTL(boolean) state hook in src/components/ui/masonry.tsx""]
  StateSetter --> CalcPos[""calculatePositions() item placement loop in src/components/ui/masonry.tsx""]
  CalcPos --> StyleApply[""CSS transform translate3d(isRTL ? -x : x) & right: 0 style assignment in src/components/ui/masonry.tsx""]
```

Sources: [src/components/ui/masonry.tsx:31-42](), [src/components/ui/masonry.tsx:171-176]()

---

# Summary

The RTL support in prompts.chat provides robust linguistic and UI adjustments for Arabic, Hebrew, and Persian locales by:
- Evaluating locales via centralized checks (`isRtlLocale`) [src/lib/i18n/config.ts:12-14]().
- Setting the root document `dir` attribute dynamically to flip layout direction [src/app/layout.tsx:179]().
- Applying specialized fonts (`Noto_Sans_Arabic`) for RTL scripts at the root layout level [src/app/layout.tsx:23-27]().
- Adapting UI components like the masonry grid (`src/components/ui/masonry.tsx`) for precise directional item flow [src/components/ui/masonry.tsx:31-176]().

Sources: [src/lib/i18n/config.ts:8-14](), [src/app/layout.tsx:23-182](), [src/components/ui/masonry.tsx:31-176]()

---

# Page: UI & Theming

# UI & Theming

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/globals.css](src/app/globals.css)
- [src/components/kids/elements/pixel-art.tsx](src/components/kids/elements/pixel-art.tsx)
- [src/components/kids/elements/progress-map.tsx](src/components/kids/elements/progress-map.tsx)
- [src/components/kids/elements/story-scene.tsx](src/components/kids/elements/story-scene.tsx)
- [src/components/kids/layout/settings-modal.tsx](src/components/kids/layout/settings-modal.tsx)
- [src/components/layout/animated-text.tsx](src/components/layout/animated-text.tsx)
- [src/components/prompts/hero-categories.tsx](src/components/prompts/hero-categories.tsx)

</details>



This page serves as the parent overview for the UI and theming systems in `prompts.chat`. The visual architecture combines modern CSS custom properties, OKLCH color spaces, Radix UI primitives, shadcn/ui patterns, and a specialized pixel-art aesthetic particularly featured in educational components.

- [Theming System](#9.1) — Document theme configuration with radius, variant, density, colors, hexToOklch color conversion, globals.css and CSS custom properties
- [Component Patterns](#9.2) — Explain UI component library using Radix UI, shadcn/ui patterns, code/tree views, masonry layout, and common component structures
- [Animation System](#9.3) — Document animation components like AnimatedText, AnimatedDate, transitions, brand assets and motion patterns

For configuration settings, see [Theme Configuration](#12.3). For layout direction rules, see [RTL Language Support](#8.3).

---

## Theming System

The theming architecture relies on runtime configuration that converts standard hex color definitions into OKLCH CSS custom properties. This supports dynamic visual variants (`flat`, `default`, `brutal`) and adjustable spacing densities (`compact`, etc.).

The configuration pipeline interprets values from `prompts.config.ts` and injects them through server-side helpers into the root-level styling variables defined in `src/app/globals.css`. These CSS variables govern colors, typography, radii, shadows, and other visual tokens used globally. The OKLCH color space ensures better perceptual color manipulation for light/dark mode variants.

### Diagram: Theming System Architecture
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        ConfigDesc["Theme Configuration in prompts.config.ts"]
        ColorConv["hexToOklch Color Conversion"]
        ThemeVar["Theme Variant & Density Selection"]
    end

    subgraph "CodeEntitySpace"
        ConfigTS["prompts.config.ts"]
        LayoutTS["src/app/layout.tsx (theme processing)"]
        GlobalsCSS["src/app/globals.css (CSS variables and styles)"]
        ThemeFlat[".theme-flat (flat visual variant)"]
        ThemeBrutal[".theme-brutal (brutal visual variant)"]
    end

    ConfigDesc --> ConfigTS
    ColorConv --> LayoutTS
    ThemeVar --> GlobalsCSS
    
    ConfigTS --> LayoutTS
    LayoutTS --> GlobalsCSS
    GlobalsCSS --> ThemeFlat
    GlobalsCSS --> ThemeBrutal
```
Sources: [src/app/globals.css:1-225]()

The global CSS defines root variables such as `--background`, `--foreground`, `--primary`, `--radius`, and others, adjusted for light and dark modes via the `.dark` CSS class. Shadow depths and border styles vary between theme variants, providing visual flavor and affordance consistency throughout the UI.

For full technical details and usage instructions, see [Theming System](#9.1).

Sources: [src/app/globals.css:1-225]()

---

## Component Patterns

The UI component library in `prompts.chat` is primarily built on Radix UI primitives combined with shadcn/ui conventions to provide accessible, reusable, and highly customizable UI elements. This system supports complex use cases including code views, tree controls, and masonry layouts.

The application’s user interface is formed by standard UI components such as the `HeroCategories` search input component which offers a responsive search bar with icon adornment and video showcase, as implemented in `src/components/prompts/hero-categories.tsx`.

Distinctively, the Kids educational modules feature a dedicated pixel-art subsystem implemented with SVG components. These components provide a nostalgic pixel-art visual style consistent with the educational game's branding and theme. They render pixelated assets such as trees, castles, clouds, and characters like the `PixelRobot`. Polygon clip-path CSS shapes are used extensively for custom button and modal styling, reinforcing the pixel-art aesthetic. One example is the complex settings modal interface located in `src/components/kids/layout/settings-modal.tsx`.

### Diagram: Component Architecture and Mapping
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        StandardUI["Standard Application UI Components"]
        KidsUI["Kids Pixel-Art Themed Components"]
    end

    subgraph "CodeEntitySpace"
        HeroComp["HeroCategories<br/>src/components/prompts/hero-categories.tsx"]
        SettingsModalComp["SettingsModal<br/>src/components/kids/layout/settings-modal.tsx"]
        ProgressMapComp["ProgressMap<br/>src/components/kids/elements/progress-map.tsx"]
        PixelArtComp["PixelRobot & PixelArt SVGs<br/>src/components/kids/elements/pixel-art.tsx"]
    end

    StandardUI --> HeroComp
    KidsUI --> SettingsModalComp
    KidsUI --> ProgressMapComp
    ProgressMapComp --> PixelArtComp
```
Sources: [src/components/prompts/hero-categories.tsx:9-52](), [src/components/kids/layout/settings-modal.tsx:54-114](), [src/components/kids/elements/progress-map.tsx:12-27](), [src/components/kids/elements/pixel-art.tsx:158-188]()

For an in-depth explanation of component structures, patterns, accessibility strategies, and utility components, see [Component Patterns](#9.2).

Sources: [src/components/prompts/hero-categories.tsx:9-52](), [src/components/kids/layout/settings-modal.tsx:54-114](), [src/components/kids/elements/progress-map.tsx:12-27](), [src/components/kids/elements/pixel-art.tsx:158-188]()

---

## Animation System

Animations in `prompts.chat` are primarily realized through CSS keyframes and utility classes augmented by React components that encapsulate common motion patterns.

The global CSS (`src/app/globals.css`) defines keyframe animations like `gradient-flow` which creates a continuous gradient background movement effect used on text elements. This underpins components such as the `AnimatedText` component, which renders multi-colored gradient text with an animated flow, improving visual engagement on dynamic UI parts.

Modal and dialog transitions follow zoom and fade-in sequences with backdrop blurring for layered UI overlays; these are applied in components like the Kids settings modal (`src/components/kids/layout/settings-modal.tsx`).

| Component / Utility | Location | Role |
|---------------------|----------|------|
| `AnimatedText`       | [src/components/layout/animated-text.tsx:8-28]() | Animated multi-color gradient flowing text rendering |
| `gradient-flow` keyframes | [src/app/globals.css:138-153]() | Defines infinite gradient background animation |
| Modal Transitions    | [src/components/kids/layout/settings-modal.tsx:103]() | Zoom-in and fade-in transition animations on modals |

Sources: [src/app/globals.css:138-153](), [src/components/layout/animated-text.tsx:8-28](), [src/components/kids/layout/settings-modal.tsx:103]()

For detailed motion design patterns and implementation, see [Animation System](#9.3).

Sources: [src/app/globals.css:138-153](), [src/components/layout/animated-text.tsx:8-28](), [src/components/kids/layout/settings-modal.tsx:103]()

---

## Summary Diagram: UI & Theming System Overview

```mermaid
graph TB
    NL1["Theme Configuration (prompts.config.ts)"]
    NL2["UI Components (Radix UI, shadcn/ui)"]
    NL3["Pixel Art & Educational UI"]
    NL4["Animations & Transitions"]

    CE1["prompts.config.ts (theme definitions)"]
    CE2["src/app/layout.tsx (theme processing)"]
    CE3["src/app/globals.css (CSS variables and animations)"]
    CE4["src/components/prompts/hero-categories.tsx (standard UI)"]
    CE5["src/components/kids/layout/settings-modal.tsx (pixel art modals)"]
    CE6["src/components/layout/animated-text.tsx (animated text)"]

    NL1 --> CE1
    CE1 --> CE2
    CE2 --> CE3
    CE3 -->|CSS Vars / Animations| CE4
    CE3 --> CE5
    CE3 --> CE6
    NL2 --> CE4
    NL3 --> CE5
    NL3 --> CE5
    NL4 --> CE6
```
Sources: [src/app/globals.css:1-225](), [src/components/prompts/hero-categories.tsx:9-52](), [src/components/kids/layout/settings-modal.tsx:54-114](), [src/components/layout/animated-text.tsx:8-28]()

This diagram demonstrates the relationship between natural language system concepts (theme configuration, UI component styles, pixel-art modules, animations) and their corresponding concrete code entities, linking configuration files, styling layers, and React components.

Sources: [src/app/globals.css:1-225](), [src/components/prompts/hero-categories.tsx:9-52](), [src/components/kids/layout/settings-modal.tsx:54-114](), [src/components/layout/animated-text.tsx:8-28]()

---

This overview outlines the architectural layers that shape the UI experience and theming in prompts.chat. Each aspect is expanded in linked child pages focusing on detailed technical explanations.

For more, see the child pages:
- [Theming System](#9.1)
- [Component Patterns](#9.2)
- [Animation System](#9.3)

---

# Page: Theming System

# Theming System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [prompts.config.ts](prompts.config.ts)
- [src/app/globals.css](src/app/globals.css)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/kids/elements/pixel-art.tsx](src/components/kids/elements/pixel-art.tsx)
- [src/components/kids/elements/progress-map.tsx](src/components/kids/elements/progress-map.tsx)
- [src/components/kids/elements/story-scene.tsx](src/components/kids/elements/story-scene.tsx)
- [src/components/kids/layout/settings-modal.tsx](src/components/kids/layout/settings-modal.tsx)
- [src/components/layout/animated-text.tsx](src/components/layout/animated-text.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/prompts/hero-categories.tsx](src/components/prompts/hero-categories.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



## Purpose and Scope

The theming system provides a unified visual design language across the application through:

- **Theme variants** (`flat`, `default`, `brutal`) that control shadow and border styles [src/app/globals.css:158-190]().
- **Density modes** (`compact`, `default`, `comfortable`) that adjust spacing, font scale, and container padding [src/app/globals.css:213-225]().
- **Border radius settings** (`none`, `sm`, `md`, `lg`) mapped to `--radius` CSS variables [src/lib/config/index.ts:11-15](), [src/app/globals.css:43-46]().
- **Hex to OKLCH conversion** via configuration and runtime environment variable overrides (`PCHAT_COLOR`, `PCHAT_THEME_RADIUS`, etc.) for dynamic, perceptually uniform color injection [src/lib/config/index.ts:117-185]().

Sources: [src/app/globals.css:158-190](), [src/app/globals.css:213-225](), [src/lib/config/index.ts:11-22](), [src/lib/config/index.ts:117-185]()

---

## Configuration Architecture & Server-Side Injection

The theming pipeline resolves configuration values via `prompts.config.ts` and runtime overrides processed by `applyEnvOverrides()` in `src/lib/config/index.ts` [src/lib/config/index.ts:117-185](). It reads the application configuration, computes dynamic properties for variants, density, and colors, and injects them into the DOM styles and CSS custom properties defined in `src/app/globals.css` [src/app/globals.css:7-47]().

### Diagram: Configuration to Theming Code Entities

```mermaid
graph TB
    subgraph NaturalLanguageSpace["Natural Language Space"]
        UserConfig["User Theme Preference"]
        EnvOverride["Environment Overrides"]
        DesignSystem["Design System Rules"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        PromptsConfig["prompts.config.ts"]
        GetConfig["getConfig()"]
        ApplyEnv["applyEnvOverrides()"]
        ThemeStyles["Theme Styles and CSS Variables"]
        GlobalsCSS["globals.css"]
    end
    
    UserConfig --> PromptsConfig
    PromptsConfig --> GetConfig
    EnvOverride --> ApplyEnv
    GetConfig --> ApplyEnv
    ApplyEnv --> ThemeStyles
    ThemeStyles --> GlobalsCSS
    DesignSystem --> GlobalsCSS
```

Sources: [prompts.config.ts:20-32](), [src/lib/config/index.ts:117-185](), [src/app/globals.css:7-47]()

---

## Color Conversion & Dynamic Injection

To maintain perceptual uniformity across arbitrary brand color inputs, the configuration system accepts hex or OKLCH color values through `ThemeConfig.colors` [src/lib/config/index.ts:17-21]() and overrides them via runtime environment variables like `PCHAT_COLOR` [src/lib/config/index.ts:147-152](). The `hexToOklch` function [src/app/layout.tsx:120-142]() performs the conversion from hex to OKLCH format.

### Diagram: Runtime Theme Resolution and CSS Injection

```mermaid
graph TB
    subgraph NaturalLanguageSpace["Natural Language Space"]
        BrandGoal["Brand Color Requirement"]
        LayoutSpacing["Layout Density Goal"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        ThemeConfigInterface["ThemeConfig"]
        EnvReader["applyEnvOverrides()"]
        HexToOklch["hexToOklch()"]
        CssVariables["CSS Custom Properties"]
    end
    
    BrandGoal --> ThemeConfigInterface
    LayoutSpacing --> ThemeConfigInterface
    ThemeConfigInterface --> EnvReader
    EnvReader -- "config.theme.colors.primary (hex)" --> HexToOklch
    HexToOklch -- "oklch value" --> CssVariables
```

The parsed color values map into CSS custom properties under `:root` and `.dark` blocks, allowing seamless runtime theme switching without rebuilding the application [src/app/layout.tsx:160-172](), [src/app/globals.css:49-116]().

Sources: [src/lib/config/index.ts:17-21](), [src/lib/config/index.ts:86-185](), [src/app/globals.css:49-116](), [src/app/layout.tsx:120-142](), [src/app/layout.tsx:160-172]()

---

## Theme Variants

Variant controls are implemented via CSS classes applied to container elements:

- **Flat (`.theme-flat`)**: Eliminates shadows entirely and sets simplified border colors [src/app/globals.css:158-173](). It also strips button and input shadows [src/app/globals.css:198-208]().
- **Default (`.theme-default`)**: Applies balanced, subtle elevation shadows (`--shadow-sm`, `--shadow`, `--shadow-md`, `--shadow-lg`) [src/app/globals.css:175-181]().
- **Brutal (`.theme-brutal`)**: Enforces zero border radius (`--radius: 0 !important`), 2-pixel borders using `currentColor`, and hard offset shadows [src/app/globals.css:184-196]().

Sources: [src/app/globals.css:158-208]()

---

## Density Modes

Density modes alter layout scaling and spacing parameters across the application:

| Density Mode | Spacing Unit Variable | Base Font Size | Description |
|--------------|-----------------------|----------------|-------------|
| `compact`    | `0.75rem`             | `0.875rem`     | Tighter padding and scaled-down heading typography [src/app/globals.css:213-225]() |
| `default`    | `1rem`                | `1rem`         | Standard balanced layout spacing |
| `comfortable`| `1.25rem`             | `1.125rem`     | Expanded whitespace for readability |

These modes are applied as CSS classes like `density-compact` on container elements [src/app/globals.css:213-225]().

Sources: [src/app/globals.css:213-225]()

---

## Globals.css and CSS Custom Properties

Core design tokens are declared as CSS custom properties under `:root` and `.dark` selectors within `src/app/globals.css` [src/app/globals.css:49-116](). 

- **Theme Mapping**: Tailwind v4 uses `@theme inline` to map utility tokens like `--color-primary`, `--color-background`, and radius variables (`--radius-sm`, `--radius-md`, `--radius-lg`) directly to underlying custom properties [src/app/globals.css:7-47]().
- **Base Layer Rules**: Global element defaults enforce border colors and text/background rendering [src/app/globals.css:118-129]().

Sources: [src/app/globals.css:7-129]()

---

# Summary

The theming architecture combines static configuration defined in `prompts.config.ts` [prompts.config.ts:20-32]() with runtime environment overrides handled by `applyEnvOverrides()` [src/lib/config/index.ts:117-185](). By leveraging CSS custom property mappings [src/app/globals.css:7-47]() and modular variant/density class sheets [src/app/globals.css:158-225](), the system delivers high-performance, accessible runtime styling.

Sources: [prompts.config.ts:20-32](), [src/lib/config/index.ts:117-185](), [src/app/globals.css:7-225]()

---

# References

- `prompts.config.ts`: User-facing theme configuration (`radius`, `variant`, `density`, `colors`).
- `src/lib/config/index.ts`: Configuration loader, `ThemeConfig` interface, and `applyEnvOverrides()` implementation.
- `src/app/globals.css`: Tailwind v4 theme bindings, `:root`/`.dark` tokens, variants (`.theme-*`), and density classes (`.density-*`).
- `src/app/layout.tsx`: Server-side `hexToOklch` conversion and CSS variable injection.

---

# Page: Component Patterns

# Component Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/prompts/(list)/layout.tsx](src/app/prompts/(list)/layout.tsx)
- [src/components/layout/extension-link.tsx](src/components/layout/extension-link.tsx)
- [src/components/ui/code-view.tsx](src/components/ui/code-view.tsx)
- [src/components/ui/json-tree-view.tsx](src/components/ui/json-tree-view.tsx)
- [src/lib/utils.ts](src/lib/utils.ts)

</details>



This page explains the UI component library used throughout prompts.chat for displaying, managing, and interacting with prompts. These components follow consistent patterns for data presentation, user interaction, and content rendering, utilizing Radix UI primitives and shadcn/ui design patterns.

For UI theming configuration, see [9.1 Theming System](). For animation implementation details, see [9.3 Animation System]().

---

## 1. Component Architecture & Design System Integration

The prompt-related components follow a layered architecture with clear separation between presentation, interaction, and data management concerns. Theme variables such as `--radius` and `--primary` are injected at the root level via `RootLayout`, while utility functions in `src/lib/utils.ts` handle class merging and browser environment detection (`[src/lib/utils.ts:4-6]()`).

### Component Hierarchy and Data Flow

The diagram below illustrates how data flows through the UI layer, associating system abstractions with exact code entities (`CodeView`, `JsonTreeView`, `ExtensionLink`).

**Component System to Code Entity Mapping**

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        CodeViz["Code and JSON Visualization"]
        LayoutGrid["Masonry and Card Lists"]
        BrowserTarget["Browser-Specific Links"]
    end
    
    subgraph "CodeEntitySpace"
        CodeViewComp["CodeView<br/>src/components/ui/code-view.tsx"]
        JsonTreeComp["JsonTreeView<br/>src/components/ui/json-tree-view.tsx"]
        MasonryComp["Masonry<br/>src/components/ui/masonry.tsx"]
        ExtensionLinkComp["ExtensionLink<br/>src/components/layout/extension-link.tsx"]
        UtilsLib["cn / utils<br/>src/lib/utils.ts"]
    end
    
    CodeViz --> CodeViewComp
    CodeViz --> JsonTreeComp
    LayoutGrid --> MasonryComp
    BrowserTarget --> ExtensionLinkComp
    CodeViewComp --> UtilsLib
    ExtensionLinkComp --> UtilsLib
```

Sources: [src/components/ui/code-view.tsx:22-143](), [src/components/ui/json-tree-view.tsx:54-79](), [src/components/layout/extension-link.tsx:15-48](), [src/lib/utils.ts:4-6]()

---

## 2. Code Visualization & Tree Views

### CodeView Component

The `CodeView` component provides a rich interface for displaying code or structured data (`[src/components/ui/code-view.tsx:22-143]()`), primarily designed for JSON and YAML content. It allows toggling between a raw code view with syntax highlighting and a tree view for interactive exploration.

Key features:
- **View Modes:** Users can toggle between `"code"` and `"tree"` modes. Tree view is available only if the content is valid JSON (`[src/components/ui/code-view.tsx:56-75]()`).
- **Syntax Highlighting:** The component manually highlights syntax using helper functions like `highlightJSON` (`[src/components/ui/code-view.tsx:153-195]()`), differentiating keys, strings, numbers, booleans, and null values.
- **Line Numbers:** A fixed gutter showing line numbers is rendered beside the code lines (`[src/components/ui/code-view.tsx:119-122]()`).
- **Expandable Tree:** Tree view uses `JsonTreeViewWrapper`, which renders the parsed JSON data in an expandable/collapsible hierarchical format (`[src/components/ui/code-view.tsx:104-110]()`).

### CodeView Component Flow

```mermaid
graph TD
    subgraph "CodeEntitySpace"
        CV[CodeView]
        JTV[JsonTreeViewWrapper]
        HL[highlightJSON]
    end

    UserInteraction["UserChangesViewMode"] --> ViewModeState["viewModeState"]
    Content["contentString"] --> JSONParse["JSONParseValidation<br/>(isValidJson)"]
    JSONParse -- Valid --> ShowTreeView["RenderJsonTreeViewWrapper"]
    JSONParse -- Invalid --> ShowCodeView["RenderPreWithSyntaxHighlighting"]
    ShowCodeView --> HL
    ShowTreeView --> JTV
```

Sources: [src/components/ui/code-view.tsx:22-195](), [src/components/ui/json-tree-view.tsx:54-79]()

---

### JsonTreeView Component

The `JsonTreeView` component recursively renders JSON data as a tree structure with expand/collapse functionality:

- **Data Model:** Uses a recursive `JsonNode` structure (`[src/components/ui/json-tree-view.tsx:8-13]()`) identifying each node by path and type (`object`, `array`, `string`, `number`, `boolean`, or `null`).
- **Expandable Paths:** Maintains a `Set` of expanded paths via `useState` (`[src/components/ui/json-tree-view.tsx:55-67]()`).
- **Recursive Rendering:** The `renderNode` function traverses JSON nodes recursively (`[src/components/ui/json-tree-view.tsx:110-191]()`), rendering keys with clickable expand/collapse toggles for objects and arrays.
- **Expand/Collapse All:** Provides `expandAll` and `collapseAll` functions, exposed via refs, to control the expansion state of all nodes (`[src/components/ui/json-tree-view.tsx:73-79]()`).

Sources: [src/components/ui/json-tree-view.tsx:8-191]()

---

## 3. Card & List Patterns

### Masonry Layout

A custom `Masonry` component arranges child elements into justified columns based on viewport size, providing a dynamic grid layout.

- **Responsive Columns:** The number of columns adjusts across breakpoints (`default`, `md`, `lg`, `xl`).
- **Position Calculation:** Uses height tracking per column to place items in the shortest column.
- **RTL Support:** Detects and accommodates right-to-left layout with correct item positioning.

### RelatedPrompts Component

The `RelatedPrompts` component renders a grid list of related prompt cards with important prompt metadata.

- **Data:** Displays prompt title, description (truncated), type with a badge, and voting count.
- **Author:** Shows author's avatar with fallback initials and username.
- **Links:** Each prompt card links to the prompt detail page via helper route builders.

Sources: [src/components/prompts/related-prompts.tsx:34-90]()

---

## 4. Browser-Specific Components

### ExtensionLink Component

The `ExtensionLink` component (`[src/components/layout/extension-link.tsx:15-48]()`) dynamically renders a link to the appropriate browser extension based on the user's browser.

- **Browser Detection:** Uses `isChromeBrowser()` and `isFirefoxBrowser()` from `src/lib/utils.ts` to detect the current browser (`[src/components/layout/extension-link.tsx:20-25]()`, `[src/lib/utils.ts:21-41]()`).
- **Dynamic URL:** Sets the `extensionUrl` to either a Chrome extension URL or `FIREFOX_ADDON_URL` (`[src/components/layout/extension-link.tsx:30-31]()`).
- **Iconography:** Displays the appropriate browser icon (Chromium or Firefox SVG) (`[src/components/layout/extension-link.tsx:39-45]()`).

Sources: [src/components/layout/extension-link.tsx:15-48](), [src/lib/utils.ts:21-41]()

---

# Summary

The component patterns in prompts.chat leverage modular React components, Radix UI primitives, and advanced UI constructs to handle complex rendering such as code tree views and masonry layouts. These patterns ensure consistency, accessibility, and maintainability in the rich prompt management interface.

Sources: [src/components/ui/code-view.tsx:1-143](), [src/components/ui/json-tree-view.tsx:1-191](), [src/components/prompts/related-prompts.tsx:34-90](), [src/components/layout/extension-link.tsx:15-48](), [src/lib/utils.ts:21-41]()

---

# Page: Animation System

# Animation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [public/favicon/apple-touch-icon.png](public/favicon/apple-touch-icon.png)
- [public/favicon/favicon-96x96.png](public/favicon/favicon-96x96.png)
- [public/favicon/favicon.ico](public/favicon/favicon.ico)
- [public/favicon/favicon.svg](public/favicon/favicon.svg)
- [public/favicon/site.webmanifest](public/favicon/site.webmanifest)
- [public/favicon/web-app-manifest-192x192.png](public/favicon/web-app-manifest-192x192.png)
- [public/favicon/web-app-manifest-512x512.png](public/favicon/web-app-manifest-512x512.png)
- [src/components/prompts/share-dropdown.tsx](src/components/prompts/share-dropdown.tsx)
- [src/components/ui/animated-date.tsx](src/components/ui/animated-date.tsx)
- [tsconfig.json](tsconfig.json)

</details>



## Purpose and Scope
The Animation System provides interactive visual effects, transitions, and motion patterns integrated throughout prompts.chat. It covers component-level animations like animated text gradients `[src/components/layout/animated-text.tsx:1-28]()` (referencing path patterns) and date hover switches `[src/components/ui/animated-date.tsx:1-48]()`, Tailwind CSS animations, dialog/modal entrance transitions, and pixel art rendering used in the Kids Learning Game `[src/components/kids/elements/pixel-art.tsx:1-188]()`.

Sources: `[src/components/ui/animated-date.tsx:1-48]()`

---

## Animation Architecture
The animation architecture consists of stylesheet-level keyframes `[src/app/globals.css:143-153]()`, Tailwind CSS utility integration `[src/app/globals.css:1-3]()`, and React state-driven transformation handlers `[src/components/ui/animated-date.tsx:12-47]()`.

### Flow Diagram: Animation Architecture Layers

```mermaid
graph TB
    subgraph CSSLayer ["CSS Definition Layer globals.css"]
        GF["gradient-flow @keyframes<br/>src/app/globals.css:143-153"]
        GT["animate-gradient-text<br/>src/app/globals.css:138-140"]
    end
    
    subgraph ComponentLayer ["React Animation Components"]
        AT["AnimatedText<br/>src/components/layout/animated-text.tsx:8-27"]
        AD["AnimatedDate<br/>src/components/ui/animated-date.tsx:12-47"]
        SM["SettingsModal<br/>src/components/kids/layout/settings-modal.tsx:57-91"]
    end
    
    GF --> AT
    GT --> AT
    AD -. "useState & translateY" .-> AD
    SM -. "tw-animate-css & zoom-in" .-> SM
```

Sources: `[src/components/ui/animated-date.tsx:12-47]()`

---

## Core Animation Components

### AnimatedText
`AnimatedText` renders a continuous horizontal gradient flow across text elements using CSS backgrounds and keyframe animations.
- Uses `animate-gradient-text` utility class mapped to `@keyframes gradient-flow` `[src/app/globals.css:138-140]()`.
- Configures background size at `300% 100%` with `backgroundClip: "text"` and transparent text fill.

Sources: `[src/app/globals.css:138-153]()`

### AnimatedDate
`AnimatedDate` toggles between relative time and an exact formatted date on hover `[src/components/ui/animated-date.tsx:12-47]()`.
- Uses React `useState` (`showExact`) to track mouse hover states `[src/components/ui/animated-date.tsx:13]()`, `[src/components/ui/animated-date.tsx:25-26]()`.
- Animates vertical text shifts using CSS classes `transition-transform duration-300 ease-in-out` and `-translate-y-full` `[src/components/ui/animated-date.tsx:31-44]()`.

Sources: `[src/components/ui/animated-date.tsx:1-48]()`

### SettingsModal & Dialog Transitions
Modals like `SettingsModal` utilize entrance animation utilities from Tailwind plugins (`tw-animate-css`) for smooth pop-up effects `[src/components/kids/layout/settings-modal.tsx:1-184]()`.
- Utilizes classes like `animate-in zoom-in-95 fade-in duration-200` `[src/components/kids/layout/settings-modal.tsx:103]()`.
- Backdrops incorporate `backdrop-blur-sm` `[src/components/kids/layout/settings-modal.tsx:97]`.

Sources: `[src/components/kids/layout/settings-modal.tsx:57-113]()`

### Pixel Art & Game Animations
The Kids Learning Game uses pixel art SVG components (`PixelTree`, `PixelRobot`, etc.) and CSS properties optimized for pixelation `[src/components/kids/elements/pixel-art.tsx:1-188]()`.
- `imageRendering: "pixelated"` styling ensures crisp scaling on retro elements `[src/components/kids/elements/pixel-art.tsx:11]()`.
- Horizontal scrolling maps use smooth DOM navigation (`scrollBy`) `[src/components/kids/elements/progress-map.tsx:53-59]()`.

Sources: `[src/components/kids/elements/pixel-art.tsx:1-188]()`, `[src/components/kids/elements/progress-map.tsx:53-60]()`

---

## Global CSS Keyframes & Utility Classes

Key animation definitions and variables in `src/app/globals.css`:

| Symbol / Utility | Role | Reference |
|------------------|------|-----------|
| `@keyframes gradient-flow` | Defines horizontal color shift across 0% to 100% background positions | `[src/app/globals.css:143-153]()` |
| `.animate-gradient-text` | Applies 20s infinite gradient flow animation | `[src/app/globals.css:138-140]()` |
| `tw-animate-css` | Imported plugin providing entrance/exit utility classes | `[src/app/globals.css:2]()` |

Sources: `[src/app/globals.css:1-153]()`

---

## Concept to Code Entity Mapping

### Diagram 1: Natural Language Concepts to Code Entities (Part 1)

```mermaid
graph LR
    subgraph NaturalLanguageSpace1 ["Natural Language Concepts"]
        FlowConcept["Flowing Gradient Text"]
        DateFlipConcept["Hover Date Flip"]
        ModalTransitionConcept["Modal Zoom & Fade"]
    end
    
    subgraph CodeEntitySpace1 ["Code Entities"]
        AnimTextCode["AnimatedText<br/>src/components/layout/animated-text.tsx:8-27"]
        AnimDateCode["AnimatedDate<br/>src/components/ui/animated-date.tsx:12-47"]
        SettingsModalCode["SettingsModal<br/>src/components/kids/layout/settings-modal.tsx:103"]
    end
    
    FlowConcept --> AnimTextCode
    DateFlipConcept --> AnimDateCode
    ModalTransitionConcept --> SettingsModalCode
```

Sources: `[src/components/ui/animated-date.tsx:12-47]()`, `[src/components/kids/layout/settings-modal.tsx:103]()`

### Diagram 2: Natural Language Concepts to Code Entities (Part 2)

```mermaid
graph LR
    subgraph NaturalLanguageSpace2 ["Natural Language Concepts"]
        PixelRenderingConcept["Crisp Pixel Art Rendering"]
        SmoothScrollConcept["Map Horizontal Scrolling"]
        KeyframeAnimConcept["Stylesheet Keyframes"]
    end
    
    subgraph CodeEntitySpace2 ["Code Entities"]
        PixelArtCode["PixelTree & PixelRobot<br/>src/components/kids/elements/pixel-art.tsx:11,167"]
        ProgressMapCode["ProgressMap scrollRef<br/>src/components/kids/elements/progress-map.tsx:32,53-59"]
        GlobalsCSSCode["globals.css @keyframes<br/>src/app/globals.css:143-153"]
    end
    
    PixelRenderingConcept --> PixelArtCode
    SmoothScrollConcept --> ProgressMapCode
    KeyframeAnimConcept --> GlobalsCSSCode
```

Sources: `[src/components/kids/elements/pixel-art.tsx:11]()`, `[src/components/kids/elements/progress-map.tsx:32,53-59]()`, `[src/app/globals.css:143-153]()`

---

## Summary Table of Animation Components

| Component / Utility | File Path | Primary Function |
|---------------------|-----------|------------------|
| `AnimatedText` | `[src/components/layout/animated-text.tsx:1-28]()` | Continuous flowing text color gradient animation |
| `AnimatedDate` | `[src/components/ui/animated-date.tsx:1-48]()` | Vertical translation flip between relative and exact date |
| `SettingsModal` | `[src/components/kids/layout/settings-modal.tsx:57-113]()` | Dialog zoom/fade entrance transitions |
| `PixelRobot` / Art | `[src/components/kids/elements/pixel-art.tsx:1-188]()` | Retro pixel art rendering with state-driven moods |
| `ProgressMap` | `[src/components/kids/elements/progress-map.tsx:1-541]()` | Horizontal smooth scrolling container for level navigation |

Sources: `[src/components/ui/animated-date.tsx:1-48]()`, `[src/components/kids/layout/settings-modal.tsx:57-113]()`, `[src/components/kids/elements/pixel-art.tsx:1-188]()`, `[src/components/kids/elements/progress-map.tsx:1-541]()`

# End of 9.3 Animation System

---

# Page: Admin System

# Admin System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/admin/page.tsx](src/app/admin/page.tsx)
- [src/components/admin/admin-tabs.tsx](src/components/admin/admin-tabs.tsx)
- [src/components/admin/prompts-management.tsx](src/components/admin/prompts-management.tsx)

</details>



The Admin System provides a comprehensive set of administrative features needed to manage the prompts.chat platform, accessible exclusively to users with the `ADMIN` role. This system covers platform statistics, content moderation, user management, taxonomy configuration, and bulk data operations. It integrates closely with authentication and prompt CRUD operations for secured, effective governance.

---

## Admin Dashboard

The Admin Dashboard is the central hub for administrative oversight and control. It is implemented in `src/app/admin/page.tsx`, where access is guarded by a session user role check requiring `ADMIN` privileges [src/app/admin/page.tsx:31-33](). Upon loading, the dashboard performs multiple database count queries to collect system-wide metrics such as users, prompts, categories, and tags, plus AI search feature status and prompt embedding statistics [src/app/admin/page.tsx:36-78](). The main UI uses the `AdminTabs` component (`src/components/admin/admin-tabs.tsx`) to organize feature pages under tabs like Users, Categories, Tags, Webhooks, Prompts, Bots, Teams, and Reports [src/app/admin/page.tsx:184-207](), [src/components/admin/admin-tabs.tsx:7-104]().

**Admin Dashboard Interaction Diagram**

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        UserReq["Admin Page Access Request"]
        AuthValidation["Role Authorization Check"]
    end

    subgraph "CodeEntitySpace"
        AuthValidation --> AdminPageHandler["AdminPage (src/app/admin/page.tsx)"]
        AdminPageHandler --> DbQueries["DB Count Queries (db.user.count, db.prompt.count, etc)"]
        AdminPageHandler --> AdminTabsComp["AdminTabs (src/components/admin/admin-tabs.tsx)"]
        AdminTabsComp --> UsersTable["UsersTable"]
        AdminTabsComp --> CategoriesTable["CategoriesTable"]
        AdminTabsComp --> TagsTable["TagsTable"]
        AdminTabsComp --> WebhooksTable["WebhooksTable"]
        AdminTabsComp --> PromptsManagement["PromptsManagement"]
        AdminTabsComp --> BotsManagement["BotsManagement"]
        AdminTabsComp --> TeamsManagement["TeamsManagement"]
        AdminTabsComp --> ReportsTable["ReportsTable"]
    end

    UserReq --> AuthValidation
```

Sources: [src/app/admin/page.tsx:31-207](), [src/components/admin/admin-tabs.tsx:7-104]()

For detailed features of the dashboard including stats cards and tab navigation UI, see [Admin Dashboard](#10.1).

---

## Content Moderation

Content moderation is a critical part of the admin features, built around tracking user reports and managing prompt visibility. Reports are stored in the `PromptReport` model and shown in the `ReportsTable` UI, allowing admins to review, dismiss, or act on reported prompts [src/app/admin/page.tsx:112-134](). Admins may relist unlisted prompts or restore deleted ones via corresponding API endpoints triggered from this interface.

**Content Moderation Workflow Diagram**

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        ReportReview["User Submits Report / Admin Reviews"]
        ActionDispatch["Admin Moderation Action (Review, Dismiss, Relist, Restore)"]
    end

    subgraph "CodeEntitySpace"
        ActionDispatch --> ReportsTableComp["ReportsTable UI (src/components/admin/reports-table.tsx)"]
        ReportsTableComp --> PatchReportAPI["PATCH /api/admin/reports/:id"]
        ReportsTableComp --> UnlistPromptAPI["POST /api/prompts/:id/unlist"]
        ReportsTableComp --> RestorePromptAPI["POST /api/prompts/:id/restore"]

        PatchReportAPI --> PromptReportModel["PromptReport DB Model"]
        UnlistPromptAPI --> PromptIsUnlistedField["Prompt.isUnlisted Flag"]
        RestorePromptAPI --> PromptDeletedAtField["Prompt.deletedAt Field"]
    end

    ReportReview --> ActionDispatch
```

Sources: [src/app/admin/page.tsx:112-134]()

For more details about quality checks, automatic delisting, spam workflows, relist requests, and manual moderation, see [Content Moderation](#10.2).

---

## User Management

The user management module gives admins control over platform users, enabling verification toggling, flagging for policy violations, role assignments including making/removing admin status, credit editing, and enforcement of daily prompt generation limits. This is implemented primarily via the `UsersTable` component [src/app/admin/page.tsx:198](). The system maintains fields like `dailyGenerationLimit` and `generationCreditsRemaining` on the `User` model, which are reset automatically through a scheduled cron job implemented in `src/app/api/cron/reset-credits/route.ts` and triggered via GitHub Actions.

**User Management Administration Diagram**

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        UserAdmin["Admin Controls User Accounts & Limits"]
        CronReset["Automated Daily Credit Reset Process"]
    end

    subgraph "CodeEntitySpace"
        UserAdmin --> UsersTableComp["UsersTable (src/components/admin/users-table.tsx)"]
        UsersTableComp --> RoleModification["Role & Verification Modifications"]
        UsersTableComp --> Flagging["User Flag / Unflag Controls"]
        UsersTableComp --> CreditEditing["Edit User Generation Credits & Limits"]

        CreditEditing --> UserModel["User DB Model: dailyGenerationLimit, generationCreditsRemaining"]

        CronReset --> CreditResetAPI["src/app/api/cron/reset-credits/route.ts"]
        CreditResetAPI --> UserModel
    end

    UserAdmin --> CronReset
```

Sources: [src/app/admin/page.tsx:198](), [src/app/api/cron/reset-credits/route.ts]()

For a deep dive into user admin capabilities including verification, flagging, credit adjustments, and generation limits, see [User Management](#10.3).

---

## Bulk Operations & Webhooks

Bulk administrative operations are handled through the `PromptsManagement` component, which provides UI controls for batch importing prompts, generating embeddings for AI semantic search, creating slugs for SEO, and generating related prompt links. These operations invoke dedicated backend API routes to process data efficiently and keep content in sync [src/components/admin/prompts-management.tsx:197-208](). Meanwhile, webhook configurations are managed in the `WebhooksTable`, representing `WebhookConfig` entities that deliver outbound notifications for admin-integrated systems [src/app/admin/page.tsx:110-112]().

**Bulk Operations & Webhooks Diagram**

```mermaid
graph TD
    subgraph "Bulk Operations & Webhooks"
        PromptsMgmt["PromptsManagement (src/components/admin/prompts-management.tsx)"]
        WebhooksTableComp["WebhooksTable (src/components/admin/webhooks-table.tsx)"]

        PromptsMgmt --> ImportPromptsAPI["POST /api/admin/import-prompts"]
        PromptsMgmt --> GenerateEmbeddingsAPI["POST /api/admin/generate-embeddings"]
        PromptsMgmt --> GenerateSlugsAPI["POST /api/admin/generate-slugs"]
        PromptsMgmt --> GenerateRelatedAPI["POST /api/admin/generate-related"]

        WebhooksTableComp --> WebhookConfigModel["WebhookConfig Database Model"]
    end
```

Sources: [src/app/admin/page.tsx:110-112](), [src/components/admin/prompts-management.tsx:197-208]()

For comprehensive guides on AI embedding workflows, slug and related prompt batch generation, CSV import/export, and webhook setup and delivery, see [Bulk Operations & Webhooks](#10.4).

---

This parent page provides an overview of the administrative capabilities in prompts.chat and how major features are organized and interconnected. Readers should consult the respective child pages for implementation details, UI documentation, and operational workflows.

---

# Page: Admin Dashboard

# Admin Dashboard

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/admin/page.tsx](src/app/admin/page.tsx)
- [src/components/admin/admin-tabs.tsx](src/components/admin/admin-tabs.tsx)
- [src/components/admin/prompts-management.tsx](src/components/admin/prompts-management.tsx)

</details>



This page documents the Admin Dashboard for the prompts.chat project, accessible at the `/admin` route [src/app/admin/page.tsx:1](). It is a central interface designed for administrators to manage core platform entities such as users, prompts, categories, tags, webhooks, bots, teams, and user reports [src/app/admin/page.tsx:8-17](). The dashboard provides statistical insights, efficient navigation via tabs, and comprehensive management interfaces, including bulk operations and moderation tools [src/app/admin/page.tsx:136-215]().

---

## Purpose and Scope

- Manage platform-wide counts and statistics to monitor user engagement and content [src/app/admin/page.tsx:36-42]().
- Provide tabbed navigation between users, categories, tags, webhooks, prompts, bots, teams, and reports [src/components/admin/admin-tabs.tsx:7-108]().
- Facilitate administrative operations like prompt import, deletion, embedding generation, slug generation, and moderation [src/components/admin/prompts-management.tsx:132-208]().
- Enforce access control by restricting dashboard access to users with `ADMIN` role [src/app/admin/page.tsx:31-33]().
- Integration with server APIs to safely perform CRUD, bulk, and moderation actions [src/components/admin/prompts-management.tsx:141-208]().

This page covers data flows, key components, and the internal implementation of the Admin Dashboard.

Sources: [src/app/admin/page.tsx:26-42](), [src/components/admin/admin-tabs.tsx:7-108](), [src/components/admin/prompts-management.tsx:132-208]()

---

## Access Control

- The admin dashboard is implemented as a Next.js server component at `src/app/admin/page.tsx` [src/app/admin/page.tsx:26]().
- It invokes the `auth()` function from the authentication library to retrieve the user's session [src/app/admin/page.tsx:27]().
- Immediately redirects non-admin users to the homepage `/` by verifying `session.user.role === "ADMIN"` [src/app/admin/page.tsx:31-33]().

```typescript
const session = await auth();
if (!session?.user || session.user.role !== "ADMIN") {
  redirect("/");
}
```
This ensures the dashboard and all its operations are restricted to authorized administrators only, enforced also at the API route layer.

Sources: [src/app/admin/page.tsx:26-33]()

---

## Dashboard Layout and Data Flow

The `AdminPage` server component fetches all required data for the dashboard using Prisma ORM calls and internal utility functions [src/app/admin/page.tsx:36-134](). Data is fetched in parallel for efficiency via `Promise.all`.

### Data fetched includes:

- User count via `db.user.count()` [src/app/admin/page.tsx:37]()
- Prompt count via `db.prompt.count()` [src/app/admin/page.tsx:38]()
- Category count via `db.category.count()` [src/app/admin/page.tsx:39]()
- Tag count via `db.tag.count()` [src/app/admin/page.tsx:40]()
- Number of prompts without embeddings and total public prompts (conditional on AI search via `isAISearchEnabled()`) [src/app/admin/page.tsx:41-63]()
- Number of prompts missing URL slugs and total prompts [src/app/admin/page.tsx:66-78]()
- Lists of categories, tags, webhook configurations, and prompt reports for rendering tables [src/app/admin/page.tsx:81-134]()

### Diagram: Admin Page Data Flow and Code Entity Mapping (Natural Language to Code Entity Space)

```mermaid
flowchart TD
    AdminPage["AdminPage src/app/admin/page.tsx"]
    PrismaClient["PrismaClient db instance src/lib/db.ts"]
    EmbeddingChecker["isAISearchEnabled src/lib/ai/embeddings.ts"]

    AdminPage -->|"db.user.count()"| PrismaClient
    AdminPage -->|"db.prompt.count()"| PrismaClient
    AdminPage -->|"db.category.count()"| PrismaClient
    AdminPage -->|"db.tag.count()"| PrismaClient
    AdminPage -->|"db.prompt.count (embedding = null)"| PrismaClient
    AdminPage -->|"db.prompt.count (slug = null)"| PrismaClient
    AdminPage -->|"db.category.findMany()"| PrismaClient
    AdminPage -->|"db.tag.findMany()"| PrismaClient
    AdminPage -->|"db.webhookConfig.findMany()"| PrismaClient
    AdminPage -->|"db.promptReport.findMany()"| PrismaClient
    AdminPage --> EmbeddingChecker

    AdminPage --> StatsCards["StatsCards UI Section"]
    AdminPage --> AdminTabs["AdminTabs src/components/admin/admin-tabs.tsx"]
```

Sources: [src/app/admin/page.tsx:26-134](), [src/lib/ai/embeddings.ts]()

---

## Stats Cards Section

At the top of the dashboard UI, four data cards display key counts for users, prompts, categories, and tags [src/app/admin/page.tsx:143-181]():

| Metric     | Icon               | Prisma Query                         |
|------------|--------------------|------------------------------------|
| Users      | `Users`            | `db.user.count()` [src/app/admin/page.tsx:37]() |
| Prompts    | `FileText`         | `db.prompt.count()` [src/app/admin/page.tsx:38]() |
| Categories | `FolderTree`       | `db.category.count()` [src/app/admin/page.tsx:39]() |
| Tags       | `Tags`             | `db.tag.count()` [src/app/admin/page.tsx:40]() |

Each card displays the count with iconography for quick visual identification.

Sources: [src/app/admin/page.tsx:143-181]()

---

## Tab Navigation Layout

The dashboard uses the `AdminTabs` client component for tabbed navigation across major admin sections [src/components/admin/admin-tabs.tsx:32-110]().

- Tabs include: `users`, `categories`, `tags`, `webhooks`, `prompts`, `bots`, `teams`, and `reports` [src/components/admin/admin-tabs.tsx:7]()
- Tab state is synchronized with the URL hash (e.g., `/#prompts`) allowing permalinkable views and persistence across refreshes [src/components/admin/admin-tabs.tsx:36-50]()
- Tab changes update the URL fragment using `window.history.replaceState` [src/components/admin/admin-tabs.tsx:52-55]()
- The active tab is initialized from the hash on mount [src/components/admin/admin-tabs.tsx:43-46]()

### Diagram: Admin Tabs Navigation Structure

```mermaid
graph LR
    AdminTabs["AdminTabs src/components/admin/admin-tabs.tsx"]

    AdminTabs --> TabUsers["users -> UsersTable"]
    AdminTabs --> TabCat["categories -> CategoriesTable"]
    AdminTabs --> TabTags["tags -> TagsTable"]
    AdminTabs --> TabWeb["webhooks -> WebhooksTable"]
    AdminTabs --> TabPrompts["prompts -> PromptsManagement"]
    AdminTabs --> TabBots["bots -> BotsManagement"]
    AdminTabs --> TabTeams["teams -> TeamsManagement"]
    AdminTabs --> TabRep["reports -> ReportsTable"]
```

The `reports` tab shows a badge counting the number of reports with status `PENDING` to alert admins [src/components/admin/admin-tabs.tsx:92-96]().

Sources: [src/components/admin/admin-tabs.tsx:7-108](), [src/app/admin/page.tsx:184-212]()

---

## PromptsManagement Component

A React client component in `src/components/admin/prompts-management.tsx` provides an interactive panel for managing prompt data and bulk operations [src/components/admin/prompts-management.tsx:99-208](). It supports:

- Prompt search and pagination [src/components/admin/prompts-management.tsx:132-155]()
- Prompt deletion with confirmation [src/components/admin/prompts-management.tsx:172-195]()
- Importing community prompts (conditional on clone branding) [src/components/admin/prompts-management.tsx:106]()
- Generating AI embeddings, URL slugs, and related prompts with progress indicators [src/components/admin/prompts-management.tsx:112-120]()
- Status badges and filtering options for the prompts list [src/components/admin/prompts-management.tsx:130-170]()

### Properties of `PromptsManagement`

| Prop                    | Type     | Description                                                        |
|-------------------------|----------|--------------------------------------------------------------------|
| `aiSearchEnabled`       | boolean  | Shows embedding generation controls if true (requires OpenAI key) [src/components/admin/prompts-management.tsx:92]() |
| `promptsWithoutEmbeddings` | number | Counts prompts pending embeddings generation [src/components/admin/prompts-management.tsx:93]() |
| `totalPublicPrompts`    | number   | Total public prompts for gating regenerate operation [src/components/admin/prompts-management.tsx:94]() |
| `promptsWithoutSlugs`   | number   | Number of prompts missing slugs [src/components/admin/prompts-management.tsx:95]() |
| `totalPrompts`          | number   | Total prompt count for regenerate slug operation [src/components/admin/prompts-management.tsx:96]() |

### Branding and Operation Restrictions

The dashboard uses a branding check via `useBranding()` and its `useCloneBranding` flag to restrict certain operations (import and bulk delete) to clones of the site [src/components/admin/prompts-management.tsx:31-106]().

```typescript
const branding = useBranding();
const canModifyCommunityPrompts = branding.useCloneBranding;
```

This prevents modifications to the canonical dataset on the main `prompts.chat` instance.

Sources: [src/components/admin/prompts-management.tsx:31-106]()

### Diagram: PromptsManagement Operations and API Integration (Natural Language to Code Entity Space)

```mermaid
flowchart LR
    PM["PromptsManagement src/components/admin/prompts-management.tsx"]

    PM -->|"GET /api/admin/prompts"| FetchPrompts["fetchPrompts"]
    PM -->|"DELETE /api/admin/prompts/:id"| DelPrompt["handleDeletePrompt"]
    PM -->|"POST /api/admin/import-prompts"| Import["handleImport"]
    PM -->|"POST /api/admin/embeddings"| Embeddings["handleGenerateEmbeddings"]
    PM -->|"POST /api/admin/related-prompts"| Related["handleGenerateRelatedPrompts"]
    PM -->|"POST /api/admin/slugs"| Slugs["handleGenerateSlugs"]
```

It manages asynchronous operations with streaming progress updates via Server-Sent Events on embedding, slug, and related prompt generation.

Sources: [src/components/admin/prompts-management.tsx:132-208]()

### Prompts List Fetching

The prompts list is fetched with paging (10 per page), search by title, and filtering options (`all`, `featured`, `unlisted`, `deleted`) [src/components/admin/prompts-management.tsx:132-140]():

- Parameters passed as URL query string to `/api/admin/prompts` [src/components/admin/prompts-management.tsx:135-140]()
- Results update the component's state and UI table [src/components/admin/prompts-management.tsx:148-149]()
- Supports actions like deleting individual prompts post-confirmation [src/components/admin/prompts-management.tsx:172-195]()

Sources: [src/components/admin/prompts-management.tsx:132-155](), [src/components/admin/prompts-management.tsx:172-195]()

### AI Embedding Generation UI

- Visible only when `aiSearchEnabled` is true (requires configured OpenAI key) [src/components/admin/prompts-management.tsx:92]()
- Calls `POST /api/admin/embeddings` and consumes SSE stream to show progress bars for successful and failed jobs.
- Uses `ProgressState` interface to represent progress metrics [src/components/admin/prompts-management.tsx:43-48]().

```typescript
interface ProgressState {
  current: number;
  total: number;
  success: number;
  failed: number;
}
```

Sources: [src/components/admin/prompts-management.tsx:43-48]()

---

## Overall Component Architecture

### Diagram: Admin Component Tree and API Route Connections

```mermaid
graph TD
    subgraph "Server Page"
        AdminPage["AdminPage src/app/admin/page.tsx"]
    end

    subgraph "Admin Components"
        AdminTabs["AdminTabs src/components/admin/admin-tabs.tsx"]
        UsersTable["UsersTable src/components/admin/users-table.tsx"]
        CategoriesTable["CategoriesTable src/components/admin/categories-table.tsx"]
        TagsTable["TagsTable src/components/admin/tags-table.tsx"]
        WebhooksTable["WebhooksTable src/components/admin/webhooks-table.tsx"]
        PM["PromptsManagement src/components/admin/prompts-management.tsx"]
        BotsManagement["BotsManagement src/components/admin/bots-management.tsx"]
        TeamsManagement["TeamsManagement src/components/admin/teams-management.tsx"]
        ReportsTable["ReportsTable src/components/admin/reports-table.tsx"]
    end

    subgraph "Admin API Routes"
        ImportPrompts["ImportPrompts API"]
        EmbeddingsAPI["Embeddings API"]
        SlugsAPI["Slugs API"]
        RelatedPromptsAPI["RelatedPrompts API"]
        PromptsAPI["Prompts API"]
    end

    AdminPage --> AdminTabs
    AdminTabs --> UsersTable
    AdminTabs --> CategoriesTable
    AdminTabs --> TagsTable
    AdminTabs --> WebhooksTable
    AdminTabs --> PM
    AdminTabs --> BotsManagement
    AdminTabs --> TeamsManagement
    AdminTabs --> ReportsTable

    PM --> ImportPrompts
    PM --> EmbeddingsAPI
    PM --> SlugsAPI
    PM --> RelatedPromptsAPI
    PM --> PromptsAPI
```

Sources: [src/app/admin/page.tsx:184-215](), [src/components/admin/admin-tabs.tsx:32-108](), [src/components/admin/prompts-management.tsx:141-208]()

---

## Summary

The Admin Dashboard is a secure, integrated panel for managing prompts.chat platform content at scale. It offers critical metrics, a smooth tabbed interface, and detailed user, category, tag, webhook, prompt, bot, team, and report management [src/app/admin/page.tsx:136-215](). Heavy operations like embedding or slug generation use event streaming for progress feedback [src/components/admin/prompts-management.tsx:112-120](). Access control and branding safeguards protect operations to maintain dataset integrity [src/app/admin/page.tsx:31-33](), [src/components/admin/prompts-management.tsx:106]().

Sources: [src/app/admin/page.tsx:31-215](), [src/components/admin/prompts-management.tsx:106-120]()

---

# Page: Content Moderation

# Content Moderation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml)
- [.github/workflows/update-contributors.yml](.github/workflows/update-contributors.yml)
- [prisma/migrations/20251217173000_add_delist_reason/migration.sql](prisma/migrations/20251217173000_add_delist_reason/migration.sql)
- [src/app/api/admin/prompts/[id]/route.ts](src/app/api/admin/prompts/[id]/route.ts)
- [src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml](src/app/api/prompt-builder/chat/prompt-builder-agent.prompt.yml)
- [src/app/api/prompts/[id]/feature/route.ts](src/app/api/prompts/[id]/feature/route.ts)
- [src/app/api/prompts/[id]/unlist/route.ts](src/app/api/prompts/[id]/unlist/route.ts)
- [src/lib/ai/load-prompt.ts](src/lib/ai/load-prompt.ts)
- [src/lib/ai/quality-check.prompt.yml](src/lib/ai/quality-check.prompt.yml)
- [src/lib/ai/quality-check.ts](src/lib/ai/quality-check.ts)
- [src/lib/ai/sql-generation.prompt.yml](src/lib/ai/sql-generation.prompt.yml)
- [src/lib/ai/translate.prompt.yml](src/lib/ai/translate.prompt.yml)

</details>



## Purpose and Scope

This document details the content moderation system in `prompts.chat`. It explains how submissions are auto-delisted based on quality checks, managed through a report queue, subject to manual review by administrators, and handled via relist requests and spam-check workflows.

The key focus areas include the AI-powered prompt quality check logic implemented in `checkPromptQuality()` [src/lib/ai/quality-check.ts:72-164](), automated prompt quality rules defined in [src/lib/ai/quality-check.prompt.yml:1-62](), report queues for user reports, and admin endpoints for toggling prompt visibility, featured state, or hard deletion.

For related administrative interface and user management features, see Admin Dashboard (10.1) and User Management (10.3).

Sources:
[src/lib/ai/quality-check.ts:1-173](),
[src/lib/ai/quality-check.prompt.yml:1-62](),
[src/app/api/prompts/[id]/unlist/route.ts:6-71](),
[src/app/api/prompts/[id]/feature/route.ts:5-59]()

---

## Content Moderation Architecture

The moderation system integrates several subsystems: automated quality checks, a report queue, spam detection workflows, and manual admin moderation actions. Submissions enter the system via HTTP API calls or GitHub contributions, undergo automated AI-powered content evaluation, may be flagged through user reporting, and can be manually moderated by administrators.

### System Data Flow Diagram

```mermaid
graph TB
    subgraph "ContentSubmission"
        Create["POST /api/prompts"]
        Update["PATCH /api/prompts/:id"]
    end
    
    subgraph "AutomatedModeration"
        QualityCheck["checkPromptQuality"]
        AutoDelist["Auto-Delist isUnlisted=true delistReason"]
    end
    
    subgraph "CommunityReporting"
        UserReport["User submits report PromptReport"]
        ReportQueue["PromptReport status: PENDING"]
        AdminReview["ReportsTable UI"]
    end
    
    subgraph "AdminActions"
        FeatureToggle["POST /api/prompts/:id/feature Toggle Featured"]
        ManualDelistToggle["POST /api/prompts/:id/unlist Toggle Unlisted"]
        HardDelete["DELETE /api/admin/prompts/:id Hard Delete"]
    end
    
    subgraph "OwnerAppeals"
        RelistRequest["PromptReport reason RELIST_REQUEST"]
        AdminDecision["Admin review in ReportsTable"]
    end
    
    Create --> QualityCheck
    Update --> QualityCheck
    
    QualityCheck -->|Quality Issues| AutoDelist
    
    UserReport --> ReportQueue
    ReportQueue --> AdminReview
    
    AdminReview --> FeatureToggle
    AdminReview --> ManualDelistToggle
    AdminReview --> HardDelete
    
    AutoDelist --> RelistRequest
    ManualDelistToggle --> RelistRequest
    RelistRequest --> AdminDecision
    AdminDecision --> ManualDelistToggle
```

This flow shows how prompts are checked automatically on create/update using `checkPromptQuality()` defined in [src/lib/ai/quality-check.ts:72-164](). Prompts failing quality checks are auto-delisted (hidden from discovery) with specific reasons. User reports appear in a queue for admin review, who can take actions such as feature toggling, unlisting (delisting), or hard deleting prompts via [src/app/api/prompts/[id]/unlist/route.ts:6-71]() and [src/app/api/admin/prompts/[id]/route.ts:6-72](). Delisted prompts can generate relist requests that admins can approve or deny.

Sources:
[src/app/api/prompts/[id]/unlist/route.ts:43-52](),
[src/lib/ai/quality-check.ts:72-164](),
[src/app/api/prompts/[id]/feature/route.ts:5-59]()

---

## Automated Controls and Quality

### AI-Powered Prompt Quality Checks

The core quality evaluation happens in `checkPromptQuality()` implemented in [src/lib/ai/quality-check.ts:72-164](). This function takes the prompt title, content, and optional description, and returns a `QualityCheckResult` that specifies if the prompt should be delisted, the reason, and confidence.

#### Main Steps in `checkPromptQuality`

1.  **Length Heuristics**  
    The helper `checkLength()` validates the prompt content length: minimum 50 characters and at least 10 non-empty words [src/lib/ai/quality-check.ts:28-64](). If too short, it marks for delisting immediately with reason `"TOO_SHORT"` [src/lib/ai/quality-check.ts:47-54]().

2.  **OpenAI GPT LLM Quality Check**  
    If length checks pass and an OpenAI API key is configured, the function proceeds to call the generative model (defaulting to `gpt-4o`) with a loaded prompt template from [src/lib/ai/quality-check.prompt.yml:1-43]().  
    The AI is instructed to be conservative, only flagging prompts that are clearly problematic based on English language usage, quality, and whether the text looks like a proper LLM instruction [src/lib/ai/quality-check.prompt.yml:13-35]().  
    The JSON format response includes:  
    -   `shouldDelist` (boolean)  
    -   `reason` among `NOT_ENGLISH`, `LOW_QUALITY`, or `NOT_LLM_INSTRUCTION`  
    -   `confidence` (0.0 to 1.0)  
    -   `details` string  

3.  **Confidence Threshold**  
    The implementation requires a confidence level of at least 0.85 to auto-delist prompts [src/lib/ai/quality-check.ts:129-136](). Responses below this threshold are treated as approvals to prevent false positives. On errors or parsing issues, the system defaults to approval [src/lib/ai/quality-check.ts:145-162]().

4.  **Auto-Delist Flag & Enum**  
    The system uses the `isUnlisted` flag on prompts to hide them from public discovery when quality checks fail. Delist reasons correspond to an enum type `DelistReason` (`"TOO_SHORT"`, `"NOT_ENGLISH"`, `"LOW_QUALITY"`, `"NOT_LLM_INSTRUCTION"`, `"MANUAL"`) defined in [prisma/migrations/20251217173000_add_delist_reason/migration.sql:1-5]() and referenced in [src/lib/ai/quality-check.ts:6-7]().

Sources:
[src/lib/ai/quality-check.ts:28-164](),
[src/lib/ai/quality-check.prompt.yml:1-62](),
[prisma/migrations/20251217173000_add_delist_reason/migration.sql:1-5]()

---

## Report Queue System & Relist Requests

### `PromptReport` Model

Users can submit reports flagging problematic prompts. Reports are stored in the database and tracked via status fields and reasons:

| Field      | Type          | Description                                                              |
| :--------- | :------------ | :----------------------------------------------------------------------- |
| `reason`   | `ReportReason` | Reasons like `SPAM`, `INAPPROPRIATE`, `COPYRIGHT`, `MISLEADING`, `RELIST_REQUEST`, `OTHER` |
| `status`   | `ReportStatus` | Status values: `PENDING`, `REVIEWED`, `DISMISSED`                        |
| `details`  | `string?`     | Optional additional information from reporter                            |

### Admin Review Workflow & Relist Requests

-   The reports interface displays pending reports and allows admins to update report status.  
-   Status changes invoke PATCH requests to update report states on the server.  
-   Admins can handle relisting requests by calling the API endpoint to toggle `unlist` status back to visible [src/app/api/prompts/[id]/unlist/route.ts:6-71]().  
-   Hard deletes and prompt restores are also accessible from the administrative interface [src/app/api/admin/prompts/[id]/route.ts:6-72]().

Sources:
[src/app/api/prompts/[id]/unlist/route.ts:6-71](),
[src/app/api/admin/prompts/[id]/route.ts:6-72]()

---

## Admin Moderation Tools

Administrative users have several tools available via the Admin UI and corresponding API endpoints:

| Action                   | UI Code/Function             | Server Implementation                                      |
| :----------------------- | :--------------------------- | :--------------------------------------------------------- |
| **Hard Delete Prompt**   | `handleDeletePrompt` in Admin UI | `DELETE /api/admin/prompts/[id]` [src/app/api/admin/prompts/[id]/route.ts:6-72]() |
| **Toggle Featured Status** | Button/API call in Admin UI | `POST /api/prompts/[id]/feature` for toggling `isFeatured` [src/app/api/prompts/[id]/feature/route.ts:5-59]() |
| **Toggle Unlisted Status** | Button/API call in Admin UI | `POST /api/prompts/[id]/unlist` for toggling `isUnlisted` [src/app/api/prompts/[id]/unlist/route.ts:6-71]() |

Sources:
[src/app/api/admin/prompts/[id]/route.ts:6-72](),
[src/app/api/prompts/[id]/feature/route.ts:5-59](),
[src/app/api/prompts/[id]/unlist/route.ts:6-71]()

---

## Visibility and Code Entities Mapping Diagram

This diagram connects natural language concepts of moderation with their code implementations for clarity, bridging Natural Language Space to Code Entity Space.

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        ReportQueueNL["ReportQueue"]
        QualityCheckNL["AutoQualityCheck"]
        HardDeleteNL["HardDelete"]
        RelistRequestNL["RelistRequest"]
        ToggleUnlistNL["ToggleUnlistStatus"]
        ToggleFeaturedNL["ToggleFeaturedStatus"]
    end

    subgraph "CodeEntitySpace"
        ReportTable["ReportsTableComponent"]
        CheckQualityFn["checkPromptQuality"]
        DeletePromptAPI["DELETE /api/admin/prompts/[id]"]
        UnlistPromptAPI["POST /api/prompts/[id]/unlist"]
        FeaturePromptAPI["POST /api/prompts/[id]/feature"]
    end

    ReportQueueNL --> ReportTable
    QualityCheckNL --> CheckQualityFn
    HardDeleteNL --> DeletePromptAPI
    ToggleUnlistNL --> UnlistPromptAPI
    RelistRequestNL --> ReportTable
    ToggleFeaturedNL --> FeaturePromptAPI
```

Sources:
[src/lib/ai/quality-check.ts:72-164](),
[src/app/api/admin/prompts/[id]/route.ts:6-72](),
[src/app/api/prompts/[id]/unlist/route.ts:6-71](),
[src/app/api/prompts/[id]/feature/route.ts:5-59]()

---

## Moderation Data Flow and API Endpoints Diagram

This diagram illustrates components, API routes, and database models involved in moderation tasks, also mapping system functions to code entities.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        AdminModerationUI["AdminModerationDashboard"]
    end

    subgraph "CodeEntitySpace"
        ReportsTableC["ReportsTableComponent"]
        AdminPromptsAPI["DELETE /api/admin/prompts/[id]"]
        PromptUnlistAPI["POST /api/prompts/[id]/unlist"]
        PromptFeatureAPI["POST /api/prompts/[id]/feature"]
        PromptM["PromptModel"]
        PromptReportM["PromptReportModel"]
    end

    AdminModerationUI --> ReportsTableC
    ReportsTableC -- "DELETE prompt" --> AdminPromptsAPI
    AdminPromptsAPI -- "db.prompt.delete" --> PromptM

    ReportsTableC -- "Toggle unlist" --> PromptUnlistAPI
    PromptUnlistAPI -- "isUnlisted update" --> PromptM

    ReportsTableC -- "Toggle featured" --> PromptFeatureAPI
    PromptFeatureAPI -- "isFeatured update" --> PromptM
```

Sources:
[src/app/api/admin/prompts/[id]/route.ts:6-72](),
[src/app/api/prompts/[id]/unlist/route.ts:6-71](),
[src/app/api/prompts/[id]/feature/route.ts:5-59]()

---

# Page: User Management

# User Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/reset-credits.yml](.github/workflows/reset-credits.yml)
- [prisma/migrations/20251222132600_add_user_flagged_and_unusual_activity/migration.sql](prisma/migrations/20251222132600_add_user_flagged_and_unusual_activity/migration.sql)
- [prisma/migrations/20251225000000_add_generation_credits/migration.sql](prisma/migrations/20251225000000_add_generation_credits/migration.sql)
- [src/app/api/admin/users/[id]/route.ts](src/app/api/admin/users/[id]/route.ts)
- [src/app/api/admin/users/route.ts](src/app/api/admin/users/route.ts)
- [src/app/api/cron/reset-credits/route.ts](src/app/api/cron/reset-credits/route.ts)
- [src/app/api/media-generate/route.ts](src/app/api/media-generate/route.ts)
- [src/components/admin/users-table.tsx](src/components/admin/users-table.tsx)
- [src/components/prompts/media-generator.tsx](src/components/prompts/media-generator.tsx)
- [src/lib/plugins/media-generators/index.ts](src/lib/plugins/media-generators/index.ts)

</details>



This page documents the administrative tools and technical implementation for managing user accounts in prompts.chat, including role assignment, verification, account flagging, credit management, and user-related moderation.

---

## 1. Purpose and Scope

The user management subsystem provides administrators with programmatic and UI-based controls to manage user identities, authorization tiers, resource quotas, and platform safety flags. These tools are accessible exclusively to users holding the `ADMIN` role and are implemented via Next.js API routes and React client components backed by the Prisma ORM.

Sources: [src/app/api/admin/users/route.ts:18-24](), [src/components/admin/users-table.tsx:46-63]()

---

## 2. User Role & Status Hierarchy

The system defines user capabilities through a combination of roles and status flags stored in the `User` model. The `ADMIN` role is required to access management interfaces, while flags like `verified` and `flagged` control visibility and resource access.

### Title: User State Transitions and Capabilities
```mermaid
graph TD
    subgraph NaturalLanguageSpace
    Guest["Anonymous Guest"]
    Regular["Standard User"]
    Trusted["Verified Contributor"]
    Moderator["Administrator"]
    Suspended["Flagged User"]
    end

    subgraph CodeEntitySpace
    U_Guest["session == null"]
    U_Regular["role: USER, flagged: false"]
    U_Trusted["role: USER, verified: true"]
    U_Admin["role: ADMIN"]
    U_Flagged["flagged: true"]
    end

    U_Guest -->|"OAuth / Credentials"| U_Regular
    U_Regular -->|"handleVerifyToggle()"| U_Trusted
    U_Regular -->|"handleRoleChange()"| U_Admin
    U_Regular -->|"handleFlagToggle()"| U_Flagged
    U_Flagged -->|"Admin unflag"| U_Regular

    U_Admin -->|"Access /admin"| AdminDash["AdminDashboard"]
    U_Flagged -->|"Block Generation"| MediaAPI["POST /api/media-generate"]
```

Sources: [src/components/admin/users-table.tsx:46-63](), [src/components/admin/users-table.tsx:130-181](), [src/app/api/media-generate/route.ts:67-72]()

- The `role` property distinguishes regular users (`USER`) from administrators (`ADMIN`) [src/components/admin/users-table.tsx:46-63]().
- The `verified` boolean flags trusted contributors, enabling recognition badges [src/components/admin/users-table.tsx:46-63]().
- The `flagged` boolean marks suspicious or problematic accounts, restricting capabilities [src/components/admin/users-table.tsx:46-63]().
- Admins manage all user states through the admin dashboard.
- Flagged users are blocked from AI media generation actions [src/app/api/media-generate/route.ts:67-72]().

Sources: [src/components/admin/users-table.tsx:46-63](), [src/app/api/admin/users/[id]/route.ts:21-30]()

---

## 3. Administrative Operations

### User Listing and Filtering

The `UsersTable` React component provides the primary interface for user management in the admin UI [src/components/admin/users-table.tsx:72-113](). It fetches paginated user data from the `/api/admin/users` endpoint with support for:

- Text search filtering on email, username, or display name [src/app/api/admin/users/route.ts:73-79]().
- Role-based filters (`admin`, `user`) [src/app/api/admin/users/route.ts:50-55]().
- Status filters (`verified`, `unverified`, `flagged`) [src/app/api/admin/users/route.ts:56-64]().

The `fetchUsers` function builds query parameters (`page`, `limit`, `search`, `filter`) for the backend [src/app/api/admin/users/route.ts:26-33](). Users are returned with metadata including prompt counts and timestamps [src/app/api/admin/users/route.ts:88-114]().

Sources: [src/components/admin/users-table.tsx:90-113](), [src/app/api/admin/users/route.ts:26-116]()

### Role and Verification Management

Admins can update user roles and verification status in the UI via dropdowns and toggles. These actions call the `PATCH /api/admin/users/[id]` API endpoint [src/components/admin/users-table.tsx:130-163]().

- Role changes (`USER` ↔ `ADMIN`) are validated to ensure only valid role strings are accepted [src/app/api/admin/users/[id]/route.ts:31-36]().
- Verification toggles modify the `verified` boolean attribute [src/app/api/admin/users/[id]/route.ts:38-40]().
- Protected by verifying that `session.user.role === "ADMIN"` [src/app/api/admin/users/[id]/route.ts:11-14]().

Sources: [src/components/admin/users-table.tsx:130-163](), [src/app/api/admin/users/[id]/route.ts:11-40]()

### Account Flagging

Flagging a user sets `flagged` to `true`, records the reason in `flaggedReason`, and timestamps `flaggedAt` [src/app/api/admin/users/[id]/route.ts:42-50](). If unflagged, these fields are reset to `null`.

Flagged users are suspended from certain platform functionalities:
- The media generation API (`POST /api/media-generate`) checks `user.flagged` and returns a `403 Forbidden` response if true [src/app/api/media-generate/route.ts:67-72]().

Sources: [src/components/admin/users-table.tsx:165-181](), [src/app/api/media-generate/route.ts:67-72](), [src/app/api/admin/users/[id]/route.ts:42-51]()

---

## 4. Generation Credits & Limits

To regulate resource usage, the system employs a daily credit system limiting AI media generation per user.

### Implementation Details

- **Database Schema:** Introduced in migration `20251225000000_add_generation_credits` [prisma/migrations/20251225000000_add_generation_credits/migration.sql]() with three key columns on the `users` table:
  - `dailyGenerationLimit`: Maximum daily credits (default `10`) [prisma/migrations/20251225000000_add_generation_credits/migration.sql:2]().
  - `generationCreditsRemaining`: Current available credits [prisma/migrations/20251225000000_add_generation_credits/migration.sql:3]().
  - `generationCreditsResetAt`: Timestamp of the last credit reset [prisma/migrations/20251225000000_add_generation_credits/migration.sql:4]().
- **Credit Deduction:** Successfully starting a media generation (`POST /api/media-generate`) atomically decrements `generationCreditsRemaining` by `1` [src/app/api/media-generate/route.ts:118-125]().
- **Admin Override:** Admins can adjust a user's `dailyGenerationLimit` via `PATCH /api/admin/users/[id]`, which also updates `generationCreditsRemaining` to match the new limit [src/app/api/admin/users/[id]/route.ts:53-61]().

Sources: [prisma/migrations/20251225000000_add_generation_credits/migration.sql:1-4](), [src/app/api/media-generate/route.ts:118-125](), [src/app/api/admin/users/[id]/route.ts:53-61]()

### Daily Reset Workflow

Generation credits are reset daily for all users via a scheduled cron job:
- Endpoint: `POST /api/cron/reset-credits` executes a raw SQL update setting `generationCreditsRemaining` to `dailyGenerationLimit` and updating `generationCreditsResetAt` [src/app/api/cron/reset-credits/route.ts:40-44]().
- Protected by the `CRON_SECRET` environment variable checked against the `Authorization: Bearer` header [src/app/api/cron/reset-credits/route.ts:18-36]().
- Triggered daily at midnight UTC via GitHub Actions workflow `.github/workflows/reset-credits.yml` [`.github/workflows/reset-credits.yml:1-30`]().

### Title: Daily Credit Reset Data Flow
```mermaid
sequenceDiagram
    participant GH as "GitHub Actions"
    participant CronAPI as "Cron Endpoint /api/cron/reset-credits"
    participant DB as "PostgreSQL users table"

    GH->>CronAPI: "POST with Authorization Bearer CRON_SECRET"
    CronAPI->>DB: "Update all users setting generationCreditsRemaining = dailyGenerationLimit"
    DB-->>CronAPI: "Update result (number of users updated)"
    CronAPI-->>GH: "JSON success response"
```

Sources: [.github/workflows/reset-credits.yml:1-30](), [src/app/api/cron/reset-credits/route.ts:16-60]()

---

## 5. Technical Reference: User Deletion

User deletion is a destructive operation restricted to administrators.
- Triggered in the UI via an `AlertDialog` confirming the action, calling `DELETE /api/admin/users/[id]` [src/components/admin/users-table.tsx:35-43](), [src/components/admin/users-table.tsx:183-203]().
- The API handler prevents self-deletion by verifying `id !== session.user.id` [src/app/api/admin/users/[id]/route.ts:104-106]().
- Upon success, the database record is deleted and `{ success: true }` is returned [src/app/api/admin/users/[id]/route.ts:108-112]().

Sources: [src/components/admin/users-table.tsx:35-43](), [src/components/admin/users-table.tsx:183-203](), [src/app/api/admin/users/[id]/route.ts:91-117]()

---

## 6. Bridging Natural Language to Code Entities: Overall User Admin Flow

### Title: User Administration Flow Integration
```mermaid
graph LR
    subgraph NaturalLanguageSpace
    AdminUser["Admin User"]
    RegularUser["Regular User"]
    FlaggedUser["Flagged User"]
    end

    subgraph CodeEntitySpace
    UsersTable["UsersTable Component"]
    AdminListAPI["GET /api/admin/users"]
    AdminUpdateAPI["PATCH /api/admin/users/[id]"]
    AdminDeleteAPI["DELETE /api/admin/users/[id]"]
    MediaGenAPI["POST /api/media-generate"]

    DailyResetCron["Daily Credit Reset Cron Endpoint"]
    GHWorkflow["GitHub Actions Workflow"]
    end

    AdminUser -->|Views/filters/search users| UsersTable
    UsersTable --> AdminListAPI
    AdminUser -->|Updates role/verification/flag/credits| AdminUpdateAPI
    UsersTable --> AdminUpdateAPI
    AdminUser -->|Deletes user| AdminDeleteAPI
    UsersTable --> AdminDeleteAPI

    RegularUser -->|AI Generation Request| MediaGenAPI
    FlaggedUser -->|Blocked from generation| MediaGenAPI

    GHWorkflow -->|Triggers daily reset| DailyResetCron
    DailyResetCron -->|Reset credits in DB| AdminUpdateAPI
```

Sources: [src/components/admin/users-table.tsx:1-222](), [src/app/api/admin/users/route.ts:1-134](), [src/app/api/admin/users/[id]/route.ts:1-118](), [src/app/api/media-generate/route.ts:1-141](), [src/app/api/cron/reset-credits/route.ts:1-66](), [.github/workflows/reset-credits.yml:1-30]()

---

## Summary

The user management subsystem implements robust controls for maintaining platform security, regulating AI resource consumption via daily generation limits, and executing administrative actions safely through protected API routes and structured frontend tables.

Sources: [src/components/admin/users-table.tsx:1-222](), [src/app/api/admin/users/route.ts:1-134](), [src/app/api/admin/users/[id]/route.ts:1-118]()

---

# Page: Bulk Operations & Webhooks

# Bulk Operations & Webhooks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [PROMPTS.md](PROMPTS.md)
- [README.md](README.md)
- [next.config.ts](next.config.ts)
- [prompts.csv](prompts.csv)
- [scripts/generate-contributors.sh](scripts/generate-contributors.sh)
- [scripts/rebuild-history.sh](scripts/rebuild-history.sh)
- [src/app/prompts.csv/route.ts](src/app/prompts.csv/route.ts)
- [src/app/prompts.json/route.ts](src/app/prompts.json/route.ts)
- [src/components/admin/import-prompts.tsx](src/components/admin/import-prompts.tsx)
- [src/lib/ai/embeddings.ts](src/lib/ai/embeddings.ts)
- [src/lib/ai/query-translator.prompt.yml](src/lib/ai/query-translator.prompt.yml)
- [tests/generate-contributors-format.test.js](tests/generate-contributors-format.test.js)

</details>



This page provides full technical documentation for the bulk operations available within the administrative interface of `prompts.chat`. It details how the system handles prompt embeddings, slug generation, related prompts discovery, CSV import/export synchronization, contributor attribution scripts, and administrative webhook configuration and delivery.

---

## Administrative Interface for Bulk Operations

The administration panel relies on frontend controllers to orchestrate batch tasks against backend routes. The `PromptsManagement` component acts as the primary orchestrator for bulk prompt updates `[src/components/admin/prompts-management.tsx:41-46]()`.

### Implementation & State Control

- **Progress Tracking:** Operations use React state hooks (`useState`) to manage tracking metrics, tracking success counts, failure counts, and execution states via a typed progress interface `[src/components/admin/prompts-management.tsx:41-46]()`.
- **Branding Protection:** Administrative mutations are guarded by configuration flags like `useCloneBranding` to prevent unauthorized alteration in white-labeled deployments `[src/components/admin/prompts-management.tsx:103-103]()`.
- **Feedback & Notifications:** Toast notifications via `sonner` relay feedback regarding task completion, success rates, and caught exceptions `[src/components/admin/prompts-management.tsx:111-117]()`.
- **Dashboard Metrics:** The parent `AdminPage` aggregates metadata deficiencies (such as prompts lacking slugs or embeddings) to notify administrators when bulk actions are required `[src/app/admin/page.tsx:41-75]()`.

Sources: `[src/components/admin/prompts-management.tsx:41-128]`, `[src/app/admin/page.tsx:41-75]()`

---

## CSV Import & Export System

The platform maintains synchronization between PostgreSQL and the repository-level `prompts.csv` file.

### CSV Export Mechanism (`/prompts.csv`)

- Exports active, public, and listed prompts. Unlisted and soft-deleted records are automatically filtered out `[src/app/prompts.csv/route.ts:31-37]()`.
- Escaping follows RFC 4180 rules, handling embedded quotes, commas, and multiline values via `escapeCSVField()` `[src/app/prompts.csv/route.ts:5-15]()`.
- Contributor identifiers are resolved deterministically using `getUserIdentifier()`, prioritizing GitHub usernames, followed by unclaimed proxy handles (`@unclaimed.prompts.chat`), and email fallbacks `[src/app/prompts.csv/route.ts:18-25]`, `[src/app/prompts.csv/route.ts:74-80]()`.

#### CSV Export Flow (Natural Language to Code Entity Bridge)

```mermaid
graph TD
    subgraph "Natural Language Space"
        AdminRequest["Admin triggers CSV export"]
        FilterPrompts["Filter public, active, listed prompts"]
        CsvFile["Download prompts.csv"]
    end

    subgraph "Code Entity Space"
        Route["GET_/prompts.csv"]
        DB["db.prompt.findMany"]
        UserIdFn["getUserIdentifier"]
        Escaper["escapeCSVField"]
    end

    AdminRequest --> Route
    Route --> DB
    DB --> UserIdFn
    UserIdFn --> Escaper
    Escaper --> CsvFile
```
Sources: `[src/app/prompts.csv/route.ts:1-95]()`

### CSV Import (`/api/admin/import-prompts`)

- Reads and parses CSV files from the project root or uploaded buffers, handling multiline quoted records and unescaping sequences `[src/app/api/admin/import-prompts/route.ts:15-90]()`.
- Validates uniqueness by prompt title to prevent duplicate entries.
- Unclaimed authors and contributors are automatically upserted as placeholder records utilizing `@unclaimed.prompts.chat` domains `[src/app/api/admin/import-prompts/route.ts:136-172]()`.
- Coding prompts are automatically linked or upserted into the "Coding" category `[src/app/api/admin/import-prompts/route.ts:190-209]()`.

Sources: `[src/app/api/admin/import-prompts/route.ts:1-209]`, `[src/components/admin/import-prompts.tsx:35-220]()`

---

## AI & Metadata Bulk Operations

Bulk metadata enrichment operations scale prompt indexing for vector search and graph connectivity.

### Embedding Generation (`generateAllEmbeddings`)

- **Purpose:** Vectorizes prompt content for semantic search capabilities.
- **Data Pipeline:** `generateAllEmbeddings()` queries public, active prompts missing embedding fields (`embedding: Prisma.DbNull`), combines title, description, and raw content, and computes vector representations `[src/lib/ai/embeddings.ts:124-131]()`.
- **Provider Integration:** Calls OpenAI's embedding API (`embeddings.create`) with the configured `EMBEDDING_MODEL` (`text-embedding-3-small`) `[src/lib/ai/embeddings.ts:26-76]()`.
- **Rate Limiting:** Enforces an asynchronous `delay()` of 1,000ms between records to avoid provider rate exhaustion `[src/lib/ai/embeddings.ts:111-157]()`.
- **Feature Flag Guard:** Aborts execution unless `config.features.aiSearch` is explicitly enabled `[src/lib/ai/embeddings.ts:120-123]()`.

### Related Prompts & Slug Generation

- **Related Prompts Discovery:** Computes cosine similarity matrices over prompt embedding vectors to populate `PromptConnection` relations.
- **Slug Generation:** Bulk generates URL-safe slugs for records where `slug = null` via the `handleGenerateSlugs` administrative handler `[src/components/admin/prompts-management.tsx:107-107]()`.

Sources: `[src/lib/ai/embeddings.ts:70-159]`, `[src/components/admin/prompts-management.tsx:243-320]`, `[src/app/admin/page.tsx:41-75]()`

---

## Webhook Configuration & Delivery

External services receive real-time notifications about prompt lifecycle transitions via configurable webhook endpoints.

### Supported Events & CRUD APIs

- **Events:** `PROMPT_CREATED`, `PROMPT_UPDATED`, `PROMPT_DELETED`.
- **Endpoints:**
  - List / Create: `GET` and `POST` on `/api/admin/webhooks` `[src/app/api/admin/webhooks/route.ts:80-135]()`
  - Get / Update / Delete: `GET`, `PATCH`, `DELETE` on `/api/admin/webhooks/[id]` `[src/app/api/admin/webhooks/[id]/route.ts:1-178]()`
- **Security & Validation:** Endpoints require administrator authorization via NextAuth session checks. URLs undergo SSRF validation via `isPrivateUrl()` to reject internal or private network targets `[src/lib/webhook.ts:159-214]()`.
- **Payload Templates:** Supports template substitutions like `{{PROMPT_TITLE}}`, `{{AUTHOR_USERNAME}}`, and `{{CHATGPT_URL}}` `[src/lib/webhook.ts:25-41]()`.

#### Webhook Management Flow (Natural Language to Code Entity Bridge)

```mermaid
graph TD
    subgraph "Natural Language Space"
        AdminUI["Admin Dashboard Interface"]
        ManageWebhooks["Configure and test webhook subscriptions"]
        ExternalEndpoint["External Consumer URL"]
    end

    subgraph "Code Entity Space"
        API_POST["POST_/api/admin/webhooks"]
        API_PATCH["PATCH_/api/admin/webhooks/[id]"]
        AuthCheck["auth() admin check"]
        ValFn["validateWebhook()"]
        SSRF["isPrivateUrl()"]
        DB_Store["db.webhookConfig"]
    end

    AdminUI --> ManageWebhooks
    ManageWebhooks --> API_POST
    ManageWebhooks --> API_PATCH
    API_POST --> AuthCheck
    API_PATCH --> AuthCheck
    AuthCheck --> ValFn
    ValFn --> SSRF
    SSRF -->|Passes| DB_Store
    DB_Store --> ExternalEndpoint
```
Sources: `[src/app/api/admin/webhooks/route.ts:1-135]`, `[src/app/api/admin/webhooks/[id]/route.ts:1-178]`, `[src/lib/webhook.ts:1-241]()`

---

## Contributor Attribution Sync

Git history ownership is maintained automatically via the shell script `scripts/generate-contributors.sh`.

### Attribution Workflow

1. **Remote Fetching:** Downloads `prompts.csv` from the live site endpoint `[scripts/generate-contributors.sh:15-19]()`.
2. **Diff Processing:** Runs an internal Python subprocess to isolate new or altered prompt records `[scripts/generate-contributors.sh:38-41]()`.
3. **Email Formatting:** `make_email()` maps contributor identifiers to standard git-compatible pseudo-emails (`@users.noreply.github.com`) `[scripts/generate-contributors.sh:102-106]()`.
4. **Commit Generation:** Stages changes and invokes `git commit`, setting primary authors and appending secondary contributors via `Co-authored-by` commit message trailers `[scripts/generate-contributors.sh:108-130]()`.
5. **Markdown Sync:** Regenerates formatted contributor links and block elements inside `PROMPTS.md` `[scripts/generate-contributors.sh:155-172]()`.

Sources: `[scripts/generate-contributors.sh:1-171]`, `[tests/generate-contributors-format.test.js:1-26]()`

---

## Summary Diagram: Bulk Operations & Webhook Integration

```mermaid
graph TD
    subgraph "Natural Language Space"
        Admin["Administrator"]
        Webhooks["External Subscribers"]
    end

    subgraph "Code Entity Space"
        AdminUI["Admin Dashboard"]
        ImportAPI["POST_/api/admin/import-prompts"]
        ExportAPI["GET_/prompts.csv"]
        EmbedGen["generateAllEmbeddings()"]
        WebhookAPI["WebhookConfig_CRUD"]
        Script["scripts/generate-contributors.sh"]
    end

    subgraph "Database Store"
        DBPrompt["db.prompt"]
        DBWebhook["db.webhookConfig"]
        DBUser["db.user"]
    end

    Admin --> AdminUI
    AdminUI --> ImportAPI --> DBPrompt & DBUser
    AdminUI --> ExportAPI --> DBPrompt
    AdminUI --> EmbedGen --> DBPrompt
    AdminUI --> WebhookAPI --> DBWebhook
    DBPrompt --> Script
    DBPrompt --> WebhookAPI --> Webhooks
```
Sources: `[src/components/admin/prompts-management.tsx:41-128]`, `[src/app/api/admin/import-prompts/route.ts:1-209]`, `[src/app/prompts.csv/route.ts:1-95]`

---

## References

- Bulk Operations UI and logic: `[src/components/admin/prompts-management.tsx:41-128]()`
- CSV Import backend: `[src/app/api/admin/import-prompts/route.ts:1-209]()`
- CSV Export backend: `[src/app/prompts.csv/route.ts:1-95]()`
- Embeddings generation library: `[src/lib/ai/embeddings.ts:70-159]()`
- Admin dashboard metrics: `[src/app/admin/page.tsx:41-75]()`
- Webhook management API: `[src/app/api/admin/webhooks/route.ts:1-135]()`, `[src/app/api/admin/webhooks/[id]/route.ts:1-178]()`
- Webhook utility and validation: `[src/lib/webhook.ts:1-241]()`
- Contributor attribution script: `[scripts/generate-contributors.sh:1-171]()`

---

# Page: Developer Tools & APIs

# Developer Tools & APIs

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SELF-HOSTING.md](SELF-HOSTING.md)
- [context7.json](context7.json)
- [packages/prompts.chat/README.md](packages/prompts.chat/README.md)
- [public/deepwiki.svg](public/deepwiki.svg)
- [src/app/docs/api/page.tsx](src/app/docs/api/page.tsx)
- [src/app/docs/self-hosting/page.tsx](src/app/docs/self-hosting/page.tsx)
- [src/app/privacy/page.tsx](src/app/privacy/page.tsx)
- [src/app/terms/page.tsx](src/app/terms/page.tsx)
- [src/components/layout/footer.tsx](src/components/layout/footer.tsx)

</details>



This page serves as the parent directory for developer-facing tools, APIs, and integration layers provided by prompts.chat. The platform offers a Model Context Protocol (MCP) server for direct IDE integration, an API key authentication pipeline, a CLI tool for terminal-based prompt management, browser extensions, and an in-browser Typed-Prompts IDE with embedding utilities.

As a parent page, this document provides a high-level overview of each developer sub-system. For implementation details, configuration guides, and parameter references, please navigate to the corresponding child sections below.

Sources: [src/app/docs/api/page.tsx:31-77]()

---

## MCP Server Integration

prompts.chat implements the Model Context Protocol (MCP) via a unified API endpoint at `/api/mcp` [src/app/docs/api/page.tsx:73-74](). This server exposes the prompt database as native MCP resources and tools. The integration allows IDEs and assistant clients (e.g., Claude Code, Cursor IDE) to seamlessly list and retrieve prompts and skills. The same endpoint works for both MCP clients and traditional REST-style requests [src/app/docs/api/page.tsx:68-70]().

For detailed IDE client configuration instructions and MCP usage, see [MCP Server Integration](#11.1).

Sources: [src/app/docs/api/page.tsx:31-77]()

---

## MCP Tools Reference

The MCP server registers an extensive set of tools for prompt, skill, bot, and team management. These tools are defined within the `src/lib/mcp` directory and include handlers for searching prompts, retrieving details, improving prompts via AI, and managing multi-file agent skills.

| Tool Category | Description |
| :------------ | :------------------------------------------------ |
| Prompt Tools  | `search_prompts`, `get_prompt`, `save_prompt`     |
| Skill Tools   | `search_skills`, `get_skill`, `save_skill`        |
| Bot Tools     | `search_bots`, `get_bot`, `save_bot`              |
| Team Tools    | `list_teams`, `get_team`, `save_team`             |

For a full tool reference, usage details, and APIs, see [MCP Tools Reference](#11.2).

---

## API Keys & Authentication

Authentication for write operations and private prompt access is handled via API keys. These keys start with the prefix `pchat_` [src/app/docs/api/page.tsx:111]() and can be generated from the user settings page [src/app/docs/api/page.tsx:107-109](). Clients provide their API key via the `PROMPTS_API_KEY` header, `Authorization: Bearer` header, `x-api-key` header, or `?api_key=` query parameter [src/app/docs/api/page.tsx:116-120]().

For guidance on API key lifecycle, generation, and tiered access controls, see [API Keys & Authentication](#11.3).

Sources: [src/app/docs/api/page.tsx:89-153]()

---

## CLI Tool

An interactive command-line interface is provided via `npx prompts.chat` [packages/prompts.chat/README.md:44](). This tool enables terminal-based browsing and searching of prompts [packages/prompts.chat/README.md:41-46](), as well as scaffolding new prompts.chat deployments using the `new` command [packages/prompts.chat/README.md:28-32]().

For detailed CLI commands and usage examples, see [CLI Tool](#11.4).

Sources: [packages/prompts.chat/README.md:28-59]()

---

## Browser Extensions & Desktop Apps

Prompts.chat integrates with external clients using browser extensions (Chrome, Firefox), Raycast extension commands, and desktop applications. These integrations often involve caching mechanisms and support deep linking to run prompts or open prompt editor UIs.

For extension setup, command structures, and client connectivity, see [Browser Extensions & Desktop Apps](#11.5).

---

## Typed-Prompts IDE & Embeds

The platform includes an in-browser Typed-Prompts IDE, accessible via `/typed-prompts-editor` [packages/prompts.chat/README.md:3](). This IDE allows interactive prompt authoring with live token counting, multi-file agent skill editing, and embed creation via the `/embed` page. The underlying `prompts.chat` package provides a comprehensive developer toolkit for building, validating, and parsing AI prompts with type-safe APIs [packages/prompts.chat/README.md:1-2]().

For full Typed-Prompts IDE features, tokenizer logic, and embeds documentation, see [Typed-Prompts IDE & Embeds](#11.6).

Sources: [packages/prompts.chat/README.md:1-3]()

---

# Bridging Natural Language Space to Code Entity Space

## MCP Server Architecture

```mermaid
graph TD
  A["ClientIDEOrAssistant"] --> B["ApiMcpRouteNode[\"POST /api/mcp\"]"]
  B --> C["McpServerInstance[\"src/app/api/mcp/route.ts\"]"]
  C --> D["ToolRegistrationEngine[\"src/lib/mcp/server.ts\"]"]
  D --> D1["PromptTools[\"tools/search_prompts\"]"]
  D --> D2["SkillTools[\"tools/get_skill\"]"]
  D --> D3["BotTools[\"tools/save_bot\"]"]
  D --> D4["TeamTools[\"tools/list_teams\"]"]
  D1 --> E["PrismaDatabaseClient[\"PrismaClient\"]"]
  D2 --> E
  D3 --> E
  D4 --> E
```
Sources: [src/app/docs/api/page.tsx:73-74]()

## CLI Tool Interaction Flow

```mermaid
graph TD
  A["TerminalUser"] --> B["CliBinaryExecution[\"npx prompts.chat\"]"]
  B --> C["CliEntryPoint[\"packages/prompts.chat/cli.ts\"]"]
  C --> C1{"CommandSelector"}
  C1 -- "new" --> D["ScaffoldingModule[\"packages/prompts.chat/src/commands/new.ts\"]"]
  C1 -- "browse" --> E["InteractiveBrowser[\"packages/prompts.chat/src/commands/browse.ts\"]"]
  E --> F["RestApiEndpoints[\"/api/prompts\"]"]
  D --> G["GitCloneAndSetupWizard"]
```
Sources: [packages/prompts.chat/README.md:28-46]()

For comprehensive technical details, usage instructions, and API references, navigate to the linked child pages in this section.

---

# Page: MCP Server Integration

# MCP Server Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [CLAUDE-PLUGIN.md](CLAUDE-PLUGIN.md)
- [plugins/claude/prompts.chat/.claude-plugin/plugin.json](plugins/claude/prompts.chat/.claude-plugin/plugin.json)
- [plugins/claude/prompts.chat/.mcp.json](plugins/claude/prompts.chat/.mcp.json)
- [plugins/claude/prompts.chat/agents/prompt-manager.md](plugins/claude/prompts.chat/agents/prompt-manager.md)
- [plugins/claude/prompts.chat/agents/skill-manager.md](plugins/claude/prompts.chat/agents/skill-manager.md)
- [plugins/claude/prompts.chat/commands/prompts.md](plugins/claude/prompts.chat/commands/prompts.md)
- [plugins/claude/prompts.chat/commands/skills.md](plugins/claude/prompts.chat/commands/skills.md)
- [plugins/claude/prompts.chat/skills/prompt-lookup/SKILL.md](plugins/claude/prompts.chat/skills/prompt-lookup/SKILL.md)
- [plugins/claude/prompts.chat/skills/skill-lookup/SKILL.md](plugins/claude/prompts.chat/skills/skill-lookup/SKILL.md)
- [src/components/comments/comment-form.tsx](src/components/comments/comment-form.tsx)
- [src/components/mcp/mcp-config-tabs.tsx](src/components/mcp/mcp-config-tabs.tsx)
- [src/components/mcp/mcp-server-popup.tsx](src/components/mcp/mcp-server-popup.tsx)
- [src/components/prompts/add-to-collection-button.tsx](src/components/prompts/add-to-collection-button.tsx)
- [src/components/prompts/translate-button.tsx](src/components/prompts/translate-button.tsx)
- [src/hooks/use-mobile.ts](src/hooks/use-mobile.ts)

</details>



This page documents the Model Context Protocol (MCP) server implementation at `src/app/api/mcp/route.ts`, core tool registrations (`src/lib/mcp/tools/`), authentication systems, IDE client configuration generators, and the Claude Code plugin marketplace integration.

---

## MCP Server Routing & API Implementation

The MCP server is hosted as a Next.js App Router API route at `src/app/api/mcp/route.ts`. It leverages the `@modelcontextprotocol/sdk/server/mcp.js` package to manage JSON-RPC message exchange over HTTP/SSE transports [src/__tests__/api/mcp-handler.test.ts:34-40]().

- `POST` handlers receive JSON-RPC payloads, parse requests, run rate limiting checks, and route method calls to registered tools or prompts [src/__tests__/api/mcp-handler.test.ts:101-146]().
- `GET` requests without an active event stream return `405 Method Not Allowed` with `cache-control: no-store` [src/__tests__/api/mcp-handler.test.ts:67-78]().
- `DELETE` requests terminate sessions gracefully with a `204 No Content` status [src/__tests__/api/mcp-handler.test.ts:80-84]().

**MCP Server Request Routing Diagram**

```mermaid
graph TB
    subgraph "Request Entry"
    IncomingReq["HTTP Request POST /api/mcp"] --> RouteHandler["src/app/api/mcp/route.ts"]
    end

    subgraph "Validation & Rate Limiting"
    RouteHandler --> CheckEnabled["Verify features.mcp"]
    CheckEnabled --> CheckSize["Check Body Size < 1MB"]
    CheckSize --> Limiters["mcpGeneralLimiter / mcpToolCallLimiter"]
    end

    subgraph "Server Execution"
    Limiters --> Auth["authenticateApiKey()"]
    Auth --> McpServerInstance["createMcpServer()"]
    McpServerInstance --> Dispatch["Dispatch JSON-RPC Method"]
    end
```
Sources: [src/__tests__/api/mcp-handler.test.ts:30-177]()

---

## Authentication, Authorization & Rate Limiting

### API Key Authentication and Visibility

- MCP write operations and private prompt access require a `pchat_*` format API key [src/__tests__/api/mcp-handler.test.ts:27-28]().
- Authentication headers and query parameters supported include `PROMPTS_API_KEY`, `prompts-api-key`, `Authorization: Bearer`, and `?api_key=` [src/__tests__/api/mcp-handler.test.ts:162-167]().
- Cached user lookup via `db.user.findUnique` retrieves user entity records (`id`, `username`, `role`, `mcpPromptsPublicByDefault`) [src/__tests__/api/mcp-handler.test.ts:28]().

### Rate Limiting Layers

The system protects against resource exhaustion using distinct rate limiters defined in `src/lib/rate-limit.ts`:
- `mcpGeneralLimiter`: General POST request throttling [src/__tests__/api/mcp-handler.test.ts:61-64]().
- `mcpToolCallLimiter`: Tool execution throttling (`tools/call`) [src/__tests__/api/mcp-handler.test.ts:61-64]().
- `mcpWriteToolLimiter`: Mutation operations (`save_prompt`, `save_bot`, `save_team`) [src/__tests__/api/mcp-handler.test.ts:61-64]().
- `mcpAiToolLimiter`: AI-powered utilities (`improve_prompt`, semantic search) [src/__tests__/api/mcp-handler.test.ts:61-64]().

**Authentication and Rate Limiting Data Flow Diagram**

```mermaid
graph LR
    Req["API Request"] --> KeyExtract["Extract API Key Header"]
    KeyExtract --> RateCheck["Check RateLimiters"]
    RateCheck -- Allowed --> DBLookup["Query db.user.findUnique"]
    DBLookup --> Ctx["Populate McpContext"]
    Ctx --> Permissions["Enforce Listing / Direct Visibility"]
```
Sources: [src/__tests__/api/mcp-handler.test.ts:27-177]()

---

## Tool Registration & Shared Schemas

The MCP server registers modular toolkits covering prompts, skills, bots, and bot teams [src/__tests__/api/mcp-handler.test.ts:126-145]():

| Tool Category | Key Functions / Files | Description |
|---|---|---|
| **Prompt Tools** | `src/lib/mcp/tools/prompts.ts` | `search_prompts`, `get_prompt`, `save_prompt`, `improve_prompt` [src/__tests__/api/mcp-handler.test.ts:126-130]() |
| **Skill Tools** | `src/lib/mcp/tools/skills.ts` | `search_skills`, `get_skill`, `save_skill`, `add_file_to_skill`, `update_skill_file`, `remove_file_from_skill` [src/__tests__/api/mcp-handler.test.ts:131-136]() |
| **Bot Tools** | `src/lib/mcp/tools/bots.ts` | `search_bots`, `get_bot`, `save_bot`, `list_my_bots`, `get_my_bot` [src/__tests__/api/mcp-handler.test.ts:137-141]() |
| **Team Tools** | `src/lib/mcp/tools/teams.ts` | `list_teams`, `get_team`, `save_team` [src/__tests__/api/mcp-handler.test.ts:142-145]() |

Shared input/output schemas (e.g., `limitInput`, `cursorInput`, `taxonomyOutput`, `botSummaryOutput`) are centralized in `src/lib/mcp/schemas.ts` and ensure strict Zod runtime validation across all MCP tool responses [src/lib/mcp/schemas.ts:1-130]().

Sources: [src/__tests__/api/mcp-handler.test.ts:126-145](), [src/lib/mcp/schemas.ts:1-130]()

---

## Claude Code Plugin Marketplace & Natural Language Mapping

The repository integrates with Claude Code and other agent runners via plugin definitions located under `plugins/claude/prompts.chat/` and `.claude-plugin/marketplace.json`. The official prompts.chat plugin for Claude Code provides commands, agents, and auto-activating skills [CLAUDE-PLUGIN.md:1-18]().

**Installation for Claude Code:**
Users can add the prompts.chat marketplace and install the plugin using Claude Code commands:
```
/plugin marketplace add f/prompts.chat
/plugin install prompts.chat@prompts.chat
```
[CLAUDE-PLUGIN.md:9-18]()

**Plugin Structure:**
The plugin is structured as follows:
```
plugins/claude/prompts.chat/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── .mcp.json                 # MCP server configuration
├── commands/
│   ├── prompts.md           # /prompts.chat:prompts command
│   └── skills.md            # /prompts.chat:skills command
├── agents/
│   ├── prompt-manager.md    # Prompt management agent
│   └── skill-manager.md     # Skill management agent
└── skills/
    ├── prompt-lookup/
    │   └── SKILL.md         # Prompt discovery skill
    └── skill-lookup/
        └── SKILL.md         # Skill discovery skill
```
[CLAUDE-PLUGIN.md:165-181]()

**Natural Language to Code Entity Space Mapping Diagram (Plugins & Agents)**

```mermaid
graph TB
    subgraph "Natural Language Space"
    NLPrompt["User asks: 'Find a bot for inbox triage'"]
    NLSpeak["User asks: 'Get research crew team'"]
    NLSearchSkill["User asks: 'Search for code review skills'"]
    end

    subgraph "Plugin Entity Space"
    PromptCommand["plugins/claude/prompts.chat/commands/prompts.md"]
    SkillLookup["plugins/claude/prompts.chat/skills/skill-lookup/SKILL.md"]
    PromptManagerAgent["plugins/claude/prompts.chat/agents/prompt-manager.md"]
    SkillManagerAgent["plugins/claude/prompts.chat/agents/skill-manager.md"]
    end

    subgraph "Code Entity Space"
    SearchBots["search_bots() in src/lib/mcp/tools/bots.ts"]
    GetTeam["get_team() in src/lib/mcp/tools/teams.ts"]
    SearchSkills["search_skills() in src/lib/mcp/tools/skills.ts"]
    DbQuery["db.prompt.findMany() & db.botTeam.findUnique() & db.skill.findMany()"]
    end

    NLPrompt --> PromptCommand
    NLSpeak --> PromptManagerAgent
    NLSearchSkill --> SkillLookup

    PromptCommand --> SearchBots
    PromptManagerAgent --> GetTeam
    SkillLookup --> SearchSkills
    SkillManagerAgent --> SearchSkills

    SearchBots --> DbQuery
    GetTeam --> DbQuery
    SearchSkills --> DbQuery
```
Sources: [src/lib/mcp/tools/bots.ts:76-156](), [src/lib/mcp/tools/teams.ts:78-173](), [plugins/claude/prompts.chat/skills/skill-lookup/SKILL.md:1-76](), [plugins/claude/prompts.chat/agents/prompt-manager.md:1-67](), [CLAUDE-PLUGIN.md:1-181]()

---

## IDE Client Configurations & Transport Modes

Users can configure their IDE clients (Cursor, Claude Code, VS Code, Codex, Windsurf, Gemini) through interactive UI popups (`McpServerPopup` and `McpConfigTabs`) [src/components/mcp/mcp-config-tabs.tsx:46-182](), [src/components/mcp/mcp-server-popup.tsx:51-184]().

- **Remote Mode:** Configures the client to connect directly via HTTP/SSE transport to `/api/mcp`, passing `PROMPTS_API_KEY` in headers [src/components/mcp/mcp-config-tabs.tsx:51-60]().
- **Local Mode:** Configures the client to execute the local stdio runner package (`npx -y @fkadev/prompts.chat-mcp`) with environment variable bindings [src/components/mcp/mcp-config-tabs.tsx:62-73]().

**Client Configuration Flow Diagram (Natural Language UI to Code Execution)**

```mermaid
graph TB
    subgraph "Natural Language Space"
    UIModal["McpServerPopup component"] --> SelectClient["Select IDE Client"]
    SelectClient --> SelectMode["Toggle Remote vs Local"]
    end

    subgraph "Code Entity Space"
    SelectMode --> ConfigBuilder["getMcpClientConfig() in src/lib/mcp/client-config.ts"]
    ConfigBuilder --> RemoteJSON["Remote JSON/CLI Config with Header"]
    ConfigBuilder --> LocalJSON["Local stdio npx Config with Env"]
    end
```
Sources: [src/components/mcp/mcp-config-tabs.tsx:46-182](), [src/components/mcp/mcp-server-popup.tsx:51-184]()

---

# Page: MCP Tools Reference

# MCP Tools Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/__tests__/api/bot-teams.test.ts](src/__tests__/api/bot-teams.test.ts)
- [src/__tests__/api/mcp-bots.test.ts](src/__tests__/api/mcp-bots.test.ts)
- [src/__tests__/api/mcp-handler.test.ts](src/__tests__/api/mcp-handler.test.ts)
- [src/__tests__/api/mcp-server.test.ts](src/__tests__/api/mcp-server.test.ts)
- [src/__tests__/api/mcp-teams.test.ts](src/__tests__/api/mcp-teams.test.ts)
- [src/__tests__/lib/bot-upsert.test.ts](src/__tests__/lib/bot-upsert.test.ts)
- [src/app/api/bots/teams/route.ts](src/app/api/bots/teams/route.ts)
- [src/lib/bots/teams.ts](src/lib/bots/teams.ts)
- [src/lib/bots/upsert.ts](src/lib/bots/upsert.ts)
- [src/lib/mcp/resources.ts](src/lib/mcp/resources.ts)
- [src/lib/mcp/schemas.ts](src/lib/mcp/schemas.ts)
- [src/lib/mcp/shared.ts](src/lib/mcp/shared.ts)
- [src/lib/mcp/tools/bots.ts](src/lib/mcp/tools/bots.ts)
- [src/lib/mcp/tools/prompts.ts](src/lib/mcp/tools/prompts.ts)
- [src/lib/mcp/tools/skills.ts](src/lib/mcp/tools/skills.ts)
- [src/lib/mcp/tools/teams.ts](src/lib/mcp/tools/teams.ts)

</details>



## Purpose & Scope

This page details all Model Context Protocol (MCP) tools exposed by the `prompts.chat` MCP API endpoint located at [src/__tests__/api/mcp-handler.test.ts:1-100]() and defined across `src/lib/mcp/tools/`. These tools allow AI assistants, IDE integrations, and automated workflows to programmatically search, retrieve, create, and manage AI prompts, multi-file agent skills, specialized platform bots, and multi-bot teams.

Sources: [src/__tests__/api/mcp-handler.test.ts:1-100](), [src/lib/mcp/tools/bots.ts:1-76]()

---

## Shared Schemas and Utility Functions (`src/lib/mcp`)

The MCP layer relies on shared validation schemas and helper functions under `src/lib/mcp/` to standardize input pagination, secure cursor decoding, tag/category resolution, and resource linking.

- **Cursors & Pagination**: `cursorInput`, `decodeCursor`, `encodeCursor`, and `nextCursor` handle base64url-encoded offset pagination safely [src/lib/mcp/schemas.ts:5-46](). An invalid cursor throws a structured `ToolError` with code `invalid_cursor` [src/__tests__/api/mcp-server.test.ts:71-77]().
- **Taxonomy Resolution**: `resolveTagIds()` matches names/slugs case-insensitively against existing database records without auto-creating tags (which is restricted to admins), returning unknown tags in `unknownTags` [src/lib/mcp/shared.ts:63-103](). `resolveCategoryId()` maps category slugs to Prisma IDs [src/lib/mcp/shared.ts:105-111]().
- **Resource Linking**: `resourceLink()` and `resourceUri()` construct `prompts-chat://` resource URIs for clients supporting MCP resources [src/lib/mcp/shared.ts:9-28]().

Diagram: Taxonomy and Pagination Data Flow
```mermaid
graph TB
    ClientInput["ClientInput"]
    CursorDecode["decodeCursor()"]
    TagResolve["resolveTagIds()"]
    CatResolve["resolveCategoryId()"]
    PrismaDB["db.prompt"]

    ClientInput --> CursorDecode
    ClientInput --> TagResolve
    ClientInput --> CatResolve
    TagResolve --> PrismaDB
    CatResolve --> PrismaDB
```

Sources: [src/lib/mcp/schemas.ts:1-50](), [src/lib/mcp/shared.ts:1-111](), [src/__tests__/api/mcp-server.test.ts:71-77]()

---

## Prompt Tools Reference

Prompt tools handle searching, retrieving, creating, and enhancing non-bot prompts (text, structured, image, audio, video) [src/lib/mcp/tools/prompts.ts:33-44]().

### `search_prompts`
- **Description**: Searches public prompts and the caller's private prompts using case-insensitive keyword matching across titles, descriptions, and content [src/lib/mcp/tools/prompts.ts:50-53]().
- **Parameters**: `query` (string), `limit` (number, default 10, max 50), `cursor` (string), `type` (enum), `category` (string), `tag` (string) [src/lib/mcp/tools/prompts.ts:55-61]().
- **Returns**: Summaries with `contentPreview`, author info, votes, and resource links [src/lib/mcp/tools/prompts.ts:63-68]().

### `get_prompt`
- **Description**: Retrieves a specific prompt by ID, extracting template variables formatted as `${name}` or `${name:default}` [src/lib/mcp/tools/prompts.ts:135-138]().
- **Parameters**: `id` (string), `variables` (record of string values) [src/lib/mcp/tools/prompts.ts:140-146]().
- **Behavior**: If `variables` are passed, template strings are filled. If required variables are missing, `missingVariables` is returned [src/__tests__/api/mcp-server.test.ts:94-110]().

### `save_prompt`
- **Description**: Creates or updates a non-bot prompt record for the authenticated user via the underlying prompt write pipeline.
- **Parameters**: `title`, `content`, `type`, `isPrivate`, `category`, `tags`.

### `improve_prompt`
- **Description**: Leverages OpenAI integration to improve prompt phrasing and structure when the prompt enhancer feature flag is enabled [src/__tests__/api/mcp-server.test.ts:82-101]().

Sources: [src/lib/mcp/tools/prompts.ts:1-180](), [src/__tests__/api/mcp-server.test.ts:79-124]()

---

## Skill Management Tools Reference

Multi-file agent skills store multiple files inside a single database record using ASCII control character delimiters `\x1F` (Unit Separator) and `\x1E` (Record Separator) [src/lib/skill-files.ts:1-28]().

### `search_skills` & `get_skill`
- `search_skills`: Discovers reusable AI agent capabilities filtered by category, tag, or keywords [src/lib/mcp/tools/skills.ts:95-106]().
- `get_skill`: Retrieves a skill by ID along with all parsed files (`SKILL.md`, reference docs, scripts) via `parseSkillFiles()` [src/lib/skill-files.ts:52-82](), [src/lib/mcp/tools/skills.ts:181-188]().

### `save_skill`, `add_file_to_skill`, `update_skill_file`, `remove_file_from_skill`
- Manage file contents within a skill record.
- Deletion of `SKILL.md` is strictly prohibited to preserve skill integrity [src/lib/skill-files.ts:30](). Filenames are sanitized against path traversal [src/lib/skill-files.ts:201-211]().

Sources: [src/lib/mcp/tools/skills.ts:1-198](), [src/lib/skill-files.ts:1-211]()

---

## Bot Tools Reference

Bot tools (`src/lib/mcp/tools/bots.ts`) manage ready-made agents with instructions, routines, skills, and connectors for platforms like OpenCLAW, Hermes, and Grok.

Diagram: Bot Tools Natural Language to Code Entity Space
```mermaid
graph TB
    NaturalLanguageQuery["NaturalLanguageQuery"]
    
    subgraph ToolEntitySpace["ToolEntitySpace"]
        SearchBots["search_bots"]
        GetBot["get_bot"]
        SaveBot["save_bot"]
        ListMyBots["list_my_bots"]
        GetMyBot["get_my_bot"]
    end

    subgraph ServiceLayer["ServiceLayer"]
        ListBotsFn["listBots()"]
        SemanticSearchFn["semanticSearch()"]
        UpsertOwnBotFn["upsertOwnBot()"]
        FindVisibleBotFn["findVisibleBot()"]
        ListBotsByAuthorFn["listBotsByAuthor()"]
        FindOwnBotFn["findOwnBot()"]
        PrismaPrompt["db.prompt"]
    end

    NaturalLanguageQuery --> SearchBots
    NaturalLanguageQuery --> GetBot
    NaturalLanguageQuery --> SaveBot
    NaturalLanguageQuery --> ListMyBots
    NaturalLanguageQuery --> GetMyBot
    
    SearchBots --> ListBotsFn
    SearchBots --> SemanticSearchFn
    GetBot --> FindVisibleBotFn
    SaveBot --> UpsertOwnBotFn
    ListMyBots --> ListBotsByAuthorFn
    GetMyBot --> FindOwnBotFn

    FindVisibleBotFn --> PrismaPrompt
    UpsertOwnBotFn --> PrismaPrompt
    ListBotsByAuthorFn --> PrismaPrompt
    FindOwnBotFn --> PrismaPrompt
```

### `search_bots`
- **Description**: Searches the public bots directory filtered by platform, computer requirement (`NONE`, `CLOUD`, `LOCAL`), category, and tags [src/lib/mcp/tools/bots.ts:81-103](). Supports AI semantic search when `semantic: true` is set and enabled on the server [src/lib/mcp/tools/bots.ts:118-141]().

### `get_bot`
- **Description**: Retrieves a public bot by ID or slug, including its full definition, routines, skills, connectors, and install instructions for various platforms [src/lib/mcp/tools/bots.ts:162-287]().

### `save_bot`
- **Description**: Creates or updates a private bot record for the authenticated user using `upsertOwnBot()` and the standard prompt creation pipeline [src/__tests__/api/mcp-bots.test.ts:115-160]().
- **Parameters**: `name` (string), `instructions` (string), `platforms` (array), `computerRequirement`, `routines`, `skills`, `connectors`, `tags`, `category` [src/__tests__/api/mcp-bots.test.ts:126-136]().

### `list_my_bots`
- **Description**: Lists all bots owned by the authenticated user, including private and unlisted ones [src/lib/mcp/tools/bots.ts:290-341]().

### `get_my_bot`
- **Description**: Retrieves a specific bot owned by the authenticated user, including private and unlisted details [src/lib/mcp/tools/bots.ts:344-391]().

Sources: [src/lib/mcp/tools/bots.ts:1-391](), [src/__tests__/api/mcp-bots.test.ts:1-166]()

---

## Team Tools Reference

Team tools (`src/lib/mcp/tools/teams.ts`) manage groups of bots that hand work off to each other.

Diagram: Team Tools Natural Language to Code Entity Space
```mermaid
graph TB
    UserTeamRequest["UserTeamRequest"]

    subgraph TeamTools["TeamToolsSpace"]
        ListTeams["list_teams"]
        GetTeam["get_team"]
        SaveTeam["save_team"]
    end

    subgraph TeamLibs["TeamLibraryLayer"]
        ListTeamsFn["listTeams()"]
        GetTeamFn["getTeam()"]
        UpsertTeamFn["upsertOwnTeam()"]
        PrismaTeam["db.botTeam"]
    end

    UserTeamRequest --> ListTeams
    UserTeamRequest --> GetTeam
    UserTeamRequest --> SaveTeam

    ListTeams --> ListTeamsFn
    GetTeam --> GetTeamFn
    SaveTeam --> UpsertTeamFn
    
    ListTeamsFn --> PrismaTeam
    GetTeamFn --> PrismaTeam
    UpsertTeamFn --> PrismaTeam
```

### `list_teams` & `get_team`
- `list_teams`: Lists bot teams, featured first, then newest, with keyword, category, and tag filtering [src/lib/mcp/tools/teams.ts:85-122]().
- `get_team`: Retrieves team description, member roles, directed handoff flows, and platform-specific install prompts via `getTeamInstallOptions()` [src/lib/mcp/tools/teams.ts:131-172]().

### `save_team`
- **Description**: Creates or updates a bot team with validated members and links (handoffs) [src/__tests__/api/mcp-teams.test.ts:111-120](). Marked as an idempotent write tool with `idempotentHint: true` [src/__tests__/api/mcp-teams.test.ts:119]().

Sources: [src/lib/mcp/tools/teams.ts:1-278](), [src/__tests__/api/mcp-teams.test.ts:1-120]()

---

# Page: API Keys & Authentication

# API Keys & Authentication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SELF-HOSTING.md](SELF-HOSTING.md)
- [context7.json](context7.json)
- [packages/prompts.chat/README.md](packages/prompts.chat/README.md)
- [prisma/migrations/20251213133000_add_github_username/migration.sql](prisma/migrations/20251213133000_add_github_username/migration.sql)
- [prisma/migrations/20260127100000_add_user_bio_and_custom_links/migration.sql](prisma/migrations/20260127100000_add_user_bio_and_custom_links/migration.sql)
- [public/deepwiki.svg](public/deepwiki.svg)
- [src/__tests__/api/user-profile.test.ts](src/__tests__/api/user-profile.test.ts)
- [src/__tests__/lib/plugins/auth/github.test.ts](src/__tests__/lib/plugins/auth/github.test.ts)
- [src/app/[username]/opengraph-image.tsx](src/app/[username]/opengraph-image.tsx)
- [src/app/api/admin/import-prompts/route.ts](src/app/api/admin/import-prompts/route.ts)
- [src/app/api/auth/register/route.ts](src/app/api/auth/register/route.ts)
- [src/app/api/user/profile/route.ts](src/app/api/user/profile/route.ts)
- [src/app/docs/api/page.tsx](src/app/docs/api/page.tsx)
- [src/app/docs/self-hosting/page.tsx](src/app/docs/self-hosting/page.tsx)
- [src/app/privacy/page.tsx](src/app/privacy/page.tsx)
- [src/app/settings/page.tsx](src/app/settings/page.tsx)
- [src/app/terms/page.tsx](src/app/terms/page.tsx)
- [src/components/auth/register-form.tsx](src/components/auth/register-form.tsx)
- [src/components/layout/footer.tsx](src/components/layout/footer.tsx)
- [src/components/settings/profile-form.tsx](src/components/settings/profile-form.tsx)
- [src/components/user/profile-links.tsx](src/components/user/profile-links.tsx)
- [src/lib/auth/index.ts](src/lib/auth/index.ts)
- [src/lib/db-errors.ts](src/lib/db-errors.ts)
- [src/lib/plugins/auth/github.ts](src/lib/plugins/auth/github.ts)

</details>



This page details the user-scoped API key system, including key generation and formatting (`pchat_*`), token validation via `authenticateApiKey` with in-memory caching, rate-limiting layers, private prompt access rules, and tiered access control across MCP and web interfaces [src/lib/auth/index.ts:1-106](). For session-based authentication via NextAuth, see [Authentication & Authorization](5.1). For MCP tools, see [MCP Server Integration](11.1).

---

## Overview

Each registered user is assigned a personal API key stored in the `apiKey` field on the `User` Prisma model [src/app/settings/page.tsx:25-39](). The key format begins with the prefix `pchat_` followed by a 32-character alphanumeric token, providing a secure bearer token for programmatic access [src/app/docs/api/page.tsx:111]().

API keys serve two primary functions:
1. **Authentication for MCP Write Operations**: Tools that modify data or save prompts (`save_prompt`, `save_skill`, `save_bot`) require a valid API key supplied through the `PROMPTS_API_KEY` HTTP header or environment variable [src/app/docs/api/page.tsx:116-121]().
2. **Private Prompt Access**: Read operations (`search_prompts`, `get_prompt`) include private prompts owned by the authenticated user when a valid API key is provided [src/app/docs/api/page.tsx:98-100]().

Sources: [src/app/settings/page.tsx:25-39](), [src/app/docs/api/page.tsx:111](), [src/app/docs/api/page.tsx:116-121](), [src/app/docs/api/page.tsx:98-100]()

---

## Database Storage & Validation

The `User` model schema stores authentication-related properties:

| Field | Type | Purpose |
| :--- | :--- | :--- |
| `apiKey` | `String?` | Unique bearer token used with the `PROMPTS_API_KEY` header [src/app/settings/page.tsx:34](). |
| `mcpPromptsPublicByDefault` | `Boolean` | Default visibility setting for prompts created via MCP tools [src/app/settings/page.tsx:35-36](). |

### API Key Format Validation

Before performing database queries, incoming keys are validated using format checking rules. A valid key must start with `pchat_` followed by exactly 32 alphanumeric characters, preventing unnecessary database lookups for malformed tokens [src/app/docs/api/page.tsx:111]().

### Authentication Cache

To minimize database overhead, authentication lookups utilize an in-memory cache (`authCache`) with a 5-minute TTL (`AUTH_CACHE_TTL`):

```typescript
async function authenticateApiKey(apiKey: string | null): Promise<AuthenticatedUser | null> {
  if (!apiKey || !isValidApiKeyFormat(apiKey)) {
    return null;
  }

  const cached = authCache.get(apiKey);
  if (cached && Date.now() < cached.expiry) {
    return cached.user;
  }

  const user = await db.user.findUnique({
    where: { apiKey },
    select: {
      id: true,
      username: true,
      mcpPromptsPublicByDefault: true,
    },
  });

  authCache.set(apiKey, { user, expiry: Date.now() + AUTH_CACHE_TTL });
  return user;
}
```

Sources: [src/app/settings/page.tsx:25-39](), [src/app/docs/api/page.tsx:111]()

---

## Authentication Flow & Code Entities

The sequence below illustrates how the system handles API requests containing `PROMPTS_API_KEY`, authenticates via `authenticateApiKey()`, checks `authCache` and `db.user`, and initializes server operations [src/lib/auth/index.ts:1-106]().

### Diagram 1: API Key Authentication and Private Prompt Access Flow
```mermaid
sequenceDiagram
    participant Client as "MCPClient"
    participant MCPHandler as "ApiRouteHandler"
    participant AuthFn as "authenticateApiKey()"
    participant Cache as "authCache"
    participant DB as "db.user"
    participant Server as "createServer()"

    Client->>MCPHandler: "POST /api/mcp (PROMPTS_API_KEY)"
    MCPHandler->>AuthFn: "authenticateApiKey(apiKey)"
    AuthFn->>Cache: "authCache.get(apiKey)"
    alt Cache Miss
        AuthFn->>DB: "db.user.findUnique({ where: { apiKey } })"
        DB-->>AuthFn: "AuthenticatedUser"
        AuthFn->>Cache: "authCache.set(apiKey, user)"
    else Cache Hit
        Cache-->>AuthFn: "Cached AuthenticatedUser"
    end
    AuthFn-->>MCPHandler: "AuthenticatedUser | null"
    MCPHandler->>Server: "createServer({ authenticatedUser })"
    Server-->>Client: "JSON-RPC Response"
```

Sources: [src/lib/auth/index.ts:1-106](), [src/app/settings/page.tsx:25-39]()

---

## Rate Limiting Architecture

API requests and MCP tool calls are governed by rate limiters implemented via the `RateLimiter` class in `src/lib/rate-limit.ts`.

### Rate Limit Configurations

| Limiter Name | Rate Limit | Applies To |
| :--- | :--- | :--- |
| `mcpGeneralLimiter` | 20 requests / min | General MCP POST requests |
| `mcpToolCallLimiter` | 10 requests / min | Tool execution calls (`tools/call`) |
| `mcpWriteToolLimiter` | 5 requests / min | Write operations (`save_prompt`, `save_skill`) |
| `mcpAiToolLimiter` | 2 requests / min | AI-powered tools (`improve_prompt`) |

### Rate Limiter Architecture
```mermaid
graph TD
    subgraph "RateLimitLibrary"
        RL["RateLimiter"]
        GL["mcpGeneralLimiter (20/min)"]
        TL["mcpToolCallLimiter (10/min)"]
        WL["mcpWriteToolLimiter (5/min)"]
        AI["mcpAiToolLimiter (2/min)"]
    end

    subgraph "APIEntrypoint"
        API["POST /api/mcp"]
    end

    API --> GL
    API --> TL
    API --> WL
    API --> AI
    GL -->|check(identifier)| RL
    TL -->|check(identifier)| RL
    WL -->|check(identifier)| RL
    AI -->|check(identifier)| RL
```

Sources: [src/lib/auth/index.ts:1-106](), [src/app/docs/api/page.tsx:116-121]()

---

## Using the API Key: `PROMPTS_API_KEY` Header

Clients authenticate by passing their API key via the `PROMPTS_API_KEY` HTTP header or environment variable [src/app/docs/api/page.tsx:116-121]().

```bash
# Remote HTTP usage
curl -X POST https://prompts.chat/api/mcp \
  -H "Content-Type: application/json" \
  -H "PROMPTS_API_KEY: pchat_your_api_key_here" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

```bash
# Local usage (stdio) environment variable
PROMPTS_API_KEY=pchat_your_api_key_here npx -y @fkadev/prompts.chat-mcp
```

Sources: [src/app/docs/api/page.tsx:116-121]()

---

## Private Prompt Access Logic

Prompt filtering constructs Prisma query conditions based on authentication state [src/app/settings/page.tsx:25-39]():

- **Unauthenticated**: Returns only public prompts (`isPrivate: false`) where `isUnlisted: false` and `deletedAt` is `null`.
- **Authenticated**: Includes public prompts plus private prompts owned by the user (`isPrivate: true` AND `authorId` matches).

```typescript
if (authenticatedUser && includeOwnPrivate) {
  const usersFilter = options.users && options.users.length > 0 ? options.users : null;
  const includeAuthUserPrivate = !usersFilter || usersFilter.includes(authenticatedUser.username);

  if (includeAuthUserPrivate) {
    baseFilter.OR = [
      { isPrivate: false },
      { isPrivate: true, authorId: authenticatedUser.id },
    ];
  } else {
    baseFilter.isPrivate = false;
  }
} else {
  baseFilter.isPrivate = false;
}
```

Sources: [src/app/settings/page.tsx:25-39](), [src/lib/auth/index.ts:1-106]()

---

## OAuth and NextAuth Integration

The web interface uses NextAuth 5.0 with `CustomPrismaAdapter` to manage user persistence, OAuth provider plugins (GitHub, Google, Apple, Azure), and credential authentication [src/lib/auth/index.ts:31-107]().

- **User Creation & Unclaimed Accounts**: `CustomPrismaAdapter.createUser` handles creation and claims unclaimed placeholder accounts created during CSV imports [src/lib/auth/index.ts:37-69](). This is particularly relevant for the `src/app/api/admin/import-prompts/route.ts` endpoint, which can create pseudo-users for contributors from CSV data [src/app/api/admin/import-prompts/route.ts:159-168]().
- **Profile Management**: Profile updates (`/api/user/profile`) validate inputs via Zod schemas and enforce case-insensitive username uniqueness [src/components/settings/profile-form.tsx:38-42]().
- **Registration**: Passwords are secure credential parameters handled via auth routes [src/lib/auth/index.ts:1-107]().

Sources: [src/lib/auth/index.ts:31-107](), [src/app/api/admin/import-prompts/route.ts:159-168](), [src/components/settings/profile-form.tsx:38-42]()

---

## Tiered Access Control & `mcpPromptsPublicByDefault`

The `mcpPromptsPublicByDefault` property dictates default prompt visibility when saving via MCP tools [src/app/settings/page.tsx:63-68]().

| `mcpPromptsPublicByDefault` | Tool Parameter `isPrivate` | Resulting Prompt Visibility |
| :--- | :--- | :--- |
| `true` | Not provided | **Public** |
| `false` | Not provided | **Private** |
| Any | `true` | **Private** (explicit override) |
| Any | `false` | **Public** (explicit override) |

Sources: [src/app/settings/page.tsx:63-68]()

---

## API Access Summary

| Access Type | Credential | Allowed Operations |
| :--- | :--- | :--- |
| **Public API** | None | Read public prompts; MCP read operations (public only). |
| **User API Key** | `PROMPTS_API_KEY` header | MCP write tools (`save_prompt`, `save_skill`); private prompt access [src/app/docs/api/page.tsx:116-121](). |
| **Web Session** | NextAuth session cookie | Web UI CRUD operations, admin dashboard (if `role = ADMIN`) [src/lib/auth/index.ts:154-196](). |

Sources: [src/lib/auth/index.ts:154-196](), [src/app/docs/api/page.tsx:116-121]()

---

## Summary Diagrams Bridging Natural Language Concepts and Code Entities

### Diagram 2: User Privilege & Tiered Access Control in MCP Server
```mermaid
flowchart TD
    APIKey["API Key pchat_*"]
    AuthUser["AuthenticatedUser {id, username, mcpPromptsPublicByDefault}"]
    MCPServer["McpServer"]
    PromptSaveTool["MCP Tool: save_prompt / save_skill"]
    PrivateFlag["isPrivate flag on prompt"]
    DefaultSetting["mcpPromptsPublicByDefault (user setting)"]
    PromptStorage["db.prompt record with isPrivate"]
    PromptQuery["Prompt Query with buildPromptFilter()"]
    PublicPrompts["Public prompts returned"]
    PrivatePrompts["Private prompts returned for user"]

    APIKey --> AuthUser
    AuthUser --> MCPServer
    DefaultSetting --> PromptSaveTool
    PromptSaveTool -->|Overrides isPrivate| PromptStorage
    MCPServer --> PromptSaveTool
    MCPServer --> PromptQuery
    PromptQuery --> PublicPrompts
    PromptQuery --> PrivatePrompts
```
Sources: [src/lib/auth/index.ts:31-107](), [src/app/settings/page.tsx:25-39]()

---

# Page: CLI Tool

# CLI Tool

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [eslint.config.mjs](eslint.config.mjs)
- [packages/prompts.chat/bin/cli.js](packages/prompts.chat/bin/cli.js)
- [packages/prompts.chat/package-lock.json](packages/prompts.chat/package-lock.json)
- [packages/prompts.chat/package.json](packages/prompts.chat/package.json)
- [packages/prompts.chat/scripts/generate-docs.ts](packages/prompts.chat/scripts/generate-docs.ts)
- [packages/prompts.chat/src/builder/index.ts](packages/prompts.chat/src/builder/index.ts)
- [packages/prompts.chat/src/cli/api.ts](packages/prompts.chat/src/cli/api.ts)
- [packages/prompts.chat/src/cli/components/PromptDetail.tsx](packages/prompts.chat/src/cli/components/PromptDetail.tsx)
- [packages/prompts.chat/src/cli/components/PromptList.tsx](packages/prompts.chat/src/cli/components/PromptList.tsx)
- [packages/prompts.chat/src/cli/components/RunPrompt.tsx](packages/prompts.chat/src/cli/components/RunPrompt.tsx)
- [packages/prompts.chat/src/cli/index.tsx](packages/prompts.chat/src/cli/index.tsx)
- [packages/prompts.chat/src/cli/new.ts](packages/prompts.chat/src/cli/new.ts)
- [packages/prompts.chat/src/parser/index.ts](packages/prompts.chat/src/parser/index.ts)
- [packages/prompts.chat/tsconfig.json](packages/prompts.chat/tsconfig.json)
- [packages/prompts.chat/tsup.config.ts](packages/prompts.chat/tsup.config.ts)
- [src/components/ide/examples/generated.ts](src/components/ide/examples/generated.ts)
- [src/components/prompts/skill-diff-viewer.tsx](src/components/prompts/skill-diff-viewer.tsx)
- [src/components/prompts/skill-editor.tsx](src/components/prompts/skill-editor.tsx)
- [src/data/api-docs.ts](src/data/api-docs.ts)
- [src/data/method-options.ts](src/data/method-options.ts)
- [src/data/type-definitions.ts](src/data/type-definitions.ts)

</details>



The `prompts.chat` CLI is a terminal-based prompt library tool combining an interactive terminal UI for browsing AI prompts, a project scaffolding mechanism to deploy self-hosted instances, and programmatic builder/parser packages. It serves developers and prompt engineers who want to explore, create, and manage prompt collections efficiently.

This page documents the CLI tool's implementation, including the interactive prompt browser, the project scaffolding command, builder/parser packages, and CLI usage patterns.

---

## Package Overview and Structure

The CLI and associated prompt toolkit reside in `packages/prompts.chat/` [packages/prompts.chat/package.json:1-44](). The package operates both as a standalone CLI application and as a modular library providing prompt building and parsing primitives.

### Key Aspects

- **Binaries:** The package exposes executables `prompts-chat` and `prompts.chat` mapped to `bin/cli.js` [packages/prompts.chat/package.json:9-12](). Runtime requires Node.js `>=18` [packages/prompts.chat/package.json:70-72]().
- **Library Exports:** Publishes ES modules and CommonJS outputs under `dist/`, including `./builder`, `./parser`, `./variables`, `./similarity`, and `./quality` [packages/prompts.chat/package.json:13-44]().
- **UI Dependencies:** Leverages `ink`, `ink-text-input`, `ink-spinner`, `ink-select-input`, and `react` for terminal user interfaces [packages/prompts.chat/package.json:83-88]().

Sources: [packages/prompts.chat/package.json:1-101]()

---

## CLI Commands and Main Entry

The CLI is implemented in `packages/prompts.chat/src/cli/index.tsx`, using `meow` for argument parsing [packages/prompts.chat/src/cli/index.tsx:3, 102-134]().

### Commands Table

| Command | Usage | Description | Code Reference |
|---|---|---|---|
| *(default)* | `npx prompts.chat` | Launch interactive TUI browser | [packages/prompts.chat/src/cli/index.tsx:161-171]() |
| `new` | `npx prompts.chat new <dir>` | Scaffold a new self-hosted instance | [packages/prompts.chat/src/cli/index.tsx:140-149](), [packages/prompts.chat/src/cli/new.ts:1-116]() |
| `mcp` | `npx prompts.chat mcp [args]` | Proxy command to launch MCP server tool | [packages/prompts.chat/src/cli/index.tsx:152-159]() |

The `main()` function reads command-line inputs and dispatches actions accordingly [packages/prompts.chat/src/cli/index.tsx:136-173]().

### Command Dispatch Flow

```mermaid
flowchart TD
  CLIInput[""CLIArgs""] --> ParseArgs[""ParseWithMeow""]
  ParseArgs -->|"new"| HandleNew[""createNew""]
  ParseArgs -->|"mcp"| SpawnMCP[""SpawnMCPProxy""]
  ParseArgs -->|"default"| RunTUI[""LaunchAppTUI""]

  subgraph CodeEntities
    HandleNew
    SpawnMCP
    RunTUI
  end
```
Sources: [packages/prompts.chat/src/cli/index.tsx:3,102-173](), [packages/prompts.chat/src/cli/new.ts:1-116]()

---

## Interactive Prompt Browser

Running the CLI without arguments launches a terminal UI for browsing, searching, filtering, and executing prompts.

### Implementation Details

- **State Management:** The root `App` component (`src/cli/index.tsx`) manages views (`list` or `detail`), search queries, page numbers, category filters, and selection indices [packages/prompts.chat/src/cli/index.tsx:11-30]().
- **Data Fetching and Caching:** Prompts are fetched from `https://prompts.chat/prompts.json?full_content=true` via `loadPrompts()` in `src/cli/api.ts` [packages/prompts.chat/src/cli/api.ts:5-89](). It caches responses locally in `~/.prompts-chat/prompts.json` [packages/prompts.chat/src/cli/api.ts:6-7]().
- **Filtering:** Client-side filtering and pagination are handled by `filterPrompts()` and `getCategories()` [packages/prompts.chat/src/cli/api.ts:110-168]().
- **Prompt List Component:** `PromptList` renders paginated items with category/search selectors and keyboard handlers (`j/k`, `n/p`, `/`, `c`, `r`) [packages/prompts.chat/src/cli/components/PromptList.tsx:22-199]().
- **Prompt Detail Component:** `PromptDetail` handles variable extraction via `extractVariables()`, variable interactive inputs, compilation, media previews (`terminal-image`), and platform execution [packages/prompts.chat/src/cli/components/PromptDetail.tsx:58-121]().

Sources: [packages/prompts.chat/src/cli/index.tsx:22-100](), [packages/prompts.chat/src/cli/api.ts:1-172](), [packages/prompts.chat/src/cli/components/PromptList.tsx:22-199](), [packages/prompts.chat/src/cli/components/PromptDetail.tsx:58-212]()

---

## Project Scaffolding with `new` Command

The `new` command scaffolds a self-hosted `prompts.chat` instance into a target directory [packages/prompts.chat/src/cli/new.ts:1-116]().

### Workflow Steps

1. **Directory Validation:** Confirms the target directory is empty [packages/prompts.chat/src/cli/new.ts:72-81]().
2. **Repository Cloning:** Runs `npx degit f/prompts.chat <dir>` [packages/prompts.chat/src/cli/new.ts:86-92]().
3. **Cleanup:** Removes extraneous configuration directories (`.github`, `.claude`, `packages`) and internal scripts [packages/prompts.chat/src/cli/new.ts:11-39]().
4. **Dependency Installation:** Executes `npm install` [packages/prompts.chat/src/cli/new.ts:99-104]().
5. **Interactive Setup:** Spawns `node scripts/setup.js` for configuration [packages/prompts.chat/src/cli/new.ts:41-70]().

Sources: [packages/prompts.chat/src/cli/index.tsx:140-149](), [packages/prompts.chat/src/cli/new.ts:1-116]()

---

## Builder and Parser Packages

The toolkit includes modular packages for constructing and parsing prompt representations.

### Builder Package (`./builder`)

- Exposes a fluent Domain-Specific Language (DSL) to construct prompts programmatically [packages/prompts.chat/package.json:34-38]().
- Supports chaining methods for video, audio, and image prompt generation [src/components/ide/examples/generated.ts:4-217]().
- Autocomplete options are supplied via auto-generated configuration mappings in `src/data/method-options.ts` [src/data/method-options.ts:1-37]().

### Parser Package (`./parser`)

- Provides multi-format parsing utilities for Markdown, YAML frontmatter, and skill file structures [packages/prompts.chat/package.json:39-43]().
- `parseSkillFiles` breaks down multi-file skill strings into individual `SkillFile` objects for editors and diff viewers [src/components/prompts/skill-diff-viewer.tsx:24](), [src/components/prompts/skill-editor.tsx:30]().

Sources: [packages/prompts.chat/package.json:34-43](), [src/components/ide/examples/generated.ts:4-217](), [src/data/method-options.ts:1-37](), [src/components/prompts/skill-diff-viewer.tsx:24](), [src/components/prompts/skill-editor.tsx:30]()

---

## CLI Usage Patterns and Interaction

### Interactive Navigation

- **List Navigation:** Use arrow keys or `j/k` to traverse prompts [packages/prompts.chat/src/cli/components/PromptList.tsx:176-182]().
- **Selection:** Press `Enter` to open prompt details [packages/prompts.chat/src/cli/components/PromptList.tsx:184-186]().
- **Search:** Press `/` to search titles, content, authors, or tags [packages/prompts.chat/src/cli/components/PromptList.tsx:165-168]().
- **Pagination:** Press `n` or `p` to change pages [packages/prompts.chat/src/cli/components/PromptList.tsx:188-194]().
- **Copying:** Press `c` for variable-filled copying or `C` for raw copying [packages/prompts.chat/src/cli/components/PromptDetail.tsx:197-209]().

### Running Prompts

The `RunPrompt` component displays supported AI chat, code, and media generation platforms [packages/prompts.chat/src/cli/components/RunPrompt.tsx:1-144](). Users toggle between categories using `h/l` keys and execute prompts directly via platform query strings or clipboard fallback [packages/prompts.chat/src/cli/components/RunPrompt.tsx:39-68]().

Sources: [packages/prompts.chat/src/cli/components/PromptList.tsx:22-199](), [packages/prompts.chat/src/cli/components/PromptDetail.tsx:58-212](), [packages/prompts.chat/src/cli/components/RunPrompt.tsx:1-144]()

---

## Architecture Diagrams

### Diagram 1: Natural Language Space to Code Entity Space: Prompt Browsing Data Flow

```mermaid
flowchart TD
  UserCmd[""UserRunCLI""] --> CLIEntry[""cli/index.tsx:main""]
  CLIEntry --> FetchPrompts[""api.loadPrompts""]
  FetchPrompts --> CacheCheck[""CacheCheckInMemory""]
  CacheCheck -->|"Hit"| ReturnCache[""ReturnCachedPrompts""]
  CacheCheck -->|"Miss"| HTTPFetch[""FetchPromptsJSON""]
  HTTPFetch --> SaveCache[""SaveCacheToDisk""]
  SaveCache --> ReturnData[""ReturnPromptArray""]
  ReturnCache --> ReturnData
  ReturnData --> Interaction[""RenderPromptList""]

  Interaction --> PromptSelect[""UserSelectPrompt""]
  PromptSelect --> PromptDetail[""RenderPromptDetail""]
  PromptDetail --> VariableFill[""ExtractAndFillVariables""]
  VariableFill --> PromptCompile[""CompilePromptContent""]
  PromptCompile --> PlatformRun[""RunPromptOnPlatform""]

  subgraph CLI_Code
    CLIEntry
    FetchPrompts
    CacheCheck
    HTTPFetch
    SaveCache
    ReturnData
    PromptDetail
    VariableFill
    PromptCompile
    PlatformRun
  end
```
Sources: [packages/prompts.chat/src/cli/index.tsx:136-173](), [packages/prompts.chat/src/cli/api.ts:81-108](), [packages/prompts.chat/src/cli/components/PromptDetail.tsx:58-212]()

---

### Diagram 2: Natural Language Space to Code Entity Space: Scaffolding a New Instance

```mermaid
flowchart TD
  UserCmd2[""UserRunNew""] --> CLIEntry2[""cli/index.tsx:main""]
  CLIEntry2 --> NewCmdHandler[""DetectNewCommand""]
  NewCmdHandler --> CreateNewFn[""new.ts:createNew""]
  CreateNewFn --> DirCheck[""VerifyDirectoryEmpty""]
  DirCheck -->|"Empty"| DegitClone[""DegitCloneRepository""]
  DegitClone --> RemoveFiles[""RemoveExtraneousFiles""]
  RemoveFiles --> NpmInstall[""RunNpmInstall""]
  NpmInstall --> SetupScript[""RunSetupScript""]
  SetupScript --> Finish[""PrintSuccessMessage""]

  subgraph CLI_Code_Scaffold
    CLIEntry2
    NewCmdHandler
    CreateNewFn
    DirCheck
    DegitClone
    RemoveFiles
    NpmInstall
    SetupScript
    Finish
  end
```
Sources: [packages/prompts.chat/src/cli/index.tsx:136-149](), [packages/prompts.chat/src/cli/new.ts:1-116]()

---

# Page: Browser Extensions & Desktop Apps

# Browser Extensions & Desktop Apps

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/raycast-extension/.gitignore](packages/raycast-extension/.gitignore)
- [packages/raycast-extension/CHANGELOG.md](packages/raycast-extension/CHANGELOG.md)
- [packages/raycast-extension/README.md](packages/raycast-extension/README.md)
- [packages/raycast-extension/assets/icon.png](packages/raycast-extension/assets/icon.png)
- [packages/raycast-extension/eslint.config.mjs](packages/raycast-extension/eslint.config.mjs)
- [packages/raycast-extension/metadata/prompts-chat-1.png](packages/raycast-extension/metadata/prompts-chat-1.png)
- [packages/raycast-extension/metadata/prompts-chat-2.png](packages/raycast-extension/metadata/prompts-chat-2.png)
- [packages/raycast-extension/metadata/prompts-chat-3.png](packages/raycast-extension/metadata/prompts-chat-3.png)
- [packages/raycast-extension/package-lock.json](packages/raycast-extension/package-lock.json)
- [packages/raycast-extension/package.json](packages/raycast-extension/package.json)
- [packages/raycast-extension/raycast-env.d.ts](packages/raycast-extension/raycast-env.d.ts)
- [packages/raycast-extension/src/api.ts](packages/raycast-extension/src/api.ts)
- [packages/raycast-extension/src/browse-categories.tsx](packages/raycast-extension/src/browse-categories.tsx)
- [packages/raycast-extension/src/browse-prompts.tsx](packages/raycast-extension/src/browse-prompts.tsx)
- [packages/raycast-extension/src/cache.ts](packages/raycast-extension/src/cache.ts)
- [packages/raycast-extension/src/components/prompt-detail.tsx](packages/raycast-extension/src/components/prompt-detail.tsx)
- [packages/raycast-extension/src/components/run-prompt.tsx](packages/raycast-extension/src/components/run-prompt.tsx)
- [packages/raycast-extension/src/download-prompts.tsx](packages/raycast-extension/src/download-prompts.tsx)
- [packages/raycast-extension/src/random-prompt.tsx](packages/raycast-extension/src/random-prompt.tsx)
- [packages/raycast-extension/src/search-prompts.tsx](packages/raycast-extension/src/search-prompts.tsx)
- [packages/raycast-extension/src/types.ts](packages/raycast-extension/src/types.ts)

</details>



This document covers external client integrations supported by prompts.chat beyond its web interface. This includes the official Raycast desktop extension for macOS, browser extensions/addons for Chrome and Firefox detected dynamically from the web UI, and mobile app integration concepts. These integrations enable users to conveniently search, browse, cache, and run prompts outside a browser tab.

> For command-line tool integration, see [CLI Tool](11.4).  
> For MCP protocol integration with IDEs and advanced workflows, see [MCP Server Integration](11.1).

---

## Purpose and Scope

The goal of browser extensions and desktop apps is to provide users an unobtrusive, fast, and accessible way to interact with the prompts.chat AI prompt library. These tools consume public API endpoints, leverage local caching for offline responsiveness, and facilitate prompt execution across multiple platforms.

**Key capabilities include:**
- **Native macOS Raycast Extension:** Commands to search, browse, and run prompts, featuring local caching for offline use and platform launching `[packages/raycast-extension/package.json:3-52]()`.
- **API Client Layer:** Standardized request handling via `packages/raycast-extension/src/api.ts` supporting configurable base URLs `[packages/raycast-extension/src/api.ts:8-11]()`, prompt fetching `[packages/raycast-extension/src/api.ts:13-41]`, and slug lookups `[packages/raycast-extension/src/api.ts:43-59]()`.
- **Command Caching & Search:** Local cache management and client-side filtering implemented in `packages/raycast-extension/src/search-prompts.tsx` `[packages/raycast-extension/src/search-prompts.tsx:24-60]()` and `packages/raycast-extension/src/random-prompt.tsx` `[packages/raycast-extension/src/random-prompt.tsx:7-38]()`.
- **Multi-Platform Integration:** Enables running prompts on multiple AI and code platforms with deep linking features `[packages/raycast-extension/README.md:25-34]()`.

Sources: `[packages/raycast-extension/package.json:3-52]`, `[packages/raycast-extension/src/api.ts:8-59]`, `[packages/raycast-extension/src/search-prompts.tsx:24-60]`, `[packages/raycast-extension/src/random-prompt.tsx:7-38]`, `[packages/raycast-extension/README.md:25-34]()`

---

## Raycast Extension Architecture

The Raycast extension is packaged under `packages/raycast-extension` `[packages/raycast-extension/package.json:1-84]()`. It is a TypeScript React application interacting with public APIs and Raycast's native extension APIs.

### Command Manifest

Defined in `packages/raycast-extension/package.json` under the `"commands"` array, core commands map directly to React components `[packages/raycast-extension/package.json:16-52]()`:

| Command Name | Component / Handler | Purpose |
| --- | --- | --- |
| `search-prompts` | `SearchPrompts` (`search-prompts.tsx`) | Search all cached prompts and remotely |
| `browse-prompts` | `BrowsePrompts` (`browse-prompts.tsx`) | Browse latest prompts with filter options |
| `random-prompt` | `RandomPrompt` (`random-prompt.tsx`) | Show a random prompt for inspiration |
| `download-prompts` | `DownloadPrompts` (`download-prompts.tsx`) | Fetch and cache all prompts for offline |
| `browse-categories` | `BrowseCategories` (`browse-categories.tsx`) | Explore prompts by category |

Title: "Raycast Command-to-Code Entity Mapping"
```mermaid
graph TD
    UserQuery["User Command Execution"] --> SC["SearchPrompts (search-prompts.tsx)"]
    UserQuery --> BC["BrowsePrompts (browse-prompts.tsx)"]
    UserQuery --> RC["RandomPrompt (random-prompt.tsx)"]
    UserQuery --> DC["DownloadPrompts (download-prompts.tsx)"]
    UserQuery --> CC["BrowseCategories (browse-categories.tsx)"]

    SC --> |"Filters & Renders"| PLI["PromptListItem"]
    DC --> |"Invokes Network"| API["downloadAllPrompts"]
    BC --> |"Groups Categories"| BCP["BrowseCategoriesComponent"]
```
Sources: `[packages/raycast-extension/package.json:16-52]`, `[packages/raycast-extension/src/search-prompts.tsx:24-105]`, `[packages/raycast-extension/src/random-prompt.tsx:7-38]()`

---

## API Client & Request Handling

The Raycast extension communicates with the prompts.chat backend via a dedicated API module located at `packages/raycast-extension/src/api.ts` `[packages/raycast-extension/src/api.ts:1-102]()`.

### Key Functions

- `getBaseUrl()`: Reads user preferences to obtain the target instance URL, defaulting to `https://prompts.chat` `[packages/raycast-extension/src/api.ts:8-11]()`.
- `fetchPrompts(options)`: Constructs query parameters (`page`, `perPage`, `type`, `category`, `tag`, `sort`, `q`) and queries `/api/prompts` `[packages/raycast-extension/src/api.ts:13-41]()`.
- `fetchPromptBySlug(username, slug)`: Fetches individual prompt records via `/api/prompts/${slug}` `[packages/raycast-extension/src/api.ts:43-59]()`.
- `searchPrompts(query, limit)`: Performs real-time keyword search against `/api/prompts/search` when query length exceeds 2 characters `[packages/raycast-extension/src/api.ts:61-93]()`.

Sources: `[packages/raycast-extension/src/api.ts:1-102]()`

---

## Caching & Data Flow Layer

The extension implements a local caching layer to store prompt data for offline use and instant search filtering.

Title: "Raycast Caching Data Flow"
```mermaid
graph TD
    subgraph ClientExecution ["Raycast Extension Space"]
        SP["SearchPrompts (search-prompts.tsx)"]
        RP["RandomPrompt (random-prompt.tsx)"]
        BP["BrowsePrompts (browse-prompts.tsx)"]
        CACHE["getCachedPrompts (cache.ts)"]
    end

    subgraph StorageLayer ["Raycast Environment"]
        LS["LocalStorage"]
    end

    subgraph RemoteAPI ["prompts.chat Server"]
        DP["DownloadPrompts (download-prompts.tsx)"]
        API["downloadAllPrompts (cache.ts)"]
        PROMPTS_API["/api/prompts"]
    end

    SP -->|Reads Cache| CACHE
    RP -->|Reads Cache| CACHE
    BP -->|Reads Cache| CACHE
    CACHE -->|Queries| LS
    DP -->|Fetches Data| API
    API -->|HTTP GET| PROMPTS_API["/api/prompts"]
    DP -->|Saves Cache| LS
```

- `SearchPrompts` initializes by calling `getCachedPrompts()` to load records into local component state `[packages/raycast-extension/src/search-prompts.tsx:53-60]()`.
- `RandomPrompt` loads cached prompts and passes a randomly selected entry to `PromptDetailView` `[packages/raycast-extension/src/random-prompt.tsx:18-34]()`.
- If no prompts are cached, empty views provide direct action triggers to invoke `downloadAllPrompts()` `[packages/raycast-extension/src/search-prompts.tsx:71-85]`, `[packages/raycast-extension/src/random-prompt.tsx:44-58]()`.

Sources: `[packages/raycast-extension/src/search-prompts.tsx:24-60]`, `[packages/raycast-extension/src/random-prompt.tsx:7-65]()`

---

## Prompt Execution & Variable Interpolation

The Raycast extension provides variable extraction and form-based filling before executing prompts against external chat, code, or media platforms.

- Pressing `Enter` on any prompt list item opens the `RunPromptForm` target `[packages/raycast-extension/src/search-prompts.tsx:117-123]()`.
- Users can copy raw prompts directly via `⌘ C` `[packages/raycast-extension/src/search-prompts.tsx:125-129]()` or open the corresponding web page via `⌘ O` `[packages/raycast-extension/src/search-prompts.tsx:130-134]()`.

Sources: `[packages/raycast-extension/src/search-prompts.tsx:107-167]()`

---

# Summary

| Integration | Description | Code Location |
| --- | --- | --- |
| Raycast Manifest | Extension package definition, commands, and preferences | `packages/raycast-extension/package.json` |
| Raycast API Client | Network wrapper for fetching prompts and search endpoints | `packages/raycast-extension/src/api.ts` |
| Search & Caching | Component implementing cached prompt list and offline download | `packages/raycast-extension/src/search-prompts.tsx` |
| Random Prompt | Component fetching and rendering randomized cached prompts | `packages/raycast-extension/src/random-prompt.tsx` |

Sources:
- `[packages/raycast-extension/package.json:1-84]()`  
- `[packages/raycast-extension/src/api.ts:1-102]()`  
- `[packages/raycast-extension/src/search-prompts.tsx:1-167]()`  
- `[packages/raycast-extension/src/random-prompt.tsx:1-65]()`  
- `[packages/raycast-extension/README.md:1-56]()`

---

# Page: Typed-Prompts IDE & Embeds

# Typed-Prompts IDE & Embeds

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/api/prompts/[id]/raw/route.ts](src/app/api/prompts/[id]/raw/route.ts)
- [src/app/developers/page.tsx](src/app/developers/page.tsx)
- [src/app/embed/page.tsx](src/app/embed/page.tsx)
- [src/components/developers/embed-designer.tsx](src/components/developers/embed-designer.tsx)
- [src/components/developers/embed-examples.ts](src/components/developers/embed-examples.ts)
- [src/components/developers/prompt-tokenizer.tsx](src/components/developers/prompt-tokenizer.tsx)
- [src/components/ide/prompt-ide.tsx](src/components/ide/prompt-ide.tsx)
- [src/components/prompts/download-prompt-dropdown.tsx](src/components/prompts/download-prompt-dropdown.tsx)
- [src/proxy.ts](src/proxy.ts)

</details>



## Purpose & Scope
This page details the in-browser developer tools available on prompts.chat, including the Typed-Prompts IDE, Prompt Builder, Prompt Tokenizer, and Embed Designer. It also covers the `/embed` page for integrating prompts into external sites and the raw prompt API for programmatic access. These tools assist developers in creating, testing, and integrating AI prompts efficiently.

Sources: [src/app/developers/page.tsx:1-7]()

---

## Typed-Prompts IDE
The Typed-Prompts IDE, accessible via the `/developers` route, provides an interactive environment for writing and testing prompts using the `prompts.chat` JavaScript library [src/components/ide/prompt-ide.tsx:15-28](). This IDE leverages Monaco Editor for code editing, syntax highlighting, type checking, and auto-completion based on the fluent API.

### Features
- **Monaco Editor Integration:** A full-featured TypeScript editor providing syntax highlighting, inline errors, and suggestions for prompt-building code [src/components/ide/prompt-ide.tsx:5-5]().
- **`prompts.chat` Library Usage:** Imports modules like `builder`, `image`, `video`, `audio`, and `chat` from `prompts.chat` to write prompts fluently and test various prompt types interactively [src/components/ide/prompt-ide.tsx:15-28]().
- **Authentication Safeguards:** Requires user session verification via `useSession` ([src/components/ide/prompt-ide.tsx:10-54]()) before executing custom TypeScript evaluation [src/components/ide/prompt-ide.tsx:149-154]().
- **TypeScript Diagnostics & Runtime Reporting:** Aggregates Monaco diagnostics via `getTypeErrors` ([src/components/ide/prompt-ide.tsx:100-146]()) and maps parameter types to valid option definitions (`TYPE_OPTIONS`) [src/components/ide/prompt-ide.tsx:33-33]().
- **API Docs Sidebar & Popups:** Displays an interactive documentation sidebar (`ApiDocsSidebar`) and item details popup (`ApiDetailsPopup`) [src/components/ide/prompt-ide.tsx:36-37]().

### Implementation Details
The `PromptIde` component ([src/components/ide/prompt-ide.tsx:51-1074]()) manages editor state, validation, and execution:
- Validates code imports to ensure only `prompts.chat` packages are evaluated [src/components/ide/prompt-ide.tsx:85-95]().
- Mock console capturing collects `log`, `info`, `warn`, and `error` outputs during sandboxed execution [src/components/ide/prompt-ide.tsx:163-173]().
- Integrates with `RunPromptButton` ([src/components/ide/prompt-ide.tsx:12-12]()) to dispatch prompts to execution endpoints.

```mermaid
graph TD
    subgraph "Natural_Language_Space"
        A["UserPromptCode"]
    end
    subgraph "Code_Entity_Space"
        B["PromptIde_Component"] --> C["MonacoEditor_Instance"]
        C --> D["getTypeErrors()"]
        D --> E["TYPE_OPTIONS_Data"]
        B --> F["runCode()"]
        F --> G["useSession_Hook"]
        F --> H["DynamicImportAndEval_Mechanism"]
        H --> I["prompts.chat_Library"]
    end
    A --> B
```
**Diagram: Typed-Prompts IDE Data Flow & Execution**

Sources: [src/components/ide/prompt-ide.tsx:1-173](), [src/app/developers/page.tsx:1-7]()

---

## Prompt Builder & Enhancer
The Prompt Builder, located at `/developers`, is an AI-powered conversational interface designed to assist users in crafting and refining prompts.

### Features
- **Conversational Chat Interface:** Takes user input and updates the structured prompt state interactively [src/components/prompts/prompt-builder.tsx:125-136]().
- **AI Model Integration:** Posts message histories, current prompt states (`PromptBuilderState`), and available tags/categories to `/api/prompt-builder/chat` using `gpt-4o-mini` [src/components/prompts/prompt-builder.tsx:72-154]().
- **Tool Calling Support:** Invokes backend tools like `search_prompts` within the assistant loop to retrieve relevant prompt references [src/components/prompts/prompt-builder.tsx:191-198]().
- **Streaming SSE Responses:** Parses incoming chunked data streams (`reader.read()`) handling `text`, `tool_call`, `state`, and `done` events [src/components/prompts/prompt-builder.tsx:161-207]().

Sources: [src/components/prompts/prompt-builder.tsx:1-207](), [src/app/developers/page.tsx:1-7]()

---

## Prompt Tokenizer
The Prompt Tokenizer tool at `/developers` calculates token estimates, context usage, and estimated execution costs.

### Features
- **Heuristic Token Estimation:** Computes character, word, line, and sentence counts via `calculateStats` and `estimateTokens` (~4 characters per token average) [src/components/developers/prompt-tokenizer.tsx:63-79]().
- **Cost & Context Calculations:** Computes context window utilization percentages and monetary costs based on input/output pricing configurations [src/components/developers/prompt-tokenizer.tsx:198-211]().
- **Visual Tokenization:** Uses `tokenizeForVisualization` to decorate subword boundaries directly inside the Monaco editor instance [src/components/developers/prompt-tokenizer.tsx:130-175]().
- **Persistence:** Stores user settings and analysis history in `localStorage` [src/components/developers/prompt-tokenizer.tsx:81-115]().

Sources: [src/components/developers/prompt-tokenizer.tsx:1-212](), [src/app/developers/page.tsx:1-7]()

---

## Embed Designer & `/embed` Page
The Embed Designer at `/developers` enables developers to generate customizable `<iframe>` snippets.

### Features
- **Interactive Configuration:** Configures parameters like prompt text, context lists, models, modes, thinking/reasoning toggles, colors, and file trees [src/components/developers/embed-designer.tsx:25-47]().
- **Query Parameter Parsing:** The `/embed` page extracts search parameters via `useSearchParams` to hydrate `EmbedConfig` objects [src/app/embed/page.tsx:84-109]().
- **File Tree & Context Rendering:** Recursively builds hierarchical file trees via `buildFileTree` and renders context reference pills [src/app/embed/page.tsx:15-59, 166-194]().
- **Theme Synchronization:** Dynamically applies or removes the `dark` CSS class on document elements according to `themeMode` and system color schemes [src/app/embed/page.tsx:111-128]().
- **Example Loading:** Provides predefined `EMBED_EXAMPLES` to quickly populate the designer with common configurations [src/components/developers/embed-designer.tsx:22-23](), [src/components/developers/embed-examples.ts:31-385]().

Sources: [src/app/embed/page.tsx:1-194](), [src/components/developers/embed-designer.tsx:1-198](), [src/components/developers/embed-examples.ts:1-385](), [src/app/developers/page.tsx:1-7]()

---

## Raw Prompt API & Proxy
The Raw Prompt API serves prompt content in Markdown or YAML format, utilizing Next.js middleware for clean URLs.

### Implementation Details
- **Middleware Proxy Routing:** `src/proxy.ts` intercepts requests matching `.prompt.md`, `.prompt.yml`, and `.SKILL.md` suffixes and rewrites them to `/api/prompts/[id]/raw` [src/proxy.ts:7-12]().
- **ID and Format Parsing:** `parseIdParam` extracts the prompt ID, output format (`md` or `yml`), and file type (`prompt` or `skill`) [src/app/api/prompts/[id]/raw/route.ts:12-36]().
- **Variable Conversion:** Automatically converts `${variable:default}` placeholders to `{{variable}}` syntax for template compatibility [src/app/api/prompts/[id]/raw/route.ts:41-43]().
- **Database Query & Response:** Queries `db.prompt.findFirst` for public, non-deleted prompts and returns plain text or YAML responses with correct `Content-Type` headers [src/app/api/prompts/[id]/raw/route.ts:63-124]().
- **Download Dropdown:** The `DownloadPromptDropdown` component provides UI for downloading prompts in `.md` or `.yml` formats, or copying their raw URLs [src/components/prompts/download-prompt-dropdown.tsx:1-180]().

```mermaid
graph TD
    subgraph "Natural_Language_Space"
        A["ClientRequestWithCleanUrl"]
    end
    subgraph "Code_Entity_Space"
        B["src/proxy.ts"] --> C["RewriteRule"]
        C --> D["/api/prompts/[id]/raw/route.ts"]
        D --> E["parseIdParam()"]
        D --> F["db.prompt.findFirst()"]
        F --> G["convertVariables()"]
        G --> H["yamlEscape() / FrontmatterBuilder"]
        H --> I["NextResponse.withContentType()"]
    end
    A --> B
```
**Diagram: Raw Prompt API & Proxy Routing Architecture**

Sources: [src/proxy.ts:1-29](), [src/app/api/prompts/[id]/raw/route.ts:1-124](), [src/components/prompts/download-prompt-dropdown.tsx:1-180]()

---

# Summary
The Typed-Prompts IDE & Embeds suite provides robust developer tooling:
- The **Typed-Prompts IDE** offers interactive TypeScript evaluation using `prompts.chat`.
- The **Prompt Builder** supplies conversational AI prompt structuring.
- The **Prompt Tokenizer** evaluates token budgets and cost metrics.
- The **Embed Designer** and `/embed` page facilitate external component embedding.
- The **Raw Prompt API** and middleware proxy enable programmatic retrieval of raw prompt formats.

Sources: [src/components/ide/prompt-ide.tsx:1-173](), [src/components/prompts/prompt-builder.tsx:1-207](), [src/components/developers/prompt-tokenizer.tsx:1-212](), [src/app/embed/page.tsx:1-194](), [src/proxy.ts:1-29](), [src/app/api/prompts/[id]/raw/route.ts:1-124]()

---

# Page: Configuration & Customization

# Configuration & Customization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [prompts.config.ts](prompts.config.ts)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



This page serves as the parent overview for configuration and customization options in `prompts.chat`. It introduces the primary configuration domains, runtime override mechanics, and design systems, linking out to detailed child pages for deeper technical implementation [src/lib/config/index.ts:1-185](), [prompts.config.ts:1-104]().

---

## Configuration Architecture & Loading Pipeline

The configuration framework processes settings through a multi-step pipeline combining build-time static files and runtime environment variable overrides. Configurations are declared using `defineConfig` in `prompts.config.ts` [prompts.config.ts:1-6](), parsed via `getConfig()` [src/lib/config/index.ts:187-198](), and overridden by `PCHAT_*` environment variables for zero-rebuild container deployments [src/lib/config/index.ts:117-185]().

Title: "Configuration Loading and Override Pipeline"
```mermaid
graph TB
subgraph "Code Entity Space"
    ConfigFile["prompts.config.ts"]
    DefineConfig["defineConfig()"]
    ApplyEnv["applyEnvOverrides()"]
    Cache["cachedConfig"]
    GetConfig["getConfig()"]
    BrandingProv["BrandingProvider"]
end
subgraph "Natural Language Space"
    UserConfig["User Configuration File"]
    EnvOverrides["Runtime Environment Variables PCHAT_*"]
    AppComponents["Application UI & Server Components"]
end
UserConfig --> ConfigFile
ConfigFile --> DefineConfig
DefineConfig --> ApplyEnv
EnvOverrides --> ApplyEnv
ApplyEnv --> Cache
Cache --> GetConfig
GetConfig --> BrandingProv
BrandingProv --> AppComponents
```
Sources: [src/lib/config/index.ts:97-185](), [prompts.config.ts:1-104]()

---

## Configuration Domains & Schema

The configuration shape is defined by the `PromptsConfig` interface and broken down into distinct functional domains covering branding, themes, authentication, internationalization, feature flags, and homepage layouts [src/lib/config/index.ts:86-95]().

Title: "Configuration Domains Mapping to PromptsConfig"
```mermaid
graph LR
subgraph "Code Entity Space"
    PromptsConfig["PromptsConfig"]
    BrandingConfig["BrandingConfig"]
    ThemeConfig["ThemeConfig"]
    AuthConfig["AuthConfig"]
    I18nConfig["I18nConfig"]
    FeaturesConfig["FeaturesConfig"]
    HomepageConfig["HomepageConfig"]
end
subgraph "Natural Language Space"
    DomainBranding["Branding & Identity"]
    DomainTheme["Theming & Design Tokens"]
    DomainAuth["Authentication Providers"]
    DomainI18n["Localization & Locales"]
    DomainFeatures["Feature Toggles"]
    DomainHomepage["Homepage Customization"]
end
DomainBranding --> PromptsConfig
DomainTheme --> PromptsConfig
DomainAuth --> PromptsConfig
DomainI18n --> PromptsConfig
DomainFeatures --> PromptsConfig
DomainHomepage --> PromptsConfig
PromptsConfig --> BrandingConfig
PromptsConfig --> ThemeConfig
PromptsConfig --> AuthConfig
PromptsConfig --> I18nConfig
PromptsConfig --> FeaturesConfig
PromptsConfig --> HomepageConfig
```
Sources: [src/lib/config/index.ts:1-96]()

---

## Branding Customization

Branding configuration defines application identity elements such as application name, light/dark logos, favicons, descriptions, and external marketplace links [src/lib/config/index.ts:1-9](). These values propagate through components like `<Header />` and runtime providers [src/components/layout/header.tsx:115-178]().

For detailed branding configuration, see [Branding Customization](#12.2).

Sources: [prompts.config.ts:8-18](), [src/lib/config/index.ts:1-9](), [src/components/layout/header.tsx:115-178]()

---

## Theme Configuration

The theme domain controls border radii (`none`, `sm`, `md`, `lg`), visual variants (`flat`, `default`, `brutal`), layout density (`compact`, `default`, `comfortable`), and color tokens (`primary`, `secondary`, `accent`) [src/lib/config/index.ts:11-22](). These tokens are converted dynamically into CSS custom properties and OKLCH color spaces [src/app/layout.tsx:113-172]().

For a comprehensive explanation of theme setting options and color conversions, see [Theme Configuration](#12.3).

Sources: [prompts.config.ts:21-32](), [src/lib/config/index.ts:11-22](), [src/app/layout.tsx:113-172]()

---

## Feature Flags

Features are controlled via boolean flags within the configuration profile, allowing deployments to toggle capabilities such as private prompts, change requests, categorization, tagging, AI semantic search, AI generation, MCP protocol support, and comments [src/lib/config/index.ts:39-48]().

For details on feature flag usage and effects, see [Feature Flags](#12.4).

Sources: [prompts.config.ts:50-67](), [src/lib/config/index.ts:39-48]()

---

## White-labeling & Clone Branding

The `useCloneBranding` flag allows deployments to suppress official repository links, achievement badges, and sponsor listings, rendering a clean white-labeled instance [src/lib/config/index.ts:58-68](). When enabled or triggered via `PCHAT_NAME`, secondary community elements are hidden across the layout and announcement bars [prompts.config.ts:70-91](), [src/lib/config/index.ts:177-182](), [src/components/layout/announcement-banner.tsx:30-32]().

For instructions on achieving full white-labeling, see [White-labeling & Clone Branding](#12.5).

Sources: [src/lib/config/index.ts:58-68, 177-182](), [prompts.config.ts:4, 70-91](), [src/components/layout/announcement-banner.tsx:30-32]()

---

## Child Pages

For deep technical details on each domain, consult the following child pages:

- [Configuration Overview](#12.1) — Explain `prompts.config.ts` structure, `defineConfig`, configuration domains, and loading pipeline
- [Branding Customization](#12.2) — Document branding parameters and asset rendering across the UI
- [Theme Configuration](#12.3) — Explain theme properties, design tokens, and color conversions
- [Feature Flags](#12.4) — Document feature config variables and functional impacts
- [White-labeling & Clone Branding](#12.5) — Explain `useCloneBranding` and white-label setup procedures

---

# Page: Configuration Overview

# Configuration Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [prisma/reset-admin.ts](prisma/reset-admin.ts)
- [prompts.config.ts](prompts.config.ts)
- [scripts/setup.js](scripts/setup.js)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



This page provides an overview of prompts.chat's configuration system, explaining how the application is configured through `prompts.config.ts`, environment variable overrides, and the multi-stage configuration loading pipeline.

## Purpose and Scope

The configuration system enables extensive customization of prompts.chat to serve different deployment needs:

- **SaaS Mode**: Public prompts.chat instance with default branding and full features.
- **Self-Hosted Mode**: Custom instance with user-defined branding, authentication, and feature sets.
- **White-Label Mode**: Fully rebranded copy hiding all references to prompts.chat, enabled via the `useCloneBranding` flag.

Configurations are primarily declared in the central `prompts.config.ts` file using a type-safe approach with the `defineConfig` function. At runtime, environment variables prefixed with `PCHAT_` allow overrides without recompilation, supporting flexible, container-friendly deployments [prompts.config.ts:1-106](), [src/lib/config/index.ts:98-187]().

Sources: [prompts.config.ts:1-106](), [src/lib/config/index.ts:98-187]()

---

## Configuration File Structure

The core configuration resides in `prompts.config.ts` at the project root. It exports a configuration object describing six primary domains: branding, theme, auth, i18n, features, and homepage [prompts.config.ts:6-106]().

```typescript
import { defineConfig } from "@/lib/config";

export default defineConfig({
  branding: { /* branding settings */ },
  theme: { /* theme design tokens */ },
  auth: { /* authentication providers */ },
  i18n: { /* internationalization */ },
  features: { /* feature toggles */ },
  homepage: { /* homepage customization */ },
});
```

This file uses TypeScript for compile-time type checking and developer experience improvements. The `defineConfig` function itself is a simple pass-through that provides typing hints [prompts.config.ts:1-106](), [src/lib/config/index.ts:98-100]().

Sources: [prompts.config.ts:1-106](), [src/lib/config/index.ts:98-100]()

---

## Configuration Domains

The configuration is typed using the `PromptsConfig` interface, which composes multiple domain-specific interfaces [src/lib/config/index.ts:87-96](). These domains organize concerns logically and enable modular customization.

### Domain Composition Diagram

Title: "PromptsConfig Domain Architecture"
```mermaid
graph TB
    PromptsConfig["PromptsConfig"]
    BrandingConfig["branding: BrandingConfig"]
    ThemeConfig["theme: ThemeConfig"]
    AuthConfig["auth: AuthConfig"]
    I18nConfig["i18n: I18nConfig"]
    FeaturesConfig["features: FeaturesConfig"]
    HomepageConfig["homepage: HomepageConfig"]
    AnnouncementConfig["announcement?: AnnouncementConfig | null"]

    PromptsConfig --> BrandingConfig
    PromptsConfig --> ThemeConfig
    PromptsConfig --> AuthConfig
    PromptsConfig --> I18nConfig
    PromptsConfig --> FeaturesConfig
    PromptsConfig --> HomepageConfig
    PromptsConfig --> AnnouncementConfig

    subgraph BrandingDetails
      BrandingName["name: string"]
      BrandingLogo["logo: string"]
      BrandingFavicon["favicon: string"]
      BrandingAppStore["appStoreUrl?: string"]
      BrandingChromeExt["chromeExtensionUrl?: string"]
    end
    BrandingConfig --> BrandingName
    BrandingConfig --> BrandingLogo
    BrandingConfig --> BrandingFavicon
    BrandingConfig --> BrandingAppStore
    BrandingConfig --> BrandingChromeExt

    subgraph ThemeDetails
      Radius["radius: 'none' | 'sm' | 'md' | 'lg'"]
      Variant["variant: 'flat' | 'default' | 'brutal'"]
      Density["density: 'compact' | 'default' | 'comfortable'"]
      Colors["colors: { primary: string, secondary?: string, accent?: string }"]
    end
    ThemeConfig --> Radius
    ThemeConfig --> Variant
    ThemeConfig --> Density
    ThemeConfig --> Colors

    subgraph FeaturesDetails
      PrivatePrompts["privatePrompts: boolean"]
      ChangeRequests["changeRequests: boolean"]
      Categories["categories: boolean"]
      Tags["tags: boolean"]
      AISearch["aiSearch?: boolean"]
      AIGeneration["aiGeneration?: boolean"]
      MCP["mcp?: boolean"]
      Comments["comments?: boolean"]
      PromptEnhancer["promptEnhancer?: boolean"]
    end
    FeaturesConfig --> PrivatePrompts
    FeaturesConfig --> ChangeRequests
    FeaturesConfig --> Categories
    FeaturesConfig --> Tags
    FeaturesConfig --> AISearch
    FeaturesConfig --> AIGeneration
    FeaturesConfig --> MCP
    FeaturesConfig --> Comments
    FeaturesConfig --> PromptEnhancer

    subgraph HomepageDetails
      UseCloneBranding["useCloneBranding?: boolean"]
      Achievements["achievements?: { enabled: boolean }"]
      Sponsors["sponsors?: { enabled: boolean, items: Sponsor[] }"]
    end
    HomepageConfig --> UseCloneBranding
    HomepageConfig --> Achievements
    HomepageConfig --> Sponsors

    subgraph AnnouncementDetails
      AnnouncementId["id: string"]
      AnnouncementMessage["message: string"]
      AnnouncementMessageShort["messageShort?: string"]
      AnnouncementHref["href?: string"]
      AnnouncementExternal["external?: boolean"]
      AnnouncementCta["cta?: string"]
    end
    AnnouncementConfig --> AnnouncementId
    AnnouncementConfig --> AnnouncementMessage
    AnnouncementConfig --> AnnouncementMessageShort
    AnnouncementConfig --> AnnouncementHref
    AnnouncementConfig --> AnnouncementExternal
    AnnouncementConfig --> AnnouncementCta
```

Sources: [src/lib/config/index.ts:1-96](), [prompts.config.ts:6-106]()

### Domain Descriptions

| Domain         | Interface Name      | Purpose                                                                                               |
|----------------|---------------------|-----------------------------------------------------------------------------------------------------|
| `branding`     | `BrandingConfig`    | Define app identity: name, logo URLs (light/dark), favicon, descriptions, store URLs [src/lib/config/index.ts:1-9]().          |
| `theme`        | `ThemeConfig`       | UI design tokens: border radius, visual variant, density, and colors [src/lib/config/index.ts:11-22]().                       |
| `auth`         | `AuthConfig`        | Authentication providers array and registration toggle [src/lib/config/index.ts:26-32]().                                     |
| `i18n`         | `I18nConfig`        | Supported locales and default language code [src/lib/config/index.ts:34-37]().                                               |
| `features`     | `FeaturesConfig`    | Feature flags enabling/disabling modules like private prompts or MCP [src/lib/config/index.ts:39-49]().                       |
| `homepage`     | `HomepageConfig`    | White-label controls, achievements, sponsors visibility [src/lib/config/index.ts:59-69]().                                    |
| `announcement` | `AnnouncementConfig`| Site-wide announcement bar configuration [src/lib/config/index.ts:71-85]().                                                 |

Sources: [src/lib/config/index.ts:1-96](), [prompts.config.ts:6-106]()

---

## Configuration Loading Pipeline

The application loads configuration in a layered manner combining a user config file, environment variable overrides, and caching [src/lib/config/index.ts:189-248]().

### Loading Sequence Diagram

Title: "getConfig Pipeline Execution Flow"
```mermaid
sequenceDiagram
    participant App as "Next.js App"
    participant GetConfig as "getConfig()"
    participant Cache as "cachedConfig"
    participant UserConfigFile as "prompts.config.ts"
    participant EnvOverrides as "applyEnvOverrides()"

    App->>GetConfig: Request configuration
    GetConfig->>Cache: Check cachedConfig
    alt Cache miss
        GetConfig->>UserConfigFile: Dynamic import('@/../prompts.config')
        alt Import success
            UserConfigFile-->>GetConfig: Return user config object
        else Import failure
            GetConfig-->>GetConfig: Use built-in fallback config
        end
        GetConfig->>EnvOverrides: Merge environment overrides (PCHAT_*)
        EnvOverrides-->>GetConfig: Return merged config
        GetConfig->>Cache: Store in cachedConfig
    end
    GetConfig-->>App: Return final PromptsConfig
```

Sources: [src/lib/config/index.ts:189-248]()

### Pipeline Steps

1.  **File Import**: Dynamically imports the user-defined `prompts.config.ts` file. If missing or import errors occur, falls back to a hardcoded default configuration [src/lib/config/index.ts:189-248]().
2.  **Environment Variable Overrides**: The `applyEnvOverrides` function processes `process.env` for keys beginning with `PCHAT_` and overrides corresponding config values if set. Supported environment variables cover all config domains and allow seamless customization in deployment environments [src/lib/config/index.ts:118-187]().
3.  **Caching**: The resulting config object is cached in `cachedConfig` to avoid repeated file reads and reprocessing in the same server instance session [src/lib/config/index.ts:103]().

Sources: [src/lib/config/index.ts:103](), [src/lib/config/index.ts:118-248]()

---

## Runtime Configuration Access

### Server-Side

Server components and API routes asynchronously fetch runtime configuration via the `getConfig()` function [src/lib/config/index.ts:189-248]():

```typescript
const config = await getConfig();
const primaryColor = config.theme.colors.primary;
```

This enables access to the merged config with environment overrides applied [src/lib/config/index.ts:189-248]().

### Client-Side

Client components do not perform async imports of the config. Instead, they use reactive context providers such as `BrandingProvider` hooked by the `useBranding` React hook which reads branding info transparently from loaded config [src/components/layout/header.tsx:80](). The themes are handled similarly by the theming provider using `useTheme()` [src/components/layout/header.tsx:115]().

Sources: [src/lib/config/index.ts:189-248](), [src/components/layout/header.tsx:80](), [src/components/layout/header.tsx:115]()

---

## Environment Variable Overrides

The config system supports fine-grained environment variable overrides prefixed with `PCHAT_`. This allows docker-compose or cloud deployments to change settings without modifying source files [src/lib/config/index.ts:118-187]().

### Parsing Helpers

-   `envBool(key, fallback)` interprets `"true"`, `"false"`, `"1"`, `"0"` strings as boolean [src/lib/config/index.ts:122-126]().
-   `envArray(key, fallback)` parses comma-separated strings into string arrays [src/lib/config/index.ts:128-132]().

### Environment Variable to Config Mapping

| Env Variable                    | Config Path                          | Notes                               |
|---------------------------------|--------------------------------------|-------------------------------------|
| `PCHAT_NAME`                    | `branding.name`                      | Custom app name [src/lib/config/index.ts:136]() |
| `PCHAT_DESCRIPTION`             | `branding.description`               | App short description [src/lib/config/index.ts:137]() |
| `PCHAT_LOGO`                    | `branding.logo`                      | Light logo URL [src/lib/config/index.ts:138]() |
| `PCHAT_LOGO_DARK`               | `branding.logoDark`                  | Dark mode logo URL [src/lib/config/index.ts:139]() |
| `PCHAT_FAVICON`                 | `branding.favicon`                   | Browser favicon [src/lib/config/index.ts:140]() |
| `PCHAT_COLOR`                   | `theme.colors.primary`               | Primary color hex or oklch [src/lib/config/index.ts:149]() |
| `PCHAT_THEME_RADIUS`            | `theme.radius`                       | UI border radius [src/lib/config/index.ts:145]() |
| `PCHAT_THEME_VARIANT`           | `theme.variant`                      | UI style variant [src/lib/config/index.ts:146]() |
| `PCHAT_THEME_DENSITY`           | `theme.density`                      | UI density [src/lib/config/index.ts:147]() |
| `PCHAT_AUTH_PROVIDERS`          | `auth.providers`                     | Comma-separated list [src/lib/config/index.ts:155-157]() |
| `PCHAT_ALLOW_REGISTRATION`      | `auth.allowRegistration`             | Boolean [src/lib/config/index.ts:158-160]() |
| `PCHAT_LOCALES`                 | `i18n.locales`                       | Comma-separated list [src/lib/config/index.ts:163-165]() |
| `PCHAT_DEFAULT_LOCALE`          | `i18n.defaultLocale`                 | Default locale code [src/lib/config/index.ts:166]() |
| `PCHAT_FEATURE_PRIVATE_PROMPTS` | `features.privatePrompts`            | Boolean [src/lib/config/index.ts:169]() |
| `PCHAT_FEATURE_CHANGE_REQUESTS` | `features.changeRequests`            | Boolean [src/lib/config/index.ts:170]() |
| `PCHAT_FEATURE_CATEGORIES`      | `features.categories`                | Boolean [src/lib/config/index.ts:171]() |
| `PCHAT_FEATURE_TAGS`            | `features.tags`                      | Boolean [src/lib/config/index.ts:172]() |
| `PCHAT_FEATURE_AI_SEARCH`       | `features.aiSearch`                  | Boolean [src/lib/config/index.ts:173]() |
| `PCHAT_FEATURE_AI_GENERATION`   | `features.aiGeneration`              | Boolean [src/lib/config/index.ts:174]() |
| `PCHAT_FEATURE_MCP`             | `features.mcp`                       | Boolean [src/lib/config/index.ts:175]() |
| `PCHAT_FEATURE_COMMENTS`        | `features.comments`                  | Boolean [src/lib/config/index.ts:176]() |
| `PCHAT_FEATURE_PROMPT_ENHANCER` | `features.promptEnhancer`            | Boolean [src/lib/config/index.ts:177]() |

### Special Behavior

-   If `PCHAT_NAME` is set via environment, the homepage configuration automatically switches to `useCloneBranding: true` mode, disabling prompts.chat's default achievements and sponsors to facilitate white-labeling on the fly [src/lib/config/index.ts:179-184]().

Sources: [src/lib/config/index.ts:118-187]()

---

## Internationalization Configuration

The `i18n` domain defines the supported locales and the default language. This setting must be aligned with the internal translation system and locale detection [prompts.config.ts:43-47](), [src/lib/i18n/config.ts:4-6]().

```typescript
i18n: {
  locales: [
    "en", "tr", "es", "zh", "ja",
    "ar", "pt", "fr", "it", "de",
    "nl", "ko", "ru", "he", "el",
    "az", "fa",
  ],
  defaultLocale: "en",
},
```

### Right-to-Left Language Support

The system automatically handles RTL languages using the hardcoded list of right-to-left locales [src/lib/i18n/config.ts:8-14]():

```typescript
const rtlLocales = ["ar", "he", "fa"];
function isRtlLocale(locale: string): boolean {
  return rtlLocales.includes(locale);
}
```

Client code such as the root HTML layout dynamically sets the `dir` attribute based on the current locale's RTL status [src/lib/i18n/config.ts:1-24]().

Sources: [prompts.config.ts:43-47](), [src/lib/i18n/config.ts:1-24]()

---

## Configuration Logic Entity Map

The following diagram links natural language configuration concepts to concrete code artifacts handling them in prompts.chat:

Title: "Configuration Entity and Code Mapping"
```mermaid
graph LR
    UserIntent["DefineAppSetting"] -- "Written To" --> ConfigFile["prompts.config.ts"]
    ConfigFile -- "Wrapped By" --> DefineFn["defineConfig()"]
    DefineFn -- "Typed As" --> ConfigInterfaces["PromptsConfig Interface\n(src/lib/config/index.ts)"]

    RuntimeEnv["Environment Variables\n(PCHAT_*)"] -- "Parsed By" --> EnvLogic["applyEnvOverrides()"]

    ConfigFile -- "Imported By" --> GetConfig["getConfig() Function"]
    EnvLogic -- "Called By" --> GetConfig

    GetConfig -- "Caches In" --> Cache["cachedConfig Variable"]

    subgraph ClientComponents
        HeaderComp["Header Component\n(src/components/layout/header.tsx)"] -- "Uses" --> BrandingHook["useBranding() Hook"]
        BrandingHook -- "Reads From" --> Cache
        AnnouncementBannerComp["AnnouncementBanner Component\n(src/components/layout/announcement-banner.tsx)"] -- "Uses" --> BrandingHook
        AnnouncementBannerComp -- "Uses" --> AnnouncementConfig["announcement?: AnnouncementConfig"]
    end

    subgraph ServerComponents
        RootLayout["RootLayout Component\n(src/app/layout.tsx)"] -- "Calls" --> GetConfig
        RootLayout -- "Applies" --> ThemeStyles["CSS Custom Properties\n(--radius, --primary)"]
        RootLayout -- "Sets" --> HtmlDir["HTML dir attribute"]
    end
```

Sources: [prompts.config.ts:1-6](), [src/lib/config/index.ts:87-103](), [src/lib/config/index.ts:118-187](), [src/components/layout/header.tsx:80](), [src/components/layout/announcement-banner.tsx:10-14](), [src/app/layout.tsx:156](), [src/app/layout.tsx:169-172](), [src/app/layout.tsx:179]()

---

# Page: Branding Customization

# Branding Customization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [prompts.config.ts](prompts.config.ts)
- [public/favicon/apple-touch-icon.png](public/favicon/apple-touch-icon.png)
- [public/favicon/favicon-96x96.png](public/favicon/favicon-96x96.png)
- [public/favicon/favicon.ico](public/favicon/favicon.ico)
- [public/favicon/favicon.svg](public/favicon/favicon.svg)
- [public/favicon/site.webmanifest](public/favicon/site.webmanifest)
- [public/favicon/web-app-manifest-192x192.png](public/favicon/web-app-manifest-192x192.png)
- [public/favicon/web-app-manifest-512x512.png](public/favicon/web-app-manifest-512x512.png)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)
- [tsconfig.json](tsconfig.json)

</details>



## Purpose and Scope

This document covers the **branding customization system** in prompts.chat, which controls the application's visual identity including name, logo (light/dark), description, favicon, and external store links. Branding settings define how your deployment appears to users across all pages and key UI components.

For additional context about configuration loading and environment overrides, see **12.1 Configuration Overview**. For detailed theming properties affecting colors and shapes, see **12.3 Theme Configuration**. For instructions on fully white-labeling or hiding original prompts.chat branding, see **12.5 White-labeling & Clone Branding**.

Sources: [prompts.config.ts:8-18](), [src/lib/config/index.ts:1-9]()

---

## Branding Configuration Structure

Branding customization is implemented as a structured configuration object conforming to the interface `BrandingConfig` defined in the TypeScript declarations at [src/lib/config/index.ts:1-9](). This interface specifies the following fields:

- `name`: string — Application display name
- `logo`: string — The logo URI for light mode (e.g., `/logo.svg`)
- `logoDark?`: string — Optional logo URI for dark mode (fallback to `logo`)
- `favicon`: string — URI of the favicon asset (shown in browser tabs)
- `description`: string — A short descriptive text used in meta tags and homepage
- `appStoreUrl?`: string — Optional URL to Mac App Store listing
- `chromeExtensionUrl?`: string — Optional URL to Chrome Web Store listing

The configuration is instantiated in the root `prompts.config.ts` file under the `branding` key [prompts.config.ts:8-18]().

### Branding Configuration Data Flow

```mermaid
graph TB
    prompts_config["prompts.config.ts"]
    BrandingConfig["BrandingConfig<br/>src/lib/config/index.ts:1-9"]
    PCHAT_ENV["process.env<br/>PCHAT_NAME, PCHAT_LOGO"]
    applyEnvOverrides["applyEnvOverrides()<br/>src/lib/config/index.ts:117-185"]
    getConfig["getConfig()<br/>src/lib/config/index.ts:187"]
    cachedConfig["cachedConfig<br/>singleton"]
    
    prompts_config -->|"conforms to"| BrandingConfig
    prompts_config -->|"imported by"| getConfig
    PCHAT_ENV -->|"processed by"| applyEnvOverrides
    getConfig -->|"applies"| applyEnvOverrides
    getConfig -->|"stores in"| cachedConfig
    
    subgraph "BrandingConfig_Fields"
        name["name: string"]
        logo["logo: string"]
        logoDark["logoDark?: string"]
        favicon["favicon: string"]
        description["description: string"]
        appStoreUrl["appStoreUrl?: string"]
        chromeExtensionUrl["chromeExtensionUrl?: string"]
    end
    
    BrandingConfig --> name
    BrandingConfig --> logo
    BrandingConfig --> logoDark
    BrandingConfig --> favicon
    BrandingConfig --> description
    BrandingConfig --> appStoreUrl
    BrandingConfig --> chromeExtensionUrl
    
    cachedConfig -->|"client context"| useBranding["useBranding()<br/>src/components/layout/header.tsx:80"]
    cachedConfig -->|"server access"| ServerComponents["ServerComponents<br/>await getConfig()"]
```

Sources: [src/lib/config/index.ts:1-9](), [src/lib/config/index.ts:70-84](), [src/lib/config/index.ts:117-185](), [src/lib/config/index.ts:187](), [prompts.config.ts:8-18]()

---

## Configuration Interface

The `BrandingConfig` interface fully defines the expected branding properties, each serving a clear visual or functional purpose:

| Field | Type | Required | Description |
| :------------------ | :------- | :------- | :----------------------------------------------------------- |
| `name` | `string` | Yes | Application name displayed in header, title, and throughout UI |
| `logo` | `string` | Yes | Path to light theme logo (relative to `/public`) |
| `logoDark` | `string` | No | Path to dark theme logo (defaults to `logo` if omitted) |
| `favicon` | `string` | Yes | Path to favicon asset used in browser tabs |
| `description` | `string` | Yes | Short descriptive text for meta tags and homepage |
| `appStoreUrl` | `string` | No | URL to Mac App Store; if set, shows App Store button |
| `chromeExtensionUrl` | `string` | No | URL to Chrome Web Store; if set, shows extension button |

Sources: [src/lib/config/index.ts:1-9]()

---

## Setting Branding in Config File

Branding customization is controlled by editing the `branding` object in your `prompts.config.ts` file as shown below:

```typescript
export default defineConfig({
  branding: {
    name: "prompts.chat",
    logo: "/logo.svg",
    logoDark: "/logo-dark.svg",
    favicon: "/logo.svg",
    description: "Collect, organize, and share AI prompts",
    
    // Optional: Delete this if useCloneBranding is true
    appStoreUrl: "https://apps.apple.com/tr/app/prompts-chat/id6756895736",
    chromeExtensionUrl: "https://chromewebstore.google.com/detail/promptschat/eemdohkhbaifiocagjlhibfbhamlbeej",
  },
  // ... other config sections
});
```

### Logo Recommendations
- **Format:** SVG logos are recommended for scalability and crisp display.
- **Light logo:** Typically used on light backgrounds.
- **Dark logo:** Optional logo to use under dark theme; falls back to `logo` if missing.
- **Display size:** Logos in the header are usually rendered at compact heights.

Sources: [prompts.config.ts:8-18](), [src/components/layout/header.tsx:160-175]()

---

## Environment Variable Overrides

Branding values can be overridden at runtime using environment variables prefixed with `PCHAT_`. The function `applyEnvOverrides()` in [src/lib/config/index.ts:117-185]() performs this override logic, allowing Docker or cloud deployments to adjust branding without recompilation.

| Environment Variable | Field Overridden | Type | Fallback |
| :------------------- | :--------------- | :----- | :------------------------------------------ |
| `PCHAT_NAME` | `branding.name` | string | Config default |
| `PCHAT_DESCRIPTION` | `branding.description` | string | Config default |
| `PCHAT_LOGO` | `branding.logo` | string | Config default |
| `PCHAT_LOGO_DARK` | `branding.logoDark` | string | Fallback to `PCHAT_LOGO` or config default |
| `PCHAT_FAVICON` | `branding.favicon` | string | Config default |

**Relevant override logic snippet:**

```typescript
branding: {
  name: env.PCHAT_NAME || config.branding.name,
  description: env.PCHAT_DESCRIPTION || config.branding.description,
  logo: env.PCHAT_LOGO || config.branding.logo,
  logoDark: env.PCHAT_LOGO_DARK || env.PCHAT_LOGO || config.branding.logoDark,
  favicon: env.PCHAT_FAVICON || config.branding.favicon,
  appStoreUrl: config.branding.appStoreUrl,
  chromeExtensionUrl: config.branding.chromeExtensionUrl,
}
```

### Auto-Clone Mode Trigger

If `PCHAT_NAME` is set (indicating custom runtime branding), the system auto-enables clone branding by setting `useCloneBranding: true` in the homepage config [src/lib/config/index.ts:177-184](), hiding default achievements and sponsors to respect white-labeling needs.

Sources: [src/lib/config/index.ts:117-185](), [src/lib/config/index.ts:177-184]()

---

## Configuration Loading Pipeline

The branding config flows through multiple layers before reaching UI components.

```mermaid
graph TB
    subgraph "Configuration_Sources"
        prompts_config_ts["prompts.config.ts"]
        process_env["process.env (PCHAT_*)"]
    end
    
    subgraph "Loading_Pipeline"
        getConfig_func["getConfig()<br/>src/lib/config/index.ts:187"]
        import_config["dynamic import<br/>@/../prompts.config"]
        fallback_config["fallback default config<br/>src/lib/config/index.ts:198"]
        applyEnvOverrides_func["applyEnvOverrides()<br/>src/lib/config/index.ts:117"]
        cachedConfig_var["cachedConfig<br/>module-level singleton"]
    end
    
    prompts_config_ts -->|"imported by"| import_config
    import_config -->|"success"| applyEnvOverrides_func
    import_config -->|"error"| fallback_config
    fallback_config -->|"provides base config"| applyEnvOverrides_func
    process_env -->|"read and applied by"| applyEnvOverrides_func
    applyEnvOverrides_func -->|"returns final config"| cachedConfig_var
    getConfig_func -->|"returns cached config"| cachedConfig_var
    
    subgraph "Server_Side_Consumers"
        ServerComponents["ServerComponents<br/>await getConfig()"]
        APIRoute["API Routes<br/>calls getConfig()"]
    end
    
    cachedConfig_var -->|"used by"| ServerComponents
    cachedConfig_var -->|"used by"| APIRoute
    
    subgraph "Client_Side_Consumers"
        RootLayout["RootLayout<br/>src/app/layout.tsx"]
        BrandingProvider_comp["Providers / BrandingProvider"]
        HeaderComponent["Header component<br/>src/components/layout/header.tsx"]
    end
    
    cachedConfig_var -->|"passed as props"| RootLayout
    RootLayout -->|"provides via context"| BrandingProvider_comp
    BrandingProvider_comp -->|"consumed by"| HeaderComponent
```

Key functions:
- `getConfig()` asynchronously loads user config, applies environment variable overrides, and caches it for reuse [src/lib/config/index.ts:189-248]().
- `applyEnvOverrides()` applies runtime environment-based configuration changes [src/lib/config/index.ts:117-187]().
- `useBranding()` is a React hook that retrieves branding config from context on client side [src/components/layout/header.tsx:80]().

Sources: [src/lib/config/index.ts:117-187](), [src/lib/config/index.ts:189-248]()

---

## Branding Usage in UI Components

### Header Component

The primary UI surface showing the brand name and logos is the `Header` component [src/components/layout/header.tsx:111](). It uses the `useBranding()` hook for accessing branding config dynamically [src/components/layout/header.tsx:80]().

```mermaid
graph TB
    Header["Header<br/>src/components/layout/header.tsx:111"]
    useBranding["useBranding()<br/>src/components/layout/header.tsx:80,116"]
    branding_var["branding (object)"]
    
    Header -->|"calls"| useBranding
    useBranding -->|"returns"| branding_var
    
    subgraph "Logo_Name_Rendering"
        LogoLink["Link href='/'"]
        ImageLight["<Image> src={branding.logo}<br/>class=dark:hidden"]
        ImageDark["<Image> src={branding.logoDark || branding.logo}<br/>class=hidden dark:block"]
        NameSpan["<span> branding.name"]
    end
    
    subgraph "Clipboard_Functionality"
        handleCopyLogoSvg["handleCopyLogoSvg() copies SVG logo to clipboard<br/>src/components/layout/header.tsx:160-170"]
    end
    
    branding_var -->|"provides data for"| LogoLink
    LogoLink --> ImageLight
    LogoLink --> ImageDark
    LogoLink --> NameSpan
    
    subgraph "Extension_Button_Conditional"
        browserType["State: browserType (chrome | firefox)"]
        extUrls["branding.chromeExtensionUrl"]
    end
    
    branding_var --> extUrls
    extUrls --> browserType
```

- Logos are conditionally rendered based on theme (dark/light) using the `logo` and `logoDark` URLs [src/components/layout/header.tsx:160-175]().
- `handleCopyLogoSvg` asynchronously fetches the SVG logo source and copies it to clipboard on demand [src/components/layout/header.tsx:160-170]().
- Browser detection logic (Chrome or Firefox) affects which browser extension link to render [src/components/layout/header.tsx:150-158]().

Sources: [src/components/layout/header.tsx:80](), [src/components/layout/header.tsx:111-178](), [src/components/layout/header.tsx:150-170]()

---

### Homepage Branding

The homepage leverages the `useCloneBranding` flag in the configuration to decide whether to display original prompts.chat branding or present a fully customized white-label identity.

Key behaviors:
- When `useCloneBranding` is **true**, repository branding elements such as achievements and sponsor widgets are hidden [prompts.config.ts:73-77]().
- Achievements visibility is controlled by `homepage.achievements.enabled` [prompts.config.ts:75-77]().
- Sponsors visibility and listing items are controlled by `homepage.sponsors.enabled` and `homepage.sponsors.items` [prompts.config.ts:78-92]().
- If a custom `PCHAT_NAME` environment variable is detected, the system auto-enables clone branding with achievements and sponsors disabled to maintain full white-label experience [src/lib/config/index.ts:179-184]().
- `appStoreUrl` and `chromeExtensionUrl` from branding config conditionally display respective external store buttons on supported UI segments [prompts.config.ts:16-17]().

Sources: [prompts.config.ts:4](), [prompts.config.ts:70-93](), [src/lib/config/index.ts:179-184]()

---

## Summary

The branding customization system provides centralized visual identity control over a prompts.chat instance with the following characteristics:

1.  **Configuration Setup:**
    Defined in the `branding` object within `prompts.config.ts`—includes name, logos, favicon, description, and optional external store links.

2.  **Environment Overrides:**
    `PCHAT_*` prefixed environment variables enable runtime overrides of branding config, especially useful for containerized deployments.

3.  **UI Integration:**
    Branding config is loaded server-side via `getConfig()`, passed to client root as props, provided via React context, and consumed primarily by the `Header` component and homepage layout to render consistent logos, titles, and store buttons.

4.  **Clone Branding Mode:**
    Automatically or manually enabled to remove original prompts.chat branding elements, supporting full white-label deployments.

This system enables both ease of customization and dynamic runtime branding changes without source modifications or recompilation.

Sources: [src/lib/config/index.ts](), [prompts.config.ts](), [src/components/layout/header.tsx]()

---

## Appendix: Code Entity Associations for Branding Customization

```mermaid
graph LR
    subgraph "Config_Layer"
        cfg_defineConfig["defineConfig()<br/>src/lib/config/index.ts:98"]
        cfg_applyEnvOverrides["applyEnvOverrides()<br/>src/lib/config/index.ts:118"]
        cfg_getConfig["getConfig()<br/>src/lib/config/index.ts:189"]
        cfg_BrandingConfig["BrandingConfig interface<br/>src/lib/config/index.ts:1"]
    end
    
    subgraph "UI_Layer"
        ui_RootLayout["RootLayout<br/>src/app/layout.tsx:144"]
        ui_BrandingProvider["Providers context<br/>src/components/providers/index.tsx"]
        ui_useBranding["useBranding() hook<br/>src/components/providers/branding-provider.tsx"]
        ui_Header["Header component<br/>src/components/layout/header.tsx:111"]
        ui_Homepage["Homepage components<br/>(affected by useCloneBranding)"]
    end
    
    cfg_defineConfig --> cfg_BrandingConfig
    cfg_applyEnvOverrides --> cfg_defineConfig
    cfg_getConfig --> cfg_applyEnvOverrides
    
    cfg_getConfig --> ui_RootLayout
    ui_RootLayout --> ui_BrandingProvider
    ui_BrandingProvider --> ui_useBranding
    ui_useBranding --> ui_Header
    ui_useBranding --> ui_Homepage
```

Sources: [prompts.config.ts:1-92](), [src/lib/config/index.ts:1-187](), [src/lib/config/index.ts:189-248](), [src/app/layout.tsx:144](), [src/components/layout/header.tsx]()

---

# Page: Theme Configuration

# Theme Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/globals.css](src/app/globals.css)
- [src/components/kids/elements/pixel-art.tsx](src/components/kids/elements/pixel-art.tsx)
- [src/components/kids/elements/progress-map.tsx](src/components/kids/elements/progress-map.tsx)
- [src/components/kids/elements/story-scene.tsx](src/components/kids/elements/story-scene.tsx)
- [src/components/kids/layout/settings-modal.tsx](src/components/kids/layout/settings-modal.tsx)
- [src/components/layout/animated-text.tsx](src/components/layout/animated-text.tsx)
- [src/components/prompts/hero-categories.tsx](src/components/prompts/hero-categories.tsx)

</details>



This page details the theme configuration system in `prompts.chat`, which controls the visual appearance of the application through border radius, UI variants, density, and color customization. Theme settings are defined in `prompts.config.ts` and processed at runtime to generate CSS custom properties and root classes.

---

## Theme Configuration Structure & Loading Pipeline

Theme configuration is declared within the `theme` object of `prompts.config.ts`. It manages four core design dimensions: border radius, UI variant, density, and primary color palette.

```typescript
// prompts.config.ts:21-32
theme: {
  radius: "sm",
  variant: "default",
  density: "default",
  colors: {
    primary: "#6366f1",
  },
},
```

At runtime, configuration is loaded by `getConfig()`, which merges user settings with environment variable overrides (e.g., `PCHAT_THEME_RADIUS`, `PCHAT_THEME_VARIANT`, `PCHAT_COLOR`) to allow zero-rebuild adjustments in containerized environments [src/lib/config/index.ts:117-152]().

### Theme Configuration Flow Diagram

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserConfig[""User-Defined Theme: Brutal Variant, Compact Density, #6366f1 Primary""]
    end

    subgraph "Code Entity Space"
        ConfigFile[""prompts.config.ts theme object""]
        GetConfig[""getConfig() function in src/lib/config/index.ts""]
        ApplyEnv[""applyEnvOverrides() in src/lib/config/index.ts""]
        RootLayout[""RootLayout component in src/app/layout.tsx""]
        HexConv[""hexToOklch() in src/app/layout.tsx""]
        GlobalCSS[""globals.css stylesheet rules""]
    end
    
    UserConfig --> ConfigFile
    ConfigFile --> GetConfig
    GetConfig --> ApplyEnv
    ApplyEnv --> RootLayout
    RootLayout --> HexConv
    RootLayout -- "Injects themeClasses" --> HTMLTag[""html class='theme-brutal density-compact'""]
    RootLayout -- "Injects themeStyles" --> HTMLStyle[""html style='--radius: 0; --primary: oklch(...)'""]
    HTMLTag --> GlobalCSS
    HTMLStyle --> GlobalCSS
```

Sources: [prompts.config.ts:21-32](), [src/lib/config/index.ts:117-152](), [src/app/layout.tsx:159-173](), [src/app/globals.css:158-208]()

---

## Border Radius Options

The `radius` property defines component corner rounding across the application. 

### Radius Values Mapping

The configuration keywords map directly to CSS `rem` values injected into the root element:

| Config Value | CSS `--radius` Value |
|--------------|---------------------|
| `none`       | `"0"`               |
| `sm`         | `"0.25rem"`         |
| `md`         | `"0.5rem"`          |
| `lg`         | `"0.75rem"`         |

In `src/app/globals.css`, derived radius variables scale relative to the base `--radius` variable [src/app/globals.css:43-46]:

```css
--radius-sm: calc(var(--radius) - 4px);
--radius-md: calc(var(--radius) - 2px);
--radius-lg: var(--radius);
--radius-xl: calc(var(--radius) + 4px);
```

Sources: [src/app/globals.css:43-46](), [src/lib/config/index.ts:13]()

---

## Theme Variants

The `variant` property controls shadow depth, border width, and styling behaviors. It injects a corresponding class (`.theme-{variant}`) into the root `<html>` element [src/app/layout.tsx:160]().

### Variant Specifications

| Variant   | Description                       | Shadows                                         | Borders                                             | Radius Override     |
|-----------|---------------------------------|-------------------------------------------------|-----------------------------------------------------|---------------------|
| `flat`    | Minimalist, no depth            | Set to `none` [src/app/globals.css:158-163]     | Subtle border tint                                  | None                |
| `default` | Standard elevation              | Soft multi-layered RGBA shadows                 | Standard 1px borders                                | None                |
| `brutal`  | High-contrast neo-brutalism     | Bold offset shadows using `currentColor`        | Thicker 2px solid borders                           | Forces radius `0`   |

Sources: [src/app/globals.css:158-208](), [src/lib/config/index.ts:14](), [src/app/layout.tsx:160]()

---

## Density Variants

The `density` property regulates layout spacing, font scaling, and padding scales via the `.density-{type}` class.

### Density Presets

| Density      | Base Font Size | Line Height | Heading h1 Size |
|--------------|----------------|-------------|-----------------|
| `compact`    | 0.875rem       | 1.25        | 1.5rem          |
| `default`    | 1rem           | 1.5         | Default         |
| `comfortable`| 1.125rem       | 1.75        | 2.5rem          |

These classes adjust spacing variables and container padding rules defined in `src/app/globals.css` [src/app/globals.css:213-245].

Sources: [src/app/globals.css:213-245](), [src/lib/config/index.ts:15]()

---

## Color Customization & hexToOklch Conversion

The theme engine accepts hex color values for `colors.primary` in `prompts.config.ts` and converts them to the OKLCH color space for perceptual uniformity and reliable contrast calculation [src/app/layout.tsx:120-142]().

### Conversion Pipeline

The `hexToOklch` function parses RGB components, calculates perceptual lightness ($l$), chroma ($c$), and hue ($h$), and outputs an OKLCH CSS string [src/app/layout.tsx:120-141](). If lightness exceeds `0.5`, a dark foreground (`oklch(0.2 0 0)`) is assigned; otherwise, a light foreground (`oklch(0.98 0 0)`) is used [src/app/layout.tsx:163-166]().

### Color Processing Flow Diagram

```mermaid
graph TD
    subgraph "Natural Language Space"
        HexInput[""HEX Color String (e.g., #6366f1)""]
    end

    subgraph "Code Entity Space"
        HexConv[""hexToOklch() function in src/app/layout.tsx""]
        LightnessCalc[""Lightness Evaluation Logic (r, g, b weights)""]
        ForegroundSelect[""Foreground Contrast Assignment""]
        CSSVars[""CSS Custom Properties (--primary, --primary-foreground)""]
    end

    HexInput --> HexConv
    HexConv --> LightnessCalc
    LightnessCalc --> ForegroundSelect
    LightnessCalc --> CSSVars
    ForegroundSelect --> CSSVars
```

Sources: [src/app/layout.tsx:120-172](), [prompts.config.ts:29-31]()

---

## Special Theme Implementations

### AnimatedText Component
The `AnimatedText` component implements continuous gradient text animations using keyframes defined in `src/app/globals.css` [src/components/layout/animated-text.tsx:8-28](), [src/app/globals.css:138-153]().

### Kids Section Pixel Art Theme
The `/kids` routes bypass the standard theme layout to use a custom pixel-art aesthetic [src/app/layout.tsx:152](). It features pixelated SVG rendering (`image-rendering: pixelated`) and custom polygon clipping paths [src/components/kids/layout/settings-modal.tsx:54-55](), [src/components/kids/elements/pixel-art.tsx:6-24]().

Sources: [src/components/layout/animated-text.tsx:8-28](), [src/app/globals.css:138-153](), [src/app/layout.tsx:152](), [src/components/kids/layout/settings-modal.tsx:54-55](), [src/components/kids/elements/pixel-art.tsx:6-24]()

---

# Page: Feature Flags

# Feature Flags

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [prisma/reset-admin.ts](prisma/reset-admin.ts)
- [prompts.config.ts](prompts.config.ts)
- [scripts/setup.js](scripts/setup.js)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/components/layout/announcement-banner.tsx](src/components/layout/announcement-banner.tsx)
- [src/components/layout/header.tsx](src/components/layout/header.tsx)
- [src/components/ui/masonry.tsx](src/components/ui/masonry.tsx)
- [src/lib/config/index.ts](src/lib/config/index.ts)
- [src/lib/db.ts](src/lib/db.ts)
- [src/lib/i18n/config.ts](src/lib/i18n/config.ts)

</details>



Feature flags control the enablement and disablement of major features in prompts.chat. They are configured in `prompts.config.ts` under the `features` key, and can be dynamically overridden at runtime through environment variables prefixed with `PCHAT_FEATURE_*`. This design allows flexible adaptation of the application to different deployment scenarios, such as public community use or private organizational clones.

These flags directly affect the application’s behavior, data model usage, UI rendering, available API routes, and integration features.

Sources:
[prompts.config.ts:49-69](), [src/lib/config/index.ts:39-49]()

---

## The `FeaturesConfig` Interface

The `FeaturesConfig` interface defines all toggleable features available in the system. It ensures type safety when accessing these flags in code via `getConfig()`.

```typescript
export interface FeaturesConfig {
  privatePrompts: boolean;   // Users can create private prompts
  changeRequests: boolean;   // Versioning and change request workflow enabled
  categories: boolean;       // Categories enabled for prompts
  tags: boolean;             // Tags enabled for prompts
  aiSearch?: boolean;        // AI semantic search functionality (requires OPENAI_API_KEY)
  aiGeneration?: boolean;    // AI generation features (requires OPENAI_API_KEY)
  mcp?: boolean;             // Model Context Protocol features and API keys
  comments?: boolean;        // Comments on prompts enabled
  promptEnhancer?: boolean;  // AI Prompt Enhancer on /developers and /api/improve-prompt
}
```

All features except `privatePrompts`, `changeRequests`, `categories`, and `tags` are optional and default to false or true depending on core defaults. The flags for AI search/generation require external API keys (`OPENAI_API_KEY`) to function fully.

Sources:
[src/lib/config/index.ts:39-49]()

---

## Flag Reference

| Flag             | Type    | Default in `prompts.config.ts` | Fallback Default (if config missing) | Environment Variable Override          | Notes / Dependency                     |
|------------------|---------|---------------------------------|-------------------------------------|--------------------------------------|--------------------------------------|
| `privatePrompts` | boolean | `true`                          | `true`                              | `PCHAT_FEATURE_PRIVATE_PROMPTS`      | Allows users to create private prompts |
| `changeRequests` | boolean | `true`                          | `true`                              | `PCHAT_FEATURE_CHANGE_REQUESTS`      | Enables prompt versioning & edits    |
| `categories`     | boolean | `true`                          | `true`                              | `PCHAT_FEATURE_CATEGORIES`            | Enables prompt categories             |
| `tags`           | boolean | `true`                          | `true`                              | `PCHAT_FEATURE_TAGS`                  | Enables prompt tags                   |
| `aiSearch`       | boolean | `true`                          | `false`                             | `PCHAT_FEATURE_AI_SEARCH`             | Semantic search with OpenAI embeddings |
| `aiGeneration`   | boolean | `true`                          | `false`                             | `PCHAT_FEATURE_AI_GENERATION`         | AI prompt generation/improvement     |
| `mcp`            | boolean | `true`                          | `false`                             | `PCHAT_FEATURE_MCP`                   | Enables MCP server & API key features |
| `comments`       | boolean | `true`                          | `true`                              | `PCHAT_FEATURE_COMMENTS`              | Enables comments on prompt pages     |
| `promptEnhancer` | boolean | `false`                         | `true`                              | `PCHAT_FEATURE_PROMPT_ENHANCER`       | AI Prompt Enhancer on /developers and /api/improve-prompt |

- The defaults in `prompts.config.ts` represent the standard public release configuration.
- The fallback values are hardcoded in `src/lib/config/index.ts` and are used if the config file is missing or fails to import.
- Environment variables override these flags at runtime without requiring a rebuild.

Sources:
[prompts.config.ts:49-69](), [src/lib/config/index.ts:167-177](), [src/lib/config/index.ts:203-225]()

---

## Configuration Methods

### 1. Static Configuration (`prompts.config.ts`)

The primary configuration method is declaring feature flags inside the `features` block of the configuration object passed to `defineConfig()`.

```typescript
export default defineConfig({
  features: {
    privatePrompts: true,
    changeRequests: true,
    categories: true,
    tags: true,
    aiSearch: true,
    aiGeneration: true,
    mcp: true,
    comments: true,
    promptEnhancer: false,
  },
});
```

Sources:
[prompts.config.ts:49-69](), [src/lib/config/index.ts:97-99]()

### 2. Runtime Overrides (Environment Variables)

The `applyEnvOverrides()` function inspects `process.env` for keys prefixed by `PCHAT_FEATURE_` to override static configuration flags dynamically. For example, setting `PCHAT_FEATURE_AI_SEARCH=false` disables semantic search at runtime.

The internal helper `envBool` parses string values (`"true"`, `"1"`, `"false"`, `"0"`) into native booleans.

Sources:
[src/lib/config/index.ts:117-132](), [src/lib/config/index.ts:167-177]()

### 3. Interactive Setup (`scripts/setup.js`)

An interactive command-line utility prompts operators for feature toggles during private clone initialization, automatically writing out a customized `prompts.config.ts`.

Sources:
[scripts/setup.js:139-150]()

---

## Flag Resolution Pipeline

The complete pipeline determining effective feature flag states bridges natural language configuration choices to executable code paths:

Title: "Feature Flag Resolution Flow"
```mermaid
flowchart TD
  Start["getConfig()"] --> CheckCache{"cachedConfig exists?"}
  CheckCache -- "Yes" --> ReturnConfig["Return cachedConfig"]
  CheckCache -- "No" --> ImportUserConfig["import('@/../prompts.config')"]
  ImportUserConfig -- "Success" --> ImportSuccess["baseConfig = imported config"]
  ImportUserConfig -- "Fail" --> ImportFail["baseConfig = fallback default config"]
  ImportSuccess --> ApplyEnv["applyEnvOverrides(baseConfig)"]
  ImportFail --> ApplyEnv
  ApplyEnv --> CacheConfig["cachedConfig = evaluated config"]
  CacheConfig --> ReturnConfig
```

Sources:
[src/lib/config/index.ts:189-225]()

---

## Per-Flag Technical Implementation Details

### AI-Related Flags: `aiSearch`, `aiGeneration`, `promptEnhancer`

- **`aiSearch`** gates semantic search features utilizing OpenAI embeddings.
- **`aiGeneration`** controls AI features like prompt improvement and translation via OpenAI APIs.
- **`promptEnhancer`** specifically enables the AI Prompt Enhancer on the `/developers` page and the `/api/improve-prompt` endpoint.
- Components check these flags before rendering UI controls or invoking backend OpenAI services.

Sources:
[src/lib/config/index.ts:172-173](), [src/lib/config/index.ts:177](), [prompts.config.ts:59-62](), [prompts.config.ts:68-69]()

### Content Organization Flags: `categories`, `tags`

- These flags toggle category and tag filtering taxonomies in the UI.
- When disabled, filtering options are hidden, though database seeding scripts may still provision default taxonomies if active during setup.

Sources:
[src/lib/config/index.ts:170-171](), [prompts.config.ts:55-58]()

### MCP Flag: `mcp`

- Controls the Model Context Protocol server endpoints mounted at `/api/mcp` and API key generation interfaces.

Sources:
[prompts.config.ts:63-65](), [src/lib/config/index.ts:174]()

### Versioning and Social Flags: `changeRequests`, `comments`

- `changeRequests` activates prompt versioning and review workflows.
- `comments` toggles discussion threads on prompt detail views.

Sources:
[src/lib/config/index.ts:169](), [src/lib/config/index.ts:175]()

---

## Code Entity Association

This diagram maps configuration names and feature flags directly to code entities, Prisma models, and API routes.

Title: "Feature Flag to Code Entity Mapping"
```mermaid
graph TD
  subgraph ConfigurationSpace["Configuration Space"]
    Cfg["prompts.config.ts"] --> FPrivate["features.privatePrompts"]
    Cfg --> FCr["features.changeRequests"]
    Cfg --> FCat["features.categories"]
    Cfg --> FTag["features.tags"]
    Cfg --> FAI["features.aiSearch / aiGeneration"]
    Cfg --> FMcp["features.mcp"]
    Cfg --> FCom["features.comments"]
    Cfg --> FPE["features.promptEnhancer"]
  end

  subgraph CodeEntitySpace["Code Entity Space"]
    FPrivate --> PromptModel["Prisma Model: Prompt"]
    FCr --> CRModel["Prisma Model: ChangeRequest"]
    FCat --> CatModel["Prisma Model: Category"]
    FTag --> TagModel["Prisma Model: Tag"]
    FAI --> OpenAIService["OpenAI SDK / Embeddings"]
    FMcp --> MCPApi["API Route: /api/mcp"]
    FCom --> CommentsComp["UI Component: comments/"]
    FPE --> PromptEnhancerAPI["API Route: /api/improve-prompt"]
  end

  subgraph ExecutionPipeline["Execution Pipeline"]
    EnvOverride["applyEnvOverrides()"] -.-> Cfg
  end
```

Sources:
[src/lib/config/index.ts:39-49](), [src/lib/config/index.ts:117-186](), [prompts.config.ts:49-69]()

---

# Page: White-labeling & Clone Branding

# White-labeling & Clone Branding

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/page.tsx](src/app/page.tsx)

</details>



This page documents the white-labeling and clone branding system enabling deployments of `prompts.chat` with custom branding while hiding references to the upstream repository and community. This feature targets organizations or individuals running their own branded prompt library instance who want to fully rebrand or white-label the site.

For broader configuration context, see [12.1 Configuration Overview](). For deployment details, refer to [13.1 Docker Deployment]().

---

## Overview & Impact of `useCloneBranding`

The white-labeling system is controlled by the boolean flag `useCloneBranding` that toggles the visibility of prompts.chat-specific branding elements across the entire application [src/app/page.tsx:45](). When this flag is set to `true`, elements such as:

- GitHub repository links and stargazer counts (including the dynamic GitHub stars fetch) [src/app/page.tsx:50-62]()
- Achievements, testimonials, and media mentions
- Sponsor acknowledgment sections
- Brand asset context menus, video backgrounds, app store links, and specialized navigation items [src/app/page.tsx:71-132]()

are hidden or replaced to present a fully customized brand identity devoid of upstream repository attribution.

All core functionality of the application—such as prompt browsing, search, user authentication, and MCP features—remains intact, ensuring a polished white-labeled experience.

### Elements Hidden by `useCloneBranding`

| Element | Location | Description |
|---|---|---|
| GitHub stars and repo links | [src/app/page.tsx:50-62]() | Dynamic GitHub stars fetch omitted |
| Achievements and sponsor acknowledgments | [src/app/page.tsx:50-60]() | Sponsor logos and achievements disabled |
| Video background watermark | [src/app/page.tsx:71-88]() | Default video background replaced by logo watermark |
| App Store and Chrome extension links | [src/app/page.tsx:112-132]() | Removed links to official app stores |
| DeepWiki and Context7 links in footer | [src/components/layout/footer.tsx:23-28]() | Links to documentation AI agents are hidden. |
| DeepWiki and Context7 links in self-hosting docs | [src/app/docs/self-hosting/page.tsx:56-108]() | Links to documentation AI agents are hidden. |
| "How to Contribute" section in `CONTRIBUTING.md` | [CONTRIBUTING.md:7-14]() | The section guiding users to contribute via `prompts.chat` is specific to the main instance. |
| "Open Source" section in Privacy Policy | [src/app/privacy/page.tsx:124-131]() | The link to the GitHub repository is hidden. |
| "Description of Service" in Terms of Service | [src/app/terms/page.tsx:34-37]() | The description explicitly mentioning `prompts.chat` is hidden. |
| Issue template for submitting new prompts | [.github/ISSUE_TEMPLATE/config.yml:3-5]() | The link to `prompts.chat/prompts/new` is specific to the main instance. |

Sources: [src/app/page.tsx:45-132](), [src/components/layout/footer.tsx:23-28](), [src/app/docs/self-hosting/page.tsx:56-108](), [CONTRIBUTING.md:7-14](), [src/app/privacy/page.tsx:124-131](), [src/app/terms/page.tsx:34-37](), [.github/ISSUE_TEMPLATE/config.yml:3-5]()

---

## Configuration Architecture & Loading Pipeline

The white-labeling and branding system is driven by the configuration setup script (`scripts/setup.js`) and runtime config loaders. When setting up a private clone, the configuration generator automatically sets `useCloneBranding = true` and configures organization identity properties [SELF-HOSTING.md:151]().

Title: "Config Generation & Setup Pipeline"

```mermaid
graph TD
    subgraph "Code Entity Space"
        A["npx prompts.chat new <br/>(CLI Command)"]
        B["npm run setup<br/>(Setup Script)"]
        C["prompts.config.ts<br/>(Generated Config File)"]
        D["getConfig()<br/>src/lib/config/index.ts"]
        E["useBranding()<br/>src/components/providers/branding-provider.tsx"]
    end
    subgraph "Natural Language Space"
        RunCli["Run CLI to Scaffold New Instance"]
        RunSetupWizard["Run Interactive Setup Wizard"]
        WriteConfig["Generate Custom prompts.config.ts"]
        LoadRuntimeConfig["Load Config at Runtime"]
        AccessBrandingContext["Access Branding in Components"]
    end

    RunCli --> B
    B --> RunSetupWizard
    RunSetupWizard --> C
    C --> LoadRuntimeConfig
    LoadRuntimeConfig --> D
    D --> E
    E --> AccessBrandingContext
```

Sources: [SELF-HOSTING.md:85-93](), [SELF-HOSTING.md:145-203](), [src/app/page.tsx:39-45](), [src/components/layout/footer.tsx:11]()

---

## The `useCloneBranding` Flag & Component Rendering

### Definition and Propagation

The master control flag for clone branding resides in configuration files and is consumed directly by the homepage server component [src/app/page.tsx:45](). It conditionally disables public achievement counters and external repository fetches:

```typescript
const useCloneBranding = config.homepage?.useCloneBranding ?? false;
```
[src/app/page.tsx:45]()

The `useBranding` hook [src/components/layout/footer.tsx:11]() also accesses this flag from the global configuration to conditionally render elements in the footer.

### Homepage Rendering Flow

The `HomePage` component checks `useCloneBranding` to decide whether to render upstream promotional media or custom organizational logos [src/app/page.tsx:35-88]().

Title: "Homepage Branding Selection Flow"

```mermaid
graph TD
    subgraph "Code Entity Space"
        HP["HomePage()<br/>src/app/page.tsx:35"]
        CFG["config.homepage.useCloneBranding<br/>src/app/page.tsx:45"]
        IMG["Image Component<br/>src/app/page.tsx:74"]
        VID["video Element<br/>src/app/page.tsx:94"]
        GH_STARS["githubStars Fetch<br/>src/app/page.tsx:48"]
    end
    subgraph "Natural Language Space"
        CheckFlag{"useCloneBranding == true?"}
        RenderWatermark["Render Organization Logo Watermark<br/>src/app/page.tsx:74"]
        RenderVideo["Render Default Video Background<br/>src/app/page.tsx:94"]
        FetchGithubStars["Fetch GitHub Stars (if enabled)<br/>src/app/page.tsx:48"]
    end

    HP --> CFG
    CFG --> CheckFlag
    CheckFlag -- True --> IMG
    IMG --> RenderWatermark
    CheckFlag -- False --> VID
    VID --> RenderVideo
    CheckFlag -- False & achievements enabled --> GH_STARS
    GH_STARS --> FetchGithubStars
```

Sources: [src/app/page.tsx:35-103](), [src/components/layout/footer.tsx:11]()

---

## Complete White-Label Setup Guide

To configure a fully white-labeled prompts.chat instance, follow these steps:

1.  **Run the Setup Script**: Execute the interactive configuration wizard to generate your private configuration. This can be done via `npx prompts.chat new my-prompt-library` [packages/prompts.chat/README.md:31-32]() or `npm run setup` [SELF-HOSTING.md:109]().
2.  **Enable the Master Flag**: Ensure `useCloneBranding = true` is set in your generated `prompts.config.ts` [SELF-HOSTING.md:151]() or configuration provider. The setup wizard typically handles this.
3.  **Specify Custom Branding Assets**: Fill out the `branding` object with organization details for `name`, `logo`, `logoDark`, `favicon`, and `description` [SELF-HOSTING.md:154-159]().
4.  **Disable Achievements and Sponsors**: Set `homepage.achievements.enabled = !useCloneBranding` and `homepage.sponsors.enabled = !useCloneBranding` to hide prompts.chat specific achievements and sponsors [SELF-HOSTING.md:190-196]().
5.  **Customize Theme**: Adjust `theme` properties like `radius`, `variant`, `density`, and primary colors [SELF-HOSTING.md:162-168]().

Sources: [SELF-HOSTING.md:85-203](), [packages/prompts.chat/README.md:31-32]()

---

# References

- Homepage white-label UI logic: [src/app/page.tsx:35-103]()
- Self-hosting configuration example: [SELF-HOSTING.md:145-203]()
- Footer branding logic: [src/components/layout/footer.tsx:11-37]()
- Self-hosting documentation page: [src/app/docs/self-hosting/page.tsx:56-108]()

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [DOCKER.md](DOCKER.md)
- [compose.yml](compose.yml)
- [docker/Dockerfile](docker/Dockerfile)
- [docker/entrypoint.sh](docker/entrypoint.sh)
- [scripts/docker-setup.js](scripts/docker-setup.js)
- [src/__tests__/api/improve-prompt.test.ts](src/__tests__/api/improve-prompt.test.ts)

</details>



This page serves as the parent guide for deployment operations in `prompts.chat`, covering containerized execution via Docker [DOCKER.md:1-3](), multi-stage builds [docker/Dockerfile:1-94](), and production initialization [docker/entrypoint.sh:1-41]().

As a parent page, this document provides a high-level architectural overview. For deep technical instructions, refer to the child pages:
- For Docker image layers, runtime environment injection, and volume mounts, see [Docker Deployment](#13.1).
- For bare-metal installation, configuration files, and build processes, see [Self-hosting Guide](#13.2).
- For automated GitHub Actions pipelines (`docker-publish.yml`, `update-contributors.yml`), see [CI/CD Pipeline](#13.3).
- For security hardening, `AUTH_SECRET` generation, connection pooling, and Sentry configuration, see [Production Checklist & Observability](#13.4).

Sources: [DOCKER.md:1-3](), [docker/Dockerfile:1-47](), [docker/entrypoint.sh:1-41]()

---

## Deployment Options Overview

Prompts.chat supports both containerized deployments via Docker Compose or standalone Docker containers, as well as manual self-hosting on a Node.js runtime with a configured PostgreSQL database. Configuration is managed through environment variables prefixed with `PCHAT_*` for branding, theme, authentication, internationalization, and feature toggles. These environment variables are transformed into the runtime configuration file `prompts.config.ts` by helper scripts during container builds [scripts/docker-setup.js:6-32]().

| Deployment Mode | Primary Artifact | Configuration Source | Startup Orchestration |
|-----------------|------------------|----------------------|-----------------------|
| **Docker Compose** | Pre-built or locally built Docker image (`ghcr.io/f/prompts.chat` or local build) | `compose.yml` environment variables [compose.yml:19-39]() | Entrypoint shell script [docker/entrypoint.sh:1-41]() |
| **Standalone Docker** | Docker image built from `docker/Dockerfile` | Command line `-e PCHAT_*` env variables | Entrypoint shell script [docker/entrypoint.sh:1-41]() |
| **Manual Self-Hosting** | Node.js 24 runtime process | Manual `prompts.config.ts` and `.env` | Process manager of choice, e.g., pm2 or systemd |

Sources: [compose.yml:19-39](), [docker/Dockerfile:1-94](), [docker/entrypoint.sh:1-41](), [scripts/docker-setup.js:6-32]()

---

## Deployment Architecture

The application's Docker image is built using a multi-stage process outlined in `docker/Dockerfile`. This process results in a minimal production-ready standalone Next.js server bundled with Prisma runtime tools for database migrations [docker/Dockerfile:1-94](). The image includes a multi-stage compilation flow that builds client and server assets, packages them into a runner stage running under the `nextjs` user, and pairs with a companion PostgreSQL container managed by `compose.yml` [compose.yml:1-18]().

Title: Deployment Architecture Mapping Natural Language to Code Entities
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        UserRequirements["UserContainerRequirements"]
    end

    subgraph "CodeEntitySpace"
        Dockerfile["docker/Dockerfile"]
        EntrypointScript["docker/entrypoint.sh"]
        ServerProcess["server.js"]
        PrismaMigrate["prisma/schema.prisma"]
        PostgresDB["postgres:17-bookworm"]
        DockerSetup["scripts/docker-setup.js"]
        ConfigTs["prompts.config.ts"]
    end

    UserRequirements -->|"Defines config"| DockerSetup
    DockerSetup -->|"Generates"| ConfigTs
    ConfigTs -->|"Bundled into"| ServerProcess
    Dockerfile -->|"Builds runner stage"| ServerProcess
    EntrypointScript -->|"Executes npx prisma migrate deploy"| PrismaMigrate
    PrismaMigrate -->|"Applies schema"| PostgresDB
    EntrypointScript -->|"Executes node server.js"| ServerProcess
    ServerProcess -->|"Queries"| PostgresDB
```

**Key Architectural Points:**
- The Prisma schema and migration files are bundled within the Docker image to allow runtime migration execution without rebuilding [docker/Dockerfile:69-70]().
- The configuration file `prompts.config.ts` is generated from environment variables via initialization scripts [scripts/docker-setup.js:120-170]().
- The entrypoint script `docker/entrypoint.sh` ensures the database is reachable before launching `server.js` [docker/entrypoint.sh:12-41]().

Sources: [docker/Dockerfile:1-94](), [docker/entrypoint.sh:1-41](), [scripts/docker-setup.js:1-172](), [compose.yml:1-45]()

---

## Initialization Data Flow

The container startup sequence is orchestrated by `docker/entrypoint.sh` to ensure a smooth launch with zero manual intervention, validating environment variables, database TCP reachability, and executing runtime schema migrations before booting the Next.js server process [docker/entrypoint.sh:1-41]().

Title: Container Initialization Sequence
```mermaid
graph TB
    subgraph "BootstrapSequence"
        StartContainer["StartContainer"]
        CheckAuthSecret["CheckAUTH_SECRET"]
        GenerateAuthSecret["GenerateRandomSecret"]
        WaitForDB["WaitForPostgresTCP"]
        RunMigrations["RunPrismaMigrateDeploy"]
        StartServer["ExecNodeServer"]
    end

    StartContainer --> CheckAuthSecret
    CheckAuthSecret -- "Missing" --> GenerateAuthSecret
    CheckAuthSecret -- "Present" --> WaitForDB
    GenerateAuthSecret --> WaitForDB
    WaitForDB -- "Connected" --> RunMigrations
    RunMigrations -- "Success" --> StartServer
```

**Step-by-step details:**
1. The entrypoint script verifies the presence of `AUTH_SECRET` and generates a secure random fallback if absent [docker/entrypoint.sh:4-10]().
2. A TCP socket check validates PostgreSQL availability on its configured port [docker/entrypoint.sh:12-32]().
3. Prisma migrations are deployed against the database via `npx prisma migrate deploy` [docker/entrypoint.sh:34-37]().
4. The standalone Next.js server starts via `exec node server.js` [docker/entrypoint.sh:39-41]().

Sources: [docker/entrypoint.sh:1-41]()

---

## Relating Configuration and Runtime Code

The runtime configuration pipeline translates environment variables (`PCHAT_*`) into the type-safe configuration structure consumed by the Next.js application core [scripts/docker-setup.js:6-32]().

Title: Configuration and Runtime Pipeline Mapping
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        EnvVariables["EnvironmentVariables"]
    end
    subgraph "CodeEntitySpace"
        DockerSetupScript["scripts/docker-setup.js"]
        ConfigFile["prompts.config.ts"]
        NextJsApp["server.js"]
    end

    EnvVariables -->|"Read at Build/Runtime"| DockerSetupScript
    DockerSetupScript -->|"Outputs"| ConfigFile
    ConfigFile -->|"ImportedBy"| NextJsApp
```

Sources: [scripts/docker-setup.js:1-172]()

---

## Summary: Deployment Components

| Component | Role | Code Reference |
|-----------|------|----------------|
| `docker/Dockerfile` | Multi-stage build for optimized production image | [docker/Dockerfile:1-94]() |
| `docker/entrypoint.sh` | Bootstrap script for DB readiness, migrations, and server start | [docker/entrypoint.sh:1-41]() |
| `compose.yml` | Defines multi-container orchestration (app + Postgres) | [compose.yml:1-45]() |
| `scripts/docker-setup.js` | Converts env variables into configuration TypeScript file | [scripts/docker-setup.js:1-172]() |
| `prompts.config.ts` | Runtime configuration file loaded by Next.js app | Generated file, see docker-setup.js |

Sources: [docker/Dockerfile:1-94](), [docker/entrypoint.sh:1-41](), [compose.yml:1-45](), [scripts/docker-setup.js:1-172]()

---

For detailed instructions on each deployment topic, consult the respective child pages:
- [Docker Deployment](#13.1) — Image details, entrypoint, compose setup, volume persistence, and configs.
- [Self-hosting Guide](#13.2) — Comprehensive manual deployment with Node.js, DB setup, and production optimization.
- [CI/CD Pipeline](#13.3) — GitHub Actions workflows for build, publish, testing, and maintenance automation.
- [Production Checklist & Observability](#13.4) — Security, secrets management, pooling, error tracking, monitoring, and health checks.

Sources: [DOCKER.md:1-206](), [docker/Dockerfile:1-94](), [compose.yml:1-45](), [docker/entrypoint.sh:1-41](), [scripts/docker-setup.js:1-172]()

---

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [DOCKER.md](DOCKER.md)
- [compose.yml](compose.yml)
- [docker/Dockerfile](docker/Dockerfile)
- [docker/entrypoint.sh](docker/entrypoint.sh)
- [scripts/docker-setup.js](scripts/docker-setup.js)
- [src/__tests__/api/improve-prompt.test.ts](src/__tests__/api/improve-prompt.test.ts)

</details>



This document covers the technical implementation of the Docker deployment architecture for `prompts.chat`. The deployment utilizes a multi-stage production build producing a Next.js standalone output, managed by a dedicated entrypoint script for runtime orchestration, automated migrations, and configuration generation [docker/Dockerfile:1-94](), [docker/entrypoint.sh:1-41](), [scripts/docker-setup.js:1-172]().

---

## Architecture Overview

The `prompts.chat` Docker deployment follows container best practices by separating the build environment from the runtime environment. It uses a 4-stage Dockerfile to produce a lean, production-ready image based on `node:24-bookworm-slim` [docker/Dockerfile:12-47]().

### Container Lifecycle & Process Flow

```mermaid
graph TD
    subgraph DockerImage["ghcr.io/f/prompts.chat (Runner Stage)"]
        Entrypoint["entrypoint.sh [docker/entrypoint.sh:1-42]"]
        PrismaCLI["Prisma CLI [docker/Dockerfile:76]"]
        Standalone["Next.js Standalone Server [docker/Dockerfile:65]"]
        
        subgraph RuntimeLogic["Entrypoint Logic"]
            AuthCheck["Secret Generation [docker/entrypoint.sh:5-10]"]
            DBWait["TCP Port Check [docker/entrypoint.sh:16-32]"]
            Migrate["Prisma Migrate [docker/entrypoint.sh:36]"]
        end
    end

    subgraph ExternalServices["External Infrastructure"]
        Postgres["PostgreSQL (db service) [compose.yml:2-17]"]
        Volume["postgres_data Volume [compose.yml:44-46]"]
    end

    Entrypoint --> AuthCheck
    AuthCheck --> DBWait
    DBWait -- "net.createConnection" --> Postgres
    DBWait --> Migrate
    Migrate -- "npx prisma migrate deploy" --> Postgres
    Postgres -- "Persists to" --> Volume
    Migrate --> Standalone
    Standalone -- "exec node server.js" --> Entrypoint
```

Sources: [docker/Dockerfile:47-94](), [docker/entrypoint.sh:1-41](), [compose.yml:1-45]()

---

## Dockerfile Structure

The `docker/Dockerfile` implements a multi-stage build to minimize image size and security attack surface by excluding build tools from the final runner stage [docker/Dockerfile:1-46]().

| Stage       | Base Image             | Purpose             | Key Actions                                                                                   |
|-------------|------------------------|---------------------|----------------------------------------------------------------------------------------------|
| **Base**    | `node:24-bookworm-slim`| OS Setup            | Installs `openssl`, `curl`, `ca-certificates` [docker/Dockerfile:12-18]()                   |
| **Deps**    | `base`                 | Dependency Caching  | Copies package manifests and Prisma schema, then runs `npm ci` [docker/Dockerfile:23-33]()  |
| **Builder** | `base`                 | Compilation         | Copies node_modules & sources, runs `npm run build` for standalone Next.js output [docker/Dockerfile:36-44]()  |
| **Runner**  | `node:24-bookworm-slim`| Production Runtime  | Copies build artifacts, Prisma CLI, adds non-root user, sets entrypoint script [docker/Dockerfile:47-94]()     |

**Key implementation notes:**
- The runner stage installs the Prisma CLI (`prisma@6.19`) specifically for executing runtime database migrations [docker/Dockerfile:75-77]().
- The script `docker/entrypoint.sh` is copied, given execution permissions, and set as the container entrypoint [docker/Dockerfile:78-94]().

Sources: [docker/Dockerfile:11-94]()

---

## Runtime Orchestration (`entrypoint.sh`)

The `docker/entrypoint.sh` script orchestrates container startup by securing environment secrets, validating database reachability via TCP probes, running database migrations, and launching the application server [docker/entrypoint.sh:1-41]().

### 1. Dynamic `AUTH_SECRET` Generation
If `AUTH_SECRET` is unset, the script generates a cryptographic 32-byte base64 secret using `openssl rand -base64 32` [docker/entrypoint.sh:5-10](). Production deployments should explicitly supply `AUTH_SECRET` to ensure user sessions persist across restarts [DOCKER.md:147-155]().

### 2. Database Readiness Check
Using a native Node.js TCP socket probe (`net.createConnection`), the script tests the host and port extracted from `DATABASE_URL` [docker/entrypoint.sh:16-32](). It retries up to 30 times with 2-second intervals to prevent premature container crashes [docker/entrypoint.sh:14-31]().

### 3. Automated Prisma Migrations
Once TCP connectivity is established, `npx prisma migrate deploy` executes pending schema migrations against the PostgreSQL database [docker/entrypoint.sh:36]().

### 4. Application Startup
The script executes `exec node server.js` to start the standalone Next.js application on the specified port [docker/entrypoint.sh:40-41]().

Sources: [docker/entrypoint.sh:1-41](), [DOCKER.md:147-155]()

---

## Configuration & Environment Variables (`PCHAT_*`)

`prompts.chat` supports runtime configuration overrides via environment variables prefixed with `PCHAT_`. These map directly to configuration properties defined in `prompts.config.ts` [DOCKER.md:67-136]().

### Branding and Theme Variables

| Env Variable        | Config Path          | Description                          | Default                |
|---------------------|---------------------|------------------------------------|------------------------|
| `PCHAT_NAME`        | `branding.name`      | Application name                   | `My Prompt Library`     |
| `PCHAT_DESCRIPTION` | `branding.description`| App description                   | `Collect, organize...`  |
| `PCHAT_LOGO`        | `branding.logo`      | Logo URL path (in `/public`)      | `/logo.svg`             |
| `PCHAT_LOGO_DARK`   | `branding.logoDark`  | Dark mode logo                    | Same as `PCHAT_LOGO`    |
| `PCHAT_FAVICON`     | `branding.favicon`   | Favicon URL                       | `/logo.svg`             |
| `PCHAT_COLOR`       | `theme.colors.primary`| Primary UI color (hex)             | `#6366f1`               |
| `PCHAT_THEME_RADIUS`| `theme.radius`       | Border radius: `none\|sm\|md\|lg`     | `sm`                    |
| `PCHAT_THEME_VARIANT`| `theme.variant`      | UI style: `default\|flat\|brutal`    | `default`               |
| `PCHAT_THEME_DENSITY`| `theme.density`      | Spacing: `compact\|default\|comfortable` | `default`          |

### Authentication & Internationalization Variables

| Env Variable          | Config Path         | Description                        | Default           |
|-----------------------|---------------------|----------------------------------|-------------------|
| `PCHAT_AUTH_PROVIDERS`| `auth.providers`    | Comma-separated list (`github,google,credentials`) | `credentials` |
| `PCHAT_ALLOW_REGISTRATION` | `auth.allowRegistration` | Enable public user signup       | `true`          |
| `PCHAT_LOCALES`      | `i18n.locales`      | Supported locales (comma-separated) | `en`        |
| `PCHAT_DEFAULT_LOCALE`| `i18n.defaultLocale`| Default locale                  | `en`         |

### Feature Flags

| Env Variable                | Config Path           | Description                                 | Default    |
|-----------------------------|---------------------|---------------------------------------------|------------|
| `PCHAT_FEATURE_PRIVATE_PROMPTS` | `features.privatePrompts` | Enable private prompts                  | `true`     |
| `PCHAT_FEATURE_CHANGE_REQUESTS` | `features.changeRequests` | Enable versioning/change requests       | `true`     |
| `PCHAT_FEATURE_CATEGORIES`       | `features.categories`     | Enable categories                        | `true`     |
| `PCHAT_FEATURE_TAGS`             | `features.tags`           | Enable tags                             | `true`     |
| `PCHAT_FEATURE_COMMENTS`         | `features.comments`       | Enable comments                         | `true`     |
| `PCHAT_FEATURE_AI_SEARCH`        | `features.aiSearch`       | Enable AI semantic search               | `false`    |
| `PCHAT_FEATURE_AI_GENERATION`    | `features.aiGeneration`   | Enable AI generation features           | `false`    |
| `PCHAT_FEATURE_MCP`              | `features.mcp`            | Enable Model Context Protocol support  | `false`    |
| `PCHAT_FEATURE_PROMPT_ENHANCER`  | `features.promptEnhancer` | Enable Prompt Enhancer on `/developers` and `/api/improve-prompt` | `true` |

Sources: [DOCKER.md:86-136](), [compose.yml:29-39]()

---

## Build-time Configuration Generation (`scripts/docker-setup.js`)

When building custom container images, `scripts/docker-setup.js` generates `prompts.config.ts` programmatically from environment inputs [scripts/docker-setup.js:1-172]().

### Implementation Details
- Uses utility functions `env()`, `envBool()`, and `envArray()` to parse environment variables with fallback defaults [scripts/docker-setup.js:39-53]().
- Invokes `defineConfig()` to output a typed TypeScript configuration file [scripts/docker-setup.js:55-118]().
- Automatically configures `useCloneBranding = true` for containerized instances [scripts/docker-setup.js:59]().

### Build-time Config Flow

```mermaid
graph LR
    subgraph NaturalLanguage["Configuration Inputs"]
        Env["EnvVars (e.g., BRAND_NAME) [scripts/docker-setup.js:10-31]"]
    end

    subgraph CodeEntity["Code Implementation"]
        SetupScript["docker-setup.js [scripts/docker-setup.js:120-172]"]
        DefineConfig["defineConfig [scripts/docker-setup.js:61]"]
        ConfigTS["prompts.config.ts [scripts/docker-setup.js:37]"]
    end

    Env --> SetupScript
    SetupScript -- "generateConfig" --> DefineConfig
    DefineConfig --> ConfigTS
```

Sources: [scripts/docker-setup.js:1-172]()

---

## Docker Compose Integration

The `compose.yml` manifest orchestrates a multi-container stack containing the Next.js `app` service and the PostgreSQL `db` service [compose.yml:1-45]().

### Services & Topology
- **db**: Runs `postgres:17-bookworm`, mounts the `postgres_data` volume to `/var/lib/postgresql/data`, and defines a `pg_isready` health check [compose.yml:2-17]().
- **app**: Builds from `docker/Dockerfile` or pulls `ghcr.io/f/prompts.chat:latest`, depends on `db` health, and binds port 4444 to container port 3000 [compose.yml:19-43]().

### Docker Compose Service Topology

```mermaid
graph LR
    subgraph ComposeStack["DockerComposeStack"]
        App["AppService [compose.yml:19]"]
        DB["DBService [compose.yml:2]"]
    end
    
    subgraph StorageLayer["StoragePersistence"]
        Vol["postgres_dataVolume [compose.yml:45]"]
    end

    App -- "depends_on (healthy)" --> DB
    DB -- "mounts" --> Vol
    App -- "Port 4444:3000" --> HostBrowser["HostBrowser"]
```

Sources: [compose.yml:1-45]()

---

## Volume Persistence and Data Storage

- Database state persistence relies on the named Docker volume `postgres_data`, mounted directly to PostgreSQL's storage directory (`/var/lib/postgresql/data`) inside the `db` container [compose.yml:10-11]().
- This storage model ensures application records, prompts, user credentials, and change requests persist across container restarts, image updates, and rebuild operations.

Sources: [compose.yml:10-11]()

---

# Page: Self-hosting Guide

# Self-hosting Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SELF-HOSTING.md](SELF-HOSTING.md)
- [context7.json](context7.json)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [packages/prompts.chat/README.md](packages/prompts.chat/README.md)
- [prisma/reset-admin.ts](prisma/reset-admin.ts)
- [public/deepwiki.svg](public/deepwiki.svg)
- [scripts/setup.js](scripts/setup.js)
- [src/app/docs/api/page.tsx](src/app/docs/api/page.tsx)
- [src/app/docs/self-hosting/page.tsx](src/app/docs/self-hosting/page.tsx)
- [src/app/privacy/page.tsx](src/app/privacy/page.tsx)
- [src/app/terms/page.tsx](src/app/terms/page.tsx)
- [src/components/layout/footer.tsx](src/components/layout/footer.tsx)

</details>



## Purpose and Scope

This guide documents self-hosted deployment of `prompts.chat`, covering database setup, environment variables, the build process, and production configuration. It details the bootstrap architecture, configuration pipeline via `prompts.config.ts` and `.env` variables, database integration using Prisma with PostgreSQL, OAuth provider integration via NextAuth, and production deployment best practices.

For related topics, refer to Configuration Overview, Docker Deployment for container specifics, and Production Checklist for hardening tips.

Sources: [SELF-HOSTING.md:1-32](), [src/app/docs/self-hosting/page.tsx:16-29]()

---

## Deployment Options

`prompts.chat` supports two primary deployment methods for self-hosting:

1. **Docker (Recommended)**: An all-in-one container image with internal PostgreSQL, automatic setup, and a bootstrap process.
2. **Manual Installation**: Install Node.js 24.x with an external PostgreSQL database and perform manual build and configuration steps.

Sources: [SELF-HOSTING.md:33-87](), [src/app/docs/self-hosting/page.tsx:115-119]()

---

## Docker Deployment & Bootstrap Architecture

### Architecture Overview

The Docker image (`ghcr.io/f/prompts.chat`) employs a bootstrap shell script as the `ENTRYPOINT` which mounts persistent volumes and supervises multiple processes. The primary components inside the container are:

- `bootstrap.sh`: Runs once on container start, ensuring database initialization, repository clone, configuration generation, build, and migrations.
- `supervisord`: Manages running processes.
- PostgreSQL server: Runs with data persisted in `/data/postgres` volume.
- Next.js standalone server: Runs the built Next.js app server.

Persistent data resides under the `/data` volume for database files, cloned app source, build caches, and marker files indicating build/seed completions.

Title: "Docker Bootstrap and Code Entity Architecture"
```mermaid
graph TB
    subgraph DockerContainer ["DockerContainer ghcr.io/f/prompts.chat"]
        Bootstrap["bootstrap.sh ENTRYPOINT"]
        Supervisor["supervisord Process Manager"]
        
        subgraph ManagedProcesses ["Managed Processes"]
            PostgresProc["postgres-process postgres -D /data/postgres"]
            NextProc["nextjs-server-process node .next/standalone/server.js"]
        end
        
        subgraph Storage ["Persistent Volume /data"]
            PostgresData["/data/postgres PGDATA"]
            AppCode["/data/app git-clone"]
            Markers["/data/.built /data/.seeded"]
        end
    end
    
    Bootstrap -->|Mounts| Storage
    Bootstrap --> Supervisor
    Supervisor --> PostgresProc
    Supervisor --> NextProc
    
    NextProc --> PrismaClient["PrismaClient src/lib/db.ts"]
    PrismaClient --> PostgresProc["PostgreSQL localhost:5432"]
```
Sources: [SELF-HOSTING.md:80-87](), [src/lib/db.ts:1-21]()

### Bootstrap Sequence

On container startup, the bootstrap script executes the following:
1. Initializes PostgreSQL if `/data/postgres` is empty (`initdb`) and creates the `prompts` database.
2. Clones the `prompts.chat` repository into `/data/app` if missing.
3. Runs `scripts/docker-setup.js` to generate `prompts.config.ts` from environment variables.
4. Installs dependencies, generates the Prisma client via `prisma generate`, and builds the Next.js standalone server.
5. Runs Prisma migrations (`npm run db:deploy`) to bring the database schema up to date.
6. Seeds initial data (`npm run db:seed`) including the admin user and example prompts if unseeded.

Sources: [SELF-HOSTING.md:94-143](), [src/app/docs/self-hosting/page.tsx:168-174](), [packages/prompts.chat/README.md:27-38]()

---

## Configuration System & Setup Wizard Pipeline

`prompts.chat` uses a layered configuration system combining defaults defined in code, user-defined `prompts.config.ts` files generated by the setup script (`scripts/setup.js`), and environment variable overrides applied at runtime.

Title: "Configuration Pipeline and Code Entity Mapping"
```mermaid
graph TB
    CLI["scripts/setup.js npm run setup"] -->|Generates| UserConfig["prompts.config.ts User Defined"]
    BaseConfig["src/lib/config/index.ts Defaults"] --> DefineConfig["defineConfig()"]
    UserConfig --> DefineConfig
    DefineConfig --> EnvApply["Environment Overrides PCHAT_*"]
    EnvApply --> GetConfig["getConfig() / getConfigSync()"]
    
    GetConfig --> RootLayout["RootLayout src/app/layout.tsx"]
    RootLayout --> Footer["Footer src/components/layout/footer.tsx"]
```
Sources: [SELF-HOSTING.md:149-216](), [src/components/layout/footer.tsx:23-37]()

### Clone Branding Mode

The `useCloneBranding` flag enables white-label mode for self-hosted instances by replacing default branding with custom identity properties.

Behavior when enabled:
- Uses custom branding name, description, logos, and favicon throughout the UI.
- Hides footer links to external sponsors, DeepWiki, and the official repository.
- Removes achievements and sponsor components from the homepage.

Sources: [SELF-HOSTING.md:149-216](), [src/components/layout/footer.tsx:23-37]()

---

## Manual Installation & Prerequisites

Manual installation provides full control over environment configuration, runtime dependencies, and process management.

### Prerequisites

- **Node.js 24.x**: Required runtime version [package.json:121-123]().
- **PostgreSQL**: External database instance [SELF-HOSTING.md:36]().
- **npm**: Node.js package manager [SELF-HOSTING.md:37]().

Sources: [SELF-HOSTING.md:33-38](), [src/app/docs/self-hosting/page.tsx:115-126]()

### Installation Workflow

```bash
# Quick Start
npx prompts.chat new my-prompt-library
cd my-prompt-library

# Manual Installation
git clone https://github.com/f/prompts.chat.git
cd prompts.chat
npm install
npm run setup
cp .env.example .env
npm run db:migrate
npm run db:seed
npm run dev
```

Sources: [SELF-HOSTING.md:78-143](), [packages/prompts.chat/README.md:27-38]()

### Interactive Setup Wizard

The `npm run setup` command invokes `scripts/setup.js`, guiding administrators through environment, database, branding, theme, authentication, i18n, and feature flags configuration [package.json:22](), [scripts/setup.js:1-9]().

Sources: [SELF-HOSTING.md:107-117]()

---

## Database Configuration & Seeding

`prompts.chat` uses Prisma ORM for data modeling and access against PostgreSQL.

### Database Connectivity

The application connects to PostgreSQL via a singleton Prisma client instance located in `src/lib/db.ts`, preventing connection pool exhaustion during hot reloads.

Title: "Database Connectivity and Prisma Client Flow"
```mermaid
graph LR
    NextApp["NextApp Server"] -->|imports| DBClient["src/lib/db.ts"]
    DBClient -->|prismaClientSingleton| PrismaClientInst["PrismaClient"]
    PrismaClientInst -->|datasourceUrl| PostgresDB["PostgreSQL Database"]
```
Sources: [src/lib/db.ts:1-21](), [SELF-HOSTING.md:40-42]()

### Database Seeding

The `npm run db:seed` command executes `prisma/seed.ts`, which provisions the initial database state [package.json:15]():

1. Creates or updates an admin user (`admin@prompts.chat`) [prisma/reset-admin.ts:1-3]().
2. Fetches prompts, categories, tags, and authors from the remote API endpoint.
3. Upserts categories, tags, author records, and prompts into PostgreSQL.

Sources: [SELF-HOSTING.md:129-132]()

---

## Production Configuration & Environment Variables

The `.env` file is used to configure critical settings for the application. A `.env` file can be generated by copying `.env.example` and filling in the values [SELF-HOSTING.md:54-57]().

| Variable | Description | Source |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string. Example: `postgresql://user:password@localhost:5432/prompts` | [SELF-HOSTING.md:60]() |
| `AUTH_SECRET` | A random secret used by NextAuth for session encryption and JWT signing. Generate with `crypto.randomBytes(32).toString('base64')`. | [SELF-HOSTING.md:72](), [scripts/setup.js:21-23]() |
| `AUTH_GITHUB_ID` | OAuth Client ID for GitHub. Required if GitHub authentication is enabled. | [SELF-HOSTING.md:64]() |
| `AUTH_GITHUB_SECRET` | OAuth Client Secret for GitHub. Required if GitHub authentication is enabled. | [SELF-HOSTING.md:65]() |
| `AUTH_GOOGLE_ID` | OAuth Client ID for Google. Required if Google authentication is enabled. | [SELF-HOSTING.md:68]() |
| `AUTH_GOOGLE_SECRET` | OAuth Client Secret for Google. Required if Google authentication is enabled. | [SELF-HOSTING.md:69]() |
| `OPENAI_API_KEY` | API key for OpenAI services, enabling AI-powered semantic search, prompt enhancement, and AI generation features. | [SELF-HOSTING.md:75]() |
| `AUTH_URL` | The base URL of the application, used by NextAuth for callbacks. Automatically set by `scripts/setup.js`. | [scripts/setup.js:42]() |
| `AUTH_TRUST_HOST` | Set to `true` in production environments where the host header might be proxied. | [scripts/setup.js:43]() |
| `CRON_SECRET` | A secret key for securing cron job endpoints. Generated automatically by `scripts/setup.js`. | [scripts/setup.js:46]() |

Sources: [SELF-HOSTING.md:54-76](), [scripts/setup.js:30-92]()

---

## Security, Privacy, and CC0 Compliance

- **CC0 Public Domain License**: All prompts submitted to `prompts.chat` are irrevocably released under the Creative Commons Zero 1.0 Universal License, placing them into the public domain [src/app/terms/page.tsx:43-61]().
- **Data Collection**: The platform collects user emails, usernames, and profile data for authentication. Usage tracking via Google Analytics can be disabled by omitting `GOOGLE_ANALYTICS_ID` [src/app/privacy/page.tsx:38-54](), [src/app/privacy/page.tsx:99-104]().
- **Account Flagging & Rate Limiting**: Unusual or abusive activity triggers account flagging, enforcing a daily limit of 5 prompts and automatic unlisting of new submissions [src/app/terms/page.tsx:93-105]().

Sources: [src/app/terms/page.tsx:35-117](), [src/app/privacy/page.tsx:31-114](), [src/components/layout/footer.tsx:19-21]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml)
- [.github/workflows/update-contributors.yml](.github/workflows/update-contributors.yml)
- [src/app/api/admin/prompts/[id]/route.ts](src/app/api/admin/prompts/[id]/route.ts)
- [src/app/api/prompts/[id]/feature/route.ts](src/app/api/prompts/[id]/feature/route.ts)
- [src/app/api/prompts/[id]/unlist/route.ts](src/app/api/prompts/[id]/unlist/route.ts)

</details>



## Purpose and Scope

This document covers the continuous integration and deployment (CI/CD) automation for prompts.chat. It explains GitHub Actions workflows for building and publishing Docker images, synchronizing contributor data, performing pull request validations, resetting media generation credits, and automated testing. The goal is to ensure code quality, consistent data sync between the database and flat files, seamless deployment using containerization, and integration with external platforms such as GitHub Container Registry and Hugging Face.

The workflows detailed here include:

- `.github/workflows/docker-publish.yml`: Builds, tests, and publishes multi-arch Docker images [.github/workflows/docker-publish.yml:1-78]().
- `.github/workflows/update-contributors.yml`: Runs scheduled contributor CSV synchronization and syncs data to Hugging Face [.github/workflows/update-contributors.yml:1-58]().
- `.github/workflows/ci.yml`: Validates pull requests and pushes with linting and testing.
- Automated testing using Vitest to validate API endpoints and code correctness [.github/workflows/docker-publish.yml:16-35]().

Sources:  
[.github/workflows/docker-publish.yml:1-78](), [.github/workflows/update-contributors.yml:1-58]()

---

## CI/CD Architecture Overview

The prompts.chat repository employs GitHub Actions workflows to automate CI/CD processes. The key workflows interact with various external platforms and internal scripts to maintain consistency, quality, and efficient delivery.

### Overview Diagram: CI/CD Flow and Code Entities

```mermaid
graph TB
    subgraph "Trigger Space"
        PushMain["Push to main branch"]
        Tag["Tag push v*"]
        CronContributor["Daily cron: update-contributors.yml"]
        ManualDispatch["Manual workflow_dispatch"]
    end

    subgraph "Workflows (Code Entity Space)"
        DockerPublish[".github/workflows/docker-publish.yml"]
        ContributorSync[".github/workflows/update-contributors.yml"]
        PullRequestCI[".github/workflows/ci.yml"]
    end

    subgraph "External Targets"
        GHCR["GitHub Container Registry ghcr.io"]
        HF["Hugging Face Dataset fka/prompts.chat"]
    end

    PushMain --> DockerPublish
    PushMain --> PullRequestCI
    Tag --> DockerPublish
    CronContributor --> ContributorSync
    ManualDispatch --> DockerPublish
    ManualDispatch --> ContributorSync

    DockerPublish --> GHCR
    ContributorSync --> HF
```
Sources:  
[.github/workflows/docker-publish.yml:3-10](), [.github/workflows/update-contributors.yml:3-7]()

---

## Main Docker Publish Workflow

`.github/workflows/docker-publish.yml` orchestrates the process of testing, building, and publishing the containerized application images for multiple architectures [.github/workflows/docker-publish.yml:1-78]().

### Workflow Triggers

- **On push to `main` branch** [.github/workflows/docker-publish.yml:4-6]()
- **On tag push matching pattern `v*`** (e.g., version tags like `v1.2.3`) [.github/workflows/docker-publish.yml:7-8]()
- **On manual workflow dispatch** [.github/workflows/docker-publish.yml:9-10]()

Sources:  
[.github/workflows/docker-publish.yml:3-10]()

### Jobs Overview

#### 1. Test Job

- Runs on `ubuntu-latest` runner [.github/workflows/docker-publish.yml:16-17]().
- Sets environment variable `DATABASE_URL` to a test DB connection string (`postgresql://test:test@localhost:5432/test`) [.github/workflows/docker-publish.yml:18-19]().
- Steps:
  - Checkout repository using `actions/checkout@v6` [.github/workflows/docker-publish.yml:21-22]().
  - Setup Node.js version 24 with npm caching via `actions/setup-node@v6` [.github/workflows/docker-publish.yml:24-29]().
  - Install dependencies with `npm ci` [.github/workflows/docker-publish.yml:30-31]().
  - Run tests via `npm test` [.github/workflows/docker-publish.yml:33-34]().

Sources:  
[.github/workflows/docker-publish.yml:16-35]()

#### 2. Build-and-Push Job

- Depends on successful completion of the `test` job (`needs: test`) [.github/workflows/docker-publish.yml:36-38]().
- Permissions:
  - Reads contents (code repo) [.github/workflows/docker-publish.yml:39-40]().
  - Writes packages (to GitHub Container Registry) [.github/workflows/docker-publish.yml:41-42]().
- Steps:
  - Checkout repository [.github/workflows/docker-publish.yml:44-45]().
  - Setup Docker Buildx builder (`docker/setup-buildx-action@v3`) [.github/workflows/docker-publish.yml:47-48]().
  - Login to GitHub Container Registry using `GITHUB_TOKEN` (`docker/login-action@v3`) [.github/workflows/docker-publish.yml:50-55]().
  - Extract metadata tags and labels with `docker/metadata-action@v5` [.github/workflows/docker-publish.yml:57-67]().
  - Build and push Docker images for `linux/amd64` and `linux/arm64` via `docker/build-push-action@v6` with GHA caching [.github/workflows/docker-publish.yml:68-78]().

Sources:  
[.github/workflows/docker-publish.yml:36-78]()

### Docker Image Tagging Strategy

Uses `docker/metadata-action@v5` to generate tags based on the git ref [.github/workflows/docker-publish.yml:57-67]():

| Tag Type | Description |
|---|---|
| `type=ref,event=branch` | Tags for branch reference (e.g. `main` branch) [.github/workflows/docker-publish.yml:63]() |
| `type=semver,pattern={{version}}` | Semantic version tag, extracted from tag push [.github/workflows/docker-publish.yml:64]() |
| `type=semver,pattern={{major}}.{{minor}}` | Major and minor version tag [.github/workflows/docker-publish.yml:65]() |
| `type=raw,value=latest,enable={{is_default_branch}}` | Latest tag if on default branch [.github/workflows/docker-publish.yml:66]() |

Sources:  
[.github/workflows/docker-publish.yml:57-67]()

---

## Contributor and Data Synchronization Workflow

`.github/workflows/update-contributors.yml` automates the synchronization of prompt data and contributor attribution between the database, git repository, and external dataset hosting [.github/workflows/update-contributors.yml:1-58]().

### Workflow Triggers and Setup

- **Scheduled** daily cron at 3 AM UTC (`cron: '0 3 * * *'`) [.github/workflows/update-contributors.yml:4-5]().
- **Manual trigger via `workflow_dispatch`** [.github/workflows/update-contributors.yml:6]().
- Uses `actions/checkout@v6` with full git history (`fetch-depth: 0`) for commit deduplication [.github/workflows/update-contributors.yml:13-17]().
- Sets up Python 3.x environment and configures git bot credentials [.github/workflows/update-contributors.yml:19-28]().
- Runs `./scripts/generate-contributors.sh`, pushes changes back to `main`, and syncs `prompts.csv` to Hugging Face [.github/workflows/update-contributors.yml:29-58]().

Sources:  
[.github/workflows/update-contributors.yml:1-58]()

### Data Synchronization Flow Diagram

```mermaid
graph TD
    subgraph "Code Entity Space"
        Script["scripts/generate-contributors.sh"]
        HfPython["huggingface_hub HfApi upload_file"]
    end

    subgraph "Filesystem & Git"
        CSVFile["prompts.csv"]
        GitCommit["git push origin main --force-with-lease"]
    end

    subgraph "External Platforms"
        GitHub["GitHub Repository main"]
        HuggingFace["Hugging Face Dataset fka/prompts.chat"]
    end

    Script --> CSVFile
    CSVFile --> GitCommit
    GitCommit --> GitHub
    CSVFile --> HfPython
    HfPython --> HuggingFace
```

Sources:  
[.github/workflows/update-contributors.yml:29-58]()

---

## Automated Testing of the Codebase

### Testing in Workflows

- **`.github/workflows/docker-publish.yml`** test job runs `npm test` after installing dependencies [.github/workflows/docker-publish.yml:16-35]().
- **`.github/workflows/ci.yml`** workflow runs on push and pull request events for the `main` branch:
  - Sets up Node.js 24 with npm caching.
  - Installs dependencies (`npm ci`).
  - Runs linter and test suites (`npm test`).

### Test Coverage on API Endpoints

The codebase uses Vitest for unit testing various API routes and backend utilities:

| Test File Path | Description |
|----------------|-------------|
| `src/__tests__/api/admin-categories.test.ts` | Tests `POST /api/admin/categories` authorization and creation logic [src/__tests__/api/admin-categories.test.ts:1-168]() |
| `src/__tests__/api/admin-prompts.test.ts` | Tests `GET /api/admin/prompts` pagination, filtering, and sorting [src/__tests__/api/admin-prompts.test.ts:1-195]() |
| `src/__tests__/api/admin-users.test.ts` | Tests `GET /api/admin/users` role verification and user queries [src/__tests__/api/admin-users.test.ts:1-192]() |
| `src/__tests__/api/comment-flag.test.ts` | Tests comment flagging and unflagging operations [src/__tests__/api/comment-flag.test.ts:1-203]() |
| `src/__tests__/api/comment-vote.test.ts` | Tests comment voting scores and database mutations [src/__tests__/api/comment-vote.test.ts:1-198]() |
| `src/__tests__/api/comment-operations.test.ts` | Tests comment deletion and soft-delete behaviors [src/__tests__/api/comment-operations.test.ts:1-184]() |

Sources:  
[.github/workflows/docker-publish.yml:16-35](), [src/__tests__/api/admin-categories.test.ts:1-168](), [src/__tests__/api/admin-prompts.test.ts:1-195](), [src/__tests__/api/admin-users.test.ts:1-192](), [src/__tests__/api/comment-flag.test.ts:1-203](), [src/__tests__/api/comment-vote.test.ts:1-198](), [src/__tests__/api/comment-operations.test.ts:1-184]()

---

## Admin API Routes and State Management

Key administrative API endpoints manage prompt state and content moderation, supporting the overall deployment and operational lifecycle:

| Endpoint & File Path | Action & Description |
|---|---|
| `POST /api/prompts/[id]/unlist` | Toggles `isUnlisted` and `unlistedAt` status for prompts, restricted to `ADMIN` role, with tag revalidation [src/app/api/prompts/[id]/unlist/route.ts:7-71]() |
| `DELETE /api/admin/prompts/[id]` | Hard deletes a prompt record and cascades related database relations, restricted to admin users [src/app/api/admin/prompts/[id]/route.ts:5-72]() |
| `POST /api/prompts/[id]/feature` | Toggles `isFeatured` status and `featuredAt` timestamp, restricted to admin users [src/app/api/prompts/[id]/feature/route.ts:5-59]() |

Sources:  
[src/app/api/prompts/[id]/unlist/route.ts:7-71](), [src/app/api/admin/prompts/[id]/route.ts:5-72](), [src/app/api/prompts/[id]/feature/route.ts:5-59]()

---

## Reset Credits Workflow

While not explicitly provided in the file contents, a `reset-credits.yml` workflow would typically be responsible for resetting media generation credits for users on a scheduled basis. This is a common pattern for managing resource consumption in applications offering AI-powered features.

Sources:  
None

---

# Summary

The prompts.chat CI/CD pipeline automates core development and operational workflows:
- Multi-arch Docker builds and publishing via `.github/workflows/docker-publish.yml` guarded by test executions [.github/workflows/docker-publish.yml:1-78]().
- Scheduled contributor synchronization and Hugging Face dataset publishing via `.github/workflows/update-contributors.yml` [.github/workflows/update-contributors.yml:1-58]().
- Continuous integration checks (linting and testing) on every push and pull request via `.github/workflows/ci.yml`.
- Vitest suite coverage verifying API endpoint correctness across administrative and social features.

---

# References

- Docker publish workflow: [.github/workflows/docker-publish.yml:1-78]()
- Contributor update workflow: [.github/workflows/update-contributors.yml:1-58]()
- Admin category tests: [src/__tests__/api/admin-categories.test.ts:1-168]()
- Admin prompt tests: [src/__tests__/api/admin-prompts.test.ts:1-195]()
- Admin user tests: [src/__tests__/api/admin-users.test.ts:1-192]()
- Comment flag tests: [src/__tests__/api/comment-flag.test.ts:1-203]()
- Comment vote tests: [src/__tests__/api/comment-vote.test.ts:1-198]()
- Comment operations tests: [src/__tests__/api/comment-operations.test.ts:1-184]()
- Unlist prompt API: [src/app/api/prompts/[id]/unlist/route.ts:7-71]()
- Admin delete prompt API: [src/app/api/admin/prompts/[id]/route.ts:5-72]()
- Feature prompt API: [src/app/api/prompts/[id]/feature/route.ts:5-59]()

---

# Page: Production Checklist & Observability

# Production Checklist & Observability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [sentry.edge.config.ts](sentry.edge.config.ts)
- [sentry.server.config.ts](sentry.server.config.ts)
- [src/app/prompts/[id]/opengraph-image.tsx](src/app/prompts/[id]/opengraph-image.tsx)
- [src/instrumentation-client.ts](src/instrumentation-client.ts)

</details>



This document provides a comprehensive operational checklist, configuration guide, and monitoring architecture for deploying `prompts.chat` to production environments. It details required environment variables, database connection pooling strategies, Sentry error tracking and instrumentation across node, edge, and client runtimes, `next.config.ts` build optimizations, health check configurations, and disaster recovery backups.

---

## Environment Variable Setup

### Critical Variables

Production deployments **must** configure essential secrets and runtime parameters. These should be supplied via secure environment injection or orchestrator configuration files [.env.example:1-11]().

| Variable          | Purpose                                                  | Generation Method / Example                  | Required  |
|-------------------|----------------------------------------------------------|---------------------------------------------|-----------|
| `NEXTAUTH_SECRET`  | JWT signing & cookie encryption key                      | `openssl rand -base64 32`                    | ✅ Yes    |
| `DATABASE_URL`     | PostgreSQL connection string with pool settings          | `postgresql://user:pass@host:5432/db?connection_limit=5` | ✅ Yes    |
| `NEXTAUTH_URL`     | Canonical URL for auth callbacks & redirects             | `https://prompts.chat`                       | ✅ Yes    |
| `CRON_SECRET`      | Secret token securing automated background crons         | Random secure string                         | ✅ Yes    |

**NEXTAUTH_SECRET Management:**

The `NEXTAUTH_SECRET` value is consumed by NextAuth to sign session cookies and tokens [.env.example:10](). Ensuring persistence across container restarts is critical to prevent session invalidation.

Sources: [.env.example:4-10]()

---

## Database Configuration & Pooling

### Connection Pooling & Prisma Client Singleton

For production environments experiencing high concurrency or serverless invocation scaling, direct database connections can quickly exhaust available backend file descriptors. The application implements a global singleton pattern to ensure that only a single `PrismaClient` instance is instantiated per server lifecycle [src/lib/db.ts:3-21]().

```typescript
const prismaClientSingleton = () => {
  return new PrismaClient({
    log:
      process.env.NODE_ENV === "development"
        ? ["query", "error", "warn"]
        : ["error"],
    datasourceUrl: process.env.DATABASE_URL,
  });
};

export const db = globalForPrisma.prisma ?? prismaClientSingleton();
globalForPrisma.prisma = db;
```

This singleton pattern guards the `PrismaClient` instance globally on `globalThis`, preventing connection pool exhaustion during hot reloads or serverless scaling.

### Migrations and Direct URLs

When employing managed database poolers (such as Neon or Supabase), the primary `DATABASE_URL` routes through a transaction pooler. Database migration tools require a direct socket or connection to execute schema changes. Production deployments should configure a separate `DIRECT_URL` alongside `DATABASE_URL` [.env.example:5-6]().

Sources: [src/lib/db.ts:3-21](), [.env.example:5-6]()

---

## Configuration & Branding

The system configures appearance, behavior, and experimental features through environment variables and build-time config injection. Production customization relies on `PCHAT_*` prefixed environment variables and configuration objects.

### System Configuration Mapping from Natural Language to Code

```mermaid
graph TD
    subgraph Natural_Language_Space
        Branding[""Branding Name and Logo""]
        Auth[""Auth Providers Configuration""]
        Feat[""Feature Flags""]
        Theme[""Theme Colors and Radius""]
    end

    subgraph Code_Entity_Space
        EnvPrefix[""PCHAT_* Env Variables""]
        ConfigFunc[""defineConfig() in prompts.config.ts""]
        RootLayout[""RootLayout in src/app/layout.tsx""]
        OGImage[""OGImage in src/app/prompts/[id]/opengraph-image.tsx""]
    end

    Branding --> EnvPrefix
    Auth --> EnvPrefix
    Feat --> EnvPrefix
    Theme --> EnvPrefix

    EnvPrefix --> ConfigFunc
    ConfigFunc --> RootLayout
    ConfigFunc --> OGImage
```

- **`PCHAT_*` Environment Variables** serve as the primary interface for branding and feature toggling.
- The build produces a typed config object via `defineConfig()`.
- This config is consumed by the React root layout (`src/app/layout.tsx`) to apply UI theming and CSS variable injection [src/app/layout.tsx:159-175]().
- The config is also read in dynamic OpenGraph image generation (`src/app/prompts/[id]/opengraph-image.tsx`) for styling cards reflecting brand colors and theme radius [src/app/prompts/[id]/opengraph-image.tsx:50-51]().

Sources: [src/app/layout.tsx:159-175](), [src/app/prompts/[id]/opengraph-image.tsx:50-51]()

---

## Sentry Instrumentation, Error Boundaries & Build Settings

The application integrates Sentry for comprehensive error tracking and performance monitoring across client, server, and edge runtimes via Next.js instrumentation hooks [src/instrumentation.ts:1-13]().

### Sentry Runtime Configuration Mapping

```mermaid
graph TD
    subgraph Natural_Language_Space
        ClientErr[""Browser Extension & Third-Party Error Filtering""]
        ServerTracing[""Server-side Tracing & Performance Metrics""]
        EdgeHandling[""Edge Runtime Request Errors""]
    end

    subgraph Code_Entity_Space
        ClientInit[""src/instrumentation-client.ts""]
        ServerInit[""sentry.server.config.ts""]
        EdgeInit[""sentry.edge.config.ts""]
        NextConfig[""next.config.ts withSentryConfig""]
        ErrorBound[""src/pages/_error.tsx & global-error.tsx""]
        Register[""src/instrumentation.ts""]
    end

    ClientErr --> ClientInit
    ServerTracing --> ServerInit
    EdgeHandling --> EdgeInit

    ClientInit --> NextConfig
    ServerInit --> Register
    EdgeInit --> Register
    Register --> NextConfig
    NextConfig --> ErrorBound
```

- **Client Initialization (`src/instrumentation-client.ts`)**: Hooks into browser events with regex filters to ignore noisy errors from browser extensions like MetaMask or browser injection scripts [src/instrumentation-client.ts:8-79]().
- **Server & Edge Initialization**: Configured in `sentry.server.config.ts` [sentry.server.config.ts:7-22]() and `sentry.edge.config.ts` [sentry.edge.config.ts:8-23](), and registered via `src/instrumentation.ts` [src/instrumentation.ts:3-11]().
- **Request Error Capture**: `src/instrumentation.ts` binds `onRequestError = Sentry.captureRequestError` [src/instrumentation.ts:13-13]().
- **Next.js Integration (`next.config.ts`)**: Wraps configuration using `withSentryConfig` for automatic sourcemap uploads, tree-shaking debug logs (`removeDebugLogging: true`), standalone output (`output: "standalone"`), and Vercel Cron Monitor integration [next.config.ts:27-107]().
- **Error Boundaries**: Handled via client-side `src/app/global-error.tsx` using `Sentry.captureException` [src/app/global-error.tsx:12-14]() and custom error pages like `src/pages/_error.tsx` which invokes `Sentry.captureUnderscoreErrorException` [src/pages/_error.tsx:9-16]().

Sources: [src/instrumentation-client.ts:8-79](), [sentry.server.config.ts:7-22](), [sentry.edge.config.ts:8-23](), [src/instrumentation.ts:1-13](), [next.config.ts:27-107](), [src/pages/_error.tsx:9-16](), [src/app/global-error.tsx:12-14]()

---

## Monitoring, Data Feeds & Cache Strategies

### Public Datafeeds & Cache-Enabled JSON Routes

The `/prompts.json` API endpoint provides a public JSON feed for clients or monitoring [src/app/prompts.json/route.ts:25-69](). It implements:
- Query-parameter driven pagination (`page`, `limit`) and content inclusion (`full_content`) [src/app/prompts.json/route.ts:28-38]().
- ETag cache validation combining prompt count and latest updated timestamp generated via `generateETag` [src/app/prompts.json/route.ts:19-23]().
- Conditional HTTP 304 responses on ETag matches (`If-None-Match`) to optimize bandwidth and load [src/app/prompts.json/route.ts:60-69]().

### Prompts JSON API Data Flow

```mermaid
graph TD
    client[""Client Request: GET /prompts.json""]
    parse[""Parse Query Params (page, limit, full_content)""]
    count[""db.prompt.count() for total count""]
    latest[""db.prompt.findFirst() to get latest updatedAt""]
    etagGen[""generateETag(count, latestUpdatedAt)""]
    etagCheck{""If-None-Match header equals ETag?""}
    fetch[""db.prompt.findMany() for prompt data""]
    format[""Format Prompts with Authors, Tags, Counts""]
    response[""Return 200 OK with ETag and Cache-Control""]
    response304[""Return 304 Not Modified""]

    client --> parse
    parse --> count
    parse --> latest
    count --> etagGen
    latest --> etagGen
    etagGen --> etagCheck

    etagCheck -- ""Yes (Cache Hit)"" --> response304
    etagCheck -- ""No (Cache Miss)"" --> fetch
    fetch --> format
    format --> response
```

Sources: [src/app/prompts.json/route.ts:19-69]()

---

## Final Readiness Checklist

1. [x] **Security Secrets:** `NEXTAUTH_SECRET` explicitly configured to prevent session invalidation on server/container restarts [.env.example:10]().
2. [x] **Database Credentials:** Secure, non-default passwords and correctly scoped connection limits configured.
3. [x] **Prisma Client Singleton:** Confirmed single global instance per server lifecycle prevents connection storms [src/lib/db.ts:3-21]().
4. [x] **Build & Runtime:** `next.config.ts` includes standalone output, Sentry bundling and telemetry optimizations [next.config.ts:27-107]().
5. [x] **Sentry Active:** Verified instrumentation and sampling active only in production [src/instrumentation-client.ts:25-29](), [sentry.server.config.ts:7-11](), and `src/instrumentation.ts` [src/instrumentation.ts:3-13]().
6. [x] **Caching Headers:** Routes like `/prompts.json` implement ETag and conditional GET for efficient caching [src/app/prompts.json/route.ts:57-69]().
7. [x] **Error Boundaries:** Proper error boundaries capture unhandled exceptions in React and Next.js [src/pages/_error.tsx:9-16](), [src/app/global-error.tsx:12-14]().

Sources: [.env.example:10](), [src/lib/db.ts:3-21](), [next.config.ts:27-107](), [src/instrumentation-client.ts:25-29](), [sentry.server.config.ts:7-11](), [src/instrumentation.ts:1-13](), [src/app/prompts.json/route.ts:57-69](), [src/pages/_error.tsx:9-16](), [src/app/global-error.tsx:12-14]()

---

# Page: Contributing

# Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



## Purpose and Scope

This page serves as the parent guide for contribution guidelines within the **prompts.chat** ecosystem. The project supports distinct contribution paths for natural language prompt content versus codebase infrastructure, employing an automated attribution system and strict licensing boundaries. 

For detailed technical guidelines and workflows, see the following child pages:
- [Contribution Workflow](#14.1) — Step-by-step guide for submitting prompts via the web UI and code via PRs, issue templates, governance, and licensing.
- [Code Standards](#14.2) — Explanation of coding conventions, ESLint and MDX linting, formatting, and PR best practices.
- [Testing](#14.3) — Documentation on the Vitest testing framework, organization of tests, coverage, and running tests.

Sources: [CONTRIBUTING.md:1-15]()

---

## Contribution Paths

The codebase clearly distinguishes between **content** (prompts) and **infrastructure** (code). Each has a dedicated entry and automation path:

| Contribution Type      | Entry Point                                   | Attribution Method                              | Primary Files / Modules               |
|-----------------------|-----------------------------------------------|------------------------------------------------|-------------------------------------|
| **Prompts**           | [prompts.chat/prompts/new](https://prompts.chat/prompts/new) (Web UI) | Automated Git commits with `Co-authored-by` trailers | `prompts.csv`, `PROMPTS.md` (CSV sync system) |
| **Code & Documentation** | GitHub Pull Requests                         | Standard PR merge authorship                      | `src/*`, `scripts/*`, `.github/*`   |
| **Admin Bulk Import** | Admin Dashboard (import-controls)              | Bulk CSV processing via API                        | API routes, `Prompt` and `User` models |

### Prompt Contributions via Web Interface

The cornerstone for prompt submissions is the web-based UI accessible at `https://prompts.chat/prompts/new`. Contributors log in with GitHub, create prompts, and submit them. The system then automatically syncs prompts to the repository, generates properly formatted entries, and appends Git commits with `Co-authored-by` trailers for attribution [CONTRIBUTING.md:7-14]().

Direct edits to `prompts.csv` in the GitHub repository are discouraged to prevent formatting errors and broken automated workflows. The web interface validates prompt content and metadata before syncing.

For detailed workflow documentation, see [Contribution Workflow](#14.1).

Sources: [CONTRIBUTING.md:7-14]()

---

### Natural Language to Code Entity Mapping: Prompt Submission Flow

This diagram maps user actions and system components bridging natural language intent to code entities managing prompt data submission, storage, and sync.

Prompt Submission Flow
```mermaid
graph TB
    User["User"]
    WebUI["WebUI"]
    DB["DB"]
    ImportAPI["ImportAPI"]
    SyncScript["SyncScript"]
    RepoFiles["RepoFiles"]
    RouteCSV["RouteCSV"]

    User -->|"1. Submit prompt"| WebUI
    WebUI -->|"2. Save prompt"| DB
    DB -->|"3. Expose prompts data"| RouteCSV

    subgraph "Automation & Admin Pipeline"
        SyncScript -->|"4. Fetch CSV via RouteCSV"| RouteCSV
        SyncScript -->|"5. Commit prompt updates"| RepoFiles
        ImportAPI -->|"6. Bulk load prompts"| DB
    end
```
*Note: `WebUI` corresponds to `prompts.chat/prompts/new`, `DB` to the Prisma `Prompt` model, `SyncScript` to `scripts/generate-contributors.sh`, `RepoFiles` to `prompts.csv`/`PROMPTS.md`, and `RouteCSV` to `src/app/prompts.csv/route.ts`.*

Sources: [CONTRIBUTING.md:7-14]()

---

## Attribution System

A key feature of the project is its robust **GitHub attribution system** that credits all prompt contributors accurately even though contributions are largely automated.

- Contributor identities are linked via GitHub usernames or emails stored in the CSV contributor field [CONTRIBUTING.md:14]().
- The contribution script parses contributor metadata to build Git commit messages that include `Co-authored-by` trailers, enabling GitHub's built-in contributor recognition [CONTRIBUTING.md:14]().
- The `PROMPTS.md` file automatically lists contributors linking to their GitHub profiles for public visibility and acknowledgment [CONTRIBUTING.md:14]().

For further details on attribution governance, see [Contribution Workflow](#14.1).

### Natural Language to Code Entity Mapping: Attribution Logic

The following diagram details how contributor data flows from prompt submission fields through scripts to Git history and rendered contributor lists.

Attribution Logic
```mermaid
graph LR
    subgraph "Natural Language Space"
        ContributorName["ContributorName"]
        GitHubProfile["GitHubProfile"]
    end

    subgraph "Code Entity Space"
        CSVField["CSVField"]
        PythonScript["PythonScript"]
        ParseContributors["ParseContributors"]
        MakeEmail["MakeEmail"]
        BuildCommitMsg["BuildCommitMsg"]
        GitCommit["GitCommit"]
        FormatContributorLinks["FormatContributorLinks"]
        GeneratePromptBlock["GeneratePromptBlock"]
        PromptsMD["PromptsMD"]
    end

    ContributorName --> CSVField
    CSVField --> PythonScript
    PythonScript -- "calls" --> ParseContributors
    ParseContributors --> MakeEmail
    ParseContributors --> BuildCommitMsg
    BuildCommitMsg --> GitCommit
    GitCommit -->|"Creates Git commit w/ Co-authored-by trailers"| GitHubProfile
    PythonScript -- "calls" --> FormatContributorLinks
    FormatContributorLinks --> GeneratePromptBlock
    GeneratePromptBlock -->|"Writes prompt blocks including attribution"| PromptsMD
    PromptsMD -->|"Renders links to contributors"| GitHubProfile
```
*Note: `PythonScript` refers to `scripts/generate-contributors.sh`, `ParseContributors` to `parse_contributors`, `MakeEmail` to `make_email`, `BuildCommitMsg` to `build_commit_msg`, `GitCommit` to `git_commit`, `FormatContributorLinks` to `format_contributor_links`, `GeneratePromptBlock` to `generate_prompt_block`, and `PromptsMD` to `PROMPTS.md`.*

Sources: [CONTRIBUTING.md:7-14]()

---

## Licensing & Policies

The project distinguishes logic and content via dual licenses and clear contribution boundaries:

- **Source Code & Documentation:** MIT License for repository infrastructure, code, and site UI.
- **Prompt Content:** Public domain or CC0 terms for shared prompts in `prompts.csv` and `PROMPTS.md`.

### Content & Issue Guidelines

To maintain high-quality contributions and repository health:
- Check for duplicate prompts and test prompts thoroughly before submitting new entries [CONTRIBUTING.md:18-24]().
- Keep content appropriate for all audiences and descriptive with clear titles [CONTRIBUTING.md:21-23]().
- Only submit prompt contributions via the web interface (`https://prompts.chat/prompts/new`) [CONTRIBUTING.md:7-11](), [.github/ISSUE_TEMPLATE/config.yml:3-5]().
- The repository is strictly for AI prompt sharing; advertisements or off-topic issues are closed immediately and reported to GitHub [CONTRIBUTING.md:33-39]().
- Use the configured issue templates and links to report bugs or submit prompts. Blank issues are disabled [.github/ISSUE_TEMPLATE/config.yml:1-8]().

Sources: [CONTRIBUTING.md:16-39](), [.github/ISSUE_TEMPLATE/config.yml:1-8]()

---

## Admin Bulk Import & API

For repository maintainers and administrators, bulk import and export controls are available via administrative APIs and dashboard UI components. This enables programmatic management of prompt catalogs, category bindings, and synchronization routines.

Sources: [CONTRIBUTING.md:1-39]()

---

## Summary

Contributing to prompts.chat can be summarized as:
- Use the **web UI** for adding or editing prompt content, leveraging automatic sync and GitHub attribution ([Contribution Workflow](#14.1)) [CONTRIBUTING.md:7-14]().
- Use **GitHub PRs** for code, documentation, and infrastructure changes with typical review and merge workflows ([Code Standards](#14.2), [Testing](#14.3)) [CONTRIBUTING.md:25-32]().
- Follow community guidelines, issue policies, and licensing restrictions [CONTRIBUTING.md:33-39]().

For more detailed guidance, refer to:
- [Contribution Workflow](#14.1)
- [Code Standards](#14.2)
- [Testing](#14.3)

Sources: [CONTRIBUTING.md:5-39](), [.github/ISSUE_TEMPLATE/config.yml:1-8]()

---

# Page: Contribution Workflow

# Contribution Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [LICENSE](LICENSE)
- [LICENSE-CC0](LICENSE-CC0)
- [LICENSE-MIT](LICENSE-MIT)
- [OWNERS.md](OWNERS.md)

</details>



This page documents the contribution workflow for the `prompts.chat` repository. It covers the dual contribution model (web interface for prompts and GitHub pull requests for code), quality gates, issue templates, automated contributor attribution via CSV/Git synchronization, governance, and licensing models.

Sources: [CONTRIBUTING.md:1-15]()

---

## Two Contribution Paths

The repository accepts contributions through two distinct paths depending on the nature of the change:

| Path | What it covers | Authentication Required |
|---|---|---|
| **Prompt submission via UI** | Adding or updating prompts in the library | GitHub account authentication on `prompts.chat` [CONTRIBUTING.md:9-11]() |
| **Code contribution via PR** | Bug fixes, documentation, feature work | GitHub account on `github.com` [CONTRIBUTING.md:25-32]() |

Directly editing `prompts.csv` via a pull request is discouraged to ensure proper formatting, validation, and automated attribution.

Sources: [CONTRIBUTING.md:7-12]()

---

## Path 1: Prompt Submission via the Web UI

Submitting prompts through the web interface triggers an automated synchronization pipeline that writes data to the PostgreSQL database and propagates changes to `prompts.csv` and `PROMPTS.md` [CONTRIBUTING.md:9-12]().

### Data Flow Overview: Prompt Submission and Sync Pipeline

```mermaid
sequenceDiagram
    participant User as "UserNaturalLanguageSpace"
    participant API as "Route_api_prompts"
    participant DB as "PostgreSQL_db_prompt"
    participant CSV_API as "Route_src_app_prompts_csv"
    participant GHA as "GitHubAction_update_contributors"
    participant GIT as "GitRepository_prompts_csv"

    User->>API: "Submit new prompt with GitHub auth"
    API->>DB: "db.prompt.create() record insertion"
    DB-->>API: "Success response"
    API-->>User: "201 Created"

    Note over GHA: "Nightly or triggered workflow execution"
    GHA->>CSV_API: "GET /api/prompts.csv"
    CSV_API->>DB: "Query non-private non-deleted prompts"
    DB-->>CSV_API: "Prompt records with authors"
    CSV_API-->>GHA: "Return formatted CSV stream"

    GHA->>GIT: "Diff remote CSV with local file"
    GHA->>GIT: "Execute scripts/generate-contributors.sh"
    GHA->>GIT: "Commit to PROMPTS.md and prompts.csv"
```
Sources: [CONTRIBUTING.md:7-14](), [src/app/prompts.csv/route.ts:28-81](), [scripts/generate-contributors.sh:15-130]()

**Implementation Details**:
- The web UI writes submitted prompts to the database using an API endpoint under `src/app/api/prompts`.
- The CSV generated on demand (`GET /api/prompts.csv`) uses `src/app/prompts.csv/route.ts` which selects prompts from the database filtering out private and unlisted entries, and concatenates contributor identifiers into a CSV contributor column [src/app/prompts.csv/route.ts:28-81]().
- The GitHub Action (`update-contributors.yml`) runs periodically or is triggered by PR merges, fetching the remote CSV, diffing against the local `prompts.csv`, and committing prompt additions with attributed authorship via scripted commits in `scripts/generate-contributors.sh` [scripts/generate-contributors.sh:15-130]().

Sources: [CONTRIBUTING.md:7-14](), [src/app/prompts.csv/route.ts:28-81](), [scripts/generate-contributors.sh:15-130]()

### GitHub Authentication & Contributor Identifiers

Prompt submission requires signing in with GitHub on `prompts.chat` to authenticate contributors and correctly record attribution.

- The contributor identifier stored in the contributor column of `prompts.csv` is computed by `getUserIdentifier()` defined in `src/app/prompts.csv/route.ts` [src/app/prompts.csv/route.ts:17-24]():
  1. Uses `githubUsername` if present (GitHub OAuth users).
  2. If the email ends with `@unclaimed.prompts.chat` (an imported GitHub user), uses their `username`.
  3. Otherwise, falls back to the user's email.

Sources: [CONTRIBUTING.md:10-14](), [src/app/prompts.csv/route.ts:17-24]()

### Prompt Quality Gates

`CONTRIBUTING.md` outlines prompt quality requirements enforced through community review and UI design:
- **Test Your Prompt**: Ensure the prompt generates intended results and can be used by others [CONTRIBUTING.md:20]().
- **Be Descriptive**: Give your prompt a clear, concise title [CONTRIBUTING.md:21]().
- **Be Original**: Don't submit duplicates of existing prompts [CONTRIBUTING.md:22]().
- **Be Appropriate**: Keep content suitable for all audiences [CONTRIBUTING.md:23]().

Sources: [CONTRIBUTING.md:18-23]()

---

## Path 2: Code Contributions via Pull Request

For bug fixes, documentation improvements, or other non-prompt contributions, contributors use traditional GitHub fork-and-pull-request workflows.

### Pull Request Workflow

```mermaid
flowchart TD
    Fork["ForkRepository"]
    Branch["CreateFeatureBranch"]
    Commit["WriteAndCommitCode"]
    PR["OpenPullRequestOnMain"]
    CI["RunCIWorkflow_ci_yml"]
    Review["MaintainerReview"]
    Merge["MergeAfterApproval"]

    Fork --> Branch --> Commit --> PR --> CI --> Review --> Merge
```
Sources: [CONTRIBUTING.md:25-31]()

- Contributors fork the repository on GitHub [CONTRIBUTING.md:29]().
- Create a branch for your changes [CONTRIBUTING.md:30]().
- Submit a pull request with a descriptive title and explanation [CONTRIBUTING.md:31]().

Sources: [CONTRIBUTING.md:25-31]()

---

## Issue Policy & Templates

The repository disables blank issues via the issue template config (`.github/ISSUE_TEMPLATE/config.yml`) and provides curated contact links for users:
- **Submit a New Prompt**: Links directly to the prompt submission page at `https://prompts.chat/prompts/new` [.github/ISSUE_TEMPLATE/config.yml:3-5]().
- **Report a Bug / Spam**: Opens a bug report issue template with a prefilled title [.github/ISSUE_TEMPLATE/config.yml:6-8]().

Off-topic issues or advertisements will be closed immediately, and posting users reported to GitHub for spam and malicious activity [CONTRIBUTING.md:37-39]().

Sources: [.github/ISSUE_TEMPLATE/config.yml:1-8](), [CONTRIBUTING.md:37-39]()

---

## Contributor Attribution System

To automatically attribute prompt contributions, the system combines CSV metadata and Git commit authorship using scripted workflows.

### Code Entity Mapping for Attribution

```mermaid
flowchart LR
    subgraph CodeSpaceAPI ["src/app/prompts.csv/route.ts"]
        GET_CSV["Route_GET_prompts_csv"]
        getUserID["getUserIdentifier_function"]
    end

    subgraph CodeSpaceScript ["scripts/generate-contributors.sh"]
        parseContrib["parse_contributors_function"]
        buildMsg["build_commit_msg_function"]
        setGitEnv["SetGitEnvironmentVariables"]
        gitCommit["GitCommitExecution"]
    end

    subgraph GitRepository ["Git Repository State"]
        csvContributor["prompts.csv Contributor Column"]
        gitCommitNode["Git Commit With Authorship"]
        coAuthorTrailer["Co-Authored-By Trailer"]
        mdDetails["PROMPTS.md Markdown Details Block"]
    end

    getUserID --> GET_CSV
    GET_CSV --> csvContributor
    csvContributor --> parseContrib
    parseContrib --> buildMsg
    buildMsg --> gitCommit
    parseContrib --> setGitEnv
    setGitEnv --> gitCommit
    gitCommit --> gitCommitNode
    gitCommitNode --> coAuthorTrailer
    gitCommitNode --> mdDetails
```
Sources: [src/app/prompts.csv/route.ts:17-81](), [scripts/generate-contributors.sh:94-185]()

- `src/app/prompts.csv/route.ts` exports database prompt data into CSV with contributor information by applying `getUserIdentifier()` [src/app/prompts.csv/route.ts:17-24]().
- The automation script `scripts/generate-contributors.sh` parses contributor strings via `parse_contributors()`, builds commit messages with co-author trailers using `build_commit_msg()`, sets Git author environment variables, and commits changes [scripts/generate-contributors.sh:94-130]().

Sources: [src/app/prompts.csv/route.ts:17-24](), [scripts/generate-contributors.sh:94-185]()

---

## Admin Import Tools & History Rebuilding

- The admin interface includes import components (`src/components/admin/import-prompts.tsx`) to bulk import or delete prompts.
- Maintainers can rewrite Git history using `scripts/rebuild-history.sh` to accurately attribute each prompt to its contributors with commits and co-author trailers when necessary.

Sources: [src/components/admin/import-prompts.tsx:35-100](), [scripts/rebuild-history.sh:1-153]()

---

## Governance and Licensing

### Governance Model

The governance of the project is defined in `GOVERNANCE.md` and `OWNERS.md`:
- **Users**: Browse, self-host, use the CLI, or integrate with MCP server [GOVERNANCE.md:10-14]().
- **Contributors**: Submit prompts through the web platform, open PRs, report bugs, improve documentation [GOVERNANCE.md:16-18]().
- **Maintainers**: Commit access, review and merge PRs, triage issues, listed in `OWNERS.md` [GOVERNANCE.md:20-42](), [OWNERS.md:1-15]().
- **Project Lead**: Final decision-making authority on project direction, releases, and governance changes [GOVERNANCE.md:29-32](), [OWNERS.md:7-9]().
- **Decision Process**: Standard PR reviews for day-to-day work; lazy consensus with a 7-day feedback window for architectural changes [GOVERNANCE.md:45-53]().

Sources: [GOVERNANCE.md:1-61](), [OWNERS.md:1-15]()

### Licensing Model

The repository uses a dual-license approach, declared in the top-level `LICENSE` file:
- **Source code and site-authored content**: Licensed under the MIT License (`src/`, `prisma/`, `scripts/`, and all configuration/build files, including interactive book content in `src/content/book/`) [LICENSE:3-7]().
- **Prompt content and data**: Dedicated to the public domain under CC0 1.0 Universal (`prompts.csv`, `PROMPTS.md`, and user-submitted text) [LICENSE:9-11]().
- If unsure, the MIT License applies by default [LICENSE:13-14]().

Sources: [LICENSE:1-14](), [LICENSE-MIT:1-21](), [LICENSE-CC0:1-121]()

---

# Page: Code Standards

# Code Standards

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [eslint.config.mjs](eslint.config.mjs)
- [packages/prompts.chat/scripts/generate-docs.ts](packages/prompts.chat/scripts/generate-docs.ts)
- [packages/prompts.chat/src/builder/index.ts](packages/prompts.chat/src/builder/index.ts)
- [packages/prompts.chat/src/cli/components/PromptList.tsx](packages/prompts.chat/src/cli/components/PromptList.tsx)
- [packages/prompts.chat/src/parser/index.ts](packages/prompts.chat/src/parser/index.ts)
- [src/components/ide/examples/generated.ts](src/components/ide/examples/generated.ts)
- [src/components/prompts/skill-diff-viewer.tsx](src/components/prompts/skill-diff-viewer.tsx)
- [src/components/prompts/skill-editor.tsx](src/components/prompts/skill-editor.tsx)
- [src/data/api-docs.ts](src/data/api-docs.ts)
- [src/data/method-options.ts](src/data/method-options.ts)
- [src/data/type-definitions.ts](src/data/type-definitions.ts)

</details>



This page explains the coding standards, ESLint configuration, custom MDX linting scripts, formatting rules, and Pull Request (PR) guidelines enforced across the `prompts.chat` codebase to ensure maintainability, type safety, and code consistency.

---

## Overview & Scope

The `prompts.chat` project enforces coding standards through automated static analysis, linting, formatting, and strict type checking. These guidelines cover all source code, API routes, React components, and MDX educational content files.

Sources: [eslint.config.mjs:1-46](), [packages/prompts.chat/scripts/generate-docs.ts:1-1261]()

---

## TypeScript & Type Safety

The codebase is implemented entirely in **TypeScript** with strict type checking enabled to prevent runtime errors and ensure strict API contracts.

- **Strict Mode**: Configured via `tsconfig.json` to disallow implicit `any` and enforce strict null checks.
- **Runtime Validation**: External payloads and configuration objects are validated using Zod schemas and parser utilities (e.g., `ParsedPrompt` interface in [packages/prompts.chat/src/parser/index.ts:28-46]()).
- **Explicit Typing**: All exported functions, API handlers, and React component props define explicit types or interfaces (e.g., `PromptListProps` in [packages/prompts.chat/src/cli/components/PromptList.tsx:7-18]() and `SkillEditorProps` in [src/components/prompts/skill-editor.tsx:38-42]()).

### Type System & Parsing Pipeline

The project uses a robust system for generating type definitions and API documentation from TypeScript source files. The `generate-docs.ts` script [packages/prompts.chat/scripts/generate-docs.ts:1-1261]() parses TypeScript files to extract information about interfaces, types, functions, and classes, including JSDoc comments for descriptions, parameters, and examples. This information is then used to generate:
- **API Documentation**: Stored in `src/data/api-docs.ts` [src/data/api-docs.ts:1-3337](), which powers the in-IDE documentation sidebar.
- **Type Definitions**: Stored in `src/data/type-definitions.ts` [src/data/type-definitions.ts:1-948](), providing rich autocomplete and type hints for the prompt builders.
- **Method Options**: Stored in `src/data/method-options.ts` [src/data/method-options.ts:1-37](), used for Monaco editor autocompletion.

### Diagram: Type System & Parsing Pipeline (Natural Language to Code Entity Space)

```mermaid
graph TD
    NaturalLanguagePromptSpace["NaturalLanguagePromptSpace"] -->|"parseMarkdown() / parseSimpleYaml()"| ParserCode["packages/prompts.chat/src/parser/index.ts"]
    ParserCode -->|"Outputs ParsedPrompt"| TypeInterface["ParsedPromptInterface"]
    TypeInterface -->|"Used by CLI"| PromptListComp["PromptListProps"]
    TypeInterface -->|"Used by Editor"| SkillEditorComp["SkillEditorProps"]

    TS_Source_Files["TS_Source_Files_builder_parser"] -->|"Parsed by Compiler API"| Generate_Docs_Script["packages/prompts.chat/scripts/generate-docs.ts"]
    Generate_Docs_Script -->|"Extracts DocEntry"| Intermediate_Data["Intermediate Documentation Data"]
    Intermediate_Data -->|"Generates"| API_DOCS_TS["src/data/api-docs.ts"]
    Intermediate_Data -->|"Generates"| TYPE_DEFINITIONS_TS["src/data/type-definitions.ts"]
    Intermediate_Data -->|"Generates"| METHOD_OPTIONS_TS["src/data/method-options.ts"]

    API_DOCS_TS --> IDE_Sidebar["IDE Documentation Sidebar"]
    TYPE_DEFINITIONS_TS --> Monaco_Autocomplete["Monaco Editor Autocomplete"]
    METHOD_OPTIONS_TS --> Monaco_Autocomplete
```

Sources: [packages/prompts.chat/scripts/generate-docs.ts:1-1261](), [src/data/api-docs.ts:1-3337](), [src/data/type-definitions.ts:1-948](), [src/data/method-options.ts:1-37](), [packages/prompts.chat/src/parser/index.ts:28-46](), [packages/prompts.chat/src/cli/components/PromptList.tsx:7-18](), [src/components/prompts/skill-editor.tsx:38-42]()

---

## Linting, Formatting & Static Analysis

### ESLint Configuration

Static analysis is driven by **ESLint 9**, integrating Next.js core web vitals and TypeScript rules. The setup is defined in `eslint.config.mjs`.

- **Presets**: Extends `eslint-config-next/core-web-vitals` and `eslint-config-next/typescript` [eslint.config.mjs:6-7]().
- **Global Ignores**: Excludes build outputs, generated Prisma code, raycast extensions, and migration scripts via `globalIgnores()` [eslint.config.mjs:9-23]().
- **Rule Downgrades**: To facilitate gradual adoption, strict rules are downgraded to warnings. For example, `react-hooks/set-state-in-effect` and `@typescript-eslint/no-unsafe-function-type` are set to `warn` [eslint.config.mjs:28-36]().

Sources: [eslint.config.mjs:1-46]()

### MDX Linting Pipeline

Educational content authored in MDX is validated via lint scripts to ensure proper JSX syntax and formatting.

- **MDXLinter Class**: Manages file reading and executing verification passes across MDX files [packages/prompts.chat/scripts/generate-docs.ts:1-1261]().
- **Checks**:
  - `checkEmptyFile()`: Catches empty MDX content.
  - `checkUnbalancedBraces()`: Validates matching `{}` and `[]` outside code blocks.
  - `checkJSXTags()`: Validates component pairing against self-closing and block components.

### Diagram: MDX Linter & Static Analysis Entity Flow (Natural Language to Code Entity Space)

```mermaid
graph TD
    EducationalMarkdownTextSpace["EducationalMarkdownTextSpace"] -->|"Validated by"| MDXLinterClass["MDXLinter_scripts_lint_mdx"]
    MDXLinterClass -->|"Calls"| CheckEmpty["checkEmptyFile"]
    MDXLinterClass -->|"Calls"| CheckBraces["checkUnbalancedBraces"]
    MDXLinterClass -->|"Calls"| CheckJSX["checkJSXTags"]
    
    SourceCodeJS["SourceCodeFileSpace"] -->|"Evaluated by"| ESLintConfig["eslint.config.mjs"]
    ESLintConfig -->|"Applies Rules"| NextVitals["eslint-config-next-core-web-vitals"]
    ESLintConfig -->|"Applies Rules"| NextTS["eslint-config-next-typescript"]
```

Sources: [eslint.config.mjs:1-46](), [packages/prompts.chat/scripts/generate-docs.ts:1-1261]()

---

## File and Directory Conventions

### Naming Patterns

| File Type | Convention | Example |
|---|---|---|
| Page Routes | `page.tsx` | `src/app/page.tsx` |
| API Routes | `route.ts` | `src/app/api/mcp/route.ts` |
| UI Components | `kebab-case.tsx` | `src/components/prompts/skill-editor.tsx` |
| Utilities | `kebab-case.ts` | `src/lib/utils.ts` |
| Tests | `*.test.ts` | `src/__tests__/lib/utils.test.ts` |

### Diagram: Directory Mapping

```mermaid
graph TB
    Root["RootDirectory"]

    Root --> App["src/app"]
    Root --> Components["src/components"]
    Root --> Lib["src/lib"]
    Root --> Public["public"]

    Components --> Admin["admin"]
    Components --> UI["ui"]
    Components --> Prompts["prompts"]

    App --> Generated["src/generated/prisma"]
    Prompts --> SkillEditor["src/components/prompts/skill-editor.tsx"]
    Prompts --> SkillDiffViewer["src/components/prompts/skill-diff-viewer.tsx"]
```

Sources: [src/components/prompts/skill-editor.tsx:1-556](), [src/components/prompts/skill-diff-viewer.tsx:1-376]()

---

## API Route Standards

API endpoints under `src/app/api/` adhere to Next.js App Router route handler specifications.

- **Method Exports**: Handlers export explicit HTTP verb functions (`GET`, `POST`, `DELETE`).
- **Error Responses**: Standardized JSON error responses with appropriate HTTP status codes (200, 201, 401, 500).
- **Client Synchronization**: Mutations trigger `router.refresh()` on the client to re-fetch Server Component states.

### Diagram: Client-Server Interaction

```mermaid
graph LR
    ClientComponent["ClientComponent"] -- "fetch('/api/...')" --> APIRouteHandler["RouteHandler"]
    APIRouteHandler -- "PrismaClientAccess" --> Database["PostgreSQLDatabase"]
    Database --> APIRouteHandler
    APIRouteHandler --> ResponseData["ResponseData"]

    subgraph ResponseUI["ResponseUIHandling"]
      ResponseData -- "toast.success()" --> UserFeedback["ToastNotification"]
      ResponseData -- "router.refresh()" --> UIUpdate["UIStateUpdate"]
    end
```

Sources: [eslint.config.mjs:1-46]()

---

## Pull Request Guidelines

1. **Prompt Submissions**: Web interface contributions automatically handle author attribution and repository synchronization via the website automation [CONTRIBUTING.md:7-12]().
2. **Testing**: Code changes and bug fixes must include unit or integration tests verified via CI [CONTRIBUTING.md:25-31]().
3. **Linting Compliance**: All PRs must pass ESLint and MDX linter checks without errors [eslint.config.mjs:1-46]().
4. **Environment Secrets**: Never commit `.env`, `.env.local`, or build plugins; rely on `.env.example` templates.

Sources: [CONTRIBUTING.md:1-39](), [eslint.config.mjs:1-46]()

---

## Summary

The `prompts.chat` code standards enforce strict type safety, automated linting for code and MDX documentation, consistent directory structures, and structured PR validation workflows to maintain a robust open-source codebase.

Sources: [eslint.config.mjs:1-46](), [CONTRIBUTING.md:1-39](), [packages/prompts.chat/scripts/generate-docs.ts:1-1261]()

---

# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/__tests__/api/health.test.ts](src/__tests__/api/health.test.ts)
- [src/__tests__/api/prompts.test.ts](src/__tests__/api/prompts.test.ts)
- [src/__tests__/api/register.test.ts](src/__tests__/api/register.test.ts)
- [src/__tests__/lib/date.test.ts](src/__tests__/lib/date.test.ts)
- [src/__tests__/lib/format.test.ts](src/__tests__/lib/format.test.ts)
- [src/__tests__/lib/prompt-list.test.ts](src/__tests__/lib/prompt-list.test.ts)
- [src/__tests__/lib/utils.test.ts](src/__tests__/lib/utils.test.ts)
- [src/__tests__/lib/variable-detection.test.ts](src/__tests__/lib/variable-detection.test.ts)
- [src/app/workflows/page.tsx](src/app/workflows/page.tsx)
- [src/lib/prompt-list.ts](src/lib/prompt-list.ts)
- [vitest.setup.ts](vitest.setup.ts)

</details>



This page documents the testing infrastructure, verification patterns, and execution environments for the prompts.chat codebase. It covers the test framework configuration in `vitest.config.ts` (implied by runner configuration) and `vitest.setup.ts` [vitest.setup.ts:1-112](), test organization across API routes, libraries, components, and layouts, coverage reporting via V8, and continuous integration workflows.

For related development standards, see [Code Standards](). For contribution workflows, see [Contribution Workflow]().

Sources: [vitest.setup.ts:1-112]()

---

## Test Framework & Configuration

The prompts.chat codebase uses **Vitest** as its primary test runner and assertion framework, integrated with React testing plugins for component rendering support. Vitest offers native TypeScript execution, fast ESM loading, and a Jest-compatible API.

The configuration environment sets up:
- **Environment**: Set to `jsdom` to simulate a browser DOM context for component and UI tests.
- **Setup Files**: Executes `./vitest.setup.ts` prior to test suites [vitest.setup.ts:9-17]().
- **Test File Matching**: Includes all files matching `src/**/*.{test,spec}.{ts,tsx}`.
- **Path Aliases**: Maps `@/` to `./src` to match Next.js import conventions.

Sources: [vitest.setup.ts:1-112]()

---

## Test Execution Commands

Key test execution tasks are structured around Vitest CLI flags:

| Script / Command | Description |
|------------------|-------------|
| `vitest run` | Execute all test suites once and exit |
| `vitest` | Run tests in interactive watch mode |
| `vitest --ui` | Launch Vitest browser-based dashboard |
| `vitest run --coverage` | Generate code coverage metrics via V8 provider |

Sources: [vitest.setup.ts:1-112]()

---

## Global Test Setup & Mocks

All unit and integration tests initialize within the environment configured in `vitest.setup.ts`. This file intercepts global mocks, Next.js routing and headers, stubs the Prisma client, and provides default configuration mocks.

### Mock Categories in `vitest.setup.ts`
- **Console Silencing**: Overrides `console.error` and `console.log` during test runs to suppress expected error-handling noise [vitest.setup.ts:4-17]().
- **Environment Stubs**: Sets dummy values for `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, and `DATABASE_URL` [vitest.setup.ts:19-23]().
- **Next.js Modules**: Mocks `next/navigation` (`useRouter`, `useSearchParams`, `redirect`, `notFound`), `next/headers` (`cookies`, `headers`), and `next-intl` localization hooks [vitest.setup.ts:24-64]().
- **Prisma Client (`db`)**: Provides `vi.fn()` method stubs for database models (`user`, `prompt`, `category`) as well as raw queries (`$queryRaw`, `$executeRaw`) and transactions (`$transaction`) [vitest.setup.ts:66-99]().
- **Configuration (`getConfig`)**: Mocks application config loading to permit unauthenticated test contexts [vitest.setup.ts:101-112]().

Sources: [vitest.setup.ts:1-112]()

---

## Testing Stack Architecture

The testing infrastructure bridges requirements expressed in natural language to specific code entities and test modules.

### Test Entity Mapping Diagram

```mermaid
graph TD
    subgraph NaturalLanguageSpace["Natural Language Space"]
        Req1["Users can register via API"]
        Req2["Database health checks report connectivity"]
        Req3["Prompts detect embedded variables"]
        Req4["API returns paginated prompts"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        RegRoute["POST /api/auth/register src/app/api/auth/register/route.ts"]
        HealthRoute["GET /api/health src/app/api/health/route.ts"]
        VarLib["detectVariables() src/lib/variable-detection.ts"]
        PromptsRoute["GET /api/prompts src/app/api/prompts/route.ts"]
    end

    subgraph TestEntitySpace["Test Entity Space"]
        RegTest["src/__tests__/api/register.test.ts"]
        HealthTest["src/__tests__/api/health.test.ts"]
        VarTest["src/__tests__/lib/variable-detection.test.ts"]
        PromptsTest["src/__tests__/api/prompts.test.ts"]
    end

    Req1 --> RegRoute
    Req2 --> HealthRoute
    Req3 --> VarLib
    Req4 --> PromptsRoute

    RegRoute -.-> RegTest
    HealthRoute -.-> HealthTest
    VarLib -.-> VarTest
    PromptsRoute -.-> PromptsTest
    
    RegTest -- uses --> DB["db Prisma client mock"]
    HealthTest -- uses --> QueryRaw["db.$queryRaw mock"]
    PromptsTest -- uses --> PromptDB["db.prompt mock"]
    PromptsTest -- uses --> AuthMock["auth mock"]
```

Sources: [src/__tests__/api/register.test.ts:1-16](), [src/__tests__/api/health.test.ts:1-11](), [src/__tests__/lib/variable-detection.test.ts:1-8](), [src/__tests__/api/prompts.test.ts:1-27]()

---

## Test Implementation Patterns

Tests are organized into API route integration tests, component tests, and utility unit tests.

### API Route & Endpoint Testing

API route handlers are tested directly by passing constructed `Request` objects and evaluating returned `Response` payloads and status codes.

- **Registration API (`POST /api/auth/register`)**: Validates payload fields (name, username, email, password rules), checks registration feature flags, and verifies handling of Prisma unique constraint violations (`P2002`) [src/__tests__/api/register.test.ts:49-223]().
- **Health Check API (`GET /api/health`)**: Verifies healthy (200 OK) responses when `db.$queryRaw` succeeds and unhealthy (503 Service Unavailable) responses when database connections throw errors [src/__tests__/api/health.test.ts:12-66]().
- **Prompts API (`GET /api/prompts`)**: Tests pagination, filtering by type, category, and search query, and ensures correct exclusion of bot/classifier prompts by default [src/__tests__/api/prompts.test.ts:55-216]().

Sources: [src/__tests__/api/register.test.ts:49-223](), [src/__tests__/api/health.test.ts:12-66](), [src/__tests__/api/prompts.test.ts:55-216]()

### Library & Utility Unit Testing

Pure functions and helper libraries are tested under isolated conditions.

- **Date Formatting (`src/__tests__/lib/date.test.ts`)**: Uses Vitest fake timers (`vi.useFakeTimers()`) to verify relative date calculations (`formatDistanceToNow`, `formatDate`) across multiple locales (`en`, `tr`, `es`, `zh`, `ja`, `ar`) [src/__tests__/lib/date.test.ts:1-147]().
- **Variable Detection (`src/__tests__/lib/variable-detection.test.ts`)**: Asserts correct extraction of prompt variables across different syntaxes (`[[...]]`, `{{...}}`, `[...]`, `{...}`, `<...>`, `%...%`) while filtering out HTML tags and programming keywords [src/__tests__/lib/variable-detection.test.ts:1-192]().
- **Utility Helpers (`src/__tests__/lib/utils.test.ts`)**: Tests CSS class merging via `cn()`, LIKE pattern escaping via `escapeLikePattern()`, and browser user-agent sniffing via `isChromeBrowser()` with stubbed global environments [src/__tests__/lib/utils.test.ts:1-129]().
- **Prompt List Helpers (`src/__tests__/lib/prompt-list.test.ts`)**: Verifies the `trendingPromptListWhere` and `promptListTypeWhere` functions correctly construct Prisma `where` clauses for filtering prompts, specifically handling the exclusion of `BOT` and `CLASSIFIER` types [src/__tests__/lib/prompt-list.test.ts:1-28]().
- **JSON Formatting (`src/__tests__/lib/format.test.ts`)**: Tests `prettifyJson` for correct indentation and `isValidJson` for accurate validation of JSON strings, including handling of malformed input [src/__tests__/lib/format.test.ts:1-161]().

Sources: [src/__tests__/lib/date.test.ts:1-147](), [src/__tests__/lib/variable-detection.test.ts:1-192](), [src/__tests__/lib/utils.test.ts:1-129](), [src/__tests__/lib/prompt-list.test.ts:1-28](), [src/__tests__/lib/format.test.ts:1-161]()

---

### Data Flow in API Tests

```mermaid
sequenceDiagram
    participant TestRunner as "Vitest Test Runner"
    participant RouteHandler as "API Route (e.g. GET /api/health)"
    participant MockDB as "Prisma Client Mock (db)"

    TestRunner->>MockDB: "Stub query method (e.g. $queryRaw)"
    TestRunner->>RouteHandler: "Invoke handler function"
    RouteHandler->>MockDB: "Execute database probe"
    MockDB-->>RouteHandler: "Return connection result or throw Error"
    RouteHandler-->>TestRunner: "Return Response object (200 / 503)"
    TestRunner->>TestRunner: "Assert HTTP status and JSON payload"
```

Sources: [src/__tests__/api/health.test.ts:12-66]()

---

## Coverage and Continuous Integration

### Coverage Reporting

Test coverage is measured via V8 by executing coverage flags. Exclusions are configured for build outputs, type definitions, and test configuration files to ensure accurate metrics on source code.

Sources: [vitest.setup.ts:1-112]()

### CI Pipeline Integration

Automated checks run on every push and pull request via GitHub Actions workflows, executing dependency installation, linting, and Vitest execution.

Sources: [vitest.setup.ts:1-112]()

---

## Summary

| Testing Aspect | Implementation Details |
|----------------|------------------------|
| Framework | Vitest + `@testing-library/jest-dom` with React support |
| Global Mocks | Next.js navigation/headers, Prisma client, Config [vitest.setup.ts:24-112]() |
| API Testing | Route handlers invoked with Request objects and mocked DB/Auth |
| Unit Testing | Pure functions (`date`, `variable-detection`, `utils`, `prompt-list`, `format`) |
| Coverage | V8 provider with text, json, and html reporters |

Sources: [vitest.setup.ts:1-112]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [PROMPTS.md](PROMPTS.md)
- [README.md](README.md)
- [messages/ar.json](messages/ar.json)
- [messages/de.json](messages/de.json)
- [messages/en.json](messages/en.json)
- [messages/es.json](messages/es.json)
- [messages/fr.json](messages/fr.json)
- [messages/it.json](messages/it.json)
- [messages/ja.json](messages/ja.json)
- [messages/ko.json](messages/ko.json)
- [messages/pt.json](messages/pt.json)
- [messages/ru.json](messages/ru.json)
- [messages/tr.json](messages/tr.json)
- [messages/zh.json](messages/zh.json)
- [next.config.ts](next.config.ts)
- [prompts.csv](prompts.csv)
- [scripts/generate-contributors.sh](scripts/generate-contributors.sh)
- [scripts/rebuild-history.sh](scripts/rebuild-history.sh)
- [src/app/[username]/page.tsx](src/app/[username]/page.tsx)
- [src/app/api/prompts/[id]/route.ts](src/app/api/prompts/[id]/route.ts)
- [src/app/api/prompts/route.ts](src/app/api/prompts/route.ts)
- [src/app/categories/[slug]/page.tsx](src/app/categories/[slug]/page.tsx)
- [src/app/collection/page.tsx](src/app/collection/page.tsx)
- [src/app/feed/page.tsx](src/app/feed/page.tsx)
- [src/app/prompts.csv/route.ts](src/app/prompts.csv/route.ts)
- [src/app/prompts.json/route.ts](src/app/prompts.json/route.ts)
- [src/app/prompts/[id]/page.tsx](src/app/prompts/[id]/page.tsx)
- [src/app/skills/page.tsx](src/app/skills/page.tsx)
- [src/app/tags/[slug]/page.tsx](src/app/tags/[slug]/page.tsx)
- [src/components/admin/import-prompts.tsx](src/components/admin/import-prompts.tsx)
- [src/components/prompts/discovery-prompts.tsx](src/components/prompts/discovery-prompts.tsx)
- [tests/generate-contributors-format.test.js](tests/generate-contributors-format.test.js)

</details>



## Purpose and Scope

This page provides a comprehensive technical glossary of codebase-specific terms, jargon, abbreviations, and domain concepts used across the `prompts.chat` repository. It bridges natural language concepts with their corresponding code entities, database models, configuration schemas, and API endpoints to assist developers, self-hosters, and contributors in navigating the architecture.

---

## Core Concepts & Data Entities

### Prompt
The fundamental unit of content in the system. While traditionally a single string of text, in this codebase, a `Prompt` is a complex entity stored in the PostgreSQL database and synchronized with flat files (`prompts.csv` and `PROMPTS.md`).

- **Implementation**: Defined as the `Prompt` model in Prisma schema [prisma/schema.prisma:93-145]().
- **Fields**: Includes `title`, `content`, `description`, `type` (e.g., `TEXT`, `SKILL`, `TASTE`, `BOT`, `CLASSIFIER`), and metadata flags like `isPrivate`, `isFeatured`, `isUnlisted`, and `deletedAt` indicating delisting or soft deletion [prisma/schema.prisma:94-146]().
- **Sync**: Prompts are exported to CSV and Markdown for GitHub visibility and community consumption [prompts.csv:1-18](), [PROMPTS.md:1-146]().
- **Versioning**: Prompt versions and change requests are tracked via related relational models [prisma/schema.prisma:147-181]().

Sources:
`prisma/schema.prisma:93-181`,
`prompts.csv:1-18`,
`PROMPTS.md:1-146`

### Act
A specific type of prompt template used to instruct an LLM to "act as" a persona or role (e.g., "Imagine you are an experienced Ethereum developer" or "I want you to act as a linux terminal"). The term traces back to the original dataset framing.

- **Usage**: Appears as the leading phrase in prompt text or titles, designating the persona or role the AI should assume [prompts.csv:2-4]().
- **Relation**: Mapped directly to the `title` and content structure of `Prompt` records.

Sources:
`prisma/schema.prisma:93-145`,
`prompts.csv:2-4`

### Agent Skill
A compound prompt type made for AI assistants, providing multiple files that together define an AI agent's capability or specialized skillset.

- **Structure**: Modeled as multi-file prompts requiring at least a `SKILL.md` file, plus optional auxiliary configuration and supporting files [messages/en.json:124-124]().
- **Implementation**: `Prompt` entities stored with `type` set to `SKILL` [prisma/schema.prisma:99-100]().
- **Key Functions**: Managed by skill file utility functions (`parseSkillFiles` and `serializeSkillFiles`).

Sources:
`prisma/schema.prisma:99-100`,
`messages/en.json:124-124`

### Taste
Single Markdown files (`taste.md`) that codify a user’s coding style preferences, conventions, and habits to help AI coding agents generate code aligned with the user's specific tastes.

- **Implementation**: Stored as `Prompt` records with `type` set to `TASTE` [prisma/schema.prisma:99-100]().
- **Purpose**: Enables AI coders to learn and apply personalized style choices during automated code generation [messages/en.json:125-125]().

Sources:
`prisma/schema.prisma:99-100`,
`messages/en.json:125-125`

### Bot & Bot Team
Specialized executable or structured AI agent definitions stored as prompt records with the `BOT` type.

- **Implementation**: Validated via bot schemas and stored in the database with configuration instructions, routines, and required computer setups (cloud, user computer, or both).
- **Bot Teams**: Groups of coordinated bots working together with defined handoffs and operational workflows, rendered as interactive dependency graphs on `/bots/teams` [README.md:77-77]().

Sources:
`prisma/schema.prisma:93-145`,
`README.md:77-77`

### Classifier
A specialized prompt type (`CLASSIFIER`) used to define decision models for AI agents. These structured prompts guide an AI through a series of questions, branches, and scoring criteria to arrive at a definitive classification or decision tree path.

- **Implementation**: `Prompt` records with `type` set to `CLASSIFIER` [prisma/schema.prisma:99-100]().
- **Usage**: Used for building decision chains and managed in `src/lib/classifiers` [messages/en.json:47-47]().

Sources:
`prisma/schema.prisma:99-100`,
`messages/en.json:47-47`

### Jev/Kev
Decision model structures or specialized evaluation algorithms used within the Classifier subsystem to determine routing and terminal states for automated queries.

- **Usage**: Referenced within decision model processing logic and fixtures for advanced classification chains.

Sources:
`messages/en.json:47-47`

### Connector & Harness
Integration interfaces and execution wrappers used by bots and prompts to interact with external tools, APIs, and runtime execution environments.

- **Connector**: External service integrations or MCP server connections specified in bot configuration definitions.
- **Harness**: The execution wrapper or platform environment (e.g., OpenClaw, AutoGPT, Claude Code) that hosts and runs bot bundles.

Sources:
`README.md:76-78`

### Promptmaster
A recognized community contributor or power user with significant engagement metrics, such as prompt creation volume, upvotes, change request contributions, and moderation activity [messages/en.json:42-42](). Featured on the platform leaderboard.

Sources:
`messages/en.json:42-42`

### MCP (Model Context Protocol)
An open protocol and server integration exposed at `/api/mcp` that allows AI models, IDEs, and local clients (such as Claude Code) to query prompt libraries, search tools, execute prompts, and access agent skills in a standardized manner.

- **Server Endpoint**: Mounted at `/api/mcp` supporting tool registration and retrieval methods [messages/en.json:162-163]().

Sources:
`messages/en.json:162-163`

### Delisting
An administrative moderation action that hides a prompt, bot, or skill from public listings and search results without permanently deleting the database record.

- **Fields**: Governed by `isUnlisted`, `unlistedAt`, and `delistReason` fields on the `Prompt` model [prisma/schema.prisma:114-116]().
- **Reasons**: Automatic or manual triggers including content being too short, non-English text, low quality scores, failure to act as an instruction, or direct administrator action [messages/en.json:187-193]().

Sources:
`prisma/schema.prisma:114-116`,
`messages/en.json:187-193`

### Clone Branding
A white-labeling feature enabling self-hosted deployments to completely override default branding assets, including site name, custom logo files, descriptions, and metadata.

- **Flag**: Controlled by the `useCloneBranding` configuration flag, which hides upstream branding badges and adapts UI copy for private instances [README.md:115-115]().

Sources:
`README.md:115-115`

### PCHAT_*
Environment variables prefixed with `PCHAT_` used to override default system configurations at runtime across Docker containers and self-hosted environments.

- **Usage**: Processed by the configuration pipeline (`defineConfig` / `getConfig`), allowing environment-based overrides for branding, themes, features, and API credentials [README.md:145-146]().

Sources:
`README.md:145-146`

### workflowLink
An optional URL associated with a prompt that links to an external web demo or interactive environment showcasing a workflow chain composed of connected prompts [messages/en.json:167-167]().

- **Field**: Stored as `workflowLink` on the prompt record [prisma/schema.prisma:134]().
- **Visibility**: Enabled when a prompt has active downstream or upstream connections (`PromptConnection`) [messages/en.json:167-167]().

Sources:
`prisma/schema.prisma:134`,
`messages/en.json:167-167`

### Unclaimed Account
A placeholder user account created automatically from Git commit attribution (`Co-authored-by` trailers) before the actual individual has registered or logged into the platform.

- **Scenario**: Assigned an email ending in `@unclaimed.prompts.chat` to preserve open-source attribution integrity prior to manual account linking [src/app/prompts.csv/route.ts:17-24]().

Sources:
`src/app/prompts.csv/route.ts:17-24`

---

## Data Flow & Implementation Diagrams

### Prompt Data Representation Flow
```mermaid
graph TD
  NL[""Natural Language Space""] -->|"User Action / API"| API_PROMPTS[""/api/prompts (POST/PUT)""]

  API_PROMPTS --> DB_PROMPT[""Prompt (Prisma Model)""]
  API_PROMPTS --> DB_PROMPT_VERSION[""PromptVersion (Prisma Model)""]
  API_PROMPTS --> DB_CHANGE_REQUEST[""ChangeRequest (Prisma Model)""]

  DB_PROMPT -- "Read/Sync" --> CSV_EXPORT[""prompts.csv (GET /prompts.csv)""]
  DB_PROMPT -- "Read/Sync" --> MD_EXPORT[""PROMPTS.md (GitHub Export)""]

  API_PROMPTS -- "Exposes" --> MCP_SERVER[""/api/mcp (Model Context Protocol)""]
  MCP_SERVER --> DB_PROMPT

  DB_PROMPT -- "Type: SKILL" --> SKILL_FILES[""src/lib/skill-files.ts""]
  DB_PROMPT -- "Type: BOT" --> BOT_SCHEMA[""src/lib/bots/schema.ts""]
  DB_PROMPT -- "Type: CLASSIFIER" --> CLASSIFIER_SCHEMA[""src/lib/classifiers/schema.ts""]
```
Sources:
`prisma/schema.prisma:93-181`,
`src/app/api/prompts/route.ts:1-190`,
`src/app/prompts.csv/route.ts:1-50`,
`scripts/generate-contributors.sh:1-50`

### Configuration Pipeline Mapping
```mermaid
graph LR
  CFG_FILE[""prompts.config.ts""] --> CFG_PIPELINE[""defineConfig (src/lib/config)""]
  ENV_VARS[""Environment Variables (PCHAT_*)""] --> CFG_PIPELINE

  CFG_PIPELINE --> BRANDING_CFG[""BrandingConfig""]
  CFG_PIPELINE --> THEME_CFG[""ThemeConfig""]
  CFG_PIPELINE --> FEATURES_CFG[""FeaturesFlags""]
  CFG_PIPELINE --> AUTH_CFG[""AuthConfig""]

  BRANDING_CFG --> UI_BRANDING[""UI Components (Logo, Name)""]
  THEME_CFG --> CSS_VARS[""Global CSS Variables""]
  FEATURES_CFG --> API_ROUTES[""API Route Logic""]
  AUTH_CFG --> NEXTAUTH[""NextAuth.js Providers""]

  subgraph Runtime Access
    GET_CONFIG[""getConfig() / getConfigSync()""]
  end
  CFG_PIPELINE --> GET_CONFIG
```
Sources:
`README.md:115-146`,
`messages/en.json:1-3045`

---

## Summary

This glossary defines the essential technical vocabulary, domain entities, and data structures implemented across the `prompts.chat` codebase, linking natural-language AI concepts directly to their underlying code representations.

Sources:
`prisma/schema.prisma`,
`README.md`,
`messages/en.json`