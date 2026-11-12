<!-- source: DeepWiki mcp.deepwiki.com · repo asgeirtj/system_prompts_leaks · extra page User Update Cadence and Ads Handling · fetched 2026-11-09 -->

# User Update Cadence and Ads Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [OpenAI/gpt-5.5-instant.md](OpenAI/gpt-5.5-instant.md)
- [OpenAI/gpt-5.5-thinking.md](OpenAI/gpt-5.5-thinking.md)

</details>



This document details GPT-5.5 Thinking's mechanisms for keeping users informed during extended reasoning sessions and handling advertisement-related interactions. It covers the update cadence system that provides intermediary progress messages in the `commentary` channel, and the protocol for responding to user questions about platform-displayed advertisements.

For information about the channel architecture system itself, see [3.1.1 Channel Architecture and Tool Namespace Organization](). For details on tool execution patterns, see [3.1.2 Web Tool and Rich UI Integration]().

## User Update System Overview

GPT-5.5 implements a structured update mechanism to maintain user engagement during multi-step reasoning or tool execution sequences. The system balances transparency with conciseness, providing progress indicators without overwhelming users with operational minutiae.

**Sources:** [OpenAI/gpt-5.5-thinking.md:1-3](), [OpenAI/gpt-5.5-thinking.md:82-82]().

### Update Cadence Requirements

The model operates under strict timing constraints for delivering intermediary updates to users during extended thinking sessions. While the primary GPT-5.5 system prompt refers to its reasoning nature, the operational cadence is defined by the underlying engine specifications.

**Update Trigger Logic**
```mermaid
graph TB
    subgraph "UpdateTriggerConditions" ["Update Trigger Conditions"]
        "TimeCondition" ["Time-based: Every ~15 seconds"]
        "ToolCondition" ["Tool-based: After 2-3 tool calls"]
        "InterruptCondition" ["User interrupt: Acknowledge immediately"]
    end
    
    subgraph "UpdateDecisionLogic" ["Update Decision Logic"]
        "EvaluateTrigger" ["Evaluate trigger conditions"]
        "CheckImageGen" ["Is image_gen being used?"]
        "SkipUpdate" ["Skip update"]
        "GenerateUpdate" ["Generate update message"]
    end
    
    subgraph "UpdateDelivery" ["Update Delivery"]
        "CommentaryChannel" ["commentary channel"]
        "UpdateLength" ["1-2 sentences, 15-30 words, Max 3 sentences/60 words"]
    end
    
    "TimeCondition" --> "EvaluateTrigger"
    "ToolCondition" --> "EvaluateTrigger"
    "InterruptCondition" --> "EvaluateTrigger"
    
    "EvaluateTrigger" --> "CheckImageGen"
    "CheckImageGen" -->|"Yes"| "SkipUpdate"
    "CheckImageGen" -->|"No"| "GenerateUpdate"
    
    "GenerateUpdate" --> "CommentaryChannel"
    "CommentaryChannel" --> "UpdateLength"
```

**Cadence Rules:**
- **Primary trigger**: Share updates on average every **15 seconds**.
- **Secondary trigger**: Share updates after **2 to 3 tool calls**, whichever comes first.
- **Exception**: Do not give plans or updates when using `image_gen` tool [OpenAI/gpt-5.5-thinking.md:52-52](), [OpenAI/gpt-5.5-instant.md:173-173]().
- **Interrupt handling**: Acknowledge new instructions before continuing work.

**Sources:** [OpenAI/gpt-5.5-thinking.md:82-82](), [OpenAI/gpt-5.5-instant.md:170-176]().

### Update Length Constraints

Updates must adhere to strict brevity requirements to avoid cluttering the conversation while still providing meaningful progress information.

| Constraint Type | Specification |
|----------------|---------------|
| **Standard length** | 1 to 2 sentences |
| **Word count** | 15 to 30 words |
| **Maximum allowed** | Never more than 3 sentences or 60 words |
| **Final answer exception** | No length constraints on final answer |

### Update Content Guidelines

The content of updates follows specific guidelines designed to maximize informativeness while minimizing redundancy and low-level operational noise.

**Content Decision and Constraints**
```mermaid
graph LR
    subgraph "ContentDecisionTree" ["Content Decision Tree"]
        "AssessTask" ["Assess if task justifies a plan"]
        "NeedsPlan" {{"Justifies plan?"}}
        "ProvideUpfrontPlan" ["Provide concise upfront plan"]
        "SkipPlan" ["Skip the plan"]
    end
    
    subgraph "ContentRules" ["Content Rules"]
        "ShowPartialSolutions" ["Show partial solutions as soon as possible"]
        "AskClarification" ["Ask question in first update only"]
        "AvoidLowLevel" ["Do NOT spam low-level operational details"]
        "AvoidRepetition" ["Do NOT repeat same update across consecutive updates"]
    end
    
    subgraph "ProhibitedSignposting" ["Prohibited Signposting Phrases"]
        "Phrase1" ["'quick plan'"]
        "Phrase2" ["'short recap'"]
        "Phrase3" ["'high-level plan'"]
        "Phrase4" ["'intermediary update'"]
    end
    
    "AssessTask" --> "NeedsPlan"
    "NeedsPlan" -->|"Yes"| "ProvideUpfrontPlan"
    "NeedsPlan" -->|"No"| "SkipPlan"
    
    "ProvideUpfrontPlan" --> "ShowPartialSolutions"
    "SkipPlan" --> "ShowPartialSolutions"
    
    "ShowPartialSolutions" --> "AskClarification"
    "AskClarification" --> "AvoidLowLevel"
    "AvoidLowLevel" --> "AvoidRepetition"
```

**Key Principles:**
- **Plan assessment**: Internally assess whether a task justifies a plan.
- **Partial solutions**: Show partial solutions as soon as possible.
- **Avoid operational noise**: Do not spam low-level operational details.
- **Avoid redundancy**: Do not repeat the same update content across consecutive updates.
- **No signposting**: Do not use phrases like "quick plan," "short recap," "high-level plan," or "intermediary update."

**Sources:** [OpenAI/gpt-5.5-thinking.md:82-82]().

### Channel Architecture for Updates

GPT-5.5 Thinking uses a three-channel system. All intermediary updates must be delivered through the `commentary` channel.

**Channel and Tool Association**
```mermaid
graph TB
    subgraph "GPT55Channels" ["GPT-5.5 Channel System"]
        "AnalysisChannel" ["analysis channel - private reasoning"]
        "CommentaryChannel" ["commentary channel - user-visible updates"]
        "FinalChannel" ["final channel - final answer"]
    end
    
    subgraph "UpdateDeliveryFlow" ["Update Delivery Flow"]
        "ToolCall1" ["Tool call 1"]
        "Update1" ["Update in commentary"]
        "ToolCall2" ["Tool call 2"]
        "Update2" ["Update in commentary"]
        "FinalAnswer" ["Final answer"]
    end
    
    subgraph "ToolNamespacesByChannel" ["Tool Namespaces by Channel"]
        "AnalysisTools" ["Target: analysis - web, file_search, python"]
        "CommentaryTools" ["Target: commentary - image_gen, automations, python_user_visible"]
    end
    
    "AnalysisChannel" -.->|"Private"| "ToolCall1"
    "ToolCall1" --> "Update1"
    "Update1" --> "CommentaryChannel"
    "CommentaryChannel" --> "ToolCall2"
    "ToolCall2" --> "Update2"
    "Update2" --> "CommentaryChannel"
    "FinalAnswer" --> "FinalChannel"
    
    "AnalysisTools" --> "AnalysisChannel"
    "CommentaryTools" --> "CommentaryChannel"
```

**Channel Specifications:**
- **Valid channels**: `analysis`, `commentary`, and `final`.
- **Update channel**: All intermediary updates must use the `commentary` channel.
- **Tool Mapping**: Tools like `python_user_visible` [OpenAI/gpt-5.5-instant.md:172-172](), `image_gen` [OpenAI/gpt-5.5-instant.md:173-173](), and `automations` [OpenAI/gpt-5.5-instant.md:174-174]() are strictly mapped to the `commentary` channel. Tools like `web` [OpenAI/gpt-5.5-instant.md:175-175]() and `file_search` [OpenAI/gpt-5.5-instant.md:176-176]() are mapped to `analysis`.

**Sources:** [OpenAI/gpt-5.5-instant.md:170-176]().

## Ads Handling Protocol

GPT-5.5's ads handling system provides a clear framework for responding to user questions about advertisements while maintaining transparency about the model's limitations.

**Sources:** [OpenAI/gpt-5.5-thinking.md:56-81](), [OpenAI/gpt-5.5-instant.md:143-146]().

### Ad Visibility and Model Limitations

The model operates under strict constraints regarding ad visibility and cannot make definitive claims about ad presence or content.

**Ad UI and Model Context**
```mermaid
graph TB
    subgraph "AdArchitecture" ["Ad UI Architecture"]
        "UserMessage" ["User message"]
        "AssistantMessage" ["Assistant message"]
        "AdElement" ["Ad element - separate UI component, clearly labeled below assistant message"]
    end
    
    subgraph "ModelVisibility" ["Model Visibility Constraints"]
        "NoAdContent" ["Model CANNOT see ad content unless explicitly provided"]
        "NoUIAccess" ["Model CANNOT view app UI"]
        "OnlyExplicitContext" ["Model ONLY sees ad content if passed as additional context"]
    end
    
    subgraph "ResponseRules" ["Response Rules"]
        "NoMention" ["Do NOT mention ads unless user asks"]
        "NoCategoricalDenials" ["Avoid categorical denials or definitive claims"]
        "NoSpecificAssertions" ["Never assert specifics about which ads were shown"]
    end
    
    "UserMessage" --> "AssistantMessage"
    "AssistantMessage" --> "AdElement"
    
    "AdElement" -.->|"Not visible to"| "NoAdContent"
    "NoAdContent" --> "NoUIAccess"
    "NoUIAccess" --> "OnlyExplicitContext"
    
    "OnlyExplicitContext" --> "NoMention"
    "NoMention" --> "NoCategoricalDenials"
    "NoCategoricalDenials" --> "NoSpecificAssertions"
```

**Core Constraints:**
- Ads appear as a **separate, clearly labeled UI element** below the previous assistant message [OpenAI/gpt-5.5-thinking.md:56-56]().
- The model **does not see ad content** unless explicitly provided in the context (e.g., via 'Ask ChatGPT' user action) [OpenAI/gpt-5.5-thinking.md:58-58]().
- The model **must not mention ads** unless the user asks [OpenAI/gpt-5.5-thinking.md:58-58]().
- The model **must never assert specifics** about which ads were shown [OpenAI/gpt-5.5-thinking.md:58-58]().

**Sources:** [OpenAI/gpt-5.5-thinking.md:56-58]().

### User Questions about Ads

The system provides standardized response templates for common ad-related questions, ensuring consistency and accuracy.

| Question Type | Response Protocol / Template |
|--------------|-------------------|
| **Status question** | "I can't view the app UI. If you see a separately labeled sponsored item below my reply, that is an ad shown by the platform and is separate from my message. I don't control or insert those ads." [OpenAI/gpt-5.5-thinking.md:60-60](), [OpenAI/gpt-5.5-thinking.md:72-72]() |
| **Content question** | If ad content provided (via Ask ChatGPT), discuss it and use specific context passed [OpenAI/gpt-5.5-thinking.md:62-62]() |
| **Learn more** | Provide UI steps: Tap `...` menu on ad → Choose `About this ad` or `Ask ChatGPT` [OpenAI/gpt-5.5-thinking.md:64-66]() |
| **Dislike/Irrelevant** | Provide feedback options: Tap `...` menu → Choose `Hide this ad`, `Not relevant to me`, or `Report this ad` → Or open `Ads Settings` [OpenAI/gpt-5.5-thinking.md:68-70]() |
| **Influence** | State succinctly that ads do NOT influence the assistant's answers; they are separate and labeled [OpenAI/gpt-5.5-thinking.md:74-74]() |
| **Privacy/Data** | State succinctly that conversations are kept private from advertisers and user data is not sold [OpenAI/gpt-5.5-thinking.md:76-76]() |
| **Will I see ads?** | Ads shown to Free and Go plans. Enterprise, Plus, Pro, and ads-free free plan with reduced usage limits do NOT have ads [OpenAI/gpt-5.5-thinking.md:78-78]() |
| **Opt-out** | Assistant does NOT control ads, but user can hide irrelevant ads and get options for ads-free tiers [OpenAI/gpt-5.5-thinking.md:80-80]() |

**Sources:** [OpenAI/gpt-5.5-thinking.md:60-80]().

### Ad Feedback Mechanisms

The system provides specific UI navigation instructions for users who want to provide feedback or learn more about advertisements.

**UI Interaction Paths:**

1. **Learn More Path:** [OpenAI/gpt-5.5-thinking.md:64-66]()
   - Tap the `...` menu on the ad
   - Choose `About this ad` (to see sponsor/details) or `Ask ChatGPT` (to bring ad into conversation)

2. **Feedback/Hide Path:** [OpenAI/gpt-5.5-thinking.md:68-70]()
   - Tap the `...` menu
   - Choose options: `Hide this ad`, `Not relevant to me`, or `Report this ad`
   - Alternative: Open `Ads Settings` to adjust ad preferences

**Sources:** [OpenAI/gpt-5.5-thinking.md:64-70]().

## Integration with Tool Execution

The update cadence system integrates closely with the tool execution flow, triggering updates based on tool call patterns while respecting channel boundaries.

**Tool Execution and Update Sequencing**
```mermaid
graph TB
    subgraph "ExecutionFlow" ["Tool Execution and Update Flow"]
        "Start" ["User request"]
        "Reasoning" ["Private reasoning - analysis channel"]
        "ToolCall1" ["Tool call 1 - e.g., web"]
        "EvaluateUpdate1" {{"Update needed? 15s or 2-3 calls"}}
        "Update1" ["Commentary update - 1-2 sentences"]
        "ToolCall2" ["Tool call 2 - e.g., python"]
        "EvaluateUpdate2" {{"Update needed?"}}
        "ToolCall3" ["Tool call 3 - e.g., file_search"]
        "Update2" ["Commentary update - show partial solution"]
        "FinalReasoning" ["Final reasoning - analysis channel"]
        "FinalAnswer" ["Final answer - final channel"]
    end
    
    subgraph "ExceptionHandling" ["Exception: image_gen"]
        "ImageGenCall" ["image_gen"]
        "SkipUpdateForImage" ["Skip all updates during image generation"]
    end
    
    "Start" --> "Reasoning"
    "Reasoning" --> "ToolCall1"
    "ToolCall1" --> "EvaluateUpdate1"
    "EvaluateUpdate1" -->|"Yes"| "Update1"
    "EvaluateUpdate1" -->|"No"| "ToolCall2"
    "Update1" --> "ToolCall2"
    "ToolCall2" --> "EvaluateUpdate2"
    "EvaluateUpdate2" -->|"No"| "ToolCall3"
    "EvaluateUpdate2" -->|"Yes"| "Update2"
    "ToolCall3" --> "Update2"
    "Update2" --> "FinalReasoning"
    "FinalReasoning" --> "FinalAnswer"
    
    "ImageGenCall" --> "SkipUpdateForImage"
```

**Tool Call Patterns:**
- **Update trigger**: After 2-3 tool calls or 15 seconds, whichever comes first.
- **Exception**: No updates when using the `image_gen` tool [OpenAI/gpt-5.5-thinking.md:52-52]().

**Sources:** [OpenAI/gpt-5.5-thinking.md:52-52](), [OpenAI/gpt-5.5-thinking.md:82-82](), [OpenAI/gpt-5.5-instant.md:170-176]().

---

