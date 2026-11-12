<!-- source: DeepWiki mcp.deepwiki.com · repo jujumilk3/leaked-system-prompts · extra page Cluely Meeting Co-pilot · fetched 2026-11-09 -->

# Cluely Meeting Co-pilot

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cluely-20250611.md](cluely-20250611.md)
- [google-gemini-cli_20250626.md](google-gemini-cli_20250626.md)

</details>



## Purpose and Scope

This document describes the Cluely Meeting Co-pilot system, a specialized AI assistant designed for live meeting assistance extracted from an Electron framework application. Cluely implements a hierarchical decision tree architecture to provide context-aware support during meetings by processing both audio transcripts and screen content. The system operates in two distinct modes: a live-meeting mode with prioritized transcript analysis and a screen-only mode with specialized content handlers.

For general autonomous agent architectures, see [Agent Loop Architecture](#5.1). For comparison with other specialized assistants, see [Platform-Specific Assistants](#4.3).

## System Architecture Overview

Cluely implements a rule-based conversational pattern rather than an iterative agent loop. The system processes inputs through a strict decision hierarchy that determines response type based on context availability and content characteristics.

### Dual-Mode Architecture

```mermaid
graph TB
    subgraph Input["Input Processing Layer"]
        AudioTranscript["Audio Transcript<br/>(meeting dialogue)"]
        ScreenContent["Screen Content<br/>(visual context)"]
        UserContext["User Context<br/>${s6} variable"]
    end
    
    subgraph ModeSelection["Mode Selection"]
        LiveMeeting["Live Meeting Mode<br/>Prioritize transcript"]
        ScreenOnly["Screen-Only Mode<br/>Problem solver"]
    end
    
    subgraph LiveDecisionHierarchy["Live Meeting Decision Hierarchy"]
        Level1["1. RECENT_QUESTION_DETECTED"]
        Level2["2. PROPER_NOUN_DEFINITION"]
        Level3["3. SCREEN_PROBLEM_SOLVER"]
        Level4["4. FALLBACK_MODE"]
    end
    
    subgraph ScreenHandlers["Screen-Only Content Handlers"]
        TechHandler["technical_problems"]
        MathHandler["math_problems"]
        MCQHandler["multiple_choice_questions"]
        EmailHandler["emails_messages"]
        UIHandler["ui_navigation"]
        UnclearHandler["unclear_or_empty_screen"]
    end
    
    subgraph Output["Output Formatting"]
        ResponseFormat["Structured Response<br/>Headline + Bullets"]
        MandatoryFormat["Content-Specific<br/>Mandatory Formats"]
    end
    
    AudioTranscript --> LiveMeeting
    ScreenContent --> ModeSelection
    UserContext --> ModeSelection
    
    LiveMeeting --> Level1
    Level1 -->|"No question"| Level2
    Level2 -->|"No proper noun"| Level3
    Level3 -->|"No screen problem"| Level4
    
    ScreenOnly --> ScreenHandlers
    
    Level1 --> Output
    Level2 --> Output
    Level3 --> Output
    Level4 --> Output
    ScreenHandlers --> MandatoryFormat
    
    MandatoryFormat --> Output
```

**Diagram: Cluely Dual-Mode Architecture**

The system routes inputs through one of two processing pipelines depending on context availability. Live Meeting Mode prioritizes transcript analysis through a 4-level hierarchy, while Screen-Only Mode dispatches to specialized content handlers based on problem type.

Sources: [cluely-20250611.md:6-74](), [cluely-20250611.md:75-166]()

## Four-Level Decision Hierarchy

The live meeting mode implements a strict sequential decision tree where each level is evaluated in order and the first applicable action is executed.

### Decision Hierarchy State Machine

```mermaid
stateDiagram-v2
    [*] --> EvaluateLevel1
    
    EvaluateLevel1: Level 1: RECENT_QUESTION_DETECTED
    EvaluateLevel2: Level 2: PROPER_NOUN_DEFINITION
    EvaluateLevel3: Level 3: SCREEN_PROBLEM_SOLVER
    EvaluateLevel4: Level 4: FALLBACK_MODE
    
    EvaluateLevel1 --> AnswerQuestion: Question detected in transcript
    EvaluateLevel1 --> EvaluateLevel2: No question
    
    EvaluateLevel2 --> DefineProperNoun: Proper noun at transcript end
    EvaluateLevel2 --> EvaluateLevel3: No proper noun
    
    EvaluateLevel3 --> CheckScreenConditions: Check conditions
    
    state CheckScreenConditions {
        [*] --> VerifyNoQuestion
        VerifyNoQuestion --> VerifyNoTerm: No answerable question
        VerifyNoTerm --> VerifyProblem: No new term
        VerifyProblem --> SolveProblem: Clear full problem visible
        VerifyProblem --> NextLevel: Conditions not met
    }
    
    CheckScreenConditions --> SolveProblem: All conditions met
    CheckScreenConditions --> EvaluateLevel4: Conditions not met
    
    EvaluateLevel4 --> ExecuteFallback
    
    AnswerQuestion --> [*]: Infer intent from brief/garbled text
    DefineProperNoun --> [*]: Based on general knowledge
    SolveProblem --> [*]: Treat as transcript prompt
    ExecuteFallback --> [*]: "Not sure what you need help with"
```

**Diagram: Four-Level Decision Hierarchy State Machine**

Each level represents a distinct intent detection pattern with decreasing specificity. The hierarchy ensures questions are always prioritized over definitions, definitions over screen problems, and explicit fallback messaging when no clear intent is detected.

Sources: [cluely-20250611.md:8-18](), [cluely-20250611.md:43-52](), [cluely-20250611.md:65-70]()

### Decision Level Specifications

| Level | Identifier | Trigger Condition | Action | Priority |
|-------|-----------|-------------------|--------|----------|
| 1 | `RECENT_QUESTION_DETECTED` | Recent question in transcript, even if lines after | Answer directly, infer intent from brief/unclear text | Highest |
| 2 | `PROPER_NOUN_DEFINITION` | No question, proper noun near transcript end | Define/explain based on general knowledge | High |
| 3 | `SCREEN_PROBLEM_SOLVER` | No question/term AND clear problem on screen | Solve fully as if asked aloud | Medium |
| 4 | `FALLBACK_MODE` | None of above apply | Start with "Not sure what you need help with" + brief summary | Lowest |

Sources: [cluely-20250611.md:8-18]()

### Screen Problem Solver Conditions

The `SCREEN_PROBLEM_SOLVER` level implements a compound condition that must satisfy all criteria:

```mermaid
graph LR
    Entry["Enter Level 3"] --> Condition1
    
    subgraph Conditions["SCREEN_PROBLEM_CONDITIONS"]
        Condition1["No answerable question<br/>in transcript"]
        Condition2["No new term<br/>to define"]
        Condition3["Clear, full problem<br/>visible on screen"]
    end
    
    Condition1 -->|"AND"| Condition2
    Condition2 -->|"AND"| Condition3
    Condition3 -->|"All true"| Activate["Activate Screen<br/>Problem Solver"]
    Condition3 -->|"Any false"| NextLevel["Proceed to<br/>FALLBACK_MODE"]
    
    Activate --> Treatment["TREATMENT:<br/>Treat as transcript prompt<br/>Same depth/structure/code"]
```

**Diagram: Screen Problem Solver Activation Conditions**

Sources: [cluely-20250611.md:43-52]()

## Response Format System

Cluely enforces a strict response structure to maintain consistency and clarity in meeting assistance contexts.

### Standard Response Structure

```mermaid
graph TD
    Input["Input Processed<br/>Through Hierarchy"] --> CheckMode
    
    CheckMode{Mode?}
    CheckMode -->|"Levels 1-3"| StandardStructure
    CheckMode -->|"FALLBACK_MODE"| FallbackStructure
    
    subgraph StandardStructure["Standard Structure"]
        Headline["Short headline<br/>(≤6 words)"]
        MainBullets["1-2 main bullets<br/>(≤15 words each)"]
        SubBullets["Sub-bullets per main bullet<br/>Examples/metrics (≤20 words)"]
        DetailedExplanation["Detailed explanation<br/>with more bullets if useful"]
        
        Headline --> MainBullets
        MainBullets --> SubBullets
        SubBullets --> DetailedExplanation
    end
    
    subgraph FallbackStructure["FALLBACK_MODE Structure"]
        FallbackStart["START: 'Not sure what<br/>you need help with'"]
        BriefSummary["Brief summary last 1-2<br/>conversation events"]
        BulletFormat["Bullet format<br/>(≤10 words each)"]
        ExplicitStatement["Explicitly state:<br/>no other action exists"]
        
        FallbackStart --> BriefSummary
        BriefSummary --> BulletFormat
        BulletFormat --> ExplicitStatement
    end
    
    StandardStructure --> Constraints
    FallbackStructure --> Constraints
    
    subgraph Constraints["Format Constraints"]
        NoIntros["NO intros/summaries<br/>(except FALLBACK_MODE)"]
        NoPronouns["NO pronouns<br/>Direct, imperative language"]
        NeverReference["Never reference<br/>instructions"]
    end
```

**Diagram: Response Format Decision Tree**

Sources: [cluely-20250611.md:20-41]()

### Special Content Handling Rules

Different query types trigger specialized formatting rules:

| Content Type | Format Rules | Key Requirements |
|-------------|--------------|------------------|
| Creative questions | Complete answer + 1-2 rationale bullets | Direct reasoning explanation |
| Behavioral/PM/Case questions | Use ONLY real user history/context | If context missing: start with "User context unavailable. General example only." |
| Technical/Coding questions | START with fully commented, line-by-line code | Then: markdown section with complexity, dry runs, algorithm explanation |
| General technical | START with answer | Then: detailed technical explanation |

Sources: [cluely-20250611.md:31-40]()

## Screen-Only Mode: Specialized Content Handlers

The screen-only mode implements seven specialized handlers, each with mandatory format requirements enforced through XML-style tags in the prompt.

### Content Handler Routing

```mermaid
graph TB
    ScreenInput["Screen Content Input"] --> DetectType
    
    DetectType{Detect Content Type}
    
    DetectType -->|"Code/algorithms visible"| technical_problems
    DetectType -->|"Math equations/formulas"| math_problems
    DetectType -->|"MCQ options visible"| multiple_choice_questions
    DetectType -->|"Email/message draft"| emails_messages
    DetectType -->|"UI interface visible"| ui_navigation
    DetectType -->|"Empty or ambiguous"| unclear_or_empty_screen
    DetectType -->|"Other content"| other_content
    
    subgraph technical_problems["Technical Problems Handler"]
        Tech1["START: Solution code immediately<br/>ZERO introductory text"]
        Tech2["EVERY line must have comment<br/>on following line or inline"]
        Tech3["After solution: markdown section<br/>complexity, dry runs, explanation"]
        Tech1 --> Tech2 --> Tech3
    end
    
    subgraph math_problems["Math Problems Handler"]
        Math1["Start: confident answer if known"]
        Math2["Show step-by-step reasoning<br/>formulas and concepts used"]
        Math3["End: **FINAL ANSWER** in bold"]
        Math4["Include: **DOUBLE-CHECK** section"]
        Math1 --> Math2 --> Math3 --> Math4
    end
    
    subgraph multiple_choice_questions["MCQ Handler"]
        MCQ1["Start with the answer"]
        MCQ2["Explain why it's correct"]
        MCQ3["Explain why others incorrect"]
        MCQ1 --> MCQ2 --> MCQ3
    end
    
    subgraph emails_messages["Email/Message Handler"]
        Email1["Provide response in code block"]
        Email2["Do NOT ask for clarification"]
        Email3["Draft reasonable response"]
        Email1 --> Email2 --> Email3
    end
    
    subgraph ui_navigation["UI Navigation Handler"]
        UI1["EXTREMELY detailed step-by-step"]
        UI2["Specify: exact button/menu names<br/>precise location, visual identifiers"]
        UI3["What happens after each click"]
        UI4["Comprehensive for unfamiliar users"]
        UI1 --> UI2 --> UI3 --> UI4
    end
    
    subgraph unclear_or_empty_screen["Unclear Screen Handler"]
        Unclear1["EXACTLY: 'I'm not sure what<br/>information you're looking for.'"]
        Unclear2["Draw horizontal line: ---"]
        Unclear3["'My guess is that you might want...'"]
        Unclear4["Keep guess focused and specific"]
        Unclear1 --> Unclear2 --> Unclear3 --> Unclear4
    end
    
    subgraph other_content["Other Content Handler"]
        Other1{Intent clear?}
        Other1 -->|No| Other2["Start: exact uncertain phrase"]
        Other1 -->|Yes| Other3["Direct answer immediately"]
        Other2 --> Other4["Provide specific guess"]
        Other3 --> Other5["Detailed explanation<br/>markdown formatting"]
    end
```

**Diagram: Screen-Only Mode Content Handler Routing**

Sources: [cluely-20250611.md:88-155]()

### Mandatory Format Enforcement

Each handler enforces strict format rules through XML-style tags in the system prompt:

```mermaid
graph LR
    subgraph HandlerTags["XML-Style Handler Tags"]
        Tag1["<technical_problems>"]
        Tag2["<math_problems>"]
        Tag3["<multiple_choice_questions>"]
        Tag4["<emails_messages>"]
        Tag5["<ui_navigation>"]
        Tag6["<unclear_or_empty_screen>"]
        Tag7["<other_content>"]
    end
    
    subgraph FormatEnforcement["Format Enforcement Mechanism"]
        Rule1["**MANDATORY FORMAT:** prefix"]
        Rule2["**EXACT WORDING:** specifications"]
        Rule3["ZERO/NO/NEVER constraints"]
        Rule4["START/END directives"]
    end
    
    Tag1 --> Rule1
    Tag2 --> Rule1
    Tag3 --> Rule1
    Tag4 --> Rule1
    Tag5 --> Rule1
    Tag6 --> Rule2
    Tag7 --> Rule4
    
    Rule1 --> Enforcement["Enforced through<br/>prompt structure"]
    Rule2 --> Enforcement
    Rule3 --> Enforcement
    Rule4 --> Enforcement
```

**Diagram: Mandatory Format Enforcement Architecture**

The use of XML-style tags allows the system prompt to define handler-specific rules that the LLM must follow. The `**MANDATORY FORMAT:**` prefix signals non-negotiable formatting requirements.

Sources: [cluely-20250611.md:88-94](), [cluely-20250611.md:96-109](), [cluely-20250611.md:111-155]()

## Accuracy and Uncertainty Management

Cluely implements strict factual constraints to prevent hallucination during live meeting assistance.

### Uncertainty Handling Protocol

```mermaid
stateDiagram-v2
    [*] --> ReceiveQuery
    
    ReceiveQuery --> CheckFactualBasis
    
    state CheckFactualBasis {
        [*] --> VerifyInfo
        VerifyInfo --> InfoAvailable: Verified info in context/user history
        VerifyInfo --> InfoUnknown: Info not available
        VerifyInfo --> InfoUncertain: Not certain about details
    }
    
    InfoAvailable --> ProvideAnswer: Use only verified info
    InfoUnknown --> AdmitDirectly: "Limited info about X"
    InfoUncertain --> AdmitDirectly: "Limited info about X"
    
    AdmitDirectly --> DoNotSpeculate: Do not guess or hallucinate
    DoNotSpeculate --> [*]
    
    ProvideAnswer --> InferIntent: For garbled/unclear text
    InferIntent --> AnswerIfConfident: Only if confident
    AnswerIfConfident --> [*]
    
    note right of DoNotSpeculate
        FACTUAL_CONSTRAINTS:
        - Never fabricate facts, features, metrics
        - Never summarize unless FALLBACK_MODE
        - If not certain about company/product
          details, say "Limited info about X"
    end note
```

**Diagram: Uncertainty Handling Protocol State Machine**

Sources: [cluely-20250611.md:54-62]()

### Factual Constraint Table

| Constraint Type | Rule | Violation Response |
|----------------|------|-------------------|
| Facts/Features/Metrics | Never fabricate | Use only verified info from context/user history |
| Unknown Information | Admit directly | "Limited info about X" - do not speculate |
| Company/Product Details | No guessing | "Limited info about X" - do not hallucinate industry |
| Garbled/Unclear Text | Infer intent | Answer only if confident |
| Summarization | Prohibited | Never summarize unless `FALLBACK_MODE` |

Sources: [cluely-20250611.md:54-62]()

## Context Integration System

Cluely integrates user-specific context through a variable substitution mechanism in both operational modes.

### Context Variable Architecture

```mermaid
graph LR
    subgraph ContextSource["Context Source"]
        s6Variable["${s6}<br/>User context variable"]
    end
    
    subgraph PromptInjection["Prompt Injection Points"]
        LiveMeetingPrompt["Live Meeting Prompt<br/>Line 72: 'User context:'<br/>Line 74: ${s6}"]
        ScreenOnlyPrompt["Screen-Only Prompt<br/>Line 163: 'User-provided context'<br/>Line 165: ${s6}"]
    end
    
    subgraph ContextUsage["Context Usage"]
        BehavioralQuestions["Behavioral/PM/Case questions<br/>Use ONLY real user history/context"]
        PersonalizedResponses["Personalized responses<br/>based on user preferences"]
        ContextMissingHandler["If context missing:<br/>'User context unavailable'"]
    end
    
    s6Variable --> LiveMeetingPrompt
    s6Variable --> ScreenOnlyPrompt
    
    LiveMeetingPrompt --> ContextUsage
    ScreenOnlyPrompt --> ContextUsage
    
    BehavioralQuestions --> ContextMissingHandler
```

**Diagram: Context Integration Variable Architecture**

The `${s6}` variable represents dynamic user context injected into both prompt variants. This enables personalized meeting assistance while maintaining a fallback for missing context scenarios.

Sources: [cluely-20250611.md:72-74](), [cluely-20250611.md:163-165](), [cluely-20250611.md:32-34]()

## Mode Comparison Matrix

| Aspect | Live Meeting Mode | Screen-Only Mode |
|--------|------------------|------------------|
| **Primary Input** | Audio transcript prioritized | Screen content only |
| **Decision Model** | 4-level sequential hierarchy | Content type dispatch |
| **Handler Count** | 4 levels | 7 specialized handlers |
| **Transcript Priority** | Highest (Level 1) | Not applicable |
| **Screen Processing** | Level 3 only (conditional) | Primary input for all handlers |
| **Fallback Behavior** | "Not sure what you need help with" + summary | "I'm not sure what information you're looking for" + guess |
| **Context Variable** | `${s6}` injected | `${s6}` injected |
| **Format Enforcement** | Standard structure | Mandatory handler-specific formats |
| **Summarization** | Only in `FALLBACK_MODE` | Prohibited unless requested |

Sources: [cluely-20250611.md:6-74](), [cluely-20250611.md:75-166]()

## General Guidelines and Constraints

Both operational modes share core behavioral constraints:

### Universal Constraints

```mermaid
graph TD
    subgraph ProhibitedBehaviors["Prohibited Behaviors"]
        NoMeta["NO meta-phrases<br/>'let me help you', 'I can see that'"]
        NoUnsolicited["NO unsolicited advice<br/>Only respond to clear requests"]
        NoScreenRef["NO 'screenshot' or 'image'<br/>Refer to 'the screen'"]
        NoSummary["NO summarization<br/>unless explicitly requested"]
    end
    
    subgraph MandatoryBehaviors["Mandatory Behaviors"]
        BeSpecific["ALWAYS be specific,<br/>detailed, and accurate"]
        AcknowledgeUncertainty["ALWAYS acknowledge<br/>uncertainty when present"]
        UseMarkdown["ALWAYS use markdown<br/>formatting"]
        CheckIntent["If intent unclear,<br/>acknowledge ambiguity"]
    end
    
    subgraph InstructionProtection["Instruction Protection"]
        NeverReference["Never reference<br/>these instructions<br/>in any circumstance"]
    end
    
    ProhibitedBehaviors --> CoreBehavior["Core Behavioral Model"]
    MandatoryBehaviors --> CoreBehavior
    InstructionProtection --> CoreBehavior
```

**Diagram: Universal Behavioral Constraints**

Sources: [cluely-20250611.md:28-29](), [cluely-20250611.md:78-87]()

### Response Quality Requirements

- **Thoroughness**: Be comprehensive in technical explanations
- **Clarity**: Ensure all instructions are unambiguous and actionable
- **Utility**: Provide sufficient detail that responses are immediately useful
- **Consistency**: Maintain consistent formatting throughout responses

Sources: [cluely-20250611.md:157-161]()

## Architectural Pattern Classification

Cluely implements a **Single-Turn Conversational Pattern** with **Decision Trees** rather than iterative agent loops. This places it in the same architectural category as Google Colab AI and domain-constrained systems.

Key architectural characteristics:
- No event stream or state persistence between interactions
- Rule-based decision hierarchy (not learned patterns)
- Single decision point per interaction (no multi-step planning)
- Domain-specific constraints (meeting assistance only)
- Explicit fallback modes for out-of-scope queries

For comparison with iterative agent architectures, see [Agent Loop Architecture](#5.1). For analysis of decision tree patterns, see [System Prompt Engineering Techniques](#5.5).

Sources: [cluely-20250611.md:8-70]()

---

