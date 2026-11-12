<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/skills · extra page Onboarding and Quickstart Templates · fetched 2026-10-30 -->

# Onboarding and Quickstart Templates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/claude-api/shared/managed-agents-onboarding-from-quickstart.md](skills/claude-api/shared/managed-agents-onboarding-from-quickstart.md)
- [skills/claude-api/shared/managed-agents-onboarding-from-url.md](skills/claude-api/shared/managed-agents-onboarding-from-url.md)
- [skills/claude-api/shared/managed-agents-onboarding.md](skills/claude-api/shared/managed-agents-onboarding.md)
- [skills/claude-api/shared/managed-agents-quickstarts/bug-hunter.md](skills/claude-api/shared/managed-agents-quickstarts/bug-hunter.md)
- [skills/claude-api/shared/managed-agents-quickstarts/contract-tracker.md](skills/claude-api/shared/managed-agents-quickstarts/contract-tracker.md)
- [skills/claude-api/shared/managed-agents-quickstarts/data-analyst.md](skills/claude-api/shared/managed-agents-quickstarts/data-analyst.md)
- [skills/claude-api/shared/managed-agents-quickstarts/deep-researcher.md](skills/claude-api/shared/managed-agents-quickstarts/deep-researcher.md)
- [skills/claude-api/shared/managed-agents-quickstarts/incident-commander.md](skills/claude-api/shared/managed-agents-quickstarts/incident-commander.md)
- [skills/claude-api/shared/managed-agents-quickstarts/support-agent.md](skills/claude-api/shared/managed-agents-quickstarts/support-agent.md)

</details>



This page documents the technical implementation and operational flows of the Managed Agents onboarding system and its bundled quickstart template library within the `anthropics/skills` repository. It covers the interactive onboarding interview, URL-based setup, pre-configured quickstart loading via the `ant` CLI, and the specific architecture of pre-built agent templates such as the Deep Researcher, Support Agent, Data Analyst, Incident Commander, Contract Tracker, and Bug Hunter.

---

## 1. Managed Agents Onboarding Flows

The managed-agents onboarding system is invoked via the `/claude-api managed-agents-onboard` skill subcommand [skills/claude-api/shared/managed-agents-onboarding.md:1-3](). Depending on how the subcommand is invoked (bare, with a URL, or with a quickstart name), the execution branches into three distinct flows: the interactive interview, the URL-ingestion flow, or the bundled quickstart template flow.

### 1.1 The Standard Interview Flow

When invoked without arguments (`/claude-api managed-agents-onboard`), the skill executes an interactive interview flow structured around a four-beat arc: **describe -> agent -> environment -> session** [skills/claude-api/shared/managed-agents-onboarding.md:5-7](). 
1. **Describe**: Collects high-level task parameters from the user via a single open-ended prompt [skills/claude-api/shared/managed-agents-onboarding.md:11-17]().
2. **Agent Configuration**: Automatically drafts an agent configuration proposal, determining necessary tools (`agent_toolset_20260401`), Model ID (`claude-opus-5-5` or `claude-fable-5-1`), MCP servers, and skill inclusions [skills/claude-api/shared/managed-agents-onboarding.md:19-32]().
3. **Environment Selection**: Configures sandboxed execution networking (`limited` vs `unrestricted`), package manager access (`allow_package_managers`), and MCP host allowlists [skills/claude-api/shared/managed-agents-onboarding.md:34-39]().
4. **Session & Credentials**: Binds user credentials at session setup (`sessions.create()`) and performs a live smoke-test [skills/claude-api/shared/managed-agents-onboarding.md:7]().

### 1.2 URL-Based Ingestion Flow

When invoked with a target URL (`/claude-api managed-agents-onboard https://...`), the system bypasses the interactive interview and delegates to the URL ingestion pipeline [skills/claude-api/shared/managed-agents-onboarding-from-url.md:1-5](). 
* **Pre-flight CLI Verification**: Before fetching any remote content, the workflow executes read-only validation commands to ensure proper client environment configuration:
  - Validates that `ant --version` is `1.34.0` or later [skills/claude-api/shared/managed-agents-onboarding-from-url.md:7-9]().
  - Checks `ant auth status` to confirm an active credential source and correct organization/workspace binding [skills/claude-api/shared/managed-agents-onboarding-from-url.md:10]().
* **Tier Enforcement**: Content parsing is governed by trust tiers (`First-party` vs. `Third-party`) [skills/claude-api/shared/managed-agents-onboarding-from-url.md:16-29](). First-party sources (Anthropic documentation domains and specified GitHub `main` branch references) permit direct copying of prompts, kickoff states, and tool structures, whereas third-party sources require design-only extraction where every word is authored locally [skills/claude-api/shared/managed-agents-onboarding-from-url.md:20-23]().

### 1.3 Quickstart-Based Ingestion Flow

When invoked with a quickstart template name (`/claude-api managed-agents-onboard <quickstart-name>`), the system loads the matching file stem from `skills/claude-api/shared/managed-agents-quickstarts/` [skills/claude-api/shared/managed-agents-onboarding-from-quickstart.md:1-3](). This flow extracts bundled configuration sections (`agent.md`, `environment.yaml`, `outcome.yaml`, `session.yaml`) and writes them directly into local project directories under `agents/<name>/` for deployment via `ant apply` [skills/claude-api/shared/managed-agents-onboarding-from-quickstart.md:5-41]().

```mermaid
title "Managed Agents Onboarding Invocation Architecture"
graph TD
    UserCommand["/claude-api managed-agents-onboard"] --> ArgCheck{"Argument Type?"}
    
    ArgCheck -->|None| StandardInterview["Interactive Interview Flow\nskills/claude-api/shared/managed-agents-onboarding.md"]
    ArgCheck -->|URL Provided| URLIngestion["URL Ingestion Flow\nskills/claude-api/shared/managed-agents-onboarding-from-url.md"]
    ArgCheck -->|Quickstart Name| QuickstartLoad["Quickstart Loading Flow\nskills/claude-api/shared/managed-agents-quickstarts/"]

    URLIngestion --> CLIPreflight["CLI Version & Auth Check\nant --version && ant auth status"]
    CLIPreflight --> TierEval{"Source Tier?"}
    TierEval -->|First-Party| DirectCopy["Copy Prompts & Configs"]
    TierEval -->|Third-Party| DesignOnly["Extract Architecture Only"]

    QuickstartLoad --> ExtractFiles["Parse Template Parts\nagent.md, environment.yaml, outcome.yaml"]
    
    StandardInterview --> AntApply["Deployment Execution\nant apply"]
    DirectCopy --> AntApply
    DesignOnly --> AntApply
    ExtractFiles --> AntApply
```
Sources: [skills/claude-api/shared/managed-agents-onboarding.md:1-8](), [skills/claude-api/shared/managed-agents-onboarding-from-url.md:1-12](), [skills/claude-api/shared/managed-agents-onboarding-from-quickstart.md:1-41]()

---

## 2. Quickstart Template Library

The repository includes a curated library of production-grade quickstart templates stored in `skills/claude-api/shared/managed-agents-quickstarts/`. Each quickstart file defines an agent's frontmatter configuration, system prompts, integration tools, and optional validation rubrics.

### 2.1 Deep Researcher

The deep researcher template configures an agent to execute multi-step web searches, decompose queries into authoritative sub-questions, and synthesize cited reports [skills/claude-api/shared/managed-agents-quickstarts/deep-researcher.md:1-36]().
* **Model Configuration**: Uses `claude-opus-5-5` with low effort tuning [skills/claude-api/shared/managed-agents-quickstarts/deep-researcher.md:18-20]().
* **Tooling**: Utilizes `agent_toolset_20260401` [skills/claude-api/shared/managed-agents-quickstarts/deep-researcher.md:21-22]().
* **Outcome Validation**: Bundles an `outcome.yaml` defining structured evaluation rubrics for source verification and confidence-gaps analysis [skills/claude-api/shared/managed-agents-quickstarts/deep-researcher.md:38-50]().

### 2.2 Support Agent

The support agent template connects Claude to customer support environments by integrating Notion knowledge bases and Slack communication channels [skills/claude-api/shared/managed-agents-quickstarts/support-agent.md:1-36]().
* **MCP Servers**: Configures URL-based MCP endpoints for Notion (`https://mcp.notion.com/mcp`) and Slack (`https://mcp.slack.com/mcp`) [skills/claude-api/shared/managed-agents-quickstarts/support-agent.md:21-27]().
* **Behavioral Rules**: Enforces strict policy quotation (no memory-based paraphrasing) and confidence thresholds ($\ge 80\%$) before direct customer replies [skills/claude-api/shared/managed-agents-quickstarts/support-agent.md:38-44]().

### 2.3 Data Analyst

The data analyst template provisions an environment for tabular data loading, cleansing, and visualization [skills/claude-api/shared/managed-agents-quickstarts/data-analyst.md:1-32]().
* **Tooling**: Combines standard file and execution tools with the Amplitude product analytics MCP server (`https://mcp.amplitude.com/mcp`) [skills/claude-api/shared/managed-agents-quickstarts/data-analyst.md:21-28]().
* **Execution Flow**: Mandates shape inspection, missing value handling, and output artifact generation under `/mnt/session/outputs/` [skills/claude-api/shared/managed-agents-quickstarts/data-analyst.md:33-41]().

### 2.4 Incident Commander

Designed for Sentry alert triage, the incident commander template orchestrates cross-service investigations [skills/claude-api/shared/managed-agents-quickstarts/incident-commander.md:1-44]().
* **MCP Integration**: Integrates Sentry (`https://mcp.sentry.dev/mcp`), Linear (`https://mcp.linear.app/mcp`), Slack (`https://mcp.slack.com/mcp`), and GitHub Copilot (`https://api.githubcopilot.com/mcp/`) [skills/claude-api/shared/managed-agents-quickstarts/incident-commander.md:19-41]().
* **Operational Cadence**: Pulls stack traces, opens tracking tickets, posts threaded status updates, and polls metrics every 15 minutes [skills/claude-api/shared/managed-agents-quickstarts/incident-commander.md:46-54]().

### 2.5 Contract Tracker

The contract tracker template automates contract lifecycle management by parsing Box documents and synchronizing obligations with Asana [skills/claude-api/shared/managed-agents-quickstarts/contract-tracker.md:1-34]().
* **MCP Servers**: Box (`https://mcp.box.com`) and Asana (`https://mcp.asana.com/sse`) [skills/claude-api/shared/managed-agents-quickstarts/contract-tracker.md:19-25]().
* **Task Automation**: Extracts parties, valuation, expiration dates, and critical milestones into categorized project tasks with verbatim clause references [skills/claude-api/shared/managed-agents-quickstarts/contract-tracker.md:36-43]().

### 2.6 Bug Hunter

The bug hunter template implements a specialized multi-agent workflow for parallel codebase inspection and proof-backed bug reporting [skills/claude-api/shared/managed-agents-quickstarts/bug-hunter.md:1-46]().
* **Multi-Agent Configuration**: Activates dynamic workflows via `multiagent: { type: multiagent_20261001, workflows: { type: enabled }, subagents: { type: disabled } }` [skills/claude-api/shared/managed-agents-quickstarts/bug-hunter.md:21-26]().
* **Execution Phases**: Distributes codebases across 4 to 20 parallel slices, executing a four-phase pipeline: reader analysis, second-round reviewer pass, candidate prioritization, and automated test-driven proof verification [skills/claude-api/shared/managed-agents-quickstarts/bug-hunter.md:52-64]().

```mermaid
title "Quickstart Template File Parsing and Application Data Flow"
graph TD
    TemplateFile["Quickstart File Stem\nskills/claude-api/shared/managed-agents-quickstarts/*.md"] --> FrontmatterParse["Parse Frontmatter\ntitle, description, console_key"]
    
    FrontmatterParse --> WriteAgentMD["Write agent.md\n(Config, Frontmatter, System Prompt)"]
    FrontmatterParse --> WriteEnvYaml["Write environment.yaml\n(Networking & Limits)"]
    FrontmatterParse --> WriteOutcomeYaml["Write outcome.yaml\n(Rubrics & Evaluation Criteria)"]
    FrontmatterParse --> WriteSessionYaml["Write session.yaml\n(Initial Message & Budget)"]

    WriteAgentMD --> TargetDir["Local Directory\nagents/<template-name>/"]
    WriteEnvYaml --> TargetDir
    WriteOutcomeYaml --> TargetDir
    WriteSessionYaml --> TargetDir

    TargetDir --> AntApplyExec["CLI Application Engine\nant apply"]
    AntApplyExec --> ManagedPlatform["Anthropic Managed Agents Platform"]
```
Sources: [skills/claude-api/shared/managed-agents-quickstarts/contract-tracker.md:1-34](), [skills/claude-api/shared/managed-agents-quickstarts/data-analyst.md:1-32](), [skills/claude-api/shared/managed-agents-quickstarts/deep-researcher.md:1-36](), [skills/claude-api/shared/managed-agents-quickstarts/incident-commander.md:1-44](), [skills/claude-api/shared/managed-agents-quickstarts/support-agent.md:1-36](), [skills/claude-api/shared/managed-agents-quickstarts/bug-hunter.md:1-46]()

---

## 3. Template Configuration Schema Reference

Each template file encapsulates standard configuration blocks recognized by the Managed Agents API and the `ant` CLI toolset. The structural components are mapped below:

| Template Part | Target Filename | API Equivalent / Resource Type | Technical Purpose |
|---|---|---|---|
| Frontmatter metadata | `agent.md` (YAML Header) | `AgentConfig` | Defines model versioning, effort levels, toolsets, and MCP endpoints [skills/claude-api/shared/managed-agents-quickstarts/contract-tracker.md:15-34]() |
| System Prompt | `agent.md` (Markdown Body) | `SystemPrompt` | Instructs agent behavior, operational rules, and step-by-step logic [skills/claude-api/shared/managed-agents-quickstarts/contract-tracker.md:36-43]() |
| Environment setup | `environment.yaml` | `EnvironmentConfig` | Provisions sandboxed containers, networking rules, and package manager allowances [skills/claude-api/shared/managed-agents-onboarding-from-quickstart.md:36]() |
| Evaluation Rubric | `outcome.yaml` | `user.define_outcome` | Establishes automated grading criteria and iterative success conditions [skills/claude-api/shared/managed-agents-onboarding-from-quickstart.md:39]() |
| Session Parameters | `session.yaml` | `SessionConfig` | Specifies initial user prompt text and token/compute budget limits [skills/claude-api/shared/managed-agents-onboarding-from-quickstart.md:38]() |

Sources: [skills/claude-api/shared/managed-agents-onboarding-from-quickstart.md:32-40](), [skills/claude-api/shared/managed-agents-quickstarts/contract-tracker.md:1-34]()

---

