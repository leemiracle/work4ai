<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/agent-chat-ui · page 4 Agent Inbox System · fetched 2026-10-26 -->

# Agent Inbox System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/thread/agent-inbox/components/thread-actions-view.tsx](src/components/thread/agent-inbox/components/thread-actions-view.tsx)
- [src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx](src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx)
- [src/components/thread/agent-inbox/index.tsx](src/components/thread/agent-inbox/index.tsx)
- [src/components/thread/messages/ai.tsx](src/components/thread/messages/ai.tsx)
- [src/components/thread/messages/generic-interrupt.tsx](src/components/thread/messages/generic-interrupt.tsx)
- [src/components/thread/messages/shared.tsx](src/components/thread/messages/shared.tsx)
- [src/lib/agent-inbox-interrupt.ts](src/lib/agent-inbox-interrupt.ts)
- [src/providers/Thread.tsx](src/providers/Thread.tsx)
- [src/providers/client.ts](src/providers/client.ts)

</details>



The Agent Inbox System provides human-in-the-loop capabilities for LangGraph agents by handling interrupt events that require human input. When a LangGraph agent emits a `HumanInterrupt`, this system detects the interrupt type, renders an appropriate user interface for collecting human responses, and submits those responses back to the agent to resume execution.

This document covers interrupt detection, specialized UI components for agent inbox interrupts, generic interrupt fallback handling, and the response submission flow. For information about the overall streaming architecture, see [Stream Provider](#2.2). For details on message rendering, see [AI Messages](#3.1).

## Interrupt Detection and Routing

When an AI message contains interrupt data, the system performs schema validation to determine the appropriate rendering approach. The interrupt routing logic is implemented in the `Interrupt` component within the `AssistantMessage` renderer.

```mermaid
graph TB
    AIMessage["AssistantMessage Component<br/>(src/components/thread/messages/ai.tsx)"]
    InterruptData["thread.interrupt.value"]
    Validation["isAgentInboxInterruptSchema()<br/>(src/lib/agent-inbox-interrupt.ts)"]
    
    AgentInboxPath["Agent Inbox Interrupt Path"]
    GenericPath["Generic Interrupt Path"]
    
    ThreadView["ThreadView Component<br/>(src/components/thread/agent-inbox/index.tsx)"]
    GenericView["GenericInterruptView Component<br/>(src/components/thread/messages/generic-interrupt.tsx)"]
    
    AIMessage --> InterruptData
    InterruptData --> Validation
    
    Validation --> |"Has action_request, config fields"| AgentInboxPath
    Validation --> |"Missing required fields"| GenericPath
    
    AgentInboxPath --> ThreadView
    GenericPath --> GenericView
    
    DisplayCondition["Display only if:<br/>isLastMessage OR<br/>hasNoAIOrToolMessages"]
    
    ThreadView --> DisplayCondition
    GenericView --> DisplayCondition
```

**Interrupt Validation Schema**

The `isAgentInboxInterruptSchema` function validates whether an interrupt value conforms to the `HumanInterrupt` type from `@langchain/langgraph/prebuilt`. The validation checks for:

| Required Field | Type | Description |
|---------------|------|-------------|
| `action_request` | `object` | Contains the action being requested |
| `config` | `object` | Configuration controlling allowed responses |
| `config.allow_respond` | `boolean` | Whether free-text responses are allowed |
| `config.allow_accept` | `boolean` | Whether accepting without changes is allowed |
| `config.allow_edit` | `boolean` | Whether editing arguments is allowed |
| `config.allow_ignore` | `boolean` | Whether ignoring the interrupt is allowed |

**Sources:** [src/lib/agent-inbox-interrupt.ts:1-19](), [src/components/thread/messages/ai.tsx:70-94]()

### Rendering Conditions

Interrupts are only displayed when they represent the current state of agent execution. The display logic enforces two conditions:

1. **Last Message Rule**: The interrupt is attached to the last message in the thread (`isLastMessage`)
2. **No Subsequent Messages Rule**: No AI or tool messages exist after this point (`hasNoAIOrToolMessages`)

These conditions prevent stale interrupts from displaying when the agent has already resumed execution.

**Sources:** [src/components/thread/messages/ai.tsx:113-117](), [src/components/thread/messages/ai.tsx:149-153]()

## Agent Inbox Components

### ThreadView Component

The `ThreadView` component serves as the main container for agent inbox interrupts, managing the layout between the action interface and optional side panels for state/description viewing.

```mermaid
graph LR
    ThreadView["ThreadView<br/>(index.tsx)"]
    
    StateManagement["State Management"]
    ShowDescription["showDescription: boolean"]
    ShowState["showState: boolean"]
    ShowSidePanel["showSidePanel = showDescription || showState"]
    
    ConditionalRender["Conditional Rendering"]
    
    StateView["StateView Component<br/>Display state or description"]
    ThreadActionsView["ThreadActionsView Component<br/>User interaction interface"]
    
    ThreadView --> StateManagement
    StateManagement --> ShowDescription
    StateManagement --> ShowState
    StateManagement --> ShowSidePanel
    
    ThreadView --> ConditionalRender
    ConditionalRender --> |"showSidePanel = true"| StateView
    ConditionalRender --> |"showSidePanel = false"| ThreadActionsView
    
    ThreadActionsView --> |"Toggle buttons"| StateManagement
```

**Layout Structure**

The component renders a scrollable container with:
- Fixed height of `80vh`
- Responsive layout: `flex-col` on mobile, `flex-row` on large screens (`lg:flex-row`)
- Custom scrollbar styling with thin track and rounded thumb
- Background color `bg-gray-50/50` with padding and rounded corners

**Sources:** [src/components/thread/agent-inbox/index.tsx:1-58]()

### ThreadActionsView Component

The `ThreadActionsView` component provides the primary user interface for interacting with agent interrupts. It displays action metadata, provides toggle buttons for viewing state/description, and renders the response input interface.

```mermaid
graph TB
    ThreadActionsView["ThreadActionsView Component"]
    
    subgraph Header["Header Section"]
        ThreadTitle["Thread Title<br/>(interrupt.action_request.action)"]
        ThreadID["ThreadIdCopyable<br/>Copy thread ID"]
        ButtonGroup["Toggle Buttons<br/>State / Description"]
        StudioButton["Open in Studio Button"]
    end
    
    subgraph Actions["Action Buttons"]
        ResolveButton["Mark as Resolved<br/>handleResolve()"]
        IgnoreButton["Ignore<br/>handleIgnore()<br/>(if allow_ignore)"]
    end
    
    subgraph InputSection["Response Input"]
        InboxItemInput["InboxItemInput Component<br/>Dynamic form based on config"]
    end
    
    ThreadActionsView --> Header
    ThreadActionsView --> Actions
    ThreadActionsView --> InputSection
    
    InterruptedActionsHook["useInterruptedActions Hook<br/>State and handlers"]
    
    ThreadActionsView --> InterruptedActionsHook
```

**Action Button Handlers**

The component provides three primary action handlers:

| Button | Handler | Behavior |
|--------|---------|----------|
| Mark as Resolved | `handleResolve()` | Submits command `{goto: END}` to terminate thread |
| Ignore | `handleIgnore()` | Submits ignore response (only if `allow_ignore=true`) |
| Studio | `handleOpenInStudio()` | Opens LangGraph Studio with constructed URL |

**Studio Integration**

The "Open in Studio" button uses `constructOpenInStudioURL` to build a URL pointing to the LangGraph Studio environment:
- Requires `apiUrl` to be configured
- Includes `threadId` in the URL
- Opens in a new browser tab

**Sources:** [src/components/thread/agent-inbox/components/thread-actions-view.tsx:1-174]()

### Response Type Configuration

The `InboxItemInput` component dynamically renders input controls based on the interrupt's configuration flags:

```mermaid
graph TD
    InterruptConfig["interrupt.config"]
    
    AllowEdit["allow_edit: boolean"]
    AllowAccept["allow_accept: boolean"]
    AllowRespond["allow_respond: boolean"]
    AllowIgnore["allow_ignore: boolean"]
    
    InterruptConfig --> AllowEdit
    InterruptConfig --> AllowAccept
    InterruptConfig --> AllowRespond
    InterruptConfig --> AllowIgnore
    
    EditUI["Argument Editing Form<br/>Edit fields with change tracking"]
    AcceptUI["Accept Button<br/>Accept without changes"]
    RespondUI["Free Text Input<br/>Provide custom response"]
    IgnoreUI["Ignore Button<br/>Skip this interrupt"]
    
    AllowEdit --> |"true"| EditUI
    AllowAccept --> |"true"| AcceptUI
    AllowRespond --> |"true"| RespondUI
    AllowIgnore --> |"true"| IgnoreUI
    
    SubmitTypeSelector["Submit Type Selector<br/>(if multiple methods allowed)"]
    
    EditUI --> SubmitTypeSelector
    AcceptUI --> SubmitTypeSelector
    RespondUI --> SubmitTypeSelector
```

**Sources:** [src/components/thread/agent-inbox/components/inbox-item-input.tsx]() (referenced), [src/components/thread/agent-inbox/components/thread-actions-view.tsx:155-170]()

## Generic Interrupt Handling

When an interrupt does not conform to the agent inbox schema, the system falls back to the `GenericInterruptView` component, which provides a flexible key-value display for arbitrary interrupt data.

```mermaid
graph TB
    GenericInterruptView["GenericInterruptView Component<br/>(src/components/thread/messages/generic-interrupt.tsx)"]
    
    InputData["interrupt: Record<string, any><br/>or Array"]
    
    ProcessData["Process Entries"]
    ArrayCheck{{"Array.isArray(interrupt)"}}
    
    ArrayPath["Display as indexed items<br/>(0, 1, 2...)"]
    ObjectPath["Display as key-value pairs"]
    
    TruncationLogic["Truncation Logic"]
    ShouldTruncate{{"contentLines.length > 4 OR<br/>contentStr.length > 500"}}
    
    ExpandableView["Expandable/Collapsible View<br/>(framer-motion animations)"]
    
    TableRender["Table Rendering<br/>tbody with tr/td"]
    
    GenericInterruptView --> InputData
    InputData --> ProcessData
    ProcessData --> ArrayCheck
    
    ArrayCheck --> |"true"| ArrayPath
    ArrayCheck --> |"false"| ObjectPath
    
    ProcessData --> TruncationLogic
    TruncationLogic --> ShouldTruncate
    ShouldTruncate --> |"true"| ExpandableView
    
    ExpandableView --> TableRender
```

**Value Rendering Logic**

The `renderInterruptStateItem` function handles different value types:

| Value Type | Rendering Approach |
|-----------|-------------------|
| Object/Array | `<code>` block with `JSON.stringify(value, null, 2)` |
| URL string | `<a>` tag with `target="_blank"` and `rel="noopener noreferrer"` |
| Other | `String(value)` conversion |

**Truncation Strategy**

The component implements intelligent truncation:
- Long strings (>100 chars): Truncated to 100 chars + "..." (except URLs)
- Arrays (when collapsed): Limited to first 2 items
- Complex objects (>100 chars): Replaced with "Truncated X characters..."
- Array items (when collapsed): Limited to first 5 items

**Animation System**

Uses `framer-motion` for expand/collapse animations:
- `AnimatePresence` with `mode="wait"` for smooth transitions
- Initial/animate/exit states with opacity and y-axis transforms
- Duration: 0.2s for content, 0.3s for height
- Expand/collapse button with scale animations on hover/tap

**Sources:** [src/components/thread/messages/generic-interrupt.tsx:1-161]()

## User Response Management

The `useInterruptedActions` hook centralizes all state management and submission logic for handling user responses to interrupts.

```mermaid
graph TB
    Hook["useInterruptedActions Hook<br/>(src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx)"]
    
    subgraph StateValues["State Values"]
        HumanResponse["humanResponse: HumanResponseWithEdits[]<br/>Response objects with type/args/metadata"]
        Loading["loading: boolean<br/>Submission in progress"]
        Streaming["streaming: boolean<br/>Agent streaming response"]
        StreamFinished["streamFinished: boolean<br/>Stream completed"]
        HasEdited["hasEdited: boolean<br/>User modified edit fields"]
        HasAddedResponse["hasAddedResponse: boolean<br/>User entered free text"]
        AcceptAllowed["acceptAllowed: boolean<br/>Accept option available"]
        SelectedSubmitType["selectedSubmitType: SubmitType<br/>edit | accept | response"]
    end
    
    subgraph Actions["Action Handlers"]
        HandleSubmit["handleSubmit()<br/>Submit selected response"]
        HandleIgnore["handleIgnore()<br/>Submit ignore response"]
        HandleResolve["handleResolve()<br/>End thread with goto:END"]
    end
    
    subgraph Initialization["Initialization"]
        CreateDefault["createDefaultHumanResponse()<br/>Parse interrupt config"]
        InitEffect["useEffect on interrupt change"]
    end
    
    Hook --> StateValues
    Hook --> Actions
    Hook --> Initialization
    
    CreateDefault --> HumanResponse
    CreateDefault --> SelectedSubmitType
    CreateDefault --> AcceptAllowed
```

**Response Type Structure**

The `HumanResponseWithEdits` type extends the base `HumanResponse` with additional metadata:

| Field | Type | Purpose |
|-------|------|---------|
| `type` | `"edit" \| "accept" \| "response" \| "ignore"` | Response method |
| `args` | `any` | Response payload |
| `acceptAllowed` | `boolean` (edit only) | Whether accept is available |
| `editsMade` | `boolean` (edit only) | Whether user changed values |

**Sources:** [src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx:1-306](), [src/components/thread/agent-inbox/types.ts]() (referenced)

### Initialization Flow

When the component receives an interrupt, the initialization process:

1. **Parse Config**: Calls `createDefaultHumanResponse(interrupt, initialHumanInterruptEditValue)`
2. **Build Response Objects**: Creates `HumanResponseWithEdits[]` array based on allowed methods
3. **Set Default Submit Type**: Determines which submit type to pre-select
4. **Check Accept Availability**: Sets `acceptAllowed` flag
5. **Store Initial Values**: Saves original edit values in `initialHumanInterruptEditValue.current` ref

**Sources:** [src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx:71-81]()

## Response Submission Flow

The submission flow transforms user input into `HumanResponse` objects and sends them to the agent via the streaming context.

```mermaid
sequenceDiagram
    participant User
    participant HandleSubmit as "handleSubmit()"
    participant Validation as "Validation Logic"
    participant Transform as "Response Transform"
    participant ResumeRun as "resumeRun()"
    participant ThreadSubmit as "thread.submit()"
    participant Agent as "LangGraph Agent"
    
    User->>HandleSubmit: Click submit/press Enter
    HandleSubmit->>Validation: Check humanResponse exists
    
    alt Response missing
        Validation-->>User: Toast error
    end
    
    HandleSubmit->>Transform: flatMap humanResponse
    
    Transform->>Transform: Check each response type
    
    alt type = "edit"
        alt acceptAllowed && !editsMade
            Transform->>Transform: Convert to {type: "accept", args}
        else
            Transform->>Transform: Keep {type: "edit", args}
        end
    end
    
    alt type = "response" && !args
        Transform->>Transform: Filter out (empty response)
    end
    
    Transform->>Transform: Find response matching selectedSubmitType
    
    alt No matching response
        Transform-->>User: Toast error: "No response found"
    end
    
    Transform->>ResumeRun: Pass filtered response array
    ResumeRun->>ThreadSubmit: submit({}, {command: {resume: response}})
    ThreadSubmit->>Agent: Resume with HumanResponse
    Agent-->>User: Continue execution
    
    HandleSubmit->>HandleSubmit: setLoading(true), setStreaming(true)
    HandleSubmit-->>User: Toast success
```

**Edit-to-Accept Conversion**

When submitting an edit response, the system performs automatic conversion:
- If `acceptAllowed = true` and `editsMade = false`: Convert `type: "edit"` to `type: "accept"`
- This optimization allows the agent to distinguish between "user reviewed but didn't change" vs "user modified values"

**Sources:** [src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx:100-220]()

### Resume Command Structure

The `resumeRun` function wraps the response in a LangGraph command:

```typescript
thread.submit(
  {},
  {
    command: {
      resume: response  // HumanResponse[]
    }
  }
)
```

This command structure tells the LangGraph agent to:
1. Resume execution from the interrupted checkpoint
2. Use the provided `HumanResponse` as input
3. Continue processing with the human-provided context

**Sources:** [src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx:83-98]()

### Ignore and Resolve Actions

**Ignore Action**

When the user clicks "Ignore":
1. Finds the `{type: "ignore"}` response in `humanResponse` array
2. Validates that ignoring is allowed
3. Calls `resumeRun([ignoreResponse])`
4. Resets `initialHumanInterruptEditValue.current`

**Resolve Action**

When the user clicks "Mark as Resolved":
1. Submits a special command: `{command: {goto: END}}`
2. This terminates the thread execution
3. No resume value is needed
4. Uses `END` symbol from `@langchain/langgraph/web`

**Sources:** [src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx:222-280]()

## Integration with Stream Provider

The Agent Inbox System integrates deeply with the Stream Provider to access thread state and submission capabilities:

```mermaid
graph LR
    StreamContext["useStreamContext()<br/>(src/providers/Stream.tsx)"]
    
    ThreadData["thread.interrupt<br/>Current interrupt value"]
    ThreadValues["thread.values<br/>Full thread state"]
    ThreadSubmit["thread.submit()<br/>Command submission"]
    
    ThreadView["ThreadView Component"]
    UseInterruptedActions["useInterruptedActions Hook"]
    
    StreamContext --> ThreadData
    StreamContext --> ThreadValues
    StreamContext --> ThreadSubmit
    
    ThreadData --> ThreadView
    ThreadValues --> ThreadView
    ThreadSubmit --> UseInterruptedActions
    
    StateView["StateView<br/>Display thread.values"]
    ResumeFlow["Resume Flow<br/>Submit command"]
    
    ThreadView --> StateView
    UseInterruptedActions --> ResumeFlow
```

The system retrieves:
- `thread.interrupt`: The current interrupt object (if any)
- `thread.values`: Full thread state for display in StateView
- `thread.submit()`: Method to send commands/responses back to agent

After successful submission, the agent resumes execution and new streaming events flow through the same Stream Provider, potentially clearing the interrupt state or emitting new messages.

**Sources:** [src/components/thread/agent-inbox/index.tsx:11-16](), [src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx:56](), [src/providers/Stream.tsx]() (referenced)

---

