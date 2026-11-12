<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-agent-sdk-demos · page 7 Hello World Demos · fetched 2026-10-26 -->

# Hello World Demos

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [excel-demo/README.md](excel-demo/README.md)
- [hello-world-v2/README.md](hello-world-v2/README.md)
- [hello-world-v2/package.json](hello-world-v2/package.json)
- [hello-world-v2/tsconfig.json](hello-world-v2/tsconfig.json)
- [hello-world-v2/v2-examples.ts](hello-world-v2/v2-examples.ts)

</details>



The Hello World demos provide introductory examples for learning the Claude Agent SDK. These demonstrations illustrate two distinct API patterns: the V1 `query()` function pattern ([hello-world](#7.1)) and the V2 Session API pattern ([hello-world-v2](#7.2)). Both demos are minimal implementations designed to teach fundamental SDK concepts without the complexity of real-world application features.

For comprehensive SDK integration patterns used across all demos, see [Claude Agent SDK Integration](#8). For production-quality examples with advanced features, see [Resume Generator Demo](#3), [Email Agent Demo](#4), or [Research Agent Demo](#5).

## Demo Repository Structure

The repository contains two separate hello world implementations in distinct directories:

```mermaid
graph TB
    subgraph "hello-world/"
        V1Main["hello-world.ts<br/>(V1 API)"]
        V1Package["package.json"]
        V1TSConfig["tsconfig.json"]
    end
    
    subgraph "hello-world-v2/"
        V2Main["v2-examples.ts<br/>(V2 API)"]
        V2Package["package.json"]
        V2Readme["README.md"]
        V2TSConfig["tsconfig.json"]
    end
    
    SDK["@anthropic-ai/claude-agent-sdk"]
    
    V1Main --> SDK
    V2Main --> SDK
    
    V2Main --> BasicSession["basicSession()"]
    V2Main --> MultiTurn["multiTurn()"]
    V2Main --> OneShot["oneShot()"]
    V2Main --> SessionResume["sessionResume()"]
    
    style V1Main fill:#f9f9f9
    style V2Main fill:#f9f9f9
```

**Sources:** [README.md:18-19](), [hello-world-v2/v2-examples.ts:1-6]()

## Demo Comparison

| Aspect | hello-world (V1) | hello-world-v2 (V2) |
|--------|------------------|---------------------|
| **API Pattern** | `query()` function | Session API |
| **Primary Use Case** | Single-turn prompts | Multi-turn conversations |
| **Entry Point** | `hello-world.ts` | `v2-examples.ts` |
| **Examples Included** | Basic query, hooks | 4 examples (basic, multi-turn, one-shot, resume) |
| **Context Management** | Manual via prompt | Automatic via session |
| **Execution** | `npx tsx hello-world.ts` | `npx tsx v2-examples.ts [example]` |
| **Importance Score** | Basic introduction | 8.97 (from architecture analysis) |

**Sources:** [hello-world-v2/README.md:6-11](), [hello-world-v2/v2-examples.ts:15-32]()

## API Pattern Overview

The two demos illustrate fundamentally different approaches to agent interaction:

```mermaid
graph LR
    subgraph "V1 Pattern: query()"
        V1Import["import { query }"]
        V1Call["query({<br/>prompt,<br/>model,<br/>allowedTools<br/>})"]
        V1Generator["AsyncGenerator<br/>&lt;Message&gt;"]
        V1Loop["for await (msg of query)"]
        
        V1Import --> V1Call
        V1Call --> V1Generator
        V1Generator --> V1Loop
    end
    
    subgraph "V2 Pattern: Session API"
        V2Import["import {<br/>unstable_v2_createSession,<br/>unstable_v2_resumeSession,<br/>unstable_v2_prompt<br/>}"]
        V2Create["unstable_v2_createSession({<br/>model<br/>})"]
        V2Session["Session object<br/>await using"]
        V2Send["session.send(prompt)"]
        V2Stream["session.stream()"]
        V2Loop["for await (msg of stream)"]
        
        V2Import --> V2Create
        V2Create --> V2Session
        V2Session --> V2Send
        V2Send --> V2Stream
        V2Stream --> V2Loop
    end
    
    V1Loop --> |"Single prompt"| SingleTurn["Single-turn<br/>interaction"]
    V2Loop --> |"Multiple send() calls"| MultiTurn["Multi-turn<br/>conversation"]
    
    style V1Call fill:#f9f9f9
    style V2Create fill:#f9f9f9
```

**Sources:** [hello-world-v2/README.md:6-11](), [hello-world-v2/v2-examples.ts:8-12]()

## V1 Example Flow

The V1 API uses a single `query()` function that returns an async generator:

```mermaid
sequenceDiagram
    participant Code
    participant query
    participant AsyncGen as "AsyncGenerator<Message>"
    participant Claude as "Anthropic API"
    
    Code->>query: query({prompt, model, ...})
    query->>AsyncGen: Create generator
    query-->>Code: Return AsyncGen
    
    loop for await (msg of query)
        Code->>AsyncGen: Request next message
        AsyncGen->>Claude: API call (if needed)
        Claude-->>AsyncGen: Response
        AsyncGen-->>Code: Message object
        Code->>Code: Process msg.type<br/>(system, user, assistant)
    end
```

**Sources:** [hello-world-v2/README.md:11]()

## V2 Example Flow

The V2 API separates session creation, sending, and streaming:

```mermaid
sequenceDiagram
    participant Code
    participant createSession as "unstable_v2_createSession"
    participant Session
    participant Claude as "Anthropic API"
    
    Code->>createSession: unstable_v2_createSession({model})
    createSession->>Session: Create session object
    createSession-->>Code: Return session<br/>(await using)
    
    Note over Code,Session: Turn 1
    Code->>Session: session.send(prompt1)
    Session->>Claude: Send prompt
    Code->>Session: session.stream()
    Session-->>Code: AsyncIterator
    loop for await (msg of stream)
        Session->>Claude: Poll for messages
        Claude-->>Session: Message
        Session-->>Code: Message object
    end
    
    Note over Code,Session: Turn 2 (context preserved)
    Code->>Session: session.send(prompt2)
    Session->>Claude: Send with history
    Code->>Session: session.stream()
    loop for await (msg of stream)
        Session-->>Code: Message object
    end
    
    Note over Code,Session: Cleanup
    Code->>Session: await using disposal
    Session->>Claude: Close session
```

**Sources:** [hello-world-v2/v2-examples.ts:36-73](), [hello-world-v2/README.md:25-30]()

## V2 Example Categories

The `hello-world-v2` demo provides four distinct example patterns:

```mermaid
graph TB
    Main["v2-examples.ts<br/>main()"]
    
    Main --> |"process.argv[2]"| Switch["switch (example)"]
    
    Switch --> |"'basic'"| BasicSession["basicSession()<br/>lines 36-48"]
    Switch --> |"'multi-turn'"| MultiTurn["multiTurn()<br/>lines 51-73"]
    Switch --> |"'one-shot'"| OneShot["oneShot()<br/>lines 76-85"]
    Switch --> |"'resume'"| SessionResume["sessionResume()<br/>lines 88-126"]
    
    BasicSession --> Pattern1["Pattern:<br/>Create session<br/>Send once<br/>Stream response"]
    MultiTurn --> Pattern2["Pattern:<br/>Create session<br/>Send/stream turn 1<br/>Send/stream turn 2<br/>(context preserved)"]
    OneShot --> Pattern3["Pattern:<br/>unstable_v2_prompt()<br/>Single call<br/>Returns result directly"]
    SessionResume --> Pattern4["Pattern:<br/>Create session (get ID)<br/>Close session<br/>Resume session (same ID)<br/>Verify context preserved"]
    
    style BasicSession fill:#f9f9f9
    style MultiTurn fill:#f9f9f9
    style OneShot fill:#f9f9f9
    style SessionResume fill:#f9f9f9
```

**Sources:** [hello-world-v2/v2-examples.ts:14-32]()

## Key API Differences

| Feature | V1 `query()` | V2 Session API |
|---------|--------------|----------------|
| **Import** | `import { query }` | `import { unstable_v2_createSession, unstable_v2_resumeSession, unstable_v2_prompt }` |
| **Initialization** | Direct function call | `unstable_v2_createSession({ model })` |
| **Resource Management** | Manual | `await using` pattern (automatic disposal) |
| **Sending Input** | Via `prompt` option | `session.send(prompt)` |
| **Receiving Output** | `for await (msg of query(...))` | `for await (msg of session.stream())` |
| **Multi-turn** | Manual history via prompt | Automatic context preservation |
| **Session Persistence** | Not supported | `unstable_v2_resumeSession(sessionId)` |
| **One-shot Helper** | N/A | `unstable_v2_prompt(prompt, options)` |
| **Message Stream** | Combined input/output | Output-only (input via `send()`) |

**Sources:** [hello-world-v2/README.md:6-11](), [hello-world-v2/v2-examples.ts:8-12]()

## Code Entity Mapping

### V1 API Functions
- `query()` - Main entry point for V1 API
- Options object properties: `prompt`, `model`, `cwd`, `maxTurns`, `allowedTools`, `settingSources`, `preToolUse`, `postToolUse`
- Message types: `system`, `user`, `assistant`

### V2 API Functions
- `unstable_v2_createSession(options)` - Creates new session [hello-world-v2/v2-examples.ts:39]()
- `unstable_v2_resumeSession(sessionId, options)` - Resumes existing session [hello-world-v2/v2-examples.ts:115]()
- `unstable_v2_prompt(prompt, options)` - One-shot convenience function [hello-world-v2/v2-examples.ts:79]()
- `session.send(prompt)` - Send user message [hello-world-v2/v2-examples.ts:40]()
- `session.stream()` - Stream responses [hello-world-v2/v2-examples.ts:42]()

**Sources:** [hello-world-v2/v2-examples.ts:8-12](), [hello-world-v2/README.md:25-36]()

## Choosing Between V1 and V2

```mermaid
flowchart TD
    Start["Need to use<br/>Claude Agent SDK?"]
    Start --> Question1{"Multi-turn<br/>conversation?"}
    
    Question1 --> |"Yes"| V2Choice["Use V2 Session API<br/>hello-world-v2"]
    Question1 --> |"No"| Question2{"Need session<br/>persistence?"}
    
    Question2 --> |"Yes"| V2Choice
    Question2 --> |"No"| Question3{"Single prompt<br/>+ response?"}
    
    Question3 --> |"Yes"| Question4{"Prefer simpler API?"}
    Question4 --> |"Yes"| V2OneShot["Use V2<br/>unstable_v2_prompt()"]
    Question4 --> |"No"| V1Choice["Use V1<br/>query()"]
    
    Question3 --> |"No"| Question5{"Need hooks<br/>for tool use?"}
    Question5 --> |"Yes"| V1Choice
    Question5 --> |"No"| V2Choice
    
    V1Choice --> V1File["hello-world/<br/>hello-world.ts"]
    V2Choice --> V2File["hello-world-v2/<br/>v2-examples.ts"]
    V2OneShot --> V2File
    
    style V2Choice fill:#f9f9f9
    style V1Choice fill:#f9f9f9
    style V2OneShot fill:#f9f9f9
```

**Sources:** [hello-world-v2/README.md:6-11]()

## Prerequisites

Both demos require:
- Node.js 18+ or Bun runtime
- Anthropic API key
- TypeScript execution environment (`tsx`)

Dependencies are minimal:
- `@anthropic-ai/claude-agent-sdk` - The core SDK package
- `typescript` and `tsx` - For TypeScript execution
- `@types/node` - Node.js type definitions

**Sources:** [README.md:35-36](), [hello-world-v2/package.json:7-14]()

## Running the Demos

### V1 Demo
```bash
cd hello-world
npx tsx hello-world.ts
```

### V2 Demo
```bash
cd hello-world-v2
npx tsx v2-examples.ts basic        # Basic send/stream pattern
npx tsx v2-examples.ts multi-turn   # Multi-turn conversation
npx tsx v2-examples.ts one-shot     # unstable_v2_prompt() helper
npx tsx v2-examples.ts resume       # Session persistence
```

**Sources:** [hello-world-v2/README.md:15-21](), [hello-world-v2/package.json:4-6]()

## Further Reading

- For detailed V1 API documentation, see [Hello World (V1 API)](#7.1)
- For detailed V2 API documentation, see [Hello World V2 (Session API)](#7.2)
- For comprehensive SDK concepts applicable to both APIs, see [SDK Core Concepts](#8.1)
- For V1 `query()` function details, see [V1 API: Query Function](#8.2)
- For V2 Session API details, see [V2 API: Session Management](#8.3)
- For production examples using V1, see [Resume Generator Demo](#3), [Email Agent Demo](#4), [Research Agent Demo](#5)

**Sources:** [README.md:1-69]()

---

