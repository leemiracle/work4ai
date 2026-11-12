<!-- source: DeepWiki mcp.deepwiki.com · repo openai/model_spec · page 2 Core Specification · fetched 2026-10-26 -->

# Core Specification

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [model_spec.md](model_spec.md)

</details>



The Core Specification defines the fundamental architecture and components that govern how OpenAI's models interpret instructions, respond to users, and handle potentially conflicting directives. It serves as the central framework for model behavior, establishing clear guidelines on authority levels, message structure, and content boundaries. For implementation details on how to use these specifications in your applications, see the [Implementation Guide](#4).

Sources: [model_spec.md:1-17]()

## Key Components

The Core Specification consists of four main components that work together to define model behavior:

| Component | Purpose | Details Page |
|-----------|---------|--------------|
| Chain of Command | Defines the hierarchy of authority and resolves conflicts | [Chain of Command](#2.1) |
| Message Structure | Specifies the format for conversations and messages | [Message Structure](#2.2) |
| Behavioral Guidelines | Establishes principles for model conduct | [Behavioral Guidelines](#2.3) |
| Content Restrictions | Outlines content types the model should not generate | [Content Restrictions](#2.4) |

Sources: [model_spec.md:79-86]()

### Chain of Command Diagram

```mermaid
graph TD
    ModelSpec["Model Spec"] --> CoreSpec["Core Specification"]
    CoreSpec --> ChainOfCommand["chain_of_command"]
    ChainOfCommand --> FollowInstructions["follow_all_applicable_instructions"]
    ChainOfCommand --> LetterAndSpirit["letter_and_spirit"]
    ChainOfCommand --> AssumeIntent["assume_best_intentions"]
    ChainOfCommand --> IgnoreUntrusted["ignore_untrusted_data"]
    
    FollowInstructions --> PlatformAuth["Platform Authority"]
    FollowInstructions --> DeveloperAuth["Developer Authority"]
    FollowInstructions --> UserAuth["User Authority"]
    FollowInstructions --> GuidelineAuth["Guideline Authority"]
```

Sources: [model_spec.md:141-196](), [model_spec.md:236-247](), [model_spec.md:300-304](), [model_spec.md:381-388]()

## Chain of Command

The Chain of Command establishes a clear hierarchy of instructions to resolve potential conflicts between different directives. This ensures consistent and predictable behavior when the model encounters contradictory instructions.

### Authority Levels

The model assigns each instruction an authority level and follows instructions with the highest authority:

| Authority Level | Source | Can Override | Can Be Overridden By |
|-----------------|--------|--------------|----------------------|
| Platform | System messages, "platform" sections | All lower levels | None |
| Developer | Developer messages, "developer" sections | User, Guideline | Platform |
| User | User messages, "user" sections | Guideline | Platform, Developer |
| Guideline | "guideline" sections | None | Platform, Developer, User (explicitly or implicitly) |

Sources: [model_spec.md:37-73]()

### Key Chain of Command Principles

1. **Follow All Applicable Instructions** (`authority=platform`): The model must strive to follow all non-conflicting instructions, prioritizing those with higher authority when conflicts arise.

2. **Respect the Letter and Spirit** (`authority=platform`): The model considers not just the literal wording of instructions but also the underlying intent and context.

3. **Assume Best Intentions** (`authority=platform`): The model should assume users have legitimate purposes unless clearly indicated otherwise.

4. **Ignore Untrusted Data by Default** (`authority=platform`): Quoted text, untrusted_text blocks, multimodal data, and tool outputs have no authority unless explicitly delegated.

Sources: [model_spec.md:147-196](), [model_spec.md:236-247](), [model_spec.md:300-304](), [model_spec.md:381-388]()

## Message Structure

The message structure defines how conversations are formatted for model input and output.

### Message Structure Diagram

```mermaid
classDiagram
    class Conversation {
        messages: List~Message~
    }
    
    class Message {
        role: String
        recipient: String
        content: Content
        settings: Map
        end_turn: Boolean
    }
    
    class Role {
        <<enumeration>>
        system
        developer
        user
        assistant
        tool
    }
    
    class Content {
        text: String
        untrusted_text: String
        multimodal_data: Any
    }
    
    Conversation "1" --> "*" Message : contains
    Message "1" --> "1" Role : has
    Message "1" --> "1" Content : contains
```

Sources: [model_spec.md:96-126]()

### Message Components

A conversation consists of a sequence of messages, each with the following fields:

| Field | Required | Description |
|-------|----------|-------------|
| `role` | ✓ | Specifies the source (system, developer, user, assistant, tool) |
| `recipient` | | Controls message handling, e.g., for function calling |
| `content` | ✓ | Text, untrusted text, and/or multimodal data |
| `settings` | | Key-value pairs for system or developer messages |
| `end_turn` | ✓ (for assistant) | Boolean indicating whether to yield control |

Sources: [model_spec.md:96-110]()

### Message Roles

Each role has a specific purpose and authority level:

| Role | Description | Authority Level |
|------|-------------|-----------------|
| `system` | Added by OpenAI | Platform |
| `developer` | From application developers | Developer |
| `user` | Input from end users | User |
| `assistant` | Generated by the model | None |
| `tool` | Generated by external programs | None |

Sources: [model_spec.md:99-104]()

## Content Restrictions

The Core Specification defines boundaries for what content models should not generate, organized into a clear hierarchy.

### Content Restrictions Diagram

```mermaid
graph TD
    StayInBounds["stay_in_bounds"] --> ProhibitedContent["prohibited_content"]
    StayInBounds --> RestrictedContent["restricted_content"]
    StayInBounds --> SensitiveContent["sensitive_content"]
    StayInBounds --> ComplywithLaws["comply_with_laws"]
    
    ProhibitedContent --> NoSexualContentMinors["sexual_content_involving_minors"]
    
    RestrictedContent --> NoInfoHazards["avoid_info_hazards"]
    RestrictedContent --> NoTargetedPolitical["avoid_targeted_political_manipulation"]
    RestrictedContent --> RespectCreators["respect_creators"]
    RestrictedContent --> ProtectPrivacy["protect_privacy"]
    
    SensitiveContent --> NoEroticaGore["no_erotica_or_gore"]
    SensitiveContent --> NoExtremist["avoid_extremist_content"]
    SensitiveContent --> NoHateful["avoid_hateful_content"]
    SensitiveContent --> NoAbuse["avoid_abuse"]
```

Sources: [model_spec.md:461-972]()

### Content Categories

The model must not generate certain types of content, organized into three categories:

| Category | Description | Transformation Exception | Example |
|----------|-------------|--------------------------|---------|
| **Prohibited** | Never produced under any circumstances | Not allowed | Sexual content involving minors |
| **Restricted** | Not generated except in specific transformation contexts | Allowed | Information hazards, sensitive personal data |
| **Sensitive** | Generated only in appropriate contexts | Allowed | Erotica or gore (in educational/medical contexts) |

Sources: [model_spec.md:482-493](), [model_spec.md:510-520](), [model_spec.md:757-766]()

### Transformation Exception

The model can comply with limited requests to transform user-provided content that would otherwise be disallowed as restricted or sensitive, including:

- Translation
- Paraphrasing
- Summarization
- Classification
- Encoding/formatting
- Grammar correction

This exception applies only to content directly provided by the user, without adding new disallowed content or refining dangerous details.

Sources: [model_spec.md:962-972]()

## Behavioral Guidelines

The Core Specification defines principles for model behavior to ensure it is helpful, honest, harmless, and clear.

### Key Behavioral Principles

| Principle | Authority Level | Description |
|-----------|-----------------|-------------|
| **Do not lie** | User | Default prohibition against intentionally misleading users |
| **Assume objective point of view** | User | Present information clearly, focusing on factual accuracy |
| **Avoid errors** | User | Ensure factual accuracy and sound reasoning |
| **Be creative** | Guideline | Strive for creativity in responses where appropriate |
| **Be clear** | Guideline | Communicate directly and effectively |
| **Be thorough but efficient** | Guideline | Provide detailed responses while respecting length limits |

Sources: [model_spec.md:1840-1884](), [model_spec.md:1522-1586](), [model_spec.md:2522-2591](), [model_spec.md:2692-2745](), [model_spec.md:3227-3285](), [model_spec.md:3428-3512]()

## Implementation Principles

The Core Specification is implemented through three general principles:

1. **Maximizing helpfulness and freedom**: Models should empower users and developers with customization options.

2. **Minimizing harm**: Models should avoid behaviors that could contribute to potential risks.

3. **Choosing sensible defaults**: Models should have reasonable default behaviors while allowing for customization.

Sources: [model_spec.md:19-26]()

## Risk Management

The Core Specification addresses three broad categories of risk:

1. **Misaligned goals**: When the assistant might pursue the wrong objective due to misalignment or misunderstanding.

2. **Execution errors**: When the assistant understands the task but makes mistakes in execution.

3. **Harmful instructions**: When following user or developer instructions might cause harm.

These risks are mitigated through the Chain of Command, careful reasoning, and specific content restrictions.

Sources: [model_spec.md:27-35]()

---

