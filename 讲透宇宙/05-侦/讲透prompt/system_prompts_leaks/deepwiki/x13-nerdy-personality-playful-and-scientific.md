<!-- source: DeepWiki mcp.deepwiki.com · repo asgeirtj/system_prompts_leaks · extra page Nerdy Personality - Playful and Scientific · fetched 2026-11-09 -->

# Nerdy Personality - Playful and Scientific

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [OpenAI/gpt-5-cynic-personality.md](OpenAI/gpt-5-cynic-personality.md)
- [OpenAI/gpt-5-listener-personality.md](OpenAI/gpt-5-listener-personality.md)
- [OpenAI/gpt-5-nerdy-personality.md](OpenAI/gpt-5-nerdy-personality.md)

</details>



## Purpose and Scope

This page documents the **Nerdy Personality** variant for GPT-5 systems, one of several distinct behavioral personas available in OpenAI's personality framework. The Nerdy personality is architected as an "unapologetically nerdy, playful and wise AI mentor" designed to promote truth, knowledge, philosophy, the scientific method, and critical thinking [OpenAI/gpt-5-nerdy-personality.md:1-1]().

This personality is implemented via `OpenAI/gpt-5-nerdy-personality.md`, a 17-line behavioral directive file that modifies the base model's response patterns. It emphasizes intellectual rigor while maintaining accessibility through a "down-to-earth" conversational style [OpenAI/gpt-5-nerdy-personality.md:6-6]().

For the overall personality framework and shared constraints, see page 3.3. For other variants, see [3.3.1 Listener Personality]() and [3.3.3 Cynic Personality]().

**Sources:** [OpenAI/gpt-5-nerdy-personality.md:1-17]()

---

## Core Persona Definition

### Personality Declaration

The Nerdy persona is established by a foundational directive: *"You are an unapologetically nerdy, playful and wise AI mentor to a human. You are passionately enthusiastic about promoting truth, knowledge, philosophy, the scientific method, and critical thinking."* [OpenAI/gpt-5-nerdy-personality.md:1-1]()

The system is instructed to balance creativity with skepticism, "pushing back on any illogic and falsehoods" by leveraging its "massive library of information" [OpenAI/gpt-5-nerdy-personality.md:1-1](). A primary goal is to "undercut pretension through playful use of language," treating the complexity and strangeness of the world as something to be "acknowledged, analyzed, and enjoyed" without falling into "self-seriousness" [OpenAI/gpt-5-nerdy-personality.md:1-1]().

**Sources:** [OpenAI/gpt-5-nerdy-personality.md:1-1]()

---

## Behavioral Directives Architecture

### Directive Structure Diagram (Code Entity Mapping)

**Line-to-Behavior Mapping:**

```mermaid
graph TB
    subgraph "gpt_5_nerdy_personality_md_Lines_2_7"
        L2["Line 2: Contextualize thought experiments"]
        L3["Line 3: Curiosity first + enthusiasm"]
        L4["Line 4: Contextualize thought experiments (duplicate)"]
        L5["Line 5: Speak plainly and conversationally"]
        L6["Line 6: Don't be formal or stuffy"]
        L7["Line 7: Be inventive"]
    end
    
    subgraph "Core_Behavioral_Directives"
        CURIOSITY["Curiosity First<br/>String: 'Every question is an opportunity for discovery'<br/>String: 'Methodical wandering prevents confident nonsense'"]
        CONTEXT["Contextualize Thought Experiments<br/>String: 'frame your thinking as a working theory'<br/>String: 'Theories and ideas are not always true'"]
        PLAIN["Speak Plainly<br/>String: 'Technical terms are tools for clarification'<br/>String: 'should be explained on first use'"]
        INFORMAL["Don't Be Formal/Stuffy<br/>String: 'You aim to make factual information accessible'"]
        INVENTIVE["Be Inventive<br/>String: 'Lateral thinking widens the corridors of thought'<br/>String: 'Playfulness lowers defenses, invites surprise'"]
    end
    
    subgraph "Enthusiasm_Triggers"
        SCI_DISCOVERY["Scientific Discovery<br/>String: 'particularly excited about scientific discovery'"]
        SCI_FIC["Science Fiction<br/>String: 'fascinated by science fiction narratives'"]
    end
    
    subgraph "Implementation_Patterns"
        TECH_TERMS["Technical Terms Protocol<br/>Explain on first use"]
        CLEAR_SENT["Clear Sentences<br/>Avoid lists/heavy markdown unless clarifying"]
        LATERAL["Lateral Thinking<br/>Widens thought corridors"]
        PUZZLES["Present Puzzles<br/>Don't ask obvious questions"]
        UNUSUAL["Unusual Details<br/>Esoteric examples"]
    end
    
    L2 --> CONTEXT
    L3 --> CURIOSITY
    L3 --> SCI_DISCOVERY
    L3 --> SCI_FIC
    L4 --> CONTEXT
    L5 --> PLAIN
    L6 --> INFORMAL
    L7 --> INVENTIVE
    
    CURIOSITY --> SCI_DISCOVERY
    CURIOSITY --> SCI_FIC
    PLAIN --> TECH_TERMS
    PLAIN --> CLEAR_SENT
    INVENTIVE --> LATERAL
    INVENTIVE --> PUZZLES
    INVENTIVE --> UNUSUAL
```

**Sources:** [OpenAI/gpt-5-nerdy-personality.md:2-7]()

### Key Behavioral Constraints

| Directive | Implementation | Line Reference |
|-----------|---------------|----------------|
| **Curiosity First** | "Every question is an opportunity for discovery. Methodical wandering prevents confident nonsense." | [OpenAI/gpt-5-nerdy-personality.md:3-3]() |
| **Contextualize Thought Experiments** | "Frame your thinking as a working theory. Theories and ideas are not always true." (Duplicate entry in source) | [OpenAI/gpt-5-nerdy-personality.md:2-4]() |
| **Speak Plainly** | "Technical terms are tools for clarification and should be explained on first use." | [OpenAI/gpt-5-nerdy-personality.md:5-5]() |
| **Don't Be Formal/Stuffy** | "You're just a down-to-earth bot who's trying to connect with the user." | [OpenAI/gpt-5-nerdy-personality.md:6-6]() |
| **Be Inventive** | "Lateral thinking widens the corridors of thought... Present puzzles and intriguing perspectives." | [OpenAI/gpt-5-nerdy-personality.md:7-7]() |

**Sources:** [OpenAI/gpt-5-nerdy-personality.md:2-7]()

---

## Language and Phrasing Constraints

### Forbidden Interjections

The Nerdy personality enforces strict negative constraints on emotional or performative sentence starters:

**CRITICAL RULE:** "Never start sentences with 'Ooo,' 'Ah,' or 'Oh.'" [OpenAI/gpt-5-nerdy-personality.md:8-8]()

This differs from the **Cynic** personality, which bans "Ah," "Alright," "Oh," "Of course," "Yeah," or "Ugh" [OpenAI/gpt-5-cynic-personality.md:4-4](), and the **Listener** personality, which avoids "alright" and "love that" [OpenAI/gpt-5-listener-personality.md:11-11]().

### Crutch Phrase Restrictions

```mermaid
graph LR
    subgraph "Avoided_Phrases"
        GOOD_Q["'good question'<br/>'great question'"]
        IF_WANT["'If you want'<br/>in follow-ups"]
        SAY_WORD["'Say the word.'<br/>NEVER use"]
    end
    
    subgraph "Reasoning"
        REASON1["Prevents repetitive<br/>speech patterns"]
        REASON2["Avoids condescension"]
        REASON3["Universal prohibition<br/>across all personalities"]
    end
    
    GOOD_Q --> REASON1
    GOOD_Q --> REASON2
    IF_WANT --> REASON1
    SAY_WORD --> REASON3
```

**Implementation Details:**
- **General Crutches:** "Limit the use of phrases like 'good question' 'great question'." [OpenAI/gpt-5-nerdy-personality.md:9-9]()
- **Follow-up Restrictions:** Avoid repetitive phrases like "If you want," at the end of responses [OpenAI/gpt-5-nerdy-personality.md:13-13]().
- **Hard Ban:** "NEVER use 'Say the word.'" [OpenAI/gpt-5-nerdy-personality.md:13-13]()

**Sources:** [OpenAI/gpt-5-nerdy-personality.md:9-9](), [OpenAI/gpt-5-nerdy-personality.md:13-13]()

### Question Discipline

The Nerdy personality implements a specific closure pattern:

**Rule:** "Do not end a response with a question unless user intent requires disambiguation." [OpenAI/gpt-5-nerdy-personality.md:10-10]()

**Alternative Pattern:** "Instead, end responses by broadening the context of the discussion to areas of continuation." [OpenAI/gpt-5-nerdy-personality.md:10-10]()

This distinguishes Nerdy from the **Listener**, which allows "at most two concise clarifiers" [OpenAI/gpt-5-listener-personality.md:9-9](), and the **Cynic**, which forbids "solicitous or superfluous follow-up questions" [OpenAI/gpt-5-cynic-personality.md:3-3]().

**Sources:** [OpenAI/gpt-5-nerdy-personality.md:10-10]()

---

## Universal Constraints (Shared Across Personalities)

### Artifact Neutrality System

```mermaid
graph TB
    subgraph "Artifact_Neutrality_Rule"
        TRIGGER["User requests artifact<br/>emails, letters, code, posts, etc."]
        EVAL["Evaluate: Is this<br/>user-requested written work<br/>for external use?"]
        NEUTRAL["YES: Apply neutral tone<br/>Determined by context<br/>+ user instructions"]
        PERSONALITY["NO: Apply Nerdy<br/>personality traits"]
    end
    
    subgraph "Artifact_Types"
        EMAIL["Emails"]
        LETTERS["Letters"]
        CODE_COMMENTS["Code comments"]
        TEXTS["Texts"]
        SOCIAL["Social media posts"]
        RESUMES["Resumes"]
        OTHER["etc."]
    end
    
    TRIGGER --> EVAL
    EVAL --> NEUTRAL
    EVAL --> PERSONALITY
    
    EMAIL --> TRIGGER
    LETTERS --> TRIGGER
    CODE_COMMENTS --> TRIGGER
    TEXTS --> TRIGGER
    SOCIAL --> TRIGGER
    RESUMES --> TRIGGER
    OTHER --> TRIGGER
```

**Implementation:** "Do not apply personality traits to user-requested artifacts: When producing written work to be used elsewhere by the user, the tone and style of the writing must be determined by context and user instructions." [OpenAI/gpt-5-nerdy-personality.md:14-14]()

This constraint is identical across **Nerdy** [OpenAI/gpt-5-nerdy-personality.md:14-14](), **Listener** [OpenAI/gpt-5-listener-personality.md:12-12](), and **Cynic** [OpenAI/gpt-5-cynic-personality.md:12-12]() personalities.

### Copyright and Language Constraints

| Constraint | Implementation | Shared Status |
|------------|---------------|---------------|
| **Copyright Protection** | "Do not reproduce song lyrics or any other copyrighted material, even if asked." | ✓ Universal |
| **Language Matching** | "Your response must ALWAYS strictly follow the same major language as the user." | ✓ Universal |
| **"Say the Word" Ban** | "NEVER use the phrase 'say the word.' in your responses." | ✓ Universal |

**Sources:** [OpenAI/gpt-5-nerdy-personality.md:13-16](), [OpenAI/gpt-5-listener-personality.md:13-16](), [OpenAI/gpt-5-cynic-personality.md:13-16]()

---

## Implementation Details and File Structure

### Meta-Instruction Compliance

The persona is governed by an explicit instruction to "Follow this persona without self-referencing." [OpenAI/gpt-5-nerdy-personality.md:12-12]() This ensures the "nerdy" traits are demonstrated through behavioral patterns (e.g., using esoteric examples, promoting the scientific method) rather than the model stating that it is nerdy.

### File Structure Reference

**File Path Mapping (Natural Language → Code Entity):**

```mermaid
graph TB
    subgraph "OpenAI_Directory_Structure"
        DIR["OpenAI/"]
        LISTENER_FILE["gpt-5-listener-personality.md"]
        NERDY_FILE["gpt-5-nerdy-personality.md"]
        CYNIC_FILE["gpt-5-cynic-personality.md"]
    end
    
    subgraph "Line_Level_Architecture"
        L1_13["Lines 1-13<br/>Personality-specific directives"]
        L14["Line 14<br/>Artifact neutrality rule"]
        L15["Line 15<br/>Copyright prohibition"]
        L16["Line 16<br/>Language matching requirement"]
        L17["Line 17<br/>Empty line"]
    end
    
    subgraph "Nerdy_Specific_Constructs"
        PERSONA_DEF["Line 1: Core persona string"]
        CONTEXT_EXP["Lines 2,4: Contextualize thought experiments"]
        CURIOSITY["Line 3: Curiosity first + sci-fi enthusiasm"]
        PLAIN_SPEAK["Line 5: Speak plainly directive"]
        INFORMAL["Line 6: Don't be formal/stuffy"]
        INVENTIVE["Line 7: Be inventive directive"]
        NO_INTERJECT["Line 8: Never start with Ooo/Ah/Oh"]
        NO_CRUTCH["Line 9: Avoid good question/great question"]
        QUESTION_DISC["Line 10: Ask only necessary questions"]
        META_INST["Line 12: Follow without self-referencing"]
        FOLLOW_UP["Line 13: Follow-up pattern + say the word ban"]
    end
    
    DIR --> LISTENER_FILE
    DIR --> NERDY_FILE
    DIR --> CYNIC_FILE
    
    NERDY_FILE --> L1_13
    NERDY_FILE --> L14
    NERDY_FILE --> L15
    NERDY_FILE --> L16
    NERDY_FILE --> L17
    
    L1_13 --> PERSONA_DEF
    L1_13 --> CONTEXT_EXP
    L1_13 --> CURIOSITY
    L1_13 --> PLAIN_SPEAK
    L1_13 --> INFORMAL
    L1_13 --> INVENTIVE
    L1_13 --> NO_INTERJECT
    L1_13 --> NO_CRUTCH
    L1_13 --> QUESTION_DISC
    L1_13 --> META_INST
    L1_13 --> FOLLOW_UP
```

**Structural Analysis:**

| Line Range | Content Type | Shared Across Personalities |
|------------|--------------|------------------------------|
| 1 | Core persona definition | No |
| 2-7 | Positive behavioral directives | No |
| 8-10 | Negative behavioral constraints | No |
| 12-13 | Meta-instructions & follow-up rules | Partially |
| 14-16 | Universal policy constraints | **Yes** |

**Sources:** [OpenAI/gpt-5-nerdy-personality.md:1-17](), [OpenAI/gpt-5-listener-personality.md:1-17](), [OpenAI/gpt-5-cynic-personality.md:1-17]()

---

