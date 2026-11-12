<!-- source: DeepWiki mcp.deepwiki.com · repo NousResearch/hermes-agent · page 8 Skills System · fetched 2026-10-30 -->

# Skills System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/skill_preprocessing.py](agent/skill_preprocessing.py)
- [apps/desktop/src/store/hub-actions.blocked.test.ts](apps/desktop/src/store/hub-actions.blocked.test.ts)
- [contributors/emails/dborodchuk@gmail.com](contributors/emails/dborodchuk@gmail.com)
- [hermes_cli/skills_hub.py](hermes_cli/skills_hub.py)
- [optional-skills/creative/impeccable/SKILL.md](optional-skills/creative/impeccable/SKILL.md)
- [optional-skills/software-development/grill-me/SKILL.md](optional-skills/software-development/grill-me/SKILL.md)
- [optional-skills/software-development/subagent-driven-development/SKILL.md](optional-skills/software-development/subagent-driven-development/SKILL.md)
- [scripts/build_skills_index.py](scripts/build_skills_index.py)
- [skills/autonomous-ai-agents/hermes-agent/SKILL.md](skills/autonomous-ai-agents/hermes-agent/SKILL.md)
- [skills/creative/songwriting-and-ai-music/SKILL.md](skills/creative/songwriting-and-ai-music/SKILL.md)
- [skills/software-development/simplify-code/SKILL.md](skills/software-development/simplify-code/SKILL.md)
- [tests/agent/test_skill_inline_shell_trust.py](tests/agent/test_skill_inline_shell_trust.py)
- [tests/hermes_cli/test_skills_failure_exit_code.py](tests/hermes_cli/test_skills_failure_exit_code.py)
- [tests/hermes_cli/test_skills_hub.py](tests/hermes_cli/test_skills_hub.py)
- [tests/hermes_cli/test_skills_provider_filter.py](tests/hermes_cli/test_skills_provider_filter.py)
- [tests/scripts/test_build_skills_index_health.py](tests/scripts/test_build_skills_index_health.py)
- [tests/scripts/test_build_skills_index_resolve.py](tests/scripts/test_build_skills_index_resolve.py)
- [tests/skills/test_authoring_standards.py](tests/skills/test_authoring_standards.py)
- [tests/tools/test_clawhub_owner_http.py](tests/tools/test_clawhub_owner_http.py)
- [tests/tools/test_clawhub_zip_stream.py](tests/tools/test_clawhub_zip_stream.py)
- [tests/tools/test_skill_bundle_provenance.py](tests/tools/test_skill_bundle_provenance.py)
- [tests/tools/test_skills_hub.py](tests/tools/test_skills_hub.py)
- [tests/tools/test_skills_hub_clawhub.py](tests/tools/test_skills_hub_clawhub.py)
- [tests/tools/test_skills_hub_github_fetch.py](tests/tools/test_skills_hub_github_fetch.py)
- [tests/website/__init__.py](tests/website/__init__.py)
- [tests/website/test_generate_skill_docs.py](tests/website/test_generate_skill_docs.py)
- [tools/skills_hub.py](tools/skills_hub.py)
- [tools/skills_hub_clawhub.py](tools/skills_hub_clawhub.py)
- [tools/skills_hub_github.py](tools/skills_hub_github.py)
- [tools/skills_hub_install.py](tools/skills_hub_install.py)
- [tools/skills_hub_models.py](tools/skills_hub_models.py)
- [tools/skills_hub_official.py](tools/skills_hub_official.py)
- [tools/skills_hub_search.py](tools/skills_hub_search.py)
- [tools/skills_hub_skillssh.py](tools/skills_hub_skillssh.py)
- [tools/skills_hub_sources.py](tools/skills_hub_sources.py)
- [website/docs/developer-guide/creating-skills.md](website/docs/developer-guide/creating-skills.md)
- [website/docs/reference/optional-skills-catalog.md](website/docs/reference/optional-skills-catalog.md)
- [website/docs/reference/skills-catalog.md](website/docs/reference/skills-catalog.md)
- [website/docs/user-guide/features/skills.md](website/docs/user-guide/features/skills.md)
- [website/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent.md](website/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent.md)
- [website/docs/user-guide/skills/bundled/creative/creative-p5js.md](website/docs/user-guide/skills/bundled/creative/creative-p5js.md)
- [website/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music.md](website/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music.md)
- [website/docs/user-guide/skills/bundled/productivity/productivity-notion.md](website/docs/user-guide/skills/bundled/productivity/productivity-notion.md)
- [website/docs/user-guide/skills/bundled/software-development/software-development-simplify-code.md](website/docs/user-guide/skills/bundled/software-development/software-development-simplify-code.md)
- [website/docs/user-guide/skills/optional/creative/creative-audiocraft-audio-generation.md](website/docs/user-guide/skills/optional/creative/creative-audiocraft-audio-generation.md)
- [website/docs/user-guide/skills/optional/creative/creative-heartmula.md](website/docs/user-guide/skills/optional/creative/creative-heartmula.md)
- [website/docs/user-guide/skills/optional/creative/creative-impeccable.md](website/docs/user-guide/skills/optional/creative/creative-impeccable.md)
- [website/docs/user-guide/skills/optional/mlops/mlops-evaluation-evaluating-llms-harness.md](website/docs/user-guide/skills/optional/mlops/mlops-evaluation-evaluating-llms-harness.md)
- [website/docs/user-guide/skills/optional/mlops/mlops-models-segment-anything-model.md](website/docs/user-guide/skills/optional/mlops/mlops-models-segment-anything-model.md)
- [website/docs/user-guide/skills/optional/mlops/mlops-tensorrt-llm.md](website/docs/user-guide/skills/optional/mlops/mlops-tensorrt-llm.md)
- [website/docs/user-guide/skills/optional/software-development/software-development-grill-me.md](website/docs/user-guide/skills/optional/software-development/software-development-grill-me.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/developer-guide/creating-skills.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/developer-guide/creating-skills.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/optional-skills-catalog.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/optional-skills-catalog.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/skills-catalog.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/skills-catalog.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/skills/optional/creative/creative-heartmula.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/skills/optional/creative/creative-heartmula.md)
- [website/scripts/generate-skill-docs.py](website/scripts/generate-skill-docs.py)
- [website/sidebars.ts](website/sidebars.ts)

</details>



This page introduces the Hermes skills system, which supplies on-demand procedural knowledge, reference documents, and tool extensions via agent-created and hub-downloaded packages [website/docs/user-guide/features/skills.md:3-9](). 

As a parent page, this section provides a high-level architectural overview. For comprehensive instructions on skill authoring, editing, security linting, background review, usage tracking (`tools/skill_usage.py`), audit ledgering (`tools/skill_ledger.py`), and syncing, see [Skills Management and Security](#8.1). For details on browsing external registries, taps, provenance tracking, and installation pipelines, see [Skills Hub](#8.2).

---

## Overview and Storage Architecture

A **skill** is a self-contained directory housing a `SKILL.md` file (containing YAML frontmatter and instructional markdown body) alongside optional `references/`, `templates/`, `assets/` or `scripts/` subdirectories [tools/skills_hub_models.py:20-21](). Skills reside locally in the user profile under `~/.hermes/skills/`, commonly referenced via the `SKILLS_DIR` constant defined in [tools/skills_hub.py:59](). This directory is seeded initially by copying the repository’s bundled skills found in the top-level `skills/` catalog [tools/skills_sync.py:2-6]().

Multi-profile or long-running Hermes Agent instances dynamically resolve the current `SKILLS_DIR` per active profile via indirection (`_skills_dir()`), ensuring proper isolation and scope [tools/skills_hub.py:59-81](). External skills directories can be added for delegation or extendability [website/docs/user-guide/features/skills.md:11-13]().

### Skills Directory Layout Example
```
~/.hermes/skills/
├── mlops/
│   ├── axolotl/
│   │   └── SKILL.md
│   └── ...
├── web/
│   ├── web-search/
│   │   └── SKILL.md
│   └── ...
├── SKILL.md
├── .usage.json
├── .curator_ledger.jsonl
└── references/
```

Sources: [tools/skills_hub_models.py:20-21](), [tools/skills_hub.py:59-81](), [website/docs/user-guide/features/skills.md:11-13](), [tools/skills_sync.py:2-6]()

---

## Progressive Disclosure and System Prompt Integration

To prevent excessive token usage in system prompts, Hermes uses **progressive disclosure** of skill information. At agent startup, only minimal metadata—skill names and truncated descriptions—are injected into the system prompt [agent/skill_preprocessing.py:1-5]().

When the agent requires detailed instructions or auxiliary skill files, it invokes tools such as `skills_list` to enumerate metadata or `skill_view` to retrieve full skill content and linked assets [tools/skills_tool_plugin.py:1-5](). This lookup supports progressive indexing rather than flooding the prompt with full skill texts.

The `agent/skill_preprocessing.py` module manages skill name slugification for commands (e.g., `"Foo Bar"` → `/foo-bar`), and extraction of user instructions from embedded skill scaffolding in prompts [agent/skill_preprocessing.py:1-5]().

### Diagram: Bridging Natural Language Skill Concepts to Code Entities
```mermaid
flowchart TD
  subgraph NaturalLanguage["Natural Language Space"]
    PromptInjected["Skill Index in System Prompt"]
    FullContent["Full Skill Instructions & File Assets"]
    SkillInvocation["User Command /skill-name and Instructions"]
  end

  subgraph CodeSpace["Code Entity Space"]
    SkillPreprocessing["agent/skill_preprocessing.py"]
    SkillUtils["agent/skill_utils.py"]
    SkillsToolPlugin["tools/skills_tool_plugin.py"]
    Filesystem["~/.hermes/skills/ directory"]
  end

  Filesystem -- "contains SKILL.md + support dirs" --> SkillUtils
  SkillUtils -- "extract metadata for index" --> SkillPreprocessing
  SkillPreprocessing -- "builds minimal skill index for prompt" --> PromptInjected
  PromptInjected -- "agent picks tool" --> SkillsToolPlugin
  SkillInvocation -- "slash command processed by" --> SkillPreprocessing
  SkillPreprocessing -- "calls & loads skill content" --> SkillsToolPlugin
  SkillsToolPlugin -- "loads full skill content from" --> Filesystem
  Filesystem -- "provides full skill body and assets" --> FullContent
```

Sources: [agent/skill_preprocessing.py:1-5](), [tools/skills_tool_plugin.py:1-5](), [tools/skills_hub_models.py:20-21]()

---

## Skills Management and Security (Child Page 8.1)

Skill creation, editing, patching, and file management are exposed to the agent through the `skill_manage` tool (`tools/skill_manager_tool.py`) [tools/skill_manager_tool.py:1-8](). This tool includes validation checks for skill names, categories, and frontmatter fields, enforcing constraints such as disallowing absolute paths and path traversal components in skill lookups [tools/skill_manager_tool.py:120-144]().

Static threat pattern scanning is performed on skill content and attached files via `tools/skills_guard.py` to prevent injection attacks, persistent backdoors, or exfiltration tactics [tools/skill_manager_tool.py:30-36](). Furthermore, `tools/skill_ledger.py` records every mutation (create, edit, patch, delete) into an append-only JSONL ledger (`.curator_ledger.jsonl`) with content-addressed blobs (`.curator_backups/blobs/`), supporting single-edit rollbacks [tools/skill_ledger.py:1-9]().

Detailed documentation covering skill creation workflows, security linting, manifest management, syncing, and background review by the `curator` (`agent/curator.py`) are available in the dedicated [Skills Management and Security](#8.1) child page.

Sources: [tools/skill_manager_tool.py:1-8, 30-36, 120-144](), [tools/skill_ledger.py:1-9](), [agent/curator.py:1-7]()

---

## Skills Hub (Child Page 8.2)

The Skills Hub subsystem enables browsing, installation, and management of external skill packages sourced from community and official registries. Installation requests flow through commands implemented in `hermes_cli/skills_hub.py` and are routed by source adapters that fetch skill bundles into quarantined directories for safety scanning [hermes_cli/skills_hub.py:2-5](), [tools/skills_hub.py:62]().

After security acceptance, skill bundles are written to the active `~/.hermes/skills/` directory or optionally to `optional-skills/`, a supplementary catalog shipped in the repository but not active by default. The `optional-skills/` catalog provides a playground for experimental or non-default skills that users can optionally install [website/docs/reference/optional-skills-catalog.md:9-9]().

The Skills Hub also handles tap management for third-party skill catalogs, provenance tracking for installed skills, and the automatic regeneration of skill catalog documentation.

### Diagram: Skills Hub Installation Flow and Security Integration
```mermaid
flowchart LR
  subgraph NaturalLanguage["Natural Language Space"]
    CLICommand["User Skill Install Request"]
    Quarantine["Temporary Quarantine Dir"]
  end

  subgraph CodeSpace["Code Entity Space"]
    HubCLI["hermes_cli/skills_hub.py"]
    SourceRouter["tools/skills_hub.py"]
    SkillsGuard["tools/skills_guard.py"]
    SkillsHubInstall["tools/skills_hub_install.py"]
    Filesystem["~/.hermes/skills/ or optional-skills/"]
  end

  CLICommand --> HubCLI
  HubCLI -- "dispatches install request" --> SourceRouter
  SourceRouter -- "downloads skill bundle" --> Quarantine
  Quarantine -- "scanned for threats by" --> SkillsGuard
  SkillsGuard -- "passes safe skill bundles to" --> SkillsHubInstall
  SkillsHubInstall -- "installs skills to" --> Filesystem
```

Sources: [website/docs/reference/optional-skills-catalog.md:9-9](), [hermes_cli/skills_hub.py:2-5](), [tools/skills_hub.py:62](), [tools/skills_guard.py:1-5]()

For comprehensive details on browsing catalogs, managing taps, tracking provenance, and the docs generation pipeline, see [Skills Hub](#8.2).

---

## Bundled and Optional Skills Catalogs

Hermes Agent ships with two primary skill catalogs:

1. **Bundled Skills (`skills/`)**: These skills are copied into `~/.hermes/skills/` upon initial installation and are synced during updates. They represent the core set of capabilities provided out-of-the-box [website/docs/reference/skills-catalog.md:9-9](). Users can opt out of bundled skills or reset them to their original state [website/docs/user-guide/features/skills.md:40-68]().
2. **Optional Skills (`optional-skills/`)**: These skills are shipped with the agent but are *not* active by default. They must be explicitly installed by the user via `hermes skills install official/<category>/<skill>` [website/docs/reference/optional-skills-catalog.md:9-13](). This catalog often contains experimental, specialized, or less commonly used skills.

Both catalogs are managed by the `skills_sync` module, which handles manifest-based seeding and updating, respecting user modifications and deletions [tools/skills_sync.py:2-6]().

Sources: [website/docs/reference/skills-catalog.md:9-9](), [website/docs/reference/optional-skills-catalog.md:9-13](), [website/docs/user-guide/features/skills.md:40-68](), [tools/skills_sync.py:2-6]()

---

This completes the high-level overview of the Hermes Skills System. For detailed documentation, please proceed to the child pages:

- [Skills Management and Security](#8.1)
- [Skills Hub](#8.2)

---

