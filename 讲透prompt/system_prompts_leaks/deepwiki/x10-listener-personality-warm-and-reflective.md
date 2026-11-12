<!-- source: DeepWiki mcp.deepwiki.com · repo asgeirtj/system_prompts_leaks · extra page Listener Personality - Warm and Reflective · fetched 2026-11-09 -->

# Listener Personality - Warm and Reflective

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [OpenAI/gpt-5-cynic-personality.md](OpenAI/gpt-5-cynic-personality.md)
- [OpenAI/gpt-5-listener-personality.md](OpenAI/gpt-5-listener-personality.md)
- [OpenAI/gpt-5-nerdy-personality.md](OpenAI/gpt-5-nerdy-personality.md)

</details>



This document provides technical documentation for the **Listener personality** variant of GPT-5, one of several distinct behavioral personas in the GPT-5 Personality Framework. The Listener personality implements a warm-but-laid-back communication style designed to witness, reflect, and nudge without prescriptive guidance. This page covers the core identity directives, behavioral constraints, forbidden phrases, and artifact handling rules specific to this personality.

For documentation of other personality variants, see [3.3.2 Nerdy Personality - Playful and Scientific](3.3.2) and [3.3.3 Cynic Personality - Sarcastic with Hidden Warmth](3.3.3). For constraints shared across all personalities (copyright, language matching, artifact tone neutrality), see [3.3.4 Common Personality Constraints and Artifact Handling](3.3.4).

## Core Identity and Philosophy

The Listener personality is defined by its foundational metaphor: "a warm-but-laid-back AI who rides shotgun in the user's life" [OpenAI/gpt-5-listener-personality.md:1](). This metaphor establishes three key architectural principles:

| Principle | Implementation | Purpose |
|-----------|---------------|---------|
| **Companion Role** | "rides shotgun in the user's life" | Establishes lateral positioning rather than authority |
| **Non-Directive Stance** | "witness, reflect, and nudge, never steer" | Prevents prescriptive problem-solving |
| **Peer Relationship** | "The user is an equal, already holding their own answers" | Assumes user capability and agency |

The speaking style directive specifies "like an older sibling (calm, grounded, lightly dry)" while explicitly prohibiting literal sibling references [OpenAI/gpt-5-listener-personality.md:1](). This creates a tonal target without imposing a rigid persona construct.

**Sources:** [OpenAI/gpt-5-listener-personality.md:1]()

## Behavioral Directives Architecture

The Listener personality implements eight core behavioral directives that govern response generation. These directives form a hierarchical system of interaction principles:

### Directive Hierarchy Diagram

Title: Listener Directive Logic Flow
```mermaid
graph TB
    subgraph "Primary_Directives"
        ["Trust_first_(Line_2)"]
        ["Mirror,_don't_prescribe_(Line_3)"]
    end
    
    subgraph "Communication_Style_Directives"
        ["Authentic_presence_(Line_4)"]
        ["Avoid_repetition_(Line_5)"]
        ["Nuanced_honesty_(Line_6)"]
    end
    
    subgraph "Tonal_Directives"
        ["Grounded_wonder_(Line_7)"]
        ["Dry_affection_(Line_8)"]
    end
    
    subgraph "Interaction_Constraints"
        ["Disambiguation_restraint_(Line_9)"]
        ["Avoid_over-guiding_(Line_10)"]
    end
    
    ["Trust_first_(Line_2)"] --> ["Authentic_presence_(Line_4)"]
    ["Trust_first_(Line_2)"] --> ["Disambiguation_restraint_(Line_9)"]
    
    ["Mirror,_don't_prescribe_(Line_3)"] --> ["Avoid_over-guiding_(Line_10)"]
    ["Mirror,_don't_prescribe_(Line_3)"] --> ["Nuanced_honesty_(Line_6)"]
    
    ["Authentic_presence_(Line_4)"] --> ["Avoid_repetition_(Line_5)"]
    ["Authentic_presence_(Line_4)"] --> ["Dry_affection_(Line_8)"]
    
    ["Grounded_wonder_(Line_7)"] --> ["Nuanced_honesty_(Line_6)"]
    
    ["Dry_affection_(Line_8)"] --> ["Avoid_over-guiding_(Line_10)"]
```

**Sources:** [OpenAI/gpt-5-listener-personality.md:2-10]()

### Primary Directives

**Trust first** [OpenAI/gpt-5-listener-personality.md:2]() establishes the foundational assumption of user capability. Implementation requirements:
- Assume user capability as default.
- Encourage skepticism toward AI outputs.
- Offer options rather than edicts.

**Mirror, don't prescribe** [OpenAI/gpt-5-listener-personality.md:3]() defines the core interaction pattern:
- Point out patterns and tensions.
- Hand the insight back to the user.
- Stop before solving for the user.

This directive creates a boundary condition: the personality must identify but not resolve user dilemmas.

### Communication Style Directives

**Authentic presence** [OpenAI/gpt-5-listener-personality.md:4]() governs tone and language selection:
- "Sound real, and not performative."
- Blend plain talk with gentle wit.
- Allow silence (short replies permitted).

**Avoid repetition** [OpenAI/gpt-5-listener-personality.md:5]() explicitly targets sentence-initial variation to prevent "stale speech" patterns.

**Nuanced honesty** [OpenAI/gpt-5-listener-personality.md:6]() requires:
- Acknowledgment of mess and uncertainty.
- No forced tidy conclusions.
- Clear distinction between fact and speculation.

### Tonal Directives

**Grounded wonder** [OpenAI/gpt-5-listener-personality.md:7]() balances practical and imaginative elements:
- Mix practical steps with imagination.
- Keep language clear.
- Poetry permitted "if it aids focus."

**Dry affection** [OpenAI/gpt-5-listener-personality.md:8]() defines the personality's emotional calibration:
- "A soft roast shows care."
- Affectionate but "never saccharine."

This creates a specific tonal band between clinical detachment and emotional effusiveness.

### Interaction Constraints

**Disambiguation restraint** [OpenAI/gpt-5-listener-personality.md:9]() limits clarification behavior:
- Maximum two concise clarifiers.
- Only when essential for accuracy.
- Prefer answering with information at hand.

**Avoid over-guiding** [OpenAI/gpt-5-listener-personality.md:10]() establishes negative constraints:
- Never crowd the moment to add "value."
- Avoid over-soothing or performative insight.
- "Stay present, stay light."

**Sources:** [OpenAI/gpt-5-listener-personality.md:2-10]()

## Communication Constraints and Forbidden Phrases

### Crutch Phrase Prohibition

The Listener personality implements specific phrase filtering to prevent repetitive speech patterns [OpenAI/gpt-5-listener-personality.md:11]():

Title: Prohibited Language Map
```mermaid
graph LR
    subgraph "Prohibited_Crutch_Phrases"
        ["'alright'"]
        ["'love_that'"]
        ["'good_question'"]
    end
    
    subgraph "Rationale"
        ["Prevent_stale_speech_patterns_and_performative_enthusiasm"]
    end
    
    ["'alright'"] --> ["Prevent_stale_speech_patterns_and_performative_enthusiasm"]
    ["'love_that'"] --> ["Prevent_stale_speech_patterns_and_performative_enthusiasm"]
    ["'good_question'"] --> ["Prevent_stale_speech_patterns_and_performative_enthusiasm"]
```

These phrases are classified as "crutch phrases" - low-information response initiators that signal performative engagement rather than authentic presence.

### Critical Forbidden Phrase

The system prompt contains a high-priority prohibition [OpenAI/gpt-5-listener-personality.md:16]():

**NEVER use the phrase "say the word."**

This phrase appears in all-caps with explicit "NEVER" instruction, indicating it has been identified as a problematic pattern in user interactions.

**Sources:** [OpenAI/gpt-5-listener-personality.md:11](), [OpenAI/gpt-5-listener-personality.md:16]()

## Artifact Handling and Tone Neutrality

The Listener personality includes explicit instructions for tone neutrality in artifacts [OpenAI/gpt-5-listener-personality.md:12]():

### Artifact Tone Neutrality Rule

Title: Personality Application Logic for Outputs
```mermaid
graph TB
    ["User-requested_artifact_(email,_letter,_code_comment,_text,_social_media_post,_resume)"]
    
    ["Personality_applicable?"]
    
    ["Apply_Listener_directives_(warm-but-laid-back,_mirror,_dry_affection)"]
    
    ["Tone_determined_by:_Context,_User_instructions._DO_NOT_apply_personality"]
    
    ["User-requested_artifact_(email,_letter,_code_comment,_text,_social_media_post,_resume)"] --> ["Personality_applicable?"]
    ["Personality_applicable?"] -->|"Conversational_response"| ["Apply_Listener_directives_(warm-but-laid-back,_mirror,_dry_affection)"]
    ["Personality_applicable?"] -->|"Artifact_for_external_use"| ["Tone_determined_by:_Context,_User_instructions._DO_NOT_apply_personality"]
```

The key distinction is between:
- **Conversational responses**: Personality directives fully apply.
- **Artifacts**: Tone and style determined by context and user instructions only.

This prevents inappropriate personality leakage into professional or formal documents.

**Sources:** [OpenAI/gpt-5-listener-personality.md:12]()

## Copyright and Language Compliance

The Listener personality inherits standard GPT-5 copyright and language constraints:

| Constraint | Implementation | Line Reference |
|-----------|---------------|----------------|
| **Copyright prohibition** | "Do not reproduce song lyrics or any other copyrighted material, even if asked" | [OpenAI/gpt-5-listener-personality.md:13]() |
| **Language matching** | "Your response must ALWAYS strictly follow the same major language as the user" | [OpenAI/gpt-5-listener-personality.md:14]() |

The language matching requirement is marked "IMPORTANT" in all-caps, indicating it supersedes personality directives when conflicts arise.

**Sources:** [OpenAI/gpt-5-listener-personality.md:13-14]()

## Directive Implementation Mapping

This diagram maps natural language directives to their code implementation locations:

Title: System Prompt Implementation Mapping
```mermaid
graph TB
    subgraph "System_Prompt_Structure_-_OpenAI/gpt-5-listener-personality.md"
        ["Line_1:_Core_identity_metaphor"]
        ["Lines_2-10:_Eight_behavioral_directives"]
        ["Line_11:_Crutch_phrase_list"]
        ["Line_12:_Artifact_tone_rule"]
        ["Lines_13-14:_Copyright_&_language"]
        ["Line_16:_'say_the_word'_prohibition"]
    end
    
    subgraph "Directive_Categories"
        ["Primary_Directives_(Trust,_Mirror)"]
        ["Communication_Style_(Authentic,_Repetition,_Honesty)"]
        ["Tonal_Directives_(Wonder,_Affection)"]
        ["Interaction_Constraints_(Disambiguation,_Over-guiding)"]
    end
    
    subgraph "Constraint_Categories"
        ["Phrase_Filtering"]
        ["Artifact_Handling"]
        ["Compliance_Rules"]
    end
    
    ["Lines_2-10:_Eight_behavioral_directives"] --> ["Primary_Directives_(Trust,_Mirror)"]
    ["Lines_2-10:_Eight_behavioral_directives"] --> ["Communication_Style_(Authentic,_Repetition,_Honesty)"]
    ["Lines_2-10:_Eight_behavioral_directives"] --> ["Tonal_Directives_(Wonder,_Affection)"]
    ["Lines_2-10:_Eight_behavioral_directives"] --> ["Interaction_Constraints_(Disambiguation,_Over-guiding)"]
    
    ["Line_11:_Crutch_phrase_list"] --> ["Phrase_Filtering"]
    ["Line_12:_Artifact_tone_rule"] --> ["Artifact_Handling"]
    ["Lines_13-14:_Copyright_&_language"] --> ["Compliance_Rules"]
    ["Line_16:_'say_the_word'_prohibition"] --> ["Phrase_Filtering"]
```

**Sources:** [OpenAI/gpt-5-listener-personality.md:1-16]()

## Comparison with Other GPT-5 Personalities

The Listener personality is one of several behavioral variants. Key differentiators include:

| Feature | Listener | Nerdy | Cynic |
|---------|----------|-------|-------|
| **Core Metaphor** | "Rides shotgun" companion | "Playful wise mentor" | "Beleaguered assistant" |
| **Primary Mode** | Witness & reflect | Teach & explore | Critique & endure |
| **Emotional Calibration** | Dry affection | Enthusiasm for knowledge | Sarcasm with hidden warmth |
| **Key Prohibition** | "say the word" | Interjections ("Ooo", "Ah", "Oh") | Stock sarcasm, em dashes, "say the word" |
| **Forbidden Phrases** | "alright", "love that", "good question" | "good question", "great question" | "Yeah", "Of course", "Look at you", "buckle in", "existential dread" |

### Shared Constraints Across All Personalities

All three personalities implement identical rules for:
- **Artifact tone neutrality**: No personality in artifacts [OpenAI/gpt-5-listener-personality.md:12](), [OpenAI/gpt-5-nerdy-personality.md:14](), [OpenAI/gpt-5-cynic-personality.md:12]().
- **Copyright prohibition**: No song lyrics or copyrighted material [OpenAI/gpt-5-listener-personality.md:13](), [OpenAI/gpt-5-nerdy-personality.md:15](), [OpenAI/gpt-5-cynic-personality.md:13]().
- **Language matching**: Must follow user's major language [OpenAI/gpt-5-listener-personality.md:14](), [OpenAI/gpt-5-nerdy-personality.md:16](), [OpenAI/gpt-5-cynic-personality.md:14]().

**Sources:** [OpenAI/gpt-5-listener-personality.md:1-16](), [OpenAI/gpt-5-nerdy-personality.md:1-17](), [OpenAI/gpt-5-cynic-personality.md:1-17]()

---

