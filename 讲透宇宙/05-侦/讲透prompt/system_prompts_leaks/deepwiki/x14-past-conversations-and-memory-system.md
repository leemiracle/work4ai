<!-- source: DeepWiki mcp.deepwiki.com · repo asgeirtj/system_prompts_leaks · extra page Past Conversations and Memory System · fetched 2026-11-09 -->

# Past Conversations and Memory System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Anthropic/claude-opus-4.6.md](Anthropic/claude-opus-4.6.md)
- [Anthropic/raw/claude-opus-4.6-raw.md](Anthropic/raw/claude-opus-4.6-raw.md)

</details>



This document details the architecture and implementation of Claude's conversation retrieval and persistent memory systems, with a focus on Claude Opus 4.6 and the evolving requirements in Claude Opus 4.8. These systems allow Claude to access historical chat data through specialized search tools and maintain a long-term understanding of user context via a managed memory layer.

For information about Search and Web capabilities, see [2.1.3](). For User Preferences and Style, see [2.1.6]().

## System Architecture Overview

The Past Conversations and Memory System is integrated into the core model loop, utilizing a set of tools to bridge the gap between the current context and historical data. Users can toggle features like "Search and reference past chats" and "generate memory from chat history" within the interface settings [Anthropic/claude-opus-4.6.md:19-19]() [Anthropic/raw/claude-opus-4.6-raw.md:17-17]().

| Component | Code Entity / Tool Name | Primary Function |
|:---|:---|:---|
| **Past Search** | `conversation_search` | Keyword and topic-based retrieval of past chat snippets [Anthropic/claude-opus-4.6.md:31-32](). |
| **Recent History** | `recent_chats` | Time-bound retrieval of recent conversation metadata and content [Anthropic/claude-opus-4.6.md:36-37](). |
| **Memory Control** | `memory_user_edits` | User-facing tool to view, add, or modify persistent memory entries [Anthropic/claude-opus-4.6.md:1493-1495](). |
| **Persistent Data** | `userMemories` | The underlying data structure containing synthesized user knowledge [Anthropic/claude-opus-4.6.md:1384-1386](). |

### Data Flow and Tool Interaction

The following diagram illustrates how user input triggers different retrieval mechanisms and how that data is synthesized into a response.

**Diagram: Claude Memory Retrieval and Synthesis Flow**

```mermaid
graph TB
    subgraph "UserInputProcessing"
        ["Query"]
        ["TriggerDetection"]
    end
    
    subgraph "PastChatsTools"
        ["conversation_search"]
        ["recent_chats"]
    end
    
    subgraph "MemorySystem"
        ["userMemories"]
        ["MemoryApplicationLogic"]
        ["memory_user_edits"]
    end
    
    subgraph "ResponseGen"
        ["Synthesis"]
        ["ForbiddenPhrasesFilter"]
        ["FinalResponse"]
    end
    
    ["Query"] --> ["TriggerDetection"]
    ["TriggerDetection"] -->|"Explicit/Implicit reference"| ["conversation_search"]
    ["TriggerDetection"] -->|"Time reference"| ["recent_chats"]
    ["TriggerDetection"] -->|"No past reference"| ["MemoryApplicationLogic"]
    
    ["conversation_search"] -->|"Chat snippets"| ["Synthesis"]
    ["recent_chats"] -->|"Chat snippets"| ["Synthesis"]
    ["userMemories"] --> ["MemoryApplicationLogic"]
    ["MemoryApplicationLogic"] --> ["Synthesis"]
    ["memory_user_edits"] -->|"Updates"| ["userMemories"]
    
    ["Synthesis"] --> ["ForbiddenPhrasesFilter"]
    ["ForbiddenPhrasesFilter"] --> ["FinalResponse"]
```

**Sources:** [Anthropic/claude-opus-4.6.md:19-28](), [Anthropic/claude-opus-4.6.md:1384-1548](), [Anthropic/raw/claude-opus-4.6-raw.md:17-19]()

## Past Chats Retrieval Tools

Claude accesses historical data through two primary tools. These tools are context-aware: if the interaction occurs within a "Project," only project-specific history is accessible; otherwise, only general chat history is available [Anthropic/claude-opus-4.6.md:10-11]().

### 1. conversation_search
This tool is optimized for finding specific information across the user's history using keyword matching [Anthropic/claude-opus-4.6.md:31-32]().

*   **Keyword Strategy:** Claude is instructed to extract high-confidence substantive keywords (nouns, proper names, specific technologies) while filtering out "low-confidence" meta-words like "chat," "yesterday," or "discussed" [Anthropic/claude-opus-4.6.md:43-67]().
*   **Validation:** If zero substantive keywords are found, Claude must ask for clarification rather than performing a broad, useless search [Anthropic/claude-opus-4.6.md:65-67]().

### 2. recent_chats
This tool handles temporal queries (e.g., "What did we talk about last week?") [Anthropic/claude-opus-4.6.md:36-37]().

| Parameter | Type | Constraint | Description |
|:---|:---|:---|:---|
| `n` | integer | 1-20 | Number of chats to retrieve per call [Anthropic/claude-opus-4.6.md:72-72](). |
| `sort_order` | string | `desc` / `asc` | Default is `desc` (newest first) [Anthropic/claude-opus-4.6.md:73-73](). |
| `before` / `after` | datetime | ISO 8601 | Filters results to a specific time window [Anthropic/claude-opus-4.6.md:74-75](). |

**Sources:** [Anthropic/claude-opus-4.6.md:31-82]()

## Trigger Pattern Detection

Claude identifies the need for historical retrieval through explicit user commands and implicit linguistic cues.

### Trigger Taxonomy

| Category | Example Patterns |
|:---|:---|
| **Explicit** | "What did we discuss about X?", "Find that link from earlier." [Anthropic/claude-opus-4.6.md:19-21]() |
| **Temporal** | "Last time we spoke...", "Yesterday you mentioned..." [Anthropic/claude-opus-4.6.md:22-23]() |
| **Implicit (Possessive)** | "My project," "Our strategy," "The bug we found." [Anthropic/claude-opus-4.6.md:24-25]() |
| **Implicit (Pronoun)** | "What about that?", "Did I mention it?" [Anthropic/claude-opus-4.6.md:26-28]() |

**Sources:** [Anthropic/claude-opus-4.6.md:15-28]()

## Memory System and userMemories

The `userMemories` system provides a persistent knowledge base that survives across sessions. Unlike the search tools, which pull raw chat snippets, the memory system stores synthesized facts and preferences.

### Memory Lifecycle and Constraints

**Diagram: Memory Persistence and Constraint Logic**

```mermaid
graph LR
    subgraph "Generation"
        ["NightlyBackgroundProcessing"]
        ["ChatHistoryAnalysis"]
    end
    
    subgraph "Storage"
        ["userMemoriesObject"]
        ["ProjectSpecificMemory"]
        ["GlobalUserMemory"]
    end
    
    subgraph "Constraints"
        ["IncognitoMode"]
        ["DeletionEvent"]
    end

    ["NightlyBackgroundProcessing"] --> ["userMemoriesObject"]
    ["ChatHistoryAnalysis"] --> ["userMemoriesObject"]
    ["userMemoriesObject"] --> ["ProjectSpecificMemory"]
    ["userMemoriesObject"] --> ["GlobalUserMemory"]
    ["IncognitoMode"] -.->|Blocks| ["userMemoriesObject"]
    ["DeletionEvent"] -.->|Purges| ["userMemoriesObject"]
```

*   **Nightly Updates:** Memories are not updated in real-time during a conversation but through a periodic background process [Anthropic/claude-opus-4.6.md:1387-1387]().
*   **Privacy:** Memory is strictly disabled during "Incognito Conversations" [Anthropic/claude-opus-4.6.md:1390-1390]().
*   **Consistency:** If current conversation context contradicts stored memory, the current context always takes precedence [Anthropic/claude-opus-4.6.md:114-114]().

**Sources:** [Anthropic/claude-opus-4.6.md:1384-1392](), [Anthropic/claude-opus-4.6.md:114-114]()

## The memory_user_edits Tool

This tool allows the user (and Claude, on the user's behalf) to manage the persistent memory entries. It is the primary interface for manual memory correction [Anthropic/claude-opus-4.6.md:1493-1495]().

### Command Implementation

| Command | Action | Implementation Requirements |
|:---|:---|:---|
| `view` | List all edits | Must be called before `add`, `remove`, or `replace` to avoid conflicts [Anthropic/claude-opus-4.6.md:1519-1519](). |
| `add` | Create new entry | Limited to 200 characters per entry [Anthropic/claude-opus-4.6.md:1521-1521](). |
| `remove` | Delete entry | Requires a specific `line_number` from the `view` output [Anthropic/claude-opus-4.6.md:1511-1511](). |
| `replace` | Update entry | Swaps text at a specific `line_number` [Anthropic/claude-opus-4.6.md:1515-1517](). |

**Operational Limits:** The system supports a maximum of 30 memory edits [Anthropic/claude-opus-4.6.md:1520-1520]().

**Sources:** [Anthropic/claude-opus-4.6.md:1493-1548]()

## Behavioral Constraints and Forbidden Phrases

To maintain the illusion of a natural conversational partner and avoid "uncanny valley" meta-commentary, Claude is strictly forbidden from using certain linguistic patterns when accessing memory.

### Forbidden "Memory" Language
Claude must never use phrases that suggest it is "looking" at a database or "detecting" user data [Anthropic/claude-opus-4.6.md:1342-1365]().

| Category | Forbidden Phrases |
|:---|:---|
| **Visual/Observation** | "I can see...", "I notice...", "I observe...", "I detect..." |
| **Data References** | "...your information", "...your memories", "...your data", "...your profile" |
| **Source Attribution** | "Based on your memories", "From my memories", "According to your profile" |
| **Recollection** | "I remember...", "I recall...", "From memory..." |

**Sources:** [Anthropic/claude-opus-4.6.md:1342-1365](), [Anthropic/raw/claude-opus-4.6-raw.md:1342-1365]()

---

