<!-- source: DeepWiki mcp.deepwiki.com · repo different-ai/openwork · extra page Skills and Commands · fetched 2026-10-26 -->

# Skills and Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/app/src/react-app/domains/settings/state/extensions-store.ts](apps/app/src/react-app/domains/settings/state/extensions-store.ts)
- [apps/server/src/cloud-plugins.ts](apps/server/src/cloud-plugins.ts)
- [apps/server/src/connect-mcp-transport.ts](apps/server/src/connect-mcp-transport.ts)
- [apps/server/src/connect-skill-catalog.ts](apps/server/src/connect-skill-catalog.ts)
- [apps/server/src/opencode-plugins/openwork-cloud-skills-v2.ts](apps/server/src/opencode-plugins/openwork-cloud-skills-v2.ts)
- [apps/server/src/opencode-plugins/openwork-context-v2.ts](apps/server/src/opencode-plugins/openwork-context-v2.ts)
- [apps/server/src/opencode-plugins/openwork-read-transport.ts](apps/server/src/opencode-plugins/openwork-read-transport.ts)
- [apps/server/src/opencode-plugins/openwork-session-groups.ts](apps/server/src/opencode-plugins/openwork-session-groups.ts)
- [apps/server/src/opencode-v2-context-bridge.ts](apps/server/src/opencode-v2-context-bridge.ts)
- [apps/server/src/opencode-v2-instructions.ts](apps/server/src/opencode-v2-instructions.ts)
- [apps/server/src/openwork-workspace-config-store.ts](apps/server/src/openwork-workspace-config-store.ts)
- [apps/server/src/routes/core.ts](apps/server/src/routes/core.ts)
- [apps/server/src/session-groups.ts](apps/server/src/session-groups.ts)
- [apps/server/test/connect-skill-catalog.test.ts](apps/server/test/connect-skill-catalog.test.ts)
- [apps/server/test/openwork-cloud-skills-v2.test.ts](apps/server/test/openwork-cloud-skills-v2.test.ts)
- [apps/server/test/openwork-session-groups.test.ts](apps/server/test/openwork-session-groups.test.ts)
- [ee/apps/den-api/src/mcp/skill-index-sync.ts](ee/apps/den-api/src/mcp/skill-index-sync.ts)
- [ee/apps/den-api/test/api/skill-index-sync.api.test.ts](ee/apps/den-api/test/api/skill-index-sync.api.test.ts)
- [ee/apps/den-api/test/skill-index-sync.test.ts](ee/apps/den-api/test/skill-index-sync.test.ts)

</details>



## Purpose and Scope
This page details the implementation of the Skills and Commands subsystems in OpenWork. It covers how skills are structured, discovered, and loaded just-in-time (JIT) across local workspaces and OpenWork Cloud (Connect), as well as how custom commands, templates, and affordances are registered and executed by agents and UI controllers through `createV2ContextBridge` and `ExtensionsStore` [apps/app/src/react-app/domains/settings/state/extensions-store.ts:171-191](), [apps/server/src/opencode-v2-context-bridge.ts:45-48]().

---

## 1. Skill Catalog and Just-In-Time (JIT) Skill Loading

OpenWork maintains a dynamic skill catalog that feeds instructions into agent system prompts without bloating the initial context. The server exposes catalog discovery through `readMcpSkillIndex`, which queries standards-shaped skill indexes (`skill://index.json`) via session readers [apps/server/src/connect-skill-catalog.ts:121-137]().

### Catalog Resolution and Caching
When a workspace requests skill metadata, the server evaluates candidate configurations through `sessionReader` and caches results using `catalogCache` with a configurable TTL (`CATALOG_CACHE_TTL_MS = 30_000`) [apps/server/src/connect-skill-catalog.ts:18-105]().

Title: "Skill Catalog Resolution and Loading Flow"
```mermaid
graph TD
    UserQuery[""UserPromptOrAgentTurn""] --> CatalogResolver[""readMcpSkillIndex(config, fetcher)""]
    CatalogResolver --> SessionReader[""sessionReader(config, fetcher)""]
    SessionReader --> CacheStore[""catalogCache (TTL 30s)""]
    CacheStore --> SkillIndex[""SKILL://index.json""]
    SkillIndex --> SyncSchema[""skillIndexSyncSchema.safeParse()""]
```
Sources: [apps/server/src/connect-skill-catalog.ts:18-137]()

---

## 2. Cloud Skills and OpenWork Connect Integration

Remote agent skills are delivered via OpenWork Connect and exposed through the `openwork-cloud` MCP server namespace. The plugin module `openwork-cloud-skills-v2.ts` manages metadata discovery and digest-verified body loading via `registerCloudSkillDiscovery` [apps/server/src/opencode-plugins/openwork-cloud-skills-v2.ts:142-147]().

### Native Skill Budgeting and Mentions
The function `nativeSkills` formats catalog entries within token budgets, while `mentionedSkillIds` parses prompts for explicit user mentions to load skill bodies on demand before the model executes [apps/server/src/opencode-plugins/openwork-cloud-skills-v2.ts:91-136]().

Title: "Cloud Skill Natural Language to Code Entity Bridge"
```mermaid
graph TD
    NLSpace[""Natural Language Mention / Prompt text""] --> MentionParser[""mentionedSkillIds(text, skills)""]
    MentionParser --> NativeBuilder[""nativeSkills(catalog, contents)""]
    NativeBuilder --> DiscoveryReg[""registerCloudSkillDiscovery(context)""]
    DiscoveryReg --> CloudTransport[""OpenWork Connect MCP Transport""]
```
Sources: [apps/server/src/opencode-plugins/openwork-cloud-skills-v2.ts:91-147]()

---

## 3. Local Skills, Storage, and Lifecycle

Local skills reside directly inside the workspace filesystem under `.opencode/skills/` and are managed on the frontend by `createExtensionsStore` [apps/app/src/react-app/domains/settings/state/extensions-store.ts:171-191]().

### Filesystem Layout and Store Management
The `ExtensionsStore` tracks local skills, plugin scopes, and imported cloud marketplaces, coordinating with desktop IPC commands to read and write local skill templates [apps/app/src/react-app/domains/settings/state/extensions-store.ts:84-104]().

Title: "Extensions Store and Local Skill State Flow"
```mermaid
graph TD
    StoreInit[""createExtensionsStore()""] --> StateSnapshot[""ExtensionsStoreSnapshot""]
    StateSnapshot --> LocalSkillsReader[""listLocalSkills()""]
    StateSnapshot --> ConfigWriter[""writeOpencodeConfig()""]
    ConfigWriter --> SkillWriter[""writeLocalSkill()""]
```
Sources: [apps/app/src/react-app/domains/settings/state/extensions-store.ts:23-40](), [apps/app/src/react-app/domains/settings/state/extensions-store.ts:171-191]()

---

## 4. Custom Commands, Templates, and Context Bridge

OpenWork exposes semantic commands and app-read affordances through `createV2ContextBridge`, which processes tool calls like `openwork_context`, `openwork_query`, `openwork_execute`, `openwork_skills`, and `openwork_skill_read` [apps/server/src/opencode-v2-context-bridge.ts:11-15]().

### Command Execution and Instruction Building
Instructions are provisioned using `buildOpenWorkV2Instructions`, mapping command execution strictly to permitted paths such as session group mutations (`isSessionGroupWritePath`) [apps/server/src/opencode-v2-instructions.ts:8-20](), [apps/server/src/opencode-v2-context-bridge.ts:21-27]().

Title: "Command and Context Bridge Natural Language to Code Entity Bridge"
```mermaid
graph TD
    NLCommand[""Natural Language / Tool Call Request""] --> BridgeRequest[""requestSchema.parse()""]
    BridgeRequest --> ContextBridge[""createV2ContextBridge(hostRequest)""]
    ContextBridge --> ToolQuery[""openwork_query / openwork_context""]
    ContextBridge --> ToolExec[""openwork_execute (SESSION_GROUP_COMMAND_IDS)""]
    ToolExec --> WritePathVal[""isSessionGroupWritePath(path)""]
```
Sources: [apps/server/src/opencode-v2-context-bridge.ts:11-39](), [apps/server/src/opencode-v2-instructions.ts:8-20]()

---

