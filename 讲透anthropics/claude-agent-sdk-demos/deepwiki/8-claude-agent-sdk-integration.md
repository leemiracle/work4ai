<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-agent-sdk-demos · page 8 Claude Agent SDK Integration · fetched 2026-10-26 -->

# Claude Agent SDK Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [hello-world-v2/README.md](hello-world-v2/README.md)
- [hello-world-v2/package.json](hello-world-v2/package.json)
- [hello-world-v2/tsconfig.json](hello-world-v2/tsconfig.json)
- [hello-world-v2/v2-examples.ts](hello-world-v2/v2-examples.ts)
- [resume-generator/.claude/skills/docx/SKILL.md](resume-generator/.claude/skills/docx/SKILL.md)
- [resume-generator/.claude/skills/docx/docx-js.md](resume-generator/.claude/skills/docx/docx-js.md)
- [resume-generator/.gitignore](resume-generator/.gitignore)
- [resume-generator/README.md](resume-generator/README.md)
- [resume-generator/package.json](resume-generator/package.json)
- [resume-generator/resume-generator.ts](resume-generator/resume-generator.ts)

</details>



## Purpose and Scope

This document provides a comprehensive overview of integrating the `@anthropic-ai/claude-agent-sdk` package across different application patterns. It covers the SDK's architecture, available API surfaces, configuration options, and message flow patterns used throughout the demonstration applications.

For detailed information on specific API versions, see [V1 API: Query Function](#8.2) and [V2 API: Session Management](#8.3). For extending agent capabilities, see [Tools and Hooks](#8.4), [Skills System](#8.5), and [Custom MCP Servers](#8.6).

---

## SDK Package Architecture

The Claude Agent SDK provides two distinct API surfaces exported from the `@anthropic-ai/claude-agent-sdk` package. All demos import directly from this package and select the appropriate API based on their use case.

### SDK Exports and API Surfaces

```mermaid
graph TB
    Package["@anthropic-ai/claude-agent-sdk<br/>NPM Package"]
    
    subgraph "V1 API Exports"
        QueryFunc["query(options)<br/>Function Export"]
        V1Types["Types:<br/>QueryOptions<br/>Message<br/>ToolUseHook<br/>ToolMatcher"]
    end
    
    subgraph "V2 API Exports"
        V2Create["unstable_v2_createSession(options)<br/>Function Export"]
        V2Resume["unstable_v2_resumeSession(sessionId, options)<br/>Function Export"]
        V2Prompt["unstable_v2_prompt(prompt, options)<br/>Function Export"]
        V2Types["Types:<br/>Session<br/>SessionOptions<br/>V2Message"]
    end
    
    subgraph "Demo Applications"
        Resume["resume-generator.ts<br/>import { query }"]
        Email["email-agent server.ts<br/>import { query }"]
        Research["research-agent<br/>import { query }"]
        HelloV1["hello-world<br/>import { query }"]
        HelloV2["hello-world-v2/v2-examples.ts<br/>import { unstable_v2_* }"]
    end
    
    Package --> QueryFunc
    Package --> V1Types
    Package --> V2Create
    Package --> V2Resume
    Package --> V2Prompt
    Package --> V2Types
    
    QueryFunc --> Resume
    QueryFunc --> Email
    QueryFunc --> Research
    QueryFunc --> HelloV1
    
    V2Create --> HelloV2
    V2Resume --> HelloV2
    V2Prompt --> HelloV2
```

**Sources:** [resume-generator/resume-generator.ts:10](), [hello-world-v2/v2-examples.ts:8-12]()

---

## Integration Patterns by Demo

Each demonstration application uses the SDK in a specific way, showcasing different integration patterns and configuration approaches.

### Demo Application SDK Usage Map

```mermaid
graph LR
    subgraph "V1 API Pattern"
        ResumeGen["resume-generator.ts<br/>const q = query({<br/>  prompt, options: {<br/>    allowedTools,<br/>    settingSources,<br/>    systemPrompt<br/>  }<br/>})<br/>for await (const msg of q)"]
        
        EmailAgent["email-agent<br/>query() with<br/>custom MCP tools<br/>search_inbox,<br/>read_emails"]
        
        ResearchAgent["research-agent<br/>query() with hooks<br/>PreToolUse,<br/>PostToolUse<br/>SubagentTracker"]
        
        HelloV1Demo["hello-world<br/>Basic query()<br/>minimal config"]
    end
    
    subgraph "V2 API Pattern"
        HelloV2Demo["v2-examples.ts<br/>await using session =<br/>  unstable_v2_createSession()<br/>await session.send()<br/>for await (msg of session.stream())"]
        
        V2Resume["sessionResume()<br/>unstable_v2_resumeSession<br/>session persistence"]
        
        V2OneShot["oneShot()<br/>unstable_v2_prompt<br/>single-turn convenience"]
    end
    
    ResumeGen -.->|"settingSources: ['project']"| Skills["Skills from<br/>.claude/skills/"]
    EmailAgent -.->|"customMcpServers"| MCPServers["Custom MCP Tools"]
    ResearchAgent -.->|"hooks"| Tracking["SubagentTracker<br/>tool_calls.jsonl"]
```

**Sources:** [resume-generator/resume-generator.ts:43-53](), [hello-world-v2/v2-examples.ts:36-48](), [hello-world-v2/v2-examples.ts:88-126]()

---

## Core Integration Components

### Required Imports and Type Definitions

The SDK provides strongly-typed interfaces for all integration points. Applications import only what they need based on their API choice.

**V1 API Core Imports:**
```typescript
import { query } from '@anthropic-ai/claude-agent-sdk';
```
[resume-generator/resume-generator.ts:10]()

**V2 API Core Imports:**
```typescript
import {
  unstable_v2_createSession,
  unstable_v2_resumeSession,
  unstable_v2_prompt,
} from '@anthropic-ai/claude-agent-sdk';
```
[hello-world-v2/v2-examples.ts:8-12]()

### Configuration Object Structure

Both API versions accept a configuration object with common fields and version-specific options.

#### Common Configuration Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `model` | `string` | Claude model selection | `'sonnet'`, `'haiku'`, `'opus'` |
| `cwd` | `string` | Current working directory for file operations | `process.cwd()` |
| `maxTurns` | `number` | Maximum conversation turns before stopping | `30` |
| `allowedTools` | `string[]` | Whitelist of tool names agent can use | `['Bash', 'Write', 'Read']` |
| `systemPrompt` | `string` | System instructions prepended to conversation | Workflow guidance |

#### V1-Specific Configuration

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `prompt` | `string` | Initial user prompt (required) | `"Research and create resume"` |
| `settingSources` | `string[]` | Sources for skill discovery | `['project']` loads `.claude/skills/` |
| `hooks` | `object` | Pre/post tool execution callbacks | `{ preToolUse: [...], postToolUse: [...] }` |

**Sources:** [resume-generator/resume-generator.ts:43-53]()

#### V2-Specific Configuration

The V2 API separates session creation from message sending, so the prompt is not part of session options.

```typescript
// Session creation
await using session = unstable_v2_createSession({ 
  model: 'sonnet',
  // other options but NO prompt
});

// Separate send operation
await session.send('Hello! Introduce yourself.');
```

**Sources:** [hello-world-v2/v2-examples.ts:39-40]()

---

## Message Flow Architecture

### V1 Query Function Message Stream

The V1 API returns an `AsyncGenerator<Message>` that yields messages representing the entire conversation flow, including both input specifications and output results.

```mermaid
graph TB
    QueryCall["const q = query({ prompt, options })"]
    AsyncGen["AsyncGenerator&lt;Message&gt;"]
    ForAwait["for await (const msg of q)"]
    
    subgraph "Message Types"
        AssistantMsg["msg.type === 'assistant'<br/>msg.message.content[]<br/>{ type: 'text', text: string }<br/>{ type: 'tool_use', name, input, id }"]
        
        ResultMsg["msg.type === 'result'<br/>msg.subtype === 'tool_result'<br/>msg.content"]
        
        SystemMsg["msg.type === 'system'<br/>msg.subtype === 'init'<br/>Session initialization"]
        
        ErrorMsg["msg.type === 'result'<br/>msg.subtype === 'error'<br/>Error details"]
    end
    
    QueryCall --> AsyncGen
    AsyncGen --> ForAwait
    ForAwait --> AssistantMsg
    ForAwait --> ResultMsg
    ForAwait --> SystemMsg
    ForAwait --> ErrorMsg
    
    AssistantMsg --> ProcessText["if (block.type === 'text')<br/>console.log(block.text)"]
    AssistantMsg --> ProcessTool["if (block.type === 'tool_use')<br/>Handle tool invocation"]
    ResultMsg --> ProcessResult["Process tool result<br/>JSON.stringify(msg.content)"]
```

**Resume Generator Message Processing:**
```typescript
for await (const msg of q) {
  if (msg.type === 'assistant' && msg.message) {
    for (const block of msg.message.content) {
      if (block.type === 'text') {
        console.log(block.text);
      }
      if (block.type === 'tool_use') {
        console.log(`\n🔧 Using tool: ${block.name}`);
      }
    }
  }
  if (msg.type === 'result' && msg.subtype === 'tool_result') {
    console.log(`   ↳ Result: ${JSON.stringify(msg.content)}`);
  }
}
```
[resume-generator/resume-generator.ts:55-76]()

**Sources:** [resume-generator/resume-generator.ts:55-76]()

---

### V2 Session API Message Stream

The V2 API separates input (`send()`) from output (`stream()`), providing a cleaner separation of concerns for multi-turn conversations.

```mermaid
graph TB
    CreateSession["await using session =<br/>unstable_v2_createSession({ model })"]
    SendMsg["await session.send(userMessage)"]
    StreamLoop["for await (const msg of session.stream())"]
    
    subgraph "V2 Message Types"
        V2Assistant["msg.type === 'assistant'<br/>msg.message.content[]<br/>Response only"]
        
        V2System["msg.type === 'system'<br/>msg.subtype === 'init'<br/>msg.session_id"]
        
        V2Result["msg.type === 'result'<br/>msg.subtype === 'success'<br/>msg.total_cost_usd"]
    end
    
    subgraph "Session Lifecycle"
        SessionObj["Session Object<br/>Maintains conversation history<br/>Automatic resource cleanup"]
        Dispose["await using auto-disposes<br/>when leaving scope"]
    end
    
    CreateSession --> SessionObj
    SessionObj --> SendMsg
    SendMsg --> StreamLoop
    StreamLoop --> V2Assistant
    StreamLoop --> V2System
    StreamLoop --> V2Result
    SessionObj --> Dispose
    
    V2System --> ExtractSessionId["sessionId = msg.session_id<br/>For resumption"]
```

**Basic V2 Session Pattern:**
```typescript
await using session = unstable_v2_createSession({ model: 'sonnet' });
await session.send('Hello! Introduce yourself in one sentence.');

for await (const msg of session.stream()) {
  if (msg.type === 'assistant') {
    const text = msg.message.content.find(
      (c): c is { type: 'text'; text: string } => c.type === 'text'
    );
    console.log(`Claude: ${text?.text}`);
  }
}
```
[hello-world-v2/v2-examples.ts:39-47]()

**Sources:** [hello-world-v2/v2-examples.ts:36-48]()

---

## Model Selection and Capabilities

The SDK supports multiple Claude model variants, each with different performance characteristics.

### Available Models

| Model Identifier | Description | Typical Use Case |
|------------------|-------------|------------------|
| `'sonnet'` | Claude 3.5 Sonnet | Default choice, balanced performance |
| `'haiku'` | Claude 3 Haiku | Fast, cost-effective for simple tasks |
| `'opus'` | Claude 3 Opus | Most capable, highest cost |

**Resume Generator uses Sonnet:**
```typescript
const q = query({
  prompt,
  options: {
    model: 'sonnet',
    maxTurns: 30,
    // ...
  },
});
```
[resume-generator/resume-generator.ts:43-53]()

**Sources:** [resume-generator/resume-generator.ts:48]()

---

## Working Directory and File System Access

The SDK's file system operations (via `Bash`, `Write`, `Read`, `Glob` tools) execute relative to a configured current working directory.

### Current Working Directory Configuration

```mermaid
graph LR
    QueryOptions["query({ options: {<br/>  cwd: process.cwd()<br/>}})"]
    
    AgentProcess["Agent Subprocess<br/>Executes in cwd"]
    
    subgraph "File Operations"
        Write["Write tool<br/>Creates files relative to cwd"]
        Read["Read tool<br/>Reads files relative to cwd"]
        Bash["Bash tool<br/>Executes commands in cwd"]
        Glob["Glob tool<br/>Searches within cwd"]
    end
    
    QueryOptions --> AgentProcess
    AgentProcess --> Write
    AgentProcess --> Read
    AgentProcess --> Bash
    AgentProcess --> Glob
    
    Write --> OutputDir["agent/custom_scripts/<br/>Generated files"]
    Read --> SkillsDir[".claude/skills/<br/>Skill documentation"]
```

**Resume Generator CWD Setup:**
```typescript
const outputDir = path.join(process.cwd(), 'agent', 'custom_scripts');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const q = query({
  prompt,
  options: {
    cwd: process.cwd(),
    // Agent can now write to agent/custom_scripts/
  },
});
```
[resume-generator/resume-generator.ts:29-53]()

**Sources:** [resume-generator/resume-generator.ts:34-47]()

---

## Tool Allowlist Configuration

The `allowedTools` array restricts which tools the agent can invoke, providing security and scope control.

### Standard Tool Names

```mermaid
graph TB
    AllowedTools["allowedTools: string[]"]
    
    subgraph "File System Tools"
        Write["'Write'<br/>Create/modify files"]
        Read["'Read'<br/>Read file contents"]
        Glob["'Glob'<br/>Search files by pattern"]
    end
    
    subgraph "Execution Tools"
        Bash["'Bash'<br/>Execute shell commands"]
    end
    
    subgraph "Web Tools"
        WebSearch["'WebSearch'<br/>Search internet"]
        WebFetch["'WebFetch'<br/>Fetch URLs"]
    end
    
    subgraph "Advanced Tools"
        Skill["'Skill'<br/>Load skills from settingSources"]
        Task["'Task'<br/>Spawn subagents"]
    end
    
    AllowedTools --> Write
    AllowedTools --> Read
    AllowedTools --> Glob
    AllowedTools --> Bash
    AllowedTools --> WebSearch
    AllowedTools --> WebFetch
    AllowedTools --> Skill
    AllowedTools --> Task
```

**Resume Generator Tool Configuration:**
```typescript
allowedTools: [
  'Skill',      // Load docx skill from .claude/skills/
  'WebSearch',  // Research person online
  'WebFetch',   // Fetch specific pages
  'Bash',       // Execute generated script
  'Write',      // Write generate_resume.js
  'Read',       // Read skill documentation
  'Glob',       // Search for existing files
],
```
[resume-generator/resume-generator.ts:49]()

**Sources:** [resume-generator/resume-generator.ts:49]()

---

## Skills Discovery and Loading

When `settingSources: ['project']` is specified, the SDK automatically discovers skills from the `.claude/skills/` directory relative to the configured `cwd`.

### Skill Loading Architecture

```mermaid
graph TB
    QueryOpts["query({ options: {<br/>  settingSources: ['project'],<br/>  allowedTools: ['Skill', ...]<br/>}})"]
    
    SkillsRoot[".claude/skills/<br/>Project skills root"]
    
    subgraph "Skill Structure"
        DocxSkill[".claude/skills/docx/<br/>SKILL.md<br/>docx-js.md<br/>ooxml.md"]
        
        OtherSkills[".claude/skills/*/<br/>Other skill directories"]
    end
    
    AgentInvoke["Agent invokes:<br/>Skill tool with skill_name"]
    
    SkillRead["SDK reads:<br/>.claude/skills/{skill_name}/SKILL.md<br/>Returns content to agent"]
    
    AgentDecision["Agent reads SKILL.md<br/>Decides which workflow<br/>May read additional files"]
    
    QueryOpts --> SkillsRoot
    SkillsRoot --> DocxSkill
    SkillsRoot --> OtherSkills
    
    AgentInvoke --> SkillRead
    SkillRead --> AgentDecision
    AgentDecision --> ReadDocs["Agent reads:<br/>docx-js.md (~500 lines)<br/>ENTIRE FILE required"]
```

**Resume Generator Skill Configuration:**
```typescript
const q = query({
  prompt,
  options: {
    allowedTools: ['Skill', 'WebSearch', 'WebFetch', 'Bash', 'Write', 'Read', 'Glob'],
    settingSources: ['project'],  // Load skills from .claude/skills/
    // ...
  },
});
```
[resume-generator/resume-generator.ts:43-53]()

The docx skill's `SKILL.md` provides a decision tree that directs the agent to read specific documentation files completely before proceeding:

```markdown
### Creating New Document
Use "Creating a new Word document" workflow

### Workflow
1. **MANDATORY - READ ENTIRE FILE**: Read [`docx-js.md`](docx-js.md) (~500 lines) 
   completely from start to finish. **NEVER set any range limits when reading this file.**
```
[resume-generator/.claude/skills/docx/SKILL.md:58-60]()

**Sources:** [resume-generator/resume-generator.ts:50](), [resume-generator/.claude/skills/docx/SKILL.md:1-5](), [resume-generator/.claude/skills/docx/SKILL.md:58-60]()

---

## System Prompt Configuration

The `systemPrompt` option prepends instructions to the conversation, providing workflow guidance and constraints.

### System Prompt Architecture

```mermaid
graph LR
    SystemPrompt["systemPrompt: string<br/>Workflow + Constraints"]
    
    ConversationContext["Full Conversation Context:<br/>1. System Prompt<br/>2. User Prompt<br/>3. Agent Responses<br/>4. Tool Results"]
    
    AgentBehavior["Agent Behavior<br/>Guided by system instructions<br/>throughout conversation"]
    
    SystemPrompt --> ConversationContext
    ConversationContext --> AgentBehavior
    
    subgraph "Resume Generator System Prompt"
        Workflow["WORKFLOW:<br/>1. WebSearch for background<br/>2. Create .docx with docx library"]
        
        Output["OUTPUT:<br/>- Script: agent/custom_scripts/generate_resume.js<br/>- Resume: agent/custom_scripts/resume.docx"]
        
        PageFit["PAGE FIT constraints:<br/>- 0.5 inch margins<br/>- Specific font sizes<br/>- Max bullet points"]
    end
    
    AgentBehavior --> Workflow
    AgentBehavior --> Output
    AgentBehavior --> PageFit
```

**Resume Generator System Prompt:**
```typescript
const SYSTEM_PROMPT = `You are a professional resume writer. Research a person and create a 1-page .docx resume.

WORKFLOW:
1. WebSearch for the person's background (LinkedIn, GitHub, company pages)
2. Create a .docx file using the docx library

OUTPUT:
- Script: agent/custom_scripts/generate_resume.js
- Resume: agent/custom_scripts/resume.docx

PAGE FIT (must be exactly 1 page):
- 0.5 inch margins, Name 24pt, Headers 12pt, Body 10pt
- 2-3 bullet points per job, ~80-100 chars each
- Max 3 job roles, 2-line summary, 2-line skills`;

const q = query({
  prompt,
  options: {
    systemPrompt: SYSTEM_PROMPT,
    // ...
  },
});
```
[resume-generator/resume-generator.ts:14-27](), [resume-generator/resume-generator.ts:51]()

**Sources:** [resume-generator/resume-generator.ts:14-27]()

---

## Session Lifecycle Management

### V1 API Lifecycle

The V1 API has no explicit session management. Each `query()` call is independent, and conversation history must be managed manually if multi-turn behavior is needed.

```mermaid
graph LR
    Start["Application Start"]
    Query1["query({ prompt: 'Task 1' })<br/>for await (msg of q1)"]
    Complete1["Task 1 Complete"]
    Query2["query({ prompt: 'Task 2' })<br/>No shared context with Task 1"]
    Complete2["Task 2 Complete"]
    End["Application End"]
    
    Start --> Query1
    Query1 --> Complete1
    Complete1 --> Query2
    Query2 --> Complete2
    Complete2 --> End
```

**Sources:** [resume-generator/resume-generator.ts:43-76]()

---

### V2 API Lifecycle with Session Persistence

The V2 API provides explicit session management with automatic resource cleanup and optional persistence via `sessionId`.

```mermaid
graph TB
    subgraph "Session Creation"
        CreateNew["await using session =<br/>unstable_v2_createSession({ model })"]
        InitMsg["Stream receives:<br/>msg.type === 'system'<br/>msg.subtype === 'init'<br/>msg.session_id"]
        StoreId["Store sessionId for later:<br/>let sessionId = msg.session_id"]
    end
    
    subgraph "Active Session"
        SendMsg1["await session.send('Question 1')"]
        Stream1["for await (msg of session.stream())"]
        SendMsg2["await session.send('Question 2')<br/>Context from Q1 maintained"]
        Stream2["for await (msg of session.stream())"]
    end
    
    subgraph "Session Cleanup"
        AutoDispose["Automatic disposal:<br/>await using ensures cleanup<br/>when leaving scope"]
    end
    
    subgraph "Session Resumption"
        LaterTime["--- Time passes ---"]
        Resume["await using session =<br/>unstable_v2_resumeSession(sessionId, { model })"]
        ContinueConv["await session.send('Question 3')<br/>Context from Q1 & Q2 restored"]
        StreamResume["for await (msg of session.stream())"]
    end
    
    CreateNew --> InitMsg
    InitMsg --> StoreId
    StoreId --> SendMsg1
    SendMsg1 --> Stream1
    Stream1 --> SendMsg2
    SendMsg2 --> Stream2
    Stream2 --> AutoDispose
    
    AutoDispose --> LaterTime
    LaterTime --> Resume
    Resume --> ContinueConv
    ContinueConv --> StreamResume
```

**Session Resume Example:**
```typescript
let sessionId: string | undefined;

// First session
{
  await using session = unstable_v2_createSession({ model: 'sonnet' });
  await session.send('My favorite color is blue. Remember this!');
  
  for await (const msg of session.stream()) {
    if (msg.type === 'system' && msg.subtype === 'init') {
      sessionId = msg.session_id;  // Capture for later
    }
  }
} // Session auto-disposed here

// Later: Resume with context
{
  await using session = unstable_v2_resumeSession(sessionId!, { model: 'sonnet' });
  await session.send('What is my favorite color?');  // Claude remembers "blue"
  
  for await (const msg of session.stream()) {
    // Process response...
  }
}
```
[hello-world-v2/v2-examples.ts:88-126]()

**Sources:** [hello-world-v2/v2-examples.ts:88-126]()

---

## One-Shot Convenience Function

The V2 API provides `unstable_v2_prompt()` as a convenience function for single-turn interactions that don't require session management.

```mermaid
graph LR
    Prompt["unstable_v2_prompt(<br/>prompt: string,<br/>options: SessionOptions<br/>)"]
    
    Result["Returns Promise&lt;Result&gt;<br/>result.subtype === 'success'<br/>result.result: string<br/>result.total_cost_usd: number"]
    
    Usage["const result = await unstable_v2_prompt(<br/>  'What is the capital of France?',<br/>  { model: 'sonnet' }<br/>)"]
    
    Prompt --> Result
    Result --> Usage
```

**One-Shot Example:**
```typescript
const result = await unstable_v2_prompt(
  'What is the capital of France? One word.',
  { model: 'sonnet' }
);

if (result.subtype === 'success') {
  console.log(`Answer: ${result.result}`);
  console.log(`Cost: $${result.total_cost_usd.toFixed(4)}`);
}
```
[hello-world-v2/v2-examples.ts:76-84]()

**Sources:** [hello-world-v2/v2-examples.ts:75-85]()

---

## Package Dependencies

All demo applications depend on the same core SDK package with consistent versioning.

### NPM Package Configuration

**Resume Generator:**
```json
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.1.59",
    "docx": "^9.5.1"
  }
}
```
[resume-generator/package.json:8-11]()

**Hello World V2:**
```json
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.1.59"
  }
}
```
[hello-world-v2/package.json:7-9]()

**Sources:** [resume-generator/package.json:8-11](), [hello-world-v2/package.json:7-9]()

---

## TypeScript Configuration

Demo applications use modern TypeScript with ESNext modules for compatibility with the SDK's module system.

### Shared TypeScript Configuration Pattern

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true
  }
}
```
[hello-world-v2/tsconfig.json:2-10]()

**Key Configuration Requirements:**
- `"module": "ESNext"` - Required for SDK's ESM exports
- `"moduleResolution": "bundler"` - Enables modern import resolution
- `"esModuleInterop": true` - Ensures compatibility with CommonJS modules
- `"target": "ES2022"` - Supports modern JavaScript features like `await using`

**Sources:** [hello-world-v2/tsconfig.json:1-13]()

---

