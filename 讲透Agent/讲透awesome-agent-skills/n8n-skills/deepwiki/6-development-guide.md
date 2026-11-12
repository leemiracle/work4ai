<!-- source: DeepWiki mcp.deepwiki.com · repo czlonkowski/n8n-skills · page 6 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.mcp.json.example](.mcp.json.example)
- [CLAUDE.md](CLAUDE.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/INSTALLATION.md](docs/INSTALLATION.md)
- [docs/MCP_TESTING_LOG.md](docs/MCP_TESTING_LOG.md)
- [docs/USAGE.md](docs/USAGE.md)

</details>



This page outlines the standards and methodologies for contributing to the `n8n-skills` repository. The development process is centered around **Evaluation-Driven Development (EDD)** and **MCP-Informed Content**, ensuring that every skill provides accurate, actionable guidance based on real-world n8n-mcp tool responses [docs/DEVELOPMENT.md:7-12]().

## Development Philosophy

The core philosophy of this repository is to bridge the gap between AI reasoning and actual n8n execution. We achieve this through three primary pillars:

1.  **Evaluation-First**: Tests are written before skill content to establish a baseline and define success [docs/DEVELOPMENT.md:9-11]().
2.  **Evidence-Based**: Content must reflect actual JSON responses from the `n8n-mcp` server, not theoretical assumptions [docs/DEVELOPMENT.md:25-27]().
3.  **Conciseness**: Core skill files are kept under 500 lines to ensure high performance and maintainability, with details offloaded to reference files [docs/DEVELOPMENT.md:39-43]().

### From Natural Language to Code Entities

The following diagram illustrates how a developer's natural language intent is translated into specific code entities and validated through the development lifecycle.

**Development Workflow: Intent to Entity**
```mermaid
graph TD
    subgraph "Natural Language Space"
        "UserIntent"["Developer Intent: 'Teach Webhook Pathing'"]
        "TriggerPhrases"["Activation Triggers: 'webhook', 'path', '$json.body'"]
    end

    subgraph "Code Entity Space"
        "SKILL_MD"["SKILL.md Frontmatter"]
        "EVAL_JSON"["eval-001-webhook.json"]
        "MCP_LOG"["MCP_TESTING_LOG.md"]
        "TOOL_REF"["search_nodes / get_node"]
    end

    "UserIntent" --> "EVAL_JSON"
    "EVAL_JSON" -- "Defines Expected" --> "SKILL_MD"
    "TriggerPhrases" -- "Informs" --> "SKILL_MD"
    "TOOL_REF" -- "Provides Data" --> "MCP_LOG"
    "MCP_LOG" -- "Verifies Facts" --> "SKILL_MD"
```
Sources: [docs/DEVELOPMENT.md:13-21](), [docs/DEVELOPMENT.md:87-113](), [docs/DEVELOPMENT.md:157-164]()

## Evaluation-Driven Development (EDD)

EDD ensures that skills solve real problems. Developers must create at least 3 evaluation scenarios per skill covering basic usage, common mistakes, and advanced scenarios [docs/DEVELOPMENT.md:126-130]().

*   **Baseline Testing**: Run the query without the skill to document the "Low Quality" generic response [docs/DEVELOPMENT.md:114-117]().
*   **Iterative Refinement**: Modify `SKILL.md` until the AI achieves a 100% pass rate against the `expected_behavior` defined in the evaluation JSON [docs/DEVELOPMENT.md:18-21]().

For details on writing effective test cases, see [Evaluation-Driven Development (EDD)](#6.1).

## Creating New Skills

New skills follow a strict directory structure under the `skills/` directory [CLAUDE.md:20-31]().

### Skill Structure and Format
A skill is composed of a primary `SKILL.md` file containing metadata (frontmatter) and core logic, supplemented by specialized reference files [docs/DEVELOPMENT.md:187-202]().

| File | Purpose | Limit |
| :--- | :--- | :--- |
| `SKILL.md` | Main content and activation triggers | < 500 lines |
| `COMMON_MISTAKES.md` | Catalog of errors and fixes | < 200 lines |
| `EXAMPLES.md` | Verified working code snippets | < 200 lines |
| `README.md` | Skill metadata and coverage stats | N/A |

**Skill Component Relationship**
```mermaid
graph LR
    "SKILL_MD"["SKILL.md"] -- "links to" --> "MISTAKES"["COMMON_MISTAKES.md"]
    "SKILL_MD" -- "links to" --> "EXAMPLES"["EXAMPLES.md"]
    "SKILL_MD" -- "references" --> "MCP_TOOLS"["n8n-mcp Tools"]
    
    subgraph "Skill Directory Entity"
        "SKILL_MD"
        "MISTAKES"
        "EXAMPLES"
    end

    "MCP_TOOLS" -- "get_node" --> "SKILL_MD"
    "MCP_TOOLS" -- "validate_node" --> "MISTAKES"
```
Sources: [docs/DEVELOPMENT.md:39-49](), [docs/DEVELOPMENT.md:59-83](), [docs/DEVELOPMENT.md:195-208]()

For a step-by-step walkthrough, see [Creating New Skills](#6.2).

## Testing and Quality Standards

Quality is enforced by the **MCP-Informed Content** rule: never invent examples [docs/DEVELOPMENT.md:50-52](). Developers must use the `MCP_TESTING_LOG.md` to record actual responses from tools like `search_nodes`, `get_node`, and `validate_node` [docs/MCP_TESTING_LOG.md:1-5]().

### Success Criteria
*   **Activation**: The skill must trigger reliably on defined keywords [docs/USAGE.md:11-20]().
*   **Accuracy**: Node types must match the dual-format requirements (e.g., `nodes-base.webhook` for discovery vs `n8n-nodes-base.webhook` for workflows) [docs/MCP_TESTING_LOG.md:59-62]().
*   **Composition**: The skill must play well with others (e.g., `n8n-workflow-patterns` identifies structure, then `n8n-expression-syntax` handles mapping) [CLAUDE.md:151-159]().

For detailed quality guidelines and logs, see [Testing and Quality Standards](#6.3).

Sources: [CLAUDE.md:138-144](), [docs/DEVELOPMENT.md:25-37](), [docs/MCP_TESTING_LOG.md:122-152]()

---

