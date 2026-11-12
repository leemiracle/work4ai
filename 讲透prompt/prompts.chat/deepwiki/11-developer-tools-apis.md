<!-- source: DeepWiki mcp.deepwiki.com · repo f/prompts.chat · page 11 Developer Tools & APIs · fetched 2026-11-09 -->

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

