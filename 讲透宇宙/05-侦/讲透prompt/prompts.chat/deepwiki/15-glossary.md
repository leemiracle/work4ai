<!-- source: DeepWiki mcp.deepwiki.com · repo f/prompts.chat · page 15 Glossary · fetched 2026-11-09 -->

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