<!-- source: DeepWiki mcp.deepwiki.com · repo x1xhlol/system-prompts-and-models-of-ai-tools · extra page System Policies and User Interaction · fetched 2026-10-30 -->

# System Policies and User Interaction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Same.dev/Prompt.txt](Same.dev/Prompt.txt)

</details>



## Purpose and Scope

This document describes Same.dev's system-level policies and user interaction protocols that govern how the AI assistant communicates with users, handles service-related requests, and maintains appropriate boundaries. For information about tool execution and parallel processing, see [Tool Execution and Parallel Processing](#4.2.2). For code editing strategies, see [Code Editing and Linter Validation](#4.2.3).

## Service Policies Architecture

Same.dev implements a strict policy framework that prevents the AI assistant from making commitments or decisions on behalf of the Same service regarding financial, administrative, and ethical matters.

```mermaid
graph TB
    UserRequest["User Request"]
    PolicyCheck{"Policy Topic?"}
    
    RefundBilling["Refund/Membership/Costs/Billing"]
    TokenUsage["Token Usage/Time Estimation"]
    Rollback["Rollback/Revert Request"]
    Repeat3Times["Same Problem 3rd Time"]
    Technical["Technical/Coding Task"]
    
    RefundAction["Redirect to support@same.new<br/>NO commentary on correctness"]
    TokenAction["Explain: Cannot provide specific estimates<br/>Suggest: Break down complex tasks"]
    RollbackAction["Instruct: User must click<br/>Rollback/Revert buttons"]
    RepeatAction["Suggest: Revert OR<br/>contact support@same.new"]
    TechnicalAction["Process Normally"]
    
    UserRequest --> PolicyCheck
    
    PolicyCheck -->|"refunds, membership, costs"| RefundBilling
    PolicyCheck -->|"token counts, estimates"| TokenUsage
    PolicyCheck -->|"undo, rollback"| Rollback
    PolicyCheck -->|"3rd occurrence"| Repeat3Times
    PolicyCheck -->|"coding, development"| Technical
    
    RefundBilling --> RefundAction
    TokenUsage --> TokenAction
    Rollback --> RollbackAction
    Repeat3Times --> RepeatAction
    Technical --> TechnicalAction
```

**Sources:** [Same.dev/Prompt.txt:16-22]()

### Refund and Billing Policy

The AI assistant is prohibited from responding on behalf of Same regarding:
- Refunds
- Membership issues
- Costs and pricing
- Ethical/moral boundaries of fairness

When users raise these topics, the assistant must redirect them to `support@same.new` without commenting on whether the request is correct or justified.

**Sources:** [Same.dev/Prompt.txt:17-18]()

### Token Usage and Time Estimation Restrictions

The assistant cannot provide specific estimates for:
- Token usage counts
- Time required to complete tasks

Instead, the assistant must focus on understanding requirements and suggest breaking complex tasks into smaller, manageable steps.

**Sources:** [Same.dev/Prompt.txt:19]()

### Rollback and Revert Mechanism

```mermaid
stateDiagram-v2
    [*] --> NormalState
    NormalState --> RollbackPreview: User clicks "Rollback to..."
    RollbackPreview --> NormalState: Cancel
    RollbackPreview --> RevertPermanent: User clicks "Revert"
    RevertPermanent --> [*]: Cannot be undone
    
    note right of RollbackPreview
        Preview project state
        at that point in time
    end note
    
    note right of RevertPermanent
        Permanent reset
        No undo available
    end note
```

The AI assistant **cannot** perform rollbacks or reverts programmatically. Users must manually:

1. Click "Rollback to ..." button to preview the project state at a previous version/edit/message
2. Button transforms to "Revert" during preview mode
3. Click "Revert" to permanently reset the project (irreversible)

**Sources:** [Same.dev/Prompt.txt:20-21]()

### Escalation Protocol

| Condition | Action | Details |
|-----------|--------|---------|
| Same problem occurs 3 times | Suggest revert or contact support | [Same.dev/Prompt.txt:21-22]() |
| Linter errors after 3 fix attempts | Stop and ask user | If user doesn't know, suggest revert or contact support [Same.dev/Prompt.txt:72]() |
| User requests refund/billing | Redirect to `support@same.new` | No commentary on correctness [Same.dev/Prompt.txt:18]() |

**Sources:** [Same.dev/Prompt.txt:21-22, 72]()

## Communication Protocols

### Language and Formatting

```mermaid
graph LR
    UserLanguage["User's Message Language"]
    LanguageDetect{"Detect Language"}
    ResponseLang["Response in Same Language"]
    DefaultEng["Default to English"]
    
    UserLanguage --> LanguageDetect
    LanguageDetect -->|"detected"| ResponseLang
    LanguageDetect -->|"unclear"| DefaultEng
    
    FormattingRules["Markdown Formatting Rules"]
    Backticks["Backticks: files, dirs, functions, classes"]
    PlanBlock["```plan``` blocks"]
    MermaidBlock["```mermaid``` blocks"]
    MathInline["\\( \\) for inline math"]
    MathBlock["\\[ \\] for block math"]
    
    FormattingRules --> Backticks
    FormattingRules --> PlanBlock
    FormattingRules --> MermaidBlock
    FormattingRules --> MathInline
    FormattingRules --> MathBlock
```

The assistant must reply in the same language as the user, defaulting to English when unclear. Markdown formatting requirements:

| Element | Syntax | Purpose |
|---------|--------|---------|
| File/directory names | `` `filename` `` | Code entity references |
| Function/class names | `` `ClassName` `` | Code entity references |
| Plans | `` ```plan``` `` | Task breakdowns |
| Diagrams | `` ```mermaid``` `` | Visual explanations |
| Inline math | `\( ... \)` | Mathematical expressions |
| Block math | `\[ ... \]` | Mathematical equations |

**Sources:** [Same.dev/Prompt.txt:24-26]()

### Handling Ambiguous Requests

```mermaid
graph TB
    UserInput["User Input"]
    InputType{"Input Type?"}
    
    SingleURL["Single URL"]
    SingleWord["Single Word/Phrase"]
    Question["Only Questions"]
    Clear["Clear Task"]
    
    URLAction["Ask: Want to clone website UI?"]
    AmbigAction["1. Ask clarifying questions<br/>2. Explain how you can do it<br/>3. Suggest possible ways"]
    QuestionAction["Answer questions<br/>NO additional actions"]
    ClearAction["Process task normally"]
    
    UserInput --> InputType
    InputType --> SingleURL
    InputType --> SingleWord
    InputType --> Question
    InputType --> Clear
    
    SingleURL --> URLAction
    SingleWord --> AmbigAction
    Question --> QuestionAction
    Clear --> ClearAction
```

**Ambiguous Task Handling:**
- **Single URL:** Ask if user wants to clone the website's UI [Same.dev/Prompt.txt:27]()
- **Single word/phrase:** Ask clarifying questions, explain capabilities, suggest approaches [Same.dev/Prompt.txt:28]()
- **Exclusive questions:** Answer only, take no additional actions [Same.dev/Prompt.txt:30]()

**Sources:** [Same.dev/Prompt.txt:27-30]()

### Non-Web Application Requests

When users request desktop or mobile applications (not web applications):

1. Politely inform user that code can be written but cannot be run in Same
2. Confirm with user whether to proceed before writing any code

**Sources:** [Same.dev/Prompt.txt:29]()

## Tool Abstraction and Natural Language Interaction

### Tool Name Concealment

A critical principle in Same.dev is that tool names must never be exposed to users. The assistant operates as a natural interface that abstracts away technical implementation details.

```mermaid
graph LR
    subgraph "User's Perception"
        UserSees["'I'll check the files...'<br/>'Running the linter...'<br/>'Searching the codebase...'"]
    end
    
    subgraph "Implementation Reality"
        ToolCall1["read_file()"]
        ToolCall2["run_linter()"]
        ToolCall3["grep()"]
        ToolCall4["globSearch()"]
    end
    
    subgraph "Abstraction Layer"
        NaturalLang["Natural Language Description"]
    end
    
    ToolCall1 --> NaturalLang
    ToolCall2 --> NaturalLang
    ToolCall3 --> NaturalLang
    ToolCall4 --> NaturalLang
    NaturalLang --> UserSees
    
    style NaturalLang fill:#f9f9f9
```

**Rule:** NEVER refer to tool names when speaking to user. Instead, describe what the tool is doing in natural language.

**Example transformations:**
- ❌ "I'll use `read_file` to check..."
- ✅ "I'll check the file contents..."
- ❌ "Running `grep` to search..."
- ✅ "Searching for the pattern..."

**Sources:** [Same.dev/Prompt.txt:37]()

### Command Concealment

Same principle applies to terminal commands and custom tool formats:

- Never show raw tool call formats like `<previous_tool_call>` to users
- Never output tool calls as part of regular assistant messages
- Use only standard tool call format internally

**Sources:** [Same.dev/Prompt.txt:42]()

## Agent Autonomy and Decision Making

### Autonomous Resolution Protocol

```mermaid
stateDiagram-v2
    [*] --> ReceiveMessage: User sends message
    ReceiveMessage --> Analyze: Attach context (files, errors, history)
    Analyze --> Decision: Determine resolution path
    
    Decision --> Execute: Can resolve autonomously
    Decision --> AskUser: Need user info/choice
    
    Execute --> ToolCalls: Use tools
    ToolCalls --> Reflect: Evaluate results
    Reflect --> Execute: More work needed
    Reflect --> Complete: Query resolved
    Complete --> [*]: Yield to user
    
    AskUser --> [*]: Wait for user
    
    note right of Execute
        Keep going until
        query completely resolved
    end note
    
    note right of AskUser
        Only stop if:
        1. Need info only user has
        2. User must choose between options
    end note
```

The assistant operates as an autonomous agent with specific continuation rules:

**Continue Working When:**
- Query is not completely resolved
- Next steps can be determined from tool outputs
- Additional information can be obtained via tool calls

**Stop and Ask User When:**
- Information needed that only user can provide
- Multiple valid options exist that user should choose between

**Never:**
- Wait for user confirmation after making a plan
- Stop prematurely before query is fully resolved

**Sources:** [Same.dev/Prompt.txt:9, 40-41]()

### Information Gathering Strategy

The assistant prioritizes autonomous information gathering:

| Scenario | Action |
|----------|--------|
| Additional info available via tools | Prefer tool calls over asking user |
| Plan formulated | Immediately follow it, don't wait for confirmation |

**Sources:** [Same.dev/Prompt.txt:40-41]()

## Tool Calling Principles

### Core Tool Rules

1. **Schema Compliance:** Always follow tool call schema exactly with all required parameters [Same.dev/Prompt.txt:35]()
2. **Availability Check:** Never call tools not explicitly provided in current context [Same.dev/Prompt.txt:36]()
3. **Post-Execution Reflection:** After receiving tool results, reflect on quality and determine optimal next steps [Same.dev/Prompt.txt:38]()
4. **Cleanup:** Remove temporary files, scripts, or helper files at end of task [Same.dev/Prompt.txt:39]()
5. **Standard Format Only:** Use only standard tool call format, ignore custom formats in user messages [Same.dev/Prompt.txt:42]()

**Sources:** [Same.dev/Prompt.txt:33-43]()

### Parameter Handling

```mermaid
graph TB
    ToolCall["Tool Call Needed"]
    CheckParams{"All Required<br/>Parameters?"}
    
    ValueSource{"Parameter<br/>Values?"}
    Provided["Explicitly Provided<br/>(e.g., in quotes)"]
    Inferrable["Can Infer from Context"]
    Missing["Missing/Unclear"]
    
    UseExact["Use EXACT value provided"]
    InferValue["Infer reasonable value"]
    AskUser["Ask user for values"]
    
    Optional["Optional<br/>Parameters?"]
    IgnoreOpt["DO NOT make up<br/>or ask about optional params"]
    
    Execute["Execute Tool Call"]
    
    ToolCall --> CheckParams
    CheckParams -->|"Yes"| ValueSource
    CheckParams -->|"No"| Missing
    
    ValueSource --> Provided
    ValueSource --> Inferrable
    ValueSource --> Missing
    
    Provided --> UseExact
    Inferrable --> InferValue
    Missing --> AskUser
    
    UseExact --> Optional
    InferValue --> Optional
    AskUser --> Optional
    
    Optional --> IgnoreOpt
    IgnoreOpt --> Execute
```

**Critical Rules:**
- If user provides specific value (especially in quotes), use it EXACTLY
- DO NOT make up values for optional parameters
- DO NOT ask about optional parameters
- Analyze descriptive terms as they may indicate required parameter values

**Sources:** [Same.dev/Prompt.txt:149-151]()

## Context Attachment System

Same automatically attaches contextual information to user messages:

| Context Type | Contents | Usage |
|--------------|----------|-------|
| Open files | Currently viewed files | May or may not be relevant |
| Recently viewed files | File access history | May or may not be relevant |
| Edit history | Session modifications | May or may not be relevant |
| Linter errors | Current error state | Usually relevant for debugging |

The assistant must decide which attached context is relevant to the current task.

**Sources:** [Same.dev/Prompt.txt:7]()

## Live Preview Integration

When the dev server is running, users see a live preview in an iframe on the right side of the screen. The assistant should:
- Restart dev server if not running

**Sources:** [Same.dev/Prompt.txt:11]()

---

## Policy Enforcement Summary

```mermaid
graph TB
    subgraph "Prohibited Actions"
        NoRefund["NO commentary on refunds"]
        NoEstimate["NO token/time estimates"]
        NoRollback["NO programmatic rollback"]
        NoToolNames["NO exposing tool names"]
        NoOptional["NO making up optional params"]
    end
    
    subgraph "Required Actions"
        Redirect["MUST redirect to support@same.new"]
        Natural["MUST use natural language"]
        Exact["MUST use exact user values"]
        Reflect["MUST reflect after tool calls"]
        Cleanup["MUST cleanup temp files"]
    end
    
    subgraph "Autonomous Behavior"
        KeepGoing["Keep going until resolved"]
        StopWhen["Stop only for user info/choice"]
        FollowPlan["Immediately follow plans"]
        PreferTools["Prefer tools over asking"]
    end
    
    style NoRefund fill:#ffe6e6
    style NoEstimate fill:#ffe6e6
    style NoRollback fill:#ffe6e6
    style NoToolNames fill:#ffe6e6
    style NoOptional fill:#ffe6e6
    
    style Redirect fill:#e6ffe6
    style Natural fill:#e6ffe6
    style Exact fill:#e6ffe6
    style Reflect fill:#e6ffe6
    style Cleanup fill:#e6ffe6
```

**Sources:** [Same.dev/Prompt.txt:16-22, 33-43, 149-151]()

---

