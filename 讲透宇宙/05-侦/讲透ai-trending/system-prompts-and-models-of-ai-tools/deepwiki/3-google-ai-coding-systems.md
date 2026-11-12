<!-- source: DeepWiki mcp.deepwiki.com · repo x1xhlol/system-prompts-and-models-of-ai-tools · page 3 Google AI Coding Systems · fetched 2026-10-30 -->

# Google AI Coding Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Google/Antigravity/Fast Prompt.txt](Google/Antigravity/Fast Prompt.txt)
- [Google/Antigravity/planning-mode.txt](Google/Antigravity/planning-mode.txt)
- [Google/Gemini/AI Studio vibe-coder.txt](Google/Gemini/AI Studio vibe-coder.txt)

</details>



This section introduces Google's AI coding systems present in this repository: Antigravity and the Gemini AI Studio vibe-coder / Gemini CLI. Antigravity is a powerful agentic AI coding assistant with a fast prompt and a planning mode, designed for comprehensive development tasks. The Gemini AI Studio vibe-coder focuses on generating complete React web applications with a strong emphasis on UI/UX design, while the Gemini CLI provides a command-line interface for AI assistance.

For detailed information on each system, please refer to their respective child pages.

## Antigravity: Agentic AI Coding Assistant

Antigravity is a sophisticated agentic AI coding assistant developed by the Google Deepmind team. It is designed to pair program with a user, handling tasks ranging from creating new codebases to debugging existing ones or answering coding questions [Google/Antigravity/Fast Prompt.txt:1-5](). Antigravity operates within a Windows PowerShell environment and features a comprehensive tool ecosystem, strict workspace access controls, and a unique workflow system with "turbo" annotations for automation. It places a significant emphasis on web application development standards and design aesthetics, aiming to "wow" the user with premium designs [Google/Antigravity/Fast Prompt.txt:32-73]().

For a deep dive into Antigravity's architecture, tool ecosystem, and Windows PowerShell environment, see [System Architecture and Agent Identity](#3.1).

Sources: [Google/Antigravity/Fast Prompt.txt:1-5, 32-73]()

## Antigravity's Knowledge and Context Management

Antigravity employs a dual-context system for managing information: Knowledge Items (KIs) for curated, distilled knowledge, and Conversation Logs for raw historical data. This allows for efficient retrieval of relevant information and persistent context across sessions. The system also includes a dedicated KNOWLEDGE SUBAGENT responsible for processing conversation logs into KIs.

For a detailed explanation of the KI system, including `metadata.json`, `artifacts/`, and the KI Summary mechanism, see [Knowledge Items (KI) Architecture](#3.2). To understand the `brain/` directory structure, UUID-organized conversation logs, and artifacts for persistent context, refer to [Conversation Logs and Persistent Context](#3.3).

Sources: [Google/Antigravity/Fast Prompt.txt:99-215, 216-301]()

## Antigravity's Workflow and Automation

Antigravity incorporates a robust workflow system, defined by `.agent/workflows/` markdown files with YAML frontmatter. This system allows for structured task execution and includes "turbo" annotations (`// turbo` and `// turbo-all`) that enable `SafeToAutoRun` automation for `run_command` tool calls [Google/Antigravity/Fast Prompt.txt:78-95](). This feature streamlines repetitive tasks and enhances the agent's efficiency.

For an in-depth look at the `.agent/workflows/` system and the functionality of `// turbo` and `// turbo-all` annotations, see [Workflow System and Turbo Annotations](#3.4).

Sources: [Google/Antigravity/Fast Prompt.txt:78-95]()

## Antigravity's Web Application Development and Design Philosophy

Antigravity adheres to a strict five-phase approach for web application development: Plan, Foundation, Components, Pages, and Polish [Google/Antigravity/Fast Prompt.txt:44-64](). It prioritizes vanilla technologies (HTML, Javascript, Vanilla CSS) unless explicitly requested otherwise, and mandates a "WOW-factor" aesthetic with rich designs, modern typography, and dynamic elements [Google/Antigravity/Fast Prompt.txt:20-40](). SEO best practices are automatically implemented on every page [Google/Antigravity/Fast Prompt.txt:65-72]().

For a comprehensive understanding of Antigravity's web application development standards, its five-phase approach, and the emphasis on design aesthetics and SEO, refer to [Web Application Development Standards and Design Aesthetics](#3.5).

Sources: [Google/Antigravity/Fast Prompt.txt:20-40, 44-64, 65-72]()

## Antigravity's Planning Mode

Antigravity features a dedicated planning mode where it researches the codebase, understands requirements, and designs its approach. In this mode, it always creates an `implementation_plan.md` to document proposed changes and seeks user approval. If the user requests changes, Antigravity remains in planning mode, updates the plan, and requests review again until approved [Google/Antigravity/planning-mode.txt:22](). This structured approach ensures alignment with user expectations before execution begins.

For a detailed explanation of how Antigravity's planning mode operates, including how plans are produced, structured, and handed off for implementation, see [Antigravity Planning Mode](#3.6).

Sources: [Google/Antigravity/planning-mode.txt:22]()

## Antigravity's Workspace Access Control and Security

Antigravity enforces stringent workspace access control through URI-to-CorpusName mappings. It is strictly forbidden from accessing files outside active workspaces and has specific guidelines for using the `C:\Users\Lucas\.gemini` directory, which is reserved for system instructions only and not for project code [Google/Antigravity/Fast Prompt.txt:12-13](). All file path arguments to tools must be absolute [Google/Antigravity/Fast Prompt.txt:17-18]().

For a thorough understanding of Antigravity's workspace access control, security measures, and the usage guidelines for the `.gemini` directory, refer to [Workspace Access Control and Security](#3.7).

Sources: [Google/Antigravity/Fast Prompt.txt:12-13, 17-18]()

## Gemini AI Studio Vibe-Coder and Gemini CLI

Beyond Antigravity, Google also offers the Gemini AI Studio vibe-coder and the Gemini CLI. The vibe-coder acts as a world-class senior frontend React engineer, generating complete and functional React web application code using TypeScript and Tailwind CSS, with a focus on excellent visual aesthetics [Google/Gemini/AI Studio vibe-coder.txt:4-5](). It adheres to a strict XML output format for code changes and specific React/TypeScript guidance [Google/Gemini/AI Studio vibe-coder.txt:18-33, 63-118](). The Gemini CLI, on the other hand, provides a command-line interface for interacting with Gemini models, offering a different modality for AI-assisted coding.

For detailed documentation on Google's AI Studio vibe-coder prompt, the Gemini CLI system prompt, their respective roles, tool conventions, and how they differ from Antigravity, see [Gemini AI Studio Vibe-Coder and Gemini CLI](#3.8).

Sources: [Google/Gemini/AI Studio vibe-coder.txt:4-5, 18-33, 63-118]()

---

