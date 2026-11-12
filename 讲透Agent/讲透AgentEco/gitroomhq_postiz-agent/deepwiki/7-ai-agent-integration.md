<!-- source: DeepWiki mcp.deepwiki.com · repo gitroomhq/postiz-agent · page 7 AI Agent Integration · fetched 2026-10-27 -->

# AI Agent Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [README.md](README.md)
- [SKILL.md](SKILL.md)
- [skills/postiz/SKILL.md](skills/postiz/SKILL.md)

</details>



The Postiz CLI is designed specifically as a "skill" for AI agents, enabling automated social media management across 28+ platforms [README.md:9-11](). By providing a structured interface for discovery, content preparation, and analytics, agents can autonomously handle the entire lifecycle of a social media campaign.

## The SKILL.md Contract

The integration is governed by a `SKILL.md` contract which defines the tool's capabilities, installation requirements, and the "Discovery Workflow" pattern [SKILL.md:2-27](). This file serves as the manifest that LLM agents (such as those using OpenClaw) use to understand how to interact with the Postiz ecosystem.

For details on the specification and exit code conventions, see [SKILL.md Contract and Discovery Workflow](#7.1).

### Natural Language to CLI Command Mapping

The following diagram bridges the agent's natural language intent to the specific CLI commands defined in the codebase.

**Agent Intent Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'What accounts are connected?'"]
        B["'Post this image to Reddit'"]
        C["'How did my last tweet perform?'"]
        D["'Get Reddit flairs'"]
    end

    subgraph "Code Entity Space (CLI Commands)"
        A --> CMD1["postiz integrations:list"]
        B --> CMD2["postiz upload <path>"]
        CMD2 --> CMD3["postiz posts:create"]
        C --> CMD4["postiz analytics:post <id>"]
        D --> CMD5["postiz integrations:trigger <id> getFlairs"]
    end

    style CMD1 stroke-dasharray: 5 5
    style CMD3 stroke-dasharray: 5 5
```
Sources: [SKILL.md:65-85](), [README.md:72-106]()

## Core Workflow Pattern

Agents follow a standardized 7-step execution pattern to ensure reliability across different social media providers [SKILL.md:48-58]().

1.  **Authenticate**: Verify credentials using `postiz auth:status` [SKILL.md:62]().
2.  **Discover**: Identify target platforms via `postiz integrations:list` [SKILL.md:66]().
3.  **Fetch**: Retrieve dynamic metadata (e.g., Subreddits, Playlists) using `postiz integrations:trigger` [SKILL.md:70]().
4.  **Prepare**: Convert local assets to remote URLs via `postiz upload` [SKILL.md:73]().
5.  **Post**: Execute the publication via `postiz posts:create` [SKILL.md:76]().
6.  **Analyze**: Retrieve performance metrics with `postiz analytics:post` [SKILL.md:80]().
7.  **Resolve**: Handle edge cases where platforms don't return IDs immediately using `posts:missing` and `posts:connect` [SKILL.md:83-84]().

**Agent Execution Lifecycle**
```mermaid
sequenceDiagram
    participant Agent as AI Agent
    participant CLI as postiz CLI (src/index.ts)
    participant API as Postiz API (src/api.ts)

    Agent->>CLI: "auth:status"
    CLI->>API: GET /auth/status
    API-->>Agent: { authenticated: true }

    Agent->>CLI: "integrations:settings <id>"
    CLI->>API: GET /integrations/settings/<id>
    API-->>Agent: { schema, tools }

    Agent->>CLI: "upload <file>"
    CLI->>API: POST /upload (multipart/form-data)
    API-->>Agent: { url: "https://..." }

    Agent->>CLI: "posts:create --json <file>"
    CLI->>API: POST /posts
    API-->>Agent: { id: "post-123" }
```
Sources: [SKILL.md:48-85](), [README.md:213-224]()

## Claude Plugin Configuration

For environments like Claude Desktop or OpenClaw, the Postiz agent is configured via the `.claude-plugin/` directory. This includes the `plugin.json` manifest and `marketplace.json` which define the tool's scope, specifically allowing the agent to execute `Bash(postiz:*)` commands [.claude-plugin/plugin.json:1-27](), [.claude-plugin/marketplace.json:1-22]().

For details on tool scoping and registration, see [Claude Plugin Configuration](#7.2).

## Common Automation Patterns

Agents typically implement the following patterns to handle platform-specific complexities:

| Pattern | CLI Commands Used | Purpose |
| :--- | :--- | :--- |
| **Media Pre-flight** | `upload` | Ensuring files are converted to "Verified URLs" before posting [README.md:253-255](). |
| **Dynamic Discovery** | `integrations:settings` | Determining if a platform requires a "title" or "subreddit" before composing [README.md:81-86](). |
| **Async Resolution** | `posts:missing` → `posts:connect` | Linking TikTok or Instagram posts that don't return an ID immediately [SKILL.md:200-217](). |
| **Draft Promotion** | `posts:status --status schedule` | Moving a generated draft into the live publishing queue [SKILL.md:177-179](). |

Sources: [SKILL.md:48-58](), [README.md:191-192](), [README.md:213-224]()

---

