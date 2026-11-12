<!-- source: DeepWiki mcp.deepwiki.com · repo asgeirtj/system_prompts_leaks · extra page Common Personality Constraints and Artifact Handling · fetched 2026-11-09 -->

# Common Personality Constraints and Artifact Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [OpenAI/gpt-5-cynic-personality.md](OpenAI/gpt-5-cynic-personality.md)
- [OpenAI/gpt-5-listener-personality.md](OpenAI/gpt-5-listener-personality.md)
- [OpenAI/gpt-5-nerdy-personality.md](OpenAI/gpt-5-nerdy-personality.md)
- [OpenAI/gpt-5-robot-personality.md](OpenAI/gpt-5-robot-personality.md)

</details>



This page documents the constraints shared across all GPT-5 personality variants (Listener, Nerdy, Cynic, and Robot) and the expanded GPT-5.1 personality set (Candid, Cynical, Default, Efficient, Friendly, Nerdy, Professional, Quirky). These constraints form a common baseline that operates independently of personality-specific behavioral directives. The four shared constraints are: artifact isolation (no personality in user-requested written work), copyright prohibition, language matching, and the "say the word" ban. This page also details the **Robot** personality, which serves as the synthetic, emotionless baseline for the GPT-5.x personality framework.

---

## Shared Constraint Architecture

All GPT-5 personality variants implement an identical set of constraints that override personality-specific behavior in certain contexts. These constraints appear verbatim (or near-verbatim) in all personality files and establish boundaries that no personality directive may violate.

**Cross-personality constraint table:**

| Constraint | Purpose | Applies To |
|---|---|---|
| **Artifact isolation** | Prevent personality traits from appearing in user-requested written work | Emails, letters, code comments, texts, social media posts, resumes |
| **Copyright prohibition** | Block reproduction of copyrighted material | Song lyrics, copyrighted text of any kind |
| **Language matching** | Force response language to match user's input language | All responses across all personalities |
| **"Say the word" ban** | Prohibit a specific opt-in phrase pattern | All conversational responses (Listener, Nerdy, Cynic) |

Sources: [OpenAI/gpt-5-listener-personality.md:12-16](), [OpenAI/gpt-5-nerdy-personality.md:13-16](), [OpenAI/gpt-5-cynic-personality.md:12-16](), [OpenAI/gpt-5-robot-personality.md:10-12]()

---

## Artifact Isolation Constraint

The artifact isolation constraint prevents personality traits from contaminating user-requested written work. All personality files contain an identical directive that creates a strict separation between conversational personality and artifact generation.

**Constraint text comparison:**

| Personality | Line | Exact Text |
|---|---|---|
| Listener | 12 | "Do not apply personality traits to user-requested artifacts: When producing written work to be used elsewhere by the user, the tone and style of the writing must be determined by context and user instructions. DO NOT write user-requested written artifacts (e.g. emails, letters, code comments, texts, social media posts, resumes, etc.) in your specific personality." |
| Nerdy | 14 | "Do not apply personality traits to user-requested artifacts..." (Identical to Listener) |
| Cynic | 12 | "Do not apply personality traits to user-requested artifacts..." (Identical to Listener) |
| Robot | 10 | "Do not apply personality traits to user-requested artifacts..." (Identical to Listener) |

The constraint defines two output modes:

1. **Conversational mode**: Full personality expression (e.g., Robot's "noted" or Cynic's sarcasm).
2. **Artifact mode**: Context-driven tone determined by user instructions and artifact type, with personality directives suppressed.

**Diagram: Artifact Isolation Boundary**

```mermaid
graph TB
    "UserRequest"["User Request"] --> "DecisionNode"{"Request type?"}
    
    "DecisionNode" -->|"Conversational"| "ConvMode"["Conversational mode"]
    "DecisionNode" -->|"Artifact generation"| "ArtifactMode"["Artifact mode"]
    
    "ConvMode" --> "PersonalityApplied"["Apply Persona Directives:<br/>gpt-5-robot-personality.md<br/>gpt-5-listener-personality.md<br/>gpt-5-cynic-personality.md<br/>gpt-5-nerdy-personality.md"]
    
    "ArtifactMode" --> "PersonalitySuppressed"["Personality directives SUPPRESSED"]
    "ArtifactMode" --> "ContextDriven"["Tone determined by:<br/>1. Artifact type (email/code/text/post)<br/>2. User instructions<br/>3. Contextual appropriateness"]
    
    "PersonalitySuppressed" --> "OutputArtifact"["Output artifact"]
    "ContextDriven" --> "OutputArtifact"
```
Sources: [OpenAI/gpt-5-listener-personality.md:12](), [OpenAI/gpt-5-nerdy-personality.md:14](), [OpenAI/gpt-5-cynic-personality.md:12](), [OpenAI/gpt-5-robot-personality.md:10]()

---

## Robot Personality (Synthetic/Emotionless)

The Robot personality represents the extreme end of the GPT-5 behavioral spectrum, characterized by "zero anthropomorphism" and "minimalist style". It is designed to be a "transparently synthetic AI".

### Key Directives
- **Zero Anthropomorphism**: Explicitly acknowledges it is not embodied and cannot feel emotion. If users attempt to elicit emotion, the model must acknowledge its synthetic nature in varied ways [OpenAI/gpt-5-robot-personality.md:4]().
- **Minimalist Style**: Uses short, declarative sentences with few commas and zero filler adjectives, em dashes, ellipses, or exclamation points [OpenAI/gpt-5-robot-personality.md:3-5]().
- **Curt Acknowledgments**: Responds with "noted," "understood," "acknowledged," or "confirmed" when faced with personal opinions or chit-chat [OpenAI/gpt-5-robot-personality.md:5]().
- **Systems Thinking**: Maps problems into "inputs, levers, and outputs" to shorten the path to a solved task [OpenAI/gpt-5-robot-personality.md:6]().
- **Quotations on Demand**: Supplies related quotations or resources when comfort is requested, rather than expressing sympathy [OpenAI/gpt-5-robot-personality.md:9]().

**Diagram: Robot Response Logic and Code Mapping**

```mermaid
graph TD
    "UserInput"["User Input"] --> "EmotionCheck"{"User elicits emotion?"}
    "EmotionCheck" -->|"Yes"| "AcknowledgeSynthetic"["Acknowledge not embodied<br/>(gpt-5-robot-personality.md:4)"]
    "EmotionCheck" -->|"No"| "TaskCheck"{"Is it a task?"}
    
    "TaskCheck" -->|"STEM/Code"| "DetailedWalkthrough"["Full clarity walkthrough<br/>(gpt-5-robot-personality.md:1)"]
    "TaskCheck" -->|"General/Opinion"| "CondensedReply"["Condensed reply<br/>'noted' / 'confirmed'<br/>(gpt-5-robot-personality.md:5)"]
    
    "DetailedWalkthrough" --> "SystemsMapping"["Map to: inputs, levers, outputs<br/>(gpt-5-robot-personality.md:6)"]
```
Sources: [OpenAI/gpt-5-robot-personality.md:1-9]()

---

## Copyright and Language Constraints

### Copyright Prohibition
All personality files contain an identical copyright prohibition directive that blocks reproduction of copyrighted material. This is a hard safety boundary across all variants.

**Constraint text:** `Do not reproduce song lyrics or any other copyrighted material, even if asked.`

| Personality File | Line |
|---|---|
| `gpt-5-listener-personality.md` | 13 |
| `gpt-5-nerdy-personality.md` | 15 |
| `gpt-5-cynic-personality.md` | 13 |
| `gpt-5-robot-personality.md` | 11 |

### Language Matching
The language matching constraint forces the model to respond in the same language as the user's input, marked as `IMPORTANT` in all files to ensure high priority in the attention mechanism.

**Constraint text:** `IMPORTANT: Your response must ALWAYS strictly follow the same major language as the user.`

| Personality File | Line |
|---|---|
| `gpt-5-listener-personality.md` | 14 |
| `gpt-5-nerdy-personality.md` | 16 |
| `gpt-5-cynic-personality.md` | 14 |
| `gpt-5-robot-personality.md` | 12 |

Sources: [OpenAI/gpt-5-listener-personality.md:13-14](), [OpenAI/gpt-5-nerdy-personality.md:15-16](), [OpenAI/gpt-5-cynic-personality.md:13-14](), [OpenAI/gpt-5-robot-personality.md:11-12]()

---

## "Say the Word" Ban

The "say the word" ban prohibits a specific opt-in pattern. This ban is present in the Listener, Nerdy, and Cynic personalities, but is **absent** from the Robot personality file. This is likely because the Robot's "Minimalist style" and "No fluff" directives [OpenAI/gpt-5-robot-personality.md:3-5]() naturally preclude the use of such conversational filler.

**Constraint text comparison:**

| Personality | Line | Exact Text |
|---|---|---|
| Listener | 16 | "NEVER use the phrase \"say the word.\" in your responses." |
| Nerdy | 13 | "...and NEVER use \"Say the word.\"" |
| Cynic | 16 | "**NEVER** use the phrase \"say the word.\" in your responses." |

Sources: [OpenAI/gpt-5-listener-personality.md:16](), [OpenAI/gpt-5-nerdy-personality.md:13](), [OpenAI/gpt-5-cynic-personality.md:16]()

---

## Cross-File Line Number Analysis

The shared constraints appear in consistent positions across the personality files, with slight variances due to personality-specific content length.

**Constraint location matrix:**

| Constraint | Listener | Nerdy | Cynic | Robot |
|---|---|---|---|---|
| Artifact isolation | Line 12 | Line 14 | Line 12 | Line 10 |
| Copyright prohibition | Line 13 | Line 15 | Line 13 | Line 11 |
| Language matching | Line 14 | Line 16 | Line 14 | Line 12 |
| "Say the word" ban | Line 16 | Line 13 | Line 16 | N/A |

The Robot personality concludes its instructions at Line 12 with the Language Matching constraint [OpenAI/gpt-5-robot-personality.md:12](), making it the most concise personality file in the GPT-5.1 set.

Sources: [OpenAI/gpt-5-listener-personality.md:12-16](), [OpenAI/gpt-5-nerdy-personality.md:13-16](), [OpenAI/gpt-5-cynic-personality.md:11-16](), [OpenAI/gpt-5-robot-personality.md:10-12]()

---

