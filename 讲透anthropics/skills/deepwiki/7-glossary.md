<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/skills · page 7 Glossary · fetched 2026-10-30 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [skills/claude-api/SKILL.md](skills/claude-api/SKILL.md)
- [skills/claude-api/shared/managed-agents-api-reference.md](skills/claude-api/shared/managed-agents-api-reference.md)
- [skills/skill-creator/SKILL.md](skills/skill-creator/SKILL.md)
- [skills/skill-creator/scripts/improve_description.py](skills/skill-creator/scripts/improve_description.py)
- [skills/skill-creator/scripts/run_loop.py](skills/skill-creator/scripts/run_loop.py)
- [spec/agent-skills-spec.md](spec/agent-skills-spec.md)

</details>



This glossary provides definitions for codebase-specific terms, technical jargon, abbreviations, and domain concepts used throughout the `anthropics/skills` repository. It is intended to help onboarding engineers navigate the intersection of natural language instructions and programmatic execution.

## Purpose and Scope

The scope of this page covers technical terminology, system architectures, API endpoints, optimization loops, and domain-specific metadata conventions present in the codebase. Every definition connects natural language space entities to their corresponding programmatic implementations and code pointers.

---

## Core Concepts

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Skill** | A self-contained folder containing instructions (`SKILL.md`), scripts, and resources that Claude loads to perform specialized tasks. | [README.md:4-4]() |
| **SKILL.md** | The mandatory entry point for a skill, containing YAML frontmatter for discovery and Markdown for instructions. | [skills/skill-creator/SKILL.md:76-79]() |
| **Frontmatter** | The YAML block at the top of a `SKILL.md` file. It must include `name` and `description`. | [README.md:84-87]() |
| **Plugin** | A logical grouping of skills defined in `marketplace.json`, allowing for bulk installation in environments like Claude Code. | [README.md:34-49]() |
| **Marketplace** | A JSON configuration file (`marketplace.json`) that catalogs available plugins and their constituent skills. | [.claude-plugin/marketplace.json:1-1]() |
| **Agent Skills Standard** | The interoperable specification for skill structure and discovery, documented at agentskills.io. | [README.md:1-1]() |
| **MCP** | Model Context Protocol. A standard for connecting AI models to external data sources and tools. | [skills/skill-creator/SKILL.md:60-61]() |
| **Academy Catalog** | A remotely fetched JSON catalog (`catalog.json`) containing Claude Academy courses, tutorials, and use cases used by the academy-guide skill. | [skills/academy-guide/SKILL.md:120-125]() |

### Skill Discovery and Execution Flow

The following diagram illustrates how a natural language query is mapped to a specific skill through the `available_skills` list and the progressive disclosure mechanism.

**Natural Language to Code Entity Mapping**
```mermaid
graph TD
    UserQuery["UserQuery"] --> ClaudeDecision["ClaudeDecisionEngine"]
    
    subgraph "Discovery Space"
        ClaudeDecision -- "Scans Descriptions" --> SkillList["available_skills List"]
        SkillList --> SkillMetadata["SKILL.md Frontmatter (name/description)"]
    end

    subgraph "Execution Space"
        SkillMetadata -- "Triggered" --> SkillBody["SKILL.md Body (Instructions)"]
        SkillBody -- "Optional" --> BundledResources["Bundled Resources (/scripts, /assets)"]
    end

    SkillMetadata -.-> [README.md:84-87]
    SkillBody -.-> [skills/skill-creator/SKILL.md:88-91]
    BundledResources -.-> [skills/skill-creator/SKILL.md:80-84]
```
Sources: [README.md:84-87](), [skills/skill-creator/SKILL.md:76-91]()

---

## Technical Features & Optimization

### Progressive Disclosure
A three-level loading system designed to minimize context window bloat:
1. **Metadata**: Name and description (~100 words) are always in context for triggering.
2. **Body**: The `SKILL.md` content is loaded only when the skill triggers.
3. **Resources**: Scripts and reference files are accessed only when explicitly needed by the model.
Sources: [skills/skill-creator/SKILL.md:86-91]()

### Triggering & "Should-Trigger"
*   **Triggering**: The process where Claude decides to invoke a skill based on its description.
*   **Should-trigger**: A boolean field in an `evals.json` test case indicating whether the skill *ought* to be activated for a given query.
*   **Adaptive Thinking**: A Claude feature (`thinking: {type: "adaptive"}`) that allows the model to perform internal reasoning before providing a response or calling a tool.
*   **Effort Ladder**: A specification of reasoning effort levels (`low`, `medium`, `high`, `xhigh`, `max`) configured on agent models.
*   **Prompt Caching**: The optimization of API requests by reusing identical prefix tokens to reduce latency and cost.
*   **Compaction**: The process of summarizing conversation history to maintain a stable, cacheable prefix.
Sources: [skills/skill-creator/SKILL.md:67-67](), [skills/claude-api/SKILL.md:30-35](), [skills/skill-creator/scripts/run_loop.py:25-29](), [skills/claude-api/shared/managed-agents-api-reference.md:47-47]()

---

## Managed Agents API

The Managed Agents system introduces several specific entities for persistent, containerized agent execution.

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Agent** | A persisted, versioned configuration (model, system prompt, tools, MCP servers, skills). | [skills/claude-api/shared/managed-agents-api-reference.md:58-60]() |
| **Session** | An active instance of an agent, provisioning a container as the agent's workspace. | [skills/claude-api/shared/managed-agents-api-reference.md:69-70]() |
| **Environment** | The infrastructure layer where tool execution occurs. Can be Anthropic-hosted or self-hosted. | [skills/claude-api/shared/managed-agents-api-reference.md:25-26]() |
| **Vault** | A secure store for credentials, particularly for MCP servers and OAuth tokens. | [skills/claude-api/shared/managed-agents-api-reference.md:33-34]() |
| **Memory Store** | A persistent storage system allowing agents to retain information across different sessions. | [skills/claude-api/shared/managed-agents-api-reference.md:35-36]() |
| **Coordinator** | A primary agent in a multi-agent session that can delegate tasks to other agents. | [skills/claude-api/shared/managed-agents-api-reference.md:23-23]() |
| **Roster** | The list of agents that a coordinator is authorized to delegate to via multiagent configurations. | [skills/claude-api/shared/managed-agents-api-reference.md:45-45]() |
| **Session Thread** | A context-isolated event stream for a subagent within a multi-agent session (`sessions.threads.*`). | [skills/claude-api/shared/managed-agents-api-reference.md:29-29]() |
| **Outcome** | A rubric-graded objective for a session, used for iterative execution loops. | [skills/claude-api/shared/managed-agents-api-reference.md:40-40]() |
| **Rubric** | Evaluation criteria used to score session outcomes. | [skills/claude-api/shared/managed-agents-api-reference.md:40-40]() |
| **Deployment Run** | An execution instance of a managed deployment (`deployment_runs.*`). | [skills/claude-api/shared/managed-agents-api-reference.md:32-32]() |
| **Self-Hosted Sandbox** | An infrastructure setup where customer-hosted workers poll for execution work (`environments.work.poller`). | [skills/claude-api/shared/managed-agents-api-reference.md:26-26]() |
| **agent_toolset_20260401** | The internal toolset identifier used by agents to perform base operations like file manipulation. | [skills/claude-api/shared/managed-agents-api-reference.md:10-10]() |
| **WIF** | Workload Identity Federation, used for secure cloud credential exchange in managed environments. | [skills/claude-api/shared/managed-agents-api-reference.md:33-34]() |

### Multi-Agent Interaction Model

**Managed Agents Entity Relationships**
```mermaid
graph TD
    subgraph "OrchestrationLayer"
        Coordinator["AgentsCreate (Coordinator)"]
        Roster["RosterConfig"]
        Session["SessionsCreate"]
    end

    subgraph "ExecutionLayer"
        Thread1["SessionsThreadsPrimary"]
        Thread2["SessionsThreadsSubagentA"]
        Thread3["SessionsThreadsSubagentB"]
        FS["SharedFilesystem"]
    end

    Coordinator --> Roster
    Session --> Thread1
    Thread1 -- "Delegates" --> Thread2
    Thread1 -- "Delegates" --> Thread3
    Thread1 --> FS
    Thread2 --> FS
    Thread3 --> FS

    Session -.-> [skills/claude-api/shared/managed-agents-api-reference.md:27-29]
    Roster -.-> [skills/claude-api/shared/managed-agents-api-reference.md:45-45]
```
Sources: [skills/claude-api/shared/managed-agents-api-reference.md:23-45]()

---

## Skill Creator & Evaluation Jargon

The `skill-creator` meta-skill uses specific terms for iterative improvement and evaluation:

*   **Tool Runner**: An SDK feature (e.g., `BetaToolRunner`) that automatically manages the agentic loop (calling tools, feeding results back to Claude).
*   **Eval Set**: A collection of test queries and expected outcomes (`evals.json`) used to benchmark skill performance.
*   **Grader Subagent**: A secondary LLM instance used to evaluate the quality of a primary agent's response against a rubric.
*   **Description Optimizer**: Automated scripts (`run_loop.py`, `improve_description.py`) that iteratively rewrite a skill's description to improve triggering accuracy based on eval results.
*   **Assertions**: Programmatic checks applied to eval outputs to determine pass/fail status.
*   **Blind Comparison**: Evaluating model outputs side-by-side without revealing which output came from the baseline vs. the skill-augmented run.
Sources: [skills/skill-creator/SKILL.md:14-18](), [skills/skill-creator/scripts/run_loop.py:24-44](), [skills/skill-creator/scripts/improve_description.py:50-60]()

### Description Optimization Loop

The following diagram maps the optimization scripts to the conceptual improvement loop.

**Optimization Loop Architecture**
```mermaid
graph LR
    subgraph "PythonScriptSpace"
        RL["RunLoopModule (run_loop.py)"]
        RE["RunEvalModule (run_eval.py)"]
        ID["ImproveDescriptionModule (improve_description.py)"]
    end

    RL -- "1. Executes" --> RE
    RE -- "2. Reports Failures" --> RL
    RL -- "3. Requests Revision" --> ID
    ID -- "4. Returns <new_description>" --> RL
    RL -- "5. Re-evaluates" --> RE

    RL -.-> [skills/skill-creator/scripts/run_loop.py:47-61]
    ID -.-> [skills/skill-creator/scripts/improve_description.py:50-60]
```
Sources: [skills/skill-creator/scripts/run_loop.py:47-61](), [skills/skill-creator/scripts/improve_description.py:50-60]()

---

## Domain-Specific Terms

### Document Skills
Production-grade skills for handling complex file formats under `skills/docx`, `skills/pdf`, `skills/pptx`, and `skills/xlsx`.
*   **DOCX Skill**: LibreOffice-backed Word document processing supporting tracked changes and comments.
*   **PDF Skill**: PDF structure extraction and form field parsing.
*   **PPTX Skill**: Slide manipulation and thumbnail generation.
*   **XLSX Skill**: Spreadsheet formula recalculation via LibreOffice integration.
Sources: [README.md:20-20]()