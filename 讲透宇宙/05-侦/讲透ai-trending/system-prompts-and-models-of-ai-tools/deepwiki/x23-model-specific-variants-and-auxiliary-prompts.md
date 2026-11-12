<!-- source: DeepWiki mcp.deepwiki.com · repo x1xhlol/system-prompts-and-models-of-ai-tools · extra page Model-Specific Variants and Auxiliary Prompts · fetched 2026-10-30 -->

# Model-Specific Variants and Auxiliary Prompts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [VSCode Agent/chat-titles.txt](VSCode Agent/chat-titles.txt)
- [VSCode Agent/claude-sonnet-4.txt](VSCode Agent/claude-sonnet-4.txt)
- [VSCode Agent/gemini-2.5-pro.txt](VSCode Agent/gemini-2.5-pro.txt)
- [VSCode Agent/gpt-4.1.txt](VSCode Agent/gpt-4.1.txt)
- [VSCode Agent/gpt-4o.txt](VSCode Agent/gpt-4o.txt)
- [VSCode Agent/gpt-5-mini.txt](VSCode Agent/gpt-5-mini.txt)
- [VSCode Agent/gpt-5.txt](VSCode Agent/gpt-5.txt)
- [VSCode Agent/nes-tab-completion.txt](VSCode Agent/nes-tab-completion.txt)

</details>



This page details the various model-specific system prompts used by the VSCode Agent (GitHub Copilot) and auxiliary prompts that serve specialized functions within the VSCode environment. The model-specific prompts define the core behavior and interaction style for different underlying large language models (LLMs), while auxiliary prompts handle specific tasks like generating chat titles or providing tab completion suggestions.

## Model-Specific VSCode Agent Prompts

The VSCode Agent leverages different system prompts tailored to specific LLMs, including `gpt-4o`, `gpt-4.1`, `gpt-5`, `gpt-5-mini`, `claude-sonnet-4`, and `gemini-2.5-pro`. While all these prompts share a common goal of assisting developers in the VS Code editor, they exhibit variations in their instructions, communication style, and tool usage guidelines, reflecting the capabilities and nuances of their respective models.

All model-specific prompts begin with a foundational identity statement: "You are an expert AI programming assistant, working with a user in the VS Code editor." and "When asked for your name, you must respond with 'GitHub Copilot'." [VSCode Agent/gpt-4o.txt:1-2](). They also uniformly enforce Microsoft content policies and copyright avoidance [VSCode Agent/gpt-4o.txt:4-5](), and instruct the model to respond with "Sorry, I can't assist with that." for harmful content requests [VSCode Agent/gpt-4o.txt:6]().

### Common Instructions and Tool Usage

Across all models, the `<instructions>` block emphasizes the agent's role as a "highly sophisticated automated coding agent with expert-level knowledge" [VSCode Agent/gpt-4o.txt:9](). Key common directives include:
*   **Context Gathering**: Prioritize gathering context before acting, using tools to research and understand the user's request [VSCode Agent/gpt-4o.txt:10-11, VSCode Agent/gpt-4o.txt:18]().
*   **Task Breakdown**: For feature implementation without specified files, break down the request into smaller concepts [VSCode Agent/gpt-4o.txt:13]().
*   **Tool Utilization**: Encourage repeated and parallel tool calls to gather context and complete tasks, with a strong emphasis on not giving up easily [VSCode Agent/gpt-4o.txt:14, VSCode Agent/gpt-4o.txt:28]().
*   **File Reading Strategy**: Prefer reading "large meaningful chunks" over small, consecutive sections to minimize tool calls and gain better context [VSCode Agent/gpt-4o.txt:15, VSCode Agent/gpt-4o.txt:29]().
*   **Output Restrictions**: Strictly prohibit printing code blocks for file changes or terminal commands directly to the user; instead, use appropriate edit or terminal tools [VSCode Agent/gpt-4o.txt:19-20]().

The `<toolUseInstructions>` section further refines tool interaction, stressing adherence to JSON schema, avoiding tool names in user communication, and the preference for parallel tool execution (except for `semantic_search`) [VSCode Agent/gpt-4o.txt:25-30](). It also provides guidance on using `grep_search` for file overviews and `semantic_search` for broader workspace exploration [VSCode Agent/gpt-4o.txt:31-32]().

### Model-Specific Differences

While the core principles are shared, specific models introduce variations, particularly in their approach to file editing and communication style.

#### GPT-4o and Gemini-2.5-Pro

The `gpt-4o` and `gemini-2.5-pro` prompts share a similar `<editFileInstructions>` block. They both emphasize reading files before editing [VSCode Agent/gpt-4o.txt:39](), using `replace_string_in_file` as the primary editing tool [VSCode Agent/gpt-4o.txt:40](), and grouping changes by file [VSCode Agent/gpt-4o.txt:40](). They also introduce `insert_edit_into_file` as a smart tool that understands how to apply edits with minimal hints, encouraging the use of comments like `// ...existing code...` to represent unchanged regions [VSCode Agent/gpt-4o.txt:47-53](). Both prompts also include a 3-loop error fixing limit for file edits [VSCode Agent/gpt-4o.txt:46]().

Sources:
*   [VSCode Agent/gpt-4o.txt:1-74]()
*   [VSCode Agent/gemini-2.5-pro.txt:1-71]()

#### GPT-4.1

The `gpt-4.1` prompt introduces a distinct `<applyPatchInstructions>` section, favoring the `apply_patch` tool for file modifications [VSCode Agent/gpt-4.1.txt:40-41](). This tool uses a specific patch format with `*** Update File:`, `-[old_code]`, and `+[new_code]` markers, along with context lines and `@@` operators for unique identification of code snippets [VSCode Agent/gpt-4.1.txt:43-66](). The prompt explicitly states that `apply_patch` is "much faster and is the preferred tool" over `insert_edit_into_file` [VSCode Agent/gpt-4.1.txt:41]().

Sources:
*   [VSCode Agent/gpt-4.1.txt:1-69]()

#### GPT-5 and GPT-5-Mini

The `gpt-5` and `gpt-5-mini` prompts introduce more sophisticated agentic behaviors and communication guidelines. They emphasize:
*   **Agentic Persistence**: "You are an agent—keep going until the user's query is completely resolved before ending your turn." [VSCode Agent/gpt-5.txt:11]().
*   **Proactive Action**: "Take action when possible; the user expects you to do useful work without unnecessary questions." [VSCode Agent/gpt-5.txt:12]().
*   **Concise Updates**: "After any parallel, read-only context gathering, give a concise progress update and what's next." [VSCode Agent/gpt-5.txt:13]().
*   **Tool Batches and Cadence**: Require preambles for tool batches and suggest compact checkpoints after 3-5 tool calls or significant file edits [VSCode Agent/gpt-5.txt:15-16]().
*   **Requirements Coverage**: Mandate extracting requirements into a visible checklist and addressing them [VSCode Agent/gpt-5.txt:17, VSCode Agent/gpt-5.txt:26-27]().
*   **Communication Style**: Prescribe a "friendly, confident, and conversational tone," avoiding formality and empty filler [VSCode Agent/gpt-5.txt:18]().
*   **Engineering Mindset**: Encourage outlining "contracts," considering edge cases, and writing/updating tests first [VSCode Agent/gpt-5.txt:35-39]().
*   **Quality Gates**: Suggest a "quality gates" triage (Build, Lint/Typecheck, Unit tests, smoke test) before wrapping up [VSCode Agent/gpt-5.txt:42-44]().
*   **Response Mode Hints**: Guide the model to choose response modes based on task complexity, escalating from lightweight to full engineering workflow when needed [VSCode Agent/gpt-5.txt:46-48]().

The `gpt-5-mini` prompt is largely identical to `gpt-5` in these advanced agentic instructions, suggesting a shared behavioral paradigm for these models.

Sources:
*   [VSCode Agent/gpt-5.txt:1-49]()
*   [VSCode Agent/gpt-5-mini.txt:1-49]()

#### Claude-Sonnet-4

The `claude-sonnet-4` prompt shares many general instructions with the GPT models but lacks the specific `<editFileInstructions>` or `<applyPatchInstructions>` blocks found in the GPT variants. This implies that its file editing capabilities might be handled more generically through its tool-use instructions, or that it relies on a different underlying mechanism not explicitly detailed in this prompt. It also includes a `<reminderInstructions>` section that reinforces the agentic behavior of continuing until the query is resolved and taking action without unnecessary questions [VSCode Agent/claude-sonnet-4.txt:102-105]().

Sources:
*   [VSCode Agent/claude-sonnet-4.txt:1-106]()

### Model Prompt Comparison Diagram

```mermaid
graph TD
    subgraph "VSCode Agent Core Principles"
        A[Identity: "GitHub Copilot"]
        B[Follow Microsoft Policies]
        C[Avoid Copyrights]
        D[Handle Harmful Content]
        E[Keep Answers Short/Impersonal]
        F[Context Gathering First]
        G[Task Breakdown]
        H[Tool Utilization]
        I[Large Chunk File Reading]
        J[No Direct Code/Terminal Output]
    end

    subgraph "Model-Specific Instructions"
        GPT4O_GEMINI["gpt-4o / gemini-2.5-pro"]
        GPT41["gpt-4.1"]
        GPT5_GPT5MINI["gpt-5 / gpt-5-mini"]
        CLAUDE4["claude-sonnet-4"]
    end

    subgraph "File Editing Strategies"
        REPLACE_STRING["replace_string_in_file (primary)"]
        INSERT_EDIT["insert_edit_into_file (secondary, smart hints)"]
        APPLY_PATCH["apply_patch (preferred, specific format)"]
        GENERIC_EDIT["Generic Tool-Based Editing"]
    end

    subgraph "Agentic Behaviors & Communication"
        AGENTIC_PERSISTENCE["Agentic Persistence"]
        PROACTIVE_ACTION["Proactive Action"]
        CONCISE_UPDATES["Concise Progress Updates"]
        TOOL_BATCHES["Tool Batches & Cadence"]
        REQUIREMENTS_COVERAGE["Requirements Checklist"]
        COMM_STYLE["Conversational Tone"]
        ENGINEERING_MINDSET["Engineering Mindset (Contracts, Edge Cases, Tests)"]
        QUALITY_GATES["Quality Gates (Build, Lint, Tests)"]
        RESPONSE_MODE["Adaptive Response Mode"]
    end

    A --> GPT4O_GEMINI
    A --> GPT41
    A --> GPT5_GPT5MINI
    A --> CLAUDE4

    GPT4O_GEMINI --> REPLACE_STRING
    GPT4O_GEMINI --> INSERT_EDIT
    GPT4O_GEMINI --> "3-Loop Error Fix Limit"

    GPT41 --> APPLY_PATCH
    GPT41 --> INSERT_EDIT

    GPT5_GPT5MINI --> AGENTIC_PERSISTENCE
    GPT5_GPT5MINI --> PROACTIVE_ACTION
    GPT5_GPT5MINI --> CONCISE_UPDATES
    GPT5_GPT5MINI --> TOOL_BATCHES
    GPT5_GPT5MINI --> REQUIREMENTS_COVERAGE
    GPT5_GPT5MINI --> COMM_STYLE
    GPT5_GPT5MINI --> ENGINEERING_MINDSET
    GPT5_GPT5MINI --> QUALITY_GATES
    GPT5_GPT5MINI --> RESPONSE_MODE

    CLAUDE4 --> GENERIC_EDIT
    CLAUDE4 --> AGENTIC_PERSISTENCE
    CLAUDE4 --> PROACTIVE_ACTION
```
**Diagram: VSCode Agent Model-Specific Prompt Comparison**
Sources:
*   [VSCode Agent/gpt-4o.txt]()
*   [VSCode Agent/gpt-4.1.txt]()
*   [VSCode Agent/gpt-5.txt]()
*   [VSCode Agent/gpt-5-mini.txt]()
*   [VSCode Agent/claude-sonnet-4.txt]()
*   [VSCode Agent/gemini-2.5-pro.txt]()

## Auxiliary Prompts

In addition to the core model-specific prompts, the VSCode Agent utilizes specialized auxiliary prompts for distinct, focused tasks.

### Chat Titles (`chat-titles.txt`)

The `chat-titles.txt` prompt defines the behavior of an AI assistant whose sole purpose is to generate concise titles for chat conversations [VSCode Agent/chat-titles.txt:1]().
Key characteristics:
*   **Role**: "expert in crafting pithy titles for chatbot conversations" [VSCode Agent/chat-titles.txt:1]().
*   **Output Format**: Brief, impersonal, not wrapped in quotes, and "about 8 words or fewer" [VSCode Agent/chat-titles.txt:5-6]().
*   **Examples**: Provides examples like "Git rebase question" or "Installing Python packages" [VSCode Agent/chat-titles.txt:8-12]().
*   **Content Policies**: Adheres to Microsoft content policies and copyright avoidance [VSCode Agent/chat-titles.txt:2-3]().

Sources:
*   [VSCode Agent/chat-titles.txt:1-12]()

### NES Tab Completion (`nes-tab-completion.txt`)

The `nes-tab-completion.txt` prompt is designed for an AI assistant that helps developers complete code tasks by suggesting edits within `<|code_to_edit|>` tags [VSCode Agent/nes-tab-completion.txt:1](). This prompt is highly specialized for an interactive code completion scenario.
Key characteristics:
*   **Role**: "AI assistant is to help developers complete their code tasks by assisting in editing specific sections of code marked by the <|code_to_edit|> and <|/code_to_edit|> tags" [VSCode Agent/nes-tab-completion.txt:1]().
*   **Context Provided**: Access to `recently_viewed_code_snippets`, `current_file_content`, `edit_diff_history`, `area_around_code_to_edit`, and `cursor position` [VSCode Agent/nes-tab-completion.txt:5-9]().
*   **Task**: "predict and complete the changes the developer would have made next" [VSCode Agent/nes-tab-completion.txt:11]().
*   **Steps**: Outlines a clear process: Review Context, Evaluate Current Code, Suggest Edits, Maintain Consistency [VSCode Agent/nes-tab-completion.txt:15-18]().
*   **Output Format**: "Provide only the revised code within the tags," without including the tags themselves or line numbers [VSCode Agent/nes-tab-completion.txt:21-24]().
*   **Notes**: Includes specific instructions for apologizing for policy breaches and avoiding undoing developer changes unless there are obvious errors [VSCode Agent/nes-tab-completion.txt:31-33]().

Sources:
*   [VSCode Agent/nes-tab-completion.txt:1-34]()

### Auxiliary Prompt Workflow Diagram

```mermaid
graph TD
    A[User Interaction in VS Code] --> B{Is it a chat title request?}
    B -- Yes --> C["chat-titles.txt" Prompt]
    C --> D[Generate Pithy Title]
    D --> E[Display Title to User]

    B -- No --> F{Is it a tab completion request?}
    F -- Yes --> G["nes-tab-completion.txt" Prompt]
    G --> H[Gather Context: recently_viewed_code_snippets, current_file_content, edit_diff_history, area_around_code_to_edit, cursor position]
    H --> I[Predict & Complete Code within <|code_to_edit|> tags]
    I --> J[Display Suggested Completion to User]

    F -- No --> K[Default to Model-Specific VSCode Agent Prompt]
    K --> L[Execute Core Agent Task]
```
**Diagram: Auxiliary Prompt Workflow**
Sources:
*   [VSCode Agent/chat-titles.txt]()
*   [VSCode Agent/nes-tab-completion.txt]()

---

