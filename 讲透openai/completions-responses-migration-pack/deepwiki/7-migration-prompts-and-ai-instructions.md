<!-- source: DeepWiki mcp.deepwiki.com · repo openai/completions-responses-migration-pack · page 7 Migration Prompts and AI Instructions · fetched 2026-10-26 -->

# Migration Prompts and AI Instructions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [prompts/migrate-to-responses.md](prompts/migrate-to-responses.md)

</details>



This page documents the internal prompts and instructions that guide the Codex AI agent during automated code transformations. These prompts serve as the "brain" of the migration process, encoding migration logic, safety constraints, and transformation rules that the AI uses to convert legacy OpenAI API calls to the unified Responses API.

For information about the overall migration workflow, see [Getting Started](#2). For details about the script that orchestrates these prompts, see [Migration Script Reference](#5).

## Purpose and Architecture

The migration prompts system provides structured instructions that enable the Codex AI agent to perform intelligent code transformations across multiple programming languages. The system is designed around a single comprehensive prompt file that contains all the necessary context, rules, and constraints for safe automated migration.

### Prompt System Overview

```mermaid
graph TB
    subgraph "Migration Script"
        A[completions-to-responses-upgrade.sh]
    end
    
    subgraph "Prompt System"
        B["migrate-to-responses.md"]
        C["AGENTS.md"]
        D["responses-cheatsheet.md"]
        E["migration-notes.md"]
    end
    
    subgraph "Language Recipes"
        F["Node.js Recipe"]
        G["Python Recipe"]
        H["Java Recipe"]
        I["Other Languages"]
    end
    
    subgraph "Codex AI Agent"
        J["Code Analysis"]
        K["Pattern Recognition"]
        L["Transformation Engine"]
        M["Safety Validation"]
    end
    
    A --> B
    B --> J
    C --> K
    D --> L
    E --> L
    F --> L
    G --> L
    H --> L
    I --> L
    
    J --> K
    K --> L
    L --> M
    
    style B fill:#ff6b6b
    style J fill:#4ecdc4
    style L fill:#8ecae6
```

Sources: [prompts/migrate-to-responses.md:1-48]()

## Core Migration Instructions

The primary migration prompt is structured as a comprehensive automation brief that provides the Codex agent with clear objectives, constraints, and transformation rules.

### Instruction Structure

The migration prompt follows a structured format with distinct sections:

| Section | Purpose | Line Range |
|---------|---------|------------|
| Goals | Define migration objectives and success criteria | [3-11]() |
| Guardrails | Safety constraints and limitations | [13-19]() |
| Reference Pack | Documentation resources to consult | [21-23]() |
| Heuristics | Language-specific transformation rules | [25-33]() |
| Acceptance | Validation criteria for completed migration | [35-46]() |

### Goals and Objectives

The prompt defines five primary objectives for the AI agent:

```mermaid
graph LR
    A["Enumerate call sites"] --> B["Propose migration plan"]
    B --> C["Apply safe edits"]
    C --> D["Update callers"]
    D --> E["Run tests/lints"]
    
    A1["Legacy endpoints/SDKs"] --> A
    B1["Per-language sequencing"] --> B
    C1["Minimal changes"] --> C
    D1["New output schema"] --> D
    E1["Fix breakages"] --> E
```

Sources: [prompts/migrate-to-responses.md:5-11]()

## Transformation Heuristics

The prompt system encodes specific transformation rules for different programming environments and API patterns. These heuristics enable the AI agent to recognize legacy patterns and apply appropriate migrations.

### Language-Specific Transformations

```mermaid
graph TB
    subgraph "Node.js Patterns"
        A1["createCompletion"] --> B1["client.responses.create"]
        A2["OpenAIApi"] --> B2["OpenAI client"]
        A3["ChatCompletion"] --> B3["responses.create"]
    end
    
    subgraph "Python Patterns"
        A4["openai.Completion.create"] --> B4["client.responses.create"]
        A5["openai.ChatCompletion.create"] --> B5["client.responses.create"]
    end
    
    subgraph "Infrastructure Patterns"
        A6["POST /v1/completions"] --> B6["POST /v1/responses"]
        A7["prompt parameter"] --> B7["input parameter"]
        A8["max_tokens"] --> B8["max_output_tokens"]
    end
    
    subgraph "API Schema Transformations"
        A9["response_format"] --> B9["text.format"]
        A10["content.type: text"] --> B10["content.type: input_text"]
        A11["function calling"] --> B11["tools with JSON Schema"]
    end
```

Sources: [prompts/migrate-to-responses.md:26-32]()

### Parameter Mapping Rules

The prompt defines specific parameter transformations that the AI agent must apply:

| Legacy Parameter | New Parameter | Context |
|------------------|---------------|---------|
| `prompt` | `input` | Basic text input |
| `max_tokens` | `max_output_tokens` | Token limits |
| `response_format` | `text.format` | Output formatting |
| `content[].type: "text"` | `content[].type: "input_text"` | User/system messages |
| Function calling | `tools` with JSON Schema | Tool integration |

Sources: [prompts/migrate-to-responses.md:28-32]()

## Safety Guardrails and Constraints

The prompt system implements multiple layers of safety constraints to ensure secure and reliable automated transformations.

### Operational Constraints

```mermaid
graph TB
    subgraph "File System Constraints"
        A["Only modify git workspace files"]
        B["Never write outside workspace"]
        C["No backup files creation"]
        D["No tombstone comments"]
    end
    
    subgraph "Version Control Constraints"
        E["No git add/commit/push"]
        F["Working-tree edits only"]
        G["Leave version control to script"]
    end
    
    subgraph "Code Quality Constraints"
        H["No backward-compatibility shims"]
        I["Migrate to new API shape"]
        J["Preserve streaming semantics"]
        K["Run tests and lints"]
    end
    
    subgraph "Security Constraints"
        L["Ask approval for commands"]
        M["No network calls without approval"]
        N["Always set store: false"]
        O["Include encrypted reasoning tokens"]
    end
    
    A --> B
    C --> D
    E --> F
    F --> G
    H --> I
    I --> J
    J --> K
    L --> M
    N --> O
```

Sources: [prompts/migrate-to-responses.md:14-19](), [prompts/migrate-to-responses.md:43-44]()

### Model-Specific Configuration

The prompt includes logic for handling different AI models with appropriate reasoning effort settings:

| Model Pattern | Reasoning Effort | Condition |
|---------------|------------------|-----------|
| `/^o/` (o-series) | `medium` | Previous model was o1, o1-mini, etc. |
| `/^gpt-/` (GPT series) | `minimal` | Previous model was gpt-4, gpt-3.5, etc. |
| Explicit setting | User-provided | Respect existing `reasoning.effort` |

Sources: [prompts/migrate-to-responses.md:33]()

## Acceptance Criteria and Validation

The prompt defines comprehensive acceptance criteria that the AI agent must satisfy for a successful migration.

### Validation Requirements

```mermaid
graph TD
    A["All legacy calls replaced"] --> B["Imports/initialization updated"]
    B --> C["Builds/tests pass"]
    C --> D["Callers consume new outputs"]
    
    D --> E["Temperature handling"]
    E --> F["response_format to text.format"]
    F --> G["SDK version compatibility"]
    G --> H["Project builds cleanly"]
    
    H --> I["store: false set"]
    I --> J["Encrypted reasoning tokens"]
    J --> K["Summary with diffs"]
    
    subgraph "Final Deliverables"
        L["Edited files list"]
        M["Before/after call counts"]
        N["Next steps documentation"]
    end
    
    K --> L
    K --> M
    K --> N
```

Sources: [prompts/migrate-to-responses.md:36-45]()

### Build and Test Requirements

The prompt specifies that migrations must ensure:

- OpenAI SDK upgraded to version supporting Responses API
- Dependencies reinstalled (`npm install`, `pip install -U openai`)
- Project builds cleanly (`npm run build`, `pnpm build`, `yarn build`)
- All tests pass with new API integration
- Clear TODO notes for any remaining issues

Sources: [prompts/migrate-to-responses.md:41-42]()

## Integration with Migration Workflow

The prompt system integrates with the broader migration toolkit through several mechanisms:

### Reference Documentation Integration

The prompt instructs the AI agent to consult specific documentation files:

- `docs/responses-cheatsheet.md` - API parameter mappings and examples
- `docs/migration-notes.md` - Technical implementation details  
- `docs/language-recipes/*.md` - Language-specific idioms and patterns

Sources: [prompts/migrate-to-responses.md:22-23]()

### Execution Context

```mermaid
graph LR
    A["Migration Script"] --> B["Codex CLI"]
    B --> C["migrate-to-responses.md"]
    C --> D["AI Agent Processing"]
    
    D --> E["Code Analysis"]
    D --> F["Pattern Recognition"]  
    D --> G["Transformation Application"]
    D --> H["Validation"]
    
    H --> I["Working Tree Changes"]
    I --> J["Test Execution"]
    J --> K["Summary Report"]
```

Sources: [prompts/migrate-to-responses.md:1-48]()

The prompt system serves as the knowledge base and instruction set that enables intelligent, safe, and comprehensive migration from legacy OpenAI APIs to the unified Responses API across multiple programming languages and environments.

---

