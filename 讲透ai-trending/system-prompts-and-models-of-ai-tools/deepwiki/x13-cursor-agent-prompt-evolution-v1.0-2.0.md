<!-- source: DeepWiki mcp.deepwiki.com · repo x1xhlol/system-prompts-and-models-of-ai-tools · extra page Cursor Agent Prompt Evolution (v1.0 → 2.0) · fetched 2026-10-30 -->

# Cursor Agent Prompt Evolution (v1.0 → 2.0)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Cursor Prompts/Agent Prompt 2.0.txt](Cursor Prompts/Agent Prompt 2.0.txt)
- [Cursor Prompts/Agent Prompt 2025-09-03.txt](Cursor Prompts/Agent Prompt 2025-09-03.txt)
- [Cursor Prompts/Agent Prompt v1.0.txt](Cursor Prompts/Agent Prompt v1.0.txt)
- [Cursor Prompts/Agent Prompt v1.2.txt](Cursor Prompts/Agent Prompt v1.2.txt)
- [Cursor Prompts/Agent Tools v1.0.json](Cursor Prompts/Agent Tools v1.0.json)

</details>



This page traces the evolution of Cursor's agent prompt across several key versions: v1.0, v1.2, 2.0, and the 2025-09-03 revision. It highlights changes in the agent's tone, rules for tool calling, code citation format, and overall autonomy, providing a detailed understanding of how Cursor's AI assistant has been refined over time.

## Agent Prompt v1.0

The initial version of the Cursor Agent Prompt, `Agent Prompt v1.0.txt`, established the foundational identity and operational guidelines for the AI coding assistant. It positioned the agent as a "pair programming" partner, powered by Claude Sonnet 4 [Cursor Prompts/Agent Prompt v1.0.txt:1]().

### Tone and Identity

In v1.0, the agent's primary goal was to "follow the USER's instructions at each message, denoted by the `<user_query>` tag" [Cursor Prompts/Agent Prompt v1.0.txt:5](). The tone was collaborative, emphasizing a partnership with the user.

### Tool-Calling Rules

The `<tool_calling>` section laid out fundamental rules for tool usage [Cursor Prompts/Agent Prompt v1.0.txt:12-23]():
*   **Schema Adherence**: Always follow the tool call schema exactly [Cursor Prompts/Agent Prompt v1.0.txt:14]().
*   **Tool Availability**: Never call tools not explicitly provided [Cursor Prompts/Agent Prompt v1.0.txt:15]().
*   **User Communication**: Never refer to tool names when speaking to the USER; instead, describe the action in natural language [Cursor Prompts/Agent Prompt v1.0.txt:16]().
*   **Information Gathering**: Prefer using tools to gather information over asking the user [Cursor Prompts/Agent Prompt v1.0.txt:19]().
*   **Autonomy in Planning**: If a plan is made, immediately follow it without waiting for user confirmation, unless blocked or needing user input on options [Cursor Prompts/Agent Prompt v1.0.txt:20]().
*   **Standard Format**: Only use the standard tool call format [Cursor Prompts/Agent Prompt v1.0.txt:21]().

A significant emphasis was placed on parallel tool execution through the `<maximize_parallel_tool_calls>` section [Cursor Prompts/Agent Prompt v1.0.txt:25-39](). This section explicitly instructed the agent to "invoke all relevant tools simultaneously rather than sequentially" for maximum efficiency, stating that "parallel tool execution can be 3-5x faster than sequential calls" [Cursor Prompts/Agent Prompt v1.0.txt:26, 38]().

### Code Citation and Formatting

The `<communication>` section specified using backticks for file, directory, function, and class names in markdown [Cursor Prompts/Agent Prompt v1.0.txt:7-9]().

### Autonomy

V1.0 exhibited a strong bias towards agent autonomy, particularly in information gathering and plan execution. The agent was instructed to "Bias towards not asking the user for help if you can find the answer yourself" [Cursor Prompts/Agent Prompt v1.0.txt:47](). It also included specific instructions for making code changes, such as adding necessary imports and dependencies, and handling linter errors [Cursor Prompts/Agent Prompt v1.0.txt:50-62](). A notable rule was the preference for `search_replace` over `edit_file` for files larger than 2500 lines [Cursor Prompts/Agent Prompt v1.0.txt:60]().

Sources:
- [Cursor Prompts/Agent Prompt v1.0.txt:1-67]()

## Agent Prompt v1.2

Version 1.2, powered by GPT-4.1 [Cursor Prompts/Agent Prompt v1.2.txt:3](), built upon v1.0, retaining many core principles while introducing refinements, particularly in context understanding and tool usage.

### Tone and Identity

The identity remained consistent as an "AI coding assistant" and "pair programming" partner [Cursor Prompts/Agent Prompt v1.2.txt:3-5](). A new directive was added emphasizing the agent's role: "You are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved. Autonomously resolve the query to the best of your ability before coming back to the user" [Cursor Prompts/Agent Prompt v1.2.txt:7](). This reinforced the agent's autonomous nature.

### Tool-Calling Rules

The `<tool_calling>` rules were largely similar to v1.0, but with some key additions:
*   **Information Gathering**: Rule 7 was added, stating, "If you are not sure about file content or codebase structure pertaining to the user's request, use your tools to read files and gather the relevant information: do NOT guess or make up an answer" [Cursor Prompts/Agent Prompt v1.2.txt:23]().
*   **Extensive Reading**: Rule 8 further emphasized autonomy in reading: "You can autonomously read as many files as you need to clarify your own questions and completely resolve the user's query, not just one" [Cursor Prompts/Agent Prompt v1.2.txt:24]().
*   **GitHub PR/Issue Preference**: Rule 9 introduced a strong preference for reading GitHub pull requests and issues for understanding larger structural changes and recent updates, including specific markdown formatting for linking [Cursor Prompts/Agent Prompt v1.2.txt:25]().

The `<maximize_parallel_tool_calls>` section from v1.0 was replaced by `<maximize_context_understanding>` [Cursor Prompts/Agent Prompt v1.2.txt:29](). While still advocating for thorough information gathering, it shifted focus to semantic search as the "MAIN exploration tool" [Cursor Prompts/Agent Prompt v1.2.txt:34](). It provided detailed guidance on crafting broad, high-level queries, breaking down multi-part questions, and running multiple searches with different wording [Cursor Prompts/Agent Prompt v1.1.txt:35-38]().

### Code Citation and Formatting

The communication guidelines for markdown and backticks remained consistent [Cursor Prompts/Agent Prompt v1.2.txt:11-13]().

### Autonomy

V1.2 maintained a high degree of autonomy, particularly in information gathering. The explicit instruction to "Autonomously resolve the query to the best of your ability" [Cursor Prompts/Agent Prompt v1.2.txt:7]() and the detailed guidance on semantic search underscored this. The bias against asking the user for help if the answer could be found via tools was reiterated [Cursor Prompts/Agent Prompt v1.2.txt:41]().

Sources:
- [Cursor Prompts/Agent Prompt v1.2.txt:1-68]()

## Agent Prompt 2.0

Cursor Agent Prompt 2.0 represented a significant overhaul, moving towards a more structured and explicit definition of tools and operational flow. The prompt itself became more concise, with detailed tool descriptions embedded directly within the prompt.

### Tone and Identity

The core identity as an "AI coding assistant" and "pair programming" partner remained [Cursor Prompts/Agent Prompt 2.0.txt:3](). The emphasis on autonomous resolution of user queries was also retained [Cursor Prompts/Agent Prompt 2.0.txt:7]().

### Tool-Calling Rules

A major change in 2.0 was the integration of tool definitions directly into the prompt, using a `namespace functions` block [Cursor Prompts/Agent Prompt 2.0.txt:8-10](). Each tool, such as `codebase_search` and `run_terminal_cmd`, included extensive documentation on "When to Use This Tool," "When NOT to Use," "Examples," "Target Directories," and "Search Strategy" [Cursor Prompts/Agent Prompt 2.0.txt:12-113](). This provided much more explicit guidance on tool usage compared to previous versions.

The general `<tool_calling>` section was removed from the main prompt body, with tool-specific rules now part of their definitions. However, the prompt still implicitly enforced rules like not referring to tool names to the user and preferring tools over asking the user.

### Code Citation and Formatting

The communication guidelines were not explicitly detailed in the provided `Agent Prompt 2.0.txt` snippet, as the focus shifted to tool definitions. However, the examples within tool descriptions (e.g., for `codebase_search`) used clear markdown and code formatting, suggesting an implicit continuation of previous standards.

### Autonomy

Agent 2.0 continued to emphasize autonomy, particularly in its detailed guidance for `codebase_search`. The "Search Strategy" section for `codebase_search` explicitly instructed the agent to "Start with exploratory queries," "Review results; if a directory or file stands out, rerun with that as the target," and "Break large questions into smaller ones" [Cursor Prompts/Agent Prompt 2.0.txt:79-83](). This indicated a sophisticated, multi-step autonomous search process. The `run_terminal_cmd` tool also included detailed instructions for autonomous command execution, including handling shell state and non-interactive flags [Cursor Prompts/Agent Prompt 2.0.txt:118-123]().

Sources:
- [Cursor Prompts/Agent Prompt 2.0.txt:1-139]()

## Agent Prompt 2025-09-03 Revision

The 2025-09-03 revision introduced significant changes to communication, status updates, and task management, aiming for greater clarity, efficiency, and user experience.

### Tone and Identity

The core identity remained consistent [Cursor Prompts/Agent Prompt 2025-09-03.txt:1-7](). However, the `<communication>` section was heavily revised to optimize for clarity and skimmability, giving users the option to read more or less [Cursor Prompts/Agent Prompt 2025-09-03.txt:9](). It also introduced a more direct and action-oriented tone: "State assumptions and continue; don't stop for approval unless you're blocked" [Cursor Prompts/Agent Prompt 2025-09-03.txt:9]().

### Tool-Calling Rules

The `<tool_calling>` section was updated with new directives:
*   **Parallelization**: Explicitly stated "Parallelize tool calls per `<maximize_parallel_tool_calls>`: batch read-only context reads and independent edits instead of serial drip calls" [Cursor Prompts/Agent Prompt 2025-09-03.txt:60]().
*   **Sequencing**: "If actions are dependent or might conflict, sequence them; otherwise, run them in the same batch/turn" [Cursor Prompts/Agent Prompt 2025-09-03.txt:62]().
*   **Progress Notes**: Mandated "Give a brief progress note before the first tool call each turn; add another before any new batch and before ending your turn" [Cursor Prompts/Agent Prompt 2025-09-03.txt:66]().
*   **TODO List Integration**: Emphasized updating the TODO list via `todo_write` before reporting progress and before new edits [Cursor Prompts/Agent Prompt 2025-09-03.txt:67-69]().
*   **No `apply_patch`**: Explicitly stated, "There is no apply_patch CLI available in terminal. Use the appropriate tool for editing the code instead" [Cursor Prompts/Agent Prompt 2025-09-03.txt:68]().

### Code Citation and Formatting

The `<communication>` section provided more granular rules for markdown: "Always ensure **only relevant sections** (code snippets, tables, commands, or structured data) are formatted in valid Markdown with proper fencing. - Avoid wrapping the entire message in a single code block. Use Markdown **only where semantically correct** (e.g., `inline code`, ```code fences```, lists, tables)" [Cursor Prompts/Agent Prompt 2025-09-03.txt:9](). It also reiterated the use of backticks for code entities and specified "Refer to code changes as “edits” not "patches"" [Cursor Prompts/Agent Prompt 2025-09-03.txt:9]().

### Autonomy

This revision introduced a detailed `<status_update_spec>` [Cursor Prompts/Agent Prompt 2025-09-03.txt:10-39]() and `<summary_spec>` [Cursor Prompts/Agent Prompt 2025-09-03.txt:40-49]() to guide the agent's self-reporting and interaction with the user. The `<flow>` section [Cursor Prompts/Agent Prompt 2025-09-03.txt:56]() outlined a structured workflow for task execution, including discovery passes, plan creation via `todo_write`, status updates, and summaries. This indicates a more sophisticated, self-managing agent capable of narrating its progress and managing tasks autonomously. The instruction "Only pause if you truly cannot proceed without the user or a tool result. Avoid optional confirmations like 'let me know if that's okay' unless you're blocked" [Cursor Prompts/Agent Prompt 2025-09-03.txt:30]() further reinforced its autonomous operational model.

Sources:
- [Cursor Prompts/Agent Prompt 2025-09-03.txt:1-76]()

## Evolution Summary

The evolution of Cursor's agent prompt reflects a continuous effort to enhance the AI assistant's effectiveness, autonomy, and user experience.

### Diagram: Cursor Agent Prompt Evolution Overview

```mermaid
graph TD
    subgraph "Cursor Agent Prompt Evolution"
        A[v1.0: Claude Sonnet 4] --> B[v1.2: GPT-4.1]
        B --> C[v2.0: GPT-4.1 (Implicit)]
        C --> D[2025-09-03: GPT-5]
    end

    subgraph "Key Changes"
        A -- "Emphasis on Parallel Tool Calls" --> A_TC(Tool-Calling Rules)
        A -- "Basic Markdown Formatting" --> A_CF(Code Citation/Formatting)
        A -- "Bias towards Self-Resolution" --> A_A(Autonomy)

        B -- "Detailed Semantic Search Guidance" --> B_TC
        B -- "GitHub PR/Issue Preference" --> B_TC
        B -- "Explicit Autonomous Resolution" --> B_A

        C -- "Tools as In-Prompt Definitions" --> C_TC
        C -- "Extensive Tool Usage Examples" --> C_TC
        C -- "Structured Search Strategy" --> C_A

        D -- "Refined Communication Guidelines" --> D_CF
        D -- "Structured Status Updates (<status_update_spec>)" --> D_TC
        D -- "Mandatory TODO List Integration (todo_write)" --> D_TC
        D -- "Explicit Workflow (<flow>)" --> D_A
        D -- "No apply_patch CLI" --> D_TC
    end

    A_TC --> B_TC
    B_TC --> C_TC
    C_TC --> D_TC

    A_CF --> B_CF(Code Citation/Formatting)
    B_CF --> C_CF(Code Citation/Formatting)
    C_CF --> D_CF

    A_A --> B_A
    B_A --> C_A
    C_A --> D_A

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#ccf,stroke:#333,stroke-width:2px
    style D fill:#cfc,stroke:#333,stroke-width:2px
```
Sources:
- [Cursor Prompts/Agent Prompt v1.0.txt]()
- [Cursor Prompts/Agent Prompt v1.2.txt]()
- [Cursor Prompts/Agent Prompt 2.0.txt]()
- [Cursor Prompts/Agent Prompt 2025-09-03.txt]()

### Diagram: Natural Language Space to Code Entity Space Mapping

```mermaid
graph TD
    subgraph "Natural Language Space (Prompt Directives)"
        NL1["'Autonomously resolve the query'"] --> CE1["Agent Prompt v1.2:7"]
        NL2["'NEVER refer to tool names when speaking to the USER'"] --> CE2["Agent Prompt v1.0:16"]
        NL3["'ALWAYS use backticks to format file, directory, function, and class names'"] --> CE3["Agent Prompt v1.0:8"]
        NL4["'Semantic search is your MAIN exploration tool'"] --> CE4["Agent Prompt v1.2:34"]
        NL5["'If you make a plan, immediately follow it'"] --> CE5["Agent Prompt v1.0:20"]
        NL6["'Parallelize tool calls'"] --> CE6["Agent Prompt 2025-09-03.txt:60"]
        NL7["'Update the todo list via todo_write'"] --> CE7["Agent Prompt 2025-09-03.txt:67"]
        NL8["'Use codebase_search to search for code'"] --> CE8["Agent Prompt 2.0.txt:12-113"]
        NL9["'PROPOSE a command to run on behalf of the user'"] --> CE9["Agent Prompt 2.0.txt:115-131"]
        NL10["'Refer to code changes as “edits” not "patches"'"] --> CE10["Agent Prompt 2025-09-03.txt:9"]
    end

    subgraph "Code Entity Space (File Paths & Line Numbers)"
        CE1["Cursor Prompts/Agent Prompt v1.2.txt:7"]
        CE2["Cursor Prompts/Agent Prompt v1.0.txt:16"]
        CE3["Cursor Prompts/Agent Prompt v1.0.txt:8"]
        CE4["Cursor Prompts/Agent Prompt v1.2.txt:34"]
        CE5["Cursor Prompts/Agent Prompt v1.0.txt:20"]
        CE6["Cursor Prompts/Agent Prompt 2025-09-03.txt:60"]
        CE7["Cursor Prompts/Agent Prompt 2025-09-03.txt:67"]
        CE8["Cursor Prompts/Agent Prompt 2.0.txt:12-113"]
        CE9["Cursor Prompts/Agent Prompt 2.0.txt:115-131"]
        CE10["Cursor Prompts/Agent Prompt 2025-09-03.txt:9"]
    end
```
Sources:
- [Cursor Prompts/Agent Prompt v1.0.txt]()
- [Cursor Prompts/Agent Prompt v1.2.txt]()
- [Cursor Prompts/Agent Prompt 2.0.txt]()
- [Cursor Prompts/Agent Prompt 2025-09-03.txt]()

### Key Changes Across Versions

| Feature / Version | v1.0 (Claude Sonnet 4) | v1.2 (GPT-4.1) | 2.0 (GPT-4.1) | 2025-09-03 (GPT-5) |
| :---------------- | :--------------------- | :------------- | :------------ | :----------------- |
| **Tone** | Collaborative, pair programming | Emphasized autonomous resolution | Consistent, detailed tool guidance | Direct, action-oriented, optimized for clarity |
| **Tool-Calling Rules** | General rules, strong emphasis on parallel execution | Added rules for extensive reading, GitHub PR/issue preference | Tools defined *within* prompt with detailed usage, examples | Structured flow, mandatory TODO list updates, explicit parallelization |
| **Code Citation Format** | Backticks for code entities | Consistent with v1.0 | Implicitly consistent via tool examples | Granular markdown rules, "edits" not "patches" |
| **Autonomy** | High, bias against asking user, immediate plan execution | Reinforced autonomous resolution, detailed semantic search strategy | Sophisticated multi-step search, detailed terminal command execution | Self-managing with structured status updates, summaries, and explicit workflow |
| **Knowledge Cutoff** | Not specified in snippet | 2024-06 [Cursor Prompts/Agent Prompt v1.2.txt:1]() | 2024-06 [Cursor Prompts/Agent Prompt 2.0.txt:2]() | Not specified in snippet |
| **Model** | Claude Sonnet 4 [Cursor Prompts/Agent Prompt v1.0.txt:1]() | GPT-4.1 [Cursor Prompts/Agent Prompt v1.2.txt:3]() | GPT-4.1 (inferred from v1.2) | GPT-5 [Cursor Prompts/Agent Prompt 2025-09-03.txt:1]() |

Sources:
- [Cursor Prompts/Agent Prompt v1.0.txt]()
- [Cursor Prompts/Agent Prompt v1.2.txt]()
- [Cursor Prompts/Agent Prompt 2.0.txt]()
- [Cursor Prompts/Agent Prompt 2025-09-03.txt]()

---

