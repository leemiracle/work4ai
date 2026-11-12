<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/agent-chat-ui · page 3 Message System · fetched 2026-10-26 -->

# Message System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/thread/index.tsx](src/components/thread/index.tsx)
- [src/components/thread/messages/ai.tsx](src/components/thread/messages/ai.tsx)
- [src/components/thread/messages/generic-interrupt.tsx](src/components/thread/messages/generic-interrupt.tsx)
- [src/components/thread/messages/human.tsx](src/components/thread/messages/human.tsx)
- [src/components/thread/messages/shared.tsx](src/components/thread/messages/shared.tsx)

</details>



This document describes the message rendering system, which is responsible for displaying conversation messages from LangGraph agents, handling user input, and managing message-related interactions. The system processes streaming events from the LangGraph server and renders them as human messages, AI messages, and tool invocations/results.

For information about the streaming connection and message state management, see [Stream Provider](#2.2). For details about human-in-the-loop agent interrupts, see [Agent Inbox System](#4). For multimodal content handling, see [File Upload and Multimodal Content](#6).

## Message Types and Rendering Pipeline

The message system handles three primary message types, each with its own rendering component:

```mermaid
graph TB
    subgraph "Message Sources"
        StreamContext["useStreamContext()"]
        StreamContext --> Messages["messages: Message[]"]
    end
    
    subgraph "Pre-Processing"
        Messages --> Filter["Filter DO_NOT_RENDER_ID_PREFIX"]
        Filter --> Ensure["ensureToolCallsHaveResponses()"]
    end
    
    subgraph "Type Routing"
        Ensure --> TypeCheck{"message.type"}
        TypeCheck -->|"'human'"| HumanRoute["HumanMessage Component"]
        TypeCheck -->|"'ai'"| AIRoute["AssistantMessage Component"]
        TypeCheck -->|"'tool'"| ToolRoute["AssistantMessage<br/>(type === 'tool')"]
    end
    
    subgraph "Content Extraction"
        HumanRoute --> GetContent1["getContentString()"]
        AIRoute --> GetContent2["getContentString()"]
        ToolRoute --> GetContent3["message.content"]
    end
    
    subgraph "Rendering Layer"
        GetContent1 --> HumanUI["Text + Multimodal Preview"]
        GetContent2 --> AIText["MarkdownText"]
        GetContent2 --> AITools["ToolCalls"]
        GetContent2 --> AICustom["LoadExternalComponent"]
        GetContent2 --> AIInterrupt["Interrupt Views"]
        GetContent3 --> ToolResult["ToolResult Display"]
    end
    
    subgraph "Message Metadata"
        StreamContext --> MetaAPI["getMessagesMetadata()"]
        MetaAPI --> BranchInfo["branch, branchOptions"]
        MetaAPI --> CheckpointInfo["firstSeenState.parent_checkpoint"]
    end
    
    BranchInfo --> BranchSwitcher["BranchSwitcher"]
    CheckpointInfo --> Regenerate["handleRegenerate()"]
```

**Sources**: [src/components/thread/index.tsx:402-433](), [src/components/thread/messages/ai.tsx:96-212](), [src/components/thread/messages/human.tsx:37-151]()

## Message Type Implementations

### Core Message Interface

All messages conform to the `Message` type from `@langchain/langgraph-sdk`:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string \| undefined` | Unique message identifier |
| `type` | `'human' \| 'ai' \| 'tool'` | Message type discriminator |
| `content` | `string \| MessageContentComplex[]` | Message content (text or structured) |
| `tool_calls` | `ToolCall[]` (AI only) | Tool invocations from AI |

**Sources**: [src/components/thread/messages/ai.tsx:3](), [src/components/thread/messages/human.tsx:2]()

### HumanMessage Component

The `HumanMessage` component renders user messages with support for editing and multimodal content display:

```mermaid
graph LR
    subgraph "HumanMessage Component"
        Message["Message Data"]
        Message --> EditCheck{"isEditing?"}
        
        EditCheck -->|"true"| EditMode["EditableContent<br/>Textarea with<br/>Cmd+Enter submit"]
        EditCheck -->|"false"| DisplayMode["Display Mode"]
        
        DisplayMode --> ContentArray{"Array.isArray<br/>(message.content)"}
        ContentArray -->|"true"| ProcessBlocks["Iterate content blocks"]
        ProcessBlocks --> BlockCheck{"isBase64ContentBlock?"}
        BlockCheck -->|"true"| MultiModal["MultimodalPreview<br/>size='md'"]
        BlockCheck -->|"false"| Skip["Skip block"]
        
        DisplayMode --> TextCheck{"contentString?"}
        TextCheck -->|"true"| TextDisplay["p.bg-muted<br/>whitespace-pre-wrap"]
        
        EditMode --> Submit["handleSubmitEdit()"]
        Submit --> ThreadSubmit["thread.submit()<br/>checkpoint: parentCheckpoint<br/>optimisticValues"]
    end
    
    subgraph "Metadata"
        Meta["getMessagesMetadata()"]
        Meta --> ParentCP["firstSeenState.parent_checkpoint"]
        Meta --> BranchData["branch, branchOptions"]
    end
    
    subgraph "Action Bar"
        BranchData --> BS["BranchSwitcher"]
        CommandBar["CommandBar<br/>isHumanMessage=true<br/>Edit/Copy controls"]
    end
    
    ParentCP --> Submit
```

**Key features**:
- **Editable content**: Users can edit their messages using `Cmd+Enter` to submit [src/components/thread/messages/human.tsx:20-24]()
- **Multimodal display**: Images and PDFs are rendered using `MultimodalPreview` [src/components/thread/messages/human.tsx:93-110]()
- **Optimistic updates**: When editing, the UI updates immediately using `optimisticValues` [src/components/thread/messages/human.tsx:63-71]()
- **Right-aligned layout**: Human messages appear on the right with `.ml-auto` styling [src/components/thread/messages/human.tsx:79]()

**Sources**: [src/components/thread/messages/human.tsx:37-151](), [src/lib/multimodal-utils.ts]()

### AssistantMessage Component

The `AssistantMessage` component is the most complex, handling AI responses, tool calls, custom UI, and interrupts:

```mermaid
graph TB
    subgraph "AssistantMessage Entry"
        Props["Props:<br/>message?: Message<br/>isLoading: boolean<br/>handleRegenerate: fn"]
        Props --> TypeCheck{"message.type"}
    end
    
    subgraph "Tool Result Path"
        TypeCheck -->|"'tool'"| ToolResult["ToolResult Component"]
        ToolResult --> InterruptCheck1["Interrupt Display"]
    end
    
    subgraph "AI Message Path"
        TypeCheck -->|"'ai'"| ContentString["getContentString()"]
        ContentString --> TextRender{"contentString.length > 0"}
        TextRender -->|"true"| Markdown["MarkdownText"]
        
        TypeCheck -->|"'ai'"| ToolCallCheck{"hasToolCalls &&<br/>toolCallsHaveContents"}
        ToolCallCheck -->|"true"| ToolCalls["ToolCalls Component"]
        
        TypeCheck -->|"'ai'"| AnthropicCheck{"anthropicStreamedToolCalls?"}
        AnthropicCheck -->|"true"| ParseAnthropic["parseAnthropicStreamedToolCalls()"]
        ParseAnthropic --> ToolCalls
        
        TypeCheck -->|"'ai'"| CustomCheck{"values.ui.length > 0"}
        CustomCheck -->|"true"| LoadExternal["LoadExternalComponent<br/>@langchain/langgraph-sdk/react-ui"]
        
        TypeCheck -->|"'ai'"| InterruptCheck2["Interrupt Display"]
    end
    
    subgraph "Interrupt Routing"
        InterruptCheck2 --> Schema{"isAgentInboxInterruptSchema()"}
        Schema -->|"true"| AgentInbox["ThreadView"]
        Schema -->|"false"| Generic["GenericInterruptView"]
    end
    
    subgraph "Action Controls"
        BranchMeta["meta.branch<br/>meta.branchOptions"]
        BranchMeta --> BranchSwitch["BranchSwitcher"]
        
        ParentCP["meta.firstSeenState<br/>.parent_checkpoint"]
        ParentCP --> RegenerateBtn["Regenerate Button"]
    end
    
    subgraph "Hide Tool Calls"
        HideFlag["hideToolCalls query param"]
        HideFlag --> HideCheck{"hideToolCalls && type === 'tool'"}
        HideCheck -->|"true"| ReturnNull["return null"]
        HideCheck -->|"false"| Render["Render tool calls"]
    end
```

**Key features**:
- **Content rendering**: Text content is processed through `MarkdownText` with syntax highlighting [src/components/thread/messages/ai.tsx:157-161]()
- **Tool call handling**: Both standard OpenAI format and Anthropic streaming format are supported [src/components/thread/messages/ai.tsx:46-68]()
- **Custom components**: External React components from agents are loaded via `LoadExternalComponent` [src/components/thread/messages/ai.tsx:177-182]()
- **Interrupt display**: Interrupts route to either `ThreadView` or `GenericInterruptView` based on schema validation [src/components/thread/messages/ai.tsx:76-94]()
- **Branch switching**: Users can navigate between different conversation branches [src/components/thread/messages/ai.tsx:194-199]()
- **Message regeneration**: The regenerate button triggers re-execution from a parent checkpoint [src/components/thread/messages/ai.tsx:239-251]()
- **Hide tool calls**: The `hideToolCalls` query parameter controls tool visibility [src/components/thread/messages/ai.tsx:139-141]()

**Sources**: [src/components/thread/messages/ai.tsx:96-224]()

## Message Content Processing

### Content Extraction

The `getContentString()` utility extracts text from message content:

```mermaid
graph LR
    Content["Message.content"]
    Content --> IsString{"typeof === 'string'"}
    IsString -->|"true"| ReturnDirect["Return string"]
    IsString -->|"false"| IsArray{"Array.isArray()"}
    IsArray -->|"true"| FilterText["Filter type === 'text'"]
    FilterText --> JoinText["Join with newlines"]
    IsArray -->|"false"| ReturnEmpty["Return empty string"]
```

**Sources**: [src/components/thread/utils.ts]()

### Anthropic Tool Call Parsing

Anthropic models stream tool calls in a different format, requiring special parsing:

```mermaid
graph TB
    Content["content: MessageContentComplex[]"]
    Content --> Filter["Filter c.type === 'tool_use' && c.id"]
    Filter --> Map["Map to ToolCall format"]
    Map --> ParseArgs["parsePartialJson(toolCall.input)"]
    ParseArgs --> Format["Format as:<br/>{name, id, args, type}"]
```

**Implementation details**:
- Uses `parsePartialJson` from `@langchain/core/output_parsers` to handle incomplete JSON [src/components/thread/messages/ai.tsx:54-57]()
- Filters for content blocks with `type === "tool_use"` and an `id` field [src/components/thread/messages/ai.tsx:49]()
- Gracefully handles parsing errors with empty object fallback [src/components/thread/messages/ai.tsx:58]()

**Sources**: [src/components/thread/messages/ai.tsx:46-68]()

## Tool Call Rendering

Tool calls and their results are rendered through specialized components defined in [src/components/thread/messages/tool-calls.tsx]():

### ToolCalls Component

Displays tool invocations with expandable argument details:

| Element | Purpose |
|---------|---------|
| Tool name badge | Shows tool name in a styled badge |
| Arguments table | Key-value pairs of tool arguments |
| Expand/collapse | Handles long content with animation |

**Sources**: [src/components/thread/messages/ai.tsx:165-174]()

### ToolResult Component

Displays tool execution results with JSON formatting and syntax highlighting:

```mermaid
graph LR
    ToolMessage["message.type === 'tool'"]
    ToolMessage --> ExtractContent["message.content"]
    ExtractContent --> IsString{"typeof === 'string'"}
    IsString -->|"true"| TryParse["Try JSON.parse()"]
    TryParse -->|"success"| FormatJSON["JSON.stringify(parsed, null, 2)"]
    TryParse -->|"fail"| DisplayRaw["Display raw string"]
    IsString -->|"false"| DisplayRaw
    FormatJSON --> Highlight["SyntaxHighlighter"]
    DisplayRaw --> Markdown["MarkdownText"]
```

**Sources**: [src/components/thread/messages/ai.tsx:146-154]()

## Interrupt Handling

When agents require human input, they emit interrupts that are displayed conditionally:

```mermaid
graph TB
    ThreadInterrupt["thread.interrupt"]
    ThreadInterrupt --> CheckConditions{"isLastMessage ||<br/>hasNoAIOrToolMessages"}
    
    CheckConditions -->|"false"| NoRender["Don't render"]
    CheckConditions -->|"true"| ValidateSchema["isAgentInboxInterruptSchema()"]
    
    ValidateSchema -->|"true"| AgentInbox["ThreadView Component<br/>Specialized agent inbox UI"]
    ValidateSchema -->|"false"| GenericView["GenericInterruptView<br/>Key-value table display"]
    
    subgraph "GenericInterruptView Features"
        GenericView --> Expandable["Expandable content<br/>framer-motion"]
        GenericView --> Truncate["Truncate long values<br/>Preserve URLs"]
        GenericView --> Table["Table layout<br/>Key-value pairs"]
    end
    
    subgraph "ThreadView Features"
        AgentInbox --> StateView["State display"]
        AgentInbox --> ActionsView["ThreadActionsView<br/>User response options"]
    end
```

**Interrupt rendering conditions**:
- Only render if `isLastMessage || hasNoAIOrToolMessages` [src/components/thread/messages/ai.tsx:84]()
- This prevents interrupts from appearing mid-conversation
- Special case: If no AI/tool messages exist, render interrupt outside message list [src/components/thread/index.tsx:420-429]()

**Generic interrupt features**:
- Expandable/collapsible content with `framer-motion` animations [src/components/thread/messages/generic-interrupt.tsx:101-106]()
- Automatic truncation for values > 100 characters [src/components/thread/messages/generic-interrupt.tsx:55-61]()
- URL detection and clickable link rendering [src/components/thread/messages/generic-interrupt.tsx:9-17]()
- Table layout for key-value pairs [src/components/thread/messages/generic-interrupt.tsx:123-141]()

**Sources**: [src/components/thread/messages/ai.tsx:76-94](), [src/components/thread/messages/generic-interrupt.tsx:42-160]()

## Custom UI Components

The system supports loading external React components from agents using the `@langchain/langgraph-sdk/react-ui` package:

```mermaid
graph LR
    Values["values.ui"]
    Values --> Filter["Filter by metadata.message_id"]
    Filter --> UIMessages["customComponents[]"]
    UIMessages --> Map["Map to LoadExternalComponent"]
    
    Map --> Props["Props:<br/>stream: thread<br/>message: customComponent<br/>meta: {ui, artifact}"]
    Props --> Render["External component renders<br/>with access to stream API"]
```

**Component discovery**:
1. Filter `values.ui` array for messages matching current `message.id` [src/components/thread/messages/ai.tsx:27-29]()
2. Each matching UI message is rendered via `LoadExternalComponent` [src/components/thread/messages/ai.tsx:35-40]()
3. Components receive stream context and artifact helpers as props [src/components/thread/messages/ai.tsx:36-39]()

**Sources**: [src/components/thread/messages/ai.tsx:18-44]()

## Message Actions and Controls

### BranchSwitcher Component

Enables navigation between conversation branches when checkpoints diverge:

```mermaid
graph LR
    BranchMeta["meta.branch<br/>meta.branchOptions"]
    BranchMeta --> Index["Find current index<br/>in branchOptions"]
    
    Index --> PrevBtn["Previous Button<br/>ChevronLeft icon"]
    Index --> Display["Display: index+1 / length"]
    Index --> NextBtn["Next Button<br/>ChevronRight icon"]
    
    PrevBtn --> OnSelect["onSelect(branchOptions[index-1])"]
    NextBtn --> OnSelect2["onSelect(branchOptions[index+1])"]
    OnSelect --> SetBranch["thread.setBranch()"]
    OnSelect2 --> SetBranch
```

**Sources**: [src/components/thread/messages/shared.tsx:69-116]()

### CommandBar Component

Provides message-specific actions (copy, edit, regenerate):

| Action | Availability | Behavior |
|--------|-------------|----------|
| Copy | All messages | Copies content to clipboard, shows checkmark feedback |
| Edit | Human messages only | Enters edit mode with textarea |
| Submit | Human edit mode | Submits edited message with checkpoint context |
| Cancel | Human edit mode | Exits edit mode without changes |
| Regenerate | AI messages only | Re-executes from parent checkpoint |

**Edit mode flow**:
1. Click edit → Set `isEditing = true`, populate `value` with `contentString` [src/components/thread/messages/human.tsx:139-142]()
2. User modifies text in `EditableContent` textarea [src/components/thread/messages/human.tsx:11-35]()
3. `Cmd+Enter` triggers `handleSubmitEdit()` [src/components/thread/messages/human.tsx:20-24]()
4. New message submitted with `checkpoint: parentCheckpoint` for time-travel [src/components/thread/messages/human.tsx:52-74]()

**Sources**: [src/components/thread/messages/shared.tsx:118-221](), [src/components/thread/messages/human.tsx:48-74]()

## Message Validation

### ensureToolCallsHaveResponses()

Before submission, messages are validated to ensure all tool calls have corresponding tool messages:

```mermaid
graph TB
    Messages["Input messages[]"]
    Messages --> Iterate["Iterate backwards"]
    Iterate --> CheckType{"message.type"}
    
    CheckType -->|"'ai'"| HasToolCalls{"Has tool_calls?"}
    HasToolCalls -->|"true"| FindResponses["Find matching tool messages<br/>by tool_call_id"]
    FindResponses --> CheckMatches{"All tool_calls<br/>have responses?"}
    CheckMatches -->|"false"| Inject["Inject placeholder<br/>tool messages with<br/>DO_NOT_RENDER_ID_PREFIX"]
    CheckMatches -->|"true"| Continue["Continue"]
    
    CheckType -->|"other"| Continue
    HasToolCalls -->|"false"| Continue
    Continue --> Done["Return validated messages[]"]
```

**Purpose**: Prevents errors when agents expect tool responses but none exist in message history.

**Implementation**:
- Placeholder tool messages use `DO_NOT_RENDER_ID_PREFIX` prefix [src/components/thread/index.tsx:12-13]()
- These messages are filtered out during rendering [src/components/thread/index.tsx:403]()
- Ensures the LangGraph agent receives properly structured message history [src/components/thread/index.tsx:212]()

**Sources**: [src/lib/ensure-tool-responses.ts](), [src/components/thread/index.tsx:212-233]()

## Message Submission Flow

```mermaid
graph TB
    UserInput["User input + contentBlocks"]
    UserInput --> CreateMsg["Create Message object<br/>id: uuidv4()<br/>type: 'human'<br/>content: [text, ...blocks]"]
    
    CreateMsg --> Validate["ensureToolCallsHaveResponses()"]
    Validate --> CheckContext{"artifactContext has keys?"}
    CheckContext -->|"true"| AddContext["Include context in submission"]
    CheckContext -->|"false"| NoContext["context: undefined"]
    
    AddContext --> Submit["thread.submit()"]
    NoContext --> Submit
    
    Submit --> Options["Options:<br/>streamMode: ['values']<br/>streamSubgraphs: true<br/>streamResumable: true<br/>optimisticValues: fn"]
    
    Options --> Optimistic["Optimistic update:<br/>Immediately add human message<br/>+ validated tool messages to UI"]
    
    Optimistic --> Stream["Stream response<br/>from LangGraph"]
    Stream --> UpdateMessages["Messages update in<br/>useStreamContext()"]
```

**Key aspects**:
- Messages are created with `uuidv4()` IDs [src/components/thread/index.tsx:204]()
- Content is array of text and multimodal blocks [src/components/thread/index.tsx:206-210]()
- Tool message validation happens before submission [src/components/thread/index.tsx:212]()
- Artifact context is conditionally included [src/components/thread/index.tsx:214-216]()
- Optimistic updates show messages immediately [src/components/thread/index.tsx:223-231]()
- Input and content blocks are cleared after submission [src/components/thread/index.tsx:235-236]()

**Sources**: [src/components/thread/index.tsx:197-237]()

## AssistantMessageLoading Component

During streaming, before the first token arrives, a loading indicator is displayed:

```mermaid
graph LR
    Loading["AssistantMessageLoading"]
    Loading --> Container["div.bg-muted.rounded-2xl"]
    Container --> Dot1["Animated dot<br/>animate-pulse 0s"]
    Container --> Dot2["Animated dot<br/>animate-pulse 0.5s"]
    Container --> Dot3["Animated dot<br/>animate-pulse 1s"]
```

**Visibility control**:
- Show when `isLoading && !firstTokenReceived` [src/components/thread/index.tsx:430-432]()
- `firstTokenReceived` is set when first AI message appears [src/components/thread/index.tsx:185-195]()
- Prevents loading indicator from showing during branch switches

**Sources**: [src/components/thread/messages/ai.tsx:214-224](), [src/components/thread/index.tsx:430-432]()

## Message Styling and Layout

Messages use distinct styling based on type:

| Message Type | Alignment | Background | Special Features |
|-------------|-----------|------------|------------------|
| Human | Right (`.ml-auto`) | `.bg-muted` | Rounded corners, text-right |
| AI | Left (`.mr-auto`) | Transparent | Left-aligned, full width |
| Tool Result | Left | Border/background | Syntax highlighted code |

**Hover actions**:
- Action bars (BranchSwitcher, CommandBar) use opacity transitions [src/components/thread/messages/ai.tsx:189-192]()
- Default `opacity-0`, visible on `group-hover` or `group-focus-within` [src/components/thread/messages/human.tsx:122-126]()
- Edit mode forces `opacity-100` [src/components/thread/messages/human.tsx:125]()

**Sources**: [src/components/thread/messages/ai.tsx:144-211](), [src/components/thread/messages/human.tsx:76-149]()

---

