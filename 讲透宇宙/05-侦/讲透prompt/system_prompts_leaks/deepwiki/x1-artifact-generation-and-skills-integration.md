<!-- source: DeepWiki mcp.deepwiki.com · repo asgeirtj/system_prompts_leaks · extra page Artifact Generation and Skills Integration · fetched 2026-11-09 -->

# Artifact Generation and Skills Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [OpenAI/gpt-5.5-instant.md](OpenAI/gpt-5.5-instant.md)
- [OpenAI/gpt-5.5-thinking.md](OpenAI/gpt-5.5-thinking.md)

</details>



This document describes GPT-5.5 Thinking's artifact generation capabilities and Skills integration system. GPT-5.5 generates two primary artifact types: writing blocks for discrete content presentation (emails, chat messages, social posts) and specialized documents (spreadsheets, slides, PDFs, docx) via the `artifact_tool` and specialized skills. The Skills system provides best practices and workflows through `SKILL.md` files located at `/home/oai/skills/*/SKILL.md`.

For information about the channel-based architecture that determines where these tools can be used, see page 3.1.1. For memory and personalization systems, see page 3.1.3.

**Sources:** [OpenAI/gpt-5.5-thinking.md:7-12](), [OpenAI/gpt-5.5-thinking.md:29-51](), [OpenAI/gpt-5.5-thinking.md:198-200]()

## Skills System Architecture

GPT-5.5 Thinking includes a Skills system that provides specialized instructions for artifact generation tasks. Skills are stored as `SKILL.md` files in the `/home/oai/skills/` directory, organized by document type.

### Skills System Organization

**Skills Directory Structure**

```mermaid
graph TB
    ["/home/oai/skills/"] --> ["/home/oai/skills/pdfs/SKILL.md"]
    ["/home/oai/skills/"] --> ["/home/oai/skills/docx/SKILL.md"]
    ["/home/oai/skills/"] --> ["/home/oai/skills/slides/SKILL.md"]
    ["/home/oai/skills/"] --> ["/home/oai/skills/spreadsheets/SKILL.md"]
    
    subgraph "Associated_Tools_and_Libraries"
        ["reportlab"]
        ["python-docx"]
        ["/home/oai/share/slides/"]
        ["artifact_tool"]
        ["openpyxl"]
    end
    
    ["/home/oai/skills/pdfs/SKILL.md"] -.-> ["reportlab"]
    ["/home/oai/skills/docx/SKILL.md"] -.-> ["python-docx"]
    ["/home/oai/skills/slides/SKILL.md"] -.-> ["/home/oai/share/slides/"]
    ["/home/oai/skills/spreadsheets/SKILL.md"] -.-> ["artifact_tool"]
    ["/home/oai/skills/spreadsheets/SKILL.md"] -.-> ["openpyxl"]
```

**Sources:** [OpenAI/gpt-5.5-thinking.md:9-12]()

### Skills Invocation Requirements

| Artifact Type | Skill File Path | Purpose | Tool/Library |
|---------------|----------------|---------|--------------|
| PDF | `/home/oai/skills/pdfs/SKILL.md` | Instructions for PDF-related tasks | `reportlab` |
| Documents | `/home/oai/skills/docx/SKILL.md` | Instructions for docx document tasks | `python-docx` |
| Slides | `/home/oai/skills/slides/SKILL.md` | Instructions for slides-related tasks | `/home/oai/share/slides/` helpers |
| Spreadsheets | `/home/oai/skills/spreadsheets/SKILL.md` | Style guidelines and logic | `artifact_tool`, `openpyxl` |

The system prompt mandates: "You *must* read [skill file path] for instructions" before performing artifact-related tasks [OpenAI/gpt-5.5-thinking.md:9-12](). This ensures adherence to best practices and style guidelines defined in each `SKILL.md` file.

**Sources:** [OpenAI/gpt-5.5-thinking.md:9-12]()

### Skills vs LibreOffice Rules

GPT-5.5 has specific constraints about tool selection for spreadsheets:

```mermaid
graph LR
    ["User_Request"] --> ["Check_Explicit_Override"]
    ["Check_Explicit_Override"] -- "No (default)" --> ["Use_artifact_tool"]
    ["Check_Explicit_Override"] -- "Yes" --> ["Use_LibreOffice_or_Doc_Skill"]
    
    subgraph "Default_Workflow"
        ["Use_artifact_tool"] --> ["Read_/home/oai/skills/spreadsheets/SKILL.md"]
    end
```

**Rule:** "DO NOT use the docs or PDF skill or LibreOffice for spreadsheets, unless user explicitly asks" [OpenAI/gpt-5.5-thinking.md:12]().

**Sources:** [OpenAI/gpt-5.5-thinking.md:12]()

## General Artifact Guidelines

The system prompt defines a strict logic for when to use artifacts. These instructions apply **ONLY** if a user has asked to create or modify artifacts like docs, spreadsheets, and slides [OpenAI/gpt-5.5-thinking.md:16]().

### Artifact Creation Workflow

```mermaid
graph TB
    ["User_Request"] --> ["Evaluate_Artifact_Need"]
    ["Evaluate_Artifact_Need"] -- "Spreadsheet/Doc/Slide" --> ["Read_Specific_SKILL.md"]
    ["Read_Specific_SKILL.md"] --> ["Execute_Artifact_Tool_Logic"]
    
    ["Execute_Artifact_Tool_Logic"] --> ["Generate_Sandbox_Link"]
    ["Generate_Sandbox_Link"] --> ["Final_Response_with_Citation"]
```

**Sources:** [OpenAI/gpt-5.5-thinking.md:16-20]()

### Sandbox Citations for Artifacts

Generated artifacts are linked using sandbox citation syntax [OpenAI/gpt-5.5-thinking.md:20]():

```markdown
[Any descriptive label](sandbox:/mnt/data/<filename>.<ext>)
```

**Constraints:**
- Never share font files in the container with the user, especially if explicitly asked [OpenAI/gpt-5.5-thinking.md:21]().
- Maintain honesty about failures or uncertainties in artifact generation [OpenAI/gpt-5.5-thinking.md:25]().

**Sources:** [OpenAI/gpt-5.5-thinking.md:20-25]()

## Writing Blocks for Content Presentation

A **writing block** fences text into a distinct section that’s easy to view, copy, and modify [OpenAI/gpt-5.5-thinking.md:31](). GPT-5.5 supports multiple variants for communication-heavy tasks.

### Writing Block Usage Scenarios

Writing blocks are only considered for the following scenarios [OpenAI/gpt-5.5-thinking.md:33-49]():
- **email**
- **chat_message** (SMS, Slack, etc.)
- **social_post**

### Writing Block Syntax Structure

Writing blocks use a specific fenced syntax with metadata fields [OpenAI/gpt-5.5-thinking.md:35-41]().

**Syntax Example:**
```text
:::writing{variant="email" id="12345" subject="Meeting Notes"}
<content>
:::
```

| Component | Rule | Details |
|-----------|------|---------|
| Opening fence | Must start with `:::writing{` | Exactly this string [OpenAI/gpt-5.5-thinking.md:37]() |
| Metadata format | key="value" pairs | Within the curly braces [OpenAI/gpt-5.5-thinking.md:37]() |
| Closing fence | Exactly `:::` | Three colons on own line [OpenAI/gpt-5.5-thinking.md:41]() |

**Sources:** [OpenAI/gpt-5.5-thinking.md:35-41]()

### Writing Block Metadata Fields

**Metadata fields [OpenAI/gpt-5.5-thinking.md:49]():**

| Field | Type | Requirement | Details |
|-------|------|-------------|---------|
| `variant` | string enum | Required | "email", "chat_message", "social_post", "standard" (fallback) |
| `id` | 5-digit string | Required | Must be unique and random |
| `subject` | string | Conditional | Required if `variant="email"`; forbidden otherwise |
| `recipient` | string | Optional | Allowed only if `variant="email"` AND provided by user |

**Sources:** [OpenAI/gpt-5.5-thinking.md:49]()

### Writing Block Constraints
- **Context Requirement:** Never give a bare writing block; include framing context [OpenAI/gpt-5.5-thinking.md:43]().
- **Volume Limit:** Never include more than 3 writing blocks in one response [OpenAI/gpt-5.5-thinking.md:45]().
- **Formatting:** No other text on the same line as the opening or closing fence [OpenAI/gpt-5.5-thinking.md:47]().
- **No References:** Content references are prohibited inside writing blocks [OpenAI/gpt-5.5-thinking.md:51]().

**Sources:** [OpenAI/gpt-5.5-thinking.md:43-51]()

## Artifact Tool and Skill Handoff

The `artifact_tool` (integrated with `openpyxl`) manages the creation of complex file types. For spreadsheets, it specifically uses the `openpyxl` library and follows instructions in `/home/oai/skills/spreadsheets/SKILL.md` [OpenAI/gpt-5.5-thinking.md:12]().

### Implementation Mapping

```mermaid
graph LR
    subgraph "Natural_Language_Space"
        ["User_Prompt: 'Create_a_budget_sheet'"]
        ["User_Prompt: 'Find_my_budget_file'"]
        ["User_Prompt: 'Generate_an_image'"]
    end

    subgraph "Code_Entity_Space"
        ["artifact_tool"]
        ["openpyxl"]
        ["/home/oai/skills/spreadsheets/SKILL.md"]
        ["file_search"]
        ["image_gen"]
    end

    ["User_Prompt: 'Create_a_budget_sheet'"] --> ["artifact_tool"]
    ["artifact_tool"] -- "uses" --> ["openpyxl"]
    ["artifact_tool"] -- "adheres_to" --> ["/home/oai/skills/spreadsheets/SKILL.md"]
    ["User_Prompt: 'Find_my_budget_file'"] --> ["file_search"]
    ["User_Prompt: 'Generate_an_image'"] --> ["image_gen"]
```

**Key principle:** GPT-5.5 must prioritize `artifact_tool` over general Python execution or LibreOffice for spreadsheet generation to ensure adherence to platform-specific style guidelines [OpenAI/gpt-5.5-thinking.md:12](). For retrieving existing artifacts, the `file_search` tool is the mandatory "Source of Truth" [OpenAI/gpt-5.5-instant.md:49-55]().

**Sources:** [OpenAI/gpt-5.5-thinking.md:12](), [OpenAI/gpt-5.5-instant.md:49-55](), [OpenAI/gpt-5.5-thinking.md:52-54]()

---

